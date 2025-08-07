# 高可靠度的微服務通訊 - Message Queue

## 摘要提示
- Message Queue 封裝: 以 RabbitMQ 為核心，設計團隊專屬 SDK，簡化開發使用門檻。
- MessageClient/Worker: 抽象化單向與雙向通訊介面，支援泛型與 async/await。
- 多執行緒處理: Worker 內建 Thread Pool 與 Graceful Shutdown，確保高併發與可靠終止。
- RPC over MQ: 以 Reply-To 與 Correlation-Id 組合兩條 Queue，實作支援 await 的 RPC。
- TrackContext 傳遞: 以 Header 攜帶 RequestId 等追蹤資訊，結合 DI 自動注入。
- Design for Operation: 服務先天支援 Auto Scaling、容器部署及 OS Shutdown 處理。
- DevOps 思維: 先遣部隊整合基礎建設，做到「能被維運的設計」而非僅選型。
- Windows 與 .NET Core: 針對 Windows Container 限制製作 WinStart/WaitForWinShutdown 補丁。
- Auto Scaling 實驗: 以 Docker Compose/Swarm 示範 --scale 動態增減 Worker 的完整流程。
- 團隊經驗分享: 集成、封裝、運維三位一體，落實微服務治理與能力升級。

## 全文重點
本文作者以實際專案為例，說明如何把 RabbitMQ 整合進 .NET 團隊的微服務生態。首先，他提出「先封裝再普及」的策略：由小組先遣隊撰寫 SDK，把連線設定、權限、序列化等繁瑣細節隱入框架，對外只暴露 MessageClient 與 MessageWorker 兩種角色。MessageClient 支援單向與 RPC，後者透過 ReplyQueue 與 CorrelationId 實踐非同步呼叫並以 async/await 取得回傳值；MessageWorker 則內建多執行緒處理、計數器與 WaitHandle，保證在 StopAsync 時能等所有訊息完成並優雅關閉。  
為了跨服務追蹤，作者將 RequestId 等資訊封裝成 TrackContext，點對點透過 MQ Header 傳遞，再配合 .NET Core DI Scoped 物件自動注入，讓開發者無痛取得。  
接著他從 DevOps 角度延伸：服務必須「設計即維運」。MessageWorker 能正確處理 OS Shutdown，便能直接受控於 Docker/K8s 的 scale in/out；實驗顯示在 Azure VM 上執行 docker-compose --scale 時，Worker 能自動加入或離開叢集且不遺漏訊息。對於 Windows Container 無法順利傳遞關機事件的缺陷，作者以 Win32 API 補寫 WinStart/WaitForWinShutdown 擴充，暫時填補 .NET Core 3 之前的空缺。  
最後作者強調，微服務成功關鍵在「整合」與「設計可維運」：選對技術只是起點，還須以架構師視角將多元基礎建設串連，並讓開發者透過統一且簡潔的 API 享受高可靠度、可觀察性與自動化部署帶來的生產力。

## 段落重點
### 團隊專屬 SDK: 通訊機制封裝
作者說明跨服務通訊型態繁雜，直接暴露完整 RabbitMQ API 給開發者將造成學習成本及易錯風險，因此決定先行抽象出 MessageClient 與 MessageWorker 兩大類別，並把連線字串、權限、序列化、Logging 等機制注入。如此一來，團隊只需關心訊息格式與業務流程即可；同時 SDK 遵循 .NET Standard 2.0，可同時用於 .NET Framework 與 .NET Core 專案。

### 抽象化: Message Client / Worker
訊息傳遞核心需求為「送」與「收」。MessageClient 只暴露 Send 方法回傳 correlationId；MessageWorker 以 delegate 交由開發者自訂 Process 邏輯，並提供 StartAsync/StopAsync 控制生命週期。兩者皆為泛型，可指定訊息型別，避免過度依賴字串或動態物件。

### 單向傳遞: MessageClient 介面定義
單向模式實作時，SDK 於建構時讀取 MessageClientOptions 初始化 Connection、Channel，SendMessage 內將訊息序列化、掛載 Header、Publish 並回傳 correlationId。此介面相容 DI，可被註冊為 Scoped 服務，透過 TrackContext 自動帶入追蹤資訊。

### 單向傳遞: MessageWorker 介面定義
Worker 採用 IHostedService/BackgroundService，於 ExecuteAsync 中依 WorkerThreadsCount 建立多組 Channel+Consumer，每組 Consumer 都以事件方式接收訊息並派發至 Process。StopAsync 會先解除事件訂閱、等待 _subscriber_received_count 歸零再關閉 Channel/Connection，以確保不遺失訊息。

