---
layout: synthesis
title: "高可靠度的微服務通訊 - Message Queue"
synthesis_type: summary
source_post: /2019/01/01/microservice12-mqrpc/
redirect_from:
  - /2019/01/01/microservice12-mqrpc/summary/
---

# 高可靠度的微服務通訊 - Message Queue

## 摘要提示
- RabbitMQ 選型與整合: 採用 RabbitMQ/CloudAMQP 作為通訊中樞，因其彈性的 exchange/queue 組合可支援各種同步與非同步模式。
- 團隊專屬 SDK: 以抽象化/封裝打造 MessageClient、MessageWorker，降低開發者直接面對 MQ SDK 的負擔。
- 單向訊息封裝: 以泛型與簡潔介面隱藏連線、序列化與 headers 處理，標準化 send/receive 流程。
- 背景服務模型: 依 .NET IHostedService/BackgroundService 規範實作 MessageWorker，符合長駐背景服務的標準生命週期。
- 多執行緒與 Graceful Shutdown: 以多 channel/consumer 提升併發，並精準收斂未完成任務以達優雅關閉。
- RPC 與 async/await: 以 reply_to/correlation_id 實作雙向 RPC，並用 Task/await 提供自然的非同步 API。
- 事件同步技巧: 以 AutoResetEvent/WaitHandle 實作 wait/notify 與 buffer/waitlist 對應回傳結果。
- TrackContext 傳遞: 將跨服務追蹤資訊封裝於 headers，並與 DI Scope 整合，確保端到端可觀測性。
- Design for Operation: 從設計即考慮維運需求，讓服務可被自動化擴縮、註冊、更新設定與關閉。
- 容器與關機訊號: 針對 Windows/Linux 與 .NET Framework/Core 差異提供擴充做法，確保能正確攔截 OS 關機並配合編排工具 scaling。

## 全文重點
本文以「整合」為核心，說明在微服務架構下如何以 RabbitMQ 打造高可靠度的通訊體系，並以團隊專屬 SDK 的抽象化與封裝降低使用門檻。作者先從需求出發，不直接把底層 MQ 細節暴露給開發者，而是設計 MessageClient（送訊息）與 MessageWorker（收訊息並處理）的清晰介面。單向通訊中，MessageClient 隱藏連線、宣告、序列化與 headers，開發者只需傳入泛型訊息模型即可；MessageWorker 則依 IHostedService/BackgroundService 規範實作，具備標準化的啟閉流程與可配置的併發度。

在效能與關閉安全性上，作者強調多執行緒與多 channel/consumer 的佈局，避免單 channel 序列化造成瓶頸；同時以計數器與 AutoResetEvent 等 wait/notify 機制，確保 StopAsync 會停止接收新訊息、等待既有處理完成、最後才釋放資源，達成 Graceful Shutdown。這一點對於日後與容器/雲端編排器進行自動擴縮尤為關鍵，因為縮容時若不能優雅關閉，容易造成訊息遺失或重試混亂。

雙向 RPC 的設計採用 RabbitMQ reply_to 與 correlation_id，在 client 端建立專用 reply queue 並共用現有連線/通道，以 AutoResetEvent 與 buffer/waitlist 對應 correlation_id 等待結果，將阻塞等待包裝成 Task 以支援 async/await，讓使用體驗與一般遠端呼叫一致。相比「兩次單向」的直觀實作，此封裝更符合實際情境：每個 client 擁有短暫 reply queue、可共用、可回收，且不必啟動笨重的 worker 流程。

跨服務追蹤（如 request-id）以 TrackContext 抽象，隨消息 header 傳遞。MessageClient 在送出時注入；MessageWorker 在接收時建立新的 DI Scope 並寫入 TrackContext，確保處理函式在正確範疇內解析到一致的追蹤資訊。這種與 DI 深度整合的設計，讓認證、授權、觀測性等 AOP 機制能自然落位。

接著作者從 DevOps/Design for Operation 的角度出發，指出自動擴縮並非僅是基礎建設問題；應在設計階段就規畫好系統啟閉行為、設定集中化、標準部署產物與 pipeline 整合，使維運能直接以編排工具（Docker Compose、Swarm、K8s）控制 instance 數，而應用可自我管理啟閉與註冊。對於 OS 關機訊號的應對，文中列舉 Windows/.NET 在不同組合下的實測結果，並提供 Win32 訊號攔截的 Host 擴充以彌補差異，最終展示以 docker-compose scale 指令動態擴縮 consumer，過程中可觀察到 Worker 停止接收新任務、等待已在途任務完成後再關閉，驗證整體設計可與基礎設施無縫配合。

