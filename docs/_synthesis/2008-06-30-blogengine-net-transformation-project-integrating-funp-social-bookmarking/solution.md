---
layout: synthesis
title: "[BlogEngine.NET] 改造工程 - 整合 FunP 推推王"
synthesis_type: solution
source_post: /2008/06/30/blogengine-net-transformation-project-integrating-funp-social-bookmarking/
redirect_from:
  - /2008/06/30/blogengine-net-transformation-project-integrating-funp-social-bookmarking/solution/
postid: 2008-06-30-blogengine-net-transformation-project-integrating-funp-social-bookmarking
---

以下為根據文章整理出的 15 個結構化問題解決案例，聚焦於 BlogEngine.NET 與 FunP 推推王的整合、佈局調整與可用性提升。每個案例均含問題、根因、可落地解法與教學要點，便於實戰教學、專案練習與能力評估。

## Case #1: 從黑米卡改用 FunP，解決載入慢與版面崩壞

### Problem Statement（問題陳述）
• 業務場景：部落格搬家到 BlogEngine.NET 後，需要在文章頁提供本地社群書籤推薦。原先嘗試整合黑米卡來取代「關於作者」區塊，但在列表頁與多元件頁面時載入緩慢，甚至造成版面崩壞，影響閱讀體驗與品牌形象。  
• 技術挑戰：第三方卡片元件過多 client-side script；與 BlogEngine 主題樣式不合，載入延遲導致 DOM 組成中斷。  
• 影響範圍：文章頁、封存頁整體載入時間與穩定性，讀者信任與停留時間。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：  
1. 黑米卡載入速度偏慢，且同頁放入多個卡片使延遲倍增。  
2. 客端腳本注入 document.write/eval 複雜，錯誤難追、易與主題樣式衝突。  
3. 網路波動或第三方失效時，造成佈局異常或半載入狀態。  
• 深層原因：  
- 架構層面：過度仰賴第三方客端注入、缺少退場機制。  
- 技術層面：未採最小依賴、未做替代載入策略。  
- 流程層面：缺乏前置的效能與相容性評估。

### Solution Design（解決方案設計）
• 解決策略：改以 FunP 作為唯一社群書籤供應商，並捨棄黑米卡；先小規模試用驗證穩定後全面替換，降低客端腳本依賴，確保版面穩定。

• 實施步驟：  
1. 供應商評估與 PoC  
- 實作細節：在同頁放多個 FunP 按鈕做壓力測試與相容性檢查。  
- 所需資源：瀏覽器開發者工具、測試頁。  
- 預估時間：0.5 天  
2. 換裝 FunP 並移除黑米卡  
- 實作細節：移除黑米卡 script；插入 FunP IFRAME（見本案或 Case #2 程式碼）。  
- 所需資源：BlogEngine 主題檔存取權。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```html
<!-- 以 FunP IFRAME 取代黑米卡 -->
<IFRAME width="60" height="55" marginWidth="0" marginHeight="0"
        frameBorder="0" scrolling="no"
        src="http://funp.com/tools/buttoniframe.php?url={EncodedUrl}&s=1">
</IFRAME>
```

• 實際案例：作者最終選 FunP，並回報速度較快、無版面掛掉問題。  
• 實作環境：BlogEngine.NET（v1.x）、ASP.NET/C#、IIS、FunP。  
• 實測數據：  
改善前：黑米卡慢、同頁多卡片易掛版。  
改善後：FunP 載入快、未再遇版面崩壞。  
改善幅度：作者敘述為「速度也快一些、沒碰到版面掛掉」。

Learning Points（學習要點）
• 核心知識點：  
- 第三方元件選型的效能與相容性驗證  
- 降低客端依賴的穩定性思維  
- 單一供應商策略的維運成本優勢  
• 技能要求：  
- 必備技能：HTML、ASP.NET 主題檔修改、瀏覽器檢測  
- 進階技能：前端效能觀察、替代方案 A/B 測試  
• 延伸思考：  
- 可應用在任何需要第三方工具的選型與換裝  
- 風險：單一供應商依賴  
- 優化：加上健康檢查或降級顯示策略

Practice Exercise（練習題）
• 基礎練習：在測試頁引入兩種社群書籤，觀察載入時間與錯誤。  
• 進階練習：設計切換旗標，能一鍵切換供應商並收集載入時間。  
• 專案練習：替既有站台完成供應商選型與換裝報告（含風險與回滾方案）。

Assessment Criteria（評估標準）
• 功能完整性（40%）：能安全替換並正常顯示。  
• 程式碼品質（30%）：主題檔結構清晰、可回滾。  
• 效能優化（20%）：載入明顯較快、穩定。  
• 創新性（10%）：提供自動化切換或監控。

---

## Case #2: 以直接 IFRAME 取代官方 Script 嵌入，降低不確定性

