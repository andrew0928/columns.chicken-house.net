---
layout: synthesis
title: "CS Control: Recent Comments"
synthesis_type: solution
source_post: /2006/05/21/cs-control-recent-comments/
redirect_from:
  - /2006/05/21/cs-control-recent-comments/solution/
---

以下內容基於原文的具體脈絡（CS 2.0 改為 Provider Model 與 Theme Model、Post 物件統一承載資料、Theme Control 對應 Skin-*.ascx、邏輯需在 DLL 中完成），萃取並擴充為可教學、可實作的案例。各案例包含問題、根因、解法、實作步驟、示意程式碼與可評估的指標。原文未提供量化數據，實測數據部分提供建議性量化指標，便於教學與評估。

## Case #1: 升級至 CS 2.0 後「最新回應」功能消失的恢復方案

### Problem Statement（問題陳述）
**業務場景**：網站升級至 CS 2.0 後，首頁與側欄缺乏「最新回應（Recent Comments）」功能，使用者無法快速掌握互動動態，造成社群體驗下降與抱怨。需在不破壞 CS 2.0 架構前提下，恢復並穩定提供最新回應顯示。
**技術挑戰**：CS 2.0 改用 Provider Model，無法直接查 DB；Theme Model 引入 Skin-*.ascx 映射，需正確掛載自訂控制。
**影響範圍**：社群互動下降、瀏覽黏著度降低、客服負擔增加。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 架構升級為 Provider Model，原本 1.0 自行改版的直連查詢失效。
2. Theme Model 更動，無法快速找到插入標記位置與掛載方式。
3. Post 物件統一承載多種型別，難以直接取得「只有留言」的資料集。

**深層原因**：
- 架構層面：資料存取抽象化，禁止繞過 Provider。
- 技術層面：Theme Control 與 Skin-*.ascx 對應增加耦合點。
- 流程層面：升級缺少功能回歸清單與遺失功能的補位方案。

### Solution Design（解決方案設計）
**解決策略**：實作一個 RecentComments 伺服器控制（DLL）使用 Provider API 取得資料，於各 Theme 的 Skin-RecentComments.ascx 掛載，並過濾 Post 為 Comment 類型，提供可設定筆數與快取。

**實施步驟**：
1. 建立 RecentComments 伺服器控制
- 實作細節：繼承 WebControl/CompositeControl，提供 Count、CacheMinutes 屬性與 CreateChildControls。
- 所需資源：Visual Studio、C#、CS 2.0 SDK/Assemblies。
- 預估時間：0.5 天

2. 透過 Provider API 取得資料
- 實作細節：使用 DataProvider 取得 Post 清單，過濾為 Comment 類型，按時間排序，Take(N)。
- 所需資源：CS 2.0 DataProvider API 文件。
- 預估時間：0.5 天

3. 在 Theme 中掛載控制
- 實作細節：於各 Theme 新增 Skin-RecentComments.ascx，註冊 TagPrefix 與控制，配置樣式。
- 所需資源：Theme 專案檔、CSS。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// 示意：RecentComments.cs（DLL 內）
public class RecentComments : CompositeControl
{
    public int Count { get; set; } = 10;
    public int CacheMinutes { get; set; } = 5;

    protected override void CreateChildControls()
    {
        var comments = GetRecentComments(Count);
        var ul = new BulletedList();
        foreach (var c in comments)
        {
            ul.Items.Add(new ListItem(
                System.Web.HttpUtility.HtmlEncode($"{c.Author}: {c.Summary}"),
                c.Url));
        }
        Controls.Add(ul);
    }

