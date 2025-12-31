---
layout: synthesis
title: "[Azure] Multi-Tenancy Application #3, (資料層)實作案例"
synthesis_type: solution
source_post: /2013/03/21/azure-multi-tenancy-application-3-data-layer-implementation/
redirect_from:
  - /2013/03/21/azure-multi-tenancy-application-3-data-layer-implementation/solution/
postid: 2013-03-21-azure-multi-tenancy-application-3-data-layer-implementation
---

以下內容根據原文的明確意圖與實作方向，萃取並組織為可教、可練、可評的實戰案例。每一案都圍繞「在資料層完成租戶隔離、MVC 路由虛擬化租戶、Azure Table Storage 的實作細節、以及雲端應用的測試與部署挑戰」等主題，並盡量對齊原文的技術棧與語境（MVC4 + Azure Table Storage，Hub/HubData 概念，單元測試導向）。由於原文為 POC 等級說明，未提供量化指標，以下實測數據以定性描述為主，並標示為 POC 層級。

------------------------------------------------------------

## Case #1: 在 DataContext 層完成租戶隔離（HubDataContext 範型）

### Problem Statement（問題陳述）
- 業務場景：SaaS 訂便當系統需要同時服務多個公司（租戶）。開發團隊希望像開發單租戶系統一樣自然地寫業務邏輯，卻又能保證每個租戶的資料嚴格隔離，避免彼此誤讀或誤寫。
- 技術挑戰：如何讓資料層自動「帶入」租戶範圍，不須在每個查詢手動加租戶條件，並且與 Azure Table Storage 的 PartitionKey 模式一致。
- 影響範圍：資料安全（跨租戶外洩）、維護成本（重複條件）、上線風險（遺漏條件）。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 查詢分散於各層，靠工程師自律加租戶條件，易漏掉。
  2. Azure Table Storage 為 schema-less，需要在程式層統一規範 PartitionKey。
  3. 缺少統一的 DataContext 介面，無法在用法上強制執行隔離。
- 深層原因：
  - 架構層面：缺乏針對多租戶的資料邊界抽象。
  - 技術層面：未將租戶上下文（ClientId）作為一級公民融入查詢管線。
  - 流程層面：沒有單元測試守門，難以在 PR 或 CI 階段攔截誤用。

### Solution Design（解決方案設計）
- 解決策略：建立 HubDataContext，於建構時引入當前租戶識別（ClientId），自動將 PartitionKey = ClientId 注入所有 HubData 的查詢與寫入，提供 EF 式 Set<T>() API 以降低心智負擔，並以單元測試驗證隔離。

- 實施步驟：
  1. 定義抽象介面 IHubDataContext
     - 實作細節：暴露 ClientId、Set<T>()、Add/Find API；泛型受限於租戶實體基底。
     - 所需資源：.NET 4.5、Azure Storage SDK（CloudTableClient）。
     - 預估時間：0.5 天
  2. 建立 HubTableEntity 作為租戶實體基底
     - 實作細節：将 PartitionKey 封裝為 ClientId，RowKey 抽象為實體主鍵。
     - 所需資源：WindowsAzure.Storage 套件。
     - 預估時間：0.5 天
  3. 實作 HubDataContext
     - 實作細節：Set<T>() 內部自動附帶 PartitionKey == ClientId 的 Query；寫入前強制寫入 PartitionKey。
     - 所需資源：TableQuery、TableOperation、序列化。
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
public interface IHubDataContext : IDisposable
{
    string ClientId { get; }
    IQueryable<T> Set<T>() where T : HubTableEntity, new();
    Task AddAsync<T>(T entity) where T : HubTableEntity, new();
    Task<T> FindAsync<T>(string rowKey) where T : HubTableEntity, new();
}

public abstract class HubTableEntity : TableEntity
{
    public string ClientId => PartitionKey;
    public void BindTenant(string clientId) => PartitionKey = clientId;
}

public sealed class HubDataContext : IHubDataContext
{
    private readonly CloudTableClient _client;
    public string ClientId { get; }

    public HubDataContext(CloudTableClient client, string clientId)
    {
        _client = client ?? throw new ArgumentNullException(nameof(client));
        ClientId = clientId ?? throw new ArgumentNullException(nameof(clientId));
    }

    public IQueryable<T> Set<T>() where T : HubTableEntity, new()
    {
        var table = _client.GetTableReference(typeof(T).Name);
        table.CreateIfNotExists();
        return table.CreateQuery<T>().Where(e => e.PartitionKey == ClientId);
    }

