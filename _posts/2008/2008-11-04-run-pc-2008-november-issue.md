---
layout: post
title: "[RUN! PC] 2008 十一月號"
categories:
- "RUN! PC 專欄文章"
tags: [".NET","RUN! PC","作品集","多執行緒","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2008/11/04/run-pc-2008-十一月號/
  - /columns/post/2008/11/04/RUNPC-2008-11.aspx/
  - /post/2008/11/04/RUNPC-2008-11.aspx/
  - /post/RUNPC-2008-11.aspx/
  - /columns/2008/11/04/RUNPC-2008-11.aspx/
  - /columns/RUNPC-2008-11.aspx/
wordpress_postid: 52
---
![IMG_0208](/wp-content/be-files/WindowsLiveWriter/RUNPC2008_1D6E/IMG_0208_1.jpg)

YA! 第四篇!! :D 還是一樣要先感謝一下編輯賞光，讓我有點空間寫些不一樣的東西。

基本的執行緒相關的程式設計跟函式庫，講的差不多了，其實這些也沒什麼好寫的。接下來打算寫一些應用的模式，來談談有那些方法，那些設計方式才能夠有效的發揮多執行緒的優點。看了 .NET Framework 4.0 / Visual Studio 2010 的 ROADMAP，有一大部份的重點擺在平行處理，INTEL年底也要發表四核 + HT 的 CPU ( WINDOWS 會認為有八個處理器 )，軟硬體都備齊了，剩下的就是程式設計師的巧思了。

其實之前貼過幾篇類似主題的文章，只是這次把它統合起來介紹一下。生產線模式，如果簡化後就是 [[生產者消費者](/post/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx)] 的模式，而把它徹底一點的應用，則是上回提到 [[Stream Pipeline](/post/MSDN-Magazine-e996b1e8ae80e5bf83e5be97-Stream-Pipeline.aspx)] .. 

這篇也是第一次在雜誌上嘗試說明比較偏設計概念的文章，實作比較少，很怕不合讀者的口味... 應該不會貼了就沒續篇了吧? :P 有買雜誌的記得讀者回函填一下，哈哈，也算是點鼓勵。這次範例程式也是 Console application (我不會寫太炫的程式 :P )，需要的可以點 [[這裡](/admin/Pages/wp-content/be-files/RUNPC-2008-11.zip)] 下載!
