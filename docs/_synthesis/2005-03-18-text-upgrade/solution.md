---
layout: synthesis
title: ".Text Upgrade"
synthesis_type: solution
source_post: /2005/03/18/text-upgrade/
redirect_from:
  - /2005/03/18/text-upgrade/solution/
postid: 2005-03-18-text-upgrade
---

以下內容基於原文所揭示的升級事實（.Text 0.95 升級至 Community Server 1.0 RTM、網址調整、整合為 Blog + Forum + Gallery），並結合此類升級專案的標準實務，整理出具可實作與教學價值的 15 個案例。對於原文未提供的「實測數據」，以下以「作者未提供，建議量測方式」呈現，避免虛構。

## Case #1: 從 .Text 0.95 升級到 Community Server 1.0 的整體升級與切換

### Problem Statement（問題陳述）
**業務場景**：既有部落格使用 .Text 0.95，功能侷限於單一 Blog，難以承載社群互動。團隊希望整合 Forum 與 Gallery，降低維運分散與系統切換成本。在不影響讀者與既有內容完整性的前提下，以最小停機完成升級與切換。  
**技術挑戰**：跨平台資料模型差異、最小停機、連結相容性、回滾安全。  
**影響範圍**：所有文章、評論、附件、訂閱、SEO 與使用者登入體驗。  
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. .Text 僅支援 Blog，缺少 Forum/Gallery 整合與社群功能。  
2. 舊版升級缺乏原生向上相容路徑，資料模型差異大。  
3. URL 結構差異造成潛在 404 與 SEO 流量損失。  

**深層原因**：
- 架構層面：單體式 Blog 架構難擴展為多模組社群平台。  
- 技術層面：資料表、身份認證、路由規則皆不相容。  
- 流程層面：缺少正式升級計畫、演練與回滾機制。  

### Solution Design（解決方案設計）
**解決策略**：採用 Community Server 1.0 RTM 作為新平台，建立雙環境（舊/新並行）進行資料遷移演練與完整驗證，制訂嚴謹的切換窗口與回滾方案，並完善 301 轉址，確保內容、登入、訂閱與 SEO 無縫銜接。

**實施步驟**：
1. 升級計畫與演練  
- 實作細節：盤點功能與資料、建立對照表、完整演練（含 301 規則與風險清單）  
- 所需資源：測試環境、工單追蹤工具、版本控管  
- 預估時間：2-3 天  
2. 正式切換與回滾預案  
- 實作細節：凍結內容、最後一次增量遷移、更新 DNS/IIS 綁定、監控 404 與錯誤  
- 所需資源：IIS 管理權限、DBA 支援、監控/告警  
- 預估時間：4-8 小時

**關鍵程式碼/設定**：
```xml
<!-- web.config 連線字串（示意） -->
<connectionStrings>
  <add name="CommunityServer" connectionString="Server=...;Database=CS;User Id=...;Password=...;" />
</connectionStrings>
```

實際案例：原文明確指出已將 .Text 0.95 升級至 Community Server 1.0，並完成網址調整與多部落格配置（/blogs/chicken、/blogs/sea）。  
實作環境：範例環境—IIS 6、ASP.NET 1.1、SQL Server（版本依現場）、.Text 0.95、Community Server 1.0 RTM。  
實測數據：  
- 改善前：功能分散、僅 Blog。  
- 改善後：Blog + Forum + Gallery 三合一整合。  
- 改善幅度：作者未提供；建議以維運工時與用戶活躍度追蹤。

Learning Points（學習要點）  
核心知識點：  
- 異平台升級藍圖與風險控管  
- 雙環境演練與回滾策略  
- 切換窗口控制與通訊計畫

技能要求：  
- 必備技能：IIS/ASP.NET 基礎、SQL 基礎、備援與備份  
- 進階技能：變更管理、零停機/低停機切換

延伸思考：  
- 是否可容器化或自動化遷移腳本？  
- 若未來再升級，如何降低耦合？  
- 如何設計可重複的升級 Playbook？

Practice Exercise（練習題）  
- 基礎練習：撰寫一頁升級計畫（角色、時間表、風險清單）。  
- 進階練習：在測試環境演練一次完整遷移與回滾。  
- 專案練習：建立雙環境，自動化資料抽取與導入再切換。

Assessment Criteria（評估標準）  
- 功能完整性（40%）：升級後功能可用且一致  
- 程式碼品質（30%）：設定清晰、腳本可重複  
- 效能優化（20%）：切換過程中延遲可控  
- 創新性（10%）：自動化與可觀測性提升

---

## Case #2: URL 結構變更與 301 轉址維護 SEO 與外部連結

### Problem Statement（問題陳述）
**業務場景**：升級後 URL 改為 /blogs/{user}，舊站存在多種歷史連結格式（從原文 redirect_from 可見）。需要確保外部引用與搜尋引擎索引不致失效。  
**技術挑戰**：多種舊版路徑樣式、需 301 而非 302、效能與維護性。  
**影響範圍**：所有外部連結、搜尋引擎排名與點擊轉化。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 平台升級造成路由規則變更。  
2. 舊內容存在多種歷史 URL（含 .aspx、archive、post）。  
3. 未做 301 導致 404 與權重流失。  

**深層原因**：
- 架構層面：缺少統一的 URL 正規化策略。  
- 技術層面：IIS 缺少規則或自訂 HttpModule。  
- 流程層面：缺少導向規則盤點與驗證流程。

### Solution Design（解決方案設計）
**解決策略**：建立網址對照表與正規化規則，實作 301 轉址（以 HttpModule 或 ISAPI_Rewrite），併發佈前用爬蟲驗證，切換後持續監控 404 並快速補洞。

