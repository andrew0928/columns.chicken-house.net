---
layout: synthesis
title: "Tips: 在 .NET Console Application 中處理 Shutdown 事件"
synthesis_type: summary
source_post: /2018/05/10/tips-handle-shutdown-event/
redirect_from:
  - /2018/05/10/tips-handle-shutdown-event/summary/
postid: 2018-05-10-tips-handle-shutdown-event
---

# Tips: 在 .NET Console Application 中處理 Shutdown 事件

## 摘要提示
- 問題背景: 在 .NET Framework 的 console application 內需安全攔截結束事件以進行收尾與服務註冊解除。
- CDD 目標: 採用 Container Driven Development，優先以 console app 搭配容器簡化部署與運維。
- 常見結束觸發: 包含程式自行結束、Ctrl-C/Ctrl-Break、關閉視窗、登出、系統關機、非預期終止。
- 初始方案限制: SetConsoleCtrlHandler 僅對部分事件有效，且 LOGOFF/SHUTDOWN 僅對 Windows Service 生效。
- 容器情境落差: 在 Windows Container 中，docker stop 無法被 SetConsoleCtrlHandler 的 console app 捕捉。
- 核心洞見: Windows 的關機/登出事件在訊息泵機制中最穩定，WinForms/WndProc 天生可接收。
- 替代解法: 在 console app 建立隱藏視窗並以 WndProc 攔截 WM_QUERYENDSESSION 等訊息以處理 shutdown。
- 技術關鍵: 以 Application.Run 啟動訊息泵；在隱藏視窗中以 AutoResetEvent 與主執行緒同步收尾。
- 減少相依: 不依賴 SystemEvents，高內聚地直接覆寫 WndProc 以避免額外庫的耦合。
- 實務價值: 使 console 應用在 Windows Container 中能優雅停止，支援 service discovery 正確下線。

## 全文重點
作者為了在微服務場景中導入 service discovery（以 Consul 為例），希望所有後端服務以 .NET Framework 的 console application 形式運行並部署於容器。為確保容器停止或系統關機時能優雅下線，程式需攔截終止事件以主動通知服務發現機制，避免殘留註冊紀錄。初期作者採用 Win32 API 的 SetConsoleCtrlHandler，該方法能處理 Ctrl-C、Ctrl-Break、關閉視窗等，但在關鍵的登出與系統關機事件上，實測在 console app 與 Windows Container 情境無效。深入查閱文件後發現，CTRL_LOGOFF_EVENT 與 CTRL_SHUTDOWN_EVENT 只對 Windows Service 有效，導致 console app 在 docker stop 等關機流程無法收到對應訊號。於是作者改以 Windows 訊息泵體系切入：在 console app 內建立一個隱藏的 WinForms 視窗，啟動 Application.Run 以具備 message pump，並在表單覆寫 WndProc 攔截 WM_QUERYENDSESSION 等關機訊息。當訊息抵達時，透過 AutoResetEvent 喚醒主程式執行收尾流程，進而實現優雅停止。此法不依賴 SystemEvents 類別，減少多餘相依，同時在 Windows Container 中實測可穩定攔截 docker stop 觸發的停機訊號。整體過程顯示，雖然 console app 是容器化的理想型態，但在 Windows 平台上，關機流程與訊息處理深受 GUI 起家的設計影響；要在非服務的進程中可靠攔截停機，仍需借力 message pump 機制。最終方案讓 console 應用能在容器停止時確實釋放資源、撤銷註冊，符合微服務下動態生命週期管理的需求，為後續 service discovery 實作鋪路。

## 段落重點
### 前言與背景：CDD 與 console app 的必要性
作者以 CDD（Container Driven Development）為核心理念，主張服務以 console application 形式搭配容器部署，可大幅簡化後台執行、啟停控制與擴縮。為確保與 service discovery 整合，在程序終止前必須主動撤銷註冊，避免健康檢查誤判與殘留紀錄。Windows 常見可執行型態有 service、WinForms 與 console，其中 console 最契合容器使用情境。然而終止來源多樣：從 Ctrl-C、關閉視窗、登出、關機到非預期終止，如何在 console app 中可靠攔截並優雅收尾，是後續微服務實作的關鍵前置問題。