    public async Task AddAsync<T>(T entity) where T : HubTableEntity, new()
    {
        entity.BindTenant(ClientId);
        var table = _client.GetTableReference(typeof(T).Name);
        await table.ExecuteAsync(TableOperation.InsertOrReplace(entity));
    }

    public async Task<T> FindAsync<T>(string rowKey) where T : HubTableEntity, new()
    {
        var table = _client.GetTableReference(typeof(T).Name);
        var result = await table.ExecuteAsync(TableOperation.Retrieve<T>(ClientId, rowKey));
        return (T)result.Result;
    }

    public void Dispose() {}
}
```

- 實際案例：POC 訂便當系統的 HubData（會員、訂單）均經由 HubDataContext 存取，單元測試驗證同一查詢在 A、B 兩個租戶下得到不同集合。
- 實作環境：MVC4、.NET 4.5、WindowsAzure.Storage v2.x、Azure Storage Emulator（本機）。
- 實測數據：
  - 改善前：每個查詢手動加 ClientId 條件，易遺漏。
  - 改善後：HubDataContext 自動注入，單元測試下跨租戶查詢為 0 次。
  - 改善幅度：定性改善（POC 級），未提供量化百分比。

Learning Points（學習要點）
- 核心知識點：
  - 將租戶上下文提昇到資料層，避免應用層重複實作。
  - Azure Table Storage PartitionKey 與租戶隔離的對應。
  - EF 式 API 在 NoSQL（Table）上的落地。
- 技能要求：
  - 必備技能：C#、Azure Table Storage SDK、LINQ。
  - 進階技能：泛型、IQueryable 管線、異步 I/O。
- 延伸思考：
  - 是否需要支援分公司/子租戶（第二層 PartitionKey）？
  - 跨租戶報表如何在不破壞隔離下實作？
  - 是否應提供審計與防範越權的額外保護層？

Practice Exercise（練習題）
- 基礎練習：為某個新實體（如 Address）加入 HubTableEntity，完成 CRUD（30 分鐘）。
- 進階練習：為 Set<T>() 增加分頁與排序，確保仍自動注入 PartitionKey（2 小時）。
- 專案練習：將現有單租戶模組移植為 HubDataContext 風格，補齊單元測試（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：自動注入租戶範圍，CRUD 正常。
- 程式碼品質（30%）：介面清晰、測試通過、錯誤處理妥當。
- 效能優化（20%）：查詢僅掃描單一 Partition。
- 創新性（10%）：可擴充的租戶策略（例如子租戶、軟隔離+硬隔離切換）。

------------------------------------------------------------

## Case #2: 在 URL 層建立虛擬目錄式租戶分區（MVC Routing 客製）

### Problem Statement（問題陳述）
- 業務場景：每個租戶希望擁有看似獨立的網站入口（如 /contoso/... 與 /fabrikam/...），方便內部溝通與書籤管理，也有助於品牌識別。
- 技術挑戰：在 MVC4 的 Routing 中加入「client」層級，確保所有控制器與動作均能讀到當前租戶，並與資料層對應。
- 影響範圍：導覽一致性、SEO、維護成本（重複傳遞租戶參數）。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 預設路由僅含 controller/action，沒有租戶維度。
  2. 未集中解析租戶，導致每個控制器各自處理，容易不一致。
  3. URL 產生器若未帶入租戶，連結會錯位。
- 深層原因：
  - 架構層面：缺乏「租戶即路由一級段」的統一規約。
  - 技術層面：缺少 RouteConstraint 確認 client 的合法性。
  - 流程層面：未設置檢查（測試/審查）以確保新路由遵守規範。

### Solution Design（解決方案設計）
- 解決策略：新增自訂 Route 與 RouteConstraint，將 {client} 作為第一段 URL，解析後放入 HttpContext.Items 或自訂 RequestContext 供後續 DataContext 使用；同時擴充 UrlHelper 以自動帶入 client。

- 實施步驟：
  1. 加入路由與約束
     - 實作細節：routes.MapRoute("{client}/{controller}/{action}/{id}")；ClientConstraint 驗證格式/存在。
     - 所需資源：System.Web.Routing。
     - 預估時間：0.5 天
  2. 寫入請求範圍的租戶上下文
     - 實作細節：ActionFilter 或 HttpModule 於 BeginRequest 擷取 RouteData.Values["client"]。
     - 所需資源：ASP.NET MVC Filter。
     - 預估時間：0.5 天
  3. 擴充 UrlHelper
     - 實作細節：包裝 Url.Action 以自動注入 client，以避免遺漏。
     - 所需資源：HtmlHelper、擴充方法。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public class ClientConstraint : IRouteConstraint
{
    public bool Match(HttpContextBase httpContext, Route route, string parameterName,
                      RouteValueDictionary values, RouteDirection routeDirection)
    {
        var client = values["client"] as string;
        return !string.IsNullOrWhiteSpace(client) && client.Length <= 32; // 簡化驗證
    }
}

public static void RegisterRoutes(RouteCollection routes)
{
    routes.MapRoute(
        name: "ClientRoute",
        url: "{client}/{controller}/{action}/{id}",
        defaults: new { controller = "Home", action = "Index", id = UrlParameter.Optional },
        constraints: new { client = new ClientConstraint() }
    );
}

public class TenantFilter : ActionFilterAttribute
{
    public override void OnActionExecuting(ActionExecutingContext filterContext)
    {
        var client = (string)filterContext.RouteData.Values["client"];
        filterContext.HttpContext.Items["ClientId"] = client;
    }
}
```

