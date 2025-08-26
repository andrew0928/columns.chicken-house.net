# 高可靠度的微服務通訊 - Message Queue

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Message Queue（訊息佇列）？
- A簡: 以訊息為單位的服務通訊中介，支援非同步、緩衝與重試，解耦服務、削峰填谷，提升可靠度與可伸縮性。
- A詳: Message Queue 是分散式系統常用的通訊中介，提供以訊息為單位的傳遞機制。它讓生產者與消費者解耦，支援非同步處理、可靠傳遞、持久化儲存與重試，常用於事件驅動、訂閱通知、命令排程等情境。當流量尖峰時，訊息會先進佇列緩衝，消費者按能力取出，避免直接壓垮服務。藉由 ack 機制與持久化設定，可避免訊息遺失。搭配交換器（exchange）與路由鍵可彈性分發訊息，實現靈活拓撲。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q10, B-Q5

Q2: 為什麼微服務需要 Message Queue？
- A簡: 它能非同步解耦、提升可靠度，支援事件驅動與削峰，讓服務各自擴展，降低耦合與等待時間。
- A詳: 微服務間存在不同節奏與負載的互動，若僅用同步呼叫（HTTP/gRPC），易受對方可用性與延遲牽制。Message Queue 引入非同步通訊，讓發送方不必等待回應，透過佇列緩衝削峰並提高整體吞吐。當部分服務故障，訊息仍可保留以待恢復，提升可靠度。它是事件驅動架構、CQRS、訂閱通知的核心，能讓服務以最適速率獨立擴展，與自動水平伸縮（auto scaling）相輔相成。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q8, A-Q9

Q3: RabbitMQ 是什麼？為何在微服務中常被選用？
- A簡: 開源 AMQP 訊息代理，提供交換器與佇列的彈性拓撲、豐富用戶端、成熟生態，易於雲端部署與管理。
- A詳: RabbitMQ 是遵循 AMQP 的開源訊息代理，具備交換器（direct、topic、fanout 等）與佇列組合的彈性拓撲，支援持久化、確認、重試、路由與延遲等能力。其 .NET、Java、Go 等多語言用戶端齊全，搭配 CloudAMQP 等託管服務可快速上雲。對需同時支援點對點命令、事件廣播、RPC 的團隊，RabbitMQ 以簡潔 API 與穩定性成為常見選擇。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q3, C-Q1

Q4: 什麼是 MessageClient 與 MessageWorker？
- A簡: 兩個團隊 SDK 抽象：Client 專責送訊息，Worker 負責收訊息並呼叫處理委派，隱藏底層 MQ 細節。
- A詳: 為簡化開發者使用 MQ 的成本，將通訊抽象為兩類：MessageClient 封裝發送（單向或 RPC 雙向），處理序列化、標頭、CorrelationId 等；MessageWorker 封裝長駐接收，負責連線、通道、消費者、事件繫結與 ack，並以委派（delegate）暴露業務處理點。兩者配合可快速實作單向命令處理與 RPC，並與 DI、追蹤、設定、記錄等基礎建設整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1, C-Q3

Q5: 什麼是 TrackContext（追蹤上下文）？
- A簡: 跨服務傳遞的追蹤資訊（如 request-id），通常放在訊息標頭，便於全鏈路追蹤與稽核。
- A詳: TrackContext 是用來跨進程、跨服務傳遞的追蹤元資料，常包含 request-id、呼叫來源、租戶等。類似 HTTP Cookie/Headers 的概念，在 MQ 場景通常置於訊息標頭，避免污染業務 Payload。Worker 端會從標頭還原並注入 DI Scope，使業務代碼能以解析服務的方式取得追蹤資訊，方便關聯多服務日誌、診斷與權限檢查。它應該輕量、可序列化且受控。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q6, D-Q7

Q6: 什麼是基於 MQ 的 RPC（Message Queue Based RPC）？
- A簡: 以兩條佇列與訊息標頭（reply_to、correlation_id）實現請求-回應，客戶端等待對應回覆。
- A詳: MQ 原生偏向單向，但可用 RPC 模式實現雙向：Client 發送時設定唯一 correlation_id 與 reply_to（回覆佇列）；Server 收到後處理並將結果發送到 reply_to，帶回相同 correlation_id。Client 監聽專用回覆佇列，將回覆與請求匹配。此模式兼具 MQ 的可靠與 HTTP RPC 的直覺，適合需結果的場景；搭配 async/await 可維持友善開發體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, A-Q7

Q7: C# 的 async/await 與 MQ 有什麼關係？
- A簡: 透過 await 將非同步回覆封裝成同步風格，提升可讀性，同時維持不阻塞與高併發。
- A詳: 在 RPC over MQ 中，回覆可能延時且無序。以 await 包裝等待機制，讓開發者以同步風格撰寫非同步流程：發送後註冊等待（如 AutoResetEvent 或 TaskCompletionSource），回覆抵達時解除阻塞，將回傳物件交還呼叫端。此作法維持非阻塞、高併發與清晰控制流程，避免回呼地獄與線程阻塞，與 .NET 的任務平行程式庫自然整合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q3, C-Q4

Q8: Event-driven、CQRS、Pub/Sub 與 MQ 的關係是什麼？
- A簡: MQ 是事件驅動與 CQRS 的基礎，透過交換器與佇列實現廣播/訂閱與讀寫分離的資料流。
- A詳: 事件驅動架構以事件作為系統變化事實，透過 MQ 的交換器（fanout/topic）將事件廣播至多個訂閱者；CQRS 將命令與查詢分離，命令產生事件，讀模型依事件流更新。Pub/Sub 則以交換器路由到不同佇列供訂閱。MQ 的可靠傳遞、重試與順序控制，使這些模式得以落地並能水平擴展。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q5, C-Q5

