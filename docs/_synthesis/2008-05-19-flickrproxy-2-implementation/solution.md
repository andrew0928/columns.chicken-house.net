---
layout: synthesis
title: "FlickrProxy #2 - 實作"
synthesis_type: solution
source_post: /2008/05/19/flickrproxy-2-implementation/
redirect_from:
  - /2008/05/19/flickrproxy-2-implementation/solution/
postid: 2008-05-19-flickrproxy-2-implementation
---

以下內容基於提供的文章，萃取並結構化出 16 個可落地教學的問題解決案例。每個案例均包含問題、根因、方案、程式碼、效益與練習評估，便於實戰練習與能力評估。

## Case #1: 透明圖片代理到 Flickr，不改 HTML 與作者流程

### Problem Statement（問題陳述）
業務場景：部落格作者不想改變任何寫文或上圖習慣，也不想碰 Flickr；站方希望在不改 HTML、資料庫與上傳流程下，把圖片託管到 Flickr，維持閱讀者體驗一致，並可隨時撤回，不影響既有資料。
技術挑戰：需在不更動 HTML 的前提攔截圖片請求，首訪自動上傳到 Flickr，後續自動導向 Flickr；同時具備快取、回復機制與低侵入性。
影響範圍：若做不到，需改 HTML 或流程，導致作者負擔、風險升高；若透明代理成功，可大幅節省頻寬與維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. IIS 預設對靜態檔（.jpg）直接送檔，無法進入 ASP.NET 管線攔截。
2. 若改 HTML 置換連結，成本高、風險大、難回復。
3. 圖片首次訪問需要上傳至 Flickr 並取得可用 URL，缺乏快取會重複上傳。
深層原因：
- 架構層面：儲存與配送未解耦，缺少中介層（proxy）處理。
- 技術層面：HTTP 管線/Handler 與 IIS 映射認知不足。
- 流程層面：無自動上傳與回退流程設計。

### Solution Design（解決方案設計）
解決策略：以 ASP.NET HttpHandler 作為圖片請求的透明代理。IIS 先把 .jpg 請求導入 ASP.NET；預設用 StaticFileHandler 回傳；唯獨指定目錄（如 ~/storage）改由自製 FlickrProxyHttpHandler：首訪上傳到 Flickr 並寫入快取（檔案+記憶體），其後 302 轉址至 Flickr，達到不改 HTML 的透明導向與可回復配置。

實施步驟：
1. IIS 映射設定
- 實作細節：將 .jpg 交由 aspnet_isapi.dll（IIS 6/7 對應），使請求進入 ASP.NET 管線。
- 所需資源：IIS 管理工具
- 預估時間：0.5 小時
2. 預設回退 StaticFileHandler
- 實作細節：web.config 設定 *.jpg 為 System.Web.StaticFileHandler，避免全站破圖。
- 所需資源：web.config 編輯
- 預估時間：0.5 小時
3. 目錄範圍 Handler
- 實作細節：僅於 ~/storage 導向自訂 FlickrProxyHttpHandler，實作首訪上傳+快取+302。
- 所需資源：ASP.NET、FlickrNet
- 預估時間：2 小時

關鍵程式碼/設定：
```xml
<!-- 預設由 StaticFileHandler 回傳 jpg -->
<system.web>
  <httpHandlers>
    <add path="*.jpg" verb="*" type="System.Web.StaticFileHandler" />
  </httpHandlers>
</system.web>

<!-- 僅 ~/storage 使用自訂 Handler -->
<location path="storage">
  <system.web>
    <httpHandlers>
      <add path="*.jpg" verb="*" type="ChickenHouse.Web.HttpHandlers.FlickrProxyHttpHandler,App_Code" />
    </httpHandlers>
  </system.web>
</location>
```

```csharp
// 核心：快取命中則直接 302；否則首訪上傳、建檔、寫快取後 302
if (!Directory.Exists(this.CacheFolder)) Directory.CreateDirectory(this.CacheFolder);

string flickrURL;
if (!File.Exists(this.CacheInfoFile))
{
    flickrURL = this.BuildCacheInfoFile(context); // 首訪上傳並產生 cache 檔
}
else
{
    string cacheKey = "flickr.proxy." + this.GetFileHash();
    flickrURL = context.Cache[cacheKey] as string;
    if (flickrURL == null)
    {
        var doc = new XmlDocument();
        doc.Load(this.CacheInfoFile);
        flickrURL = doc.DocumentElement.GetAttribute("url");
        context.Cache.Insert(cacheKey, flickrURL, new CacheDependency(this.CacheInfoFile));
    }
}
context.Response.Redirect(flickrURL);
```

實際案例：小熊子 BLOG 接入，不改貼文/HTML，由 Handler 透明代理至 Flickr。Fiddler 顯示 HTML 與 JPG 下載，JPG 先收 302 再向 Flickr 取圖；Flickr 帳號中可見上傳圖片。
實作環境：ASP.NET（.NET Framework）、IIS、FlickrNet、Fiddler
實測數據：
改善前：所有圖片流量由部落格伺服器傳送。
改善後：首訪上傳一次，後續圖片傳輸由 Flickr 承擔，部落格僅回應 302。
改善幅度：後續訪問的圖片傳輸量幾近歸零（僅 302 header）。

Learning Points（學習要點）
核心知識點：
- HTTP 管線與 HttpHandler 的介入時機
- 以 302 轉址實作透明代理
- 「目錄範圍」與「預設回退」的配置模式

技能要求：
- 必備技能：IIS 映射、web.config、基本 ASP.NET 開發
- 進階技能：代理快取設計、回退策略設計

延伸思考：
- 同法可用於雲端物件儲存（S3/Blob）的透明外掛。
- 若 Flickr 連線失敗，應有降級方案（回傳本地檔）。
- 可加入預先上傳批次以降低首訪延遲。

Practice Exercise（練習題）
- 基礎練習：在本機站點配置 jpg 進入 ASP.NET 管線並不破圖（30 分鐘）
- 進階練習：實作 ~/media 專屬 Handler，非 media 仍走 StaticFileHandler（2 小時）
- 專案練習：完成透明 Flickr 代理（首訪上傳、快取、302）並在測試頁驗證（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：透明代理可用、首訪上傳、後續 302
- 程式碼品質（30%）：結構清晰、錯誤處理、設定分離
- 效能優化（20%）：快取命中率、避免重複上傳
- 創新性（10%）：回退/診斷工具整合、可觀測性

---

## Case #2: IIS 靜態檔預設處理導致 Handler 無法攔截

