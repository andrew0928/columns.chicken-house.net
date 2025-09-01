# 微服務基礎建設 - Service Discovery

## 摘要提示
- 核心問題: 微服務的關鍵在於快速、精準地定位可用的服務實例並持續感知其健康狀態。
- 三要素: Service discovery 由 Register、Query、Health Check 三步驟組成，維持可用服務清單。
- DNS+DHCP類比: 以老牌 DHCP+DNS 說明註冊/查詢/探活，但在動態性與健康判定上不足。
- 註冊模式: 自我註冊與第三方註冊兩種，後者可提升健康檢測的客觀性與清單精度。
- Client-Side Pattern: 由客戶端查詢與負載均衡，彈性高效能佳，但具侵入性與綁定風險。
- Server-Side Pattern: 以負載平衡器集中央向代理與轉送，對應用透明，易治理但增延遲與單點風險。
- Netflix 案例: Eureka 提供註冊中心，Ribbon 在客戶端負載均衡與容錯，典型 client-side 實踐。
- Consul 案例: 內建服務發現、健康檢測、DNS介面與KV Store，易導入且兼顧舊系統整合。
- 雲端與容器: 雲端 LB、Docker/K8s 網路與內建 DNS 實現 server-side 與內部發現的實務。
- 效益與SLA: 妥善的 service discovery 可大幅降低整體故障率，但導入需配合 DevOps 與工程紀律。

## 全文重點
本文從架構視角拆解微服務中的服務發現問題，指出在高動態、海量實例的環境下，系統需要一套能即時註冊、查詢與健康檢測的機制，才能讓服務彼此可尋址且可靠呼叫。作者以 DHCP+DNS 作為直觀類比，說明 register、query、health check 三要素，但也點出 DNS 在 TTL、健康感知、負載導引與請求轉送等面向的不足，無法滿足秒級擴縮與高彈性路由的場景，因此才演化出多種 service discovery 模式。

在註冊面向，分為自我註冊與第三方註冊兩種：自我註冊由服務本人向 registry 報到並維持心跳，簡單直接；第三方註冊則由外部探測與拉黑不健康節點，避免「心跳仍在但對外已離線」的誤判，兩者可視需求並用以提升清單精度。

本文進一步比較 client-side 與 server-side 兩大模式。Client-side discovery 由客戶端直接向 registry 查詢並本地決策負載均衡，優勢是彈性高、效能佳、利於點對點網狀通訊與服務等級差異化，但缺點是侵入性高、更新散落在多語言多專案中難以一致、與特定 registry 綁定加劇技術債。典型實踐是 Netflix OSS：Eureka 作註冊中心，Ribbon 作客戶端負載均衡與容錯。Consul 則以更高整合度著稱：提供 HTTP 與 DNS 介面、內建健康檢測與 KV Store，有利於集中式設定、功能旗標與跨舊系統遷移。

Server-side discovery 則把 registry-aware 的路由決策外移到負載平衡器/反向代理，讓應用程式對發現機制透明，部署與更新集中、治理容易；但代價是多一跳延遲、潛在瓶頸與新的故障點，且與 API Gateway 等角色易重疊增加複雜度。雲端供應商的 ELB/ALB、Azure Load Balancer，與容器平台（Docker 內建 DNS、Swarm routing mesh、Kubernetes 服務/Ingress）皆為常見實踐：平台代管註冊、健康檢測與流量轉發，讓服務從「出生」即受控於內部 service discovery 機制。

最後，作者以簡化的 SLA 推導展示 service discovery 對降低系統故障率的巨大貢獻，強調微服務化是對團隊工程能力的一次總體檢：從 DevOps、CI/CD、版本管理、測試到可觀測性都需相應提升。結論是：服務發現是微服務上線運作的首要關鍵，應理解其原理、審慎選型與按需組合（自我/第三方註冊、client/server-side、配合平台能力），並以可維運、可演進為核心原則落地。後續將以 Consul+.NET 實作與 Service Mesh 進階篇延伸。

## 段落重點
### Service Discovery Concepts
服務發現的目的在於於分散式環境中精準定位可用的服務端點。其機制包含：啟動註冊（Register）、查詢（Query）、健康檢測（Health Check）。作者以 DHCP+DNS 類比：DHCP 分配 IP、向 DNS 註冊 Host/IP、透過 DNS 查詢，再以 ping 類似健康檢測。此模型直覺但不敷微服務需求：DNS TTL 粗糙、缺乏服務元資料、無法自動剔除故障節點與依負載導引、且不支援就地轉發。因此才需更進階的 registry 與動態路由模式來支撐秒級擴縮、千萬級端點與健康導向的流量分配。

