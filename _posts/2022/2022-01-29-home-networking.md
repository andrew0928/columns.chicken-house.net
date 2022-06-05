---
layout: post
title: "水電工日誌 #8. 邁向 UniFi 全家餐的升級之路"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "有的沒有的", "敗家"]
published: false
comments: true
redirect_from:
logo: /wp-content/images/2022-01-29-home-networking/2022-06-05-03-48-45.png
---

![](/wp-content/images/2022-01-29-home-networking/2022-06-05-03-48-45.png)


自從 2019/10 因為原本網路設備掛掉, 開始敗入 UniFi 的體系, 果然如同傳聞的一般, 不知不覺就整套換下去, UniFi 的設備就這樣一直繁殖下去了。事隔兩年半, 我家網路主要設備總算都更新完畢, 於是重新補上這篇, 把我對家裡網路的想法交代一下。

這篇我想寫的，不是只介紹硬體的更新而已。硬體更新沒啥特別要交代的啊，這種東西裝好了大概就無感了 (會有感都是網路出問題)。我想說明的是我怎麼藉由 UniFi 的 SDN 把我想要的環境搭建起來。從 2007 我開始在家裡擺機櫃開始，機櫃裡的設備其實都在處理這些事情:

1. 網路設施 (routing, switch)
1. 網路服務 (dns, web server, storage, backup)
1. 監控設備
1. 電話總機

回顧一下[當年的設備](/2007/10/05/水電工日誌-6-機櫃設備展示/), 果然看得出時代的眼淚, 在過去幾年都被我逐步的換掉了。這一連串設備的整併更新，其實我早就想做了，只是一直都沒有看到滿意的 solution 就沒有很積極的替換，直到我開始購入 UDM-PRO ...

<!--more-->


# 前言: 理想的網路環境

寫到前面，提到當年的設備... 我自己回顧了一下當年的文章，這 15 年來變化還真大啊... 有些當年的規劃, 現在已經完全派不上用場了。現在回頭看，投資錯誤的地方有:

1. 同軸電纜的布線完全出局了，我家已經沒有第四台了，無線的數位電視也沒在用了，家裡的監控攝影機也換成 IPCam，當時在家裡拉了 10 條的同軸電纜，目前處於完全荒廢的狀態 XDD
1. 當年網路線太保守，沒有投資 CAT6A.. (我拉的線路是 CAT5E), 導致我跟 10G 無緣
1. 市內電話幾乎完全陣亡了, 電話總機 & 牆壁上的 RJ12 插座也幾乎荒廢
1. 當年買了 4U 的電腦機殼, 組了台 PC, 跑 windows server 負責家裡的網路 & 我自己工作相關需要架設的各種 lab 環境.. 這也撤掉好幾年了, 完全被 UniFi + NAS + Cloud 取代了

以上的想法，在 15 年後其實都不一樣了，我把我期待的架構描述一下，分成五大目標，後面段落再介紹我的作法:

回到現代，一切都簡單的多了，只要有穩定可靠的網路 (包含有線跟無線) 跟足夠的頻寬，其他都不是大問題了。還好當時的網路線拉的很充足，即使只有 CAT5E, 但是到現在跑 2.5G 完全沒問題。所有升級的路線都往 IP 化, PoE 化的方向在進行。因此我的理想是，設備越精簡越好，能用一台就不要用兩台，規格能統一就不要用兩種規格。這段的過程就是我的第一個目標: 網路設備整併。

既然所有東西都往網路靠攏了，我就開始期待網路能有些隔離跟規劃了，主要是網段的規劃跟管理。過去我沒有太多網管的經驗 (我的經驗都集中在軟體開發啊啊啊啊)，設備也大多是陽春的非網管類型，直到跨入 UDM-PRO 我才開始大量使用 VLAN (這是剛好，不是只有靠 UDM-PRO 才辦的到)。我希望家人上網的品質是被保障的；我希望我的 LAB 區是被隔離的 (至少要有基本的 routing & firewall 隔離)；我希望有些我不信任的設備 (或是客人) 能上網，但是跟我家人用或 LAB 用的環境是隔離的；最後我希望能善用 HINET 提供的同時最多八組 PPPoE 撥接，有時我自己臨時需要，能直接從筆電或是 PC 撥接上網取得外部 IP，不用經過家裡的 router ..。這是我的第二個目標: 網路基礎建設。

原本我是有規劃 DVR 的 (還升級過一次)，布線相當的麻煩，需要拉一條同軸電纜 (又粗又硬的纜線)，還要外加電源.. DVR 的介面又難用的很，我希望從攝影機開始就走網路 + PoE, 或是 WiFi 加上一般的 USB 供電就好。這是我的第三個目標: 居家監控。

硬體建設的背後，終究還是要靠軟體服務來整合啊，第四個目標就是我希望有良好可靠的網路服務規劃。從 DNS 開始，到各種個人用的網路服務，到我的 LAB 環境，我都投資在 UDM-PRO, NAS, 以及上面可靠的 Docker 環境了。這部份是我的第四個目標: 網路服務。

最後一個，單純是個人的怨念而已。15 年前想說 CAT5E 可以跑到 1GB 已經很夠用了 (當時機櫃裝的 switch 還只是 24 ports 100M unmanaged 的規格而已)，沒預先準備好 CAT6A (就算只有一條也好啊, 拉到我的書桌), 也沒先拉好光纖... 不過隨著 1GB 的頻寬逐漸不夠 NAS 跟 HDD 使用的情況下，我開始肖想 10GB 的環境.. 這是我第五個目標: 邁向 10G 網路

每個阿宅，其實都想在家裡弄這些東西啊 (是這樣沒錯吧)，我運氣好一點，有機櫃跟布線，其他都是相對好辦的東西了，我就從這兩年多，升級到 UniFi 全家餐的過程中，如何逐步搭建我理想中的環境吧。


# 目標 1, 網路設備整併

整個看來，設備整併，其實是最簡單的一環了。中間經歷過很多評估考慮的過程，我就跳過了。上一篇剛採用 UniFi WiFi AP 時, 購入的一批設備 (主要是 router, 兩台 switch) 最終也被我換掉了。目前上線運作中的設備 (這批應該夠我用很久了，沒有更換的打算了，應該夠我用到壞掉為止吧) 如下:

(我就直接用 UniFi Console 提供的 Network Topology 就好了)

![](/wp-content/images/2022-01-29-home-networking/2022-02-02-01-17-48.png)

跟基礎建設有關的就都在上面了, 底下這些除了兩台 UAP AC-Lite 之外，都是這兩年間購入的, 在 [上一篇] 都還沒出現:

* UDM-PRO:   UniFi Dream Machine Pro, 擔任 router, network controller, 監控錄影 service, firewall 等服務。
* USW-ENT:   UniFi Enterprise 24 PoE Switch, layer 3 switch, 身兼了內網的 routing, 24 ports 都支援 PoE+ 供電, 提供 10G ports x 2
* USW:       UniFi Switch Flex Mini, 家人書桌上的小台 switch, 接兩台 PC 及印表機
* UAP:       UniFi AP AC-Lite x 2, UniFi AP AC-LR (Long Range)

其他網路設備 (Orz, 都是 [上一篇] 介紹的...) 都被我換下線了，包含:

* Netgear (16 ports GBE managed switch)
* Netgear (8 ports GBE PoE managed switch)
* Ubiquiti EdgeRouter-X SFP

其他更古早也被退下的設備:

* 擔任 router 角色好一段時間的刷機神器 ASUS RT-N16, 以及 MikroTek 的 RB450G ...
* 白牌的監控主機 DVR, 四路
* 市內電話主機, 3 外線, 8 內線
* 第四台 cable 訊號強波器
* 白牌 (其實有牌子，懶得記型號而已) 5 ports GBE switch

其他有些軟硬體，也被網路基礎設替代了，包含:

* UniFi Network Controller (本來是安裝在 NAS 的 docker 上, 現在內建在 UDM-PRO 裡面)
* DVR + Camera, 被 UDM-PRO 內建的 UniFi Protect 取代, 攝影機也因為老舊故障, 直接換成 UniFi Protect 系列的 G3-Flex 跟 G3-Instant
* 兩台 Synology NAS ( 8 Bay + 4 Bay ), 取代了當年那台 4U PC server, 被取代的除了硬體之外，也包含上面跑的各種服務

最後，為了跟 10G 沾上一點邊，也敗了這些東西:

* Mellanox ConnectX-3 10G NIC (SFP+), 裝在 Synology DS1821+ 上面
* Intel i225-v 2.5G NIC, 裝在我的桌機上
* USB3 2.5G NIC (Realtek chipset), 筆電用

為了串連這些東西，由於佈線的關係，加上現實的考量，我決定 NAS 主幹先升級到 10G 就好 (都在機櫃內沒有佈線的問題)，直接用 UniFi 原廠的 DAC 銅線，用 SPF+ 接頭跟 switch 對接。而 PC 端則先升級到 2.5G 就夠了。一來 NAS 我沒有用太複雜的 RAID, 單顆硬碟其實 2.5G 的速度就足夠了。也因為這樣 (加上後面會交代的 L3 switch 的連線速度問題) 我才決定一次到位，購入了 UniFi Switch - Enterprise 24PoE, 提供了 24(RJ45) + 2(SPF+) ports, 提供了 12 個 2.5G ports, 2 個 10G ports, 以及 Layer 3 Switch 的管理能力。

最後，幾乎沒有在用的市內電話，當年的我實在太睿智了 (其實只是懶得另外換線)，即使是電話線，我都統一用一樣的線材 (CAT5E) 來佈線，趁著這次我用多餘的 Patch Panel, 把機櫃跟牆上的插座，都換成 RJ45 了。線材早就是 CAT5E 了，而且電話用的插座規格 RJ11 其實跟網路的規格 RJ45 是相容的啊 (這點我是後來才知道的)，我當年根本可以不用另外做不同的插座的。現在一切都統一了，我需要時再跳線就好，隨時可以把牆上的插座按照我的需要，改成網路或是市內電話使用。

最後，硬體的整併就變成上述的這樣了。當年那麼多設備，現在只要 5U 的空間就通通搞定了。這三年陸陸續續清出了不少老舊設備，現在機櫃也清爽多了，換上 UniFi 原廠的線材 (其實價格很合理不貴啊)，10cm / 30cm 的 CAT6A 短跳線, 藍色連接主幹設備, 白色連接 Client 設備，以及 UniFi 的 DAC (SPF+), 50cm 拿來串接 UDM-PRO 跟 USW-ENT24POE, 2m 拿來串接 NAS 跟 Switch, 線材換上去整個質感就起來了 XDD, 貼一下目前機櫃的照片當作這段的結尾:


![](/wp-content/images/2022-01-29-home-networking/2022-06-05-03-49-52.png)



