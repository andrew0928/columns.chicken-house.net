---
layout: post
title: "[RUN! PC] 2010 五月號 - TxF讓檔案系統也能達到交易控制"
categories:
- "RUN! PC 專欄文章"
tags: [".NET","RUN! PC","Transactional NTFS","作品集","作業系統","技術隨筆","物件導向"]
published: true
comments: true
redirect_from:
  - /2010/05/05/run-pc-2010-五月號-txf讓檔案系統也能達到交易控制/
  - /columns/post/2010/05/05/RUNPC-2010-05.aspx/
  - /post/2010/05/05/RUNPC-2010-05.aspx/
  - /post/RUNPC-2010-05.aspx/
  - /columns/2010/05/05/RUNPC-2010-05.aspx/
  - /columns/RUNPC-2010-05.aspx/
wordpress_postid: 15
---

![image](/wp-content/be-files/image_10.png)

五月號就刊出來，還真有點意外 :D，這次稿件趕不及，晚了幾天才交出去，編輯大人還是讓我上五月號啦，真是感謝 :D

之前執行緒的系列，是打算把各種應用執行緒的演算法都介紹一下，寫了五篇就沒靈感了。實際寫CODE的技巧倒是很多可以介紹，不過 .NET FX 4.0 出來之後，這些鎖碎的 coding 技巧又大幅簡化了，除非有特別的演算法需要 (如同之前那五篇 :D)，否則還自己拿 Thread 物件硬幹已經沒什麼意義了，所以就換另一個我有興趣的主題 - Transactional NTFS 來寫。

這系列第一篇出爐了，主要就是先介紹它的觀念及如何入門，國內這類資訊還不多，我就野人獻曝寫了一篇，試著寫看看了。較鎖碎的實作技巧 (如 P/Invoke) 我會直接貼 BLOG，而較完整的概念及實作探討等等就會整理成文章拿來投稿了。

再次感謝各位支持啦，底下有範例程式跟一些參考資源的 LINK，需要的歡迎取用 :D

範例程式:

1. Visual Studio 2008 Project (C#) File: [TransactionDemo.zip](/wp-content/be-files/TransactionDemo.zip)

參考資訊:

1. AlphaFS: Brining Advanced Windows FileSystem Support to .NET
   [http://alphafs.codeplex.com/](http://alphafs.codeplex.com/)

2. MSDN magazine (July 2007): Enhance Your Apps With File System Transactions
   [http://msdn.microsoft.com/en-us/magazine/cc163388.aspx](http://msdn.microsoft.com/en-us/magazine/cc163388.aspx)

3. B# .NET BLOG: Windows Vista - Introducing TxF In C#
   Part 1: [Transacted File Delete](http://community.bartdesmet.net/blogs/bart/archive/2006/11/05/Windows-Vista-_2D00_-Introducing-TxF-in-C_2300_-_2800_part-1_2900_-_2D00_-Transacted-file-delete.aspx)
   Part 2: [Using System.Transactions and the DTC](http://community.bartdesmet.net/blogs/bart/archive/2006/11/19/Windows-Vista-_2D00_-Introducing-TxF-in-C_2300_-_2800_part-2_2900_-_2D00_-Using-System.Transactions-and-the-DTC.aspx)
   Part 3: [CreateFileTransacted Demo](http://community.bartdesmet.net/blogs/bart/archive/2007/02/21/windows-vista-introducing-txf-in-c-part-3-createfiletransacted-demo.aspx)

4. Code Project: Windows Vista TxF / TxR
   [http://www.codeproject.com/KB/vista/KTM.aspx](http://www.codeproject.com/KB/vista/KTM.aspx)

5. BLOG: Because we can
   [http://blogs.msdn.com/because_we_can/archive/2005/05/18/419809.aspx](http://blogs.msdn.com/because_we_can/archive/2005/05/18/419809.aspx)
   Discussion and explanation relating to the Transactional NTFS feature coming in Longhorn, plus any other interesting anecdotes...

6. Performance Consoderations for Transactional NTFS
   [http://msdn.microsoft.com/en-us/library/ee240893(VS.85).aspx](http://msdn.microsoft.com/en-us/library/ee240893(VS.85).aspx)

7. When to Use Transactional NTFS
   [http://msdn.microsoft.com/en-us/library/aa365738(VS.85).aspx](http://msdn.microsoft.com/en-us/library/aa365738(VS.85).aspx)
