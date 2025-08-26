以下內容基於文章提到的遷移經驗與具體做法，整理出 16 個可教學、可實作、可評估的解決方案案例。每個案例均包含問題、根因、解法、步驟、程式碼與學習評估，便於用於實戰教學、專案練習與能力評估。

## Case #1: 以 ASHX 重寫匯入器，取代 BlogEngine WebService 匯入

### Problem Statement（問題陳述）
業務場景：從 CS2007 遷移至 BlogEngine.NET，先用「CS2007 → BlogML → BlogEngine」流程完成約 90% 的匯入，但仍有 10% 關鍵資料（如原始 CS PostID、PageViewCount）遺漏。官方 BlogEngine 的 BlogML Importer 以 WebService 單筆呼叫設計，拓展性不足且效率不佳，對資料完整性與後續轉址對照造成風險。
技術挑戰：WebService 端沒有 Source Code、不易擴充欄位；一篇文章/回應一個呼叫，對大量資料延遲高；BlogML 未囊括自訂欄位。
影響範圍：舊文無法完整還原、站內/站外轉址無從建立、計數與評論資料不完整。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 官方 BlogImporter WebMethod 介面缺欄位：缺少 CS PostID、PageViewCount 等，導致資料無法帶入。
2. 設計為單筆呼叫：每篇文章/留言一個 WebService 呼叫，效率差。
3. 過度依賴 BlogML：BlogML 不包含所有需要的自訂資料。
深層原因：
- 架構層面：匯入被綁定在遠端 WebService，擴充成本高。
- 技術層面：未直接使用 BlogEngine Core API 導入，限制可控性。
- 流程層面：先導方案以「能用」為目標，未建立可擴充的匯入策略。

### Solution Design（解決方案設計）
解決策略：改以站內 ASHX 處理器讀取 App_Data 中的 BlogML 檔，直接呼叫 BlogEngine.Core API 建立 Post/Comment，並在此流程中注入 CS PostID、計數等擴充欄位，同步建立「CS→BE」ID 對照表，以二階段完成內容與連結修正。

實施步驟：
1. 分析 WSDL 與現況缺口
- 實作細節：比對 BlogImporter.asmx 的 WebMethod 與所需欄位清單。
- 所需資源：瀏覽器、WSDL、需求清單。
- 預估時間：0.5 天

2. 建立 ASHX 匯入處理器
- 實作細節：讀檔、解析 BlogML、呼叫 BlogEngine.Core 建立 Post/Comment。
- 所需資源：BlogEngine.Core、XDocument/BlogML Parser。
- 預估時間：1.5 天

3. 擴充欄位併入與對照表保存
- 實作細節：CS PostID、PageViewCount 寫入自訂儲存；序列化對照表。
- 所需資源：App_Data 儲存、序列化工具（XML/JSON）。
- 預估時間：1 天

4. 測試與回歸
- 實作細節：以 200+ 篇資料全量測試，校驗計數與連結處理前置資料。
- 所需資源：測試清單、比對工具。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// App_Data/Importer.ashx (概念性範例)
public class BlogMlImporter : IHttpHandler
{
    public void ProcessRequest(HttpContext ctx)
    {
        string path = ctx.Server.MapPath("~/App_Data/export.blogml.xml");
        var xdoc = XDocument.Load(path);

        var map = new Dictionary<string, Guid>(); // csPostId -> beGuid
        foreach (var p in xdoc.Descendants("post"))
        {
            string csPostId = (string)p.Attribute("id");         // 來源的 CS PostID
            string title    = (string)p.Element("title");
            string content  = (string)p.Element("content");
            DateTime pub    = (DateTime)p.Element("date-created");

            var bePost = new BlogEngine.Core.Post();
            bePost.Title = title;
            bePost.Content = content;
            bePost.DateCreated = pub;
            // 後續額外欄位（如 ViewCount）在後續步驟或 CustomField 寫入
            bePost.Save();

            map[csPostId] = bePost.Id; // 記錄新舊對應
            // 迴圈處理 comments ...
        }
        // 對照表持久化
        File.WriteAllText(ctx.Server.MapPath("~/App_Data/cs-be-map.json"),
            System.Text.Json.JsonSerializer.Serialize(map));
        ctx.Response.Write("OK");
    }
}
```

實際案例：以站內 ASHX 匯入 BlogML + 自訂欄位，成功避開 WS 的欄位限制與呼叫成本；以兩層迴圈完成 90% 主匯入，後續再補 10% 自訂資料。
實作環境：ASP.NET（.NET 2.0/3.5 時代）、BlogEngine.NET、SQL Server 2005
實測數據：
改善前：匯入涵蓋率 ~90%，WS 單筆呼叫 O(n)
改善後：涵蓋率 ~100%，站內匯入 0 遠端呼叫
改善幅度：資料完整性 +10%，遠端呼叫 -100%

Learning Points（學習要點）
核心知識點：
- 以站內 Handler 直呼 Core API 可大幅提升可控性
- 匯入流程與擴充欄位應同時設計
- 匯入同時建立映射，為後續連結修正鋪路
技能要求：
- 必備技能：ASP.NET Handler、XML 解析、BlogEngine API
- 進階技能：序列化存取、可重入匯入流程設計
延伸思考：
- 可否批次/並行優化大規模匯入？
- 自訂欄位的資料模型長期維護風險？
- 匯入流程可否做成 CLI/CI 任務？
Practice Exercise（練習題）
- 基礎練習：撰寫最小 ASHX，讀取 BlogML 並建立一篇 Post
- 進階練習：匯入時記錄 CS→BE 對照表到 App_Data
- 專案練習：完成全量匯入（Post+Comments）與對照表保存
Assessment Criteria（評估標準）
- 功能完整性（40%）：可完整匯入 Post/Comment 並保存映射
- 程式碼品質（30%）：清楚的結構、錯誤處理與日誌
- 效能優化（20%）：避免重複 I/O、無遠端呼叫
- 創新性（10%）：可擴充欄位與流程可重入設計

---

## Case #2: 解析 CS2007 PropertyNames/PropertyValues 邏輯欄位

### Problem Statement（問題陳述）
業務場景：CS2007 將評論額外資訊（匿名作者、TitleUrl、IP…）序列化壓在兩個欄位：PropertyNames、PropertyValues，BlogML 未輸出，導致匯入 BlogEngine 時資料不完整。
技術挑戰：PropertyNames 是 Name:Type:Start:End 的連續定義；PropertyValues 是扁平大字串，須依位置擷取；無現成工具可直接解析。
影響範圍：匿名評論作者資訊遺失，影響資料完整性與後續資料分析。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. CS2007 採序列化扁平化欄位，失去結構化查詢能力。
2. BlogML 未包含自訂屬性。
3. 直接用 SQL/XPath 難以便利拆解字串與對應位置。
深層原因：
- 架構層面：資料模型為通用屬性袋（property bag），不利跨系統匯出。
- 技術層面：位置式序列化格式難讀、難測。
- 流程層面：未先建立屬性萃取的輔助工具或流程。

### Solution Design（解決方案設計）
解決策略：撰寫解析器，逐一讀取 PropertyNames 的 Token（Name/Type/Start/End），對 PropertyValues 進行子字串切割，組回鍵值對，提供匯入程序使用。

實施步驟：
1. 定義資料結構
- 實作細節：PropertyDefinition {Name, Type, Start, End}
- 所需資源：C# 類別
- 預估時間：0.5 天

2. 撰寫解析函式
- 實作細節：掃描 PropertyNames，逐組解析並從 PropertyValues 擷取
- 所需資源：C# 字串處理
- 預估時間：1 天

3. 整合匯入流程
- 實作細節：將解析結果注入 Comment 建立流程
- 所需資源：Case #1 匯入器
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public static IDictionary<string, string> ParseCsProperties(string propertyNames, string propertyValues)
{
    var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
    if (string.IsNullOrEmpty(propertyNames)) return result;

    // 格式: Name:Type:Start:End:Name:Type:Start:End:...
    var tokens = propertyNames.Split(new[] { ':' }, StringSplitOptions.RemoveEmptyEntries);
    for (int i = 0; i + 3 < tokens.Length; i += 4)
    {
        string name = tokens[i];
        string type = tokens[i + 1]; // 'S' for string, etc.
        int start = int.Parse(tokens[i + 2]);
        int end = int.Parse(tokens[i + 3]);

        int len = Math.Max(0, end - start);
        string val = start >= 0 && start + len <= propertyValues.Length
            ? propertyValues.Substring(start, len)
            : string.Empty;
        result[name] = val;
    }
    return result;
}
```

