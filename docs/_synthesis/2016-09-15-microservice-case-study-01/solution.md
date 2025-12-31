---
layout: synthesis
title: "微服務架構 #1, WHY Microservices?"
synthesis_type: solution
source_post: /2016/09/15/microservice-case-study-01/
redirect_from:
  - /2016/09/15/microservice-case-study-01/solution/
postid: 2016-09-15-microservice-case-study-01
---

以下內容依據文章中的關鍵脈絡（微服務 vs 單體式、容器化佈署、開發與維運觀點差異、Windows Container 與 .NET 場景）萃取出完整可教學的方案案例，並補足通用實作與設定示例，供實戰教學、專案練習與能力評估之用。實測數據部分為示意與可量化指標範本，便於落地時自訂與驗證。

## Case #1: 以容器化降低 SOA/微服務導入門檻

### Problem Statement（問題陳述）
- 業務場景：企業已累積大量 .NET 應用，想導入微服務以提升交付速度與彈性，但早期 SOA 在公司內口碑不佳，常被評為「部署麻煩、成本高」，小團隊承擔不起。現在希望利用 Windows Container 與現有 .NET 能力，先把既有 ASP.NET MVC 應用容器化，建立標準化可複製的部署流程。
- 技術挑戰：缺乏容器化經驗；Windows 容器映像選型；建置/發行流程未自動化；環境差異常導致「本機可跑、伺服器不行」。
- 影響範圍：上線頻率、交付風險、維運穩定度、環境成本與一致性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 以 VM/Server 為最小單位部署，啟動慢、佈署重。
  2. 缺少基於映像的標準化環境，環境漂移頻繁。
  3. 發布流程手工為主，出錯率高、可追溯性差。
- 深層原因：
  - 架構層面：單體式部署耦合所有模組，升級風險大。
  - 技術層面：缺乏容器映像/登錄庫/基底映像治理。
  - 流程層面：CI/CD 缺失，仍以人工為主。

### Solution Design（解決方案設計）
- 解決策略：先將 ASP.NET MVC 應用容器化，建立可重複、可遷移的映像與運行期設定；導入私有映像登錄庫與基本 CI 流程，確保同一映像橫跨開發/測試/正式一致運作，降低導入微服務的第一階段成本與風險。

- 實施步驟：
  1. 制作 Dockerfile（Windows Container）
     - 實作細節：選用 .NET Framework ASP.NET 4.8 Windows Server Core 基底映像；拷貝網站檔案；設定 IIS 站台。
     - 所需資源：Docker Desktop（Windows containers 模式）、mcr.microsoft.com 基底映像
     - 預估時間：0.5 天
  2. 本機建置與執行
     - 實作細節：docker build、docker run；以環境變數注入設定。
     - 所需資源：PowerShell、Docker CLI
     - 預估時間：0.5 天
  3. 建立私有映像庫與推送流程
     - 實作細節：規範標籤命名（app:version、env）；推送到 ACR/Harbor。
     - 所需資源：Azure Container Registry 或內部 Harbor
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```Dockerfile
# Windows Container for ASP.NET MVC (.NET Framework)
FROM mcr.microsoft.com/dotnet/framework/aspnet:4.8-windowsservercore-ltsc2019
SHELL ["powershell", "-Command"]

# 將網站發佈內容拷貝到 IIS 預設路徑
COPY . /inetpub/wwwroot

# 健康檢查（可選，需應用提供 /healthz）
HEALTHCHECK --interval=30s --timeout=5s --retries=3 `
 CMD powershell -command `
  try { `
    $resp = iwr http://localhost/healthz -UseBasicParsing; `
    if ($resp.StatusCode -eq 200) { exit 0 } else { exit 1 } `
  } catch { exit 1 }
```

- 實際案例：依文章情境，ASP.NET MVC 專案採用 Windows Container 展示。
- 實作環境：Windows 10/11 + Docker Desktop（Windows 容器）、.NET Framework 4.8、IIS。
- 實測數據（示意）：
  - 改善前：部署需 60-120 分鐘；部署失敗率 10-15%
  - 改善後：部署 10-15 分鐘；失敗率 <2%
  - 改善幅度：部署時間 -80% 以上；失敗率 -80% 以上

- Learning Points
  - 核心知識點：
    - Windows 容器基底映像選型（Server Core vs Nano Server）
    - 基於映像的環境一致性
    - 健康檢查的容器層設計
  - 技能要求：
    - 必備技能：Docker 基礎、IIS/ASP.NET 發佈
    - 進階技能：映像體積優化、私有登錄治理
  - 延伸思考：
    - 是否改用 .NET 6+ on Nano Server 降低映像體積？
    - 基底映像安全修補與再建置策略？
    - 如何與 CI/CD 串接版本管理？
- Practice Exercise
  - 基礎練習：將現有 ASP.NET MVC 專案容器化並本機啟動（30 分）
  - 進階練習：加入健康檢查與多環境設定（2 小時）
  - 專案練習：建置私有登錄庫並完成推送/拉取策略（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：容器可啟動並提供既有功能
  - 程式碼品質（30%）：Dockerfile 可讀、層次合理
  - 效能優化（20%）：映像大小與啟動時間優化
  - 創新性（10%）：健康檢查設計與診斷資訊豐富度

---

## Case #2: 單體式拆分：以領域邊界切出第一個微服務

### Problem Statement（問題陳述）
- 業務場景：既有 ASP.NET MVC 單體系統難以維護，任一小改都需重編整體與大規模回歸測試。希望先挑選「變更頻繁且獨立性高」的功能（例如使用者設定或通知）切出為第一個微服務，降低耦合、試運轉微服務模式。
- 技術挑戰：如何定義服務邊界、資料與介面契約；如何不影響現有用戶與功能；如何在最小風險下上線。
- 影響範圍：需求交付速度、回歸測試規模、可維護性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 編譯時期耦合過強，改動一處須重建全域。
  2. 整體部署，升級風險與回溯成本高。
  3. 資料與商業邏輯缺乏清晰邊界。
