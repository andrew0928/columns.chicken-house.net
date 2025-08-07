# ThreadPool 實作 #2. 程式碼 (C#)

## 摘要提示
- 目標功能: 使用者可設定執行緒上限、優先權、Idle Timeout 與佇列安全值。
- 動態擴充: 佇列超載時 ThreadPool 會自動產生額外 Worker Threads。
- 資源回收: Worker Thread 閒置超過 Idle Timeout 會自行結束並自動從池中移除。
- 同步控制: 提供 EndPool 與 CancelPool 等 API，以阻塞或放棄等待中的工作。
- 外部介面: SimpleThreadPool 類別公開 QueueUserWorkItem、EndPool、CancelPool 等方法供呼叫。
- Worker 邏輯: DoWorkerThread 迴圈負責取出並執行工作，空閒時以 ManualResetEvent 進入等待。
- 工作佇列: 新工作入列後透過 ManualResetEvent.Set 喚醒睡眠中的 Worker Threads。
- 擴編條件: 如佇列非空且 Thread 數未達上限即呼叫 CreateWorkerThread 擴充。
- 範例用法: 示範建立兩條 Thread 的池，排入 25 筆工作並於全部完成後收攤。
- 設計理念: 讓 OS 決定多執行緒爭用，ThreadPool 只負責排程與同步，降低複雜度。

## 全文重點
本文延續上一回的 pseudo code，實作一個可組態的 C# 簡易 ThreadPool。開發者可於建構時傳入最大 Worker Thread 數與優先權，於執行期再透過屬性調整 Idle Timeout 與 Job Queue 的安全範圍。池內維護一組 Worker Thread 與一條工作佇列；當佇列累積且 Thread 數少於上限時，自動建立新 Thread；反之，若 Thread 閒置超過 Idle Timeout 就會自我結束並從池中移除。對外介面包含 QueueUserWorkItem（兩種多載）負責入列工作、EndPool 等待工作完成並關閉、CancelPool 放棄尚未執行的工作並立刻收攤。核心函式 DoWorkerThread 以無窮迴圈從佇列取出 WorkItem 執行，若佇列為空便以 ManualResetEvent.WaitOne 進入睡眠；被 Set 喚醒或超時即再度檢查佇列或結束。工作入列時除加入佇列外，亦呼叫 Set 喚醒所有睡眠中的 Thread。整體藉由 ManualResetEvent 達成最少同步開銷，並將「誰拿到工作」的判斷完全交由 OS 的排程器。文章最後貼出完整程式碼並示範以兩條 Thread 建立池、排入 25 筆工作、等待工作全數完成後結束的範例，說明 ThreadPool 的使用情境與設計哲學。

## 段落重點
### 設計目標與需求
作者首先列出五大功能需求：可設定執行緒上限、優先權、Idle Timeout 與安全佇列範圍；佇列爆量時能自動增生執行緒；Idle 超時即自我回收；提供同步 API 等待所有工作完成；多執行緒搶同一工作時由 OS 決定。這些條件構成本次實作的邊界與目標。

### SimpleThreadPool 介面與範例用法
根據需求，作者設計 SimpleThreadPool 類別，公開建構子、QueueUserWorkItem 的兩種多載、EndPool、CancelPool 與 IDisposable 介面。接著以範例程式展示：先建立兩條 Thread 的池，連續排入 25 筆工作，每排一次隨機 Sleep，以模擬真實負載並示範 EndPool 阻塞直到全部完成的行為。

### Worker Thread 執行流程 (DoWorkerThread)
DoWorkerThread 是核心：Thread 進入無窮迴圈，佇列有資料時以 lock 取出並執行 WorkItem；若收到 _cancel_flag 即跳出。佇列清空後 Thread 呼叫 enqueueNotify.WaitOne 進入睡眠，若在 Idle Timeout 前被 Set 喚醒則繼續執行新工作，否則自動 break 退出迴圈並從池中移除。此機制確保動態擴充與閒置回收。

### Job 入列與動態擴充
QueueUserWorkItem 裡先檢查池是否已關閉，接著建立 WorkItem 物件放入佇列。若佇列已非空且 Thread 數量未達上限便呼叫 CreateWorkerThread 增生 Thread。最後呼叫 enqueueNotify.Set 喚醒所有睡眠中的 Worker。這段邏輯同時兼顧擴充與喚醒需求。

### 同步機制與設計哲學
實作使用 ManualResetEvent 作為等待／喚醒機制，因為它能一次叫醒多條 Thread，再靠 OS 排程決定哪一條真正取得 lock 執行工作。作者強調 ThreadPool 僅負責排程與同步，避免自行實作複雜爭用邏輯，藉此降低錯誤並保持簡潔。文章最後預告後續將深入討論同步原理與事件物件選型。