# 目標 2, 網路基礎建設

這段落的主角，其實都是 UDM-PRO 啊，因為這些東西大概都是靠 UDM-PRO 建立起來的。不過說在前頭，以硬體、或是 CP 值來說，UniFi 最被推崇的都是 WiFi AP 系列的產品。其他像是 UniFi Console, 或是 Switch 等等, 單純就功能與規格來說, 就沒有那麼突出了。例如 Router / Switch, 尤其是你越需要進階管理，或是講求效能的，都有其他更好的選擇，UniFi 不會是首選。不過我會在這邊談 UniFi Network，一定有它特別的地方，就是高度的整合。

也是因為 UniFi Network 高度整合這些複雜的網路管理機制，我這種半調子的網管才有能力建構這些環境起來啊，換成他牌的 (例如前一手我用的 MikroTek) 可以做得更出色，但是我學不來啊 XDDD, 因為 UDM-PRO 內建的 netowkr controller 大幅簡化, 加上 UDM-PRO 用硬體把這些服務都塞進去了, 我可以在單一設備搞定這些服務，這才是 UniFi 全家桶的魅力。我就說明一下我拿 UDM-PRO 的應用方式。

我在家裡的網路，建構了這些我期待的自用服務, 包含:

1. 5 個不同用途的 VLAN 與其之間的 routing (UDM-PRO, USW-ENT24)
1. VPN (L2TP, Teleport VPN)
1. 基本的對外攻擊防禦 (IDS/IPS)
1. 基本的網路監控與流量分析
1. IPerf3 server
1. Internal DNS rewrite (這不是 UDM-PRO 提供的, 我是裝在 NAS 上)


## VLAN

其實 VLAN 的建置跟兩年前那篇沒有太大的改變，我直接列我切了幾個 VLAN 以及用途就好。這麼做的目的可以看上一篇:

1. TRUNK(0, 10.0.0.0/24): 預設, 主要用來網路骨幹設備 ( Router, Switch, AP, Camera, DNS ) 串聯用
1. MODEM(10, --): 直連光世代的數據機, 當我有任何設備要直接 PPPoE 撥接，或是電視要直接看 MOD 時使用 (不過我沒有申請 MOD)
1. NAS (100, 192.168.100.0/24): 主要是供兩台 NAS, 以及在 NAS 上面跑的各種 docker containers, 包含我的 LAB 環境都在這邊。做基本的隔離跟防火牆，跟家人用的上網往段隔離，方便我做實驗，也方便監控流量。
1. HOME (200, 192.168.200.0/24): 主要家人各種設備上網用。WiFi SSID 也都是配置到這個網段
1. GUEST/IOT (201, 192.168.201.0/24): 直接用 UDM-PRO 內建的 Guest Network 功能搭起來的。這網段能直接上網，但是無法連到內部其他的網段。適合給那些還沒換掉的對岸聯網設備或是家電。

其實這些設定並不難，你有良好的 TCP/IP 基礎知識，還有懂得那些 VLAN 的設定方式 ( tag / untag, 或是 pvid 之類的表示方式就 OK 了 )，以及多個網段之間的 routing 管理。另外 Guest Network 就麻煩一點，除了 VLAN 跟 routing 之外，你還要知道怎麼處理認證問題啊... 這之前我在用 RouterOS 的時候就碰到瓶頸了，天分不夠弄起來就是不滿意...。在更換 UDM-PRO 之前這些設置對我而言是個大工程，尤其還橫跨多種設備時，VLAN 我得要自己去整合啊，光是換個 VLAN ID 我就得去三台設備改三次就夠頭痛的了。Guest Network 也是，沒有 UniFi Network Controller 提供的 Guest Portal 的話，我大概也是弄不起來...。這些高度整合的服務幫了我不少忙，我才會下定決心，用全家餐換掉其他牌子或是系列的 router / switch.

整合的好處是網路拓樸一目了然 (實體連結)，網段或是 switch ports 的流量也是輕鬆就可以掌握。如果你想知道這些流量都是在傳輸哪些類型的資料 (application) 也難不倒 UDM-PRO, 可以看網段，或是設備跟流量之間的統計，當你發現流量異常時，你至少可以知道是哪類通訊協定在傳資料。雖然這些都是要花 CPU 標示統計出來的，不過買了就是要用啊，這些東西要自己架設也做得到，不過要花不少功夫研究就是了。

(圖: 網路拓樸)
(圖: PORT統計)
(圖: APP統計)

至於 VLAN 之間的 routing, 除了 L3 switch 之外, 其他也沒有太多需要留意的。L3 這部分我留待最後聊 10G 的部分再談就好。

## DNS - AdGuard Home

DNS 我想了很久，最後我還是把他歸類到基礎建設這段了 (雖然他應該算是網路服務)。我不需要在家裡弄一套完全獨立的 domain name (例如 andrew.local 這類的)，不過礙於 SSL 憑證的關係，有些自己的 host 在家裡連，不想繞到外面再繞回來，但是沒有 DNS 來指路的話又有點麻煩，最後選擇在 NAS 的 docker 上面架設了 AdGuard Home 這套服務。他是透過 DNS 的機制，幫你擋掉廣告或是惡意網站，同時也提供讓你 rewrite 的白名單。當你沒有特別指定覆寫的清單，或是被 AdGuard Home 列為黑名單被阻擋之外，其他情況他都會把 DNS Query 轉發到上游的 DNS。不需要太多的管理，對我而言剛剛好夠用，就是個理想的選擇。

對 DNS 有掌控能力之後，後面會提到的網路服務就開始有好的出發點了。我可以很輕鬆的用 domain 來搭配 reverse proxy (NAS 內建), 去組織我用 docker 建立起來的一堆服務。這後面再談。


## VPN - Teleport VPN / L2TP

最後一個 VPN，也是被我歸類在網路基礎建設，而非網路服務的另一個功能。UDM-PRO 內建了幾種主流的 VPN service, 同時也內建了讓你管理帳號認證的 RADIUS service. 一樣是簡單方便的懶人 solution, UniFi Network Controller 可以幫我搞定大部分的雜事, 包含網段、Routing、開通防火牆等等。最後我設定了 L2TP/IPsec 來架設家裡的 VPN, 有需要的話我可以直接從外面撥接回家。

不過 L2TP 有點年代了，UDM-PRO 又還不支援 SSL-VPN 這類協定... 正好在上周正式 release 了新功能: Teleport VPN, 這個真的要大推一下。

Teleport VPN, 其實早在 UniFi 其他產品線就出現過了，對於懶人是個福音，幾乎不需要任何的設定就能啟用了。它背後的基礎不是基於 OpenVPN, 而是另一套後起之秀: WireGuard VPN. 相對 OpenVPN 完整的生態系，WireGuard VPN 的快速與簡易是另一個不錯的選擇。使用的體驗 加上 UniFi 的整合能力都很令人滿意，唯一不足的是目前還沒有 windows 版本的 client, 所以暫時我還拿不掉 L2TP ...

想要自己設定的也很簡單，先在 UniFi Netowkr Controller 內產生連結，給 Client 點選接受，就完成了。手機端的 APP 是 WiFi Man, 他會幫你完成所有的設定，你不需要再繞到系統那邊自己建立 VPN Profile。

(圖: generate link)

(圖: click link)

想體驗或是深入了解的，可以看一下這些介紹...



# 目標 3, 居家監控

監控系統，是主要讓我決定敗入 UDM-PRO 的最後一根稻草。雖說整合式的一體機 UDM-PRO 有很多優勢，但是不管再怎麼說，我先前也是很克難的搞定 VPN / VLAN / DNS 了啊... 主要就是先體驗過 UniFi Network Controller 的優勢，加上家裡的古早監控攝影機一台接著一台掛掉了... 於是先購入兩台 G3-Flex, 搭配當時的末代自建 controller: UniFi Video, 使用起來還不錯, 加上官網宣告 UniFi Video 不再繼續維護, 以後會將重心轉移到 UniFi Protect (這個只限定 UniFi Console 內建使用).. 於是就敗了 UDM-PRO, 同時也正式的邁入全家餐的行列

之後又陸陸續續加了兩台 G3-Instant, 有可靠的 WiFi 訊號, 又有隨手可得的 USB-C 電源供應，就這樣替換掉原本的 RG58 同軸電纜, 類比式的監控攝影機, 還有難用的 DVR 主機了..

# 目標 4, 網路服務

這段就真的是大雜燴了，有了好的基礎建設，真的要玩什麼都容易了。我在一年半前，因為原本的 NAS (Synology DS412+) 無預警掛掉了，看來是主機板陣亡了。快要十年的機器就直接讓他安息吧，備份用的設備也沒有造成什麼損失，只是剩下一台 Synology DS918+ 也有點不安。所以在接下來的時間就物色了一台新機，同時為了跑 docker / virtual machine / 10G 做好準備，就挑了這台 Synology DS1821+, 同時陸陸續續擴充了 32GB RAM, 跟 10G NIC (SPF+)。

S 牌的硬體都給的很小氣，這等級的設備也只是給到 4 ports GBE 網路, 我自己擴充才有 10G SPF+ 擴充能力。這款也開始改用 AMD Ryzen 的 CPU (v1500b), 運算能力不能跟桌機比，但是跟之前的 DS412+ / DS918+ 比起來就好太多了，至少已經可以跑跑輕量級的 virtual machine 了。網路的連線速度雖然給的很不乾脆，但是數量也夠了。10G 我就接在 NAS 的網段 (VLAN: 100) 專門拿來提供檔案傳輸的服務 (SMB), 另外接了 TRUNK 網段 (VLAN: 0) 與 HOME (VLAN: 200), 分別給 DNS 與 HomeKit Assistant 使用。

只能說 NAS + Docker 真是好物，我簡單介紹一下我在上面跑了哪些東西:

## 網路基礎服務相關

歸在這類的有 ADGuardHome (DNS), 還有取代 Synology 自己封裝的 Docker 管理工具用的 Portainer-CE. 其他還有一些冷門的我就略過了。DNS 前面提過我就不多說了，這是個必要的東西，也是所有其他網路服務架起來好不好用的基礎。沒有 DNS，你就得用 IP + PORT。你用了 IP 就沒辦法用 SSL，你也得記得每個服務的 Port 號碼。有了 DNS 你就能申請 Let's Encrypt 憑證 (讓你的瀏覽器別跳警告而已 XDD)，你也能搭配 NAS 內建的 Reverse Proxy, 讓你不同 domain 的網址都能共用 443 ports, 省了不少麻煩。這組合大推! 你需要的所有東西，NAS 都可以替你搞定。我就拿後面示範的 Bitwarden 來說明:

(圖: NAS Docker, 架設你的服務, 並且指定 port mapping)

(圖: AdGuard Home 指定 rewrite)