實際案例：成功解出匿名評論 SubmittedUserName 與 TitleUrl 等資訊，補足 BlogML 缺漏。
實作環境：.NET/C#
實測數據：
改善前：匿名評論無法還原作者與連結
改善後：匿名評論細節可完整匯入（覆蓋率 ~100%）
改善幅度：評論資料完整性顯著提升

Learning Points（學習要點）
核心知識點：
- 位置式序列化解析策略
- 容錯字串處理與邊界檢查
- 匯入前資料前處理的重要性
技能要求：
- 必備技能：C# 字串/集合操作
- 進階技能：單元測試驗證解析器
延伸思考：
- 是否轉存為結構化 XML/JSON 供後續流程重用？
- 類似屬性袋資料如何制定一致匯出規格？
Practice Exercise（練習題）
- 基礎：用提供的範例字串解析 SubmittedUserName、TitleUrl
- 進階：加入 Type 檢核與錯誤容錯
- 專案：將解析器整合至匯入流程，為每則評論補齊匿名資訊
Assessment Criteria（評估標準）
- 功能完整性（40%）：可正確解析多組屬性
- 程式碼品質（30%）：邊界處理、單元測試
- 效能優化（20%）：迴圈與 Substring 使用有效率
- 創新性（10%）：可重用的抽象化與擴充

---

## Case #3: 用 SQL Server 2005 FOR XML 將查詢結果一次倒成 XML

### Problem Statement（問題陳述）
業務場景：需要將 CS2007 中評論的 PropertyValues 等輔助資料匯出為 XML，供後續匯入程式解析使用。此工作只進行一次，希望避免額外開發時間。
技術挑戰：XML 匯出不希望再寫應用程式；要快速、可靠地把查詢結果變成 XML 檔。
影響範圍：若匯出成本高，會延宕整體匯入專案進度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 僅需一次性匯出，不值得寫大量程式。
2. 需用 XML 格式做後續處理。
3. 人力有限，匯出時間需最小化。
深層原因：
- 架構層面：缺乏資料抽取（Data Extraction）標準流程。
- 技術層面：未善用 DB 既有 XML 支援能力。
- 流程層面：臨時任務希望以最小代價完成。

### Solution Design（解決方案設計）
解決策略：在 SQL Server 2005 Management Studio 執行查詢，使用 FOR XML AUTO，直接把結果轉為 XML 顯示，手動加 Root 存檔。

實施步驟：
1. 撰寫查詢
- 實作細節：鎖定所需欄位（PostID、PostAuthor、PropertyNames、PropertyValues）
- 所需資源：SSMS
- 預估時間：0.5 天

2. 使用 FOR XML 輸出
- 實作細節：在結果窗點開 XML，加入根節點存檔
- 所需資源：SSMS
- 預估時間：0.5 天

關鍵程式碼/設定：
```sql
select 
    PostID, 
    PostAuthor, 
    PropertyNames, 
    PropertyValues 
from cs_posts 
where ApplicationPostType = 4 
for xml auto
```

實際案例：快速產生評論屬性 XML，後續由匯入器解析，第一階段資料準備完成。
實作環境：SQL Server 2005
實測數據：
改善前：需另寫匯出程式
改善後：0 行應用程式碼完成匯出
改善幅度：開發時間顯著縮短（以天計縮至小時）

Learning Points（學習要點）
核心知識點：
- SQL Server FOR XML 用途
- 善用 DB 工具取代一次性程式
- 匯出資料前的欄位取捨
技能要求：
- 必備技能：SQL 基礎
- 進階技能：XML 與 DB 整合
延伸思考：
- 大量資料是否需分批輸出？
- 是否需加入 XSD 或 Schema 驗證？
Practice Exercise（練習題）
- 基礎：用 FOR XML 將任意查詢輸出為 XML
- 進階：改用 FOR XML PATH 自訂節點名稱
- 專案：為匯入流程所需欄位製作 XML 匯出腳本
Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出 XML 可被下游程式消費
- 程式碼品質（30%）：查詢清楚、過濾正確
- 效能優化（20%）：查詢效率、索引使用
- 創新性（10%）：靈活運用各種 FOR XML 模式

---

## Case #4: 以正則表達式批次修補圖檔/附件連結為 BlogEngine Handler