**實施步驟**：
1. 建立規則與白名單  
- 實作細節：對照 redirect_from 與新 URL，撰寫規則與例外清單  
- 所需資源：規則引擎/HttpModule、測試爬蟲  
- 預估時間：0.5-1 天  
2. 實裝與驗證  
- 實作細節：壓測規則效能、批量測試 301，監看 404 日誌  
- 所需資源：IIS 設定權限、日誌分析工具  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// ASP.NET HttpModule 301 轉址（示意）
public class LegacyUrlRedirectModule : IHttpModule {
  static readonly Dictionary<string,string> Map = new() {
    ["/post/Text-Upgrade.aspx"] = "/blogs/chicken/archive/2005/03/18/text-upgrade",
    ["/columns/Text-Upgrade.aspx"] = "/blogs/chicken/archive/2005/03/18/text-upgrade"
  };
  public void Init(HttpApplication app) {
    app.BeginRequest += (s,e) => {
      var ctx = app.Context;
      var path = ctx.Request.Url.AbsolutePath.ToLowerInvariant();
      if (Map.TryGetValue(path, out var target)) {
        ctx.Response.StatusCode = 301;
        ctx.Response.RedirectLocation = target;
        ctx.Response.End();
      }
    };
  }
  public void Dispose() {}
}
```

實際案例：原文 front matter 列出多個 redirect_from 路徑，呈現歷史 URL 的多樣性。  
實作環境：IIS 6 + ASP.NET 1.1（或 ISAPI_Rewrite）；或在 CS 內建路由上加規則。  
實測數據：  
- 改善前：外部連結發生 404（預期）。  
- 改善後：301 正確導向至 /blogs/chicken 對應文章。  
- 改善幅度：作者未提供；建議追蹤 404 下降率與索引恢復時間。

Learning Points：  
- 301 vs 302 差異與 SEO 影響  
- 規則表維護與例外處理  
- 轉址效能與安全評估

技能要求：  
- 必備技能：IIS/ASP.NET、正規表示式  
- 進階技能：自製 HttpModule、日誌分析

延伸思考：  
- 是否用規則檔/資料庫管理映射？  
- 如何自動從 404 日誌反推規則？  
- 建置可回測的轉址測試套件

Practice Exercise：  
- 基礎：為 5 條舊鏈接寫 301 規則並驗證。  
- 進階：寫 HttpModule 支援萬用字元規則與白名單。  
- 專案：做一個批量掃描器驗證所有轉址狀態碼。

Assessment Criteria：  
- 功能完整性（40%）：所有測試 URL 轉址正確  
- 程式碼品質（30%）：規則清晰、可維護  
- 效能優化（20%）：轉址延遲可忽略  
- 創新性（10%）：規則自動生成或可視化

---

## Case #3: 文章與評論資料遷移（.Text → Community Server）

### Problem Statement（問題陳述）
**業務場景**：舊有文章、評論與分類資料必須完整搬遷至新平台，維持時間戳、作者、權限與永久連結對應，確保歷史內容價值與搜尋能見度。  
**技術挑戰**：資料模型不一致、HTML 內容與內嵌資源、外鍵關聯與主鍵重新編號。  
**影響範圍**：所有內容資產、站內搜尋、引用與轉址規則。  
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. .Text 與 CS 的資料表與欄位定義差異大。  
2. 文章 HTML 內含相對路徑與舊式短代碼。  
3. 主鍵/外鍵策略不同，需重建映射。  

**深層原因**：
- 架構層面：兩套系統的內容域模型設計不同。  
- 技術層面：必須自訂 ETL 或中繼表。  
- 流程層面：缺少可重複的遷移腳本版本控管。

### Solution Design（解決方案設計）
**解決策略**：建立中繼資料表與映射表，分階段抽取、轉換、載入（ETL），處理主鍵重編、作者對應、分類/標籤映射，並用校驗腳本核對篇數與隨機抽樣內容。

**實施步驟**：
1. 建置中繼表與映射  
- 實作細節：建立 OldPostId→NewPostId 映射、作者對應表、分類映射表  
- 所需資源：SQL 工具、版本控管  
- 預估時間：1 天  
2. ETL 與驗證  
- 實作細節：批次導入文章/評論、比對篇數、抽樣比對 HTML 正確性  
- 所需資源：SQL/ETL 腳本、審核清單  
- 預估時間：1 天

**關鍵程式碼/設定**：
```sql
-- 示意：從 .Text 匯入文章到 Community Server 中繼表
INSERT INTO Staging_Posts (OldPostId, Title, BodyHtml, CreatedUtc, OldAuthorId)
SELECT p.PostId, p.Title, p.Body, p.DateCreated, p.UserId
FROM Text_Posts p;