Q9: 同步通訊（HTTP/gRPC）與非同步通訊（MQ）有何差異？
- A簡: 同步需即時回應、耦合高；非同步可解耦與削峰，但回應延遲與一致性需設計補償。
- A詳: 同步呼叫（HTTP/gRPC）適合即時查詢與強一致流程，易於理解與除錯，但呼叫方受被呼叫方可用性與延遲牽制。非同步（MQ）以訊息為介面，降低耦合與等待，利於擴展與削峰，但需處理最終一致、重複投遞、回覆延遲與有序性。實務多為混合：查詢同步、命令與事件非同步，必要時以 MQ RPC 補齊結果需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q6, C-Q3

Q10: 在 MQ 中 Connection、Channel、Consumer 有何不同？
- A簡: Connection 是 TCP 連線；Channel 為邏輯通道；Consumer 為取用訊息的消費者與事件處理。
- A詳: Connection 對應實體 TCP 連線，成本較高；Channel 是在連線上多工的虛擬通道，建議每執行緒各用一條避免序列化瓶頸；Consumer 綁定 Channel，負責從佇列取得訊息並觸發處理事件。實務上常一 Connection 多 Channel，多個 Consumer 對應多個工作執行緒，並設定 QoS（prefetch）控制未確認訊息數。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, C-Q5

Q11: 為何要封裝成團隊專屬 SDK，而非直接用 RabbitMQ Client？
- A簡: 降低學習與整合成本，統一追蹤、設定、安全與維運模式，提升團隊生產力與一致性。
- A詳: 直接操作 MQ SDK 需處理連線、序列化、標頭、DI、追蹤、紀錄、關閉序列等繁瑣細節，且每個成員做法易不一致。團隊 SDK 將通用模式（單向、RPC、追蹤、graceful shutdown）抽象，並整合設定與安全控管，讓業務開發專注在處理委派。本質不是取代原生 SDK，而是建立一致、安全、可維運的使用介面。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q23, A-Q12

Q12: 什麼是 Design for Operation（為維運而設計）？
- A簡: 在設計與開發階段即納入部署、監控、伸縮、關閉等維運需求，讓系統可被有效維運。
- A詳: Design for Operation 強調 Dev 與 Ops 一體化思維，從開發起即考慮部署標準化、設定集中、健康檢查、記錄追蹤、告警、可觀測性、平滑啟停與自動伸縮。藉由將系統行為與 infra 工具（如 K8s、Compose、Swarm）對齊，維運可僅以標準指令調整實例數，應用即可自動註冊/退出、平滑關閉，降低人工作業與錯誤率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q9, D-Q3

Q13: 為什麼使用 IHostedService/BackgroundService 來寫 Worker？
- A簡: 提供統一長駐服務模型與生命周期管理，易於被宿主啟停並與容器/雲平台對齊。
- A詳: IHostedService 定義長駐服務啟停契約，BackgroundService 提供 ExecuteAsync 模板，負責與宿主協作（啟動、Cancel Token、停止）。採用該模型可在 .NET Host 中統一管理多個 Worker，與容器停止訊號（SIGTERM/CTRL_CLOSE）整合，實作平滑關閉。也利於注入 DI、設定、記錄等基建能力，降低樣板碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q17, C-Q2

Q14: 什麼是 Graceful Shutdown？為什麼重要？
- A簡: 在停止時不再接新訊息，等待既有工作完成再關閉連線，確保不丟資料與易維運。
- A詳: Graceful Shutdown 指服務收到停止信號後，先斷開新訊息來源（移除事件處理），僅收尾進行中的工作，待全部完成與回報 ack，再關閉通道與連線。如此可避免半途而廢、訊息遺失或重複，並與自動伸縮協作：縮容時由 orchestrator 發停止信號，Worker 平順退出。無此機制將導致難以自動化與增加營運風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q1, C-Q9

Q15: AutoResetEvent 與 ManualResetEvent 有何差異？
- A簡: AutoResetEvent 釋放一個等待者後自動關閉；ManualResetEvent 開啟後需手動重置，適合廣播喚醒。
- A詳: 兩者皆為執行緒同步原語。AutoResetEvent.Set 會放行一個等待者並自動重置回關閉，適用於一對一喚醒（如 RPC 單請求等待回覆）；ManualResetEvent.Set 會讓所有等待者通過，直到手動 Reset，適合廣播。選擇錯誤會導致漏喚醒或過度喚醒，需配合字典映射與鎖保障資料一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q5, C-Q3

Q16: 為什麼不建議跨執行緒共用 Channel？
- A簡: Channel 會序列化消息處理，跨執行緒共享容易造成效能瓶頸與順序干擾。
- A詳: RabbitMQ 的 Channel 並非完全執行緒安全，且為維持消息序，對單 Channel 的操作常被序列化。多執行緒共用會出現鎖競爭與頭部阻塞。實務建議每工作執行緒建立各自 Channel，搭配每 Channel 設定 QoS（prefetch）取得最佳吞吐，避免因一則慢訊息拖累全體處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q5, D-Q2

Q17: 什麼是 PrefetchCount？如何影響吞吐與公平性？
- A簡: Consumer 未確認訊息的上限，控制每次拉取量，平衡吞吐與公平分配。
- A詳: PrefetchCount（BasicQos）限制 Consumer/Channel 在 ack 之前可同時處理的訊息數。較大值可提升吞吐，卻可能造成負載不均與記憶體壓力；較小值公平性高但吞吐下降。應配合工作時間分布與執行緒數實測調整。對 RPC 或重量級任務常建議小 prefetch；對輕量任務可略增以降低往返開銷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q5, D-Q9

Q18: 什麼是 CorrelationId？在 RPC 中扮演什麼角色？
- A簡: 每請求唯一識別碼，用於將回覆與請求匹配，是 RPC 映射的關鍵索引。
- A詳: CorrelationId 是 Client 發送請求時產生的全域唯一 ID，Server 回覆時原樣帶回。Client 端以此作為映射鍵，將回覆放入緩衝並喚醒相對應等待者（如 AutoResetEvent）。若未維護此鍵的唯一性或映射表管理不當，易造成回覆丟失或錯配，導致等待不返或誤用結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q3, D-Q6