    private IEnumerable<Post> GetRecentComments(int count)
    {
        var cacheKey = $"RecentComments:{count}";
        var cache = HttpContext.Current.Cache;
        var data = cache[cacheKey] as IEnumerable<Post>;
        if (data == null)
        {
            var all = DataProvider.Instance().GetRecentPosts(count * 3); // 多抓再過濾
            data = all.Where(p => p.Type == PostType.Comment)
                      .OrderByDescending(p => p.CreatedOn)
                      .Take(count)
                      .ToList();
            cache.Insert(cacheKey, data, null,
                DateTime.Now.AddMinutes(CacheMinutes),
                System.Web.Caching.Cache.NoSlidingExpiration);
        }
        return data;
    }
}
```

實際案例：本文作者在 CS 2.0 環境透過 Provider 取回 WeblogPost，並以 Theme 控制 + Skin 映射恢復「最新回應」。
實作環境：CS 2.0、ASP.NET 2.0、C#、Visual Studio 2005。
實測數據：
- 改善前：最新回應不可用（功能覆蓋率 0%）
- 改善後：最新回應可用且可設定筆數（功能覆蓋率 100%）
- 改善幅度：功能可用性 +100%；建議首屏額外渲染時間 < 50ms（快取命中）

Learning Points（學習要點）
核心知識點：
- Provider Model 正確取數，避免直連 DB
- Theme Control 與 Skin-*.ascx 的映射與掛載
- Post 型別過濾策略（只取 Comment）

技能要求：
- 必備技能：C# WebForms、自訂伺服器控制、基本 LINQ/集合操作
- 進階技能：快取策略、可設定性與封裝

延伸思考：
- 這個解決方案還能應用在 Recent Posts、Recent Activities。
- 風險：Provider 介面變動、快取過期策略不當導致資料不一致。
- 可優化：加入權限/審核過濾、併發安全、樣式統一化。

Practice Exercise（練習題）
- 基礎練習：將 Count 改為從 Web.config 讀取（30 分鐘）
- 進階練習：加入 CacheMinutes 與空清快取按鈕（2 小時）
- 專案練習：完成 Recent Activities（留言、回覆、上傳）組合控制（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可設定筆數、正確顯示最新回應
- 程式碼品質（30%）：控制封裝良好、無硬編碼、具註解
- 效能優化（20%）：快取命中下渲染 < 50ms
- 創新性（10%）：支援更多來源與樣式配置

---

## Case #2: 在 CS 2.0 Theme 中定位插入點與掛載流程

### Problem Statement（問題陳述）
**業務場景**：開發者需要在不同 Theme 中顯示相同的「最新回應」元件，但在 Theme Model 下，控制需對應 Skin-*.ascx，且各主題檔案結構不同，難以快速定位與掛載。
**技術挑戰**：理解 Theme Control 與 Skin 檔案的映射關係、正確註冊控制、避免破壞主題佈局。
**影響範圍**：開發效率、主題一致性、維護成本。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 每個 Theme Control 需對應同名 Skin-*.ascx。
2. 不同主題檔位置與命名差異大。
3. 控制註冊與樣式衝突易發生。

**深層原因**：
- 架構層面：Theme 以檔案映射為主，設計上偏靜態掛載。
- 技術層面：User Control、伺服器控制與樣式間耦合多。
- 流程層面：缺少統一掛載流程與文件。

### Solution Design（解決方案設計）
**解決策略**：建立統一掛載規範：控制命名、註冊程式碼片段與 Skin 檔範本，於每個 Theme 一致放置，減少差異與錯誤。

**實施步驟**：
1. 制定命名規則與 Skin 範本
- 實作細節：文件化「Skin-RecentComments.ascx」格式、位置。
- 所需資源：內部維運 Wiki。
- 預估時間：0.5 天

2. 撰寫 Skin 檔並註冊控制
- 實作細節：Register 指示詞、控制標籤、CSS 容器。
- 所需資源：每個 Theme 專案。
- 預估時間：0.5 天/Theme

3. 驗證與視覺調整
- 實作細節：在各 Theme 頁面插入 Skin，視覺微調。
- 所需資源：瀏覽器、F12 工具。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```aspnet
<%@ Control Language="C#" %>
<%@ Register TagPrefix="csx" Namespace="Company.CS.Controls" Assembly="Company.CS.Controls" %>
<div class="sidebar-block recent-comments">
  <h3>最新回應</h3>
  <csx:RecentComments ID="RecentComments1" runat="server" Count="10" CacheMinutes="5" />
</div>
```

實際案例：作者提到 Theme Control 映射至 Skin-*.ascx 並需在 Theme 檔案中引用。
實作環境：CS 2.0 Theme、ASP.NET WebForms。
實測數據：
- 改善前：每次掛載耗時探索 > 60 分鐘
- 改善後：有範本可快速掛載 < 10 分鐘/Theme
- 改善幅度：上線效率 +83%（建議目標）

Learning Points（學習要點）
- Theme Control 與 Skin 的一對一映射機制
- ASCX 註冊與控制標籤使用
- 跨主題一致化策略

技能要求：
- 必備技能：ASCX、WebForms 標記語法
- 進階技能：跨主題樣式抽象與變數化配置

延伸思考：
- 可用 MSBuild/腳本自動複製 Skin 範本。
- 風險：不同主題 CSS 衝突。
- 優化：以基底 CSS 抽離共用樣式。

Practice Exercise
- 基礎：建立一個 Skin-RecentPosts.ascx（30 分鐘）
- 進階：用變數控制標題與圖示（2 小時）
- 專案：工具化一鍵同步 Skin 至所有 Theme（8 小時）

Assessment Criteria
- 功能完整性（40%）：所有 Theme 成功顯示
- 程式碼品質（30%）：註冊與命名規範化
- 效能（20%）：首屏無可感延遲
- 創新（10%）：自動化同步工具

---

## Case #3: 以統一 Post 型別準確過濾出 Comment

### Problem Statement（問題陳述）
**業務場景**：CS 2.0 中 Post 物件同時代表部落格文章、留言、論壇主題、相片等。要做「最新回應」必須只取得留言，否則清單混入非留言項，造成使用者困惑。
**技術挑戰**：理解 Post 的型別標記並正確過濾集合，兼顧效能與正確性。
**影響範圍**：資料正確性、使用者體驗、維護負擔。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Post 為統一型別承載多種資料。
2. Provider 取得的是混合集合。
3. 未加入類型過濾與排序。

**深層原因**：
- 架構層面：以抽象型別簡化接口。
- 技術層面：缺少標準的型別過濾工具方法。
- 流程層面：需求未明確定義要顯示的類型。

### Solution Design（解決方案設計）
**解決策略**：基於 Post.Type（或等價欄位）過濾為 Comment，按時間排序後截取前 N 筆，並增加審核/可見性條件。

**實施步驟**：
1. 確認型別列舉與欄位
- 實作細節：比對 PostType.Comment 值與屬性。
- 所需資源：CS 2.0 API 文件。
- 預估時間：0.25 天

2. 實作過濾與排序
- 實作細節：LINQ/迭代器實作 Where, OrderByDescending, Take。
- 所需資源：程式碼編輯器。
- 預估時間：0.25 天

3. 補強條件
- 實作細節：IsApproved、IsPublic、NotDeleted。
- 所需資源：API 支援。
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```csharp
var comments = posts
    .Where(p => p.Type == PostType.Comment && p.IsApproved && p.IsPublic)
    .OrderByDescending(p => p.CreatedOn)
    .Take(count)
    .ToList();