- 深層原因：
  - 架構層面：未以服務邊界來規劃系統。
  - 技術層面：僅有二進位/原始碼重用，缺少服務層抽象。
  - 流程層面：缺少契約先行（API First）與自動化測試。

### Solution Design（解決方案設計）
- 解決策略：採用領域劃分（DDD 的 Bounded Context 概念），從最易切分的功能開始，定義清晰的 REST API 契約與獨立資料存放。以 Gateway 或反向代理將原路由導向新服務，確保對外行為不變。

- 實施步驟：
  1. 識別候選服務與 API 契約
     - 實作細節：產出 OpenAPI；定義錯誤碼與版本策略。
     - 所需資源：Swagger/OpenAPI 工具
     - 預估時間：0.5-1 天
  2. 建立微服務骨架與資料儲存
     - 實作細節：ASP.NET Web API / .NET 6 Minimal API；獨立資料庫。
     - 所需資源：.NET SDK、資料庫
     - 預估時間：1-2 天
  3. 路由切換與灰度
     - 實作細節：以反向代理/Rewrite 將特定路由導向新服務，灰度驗證。
     - 所需資源：IIS ARR / YARP
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 範例：ASP.NET Core Minimal API for UserProfile service
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/api/v1/userprofiles/{id}", (string id) =>
{
    // TODO: 查詢資料庫
    return Results.Ok(new { id, displayName = "Demo", email = "demo@company.com" });
});

app.Run();
```

- 實作環境：.NET 6+、Windows Container（nanoserver-ltsc2022）
- 實測數據（示意）：
  - 改善前：修改與回歸需 3-5 天
  - 改善後：獨立服務修改 0.5-1 天；回歸侷限在服務域
  - 改善幅度：交付周期縮短 60-80%

- Learning Points
  - 核心知識點：Bounded Context、API First、資料邊界
  - 技能要求：.NET Web API、OpenAPI 定義
  - 延伸思考：資料同步與最終一致性、跨域交易處理
- Practice Exercise
  - 基礎：為一個「偏獨立」功能定義 OpenAPI（30 分）
  - 進階：建立 Minimal API 與資料層（2 小時）
  - 專案：完成代理路由切分與灰度（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：API 契約正確、覆蓋主要用例
  - 程式碼品質（30%）：分層清晰、測試完善
  - 效能優化（20%）：API 延遲低、資源使用合理
  - 創新性（10%）：契約管理與版本策略完整

---

## Case #3: 精準擴展：只擴服務熱點而非整體系統

### Problem Statement（問題陳述）
- 業務場景：單體式系統中登入、報表等熱點尖峰時造成全站壓力，過去只能擴整個應用，成本高且浪費。希望在微服務下只對高負載服務（如 AuthService）擴容，提升資源使用率與可用性。
- 技術挑戰：如何以容器為單位快速複製與擴張；如何實施無狀態化支援水平擴展；如何在 Windows 環境下用 Compose/Swarm 進行擴容。
- 影響範圍：成本、可用性、用戶體驗（延遲/錯誤率）。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單體式只能整體擴容，不能精準到模組。
  2. 狀態綁定（in-memory session）阻礙水平擴展。
  3. 缺乏服務分層監控，難定位熱點。
- 深層原因：
  - 架構層面：未切分服務，缺少彈性擴展單位。
  - 技術層面：未設計 stateless 與外部化狀態。
  - 流程層面：未建立服務級擴容策略（自動/手動）。

### Solution Design（解決方案設計）
- 解決策略：將熱點功能獨立為服務，移除 session 綁定（改 JWT/外部 session），以 Docker Compose 的 --scale 或 Swarm/K8s 副本調整，透過反向代理/服務發現平均分流。

- 實施步驟：
  1. 外部化狀態與無狀態化服務
     - 實作細節：移除 in-memory session；以 JWT 或分散式快取。
     - 所需資源：Redis/SQL/Token 服務
     - 預估時間：1 天
  2. 建立可水平擴展的映像與啟動腳本
     - 實作細節：容器內參數化設定（env）
     - 所需資源：Dockerfile、Compose
     - 預估時間：0.5 天
  3. 擴容與流量分配
     - 實作細節：docker-compose --scale；或 Swarm deploy replicas
     - 所需資源：Docker Engine/Swarm
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# docker-compose.yml（Windows Containers）
version: "3.8"
services:
  authsvc:
    image: myacr.azurecr.io/authsvc:1.0.0
    ports:
      - "5001:80"
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
    networks: [appnet]
networks:
  appnet:

# 擴容指令（例）
# docker-compose up -d --scale authsvc=3
```

- 實作環境：Windows Server 2019/2022 + Docker、.NET 6/Framework
- 實測數據（示意）：
  - 改善前：尖峰時 P95 延遲 1500ms，錯誤率 3%
  - 改善後：P95 400ms，錯誤率 0.5%
  - 改善幅度：延遲 -73%；錯誤率 -83%

- Learning Points
  - 核心知識點：Stateless 設計、橫向擴展、反向代理分流
  - 技能要求：Compose/Swarm 操作、Windows 容器網路
  - 延伸思考：自動擴縮（HPA）與容量門檻設定
- Practice Exercise
  - 基礎：用 Compose 將服務擴至三副本（30 分）
  - 進階：將 session 外部化並驗證擴展效果（2 小時）
  - 專案：為 2 個熱點服務建立擴縮手冊與指標（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：服務可擴容並穩定
  - 程式碼品質（30%）：設定外部化、無狀態
  - 效能優化（20%）：延遲、錯誤率明顯改善
  - 創新性（10%）：擴縮策略與自動化

---

## Case #4: 可觀測性起步：健康檢查與容器健康探針

