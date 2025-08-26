以下內容依據原文中可提煉的真實問題、根因、解法與實際效益，整理出 15 個具教學與實作價值的案例，並補充必要的程式碼與步驟，方便直接用於實戰教學、專案練習與能力評估。實作環境預設為 .NET 3.5 SP1、Entity Framework v1（VS2008），模型以 .edmx 維護，編譯時由 EntityDeploy 產生 csdl/ssdl/msl 內嵌資源。

## Case #1: 超大型資料庫單一 .edmx 難以維護的模型分割

### Problem Statement（問題陳述）
業務場景：企業級系統演進多年，Schema 複雜、歷史表未刪，新表持續增加，超過 100 張資料表與多個 View。單一 .edmx 模型在設計、瀏覽、衝突解決與重新產生時成本極高，開發效率下滑，建置風險上升。團隊希望以模組化方式分治模型與邏輯，降低耦合並提升可維護性。  
技術挑戰：如何將單一龐大 EF 模型切割為多個 .edmx，同時保持查詢、部署、版本升級上的可行性。  
影響範圍：影響開發效率、模型品質、建置穩定性與後續演進成本。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 模型過大：單一 .edmx 需包覆數百個 Table/View，視覺化工具與檔案維護成本極高。
2. 設計工具侷限：EF v1 設計工具對超大模型操作（刪/加）易出錯。
3. 組件耦合：所有實體/對應集中在單一組件，難於模組化與分工。

深層原因：
- 架構層面：單體式 O/R 映射設計，缺乏明確的模組邊界。
- 技術層面：EF v1 的工具與 LINQ provider 偏向單一容器使用。
- 流程層面：未建立以領域/模組分治的模型治理流程。

### Solution Design（解決方案設計）
解決策略：依業務模組切割 Schema，為每個模組建立獨立 .edmx 與邏輯層，編譯為各自的組件並將 csdl/ssdl/msl 內嵌為資源。跨模組查詢則透過在執行階段合併多組 metadata 至單一 ObjectContext 來實現。

實施步驟：
1. 模組邊界切割
- 實作細節：依 bounded context/子系統切割表與 View；避免跨模組循環依賴。
- 所需資源：架構設計、Schema 清單、UML/ER 圖。
- 預估時間：1-2 天（依 Schema 複雜度）

2. 建立多個 .edmx 並內嵌資源
- 實作細節：每個模組建立一個 .edmx（Build Action=EntityDeploy，預設會產生內嵌 csdl/ssdl/msl）。
- 所需資源：VS2008、EF v1 工具。
- 預估時間：0.5-1 天

3. 更新模組專案結構
- 實作細節：每個模組封裝其 Repository/Service 與 .edmx，對外只暴露必要 API。
- 所需資源：解決方案結構調整。
- 預估時間：0.5-1 天

關鍵程式碼/設定：
無（此案以設計與專案結構為主）

實際案例：大型 AP 用到 100+ 表與多個 View，拆為銷售、客戶、帳務三個 .edmx，交由三支團隊並行開發維護。  
實作環境：.NET 3.5 SP1、EF v1、VS2008。  
實測數據：  
改善前：單一 .edmx 操作卡頓且頻繁產生建置錯誤。  
改善後：每個 .edmx 明顯輕量、可由專責團隊維護。  
改善幅度：開發效率與穩定度顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- 模型分割的邊界設計（bounded context）
- EF v1 的 EntityDeploy 與內嵌資源
- 模組化專案結構與封裝

技能要求：
- 必備技能：EF 模型設計、.edmx 操作
- 進階技能：領域驅動設計、模組化架構

延伸思考：
- 還能應用在多團隊協作、漸進式遷移舊系統。
- 風險：跨模組實體重名、關聯關係消失。
- 優化：建立命名規約與共用基礎模型包。

Practice Exercise（練習題）
- 基礎練習：將 30 張表拆成兩個 .edmx（30 分）
- 進階練習：為每個 .edmx 加入對應的 Repository 層（2 小時）
- 專案練習：完成三模組分割與封裝、示範跨模組查詢（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：分割後仍可支援原查詢/更新
- 程式碼品質（30%）：清晰邊界與封裝
- 效能優化（20%）：設計工具操作流暢
- 創新性（10%）：分割策略與自動化腳本

---

## Case #2: 多 ObjectContext 需分別 SaveChanges 的一致性與複雜度

### Problem Statement（問題陳述）
業務場景：拆成多個 .edmx 後，每個模組對資料做更新需呼叫各自的 ObjectContext.SaveChanges()。若一次操作涉及多模組，需手動協調多次提交。  
技術挑戰：多個 SaveChanges 帶來的一致性和流程複雜度管理。  
影響範圍：交易一致性、錯誤處理複雜度、程式碼重複。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 一個 .edmx 對應一個 ObjectContext。
2. EF v1 無法跨 Context 自然合併工作單元。
3. 手動協調 SaveChanges 容易引發部分提交。

深層原因：
- 架構層面：每個模組獨立 UoW，缺乏跨模組 UoW 聚合。
- 技術層面：EF v1 不支援跨 Context 聚合。
- 流程層面：缺乏統一提交點（commit point）設計。

### Solution Design（解決方案設計）
解決策略：在執行階段把多組 metadata 併入同一 EntityConnection，建立單一 ObjectContext 操作所有模組的實體，集中一次 SaveChanges。

實施步驟：
1. 建構合併 metadata 的 EntityConnection
- 實作細節：metadata 欄位串接多組 csdl/ssdl/msl。
- 所需資源：EntityConnectionStringBuilder。
- 預估時間：1 小時

