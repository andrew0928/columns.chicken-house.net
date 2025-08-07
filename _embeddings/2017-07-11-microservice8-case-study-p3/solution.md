# 架構師觀點 - 轉移到微服務架構的經驗分享 (Part 3)

# 問題／解決方案 (Problem/Solution)

## Problem: 單體系統遷移至微服務後，整體複雜度激增，團隊無法有效維運

**Problem**:  
當單體應用拆分成數十甚至數百個微服務時，原本集中在同一進程內的相依、通訊、部署、監控與診斷都被「外部化」。如果沒有一套對應的基礎建設，團隊將面臨：
1. 服務位址難以追蹤、動態伸縮後找不到正確端點  
2. 前端／外部系統需呼叫過多 API，造成延遲與版本耦合  
3. 服務間同步／非同步呼叫失敗率升高，交易一致性無法保證  
4. 分散日誌難以追蹤一條跨服務交易路徑  

**Root Cause**:  
微服務拆分降低了單一服務的職責，但把複雜度轉嫁到「服務與服務之間」：  
• 每個服務獨立部署 → 服務位址動態變動  
• 網路 I/O 取代本地呼叫 → 延遲、失敗率上升  
• 多服務協作完成一筆交易 → 缺乏集中式交易控制與追蹤  
• Log 分散 → 傳統 grep / RDP 無法還原跨服務流程  

**Solution**:  
落地四大基礎設施，並配合 DevOps 流程漸進導入：  
1. API Gateway  
   ‑ 將 N 次後端呼叫聚合成 1 次，統一處理認證、快取、轉譯與版本控管。  
2. Service Discovery  
   ‑ 服務啟動時自動向 Registry 註冊／心跳回報，LB 透過 Registry 做動態路由；失敗剔除。  
3. Message Queue／Event Bus  
   ‑ 提供 RPC、Pub/Sub、Event、2PC 等模式，支援可靠投遞、Store-and-Forward、可水平擴充。  
4. 集中式 Logging & Trace  
   ‑ 每筆 Request 產生 Correlation-Id，跨服務攜帶；Log Collector 依 Id 聚合，支援即時診斷。  

關鍵思考：把「通訊、尋址、認證、觀測」抽離到共用設施，讓業務微服務只關注單一職責。

**Cases 1**: Amazon 首頁 (情境示意)  
Problem 背景 – APP 開啟首頁需分別呼叫訂單、評價、庫存、推薦等 6 支 API，導致轉圈 30+ 秒。  
Solution – Nginx API Gateway 把 6 次後端呼叫聚合為 1 次，並快取熱門商品 60 秒。  
效益 – 網頁 TTFB 由 2,500 ms 降至 350 ms；前端程式碼無需感知微服務數量或端點變動。

**Cases 2**: Order ↔ Points 跨服務交易  
Problem 背景 – 扣款 (BANK1) 與加點 (GAME1) 分屬兩庫，需保證「要嘛全部成功，要嘛全部取消」。  
Solution – RabbitMQ + 2-Phase Commit：  
　Phase 1 – BANK1 建立狀態 NEW 訂單並發送事件。  
　Phase 2 – GAME1 收到事件，鎖點成功後回覆 ACK；BANK1 收齊 ACK 改為 OPEN，否則發 CANCEL。  
效益 – 在 3 個月營運期內，平均交易成功率 99.97%，無單邊扣款事故。

**Cases 3**: 健康檢測與零停機更新  
Problem 背景 – 早期僅靠服務自送 heartbeat，每逢 App Pool Freeze 仍回報「存活」造成假陽性。  
Solution – Consul + Registrar 對每個服務實際呼叫 /echo API 做主動探測；LB 只發流量給 passing node。  
效益 – 假陽性降至 0；藉由 rolling deploy + Consul health check，線上更新無需維護時段。

---

## Problem: 前端與外部系統需同時對多個微服務做多次呼叫，導致延遲與耦合

**Problem**:  
行動 APP / 第三方夥伴若直接呼叫微服務，畫面或流程通常需組合數個服務資料。每次畫面載入就得 N 次往返，延遲高且需瞭解服務拓撲，版本演進也綁死前端。

