## Case #1: 以 RBAC 將「使用者×功能」組合降維

### Problem Statement（問題陳述）
業務場景：B2B 銷售系統有 20 位內部使用者與 50 個受控功能。老闆要確保助理可維護單筆訂單，主管可查閱全域報表，系統管理員僅可調整安全設定。原始設計逐使用者逐功能控制，造成設定成本暴增且容易出錯。

技術挑戰：逐點控管產生 1000 個組合，規模成長時難以維護與驗證一致性。

影響範圍：授權配置易錯、審核困難、不可追溯，導致越權或不足權限的風險提升。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 授權維度過細：以「使用者×功能」維度設定，導致組合爆炸。
2. 缺少角色抽象：未將業務職責歸納為角色與權限映射。
3. 缺乏可驗證的結構：沒有可推導與驗證的 Role-Permission-Operation 關係。

深層原因：
- 架構層面：缺少統一的授權模型與對照表（R/P/PA/O）。
- 技術層面：以零散布林值、旗標維護，缺少標準介面。
- 流程層面：授權規格未視為產品規格的一部分，未在設計期定稿。

### Solution Design（解決方案設計）
解決策略：採用 RBAC，將 20×50 的組合降至 3 角色×5 權限×N 作業，建立「角色→權限」、「作業→權限」兩張映射表，僅在登入載入「使用者→角色」，後續校驗以靜態配置與程式內映射完成，并以單元測試驗證 Role×Operation 推導結果。

實施步驟：
1. 角色與權限定義
- 實作細節：定義 sales-manager、sales-operator、system-admin 與 CRUD/Query 權限。
- 所需資源：產品規格會議、架構師審核、維度拆解工作坊。
- 預估時間：1-2 天

2. 建立映射表與程式碼落地
- 實作細節：以程式/設定檔維護 PA（Role→Permissions）與 OA（Operation→Permissions）。
- 所需資源：C# 專案、設定管理、Code Review。
- 預估時間：2-3 天

3. 驗證與自動化測試
- 實作細節：撰寫推導 Role×Operation 的測試，對照預期結果。
- 所需資源：xUnit/NUnit、CI。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 定義角色與權限
public enum Role { SystemAdmin, SalesManager, SalesOperator }
public enum Perm { OrderCreate, OrderRead, OrderUpdate, OrderDelete, OrdersQuery }

// Role -> Permissions
var rolePerms = new Dictionary<Role, HashSet<Perm>>
{
  [Role.SalesManager] = new() { Perm.OrderRead, Perm.OrdersQuery },
  [Role.SalesOperator] = new() { Perm.OrderCreate, Perm.OrderRead, Perm.OrderUpdate, Perm.OrderDelete },
  [Role.SystemAdmin] = new() { /* 僅安全設定，避免業務資料權限 */ }
};

// Operation -> Permissions
public record Operation(string Name, Perm[] Required);
var operations = new Dictionary<string, Operation>
{
  ["Sales_Report"] = new("Sales_Report", new[]{ Perm.OrdersQuery }),
  ["Orders_Create"] = new("Orders_Create", new[]{ Perm.OrderCreate, Perm.OrderRead, Perm.OrderUpdate }),
  // ...
};
```

實際案例：文中銷售系統，將 20 人×50 功能（1000 組）降維為 3 角色×5 權限（15 組）。

實作環境：.NET/C#（任何版本皆可），設定檔或硬編碼均可。

實測數據：
改善前：需維護 1000 組合。
改善後：需維護 15 組合。
改善幅度：98.5% 複雜度下降（組合數）。

Learning Points（學習要點）
核心知識點：
- RBAC 的角色/權限/作業拆分法
- PA 與 OA 映射的落地方式
- 減乘為加的降維思維（組合爆炸治理）

技能要求：
- 必備技能：基本物件建模、字典/集合操作、單元測試
- 進階技能：抽象化維度、規格對齊與測試驗證

延伸思考：
- 可擴展至多租戶與產品線（增加 Client/Contract 維度）。
- 限制：RBAC 對資料層級限制較弱，需配合 ABAC/資料過濾。
- 優化：將映射由硬編碼抽出到可版本管理的配置與測試。

Practice Exercise（練習題）
基礎練習：定義 3 角色與 5 權限，完成兩張映射表。
進階練習：撰寫推導 Role×Operation 的自動驗證測試。
專案練習：實作一個小型後台，登入後依角色顯示不同選單。

Assessment Criteria（評估標準）
- 功能完整性（40%）：Role/Perm/Operation 與映射可正確推導
- 程式碼品質（30%）：結構清晰、測試齊全、命名一致
- 效能優化（20%）：登入後零 DB 查詢的權限檢查
- 創新性（10%）：降維設計與驗證自動化方案


## Case #2: 作業-權限錯配導致的越權（批次匯入案例）

### Problem Statement（問題陳述）
業務場景：業務專員需可批次匯入訂單以提升效率，但不得查詢或匯出所有訂單，避免外洩業績與客戶清單。設計上若將「批次匯入」綁定為包含廣域查詢，易造成錯配而越權。

技術挑戰：作業（Operation）與權限（Permission）拆解錯誤，造成功能耦合與越權路徑。

影響範圍：專員能藉匯入流程間接取得不該看到的資料。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 將「批次匯入」實作為「匯入=查詢+寫入」，造成查詢越權。
2. 權限最小單位定義不清，作業與權限混雜。
3. 缺乏跨作業的權限一致性驗證。

深層原因：
- 架構層面：缺少 Operation→Permission 的嚴格映射與審核。
- 技術層面：在應用層散落權限檢查，難以全局一致。
- 流程層面：產品/工程對越權風險未建立測試防護。

### Solution Design（解決方案設計）
解決策略：將批次匯入 Operation 僅綁定「order-create」與必要的單筆讀取（必要驗證內聚於領域服務），禁止廣域查詢「orders-query」。所有越權查詢需求改由領域層內封裝的驗證 API 完成，不暴露資料。

實施步驟：
1. 重新定義 Operation→Permission
- 實作細節：Orders_BatchImport 僅要求 {OrderCreate}。
- 所需資源：設計審查、PO 同步。
- 預估時間：0.5-1 天

2. 封裝領域驗證
- 實作細節：在 Domain Service 中封裝必要的重複檢查（如重複單號），不開放廣域查詢。
- 所需資源：Domain Service、Repository 模式。
- 預估時間：1-2 天

3. 單元測試與攻擊路徑測試
- 實作細節：驗證批次匯入流程無法取得全量資料。
- 所需資源：測試用例、CI。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Operation 定義
var operations = new Dictionary<string, Operation> {
  ["Orders_BatchImport"] = new("Orders_BatchImport", new[]{ Perm.OrderCreate })
};

// 領域服務內聚驗證（避免暴露廣域查詢）
public class OrderService
{
  public void Import(IEnumerable<OrderDto> rows, IPrincipal user)
  {
    // 僅針對單筆進行必要檢核（如唯一鍵），不提供全量查詢
    foreach (var dto in rows)
    {
      if (_repo.ExistsOrderNumber(dto.OrderNumber))
         throw new InvalidOperationException("Duplicated order number.");
      _repo.Create(dto, user);
    }
  }
}
```

