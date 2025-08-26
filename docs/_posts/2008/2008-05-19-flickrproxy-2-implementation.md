---
layout: post
title: "FlickrProxy #2 - 實作"
categories:
- "作品集: FlickrProxy"
tags: [".NET","ASP.NET","作品集"]
published: true
comments: true
redirect_from:
  - /2008/05/19/flickrproxy-2-實作/
  - /columns/post/2008/05/19/FlickrProxy-2-e5afa6e4bd9c.aspx/
  - /post/2008/05/19/FlickrProxy-2-e5afa6e4bd9c.aspx/
  - /post/FlickrProxy-2-e5afa6e4bd9c.aspx/
  - /columns/2008/05/19/FlickrProxy-2-e5afa6e4bd9c.aspx/
  - /columns/FlickrProxy-2-e5afa6e4bd9c.aspx/
  - /columns/post/2008/05/19/FlickrProxy-2---e5afa6e4bd9c.aspx/
  - /post/2008/05/19/FlickrProxy-2---e5afa6e4bd9c.aspx/
  - /post/FlickrProxy-2---e5afa6e4bd9c.aspx/
  - /columns/2008/05/19/FlickrProxy-2---e5afa6e4bd9c.aspx/
  - /columns/FlickrProxy-2---e5afa6e4bd9c.aspx/
  - /blogs/chicken/archive/2008/05/19/3243.aspx/
wordpress_postid: 105
---