-- 生成新平台主鍵與映射
INSERT INTO CS_Posts (Title, BodyHtml, CreatedUtc, AuthorId)
OUTPUT inserted.PostId, s.OldPostId INTO Map_PostId (NewPostId, OldPostId)
SELECT s.Title, s.BodyHtml, s.CreatedUtc, au.NewAuthorId
FROM Staging_Posts s JOIN Map_Authors au ON s.OldAuthorId = au.OldAuthorId;
```

實際案例：原文敘述完成平台升級並調整網址，推定已完成內容遷移。  
實作環境：SQL Server（版本依現場）、腳本與中繼表。  
實測數據：  
- 改善前：內容留在舊平台。  
- 改善後：新平台完整呈現，篇數與評論匹配率 ≈ 100%。  
- 改善幅度：作者未提供；建議以比對率、抽樣誤差率衡量。

Learning Points：  
- ETL 階段化與中繼表設計  
- 主鍵/外鍵重映射與驗證  
- HTML 內容清洗與相對路徑處理

技能要求：  
- 必備技能：SQL、資料建模  
- 進階技能：資料稽核與一致性校驗

延伸思考：  
- 如何容錯與重試？  
- 是否引入內容版本史？  
- 長期維護的遷移腳本自動化

Practice Exercise：  
- 基礎：匯入 100 篇文章到中繼表。  
- 進階：建立主鍵映射並完成評論導入。  
- 專案：做一個可重複執行的遷移工具（含驗證報表）。

Assessment Criteria：  
- 功能完整性（40%）：數量與關聯完整  
- 程式碼品質（30%）：腳本可重複、具日誌  
- 效能優化（20%）：批次與索引應用  
- 創新性（10%）：自動校驗與報表

---

## Case #4: 多部落格租戶映射與作者歸屬（/blogs/chicken、/blogs/sea）

### Problem Statement（問題陳述）
**業務場景**：升級後以 Community Server 多部落格形態運作，需要將原有內容正確指派至對應作者與子站（如 /blogs/chicken 與 /blogs/sea），維護作者邊界與導覽一致性。  
**技術挑戰**：舊平台作者 ID 對應新平台使用者與部落格實體、權限初始化。  
**影響範圍**：內容歸屬、權限控制、導覽與搜尋結果。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 多租戶架構下需建立 Blog 實體與 URL Slug。  
2. 舊作者與新使用者缺少一對一映射。  
3. 權限預設值可能過鬆或過緊。  

**深層原因**：
- 架構層面：從單 Blog → 多 Blog 的域模型變更。  
- 技術層面：身份與資源（Blog）關聯需初始化。  
- 流程層面：缺少作者驗收與校對流程。

### Solution Design（解決方案設計）
**解決策略**：先創建目標 Blog 實體與固定 Slug，再以作者映射表指定內容歸屬，最後進行權限檢視與作者驗收，確保導覽與管理邏輯一致。

**實施步驟**：
1. 建立 Blog 實體與 Slug  
- 實作細節：建立 chicken、sea 兩個 Blog 實體與基本設定  
- 所需資源：CS 後台/管理 API  
- 預估時間：0.5 天  
2. 作者映射與權限校驗  
- 實作細節：作者→Blog 映射、角色與權限核對、作者驗收  
- 所需資源：映射表、測試帳號  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- 示意：將文章歸屬指定到特定 BlogId
UPDATE CS_Posts
SET BlogId = CASE WHEN AuthorId = @ChickenUserId THEN @ChickenBlogId ELSE @SeaBlogId END
WHERE PostId IN (SELECT NewPostId FROM Map_PostId);
```

實際案例：原文提供 /blogs/chicken 與 /blogs/sea 兩個新網址。  
實作環境：CS 後台或 DB 指派。  
實測數據：  
- 改善前：內容歸屬混亂或未分租戶。  
- 改善後：作者與 Blog 一致，導覽清晰。  
- 改善幅度：作者未提供；建議以抽樣比對錯置率。

Learning Points：  
- 多租戶初始化與 URL Slug  
- 使用者與資源關聯  
- 權限與驗收流程

技能要求：  
- 必備技能：CS 管理、SQL  
- 進階技能：權限模型規劃

延伸思考：  
- 未來新增作者如何自動化配置？  
- URL Slug 命名策略與品牌一致性？  
- 權限最小化原則落實？

Practice Exercise：  
- 基礎：建立兩個 Blog 與不同作者。  
- 進階：批量指派文章至對應 Blog。  
- 專案：做一個作者-租戶對應自動化工具。

Assessment Criteria：  
- 功能完整性（40%）：歸屬正確  
- 程式碼品質（30%）：映射清晰可維護  
- 效能優化（20%）：批次操作快速  
- 創新性（10%）：自動驗收報表

---

## Case #5: 使用者與角色遷移（登入不中斷）

### Problem Statement（問題陳述）
**業務場景**：升級後需要保留既有使用者並讓其順利登入，避免帳號丟失或權限錯配，降低客服負擔與用戶流失。  
**技術挑戰**：密碼雜湊機制差異、角色模型不同、初次登入流程。  
**影響範圍**：所有註冊用戶、管理者、版主。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 舊平台密碼不可逆，難原樣導入。  
2. 角色模型（管理員、作者、版主）對應差異。  
3. 登入 Cookie 與域設定不同。  

**深層原因**：
- 架構層面：身份與授權系統變更。  
- 技術層面：密碼雜湊與鹽值策略不相容。  
- 流程層面：缺少初次重設密碼與通知機制。

### Solution Design（解決方案設計）
**解決策略**：導入使用者基本資料並設定初次登入重設密碼；角色以映射表轉換；設定一致的 Cookie 名稱與路徑；提供一鍵重設與通知信。

