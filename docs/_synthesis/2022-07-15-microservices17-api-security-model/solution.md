---
layout: synthesis
title: "微服務架構 - API 的安全管控模型"
synthesis_type: solution
source_post: /2022/07/15/microservices17-api-security-model/
redirect_from:
  - /2022/07/15/microservices17-api-security-model/solution/
postid: 2022-07-15-microservices17-api-security-model
---

以下內容基於原文脈絡，提取並結構化為 15 個可落地的問題解決案例。每個案例均包含：問題、根因、可操作方案與範例程式碼、學習要點、練習與評估。原文未提供具體效益數據；各案例提供建議的可量測指標與目標值，供實作後自行量測。

## Case #1: 把安全機制變設計題：建立統一的 API 安全模型

### Problem Statement（問題陳述）
業務場景：組織自單體轉向微服務，多個團隊同時開放與消費 API，內外部合作方亦透過 API 整合。需求方包含產品、研發、客服與客戶 IT，授權需求涵蓋功能、資料與指令三層。過往由基礎設施控管的思維已不足，安全須在設計階段被明確定義並可落地執行。

技術挑戰：缺乏統一模型描述「控什麼、控誰、誰管理、在哪一層判斷」，導致各系統各行其是，無法共用工具與策略。

影響範圍：授權不一致、漏洞難以發現、跨團隊協作成本高、上線風險與合規壓力上升。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 無一致的授權語彙與物件模型：各團隊自行定義 scope/role，無法互通。
2. 只靠基礎設施或單點框架：無法涵蓋業務規則、租戶、委任等複雜情境。
3. 缺乏決策點設計：未明確規範在 Gateway 還是 App 內做哪種授權。

深層原因：
- 架構層面：沒有中心化的「安全模型與政策即資料」的架構基座。
- 技術層面：技術選型未以模型為先，導致平台與框架難以替換或共存。
- 流程層面：安全未納入需求與設計審查，缺少跨角色責任分工。

### Solution Design（解決方案設計）
解決策略：先定義統一的 API 安全模型（資源、操作、主體、條件、限制、決策點），形成政策 Schema 與治理流程，再映射到工具（JWT/OAuth2/APIM/YARP/中介軟體）。以「政策即資料」方式集中管理，執行在 Gateway 與 App 的明確分工。

實施步驟：
1. 建模工作坊
- 實作細節：盤點資源分類（功能/資料/指令）、主體分類（內部/外部/委任）、條件（租戶/IP/時間/配額）、決策點（Gateway/App）。
- 所需資源：架構師/PO/RD/Sec 共工會議
- 預估時間：1-2 週

2. 政策 Schema 與政策存放
- 實作細節：定義 JSON Schema，建立政策儲存（DB/Git），制定版本與審核流程。
- 所需資源：DB/Git、審核工作流
- 預估時間：1-2 週

3. 參考實作與樣板
- 實作細節：提供 Gateway Policy、App 授權 Handler、測試樣板，落地 1-2 條關鍵 API 作為藍本。
- 所需資源：ASP.NET Core、APIM/YARP、示例專案
- 預估時間：2-3 週

關鍵程式碼/設定：
```json
// Policy as Data（片段）：統一授權模型
{
  "resource": "Member",
  "operations": [
    { "op": "Read", "method": "GET", "path": "/members/{id}" },
    { "op": "List", "method": "GET", "path": "/members" },
    { "op": "Activate", "method": "POST", "path": "/members/{id}/activate" },
    { "op": "Delete", "method": "DELETE", "path": "/members/{id}" }
  ],
  "subjects": [
    { "type": "Service", "id": "svc.billing" },
    { "type": "Partner", "id": "vendor.x" },
    { "type": "User", "role": "Admin" }
  ],
  "conditions": {
    "tenant": "claim:tenantId == route:tenantId",
    "owner": "claim:userId == route:id",
    "ip": "in( clientIp, allowlist )",
    "time": "within(09:00-18:00)"
  },
  "limits": { "rpm": 120, "burst": 20 },
  "decisionPoints": { "gateway": ["ip","limits"], "app": ["tenant","owner","state"] }
}
```

實際案例：以 MemberService 為範例，為各方法建立資源與操作映射，並將租戶、擁有者與狀態檢查分別分配在 Gateway 與 App 層。

實作環境：ASP.NET Core 6+/8、YARP 或 Azure APIM、JWT/OAuth2、Git/DB 政策庫

實測數據：
- 改善前：無統一模型；授權規則分散；變更需多團隊對齊
- 改善後：單一模型與政策庫；變更一次發布多處生效
- 改善幅度：建議衡量上線時間縮短 30-50%，授權缺漏事故數下降 80%（目標值）

Learning Points（學習要點）
核心知識點：
- 政策即資料（Policy-as-Data）與決策點設計
- 資源/操作/主體/條件/限制的共通語彙
- Gateway vs App 的授權分工

技能要求：
- 必備技能：REST 設計、JWT/OAuth2 概念、JSON Schema
- 進階技能：組織治理、平台抽象、藍圖落地

