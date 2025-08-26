## Case #1: API Gateway 聚合，消除首頁 N 次後端呼叫的轉圈延遲

### Problem Statement（問題陳述）
**業務場景**：電商 App 首頁需同時顯示訂購紀錄、商品評價、商品資訊、推薦、庫存、購物車等資訊。微服務化後，前端須向多個後端服務各自發起 API 呼叫，行動網路環境下延遲顯著，使用者開啟首頁常見長時間等待，影響轉換率與留存。

**技術挑戰**：前端多次往返（N 次 REST 呼叫）、網路抖動、TLS/連線開銷、與多服務間異常控制分散，導致效能與穩定性難以保證。

**影響範圍**：使用者體驗、首頁載入時間、後端服務負載、前端程式複雜度與維護性。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 前端直連多個微服務，造成多次網路往返與序列化/反序列化開銷。
2. 無集中快取與降載機制，同一資料被重複請求。
3. 版本/介面異動會波及前端，導致耦合度高、變更成本大。

**深層原因**：
- 架構層面：缺乏中介層協調，未整合輸出合併（aggregation）與 API 管控。
- 技術層面：缺少反向代理、聚合器與跨服務錯誤控制的通用元件。
- 流程層面：前後端協作未明確定義聚合責任與快取策略。

### Solution Design（解決方案設計）
**解決策略**：引入 API Gateway 作為對外唯一入口，將多個後端微服務呼叫在 Gateway 層聚合為單一 API，並於 Gateway 層實施快取、超時、重試、降級與日誌。前端僅需一次呼叫即可取得首頁所有區塊資料，降低耦合、減少往返。

**實施步驟**：
1. 規劃聚合 API 與資料契約
- 實作細節：定義 /api/home 聚合端點與後端各服務契約；約定錯誤/超時策略與部分失敗回傳格式。
- 所需資源：API 規格文件、契約測試工具（OpenAPI/Swagger）
- 預估時間：1-2 人日

2. 部署 API Gateway 並設定上游服務
- 實作細節：以 NGINX/Kong 定義 upstream 與路由，設定超時、重試、斷路器。
- 所需資源：NGINX/Kong、Docker/K8s
- 預估時間：1-2 人日

3. 實作聚合邏輯與快取
- 實作細節：Gateway 以非同步並行呼叫各服務，聚合 JSON；對可快取區塊設定 TTL。
- 所需資源：Node.js/OpenResty(Lua)/Kong plugin
- 預估時間：2-3 人日

**關鍵程式碼/設定**：
```nginx
# NGINX: 定義上游服務
upstream svc_orders   { server orders:8080; }
upstream svc_reviews  { server reviews:8080; }
upstream svc_catalog  { server catalog:8080; }
# ... 其他服務

# 基本快取區
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=apicache:50m max_size=1g inactive=10m use_temp_path=off;

server {
  listen 80;
  location /api/home {
    proxy_cache apicache;
    proxy_cache_valid 200 1m;  # 可依區塊細分
    # 以子請求並行聚合（OpenResty 可用 lua）
    # 或交由上游 aggregator 服務實作
    proxy_pass http://aggregator:8080/home; 
  }
}
```

Implementation Example（實作範例）
- 使用 OpenResty 在 Gateway 內以 Lua 並行 subrequest（ngx.location.capture_multi），或以 Node.js 寫 aggregator 微服務承接 /api/home。

實際案例：文章以 Amazon 首頁為例，首頁需同時取多個微服務資料，改由 Gateway 聚合，前端僅呼叫一次。
實作環境：API Gateway（NGINX/Kong）、ASP.NET Core 微服務、Docker/K8s。
實測數據：
- 改善前：首頁需 6 次後端呼叫；TTFB 不穩定
- 改善後：1 次呼叫；TTFB 穩定且下降
- 改善幅度：往返次數 -83%（6→1），網路開銷顯著下降

Learning Points（學習要點）
核心知識點：
- API Gateway 聚合與快取模式
- 反向代理、超時/重試/斷路器基本工
- 前後端契約與部分失敗設計

技能要求：
- 必備技能：HTTP/REST、反向代理基礎、JSON 契約管理
- 進階技能：OpenResty/Kong 自訂插件並行聚合與快取

延伸思考：
- 還可應用於行動端弱網加速、BFF（Backend For Frontend）
- 風險：聚合器成為單點，需高可用與資源隔離
- 優化：區塊化快取、預取、條件式請求（ETag/If-None-Match）

Practice Exercise（練習題）
- 基礎練習：用 NGINX 配置一個簡單 upstream 與 proxy_cache（30 分）
- 進階練習：用 OpenResty 並行拉取三個 mock 服務並聚合回傳（2 小時）
- 專案練習：為一個既有前端頁面設計 BFF/Gateway 聚合與分區塊快取（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：單次呼叫返回所有區塊並處理部分失敗
- 程式碼品質（30%）：契約清晰、錯誤處理與觀測完善
- 效能優化（20%）：快取命中率、TTFB 改善明顯
- 創新性（10%）：靈活路由、A/B 快取策略或預取
```

## Case #2: 跨服務認證複雜度爆炸，改由 API Gateway 統一認證授權

### Problem Statement（問題陳述）
**業務場景**：用戶登入後需呼叫多個後端服務（訂單、評價、購物車等）。各服務各自實作認證與授權，導致維護多套邏輯、憑證傳遞不一致，權限錯誤與安全風險增加。

**技術挑戰**：N 個服務互調產生 N×(N-1) 種認證傳遞組合；權杖驗證、過期、續發、角色/範圍差異造成錯誤率高且難排障。

**影響範圍**：安全事件風險、用戶操作失敗率、服務間契約與維護成本。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 每個微服務重複實作認證授權，標準與版本不一致。
2. 憑證/Claims 在服務間傳遞缺乏統一格式與驗證。
3. 排障無統一審計點，難以重現問題。

**深層原因**：
- 架構層面：缺乏統一邊界，內部細節暴露給外部。
- 技術層面：沒有集中式 Token 驗證與策略執行點。
- 流程層面：認證策略與金鑰輪替缺乏自動化。

### Solution Design（解決方案設計）
**解決策略**：在 API Gateway 統一驗證 JWT/OAuth2/OIDC，落地授權策略（Scopes/Policies），將驗證結果以受信標頭（如 X-User-Claims）轉發至後端。後端僅信任 Gateway 並依最小知悉原則處理。

**實施步驟**：
1. 決定認證協定與權杖格式
- 實作細節：採用 OIDC + JWT；定義必要 Claims 與簽章演算法。
- 所需資源：身分提供者（IdP）、密鑰管理（JWKS）
- 預估時間：1-2 人日

2. Gateway 啟用驗證與授權
- 實作細節：Kong JWT/OPA plugin、NGINX+Lua 驗簽與範圍檢查。
- 所需資源：Kong/NGINX、策略服務
- 預估時間：1-2 人日

3. 後端最小化處理與信任鏈
- 實作細節：只驗證來自 Gateway 的受信標頭與內部憑證；落實零信任分段。
- 所需資源：服務網段隔離、mTLS（可選）
- 預估時間：1 人日

**關鍵程式碼/設定**：
```yaml
# Kong: 啟用 JWT plugin
plugins:
- name: jwt
  service: home-aggregate
  config:
    key_claim_name: kid
    secret_is_base64: false
    run_on_preflight: true