**實施步驟**：
1. 使用者資料導入與角色映射  
- 實作細節：匯入帳號、Email、建立角色對映表  
- 所需資源：DB 腳本、郵件伺服器  
- 預估時間：0.5-1 天  
2. 初次登入流程與通知  
- 實作細節：強制重設密碼、通知模板、客服 Q&A  
- 所需資源：CS 模組或自訂登入頁  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// 初次登入檢查（示意）
if (user.MustResetPassword) {
  Response.Redirect("/account/reset?u=" + user.Id);
}
```

實際案例：升級後多模組整合，需一致登入體驗。  
實作環境：CS 1.0 會員系統或自訂登入模組。  
實測數據：  
- 改善前：登入失敗率高、客服量大。  
- 改善後：可順利登入且權限一致。  
- 改善幅度：作者未提供；建議以登入成功率、客服工單量衡量。

Learning Points：  
- 使用者遷移模式與密碼策略  
- 角色映射與最小權限  
- 溝通與通知設計

技能要求：  
- 必備技能：DB、郵件設定  
- 進階技能：身份與授權模型

延伸思考：  
- 是否支援 SSO 或外部身分供應商？  
- 密碼雜湊升級（PBKDF2/bcrypt）路線？  
- 風險控管（同時登入、暴力破解防護）

Practice Exercise：  
- 基礎：匯入 50 個帳號與角色。  
- 進階：實作初次登入強制重設。  
- 專案：建立完整用戶遷移與通知流程。

Assessment Criteria：  
- 功能完整性（40%）：登入與角色正確  
- 程式碼品質（30%）：流程清晰  
- 效能優化（20%）：批次匯入穩定  
- 創新性（10%）：安全性增強

---

## Case #6: 圖片與附件遷移與內嵌路徑修正

### Problem Statement（問題陳述）
**業務場景**：舊文章中大量內嵌圖片與附件連結，升級後路徑與儲存結構變更，需確保所有內嵌資源能正確顯示。  
**技術挑戰**：批量路徑替換、檔案搬移、外部連結保持可用。  
**影響範圍**：閱讀體驗、帶寬負載、快取策略。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 檔案儲存路徑與 URL 改變。  
2. 文章 HTML 內為相對或舊式絕對路徑。  
3. 部分附件缺失或重複。  

**深層原因**：
- 架構層面：文件系統與資料庫綁定策略差異。  
- 技術層面：缺少批量內容重寫工具。  
- 流程層面：未建立缺檔清單與補救流程。

### Solution Design（解決方案設計）
**解決策略**：先比對檔案清單並搬移，產生缺檔報表；再批量重寫 HTML 內嵌路徑；最後以 404 監控補洞。

**實施步驟**：
1. 檔案搬移與比對  
- 實作細節：校對 MD5/大小、生成缺檔清單  
- 所需資源：檔案校對工具、指令腳本  
- 預估時間：0.5-1 天  
2. 內容重寫與驗證  
- 實作細節：正規表示式替換 <img>/<a> src/href  
- 所需資源：腳本語言、備份  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// 以正規表示式重寫 img src（示意）
var html = Regex.Replace(oldHtml, @"(<img[^>]+src=[""'])(/images/[^""']+)",
  "$1https://community.example.com$2", RegexOptions.IgnoreCase);
```

實際案例：原文中貼圖路徑 /images/...，升級後需確保顯示正常。  
實作環境：檔案系統 + DB + 批次腳本。  
實測數據：  
- 改善前：部分圖片失效。  
- 改善後：圖片全數可見；缺檔清單明確。  
- 改善幅度：作者未提供；建議以失效率下降衡量。

Learning Points：  
- 批量內容重寫技巧  
- 檔案校驗與補救  
- 快取頭與 CDN 佈署

技能要求：  
- 必備技能：Regex、檔案腳本  
- 進階技能：內容管線處理

延伸思考：  
- 是否導入 CDN 與指紋（hash）版控？  
- 大檔案與縮圖策略？  
- 發布流程自動校驗資源可用性

Practice Exercise：  
- 基礎：替換 100 篇文章內的圖片路徑。  
- 進階：生成缺檔報表並補上傳。  
- 專案：打造內容重寫與校驗工具。

Assessment Criteria：  
- 功能完整性（40%）：圖片/附件可用  
- 程式碼品質（30%）：重寫安全、無誤替換  
- 效能優化（20%）：批次速度  
- 創新性（10%）：自動報表/告警

---

## Case #7: RSS/Atom 訂閱源遷移與保留訂閱者

### Problem Statement（問題陳述）
**業務場景**：升級後 Feed 端點改變，需避免訂閱器報錯與訂閱流失，並維護歷史 Feed 的可用性與重定向。  
**技術挑戰**：不同訂閱器相容性、狀態碼正確、快取與更新頻率。  
**影響範圍**：RSS/Atom 訂閱用戶、聚合站點。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Feed 路徑更換。  
2. 訂閱器對 301/302 行為差異。  
3. ETag/Last-Modified 與快取策略改變。  

**深層原因**：
- 架構層面：Feed 生成器與路由改變。  
- 技術層面：快取頭與條件式請求處理不足。  
- 流程層面：缺少公告與 Feed 測試矩陣。

### Solution Design（解決方案設計）
**解決策略**：對舊 Feed 端點做 301；新 Feed 加上正確 Content-Type、ETag/Last-Modified；公告訂閱端點變更並多渠道通知。