### Problem Statement（問題陳述）
• 業務場景：FunP 官方工具主要提供一段 JS 以 document.write/eval 產生 HTML，錯誤與延遲不易排查。部落格需要穩定、可控的嵌入方式，避免版面被第三方腳本牽動。  
• 技術挑戰：無法掌控第三方 script 的載入順序與錯誤處理；debug 複雜。  
• 影響範圍：文章頁與封存頁可用性、維護成本。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：JS 動態注入與遞迴 document.write/eval 造成難以斷點與監控。  
• 深層原因：  
- 架構層面：非必要的客端動態 DOM 操作。  
- 技術層面：無 degrade 模式與錯誤隔離。  
- 流程層面：未預先擷取最終輸出以直嵌。

### Solution Design（解決方案設計）
• 解決策略：用瀏覽器觀察最終插入的標記，抽取 IFRAME 端點，改為直接 IFRAME 嵌入，避免第三方 JS 執行。

• 實施步驟：  
1. 追蹤最終輸出  
- 實作細節：以開發者工具或檔案檢視，找出最後插入的 IFRAME src。  
- 所需資源：瀏覽器開發者工具。  
- 預估時間：0.5 天  
2. 主題檔改為直嵌  
- 實作細節：將 IFRAME 直接寫入 PostView.ascx。  
- 所需資源：BlogEngine 主題檔。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```html
<!-- 追出來的最終輸出（示意） -->
<IFRAME width="60" height="55" marginWidth="0" marginHeight="0"
        frameBorder="0" scrolling="no"
        src="http://funp.com/tools/buttoniframe.php?url=xxxxxxxx&s=1">
</IFRAME>
```

• 實際案例：作者表示改為 IFRAME 後「效果好多了」，版面不再掛掉。  
• 實作環境：BlogEngine.NET（v1.x）、ASP.NET/C#。  
• 實測數據：  
改善前：JS 注入不穩、debug 困難。  
改善後：直嵌 IFRAME 可控、穩定。  
改善幅度：明顯降低不確定性。

Learning Points（學習要點）
• 核心知識點：第三方腳本替換為直嵌的工程化方法  
• 技能要求：  
- 必備技能：DOM 分析、HTML  
- 進階技能：網路/DOM 追蹤、降級策略設計  
• 延伸思考：  
- 可應用在廣告、追蹤碼、社群元件  
- 風險：第三方介面若變更 URL 參數需同步維護  
- 優化：包裝成伺服端控制項

Practice Exercise（練習題）
• 基礎：在測試頁重現第三方 script 並找出最終 IFRAME。  
• 進階：撰寫小工具自動抽取最終 src。  
• 專案：封裝為可重用的 ASP.NET UserControl。

Assessment Criteria（評估標準）
• 功能完整性：直嵌功能正常  
• 程式碼品質：可維護、註解清楚  
• 效能優化：減少阻塞與錯誤  
• 創新性：自動化抽取與封裝

---

## Case #3: 推文連結預填資料（標題/內文/標籤），降低使用者輸入

### Problem Statement（問題陳述）
• 業務場景：讀者推文至 FunP 時，若需自行填寫標題、摘要與標籤，容易中斷與流失。希望自動帶出文章基本資訊，提升推文完成率。  
• 技術挑戰：需正確組合並編碼參數，避免亂碼與截斷。  
• 影響範圍：推文流程完成率、分享數。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：未預填資料導致使用者需重複輸入。  
• 深層原因：  
- 架構層面：缺少後端組裝分享參數的流程。  
- 技術層面：未處理 URL 編碼與摘要長度。  
- 流程層面：缺少以使用者減負為目標的 UX 設計。

### Solution Design（解決方案設計）
• 解決策略：於伺服端生成包含 url、標題、摘要、tags[] 的推文連結，確保中文等特殊字元正確編碼，摘要採 70 字截斷。

• 實施步驟：  
1. 伺服端組字串  
- 實作細節：UrlEncode 標題、URL、摘要，並依分類組 tags[]。  
- 所需資源：ASP.NET Server.UrlEncode。  
- 預估時間：0.5 天  
2. 以 <a> 連結呈現  
- 實作細節：於 PostView.ascx 放入 anchor 與按鈕圖。  
- 所需資源：主題檔。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```csharp
// PostView.ascx 伺服端變數
Regex strip = new Regex("<[^>]*>", RegexOptions.Compiled);
string bodyText = strip.Replace(Post.Content, "");
int max = 70;

string EncUrl = Page.Server.UrlEncode(Post.AbsoluteLink.ToString());
string EncTitle = Page.Server.UrlEncode(Post.Title);
string EncBody = Page.Server.UrlEncode(bodyText.Length > max ? bodyText.Substring(0, max) + "..." : bodyText);

string TagsQS = "";
foreach (var cat in Post.Categories)
{
    TagsQS += "&tags[]=" + Page.Server.UrlEncode(cat.Title);
}
```

```html
<!-- 預填推文連結 -->
<a href="http://funp.com/push/submit/add.php?url=<%=EncUrl%>&s=<%=EncTitle%>&t=<%=EncBody%><%=TagsQS%>&via=tools"
   title="貼到 funP">
  <img src="http://funp.com/tools/images/post_03.gif" border="0"/>
</a>
```

• 實際案例：作者表示「推文時自動帶出文章的基本資訊」。  
• 實作環境：BlogEngine.NET、ASP.NET/C#。  
• 實測數據：  
改善前：推文需手動輸入。  
改善後：推文自動帶入標題/摘要/標籤。  
改善幅度：流程明顯簡化。