# NGINX + Lua 簡化示意（驗簽與轉發 Claims）
# access_by_lua_block {
#   local jwt = require "resty.jwt"
#   local token = ngx.var.http_authorization
#   local verified = jwt:verify(jwks, token)
#   if not verified.verified then return ngx.exit(401) end
#   ngx.req.set_header("X-User-Claims", verified.payload.sub .. ";" .. verified.payload.scope)
# }
```

實作環境：Kong/NGINX Gateway、OIDC IdP（如 Auth0/Keycloak）、ASP.NET Core 後端。
實測數據：
- 改善前：需維護 N×(N-1) 認證傳遞組合；出錯點分散
- 改善後：統一入口 1 套策略；後端簡化為信任 Gateway
- 改善幅度：認證耦合度 O(N²)→O(1)，攻擊面縮小

Learning Points（學習要點）
- 中心化認證授權與邊界控制
- JWT/OIDC 與 Claims 設計
- 受信轉發與最小權限原則

技能要求：
- 必備：OAuth2/OIDC、JWT、反向代理
- 進階：OPA/Rego 策略、mTLS、Key rotation

延伸思考：
- 適用於多端（Web/App/3rd-party）統一入口
- 風險：Gateway 成為關鍵點，需高可用與金鑰輪替
- 優化：快取 JWKS、細粒度 ABAC

Practice Exercise
- 基礎：在 Kong 為一條路由開啟 JWT 驗證（30 分）
- 進階：實作 OPA 授權策略並透過插件執行（2 小時）
- 專案：把三個既有服務的認證收斂至 Gateway（8 小時）

Assessment Criteria
- 功能完整性：所有路由統一認證授權
- 程式碼品質：策略可測試、日志可追
- 效能優化：驗證快取、低延遲
- 創新性：細粒度授權與審計可視化
```

## Case #3: API Gateway 輸出快取，降低重複讀流量與延遲

### Problem Statement（問題陳述）
**業務場景**：商品資訊、評價、推薦等讀多寫少，尖峰時段讀取量暴增，後端服務與資料庫承壓，延遲上升影響瀏覽轉換。

**技術挑戰**：多個前端與頁面重複請求相同資料；缺少統一快取策略與一致性控制；後端無法針對外部流量做集中降載。

**影響範圍**：瀏覽速度、服務成本、資料庫負載與擴容成本。

**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 沒有集中式輸出快取，重複 Query 未被吸收。
2. 快取粒度與失效策略不一致，命中率低。
3. 各服務重複造輪子，缺乏統一觀測。

**深層原因**：
- 架構層面：缺乏單一進出口利於快取。
- 技術層面：無條件式請求（ETag）與分區塊快取機制。
- 流程層面：快取策略未與產品更新節奏協調。

### Solution Design（解決方案設計）
**解決策略**：在 API Gateway 啟用輸出快取（proxy_cache），以資源類型與穩定度設計 TTL；對個別區塊實施分區塊快取與條件式請求（ETag/If-None-Match），命中則 304。

**實施步驟**：
1. 快取對象與 TTL 設計
- 實作細節：針對商品詳情、評價列表、推薦結果設定 TTL；對個人化結果採短 TTL。
- 所需資源：需求盤點與資料波動分析
- 預估時間：1 人日

2. Gateway 快取與條件式請求
- 實作細節：NGINX proxy_cache + add_header ETag；後端支援 ETag/Last-Modified。
- 所需資源：NGINX、後端少量改造
- 預估時間：1-2 人日

3. 觀測與調參
- 實作細節：曝光 cache_status、命中率、回源率；APM 整合。
- 所需資源：Grafana/Prometheus
- 預估時間：1 人日

**關鍵程式碼/設定**：
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=apicache:100m inactive=10m use_temp_path=off;

map $upstream_cache_status $cache_header {
  HIT "HIT"; MISS "MISS"; BYPASS "BYPASS"; EXPIRED "EXPIRED"; default "NONE";
}

server {
  location /api/products/ {
    proxy_cache apicache;
    proxy_cache_key "$scheme$proxy_host$request_uri";
    proxy_cache_valid 200 2m;
    add_header X-Cache $cache_header;
    proxy_pass http://svc_catalog;
  }
}
```

實作環境：NGINX/Kong、ASP.NET Core 後端支援 ETag。
實測數據：
- 改善前：重複讀流量 100%；高峰回源率高
- 改善後：快取命中率提升（例如 >60%）；回源率下降
- 改善幅度：回源次數顯著下降，端到端延遲大幅改善

Learning Points
- 輸出快取與條件式請求
- 快取鍵設計與命中觀測
- 分區塊快取策略

技能要求
- 必備：NGINX 基礎、HTTP 緩存頭
- 進階：個人化快取、Vary、Cache stampede 防護

延伸思考
- 適用於讀多寫少場景與 SEO/SSR
- 風險：過期資料；需正確失效策略
- 優化：主動失效、預熱、分級 TTL

Practice Exercise
- 基礎：為 /api/products 啟用 proxy_cache（30 分）
- 進階：加上 ETag 支援並驗證 304 流程（2 小時）
- 專案：設計首頁分區塊快取與觀測面板（8 小時）

Assessment Criteria
- 功能完整性：命中率可觀測、正確回源
- 程式碼品質：頭資訊與鍵設計合理
- 效能優化：回源率顯著下降
- 創新性：動態 TTL 或預取設計
```

## Case #4: 以 API Gateway 做版本轉譯，隔離內外部變更

### Problem Statement（問題陳述）
**業務場景**：內部微服務需要重構 API（欄位更名、資源重組），但外部客戶端已大規模部署，無法同步升版，造成變更窒礙難行。

**技術挑戰**：前端/三方客戶端難以快速跟進；多版本共存時路由與轉譯複雜；防止破壞性變更影響體驗。

**影響範圍**：產品迭代速度、相容性、技術債積累。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 少了穩定外部契約層，內部變更直接外溢。
2. 多端客戶端升級週期長，無法快速同步。
3. 缺乏轉譯與版本路由管控。

**深層原因**：
- 架構層面：沒有 API 稳定外觀（facade）。
- 技術層面：缺乏映射/轉換機制（header/URL/格式）。
- 流程層面：版本生命周期與棄用（deprecation）缺失。

### Solution Design
**解決策略**：在 API Gateway 提供穩定對外版本（/v1），內部服務可獨立演進（/v2）。使用路由與轉換插件（request/response transformer）完成欄位映射與資源聚合/拆分，分階段導流與灰度。

**實施步驟**：
1. 設計版本策略與棄用計劃
- 實作細節：URL 版或 Header 版；公告與期限。
- 資源：API 文檔、溝通渠道
- 時間：1 人日

2. Gateway 路由與轉換
- 實作細節：Kong request/response-transformer；NGINX map/rewrite。
- 資源：Kong/NGINX
- 時間：1-2 人日

3. 觀測與灰度導流
- 實作細節：按客戶端版本 UA/標頭導流；比對錯誤率/延遲。
- 資源：APM、Feature flag
- 時間：1 人日

**關鍵程式碼/設定**：
```nginx
# 依版本路由
location ~ ^/api/(?<ver>v[12])/(.*)$ {
  set $backend "svc_v1";
  if ($ver = v2) { set $backend "svc_v2"; }
  proxy_pass http://$backend/$2;
}

# Kong request-transformer（示意）
plugins:
- name: request-transformer
  config:
    add:
      headers:
      - "X-Api-Version:v1"
    rename:
      json:
      - "oldName:newName"
```

實作環境：Kong/NGINX，ASP.NET Core 微服務雙版本並行。
實測數據：
- 改善前：外部受內部變更牽動，部署風險高
- 改善後：穩定對外契約，內外解耦，灰度導流
- 改善幅度：破壞性變更對外影響降至最小

Learning Points
- API 版本策略與轉譯
- 灰度導流與回滾
- 相容性與棄用流程

技能要求
- 必備：反向代理路由、HTTP 協議
- 進階：插件二次開發、流量治理