### (Win32API) SetConsoleCtrlHandler
作者首先選用 SetConsoleCtrlHandler（透過 P/Invoke 調用 Kernel32）攔截控制事件。此法在本機互動測試能處理 Ctrl-C、Ctrl-Break、關閉視窗等狀況，並以 AutoResetEvent 與主執行緒同步，達到乾淨收尾。最初測試顯示行為正常，導致作者誤以為可涵蓋登出與關機場景，忽略了更嚴苛的系統事件與容器情境測試，為後續踩雷埋下伏筆。

### 搬到 Windows Container 內測試
進一步以 Windows Container 驗證：將 console app 打包成映像，啟動容器觀察日誌，再以 docker stop 停止，期待看到 shutdown 日誌與收尾流程。實測發現 docker stop 觸發時，容器直接終止，程式未能攔截到停機訊號，日誌缺少關機處理輸出。多個 Windows 版本（Win10 1709/1803、Server 2016/1709）結果一致。追溯官方文件得知，SetConsoleCtrlHandler 的 CTRL_LOGOFF_EVENT 與 CTRL_SHUTDOWN_EVENT 僅對 Windows Service 保證觸發，console app 並非適用對象，難以在容器內捕捉 docker stop 對應的停機流程。

### (WinForm) 從 WndProc 下手
轉而採用 Windows 訊息泵機制：參考 SystemEvents.SessionEnding 的說明，該事件僅在 message pump 運行時觸發；若在非 GUI 程式可建立隱藏視窗或手動啟動訊息泵。作者在 console app 中建立隱藏的 WinForms 視窗並啟動 Application.Run，於表單覆寫 WndProc 攔截 WM_QUERYENDSESSION 等訊息，接收到後以 AutoResetEvent 通知主執行緒進行收尾。此作法不依賴 SystemEvents 類別，直接操作 WndProc 降低相依。於 Windows Container 中實測，docker stop 能被攔截並完成優雅停止，符合預期。

### 總結與反思
最終方案證實：在 Windows 平台上，console app 若需可靠攔截關機/登出，需借助 GUI 的訊息泵；以隱藏視窗承接訊息是有效策略。雖然看似「為了 console 還得引入 WinForms」有點繞路，但能換取容器中可預期的停機處理，對微服務的服務註冊解除與資源釋放至關重要。此議題在社群與文件中資訊稀少，顯示 Windows Container 的 console 模式停機攔截尚屬冷門。問題解決後，作者將續推微服務系列，著手 service discovery（Consul）實作，並期望此經驗為日後採用 Windows Container 的開發者避坑。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - .NET Framework 與 Console Application 基本結構
   - Windows 作業系統的訊息機制（Windows Message、Message Pump）
   - P/Invoke 基本概念（呼叫 Win32 API）
   - Docker 與 Windows Container 基礎操作（build/run/stop/logs）
   - 微服務與 Service Discovery（如 Consul）對「優雅關閉」的需求

2. 核心概念：
   - Console 關機事件攔截的限制：SetConsoleCtrlHandler 在 Console 下無法接到 LOGOFF/SHUTDOWN
   - Windows Message Pump 的重要性：只有有 Message Pump 的進程才能收到系統 Session 結束/關機訊息
   - 隱藏視窗策略：在非 WinForms（Console/Service）中建立隱藏表單以接收 WM_QUERYENDSESSION
   - 容器內的關閉流程：docker stop 如何傳遞終止訊號給應用並影響訊息接收
   - 優雅關閉流程：在被通知前釋放資源、回報 Service Discovery、寫入日誌

