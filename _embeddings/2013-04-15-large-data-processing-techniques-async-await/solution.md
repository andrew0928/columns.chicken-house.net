# 處理大型資料的技巧 – Async / Await

# 問題／解決方案 (Problem/Solution)

## Problem: Web 服務在讀取 Azure Blob 大型檔案並即時回傳時效能只有原始下載速度的一半

**Problem**:  
Web 服務必須  
1. 從 Azure Storage Blob 讀取約 100 MB 的大型 Video 檔案  
2. 進行授權驗證與轉碼  
3. 直接寫入 HTTP Response 串流給使用者  

實際量測只有 3.5 Mbps，與直接下載 Blob 的 7.3 Mbps 相比效能幾乎腰斬。CPU、頻寬、Disk I/O 監控皆無明顯瓶頸，但整體速度仍很慢。

**Root Cause**:  
程式採單執行緒、同步 while loop 模型：  
• Read → Process → Write 依序執行，三段完全沒有重疊  
• 讀取時 CPU、網路閒置；處理時 Disk、網路閒置；寫入時 CPU、Disk 閒置  
• 等於公司「三個員工同時只做一件事」──硬體資源利用率低，執行時間被各階段相加拉長

**Solution**: 以 C# 5 / .NET 4.5 的 async / await 改寫為「非同步管線」  
關鍵思路  
1. 把 Write() 改為 `async Task`；呼叫後立即 return，不阻塞主流程  
2. 在迴圈中先做 `Read()` + `Process()` → 之後立刻丟下一個 `Write()`  
3. 透過 `await 上一次 writeTask` 確保寫入順序正確  
4. Read/Process 與 Write 兩段得以重疊，CPU、Network、Disk 同時被利用

示意核心程式碼 (簡化)：

```csharp
for(int i=0;i<LoopCount;i++){
    Read();            // 同步
    Process();         // 同步
    if(previousWrite!=null) await previousWrite;  // 等待上一輪寫完
    previousWrite = Write(); // 非同步寫入，立即返回
}
await previousWrite;  // 等待最後一次寫完
```

這種「Producer(Read+Process)/Consumer(Write)」pipeline 只需數行 async/await 即能實現；程式結構 90% 不變，可讀性遠高於傳統 Thread/Callback。

**Cases 1**: 範例程式 (Read=200 ms, Process=300 ms, Write=500 ms，迴圈 10 次)  
- 同步版總耗時：10 000 ms  
- async/await 版總耗時：≈ 5 500 ms  
- 實際縮短 45%，完全符合「Read+Process 與 Write 重疊」的預期

**Cases 2**: 真實生產環境 (VM 內網 200 Mbps, Client ↔ VM 10 Mbps)  
- 原始 throughput：3.5 Mbps  
- 改用 async/await 後：≈ 6–7 Mbps (取決於 client 網路)，接近理論上限  
- Server CPU 使用率由 30% 提升至 60%，Network 由 40% 提升至 80%，資源利用率顯著提高

**Cases 3**: 不同 Client 頻寬下的改善幅度 (擷取文中試算)  
|Client 頻寬|同步(ms)|async(ms)|改善%|
|-----------|--------|---------|-----|
|200 Mbps|7 000|5 500|+27%|
|80 Mbps |10 000|5 500|+82%|
|10 Mbps |45 000|40 500|+11%|
|2 Mbps  |205 000|200 500|+2%|

結論：若 Write 時間與 Read+Process 時間在同一量級 (如 80 Mbps 案例)，async/await 能帶來 80% 以上效能提升；當 Write 遠慢於 Read/Process (低頻寬) 時，改善幅度趨近於 0–10%，屬「體感無感」。判斷依據即是「執行流程中是否存在大量等待」。