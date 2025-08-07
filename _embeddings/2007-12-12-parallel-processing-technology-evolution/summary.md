# 平行處理的技術演進

## 摘要提示
- 多核心潮流: CPU 廠商以「多核心」行銷，使軟體必須改採平行思維方能榨取效能。
- 平行程式設計難題: 流程控制、資料交換、Critical Section 與 Lock/Race Condition 是四大挑戰。
- fork 到 thread: 從 Unix fork 到現代 thread，IPC 成本雖降，但問題仍多。
- Java/.NET 改善: 高階平台簡化了 Thread API，卻仍需手動管理生命週期與同步。
- TPL 概念: .NET 3.5 之後的 Task Parallel Library 讓平行拆工如同寫 for 迴圈般容易。
- Delegate 包裝: 透過 delegate 把迴圈工作分派給 Task Manager，自動用盡所有核心。
- TPL vs ThreadPool: TPL 以「任務」為單位進行最佳化排程，和純 ThreadPool 有本質差異。
- C++ 先驅: Intel Threading Building Blocks 為 C++ 社群提供類似理念與範本。
- 平行化優先順序: 先靠函式庫／編譯器，再優化迴圈，最後才考慮手寫多執行緒。
- 技術價值: 將繁雜的同步與分工封裝，讓開發者專注業務邏輯，真正享受多核心效能。

## 全文重點
本文從硬體邁入多核心時代談起，指出唯有「專為多核心設計的軟體」才能發揮效能，而關鍵即是平行處理。作者首先勾勒程式在並行化時必須面對的四大難題：流程控制、跨程序資料交換、Critical Section 與 Lock/Race Condition；並回顧 Unix fork 模式與後來盛行的 thread 如何試圖解決這些痛點，但多數開發者仍需耗費大量心力在同步與通訊，而非商業邏輯。

Java 與 .NET 雖提供較友善的 Thread API，仍須自行決定執行緒何時啟動、結束，與彼此溝通。MSDN Magazine 介紹的 Task Parallel Library（TPL）則將此負擔大幅降低：開發者只須以類似 for 迴圈的新語法（Parallel.For, Parallel.ForEach 等）撰寫程式，TPL 便透過 Task Scheduler 將每一次迴圈迭代封裝為 Task，自動分配至可用核心，並在背景處理同步、負載均衡與資源回收。文中以簡單平方陣列範例示範：傳統 for 迴圈僅用單一執行緒，而 Parallel.For 立即併行執行 100 次運算，無需開發者涉入任何鎖定或訊號機機制。

作者接著點出類似理念早在 C++ 世界出現，Intel Threading Building Blocks（TBB）以 Template 為核心，同樣將平行化常見模式（如 parallel_for）封裝，強調「函式庫／編譯器優先、多執行緒最後」的平行思維。最後作者感嘆技術日新月異：昔日艱辛的多進程/多執行緒程式，如今只須一個高階 for loop 即可完成；呼籲讀者及早掌握 TPL 等工具，才能在多核心浪潮中寫出高效、安全且易維護的程式。文末附上 TPL Tech Preview 下載連結與相關影片，供讀者深入研究。

## 段落重點
### 多核心時代的挑戰
CPU 廠商全面推廣多核心，軟體若仍以單流程思考將無法發揮硬體效能。平行處理就像把工作分給十個員工：分派與管理做得好能提速，不當則可能更慢並增加溝通成本。

### 傳統並行程式設計的困難
真正落實平行化必須處理四大技術門檻：並行流程控制、跨程序資料交換、Critical Section 及 Lock/Race Condition。早期 Unix 的 fork 讓程式分身卻需繁複 IPC；開發者常把八成時間耗在同步而非問題本身。

### Java/.NET 與 Threading 的進步
隨著作業系統加入 thread 觀念，IPC 雖減少但同步仍難。Java 與 .NET 改善了 Thread API，卻依舊要自行管理 thread 生命週期、訊息通知與資源回收，平行程式仍具高度複雜度。

### Task Parallel Library (TPL) 介紹
MSDN Magazine 文章指出，即使在受管環境，Threading 仍過於低階，TPL 應運而生。它以 delegate 將「任務」包裝進 Library，讓平行程序調度變成開發者看似簡單的 for 迴圈寫法，並將排程、負載均衡、同步全交給 Task Scheduler。

### 示範程式與使用心得
作者展示兩段程式：傳統 for 與 Parallel.For。後者將每次迴圈迭代交由 Task 自動分派到所有核心，與 ThreadPool 不同，TPL 針對 Task 類型與關係進行最佳化，讓程式在多核心機器上線性擴充且免除鎖定細節。

### Intel TBB 與平行化思維
平行封裝並非 .NET 專利，Intel Threading Building Blocks 為 C++ 提供 parallel_for、pipeline 等 template。Intel 工程師 James Reinders 強調：優先用函式庫或編譯器自動平行化，再手動優化迴圈，最後才考慮顯式多執行緒，以免過早固化 thread 數量而限制擴充。

### 技術演進的感想與資源
作者回顧從多進程到 TPL 的轉變，感嘆昔日耗時費力的同步如今可由高階 Library 一筆帶過，深感技術革新的價值。文末提供 TPL Tech Preview 下載與 ZDNet 相關影片，鼓勵讀者學習並把握多核心帶來的龐大效能紅利。