```

實際案例：原文指出 Post 物件可代表多種資料，需透過 Provider 取回再自行過濾。
實作環境：C#、CS 2.0。
實測數據：
- 改善前：混入 30% 非留言項
- 改善後：100% 皆為留言
- 改善幅度：資料正確率 +30%（建議目標）

Learning Points
- 統一型別下的型別安全與過濾
- 排序與截取的效能考量
- 額外條件（審核/權限）的必要性

Practice Exercise
- 基礎：加入 NotDeleted 條件（30 分鐘）
- 進階：支援來源篩選（部落格/論壇）（2 小時）
- 專案：共用過濾器工具類別（8 小時）

Assessment Criteria
- 功能完整性：過濾正確
- 程式碼品質：可讀性高、具測試
- 效能：Top-N 查詢迅速
- 創新：過濾條件可配置

---

## Case #4: 建立可重用的 RecentComments 控制與 Skin 映射

### Problem Statement（問題陳述）
**業務場景**：同一「最新回應」控制需在多頁面與多 Theme 重複使用，避免重複程式與標記。
**技術挑戰**：設計可重用控制與 Skin 對應，支援樣式客製化。
**影響範圍**：重用性、維護性、開發效率。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 重複複製 ASCX 容易造成維護困難。
2. 標記與邏輯交錯，難以更新。
3. 主題之間樣式差異造成顯示不一致。

**深層原因**：
- 架構層面：Theme 以檔案為單位。
- 技術層面：缺少核心 DLL 控制封裝。
- 流程層面：未建立共用元件策略。

### Solution Design
**解決策略**：將邏輯封裝於 DLL 控制，Skin 只作為掛載與樣式容器；建立控制屬性以支援樣式與數量客製。

**實施步驟**：
1. 封裝 DLL 控制
- 實作細節：屬性化參數（Count、Title、CssClass）。
- 所需資源：C# 專案。
- 預估時間：0.5 天

2. Skin 標記最小化
- 實作細節：僅保留容器與控制標籤。
- 所需資源：Theme 工程。
- 預估時間：0.25 天

3. 樣式對齊
- 實作細節：CSS BEM 命名，對齊主題字體。
- 所需資源：CSS。
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```aspnet
<!-- Skin-RecentComments.ascx -->
<%@ Register TagPrefix="csx" Namespace="Company.CS.Controls" Assembly="Company.CS.Controls" %>
<csx:RecentComments ID="rc" runat="server" Count="8" CssClass="rc-list" />
```

實際案例：作者於 Theme 中引用同名 Skin，控制在 DLL 處理細節。
實作環境：CS 2.0、ASP.NET 2.0。
實測數據：
- 改善前：多處複製易出錯
- 改善後：邏輯集中維護
- 改善幅度：維護工時 -50%（建議目標）

Learning Points
- 控制屬性化設計
- Skin 輕量化策略
- DLL 與 Theme 職責分離

Practice Exercise
- 基礎：新增 Title 屬性，Skin 中顯示（30 分鐘）
- 進階：支援 EmptyTemplate（2 小時）
- 專案：提取共用 BaseListControl（8 小時）

Assessment Criteria
- 功能完整性：可重用、可配置
- 品質：低耦合高內聚
- 效能：無多餘 DOM/回傳
- 創新：模板化擴展

---

## Case #5: 透過 Provider API 取得最新回應清單

### Problem Statement
**業務場景**：不得直連資料庫，只能以 Provider API 正規取得資料，需確保向後相容與升級安全。
**技術挑戰**：熟悉 DataProvider 介面、分頁/排序與型別過濾。
**影響範圍**：穩定性、升級可維護性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. Provider Model 限制直連 DB。
2. API 傳回混合 Post 型別。
3. 缺少既有封裝方法。

**深層原因**：
- 架構：抽象化資料來源。
- 技術：API 學習曲線。
- 流程：無標準存取封裝。

### Solution Design
**解決策略**：撰寫 CommentRepository 封裝 Provider 呼叫，支援 Top-N 與條件過濾。

**實施步驟**：
1. 定義 ICommentService 介面
- 實作細節：GetRecent(int take)。
- 時間：0.25 天

2. 實作 ProviderCommentService
- 實作細節：透過 DataProvider 取資料。
- 時間：0.5 天

3. 封裝過濾與排序
- 實作細節：過濾型別、審核、時間。
- 時間：0.25 天

**關鍵程式碼/設定**：
```csharp
public interface ICommentService {
    IEnumerable<Post> GetRecent(int take);
}