2. 以單一 ObjectContext 執行更新
- 實作細節：同一 Context 追蹤所有修改後一次 SaveChanges。
- 所需資源：共同的資料庫連線字串。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
using System.Data.EntityClient;
using System.Data.Objects;

var ecsb = new EntityConnectionStringBuilder
{
    Provider = "System.Data.SqlClient",
    ProviderConnectionString = "Data Source=.;Initial Catalog=AppDb;Integrated Security=True;",
    Metadata =
      "res://*/Model1.csdl|res://*/Model1.ssdl|res://*/Model1.msl|" +
      "res://*/Model2.csdl|res://*/Model2.ssdl|res://*/Model2.msl"
};

using (var conn = new EntityConnection(ecsb.ConnectionString))
using (var ctx = new ObjectContext(conn))
{
    // 在同一個 ctx 追蹤來自兩個模型的變更
    // ... attach/modify entities here ...
    ctx.SaveChanges(); // 單次提交
}
```

實際案例：原需對 A/B 模組各呼叫 SaveChanges；合併後一次 SaveChanges 完成。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：每模組各一個 SaveChanges，錯誤恢復複雜。  
改善後：單一 SaveChanges。  
改善幅度：提交流程簡化（定性），一致性風險降低。

Learning Points（學習要點）
核心知識點：
- EntityConnection 多組 metadata
- ObjectContext 作為單一 UoW

技能要求：
- 必備技能：EF 連線與追蹤
- 進階技能：跨模組一致性設計

延伸思考：
- 可應用在多模組一致提交。
- 風險：跨資料庫無法原子，需分散式交易另議。
- 優化：以 TransactionScope 控制交易邊界。

Practice Exercise（練習題）
- 基礎：以單一 ObjectContext 實作兩模組更新一次提交（30 分）
- 進階：加入錯誤回滾與重試（2 小時）
- 專案：重構既有多次 SaveChanges 成單一提交（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：單次提交涵蓋所有修改
- 程式碼品質（30%）：清晰的 UoW 邊界
- 效能優化（20%）：避免多次連線開銷
- 創新性（10%）：通用提交協調器設計

---

## Case #3: 跨 Context 的 JOIN 查詢不支援

### Problem Statement（問題陳述）
業務場景：報表與查詢需要同時使用 A 模組與 B 模組的實體資料進行 JOIN。  
技術挑戰：EF v1 不支援跨 ObjectContext（亦即跨 .edmx）直接 JOIN 的 LINQ/eSQL 查詢。  
影響範圍：查詢功能受限、需回退至存儲程序或手寫 SQL。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. EF v1 限制：不支援跨 Context 查詢。
2. 各 .edmx 有獨立 EntityContainer。
3. 預設連線只載入單組 metadata。

深層原因：
- 架構層面：模型分割斷開跨模組關聯。
- 技術層面：LINQ provider 與 eSQL 解析器需單一 MetadataWorkspace。
- 流程層面：查詢層未設計跨容器策略。

### Solution Design（解決方案設計）
解決策略：在連線字串 metadata 欄位串接多組 csdl/ssdl/msl，建立單一 ObjectContext 後，用 eSQL 以「容器限定名（ContainerQualified）」從不同容器取資料並進行 JOIN。

實施步驟：
1. 合併 metadata 並建立 ObjectContext（同 Case #2）
2. 使用 eSQL 寫跨容器 JOIN
- 實作細節：FROM 子句使用 Model1Container.EntitySet 與 Model2Container.EntitySet。
- 所需資源：ObjectContext.CreateQuery<DbDataRecord>()。
- 預估時間：1-2 小時

關鍵程式碼/設定：
```csharp
string esql = @"
SELECT c.CustomerId, c.Name, o.OrderId, o.Total
FROM Model1Container.Customers AS c
JOIN Model2Container.Orders AS o
ON c.CustomerId = o.CustomerId";