最後，作者總結兩大主張：一是由少數先遣者先整合與封裝基礎建設，打造團隊專屬 SDK 以提升統一性與效率；二是設計可被維運的服務，讓應用貼合主流編排與雲端平台的操作模式，真正把 Dev 與 Ops 連成閉環，持續優化。

## 段落重點
### 前言與問題背景
作者以在 .NET Conf 2018 的分享為引，指出 Message Queue 是高可靠度與非同步通訊的核心。架構師不僅要做技術選型，更要把各項技術「整合」給團隊使用；不同團隊在商業需求、歷史包袱與組成上皆異，需要因地制宜的封裝與抽象。本文以 RabbitMQ 為通訊骨幹，目標是建立能串接可靠通訊、事件驅動、CQRS、訂閱/通知等機制的團隊體系，並從程式碼層幫助開發者。文章會涵蓋：如何把 MQ 封裝為 RPC 並支援 C# async/await、如何與環境與 DI 整合，以及如何做到 Design for Operation 以自我管理與自動擴縮。作者也分享個人知識累積的連結性：多執行緒、平行處理、Docker/Linux 等經驗最後都匯流於此，強調宏觀與持續累積的重要。

### 團隊專屬 SDK: 通訊機制封裝
跨服務通訊不僅是簡單的 REST 呼叫，還包含共享資料庫、事件驅動、事件溯源、同步/非同步混合等。RabbitMQ/CloudAMQP 被選為通訊管道，因其彈性與可組合性；然而官方 sample 雖簡潔但實務上要處理連線、宣告、序列化、設定、權限與 headers 等細節，成本高且易不一致。作者主張先抽象需求並封裝後再推廣使用，讓開發者專注於業務訊息格式。為此設計 MessageClient（單向送出，傳回 correlationId）與 MessageWorker（定義處理委派、Start/Stop 與背景執行），其餘環境細節透過 options 與 DI 注入。此 SDK 以泛型承載訊息模型，序列化使用 JSON，並引入 TrackContext 供跨服務攜帶追蹤資訊，與 HTTP cookie 類似，但經由 MQ headers 傳遞。

### 抽象化: Message Client / Worker
MessageClient<T> 提供 Send 介面，將 routing key、訊息與自訂 headers 打包並傳回 correlationId。MessageWorker<T> 暴露委派 MessageWorkerProcess 供使用者自定處理邏輯，並提供 StartAsync/StopAsync 啟閉。以委派定義處理函式的簽章，讓業務邏輯集中在 message 的內容處理，通訊與生命週期細節則隱藏在 SDK 內。此分工讓團隊在一致介面下開發多個工作者，減少重複樣板與錯誤機會。

### 單向傳遞: MessageClient 介面定義
MessageClient 透過 MessageClientOptions 取得連線、exchange/queue、bus 類型等配置；建構時可由 DI 注入 TrackContext 與 Logger。SendMessage 封裝序列化與 publish，並帶上 correlationId 與 TrackContext 的 headers。訊息 body 僅要求可 JSON 序列化，降低耦合。此層把 RabbitMQ 連線、通道、宣告、屬性設置統一處理，開發者以最少程式即能發送大量訊息，並可與團隊既有的設定/安全/記錄機制協作。

### 單向傳遞: MessageWorker 介面定義
MessageWorker 繼承 BackgroundService，符合 .NET Core IHostedService 範式，讓 worker 可由 Host 啟閉、與其他 hosted services 一致管理。內部僅暴露委派供處理訊息，啟閉由 StartAsync/StopAsync 控制，邏輯線路清晰。示例中以多 worker threads 與 Prefetch 配置搭配 BasicConsume，將收到訊息交由委派處理。主執行緒啟動後等待關閉指令，StopAsync 觸發優雅關機。此一模型對接容器與雲端編排極為自然。

