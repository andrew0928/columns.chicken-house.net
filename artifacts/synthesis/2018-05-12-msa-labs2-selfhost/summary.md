# 容器化的微服務開發 #2, IIS or Self Host ?

## 摘要提示
- 架構選擇: IIS 與 Self Host 的選擇會直接影響容器生命週期管理與後續 Service Discovery 整合方式。
- 容器驅動開發: 預設未來必定容器化部署，以刪繁就簡的方式在設計期即對容器最佳化。
- IIS 與容器落差: IIS 為 Windows Service，與容器以單一 EntryPoint Process 管生命週期的模式不合。
- Self Host優勢: 以 Console App 當 EntryPoint，能精準掌握啟動/終止時機，利於註冊與反註冊。
- 環境分工: 微服務下 IIS 多數功能可由 Orchestrator/Reverse Proxy/Logging 替代，非必要組件。
- 應用生命週期: IIS App Pool 的延遲啟動/回收導致註冊時機難控，與 Service Discovery 流程相衝突。
- 效能比較: 自行宿主較 IIS 具優勢（文內引述測試自宿主約快17.5%）。
- 實作步驟: 以 OWIN Self Host 啟動 Web API，補齊組件載入、路由、與事件鉤點。
- 關機處理: 透過 SetConsoleCtrlHandler 與隱藏視窗攔截系統關機訊號，安全完成 De-Register。
- 健康檢查: 啟動背景工作定期送心跳，與停止流程協同收斂，為後續整合 Consul 打底。

## 全文重點
本文聚焦於在微服務與容器化場景中，ASP.NET Web API 應選擇 IIS Hosting 還是 Self Host。作者主張：若以容器驅動開發為前提，自行宿主（Self Host）往往更契合容器生命週期與 Orchestrator 的管理模型。IIS 作為 Windows Service，與容器以單一進程作為 EntryPoint 的設計衝突；再加上 IIS 的 App Pool 運作（延遲啟動、回收與重啟）使服務啟動/終止時機難以精準掌握，造成 Service Discovery（註冊、反註冊、心跳）流程難以正確落位。反觀 Self Host 以 Console App 作為容器的 EntryPoint，可明確控制 Start/Stop，簡化 Dockerfile 與整合程式碼，避免 ServiceMonitor 這類相容性包裝。

環境層面，在微服務分工下，IIS 所提供的記錄、相依組態、縮放、節流、預熱、多站台等功能，通常改由 Orchestrator、Reverse Proxy、集中式日誌與部署系統接手；因此 IIS 在容器中的必要性大幅降低。效能面，文章引述的測試顯示 Self Host 具可觀優勢，符合「用同樣資源榨出更多效能」的目標。

實作方面，作者示範以 OWIN Self Host 啟動 Web API，處理組件載入（避免找不到 Controller）、定義路由，並在可控時機掛上註冊/反註冊與健康檢查的心跳邏輯。為了安全收尾，透過 Win32 API SetConsoleCtrlHandler 攔截 CTRL-C/關閉視窗/系統關機等事件，另以隱藏視窗接收 WM_QUERYENDSESSION，以確保在 OS 強制結束前有短暫緩衝完成 De-Register 與延遲關閉。文中亦記錄 Windows 1709/1803 在 docker stop 與訊號攔截的行為差異與可用時間上限（約 5~10 秒），提示實務上要以忙等/SpinWait 等策略避免被提早中斷。

最後以 Dockerfile 打包，並透過本機與容器兩種情境驗證生命週期訊號與心跳流程是否如預期執行。結論是：在微服務+容器化的架構下，以 Self Host 取代 IIS 可降低整合複雜度、提升對生命周期的掌控與效能；後續可將此 Self Host 架構抽象為通用 Web Host Framework，再掛載 Consul 完成 Service Discovery、Health Check 與設定管理。