using (var ctx = new ObjectContext(new EntityConnection(ecsb.ConnectionString)))
{
    var query = ctx.CreateQuery<System.Data.Common.DbDataRecord>(esql);
    foreach (var row in query)
    {
        int customerId = (int)row[0];
        string name    = (string)row[1];
        int orderId    = (int)row[2];
        decimal total  = (decimal)row[3];
        // ... use data
    }
}
```

實際案例：報表服務以 eSQL 完成跨模組 JOIN，不再回退至存儲程序。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：跨 Context JOIN 不支援。  
改善後：eSQL 跨容器 JOIN 可行。  
改善幅度：功能可行性 100% 達成。

Learning Points（學習要點）
核心知識點：
- eSQL 容器限定名稱
- 多 metadata 合併的查詢

技能要求：
- 必備技能：eSQL、EF 連線設定
- 進階技能：查詢優化與投影

延伸思考：
- 可用於跨模組報表、聚合查詢。
- 風險：失去導航屬性便利性。
- 優化：投影至 DTO、建立可重用查詢片段。

Practice Exercise（練習題）
- 基礎：撰寫一個跨兩容器的 INNER JOIN 查詢（30 分）
- 進階：加入過濾、排序、分頁（2 小時）
- 專案：完成三容器 JOIN 的統一查詢服務（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：JOIN 正確與覆蓋需求
- 程式碼品質（30%）：清楚的 eSQL 與參數化
- 效能優化（20%）：合理的索引使用
- 創新性（10%）：可重用查詢構件

---

## Case #4: 跨 .edmx 無法使用 Navigation Property 的替代方案

### Problem Statement（問題陳述）
業務場景：原本在單一模型中可用導航屬性（Navigation Property）取得關聯資料；分割模型後跨 .edmx 不再可用。  
技術挑戰：導航屬性依賴 AssociationSet，EF v1 無法跨 Context 定義關聯。  
影響範圍：需手動 JOIN 與資料組裝，代碼可讀性下降。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. AssociationSet 無法跨越 context。
2. 跨模型缺少關聯定義。
3. 導航屬性生成依賴單一模型。

深層原因：
- 架構層面：拆分模型切斷關聯。
- 技術層面：EF v1 只在單容器內解析關聯。
- 流程層面：未規劃 DTO 與查詢層投影。

### Solution Design（解決方案設計）
解決策略：以 eSQL/手動 JOIN 取得跨模組資料，再投影到專用的 DTO；在需要 LINQ 的場景，維持單模組內 LINQ，跨模組用 eSQL。

實施步驟：
1. 設計跨模組 DTO
- 實作細節：定義最小欄位集，避免依賴模組型別。
- 所需資源：共用類別庫。
- 預估時間：1 小時

2. 以 eSQL JOIN 後投影填充 DTO
- 實作細節：DbDataRecord 取值→組裝 DTO。
- 所需資源：ObjectContext。
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public class CustomerOrderDto
{
    public int CustomerId { get; set; }
    public string Name { get; set; }
    public int OrderId { get; set; }
    public decimal Total { get; set; }
}

var esql = @"
SELECT c.CustomerId, c.Name, o.OrderId, o.Total
FROM Model1Container.Customers AS c
JOIN Model2Container.Orders AS o ON c.CustomerId = o.CustomerId";

var rows = ctx.CreateQuery<System.Data.Common.DbDataRecord>(esql);
var list = new List<CustomerOrderDto>();
foreach (var r in rows)
{
    list.Add(new CustomerOrderDto {
        CustomerId = (int)r[0],
        Name       = (string)r[1],
        OrderId    = (int)r[2],
        Total      = (decimal)r[3]
    });
}
```

實際案例：跨模組導航改以 DTO 投影實現。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：無法使用跨模組導航。  
改善後：以 JOIN + DTO 達成相同目的。  
改善幅度：功能可用性恢復。

Learning Points（學習要點）
核心知識點：
- 導航屬性 vs. 明確 JOIN
- DTO 隔離跨模組依賴
- eSQL 投影技巧

技能要求：
- 必備技能：eSQL、C# DTO
- 進階技能：查詢與投影最佳化

延伸思考：
- 可應用在跨界限內容查詢。
- 限制：失去延遲載入便利性。
- 優化：建立查詢方法庫（Query Object）。

Practice Exercise（練習題）
- 基礎：建立跨模組 DTO 並以 eSQL 填充（30 分）
- 進階：新增聚合欄位與分頁（2 小時）
- 專案：設計可重用的查詢+DTO 模式（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：DTO 資料完整正確
- 程式碼品質（30%）：清晰邏輯與命名
- 效能優化（20%）：查詢與資料轉換成本
- 創新性（10%）：抽象與重用程度

---

## Case #5: 以組件封裝 .edmx 與邏輯的模組化部署

### Problem Statement（問題陳述）
業務場景：因應模組化需求，需將 .edmx 及相關邏輯封裝到獨立組件，方便分發、維護與更新。  
技術挑戰：如何部署 csdl/ssdl/msl 並在執行階段可被 EF 識別。  
影響範圍：部署簡化、版本管理、可維護性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. EF 需要在執行階段取得 metadata。
2. 若使用檔案路徑管理，部署易錯。
3. 缺乏標準化封裝與命名。

深層原因：
- 架構層面：無模組封裝與部署策略。
- 技術層面：不熟悉 res:// 內嵌資源載入。
- 流程層面：部署依賴人工步驟。

### Solution Design（解決方案設計）
解決策略：所有 .edmx 維持 Build Action=EntityDeploy，讓 csdl/ssdl/msl 內嵌到各自組件，連線字串以 res://*/ModelX.* 取用，達成模組化部署。

實施步驟：
1. 設計組件命名與版本策略
- 實作細節：Module.Customer.dll、Module.Order.dll 等。
- 所需資源：命名規範。
- 預估時間：0.5 天

2. 設定內嵌資源與連線字串
- 實作細節：metadata=res://*/Model1.csdl|res://*/Model1.ssdl|res://*/Model1.msl 等。
- 所需資源：App/Web.config。
- 預估時間：1 小時

關鍵程式碼/設定：
```ini
<connectionStrings>
  <add name="AppEntities"
       connectionString="
         metadata=res://*/Model1.csdl|res://*/Model1.ssdl|res://*/Model1.msl|
                  res://*/Model2.csdl|res://*/Model2.ssdl|res://*/Model2.msl;
         provider=System.Data.SqlClient;
         provider connection string='Data Source=.;Initial Catalog=AppDb;Integrated Security=True;'" 
       providerName="System.Data.EntityClient" />
</connectionStrings>
```

實際案例：各模組打包後只需放入 bin，即可被 eSQL/Context 使用。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：手動拷貝對應檔易遺漏。  
改善後：內嵌資源自包含，部署穩定。  
改善幅度：部署錯誤顯著下降（定性）。

Learning Points（學習要點）
核心知識點：
- res:// 內嵌資源尋址
- EntityDeploy 的產物

技能要求：
- 必備技能：組態管理
- 進階技能：版本相容策略

延伸思考：
- 可應用於外掛式模組。
- 限制：res://*/ 需組件載入於 AppDomain。
- 優化：啟動時預載入指定模組組件。

