---
layout: post
title: "三個好用的 ASP.NET HttpHandler"
categories:

tags: [".NET","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2004/12/15/三個好用的-asp-net-httphandler/
  - /columns/post/2004/12/15/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx/
  - /post/2004/12/15/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx/
  - /post/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx/
  - /columns/2004/12/15/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx/
  - /columns/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx/
  - /blogs/chicken/archive/2004/12/15/183.aspx/
wordpress_postid: 316
---

花了幾個晚上寫了這幾個 ASP.NET HttpHandler, 貼上來現一下... 寫這些東西的起因都只有一個字, 就是"懶"!! 科技果然都是來自惰性...

1. ChickenHouse.Web.HttpHandlers.MediaServiceHttpHandler

> video / audio file 直接放網頁, 很吃頻寬, 尤其我這種用ADSL架的小站沒有頻寬可以揮豁, 只好把這種大檔案放在 windows media service. 不過老實說挺麻煩的, 我自己都嫌麻煩了, 還要教會老婆大人什麼時後要用 http://www.chicken-house.net, 什麼時後要用 mms://www.chicken-house.net, ... !@#%@^&
> 
> 這個 http handler 就可以把這惱人的動作解決掉了, 放在 web 下的檔案會自動轉到 media service, 只要你的 media player 是 7.0 以上, 一切就全自動了!

2. ChickenHouse.Web.HttpHandlers.RssMonitorHttpHandler

> 又是個懶人作品... 常常想看某個目錄多了什麼檔案, 雖然可以用時間排序, 但是卻忘了上次是什麼時後看的...
> 
> 這時 RSS 訂閱就派上用場了. 這個 HttpHandler 會把某個目錄下的所有檔案都當成網頁, 新增檔案就像 blog 新貼文章一樣, 你的 Rss Reader 就會通知你了.
> 
> 不過這個能幹嘛? 對付全都是 *.html 做出來的靜態網頁就超好用,?什麼事都不用作就可以有 "RSS 訂閱" 的功能了. 拿[小皮的網頁[RSS]](/files/baby.rss)示範...

3. ChickenHouse.Web.HttpHandlers.ZipVirtualFolderHttpHandler

> 這也是對付靜態網頁用的. 老婆大人常喜歡用 ACDSee 產生相簿網頁, 我則喜歡用 [Windows XP : Slide Show Generator Power Toys](http://www.microsoft.com/windowsxp/downloads/powertoys/xppowertoys.mspx) 產生相簿網頁. 但是除了掛上網站外, 常會另外再放個 zip 檔方便大家下載. 一樣的東西放兩份以後維護就很頭痛...
> 
> 沒錯, 又是因為懶, 所以就寫了這個 Http Handler. 就像 WinXP 檔案總管一樣, 會把 ZIP 檔當成一個目錄, 這個 HttpHandler 也會把 *.zip 當成網頁的一個目錄, 以後像上面講的情況, 就只要擺個 zip 檔到網站上就可以了
> 
> 例如:  
> [http://www.chicken-house.net/files/chicken/slide.zip?download](/files/chicken/slide.zip?download) 就是普通的 zip 檔下載,  
> [http://www.chicken-house.net/files/chicken/slide.zip](/files/chicken/slide.zip) 就可以看 zip 檔的內容  
> [http://www.chicken-house.net/files/chicken/slide.zip/default.htm](/files/chicken/slide.zip/default.htm) 就可以直接連到 zip檔內的檔案了
> 
> 以後網站只要在裡面放一堆 zip 檔就好了, 不然每次一堆檔案整理起來也是很累人...

純現寶用, 哈哈... 崇拜的話就留個回應就好 (H)

Sample Code 下載:

[ChickenHouse.Web.zip](/wp-content/be-files/ChickenHouse.Web.zip)