### Problem Statement（問題陳述）
業務場景：CS2007 中的圖檔多為絕對路徑（WLW 產出），BlogEngine 以 image.axd/file.axd Handler 提供圖檔，需將內文中的舊連結批次替換。
技術挑戰：來源網址有多種主機與格式；單純文字替換容易誤傷；需避開內建路徑（如 rss.aspx）。
影響範圍：若替換錯誤將造成大量資源失連或誤導。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多種歷史網域與路徑存在（columns/community…）。
2. WLW 生成絕對路徑，與現行 Handler 機制不相容。
3. 單純字串取代會破壞其他連結。
深層原因：
- 架構層面：靜態資源服務機制變動（實檔→Handler）。
- 技術層面：缺少精確匹配與排除策略。
- 流程層面：缺少替換順序規劃與測試集。

### Solution Design（解決方案設計）
解決策略：設計能涵蓋多主機/路徑的 Regex，精確提取 /blogs/chicken/ 後段路徑，重寫為 image.axd?picture=…；配置替換順序避免誤傷，對特殊未涵蓋個案保留手動處理。

實施步驟：
1. 蒐集樣本網址與建立 Regex
- 實作細節：使用 regexlib.com 驗證匹配結果
- 所需資源：Regex 測試工具
- 預估時間：0.5 天

2. 批次替換與排除
- 實作細節：跳過 rss.aspx 等路徑；替換順序 1→2→3
- 所需資源：小工具程式/腳本
- 預估時間：1 天

3. 覆核與補救
- 實作細節：少數 case 手動修補
- 所需資源：比對報表
- 預估時間：0.5 天

關鍵程式碼/設定：
```regex
(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/([a-zA-Z0-9\-_\./%]*)
```
```csharp
string pattern = @"(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/([a-zA-Z0-9\-_\./%]*)";
var re = new Regex(pattern, RegexOptions.IgnoreCase);
content = re.Replace(content, m =>
{
    var rel = m.Groups[3].Value; // 相對於 /blogs/chicken/ 的路徑
    if (rel.EndsWith("rss.aspx", StringComparison.OrdinalIgnoreCase))
        return m.Value; // 排除
    return $"image.axd?picture={rel}";
});
```

實際案例：成功批次處理大多數圖檔連結；極少數歷史手工路徑採手動修補。
實作環境：.NET/C#
實測數據：
改善前：需手工逐篇修正或高風險全域替換
改善後：正確匹配批次替換，少量手動收尾
改善幅度：自動化覆蓋率達高比例（除少數古早手工路徑）

Learning Points（學習要點）
核心知識點：
- Regex 精確匹配與群組擷取
- 替換順序與排除名單的必要性
- Handler 化資源存取策略
技能要求：
- 必備技能：Regex、字串處理
- 進階技能：大量內容的安全替換策略
延伸思考：
- 可否於輸入層做統一 URL 正規化？
- 是否引入鏈接檢查器（Link Checker）驗證結果？
Practice Exercise（練習題）
- 基礎：寫 Regex 擷取 /blogs/chicken/ 後段
- 進階：加入排除條件（避開 rss.aspx）
- 專案：將替換工具整合入匯入後處理管線
Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確替換常見格式並排除內建路徑
- 程式碼品質（30%）：清楚的 Regex 與註解
- 效能優化（20%）：批次處理效率
- 創新性（10%）：可復用的小工具化

---

## Case #5: 以 Two-Pass 設計修正站內連結（新 ID 未知問題）

### Problem Statement（問題陳述）
業務場景：匯入 BlogEngine 時新文章 ID（GUID/Slug）要待建立後才知，內文中的站內連結需轉為新 URL，無法一次在匯入前完成。
技術挑戰：需要先知曉新 ID 才能替換；但替換材料來自匯入結果，形成先後依賴。
影響範圍：如果不處理，站內連結將失效或錯指。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. BlogEngine 使用 GUID/Slug，匯入前無法預知。
2. CS2007 有多種 URL 格式，需精準抓出舊 PostID。
3. 單次處理無法同時滿足建立與替換。
深層原因：
- 架構層面：ID 生成時機與內容替換耦合問題。
- 技術層面：Regex 抽取與映射資料依賴。
- 流程層面：缺少兩階段管線設計。

### Solution Design（解決方案設計）
解決策略：Two-Pass 管線：第一階段匯入並建立「CS PostID → BE GUID」映射；第二階段掃描內容用 Regex 擷取舊 PostID，據映射重寫為 /post.aspx?id=GUID 或依 API 生成 Slug URL。

實施步驟：
1. Pass 1 建立映射
- 實作細節：匯入 Post 後記錄 csId→beGuid
- 所需資源：App_Data 映射檔
- 預估時間：0.5 天

2. Pass 2 內容替換
- 實作細節：用 Regex 抓舊 ID，替換為新 URL
- 所需資源：Regex、替換腳本
- 預估時間：1 天

3. 驗證
- 實作細節：批次掃描替換後的連結有效性
- 所需資源：簡易 Link Check
- 預估時間：0.5 天

關鍵程式碼/設定：
```regex
(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/archive/\d+/\d+/\d+/(\d+)\.aspx
```
```csharp
var re = new Regex(pattern, RegexOptions.IgnoreCase);
content = re.Replace(content, m =>
{
    var csId = m.Groups[3].Value;
    if (map.TryGetValue(csId, out var beGuid))
        return $"/post.aspx?id={beGuid}";
    return m.Value; // 未匹配則保持
});
```

實際案例：Two-Pass 後，站內連結得以全部指向新站的正確文章網址。
實作環境：.NET/C#
實測數據：
改善前：無法一次性修正站內連結
改善後：以二階段完成 100% 正確替換（基於映射覆蓋範圍）
改善幅度：連結可用性從不確定 → 穩定

Learning Points（學習要點）
核心知識點：
- Two-Pass 管線化思維
- Regex 擷取與映射替代
- ID 生成與內容處理解耦
技能要求：
- 必備技能：Regex、字典映射
- 進階技能：內容管線化設計
延伸思考：
- 增量匯入如何維持映射一致性？
- 是否以 Slug 優先而非 GUID URL？
Practice Exercise（練習題）
- 基礎：實作替換函式將 CS URL 轉為 /post.aspx?id=GUID
- 進階：增加對 /blogs/1234.aspx 的支援
- 專案：完成 Two-Pass 全站替換與報表
Assessment Criteria（評估標準）
- 功能完整性（40%）：兩階段流程可重跑、可恢復
- 程式碼品質（30%）：乾淨、可測試
- 效能優化（20%）：批次替換效率
- 創新性（10%）：增量與錯誤回復機制

