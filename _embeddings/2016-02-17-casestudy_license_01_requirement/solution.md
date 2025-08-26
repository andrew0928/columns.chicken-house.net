以下內容基於提供的文章主題與情境（Install-Based 部署、Service A/B/C、離線授權、API KEY、DX 與安全強度與擴充性），將需求與問題拆解為 16 個教學導向的實戰解決方案案例。因本篇原文為「需求篇」，未提供具體度量數據與程式碼細節；為滿足教學/練習/評估用途，以下案例之流程、程式碼片段與成效指標為可落地的設計與測試基準建議，適用於實作與評估。

----------------------------------------

## Case #1: 離線授權驗證（授權碼數位簽章）

### Problem Statement（問題陳述）
業務場景：在 Install-Based 佈署中，Service B/C 安裝於客戶資料中心，無法保證連網至原廠雲端。即使處於封閉網路，仍需按合約授權啟動功能，且不可由系統整合商或 IT 人員私自開啟。需能以一段授權碼（檔/字串）於離線環境完成驗證與啟動。
技術挑戰：不依賴線上查驗，如何可靠判斷授權真偽與內容完整性（功能列表、租戶、期限）？
影響範圍：未授權功能被開啟、合約到期後仍可使用、審計與法務風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 功能開關存於設定檔，缺乏完整性保護，易被篡改。
2. 驗證流程依賴雲端查核，不適用離線環境。
3. 未使用數位簽章，授權內容可被偽造或修改。
深層原因：
- 架構層面：信任邊界模糊，未將「授權」設計為獨立驗證邏輯。
- 技術層面：未採用公私鑰簽章，缺乏不可否認性。
- 流程層面：授權發佈與驗證未定義標準格式與工作流程。

### Solution Design（解決方案設計）
解決策略：採公私鑰非對稱簽章（原廠私鑰簽發、產品內置公鑰驗證），以 JSON 序列化授權內容，包含租戶、功能、有效期、硬體綁定與 key id。產品啟動與關鍵流程時進行驗證，確保在完全離線環境也能可信賴地啟用與禁用功能。

實施步驟：
1. 定義授權格式與信任模型
- 實作細節：設計 License JSON payload 與簽章欄位，加入 kid、nbf、exp、tenantId、features[]、hardwareId。
- 所需資源：JSON Schema、密鑰管理計畫。
- 預估時間：1-2 天
2. 實作簽章與驗章
- 實作細節：原廠簽章（私鑰）；產品端驗章（公鑰），在啟動與每次關鍵操作前校驗。
- 所需資源：.NET System.Security.Cryptography
- 預估時間：2-3 天

關鍵程式碼/設定：
```csharp
// License payload: base64(JSON), signature: base64
public record LicensePayload(
    string TenantId, string[] Features, DateTimeOffset Nbf, DateTimeOffset Exp,
    string HardwareId, string Kid, string Version);

public static bool VerifyLicense(string payloadB64, string sigB64, RSA rsa)
{
    var data = Convert.FromBase64String(payloadB64);
    var sig  = Convert.FromBase64String(sigB64);
    return rsa.VerifyData(data, sig, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}
```

實際案例：Service B/C 離線安裝，從原廠取得 license.json（含 payload+signature），啟動時載入並驗章後啟用功能。
實作環境：.NET 6/7/8, C# 10+, System.Security.Cryptography
實測數據：
改善前：功能開關易被改動；離線不可查核
改善後：離線驗章通過才啟用；偽造/篡改即失敗
改善幅度：未授權啟用事件降至 0（內部基準）

Learning Points（學習要點）
核心知識點：
- 非對稱簽章（私簽公驗）
- 授權內容序列化與不可否認性
- 信任邊界與離線驗證
技能要求：
- 必備技能：C#、JSON、基礎密碼學 API
- 進階技能：簽章格式設計、異常與審計策略
延伸思考：
- 可改用 ECDSA 以縮短授權碼大小
- 若公鑰被替換，如何偵測？（見 Case #16）
- 如何安全更新公鑰信任庫？（見 Case #12）
Practice Exercise（練習題）
- 基礎練習：撰寫 VerifyLicense，驗證簽章失敗時拒用（30 分）
- 進階練習：加入 nbf/exp 驗證與錯誤分類（2 小時）
- 專案練習：做一個離線 License 驗證 CLI（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：離線可驗章、必備欄位檢查
- 程式碼品質（30%）：結構清晰、錯誤處理完善
- 效能優化（20%）：啟動驗章延遲<10ms
- 創新性（10%）：格式版本化/可擴充性

----------------------------------------

## Case #2: API KEY 與功能範圍（Scopes）授權

### Problem Statement（問題陳述）
業務場景：Service B 需呼叫 Service A API，Service A 需根據 API KEY 判斷允許的功能/資源，且在內網或封閉網路中可能無法回原廠查核。
技術挑戰：如何不透過中心化查詢即可可信地判斷 key 的權限與有效期？
影響範圍：權限過寬導致資料外洩或越權操作。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. API KEY 未包含 scope 與租戶，難以實施最小權限。
2. 靠資料庫查表，不適用封閉環境。
3. 無簽章保護，key 可被修改或偽造。
深層原因：
- 架構層面：未定義權限在 token 中自我描述（self-contained）。
- 技術層面：缺少 JWS（或等效）簽章模型。
- 流程層面：key 發放與到期策略不完整。