Q19: 為何建議每個 Client 使用專屬回覆佇列（Reply Queue）？
- A簡: 避免回覆互相阻塞與錯配，當 Client 結束時可安全釋放資源（auto-delete）。
- A詳: 共用回覆佇列會導致頭部阻塞與映射表膨脹，甚至不同 Client 間的回覆互擾。每 Client 專屬回覆佇列（exclusive、auto-delete）可確保回覆不被其他實例搶走，且當 Client 釋放時自動清理。此作法降低延遲、簡化管理並減少資源洩漏風險，是 RPC 常見最佳實踐。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q6, C-Q3

Q20: 什麼是 Auto Scaling？與 MQ Worker 有何關聯？
- A簡: 依負載自動調整實例數。Worker 需支援平滑啟停，以便編排系統安全擴縮。
- A詳: Auto Scaling 是依指標（佇列長度、CPU、延遲）自動調整服務實例數。MQ Worker 因消費者可水平擴展，特別適合以實例數應對佇列堆積。前提是 Worker 能在收停止信號後不接新訊息、收尾既有任務並正常退出，使編排工具（Compose/Swarm/K8s）僅透過標準伸縮命令即可安全調整容量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q9, D-Q3

Q21: DI 生命週期與 MessageWorker 的關係是什麼？
- A簡: 每則訊息建立獨立 Scoped，注入 TrackContext 與相依服務，處理完即釋放。
- A詳: Worker 會在收到每則訊息時建立 DI Scope，將從標頭還原的 TrackContext 注入，業務處理在此 Scope 中解析相依（如 DbContext、Logger）。此模式保證隔離與執行緒安全，避免跨訊息狀態污染。同時在處理完成後正確 Dispose，避免資源累積與記憶體洩漏。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q6, D-Q7

Q22: 為什麼要把 TrackContext 放到訊息「標頭」而非「本文」？
- A簡: 追蹤屬於跨切關注點，應與業務資料分離，便於重用、治理與安全控管。
- A詳: 將追蹤與權限等橫切資料置於標頭，能與不同業務負載復用相同協議與中介軟體處理，避免每個 Payload 都自帶非業務欄位。標頭更利於過濾、日誌與安全策略，且可由通用攔截器統一填充/擷取，降低漏傳風險。本文僅承載業務資料，提升清晰度與維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, C-Q7, D-Q7

---

### Q&A 類別 B: 技術原理類

Q1: MessageWorker 背後如何運作？
- A簡: 以 BackgroundService 啟動多 Channel/Consumer，綁定 Received 事件，委派處理並 ack，Stop 時平滑退出。
- A詳: Worker 繼承 BackgroundService，於 ExecuteAsync 中建立連線與多個 Channel，為每個 Channel 建立 EventingBasicConsumer 綁定 Received。每則訊息反序列化後建立 DI Scope，注入 TrackContext，呼叫 Process 委派處理，成功後 ack。Stop 時移除事件處理避免新訊息進入，等待進行中計數歸零，再依序關閉 Channel 與 Connection。關鍵組件：IHostedService/BackgroundService、IConnection/IModel（Channel）、EventingBasicConsumer、DI Scope。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q2, C-Q2

Q2: Worker 從啟動到關閉的完整生命週期是什麼？
- A簡: Init 連線→建立多 Channel/Consumer→開始消費→收到停止信號→移除事件→等計數清空→關閉資源。
- A詳: 啟動期：建立 Connection；迴圈建立 N 個 Channel（首次宣告佇列），為每個 Channel 建 Consumer、設定 BasicQos（prefetch），開始 BasicConsume。運行期：收到訊息即進入處理，計數+1，完成後 ack 並計數-1。關閉期：WaitHandle 等待停止信號，先解除 Received 事件阻斷新訊息；以 WaitHandle/計數等候進行中全部完成；最後關閉 Channels 與 Connection，確保無遺漏與重複。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q18, D-Q1

Q3: 為什麼要為每個工作執行緒建立獨立 Channel？
- A簡: Channel 操作序列化且不宜跨執行緒共享，獨立配置可避免鎖競爭、提升吞吐與隔離故障。
- A詳: RabbitMQ Channel 並非完全 thread-safe，對單 Channel 的消費序會被序列化。多執行緒共享導致鎖競爭與頭部阻塞，單慢訊息拖累整體。採每線程一 Channel，配合 per-channel prefetch 與事件處理，能提升平行度與公平性。出錯時僅影響單 Channel，縮小爆炸半徑，利於恢復與觀測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q22, D-Q2

Q4: Prefetch 與多執行緒如何協作以達最佳吞吐？
- A簡: 依工作耗時與併發調整每 Channel 的 prefetch，平衡吞吐、記憶體與公平分配。
- A詳: 對輕量快速任務，適度提高 prefetch 減少往返；對重任務或耗時差異大，prefetch 小值可提升公平與可預測性。配合 WorkerThreadsCount 為每執行緒設 Channel，調整 prefetch*threads≈目標管道深度，並以實測指標（TPS、延遲、未 ack 數）迭代優化。過大 prefetch 會放大單點阻塞與記憶體壓力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q5, D-Q9

Q5: Exchange、Queue、Routing key 在設計中如何分工？
- A簡: Exchange 依規則分發，Queue 緩衝與拉取，Routing key 決定投遞路徑，三者組合塑造拓撲。
- A詳: Producer 發訊息到 Exchange；Exchange 依型別（direct/topic/fanout）與 Bindings 將訊息路由到一或多個 Queue；Consumer 自 Queue 拉取（推送）處理。Routing key 是路由依據（如 direct 完全匹配；topic 支援通配）。依業務選擇拓撲：命令多用 direct，事件廣播用 fanout/topic，RPC 的 reply 則用匿名/專屬 Queue。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, C-Q1, C-Q3

Q6: RPC 模式的技術機制是什麼？
- A簡: 發送設 reply_to 與 correlation_id；Server 回覆帶同 id 至回覆佇列；Client 監聽匹配等待。
- A詳: Client 建立專屬回覆佇列（exclusive、auto-delete），發送請求時在訊息屬性設 ReplyTo=該佇列、CorrelationId=GUID。Server 收到後處理結果，Publish 至 ReplyTo，帶同 CorrelationId。Client 端收到回覆事件時，將回覆放入以 CorrelationId 為鍵的緩衝並喚醒等待者，完成 Task。此機制需保障 id 唯一、回覆佇列隔離與正確清理映射。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q11, B-Q12