實際案例：文中點出「批次處理若內含查詢」會造成設計漏洞。

實作環境：.NET/C#，Domain Service + Repository。

實測數據：
改善前：批次匯入隱含 OrdersQuery，專員可間接取得資料。
改善後：批次匯入僅含 Create，無法取得廣域資料。
改善幅度：越權路徑消除（0 未授權查詢）。

Learning Points（學習要點）
核心知識點：
- Operation 與 Permission 的耦合治理
- 領域層封裝驗證避免資料外洩
- 最小權限原則落地技巧

技能要求：
- 必備技能：RBAC 基礎、Domain Service 設計
- 進階技能：威脅建模、越權測試

延伸思考：
- 可與審計日誌（Case #17）結合，監控匯入操作。
- 限制：需補齊領域驗證以免需求外溢到應用層。
- 優化：以策略/規則引擎管理校驗邏輯。

Practice Exercise（練習題）
基礎練習：重構一個匯入作業，只綁定 Create 權限。
進階練習：撰寫單元測試，嘗試透過匯入路徑取得全量資料應被阻擋。
專案練習：設計一套匯入規則校驗服務並與 RBAC 整合。

Assessment Criteria（評估標準）
- 功能完整性（40%）：匯入能運作且無越權查詢
- 程式碼品質（30%）：分層清晰、職責內聚
- 效能優化（20%）：匯入校驗在可接受延遲內
- 創新性（10%）：提供可重用的驗證策略


## Case #3: 使用 IIdentity/IPrincipal 與 AuthorizeAttribute 的最小落地

### Problem Statement（問題陳述）
業務場景：Web 與工具（Console）並存的系統需一致的權限校驗。Web 端希望用標註簡化權限；工具端需程式碼中判斷角色。

技術挑戰：多執行環境（Web/Console）一致性與重用性。

影響範圍：分散的檢查易不一致、維護成本高。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 權限檢查散落各層，無統一機制。
2. Web/Console 使用不同判斷寫法，難以共用。
3. 未善用框架內建物件（IPrincipal、AuthorizeAttribute）。

深層原因：
- 架構層面：缺少共用授權契約。
- 技術層面：未依賴 HttpContext.User/Thread.CurrentPrincipal。
- 流程層面：缺少用法規範。

### Solution Design（解決方案設計）
解決策略：統一使用 IPrincipal 代表登入者，Console 透過 Thread.CurrentPrincipal，Web 透過 HttpContext.User，Controller 以 [Authorize(Roles="...")] 標註完成授權。

實施步驟：
1. 設定使用者主體
- 實作細節：登入成功後建立 ClaimsPrincipal/GenericPrincipal。
- 所需資源：登入流程、身分來源。
- 預估時間：0.5 天

2. Web 授權標註
- 實作細節：使用 [Authorize(Roles="manager")] 保護控制器或 Action。
- 所需資源：ASP.NET Core。
- 預估時間：0.5 天

3. Console 檢查統一
- 實作細節：在需要權限之處，以 Thread.CurrentPrincipal.IsInRole() 檢查。
- 所需資源：.NET runtime。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Console
var identity = new GenericIdentity("andrew");
Thread.CurrentPrincipal = new GenericPrincipal(identity, new[] { "manager" });
if (Thread.CurrentPrincipal.IsInRole("manager")) { /* 執行 */ }

// ASP.NET Core
[Authorize(Roles = "manager")]
public class ControlPanelController : Controller
{
    public IActionResult Sales_Report() => Content("query orders...");
}
```

實際案例：文中展示 Console 與 ASP.NET 的用法。

實作環境：.NET Framework/.NET Core、ASP.NET Core。

實測數據：
改善前：各處自寫檢查，重複且易錯。
改善後：以 IPrincipal 與 AuthorizeAttribute 一致化。
改善幅度：權限檢查重用率顯著提升（標註即用）。

Learning Points（學習要點）
核心知識點：
- IIdentity/IPrincipal/AuthorizeAttribute 的角色
- 框架支持的授權生命周期
- 一致性與重用的重要性

技能要求：
- 必備技能：ASP.NET Core 基礎、.NET 物件模型
- 進階技能：Claims 與 Cookie/OIDC 整合

延伸思考：
- 改以 Policy/Claims 做更細粒度控制。
- 限制：角色字串硬編碼可抽至常數與測試。
- 優化：集中使用自訂授權服務（見 Case #4）。

Practice Exercise（練習題）
基礎練習：為三個 Controller Action 各加一個角色標註。
進階練習：在 Console 中統一以 Thread.CurrentPrincipal 驗證。
專案練習：建立登入流程，完成 Web 與 Console 一致的授權體驗。

Assessment Criteria（評估標準）
- 功能完整性（40%）：授權生效、未授權可阻擋
- 程式碼品質（30%）：少重複、集中管理常數
- 效能優化（20%）：零額外 DB 查詢
- 創新性（10%）：可擴展到 Claims/Policy


## Case #4: 建立 ICustomAuthorization，統一授權入口

### Problem Statement（問題陳述）
業務場景：系統多處有權限判斷，若散落於 Controller/Service 容易不一致且難審計。需要一個統一授權入口，以支援測試與審計。

技術挑戰：將 Operation→Permissions 與 User（IPrincipal）串接，並可替換策略（RBAC/PBAC/ABAC）。

影響範圍：一致性、可測試性與審計能力。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無統一授權介面，難以替換/擴展。
2. 權限檢查與商業邏輯交織。
3. 無法集中記錄與審計。

深層原因：
- 架構層面：缺乏可插拔授權層。
- 技術層面：未抽象 Permission/Operation。
- 流程層面：未建立授權測試用例。

### Solution Design（解決方案設計）
解決策略：定義 ICustomAuthorization 與 ICustomOperation/Permission，將授權判斷集中至一服務，讓應用只呼叫 IsAuthorized(user, operation)，配合測試與審計裝飾器。

實施步驟：
1. 介面定義與映射
- 實作細節：建立 Permission/Operation 與 Role 的映射。
- 所需資源：C# 介面、集合。
- 預估時間：1 天

2. 實作 RBAC Authorization
- 實作細節：逐一檢查 operation.RequiredPermissions 是否由 user 的角色授與。
- 所需資源：IPrincipal、角色映射。
- 預估時間：1 天

3. 加入審計裝飾器（可選）
- 實作細節：外包裝記錄 allow/deny 與原因。
- 所需資源：Logger。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public interface ICustomPremission
{
  string Name { get; }
  bool IsGranted(IPrincipal user);
}

public interface ICustomOperation
{
  string Name { get; }
  IEnumerable<ICustomPremission> RequiredPermissions { get; }
}

public interface ICustomAuthorization
{
  bool IsAuthorized(IPrincipal user, ICustomOperation op);
}

public class RbacAuthorization : ICustomAuthorization
{
  public bool IsAuthorized(IPrincipal user, ICustomOperation op)
    => op.RequiredPermissions.All(p => p.IsGranted(user));
}
```