public class ProviderCommentService : ICommentService {
    public IEnumerable<Post> GetRecent(int take) {
        var raw = DataProvider.Instance().GetRecentPosts(take * 3);
        return raw.Where(p => p.Type == PostType.Comment && p.IsApproved)
                  .OrderByDescending(p => p.CreatedOn)
                  .Take(take);
    }
}
```

實際案例：原文明確指出需透過 DataProvider 取得 WeblogPost 型態。
實作環境：CS 2.0、C#。
實測數據：
- 改善前：直連 DB 造成升級風險
- 改善後：完全使用 Provider
- 改善幅度：升級相容性 +100%（建議目標）

Learning Points
- Provider 封裝與測試友善設計
- Top-N 與排序策略
- 依賴反轉促進可測試性

Practice Exercise
- 基礎：加入來源過濾（30 分鐘）
- 進階：支援日期區間查詢（2 小時）
- 專案：抽象為 PostQueryBuilder（8 小時）

Assessment Criteria
- 完整性：封裝提供穩定 API
- 品質：介面清晰、依賴注入
- 效能：O(Take) 遍歷
- 創新：查詢建構器

---

## Case #6: 避免直連資料庫，確保升級相容性

### Problem Statement
**業務場景**：團隊有人建議直連 DB 快速完成，但會破壞 CS 2.0 相容性與維護性。
**技術挑戰**：在時程壓力下平衡速度與架構正確性。
**影響範圍**：升級風險、維運成本。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 不熟 Provider Model 使直連看似更快。
2. 缺少「禁止直連」的工程守則。
3. 無倚賴 Provider 的範例可用。

**深層原因**：
- 架構：資料來源抽象化。
- 技術：學習成本。
- 流程：缺少 code review 檢查點。

### Solution Design
**解決策略**：建立規範與 Linter/Review 清單，強制所有取數經由 Provider 封裝服務，並提供範例程式碼庫。

**實施步驟**：
1. 制定規範與樣板
- 實作細節：禁止使用 SqlConnection/SqlCommand。
- 時間：0.25 天

2. Code Review 檢查點
- 實作細節：PR 模板新增檢查欄位。
- 時間：0.25 天

3. 提供 Provider 範例實作
- 實作細節：供複製的 CommentService。
- 時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// 反面案例（禁止）
/* using (var cn = new SqlConnection(conn)) { ... } */

// 正面案例：透過 Provider
var comments = commentService.GetRecent(10);
```

實際案例：原文提到除非改寫 Data Provider，否則須使用 API。
實作環境：團隊工程規範。
實測數據：
- 改善前：直連 DB 修正頻繁
- 改善後：統一經由 Provider
- 改善幅度：升級改修缺陷 -80%（建議）

Learning Points
- 架構邊界與契約
- 工程規範與治理
- 範例驅動複用

Practice Exercise
- 基礎：撰寫 PR 檢查清單（30 分鐘）
- 進階：Script 搜尋直連代碼（2 小時）
- 專案：建立 Provider 範本庫（8 小時）

Assessment Criteria
- 完整性：規範落地
- 品質：可被工具檢查
- 效能：無拖累
- 創新：自動化檢測

---

## Case #7: 將 UI 與邏輯封裝為 DLL 與 Child Controls

### Problem Statement
**業務場景**：需要在控制內產生列表、標題、連結等 UI，確保可重用與可擴充。
**技術挑戰**：WebForms 生命週期、CreateChildControls、CompositeControl 模式。
**影響範圍**：擴充性、維護性、測試性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 邏輯夾在 ASCX 中不利重用。
2. 需要程式產生子控制以動態渲染。
3. 控制狀態管理（ViewState）需謹慎。

**深層原因**：
- 架構：User Control 不利跨專案重用。
- 技術：WebForms 控制生命週期複雜。
- 流程：缺少封裝範式。