### Service Registration Pattern(s)
服務清單的品質取決於註冊與健康檢測。自我註冊模式由服務啟動後自行向 registry 報到並維持心跳，結束時註銷；優點是簡單直接、延遲低。第三方註冊模式由外部代理持續探測服務健康，避免「服務本身還在送心跳但實際已不可用」的誤判，亦可從使用者路徑外部驗證連通性。兩者並非互斥：在大型系統常採雙軌並用（內外檢），以最大化服務清單的即時性與正確性，也為後續的流量調度提供可信任的基礎數據。

### The Client‑Side Discovery Pattern
客戶端在呼叫前向 registry 查詢可用端點清單，並於本地以演算法（如輪詢、最小連線、加權、就近性）選擇目標端點直接呼叫。

#### 優點
- 高彈性：可按租戶/等級/地域自訂策略，便於精細化流控與差異化服務。
- 高效能：決策在進程內完成，少一跳轉送，延遲最低；易做點對點網狀通訊（service mesh 前置形態）。
- 工程友善：以 SDK/Library 形式整合，便於擴展容錯（重試、斷路器、快取、批次等）。

#### 缺點
- 侵入性與綁定：需在應用內嵌入庫，語言/框架差異導致維護成本高；更換 registry 需改碼重佈。
- 一致性挑戰：策略升級需全量發版，短期內新舊並存；跨團隊治理與測試成本上升。
- 架構解耦不足：將流量調度邏輯與業務耦合，影響升級與回滾速度。

#### 案例: Netflix Eureka
Eureka 作為 REST 式註冊中心，承載中層服務的定位、負載分散與故障切換；常配合 Ribbon（客戶端 IPC/負載均衡庫）實現多協議支援、容錯與快取批次能力。Netflix OSS 以開源鞏固技術影響力，並提供雲原生微服務的實戰範本。

#### 案例: Consul
Consul 以「易整合、易運維」見長：
- Service Discovery：同時提供 HTTP 與 DNS 介面，利於新舊系統共存與平滑遷移。
- Failure Detection：內建健康檢測（HTTP/TCP/自訂腳本），自動剔除不健康節點，支撐斷路器策略。
- KV Store：提供集中式設定、功能旗標、協調與領袖選舉，長輪詢支援近即時配置下發。
- Multiple Datacenter：原生支援多資料中心查詢與就地優先，簡化跨區擴展與容災設計。

### The Server-Side Discovery Pattern
將「查詢與選路」外移到負載平衡器/反向代理，負責對 registry 感知並動態轉送請求；應用端僅面向穩定入口，對發現機制透明。

#### 優點
- 非侵入：無需改動應用程式碼，多語言多框架一致治理。
- 集中運維：策略調整在 LB/代理層統一發布，收斂變更半徑、加速回滾。
- 職能聚焦：與 API Gateway/安全/可觀測性等周邊能力協同，形成平台化能力。

#### 缺點
- 代價與風險：新增一跳與延遲，引入新故障點與潛在瓶頸；需高可用架構與橫向擴展。
- 邊界重疊：與 API Gateway 職責交疊，易重複建設增加複雜度與成本。
- 平台耦合：LB 與 registry 的緊密耦合可能限制自由選型。

#### 案例: Azure Load Balancer / AWS Elastic Load Balancer
雲端 LB 天生與供應商內部 registry 與健康檢測整合，能將外部流量依內部狀態分散至 VM/容器端點，提供即用型 server-side discovery 能力。應用專注業務，平台負責註冊、監測與轉送，降低自建成本，但需評估供應商鎖定與行為細節（超時、探測邏輯）。

#### 案例: Docker Container Network
容器平台內建 DNS（如 Docker 的 127.0.0.11）以 service name 做解析，容器啟動即自動註冊 IP；搭配反向代理（如 Nginx）可實現動態負載均衡。進一步在 Swarm/Kubernetes 中，平台提供 routing mesh/Service/Ingress 等能力，自動處理端點註冊、健康剔除與流量轉送，等同內建的 service discovery；除非需要更精細的健康與元資料管理，否則可直接依賴平台能力。

### 效益 & 結論
在微服務將實例數量從「數個」擴至「數十/數百/數千」後，若無 service discovery 維護健康服務清單與導流，系統可靠性會急遽惡化。以簡化模型估算，可見妥善的健康剔除與動態選路能顯著降低整體故障率。然導入不僅是技術選型，也考驗團隊在 DevOps、CI/CD、測試、觀測與治理上的成熟度。建議依規模與現況選擇 client-side 或 server-side，並視需求組合自我/第三方註冊與平台內建能力；優先追求「可運維、可演進」，避免早期過度複雜化。後續作者將以 Consul+.NET 實作與 Service Mesh 進階篇進一步展開。

## 資訊整理