---

## Case #6: 建立 CSUrlMap HttpHandler 重新導向舊 CS URL

### Problem Statement（問題陳述）
業務場景：外部網站與搜尋引擎仍保存舊的 CS2007 文章網址，需在新站上承接並即時導向至對應 BlogEngine 文章，避免 404 與流量流失。
技術挑戰：舊網址模式多樣；需根據映射表快速找到新網址；要處理例外並提供友善訊息。
影響範圍：無法導向將造成 SEO 下降、使用者體驗不佳。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 網址格式分歧（archive/ID、archive/TitleHash、/blogs/1234.aspx）。
2. 需要即時匹配與查表。
3. 某些資源（rss.aspx）需特殊處理。
深層原因：
- 架構層面：網址策略變更後缺乏兼容層。
- 技術層面：正確匹配與高效查詢的需求。
- 流程層面：缺少持續維護的映射資料來源。

### Solution Design（解決方案設計）
解決策略：實作 HttpHandler（CSUrlMap），以 Regex 匹配舊 URL 擷取 CS PostID，查映射表得新 GUID，將 postID 與說明放入 context.Items，Server.Transfer 到統一頁面產生 301/302 或顯示訊息。

實施步驟：
1. 建立 Handler 與規則
- 實作細節：多個 Regex 覆蓋不同格式
- 所需資源：C#、Web.config 映射
- 預估時間：1 天

2. 載入映射
- 實作細節：App_Data 中 map.json / map.xml
- 所需資源：序列化工具
- 預估時間：0.5 天

3. 顯示與導向
- 實作細節：AutoRedirFromCsUrl.aspx 處理訊息與導向
- 所需資源：ASPX 頁
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public void ProcessRequest(HttpContext context)
{
    if (matchRss.IsMatch(context.Request.Path))
    {
        context.Response.ContentType = "text/xml";
        context.Response.TransmitFile("~/blogs/rss.xml");
    }
    else if (matchPostID.IsMatch(context.Request.Path))
    {
        Match result = matchPostID.Match(context.Request.Path);
        if (result != null && result.Groups.Count > 0)
        {
            string csPostID = result.Groups[result.Groups.Count - 1].Value;
            if (this.MAP.postIDs.ContainsKey(csPostID))
            {
                context.Items["postID"] = this.MAP.postIDs[csPostID];
                context.Items["redirDesc"] = "網站系統更新，原文章已經搬移到新的網址。";
            }
            else
            {
                context.Items["redirDesc"] = "查無此文章代碼，文章不存在或已刪除。";
            }
        }
    }
    else if (matchPostURL.IsMatch(context.Request.Path))
    {
        context.Items["postID"] = this.MAP.postURLs[context.Request.Path];
        context.Items["redirDesc"] = "網站系統更新，原文章已搬移。";
    }
    else
    {
        context.Items["redirDesc"] = "查無此頁。將返回網站首頁。";
    }
    context.Server.Transfer("~/blogs/AutoRedirFromCsUrl.aspx");
}
```

實際案例：舊 CS 文章連結點擊後能正確導到新站對應文章，RSS 特殊路徑也能正確回應。
實作環境：ASP.NET、BlogEngine.NET
實測數據：
改善前：外部舊連結大量 404
改善後：常見格式皆被導向至新頁面
改善幅度：舊連結可用性大幅提升

Learning Points（學習要點）
核心知識點：
- HttpHandler 在遷移兼容層的用途
- Regex 與映射檔聯動
- 轉址/轉呈策略（301/302/Transfer）
技能要求：
- 必備技能：ASP.NET Handler、Regex
- 進階技能：SEO 友好轉址策略
延伸思考：
- 直接回傳 301 是否優於 Server.Transfer？
- 映射檔熱更新與快取策略？
Practice Exercise（練習題）
- 基礎：匹配 /blogs/1234.aspx 並查表導向
- 進階：加入 archive/ID 格式支持
- 專案：完成全站舊連結導向與日誌紀錄
Assessment Criteria（評估標準）
- 功能完整性（40%）：涵蓋主要 URL 模式
- 程式碼品質（30%）：結構清楚、錯誤訊息友善
- 效能優化（20%）：快取映射與 Regex
- 創新性（10%）：SEO 最佳實踐

---

## Case #7: 處理 CS2007 多種 URL 模式的 PostID 擷取

### Problem Statement（問題陳述）
業務場景：CS2007 存在多種文章網址模式（archive/ID、archive/TitleHash、/blogs/1234.aspx），需準確擷取 PostID 用於映射與替換。
技術挑戰：各格式結構不同；需避免誤匹配；需易維護。
影響範圍：擷取失敗導致替換與導向失效。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 歷史遷移與設定造成多樣 URL。
2. 擷取規則分散、容易遺漏。
3. Regex 可讀性差，易誤用。
深層原因：
- 架構層面：URL Rewrite 規則過多。
- 技術層面：Regex 複雜、需單測與工具輔助。
- 流程層面：缺少白名單/黑名單策略。

### Solution Design（解決方案設計）
解決策略：為各主要模式設計專用 Regex，並以測試資料集驗證；將規則集中管理，並加入排除清單（如 rss.aspx）。

實施步驟：
1. 整理 URL 樣本
- 實作細節：列出三大模式與例外
- 所需資源：歷史資料
- 預估時間：0.5 天

2. 撰寫與測試 Regex
- 實作細節：逐一驗證群組擷取結果
- 所需資源：Regex 測試工具
- 預估時間：1 天

3. 集中管理與部署
- 實作細節：以常數/設定檔管理
- 所需資源：設定管理
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var reArchiveId = new Regex(@"/blogs/chicken/archive/\d+/\d+/\d+/(\d+)\.aspx", RegexOptions.IgnoreCase);
var reRootId    = new Regex(@"/blogs/(\d+)\.aspx", RegexOptions.IgnoreCase);
```

實際案例：對三大主要模式可穩定擷取 PostID，未涵蓋的古早手工路徑採人工修補。
實作環境：.NET/C#
實測數據：
改善前：擷取失敗頻繁
改善後：主要模式擷取成功率高（接近 100%）
改善幅度：連結修補與導向成功率顯著提升