延伸思考：
- 如何讓客戶自助調整政策（沙箱+審核）？
- 模型的過度抽象會導致可用性下降
- 可引入 OPA/自建 PDP 做遠端決策

Practice Exercise（練習題）
- 基礎練習：列出你系統的資源與操作清單（30 分鐘）
- 進階練習：為 3 條 API 建立政策 JSON 並定義決策點（2 小時）
- 專案練習：搭建政策庫與審核流程，落地到一條關鍵服務（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：模型覆蓋資源/操作/主體/條件/限制
- 程式碼品質（30%）：Schema 清晰、樣板可重用
- 效能優化（20%）：決策點分工合理
- 創新性（10%）：治理流程與自助能力設計


## Case #2: 微服務內部 S2S 認證與授權：Client Credentials + mTLS

### Problem Statement（問題陳述）
業務場景：N 個微服務彼此互相呼叫，過往依賴內網信任。隨系統擴張與容器化、跨區部署，內部流量不再等於可信。需要對內部服務之間建立身份驗證與授權，防止橫向移動與越權調用。

技術挑戰：服務身份管理、金鑰託管、零信任網路、低延遲與高可用的驗證。

影響範圍：任何被濫用的內部 API 可能造成資料外洩與大規模事故。

複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. 以網段信任代替服務身份認證。
2. 未統一使用 Token；缺少 Client ID/Secret 管理。
3. 授權粗糙：只做「能否呼叫」，未做「能呼叫什麼」。

深層原因：
- 架構層面：沒有服務身份（Service Identity）與頒發端（STS）。
- 技術層面：缺少 JWT 驗證與策略；未使用 mTLS。
- 流程層面：金鑰無輪替流程；憑證散落。

### Solution Design（解決方案設計）
解決策略：採用 OAuth2 Client Credentials 為 S2S 身份，頒發 JWT 存放 scope 與租戶，Gateway 啟用 mTLS 與基本限制，App 層做細粒度授權策略。

實施步驟：
1. 身份與頒發
- 實作細節：建立 STS/AAD App，為服務發 ClientId/Secret，頒發 JWT（client_credentials）。
- 所需資源：Azure AD/自建 STS
- 預估時間：1 週

2. Gateway 強制 mTLS 與 Token 驗證
- 實作細節：YARP/NGINX 設定雙向 TLS，驗證 JWT，限流。
- 所需資源：YARP/APIM、CA/憑證
- 預估時間：1-2 週

關鍵程式碼/設定：
```csharp
// ASP.NET Core（下游服務）— 驗證 JWT 與授權
services.AddAuthentication("Bearer")
    .AddJwtBearer("Bearer", o =>
    {
        o.Authority = "https://sts.example.com";
        o.Audience = "member.api";
        o.RefreshOnIssuerKeyNotFound = true;
    });

services.AddAuthorization(o =>
{
    o.AddPolicy("CanReadMember",
        p => p.RequireClaim("scope", "member.read"));
});
```

實際案例：MemberService 對外僅允許具有 scope=member.read 的服務呼叫 GetMember/GetMembers，其他操作需對應 scope。

實作環境：ASP.NET Core 6+/8、YARP 或 APIM、Azure AD/IdentityServer

實測數據：
- 改善前：內部 API 無 Token；橫向移動風險高
- 改善後：100% 內部流量帶 JWT；mTLS 啟用
- 改善幅度：建議目標 未授權請求攔截率 ≥99.9%，STS 可用性 ≥99.95%

Learning Points
- S2S 與 User 授權差異
- mTLS 與 JWT 的互補
- scope 設計與服務身份

技能要求
- 必備：OAuth2、TLS、ASP.NET Core Auth
- 進階：CA/憑證自動化、Service Mesh

延伸思考
- 與 Service Mesh（mTLS）整合
- Token 壽命與快取策略
- STS 高可用與災備

Practice Exercise
- 基礎：為一個內部服務註冊 Client Credentials（30 分）
- 進階：在 YARP 啟用 mTLS 與 JWT 驗證（2 小時）
- 專案：將 3 個服務流量全面 Token 化（8 小時）

Assessment
- 完整性：S2S 全面 Token 化
- 品質：策略與錯誤處理健全
- 效能：延遲小於 10ms
- 創新：自動化憑證輪替


## Case #3: 以方法為單位的細粒度授權（by domain method）

### Problem Statement（問題陳述）
業務場景：MemberService 暴露多個方法（Activate、Delete、ResetPassword...）。不同角色與客戶對每個方法的使用權限不同，必須精準到方法層級授權，避免「讀可等於寫」或「一權通用」。

技術挑戰：如何將方法映射到可治理的權限，並讓策略可演進且可稽核。

影響範圍：過度授權導致資安事故、合規違規。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 角色定義過粗（Admin/Editor），無法對應方法。
2. 未建立方法到 scope 的標準映射。
3. 缺少政策集中管理與審核。

深層原因：
- 架構：缺統一資源/操作模型。
- 技術：未使用政策式授權與自訂 Handler。
- 流程：授權由開發臨時決定，無版本與審核。