## 段落重點
### IIS Host or Self Host?
本文首先界定選擇 IIS 或 Self Host 的關鍵，因其決策將影響與 Consul 等服務發現機制的整合。IIS 屬 Windows Service，容器要求以單一進程為 EntryPoint，兩者在生命週期管理上不一致；再者，ASP.NET 應用還受 IIS 的 App Pool 管理，導致啟動/終止時機與請求驅動模型被動化，使註冊與反註冊的時間點難以掌控。相較之下，Self Host 以 Console App 直入容器 EntryPoint，能精準掌握 Start/Stop，避免多 Pool 並行、延遲啟動等問題；並可將 App Pool 類似的管理工作交由 Orchestrator 統一負責，貼合容器化實務。

### THINK #1, 架構考量
以時間線圖比對 IIS 與 Self Host。IIS 需 ServiceMonitor 監視 w3wp 以銜接容器生命週期，App Pool 可能多次啟停且等首個 HTTP 請求才觸發 Application_Start；這與「先註冊再收流量」的服務發現前提衝突。Self Host 則單一進程、單一生命週期，啟動即能註冊，停止前確保反註冊，架構更單純。由於容器本身即可提供服務守護、重啟與資源管理，將 Windows Service 的角色交由 Docker/Orchestrator 取代更合理。

### THINK #2, 環境考量
IIS 的優點（日誌、App Pool 縮放、節流、預熱、多站台、部署）在微服務+容器化環境多由替代元件承擔：集中式日誌、反向代理/API Gateway、Orchestrator 的擴縮與生命週期、CI/CD 與映像部署等。於是 IIS 在單一服務容器內成為「重複角色」，非必要。微服務提倡一進程一容器，域名綁定、多站台聚合應交由反向代理與服務網格處理。

### THINK #3, ASP.NET Application Life Cycle
IIS App Pool 具延遲啟動、閒置回收、多工 Worker、回收再啟動等設計，以節省資源與維持穩定；但這使開發者僅能在 Application_Start/End 範圍內控制。服務發現流程要求「啟動即註冊、運行送心跳、關閉先反註冊」；若必須等請求才啟動，則與「先註冊才有流量」互斥，且回收造成重複註冊。從本質看，App Pool 類似 IIS 的「小型容器」，在真正容器化後這層管理應由 Orchestrator 負責，避免重疊。

### THINK #4, 效能考量
在無須 IIS 額外功能的前提下，Self Host 減少中介與管理開銷，效能更好。文中引用測試顯示自架宿主每秒請求數高於 IIS 約 17.5%。在微服務分工下，將跨切關注交由專職元件（Gateway、網格、Orchestrator）處理，單一服務進程可用相同資源獲得更高效能與更少複雜度。

### 微服務架構下的 Self-Host 實作
作者以 OWIN Self Host 重新包裝現有 Web API，讓啟動/終止可被精準掌控，為 Service Discovery 與 Health Check 奠基。核心是以 Console App 為宿主，啟動 WebApp 後立即註冊，停止前反註冊，運行期間以背景工作定期送心跳。相較 IIS Host，不再受 App Pool 事件與延遲啟動影響，容器層的 Start/Stop 即是服務事件，整合簡化許多。

### STEP #1, 將 Web Project 改為 SelfHost 模式
利用 OWIN WebApp.Start<Startup> 以程式啟動 Web API，設定路由後需注意 Controller 掃描：IAssembliesResolver 預設只掃已載入的組件，故以對 Controller 類型的參考（輸出訊息）強迫載入，或自訂 AssembliesResolver 以精準控制。此舉確保 Self Host 啟動時所有控制器皆在 AppDomain 中，避免「找不到 Controller」錯誤。

### STEP #2, 處理「啟動」與「終止」
Self Host 啟動成功後即可插入「註冊」邏輯；終止前需插入「反註冊」。以 Console.ReadLine 阻塞只是示範，實務上需改以攔截系統訊號方式來觸發終止流程，確保在容器或系統停止本進程前能優雅收尾，避免遺漏註冊清理與未完成請求。

