---
layout: synthesis
title: "Tips: 在 .NET Console Application 中處理 Shutdown 事件"
synthesis_type: faq
source_post: /2018/05/10/tips-handle-shutdown-event/
redirect_from:
  - /2018/05/10/tips-handle-shutdown-event/faq/
postid: 2018-05-10-tips-handle-shutdown-event
---

# Tips: 在 .NET Console Application 中處理 Shutdown 事件

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 .NET Console Application 的 Shutdown 事件？
- A簡: 應用程式即將終止時系統發出的通知，讓程式能在結束前安全釋放資源與收尾。
- A詳: Shutdown 事件是系統或使用者終止應用程式前的通知機制，常見來源包含使用者按下 Ctrl-C/Ctrl-Break、關閉視窗、登出(Logoff)、系統關機(Shutdown)、或容器停止(Container stop)。在 Console App 中，若能正確攔截這些事件，就能在終止前完成註銷服務、釋放連線、寫入最後日志等收尾工作，避免遺漏狀態或髒資料，特別是在微服務與容器情境下更為關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q14, B-Q1

A-Q2: 為什麼在容器與微服務架構中要處理 Shutdown？
- A簡: 為確保服務可預期下線、釋放資源、註銷註冊資訊，避免流量打到無效節點。
- A詳: 在微服務與容器環境，實例常被動態調度與回收。處理 Shutdown 可讓服務於終止前：主動向 service discovery 註銷，從路由清單移除；安全關閉連線、釋放檔案鎖與記憶體；寫入完整運行週期日志，便於追蹤與監控。否則可能出現流量導向已死節點、資源洩漏或不一致，影響穩定性與擴展性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q14, C-Q5

A-Q3: 什麼是 CDD（Container Driven Development）？
- A簡: 以容器為一級公民的開發思維，優先設計可在容器中運行、部署與管理的服務。
- A詳: CDD 是以容器能力為核心的開發模式。開發者將服務設計為可在容器內直接運行的 Console App，依賴容器提供啟動、停止、重啟、日誌、監控與編排能力，減少對 Windows Service 或 IIS 的耦合。這使交付與環境一致性更高，開發、測試、部署過程更簡化，也利於水平擴展與自動化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q3, C-Q4

A-Q4: Windows 常見應用程式型態有哪些？差異為何？
- A簡: Windows Service、Windows Forms、Console App。差異在介面、生命週期與訊息機制。
- A詳: Windows Service在背景無互動，受 SCM 管理，有專屬生命周期；Windows Forms具 GUI 與訊息泵(Message Pump)，可接收各種系統訊息；Console App無 GUI，通常無訊息泵。因機制不同，對系統事件（如關機、登出）的支援也不同，例如某些訊號只送達服務或具視窗的程序。選擇型態須依部署與運作需求決定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q10, B-Q12

A-Q5: Console 應用常見終止來源有哪些？
- A簡: 程式自然結束、Ctrl-C/Ctrl-Break、關閉視窗、登出、系統關機、強制終止等。
- A詳: 典型終止來源包括：1) 程式自行完成流程返回；2) 使用者送出 Ctrl-C/Ctrl-Break；3) 關閉 Console 視窗或工作管理員 End Task；4) 使用者登出；5) 系統關機；6) 非預期終止（強制 Kill、斷電）。不同來源觸發的事件不同，Console App能否攔截與回應亦受限於 OS 與應用型態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q14, D-Q1

A-Q6: 什麼是 SetConsoleCtrlHandler？
- A簡: 一個 Win32 API，可讓 Console 程式處理 Ctrl-C、Ctrl-Break 等控制事件。
- A詳: SetConsoleCtrlHandler 是 Kernel32 提供的 API，可在 Console 行程註冊處理常見控制信號（如 CTRL_C_EVENT、CTRL_BREAK_EVENT、CTRL_CLOSE_EVENT）。理論上也有 CTRL_LOGOFF_EVENT、CTRL_SHUTDOWN_EVENT 常數，但其生效對象與情境有限制。此 API 需經由 P/Invoke 使用，能低相依性攔截部分終止事件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, A-Q7, C-Q1

A-Q7: 為何 SetConsoleCtrlHandler 無法攔截容器中的 docker stop？
- A簡: 登出與關機事件對 Console 不保證投遞，多數情境只送達服務或有訊息泵者。
- A詳: 官方文件註明 CTRL_LOGOFF_EVENT 與 CTRL_SHUTDOWN_EVENT 主要適用於 Windows Service。Console App 在許多情境下不會收到這兩種事件。在 Windows 容器內執行時，docker stop 所觸發的終止過程並未如預期投遞到 Console 控制處理常式，因此實測無法攔截。必須改走具訊息泵的路徑（例如隱藏視窗接收 WM_QUERYENDSESSION）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q10, C-Q2