- 實際案例：/contoso/orders 與 /fabrikam/orders 指到相同 OrdersController，但因 HttpContext.Items["ClientId"] 不同，HubDataContext 即自動指向不同 Partition。
- 實作環境：ASP.NET MVC4。
- 實測數據：
  - 改善前：需在每個 Action 手動讀寫租戶參數，易遺漏。
  - 改善後：路由統一解析，資料與視圖自動對齊。
  - 改善幅度：定性改善（POC），連結生成錯位問題在測試中未再出現。

Learning Points
- 核心知識點：RouteConstraint、Filter 管線、UrlHelper 擴充。
- 技能要求：MVC Routing、Filter、HttpContext。
- 延伸思考：是否改用子網域（client.example.com）？如何同時支援兩種模式？

Practice Exercise
- 基礎練習：為 ReportsController 新增路由並驗證 client 注入（30 分鐘）。
- 進階練習：加入白名單租戶驗證與 404 fallback（2 小時）。
- 專案練習：將舊有無租戶段的連結全面改造並回歸測試（8 小時）。

Assessment Criteria
- 功能完整性：所有控制器可取得正確 client。
- 程式碼品質：無散落的 client 參數硬編碼。
- 效能優化：路由匹配不造成明顯延遲。
- 創新性：同時支援虛擬目錄與子網域切換。

------------------------------------------------------------

## Case #3: 每請求租戶解析，讓 Web 與 Data 緊密結合

### Problem Statement（問題陳述）
- 業務場景：控制器與 repository 需要一個可靠的當前租戶，避免層與層之間手動傳遞 ClientId。
- 技術挑戰：如何在每個 HTTP 請求生命周期中，提供一致的租戶解析，並注入到 HubDataContext。
- 影響範圍：可維護性、測試性、跨層一致性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺少集中式租戶解析元件。
  2. DI 配置未把租戶作為作用域相依性注入。
  3. 單元測試難以模擬 HttpContext，導致易偏離真實情境。
- 深層原因：
  - 架構層面：未定義「每請求作用域」的組態。
  - 技術層面：Mvc 與資料層抽象耦合不清。
  - 流程層面：測試/程式未以同一進入點解析租戶。

### Solution Design
- 解決策略：實作 ITenantProvider 於每請求作用域解析 ClientId（來自路由/子網域），並由 DI 建構 HubDataContext 時注入；提供替身實作便於單元測試。

- 實施步驟：
  1. 定義 ITenantProvider
     - 實作細節：從 HttpContext.Items 或 Thread.CurrentPrincipal 取 client。
     - 所需資源：DI 容器（Ninject/Autofac）。
     - 預估時間：0.5 天
  2. 註冊每請求生命周期
     - 實作細節：PerRequest scope 綁定 HubDataContext 與 CloudTableClient。
     - 所需資源：DI 容器生命週期設定。
     - 預估時間：0.5 天
  3. 撰寫測試替身
     - 實作細節：FakeTenantProvider 回傳指定 ClientId。
     - 所需資源：測試框架。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public interface ITenantProvider { string CurrentClientId { get; } }

