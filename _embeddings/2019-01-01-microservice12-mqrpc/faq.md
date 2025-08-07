# 高可靠度的微服務通訊 - Message Queue

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在微服務架構中一定要導入 Message Queue？
Message Queue 具備「高可靠度」與「非同步通訊」的特性：  
1. 即便部分服務掛掉，訊息仍可先排隊等待，被其他存活的服務處理。  
2. 發送端不必同步等待回應，可提升系統吞吐與效能。  
3. 與 CQRS、Event Driven、訂閱/通知等模式天然契合，是微服務間解耦的關鍵核心。

## Q: 作者的團隊最後選擇了哪一套 MQ 解決方案？主要考量是什麼？
採用 RabbitMQ 並搭配 CloudAMQP 託管服務。主因是 RabbitMQ 的 exchange/queue 組合彈性極高，能同時支援可靠傳遞、非同步事件、RPC 等多種情境，而且不受限於特定雲端供應商。

## Q: 什麼是 MessageClient 與 MessageWorker？各自負責哪些功能？
• MessageClient：封裝「發送端」邏輯，只需呼叫 `SendMessage()`/`SendMessageAsync()` 即可把訊息送進指定 queue（或做 RPC 呼叫）。  
• MessageWorker：封裝「接收端」邏輯，長時間監聽 queue；收到訊息後觸發開發者指定的 delegate `Process()` 來處理工作。兩者抽象化後，開發者專注於商業邏輯，不必直接操作 RabbitMQ SDK。

## Q: 作者如何把 MQ 封裝成支援 C# async/await 的 RPC？
1. 每筆請求帶上唯一 correlationId 與 replyTo queue。  
2. MessageClient 送出訊息後，以 `AutoResetEvent` 配合 `await Task.Run()` 非同步等待回覆。  
3. MessageWorker 處理完訊息後，依 replyTo 與 correlationId 回送結果。  
4. Client 端收到回覆即喚醒等待執行緒並回傳 `Task<TOutput>`，讓呼叫者可用 `await` 取得結果，語法層面就像一般 RPC。

## Q: 什麼是 TrackContext？為何需要它？
TrackContext 用來攜帶跨服務的追蹤資訊（例如 request-id）。  
• MessageClient 會把 TrackContext 打包進訊息 header。  
• MessageWorker 收到訊息後先還原並注入 DI Scope，之後所有 service 物件都能直接解析取得同一份追蹤資料。  
如此即可在多服務、多執行緒環境中完整串起同一筆交易的日誌與監控資訊。

## Q: 為什麼必須實作 Graceful Shutdown？作者怎麼做？
在自動擴縮 (auto-scaling) 時，Orchestrator 會動態啟動或關閉容器／VM：  
• 若 Worker 收到關機訊號卻立即中斷，排程中的訊息可能遺失或重複執行。  
• 作者於 `StopAsync()` 先停止接收新訊息、統計尚未完成的工作，待全部 ack 完畢後才真正關閉 channel/connection，再向 OS 回報「可安全關機」，保證訊息 0 遺失。  

## Q: DevOps 中常說的「Design for Operation」是什麼？跟本文有何關聯？
Design for Operation 指在開發階段就把「未來維運」場景納入設計：  
• 服務要能被標準的雲端／容器工具（K8s、Swarm、docker-compose…）直接啟動、縮放與關閉。  
• 本文透過 IHostedService + Graceful Shutdown + 集中 configuration ，使 MessageWorker 能用 `--scale` 一行指令自動擴縮，無需額外自製腳本或人工介入，正是落實 Design for Operation 的實例。

## Q: 架構師除了「技術選型」之外，還需要做什麼？
選型之後更重要的是「整合」：  
1. 先遣部隊要把 RabbitMQ、DI、Logging、Configuration 等基礎建設整合並封裝成團隊專屬 SDK。  
2. 讓其他開發者專注業務邏輯、不必重複學習所有底層細節。  
3. 同時顧及維運需求（如自動化部署、可觀測性、可擴縮性），才能真正提升整體團隊效能。