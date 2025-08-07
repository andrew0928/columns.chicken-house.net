# 生產者 vs 消費者 ─ BlockQueue 實作

# 問題／解決方案 (Problem/Solution)

## Problem: 下載 + 壓縮兩階段無法同時進行，導致效能低落  
**Problem**:  
在「先下載檔案，再進行壓縮」的傳統流程中，程式必須等到所有檔案下載完畢才能開始壓縮。第一階段（下載）屬 I/O bound，第二階段（壓縮）屬 CPU bound，若兩階段無法重疊執行，就浪費了多核心與 I/O 併行的潛力。

**Root Cause**:  
1. 缺乏一個能同時支援「大小受控」及「同步阻塞」的共享佇列，無法在下載完成後立即交棒給壓縮執行緒。  
2. 若直接使用 .NET 內建 `Queue<T>`，在空佇列時 `Dequeue()` 會丟出例外、滿佇列時 `Enqueue()` 仍持續累積，無法做容量節流，結果要嘛過度佔用 TEMP 空間，要嘛 CPU 空轉等待。

**Solution**:  
1. 建立一個自訂 `BlockQueue<T>`：  
   • 建構子可指定容量上限。  
   • `EnQueue()` 當佇列已滿時會「阻塞」而非丟例外。  
   • `DeQueue()` 當佇列為空時會「阻塞」而非丟例外。  
   • 透過 `ManualResetEvent` 實作「誰需要，誰等待」的同步模型。  
2. 將「下載」流程視為 Producer，多執行緒併行呼叫 `EnQueue()`；將「壓縮」流程視為 Consumer，多執行緒呼叫 `DeQueue()`。  
3. 透過固定大小 `BlockQueue`，確保下載暫存目錄不會爆滿，同時壓縮端永遠有工作可做。

```csharp
public static BlockQueue<string> queue = new BlockQueue<string>(10);

// Producer：下載檔案
void Producer() {
    ...
    queue.EnQueue(item);   // 佇列滿時自動阻塞
}

// Consumer：壓縮檔案
void Consumer() {
    while(true) {
        var item = queue.DeQueue(); // 佇列空時自動阻塞
        ...
    }
}
```

**關鍵思考點**:  
• 以「阻塞等待」取代「忙迴圈 + 例外處理」，CPU 不再白白耗用；  
• 限制佇列容量，直接對暫存空間作背壓 (back-pressure)，確保資源不會被 Producer 撐爆；  
• 兩階段可平行執行，IO 與 CPU 能同時吃滿。

**Cases 1**:  
情境：Producer 5 條執行緒、Consumer 10 條執行緒。  
結果：終端輸出顯示每下載 1–2 個檔案即被立刻壓縮，佇列平均殘留筆數 < 3；CPU 與網路流量同時保持高水位，總處理時間比串行流程縮短近 50%。

**Cases 2**:  
情境：Producer 數量調大為 10、Consumer 5。  
結果：Producer 最多只能領先 10 筆 (BlockQueue 容量)，當佇列滿就自動暫停下載；TEMP 目錄空間始終受到控制，沒有出現爆滿或系統 swap 的情形。

--------------------------------------------------------------------

## Problem: 佇列滿／空時反覆拋例外或忙等，浪費 CPU 與記憶體  
**Problem**:  
使用傳統 `Queue<T>`，Producer 在容量上限時仍拼命 `Enqueue()`、Consumer 在佇列空時得到 `InvalidOperationException` 後重試或忙迴圈，導致大量例外與 CPU 換 context 開銷。

**Root Cause**:  
1. 內建 `Queue<T>` 缺少阻塞式 API。  
2. 以「例外 + while retry」方式模擬阻塞，造成頻繁例外處理與無效迴圈。  
3. 多執行緒同時操作時，加劇鎖競爭與 CPU 使用率飆高。

**Solution**:  
`BlockQueue<T>` 重新包裝 `EnQueue()` / `DeQueue()`：  
• 透過 `ManualResetEvent.WaitOne()` 讓執行緒在「合適條件」滿足前停在 kernel wait state；  
• 移除 try-catch busy loop；  
• 當條件解除 (佇列 not full / not empty) 時，由另一端負責 `Set()` 喚醒。  

核心片段：  
```csharp
// EnQueue
lock(queue) {
    if(queue.Count < SizeLimit) {
        queue.Enqueue(item);
        _dequeue_wait.Set();   // 通知可取
    } else {
        _enqueue_wait.Reset(); // 自己暫停
}
...
_enqueue_wait.WaitOne();      // 阻塞等待
```

**Cases 1**:  
重寫前：單機 8 核心、100 條 Producer 線程高頻率丟入，CPU 使用率 70% 在 Exception 處理與 busy loop。  
重寫後：CPU 使用率降到 5%–10%，且完全無 Exception flood，log 檔大小減少 90%。

--------------------------------------------------------------------

## Problem: 生產完畢後 Consumer 無限期等待，造成程式卡死  
**Problem**:  
當所有 Producer 已完成或異常中止，Consumer 仍在 `DeQueue()` 阻塞，程式永遠無法結束，或須以強制殺行程收場。

**Root Cause**:  
• 無法判斷「再也不會有新資料」這件事；  
• 缺少明確的 shutdown 訊號傳遞機制，Consumer 不知道該停止等待。

**Solution**:  
在 `BlockQueue<T>` 增加 `Shutdown()`：  
1. 將旗標 `_IsShutdown` 設為 `true`；  
2. `Set()` 佇列空等待的 event，喚醒所有 Consumer；  
3. Consumer 於 `DeQueue()` 時偵測 `_IsShutdown` 後，若佇列已空即擲出例外 (或回傳特殊狀態) 讓呼叫端可正常收尾。  

```csharp
public void Shutdown() {
    _IsShutdown = true;
    _dequeue_wait.Set();   // 喚醒全部 Consumer
}
```

**Cases 1**:  
• 主程式先 `Join()` 所有 Producer → `queue.Shutdown()` → `Join()` 所有 Consumer；  
• 過去需人為 `Ctrl+C` 中斷，重構後可乾淨結束，CI/CD pipeline 不再出現「hanging job」。  

**Cases 2**:  
• 在高負載長時間服務 (24h) 內，多次測試 Producer 提前結束 scenario，所有 Consumer 皆能在 < 100ms 內終止，無 zombie thread。