Learning Points（學習要點）
• 核心知識點：分享連結的參數設計與編碼  
• 技能要求：  
- 必備技能：C# 字串處理、UrlEncode  
- 進階技能：多語系/中文參數處理  
• 延伸思考：  
- 適用於任何外部分享/申請連結  
- 風險：第三方參數命名改動  
- 優化：抽象為可配置模板

Practice Exercise（練習題）
• 基礎：為任一第三方分享服務生成預填連結。  
• 進階：支援多個服務並以策略模式切換。  
• 專案：做一個分享參數產生器 SDK。

Assessment Criteria（評估標準）
• 功能完整性：能正確預填  
• 程式碼品質：可讀、可維護  
• 效能優化：伺服端生成、無額外阻塞  
• 創新性：支援多服務與模板

---

## Case #4: 用 Regex 去除 HTML 並限制摘要長度，避免分享描述污染

### Problem Statement（問題陳述）
• 業務場景：分享描述應為精簡純文字，避免夾雜 HTML 標籤或過長導致外部頁面顯示錯亂。  
• 技術挑戰：可靠去標籤、避免多字節字元截斷問題。  
• 影響範圍：分享呈現品質、點擊率。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：直接取用 Post.Content 會包含 HTML，長度亦無限制。  
• 深層原因：  
- 架構層面：缺少共同的摘要生成邏輯。  
- 技術層面：未作去標籤與長度控制。  
- 流程層面：未規範分享內容格式。

### Solution Design（解決方案設計）
• 解決策略：用 Regex 去除 HTML，長度限制 70 字，超出則加 ...，確保分享描述簡潔易讀。

• 實施步驟：  
1. 實作摘要工具  
- 實作細節：Regex <[^>]*> 去標籤，Substring 控制長度。  
- 所需資源：.NET Regex。  
- 預估時間：0.5 天  
2. 整合分享流程  
- 實作細節：在 Case #3 的 EncBody 使用。  
- 所需資源：PostView.ascx。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```csharp
Regex strip = new Regex("<[^>]*>", RegexOptions.Compiled);
string text = strip.Replace(Post.Content, "");
int max = 70;
string excerpt = text.Length > max ? text.Substring(0, max) + "..." : text;
```

• 實際案例：作者使用該方式生成摘要參數 t。  
• 實作環境：ASP.NET/C#。  
• 實測數據：  
改善前：描述可能含 HTML。  
改善後：純文字且長度受控。  
改善幅度：顯著提升可讀性。

Learning Points（學習要點）
• 核心知識點：去標籤與字串安全截斷  
• 技能要求：Regex、字串處理  
• 延伸思考：  
- 可擴展為多語系摘要策略  
- 潛在風險：Regex 過度簡化對 Edge HTML  
- 優化：採 HTML parser

Practice Exercise（練習題）
• 基礎：寫一個去 HTML 並截斷的小函式。  
• 進階：加入多語系與 unicode 安全截斷。  
• 專案：封裝摘要產生器 NuGet 包。

Assessment Criteria（評估標準）
• 功能完整性：能穩定生成摘要  
• 程式碼品質：容錯與測試  
• 效能優化：Regex 編譯化  
• 創新性：可配置策略

---

## Case #5: 從分類自動帶出 FunP tags[] 參數，提升貼標一致性

### Problem Statement（問題陳述）
• 業務場景：讓 FunP 分享自動帶入標籤，避免使用者重填，並與部落格現有分類一致。  
• 技術挑戰：需從 Post.Categories 正確組合多值 query string。  
• 影響範圍：分享可見度與檢索友好度。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：未帶入 tags[] 導致分享未分類或資訊不足。  
• 深層原因：  
- 架構層面：分類與外部標籤未映射。  
- 技術層面：未處理多值參數與 URL 編碼。  
- 流程層面：缺乏規則自動化。

### Solution Design（解決方案設計）
• 解決策略：遍歷 Post.Categories，為每個分類加上 &tags[]=Title（UrlEncode），統一連動分享標籤。

• 實施步驟：  
1. 組 tags[] 參數  
- 實作細節：逐一 UrlEncode 後串接。  
- 所需資源：C#。  
- 預估時間：0.5 天  
2. 整合分享連結  
- 實作細節：插入 Case #3 範例中的 <%=TagsQS%>。  
- 所需資源：PostView.ascx。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```csharp
string TagsQS = "";
foreach (var cat in Post.Categories)
{
    TagsQS += "&tags[]=" + Page.Server.UrlEncode(cat.Title);
}
```

• 實際案例：作者分享時自動帶出標籤。  
• 實作環境：BlogEngine.NET。  
• 實測數據：  
改善前：分享缺標籤。  
改善後：與分類一致的標籤自動帶入。  
改善幅度：一致性提升。

Learning Points（學習要點）
• 核心知識點：多值 query string 組裝  
• 技能要求：C#、URL 編碼  
• 延伸思考：  
- 可支援標籤白名單或映射表  
- 風險：分類名稱過長  
- 優化：長度/字元過濾

Practice Exercise（練習題）
• 基礎：將多分類轉為 tags[] 參數。  
• 進階：加入映射表，避免同義詞重複。  
• 專案：建立分類-標籤對照同步器。

