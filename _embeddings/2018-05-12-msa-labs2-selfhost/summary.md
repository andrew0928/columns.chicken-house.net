# 容器化的微服務開發 #2 ─ IIS or Self-Host ?

## 摘要提示
- 架構整合: 容器以單一 entrypoint 為核心，Self-Host 能直接對接生命週期，IIS 需額外 ServiceMonitor。
- 環境重疊: Orchestration 與 Reverse Proxy 已涵蓋 Logging、Scaling 等機能，IIS 多屬重覆投資。
- 效能差異: 實測 Self-Host 請求處理速度較 IIS 約提升 17%，相同硬體可擠出更高吞吐。
- 生命週期衝突: AppPool 需先有 Request 才啟動，與 Service Discovery「先註冊再被呼叫」的流程相斥。
- 開發簡化: 以 Console App 為 WebAPI 宿主，程式碼可直接掌握啟動、結束與心跳邏輯。
- 系統訊號: 透過 SetConsoleCtrlHandler 與隱藏視窗攔截 WM_QUERYENDSESSION，可在 shutdown 前釋放資源。
- 心跳機制: 在 Self-Host 內啟動背景 Task，定期向 Consul 送 Heartbeats 以維持健康狀態。
- 範例重構: IP2C WebAPI 改裝成自製 Self-Host，示範 Dockerfile 與 Windows Container 部署。
- 實測驗證: 在 Win10/Server 1709/1803 透過 docker run/stop 驗證訊號攔截與優雅收尾。
- 後續工作: 抽象出通用 Web Host Framework，與 Consul 整合註冊、反註冊與設定管理。

## 全文重點
本文聚焦於「在 Windows Container 中部署 .NET 微服務時，應選擇 IIS Hosting 還是 Self-Hosting？」作者從架構、環境、生命週期與效能四個面向分析：IIS 本身是 Windows Service，與 container「單一行程即 container」的哲學衝突；要在容器內使用 IIS 得仰賴 ServiceMonitor 轉接，使啟停、註冊與反註冊時機難以精準掌握，而 AppPool 的延遲啟動更與 Service Discovery 流程相抵觸。若改採 Console Self-Host，可直接成為 container entrypoint，搭配 SetConsoleCtrlHandler 及隱藏視窗監聽系統訊號，就能在 docker stop、系統關機或使用者關閉視窗時，先移除 Consul 註冊並保留緩衝時間處理未完請求。此外，Benchmark 顯示 Self-Host 效能優於 IIS；IIS 所帶來的 Logging、Scaling、Warm-up 等機能，在微服務＋Orchestration 架構下已由其他元件承擔，留下的只是多餘開銷。文章後段提供範例：將既有 IP2C WebAPI 專案改為 Self-Host，示範註冊、心跳、優雅停機與 Dockerfile 實作，並在 Win10/Server 1709/1803 上測試 docker run/stop 的訊號處理結果。作者最後預告將把本篇機制封裝成共用 Web Host Framework，並進一步介紹與 Consul 的全面整合。

## 段落重點
### IIS Host or Self Host?
作者點出決策對後續 Consul 整合影響重大；對開發者而言兩者 Coding 幾乎相同，但在佈署階段的差異顯著。Container 需要單一 entrypoint 行程，IIS 需借助 ServiceMonitor 監控 w3wp；Self-Host 則直接對應生命週期。若無需 IIS 進階功能，Self-Host 是更貼近容器哲學的選擇。

### THINK #1 架構考量
IIS 為 Windows Service，Web 應用則在 AppPool 中延遲啟動；在容器內難以掌握「何時真正可服務」與「何時確實終止」。Self-Host 只有單一行程，可精準在啟動後立即向 Service Discovery 註冊，結束前確定反註冊，同時避免多個 AppPool 併存、重複註冊的問題。

### THINK #2 環境考量
IIS 提供 Logging、Scale-out、Throttling 等能力，但在微服務世界通常已有 Orchestration、Reverse Proxy、集中式 Log Pipeline 等工具取代。使用 IIS 等於在每個 container 內重覆同一套機制，徒增映像檔大小及系統負載；若把工作交給外部基礎設施，Self-Host 反而能精簡執行環境。

### THINK #3 ASP.NET Application Life Cycle
AppPool 的回收與重建機制會重複觸發 Application_Start/End，對 Consul 註冊造成混亂；延遲啟動也使「先註冊後服務」的需求無法滿足。作者將 AppPool 視為另一層「mini-container」，其職責與現代 Container Orchestrator 重疊，因而建議捨棄。

### THINK #4 效能考量
引用實測資料顯示，在相同硬體下 Self-Host 每秒可多處理約 17% 請求；省去 IIS 解析與額外模組後，容器映像更小、啟動更快。微服務講求水平擴充與資源效率，效能優勢成為選擇 Self-Host 的又一理由。

### 微服務架構下的 Self-Host 實作
作者以 IP2C WebAPI 為例，新增 Console Self-Host 專案：Startup 內設定路由並強迫載入 Controller Assembly；透過 SetConsoleCtrlHandler 與隱藏視窗攔截 CTRL_C、CTRL_SHUTDOWN 等訊號；啟動後立即註冊服務，背景 Task 定時送心跳；接收終止訊號時先反註冊，再延遲 5 秒優雅停機。程式碼同時示範如何把 heartbeats、註冊與反註冊邏輯集中管理。

### DEMO
透過 Dockerfile（以 microsoft/dotnet-framework 基底）構建映像，分別在 Windows 10、Server 1709、Server 1803 測試 docker run/stop；驗證不同版本對訊號攔截與可用收尾時間（1709 約 10 秒、1803 約 5 秒）的差異。Log 中可觀察啟動、心跳、反註冊、延遲停機等流程完整且順序正確。

### 結論
IIS 與 Self-Host 兩種路徑無對錯，但在「容器化＋微服務」場景下，Self-Host 於生命週期控制、效能與環境精簡皆顯優勢；加上 Orchestration 已取代 IIS 多數功能，選擇 Self-Host 更合理。作者已將範例開源，下一篇將把本篇技巧封裝成通用 Web Host Framework，並整合 Consul 完成 Service Discovery、Health Checking 及設定管理。