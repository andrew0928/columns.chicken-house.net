---
layout: post
title: "水電工日誌 #8. 邁向 UniFi 全家餐的升級之路"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "有的沒有的", "敗家"]
published: false
comments: true
redirect_from:
logo: 
---

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

撇開當時其他設備為了搞好 VLAN 花了不少時間之外，沒想到這些需求靠一台 UDMPRO + AP 就搞定了。我目前實體的網路拓樸長這樣 (當時還沒購入 switch, 請先忽略)，我只列出 UniFi 有接管的設備:

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

接下來就是攝影機了。我是先買了兩台 UniFi G3-Flex, 透過 PoE 供電的機種，供電跟連線一次搞定。由於前面的網段早就規劃好，這邊實在沒什麼難度，只是 UDM-PRO 不支援 PoE, 我得另外想辦法就是 (先前我用 ER-X SFP 頂著，後來改用 USW-Enterprise-24PoE)。後來越用越順手，趁著官網短暫的開賣 (一上架就被搶光了) 幸運的搶到兩台 UniFi G3-Instant, 這是透過 USB type-c 供電的機種，連線則是透過 WiFi。普通 USB 變壓器插上去就可以用了，如果你想要不斷電，也不用買 UPS 了，找個行動電源插上去就是個陽春的 UPS 了。不然你買這種電池 + 變壓器二合一的也可以，短暫斷電 (只要你的 WiFi 跟主機也有 UPS) 就不會影響運作了。

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

有了可靠的基礎建設，就像一個城市的道路交通跟衛生下水道等等都完善後，就可以在上面做各種服務建設了，例如公園，醫院，活動中心等等。我當時的想法也一樣，我自己擅長的是雲端服務開發跟規劃啊，自己家裡沒有對應的配置怎麼說得過去? 雖然我一直有在 NAS 上架設一些自己用的小服務，不過從 DS412+ 換到 DS918+ (當時也是想很久然後碰到特價活動)，總覺得缺了點什麼...

兩個原因，一個是 Synology 給的硬體實在太保守了。當 NAS 的話網路速度都卡在 1G, 即使 plus 系列通常都有 2 ~ 4 ports, 不過 1G 給我那麼多個也沒用啊，即使 LACP 啟用了，我自己 PC 單機的連線速度還是受限。1G 的頻寬很容易就到頂了，現在的 HDD 隨便都能突破，至少到 2.5G 比較合理一點。無奈 S 牌 NAS 沒這選項，要嘛就 1G, 要嘛你要往上跳一大級，挑選有 PCIe 擴充槽的機種，然後自己加購 10G 網路卡...

另一個是運算能力。NAS 主要任務是處理 I/O, 通常 CPU 都給得剛剛好而已，要拿來當運算服務，即使是 DS918+ 也不大夠用，CPU 跟 RAM 都有類似的困境。我想跑 VM 或是跑大型一點的 container 就卡住了啊...

因為有這些念頭，在 2021/01 我的 DS412+ 服役八年多之後不幸 (該說不幸嗎? @@) 在某次關機後就再也開不了機了，我就把 DS918+ 退居二線擔任備份用的 NAS，這次就直接添購一次到位的機種 DS1821+, 並且一次把 ECC RAM 加滿到 32GB, 上線當作主力機來使用。


## 網路服務環境準備

有了足夠的運算能力，我開始在上面架設我理想中的服務了。這邊我要大推一下 Synology DSM, 有很多實用的小設計，非常適合像我這種個人使用的環境。我雖然知道怎麼善用 public cloud, 善用 container / kubernetes 等等大型服務的基礎建設, 不過自己在家裡搞這些太超過了啊, 家用我只要有基本的穩定度就夠了, 其他則是省事經濟一點為優先。因此就不考慮 azure / aws 之類的服務了, 也暫時不考慮 kubernetes 這種架構了，簡單的 docker, 頂多用到 docker-compose 就夠, 其他盡量用現成的。

Synology DSM 在這需求上，幫了我很大的忙。除了 NAS 本身就最擅長的磁碟管理跟備份服務 (我完全不用擔心這些服務的資料是否夠安全，我只要 mount 到可靠的 volume, 同時有做好備份就夠了, 不用額外花心思去顧慮資料的可靠度)，我就挑幾個我最推薦的功能來介紹就好。

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

之後你就可以隨意地在你家內部，用 https://myservice.domain.com 使用你自己架設的服務了。你可以任意選用你喜歡的 domain name (免費), 你也不用擔心瀏覽器會警告網站不安全，只要你有替她綁定 SSL 憑證 (免費，自動 RENEW)。這些服務大部分都在 docker hub 上垂手可得，只要幾行指令就能裝好 (免費)


## 網路服務

這些東西上手後，你開始要擔心的是不自覺就架設太多服務了 XDD

1. Home Assistant
1. BitWarden Server
1. iperf3

1. photo
1. video
1. music

1. Legacy ASP.NET support (mono)
1. Legacy Windows Service (virtual machine)



## 連線速度




<span id="step3">

# 第三部, Link Speed Upgrade










<!-- more -->

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














<!-- more -->

<!--

0. udm-pro cross vlan routing with IDS enable -> low performance ( only 850Mbps )
0. use 扁線, 2.5Gbps will lost connection
1. upnp, can not forward port 5001
2. inter-vlan routing, 10.255.253.0/24 conflict with 10.0.0.0 / 8
3. 192.168.100.1 do not provide dns service
4. legacy UI vs new UI

-->






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


<!--more-->

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