Practice Exercise（練習題）
- 基礎：將 .edmx 設為內嵌資源並以 res:// 取用（30 分）
- 進階：多模組連線字串組態（2 小時）
- 專案：完成一鍵部署腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：內嵌資源可被載入
- 程式碼品質（30%）：組態清晰
- 效能優化（20%）：啟動載入時間控制
- 創新性（10%）：部署自動化

---

## Case #6: 新增模組不需重編譯其他模組的擴充機制

### Problem Statement（問題陳述）
業務場景：持續新增模組，要求不需重編譯既有模組即可使用新模組資料參與查詢。  
技術挑戰：如何讓應用在執行時驅動新的 metadata，而不改變既有組件。  
影響範圍：發版效率、系統可擴充性。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 一般情況下新增型別需重新參考與編譯。
2. metadata 清單硬編在 config 或程式碼中。
3. 未建立動態載入流程。

深層原因：
- 架構層面：缺乏外掛式模組機制。
- 技術層面：不了解 res://*/ 搜索行為需已載入組件。
- 流程層面：發版流程依賴手動更新。

### Solution Design（解決方案設計）
解決策略：以外掛目錄存放模組 DLL；啟動時掃描並 Assembly.LoadFrom 預載入；動態組合 EntityConnectionStringBuilder.Metadata；建立單一 ObjectContext 提供 eSQL 查詢。LINQ 僅於模組內實作。

實施步驟：
1. 啟動載入模組組件
- 實作細節：掃描 bin/Modules/*.dll 並載入。
- 所需資源：檔案系統 API。
- 預估時間：1-2 小時

2. 動態組合 metadata 字串
- 實作細節：串接所有已載入模組的 ModelX.csdl/ssdl/msl。
- 所需資源：EntityConnectionStringBuilder。
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var moduleDir = System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Modules");
foreach (var dll in System.IO.Directory.GetFiles(moduleDir, "*.dll"))
{
    System.Reflection.Assembly.LoadFrom(dll); // 讓 res://*/ 可見
}

string BuildMetadata(params string[] modelNames)
{
    var parts = new List<string>();
    foreach (var m in modelNames)
        parts.AddRange(new[] { $"res://*/{m}.csdl", $"res://*/{m}.ssdl", $"res://*/{m}.msl" });
    return string.Join("|", parts.ToArray());
}

var ecsb = new EntityConnectionStringBuilder
{
    Provider = "System.Data.SqlClient",
    ProviderConnectionString = "...",
    Metadata = BuildMetadata("Model1", "Model2", "Model3") // 新模組加入此清單即可
};
```

實際案例：新增 Module.Inventory.dll 後，無需重編譯其他模組，即可參與 eSQL 查詢。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：需重編譯或手動改程式碼。  
改善後：僅丟 DLL 至 Modules/ 並更新 metadata 清單。  
改善幅度：發版流程明顯簡化。

Learning Points（學習要點）
核心知識點：
- 外掛組件載入與 AppDomain
- 動態 metadata 組合

技能要求：
- 必備技能：反射、組態
- 進階技能：模組化平台設計

延伸思考：
- 風險：版本不相容需偵測。
- 限制：LINQ 的強型別需編譯期參考。
- 優化：以命名慣例自動推導 model 名。

Practice Exercise（練習題）
- 基礎：動態載入指定 DLL（30 分）
- 進階：自動拼接 metadata 並測試查詢（2 小時）
- 專案：做一個模組管理器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：新增模組可即時查詢
- 程式碼品質（30%）：載入/錯誤處理完善
- 效能優化（20%）：載入與快取策略
- 創新性（10%）：自動發現與驗證

---

## Case #7: 保留基本 LINQ 能力（CreateQuery<T> 起點）

### Problem Statement（問題陳述）
業務場景：雖跨模組查詢用 eSQL，但在模組內仍需使用 LINQ to Entities 進行易讀的查詢。  
技術挑戰：在 non-typed ObjectContext 中如何取得可 LINQ 化的 ObjectQuery<T>。  
影響範圍：開發體驗、查詢維護性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 跨模組組合後沒有單一產生的 typed Context。
2. 需要以字串起點建立 EntitySet。
3. 類型位於模組組件內。

深層原因：
- 架構層面：跨模組共用 Context。
- 技術層面：CreateQuery<T>() + ContainerQualified 名稱。
- 流程層面：模組內查詢由模組維護。

### Solution Design（解決方案設計）
解決策略：透過 ObjectContext.CreateQuery<T>("Container.EntitySet") 取得 ObjectQuery<T>，後續即使用 LINQ 撰寫條件與投影。只在模組內使用本模組型別。

實施步驟：
1. 以 CreateQuery<T> 取得實體集
2. 撰寫 LINQ 篩選與投影

關鍵程式碼/設定：
```csharp
using System.Linq;

// 型別 Customer 來自 Model1 模組組件
var customers = ctx.CreateQuery<Model1Namespace.Customer>("Model1Container.Customers");
var vip = from c in customers
          where c.Level == "VIP"
          select new { c.CustomerId, c.Name };
