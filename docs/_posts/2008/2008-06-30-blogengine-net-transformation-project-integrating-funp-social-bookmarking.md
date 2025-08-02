---
layout: post
title: "[BlogEngine.NET] 改造工程 - 整合 FunP 推推王"
categories:

tags: [".NET","ASP.NET","BlogEngine.NET","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/06/30/blogengine-net-改造工程-整合-funp-推推王/
  - /columns/post/2008/06/30/CustomizeBlogEngineNET-FunP.aspx/
  - /post/2008/06/30/CustomizeBlogEngineNET-FunP.aspx/
  - /post/CustomizeBlogEngineNET-FunP.aspx/
  - /columns/2008/06/30/CustomizeBlogEngineNET-FunP.aspx/
  - /columns/CustomizeBlogEngineNET-FunP.aspx/
wordpress_postid: 90
---
[古早以前](/post/e68ea8!!!.aspx)，曾替我的 BLOG 加上推推王的小貼紙，不過當時也僅止於把 CODE 加上去而以，成效不大好...。這次搬家搬到 BlogEngine 後，又開始一樣的循環了..，要不要加上這些共用書籤? 要加那一套? 目前台灣用的最多就是[黑米](http://www.hemidemi.com/)跟[推推王](http://www.funp.com/)了。

原本挑了黑米，只因為它有提供 [黑米卡](http://www.hemidemi.com/blogtools/hemi_card)，正好取代掉 BlogEngine 右邊那塊 [關於作者] .. 不過試用的情況不怎麼理想，除了速度有點慢之外，同一頁放太多 (幾十個) 的速度也很慢，也許跟 BlogEngine 我選用的樣板有點不合，速度太慢時有時整個版面就毀了，下載到一半就掛掉...

相對之下，看了看 FunP 提供的 SCRIPT，看起來 CODING STYLE 比較合我的胃口，速度也快一些，沒碰到會讓我版面掛掉的問題。另外使用上的流程 FunP 也簡單一點，本來想兩家的書籤都放的，到最後就決定支持一下交大的學弟，就全力跟 [FunP 推推王](http://www.funp.com/)整合好了。

動手前先計劃了一下，毫無目的的把一堆 CODE 加上去，我最忌誨這樣弄了，看起來一點主題都沒有。常看到別人的 BLOG 滿滿一堆標籤，從國內的 FunP，黑米，MyShare，到國外的DELICIUS，還有一堆叫不出名字的，一字排開落落長...

BlogEngine 原本也有內建一些，不過被我拿掉了。底下列出我調整的前後差異:

1. 捨棄內建的 Rating 機制，直接用推文就好。
2. 版面我希望類似原有 CS 的樣式，正好拿推文按鈕來取代原本的計數器
3. 就鎖定一個共用書簽就好，把原有左下方的其它都拿掉
4. Tags 我也決定捨棄不用，以分類為主。因此左下的 Tags 就移掉了
5. 分類放右下很礙眼，移到右上
6. 不爽被盜文，加上一段智財權的聲明
7. 加上自己補的計數器... (說來話長，請見下一篇)
8. 推文時自動帶出文章的基本資訊，如標題，內文，標簽等等

原 CS 的樣式:

![image](/wp-content/be-files/WindowsLiveWriter/BlogEngine.NETFunP_11CED/image_10.png)

修改前:

![image](/wp-content/be-files/WindowsLiveWriter/BlogEngine.NETFunP_11CED/image_11.png)

修改後:

![image](/wp-content/be-files/WindowsLiveWriter/BlogEngine.NETFunP_11CED/image_12.png)

看了一下推推王的[工具](http://funp.com/tools/buttongen.php)，不外乎都是插入一段 `<SCRIPT>` 標簽，然後用 document.write( ) 或是 eval 等等 client side script 的方式產生片 HTML Code, 缺點就是繞了一大圈，出了問題也常讓人搞不清楚問題在那裡。花了點時間追一下，追出最後插在網頁的 HTML CODE 長這樣:

```html
<IFRAME	width=60 	height=55	marginWidth=0 	marginHeight=0 	frameBorder=0 	scrolling=no 	src="http://funp.com/tools/buttoniframe.php?url=xxxxxxxxxxxxxx&s=1">
</IFRAME>
```

看起來就是直接產生一個帶著指定參數的 `<IFRAME ...>`，於是我在 BlogEngine Themes 版面就直接產生 `<IFRAME>` ...底下是 BlogEngine THEME 目錄下的 PostView.ascx 片段:

**在 PostView.ascx 顯示推文按鈕的片段**

```csharp
<%
    Regex _stripHTML = new Regex("<[^>]*>", RegexOptions.Compiled);
    string PostTextContent = _stripHTML.Replace(Post.Content, "");
    int maxLength = 70;
    
    string EncodedAbsoluteLink = Page.Server.UrlEncode(Post.AbsoluteLink.ToString());
    string EncodedPostTitle = Page.Server.UrlEncode(Post.Title);
    string EncodedPostBody = Page.Server.UrlEncode((PostTextContent.Length > maxLength) ? (PostTextContent.Substring(0, maxLength) + "...") : (PostTextContent));
    string TagsQueryString = "";
    foreach (BlogEngine.Core.Category cat in Post.Categories)
    {
        TagsQueryString += string.Format("&tags[]=" + Page.Server.UrlEncode(cat.Title));
    }
%>
<IFRAME
    width=60 
    height=55
    marginWidth=0 
    marginHeight=0 
    frameBorder=0 
    scrolling=no 
    src="http://funp.com/tools/buttoniframe.php?url=<%=EncodedAbsoluteLink %>&s=1">
</IFRAME>
```

這是推文的部份，如果要張貼的話就不一樣了，要放的是把文章的預設資訊都帶過去，免的到時要重新輸入一次... 這部份的 CODE 比較囉唆，不過產生出來的 CODE 比較單純，就是個 `<A>` LINK 而以，不過因為帶的資訊比較多，所以部份 CODE 是由上面的 CODE 事先產生好，這裡才拿來用的:

**產生推文按鈕的部份**

```html
<a href="http://funp.com/push/submit/add.php?url=<%=EncodedAbsoluteLink %>&s=<%=EncodedPostTitle %>&t=<%=EncodedPostBody %><%=TagsQueryString %>&via=tools" title="貼到funP">
    <img src="http://funp.com/tools/images/post_03.gif" border="0"/>
</a>
```

果然效果好多了，也不會再碰到版面掛掉等等鳥問題，只不過載入 [封存] 頁面時，一次四五百個 `<IFRAME>` 同時在跑，IE也是跑的很吃力....

![image](/wp-content/be-files/WindowsLiveWriter/BlogEngine.NETFunP_11CED/image_3.png)

同樣的技巧也拿來修改 ~/archive.aspx 這頁。這頁原本是把所有的文章按照分類一篇一篇列出來，捨棄原有的 RATING 機制不用，直接用推文的機制取代。因此這頁原本顯示 RATING 分數的地方就被我改成推推王的推薦次術了。我的文章有兩百多篇，出現過的地方都列一次，加一加總共會出現近五百個推文按鈕 @_@，自然也不可能用原本官方的作法產生按鈕，直接用上面挖出來的方法，修改 archive.aspx.cs:

**~/archive.aspx.cs 顯示推文按鈕的片段程式**

```csharp
if (BlogSettings.Instance.EnableRating)
{
    HtmlTableCell rating = new HtmlTableCell();
    rating.InnerHtml = string.Format(
      @"<IFRAME 
  marginWidth=0 
  marginHeight=0 
  src='http://funp.com/tools/buttoniframe.php?url={0}&amp;s=12' 
  frameBorder=0 
  width=80 
  scrolling=no 
  height=15>
</IFRAME>", 
      (post.AbsoluteLink.ToString()));
    rating.Attributes.Add("class", "rating");
    row.Cells.Add(rating);
}
```

嗯，看起來效果好多了，至少我自己看起來順眼多了 :D 

下一篇預告一下，下一篇會推出我自己寫的 PostViewCounter Extension，主要就是拿來作每篇文章的點閱率。BlogEngine 沒內建，找來的現成的又不是很合用，索性就自己寫了一個，請期待續篇 :D