### Solution Design
解決策略：建立方法級 scope 命名規則與政策，使用 ASP.NET Core Authorization Policy 搭配自訂 Requirement，集中維護映射。

實施步驟：
1. 命名與映射
- 實作：member.read/member.activate/member.delete 等
- 資源：政策庫
- 時間：1 週

2. App 實作與套件化
- 實作：AuthorizePolicy 屬性與 Handler 封裝成 NuGet/共用程式庫
- 資源：ASP.NET Core
- 時間：1 週

關鍵程式碼/設定：
```csharp
[Authorize(Policy = "member.activate")]
public bool Activate(int id, string code) { ... }

services.AddAuthorization(o =>
{
    foreach (var s in new[] { "member.read", "member.list", "member.activate", "member.delete" })
        o.AddPolicy(s, p => p.RequireClaim("scope", s));
});
```

實際案例：僅具備 member.activate 的客戶服務團隊可執行 Activate，其它角色只能讀。

實作環境：ASP.NET Core 6+/8

實測數據：
- 改善前：角色過粗導致越權
- 改善後：方法級控制，授權審查清晰
- 改善幅度：建議目標 未授權方法呼叫下降 90%+

Learning Points
- scope 命名與方法映射
- Policy-based Authorization
- 權限封裝與重用

Practice
- 基礎：為 3 個方法定義 policy（30 分）
- 進階：自訂 AuthorizationHandler 驗證多個條件（2 小時）
- 專案：萃取為共用套件（8 小時）


## Case #4: 使用者資料隔離：A 不得存取 B（by owner）

### Problem Statement
業務場景：會員登入後能讀寫自己的資料，但不得讀寫他人資料。需要在讀與寫兩邊同時防護，避免以 ID 猜測取得他人資料。

技術挑戰：資料層與 API 層一致性、效能與快取、避免遺漏。

影響範圍：隱私外洩、法規風險。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 僅在控制器檢查 owner，資料查詢未過濾。
2. 無全域過濾器；開發者易遺漏。
3. Token 未攜帶 userId 或不可信。

深層原因：
- 架構：未把「owner」納入模型。
- 技術：EF/ORM 無全域過濾、或關閉。
- 流程：缺少安全測試用例。

### Solution Design
解決策略：JWT 攜帶 userId，API 層驗證 owner，資料層加全域 Query Filter，雙層防護。

實施步驟：
1. Token 與 API 防護
- 實作：從 claims 取 userId 與 route:id 比對
- 資源：ASP.NET Core
- 時間：0.5 週

2. 資料層過濾
- 實作：EF Core HasQueryFilter 依 userId 自動過濾
- 資源：EF Core
- 時間：0.5 週

關鍵程式碼/設定：
```csharp
// API 層
if (User.FindFirst("sub")?.Value != id.ToString())
    return Forbid();

// EF Core 層（假設 Member 有 OwnerId）
modelBuilder.Entity<Member>()
    .HasQueryFilter(m => m.OwnerId == _currentUser.UserId);
```

實作環境：ASP.NET Core、EF Core

實測數據：
- 改善前：可透過猜 ID 讀取他人資料
- 改善後：API 與資料雙層阻擋
- 改善幅度：建議目標 資料越權事件 0 起

Learning Points
- 雙層授權防護
- claims 對齊資料模型
- 全域過濾器

Practice
- 基礎：在一個查詢加入 owner 驗證（30 分）
- 進階：全域 Filter 與單元測試（2 小時）
- 專案：全域導入 owner 模式（8 小時）


## Case #5: 多租戶隔離：X 廠商不得讀取 Y 的資料（by tenant）

### Problem Statement
業務場景：系統提供多租戶 SaaS，合作廠商 X 與 Y 的資料必須嚴格隔離；外包或子帳號仍需在租戶邊界內。

技術挑戰：租戶辨識、資料層隔離、報表跨租戶匯整需求與安全。

影響範圍：資料外洩、合約/合規風險。

複雜度評級：高

### Root Cause Analysis
直接原因：
1. Token 無租戶宣告或不一致。
2. 資料庫未分區或無租戶欄位。
3. 查詢與快取未考慮租戶。

深層原因：
- 架構：未定義租戶作為一級維度。
- 技術：無 Row-Level Security/Filter。
- 流程：外部委任未綁定租戶。

### Solution Design
解決策略：Token 強制攜帶 tenantId，Gateway 與 App 驗證 tenant 邊界，資料層施加租戶過濾或分庫，配合快取分片。

實施步驟：
1. Token 與路由綁定
- 實作：route:tenantId 必須等於 claim:tenantId
- 資源：APIM/YARP、ASP.NET Core
- 時間：1 週

2. 資料層隔離
- 實作：EF Query Filter/Row-Level Security/分庫
- 資源：EF/DB
- 時間：1-2 週

關鍵程式碼/設定：
```csharp
// Gateway：條件判斷（APIM）
<choose>
  <when condition="@(context.Request.MatchedParameters["tenantId"] != context.Principal.GetClaimValue('tenantId'))">
    <return-response><set-status code="403" reason="Tenant Mismatch"/></return-response>
  </when>
</choose>
```