### Solution Design（解決方案設計）
解決策略：採用 JWS 風格的自包含 API Token（非對稱簽章），包含 scopes/tenantId/exp/nbf/kid；Service A 僅需公鑰驗章與 scope 比對。可於 Intranet 運作。

實施步驟：
1. 設計 Token Claims 與驗證中介層
- 實作細節：Authorization header 攜帶簽章 token；中介層驗章並將 claims 放入 HttpContext。
- 所需資源：ASP.NET Core Middleware
- 預估時間：1-2 天
2. Scope 授權檢查
- 實作細節：Controller/Endpoint 層比對 scope，拒絕越權。
- 所需資源：Policy-based 授權
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
app.Use(async (ctx, next) =>
{
    var token = ctx.Request.Headers["Authorization"].ToString().Replace("Bearer ", "", StringComparison.OrdinalIgnoreCase);
    if (TryValidateJws(token, out var claims)) // 驗章+exp/nbf
    {
        ctx.Items["Scopes"] = claims["scopes"]; // string[]
        await next();
    }
    else
    {
        ctx.Response.StatusCode = 401;
    }
});
```

實際案例：Service A 對 B 簽發包含「orders.read」「invoices.write」的 Token。Service A 驗章後按 scope 控制 API。
實作環境：ASP.NET Core 6/7/8、System.Security.Cryptography
實測數據：
改善前：API KEY 共享且權限過寬
改善後：最小權限、離線驗章
改善幅度：越權失敗率降至 0（內部基準）

Learning Points（學習要點）
核心知識點：
- 自包含 Token（JWS）
- Scope/Policy-based 授權
- 中介層驗證與 Claims 注入
技能要求：
- 必備技能：ASP.NET Core Middleware、驗章
- 進階技能：Policy/Attribute 授權
延伸思考：
- 是否需加入 rate limit（見 Case #10）
- kid 與金鑰輪替（見 Case #12）
- DX：以屬性宣告 scope（見 Case #8）
Practice Exercise
- 基礎：撰寫 TryValidateJws 並驗證 exp/nbf（30 分）
- 進階：實作 ScopePolicyHandler（2 小時）
- 專案：完成一套 API-Key 發放與驗證樣板（8 小時）
Assessment Criteria
- 功能完整性：驗章+scope 驗證
- 程式碼品質：中介層職責清晰
- 效能優化：驗證延遲<2ms
- 創新性：多租戶隔離策略

----------------------------------------

## Case #3: 授權期限與合約續約（nbf/exp/寬限期）

### Problem Statement（問題陳述）
業務場景：授權需隨合約到期自動停用，續約後更換新授權恢復運作；全程可在離線環境。
技術挑戰：時間驗證、時鐘偏移、寬限期、操作人為錯誤。
影響範圍：過期未停用或誤停造成法務或 SLA 風險。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無 nbf/exp 欄位，或不驗證。
2. 對時不準，造成誤判。
3. 沒有續約換證工作流程。
深層原因：
- 架構層面：未定義過期行為與狀態轉換。
- 技術層面：無寬限期（grace period）與時鐘容錯。
- 流程層面：缺少換證 SOP 與回滾策略。

### Solution Design
解決策略：在授權中定義 nbf/exp；驗證加入 clockSkew 與 gracePeriod；提供換證工具，支持多版本共存短期切換。

實施步驟：
1. 時間驗證與容錯
- 實作細節：允許 ±N 分鐘 clock skew；exp 後進入 grace 狀態，降級功能。
- 所需資源：設定檔/Policy
- 預估時間：1 天
2. 換證作業
- 實作細節：支援新/舊授權共存 24h，平順切換。
- 所需資源：CLI 工具
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
bool IsWithin(DateTimeOffset now, DateTimeOffset nbf, DateTimeOffset exp, TimeSpan skew, TimeSpan grace, out bool inGrace)
{
    inGrace = now > exp && now <= exp + grace;
    return now >= nbf - skew && now <= exp + grace;
}
```

實際案例：Service B 授權 exp 後 7 天內維持唯讀模式，續約上傳新授權即時恢復。
實作環境：.NET 6/7/8
實測數據：
改善前：過期立即停擺；續約切換有風險
改善後：平滑切換與降級運作
改善幅度：續約停機時間降至 <1 分鐘（內部基準）

Learning Points
- nbf/exp/clockSkew/grace period
- 降級模式與風險控制
- 換證流程設計
技能要求：
- 必備：時間處理、設定管理
- 進階：零停機切換策略
延伸思考：
- 與時間來源防回撥（見 Case #18）
- DX 的換證導引（見 Case #8）
Practice Exercise
- 基礎：實作 IsWithin 測試（30 分）
- 進階：加入降級功能旗標（2 小時）
- 專案：做一個換證工具與回滾（8 小時）
Assessment Criteria
- 功能：準確判斷與降級
- 品質：時間區域/時差處理嚴謹
- 效能：常數時間檢查
- 創新：零停機切換

----------------------------------------

## Case #4: 金鑰管理與保護（私鑰安全與簽章服務）

### Problem Statement
業務場景：原廠用私鑰簽發授權/Token，一旦私鑰洩漏，所有授權可信度崩潰。
技術挑戰：確保私鑰不落地、可審計、可輪替。
影響範圍：大規模偽造授權、品牌與法務風險。
複雜度評級：高

