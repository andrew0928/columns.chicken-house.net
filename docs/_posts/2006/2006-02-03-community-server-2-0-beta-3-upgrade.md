---
layout: post
title: "換新系統了!! CS 2.0 Beta 3"
categories:

tags: ["有的沒的"]
published: true
comments: true
redirect_from:
  - /2006/02/03/換新系統了-cs-2-0-beta-3/
  - /columns/post/2006/02/03/e68f9be696b0e7b3bbe7b5b1e4ba86!!-CS-20-Beta-3.aspx/
  - /post/2006/02/03/e68f9be696b0e7b3bbe7b5b1e4ba86!!-CS-20-Beta-3.aspx/
  - /post/e68f9be696b0e7b3bbe7b5b1e4ba86!!-CS-20-Beta-3.aspx/
  - /columns/2006/02/03/e68f9be696b0e7b3bbe7b5b1e4ba86!!-CS-20-Beta-3.aspx/
  - /columns/e68f9be696b0e7b3bbe7b5b1e4ba86!!-CS-20-Beta-3.aspx/
  - /blogs/chicken/archive/2006/02/03/1407.aspx/
wordpress_postid: 234
---

雖然平常啥軟體有新版, 我都會手癢的想換來看看, 不過這套 BLOG ( CommunityServer ) 倒是特例, 從 1.0 release 後就再也沒動過了, 為的當然就是我自己加的那堆功能...

<!--more-->

[.TEXT 的編輯介面補強 (自己爽一下)..](/post/TEXT-e79a84e7b7a8e8bcafe4bb8be99da2e8a39ce5bcb7-(e887aae5b7b1e788bde4b880e4b88b).aspx)

[修改 Community Server 的 blog editor](/post/e4bfaee694b9-Community-Server-e79a84-blog-editor.aspx)

[修改 Community Server 的 blog editor ( Part II )](/post/e4bfaee694b9-Community-Server-e79a84-blog-editor-(-Part-II-).aspx)

[Photo Gallery 啟用 !!](/post/Photo-Gallery-e5959fe794a8-!!.aspx)

[community server 改造工程](/post/community-server-e694b9e980a0e5b7a5e7a88b.aspx)

[ChickenHouse.Web.CommunityServiceExtension 新增功能](/post/ChickenHouseWebCommunityServiceExtension-e696b0e5a29ee58a9fe883bd.aspx)

[ChickenHouse.Web.CommunityServerExtension 新功能 之 2](/post/ChickenHouseWebCommunityServerExtension-e696b0e58a9fe883bd-e4b98b-2.aspx)

列在一起, 看起來還真多... 不過後來還是破戒了, 因為 Server 升級了, OS 也換成 64 位元版本的 windows 2003 .. 舊版的 CS 1.0 碰到了這個鳥問題, 不得不升級...

[**如何在 64 位元版的 Windows 上切換 32 位元版的 ASP.NET 1.1 與 64 位元版的 ASP.NET 2.0**](http://support.microsoft.com/kb/894435/zh-tw)

> **IIS 6.0 同時支援 32 位元模式及 64 位元模式。但是，IIS 6.0 不支援同時在 64 位元版的 Windows 上執行兩種模式。ASP.NET 1.1 只能在 32 位元模式中執行。ASP.NET 2.0 可以在 32 位元模式或 64 位元模式中執行。因此，如果要同時執行 ASP.NET 1.1 和 ASP.NET 2.0，您必須在 32 位元模式中執行 IIS。**

嘖嘖嘖, CS 1.0 只能在 ASP.NET 1.1 環境下運作, 直接丟在 ASP.NET 2.0 下會跑不了. 偏偏 Microsoft 又不提供 64 位元版本的 .NET 1.1 Runtime, 搞到最後, 為了這舊版的 CS, 我整個 IIS 都得在 32 位元模式下運作... [:@]

真是枉費我破除萬難升級上來的新系統, 嘖嘖嘖... 所以只好忍痛暫時犧牲我修改的那些功能, 改用官方的 2,0 beta 3 版本 (就是現在用的這套).

其實換完之後感覺還不錯, 雖然少掉我之前修正了不少 sea 不滿意的地方, 但是我頂多改改別人的小地方, 官方版本才有辦法做根本上的改進, 到底好在那裡, 用過就知道啦 [H], 以後再慢慢講...