(圖: Synology Control Panel -> Application Portal -> Reverse Proxy 轉址)

(圖: Synology Control Panel -> Security -> Certification, 綁定到 Reverse Proxy 轉址項目)

前後互相搭配，你的服務看起來就很專業了 (誤)。

## 個人應用相關

拿 NAS 當 server, 跟自己架設 PC 當 server, 其實有幾點很關鍵的差別。功能上都能做得到，但是 NAS 廠商在設計上的最佳化角度就完全不同。如果你還在傷腦筋這兩者之間的選擇，給你一些我的建議:

1. NAS 是以儲存為出發點, 資料的可靠度 (RAID), 資料的安全 (Backup) 都有很妥善的設置。
1. NAS 在能達到上述目的為前提, 搭配的硬體資源足夠就好 (CPU, RAM, I/O). 其餘以能長時間運作, 降低耗電為主
1. NAS 考量市場規模，使用者定位在入門與進階，基本上操作的門檻不會太高。真正需要的是背後的知識 (例如網路設定，或是憑證等等)

對我來說，如果要我把一些重要的服務 (重要是指資料重要)，我最擔心的是怎麼確保資料安全? 最終我還是需要 RAID 跟 Backup 啊，這些就是自己弄最麻煩的地方。過去我曾經買過這種 [MiniPC](), 灌了 Linux 專門拿來跑 docker, 效果其實不錯, 不過維護麻煩, 加上上面的資料問題, 我終究只能擺些 LAB 的應用。像我這段要介紹的 Bitwarden 這類應用我就不敢擺上去了。

Birwarden 是個不錯的密碼管理服務，他 open source, 也提供 docker image 讓你自己架設。家用吃不了多少運算資源的, NAS 的 CPU / RAM 要應付他綽綽有餘了。他的資料庫也沒多大，幾十 MB 就夠了。你要為了這些就去弄一組 RAID 嗎? 好像小題大作了，但是這在 NAS 卻是很容易辦到的事情。當我發現除了 LAB 以外，真正要解決自己生活上的應用，這些資料層面的問題越來越比效能跟 C/P 值還重要，這也是我逐漸放棄自組 PC 當作 Server, 而轉向改採用中高階 NAS 型號來當作 server 的原因。

我自己用 docker 架設，個人使用的服務，最具代表性的就屬 Bitwarden 了，其他像是相簿，筆記等等選擇也很多。你如果不放心放在別人家，自己嘗試建立看看是個好選擇。

## Network Tools

被我歸類在這邊的，有兩個 Docker: Iperf3, 以及 FileZilla client.

NAS 既然負責儲存，那麼網路傳輸才是他的本業對吧! FTP 雖然已經越來越少用了，但是我自己的應用上，偶爾還是有需要啊。我想要找一個類似 Download Station 那樣，有基本的功能即可，但是我需要長時間放著讓 NAS 慢慢傳輸。我需要足夠的 disk storage 當作暫存空間, 無奈找不到太多合適的 web 介面 ftp client ... 都只有 GUI 版本的 ftp client, 例如 FileZilla FTP Client ...

但是我卻無意間發現, 有人把 Linux, GUI support, File Zilla FTP Client, 以及 VNC service 打包成同一個 docker image... 這實在太方便了 XDD, 我只需要啟動這個 container, mount 好必要的 volumns, 其餘我只需要啟動瀏覽器, 用 web browser 充當 vnc client 就好了。操作上雖然不像是 web application, 比較像是 remote desktop, 不過這無所謂, 已經能解決我的主要問題了。至少在目前這是最理想的選擇。

推薦: (docker hub link)

另一個是 Iperf3, 升級到 10G, 最在意的就是連線速度了。與其每次都 copy 大檔案測試, 還要 copy 兩次避免 disk cache 等等土炮的測試方式，用 Iperf 這類正規的網路傳輸測試工具才是正軌啊! 我不想在 NAS 上用一些奇怪的手段 SSH 進去裝這些工具，我選擇用 docker 的方式安裝。一來效能影響應該能夠忽略, 二來這樣的安裝方式較好管理與維護。為了後續的 10G 之路，這也變成一個常駐在我的 NAS 內的 container.


## Labs for Web Developer

VSCODE, GitHub Pages, Blog Engine (with mono)

我自己工作相關，常常會需要架設一些環境自己來研究。那些短期架完就砍掉的我就不寫了，我留三個值得介紹的，都是跟我寫部落格相關的主題。其中之一是 GitHub Pages 模擬環境，加上 Web 版本的 VS CODE 整合。另一個是我過去舊版的 Blog, 是架設在 Blog Engine 之上的 (參考: Blog As Code), 我自己的已經移轉完成了，但是我家大人的沒有啊啊啊啊。Blog Engine 當年的版本是 .NET Framework 開發的，我想辦法把 Blog Engine 讓他能在 Mono 上面執行，並且封裝成 docker image ..

把寫部落格的環境，轉移到 NAS 上，是我的實驗專案。我自己部落格已經轉移到 GitHub Pages 上面執行了，不過從 push 到看到結果，要等個幾分鐘啊，我自然希望能有快速一點的回饋，之前在做實驗時，發現 windows 架構的關係，container 的 I/O 效率在某些情況下會變得很糟，尤其是需要監控 file system 異動時，若又碰到 volume mount, 橫跨不同的 file system (例如 NTFS mount 到 container 內)，這時 I/O 的效能整個掉下來，我改一行字要等上兩分鐘才看的到結果 (參考: XXXXX)

於是我就有了這樣的念頭，能否直接把檔案編輯好放上 NAS, 然後透過 NAS 上面的 container 幫我做及時發布與預覽? 後半段我找到合適的 solution 了，就是 GitHub Pages Emulator 了。

但是想想不對啊，我的網站最終是要 push 到 git repo 上的, 我要嘛就把 local repo 擺在網路磁碟機上，或是要預覽時 copy 到 NAS, 但是怎麼想都不對... 最後把腦筋動到 vs code 身上。VSCode 不是有 web 版本嗎 (參考: CDR) ? 我把她一起裝到 NAS 上就可以了啊...

於是這樣的組合就出現了。我可以很方便地從任何地方，只要瀏覽器一開，連回家就可以開 vscode 寫部落格了。其他類似的檔案管理也可以這樣使用，VSCode 已經可以搖身一變變成 NAS 上面的檔案編輯器了。不過我還沒正式遷移到這個方案 (目前還只是在測試中)，因為我試了好幾套，能自動替我把剪貼簿裡面的圖形，存成圖檔，然後在 Markdown 插入正確的圖片連結標記的 vscode extension, 沒有一套能在這環境下運作的... 這就是唯一的未解決問題啊, 其他就一切完美了。





# 目標 5, 邁向 10G 的路

最後一個，就是未完成的夢想: 10G 網路。其實這也不是特別難的事情，10G 就是錢坑而已，看你要不要一次跳進去...。我的選擇是，先讓骨幹做好準備，外圍先升級到夠用為止就好，所以在這兩年間的升級計畫都是以這目標為準，用最低的花費滿足大部分的需求。

即使如此，也是碰到一點狀況，規劃時要留意的地方不少啊，特地保留這段，讓其他用 UniFi 全家餐，也想要升級到 10G 的人參考。10G 對家用網路環境來說，是個不算低的門檻，除了線材的挑選 (RJ45, SPF+, CAT6A, DAC, 光纖..), 設備能不能上 10G, 規格效能都是個考驗。我說明兩個我踩過的坑:

## UDM-PRO 架構上的瓶頸

這不是來自官方資訊 (我也不之來源)，但是所有 UniFi 的社群看似大家都知道這回事，就是 UDM-PRO 本身的 10G, 你要把 10G 跟 1G x 8 當作兩個分開的設備來看待 (只是他們剛好被裝在同一個盒子裡)。

最主要的原因，就是這張架構圖:



意思是，如果我在 LAN 的 SPF+ 裝上 10G 的 NAS, 我在 LAN 1 ~ 8 每個 port 雖然都只有 1G 的頻寬，但是同時對 NAS 存取時，能否每個 client 都有 1G 的滿速, 讓 NAS 同時達到 8GB 的 throughtput 呢?

從架構圖上看來，是不行的，因為內部架構，你要把那 8 ports switch 當作內置一台 9 ports giga switch, 連結到一台 1G + 10G LAN, 與 1G + 10G WAN 的 router (咦? 這不就是 USG4 pro 嗎? XDDD), 瓶頸會卡在內部看不到的那 1G 連線..

所以，如果你要走 10G, 第一件事是你就要放棄左邊那 8 ports switch 了... 否則你那單一 10G port 只是升級好看的，他的流量永遠上不去 10G, 除非你的 NAS 只跟 UDM-PRO 本身的 application 通訊..

因此，大部分社群上有經驗的人，都會配置一台專業一點的 switch, 把所有的流量都集中到 switch 身上，只把 UDM-PRO 當作 up-link, 當作單純的 router 使用。不過，就在上周的更新 (UDM-PRO firmware: 1.12.22) 這個局勢有些微的改變了。新版 firmware, 允許你自己選擇第二個 SPF+ 是要當作 LAN or WAN 看待，如果你改成 LAN，至少 UDM-PRO 有辦法有兩個 10G LAN port 可以對接，如果這樣足夠你使用，你是可以省下一筆 switch 的花費的...

(圖: 1.12.22 settings)


我本來以為 10G 的事情只到這裡為止，直到我敗入了 UniFi Switch - Enterprise 24 PoE ...

## UDM-PRO IDS/IPS 的效能瓶頸

購入 USW-ENT-24POE 後，很開心的用 DAC，把 UDM-PRO / USW 用 10G 連線串起來，另外多的一個 10G 則接到 NAS 身上..., 而 PC 端也升級成 2.5G 網卡, 接到 USW 上的 2.5G port..

不過，用上前面介紹的 Iperf3, 我在 PC 端連到 NAS, 怎麼測都測不到預期的 2.5G 速度啊，而且速度是落在很詭異的 1.1Gbps 左右... 如果速度是卡在 1G, 那我怎麼測的出 1.1G 的速度? 如果不是，線材或是設定的關係導致的嗎? 我的線材有這麼不勘嗎? 

後來我甚至 SSH 進 UDM-PRO，也裝了 Iperf3 ... 才發現:

(我先畫張網路拓樸好了，方便大家理解)

1. NAS -> UDMPRO, 可以跑到 7.x G, 算是可以接受的速度
1. PC -> UDMPRO, 可以跑到 2.5G, 滿速
1. PC -> (USW) -> (UDMPRO) -> NAS, 1.1G

因為 (1), (2) 的結果，可以證明完全不是實體連線或是線材的問題了啊




## 小結

























