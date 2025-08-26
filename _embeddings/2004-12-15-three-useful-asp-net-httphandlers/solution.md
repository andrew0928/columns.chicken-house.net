以下內容基於文章中提出的三個 ASP.NET HttpHandler（MediaService、RssMonitor、ZipVirtualFolder）所衍生的實戰型案例，共 16 個。每個案例均以實務場景、根因、方案、代碼與練習評估構成，便於教學、專案實作與能力評估。

## Case #1: 影音檔自動轉向 Windows Media Services（ASX 轉發）

### Problem Statement（問題陳述）
業務場景：小型 ADSL 架站者在網頁直接提供 video/audio 檔供親友瀏覽。但大檔案以 HTTP 直下非常吃頻寬，且需教非技術使用者分辨何時用 http:// 與何時用 mms://，經常操作錯誤造成人員溝通成本與使用體驗不一致。
技術挑戰：需要在不改動內容發佈流程與 URL 的前提下，將針對影音檔的 HTTP 請求自動轉向 Windows Media Services，且能被 Media Player 7.0+ 自動啟動播放。
影響範圍：網站頻寬消耗、影音播放成功率、使用者訓練成本、站點可用性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 影音檔透過 HTTP 直接下載，消耗上行頻寬且不支援串流最佳化。
2. 使用者必須手動選擇 http:// 或 mms://，容易誤用。
3. 網站缺少針對特定副檔名的自動轉向機制。
深層原因：
- 架構層面：前端 URL 與後端媒體服務之間缺乏抽象層。
- 技術層面：未利用 HttpHandler 針對副檔名做協定切換（HTTP→MMS）。
- 流程層面：內容發佈與播放協定切換未自動化，依賴人工作業。

