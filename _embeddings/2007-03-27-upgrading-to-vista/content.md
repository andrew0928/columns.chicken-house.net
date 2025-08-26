家裡的 PC 決定改裝 vista 了. 原本的機器是跑 windows 2003 x64, 機器很閒, web site + file server 跟本用不到 5% 的 loading, 就決定改為桌機...

計劃中這台 pc 要能處理這些事:

1. 最基本的 network service, 包括 RRAS, IIS, Media Service, SQL express, DNS, DHCP, SMTP.
2. File Server, 原本用了 windows 內建的 RAID-1, 還有 Volume Shadow Copy, 保護自己的檔案, 如照片, DV拍的影片, 還有一些個人檔案等...
3. MCE, 看電視, 錄電視, 節目表... etc
4. Batch job, 如 weekly backup, video encoding... etc
5. 桌機, 不外呼上上網, 玩玩 game 之類的需求

最麻煩的部份就是 (1) 跟 (3), 跟本是互斥的 option ... [:'(], 兩者跟本沒機會湊在同一套 os 裡... 最後我決定用很兩光的作法, 把 (1) 移到 virtual pc 的 guest os, 其它 (2) (3) (4) (5) 則留在 host os 上.

Host OS 就用 Vista Ultimate, 果然年紀大了, 之前被 MCE 的上網啟動問題搞半天, 這次不想花這種時間了, 剛好有優惠價, 就去買了套正版的來用 [:$], 不過換機真的是大工程, 之前為了把 (1) 的部份移到 vpc 就搞了半天. 到最後, 發現原本提供的服務用了 E6300 + 3GB ram, 換到 vpc 只開 256mb (vpc 不支援 SMP, 因此 cpu 只用到半顆), 問了一堆人都不覺的有變慢, 果然換機是對的... 以前太奢侈了... 現在是 vpc + 512mb 在跑..

Vista 已經到手了, 裡面有附 32 / 64 位元版, 不過正式換裝又是另一個大工程, 這個禮拜就先灌到 vpc 裡玩看看吧 [:D]