延伸思考
- 適用於多三方整合平台
- 風險：轉譯邏輯過多難維護
- 優化：契約測試與差異檢測自動化

Practice Exercise
- 基礎：配置 v1/v2 路由（30 分）
- 進階：對回應做欄位轉換（2 小時）
- 專案：制定版本棄用計畫並實作灰度（8 小時）

Assessment Criteria
- 功能完整性：多版本共存且正確轉譯
- 程式碼品質：轉換規則可測可觀測
- 效能優化：轉譯開銷可控
- 創新性：自動契約驗證
```

## Case #5: Service Discovery 註冊/反註冊，解決動態實例尋址

### Problem Statement
**業務場景**：微服務彈性擴縮、故障遷移頻繁，實例 IP/Port 動態變更。上游服務用固定設定導致連線失敗、故障恢復速度慢。

**技術挑戰**：服務啟停無自動註冊/反註冊；無統一服務清單與端點查詢；客戶端硬編碼或手動維護成本高。

**影響範圍**：可用性、擴縮效率、維運成本。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 缺少服務登錄中心（Service Registry）。
2. 客戶端無法自動獲取有效端點。
3. 啟停與健康狀態未同步。

**深層原因**：
- 架構層面：沒有集中式發現機制。
- 技術層面：未導入 Consul/etcd/ZooKeeper 等。
- 流程層面：部署流程未與註冊生命周期整合。

### Solution Design
**解決策略**：導入 Service Registry（如 Consul），服務啟動自動註冊，停止自動反註冊，並提供健康檢查。呼叫方透過 Registry 或 LB 查詢可用端點。

**實施步驟**：
1. 部署 Registry 並定義命名
- 實作細節：安裝 Consul，多節點高可用；定義 serviceName/tag。
- 資源：Consul、K8s/Docker
- 時間：1-2 人日

2. 服務註冊/反註冊整合
- 實作細節：服務啟停 hook 呼叫 Consul API；註冊健康檢查。
- 資源：SDK/Sidecar
- 時間：1-2 人日

3. 呼叫方整合查詢
- 實作細節：呼叫前查詢 /v1/health/service/<name>；或接入 LB。
- 資源：Client SDK/NGINX
- 時間：1 人日

**關鍵程式碼/設定**：
```json
// Consul 服務註冊（service.json）
{
  "Name": "orders",
  "ID": "orders-10.4.3.1-8080",
  "Address": "10.4.3.1",
  "Port": 8080,
  "Tags": ["v1"],
  "Check": {
    "HTTP": "http://10.4.3.1:8080/health",
    "Interval": "5s",
    "Timeout": "1s"
  }
}
```

```csharp
// .NET 啟動時自動註冊（簡化示意）
using Consul;
var consul = new ConsulClient();
var reg = new AgentServiceRegistration { Name="orders", Address="10.4.3.1", Port=8080, ID="orders-10.4.3.1-8080" };
await consul.Agent.ServiceRegister(reg);
// 停止時 ServiceDeregister(...)
```

實作環境：Consul、ASP.NET Core、NGINX/Envoy。
實測數據：
- 改善前：端點硬編碼，故障恢復需手動調整
- 改善後：動態註冊/反註冊，查詢即得有效端點
- 改善幅度：故障切換自動化，人工介入趨近於零

Learning Points
- 註冊中心與健康檢查設計
- 客戶端查詢與命名規則
- 服務生命周期 hook

技能要求
- 必備：HTTP API、Consul 基礎
- 進階：Sidecar、自動註冊 SDK

延伸思考
- 可應用於非 K8s 環境
- 風險：Registry 本身需高可用
- 優化：ACL/多資料中心/權限控管

Practice Exercise
- 基礎：手動向 Consul 註冊一個服務（30 分）
- 進階：在服務啟停自動註冊/反註冊（2 小時）
- 專案：為三個服務導入發現與呼叫流程（8 小時）

Assessment Criteria
- 功能完整性：健康可用名單可查
- 程式碼品質：生命周期與錯誤處理
- 效能優化：查詢延遲與快取
- 創新性：動態權重與灰度
```

## Case #6: 心跳誤判導致誤認存活，改為主動健康檢查

### Problem Statement
**業務場景**：服務以每 10 秒上報心跳，偶發 App Pool 崩潰或下游依賴掛掉時仍持續發心跳，Registry 將其視為存活，造成錯誤路由與請求失敗。

**技術挑戰**：被動心跳對「實際可服務能力」感知不足；偵測與隔離延遲長，不易快速繞過故障。

**影響範圍**：可用性、錯誤率、SLA。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 心跳僅代表進程活著，不代表服務可用。
2. 心跳間隔造成偵測盲區（如 10 秒）。
3. 缺乏對 API 層級的探測與降級。

**深層原因**：
- 架構層面：無獨立 Registrar 主動探測。
- 技術層面：健康檢查未覆蓋依賴（DB/Queue 等）。
- 流程層面：探測閾值與隔離策略未建立。

### Solution Design
**解決策略**：引入主動健康檢查（Registrar/Load Balancer 探測），服務提供 /health/ready 與 /health/live，檢查核心依賴（DB/MQ），不健康即從可用名單剔除；縮短探測間隔與超時。

**實施步驟**：
1. 健康端點與檢查項設計
- 實作細節：Readiness/Liveness 分離；檢查依賴。
- 資源：ASP.NET HealthChecks
- 時間：1 人日

2. Registry/LB 主動檢查
- 實作細節：Consul/NGINX 主動探測配置；降低 interval/timeout。
- 資源：Consul、NGINX
- 時間：1 人日

3. 故障隔離與恢復
- 實作細節：不健康移除；恢復自動加回；告警。
- 資源：監控/告警系統
- 時間：0.5 人日

**關鍵程式碼/設定**：
```csharp
// ASP.NET Core 健康檢查
builder.Services.AddHealthChecks()
    .AddSqlServer("conn", name: "db")
    .AddRabbitMQ("amqp://...", name: "mq");

app.MapHealthChecks("/health/live");     // 進程
app.MapHealthChecks("/health/ready");    // 依賴就緒
```

```json
// Consul 主動檢查
"Check": {
  "HTTP": "http://10.4.3.1:8080/health/ready",
  "Interval": "2s",
  "Timeout": "800ms",
  "DeregisterCriticalServiceAfter": "1m"
}
```

實作環境：ASP.NET Core、Consul、NGINX。
實測數據：
- 改善前：偵測延遲約心跳間隔（例 10s），偶有誤判存活
- 改善後：2s 間隔、<1s 超時，API 層可用性準確
- 改善幅度：故障繞過時間縮短約 80%-90%

Learning Points
- Readiness/Liveness 差異
- 主動探測與依賴檢查
- 故障隔離策略

技能要求
- 必備：健康檢查實作、Consul/NGINX 配置
- 進階：自適應探測、金絲雀隔離

延伸思考
- 適用任何需要高可用的服務
- 風險：過於頻繁探測帶來負載
- 優化：指數回退、連續錯誤閾值

Practice Exercise
- 基礎：加上 /health/ready 與資料庫檢查（30 分）
- 進階：Consul 主動檢查+自動剔除（2 小時）
- 專案：設計完整健康面板與告警（8 小時）

