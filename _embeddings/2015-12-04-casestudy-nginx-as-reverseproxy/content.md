---
layout: post
title: "CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)"
categories:

tags: ["BlogEngine.NET","Docker","Tips"]
published: true
comments: true
permalink: "/2015/12/03/casestudy-nginx-as-reverseproxy/"
redirect_from:
wordpress_postid: 543
---
網站架構調整後有感: 要學習另一個陣營的技術，還真是條不歸路，越挖越覺得要摸索的東西越多 @@ 照例前面先來點碎碎念，正題後面再來。這年頭，大型的佈署是少不了 Linux + OpenSource Solution 的，再加上我吃飯的傢伙 ASP.NET 的下一版 (vNext, .NET Core) 也要正式跨各種平台了，不熟悉一下 Linux 以後怎麼會有能力把寫出來的 code 搬到 Linux 上面執行? 不過，要跨到完全另一個生態體系的環境，還真要下點決心才跨得過去... 所幸，我挑對了切入點 (把自己的 BLOG 從 BlogEngine 轉移到 WordPress, 架設在 NAS + DOCKER 環境)，這幾個月下來，也算累積了不少的心得 :D 要在 Linux 的世界裡打滾，最痛苦的就是安裝各種軟體了，只能說那真是地獄... @@，尤其是對於不熟 Linux 的人來說更是如此。現在有各種套件安裝的工具，向是 APT-GET 之類的，其實已經簡化很多了，但是難的在後頭，各種的 configuration 都要自己編 conf 檔，而每套系統用的語法都不一樣... 我不論是在 Coding 或是 System Admin 時，都很講究系統架構。因此往往預設的安裝我都不滿意，我都會想盡辦法用最基礎的模組，搭建出我認為最理想最適合的架構。很多組態都必須自己研究摸索，都需要碰到進階的安裝設定，這也是要開始認真用 Linux 的我最大的障礙... 然而我的目的不是要熟悉這些 configuration 啊，我目的是架設出期望的系統，來解決後續的問題，這些繁瑣的安裝設定機制 (除非必要，像是這篇要講的 Rewrite ) 就能省則省... 所幸 Docker 的出現，正好給了我這種人一個機會，我只要搞定最基本的 Docker 執行環境，其他安裝就簡單了，找到正確的 container image 就一切搞定。加上我用的 NAS 內建 Docker 的支援，連 Linux + Docker 架設都免了... 至於為何要這麼大費周章的熟悉 Linux ? 轉貼一則最近看到的新聞... 連 Microsoft CEO Satya Nadella 都公開表示 "Linux is Best for Cloud" 了，多年的 Microsoft 信徒軟絲當然要花時間去研究一下.. XD