實際案例：文中定義 ICustomAuthorization 模型並以 RBAC 實作。

實作環境：.NET/C#。

實測數據：
改善前：權限判斷散落，難以覆蓋測試。
改善後：單一入口，可替換策略、可審計。
改善幅度：授權程式碼集中度 100%，覆測性大幅提升。

Learning Points（學習要點）
核心知識點：
- 授權層抽象的好處
- 以介面隔離策略（RBAC/ABAC/PBAC）
- 審計與測試友善設計

技能要求：
- 必備技能：介面設計、依賴注入
- 進階技能：AOP/Decorator、審計設計

延伸思考：
- 可加入快取與策略鏈。
- 限制：介面過度抽象需防止複雜化。
- 優化：與 Policy/Claims 整合。

Practice Exercise（練習題）
基礎練習：實作一個最小的 RbacAuthorization。
進階練習：加上審計裝飾器，記錄決策。
專案練習：用該服務保護三個模組（操作/報表/匯入）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：IsAuthorized 正確判斷
- 程式碼品質（30%）：介面清晰、易擴充
- 效能優化（20%）：合理快取、不多餘 DB
- 創新性（10%）：審計/裝飾器設計


## Case #5: 以 Session 承載角色，消除每次檢查的 DB 查詢

### Problem Statement（問題陳述）
業務場景：高併發 Web 系統，每個請求都需權限檢查。若每次檢查都查 DB 取得角色/權限，造成 DB 壓力。

技術挑戰：在安全前提下，避免每次檢查存取 DB。

影響範圍：效能、可擴展性、成本。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 每次檢查都查 DB 讀取使用者角色。
2. 權限資料未有效快取於 Session 中。
3. 未使用框架提供的 User（IPrincipal）承載角色。

深層原因：
- 架構層面：未規劃登入時載入所有授權資訊。
- 技術層面：缺少 Claims/Session 的策略。
- 流程層面：角色變更流程未定義（需登出/刷新）。

### Solution Design（解決方案設計）
解決策略：登入成功時將角色載入 ClaimsPrincipal，透過 Cookie/JWT 保存 Session 期間。每次請求只讀 HttpContext.User，不再查 DB；角色變更時要求重新登入或刷新 Token。

實施步驟：
1. 登入建立 ClaimsPrincipal
- 實作細節：加入 ClaimTypes.Role。
- 所需資源：身分來源、驗證流程。
- 預估時間：0.5 天

2. 配置 Cookie/JWT 期限
- 實作細節：設定 20 分鐘存活等。
- 所需資源：ASP.NET Core 認證中介軟體。
- 預估時間：0.5 天

3. 角色變更管理
- 實作細節：要求重新登入或使用 Security Stamp 刷新。
- 所需資源：登出/刷新端點。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 登入成功後
var claims = new List<Claim> {
  new(ClaimTypes.Name, user.UserName),
  new(ClaimTypes.Role, "sales-manager")
};
var identity = new ClaimsIdentity(claims, "Cookies");
await HttpContext.SignInAsync(
  new ClaimsPrincipal(identity),
  new AuthenticationProperties {
    IsPersistent = true,
    ExpiresUtc = DateTimeOffset.UtcNow.AddMinutes(20)
  });
```

實際案例：文中指出登入後把 IPrincipal 放入 HttpContext.User 或 Thread.CurrentPrincipal。

實作環境：ASP.NET Core、Cookie/JWT。

實測數據：
改善前：每次檢查 1 次 DB 查詢。
改善後：每次檢查 0 次 DB 查詢（Session 期間）。
改善幅度：DB 查詢次數每請求降低 100%。

Learning Points（學習要點）
核心知識點：
- Session/Claims 的正確使用
- 認證與授權分離的介面
- 角色變更的生命周期管理

技能要求：
- 必備技能：ASP.NET Core 認證/授權
- 進階技能：Security Stamp/Token Refresh

延伸思考：
- JWT 無法強制撤銷需配合短生命期與黑名單。
- 限制：角色變更即時性需設計折衷。
- 優化：以分散式快取承載會話資訊。

Practice Exercise（練習題）
基礎練習：完成登入建立角色 Claim。
進階練習：實作角色變更後的強制登出。
專案練習：實作分散式 Session 快取（Redis）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：Session 期間不查 DB
- 程式碼品質（30%）：身份處理清晰
- 效能優化（20%）：顯著降低 DB 負載
- 創新性（10%）：刷新與撤銷設計


## Case #6: 角色與群組分離，避免「群組即授權」的誤用

### Problem Statement（問題陳述）
業務場景：管理者常以群組對使用者分類，誤把群組當角色使用，導致非預期授權。需在設計期明確界定角色（帶有授權語意）與群組（純分類）。

技術挑戰：語意界定與系統限制，避免運維誤用。

影響範圍：越權風險、合規性、審計難度。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 群組被用來承載權限，語意混亂。
2. 管理界面允許任意新增角色/群組與授權綁定。
3. 角色設計未成為產品規格。

深層原因：
- 架構層面：未設計「固定角色集合」。
- 技術層面：缺少限制新增/刪除角色的機制。
- 流程層面：授權變更審核缺失。

### Solution Design（解決方案設計）
解決策略：將角色視為產品規格固定集合（如 Windows Users/Power Users/Admins），只允許「使用者指派角色」，不允許動態新增角色或調整 PA；群組純分類，不參與授權判定。

實施步驟：
1. 角色枚舉化與配置鎖定
- 實作細節：以 enum/常數定義角色，限制新增。
- 所需資源：規格審核。
- 預估時間：0.5 天

2. 後台介面改造
- 實作細節：只提供「指派角色」，移除「新增角色」。
- 所需資源：UI/後端調整。
- 預估時間：1-2 天

3. 稽核與告警
- 實作細節：異常角色變更告警與審計（Case #17）。
- 所需資源：審計流水。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public enum Role { SystemAdmin, SalesManager, SalesOperator }
// UI 僅允許從 Role 列表指派給 User，不提供新增/刪除角色
```

實際案例：文中強調 Role=權限語意、Group=分類，並以 Windows 內建角色為例。

實作環境：任意後台系統。

實測數據：
改善前：管理者可任意新增角色與權限。
改善後：角色固定，僅允許指派。
改善幅度：配置錯誤風險顯著下降（可稽核）。

Learning Points（學習要點）
核心知識點：
- 角色/群組語意差異
- 將角色作為產品規格固化
- 降低誤配置面積

技能要求：
- 必備技能：規格管理、存取控制
- 進階技能：合規與審計流程

延伸思考：
- 群組可做通訊錄、報表篩選等非授權用途。
- 限制：客制化需求需走變更流程。
- 優化：以 Feature Flag 處理差異（非授權）。

Practice Exercise（練習題）
基礎練習：將角色定義改為 enum 並鎖定。
進階練習：調整後台介面，移除新增角色功能。
專案練習：加入異常角色變更的審計告警。

