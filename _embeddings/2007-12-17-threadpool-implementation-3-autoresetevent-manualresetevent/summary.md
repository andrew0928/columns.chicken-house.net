# ThreadPool 實作 #3. AutoResetEvent / ManualResetEvent

## 摘要提示
- 執行緒喚醒策略: ThreadPool 可採「先到先贏」或「任由 OS 排程」兩種分派模式。
- WaitHandle 選擇: 以上兩種策略只需在 AutoResetEvent 與 ManualResetEvent 間切換一行程式碼即可。
- AutoResetEvent 特性: 每次 Set() 僅喚醒一條被 WaitOne() 阻塞的執行緒。
- ManualResetEvent 特性: 一次 Set() 可同時喚醒所有等待中的執行緒。
- 範例程式: 透過五條 thread 等待同一個事件，觀察兩種 Event 型別造成的不同輸出。
- OS 排程影響: 當同時喚醒多條執行緒時，實際誰先跑完全由作業系統排程決定。
- ThreadPool 微調: 想實作公平排隊就用 AutoResetEvent；需根據 Priority 讓 OS 決定則用 ManualResetEvent。
- SimpleThreadPool: 文末附上一百餘行的完整原始碼，示範手工 ThreadPool 的基本結構。
- 資源釋放: 實作中以 EndPool、CancelPool 與 Dispose 確保工作結束與記憶體回收。
- 讀者授權: 作者歡迎引用或專案使用，禮貌性告知即可。

## 全文重點
本文延續前兩篇 ThreadPool 系列，討論當工作排入佇列後，該由哪一條閒置 worker thread 來承接的策略。作者指出可自行指定「等最久者先拿工作」，也可以完全交給作業系統排程決定。雖然前者看似公平，但若執行緒優先序不同、碰上 GC 或被換出記憶體，硬指定反而拖慢效率，因此多數情況放手給 OS 會更簡單也更有效率。  
在 .NET 中，這兩種策略竟只差一行程式：採用 AutoResetEvent 或 ManualResetEvent。AutoResetEvent 每次 Set() 僅喚醒一條 thread，形成「排隊制」；ManualResetEvent 則一次喚醒全部，形成「放任制」。作者以簡短的 Main 函式創建五條 thread，操作兩種 Event 型別並列出輸出差異，實際證明了上述行為。  
文章最後提供約百行的 SimpleThreadPool 完整原始碼，示範工作佇列、worker thread 建立、逾時機制與結束流程。若想改成「先排隊先贏」，只需把 enqueueNotify 由 ManualResetEvent 改成 AutoResetEvent；若需依 thread priority 讓 OS 排程，就保持 ManualResetEvent。作者歡迎讀者在專案中使用並回饋心得。

## 段落重點
### 兩種 worker thread 選擇策略
開場闡述 ThreadPool 在面對多條閒置 thread 時，可由程式端決定誰接下一個工作，或完全交給 OS 排程器。OS 擁有完整的優先序、GC、換頁等資訊，往往能做出較佳決策，因此「全部同時喚醒、由 OS 競爭」常比「先到先贏」更有效率。

### AutoResetEvent 實測
示範程式建立五條 thread，皆對同一個 AutoResetEvent.WaitOne()。主程式每秒呼叫一次 Set()，觀察到五條 thread 依序被喚醒，完美符合「一次喚醒一人」的排隊模型，顯示 AutoResetEvent 適用於希望精確控制執行緒數量的情境。

### ManualResetEvent 實測
將同一段程式僅改成 ManualResetEvent，主程式只需一次 Set()，五條 thread 即同時解除阻塞並隨機輸出 wakeup 訊息。此行為代表「一次喚醒全部」，交由作業系統決定誰先執行，映射到 ThreadPool 即為讓所有 worker 同時競爭工作。

### 對 ThreadPool 設計的啟示
透過 Auto/ManualResetEvent 切換即可改變 ThreadPool 的分派策略。若想實作嚴格公平佇列，選用 AutoResetEvent；若工作特性需混合不同優先權而仰賴 OS 排程，就使用 ManualResetEvent。簡單一行即可達到不同目標，卻牽動整體效能與行為，因而值得多加說明。

### SimpleThreadPool 完整程式碼
作者提供 ChickenHouse.Core.Threading.SimpleThreadPool 類別，核心約百行，包含工作佇列、worker thread 動態增生、逾時、終止與取消機制。enqueueNotify 預設為 ManualResetEvent，但讀者可依需求改成 AutoResetEvent 立即切換策略。程式可直接引用於專案，僅需禮貌性通知作者用途。