### Root Cause Analysis
直接原因：
1. 私鑰存於檔案/原始碼庫。
2. 未使用 HSM 或雲端 KMS。
3. 無簽章審計與輪替機制。
深層原因：
- 架構：未將簽章視為關鍵服務（Signing Service）。
- 技術：缺 KID 與多金鑰支援。
- 流程：人員權限與 M-of-N 缺失。

### Solution Design
解決策略：導入 HSM/雲端 Key Vault，建立「簽章服務」對外只提供 Sign/Verify API（Verify 可在客戶端用公鑰）；實施 KID 與輪替計畫，簽章操作皆被審計。

實施步驟：
1. 導入 KMS/HSM
- 實作細節：私鑰僅存在 HSM；應用以 API 請求簽章。
- 所需資源：Azure Key Vault/HSM
- 預估時間：3-5 天
2. KID 與輪替
- 實作細節：授權/Token 帶 kid；信任庫多公鑰並行。
- 所需資源：版本管理
- 預估時間：2 天

關鍵程式碼/設定：
```csharp
// 以 Azure Key Vault 簽章
var crypto = new CryptographyClient(new Uri(keyId), new DefaultAzureCredential());
var signRes = await crypto.SignDataAsync(SignatureAlgorithm.RS256, data);
var signature = signRes.Signature;
```

實際案例：原廠每 6 個月輪替金鑰，授權帶 kid，產品內信任庫同時包含新/舊公鑰。
實作環境：Azure Key Vault/HSM、.NET
實測數據：
改善前：私鑰散佈、不可審計
改善後：私鑰不落地、可追蹤
改善幅度：私鑰外洩風險大幅降低

Learning Points
- KMS/HSM 與簽章服務化
- KID/輪替與信任庫
- 審計與合規
技能要求：
- 必備：雲端金鑰服務、簽章 API
- 進階：合規與審計
延伸思考：
- 緊急撤換（見 Case #14、#12）
- 多區容災
Practice Exercise
- 基礎：以 KV 完成一次簽章（30 分）
- 進階：加入 kid 與信任庫驗證（2 小時）
- 專案：建立簽章微服務（8 小時）
Assessment Criteria
- 功能：私鑰不落地、簽章可用
- 品質：錯誤/重試/審計
- 效能：簽章延遲可控
- 創新：藍綠輪替

----------------------------------------

## Case #5: 防設定檔篡改（以授權取代配置開關）

### Problem Statement
業務場景：整合商熟悉設定檔/程式碼，若功能以配置開關控制，易被直接開啟。
技術挑戰：在保留配置彈性的基礎上，杜絕未授權啟用。
影響範圍：非法啟用、售後風險。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 功能開關存在 appsettings/DB。
2. 無授權層與配置層隔離。
3. 沒有完整性驗證。
深層原因：
- 架構：缺少授權 Gate 層。
- 技術：未對配置敏感值做簽章或忽略策略。
- 流程：缺審核/審計。

### Solution Design
解決策略：功能啟用以「授權」為單一可信來源（SoT），配置檔中同名開關視為無效或唯讀；必要時對配置檔做簽章/校驗，或將敏感配置遷移至安全儲存。

實施步驟：
1. 導入 FeatureGate
- 實作細節：所有功能入口都依 ILicenseService.QueryFeature()
- 所需資源：DI/Service
- 預估時間：1 天
2. 配置保護
- 實作細節：敏感配置簽章，或轉存 KeyVault
- 所需資源：KV/簽章工具
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
public interface IFeatureGate { bool Enabled(string feature); }
public class LicenseFeatureGate : IFeatureGate
{
    private readonly LicensePayload _lp;
    public bool Enabled(string f) => _lp.Features.Contains(f);
}
```

實際案例：即使整合商修改 appsettings 中某功能=true，因入口檢查走 LicenseFeatureGate，仍無法啟用。
實作環境：.NET、DI
實測數據：
改善前：配置改動可啟用功能
改善後：以授權為準，配置無效
改善幅度：未授權啟用=0

Learning Points
- 單一可信來源（SoT）
- 授權 Gate 與配置分層
- 配置完整性保護
技能要求：
- 必備：DI、設定管理
- 進階：簽章與 KeyVault 整合
延伸思考：
- DX：屬性/中介層自動檢查（見 Case #8）
Practice Exercise
- 基礎：介面化 FeatureGate（30 分）
- 進階：對 appsettings 做簽章校驗（2 小時）
- 專案：功能旗標與授權整合（8 小時）
Assessment Criteria
- 功能：所有入口走 Gate
- 品質：單元測試覆蓋
- 效能：常數時間檢查
- 創新：Rule-based Gate

----------------------------------------

## Case #6: 環境綁定（Hardware/Environment Binding）

### Problem Statement
業務場景：授權檔被複製到其他機器/客戶後仍可使用。
技術挑戰：離線狀態下如何可靠綁定硬體/環境識別。
影響範圍：授權濫用與收益流失。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 授權未含 hardwareId。
2. 指紋易變或不穩定。
3. 綁定策略不可調。
深層原因：
- 架構：未定義指紋來源與降級策略。
- 技術：蒐集多因子、容忍部分變動不足。
- 流程：換機/維護流程缺失。

### Solution Design
解決策略：硬體指紋取多來源（CPU/MAC/OS/Domain），以穩定可重現策略產生 hardwareId，授權中綁定並驗證；提供容忍度與換機流程。

實施步驟：
1. 指紋模型
- 實作細節：收集多項，排序、正規化、Hash
- 所需資源：系統 API
- 預估時間：2 天
2. 綁定驗證與容錯
- 實作細節：容忍少量變動（權重）
- 所需資源：策略設定
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
string GetHardwareId()
{
    var parts = new[]{
        GetCpuId(), GetPrimaryMac(), GetMachineName(), GetDomainName()
    }.Where(x=>!string.IsNullOrEmpty(x)).OrderBy(x=>x);
    var bytes = System.Text.Encoding.UTF8.GetBytes(string.Join("|", parts));
    return Convert.ToHexString(SHA256.HashData(bytes));
}
```