A-Q8: 什麼是 Windows Message 與 WndProc？
- A簡: Windows 以訊息機制驅動視窗行為，WndProc 是視窗處理訊息的核心方法。
- A詳: Windows 以訊息（Message）傳遞事件，如滑鼠、鍵盤、系統狀態變更等。具視窗的程序會建立訊息泵取得訊息，並由各視窗的 WndProc 處理。系統關機、登出會發送如 WM_QUERYENDSESSION、WM_ENDSESSION 等訊息。若 Console App 能建立隱藏視窗並啟用訊息泵，即可在 WndProc 中攔截這些系統級訊息。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q2

A-Q9: WM_QUERYENDSESSION 是什麼？與何時發生？
- A簡: 系統詢問會話是否可結束的訊息，通常在登出或關機前送出。
- A詳: WM_QUERYENDSESSION 是 Windows 在準備結束使用者會話（登出或關機）前廣播給所有頂層視窗的訊息，讓應用判斷是否允許結束並做收尾。處理時可回傳允許或否決；隨後若系統進一步結束會話，會再送出 WM_ENDSESSION。無視窗的 Console 若未建立訊息泵，無法收到該訊息。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q2, D-Q3

A-Q10: 為什麼在 Console 中建立隱藏視窗能解決問題？
- A簡: 隱藏視窗提供訊息泵，讓程式能接收關機類系統訊息並進行收尾。
- A詳: Console 預設沒有訊息泵，因此收不到 WM_QUERYENDSESSION 等訊息。建立一個不顯示的 WinForms 視窗，啟動 Application.Run 啟動訊息泵，便能在 WndProc 攔截關機與登出訊息，進而同步通知主工作流程完成優雅關閉。此法相依性小、實作直接，且在容器內實測可攔截 docker stop 流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q3, D-Q3

A-Q11: 什麼是 P/Invoke？在文中扮演的角色？
- A簡: 受控程式呼叫非受控 Win32 API 的機制，用於存取 Kernel32 的控制事件處理。
- A詳: P/Invoke（Platform Invocation Services）讓 .NET 程式能呼叫原生 DLL（如 Kernel32）。文中使用 P/Invoke 呼叫 SetConsoleCtrlHandler 以攔截控制事件。此作法相依性低、效能高，但需正確聲明方法簽名與列舉，且受限於 API 本身對不同應用型態的行為差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q1, D-Q9

A-Q12: AutoResetEvent 在關閉流程中的角色是什麼？
- A簡: 用於訊號同步，通知主執行緒停止等待並開始執行收尾工作。
- A詳: AutoResetEvent 提供執行緒間同步。文中主執行緒在 WaitOne 等待，當控制事件或訊息到達時，事件處理器/WndProc 呼叫 Set 發送訊號，喚醒主流程開始關閉與釋放資源。AutoResetEvent 自動重置，避免誤觸發，簡化多次等待的場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q2, C-Q7

A-Q13: 在 Windows 容器中 docker stop 的本質行為為何？
- A簡: 觸發容器內程序的優雅終止流程，對 Console 與服務的投遞機制可能不同。
- A詳: docker stop 目標是優雅停止容器內主要進程。於 Windows 容器，對於不同應用型態（服務/具視窗/純 Console）投遞的訊號與訊息路徑可能不同。實測顯示純 Console 透過 SetConsoleCtrlHandler 收不到會話結束事件，而隱藏視窗的 WndProc 能收到 WM_QUERYENDSESSION，從而完成收尾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q4, D-Q1

A-Q14: 為何選擇 Console 作為微服務執行型態？
- A簡: 簡化開發與部署，配合容器管理生命週期，無需依賴 IIS/Service。
- A詳: Console App 天生輕量、啟動快，輸入輸出直通標準管道，易於與 shell/容器整合。容器提供背景執行、重啟策略、擴縮與編排，取代傳統 Windows Service 或 IIS 的生命周期管理。此模式讓開發者專注業務邏輯，減少宿主耦合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q3, C-Q4