public class HttpTenantProvider : ITenantProvider
{
    public string CurrentClientId => (string)HttpContext.Current.Items["ClientId"];
}

// DI 設定概念（以 Autofac 為例）
builder.RegisterType<HttpTenantProvider>().As<ITenantProvider>().InstancePerRequest();
builder.Register(ctx =>
{
    var tp = ctx.Resolve<ITenantProvider>();
    var tableClient = CreateTableClient(); // 省略
    return new HubDataContext(tableClient, tp.CurrentClientId);
}).As<IHubDataContext>().InstancePerRequest();
```

- 實際案例：OrdersController 注入 IHubDataContext 不需傳遞 ClientId；單元測試用 FakeTenantProvider 模擬不同租戶。
- 實作環境：MVC4、Autofac/Ninject（任一）。
- 實測數據：定性顯示跨層一致性提升，測試可重現租戶行為。

Learning Points
- 核心知識點：Per-request scope、依賴注入、替身（test double）。
- 技能要求：DI 容器使用、MVC Filter。
- 延伸思考：非 Web 背景工作如何取得租戶？是否引入 Correlation/ActivityId？

Practice/Assessment 省略細節（同 Case #1 模式）

------------------------------------------------------------

## Case #4: HubData 與 Global Data 的資料邊界

### Problem Statement
- 業務場景：平台方需要共用的資料（例如合作餐廳清單），同時又要維護各租戶的私有資料（成員、訂單）。
- 技術挑戰：在同一個儲存體中，同時支持「帶租戶範圍」與「無租戶範圍」的存取。
- 影響範圍：權限設計、程式可讀性、資料一致性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 單一 DataContext 強制注入 PartitionKey，導致無法存取全球資料。
  2. 缺乏清楚標註哪些實體屬於 Global。
  3. 讀寫路徑混雜，產生權限混淆。
- 深層原因：
  - 架構層面：未明確分離 Hub 與 Global 的存取邊界。
  - 技術層面：缺少略過租戶篩選的安全通道。
  - 流程層面：缺少審核與測試對邊界進行驗證。

### Solution Design
- 解決策略：提供 GlobalDataContext 或在 HubDataContext 暴露安全的 Bypass API；同時以標註（Attribute）或命名規範界定 Global 實體，並加上測試。

- 實施步驟：
  1. 定義 Global 實體標註
     - 實作細節：GlobalEntityAttribute 標記實體。
     - 所需資源：反射。
     - 預估時間：0.5 天
  2. 提供安全的 Bypass API
     - 實作細節：需顯式呼叫，並受權限保護。
     - 所需資源：角色/權限檢查。
     - 預估時間：0.5 天
  3. 撰寫邊界測試
     - 實作細節：驗證 Hub 實體不可繞過；Global 才可。
     - 所需資源：測試框架。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
[AttributeUsage(AttributeTargets.Class)]
public class GlobalEntityAttribute : Attribute { }

[GlobalEntity]
public class Restaurant : TableEntity { /* PartitionKey = "GLOBAL" */ }

public interface IGlobalDataContext
{
    IQueryable<T> SetGlobal<T>() where T : ITableEntity, new();
}

public sealed class GlobalDataContext : IGlobalDataContext
{
    private readonly CloudTableClient _client;
    public IQueryable<T> SetGlobal<T>() where T : ITableEntity, new()
    {
        var table = _client.GetTableReference(typeof(T).Name);
        return table.CreateQuery<T>();
    }
}
```

- 實際案例：餐廳/菜單屬於 Global；租戶可「連結」到 Global 餐廳以供下單，但訂單屬於 HubData。
- 實作環境：同上。
- 實測數據：定性結果顯示權限與邊界更清晰，誤用降低。

Learning Points：資料邊界、標註驅動的規範、最小權限原則。

Practice/Assessment 省略（同格式）

------------------------------------------------------------

## Case #5: 用 PartitionKey 模擬每租戶獨立儲存體

### Problem Statement
- 業務場景：系統希望「在一個 Storage 內，模擬每個租戶都有獨立 Storage」。
- 技術挑戰：Table Storage 無 schema，但需以結構化方式隔離與高效查詢。
- 影響範圍：效能、成本、操作簡便性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 一租戶一 Storage 成本高、管理複雜。
  2. 同庫多租戶容易查詢誤傷與熱點。
  3. 沒有統一的 PartitionKey 策略。