### Solution Design
**解決策略**：使用 CompositeControl，在 CreateChildControls 產生 Repeater 或 BulletedList，並暴露模板事件。

**實施步驟**：
1. 建立 CompositeControl
- 實作細節：Override CreateChildControls。
- 時間：0.5 天

2. 事件/模板化
- 實作細節：ItemDataBound、ITemplate 支援。
- 時間：0.5 天

3. ViewState 最小化
- 實作細節：EnableViewState=false。
- 時間：0.25 天

**關鍵程式碼/設定**：
```csharp
protected override void CreateChildControls()
{
    Controls.Clear();
    var rpt = new Repeater();
    rpt.ItemTemplate = new CommentItemTemplate();
    rpt.DataSource = GetRecentComments(Count);
    rpt.DataBind();
    Controls.Add(rpt);
}
```

實際案例：原文提及「剩下的動作你得自己在 dll 裡處理好」。
實作環境：WebForms、C#。
實測數據：
- 改善前：多處複製 UI 邏輯
- 改善後：集中於 DLL 控制
- 改善幅度：重用度 +70%（建議）

Learning Points
- CompositeControl 模式
- 模板化與事件
- ViewState 控制

Practice Exercise
- 基礎：改為 Repeater 呈現（30 分鐘）
- 進階：加入 Template 支援（2 小時）
- 專案：可插入 Icon/Avatar 的模板（8 小時）

Assessment Criteria
- 完整性：模板可用
- 品質：生命週期正確
- 效能：無過度 ViewState
- 創新：模板擴展點

---

## Case #8: 多 Theme 支援與一致性維護

### Problem Statement
**業務場景**：同一控制需在多主題呈現，確保一致功能與風格調整彈性。
**技術挑戰**：不同 Theme 的 CSS 與版位差異、資源路徑差異。
**影響範圍**：一致性、品牌體驗、維護成本。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. Theme 之間樣式不同。
2. Skin 放置位置不同。
3. 靜態資源路徑不統一。

**深層原因**：
- 架構：以檔案為邊界的主題機制。
- 技術：CSS 命名不統一。
- 流程：缺少多主題清單與同步流程。

### Solution Design
**解決策略**：建立共享樣式基底與主題覆蓋策略，Skin 統一命名與位置，提供 CSS 變數/修飾類。

**實施步驟**：
1. 共用樣式抽離
- 實作細節：base.css + theme override。
- 時間：0.5 天

2. Skin 同步腳本
- 實作細節：批次拷貝/驗證。
- 時間：0.5 天

3. 視覺驗證清單
- 實作細節：不同 Theme 截圖比對。
- 時間：0.5 天

**關鍵程式碼/設定**：
```css
/* base.css */
.rc-list { margin:0; padding:0; list-style:none; }
.rc-list .item { padding:6px 0; border-bottom:1px solid #eee; }
/* theme-dark.css override */
.theme-dark .rc-list .item { border-color:#444; }
```

實測數據（建議）：
- 改善前：每主題需單獨修 1-2 小時
- 改善後：新主題接入 < 20 分鐘
- 改善幅度：效率 +70%

Learning Points
- 基底/覆蓋樣式策略
- Skin 檔案同步
- 跨主題一致性設計

Practice Exercise
- 基礎：提取 base.css（30 分鐘）
- 進階：新增暗色主題覆蓋（2 小時）
- 專案：自動化 Skin 校驗工具（8 小時）

Assessment Criteria
- 完整性：所有主題呈現一致
- 品質：CSS 可維護
- 效能：無多餘資源
- 創新：自動校驗

---

## Case #9: Recent Comments 的快取策略與效能優化

### Problem Statement
**業務場景**：首頁每次載入都呼叫 Provider 取得最新留言，造成不必要負載與延遲。
**技術挑戰**：在資料新鮮度與效能間平衡；快取過期與失效策略。
**影響範圍**：回應時間、後端負載。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 無快取，每次即時查詢。
2. 缺少過期策略。
3. 測試環境未壓測。

**深層原因**：
- 架構：缺少快取層封裝。
- 技術：無統一快取鍵與依賴。
- 流程：未定義新鮮度 SLA。

### Solution Design
**解決策略**：以 HttpRuntime.Cache 設定 3-5 分鐘絕對過期，依 Count 形成鍵；新增手動失效 API 供後台清除。

**實施步驟**：
1. 快取封裝
- 實作細節：CacheKey=RecentComments:{count}。
- 時間：0.25 天

2. 設定過期策略
- 實作細節：絕對過期 5 分鐘。
- 時間：0.25 天

3. 失效 API
- 實作細節：管理頁呼叫 Cache.Remove。
- 時間：0.5 天