Assessment Criteria
- 功能完整性：可正確剔除/恢復節點
- 程式碼品質：檢查模組化、可測
- 效能優化：探測負載可控
- 創新性：依賴權重化健康評分
```

## Case #7: 由伺服端負載平衡整合發現，簡化客戶端與提升可用性

### Problem Statement
**業務場景**：目前由客戶端自行查詢 Registry 並選擇節點呼叫，導致各語言實作不一，錯誤處理與重試不一致，變更難以集中治理。

**技術挑戰**：客戶端複雜度高；無法快速全局調參（超時、重試、斷路器）；異常擴散。

**影響範圍**：服務一致性、維護成本、可用性。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 客戶端承擔發現與負載平衡邏輯。
2. 各端實作差異大，難統一。
3. 故障策略分散。

**深層原因**：
- 架構層面：缺少中心化 L7 LB 與服務治理。
- 技術層面：未整合 Registry 與 LB。
- 流程層面：調參與灰度需遍佈多端。

### Solution Design
**解決策略**：引入伺服端 LB（NGINX/Envoy），由 LB 向 Registry 查詢健康端點並進行負載分配、重試、超時與熔斷。客戶端僅向 LB 請求，大幅簡化。

**實施步驟**：
1. 部署 LB 並接 Registry
- 實作細節：via Consul-Template 動態渲染 upstream 或 Envoy xDS。
- 資源：NGINX/Envoy、Consul-Template
- 時間：1-2 人日

2. 配置流控策略
- 實作細節：超時、重試、熔斷、限流。
- 資源：LB 配置
- 時間：1 人日

3. 客戶端切換與觀測
- 實作細節：指向 LB；監控錯誤率與延遲。
- 資源：APM/日誌
- 時間：0.5 人日

**關鍵程式碼/設定**：
```nginx
# 透過 consul-template 生成 upstream（簡化）
upstream orders_upstream {
  server 10.4.3.1:8080 max_fails=3 fail_timeout=10s;
  # ... 動態生成更多節點
}
server {
  location /orders/ {
    proxy_connect_timeout 500ms;
    proxy_read_timeout 800ms;
    proxy_next_upstream error timeout http_500 http_502;
    proxy_pass http://orders_upstream;
  }
}
```

實作環境：NGINX/Envoy、Consul/etcd。
實測數據：
- 改善前：客戶端複雜且不一致，錯誤率高
- 改善後：中心化策略與治理，錯誤快速繞過
- 改善幅度：客戶端代碼大幅簡化；故障域縮小

Learning Points
- 伺服端 LB 與 Registry 整合
- 重試與熔斷策略
- 動態配置渲染

技能要求
- 必備：LB 基礎、反向代理配置
- 進階：xDS/服務網格基礎

延伸思考
- 適用於多語言/多團隊環境
- 風險：LB 需高可用、避免瓶頸
- 優化：多層 LB、地域容災

Practice Exercise
- 基礎：配置一個 upstream 與重試（30 分）
- 進階：consul-template 動態生 upstream（2 小時）
- 專案：為兩個服務落地 LB+Registry（8 小時）

Assessment Criteria
- 功能完整性：自動獲取健康端點
- 程式碼品質：模板/配置清晰
- 效能優化：重試策略合理
- 創新性：按健康分數加權
```

## Case #8: 以 DNS（SRV/DDNS）實作輕量級 Service Discovery

### Problem Statement
**業務場景**：團隊規模尚小，導入完整 Registry 成本過高，但服務仍有動態端點需求。

**技術挑戰**：需快速、低成本達成服務發現；兼顧健康與權重控制有限。

**影響範圍**：上線速度、維運複雜度、成本。

**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 沒有預算/能力維護 Consul/etcd。
2. 部署環境已有 DNS 基礎設施。
3. 需求較簡單、服務數量有限。

**深層原因**：
- 架構層面：早期不宜過度工程化。
- 技術層面：DNS SRV/TXT 可滿足基本映射。
- 流程層面：登錄/更新流程可自動化。

### Solution Design
**解決策略**：使用 DNS SRV 記錄宣告服務名對應的目標主機與 Port；服務啟停透過 DDNS 更新記錄；呼叫端查詢 SRV 取得端點並實作簡單健康重試。

**實施步驟**：
1. 規劃域名與 SRV 記錄
- 實作細節：_orders._tcp.svc.local 指向多節點。
- 資源：DNS 伺服器（BIND/Windows DNS）
- 時間：0.5 人日

2. 自動更新（DDNS）
- 實作細節：服務啟停調用 nsupdate 更新 A/SRV。
- 資源：nsupdate 腳本
- 時間：0.5 人日

3. 客戶端查詢與重試
- 實作細節：使用 SRV 查詢庫；簡單重試/輪詢。
- 資源：語言 SRV 客戶端
- 時間：0.5 人日

**關鍵程式碼/設定**：
```bash
# nsupdate 更新 SRV 記錄（示意）
server dns.local
zone svc.local
update add _orders._tcp.svc.local. 60 IN SRV 10 5 8080 orders-1.svc.local.
send
```

實作環境：DNS（BIND/Windows DNS）、小規模服務。
實測數據：
- 改善前：端點硬編碼，變更需手工
- 改善後：SRV 查詢即可獲取端點
- 改善幅度：部署自動化，配置錯誤下降

Learning Points
- SRV/TXT 於發現的應用
- DDNS 自動化
- 簡易健康與重試

技能要求
- 必備：DNS 基礎
- 進階：權重/優先級調整

延伸思考
- 適用早期/小規模團隊
- 風險：無豐富健康治理
- 優化：結合 LB/探測

Practice Exercise
- 基礎：建立一筆 SRV 記錄（30 分）
- 進階：啟停觸發 nsupdate（2 小時）
- 專案：替兩個服務導入 SRV 發現（8 小時）

Assessment Criteria
- 功能完整性：正確查詢與更新
- 程式碼品質：腳本健壯
- 效能優化：TTL 與快取設計
- 創新性：自動權重調整
```

## Case #9: 透過 Discovery 做組態集中管理，避免配置飄移

### Problem Statement
**業務場景**：多個服務維護相同環境配置（連線字串、MQ 主機、外部 API），版本/環境差異導致配置飄移與事故。

**技術挑戰**：缺乏單一可信來源（Single Source of Truth），配置變更需重發版；密鑰與憑證散佈風險高。

**影響範圍**：故障率、維運成本、安全。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 配置散落於各服務，無集中存取。
2. 變更流程需發版，耗時易錯。
3. 憑證與密鑰無統一管理。

**深層原因**：
- 架構層面：未使用集中 KV（Consul KV）。
- 技術層面：服務不具備開機取配置能力。
- 流程層面：變更/審批/審計缺失。

### Solution Design
**解決策略**：使用 Consul KV 做全域配置；服務啟動僅保留最小引導配置（如 Registry 位址與憑證），其餘組態於註冊後讀取。敏感資訊結合 Secrets 管理。

**實施步驟**：
1. 配置盤點與分級
- 實作細節：區分敏感/非敏感、環境/服務級。
- 資源：配置清單
- 時間：1 人日

2. KV 結構與讀取 SDK
- 實作細節：設計 key 命名；服務啟動讀取與快取。
- 資源：Consul KV、SDK
- 時間：1-2 人日

3. 變更流程與審計
- 實作細節：變更審批、審計日誌、灰度變更。
- 資源：變更工具
- 時間：1 人日

**關鍵程式碼/設定**：
```bash
# Consul KV（示意）
consul kv put config/catalog/redis "redis:6379"
consul kv put config/common/featureFlag:recommendation "on"
```

```csharp
// 開機載入配置（簡化）
using Consul;
var kv = new ConsulClient();
var pair = await kv.KV.Get("config/catalog/redis");
var redisConn = Encoding.UTF8.GetString(pair.Response.Value);
```

實作環境：Consul KV、ASP.NET Core。
實測數據：
- 改善前：多源配置、手動變更多處
- 改善後：集中配置，服務啟動自取
- 改善幅度：上線與變更錯誤率下降；變更時間縮短

Learning Points
- 配置分級與命名約定
- 啟動引導配置最小化
- 變更審批與審計

技能要求
- 必備：KV 使用、SDK 調用
- 進階：熱更新、加密密鑰整合

延伸思考
- 適用於多環境與多團隊
- 風險：單點配置中心需高可用
- 優化：本地快取/回退策略

Practice Exercise
- 基礎：從 KV 讀取一筆配置（30 分）
- 進階：實作配置熱更新回調（2 小時）
- 專案：替三個服務落地集中配置（8 小時）

Assessment Criteria
- 功能完整性：配置集中與可讀
- 程式碼品質：錯誤處理與回退
- 效能優化：快取與降載
- 創新性：動態配置灰度
```