離上次更新 [#水電工日誌](/categories/#系列文章:%20水電工日誌) 這系列文章已經兩年了。上次的升級 ([水電工日誌 #7](/2019/12/12/home-networking/))，替家裡的網路環境打了良好的基礎，開始採用 VLAN，以及開始改用 UniFi 的 Thin AP 來替代一般家用的 router + wifi 機種 (每次都覺得這種機種的 wifi 很差, router 也很差, 然後一換就整個重來, 用兩台第二台就要廢掉一半武功)。UniFi Network 是個很好的起點, 我決定接下來的基礎連線設備都往這邊靠攏。穩定的連線都到位之後，就開始想要朝向設備精簡，提升速度，以及開始重新建置家裡用的各種服務了。

所以兩年後才有這篇，我想記錄一下這兩年間升級的設備，跟我背後的規劃及想法。我習慣是先想好了我想要的環境，物色好合適的機種或是系列，然後等機會購入 (反正不急)。要嘛等到舊設備掛了，或是等到有意外的折扣活動出現，到時就可以立刻做決定，然後下單 :D

我就先講結果了，我理想中的環境必要的設備有這三種角色，我購入的分別是:

1. UniFi OS Console (我買的是: UniFi Dream Machine Pro, 2020/04)
2. UniFi PoE Switch (我買的是: UniFi Switch Enterprise 24 PoE, 2022/01)
3. NAS (我買的是: Synology DiskStation DS1821+, 2021/01)

就這樣，到了現在這三大設備總算在今年 2022 全部到位了。<!--more-->這兩年間的設備升級，其實我是逐步在搭建我理想中的家用網路環境... 主要目標有這幾個:

1. 升級速度: 我希望內網的速度 NAS 可以上 10G, PC 至少 2.5G (線材只有 cat5e)
1. 設備整合: 我希望所有網路設定都能透過 UniFi Network 管理
1. 監控整合: 同樣的, 我希望家裡的監控攝影機也想納入 UniFi Protect 一套搞定
1. 其他服務: 我希望家裡用的一些網路服務能有效能足夠且可靠的 hosting 環境, NAS + Docker 是我的首選

以上大概就是這篇會交代的內容。這篇是我的建置過程流水帳，同時附帶一些敗家的開箱文。自己家裡用完全是以現況考量 + 自己的喜好，不見得所有的設計都是最好的架構，要筆戰就可以免了，純粹分享而已。





# 寫在前面

一切都要從 2019 換了 UniFi AP 開始。在那之前，雖然我在家裡自己架了一堆設備跟服務，這些有線的設定難不倒我，但是唯獨 WiFi 這段一直都很令我頭痛。不論買了哪台鄉民一致推薦的機種，用起來都不滿意。從當年的掛包機 (Ruckus MediaFlex 2825, 2010)，到刷機的神機 (ASUS RT-N16, 2012)，到後來放棄一台搞定改用多台小米 Wifi Mini.. 結果都一樣。最後在 2019/10 一次跳電，即使有 UPS 保護仍然掛掉了一些設備後，換了 UniFi 的系統，用多台 Thin AP + controller 的架構，才開始體會到這是架構問題，不是單一設備問題...，原來以前都搞錯方向了，枉費我大學還是念通訊的... 行動通訊應該就是要靠多個基地台搭配 controller 居中協調才能達到最好的涵蓋率啊! 改用了 UniFi 的系統讓我感受到了完全不同層級的體驗..

於是不歸路就開始了，體會到 UniFi AP + Controller 的優勢之後，我開始朝向把主要網路管理都納入 Controller 管控範圍的路線來升級，同時逐步把規格提升到我期待的層次，也在這體系下建構我想要的個人 + 居家網路環境。

接下來就是一系列的需求 + 解決方案的考量了，背後也是一連串敗家的研究。我不是個會衝動購物的人，通常都是想要的東西就會先花時間研究，看準了之後若沒有急用我也不會立刻下手，會等到適合的買點 (例如雙十一，或是特惠活動) 才下手。過程中當然會持續關注我鎖定的標的物，隨時更新我的 wish list, 直到最佳買點，或是有急迫需求 (例如 2019 那次跳電) 就不用再作任何評估可以立即下手，也不用擔心腦衝會買錯東西 XDD



這就是這兩年來背後的想法了。由於體會到 device + controller 的威力, 我開始期待把家裡的網路設備都逐步納管。從 WiFi AP 開始，接著是 internet gateway (這樣才能看到對外流量的狀況分析)，再來是 switch (這樣才能看的到內部每個 port 狀況)，全面 PoE 化 (省去佈線跟電源問題，附帶好處是耗電計算跟可以遠端斷電重啟)，接著是監控設備也開始走網路 (以前是走 cable, 直接傳輸影像訊號到 NVR) + PoE, 因此第一步就是 UniFi Dream Machine Pro (以下簡稱 UDM-PRO) 了。這個等不及特價 (沒想到上市後幾個月就半價大優惠 T_T)，一出來我就下手了。購入 UDM-PRO 後的改變，我放在: [第一步, UniFi OS Console](#step1)。購入 UDM-PRO 最主要的目的，就是管理家裡網路的架構 (UniFi Network)，跟監控攝影機相關服務 (UniFi Protect)。

接著是內部服務了。我自己工作會碰到後端的系統開發，熟悉 docker 勢必要條件，我也有不少 docker 的應用需要環境來測試。有些家用的服務 (例如 local dns) 需要架設，有些簡單或是自己用的服務 (例如 password management) 想自己架設不想用外面的，都需要一個相對可靠的地方來擺。個人用的服務我首重資料絕對不能 lost, 反而可靠度問題我忍受度還高一點, 掛掉重啟就能解決的話那就還好，只要頻率別太高就行。這時我用慣的 Synology NAS 就是個好選擇了。本來我用的是 DS918+, DS412+ 退位備份使用。DS918+ 擔任 container 其實綽綽有餘，不過要跑 virtual machine 或是某些較吃資源的服務 (CPU, RAM) 就勉強了點..., 在 2021/01 時, DS412+ 服務也夠久了，經歷過幾次的故障，最後無法開機，我就決定讓他休息了... 物色很久的 Synology 8bay plus 系列的機種我一直在關注, 剛好 DS1821+ 符合當時我的期待，CPU 運算能力足夠 (AMD Ryzen 1500B), RAM 擴充空間也足夠 (DDR4, ECC, 32GB), 連帶的也有 PCIe 8x 擴充, 我有升級到 10G 網路的空間... 這個等不及特價，DS412+ 掛掉了我就馬上下手了，無痛移轉。這段相關的建置紀錄，我放在: [第二步, Home Service Hosting](#step2)。購入運算跟儲存能力都足夠的 DS1821+, 就是希望在理想的網路架構下，我能有足夠的運算能力安全的架設我想要的內部網路應用服務。

最後就是單純的虛榮心作祟的部分了 XDD, 現在 1G 網路已經是基本配備了，稱不上 "快" ...，但是要跨越 1G 的門檻很高啊，10G 的設備成本完全是另一個等級，簡單的說就是個錢坑，直到 2.5G 開始落入可接受的價格帶。我唯一會覺得 1G 不夠用的場景是: 要從 PC (有線) 跟 NAS (有線) 之間傳輸大檔案時，即使用傳統硬碟，都會受限於 1G 的連線速度... 因此速度升級一直在我的考量內很久了，從當年敗入 UDM-PRO，其中一點考量就是它內建 10G SFP+ 的 LAN port (雖然只有一個)，就是為了這個因素啊。只要我 NAS 還在用 HDD, 那麼換成 2.5G 應該就足夠我未來好幾年內的需求了 (我家裡的線路是 CAT5E, 除了重新裝潢之外大概也沒機會換成 CAT6A 或是拉光纖，完全放棄 PC 升級到 10G 的想法了 XDD)。我一直在關注 UniFi 是否有適合的 Switch 能滿足這些需求? 原本 UniFi Switch Enterprise 8 PoE 是我的口袋名單，直到 2022/1/1 官網的新年優惠 (折抵 2022 元) 我才當下決定一次到位，稍微提升一下敗家目標，改買 UniFi Switch Enterprise 24 PoE... 這段相關的建置紀錄，我放在: [第三部, Link Speed Upgrade](#step3)。購入這台貴鬆鬆的交換器，最主要的目的就是改善內網的連線速度，還有整併各種實體連線的需求 (PoE, SFP+, 2.5G, 10G, Layer 3)

以上大致上就是這篇的摘要了，有你有興趣的內容就歡迎往下看吧! 





<span id="step1">

# 第一步, UniFi OS Console

> 本段落用到的設備清單:
> UDMPRO
> UAP-AC-Lite x 2
> UAP-AC-LR x 1
> UVC-G3-Flex x 2
> UVC-G3-Instant x 2

以我的角度來看，其實整套 UniFi 系統的賣點，就是圍繞著核心的 controller 搭建起來的 SDN (Software Defined Network). 每個設備只要能被接管 (Adoption), 就能從 controller 的角度統一管理所有的設備協作。這能從過去 "管理" 每個設備，建構起整個 "網路" 的做法，轉換為直接在 controller 內管理每個 "網路"，然後由 controller 將這些網路環境的組態翻譯成每個設備需要支援的設定，統一推送給每個設備 (provision). 這也是為何每個 UniFi 的設備都需要被 controller 接管的原因。

舉例來說，常見的 VLAN 在一般的做法是，網管先 (在紙上) 規劃好網路結構，規劃好 vlan id 等等網路結構的設計，然後逐一將這些設定套用在每台 router 或是網管型的 switch 的每個 port. 過去我就是在幾台設備中用了不同的方式在維護同一套 vlan 的經歷... 有的設備是讓你指定每個 port 的 tag / untag 的方式 (例如我這次退役的 netgear prosafe gs116ev2), 有的設備是讓你用 pvid / vid (例如我這次退役的 ubiquiti edgerouter-x sfp+), 而 unifi 的 controller 則是用 SDN 的做法，直接建立你想要的 network (vlan), 對應 port profile 然後套用在你指定的 switch port 上。

UniFi 令人讚賞的就是這些設定都被 controller 簡化了。在 controller 上規劃好 network(s), 以及 wifi(s), 指定對應的 vlan / port profile, 剩下就等 controller 替你把設定都套用在每個設備上，網路就通了。因此這整個升級過程，把骨幹的設備都升級成 UniFi 體系的設備就是我的第一步了。2019 時我是在 NAS 上面用 docker 來架設 network controller 的，這次第一步我就直接改用 UniFi Dream Machine Pro 來替代了。一來有專屬的硬體，另一來除了 network controller 之外，也開始具備了 unifi 其他服務的能力 (例如 protect, 視訊監控)。UniFi 官方的策略是，除了 network controller 提供軟體下載讓大家自行架設之外，其他軟體服務未來都只搭建在 UniFi OS Console 內，也就是 UDM, UDM Pro, UDM SE ... 等等設備上才有。

UDM 系列的設計都是 "一體機"，讓你一台搞定所有需求。這是他的優點也是缺點，最顯而易見的缺點是 UDM 就不能被別的 controller 接管了。當你有好幾個 site 要共同管理，或是 controller 本身需要 HA (high availability) 的話 UDM 是半不到的，不過我自己家裡用這樣剛剛好，我事業沒有做那麼大啊 XDD, 這也是很多人批評 UniFi 是介於商用跟個人用之間的市場區隔的原因。

了解完缺點，了解完他辦不到什麼事之後，剩下的就簡單了。一體機的優勢很明顯，網路環境需要的幾個關鍵組件都內建了，包含:

(以下是 UniFi Netowkr 的範圍)
1. Internet Access
1. (LAN) WiFi 管理相關
1. (LAN) Network 管理相關 (主要是 switch)
1. Traffic & Security 流量管理與安全防禦相關

(以下是 UniFi Protect 的範圍)
1. 設備 (攝影機, NVR)
1. Live View & Playback
1. Detection

以單一一台設備來說，UDM-PRO 其實真的算超值了。硬體就包含了
* LAN: 8 port (1G, RJ45) + 1 port (10G, SFP+) switch
* WAN: 1 port (1G, RJ45) + 1 port (10G, SFP+) failover
* NVR: 1 sata 3.5" HDD




## 網路架構 (UniFi Network)


不過，別看到 10G 就 high 起來了，這邊的坑很大，後面 (3) 再來說...。購入 UDMPRO，整個網路結構就大升級了，多年以來我想達成的架構終於實現了。我說明一下我的規劃:

一般人大概就能穩定可靠的上網就夠了，不過我這麼宅怎麼可能這樣就滿足... 對於家裡的網路，我期待有這幾個要求能滿足:

1. 穩定可靠的 WiFi, 能用多台 AP 擴大涵蓋率，讓家裡沒有收訊的死角，設備能自動漫遊到最適合的 AP
1. 用 VLAN 區分出單純要上網的設備
1. 用 VLAN 區分出 NAS 以及內部其他服務 (例如: 檔廣告用的 DNS)
1. 用 VLAN 區分出不被信任的設備 (主要是對岸的上網家電)，包含有線跟無線。這往段只允許連 internet, 其他一律封鎖。
1. 支援手機或 PC 從外面連 VPN 回來 (至少支援到 L2TP/IPSec)
1. 能有基本的入侵偵測，擋掉惡意的攻擊

撇開當時其他設備為了搞好 VLAN 花了不少時間之外，沒想到這些需求靠一台 UDM-PRO + AP 就搞定了。除了 UDM-PRO 之外，我陸陸續續添購了三台 AP, 分別是 UAP AC-Lite x 2, 以及 UAP AC-LR... 這三台 AP 都是 Quancomm 的晶片，5G / 2.4GHz 的無線基地台。雖然不是最新的 WiFi6 系列，不過非常穩定可靠啊，我也還沒有打算換掉他，畢竟無線網路對我而言都是穩定度遠遠優先於連線速度，連線速度只要讓我逛網頁跟看串流影片不至於 lag (大約 20Mbps 以上) 就足夠了吧，現有 AP 的規格遠遠超過了。我目前實體的網路拓樸長這樣 (當時還沒購入 switch, 請先忽略)，我只列出 UniFi 有接管的設備:

![](/wp-content/images/2022-01-29-home-networking/2022-02-02-01-17-48.png)

實體的連線看起來很簡單，完全沒有什麼特別的，就是每個設備都插上去而已... 不過用 VLAN 的角度來看就完全不一樣了 (這樣的彈性就是 SDN 迷人的地方啊)... 我自己用 PPT 簡單的畫了一張網路架構圖:

![](/wp-content/images/2022-01-29-home-networking/2022-02-02-02-34-39.png)

靠著 UDM-Pro, 理想的網路結構就很容易地建立起來了。我開始可以有我自己的網段去架設我想要在家裡試用的服務。架設了多少服務其實不是重點，重點是這些服務都有能被安置的地方了。

我建立了四個 Netowkr, 各別指定不同的 vlan id (如上圖)。我也替它們個別指派了對應的 WiFi SSID, 只要設備連到對應的 SSID 就好了。用途簡單說明一下:

1. 一般上網用 (200)  

大部分的設備都算在這區，包含我家人的手機、平板、電腦 (有線、無線) 等等，都算在這區。這區用 DHCP 分配 IP, 同時指派的 DNS 是我自己在 (vlan: 100) 架設的 AdGuard Home DNS, 有基本的擋廣告能力, 同時也充當我內網的專用 DNS, 如果我自己在 NAS 上跑了某些內部服務，我是可以給牠專屬的 domain name 的 (例如: 我架了 BitWarden, 我可以給他 https://password.chicken-house.net 這樣的網址)。

由於交換器跟 AP 都已經是 UniFi 接管的產品了，因此我需要了解每個 client / port 的使用流量都很容易，可以 by switch port, by client, by application 等等視角來看統計數字都不是問題。這些有在用 UniFi 系統的人大概都了解了，我就不贅述。

1. 網路服務用 (100)

額外隔離一區出來，專門擺放 NAS。我希望 NAS 別混在上網用的網段，看過很多勒索病毒的案例，一台 PC 中獎，連帶地把內網的 server 也搞掛了。格離開我希望對這類問題還能有基本防護，至少我可以在 UDM-PRO 的防火牆阻擋一些不正常的流量吧! 另外跨網斷如果有異常的流量我也能夠簡單一點的抓出來，有基本的隔離跟不同的設定是我想要的，過去設備也可以做的到，但是網管實在不是我的專業啊，有時架構想法跟得上，實際操作設定就跟不上了，這對我來說是很苦惱的事情，UniFi controller 對我最大的效益就是這部分。

軟體的部分，跟 S 牌的 NAS 就真的是完美的搭配了。我強烈推薦跟我一樣硬體組合的人都可以試一試:  
* 安裝自己內部使用的 DNS, 我是用 AdGuard Home, 你可以 overwrite 部分查詢, 在你的內網也可以用 domain name 存取服務  
* 安裝 NAS 的 docker 套件, 現在透過 docker image 發行服務已經是標準動作了, 只要你懂基本操作, docker hub 已經可以當成一個世界通用的 server side app store 了。不必受限於 synology 自己的套件服務, 你幾乎能架設所有通用的服務.. 這已經是必備的功能了  
* 啟用 NAS 的 reverse proxy, 為何我大推建立自己的 DNS? 安裝的 container 一多，難免你會碰到 port 衝突的問題。當然 container 可以 port mapping 錯開，但是你要使用時都要記好 port number 也很煩啊，所以我的作法反其道而行，內網盡量用預設的 port, 衝突問題我就交給 reverse proxy 來解決。用不同的 domain name 來區隔, 我就能共用實體的 port 了。Synology 內建 NGINX 來擔任 reverse proxy, 可以省下不少管理的功夫
* 啟用 NAS 的 SSL 憑證管理。這是最後一個大推的服務，Synology 幫你整合了 Let's Encrypt 憑證的申請 + 定期更新，同時可以替你綁到對應的 reverse proxy 上面。簡單的說你只要把你的 container 服務透過 reverse proxy 發布，NAS 就會替你管好所有的 SSL 憑證問題了。現在的瀏覽器，沒有 HTTPS 很煩人的，有潔癖的人可以試試

1. 隔離設備用 (201)

這是另一個我購入 UDM-PRO 的原因，內建 Gateway... 只要 Gateway 也能接管，UniFi controller 就能很容易的建立出 Guest Network. 就字面上的意思就是你能讓訪客上網，同時又能跟你內部網路 (除了 guest network 以外所有的) 完全隔離。Guest Netowork 也可以有 portal, 第一次登入後要在網頁上輸入密碼才能連線，就像有些餐廳或是旅館的設置那樣。

這些需求，沒有搭配 UniFi 的 Gateway 其實弄起來就很麻煩啊，我這種外行人實在很懶得去跟他奮鬥，不過現在就容易得多了就沒有不用的道理了。在 Guest Network 內的設備，我至少不用擔心她會竊聽到我其他網段的流量，自然也不用擔心有些看不到的攻擊等等。這些不信任的設備，我就都讓他連到這個 SSID 就好了。如果有對應的 APP 需要安裝怎麼辦? 我找了台舊手機裝這些 APP, 手機也連到這個網段就好了。

在這個年代，別在你主要使用 (有幾乎你所有的個資跟使用習慣) 的手機上安裝對岸的 APP 應該已經是常識了吧?


1. 網路骨幹用 (0)

最後，就是 UniFi 自己的設備了。其實這個有點多餘，不需要他也可以運行的好好的，單純個人喜好而已。我多切了一個網段出來，收納這些要被接管的 UniFi 網路設備。包含 switch, wifi ap, camera 等等，包含有線連線，也包含無線連線的設備。

UniFi 自己定義了擴充的 DHCP options, 設備取得 IP 時連帶的也會知道要接管的 controller 在哪裡, 這些設備重新連線就會找的到 UDM-PRO 了。這個網段的 DHCP 我啟用了這個 option, 以後有新的 UniFi 設備 (應該都買齊了吧 @@)，放到這邊就可以被接管了。


## 監控攝影機 (UniFi Protect)

網路結構搞定後，接下來就是監控攝影機了。這方面還真的不大需要擔心，UniFi 都弄得好好的，我只要買對的設備回來安裝就好...

必要的設備，就是監控主機 NVR 了。說是 NVR，其實主要核心就是背後的監控服務，UniFi Protect。UDM-PRO 你只要啟用這個 app 就可以了。不過 UDM-PRO 的儲存空間有限 (只能安裝一顆 3.5" SATA HDD / SSD, 不支援 RAID)，運算能力也有限，能接管的攝影機數量是有上限的 (我沒去查，不過我自己接四支攝影機是夠用了)。這些都足夠的話，UDM-PRO 是個很好的起手式。

接下來就是攝影機了。我是先買了兩台 UniFi G3-Flex, 透過 PoE 供電的機種，供電跟連線一次搞定。由於前面的網段早就規劃好，這邊實在沒什麼難度，只是 UDM-PRO 不支援 PoE, 我得另外想辦法就是 (先前我用 ER-X SFP 頂著，後來改用 USW-Enterprise-24PoE)。後來越用越順手，趁著官網短暫的開賣 (一上架就被搶光了) 幸運的搶到兩台 UniFi G3-Instant, 這是透過 USB type-c 供電的機種，連線則是透過 WiFi。話說這台 G3 Instant 真是超值，我看了 [這篇: UBIQUITI UNIFI G3 INSTANT WI-FI 無線攝影機，UNIFI PROTECT 系統中最超值， 身形如麻雀，用料如殿堂](https://masonsfavour.com/ubiquiti-unifi-g3-instant/) 開箱文才知道，他的用料一點都不含糊，賣這價格被搶光是正常的，他應該扮演的是鼓吹大家多多購買 UniFi OS Console 以及 UniFi AP 的帶路雞吧... 畢竟沒有 Console + AP, 你也沒辦法使用這台監控攝影機... 這台攝影機的供電，只要普通 USB-C 變壓器插上去就可以用了，如果你想要不斷電，也不用買 UPS 了，找個行動電源插上去就是個陽春的 UPS 了。短暫斷電 (只要你的 WiFi 跟主機也有 UPS) 就不會影響運作了。

用了 UniFi Protect, 良好的網頁介面，跟 APP 都是我大推的主要原因。過去用的是便宜的 DVR, 那個介面難用到想打人... 跟 UniFi Protect 比起來完全是兩個世代的產品，大推。

不過這邊我特地補充一下，UniFi Protect 也不是全然沒有缺點。即使你額外添購了 UniFi NVR，支援磁碟陣列，我覺得用起來也不夠順手，離真正可靠還有一段距離。主要是差在這裡:

1. 缺乏良好的 DISK 管理機制
UniFi 把這些管理都做得很簡單，相對的是你只能買新硬碟插上去，然後讓他 init, 其他你就不能做了 (對，連格式化，或是選擇 RAID TYPE 都沒機會)。

2. 缺乏SMB等等網路傳輸的支援
UniFi Protect 唯一下載錄製影片的管道，是透過 Web 或是 APP 選取影片段落下載。並沒有很簡單的方式把大範圍的影片一次備份出來的方法。

還好 UniFi 提供了不錯的替代方式，在 UniFi Protect 服務，他可以替每個攝影機用 rtsp:// 的協定轉發串流影像。他是統一透過主機轉送 (你可以把這功能當成 RTSP 協定的 reverse proxy)，可靠度跟連線速度是看主機，不是直接連到攝影機本身。我自己是搭配 synology surveillance station 的監控服務來當作後級備援。你在 Synology Surveillance Station 新增 RTSP 攝影機，輸入 UniFi Protect 提供的 rtsp:// 網址即可。這麼一來，你轉發的攝影機內容，也會同步出現在 Synology 的監控服務上了。Synology 是 NAS 起家的公司，剛好上面的缺點通通補上了，只要你有足夠的授權 (S 牌 NAS 都內建兩個攝影機的授權)，你是可以搭配使用的。要簡單好用，直接用 UniFi Protect, 要可靠，長期備份, 有效管理硬碟檔案，大量匯出錄製影片等等進階需求，轉發到 Synology Surveillance Station 處理。




## UDM-PRO 小結

雖然購入 UDM-PRO 的過程碰到不少障礙，包含新產品線剛出來，UDM-PRO 有好一段時間是不大穩定的 (現在不會了)，同時剛上市的價格也不便宜 (後來官網有半價促銷，事後的訂價也比剛上市時便宜許多)，現在又有替代機種 UDM-PRO SE ... 不過我不後悔先買了這台。他的確替我解決了網路基礎建設的很多鳥問題，只要你有需求，大推!





<span id="step2">

# 第二步, Home Service Hosting

> 本段落用到的設備清單:
> Synology DS1821+ (主力機), 32GB DDR4 ECC RAM
> Synology DS918+ (備份機)
> Synology DS412+ (已退役)

有了可靠的基礎建設，就像一個城市的道路交通跟衛生下水道等等都完善後，就可以在上面做各種服務建設了，例如公園，醫院，活動中心等等。我當時的想法也一樣，我自己擅長的是雲端服務開發跟規劃啊，自己家裡沒有對應的配置怎麼說得過去? 雖然我一直有在 NAS 上架設一些自己用的小服務，不過從 DS412+ 換到 DS918+ (當時也是想很久然後碰到特價活動)，總覺得缺了點什麼...

兩個原因，一個是 Synology 給的硬體實在太保守了。當 NAS 的話網路速度都卡在 1G, 即使 plus 系列通常都有 2 ~ 4 ports, 不過 1G 給我那麼多個也沒用啊，即使 LACP 啟用了，我自己 PC 單機的連線速度還是受限。1G 的頻寬很容易就到頂了，現在的 HDD 隨便都能突破，至少到 2.5G 比較合理一點。無奈 S 牌 NAS 沒這選項，要嘛就 1G, 要嘛你要往上跳一大級，挑選有 PCIe 擴充槽的機種，然後自己加購 10G 網路卡...

另一個是運算能力。NAS 主要任務是處理 I/O, 通常 CPU 都給得剛剛好而已，要拿來當運算服務，即使是 DS918+ 也不大夠用，CPU 跟 RAM 都有類似的困境。我想跑 VM 或是跑大型一點的 container 就卡住了啊...

因為有這些念頭，在 2021/01 我的 DS412+ 服役八年多之後不幸 (該說不幸嗎? @@) 在某次關機後就再也開不了機了，我就把 DS918+ 退居二線擔任備份用的 NAS，這次就直接添購一次到位的機種 DS1821+, 並且一次把 ECC RAM 加滿到 32GB, 上線當作主力機來使用。


## 網路服務環境準備

有了足夠的運算能力，我開始在上面架設我理想中的服務了。這邊我要大推一下 Synology DSM, 有很多實用的小設計，非常適合像我這種個人使用的環境。我雖然知道怎麼善用 public cloud, 善用 container / kubernetes 等等大型服務的基礎建設, 不過自己在家裡搞這些太超過了啊, 家用我只要有基本的穩定度就夠了, 其他則是省事經濟一點為優先。因此就不考慮 azure / aws 之類的服務了, 也暫時不考慮 kubernetes 這種架構了，簡單的 docker, 頂多用到 docker-compose 就夠, 其他盡量用現成的。

Synology DSM 在這需求上，幫了我很大的忙。在 NAS 上面架設自己個人或家用的服務，有很多好處的。一來是取得方便，買來就可以用了，相較在公有雲上面開設對應的資源，自己購買 NAS 不但經濟，而且也夠穩定可靠管理容易。二來 NAS 本身擅長的就是磁碟管理跟資料備份，你不大需要去考慮儲存容量或是資料遺失之類的問題，只要你 mount 的 volume 有選擇正確的 RAID type, 有做好正確的備份設定就夠了，不大需要額外花心思去顧慮資料的可靠度等等問題。因為這些特性，那些媒體管理類型的服務 (例如相片管理，音樂或是影片管理，或是 BT 下載管理類的服務特別適合) 都在候選清單內，只要你有需要的話。我就挑幾個我最推薦的功能來介紹就好。

1. Docker

這個我想不用說了吧，沒有 docker 你大概只能 ssh 進去自己安裝 (太麻煩)，或是只能選用官方包裝好的套件了 (選擇太少)。這是必裝的套件，不用考慮。不過你倒是要習慣一下他的管理介面，我會推薦安裝時還是直接 ssh 進去自己下 docker cli 比較容易。一來不會被陽春的 UI 限制住，二來所有的 offical docker image 的說明都是用 docker cli, 你還是得看得懂 CLI 才知道怎麼對應到 Synology Docker UI 的操作。

這邊我推薦一個能夠管理 docker 的服務 (你也能用 docker 來安裝這個 docker 管理服務...): Portainer, 一來這個 UI 比起 NAS 提供的管理介面完整的多，另一個原因是他支援 stack, 你能在 UI 上管理 docker-compose, 有些服務需要一次架設多個 container 時你就會需要了，一次管理一組 container 是很實用的功能，全手動你應該會煩死吧 XDD

1. DNS (AdGuard Home, on docker)

再來就是 DNS 了。我用這套: AdGuard Home，他是一套 DNS server, 他透過幫你轉發 DNS query, 搭配定期維護的黑名單, 利用 DNS 的方式來幫你阻擋各種廣告或惡意軟體。同時也讓你有能力局部的改寫 DNS 查詢結果，你可以透過這樣替你自己的服務加上 domain name, 而不用真得大費周章架設 DNS 跟建立 domain ...

同樣性質的服務其實也有別套，我不特別推薦 AdGuard Home, 不過我推薦這類型的服務你應該挑一個順手的架起來自己用。即使內網，你能用 domain name 來連線會比用 IP 方便得多，另一個更重要的是有 DNS 你才有能力搭配 Reverse Proxy 共用 443 port 發行你自己架設的服務。RP 可以透過 domain name 幫你對應到不同的 ip + port, 這麼一來你就能夠排除 docker 不能轉發相同 port 給不同 container 的困境


1. Reverse Proxy / Certification

同上所述，NAS 的 RP 是個很好的應用程式入口服務，就如同 kubernetes 的 ingress 一般，個人用可以簡化一點，但是你終究是需要一個這樣的角色的。用 NAS 內建的好處是管理容易，他背後其實就是 NGINX，你可以省掉自己編輯 nginx.conf 的苦差事。另一個好處是 NAS 內建 HTTPS 憑證的管理，S 牌的服務可以替你跟 Let's Encrypt 申請憑證，也能在三個月到期之前自動幫你 renew. 同時這些憑證還能自動幫你綁到內建的 RP 上面。

因為這些都是 S 牌 NAS 內建的服務，整合的也很完美，個人家用剛剛好，大推。

這些都準備好之後，我要自己玩玩新的服務就很容易了，大致程序是這樣:

1. 架設服務，給他一個 port (通常我照順序排)，例如 docker run -d ...... -p 8001:443 ......
1. 給專屬的 domain name, 例如 myservice.domain.com -> 192.168.100.123 (NAS IP)
1. 設置 RP, 將 https://myservice.domain.com 轉發到 127.0.0.1:8001
1. 申請 SSL 憑證，綁訂到 (3)


舉我實際的例子示範一下，我自己用 docker 架了 AdGuard Home 當作 DNS, 我希望內部網路可以用 https://dns.chicken-house.net 當作管理的網址入口，從 docker 開始上面的步驟:

// 略



## 網路服務

這些東西上手後，你開始要擔心的是不自覺就架設太多服務了 XDD, 要列應該列不完吧, 有太多適合這樣架設起來自己在家裡玩的服務了。下一步就是挑選你想在自己家裡架設哪些服務來用了。我貼了幾篇其他人的建議:

https://www.mobile01.com/topicdetail.php?f=494&t=5110556
https://post.smzdm.com/p/avwd6ngn/

我自己則是用了這幾套:

工具類:
1. AdGuard Home
1. Home Assistant
1. BitWarden Server
1. iperf3
1. BT client
1. FTP client

媒體管理類:
1. // photo
1. // video
1. // music

開發用:
1. Legacy ASP.NET support (mono)
1. Legacy Windows Service (virtual machine)
1. code server
1. github pages server
1. pgsql + pgadmin
1. Ubuntu (當作輕量化的虛擬機來用)








<span id="step3">

# 第三部, Link Speed Upgrade

> 本段落用到的設備清單:
> USW-Enterprise-24PoE
> Maxxon ... 10G NIC (SFP+), on Synology DS1821+
> Intel i225-v 2.5G NIC
> USB3 2.5G NIC (Realtek chipset)
> DAC x 2

其實這段應該擺在第二部分來談的，只是我自己實際執行的順序是擺在最後而已。應該要擺在中間的原因是，這部分其實會稍微影響到前面的網路架構跟服務架構 (因為 layer 3 network 的關係)，如果你要參考我的結果重新建置，順序對調會更順利一點。

會把這段獨立出來寫，主要是因為超過 1G 以上的連線速度，到處都是坑啊! 有錢坑，也有陷阱，一不小心就踩進去... 即使我不貪心，只求 2.5G 也是一樣... 有心要用 UniFi 全家餐，又想用 2.5G / 10G 的可以先參考看看..

首先先來科普一下，有幾件事是你必須先知道的:

1. 規格:  
2.5G 連線速度，是 10G 的規格降頻來的。所以有些老一點的設備只支援 10G, 不支援 5G / 2.5G 等等這種速度的，如果你要從淘寶買 server 的拆機零件的話要特別注意。
1. 接頭:  
同樣 10G 的連線速度，用 SFP+ 跟 RJ45 的成本完全不同... SFP+ 本身便宜，熱量低，貴的是那個 SFP+ 頭... 另外不管你是 switch 內建 RJ45, 或是你買 SFP+ 轉 RJ45 都一樣，光轉電的發熱量很高的
1. 線材:  
如果你的接頭是 SFP+，距離短的話你可以選擇 DAC (3m 以內)，便宜，發熱低，簡單。超過的話就要買 SFP+ transiver 跟光纖了。  
如果你用的是 RJ45, 那要上 10G 你至少需要用 cat6a 的線材。如果 5G / 2.5G, 那 cat5e 就夠了
1. 設備:  
UDM-PRO 只提供一個 LAN 的 10G SFP+ 接頭, 你如果 PC 跟 NAS 想要達到 10G 連線，要嘛直連不要經過任何 switch / router, 不然你至少要買台 3 port 以上支援 10G 的 switch 才能滿足完整的 10G 連線..
1. 拓樸:  
如果你的案例像我一樣，NAS 跟 PC 分別處於不同的網段 (我用 vlan 隔離), 那麼問題會在更複雜一點, 你要考慮到你的 router 效能撐不撐的住。跨越網段的流量 switch 是無法直接轉發的，一定要送回 router 處理才行。

由於以上種種限制，排下來能接受的組合其實很有限。我期待 NAS 至少能用 10G SFP+ 的規格連到 switch, NAS 跟 switch 都擺在機櫃，用 DAC 就足夠了。而我的 PC 在另一個房間，當年布線只用了 cat5e 的線材，短期內我也不打算抽掉換線，因此 PC 端我只要 2.5G 的連線速度就夠了。按照這期待，我最後列出來需要採購的交換器條件:

1. 至少需要具備 10G SFP+ x 2 ports
1. 至少需要具備 2.5G RJ45 x 3 ports (我有三台設備要用到 2.5G 的頻寬)

從 [這張表: UniFi switch comparison](https://www.ui.com/switching#compare) 來看，符合規格的 "單一" 設備只有這兩台啊: USW-Enterprise-8PoE, USW-Enterprise-24PoE. 原本我是鎖定 8 port 這台的，後來沒捏好就拜了 24 ports 這台 (事後證明我買對了 XDD)。

連線速度，要整個路徑都打通，才能達到我想要的連線速度啊 (2.5G), 因此把路線標出來是重要的。我把上面那張說明 vlan 架構的圖，升級一下，加上交換器。PC 要從 NAS 複製 1GB 檔案的話，資料必須按照紅色的路線傳輸:

![](/wp-content/images/2022-01-29-home-networking/2022-02-02-23-50-05.png)

簡單的計算一下，如果 PC 端想要全速下載檔案，標記 (1) 是 NAS 連到 USW 的 port, 流經這個 port 的資料至少有 2.5Gbps 的流量 (後面以此類推)。然而 PC 跟 NAS 是不同的 VLAN，因此流量會流到 UDM-PRO，(2) 的部分就必須承受 2.5Gbps (In) + 2.5Gps (Out) 的流量，(3) 的部分就必須承受 2.5Gbps 的轉發流量，最後 (4) 的 port 則必須承受 2.5Gbps 的流量。

這四個環節，任何一個點跟不上，整個速度就上不去了。UDMPRO 的部分，我在 [ubnt wiki](https://www.ubntwiki.com/products/unifi/unifi_dream_machine_pro) 找到這張圖:

![](/wp-content/images/2022-01-29-home-networking/2022-02-02-23-56-26.png)

看起來 LAN SFP+ 是直通 CPU 的啊，看來 CPU 處理 routing 的速度就是關鍵了，也是整個規格上沒有明確標示的環節。於是，我在 NAS 上面裝了 iperf3 (對，就是用第二部的 docker 安裝的)，在 PC 端測試看看。結果意外地只跑出 800 Mbps 左右的數字，直接從 NAS 拉檔案 (我重複複製同一個檔案，確保檔案已經在 NAS 的 cache 內) 大概也是停在這個速度就停了...

// 補圖

為了抓問題，我 SSH 進去 UDM-PRO，在 UDM-PRO 裡面也跑了 iperf3, 這樣測出來的成績應該就不需要經過 routing 轉發，跑出來的成績就很正常，大約是在 2.5Gbps 左右。

// 補圖

同樣的測試，我也從 NAS 對 UDM-PRO 測了一次，理論值應該是 10Gbps, 跑出來大約在 8Gbps 左右，基本上也算在正常範圍內:

// 補圖


中間抓問題的過程我就跳過了，有興趣的可以到這 facebook 討論串研究。最後是我 UDM-PRO 啟用了 IDS/IPS, 導致整個 routing 轉發的效能掉下來沒辦法跑到全速。不過，即使我關閉 IPS, 或是把這兩個網段設定掠過清單，過程中也發生過沒有重新啟動 UDM-PRO 的話，速度還是一樣拉不起來。

最後，我買的這台是支援 layer 3 network 的 switch 啊，理論上應該可以走底下這條綠色的路徑才對啊:

![](/wp-content/images/2022-01-29-home-networking/2022-02-03-00-08-33.png)

果然調整過後，重新測試了一次，就算 IPS / IDS 全開也能輕鬆達到正常速度 2.5Gbps. 測試了 traceroute 結果也正確無誤。測到這時我心裡就想..

> 不就還好我有買支援 layer 3 switch 的機種，不然現在不就尷尬了嗎?

這時我開始慶幸我挑的是 24PoE 了，另外看上的 8PoE 那台雖然也支援 layer 3, 不過官網是說未來的韌體更新才會加上去啊! 也沒給時間表，意思是我如果買了我還不能馬上用全速跑.. (截至這篇文章撰寫時間 2022/02/02 為止，官方正式釋出的 firmware 還不支援 layer 3 switch).. 

另外，也因為我在 switch 上面啟用了 layer 3 routing, 因此 PC 跟 NAS 的設備，我最理想的接法是通通都接在 24 port switch 上比較合適，如果我還把這兩個 vlan 的設備接在 UDM-PRO 的 1G x 8 ports 上面的話，就真的繞了超級遠的路了。不但拓樸繞路，中間也會經過 UDM-PRO 內部 8 ports 共用 1G 頻寬的瓶頸 (經過 CPU 的那段只有 1G 頻寬)。怎麼想都不應該這樣接，因此相對的 UDM-PRO 上面的 8 ports 我能運用的空間也變小了，這是另一個我慶幸我最後是買了 24 port switch, 而不是原本決定的那台 8 ports switch ...

以上是我為了突破 1G 速度限制，所踩過的坑，當然很多人都會說直上 10G 才是王道，不過我事業沒做那麼大啊，現在的狀態對我來說是個最適合的平衡點了，保留了 10G 的升級空間，現階段可以全面提升到 2.5G 的速度，只要我的 NAS 還在用傳統硬碟 (HDD) 的話，這速度應該都還夠用，而且這樣的搭配我可以有足夠多的 port 都能支援 PoE+, 同時也可以達到精簡設備的目的 (如果我買 8 ports 那台就沒辦法淘汰舊設備了, ports 會不夠用), 整體來說是值得的啦。

這些坑陷阱還蠻多的，如果你不像我一樣家裡自己搞了 VLAN 來折磨自己，也許這些都不會是問題，如果有，設備的挑選就要留意一下..., 經過這次的升級，我終於體會到大家所謂的 10G 都是錢坑 這句話的意思了, Orz ...

<!--
另外我也補充一下小插曲，在測試過程中發現，其實 UniFi 的 Network Controller 是這樣建構 layer 3 network 的。我是參考官網這篇 KB: [UniFi - USW: How to Enable L3 Routing on UniFi Switch](https://help.ui.com/hc/en-us/articles/360042281174-UniFi-USW-How-to-Enable-L3-Routing-on-UniFi-Switch) 的說明摸索出來的，文內提到為了讓 layer 3 routing 能夠正常運作 (其實就是把 switch 也當作一台有基本功能的 router 來看待), controller 會自動建立 inter-vlan routing 這個 network (vlan id: 4040, ip: 10.255.253.0/8) 來當作橋接. 因此我就突發奇想，如果我把 PC (vlan: 200) 的 port 指定到 UDM-PRO，那會怎麼樣?

我分別以不啟用 & 啟用 layer 3 network 的角度來看一下這樣的設定，預期的路徑應該怎麼跑。先來看看 layer 2 的模式:




再來看看 layer 3 的模式:
-->







<!--

不得不說，UniFi 的設備整合度都做的不錯，除了 NAS 之外上述需求大概都搞的定... 以下是這篇文章內會出現的主角們:

- UniFi Dream Machine Pro
- UniFi Enterprise 24 PoE (layer 3 switch)
- UniFi Flex Mini (5 ports managed switch)
- UniFi Camera (G3 flex, G3 instant)
- UniFi AP AC-Lite, AC-LR
- Synology DS1821+, 10G SFP+ NIC
- PC / NB 用的網卡: Intel i225v, 2.5G PCIe 1x NIC, Realtek 2.5G USB3 NIC

舊的不去新的不來，過程中也汰換了一些只上線了兩年，就被退下的設備們:

- Netgear Prosafe GS116Ev2 (16 ports managed switch)
- Ubiquiti EdgeRouter-X SFP (5 port router, 也是 UniFi, 只是不同系列)
- PoE injector (因為設備整合，退下來的一堆零件)
- Intel i350-T4
- 壽終正寢的 Synology DS412+ (特此紀念)


# 第一步，升級主要設備

在上一篇 [水電工日誌 #7](/2019/12/12/home-networking/)，大約是 2019/11 的時候，因為家裡跳電掛了一些設備，於是開始啟動想了很久的網路升級計畫。當時主要在硬體升級，把 wifi ap 從 asus / 小米, 替換成 UniFi 的 AP, switch 也開始改用網管的機種, 用 vlan 開始重新整理家裡的網路結構。整體來說只是打個基礎而已。

不過人就是越用越貪心啊，當時礙於有設備故障 (包含 router 及 switch), 就沒有選擇一次到位全面更換 UniFi 全家餐 (只有 AP 而已), 不過 SDN 的魅力實在太大，用了就回不去了。雖然 UniFi 的 router 及 switch, 在規格跟可靠度都還不算頂尖, 不過在不錯的硬體用料, 良好的 controller 使用體驗下，我還是一步一步地更換了...

這兩年來的更新，主要是想要解決幾個主要問題 (前面提過了, 升級速度、設備整合、隔離設備、監控整合、建構其他服務)，想來想去，有三個主要的設備是需要升級的 (其他都是搭配使用的), 按照我採購的時間順序, 分別是這幾種角色:

1. UniFi OS Console
1. UniFi PoE / 10G + 2.5G Switch
1. NAS + 10G NIC

在 UniFi 的 roadmap 裡面, UniFi OS console 已經是不可或缺的設備了。雖然 Network Controller 還能夠自己下載安裝，但是其他的應用 (例如監控: UniFi Protect) 已經開始變成 UniFi OS console 限定的了 (前個世代的 UniFi Video 已經不再支援了)。同時要有足夠的流量與 IDS/IPS 管控, 整合的 Gateway 也省不掉。於是，在 2020/04 UniFi Dream Machine Pro 剛上市時就敗下去了 (沒等到後來的半價優惠，實在是虧大了) ..., 完成第一步。這步到位後，開始解放整個網路的管理跟監控了。由於 Gateway 也開始納入 controller 管控, 我開始有機會建立 Guest network, 也開始能夠監控 client 的對外流量, 以及 IPS 層級的外部攻擊防禦能力了。

接著，原本我是兩台 NAS 上線服務 ( Synology DS918+ 為主, DS412+ 為副 ), 結果也是某天 DS412+ 無預警掛掉了，想想一台 NAS 都陪我八九年了，這次添購到他淘汰可能又是十年，這次牙一咬，直接一次到位挑選理想的機種: Synology DS1821+, AMD Ryzen CPU, 可擴充至 32GB ECC RAM (當然是插滿), 8 Bays, 有一個 PCIe 8x 擴充槽可以外加 10G 網卡... 想想這已經有足夠的運算跟傳輸能力了，就在一年前 2021/01 購入，替未來的 10G 跟各種服務執行環境做好準備, 完成第二步。硬體規格的解放，我的服務搭建 (包含 docker, 以及 virtual machine) 都不再是問題了。

最後，就差實體連線的 switch 了。在那之前，用的是拼湊的高 CP 值解決方案，退居二線的 EdgeRouter-X SFP 內建 PoE (24v, passive), 剛好足夠當時的 AC-Lite / AC-LR 使用, 我也沒特別再去購入 UniFi 的 PoE 交換器了.. 至於 VLAN 我直接買別牌的來使用 (Netgear GS116Ev2). 雖說都是走 802.11q VLAN 規格，互通都是沒問題的，不過不能在同一個 controller 內指派，SDN 的方便性就不存在了啊! 但是也好在有這段經歷，也讓我摸熟了 VLAN 的 tag / untag 是怎麼一回事。壓垮理智線的最後一根稻草，就是 2022/01 的一項促銷活動，在迎接 2022 的那幾天，滿 xxxx 元的訂單 (消音) 就可以優惠 2022 元，此時不敗更待何時? 於是就挑選了這台交換器: UniFi Enterprise 24PoE, 支援 10G SFP+, 2.5G, PoE+, Layer 3 等功能的交換器。補了這台，總算完成第三部，就此全部到位。因為這台 switch, 把硬體的所有的連線相關問題都解決了。PoE 的 port 數量足夠，我可以撤下所有拼湊的 PoE injector / 舊規格的 24v passive, 這台也解放了 10G SFP+ 跟 2.5G RJ45 的連線能力 (我家裡佈線只有 cat5e, 2.5G 我就滿足了), 最後是個意外, 原本只是把 layer 3 switch 當作加分項目而已, 沒想到這也是個必要條件 (後面補充)。

這三套設備到位後，剩下的就是考驗我的駕馭能力了... 搞不定就只剩下我的本事不夠而已...














-->

<!--

0. udm-pro cross vlan routing with IDS enable -> low performance ( only 850Mbps )
0. use 扁線, 2.5Gbps will lost connection
1. upnp, can not forward port 5001
2. inter-vlan routing, 10.255.253.0/24 conflict with 10.0.0.0 / 8
3. 192.168.100.1 do not provide dns service
4. legacy UI vs new UI

-->




<!--

趁著過年, 繼上篇把家裡的 wifi 弄起來之後, 過年期間我把最後一哩路也補上了。總算，從 12 年前初次建置後，這次我終於把累積的幾個需求通通都解決掉了。物理上最麻煩的就是布線了，這次總算在過年前把實體的環境跟設備都準備到位了，過年期間可以好好的把線上的設定跟組態全部搞定，過完年開工就可以正式享用建設的成果了 :D

由於是我自己的施工跟建置紀錄，寫起來有點像流水帳；但是其中有不少我自己搭建 UniFi (非全家筒, 有部分是自行搭配) 採到的地雷，我相信會有很多人有興趣想要參考的。因此我就按照我的需求來逐一說明。如果你碰到的環境跟需求跟我雷同，那就可以點近來參考看看我的作法。

事隔 12 年，我自己在三個月前，期望要解決的問題有這些:

1. 隔離: servers / NAS 要有獨立的網段, 手機 / PC 存取要經過防火牆防護。NAS / 我的 PC 要能支援 LACP
1. 隔離: 不受信任的設備有獨立網段, 要能上網但是不能存取內部網路 (訪客手機, 以及部分需要上網的大陸家電: 小米電扇, 小米掃地機器人... etc)。
1. 隔離: 網路設備完全排除 Made In China, 既有的部分智慧家電則給他 Guest Network 隔離內部網路的存取
1. 統一 WiFi SSID, 兩台 AP 之間可以自動漫遊不用再手動選擇切換。
1. 監控設備網路化 (原本是類比監控攝影機, 需要額外一台 DVR, 線路要透過 cable 同軸電纜, 希望統一改成網路線)。
1. 我個人 PC 要有專屬 port, 能直接存取家中所有的網段, 包含能直接撥接 PPPoE。
1. 集中管理，簡化實體架構 (包含設備跟最少的佈線), 需要建置的管理服務全部往 NAS 集中 (docker, 內建 package 皆可), 設備別讓我再擔心散熱或穩定度問題。

於是，花了三個月，空閒之餘 (平常沒什麼空閒啊啊啊啊) 總算買齊也建置好我理想中的環境了。以下我列出這次從頭到尾我採購的設備清單，如果不想踩雷可以參考我的清單 (除了二手品之外，其他都是含稅開發票, 不含運費):

1. 網路卡: Intel i350-T4 (OEM, 二手), NTD 900
1. 路由器: Ubiquiti EdgeRouter-X SFP (曾經考慮過 USG: UniFi Security Guard, 最後決定的原因後述), NTD 2900
1. 交換器: Netgear GS116E v2 (16 ports, 網管, NTD 3210), Netgear GS108PE v3 (8 ports, 網管, PoE, NTD 3150)
1. 基地台: Ubiquiti UniFi AP AC-Lite x 2, NTD 6600
1. 攝影機: Ubiquiti UniFi UVC-G3 Flex x 2, NTD 5800

相關的既有設備:

1. NAS #1 (Synology DS-918+, 執行 UniFi controller, UniFi video controller, Synology Surveillance Station)
1. NAS #2 (Synology DS-412+, 負責備份)
1. 我的 PC (AMD Ryzen 9 - 3900X, 64GB, Samsung 970Pro 480GB SSD)

其他材料類型的就參考用了，我單純是自己想紀錄而已:

1. 拉線器 (10m)
1. 網路線 (50m) + 水晶頭 (RJ45 x 100)
1. 標籤機: (這是亂入的) 精臣 D11 + 網路標線貼紙 x 2

OK, 專案需求列好了, 設備清單也出來了, 剩下就剩建置系統而已。如果上面有講到你感興趣的細節, 那就往下看吧 :D



# 前言 - 為何不挑選 UniFi 全家筒?

// cost, waiting all in one solution

// 可用性: 希望 router 活著，主要網路都還能正常運作

// 儲存都集中到 NAS
// - syslogd
// - video record
// - redius

// poe

// 手X, 想自己摸索 router, switch, vlan

// next: UDM pro

// https://www.mobile01.com/topicdetail.php?f=110&t=5952455&p=3
// 1. 若一台 NAS 是透過 USG 配發 DHCP，是不是在這台 NAS 的 Docker 上是沒辦法裝 Unifi Controller 去控制 USG 的，因為我可以抓到，但是他會一直斷掉，不能接管

// no qos
// expected IDP

# VLAN 規劃與設定

// vlan: 1,  設備管理網路
// vlan: 10, MODEM
// vlan: 100, NAS
// vlan: 200, Home
// vlan: 201, Guest

// PC settings

// NAS settings (?)




// ref:
// https://blog.router-switch.com/2014/04/network-design-with-examples-core-and-distribution/
// https://www.microsemi.com/applications/communications/enterprise-infrastructure
// https://blog.westmonroepartners.com/a-beginners-guide-to-understanding-the-leaf-spine-network-topology/






// ref:
// https://www.windshow.com/archives/1516

// ref:
// https://medium.com/@nonsingular/unifi-usgpro4-dualwan-%E8%A8%AD%E5%AE%9A%E7%AD%86%E8%A8%98-f707ba54a18f

## 網管設備的管理: SWITCH

// 管理 IP 透過 vlan1 發放

## 網路設備的管理: AP + VLAN

// AP 管理 IP 透過 vlan1 or untagged lan 發放

## 外部存取: L2TP VPN

## PC 端的設定

// pppoe

// intel vlan

// switch config




# AP 設定 (SSID, Guest WiFi without USG)

# CAM 設定 (UniFi Video vs Synology Surveillance)

## 佈線

## UniFi Video / UniFi Protect / Synology Surveillance Station

-->