實作環境：APIM 或 YARP、ASP.NET Core、EF/資料庫

實測數據：
- 改善前：租戶邊界在應用層易被繞過
- 改善後：Gateway+App+DB 三層防護
- 改善幅度：建議目標 租戶越權 0 起；跨租戶報表使用唯讀隔離

Learning Points
- 租戶作為一級維度
- 三層隔離策略
- 快取與租戶分片

Practice
- 基礎：在 API 驗證 route 與 claims 的租戶（30 分）
- 進階：Row-Level Security/分庫策略（2 小時）
- 專案：為一個服務落地租戶隔離（8 小時）


## Case #6: 委任存取：客戶委託外包團隊 Z 代為操作（by intention）

### Problem Statement
業務場景：廠商 X 委託外包 Z 開發，Z 需使用 API 操作，但權限不得超出 X 的邊界，且行為需可追溯「代誰操作」。

技術挑戰：多方身份鏈、可審計、撤銷與時效、最小必要授權。

影響範圍：資料外洩、爭議追溯困難。

複雜度評級：高

### Root Cause Analysis
直接原因：
1. 使用共享帳密或共享金鑰，無法區分主體。
2. 無委任協議（consent）與時間/範圍限制。
3. Token 無代理關係（actor/obo）資訊。

深層原因：
- 架構：未定義委任模型。
- 技術：未支持 On-Behalf-Of（OBO）流程或 act claim。
- 流程：缺乏委任審批與撤銷。

### Solution Design
解決策略：使用 OAuth2 OBO 或自定 JWT act/delegation 聲明，委任必須記錄發起方、受委方、租戶、範圍與有效期；決策時同時驗證「代表關係」與「範圍」。

實施步驟：
1. 模型與發卡
- 實作：委任表單/審批，生成帶 act 的短期 Token
- 資源：STS/授權服務
- 時間：1-2 週

2. 驗證與審計
- 實作：授權 Handler 驗證 act 鏈，寫入審計
- 資源：ASP.NET Core/審計存儲
- 時間：1 週

關鍵程式碼/設定：
```csharp
// 授權處理：驗證委任鏈
var actor = User.FindFirst("act")?.Value;      // 代理方
var subject = User.FindFirst("sub")?.Value;    // 被代理/最終主體
var tenant = User.FindFirst("tenantId")?.Value;
if (string.IsNullOrEmpty(actor) || actor != "vendor.Z") return Forbid();
// 確認 actor 被 X 委任且在有效期與範圍內
```

實作環境：OAuth2/OBO（Azure AD 可用）、自建 STS、ASP.NET Core

實測數據：
- 改善前：無法追溯代誰操作；權限無邊界
- 改善後：代辦行為可審計、可撤銷、範圍受限
- 改善幅度：建議目標 100% 委任流量具備 act 與審計紀錄

Learning Points
- 委任模型與 OBO
- act/obo claims 設計
- 撤銷與時效

Practice
- 基礎：設計委任 Token claims（30 分）
- 進階：委任審批與撤銷 API（2 小時）
- 專案：將一條 API 改為 OBO 模式（8 小時）


## Case #7: 批次與大量操作風險：配額、速率與作業化

### Problem Statement
業務場景：Import、List 等大量操作容易被濫用（資料撈取、撞庫），也可能拖垮後端。需限制速率與配額，並將重操作作業化（job）。

技術挑戰：差異化限流、租戶/主體維度、回應可觀測與可恢復。

影響範圍：服務可用性、資料外洩風險。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無差異限流與配額。
2. 同步批次操作造成阻塞。
3. 無審計與告警。

深層原因：
- 架構：未定義 by client/tenant 的限制。
- 技術：Gateway 缺少策略；後端無排程機制。
- 流程：未定義配額與升級流程。

### Solution Design
解決策略：Gateway 實施 rate limit 與 quota，按租戶/主體/金鑰分流；將重操作改為非同步作業，提供查詢狀態 API。

實施步驟：
1. Gateway 限流/配額
- 實作：APIM policy 或 YARP 中介
- 資源：APIM/YARP
- 時間：0.5-1 週

2. 作業化
- 實作：將 Import 改為 job 提交 + 狀態查詢
- 資源：Queue/Worker
- 時間：1-2 週

關鍵程式碼/設定：
```xml
<!-- APIM：按訂閱金鑰限流 -->
<rate-limit-by-key calls="100" renewal-period="60"
                   counter-key="@(context.Subscription.Key)" />
```

實作環境：Azure APIM 或 YARP+中介、Queue/Worker

實測數據：
- 改善前：尖峰時段資源耗盡
- 改善後：錯峰與削峰、濫用受控
- 改善幅度：建議目標 P99 延遲穩定，拒絕率可觀測且受控

Learning Points
- 限流與配額策略
- 非同步批次化
- 可觀測與客訴處理