實際案例：Service B 授權綁定於其資料中心伺服器群特徵，複製至 C 即失效。
實作環境：.NET、系統資訊 API
實測數據：
改善前：授權可隨意複製
改善後：跨機不可用
改善幅度：未授權複製成功率降至 0

Learning Points
- 指紋設計與穩定性
- Hash 與正規化
- 維護/換機流程
技能要求：
- 必備：系統資訊存取、Hash
- 進階：權重/容忍策略
延伸思考：
- 與時間回撥偵測合用（Case #18）
Practice Exercise
- 基礎：實作 GetHardwareId（30 分）
- 進階：設計容忍度策略（2 小時）
- 專案：換機授權轉移工具（8 小時）
Assessment Criteria
- 功能：穩定且可重現
- 品質：跨版本穩定
- 效能：計算<5ms
- 創新：多因子融合

----------------------------------------

## Case #7: 授權格式版本化與可擴充性

### Problem Statement
業務場景：未來持續新增授權項目與屬性，需兼顧舊版相容。
技術挑戰：格式演進、向後相容、開發者體驗。
影響範圍：升級成本與風險。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 硬編碼欄位，加入新項目需大改。
2. 無 version 與未知欄位策略。
3. 沒有 schema/契約。
深層原因：
- 架構：無明確契約治理。
- 技術：序列化策略缺乏。
- 流程：變更管理與文件不足。

### Solution Design
解決策略：JSON 授權 payload 加入 version；未知欄位忽略（forward compatibility）；核心欄位固定，擴充欄位使用字典；提供 JSON Schema 與契約測試。

實施步驟：
1. 模型調整
- 實作細節：新增 Version 與 Extensions: Dictionary<string,object>
- 所需資源：JSON Schema
- 預估時間：1 天
2. 契約測試
- 實作細節：對舊檔案做回歸測試
- 所需資源：CI/測試套件
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public class LicenseModel {
  public string Version {get;set;} = "1.0";
  public string TenantId {get;set;} = "";
  public string[] Features {get;set;} = Array.Empty<string>();
  public Dictionary<string, object> Extensions {get;set;} = new();
}
```

實際案例：新增「seatLimit」擴充欄位不影響舊版驗證器。
實作環境：.NET、System.Text.Json
實測數據：
改善前：加欄位需同步升級所有產品
改善後：擴充不破壞舊版
改善幅度：功能交付速度提升（內部基準）

Learning Points
- 契約治理與版本化
- Forward/Backward compatibility
- JSON Schema 與測試
技能要求：
- 必備：序列化/反序列化
- 進階：契約測試/Schema 驗證
延伸思考：
- kid 與演算法切換（Case #12、#13）
Practice Exercise
- 基礎：加入 Extensions 支援（30 分）
- 進階：Schema 驗證工具（2 小時）
- 專案：契約測試流水線（8 小時）
Assessment Criteria
- 功能：忽略未知欄位
- 品質：Schema 與測試齊備
- 效能：序列化穩定
- 創新：擴充模式設計

----------------------------------------

## Case #8: DX 改善：Fluent API / Attribute 授權檢查

### Problem Statement
業務場景：開發者常需在多處手動撰寫授權檢查，易散亂、可讀性差。
技術挑戰：提供直覺、一致、可測試的 DX。
影響範圍：開發效率、缺陷率。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 檢查散落在控制器/服務。
2. 無中心化 Gate/Attribute 支援。
3. 文檔不足、易誤用。
深層原因：
- 架構：缺授權抽象層。
- 技術：缺 AOP/Filter
- 流程：DX 指南缺失。

### Solution Design
解決策略：提供 IFeatureGate 與 [RequiresFeature] 屬性，於中介層/Filter 統一注入授權檢查；另提供 Fluent API（Feature("X").Require()）以應對服務層檢查。

實施步驟：
1. 屬性與 Filter
- 實作細節：ActionFilter 於執行前檢查
- 所需資源：ASP.NET Core Filters
- 預估時間：1 天
2. Fluent API
- 實作細節：鏈式檢查與例外處理
- 所需資源：擴充方法
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
[AttributeUsage(AttributeTargets.Method)]
public class RequiresFeatureAttribute : Attribute { public string Name; public RequiresFeatureAttribute(string n)=>Name=n; }

public class FeatureFilter : IAsyncActionFilter {
  private readonly IFeatureGate _gate;
  public FeatureFilter(IFeatureGate gate)=>_gate=gate;
  public async Task OnActionExecutionAsync(ActionExecutingContext ctx, ActionExecutionDelegate next){
    var rf = ctx.ActionDescriptor.EndpointMetadata.OfType<RequiresFeatureAttribute>().FirstOrDefault();
    if(rf!=null && !_gate.Enabled(rf.Name)) { ctx.Result=new ForbidResult(); return; }
    await next();
  }
}
```