Q7: 如何以 AutoResetEvent/Task 封裝 await-like 的等待？
- A簡: 送出後建立事件並加入等待表；回覆到來時 Set 喚醒；以 Task.Run 包裝 WaitOne 供 await。
- A詳: 發送請求後建立 AutoResetEvent，儲存於 waitlist[correlationId]。回覆事件處理中以相同 id 取出事件並 Set，再把結果存 buffer。等待端以 await Task.Run(()=>wait.WaitOne()) 非阻塞等待，醒來後取回 buffer[id]。以 lock 保護 buffer/waitlist 原子性，避免競態導致洩漏或死結。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q3, D-Q5

Q8: TrackContext 如何跨服務傳遞並在 Worker 端注入？
- A簡: Client 將追蹤序列化到標頭，Worker 收到後還原並注入 DI Scope，供業務解析使用。
- A詳: Client 從 DI 取得當前 TrackContext，於送出前寫入訊息標頭（如 RequestId、Tenant）。Worker 收到訊息後建立新 Scope，從標頭還原 TrackContext 並註冊至 Scope。Process 委派內僅解析依賴即可取得追蹤資訊。此對稱設計避免漏傳，並確保每訊息隔離。常以 Newtonsoft.Json 序列化與自訂標頭鍵管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q6, D-Q7

Q9: Graceful Shutdown 的關鍵步驟有哪些？
- A簡: 解除 Received、停止取新訊息；以計數與 WaitHandle 等待在途完成；再關閉 Channel/Connection。
- A詳: 收到停止信號後：1) 解除所有 Consumer.Received 事件處理器，阻斷新訊息交付；2) 維持在途處理，藉由 Interlocked 計數與 AutoResetEvent 喚醒機制，等待計數歸零；3) 依序關閉 Channels 與 Connection。切忌先關連線，否則在途訊息無法 ack 導致重投與不一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q1, C-Q9

Q10: Worker 與容器編排的 Auto Scaling 如何互動？
- A簡: 編排發停止信號→Host 停止→Worker 平滑退出；擴容時新實例自動連線與消費。
- A詳: 編排（Compose/Swarm/K8s）縮容時送出 OS 訊號（Windows: CTRL_CLOSE；Linux: SIGTERM），.NET Host 轉為 Cancel Token，Worker 依 Graceful 流程退出。擴容時新實例按設定連到同佇列分食訊息。只要 Worker 遵循 Host 契約與關閉序列，運維僅需以 scale 指令調整實例數，無需侵入應用邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q20, C-Q9

Q11: MessageClient 的 SendMessageAsync 流程如何設計？
- A簡: 發送前建立等待事件並註冊；Publish 後 await 事件；回覆到來寫入緩衝並喚醒，最後回傳結果。
- A詳: 客戶端先以 PublishMessage 建立 CorrelationId 並送出，隨即建立 AutoResetEvent 並記錄至 waitlist[id]。回覆事件處理將結果寫入 buffer[id] 並 Set 對應事件。主流程 await Task.Run(()=>wait.WaitOne())，醒來後取出 buffer[id]、清理表項並回傳對象。需以 lock 保護字典，避免競態或洩漏。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, A-Q7, B-Q24

Q12: Reply Queue 應如何管理？
- A簡: 於 Client 建構時宣告匿名佇列，設 exclusive/auto-delete；釋放時移除事件並刪佇列。
- A詳: 為避免回覆擁堵與衝突，對每 Client 建立專用匿名佇列，設定 exclusive=true、auto-delete=true。建構時宣告並開始 BasicConsume；Dispose 時移除 Received 事件、刪除佇列，釋放資源。如此在 Client 退出後不留垃圾，且回覆不會被其他實例搶走。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q6, B-Q25

Q13: 為什麼要以 lock 保護 buffer/waitlist？
- A簡: 回覆事件與主流程併發存取同一資料結構，需鎖定確保加入/喚醒/清理的一致性。
- A詳: 回覆事件在不同執行緒觸發，會同時讀寫映射集合。若缺少鎖，可能出現尚未註冊事件即回覆到達、或清理與喚醒交錯導致 KeyNotFound/等待永不返回。以 lock 包裹寫入、喚醒與清理邏輯，維持原子性，避免競態條件與資源洩漏。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q5, C-Q3

Q14: Interlocked 計數器如何協助正確關閉？
- A簡: 在處理開始/結束時遞增/遞減，最後以等待事件在遞減至零時喚醒關閉流程。
- A詳: 每則訊息進入 Process 前 Interlocked.Increment，在完成與 ack 後 Decrement。若 Decrement 後為零，Set 等待事件喚醒關閉迴圈。關閉時輪詢等待事件直到計數為零，確保所有在途工作收尾。Interlocked 避免多執行緒競態造成計數不正。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q1, C-Q5

Q15: BasicAck 應在何時呼叫？有何語義？
- A簡: 僅在處理成功後 ack；若失敗可拒絕並重回佇列，確保至少一次交付語義。
- A詳: ack 是 Consumer 對 Broker 的「已處理」保證。若於處理前 ack，故障將造成訊息遺失；若從不 ack，訊息將反覆投遞。建議完成業務後 ack；失敗時使用 Nack/Requeue 或死信策略。停止流程中切勿先關連線，以免未 ack 訊息無法回補。正確 ack 策略是可靠度的關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q8, B-Q9, C-Q1

Q16: JSON 序列化對 Message 型別有何要求？
- A簡: 可序列化、前後相容、避免循環參照，版本演進需保留欄位或提供預設值。
- A詳: 型別需能被序列化；版本演進時新增欄位要可選且有預設，移除欄位要兼容舊訊息；避免日期/時區不一致；大型物件注意效能。可採明確版本欄位與契約測試，確保跨服務與跨版本穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q10, C-Q1, C-Q10

