---
layout: post
title: "修改 Community Server 的 blog editor"
categories:

tags: ["ASP.NET","Community Server","有的沒的"]
published: true
comments: true
redirect_from:
  - /2005/03/19/修改-community-server-的-blog-editor/
  - /columns/post/2005/03/19/e4bfaee694b9-Community-Server-e79a84-blog-editor.aspx/
  - /post/2005/03/19/e4bfaee694b9-Community-Server-e79a84-blog-editor.aspx/
  - /post/e4bfaee694b9-Community-Server-e79a84-blog-editor.aspx/
  - /columns/2005/03/19/e4bfaee694b9-Community-Server-e79a84-blog-editor.aspx/
  - /columns/e4bfaee694b9-Community-Server-e79a84-blog-editor.aspx/
  - /blogs/chicken/archive/2005/03/19/345.aspx/
wordpress_postid: 268
---

![Community Server Editor](/wp-content/be-files/cs_editor.jpg)

好像每次換一套 blog, 我的宿命就是先改 editor, 讓它可以貼圖及貼表情符號... 哈哈 ![emotion](/Emoticons/emotion-2.gif)

CommunityServer 用的是之前我介紹過的 FreeTextBox, 還不難改, 但是討厭的是 CS 並不是直接內嵌 FTB, 而是  
中間多擋了一層 CS 自己的 Editor Wrapper... ![emotion](/Emoticons/emotion-8.gif), 然後 CS 提供的 source code 就是少了這一塊...

沒辦法, 所以改出來的東西就有點格格不入, 多的工具列得排在畫面上方, 沒辦法加到原本 FTB 自己的工具列.  
不然 FTB 其實還有很多好用的工具列可以打開... 真是可惜..