Assessment Criteria（評估標準）
• 功能完整性：多值可用  
• 程式碼品質：可讀性  
• 效能優化：O(n) 迭代即可  
• 創新性：可配置映射

---

## Case #6: 在 PostView 以 FunP 推薦數取代內建 Rating

### Problem Statement（問題陳述）
• 業務場景：BlogEngine 內建 Rating 與外部推文機制重複，決定以推文數作為社群認可指標，簡化介面與互動。  
• 技術挑戰：安全移除 Rating，並以推文按鈕無縫取代。  
• 影響範圍：文章頁 UI、互動機制的一致性。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：雙軌機制混淆。  
• 深層原因：  
- 架構層面：指標過多，缺乏聚焦。  
- 技術層面：Rating 控制項與主題耦合。  
- 流程層面：未定義唯一互動指標。

### Solution Design（解決方案設計）
• 解決策略：移除 Rating 控制，於原位置以 FunP IFRAME 取代，維持視覺一致。

• 實施步驟：  
1. 移除 Rating  
- 實作細節：從 PostView.ascx 拔除 Rating 控件/標記。  
- 所需資源：主題檔。  
- 預估時間：0.5 天  
2. 插入 FunP IFRAME  
- 實作細節：用 s=1 樣式置於原位置。  
- 所需資源：同上。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```csharp
<IFRAME width="60" height="55" marginWidth="0" marginHeight="0"
        frameBorder="0" scrolling="no"
        src="http://funp.com/tools/buttoniframe.php?url=<%=EncodedAbsoluteLink%>&s=1">
</IFRAME>
```

• 實際案例：作者「捨棄內建 Rating，直接用推文」。  
• 實作環境：BlogEngine.NET。  
• 實測數據：  
改善前：Rating 與推文並存。  
改善後：以推文為唯一互動指標。  
改善幅度：介面簡化。

Learning Points（學習要點）
• 核心知識點：指標統一與 UI 精簡  
• 技能要求：主題檔修改  
• 延伸思考：  
- 適用於移除重複互動元件  
- 風險：舊資料累計怎麼處理  
- 優化：提供改版說明

Practice Exercise（練習題）
• 基礎：在測試主題中移除一個元件並以新元件取代。  
• 進階：提供切換旗標以支持雙模式。  
• 專案：清理網站的重複互動元件並統一指標。

Assessment Criteria（評估標準）
• 功能完整性：替換無縫  
• 程式碼品質：簡潔  
• 效能優化：無多餘資源  
• 創新性：模式切換

---

## Case #7: 在 Archive 頁以 FunP 按鈕取代 Rating 欄位

### Problem Statement（問題陳述）
• 業務場景：封存頁按分類列出所有文章，原顯示 Rating 欄。希望改為顯示 FunP 推薦數，與文章頁一致。  
• 技術挑戰：大量項目渲染、樣式壓縮、避免版面破壞。  
• 影響範圍：封存頁載入體驗、穩定性。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：原 Rating 欄位不再使用。  
• 深層原因：  
- 架構層面：清單頁與詳情頁指標不一致。  
- 技術層面：官方 script 無法應付數百按鈕。  
- 流程層面：缺乏清單頁的資源量管控。

### Solution Design（解決方案設計）
• 解決策略：改寫 archive.aspx.cs，在 Rating 位置插入小尺寸 FunP IFRAME（s=12），避免使用官方 script。

• 實施步驟：  
1. 代碼注入  
- 實作細節：在產列迴圈為每行加入 IFRAME HTML。  
- 所需資源：archive.aspx.cs。  
- 預估時間：0.5 天  
2. 樣式與測試  
- 實作細節：縮小寬高、測 IE/多瀏覽器。  
- 所需資源：瀏覽器。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```csharp
if (BlogSettings.Instance.EnableRating)
{
    HtmlTableCell rating = new HtmlTableCell();
    rating.InnerHtml = string.Format(
      @"<IFRAME marginWidth=0 marginHeight=0 
          src='http://funp.com/tools/buttoniframe.php?url={0}&amp;s=12'
          frameBorder=0 width=80 scrolling=no height=15></IFRAME>",
      (post.AbsoluteLink.ToString()));
    rating.Attributes.Add("class", "rating");
    row.Cells.Add(rating);
}
```

• 實際案例：作者以此法完成封存頁整合，並指出 IE 面對四五百 IFRAME 仍吃力。  
• 實作環境：BlogEngine.NET、ASP.NET/C#、IE。  
• 實測數據：  
改善前：使用官方 script 不切實際。  
改善後：以直嵌 IFRAME 成功顯示，各列一致。  
改善幅度：顯著提升穩定性，但在大量 IFRAME 下 IE 仍重。

Learning Points（學習要點）
• 核心知識點：清單頁大量元件的穩定渲染  
• 技能要求：ASP.NET WebForms 控制項動態插入  
• 延伸思考：  
- 可應用到任何清單頁外掛元件  
- 風險：大量 IFRAME 的效能  
- 優化：延遲載入、分頁或僅顯示熱門