## Case #10: 訂單受理改為非同步，降低前端等待時間

### Problem Statement
**業務場景**：訂單處理包含支付、記帳、庫存、通知等長流程。同步 HTTP 造成前端長時間等待與超時，體驗差且後端扛不住尖峰。

**技術挑戰**：將長流程從請求路徑中移除，提供立即回覆並保證後續可靠處理。

**影響範圍**：使用者體驗、吞吐量、後端負載。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 同步耦合使端到端延遲高，錯誤率提升。
2. 無緩衝層吸收尖峰。
3. 無事件通知機制進行後續處理。

**深層原因**：
- 架構層面：未採用消息隊列/事件驅動。
- 技術層面：缺乏可靠投遞與持久化。
- 流程層面：狀態機與最終一致性未設計。

### Solution Design
**解決策略**：前端提交 → API 立即返回「已受理」與單號 → 後端將訂單事件持久化並發布到 MQ（RabbitMQ/Kafka） → 各服務訂閱處理，最終一致性透過事件回覆/狀態機。

**實施步驟**：
1. 事件模型與狀態機
- 實作細節：OrderCreated、PaymentConfirmed、OrderCompleted。
- 資源：事件契約
- 時間：1 人日

2. MQ 部署與 Topic
- 實作細節：RabbitMQ direct/topic exchange；持久化開啟。
- 資源：RabbitMQ/Kafka
- 時間：1 人日

3. Producer/Consumer 實作
- 実作細節：確保發佈前先本地持久化；消費端 Ack/重試。
- 資源：官方客戶端
- 時間：2 人日

**關鍵程式碼/設定**：
```csharp
// RabbitMQ Producer（簡化）
var factory = new ConnectionFactory(){ Uri = new Uri("amqp://...") };
using var conn = factory.CreateConnection();
using var ch = conn.CreateModel();
ch.ExchangeDeclare("orders", ExchangeType.Topic, durable:true);
var body = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(orderEvent));
var props = ch.CreateBasicProperties(); props.DeliveryMode = 2; // persistent
ch.BasicPublish("orders", "order.created", props, body);
```

實作環境：RabbitMQ、ASP.NET Core。
實測數據：
- 改善前：前端等待整個流程，易超時
- 改善後：即時回覆「已受理」，後端異步處理
- 改善幅度：端到端體感延遲顯著下降；吞吐提升

Learning Points
- 異步/事件驅動設計
- 持久化與 Ack
- 狀態機與最終一致性

技能要求
- 必備：RabbitMQ/Kafka 基礎
- 進階：重試/死信與補償

延伸思考
- 適用任何長流程
- 風險：一致性延遲
- 優化：用戶通知與進度查詢

Practice Exercise
- 基礎：發佈一則 order.created（30 分）
- 進階：完成消費端與 Ack/重試（2 小時）
- 專案：訂單全流程事件化（8 小時）

Assessment Criteria
- 功能完整性：受理即回覆，後續完成
- 程式碼品質：事件契約穩定
- 效能優化：吞吐與穩定性
- 創新性：進度查詢/通知
```

## Case #11: 用 MQ 實作可靠同步 RPC（Request/Response Queue）

### Problem Statement
**業務場景**：某些查詢/操作需同步回應，但 HTTP 在網路抖動下重試與冪等難控，可靠度不足。

**技術挑戰**：需要同步語義與可靠傳輸，處理網路錯誤與超時，確保不丟消息。

**影響範圍**：可靠性、使用者體驗、數據一致性。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. HTTP 無持久化與內建重投機制。
2. 端到端冪等/重試策略缺失。
3. 回應關聯困難。

**深層原因**：
- 架構層面：缺少消息雙向通道。
- 技術層面：未使用 CorrelationId/ReplyTo。
- 流程層面：無統一超時/重試約定。

### Solution Design
**解決策略**：採 RabbitMQ RPC Pattern：Client 對 Request Queue 發送消息，帶 CorrelationId 與 ReplyTo；服務處理後發回 Reply Queue；Client 等待相同 CorrelationId 回覆，設置超時與重試。

**實施步驟**：
1. 定義請求/回應契約
- 實作細節：JSON/Protobuf；CorrelationId。
- 資源：契約文件
- 時間：0.5 人日

2. 配置 Request/Reply Queue
- 實作細節：持久化、獨佔/自動刪除 Reply Queue（或共享）。
- 資源：RabbitMQ
- 時間：0.5 人日

3. Client/Server 實作
- 實作細節：超時、重試、冪等鍵。
- 資源：客戶端 SDK
- 時間：1-2 人日

**關鍵程式碼/設定**：
```csharp
// Client 發送
props.CorrelationId = Guid.NewGuid().ToString();
props.ReplyTo = "reply.q";
ch.BasicPublish("", "rpc.request", props, body);

// Server 消費
ch.BasicConsume("rpc.request", autoAck:false, consumer);
consumer.Received += (m, ea) => {
  var respProps = ch.CreateBasicProperties();
  respProps.CorrelationId = ea.BasicProperties.CorrelationId;
  ch.BasicPublish("", ea.BasicProperties.ReplyTo, respProps, resultBody);
  ch.BasicAck(ea.DeliveryTag, false);
};
```

實作環境：RabbitMQ、ASP.NET Core。
實測數據：
- 改善前：HTTP 失敗率高、重試難控
- 改善後：持久化、關聯可追蹤、可重試
- 改善幅度：成功率與可觀測性提升

Learning Points
- RPC over MQ 模式
- CorrelationId 與 ReplyTo
- 超時、重試、冪等

技能要求
- 必備：RabbitMQ 基礎
- 進階：共享回應隊列與並發處理

延伸思考
- 適用需同步回應但要求高可靠
- 風險：端到端延遲略增
- 優化：預取/並發窗口控制

Practice Exercise
- 基礎：建立 RPC Request/Reply 隊列（30 分）
- 進階：實作超時與重試（2 小時）
- 專案：把一個 HTTP RPC 改為 MQ RPC（8 小時）

Assessment Criteria
- 功能完整性：請求關聯正確
- 程式碼品質：錯誤處理完善
- 效能優化：並發與預取
- 創新性：動態路由與優先級
```

## Case #12: 事件驅動把 N×M 整合關係降為 N+M

### Problem Statement
**業務場景**：多個服務間相互呼叫，新增/變更一個服務都需調整多處呼叫方，關係複雜、脆弱、難擴展。

**技術挑戰**：點對點整合數暴增；耦合緊密；變更牽引大。

**影響範圍**：演進速度、可靠性、維護成本。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 直連呼叫導致多對多關係。
2. 無事件匯流排，無法解耦。
3. 無統一主題與訂閱模型。

**深層原因**：
- 架構層面：未採用 Pub/Sub。
- 技術層面：消息路由與主題缺失。
- 流程層面：資料契約與版本未管理。

### Solution Design
**解決策略**：導入消息匯流排（RabbitMQ/Kafka），各服務作為發佈者或訂閱者，依主題分發事件。新增服務僅訂閱主題即可，無需改動發佈者，將 N×M 降為 N+M。