A-Q15: SetConsoleCtrlHandler 與 WndProc 方案差異？
- A簡: 前者攔截控制事件，對關機/登出在 Console 不保證；後者依賴訊息泵可靠收訊息。
- A詳: SetConsoleCtrlHandler 對 Ctrl-C/Close 有效，但關於登出與關機事件主要面向服務；在 Console 與容器中常無法攔截。WndProc 方案透過隱藏視窗與訊息泵，直接處理系統訊息（WM_QUERYENDSESSION），實測能在容器 stop 時生效。取捨在於依賴性與覆蓋面，實務上常需兩者並用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q10, D-Q1


### Q&A 類別 B: 技術原理類

B-Q1: SetConsoleCtrlHandler 如何運作？
- A簡: 註冊控制事件回呼，當 Console 收到 Ctrl-C/Close 等事件時觸發指定處理器。
- A詳: 技術原理說明：透過 P/Invoke 將委派註冊為控制事件處理器。核心步驟或流程：1) 宣告 DllImport("Kernel32")；2) 定義處理委派與事件列舉；3) 在 Main 註冊與解除註冊；4) 在回呼內喚醒關閉流程。核心組件介紹：Kernel32 的 SetConsoleCtrlHandler、處理委派、同步原語（AutoResetEvent）。限制在於 LOGOFF/SHUTDOWN 對 Console 並非保證送達。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q1, D-Q9

B-Q2: 為何 LOGOFF/SHUTDOWN 事件常只傳給服務？
- A簡: OS 針對會話結束事件的投遞以服務與具視窗程序為主，Console 可能收不到。
- A詳: 技術原理說明：Windows 在會話結束時，透過 SCM 與視窗訊息廣播處理。關鍵步驟或流程：1) 系統進入會話結束；2) 向服務發送控制碼；3) 向所有視窗廣播查詢/結束訊息。核心組件介紹：Service Control Manager、Message Pump。因 Console 無視窗且非服務，未必成為投遞對象。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q3, B-Q7

B-Q3: Windows 訊息泵（Message Pump）如何運作？
- A簡: 以迴圈提取訊息並分派至各視窗的 WndProc，是處理系統訊息的基礎。
- A詳: 技術原理說明：Message Pump 執行 GetMessage/TranslateMessage/DispatchMessage 迴圈。關鍵步驟或流程：1) 建立視窗與訊息佇列；2) 迴圈讀取訊息；3) 分派至 WndProc；4) 視窗根據訊息執行動作。核心組件介紹：Application.Run、WndProc、Message 結構。無訊息泵則無法收到如 WM_QUERYENDSESSION 的廣播。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q10, C-Q2

B-Q4: WndProc 在訊息傳遞中扮演什麼角色？
- A簡: 視窗的訊息處理中心，負責針對特定訊息執行對應邏輯並回傳結果。
- A詳: 技術原理說明：WndProc 以 switch/條件分支處理 m.Msg。關鍵步驟或流程：1) 比對訊息代碼；2) 執行對應處理（如結束會話前同步）；3) 設定 m.Result；4) 呼叫 base.WndProc。核心組件介紹：Message、Result、視窗 Handle。處理 WM_QUERYENDSESSION 可回報允許並喚醒主流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q2, D-Q3

B-Q5: 如何在 Console 中啟動訊息泵而不阻塞主流程？
- A簡: 於背景執行緒呼叫 Application.Run(hiddenForm)，主執行緒維持業務邏輯。
- A詳: 技術原理說明：將 UI 訊息泵與業務邏輯分離。關鍵步驟或流程：1) 建立隱藏 Form；2) 以 Task.Run/Thread 啟動 Application.Run；3) 主執行緒 WaitOne 等待訊號；4) 收到訊息時 Set 喚醒主流程。核心組件介紹：Application、Task/Thread、AutoResetEvent。避免阻塞可兼顧事件攔截與邏輯執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q7, D-Q4

B-Q6: 隱藏視窗需要設定哪些關鍵屬性？
- A簡: 設定 ShowInTaskbar=false、Visible=false、WindowState=Minimized，確保不露出。
- A詳: 技術原理說明：視窗需擁有 Handle 與訊息佇列但不干擾使用者。關鍵步驟或流程：1) 建立 Form 實例；2) 設定不顯示於工作列；3) 隱藏或最小化；4) 啟動訊息泵。核心組件介紹：Form 屬性、CreateHandle。這樣可穩定接收系統訊息又不影響互動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q5, D-Q3

