# ThreadPool 實作 #3. AutoResetEvent / ManualResetEvent

# 問答集 (FAQ, frequently asked questions and answers)

## Q: AutoResetEvent 與 ManualResetEvent 在喚醒 thread 上有什麼差異？
AutoResetEvent 每次 `Set()` 只會喚醒「一條」等待中的執行緒；ManualResetEvent 每次 `Set()` 則會同時喚醒「一條以上、所有」等待中的執行緒。

## Q: 如果想讓 ThreadPool 採用「先排隊先贏」的策略，程式碼上需要做什麼改動？
只要把 ThreadPool 內部用來同步的 WaitHandle 型別改成 AutoResetEvent，即可達到一次只喚醒一條 thread、誰等最久誰先被喚醒的效果。

## Q: 若希望把工作分派的選擇權完全交給作業系統排程器，應該用哪一種 WaitHandle？
應該使用 ManualResetEvent。它會一次喚醒所有等待中的 worker threads，接下來由 OS 排程器決定哪一條 thread 先進入 running 狀態並搶到工作。

## Q: 在 SimpleThreadPool 中，何時需要選用 ManualResetEvent？
當你想根據工作特性微調每條 thread 的優先順序 (priority)，或希望讓 OS 排程器自行決定第一個可用 thread 時，就應採用 ManualResetEvent。

## Q: 被 ManualResetEvent 一次喚醒的多條 thread，哪一條會第一個開始執行工作？
順序取決於作業系統的排程策略，例如各 thread 的優先權、當下是否 GC、是否被換出到虛擬記憶體等因素；應用程式端很難準確控制，因此交由 OS 決定通常較有效率。