整個進度算是很順利，初版已經可以運作了，而且也成功的套用在[小熊子的 BLOG](http://michadel.chicken-house.net/blogs/michadel/default.aspx)上... 因為過去已經有幾個[類似的 HttpHandler](/post/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx)的 code 可以直接拿來改了，反而真正的瓶頸是在瞭解如何操控 FlickrNet 這個 .NET 版的 Flickr API 身上 Orz。FlickrNet 碰到的問題後面再說明，先來看一下整個 Project 的源頭: system design。

這個程式的目標很明確，就是我不想改變任何的使用習慣，我要讓 blogger (比如我家大人) 完全不用理會 flickr 這東西的存在，也不需要在寫文章時去傷腦筋該把照片先放到 Flickr 然後再放到網頁上這類瑣事.. 因此我需要的是在 blog server 上有某些自動的機制，能夠自動把照片丟到 flickr 上，也能夠自動的把網頁上要顯示的照片轉到 flickr 那邊。而必要時，這些機制都能夠取消或調整，不會影響到 blog 的資料等等問題。

初步的想法就是從接手這些圖檔的 HttpHandler 著手。如果前端 (BROWSER) 到 BLOG SERVER 上要求下載照片的要求都能經過我的控制，理論上我就能達成這個目的。因為前端的 Http Request 不需要修改，因此我這次的任務不需要像[黑暗大哥](http://www.darkthread.net/)那樣辛苦的去[調整每一頁的 HTML code](http://blog.darkthread.net/blogs/darkthreadtw/archive/2008/05/10/replace-html-of-asp-net.aspx) (雖然我的方法也沒多輕鬆.. Orz)，這是我決定採用這個方式的主要優點。HTML不用改，我也不用改變原本上傳圖檔的方式，因此所有的調整都不會影響到最重要的 DATA，所有改變都是可以還原的。

負責處理照片的 Http Handler 只要能依照這流程作事就夠了，因此等等會看到的程式碼也是很簡單:

1. 接收 Http Request，如果條件符合 (確認這是要轉到 Flickr 的照片，檔案大小超過指定值... 等等) 則進行下一個步驟，否則就像一般的靜態檔案一樣，直接回傳檔案內容。
2. 先檢查 CACHE 是否已經有對應的資訊 ( ASP.NET 內建的 Cache, 及在暫存目錄建立的 cache file ... 等等 )，有的話直接把 Http Request 重新導向到 Flickr 上同一張照片的網址。
3. 如果 (2) 不成立的話，就要執行主要的動作 - 上傳到 Flickr 並且建立必要的 CACHE 資訊，然後重複 (2) 的動作。主要的動作包括:
   - 計算 HASH，建立 CACHE 檔案
   - 透過 Flickr API，把檔案丟到 Flickr 服務上，並且取得 URL 等資訊
   - 把取得的資訊放在 CACHE 檔案裡
   - 執行 (2)，直接把 Http Request 重新導向到 Flickr URL

這樣就完成了。我把它畫成 UML Sequency Diagram:

![UML Diagram](/images/2008-05-19-flickrproxy-2-implementation/1_3.png)

接下來就是看 Code 了，寫這樣的程式，關鍵有幾個，大部份都是 IIS / ASP.NET 的設定要正確，讓 IIS 能把 REQUEST 轉到你的程式，剩下的就沒什麼特別的了。對 HttpHandler 不熟的人可以先參考一下這幾篇 ( From MSDN ):

[How to: Configure an HTTP Handler Extension in IIS](ms-help://MS.MSDNQTR.v90.en/dv_vwdcon/html/f5d7bdde-f52d-4f5e-8f86-397378ed1024.htm)  
[How to: Register HTTP Handlers](ms-help://MS.MSDNQTR.v90.en/dv_vwdcon/html/d5633f9a-03fb-4ccc-a799-dc67d656fa60.htm)  
[HTTP Handlers and HTTP Modules Overview](ms-help://MS.MSDNQTR.v90.en/dv_vwdcon/html/f540bdeb-d22e-4e1d-ba8a-fe6c9926283b.htm)  
[Walkthrough: Creating a Synchronous HTTP Handler](ms-help://MS.MSDNQTR.v90.en/dv_vwdcon/html/daa90a3b-47d7-45f7-98cc-188fa56424c9.htm)

在 IIS 上寫這些東西，比較麻煩的是 configuration，反而不是程式... 初學者常會卡在這裡，而這部份的行為正好又跟 Visual Studio 內建的 DevWeb 差很多 (真的差很多... 有時連抓到的 Path Info 都會不一樣 @_@)，強烈建議開發階段就直接在 IIS 上面開發...

要克服的第一個設定，就是 IIS。預設情況下，IIS 看到圖檔的 request，毫不考慮就會把內容丟回去了，你程式怎麼寫都沒機會攔到，所以要在應用程式對應這邊，先把 *.JPG 的控制權交給 .NET Framework 的 ISAPI filter ..

有兩個選擇，你心藏夠力的話可以把所有的 Request 都指到 .NET Framework，或是只指定 .JPG 就好。我這邊是以 .JPG 為例:

![IIS 設定](/images/2008-05-19-flickrproxy-2-implementation/image_thumb_2.png)

仔細看一下可以發現，其實所有 ASP.NET 的附檔名，通通都是指向同一個 ISAPI Filter: aspnet_isapi.dll。至於每一種附擋名會有什麼不同的行為，那是 .NET 自己關起門來解決的事，這邊不用傷腦筋... 直接 COPY 別的設定過來最快..

IIS 的部份搞定了，如果現在就透過 IIS 去看網站上的 .JPG，全部都會破圖... 因為所有的 Request 全都被 .NET 接管了。除非你整個 WEB APP 的 .JPG 都要透過你的 HTTP HANDLER，否則請先在 WEB.CONFIG 裡加上這段:

加在 /configuration/system.web/httpHandlers 下 (這是 XPath):

**用內建的 StaticFileHandler 來處理 *.JPG 的 Http Request**

```xml
<httpHandlers>
  <add path="*.jpg" verb="*" type="System.Web.StaticFileHandler" />
</httpHandlers>
```

System.Web.StaticFileHandler 是 ASP.NET 內建的，是跟 IIS 預設一樣的行為，就是原封不動的把檔案的 BINARY DATA 照傳回去而以。預設的還有其它幾個，Forbidden 等等的都可以用同樣的方式指定。

這一段加上去等於繞了一圈，IIS把 .JPG 交給 ASP.NET，而 ASP.NET 又原封不動的傳了回去。沒錯，一切都是為了後面作準備... 接下來要把未來會放照片的目錄，重新指定 HttpHandler。我的例子是 ~/storage 下的 *.JPG 通通都要轉到 Flickr，因此我在 Web.config 加上這段 (當然，你直接放在 ~/storage/web.config 也是可以):

**重新指定在 ~/storage 目錄下的 HttpHandlers**

```xml
<location path="storage">
  <system.web>
    <httpHandlers>
      <add path="*.jpg" verb="*" type="ChickenHouse.Web.HttpHandlers.FlickrProxyHttpHandler,App_Code" />
    </httpHandlers>
  </system.web>
</location>
```

設定的部份大功告成，剩下的就是程式碼了。看一下主要的部份:

**FlickrProxyHttpHandler 主程式片段**

```csharp
//
//  確認 CACHE 目錄已存在
//
if (Directory.Exists(this.CacheFolder) == false)
{
    Directory.CreateDirectory(this.CacheFolder);
}
XmlDocument cacheInfoDoc = new XmlDocument();
string flickrURL = null;
if (File.Exists(this.CacheInfoFile) == false)
{
    //
    //  CACHE INFO 不存在，重新建立
    //
    flickrURL = this.BuildCacheInfoFile(context);
}
else
{
    //
    //  CACHE INFO 已經存在。確認 CACHE 的正確性後就可以直接導到 FLICKR URL
    //
    string cacheKey = "flickr.proxy." + this.GetFileHash();
    flickrURL = context.Cache[cacheKey] as string;
    if (flickrURL == null)
    {
        cacheInfoDoc.Load(this.CacheInfoFile);
        flickrURL = cacheInfoDoc.DocumentElement.GetAttribute("url");
        context.Cache.Insert(
            cacheKey,
            flickrURL,
            new CacheDependency(this.CacheInfoFile));
    }
}
context.Response.Redirect(flickrURL);
```

刪掉了一些無關緊要的 CODE。主程式很簡單，就上面提到了邏輯而以。想辦法取得照片在 Flickr 那邊的正確網址，Redirect回去就好。如何得知網址? 第一次如何把照片傳上去? 這次來看看主角: BuildCacheInfoFile。

**Method: BuildCacheInfoFile( )**

```csharp
private string BuildCacheInfoFile(HttpContext context)
{
    Flickr flickr = new Flickr(
        ConfigurationManager.AppSettings["flickrProxy.API.key"],
        ConfigurationManager.AppSettings["flickrProxy.API.security"]);
    flickr.AuthToken = ConfigurationManager.AppSettings["flickrProxy.API.token"];
    string photoID = flickr.UploadPicture(this.FileLocation);
    PhotoInfo pi = flickr.PhotosGetInfo(photoID);
    string flickrURL = null;
    try
    {
        flickrURL = this.CheckFlickrUrlAvailability(pi.MediumUrl);
        flickrURL = this.CheckFlickrUrlAvailability(pi.LargeUrl);
        flickrURL = this.CheckFlickrUrlAvailability(pi.OriginalUrl);
    }
    catch { }
    XmlDocument cacheInfoDoc = new XmlDocument();
    cacheInfoDoc.LoadXml("<proxy />");
    cacheInfoDoc.DocumentElement.SetAttribute(
        "src",
        this.FileLocation);
    cacheInfoDoc.DocumentElement.SetAttribute(
        "url",
        flickrURL);
    cacheInfoDoc.DocumentElement.SetAttribute(
        "photoID",
        photoID);
    cacheInfoDoc.Save(this.CacheInfoFile);
    
    return flickrURL;
}
```

寫這段，其實時間都花在怎麼用 Flickr API。Flickr API 很重視使用者的安全。認證部份一定要使用者親自到 Flickr 網站登入，同時按下授權後，API才能正常使用。經過這一連串動作，可以拿到三組序號:

1. API Key
2. Share Security Key
3. Token

其中 (1) 及 (2) 是使用者要自己到 Flickr 網站申請的 (http://www.flickr.com/services/api/keys)，第三個 TOKEN 就是要程式呼叫過程中會要求使用者連上網啟用後才能得到的。這邊我沒另外寫程式，我是直接用 [FlickrNet](http://www.codeplex.com/FlickrNet) 的作者提供的 [SAMPLE CODE](http://www.codeplex.com/FlickrNet/Wiki/View.aspx?title=Examples&referringTitle=Home)，照著操作就可以拿到 TOKEN 了。

有了這三段序號 API 才能正常運作。之後只要上傳 (第七行) 取得 photoID 回來就算完成。接下來第 12 行取得網址就 OK 了。

不過這邊也是卡最久的地方... 有人說 flickr server 忙的時後連到照片網址，有時會出現 "photo not available" 的訊習，有時又正常。有人則說某些照片只會有特定 SIZE，像是 original / large size 的有時也會發生 "photo not available" 的狀況...

試了幾次，實在是抓不出它的規則，也找不出避開的辦法... 只好硬著頭皮，每個取得的網址就都用 HTTP 硬給它試看看... 因為 Flickr API 取得網址的 property 在失敗時會丟出 EXCEPTION，因此這段 code 寫成這樣:

**取得 SIZE 最大的可用網址**

```csharp
try
{
    flickrURL = this.CheckFlickrUrlAvailability(pi.MediumUrl);
    flickrURL = this.CheckFlickrUrlAvailability(pi.LargeUrl);
    flickrURL = this.CheckFlickrUrlAvailability(pi.OriginalUrl);
}
catch { }
```

CheckFlickrUrlAvailability() 是我自己寫的，就是真正連到 Flickr 判定到底照片能不能從這網址下載... 任一行只要發生 EXCEPTION 就會跳出，flickrURL 變數就可以保留最後一個 (最大) 可用的網址...。

好，程式碼看完了... 最後來看看[測試網站](http://demo.chicken-house.net/MediaProxy/storage/HTMLPage.htm)。我放了一個很簡單的網頁，簡單的幾行 HTML，加上一張圖。

**測試用的 HTML 檔**

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Untitled Page</title>
</head>
<body>

<hr />

<img src="smile_sunkist.jpg" alt="test image" />

<hr />


</body>
</html>
```

網頁上看到的結果:

![測試結果](/images/2008-05-19-flickrproxy-2-implementation/image_thumb_3.png)

這有啥好看的? 只是證明 USER 看起來完全正常而以... 哈哈，拿出 Fiddler 看一下:

![Fiddler 結果](/images/2008-05-19-flickrproxy-2-implementation/image_thumb_4.png)

#0 及 01 都是正常情況下就會有的 HTTP REQUEST，代表 IE 要下載 HTML 跟 JPG。不過在下載 JPG 檔，卻收到了 302 (OBJECT MOVE) 的重新導向的結果，因此 IE 就接著再到 Flickr 去下載照片，最後秀在網頁上。不過照片真的有出現在 Flickr 上嗎? 用我的帳號登入看看...

![Flickr 帳號截圖](/images/2008-05-19-flickrproxy-2-implementation/image_thumb_5.png)

哈哈，果然出現了。看來這沒幾行的 CODE 真正發恢它的作用了。網站什麼都不用改，只要加上這 HttpHandler，配合調一些設定，馬上下載圖片的頻寬就省下來了。不過最少還是得花一次頻寬啦。BLOGGER把圖檔傳上來就不說了，圖檔第一次有人來看的時後，程式還是需要把檔案傳出去，放到 Flickr 上。不過一旦放成功了，以後第二次第三次.... 的頻寬就都省下來了。要花的只有 Fiddler 抓到的 #1 那少少的 302 REDIR 回應而以。

這個 Project 告一段落，後續還是會繼續改進，不過就都是小地方的調整，一些重構及把舊的 code 整理在一起的動作而以。對程式碼有興趣的人可以再跟我聯絡。