### Problem Statement（問題陳述）
- 業務場景：過去維運只能重啟整個應用，無法針對部件做健康檢查與復原。導入微服務後希望每個服務都能自我回報健康狀態，讓維運可局部重啟或下線不健康實例。
- 技術挑戰：設計健康端點；容器層健康探針；與負載平衡器/反向代理整合；健康狀態分級（Ready/Live）。
- 影響範圍：MTTR、服務可用性、變更風險。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單體式缺少可組合監控；只能整體重啟。
  2. 無健康端點，無法自動隔離故障實例。
  3. 部署管線無健康驗證步驟。
- 深層原因：
  - 架構層面：缺乏服務自描述能力。
  - 技術層面：未實作健康端點/探針。
  - 流程層面：未將健康檢查納入發佈前後檢核。

### Solution Design（解決方案設計）
- 解決策略：每個服務提供 /healthz（Liveness）與 /readyz（Readiness），容器層以 HEALTHCHECK 整合，部署/代理側以健康狀態做流量調度與回滾判斷。

- 實施步驟：
  1. 新增健康端點
     - 實作細節：檢查依賴（DB、外部 API），分級輸出。
     - 所需資源：應用程式碼
     - 預估時間：0.5 天
  2. 容器 HEALTHCHECK
     - 實作細節：Dockerfile 加入健康檢查指令。
     - 所需資源：Dockerfile
     - 預估時間：0.5 天
  3. 代理整合
     - 實作細節：反向代理根據健康狀態下線實例。
     - 所需資源：IIS ARR/YARP
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// ASP.NET MVC/Web API 健康端點示例
public class HealthController : Controller {
    [HttpGet] [Route("healthz")]
    public ActionResult Health() => Content("OK"); // Liveness

    [HttpGet] [Route("readyz")]
    public ActionResult Ready() {
        // 檢查資料庫/快取等
        bool dbOk = true; // TODO: 實作
        return dbOk ? Content("READY") : new HttpStatusCodeResult(503, "NOT_READY");
    }
}
```

- 實作環境：ASP.NET MVC/Web API、Windows Container
- 實測數據（示意）：
  - 改善前：MTTR 60 分鐘
  - 改善後：MTTR 5-10 分鐘（自動隔離與重啟）
  - 改善幅度：-80% 以上

- Learning Points
  - 核心知識點：Liveness vs Readiness、探針與代理整合
  - 技能要求：控制器/中介層開發、Docker HEALTHCHECK
  - 延伸思考：健康端點安全與節流
- Practice Exercise
  - 基礎：新增基本 /healthz（30 分）
  - 進階：/readyz 檢查依賴（2 小時）
  - 專案：將健康檢查納入部署自動驗證（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：健康狀態能準確反映依賴
  - 程式碼品質（30%）：清楚、可測試
  - 效能優化（20%）：探針低負擔
  - 創新性（10%）：健康狀態儀表板

---

## Case #5: 零停機變更：藍綠與滾動升級（Windows 生態）

### Problem Statement（問題陳述）
- 業務場景：40 分鐘內需交代前後脈絡的場合常要求「不影響線上」地展示新版本。團隊希望透過藍綠或滾動升級，做到零停機布署與快速回滾。
- 技術挑戰：在 Windows 容器與 .NET 場景下建立反向代理（例如 YARP）分流能力；以健康檢查與權重控制流量；實作快速回滾。
- 影響範圍：SLA、變更風險、用戶體驗。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單體式需整站重啟造成停機。
  2. 無流量切換層與健康驗證。
  3. 回滾需重佈，耗時且風險高。
- 深層原因：
  - 架構層面：缺少流量治理層（Gateway/Proxy）。
  - 技術層面：未建立版本並存部署模型。
  - 流程層面：缺少發布前後自動驗證與回滾策略。

### Solution Design（解決方案設計）
- 解決策略：引入 .NET 反向代理（YARP）容器作為 Gateway，並行部署 v1/v2 服務，以權重/標頭引導流量；配合健康檢查與自動回退。

- 實施步驟：
  1. 建立 Gateway（YARP）
     - 實作細節：設定路由/叢集目標；啟用健康檢查。
     - 所需資源：YARP、.NET 6
     - 預估時間：1 天
  2. 版本並存與灰度
     - 實作細節：v1/v2 同時上線，調整權重。
     - 所需資源：Docker Compose
     - 預估時間：0.5 天
  3. 自動回滾
     - 實作細節：監控錯誤率/延遲，超閾值回退。
     - 所需資源：監控/腳本
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
// YARP appsettings.json（簡化）
{
  "ReverseProxy": {
    "Routes": {
      "api": { "ClusterId": "apiCluster", "Match": { "Path": "/api/{**catchall}" } }
    },
    "Clusters": {
      "apiCluster": {
        "Destinations": {
          "v1": { "Address": "http://apisvc-v1:80/" },
          "v2": { "Address": "http://apisvc-v2:80/" }
        },
        "HealthCheck": { "Active": { "Enabled": true, "Interval": "00:00:10", "Path": "/healthz" } }
      }
    }
  }
}
```

- 實作環境：.NET 6 + YARP（Windows Container）
- 實測數據（示意）：
  - 改善前：部署需停機 15 分鐘
  - 改善後：零停機；回滾 < 2 分鐘
  - 改善幅度：停機時間 -100%；回滾時間 -85% 以上

- Learning Points
  - 核心知識點：藍綠/滾動、權重路由、健康檢查
  - 技能要求：反向代理設定、容器網路
  - 延伸思考：Header/Cookie 定向灰度、金絲雀發布
- Practice Exercise
  - 基礎：以 YARP 導流至單一服務（30 分）
  - 進階：並行 v1/v2，調整權重（2 小時）
  - 專案：自動化回滾腳本與監控閾值（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：無中斷切換
  - 程式碼品質（30%）：設定清晰可維護
  - 效能優化（20%）：切換延遲最小
  - 創新性（10%）：灰度策略豐富

---

## Case #6: 異質技術共存：以 API 契約達到語言/框架解耦

