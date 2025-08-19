---
layout: post
title: "架構師觀點 - 轉移到微服務架構的經驗分享 (Part 3)"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "infra", "message queue", "api gateway", "service discovery"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/07/bridge.jpg
---


![](/wp-content/uploads/2017/07/bridge.jpg)

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
* Log

![](/wp-content/uploads/2017/07/2017-06-18-01-41-32.png)

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

![](/wp-content/uploads/2017/07/2017-06-06-02-07-00.png)
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

![](/wp-content/uploads/2017/07/2017-06-07-00-50-18.png)

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

![](/wp-content/uploads/2017/07/2017-06-07-01-00-44.png)

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

![](/wp-content/uploads/2017/07/2017-06-07-00-28-21.png)

再來是服務發現的機制。這張圖就說明了 Service Discovery 想要解決的問題。服務那麼多，你如何知道你要的服務在哪裡? 替每個服務解決
這個問題，就是 Service Discovery 主要的目的了。服務發現的機制是微服務架構的核心，基礎建設裡的其他服務也離不開它，包括前面提到的
API Gateway 也是。

Service Discovery 的目的很明確，就是處理好整套微服務架構內，每個各別的服務的管理，讓其他服務或是外界的服務，能夠很明確的 "找到"
他需要的服務在哪裡 (IP，PORT 等等資訊)。為了讓這個機制能順利運作，服務發現的機制通常也包含了可用服務的清單維護，同時也涵蓋了讓其他
服務順利找到正確服務端點的 config management 機制。

因為建置 Service Discovery 是每個微服務系統的必經過程，因此整個 application 的共用組態資訊大都也都集中在 Service Discovery
身上，每個服務大概只要準備最基本的憑證資訊，還有如何找到 Service Discovery 的最基本設定註冊資訊就夠了。剩下的組態都等到註冊
完畢之後再說..

![](/wp-content/uploads/2017/07/2017-06-07-00-28-22.png)

這張圖，就是最典型的 Service Discovery 的運作機制了。如果搭配的服務註冊 (Service Registry) 有搭配
的用戶端 (Registry Client) 的話，每個服務在啟動時，執行一次 Registry Client, 這時 
Service Registry 就能夠隨時掌握到現在有多少服務執行中了。當其他服務需要呼叫 API 時，只要到
Service Registry 去查詢，就可以知道該服務的 IP 跟 PORT 了。

這流程幾乎跟 DNS 是一模一樣的，所以我才會說有些狀況下，直接採用 DNS 就足以應付 Service Discovery 的需求。

![](/wp-content/uploads/2017/07/2017-06-07-00-28-31.png)

再來看個進階一點的架構。前面講的做法，負載平衡或是高可用性的機制，是由呼叫端決定的 (左側的 service instance a) 但是大部分情況下，由後端來決定是比較好的選擇。因此有了這個改善過的架構圖。

這個架構裡，呼叫端不再需要自行到 Service Discovery 查詢可用的服務端點，而是直接到 Load Balancer 
要求服務就好了。Load Balancer 再執行前面說明的動作: 查詢 Service Registry 後挑出一台把 request
轉給他。由於這些都是服務端管控決定的，萬一出了甚麼意外，維運人員能夠很妥善的處理，不會影響到前端的運作。

![](/wp-content/uploads/2017/07/2017-06-07-00-28-41.png)

接著再來看服務健康狀態的監控吧! 這兩張圖就一起看了。
上圖是基本的架構，每個服務啟動時會跟 Service Registry 回報服務已啟動，除此之外啟動過程中也會定期
傳送通知，告訴 Service Registry 說 "我還活著!"

這樣的作法，缺點有幾個:

1. 服務中斷時有一段無法確認的時間。例如 heartbeat 如果是每 10 sec 發送一次，那麼這 10 sec 內掛掉的話，Service Registry 會無法在第一時間就偵測到服務中斷。
1. 服務掛掉，但是還在持續傳送 heartbeat, 導致 Service Registry 判定錯誤。

其實這些點歸納起來，關鍵應該在 Service Registry 最好也能夠有 "主動" 偵測該服務是否正常運作的機制，
而不是只能被動地等服務自己回報。這時調整過的架構 (下圖) 就派上用場了。

