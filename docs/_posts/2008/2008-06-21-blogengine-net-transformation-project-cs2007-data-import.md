---
layout: post
title: "[BlogEngine.NET] 改造工程 - CS2007 資料匯入"
categories:

tags: [".NET","ASP.NET","BlogEngine.NET","Community Server","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/06/21/blogengine-net-改造工程-cs2007-資料匯入/
  - /2008/06/21/blogengine-net-改造工程-cs2007-資料匯入/
  - /columns/post/2008/06/21/BlogEngineNET-e694b9e980a0e5b7a5e7a88b-CS2007-e8b387e69699e58cafe585a5.aspx/
  - /post/2008/06/21/BlogEngineNET-e694b9e980a0e5b7a5e7a88b-CS2007-e8b387e69699e58cafe585a5.aspx/
  - /post/BlogEngineNET-e694b9e980a0e5b7a5e7a88b-CS2007-e8b387e69699e58cafe585a5.aspx/
  - /columns/2008/06/21/BlogEngineNET-e694b9e980a0e5b7a5e7a88b-CS2007-e8b387e69699e58cafe585a5.aspx/
  - /columns/BlogEngineNET-e694b9e980a0e5b7a5e7a88b-CS2007-e8b387e69699e58cafe585a5.aspx/
  - /columns/post/2008/06/21/BlogEngineNET-e694b9e980a0e5b7a5e7a88b---CS2007-e8b387e69699e58cafe585a5.aspx/
  - /post/2008/06/21/BlogEngineNET-e694b9e980a0e5b7a5e7a88b---CS2007-e8b387e69699e58cafe585a5.aspx/
  - /post/BlogEngineNET-e694b9e980a0e5b7a5e7a88b---CS2007-e8b387e69699e58cafe585a5.aspx/
  - /columns/2008/06/21/BlogEngineNET-e694b9e980a0e5b7a5e7a88b---CS2007-e8b387e69699e58cafe585a5.aspx/
  - /columns/BlogEngineNET-e694b9e980a0e5b7a5e7a88b---CS2007-e8b387e69699e58cafe585a5.aspx/
wordpress_postid: 95
---

自從搬到 BlogEngine.NET 之後，每天晚上都沒閒著，一點一點的慢慢把整個網站改成我要的樣子... 資料庫 / 檔案是我最在意的，當然要優先顧好，光這部份就花了一個多禮拜...

最早找到了 CS2007 --> BlogML --> BlogEngine，大概把我想要的 90% 資料都轉過來了，不過看到那 10% 的資訊沒過來，心裡就很不是滋味...

"這是我要一直保留下來的資料耶，現在沒把資料補回來，以後就永遠補不回來了..."

就是心裡一直這樣想，所以... 重匯吧! 不然以後後悔也是補不回來的。首先當然是想先從 BlogEngine 匯入 BlogML 的工具下手，看了一下，沒提供 Source Code ? 再看一下，一篇文章一個 Web Service Call，一則回應也是一個 Web Service Call ... 感覺起來有點沒效率，不過不管了，我內容也不多 (兩百多篇文章) ... 既然有 Web Services，先看看它的 WSDL ...

![image](/wp-content/be-files/WindowsLiveWriter/BlogEngine.NETCS2007_3ABA/image_3.png)
[http://columns.chicken-house.net/api/blogImporter.asmx](http://columns.chicken-house.net/api/blogImporter.asmx)

沒幾個 WebMethod 嘛，不過看一看它的 Interface 就已經漏掉很多資訊沒轉進來了 (像是我要的原 CS PostID，事後作新舊網址對照表用，還有 PageViewCount... etc)，要改原程式也是個大工程，不但 CLIENT 要改，WEB METHOD 也要擴充... 我又不是非得遠端用 WEB SERVICES 執行匯入不可，就當下決定另外寫一個匯入程式還比較快...。重寫的話就得研究它的寫法，正好每個 WebMethod 都只作單一的動作，裡面的實作就是現成的範例... 省了不少熟悉 API 的時間 :P

事後證明這作法沒錯，BlogEngine 的 LIB 蠻簡單易懂的，另外寫真的比較快... 就一切以原 .ASMX 的程式碼為藍本，寫了一個 .ASHX ，不作什麼事，就是把事先放在 ~/App_Data 下的 BLOGML 讀進來，一篇一篇 POST 處理，一個一個回應處理... 兩層迴圈就搞定原本那 90% 的匯入作業...

接下來就是自訂的部份了。先來列一下那些是我要補的資訊:

1. 每篇 POST 的 COUNTER
2. 每則回應的詳細資訊
3. 每篇 POST 的 ID ( CS2007 內的 ID )，及匯入後的新 ID
4. 所有必要的網址修正 (圖檔，站內文章連結..)
5. 原程式的一些缺陷修正 (如前文提到，Modified Date錯誤的問題)

源頭就有東西要補了。如果一切基於 BlogML 的話，BlogML 沒定義到的資料就沒機會撈出來了。看了一下我還需要額外抓出來的資訊，像匿名的 COMMENTS 作者資訊，IP 等... 不過這些都用某種序列化的方式存在 CSDB，ㄨ!! 真麻煩... 在 CS2007 DB 內的 [cs_posts] 有這兩個欄位: PropertyNames, PropertyValues... 沒錯，全部壓成一個大字串，得自己寫程式去 PARSE ...

CS2007 的作法是這樣，在 PropertyNames 欄位放的值長的像這樣 (包含 Name, 型別, 字串起始及結束位置):

**SubmittedUserName:S:0:3:TitleUrl:S:3:35:**

而在 PropertyValues 對應的值為:

**小熊子[http://michadel.dyndns.org/netblog/](http://michadel.dyndns.org/netblog/)**

拆起來有點小麻煩，PropertyNames 是 {Name}:{Type}:{StartPos}:{EndPos}: 的組合，有多組的話就一直重複下去。以 Comments 的 SubmittedUserName 來說，它的型別是 S ( String )，它的值就要從後面的 PropertyValues 整個字串的第 0 個字元 ~ 第 3 個字元之間的值 ( 小熊子 )，而 TitleUrl 則是第 3 個字元 ~ 第 35 個字元的值 ( [http://michadel.dyndns.org/netblog/](http://michadel.dyndns.org/netblog/) ) ...

看來用 T-SQL 拆或是用 XPath / XSLT 拆都有點辛苦，想想算了... 這段 CODE 跑不掉一定要寫... 就硬解出來吧。解出來後就可以修正 CS2007 匿名張貼的 Comment 沒正確顯示在 BlogML 內的問題。

接下來要把 SQL 這堆資料倒成 XML 檔，偷吃步一下，找工具直接倒出來就好。反正只作一次，可以不要寫 CODE 就不要寫了... SQL2005 要把 QUERY 結果存成 XML 倒是很簡單，打開 SQL2005 Management Studio, 執行這段 QUERY:

**取得所有 comments 的額外 PropertyValues 的查詢指令**

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

會看到這樣的畫面:

![image](/wp-content/be-files/WindowsLiveWriter/BlogEngine.NETCS2007_3ABA/image_8.png)

點下去就是 XML 了，手到加上頭尾的 Root Element 存檔就搞定了。接下來補段 CODE 把我要的 Property 拆出來存 XML 檔，第一步驟收工!

接下來這堆問題就以 (4) 最麻煩了。原本想的很天真，用文字編輯器把所有 XML 檔替換掉就沒事... 錯! 先從最單純的圖檔路逕來看吧..

**[替換圖檔及下載檔案的網址]**

最基本的就是圖檔網址... 在 CS2007 裡圖檔是這樣放的 (WLW會幫你補上絕對路逕，不是用相對路逕)

[http://columns.chicken-house.net/blogs/chicken/xxxxxxx/xxx.jpg](http://columns.chicken-house.net/blogs/chicken/xxxxxxx/xxx.jpg)

而看了 BlogEngine 的作法，它用 HttpHandler 的方式來提供前端下載圖檔，格式像這樣:

[http://columns.chicken-house.net/xxxxx/wp-content/be-files/xxx.jpg](http://columns.chicken-house.net/xxxxx/wp-content/be-files/xxx.jpg)

而 BlogEngine 的設定檔是這樣寫的:

**BlogEngine 在 Web.config 內的 HttpHandler 區段**

```xml
<httpHandlers>
	<add	verb="*" 
		path="file.axd" 
		type="BlogEngine.Core.Web.HttpHandlers.FileHandler, BlogEngine.Core" 
		validate="false"/>
	<add	verb="*" 
		path="image.axd" 
		type="BlogEngine.Core.Web.HttpHandlers.ImageHandler, 
		BlogEngine.Core" 
		validate="false"/>
	.....
</httpHandlers>
```

看起來不難，理論上我只要找到原網址，把 ~/blog/chicken/ 後的路逕切出來，前段改成 image.axd?picthre= 就可以了。

大致上是這樣沒錯，不過變數還不少... 因為有好幾種網址 @_@

1. 分家前  ( [http://community.chicken-house.net/blogs/chicken/xxxxx](http://community.chicken-house.net/blogs/chicken/xxxxx) )
2. 分家後  ( [http://columns.chicken-house.net/blogs/chicken/xxxxx](http://columns.chicken-house.net/blogs/chicken/xxxxx) )
3. 古早時代手工打的 ( /blogs/chicken/xxxxx )
4. 有些內建的要避開，像 ( [http://columns.chicken-house.net/blogs/chicken/rss.aspx](http://columns.chicken-house.net/blogs/chicken/rss.aspx) )

代換要嘛一次做完，要嘛一定要照 1 2 3 順序，否則先做 (3) 就會把 (1) (2) 都破壞掉了... 但是怎麼想程式都很不乾脆，雜七雜八的 CODE 一堆... 最後搬出  [http://regexlib.com/](http://regexlib.com/) 這個網站，它提供大量的 Regular Expression 的資料庫供你使用，也提供了線上版本讓你測試 MATCH 的結果，很好用! 一定要推一下...

最後定案的 Regular Expression 長這樣:

(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/([a-zA-Z0-9\-_\./%]*)

一切都很順利，簡單的就精確的抓到要代換的範圍。補一下小插曲，最後轉完才發現漏掉 (4)，不過沒幾篇，就手動改掉了 :P，所以這段 REGEXP 是沒處理到 (4) 這種情況的...

**[站內連結的修正]**

再來就開始麻煩了... 動手前我先想了一下，每篇文章要匯進去後才會知道它的新 ID，新網址... 在還不知道新網址之前有些內容的聯結就無法替換了，怎麼樣都不可能在 1 PASS 內解決這問題... 只能用 2 PASS 來處理了。

既然這樣，第一次匯入就不修站內聯結了，只要把新舊 ID 記下來就好...

頭痛的來了，CS2007 的網址格式有好幾種 @_@ (難怪它有專門一個 config 檔來設定幾十個 URL Rewrite 的設定...):

1. /blogs/chicken/archive/2008/06/20/1234.aspx
2. /blogs/chicken/archive/2008/06/20/MyPostTitleHash.aspx
3. /blogs/1234.aspx

其中 1234 是 CS2007 內部使用的 PostID .  再看看 BlogEngine 的網址格式:

1. /post.aspx?id=xxxx-xxxx-xxxxxx-xxxxxxxxxxx
2. /post/xxxxxxxxxxxxxxxx.aspx (某種 TITLE 的 HASH，它稱作 SLUG)

還好 BlogEngine 單純多了，只要抓到 (1) 的 ID，SLUG 就有 API 抓的到...

記得 CS 網址還有不需要 URL Rewrite 的版本 ( /blogs/xxxxx.aspx?postID=1234 這樣)，不過從來沒出現在我文章內容，就不理它了...

這裡的重點不是單純的代換了，還要精確的抓出 1234 這段 PostID .. 最後定案的 Regular Expression 長這樣:

(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/archive/\d+/\d+/\d+/(\d+)\.aspx

果然人家說 Regular Expression 是 "WRITE ONLY LANGUAGE" 真有道理，寫完連我自己都看不懂這堆符號是在幹嘛... 最後新舊 ID 都抓到就可以產生出正確的新站內連結了..

**[站外連結修正]**

我自己的 LINK 找到就可以修，不過寫在別人那邊的我那修的到啊... 因此就要靠上一篇講的，想辦法要去接有人點到舊的 CS LINK，然後當場做轉址的動作...

好在舊的文章不會再變多了，靠前面做出來的對照表就有足夠的資訊了... 成果看上一篇就知道了。這裡主要是靠 CSUrlMap.cs 這個我自己寫的 HttpHandler 來解決所有連到 /blogs/*.aspx 的連結...

方法差不多，我得從各種可能的網址格式，抓出舊的 CS PostID，然後查表，找出新的網址，把使用者引導到新的頁面... 貼一下主程式的部份:

**CSUrlMap, 將 CS2007 的網址重新導向到 BlogEngine 網址的 HttpHandler**

```csharp
public void ProcessRequest(HttpContext context)
{
    if (matchRss.IsMatch(context.Request.Path) == true)
    {
        //  redir to RSS
        context.Response.ContentType = "text/xml";
        context.Response.TransmitFile("~/blogs/rss.xml");
    }
    else if (matchPostID.IsMatch(context.Request.Path) == true)
    {
        //  redir to post URL
        Match result = matchPostID.Match(context.Request.Path);

        if (result != null && result.Groups.Count > 0)
        {
            string csPostID = result.Groups[result.Groups.Count - 1].Value;

            if (this.MAP.postIDs.ContainsKey(csPostID) == true)
            {
                context.Items["postID"] = this.MAP.postIDs[csPostID];
                context.Items["redirDesc"] = "網站系統更新，原文章已經搬移到新的網址。";
            }
            else
            {
                context.Items["redirDesc"] = "查無此文章代碼，文章不存在或是已被刪除。將返回網站首頁。";
            }
        }
        else
        {
            context.Items["redirDesc"] = "4444";
        }
    }
    else if (matchPostURL.IsMatch(context.Request.Path) == true)
    {
        context.Items["postID"] = this.MAP.postURLs[context.Request.Path];
        context.Items["redirDesc"] = "網站系統更新，原文章已經搬移到新的網址。";
    }
    else
    {
        context.Items["redirDesc"] = "查無此頁。將返回網站首頁。";
    }

    context.Server.Transfer("~/blogs/AutoRedirFromCsUrl.aspx");
}
```

看程式說故事，大家都會吧 :D，結果就是上一篇各位看到的樣子... 已經沒力一行一行再說明下去了 :P

寫到這邊真是大工程 @_@，動作都不困難，但是都是雜七雜八的工作，害我搞了一個禮拜... 不過到此為止搬家要處理的資料部份全部都完成了。下一篇就輕鬆多了，把網站的版面調整成我想要的樣式... 有興趣的人請多等一等吧 :D 主題會放在跟 [FunP 推推王](http://www.funp.com/)的密切整合上... 敬請期待 :D 