Learning Points（學習要點）
核心知識點：
- 多 Regex 規則的策略化管理
- 測試驅動的 Regex 開發
- 例外排除（rss.aspx）
技能要求：
- 必備技能：Regex
- 進階技能：單元測試與測試資料集設計
延伸思考：
- 是否以路由表重建更可靠？
- 以狀態機取代複雜 Regex？
Practice Exercise（練習題）
- 基礎：寫出兩種模式的 Regex 並擷取 PostID
- 進階：加入對 TitleHash 模式的支援（若 PostID 可間接查得）
- 專案：建置 Regex 規則中心與單測
Assessment Criteria（評估標準）
- 功能完整性（40%）：涵蓋主模式
- 程式碼品質（30%）：規則可讀可維護
- 效能優化（20%）：Regex 效率
- 創新性（10%）：規則管理方式

---

## Case #8: 修正匯入後 Modified Date 錯誤的問題

### Problem Statement（問題陳述）
業務場景：官方 Importer 存在 Modified Date 錯誤（可能寫入 Now 或未正確帶入），導致文章時間軸與排序不正確。
技術挑戰：需從來源資料正確帶入並設定 BlogEngine 的修改時間欄位。
影響範圍：文章時間顯示錯誤、RSS 與排序異常。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Importer 未使用來源 Modified Date
2. BlogML 欄位對應未完整
3. 文章儲存流程未覆寫預設值
深層原因：
- 架構層面：匯入器對時間欄位缺少映射
- 技術層面：欄位對應疏漏
- 流程層面：測試覆蓋不足

### Solution Design（解決方案設計）
解決策略：在自訂匯入流程中，顯式設定 DateCreated 與 LastModified（或相對欄位）為 BlogML 中的對應值，避免系統預設時間覆蓋。

實施步驟：
1. 確認來源欄位
- 實作細節：讀 BlogML 的 date-created, date-modified
- 所需資源：BlogML 結構
- 預估時間：0.5 天

2. 匯入程式設定欄位
- 實作細節：Save 前寫入
- 所需資源：BlogEngine.Core
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
bePost.DateCreated = (DateTime)p.Element("date-created");
var mod = p.Element("date-modified");
if (mod != null)
{
    bePost.DateModified = (DateTime)mod;
}
bePost.Save();
```

實際案例：修改時間正確呈現，RSS/排序恢復正常。
實作環境：.NET/C#
實測數據：
改善前：修改時間錯誤
改善後：時間欄位正確
改善幅度：異常率 → 0（以測得樣本）

Learning Points（學習要點）
核心知識點：
- 時間欄位在內容系統的重要性
- Save 前欄位覆蓋策略
- 來源→目標欄位對映
技能要求：
- 必備技能：XML 欄位讀取
- 進階技能：欄位映射設計
延伸思考：
- 時區/UTC 處理策略？
- RSS/Feed 的 LastBuildDate 一致性？
Practice Exercise（練習題）
- 基礎：讀取並設定 DateCreated/DateModified
- 進階：加入時區換算
- 專案：為所有 Post 驗證/修補時間欄位
Assessment Criteria（評估標準）
- 功能完整性（40%）：欄位正確寫入
- 程式碼品質（30%）：清楚註解
- 效能優化（20%）：批次處理效率
- 創新性（10%）：時區/UTC 一致性策略

---

## Case #9: 匯入與保留每篇文章的瀏覽計數（Counter）

### Problem Statement（問題陳述）
業務場景：需保留 CS2007 的每篇文章瀏覽計數（Counter），BlogML 未包含；若不保留，既有熱門度與排序會失真。
技術挑戰：BlogEngine 是否有現成欄位可用不一定；需在不動核心資料表的前提下保存與顯示。
影響範圍：熱門文章排序、歷史數據分析。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. BlogML 無計數欄位
2. BlogEngine 現行模型未必提供可寫入的 ViewCount
3. 不宜直接修改核心 Schema
深層原因：
- 架構層面：跨系統數據模型不一致
- 技術層面：擴充資料的存放策略
- 流程層面：匯入與顯示層需同步改造

### Solution Design（解決方案設計）
解決策略：將 Counter 以外掛/側檔（App_Data JSON/XML）對映 Post.Id 保存；主題顯示時讀取對映補值；後續新的瀏覽計數可與舊值相加或另行累積。

實施步驟：
1. 匯出 Counter 與映射
- 實作細節：CS→BE 匯入時一併保存 PostId→Counter
- 所需資源：Case #1 映射流程
- 預估時間：0.5 天

2. 讀取與顯示
- 實作細節：加載對映於 Application 啟動或延遲載入，主題層讀取
- 所需資源：主題模板小改
- 預估時間：0.5 天

3. 後續累計策略
- 實作細節：新訪問計入臨時表/檔，再合併
- 所需資源：簡單計數器
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 讀取 Counter Map
var counters = JsonSerializer.Deserialize<Dictionary<Guid, int>>(
    File.ReadAllText(Server.MapPath("~/App_Data/counters.json")));

// 顯示層（概念）：在頁面上顯示舊值
int legacyViews = counters.TryGetValue(post.Id, out var v) ? v : 0;
```

實際案例：歷史瀏覽數在新站保留顯示，避免熱門度失真。
實作環境：.NET/C#
實測數據：
改善前：瀏覽數清零
改善後：保留歷史瀏覽數
改善幅度：資料完整性提升（熱門度不失真）

Learning Points（學習要點）
核心知識點：
- 側存策略與可逆轉
- 顯示層補值技巧
- 舊值與新計數合併
技能要求：
- 必備技能：序列化、讀檔
- 進階技能：應用啟動快取/快取失效
延伸思考：
- 日後是否遷入正式欄位？
- SEO/外掛對計數影響？
Practice Exercise（練習題）
- 基礎：從 JSON 讀取 PostId→Counter 並顯示
- 進階：合併新訪問計數
- 專案：設計可配置的 Counter 補值外掛
Assessment Criteria（評估標準）
- 功能完整性（40%）：正確顯示歷史計數
- 程式碼品質（30%）：簡潔與容錯
- 效能優化（20%）：快取與 I/O
- 創新性（10%）：合併策略

---

## Case #10: 以解析結果補齊評論的作者/網址/IP 等細節

### Problem Statement（問題陳述）
業務場景：匿名評論的作者資訊未出現在 BlogML，需在匯入時根據解析結果（Case #2）補齊到 BlogEngine 的 Comment。
技術挑戰：Comment 建立 API 需正確填入欄位；缺值處理；字元編碼。
影響範圍：評論可信度、文章互動歷史。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. BlogML 缺欄位
2. 解析器輸出需整合到 Comment 實體
3. 缺少欄位對映策略
深層原因：
- 架構層面：跨系統評論模型差異
- 技術層面：實體建立與驗證
- 流程層面：資料清洗與遺漏補值