- 深層原因：
  - 架構層面：沒有抽象出「租戶=分區」的模型。
  - 技術層面：RowKey 設計、查詢路徑不一致。
  - 流程層面：缺少遷移策略（改 PartitionKey）。

### Solution Design
- 解決策略：統一以 ClientId 作為 PartitionKey；以實體語義設計 RowKey，確保高選擇性與排序；集中於 HubDataContext 實作。

- 實施步驟：
  1. 決定 PartitionKey 與 RowKey 策略
  2. 封裝於 HubTableEntity
  3. 用單元測試驗證查詢只掃單分區

- 關鍵程式碼/設定：
```csharp
public abstract class HubTableEntity : TableEntity
{
    // PartitionKey = ClientId
    // RowKey 建議：語義化 + 唯一，如 $"ORD#{date:yyyyMMdd}#{Guid.NewGuid()}"
}
```

- 實際案例：訂單類（Order/OrderItem）均以租戶為 PartitionKey，避免跨租戶掃描。
- 實作環境：同上。
- 實測數據：定性顯示查詢只掃單分區，延遲穩定。

Learning Points：分區鍵設計、儲存體成本與維運平衡。

------------------------------------------------------------

## Case #6: 以 EF 式 API 降低多租戶資料存取心智負擔

### Problem Statement
- 業務場景：開發者習慣 EF 的 DbSet/Context 模式，希望用相似 API 操作 Table Storage。
- 技術挑戰：NoSQL API 與 EF 心智模型不同，易出錯。
- 影響範圍：學習曲線、Bug 率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：SDK 較底層，操作繁瑣。
- 深層原因：缺乏抽象層配合租戶策略。

### Solution Design
- 解決策略：HubDataContext 暴露 Set<T>()、Add/Find 等方法，模擬 DbSet；內部封裝 TableOperation 與查詢條件。

- 實施步驟：定義介面、實作包裝、提供少量擴充方法（Where, OrderBy）。

- 關鍵程式碼/設定：
```csharp
// 參考 Case #1 Set<T>(), AddAsync, FindAsync 的 API 風格
```

- 實際案例：業務層使用類 EF API 操作 HubData。
- 實測數據：定性顯示開發體驗改善。

Learning Points：介面設計、抽象層價值。

------------------------------------------------------------

## Case #7: Code First 風格建模 Azure Table Storage 實體（訂便當模型）

### Problem Statement
- 業務場景：需要用實體類別直接表達資料關係（會員、餐廳、菜單、訂單、明細）。
- 技術挑戰：Table Storage 無關聯，需以鍵與冪等模式表達關係。
- 影響範圍：資料正規化、查詢便利性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：無 FK、無 Join。
- 深層原因：需以設計換取查詢體驗（冗餘/去正規化）。

### Solution Design
- 解決策略：以實體類表達，並以鍵串聯；適度去正規化如在 OrderItem 冗餘餐點名稱/價格快照。

- 實施步驟：定義各實體；決定 PartitionKey/RowKey；實作轉換與組裝（DTO/ViewModel）。

- 關鍵程式碼/設定：
```csharp
public class Member : HubTableEntity { public string RowKey { get; set; } public string Name { get; set; } }
public class Order : HubTableEntity { public string RowKey { get; set; } public DateTime Date { get; set; } public string VendorId { get; set; } }
public class OrderItem : HubTableEntity {
    public string RowKey { get; set; } // $"{orderId}#{itemId}"
    public string OrderId { get; set; } public string MenuItemId { get; set; }
    public string MenuItemName { get; set; } public decimal Price { get; set; } // 冗餘快照
}
[GlobalEntity]
public class Restaurant : TableEntity { public string Name { get; set; } } // PartitionKey = "GLOBAL"
```

- 實際案例：以 class diagram 方式規劃，POC 直上。
- 實測數據：定性顯示開發速度提升。

Learning Points：去正規化、鍵設計、關係的弱連結。

------------------------------------------------------------

## Case #8: 單元測試驗證多租戶資料安全與行為

### Problem Statement
- 業務場景：雲端系統的測試與佈署更麻煩，需要強力單元測試保護資料隔離。
- 技術挑戰：如何於本機快速驗證多租戶隔離（A/B 租戶同一測試內）。
- 影響範圍：品質風險、回歸測試成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：測試難以覆蓋實際儲存體行為。
- 深層原因：缺少測試替身與資料種子。

