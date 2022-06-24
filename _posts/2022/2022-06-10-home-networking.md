---
layout: post
title: "水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "有的沒有的", "敗家", "UniFi"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2022-06-10-home-networking/2022-06-12-03-36-32.png
---

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-12-03-36-32.png)


自從 2019/10 因為原本網路設備掛掉, 開始敗入 UniFi 的體系, 果然如同傳聞的一般, 不知不覺就整套換下去, UniFi 的設備就這樣一直繁殖下去了。事隔兩年半, 我家網路主要設備總算都更新完畢, 於是重新補上這篇, 把我對家裡網路的想法交代一下。

這篇我想寫的，不是只介紹硬體的更新而已。硬體更新沒啥特別要交代的啊，這種東西裝好了大概就無感了 (會有感都是網路出問題)。我想說明的是我怎麼藉由 UniFi 的 SDN 把我想要的網路環境搭建起來。從 2007 我開始在家裡擺機櫃開始，機櫃裡的設備其實都在處理這些事情:

1. 網路設施 (routing, switch)
1. 網路服務 (dns, web server, storage, backup)
1. 監控設備 (dvr)
1. 電話總機 

回顧一下[當年的設備](/2007/10/05/水電工日誌-6-機櫃設備展示/), 果然看得出時代的眼淚, 在過去幾年都被我逐步的換掉了。這一連串設備的整併更新，其實我早就想做了，只是一直都沒有看到滿意的 solution 就沒有很積極的替換，直到我開始購入 UniFi WiFi AP 開始 ...

<!--more-->


# 前言: 理想的網路環境

寫到前面，提到當年的設備... 我自己回顧了一下當年的[文章](/2007/10/05/水電工日誌-6-機櫃設備展示/) ，這 15 年來變化還真大啊... 有些當年的規劃, 現在已經完全派不上用場了。現在回頭看，投資錯誤的地方有:

1. 同軸電纜的布線完全出局了，我家已經沒有第四台了，無線的數位電視也沒在用了，家裡的監控攝影機也換成 IP camera ..., 當時在家裡拉了 10 條的同軸電纜，目前處於完全荒廢的狀態 XDD
1. 當年網路線太保守，沒有投資 CAT6A.. (我拉的線路是 CAT5E), 導致我跟 10G 無緣
1. 市內電話幾乎完全陣亡了, 電話總機 & 牆壁上的 RJ12 插座也幾乎荒廢
1. 當年買了 4U 的電腦機殼, 組了台 PC, 跑 windows server 負責家裡的網路 & 我自己工作相關需要架設的各種 lab 環境.. 這也撤掉好幾年了, 完全被 UniFi + NAS + Cloud 取代了

以上的想法，在 15 年後其實都不一樣了，我把我期待的架構描述一下，分成五大目標，後面段落再介紹我的作法:

回到現代，一切都簡單的多了，只要有穩定可靠的網路 (包含有線跟無線) 跟足夠的頻寬，其他都不是大問題了。還好當時的網路線拉的很充足，即使只有 CAT5E, 但是到現在跑 2.5G 完全沒問題。所有升級的路線都往 IP 化, PoE (透過網路線供電, Power Over Ethernet) 化的方向在進行。因此我的理想是: 設備越精簡越好，能用一台就不要用兩台，規格能統一就不要用兩種規格。因此，我就把 AP, DVR, Router, Switch 通通整併成 UniFi 全家餐了, 其他自己架設的服務通通整併到 NAS 裡面。這段的過程就是我的第一個目標: 網路設備整併。

既然所有東西都往網路靠攏了，我就開始期待網路能有些隔離跟規劃了，主要是網段的規劃跟管理。過去我沒有太多網管的經驗 (我的經驗都集中在軟體開發啊啊啊啊，網管知識都是當年 K MCSE 官方教材累積下來的)，設備也大多是陽春的非網管類型，直到跨入 UDM-PRO 來主導整個網路架構的 controller, 我才開始大量使用 VLAN (這是剛好，不是只有靠 UDM-PRO 才辦的到)。想要用 VLAN 隔離，主要是希望:

1. 我希望家人上網的品質是被保障的；
1. 我希望我的 LAB 區是被隔離的 (至少要有基本的 routing & firewall 隔離)；
1. 我希望有些我不信任的設備 (或是客人) 能上網，但是跟我家人用或 LAB 用的環境是隔離的；
1. 最後我希望能善用 HINET 提供的同時最多八組 PPPoE 撥接，有時我自己臨時需要，能直接從筆電或是 PC 撥接上網取得外部 IP，不用經過家裡的 router ..。

以上，這是我的第二個目標: 網路基礎建設。



當年，原本我是有規劃 DVR 的 (還升級過一次)，不過當年的監控攝影機布線相當的麻煩，需要拉一條同軸電纜 (又粗又硬的纜線)，還要外加電源.. DVR 的介面又難用的很，我希望從攝影機開始就走網路 + PoE, 或是 WiFi 加上一般的 USB 供電就好。這是我的第三個目標: 居家監控。

硬體建設的背後，終究還是要靠軟體服務來整合啊，第四個目標就是我希望有良好可靠的網路服務規劃。從 DNS 開始，到各種個人用的網路服務，到我的 LAB 環境，我都投資在 UDM-PRO, NAS, 以及上面可靠的 Docker 環境了。這部份是我的第四個目標: 網路服務。

最後一個，單純是個人的怨念而已。15 年前想說 CAT5E 可以跑到 1GB 已經很夠用了 (當時機櫃裝的 switch 還只是 24 ports 100M unmanaged 的規格而已)，沒預先準備好 CAT6A (就算只有一條也好啊, 拉到我的書桌), 也沒先拉好光纖... 不過隨著 1GB 的頻寬逐漸不夠 NAS 跟 HDD 使用的情況下，我開始肖想 10GB 的環境.. 這是我第五個目標: 邁向 10G 網路

每個阿宅，其實都想在家裡弄這些東西啊 (是這樣沒錯吧)，我運氣好一點，有機櫃跟布線，其他都是相對好辦的東西了，我就從這兩年多，升級到 UniFi 全家餐的過程中，如何逐步搭建我理想中的環境吧。


# 目標 1, 網路設備整併

整個看來，設備整併，其實是最簡單的一環了。中間經歷過很多評估考慮的過程，我就跳過了。上一篇剛採用 UniFi WiFi AP 時, 購入的一批設備 (主要是 router, 兩台 switch) 最終也被我換掉了。目前上線運作中的設備 (這批應該夠我用很久了，沒有更換的打算了，應該夠我用到壞掉為止吧) 如下:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-02-02-01-17-48.png)
> 圖: UniFi Console 提供的 Network Topology


跟基礎建設有關的就都在上面了, 底下這些除了兩台 UAP AC-Lite 之外，都是這兩年間購入的, 在 [上一篇] 都還沒出現:

* [UDM-PRO](https://tw.store.ui.com/collections/unifi-network-unifi-os-consoles/products/udm-pro-1):   UniFi Dream Machine Pro, 擔任 router, network controller, 監控錄影 service, firewall 等服務。
* [USW-ENT](https://tw.store.ui.com/collections/unifi-network-switching/products/unifi-enterprise-switch-24-poe):   UniFi Enterprise 24 PoE Switch, layer 3 switch, 身兼了內網的 routing, 24 ports 都支援 PoE+ 供電, 提供 10G ports x 2
* [USW](https://tw.store.ui.com/collections/unifi-network-switching/products/usw-flex-mini):       UniFi Switch Flex Mini, 家人書桌上的小台 switch, 接兩台 PC 及印表機
* UAP:       UniFi AP AC-Lite x 2, UniFi AP AC-LR (Long Range)

其他網路設備 (Orz, 都是 [上一篇] 介紹的...) 都被我換下線了，包含:

* Netgear ProSafe [GS116E](https://www.netgear.com/business/wired/switches/plus/gs116ev2/) (16 ports GBE managed switch)
* Netgear ProSafe [GS108PE](https://www.netgear.com/business/wired/switches/plus/gs108pe/) (8 ports GBE PoE managed switch)
* Ubiquiti [EdgeRouter-X SFP](https://tw.store.ui.com/collections/operator-isp-infrastructure/products/edgerouter-x-sfp)

其他更古早也被退下的設備:

* 擔任 router 角色好一段時間的刷機神器 ASUS RT-N16, 以及 MikroTek 的 RB450G ...
* 小米 wifi 兩台, 因為不想繼續用對岸的網路設備，也被我換掉了
* 白牌的監控主機 DVR, 四路
* 市內電話主機, 3 外線, 8 內線
* 第四台 cable 訊號強波器
* 白牌 (其實有牌子，懶得記型號而已) 24 ports GBE switch

其他有些軟硬體，也被網路基礎設替代了，包含:

* [UniFi Network Controller](https://www.ui.com/) (本來是安裝在 NAS 的 docker 上, 現在內建在 UDM-PRO 裡面)
* DVR + Camera, 被 UDM-PRO 內建的 [UniFi Protect](https://www.techbang.com/posts/84279-unifi-protect-video-surveillance-solution) 取代, 攝影機也因為老舊故障, 直接換成 UniFi Protect 系列的 [G3-Flex](https://tw.store.ui.com/collections/unifi-protect/products/unifi-video-g3-flex-camera-1) 跟 [G3-Instant](https://tw.store.ui.com/collections/unifi-protect/products/unifi-protect-g3-instant-camera-2)
* 兩台 Synology NAS ( 8 Bay + 4 Bay ), 取代了當年那台 4U PC server, 被取代的除了硬體之外，也包含上面跑的各種服務

最後，為了跟 10G 沾上一點邊，也敗了這些東西:

* Mellanox ConnectX-3 10G NIC (SFP+), 裝在 Synology DS1821+ 上面。網拍有很多 server 退下來的, 便宜好用
* Intel i225-v 2.5G NIC, 裝在我的桌機上。桌機就不要求了, 平日日常使用連線穩定速度足夠就可以了
* USB3 2.5G NIC (Realtek chipset), 筆電用，沒內建 2.5G 網卡，只能 USB 擴充了
* (家裡另一台 PC, 主機板內建的 LAN 也是 2.5G 的)

為了串連這些東西，由於佈線的關係，加上現實的考量，我決定 NAS 主幹先升級到 10G 就好 (都在機櫃內沒有佈線的問題)，我用 SPF+ 的規格，避開 RJ45 過熱的問題；由於設備都在機櫃內，光纖也省了，我直接買 UniFi 原廠的 DAC 銅線 (2m) 就好了，既便宜又可靠，溫度又低。而 PC 端則先升級到 2.5G 就夠了。一來 NAS 我沒有用太複雜的 RAID, 單顆硬碟其實 2.5G 的速度就足夠了。也因為這樣 (加上後面會交代的 L3 switch 的連線速度問題) 我才決定一次到位，購入了 UniFi Switch - Enterprise 24PoE, 提供了 24(RJ45) + 2(SPF+) ports, 提供了 12 個 2.5G ports, 2 個 10G ports, 以及 Layer 3 Switch 的管理能力。原本想買同等級同規格，只是 port 少一些的 Enterprise 8PoE (2.5G x 8 + 10G SPF+ x 2), 不過我算了算, 8 ports 剛剛好不夠用啊, 加上之前 firmware 還沒準備好, 還沒正式支援 L3 switch, 又碰到特價, 我就直接一次到位, 買了 24 ports ..

最後來到線材的部分，全部都集中到 CAT5E 的線路上了。這幾年來，我家幾乎沒有在用的市內電話，[當年](/2007/09/14/水電工日誌-2-資訊插座-面板/) 的我實在太睿智了，即使是電話線，我都統一用一樣的線材 (CAT5E) 來佈線，我個人喜好也剛好符合結構化布線的要求，線的兩端都是固定的資訊插座。這次只有簡單地把牆上的插座換成 RJ45，而機櫃這端則是用 24 ports 的 patch panel, 線材的兩端都是 RJ45... 電話用的插座規格是 RJ11 ，其實跟網路的規格 RJ45 是相容的啊 (這點我是後來才知道的)，電話線的水晶頭完全可以插在 RJ45 上面，只要另一頭是電話線，不是網路 switch 就好... 我當年根本可以不用另外做不同的插座的。現在一切都統一了，我需要時再跳線就好，隨時可以把牆上的插座按照我的需要，改成網路或是市內電話使用。

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-12-03-50-25.png)
> 圖: UniFi 乙太網路跳線, 我把自己壓的短跳線全換掉了。可彎護套實在太讚, 可以彎成你想要的角度 (SKU: U-Cable-Patch-RJ45)

最後硬體的整併就變成上述的這樣了。當年那麼多設備，現在只要 5U 的空間就通通搞定了。這三年陸陸續續清出了不少老舊設備，現在機櫃也清爽多了，換上 UniFi 原廠的跳線 (其實價格很合理不貴啊，內藏鐵絲的接頭護套很好用，大推)，10cm / 30cm 的 CAT6A 短跳線, 藍色連接主幹設備, 白色連接 Client 設備，以及 UniFi 的 DAC (SPF+), 50cm 拿來串接 UDM-PRO 跟 USW-ENT24POE, 2m 拿來串接 NAS 跟 Switch, 線材換上去整個質感就起來了 XDD, 貼一下目前機櫃的照片當作這段的結尾。跟 15 年前比，是不是單純多了? 現在只剩 NAS x 2, UPS, Router, Switch 就沒有了。當年規模小一些，但是設備複雜多了，有 4U PC-Server, Switch, DVR, 電話總機...


 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-15-20-03.png)  
> 圖: 懷舊照片, 2007/10 的機櫃設備

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-24-46.png)
> 圖: 懷舊照片, 2019/12 的機櫃設備

2019/12 的那批升級，已經換上 VLAN, UniFi AP 了, 不過當時還未購入 UDM-PRO, 零散的設備一堆, 同時電話總機跟 DVR 也都還在服役中的混亂期, 也開始體會到 UniFi 的整合優勢。當時我的 Synology DS412+ 還健在...

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-13-59-39.png)  
> 圖: 現況照片, 2022/06 的機櫃設備, 設備都整併成 UniFi 了, 軟體都塞 NAS 了, 線路都整併成網路線了。

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-12-16-08-48.png)
> 圖: 主要設備的管理就都靠 UniFi OS Console 了。管理畫面可以看到所有被託管的 UniFi Devices (正式突破 2 位數)


# 目標 2, 網路基礎建設

這段落的主角，其實都是 UDM-PRO 啊，因為這些東西大概都是靠 [UniFi OS Console](https://store.ui.com/collections/unifi-network-unifi-os-consoles) 建立起來的。不過說在前頭，以硬體、或是 CP 值來說，UniFi 最被推崇的都是 WiFi AP 系列的產品。其他像是 UniFi OS Console, 或是 Switch 等等, 單純就功能與規格來說, 就沒有那麼突出了，例如 Router / Switch 等等。尤其是你越需要進階管理，或是講求效能的，都有其他更好的選擇，UniFi 不會是首選。不過我會在這邊談 UniFi Network，一定有它特別的地方，就是高度的整合，以及還不錯的 CP 值。

也是因為 UniFi Network 高度整合相關設備 ( router, switch, wifi ap ) 及這些複雜的網路管理機制，我這種半調子的網管才有能力建構這些環境起來啊，換成他牌的 (例如前一手我用的 MikroTek) 雖然可以做得更出色，但是我學不來啊 XDDD，對我來說太困難了。 可以在單一設備搞定這些服務，這才是 UniFi 全家桶的魅力。

我在家裡的網路，建構了這些我期待的自用服務, 包含:

1. 5 個不同用途的 VLAN 與其之間的 routing (UDM-PRO, USW-ENT24)
1. VPN (L2TP, Teleport VPN)
1. 基本的對外攻擊防禦 (Threat Management)
1. 基本的網路監控與流量分析
1. IPerf3 server
1. Internal DNS rewrite (這不是 UDM-PRO 提供的, 我是在 NAS 上面另外安裝的)


## VLAN

其實 VLAN 的建置跟[兩年前那篇](/2019/12/12/home-networking/)沒有太大的改變，我直接列我切了幾個 VLAN 以及用途就好。這麼做的目的可以看上一篇:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-14-02-42.png)
> 圖: VLAN 架構示意圖

1. **TRUNK(0, 10.0.0.0/24)**:  
預設, 主要用來網路骨幹設備 ( Router, Switch, AP, Camera, DNS ) 串聯用
1. MODEM(10, --):  
直連光世代的數據機, 當我有任何設備要直接 PPPoE 撥接，或是電視要直接看 MOD 時使用 (不過我沒有申請 MOD)
1. **NAS (100, 192.168.100.0/24)**:  
主要是供兩台 NAS, 以及在 NAS 上面跑的各種 docker containers, 包含我的 LAB 環境都在這邊。做基本的隔離跟防火牆，跟家人用的上網往段隔離，方便我做實驗，也方便監控流量。
1. **HOME (200, 192.168.200.0/24)**:  
主要家人各種設備上網用。WiFi SSID 也都是配置到這個網段
1. **GUEST/IOT (201, 192.168.201.0/24)**:  
直接用 UDM-PRO 內建的 Guest Network 功能搭起來的。這網段能直接上網，但是無法連到內部其他的網段。適合給那些還沒換掉的對岸聯網設備或是家電。

其實這些設定並不難，就是很麻煩而已，你要懂得那些 VLAN 的設定方式 ( tag / untag, 或是 pvid 之類的表示方式 )，以及多個網段之間的 routing 管理。兩年前我是自己在三套設備之間一個一個 ports 慢慢指定 tag / untag vlan id, 好幾次弄到網路不通, 搞半天才弄起來的 (弄好就完全不想改了, 即使我臨時想讓桌機換個 VLAN 也懶)。另外 Guest Network 就麻煩一點，除了 VLAN 跟 routing 之外，你還要知道怎麼處理認證啊... 這之前我在用 RouterOS 的時候就碰到瓶頸了，天分不夠弄起來就是不滿意...。在更換 UDM-PRO 之前這些設置對我而言是個大工程，尤其還橫跨多種設備時，VLAN 我得要自己去整合，光是換個 VLAN ID 我就得去三台設備改三次就夠頭痛的了。Guest Network 也是，沒有 UniFi Network Controller 提供的 Guest Portal 的話，我大概也是弄不起來...。這些高度整合的服務幫了我不少忙，我才會下定決心，用全家餐換掉其他牌子或是系列的 router / switch.

整合的好處是網路拓樸一目了然 (實體連結)，網段或是 switch ports 的流量也是輕鬆就可以掌握。如果你想知道這些流量都是在傳輸哪些類型的資料 (application) 也難不倒 UDM-PRO, 可以看網段，或是設備跟流量之間的統計，當你發現流量異常時，你至少可以知道是哪類通訊協定在傳資料。雖然這些都是要花 CPU 標示統計出來的，不過買了就是要用啊，這些東西要自己架設也做得到，不過要花不少功夫研究就是了。

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-14-06-07.png)  
> 圖: 網路拓樸

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-14-07-09.png)  
> 圖: PORT 流量統計

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-14-08-10.png)  
> 圖: APP 流量統計

