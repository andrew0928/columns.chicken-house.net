# Tips: 在 .NET Console Application 中處理 Shutdown 事件

## 摘要提示
- Console Shutdown 處理: 在 .NET Console App 內攔截關機/中斷訊號是微服務退場的必要機制。
- SetConsoleCtrlHandler 侷限: 此 Win32 API 只對 Windows Service 生效，無法處理 Container 的 stop。
- Windows Container 困境: docker stop 不會觸發 Console 應用註冊的 CtrlHandler，導致清除動作失效。
- WinForm 隱形視窗技巧: 透過建立隱藏視窗並覆寫 WndProc，可捕捉 WM_QUERYENDSESSION。
- SystemEvents 說明: MSDN 明示只有「有 message pump」的程式才能收到 SessionEnding 事件。
- 最低相依實作: 自行 P/Invoke 建立最小 WinForm，僅負責接收關機訊息並用 AutoResetEvent 通知主執行緒。
- Container 測試流程: build image→run→docker stop→檢視 log，以確認“Service Stopped”訊息被輸出。
- CDD 開發思維: 將所有後端服務做成 Console App + 容器，可簡化部署與環境差異。
- 社群缺乏資料: Google、StackOverflow 幾乎無範例，Windows Container 使用者仍少。
- 後續應用: 解決 Shutdown 問題後，才能實作以 Consul 為核心的 service discovery。

## 全文重點
作者在推行 Container Driven Development（CDD）時，將微服務統一實作為 .NET Framework Console Application，希望在 Windows Container 內透過 docker stop 便能優雅退場並通知 service discovery 移除節點。首先嘗試使用 Win32 的 SetConsoleCtrlHandler，以 P/Invoke 方式攔截 CTRL_C、CTRL_BREAK、LOGOFF、SHUTDOWN 等事件，於本機測試確可響應 CTRL+C 與關閉視窗，但搬進 Windows Container 後，docker stop 並未觸發任何訊號，log 也看不到收尾訊息。進一步閱讀 HandlerRoutine 文件才發現，LOGOFF 與 SHUTDOWN 僅對 Windows Service 有效，Console App 在無 GUI、無 message pump 的情境下收不到這些系統廣播。

為了讓純 Console 程式也能收到關機通知，作者改從 Windows 訊息機制下手。MSDN 的 SystemEvents.SessionEnding 說明提到：「只有 message pump 運作時才會觸發」。因此可在 Console 內動態建立一個隱藏的 WinForm 視窗，讓系統對應的 WM_QUERYENDSESSION 訊息得以被捕捉。作者簡化範例：在 Main 中啟動一條執行緒呼叫 Application.Run(hiddenForm)，主線程以 AutoResetEvent 等待；在 Form.WndProc 偵測到 0x11（WM_QUERYENDSESSION）時設定 Event 並印出 “Shutdown” 訊息。經實測，將此程式封裝成 WindowsServerCore Image，執行 docker stop 後確實能看到 “Service Stopped” 被輸出，證實方案可行。

整體過程彰顯 Windows 出身自 GUI 的歷史：許多系統事件預設只發送給有視窗或 Service 型態的行程；在 Windows Container 中運行 Console App 若需攔截關機，就必須自行補上一層 message pump。作者最後感嘆相關資料稀少，並期許此心得能幫助想在 Windows Container 內開發微服務的人，下一篇文章將接續介紹 Consul 的 service discovery 實作。

## 段落重點
### 容器驅動開發與問題背景
作者推廣 CDD，將服務簡化為 Console App 以利在容器與腳本中執行；為在終止前通知 service discovery，需要攔截程式關閉事件。Windows 主要執行型態有 Service、WinForm 及 Console，其中 Console 最符合容器需求，但必須處理多種結束途徑（Ctrl+C、關閉視窗、Logoff、Shutdown 等）。

### 方法一：使用 SetConsoleCtrlHandler
作者以 P/Invoke 呼叫 Kernel32 的 SetConsoleCtrlHandler，註冊 ShutdownHandler 處理 CTRL_C、CTRL_BREAK、LOGOFF、SHUTDOWN 等訊號，本機測試成功；然而將應用程式封裝進 Windows Container，透過 docker stop 測試時卻無法攔截停機事件，顯示方案在 Container 環境失效。

### Container 測試流程與失敗結果
說明如何 build image、run container、查看 logs，再以 docker stop 測試。結果顯示 container 立即結束且未輸出 “Shutdown Program”，證實 Win32 API 方案對 Console App 於 Container 中無效；多次嘗試與跨版本測試皆相同，Google 與 StackOverflow 亦無解答。

### 方法二：透過 WinForm WndProc
閱讀 MSDN 文件得知只有 Windows Service 或有 message pump 的程式能收 LOGOFF/SHUTDOWN；因此改用隱藏 WinForm。程式在背景執行 Application.Run(Form)，並在 Form.WndProc 收到 WM_QUERYENDSESSION 時喚醒主線程。此做法不依賴 SystemEvents 額外封裝，僅用最低相依的 Win32 訊息即可完成。

### 在 Windows Container 內的成功驗證
將新版程式重新打包為 Image，啟動之後下 docker stop，再查看 logs，可見 “application stopped” 等訊息，表示成功攔截 Shutdown。證明建立隱藏視窗並處理 WndProc 是在 Console App 補足 message pump 的有效方式。

### 結語與未來工作
經過多次嘗試終於完成 Console App 關機攔截，作者感嘆文獻稀缺且 Windows GUI 血統根深蒂固；期待此分享能替日後進入 Windows Container 領域的人鋪路。問題解除後，將繼續撰寫微服務系列文章，實作以 Consul 進行 service discovery。