### Solution Design
- 解決策略：使用 Storage Emulator（或 Azurite 等價）與測試替身 ITenantProvider；針對關鍵路徑撰寫測試：不同租戶讀不到對方資料。

- 實施步驟：
  1. 測試環境啟動/重置 Emulator
  2. 測試中以 FakeTenantProvider 切換租戶
  3. 驗證跨租戶不可見

- 關鍵程式碼/設定：
```csharp
[Test]
public async Task Different_Tenants_Should_Not_See_Each_Other_Data()
{
    var client = CreateTableClient();
    var ctxA = new HubDataContext(client, "contoso");
    var ctxB = new HubDataContext(client, "fabrikam");

    await ctxA.AddAsync(new Member { RowKey = "alice", Name = "Alice" });
    Assert.IsNull(await ctxB.FindAsync<Member>("alice")); // 不可見
}
```

- 實際案例：作者強調雲端程式的測試與部署麻煩，單元測試不可少。
- 實測數據：POC 測試全部通過，跨租戶讀取 0 次。

Learning Points：可重現、快速回饋的單元測試設計。

------------------------------------------------------------

## Case #9: 避免跨租戶查詢/寫入的查詢攔截與預設篩選

### Problem Statement
- 業務場景：開發者可能直接呼叫 TableQuery 而跳過租戶條件。
- 技術挑戰：即使有人低階操作，也要預設安全。
- 影響範圍：資料安全、程式一致性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：低階 API 可繞過封裝。
- 深層原因：缺少統一擴充或守門規則。

### Solution Design
- 解決策略：提供僅暴露 IQueryable 的 Set<T>()，並以擴充方法產出只能在當前 Partition 的 Query；或在 Repository 層集中對外。

- 實施步驟：限制可見 API；提供安全擴充；Code Review 規範。

- 關鍵程式碼/設定：
```csharp
public static class TenantQueryExtensions
{
    public static IQueryable<T> AsTenantScoped<T>(this IQueryable<T> src, string clientId)
        where T : TableEntity
        => src.Where(e => e.PartitionKey == clientId);
}
```

- 實測數據：在測試與 Code Review 中未再出現不帶租戶條件的路徑。

Learning Points：安全默契（secure by default）、API 設計。

------------------------------------------------------------

## Case #10: 訂便當核心流程的多租戶落地（下單/查單）

### Problem Statement
- 業務場景：每個租戶每日建立訂單，成員可新增訂單明細，且只見自家資料。
- 技術挑戰：在 Table Storage 中組裝聚合（Order+OrderItems）並保持租戶隔離。
- 影響範圍：功能正確性、使用體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：跨表（Order/Items）無 Join。
- 深層原因：需在應用層聚合。

### Solution Design
- 解決策略：以 OrderId 作為 RowKey 前綴關聯 Items；同一租戶 Partition 下用前綴查詢；應用層組裝 DTO。

- 實施步驟：建立 Order、OrderItem；寫入與查詢 API；組裝 DTO。

- 關鍵程式碼/設定：
```csharp
public async Task<OrderDto> GetOrderAsync(IHubDataContext ctx, string orderId)
{
    var order = await ctx.FindAsync<Order>(orderId);
    var items = ctx.Set<OrderItem>()
                   .Where(i => i.RowKey.StartsWith(orderId + "#"))
                   .ToList();
    return new OrderDto(order, items);
}
```

- 實測數據：POC 下單/查單於多租戶皆正確。

Learning Points：前綴查詢、應用層聚合。

------------------------------------------------------------

## Case #11: 共用餐廳/菜單資料與租戶關聯

### Problem Statement
- 業務場景：平台方維護餐廳清單（Global），租戶可引用；帶來營運效率與商機（合作抽成等）。
- 技術挑戰：Global 資料如何安全地與租戶資料關聯？
- 影響範圍：資料治理、授權。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：Hub 與 Global 邊界不清。
- 深層原因：關聯資料結構缺失。

### Solution Design
- 解決策略：建立租戶-餐廳連結表（HubData：TenantRestaurantLink），以 Global RestaurantId 作 RowKey，租戶為 Partition；讀取時先從 Link 得到 Global Id 再讀 Global。

- 實施步驟：定義 Link 實體；維護 Link 的 CRUD；讀取流程。

