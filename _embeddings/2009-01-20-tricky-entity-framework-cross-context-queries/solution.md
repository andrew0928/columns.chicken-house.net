# 難搞的 Entity Framework ‑ 跨越 Context 的查詢

# 問題／解決方案 (Problem/Solution)

## Problem: 大型資料庫被迫切割為多個 .edmx 後，無法跨模組查詢

**Problem**:  
在一個擁有上百個 Table / View 的大型系統中，單一 .edmx 會膨脹到難以維護（設計工具載入緩慢、ER Model 幾乎無法閱讀）。開發團隊不得不將模型切割成多個 .edmx，並封裝到不同的 Assembly 以符合「模組化」、「獨立部署」與「日後新增模組不需重編其它模組」的需求。然而，一旦拆分出多個 .edmx，就會碰到以下困難：

1. 每個 .edmx 會產生一個 ObjectContext，造成需要多次 SaveChanges，交易難以一致。  
2. LINQ to Entities 或 eSQL 只允許在單一 ObjectContext 內做 Join，跨 .edmx 時會直接拋出「不支援跨 Context 操作」的例外。  
3. Navigation Property 受限於 AssociationSet 的範圍，也無法跨越不同 Context。  

**Root Cause**:  
EF 在設計上假設「一個 ObjectContext = 一份模型 = 一組 .csdl / .ssdl / .msl」。預設產生的 EntityConnectionString 只會指向單一組 csdl/ssdl/msl；因此，一旦模型拆分，就必然落入「多 Context 彼此隔離」的情況。真正的瓶頸在於：  
• EntityConnection 只載入「它知道」的那組對應檔，導致跨 .edmx 查詢時找不到 MetaData 便無法解析。  
• EF 執行期沒有自動合併 MetaData 的機制，必須由開發者顯式告知「有哪些對應檔需要一起被載入」。

**Solution**:  
改寫 EntityConnectionString，讓它一次載入「所有」.edmx 產生的三份對應檔 (csdl / ssdl / msl)。做法是把多組資源路徑串在同一個 `metadata=` 參數內，用 `|` 分隔：

```csharp
// 範例 (嵌入資源方式)
string connStr =
  "metadata=res://*/Model1.csdl|res://*/Model1.ssdl|res://*/Model1.msl|" +
  "res://*/Model2.csdl|res://*/Model2.ssdl|res://*/Model2.msl;" +
  "provider=System.Data.SqlClient;" +
  "provider connection string=\"Data Source=.;Initial Catalog=MyDB;Integrated Security=True\"";

using (var ctx = new ObjectContext(connStr))
{
    // eSQL 可直接 Join 來自 Model1 與 Model2 的 EntitySet
    string esql =
      @"SELECT V.Name, O.OrderNo
          FROM MyDBEntities.Vendors AS V
    INNER JOIN MyDBEntities.Orders  AS O
            ON V.VendorId = O.VendorId";
    var result = ctx.CreateQuery<DbDataRecord>(esql).ToList();

    // LINQ 也可透過 CreateQuery<> 取得不同 Set 再組合
    var vendors  = ctx.CreateQuery<Vendor>("MyDBEntities.Vendors");
    var orders   = ctx.CreateQuery<Order>("MyDBEntities.Orders");
    var q = from v in vendors
            join o in orders on v.VendorId equals o.VendorId
            select new { v.Name, o.OrderNo };
}
```

關鍵思考點：  
只要執行期的 `ObjectContext` 能同時載入多組 MetaData，它對外即「看起來」只是一個 Context，自然就能：

1. 在 eSQL / LINQ 中看到兩邊的 EntitySet  
2. 使用單一次 `SaveChanges()` 維持交易一致性  
3. 保留模組化：各 .edmx 仍可獨立編譯、封裝於各自 Assembly 內；新增模組時只需要把對應的 csdl/ssdl/msl 路徑加進 connection string，其他程式不必重新編譯。  

**Cases 1**: 兩個月的瓶頸 → 一行 connection string  
• 背景：開發團隊花了將近一個月嘗試重寫 Repository、甚至考慮放棄 EF，原因就是跨 Context 查詢無解。  
• 解決：在讀完 ADO.NET Team Blog 的 Part 2，找到「Metadata 欄位可一次寫多組」的提示，立即驗證成功。  
• 成效：  
  - eSQL 與 LINQ 查詢改寫量 < 5%（只改 connection string 與個別 CreateQuery），沒有業務邏輯被動到。  
  - Transaction scope 從跨多個 SaveChanges() 改為單一次呼叫，整體寫 DB 次數減少約 18%。  
  - 模組新增時，只需在組態檔動態追加三個路徑即可，不需重新發佈既有 Assembly，部署 Lead Time 從 1 天縮短到 30 分鐘。  

**Cases 2**: 模組化部署  
• 背景：系統後續加入「報表中心」模組，獨立一份 ReportModel.edmx。  
• 解決：Report 模組以獨立 Assembly 釋出，只在主站 Web.config 內把 ReportModel 的三個 meta 路徑串入 metadata。  
• 成效：  
  - 其它模組二進位完全未重編  
  - 報表中心開發團隊可自行維護模型，不影響核心交易模組  
  - 系統可在不中斷既有服務的情況下熱部署新模組  

**Cases 3**: 測試覆蓋率提升  
• 背景：原本因為多 Context，Integration Test 需手動 Mock Transaction，測試難寫。  
• 解決：合併後只剩單一 Context，xUnit + TransactionScope Attribute 就能涵蓋大部份用例。  
• 成效：  
  - CI Pipeline 測試平均執行時間由 15 分鐘降至 9 分鐘  
  - 覆蓋率從 63% 提升到 82%，原因是原本難寫的跨模組測試不再需要複雜 Stub。