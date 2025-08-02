---
layout: post
title: "水電工日誌 4. 配接電話線 & 網路線"
categories:
- "系列文章: 水電工日誌"
tags: ["有的沒的","水電工"]
published: true
comments: true
redirect_from:
  - /2007/09/26/水電工日誌-4-配接電話線-網路線/
  - /columns/post/2007/09/26/e6b0b4e99bbbe5b7a5e697a5e8aa8c-4-e9858de68ea5e99bbbe8a9b1e7b79a-amp3b-e7b6b2e8b7afe7b79a.aspx/
  - /post/2007/09/26/e6b0b4e99bbbe5b7a5e697a5e8aa8c-4-e9858de68ea5e99bbbe8a9b1e7b79a-amp3b-e7b6b2e8b7afe7b79a.aspx/
  - /post/e6b0b4e99bbbe5b7a5e697a5e8aa8c-4-e9858de68ea5e99bbbe8a9b1e7b79a-amp3b-e7b6b2e8b7afe7b79a.aspx/
  - /columns/2007/09/26/e6b0b4e99bbbe5b7a5e697a5e8aa8c-4-e9858de68ea5e99bbbe8a9b1e7b79a-amp3b-e7b6b2e8b7afe7b79a.aspx/
  - /columns/e6b0b4e99bbbe5b7a5e697a5e8aa8c-4-e9858de68ea5e99bbbe8a9b1e7b79a-amp3b-e7b6b2e8b7afe7b79a.aspx/
  - /blogs/chicken/archive/2007/09/26/2708.aspx/
wordpress_postid: 143
---

做到這個步驟, 漸漸脫離水電工的範圍了, 開始變成所有插電的東西都要管的 MIS ... Orz 線查好之後就要開始把設備給裝起來了. 這邊的工作就雜了點, 每個地方都同時進行... 包括網路, SERVER, 電話交換器, 監控錄影機, 還有第四台的強波器...

裝SERVER, 上機櫃, 還有裝 switch 跟配線等等的, 大概沒有人有興趣看, 趁這篇來講一下事先作的功課吧. 即使事前 survey 了兩個月, 到最後還是碰到一堆意外狀況... -_-  之前的工作通通都是 software development, 雖然都碰的到網路 & server, 不過配線跟裝機都不算主要的工作, 因此也是一知半解的. 只壓一兩條線還可以買現成混過去, 這次要弄廿卅條線可不能這樣混...

首先光是線的接法就傷透腦筋, 因為有這些問題混在一起, 得一次解決掉. 網路線的接法就有兩種, T586A / 586B, 其實沒有什麼特別的規定, 兩端用一樣的壓法就是正常的線, 兩端不一樣就是所謂的跳線 (crossover), 看起來似乎沒差, 不過直到我查了 wikipedia 才發現, 原來 586A / B 的配線法是有典故的...

因為要一起處理電話線的關係, 也去查了 RJ11 的 pinout 定義, 無意間看到了[對岸的文件](http://www.tech-faq.com/lang/zh-TW/rj-11.shtml), 原來 RJ11 的 RJ 是指 "註冊傑克" ... 當下反應真是傻眼, 這是什麼鬼? 以後該設定 google 只要找英文及繁中就好... -_-, 去查英文的才知道是 [registered jack](http://en.wikipedia.org/wiki/Registered_jack), 登記有案的接頭規格就會有個編號, 就像 RJ-11, RJ-45,.. etc. 古早電話線只要二蕊就夠, 後來越來越多, 因此線的顏色也有定義, pinout 也有定義, 最中間一對線, 外圍第二對... 就像我找到的[這篇](http://en.wikipedia.org/wiki/RJ11%2C_RJ14%2C_RJ25).. 看起來紅綠黃黑那種線是舊式的, 新的都改成像網路線一樣, 單色跟半白的. 有了對照表也方便多了. 拿這張圖再跟 [586A / 586B](http://en.wikipedia.org/wiki/TIA/EIA-568-B) 的 pinout 對照一下, 原來 586A 中間 4 pin 是跟 RJ11 相容的, 12 跟 78 再多兩對線就是 586A, 然後為了跳線才多了 586B ..

搞了半天, 原來是這樣. 看完才發現唸電信系, 對這些一點幫助都沒有... 哈哈, 跟同學聊過, 電信是不管這個的, 電匠才要管, 還叫我去考執照... 嘖嘖... 因為上一篇有提到, 電話線網路線都會接到 patch panel, 因此我就得做幾條 patch cord, 一頭是 RJ45, 另一頭是 RJ11, 因此決定統一都用 586A ... 這樣問題就單純多了.

![image](/wp-content/be-files/WindowsLiveWriter/4_2D9A/image_3.png)

因為都是事後寫的, 過程中沒拍到照片就來不及了, 照片中只有兩條線是接到 switch 的, 其它都是一頭網路一頭電話... 另一端就是接到電話總機. 這種線沒人在賣, 只能自己做... 如果沒有看完上面那堆文件, 還真搞不懂這種線要怎麼做... 順帶提一下, 電話總機就是這台, 閃藍光的, 產品網址在[這裡](http://www.tomat.com.tw/PABX/CD2000A-T.htm) ([說明](http://www.tomat.com.tw/PABX/CD308A-con-t.htm)), 可以接三外線八內線, 剛剛好夠我用. 這台大概在促銷, 比其它產品便宜很多, 主機加四台還不差的電話 (就普通的電話, 不是專用分機), ntd 2950... 很好裝, 背後有一堆電話插座, 接法就像 IP 分享器一樣, 把外線接在一頭, 內線就像 HUB 一樣插上去, 電源打開, 就搞定了...

![image](/wp-content/be-files/WindowsLiveWriter/4_2D9A/image_9.png)

最後總算順利的把牆上的電話線接頭 (RJ11), 經過 patch panel (RJ45), patch cord (RJ45 + RJ11), 順利的接到電話總機 (RJ11) 了.. 接頭規格換來換去還真麻煩, 沒辦法..., 為了這個再去買一片電話用的 patch panel 實在太貴了, 一點都不划算... 只好出此下策.

這階段搞定後, 牆上的電話及網路接頭就算都完成了, 最後都能順利的接通到 network switch 及 telephone switch ... 最後補一下怎麼測這種線. 之前講到有買台測線器, 把網路線兩頭都插上測線器按個鈕, 看燈號就知道線有沒有問題. 測線器長這樣:

![image](/wp-content/be-files/WindowsLiveWriter/4_2D9A/image_6.png)

我買的是很陽春的款式, 只能測 RJ45 跟 RJ11.. 看右邊的鑰匙鍊, 大概就想像的出整台的大小了, 很小一台, 7x 元而以, Y拍買的, 幫[賣家](http://tw.page.bid.yahoo.com/tw/auction/1163911957?u=:partsworld66)打個廣告好了. 吃的是 9V 方型的電池, 電池都要跟測線器一樣貴了, 嘖嘖... 測線器本身是可以分兩塊的, 方便你拆開各接在線的兩端. 我的作法是多做兩條線 (下圖紅色的部份), 像這樣接起來, 按下開關就可以測:

```
測線器 o----------------o 牆上的接頭 |------------//------------| PatchPanel o----------------o 測線器
```

運氣不錯, 所有的線都沒給我出問題, 通過測試... 下回講的是一樣的東西, 不過對象換成 cable tv ...