**實施步驟**：
1. 主題與事件契約設計
- 實作細節：topic key 設計、版本管理。
- 資源：契約倉庫
- 時間：1 人日

2. 匯流排部署與路由
- 實作細節：RabbitMQ topic exchange；Kafka topics。
- 資源：MQ
- 時間：1 人日

3. 發佈/訂閱實作與觀測
- 實作細節：死信/重試；消費延遲面板。
- 資源：SDK、監控
- 時間：1-2 人日

**關鍵程式碼/設定**：
```csharp
// 發佈產品上架事件
ch.ExchangeDeclare("catalog", ExchangeType.Topic, durable:true);
ch.BasicPublish("catalog", "product.created", props, body);

// 訂閱
ch.QueueDeclare("recommend.product", durable:true, exclusive:false, autoDelete:false);
ch.QueueBind("recommend.product", "catalog", "product.*");
```

實作環境：RabbitMQ/Kafka。
實測數據：
- 改善前：新增整合需改多個呼叫方
- 改善後：只需訂閱主題即可
- 改善幅度：整合關係由 O(N²) 降為 O(N)

Learning Points
- Pub/Sub 與主題設計
- 路由鍵與版本策略
- 解耦與變更隔離

技能要求
- 必備：MQ 路由基礎
- 進階：事件版本/演進策略

延伸思考
- 適用資料廣播、多消費者場景
- 風險：無消費者時消息積壓
- 優化：壓測與背壓策略

Practice Exercise
- 基礎：建立一個 topic exchange 與綁定（30 分）
- 進階：兩個服務訂閱不同路由鍵（2 小時）
- 專案：把三個直連整合改為事件驅動（8 小時）

Assessment Criteria
- 功能完整性：正確分發與消費
- 程式碼品質：契約穩定
- 效能優化：積壓可控
- 創新性：動態路由/規則
```

## Case #13: 以事件驅動與 2PC 思維處理分散式交易一致性

### Problem Statement
**業務場景**：使用者從錢包（BANK1）扣款並在遊戲（GAME1）加點，需保證一致性：成功則雙方都變更，失敗則全部回復。

**技術挑戰**：跨服務/跨資料庫，無法依賴單一 RDBMS 交易；需處理部分失敗與超時。

**影響範圍**：資金準確性、風險、信任。

**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 資料分散，RDBMS 本地交易無法涵蓋。
2. 同步呼叫遇故障難以回復。
3. 缺乏統一的交易協調。

**深層原因**：
- 架構層面：未採用事件/交易協調器。
- 技術層面：無可靠投遞和狀態機。
- 流程層面：補償/回滾策略未設計。

### Solution Design
**解決策略**：實作 Saga/2PC 思維：Order Service 建立交易記錄（NEW）並發布事件；Game Service 收到後預留點數並回覆確認；Order 收到確認改為 OPEN。若逾時未回覆或失敗，則標記 CANCEL 並發佈取消事件，對方執行補償（釋放預留）。

**實施步驟**：
1. 交易狀態機與超時
- 實作細節：NEW/OPEN/CANCEL；超時任務（scheduler）。
- 資源：資料模型
- 時間：1 人日

2. 事件流與可靠投遞
- 實作細節：持久化後發佈；消費端冪等。
- 資源：MQ
- 時間：1-2 人日

3. 補償與審計
- 實作細節：取消事件重試至確認；審計記錄。
- 資源：日志/審計系統
- 時間：1 人日

**關鍵程式碼/設定**：
```csharp
// 1) 建立交易並發事件
txRepo.Add(new Tx{ Id=id, Status="NEW" });
Publish("order.created", new { TxId=id, Amount=100 });

// 2) Game 預留並回覆
On("order.created", msg => {
  reservePoints(msg.Amount);
  Publish("game.confirmed", new { TxId=msg.TxId });
});

// 3) Order 收到確認
On("game.confirmed", msg => txRepo.Update(msg.TxId, "OPEN"));

// 逾時補償
if (timeout) {
  txRepo.Update(id, "CANCEL");
  Publish("order.cancelled", new { TxId=id });
}
```

實作環境：RabbitMQ/Kafka、ASP.NET Core。
實測數據：
- 改善前：跨服務交易難以保障一致
- 改善後：狀態機+事件補償可控
- 改善幅度：失敗處理有據可循，漏單風險下降

Learning Points
- Saga/2PC 核心概念
- 可靠投遞與冪等
- 超時/補償策略

技能要求
- 必備：事件驅動、交易狀態機
- 進階：分散式鎖與一致性模式

延伸思考
- 適用金流/庫存/帳務
- 風險：長尾補償與人為干預
- 優化：監控告警與人工介入流程

Practice Exercise
- 基礎：訂單→遊戲點數確認事件流（30 分）
- 進階：加入逾時取消與補償（2 小時）
- 專案：完整實作一個雙方交易 Saga（8 小時）

Assessment Criteria
- 功能完整性：一致性與補償覆蓋
- 程式碼品質：冪等與審計完善
- 效能優化：延遲可控
- 創新性：可視化交易追蹤
```

## Case #14: 耐久消息與離線容忍，避免消費端故障丟單

### Problem Statement
**業務場景**：某些下游服務會短暫故障或維護，如用 HTTP 同步，請求將失敗且資料遺失。

**技術挑戰**：需在消費端離線時仍能保留消息，待恢復後續處理，達成使命必達。

**影響範圍**：資料完整性、可用性。

**複雜度評級**：低-中

### Root Cause Analysis
**直接原因**：
1. 直接呼叫無持久化與重送。
2. 消費端暫停即資料流失。
3. 無死信與補償。

**深層原因**：
- 架構層面：無消息中介儲存後轉送。
- 技術層面：未開啟持久化與 Ack。
- 流程層面：無監控積壓與回放。

### Solution Design
**解決策略**：導入 MQ，開啟持久化（durable queue + persistent message），消費端採手動 Ack；消費端故障時消息保留，恢復後繼續處理；配置死信與重試。

**實施步驟**：
1. 隊列與消息持久化
- 實作細節：durable/exclusive 設定；DeliveryMode=2。
- 資源：RabbitMQ
- 時間：0.5 人日

2. 消費端 Ack 與重試
- 實作細節：手動 Ack，失敗 Nack 重回或進死信。
- 資源：SDK
- 時間：0.5 人日

3. 監控積壓
- 實作細節：隊列長度、消費延遲面板；告警。
- 資源：監控
- 時間：0.5 人日

**關鍵程式碼/設定**：
```csharp
// 宣告持久化隊列
ch.QueueDeclare("q", durable:true, exclusive:false, autoDelete:false);
var props = ch.CreateBasicProperties(); props.DeliveryMode = 2;
ch.BasicPublish("", "q", props, body);

// 消費端手動 Ack
ch.BasicConsume("q", autoAck:false, consumer);
consumer.Received += (m, ea) => {
  try { Process(ea.Body); ch.BasicAck(ea.DeliveryTag, false); }
  catch { ch.BasicNack(ea.DeliveryTag, false, requeue:false); } // 或丟 DLX
};
```

實作環境：RabbitMQ。
實測數據：
- 改善前：下游離線導致丟單
- 改善後：消息保留，恢復後續處理
- 改善幅度：消息丟失降為 0（在正確配置前提）

Learning Points
- 持久化與 Ack/Nack
- 死信隊列與重試
- 積壓監控

技能要求
- 必備：消息模型
- 進階：重放/補償策略

延伸思考
- 適用關鍵資料流
- 風險：磁碟壓力、堆積
- 優化：分段處理/限流

