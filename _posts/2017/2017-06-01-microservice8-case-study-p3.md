---
layout: post
title: "架構師觀點 - 轉移到微服務架構的經驗分享 (Part 3)"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/05/
---

前面兩篇，分別介紹了微服務架構的規劃方向，還有實際切割的案例探討。這篇 (Part 3) 的重點就要擺在微服務到底該在甚麼樣的基礎建設上面
運行? 維運過去單體式架構的 application, 所需要的基礎建設，會跟微服務架構下可能會有數十個 service instances 同時執行，甚至上百個
service instances 一樣嗎?

我只能說，考量完全不一樣!! 微服務架構簡化了服務本身的複雜度 (每個服務變小了，責任也變單一)，但是整體的 application 並沒有變簡單啊，
因此複雜度都轉移到服務與服務之間。因此要能妥善管理及維護好眾多的服務 instances 能彼此順利的合作，是個不小的挑戰。這邊最主要的關鍵，
就在於底層的基礎建設了! 這篇就花點篇幅來聊聊這個部分: 微服務架構的基礎建設與部署。

<!--more-->

{% include series-2016-microservice.md %}


--

# 微服務需要那些基礎建設?

由於微服務架構下，服務與服務之間的關係變複雜了，基礎建設要解決的問題也跟著複雜。基礎建設的優劣，直接影響到整個系統的運作。
很多人認為，新創的公司或是新創的團隊，直接導入微服務就好了啊! 其實這不見得是最好的方式。想要一次到位的話，規模不夠大
可能還支撐不起這樣的基礎建設的維運；你的系統可能也還沒有大到需要靠微服務架構來支撐。我認為比較好的方式是漸進式，先從單體式架構
開始，但是要不斷地重構，隨時維持軟體本身的架構是優良的，隨時做好下一步切割為微服務的準備；在成長面臨瓶頸時，逐步的切割擴大，
自然而然的就會演變成微服務架構了，這時就是同步擴充基礎建設的好時機。

很多文章都在教你怎麼開發微服務的系統 (包括我)，但是卻很少人把黑暗面講出來，微服務的好處是要靠一個良好的基礎建設，讓微服務
可以在上面妥善的運行，才堆積出來的。這些基礎建設還沒準備好之前，微服務是沒有效益的。這篇文章就很露骨的點出關鍵:

[夠了，不要一上來就把微服務說的神乎其神](https://tw.wxwenku.com/d/100702684)

> **我們為微服務做好準備了嗎？**
> 我敢說，大部分成長型初創公司幾乎連一個先決條件都無法滿足，更不用說滿足所有的條件了。如果你的技術團隊不具備快速配置、部署和
> 監控能力，那麼在遷移到微服務前必須先獲得這些能力。

先決條件我認為有兩大類，一個是你團隊的流程能否應付微服務架構下的複雜度? (你可能有好幾個服務要維護)。這時 DevOps 的相關流程
是個關鍵。另一個是你的系統架構、環境配置與維運流程，這是考驗你的微服務運作環境是否可靠的關鍵。

因此，若你身為架構師或是 CTO，必須替團隊做好長遠規劃時，了解將來需要什麼樣的基礎建設是必要的。這篇文章就來聊聊這個部分~
我先直接排除所有系統都需要的共通設備 (如防火牆，Load Balancer 這類的)，就針對微服務必備的基礎設施:

* API Gateway
* Service Discovery
* Communication & Event-Driven System
> orchestration vs choreography, sync vs async, event-driven
* Log

![](/wp-content/uploads/2017/06/2017-06-18-01-41-32.png)

簡單的話張圖，順序我就由外到內來談吧。這幾個部分，可以說是微服務架構必備的基礎了，就像人體的重要器官一樣，各有各的功能，只要
其中一個環節運作不正常，就會受到影響。

(微)服務對外提供的主要是服務的 API，負責管控對外的 API 關卡，就是 API Gateway, 你可以把它想像成類似 WAF (**W**eb **A**pplication **F**irewall) 一類的東西，只是他專門處理 API 而已。對外的管控不外乎安全、認證、快取。比較特別的是有些
狀況也會做 API 的聚合 (aggration)。

微服務架構的內部，可能會有數十個到數萬個不等的 instance 在運行，有效掌握這些服務的狀態也是很重要的。這些資訊會運用在 API Gateway
該將服務轉送到哪裡的機制 (例如: 查詢某服務有哪些節點可用? 轉送到負載最輕的 node, 避開掛掉的節點... 等等)。為了做到這些，就需要有
Service Discovery 的機制，讓每個服務啟動時能夠去註冊，停機時能夠去取消註冊，或是有定期回報 (heartbeat) 的機制，讓 service discovery 能判定那些 nodes 已經失聯了。同時，更進一步的 configuration management, 也有的系統是安排服務註冊時，同時也把相關的
組態取回，這時 service discovery 同時也做好了組態的管理。基本的需求下，其實 DNS 已經足以滿足這需求，例如 DDNS register / unregister, DNS round robin, DNS srv / txt records 等等, 都能協助你解決這些問題。

再來是訊息的溝通。過去單體式架構下，模組跟模組之間的通訊，就是很單純的 LPC (Local Procedure Call) 本地端呼叫而已。就 C# 來說，
Microsoft 提供了各種呼叫方式讓你運用 (例如: direct call, reflection, async call, event handler, delegate / callback ...)。
但是轉換到微服務的場景，除了典型的 RPC 之外，如何達到上述其他各種不同的呼叫情境? 一套良好的 message queue / message bus 系統
能很有效的搞定這件事。從最基本的 message publish / receive 之外，routing, pub / sub 模式, RPC, 甚至更進階的 event, 
scheduled message 等都能讓你把這些複雜問題從你的 code 裡面切出來。

這時一套妥善的 message queue 就派上用場了。靈活的 message routing 與配置的機制就變得很重要。既然服務本身都只想專心專注一件事，
服務本身都要解耦合，那麼服務與服務之間的複雜關係，之間的訊息該怎麼流向目的地，就是 message queue 的責任範圍了。挑選一套好的
message queue, 你可以把訊息傳遞的複雜度從程式碼切出來，方便維護與管理。

最後是日誌的追查與管理。日誌可不是像流水帳一樣，記下來就結束了 (雖然大部分人都這樣看待 log)。微服務架構的一大罩門，就是一件事情
需要由多個服務共同合作 (呼叫 API 或是傳遞 Message) 才能完成。這時一但某個環節出了問題，你想要靠 log 回頭追查就變得非常困難了。
log 的目的不只是記下來而已，更重要的是在問題發生的當下，能夠很快地還原你想了解的狀況。因此能否針對某個 "事件"，把所有散在多個服務
的 log 集中起來，像貨運的 tracking number 一樣，能讓使用者在多個轉送站之間明確地看到貨物的運送狀況，這就是我要講的 log 基礎建設。


----

以上這些就是導入微服務架構前，我認為應該要先評估好的基礎環境建設必要的幾個項目。
在逐一深入介紹之前，我先大力推薦這本 Nginx 的電子書給大家看:

![](/wp-content/uploads/2017/06/2017-06-06-02-07-00.png)
[Microservices: From Design to Deployment, a Free Ebook from NGINX](https://www.nginx.com/blog/microservices-from-design-to-deployment-ebook-nginx/)

會推薦這本電子書的的原因，主要是它的內容長度，內容深度跟講解的複雜度，都拿捏得剛剛好。沒有深入到太多實作細節，也沒有
淺顯到空談一堆你看完還是不知道怎麼做，更重要的是份量也剛好，只有 70 頁，薄薄的一本 (咦? 電子書有厚度嗎?) 不需要花很多
時間就能看完。這 ebook 介紹了微服務系統中幾個關鍵的基礎建設，以及為何需要它的原因，推薦大家都先去看一下這本書的內容。

想看網頁版也有.. 當初還沒出電子書時，我就是看網頁版連載的文章:
[Introduction to Microservices](https://www.nginx.com/blog/introduction-to-microservices/)

----

以下我就截錄 NGINX 這系列文章的內容，來說明一下這幾個基礎的服務能做些什麼:


## API Gateway

不論你的服務是單體式架構 (Monolitch)，服務導向 (SOA)，還是微服務 (Microservice), 最終終究是要開放 API 給別人使用的。
這時最基本的防火牆 (Firewall), 反向代理 (Reverse Proxy), 以及負載平衡 (Load Balancer) 等等我就略過不談了。我們先來談談
API 特有的對外關卡: API Gateway

![](/wp-content/uploads/2017/06/2017-06-07-00-50-18.png)

先來看看實際的使用情境: 假設 Amazon 網站已經微服務化了 (實際上也真的是沒錯)，來想像一下這個 APP 為了實現畫面上的所有功能，
進入這個購物 APP 首頁時，究竟要從後端呼叫多少微服務的 API 才能湊齊這個畫面所需的所有資訊?

按照圖上的標號，分別有:

1. 訂購紀錄: 要從訂購管理的服務 API 取得
1. 商品評價: 評價系統 API
1. 商品資訊: 商品上架管理系統 API
1. 推薦商品: 採購行為與紀錄分析 (big data?)
1. 商品庫存: 庫存管理系統 API
1. 購物車:   訂購流程管理 API

如果這個 APP 真的這樣寫，我看打開 APP 時，轉圈圈至少會轉個半分鐘以上吧。用 fiddler 錄製中間的 http traffic, 會看到好幾條。
微服務要解決的是內部軟體開發架構的維護，擴展等等架構問題，這些對外面的客戶及系統是非必要的。對外界來說，只要把整套系統當成單一應用程式就好了。這時要知道這麼多服務的 API 在哪裡，還要呼叫這麼多次 API 才能湊齊足夠的資訊，這做法還蠻蠢的...

![](/wp-content/uploads/2017/06/2017-06-07-01-00-44.png)

於是... 開始出現了 API Gateway 這樣的處理模式，額外建立一個 API Gateway, 放在 APP 與 Microservices 之間，用來轉發及合併多次
API 呼叫。APP 只要對 API Gateway 做一次 API call, 由 API Gateway 代勞，到後端各個服務個別取得所需資訊之後，統一匯集起來傳回前端 APP。這麼一來，對於 APP 來說，他只要一次的呼叫就能取得所有的資訊。

當然 API Gateway 不只是做 N => 1 這種事情而已。其他如 API management, API routing, caching, authorization, logging ... 等等
都有可能在 API Gateway 之中一起處理。這兩種模式 (直接呼叫 vs 透過 API Gateway) 有哪些差異? 我列舉幾個最明顯的特徵:

模式  |   直接呼叫    |   透過 API Gateway
------|--------------|--------------------
1. | 效率差，須經過多次往返 | 效率好，只需一次往返
2. | 不易管理，內部服務架構異動會影響 APP 設計 | 好管理，將內部服務架構的細節隔離在內部。必要時也能進行不同版本或格式的 API 轉譯
3. | 難以最佳化 | 有統一的進出端口，容易進行最佳化，API Gateway 能妥善做好 output cache
4. | 安全性差，跨服務的溝通細節暴露在外界 | 安全性佳，不需將不必要的細節傳遞到外面。API Gateway 甚至能負責認證等等問題。

API Gateway 除了單純的替 APP 呼叫後端 API 時做好 reverse proxy 以及 API call aggration 之外，有些架構師甚至這樣應用 API Gateway, 這是我覺得 API Gateway 在架構上最關鍵的一項應用，就是認證。

跨越服務的認證，一直都是件麻煩的事情。在沒有有經驗的架構師的情況下，團隊往往會做出很糟糕的設計: 每個服務都有自己的認證跟授權機制，
A -> B 有一套轉移認證資訊的作法，B -> C 又一套... 有 N 套服務在運作時，就有 N x (N-1) 種組合要處理... 這時 API Gateway 可以額外
跟負責任證的服務整合，所有 request 統一先取得認證資訊之後，再交由 API Gateway 轉發給內部各個服務。由 API Gateway 統一處理認證
失敗，認證過程的 log 等等動作，後端的服務則在安全的保護傘之下，只要憑著 API Gateway 傳過來的憑證，提供 APP 各種服務即可。

其實這部分實作的原理，在這系列的這篇 [API Token](/2016/12/01/microservice7-apitoken/) 就已經說明過實作細節了。這個機制可以
實現跨服務的認證，需要作法說明的可以參考。

如果想要參考相關的 API Gateway Solutions, 可以找找 open source projects (例如: [Kong](https://getkong.org/about/)), 或是找找雲端的 PaaS 服務。用的進階
一點，甚至 API Management 類型的服務也可以先評估看看 (例如: [Azure API Management](https://azure.microsoft.com/zh-tw/services/api-management/))，最後才是考量自己開發。




## Service Discovery

![](/wp-content/uploads/2017/06/2017-06-07-00-28-21.png)

再來是服務發現的機制。這張圖就說明了 Service Discovery 想要解決的問題。服務那麼多，你如何知道你要的服務在哪裡? 替每個服務解決
這個問題，就是 Service Discovery 主要的目的了。服務發現的機制是微服務架構的核心，基礎建設裡的其他服務也離不開它，包括前面提到的
API Gateway 也是。

Service Discovery 的目的很明確，就是處理好整套微服務架構內，每個各別的服務的管理，讓其他服務或是外界的服務，能夠很明確的 "找到"
他需要的服務在哪裡 (IP，PORT 等等資訊)。為了讓這個機制能順利運作，服務發現的機制通常也包含了可用服務的清單維護，同時也涵蓋了讓其他
服務順利找到正確服務端點的 config management 機制。

因為建置 Service Discovery 是每個微服務系統的必經過程，因此整個 application 的共用組態資訊大都也都集中在 Service Discovery
身上，每個服務大概只要準備最基本的憑證資訊，還有如何找到 Service Discovery 的最基本設定註冊資訊就夠了。剩下的組態都等到註冊
完畢之後再說..

![](/wp-content/uploads/2017/06/2017-06-07-00-28-22.png)

這張圖，就是最典型的 Service Discovery 的運作機制了。如果搭配的服務註冊 (Service Registry) 有搭配
的用戶端 (Registry Client) 的話，每個服務在啟動時，執行一次 Registry Client, 這時 
Service Registry 就能夠隨時掌握到現在有多少服務執行中了。當其他服務需要呼叫 API 時，只要到
Service Registry 去查詢，就可以知道該服務的 IP 跟 PORT 了。

這流程幾乎跟 DNS 是一模一樣的，所以我才會說有些狀況下，直接採用 DNS 就足以應付 Service Discovery 的需求。

![](/wp-content/uploads/2017/06/2017-06-07-00-28-31.png)

再來看個進階一點的架構。前面講的做法，負載平衡或是高可用性的機制，是由呼叫端決定的 (左側的 service instance a) 但是大部分情況下，由後端來決定是比較好的選擇。因此有了這個改善過的架構圖。

這個架構裡，呼叫端不再需要自行到 Service Discovery 查詢可用的服務端點，而是直接到 Load Balancer 
要求服務就好了。Load Balancer 再執行前面說明的動作: 查詢 Service Registry 後挑出一台把 request
轉給他。由於這些都是服務端管控決定的，萬一出了甚麼意外，維運人員能夠很妥善的處理，不會影響到前端的運作。

![](/wp-content/uploads/2017/06/2017-06-07-00-28-41.png)
![](/wp-content/uploads/2017/06/2017-06-07-00-28-42.png)

接著再來看服務健康狀態的監控吧! 這兩張圖就一起看了。
上圖是基本的架構，每個服務啟動時會跟 Service Registry 回報服務已啟動，除此之外啟動過程中也會定期
傳送通知，告訴 Service Registry 說 "我還活著!"

這樣的作法，缺點有幾個:

1. 服務中斷時有一段無法確認的時間。例如 heartbeat 如果是每 10 sec 發送一次，那麼這 10 sec 內掛掉的話，Service Registry 會無法在第一時間就偵測到服務中斷。
1. 服務掛掉，但是還在持續傳送 heartbeat, 導致 Service Registry 判定錯誤。

其實這些點歸納起來，關鍵應該在 Service Registry 最好也能夠有 "主動" 偵測該服務是否正常運作的機制，
而不是只能被動地等服務自己回報。這時調整過的架構 (下圖) 就派上用場了。

除了服務 10.4.3.1:8756 主動跟 Service Registry 回報之外，多了 Registrar, 會代表偵測服務本身
是否正常運作? 通常這樣的偵測會比較精確，因為它會真的呼叫 API 來驗證，比如 PingAPI(), 或是服務會專門
提供 Echo(), 或是 Diagnoistic() 之類的 API，專門拿來偵測健康狀態用。

因為他是透過真正的 API 來確認，因此至少可以確定該服務是真正在線上的。舉個例子，.NET 開發人員應該都
能理解，有時 IIS 的 App Pool 掛掉的狀況下，每個 API 都無法運作 (直接傳回 500), 但是該 Server 排的
定期 10 sec 發送 heartbeat 卻一直正常執行中。這時 API 提供 Echo() 就能更精確地偵測這種狀況，因為
Echo() 也是 API 的一部分，若他能正常地回應，那代表至少該 App Pool 是正常運作的...


## Async & Sync Communication / Event System

這邊講到服務與服務之間的通訊方式，就複雜得多。一般來說，通訊方式好幾種，有同步 (Sync) 與非同步 (Async) 的區別，
有主動呼叫與被動回呼 (Callback) 的差別，也有根據主題 (Topic) 進行發布 (Publish) 與訂閱 (Subscription) 的模式等等
都有。但是我們講到服務提供的 API，印象中大概只會浮現 HTTP / RESTFul 這類的實作技術... 明顯的中間還有好大一段落差..。









# Docker, 最佳的微服務部署方式

# Immutable Services




---------------



微服務對外提供的主要都是各種服務的 API，因此對外的第一個關卡就是 API Gateway. 
想像一下，這些 API 的背後若都是由幾百個微服務所組合而成的，你如何叫外面的系統各自呼叫到正確的微服務? 因此需要有個
良好的 API 代理機制來負責。

細節後面再談，API Gateway 大致上可以解決這幾件事:

1. 身分認證
1. API 路由 (routing)
1. API 聚合 (aggration)
1. API 流量管控 (throttle)

接著是 Service Discovery。既然我們都把整套系統切割成眾多微小的個別服務了。這時可能會很頻繁的增加或減少服務的 instance 。
那麼這麼多 service instance 的動態資訊該如何維護與管理? 這就是 service discovery 要扮演的
角色了。基本的模式就是有個 service registry 的機制，只要每個服務啟動了，第一件事就是跟他報告，其他人就能找的到正確的定位
服務。為了維護這清單的正確性，自然也有一些 healthy check 的機制。

實際上的狀況，DNS + instance 啟動時自動註冊已經可以負責處理大部分的 service discovery 需求。不過當然也有更進階更精準的
解決方案可以選擇。

再來就是微服務最關鍵的通訊機制了。這可以說是微服務的核心了。服務跟服務之間，就是各種的 API 呼叫了。隨著用途的不同，會有
同步(sync), 非同步(async), 回呼(callback), 事件觸發(event-driven), 訂閱(pub/sub) 等等不同的模式，單靠一種 HTTP 難以
涵蓋各種需求；這類問題自己處理通常也會有可靠度與效能不佳的問題。當你需要可靠的通訊時，Message Queue 變成不可或缺的一環。

最後的 Log, 也是必須考量的一個基礎建設。除了典型的 Log 之外，我另外提一點: 跨越服務的紀錄追蹤。我舉個很常見的例子，快遞往往
有很多收發站，你送件之後就可以拿到 tracking number, 之後你就可以靠這個 tracking number 追查你的貨物到底送到哪裡了? 系統的
處理也是一樣，當一件事情拆成好幾個服務分別解決時 (別忘了，每個服務可能都還有上百個 instance ...), 出問題時你如何能從 Log
追查出這些問題所在? 如果你還是把 Log 當成每個 service 自己的日誌流水帳看待的話，碰到這種問題應該會一個頭兩個大。

看完有沒有覺得，微服務真是個坑啊，沒有準備好就跨進來的話真的是找死... 其實很多有經驗的架構施，分享微服務的經驗的看法都差不多，
他有很多好處，但是不代表每個團隊都需要用。我舉幾篇給大家參考，跟之前一窩蜂的那篇有異曲同工之妙:



































在這份電子書裡面，提到跟 microservices infrastructure 有關的有這幾個部分:

* API Gateway
* IPC (Inter-Process Communication)
* Service Discovery
* Event-Driven

除此之外，我另外追加一個我認為很重要的部分:

* Logs & Tracking

這幾個關鍵元件服務，被歸類在微服務架構的基礎建設之中。原因無他，因為只要你使用了微服務架構的概念來設計整套系統架構的話，
有些問題你是一定會碰到的。而這些基礎建設就是解決這些問題的最佳 solution. 

整體來看，API Gateway 扮演的就是 API 對外的關卡，你可以把他跟反向代理 (Reverse Proxy) 做個對比。反向代理主要用途，是
用來發行內部的 "網站"，在這過程中反向代理有時也會身兼 load balancer, waf (web application firewall) 等等角色來兼顧
安全，效能，擴充性與架構調整的彈性等等；而 API Gateway 則是用來發行內部的 "API"，也有一樣的目的與功能。

跨服務的通訊，也是個大問題。雖然微服務的特色之一是允許技術的異質性 - 每個服務互相獨立，可以個別採用最適合的技術，不需要
彼此限制。但是互相通訊的時候就需要統一了。這部分就牽涉到通訊的機制了。一般最常見的就是 HTTP + REST + JSON，可以提供同步 (SYNC)
的 API 呼叫。但是若你需要更複雜且可靠度更高的通訊機制，則需要採用 Message Queue 或是 Message Bus 這類的基礎建設了。
一個良好的 Message Bus 可以解決你很多可靠的通訊問題，包含提供非同步 (ASYNC) 的通訊模式，這點我們後面再探討。

通訊及提供服務的模式，除了同步 (SYNC) 與非同步 (ASYNC) 之外，從另一個角度來分類，則是被動呼叫與主動執行兩種。WEB 就是
典型的被動呼叫模式，你的 API 放在那邊等著人家來呼叫就是一例。但是有些時候，你的服務必須在沒有外面的系統呼叫 API 時執行。
最常見的就是定期執行的任務，或是某些重複執行，長時間執行等等任務都屬這種。

因此，進入實作微服務架構的第一件事，不是捲起袖子開始寫 code, 而是先把你需要的基礎建設與開發環境搭建起來。即使是基礎建設，
它們也維持跟微服務一樣的準則，簡單，只負責一件事，自主運作。不過，除非你很清楚知道你自己要做什麼，否則我強烈建議不要自己
動手開發基礎建設的服務，盡可能地採用成熟穩定可靠的 solution 才是上策。因此這段我主要的目的，是介紹每類基礎建設的服務是要
解決那些問題，而非你怎麼操作或是安裝他們。只有知道這些東西存在的目的，你才能做出最正確的判斷與選擇 (該挑選哪一套?
還是要自己開發? 該如何評估?)。

其他講微服務架構與觀念的，還有如何重構既有的 application, 我們在前面兩篇其實都帶到了，這裡就針對基礎建設來探討。
基礎建設通常也是某個(微)服務，用來解決多個微服務互相協同合作必要的基礎。例如通訊、代理、服務註冊語組態管理等等。



API Gateway 可以替整套系統統一解決掉認證問題，後面的每個服務就不再需要逐一確認呼叫者的身分，可以直接針對身分做授權的管控
即可。其他如API 呼叫次數的管控，API 呼叫的日誌等等都可以由 API Gateway 統一處理。但是最重要的，我認為是這兩項: aggration & routing。

Routing 是第一件最關鍵的任務，他可以把外面的 API 呼叫，引導到內部適合的服務接手處理。這個 routing 的機制能解決很多衍生的問題，
包括版本 (例如: 新舊版本的 client 呼叫同一組 API 需要提供不同的服務)，負載平衡與服務註冊 (例如: 需要將 API call 引導到 loading
較低的服務端點，或是引導到狀態良好沒有當掉或停機維護的端點)。這部份很多現成的服務可以選擇，可以找 API Gateway, 或是 API Management
這些關鍵字，可以找到不少資訊。

另一個關鍵的功能就是 Call Aggration。