### Problem Statement（問題陳述）
業務場景：站台需攔截 .jpg 請求以代理到 Flickr，但在 IIS 上測試時自訂 HttpHandler 完全沒有被觸發，導致功能無法運作。
技術挑戰：理解 IIS 與 ASP.NET 管線如何協作，讓 .jpg 的請求能進入 ASP.NET 而非直接由 IIS 回檔。
影響範圍：Handler 不進管線則後續所有代理、上傳、快取全數失效。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. IIS 預設的靜態處理直接回傳 .jpg，未交由 ASP.NET。
2. 未在應用程式對應中將 .jpg 指向 aspnet_isapi.dll。
3. 僅在 web.config 設定 Handler 不足以讓請求進入 ASP.NET。
深層原因：
- 架構層面：應用程式管線分層（IIS vs ASP.NET）未被納入設計。
- 技術層面：IIS 映射與 Handler 註冊差異理解不足。
- 流程層面：只在 Dev Server 測試，忽略 IIS 行為差異。

### Solution Design（解決方案設計）
解決策略：在 IIS 應用程式對應中，將 *.jpg 交由 ASP.NET（aspnet_isapi.dll）處理，使請求進入 ASP.NET 管線；再由 web.config 控制預設與目錄層級的 Handler 行為。

實施步驟：
1. IIS 應用程式對應
- 實作細節：新增或編輯 *.jpg 對應至 aspnet_isapi.dll；勾選允許執行。
- 所需資源：IIS 管理員
- 預估時間：0.5 小時
2. 驗證進管線
- 實作細節：暫時於 Global.asax BeginRequest 記錄 *.jpg 請求路徑確認。
- 所需資源：ASP.NET 專案
- 預估時間：0.5 小時
3. 移除驗證碼
- 實作細節：上線前清理診斷碼。
- 所需資源：程式碼審查
- 預估時間：0.2 小時

關鍵程式碼/設定：
（IIS GUI 設定為主）
可輔以 web.config 驗證是否由 ASP.NET 回應：
```xml
<system.web>
  <httpHandlers>
    <add path="*.jpg" verb="*" type="System.Web.StaticFileHandler" />
  </httpHandlers>
</system.web>
```

實際案例：IIS 設定後，Fiddler 出現 jpg 請求的 302（來自 ASP.NET），確認已進入管線。
實作環境：IIS、ASP.NET
實測數據：
改善前：Handler 不觸發。
改善後：jpg 請求由 ASP.NET 回應 302。
改善幅度：功能從 0% 提升為可運作。

Learning Points（學習要點）
核心知識點：
- IIS 靜態處理與 ASP.NET 管線關係
- 檔案副檔名與 ISAPI 映射
- 驗證請求是否進入管線的技巧

技能要求：
- 必備技能：IIS 管理、基本 ASP.NET
- 進階技能：ISAPI/整合式管線差異

延伸思考：
- 在整合式管線（IIS7+）如何用 managed module 攔截？
- 大量副檔名映射對效能影響？
- 以 URL Rewrite 攔截的替代做法？

Practice Exercise（練習題）
- 基礎練習：將 *.jpg 映射到 ASP.NET 並驗證（30 分鐘）
- 進階練習：改用 URL Rewrite 導入 ASP.NET（2 小時）
- 專案練習：建立映射與回退策略文件，含風險與驗證清單（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：映射有效、請求進入管線
- 程式碼品質（30%）：診斷碼可控、可關閉
- 效能優化（20%）：僅必要副檔名映射
- 創新性（10%）：替代方案比較

---

## Case #3: 避免全站破圖：StaticFileHandler 與目錄範圍 Handler

### Problem Statement（問題陳述）
業務場景：站台將 .jpg 導入 ASP.NET 後，若未設定預設處理，所有圖片將無 Handler 可處理而破圖。需確保只有特定目錄走代理，其他維持原樣。
技術挑戰：以 web.config 設計「預設回退」與「目錄覆寫」的 Handler 組合。
影響範圍：若處理錯誤，全站圖片無法顯示，造成重大影響。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 全站 .jpg 進入 ASP.NET，未設預設處理器。
2. 缺少目錄層級覆寫規則，導致無差別攔截。
3. 未使用 StaticFileHandler 做為安全回退。
深層原因：
- 架構層面：缺少分層策略（全域 vs 區域）。
- 技術層面：location 規則與 Handler 繫結理解不足。
- 流程層面：缺少回退設計與測試驗證。

### Solution Design（解決方案設計）
解決策略：全域設定以 StaticFileHandler 處理 *.jpg，確保預設行為不變；再使用 <location path="storage"> 覆寫目錄 Handler 為自訂 FlickrProxy，達到「僅特定資料夾代理」。

實施步驟：
1. 全域回退
- 實作細節：在 system.web/httpHandlers 下註冊 StaticFileHandler。
- 所需資源：web.config
- 預估時間：0.3 小時
2. 目錄覆寫
- 實作細節：以 <location path="storage"> 指定自訂 Handler。
- 所需資源：web.config
- 預估時間：0.3 小時
3. 驗證
- 實作細節：非 storage 圖片顯示正常；storage 圖片出現 302。
- 所需資源：瀏覽器、Fiddler
- 預估時間：0.4 小時

關鍵程式碼/設定：
```xml
<system.web>
  <httpHandlers>
    <add path="*.jpg" verb="*" type="System.Web.StaticFileHandler" />
  </httpHandlers>
</system.web>

<location path="storage">
  <system.web>
    <httpHandlers>
      <add path="*.jpg" verb="*" type="ChickenHouse.Web.HttpHandlers.FlickrProxyHttpHandler,App_Code" />
    </httpHandlers>
  </system.web>
</location>
```

實際案例：設定完成後，測試頁僅 storage 下圖片被 302 至 Flickr，其餘頁面不受影響。
實作環境：ASP.NET、IIS
實測數據：
改善前：全站破圖風險。
改善後：僅目錄範圍代理，其他維持原狀。
改善幅度：故障面縮小到單一目錄，可回退。

Learning Points（學習要點）
核心知識點：
- StaticFileHandler 的用途
- location 範圍覆寫
- 以配置實現「安全預設 + 最小覆寫」

技能要求：
- 必備技能：web.config 操作
- 進階技能：複合配置策略與風險控管

延伸思考：
- 可否用路由或中介軟體達到同效果？
- 以子 web.config 在資料夾就地管理配置的優缺點？
- 加入黑白名單策略？

Practice Exercise（練習題）
- 基礎練習：配置全域 StaticFileHandler（30 分鐘）
- 進階練習：建立兩個不同目錄使用不同 Handler（2 小時）
- 專案練習：撰寫配置回退 SOP 與自動化驗證腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：回退與覆寫正確
- 程式碼品質（30%）：配置清楚、註解完整
- 效能優化（20%）：僅必要範圍覆寫
- 創新性（10%）：配置自動化驗證