實際案例：Controller 方法以屬性標註所需功能，統一授權檢查。
實作環境：ASP.NET Core
實測數據：
改善前：每處手寫檢查
改善後：集中化/可測試
改善幅度：授權相關缺陷率降低（內部基準）

Learning Points
- DX 與一致性
- Filter/AOP
- 測試性與可維護性
技能要求：
- 必備：ASP.NET Core Filters、DI
- 進階：AOP 與錯誤架構
延伸思考：
- 搭配 Scope 授權（Case #2）
Practice Exercise
- 基礎：實作 FeatureFilter（30 分）
- 進階：建立 Fluent API（2 小時）
- 專案：DX 指南與範本（8 小時）
Assessment Criteria
- 功能：屬性生效
- 品質：可測試/可維護
- 效能：Filter 開銷極低
- 創新：Fluent 語法

----------------------------------------

## Case #9: 離線授權發佈與匯入流程

### Problem Statement
業務場景：客戶在封閉網路，原廠需安全地發佈授權並由現場人員匯入。
技術挑戰：傳輸中不可被篡改、匯入步驟直覺防錯。
影響範圍：安裝失敗、停機風險。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 手動複製檔案易遺漏/誤版。
2. 無完整性校驗。
3. 匯入工具體驗差。
深層原因：
- 架構：缺標準化交付包。
- 技術：未加校驗碼/簽章。
- 流程：缺驗收清單與回報。

### Solution Design
解決策略：定義「授權包」格式（license.json、checksum.txt、readme、版本）；匯入工具自動驗章、校驗、備份舊檔與可回滾；產生安裝報告。

實施步驟：
1. 打包與簽章
- 實作細節：生成 SHA256 校驗與簽章
- 所需資源：打包腳本
- 預估時間：1 天
2. 匯入工具
- 實作細節：GUI/CLI、日志、回滾
- 所需資源：桌面/CLI 技術
- 預估時間：2-3 天

關鍵程式碼/設定：
```csharp
bool VerifyChecksum(string file, string expectedHex)
{
    using var fs = File.OpenRead(file);
    var hash = SHA256.HashData(fs);
    return Convert.ToHexString(hash).Equals(expectedHex, StringComparison.OrdinalIgnoreCase);
}
```

實際案例：現場人員以 USB 帶入授權包，工具自動驗校與備份。
實作環境：.NET、CLI/WinForms/WPF
實測數據：
改善前：安裝錯誤率高
改善後：自動驗校/報告
改善幅度：安裝失敗率顯著下降

Learning Points
- 交付包標準化
- 校驗碼與回滾
- 作業流程與審計
技能要求：
- 必備：檔案操作、Hash
- 進階：UI/UX 與日志
延伸思考：
- 線上激活改離線（補登）
Practice Exercise
- 基礎：計算/驗證 checksum（30 分）
- 進階：實作回滾（2 小時）
- 專案：完整匯入工具（8 小時）
Assessment Criteria
- 功能：驗章+校驗+回滾
- 品質：防呆/報告
- 效能：大檔處理
- 創新：自動偵測版本

----------------------------------------

## Case #10: API Key 速率限制與零信任邊界

### Problem Statement
業務場景：即使有 API Key，仍需要防濫用與 DDoS 風險；需按 Key/租戶限速。
技術挑戰：在內網中有效限速與隔離。
影響範圍：可用性、資源爭奪。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無 per-key rate limit。
2. 無 IP 限制或網段白名單。
3. 無熔斷/退流控。
深層原因：
- 架構：零信任邊界未建立。
- 技術：RateLimiter 缺乏。
- 流程：告警與黑名單機制不足。

### Solution Design
解決策略：以 API Key 為維度建立令牌桶/固定窗口限速；配置白名單；超限回 429 並記錄。

實施步驟：
1. 引入 RateLimiter
- 實作細節：ASP.NET Core RateLimiter 中介層
- 所需資源：Microsoft.AspNetCore.RateLimiting
- 預估時間：1 天
2. 白名單/黑名單
- 實作細節：動態更新
- 所需資源：設定/資料庫
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
builder.Services.AddRateLimiter(_ => _.AddPolicy("PerKey", ctx =>
{
    var key = ctx.Request.Headers["X-Api-Key"].ToString();
    return RateLimitPartition.GetTokenBucketLimiter(key,
      _=> new TokenBucketRateLimiterOptions{ TokenLimit=100, TokensPerPeriod=100, ReplenishmentPeriod=TimeSpan.FromMinutes(1), AutoReplenishment=true });
}));
app.UseRateLimiter();
```

實際案例：每個租戶每分鐘 100 次，超限立刻 429。
實作環境：ASP.NET Core 7/8 RateLimiter
實測數據：
改善前：高峰時互相影響
改善後：限速與隔離
改善幅度：高峰錯誤率下降

Learning Points
- Rate limiting 策略
- 零信任邊界
- 告警與黑名單
技能要求：
- 必備：中介層、限速原理
- 進階：動態策略
延伸思考：
- 與 Scope（Case #2）聯動
Practice Exercise
- 基礎：設定 per-key 限速（30 分）
- 進階：動態配置策略（2 小時）
- 專案：限速+告警+黑名單（8 小時）
Assessment Criteria
- 功能：限速正確
- 品質：可配置/可觀測
- 效能：低額外開銷
- 創新：自適應限速

----------------------------------------

## Case #11: 審計與偵測（篡改/攻擊跡象可觀測）

### Problem Statement
業務場景：需追蹤授權驗證失敗、時間回撥、硬體變動等可疑事件。
技術挑戰：在封閉網路中仍要可觀測與可追蹤。
影響範圍：合規、法務、事件處理。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無結構化審計日誌。
2. 錯誤類型未分類。
3. 無儀表板/警示。
深層原因：
- 架構：可觀測性不足。
- 技術：缺事件模型。
- 流程：無通報 SLA。

### Solution Design
解決策略：定義審計事件表（驗章失敗/過期/硬體不符/回撥/多次攻擊）；結構化輸出；彙整到本地 SIEM 或上傳雲端（可選）。

實施步驟：
1. 事件模型與記錄
- 實作細節：EventId、嚴重度、租戶/主機標識
- 所需資源：Logging/Serilog
- 預估時間：1 天
2. 儀表板與告警
- 實作細節：本地儀表板+Email
- 所需資源：Grafana/ELK
- 預估時間：2 天

關鍵程式碼/設定：
```csharp
logger.LogWarning("LicenseVerifyFailed {TenantId} {Reason} {Host}",
    tenantId, reason, Environment.MachineName);
