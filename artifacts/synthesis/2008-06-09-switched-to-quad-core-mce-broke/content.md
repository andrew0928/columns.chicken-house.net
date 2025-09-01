這年頭，標題不下的聳動一點就沒人看了... 不過我生性保守，這標題可是一點也不誇張... 補一下前陣子狠下心買了顆 Q9300 來給 SERVER 用，發生的小障礙及處理過程。新的 CPU 裝在 SERVER 上， SERVER 關在機櫃裡看不到摸不到，當然是先裝到桌機享受一下，桌機用的是 Vista，平常會用用 MCE 看電視，還有錄電視下來慢慢看...

把桌機的 E6300 換掉，換 Q9300 上去，不錯，什麼東西都很正常，速度也快，溫度也低...。正當一切都很美好的時後，想說開個 MCE 來看電視，嘖... 掛了? 出現這個美化過的 General Protection Failure 畫面:

![MCE 錯誤畫面](/images/2008-06-09-switched-to-quad-core-mce-broke/clip_image002_3.jpg)

點了建議選項，無解。點了 DETAIL 下去看，也看不出個所以然...

![詳細錯誤資訊](/images/2008-06-09-switched-to-quad-core-mce-broke/clip_image002%5B6%5D_thumb.jpg)

Microsoft 這次算是有良心，沒有再寫 "請聯絡您的系統管理員" ... 別再叫 USER 找系統管理員了，最好這種五四三的問題跟外星人的數字，系統管理員都看的懂...

看了這些資料，也看不出問題在那，換了 Media Player 來播放之前 MCE 錄下來的 *.dvr-ms 也是出現一樣的錯誤，連 Media Player Classic 通通都一樣，害我懷疑起是不是 Microsoft 的 codec 寫的不好，在四核心CPU上會有什麼怪問題發生?

不過越看越不對，隨便查了一下 GOOGLE，有一堆人用 Q9300 用 MCE 用的好好的啊... 回頭再來看看詳細的資訊，看到比較特別的，錯誤模組: Indiv01.key ? 這不像是 DLL 還是啥的，怎麼會錯在這? 就順手 GOOGLE 了一下...

沒啥用，只知道這是 Microsoft 的 DRM 用的秘鑰，再去查 Microsoft 的 support center，這次像樣多了，找到這篇:

[KB891664: 如果您的電腦硬體經過變更，Windows Media Digital Rights Management 系統可能會無法運作](http://support.microsoft.com/kb/891664)

真是它ㄨㄨㄨㄨㄨ的，找到問題了... 原來各種加秘的演算法都需要一個 KEY，來識別使用者，或是某一份發佈的媒體檔案。為了讓每一台 PC 有不同的 KEY，因此 Microsoft 會有自己的演算法來替每台 PC 產生一組 KEY，就是 Indiv01.key 這檔案的內容。產生 KEY 的過程中，硬體組態 (包含可用的 CPU 數量) 是來源的一部份，因此換了顆 CPU (核心個數有變化)，就會被 Microsoft 視為是換了台電腦了...。

就是這鳥問題，MCE 認為我換了台新電腦，又用舊的 KEY，判定是 "違法" 的複製 Media，就給我擋了下來... 照著這篇文章的步驟，可以清除 DRM 的授權，一切重頭來過，果然就正常了! BINGO。

有點鳥的問題，嘖嘖... 真正解決花了我十分鐘的時間 (包含 REBOOT)，不過在這之前卻懹我懊惱了好幾個小時...，這裡借題發洩一下 [:@]... 也給剛好也用 MCE 想換四核心 CPU 的人參考一下...

這個故事告訴我們，沒事別亂換硬體，要換硬體請準備好耐心及奮戰到底的決心，不然就準備好重灌的準備... Orz