### Problem Statement（問題陳述）
- 業務場景：微服務允許不同語言/平台開發（文章指明語言/平台差異不重要），團隊希望以 .NET 與其他語言（如 Node.js）協作，在運行期透過 API 溝通。
- 技術挑戰：契約定義、錯誤與安全一致性、跨語言資料格式與相容性測試。
- 影響範圍：跨團隊協作效率、上線風險、可替換性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 編譯期耦合使得跨語言重用困難。
  2. 缺乏清晰 API 契約導致對接摩擦。
  3. 錯誤/安全處理不一致。
- 深層原因：
  - 架構層面：未採用契約先行（API First）。
  - 技術層面：缺少 OpenAPI/Schema 管理。
  - 流程層面：未建立契約測試與破壞性變更治理。

### Solution Design（解決方案設計）
- 解決策略：使用 OpenAPI 定義契約、錯誤碼與安全需求（Bearer/JWT），在各服務語言分別實作並以契約測試驗證；版本化管理避免破壞性變更。

- 實施步驟：
  1. 定義 OpenAPI 與錯誤模型
     - 實作細節：描述 request/response、錯誤碼、securitySchemes。
     - 所需資源：Swagger Editor
     - 預估時間：0.5 天
  2. 產生/對接 Client SDK（可選）
     - 實作細節：根據契約生成或手寫 client。
     - 所需資源：OpenAPI Generator
     - 預估時間：0.5 天
  3. 契約測試
     - 實作細節：用 Postman/Newman 或 Pact 驗證。
     - 所需資源：測試工具
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# OpenAPI 片段（users API）
openapi: 3.0.3
paths:
  /api/v1/users/{id}:
    get:
      security: [{ bearerAuth: [] }]
      responses:
        '200': { description: OK }
        '404': { description: Not Found }
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

- 實作環境：.NET 6 Web API、Node.js/其他語言服務
- 實測數據（示意）：
  - 改善前：跨團隊對接 3-5 天反覆
  - 改善後：以契約為中心 1-2 天完成
  - 改善幅度：對接周期 -50% 以上

- Learning Points
  - 核心知識點：API First、OpenAPI、契約測試
  - 技能要求：Swagger 生態、跨語言資料格式
  - 延伸思考：gRPC vs REST、Schema Registry
- Practice Exercise
  - 基礎：為一個 API 建立 OpenAPI（30 分）
  - 進階：生成 Client 並調用（2 小時）
  - 專案：建立契約測試管線（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：契約覆蓋完整
  - 程式碼品質（30%）：錯誤/安全一致
  - 效能優化（20%）：序列化/延遲可控
  - 創新性（10%）：契約治理與審核流程

---

## Case #7: DevOps 自動化：建置與發佈 Windows 容器映像

### Problem Statement（問題陳述）
- 業務場景：容器化後仍以手動建置/推送映像，常錯用標籤或遺漏步驟。需要建立 CI/CD，自動建置、測試、推送到 ACR/Harbor，再部署到測試/正式。
- 技術挑戰：Windows 代理節點配置；Docker Buildx/標籤規範；敏感資訊管理。
- 影響範圍：交付速度、可追溯性、錯誤率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 手動流程易錯且不可複製。
  2. 無版本與標籤規範。
  3. 憑證/金鑰裸露風險。
- 深層原因：
  - 架構層面：無標準化管線。
  - 技術層面：缺乏容器建置最佳實踐。
  - 流程層面：未定義發佈門檻與核可。

### Solution Design（解決方案設計）
- 解決策略：以 Azure DevOps/GitHub Actions 建立 Windows Agent 的 CI，標準化版號與標籤（semver + git sha），安全推送至私有登錄，之後觸發部署。

- 實施步驟：
  1. 建立 CI Pipeline
     - 實作細節：拉原始碼、還原、測試、docker build。
     - 所需資源：Azure DevOps/GitHub Actions
     - 預估時間：1 天
  2. 登錄與推送
     - 實作細節：安全變數存放登入資訊。
     - 所需資源：ACR/Harbor
     - 預估時間：0.5 天
  3. 版本與標籤規範
     - 實作細節：latest + 1.2.3 + gitsha 三重標籤。
     - 所需資源：腳本
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# azure-pipelines.yml（精簡）
trigger:
- main
pool:
  vmImage: 'windows-2022'
steps:
- task: PowerShell@2
  inputs:
    targetType: 'inline'
    script: |
      docker build -t $(ACR_LOGIN_SERVER)/web:$(Build.BuildNumber) .
      docker login $(ACR_LOGIN_SERVER) -u $(ACR_USER) -p $(ACR_PWD)
      docker push $(ACR_LOGIN_SERVER)/web:$(Build.BuildNumber)
```

- 實作環境：Azure DevOps/GitHub Actions（Windows Agent）、ACR
- 實測數據（示意）：
  - 改善前：手動建置 30-60 分鐘；錯推/漏推每月 2-3 次
  - 改善後：自動建置 < 10 分；錯誤趨近 0
  - 改善幅度：建置時間 -70% 以上；錯誤率 -90% 以上

- Learning Points
  - 核心知識點：CI 版號與映像標籤策略
  - 技能要求：YAML Pipeline、敏感資訊管理
  - 延伸思考：佈署到測試/正式的自動化與審批
- Practice Exercise
  - 基礎：建置並推送映像到 ACR（30 分）
  - 進階：加入單元測試與質量門檻（2 小時）
  - 專案：打通 CI→CD 全流程（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：映像可用且可追溯
  - 程式碼品質（30%）：管線易讀、變數安全
  - 效能優化（20%）：建置時間與快取運用
  - 創新性（10%）：多標籤/多架構策略

---

## Case #8: 小團隊成本壓力：以容器提升佈署密度與效率

### Problem Statement（問題陳述）
- 業務場景：文章指出部署成本由 Server→VM→Container 不斷下降。小團隊需在有限硬體上運行多個環境（Dev/Test/UAT），希望以容器提升密度、降低費用。
- 技術挑戰：資源配額與爭用控制；容器密度與穩定度的平衡；監控與警示。
- 影響範圍：硬體成本、運維效率、風險控制。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 以 VM 為最小單位導致浪費。
  2. 應用無資源限制，互相干擾。
  3. 缺乏密度監控指標。
- 深層原因：
  - 架構層面：缺少容器化與共享主機策略。
  - 技術層面：未設配額/限制。
  - 流程層面：無容量/密度規劃。

### Solution Design（解決方案設計）
- 解決策略：將多個應用容器化，設定 CPU/Memory 限制與保留，集中部署於少量主機；定義容量目標（CPU/Memory 使用率）與警戒線，逐步提高密度。

- 實施步驟：
  1. 容器化與資源估算
     - 實作細節：量測平/尖峰資源用量。
     - 所需資源：監控工具
     - 預估時間：1 天
  2. 配額與限制設定
     - 實作細節：docker run/compose 設定 cpus/mem_limit。
     - 所需資源：Docker
     - 預估時間：0.5 天
  3. 密度監測與調整
     - 實作細節：持續監測，滾動調整限制。
     - 所需資源：監控與告警
     - 預估時間：持續性

- 關鍵程式碼/設定：
```yaml
# docker-compose（資源限制）
services:
  web:
    image: myacr/web:1.0.0
    mem_limit: 512m
    cpus: "1.0"