B-Q7: WM_QUERYENDSESSION 與 WM_ENDSESSION 有何差異？
- A簡: 前者為詢問能否結束會話，後者表示會話即將或已經結束的通知。
- A詳: 技術原理說明：兩者屬於系統會話終止流程中的不同階段。關鍵步驟或流程：1) 系統送 WM_QUERYENDSESSION 讓應用準備或否決；2) 若繼續，送 WM_ENDSESSION 表示正在結束；3) 應用完成收尾。核心組件介紹：Message 參數與回傳值。實務上處理 WM_QUERYENDSESSION 即可觸發優雅停機。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q2, D-Q3

B-Q8: AutoResetEvent 與 ManualResetEvent 差異與選擇？
- A簡: AutoResetEvent 單次釋放即自動重置；Manual 需手動重置，適合廣播多執行緒。
- A詳: 技術原理說明：兩者皆為事件同步原語。關鍵步驟或流程：Auto：Set 釋放一個等待者後自重置；Manual：Set 釋放所有等待者，需 Reset。核心組件介紹：WaitOne/Set/Reset。關閉流程通常一對一喚醒主線，選 AutoResetEvent 即可避免重入與誤觸發。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q7

B-Q9: 使用 P/Invoke 註冊/解除控制處理器的注意事項？
- A簡: 簽名須正確、委派需保留參考、啟停對稱呼叫避免洩漏與未定義行為。
- A詳: 技術原理說明：P/Invoke 需匹配原生簽名與呼叫慣例。關鍵步驟或流程：1) 正確定義 delegate 與 enum；2) 於程式啟動註冊；3) 關閉前解除；4) 確保委派不被 GC 回收。核心組件介紹：DllImport、GCHandle、Kernel32。錯誤簽名可能導致崩潰或事件不觸發。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q9

B-Q10: docker stop 在 Windows 容器中的訊號傳遞流程是？
- A簡: 觸發容器內主進程的終止流程；不同應用型態的接收路徑不盡相同。
- A詳: 技術原理說明：容器引擎嘗試優雅停止主進程。關鍵步驟或流程：1) 發出終止請求；2) 由 OS 對服務或具視窗程序投遞特定控制碼/訊息；3) 逾時則強制終止。核心組件介紹：容器執行時、作業系統訊號/訊息。實測顯示 Console 的 SetConsoleCtrlHandler 不一定收到，訊息泵方案能補足。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q1, C-Q4

B-Q11: 如何以 docker logs 觀察 Console 的 stdout/stderr？
- A簡: 以 docker logs [-f] 追蹤輸出，容器層級會收集標準輸出與錯誤流。
- A詳: 技術原理說明：容器預設將 stdout/stderr 收集為日志。關鍵步驟或流程：1) 以 -d 背景啟動；2) 使用 docker logs <name> -f 追蹤；3) 停止後再讀取完整輸出。核心組件介紹：日志驅動、stdout/err。這有助於驗證關閉事件是否被攔截與收尾訊息是否出現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q8

B-Q12: Windows Service 如何處理停機與關機？
- A簡: 藉由 ServiceBase 的 OnStop/OnShutdown，或控制碼處理，具完整生命週期。
- A詳: 技術原理說明：服務由 SCM 管理，接收控制碼與關機通知。關鍵步驟或流程：1) 覆寫 OnStart/OnStop；2) 需要時處理 OnShutdown；3) 完成釋放工作。核心組件介紹：ServiceBase、SCM、控制碼。此模式天然支援會話終止相較 Console 更直接。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q7

B-Q13: SystemEvents.SessionEnding 的運作條件是什麼？
- A簡: 僅在訊息泵運行時觸發；服務或 Console 需用隱藏視窗或手動啟泵。
- A詳: 技術原理說明：SystemEvents 依賴 UI 訊息機制。關鍵步驟或流程：1) 建立隱藏視窗；2) 啟動訊息泵；3) 訂閱 SessionEnding；4) 在事件處理中執行收尾。核心組件介紹：Microsoft.Win32.SystemEvents、Application.Run。文件明確指出無泵即不會觸發。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q2, D-Q3

B-Q14: 關閉 Console 視窗與 OS 關機訊息有何不同？
- A簡: 關閉視窗屬於控制事件；OS 關機為會話級訊息，投遞路徑與對象不同。
- A詳: 技術原理說明：Ctrl-C/Close 屬 Console 控制事件；Session Ending 為系統廣播訊息。關鍵步驟或流程：1) 關閉視窗→CTRL_CLOSE_EVENT；2) 會話結束→WM_QUERYENDSESSION/WM_ENDSESSION。核心組件介紹：控制處理器、WndProc。兩者需用不同機制攔截，實務上建議雙軌並用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q15, C-Q10