# ![](/wp-content/uploads/2015/11/microsoft_loves_linux-300x199.jpg)  
[Microsoft Agrees Linux is Best for Cloud](http://technochords.com/microsoft-agrees-linux-is-best-for-cloud/)

Ever since the new CEO, Satya Nadella, has taken the place of the Linux-hater Steve Balmer, the change in Microsoft’s rhetoric regarding Linux has been clear.<span id="more-833"></span> Now, Microsoft is officially recommending Linux on Twitter.

* * *

  好，看到分隔線，就代表正題開始! 前面幾篇有跟到的讀者們，應該都知道我之前在研究甚麼.. 為了在我能力範圍內用最快的方式搭建能夠執行 .NET Core 的 Linux 環境，我選用了 
[Synology NAS + Docker](/2015/10/13/docker-%e5%88%9d%e9%ab%94%e9%a9%97-synology-dsm-%e4%b8%8a%e9%9d%a2%e6%9e%b6%e8%a8%ad-wordpress-redmine-reverse-proxy/) 
來踏出第一步. 為了快速熟悉各種實作技巧，我把自己的 BLOG 從原本的 BlogEngine ( ASP.NET ) 轉移到 WordPress (現在還是 PHP, 以後要變成 Node.js 了)。前兩篇說明了用 Apache 做前端的 Reverse Proxy, 同時也為了
[新舊系統的文章轉址，用 Apache 的 RewriteMap 解決 400 篇文章 x 6 種網址格式，多達 2400 種組合的新舊網址轉址](/2015/11/06/apache-rewritemap-urlmapping-case-study/)。
就當越用越熟練之際，我擔心的問題來了! NAS 再好用，他終究不是正規的 SERVER ... NAS 的硬體都不怎麼樣，我的 Synology 412+ (Atom 2701D + 2GB RAM) 很快地就碰到瓶頸了，多開兩個 container 就明顯
的感覺的到回應變慢了... 於是我決定開始把我的 BLOG 系統轉移到 Ubuntu Server 上，用專屬的硬體來架設 (NB)。架設的硬體其實也很巧，是我老姊請我幫她處理掉的舊 NB。拿舊的 NB 其實很適合，一來省電，二來 Linux 省資源，
跑 Windows 跑不動，換成裝 Linux 跑個人 BLOG 其實還綽綽有餘，三來 NB 內建的電池正好當成 UPS，也省了一筆開銷... 。接手的 NB 硬體只是貧弱的 Intel Pentium P6100 + 4GB RAM，不過不管在運算能力或是 RAM 都遠比
我現在的 NAS 強... 於是架好 
[Ubuntu Server + Docker 後](/2015/10/24/%e7%b5%82%e6%96%bc%e6%90%9e%e5%ae%9a-ubuntu-server-15-10/)就開始動手了

![](http://columns.chicken-house.net/wp-content/uploads/2015/12/img_5660723bd1e09.png)

先來看看這次我想調整的架構圖。第一張圖是現有的架構，就是[兩個月前剛轉移 BLOG](http://columns.chicken-house.net/2015/10/13/docker-%e5%88%9d%e9%ab%94%e9%a9%97-synology-dsm-%e4%b8%8a%e9%9d%a2%e6%9e%b6%e8%a8%ad-wordpress-redmine-reverse-proxy/) 用的架構: [![NETWORK](/wp-content/uploads/2015/10/NETWORK.png)](/wp-content/uploads/2015/10/NETWORK.png) 第二張是我想調整的新架構，也就是這次要做的:

![](http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56608a1da440e.png)

這次的調整，我決定沿用之前的架構，就是前端用 Reverse Proxy 來發布藏在後面的 WEB application, 因為後面有好幾個 Docker Container 需要同時用一個 IP + 80 port 發布，這層是跑不掉的。加上大量舊網址轉址的需求，我不想把這個複雜度加在 WordPress 上面，所以這需求就落在 Reverse Proxy 身上。原先的架構中，Reverse Proxy 是用 Apache Httpd 來負責 (因為 NAS 內建 apache httpd, 而且已經把 port 80 佔住了，沒辦法換掉)，現在自己架設 Ubuntu Server 就沒有這些限制，我當然就改用現在當紅的 NGINX 來代替。 既然都用 Docker 了，其實找到正確的套件，設定一下就搞定，單純系統安裝的部分我就跳過去了。架構上調整的兩個較大的工程我補充一下:

1.  前端 Reverse Proxy 的部分，改用 Nginx 。這邊面臨的是上一篇文章說明的轉址技巧，還有對照表的部分必須重新來過，改用 nginx 的 conf 重新設定一次。
2.  原本架構只用了兩個 container, 分別負責 WEB 及 DB，資料檔案是直接掛上 local server 的目錄。這次則按照 Docker 官方建議，建立了專門管理資料用的 [VOLUME-CONTAINER](https://docs.docker.com/engine/userguide/dockervolumes/)。

調整後的架構跟效能，應該都會遠比原本的好。直到現在用了 Docker, 才開始對當年學 [UML 的 deployemnt diagram](https://en.wikipedia.org/wiki/Deployment_diagram) 有感覺... 後來 Visual Studio Team Suite 也出現過這個功能，可以繪製 deploy diagram (強的是還能跟你實際的 code 雙向同步)。但是當年的實作上，總覺得實際要處理的問題遠比 diagram 要複雜得多，系統架設跟UML表達的架構，中間距離還很遠，往往高階架構都只在架構師腦袋裡，真正執行的工程師則被一堆設定的細節給淹沒了，直到現在有了 container 技術，才開始覺得佈署系統就真的跟 deployment diagram 上講的是同一件事，真的就是把元件拉出來，按照設計圖一個一個擺到定位，線接一接就完成了。 Volume-Container 的應用，有機會再另外寫一篇吧，先來看看 NGINX Reverse Proxy 的部分: 在[上一篇](http://columns.chicken-house.net/2015/11/06/apache-rewritemap-urlmapping-case-study/)在解決新舊系統網址對應最主要的技巧，就是如何簡潔又有效率地做好 2400 條轉址的需求。主要就是用 Apache 的 RewriteMap 來兼顧 Rule 的撰寫及對照表的維護。而同樣的機制，在 nginx 上也有，不過語法不大一樣，我先貼一段 example:

```yml
# map blogengine with slug (encodded title) format
if ($uri ~* "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*).aspx$") {
    set $slug $5;
    return 301 /?p=$slugwpid;
}
```

Nginx 的 Map 簡潔到不能再簡潔了，加上他用的 C Like 設定擋語法，老是讓我有個錯覺，覺得我在寫得是 script 而不是在寫設定擋...
然而簡潔到極致的 Map 用法，我看了半天才看出他的端倪...   上面這幾行，背後有條看不見的線，把 $slug 跟 $slugwpid 這兩個變數串起來...
當我把某個數值 assign 給 ```$slug``` 時，Map 的機制就會偷偷的啟動，用 ```$slug``` 的值去查表，把查到的結果放到 ```$slugwpid```, 然後接著 run 後面
的 script / config. 上面這幾行，意思就是每個 request, 會把他的 URI 部分 (不含 hostname) 抓出來，用後面的 regular express 比對，
抓出第五個 ```match ($5)``` 的內容，指定到 ```$slug``` 這個變數內。接著透過 MAP 的機制，下一段指令 ```return 301 /?p=$slugwpid;``` 就是
用 HTTP 301 的方式轉址，轉到 ```/?p=xxxx``` 這樣的網址。 這看不到的機制，靠的就是整個 nginx 設定擋的另一個部分定義 MAP 的效果:

```yml
    map $slug $slugwpid {
        include maps/slugmap.txt;
        * 0;
    }
```
Map 這精巧的機制想通後就很簡單了，Map 的宣告後面直接接兩個變數，一個是原變數 ($slug), 另一個是查表後對照的結果變數 ($slugwpid)。你在任何地方把數值指定給 $slug 的話，同時間另一個變數 $slugwpid 的值就會被替換掉。 說穿了不值錢，這些可是我研究了好一陣子才搞懂的。研究的過程中我也去找了 NGINX for Win32, 這樣測是起來比較方便，有需要快速體驗或測試 nginx 的朋友可以參考。用這個來研究設定擋的寫法，可以省掉很多時間 (畢竟我還是 windows 操作比較熟悉...) 最後就是對照表的定義了。NGINX 的設定蠻有彈性的，如果你的對照表不多，可以直接寫再 CONF 裡面就好。不過我的狀況有四百多篇文章，我選擇放到外部檔案再引用。我貼片段的對照表內容出來:

```yml
GoodProgrammer1 65; # 2008/09/27, 該如何學好 "寫程式" ??
IBM-ThinkPad-X111- 252; # 2005/06/28, IBM ThinkPad X111 ...
e6b0b4e99bbbe5b7a5e697a5e8aa8c-1-Cable-TV-e99da2e69dbf 146; # 2007/09/12, 水電工日誌 1\. Cable TV 面板
e5a682e4bd95e59ca8e59fb7e8a18ce6aa94-(NET)-e8a3a1e99984e58aa0e9a18de5a496e79a84e8b387e69699 180; # 2007/02/28, 如何在執行檔 (.NET) 裡附加額外的資料?
X31-2b-e99b99e89ea2e5b995e79a84e68c91e688b0-_ 273; # 2005/03/06, X31 + 雙螢幕的挑戰 @_@
e588a9e794a8-NUnitLite2c-e59ca8-App_Code-e4b88be5afabe596aee58583e6b8ace8a9a6 215; # 2006/10/29, 利用 NUnitLite, 在 App_Code 下寫單元測試
```

格是很簡單，就是新舊對照的值，一筆一行。兩個字串用空格隔開，最後用 ; 結尾。如果有需要的話， # 之後的字串會被當成註解忽略掉，就像上面這樣。還好這格式跟之前 Apache 用的 RewriteMap TXT 格是很類似，我用文字編輯器簡單替換一下其實就搞定了 看了 NGINX 官網的說明，他的 MAP 彈性大很多，除了靜態的字串對應 ( key / value pair ) 之外，可以包含萬用字元，也可以包含 Regular Express, 也就是說他也包含某些運算能力在 Map 裡。我擔心的是這麼一來 MAP 也許就無法像 Apache 一樣，把 Map 編譯成二進位的 Hash table 格式，大量查表的效能也許會受影響... 這邊我就沒有像上次一樣查 benchmark 了，不過新環境運算能力本來就強很多了，同時 nginx 本身效能也比 apache 強的多，加上我的舊文章數量又是固定的 (400)，數量還不算太大，也不會再繼續成長下去，測試過沒有明顯的影響，我就暫時不理它了 XD 好! 寫到這邊，其實搬家動作大概就告一段落。雖然如此，也是花掉我幾個下班休息時間才搞定的... 我想應該很多人跟我一樣，想從熟 Microsoft 領域，跨越到 Linux / Open Source 的領域而不得其門而入的困境吧? 我這系列文章都會用實際的案例，說明我 "為什麼" 會這樣做，而不是只有單純的 step by step. 畢竟比我熟這些操作的人太多了，人外有人.. 這應該輪步道我來寫。而我真正想分享的，是這些架構規劃面的經驗。希望我這些實作的案例 & 紀錄，可以幫到跟我一樣從 Microsoft Solution 要跨越到 Linux 這邊的人  :)