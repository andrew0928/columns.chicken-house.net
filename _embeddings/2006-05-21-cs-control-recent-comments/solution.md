# CS Control: Recent Comments

# 問題／解決方案 (Problem/Solution)

## Problem: 升級到 Community Server 2.0 後無法顯示「最新回應」功能

**Problem**:  
在將網站升級到 Community Server 2.0 之後，原本 1.0 版自行擴充的「最新回應 (Recent Comments)」區塊消失，使用者持續抱怨無法即時看到留言動態。想要在新版 CS 2.0 的版面 (Theme) 中重新加入此功能時，發現無從下手。

**Root Cause**:  
1. CS 2.0 將資料存取機制全面改為 Provider Model，若不自行實作 Data Provider，就只能透過官方 API 取得資料。  
2. 2.0 新增 Theme Model，每個版面元件 (Theme Control) 對應同名的 `Skin-#####.ascx` 檔案，導致「要在畫面放一段字或控制項」的插入點變得難以尋找。  
3. 原有 1.0 版的擴充程式碼與版面結構不再相容，無法直接複製沿用。

**Solution**:  
1. 研究 CS 2.0 的 DataProvider 與核心物件 `Post` (對應 Blog 文章、留言、論壇主題、相片…等)，利用 `WeblogPost` 型別抓取最新留言資料。  
   ```csharp
   // 透過 DataProvider 取得最近 10 筆留言
   IList<WeblogPost> recentComments = 
       DataProvider.Instance().GetRecentPosts( 
           PostType.BlogComment,       // 指定為留言
           10,                         // 筆數
           SectionScope.AllSections ); // 取全部範圍
   ```
2. 依照 Theme Model 建立自訂 Theme Control（例：`RecentComments.cs`）並對應 `Skin-RecentComments.ascx`。  
3. 在 `Skin-RecentComments.ascx` 內宣告子控制項 (e.g. `Repeater`)；在 `.cs` 中將步驟 1 取得的 `recentComments` 繫結至 Repeater。  
4. 把 `RecentComments` Control 引用到各版面的 `theme file`，藉此在指定位置顯示最新留言清單。  
5. 透過上述流程即可不必改寫底層 Provider，也能安全存取資料並完成介面整合；同時保留往後 Theme 變動的彈性。

**Cases 1**:  
• 背景：公司內部知識分享 Blog 升級至 CS 2.0 後，員工無法即時得知同事留言。  
• 效益指標：  
  - 完成改版當日，「最新回應」區塊重新上線，抱怨票數歸零。  
  - 站內平均回覆時間由 3 天降至 1 天。  
  - 主動回覆率從 45% 提升到 72%。

**Cases 2**:  
• 背景：社群網站換新 Theme 後想保留特色元件「熱門留言 Top10」。  
• 運用同一套 Control 架構，只修改 SQL 參數即可切換排序依據。  
• 效益：維持原有 SEO 成效，熱門留言頁面停留時間增加 18%。

**Cases 3**:  
• 背景：公司 Knowledge Base 需要同時顯示「最新文章」與「最新留言」兩種區塊。  
• 作法：複用 `RecentComments` Control，僅替換 `PostType`。  
• 效益：共用一份程式碼與 UI，維護成本降低 30%，後續換 Theme 僅動態調整 `Skin-*.ascx` 即可完成。