**關鍵程式碼/設定**：
```csharp
var cacheKey = $"RecentComments:{count}";
var cached = HttpContext.Current.Cache[cacheKey] as IList<Post>;
if (cached == null) {
    cached = FetchComments(count).ToList();
    HttpContext.Current.Cache.Insert(cacheKey, cached, null,
        DateTime.Now.AddMinutes(5), System.Web.Caching.Cache.NoSlidingExpiration);
}
return cached;
```

實測數據（建議）：
- 改善前：TTFB +120ms（每請求）
- 改善後：TTFB +10ms（快取命中）
- 改善幅度：延遲 -90%，Provider 呼叫減少 90%+

Learning Points
- 絕對/滑動過期
- 快取鍵設計
- 失效策略與管理

Practice Exercise
- 基礎：改用滑動過期（30 分鐘）
- 進階：新增管理端清除快取（2 小時）
- 專案：封裝 ICacheProvider 並可切換 Memory/Redis（8 小時）

Assessment Criteria
- 完整性：快取可用
- 品質：鍵一致、封裝良好
- 效能：命中率 > 80%
- 創新：可插拔快取層

---

## Case #10: Provider 例外處理與 UI 降級

### Problem Statement
**業務場景**：當 Provider 失敗（DB/網路短暫異常）時，頁面需優雅降級，不影響整體瀏覽。
**技術挑戰**：錯誤攔截、備援資料或替代顯示、記錄與告警。
**影響範圍**：穩定性、用戶體驗。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 缺少 try/catch 包裹資料取得。
2. 未提供空狀態 Placeholder。
3. 無錯誤記錄。

**深層原因**：
- 架構：UI 缺少降級設計。
- 技術：例外處理不足。
- 流程：監控缺失。

### Solution Design
**解決策略**：加入例外捕捉、顯示預設訊息、記錄 Log，並可選用前次快取作降級資料。

**實施步驟**：
1. 例外捕捉與日誌
- 實作細節：try/catch + Logger。
- 時間：0.25 天

2. 降級 UI
- 實作細節：EmptyTemplate 或預設訊息。
- 時間：0.25 天

3. 使用舊快取
- 實作細節：快取存在則顯示過期資料。
- 時間：0.25 天

**關鍵程式碼/設定**：
```csharp
IEnumerable<Post> data = null;
try {
    data = GetRecentComments(count);
}
catch (Exception ex) {
    Logger.Error("RecentComments failed", ex);
    data = GetStaleCache(count) ?? Enumerable.Empty<Post>();
}
if (!data.Any()) RenderPlaceholder("暫無可顯示的回應");
```

實測數據（建議）：
- 改善前：錯誤導致區塊空白/崩潰
- 改善後：顯示友善提示或舊資料
- 改善幅度：區塊可用性 99.9%+

Learning Points
- 容錯與降級設計
- 日誌與監控
- 舊快取備援

Practice Exercise
- 基礎：加入 Placeholder（30 分鐘）
- 進階：接入應用程式事件記錄（2 小時）
- 專案：加上告警與健康檢查（8 小時）

Assessment Criteria
- 完整性：錯誤不影響整頁
- 品質：日誌完整
- 效能：降級不增額外延遲
- 創新：備援策略

---

## Case #11: 權限與審核：只顯示可見/已核准留言

### Problem Statement
**業務場景**：需確保首頁不顯示未審核或隱私留言，避免資訊外洩或爭議。
**技術挑戰**：在 Provider 結果中加入權限與審核檢查。
**影響範圍**：合規、安全、信任。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 預設查詢未過濾審核狀態。
2. 權限模型未整合。
3. 顯示層缺少最後把關。

**深層原因**：
- 架構：查詢與權限分離。
- 技術：狀態欄位定義不一致。
- 流程：審核規則未落地到程式。

### Solution Design
**解決策略**：在查詢與呈現雙重過濾 IsApproved、IsPublic、NotDeleted，並加入使用者可見性檢查（若需）。

**實施步驟**：
1. 查詢層過濾
- 實作細節：Where 條件。
- 時間：0.25 天

2. 呈現層再次檢查
- 實作細節：防止錯漏。
- 時間：0.25 天

3. 單元測試
- 實作細節：邊界情況測試。
- 時間：0.5 天

**關鍵程式碼/設定**：
```csharp
var comments = provider.GetRecentPosts(100)
 .Where(p => p.Type == PostType.Comment && p.IsApproved && p.IsPublic && !p.IsDeleted)
 .Take(count);
```

實測數據（建議）：
- 改善前：偶發未審核露出
- 改善後：0 露出事件
- 改善幅度：合規風險 -100%

Learning Points
- 顯示前的權限再檢
- 防禦式編程
- 單元測試保護線

Practice Exercise
- 基礎：加上 IsDeleted 檢查（30 分鐘）
- 進階：權限介面抽象（2 小時）
- 專案：建立審核流程整合（8 小時）

Assessment Criteria
- 完整性：無未審核露出
- 品質：測試完善
- 效能：過濾高效
- 創新：權限抽象

