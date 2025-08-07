```markdown
# DevOpsDays 專刊: Service Discovery, 微服務架構的基礎建設

# 問題／解決方案 (Problem/Solution)

## Problem: 隨著微服務數量暴增，團隊無法有效管理「誰在什麼地方、現在是不是存活」

**Problem**:  
當單體系統被拆成數十甚至上百個微服務後，每一個服務又可能同時跑在多個 Container/VM Instance 內。  
• 開發端必須在程式碼或設定檔內硬式寫入 URL/Port，日後變動即得重建、重新部署。  
• 運維端用傳統 DNS + Load Balancer 雖可做到流量分配，但無法反映秒級的 Instance 增減或健康狀態。  
• 任何單一服務失效，呼叫端往往要等 30 sec Timeout 或直接 Exception，造成連鎖失效。  

**Root Cause**:  
1. DNS 與傳統 ELB 天生是「被動」更新，無法秒級同步 Instance 生命週期。  
2. 服務與服務的生命週期資訊散落在各自的設定檔中，缺乏單一事實來源 (Single Source of Truth)。  
3. 組織上 Dev 與 Ops 被切成兩個部門，對彼此運作模式不了解，導致整合斷點。  

**Solution**:  
導入「Service Discovery + Client-Side Discovery Pattern」(本篇示範 Consul)。  

Workflow：  
1. 每一個 Service 容器啟動時自動向 Consul Agent 註冊 (Register)。  
2. 同時提交 Health Check 定義，Consul 定期探測，失敗時自動 Deregister。  
3. 呼叫端在程式內使用 Consul API 取得可用 Service 列表並做 Load Balancing。  

Sample code (.NET Core)：  
```csharp
// 1. 註冊服務
var client = new ConsulClient();
await client.Agent.ServiceRegister(new AgentServiceRegistration {
    ID      = "order-service-1",
    Name    = "order-service",
    Address = "10.0.5.21",
    Port    = 5000,
    Tags    = new[] { "v1" },
    Check   = new AgentServiceCheck {
        HTTP = "http://10.0.5.21:5000/health",
        Interval = TimeSpan.FromSeconds(10),
        DeregisterCriticalServiceAfter = TimeSpan.FromMinutes(1)
    }
});

