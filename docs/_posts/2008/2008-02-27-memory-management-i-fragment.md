---
layout: post
title: "Memory Management - (I). Fragment ?"
categories:
- "系列文章: Memory Management"
tags: [".NET","作業系統","技術隨筆","有的沒的"]
published: true
comments: true
permalink: "/2008/02/26/memory-management-i-fragment/"
redirect_from:
  - /columns/post/2008/02/27/Memory-Management-(I)-Fragment-.aspx/
  - /post/2008/02/27/Memory-Management-(I)-Fragment-.aspx/
  - /post/Memory-Management-(I)-Fragment-.aspx/
  - /columns/2008/02/27/Memory-Management-(I)-Fragment-.aspx/
  - /columns/Memory-Management-(I)-Fragment-.aspx/
  - /columns/post/2008/02/27/Memory-Management---(I)-Fragment-.aspx/
  - /post/2008/02/27/Memory-Management---(I)-Fragment-.aspx/
  - /post/Memory-Management---(I)-Fragment-.aspx/
  - /columns/2008/02/27/Memory-Management---(I)-Fragment-.aspx/
  - /columns/Memory-Management---(I)-Fragment-.aspx/
  - /blogs/chicken/archive/2008/02/27/3009.aspx/
wordpress_postid: 120
---


程式越寫, 越覺的課本教的東西很重要... 最近碰到一些記憶體管理的問題, 想到以前學 C 跟 OS 時, 大家都有個理想.. 

> 只要 OS 支援虛擬記憶體, 以後寫 code 都不用耽心 Memory 不夠...


聽起來很合理, 虛擬記憶體本來就是讓開發人員省事的機制啊... 當然前提不超過硬體限制, 像是 32 位元的程式就不能超過 4GB. Virtual Memory 也帶來很多好處. 除了可以以硬碟空間換取記憶體空間之外, 因為 swap 需要的 paging 機制, 也間接的解決了 "PHYSICAL" Memory Fragment 的問題. 

怎麼說? 邏輯的記憶體位址, 對應到實體的記憶體位址, 不一定是連續的. 有點像是硬碟的一個大檔案, 實際上可能是散在硬碟的好幾個不連續區塊. 除了效能問題之外, 是沒有任何不同的. 

因為這堆 "便民" 的機制, 現在的程式設計師還會考慮這種問題的人, 少之又少. 有的還聽不懂你在問啥... 以前在 BBS 討論版看到一個問題, 印像很深刻, 算一算十來年了還記得... 把這問題貼一下, 主題就是 programmer 到底該不該耽心 memory fragment 的問題? 實驗的方式很有趣: 

1. 連續以固定 size (ex: 4KB) allocate memory, 直到沒有記憶體為止
1. 開始 free memory. 不過是跳著釋放. 比如 (1) 取得的一連串記憶體, 只放奇數位子 1st, 3rd, 5th, 7th .... 
1. 挑戰來了, 這時應該清出一半空間了. 如果我再 allocate 5KB 的記憶體, OS 會成功清給我? 還是會失敗?


簡單畫張圖說明，就像這樣: 

![](/wp-content/be-files/WindowsLiveWriter/MemoryManagementI.Fragment_45D5/image_3.gif)


其中:
(1) 就是在可用的定址空間內盡量塞，因為虛擬記憶體的關係，不管實體記憶體夠不夠，都能夠使用。 
(2) 就是跳著釋放記憶體後的分佈情況。 
(3) 圖上看來已經沒有能夠容納 "大一點" 區塊的空間了，那麼 [?] 這個區塊到底還放不放的下? 

來來來, 大挑戰... 這種程式千萬別在自己家裡亂玩... 也別在你按不到 reset 開關的電腦亂玩 (ex: 遠端連到機房的 server) ... 前題是用 C / C++ 這類可以直接操作 pointer 的 language. OS 不限, 覺的 Linux 強就用 Linux, 喜歡 Gates 的就用 windows... 32 / 64 位元都可以... 

先賣個關子, 結果會是怎麼樣? 不同的 OS 會有不同的結果嗎? 64位元會有不同嗎? 有興趣可以試看看，懶的寫 code 也可以猜看看! 