Practice Exercise（練習題）
• 基礎：在表格每列加入自訂 IFRAME。  
• 進階：加入分頁或 IntersectionObserver 延遲載入（若前端可用）。  
• 專案：封存頁效能優化 PoC，含 3 種策略比較。

Assessment Criteria（評估標準）
• 功能完整性：欄位準確替換  
• 程式碼品質：插入點與樣式清晰  
• 效能優化：降低阻塞  
• 創新性：提供延遲/分頁策略

---

## Case #8: 僅保留單一社群書籤供應商，避免頁面雜訊與性能損耗

### Problem Statement（問題陳述）
• 業務場景：許多部落格同時放入多家書籤服務（FunP、黑米、MyShare 乃至國外服務），造成 UI 擁擠、載入慢。  
• 技術挑戰：識別核心需求與刪繁就簡，保留關鍵服務。  
• 影響範圍：載入速度、可用性、操作成本。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：多供應商並存，增加請求數與腳本量。  
• 深層原因：  
- 架構層面：缺乏 UI 極簡原則。  
- 技術層面：未聚合或選優。  
- 流程層面：沒有資料導向的選型。

### Solution Design（解決方案設計）
• 解決策略：只保留 FunP 一套，移除其他書籤，將互動聚焦於單一指標，並簡化頁面元素。

• 實施步驟：  
1. 清單與清理  
- 實作細節：盤點所有社群書籤，逐一下線。  
- 所需資源：主題檔與版型。  
- 預估時間：0.5 天  
2. 單點優化  
- 實作細節：保留 FunP，確保位置與樣式一致。  
- 所需資源：CSS/主題檔。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：  
- 移除其他供應商 script/IFRAME，僅保留 FunP（見 Case #2/6 片段）。

• 實際案例：作者明確「就鎖定一個共用書籤就好」。  
• 實作環境：BlogEngine.NET。  
• 實測數據：  
改善前：一字排開落落長、載入慢。  
改善後：專注 FunP，頁面清爽。  
改善幅度：體感明顯。

Learning Points（學習要點）
• 核心知識點：設計取捨與聚焦  
• 技能要求：前端結構梳理  
• 延伸思考：  
- 通用于任何第三方元件清理  
- 風險：單點依賴  
- 優化：增加監控與替代方案

Practice Exercise（練習題）
• 基礎：移除多餘第三方圖標/腳本。  
• 進階：以設定檔控制保留清單。  
• 專案：制訂外掛治理規範與流程。

Assessment Criteria（評估標準）
• 功能完整性：清理到位  
• 程式碼品質：無殘留  
• 效能優化：請求數降低  
• 創新性：治理規範與工具

---

## Case #9: 保留原 CS 視覺語言，用推文按鈕取代舊計數器

### Problem Statement（問題陳述）
• 業務場景：希望新元件（FunP 按鈕）不破壞既有「CS」風格的視覺語意，延續用戶對原位置/功能的認知。  
• 技術挑戰：在不改大版的前提下調整定位與尺寸，確保一致性。  
• 影響範圍：整體設計一致性與學習成本。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：新元件大小/位置與舊計數器不同。  
• 深層原因：  
- 架構層面：UI 元件替換未納入設計系統。  
- 技術層面：IFRAME 尺寸與 CSS 未調和。  
- 流程層面：缺乏設計對齊。

### Solution Design（解決方案設計）
• 解決策略：沿用原計數器位置，將 FunP IFRAME 設為相同占位/尺寸，確保視覺延續性。

• 實施步驟：  
1. 位置對齊  
- 實作細節：找到原計數器容器，替換為 FunP IFRAME。  
- 所需資源：主題檔。  
- 預估時間：0.5 天  
2. 尺寸微調  
- 實作細節：透過 width/height/CSS 對齊原風格。  
- 所需資源：CSS。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```html
<div class="post-meta-counter">
  <IFRAME width="60" height="55" frameBorder="0" scrolling="no"
          src="http://funp.com/tools/buttoniframe.php?url=<%=EncodedAbsoluteLink%>&s=1">
  </IFRAME>
</div>
```

• 實際案例：作者「版面希望類似原有 CS 樣式，拿推文按鈕取代原計數器」。  
• 實作環境：BlogEngine.NET/CSS。  
• 實測數據：  
改善前：視覺斷裂。  
改善後：視覺延續、一致。  
改善幅度：明顯。

Learning Points（學習要點）
• 核心知識點：替換式設計與一致性  
• 技能要求：CSS/HTML  
• 延伸思考：  
- 適用於任何元件替換  
- 風險：第三方樣式變動  
- 優化：外層容器抽象

Practice Exercise（練習題）
• 基礎：在固定容器替換為新元件並對齊樣式。  
• 進階：建立樣式對齊檢查清單。  
• 專案：完成一個 UI 元件替換指南。

Assessment Criteria（評估標準）
• 功能完整性：替換成功  
• 程式碼品質：語意化標記  
• 效能優化：無新增阻塞  
• 創新性：設計系統化

---

## Case #10: 移除 Tags 區塊，改以分類為主，降低資訊噪音