Assessment Criteria（評估標準）
- 功能完整性（40%）：僅允許角色指派
- 程式碼品質（30%）：定義清晰、常數化
- 效能優化（20%）：無關
- 創新性（10%）：合規設計與告警


## Case #7: 銷售系統角色藍圖（系統管理員/主管/專員）

### Problem Statement（問題陳述）
業務場景：需將系統管理員與業務權限完全解耦。主管可查閱全域統計但不可改單；專員可維護個別訂單但不可查閱全域統計；系統管理員僅能安全相關設定。

技術挑戰：正確定義角色與對應權限集合。

影響範圍：資料機密性、職責分離、合規。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用「admin 大權限」概念套所有。
2. 沒有把角色設計對準職責（Job Function）。
3. 權限集合與作業對應不清楚。

深層原因：
- 架構層面：缺少職責導向的角色規格。
- 技術層面：角色/權限映射未明確。
- 流程層面：未與 HR/業務流程對齊。

### Solution Design（解決方案設計）
解決策略：明確定義三角色，建立 Role→Permissions 與 Operation→Permissions 的映射。系統管理員不擁有任何業務資料存取權限。

實施步驟：
1. 角色定義
- 實作細節：SystemAdmin、SalesManager、SalesOperator。
- 所需資源：規格會議。
- 預估時間：0.5 天

2. 權限集合
- 實作細節：CRUD + OrdersQuery。
- 所需資源：工程/PO 協作。
- 預估時間：1 天

3. 映射與測試
- 實作細節：建立 PA/OA 與推導測試（Case #10）。
- 所需資源：單元測試。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
var rolePerms = new Dictionary<Role, HashSet<Perm>>
{
  [Role.SalesManager] = new() { Perm.OrderRead, Perm.OrdersQuery },
  [Role.SalesOperator] = new() { Perm.OrderCreate, Perm.OrderRead, Perm.OrderUpdate, Perm.OrderDelete },
  [Role.SystemAdmin] = new() { /* 僅安全設定相關 */ }
};
```

實際案例：文中舉例三角色設計與 CRUD/Query 權限集合。

實作環境：.NET/C#，RBAC。

實測數據：
改善前：Admin 同時具備業務與安全權限。
改善後：職責分離，互不干涉。
改善幅度：越權面積顯著下降（職責清晰）。

Learning Points（學習要點）
核心知識點：
- 角色以職責為先
- 系統管理員與業務資料完全隔離
- PA/OA 映射的設計邏輯

技能要求：
- 必備技能：RBAC、需求落地
- 進階技能：合規與審計思維

延伸思考：
- 可擴展為階層角色（Role Hierarchy）。
- 限制：資料層級需配合 ABAC（Case #12）。
- 優化：以政策/規則引擎表達複雜映射。

Practice Exercise（練習題）
基礎練習：用 enum/字典定義三角色映射。
進階練習：為三角色推導各自可執行作業清單。
專案練習：後台完成角色切換視角（不同選單）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：角色權限完全對齊職責
- 程式碼品質（30%）：簡潔映射與測試
- 效能優化（20%）：零額外 DB 檢查
- 創新性（10%）：映射驗證自動化


## Case #8: 阻止基層資料外洩：限制廣域查詢與匯出

### Problem Statement（問題陳述）
業務場景：助理需快速維護訂單，但不得取得全域業績與客戶清單。需避免 UI 或 API 提供批量匯出或廣域查詢給助理。

技術挑戰：以 RBAC 分離「單筆操作」與「廣域查詢/匯出」。

影響範圍：資料外洩風險、合規。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 將廣域查詢或匯出對所有已登入者開放。
2. 作業未區分單筆 vs 全域操作。
3. 權限過度寬鬆。

深層原因：
- 架構層面：作業分層與權限綁定不當。
- 技術層面：UI/後端同時缺乏權限檢查。
- 流程層面：未定義資料外洩防護策略。

### Solution Design（解決方案設計）
解決策略：定義 OrdersQuery 權限僅授予主管；報表與匯出 Operation 綁定 OrdersQuery；UI 隱藏匯出按鈕但後端仍強制授權，確保雙層防護。

實施步驟：
1. 權限與作業調整
- 實作細節：匯出/報表 Operation 需 OrdersQuery。
- 所需資源：映射調整。
- 預估時間：0.5 天

2. UI 條件渲染
- 實作細節：前端依角色隱藏匯出按鈕。
- 所需資源：前端修改。
- 預估時間：0.5 天

3. 後端強制授權
- 實作細節：Authorize 或 IsAuthorized 驗證。
- 所需資源：控制器/服務調整。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 後端保護
[Authorize(Roles = "manager")]
public IActionResult ExportOrders() => File(...);

// UI 條件渲染（偽代碼）
if (user.roles.includes('manager')) { showExportButton(); }
```

實際案例：文中明確要求助理不得接觸批次匯出與全域統計。

實作環境：ASP.NET Core + 前端框架。

實測數據：
改善前：所有已登入者可見匯出。
改善後：僅主管具備匯出/報表。
改善幅度：外洩風險顯著降低（設計性消除）。

Learning Points（學習要點）
核心知識點：
- 以權限綁定全域操作
- 前後端雙層防護
- 最小權限原則

技能要求：
- 必備技能：Authorize 使用、前端條件渲染
- 進階技能：安全評估與威脅建模

延伸思考：
- 加入下載速率限制與審計（Case #17）。
- 限制：助理仍可透過單筆檢視收集資料（需額外防護）。
- 優化：異常行為偵測與警示。

Practice Exercise（練習題）
基礎練習：為匯出 API 加上 Authorize。
進階練習：在 UI 隱藏匯出功能。
專案練習：建置報表模組僅允許主管訪問。

Assessment Criteria（評估標準）
- 功能完整性（40%）：非主管被阻擋
- 程式碼品質（30%）：前後端一致性
- 效能優化（20%）：無關
- 創新性（10%）：風險評估設計


## Case #9: 將必要查核內聚到領域服務，避免權限耦合（Create 不需 Query）

### Problem Statement（問題陳述）
業務場景：建立訂單需檢查重複、衝突等條件。若要求具備廣域 Query 才能建立，助理將被迫擁有不必要的查詢權限。

技術挑戰：避免在應用層為 Create 引入 OrdersQuery。

影響範圍：越權風險、耦合度、複用性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 在應用層以廣域查詢來實作驗證。
2. 驗證邏輯與查詢權限綁死。
3. 未把驗證設計為領域內聚的服務。

深層原因：
- 架構層面：邏輯未內聚於領域層。
- 技術層面：缺少明確的檢核 API。
- 流程層面：未定義驗證責任分配。

### Solution Design（解決方案設計）
解決策略：在 Domain Service 提供必要的 Exists/Validate API，Create 只需 Create 權限即可，驗證由領域服務內完成，不暴露廣域資料。

實施步驟：
1. 定義驗證 API
- 實作細節：ExistsOrderNumber、CheckConflict。
- 所需資源：Repository/索引。
- 預估時間：1 天

2. 重構 Create Flow
- 實作細節：呼叫驗證 API，不做廣域 Query。
- 所需資源：Service 重構。
- 預估時間：1 天