B-Q15: 跨 Windows 版本與 SKU（桌機/伺服器/容器）的行為一致性？
- A簡: 文章實測多版本行為一致：SetConsoleCtrlHandler 無法捕捉容器 stop 的會話結束。
- A詳: 技術原理說明：OS 與容器對事件投遞策略較固定。關鍵步驟或流程：於 Win10 1709/1803、Win Server 2016/1709 等環境測試。核心組件介紹：OS 版本、容器執行時。結論是行為一致，需以訊息泵方案補強。實務仍建議針對目標環境驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q10, D-Q1


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何以 SetConsoleCtrlHandler 在 Console 攔截 Ctrl-C？
- A簡: 透過 P/Invoke 註冊處理器，於回呼內喚醒收尾流程並安全結束。
- A詳: 具體實作步驟：1) 定義 DllImport("Kernel32") SetConsoleCtrlHandler；2) 定義委派與 CtrlType；3) Main 註冊；4) 回呼中 Set 事件。關鍵程式碼片段：
  DllImport("Kernel32") static extern bool SetConsoleCtrlHandler(Handler h, bool add);
  enum CtrlType { CTRL_C_EVENT=0, ... }
  static bool Handler(CtrlType sig){ shutdown.Set(); return true; }
  注意事項與最佳實踐：僅涵蓋 Ctrl-C/Break/Close，Logoff/Shutdown 在 Console 不保證；註冊與解除需對稱；委派需保持存活。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, A-Q6, D-Q9

C-Q2: 如何在 Console 建立隱藏視窗並用 WndProc 攔截關機？
- A簡: 建立隱藏 WinForms 視窗，背景執行 Application.Run，WndProc 處理 WM_QUERYENDSESSION。
- A詳: 具體實作步驟：1) 新增 Form1，設定 ShowInTaskbar=false、Visible=false；2) 覆寫 WndProc 處理 m.Msg==0x11；3) Main 以 Task.Run(()=>Application.Run(form)) 啟動訊息泵；4) 以 AutoResetEvent 同步。關鍵程式碼片段：
  if(m.Msg==0x11){ m.Result=(IntPtr)1; shutdown.Set(); }
  注意事項與最佳實踐：確保視窗 Handle 建立；不要顯示 UI；回應迅速避免阻塞關機流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q3, D-Q3

C-Q3: 如何將 Console App 打包為 Windows 容器映像？
- A簡: 使用 dotnet-framework runtime 基底映像，COPY 執行檔，ENTRYPOINT 指向主程式。
- A詳: 具體實作步驟：1) 撰寫 Dockerfile；2) FROM microsoft/dotnet-framework:4.7.2-...；3) WORKDIR、COPY；4) ENTRYPOINT 指向 exe。關鍵設定：
  FROM mcr.microsoft.com/dotnet/framework/runtime:4.7.2
  WORKDIR C:\app
  COPY . .
  ENTRYPOINT myapp.exe
  注意事項與最佳實踐：對應目標 OS 版本；最小化映像；避免多餘相依；以 stdout 產生日誌，利於 docker logs。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q14, C-Q4

C-Q4: 如何用 docker 驗證關機事件是否被攔截？
- A簡: 背景啟動容器，docker logs -f 追蹤，執行 docker stop，觀察收尾訊息是否輸出。
- A詳: 具體實作步驟：1) docker run -d --name demo app:tag；2) docker logs demo -f；3) 另窗 docker stop demo；4) 檢視「Shutdown Program.../Service Stopped.」訊息。關鍵指令：
  docker run -d --name demo image
  docker logs demo -f
  docker stop demo
  注意事項與最佳實踐：如日志太快結束可用檔案日志輔助；確保緩衝刷新；必要時加入短暫延遲完成收尾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, A-Q13, D-Q8

C-Q5: 如何在關機前註銷 service discovery（如 Consul）？
- A簡: 攔截關機訊號後呼叫註銷 API，移除節點，確保流量不導向已下線服務。
- A詳: 具體實作步驟：1) 於事件處理器中呼叫 Consul/Etcd 註銷；2) 確認成功回應；3) 再釋放資源並結束。關鍵程式碼片段：
  handler(){ consul.Agent.ServiceDeregister(serviceId); shutdown.Set(); }
  注意事項與最佳實踐：註銷需具超時與重試；確保處理器快速；避免阻塞訊息泵；必要時排程背景工作並立即允許結束。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q3, D-Q7