---

## Case #4: IIS 與 Visual Studio Dev Server 行為不一致

### Problem Statement（問題陳述）
業務場景：開發時在 VS Dev Server 上正常，但部署到 IIS 出現 Path Info 不一致、Handler 不觸發等問題，導致功能失效。
技術挑戰：不同宿主對路徑、管線與映射的處理行為差異大，需在開發階段即對齊 IIS 環境。
影響範圍：功能在生產環境不穩，偵錯成本高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Dev Server 與 IIS 的管線與映射差異大。
2. 開發未在 IIS 下進行，誤判行為。
3. 路徑（PathInfo）在兩環境解析不同。
深層原因：
- 架構層面：環境一致性未納入計畫。
- 技術層面：宿主差異認知不足。
- 流程層面：缺 CI/本機 IIS 開發流程。

### Solution Design（解決方案設計）
解決策略：開發即使用本機 IIS，對齊映射與配置；新增環境檢查清單與自動化驗證，確保路徑與 Handler 行為一致。

實施步驟：
1. 本機 IIS 開發
- 實作細節：建立本機站台，套用與生產一致的映射與 web.config。
- 所需資源：IIS、管理員權限
- 預估時間：1 小時
2. 環境檢查
- 實作細節：撰寫檢查清單（映射、PathInfo、處理器）；用 Fiddler 比對。
- 所需資源：文檔、Fiddler
- 預估時間：1 小時
3. 自動化
- 實作細節：簡單的 smoke test 腳本，檢查 302/200/404 序列。
- 所需資源：Powershell/curl
- 預估時間：1 小時

關鍵程式碼/設定：
（流程/配置為主；無特定程式碼）

實際案例：作者明確指出 DevWeb 與 IIS 行為差很多，建議開發階段即在 IIS 上開發。
實作環境：IIS、VS
實測數據：
改善前：部署後才發現問題。
改善後：開發期即對齊，減少回退與修正。
改善幅度：缺陷前移，風險降低。

Learning Points（學習要點）
核心知識點：
- 宿主差異對 HTTP 管線的影響
- 環境一致性策略
- 基礎 smoke test 設計

技能要求：
- 必備技能：IIS 基本操作
- 進階技能：自動化驗證/腳本化

延伸思考：
- 容器化/同構化開發環境是否更佳？
- 如何把 Fiddler 驗證自動化？
- 預先檢查清單如何納入 CI？

Practice Exercise（練習題）
- 基礎練習：在本機 IIS 重現 Handler 流程（30 分鐘）
- 進階練習：寫 smoke test 驗證 302 流程（2 小時）
- 專案練習：建立環境對齊與驗證手冊（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：IIS 開發環境運行正常
- 程式碼品質（30%）：檢查清單與腳本完整
- 效能優化（20%）：快速定位環境差異
- 創新性（10%）：驗證自動化程度

---

## Case #5: 串接 Flickr API 認證與上傳流程

### Problem Statement（問題陳述）
業務場景：需程式化上傳圖片到 Flickr 並取得可用 URL，但 Flickr 對安全要求高，必須取得 API Key、Secret、Token 才能呼叫。
技術挑戰：導入 FlickrNet 並正確完成使用者授權流程與憑證管理。
影響範圍：未取得 Token 將導致 API 無法使用，上傳失敗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未申請 API Key/Secret。
2. 未經使用者授權的 Token。
3. 程式碼未正確設定憑證。
深層原因：
- 架構層面：外部 API 憑證管理缺位。
- 技術層面：Flickr 安全模型理解不足。
- 流程層面：授權流程未納入部署步驟。

### Solution Design（解決方案設計）
解決策略：申請 Key/Secret，依 FlickrNet 提供範例導引使用者登入與授權取得 Token，將三者寫入 appSettings，於程式啟動時注入 Flickr 客戶端。

實施步驟：
1. 申請與授權
- 實作細節：至 Flickr API 申請 Key/Secret；用 FlickrNet Sample 流程取得 Token。
- 所需資源：Flickr 帳號、FlickrNet 範例
- 預估時間：0.5-1 小時
2. 組態管理
- 實作細節：將 Key/Secret/Token 放入 web.config appSettings。
- 所需資源：web.config
- 預估時間：0.2 小時
3. 程式注入
- 實作細節：以 ConfigurationManager 讀取設定，設定 Flickr 客戶端。
- 所需資源：FlickrNet
- 預估時間：0.2 小時

關鍵程式碼/設定：
```csharp
private string BuildCacheInfoFile(HttpContext context)
{
    var flickr = new Flickr(
        ConfigurationManager.AppSettings["flickrProxy.API.key"],
        ConfigurationManager.AppSettings["flickrProxy.API.security"]);
    flickr.AuthToken = ConfigurationManager.AppSettings["flickrProxy.API.token"];

    string photoID = flickr.UploadPicture(this.FileLocation);
    PhotoInfo pi = flickr.PhotosGetInfo(photoID);
    // ...
}
```

實際案例：作者使用 FlickrNet Sample 取得 Token，成功上傳並回讀 PhotoInfo。
實作環境：ASP.NET、FlickrNet
實測數據：
改善前：API 呼叫失敗。
改善後：可正常上傳並取得 URL。
改善幅度：上傳成功率由 0% → 100%（授權完成後）。

Learning Points（學習要點）
核心知識點：
- Flickr 認證模型（Key/Secret/Token）
- 第三方 SDK 注入與配置
- 授權流程在部署中的位置

技能要求：
- 必備技能：外部 API 串接
- 進階技能：憑證安全與組態管理

延伸思考：
- 憑證滾動（rotation）流程如何設計？
- 多環境（Dev/Prod）憑證區隔？
- 以組態轉換（transform）自動化部署？

Practice Exercise（練習題）
- 基礎練習：以 FlickrNet 取得 Token（30 分鐘）
- 進階練習：將憑證注入並上傳一張圖片（2 小時）
- 專案練習：撰寫憑證配置與授權 SOP（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能上傳並取得 PhotoInfo
- 程式碼品質（30%）：設定注入、錯誤處理
- 效能優化（20%）：僅初始化一次客戶端
- 創新性（10%）：憑證保護策略

---

## Case #6: Flickr 圖片尺寸可用性不穩的降級策略