3. 測試覆蓋
- 實作細節：新增/匯入皆通過驗證。
- 所需資源：單元測試。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class OrderService {
  public void Create(OrderDto dto, IPrincipal user) {
    if(!_repo.IsUniqueNumber(dto.OrderNumber)) 
       throw new InvalidOperationException("Duplicated");
    _repo.Create(dto, user);
  }
}
```

實際案例：文中指出「Create 若需 Query 應內聚於 Create 邏輯」。

實作環境：.NET/C#，Domain Service。

實測數據：
改善前：Create 依賴廣域 Query 權限。
改善後：Create 僅需 Create 權限。
改善幅度：權限耦合度下降，越權風險消除。

Learning Points（學習要點）
核心知識點：
- 內聚驗證，減少權限面積
- Domain Service 設計
- 防止邏輯外流到應用層

技能要求：
- 必備技能：DDD/分層設計
- 進階技能：效能/索引優化

延伸思考：
- 需要審計驗證結果（Case #17）。
- 限制：部分複雜驗證仍需有限資料存取。
- 優化：用規則引擎配置化。

Practice Exercise（練習題）
基礎練習：為 Create 建立唯一性檢核。
進階練習：將匯入流程改用內聚驗證。
專案練習：設計完整訂單狀態轉移與驗證集合。

Assessment Criteria（評估標準）
- 功能完整性（40%）：Create 可運作且不需 Query
- 程式碼品質（30%）：內聚且可測
- 效能優化（20%）：檢核延遲可接受
- 創新性（10%）：驗證可配置化


## Case #10: 自動推導與驗證 Role×Operation 對照表

### Problem Statement（問題陳述）
業務場景：設計後需驗證每個角色能執行的作業是否符合預期，避免 PA/OA 映射錯漏。

技術挑戰：自動化推導與比對，避免手工核對遺漏。

影響範圍：上線品質、風險控制。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手動維護對照表易錯。
2. 缺少自動化推導工具。
3. 無回歸測試覆蓋。

深層原因：
- 架構層面：映射無可程式化驗證。
- 技術層面：未建立產生/比對管線。
- 流程層面：缺測試檢查點。

### Solution Design（解決方案設計）
解決策略：撰寫程式從 Role→Perm 與 Operation→Perm 自動推導 Role→Operation，與期望清單比對；CI 內執行，確保變更不破壞授權規格。

實施步驟：
1. 推導程式
- 實作細節：以集合運算推導。
- 所需資源：C# 測試工程。
- 預估時間：0.5 天

2. 期望清單
- 實作細節：由 PO/架構師提供。
- 所需資源：文件/配置。
- 預估時間：0.5 天

3. CI 集成
- 實作細節：失敗時阻擋合併。
- 所需資源：CI/CD。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
bool CanRoleRunOp(Role r, Operation op)
  => op.Required.All(p => rolePerms[r].Contains(p));

var derived = roles.ToDictionary(r => r, r => operations.Values
  .Where(op => CanRoleRunOp(r, op)).Select(op => op.Name).ToArray());

Assert.Equal(expected["SalesManager"], derived[Role.SalesManager]);
```

實際案例：文中建議以推導檢核映射品質。

實作環境：.NET Test、CI。

實測數據：
改善前：手工核對易漏。
改善後：自動推導比對，回歸可防破壞。
改善幅度：授權規格迭代風險顯著下降。

Learning Points（學習要點）
核心知識點：
- 集合運算推導
- 可測性與 CI 防護
- 授權做為產品規格

技能要求：
- 必備技能：單元測試、集合運算
- 進階技能：規格轉測試

延伸思考：
- 可輸出 CSV 供審核留底。
- 限制：期望清單需維護。
- 優化：生成權限矩陣文件。

Practice Exercise（練習題）
基礎練習：推導 Role→Operation。
進階練習：比對期望清單。
專案練習：加入 CI Gate。

Assessment Criteria（評估標準）
- 功能完整性（40%）：推導正確
- 程式碼品質（30%）：測試清晰
- 效能優化（20%）：無關
- 創新性（10%）：輸出審核文件


## Case #11: 權限查詢效能優化：從乘法變加法（模組快取）

### Problem Statement（問題陳述）
業務場景：大型多客戶系統（1 萬用戶、5000 行為、1 萬客戶）若以最細 HasPermission(user, action, client) 查詢將面臨 1.5 兆可能組合。

技術挑戰：高頻權限查詢的效能與成本。

影響範圍：延遲、吞吐、成本。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 權限查詢以最小粒度重複執行。
2. 沒有聚合與快取策略。
3. 未設計「模組上下文」。

深層原因：
- 架構層面：API 設計非聚合導向。
- 技術層面：無 session/module 快取。
- 流程層面：未分析熱路徑。

### Solution Design（解決方案設計）
解決策略：定義 session_context 與 module_context，改為 CheckModulePermission(session, module) 一次回傳該模組所有常用權限集合並快取，將乘法空間降維為可快取的加法組合。

實施步驟：
1. 模組劃分
- 實作細節：5000 action 歸為 ~50 modules。
- 所需資源：產品/工程共創。
- 預估時間：1-2 天

2. 快取介面
- 實作細節：以 (sessionId, moduleId) 做 key。
- 所需資源：記憶體/分散式快取。
- 預估時間：1 天

3. 熱路徑優化
- 實作細節：預熱常用模組。
- 所需資源：啟動鉤子。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public record SessionContext(string SessionId, string[] Roles);
public record ModuleContext(string ModuleId, string[] Actions);