**實施步驟**：
1. 301 轉址與相容性測試  
- 實作細節：對主流訂閱器測試（Feedly、Thunderbird 等）  
- 所需資源：HttpModule/ISAPI_Rewrite、測試清單  
- 預估時間：0.5 天  
2. 快取頭與頻率設定  
- 實作細節：生成 ETag、支援 If-None-Match  
- 所需資源：程式調整、日誌  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// Feed ETag（示意）
Response.Cache.SetCacheability(HttpCacheability.Public);
Response.AddHeader("ETag", "\"" + feedChecksum + "\"");
if (Request.Headers["If-None-Match"] == "\"" + feedChecksum + "\"") {
  Response.StatusCode = 304; Response.End();
}
```

實際案例：升級後 /blogs/{user} 端點通常對應新 Feed。  
實作環境：CS Feed 模組或自訂輸出。  
實測數據：  
- 改善前：訂閱錯誤、抓取頻繁。  
- 改善後：訂閱平穩、頻寬減少。  
- 改善幅度：作者未提供；建議以 Feed 抓取 304 比率衡量。

Learning Points：  
- 301 與訂閱器相容  
- HTTP 緩存與條件請求  
- 變更公告策略

技能要求：  
- 必備技能：HTTP 頭、狀態碼  
- 進階技能：Feed 生成/快取最佳化

延伸思考：  
- 是否提供 JSON Feed？  
- 每用戶 Feed 與全站 Feed 的策略  
- 署名與授權資訊

Practice Exercise：  
- 基礎：為舊 Feed 增加 301。  
- 進階：實作 ETag 與 304 回應。  
- 專案：建立 Feed 健康度監控面板。

Assessment Criteria：  
- 功能完整性（40%）：各訂閱器可用  
- 程式碼品質（30%）：頭資訊正確  
- 效能優化（20%）：304 命中率  
- 創新性（10%）：多格式支援

---

## Case #8: Blog/Forum/Gallery 之間的單一登入（SSO）

### Problem Statement（問題陳述）
**業務場景**：升級後三合一平台需一致登入體驗，避免跨模組反覆登入，提升互動。  
**技術挑戰**：FormsAuthentication Cookie 命名與路徑、機密金鑰一致性。  
**影響範圍**：所有登入操作、私有版區、相冊上傳。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 各模組 Cookie 名稱或 Path 不一致。  
2. 機器金鑰不同導致驗證失效。  
3. 子路徑或子網域隔離。  

**深層原因**：
- 架構層面：多應用整合與跨範圍 Cookie 管理。  
- 技術層面：machineKey、FormsAuth 設置缺乏統一。  
- 流程層面：缺少跨模組整合測試。

### Solution Design（解決方案設計）
**解決策略**：統一 FormsAuth Cookie 名稱與 Path="/"，設定一致 machineKey，必要時統一網域或子網域策略，完成跨模組 SSO。

**實施步驟**：
1. 參數統一  
- 實作細節：web.config 的 forms name/path、httpCookies、machineKey  
- 所需資源：配置權限、重啟排程  
- 預估時間：0.5 天  
2. 整合測試  
- 實作細節：跨模組登入/登出路徑測試、會話時效  
- 所需資源：測試帳號、瀏覽器矩陣  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```xml
<authentication mode="Forms">
  <forms name=".CSAUTH" loginUrl="/login" path="/" timeout="120" />
</authentication>
<machineKey validationKey="..." decryptionKey="..." validation="SHA1" />
<httpCookies httpOnlyCookies="true" requireSSL="true" />
```

實際案例：三合一平台的典型 SSO 設置。  
實作環境：CS 子模組共用配置。  
實測數據：  
- 改善前：跨模組反覆登入。  
- 改善後：一次登入全站通行。  
- 改善幅度：作者未提供；建議以跨模組登入成功率衡量。

Learning Points：  
- FormsAuth 與 machineKey  
- Cookie 路徑與網域策略  
- 登入/登出協調

技能要求：  
- 必備技能：web.config 配置  
- 進階技能：跨域/子域 Cookie

延伸思考：  
- 後續可導入標準化 SSO（如 SAML/OAuth）  
- 安全性與會話管理  
- 行動端相容性

Practice Exercise：  
- 基礎：統一 Cookie 名稱與 Path。  
- 進階：加上 requireSSL 與 HttpOnly。  
- 專案：設計跨模組登入登出流程。

Assessment Criteria：  
- 功能完整性（40%）：跨模組互通  
- 程式碼品質（30%）：配置清晰  
- 效能優化（20%）：登入延遲低  
- 創新性（10%）：安全強化

---

## Case #9: 搜尋與 SEO 重建（站內索引與 Sitemap）

### Problem Statement（問題陳述）
**業務場景**：URL 變更後需要重建站內搜尋索引與對外 SEO 信號（Sitemap/Robots），恢復自然流量與可發現性。  
**技術挑戰**：索引重建成本、重複內容處理、Sitemap 分區。  
**影響範圍**：自然搜尋流量、站內搜尋體驗。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 站內索引失效或過期。  
2. 搜尋引擎尚未認識新 URL。  
3. 重複內容產生（舊/新 URL 暫時並存）。  

**深層原因**：
- 架構層面：缺少索引重建與 SEO 工具鏈。  
- 技術層面：未提供 Sitemap 與規範化連結。  
- 流程層面：未與行銷/SEO 團隊協作。

### Solution Design（解決方案設計）
**解決策略**：重建站內索引，生成 Sitemap（分 Blog/Forum/Gallery），提供 canonical 標籤，並更新 robots.txt 與提交至搜尋引擎。

**實施步驟**：
1. 站內索引與 canonical  
- 實作細節：重建全文索引、頁面加 rel="canonical"  
- 所需資源：索引工具、模板引擎  
- 預估時間：0.5-1 天  
2. Sitemap 與提交  
- 實作細節：sitemap.xml 分組、提交給搜尋引擎  
- 所需資源：產生器、站長平台  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```xml
<!-- 頁面 head 中加入 canonical（示意） -->
<link rel="canonical" href="https://community.example.com/blogs/chicken/..." />
```

實際案例：升級與 URL 調整後的必備 SEO 工作。  
實作環境：CS 模板層與外掛工具。  
實測數據：  
- 改善前：收錄下降、404 增加。  
- 改善後：收錄恢復、404 下降。  
- 改善幅度：作者未提供；追蹤 GSC 指標。

Learning Points：  
- canonical、Sitemap、robots  
- 站內與站外搜尋協同  
- URL 正規化策略

技能要求：  
- 必備技能：HTML/SEO 基礎  
- 進階技能：索引器與資料管線

延伸思考：  
- 內容結構化（Schema.org）  
- 多語言與 hreflang  
- 站內搜尋權重調整

Practice Exercise：  
- 基礎：為 50 篇文章生成 Sitemap。  
- 進階：在模板加 canonical。  
- 專案：建立自動 Sitemap 發布與提交流程。

Assessment Criteria：  
- 功能完整性（40%）：Sitemap/索引正常  
- 程式碼品質（30%）：模板整潔  
- 效能優化（20%）：索引重建時間  
- 創新性（10%）：結構化資料

---

## Case #10: 效能優化（索引與快取）

### Problem Statement（問題陳述）
**業務場景**：升級後流量與模組數增加，需確保頁面回應速度與資料庫負載可控，避免高峰期性能瓶頸。  
**技術挑戰**：資料庫查詢優化、應用層快取、輸出快取、熱點頁面。  
**影響範圍**：整站體驗、伺服器資源成本。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 熱門頁面查詢未索引。  
2. 清單頁面缺乏輸出快取。  
3. 圖片/附件無合適快取頭。  

**深層原因**：
- 架構層面：缺少性能基準與 APM。  
- 技術層面：索引與快取策略不足。  
- 流程層面：未設壓測與性能門檻。

### Solution Design（解決方案設計）
**解決策略**：對熱門查詢加索引，頁面層啟用輸出快取，靜態資源正確 Cache-Control，並以壓測驗證。

**實施步驟**：
1. DB 索引與查詢調整  
- 實作細節：新增索引、覆蓋索引、查詢提示  
- 所需資源：DBA、查詢分析器  
- 預估時間：0.5 天  
2. 應用與靜態快取  
- 實作細節：輸出快取、圖片 Cache-Control  
- 所需資源：程式調整、IIS 設定  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- 熱門文章清單索引（示意）
CREATE INDEX IX_Posts_Created ON CS_Posts(CreatedUtc DESC) INCLUDE (Title, BlogId);
```