```

- 實作環境：Windows 主機 + Docker、監控/告警
- 實測數據（示意）：
  - 改善前：3 台 VM 支撐 3 環境
  - 改善後：1 台實體/大 VM + 多容器支撐 3 環境
  - 改善幅度：基礎設施成本 -50~70%

- Learning Points
  - 核心知識點：資源配額、密度與穩定度的平衡
  - 技能要求：Compose 限制、監控告警
  - 延伸思考：不同服務等級的資源策略
- Practice Exercise
  - 基礎：為 2 個服務設置 mem/cpu 限制（30 分）
  - 進階：以壓測調整限制（2 小時）
  - 專案：制定容量與密度治理準則（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：限制生效且穩定
  - 程式碼品質（30%）：設定清楚可維護
  - 效能優化（20%）：密度提升但不犧牲穩定
  - 創新性（10%）：自動化調參

---

## Case #9: API 版本管理：避免破壞性升級

### Problem Statement（問題陳述）
- 業務場景：服務常演進，若直接修改現有 API 會破壞舊客戶端。需提供平滑版本策略，並行支援 v1/v2，逐步淘汰舊版。
- 技術挑戰：版本路由、相容性測試、文件同步與去舊。
- 影響範圍：合作方穩定性、上線風險。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 直接更動介面造成破壞性變更。
  2. 無版本策略與文件。
  3. 缺乏去舊機制。
- 深層原因：
  - 架構層面：未納入版本治理。
  - 技術層面：路由與相容策略缺失。
  - 流程層面：缺少去舊公告與期限管理。

### Solution Design（解決方案設計）
- 解決策略：採用 URL/標頭版本化（/api/v1/...），同時提供 v1 與 v2；以 API 版本管理套件與文件告知；設去舊時間表。

- 實施步驟：
  1. 加入版本管理套件（.NET）
     - 實作細節：Microsoft.AspNetCore.Mvc.Versioning
     - 所需資源：NuGet
     - 預估時間：0.5 天
  2. 路由與文件
     - 實作細節：v1/v2 路由與 Swagger Doc。
     - 所需資源：Swashbuckle
     - 預估時間：0.5 天
  3. 去舊策略
     - 實作細節：公告時間表與監測使用比例。
     - 所需資源：分析日誌
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
builder.Services.AddApiVersioning(o => {
  o.AssumeDefaultVersionWhenUnspecified = true;
  o.DefaultApiVersion = new ApiVersion(1,0);
  o.ReportApiVersions = true;
});
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/users")]
public class UsersV1Controller : ControllerBase { /* ... */ }
```

- 實作環境：.NET 6 Web API、Windows Container
- 實測數據（示意）：
  - 改善前：升級頻繁造成客戶端故障
  - 改善後：版本並存，故障率顯著下降
  - 改善幅度：升級引起的故障 -80% 以上

- Learning Points
  - 核心知識點：版本策略、契約相容性
  - 技能要求：API Versioning 套件、Swagger 多文件
  - 延伸思考：Header/Media Type 版本化
- Practice Exercise
  - 基礎：新增 v2 並保留 v1（30 分）
  - 進階：建立多版本 Swagger（2 小時）
  - 專案：制定去舊流程與監測儀表（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：兩版同時可用
  - 程式碼品質（30%）：路由清楚、測試覆蓋
  - 效能優化（20%）：文件與治理自動化
  - 創新性（10%）：去舊暖流策略

---

## Case #10: 每服務資料庫：避免共享資料庫耦合

### Problem Statement（問題陳述）
- 業務場景：單體式常用單庫，導致跨模組強耦合。微服務需每服務自有資料存放，以提升自治與可替換性。
- 技術挑戰：連線字串管理、交易邊界、報表整合。
- 影響範圍：資料一致性、開發獨立性、維運風險。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 共享資料庫耦合所有服務。
  2. 任一變更影響全域。
  3. 權限與安全邊界模糊。
- 深層原因：
  - 架構層面：資料未與服務邊界一致。
  - 技術層面：連線設定/密鑰管理缺失。
  - 流程層面：跨域報表與 ETL 無規劃。

### Solution Design（解決方案設計）
- 解決策略：每服務擁有資料庫，以環境變數注入連線設定；報表以 ETL 或 API 組合；避免跨服務直接共享資料表。

- 實施步驟：
  1. 拆分資料域與連線設定
     - 實作細節：為每服務建立獨立 schema/db。
     - 所需資源：SQL Server
     - 預估時間：1-2 天
  2. 配置注入與密鑰管理
     - 實作細節：env/secrets 注入 connection string。
     - 所需資源：Compose/Key Vault
     - 預估時間：0.5 天
  3. 報表/整合路徑設計
     - 實作細節：建立只讀視圖/ETL。
     - 所需資源：ETL 工具
     - 預估時間：1 天