### Problem Statement（問題陳述）
• 業務場景：左下 Tags 區塊影響閱讀動線，決定以分類為主，清理多餘標籤展示。  
• 技術挑戰：安全移除區塊且不影響 SEO 與站內結構。  
• 影響範圍：側欄可讀性、導航清晰度。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：Tags 展示冗長、影響視覺。  
• 深層原因：  
- 架構層面：導航結構重疊（分類 vs 標籤）。  
- 技術層面：主題側欄耦合。  
- 流程層面：導航策略未統一。

### Solution Design（解決方案設計）
• 解決策略：移除 Tags 控制項/標記，以分類導覽為主，並確保內頁仍保留標籤語意（如 meta）。

• 實施步驟：  
1. 主題清理  
- 實作細節：在 MasterPage/側欄 ascx 移除 Tags 模塊。  
- 所需資源：主題檔。  
- 預估時間：0.5 天  
2. 導向檢查  
- 實作細節：確認分類導覽可達。  
- 所需資源：站內連結檢查。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```html
<!-- 刪除或註解掉 Tags 側欄 -->
<!-- <uc:Tags runat="server" ID="TagsList" /> -->
```

• 實際案例：作者「Tags 決定捨棄不用，以分類為主」。  
• 實作環境：BlogEngine.NET 主題。  
• 實測數據：  
改善前：側欄擁擠。  
改善後：動線清晰。  
改善幅度：可讀性提升。

Learning Points（學習要點）
• 核心知識點：導航簡化與取捨  
• 技能要求：主題檔編修  
• 延伸思考：  
- 適用於所有側欄清理  
- 風險：既有標籤頁權重  
- 優化：保留標籤 sitemap 但不顯示

Practice Exercise（練習題）
• 基礎：移除任一側欄模塊並驗證導覽。  
• 進階：提供設定控制顯示/隱藏。  
• 專案：側欄治理專案（含可用性測試）。

Assessment Criteria（評估標準）
• 功能完整性：清理無副作用  
• 程式碼品質：注釋清楚  
• 效能優化：元素減量  
• 創新性：設定化控制

---

## Case #11: 調整分類區塊位置（右下 → 右上），提升可見度

### Problem Statement（問題陳述）
• 業務場景：分類放右下「很礙眼」且不利於導航，決定移至右上提高可見度與可用性。  
• 技術挑戰：不破壞整體版面、維持自適應。  
• 影響範圍：導航效率、使用者體驗。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：分類位置過低。  
• 深層原因：  
- 架構層面：版面區塊優先級未定義。  
- 技術層面：框架與樣式耦合。  
- 流程層面：未基於用戶行為調整。

### Solution Design（解決方案設計）
• 解決策略：在右上區塊占位添加分類控件，移除原位置，並以 CSS 保持一致。

• 實施步驟：  
1. 移動控制項  
- 實作細節：剪下分類控件標籤，貼至右上容器。  
- 所需資源：MasterPage/側欄 ascx。  
- 預估時間：0.5 天  
2. 樣式對齊  
- 實作細節：調整 margin/padding 保持整體一致。  
- 所需資源：CSS。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```html
<!-- 原右下移除 -->
<!-- <uc:Categories runat="server" ID="CatsBottom" /> -->

<!-- 新右上放置 -->
<div class="sidebar-top">
  <uc:Categories runat="server" ID="CatsTop" />
</div>
```

• 實際案例：作者「分類放右下很礙眼，移到右上」。  
• 實作環境：BlogEngine.NET/CSS。  
• 實測數據：  
改善前：可見度低。  
改善後：導航更直覺。  
改善幅度：體感提升。

Learning Points（學習要點）
• 核心知識點：資訊架構與視覺層級  
• 技能要求：主題檔與 CSS  
• 延伸思考：  
- 適用於常用導航提升  
- 風險：小螢幕擠壓  
- 優化：響應式

Practice Exercise（練習題）
• 基礎：移動任一側欄元件位置。  
• 進階：依視窗寬度自動變位。  
• 專案：完成一套側欄優先級策略。

Assessment Criteria（評估標準）
• 功能完整性：位置正確  
• 程式碼品質：結構清晰  
• 效能優化：不增加開銷  
• 創新性：響應式處理

---

## Case #12: 加上智財權聲明，降低被盜文風險

### Problem Statement（問題陳述）
• 業務場景：作者不滿被盜文，希望在頁面加入智財權聲明，明確告知使用規範與引用條件。  
• 技術挑戰：在不干擾閱讀的前提下顯示法務訊息。  
• 影響範圍：法務合規、品牌保護。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：缺少明確著作權聲明。  
• 深層原因：  
- 架構層面：頁面未預留法務區塊。  
- 技術層面：插入位置與樣式需斟酌。  
- 流程層面：缺法務溝通與版權策略。

### Solution Design（解決方案設計）
• 解決策略：在頁尾或側欄加入簡潔版權聲明，並連結詳細政策頁。

• 實施步驟：  
1. 聲明添加  
- 實作細節：MasterPage 頁尾加入聲明文字與連結。  
- 所需資源：主題檔。  
- 預估時間：0.5 天  
2. 樣式設計  
- 實作細節：以小字不干擾閱讀。  
- 所需資源：CSS。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```html
<footer class="site-footer">
  <small>本文版權為原作者所有，未經允許不得轉載。
    <a href="/copyright">詳細聲明</a>
  </small>
</footer>
```