Q17: IHostedService 與 ExecuteAsync 的交互細節是什麼？
- A簡: Host 以 await 呼叫 ExecuteAsync，內部需以 await 非阻塞等待停止信號，避免卡住啟動。
- A詳: BackgroundService 的 ExecuteAsync 應回傳一個代表整個服務生命周期的 Task。若內部使用阻塞等待（如 WaitOne），需以 Task.Run 包裝並 await，讓 Host 能繼續執行其他服務與關機監聽。停止時 Host 取消 Token，ExecuteAsync 應感知並完成，釋放資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q2, B-Q18

Q18: Stop Token 與 WaitHandle 應如何搭配？
- A簡: 以 token.WaitHandle.WaitOne 阻塞等待，為配合 async 以 Task.Run 包裝供 await 使用。
- A詳: 停止流程常以 CancellationToken 提供 WaitHandle，透過 WaitOne 等待停止信號。為避免阻塞導致 Host 無法前進，使用 Task.Run(()=>waitHandle.WaitOne()) 並 await，將同步等待轉為可取消/可回傳的 Task。醒來後進入移除事件、等待在途清空與釋放資源序列。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q17, C-Q2

Q19: 為何要將 Metadata 放標頭、Payload 放本文？
- A簡: 促進關注點分離與治理，讓追蹤、認證等通用邏輯由攔截器統一處理。
- A詳: 將 TrackContext、認證、路由等通用資料放標頭，便於在中介層統一讀寫與稽核；本文專注業務資料，簡化契約、降低耦合。此分離利於日誌、重試、限流與安全策略的統一施作，避免每個業務型別都重複欄位與邏輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, C-Q7, D-Q7

Q20: 每訊息建立 DI Scope 有何優點與成本？
- A簡: 提供隔離與生命週期管理，代價是建立/釋放開銷，通常可接受且利於正確性。
- A詳: 每訊息 Scope 可確保相依的 Scoped 服務（DbContext、UnitOfWork）不被跨訊息共用，避免資料污染與競態。處理完成即釋放，降低資源洩漏風險。成本為建立/Dispose 的額外耗時，一般遠小於業務處理耗時，效益大於成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q6, D-Q7

Q21: Windows 與 Linux 的停機訊號與處理差異？
- A簡: Linux 以 SIGTERM/SIGINT；Windows 容器常見 CTRL_CLOSE。可用 Host API 或 Win32 轉接處理。
- A詳: Linux 容器停止多用 SIGTERM，.NET Host 會轉為停止事件；Windows 容器可能需透過 SetConsoleCtrlHandler 捕捉 CTRL_CLOSE/SHUTDOWN。若環境支援不足，可以 Host 擴充方法將 Win32 訊號轉為 Host 停止流程，確保 Worker 仍能 Graceful。跨平台需實測訊號傳遞可靠性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q4, B-Q10

Q22: EventingBasicConsumer 的事件處理背後機制是什麼？
- A簡: 用戶端建立內部執行緒處理收到的交付並觸發 Received，需注意執行緒安全與效能。
- A詳: RabbitMQ .NET Client 會在收到交付時於背景執行緒觸發 Received 事件，開發者在此執行反序列化、Scope 建立與業務處理。由於事件並行觸發，需自管鎖與可變狀態，並避免長阻塞阻斷後續處理。搭配 per-channel consumer 與適當 prefetch 可提升效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q5, D-Q2

Q23: 為何不直接用 MessageWorker 來接收 RPC 回覆？
- A簡: Worker 太重且設計為長駐並行；RPC 回覆僅需輕量事件監聽，專用回覆佇列更合適。
- A詳: RPC 回覆的需求是單 Client 低並發監聽、快速匹配與喚醒等待者，不需要多執行緒、Graceful 與 DI 注入等重型機制。以輕量 Consumer 監聽專屬回覆佇列，能降低資源、延遲與複雜度；Worker 應聚焦於業務處理的消費者角色。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, B-Q12

Q24: ReplyTo/CorrelationId 如何映射到等待集合？
- A簡: 以 correlationId 為鍵存放事件與回覆，事件喚醒後取出回覆並清理兩個字典。
- A詳: 發送前建立 waitlist[id]=AutoResetEvent；回覆事件到達時 buffer[id]=output 並 Set(waitlist[id])。等待端 await WaitOne 後取 buffer[id] 並移除 waitlist/id，避免洩漏。需用 lock 確保加入→等待→喚醒→清理的原子順序，避免競態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q13, D-Q5

Q25: Durable Queue 與回覆佇列（auto-delete）的取捨？
- A簡: 業務佇列通常 durable；回覆佇列短生命週期用 auto-delete/exclusive 減少資源與干擾。
- A詳: 業務命令/事件佇列常需持久化與重啟存活；RPC 回覆僅為短暫結果通道，具體現值短、容忍丟失（Client 不在則無需保留），適合使用 auto-delete/exclusive 確保隔離與釋放。混用配置不當會造成資源浪費或回覆混淆。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q6, C-Q3

Q26: 什麼是 Design for Operation 的可操作指標？
- A簡: 設定集中、單一產物、多環境配置、可觀測、平滑啟停、標準伸縮介面與自動化管線。
- A詳: 可評估項包含：設定中心化且熱更新、單一 artifacts 覆蓋多環境、監控與分散追蹤、健康/啟停探針、Graceful 啟停、支援編排標準指令伸縮、CI/CD 接續管理 artifacts 與版本治理。這些使運維能以平台工具完成日常操作，減少人工腳本與專屬入口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, A-Q12, C-Q9

Q27: 為何避免將 MessageClient 註冊為 Singleton？
- A簡: 它需攜帶當前 TrackContext 與回覆狀態，Singleton 易造成追蹤錯亂與競態問題。
- A詳: Client 在發送時會讀取當前 Scope 的 TrackContext 並寫入標頭，若為 Singleton，跨請求共享將導致追蹤汙染或舊值殘留；RPC 回覆映射也涉及共享集合，Singleton 容易引發競態。建議使用 Scoped 或 Transient，並以 DI 提供正確的上下文。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q7, D-Q7

