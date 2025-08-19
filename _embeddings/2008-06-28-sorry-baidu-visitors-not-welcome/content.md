---
layout: post
title: "很抱歉，本站不歡迎來自 [百度] (Baidu.com) 的訪客 !!"
categories:

tags: ["技術隨筆","有的沒的","火大"]
published: true
comments: true
redirect_from:
  - /2008/06/28/很抱歉，本站不歡迎來自-百度-baidu-com-的訪客/
  - /columns/post/2008/06/28/e5be88e68ab1e6ad89efbc8ce69cace7ab99e4b88de6ada1e8bf8ee4be86e887aa-e799bee5baa6-(Baiducom)-e79a84e8a8aae5aea2-!!.aspx/
  - /post/2008/06/28/e5be88e68ab1e6ad89efbc8ce69cace7ab99e4b88de6ada1e8bf8ee4be86e887aa-e799bee5baa6-(Baiducom)-e79a84e8a8aae5aea2-!!.aspx/
  - /post/e5be88e68ab1e6ad89efbc8ce69cace7ab99e4b88de6ada1e8bf8ee4be86e887aa-e799bee5baa6-(Baiducom)-e79a84e8a8aae5aea2-!!.aspx/
  - /columns/2008/06/28/e5be88e68ab1e6ad89efbc8ce69cace7ab99e4b88de6ada1e8bf8ee4be86e887aa-e799bee5baa6-(Baiducom)-e79a84e8a8aae5aea2-!!.aspx/
  - /columns/e5be88e68ab1e6ad89efbc8ce69cace7ab99e4b88de6ada1e8bf8ee4be86e887aa-e799bee5baa6-(Baiducom)-e79a84e8a8aae5aea2-!!.aspx/
wordpress_postid: 91
---
沒什麼特別的，只是針對[這次的盜文事件](/post/e58f88e8a2abe79b9ce69687e4ba86-.aspx)，我很不滿意百度 (Baidu.com) 的處理方式而以。

幾個月前曾[發生過](/post/e58fafe683a12c-e7ab9fe784b6e581b7e8b2bce68891e79a84e69687e7aba0-.aspx) BLOGGER.COM 有人直接把我的文章一字不漏的貼在他的 BLOG 上，沒有標示文章出處，最後用我破破的英文跟 GOOGLE 反映之後，GOOGLE 立即作了處理，[關閉那位使用者的網頁](/post/e981b2e4be86e79a84e6ada3e7bea9.aspx)。

這次碰到類似的情況，有耐心的人就聽我講完這無聊的故事吧。無意間我在對岸的入口網站 [百度知道] (類似奇摩知識+的網站)，發現有人拿我的文章，[一字不漏的貼上去](http://zhidao.baidu.com/question/35002663.html)回答問題賺點數，一樣沒有標示文章出處，感到非常的不滿，馬上註冊了帳號，留下回應表示該文侵犯了我的權益，要求引用文章要註明出處，同時也跟[站方反應](http://tieba.baidu.com/f?kz=419005957)了這個情況，要求站方作妥善的處理。

原本以為事情會像上次一樣，跟 GOOGLE 一樣的處理方式結束。沒料到...

1. 隔天，發現我的留言被刪了? 嗯... 再補一次。
2. 跟站方反應的結果? 竟然說這個不尊重智財權的使用者沒有違反規定???? 所以不做任何處理。
3. 另一方面，留言留了不斷的被刪除，到現在已經被刪了第五次了，第六次的留言不知道會留到什麼時後...。

很無聊的戲就這樣一直演下去... 就是不斷的抗議又被刪除，跟站方反應卻又不理睬...。看來小蝦米是對抗不了大鯨魚的，也只能這樣了。其實我除了文章被盜貼之外沒有什麼具體的損失，就是心理很不爽而以，而更離譜的是百度站方處理的態度...。

資訊隨手可得，不代表資訊是可以任意踐踏的。免費的資訊，不用付費不代表就不需要尊重，也許對岸還有很多使用者沒建立起這樣的觀念，但是百度站方的處理方式也令我跌破眼鏡，有這樣的站方難怪會縱容這樣的使用者... :@

身為渺小不起眼 BLOG 主人，我也只能用消極的抗議，來表示我的不滿。除了寫這篇文章以外，也順帶來個 ASP.NET HttpModule 教學...。針對這次事件，我特地在本站加上了這個 HttpModule，只要查出使用者是透過任何由百度提供的 LINK 而連到本站的話，都會顯示這頁抗議的畫面，如下:

![image](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/image_3.png)

顯示了 60 秒抗議畫面後，就會自動進如原本要連結的頁面。在透過正規的管道而得不到妥善的處置，我也只能用消極的抗意來表達我的不滿。請看到的人留個 MESSAGE 支持一下吧，或是有推推王帳號的人也幫忙推一下，一起對不重視智慧財產權的百度表答不滿 & 抗議!

抗議之餘，本站再怎樣也是討論進階 .NET 技術的網站，就拿這次的案例，看看這樣的 HttpModule 該怎麼處理! 未來如果你也不幸碰到這樣的事件 (最好不要碰到)，可以拿出來用一用! 要替網站加上這樣的功能很簡單，只要在 Web.config 把你寫的 HttpModule 掛上就好。一旦掛上，所有針對這個網站的 Http Request 都會經過你的 HttpModule 處理，任何一個 LINK 都跑不掉!

**ASP.NET HttpModule開發範例: 把所有來自百度的使用者，引導到抗議的畫面!**

```csharp
public class SiteBlockerHttpModule : IHttpModule
{
   public void Init(HttpApplication context)
   {
       context.AuthenticateRequest += new EventHandler(context_AuthenticateRequest);
   }

   void context_AuthenticateRequest(object sender, EventArgs e)
   {
       HttpApplication application = sender as HttpApplication;
       string referer = application.Context.Request.ServerVariables["HTTP_REFERER"];

       if (string.IsNullOrEmpty(referer) == false)
       {
           Uri refererURL = new Uri(referer);
           if (refererURL.Host.ToUpperInvariant().Contains("BAIDU.COM") == true)
           {
               application.Context.Server.Transfer("~/Blogs/ShowBlockedMessage.aspx");
           }
       }
   }
}
```

---

後記: 針對這次事件的記錄:

1. 2008年6月22日, 下午 11:59:16，[第一次張貼抗議的回應](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/01.jpg)
2. 2008年6月23日, 上午 11:44:50，[第二次張貼抗議的回應](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/02.jpg)
3. 2008年6月23日, 下午 04:53:44，[第三次張貼抗議的回應](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/03.jpg)
4. 2008年6月23日, 下午 11:32:05，[第四次張貼抗議的回應](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/04.jpg)
5. 2008年6月25日, 下午 08:08:14，[第五次張貼抗議的回應](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/05.jpg)
6. 2008年6月26日, 下午 07:26:36，[第六次張貼抗議的回應](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/06.jpg)
7. 2008年6月28日, 上午 12:58:54，[百度站方的回應](/wp-content/be-files/WindowsLiveWriter/Baidu.com_BED/07.jpg)
