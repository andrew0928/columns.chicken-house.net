---
layout: post
title: "水電工日誌 7. 事隔 12 年的家用網路架構大翻新"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "有的沒有的", "敗家"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2019-12-12-home-networking/network.jpg
---

![](/wp-content/images/2019-12-12-home-networking/network.jpg)

好久不見的 [水電工日誌](/categories/#%E7%B3%BB%E5%88%97%E6%96%87%E7%AB%A0:%20%E6%B0%B4%E9%9B%BB%E5%B7%A5%E6%97%A5%E8%AA%8C) 又出現了 !

自從 12 年前，家裡重新整修了一番，花了不少時間把家裡的區域網路弄起來後，就再也沒花功夫去搞他了，只能說在家裡先佈好足夠的網路線，還有一個可靠的機櫃真是好用啊 (果然是阿宅的夢想)。不過四個多月前，一次台電計畫性的停電，就把我家的 router 跟 switch 搞掛了, 雖然 router 兩天後莫名其妙的又活起來, 但是終究壽命已盡, 撐到一個月前雙十一前夕又掛了, 再也救不起來...

事後發現，停電根本不是真正的原因啊 (我有 UPS, 又有事先主動關機...), 根本原因就是裡面的電容都鼓起來了, 單純關機就再也開不起來而已... 雖然掛掉的 router 被蘇老妙手回春救回來, 不過我替他安排好退休生活了, 趁著雙十一敗家合理 (其實根本沒優惠啊啊啊) 的氛圍下，我把家裡的網路設備都換了一輪了... Orz

<!--more-->

這次替換，主要有兩大目的，其一是我要換掉困擾我很久的 WiFi 網路連線問題；另一個就是網路的基礎設備 router / switch 的規劃問題。前面那系列 [水電工日誌](/categories/#%E7%B3%BB%E5%88%97%E6%96%87%E7%AB%A0:%20%E6%B0%B4%E9%9B%BB%E5%B7%A5%E6%97%A5%E8%AA%8C) ，已經是 12 年前。當年的重點在從無到有，都在弄佈線等等施工的問題，網路的架構 (其實當時也不懂) 只要設備正常能動能上網就好了。當時甚至沒用啥路由器，還是自己架 server, 插上兩張網卡自己弄軟體的 NAT server ...

這次趁著 "天災" ，折損了一些設備，不得不正面面對這些問題了，剛好就半推半就，把看了很久的設備買進來。辛苦摸索了近一個月，總算搞定了 (所以才會有這篇文章)。許久不見的水電工日誌，就這樣重返江湖了 :D



# 敗家有理 #1, UniFi AP

其他網路設備，大概都只能算是我自己愛玩才弄的，但是 WiFi 不一樣啊，只要訊號不好或是斷線連不上，全家人就會跑來問我為什麼不能連... 先前服役的設備是 7 年前 (2012) 買的 [ASUS RT-N16](https://www.asus.com/tw/Networking/RTN16/), 這台大家都是買來刷機用的, 原廠 firmware 你用到會想丟掉他, 換上第三方韌體就變成神器了。我家的格局一台 WiFi 搞不定，所以後來又添購了第二台 小米 WiFi Mini ...

一台 RT-N16 只有 2.4GHz, 另一台雖然有 2.4GHz / 5GHz, 不過 LAN 只有 100Mbps (加上是對岸的網路設備...), 加上沒有 WiFi Mesh, 走到另一個區域就要自己切換 SSID, 否則可能還黏在訊號很弱的那台, 不會自動切換到訊號強的那台...。

其實我早就物色好要換哪台了啊! 只是一直缺臨門一腳敗下去... 直到這次老天爺給我製造了這個機會 (咦?)   笑想很久的小藍圈: [UniFi-AP AC Lite](https://www.ui.com/unifi/unifi-ap-ac-lite/) 兩台就一次給他買下去了.. 

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-21-53-00.jpg)

這牌子的 AP, 用過的就知道了, 網路論壇上完全不缺勸敗文跟開箱文，加上前陣子一篇 [廚師弟弟買了這套設備的 PO 文](https://www.mobile01.com/topicdetail.php?f=110&t=5836357)，這套設備突然就爆紅了起來 XDD，這麼多開箱文，我就不自己寫了, 反正用過就知道好用, 我這次只買兩台算客氣了。這其實是企業用的 AP, 從一開始設計就是為了讓你大規模部署用的。你可以在同一個空間，買好幾台設置在同個空間，只需要一個 SSID 連線就能漫遊所有的 AP 。多台 AP 背後只需要靠 unifi controller 統一控制, 簡單用滑鼠設定一下就會自動部署到每一台 AP ...。加上吸頂的造型設計, 支援 PoE (Power over Ethernet, 透過網路線供電), 連線又穩定, 訊號也棒, 用過就回不去了。鄉民都說這牌子的設備會自體繁殖，只要你買了一台，過一陣子就會越買越多...

![](/wp-content/images/2019-12-12-home-networking/unifi-ap-aclite.jpg)

至於他的控制軟體 UniFi Controller 也是個好物, 他不只是遠端設定你的 AP, 而是替你管理你整套的 networking (只要你願意整套都買它們家的...  Wireless AP, Internet Gateway, Switch ... etc), 所以會越買越多不是沒原因的, 不過我... 財力有限, 就忍住了, UniFi 沒有買到全家餐, 就兩台 AP (AC Lite) 而已... 

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-22-19-41.png)

這 UniFi Controller 軟體需要另外安裝 (不然你就要花錢買硬體: UniFi Cloud Key) 對有些人來說是個缺點, 因為你要另外找電腦安裝才能用... 還好他有 docker 的版本, 我直接裝在 NAS 上就沒事了 (這軟體要安裝 Java, 實在不想在 PC 上面裝這個...)

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-22-35-45.png)

參考文章: [UniFi 系統免買 Cloud Key！用 Docker 在 NAS 上建立 UniFi Controller 現省三千～](https://ningselect.com/24319/28/)


# 敗家有理 #2, Router + Switch

前面提到的退役設備: ASUS RT-N16, 其實這七年間扮演過不少角色, 一開始是扮演 AP 沒錯, 但是他的訊號實在不怎麼樣, 反而刷機之後 router 本身的穩定性跟效能都是一時之選, 當時大家都是為了刷機才買這台的...。刷機後 router 相關的功能還不錯, 速度快又穩定，因此有一陣子他的天線都被我拔掉，關進機櫃專心負責 router 的角色了。從此之後, 我就再也不用那種 WiFi + Router 的機種了，兩個角色分開對我比較合適。Router 我可以關進機櫃，穩定可靠就好，WiFi 則可以放到天花板，給他最好的位置服務全家。

前面已經選定了 WiFi 的設備機種，至於 Router 的部分，這次我則是挑了這台: [Ubiquiti EdgeRouter-X SFP](https://www.ui.com/edgemax/edgerouter-x-sfp/)...

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-23-10-49.jpg)



其實，就功能而言，先前陣亡的 RouterOS 的機種，其實口碑比 EdgeRouter 系列的好的多，網路上找的到的參考資源也比較多。不過會換掉的原因很簡單，除了原設備掛了之外，另一個是我要找台支援 PoE, 可以接 UniFi AP, 一條網路線就搞定，可以省掉一個變壓器；另一個是溫度低, 先前的 [MikroTik RB450G](https://mikrotik.com/product/RB450G) 運作中會燙到拿不起來... (運作溫度大概都飆到 90℃，電容大概就是這樣爆掉的)。決定換陣營的最後一根稻草, 就是他的 WebUI 比較合我胃口 (雖然功能很陽春, 進階一點的功能都得自己下 CLI)。美中不足的是，雖然是同一家公司 Ubiquiti 的產品, 但是他跟 UniFi AP 是不同產品線...，因此 EdgeRouter 無法納入 UniFi controller 的管轄範圍內，就得分開在兩個不同介面下進行管理了。

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-23-13-28.png)

好啦，其實沒有什麼非換不可的理由 (上面的理由都很牽強)，就是想換新設備而已... 這次掛掉 router + 24 ports switch, 當然也要買一組新的回來... router 前面介紹過, switch 我則是挑了 [Netgear GS116Ev2](http://www.netguardstore.com/GS116E.asp) 這台支援簡易網管 (主要就是 VLAN, QoS, LAGP 而已) 的 16 ports GBE switch...


原本壞掉的是 [Belkin 24ports GBE switch](http://cache-www.belkin.com/support/dl/p75179_f5d5141-16-24_man.pdf), 我估計也是電容爆掉了 (我就沒去修了)，幾年前買的都是無網管的機種，沒辦法在一台 switch 的前提下區隔不同網段，例如碰到 MOD 就無解了，要區隔 NAS 有獨立的網段也無解... 趁這次壞掉要換新的，我就直接挑選有網管的機種了，最主要的目的就是要切 VLAN 啊! 

其實要是設備沒燒掉的話，我應該會再多撐兩年再更換的，到時再直接升級到 10GBE 網路... 雖然當年家裡重新拉水電管線時，我預埋了一堆資訊插座，埋到竟然要買到 24 ports 才夠用，不過牆上雖然有那麼多孔，不過固定會用到的 ports 其實沒那麼多 (現在都無線化了，雖然我不是那麼喜歡無線) ... 因此我就挑了台尺寸迷你的 16 ports 機種，為了節省空間，我也不買機架型的了，買桌上型的放在機櫃...


![](/wp-content/images/2019-12-12-home-networking/2019-12-12-23-16-01.jpg)
> 測試中的 EdgeRouter-X SFP (上) 與 Netgear GS116E (下)

# 敗家有理 #3, (亂入) Intel i350-T4

這個真的是亂入的 XDD, 這是前陣子換 PC, 各方考量挑了最適合的主機板: [ASUS TUF GAMING X570-PLUS (WI-FI)](https://www.asus.com/tw/Motherboards/TUF-GAMING-X570-PLUS-WI-FI/overview/) ... 這張主機板什麼都好，就是敗在他的內建網路晶片不是我慣用的 Intel NIC... (雖然 Intel onboard 的網路晶片也沒強到哪裡去)。不過 Intel 的網路晶片好處之一就是各種 OS 都內建啊! 有些虛擬化或是 server 端的軟體支持度就是比較好一點, 身為架構師應該換張網路卡也是很合理的... 於是網拍看到一張狀況不錯的 [Intel i350-T4](https://ark.intel.com/content/www/tw/zh/ark/products/84805/intel-ethernet-server-adapter-i350-t4v2.html), 有四個 ports, 就豪不考慮的敗下去...

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-23-35-10.jpg)
> (2019/09 購入的 Intel i350-T4 server 用 4 ports GBE 網卡)


# 網路規劃 - 切割 VLAN

曬完設備, 開始來聊點頭痛的... 前面的東西都是想完之後捏一下就敗下去了，但是東西買回家之後才是惡夢的開始啊! 想到當年我買 MikroTik RB450G 回來時也是搞了整整一個禮拜才能上線... 這次也差不多，不過這次工程浩大一點，如果加上把 UniFi AP 弄到好安裝在天花板上，前前後後我也花了近一個月才通通搞定... Orz

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-23-27-12.jpg)
> (2015/03 購入的 MikroTik RB450G)

新網路新希望，我期望新的網路環境能夠搞定這幾件事:

1. 我希望: NAS 等 server(s) 能有專屬網段，能有防火牆隔離
1. 我希望: WiFi AP 能直接用網路線供電 (PoE)
1. 我希望: 關鍵的線路能直接接在 router 上
1. 我希望: 我的工作用 PC 能接到 switch 就能直接 PPPoE 撥接上網測試 (不用另外跳接到 VDSL Modem)
1. 我希望: 我的 NAS 可以 LAGP 合併兩個 ports 來增加頻寬

上面的需求 (1), (2), (3) 其實不難, 挑一台合適規格的 router 就可以直接搞定 (我就是這樣才挑 EdgeRouter-X SFP)。切網段跟防火牆，只要是 router 就能搞定了。但是 PoE 在 router 上而不是在 switch 上，代表我需要讓橫跨兩台不同設備的 ports 能組成同一個 VLAN ... 這對我這種外行人來說是個挑戰啊...，這要搞定才能解決 (3), (4), (5) 的需求...

我期望建立的 VLAN 至少要有三組，而且都必須橫跨到不同設備的 ports... 因此 router 本身也必須包含支援網管的 switch 功能, 這也是我挑選 EdgeRouter-X SFP 的另一個原因。高階一點的 EdgeRouter 都不支援 switch (只能用 bridge, 靠軟體實作出來的), 反倒是 X / X SFP 這兩款，直接用 MediaTek 的 SoC, CPU 直接包含 5 ports switch 的硬體支援，解決了我的難題。

對網管不熟的我, 就是這次才真的搞懂 VLAN 怎麼弄...。我期望的網路架構 (邏輯) 應該長這樣:

![](/wp-content/images/2019-12-12-home-networking/2019-12-13-01-38-06.png)



然而，實際的配線, 因為 router / switch 的 ports 都有限, 因此我希望能這樣架設:

![](/wp-content/images/2019-12-12-home-networking/2019-12-13-02-06-43.png)



若實際列出 ports 的用途, 應該要像這樣:

|顏色|用途|EdgeRouter-X SFP|NETGEAR GS116E|
|----|----|----------------|--------------|
|紅|VDSL|port #2|port #16|
|綠|Server LAN|--|port #2 ~ #6|
|藍|Home LAN|port #3 ~ #5|port #7 ~ #15|
|紅綠藍|*Link|port #1|port #1|

得力於 router 上的 hardware switch 支援, 我終於可以靈活的調度所有可用的 ports 了。同樣的需求，如果沒有 VLAN，而是用一堆傳統非網管的 switch 組合起來的話，我至少需要三台 switch, 同時我得浪費三條線，共六個 ports 來處理這些設備之間的連線。換成 VLAN 我就有機會精簡成一條線，占用兩端的兩個 ports 就能搞定，這就是我這次重新規劃我的網路設備考量的重點。VLAN 我用顏色區分，我希望 switch 上面的 16 個 ports, 以及 router 上面的 5 個 ports, 我都能靈活分配。我希望 ports 都能夠有效利用。UniFi AP 因為需要 PoE 的關係, 也要直連到 router 的 port, 其他設備都按照架構圖, 直接連到 switch 上。

細節我就不多說，總之最後是成功的達成目的了 :D。這不是程式碼，而且我也不夠熟練，我就不獻醜貼我自己的設定了，有興趣的朋友可以直接透過 [facebook](https://www.facebook.com/andrew.blog.0928/) 跟我討論 XDD，最後補張最後完工的上機櫃照片

![](/wp-content/images/2019-12-12-home-networking/2019-12-12-23-23-47.jpg)

如果你跟我一樣想入門 VLAN 的設定 (學會了才有理由敗家換設備)，底下這幾篇是我覺得講的簡單清楚的文章，適合入門觀念，也有提到設定方式:

* [新手都能看明白的VLAN原理解釋](https://kknews.cc/zh-tw/news/5bjqg96.html)
* [VLAN Basics](https://www.thomas-krenn.com/en/wiki/VLAN_Basics)
* [IEEE 802.1Q VLAN Tutorial](http://www.microhowto.info/tutorials/802.1q.html)
* [ER-X系列Per-Port vlan配置说明](https://wiki.edcwifi.com/index.php?title=ER-X%E7%B3%BB%E5%88%97Per-Port_vlan%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E)



網路架構完工後，我的 PC 也換上 Intel i350-T4 網卡, 有 4 ports 可以用 (根本用不完啊), 常常需要測些有的沒有的，我終於能夠按照我需要隨時 PPPoE 直接取得對外 IP 了。因此我直接很奢侈的接了兩條網路線，一條 Home LAN, 一條 Modem LAN, 測試 PPPoE 撥接上網完全沒問題，我只要動動滑鼠就夠了! 其實仔細想想，Server 用的網路卡應該也有能力在單一 port 上指定 VLAN ID, 搞不好我還有機會進一步把這兩條線再合併成一條 (就像那條 router 接到 switch 的多色線一樣的道理)，不過搞到這邊已經快超過我腦袋的負荷了，決定到此為止。


# 實測效能

我這邊就不花功夫去測試頻寬了，直接單純的從 NAS 拉大檔案來測看看就好。測試的大檔 (別想歪，不是迷片) 就拿我 .NET Conf 2019 兩場演講的錄影檔來測試，攝影機加上電腦螢幕錄製，前後總共 2hr 的影片總共 XX GB, 中間經過 router 轉發 (沒有經過 NAT)，可以跑出接近極限的 986 Mbps...

![](/wp-content/images/2019-12-12-home-networking/2019-12-13-22-21-31.png)

如果有經過 NAT 呢? 我直接拿 HiNET 官方的測速軟體，測試 PC 透過 switch / router / modem 上網的速度, 可以跑出 91.03 / 39.84 Mbps 的速度 (我租用的是 100 / 40 Mbps ..):

![](/wp-content/images/2019-12-12-home-networking/2019-12-13-22-24-23.png)

看來我的環境測不出極限... 通通都卡在 ISP 或是網路環境的上限... 上網找找別人的測試結果好了:

* [Ubiquiti EdgeRouter X SFP評測：迷你高階Router](https://www.sakamoto.blog/ubiquiti-edgerouter-x-sfp-router/#outline__5)

如果打開 hardware offloading, 則不論 LAN to LAN 或是 LAN to WAN 都可以跑到幾乎 1Gbps 的滿速... ( 若要 QoS 則必須關閉 hardware offloading ), 看來我短時間內完全不用擔心效能問題了, 這台雖然稱不上高階機種，但是功能及效能都遠遠超出我實際的需求...，可以滿足了。


# 後記

折騰了一整個月，總算一步一步把我家裡的網路架構都翻新一遍了。其實我對網管是個大外行，出社會後就一直從事軟體開發的工作... 會想自己在家架設網路，純粹是阿宅的天性使然，單純想享受在家裡自己蓋起我理想中的網路環境 (就是自嗨) 的成就感而已。另一個很重要的原因，就是我往往都可以在網路設備上，找到解決問題的靈感。

靈感? 應該這麼說，網路設備算是硬體，但是要解決的都是很複雜的網路環境需求，尤其是路由器或是防火牆這類的設備。我常在想，為什麼面對複雜的問題 (每間公司的網路環境其實落差都很大)，網路設備都能有這麼高的適應能力，光靠設定就能解決問題? 反觀我們自己在開發軟體，往往面臨複雜的需求，只能不斷的更改系統的設計，而不能像網管系統一樣只靠設定解決...。

回頭看網路設備，雖然設定都不容易，但是網管總是有辦法搞的定。我想其中一部分的道理，就是這些問題，都被歸納出很一致的規則，例如 VLAN 就是 package 搭配 vlan id tag 的應用, 同時定義每個 port 對進出的 package 該如何解讀上面的 vlan id tag 而已；至於 router 就是各種 routing table / firewall policy 的組合...，只要按照 priority 逐條檢驗 rules, 符合就套用, 不符合就繼續往下, 直到結束為止...。

因為這些複雜的問題已經被梳理成背後一些網通產業的 "領域知識"，因此設備廠商只要時做這些 "領域知識" 的管理介面，訓練有素的網管就能把整個環境蓋起來。我在面對一些其他應用程式的複雜問題時，往往能從這些做法中找到一些靈感，例如利用 rules + priority 的組合, 就能取代大量的開關設定，這是研究網管怎麼解決問題背後的收穫啊! 

資訊的世界，很多東西觀念都是相通的。其實不指這裡講到的網管，甚至是作業系統等等都是，很多資訊工程的基礎知識，都可以在這些成熟的系統內看到蹤跡。多看多想，你會發現其實這些基礎知識真的很實用，多看多想你也會得到更多靈感與啟發；像我就從網管的設定方式，學到很多 rule engine 的設計技巧，下次有機會來寫一篇介紹 rules engine 的應用吧!