至於 VLAN 之間的 routing, 除了 L3 switch 之外, 其他也沒有太多需要留意的。L3 這部分我留待最後聊 10G 的部分再談就好。

## DNS - AdGuard Home

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-14-08-46.png)
> 圖: AdGuard Home


DNS 我想了很久，最後我還是把他歸類到基礎建設這段了 (雖然他應該算是網路服務)。我不需要在家裡弄一套完全獨立的 domain name (例如 andrew.local 這類的)，不過礙於 SSL 憑證的關係，有些自己的 host 在家裡連，不想繞到外面再繞回來，但是沒有 DNS 來指路的話又有點麻煩，最後選擇在 NAS 的 docker 上面架設了 [AdGuard Home](https://adguard.com/zh_tw/adguard-home/overview.html) 這套服務。他是透過 DNS 的機制，幫你擋掉廣告或是惡意網站，同時也提供讓你 rewrite 的白名單。當你沒有特別指定覆寫的清單，或是被 AdGuard Home 列為黑名單被阻擋之外，其他情況他都會把 DNS Query 轉發到上游的 DNS。不需要太多的管理，對我而言剛剛好夠用，就是個理想的選擇。

對 DNS 有掌控能力之後，後面會提到的網路服務就開始有好的出發點了。我可以很輕鬆的用 domain 來搭配 reverse proxy (NAS 內建), 去組織我用 docker 建立起來的一堆服務。這後面再談。

* [是時候裝一套 AdGuard Home 全局擋廣告神器了！](https://www.jkg.tw/p2158/),2019/06 Jkgtw's Blog

## VPN - Teleport VPN / L2TP

最後一個 VPN，也是被我歸類在網路基礎建設，而非網路服務的另一個功能。UDM-PRO 內建了幾種主流的 VPN service, 同時也內建了讓你管理帳號認證的 RADIUS service. 一樣是簡單方便的懶人 solution, UniFi Network Controller 可以幫我搞定大部分的雜事, 包含網段、Routing、開通防火牆等等。最後我設定了 L2TP/IPsec 來架設家裡的 VPN, 有需要的話我可以直接從外面撥接回家。

不過 L2TP 有點年代了，UDM-PRO 又還不支援 SSL-VPN 這類協定... 正好在上周正式 release 了新功能: Teleport VPN, 這個真的要大推一下。

Teleport VPN, 其實早在 UniFi 其他產品線 (AMPLIFI) 就出現過了，對於懶人是個福音，幾乎不需要任何的設定就能啟用了。一般的 VPN server 設定是出了名的囉嗦啊，連我都沒辦法保證一次 OK。這次 UniFi "下放" 的 teleport vpn, 研究了一下來頭還不小。它背後的基礎不是基於常見的 [OpenVPN](https://zh.wikipedia.org/zh-tw/OpenVPN), 而是另一套後起之秀: [WireGuard VPN](https://www.wireguard.com/). 相對 OpenVPN 完整的生態系，WireGuard VPN 的快速與簡易是另一個[不錯的選擇](https://www.purevpn.com.tw/blog/wireguard-vs-openvpn/)。使用的體驗 加上 UniFi 的整合能力都很令人滿意，唯一不足的是目前還沒有 windows 版本的 client, 所以暫時我還拿不掉 L2TP ...

想要自己設定的也很簡單，先在 UniFi Netowkr Controller 內產生連結 (下圖左方)，產生的連結想辦法傳給對方的手機點選，會跳出 APP 問你是否接受，就完成了 (右方)。手機端的 APP 是 [WiFi Man](https://apps.apple.com/us/app/ubiquiti-wifiman/id1385561119), 他會幫你完成所有的設定，你不需要再繞到系統那邊自己建立 VPN Profile。要連線時你只需要打開或關閉 VPN 就好，其他什麼 server ip address, secret, password, 還有啥安全設定的通通不需要, 就是這麼無腦。

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-33-00.png)
> 圖: Teleport VPN 的設定 (WEB) 與啟用 (APP) 畫面


想體驗或是深入了解的，可以看一下這些介紹...

* 官網介紹: (AMPLIFI Teleport](https://tw.amplifi.com/teleport)
* Mobile01: [Ubiquiti Amplifi Teleport 傳送術 穿梭來去自如](https://www.mobile01.com/topicdetail.php?f=110&t=5945594)
* [WireGuard 與 OpenVPN：哪個更高級？](https://www.purevpn.com.tw/blog/wireguard-vs-openvpn/)



## Multiple PPPoE Connection

> Note @ 2022/06/24  
> 這段是文章發布後才追加的, 感謝 1.12.22 版本更新, 終於讓我願望成真了 :D

感謝一下官方的努力, [1.12.22](https://community.ui.com/releases/UniFi-OS-Dream-Machines-1-12-22/851bdc97-fc39-40ef-bd71-786766512c58) 版本更新, 我終於可以用一個 HiNET 光世代的線路, 同時撥兩組 PPPoE 連線, 取得兩組 IP 給 UDM-PRO 使用。其中 WAN1 我給浮動 IP, 作為所有設備預設連上 internet 使用；另一個 WAN2 我則給撥接配發的固定 IP, 保留給 NAS 使用, 包含 NAS Download Station 連外使用, NAS 上的一堆服務對外開放 (用 Port Forwarding) 使用惹。

這配置得力於 UDM-PRO 1.12.22 Firmware, 以及 UniFi Network [7.1.66](https://community.ui.com/releases/UniFi-Network-Application-7-1-66/cf1208d2-3898-418c-b841-699e7b773fd4) 帶來的這幾個新功能:

1. **Port Remapping**:  
UDM-PRO 上面的 Port #8, Port #9, Port #10 (SPF+ 10G), Port #11 (SPF+ 10G) 終於可以自由的對應 LAN / WAN1 / WAN2 了。除了我可以把兩個 SPF+ 對應到 LAN 連接兩台 10G 設備之外，我也可以不用多買額外的配件 (SPF+ 轉 RJ45) 就可以玩玩 Dual WAN 了.. 我家頻寬只有 100M/40M 啊，原本的配置 WAN2 一定要用 SPF+ 真是個折磨人的設計..  

1. **Traffic Routing**:
這後面再仔細介紹, 這版終於支援以前 Policy Routing 的功能了，你可以指定那些人連上哪些網站，要走哪條線路出去... WAN1 / WAN2 終於不再只能是備援了，可以有更多樣化的應用。

好，感謝完畢，開始來聊正題了。前面講到我自己家裡切了幾個 VLAN, 最主要的就是分別管理我設備骨幹 (**TRUNK**), 我的 NAS 網段 (**NAS**), 以及我上網用的設備網段 (**HOME**)。我的期待是這樣:

1. 我希望能同時建立兩個 PPPoE 連線, 取得兩個 IP address, 分別指派給 UDM-PRO 的 WAN1 與 WAN2 使用
1. WAN1 就用浮動 IP 就好, 會隨時間變動沒關係, 反正只是上網用。我不希望連到網站, 下載內容, 或是 PTT 長期都使用一樣的 IP address ... 
1. WAN2 則使用固定 IP (PPPoE 每次都配發固定的 IP, 不是企業專線的那種)。我自己有用 NAS 架設一些服務 (後面的段落: [目標 4, 網路服務](#目標-4-網路服務) 會介紹)，我希望這對外服務能有固定 IP, 搭配我自己的 domain name, 以及 UDM-PRO 的 Port Forward, 還有 Threat Management 等等防護功能，發布我內部架設的個人用服務。
1. 其他我自己臨時的需求, 內部特定設備或是網段, 可以安排 Rules, 選擇要從 WAN1 或是 WAN2 上網
1. 最後其他狀況下, 我希望我自己的 PC 或是 Notebook, 能無視這些設定, 選擇自己直接 PPPoE 撥接取得對外的 IP address 使用與測試


**STEP 1, Setup Dual WAN**

有點變態的需求 (你是有多少對外 IP 要用啊...)，不過單一一台 UDM-PRO 其實都很容易的就滿足了 XDD, 因為是新功能, 我就特別花點篇幅說明一下好了... 首先, 先把 Internet Connection 建起來。這是我的設定畫面:

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-00-28-30.png)
> 圖: Internet 設定畫面, 設定了兩組 Internet Connection 連線


接著來看一下 Port Remapping, 我把能重新定義的四個 ports ( #8, #9, #10, #11 ) 中的兩個 RJ45 1G 留給 WAN, 兩個珍貴的 SPF+ 10G 則留給 LAN 使用:

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-00-30-22.png)
> 圖: 重新指派 WAN2 給 Port 8

接著，這兩個 ports 就直接連到 HINET 的小烏龜了。我正好買了一堆 UniFi 原廠的短跳線 (好用, 大推), 黑色的我就專門拿來標示對外的線路了。我拿兩條黑色的把 Port #8, #9 直接連到小烏龜。我家只有 100M/40M, 小烏龜還是舊款走電話線的, LAN port 的規格只有 100M ... 無奈還沒辦法升級 FTTH, 只能將就著看他閃黃燈 (100M)...

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-00-34-30.png)
> 圖: 實機照片, 小烏龜拉了兩條黑色的網路線, 分別接到 Port #8, #9

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-00-39-30.png)
> 圖: UniFi Network 上面的顯示, 綠色的圖示是 FE, 裡面有個地球的 icon 是指這是 internet 連線。

(其實應該還要有第三條黑色的連到 Port #7, 接到 MODEM 這個 VLAN 的, 讓我的桌機連這個 VLAN 就能夠直接本機 PPPoE, 不過拍的時候剛好拔掉就懶得重拍了)



**STEP 2, Setup Traffic Routes**

接下來就是另一個新功能登場了: **Traffic Routes** !!

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-00-42-25.png)


我只設定一條 rule: 我的 NAS 上網走 WAN2, 其他沒有指定的就通通都走預設的 WAN1, 除非 WAN1 掛掉才會切到備援的 WAN2... 不過這對我沒啥意義啊，我就那麼一台數據機，就只有一條實體的線路，要掛也是一起掛掉 XDD，備援的功能就當作自嗨就好 XDD。設定畫面簡單到不行，我也懶得說明了，貼圖就好:

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-00-46-58.png)
> 圖: 指定來自 NAS 的 Internet Access 流量通通都改走 WAN2

畫面上的 Category, 你可以選擇類型, 看是指定 domain, 或是指定 ip + port, 或是指定全部上網的轉導類型。Source 是指定那些範圍需要轉導, 可以指定個別 Devices, 或是 Group (看起來是照 Network 來區分的), 最後 Interface 就是讓你選擇符合的流量要走哪個 Internet 連線出去... 

實際上真的可行啊, 我做了簡單的測試:

1. 我用我的桌機, 連到 www.myip.com
1. 我用我的 NAS, 用 Synology 內建的 DDNS 自動偵測對外 IP 註冊 DDNS

畫面我就不貼了，都是我的 IP address, 但是都會被我馬賽克遮掉... 既然都看不到我還貼這圖幹嘛呢? XDD, 我只講結論, 這樣設定證實真的會走不同線路出去。而這兩個 IP 則會跟 UDM-PRO 拿到的對外 IP 是一致的。你可以從 dashboard 這邊核對看看:

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-00-56-11.png)
> 圖: dashboard 現在會顯示 UDM-PRO 內外 IP 資訊了 (忘了哪一版才開始有這資訊... 以前很難找)

為了證實真的有效，我又多加了第二個 traffic routes, 我想把我自己的 PC 連到 [MyIP.com](https://www.myip.com/) 的流量改走 WAN2:

> 不知為何, 我測試時用 domain 轉導 [MyIP.com](https://www.myip.com/) 無效, 我就手動改轉導指定 ip address 就成功了.. 以下用 ip address 示範

先 nslookup 一下 [MyIP.com](https://www.myip.com/) 的資訊:

```

D:\> nslookup myip.com
Server:  UnKnown
Address:  10.0.0.20

Non-authoritative answer:
Name:    myip.com
Addresses:  2606:4700:3033::6815:1705
          2606:4700:3031::ac43:d02d
          172.67.208.45
          104.21.23.5

```

我拿 IPv4 就好, 多加這條 traffic rules:

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-01-09-06.png)
> 圖: 指派來自 ANDREW-PC 對外部指定 IP 的流量，通通改走 WAN2

我拿了兩個偵測外部 IP 的網站來實驗，真的有效耶 (算了，我就保留 IP 最後一段不要馬賽克好了) ... 第一個拿我轉導的標的, [MyIP.com](https://www.myip.com/) :

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-01-10-47.png)
> 圖: 我的 PC 連上 MyIP.com 的結果

接這找沒列入清單的對照組，我隨便找了一個, 我用 [WhatIsMyIpAddress.com](https://whatismyipaddress.com/) :

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-01-12-37.png)
> 圖: 我的 PC 連上 WhatIsMyIpAddress.com 的結果

當然這兩個 IP 都是對的，都是 UDM-PRO 的 WAN1 / WAN2 的 IP, 不是網站亂掰的結果。

測試到這邊，最後小結一下，這功能真是太棒了，我買了 UDM-PRO 買了一年半，總算是等到這個功能了。只能說 UniFi Network Application 整合的真好，操作使用起來完全沒有障礙，WAN1 / WAN2 的功能在每個地方都有正確的標示。例如我讓 NAS 走 WAN2 之後，在 Port Forward 的設定，我也能精準的指定我要讓哪個 WAN 的對外 Port 轉導回來內部的 NAS:

![](/wp-content/images/2022-06-10-home-networking/2022-06-25-01-16-54.png)
> 圖: Port Forward 可以指定你要轉發 WAN1 / WAN2 哪個 interface 的 port

這跟當年 (2021/01 左右) 剛買 UDM-PRO 的時候完全不同檔次啊，那時的 WAN2 對我就跟雞肋一樣，食之無味棄之可惜，擺一個漂亮的高規格 SPF+ 在那邊看的到吃不到，當時的 WAN2 除了備援之外根本也沒別的用途，更何況我真要備援的話還沒有那些設備 (家用的寬頻上網用不到 SPF+ 啊, 看看我的小烏龜還只配備 100M 的網路規格...)，我還得額外準備 SPF+ 轉 RJ45 ...

不過這批更新一次到位，實用度完全不一樣了。我除了 NAS 能有專屬 IP 發布服務之外，我自己電腦連特定服務也能走專屬 IP 了。這一切都只要在 UniFi Network 上面簡單的設定幾條規則就可以搞定，大推!



# 目標 3, 居家監控

監控系統，是主要讓我決定敗入 UDM-PRO 的最後一根稻草。雖說整合式的一體機 UDM-PRO 有很多優勢，但是不管再怎麼說，我先前也是很克難的搞定 VPN / VLAN / DNS 了啊... 主要就是先體驗過 UniFi Network Controller 的優勢，加上家裡的古早監控攝影機一台接著一台掛掉了... 於是先購入兩台 G3-Flex, 搭配當時的末代自建 controller: UniFi Video, 使用起來還不錯, 加上官網宣告 UniFi Video 不再繼續維護, 以後會將重心轉移到 UniFi Protect (這個只限定 UniFi Console 內建使用).. 於是就敗了 UDM-PRO, 同時也正式的邁入全家餐的行列。

不得不說，UniFi 的軟體與整合真是大加分，UDM-PRO 內建 UniFi Protect, 你只要自己插一顆硬碟進去就可以錄影了。監控的 Web 介面或是手機 APP 也寫得很好用，完全跟當年那些小廠的 DVR (難用到爆的 UI) 完全是不同檔次的。說到好用，其實 [Synology Surveillance Station](https://www.synology.com/zh-tw/surveillance) 也不錯，不過要額外授權，設定的選項也過頭了，我個人是比較喜歡 UniFi 的體驗，恰到好處不用花太多心思。

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-12-03-43-39.png)
> 圖: 沒啥出場機會的照片: 裝在我家門口的 UniFi G3-Flex (SKU: UVC-G3-FLEX)

如果真要說 UniFi Protect 的缺點，當然也有。一來是攝影機只能用自家的，雖然有不錯的入門機種 (G3 Instant, 有[網友的開箱文](https://masonsfavour.com/ubiquiti-unifi-g3-instant/), 這台買的到的話真的大推) ，也是超高 CP 值，用料好又穩定可靠，一台還不到 1000 塊，不過大缺貨，根本買不到啊啊啊啊。買的到的只有高階機種，一台要上萬...；另外就是硬碟配置完全沒有自主的彈性，錄影的額外備份機制也完全沒有，你只能自己手動下載你要的區間影片，如果你想要大量匯出錄影，那現在並沒有很好的做法。比較推薦的作法是: UniFi Protect 可以統一提供每支攝影機的 rtsp:// 網址, 拿 Synology Surveillance Station 當作自訂攝影機輸入，就用 NAS 同步抄寫一份當作備份了。

原本我只購入兩台 G3 Flex (走 PoE, 有線的機種)，由於實在太好用，某次剛好搶的到，就陸陸續續添購了兩台 G3-Instant, 有可靠的 WiFi 訊號, 又有隨手可得的 USB-C 電源供應，就這樣替換掉原本的 RG58 同軸電纜, 類比式的監控攝影機, 還有難用的 DVR 主機了..。會放心地用 WiFi Cam 還有另一個原因，也是因為家裡的 WiFi 換了 UniFi AP 後 (雖然只有 5G, 還買不到 WiFi6 ...) 訊號夠穩定, 完全不用去擔心 WiFi Cam 會不會不穩定, 或是流量過大影像傳輸失敗等等鳥問題。WiFi 就沒有 PoE 的優勢了，必須另外自己插電，但是因為是很通用的 USB-C 供電 (5V 就夠了, 不用用到 PD)，電源來源也是垂手可得完全不用擔心啊! 如果你擔心電源不穩, 串一個行動電源就是個小型的不斷電系統了。或者你可以買這種內建電池的電源 (我用 [小米 50W 雙模行動電源](https://buy.mi.com/tw/item/3204100008)) 也有一樣效果，家裡很多現成的，不用額外花錢。

用 NAS 當作第二錄影兼備份的做法，剛好這兩天也看到經營弱電工程的 youtube 有 [介紹](https://www.youtube.com/watch?v=yUFFyagPS-I)，我就直接轉貼了。我說為什麼都買不到 G3 instant 啊? 原來都被掃光了 =_=

最後貼一下 Web UI / APP 的介面，跟相關的介紹文章，讓各位體驗一下操作介面；實在太好用，我媽除了看第四台之外，看得最多的影片就是這個 APP 了 XDDD，錄影內容涉及居家隱私我就不貼了，只貼 Web UI 的介面，同時把監控內容馬賽克一下...。想多了解的，我貼別人的介紹..

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-38-24.png)
> 圖: UniFi Protect 的 Web UI 畫面, 右側會列出偵測到動作的時間軸

參考連結:
* 官網 [UniFi Protect, 易於擴充的安全監控系統](https://tw.ui.com/camera-security)
* [UBIQUITI UNIFI G3 INSTANT WI-FI 無線攝影機，UNIFI PROTECT 系統中最超值， 身形如麻雀，用料如殿堂](https://masonsfavour.com/ubiquiti-unifi-g3-instant/), written by Mason, 2021/09/04
* [買買買!都買！教你簡單用NAS整合管理WI-FI攝影機！｜NAS1821+安裝監視系統｜UNIFI G3 instant IP Camera 開箱｜cp值高的監視器](https://www.youtube.com/watch?v=yUFFyagPS-I)



# 目標 4, 網路服務

這段就真的是大雜燴了，有了好的基礎建設，真的要玩什麼都容易了。我在一年半前，因為原本的 NAS (Synology [DS412+](https://global.download.synology.com/download/Document/Hardware/DataSheet/DiskStation/12-year/DS412+/cht/Synology_DS412_Plus_Data_Sheet_cht.pdf)) 無預警掛掉了，看來是主機板陣亡了。快要十年的機器就直接讓他安息吧，備份用的設備也沒有造成什麼資料損失，只是剩下一台 Synology [DS918+](https://global.download.synology.com/download/Document/Hardware/DataSheet/DiskStation/18-year/DS918+/cht/Synology_DS918_Plus_Data_Sheet_cht.pdf) 也有點不安。所以在接下來的時間就物色了一台新機，同時為了跑 docker / virtual machine / 10G 做好準備，就挑了這台 Synology [DS1821+](https://www.synology.com/zh-tw/products/DS1821+), 同時陸陸續續擴充了 32GB RAM, 跟 10G NIC (SPF+)。

S 牌的硬體都給的很小氣，這等級的設備也只是給到 4 ports GBE 網路, 我自己擴充才有 10G SPF+ 擴充能力。這款也開始改用 AMD Ryzen 的嵌入式 CPU (v1500b, [跑分](https://www.cpubenchmark.net/cpu.php?cpu=AMD+Ryzen+Embedded+V1500B&id=4304)), 運算能力不能跟桌機比，但是跟之前的 DS412+ / DS918+ 比起來就好太多了，至少已經可以跑跑輕量級的 virtual machine 了。網路的連線速度雖然給的很不乾脆，但是數量也夠了。10G 我就接在 NAS 的網段 (VLAN: 100) 專門拿來提供檔案傳輸的服務 (SMB), 另外那些雞肋的 GBE Ports, 我就拿來接 TRUNK 網段 (VLAN: 0) 與 HOME (VLAN: 200), 分別給 DNS 與 [HomeKit Assistant](https://www.home-assistant.io/) 使用。

只能說 NAS + Docker 真是好物，我簡單介紹一下我在上面跑了哪些東西:

## 網路基礎服務相關

> #DNS, #SSL #cert, #Reverse Proxy

歸在這類的有 [ADGuardHome](https://adguard.com/zh_tw/adguard-home/overview.html) (DNS), 還有取代 Synology 自己封裝的 Docker 管理工具用的 [Portainer-CE](https://www.portainer.io/). 其他還有一些冷門的我就略過了。DNS 前面提過我就不多說了，這是個必要的東西，也是所有其他網路服務架起來好不好用的基礎。沒有 DNS，你就得用 IP + PORT。你用了 IP 就沒辦法用 SSL，你也得記得每個服務的 Port 號碼。有了 DNS 你就能申請 Let's Encrypt 憑證 (讓你的瀏覽器別跳警告而已 XDD)，你也能搭配 NAS 內建的 Reverse Proxy, 讓你不同 domain 的網址都能共用 443 ports, 省了不少麻煩。這組合大推! 你需要的所有東西，NAS 都可以替你搞定。我就拿後面示範的 [Bitwarden](https://bitwarden.com/) 來說明:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-14-29-55.png)  
> 圖: NAS Docker, 架設你的服務, 並且指定 port mapping



 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-49-49.png)  
> 圖: AdGuard Home 指定 rewrite


 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-50-36.png)  
> 圖: Synology Control Panel -> Application Portal -> Reverse Proxy 轉址

我自己是沒那麼勤勞啦，不過如果你介意瀏覽器會顯示 "不安全的網站"，或是你要開放對外，必須要有 SSL 憑證的話，搭配 NAS 也是很容易一次到位的。除了上面的步驟之外，再多追加這步驟，憑證就完成了 (而且還會定期自動更新)，真是懶人的福音:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-14-36-32.png)
> 圖: Synology Control Panel -> Security -> Certification, 自動取得 SSL 憑證，並且綁定到 Reverse Proxy 轉址項目

大部分個人用的服務，大都能這樣建置起來。我自己有買 domain name (對，就是這個部落格用的: chicken-house.net) 搭配起來就更方便了。隨手架設一個服務，NAS + Docker + Reverse Proxy, 加上自訂 domain name 跟免費的 SSL, 實在是個自家用的黃金組合啊..



## 個人應用相關

> #Bitwarden

除了方便之外，我另外也補充一下，為何我推薦拿 NAS 自架服務會比自組 PC 來的適合。拿 NAS 當 server, 跟自己架設 PC 當 server, 其實有幾點很關鍵的差別。功能上都能做得到，但是 NAS 廠商在設計上的最佳化角度就完全不同。如果你還在傷腦筋這兩者之間的選擇，給你一些我的建議:

1. NAS 是以儲存為出發點, 資料的可靠度 (RAID), 資料的安全 (Backup) 都有很妥善的設置。
1. NAS 在能達到上述目的為前提, 搭配的硬體資源足夠就好 (CPU, RAM, I/O). 其餘以能長時間運作, 降低耗電為主
1. NAS 考量市場規模，使用者定位在入門與進階，基本上操作的門檻不會太高。真正需要的是背後的知識 (例如網路設定，或是憑證設置等等)

對我來說，如果要我把一些重要的服務 (重要是指資料重要)，我最擔心的是怎麼確保資料安全? 最終我還是需要 RAID 跟 Backup 啊，這些就是自己弄最麻煩的地方。過去我曾經買過這種 [MiniPC](/2016/02/07/buy_minipc_server/), 灌了 Linux 專門拿來跑 docker, 效果其實不錯, 不過維護麻煩, 加上上面的資料問題 (只能裝 SSD + HDD 各一, 難以達到 RAID1 的要求), 我終究只能擺些 LAB 的應用。像我這段要介紹的 Bitwarden 這類應用我就不敢擺上去了。

[Birwarden](https://bitwarden.com/) 是個不錯的密碼管理服務，他 open source, 也提供 docker image 讓你自己架設。家用吃不了多少運算資源的, NAS 的 CPU / RAM 要應付他綽綽有餘了，他的資料庫也沒多大，幾十 MB 就夠了。不過這類東西的可靠度要夠高啊，服務中斷一下事小，資料不見了事大。你要為了這些就在 PC server 去弄一組 RAID 嗎? 好像小題大作了，但是這在 NAS 卻是很容易辦到的事情 (NAS 的 Home 我本來就會弄 RAID1 + Backup 了，我只要切一小塊空間給 Docker Apps 用就好)。當我發現除了 LAB 以外，真正要解決自己生活上的應用，這些資料層面的問題越來越比效能跟 C/P 值還重要，這也是我逐漸放棄自組 PC 當作 Server, 而轉向改採用中高階 NAS 型號來當作 server 的原因。

我自己用 docker 架設，個人使用的服務，最具代表性的就屬 Bitwarden 了，其他像是相簿，筆記等等選擇也很多，不過我的用法沒有太特別，我就不花篇幅介紹了。你如果不放心放在別人家，自己嘗試建立看看是個好選擇。

* [Bitwarden 與 LastPass（哪個密碼管理器更好、更安全……而且更便宜？）](https://www.websiterating.com/zh-TW/password-managers/bitwarden-vs-lastpass/)

## Network Tools

> #Iperf3, #FileZilla

被我歸類在這邊的，我自己在用的有兩個: [Iperf3](https://iperf.fr/), 以及 [FileZilla FTP client](https://filezilla-project.org/).

NAS 既然負責儲存，那麼網路傳輸才是他的本業對吧! FTP 雖然已經越來越少用了，但是我自己的應用上，偶爾還是有需要啊。我想要找一個類似 [Download Station](https://www.synology.com/zh-tw/dsm/packages/DownloadStation) 那樣，有基本的功能即可，但是我需要長時間放著讓 NAS 慢慢傳輸。我需要足夠的 disk storage 當作暫存空間, 無奈找不到太多合適的 web 介面 ftp client ... 都只有 GUI 版本的 ftp client, 例如 FileZilla FTP Client ...

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-54-43.png)
> 圖: 透過瀏覽器, 內嵌 VNC player 直接操作 FileZilla ..

但是我卻無意間發現, 有人把 Linux, GUI support, File Zilla FTP Client, 以及 VNC service 打包成同一個 [docker image](https://registry.hub.docker.com/r/jlesage/filezilla/)... 這實在太方便了 XDD, 我只需要啟動這個 container, mount 好必要的 volumns, 其餘我只需要啟動瀏覽器, 用 web browser 充當 vnc client 就好了。操作上雖然不像是 web application, 比較像是 remote desktop, 不過這無所謂, 已經能解決我的主要問題了。至少在目前這是最理想的選擇。


另一個是 Iperf3, 升級到 10G, 最在意的就是連線速度了。與其每次都 copy 大檔案測試, 還要 copy 兩次避免 disk cache 等等土炮的測試方式，用 Iperf 這類正規的網路傳輸測試工具才是正軌啊! 我不想在 NAS 上用一些奇怪的手段 SSH 進去裝這些工具，我選擇用 [docker image](https://registry.hub.docker.com/r/networkstatic/iperf3/) 的方式安裝。一來效能影響應該能夠忽略, 二來這樣的安裝方式較好管理與維護。為了後續的 10G 之路，這也變成一個常駐在我的 NAS 內的 container.

Iperf3 沒有 web UI, 不過在用這工具的人應該也沒在管 UI 的吧... 你要操作時可以 SSH 進 NAS 用 docker exec 的指令來使用，後面我在說明 10G 連線測試時就是這樣測的，直接截圖:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-57-11.png)

或者，你就是不想用 SSH 的話，DSM 介面的 Docker 管理工具也能幫上一些忙，你可以直接在裡面開 terminal:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-59-28.png)

如果只是要看別的 client 連過來的測試 log, 那打開 iperf3 container 的 log 就可以了:
 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-17-59-52.png)


參考:
* Docker Hub: [Docker container for FileZilla](https://registry.hub.docker.com/r/jlesage/filezilla/)
* Docker Hub: [IPerf3 Docker Build for Network Performance and Bandwidth Testing](https://registry.hub.docker.com/r/networkstatic/iperf3/)


## Labs for Web Developer

> #vscode, #code-server, #github-pages, #mono

回到我的老本行, 軟體跟服務開發。這邊用到的有: [VSCODE](https://code.visualstudio.com/), [GitHub Pages](https://pages.github.com/), 以及我當年用來架設部落格的系統: [Blog Engine](https://blogengine.io/)

我自己工作相關，常常會需要架設一些環境自己來研究。那些短期架完就砍掉的我就不寫了，我留三個值得介紹的，都是跟我寫部落格相關的主題。其中之一是 GitHub Pages 模擬環境，加上 Web 版本的 VS CODE 整合。另一個是我過去舊版的 Blog, 是架設在 Blog Engine 之上的 (參考: [Blogging As Code!!](/2016/09/16/blog-as-code/)), 我自己的已經移轉完成了，但是我家大人的沒有啊啊啊啊。Blog Engine 當年的版本是 .NET Framework 開發的，我想辦法把 Blog Engine 讓他能在 Mono 上面執行，並且封裝成 docker image .. 有好心人先包裝好了 [linux + mono 的環境](https://hub.docker.com/r/flexberry/mono-nginx), 我只要自己再把當年的 blog engine 環境打包成 image 就好了。以下是 dockerfile 的內容:

```dockerfile
FROM flexberry/mono-nginx:latest

WORKDIR /app
COPY . /app
```

不過，我不想把我整包部落格 (包含內容) 都打包丟上 docker hub 啊，加上這只是懷舊用的，我就在本機 build docker image, 同時手動 export image, 再扔到 NAS 上面 import 就可以了。除了當年塞了一些 social plugins 現在不能動之外畫面會破圖 (記得我好像有用 FunP 之類的)，其他基本運作都 OK 啊! 貼個截圖懷舊一下我當年的 blog, 看來我當年最後一篇在 BlogEngine 寫的文章是 2013 啊...

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-15-02-51.png)
> 圖: 把當年 Blog Engine 年代的備份檔案 (code + content 一起) 重新在 container 上面跑起來的感動... (原本我都打算要用 VM 來做這件事了)


接下來，把寫部落格的環境，轉移到 NAS 上，是我進行中的一個實驗專案。我自己部落格已經轉移到 GitHub Pages 上面執行了，不過從 push 到看到結果，要等個幾分鐘啊，我自然希望能有快速一點的回饋，之前在做實驗時，發現 windows 架構的關係，container 的 I/O 效率在某些情況下會變得很糟，尤其是需要監控 file system 異動時，若又碰到 volume mount, 橫跨不同的 file system (例如 NTFS mount 到 container 內)，這時 I/O 的效能整個掉下來，我改一行字要等上兩分鐘才看的到結果 (參考: [使用 LCOW 掛載 Volume 的效能陷阱](/2018/07/28/labs-lcow-volume/))

於是我就有了這樣的念頭，能否直接把檔案編輯好放上 NAS, 然後透過 NAS 上面的 container 幫我做及時發布與預覽? 後半段我找到合適的 solution 了，就是 [Alpine Docker GitHub Pages](https://github.com/Starefossen/docker-github-pages) 了。

但是想想不對啊，我的網站最終是要 push 到 git repo 上的, 我要嘛就把 local repo 擺在網路磁碟機上，或是要預覽時 copy 到 NAS, 但是怎麼想都不對... 最後把腦筋動到 vs code 身上。VSCode 不是有 web 版本嗎 (參考: [CDR, code-server](https://github.com/coder/code-server)) ? 我把她一起裝到 NAS 上就可以了啊...

於是這樣的組合就出現了。我可以很方便地從任何地方，只要瀏覽器一開，連回家就可以開 vscode 寫部落格了。其他類似的檔案管理也可以這樣使用，VSCode 已經可以搖身一變變成 NAS 上面的檔案編輯器了。不過我還沒正式遷移到這個方案 (目前還只是在測試中)，因為我試了好幾套，能自動替我把剪貼簿裡面的圖形，存成圖檔，然後在 Markdown 插入正確的圖片連結標記的 vscode extension, 沒有一套能在這環境下運作的... 這就是唯一的未解決問題啊, 其他就一切完美了。

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-18-09-06.png)
> 圖: 透過 container, 能透過 browser 執行安裝在 NAS 上的 vscode, 也能藉由 vscode 的 terminal 執行 NAS 本地的指令

由於太多敏感資訊，我就不貼我平時工作用的畫面了，上面的圖是我另外開一個新的 container, 目的只是截圖展示一下。我只要起一個 container, 瀏覽器就能開出一個位在我 NAS 本機上的 vscode 了。因為就在本機, 只要我 mount volume, 我其實不需要另外 SSH 了，只要開出 vscode 的 terminal, 就可以直接在本機作業了。我就是這樣跟 github pages (其實背後就是 jekyll) 整合的, 不論人在哪邊，只要 VPN + 瀏覽器開啟 vscode (這有點危險，我還沒大膽到不用 VPN 就能使用), 改完可以本地直接 build 直接預覽 (也是 NAS 上的另一個 docker), 基本上也是開個瀏覽器分頁就可以看編輯的成果了。如果內容滿意，VSCODE 直接 commit / push 推上 github, 部落格內容就完成發布了。整個流程一氣呵成，沒有半點多餘的動作。真是適合 developer 的黃金組合。

參考:
* [Code-server：在瀏覽器上執行雲端 VS Code](https://noob.tw/code-server/), Noob's Space
* Docker Hub: [Code-Server from LinuxServer.io](https://hub.docker.com/r/linuxserver/code-server)


## 參考資源

其實這個段落，我本來還想聊聊 Home Assistant 的，不過我還沒弄到滿意，這段就先略過了。我把前面介紹過的相關資源跟外部連結，都收整在這裡，有需要的請取用:

* 部落格: [是時候裝一套 AdGuard Home 全局擋廣告神器了！](https://www.jkg.tw/p2158/),2019/06 Jkgtw's Blog
* 官網介紹: [AMPLIFI Teleport](https://tw.amplifi.com/teleport)
* Mobile01: [Ubiquiti Amplifi Teleport 傳送術 穿梭來去自如](https://www.mobile01.com/topicdetail.php?f=110&t=5945594)
* [WireGuard 與 OpenVPN：哪個更高級？](https://www.purevpn.com.tw/blog/wireguard-vs-openvpn/)
* 官網介紹: [UniFi Protect, 易於擴充的安全監控系統](https://tw.ui.com/camera-security)
* 部落格: [UBIQUITI UNIFI G3 INSTANT WI-FI 無線攝影機，UNIFI PROTECT 系統中最超值， 身形如麻雀，用料如殿堂](https://masonsfavour.com/ubiquiti-unifi-g3-instant/), written by Mason, 2021/09/04
* YouTube Channel: [買買買!都買！教你簡單用NAS整合管理WI-FI攝影機！｜NAS1821+安裝監視系統｜UNIFI G3 instant IP Camera 開箱｜cp值高的監視器](https://www.youtube.com/watch?v=yUFFyagPS-I)
* [Bitwarden 與 LastPass（哪個密碼管理器更好、更安全……而且更便宜？）](https://www.websiterating.com/zh-TW/password-managers/bitwarden-vs-lastpass/)
* Docker Hub: [Docker container for FileZilla](https://registry.hub.docker.com/r/jlesage/filezilla/)
* Docker Hub: [IPerf3 Docker Build for Network Performance and Bandwidth Testing](https://registry.hub.docker.com/r/networkstatic/iperf3/)



# 目標 5, 邁向 10G 的路

最後一個，就是未完成的夢想: 10G 網路。其實這也不是特別難的事情，10G 就是錢坑而已，設備跟線路湊齊就有了，就看你要不要一次跳進去...。我的選擇是，先讓骨幹做好準備，外圍先升級到夠用為止就好，務實上的考量我暫時也用不到那麼大的頻寬，短期內 2.5G 就足夠了，所以在這兩年間的升級計畫都是以這目標為準，用最低的花費滿足大部分的需求。

即使如此，也是碰到一點狀況，規劃時要留意的地方不少啊，特地保留這段，讓其他用 UniFi 全家餐，也想要升級到 10G 的人參考。10G 對家用網路環境來說，是個不算低的門檻，除了線材的挑選 (RJ45, SPF+, CAT6A, DAC, 光纖..), 設備能不能上 10G, 規格效能都是個考驗。我說明兩個我踩過的坑:

## UDM-PRO 架構上的瓶頸

要上 10G, 簡單的說設備之間每個環節都要 10G, 不然就沒有意義了。別以為 UDM-PRO 上面有兩個 10G 的 SPF+ 接上去就搞定了... 背後有陷阱啊! 這不是來自官方資訊 (我也不之來源)，但是所有 UniFi 的社群看似大家都知道這回事，就是 UDM-PRO 本身的 10G, 你要把 10G 跟 1G x 8 當作兩個分開的設備來看待 (只是他們剛好被裝在同一個盒子裡)。

最主要的原因，就是這張架構圖:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-12-41-16.png)
> 來源: [Ubiquiti Community Wiki](https://ubntwiki.com/products/unifi/unifi_dream_machine_pro)

意思是，如果我在 LAN 的 SPF+ 裝上 10G 的 NAS, 我在 LAN 1 ~ 8 每個 port 雖然都只有 1G 的頻寬，但是同時對 NAS 存取時，能否每個 client 都有 1G 的滿速, 讓 NAS 同時達到 8GB 的 throughtput 呢? 從架構圖上看來，是不行的，因為內部架構，你要把那 8 ports switch 當作內置一台 9 ports giga switch, 連結到一台 1G + 10G LAN, 與 1G + 10G WAN 的 router (咦? 這不就是 Next-generation Gateway Pro 嗎? XDDD), 瓶頸會卡在內部看不到的那 1G 連線..

所以，如果你要走 10G, 第一件事是你就要放棄左邊那 8 ports switch 了... 否則你那單一 10G port 只是升級好看的，他的流量永遠上不去 10G, 除非你的 NAS 只跟 UDM-PRO 本身的 application 通訊.. 因此，大部分社群上有經驗的人，都會配置一台專業一點的 switch, 把所有的流量都集中到 switch 身上，只把 UDM-PRO 當作 up-link, 當作單純的 router 使用。不過，就在上周的更新 (UDM-PRO firmware update: [1.12.22](https://community.ui.com/releases/UniFi-OS-Dream-Machines-1-12-22/851bdc97-fc39-40ef-bd71-786766512c58)) 這個局勢有些微的改變了。新版 firmware, 允許你自己選擇第二個 SPF+ 是要當作 LAN or WAN 看待，如果你改成 LAN，至少 UDM-PRO 有辦法有兩個 10G LAN port 可以對接，如果這樣足夠你使用，你是可以省下一筆 switch 的花費的...

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-15-28-31.png)
> 圖: UDM-PRO 更新到 1.12.22 版之後，就允許你重新定義兩個 SPF+ 的用途了

我本來天真的以為 10G 的事情只到這裡為止，直到我敗入了 UniFi Switch - Enterprise 24 PoE 想要替我的內網提升到 2.5G 時, 才發現問題並不單純...

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-12-03-47-21.png)
> 曬圖, 這段落的主角: UniFi Switch Enterprise 24 PoE (SKU: USW-Enterprise-24-PoE)

## 啟用 threat management 的效能瓶頸

購入 USW-ENT-24POE 後，很開心的用 DAC，把 UDM-PRO / USW 用 10G 連線串起來，另外多的一個 10G 則接到 NAS 身上..., 而 PC 端也升級成 2.5G 網卡, 接到 USW 上的 2.5G port.. 不過，用上前面介紹的 Iperf3, 我在 PC 端連到 NAS, 怎麼測都測不到預期的 2.5G 速度啊，而且速度是落在很詭異的 1.4Gbps 左右... (之前速度卡在 8xx mbps, firmware 升級到 1.2.22 後有改善) 如果是我配置錯誤, 走 1G port, 那我怎麼測的出 1.4G 的速度? 如果不是，難道這些設備連 2.5G 都跟不上嗎? 或是線材品質問題? 我的線材有這麼不堪嗎? 
  


```

D:\WinAPP\Tools\iperf3>iperf3.exe -c home.chicken-house.net
Connecting to host home.chicken-house.net, port 5201
[  4] local 192.168.200.100 port 55165 connected to 192.168.100.20 port 5201
[ ID] Interval           Transfer     Bandwidth
[  4]   0.00-1.00   sec   163 MBytes  1.37 Gbits/sec
[  4]   1.00-2.00   sec   169 MBytes  1.41 Gbits/sec
[  4]   2.00-3.00   sec   175 MBytes  1.46 Gbits/sec
[  4]   3.00-4.00   sec   179 MBytes  1.50 Gbits/sec
[  4]   4.00-5.00   sec   168 MBytes  1.41 Gbits/sec
[  4]   5.00-6.00   sec   161 MBytes  1.35 Gbits/sec
[  4]   6.00-7.00   sec   173 MBytes  1.45 Gbits/sec
[  4]   7.00-8.00   sec   163 MBytes  1.36 Gbits/sec
[  4]   8.00-9.00   sec   166 MBytes  1.39 Gbits/sec
[  4]   9.00-10.00  sec   171 MBytes  1.43 Gbits/sec
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bandwidth
[  4]   0.00-10.00  sec  1.65 GBytes  1.41 Gbits/sec                  sender
[  4]   0.00-10.00  sec  1.65 GBytes  1.41 Gbits/sec                  receiver

iperf Done.

```
> 測試結果: 從 PC 到 NAS 的 iperf3 的連線速度測試

後來我 SSH 進 UDM-PRO，在 UDM-PRO 上面也裝了 Iperf3 ... 各種組合都測一輪，才發現問題的源頭。我先畫張網路拓樸好了，方便大家理解好了，下圖是我的 PC 連到 NAS 的路徑，PC 用 2.5G 連線速率連到 USW-24ENT, 然後透過 10G SPF+ uplink 連到 UDM-PRO，因為屬於不同網段，所以需要通過路由 (UDM-PRO) 封包才能轉到 NAS 的網段，然後再繞回 USW-24ENT，最後走 10G SPF+ 的 port 連到 NAS (紅線) :

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-12-59-39.png)
> 圖: 從網路拓樸來看傳輸路徑。跨 VLAN 需要經過 UDM-PRO 處理 routing


為了找出瓶頸卡在哪邊，我分別測試這幾個不同路徑的 iperf3 傳輸速度:

1. NAS -> (USW) -> UDMPRO, 可以跑到 4.77 G, 還... 還可以啦 (CPU: 72%)
1. UDMPRO -> (USW) -> NAS, 1.91 G, 這....? (CPU: 84%)
1. PC -> (USW) -> UDMPRO, 可以跑到 2.35G, 正常速度 (CPU: 70%)
1. PC -> (USW) -> (UDMPRO) -> NAS, 1.4G (CPU: 85%)

不過，測試的過程中數據不是很穩定，上下落差不小，我取 30 sec 的平均值。測試過程中 UDM-PRO 的 CPU 使用率大概都維持在 70% ~ 80% 上下 (沒測的時候大約 25%)。從上面數字看來，只要經過 UDMPRO routing 的話速度都上不去啊... 我把 PC 擺到跟 NAS 同一個網段再測一次:

1. PC -> NAS, 2.37G (CPU: 35%)

這時傳輸路徑應該是這樣:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-13-00-20.png)
> 圖: PC / NAS 同 VLAN 的話，不需要 routing 就能通，只需要經過 (L2) switch 封包交換


這個測試結果看來就正常多了，看來問題就是出在 UDM-PRO 身上沒錯了... 最後追查，才發現... 我有打開 Threat Management, UDM-PRO 會分析過濾每個經過的封包，判斷他的 protocol, 以及內容與行為, 判定是否符合惡意攻擊的 patterns ... 看起來是 layer 7 層次的服務，跑這些功能是要吃 CPU 的... 當我在跑 iperf3 的時候，UDM-PRO 的 CPU usage 直接飆上來。雖然關掉就解決了，不過我沒打算關掉這功能，這時突然想到，我買的這台 switch 不是有支援 L3 switch 嗎?

要轉移到 L3 switch 之前，我做最後的測試，因為要改這個很麻煩啊 (聽說新版的 network 可以簡化設定的動作，不過還沒 release 就沒有理它了)，我直接把這個威脅偵測的功能關掉:

![](/wp-content/images/2022-06-10-home-networking/2022-06-13-00-17-12.png)
> 圖: 從 /settings/firewall & security/threat management 關掉威脅偵測的功能


管理介面上面也親切的提醒你會影響效能啊啊啊，關掉後果然速度都逼近理論速度了，NAS -> (USW) -> UDMPRO 可以飆到 9.1G, 完全就是正常的速度。看來上面的測試跑到 4.77 G 多少還是有被影響，只是高於 2.5G 所以我沒發現嗎? 另外我也測了 PC -> (USW) -> (UDMPRO) -> NAS, 沒意外, 穩穩地維持在 2.35G, 明顯的就是受到介面速度影響, 因為連線速度只有 2.5G...

最後，沒有懸念了, 我也懶得去研究威脅偵測能有哪些選項可調整, 我直接搬出了 L3 switch 的功能出來用了... 我會買這台 USW-ENT-24POE 有很多原因，有 10G x 2, 有 2.5G x 12, 有 PoE+, RJ45 ports 的佈局是一排的 (大多數 switch 為了省電路板面積，都會做成上下兩排...)，L3 switch 本來不是我考量的重點, 我個人用的流量應該不至於需要動用到 L3 吧? 雖然我切了很多 VLAN ... 結果事後證明，還好我買了這台 XDD, 看來啟動 L3 switch 來負責 VLAN 之間的 routing, 問題就全沒了。PC -> NAS 的速度很正常, 跑到 2.35G, 算是滿足我目前的需求了。

於是，我除了在家裡用上了 24 ports switch 之外，我也在家裡用上了 layer 3 switch 了.... Orz

啟用 L3 switch 之後，內網的 routing 就不會繞到 UDM-PRO 本身了。上圖的流量，在啟用 L3 switch 後應該會變成這樣:

 
  
  
![](/wp-content/images/2022-06-10-home-networking/2022-06-11-13-00-43.png)
> 圖: 啟用 L3 switch, 跨 VLAN 的 routing, 可以就近由 switch 負責, 流量與運算不需再依靠 UDM-PRO, 能有效降低不必要的流量, 也不會佔用 Threat Management 的運算資源

整個傳輸過程，只要靠 switch 就能搞定了，自然沒有 UDM-PRO 架構限制，也不會碰到 Threat Management 瓶頸了，同時也不會碰到單一線路頻寬減半的問題。可惜我的設備太陽春，沒有多餘可以跑 10G 的設備，來測看看是不是真的有突破瓶頸...，這個等以後真的有機會再補了 XDD。











## 小結


果然我還是適合軟體產業 XDD, 這 15 年前後對比, 很明顯地看到軟體的高度整合帶來的改變。過去是一種硬體應付一種需求，現在則是通通統一了，然後靠軟體來解決複雜度與整合性的問題。UniFi 還有很多不錯的體驗，例如 AR ，或是設備左邊都有個觸控的小螢幕，他的 controller 也是下過功夫，這些都是其他廠牌無法取代的優勢。靠著這些幫助，我也讓我家裡的網路環境都翻新了一次。

總算現在已經達到我滿意的階段了。這一連串的機櫃進化發展史，最後都是靠 UniFi 達成整合的啊，我自己是蠻滿意這樣的配置啦，雖然有一些小遺憾，例如沒能全面 10G, 另外 UniFi 的設備缺貨也缺得太嚴重了吧，想買還買不到...。硬體跟基礎服務的建置我都靠 UniFi 了，其他我自己有興趣架設的服務我都靠 Synology 了，工作上累積的技能，剛剛好也派上用場了，靈活一點的組合這些基本的服務，就能有意想不到的結果。

這是我自己的建置方式，花了點時間整理下來，我就當作日記了，同時也給各位參考。如果覺得好用，歡迎回來留言跟我分享 :)