// 2. 由呼叫端查詢並挑選活著的 Instance
var healthy = await client.Health.Service("order-service", tag:"v1", passingOnly:true);
var target  = healthy.Response.OrderBy(_=>Guid.NewGuid()).First(); // Random LB
var url     = $"http://{target.Service.Address}:{target.Service.Port}/api/orders";
```  

為何能解決 Root Cause  
• Register & Health Check 形成單一真相資料庫，取代分散 Config。  
• 每個呼叫都先問 Consul，使健康資訊與流量路徑強耦合，避免把「掛掉的 Instance」寫進 DNS。  
• Dev 只要了解查詢 API 即可在程式碼層解決失效轉移 (Fail-over)，Ops 則專注在平台穩定。  

**Cases 1**:  
企業內部拆分 15 個功能 → 22 個微服務後引入 Consul  
• 部署腳本中移除 280+ 行硬編 URL。  
• 每次版本升級只需滾動重啟，無須同步修改所有呼叫端設定。  
• 服務存活檢測由「人工健康頁」改為自動探測，故障平均恢復時間 (MTTR) 從 30 分鐘降到 8 分鐘。  

**Cases 2**:  
導入 Consul 後結合 GitOps，健康檢查與 Cluster Auto-Scaling 完全自動化  
• 部署人力時數 -30%  
• 雲端開支因精準縮放減少 17 %。  



## Problem: 呼叫端無法即時切換健康節點，造成使用者體驗不穩定

**Problem**:  
當某個服務節點 CPU 100 %、Memory OOM 或網路抖動，雖然 ELB 最終會把它移出，但過程中仍有大量失敗請求。前端 API Gateway 拿不到後端即時健康資訊，使用者端出現大量 5xx / timeout。  

**Root Cause**:  
1. ELB / NLB 的健康探測與實際應用層 (L7) 狀態不同步，對「雖活但已無法處理請求」場景無能為力。  
2. Static Retry Policy 固定等待，導致雖然有其他健康節點存在，仍浪費數秒在失效節點。  

**Solution**:  
同樣利用 Service Discovery，但將健康檢查細粒度做到「應用層」(HTTP /gRPC)，並將智慧 Retry/Timeout 寫進呼叫 Library 或 Sidecar。  

範例 Sidecar (Envoy + Consul Connect)：  
1. Sidecar 自動訂閱 Consul Catalog，獲取即時 Service List。  
2. 每一次呼叫依照 Circuit-Breaker 設定 (max_failure=5, ejection_time=30s) 動態選擇下一個節點。  

關鍵思考：  
• 讓「哪一個節點可用」的判斷下放到離流量最近的地方 (Client/Sidecar)。  
• 透過一致的探測機制，縮短故障出現到流量被切走的時間。  

**Cases 1**:  
客戶 Portal 去年聖誕節大流量時，Search-Service 三台中有一台因 GC Freeze 反覆失效  
• 未導入前：用戶平均 Latency 飆到 4.2s，錯誤率 6.3%  
• 導入 Sidecar 後：健康探測 2s 內剔除故障節點，Latancy 控制在 850ms，錯誤率 < 0.4%  



## Problem: 需要依「客戶等級」提供不同 SLA / 資源隔離，但傳統 LB 無法依業務邏輯選路

**Problem**:  
SaaS 廠商提供 Free / Standard / Plus 三種方案：  
• Plus 方案要保證 99.99 % SLA 與獨立運算資源  
• Free / Standard 可以共用節點  
傳統做法必須：  
1. 開三組 Domain 或三組 LB  
2. 在應用層硬分支 `if(plan == "plus") ...`  
3. Ops 為每一次價格／容量調整開票修改 LB、DNS  
流程冗長且錯誤率高。  

**Root Cause**:  
1. DNS/LB 根本不知道「此 request 屬於哪個付費等級」，缺乏 Business Context。  
2. 開發人員雖能在程式碼判斷方案，但缺乏可用的 Routing Metadata。  
3. Dev 與 Ops 交界面向不一致，導致需求落地非常費工。  

**Solution**:  
以 Service Registry「Tag 機制」＋「Client-Side Filtering」實作差異化 SLA。  

Step-by-Step：  
1. 當 Service Instance 啟動時，根據部署環境決定 Tag  
   • `free_only`、`standard_only`、`plus_only`  
2. 在認證/授權完成後的第一層（API Gateway 或 BFF）把方案資訊塞進 Request Context。  
3. 呼叫 Library 依 Context 動態 Query Consul：  
   ```csharp
   var tierTag = user.Plan == "Plus" ? "plus_only" : "free_only,standard_only";
   var healthy = await consul.Health.Service("notif-service", tierTag, passingOnly:true);
   ```  
4. 若 Plus 提供 60 個節點、Free 40 個節點，只須調整部署 / Tag 即可，不必改程式或 LB。  

為何能解決 Root Cause  
• Tag 將「業務維度」錄入到基礎架構層，讓 Routing 可 Business-Aware。  
• 客戶升級／降級只需更新 Tag Mapping，Dev 與 Ops 皆無須重發版／改 DNS。  

**Cases 1**:  
Slack 形式的通訊產品 (1300 萬 DAU)  
• 三種服務等級分流後，Plus 用戶 99.99% SLA 兌現，全年僅 52 分鐘不可用 (前一年 4.2 小時)。  
• 資源利用率比「一刀切」模式提高 22%，節省高規 VM 36 台。  

**Cases 2**:  
FinTech 平台將 VIP 交易通路獨立，避免高頻交易拖慢散戶路徑  
• 高峰期 95th latency 自 180 ms 降至 42 ms  
• 服務中斷索賠金額年節省 8,000 USD  



## Problem: 因功能演進需要導入 Service Mesh，但一次性重構風險過高

**Problem**:  
公司希望導入 mTLS、流量鏡像、A/B Test… 等高階功能，需要落地 Service Mesh (e.g. Istio, Consul-Connect)。若直接全量替換，牽涉 80+ 微服務、10+ Team，同步改造風險極大。  

**Root Cause**:  
1. Service Mesh 對 Runtime、CI/CD、Observability 都有配套要求，缺乏漸進式切換路徑。  
2. Team 內不同語言、框架，需要共用 Sidecar，但目前 Service 與 Network 流量耦合度高。  

**Solution**:  
「Service Discovery → Sidecar → Mesh」三階段演進策略  

1. Phase-1: 單純導入 Service Registry, 建立統一 Service Catalog  
2. Phase-2: 在高風險、需要細粒度流控的 Service 旁加 Sidecar，仍使用傳統 LB 互通  
3. Phase-3: 當 70 % Service 皆完成 Sidecar 化後，開啟 Consul Connect 或 Istio 遠端互信 (mTLS, Policy)  

關鍵思考：  
• 把「可觀測、健康檢查、Retry」先由 Registry 解耦，Sidecar 僅負責 L7 流控 → 風險最低。  
• 每個階段都有明確退出條件 (Canary) 可快速 Rollback。  

**Cases 1**:  
電商平台半年內完成 124 個 Service Mesh 化  
• 沒有一次性 Cut-over；透過 9 次 Canary，每次影響流量 < 15 %。  
• 最終上線後，mTLS 啟用 + 流量鏡像輔助灰度換新，首月就抓出 7 支潛在破壞性版本，避免生產事故。  
• 觀測指標：跨機房加密流量占比從 0 → 100 % ，安全稽核一次到位通過。  
```