```

實際案例：模組內保留 LINQ 可讀性，跨模組仍用 eSQL。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：LINQ 受限於 typed Context。  
改善後：以 CreateQuery<T> 保留 LINQ 體驗。  
改善幅度：可讀性回升（定性）。

Learning Points（學習要點）
核心知識點：
- CreateQuery<T>() 用法
- 容器限定的實體集名稱

技能要求：
- 必備技能：LINQ to Entities
- 進階技能：混合查詢策略設計

延伸思考：
- 可應用於多模型共用 Context。
- 限制：需引用模組型別。
- 優化：查詢擴充方法庫化。

Practice Exercise（練習題）
- 基礎：以 CreateQuery<T> 撰寫一個 LINQ 查詢（30 分）
- 進階：加入分頁與排序（2 小時）
- 專案：整理常用 LINQ 片段為擴充方法（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：查詢正確
- 程式碼品質（30%）：LINQ 可讀性
- 效能優化（20%）：產生 SQL 合理
- 創新性（10%）：可重用性

---

## Case #8: 又臭又長的 Entity Connection 連接字串維護

### Problem Statement（問題陳述）
業務場景：多模型合併後，metadata 連接字串極長且難以維護，易出錯。  
技術挑戰：如何以程式產生與驗證連接字串，避免手寫錯漏。  
影響範圍：組態錯誤率、維護成本。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多組 csdl/ssdl/msl 需以 | 串接。
2. 手動編輯易遺漏或順序錯誤。
3. 檔案/資源路徑相似。

深層原因：
- 架構層面：多模型設計必然複雜。
- 技術層面：不熟悉 EntityConnectionStringBuilder。
- 流程層面：缺少產生器工具。

### Solution Design（解決方案設計）
解決策略：使用 EntityConnectionStringBuilder 組合 Provider、ProviderConnectionString 與 Metadata，並集中在一處產生與測試。

實施步驟：
1. 撰寫產生器方法
2. 啟動時驗證資源可解析

關鍵程式碼/設定：
```csharp
EntityConnectionStringBuilder BuildConn(string providerConn, params string[] models)
{
    string md = string.Join("|", models.SelectMany(m => new[]{
        $"res://*/{m}.csdl", $"res://*/{m}.ssdl", $"res://*/{m}.msl"
    }).ToArray());

    return new EntityConnectionStringBuilder
    {
        Provider = "System.Data.SqlClient",
        ProviderConnectionString = providerConn,
        Metadata = md
    };
}

// 使用
var ecsb = BuildConn("Data Source=.;Initial Catalog=AppDb;Integrated Security=True;",
                     "Model1", "Model2", "Model3");
```

實際案例：以程式產生 metadata 字串，避免人為錯誤。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：連接字串易誤。  
改善後：自動產生與驗證。  
改善幅度：錯誤率下降（定性）。

Learning Points（學習要點）
核心知識點：
- EntityConnectionStringBuilder
- res:// 資源組合

技能要求：
- 必備技能：組態管理
- 進階技能：工具化

延伸思考：
- 可應用於 CI/CD 注入。
- 限制：仍需先載入組件。
- 優化：加入存在性檢查與記錄。

Practice Exercise（練習題）
- 基礎：將手寫改成程式產生（30 分）
- 進階：加入驗證與記錄（2 小時）
- 專案：做成小工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：連線成功
- 程式碼品質（30%）：產生器可維護
- 效能優化（20%）：啟動時間控制
- 創新性（10%）：工具可用性

---

## Case #9: 設計工具中表刪了再拉回導致 Build 失敗

### Problem Statement（問題陳述）
業務場景：在 EF 設計工具中刪除再加入表後，專案建置失敗。  
技術挑戰：設計器未完全移除舊對應或殘留型別，導致衝突。  
影響範圍：阻斷建置、影響進度。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 設計器留下殘存對應或重複型別。
2. 局部修改未同步到 MSL/CSDL/SSDL。
3. 自動產生程式碼存在重複定義。

深層原因：
- 架構層面：大模型對工具容錯要求高。
- 技術層面：EF v1 設計器缺陷。
- 流程層面：未建立手動校正流程。

### Solution Design（解決方案設計）
解決策略：手動清理 .edmx 內三段（CSDL/SSDL/MSL）中重複定義與殘留對應，或以版本管控回退再正確操作；必要時手動編輯後重建。

實施步驟：
1. 檢查重複的 EntityType/EntitySet 名稱
2. 清理 MSL 中多餘 EntitySetMapping/AssociationSetMapping
3. 重新產生實體類別檔

關鍵程式碼/設定（示意清理 CSDL 類型重複）：
```xml
<!-- CSDL: 移除重複的 EntityType 定義 -->
<Schema Namespace="Model1" ...>
  <!-- 確保 Customer 僅定義一次 -->
  <EntityType Name="Customer"> ... </EntityType>