### Problem Statement（問題陳述）
業務場景：Flickr 端偶發 Medium/Large/Original URL 回應 “photo not available”；若直接使用可能顯示失敗。
技術挑戰：在不確定每個尺寸是否立即可用下，動態挑選最大可用尺寸，避免破圖。
影響範圍：讀者端顯示失敗，體驗不佳。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Flickr 各尺寸生成具有延遲或可用性不穩。
2. FlickrNet 在尺寸不可用時拋出例外。
3. 程式未檢測實際可下載性。
深層原因：
- 架構層面：對外部服務最終一致性缺少容錯。
- 技術層面：缺少探測機制與降級路徑。
- 流程層面：未規劃重試/回退策略。

### Solution Design（解決方案設計）
解決策略：自訂 CheckFlickrUrlAvailability 依序探測 Medium → Large → Original，以 HTTP 實測可下載性；捕捉例外並保留最後成功的 URL 作為輸出，確保顯示。

實施步驟：
1. 撰寫探測函式
- 實作細節：HEAD/GET 測試 200 回應；異常丟出例外。
- 所需資源：HttpWebRequest/HttpClient
- 預估時間：0.5 小時
2. 採用遞進策略
- 實作細節：由中到大逐一測試，保留最大可用 URL。
- 所需資源：FlickrNet PhotoInfo
- 預估時間：0.5 小時
3. 例外處理
- 實作細節：try/catch 包覆整段，確保至少回傳一個可用 URL。
- 所需資源：程式碼調整
- 預估時間：0.3 小時

關鍵程式碼/設定：
```csharp
string flickrURL = null;
try
{
    flickrURL = this.CheckFlickrUrlAvailability(pi.MediumUrl);
    flickrURL = this.CheckFlickrUrlAvailability(pi.LargeUrl);
    flickrURL = this.CheckFlickrUrlAvailability(pi.OriginalUrl);
}
catch { /* 保留最後成功的 flickrURL */ }
```

實際案例：作者實測 Flickr 尺寸不穩，採取逐步探測策略避免破圖。
實作環境：ASP.NET、FlickrNet
實測數據：
改善前：偶發破圖。
改善後：自動降級到最大可用尺寸。
改善幅度：顯示可靠性明顯提升（定性）。

Learning Points（學習要點）
核心知識點：
- 外部服務最終一致性
- 探測與降級設計
- 例外管理策略

技能要求：
- 必備技能：HTTP 狀態碼處理
- 進階技能：健壯性設計與觀察度量

延伸思考：
- 可否加上重試/延遲再試？
- 是否暫存尺寸可用性避免重複探測？
- 遇到全尺寸不可用時的回退圖（placeholder）？

Practice Exercise（練習題）
- 基礎練習：實作 CheckFlickrUrlAvailability（30 分鐘）
- 進階練習：加入重試與指數回退（2 小時）
- 專案練習：設計完整降級矩陣與監控指標（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可選最大可用尺寸
- 程式碼品質（30%）：例外處理清晰
- 效能優化（20%）：避免過度探測
- 創新性（10%）：更聰明的尺寸選擇策略

---

## Case #7: 雙層快取（檔案 + 記憶體）與 CacheDependency

### Problem Statement（問題陳述）
業務場景：若每次請求都上傳或呼叫 Flickr API，效能差且易觸發限制；需保存本地映射（本地檔 ↔ Flickr URL）。
技術挑戰：設計持久化（檔案）與快速（記憶體）快取，並保持一致。
影響範圍：效能與穩定性，重複上傳風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未保存 Flickr URL 導致每次都重新上傳/查詢。
2. 記憶體與檔案快取不一致。
3. 無過期或依附機制。
深層原因：
- 架構層面：快取層設計缺失。
- 技術層面：CacheDependency 未使用。
- 流程層面：缺乏快取生成與失效流程。

### Solution Design（解決方案設計）
解決策略：以 XML 檔保存來源/URL/photoID，並把 URL 放入 ASP.NET Cache，以 cache 檔作為 CacheDependency，當檔案變更時自動失效記憶體快取。

實施步驟：
1. 檔案快取
- 實作細節：XML 存 src/url/photoID。
- 所需資源：System.Xml
- 預估時間：0.5 小時
2. 記憶體快取
- 實作細節：context.Cache.Insert(key, url, new CacheDependency(file))
- 所需資源：System.Web.Caching
- 預估時間：0.3 小時
3. 一致性
- 實作細節：先讀記憶體，miss 才讀檔，檔 miss 才上傳。
- 所需資源：程式碼調整
- 預估時間：0.3 小時

關鍵程式碼/設定：
```csharp
string cacheKey = "flickr.proxy." + this.GetFileHash();
string flickrURL = context.Cache[cacheKey] as string;
if (flickrURL == null)
{
    var doc = new XmlDocument();
    doc.Load(this.CacheInfoFile);
    flickrURL = doc.DocumentElement.GetAttribute("url");
    context.Cache.Insert(cacheKey, flickrURL, new CacheDependency(this.CacheInfoFile));
}
```

實際案例：XML 檔與 ASP.NET Cache 搭配，顯著降低 API 呼叫與上傳次數。
實作環境：ASP.NET
實測數據：
改善前：頻繁呼叫 API。
改善後：命中記憶體快取，檔案變更自動失效。
改善幅度：API/上傳次數大幅下降（定性）。

Learning Points（學習要點）
核心知識點：
- 多層快取策略
- CacheDependency
- 快取一致性模式

技能要求：
- 必備技能：ASP.NET Cache API
- 進階技能：快取失效與一致性設計

延伸思考：
- 可否加入過期策略與統計？
- 改用分散式快取（Redis）？
- 檔案快取命名與併發鎖？

Practice Exercise（練習題）
- 基礎練習：以 CacheDependency 綁定檔案（30 分鐘）
- 進階練習：實作三層（記憶體/檔案/API）查詢鏈（2 小時）
- 專案練習：加入分散式快取與併發控制（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：快取命中/失效正確
- 程式碼品質（30%）：層次清楚
- 效能優化（20%）：API 呼叫下降
- 創新性（10%）：多層快取優化

---

## Case #8: 快取目錄不存在導致首訪失敗

### Problem Statement（問題陳述）
業務場景：首次運行在沒有預先建立 cache 目錄的情況下，寫入快取檔案失敗，流程中斷。
技術挑戰：健壯性初始化，確保必要目錄存在。
影響範圍：首訪即失敗，無法上傳與導向。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 目錄不存在，存檔異常。
2. 未在程式碼中建立目錄。
3. 部署未包含目錄初始化步驟。
深層原因：
- 架構層面：缺少啟動初始化流程。
- 技術層面：檔案 I/O 錯誤處理不足。
- 流程層面：部署步驟未檢查目錄。