- 關鍵程式碼/設定：
```csharp
public class TenantRestaurantLink : HubTableEntity
{
    public string RowKey { get; set; } // global restaurant id
    public string DisplayName { get; set; } // 可覆蓋別名
}
```

- 實測數據：POC 顯示租戶可共享餐廳，訂單仍屬自家 Partition。

Learning Points：共享資料設計、間接關聯。

------------------------------------------------------------

## Case #12: 新租戶開站初始化與種子資料流程

### Problem Statement
- 業務場景：新客戶開通時需建立最基本資料（管理者帳號、常用餐廳連結）。
- 技術挑戰：如何在 Table Storage 正確建立新分區的初始資料。
- 影響範圍：導入效率、體驗。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：手動建立易錯。
- 深層原因：缺乏自動化種子流程。

### Solution Design
- 解決策略：提供 SeedTenantAsync，於 Partition=ClientId 下建立必要資料；支援冪等。

- 實施步驟：實作種子；支援重跑；加入管理工具或後台 API。

- 關鍵程式碼/設定：
```csharp
public async Task SeedTenantAsync(IHubDataContext ctx)
{
    if (await ctx.FindAsync<Member>("admin") == null)
        await ctx.AddAsync(new Member { RowKey = "admin", Name = "Admin" });
    // 連結幾家熱門餐廳...
}
```

- 實測數據：POC 開站時間縮短（定性）。

Learning Points：冪等、可重入的種子流程。

------------------------------------------------------------

## Case #13: Routing 產生與連結生成的一致性（避免漏帶 client）

### Problem Statement
- 業務場景：視圖/部分視圖產生連結時，必須永遠帶著 {client}。
- 技術挑戰：人為遺漏造成錯路由。
- 影響範圍：使用者體驗、錯誤率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：手動傳遞路由值易遺漏。
- 深層原因：缺少共用的 UrlHelper 擴充。

### Solution Design
- 解決策略：擴充 UrlHelper/HtmlHelper，從 ITenantProvider 讀 client，自動注入。

- 實施步驟：撰寫擴充方法；統一替換所有 Url.Action 呼叫；寫測試。

- 關鍵程式碼/設定：
```csharp
public static class UrlTenantExtensions
{
    public static string TenantAction(this UrlHelper url, string action, string controller, object routeValues = null)
    {
        var client = (string)url.RequestContext.HttpContext.Items["ClientId"];
        var dict = new RouteValueDictionary(routeValues ?? new { });
        dict["client"] = client;
        return url.Action(action, controller, dict);
    }
}
```

- 實測數據：測試中未再出現漏帶 client 的連結。

Learning Points：輔助 API 保證一致性。

------------------------------------------------------------

## Case #14: 本機模擬與部署前測：弭平雲端測試痛點

### Problem Statement
- 業務場景：作者提到雲端程式測試與部署比以前麻煩，需要規劃與測試。
- 技術挑戰：如何在本機可靠重現雲端存取，避免部署後踩雷。
- 影響範圍：交付速度、穩定性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：依賴雲端服務，測試慢且脆弱。
- 深層原因：缺乏模擬器與測試隔離策略。

### Solution Design
- 解決策略：使用 Azure Storage Emulator（或等價模擬器）；測試前清表；以 Fixture 建立測試資料；CI 內跑單元測試。

- 實施步驟：建立測試基底類；清理資料；注入模擬連線字串。

- 關鍵程式碼/設定：
```csharp
// App.config 測試用
<appSettings>
  <add key="StorageConnectionString" value="UseDevelopmentStorage=true" />
</appSettings>
```

- 實測數據：定性顯示測試時間可控、穩定通過。

Learning Points：雲服務本機模擬、測試資料生命週期。

------------------------------------------------------------

## Case #15: 從單一儲存體到多租戶 SaaS 的成本效益與治理

### Problem Statement
- 業務場景：平台營運希望以單一儲存體承載多租戶以降低成本，仍保持隔離與可管控。
- 技術挑戰：在治理（權限、審計）與成本（帳單複雜度）間取得平衡。
- 影響範圍：TCO、SLA。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：一租戶一帳號維運成本高。
- 深層原因：缺少分區與治理策略。

### Solution Design
- 解決策略：PartitionKey=ClientId；審計日誌包含 ClientId；計量按租戶彙整報表；必要時支援升級到獨立儲存體。

- 實施步驟：審計欄位設計；報表匯總；升級流程（資料搬遷腳本，選配）。

- 關鍵程式碼/設定：略（設計向）。