Q28: Queue 宣告與 QoS 設定有何實務建議？
- A簡: 佇列宣告一次即可；手動 ack；每 Channel 設 prefetch；謹慎使用 exclusive；環境以設定集中。
- A詳: 啟動時首次宣告佇列（避免重複），設定 durable/死信等策略；使用 autoAck=false，業務完成後 ack；為每 Channel 設 BasicQos 控制 fair dispatch；exclusive 僅在回覆佇列使用；連線與佇列名稱由設定中心管理，利於多環境與伸縮。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q5, B-Q12

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何實作最小可用的單向 MessageClient/Worker？
- A簡: 建立佇列→Client 序列化送出→Worker 消費、反序列化、處理、ack→以設定與日誌整合。
- A詳: 
  - 實作步驟: 
    1) 啟動時宣告 Queue（durable 視需求）。2) Client 以 Newtonsoft.Json 序列化訊息，Publish 至指定 routing。3) Worker 建立連線/Channel/Consumer，Received 事件反序列化後呼叫 Process 委派，完成後 BasicAck。4) Stop 時移除事件、等待在途清零、關閉資源。
  - 範例: 
    ```csharp
    // Client
    client.SendMessage("", new DemoMessage{...}, null);
    // Worker
    Process = (msg,cid,scope)=>{ /*業務*/ };
    ```
  - 注意: autoAck=false；以設定注入連線字串；加入日誌與錯誤處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q28, A-Q4

Q2: 如何用 IHostedService 啟動與關閉 MessageWorker？
- A簡: 以 HostBuilder 註冊 Worker 為 HostedService，Start 啟動，WaitForShutdown 等停止，確保平滑關閉。
- A詳:
  - 步驟:
    1) 實作繼承 BackgroundService 的 Worker。2) 於 HostBuilder.ConfigureServices 註冊 AddHostedService。3) 程式入口 host.Start(); host.WaitForShutdown();。
  - 程式碼:
    ```csharp
    var host = new HostBuilder()
      .ConfigureServices(s=> s.AddHostedService<MyWorker>())
      .Build();
    host.Start();
    host.WaitForShutdown();
    ```
  - 注意: ExecuteAsync 內使用 await 包裝 WaitHandle；Stop 時依 Graceful 流程釋放資源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, B-Q2, A-Q13

Q3: 如何實作以 async/await 的 RPC（含回覆佇列與對應）？
- A簡: Client 建專屬回覆佇列，送出時寫 reply_to/correlation_id；回覆事件匹配緩衝並喚醒等待。
- A詳:
  - 步驟:
    1) Client 建構時 QueueDeclare() 取得匿名回覆佇列，BasicConsume。2) Send 前建立 AutoResetEvent 並登記 waitlist[id]。3) Publish 時設 ReplyTo/CorrelationId。4) 回覆事件：buffer[id]=result；waitlist[id].Set()；BasicAck。5) await Task.Run(()=>wait.WaitOne()) 取回結果並清理。
  - 程式碼片段:
    ```csharp
    var id = Publish(...); waitlist[id]=new AutoResetEvent(false);
    await Task.Run(()=>waitlist[id].WaitOne());
    var output = buffer[id];
    ```
  - 注意: exclusive/auto-delete；以 lock 保護字典；避免 .Result 造成死結。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, A-Q7

Q4: 如何同時發送多個 RPC 並收集結果？
- A簡: 建立多個 SendMessageAsync 任務以 Task.WhenAll 等待，並設定逾時與錯誤處理避免阻塞。
- A詳:
  - 步驟:
    1) 產生多筆請求 Task。2) 使用 await Task.WhenAll(tasks)。3) 處理結果陣列。
  - 程式碼:
    ```csharp
    var tasks = Enumerable.Range(1,10)
      .Select(i=>client.SendMessageAsync("", new In{...}, null));
    var results = await Task.WhenAll(tasks);
    ```
  - 注意: 避免混用 .Result；可加入逾時 CancellationToken 與重試；觀察回覆佇列延遲，調整併發。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, D-Q5, B-Q11

Q5: 如何設定 Prefetch 與 WorkerThreads 提升吞吐？
- A簡: 一執行緒一 Channel；每 Channel 設 prefetch；以壓測調整 threads×prefetch 與任務耗時平衡。
- A詳:
  - 步驟:
    1) 依 CPU/IO 性質設定 WorkerThreadsCount。2) 每 Channel 呼叫 BasicQos(0, Prefetch, false)。3) 壓測收集 TPS、延遲、未 ack 數。
  - 程式碼:
    ```csharp
    channel.BasicQos(0, options.PrefetchCount, true);
    ```
  - 注意: 過大 prefetch 會造成記憶體壓力與不公平；過小降低吞吐；觀察指標迭代調整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q17, D-Q9

Q6: 如何在 Worker 中使用 DI Scope 與 TrackContext？
- A簡: Received 事件內 CreateScope，還原標頭為 TrackContext 注入 Scope，委派中解析使用。
- A詳:
  - 步驟:
    1) 在收到訊息後 using var scope = services.CreateScope()。2) 從 e.BasicProperties.Headers 還原 TrackContext。3) TrackContext.InitScope(scope, ctx)。4) 呼叫 Process(msg, cid, scope)。
  - 程式碼:
    ```csharp
    using var scope = _services.CreateScope();
    TrackContext.InitScope(scope, headers);
    Process(message, props.CorrelationId, scope);
    ```
  - 注意: Client 端避免 Singleton；標頭鍵名一致；處理完要 ack。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q5, D-Q7

Q7: 如何封裝 TrackContext 至標頭並在 Client 注入？
- A簡: 於 Client 建構時注入當前 TrackContext；送出前序列化寫入 props.Headers；Worker 端對稱還原。
- A詳:
  - 步驟:
    1) DI 提供 TrackContext（Scoped）。2) Send 前將 ctx 序列化存入 headers（如 "x-track"）。3) Publish 時附加 headers。
  - 程式碼:
    ```csharp
    props.Headers["x-track"] = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(ctx));
    ```
  - 注意: 請用 Scoped/Transient 註冊 Client；敏感資訊最小化；鍵名與版本一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, B-Q19, D-Q7