### Solution Design（解決方案設計）
解決策略：於 Handler 執行前檢查並建立 cache 目錄；把此檢查納入啟動或每次請求的前置步驟（低成本）。

實施步驟：
1. 目錄檢查
- 實作細節：Directory.Exists/Directory.CreateDirectory
- 所需資源：System.IO
- 預估時間：0.1 小時
2. 例外處理
- 實作細節：捕捉 I/O 例外，回退至本地回傳。
- 所需資源：程式碼調整
- 預估時間：0.3 小時
3. 部署清單
- 實作細節：在 SOP 加入目錄初始化檢查。
- 所需資源：文檔
- 預估時間：0.2 小時

關鍵程式碼/設定：
```csharp
if (Directory.Exists(this.CacheFolder) == false)
{
    Directory.CreateDirectory(this.CacheFolder);
}
```

實際案例：作者於主程式第一步即建立目錄，避免首訪失敗。
實作環境：ASP.NET
實測數據：
改善前：首次寫檔失敗。
改善後：自動建立目錄，流程順利。
改善幅度：首訪失敗率顯著降低。

Learning Points（學習要點）
核心知識點：
- 初始化與健壯性
- 檔案 I/O 例外處理
- 部署檢查點

技能要求：
- 必備技能：System.IO
- 進階技能：啟動健檢設計

延伸思考：
- 可否移至應用程式啟動時一次完成？
- 權限不足時的替代路徑？
- 寫入失敗監控與警示？

Practice Exercise（練習題）
- 基礎練習：執行時自建目錄（30 分鐘）
- 進階練習：封裝健檢模組（2 小時）
- 專案練習：加上權限檢查與失敗回退（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：目錄自動建立
- 程式碼品質（30%）：錯誤處理完整
- 效能優化（20%）：檢查成本低
- 創新性（10%）：健檢模組化

---

## Case #9: 以檔案雜湊當快取鍵避免衝突

### Problem Statement（問題陳述）
業務場景：需為圖片建立穩定唯一鍵，用於記憶體快取與快取檔命名，避免鍵衝突與重複上傳。
技術挑戰：基於檔案內容生成雜湊，保證一致性與唯一性。
影響範圍：鍵衝突導致誤導向或重複上傳。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用檔名/路徑不保證唯一。
2. 未以內容雜湊作識別。
3. 快取檔命名策略不足。
深層原因：
- 架構層面：快取鍵策略缺失。
- 技術層面：雜湊與碰撞管理未知。
- 流程層面：未規範鍵生成流程。

### Solution Design（解決方案設計）
解決策略：以 SHA-1/SHA-256 計算檔案內容雜湊，作為 cacheKey 與快取檔名的一部分，確保不同內容不同鍵，相同內容穩定一致。

實施步驟：
1. 雜湊函式
- 實作細節：讀取檔案 bytes → SHA1Managed.ComputeHash → Hex 字串。
- 所需資源：System.Security.Cryptography
- 預估時間：0.5 小時
2. 快取鍵
- 實作細節：cacheKey = "flickr.proxy." + Hash
- 所需資源：程式碼調整
- 預估時間：0.2 小時
3. 檔名策略
- 實作細節：快取檔以 Hash 命名，避免衝突。
- 所需資源：System.IO
- 預估時間：0.2 小時

關鍵程式碼/設定：
```csharp
private string GetFileHash()
{
    using (var sha1 = SHA1.Create())
    using (var fs = File.OpenRead(this.FileLocation))
    {
        var hash = sha1.ComputeHash(fs);
        return BitConverter.ToString(hash).Replace("-", "").ToLowerInvariant();
    }
}
```

實際案例：程式以 Hash 作為 cacheKey 前綴，對應快取檔與記憶體快取。
實作環境：ASP.NET
實測數據：
改善前：可能鍵重疊。
改善後：鍵唯一且穩定。
改善幅度：衝突與重上傳風險下降（定性）。

Learning Points（學習要點）
核心知識點：
- 雜湊函式應用
- 快取鍵設計
- 一致性與碰撞考量

技能要求：
- 必備技能：加密雜湊 API
- 進階技能：碰撞處理策略

延伸思考：
- 是否應加入檔案 metadata（尺寸/時間）於鍵？
- 雜湊計算成本與快取命中平衡？
- 大檔案的串流計算優化？

Practice Exercise（練習題）
- 基礎練習：實作檔案雜湊（30 分鐘）
- 進階練習：以 Hash 命名快取檔並測試碰撞（2 小時）
- 專案練習：建立快取鍵策略文件與單元測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：鍵穩定且唯一
- 程式碼品質（30%）：API 正確、資源釋放
- 效能優化（20%）：大檔流式計算
- 創新性（10%）：多因子鍵策略

---

## Case #10: 條件式代理：僅轉向特定目錄與超過閾值的大圖

### Problem Statement（問題陳述）
業務場景：非所有圖片都需要代理至 Flickr，例如小圖或非 storage 目錄檔案；全攔截會增加負擔。
技術挑戰：在 Handler 內實作條件判斷，僅符合條件才觸發上傳與轉址。
影響範圍：過度攔截影響效能與穩定性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏條件過濾，所有 .jpg 一視同仁。
2. 小圖上傳成本大於收益。
3. 非目錄內檔案不需代理。
深層原因：
- 架構層面：策略未分層。
- 技術層面：Handler 未加入早退（early return）。
- 流程層面：缺省策略過重。

### Solution Design（解決方案設計）
解決策略：在 Handler 中檢查路徑與檔案大小（門檻），符合才進入代理流程；其他直接走 StaticFileHandler。

實施步驟：
1. 門檻設定
- 實作細節：從 config 讀取目錄與大小閾值。
- 所需資源：web.config
- 預估時間：0.3 小時
2. 早退邏輯
- 實作細節：不符合條件直接傳回本地檔。
- 所需資源：程式碼調整
- 預估時間：0.5 小時
3. 監控
- 實作細節：記錄命中率與節省帶寬估算。
- 所需資源：日誌
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var fi = new FileInfo(this.FileLocation);
long minSize = long.Parse(ConfigurationManager.AppSettings["flickrProxy.MinBytes"] ?? "0");