### Solution Design（解決方案設計）
解決策略：在匯入每則 Comment 時，查詢解析器輸出的字典，填入 Author、Website、IP 等欄位，補齊資料。

實施步驟：
1. 整合解析器
- 實作細節：由 PostID/CommentID 對應解析資料
- 所需資源：Case #2 輸出
- 預估時間：0.5 天

2. 建立 Comment
- 實作細節：建立 Comment 物件，填欄位，附加至 Post
- 所需資源：BlogEngine.Core
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var props = ParseCsProperties(propertyNames, propertyValues);
var c = new BlogEngine.Core.Comment();
c.Author = props.TryGetValue("SubmittedUserName", out var name) ? name : "Anonymous";
c.Website = props.TryGetValue("TitleUrl", out var url) ? url : null;
c.IP = props.TryGetValue("IP", out var ip) ? ip : null;
c.Content = commentContent;
c.DateCreated = commentDate;
post.Comments.Add(c);
post.Save();
```

實際案例：匿名評論顯示作者與網站連結，完整還原互動。
實作環境：.NET/C#
實測數據：
改善前：匿名評論缺作者/網址
改善後：評論細節完整
改善幅度：評論資料完整性顯著提升

Learning Points（學習要點）
核心知識點：
- 實體組合與缺值策略
- 字元編碼與 HTML 安全
- 匯入順序（先 Post 後 Comment）
技能要求：
- 必備技能：C# 物件操作
- 進階技能：資料清洗
延伸思考：
- 是否記錄原始屬性原文以備查？
- 欄位映射改動的可維護性？
Practice Exercise（練習題）
- 基礎：為一則匿名評論補價作者與網址
- 進階：加入 IP 欄位與驗證
- 專案：完成全量評論補齊模組
Assessment Criteria（評估標準）
- 功能完整性（40%）：欄位完整寫入
- 程式碼品質（30%）：容錯與校驗
- 效能優化（20%）：批次處理效率
- 創新性（10%）：可配置欄位映射

---

## Case #11: 排除特定內建端點（如 rss.aspx）避免誤替換

### Problem Statement（問題陳述）
業務場景：批次替換圖檔與連結時，可能誤處理 /blogs/chicken/rss.aspx 等內建端點，造成功能損壞。
技術挑戰：Regex 需兼顧匹配與排除；替換流程需明確順序。
影響範圍：RSS 服務異常、用戶端錯誤。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Regex 覆蓋範圍過廣
2. 沒有排除清單
3. 替換順序不明確
深層原因：
- 架構層面：不同用途路徑混雜
- 技術層面：Regex 缺少負向條件
- 流程層面：沒有白名單/黑名單

### Solution Design（解決方案設計）
解決策略：在 Regex 或替換邏輯中加入排除條件（負向先行斷言或後置檢查）；建立固定替換順序與排除名單。

實施步驟：
1. 建立排除名單
- 實作細節：rss.aspx 等
- 所需資源：設定檔
- 預估時間：0.5 天

2. 增強 Regex 或後置檢查
- 實作細節：EndsWith/rx 排除
- 所需資源：程式小改
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
if (rel.EndsWith("rss.aspx", StringComparison.OrdinalIgnoreCase))
    return m.Value; // 排除
```
或使用負向先行斷言：
```regex
(?!.*rss\.aspx$)(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/([a-zA-Z0-9\-_\./%]*)
```

實際案例：RSS 與內建端點不再被誤替換。
實作環境：.NET/C#
實測數據：
改善前：出現誤替換個案
改善後：誤替換 0（基於測試集合）
改善幅度：穩定性提升

Learning Points（學習要點）
核心知識點：
- 負向先行斷言與後置檢查
- 白/黑名單策略
- 替換順序的重要性
技能要求：
- 必備技能：Regex
- 進階技能：規則集管理
延伸思考：
- 是否將排除名單配置化可熱更新？
Practice Exercise（練習題）
- 基礎：在替換中加入 rss.aspx 排除
- 進階：加入更多系統端點排除
- 專案：建立可配置的排除名單機制
Assessment Criteria（評估標準）
- 功能完整性（40%）：所有內建端點被排除
- 程式碼品質（30%）：規則清晰
- 效能優化（20%）：少量檢查不影響效能
- 創新性（10%）：配置化

---

## Case #12: 用 Regex 測試工具與單元測試驗證替換規則

### Problem Statement（問題陳述）
業務場景：Regex 被稱為「Write-only language」，規則複雜易錯，需在批次替換前確保正確性。
技術挑戰：如何系統化驗證多模式與例外的匹配與替換行為。
影響範圍：替換錯誤將造成大規模內容破壞。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Regex 可讀性低
2. 覆蓋案例不足
3. 缺乏自動化測試
深層原因：
- 架構層面：沒有規則測試框架
- 技術層面：缺少工具使用習慣
- 流程層面：未建立測試資料集

### Solution Design（解決方案設計）
解決策略：使用線上 Regex 測試器（regexlib.com）和本地單元測試針對主要模式、例外、極端案例建立測試，確保規則穩定。

實施步驟：
1. 建立測試樣本
- 實作細節：正向/負向/邊界案例
- 所需資源：樣本清單
- 預估時間：0.5 天

2. 線上驗證
- 實作細節：regexlib.com 驗證群組擷取
- 所需資源：瀏覽器
- 預估時間：0.5 天