### STEP #3, 處理系統關機事件
以 SetConsoleCtrlHandler 攔截 CTRL-C、關閉視窗、登出與關機事件；另啟動隱藏視窗攔截 WM_QUERYENDSESSION，將兩路訊號以 ManualResetEvent 匯流，任何一路觸發即開始反註冊與收尾。作者記錄 1709 與 1803 在 docker stop 下可用處理時限差異（約 5–10 秒），且在回應時避免 Thread.Sleep/Wait 造成被 OS 早殺，建議以忙等/SpinWait 撐住關鍵收尾窗口。

### STEP #4, Health Checking
在註冊成功後啟動背景 Task 週期送心跳，主程式於收到終止訊號時設置 stop 旗標並等待心跳任務收斂再行關閉。如此可確保服務在反註冊後仍保留短暫緩衝（例如 5 秒），讓既有請求完成與客戶端快取刷新，符合服務優雅下線的常見實務。

### DEMO
提供 Dockerfile（.NET Framework 4.7.2 runtime, windowsservercore）打包 Self Host，並在本機與容器內驗證啟動、註冊、心跳、停止與反註冊的訊息順序。以 docker run 啟動、docker logs 檢視、docker stop 終止，對比 Windows 10/Server 1709/1803 的日誌行為與訊號攔截差異，驗證生命週期鉤點如預期觸發與可用時間窗是否足以完成收尾。

### Scenario #1, 直接在 Windows 下執行
在 VS 下以無偵錯模式啟動，觀察啟動、註冊、心跳訊息，並以 CTRL-C 或點擊關閉按鈕觸發終止事件，確認不同事件型別（CTRL_C、CTRL_CLOSE）皆能引發反註冊與延遲關閉，最終優雅停止。此步驟驗證 Self Host 在純 OS 環境的生命週期控制是否正確。

### Scenario #2, 透過 Container 執行
以 docker build/run/logs/stop 在不同 Windows 版本測試，觀察 docker stop 時訊號攔截與日誌序列。1709 多依賴 HiddenForm 接收 WM_QUERYENDSESSION，1803 可由 SetConsoleCtrlHandler 攔到 CTRL_SHUTDOWN_EVENT。不同版本可用處理時間略有差異，但整體流程（反註冊、停止心跳、等待緩衝、停止宿主）依序進行，驗證容器場景下的優雅下線。

### 結論
在微服務與容器化前提下，IIS 在容器內多屬重疊責任，且其 App Pool 生命週期與服務發現流程相矛盾；Self Host 能以更低複雜度、更好效能與更精準的生命周期控制支援註冊/反註冊與健康檢查。本文完成 Self Host 範本與生命週期攔截實作，為後續抽象成通用 Web Host Framework 並整合 Consul（Service Discovery、Health Checking、設定管理）鋪路。範例程式碼已公開，將於下篇擴充 Consul 相關能力。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基礎容器概念與 Docker 基本操作（entrypoint、lifecycle、logs、stop/timeout）
   - Windows Container 與版本相容性（1709/1803）差異
   - ASP.NET Web API、OWIN Self-Host 基本用法
   - 反向代理/閘道（API Gateway、Reverse Proxy）與微服務基礎
   - Service Discovery/Consul 與健康檢查的基本概念

2. 核心概念：
   - 容器驅動開發（CDD）：從一開始就假設將以容器部署，剔除多餘的基礎設施依賴
   - Hosting 模式取捨：IIS Host（Windows Service + App Pool）vs Self-Host（Console/單一 Process）
   - 生命週期掌控：精準掌握 Start/End 時點以配合註冊/反註冊與心跳
   - 基礎設施外移：以 Orchestration/Reverse Proxy 取代 IIS 提供的多數運維功能
   - 關機/終止處理：攔截 OS 停止事件（Console Ctrl Handler、WM_QUERYENDSESSION）