Practice
- 基礎：為某路由配置限流（30 分）
- 進階：把 Import 改為 Job 提交（2 小時）
- 專案：差異化限流（租戶等級）（8 小時）


## Case #8: 來源環境控制：IP 白名單與時間窗限制（by client environment）

### Problem Statement
業務場景：部分合作方只能從固定辦公室 IP 於工作時段呼叫 API；異常來源需立即拒絕於 Gateway。

技術挑戰：真實客戶 IP 解析、反代轉發標頭、規則管理。

影響範圍：降低外洩面與暴露面。

複雜度評級：低-中

### Root Cause Analysis
直接原因：
1. 僅在 App 層判斷，成本高且延遲。
2. 未解析 X-Forwarded-For。
3. 無規則化政策管理。

深層原因：
- 架構：未在 Gateway 前置過濾。
- 技術：缺少正確來源解析。
- 流程：白名單變更無審核流程。

### Solution Design
解決策略：在 Gateway 前置 IP/時間窗策略，App 僅處理業務授權；規則集中管理。

實施步驟：
1. 來源解析與規則
- 實作：解析 client IP，按金鑰/租戶套用白名單
- 資源：APIM/YARP
- 時間：0.5 週

2. 時間窗限制
- 實作：營業時間內允許
- 資源：APIM/YARP
- 時間：0.5 週

關鍵程式碼/設定：
```xml
<!-- APIM：依 IP 限制 -->
<choose>
  <when condition="@(context.Request.IpAddress != "203.0.113.10")">
    <return-response><set-status code="403" reason="IP Not Allowed"/></return-response>
  </when>
</choose>
```

實作環境：APIM 或 YARP

實測數據：
- 改善前：可從任意來源呼叫
- 改善後：僅允許白名單來源
- 改善幅度：建議目標 非白名單請求阻擋率 100%

Learning Points
- 來源解析與鏈路標頭
- Gateway 前置過濾
- 規則治理

Practice
- 基礎：新增一條 IP 白名單規則（30 分）
- 進階：依租戶套用差異白名單（2 小時）
- 專案：自助白名單申請流程（8 小時）


## Case #9: Gateway 與 App 的授權分工與卸載（offloading）

### Problem Statement
業務場景：高流量服務需要把可前置的檢查（IP、限流、基本 Token 驗證）卸載到 Gateway，App 僅專注業務授權（租戶/狀態/擁有者）。

技術挑戰：分工邊界設計、重入與上下文傳遞、故障隔離。

影響範圍：效能、穩定性與可維運性。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 所有授權都在 App，造成壓力與重複。
2. Gateway 僅轉發，不做安全價值。
3. 缺乏上下文傳遞（如 user/tenant）。

深層原因：
- 架構：未規範決策點。
- 技術：無 Gateway 擴展機制。
- 流程：部署與變更未分層。

### Solution Design
解決策略：確立「前置可通用在 Gateway、業務需上下文在 App」，使用 APIM/YARP 實施卸載；用標頭安全傳遞下游所需上下文。

實施步驟：
1. 邊界定義與實施
- 實作：在 Gateway 驗證 Token/限流/IP，傳遞已驗證 claims
- 資源：APIM/YARP
- 時間：1 週

2. App 僅處理業務授權
- 實作：租戶/擁有者/狀態
- 資源：ASP.NET Core
- 時間：1 週

關鍵程式碼/設定：
```json
// YARP：轉發並附加已驗證的租戶與主體（僅作示意）
"Transforms": [
  { "RequestHeader": "X-Sub", "Set": "{claims:sub}" },
  { "RequestHeader": "X-Tenant", "Set": "{claims:tenantId}" }
]
```

實作環境：APIM 或 YARP、ASP.NET Core

實測數據：
- 改善前：App CPU/延遲偏高
- 改善後：前置卸載，App 聚焦業務
- 改善幅度：建議目標 認證耗時下降 50%，P95 延遲改善 20%（目標）

Learning Points
- 決策點設計
- 上下文傳遞
- 卸載與隔離

Practice
- 基礎：把限流移到 Gateway（30 分）
- 進階：標頭帶上下文到下游（2 小時）
- 專案：完成一條鏈路的卸載改造（8 小時）


## Case #10: 憑證模型選型：API Key、JWT、Azure AD（何時用哪個）

### Problem Statement
業務場景：對外提供 API，部分簡單場景用金鑰即可；對內/對外合作需更豐富的身份與範圍控制；企業客戶偏好 AAD 統一治理。

技術挑戰：同時支援多種機制、平滑演進、不破壞現有客戶整合。

影響範圍：接入門檻、維運複雜度、合規。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 單一機制無法覆蓋全部場景。
2. 不同客戶有不同 IdP 偏好。
3. 缺少抽象與協議。

深層原因：
- 架構：未定義統一抽象。
- 技術：驗證管線不具可插拔性。
- 流程：客戶接入流程未分級。

### Solution Design
解決策略：提供多鑰方案：API Key（簡單）、JWT（細權限）、Azure AD（企業整合）。使用 PolicyScheme 依請求自動分流到對應驗證器。