```

實際案例：多次硬體不符與回撥被記錄並告警。
實作環境：.NET Logging、ELK/Grafana（可選）
實測數據：
改善前：黑盒無可觀測
改善後：可審計、可追蹤
改善幅度：MTTD 顯著降低

Learning Points
- 安全事件可觀測性
- 結構化日誌與告警
- 審計合規
技能要求：
- 必備：Logging、指標
- 進階：SIEM 整合
延伸思考：
- 離線暫存後批次上傳
Practice Exercise
- 基礎：事件記錄（30 分）
- 進階：告警策略（2 小時）
- 專案：安全儀表板（8 小時）
Assessment Criteria
- 功能：事件完整記錄
- 品質：分類清晰
- 效能：低開銷
- 創新：攻擊跡象偵測

----------------------------------------

## Case #12: 金鑰輪替與信任庫（多公鑰/KID）

### Problem Statement
業務場景：需在不影響已部署客戶的前提下輪替簽章金鑰。
技術挑戰：多把公鑰並行、授權載明 kid、信任庫可更新且具完整性。
影響範圍：連續性與安全性。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 產品僅內嵌單一公鑰。
2. 授權不含 kid。
3. 信任庫更新不可驗證。
深層原因：
- 架構：輪替未納入設計。
- 技術：缺 kid 對應。
- 流程：更新與回滾不明確。

### Solution Design
解決策略：授權/Token 必含 kid；產品內部維護公鑰信任庫（多把），可離線更新且附完整性簽章；驗章時按 kid 選擇公鑰。

實施步驟：
1. kid 支援
- 實作細節：payload/kid
- 所需資源：簽章服務
- 預估時間：0.5 天
2. 信任庫
- 實作細節：多把公鑰 JSON + 簽章
- 所需資源：更新工具
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
RSA GetRsaByKid(string kid, TrustStore store)
{
    var pem = store.Keys.First(k=>k.Kid==kid).Pem;
    var rsa = RSA.Create(); rsa.ImportFromPem(pem); return rsa;
}
```

實際案例：原廠發新授權以新 kid 簽發，舊授權仍可驗，過渡期後移除舊公鑰。
實作環境：.NET、PEM Key
實測數據：
改善前：輪替需重佈產品
改善後：信任庫離線更新即可
改善幅度：輪替停機=0

Learning Points
- kid 與多公鑰並行
- 信任庫完整性
- 輪替策略
技能要求：
- 必備：PEM、RSA/ECDSA
- 進階：更新與回滾
延伸思考：
- 產品自身完整性（Case #16）
Practice Exercise
- 基礎：依 kid 取公鑰（30 分）
- 進階：信任庫簽章驗證（2 小時）
- 專案：輪替發佈流程（8 小時）
Assessment Criteria
- 功能：多鍵驗章
- 品質：更新可驗/可回滾
- 效能：查找常數時間
- 創新：過渡窗口設計

----------------------------------------

## Case #13: 演算法選型（RSA vs ECDSA）與強度/大小折衷

### Problem Statement
業務場景：授權碼需短小易傳、驗章快且安全。
技術挑戰：選擇合適的簽章演算法與金鑰長度。
影響範圍：DX、效能與安全。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 使用過長 RSA 金鑰導致授權碼過大。
2. 驗章成本高。
3. 缺少標準化格式（如 JWS）。
深層原因：
- 架構：無演算法抽象層。
- 技術：對曲線簽章不熟悉。
- 流程：未定期評估安全等級。

### Solution Design
解決策略：採 ECDSA P-256（或 Ed25519）取代 RSA 2048 作簽章，縮小簽章大小並提升驗章效能；抽象簽章介面便於替換。

實施步驟：
1. 策略/抽象
- 實作細節：ISigner 介面；RSA/ECDSA 實作
- 所需資源：Crypto API
- 預估時間：1 天
2. 切換/測試
- 實作細節：效能與相容性測試
- 所需資源：基準測試
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 驗證 ECDSA P-256
bool VerifyEcdsa(byte[] data, byte[] sig, ECDsa ecdsa)
    => ecdsa.VerifyData(data, sig, HashAlgorithmName.SHA256);
