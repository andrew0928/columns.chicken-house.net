# ThreadPool 實作 #1. 基本概念

# 問答集 (FAQ, frequently asked questions and answers)

## Q: ThreadPool 設計模式的主要目的是什麼？
ThreadPool 透過把複雜的執行緒控制(建立、回收、同步)封裝在池內，讓使用者只需要把要執行的工作(job)包成物件丟進池子即可。如此可以大幅簡化傳統 multi-threading 程式設計模型。

## Q: 在實作一個 ThreadPool 時，必須解決哪三大課題？
1. 基本的執行緒同步機制 (thread sync)  
2. ThreadPool 內部的執行緒管理，包含動態建立與回收  
3. 工作(job)的封裝與 Job Queue 的實作  

## Q: OS Process/Thread 的三個主要狀態 (與同步最相關者) 是什麼？
Running (執行中)、Blocked (被同步物件暫停，OS 不會分配 CPU time slice)、Waiting/Ready (被喚醒後等待排程器再次分配 CPU)。

## Q: 在多執行緒環境下，為什麼不建議使用「全域變數 + 迴圈輪詢」做同步？
因為這種 busy-waiting 方式會浪費 CPU 資源而且效率低；應使用 OS 提供的同步原語，讓執行緒在需要等待時真正進入 Blocked 狀態，節省 CPU 並簡化程式碼。

## Q: 在 .NET 中，用哪個類別可以最直接地做到「等待 / 喚醒」？
System.Threading.WaitHandle 及其衍生類別，例如 ManualResetEvent：
```csharp
// thread 1: 等待
waitHandle.WaitOne();

// thread 2: 喚醒
waitHandle.Set();
```

## Q: AutoResetEvent、ManualResetEvent 與 Semaphore 各適合什麼情境？
• AutoResetEvent：喚醒「單一」等待中的執行緒後自動重設。  
• ManualResetEvent：可同時喚醒「多個」等待中的執行緒，需手動重設。  
• Semaphore：限制同時進入某段程式碼的執行緒數量，例如網站僅允許最多 3 條下載執行緒。

## Q: 什麼情況下特別需要 ThreadPool？
1. 工作數量龐大，不宜為每個工作各建一條執行緒  
2. 工作會持續產生，需要隨時有執行緒待命以降低回應時間  
3. 工作性質適合由「有限數量」的執行緒處理

## Q: ThreadPool 在動態管理執行緒時常見的兩項策略是？
1. 如果 Queue 中還有大量工作且現有執行緒不足 (且未達上限)，就動態建立新執行緒加入池中。  
2. 如果工作已清空，執行緒進入 idle；當 idle 時間超過預設閾值便回收(fired)多餘的執行緒。

## Q: ASP.NET 如何利用 ThreadPool 改善回應時間？
ASP.NET Hosting 會預先養一批執行緒來服務 IIS 傳來的 HTTP Request。即便只有一顆 CPU，多執行緒仍能透過排程降低整體回應延遲；MSDN 建議大約每顆 CPU 配 25 條執行緒的上限設定。