• 實際案例：作者「不爽被盜文，加上一段智財權聲明」。  
• 實作環境：BlogEngine.NET。  
• 實測數據：  
改善前：無聲明。  
改善後：有清楚告示。  
改善幅度：合規度提升。

Learning Points（學習要點）
• 核心知識點：法務訊息展示與 UX 平衡  
• 技能要求：HTML/CSS  
• 延伸思考：  
- 可應用於隱私、Cookie 提示  
- 風險：過度打擾  
- 優化：彈性顯示策略

Practice Exercise（練習題）
• 基礎：新增頁尾版權宣告。  
• 進階：建立著作權政策頁模板。  
• 專案：站台法務訊息標準化。

Assessment Criteria（評估標準）
• 功能完整性：訊息可見  
• 程式碼品質：語意化  
• 效能優化：極簡負擔  
• 融合度：不干擾閱讀

---

## Case #13: 以 Server.UrlEncode 正確處理中文參數，避免亂碼/截斷

### Problem Statement（問題陳述）
• 業務場景：分享連結中包含中文標題、摘要、分類，需確保在 FunP URL 參數中正常傳遞。  
• 技術挑戰：未編碼的多語系字元可能導致亂碼或連結失效。  
• 影響範圍：分享成功率、資料正確性。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：未對 querystring 進行 URL 編碼。  
• 深層原因：  
- 架構層面：缺少統一的編碼流程。  
- 技術層面：中文/特殊字元易導致錯誤。  
- 流程層面：未制定跨語系規範。

### Solution Design（解決方案設計）
• 解決策略：對 url、標題、摘要、tags[] 全部使用 Page.Server.UrlEncode 統一編碼。

• 實施步驟：  
1. 建立工具方法  
- 實作細節：封裝 Encode 方法供重用。  
- 所需資源：C#。  
- 預估時間：0.5 天  
2. 全面替換  
- 實作細節：在分享組裝點替換為工具方法。  
- 所需資源：PostView.ascx。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```csharp
string E(string s) => Page.Server.UrlEncode(s);
string EncUrl = E(Post.AbsoluteLink.ToString());
string EncTitle = E(Post.Title);
string EncBody = E(excerpt);
string TagsQS = string.Join("", Post.Categories.Select(c => "&tags[]=" + E(c.Title)));
```

• 實際案例：作者程式碼顯示全面使用 UrlEncode。  
• 實作環境：ASP.NET。  
• 實測數據：  
改善前：可能出現亂碼/失效。  
改善後：中文參數正常。  
改善幅度：穩定性提升。

Learning Points（學習要點）
• 核心知識點：URL 編碼與國際化  
• 技能要求：C#、HTTP 基礎  
• 延伸思考：  
- 適用於所有外部連結組裝  
- 風險：雙重編碼  
- 優化：集中式編碼工具

Practice Exercise（練習題）
• 基礎：對多語系字串進行 UrlEncode 測試。  
• 進階：處理雙重編碼與空白、emoji。  
• 專案：建立統一的 URL 工具庫。

Assessment Criteria（評估標準）
• 功能完整性：參數正確  
• 程式碼品質：統一封裝  
• 效能優化：輕量  
• 創新性：工具化程度

---

## Case #14: 逆向官方工具輸出，鎖定 IFRAME 端點，簡化整合

### Problem Statement（問題陳述）
• 業務場景：官方僅提供 script 嵌入，為降低不確定性，需要知道實際生成的 HTML/端點。  
• 技術挑戰：需要定位最終輸出，不被多層 script 混淆。  
• 影響範圍：整合開發效率、可維護性。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：script 多層包裝，閱讀困難。  
• 深層原因：  
- 架構層面：第三方工具強制客端注入。  
- 技術層面：動態生成隱藏最終端點。  
- 流程層面：缺乏逆向定位流程。

### Solution Design（解決方案設計）
• 解決策略：以網頁監聽或檔案檢視追出最終 IFRAME，改為直嵌並控制參數。

• 實施步驟：  
1. 監看輸出  
- 實作細節：載入官方工具，觀察 DOM 變化与 IFRAME src。  
- 所需資源：瀏覽器工具。  
- 預估時間：0.5 天  
2. 記錄端點  
- 實作細節：萃取出 buttoniframe.php?url=...&s=... 作為基底。  
- 所需資源：筆記/文件。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```html
<!-- 萃取出的端點 -->
http://funp.com/tools/buttoniframe.php?url=<EncodedUrl>&s=<StyleId>
```

• 實際案例：作者「花了點時間追一下，追出最後插在網頁的 HTML CODE」。  
• 實作環境：瀏覽器/ASP.NET。  
• 實測數據：  
改善前：整合不透明。  
改善後：端點清晰、直嵌可控。  
改善幅度：可維護性提升。

Learning Points（學習要點）
• 核心知識點：前端輸出逆向與端點萃取  
• 技能要求：DOM/Network 檢視  
• 延伸思考：  
- 適用於任何第三方 script  
- 風險：對方改版  
- 優化：加上監測