```

實際案例：授權檔大小減少、驗章更快，適合透過 QR 或短字串傳輸。
實作環境：.NET、ECDsa
實測數據：
改善前：RSA 簽章較大
改善後：ECDSA 簽章更小更快
改善幅度：大小/延遲顯著改善（內部基準）

Learning Points
- RSA vs ECDSA 折衷
- 抽象與熱插拔
- 基準測試
技能要求：
- 必備：Crypto API
- 進階：基準設計
延伸思考：
- Ed25519 支援
Practice Exercise
- 基礎：ECDSA 驗章（30 分）
- 進階：ISigner 介面化（2 小時）
- 專案：切換演算法 POC（8 小時）
Assessment Criteria
- 功能：雙演算法可用
- 品質：抽象清晰
- 效能：顯著改善
- 創新：最小化授權碼

----------------------------------------

## Case #14: 撤銷與有效期策略（短期授權/離線撤銷）

### Problem Statement
業務場景：離線環境無法即時撤銷已簽發的授權。
技術挑戰：如何降低風險窗口。
影響範圍：安全與合規。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 長期有效授權難以撤銷。
2. 無 CRL/OCSP 類比機制。
3. 無短期換證流程。
深層原因：
- 架構：未設計撤銷策略。
- 技術：依賴線上清單。
- 流程：換證頻率過低。

### Solution Design
解決策略：採短期授權（例如 30 天），配合續期工具離線更新；重大事件時透過信任庫更新黑名單或停用某 kid（與 Case #12/16 搭配）。

實施步驟：
1. 短期授權
- 實作細節：發放與提醒續期
- 所需資源：排程/通知
- 預估時間：1 天
2. 黑名單/停用 kid
- 實作細節：信任庫更新時禁用特定 kid
- 所需資源：更新工具
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
bool IsRevoked(string kid, TrustStore store) => store.RevokedKids.Contains(kid);
```

實際案例：某客戶授權遭疑涉外洩，透過更新信任庫撤用該 kid。
實作環境：.NET
實測數據：
改善前：撤銷不可行
改善後：可在 30 天內風險收斂
改善幅度：曝險期從 1 年降至 30 天

Learning Points
- 短期授權策略
- 黑名單與 kid 停用
- 更新與通知流程
技能要求：
- 必備：排程/通知
- 進階：信任庫治理
延伸思考：
- 結合時間回撥偵測（Case #18）
Practice Exercise
- 基礎：檢查 kid 是否撤銷（30 分）
- 進階：短期續期提醒（2 小時）
- 專案：撤銷/續期端到端（8 小時）
Assessment Criteria
- 功能：撤銷可用
- 品質：流程清晰
- 效能：更新迅速
- 創新：短期授權治理

----------------------------------------

## Case #15: 測試策略（過期/篡改/離線/硬體變更）

### Problem Statement
業務場景：授權驗證邏輯複雜，需完整測試。
技術挑戰：如何建立可重現、可擴充的測試套件。
影響範圍：品質與回歸風險。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 缺少測試樣本（合法/過期/篡改）。
2. 無時間/硬體模擬。
3. 缺整合測試與回歸。
深層原因：
- 架構：可測性不足。
- 技術：測試替身不足。
- 流程：CI/CD 未納入。

### Solution Design
解決策略：建立「金樣本」授權檔庫；提供時間/硬體偽裝層；端到端整合測試與 fuzz 測試；CI 報告。

實施步驟：
1. 單元/契約測試
- 實作細節：各種情境樣本
- 所需資源：xUnit/NUnit
- 預估時間：2 天
2. 整合/端到端
- 實作細節：啟動驗章、API 驗證
- 所需資源：測試容器
- 預估時間：2 天

關鍵程式碼/設定：
```csharp
[Fact]
public void Expired_License_Should_Fail()
{
    var now = DateTimeOffset.UtcNow;
    var lic = new LicensePayload(..., Exp: now.AddDays(-1), ...);
    Assert.False(Verifier.IsValid(lic));
}
```

實際案例：PR 需通過 50+ 授權情境測試才可合併。
實作環境：xUnit、.NET
實測數據：
改善前：回歸頻繁
改善後：缺陷顯著下降
改善幅度：授權相關缺陷下降

Learning Points
- 金樣本與契約測試
- 偽裝時間/硬體
- CI 報告
技能要求：
- 必備：單元/整合測試
- 進階：測試替身
延伸思考：
- 模糊測試（Fuzz）
Practice Exercise
- 基礎：過期測試（30 分）
- 進階：硬體不符測試（2 小時）
- 專案：CI 測試矩陣（8 小時）
Assessment Criteria
- 功能：覆蓋關鍵場景
- 品質：穩定重現
- 效能：測試時間可控
- 創新：自動生成樣本

----------------------------------------

## Case #16: 產品完整性與公鑰保護（信任錨不被替換）

### Problem Statement
業務場景：攻擊者若能替換產品內嵌的公鑰或信任庫，即可接受偽造授權。
技術挑戰：如何確保驗章信任錨不被篡改。
影響範圍：全盤信任崩潰。
複雜度評級：高