3. 技術依賴：
   - .NET Framework ASP.NET Web API + OWIN Self-Host（WebApp.Start<Startup>）
   - Consul（Service Registry、Health Checking、心跳）
   - Docker（Windows Base Image、ENTRYPOINT、EXPOSE）
   - 微服務運維面：Orchestrator（重啟、擴縮、健康檢查）與 Reverse Proxy/API Gateway
   - Windows 平台訊號處理：SetConsoleCtrlHandler、Hidden Form 攔 WM_QUERYENDSESSION

4. 應用場景：
   - 以 Windows/.NET Framework 建置的微服務需容器化部署
   - 需要與 Service Discovery/Consul 精準整合（啟動即註冊、終止即反註冊）
   - 對效能/資源占用在意，盡量減少中介層與重複功能
   - 需統一打造可複用的 Self-Host Host Framework（共用註冊、心跳、關機處理）

### 學習路徑建議
1. 入門者路徑：
   - 了解 Docker 基礎與容器生命週期、ENTRYPOINT 概念
   - 快速搭一個 ASP.NET Web API，改為 OWIN Self-Host 跑起來
   - 用最小 Dockerfile 將 Self-Host 打包並以 docker run 驗證

2. 進階者路徑：
   - 深入理解 IIS App Pool 與容器 lifecycle 的衝突點
   - 練習攔截關機事件（SetConsoleCtrlHandler、Hidden Window）並做優雅關閉
   - 將註冊/反註冊/心跳抽象為共用 Host Library

3. 實戰路徑：
   - 將現有數個 Web API 服務遷移到 Self-Host 樣板（共用 Startup、Host 構件）
   - 整合 Consul：啟動註冊、關閉反註冊、週期心跳/健康檢查
   - 以 Orchestrator/Reverse Proxy 取代 IIS 功能，驗證擴縮、滾動更新與存活性

### 關鍵要點清單
- 容器驅動開發（CDD）：以容器部署為前提做架構簡化，去除多餘依賴（優先級: 高）
- Hosting 取捨（IIS vs Self-Host）：IIS 與容器 lifecycle 不契合，自託管更可控（優先級: 高）
- 容器生命週期與 ENTRYPOINT：單一前景程序存活即容器存活，便於掌握 Start/End（優先級: 高）
- IIS App Pool 問題：延遲啟動/回收導致註冊時機不確定，可能重複註冊（優先級: 高）
- ServiceMonitor.exe 角色：為了讓 IIS 映射到容器前景程序的相容包裝（優先級: 中）
- Self-Host with OWIN：使用 WebApp.Start<Startup> 啟動 Web API，簡化運行模型（優先級: 高）
- Controller 掃描與 Assembly 載入：Self-Host 需確保控制器 Assembly 已載入或自訂 IAssembliesResolver（優先級: 中）
- 啟動註冊與終止反註冊：在 Self-Host 控制流中精準執行（優先級: 高）
- 心跳/健康檢查：以背景 Task 週期送心跳，關閉前停止並留緩衝（優先級: 高）
- 關機事件攔截：SetConsoleCtrlHandler 與 Hidden Form 攔 WM_QUERYENDSESSION（優先級: 高）
- Windows 版本差異：1709/1803 對信號攔截與可用處理時間行為不同（優先級: 中）
- Orchestrator/Reverse Proxy 取代 IIS 功能：擴縮、日誌、暖機、負載均衡由外部解決（優先級: 高）
- 效能差異：Self-Host 相較 IIS 具體測試顯示約 17% 提升（優先級: 中）
- Dockerfile 最小化：以 .NET Framework 基底，ENTRYPOINT 指向自託管可執行檔（優先級: 中）
- 測試情境與時序驗證：在本機與容器環境驗證啟動/心跳/停止序列與日誌（優先級: 中）