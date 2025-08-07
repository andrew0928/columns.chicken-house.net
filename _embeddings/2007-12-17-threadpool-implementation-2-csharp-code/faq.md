# ThreadPool 實作 #2. 程式碼 (C#)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: SimpleThreadPool 可讓使用者設定哪些組態參數？
1. Worker thread 的數量上限  
2. Worker thread 的優先權  
3. Thread 的 idle timeout 時間 (超過後就會被回收)  
4. Job queue 的「安全範圍」(超過後需增援新的 worker)

## Q: 當 job queue 已超過安全範圍且目前的 worker thread 數量尚未達上限時，ThreadPool 會怎麼做？
它會呼叫 `CreateWorkerThread()` 動態建立新的 worker thread 來加速消化佇列中的工作。

## Q: 如果一個 worker thread 的閒置時間超過 idle timeout，ThreadPool 會怎麼處理？
當 `WaitOne()` 等待超過 idle timeout 時，worker thread 會跳出迴圈並自我終止，從而被 ThreadPool 回收。

## Q: `EndPool()` 與 `CancelPool()` 有什麼差別？
• `EndPool()` 會阻塞呼叫端，直到所有排隊中的工作都處理完畢後才結束 ThreadPool。  
• `CancelPool()` 則只讓正在執行中的工作跑完，剩下尚未開始的排隊工作全部丟棄，ThreadPool 立即關閉。

## Q: SimpleThreadPool 內部用什麼同步原語來喚醒等待中的 worker threads？
使用 `ManualResetEvent`。  
工作加入佇列後呼叫 `Set()`；worker threads 透過 `WaitOne()` 被喚醒或在 timeout 後自行醒來。

## Q: 如果有多個 worker thread 同時競爭同一個工作，誰決定哪一條 thread 取得該工作？
交由作業系統 (OS) 的排程器決定，ThreadPool 本身不做主動分配。

## Q: `DoWorkerThread()` 方法的核心流程是什麼？
1. 進入無窮迴圈，持續從 job queue 中 `Dequeue()` 工作並執行。  
2. queue 清空後以 `WaitOne(idleTimeout)` 進入睡眠，等待新工作或 idle timeout。  
3. 若收到停止/取消旗標或 timeout 到期即跳出迴圈並終結自己。  
4. 結束前將自己從 `_workerThreads` 清單中移除。

## Q: 在 `QueueUserWorkItem()` 裡什麼情況下會呼叫 `CreateWorkerThread()`？
當「佇列中已經至少有一個工作」且「目前的 worker thread 數量仍小於設定的上限」時，就會再建立一條新的 worker thread。