### MessageWorker: 多執行緒平行處理
為提升併發，Worker 以 PrefetchCount 控制批次抓取，並用 AutoResetEvent 與 Interlocked 精準計算處理中訊息數。Shutdown 時透過 WaitHandle 阻塞主流程直至全部 Process 完成。此 Thread-safe 設計同時兼顧效率與正確性，對日後容器 Orchestration 至關重要。

### 啟動／停止 MessageWorker 的程序
啟動階段先宣告 Queue、配置 QoS、註冊 Consumer 並開始 BasicConsume；停止階段分三步：解除 Consumer 事件、等待正在處理的訊息完成、逐一關閉 Channel 與 Connection。整體運作符合 RabbitMQ 最佳實務，避免因過早關閉導致未 Ack 訊息重送或遺失。

### 雙向通訊: RPC
依官方 tutorial，以兩條 Queue 組成 RPC。Client 送訊息時附上唯一 correlationId 與 reply_to；Server 處理完後把結果發回指定 Queue。此法可在 MQ 架構下實作同步式介面而保留非同步優勢。

### 有效率的 RPC 封裝: async / await
SDK 將 MessageClient 擴充為泛型 <TIn,TOut>，並新增 SendMessageAsync，內部用 AutoResetEvent 等待對應 correlationId 的回應後以 await 非阻塞回傳。MessageWorker Process 也改為回傳 TOutputMessage。如此開發者呼叫介面即如同本機函式：var result = await client.SendAsync(...);

### MessageClient RPC 實作
每個 Client 啟動時動態宣告私有 ReplyQueue，並共用同一 Channel。收到回覆時將訊息暫存於 buffer 並 Set 該 correlationId 的 WaitHandle；SendMessageAsync 發送後進入 wait.WaitOne()，直到對應回覆到達即喚醒並取得結果。此設計減少多餘 頻繁 Polling，同時支援多筆併發 RPC。

### 跨服務的 (Track)Context 轉移
為快速定位跨服務請求，作者定義 TrackContext 保存 RequestId 等資訊。MessageClient 在 Header 注入，MessageWorker 收到後以 TrackContext.InitScope(scope, headers) 寫入新的 DI Scope，讓後續程式可直接透過注入取得，無須手動傳遞參數。

### Auto Scaling
作者從 DevOps 角度闡述「Design for Operation」，核心在於 Worker 能配合基礎設施自動增減。只要容器管理平台透過 OS Shutdown 訊號要求結束，Worker 即會完成手上任務並優雅離線；新實例啟動則自動連線 Queue 開始服務，整體無須人為介入。

### DevOps Concepts
DevOps 精神是持續回饋並優化，開發者除了功能外須考量部署、監控、配置、Scaling 等運維需求。若服務能用標準平台（Docker/K8s）調整 instance，即可避免額外撰寫管理腳本，降低維運複雜度。

### Design For Operation
檢查服務是否集中管理設定、是否能以單一 Artifact 多環境部署、是否能在 1 分鐘內完成 Scale 動作。唯有在設計期將這些需求納入，才算真正 DevOps Ready。

### Labs: Handling OS Shutdown
在 Windows Container 上偵測關機訊號仍有缺陷，作者以 Win32 API 註冊 SetConsoleCtrlHandler，並封裝 WinStart/WaitForWinShutdown 兩擴充方法，暫時解決 .NET Framework/Windows Server 1809 容器無法觸發 IHost StopAsync 的問題。

### Labs: MessageWorker Auto Scaling
透過 docker-compose 上線 RabbitMQ、Producer 五個、Consumer 一個；之後用 --scale 動態調整 Consumer 1→2→1→0，可見 Worker 準確停止且訊息不遺失。證實 SDK 可直接搭配 Docker Swarm、K8s 等平台達成自動擴縮。

### 後記
作者重申微服務成功的關鍵在於「整合」與「可維運性」，團隊須先由少數人試煉並封裝基礎能力，再推廣使用；同時以標準化、雲原生方式設計服務，才能真正站上雲端平台的肩膀，減少重複造輪與深夜維修的痛苦。

### 為團隊整合基礎服務
派先遣小隊測試框架並抽象化，共享簡潔 API，減少所有開發者面對多種 SDK 的負擔。抽象層應「恰到好處」，既隱藏繁雜細節又不犧牲彈性。

### 設計出能被維運的服務
從啟動至關閉皆須自動化、可觀測、可追蹤；只要基礎設施能用標準指令擴縮，就不必再養一堆自製工具。這正是「DevOps = Design for Operation」的實踐。