---

## Case #12: 筆數限制與分頁設計降低負載

### Problem Statement
**業務場景**：顯示過多留言影響載入時間與視覺可讀性。
**技術挑戰**：Top-N 截斷與可選分頁/更多連結。
**影響範圍**：效能、體驗。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 一次取太多資料。
2. 無截斷或延遲載入。
3. UI 無更多連結。

**深層原因**：
- 架構：缺少分頁支援。
- 技術：Provider 查詢未優化。
- 流程：需求未定義筆數。

### Solution Design
**解決策略**：預設顯示 Top 10，提供「更多」連結到完整頁；如需分頁，於專屬頁面實作。

**實施步驟**：
1. Top-N 屬性化
- 實作細節：Count 屬性預設 10。
- 時間：0.1 天

2. 更多連結
- 實作細節：MoreUrl 屬性。
- 時間：0.2 天

3. 完整頁分頁（選）
- 實作細節：Skip/Take 或 Provider 支援。
- 時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public string MoreUrl { get; set; } = "/comments";
if (!string.IsNullOrEmpty(MoreUrl))
  Controls.Add(new HyperLink { NavigateUrl = MoreUrl, Text = "更多…" });
```

實測數據（建議）：
- 改善前：首頁載入 800ms
- 改善後：首頁載入 400ms
- 改善幅度：-50%

Learning Points
- Top-N 最佳化
- 導流設計
- 分頁成本轉移

Practice Exercise
- 基礎：新增 MoreUrl（30 分鐘）
- 進階：完整頁分頁（2 小時）
- 專案：Lazy-load（8 小時）

Assessment Criteria
- 完整性：Top-N 與更多連結
- 品質：屬性化良好
- 效能：顯著下降載入時間
- 創新：延遲載入

---

## Case #13: 安全性與 XSS 防護（HTML 編碼）

### Problem Statement
**業務場景**：留言內容可能含惡意腳本，若直接輸出將造成 XSS 風險。
**技術挑戰**：正確編碼作者與摘要、連結處理、安全截斷。
**影響範圍**：安全、信任、法遵。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 未對輸出做 HtmlEncode。
2. 直接輸出原文片段。
3. 未處理長內容。

**深層原因**：
- 架構：顯示層缺少統一安全過濾。
- 技術：編碼與截斷未實作。
- 流程：安全審查缺失。

### Solution Design
**解決策略**：所有動態文字皆 HtmlEncode；摘要先移除標籤再截斷；URL 驗證合法性。

**實施步驟**：
1. 編碼輸出
- 實作細節：HttpUtility.HtmlEncode。
- 時間：0.1 天

2. 安全截斷
- 實作細節：Strip HTML + MaxLength。
- 時間：0.2 天

3. URL 檢查
- 實作細節：只允許 http/https。
- 時間：0.2 天

**關鍵程式碼/設定**：
```csharp
string Safe(string s) => HttpUtility.HtmlEncode(s ?? "");
string Summary(string html, int max) =>
    Safe(Regex.Replace(html ?? "", "<.*?>", "")).Truncate(max);
```

實測數據（建議）：
- 改善前：潛在 XSS 漏洞
- 改善後：0 已知 XSS
- 改善幅度：風險 -100%

Learning Points
- 輸出編碼原則
- 安全截斷與過濾
- URL 白名單

Practice Exercise
- 基礎：套用 HtmlEncode（30 分鐘）
- 進階：Strip + Truncate（2 小時）
- 專案：集中安全工具類別（8 小時）

Assessment Criteria
- 完整性：所有輸出安全
- 品質：工具化
- 效能：低成本
- 創新：安全中介層

---

## Case #14: 可測試性設計：介面抽象與依賴注入

### Problem Statement
**業務場景**：Theme 控制難以測試，需要將資料取得與 UI 分離，實現單元測試與模擬。
**技術挑戰**：抽象資料服務、注入依賴、建立假資料。
**影響範圍**：品質、回歸穩定性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 控制直接呼叫 Provider。
2. 缺少介面抽象。
3. 無測試替身。

**深層原因**：
- 架構：UI 與資料耦合。
- 技術：無 DI 容器。
- 流程：未納入測試策略。

### Solution Design
**解決策略**：引入 ICommentService 作為控制依賴，於控制提供屬性注入或建構注入（在 WebForms 可用屬性注入），測試時以 Fake 實作提供資料。

**實施步驟**：
1. 定義服務介面
- 實作細節：GetRecent。
- 時間：0.25 天

2. 控制屬性注入
- 實作細節：public ICommentService Service {get;set;}
- 時間：0.25 天

3. 單元測試
- 實作細節：注入 Fake，驗證輸出。
- 時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public ICommentService Service { get; set; } = new ProviderCommentService();
protected override void CreateChildControls() {
    var data = Service.GetRecent(Count);
    // render...
}
```