- 關鍵程式碼/設定：
```yaml
services:
  usersvc:
    image: myacr/usersvc:1.0.0
    environment:
      - ConnectionStrings__Default=Server=sql1;Database=UserDb;User Id=app;Password=***;
    depends_on: [sql1]
  sql1:
    image: mcr.microsoft.com/mssql/server/windows/servercore:ltsc2019
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=YourStrong!Passw0rd
```

- 實作環境：Windows 容器（SQL Server/應用皆可）、.NET 6/Framework
- 實測數據（示意）：
  - 改善前：每次資料庫改動需全域回歸
  - 改善後：服務內部自主管控，影響面縮小
  - 改善幅度：回歸範圍 -50% 以上；事故半徑顯著縮小

- Learning Points
  - 核心知識點：資料邊界、連線設定注入
  - 技能要求：SQL Server/Schema 設計、Secrets 管理
  - 延伸思考：最終一致性、跨服務查詢策略
- Practice Exercise
  - 基礎：將連線字串外部化（30 分）
  - 進階：建立報表只讀視圖（2 小時）
  - 專案：為 2 個服務拆出獨立資料庫（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：服務可獨立運作
  - 程式碼品質（30%）：設定安全、可維運
  - 效能優化（20%）：查詢效能/索引
  - 創新性（10%）：報表整合方式

---

## Case #11: 服務發現與組態：用 Docker DNS 簡化連線

### Problem Statement（問題陳述）
- 業務場景：微服務數量很多，手動維護 IP/端口易錯。希望在同一 Compose/網路中，以服務名直接互連，簡化配置與部署。
- 技術挑戰：Windows 容器網路、DNS 解析、組態注入。
- 影響範圍：部署可靠性、維護成本。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 以硬編碼 IP 連線導致頻繁出錯。
  2. 每環境端口/位址不同。
  3. 缺乏統一組態策略。
- 深層原因：
  - 架構層面：未善用容器網路與 DNS。
  - 技術層面：配置未環境化。
  - 流程層面：未定義組態中心/層級。

### Solution Design（解決方案設計）
- 解決策略：在同一自訂網路下使用 Docker 內建 DNS，以服務名當主機名；所有連線透過環境變數注入，避免硬編碼。

- 實施步驟：
  1. 建立自訂網路
     - 實作細節：Compose networks 配置。
     - 所需資源：docker-compose.yml
     - 預估時間：0.5 天
  2. 服務名解析
     - 實作細節：以服務名互連（http://usersvc）
     - 所需資源：容器 DNS
     - 預估時間：0.5 天
  3. 組態注入
     - 實作細節：環境變數/Secret
     - 所需資源：Compose
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```yaml
version: "3.9"
networks: { appnet: {} }
services:
  apigw:
    image: myacr/gw:1.0
    networks: [appnet]
  usersvc:
    image: myacr/usersvc:1.0
    networks: [appnet]
# apigw 內可直呼 http://usersvc:80
```

- 實作環境：Windows 容器 + Docker 網路
- 實測數據（示意）：
  - 改善前：配置錯誤每次上線 2-3 起
  - 改善後：幾乎消失
  - 改善幅度：配置錯誤 -90% 以上

- Learning Points
  - 核心知識點：容器網路、DNS、組態注入
  - 技能要求：Compose 網路、環境變數
  - 延伸思考：跨主機服務發現（Consul/Eureka/DNS SRV）
- Practice Exercise
  - 基礎：以服務名互連（30 分）
  - 進階：抽離組態到 env file（2 小時）
  - 專案：加入組態中心（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：互連成功且穩定
  - 程式碼品質（30%）：無硬編碼
  - 效能優化（20%）：DNS 快取/重試
  - 創新性（10%）：多環境組態策略

---

## Case #12: 無狀態驗證：微服務間以 JWT 傳遞身分

### Problem Statement（問題陳述）
- 業務場景：圖片顯示「stateless authentication for microservices」議題。希望移除伺服器端 Session，改以 JWT 在微服務間傳遞使用者身分，提升擴展性與跨語言互通。
- 技術挑戰：票證簽發與驗證、安全與效期管理、金鑰輪替。
- 影響範圍：擴展性、安全性、使用者體驗。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. in-memory session 綁定節點，阻礙水平擴展。
  2. 跨服務共享 Session 困難。
  3. 多語言服務無法共享狀態。
- 深層原因：
  - 架構層面：缺少跨服務身分標準。
  - 技術層面：未實作 JWT/OIDC。
  - 流程層面：金鑰管理與輪替缺失。

### Solution Design（解決方案設計）
- 解決策略：引入 JWT（或 OIDC）作為通用身分憑證，簽發服務簽名，服務端以中介層驗證與解析 Claims；設定過期與刷新策略，逐步移除 Session 依賴。

- 實施步驟：
  1. JWT 簽發服務與金鑰管理
     - 實作細節：HMAC/RSA 簽名；金鑰安全存放。
     - 所需資源：Key Vault/機密管理
     - 預估時間：1 天
  2. 服務端驗證與授權
     - 實作細節：中介層驗證 Bearer Token。
     - 所需資源：.NET JWT 套件
     - 預估時間：0.5 天
  3. 漸進去 Session
     - 實作細節：混合期支援 Session & JWT。
     - 所需資源：程式碼調整
     - 預估時間：1-2 天

- 關鍵程式碼/設定：
```csharp
// 生成 JWT（簽發端）
var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes("super-secret-key"));
var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
var token = new JwtSecurityToken(issuer:"issuer", audience:"aud", claims: claims,
    expires: DateTime.UtcNow.AddMinutes(30), signingCredentials: creds);
var jwt = new JwtSecurityTokenHandler().WriteToken(token);

// 驗證 JWT（服務端 Program.cs）
builder.Services.AddAuthentication("Bearer")
 .AddJwtBearer("Bearer", o => {
   o.TokenValidationParameters = new TokenValidationParameters {
     ValidateIssuer = true, ValidIssuer = "issuer",
     ValidateAudience = true, ValidAudience = "aud",
     IssuerSigningKey = key
   };
 });
```

