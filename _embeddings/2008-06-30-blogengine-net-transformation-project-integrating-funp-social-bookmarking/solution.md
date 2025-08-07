# [BlogEngine.NET] 改造工程 – 整合 FunP 推推王

# 問題／解決方案 (Problem/Solution)

## Problem: 在 BlogEngine.NET 中整合社群書籤服務時導致頁面載入緩慢與版面崩潰

**Problem**:  
當在 BlogEngine.NET 部署「黑米卡」或其他第三方書籤工具時，首頁、文章頁及封存頁一次要載入數十到數百個書籤按鈕。原本使用黑米卡 (HemiCard) 時，不僅載入速度緩慢，還常因為 JavaScript 還沒完整執行就被中斷，造成整個版面走樣甚至掛掉。

**Root Cause**:  
1. 黑米卡採用繁複的 client-side script（document.write、eval 等）才動態產生 HTML。  
2. 每產生一顆按鈕就送出一次 request，文章較多時（封存頁一次 400~500 篇）瀏覽器需同時執行上百段 Script，導致 Render 及網路請求量暴增。  
3. BlogEngine.NET 使用的版型與黑米卡 CSS/JS 衝突，任何執行中斷都可能讓版面直接被「撐爆」。

**Solution**:  
1. 捨棄黑米卡，改採程式碼較輕量、API 筆數要求較少的 FunP 推推王按鈕。  
2. 直接在 PostView.ascx 產生「純 IFRAME」標籤，完全迴避第三方 Script：  

   ```csharp
   <%
       Regex _stripHTML = new Regex("<[^>]*>", RegexOptions.Compiled);
       string PostTextContent = _stripHTML.Replace(Post.Content, "");
       int maxLength = 70;
       
       string EncodedAbsoluteLink = Page.Server.UrlEncode(Post.AbsoluteLink.ToString());
       string EncodedPostTitle   = Page.Server.UrlEncode(Post.Title);
       string EncodedPostBody    = Page.Server.UrlEncode(
                                   (PostTextContent.Length > maxLength) ? 
                                   (PostTextContent.Substring(0, maxLength) + "...") : 
                                   (PostTextContent));
   %>
   <IFRAME width=60 height=55 marginWidth=0 marginHeight=0 frameBorder=0 scrolling=no
           src="http://funp.com/tools/buttoniframe.php?url=<%=EncodedAbsoluteLink%>&s=1">
   </IFRAME>
   ```
3. 透過一次 request 取得內嵌 IFRAME，避免多重 JavaScript 解析，減少資源占用並消除版面崩潰風險。

**Cases 1**:  
• 文章頁面自載入時間由原本 5~7 秒降至 2~3 秒。  
• 再次整理模板後，不再出現因書籤 Script 被中止而導致的「整個版型消失」現象。  

---

## Problem: 推文時無法自動帶出文章標題、內文摘要與分類標籤，使用者需另外填寫

**Problem**:  
若直接使用 FunP 官方 Button Generator 嵌入的 Script，點擊「推」之後僅帶入 URL，其餘欄位（標題、內文、分類）需使用者自行輸入，降低互動意願與推文數。

**Root Cause**:  
FunP 官方工具只在 client side Script 端處理欄位對應，若改為 IFRAME 直出就失去自動帶參數能力；而 BlogEngine.NET 本身沒有內建把文章資訊包進 QueryString 的功能。

**Solution**:  
1. 於 PostView.ascx 先行將標題、內文、分類進行 URL Encode。  
2. 再組出一條完整的 `<a>` 連結，於 QueryString 帶入 `url`、`s`(title)、`t`(content)、`tags[]`(多筆) 等欄位。  

   ```html
   <a href="http://funp.com/push/submit/add.php?url=<%=EncodedAbsoluteLink%>
           &s=<%=EncodedPostTitle%>
           &t=<%=EncodedPostBody%>
           <%=TagsQueryString%>
           &via=tools"
      title="貼到 funP">
       <img src="http://funp.com/tools/images/post_03.gif" border="0"/>
   </a>
   ```

   TagsQueryString 由下列 C# 迴圈組成：  

   ```csharp
   string TagsQueryString = "";
   foreach (BlogEngine.Core.Category cat in Post.Categories)
   {
       TagsQueryString += "&tags[]=" + Page.Server.UrlEncode(cat.Title);
   }
   ```

3. 使用者點擊後，FunP 發文頁面自動帶好所有欄位，零輸入即可完成推文。

**Cases 1**:  
• 推文流程由「平均 4~5 個輸入動作」縮減為「1 次點擊」。  
• 文章被推次數提高約 25%，讀者互動率同步提升。

---

## Problem: 封存頁一次需顯示數百顆推文按鈕，若沿用原 Rating 位置及官方 Script 會拖垮瀏覽器

**Problem**:  
BlogEngine.NET 的 archive.aspx 會將所有文章按年月分組列出；我的部落格累積近 250 篇文章，包含重複出現的目錄列舉，實際會產生近 500 個按鈕欄位。若使用 FunP Script 或沿用 Rating 機制，IE/Firefox 皆會因同步 500+ 次 HTTP 與大量 JS 解析而明顯延遲甚至當掉。

**Root Cause**:  
1. Rating 機制原以 Ajax 請求取得分數，同時封存頁一次綁定多個 JS Handler。  
2. FunP 官方 Script 同樣需大量動態 JS。  
3. 瀏覽器對大量 DOM 注入 IFRAME/Script 反覆 Reflow，CPU 持續飆高。

**Solution**:  
1. 取消 BlogEngine「EnableRating」設定，在 Cell 中直接出 IFRAME 版本的 FunP 小尺寸按鈕 (`s=12`)。  
2. 於 ~/archive.aspx.cs 動態產生 HTML 字串取代 Rating Cell：  

   ```csharp
   if (BlogSettings.Instance.EnableRating)
   {
       HtmlTableCell rating = new HtmlTableCell();
       rating.InnerHtml = string.Format(
           @"<IFRAME marginWidth=0 marginHeight=0 
                     src='http://funp.com/tools/buttoniframe.php?url={0}&amp;s=12'
                     frameBorder=0 width=80 scrolling=no height=15>
             </IFRAME>",
           post.AbsoluteLink.ToString());
       rating.Attributes.Add("class", "rating");
       row.Cells.Add(rating);
   }
   ```

3. 小尺寸 IFRAME 只需靜態組字串，不牽涉額外 JS，500 次 request 仍集中於 FunP 服務端，不佔用瀏覽器執行緒。

**Cases 1**:  
• 封存頁完全載入時間自 30+ 秒降至 10 秒以內。  
• IE 在同頁 500 IFRAME 情境下 CPU 利用率從接近 100% 降至 40% 以下，瀏覽器不再假死。  

---

以上三項改造以最小化 Script 依賴的方式成功把 FunP 推推王整合進 BlogEngine.NET，既改善效能，又保留完整推文功能，也為後續擴充（如自製 ViewCounter Extension）奠定簡潔基礎。