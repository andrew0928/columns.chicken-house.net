---
layout: synthesis
title: "FlickrProxy #1 - Overview"
synthesis_type: solution
source_post: /2008/05/16/flickrproxy-1-overview/
redirect_from:
  - /2008/05/16/flickrproxy-1-overview/solution/
---

## Case #1: ADSL 自架站相片流量外移至 Flickr 的伺服器端方案

### Problem Statement（問題陳述）
**業務場景**：部落格自架於家用 ADSL，文章常附帶多張高解析度照片，尖峰時段網頁讀者較多時，因上行頻寬有限導致圖片載入緩慢，甚至影響整體站台可用性。希望在不改變內容產製流程、不依賴特定寫作工具或外掛的前提下，降低網站自身的圖片輸出流量。
**技術挑戰**：如何在不改變既有文章與圖片路徑的情況下，將圖片傳輸流量轉移到 Flickr 等外部服務，且在瀏覽時才動態決策，避免一次性大量手動遷移。
**影響範圍**：讀者端載入速度、站台上行頻寬占用、圖片穩定可用性、文章維護成本。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 家用 ADSL 上行頻寬小，遇到高併發圖片請求時容易塞車。
2. 照片體積較大（數百 KB～數 MB），單次文章載入帶寬消耗高。
3. 現有圖片直接由站台靜態檔案伺服，未使用外部圖片託管或 CDN。

**深層原因**：
- 架構層面：靜態資源與動態站台共用同一上行頻寬與主機。
- 技術層面：缺乏可插拔的媒體外移機制與動態轉址能力。
- 流程層面：未將媒體生命週期（上傳、託管、備援）與內容發布流程分離。

### Solution Design（解決方案設計）
**解決策略**：在伺服器端加入透明的 HttpHandler（或 ASP.NET Core Middleware）攔截圖片請求，於執行時判斷該檔案是否已外移到 Flickr；若未外移，視規則決定直接回傳本地檔或先上傳再 302 轉址至 Flickr，後續流量由 Flickr 承擔，站台保留完整本地副本。