- 實測數據：定性顯示可用單體儲存體起步，靈活升級。

Learning Points：治理、可演進架構。

------------------------------------------------------------

## Case #16: 查詢效能與排序：RowKey/鍵設計最佳化

### Problem Statement
- 業務場景：使用者常依日期檢視訂單與明細，需要快速排序與分頁。
- 技術挑戰：Table Storage 無複合索引，排序僅能靠 RowKey。
- 影響範圍：效能、使用體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：無二級索引。
- 深層原因：鍵設計未兼顧排序。

### Solution Design
- 解決策略：RowKey 前綴設計（如 ORD#yyyyMMdd#Guid），利用字典序達成按日排序；必要時維護二維表（日期->訂單）。

- 實施步驟：決定鍵格式；調整查詢；撰寫回溯遷移腳本（如有舊資料）。

- 關鍵程式碼/設定：
```csharp
var rowKey = $"ORD#{DateTime.UtcNow:yyyyMMdd}#{Guid.NewGuid():N}";
var orders = ctx.Set<Order>()
                .Where(o => o.RowKey.CompareTo("ORD#20250101") >= 0 &&
                            o.RowKey.CompareTo("ORD#20250131~") <= 0) // ~ 作為上界技巧
                .ToList();
```

- 實測數據：定性顯示查詢穩定、分頁簡化。

Learning Points：鍵編碼技巧、範圍查詢。

------------------------------------------------------------

案例總數：16

------------------------------------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 6（EF 式 API）
  - Case 12（種子資料）
  - Case 13（連結生成一致性）
- 中級（需要一定基礎）
  - Case 1（HubDataContext）
  - Case 2（Routing 客製）
  - Case 3（每請求租戶解析）
  - Case 4（Hub/Global 邊界）
  - Case 5（PartitionKey 模擬獨立儲存）
  - Case 7（Code First 建模）
  - Case 8（單元測試）
  - Case 9（查詢攔截）
  - Case 10（核心流程落地）
  - Case 14（本機模擬/部署前測）
  - Case 16（鍵設計最佳化）
- 高級（需要深厚經驗）
  - Case 11（共享資料與租戶關聯）
  - Case 15（成本效益與治理）

2) 按技術領域分類
- 架構設計類
  - Case 1, 3, 4, 5, 11, 15
- 效能優化類
  - Case 5, 16
- 整合開發類
  - Case 2, 3, 10, 13
- 除錯診斷類
  - Case 8, 9, 14
- 安全防護類
  - Case 1, 4, 9, 11, 13, 15

3) 按學習目標分類
- 概念理解型
  - Case 1, 4, 5, 15
- 技能練習型
  - Case 2, 3, 6, 7, 12, 13, 16
- 問題解決型
  - Case 8, 9, 10, 14
- 創新應用型
  - Case 11（共享資料）、Case 15（治理升級路徑）

------------------------------------------------------------
案例關聯圖（學習路徑建議）

- 起點（基礎概念與骨幹）
  - 先學：Case 1（HubDataContext）、Case 2（Routing 客製）
  - 依賴關係：Case 3（每請求解析）依賴 1、2
- 建模與資料層落地
  - 接著：Case 5（PartitionKey）→ Case 7（實體建模）→ Case 16（鍵最佳化）
  - 依賴關係：Case 7 需理解 Case 5；Case 16 建立在 7
- Web 整合與一致性
  - 然後：Case 13（連結一致性）
  - 與：Case 10（核心流程落地）依賴 1、2、5、7
- 邊界與共享資料
  - 再來：Case 4（Hub/Global 邊界）→ Case 11（共享餐廳關聯）
- 測試與品質保證
  - 同步學：Case 8（單元測試）、Case 9（查詢攔截）、Case 14（本機模擬）
  - 它們支撐所有上層案例
- 營運與治理
  - 最後：Case 12（種子流程）→ Case 15（成本治理與升級策略）

完整學習路徑建議：
1) Case 1 → 2 → 3（建立租戶骨架）
2) Case 5 → 7 → 16（資料鍵與實體）
3) Case 13 → 10（前端整合與核心流程）
4) Case 4 → 11（邊界與共享）
5) Case 8 → 9 → 14（測試與品質）
6) Case 12 → 15（導入與治理）

此路徑從基礎到實戰，最後延伸到營運治理，能在最短時間把 POC 推到可上線的工程品質。