public PermissionSet CheckModulePermission(SessionContext s, ModuleContext m)
{
  var key = $"{s.SessionId}:{m.ModuleId}";
  return _cache.GetOrCreate(key, _ => ComputePermissions(s, m));
}
```

實際案例：文中以 10000×5000×10000 的組合分析並提出模組化與快取思路。

實作環境：.NET + Cache（Memory/Redis）。

實測數據（估算）：
改善前：組合空間 1.5e12。
改善後：約 1e8（10000 sessions×10000 clients×50 modules）。
改善幅度：降維 99.99%（空間層面估算）。

Learning Points（學習要點）
核心知識點：
- 降維思維（乘法→加法）
- Session/Module 快取鍵設計
- 熱路徑預熱

技能要求：
- 必備技能：快取、鍵設計
- 進階技能：模組邊界與聚合

延伸思考：
- 與分散式快取一致性策略。
- 限制：模組劃分需審慎。
- 優化：增量更新與事件驅動失效。

Practice Exercise（練習題）
基礎練習：為 10 個 action 劃分 2 模組並快取。
進階練習：加入快取失效策略。
專案練習：對整個 API 面實作模組快取層。

Assessment Criteria（評估標準）
- 功能完整性（40%）：模組快取可用
- 程式碼品質（30%）：鍵設計清晰
- 效能優化（20%）：命中率與延遲下降
- 創新性（10%）：預熱與增量刷新


## Case #12: 資料層級授權：以屬性/查詢過濾限制資料可見性

### Problem Statement（問題陳述）
業務場景：專員可維護「自己負責」的訂單，不可看到他人訂單；主管可看全部。僅靠 RBAC 難以滿足資料層級限制。

技術挑戰：在資料存取層套用屬性條件（如 ownerId=本人）。

影響範圍：資料機密性、可用性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. RBAC 粒度不足以表達資料屬性限制。
2. 檢查只在應用層，未下推到查詢層。
3. 缺少統一的過濾策略。

深層原因：
- 架構層面：未設計 ABAC/資料層過濾。
- 技術層面：ORM/SQL 未內建過濾。
- 流程層面：未定義可見性規則。

### Solution Design（解決方案設計）
解決策略：在 Repository/Query 層為每個查詢注入可見性過濾，角色為 manager 則無過濾、operator 則加 ownerId=@currentUserId；同時以 Claim 承載 userId。

實施步驟：
1. 可見性規則定義
- 實作細節：manager=all, operator=own only。
- 所需資源：規格。
- 預估時間：0.5 天

2. 查詢過濾實作
- 實作細節：Repository 包裝，注入 userId。
- 所需資源：ORM/SQL。
- 預估時間：1-2 天

3. 測試資料可見性
- 實作細節：多身分測試可見性。
- 所需資源：單元/整合測試。
- 預估時間：0.5-1 天

關鍵程式碼/設定：
```csharp
// EF LINQ
IQueryable<Order> OrdersFor(IPrincipal user) {
  if (user.IsInRole("sales-manager")) return _db.Orders;
  var userId = ((ClaimsPrincipal)user).FindFirst(ClaimTypes.NameIdentifier)?.Value;
  return _db.Orders.Where(o => o.AssignedTo == userId);
}

// SQL
// operator:
SELECT * FROM Orders WHERE AssignedTo = @UserId;
// manager:
SELECT * FROM Orders;
```

實際案例：文末提及「資料層級的權限管理」「Database Query 層級就支援權限過濾」。

實作環境：.NET/EF 或 SQL。

實測數據：
改善前：專員可見全部資料。
改善後：專員僅見自有資料，主管見全部。
改善幅度：資料外露面積顯著降低。

Learning Points（學習要點）
核心知識點：
- RBAC+ABAC 混合模式
- 查詢過濾設計
- Claim 承載上下文

技能要求：
- 必備技能：ORM/SQL、Claims
- 進階技能：多租戶/Row-Level Security

延伸思考：
- 可用資料庫原生 RLS（Row-Level Security）。
- 限制：複雜過濾需性能評估。
- 優化：以索引改善過濾效能。

Practice Exercise（練習題）
基礎練習：為 Orders 查詢加 ownerId 過濾。
進階練習：為多身分測試可見性。
專案練習：封裝通用可見性過濾器中介層。

Assessment Criteria（評估標準）
- 功能完整性（40%）：資料可見性正確
- 程式碼品質（30%）：封裝良好
- 效能優化（20%）：查詢高效
- 創新性（10%）：RLS/Claim 混合運用


## Case #13: 不會規劃 Permission？以 CRUD/狀態轉移起步

### Problem Statement（問題陳述）
業務場景：團隊不確定該如何拆分權限單位，權限經常過多或過少，導致無法覆蓋需求。

技術挑戰：設計一組穩健的最小權限集合。

影響範圍：可維護性、準確性、擴展性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 權限命名混亂。
2. 未有系統化方法（CRUD/狀態轉移）。
3. 操作與權限無一致準則。

深層原因：
- 架構層面：缺少設計規範。
- 技術層面：未以實體與狀態導出權限。
- 流程層面：缺少審核基準。

### Solution Design（解決方案設計）
解決策略：以實體為中心（如 Order），先用 CRUD+Query 做為基礎權限集合；若已有狀態機，則以狀態轉移（箭頭）為權限單位，Operation 由權限組合而成。

實施步驟：
1. 實體盤點
- 實作細節：識別核心實體（Order 等）。
- 所需資源：需求清單。
- 預估時間：0.5 天

2. 權限草案
- 實作細節：CRUD+Query 或狀態轉移列出。
- 所需資源：設計會議。
- 預估時間：0.5 天

3. Operation 組合
- 實作細節：由權限組合出高階作業。
- 所需資源：映射表。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 基礎權限集合
enum Perm { OrderCreate, OrderRead, OrderUpdate, OrderDelete, OrdersQuery }

// Operation 以組合表達
var operations = new Dictionary<string, Operation> {
  ["Orders_Process"] = new("Orders_Process", new[]{ Perm.OrderRead, Perm.OrderUpdate }),
};
```

實際案例：文中建議以 CRUD/狀態轉移作為起點。

實作環境：任意。

實測數據：
改善前：權限定義隨意。
改善後：可重用、可組合的權限基座。
改善幅度：權限定義錯誤率顯著下降（可審核）。

Learning Points（學習要點）
核心知識點：
- 由實體/狀態導出權限
- Operation=權限組合
- 可演進的權限基座

技能要求：
- 必備技能：資料模型設計
- 進階技能：狀態機建模

延伸思考：
- 未來可接入 PBAC/ABAC。
- 限制：過於粗糙需微調。
- 優化：與測試（Case #10）結合驗證。

Practice Exercise（練習題）
基礎練習：為 2 個實體列出 CRUD/Query 權限。
進階練習：以狀態轉移定義 3 條權限。
專案練習：將 5 個 Operation 用權限組合實作。

Assessment Criteria（評估標準）
- 功能完整性（40%）：權限完整覆蓋
- 程式碼品質（30%）：命名與結構清晰
- 效能優化（20%）：無關
- 創新性（10%）：狀態驅動設計


## Case #14: 背景/工具程式中的一致授權：Thread.CurrentPrincipal

### Problem Statement（問題陳述）
業務場景：除了 Web，還有排程、CLI 工具需要執行受控操作，需與 Web 相同的授權決策規則。

技術挑戰：無 HttpContext 時如何套用相同授權規則。

影響範圍：一致性、維護性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏統一「目前使用者」來源。
2. 在工具程式內跳過授權。
3. 無法複用 Web 的邏輯。

深層原因：
- 架構層面：授權對環境耦合。
- 技術層面：未使用 Thread.CurrentPrincipal。
- 流程層面：工具未納入安全規範。

### Solution Design（解決方案設計）
解決策略：啟動工具/排程時建立 GenericPrincipal（或載入服務帳號角色），指派至 Thread.CurrentPrincipal，後續沿用相同授權服務（Case #4）。

實施步驟：
1. 建立 Principal
- 實作細節：GenericPrincipal/ClaimsPrincipal。
- 所需資源：帳號/角色規劃。
- 預估時間：0.5 天

2. 指派至 Thread
- 實作細節：Thread.CurrentPrincipal = ...
- 所需資源：程式碼調整。
- 預估時間：0.5 天