C-Q6: 如何同時處理 Ctrl-C 與關機訊息以覆蓋多數情境？
- A簡: 以 SetConsoleCtrlHandler 捕捉 Ctrl-C/Close，並用 WndProc 捕捉 Session Ending。
- A詳: 具體實作步驟：1) 註冊 ConsoleCtrlHandler；2) 建立隱藏視窗啟動泵；3) 兩邊回呼皆呼叫同一收尾方法；4) 主執行緒等待事件。關鍵程式碼片段：
  SetConsoleCtrlHandler(Handler,true);
  if(m.Msg==WM_QUERYENDSESSION) OnShutdown();
  注意事項與最佳實踐：避免重入；以旗標確保只執行一次；回呼內快速返回。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q14, D-Q1

C-Q7: 如何設計訊號同步避免阻塞或多次觸發？
- A簡: 以 AutoResetEvent 與一次性旗標協調，保證收尾邏輯只執行一次且不阻塞泵。
- A詳: 具體實作步驟：1) 定義 AutoResetEvent shutdown；2) 定義 volatile bool stopped；3) 在回呼判斷與設置 stopped；4) 主線 WaitOne 後執行收尾。關鍵程式碼片段：
  if(!stopped){ stopped=true; shutdown.Set(); }
  注意事項與最佳實踐：避免在回呼做重工作；在主線處理釋放；必要時用 CancellationToken 協助。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q10

C-Q8: 如何最小化對 WinForms 的相依性？
- A簡: 僅引用 System.Windows.Forms，建最小 Form，禁用視覺樣式，無 UI 控制項。
- A詳: 具體實作步驟：1) 僅建立空白 Form 類別；2) 不載入 Designer 物件；3) 不啟用視覺樣式；4) 僅覆寫 WndProc。關鍵程式碼片段：
  // Application.EnableVisualStyles(); // 可省略
  Application.Run(new HiddenForm());
  注意事項與最佳實踐：避免依賴其他 UI 元件；確保組件版本與目標框架相容；在結束時適當 Dispose。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q6

C-Q9: 如何在容器中可靠擷取最後日志？
- A簡: 使用 stdout 寫關鍵訊息並立即 Flush；必要時同步寫檔並掛載卷。
- A詳: 具體實作步驟：1) 收尾關鍵處 Console.WriteLine 並 Flush；2) 設定 logger 立即寫入；3) 需持久化則寫入掛載卷（-v）。關鍵設定：
  docker run -v C:\logs:C:\logs image
  注意事項與最佳實踐：避免在回呼長時間 IO；必要時簡訊記錄並讓主線處理；確認 docker logs 可見。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q8

C-Q10: 範例：合併控制處理器與 WndProc 的關閉範本？
- A簡: 建立共同 OnShutdown，兩種處理器均呼叫，主線等待事件後釋放與退出。
- A詳: 具體實作步驟與片段：
  static volatile bool stopping=false; static AutoResetEvent ev=new(...);
  static void OnShutdown(){ if(!stopping){ stopping=true; ev.Set(); } }
  SetConsoleCtrlHandler(sig=>{ OnShutdown(); return true; },true);
  class HiddenForm:Form{ protected override void WndProc(ref Message m){ if(m.Msg==0x11){ m.Result=(IntPtr)1; OnShutdown(); } base.WndProc(ref m);} }
  注意事項與最佳實踐：處理一次；快速返回；收尾放主線；測試多種終止情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q6, D-Q10


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 容器執行 docker stop，但無任何關閉日志，怎麼辦？
- A簡: 可能未收到會話結束事件；改用隱藏視窗與 WndProc 攔截 WM_QUERYENDSESSION。
- A詳: 問題症狀描述：docker stop 後容器停止，logs -f 立即結束，未見「Shutdown」輸出。可能原因分析：Console 僅註冊 SetConsoleCtrlHandler，未收到 LOGOFF/SHUTDOWN；或回呼未正確綁定。解決步驟：1) 建立隱藏視窗；2) 啟動訊息泵；3) 在 WndProc 處理 0x11；4) 用 AutoResetEvent 通知主線。預防措施：雙軌處理（控制事件+訊息泵）；於多版本環境驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q2, B-Q10

D-Q2: 程式可攔截 Ctrl-C，卻攔不住關閉 Console 視窗？
- A簡: 需處理 CTRL_CLOSE_EVENT 或使用 Console.CancelKeyPress；確認處理器回傳值。
- A詳: 問題症狀描述：按 X 關閉視窗無收尾。可能原因分析：未處理 CTRL_CLOSE_EVENT；回呼回傳值不正確導致預設行為。解決步驟：1) SetConsoleCtrlHandler 處理 CTRL_CLOSE_EVENT；2) 設回傳 true 表示已處理；3) 迅速喚醒主線。預防措施：測試多種終止來源；避免回呼長時間阻塞。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q6