### MessageWorker: 多執行緒平行處理
Worker 啟動後建立多組 channel/consumer 以提升併發（RabbitMQ 官方不建議跨執行緒共享 channel 並序），每個 consumer 綁定 Received 事件並設置 QoS。StopAsync 發出時，先解除事件綁定停止接收新訊息，再等待在途訊息處理完畢才關閉 channel/connection。等待過程以計數器+AutoResetEvent 準確喚醒與收斂，避免忙等。此設計兼顧效能與正確性，為後續自動縮容、滾動更新、故障切換鋪路。

### 啟動 MessageWorker 的程序
ExecuteAsync 內完成初始化：宣告 queue、依 worker 數建立多個 channel/consumer，消費開始後便阻塞等待 stoppingToken；當 Stop 觸發時，先移除事件處理器、停止接收，再以 WaitHandle 等待計數器歸零，最後釋放通道與連線。以此確保生命週期可被 Host 正確管理，且不遺留未處理訊息或中途終止。這段程式雖短，卻完整描述了一個可運維的背景服務的啟停協定。

### 停止 MessageWorker 的程序
關閉流程的關鍵在於切斷新訊息來源、等待在途完成、再釋放資源。由於 RabbitMQ 文件對終止程序著墨不多，作者採試驗法訂出順序：先拔掉 consumer.Received 避免新訊息進入處理，未 ack 的訊息會在關閉後回到 queue；透過 threadsafe 計數器追蹤在處理中的任務，以 AutoResetEvent 喚醒等待迴圈，達到精準、即時的收斂，避免 pooling。最後依序關閉 channels/connection，避免提早關閉導致 ack 失敗。此流程是支援編排器安全縮容的必要條件。

### 雙向通訊: RPC
基於官方教學，客戶端以 reply_to 指定回覆 queue，並以 correlation_id 區分請求-回覆關聯；伺服端處理完後根據原訊息的 reply_to/correlation_id 回送結果。此模式下 client/server 互為 producer/consumer，組成雙向通訊。挑戰在於要把 sample code 提升為可重用、可擴展、效能佳的 SDK：避免回覆排隊延遲、讓 reply queue 可共用與自動回收、減少額外通道與執行緒成本，並提供優雅的 API。

### 有效率的 RPC 封裝: async / await
在 API 設計上，作者將單向 Send 擴展為泛型 MessageClient<TInput,TOutput>，並提供同步/非同步兩種 Send（回傳 TOutput 或 Task<TOutput>），讓使用端以 await 或 Task.WaitAll 並行等待多筆回覆。此設計貼近 C# 語法體驗，隱藏網路延遲與隊列傳遞，使 RPC 調用像本地函式。Worker 端委派亦調整為回傳 TOutput。範例展示先 await start，再同時送 10 筆工作並一次 WaitAll 接回，最後 await end，驗證介面自然、易讀且具備併發能力。

### MessageClient RPC 實作
為降低重量與耦合，RPC 回覆端不再內嵌一個 Worker，而是在 Client 內建立一個臨時 reply queue 與單一 consumer，共用既有連線/通道。以字典 buffer 與 waitlist（AutoResetEvent）根據 correlation_id 暫存回覆與喚醒等待者。ReplyQueue_Received 反序列化後放入 buffer，Set 對應 wait；SendMessageAsync 在 publish 後建立 wait，await Task.Run(() => wait.WaitOne()) 等待喚醒，再取回 output 並清理。此模式精煉、資源友善，滿足多 RPC 並發共用一個 reply queue 的需求，也保留了高效同步機制。

### 跨服務的 (Track)Context 轉移
微服務要做端到端追蹤，需在服務邊界生成 request-id 類追蹤資訊，並在各通訊管道中傳遞。作者將其抽象為 TrackContext 透過 headers 傳輸，並與 DI 整合：MessageClient 由 DI 注入 TrackContext 並在送出時寫入 headers；MessageWorker 每次收到訊息就建立新的 Scope，從 headers 還原 TrackContext 注入該 Scope，使處理委派在正確上下文中執行。此作法避免在每層函式顯式傳遞參數，也讓認證、日誌、追蹤等橫切關注點可在適當範圍解析到一致資料，減少遺漏風險。