3. 單元測試
- 實作細節：NUnit/xUnit 撰寫測試
- 所需資源：測試框架
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
[Test]
public void Extract_CsPostId_From_ArchiveId_Url()
{
    var url = "/blogs/chicken/archive/2008/06/20/1234.aspx";
    var m = reArchiveId.Match(url);
    Assert.IsTrue(m.Success);
    Assert.AreEqual("1234", m.Groups[1].Value);
}
```

實際案例：部署前發現並修正若干誤匹配，避免實際內容受損。
實作環境：.NET、NUnit/xUnit、regexlib.com
實測數據：
改善前：規則穩定性未知
改善後：通過測試集，信心提升
改善幅度：部署風險大幅降低

Learning Points（學習要點）
核心知識點：
- 測試驅動 Regex 開發
- 正/負/邊界案例設計
- 工具輔助的重要性
技能要求：
- 必備技能：單元測試
- 進階技能：測試資料設計
延伸思考：
- 將規則測試納入 CI？
Practice Exercise（練習題）
- 基礎：為一個 Regex 規則寫 3 個測試
- 進階：覆蓋例外與邊界
- 專案：建立替換規則測試套件
Assessment Criteria（評估標準）
- 功能完整性（40%）：測試覆蓋主要規則
- 程式碼品質（30%）：測試可讀性
- 效能優化（20%）：測試執行效率
- 創新性（10%）：CI 整合

---

## Case #13: 建立並持久化「CS PostID → BE GUID/Slug」映射

### Problem Statement（問題陳述）
業務場景：站內連結替換與外部導向皆依賴舊→新 ID 映射，需可靠保存與重用。
技術挑戰：匯入當下生成、後續多處使用；需可重跑、可回溯。
影響範圍：映射遺失將造成替換/導向全面失效。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 映射為臨時生成
2. 多模組都需使用
3. 缺乏持久化方案
深層原因：
- 架構層面：跨流程共享資料缺口
- 技術層面：序列化與版本化
- 流程層面：變更管理

### Solution Design（解決方案設計）
解決策略：映射以 JSON/XML 存於 App_Data，含版本與時間戳；提供載入 API 與緩存；必要時產出報表。

實施步驟：
1. 設計格式
- 實作細節：字典結構，含 meta
- 所需資源：JSON/XML
- 預估時間：0.5 天

2. 實作序列化
- 實作細節：匯入結束寫入、啟動載入
- 所需資源：序列化工具
- 預估時間：0.5 天

3. 報表與備份
- 實作細節：生成 .csv 供人工檢閱
- 所需資源：簡易工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class CsBeMap
{
    public DateTime GeneratedAt { get; set; }
    public Dictionary<string, Guid> PostIds { get; set; }
}
File.WriteAllText(mapPath, JsonSerializer.Serialize(new CsBeMap {
    GeneratedAt = DateTime.UtcNow, PostIds = map
}));
```

實際案例：映射可被匯入後處理與導向模組共用，降低耦合。
實作環境：.NET/C#
實測數據：
改善前：映射散落或易遺失
改善後：集中持久化、可重用
改善幅度：穩定性提升

Learning Points（學習要點）
核心知識點：
- 關鍵資料的持久化與版本化
- 跨模組共享資料
- 失效/重建策略
技能要求：
- 必備技能：序列化
- 進階技能：資料版本管理
延伸思考：
- 是否上傳至獨立 Key-Value 儲存？
Practice Exercise（練習題）
- 基礎：序列化字典為 JSON
- 進階：加入 meta 欄位
- 專案：映射載入快取與報表
Assessment Criteria（評估標準）
- 功能完整性（40%）：映射可被多處使用
- 程式碼品質（30%）：格式清晰
- 效能優化（20%）：載入快速
- 創新性（10%）：版本化

---

## Case #14: 以兩層迴圈實作 BlogML 匯入處理管線

### Problem Statement（問題陳述）
業務場景：BlogML 匯入需逐篇文章與每則評論處理；原 WebService 單筆呼叫效率差，需自建簡潔穩定的處理管線。
技術挑戰：在單一請求中正確處理「文章→其評論」的階層結構，並確保錯誤不影響全局。
影響範圍：匯入品質與效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. WS 呼叫次數過多
2. 缺少清楚的處理管線
3. 錯誤容易中斷
深層原因：
- 架構層面：沒有本地化批次匯入
- 技術層面：缺少批次錯誤處理
- 流程層面：缺少日誌與回溯

### Solution Design（解決方案設計）
解決策略：以「文章外層迴圈、評論內層迴圈」處理，單篇失敗不影響其他，逐步寫入與記錄。

實施步驟：
1. 外層迴圈
- 實作細節：找出 Post 節點，建立 Post
- 所需資源：XML/BlogML Parser
- 預估時間：0.5 天

2. 內層迴圈
- 實作細節：遍歷 Comment 節點並附加
- 所需資源：BlogEngine.Core
- 預估時間：0.5 天

3. 錯誤處理與日誌
- 實作細節：try/catch 每篇、記錄錯誤
- 所需資源：日誌工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
foreach (var p in xdoc.Descendants("post"))
{
    try
    {
        var bePost = CreatePost(p);
        foreach (var c in p.Descendants("comment"))
        {
            var beComment = CreateComment(c);
            bePost.Comments.Add(beComment);
        }
        bePost.Save();
    }
    catch (Exception ex)
    {
        LogError(p, ex);
    }
}
```

實際案例：以兩層迴圈在短時間內搬完 200+ 文章與評論。
實作環境：.NET/C#
實測數據：
改善前：WS 單筆呼叫，大量往返
改善後：本地批次，I/O 成本下降
改善幅度：效率與穩定性提升

Learning Points（學習要點）
核心知識點：
- 階層資料匯入策略
- 局部失敗、全局繼續
- 日誌與錯誤回報
技能要求：
- 必備技能：XML 處理
- 進階技能：健壯性設計
延伸思考：
- 大量資料的批次大小與事務控制？
Practice Exercise（練習題）
- 基礎：以兩層迴圈寫入 5 篇文章與其評論
- 進階：對單篇失敗記錄與跳過
- 專案：全量匯入與錯誤報表
Assessment Criteria（評估標準）
- 功能完整性（40%）：文章與評論完整寫入
- 程式碼品質（30%）：結構與錯誤處理
- 效能優化（20%）：批次化
- 創新性（10%）：回復策略

---

## Case #15: 控制替換順序，避免相對路徑先替換造成污染

### Problem Statement（問題陳述）
業務場景：來源同時存在「絕對」與「相對」路徑；若先處理相對路徑，可能誤傷絕對路徑的子字串。
技術挑戰：定義安全的替換優先序，避免連鎖破壞。
影響範圍：內容被非預期改寫，難以回復。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 路徑層次互相包含
2. 全域替換未定義順序
3. 缺少預演與快照
深層原因：
- 架構層面：替換策略未標準化
- 技術層面：Regex 規則間干擾
- 流程層面：缺少 Dry-run

### Solution Design（解決方案設計）
解決策略：採「先長後短、先絕對後相對」的替換順序；每一步對比前後差異，必要時以 Dry-run 產生差異報告再執行。

實施步驟：
1. 規則排序
- 實作細節：1) columns/community 絕對 → 2) 相對
- 所需資源：規則清單
- 預估時間：0.5 天

2. Dry-run 與差異
- 實作細節：產生 diff.json
- 所需資源：小工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Step 1: 絕對網址替換
content = reAbsolute.Replace(content, ReplaceImage);
// Step 2: 相對網址替換
content = reRelative.Replace(content, ReplaceImage);
```