- 實作環境：.NET 6、Windows Container
- 實測數據（示意）：
  - 改善前：擴容需黏著 Session，流量不均
  - 改善後：可自由擴縮，多實例平均分流
  - 改善幅度：擴展瓶頸解除，P95 延遲下降 30-50%

- Learning Points
  - 核心知識點：JWT 基礎、金鑰輪替、Claims 設計
  - 技能要求：.NET Authentication/Authorization
  - 延伸思考：OIDC、Token 交換/委派
- Practice Exercise
  - 基礎：簽發與驗證簡單 Token（30 分）
  - 進階：加上角色/範圍授權（2 小時）
  - 專案：移除傳統 Session 改 JWT（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：登入與授權可用
  - 程式碼品質（30%）：安全、結構清晰
  - 效能優化（20%）：延遲/擴展性提升
  - 創新性（10%）：刷新/撤銷策略

---

## Case #13: 分散式診斷：Correlation ID 與結構化日誌

### Problem Statement（問題陳述）
- 業務場景：微服務後請求跨多服務，很難追查問題。需導入 Correlation ID 與結構化日誌，維運能以單一 ID 貫穿所有服務呼叫。
- 技術挑戰：ID 產生與傳遞、日誌格式統一、跨語言一致性。
- 影響範圍：故障排查時間、跨團隊協作效率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺少請求貫通標識。
  2. 非結構化日誌難以檢索。
  3. 無集中化彙整。
- 深層原因：
  - 架構層面：未定義可觀測性標準。
  - 技術層面：中介層未實作 ID 傳播。
  - 流程層面：缺少日誌治理與留存策略。

### Solution Design（解決方案設計）
- 解決策略：在入口產生或取得 X-Correlation-ID，於所有出站請求傳遞；統一結構化日誌格式（JSON），集中於 ELK/Seq 等平台檢索。

- 實施步驟：
  1. 中介層實作 ID 生成與傳播
     - 實作細節：若無則生成；寫入 Response。
     - 所需資源：.NET 中介層
     - 預估時間：0.5 天
  2. 結構化日誌
     - 實作細節：Serilog JSON 格式。
     - 所需資源：Serilog
     - 預估時間：0.5 天
  3. 集中化收集
     - 實作細節：收集到 ELK/Seq。
     - 所需資源：日誌平台
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
app.Use(async (ctx, next) => {
  var cid = ctx.Request.Headers["X-Correlation-ID"].FirstOrDefault()
            ?? Guid.NewGuid().ToString("N");
  ctx.Response.Headers["X-Correlation-ID"] = cid;
  using (LogContext.PushProperty("CorrelationId", cid))
    await next();
});
// 出站 HttpClient 傳遞
httpClient.DefaultRequestHeaders.Add("X-Correlation-ID", cid);
```

- 實作環境：.NET 6、Serilog、Windows Container
- 實測數據（示意）：
  - 改善前：跨服務問題定位需 2-4 小時
  - 改善後：以 ID 快速聚合檢索，15-30 分鐘
  - 改善幅度：排障時間 -70% 以上

- Learning Points
  - 核心知識點：ID 傳播、結構化日誌、集中化
  - 技能要求：中介層、Serilog、ELK/Seq
  - 延伸思考：W3C TraceContext、OpenTelemetry
- Practice Exercise
  - 基礎：加入 ID 中介層（30 分）
  - 進階：整合 Serilog JSON（2 小時）
  - 專案：集中化查詢面板（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：ID 貫穿完整
  - 程式碼品質（30%）：中介層清晰、低侵入
  - 效能優化（20%）：日誌量/成本控制
  - 創新性（10%）：Trace/Span 擴展

---

## Case #14: 本機多服務開發：用 Docker Compose 一鍵啟動

### Problem Statement（問題陳述）
- 業務場景：演講時間有限，需要流暢展示多服務協作。開發者也需要快速在本機還原多服務依賴。希望以 Compose 一鍵啟動 Web、API、DB。
- 技術挑戰：Windows 容器間網路、資料初始化、調試體驗。
- 影響範圍：開發效率、演示體驗、入門門檻。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 本機手動啟多服務耗時。
  2. 依賴服務安裝複雜。
  3. 環境不一致。
- 深層原因：
  - 架構層面：未容器化開發依賴。
  - 技術層面：缺少 Compose 描述。
  - 流程層面：無啟動/關閉腳本。

### Solution Design（解決方案設計）
- 解決策略：以 docker-compose 定義所有服務、網路與環境變數；配合初始化腳本；讓開發者以單一指令 up/down 還原場景。

- 實施步驟：
  1. 定義 Compose
     - 實作細節：web/api/db 服務、相依、網路。
     - 所需資源：docker-compose.yml
     - 預估時間：0.5 天
  2. 初始化資料
     - 實作細節：db 啟動腳本/種子資料。
     - 所需資源：SQL 腳本
     - 預估時間：0.5 天
  3. 調試與熱更新（可選）
     - 實作細節：volume 映射/遠端調試。
     - 所需資源：VS/VS Code
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```yaml
version: "3.8"
services:
  web:
    image: myacr/web:1.0
    ports: ["8080:80"]
    depends_on: [api]
  api:
    image: myacr/api:1.0
    ports: ["5000:80"]
    environment: ["ConnectionStrings__Default=Server=db;Database=App;User Id=sa;Password=***;"]
    depends_on: [db]
  db:
    image: mcr.microsoft.com/mssql/server/windows/servercore:ltsc2019
    environment: ["ACCEPT_EULA=Y","SA_PASSWORD=YourStrong!Passw0rd"]