D-Q3: WndProc 收不到 WM_QUERYENDSESSION，該如何診斷？
- A簡: 檢查是否啟動訊息泵、視窗 Handle 是否建立、是否被阻塞。
- A詳: 問題症狀描述：關機/stop 時無任何 WndProc 訊息。可能原因分析：未呼叫 Application.Run；視窗未建立；WndProc 被長任務阻塞。解決步驟：1) 背景執行 Application.Run(form)；2) 呼叫 form.CreateHandle()；3) 在 WndProc 僅發送訊號快速返回。預防措施：以日志列印收到訊息；避免在 WndProc 進行 IO。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q6, C-Q2

D-Q4: Application.Run 阻塞主執行緒，程式無法工作？
- A簡: 將訊息泵放入背景執行緒，主執行緒維持業務流程與等待事件。
- A詳: 問題症狀描述：主邏輯未執行或被卡住。可能原因分析：在 Main 直接呼叫 Application.Run。解決步驟：1) 以 Task.Run(()=>Application.Run(form))；2) 主線 Console.WriteLine 與 WaitOne 正常運作；3) 事件觸發後收尾。預防措施：避免在 UI 線程執行業務；清晰分工訊息與業務線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q2

D-Q5: 隱藏視窗偶爾出現在工作列，如何避免？
- A簡: 設定 ShowInTaskbar=false、Visible=false、WindowState=Minimized；必要時避免 Activate。
- A詳: 問題症狀描述：任務列出現異常圖示。可能原因分析：預設屬性未正確設定；在建立期間被其他呼叫顯示。解決步驟：1) 建立前設定屬性；2) 禁止顯示任何 UI；3) 測試不同建立時機。預防措施：最小化相依與 UI 操作；只覆寫 WndProc。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q8

D-Q6: 引用 WinForms 會引入過多相依嗎？如何降低風險？
- A簡: 僅引用必要組件並最小化使用，避免 UI 控制項與視覺資源。
- A詳: 問題症狀描述：擔心相依膨脹或部署複雜。可能原因分析：引入完整 UI 框架。解決步驟：1) 僅引用 System.Windows.Forms；2) 不使用 Designer；3) 無任何控制項；4) 僅覆寫 WndProc。預防措施：持續檢視相依；以 Console 為主設計；必要時抽象封裝。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, A-Q10

D-Q7: 關機前註銷 service discovery 不成功怎麼辦？
- A簡: 增加超時與重試，簡化回呼中的工作，將重任移交主執行緒。
- A詳: 問題症狀描述：節點仍留在服務清單。可能原因分析：回呼阻塞或網路抖動；時間不足。解決步驟：1) 回呼只發訊號；2) 主線以短超時呼叫註銷並記錄結果；3) 必要時延遲極短時間等待回應。預防措施：在健康檢查設定短 TTL；服務端也能快速摘除不健康節點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, A-Q2

D-Q8: 為何 docker logs -f 在停止時很快結束，看不到收尾訊息？
- A簡: 容器已停止導致追蹤中斷；需在停止前輸出並 Flush，或改查完整日志。
- A詳: 問題症狀描述：停止當下追蹤中斷。可能原因分析：-f 會在容器停止時退出；日志緩衝未刷。解決步驟：1) 收尾前立刻輸出關鍵訊息並 Flush；2) 停止後不加 -f 再查看；3) 必要時寫檔至卷持久化。預防措施：使用結尾標記行；建立文件日志備援。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, B-Q11

D-Q9: P/Invoke 使用 SetConsoleCtrlHandler 發生異常或無效？
- A簡: 檢查方法簽名、委派生命週期、回傳值與事件列舉是否正確。
- A詳: 問題症狀描述：未觸發或崩潰。可能原因分析：DllImport 簽名錯誤；委派被 GC 回收；enum 錯誤；返回值導致預設行為。解決步驟：1) 對照官方文件修正簽名；2) 保留委派引用；3) 正確處理回傳布林；4) 測試各事件。預防措施：包裝於穩定類別；加強日志。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q1