實施步驟：
1. 驗證多方案
- 實作：API Key + JWT + AAD（OIDC）
- 資源：ASP.NET Core
- 時間：1 週

2. 客戶分級接入
- 實作：自助開通與升級路徑
- 資源：門戶/工作流
- 時間：1 週

關鍵程式碼/設定：
```csharp
services.AddAuthentication(o =>
{
    o.DefaultScheme = "smart";
})
.AddPolicyScheme("smart", "Smart", options =>
{
    options.ForwardDefaultSelector = ctx =>
        ctx.Request.Headers.ContainsKey("Authorization") ? "Bearer" : "ApiKey";
})
.AddJwtBearer("Bearer", o => { o.Authority = "..."; o.Audience = "api"; })
.AddScheme<ApiKeyOptions, ApiKeyHandler>("ApiKey", o => { /*...*/ });
```

實作環境：ASP.NET Core、Azure AD/APIM（可選）

實測數據：
- 改善前：單一機制造成阻力
- 改善後：多鑰並存，接入友好
- 改善幅度：建議目標 接入時間縮短 30%，升級路徑清晰

Learning Points
- 多鑰並存與分流
- 客戶分級策略
- 可插拔驗證

Practice
- 基礎：加上 API Key 驗證（30 分）
- 進階：PolicyScheme 自動分流（2 小時）
- 專案：接入 Azure AD（8 小時）


## Case #11: 指令級保護：依狀態機授權（Activate/Delete/ResetPassword）

### Problem Statement
業務場景：MemberService 的命令（Activate、Lock、Delete...）需遵循狀態機，不同狀態可執行的命令不同，需在授權時導入狀態檢查。

技術挑戰：授權與領域邏輯的協作、避免循環依賴、效能。

影響範圍：非法狀態變更導致資料錯亂與風險。

複雜度評級：中-高

### Root Cause Analysis
直接原因：
1. 只驗證 scope，未驗證狀態。
2. 控制器與服務層分散檢查，易遺漏。
3. 缺乏可重用的狀態檢查策略。

深層原因：
- 架構：未把狀態納入安全模型。
- 技術：授權 Handler 無法存取領域狀態。
- 流程：缺乏狀態級測試。

### Solution Design
解決策略：自訂 AuthorizationHandler 讀取資料庫/領域服務判定狀態是否允許；以 Requirement 表示命令需求，控制器與服務層雙檢。

實施步驟：
1. Requirement 與 Handler
- 實作：RequiresState("Locked").For(UnLock)
- 資源：ASP.NET Core、Repo
- 時間：1 週

2. 服務層守門
- 實作：即使繞過控制器也不能執行
- 資源：MemberService
- 時間：0.5 週

關鍵程式碼/設定：
```csharp
public class MemberStateRequirement : IAuthorizationRequirement
{
    public string MustBeState { get; }
    public MemberStateRequirement(string s) => MustBeState = s;
}

public class MemberStateHandler : AuthorizationHandler<MemberStateRequirement>
{
    private readonly IMemberRepo _repo;
    public MemberStateHandler(IMemberRepo repo) => _repo = repo;
    protected override async Task HandleAsync(AuthorizationHandlerContext context)
    {
        var req = context.PendingRequirements.OfType<MemberStateRequirement>().FirstOrDefault();
        var id = context.User.FindFirst("memberId")?.Value;
        var state = await _repo.GetStateAsync(int.Parse(id));
        if (state == req.MustBeState) context.Succeed(req);
    }
}
```

實作環境：ASP.NET Core、EF/Repo

實測數據：
- 改善前：非法狀態變更零星發生
- 改善後：狀態不符直接拒絕
- 改善幅度：建議目標 非法變更 0 起

Learning Points
- 授權與狀態機整合
- 雙層守門設計
- 可重用 Requirement

Practice
- 基礎：為 Unlock 加狀態授權（30 分）
- 進階：抽象化 Requirement 工具包（2 小時）
- 專案：覆蓋全部命令（8 小時）


## Case #12: 誰來管理權限：集中治理與自助授權（PM/客服/客戶）

### Problem Statement
業務場景：授權不僅是 RD 責任，PM/PO、客服、甚至客戶需能管理 API 權限與配額。缺乏安全的自助入口與審核流程，導致授權變更慢且易錯。

技術挑戰：政策即資料、版本/審核、審計與追溯、衝突處理。

影響範圍：交付效率、合規。

複雜度評級：中-高

### Root Cause Analysis
直接原因：
1. 權限變更需發版，週期長。
2. 缺少自助與審核。
3. 無審計與回滾。

深層原因：
- 架構：政策不在資料層。
- 技術：政策讀取與熱更新缺失。
- 流程：無 RACI 與 SOP。

### Solution Design
解決策略：建立「授權中心」，政策存 DB/Git，提供申請/審核/生效流水線，Gateway/App 定期同步或即時拉取政策。

實施步驟：
1. 政策服務與門戶
- 實作：CRUD+審核+審計
- 資源：Web/DB
- 時間：2-3 週

