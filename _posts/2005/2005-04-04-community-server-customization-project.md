---
layout: post
title: "community server 改造工程"
categories:

tags: []
published: true
comments: true
redirect_from:
  - /2005/04/04/community-server-改造工程/
  - /columns/post/2005/04/04/community-server-e694b9e980a0e5b7a5e7a88b.aspx/
  - /post/2005/04/04/community-server-e694b9e980a0e5b7a5e7a88b.aspx/
  - /post/community-server-e694b9e980a0e5b7a5e7a88b.aspx/
  - /columns/2005/04/04/community-server-e694b9e980a0e5b7a5e7a88b.aspx/
  - /columns/community-server-e694b9e980a0e5b7a5e7a88b.aspx/
  - /blogs/chicken/archive/2005/04/04/527.aspx/
wordpress_postid: 263
---

自從裝了 community server 1.0 rtm 之後, 就一直對它東補補西改改的, 到現在家裡太座對它不滿的地方終於修的差不多了, 我自己補的新功能也補的差不多了, 做個總結, 總共改的地方有:

1. TextEditorWrapper 改進:  
   CS 1.0 用的是 FTB 3.0, 有很多進階的編輯功能都沒被打開, 改寫了自己的 TextEditorProvider, 掛上 CS 後就通通啟用了 ![emotion](/Emoticons/emotion-2.gif)

2. 啟用 FTB 3.0 的 "Insert Image From Gallery" 功能:  
   FTB 3.0 內建了 image gallery, 可以讓使用者上傳要插入的圖檔, 就像 office 裡的多媒體藝廊一樣, 花了點時間也把這地方補好了, 張貼 blog 及 forum 裡的 post 都可以啟用這功能

3. FTB 3.0 多了一排 emotion icons 的工具列, 點下去就能插入表情符號

4. CS 相簿批次上傳:  
   CS並沒有提供批次上傳照片的功能, 我自己寫了 web service 掛上去, 再照這個 api 寫了 command line tools, 可以把 local 的相片批次縮小後再上傳, 同時會自動建立相關的 group / gallery

5. 改掉一些我不喜歡的 page:  
   首頁: 原本那堆字都被我改掉了, 改成 gallery / blogs / forums 的 asp.net control  
   Blog 首頁: 也被我改掉了, 改成 blog 列表  
   Blog Homepage: 也改掉了, 只會秀 title, 內文要點進去才有 ( 應太座需求, 不得不改...![emotion](/Emoticons/emotion-15.gif) )

目前就大概做到這樣. 用起來真有成就感啊 ![emotion](/Emoticons/emotion-11.gif)!! 接下來的動作就是要把舊的 ChickenHouse Forum 裡的資料轉到 CS 來...
