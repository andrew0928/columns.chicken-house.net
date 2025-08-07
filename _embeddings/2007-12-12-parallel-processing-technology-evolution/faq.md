# 平行處理的技術演進

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼叫作「專為多核心設計的軟體」？
專為多核心設計的軟體指的是以平行處理（Parallel Processing）為思維來撰寫的程式。它會將工作拆分並同時分派到多顆 CPU／多個核心上執行，而不是只在單一流程（Single Thread）裡順序完成。

## Q: 在程式設計上實現平行處理常見的困難有哪些？
1. 並行流程的控制  
2. 多個程序／執行緒之間的資料交換  
3. Critical Section（臨界區）管理——某些程式片段不能被同時執行  
4. 資料 Lock 與 Racing Condition（競爭條件）問題  

## Q: 為什麼單靠 Unix 的 fork() 寫平行程式會耗去大量精力？
fork() 會複製出兩份一模一樣的程式同時執行，開發者必須手動判斷誰是父／子行程，並用 IPC（socket、shared memory、signal…）來溝通與同步，往往 80% 以上的時間都在處理溝通與同步，而非真正的業務邏輯。

## Q: Thread 的概念引進後改善了哪些問題？又留下了哪些麻煩？
Thread 減少了部份跨行程通訊 (IPC) 的成本；然而開發者仍需自行決定 Thread 的建立、結束、同步及完成通知等細節，依舊容易出現同步、死鎖、效能不佳等問題。

## Q: 什麼是 TPL（Task Parallel Library）？它帶來了哪些好處？
TPL 是 .NET 3.5 開始提供的平行處理函式庫。它利用 delegate 把「工作」包裝成 Task，並由內建的 Task Manager 自動分派到可用的 CPU 核心執行。開發者只需把傳統迴圈改寫為 Parallel.For/ForEach 等 API，就能輕鬆取得多核心效能，而不必手動管理 Thread。

## Q: 把傳統 for 迴圈改用 TPL 需要做哪些改動？
只要：
1. 將 `for` 換成 `Parallel.For` 或 `Parallel.ForEach`  
2. 把迴圈內容包成一個 delegate（匿名方法或 Lambda）  
其餘運算邏輯不動。TPL 會自動把每次迴圈迭代分派到不同核心上執行。

## Q: 為什麼「直接寫 multi-threading」不是最推薦的平行化途徑？
因為 Threading 必須在架構層面就周全考量，開發、除錯難度高，且通常把 Thread 數量固定死（例如 4 個），在超過該核心數量的機器上就無法再獲得額外效能。相較之下，透過函式庫（TPL、TBB）或編譯器自動平行化會更省時、省心且具備更佳的擴充性。

## Q: 除了 .NET 的 TPL，C/C++ 開發者可以用什麼類似工具來平行化程式？
Intel 大力推廣的開源專案 Threading Building Blocks (TBB) 提供大量 C++ Template，以相似的「把迴圈改寫」方式來自動平行化工作。

## Q: 要在哪裡下載 TPL 的技術預覽 (Tech Preview)？
可以從 Microsoft 官方下載：  
http://www.microsoft.com/downloads/details.aspx?FamilyID=e848dc1d-5be3-4941-8705-024bc7f180ba&DisplayLang=en