Practice Exercise
- 基礎：開啟 durable/persistent（30 分）
- 進階：實作死信與重試（2 小時）
- 專案：為一條關鍵流程落地持久化（8 小時）

Assessment Criteria
- 功能完整性：離線期間不丟消息
- 程式碼品質：Ack/錯誤處理
- 效能優化：控制堆積
- 創新性：重放工具
```

## Case #15: 橫向擴展消費端，平滑尖峰負載

### Problem Statement
**業務場景**：行銷活動造成瞬時請求暴增，單一消費端無法即時處理導致超時與排隊。

**技術挑戰**：需要快速水平擴展消費端，提高吞吐並維持處理穩定。

**影響範圍**：性能、穩定性、成本。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 單消費端吞吐不足。
2. 無並行處理與預取控制。
3. 負載不均與背壓缺失。

**深層原因**：
- 架構層面：未設計水平擴展與競爭消費。
- 技術層面：預取與自動擴縮未配置。
- 流程層面：缺乏容量規劃與指標。

### Solution Design
**解決策略**：啟動多個消費端實例（競爭消費），設定合理 prefetch（QoS），自動擴縮依據隊列深度與處理延遲，平滑尖峰。

**實施步驟**：
1. 並發與預取配置
- 實作細節：BasicQos(prefetchCount)；避免壓垮單體。
- 資源：MQ
- 時間：0.5 人日

2. 橫向擴展與自動擴縮
- 實作細節：副本數與 HPA（如 K8s 基於自定義指標）。
- 資源：容器平臺
- 時間：1 人日

3. 觀測與調優
- 實作細節：吞吐、延遲、堆積、錯誤率面板。
- 資源：監控
- 時間：0.5 人日

**關鍵程式碼/設定**：
```csharp
// 設定預取
ch.BasicQos(0, prefetchCount: 50, global: false);
// 多副本部署由平台（如 K8s Deployment replicas）控制
```

實作環境：RabbitMQ、K8s/容器。
實測數據：
- 改善前：尖峰時延遲飆升、超時
- 改善後：多消費者並行處理，延遲平滑
- 改善幅度：吞吐提升、多峰平滑

Learning Points
- 競爭消費與預取
- 擴縮策略與指標
- 背壓與限流

技能要求
- 必備：MQ 消費模型
- 進階：自動擴縮與自定義指標

延伸思考
- 適用所有高峰業務
- 風險：過度並行造成下游壓力
- 優化：令牌桶限流、熔斷

Practice Exercise
- 基礎：設定 prefetch 並啟兩個消費者（30 分）
- 進階：基於隊列深度自動擴縮（2 小時）
- 專案：完整尖峰壓測與調參（8 小時）

Assessment Criteria
- 功能完整性：擴縮有效
- 程式碼品質：可觀測與限流
- 效能優化：延遲平滑
- 創新性：自適應預取
```

## Case #16: 分散式追蹤與關聯 ID，快速回溯跨服務請求

### Problem Statement
**業務場景**：一個請求需穿越多個服務，出錯時需快速定位問題。但日誌分散且缺乏共同「追蹤號」，排障成本高。

**技術挑戰**：跨服務關聯與全鏈路可觀測；需要集中收集/查詢與一致標頭傳遞。

**影響範圍**：MTTR、運維效率、客訴處理。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 各服務日誌不一致，無關聯 ID。
2. 無集中聚合與查詢。
3. 缺乏即時還原能力。

**深層原因**：
- 架構層面：無統一追蹤號（如 X-Correlation-ID）。
- 技術層面：無日誌管道與格式標準。
- 流程層面：排障流程缺失。

### Solution Design
**解決策略**：在入口（Gateway）產生/驗證 Correlation ID，透過標頭傳遞；各服務日誌統一輸出此 ID 至集中系統（ELK/OpenSearch），或用分散追蹤（OpenTelemetry/Jaeger）補齊時間線。

**實施步驟**：
1. 標頭與中介軟體
- 實作細節：若無則產生 X-Correlation-ID；全鏈路透傳。
- 資源：ASP.NET Middleware
- 時間：0.5 人日

2. 日誌統一與收集
- 實作細節：結構化日誌（JSON）、Ship 到 ELK。
- 資源：Serilog/NLog、Filebeat
- 時間：1-2 人日

3. 追蹤導入（可選）
- 實作細節：OpenTelemetry SDK、Jaeger。
- 資源：OTEL
- 時間：1-2 人日

**關鍵程式碼/設定**：
```csharp
// ASP.NET Core 中介軟體
app.Use(async (ctx, next) => {
  var cid = ctx.Request.Headers["X-Correlation-ID"].FirstOrDefault() ?? Guid.NewGuid().ToString();
  ctx.Response.Headers["X-Correlation-ID"] = cid;
  using (LogContext.PushProperty("CorrelationId", cid)) {
    await next();
  }
});
```

實作環境：ASP.NET Core、ELK/OpenSearch、OpenTelemetry。
實測數據：
- 改善前：跨服務排障需逐一比對時間與內容
- 改善後：以追蹤號一鍵聚合，快速定位
- 改善幅度：MTTR 顯著下降；排障效率提升

Learning Points
- 關聯 ID 與結構化日誌
- 日誌集中與查詢
- 分散式追蹤

技能要求
- 必備：中介軟體、日誌框架
- 進階：OTEL/Tracing

延伸思考
- 適用所有跨服務場景
- 風險：敏感資訊脫敏
- 優化：採樣率與指標面板

Practice Exercise
- 基礎：加入 X-Correlation-ID（30 分）
- 進階：串 ELK 並以 ID 聚合查詢（2 小時）
- 專案：全鏈路追蹤落地（8 小時）

Assessment Criteria
- 功能完整性：鏈路可追
- 程式碼品質：一致性與脫敏
- 效能優化：採樣與輸出量
- 創新性：視覺化追蹤
```

## Case #17: 先備條件—建置快速配置/部署/監控能力（DevOps）

### Problem Statement
**業務場景**：團隊欲導入微服務，但尚缺快速配置、部署與監控能力，導致任何變更緩慢且高風險，難以支撐微服務複雜度。

**技術挑戰**：多服務 CI/CD、基礎設施即程式碼（IaC）、可觀測性缺失。

**影響範圍**：交付速度、品質、擴展能力。

**複雜度評級**：中-高

### Root Cause Analysis
**直接原因**：
1. 手動配置與部署，缺乏自動化。
2. 監控/告警體系缺失。
3. 無環境一致性保障。

**深層原因**：
- 架構層面：缺 IaC/模板化。
- 技術層面：缺 CI/CD 與健康標準。
- 流程層面：缺版本/變更治理。

### Solution Design
**解決策略**：優先建置 CI/CD、基礎設施即程式碼（Terraform/Helm）、統一監控與告警。以模板化專案、標準化健康檢查與運行指標，達到快速、安全交付。

**實施步驟**：
1. CI/CD 流水線模板
- 實作細節：Build/Test/SCA/SAST/Deploy。
- 資源：GitHub Actions/Azure DevOps
- 時間：1-2 人日/服務模板

2. IaC 與環境一致性
- 實作細節：Terraform/Helm；配置版本化。
- 資源：IaC 工具
- 時間：2 人日

3. 監控與告警
- 實作細節：APM、Metrics、Trace 統一；SLO/SLA。
- 資源：Prometheus/Grafana
- 時間：2 人日

**關鍵程式碼/設定**：
```yaml
# GitHub Actions（簡化）
name: ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - run: dotnet build && dotnet test
    - run: docker build -t app:${{ github.sha }} .
    - run: helm upgrade --install app ./chart --set image.tag=${{ github.sha }}