實測數據（建議）：
- 改善前：幾乎不可測
- 改善後：核心邏輯具單元測試
- 改善幅度：測試覆蓋率 +60%（建議）

Learning Points
- 依賴反轉
- 假實作與測試替身
- UI 渲染可測策略

Practice Exercise
- 基礎：屬性注入（30 分鐘）
- 進階：建立 Fake 服務（2 小時）
- 專案：加入 CI 單元測試（8 小時）

Assessment Criteria
- 完整性：可注入、可測
- 品質：介面清晰
- 效能：無過度抽象損耗
- 創新：測試替身設計

---

## Case #15: 從 CS 1.0 客製遷移到 CS 2.0 Provider/Theme 架構

### Problem Statement
**業務場景**：CS 1.0 時期的自改程式（直連 DB、硬貼標記）在 2.0 架構下失效。需在最短時間恢復功能並符合新架構。
**技術挑戰**：舊功能盤點、對映到 Provider/Theme 模式、風險控管。
**影響範圍**：上線時程、品質穩定度。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 架構變更破壞相容。
2. 舊代碼無抽象層。
3. 無遷移計畫。

**深層原因**：
- 架構：1.0 與 2.0 設計哲學不同。
- 技術：缺少封裝與測試。
- 流程：升級前未做功能回歸清單。

### Solution Design
**解決策略**：建立遷移藍圖：功能清單→分群（資料存取/顯示）→以 Provider/Theme 重建→逐步替換，先恢復關鍵功能（如 Recent Comments）。

**實施步驟**：
1. 盤點與優先排序
- 實作細節：標記關鍵度/風險。
- 時間：0.5 天

2. 重建資料存取層
- 實作細節：Provider 封裝服務。
- 時間：1 天

3. 重建顯示層
- 實作細節：控制 + Skin 映射。
- 時間：1 天

4. 驗收與回歸
- 實作細節：測試用例、使用者驗收。
- 時間：0.5 天

**關鍵程式碼/設定**：
```text
遷移清單樣式（片段）
- 最新回應：資料存取→Provider；顯示→控制+Skin；完成 ✓
- 最新文章：同上；進度 50%
```

實測數據（建議）：
- 改善前：核心功能缺失
- 改善後：核心功能恢復
- 改善幅度：回歸覆蓋率 100%

Learning Points
- 升級遷移策略
- 風險分層處理
- 先關鍵後非關鍵

Practice Exercise
- 基礎：製作遷移清單（30 分鐘）
- 進階：完成第二個小功能遷移（2 小時）
- 專案：完整升級小模組（8 小時）

Assessment Criteria
- 完整性：核心功能恢復
- 品質：遷移文檔與測試
- 效能：不退化
- 創新：工具/模板沉澱

---

# 案例分類

1. 按難度分類
- 入門級：Case 3, 6, 11, 12, 13
- 中級：Case 1, 2, 4, 5, 7, 8, 9, 10, 14
- 高級：Case 15

2. 按技術領域分類
- 架構設計類：Case 1, 4, 6, 8, 15
- 效能優化類：Case 9, 12
- 整合開發類：Case 2, 5, 7
- 除錯診斷類：Case 10, 14
- 安全防護類：Case 11, 13

3. 按學習目標分類
- 概念理解型：Case 2, 3, 6
- 技能練習型：Case 4, 5, 7, 12, 13
- 問題解決型：Case 1, 8, 9, 10, 11
- 創新應用型：Case 14, 15

# 案例關聯圖（學習路徑建議）
- 先學案例：
  - Case 3（Post 類型過濾基礎）
  - Case 6（Provider 原則與禁忌）
  - Case 2（Theme/Skin 映射概念）
- 進階依賴：
  - Case 5 依賴 Case 6（Provider 封裝）
  - Case 4 依賴 Case 2（Skin 掛載）與 Case 7（控制封裝）
  - Case 1 綜合 Case 3、4、5（完成「最新回應」）
- 強化階段：
  - Case 9（快取效能）在 Case 1 完成後導入
  - Case 10（降級）、Case 11（審核權限）、Case 13（XSS）為品質強化
  - Case 12（Top-N/分頁）優化體驗
  - Case 14（可測試性）落實工程品質
- 高階整合：
  - Case 8（多 Theme 支援）在控制成熟後推廣
  - Case 15（遷移策略）作為整體升級方法論

完整路徑建議：
Case 3 → Case 6 → Case 2 → Case 5 → Case 4 → Case 1 → Case 9 → Case 10 → Case 11 → Case 13 → Case 12 → Case 8 → Case 14 → Case 15

以上 15 個案例均以原文脈絡（CS 2.0 Provider/Theme、Post 統一型別、控制對應 Skin、DLL 處理邏輯）為基礎進行結構化與教學化，並加入可操作的程式與量化評估目標，便於實戰、專案練習與能力評估。