```

- 實作環境：Windows 容器、Docker Desktop
- 實測數據（示意）：
  - 改善前：本機準備環境 1-2 天
  - 改善後：10-20 分鐘可還原
  - 改善幅度：環境準備時間 -90% 以上

- Learning Points
  - 核心知識點：Compose 基礎、相依與網路
  - 技能要求：YAML、初始化腳本
  - 延伸思考：Dev Container 與 Codespaces
- Practice Exercise
  - 基礎：在本機 up 下三服務（30 分）
  - 進階：加入初始化腳本（2 小時）
  - 專案：建立一鍵啟停/清理腳本（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：一鍵還原成功
  - 程式碼品質（30%）：Compose 可維護
  - 效能優化（20%）：啟動時間/資源
  - 創新性（10%）：開發者體驗提升

---

## Case #15: 漸進式改造：IIS URL Rewrite + ARR 實作 Strangler 模式

### Problem Statement（問題陳述）
- 業務場景：既有 ASP.NET WebForm/ MVC 單體系統龐大，不可能一次重寫。希望以 Strangler 模式逐步把部分路由代理到新微服務，對外 URL 與使用體驗不變。
- 技術挑戰：IIS 反向代理配置（需 ARR）、Rewrite 規則、健康檢查與回退。
- 影響範圍：穩定性、改造速度、風險控制。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 大改動風險高、周期長。
  2. 用戶不能接受大幅變更與停機。
  3. 無法一次性替換所有功能。
- 深層原因：
  - 架構層面：缺乏流量路由層。
  - 技術層面：未建立代理與健康驗證。
  - 流程層面：無灰度與回滾方案。

### Solution Design（解決方案設計）
- 解決策略：在 IIS 啟用 ARR，使用 URL Rewrite 將 /api/users 等路徑代理到新服務容器，並保留健康檢查與回退規則，逐步擴大代理範圍。

- 實施步驟：
  1. 安裝與啟用 ARR/Rewrite
     - 實作細節：IIS 外掛；啟用 Proxy。
     - 所需資源：IIS 管理工具
     - 預估時間：0.5 天
  2. 代理規則
     - 實作細節：針對特定路徑代理至 http://usersvc。
     - 所需資源：web.config
     - 預估時間：0.5 天
  3. 灰度與回退
     - 實作細節：健康檢查失敗則回到本地處理/頁面。
     - 所需資源：Rewrite 條件
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```xml
<configuration>
  <system.webServer>
    <rewrite>
      <rules>
        <rule name="Users API proxy" stopProcessing="true">
          <match url="^api/users(.*)$" />
          <action type="Rewrite" url="http://usersvc:80/api/users{R:1}" />
        </rule>
      </rules>
    </rewrite>
    <proxy enabled="true" />
  </system.webServer>
</configuration>
```

- 實作環境：IIS + ARR + URL Rewrite、Windows 容器（新服務）
- 實測數據（示意）：
  - 改善前：大改需 3-6 個月且高風險
  - 改善後：逐路徑導入，2-4 週可穩定上線一批
  - 改善幅度：風險/周期顯著降低（-50% 以上）

- Learning Points
  - 核心知識點：Strangler 模式、反向代理、Rewrite
  - 技能要求：IIS/ARR 配置、路由規則
  - 延伸思考：遷移過程的資料一致性
- Practice Exercise
  - 基礎：配置單一路徑代理（30 分）
  - 進階：加入健康檢查與回退（2 小時）
  - 專案：完成 3 條路徑遷移計畫（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：對外行為不變
  - 程式碼品質（30%）：規則清晰、可維護
  - 效能優化（20%）：代理延遲可控
  - 創新性（10%）：灰度策略與報表

---

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #1 容器化入門
  - Case #4 健康檢查
  - Case #11 服務發現與組態
  - Case #14 本機 Compose 啟動
- 中級（需要一定基礎）
  - Case #2 單體拆分
  - Case #3 精準擴展
  - Case #5 藍綠/滾動升級
  - Case #6 API 契約與異質共存
  - Case #7 DevOps 自動化
  - Case #8 佈署密度與成本
  - Case #9 API 版本管理
  - Case #10 每服務資料庫
  - Case #13 分散式診斷
  - Case #15 Strangler 模式
- 高級（需要深厚經驗）
  - （可延伸：跨資料中心部署、事件驅動一致性、全鏈路追蹤/Service Mesh — 本篇未展開）

2) 按技術領域分類
- 架構設計類：#2 #3 #5 #8 #9 #10 #15
- 效能優化類：#3 #8 #12
- 整合開發類：#1 #6 #7 #11 #14
- 除錯診斷類：#4 #13
- 安全防護類：#12

3) 按學習目標分類
- 概念理解型：#1 #2 #3 #8
- 技能練習型：#4 #7 #11 #14
- 問題解決型：#5 #9 #10 #13 #15
- 創新應用型：#6 #12

案例關聯圖（學習路徑建議）
- 先學（基礎環境與概念）：
  1) Case #1 容器化入門 → 2) Case #14 本機 Compose → 3) Case #11 服務發現與組態 → 4) Case #4 健康檢查
- 中段（服務化與交付能力）：
  5) Case #2 單體拆分 → 6) Case #10 每服務資料庫 → 7) Case #6 API 契約 → 8) Case #9 API 版本管理 → 9) Case #7 DevOps 自動化
- 進階（可靠性與擴展）：
  10) Case #12 無狀態驗證（JWT） → 11) Case #3 精準擴展 → 12) Case #5 藍綠/滾動升級 → 13) Case #13 分散式診斷
- 遷移策略收斂：
  14) Case #15 Strangler 模式 → 持續循環擴展與去舊
- 依賴關係提示：
  - #2 依賴 #1/#14（先能啟動與運行）
  - #3 依賴 #12（無狀態化）與 #4（健康）
  - #5 依賴 #4/#7（健康與自動化）
  - #10 依賴 #2（邊界清晰再拆庫）
  - #13 依賴 #6（契約）與 #7（管線整合）

說明
- 上述案例均緊扣原文脈絡：微服務 vs 單體式、Windows Container、.NET 團隊導入、維運可觀測性與彈性、部署成本與流程影響。
- 實測數據為示意與可量化指標模板，落地時請以實際壓測與監控數據替換，作為能力驗證與持續改進依據。