</Schema>
```

實際案例：清理殘留後恢復建置。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：建置失敗。  
改善後：建置成功。  
改善幅度：可用性恢復。

Learning Points（學習要點）
核心知識點：
- .edmx 結構（CSDL/SSDL/MSL）
- 常見設計器殘留問題

技能要求：
- 必備技能：XML 編修、比對工具
- 進階技能：自動檢測腳本

延伸思考：
- 可應用於 CI 檢查 .edmx 健康度。
- 限制：手動編輯需小心。
- 優化：工具化檢查重複定義。

Practice Exercise（練習題）
- 基礎：修復一個重複實體定義案例（30 分）
- 進階：寫一段 XPATH 驗證規則（2 小時）
- 專案：製作 .edmx 健康檢查器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能重現並修復問題
- 程式碼品質（30%）：清晰的檢查規則
- 效能優化（20%）：分析速度
- 創新性（10%）：自動化程度

---

## Case #10: View 無法指定 Key 導致結果不對或 Build 失敗

### Problem Statement（問題陳述）
業務場景：將資料庫 View 拉入 .edmx 後，無法明確指定 Key，導致追蹤/查詢異常或建置錯誤。  
技術挑戰：EF 需要主鍵資訊以進行實體追蹤。  
影響範圍：資料一致性、查詢正確性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. View 無自然主鍵，設計器未生成 Key。
2. EF 追蹤需 Key 決定實體身份。
3. 映射不完整導致建置失敗。

深層原因：
- 架構層面：以 View 暴露資料但未規劃 Key。
- 技術層面：EF v1 對 View Key 支援有限。
- 流程層面：未手動補齊 Key 定義。

### Solution Design（解決方案設計）
解決策略：手動編輯 CSDL 為 View 對應的 EntityType 指定 Key（選用唯一且不為 Null 的欄位或組合鍵），並確保 SSDL/MSL 對應正確。

實施步驟：
1. 在 CSDL 為 View 的 EntityType 定義 <Key>
2. 確認 SSDL 中對應欄位型別與 Nullable 屬性
3. 校驗 MSL 對應正確

關鍵程式碼/設定：
```xml
<!-- CSDL: 指定 View 的 Key -->
<EntityType Name="VwOrder">
  <Key>
    <PropertyRef Name="OrderId"/>
  </Key>
  <Property Name="OrderId" Type="Int32" Nullable="false" />
  <Property Name="CustomerName" Type="String" Nullable="false" MaxLength="100" />
  <!-- 其他欄位 -->
</EntityType>
```

實際案例：手動指定 Key 後，查詢與建置恢復正常。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：追蹤異常/建置失敗。  
改善後：正常。  
改善幅度：可用性恢復。

Learning Points（學習要點）
核心知識點：
- EF 實體身份與 Key
- View 的 Key 策略

技能要求：
- 必備技能：.edmx 編修
- 進階技能：資料建模（組合鍵）

延伸思考：
- 可應用在報表 View 模型化。
- 限制：View 無唯一鍵時需調整 View。
- 優化：在 DB 層補唯一性約束。

Practice Exercise（練習題）
- 基礎：為一個 View 指定 Key（30 分）
- 進階：處理組合鍵 View（2 小時）
- 專案：建立 View 模型化準則（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：追蹤/查詢正常
- 程式碼品質（30%）：對應清楚
- 效能優化（20%）：查詢計畫合理
- 創新性（10%）：建模策略

---

## Case #11: 多容器下的實體集名稱歧義與容器限定

### Problem Statement（問題陳述）
業務場景：多 .edmx 併入同一 Context 後，存在相同實體集名稱，需要精確指向來源容器。  
技術挑戰：eSQL/CreateQuery<T> 需使用 ContainerQualified 名稱避免歧義。  
影響範圍：查詢錯誤、難以維護。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多個容器可能包含同名 EntitySet。
2. 預設查詢解析無法判定目標容器。
3. eSQL/LINQ 均可遭遇歧義。

深層原因：
- 架構層面：多模組命名未協調。
- 技術層面：查詢需容器限定。
- 流程層面：命名規範缺失。

### Solution Design（解決方案設計）
解決策略：一律在跨模型情境使用 ContainerQualified 名稱（Container.EntitySet），並制定命名規範以降低同名機率。

實施步驟：
1. 查詢時使用 ModelXContainer.EntitySet
2. 制定容器命名規約

關鍵程式碼/設定：
```csharp
// eSQL
"SELECT VALUE c FROM Model1Container.Customers AS c"

// LINQ 起點
var q = ctx.CreateQuery<Model1Namespace.Customer>("Model1Container.Customers");
```

實際案例：解決查詢歧義，降低維護風險。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：名稱衝突導致錯誤。  
改善後：容器限定後正常。  
改善幅度：錯誤移除。

Learning Points（學習要點）
核心知識點：
- ContainerQualified 名稱
- 命名規範

技能要求：
- 必備技能：eSQL/LINQ 查詢
- 進階技能：規範制定

延伸思考：
- 應用於大型多模組平台。
- 限制：字串易打錯。
- 優化：常數/列舉封裝容器名。

Practice Exercise（練習題）
- 基礎：改寫查詢為容器限定（30 分）
- 進階：製作容器名常數庫（2 小時）
- 專案：命名規約文件化（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：查詢正確
- 程式碼品質（30%）：命名一致
- 效能優化（20%）：無多餘解析
- 創新性（10%）：規範落地

---

## Case #12: 以程式建立單一 ObjectContext 跨模型工作

### Problem Statement（問題陳述）
業務場景：需要一個不依賴任何特定 typed Context 的通用存取層，能在執行階段跨多模型工作。  
技術挑戰：如何以最小依賴建立 ObjectContext 並能執行 LINQ/eSQL。  
影響範圍：共用資料層、測試可替換性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Typed Context 綁定單一 .edmx。
2. 跨模型需通用的 ObjectContext。
3. 連線字串需包含多組 metadata。

深層原因：
- 架構層面：通用資料層設計。
- 技術層面：EntityConnection 與 ObjectContext 基類。
- 流程層面：執行時組態。

### Solution Design（解決方案設計）
解決策略：使用 EntityConnectionStringBuilder 組 metadata，EntityConnection 建立後丟入 ObjectContext 基類，使用 eSQL + CreateQuery<T> 完成查詢。

實施步驟：
1. 組合連線（同 Case #8）
2. new ObjectContext(EntityConnection) 建立上下文
3. 提供泛用查詢 API

關鍵程式碼/設定：
```csharp
public sealed class UnifiedContext : IDisposable
{
    readonly ObjectContext _ctx;
    public UnifiedContext(string providerConn, params string[] models)
    {
        var ecsb = BuildConn(providerConn, models);
        _ctx = new ObjectContext(new EntityConnection(ecsb.ConnectionString));
    }

