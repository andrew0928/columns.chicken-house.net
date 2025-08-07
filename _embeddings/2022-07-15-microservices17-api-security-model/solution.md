# 微服務架構 – API 的安全管控模型

# 問題／解決方案 (Problem/Solution)

## Problem: 微服務之間缺乏一致且細緻的 API 存取控管

**Problem**:  
在微服務架構下，服務數量激增，彼此透過 API 溝通。若僅以單一 API Key 或存取 Token 做「全域」授權，容易出現以下困境：  
1. 不同 Method / Resource 難以設定各自的授權規則。  
2. 同一把金鑰被分享後，所有權限直接外洩。  
3. 外部合作廠商或客戶的權限與內部服務混在一起，無法快速區分、追蹤。  

**Root Cause**:  
1. 傳統「KEY＝全部功能」的授權模型過於粗糙，無法滿足 Method、資料範圍、呼叫者角色…等多維度需求。  
2. 安全權限被視為「基礎建設」議題，而非系統設計議題，因此缺乏在 Domain Layer 內就定義「誰可以呼叫什麼」。  

**Solution**:  
1. 在系統設計階段，先以「功能/資料/行為」切出授權單位 (Scope)。  
2. 以 Claim‐Based 的 JWT／OAuth2 Access Token 為核心，將「可呼叫的 Method」與「可存取的資料範圍」寫入 Claim。  
3. 透過 API Gateway (Azure API Management、Ocelot、YARP…​) 進行 Token Validation 與 Scope 判斷，將流量在進入服務前 Off-loading。  
4. 範例 (ASP.NET Core Middleware)：  

```csharp
public void Configure(IApplicationBuilder app, IHostingEnvironment env)
{
    app.UseAuthentication();          // JWT 驗證
    app.UseAuthorization();           // Scope / Role 授權
    app.UseEndpoints(endpoints =>
    {
        endpoints.MapControllers()
                 .RequireAuthorization("MemberService.Scope");
    });
}
```

關鍵思考點：  
• 把「授權對象」與「功能／資料」轉為可驗證的 Claim，才能在 Gateway 層直接阻擋不合法請求。  
• 服務越多，越需要在邊界 (Gateway) 阻擋，降低各服務重複實作負擔。  

**Cases 1**:  
企業內部 40+ 微服務統一接入 Azure API Management，使用 OAuth2 + JWT Scope。導入後：  
• 服務端不再各自維護白名單/權限表，開發工時下降 30%。  
• 外部協力廠商僅能呼叫被授權的 6 組 API，審計報告顯示越權存取事件降為 0。  

---

## Problem: 安全機制沒有在需求階段即被評估，導致後期補強成本高

**Problem**:  
許多團隊先把功能做完，最後才「交給基礎建設人員」補做資安。結果常見：  
1. 已上線的 API 需大改簽章才能加權限。  
2. 整合測試階段才發現資料可被任意跨租戶存取，必須臨時封鎖。  

**Root Cause**:  
安全需求被視為「Infra 工作」，未列入需求／規格，導致 Domain Model 與授權 Model 脫鉤。  

**Solution**:  
1. 把「安全條件」視為 Acceptance Criteria，與功能需求同時寫入 User Story。  
2. 導入 Threat Modeling 工作坊 (STRIDE)；在設計審查時，將可能的跨租戶、重放、越權等風險納入設計決策。  
3. Pipeline 加入自動化 API 合規測試 (OWASP Zap / Postman Test)。  

**Cases 1**:  
Scrum Team 於 Refinement 就加入「安全維度」。每個 Story 完成 DoD (Definition of Done) 需附帶 API Abuse Test。Release 後六個月未出現任何越權事件，因修正時程壓縮，平均新功能時程縮短 15%。  

---

## Problem: 多租戶與 3rd-Party 整合時，資料外洩風險大幅提升

**Problem**:  
• 客戶 A 的系統需要委外給外包商 Z 開發附加功能。  
• API 金鑰被 Z 重覆使用，可能存取客戶 B 或其他租戶的資料。  
• 沒有流量／IP／時間的額外限制；一旦金鑰外洩，所有資料可被瞬間掃光。  

**Root Cause**:  
1. 授權模型沒有「租戶 (Tenant)」的第一級隔離。  
2. 權限綁在「Key」而非「租戶 + Key + 限制條件」，難以做即時吊銷或限流。  

**Solution**:  
1. 採用「Tenant-Aware」的 Token：Token 內含 tenant_id、client_id、scope。  
2. Token 取得流程 (Auth Server) 必須驗證「呼叫者身份是否隸屬該 Tenant」。  
3. 在 Gateway 層加上 Rate Limit、IP 白名單、使用時段等多重限制。  
4. 引入 Token Introspection 介面，做到即時吊銷。  
   • Azure API Management 直接設定「By Subscription + By Product + Rate Limit」。  
   • 自架方案可在 Ocelot 加 RateLimitMiddleware。  

**Cases 1**:  
SaaS 產品導入「Tenant-Aware Token」後，成功阻斷一次外包商嘗試列舉其他租戶資料的行為；安全稽核分數自 65 提升至 92。  

**Cases 2**:  
對外 API 日流量 3,000,000，加入 Gateway Rate Limit 後，遭惡意掃描時自動限速；後端服務 CPU 使用率高峰由 85% 降至 40%，避免整體服務降速。  

---

## Problem: 服務端沒有流量 Off-loading，安全檢查導致核心服務踩 CPU / 記憶體瓶頸

**Problem**:  
當使用者量迅速成長，每個請求都進到核心服務做 JWT 驗證、Scope 比對，造成：  
• CPU 大量消耗在驗證流程。  
• 授權邏輯分散在 N 個服務，維護成本高。  

**Root Cause**:  
授權實作與業務邏輯耦合在一起；未將「共通的驗證、授權、限流」外移至 Reverse Proxy / Gateway。  

**Solution**:  
1. 於流量入口處 (Nginx + lua、Envoy、Kong、YARP) 實作統一的 Authorization Filter。  
2. 服務只處理業務邏輯；授權結果以 Downstream Header 傳遞 (e.g. X-UserId, X-TenantId)。  
3. 實際導入 (YARP Example)：  

```csharp
builder.Services.AddReverseProxy()
    .LoadFromMemory(routes, clusters)
    .AddTransforms(builderContext =>
    {
        builderContext.AddRequestTransform(async transformContext =>
        {
            var user = transformContext.HttpContext.User;
            if (!user.HasClaim("scope","MemberService.Read"))
            {
                transformContext.HttpContext.Response.StatusCode = 403;
                transformContext.SuppressRequestBody = true;
            }
        });
    });
```  

**Cases 1**:  
將 JWT 驗證移到 Gateway 之後，MemberService 平均 CPU 使用率下降 45%；單節點可支撐 QPS 從 600 提升到 1,100。  

---

以上各方案，可依系統規模、租戶複雜度與流量級別自由組合，形成一套自動化、可演進的 API 安全管控模型。