2. 熱更新與快取
- 實作：IOptionsMonitor/ETag 拉取
- 資源：ASP.NET Core
- 時間：1 週

關鍵程式碼/設定：
```csharp
// 以 ETag 拉取最新政策（示意）
var req = new HttpRequestMessage(HttpMethod.Get, policyUrl);
req.Headers.IfNoneMatch.Add(new EntityTagHeaderValue(currentEtag));
var resp = await http.SendAsync(req);
if (resp.StatusCode == HttpStatusCode.OK) { /* 更新政策與 ETag */ }
```

實作環境：ASP.NET Core、DB/Git

實測數據：
- 改善前：權限變更=發版
- 改善後：權限變更=審核+即時生效
- 改善幅度：建議目標 變更週期縮短 70%

Learning Points
- 政策即資料與熱更新
- 權限門戶與審核
- 審計與回滾

Practice
- 基礎：做一個政策查詢 API（30 分）
- 進階：ETag 熱更新快取（2 小時）
- 專案：最小可用授權中心（8 小時）


## Case #13: 金鑰與簽章輪替：API Key 與 JWKS 無痛更新

### Problem Statement
業務場景：API Key 與 JWT 簽章需定期輪替以降低風險，但不能影響線上服務。需支援雙活金鑰與自動刷新公鑰。

技術挑戰：兼容舊新金鑰、客戶端協調、最小化中斷。

影響範圍：安全與穩定性。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 單一金鑰使用過久。
2. 發現新金鑰無法即時同步。
3. 舊金鑰撤銷造成中斷。

深層原因：
- 架構：無輪替計畫與雙金鑰策略。
- 技術：未使用 JWKS/自動刷新。
- 流程：客戶通知與灰度缺失。

### Solution Design
解決策略：API Key 實施「兩把有效、一把預置」策略；JWT 使用 JWKS 與自動刷新，設定 RefreshOnIssuerKeyNotFound；灰度切換。

實施步驟：
1. 雙金鑰策略
- 實作：接受兩把有效金鑰，逐步撤換
- 資源：授權中心
- 時間：0.5 週

2. JWKS 自動刷新
- 實作：設定自動取鑰與快取
- 資源：ASP.NET Core
- 時間：0.5 週

關鍵程式碼/設定：
```csharp
.AddJwtBearer(o =>
{
    o.Authority = "https://sts.example.com";
    o.Audience = "api";
    o.RefreshOnIssuerKeyNotFound = true; // 找不到 kid 時自動刷新
});
```

實作環境：ASP.NET Core、STS/JWKS

實測數據：
- 改善前：輪替造成短暫中斷
- 改善後：無縫輪替
- 改善幅度：建議目標 中斷 0；輪替周期 ≤90 天

Learning Points
- 雙金鑰/灰度策略
- JWKS 與自動刷新
- 通知與回退

Practice
- 基礎：為驗證端啟用 RefreshOnIssuerKeyNotFound（30 分）
- 進階：API Key 雙活驗證（2 小時）
- 專案：輪替 Runbook（8 小時）


## Case #14: 可觀測與審計：把安全事件「說清楚、記下來」

### Problem Statement
業務場景：需追蹤誰在何時對哪個資源做了什麼動作、結果如何，尤其是委任、租戶越權與批次操作。缺乏標準審計造成追溯困難。

技術挑戰：結構化、安全、不洩密、易查詢與告警。

影響範圍：合規、資安調查、SLA。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 日誌不結構化、分散。
2. 缺乏安全上下文（sub/tenant/act/op）。
3. 無對應告警與報表。

深層原因：
- 架構：沒有安全事件模型。
- 技術：缺少中介軟體與事件匯流。
- 流程：未定義保留期與取證流程。

### Solution Design
解決策略：統一安全事件模型，使用 Middleware 捕捉請求與授權結果，送往集中式日誌/事件匯流；建立告警與報表。

實施步驟：
1. 安全中介與事件模型
- 實作：Action/Resource/Subject/Tenant/Result
- 資源：ASP.NET Core Middleware
- 時間：1 週

2. 告警與報表
- 實作：未授權尖峰、配額超限、委任異常
- 資源：SIEM/Log 平台
- 時間：1 週

關鍵程式碼/設定：
```csharp
app.Use(async (ctx, next) =>
{
    var sw = Stopwatch.StartNew();
    await next();
    sw.Stop();
    var ev = new {
        ts = DateTime.UtcNow,
        sub = ctx.User.FindFirst("sub")?.Value,
        tenant = ctx.User.FindFirst("tenantId")?.Value,
        act = ctx.Request.Method + " " + ctx.Request.Path,
        status = ctx.Response.StatusCode,
        durMs = sw.ElapsedMilliseconds
    };
    logger.LogInformation("SEC_AUDIT {evt}", JsonSerializer.Serialize(ev));
});
```

實作環境：ASP.NET Core、集中式日誌/SIEM

實測數據：
- 改善前：無法追溯與告警
- 改善後：可視化安全狀態
- 改善幅度：建議目標 重大事件檢出時間 < 5 分鐘