if (!this.FileLocation.StartsWith(this.StorageRoot, StringComparison.OrdinalIgnoreCase) ||
    fi.Length < minSize)
{
    // 不代理，傳回本地檔（可改呼叫 StaticFileHandler）
    context.RemapHandler(new StaticFileHandler());
    return;
}
```

實際案例：作者提到以條件判斷（目錄/大小）決定是否代理。
實作環境：ASP.NET
實測數據：
改善前：全站攔截。
改善後：僅必要圖片代理，降低成本。
改善幅度：代理覆蓋面縮小，效益提升（定性）。

Learning Points（學習要點）
核心知識點：
- Early return 模式
- 策略與規則配置
- 效益分層

技能要求：
- 必備技能：條件設計
- 進階技能：策略參數化與監控

延伸思考：
- 是否可依 URI pattern 黑白名單？
- 動態調整門檻（A/B 測試）？
- 依圖片類別（封面/縮圖）施策？

Practice Exercise（練習題）
- 基礎練習：加入大小門檻（30 分鐘）
- 進階練習：加上路徑黑白名單（2 小時）
- 專案練習：以設定檔驅動策略並記錄命中率（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：條件過濾有效
- 程式碼品質（30%）：參數化良好
- 效能優化（20%）：降低非必要代理
- 創新性（10%）：策略調優

---

## Case #11: 首訪上傳策略：按需上傳減少流程改造

### Problem Statement（問題陳述）
業務場景：不想改變作者上傳流程，仍上傳至站台；首次讀者請求時才把圖片上傳到 Flickr，後續皆走 Flickr。
技術挑戰：在 Handler 內完成即時上傳與 URL 生成，並寫入快取。
影響範圍：降低作者負擔，維持習慣。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 事先批次上傳會改變作者流程。
2. 未保存上傳結果導致重複上傳。
3. 首訪延遲需控制。
深層原因：
- 架構層面：按需（lazy）策略未落地。
- 技術層面：上傳與快取組合設計。
- 流程層面：作者無需認知 Flickr。

### Solution Design（解決方案設計）
解決策略：BuildCacheInfoFile 在首次命中時觸發上傳，取得 photoID 與 URL，寫入快取檔與記憶體。後續命中直接 302 至 Flickr，作者流程零變動。

實施步驟：
1. 上傳並取回資訊
- 實作細節：UploadPicture → PhotosGetInfo。
- 所需資源：FlickrNet
- 預估時間：0.5 小時
2. 快取寫入
- 實作細節：XML 記錄 src/url/photoID；Cache.Insert。
- 所需資源：System.Xml
- 預估時間：0.5 小時
3. 控制首訪延遲
- 實作細節：必要時先回本地檔並背景上傳（可選）。
- 所需資源：背景工作
- 預估時間：2 小時（可選）

關鍵程式碼/設定：
```csharp
string photoID = flickr.UploadPicture(this.FileLocation);
PhotoInfo pi = flickr.PhotosGetInfo(photoID);
// ... 選擇最大可用 URL 後存入 XML 與記憶體快取
```

實際案例：作者首訪上傳成功，後續轉址；Flickr 帳號可見圖片。
實作環境：ASP.NET、FlickrNet
實測數據：
改善前：需改作者流程或手動操作。
改善後：作者無感，讀者透明。
改善幅度：流程改造成本→0。

Learning Points（學習要點）
核心知識點：
- Lazy 上傳策略
- 首訪延遲管理
- 快取與上傳一致性

技能要求：
- 必備技能：HTTP/SDK 使用
- 進階技能：背景處理/非同步（選）

延伸思考：
- 大量首訪時可能同時上傳，如何鎖定？
- 可否預先上傳熱門內容？
- 首訪超時的降級策略？

Practice Exercise（練習題）
- 基礎練習：完成首訪上傳（30 分鐘）
- 進階練習：為同一檔案加互斥鎖避免重複上傳（2 小時）
- 專案練習：加入背景上傳與臨時回退本地（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：首訪上傳與後續 302 正確
- 程式碼品質（30%）：鎖定與錯誤處理
- 效能優化（20%）：降低首訪延遲
- 創新性（10%）：背景/預先上傳

---

## Case #12: 使用 302 重新導向最小化原站頻寬

### Problem Statement（問題陳述）
業務場景：希望原站不再承擔圖片傳輸，僅引導用戶端向 Flickr 取圖，以節省帶寬與成本。
技術挑戰：選擇 302 轉址而非反向代理轉送，完全卸載圖片流量。
影響範圍：後續圖片流量幾近歸零，僅保留 302 回應。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 若以反向代理，仍需中轉圖片數據。
2. 需要簡單、標準的卸載方式。
3. 客戶端需能跟隨轉址。
深層原因：
- 架構層面：帶寬成本控制。
- 技術層面：HTTP 轉址語義。
- 流程層面：用戶端相容性（瀏覽器皆支援）。

### Solution Design（解決方案設計）
解決策略：Handler 以 Response.Redirect(flickrURL) 回應 302，瀏覽器跟隨到 Flickr 下載圖片，原站不再傳輸圖片內容。

實施步驟：
1. 取得 Flickr URL
- 實作細節：首訪上傳或快取命中。
- 所需資源：見前案例
- 預估時間：N/A
2. 回應 302
- 實作細節：Response.Redirect(url)。
- 所需資源：ASP.NET
- 預估時間：0.1 小時
3. 驗證
- 實作細節：Fiddler 觀察 302 → Flickr 200。
- 所需資源：Fiddler
- 預估時間：0.3 小時

關鍵程式碼/設定：
```csharp
context.Response.Redirect(flickrURL); // 302 Object moved
```

實際案例：Fiddler 顯示 JPG 收到 302，接著向 Flickr 請求並回 200 顯示。
實作環境：ASP.NET、瀏覽器
實測數據：
改善前：圖片流量由原站傳送。
改善後：原站僅送 302 metadata。
改善幅度：後續請求帶寬幾近歸零（定性）。

Learning Points（學習要點）
核心知識點：
- HTTP 302 的語義與行為
- 反向代理 vs 轉址的取捨
- 帶寬成本模型

技能要求：
- 必備技能：HTTP 狀態碼
- 進階技能：流量/成本分析

延伸思考：
- 301/302/307 的差異與快取策略？
- CDN 配合下的行為（Cache-Control）？
- 斷線或超時的回退？

Practice Exercise（練習題）
- 基礎練習：以 302 導向任一靜態圖（30 分鐘）
- 進階練習：評估 301/302 差異並測試瀏覽器快取（2 小時）
- 專案練習：設計導向+Cache-Control 策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確 302 與顯示
- 程式碼品質（30%）：簡潔可靠
- 效能優化（20%）：帶寬卸載
- 創新性（10%）：快取策略

---

## Case #13: 以 XML 快取檔保存 src/url/photoID

### Problem Statement（問題陳述）
業務場景：需在磁碟持久化保存來源檔與 Flickr URL 的對應，方便重啟後快速恢復，不依賴資料庫。
技術挑戰：選擇簡單可讀格式，快速讀寫。
影響範圍：避免重複上傳，縮短冷啟動時間。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無持久化，重啟後資訊遺失。
2. 資料庫過重，不符需求。
3. 欠缺簡單格式。
深層原因：
- 架構層面：狀態持久化考量不足。
- 技術層面：格式選擇與序列化缺失。
- 流程層面：重啟恢復流程未設計。

### Solution Design（解決方案設計）
解決策略：用 XML 文件記錄 <proxy src="" url="" photoID="">，首訪生成，後續讀取；配合 CacheDependency 控制記憶體失效。

實施步驟：
1. 寫入
- 實作細節：XmlDocument.SetAttribute/Save
- 所需資源：System.Xml
- 預估時間：0.3 小時
2. 讀取
- 實作細節：Load/GetAttribute
- 所需資源：System.Xml
- 預估時間：0.3 小時
3. 失效綁定
- 實作細節：CacheDependency 指向 XML 檔。
- 所需資源：ASP.NET Cache
- 預估時間：0.3 小時

關鍵程式碼/設定：
```csharp
var doc = new XmlDocument();
doc.LoadXml("<proxy />");
doc.DocumentElement.SetAttribute("src", this.FileLocation);
doc.DocumentElement.SetAttribute("url", flickrURL);
doc.DocumentElement.SetAttribute("photoID", photoID);
doc.Save(this.CacheInfoFile);
```

實際案例：作者以 XML 快取檔保存映射，重用方便。
實作環境：ASP.NET
實測數據：
改善前：重啟後需重上傳/查詢。
改善後：直接讀檔得 URL。
改善幅度：冷啟動開銷下降（定性）。

Learning Points（學習要點）
核心知識點：
- 輕量持久化
- XML 讀寫
- 快取與檔案協作

技能要求：
- 必備技能：XML API
- 進階技能：檔案鎖與競態處理

延伸思考：
- 是否轉為 JSON/YAML 更輕量？
- 多程序同寫時的鎖定策略？
- 檔案清理（過期/孤兒檔）？

Practice Exercise（練習題）
- 基礎練習：寫入/讀取 xml 快取檔（30 分鐘）
- 進階練習：加入基本鎖定避免併發寫入（2 小時）
- 專案練習：快取檔維護工具（清理/驗證）（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：讀寫正確
- 程式碼品質（30%）：併發處理
- 效能優化（20%）：I/O 成本控制
- 創新性（10%）：工具化

---

## Case #14: 用 Fiddler 驗證代理與轉址流程（可觀測性）

### Problem Statement（問題陳述）
業務場景：需要證明使用者端仍看到正常圖片，但實際圖片流量已卸載到 Flickr；需可觀測的驗證手段。
技術挑戰：觀察 HTTP 請求序列與狀態碼，定位問題。
影響範圍：缺乏觀測導致疑難排查困難。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無法直觀看到轉址序列。
2. 難以判斷是誰提供圖片。
3. 代理錯誤不易發現。
深層原因：
- 架構層面：缺少可觀測性設計。
- 技術層面：HTTP 診斷工具未使用。
- 流程層面：驗證步驟缺失。

### Solution Design（解決方案設計）
解決策略：使用 Fiddler 抓取請求，確認 HTML 請求（200）、JPG 請求（302 Object Moved）、Flickr 端最終圖片（200）；同時檢查 Response Headers 與目標主機。

實施步驟：
1. 搭建測試頁
- 實作細節：簡單 HTML + 一張圖片。
- 所需資源：HTML
- 預估時間：0.2 小時
2. Fiddler 抓包
- 實作細節：觀察請求順序與狀態碼。
- 所需資源：Fiddler
- 預估時間：0.3 小時
3. 截圖/紀錄
- 實作細節：保存結果作為驗證證據。
- 所需資源：文檔
- 預估時間：0.2 小時

關鍵程式碼/設定：
```html
<img src="smile_sunkist.jpg" alt="test image" />
```

實際案例：作者以 Fiddler 證明 JPG 收到 302，後向 Flickr 取圖 200 顯示。
實作環境：瀏覽器、Fiddler
實測數據：
改善前：難以證明卸載成功。
改善後：以抓包證明 302 → Flickr。
改善幅度：可觀測性提升。

Learning Points（學習要點）
核心知識點：
- HTTP 抓包與分析
- 狀態碼與轉址鏈
- 端到端驗證

技能要求：
- 必備技能：Fiddler/瀏覽器開發者工具
- 進階技能：自動化抓包

延伸思考：
- 加入伺服器端日誌關聯 ID？
- 自動化合規驗證（E2E 測試）？
- 監控儀表板（302 比率）？

Practice Exercise（練習題）
- 基礎練習：抓取 302 轉址（30 分鐘）
- 進階練習：撰寫腳本驗證特定鏈（2 小時）
- 專案練習：建立代理監控面板設計稿（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能準確觀測流程
- 程式碼品質（30%）：驗證腳本清楚
- 效能優化（20%）：問題定位效率
- 創新性（10%）：觀測指標設計

---

## Case #15: 處理 FlickrNet 例外與安全降級

### Problem Statement（問題陳述）
業務場景：FlickrNet 在存取特定尺寸 URL 時會拋出例外，若未處理將中斷流程。
技術挑戰：以 try/catch 包裹尺寸選取流程，確保至少回傳一個可用 URL。
影響範圍：未處理導致讀者端破圖。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. API 屬性取值可能丟例外。
2. 未捕捉例外與保留最後成功值。
3. 未設回退 URL。
深層原因：
- 架構層面：容錯策略不足。
- 技術層面：API 例外行為理解不足。
- 流程層面：未規範降級路徑。

### Solution Design（解決方案設計）
解決策略：以 try/catch 包覆尺寸挑選，遇例外保留前一個成功尺寸；必要時回退到本地檔案 URL 或預設占位圖。

實施步驟：
1. 尺寸挑選 try/catch
- 實作細節：同 Case #6。
- 所需資源：程式碼
- 預估時間：0.2 小時
2. 回退 URL
- 實作細節：若全失敗，改回本地檔案。
- 所需資源：StaticFileHandler
- 預估時間：0.3 小時
3. 監控
- 實作細節：記錄例外發生率。
- 所需資源：日誌
- 預估時間：0.3 小時

關鍵程式碼/設定：
```csharp
string fallback = context.Request.Url.GetLeftPart(UriPartial.Authority) + context.Request.RawUrl;
try
{
    flickrURL = this.CheckFlickrUrlAvailability(pi.MediumUrl);
    flickrURL = this.CheckFlickrUrlAvailability(pi.LargeUrl);
    flickrURL = this.CheckFlickrUrlAvailability(pi.OriginalUrl);
}
catch
{
    flickrURL ??= fallback; // 全失敗回本地
}
```

實際案例：作者以 try/catch 保留最後成功的 URL，避免破圖。
實作環境：ASP.NET、FlickrNet
實測數據：
改善前：例外造成破圖。
改善後：自動降級或回退。
改善幅度：可靠性提升（定性）。

Learning Points（學習要點）
核心知識點：
- 例外安全與降級
- 回退 URL 設計
- 觀測例外

技能要求：
- 必備技能：例外處理
- 進階技能：回退策略

延伸思考：
- 是否加入熔斷器避免連續失敗？
- 回退後是否暫停代理一段時間？
- 回報/警示機制？

Practice Exercise（練習題）
- 基礎練習：加入回退本地圖（30 分鐘）
- 進階練習：加入熔斷與重新恢復（2 小時）
- 專案練習：設計降級矩陣與告警（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：例外不破圖
- 程式碼品質（30%）：錯誤處理完善
- 效能優化（20%）：避免無謂重試
- 創新性（10%）：熔斷/回退策略

---

## Case #16: 快速回復與可逆性：移除配置即可回原狀

### Problem Statement（問題陳述）
業務場景：站方需確保任何改造可撤回，不影響既有資料與 HTML；異常時能快速回復原狀。
技術挑戰：以配置可控的方式導入/移除代理，不改動內容層。
影響範圍：降低上線風險，便於試行。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 若改 HTML 則不易回退。
2. 導入代理若不可控，風險大。
3. 無回退 SOP。
深層原因：
- 架構層面：可逆性未納入設計目標。
- 技術層面：配置驅動程度不足。
- 流程層面：回退流程缺失。

### Solution Design（解決方案設計）
解決策略：以 Handler 與 web.config 控制代理；移除 <location path="storage"> 或改回 StaticFileHandler，即時回復；資料不變、HTML 不變，回退成本極低。

實施步驟：
1. 配置驅動
- 實作細節：所有代理行為由 web.config 控制。
- 所需資源：web.config
- 預估時間：0.3 小時
2. 回退 SOP
- 實作細節：文件化步驟：移除 location、回 IIS 靜態。
- 所需資源：文檔
- 預估時間：0.5 小時
3. 演練
- 實作細節：演練回退/恢復各一次。
- 所需資源：測試環境
- 預估時間：0.5 小時

關鍵程式碼/設定：
（同 Case #3 配置；回退即移除該段或改回 StaticFileHandler）

實際案例：作者強調不改 HTML/資料，所有改變可還原。
實作環境：ASP.NET、IIS
實測數據：
改善前：需修改內容層，回退困難。
改善後：刪配置即回原狀。
改善幅度：回復時間顯著縮短。

Learning Points（學習要點）
核心知識點：
- 可逆性設計
- 配置驅動
- 回退演練

技能要求：
- 必備技能：配置管理
- 進階技能：變更控制與風險管理

延伸思考：
- 配置開關（feature toggle）是否需要？
- 自動回退條件（錯誤率升高）？
- 藍綠/金絲雀發布？

Practice Exercise（練習題）
- 基礎練習：以配置開關啟閉代理（30 分鐘）
- 進階練習：撰寫回退 SOP 並演練（2 小時）
- 專案練習：導入 feature flag 與自動回退腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可快速回復
- 程式碼品質（30%）：配置清晰
- 效能優化（20%）：變更影響面小
- 創新性（10%）：自動回退設計


--------------------------------
案例分類
--------------------------------

1) 按難度分類
- 入門級（適合初學者）
  - Case #2 IIS 靜態檔處理
  - Case #3 StaticFileHandler 與目錄覆寫
  - Case #8 快取目錄初始化
  - Case #9 檔案雜湊快取鍵
  - Case #12 302 重新導向
  - Case #14 Fiddler 可觀測性
  - Case #16 可逆性與回退
- 中級（需要一定基礎）
  - Case #1 透明代理整體方案
  - Case #4 IIS 與 Dev Server 差異
  - Case #5 Flickr 認證串接
  - Case #6 尺寸可用性降級
  - Case #7 雙層快取與依附
  - Case #10 條件式代理
  - Case #11 首訪上傳策略
  - Case #15 例外處理與降級

2) 按技術領域分類
- 架構設計類
  - Case #1, #3, #7, #10, #11, #16
- 效能優化類
  - Case #7, #9, #10, #12
- 整合開發類
  - Case #5, #11
- 除錯診斷類
  - Case #4, #14, #15
- 安全防護類（含可靠性）
  - Case #5, #6, #15, #16

3) 按學習目標分類
- 概念理解型
  - Case #2, #3, #12, #16
- 技能練習型
  - Case #8, #9, #14
- 問題解決型
  - Case #1, #4, #5, #6, #7, #10, #11, #15
- 創新應用型
  - Case #7, #10, #11, #16


--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 入門先學（基礎配置與觀念）
  1) Case #2（IIS 映射）→ 關鍵前置
  2) Case #3（回退與目錄覆寫）→ 安全預設
  3) Case #12（302 轉址）→ 卸載原理
  4) Case #14（Fiddler）→ 可觀測性

- 中段進階（核心功能）
  5) Case #1（整體透明代理）→ 綜合實作
  6) Case #5（Flickr 認證）→ 外部整合
  7) Case #7（雙層快取）→ 效能與一致性
  8) Case #9（雜湊鍵）→ 快取鍵策略
  9) Case #11（首訪上傳）→ 按需策略
  10) Case #10（條件式代理）→ 策略細化

- 可靠性與實戰（健壯性與運維）
  11) Case #6（尺寸降級）
  12) Case #15（例外與回退）
  13) Case #8（初始化）
  14) Case #4（IIS vs Dev Server）
  15) Case #16（可逆性/回退 SOP）

依賴關係示意：
- Case #2 → #3 →（#12 與 #14）→ #1
- #5 是 #1 上傳能力的前置
- #7、#9 為 #1 的效能支撐
- #10、#11 在 #1 完成後優化策略
- #6、#15 增強穩定性，依賴 #1、#5
- #8 為 #7 的前置（快取檔）
- #4 確保所有案例在 IIS 上行為一致
- #16 提供整體解決方案的快速回退能力

完整學習路徑建議：
- 先建立正確的宿主與配置心智模型（#2 → #3 → #12 → #14）
- 再完成端到端透明代理（#1）與認證整合（#5）
- 然後強化效能與一致性（#7, #9），完善策略（#10, #11）
- 最後補齊可靠性與運維能力（#6, #15, #8, #4, #16）
- 完成後可嘗試延伸到其他物件儲存/圖像服務（延伸思考題）