### Auto Scaling
作者從 DevOps 核心出發，主張開發與維運的緊密迭代，並在設計期就思考系統如何被維運（Design for Operation）。自動擴縮的本質要求應用能自我管理啟動與關閉：新增實例時自動連線投入工作；縮容時能優雅停止接收、等在途完成、再關機。團隊應檢視設定集中化、部署產物一致性與 CI/CD 流程銜接，避免把複雜度留在手工腳本。若應用能遵循標準關機訊號並正確關閉，就能由編排工具直接控制副本數而不需開發自製運維平台。

### DevOps Concepts
多數團隊把 DevOps 簡化為部署自動化，忽略了從運維反饋回開發、設計可維運性的本質。作者提出檢核：是否需仰賴開發人員操作才能 scaling？管理面用雲商原生工具還是自製平台？過程能否全自動？耗時是否可控？正確途徑是讓應用遵循通用的啟閉協定與配置策略，讓 SRE 以 infra 手段完成擴縮與滾更；否則自製工具將疊加維護負擔且難與主流平台對齊。

### Design For Operation
落地上，重點在把 infra 與 app 的責任邊界釐清：集中設定、單一產物、多環部署無需重打包、pipeline 與 artifact 管理貫通。Graceful Shutdown 是縮容的關鍵拼圖，但也需思考啟動流程的自動化與治理。作者主張對齊 infra 團隊成熟做法，避免以腳本「自動化複雜度」。最終目標是運維只需調整副本數，應用即可自動進場/退場，無需人手介入特製步驟。

### Labs: Handling OS Shutdown
作者實測在不同 OS/Runtime/Container 組合下攔截關機訊號的情況：Linux 容器最穩定；Windows/ .NET Framework/Core 在某些版本下有缺陷。為此提供 WindowsHostExtensions 以 Win32 SetConsoleCtrlHandler 補齊，並與 IHost 擴充方法整合（WinStart/WaitForWinShutdown），在不改整體架構下確保能接收 OS 關機並呼叫 StopAsync，等待在途完成。此 workaround 讓 Windows 環境亦可達成設計目標，等待 .NET/Windows 未來版本完善。

### Labs: MessageWorker Auto Scaling
示範以 docker-compose 部署 RabbitMQ、client（producer）、server（consumer），並用 --scale 動態調整 consumer 實例數。觀察 logs 可見擴容時新 worker 直接加入處理；縮容時收到關機訊號即停止新任務、等待既有任務完成後結束。此驗證了 MessageWorker 的生命週期與 graceful 關閉設計能與容器編排工具配合，而觸發來源只需標準 OS 關機訊號，適用於實機、VM、單機容器與叢集編排（Swarm/K8s/雲端容器服務）場景。

### 後記
作者強調兩點：其一，先遣整合比工具選型更重要。面對眾多 OSS/PaaS，應由少數具備廣度與工程素養的人先打樣、封裝為團隊專屬 SDK，讓大多數開發者在一致介面下生產，避免直接暴露多元 SDK 與環境耦合。其二，設計可被維運的服務。以 Graceful Shutdown 為例，若應用能與編排工具標準流程對齊，SRE 便可用既有平台順手維運，團隊無須自建管理系統。當開發者親身參與運維，便能體會 design for operation 的必要，從而讓系統更容易貼合主流平台與最佳實踐。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C#/.NET（泛型、委派、async/await、Task、執行緒與同步原語）
   - RabbitMQ 基礎（exchange、queue、connection/channel/consumer、ACK、QoS prefetch）
   - 依賴注入與 .NET Generic Host（IHost、IHostedService、BackgroundService、DI Scope）
   - 序列化（JSON/Newtonsoft.Json）、結構化日誌與追蹤（request-id 概念）
   - 容器與編排（Docker、docker-compose、基本 Auto Scaling 概念）
2. 核心概念（3-5 個）及其關係：
   - MQ 驅動的通訊模型：以 RabbitMQ 提供可靠、非同步的跨服務通訊（事件/指令）。
   - SDK 抽象：以 MessageClient（傳送端）與 MessageWorker（接收/處理端）封裝複雜度，支援單向與 RPC。
   - 非同步與 RPC：透過 correlationId + reply_to 實作 RPC；以 async/await 與同步原語橋接網路等待。
   - 服務生命週期與可維運性：以 IHostedService/BackgroundService 實作 worker、確保 graceful shutdown，對接 Auto Scaling。
   - 跨服務的 Context 傳遞：以 TrackContext（如 request-id）透過 headers 傳遞，並藉 DI Scope 注入處理流程。