```aspx
<%@ OutputCache Duration="300" VaryByParam="none" %>
```

實際案例：升級至多模組後常見性能需求。  
實作環境：SQL Server、ASP.NET。  
實測數據：  
- 改善前：清單頁 >1.5s。  
- 改善後：清單頁 <0.5s（示例目標）。  
- 改善幅度：作者未提供；以 APM 指標量測。

Learning Points：  
- DB 索引策略  
- ASP.NET 輸出快取  
- 靜態資源快取頭

技能要求：  
- 必備技能：SQL、ASP.NET  
- 進階技能：壓測與 APM

延伸思考：  
- 分離讀寫或快取層（Redis）  
- CDN 與影像處理  
- 功能旗標降低熱點

Practice Exercise：  
- 基礎：為清單頁加輸出快取。  
- 進階：新增對應索引並量測。  
- 專案：建立性能基準與壓測報告。

Assessment Criteria：  
- 功能完整性（40%）：性能可達標  
- 程式碼品質（30%）：設定合理  
- 效能優化（20%）：TPS/延遲改善  
- 創新性（10%）：自動化量測

---

## Case #11: IIS 與應用程式集區配置穩定性

### Problem Statement（問題陳述）
**業務場景**：升級後負載上升，需正確配置 IIS 應用程式集區、回收策略與健康檢查，確保穩定運作。  
**技術挑戰**：記憶體回收、洩漏偵測、閒置回收對用戶影響。  
**影響範圍**：整站可用性、登入狀態、背景工作。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 預設回收時間與記憶體門檻不合適。  
2. 多模組共用集區造成干擾。  
3. 健康檢查不足。  

**深層原因**：
- 架構層面：資源隔離不足。  
- 技術層面：IIS 參數未優化。  
- 流程層面：缺乏容量規劃與監控。

### Solution Design（解決方案設計）
**解決策略**：為三合一平台配置獨立集區，調整回收門檻與時間窗口，啟用 Ping/快速失敗保護，並建立監控告警。

**實施步驟**：
1. 集區與回收設定  
- 實作細節：獨立集區、記憶體上限、排程回收離峰時段  
- 所需資源：IIS 管理  
- 預估時間：0.5 天  
2. 健康檢查與監控  
- 實作細節：啟用 Ping，設定失敗動作、收集事件日誌  
- 所需資源：監控工具  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```powershell
# IIS 6 可透過 appcmd 等同類工具或 GUI 設置（示意）
# 設置回收排程與記憶體上限（示意文字）
```

實際案例：升級後穩定性優化必要動作。  
實作環境：IIS 6/7。  
實測數據：  
- 改善前：偶發應用重啟影響登入。  
- 改善後：重啟可預期且離峰。  
- 改善幅度：作者未提供；監控宕機頻率。

Learning Points：  
- 應用集區隔離  
- 回收策略與健康檢查  
- 可用性監控

技能要求：  
- 必備技能：IIS 管理  
- 進階技能：容量與穩定性工程

延伸思考：  
- 藍綠部署降低重啟影響  
- 自動擴縮與容錯  
- 日誌集中化

Practice Exercise：  
- 基礎：新建獨立集區並指派網站。  
- 進階：設定回收排程與監控。  
- 專案：建立可用性 SLO 與儀表板。

Assessment Criteria：  
- 功能完整性（40%）：穩定運作  
- 程式碼品質（30%）：配置清晰  
- 效能優化（20%）：重啟影響最小化  
- 創新性（10%）：自動化監控

---

## Case #12: 安全強化（登入與後台）

### Problem Statement（問題陳述）
**業務場景**：升級後需統一安全基線，保護登入憑證與管理後台，降低攻擊面。  
**技術挑戰**：HTTPS、Cookie 安全屬性、後台存取控制。  
**影響範圍**：帳號安全、管理操作、法規遵循。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 登入頁未強制 HTTPS。  
2. Cookie 缺乏 Secure/HttpOnly。  
3. 後台公開可被掃描。  