### 知識架構圖
1. 前置知識：
- 分散式系統與微服務基本概念（服務拆分、跨服務通訊）
- 網路基礎（IP、Port、DNS、DHCP、負載平衡、反向代理）
- 健康檢查與可用性概念（heartbeat、ping、端點探測）
- 容器與編排基礎（Docker、Docker Compose/Swarm、Kubernetes 概念）
- 基礎雲端服務（Load Balancer、跨可用區/資料中心）

2. 核心概念：
- 服務發現（Service Discovery）：用 Registry 維護可用服務端點並提供查詢
- 三大機制：Register、Query、Health Check 相互配合維護「正確的可用清單」
- 註冊模式：Self-Registration vs Third-Party Registration（外部主動探測）
- 發現模式：Client-Side Discovery vs Server-Side Discovery（負載與轉送責任位置）
- 可靠性與擴展：健康檢查+動態實例+彈性伸縮支撐微服務大規模運行

3. 技術依賴：
- Registry（Consul、Eureka、etcd/ZooKeeper 作為存儲/協調）
- 健康檢查（HTTP/TCP/腳本/外部探測）
- 負載平衡與轉送（Ribbon/客戶端LB、Nginx/Envoy、雲端LB）
- DNS 整合（傳統系統過渡；SRV/TXT、短 TTL 需求）
- 組態/協調（KV Store、動態配置、Feature Flag）
- 容器網路（Docker 內建 DNS、Routing Mesh；K8s 服務抽象）

4. 應用場景：
- 大量動態實例的微服務集群（100+ 到 10,000+）
- 雲端/容器環境的自動擴縮與故障隔離
- 舊系統平滑遷移（透過 DNS 介面對接）
- 高可靠要求的業務（需要精準健康檢查與熔斷/避障）
- 跨資料中心/多區部署的服務尋址

### 學習路徑建議
1. 入門者路徑：
- 了解 DNS+DHCP 與 Service Discovery 的類比（Register/Query/Health Check）
- 動手以 Docker Compose 啟動多服務，體驗 Docker 內建 DNS 解析服務名
- 讀 Nginx/微服務服務發現入門文章，理解 Client/Server-Side 差異與權衡

2. 進階者路徑：
- 嘗試 Consul：服務註冊、健康檢查、DNS/HTTP 介面、KV Store 動態組態
- 實作 Self-Registration 與 Third-Party Registration 的健康檢查策略
- 引入客戶端負載均衡（如 Ribbon/或語言對應 SDK）與重試、超時、熔斷

3. 實戰路徑：
- 以 Consul + .NET + 容器部署一組服務（自動註冊、檢查、查詢）
- 在邊界安置反向代理/雲端 LB 實作 Server-Side Discovery，並與 Registry 同步
- 加入配置中心（Consul KV）和觀測性（日誌、指標、分散式追蹤）完善運維
- 擴展到多實例/多區域，壓測評估延遲、可用性與瓶頸；評估 Service Mesh 遷移

### 關鍵要點清單
- Service Discovery 三要素: 啟動註冊、查詢發現、健康檢查形成閉環維護可用端點清單 (優先級: 高)
- DNS/DHCP 類比: 最直觀理解服務發現的傳統實踐與其在微服務下的不足 (優先級: 中)
- DNS 的限制: TTL、缺乏健康狀態與負載感知、僅客戶端選擇端點的局限 (優先級: 高)
- Self-Registration: 服務自行註冊與心跳回報，簡單高效但可能誤報健康 (優先級: 中)
- Third-Party Registration/Health Check: 外部探測更準確，能避免心跳假陽性 (優先級: 高)
- Client-Side Discovery: 客戶端按清單自選端點，彈性大、效能佳但侵入性與維護成本高 (優先級: 高)
- Server-Side Discovery: 以 LB/反向代理承接調度，對應用透明但引入延遲與集中式瓶頸 (優先級: 高)
- Netflix Eureka/Ribbon: 經典客戶端發現與客戶端負載均衡實踐 (優先級: 中)
- Consul 能力組合: 服務發現+健康檢查+DNS/HTTP 介面+KV Store+多資料中心 (優先級: 高)
- KV Store 與動態配置: 集中管理配置、Feature Flag、協調與選主 (優先級: 中)
- 容器內建發現: Docker 內建 DNS 以服務名尋址，搭配 Nginx/Swarm Routing Mesh (優先級: 中)
- 雲端 LB（ALB/ELB/Azure LB）: 與供應商內部 Registry 整合的 Server-Side 入口 (優先級: 中)
- 負載均衡策略與健康檢查設計: 影響可用性、延遲與故障隔離的關鍵 (優先級: 高)
- 可用性量化與SLA直覺: 實例數擴張放大風險，發現機制能顯著降低整體故障率 (優先級: 中)
- 向 Service Mesh 演進: 去侵入、強策略、細緻流量治理是大型微服務的自然升級路徑 (優先級: 中)