3. 技術依賴：
   - .NET Framework Console App 需依賴 WinForms（System.Windows.Forms）以建立隱藏視窗與 Message Pump
   - Win32 API 與 P/Invoke（SetConsoleCtrlHandler）僅能處理部分 Console 訊號（CTRL_C/BREAK/CLOSE）
   - Windows OS 訊息（WM_QUERYENDSESSION）才能正確攔截系統的 Logoff/Shutdown
   - Docker Windows Container 基底映像與 Windows 版本相容性
   - 日誌與同步原語（AutoResetEvent）用於主流程與訊息處理同步

4. 應用場景：
   - 在 Windows Container 內的 .NET Framework Console 服務需要優雅關閉（graceful shutdown）
   - 微服務下線前必須從 Service Discovery（如 Consul）註銷
   - 需要處理系統關機、使用者登出造成的服務中止
   - 不希望改成 Windows Service 或 WinForms，但又要接收關機事件的 Console 應用

### 學習路徑建議
1. 入門者路徑：
   - 了解 Console App 基本結構與 Docker Windows Container 基礎指令（build/run/logs/stop）
   - 實作最簡單的 Console 長時程程式（WaitOne 迴圈＋日誌）
   - 嘗試 SetConsoleCtrlHandler，理解能處理與無法處理的事件差異

2. 進階者路徑：
   - 研究 Windows Message Pump 與 WM_QUERYENDSESSION、SystemEvents.SessionEnding
   - 在 Console App 中建立隱藏表單（WinForms），以 Application.Run 啟動 Message Pump
   - 在 WndProc 攔截 WM_QUERYENDSESSION 並與主執行緒同步（AutoResetEvent）

3. 實戰路徑：
   - 打包 Docker 映像（撰寫 Dockerfile，指定 ENTRYPOINT）
   - 實測 docker run（背景執行）與 docker logs -f 觀察輸出
   - 使用 docker stop 驗證是否能攔截關閉事件，並在 Handler 中實作：釋放資源、註銷 Service Discovery、輸出完整生命週期日誌

### 關鍵要點清單
- Console 關機事件限制：SetConsoleCtrlHandler 無法在 Console 收到 LOGOFF/SHUTDOWN（僅 Service 可） (優先級: 高)
- CTRL 訊號可行範圍：CTRL_C/CTRL_BREAK/CTRL_CLOSE 可由 SetConsoleCtrlHandler 處理 (優先級: 中)
- Windows Message Pump：要接收 Session/Shutdown 類訊息必須有 Message Pump (優先級: 高)
- 隱藏視窗策略：在 Console 內建立隱藏 WinForm 啟動 Application.Run 以取得訊息 (優先級: 高)
- WndProc 攔截：使用 WndProc 攔截 WM_QUERYENDSESSION 做關閉前處理 (優先級: 高)
- 同步機制：用 AutoResetEvent 在訊息處理與主流程間同步關閉步驟 (優先級: 中)
- SystemEvents.SessionEnding：替代路徑但同樣需要 Message Pump；可做為參考 (優先級: 低)
- Docker stop 與訊號：docker stop 對 Windows Container 不會等同於 Linux SIGTERM；需以 OS 訊息處理 (優先級: 高)
- 優雅關閉流程設計：在通知到達時，先記錄日誌、釋放資源、註銷 Service Discovery、再結束 (優先級: 高)
- 測試矩陣：需於多版本 Windows（Win10/Server/1709/1803）與 Container 基底測試行為一致性 (優先級: 中)
- 相依性最小化：直接用 WndProc 與少量 WinForms，避免過度依賴高階封裝 (優先級: 中)
- 容器化實務：撰寫正確的 Dockerfile、使用 ENTRYPOINT、以 logs -f 觀察 runtime 輸出 (優先級: 中)
- 失敗案例教訓：僅用 SetConsoleCtrlHandler 測 CTRL-C 容易誤判整體可行性 (優先級: 中)
- 安全關閉不可預期狀況：強制終止/斷電無法保證觸發事件，需設計復原與冪等註銷機制 (優先級: 中)
- 微服務整合：與 Consul 等 Service Discovery 整合時，將註銷步驟放入關閉處理流程 (優先級: 高)