Learning Points
- 安全事件模型
- 中介與結構化日誌
- 告警與報表

Practice
- 基礎：中介記錄審計事件（30 分）
- 進階：建立未授權告警規則（2 小時）
- 專案：安全月報表（8 小時）


## Case #15: 把安全變成可測的：單元/整合測試與 Pipeline Gate

### Problem Statement
業務場景：安全規則複雜且變動頻繁，僅靠人工驗收風險極高。需在 CI/CD 中自動驗證授權與安全行為，阻擋錯誤上線。

技術挑戰：測試 Token 發行、場景覆蓋、測試資料準備、可重用。

影響範圍：品質、交付效率、事故率。

複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無安全測試樣板。
2. 手動測 Token，易出錯。
3. Pipeline 無安全 Gate。

深層原因：
- 架構：測試不納入設計。
- 技術：無測試 STS/工廠。
- 流程：CI/CD 未設 Gate。

### Solution Design
解決策略：建立測試憑證工廠（可發測試 JWT/API Key），撰寫單元/整合測試覆蓋關鍵規則，CI/CD 設定測試 Gate 與安全掃描。

實施步驟：
1. 測試憑證工廠
- 實作：本地簽章、固定 kid
- 資源：測試程式庫
- 時間：0.5 週

2. 測試與 Gate
- 實作：xUnit + WebApplicationFactory + GitHub Actions
- 資源：CI/CD
- 時間：0.5-1 週

關鍵程式碼/設定：
```csharp
[Fact]
public async Task GetMember_Should_403_When_TenantMismatch()
{
    var token = TestTokenFactory.Create(new { sub="u1", tenantId="t1", scope="member.read" });
    var client = _factory.CreateClient();
    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
    var resp = await client.GetAsync("/t2/members/1");
    Assert.Equal(HttpStatusCode.Forbidden, resp.StatusCode);
}
```

實作環境：.NET、xUnit、CI/CD

實測數據：
- 改善前：安全回歸成本高
- 改善後：每次提交自動驗證
- 改善幅度：建議目標 高風險規則覆蓋率 ≥90%


--------------------------------
案例分類
--------------------------------

1) 按難度分類
- 入門級（適合初學者）
  - Case 3 方法級授權
  - Case 4 使用者資料隔離
  - Case 7 限流與作業化（基礎）
  - Case 8 IP/時間窗限制
  - Case 10 多鑰並存選型（基礎）

- 中級（需要一定基礎）
  - Case 2 內部 S2S 認證與授權
  - Case 5 多租戶隔離
  - Case 9 Gateway 卸載分工
  - Case 11 狀態機授權
  - Case 13 金鑰/JWKS 輪替
  - Case 14 可觀測與審計
  - Case 15 安全測試與 Gate

- 高級（需要深厚經驗）
  - Case 1 安全模型與政策即資料
  - Case 6 委任存取（OBO）
  - Case 12 集中治理與自助授權

2) 按技術領域分類
- 架構設計類：Case 1, 5, 6, 9, 12
- 效能優化類：Case 7, 9, 13
- 整合開發類：Case 2, 10
- 除錯診斷類：Case 14, 15
- 安全防護類：Case 3, 4, 5, 6, 8, 11, 13

3) 按學習目標分類
- 概念理解型：Case 1, 10, 12
- 技能練習型：Case 3, 4, 7, 8, 11, 13, 14, 15
- 問題解決型：Case 2, 5, 6, 9
- 創新應用型：Case 6, 12


--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 建議先學（基礎概念與最小實作）：
  - Case 1（建立共同語彙與模型）
  - Case 10（理解多種憑證模型與分流）
  - Case 3（方法級授權）、Case 4（owner 隔離）

- 進階主題（核心能力）：
  - Case 5（多租戶隔離）：依賴 Case 1, 4
  - Case 7（限流/配額/作業化）：依賴 Case 9 的分工理念
  - Case 8（IP/時間窗）：可並行

- 微服務落地（系統化）：
  - Case 2（S2S 認證）：依賴 Case 10
  - Case 9（Gateway 卸載）：依賴 Case 1, 10
  - Case 11（狀態機授權）：依賴 Case 3

- 治理與可運營：
  - Case 12（集中治理與自助）：依賴 Case 1
  - Case 13（金鑰/JWKS 輪替）：依賴 Case 10
  - Case 14（可觀測與審計）：覆蓋所有案例
  - Case 15（測試與 Gate）：覆蓋所有案例

完整學習路徑建議：
1 -> 10 -> 3 -> 4 -> 5 -> 8 -> 7 -> 2 -> 9 -> 11 -> 13 -> 14 -> 15 -> 12 -> 6

- 先打好模型與多鑰並存基礎，再落到方法與資料隔離；
- 之後學會租戶隔離與環境限制，再上限流與作業化；
- 進入微服務世界的 S2S 與 Gateway 卸載，接著導入狀態機授權；
- 具備輪替與審計/測試後，導入集中治理與委任，完成企業級 API 安全管控閉環。
