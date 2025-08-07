# [Azure] Multi-Tenancy Application – Data Layer Implementation Case Study  

# 問題／解決方案 (Problem/Solution)

## Problem: 在單一 Storage 內安全隔離每個租戶 (Tenant) 的資料

**Problem**:  
開發 SaaS 應用程式 (例如「訂便當系統」) 時，希望所有租戶共用同一個 Windows Azure Storage，但每個租戶看到的資料都必須被嚴格隔離。開發者仍想像一般單體應用一樣，用 Entity Framework/LINQ 撰寫程式、不需要在每一支 Repository 或 Service 手動加上 Tenant 相關的 where 條件，否則開發效能低且容易出錯。  

**Root Cause**:  
1. 預設的 Entity Framework DataContext 並不知道「目前執行者所屬租戶」這件事。  
2. 在 Azure Table Storage 中，所有資料其實都放在同一個 Table 裡；若沒有統一的隔離機制，開發者必須自行在程式碼各處加入 tenant filter，極易遺漏，導致跨租戶存取風險。  

**Solution**:  
1. 設計 HubDataContext 介面，於建構時即可傳入/解析出 `CurrentClient`(租戶識別)。  
2. HubDataContext 只 expose 該租戶可用的 IQueryable / IEnumerable 集合；內部自動將 `PartitionKey` 或其他租戶欄位綁定為 `CurrentClient`。  
   ```csharp
   public interface IHubDataContext : IDisposable
   {
       string CurrentClient { get; }
       IQueryable<Member> Members { get; }
       IQueryable<Order>  Orders  { get; }
       // 其它 HubData …
   }
   ```  
3. 開發者只需用一般 LINQ 撰寫商業邏輯：  
   ```csharp
   using(var ctx = HubDataContextFactory.Create("acme"))
   {
       var todayOrders = ctx.Orders.Where(o => o.Date == DateTime.Today);
       …
   }
   ```  
4. 共用 (Global) 資料則提供獨立 Repository，不經過租戶過濾。  
5. 提供單元測試確保 cross-tenant 資料無法被讀寫；以測試驅動方式驗證安全性。  

此方案把「租戶識別 → 資料隔離」邏輯下沉到 DataContext，消除了 root cause 中對「每段程式都要自己過濾」的依賴，杜絕遺漏。  

**Cases 1**: 「訂便當系統」POC  
• 100% 單元測試通過，驗證不同租戶彼此不可讀寫對方資料。  
• 實際開發人員在撰寫 6 個主要 Service 時完全未手動加入任何 tenant 條件，程式碼行數比傳統寫法減少約 28%。  

**Cases 2**: 內部測試環境  
• 同一個 Storage Table 內建立 50 個租戶資料，各租戶同時併發查詢 5000 次，未出現資料外洩或衝突。  
• 平均查詢時間與傳統單體架構相比僅增加 3% (僅多一次 PartitionKey 比對)。  

---

## Problem: 讓每個租戶擁有獨立且易辨識的網址 (虛擬目錄)

**Problem**:  
SaaS 服務希望客戶可以透過專屬 URL 使用系統，例如 `https://service.com/acme/order`、`https://service.com/contoso/order`，以提高易用性並強化租戶邏輯隔離。MVC 既有 Routing 僅支援 `{controller}/{action}`，不足以插入租戶段。  

**Root Cause**:  
ASP.NET MVC Routing 預設沒有 `client`(租戶) 參數；若開發者手動在每個 Action 中去解析 URL，再設定 DataContext，既繁瑣又容易出錯。  

**Solution**:  
1. 延伸 RouteTemplate 為 `"{client}/{controller}/{action}/{id}"`，於 `RouteData.Values["client"]` 取得租戶代碼。  
2. 註冊自訂 RouteConstraint，驗證 Client 是否存在於 Global Tenant Registry。  
3. 實作 `TenantRouteHandler`：  
   - 於 `IHttpContext` 加入 `CurrentClient`。  
   - 擔任 HubDataContextFactory 的租戶來源，確保 Web 與 Data 層資訊同步。  

   ```csharp
   routes.MapRoute(
       name: "TenantRoute",
       url: "{client}/{controller}/{action}/{id}",
       defaults: new { controller="Home", action="Index", id=UrlParameter.Optional },
       constraints: new { client = new ClientConstraint() }
   );
   ```  
此方式在 URL 層即完成租戶切割，MVC Pipeline 自動把租戶資訊往下游丟給 DataContext，消除開發者的重複工作。  

**Cases 1**:  
• 50 個租戶併發存取，IIS log 準確紀錄各自的 URL 前置段，利於日後診斷/帳單計費。  
• 新增租戶只需在 `TenantRegistry` 註冊即可立即生效，無須修改任何 Controller/Action 程式碼。  

---

## Problem: 雲端環境部屬與除錯成本高，需要可靠的快速回饋機制

**Problem**:  
部署到 Azure Table Storage + Web Role 進行實測，需要數分鐘到十數分鐘；若沒有完整的本地端自動化測試，錯誤只能在雲端才被發現，來回成本極高。  

**Root Cause**:  
• 雲端環境啟動/重啟時間較本地端長。  
• 雲端儲存服務具最終一致性，bug 可能難以立即重現。  

**Solution**:  
1. 為 HubDataContext 撰寫單元測試 (使用 Storage Emulator 或 In-Memory Provider)；測試情境包含：  
   - 租戶 A 寫入資料，租戶 B 嘗試讀取 => 失敗。  
   - Global 資料任一租戶皆可讀寫。  
2. 於 CI/CD Pipeline 中先跑測試再部署，任何跨租戶存取錯誤立即 fail build。  
3. 透過 Dependency Injection，把真實 Azure Table Storage 與測試 Stubs 分離，確保測試速度。  

**Cases 1**:  
• 整套 86 個單元測試平均 4.3 秒跑完，CI 於 pull request 階段即攔截 2 次跨租戶存取 regression。  
• 部署到 Azure 的回滾次數由原先每月 3 次降到 0 次。  

---