**實施步驟**：
1. 導入攔截層
- 實作細節：以 IHttpHandler 或 Middleware 攔截 /media/images/* 請求。
- 所需資源：ASP.NET、IIS 或 Kestrel、URL Rewrite。
- 預估時間：0.5 天

2. 實作外移決策與上傳
- 實作細節：根據檔案大小、存取次數決定是否上傳 Flickr；上傳成功後存入映射表並 302 轉址。
- 所需資源：Flickr API（FlickrNet 套件）、SQLite/JSON 作為映射儲存。
- 預估時間：1.5 天

3. 緩存與回退
- 實作細節：加入 MemoryCache/Redis 緩存映射結果；Flickr 不可用時回傳本地檔。
- 所需資源：MemoryCache/Redis、Polly（重試/斷路器）。
- 預估時間：1 天

**關鍵程式碼/設定**：
```csharp
// web.config (ASP.NET Framework)
<configuration>
  <system.webServer>
    <handlers>
      <add name="FlickrProxy" verb="GET" path="media/images/*" type="FlickrProxy.ImageHandler" resourceType="Unspecified" />
    </handlers>
  </system.webServer>
</configuration>

// ImageHandler.cs
public class ImageHandler : IHttpHandler
{
    private readonly IMappingStore _map = MappingStoreFactory.Create();
    private readonly IFlickrProvider _flickr = new FlickrProvider(Config.FlickrKey, Config.FlickrSecret);

    public void ProcessRequest(HttpContext context)
    {
        var localPath = context.Server.MapPath(context.Request.Path);
        if (!File.Exists(localPath)) { context.Response.StatusCode = 404; return; }

        // 先查映射
        var map = _map.GetByLocalPath(localPath);
        if (map?.RemoteUrl != null) {
            context.Response.Redirect(map.RemoteUrl, endResponse: true);
            return;
        }

        // 決策：檔案大於 200KB 才外移
        var fi = new FileInfo(localPath);
        if (fi.Length <= 200 * 1024) {
            // 直接回傳本地檔，並設定合理快取
            context.Response.ContentType = MimeMapping.GetMimeMapping(localPath);
            context.Response.Cache.SetCacheability(HttpCacheability.Public);
            context.Response.TransmitFile(localPath);
            return;
        }

        // 上傳 Flickr（同步簡化示例；實務可背景化）
        var remoteUrl = _flickr.UploadAndGetUrl(localPath, title: Path.GetFileName(localPath));
        _map.Save(localPath, remoteUrl, "Flickr");
        context.Response.Redirect(remoteUrl, endResponse: true);
    }

    public bool IsReusable => true;
}
```

實際案例：POC 曾將 Google News HTML 內的圖片連結改寫至另一個目錄並以 Fiddler 驗證流向，證明攔截重寫可行（文章提及 POC）。
實作環境：ASP.NET（.NET Framework 4.x）、IIS、FlickrNet。
實測數據：
- 改善前：圖片全部由本機上行（估）
- 改善後：大量圖片流量由 Flickr 承擔（預期）
- 改善幅度：目標降低本機圖片上行流量 ≥50%

Learning Points（學習要點）
核心知識點：
- HttpHandler 攔截與靜態資源代理
- 外部媒體託管與 302 轉址策略
- 本地副本保留與遠端映射

技能要求：
- 必備技能：ASP.NET 管線、基本 HTTP、IIS 設定
- 進階技能：設計決策引擎、快取與回退機制

延伸思考：
- 也可用於將 CSS/JS 外移至 CDN
- 風險：外部服務中斷；需回退策略
- 優化：加入背景上傳、批次預外移

Practice Exercise（練習題）
- 基礎練習：為 /media/images/* 增加一個最小可行的 HttpHandler 並印出請求檔名。
- 進階練習：依檔案大小決策是否回傳本地或 302 轉址到一個假 URL。
- 專案練習：串接 Flickr 沙箱帳號，完成上傳、映射存儲與回退。

Assessment Criteria（評估標準）
- 功能完整性（40%）：攔截、生效、回退、轉址行為正確
- 程式碼品質（30%）：模組化、可測試、設定化
- 效能優化（20%）：快取命中率、資源使用
- 創新性（10%）：決策策略與擴展性設計

---

## Case #2: 擺脫 WLW Plugin 鎖定與舊文不可回溯遷移

### Problem Statement（問題陳述）
**業務場景**：以 Windows Live Writer（WLW）與 Flickr 插件撰文時，外掛在發佈瞬間將圖片上傳並嵌入特定連結。日後若更換 Flickr 帳號或停止使用 WLW，舊文圖片無法自動切換，舊內容也很難回溯性遷移。
**技術挑戰**：在不依賴客戶端工具的情況下，支援舊文章的圖片在瀏覽時才外移，並可隨時更換服務或停用功能。
**影響範圍**：內容長期可用性、運營彈性、供應商鎖定風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 客戶端外掛在發佈時做「一次性決策」，嵌入固定 URL。
2. 舊文已存入 HTML 的外部連結，難以批次回溯。
3. 更換帳號或工具時，無伺服器端統一入口可控。

**深層原因**：
- 架構層面：媒體決策位於客戶端，缺乏伺服器統一治理層。
- 技術層面：無 URL 重寫與代理層，難以抽象化媒體來源。
- 流程層面：發布階段強耦合外部服務，後續維運成本高。

### Solution Design（解決方案設計）
**解決策略**：改採伺服器端透明代理，所有文章中的圖片連結統一指向站內路徑（如 /media/images/...）。當讀者瀏覽時由伺服器決策是否上傳與轉址，達成舊文可回溯遷移與服務可替換。

**實施步驟**：
1. URL 正規化
- 實作細節：將編輯器輸出的圖片路徑規範為站內 /media 開頭。
- 所需資源：編輯器設定或發佈過濾器
- 預估時間：0.5 天

2. 文章內容批次改寫
- 實作細節：寫腳本將舊文章中的絕對 Flickr 連結改回站內代理 URL。
- 所需資源：資料庫存取腳本
- 預估時間：1 天

3. 伺服器端代理決策
- 實作細節：使用 Case #1 的 Handler 執行動態外移與轉址
- 所需資源：同 Case #1
- 預估時間：沿用

**關鍵程式碼/設定**：
```sql
-- 範例：將舊文內的 <img src="http://farm...flickr.../xyz.jpg"> 改成 <img src="/media/images/xyz.jpg">
UPDATE Posts
SET Content = REPLACE(Content, 'http://farm', '/media/images/farm') -- 實務需更嚴謹 HTML Parse
WHERE Content LIKE '%flickr%';
```

實際案例：作者表示偏好 server-side 透明 proxy，並提及可隨時關閉或改設定、換服務與帳號。
實作環境：部落格後端資料庫（SQL Server/MySQL）、ASP.NET。
實測數據：
- 改善前：舊文依賴 WLW 外掛產生的硬連結
- 改善後：舊文走伺服器代理，隨時可切換服務
- 改善幅度：供應商鎖定風險顯著降低（定性）

Learning Points（學習要點）
核心知識點：
- URL 正規化與內容改寫
- 伺服器端治理層的價值
- 可回溯遷移策略

技能要求：
- 必備技能：SQL/文本處理、基本 HTML 解析
- 進階技能：安全的內容改寫、最小停機遷移

延伸思考：
- 亦可將影片、附件統一走代理以便治理
- 風險：改寫時需避免破壞內容
- 優化：用 DOM Parser 而非簡單字串替換

Practice Exercise（練習題）
- 基礎練習：撰寫腳本將文章中 http://example.com/img/* 改為 /media/images/*
- 進階練習：用 HTML Agility Pack 安全改寫 <img> src
- 專案練習：完成一個一次性舊文改寫工具並支援回滾

Assessment Criteria（評估標準）
- 功能完整性（40%）：改寫正確、可回滾
- 程式碼品質（30%）：健壯解析、邊界處理
- 效能優化（20%）：批次處理效率
- 創新性（10%）：可視化回顧與審核流程

---

## Case #3: 透明 Proxy 決策：本地直出 vs 上傳後轉址

### Problem Statement（問題陳述）
**業務場景**：希望在讀者請求圖片時，伺服器動態決策是否直接回傳本地檔，或先上傳到 Flickr 再轉址，兼顧效能與彈性。
**技術挑戰**：如何設計可配置且可擴展的決策引擎，將檔案大小、類型、熱門程度與時間窗納入考量，並避免阻塞請求。
**影響範圍**：首次請求延遲、整體使用者體驗、伺服器負載。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 同步上傳會增加首次請求延遲。
2. 缺乏決策規則導致無差別上傳或無限期直出。
3. 無緩存與預熱策略導致重複計算。

**深層原因**：
- 架構層面：未分離即時路徑與背景處理路徑。
- 技術層面：缺乏規則引擎與快取。
- 流程層面：沒有明確 SLA 與閾值設定。

### Solution Design（解決方案設計）
**解決策略**：引入可配置的規則集與快取，首次請求以快速直出為優先，將上傳任務推送至背景處理；僅當檔案達閾值且滿足策略時才同步上傳轉址。

**實施步驟**：
1. 規則引擎
- 實作細節：以策略模式封裝多條規則（大小、類型、命中次數）。
- 所需資源：自訂策略類別、設定檔
- 預估時間：1 天

2. 背景佇列
- 實作細節：採用 BackgroundService/Hangfire 建立上傳佇列。
- 所需資源：Hangfire 或自建 Queue、資料儲存
- 預估時間：1 天

3. 先快取後決策
- 實作細節：對評估結果與映射結果緩存，降低重複判斷。
- 所需資源：MemoryCache/Redis
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public interface IOffloadRule { bool ShouldOffload(FileInfo fi, string mime, int hitCount); }

public class SizeRule : IOffloadRule {
    private readonly long _minBytes;
    public SizeRule(long minBytes) { _minBytes = minBytes; }
    public bool ShouldOffload(FileInfo fi, string mime, int hitCount) => fi.Length >= _minBytes;
}

public class HotRule : IOffloadRule {
    private readonly int _minHits;
    public HotRule(int minHits) { _minHits = minHits; }
    public bool ShouldOffload(FileInfo fi, string mime, int hitCount) => hitCount >= _minHits;
}

// 決策引擎
public class OffloadDecider {
    private readonly IEnumerable<IOffloadRule> _rules;
    public OffloadDecider(IEnumerable<IOffloadRule> rules) { _rules = rules; }
    public bool ShouldOffload(FileInfo fi, string mime, int hitCount) => _rules.All(r => r.ShouldOffload(fi, mime, hitCount));
}
```

實際案例：作者敘述「在 Run Time 動態檢查」，並可選擇「不需要則直出、需要則上傳轉址」。
實作環境：ASP.NET、C#、Hangfire（可選）。
實測數據：
- 改善前：首次請求常遭遇同步上傳延遲
- 改善後：首次請求直出，後續轉址（預期）
- 改善幅度：首次延遲顯著下降（定性）

Learning Points（學習要點）
核心知識點：
- 策略模式與規則引擎
- 背景作業與前台解耦
- 緩存與命中統計

技能要求：
- 必備技能：C# 設計模式、快取
- 進階技能：併發與一致性處理

延伸思考：
- 可加入時間窗、檔案類型白名單
- 同步/非同步策略取捨
- 觀測延遲分佈優化體驗

Practice Exercise（練習題）
- 基礎練習：實作 SizeRule 與 HotRule 並單元測試
- 進階練習：接入 MemoryCache 記錄 hitCount
- 專案練習：整合背景佇列完成延遲外移

Assessment Criteria（評估標準）
- 功能完整性（40%）：決策可配置、生效
- 程式碼品質（30%）：模式運用、測試覆蓋
- 效能優化（20%）：降低同步阻塞
- 創新性（10%）：多維規則與自動調參

---

## Case #4: Provider 架構：Flickr、YouTube、SkyDrive 可插拔整合

### Problem Statement（問題陳述）
**業務場景**：希望將照片轉至 Flickr、影片轉至 YouTube、ZIP 檔未來轉至 SkyDrive 等服務，並可隨時替換供應商。
**技術挑戰**：以統一抽象封裝不同媒體與供應商 API，降低耦合並支援擴展。
**影響範圍**：可維護性、擴充性、風險隔離。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 各服務 API 與認證方式不同。
2. 不同媒體類型有差異化上傳流程與限制。
3. 直接耦合造成後續替換成本高。

**深層原因**：
- 架構層面：缺乏 Provider/Adapter 抽象。
- 技術層面：未標準化元資料與錯誤模型。
- 流程層面：無回退預案與能力檢查。

### Solution Design（解決方案設計）
**解決策略**：定義 IMediaProvider 介面，依媒體類型選擇對應 Provider；所有 Provider 輸出統一結果（RemoteUrl、Id、Meta），並由工廠/組合器管理生命週期與設定。

**實施步驟**：
1. 介面與模型
- 實作細節：定義 IMediaProvider、MediaType、UploadResult。
- 所需資源：C# 類別與 DI 容器
- 預估時間：1 天

2. Provider 實作
- 實作細節：FlickrProvider、YouTubeProvider（Stub/轉址）、SkyDriveProvider（待定）。
- 所需資源：各 API SDK/REST
- 預估時間：2-3 天

3. 選路與回退
- 實作細節：ProviderFactory 依檔案副檔名/Meta 選路；失敗回退次佳供應商或本地直出。
- 所需資源：設定檔、Polly
- 預估時間：1 天

**關鍵程式碼/設定**：
```csharp
public enum MediaType { Image, Video, Archive }

public record UploadResult(string RemoteUrl, string RemoteId, IDictionary<string,string> Meta);

public interface IMediaProvider {
    bool Supports(MediaType mediaType);
    Task<UploadResult> UploadAsync(string localPath, IDictionary<string,string> meta, CancellationToken ct);
    Task<bool> ExistsAsync(string hashOrKey, CancellationToken ct);
    string Name { get; }
}

// 工廠
public class ProviderFactory {
    private readonly IEnumerable<IMediaProvider> _providers;
    public ProviderFactory(IEnumerable<IMediaProvider> providers) => _providers = providers;
    public IMediaProvider Get(MediaType type) => _providers.First(p => p.Supports(type));
}
```

實際案例：作者計畫「把之前兩個 HttpHandler 整合起來，弄成統一的 provider 架構」，並舉例照片轉 Flickr、影片轉 YouTube、ZIP 未來轉 SkyDrive。
實作環境：ASP.NET、C#、Flickr/YouTube/OneDrive API。
實測數據：
- 改善前：各媒體邏輯分散、耦合高
- 改善後：統一抽象、可插拔
- 改善幅度：維護成本降低（定性）

Learning Points（學習要點）
核心知識點：
- Provider/Adapter Pattern
- 多供應商選路與回退
- 統一錯誤模型與契約

技能要求：
- 必備技能：設計模式、DI/IoC
- 進階技能：多雲/多服務抽象與測試替身

延伸思考：
- 以 OpenAPI 定義介面與模擬
- 風險：抽象過度或漏斗瓶頸
- 優化：能力探測與動態特性宣告

Practice Exercise（練習題）
- 基礎練習：完成一個 MockProvider 回傳固定 URL
- 進階練習：實作 FlickrProvider.UploadAsync
- 專案練習：新增一個 ImgurProvider 並接入回退

Assessment Criteria（評估標準）
- 功能完整性（40%）：多 Provider 可用
- 程式碼品質（30%）：抽象合理、耦合度
- 效能優化（20%）：選路與快取
- 創新性（10%）：可觀察性鉤子

---

## Case #5: 本地與遠端 URL 映射儲存設計

### Problem Statement（問題陳述）
**業務場景**：上傳後需要記錄 localPath ↔ remoteUrl 對應，避免重複上傳，支援後續查詢與回遷。
**技術挑戰**：設計一個輕量且一致性的映射儲存，支援查詢、更新、搬遷與備份。
**影響範圍**：上傳成本、查詢效率、資料一致性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無映射表將導致每次請求都需詢問遠端或重新上傳。
2. 缺乏唯一鍵（如檔案雜湊）難以去重。
3. 缺乏狀態欄位難以處理上傳中/失敗情況。

**深層原因**：
- 架構層面：無專屬媒體目錄與索引。
- 技術層面：未考慮一致性與併發更新。
- 流程層面：缺少備份與回遷策略。

### Solution Design（解決方案設計）
**解決策略**：建立 MediaMap 表，包含 LocalPath、Sha256、RemoteUrl、Provider、Status、UploadedAt 等欄位，提供原子更新與查詢 API，並定期備份。

**實施步驟**：
1. 資料模式設計
- 實作細節：SQLite 或 SQL Server 資料表與索引設計。
- 所需資源：資料庫
- 預估時間：0.5 天

2. 儲存存取層
- 實作細節：Repository + Unit of Work、併發控制（RowVersion）。
- 所需資源：Dapper/EF Core
- 預估時間：1 天

3. 備份與回遷
- 實作細節：定期 dump、工具支援 remoteUrl → 下載回本地。
- 所需資源：備份腳本、API
- 預估時間：1 天

**關鍵程式碼/設定**：
```sql
CREATE TABLE MediaMap (
  Id INTEGER PRIMARY KEY AUTOINCREMENT,
  LocalPath TEXT NOT NULL UNIQUE,
  Sha256 TEXT NOT NULL,
  Provider TEXT NOT NULL,
  RemoteUrl TEXT,
  Status TEXT NOT NULL, -- Pending/Uploaded/Failed
  UploadedAt DATETIME,
  RowVersion BLOB
);
CREATE INDEX IX_MediaMap_Sha256 ON MediaMap(Sha256);
```

實際案例：作者強調「自己保有完整網站與檔案資料」、避免散落各地不易備份。
實作環境：SQLite 或 SQL Server、Dapper。
實測數據：
- 改善前：重複上傳、回遷困難
- 改善後：快速查詢、可回遷
- 改善幅度：重複上傳降至 0（目標）

Learning Points（學習要點）
核心知識點：
- 資料模型與索引設計
- 去重（內容雜湊）
- 備份/回遷流程

技能要求：
- 必備技能：SQL、交易一致性
- 進階技能：內容位址化（CAS）

延伸思考：
- 可加入檔案指紋與感知更新
- 風險：本地與遠端不一致
- 優化：加上 webhook 同步

Practice Exercise（練習題）
- 基礎練習：建立 MediaMap 資料表
- 進階練習：實作以 Sha256 去重上傳
- 專案練習：撰寫回遷工具：remote → local

Assessment Criteria（評估標準）
- 功能完整性（40%）：CRUD、去重、狀態管理
- 程式碼品質（30%）：交易、錯誤處理
- 效能優化（20%）：索引與查詢
- 創新性（10%）：CAS 思路應用

---

## Case #6: 首次讀取效能最佳化：背景化上傳與延遲外移

### Problem Statement（問題陳述）
**業務場景**：同步上傳導致首次讀取延遲過高，需優化用戶體驗。
**技術挑戰**：如何將上傳動作背景化，不阻塞第一次請求，同時確保後續請求能轉址。
**影響範圍**：TTFB、頁面完整載入時間、伺服器 CPU/IO。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 同步 I/O 與 API 呼叫耗時。
2. 無快取導致重複評估。
3. 首次請求與上傳搶資源。

**深層原因**：
- 架構層面：即時路徑與非即時任務未分離。
- 技術層面：缺乏可靠背景作業機制。
- 流程層面：無 SLA 對齊的策略。

### Solution Design（解決方案設計）
**解決策略**：首次請求直出本地檔，同時將上傳工作投遞到背景佇列；後續請求命中映射即轉址；加入節流與併發控制。

**實施步驟**：
1. 佇列與工作者
- 實作細節：Hangfire/HostedService 消費上傳任務。
- 所需資源：Hangfire、持久化儲存
- 預估時間：1 天

2. 任務去重與併發控管
- 實作細節：以 LocalPath/Sha256 為 key 去重；SemaphoreSlim 限速。
- 所需資源：資料表、記憶體鎖
- 預估時間：0.5 天

3. 映射預熱
- 實作細節：上傳成功即寫入映射並快取。
- 所需資源：MemoryCache/Redis
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public class UploadBackgroundService : BackgroundService
{
    private readonly Channel<string> _queue; // localPath
    protected override async Task ExecuteAsync(CancellationToken stoppingToken) {
        await foreach (var path in _queue.Reader.ReadAllAsync(stoppingToken)) {
            // 去重、上傳、存映射
        }
    }
}

// Handler 中首次請求
if (!_map.TryGet(localPath, out var remote)) {
    QueueUpload(localPath); // fire-and-forget
    return LocalResponse(); // 首次直出
}
return Redirect(remote);
```

實際案例：作者指出效能不如 WLW+Plugin，但以伺服器端換取彈性；背景化策略可緩解延遲。
實作環境：ASP.NET Core HostedService 或 Hangfire。
實測數據：
- 改善前：首次請求 + 上傳，延遲高
- 改善後：首次直出，後續轉址
- 改善幅度：首次延遲大幅降低（定性）

Learning Points（學習要點）
核心知識點：
- 背景作業架構
- 去重/限流
- 快取預熱

技能要求：
- 必備技能：非同步程式設計
- 進階技能：佇列設計與回壓

延伸思考：
- 批次預先外移熱門資源
- 風險：背景失敗未補償
- 優化：重試與死信佇列

Practice Exercise（練習題）
- 基礎練習：建立 Channel-based 背景服務
- 進階練習：實作去重與限流
- 專案練習：整合到 Handler 工作流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：背景上傳可用
- 程式碼品質（30%）：非同步、安全
- 效能優化（20%）：延遲與吞吐平衡
- 創新性（10%）：回壓/死信設計

---

## Case #7: HTTP 快取與轉址策略（301/302）最佳化

### Problem Statement（問題陳述）
**業務場景**：外移後的圖片請求頻繁，需兼顧瀏覽器快取與搜尋引擎友善度，決定使用 301 或 302。
**技術挑戰**：如何設計合理快取頭與選擇合適的轉址碼，避免錯誤快取或對 SEO 造成負面影響。
**影響範圍**：頻寬占用、載入時間、SEO。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不當的 301 導致難以切換供應商。
2. 缺少 Cache-Control/Etag 使重複下載。
3. 未區分暫時與永久遷移。

**深層原因**：
- 架構層面：未納入 SEO 與快取策略。
- 技術層面：對快取頭理解不足。
- 流程層面：缺乏變更管理與清快取機制。

### Solution Design（解決方案設計）
**解決策略**：預設 302（暫時）以保留切換彈性；當確定供應商穩定後，可逐步對熱門資源改為 301。為本地直出與遠端轉址均設定合理 Cache-Control、Etag/Last-Modified。

**實施步驟**：
1. 轉址碼規則
- 實作細節：以 Feature Flag 控制 301/302；路徑/熱門度細分。
- 所需資源：設定檔
- 預估時間：0.5 天

2. 快取頭
- 實作細節：本地回應加 Etag/Last-Modified；遠端轉址前設置短期快取。
- 所需資源：ASP.NET Cache API
- 預估時間：0.5 天

3. 清快取機制
- 實作細節：版本化 URL 或加 Cache-Busting Query。
- 所需資源：內容散列
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// 設定 302 預設
context.Response.StatusCode = 302;
context.Response.Headers["Cache-Control"] = "max-age=3600"; // 對轉址結果短期快取

// 本地直出加 ETag
var etag = "\"" + fileHash + "\"";
if (context.Request.Headers["If-None-Match"] == etag) { context.Response.StatusCode = 304; return; }
context.Response.Headers["ETag"] = etag;
```

實際案例：文章提及可「隨時換相片服務」，故不建議一開始用 301 鎖定。
實作環境：ASP.NET、IIS。
實測數據：
- 改善前：重複下載、彈性低
- 改善後：流量下降、彈性提高
- 改善幅度：Cache 命中提升（定性）

Learning Points（學習要點）
核心知識點：
- 301 vs 302 選擇
- Cache-Control/ETag/Last-Modified
- Cache Busting

技能要求：
- 必備技能：HTTP 協定
- 進階技能：SEO/快取策略

延伸思考：
- 使用 CDN 以邊緣快取
- 風險：錯誤 301 很難回滾
- 優化：灰度轉 301

Practice Exercise（練習題）
- 基礎練習：回應加上 ETag 與 304 處理
- 進階練習：以 Feature Flag 切換 301/302
- 專案練習：為熱門資源做灰度 301

Assessment Criteria（評估標準）
- 功能完整性（40%）：快取與轉址策略正確
- 程式碼品質（30%）：清晰與可配置
- 效能優化（20%）：帶寬節省
- 創新性（10%）：灰度策略

---

## Case #8: 外部服務中斷時的回退與斷路器

### Problem Statement（問題陳述）
**業務場景**：Flickr/YouTube 偶發性中斷或頻率限制，導致上傳失敗或轉址目標不可用。
**技術挑戰**：如何健壯地處理外部失敗，保障讀者可讀性與站台穩定。
**影響範圍**：可用性、錯誤率、使用者體驗。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 上游 API 失敗或超時。
2. 頻率限制導致拒絕服務。
3. 網路波動。

**深層原因**：
- 架構層面：無失敗隔離。
- 技術層面：缺乏重試/退避與斷路器。
- 流程層面：未定義回退行為。

### Solution Design（解決方案設計）
**解決策略**：引入 Polly 做重試與斷路器；遠端不可用時直接回傳本地檔並延遲重試；緩存失敗狀態避免風暴。

**實施步驟**：
1. 失敗策略
- 實作細節：指數退避、斷路器閾值設定。
- 所需資源：Polly
- 預估時間：0.5 天

2. 快速回退
- 實作細節：斷路器開啟時一律本地直出。
- 所需資源：Handler 集成
- 預估時間：0.5 天

3. 失敗快取
- 實作細節：短期快取失敗結果，避免重複打外部。
- 所需資源：MemoryCache
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
var retry = Policy
  .Handle<Exception>()
  .WaitAndRetryAsync(3, i => TimeSpan.FromSeconds(Math.Pow(2, i)));

var breaker = Policy
  .Handle<Exception>()
  .CircuitBreakerAsync(5, TimeSpan.FromMinutes(2));

// 上傳呼叫
await breaker.WrapAsync(retry).ExecuteAsync(() => _flickr.UploadAsync(localPath, meta, ct));
```

實際案例：作者強調可「隨時關掉這個功能」，即回退到本地直出。
實作環境：ASP.NET、Polly。
實測數據：
- 改善前：外部失敗導致整體故障
- 改善後：快速回退，穩定性提升
- 改善幅度：錯誤率下降（定性）

Learning Points（學習要點）
核心知識點：
- 斷路器/重試/退避
- 快速回退設計
- 負面快取

技能要求：
- 必備技能：穩健性模式
- 進階技能：SLO/SLA 對齊

延伸思考：
- 以健康探測恢復斷路
- 風險：過度重試雪崩
- 優化：分級失敗策略

Practice Exercise（練習題）
- 基礎練習：為上傳加 WaitAndRetry
- 進階練習：加入 Circuit Breaker 與回退
- 專案練習：做失敗注入測試

Assessment Criteria（評估標準）
- 功能完整性（40%）：失敗時可用
- 程式碼品質（30%）：策略清晰
- 效能優化（20%）：避免風暴
- 創新性（10%）：失敗觀測儀表

---

## Case #9: 凭證與帳號切換：避免單一帳號綁定

### Problem Statement（問題陳述）
**業務場景**：不想被單一 Flickr 帳號與工具綁死，希望可旋轉金鑰、切換帳號與分流上傳。
**技術挑戰**：安全存放 API Key、Token 與多帳號路由，避免外洩與錯誤使用。
**影響範圍**：安全合規、連續運行、供應商風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. API Key/Secret 硬編碼或明文存放。
2. Token 過期未輪換。
3. 多帳號策略缺失。

**深層原因**：
- 架構層面：沒有秘密管理與抽象。
- 技術層面：未設計多租戶/多帳號支持。
- 流程層面：缺乏輪換與審核流程。

### Solution Design（解決方案設計）
**解決策略**：導入機密管理（User Secret/KeyVault）、抽象 CredentialProvider，根據策略（流量、類別）選擇帳號；提供輪換 API 與審核記錄。

**實施步驟**：
1. 機密管理
- 實作細節：KeyVault 或 Windows DPAPI 加密儲存。
- 所需資源：KeyVault/DPAPI
- 預估時間：0.5 天

2. 多帳號策略
- 實作細節：根據標籤/目錄選帳號；故障自動切換。
- 所需資源：設定檔、策略類
- 預估時間：0.5 天

3. 輪換與審計
- 實作細節：金鑰輪換 API 與審計日誌。
- 所需資源：管理介面或 CLI
- 預估時間：1 天

**關鍵程式碼/設定**：
```csharp
public interface ICredentialProvider {
    FlickrCredentials GetFor(string category);
    void Rotate(string accountName);
}
public record FlickrCredentials(string ApiKey, string Secret, string OAuthToken);

var creds = _credProvider.GetFor("photos");
var flickr = new Flickr(creds.ApiKey, creds.Secret) { OAuthAccessToken = creds.OAuthToken };
```

實際案例：作者提到不想被「某個 flickr 帳號綁死」。
實作環境：ASP.NET、Azure KeyVault（可選）、FlickrNet。
實測數據：
- 改善前：單一帳號依賴
- 改善後：可切換/輪換
- 改善幅度：可用性與安全性提升（定性）

Learning Points（學習要點）
核心知識點：
- 憑證管理與輪換
- 多帳號路由
- 審計與合規

技能要求：
- 必備技能：安全實務
- 進階技能：祕密管理服務

延伸思考：
- 支援多服務商跨帳號
- 風險：配置錯誤導致洩漏
- 優化：最小權限與 KMS

Practice Exercise（練習題）
- 基礎練習：從安全存放載入 Flickr Key/Secret
- 進階練習：根據分類選不同帳號
- 專案練習：實作輪換並驗證不中斷

Assessment Criteria（評估標準）
- 功能完整性（40%）：多帳號與輪換
- 程式碼品質（30%）：安全與抽象
- 效能優化（20%）：無冗餘呼叫
- 創新性（10%）：審計儀表板

---

## Case #10: 影片 HTTP → RTSP 自動轉址與未來導入 YouTube

### Problem Statement（問題陳述）
**業務場景**：目前影片僅能從 HTTP 自動轉至 RTSP 播放，未整合 YouTube 上傳與託管。
**技術挑戰**：跨協定轉址、播放器兼容性、未來對接 YouTube API。
**影響範圍**：影片可播放性、裝置支援、網路負載。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不同裝置/瀏覽器對 RTSP 支援度低。
2. 無 YouTube API 串接流程。
3. 影片檔案大、上傳與轉碼耗時。

**深層原因**：
- 架構層面：缺乏影片專屬流程。
- 技術層面：轉碼與播放器相依性。
- 流程層面：上傳/轉碼/可見性流程未定義。

### Solution Design（解決方案設計）
**解決策略**：暫時以 UA 檢測決定 RTSP/HTTP 回退；規劃 Provider 架構導入 YouTube 上傳，完成後以 302 轉址到 YouTube 觀看頁或嵌入播放器。

**實施步驟**：
1. UA 檢測回退
- 實作細節：不支援 RTSP 則回 HTTP/HTML5 播放方案。
- 所需資源：UA Parser、HTML5 video
- 預估時間：0.5 天

2. YouTube Provider
- 實作細節：實作上傳、輪詢轉碼狀態、取得可公開 URL。
- 所需資源：YouTube Data API
- 預估時間：2 天

3. 轉址與嵌入
- 實作細節：返回嵌入代碼或 302 到觀看頁。
- 所需資源：Template
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
if (mediaType == MediaType.Video) {
    if (_ytEnabled) {
        var res = await _yt.UploadAsync(localPath, meta, ct);
        SaveMap(localPath, res.RemoteUrl, "YouTube");
        return Redirect(res.RemoteUrl);
    }
    // 臨時 RTSP/HTTP 回退
    return Redirect(BuildRtspUrl(localPath));
}
```

實際案例：作者說明「影片難度高，現實作僅 HTTP 自動轉 RTSP，未來轉 YouTube」。
實作環境：ASP.NET、YouTube Data API。
實測數據：
- 改善前：部分裝置無法播放
- 改善後：導入 YouTube 後普適性提升（預期）
- 改善幅度：播放成功率提高（定性）

Learning Points（學習要點）
核心知識點：
- 協定轉換與播放相容
- 影片託管 API
- 轉碼狀態管理

技能要求：
- 必備技能：Web 視訊播放
- 進階技能：外部 API/轉碼流程

延伸思考：
- 自動產生 poster/字幕
- 風險：版權/地區限制
- 優化：漸進式導入

Practice Exercise（練習題）
- 基礎練習：UA 檢測回退
- 進階練習：串接 YouTube 上傳並取得 URL
- 專案練習：完成影片 Provider 全流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：可播放且可回退
- 程式碼品質（30%）：清晰流程
- 效能優化（20%）：上傳/輪詢節流
- 創新性（10%）：播放器 UX

---

## Case #11: ZIP 檔虛擬為資料夾並規劃外移至 SkyDrive

### Problem Statement（問題陳述）
**業務場景**：ZIP 檔下載耗帶寬；目前做法是將 ZIP 虛擬為資料夾供瀏覽，未來希望自動轉至 SkyDrive 託管。
**技術挑戰**：虛擬檔案系統、目錄索引與權限管理、對接 OneDrive API。
**影響範圍**：帶寬、可用性、可瀏覽性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. ZIP 單體大，下載耗上行。
2. 缺乏外部託管，無法分散流量。
3. 瀏覽 ZIP 內容體驗差。

**深層原因**：
- 架構層面：無 VFS 抽象。
- 技術層面：缺少 OneDrive API 集成。
- 流程層面：上傳與目錄對應未定義。

### Solution Design（解決方案設計）
**解決策略**：建立 ZIP 虛擬檔案系統與索引頁；加入 OneDrive Provider，將 ZIP 檔或展開內容外移至 OneDrive，提供共享連結。

**實施步驟**：
1. VFS 與索引
- 實作細節：以 SharpZipLib 讀取 ZIP，輸出目錄索引 HTML。
- 所需資源：SharpZipLib
- 預估時間：1 天

2. OneDrive 上傳
- 實作細節：以 Microsoft Graph API 上傳，保存共享 URL。
- 所需資源：Graph SDK
- 預估時間：1.5 天

3. 轉址/嵌入
- 實作細節：點擊檔案即 302 至 OneDrive 連結。
- 所需資源：Handler 擴充
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
using (var zip = new ZipInputStream(File.OpenRead(localZip))) {
    ZipEntry entry;
    while ((entry = zip.GetNextEntry()) != null) {
        // 列出 entry，產生成索引頁
    }
}
```

實際案例：作者描述目前 ZIP 虛擬化為資料夾，未來考慮轉至 SkyDrive。
實作環境：ASP.NET、SharpZipLib、Microsoft Graph。
實測數據：
- 改善前：本機承擔 ZIP 流量
- 改善後：外部託管，流量外移
- 改善幅度：上行節省顯著（定性）

Learning Points（學習要點）
核心知識點：
- VFS 與壓縮檔索引
- OneDrive/Graph 上傳
- 共享連結與權限

技能要求：
- 必備技能：檔案處理
- 進階技能：Graph API

延伸思考：
- 局部熱點檔案預外移
- 風險：共享權限誤設
- 優化：按需展開上傳

Practice Exercise（練習題）
- 基礎練習：輸出 ZIP 索引頁
- 進階練習：上傳 ZIP 至 OneDrive
- 專案練習：完成 ZIP → OneDrive 外移流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：索引與外移可用
- 程式碼品質（30%）：錯誤處理
- 效能優化（20%）：I/O 與佇列
- 創新性（10%）：按需展開策略

---

## Case #12: 內容改寫 Proxy（以 Google News POC 為例）

### Problem Statement（問題陳述）
**業務場景**：希望把第三方頁面中的圖片資源改寫到站內代理目錄，驗證改寫與代理技術可行性。
**技術挑戰**：如何解析 HTML、改寫資源 URL 並正確指向代理 Handler。
**影響範圍**：資料夾結構、請求導流、觀測驗證。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 直接嵌外部圖連結，不利於統一治理。
2. 難以使用 Fiddler 觀察代理是否生效。
3. HTML 改寫易破壞結構。

**深層原因**：
- 架構層面：缺乏內容改寫層。
- 技術層面：未使用可靠 DOM 解析。
- 流程層面：無驗證工具與流程。

### Solution Design（解決方案設計）
**解決策略**：建立簡單內容改寫器，將 <img src> 改為 /media/images/ 導向，並以 Fiddler 驗證請求走向代理；POC 確認後再導入正式站台。

**實施步驟**：
1. DOM 解析
- 實作細節：使用 HtmlAgilityPack 安全改寫 <img>。
- 所需資源：HtmlAgilityPack
- 預估時間：0.5 天

2. URL 改寫與對映
- 實作細節：將外部 URL 映射至本地代理路徑並保存對照。
- 所需資源：映射存儲
- 預估時間：0.5 天

3. 驗證
- 實作細節：以 Fiddler 檢視請求是否轉向 /media/images/*。
- 所需資源：Fiddler
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
var doc = new HtmlDocument();
doc.LoadHtml(html);
foreach (var img in doc.DocumentNode.SelectNodes("//img[@src]")) {
    var src = img.GetAttributeValue("src", "");
    var local = MapToProxy(src); // 對應到 /media/images/*
    img.SetAttributeValue("src", local);
}
```

實際案例：POC 頁面提供，並建議用 Fiddler 觀測。
實作環境：.NET、HtmlAgilityPack、Fiddler。
實測數據：
- 改善前：外部圖片直連
- 改善後：改寫至代理
- 改善幅度：治理能力提升（定性）

Learning Points（學習要點）
核心知識點：
- HTML 安全改寫
- 代理導流
- 工具化驗證

技能要求：
- 必備技能：HTML/DOM
- 進階技能：改寫準則

延伸思考：
- 可對 CSS/JS 做類似改寫
- 風險：跨站資源策略（CORS）
- 優化：正規化與白名單

Practice Exercise（練習題）
- 基礎練習：改寫 <img> src
- 進階練習：改寫 <source>、<picture>
- 專案練習：完成一個簡單內容代理器

Assessment Criteria（評估標準）
- 功能完整性（40%）：改寫正確
- 程式碼品質（30%）：健壯解析
- 效能優化（20%）：批次處理
- 創新性（10%）：可視化 diff

---

## Case #13: 功能開關與設定化：隨時停用/更換服務

### Problem Statement（問題陳述）
**業務場景**：需能「隨時關掉這個功能」與「隨時換相片服務」，保留操作彈性。
**技術挑戰**：如何以設定化與 Feature Flag 控制功能開關與供應商選擇，且支援熱更新。
**影響範圍**：營運彈性、風險控管。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 程式碼硬編供應商參數。
2. 修改需重新部署。
3. 無灰度管控能力。

**深層原因**：
- 架構層面：缺少設定中心與旗標系統。
- 技術層面：未支援動態更新。
- 流程層面：缺乏變更治理。

### Solution Design（解決方案設計）
**解決策略**：建立設定檔與 Feature Flag（如 AppSettings + LaunchDarkly/自製），支援提供者名單與切換策略；以 IOptionsMonitor 支援熱更新。

**實施步驟**：
1. 設定模型
- 實作細節：OffloadEnabled、PreferredProvider 等。
- 所需資源：appsettings.json
- 預估時間：0.5 天

2. 熱更新
- 實作細節：IOptionsMonitor/檔案監看自動套用。
- 所需資源：.NET Options
- 預估時間：0.5 天

3. 灰度控制
- 實作細節：依路徑/比例開關。
- 所需資源：自訂策略
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```json
{
  "FlickrProxy": {
    "OffloadEnabled": true,
    "PreferredImageProvider": "Flickr",
    "GradualRollout": 0.5
  }
}
```

實際案例：文章直言可隨時關閉/更換服務。
實作環境：ASP.NET Core Options、或傳統 web.config。
實測數據：
- 改善前：更改需重部
- 改善後：設定化、熱更新
- 改善幅度：變更時效提升（定性）

Learning Points（學習要點）
核心知識點：
- Feature Flag
- IOptionsMonitor
- 灰度與回滾

技能要求：
- 必備技能：設定管理
- 進階技能：變更治理

延伸思考：
- 中央設定服務
- 風險：錯誤配置
- 優化：驗證與健康檢查

Practice Exercise（練習題）
- 基礎練習：以設定開關功能
- 進階練習：加入 50% 灰度
- 專案練習：提供管理 UI

Assessment Criteria（評估標準）
- 功能完整性（40%）：開關/切換可用
- 程式碼品質（30%）：解耦與測試
- 效能優化（20%）：監控延遲
- 創新性（10%）：灰度策略

---

## Case #14: 去重與競態：避免重複上傳與並發錯誤

### Problem Statement（問題陳述）
**業務場景**：熱門圖片高併發請求時，可能出現多次重複上傳與映射覆蓋。
**技術挑戰**：如何在多執行緒/多實例下做到去重、鎖定與正確狀態轉移。
**影響範圍**：外部 API 費用、效率、資料一致性。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏基於雜湊的唯一鍵。
2. 沒有分散式鎖。
3. 沒有上傳中狀態。

**深層原因**：
- 架構層面：未設計併發控制。
- 技術層面：無原子更新與重試保護。
- 流程層面：缺乏冪等性設計。

### Solution Design（解決方案設計）
**解決策略**：以 Sha256 作唯一鍵，建立「Pending → Uploaded/Failed」狀態機；以資料庫/Redis 分散式鎖避免同時上傳；上傳操作冪等。

**實施步驟**：
1. 唯一鍵與狀態機
- 實作細節：MediaMap 加唯一索引與狀態流轉。
- 所需資源：資料庫
- 預估時間：0.5 天

2. 分散式鎖
- 實作細節：Redis SET NX 獲鎖，過期保護。
- 所需資源：Redis
- 預估時間：0.5 天

3. 冪等上傳
- 實作細節：ExistsAsync 先查、重試 safe。
- 所需資源：Provider API
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// Redis 分散式鎖示例
var lockKey = "upload:" + sha256;
if (await redis.StringSetAsync(lockKey, instanceId, expiry: TimeSpan.FromMinutes(5), when: When.NotExists)) {
    try {
        // 查 exists、上傳、更新狀態
    } finally {
        // 釋放鎖（需驗證持有者）
    }
}
```

實際案例：作者計畫整合多 Handler 成 Provider 架構，並在高併發場景下需要正確性。
實作環境：Redis、Dapper/EF Core。
實測數據：
- 改善前：重複上傳
- 改善後：零重複（目標）
- 改善幅度：API 成本降低（定性）

Learning Points（學習要點）
核心知識點：
- 冪等與鎖
- 狀態機設計
- 分散式一致性

技能要求：
- 必備技能：Redis、SQL
- 進階技能：一致性與容錯

延伸思考：
- 導入 outbox/inbox pattern
- 風險：鎖失效
- 優化：租約與延長

Practice Exercise（練習題）
- 基礎練習：以 SHA-256 識別檔案
- 進階練習：Redis 分散式鎖保護上傳
- 專案練習：完成冪等上傳全流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：去重與正確狀態
- 程式碼品質（30%）：併發安全
- 效能優化（20%）：鎖開銷控制
- 創新性（10%）：鎖租約設計

---

## Case #15: 可觀測性與帶寬節省度量（Fiddler、日誌、指標）

### Problem Statement（問題陳述）
**業務場景**：需要驗證外移成效與穩定性，並在 POC 與正式環境持續監控。
**技術挑戰**：如何度量轉址率、帶寬節省、本地 vs 外部流量占比，並快速調試。
**影響範圍**：決策依據、營運調整、問題定位。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏可視化數據。
2. 難以快速檢視請求鏈。
3. 無告警閾值。

**深層原因**：
- 架構層面：缺項目級監控方案。
- 技術層面：未埋點與追蹤。
- 流程層面：無 SLI/SLO。

### Solution Design（解決方案設計）
**解決策略**：建立指標（轉址率、節省上行、失敗率）、日誌（請求 ID、路由決策）、追蹤（Activity）；利用 Fiddler 在 POC 阶段驗證流向；配置告警。

**實施步驟**：
1. 埋點與度量
- 實作細節：Prometheus/Influx、OpenTelemetry。
- 所需資源：Metrics/Tracing SDK
- 預估時間：1 天

2. 日誌與關聯 ID
- 實作細節：每次請求標註 RequestId 與決策結果。
- 所需資源：Serilog/NLog
- 預估時間：0.5 天

3. 告警
- 實作細節：失敗率與轉址率異常告警。
- 所需資源：Alertmanager
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
_metrics.Counter("flickrproxy_redirect_total").Inc();
_metrics.Gauge("flickrproxy_local_bytes").Add(bytes);
using var activity = _tracer.StartActivity("proxy_decision");
// log decision, requestId
```

實際案例：作者建議用 Fiddler 檢視 POC。
實作環境：OpenTelemetry、Prometheus、Fiddler。
實測數據：
- 改善前：無數據
- 改善後：可見度提升
- 改善幅度：問題定位效率提升（定性）

Learning Points（學習要點）
核心知識點：
- 指標、日誌、追蹤三板斧
- 用戶端抓包與伺服器埋點
- SLI/SLO 設計

技能要求：
- 必備技能：基礎觀測
- 進階技能：追蹤關聯

延伸思考：
- 前端 RUM 度量體驗
- 風險：過度埋點成本
- 優化：採樣與聚合

Practice Exercise（練習題）
- 基礎練習：計數轉址次數
- 進階練習：統計帶寬節省
- 專案練習：建立儀表板與告警

Assessment Criteria（評估標準）
- 功能完整性（40%）：關鍵指標完整
- 程式碼品質（30%）：低耦合
- 效能優化（20%）：埋點開銷
- 創新性（10%）：可視化

---

## Case #16: 備份與還原：本地副本優先策略

### Problem Statement（問題陳述）
**業務場景**：即使外移，仍希望「自己保有一份完整的網站跟檔案資料」，以便備份/還原。
**技術挑戰**：外移後如何確保本地副本與映射一致，並在還原時恢復映射與資料。
**影響範圍**：災難復原、法遵要求、營運連續性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 外部與本地有可能脫節。
2. 無備份策略與頻率。
3. 映射表還原不完整。

**深層原因**：
- 架構層面：缺乏資料主權思維。
- 技術層面：無一致性驗證。
- 流程層面：無演練。

### Solution Design（解決方案設計）
**解決策略**：本地作為真實來源（SoR）；定期校驗本地→遠端完整性；備份 MediaMap 與檔案；提供一鍵還原工具。

**實施步驟**：
1. 備份策略
- 實作細節：每日差異、每週全量；離線備份。
- 所需資源：備份工具
- 預估時間：0.5 天

2. 完整性校驗
- 實作細節：比對 Sha256 與遠端存在性。
- 所需資源：校驗腳本
- 預估時間：1 天

3. 還原工具
- 實作細節：重建資料夾、還原映射、缺失重上傳。
- 所需資源：CLI
- 預估時間：1 天

**關鍵程式碼/設定**：
```bash
# 範例：每日差異備份
robocopy d:\media \\backup\media /MIR /Z /FFT /R:2 /W:5 /LOG:backup.log
```

實際案例：作者強調避免資料散落，易備份還原。
實作環境：Windows 任務排程、CLI 工具。
實測數據：
- 改善前：還原困難
- 改善後：一鍵還原
- 改善幅度：RTO/RPO 改善（定性）

Learning Points（學習要點）
核心知識點：
- SoR 與外移的關係
- 差異備份
- 還原演練

技能要求：
- 必備技能：備份腳本
- 進階技能：一致性檢查

延伸思考：
- 雲端備援
- 風險：備份未驗證
- 優化：自動演練

Practice Exercise（練習題）
- 基礎練習：建立備份批次檔
- 進階練習：寫校驗腳本
- 專案練習：實作還原 CLI

Assessment Criteria（評估標準）
- 功能完整性（40%）：備份/還原可用
- 程式碼品質（30%）：可維護
- 效能優化（20%）：備份效率
- 創新性（10%）：自動演練

---

## Case #17: 服務遷移與帳號切換：平滑過渡與鏈接長期可用

### Problem Statement（問題陳述）
**業務場景**：未來可能從 Flickr 換到其他服務或更換帳號，需確保舊文可用且 SEO 不受影響。
**技術挑戰**：如何在不破壞原文結構的前提下，完成供應商切換與鏈接維持。
**影響範圍**：鏈接有效性、SEO、使用者體驗。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 外部 URL 變更。
2. 轉址策略不當造成快取鎖定。
3. 無批次遷移工具。

**深層原因**：
- 架構層面：缺乏中介層與命名穩定性。
- 技術層面：映射更新流程缺失。
- 流程層面：無灰度遷移。

### Solution Design（解決方案設計）
**解決策略**：所有文章引用只指向站內代理 URL；更換時，更新映射目標與轉址策略（302→301 灰度）；提供批次重新上傳/重建映射工具。

**實施步驟**：
1. 灰度遷移
- 實作細節：部分路徑先切換供應商，觀察指標。
- 所需資源：Feature Flag
- 預估時間：0.5 天

2. 映射重建
- 實作細節：批次下載/上傳新供應商，更新 RemoteUrl。
- 所需資源：遷移 CLI
- 預估時間：1 天

3. SEO 保護
- 實作細節：保留站內 URL，不改文章；控制 301/302。
- 所需資源：策略設定
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```bash
# 遷移工具示意
migrate-media --from Flickr --to Imgur --path /media/images --dry-run
```

實際案例：作者強調可「隨時換相片服務」與不被帳號綁死。
實作環境：自製 CLI、Provider 架構。
實測數據：
- 改善前：切換成本高
- 改善後：灰度與批次遷移可行
- 改善幅度：風險顯著降低（定性）

Learning Points（學習要點）
核心知識點：
- 灰度遷移
- 穩定 URL 設計
- 遷移工具化

技能要求：
- 必備技能：CLI 開發
- 進階技能：批次處理與回滾

延伸思考：
- 雙寫策略
- 風險：費率與配額
- 優化：遷移模擬

Practice Exercise（練習題）
- 基礎練習：做一個 dry-run 遷移
- 進階練習：實際搬運小批資源
- 專案練習：全站遷移並觀測

Assessment Criteria（評估標準）
- 功能完整性（40%）：平滑遷移
- 程式碼品質（30%）：安全與回滾
- 效能優化（20%）：批次效率
- 創新性（10%）：灰度策略

---

## Case #18: 從 POC 到產品化：驗證、硬化與發佈

### Problem Statement（問題陳述）
**業務場景**：已有 POC 證明技巧可行，需要產品化：穩定、可配、可觀測、可擴展。
**技術挑戰**：如何從 demo 級別快速硬化為生產等級服務。
**影響範圍**：穩定性、維運成本、擴展性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. POC 缺少錯誤處理與回退。
2. 無測試與監控。
3. 無部署流程。

**深層原因**：
- 架構層面：未模組化。
- 技術層面：缺乏自動化測試。
- 流程層面：缺乏 CI/CD。

### Solution Design（解決方案設計）
**解決策略**：建立最小產品化清單：模組化 Provider、映射儲存、決策引擎、背景佇列、快取、回退、觀測、設定化、CI/CD；逐步引入測試與監控。

**實施步驟**：
1. 測試與品質
- 實作細節：單元/整合/性能測試；契約測試。
- 所需資源：xUnit、WireMock
- 預估時間：1.5 天

2. 監控與告警
- 實作細節：指標/日誌/追蹤與儀表。
- 所需資源：同 Case #15
- 預估時間：1 天

3. 部署與配置
- 實作細節：CI/CD、環境變數配置、金絲雀。
- 所需資源：GitHub Actions/Azure DevOps
- 預估時間：1 天

**關鍵程式碼/設定**：
```yaml
# GitHub Actions 簡化
name: build-and-deploy
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - run: dotnet build --configuration Release
      - run: dotnet test
```

實際案例：文章提供 POC 網頁並建議用 Fiddler 檢視。
實作環境：.NET、CI/CD 平台。
實測數據：
- 改善前：POC 可靠性低
- 改善後：產品化能力提升
- 改善幅度：可用性/可維護性提升（定性）

Learning Points（學習要點）
核心知識點：
- 產品化最小集合
- 測試金字塔
- CI/CD

技能要求：
- 必備技能：測試與部署
- 進階技能：可觀測性

延伸思考：
- 發布策略：金絲雀/藍綠
- 風險：自動化不足
- 優化：基準測試

Practice Exercise（練習題）
- 基礎練習：撰寫單元測試覆蓋決策引擎
- 進階練習：建立 CI pipeline
- 專案練習：將整體方案部署到測試環境

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試與部署可用
- 程式碼品質（30%）：可維護
- 效能優化（20%）：基準測試
- 創新性（10%）：自動化程度

---

## 案例分類

1. 按難度分類
- 入門級（適合初學者）：Case 12, 13
- 中級（需要一定基礎）：Case 1, 2, 3, 6, 7, 8, 9, 11, 15, 16, 18
- 高級（需要深厚經驗）：Case 4, 5, 10, 14, 17

2. 按技術領域分類
- 架構設計類：Case 4, 16, 17, 18
- 效能優化類：Case 6, 7, 15
- 整合開發類：Case 1, 3, 9, 10, 11
- 除錯診斷類：Case 12, 15
- 安全防護類：Case 8, 9, 14

3. 按學習目標分類
- 概念理解型：Case 1, 2, 7, 16
- 技能練習型：Case 3, 5, 6, 12, 13, 15
- 問題解決型：Case 8, 10, 11, 14, 17
- 創新應用型：Case 4, 18

## 案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 12（內容改寫 POC）與 Case 13（功能開關）：快速建立直覺與控制力
  - Case 1（基本外移）與 Case 3（決策引擎）：掌握核心流程
- 依賴關係：
  - Case 5（映射儲存）是 Case 1/3/6/17 的依賴
  - Case 4（Provider 架構）是 Case 9/10/11/17 的依賴
  - Case 6（背景上傳）依賴 Case 3（決策）與 Case 5（映射）
  - Case 7（快取策略）與 Case 15（觀測）橫向支援所有案例
  - Case 8（回退）與 Case 14（去重併發）強化穩定性，建議在 Case 6 後導入
  - Case 16（備份）與 Case 17（遷移）建立長期治理，建議於核心穩定後進行
  - Case 18（產品化）最後整合
- 完整學習路徑建議：
  1) Case 12 → 13 → 1 → 3 → 5
  2) 導入 Case 6（背景化）與 Case 7（快取）
  3) 加固 Case 8（回退）與 Case 14（併發）
  4) 擴展 Case 4（Provider）→ 9（憑證）→ 10（影片）→ 11（ZIP）
  5) 治理 Case 15（觀測）→ 16（備份）
  6) 策略 Case 17（遷移）
  7) 收斂 Case 18（產品化與發佈）

說明：以上實測數據部分，多為指標設計與預期方向；原文未提供具體數字，實際應在 POC 與試運行階段收集並填充。