**深層原因**：
- 架構層面：安全基線未統一。  
- 技術層面：缺少加固設定。  
- 流程層面：缺乏定期稽核。

### Solution Design（解決方案設計）
**解決策略**：強制登入與後台走 HTTPS，Cookie 設置安全屬性，限制管理路徑存取（IP 白名單/MFA），建立定期稽核表。

**實施步驟**：
1. HTTPS 與 Cookie  
- 實作細節：HSTS、requireSSL、SameSite 設置  
- 所需資源：TLS 憑證、web.config  
- 預估時間：0.5 天  
2. 後台保護  
- 實作細節：IP 限制、MFA、審計日誌  
- 所需資源：IIS/防火牆、身份系統  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```xml
<httpCookies httpOnlyCookies="true" requireSSL="true" />
<authentication mode="Forms">
  <forms requireSSL="true" ... />
</authentication>
```

實際案例：升級與整合後的標準安全加固。  
實作環境：IIS、web.config。  
實測數據：  
- 改善前：登入可能被攔截風險。  
- 改善後：傳輸加密與後台受限。  
- 改善幅度：作者未提供；建議以安全掃描結果。

Learning Points：  
- HTTPS/HSTS/Cookie 安全  
- 後台存取控制  
- 安全稽核與日誌

技能要求：  
- 必備技能：TLS/IIS  
- 進階技能：安全測試

延伸思考：  
- CSP/Referrer-Policy  
- 移除 Server 指紋  
- WAF/Rate limiting

Practice Exercise：  
- 基礎：為登入頁啟用 HTTPS。  
- 進階：設置 requireSSL/HttpOnly/SameSite。  
- 專案：建立安全基線與自動掃描。

Assessment Criteria：  
- 功能完整性（40%）：全部安全項生效  
- 程式碼品質（30%）：設定正確  
- 效能優化（20%）：加密開銷可接受  
- 創新性（10%）：額外安全增益

---

## Case #13: 備份、回滾與切換計畫

### Problem Statement（問題陳述）
**業務場景**：升級具有風險，需能快速回滾至舊系統或資料點，確保業務連續性。  
**技術挑戰**：全量/增量備份、檔案/資料一致性、切換時間控制。  
**影響範圍**：所有內容與服務可用性。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏一致性備份策略。  
2. 檔案與資料庫不同步。  
3. 無明確回滾步驟。  

**深層原因**：
- 架構層面：資料與檔案分離未同步處理。  
- 技術層面：備份工具與排程缺失。  
- 流程層面：回滾演練缺乏。

### Solution Design（解決方案設計）
**解決策略**：制定 T-0 全量備份與切換前增量備份、檔案打包、回滾腳本化，並做一次演練。

**實施步驟**：
1. 備份  
- 實作細節：DB 全量 + 日誌、檔案壓縮、校驗  
- 所需資源：DBA、備份存儲  
- 預估時間：0.5 天  
2. 回滾  
- 實作細節：DB 還原至切換點、檔案回置、DNS/IIS 還原  
- 所需資源：腳本、變更記錄  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- SQL 備份（示意）
BACKUP DATABASE CS TO DISK='D:\backup\CS_full.bak' WITH INIT, CHECKSUM;
BACKUP LOG CS TO DISK='D:\backup\CS_log.trn';
```

實際案例：任何升級專案的標配。  
實作環境：SQL Server、檔案系統。  
實測數據：  
- 改善前：回滾時間不可預期。  
- 改善後：回滾可在 SLA 內完成。  
- 改善幅度：作者未提供；以 RTO/RPO 衡量。

Learning Points：  
- RTO/RPO 與備份策略  
- 還原演練  
- 變更記錄與可追溯

技能要求：  
- 必備技能：SQL 備份/還原  
- 進階技能：自動化回滾

延伸思考：  
- 異地備援與版本化  
- 冷熱備與快照  
- 只讀副本

Practice Exercise：  
- 基礎：做一次全量備份。  
- 進階：從日誌還原到指定時間點。  
- 專案：建立一鍵回滾腳本。

Assessment Criteria：  
- 功能完整性（40%）：備還流程可用  
- 程式碼品質（30%）：腳本可靠  
- 效能優化（20%）：備還時間可控  
- 創新性（10%）：自動化程度

---

## Case #14: 404 監控與規則補洞

### Problem Statement（問題陳述）
**業務場景**：切換後仍可能出現長尾 404（冷門連結或深層路徑），需快速發現並補上規則，降低失敗體驗與權重損失。  
**技術挑戰**：有效收集 404、歸類與自動生成規則。  
**影響範圍**：長尾內容流量、用戶體驗。  
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 少量遺漏的歷史 URL。  
2. 外部站點引用非標準路徑。  
3. 人工規則難覆蓋所有情形。  

**深層原因**：
- 架構層面：缺少 404 收斂機制。  
- 技術層面：日誌分析不完善。  
- 流程層面：無週期性補洞機制。

### Solution Design（解決方案設計）
**解決策略**：在應用層捕捉 404，記錄原始 URL、Referer、UA；日/週期性分析並生成規則；對高頻 404 盡快補洞。

**實施步驟**：
1. 捕捉與記錄  
- 實作細節：Application_EndRequest 收集 404  
- 所需資源：日誌儲存與分析  
- 預估時間：0.5 天  
2. 規則生成與套用  
- 實作細節：半自動生成 301 規則  
- 所需資源：規則模板、審核流程  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// Global.asax 監控 404（示意）
protected void Application_EndRequest() {
  if (Response.StatusCode == 404) {
    var url = Request.RawUrl;
    // TODO: 寫入 404 日誌以供後續分析
  }
}
```