3. 授權重用
- 實作細節：呼叫同一 ICustomAuthorization。
- 所需資源：參考 Case #4。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var identity = new GenericIdentity("scheduler");
Thread.CurrentPrincipal = new GenericPrincipal(identity, new[] { "system-admin" });
if (_auth.IsAuthorized(Thread.CurrentPrincipal, operations["Orders_BatchImport"])) { /* ... */ }
```

實際案例：文中提供 Console 範例使用 Thread.CurrentPrincipal。

實作環境：.NET Console/Worker Service。

實測數據：
改善前：工具程式繞過授權。
改善後：沿用同一授權規則。
改善幅度：一致性提升，風險降低。

Learning Points（學習要點）
核心知識點：
- Principal 於不同環境的承載方式
- 服務帳號/機器帳號概念
- 授權邏輯重用

技能要求：
- 必備技能：.NET 執行緒原理
- 進階技能：服務帳號安全

延伸思考：
- 與 KeyVault/OIDC 服務帳號整合。
- 限制：多執行緒需留意 Principal 傳遞。
- 優化：上下文傳遞封裝。

Practice Exercise（練習題）
基礎練習：在 Console 使用 Principal 判斷角色。
進階練習：在背景工作呼叫授權服務。
專案練習：建立統一的主體建立器。

Assessment Criteria（評估標準）
- 功能完整性（40%）：工具程式可授權判斷
- 程式碼品質（30%）：重用與封裝
- 效能優化（20%）：無關
- 創新性（10%）：上下文傳遞設計


## Case #15: Session 生命周期與過期設定，降低權限漂移風險

### Problem Statement（問題陳述）
業務場景：登入後需在一段時間內持續使用身分。若 Session 無過期，角色變更難即時生效，存在權限漂移風險。

技術挑戰：安全與使用體驗的平衡（例如 20 分鐘 Cookie 期限）。

影響範圍：安全、體驗、合規。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Session 過期策略缺失。
2. 角色變更後仍沿用舊權限。
3. 無強制登出/刷新流程。

深層原因：
- 架構層面：認證授權生命周期未定義。
- 技術層面：Cookie/JWT 配置不當。
- 流程層面：角色變更 SOP 缺少。

### Solution Design（解決方案設計）
解決策略：設定合理 Session 過期（如 20 分鐘），必要時縮短 JWT TTL；角色變更時強制登出或刷新 Token；敏感操作增加二次驗證。

實施步驟：
1. 過期設定
- 實作細節：Cookie ExpiresUtc、JWT exp。
- 所需資源：安全策略。
- 預估時間：0.5 天

2. 變更處理
- 實作細節：角色變更觸發登出。
- 所需資源：事件/通知。
- 預估時間：1 天

3. 敏感操作提升
- 實作細節：二次驗證。
- 所需資源：MFA/OTP。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
await HttpContext.SignInAsync(
  principal,
  new AuthenticationProperties { ExpiresUtc = DateTimeOffset.UtcNow.AddMinutes(20) });
```

實際案例：文中示例 Cookie 20 分鐘的說明。

實作環境：ASP.NET Core。

實測數據：
改善前：Session 長存，權限漂移。
改善後：Session 適時過期，變更可生效。
改善幅度：漂移窗口顯著收斂。

Learning Points（學習要點）
核心知識點：
- Session 與權限變更
- TTL 設計折衷
- 敏感操作額外強化

技能要求：
- 必備技能：Cookie/JWT 設定
- 進階技能：MFA/OIDC

延伸思考：
- 使用 Security Stamp/Token Revocation。
- 限制：單點登出在 JWT 下較難。
- 優化：短 TTL + Refresh Token。

Practice Exercise（練習題）
基礎練習：設定 Cookie 20 分鐘過期。
進階練習：實作角色變更強制登出。
專案練習：對匯出報表加二次驗證。

Assessment Criteria（評估標準）
- 功能完整性（40%）：過期與登出生效
- 程式碼品質（30%）：設定清晰
- 效能優化（20%）：無關
- 創新性（10%）：變更事件設計


## Case #16: 產品授權（合約/Feature Flag）與使用者授權分離

### Problem Statement（問題陳述）
業務場景：不同客戶合約/版本對功能開關不同，且同一客戶內不同使用者角色權限也不同。若混為一談，維護困難且容易錯配。

技術挑戰：在「客戶層級功能授權」與「使用者層級操作授權」間解耦。

影響範圍：可維護性、錯配風險、上線效率。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 把 Feature Flag 與 Role 放在同一維度。
2. 合約配置與使用者權限互相覆蓋。
3. 缺少 API scope/feature 維度。

深層原因：
- 架構層面：授權維度未分離。
- 技術層面：無 Policy/Scope 驗證。
- 流程層面：合約變更與角色變更混雜。

### Solution Design（解決方案設計）
解決策略：以「Feature Flag/Contract/Scope」判斷「功能是否對該客戶開放」，再以 RBAC 判斷「使用者是否可執行操作」。Web 使用 Policy（RequireClaim feature=X）+ Role 雙檢查。

實施步驟：
1. 定義 Feature/Scope
- 實作細節：features=[Reports, BatchImport...]。
- 所需資源：產品規格。
- 預估時間：1 天

2. Policy 設定
- 實作細節：AddAuthorization options 添加 policies。
- 所需資源：ASP.NET Core。
- 預估時間：0.5 天

3. 控制器雙檢查
- 實作細節：[Authorize(Policy="FeatureReports", Roles="manager")]。
- 所需資源：控制器調整。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Startup
services.AddAuthorization(o => {
  o.AddPolicy("FeatureReports", p => p.RequireClaim("feature", "Reports"));
});

// Controller
[Authorize(Policy="FeatureReports", Roles="manager")]
public IActionResult Sales_Report() => ...
```

實際案例：文末提及 contract/config/feature flag 與 api scope。

實作環境：ASP.NET Core、Claims。

實測數據：
改善前：合約與角色混雜，易錯。
改善後：維度分離，雙層校驗。
改善幅度：配置錯誤率顯著下降。

Learning Points（學習要點）
核心知識點：
- 維度分離（Feature vs Role）
- Policy/Claim 的運用
- Scope/Contract 與 RBAC 組合

技能要求：
- 必備技能：ASP.NET Core Authorization Policy
- 進階技能：多維授權設計

延伸思考：
- 可用外部配置中心管理 features。
- 限制：Claim 攜帶 feature 需防竄改。
- 優化：以 API Gateway 驗證 scope。

Practice Exercise（練習題）
基礎練習：定義一個 Feature Policy。
進階練習：Controller 套用雙檢查。
專案練習：建立合約配置→Claim 發行流程。

Assessment Criteria（評估標準）
- 功能完整性（40%）：雙檢查生效
- 程式碼品質（30%）：Policy 清晰
- 效能優化（20%）：無關
- 創新性（10%）：配置化與發行流程


## Case #17: 審計日誌（Audit Log）導入授權決策全鏈路可追溯

### Problem Statement（問題陳述）
業務場景：需回答「誰在何時對何資源進行何操作，為何允許/拒絕」。沒有審計很難調查外洩或越權。

技術挑戰：低侵入地記錄授權決策與關鍵操作。

影響範圍：合規、資安、事故回溯。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無統一審計機制。
2. 授權決策不可追溯。
3. 日誌與操作未關聯。

深層原因：
- 架構層面：缺審計層/裝飾器。
- 技術層面：缺少關聯 ID/TraceId。
- 流程層面：無保留策略。

### Solution Design（解決方案設計）
解決策略：以 Decorator 包裝 ICustomAuthorization 記錄允許/拒絕、使用者/角色、Operation、原因；對敏感操作記錄前/後差異與輸出大小；集中輸出到日誌系統並設保留/告警規則。

實施步驟：
1. 裝飾器實作
- 實作細節：包裝 IsAuthorized 記錄決策。
- 所需資源：Logger/CorrelationId。
- 預估時間：1 天

2. 敏感操作審計
- 實作細節：匯出/刪除等加強紀錄。
- 所需資源：中介層。
- 預估時間：1 天

3. 保留/告警
- 實作細節：規則與儲存期限。
- 所需資源：Log 系統/SIEM。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class AuditingAuthorization : ICustomAuthorization
{
  private readonly ICustomAuthorization _inner; private readonly ILogger _log;
  public bool IsAuthorized(IPrincipal u, ICustomOperation op) {
    var ok = _inner.IsAuthorized(u, op);
    _log.LogInformation("auth {User} op={Op} result={Res}", u.Identity?.Name, op.Name, ok);
    return ok;
  }
}
```