```

實作環境：GitHub Actions、Helm/Terraform、Prometheus/Grafana。
實測數據：
- 改善前：手動部署、缺觀測
- 改善後：自動化交付、可觀測
- 改善幅度：部署頻率提升、變更失敗率下降（以 DORA 指標評估）

Learning Points
- DevOps 先備能力
- 模板化/標準化
- DORA 指標

技能要求
- 必備：CI/CD、容器
- 進階：IaC 與 SRE 實務

延伸思考
- 適用任何轉微服務的團隊
- 風險：自動化誤操作
- 優化：審批、金絲雀/藍綠

Practice Exercise
- 基礎：建立一條 Build+Test pipeline（30 分）
- 進階：Helm 部署與回滾（2 小時）
- 專案：為一個服務打包完整模板（8 小時）

Assessment Criteria
- 功能完整性：自動化端到端
- 程式碼品質：pipeline 可重用
- 效能優化：併行與快取
- 創新性：自動化品質門檻
```

## Case #18: 選型取捨—RabbitMQ/Kafka/MSMQ/Redis 的務實比較

### Problem Statement
**業務場景**：需導入消息中介解耦與可靠傳輸，但不同方案特性差異大，盲目選型導致後續難以滿足需求或運維困難。

**技術挑戰**：在可靠性、吞吐、延遲、靈活度、運維成本間取捨。

**影響範圍**：系統穩定性、擴展性、成本。

**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 未明確需求（事件流、命令隊列、流處理）。
2. 忽視客戶端與生態成熟度。
3. 未評估基礎設施依賴與團隊經驗。

**深層原因**：
- 架構層面：需求與系統特性不匹配。
- 技術層面：可靠性/靈活性/吞吐的平衡。
- 流程層面：運維與監控能力不足。

### Solution Design
**解決策略**：基於需求映射選型：
- RabbitMQ：豐富路由、命令/事件解耦、可靠投遞、中吞吐。
- Kafka：高吞吐順序日誌、事件流/回放、長期保留。
- MSMQ：Windows 環境下強可靠（含客戶端 Store&Forward）、但生態老舊。
- Redis Stream/列表：輕量任務隊列，可靠性有限。

制定選型矩陣與 PoC，以最小成本滿足當前需求並可演進。

**實施步驟**：
1. 需求維度與權重
- 實作細節：可靠性、延遲、吞吐、路由、保留、運維。
- 資源：選型表
- 時間：0.5 人日

2. PoC 與觀測
- 實作細節：基準測試/故障演練。
- 資源：壓測工具
- 時間：1-2 人日

3. 運維方案
- 實作細節：監控、告警、備援。
- 資源：平台工具
- 時間：1 人日

**關鍵程式碼/設定**：
```xml
<!-- MSMQ Response Queue/CorrelationId 示意 -->
<System.Messaging>
  <!-- 以 CorrelationId 關聯請求/回應 -->
</System.Messaging>
```

實作環境：RabbitMQ/Kafka/MSMQ/Redis（擇一或多個）。
實測數據：
- 改善前：無系統性選型，後期返工
- 改善後：基於指標與 PoC 的決策
- 改善幅度：風險可控、滿足需求

Learning Points
- 消息系統特性與適用場景
- 指標驅動選型
- PoC 與運維考量

技能要求
- 必備：各系統基本知識
- 進階：基準測試與容量規劃

延伸思考
- 可多系統並存分工
- 風險：複雜度上升
- 優化：統一事件契約與治理

Practice Exercise
- 基礎：列出你的需求維度（30 分）
- 進階：完成 RabbitMQ 與 Kafka 的小 PoC（2 小時）
- 專案：產出選型矩陣與結論（8 小時）

Assessment Criteria
- 功能完整性：需求覆蓋
- 程式碼品質：PoC 可重現
- 效能優化：合理參數
- 創新性：多方案互補
```

——
以下幾個案例聚焦在相同大方向的不同切面，供完整學習路徑使用：

## Case #19: API Gateway 安全外觀，隱匿內部拓撲與最小暴露

### Problem Statement
對外直接暴露內部多服務端點，增加攻擊面、洩漏內部實作與版本差異，安全與維護風險高。

...（為節省篇幅，此案例與 Case #2、#4 有重疊之處；可按需展開或合併到 Case #2/#4 的實作）

## Case #20: 以 Gateway/事件回傳設計用戶「貨運單號」式查詢體驗

### Problem Statement
用戶在多服務協作的長流程中需要可視化進度（文章提出「像貨運 tracking number」），現況缺乏對單一事件的聚合查詢。

...（可作為 Case #16 的延伸，重點在用戶可視化體驗；實作包含事件儲存、查詢 API 與前端頁面）

（若需要完整 20 個案例，可將 #19、#20 作為擴展練習；核心 18 個案例已涵蓋文章主旨與關鍵基礎建設。）

--------------------------------

案例分類

1. 按難度分類
- 入門級：#3, #8, #14
- 中級：#1, #2, #4, #5, #6, #7, #9, #10, #11, #12, #16
- 高級：#13, #15, #17, #18

2. 按技術領域分類
- 架構設計類：#1, #2, #4, #7, #12, #13, #17, #18
- 效能優化類：#3, #6, #7, #15
- 整合開發類：#5, #8, #9, #10, #11, #12
- 除錯診斷類：#16
- 安全防護類：#2, #4, #7, #16（審計）

3. 按學習目標分類
- 概念理解型：#12, #13, #18
- 技能練習型：#3, #5, #6, #8, #9, #10, #11, #16
- 問題解決型：#1, #2, #4, #7, #14, #15
- 創新應用型：#17（流程/能力建設）, #18（選型策略）

案例關聯圖（學習路徑建議）
- 建議先學：
  - 基礎門檻與觀念：#17（DevOps 先備）、#5（Service Discovery 基礎）、#8（DNS 輕量方案）
- 之後學：
  - 對外入口與體驗：#1（聚合）、#2（認證）、#3（快取）、#4（版本轉譯）
  - 內部服務治理：#6（主動健康）、#7（伺服端 LB）
  - 配置與整合：#9（集中配置）
- 進階通信與資料一致性：
  - #10（異步受理）、#11（MQ RPC）、#12（事件解耦）、#13（Saga/2PC）
  - 可用性與容量：#14（耐久消息）、#15（水平擴展）
- 可觀測與持續優化：
  - #16（分散式追蹤）
  - #18（選型權衡，持續演進）

依賴關係
- #5/#8 是 #6/#7 的依賴（先有發現再談健康/LB）
- #1/#2/#3/#4 依賴 Gateway 能力與 #5（服務定位）
- #10/#11/#12/#13 依賴 MQ（可先從 #10/#12 入門再進 #11/#13）
- #16 受益於 #1/#2（入口統一易注入追蹤）
- #17 是整體前置能力，支撐所有案例
- #18 為 MQ 相關案例（#10/#11/#12/#13/#14/#15）的選型前置

完整學習路徑（建議）
1) #17 → 夯實 DevOps 基礎
2) #5/#8 → 建立服務發現基礎
3) #1/#2/#3/#4 → 打造統一對外入口與體驗
4) #6/#7/#9 → 健康、LB、配置治理
5) #10/#12 → 事件/異步的核心思維
6) #11/#13 → 可靠同步與一致性進階
7) #14/#15 → 可用性與容量工程
8) #16 → 全鏈路可觀測
9) #18 → 選型與演進策略
10) 擴展 #19/#20 → 安全外觀與用戶可視化體驗

以上 18 個核心案例覆蓋文章提出的關鍵基礎建設（API Gateway、Service Discovery、通信/事件、Log/追蹤）與導入微服務的黑暗面與對策，可直接用於實戰教學、專案練習與評估。