Q8: 如何在 Windows 宿主處理 OS 停機信號？
- A簡: 使用 SetConsoleCtrlHandler 捕捉 CTRL_CLOSE，轉為 Host 停止流程，確保 Worker 平滑關閉。
- A詳:
  - 步驟:
    1) 撰寫 WindowsHostExtensions，註冊 SetConsoleCtrlHandler。2) 收到信號 Set 事件；呼叫 host.StopAsync()。3) 在 WaitForWinShutdown 等候停止。
  - 程式碼:
    ```csharp
    host.WinStart();
    host.WaitForWinShutdown();
    ```
  - 注意: .NET/容器版本差異需實測；清理事件處理；避免阻塞 Handler 執行緒。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, D-Q4, B-Q10

Q9: 如何用 docker-compose 進行 Worker 的 Auto Scaling？
- A簡: 定義 rabbitmq/producer/consumer 服務，透過 --scale 調整 consumer 數量，依賴 Worker 的平滑關閉。
- A詳:
  - 步驟:
    1) 撰寫 compose 服務（RabbitMQ、Producer、Consumer）。2) 啟動：docker-compose up -d。3) 擴容：--scale consumer=N。4) 縮容：--scale consumer=M（觀察 Worker 正常退出）。
  - 設定:
    ```yaml
    services: 
      consumer: { image: app, environment: [MQURL=amqp://...] }
    ```
  - 注意: 映像版本與 OS 訊號一致；記錄與指標監控；確保 Worker 實作 Graceful。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, B-Q10, D-Q3

Q10: 如何將 SDK 納入 CI/CD 與集中設定管理？
- A簡: 以單一產物搭配環境變數/設定中心提供連線字串與安全設定，管線自動化構建與發佈。
- A詳:
  - 步驟:
    1) SDK/服務以 .NET Standard/容器化建構單一 artifacts。2) 設定以環境變數或設定中心（ConnURL、佇列名）。3) CI/CD 管線：建置→測試→發佈映像→部署。4) 配合秘密管理（密碼/憑證）。
  - 注意: 設定熱更新策略；版本相容測試；分環境分層授權。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q26, A-Q12, C-Q9

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 停止服務時仍有訊息在處理，怎麼辦？
- A簡: 實作平滑關閉：先移除事件避免新訊息，再以計數/等待事件等候在途完成，最後關閉通道與連線。
- A詳: 
  - 症狀: 縮容時訊息丟失或重複、服務卡死。
  - 可能原因: 直接關連線、未等在途完成、提早 ack。
  - 解決步驟: Stop→解除 Received→等待計數歸零（AutoResetEvent 喚醒）→關閉 Channel/Connection→釋放資源。
  - 預防: 以壓測驗證關閉時間；在 Host 停止流程中實作上述序列。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q14, C-Q9

Q2: 多執行緒共用 Channel 造成效能低落，如何處理？
- A簡: 改為每執行緒一 Channel，並設定 per-channel prefetch，避免序列化與鎖競爭。
- A詳:
  - 症狀: 吞吐偏低、延遲不穩、CPU 空閒但處理慢。
  - 原因: Channel 操作序列化，跨執行緒共享造成頭部阻塞。
  - 解法: 每工作執行緒建立獨立 Channel/Consumer；調整 prefetch；監控未 ack。
  - 預防: 壓測找最佳 threads×prefetch；避免跨執行緒共享 Channel。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q5

Q3: Auto Scaling 時服務關不乾淨怎麼辦？
- A簡: 確保接收 OS 停止信號並實作 Graceful；用標準編排指令伸縮，避免自製關閉腳本。
- A詳:
  - 症狀: 縮容卡住、容器殺不掉、訊息遺失。
  - 原因: 未處理停機信號或未正確移除事件與等待在途。
  - 解法: Host 偵測停止→Worker 走 Graceful 流程；Windows 可用 Win32 轉接；Linux 用 SIGTERM。
  - 預防: 壓測關閉路徑；納入 CI/CD 健康檢查與啟停探針。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q10, C-Q9

Q4: Windows 容器收不到 Shutdown 事件，如何因應？
- A簡: 使用 SetConsoleCtrlHandler 將 CTRL_CLOSE 轉為 Host 停止，或評估 Linux 容器化路徑。
- A詳:
  - 症狀: docker stop 後應用未收到停止事件。
  - 原因: 特定版本 .NET/Windows 容器訊號橋接限制。
  - 解法: 實作 WindowsHostExtensions（Win32→Host.StopAsync）；或改用 Linux 基礎映像。
  - 預防: 指定相容基底映像版本；持續整合環境驗證停機路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, C-Q8, B-Q17

Q5: RPC 等待一直不返回或發生死結，怎麼排查？
- A簡: 檢查 correlationId 一致、事件註冊順序、字典加鎖與避免 .Result，同步改用 await。
- A詳:
  - 症狀: await 永不完成、CPU 閒置、無回覆。
  - 原因: id 不匹配、尚未加入 waitlist 即回覆抵達、未鎖導致競態、以 .Result 阻塞。
  - 解法: 先註冊事件與字典再發送；以 lock 保證順序；全面 async/await；加入逾時與記錄。
  - 預防: 加入測試涵蓋競態；統一非阻塞程式風格。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q13, C-Q4

Q6: 回覆無法對上請求或被丟棄，如何處理？
- A簡: 使用專屬回覆佇列（exclusive/auto-delete），維護 correlation 映射並妥善清理資源。
- A詳:
  - 症狀: 回覆混雜、錯用結果、記憶體洩漏。
  - 原因: 共用回覆佇列、映射清理不當、Client 提早釋放。
  - 解法: 每 Client 回覆佇列；回覆事件中以 id 對應緩衝並喚醒；Dispose 時移除事件/刪佇列。
  - 預防: 統一 RPC 模板；壓測回覆路徑；加逾時清理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q12, B-Q24

Q7: Worker 端 TrackContext 為何是 null？如何修正？
- A簡: 確認 Client 有寫入標頭、Worker 以 Scope 還原注入，避免 Client 註冊為 Singleton。
- A詳:
  - 症狀: 日誌無 request-id、無法跨服務追蹤。
  - 原因: Client 未填標頭；Worker 未 CreateScope/還原；Client Singleton 導致上下文錯亂。
  - 解法: 以 Scoped 注入 TrackContext；Client 送出前填 headers；Worker 收到後還原並注入 Scope。
  - 預防: 契約測試；中介層自動填充；避免 Singleton Client。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q22, C-Q6