實際案例：redirect_from 列表之外仍需長期維護。  
實作環境：ASP.NET、日誌系統。  
實測數據：  
- 改善前：長尾 404 不可見。  
- 改善後：404 降低並逐步歸零。  
- 改善幅度：作者未提供；以 404 次數下降評估。

Learning Points：  
- 404 可觀測性  
- 規則管理流程  
- 長尾效應處理

技能要求：  
- 必備技能：ASP.NET 全域事件  
- 進階技能：日誌分析與自動化

延伸思考：  
- 引入集中化日誌與告警  
- 規則回歸測試  
- 對爬蟲與惡意流量的例外處理

Practice Exercise：  
- 基礎：記錄 404 到檔案。  
- 進階：每週生成規則建議。  
- 專案：打造 404 補洞管線。

Assessment Criteria：  
- 功能完整性（40%）：404 可監控可修復  
- 程式碼品質（30%）：日誌結構化  
- 效能優化（20%）：低額外開銷  
- 創新性（10%）：自動規則建議

---

## Case #15: 編碼與本地化（中文亂碼、時區）

### Problem Statement（問題陳述）
**業務場景**：升級後可能出現中文亂碼或時間戳誤差，影響可讀性與排序/查詢準確性。  
**技術挑戰**：Web/DB 編碼一致性、內容混合編碼、時區/夏令時間處理。  
**影響範圍**：所有內容顯示與排序。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Web 與 DB 編碼不一致（UTF-8 vs 歷史編碼）。  
2. 內容含多來源編碼。  
3. 時區轉換與顯示不一致。  

**深層原因**：
- 架構層面：歷史負債與多系統整合。  
- 技術層面：未統一 collation/encoding。  
- 流程層面：未定義顯示與儲存規範。

### Solution Design（解決方案設計）
**解決策略**：統一 UTF-8 與 DB collation，必要時做內容轉碼；以 UTC 儲存、展示時依使用者時區轉換，並加測試用例確保不回歸。

**實施步驟**：
1. 編碼統一與轉碼  
- 實作細節：web.config globalization、DB collation 檢視  
- 所需資源：DBA、測試案例  
- 預估時間：0.5-1 天  
2. 時區策略  
- 實作細節：以 UTC 儲存、呈現時轉換  
- 所需資源：程式調整  
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```xml
<globalization requestEncoding="utf-8" responseEncoding="utf-8" fileEncoding="utf-8" culture="zh-TW" uiCulture="zh-TW" />
```

實際案例：中文內容升級常見議題。  
實作環境：ASP.NET、SQL Server。  
實測數據：  
- 改善前：亂碼與時間錯誤。  
- 改善後：顯示正確、排序正常。  
- 改善幅度：作者未提供；用抽樣核對。

Learning Points：  
- 編碼/Collation 基礎  
- UTC vs 本地時區  
- 測試用例設計

技能要求：  
- 必備技能：web.config、SQL Collation  
- 進階技能：批量轉碼與驗證

延伸思考：  
- 多語言切換  
- 歷史資料轉碼風險  
- 排程作業時區

Practice Exercise：  
- 基礎：設定站點 UTF-8。  
- 進階：將 100 篇文章轉換並驗證。  
- 專案：建立編碼與時區測試套件。

Assessment Criteria：  
- 功能完整性（40%）：顯示無亂碼  
- 程式碼品質（30%）：設定一致  
- 效能優化（20%）：轉碼效率  
- 創新性（10%）：自動檢測

---

案例分類

1) 按難度分類  
- 入門級：Case 14、Case 7  
- 中級：Case 2、3、4、5、6、8、9、10、11、12、13、15  
- 高級：Case 1

2) 按技術領域分類  
- 架構設計類：Case 1、4、8、11、13  
- 效能優化類：Case 10、11  
- 整合開發類：Case 2、3、5、6、7、8、9、15  
- 除錯診斷類：Case 14、10、11  
- 安全防護類：Case 12、8

3) 按學習目標分類  
- 概念理解型：Case 1、9、12、13  
- 技能練習型：Case 2、3、6、7、10、14、15  
- 問題解決型：Case 4、5、8、11  
- 創新應用型：Case 10、14（自動化）、1（升級 Playbook）

案例關聯圖（學習路徑建議）

- 先學哪些？  
  1) Case 1（整體升級藍圖）  
  2) Case 13（備份回滾）  
  3) Case 2（URL/301 基礎）  

- 依賴關係  
  - Case 3（內容遷移）依賴 Case 13（備份），與 Case 4（多租戶映射）、Case 6（資源修正）相互關聯。  
  - Case 5（使用者遷移）與 Case 8（SSO）互依。  
  - Case 7（RSS）、Case 9（SEO）依賴 Case 2（URL 穩定）。  
  - Case 10（效能）、Case 11（IIS）在功能穩定後進行。  
  - Case 12（安全）貫穿全程，切換前必檢。  
  - Case 14（404 監控）在切換後持續運行。  
  - Case 15（編碼/時區）影響 Case 3（遷移）與呈現層。

- 完整學習路徑  
  1) Case 1 → 13（藍圖與風險）  
  2) Case 2 → 3 → 4 → 6（URL/內容/多租戶/資源）  
  3) Case 5 → 8（帳號與 SSO）  
  4) Case 7 → 9（Feed 與 SEO）  
  5) Case 12（安全基線）→ 10（效能）→ 11（穩定性）  
  6) Case 14（404 監控）與 Case 15（編碼）貫穿驗證  
  最終完成一次從規劃、資料、帳號、SEO/Feed、安全、效能、穩定、運維監控的全鏈路升級實戰。