實際案例：避免替換污染，僅遺留少量歷史手工路徑手動修正。
實作環境：.NET/C#
實測數據：
改善前：先相對後絕對導致污染
改善後：替換正確率大幅提升
改善幅度：誤替換顯著下降

Learning Points（學習要點）
核心知識點：
- 規則順序的關鍵性
- Dry-run 的價值
- 差異報告
技能要求：
- 必備技能：Regex 替換
- 進階技能：Diff/審查流程
延伸思考：
- 可否以 Token 化方式避免重疊匹配？
Practice Exercise（練習題）
- 基礎：兩步替換策略實作
- 進階：產生差異報告
- 專案：替換流程工具化與回滾
Assessment Criteria（評估標準）
- 功能完整性（40%）：順序正確執行
- 程式碼品質（30%）：清楚分離
- 效能優化（20%）：批次性能
- 創新性（10%）：回滾

---

## Case #16: 尋找未覆蓋模式並產生人工修補清單

### Problem Statement（問題陳述）
業務場景：批次替換後仍有少數歷史手工路徑（如早年手工/非規範 URL）未被涵蓋，需要快速盤點與人工修補。
技術挑戰：如何自動找出「未匹配但疑似需修正」的連結並列出清單。
影響範圍：遺漏連結造成使用者體驗不一致。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 歷史資料非標準
2. 規則不可能 100% 全覆蓋
3. 缺少餘缺報告
深層原因：
- 架構層面：長尾異常無法完全自動化
- 技術層面：需有偵測/報表機制
- 流程層面：人工審查必需

### Solution Design（解決方案設計）
解決策略：以「已知規則集合」做匹配，將未匹配且符合候選特徵的連結抽出清單，產出人工修補待辦。

實施步驟：
1. 匯整已知規則
- 實作細節：整合 Case #4/#7 的 Regex
- 所需資源：規則庫
- 預估時間：0.5 天

2. 掃描產出清單
- 實作細節：輸出 CSV（文章ID、段落、連結）
- 所需資源：小工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var knownPatterns = new[] { reArchiveId, reRootId, reImagePath };
var candidates = ExtractLinks(content).Where(link => !knownPatterns.Any(r => r.IsMatch(link)));
SaveCsv(postId, candidates);
```

實際案例：轉換完成後僅少量案例人工修補，快速收斂。
實作環境：.NET/C#
實測數據：
改善前：人工逐篇檢查成本高
改善後：僅處理清單上的少數項目
改善幅度：人工成本大幅下降

Learning Points（學習要點）
核心知識點：
- 長尾問題處理策略
- 報表化與人工介入點
- 完成定義（Definition of Done）
技能要求：
- 必備技能：字串/集合處理
- 進階技能：簡易報表
延伸思考：
- 是否可用機器學習/啟發式擴大候選識別？
Practice Exercise（練習題）
- 基礎：列出未匹配連結
- 進階：輸出 CSV 報表
- 專案：整合至替換流程的收斂步驟
Assessment Criteria（評估標準）
- 功能完整性（40%）：能準確列出候選
- 程式碼品質（30%）：易用報表
- 效能優化（20%）：掃描效率
- 創新性（10%）：候選識別策略

---

案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #3, #8, #10, #11, #12, #14, #16
- 中級（需要一定基礎）
  - Case #1, #2, #4, #5, #6, #7, #9, #13, #15
- 高級（需要深厚經驗）
  - 本組案例以中低階為主，若延伸至大規模與零停機匯入才屬高級

2. 按技術領域分類
- 架構設計類
  - Case #1, #5, #6, #13, #14, #15
- 效能優化類
  - Case #1, #4, #14
- 整合開發類
  - Case #2, #3, #5, #9, #10, #13
- 除錯診斷類
  - Case #8, #11, #12, #16
- 安全防護類
  - 間接涉及（如 #11 避免誤替換造成供應中斷），可延伸加入權限與輸入驗證

3. 按學習目標分類
- 概念理解型
  - Case #5（Two-Pass 管線）、#13（映射持久化）
- 技能練習型
  - Case #2（解析器）、#4（Regex 替換）、#12（Regex 測試）
- 問題解決型
  - Case #1（自訂匯入器）、#6（舊連結導向）、#7（多模式擷取）、#11（排除策略）、#16（未覆蓋清單）
- 創新應用型
  - Case #9（Counter 側存顯示）、#15（替換順序與 Dry-run）

案例學習路徑建議（案例關聯圖）

- 建議先學
  - Case #12（Regex 測試思維）→ 為後續所有 Regex 密集案例打基礎
  - Case #14（兩層迴圈匯入管線）→ 理解匯入的骨幹流程
  - Case #13（映射持久化）→ 理解舊新 ID 依賴

- 依賴關係
  - Case #1（自訂匯入器）依賴 Case #14（管線）與 Case #13（映射）
  - Case #5（站內連結 Two-Pass）依賴 Case #13（映射）與 Case #7（PostID 擷取）
  - Case #6（舊連結導向）依賴 Case #13（映射）與 Case #7（PostID 擷取）
  - Case #4（圖檔替換）與 Case #11（排除策略）依賴 Case #12（Regex 測試）
  - Case #10（評論補齊）依賴 Case #2（屬性解析）與 Case #3（XML 匯出）
  - Case #9（Counter 保留）依賴 Case #1（匯入擴充）與 Case #13（映射）

- 完整學習路徑建議
  1) Case #12 → 先建立 Regex 測試與驗證能力
  2) Case #14 → 學會匯入管線骨幹
  3) Case #13 → 學會映射持久化
  4) Case #1 → 完成可擴充的自訂匯入器
  5) Case #2 → 能解析 CS2007 屬性袋
  6) Case #3 → 一次性資料匯出技巧
  7) Case #10 → 整合評論補齊
  8) Case #8 → 修正時間欄位
  9) Case #9 → 保留瀏覽數
  10) Case #7 → 熟悉多 URL 模式擷取
  11) Case #5 → 站內連結 Two-Pass 替換
  12) Case #4 + #11 → 圖檔/附件替換與排除策略
  13) Case #6 → 舊連結導向層
  14) Case #15 → 替換順序與 Dry-run 品質保證
  15) Case #16 → 未覆蓋項清單與人工收斂

以上 16 個案例完整對應文章中的問題、根因、解決方案與實作細節，可直接轉化為教學與實戰演練素材。