Q8: 訊息重複或遺失，怎麼避免？
- A簡: 僅在成功後 ack；失敗用 nack/requeue；停止時先移除事件後等待收尾；業務層設計冪等。
- A詳:
  - 症狀: 重複處理或資料缺漏。
  - 原因: 提前 ack、連線過早關閉、未正確關閉流程。
  - 解法: 成功後 ack；失敗重試或死信；Shutdown 先斷事件，再等在途清零；業務端冪等鍵。
  - 預防: 以壓測覆蓋異常；設計補償流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q14, C-Q1

Q9: 吞吐量不佳的常見原因與調優方法？
- A簡: 檢查 prefetch、執行緒數、序列化成本、網路延遲與 CPU/IO 瓶頸，迭代壓測調整。
- A詳:
  - 症狀: TPS 低、佇列堆積。
  - 原因: prefetch 太小/太大不當、Channel 共享、處理耗時、序列化過重。
  - 解法: 一線程一 Channel；調整 prefetch；優化業務與序列化；批次/並發；觀測指標。
  - 預防: 壓測基準；自動化容量檢測與預警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q5, A-Q20

Q10: 反序列化錯誤（相容性問題）如何處理？
- A簡: 制定訊息契約版本策略，新增欄位保持相容，提供預設值並加強錯誤處理與告警。
- A詳:
  - 症狀: JSON 解析失敗、欄位缺失、資料破壞。
  - 原因: 雙方版本不一致、欄位變更未相容、時間/文化設定不一致。
  - 解法: 契約版本欄位；新增欄位設預設；嚴格反序列化錯誤捕捉與死信；統一日期格式。
  - 預防: 消息契約測試；灰度發布；文件化契約演進。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, C-Q1, C-Q10

---

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Message Queue（訊息佇列）？
    - A-Q2: 為什麼微服務需要 Message Queue？
    - A-Q3: RabbitMQ 是什麼？為何在微服務中常被選用？
    - A-Q4: 什麼是 MessageClient 與 MessageWorker？
    - A-Q9: 同步通訊（HTTP/gRPC）與非同步通訊（MQ）有何差異？
    - A-Q10: 在 MQ 中 Connection、Channel、Consumer 有何不同？
    - C-Q1: 如何實作最小可用的單向 MessageClient/Worker？
    - C-Q2: 如何用 IHostedService 啟動與關閉 MessageWorker？
    - A-Q13: 為什麼使用 IHostedService/BackgroundService 來寫 Worker？
    - A-Q14: 什麼是 Graceful Shutdown？為什麼重要？
    - A-Q17: 什麼是 PrefetchCount？如何影響吞吐與公平性？
    - A-Q5: 什麼是 TrackContext（追蹤上下文）？
    - C-Q7: 如何封裝 TrackContext 至標頭並在 Client 注入？
    - C-Q9: 如何用 docker-compose 進行 Worker 的 Auto Scaling？
    - A-Q12: 什麼是 Design for Operation（為維運而設計）？

- 中級者：建議學習哪 20 題
    - B-Q1: MessageWorker 背後如何運作？
    - B-Q2: Worker 從啟動到關閉的完整生命週期是什麼？
    - B-Q3: 為什麼要為每個工作執行緒建立獨立 Channel？
    - B-Q4: Prefetch 與多執行緒如何協作以達最佳吞吐？
    - C-Q5: 如何設定 Prefetch 與 WorkerThreads 提升吞吐？
    - B-Q5: Exchange、Queue、Routing key 在設計中如何分工？
    - A-Q6: 什麼是基於 MQ 的 RPC？
    - B-Q6: RPC 模式的技術機制是什麼？
    - C-Q3: 如何實作以 async/await 的 RPC（含回覆佇列與對應）？
    - C-Q4: 如何同時發送多個 RPC 並收集結果？
    - B-Q7: 如何以 AutoResetEvent/Task 封裝 await-like 的等待？
    - B-Q12: Reply Queue 應如何管理？
    - B-Q13: 為什麼要以 lock 保護 buffer/waitlist？
    - B-Q15: BasicAck 應在何時呼叫？有何語義？
    - B-Q8: TrackContext 如何跨服務傳遞並在 Worker 端注入？
    - C-Q6: 如何在 Worker 中使用 DI Scope 與 TrackContext？
    - D-Q5: RPC 等待一直不返回或發生死結，怎麼排查？
    - D-Q8: 訊息重複或遺失，怎麼避免？
    - D-Q9: 吞吐量不佳的常見原因與調優方法？
    - B-Q28: Queue 宣告與 QoS 設定有何實務建議？

- 高級者：建議關注哪 15 題
    - B-Q9: Graceful Shutdown 的關鍵步驟有哪些？
    - B-Q10: Worker 與容器編排的 Auto Scaling 如何互動？
    - C-Q8: 如何在 Windows 宿主處理 OS 停機信號？
    - B-Q21: Windows 與 Linux 的停機訊號與處理差異？
    - D-Q4: Windows 容器收不到 Shutdown 事件，如何因應？
    - A-Q19: 為何建議每個 Client 使用專屬回覆佇列？
    - B-Q25: Durable Queue 與回覆佇列的取捨？
    - B-Q20: 每訊息建立 DI Scope 有何優點與成本？
    - B-Q26: 什麼是 Design for Operation 的可操作指標？
    - C-Q10: 如何將 SDK 納入 CI/CD 與集中設定管理？
    - D-Q3: Auto Scaling 時服務關不乾淨怎麼辦？
    - D-Q6: 回覆無法對上請求或被丟棄，如何處理？
    - D-Q10: 反序列化錯誤（相容性問題）如何處理？
    - B-Q17: IHostedService 與 ExecuteAsync 的交互細節是什麼？
    - B-Q23: 為何不直接用 MessageWorker 來接收 RPC 回覆？