D-Q10: 關閉回呼中做太多事導致停止緩慢或卡住怎麼辦？
- A簡: 回呼只發訊號，將重工作交給主線處理，保證快速返回。
- A詳: 問題症狀描述：停止耗時或逾時被強殺。可能原因分析：回呼中執行 IO、網路或長任務。解決步驟：1) 回呼僅 Set 事件與記簡訊；2) 主線有條理釋放資源；3) 若有外部呼叫設置短超時與重試。預防措施：建立明確關閉設計；以非阻塞方式完成必要報告。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, C-Q10, A-Q2


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 .NET Console Application 的 Shutdown 事件？
    - A-Q2: 為什麼在容器與微服務架構中要處理 Shutdown？
    - A-Q3: 什麼是 CDD（Container Driven Development）？
    - A-Q4: Windows 常見應用程式型態有哪些？差異為何？
    - A-Q5: Console 應用常見終止來源有哪些？
    - A-Q6: 什麼是 SetConsoleCtrlHandler？
    - A-Q8: 什麼是 Windows Message 與 WndProc？
    - A-Q9: WM_QUERYENDSESSION 是什麼？與何時發生？
    - A-Q10: 為什麼在 Console 中建立隱藏視窗能解決問題？
    - B-Q6: 隱藏視窗需要設定哪些關鍵屬性？
    - B-Q11: 如何以 docker logs 觀察 Console 的 stdout/stderr？
    - C-Q3: 如何將 Console App 打包為 Windows 容器映像？
    - C-Q4: 如何用 docker 驗證關機事件是否被攔截？
    - D-Q2: 可攔截 Ctrl-C，卻攔不住關閉視窗？
    - D-Q8: 為何 docker logs -f 在停止時很快結束？

- 中級者：建議學習哪 20 題
    - A-Q7: 為何 SetConsoleCtrlHandler 無法攔截 docker stop？
    - A-Q11: 什麼是 P/Invoke？在文中扮演的角色？
    - A-Q12: AutoResetEvent 在關閉流程中的角色是什麼？
    - A-Q13: 在 Windows 容器中 docker stop 的本質行為為何？
    - A-Q14: 為何選擇 Console 作為微服務執行型態？
    - A-Q15: SetConsoleCtrlHandler 與 WndProc 方案差異？
    - B-Q1: SetConsoleCtrlHandler 如何運作？
    - B-Q2: 為何 LOGOFF/SHUTDOWN 事件常只傳給服務？
    - B-Q3: Windows 訊息泵（Message Pump）如何運作？
    - B-Q4: WndProc 在訊息傳遞中扮演什麼角色？
    - B-Q5: 如何在 Console 中啟動訊息泵而不阻塞主流程？
    - B-Q7: WM_QUERYENDSESSION 與 WM_ENDSESSION 有何差異？
    - B-Q14: 關閉 Console 視窗與 OS 關機訊息有何不同？
    - C-Q1: 如何以 SetConsoleCtrlHandler 在 Console 攔截 Ctrl-C？
    - C-Q2: 如何在 Console 建立隱藏視窗並用 WndProc 攔截關機？
    - C-Q6: 如何同時處理 Ctrl-C 與關機訊息以覆蓋多數情境？
    - C-Q7: 如何設計訊號同步避免阻塞或多次觸發？
    - C-Q10: 合併控制處理器與 WndProc 的關閉範本？
    - D-Q1: docker stop 無關閉日志，怎麼辦？
    - D-Q3: WndProc 收不到 WM_QUERYENDSESSION，如何診斷？

- 高級者：建議關注哪 15 題
    - B-Q8: AutoResetEvent 與 ManualResetEvent 差異與選擇？
    - B-Q9: 使用 P/Invoke 註冊/解除控制處理器的注意事項？
    - B-Q10: docker stop 在 Windows 容器中的訊號傳遞流程是？
    - B-Q12: Windows Service 如何處理停機與關機？
    - B-Q13: SystemEvents.SessionEnding 的運作條件是什麼？
    - B-Q15: 跨 Windows 版本與 SKU 的行為一致性？
    - C-Q5: 關機前註銷 service discovery（如 Consul）
    - C-Q8: 如何最小化對 WinForms 的相依性？
    - C-Q9: 如何在容器中可靠擷取最後日志？
    - D-Q4: Application.Run 阻塞主執行緒，如何處置？
    - D-Q5: 隱藏視窗偶爾出現在工作列，如何避免？
    - D-Q6: 引用 WinForms 會引入過多相依嗎？
    - D-Q7: 註銷 service discovery 不成功怎麼辦？
    - D-Q9: P/Invoke 使用 SetConsoleCtrlHandler 發生異常？
    - D-Q10: 回呼中做太多事導致停止緩慢，如何改善？