# 容器化的微服務開發 #2, IIS or Self Host ?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在容器化的微服務架構中，建議放棄 IIS，改採 Self-Host（Console App）來承載 ASP.NET Web API？
Self-Host 更符合 Docker「一個 container 一個 process」的模型，能直接把 Console Process 指定為 container 的 entrypoint。  
好處包括：  
1. 架構單純，可精確掌握啟動/終止時間點，方便做 Service Registry / Deregistry。  
2. 不再需要為了相容性多包一層 Windows Service ＋ ServiceMonitor.exe，降低複雜度。  
3. IIS 內建的 App-Pool 管理、負載平衡、健康檢查等，在 Orchestration（Swarm／K8s 等）及 Reverse-Proxy 層已經有更合適的替代方案。  
4. 實測效能較佳（Self-Host 每秒 5612 req，IIS8 約 4778 req，提升約 17.5%）。  

## Q: IIS Host 在容器中最大的不便是什麼？
1. IIS 本身是 Windows Service，無法直接當作 Docker Entrypoint。  
2. App-Pool 生命週期與 IIS 再加上一層，導致「服務啟動」及「關閉」事件被多次觸發，難以判斷何時向 Service Discovery 註冊/反註冊。  
3. 必須等第一個 HTTP Request 進來才會真正啟動 App-Pool，與「先註冊才會被呼叫」的微服務流程互相衝突。  

## Q: 在微服務情境下，IIS 提供的 Logging、Warm-Up、負載平衡等功能還需要嗎？
通常不再需要。  
‧ Logging、Scaling、Throttling 可由 Orchestration 平台統一收集與管控。  
‧ Warm-Up、Health-Check 交由 Service Discovery / Orchestrator 或 Sidecar 實作更彈性。  
‧ 多網站共用同一 IP/Port 的需求會交給前端 Reverse-Proxy；每個服務只需對外暴露自己的容器埠即可。  

## Q: Self-Host 與 IIS 的效能差距有多大？
引用實測數據（MVC4 Web API）：  
• IIS 8：每秒 4,778 requests，平均 20.9 ms/req  
• Self-Host：每秒 5,612 requests，平均 17.8 ms/req  
Self-Host 約快 17.5%，且少了 IIS 額外耗用的記憶體與 CPU。  

## Q: 改用 Self-Host 後，開發人員需要自行處理哪些服務生命週期事件？
1. 服務啟動：完成 Web API 啟動後向 Consul 等 Service Discovery 註冊。  
2. 執行中：定期送 Heartbeats 保持服務狀態。  
3. 服務終止：攔截關機／容器停止訊號，先反註冊，再保留緩衝時間讓現有請求完成。  

## Q: 如何在 .NET Console Application（Self-Host）中攔截系統關機或 docker stop 的事件？
‧ 使用 Win32 API `SetConsoleCtrlHandler` 監聽 `CTRL_C_EVENT`, `CTRL_CLOSE_EVENT`, `CTRL_SHUTDOWN_EVENT` 等訊號。  
‧ 再以 Hidden Window 監聽 `WM_QUERYENDSESSION`，可捕捉 Windows 發出的關機/登出訊息。  
‧ 兩者皆觸發 `ManualResetEvent` 喚醒主執行緒，執行 Deregistry、停止 Heartbeat，最後延遲數秒讓請求收尾後關閉程式。