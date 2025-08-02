---
layout: post
title: "Docker 初體驗 - Synology DSM 上面架設 WordPress / Redmine / Reverse Proxy"
categories:

tags: ["Docker","Tips","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2015/10/13/docker-初體驗-synology-dsm-上面架設-wordpress-redmine-reverse-proxy/
wordpress_postid: 339
---

[![img_56358907f0c81](/wp-content/uploads/2015/11/img_56358907f0c81.png)](/wp-content/uploads/2015/11/img_56358907f0c81.png)

前言: 先讓我講一點前情提要 XD，想看安裝步驟的請自己跳到後面...

在買這台 NAS 之前 (Synology DS-412+), 我是自己在家裡弄了台 PC, 裝了一堆硬碟充當個人用 file server, 同時順便在裡面架了自己常用的網站，包含這部落格的前身 (BlogEngine)，還有自己用的 Visual SVN, 另外也架了 Linux VM 裝 Redmine 等等其他的東西..

後來 PC 開始不聽話了，開始三不五時當機，心一橫，兩年多前就買了台 4Bays NAS 把 Server 換掉，頓時輕鬆許多... 只是 NAS 不比 Server, 慣用 Windows Server 的我一時找不到替代品，這些服務就一個一個搬家了。其中最重要的 BLOG，就搬到 GoDaddy 的免費 web hosting (有 IIS)，繼續在上面掛著..

用過 Synology NAS 的大概都知道，它的特色就是 DSM 很好用，也有提供很多 Package, 讓 NAS 加裝軟體就像手機逛 App Store 一樣簡單... 不過，DSM 的裝機量不比手機，很多套件要是沒有經過 Synology 包裝，要安裝就是件麻煩事了。就算有 Synology 官方的打包套件，更新或是維護也不比這些軟體的官方來的快。尤其是從小到大都是抱著 Microsoft 大腿的我更是不適應 @@

直到幾個月前 Synology Release DSM 5.2, [正式在裡面搭載了 Docker](https://www.synology.com/zh-tw/dsm/app_packages/Docker)! 這真是天大的好消息..  :D

Docker 是個好物，沒用過或沒聽過的可以參考這裡:  [What is docker ?](https://www.docker.com/whatisdocker)

簡單的說，是另一種虛擬化的應用。他不像 VM 是將硬體虛擬化，所以不用在上面安裝 OS，只虛擬化執行環境... 啟動速度很快，兩三秒就可以啟動了，少掉 OS 這層，整個就很輕量化，架在 Docker 裡，跟原生地執行環境速度，CPU / RAM 資源的使用沒甚麼明顯差別...  我覺得 DSM 加入 Docker 真的是 Synology 最聰明的決定了，比 Q 牌直接導入正統的虛擬化技術還實用... 畢竟個人用的 NAS 都不會有太強大的運算資源，為了這樣去拚硬體配備就有點本末倒置了。Docker 這種輕量化的虛擬化技術，正好補足了這需求

講這麼多幹嘛? 因為 Docker 實在太熱門了，所以在 [Docker Hub](https://hub.docker.com/) 上大概所有熱門的應用都有人包好了，煩惱的是同樣的東西太多人包了，有時還真不知該怎麼選 @@.. 我是有官方版的就盡量挑官方的來用。因為社群的差異太大了，因此從 Docker 上可以找到的選擇，遠比從 Synology Package Center 找到的又多又廣泛，我就開始一個一個替換的計畫...

計畫要安裝的有好幾個，包括 WordPress, Redmine, MYSQL, WebSVN, 還有為了方便發布這些服務，還想裝個 Reverse Proxy... 不過流水帳我就省了，這次的範例我就拿 WordPress 跟 Reverse Proxy 當案例，給有需要的人參考步驟就好。

---

正文開始

這次打算把在 GoDaddy 流浪兩年多的 Blog Engine 搬回家，於是花了點時間把資料從 BlogEngine 匯出，轉到 WordPress, 這邊很多文章有教你一步一步處理，我就跳過了。

在 Docker 上安裝 WordPress + MySQL, 也是小事一件，最花時間的就是... 就是下載 image ... 這我也跳過。比較特別的是，不知是 Synology 搭配的 Docker 套件問題，還是別的的問題 @@，WordPress 官方版的 image 開 DSM Docker 管理員的 terminal 就很容易會整個 container crash .. @@，不過因禍得福，意外發現有人用 Nginx 這個新興的 web server 架設的 WP image.

[NGINX](http://nginx.org/en/) 是啥? 是個俄國人寫的 web server, 世界上的佔有率大概 1x % 吧~ 它的特色就是又小又快..  Apache 走的是可以外掛很多 module 的模式，NGINX 則是走把你要的東西編譯進去的模式，跑起來又快又省記憶體，正適合我的需要。換了這個 image, 前面講的 crash 怪問題就不藥而癒.. 算是因禍得福 :D

做個筆記，我用的 image 分別是這兩個:

[wordpress image with php-fpm + nginx](https://registry.hub.docker.com/u/amontaigu/wordpress/)

[mysql offical image](https://hub.docker.com/_/mysql/)

架好後當然快樂的使用了。這時問題開始來了... 畢竟我用的是 NAS 內建的套件，我又不熟 Linux, 有很多東西就算我找到文章可以進去大改特改，我也不大敢動手，NAS 終究是拿來讓我日子過快樂一點的，不是要重回當黑手的日子... 因此太過古怪的技巧我就不想用了，我想盡量用正常一點的方式來設定，免得以後換個版本我就搞不定...

[![NETWORK](/wp-content/uploads/2015/10/NETWORK.png)](/wp-content/uploads/2015/10/NETWORK.png)

上圖是我現在家裡的網路架構，這時碰到的問題在於，PORT 80 早就被 NAS 內建的 apache 搶去用了。WordPress 若要用 80 PORT 就沒辦法了。DSM 也沒地方讓你把 PORT 80 放出來，二來就算放出來，我也沒辦法讓兩個以上的 container 都 mapping 到 80 PORT... 這樣要開放對外網站就顯得很棘手... 最終 WordPress 分配給他 8012 這個 port, 總不能叫所有的網友，以後要看我的文章要連這 PORT 吧? @@

一般業界最常處理這種問題的方式，就是用 [Reverse Proxy](https://en.wikipedia.org/wiki/Reverse_proxy) 了。顧名思義，Reverse Proxy 就是反向的 Proxy, 他是替 "外面" 的 User 到你家裏面的網站抓資料後，再丟給外面的 User, 用這樣的技巧將內部的網站發布出去。其實他的機制跟一般的 Web Proxy 是一模一樣的，只不過他服務的是外面的 User 抓內部的網站，跟正常的應用情境相反，所以叫 Reverse Proxy.

Reverse Proxy 其實很多種應用，進階一點的 Load Balancer, Cache, HTTPS 發行 (在 Reverse Proxy 上加掛 SSL) 等等用途。在 Windows Server 上有 [ARR](http://www.iis.net/downloads/microsoft/application-request-routing) (Application Request Routing) 這個 IIS 外掛可以用，也是另一種常用的 Reverse Proxy。回到我的狀況，由於唯一的 80 PORT 已經被 DSM 佔住了，所以沒得選擇，我開始尋找 DSM 內建的 Apache 上可以加掛的 proxy module... 結果得來完全不費工夫，內建就有 :D

架構跟方向都想好之後，就開始動手了... 各位現在看的到我翻新的 BLOG，可見是成功了! 以下是我的操作步驟:

1. Synology DSM 的控制台，底下有 Web Station, 先用正常的介面，建立 virtual host, 綁到 columns.chicken-house.net 這個 hostname (80)

   [![01](/wp-content/uploads/2015/10/01.png)](/wp-content/uploads/2015/10/01.png)

   當然，其他 DNS 的設定你要自己搞定。我自己家裡用的 ROUTER 有內建個小型 DNS，加個 static record 就可以把 columns.chicken-house.net 對應到 NAS 的內部 IP，我自己要看我的 BLOG 不用繞到外面出國比賽再繞回來... 外面的 DNS 也要改一改，對到 router 的對外 IP，有固定 IP 的可以設 A record, 有 DDNS 的可以用 cname record. 改完可以測看看，這時應該會看到 Synology 自己準備的 404 page:
   
   [![02](/wp-content/uploads/2015/10/02.png)](/wp-content/uploads/2015/10/02.png)

2. 接下來，就是要設定這個 virtual host 要扮演 reverse proxy, 轉向內部的 word press 網站了。其實整篇廢話這麼多，重點就這一段而已 @@用 SSH 登入 NAS，修改這個檔案: /etc/httpd/httpd-vhost.conf-user , 其中 line 15 ~ 25, 就是我加進去的指令，告訴 apache 在這個 virtual host 內，位於 / 以下的 http request, 都轉給 http://nas:8012 這個內部的 URL，也就是安裝 WordPress 的 container 的發行端點

   ```sh
   NameVirtualHost *:80
   <VirtualHost *:80>
   ServerName *
   DocumentRoot /var/services/web
   </VirtualHost>

   <VirtualHost *:80>

   ServerName columns.chicken-house.net
   DocumentRoot "/var/services/web/columns"
   ErrorDocument 403 "/webdefault/error.html"
   ErrorDocument 404 "/webdefault/error.html"
   ErrorDocument 500 "/webdefault/error.html"

     # start of (reverse proxy settings)
     ProxyPreserveHost On
     ProxyRequests     Off

     <Location / >
       ProxyPass http://nas:8012/
       ProxyPassReverse http://columns.chicken-house.net/
       Order allow,deny
       Allow from all
     </Location>
     # end of (reverse proxy settings)

   </VirtualHost>
   ```

   完成後，用這個指令 restart apache (httpd), 讓設定生效:

   ```
   httpd -k restart
   ```

   再用瀏覽器測試一下網址  http://columns.chicken-house.net, 應該就可以看到 wordpress 的內容了 !

   拿手機測試一下，關掉 wifi, 用 4G 連看看我自己的網站... 果然可以用正常的 URL 看到內容:
   
   ![wp_ss_20151012_0002](/wp-content/uploads/2015/10/wp_ss_20151012_0002.png)

3. 其實到這邊就大功告成了。不過... 請務必備份這個檔案 !!  DSM 的介面設計得太簡單好用了，所以當你回到 (1) 重新調整後，或是有第二個 docker container 也要依樣畫葫蘆發布的話，DSM 會把這個設定擋蓋掉 T_T，我就是因為這樣全部重來一次...

OK，大功告成! 繞了一大圈，總算把我的 NAS 調教成可以擔負重要任務的 Personal Server 了，以前不覺得 NAS 跑的慢，現在開始覺得 RAM 好像值得加大一點了 :D，也許有人會問，這樣其實用 Synology 套件中心的 WordPress 好像也一樣不是嗎? 不不不，處女座的人是忍受不了這幾個問題的:

1. 套件中心的 WordPress, 網址會多一段... 像這樣... _http://columns.chicken-house.net/**wordpress**/......_ 這我看了就很礙眼，更重要的是其他人透過 search engine 找到的連結，會點不進來... 身為點閱率破百萬的知名部落格 (並沒有) 怎麼能忍受這種現象...

2. 套件中心的 WordPress 只能裝 "一份"，我想架兩個 wordpress 就沒辦法分開管理了

3. docker 將來要搬出去非常容易，匯出 container, 之後搬到別的地方，如 Azure / Amazon 都有提供 docker 執行環境了... synology 的套件就沒這優勢了...

4. docker 的選擇多太多了，到 docker hub 裡找找，甚麼都有... 能選擇的數量遠遠高於 synology package center

5. 有統一的 container 管理工具，mount storage, port mapping, cpu / ram resource management 等等都有現成的, 套件中心提供的就沒這樣的管理彈性:

   [![03](/wp-content/uploads/2015/10/03.png)](/wp-content/uploads/2015/10/03.png)

好，流水帳就記到這裡，當你還想再加上其他 container, 就依樣畫葫蘆就好。這篇其實沒甚麼重點，主要就是為了滿足 Synology NAS 用戶，能用 Docker 套件來做些正是用途的小技巧而已，歡迎分享 :D