實際案例：文末「應用：audit log」指出導入必要性。

實作環境：.NET + Logging/SIEM。

實測數據：
改善前：事故難回溯。
改善後：決策可追溯、可告警。
改善幅度：調查效率顯著提升。

Learning Points（學習要點）
核心知識點：
- 授權決策審計
- 敏感操作強化
- 可追溯性設計

技能要求：
- 必備技能：日誌、結構化訊息
- 進階技能：SIEM/SOC 整合

延伸思考：
- 配合異常行為偵測。
- 限制：日誌量/成本。
- 優化：取樣與遮蔽個資。

Practice Exercise（練習題）
基礎練習：為授權服務加審計。
進階練習：對匯出操作記錄輸出大小。
專案練習：整合到 ELK/CloudWatch 並設告警。

Assessment Criteria（評估標準）
- 功能完整性（40%）：決策都有記錄
- 程式碼品質（30%）：低侵入、可重用
- 效能優化（20%）：日誌開銷可控
- 創新性（10%）：告警與取樣策略


## Case #18: 避免「通用配置介面」破壞授權秩序（設計期定稿）

### Problem Statement（問題陳述）
業務場景：有些系統允許管理者自由新增/變更角色與權限映射，短期看靈活，長期造成「人人皆超管」的災難。

技術挑戰：如何在滿足變更需求下，避免動態破壞設計期的授權模型。

影響範圍：安全風險、合規違反、維護困難。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 過度彈性的配置 UI。
2. 將設計期決策移到執行期。
3. 缺少防呆與審核。

深層原因：
- 架構層面：授權模型未封裝於產品規格。
- 技術層面：允許直接改 PA/OA。
- 流程層面：缺審核流程與 CI 測試。

### Solution Design（解決方案設計）
解決策略：將角色、權限、映射視為產品憲法，由程式或受控配置管理；執行期僅開放「使用者→角色」指派；任何模型變更需經版本管理與測試（Case #10）。

實施步驟：
1. 固化模型
- 實作細節：以程式/受控配置儲存 R/P/PA/OA。
- 所需資源：Repo/審核流程。
- 預估時間：1 天

2. 限制 UI
- 實作細節：移除新增/修改角色/映射功能。
- 所需資源：後台調整。
- 預估時間：1 天

3. 變更流程
- 實作細節：PR+測試+審核+版本。
- 所需資源：CI/CD。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 將映射存於只讀配置或程式中，透過版本控制管理
readonly Dictionary<Role, HashSet<Perm>> rolePerms = LoadFromVersionedConfig();
```

實際案例：文中指出「不應該讓客戶在 runtime 任意調整 R/P/PA」。

實作環境：任意後台系統。

實測數據：
改善前：任意改動造成越權泛濫。
改善後：模型受版本控制與測試保護。
改善幅度：系統性越權風險顯著下降。

Learning Points（學習要點）
核心知識點：
- 授權模型作為產品憲法
- 版本控制與測試護欄
- 降低配置面積

技能要求：
- 必備技能：配置管理、CI
- 進階技能：合規流程設計

延伸思考：
- 可提供沙箱環境試配。
- 限制：變更速度較慢。
- 優化：以功能旗標逐步開放。

Practice Exercise（練習題）
基礎練習：將映射改為只讀配置。
進階練習：建立變更審核流程。
專案練習：打造授權模型 CI Gate（Case #10）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：執行期不可改模型
- 程式碼品質（30%）：配置可讀可測
- 效能優化（20%）：無關
- 創新性（10%）：變更治理設計


====================

案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #3, #5, #6, #7, #8, #13, #14, #15
- 中級（需要一定基礎）
  - Case #1, #2, #4, #10, #16, #18
- 高級（需要深厚經驗）
  - Case #11, #12, #17

2. 按技術領域分類
- 架構設計類
  - Case #1, #4, #6, #7, #10, #16, #18
- 效能優化類
  - Case #5, #11
- 整合開發類
  - Case #3, #14, #16
- 除錯診斷類
  - Case #10, #17
- 安全防護類
  - Case #2, #8, #9, #12, #15, #17

3. 按學習目標分類
- 概念理解型
  - Case #1, #6, #7, #13, #15, #16, #18
- 技能練習型
  - Case #3, #4, #5, #10, #14
- 問題解決型
  - Case #2, #8, #9, #12, #17
- 創新應用型
  - Case #11, #16

案例關聯圖（學習路徑建議）
- 先學案例：
  - Case #3（IPrincipal/Authorize 基礎）
  - Case #1（RBAC 降維思維）
  - Case #13（CRUD/狀態轉移導出權限）
- 進階串接：
  - Case #7（角色藍圖）→ Case #8（資料外洩防護）→ Case #2（Operation-權限錯配治理）→ Case #9（領域內聚驗證）
  - Case #4（統一授權入口）→ Case #5（Session 裝載）→ Case #14（背景程式一致化）
- 品質與驗證：
  - Case #10（矩陣推導與測試）→ Case #18（模型治理）
- 高階能力：
  - Case #11（模組快取降維）→ Case #12（資料層級授權）
  - Case #16（Contract/Feature 與 Role 分離）
  - Case #17（審計全鏈路）

完整學習路徑建議：
1) 打基礎：#3 → #1 → #13 → #7
2) 實務防護：#8 → #2 → #9
3) 工程化：#4 → #5 → #14
4) 規格與品質：#10 → #18
5) 進階優化與擴展：#11 → #12 → #16
6) 安全落地與追溯：#17 → 回顧全鏈路測試與演練

透過以上路徑，從框架用法到授權模型設計、從效能優化到資料層級控制，再到合約/Feature 與審計，逐步形成完整的權限管理實戰能力。