### Root Cause Analysis
直接原因：
1. 公鑰硬編碼但可被動態替換。
2. 信任庫未做完整性校驗。
3. 無程式碼/組件完整性檢查。
深層原因：
- 架構：缺信任錨保護。
- 技術：缺碼簽章與校驗。
- 流程：更新散落、缺驗證。

### Solution Design
解決策略：對信任庫簽章（原廠碼簽或獨立簽章）；啟動時校驗信任庫/公鑰哈希；若可行，導入組件碼簽與防調試；異常時進入安全模式。

實施步驟：
1. 信任庫簽章
- 實作細節：truststore.json.sig
- 所需資源：簽章工具
- 預估時間：1 天
2. 啟動校驗
- 實作細節：比對公鑰哈希
- 所需資源：Hash API
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
bool VerifyTrustStore(byte[] storeBytes, byte[] sig, RSA codeSignPub)
    => codeSignPub.VerifyData(storeBytes, sig, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);

bool CheckKeyHash(RSA rsa, string expectedHex)
{
    var hash = Convert.ToHexString(SHA256.HashData(rsa.ExportSubjectPublicKeyInfo()));
    return hash.Equals(expectedHex, StringComparison.OrdinalIgnoreCase);
}
```

實際案例：啟動時若信任庫簽章不符，產品轉安全模式並告警。
實作環境：.NET、碼簽工具
實測數據：
改善前：公鑰可被替換
改善後：替換即被攔阻
改善幅度：竄改成功率=0（內部基準）

Learning Points
- 信任錨與碼簽
- 啟動完整性校驗
- 安全模式降級
技能要求：
- 必備：簽章/Hash
- 進階：碼簽與反篡改
延伸思考：
- 與金鑰輪替配合（Case #12）
Practice Exercise
- 基礎：驗證 truststore 簽章（30 分）
- 進階：公鑰哈希校驗（2 小時）
- 專案：安全模式與告警（8 小時）
Assessment Criteria
- 功能：篡改可偵測
- 品質：錯誤處置妥當
- 效能：啟動開銷小
- 創新：多重校驗

----------------------------------------

案例分類
1) 按難度分類
- 入門級（適合初學者）
  - Case #1 離線授權驗證
  - Case #2 API KEY 與 Scopes
  - Case #5 防設定檔篡改
  - Case #7 格式版本化
- 中級（需要一定基礎）
  - Case #3 授權期限/續約
  - Case #6 環境綁定
  - Case #8 DX 改善
  - Case #9 離線發佈/匯入
  - Case #10 速率限制
  - Case #11 審計與偵測
  - Case #12 金鑰輪替/信任庫
  - Case #13 演算法選型
  - Case #15 測試策略
- 高級（需要深厚經驗）
  - Case #4 金鑰管理/HSM
  - Case #14 撤銷策略（短期授權/黑名單）
  - Case #16 產品完整性/信任錨

2) 按技術領域分類
- 架構設計類
  - Case #1, #2, #3, #4, #7, #12, #14, #16
- 效能優化類
  - Case #10, #13
- 整合開發類
  - Case #8, #9, #12
- 除錯診斷類
  - Case #11, #15
- 安全防護類
  - Case #1, #2, #4, #5, #6, #12, #14, #16

3) 按學習目標分類
- 概念理解型
  - Case #1, #2, #3, #7, #13, #14
- 技能練習型
  - Case #5, #6, #8, #9, #10, #11, #12, #15, #16
- 問題解決型
  - Case #3, #4, #5, #6, #10, #11, #12, #16
- 創新應用型
  - Case #8, #12, #13, #16

案例關聯圖（學習路徑建議）
- 入門順序（基礎信任與核心概念）
  1) Case #1 離線授權驗證
  2) Case #2 API KEY 與 Scopes
  3) Case #3 授權期限/續約
  4) Case #5 防設定檔篡改
  5) Case #7 格式版本化
- 中級強化（可落地與可運營）
  6) Case #8 DX 改善（在 #1/#2 基礎上提升 DX）
  7) Case #6 環境綁定（需先懂 #1）
  8) Case #9 離線發佈/匯入（依賴 #1/#3）
  9) Case #10 速率限制（依賴 #2）
  10) Case #11 審計與偵測（覆蓋 #1-#10）
  11) Case #15 測試策略（總結 #1-#11）
- 高級治理（安全營運與長期維護）
  12) Case #12 金鑰輪替/信任庫（需懂 #1、#3、#7）
  13) Case #13 演算法選型（可與 #12 並行）
  14) Case #4 金鑰管理/HSM（高度依賴 #12）
  15) Case #14 撤銷策略（短期授權/黑名單，依賴 #12）
  16) Case #16 產品完整性/信任錨（壓軸，保障整體信任鏈）

依賴關係摘要
- #1 為整體根基；#2、#3 緊隨其後
- #8（DX）建立在 #1/#2 成果之上
- #12（輪替）依賴 #1/#3/#7；#4、#14 建立在 #12 之上
- #16（信任錨）與 #12 形成完善的供應鏈信任閉環

完整學習路徑建議
- 先打好信任與授權核心（#1~#3、#5、#7）
- 再強化開發體驗與現場可操作性（#8、#6、#9、#10、#11、#15）
- 最後完成長期安全治理閉環（#12、#13、#4、#14、#16）

以上 16 個案例可直接用於教學、專案練習與能力評估，並完整覆蓋文章情境中的關鍵難題：離線授權、API KEY、安全強度與擴充性、以及開發者體驗（DX）。