Practice Exercise（練習題）
• 基礎：對一個第三方 script 找出最終輸出。  
• 進階：寫腳本自動擷取 IFRAME src。  
• 專案：建立第三方整合檢視清單與端點庫。

Assessment Criteria（評估標準）
• 功能完整性：能準確萃取  
• 程式碼品質：工具腳本可維護  
• 效能優化：加速整合  
• 創新性：自動化程度

---

## Case #15: 大量清單頁選用小樣式（s=12）與縮小占位，緩解渲染壓力

### Problem Statement（問題陳述）
• 業務場景：封存頁出現近 500 個推文按鈕，IE 渲染吃力。需要在功能與壓力間取得平衡。  
• 技術挑戰：大量 IFRAME 導致繪製與網路請求壓力。  
• 影響範圍：封存頁載入時間、互動延遲。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：每列一個 IFRAME，總數過大。  
• 深層原因：  
- 架構層面：清單頁無延遲載入/分頁。  
- 技術層面：IFRAME 成本高。  
- 流程層面：未針對清單頁定義輕量展示策略。

### Solution Design（解決方案設計）
• 解決策略：選用較小樣式參數 s=12，設定 width=80/height=15，降低占位與重排；保留功能之餘盡量減負。

• 實施步驟：  
1. 採小樣式  
- 實作細節：在 archive.aspx.cs 使用 s=12，縮小寬高（見 Case #7 代碼）。  
- 所需資源：主題/程式檔。  
- 預估時間：0.5 天  
2. 壓力測試  
- 實作細節：在 IE 與其他瀏覽器實測。  
- 所需資源：多瀏覽器。  
- 預估時間：0.5 天

• 關鍵程式碼/設定：
```csharp
// 參數 s=12 並縮小占位（引用 Case #7）
src='http://funp.com/tools/buttoniframe.php?url={0}&amp;s=12'
width=80 height=15
```

• 實際案例：作者指出使用直嵌後 IE 仍吃力，但較官方法可行。  
• 實作環境：BlogEngine.NET、IE。  
• 實測數據：  
改善前：官方 script 不可行。  
改善後：小尺寸直嵌可用，但 IE 吃力。  
改善幅度：可用性提升，效能瓶頸部分緩解。

Learning Points（學習要點）
• 核心知識點：大量外掛在清單頁的降載策略  
• 技能要求：WebForms 動態插入、跨瀏覽器測試  
• 延伸思考：  
- 可再結合分頁/延遲載入  
- 風險：仍有極限  
- 優化：僅顯示熱門/hover 請求

Practice Exercise（練習題）
• 基礎：用不同 s 參數比較占位與觀感。  
• 進階：封存頁加入分頁/按需載入。  
• 專案：做一份清單頁降載方案白皮書。

Assessment Criteria（評估標準）
• 功能完整性：保持功能  
• 程式碼品質：樣式統一  
• 效能優化：占位縮小  
• 創新性：多策略並行

------------------------------------------------------------

案例分類

1) 按難度分類
• 入門級（適合初學者）：Case 4, 5, 6, 8, 9, 10, 11, 12, 13  
• 中級（需要一定基礎）：Case 1, 2, 3, 7, 15, 14  
• 高級（需要深厚經驗）：（本文範圍內無需高階分散式或深度改造，若加入延遲載入/分頁/快取可提升為高級）

2) 按技術領域分類
• 架構設計類：Case 6, 8, 9, 10, 11  
• 效能優化類：Case 1, 2, 7, 15  
• 整合開發類：Case 2, 3, 5, 6, 7, 13, 14  
• 除錯診斷類：Case 2, 7, 14  
• 安全防護類：Case 12

3) 按學習目標分類
• 概念理解型：Case 8, 9, 10, 11, 12  
• 技能練習型：Case 3, 4, 5, 6, 13  
• 問題解決型：Case 1, 2, 7, 15, 14  
• 創新應用型：Case 14, 15（若延伸延遲載入/自動化抽取）

案例關聯圖（學習路徑建議）
• 建議先學：  
- Case 8（單一供應商策略）→ 建立思維基礎  
- Case 1（供應商選型與換裝）→ 做出正確選擇  
- Case 2（直嵌 IFRAME）→ 奠定整合方法論

• 依賴關係：  
- Case 3（預填資料）依賴 Case 2 的直嵌與 PostView 修改  
- Case 4、5、13（摘要與編碼、標籤）依賴 Case 3 的參數組裝  
- Case 6（PostView 替換）與 Case 9（視覺對齊）相互支援  
- Case 7、15（封存頁）依賴 Case 2 的直嵌思路，並延伸效能考量  
- Case 14（逆向端點）可在 Case 2 前並行學習，加深理解  
- Case 10、11、12（佈局/法務）可在主流程完成後進行

• 完整學習路徑：  
1) Case 8 → 1 → 14 → 2 → 6 → 9  
2) Case 3 → 4 → 5 → 13（完成推文參數全鏈路）  
3) Case 7 → 15（清單頁整合與效能策略）  
4) Case 10 → 11 → 12（版面與政策收尾）

此學習路徑從策略（選型/治理）入手，進入整合核心（直嵌/參數/視覺），再擴展到清單頁效能，最後完善版面與合規，形成完整實戰閉環。