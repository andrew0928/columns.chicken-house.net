---
layout: post
title: "CS Control: Recent Comments"
categories:

tags: []
published: true
comments: true
redirect_from:
  - /2006/05/21/cs-control-recent-comments/
  - /columns/post/2006/05/21/CS-Control-Recent-Comments.aspx/
  - /post/2006/05/21/CS-Control-Recent-Comments.aspx/
  - /post/CS-Control-Recent-Comments.aspx/
  - /columns/2006/05/21/CS-Control-Recent-Comments.aspx/
  - /columns/CS-Control-Recent-Comments.aspx/
  - /blogs/chicken/archive/2006/05/21/1542.aspx/
wordpress_postid: 228
---

自從換了 CS 2.0, 就一直被抱怨沒有顯示最新回應的功能... ( 之前 1.0 版我有[自己改一個](/post/ChickenHouseWebCommunityServerExtension-e696b0e58a9fe883bd-e4b98b-2.aspx) ), 不過 CS 2.0 存取資料庫的方式改用 Provider Model, 除非自己改寫 Data Provider, 否則只能用它提供的 API 才能拿到你要的 data ...

因為這一點被卡了很久, 加上 2.0 新的 Theme Model, Orz, 想要在畫面加一段字, 要找到在那裡加是最麻煩的地方, 找到之後一切就簡單多了... 研究了半天加上官方網站的討論, 總算研究出來該如何下手...

<!--more-->

最後的方法大致是這樣, CS 的 "Post" 物件, 代表了 CS 裡主要的幾種資料型態, 包括 blog 文章, blog comment, forum 的討論串, album 裡的相片... etc, 所以透過 DataProvider可以拿出原始資料, 會用 WeblogPost 型態的物件傳回.

另外 Theme 則沒那麼簡單... 每個 Theme Control 都會對應到同名的 Skin-#####.ascx, 因此在每套 theme file 裡會去引用到這些 user control, 同時 user control 裡必需再定義 child control, 剩下的動作你得自己在 dll 裡處理好..

總算是研究出來了, 哇哈哈, 現在我們家的 CS 又有跟別人不一樣的特色了.. [:$]

![Recent Comments](/images/2006-05-21-cs-control-recent-comments/recent-comments.jpg)