![](/wp-content/uploads/2017/07/2017-06-07-00-28-42.png)

除了服務 10.4.3.1:8756 主動跟 Service Registry 回報之外，多了 Registrar, 會代表偵測服務本身
是否正常運作? 通常這樣的偵測會比較精確，因為它會真的呼叫 API 來驗證，比如 PingAPI(), 或是服務會專門
提供 Echo(), 或是 Diagnoistic() 之類的 API，專門拿來偵測健康狀態用。

因為他是透過真正的 API 來確認，因此至少可以確定該服務是真正在線上的。舉個例子，.NET 開發人員應該都
能理解，有時 IIS 的 App Pool 掛掉的狀況下，每個 API 都無法運作 (直接傳回 500), 但是該 Server 排的
定期 10 sec 發送 heartbeat 卻一直正常執行中。這時 API 提供 Echo() 就能更精確地偵測這種狀況，因為
Echo() 也是 API 的一部分，若他能正常地回應，那代表至少該 App Pool 是正常運作的...


業界常用的 Service Discovery 服務，有興趣的可以參考看看 CentOS 的 etcd, ZooKeeper, Consul, 或是 .NET 也有人提供
一整套的服務，方便你自己建置你專屬的 Service Discovery 機制。

* [Service Discovery: Zookeeper vs etcd vs Consul](https://technologyconversations.com/2015/09/08/service-discovery-zookeeper-vs-etcd-vs-consul/)
* [Introducing Microphone - Microservices with Service Discovery for .NET](http://blog.nethouse.se/2015/10/19/introducing-microphone-microservices-with-service-discovery-for-net/)
* [Service Discovery for .NET developers - Ian Cooper](https://vimeo.com/155652026)


## Async & Sync Communication / Event System

這邊講到服務與服務之間的通訊方式，就複雜得多。一般來說，通訊方式好幾種，有同步 (Sync) 與非同步 (Async) 的區別，
有主動呼叫與被動回呼 (Callback) 的差別，也有根據主題 (Topic) 進行發布 (Publish) 與訂閱 (Subscription) 的模式等等
都有。但是我們講到服務提供的 API，印象中大概只會浮現 HTTP / RESTFul 這類的實作技術... 明顯的中間還有好大一段落差..。

技術上來說，有很多基礎建設，可以解決各類的通訊問題。不過我想最關鍵的還是你的應用系統，需要什麼樣的通訊機制? 舉例來說:

1. 非同步 (Async):  
最典型的是訂購系統。接受訂單後也許有很長的處理流程，但是前端不需要一直等待整個訂購流程處理完畢，只要收到 "確認訂單已受理"
的訊息就足夠了。這時挑選一套 Message Queue 的服務，或是自己在後端的 database 做好類似的設計即可。
1. 可靠的通訊 (Sync):
一般都是透過 HTTP + REST API, 中間搭配 Load Balancer / Reverse Proxy 等等設備來架構大型的同步通訊。不過可靠度
的處理，都是 application 要自己負責的。若 HTTP 無法滿足，則可以藉由兩組 Message Queue 來協助。一組負責處理 Request,
另一組負責處理 Response, 即可達到雙向的同步通訊
1. 事件通知 (Event):  
這是比較複雜的情境，沒有明確的呼叫端與被呼叫端，而是某個狀況發生後，負責處理的服務必須主動地去攔截下來處理的機制。這類
協同運作的機制，在微服務架構內尤其重要，幾十個服務一起處理同一筆交易時，你可以想像沒有事件的機制時要如何溝通...。正確的使用
事件機制，能把 N x M 種溝通組合，簡化成 N + M, 是架構上很重要的一種規劃。同樣的，這類機制也需要依靠 Message Queue, 或是
Message Bus 這樣的服務來處理。

講來講去都是需要 Message Queue 啊，好好運用 Message Queue 的話，是能大幅簡化你的 application 複雜度的。通常系統之間最
複雜的就是資料流，Message Queue 之所以能夠解耦 (decop), 主要就是把整套系統區分為發布訊息 (publisher), 接收訊息 (subscriber)
與轉送訊息 (exchange + queue) 三種角色。前兩者 (pub / sub) 是你的 code, 第三者就是 Message Queue, 你可以有統一的地方
去管控訊息的流向，這部分能用成熟的 solution 來規劃與監控，自己開發的部分只要顧好何時該發送與接收訊息。

降低複雜度，是我認為使用 MQ 最主要的原因。就系統層面來看，提高效能與可靠度也是原因之一，MQ 能做到這點有兩個原因:

1. 儲存後轉送，可允許訊息接收端離線。重新上線後就能繼續處理，不會丟失資料。
1. 容易擴充。可以同時用多個接收端，接到訊息就處理。負載可維持在穩定的處理速度，不會有瞬間飆高的情況。免除了中間一層負載平衡(LB)也簡化了架構的複雜度。

說了這麼多，就拿一個簡單的例子來看看好了。就拿微服務架構下，最常被問到的問題: 微服務架構下如何確保交易的一致性?

這已經是 FAQ 等級的問題了。過去交易的正確性都是靠 RDBMS 的 transaction control 在控制的。一連串的 SQL 指令，RDBMS 會確保
他一定會完整的執行完畢 (commit)，若有任何問題則會完整地回復 (rollback)。然而系統已經微服務化，切割為多個獨立且分散的服務時，資料庫
連帶的也被拆解，因此這類交易的問題就落到系統開發者與架構師的身上了。

這邊就用個簡單的 Story 當作案例來說明這狀況: 系統的用戶 USER1, 透過網站 WEB 操作下達了指令，要拿它儲值在網站 (BANK1) 上的
金額扣掉 $100 元，購買遊戲點數 (GAME1) 100P；交易成功後 BANK1 要扣掉 $100，而 GAME1 的戶頭則要加上 100P，否則則要恢復原狀，
不能有其他的結果。

在這案例內 BANK1 跟 POINT1 則是個別獨立的微服務，彼此的資料可能是存在 NOSQL Database, 或是分別處於獨立的 SQL database, 無法
使用 RDBMS 內建的 transaction control.

這邊就考驗你的基礎知識夠不夠札實了。在這邊你大概得了解兩件事，一個就是可靠的通訊如何實作 (例如 Message Queue), 另一個是理論基礎，
如何做好分散式的交易控制 (例如 2PC, 2 phase commit)。

正好前面介紹的 Nginx 那系列 Microservice 文章, 就有提到 IPC (Inter Process Communication) 跟 Event Driven Systems, 正好有
類似的案例可以參考，我就借來說明一下:

* [IPC](https://www.nginx.com/blog/building-microservices-inter-process-communication/)
* [Event-Driven Data Management for Microservices](https://www.nginx.com/blog/event-driven-data-management-microservices/)

在 Event-Driven 那篇文章裡，講到這個例子:

![](/wp-content/uploads/2017/07/2017-07-11-23-29-15.png)

交易剛被受理時，訂購服務 (Order Services, 也就是我們案例提到的 BANK1) 先在自己的 storage 內新增一筆交易紀錄，但是交易尚未完成，
因此將狀態標記為 "NEW"，同時在 Message Broker (或是 Message Queue, Message Bus 等名詞都是指類似功能的服務) 送出這筆訊息 (Message, or Event)。


![](/wp-content/uploads/2017/07/2017-07-11-23-34-46.png)

另一個服務 (Custom Services, 也就是我們案例提到的 GAME1) 對這個訊息有興趣，系統啟動之初早已先行註冊，訂閱這些交易相關的訊息。
因此當訂購事件被送出時，他會收到由訂購服務傳來的訊息。這時 Custom Services 就在自己的 storage 內也新增一筆交易紀錄，確認收到
費用，同時也記錄 Order Services 那邊傳過來的單號 (OrderId) 以利將來的查帳。完成之後也透過 Message Broker 再送出收到款項
的訊息。


![](/wp-content/uploads/2017/07/2017-07-11-23-37-21.png)

最後，原本的 Order Services 也訂閱了這訊息，會收到來自 Custom Services 送出來的交易確認訊息，確認這筆交易成功執行，因此更新
自己的 storage, 將該筆交易的狀態從 "NEW" 改為 "OPEN"，確認交易成功執行完畢。


在這裡講的都是很順利的狀況，如果過程不是那麼順利，例如 Custom Services 當掉了，遲遲沒有回覆，或是 Custom Services 碰到問題，
無法提供服務時 (例如遊戲已經下架，不再提供儲值)，該如何取消交易?

這邊我就簡單說明一下 2PC 好了，不再逐步說明。2PC 簡單的說就是把整個交易拆成兩個階段 (2 phase), 第一個階段由交易控制端 (Order Services) 先詢問所有跟這交易相關的對象，是否能夠成功執行該筆交易? (此例就是 Custom Services) 如果每個對象都能在指定的 Time out
時間內回覆確認訊息，則該筆交易就會照常執行。只要有任何一項條件不滿足 (例如沒有全部對象都回覆確認，或是超出時間還未收到所有回覆)，
則該筆交易會取消。

回到這個例子，Order Service 收到 Custom Services 的確認訊息，就算完成 1st phase 了，於是就把自己的交易紀錄狀態改為 "OPEN"。
如果失敗的話，Order Service 應該將自己的交易紀錄標記為 "CANCEL"，同時再送出交易取消的訊息。這時該筆交易已經不可能再執行了，只有
取消一途，因此若無法確認 Custom Services 是否收到取消交易的訊息，則可以在未確認前不斷重送取消的訊息，直到確認為止。

其實分散式交易要確認執行，還有很多種變通的作法，這只是最典型的案例。在這邊 Message Broker 是主要的關鍵，他同時負責了一對多的
通訊，也同時負責了可靠的通訊。當然這邊把 Message Broker 拿掉，改成 HTTP + REST 也行，不過你這樣就得花費更多心思去處理通訊
失敗的狀況。

其他微服務之間通訊相關的問題 (IPC)，以及事件處理 (Event-Driven) 相關的機制，可以參考這兩篇文章其他的內容，我就不再多做介紹。


同樣的，這類通訊相關的基礎建設，自己做太不靠譜了。可靠度這種東西，沒有足夠的社群用戶支持，是很難支撐起來的。我推薦這部分盡可能
的找經過多人驗證過可靠的系統來使用。這幾套都是不錯的選擇:

* [RabbitMQ is the most widely deployed open source message broker](http://www.rabbitmq.com/)
* [Kafka](https://kafka.apache.org/)

另外如果你對架構的要求並不高，而且這些也正好已經在你的 service stack 內的話，也可以考慮拿來擔任通訊的服務:

* [Queuing tasks with Redis](https://blog.logentries.com/2016/05/queuing-tasks-with-redis/)

別訝異，這邊 MSMQ 也在清單內。其實 MSMQ 算蠻可靠的，他連 client side 都是 store and forward, 就可靠度而言甚至還贏過其他的
message queue. 如果你要雙向的通訊，MSMQ 也支援 Response Queue 及 CorrelationId 的設計。只是他的年紀也大了，要實作
pub / sub 略嫌麻煩了點，也不夠靈活。同時部署還要依賴 AD ... 如果這些限制不是你在意的點，同時你對於 "使命必達" 這件事要求
特別高，又剛剛好是用 windows, 是可以考慮看看:

* [MSMQ](https://msdn.microsoft.com/en-us/library/ms711472(v=vs.85).aspx)
* [Response Queues](https://msdn.microsoft.com/en-us/library/ms705701(v=vs.85).aspx)



# 後記

特地把微服務架構必備的基礎建設獨立成一篇來介紹，其實主要的目的是想藉這篇告訴大家，微服務的基礎建設是否可靠與完善，大概就已經
決定了你的微服務架構能否成功了。要在不穩固的基礎上搭建微服務架構，幾乎是不可能的事，這也是微服務架構的進入門檻。這些基礎建設，大都
已經有成熟可靠的選擇了。在你能力範圍以內 (有能力是指: 買得起，跑的動，夠了解，有能力維護)，盡可能挑選一套最好的。當然整體搭配
的好不好也是個關鍵，這邊如何拿捏就看你的經驗與判斷了!

原本想在這篇一起講的微服務部署，看來得等下一篇了 @@, 敬請期待...