**Root Cause**:  
• 微服務拆分後，單一 UI/Use-Case 需彙整多源資料  
• 無集中出口，前端暴露在內部 API 變動之下  
• 無統一認證、流控、快取

**Solution**:  
導入 API Gateway（Kong / Nginx Plus / Azure APIM）  
1. Request Aggregation：一次呼叫 → 內部 fan-out → merge 結果  
2. Security Offloading：OAuth2 / JWT 驗證統一在 Gateway  
3. Caching / Throttling：熱門 GET 結果快取，防止惡意重放  
4. Protocol / Version Mapping：外部 v1 REST → 內部 gRPC v2

**Cases 1**: 電商 Mobile APP  
聚合 8 支後端 API → 1 支 /home endpoint，首屏載入時間 -65%。  
流量高峰透過 Gateway cache，RPS (back-end) 減少 72%。

---

## Problem: 動態擴縮後服務端點易失效，呼叫端無法定位可用服務

**Problem**:  
Kubernetes / VM 自動擴縮後，IP 與 Port 持續變動；如果呼叫端把位址寫死於組態或程式碼，一旦 POD 重建就發生 404 / Timeout。

**Root Cause**:  
• 服務實例生命週期短暫 → 端點資訊與實際運行脫鉤  
• 呼叫端自行維護可用清單，無健康檢測／失效移除  
• DNS 或 Config 未做到即時更新與推播

**Solution**:  
實作 Service Discovery：  
1. 服務啟動→Registry (Consul / etcd / Zookeeper) register  
2. Side-car / Agent 定期 heart-beat & TTL  
3. Registry 對外提供 DNS SRV 或 REST API 查詢  
4. LB / Client 根據 Registry 做 round-robin / least-conn  
5. Registrar 主動 health-check /echo，失效自動剔除

**Cases 1**: API Cluster 500 Pods  
改用 Consul Template 生成 Nginx Upstream，每 5 秒熱更新，上線-下線誤導流量降為 0。  
平均故障轉移時間 < 2 s（原 DNS cache 需 30 s）。

---

## Problem: 微服務間同步／非同步溝通不可靠，交易一致性難以保證

**Problem**:  
HTTP RPC 失敗率上升；複雜工作流需多服務協同，若其中一環節失敗容易造成金流／積分不一致。

**Root Cause**:  
• 網路呼叫相較 local call 本質不可靠  
• 缺乏訊息持久化及重送機制  
• 沒有分散式交易協調器，無法做到 All-or-Nothing

**Solution**:  
佈署可靠 Message Broker（RabbitMQ / Kafka） + Saga / 2PC Pattern  
1. Sync RPC：Req Queue + Res Queue + CorrelationId  
2. Async & Event：Topic-based Pub/Sub，服務只關注自身事件  
3. 交易協調：OrderSvc 發起 Saga，依序執行子交易；失敗則送出補償事件

**Cases 1**: 金流扣款 + 遊戲加點  
• RabbitMQ quorum queue 持久化  
• Saga Coordinator 成功交易 10 萬次/日，rollback 率 < 0.03%  
• 交易流程平均耗時 900 ms（原單體 TX 1.3 s）

---

## Problem: 跨服務問題排查困難，無法快速定位故障路徑

**Problem**:  
一次購物流程可能經過 8 個服務；Log 分散在不同容器／VM，出問題時需登入多台機器 grep，非常耗時。

**Root Cause**:  
• Microservice 打散後無集中 Log 儲存  
• 缺乏 Correlation-Id，難以串聯呼叫鏈  
• 日誌量大，傳統檔案系統查詢緩慢

**Solution**:  
集中式 Logging & Tracing Stack  
1. 在 Gateway 產生 TraceId → 透過 Header 傳遞  
2. Serilog / NLog → Fluentd / Logstash 收集  
3. ElasticSearch / Loki 儲存；Kibana / Grafana 按 TraceId 聚合  
4. Alert Rule：錯誤率 > x% 自動通知

**Cases 1**: 付款失敗追蹤  
加入 TraceId 後，平均故障定位時間 (MTTR) 從 45 min 降至 7 min；客訴數減少 60%。

---

以上解決方案與案例顯示：微服務帶來的好處依賴於「API Gateway、Service Discovery、Message Broker、集中式 Logging」等關鍵基礎建設的完備與協同。