    public ObjectQuery<T> Set<T>(string container, string entitySet) =>
        _ctx.CreateQuery<T>($"{container}.{entitySet}");

    public ObjectQuery<System.Data.Common.DbDataRecord> Esql(string esql, params ObjectParameter[] ps) =>
        _ctx.CreateQuery<System.Data.Common.DbDataRecord>(esql, ps);

    public int SaveChanges() => _ctx.SaveChanges();
    public void Dispose() => _ctx.Dispose();
}
```

實際案例：共用資料層對多模型提供統一入口。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：每模型有各自資料層。  
改善後：統一資料層。  
改善幅度：重用性提升。

Learning Points（學習要點）
核心知識點：
- ObjectContext 基類
- 泛用查詢入口

技能要求：
- 必備技能：C# 泛型、EF 基礎
- 進階技能：抽象設計

延伸思考：
- 可應用於微服務內共享基礎層。
- 限制：仍需容器名/實體集名。
- 優化：加入查詢快取與攔截器。

Practice Exercise（練習題）
- 基礎：完成統一 Context 類別（30 分）
- 進階：加入攔截記錄（2 小時）
- 專案：替換既有資料層（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：支持 LINQ/eSQL/SaveChanges
- 程式碼品質（30%）：清楚抽象
- 效能優化（20%）：資源釋放
- 創新性（10%）：可擴充性

---

## Case #13: 跨模組用 eSQL、單模組用 LINQ 的雙查詢策略

### Problem Statement（問題陳述）
業務場景：需求同時包含跨模組 JOIN 報表與模組內日常查詢，需兼顧可讀性與功能覆蓋。  
技術挑戰：在 EF v1 前提下兼容兩種查詢方式。  
影響範圍：團隊開發體驗、查詢覆蓋率。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 跨 Context LINQ 不支援。
2. 模組內 LINQ 體驗較佳。
3. 需避免對新模組的編譯期依賴。

深層原因：
- 架構層面：查詢策略未分層。
- 技術層面：eSQL/ LINQ 能力差異。
- 流程層面：查詢責任劃分。

### Solution Design（解決方案設計）
解決策略：制定準則：跨模組查詢一律用 eSQL + DTO；模組內查詢用 CreateQuery<T> + LINQ。減少交叉依賴、提高可讀性。

實施步驟：
1. 撰寫查詢準則與範例
2. 建立 DTO 命名規範與資料夾
3. 稽核 PR 確保遵循

關鍵程式碼/設定：
```csharp
// 跨模組：eSQL + DTO
var reportRows = ctx.Esql(@"
  SELECT c.CustomerId, c.Name, o.OrderId, o.Total
  FROM AContainer.Customers AS c
  JOIN BContainer.Orders AS o ON c.CustomerId = o.CustomerId");

// 模組內：LINQ
var orders = unified.Set<BNS.Order>("BContainer", "Orders")
                    .Where(o => o.Total > 1000);
```

實際案例：團隊統一查詢策略，降低紛爭與錯用。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：查詢方式混亂。  
改善後：清楚分工。  
改善幅度：維護性提升。

Learning Points（學習要點）
核心知識點：
- 查詢策略分層
- DTO 與 LINQ 使用時機

技能要求：
- 必備技能：eSQL/LINQ
- 進階技能：團隊規範制定

延伸思考：
- 可擴展到 API 層。
- 限制：策略需教育與落地。
- 優化：加入範本與腳手架。

Practice Exercise（練習題）
- 基礎：依準則重寫兩個查詢（30 分）
- 進階：補充 Code Review 檢核表（2 小時）
- 專案：落地專案模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：場景覆蓋
- 程式碼品質（30%）：一致性
- 效能優化（20%）：查詢效率
- 創新性（10%）：落地方法

---

## Case #14: 以 res:// 內嵌資源避免部署路徑問題

### Problem Statement（問題陳述）
業務場景：多環境部署（DEV/QA/PROD）容易因為檔案路徑不同導致 metadata 找不到。  
技術挑戰：確保 csdl/ssdl/msl 能在任何環境正確定位。  
影響範圍：部署穩定性、啟動可靠性。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用實體檔案路徑部署易錯。
2. 部署目錄結構差異大。
3. 未內嵌資源。

深層原因：
- 架構層面：部署策略未標準化。
- 技術層面：未使用 res://。
- 流程層面：缺少部署檢核。

### Solution Design（解決方案設計）
解決策略：一律內嵌資源，連線以 res:// 指向；以 Assembly.LoadFrom 預載入模組，避免無法解析。

實施步驟：
1. 設定 EntityDeploy（預設）
2. 部署時確保 DLL 均到位
3. 啟動預載模組（同 Case #6）

關鍵程式碼/設定：
（同 Case #5/6 連線與載入設定）

實際案例：跨環境部署不再發生 metadata 找不到。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：部署後啟動失敗偶發。  
改善後：穩定啟動。  
改善幅度：部署穩定性提升。

Learning Points（學習要點）
核心知識點：
- res:// 與內嵌資源
- 組件預載

技能要求：
- 必備技能：部署與組態
- 進階技能：啟動流程優化

延伸思考：
- 可配合健康檢查端點。
- 限制：組件載入順序。
- 優化：啟動快取 MetadataWorkspace。

Practice Exercise（練習題）
- 基礎：改為 res:// 部署（30 分）
- 進階：加入啟動時資源檢查（2 小時）
- 專案：部署腳本自動驗證（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：啟動成功
- 程式碼品質（30%）：組態一致
- 效能優化（20%）：啟動時間
- 創新性（10%）：自動驗證

---

## Case #15: 以跨模型查詢滿足「四項需求」的整體落地

### Problem Statement（問題陳述）
業務場景：作者列出四項需求：模組化封裝、跨模組 eSQL JOIN、保留基本 LINQ、增模不需重編譯其他模組。  
技術挑戰：在 EF v1 限制下同時滿足四項。  
影響範圍：產品架構目標與團隊交付能力。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. EF v1 跨 Context 限制。
2. 模組化後關聯/查詢受限。
3. 編譯期型別依賴。

深層原因：
- 架構層面：需兼顧封裝與聚合。
- 技術層面：多 metadata 合併、eSQL、CreateQuery。
- 流程層面：動態載入與版本管理。

### Solution Design（解決方案設計）
解決策略：採用「多 metadata 合併 + 單一 ObjectContext + eSQL 跨模組 + 模組內 LINQ + 外掛式載入」的整體方案，滿足四項需求且不破壞模組邊界。

實施步驟：
1. 模型分割（Case #1）
2. 內嵌資源與部署（Case #5、#14）
3. 合併 metadata、單一 Context（Case #2、#12）
4. 跨模組 eSQL（Case #3、#4）
5. 模組內 LINQ（Case #7）
6. 動態載入（Case #6）
7. 名稱規範（Case #11）

關鍵程式碼/設定：
（綜合前述關鍵片段）

實際案例：作者以 MSDN ADO.NET 團隊文章的關鍵段落為引，落地多 metadata 的連線字串，解了困擾一個多月的問題。  
實作環境：.NET 3.5 SP1、EF v1。  
實測數據：  
改善前：跨模組 JOIN 不可行、需多次 SaveChanges、增模需重編譯。  
改善後：跨模組 JOIN 可行、單次 SaveChanges、增模免重編其他模組。  
改善幅度：四項需求逐一達成（定性 100% 覆蓋）。

Learning Points（學習要點）
核心知識點：
- 多 metadata 合併
- eSQL/LINQ 雙策略
- 模組化封裝與外掛載入

技能要求：
- 必備技能：EF 連線/查詢
- 進階技能：架構整合

延伸思考：
- 可套用於分階段遷移舊系統。
- 限制：導覽屬性跨模組不可用。
- 優化：引入查詢門面層與快取。

Practice Exercise（練習題）
- 基礎：將兩模型合併並完成一個跨模組查詢（30 分）
- 進階：加入第三模型並更新查詢（2 小時）
- 專案：完成四項需求的樣板專案（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：四項需求達成
- 程式碼品質（30%）：架構清晰
- 效能優化（20%）：查詢/提交效率
- 創新性（10%）：可擴展性

---

# 案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #8（連接字串產生）
  - Case #9（設計器殘留清理）
  - Case #10（View Key 指定）
  - Case #11（容器限定）
  - Case #14（res:// 部署）
- 中級（需要一定基礎）
  - Case #1（模型分割）
  - Case #5（模組封裝部署）
  - Case #7（CreateQuery + LINQ）
  - Case #12（通用 ObjectContext）
  - Case #13（雙查詢策略）
- 高級（需要深厚經驗）
  - Case #2（單一 SaveChanges/UoW）
  - Case #3（跨容器 eSQL JOIN）
  - Case #4（導航替代 + DTO）
  - Case #6（動態載入與擴充）
  - Case #15（四項需求整體落地）

2) 按技術領域分類
- 架構設計類
  - Case #1, #2, #5, #6, #12, #13, #15
- 效能優化類
  -（本篇以功能可行性為主；效能優化非核心）
- 整合開發類
  - Case #3, #4, #7, #8, #11, #14
- 除錯診斷類
  - Case #9, #10, #11
- 安全防護類
  -（本文場景未涉及）

3) 按學習目標分類
- 概念理解型
  - Case #1, #5, #11, #13, #14
- 技能練習型
  - Case #7, #8, #9, #10, #12
- 問題解決型
  - Case #2, #3, #4, #6, #15
- 創新應用型
  - Case #6, #12, #13, #15

# 案例關聯圖（學習路徑建議）

- 建議先學：
  - Case #9（設計器清理）、Case #10（View Key）：先修基礎工具問題，避免卡關。
  - Case #14（res:// 部署）、Case #11（容器限定）：掌握基礎部署與命名。
- 進階步驟（有依賴關係）：
  1) Case #1（模型分割）→ 奠定模組化基底
  2) Case #5（模組封裝）→ 形成可部署單元
  3) Case #12（通用 ObjectContext）→ 建立共用資料層
  4) Case #8（連接字串產生）→ 降低組態風險
  5) Case #3（跨容器 eSQL JOIN）→ 核心跨模組查詢能力
  6) Case #7（模組內 LINQ）→ 兼顧開發體驗
  7) Case #4（導航替代 + DTO）→ 解決跨模組關聯缺失
  8) Case #2（單一 SaveChanges）→ 簡化提交流程
  9) Case #6（動態載入）→ 支援免重編譯擴充
  10) Case #13（雙查詢策略）→ 團隊規範與最佳實踐
  11) Case #15（整體落地）→ 收斂為完整可交付的架構方案

- 完整學習路徑建議：
  先修工具與部署基礎（#9, #10, #14, #11）→ 建立模組化能力（#1, #5）→ 打造共用 Context 與組態自動化（#12, #8）→ 取得跨模組查詢與導航替代能力（#3, #4, #7）→ 完成提交一致性與擴充機制（#2, #6）→ 最後以策略與整體落地收尾（#13, #15）。