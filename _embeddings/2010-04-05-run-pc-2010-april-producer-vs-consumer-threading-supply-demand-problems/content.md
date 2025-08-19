---
layout: post
title: "[RUN! PC] 2010 四月號 - 生產者vs消費者– 執行緒的供需問題"
categories:
- "RUN! PC 專欄文章"
tags: [".NET","RUN! PC","作品集","多執行緒","技術隨筆","物件導向"]
published: true
comments: true
redirect_from:
  - /2010/04/05/run-pc-2010-四月號-生產者vs消費者-執行緒的供需問題/
  - /columns/post/2010/04/05/RUNPC-2010-04.aspx/
  - /post/2010/04/05/RUNPC-2010-04.aspx/
  - /post/RUNPC-2010-04.aspx/
  - /columns/2010/04/05/RUNPC-2010-04.aspx/
  - /columns/RUNPC-2010-04.aspx/
wordpress_postid: 16
---

![image](/wp-content/be-files/image_9.png)

隔了足足一年，趁著過年，生出第五篇了 :D，再次感謝編輯賞光啦，願意刊登我寫的題材...

這篇 [生產者/消費者] 其實是延續上一篇 [生產線模式] 而來的，生產線模式，是利用 PIPE 的方式，把工作切成各個階段同時進行。而生產者消費者，則是去探討兩個階段之間如何做好進度的協調。這篇除了講講處理的原則之外，也實作了BlockQueue來簡化這個問題。

其實更漂亮的用法，是我在 MSDN Magazine 上看到的 BlockingStream, 直接把它作成 System.IO.Stream 的衍生類別。像那些包裝成 Stream 的資料處理 (像是壓縮、加密、或是 Socket 這類)，都很適合。不過一般情況下不是所有應用都能套上 Stream 的模式，因此就有了把它包裝成 Queue 的念頭，也就是這篇寫的 BlockQueue 的應用。

相關的東西其實過去也寫了幾篇，只不過 BLOG 寫的都比較瑣碎，都是針對特定主題較深入的討論，而投稿的文章就會比較完整的介紹原理及作法等等，細節就沒辦法兼顧了。有興趣的讀者可以參考一下我部落格的相關文章 :D 這期的範例程式可以在底下下載，相關的 LINK 也列在底下。

再次謝謝各位支持啦 :D

[MSDN Magazine 閱讀心得: Stream Pipeline](http://columns.chicken-house.net/post/MSDN-Magazine-e996b1e8ae80e5bf83e5be97-Stream-Pipeline.aspx)
[RUN!PC 精選文章 - 生產線模式的多執行緒應用](http://columns.chicken-house.net/post/RUN!PC-e7b2bee981b8e69687e7aba0-e7949fe794a2e7b79ae6a8a1e5bc8fe79a84e5a49ae59fb7e8a18ce7b792e68789e794a8.aspx)
[[RUN! PC] 2008 十一月號](http://columns.chicken-house.net/post/RUNPC-2008-11.aspx) 生產線模式的多執行緒應用
[生產者 vs 消費者 - BlockQueue 實作](http://columns.chicken-house.net/post/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx)