### Solution Design（解決方案設計）
解決策略：以 HttpHandler 接管 *.wmv/*.wma/*.asf 等請求，輸出一段 ASX（Advanced Stream Redirector）播放清單，內含 mms:// 來源。瀏覽器接收 ASX 後由 Media Player 啟動串流播放，達到對使用者透明的自動轉向。

實施步驟：
1. 註冊副檔名對應的 HttpHandler
- 實作細節：在 web.config 以 <httpHandlers> 或 <handlers> 綁定 *.wmv、*.wma、*.asf 至自訂 Handler。
- 所需資源：IIS/ASP.NET、Visual Studio。
- 預估時間：0.5 小時。

2. 在 Handler 回應 ASX 指向 mms://
- 實作細節：將 http:// 的主機名映射為 mms://，回應 Content-Type=video/x-ms-asf 並輸出 ASX。
- 所需資源：ASP.NET（.NET Framework 2.0+）。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// MediaServiceHttpHandler.cs
using System;
using System.Web;

public class MediaServiceHttpHandler : IHttpHandler
{
    public bool IsReusable => true;

    public void ProcessRequest(HttpContext context)
    {
        var requestUrl = context.Request.Url; // http://www.chicken-house.net/media/foo.wmv
        var httpBase = "http://www.chicken-house.net";
        var mmsBase  = "mms://www.chicken-house.net";

        // 依據實際環境做更穩健的主機映射
        var mmsUrl = requestUrl.ToString().Replace(httpBase, mmsBase, StringComparison.OrdinalIgnoreCase);

        context.Response.ContentType = "video/x-ms-asf"; // ASX MIME
        var asx = $"<ASX version='3.0'><ENTRY><REF HREF='{mmsUrl}'/></ENTRY></ASX>";
        context.Response.Write(asx);
    }
}
// web.config (IIS 7+)
<configuration>
  <system.webServer>
    <handlers>
      <add name="MediaHandlerWmv" path="*.wmv" verb="GET" type="MediaServiceHttpHandler"/>
      <add name="MediaHandlerWma" path="*.wma" verb="GET" type="MediaServiceHttpHandler"/>
      <add name="MediaHandlerAsf" path="*.asf" verb="GET" type="MediaServiceHttpHandler"/>
    </handlers>
  </system.webServer>
</configuration>
```

實際案例：文章作者以 ADSL 架設網站，將大檔丟給 Windows Media Services 播放，透過 HttpHandler 自動切換協定，讓家人無需分辨 http:// 與 mms://。
實作環境：ASP.NET（.NET Framework 2.0+）、Windows Media Player 7+、Windows Media Services。
實測數據：
改善前：使用者需手動選 mms://；HTTP 直載吃頻寬。
改善後：ASX 自動轉向 mms://；減少 HTTP 帶寬占用。
改善幅度：操作負擔明顯降低、頻寬壓力降低（非數值性描述）。

Learning Points（學習要點）
核心知識點：
- HttpHandler 以副檔名為條件進行協定轉向
- ASX 清單格式與 Content-Type
- URL 主機映射與透明轉發

技能要求：
必備技能：ASP.NET HttpHandler、web.config 映射、基本 XML 輸出。
進階技能：對串流服務（WMS）的理解、播放器相容性測試。

延伸思考：
此方案亦可用於 HLS/DASH 播放清單轉發；限制是依賴 Media Player 相容性；可優化為偵測 UA 或同時提供 fallback。

Practice Exercise（練習題）
基礎練習：為 *.mp3 請求產生 ASX 轉向 mms://（30 分鐘）
進階練習：同時提供 mms 與 http 的雙 REF，並測試相容性（2 小時）
專案練習：為整個 /media 目錄動態產生 ASX 播放清單（多檔連播）（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可正確為 *.wmv/*.wma/*.asf 產出可播放的 ASX
程式碼品質（30%）：結構清晰、具例外處理與日誌
效能優化（20%）：避免多餘 IO、回應頭設置正確
創新性（10%）：提供智慧映射與多來源 fallback 設計

---

## Case #2: 統一 URL 與協定映射（HTTP→MMS 的單一入口）

### Problem Statement（問題陳述）
業務場景：內容編輯者只懂把影音檔放到網站目錄，卻不清楚串流服務的位址與協定，經常導致貼錯連結。期望對外只暴露一組 http:// 網址，後端自動決定使用 mms:// 播放。
技術挑戰：實現單一 URL 發佈與多協定後端映射，避免更動內容編輯工作流。
影響範圍：內容管理、錯誤連結率、維運溝通成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 前端 URL 與後端串流 URL 不一致，易貼錯。
2. 缺乏統一的映射策略與自動化。
3. 編輯人員不熟悉串流協定。
深層原因：
- 架構層面：未定義發佈層與播放層的邏輯隔離。
- 技術層面：缺乏以 HttpHandler 實作的 URL 轉換。
- 流程層面：內容發佈規範未標準化。

### Solution Design（解決方案設計）
解決策略：以 HttpHandler 為媒合層，建立 Host/Path 映射規則表，讓所有多媒體請求先經過 Handler，統一轉為串流協定，再回傳播放器可識別格式。

實施步驟：
1. 設計映射規則（Domain/Path → mms）
- 實作細節：以設定檔維護對應關係，支援不同環境（DEV/UAT/PROD）。
- 所需資源：web.config appSettings。
- 預估時間：1 小時。

2. 在 Handler 套用規則
- 實作細節：讀取配置，以字典匹配主機與目錄，組裝目標 mms URL。
- 所需資源：ASP.NET。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 映射設定讀取範例
var mappings = new Dictionary<string,string> {
  { "http://www.chicken-house.net/media", "mms://www.chicken-house.net/media" }
};
string MapToMms(string httpUrl)
{
    foreach (var kv in mappings)
        if (httpUrl.StartsWith(kv.Key, StringComparison.OrdinalIgnoreCase))
            return kv.Value + httpUrl.Substring(kv.Key.Length);
    return httpUrl; // fallback
}
```

實際案例：作者以一組 http:// 對外發佈，Handler 自動轉向 mms://，編輯者不需變更發佈步驟。
實作環境：ASP.NET。
實測數據：
改善前：連結錯誤率偏高、需教學分辨協定。
改善後：只需 http://，後端自動轉；錯誤率下降。
改善幅度：內容發佈失誤顯著降低（定性）。

Learning Points（學習要點）
核心知識點：
- URL 映射策略與設定化
- Handler 作為邏輯閘道

技能要求：
必備技能：web.config 管理、字串處理。
進階技能：多環境配置與熱更新。

延伸思考：
可擴展至 CDN/HLS/多來源加權選路；注意不同協定的權限控制差異。

Practice Exercise（練習題）
基礎練習：以 appSettings 建立一條映射規則（30 分鐘）
進階練習：支援多規則與環境變數切換（2 小時）
專案練習：可視化管理映射表的小工具（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：配置變更後可即時套用
程式碼品質（30%）：配置解析健壯、易維護
效能優化（20%）：映射查找 O(1)/O(logN)
創新性（10%）：支援規則優先級與萬用字元

---

## Case #3: 播放器相容性與回退（WMP 7+ 與 HTTP Fallback）

### Problem Statement（問題陳述）
業務場景：訪客裝置不一，有的未安裝或不支援 Media Player 7+。若僅回傳 ASX 會導致不可播放，需提供相容性的回退機制，以提升可達性。
技術挑戰：在不破壞既有串流優先的前提下，為不支援客戶端提供次佳解（例如直接 HTTP 下載）。
影響範圍：播放成功率、用戶體驗、客服負擔。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 客戶端能力差異導致 ASX 不一定可用。
2. 純 mms:// 方案缺乏備援。
3. 無法可靠偵測所有播放器能力。
深層原因：
- 架構層面：單一路徑設計缺乏多來源冗餘。
- 技術層面：未利用 ASX 支援多 REF。
- 流程層面：缺少相容性測試與回退策略。

### Solution Design（解決方案設計）
解決策略：在 ASX 中同時提供 mms:// 與 http:// REF；支援者優先用 mms，否則自動落到 http。必要時觀察 UA/Accept 進行微調，不做強耦合判斷。

實施步驟：
1. 產出多來源 ASX
- 實作細節：ASX <ENTRY> 內放多個 <REF>，順序代表優先級。
- 所需資源：ASP.NET。
- 預估時間：0.5 小時。

2. 加上 UA 訊息記錄
- 實作細節：記錄 UA 以便後續統計回退比例。
- 所需資源：日誌系統。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
var mmsUrl = MapToMms(requestUrl);
var httpUrl = requestUrl.ToString(); // 原始 HTTP 位址
var asx = $@"<ASX version='3.0'>
  <ENTRY>
    <REF HREF='{mmsUrl}'/>
    <REF HREF='{httpUrl}'/>
  </ENTRY>
</ASX>";
```

實際案例：文章提及「Media Player 7.0 以上，一切就全自動」，本方案擴充為未滿足條件時亦可播放或下載。
實作環境：ASP.NET。
實測數據：
改善前：部分裝置打不開 ASX。
改善後：提供回退路徑，成功率提高。
改善幅度：可用性提升（定性）。

Learning Points（學習要點）
核心知識點：
- ASX 多 REF 與優先序
- 相容性策略設計

技能要求：
必備技能：XML 操作、基本日誌。
進階技能：基於數據的相容性優化。

延伸思考：
可改以 HTML5 <video> 與 MSE 方案；風險是不同瀏覽器的解碼支援差異。

Practice Exercise（練習題）
基礎練習：為 ASX 加入 http Fallback（30 分鐘）
進階練習：記錄 UA 並產出回退統計（2 小時）
專案練習：自動調整 REF 順序的自適應策略（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：mms 不可用時能落到 http
程式碼品質（30%）：清晰可測試
效能優化（20%）：ASX 輕量、無冗餘
創新性（10%）：動態優先級調整

---

## Case #4: 頻寬保護與站台可用性（把大檔交給串流服務）

### Problem Statement（問題陳述）
業務場景：ADSL 小站遭遇影音直載時，上行頻寬被占滿，影響其他頁面載入與整體可用性。需要讓大檔交給更適合的 Windows Media Services。
技術挑戰：將現有連結不改、最小侵入導入，並觀察帶寬使用變化。
影響範圍：站台可用性、延遲、超時率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. HTTP 直載無串流最佳化，長連線大量占用。
2. ADSL 上行頻寬小。
3. 下載與瀏覽資源競爭。
深層原因：
- 架構層面：未做職責分離（Web vs Media）。
- 技術層面：無串流卸載。
- 流程層面：無監控帶寬與壓力測試流程。

### Solution Design（解決方案設計）
解決策略：沿用 Case #1 Handler，將影音卸載到 WMS，並加上簡易監控（IIS 日誌、性能計數器）以驗證效果。

實施步驟：
1. 導入 Handler（同 Case #1）
- 實作細節：綁定副檔名。
- 所需資源：ASP.NET/IIS。
- 預估時間：0.5 小時。

2. 帶寬觀測與比對
- 實作細節：比對前後 IIS 帶寬與請求分佈、峰值。
- 所需資源：IIS 日誌分析工具。
- 預估時間：2 小時。

關鍵程式碼/設定：同 Case #1（略）

實際案例：作者將大檔放在 WMS，降低網站頻寬壓力。
實作環境：IIS + Windows Media Services。
實測數據：
改善前：HTTP 影音流量佔比高、網頁載入緩慢。
改善後：HTTP 影音降載，頁面回應變穩定。
改善幅度：站台可用性提升（定性）。

Learning Points（學習要點）
核心知識點：
- 職責分離與流量卸載
- 基於日誌的效益驗證

技能要求：
必備技能：IIS 日誌分析。
進階技能：建立簡單的帶寬儀表板。

延伸思考：
亦可導入 CDN；限制是串流協定支援差異；可進一步以 QoS 或頻寬限制輔助。

Practice Exercise（練習題）
基礎練習：用 Log Parser 分析影音請求佔比（30 分鐘）
進階練習：導入帶寬趨勢圖表（2 小時）
專案練習：壓測（JMeter）比對卸載前後延遲（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：卸載生效
程式碼品質（30%）：配置清楚
效能優化（20%）：觀測與回饋
創新性（10%）：自動化報表

---

## Case #5: 內容編輯流程簡化（無需教育協定差異）

### Problem Statement（問題陳述）
業務場景：非技術成員（如家人）上傳影音並貼連結，但無法理解 mms 與 http 的差異，導致操作負擔與錯誤。
技術挑戰：確保編輯人員只需按原本流程發佈檔案，不需學新知識。
影響範圍：訓練成本、出錯率、上線速度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 協定概念複雜。
2. 人工判斷易出錯。
3. 沒有自動化轉換機制。
深層原因：
- 架構層面：缺乏中介層抽象協定。
- 技術層面：未使用 Handler 自動處理。
- 流程層面：缺少“只管放檔”的簡化規範。

### Solution Design（解決方案設計）
解決策略：以 Handler 隱藏協定細節，編輯者照常上傳與貼 http 連結即可。必要時在 CMS 發表介面做提示，但不要求協定知識。

實施步驟：
1. 導入 Handler（同 Case #1）
- 實作細節：副檔名綁定。
- 所需資源：ASP.NET。
- 預估時間：0.5 小時。

2. 文件化簡易發佈規範
- 實作細節：一頁說明「只需貼 http://」。
- 所需資源：團隊 Wiki。
- 預估時間：0.5 小時。

關鍵程式碼/設定：同 Case #1（略）

實際案例：作者以 Handler 達到「放在 web 下的檔案會自動轉到 media service」。
實作環境：ASP.NET。
實測數據：
改善前：需教學與記憶規則。
改善後：零教育成本，錯誤顯著下降。
改善幅度：流程效率提升（定性）。

Learning Points（學習要點）
核心知識點：
- 以技術抽象降低人為錯誤
- 無侵入式整合

技能要求：
必備技能：基本配置。
進階技能：撰寫簡明操作指南。

延伸思考：
可再加入自動檢核（上傳副檔名提示）。

Practice Exercise（練習題）
基礎練習：撰寫 1 頁發佈規範（30 分鐘）
進階練習：在 CMS 介面做自動提示（2 小時）
專案練習：實作連結校驗插件（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：編輯流程無改動即可使用
程式碼品質（30%）：設定簡潔
效能優化（20%）：流程順暢
創新性（10%）：人因工程優化

---

## Case #6: 靜態目錄轉 RSS 訂閱（RssMonitorHttpHandler）

### Problem Statement（問題陳述）
業務場景：想知道某目錄新增了哪些檔案，但人工按時間排序易忘記上次看到哪裡。希望像 Blog 一樣訂閱目錄更新。
技術挑戰：針對純靜態 *.html 網站，如何無需改檔案內容就提供 RSS。
影響範圍：內容可發現性、用戶回訪率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態網站無內建 RSS。
2. 使用者無法自動收到更新通知。
3. 缺少將檔案系統變動轉換成 feed 的橋接層。
深層原因：
- 架構層面：內容層與訂閱層未打通。
- 技術層面：未生成 RSS XML。
- 流程層面：未建立自動化更新通知流程。

### Solution Design（解決方案設計）
解決策略：以 HttpHandler 掃描指定目錄，將每個檔案映射為 RSS item（標題=檔名、日期=最後寫入時間、link=檔案 URL），輸出 RSS 2.0。

實施步驟：
1. Handler 實作：列檔、排序、輸出 RSS
- 實作細節：Directory.GetFiles + File.GetLastWriteTime，輸出 XML。
- 所需資源：ASP.NET。
- 預估時間：2 小時。

2. 綁定路由與目錄參數
- 實作細節：支援 /rss?dir=/files/baby 之類參數。
- 所需資源：QueryString 解析。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
public class RssMonitorHttpHandler : IHttpHandler
{
    public bool IsReusable => true;

    public void ProcessRequest(HttpContext ctx)
    {
        var dir = ctx.Request["dir"] ?? "~/files"; // 目錄參數
        var physical = ctx.Server.MapPath(dir);
        var files = Directory.GetFiles(physical, "*.html", SearchOption.TopDirectoryOnly)
            .Select(p => new FileInfo(p))
            .OrderByDescending(f => f.LastWriteTime)
            .Take(20)
            .ToList();

        ctx.Response.ContentType = "application/rss+xml; charset=utf-8";
        var site = ctx.Request.Url.GetLeftPart(UriPartial.Authority);
        using (var w = new System.IO.StreamWriter(ctx.Response.OutputStream, System.Text.Encoding.UTF8))
        {
            w.WriteLine("<?xml version='1.0' encoding='utf-8'?>");
            w.WriteLine("<rss version='2.0'><channel>");
            w.WriteLine($"<title>Directory feed: {dir}</title>");
            w.WriteLine($"<link>{site}{VirtualPathUtility.ToAbsolute(dir)}</link>");
            w.WriteLine("<description>Auto-generated from static files</description>");
            foreach (var f in files)
            {
                var url = site + VirtualPathUtility.ToAbsolute(Path.Combine(dir, f.Name));
                w.WriteLine("<item>");
                w.WriteLine($"<title>{HttpUtility.HtmlEncode(Path.GetFileNameWithoutExtension(f.Name))}</title>");
                w.WriteLine($"<link>{url}</link>");
                w.WriteLine($"<pubDate>{f.LastWriteTime.ToUniversalTime():r}</pubDate>");
                w.WriteLine("</item>");
            }
            w.WriteLine("</channel></rss>");
        }
    }
}
```

實際案例：文章提供 baby.rss 的示範，將靜態相簿/頁面變更以 RSS 方式通知。
實作環境：ASP.NET。
實測數據：
改善前：需要人工巡檢。
改善後：RSS Reader 自動通知。
改善幅度：可發現性明顯提升（定性）。

Learning Points（學習要點）
核心知識點：
- RSS 2.0 結構
- 檔案系統掃描與時間排序

技能要求：
必備技能：XML 組裝、I/O 操作。
進階技能：排序、分頁、限制數量。

延伸思考：
可加上 Atom 支援；注意目錄掃描成本與安全。

Practice Exercise（練習題）
基礎練習：為一個目錄輸出最近 10 筆 RSS（30 分鐘）
進階練習：支援子目錄遞迴與型別篩選（2 小時）
專案練習：打造可設定的 RSS 監控中心頁面（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：RSS 在 Reader 可正常訂閱
程式碼品質（30%）：I/O 處理與錯誤防護
效能優化（20%）：掃描與排序效率
創新性（10%）：自訂欄位與模板化

---

## Case #7: 最近更新排序與項目數限制（RSS 可讀性優化）

### Problem Statement（問題陳述）
業務場景：目錄檔案眾多，若全部納入 RSS 會造成雜訊與 Reader 負擔。需提供最近更新排序與最大項目數限制。
技術挑戰：在不引入資料庫的前提下，高效排序與截斷。
影響範圍：RSS 可用性、讀者體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未限制項目數導致 RSS 過長。
2. 無排序造成資訊未聚焦。
3. Reader 解析效能下降。
深層原因：
- 架構層面：缺少輸出策略。
- 技術層面：未做 Take(N) 與排序。
- 流程層面：未定義合理的 feed 大小。

### Solution Design（解決方案設計）
解決策略：依 LastWriteTime 遞減排序，預設輸出 top 20，支援 ?top= 參數覆寫但限制上限（例如 100）。

實施步驟：
1. 增加 ?top= 參數解析
- 實作細節：TryParse 並限制 1..100。
- 所需資源：ASP.NET。
- 預估時間：0.5 小時。

2. 排序與截斷
- 實作細節：OrderByDescending + Take(top)。
- 所需資源：LINQ。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
int top = 20;
int.TryParse(ctx.Request["top"], out var t);
if (t >= 1 && t <= 100) top = t;
var files = Directory.GetFiles(physical, pattern)
    .Select(p => new FileInfo(p))
    .OrderByDescending(f => f.LastWriteTime)
    .Take(top)
    .ToList();
```

實際案例：文章提及「新增檔案就像 blog 新貼文章」，本案例確保輸出聚焦於最新項目。
實作環境：ASP.NET。
實測數據：
改善前：feed 過長，讀者負擔高。
改善後：聚焦最新，讀者體驗提升。
改善幅度：可讀性提升（定性）。

Learning Points（學習要點）
核心知識點：
- 以檔案系統時間模擬發文時間
- 請求參數與安全上限

技能要求：
必備技能：LINQ 排序、參數驗證。
進階技能：流量與 Reader 友善度考量。

延伸思考：
加入分頁與歷史存取入口。

Practice Exercise（練習題）
基礎練習：加入 ?top=（30 分鐘）
進階練習：支援 ?page= 分頁（2 小時）
專案練習：加上快取與 ETag（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：排序與限制可用
程式碼品質（30%）：參數安全
效能優化（20%）：I/O 減少
創新性（10%）：分頁與導航

---

## Case #8: 檔案型別過濾（只發佈 .html/.htm）

### Problem Statement（問題陳述）
業務場景：目錄中可能有圖片、腳本等非內容頁。RSS 若全數包含會降低價值。需支援副檔名白名單。
技術挑戰：彈性設定可發佈型別，避免硬編碼。
影響範圍：RSS 品質、訂閱者體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 非內容檔混雜。
2. 無白名單管理。
3. 手動過濾不可行。
深層原因：
- 架構層面：缺乏可配置的過濾層。
- 技術層面：未建立副檔名白名單。
- 流程層面：沒有分類規範。

### Solution Design（解決方案設計）
解決策略：以配置提供可發佈型別，如 .html;.htm；Handler 依清單過濾。

實施步驟：
1. 新增配置項 allowedExtensions
- 實作細節：分號分隔，轉成 HashSet。
- 所需資源：web.config。
- 預估時間：0.5 小時。

2. 應用於掃描流程
- 實作細節：依副檔名判斷是否納入。
- 所需資源：ASP.NET。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
var allowed = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
  { ".html", ".htm" };
// ... files.Where(f => allowed.Contains(f.Extension))
```

實際案例：文章點名「全都是 *.html 的靜態網頁」，白名單確保聚焦內容頁。
實作環境：ASP.NET。
實測數據：—（以質化描述為主）

Learning Points（學習要點）
核心知識點：
- 白名單過濾
- web.config 配置化

技能要求：
必備技能：字串處理。
進階技能：環境化配置。

延伸思考：
支援黑名單與路徑過濾。

Practice Exercise（練習題）
基礎練習：加入白名單（30 分鐘）
進階練習：支援多目錄不同白名單（2 小時）
專案練習：圖形化配置管理頁（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：過濾生效
程式碼品質（30%）：配置易讀
效能優化（20%）：過濾高效
創新性（10%）：可視化管理

---

## Case #9: RSS 標題與描述自訂（靜態站點品牌化）

### Problem Statement（問題陳述）
業務場景：為特定目錄（如小皮的相簿）提供具品牌化的 RSS 標題、描述與連結，提升可讀性與辨識度。
技術挑戰：在 Handler 層支援可選參數或配置覆寫標題與描述。
影響範圍：訂閱體驗、品牌識別。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設標題/描述過於制式。
2. 靜態站缺少 CMS 可設定功能。
3. 無法快速針對不同目錄自訂。
深層原因：
- 架構層面：缺少模板層。
- 技術層面：未支援參數化輸出。
- 流程層面：無配置入口。

### Solution Design（解決方案設計）
解決策略：支援 ?title=&desc=&link= 三參數，若未提供則採預設，或以 web.config 針對目錄設 profile。

實施步驟：
1. QueryString 覆寫
- 實作細節：容忍空值、長度限制。
- 所需資源：ASP.NET。
- 預估時間：0.5 小時。

2. 配置檔映射
- 實作細節：dir→(title,desc,link) 對應。
- 所需資源：web.config。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
string title = ctx.Request["title"] ?? $"Directory feed: {dir}";
string desc  = ctx.Request["desc"]  ?? "Auto-generated from static files";
string link  = ctx.Request["link"]  ?? site + VirtualPathUtility.ToAbsolute(dir);
// 寫入 channel 節點
```

實際案例：文章示範 baby.rss，可對應「小皮的網頁」命名。
實作環境：ASP.NET。
實測數據：—（定性）

Learning Points（學習要點）
核心知識點：
- 可參數化的輸出模板
- 使用者導向的資訊設計

技能要求：
必備技能：QueryString 處理。
進階技能：多目錄配置管理。

延伸思考：
可加入語言/地區參數，多語系 feed。

Practice Exercise（練習題）
基礎練習：支援 title/desc 覆寫（30 分鐘）
進階練習：基於目錄的預設配置（2 小時）
專案練習：建立 UI 管理多目錄描述（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：參數覆寫生效
程式碼品質（30%）：引數驗證
效能優化（20%）：無額外負擔
創新性（10%）：模板化方案

---

## Case #10: RSS 的條件式 GET（ETag/Last-Modified）

### Problem Statement（問題陳述）
業務場景：RSS Reader 會定期輪詢，若每次都輸出完整 feed 將浪費小站資源。需支援 304 Not Modified。
技術挑戰：在檔案系統為資料源的情況，計算合適的 Last-Modified 與 ETag。
影響範圍：伺服器負載、頻寬成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 重複傳輸未變更內容。
2. 未實作協商快取。
3. Reader 輪詢頻繁。
深層原因：
- 架構層面：無快取層設計。
- 技術層面：未產生 304。
- 流程層面：未衡量輪詢成本。

### Solution Design（解決方案設計）
解決策略：以目錄中檔案最大 LastWriteTime 作為 feed 的 Last-Modified；以「最大時間戳+項目數」生成 ETag。若 If-Modified-Since/If-None-Match 命中則回 304。

實施步驟：
1. 計算時間戳與 ETag
- 實作細節：maxTime = files.Max(f=>f.LastWriteTimeUtc)；ETag = 哈希。
- 所需資源：ASP.NET。
- 預估時間：1 小時。

2. 產生 304 回應
- 實作細節：比對請求標頭，短路回應。
- 所需資源：HTTP 基礎。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
var maxUtc = files.Any() ? files.Max(f => f.LastWriteTimeUtc) : DateTime.MinValue;
var etag = "\"" + maxUtc.Ticks.ToString("X") + "-" + files.Count + "\"";
var req = ctx.Request;

ctx.Response.Cache.SetETag(etag);
ctx.Response.Cache.SetLastModified(maxUtc);

bool notModified = (req.Headers["If-None-Match"] == etag) ||
                   DateTime.TryParse(req.Headers["If-Modified-Since"], out var ims) && ims.ToUniversalTime() >= maxUtc;
if (notModified)
{
    ctx.Response.StatusCode = 304;
    ctx.Response.End();
    return;
}
```

實際案例：文章要求 RSS Reader 通知更新，本方案降低輪詢成本。
實作環境：ASP.NET。
實測數據：
改善前：每次輪詢皆全量傳輸。
改善後：未變更返回 304。
改善幅度：頻寬與 CPU 降低（定性）。

Learning Points（學習要點）
核心知識點：
- HTTP 協商快取
- 檔案系統→HTTP 時間戳對映

技能要求：
必備技能：HTTP 標頭與狀態碼。
進階技能：快取策略設計。

延伸思考：
可加入伺服端快取與輸出緩存。

Practice Exercise（練習題）
基礎練習：加入 Last-Modified（30 分鐘）
進階練習：加入 ETag 與 304 回應（2 小時）
專案練習：統計節省的流量（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：304 正確運作
程式碼品質（30%）：時間處理嚴謹
效能優化（20%）：輪詢負擔降低
創新性（10%）：多層快取

---

## Case #11: ZIP 當虛擬目錄（清單瀏覽頁）

### Problem Statement（問題陳述）
業務場景：相簿網頁常同時提供在線瀏覽與 ZIP 下載，導致同一份內容維護兩套。希望只放 ZIP，又可像目錄一樣瀏覽。
技術挑戰：讓 /path/foo.zip 以瀏覽頁形式顯示 ZIP 內容清單。
影響範圍：維護成本、使用體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 同內容放兩份，易不一致。
2. 缺乏 ZIP 虛擬化層。
3. 使用者需下載才看內容。
深層原因：
- 架構層面：存取層未抽象壓縮容器。
- 技術層面：未解析 ZIP 目錄結構。
- 流程層面：重複發佈。

### Solution Design（解決方案設計）
解決策略：以 HttpHandler 解析 ZIP，輸出清單為 HTML（或 JSON），使 /foo.zip 變成可瀏覽的目錄視圖。

實施步驟：
1. ZIP 讀取與列舉
- 實作細節：使用 SharpZipLib 讀取 entries，忽略目錄項，按名稱/路徑呈現。
- 所需資源：ICSharpCode.SharpZipLib。
- 預估時間：2 小時。

2. 清單頁輸出
- 實作細節：生成連結至 /foo.zip/{entryPath}。
- 所需資源：ASP.NET。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// ZipVirtualFolderHttpHandler.cs (清單輸出節選)
using ICSharpCode.SharpZipLib.Zip;

void ListZip(HttpContext ctx, string zipPathVirtual)
{
    var physical = ctx.Server.MapPath(zipPathVirtual);
    using var zf = new ZipFile(physical);
    ctx.Response.ContentType = "text/html; charset=utf-8";
    ctx.Response.Write("<ul>");
    foreach (ZipEntry e in zf)
    {
        if (!e.IsFile) continue;
        var link = zipPathVirtual + "/" + e.Name; // /files/chicken/slide.zip/default.htm
        ctx.Response.Write($"<li><a href='{link}'>{HttpUtility.HtmlEncode(e.Name)}</a></li>");
    }
    ctx.Response.Write("</ul>");
}
```

實際案例：文章提供 /files/chicken/slide.zip 可直接看到內容清單。
實作環境：ASP.NET + SharpZipLib。
實測數據：—（定性）

Learning Points（學習要點）
核心知識點：
- ZIP 目錄結構解析
- 虛擬路徑設計

技能要求：
必備技能：第三方壓縮庫使用。
進階技能：清單視圖設計與排序。

延伸思考：
可輸出 JSON 用前端渲染；注意安全與路徑處理。

Practice Exercise（練習題）
基礎練習：列出 ZIP 內容（30 分鐘）
進階練習：按照路徑分層顯示（2 小時）
專案練習：加入搜尋與篩選（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能列出全部檔案
程式碼品質（30%）：路徑處理健全
效能優化（20%）：只讀必要資訊
創新性（10%）：多格式輸出

---

## Case #12: 直接連到 ZIP 內檔案（/zip/file 路徑映射）

### Problem Statement（問題陳述）
業務場景：用戶想直接打開 ZIP 中的 default.htm 等頁面，不需整包下載。URL 如 /files/chicken/slide.zip/default.htm。
技術挑戰：解析 .zip 之後的子路徑，按需串流對應 entry。
影響範圍：使用體驗、伺服器資源。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 傳統 HTTP 無法直訪壓縮內檔。
2. 需即時解壓對應 entry。
3. 需正確回應 MIME。
深層原因：
- 架構層面：URL 路徑與 ZIP 內路徑未對應。
- 技術層面：即時串流解壓。
- 流程層面：維運無需多份內容。

### Solution Design（解決方案設計）
解決策略：Handler 識別 URL 中 .zip 的位置，將後綴視為 ZIP entry 路徑，以流方式讀取並回應正確 Content-Type。

實施步驟：
1. 解析 URL
- 實作細節：找到 ".zip" 索引，分割 zipPath 與 entryPath。
- 所需資源：ASP.NET。
- 預估時間：0.5 小時。

2. 對應 MIME 並串流
- 實作細節：依副檔名回應 Content-Type，避免大檔全部載入記憶體。
- 所需資源：SharpZipLib。
- 預估時間：1.5 小時。

關鍵程式碼/設定：
```csharp
void ServeZipEntry(HttpContext ctx, string fullVirtualPath)
{
    var idx = fullVirtualPath.IndexOf(".zip", StringComparison.OrdinalIgnoreCase);
    var zipVPath = fullVirtualPath.Substring(0, idx + 4);
    var entryPath = fullVirtualPath.Substring(idx + 5); // 之後的 /entry

    using var zf = new ICSharpCode.SharpZipLib.Zip.ZipFile(ctx.Server.MapPath(zipVPath));
    var ze = zf.GetEntry(entryPath.Replace('\\','/'));
    if (ze == null || !ze.IsFile) { ctx.Response.StatusCode = 404; return; }

    ctx.Response.ContentType = MimeMapping.GetMimeMapping(entryPath);
    using var s = zf.GetInputStream(ze);
    s.CopyTo(ctx.Response.OutputStream); // 串流輸出
}
```

實際案例：文章示範 /files/chicken/slide.zip/default.htm 直接開啟 ZIP 內頁面。
實作環境：ASP.NET + SharpZipLib。
實測數據：—（定性）

Learning Points（學習要點）
核心知識點：
- URL 路徑重寫與解析
- 串流輸出與 MIME 對映

技能要求：
必備技能：字串處理、串流 API。
進階技能：錯誤與安全防護。

延伸思考：
可加入 Range 支援；注意 Zip Slip 攻擊防護。

Practice Exercise（練習題）
基礎練習：支援 /zip/entry 路徑（30 分鐘）
進階練習：加入 Content-Type 對映（2 小時）
專案練習：實作 Range/斷點續傳（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可直連 entry
程式碼品質（30%）：錯誤處理
效能優化（20%）：串流無多餘緩存
創新性（10%）：Range 支援

---

## Case #13: ZIP 整包下載（?download 參數）

### Problem Statement（問題陳述）
業務場景：除了線上瀏覽，有些用戶仍偏好整包下載備份。希望同一 URL 加 ?download 可觸發直接下載。
技術挑戰：在清單/直連模式與整包下載之間切換，且設定正確的 Content-Disposition。
影響範圍：用戶選擇權、下載體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 不同用戶需求差異。
2. 需要同一資源支援不同語義。
3. 缺少下載語義切換。
深層原因：
- 架構層面：資源多模式呈現。
- 技術層面：HTTP 標頭控制。
- 流程層面：單一來源多用途。

### Solution Design（解決方案設計）
解決策略：若 QueryString 含 download，則 Response.TransmitFile 或 WriteFile 直傳 ZIP，並設定附件下載標頭；否則維持清單或 entry 模式。

實施步驟：
1. 參數解析
- 實作細節：bool download = !string.IsNullOrEmpty(Request["download"])
- 所需資源：ASP.NET。
- 預估時間：0.2 小時。

2. 下載回應
- 實作細節：Content-Type=application/zip；Content-Disposition=attachment。
- 所需資源：IIS/ASP.NET。
- 預估時間：0.3 小時。

關鍵程式碼/設定：
```csharp
if (!string.IsNullOrEmpty(ctx.Request["download"]))
{
    var physical = ctx.Server.MapPath(zipVPath);
    ctx.Response.ContentType = "application/zip";
    ctx.Response.AddHeader("Content-Disposition", $"attachment; filename=\"{Path.GetFileName(physical)}\"");
    ctx.Response.TransmitFile(physical);
    return;
}
```

實際案例：文章示範 /files/chicken/slide.zip?download 為普通 zip 檔下載。
實作環境：ASP.NET。
實測數據：—（定性）

Learning Points（學習要點）
核心知識點：
- Content-Disposition 與檔名處理
- 同資源多語義

技能要求：
必備技能：HTTP 標頭。
進階技能：防止檔名亂碼（RFC5987）。

延伸思考：
可加入壓縮等級與臨時打包。

Practice Exercise（練習題）
基礎練習：支援 ?download（30 分鐘）
進階練習：跨瀏覽器檔名相容（2 小時）
專案練習：打包多 ZIP 為單一下載（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能正確下載
程式碼品質（30%）：標頭處理嚴謹
效能優化（20%）：TransmitFile 使用
創新性（10%）：動態打包

---

## Case #14: ZIP 串流抽取與記憶體控制（大檔最佳化）

### Problem Statement（問題陳述）
業務場景：ZIP 內檔案可能很大（影像、影片），若一次載入記憶體會造成壓力。需以串流管線輸出，控制記憶體佔用。
技術挑戰：邊讀邊寫、適當的緩衝區大小、避免 Server GC 壓力。
影響範圍：伺服器可用性、併發能力。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 一次性讀取造成高峰記憶體。
2. 並發時容易 OOM。
3. 未設計串流管線。
深層原因：
- 架構層面：IO 模式選擇不當。
- 技術層面：未採用 Stream-to-Stream。
- 流程層面：缺少大檔測試。

### Solution Design（解決方案設計）
解決策略：使用 ZipEntry InputStream.CopyTo(Response.OutputStream) 或手動緩衝區讀寫，禁用 Response.BufferOutput，設定合適的快取頭。

實施步驟：
1. 關閉輸出緩衝與 chunked
- 實作細節：Response.BufferOutput=false。
- 所需資源：ASP.NET。
- 預估時間：0.2 小時。

2. 串流複製
- 實作細節：使用 CopyTo 或 64KB buffer 手動寫入。
- 所需資源：SharpZipLib。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
ctx.Response.BufferOutput = false;
using var s = zf.GetInputStream(ze);
byte[] buf = new byte[64 * 1024];
int read;
while ((read = s.Read(buf, 0, buf.Length)) > 0)
{
    ctx.Response.OutputStream.Write(buf, 0, read);
    ctx.Response.Flush(); // 謹慎使用，視環境調整
}
```

實際案例：文章所述以 ZIP 作為來源，線上預覽時需避免大檔壓力。
實作環境：ASP.NET + SharpZipLib。
實測數據：—（定性）

Learning Points（學習要點）
核心知識點：
- 串流 IO 最佳化
- Response 緩衝策略

技能要求：
必備技能：Stream API。
進階技能：壓力測試與監控。

延伸思考：
可加入 Range 支援與下載斷點續傳。

Practice Exercise（練習題）
基礎練習：導入 64KB 緩衝串流（30 分鐘）
進階練習：壓測並調整緩衝大小（2 小時）
專案練習：加入 Range/ETag 支援（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：大檔穩定串流
程式碼品質（30%）：IO 錯誤處理
效能優化（20%）：記憶體佔用合理
創新性（10%）：續傳與分段

---

## Case #15: 單一來源維護（ZIP 即內容來源）

### Problem Statement（問題陳述）
業務場景：相簿網頁同時維護「線上頁面」與「ZIP 下載」兩份，更新麻煩且容易不同步。希望只維護 ZIP。
技術挑戰：確保 ZIP 即可提供線上瀏覽與下載兩種體驗。
影響範圍：維護成本、一致性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 雙份內容易失同步。
2. 維護時間成本高。
3. 發佈流程繁瑣。
深層原因：
- 架構層面：未建立單一來源原則（SSOT）。
- 技術層面：缺少 ZIP 虛擬化。
- 流程層面：重複步驟無需存在。

### Solution Design（解決方案設計）
解決策略：結合 Case #11~#13，ZIP 既是可瀏覽的虛擬目錄，也是可直接下載的容器。維護只需更新 ZIP。

實施步驟：
1. 規範化發佈：僅上傳 ZIP
- 實作細節：文件化流程。
- 所需資源：Wiki。
- 預估時間：0.5 小時。

2. 整合三模式
- 實作細節：/zip → 清單、/zip/file → 直連、/zip?download → 整包。
- 所需資源：Handler。
- 預估時間：1 小時。

關鍵程式碼/設定：沿用前述三案（略）

實際案例：文章提出「只要擺個 zip 檔到網站上就可以」達成 SSOT。
實作環境：ASP.NET。
實測數據：
改善前：雙份維護、易失同步。
改善後：單一 ZIP，零重工。
改善幅度：維運效率顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- 單一事實來源（SSOT）
- 模式組合設計

技能要求：
必備技能：Handler 整合。
進階技能：變更管理。

延伸思考：
加入校驗 ZIP 完整性與簽章。

Practice Exercise（練習題）
基礎練習：撰寫 SSOT 發佈 SOP（30 分鐘）
進階練習：工具化 ZIP 上傳與驗證（2 小時）
專案練習：自動化部署 ZIP（8 時間）

Assessment Criteria（評估標準）
功能完整性（40%）：三模式皆可用
程式碼品質（30%）：邏輯清楚
效能優化（20%）：流程無冗餘
創新性（10%）：自動化工具

---

## Case #16: 三個 HttpHandler 的整合部署（最小侵入）

### Problem Statement（問題陳述）
業務場景：需要同時導入 MediaService、RssMonitor、ZipVirtualFolder 三個 Handler 到既有 ASP.NET 網站，盡量不改現有頁面與流程。
技術挑戰：正確的路由規則、避免互相干擾、清晰的配置與文件化。
影響範圍：部署風險、維護性、可觀測性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多 Handler 共存需避免路徑衝突。
2. 需確認優先順序。
3. 缺乏部署說明。
深層原因：
- 架構層面：路由規則設計不完善。
- 技術層面：IIS 管線與處理順序理解不足。
- 流程層面：缺乏標準化部署指南。

### Solution Design（解決方案設計）
解決策略：在 web.config 以明確的 path 綁定與副檔名綁定，撰寫部署與回滾指南；加入基本健康檢查端點與日誌。

實施步驟：
1. web.config 整合
- 實作細節：Media 綁定副檔名、Rss 綁定特定路徑（/rss.ashx 或 /rss/*）、Zip 綁定 *.zip。
- 所需資源：IIS/ASP.NET。
- 預估時間：1 小時。

2. 驗證與文件化
- 實作細節：測試全部案例 URL；撰寫 README。
- 所需資源：團隊 Wiki。
- 預估時間：1 小時。

關鍵程式碼/設定：
```xml
<configuration>
  <system.webServer>
    <handlers>
      <!-- Media -->
      <add name="MediaHandlerWmv" path="*.wmv" verb="GET" type="MediaServiceHttpHandler" />
      <add name="MediaHandlerWma" path="*.wma" verb="GET" type="MediaServiceHttpHandler" />
      <add name="MediaHandlerAsf" path="*.asf" verb="GET" type="MediaServiceHttpHandler" />
      <!-- RSS -->
      <add name="RssMonitor" path="rss.ashx" verb="GET" type="RssMonitorHttpHandler" />
      <!-- ZIP -->
      <add name="ZipVirtualFolder" path="*.zip*" verb="GET" type="ZipVirtualFolderHttpHandler" />
    </handlers>
  </system.webServer>
</configuration>
```

實際案例：文章結尾提供 ChickenHouse.Web.zip，表示三個 Handler 可打包整合。
實作環境：ASP.NET/IIS。
實測數據：—（定性）

Learning Points（學習要點）
核心知識點：
- IIS 管線與 Handler 綁定策略
- 路由優先級與通配符

技能要求：
必備技能：web.config 維護。
進階技能：藍綠部署與回滾。

延伸思考：
可加入健康檢查與監控告警。

Practice Exercise（練習題）
基礎練習：整合三 Handler 至測試站（30 分鐘）
進階練習：寫部署與回滾指南（2 小時）
專案練習：自動化部署（Web Deploy/CI）（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：三 Handler 均正常
程式碼品質（30%）：配置清晰無衝突
效能優化（20%）：處理順序合理
創新性（10%）：自動化與監控

--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case 2（統一 URL 映射）
  - Case 5（流程簡化）
  - Case 7（排序與限制）
  - Case 8（型別過濾）
  - Case 13（ZIP 下載）
- 中級（需要一定基礎）
  - Case 1（ASX 轉發）
  - Case 3（相容性回退）
  - Case 4（頻寬保護）
  - Case 6（靜態目錄 RSS）
  - Case 9（RSS 自訂）
  - Case 10（條件式 GET）
  - Case 11（ZIP 清單）
  - Case 12（ZIP 直連）
  - Case 14（ZIP 串流最佳化）
  - Case 16（整合部署）
- 高級（需要深厚經驗）
  - Case 15（SSOT 與流程落地）

2. 按技術領域分類
- 架構設計類
  - Case 4, 5, 15, 16
- 效能優化類
  - Case 4, 10, 14
- 整合開發類
  - Case 1, 2, 3, 6, 7, 8, 9, 11, 12, 13, 16
- 除錯診斷類
  - Case 3, 10, 14
- 安全防護類
  -（本篇以功能為主，安全議題在延伸思考中提示）

3. 按學習目標分類
- 概念理解型
  - Case 4（卸載思維）、Case 15（SSOT）
- 技能練習型
  - Case 2, 7, 8, 9, 13
- 問題解決型
  - Case 1, 3, 6, 10, 11, 12, 14, 16
- 創新應用型
  - Case 5（人因優化）、Case 16（最小侵入整合）

--------------------------------
案例關聯圖（學習路徑建議）

- 入門起點（基礎 Handler 與參數化）
  1) Case 2（統一 URL 映射）→ 2) Case 5（流程簡化）
  3) Case 7（排序與限制）→ 4) Case 8（型別過濾）→ 5) Case 9（RSS 自訂）

- 影音串流路徑
  - 先學 Case 2 → Case 1（ASX 轉發）
  - 再進階 Case 3（相容性回退）
  - 補上效益驗證 Case 4（頻寬保護）
  - 完整度：與 Case 16（整合部署）收尾

- RSS 路徑
  - 先學 Case 7/8（輸出策略）→ Case 6（靜態目錄 RSS）
  - 加強 Case 9（品牌化）
  - 最後 Case 10（條件式 GET）

- ZIP 虛擬目錄路徑
  - 先學 Case 11（清單）→ Case 12（直連）→ Case 13（整包下載）
  - 強化 Case 14（串流最佳化）
  - 以 Case 15（SSOT）總結方法論

- 全站整合與部署
  - 所有路徑完成後，統一到 Case 16（整合部署），形成最小侵入的整體方案。

依賴關係摘要：
- Case 1 依賴 Case 2 的映射思維。
- Case 3 依賴 Case 1 的 ASX 產出能力。
- Case 6 依賴 Case 7/8 的輸出策略。
- Case 12/13 依賴 Case 11 的 ZIP 解析。
- Case 15 依賴 Case 11~13 的功能完備。
- Case 16 依賴所有單點功能成熟後的整合。

完整學習路徑建議：
- 第一階段：Case 2 → 5 → 7 → 8（建立 Handler 與輸出控制基本功）
- 第二階段（兩條並進）：
  - 影音：Case 1 → 3 → 4
  - RSS：Case 6 → 9 → 10
- 第三階段（ZIP）：Case 11 → 12 → 13 → 14 → 15
- 收斂整合：Case 16（部署、監控、回滾）
此路徑兼顧功能構建、效益驗證與流程優化，完成後可在既有 ASP.NET 網站快速導入三個高實用性的 HttpHandler 能力。