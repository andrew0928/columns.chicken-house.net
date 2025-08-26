---
layout: post
title: "[Tips] 用 磁碟鏡像 無痛更換硬碟"
categories:

tags: ["Tips","技術隨筆","敗家","有的沒的"]
published: true
comments: true
redirect_from:
  - /2010/03/06/tips-用-磁碟鏡像-無痛更換硬碟/
  - /columns/post/2010/03/06/Tips-e794a8-e2809ce7a381e7a29fe98fa1e5838f-e784a1e7979be69bb4e68f9be7a1ace7a29f.aspx/
  - /post/2010/03/06/Tips-e794a8-e2809ce7a381e7a29fe98fa1e5838f-e784a1e7979be69bb4e68f9be7a1ace7a29f.aspx/
  - /post/Tips-e794a8-e2809ce7a381e7a29fe98fa1e5838f-e784a1e7979be69bb4e68f9be7a1ace7a29f.aspx/
  - /columns/2010/03/06/Tips-e794a8-e2809ce7a381e7a29fe98fa1e5838f-e784a1e7979be69bb4e68f9be7a1ace7a29f.aspx/
  - /columns/Tips-e794a8-e2809ce7a381e7a29fe98fa1e5838f-e784a1e7979be69bb4e68f9be7a1ace7a29f.aspx/
wordpress_postid: 20
---

老是寫一堆像外星文，沒人看的懂的 multi-threading 文章，偶爾也來換換口味吧。前陣子把 SERVER 的兩顆 750GB HDD (RAID1) 升級了一下，升級成兩顆 1.5TB HDD (RAID1)。更換硬碟是小事，不過這個硬碟上有些服務，如網站，資料庫，還有一些重要資料，跟分享資料夾，想一想要更換也是挺囉唆的...。

想了幾個辦法，不過都不符合我既懶又挑毛病的個性... 原本考慮的更換方式有:

1. 硬上... 新硬碟裝上去，檔案COPY過去，能停的服務就停掉，花一堆時間搬資料，然後再恢復原服務 (如 SQL、IIS等等)。至於比較麻煩的，像是目錄分享的，只好移掉再重建。中斷服務的時間就是從關機裝硬碟，一直到全部完成為止。

2. 用 disk clone 的工具，如 true image / ghost 之類的軟體。不過這樣通常得停機做 clone, 750GB 也是要執行好一段時間，加上我這次買的是 [Advanced Format](http://www.wdc.com/wdproducts/library/WhitePapers/CHT/2579-771430.pdf) 的硬碟，用這類工具會有效能的問題，事後還得校正回來… ouch, 算了...

想來想去，我用的是 windows server, 有內建的 Mirror set, 就拿來用一用好了。我真正作的是把 mirror set 的兩顆都升級，不過為了簡化說明，我底下的例子就只以替換一般的硬碟就好，反正道理是一樣的。

說穿了不值錢，就是用 mirror 的磁碟複製特性，加上 extend volume 的功能，我除了需要關機裝上新硬碟之外，其它包含資料複製的所有時間，原服務都不用中斷 (當然速度會慢一點)，所有服務的設定也都不用修改，算是既無腦又防呆的完美方案... 只要簡單的按幾下滑鼠就可以達成我的目標。

直接來看看怎麼作的吧! 很簡單，先利用 mirror 把資料轉移到新硬碟... 然後中斷 mirror, 再用 extend volume 把磁區大小調大就可以收工了。來看分解步驟:

1. 我原本的磁碟組態是長這個樣子 (圖我是事後用 VM 模擬的)，其中 Disk 1 (8.00GB) 就是我要換掉的...

   ![image](/images/2010-03-06-tips-painless-hard-drive-replacement-with-disk-mirroring/image.png)

2. 關機裝上一顆新的硬碟 Disk 2 之後，變成這樣 (Disk 2 (16.00GB) 是新的硬碟):

   ![image](/images/2010-03-06-tips-painless-hard-drive-replacement-with-disk-mirroring/image_1.png)

3. 把 disk1 / disk2 做成磁碟鏡像之後，就變成這樣:

   ![image](/images/2010-03-06-tips-painless-hard-drive-replacement-with-disk-mirroring/image_2.png)

4. 鏡像做好，Resync 完成後，就可以中斷鏡像了。中斷之後變成這個樣子:

   ![image](/images/2010-03-06-tips-painless-hard-drive-replacement-with-disk-mirroring/image_3.png)

5. 目前為止，看來磁碟轉移已經完成了，剩下就是想辦法把後面的空間吃進來。接下來的就用 Extend Volume 括大 D: 的大小:

   ![image](/images/2010-03-06-tips-painless-hard-drive-replacement-with-disk-mirroring/image_4.png)

   ![image](/images/2010-03-06-tips-painless-hard-drive-replacement-with-disk-mirroring/image_5.png)

之後就大功告成了。這方法不但簡單，而且整個過程中，全程 D:\ 都可以正常的使用。除了 (1) --> (2) 需要關機裝硬碟之外， (2) ~ (5) 全程，放在 D:\ 的 SQL DB，IIS 網站，還有 pagefile 通通都正常運作中。有了 windows server 的磁碟陣列還真是好用啊 :D

不過，事情也是有黑暗面的... 這個方法是有幾個小缺點啦...

1. 被迫使用 "動態磁碟" :
   
   dynamic disk 其實不是什麼缺點啦，不過你要是會用到其它 OS，像 linux 之類的，或是用其它的磁碟管理軟體，可能就不認得了。這是缺點之一..

2. 只有 windows server 可以使用:
   
   desktop os (windows 2000 pro, xp, vista, win7) 都只支援部份的磁碟管理功能，這作法關鍵的 mirror 是不支援的... 只能乾瞪眼 @@

3. Extend Volume 只適用 windows 2008 以上的版本:
   
   記得 windows 2003 只支援到 span volume, 在 disk manager 裡還是會顯示兩個 partition, 只不過只會有一個磁碟機代號，容量會是兩個加起來的而已。一樣啦，是不會有什麼大問題，看起來不大爽而已 XD

偶爾換個口味，貼些小品文章，這邊我也不是很專業，有啥更好的作法也歡迎留 comment 啊 :D