3. 技術依賴：
   - MessageClient/Worker 依賴 RabbitMQ .NET Client、JSON 序列化
   - Worker 依賴 .NET Generic Host（BackgroundService）、DI（IServiceProvider/Scope）
   - RPC 依賴 correlationId、reply_to、專屬 reply queue 與事件回傳
   - 非同步等待依賴 AutoResetEvent/WaitHandle 與 Task.Run 包裝供 await
   - 運維整合依賴 OS shutdown signal、Docker 停止事件、（Windows 場景需額外 Win32 處理）
4. 應用場景：
   - 微服務間可靠非同步通訊（事件驅動、訂閱/通知、工作派送）
   - 需要等待結果的跨服務呼叫（以 MQ 實作 RPC）
   - 高併發背景處理（多執行緒 worker、QoS 控制）
   - 可水平擴展的工作者服務（容器化、以編排工具調整副本數、優雅關閉）

### 學習路徑建議
1. 入門者路徑：
   - 學 RabbitMQ 基本概念與官方 .NET 範例（send/receive、ack、queue/exchange）
   - 熟悉 C# async/await、Task 與基本執行緒概念（AutoResetEvent/ManualResetEvent）
   - 用最小範例試作 MessageClient 單向傳送、MessageWorker 單向接收與處理
2. 進階者路徑：
   - 實作多執行緒 worker：每執行緒一個 channel、QoS prefetch、正確 ACK
   - 套用 .NET Generic Host/BackgroundService 與 DI（IServiceProvider.CreateScope）
   - 實作 RPC：correlationId/reply_to、專屬 reply queue、以 AutoResetEvent + await 等待回應
   - 將 TrackContext 透過 headers 傳遞，於 worker 端還原並注入 DI Scope
3. 實戰路徑：
   - 封裝成團隊 SDK（options/config、logging、安全、序列化一致性）
   - 容器化部署（Dockerfile/docker-compose），用 --scale 驗證擴縮
   - 驗證 graceful shutdown（停止時不再接新訊息、等在途訊息完成再關閉）
   - 觀測性與追蹤：以 TrackContext/request-id 串接多服務 log，建立故障排除流程

### 關鍵要點清單
- MessageClient 抽象：封裝傳送邏輯與設定，統一進出點，降低使用 RabbitMQ SDK 的複雜度 (優先級: 高)
- MessageWorker 抽象：以 BackgroundService/IHostedService 管理生命週期，集中處理接收與工作執行 (優先級: 高)
- 單向訊息模型：可靠非同步傳輸、顧好 ACK 與錯誤處理，避免阻塞呼叫方 (優先級: 高)
- RPC over MQ：以 correlationId + reply_to 與專屬 reply queue 提供雙向結果回傳 (優先級: 高)
- async/await 整合：用 AutoResetEvent/WaitHandle 包裝為 Task 以 await 非同步回應 (優先級: 高)
- 多執行緒與 Channel 策略：每執行緒獨立 channel，避免序列化瓶頸，提升吞吐 (優先級: 中)
- QoS 與 Prefetch：設定 PrefetchCount 控制併發與公平分配，搭配 ACK 確保可靠性 (優先級: 中)
- Graceful Shutdown：停止接新訊息、等待在途處理完成、再關閉 channel/connection (優先級: 高)
- DI 與 Scope 管理：每則訊息建立獨立 Scope，隔離相依與生命周期，利於測試與維護 (優先級: 中)
- TrackContext 傳遞：以 headers 傳遞 request-id 等追蹤資訊，於 worker 還原注入，支援跨服務追蹤 (優先級: 高)
- 設計可維運性（Design for Operation）：在設計階段納入運維需求，簡化擴縮、部署與故障處理 (優先級: 高)
- 容器與擴縮實踐：以 docker-compose/K8s --scale 管理 worker 數量，驗證自動/手動擴縮流程 (優先級: 中)
- Windows/Linux 關機事件處理：Linux 路徑較順暢；Windows 需以 Win32 Handler 補強 IHost 偵測 (優先級: 低)
- 組態集中與注入：以 options/configuration 管理 MQ 與連線設定，避免硬編碼，利於環境切換 (優先級: 中)
- 序列化一致性：以 JSON（Newtonsoft）序列化/反序列化訊息，確保跨服務相容與可觀測性 (優先級: 低)