---
layout: post
title: "微服務基礎建設 - Service Discovery"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "架構師", "service discovery", "service mesh"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/12/Modern-Apps-1024x564.png
---


微服務系列文章停了幾個月，因為這系列的文章不好寫啊，很多內容有想法，但是沒有實做過一遍的話，寫出來的東西就只是整理網路上
其他文章的觀點而以，那不是我想做的 (這種事 google 做的都比我好)。經過這幾個月，自己私下 & 工作上又都累積了一些經驗，就又有
素材繼續動筆了! 這次要補的是微服務必備的基礎建設之一: 服務註冊與發現機制 (Service Discovery)。

Microservices 先天就是個分散式系統，在開發領域上的門檻，主要就是各種呼叫遠端服務 RPC - Remote Procedure Call 的相關技術了。
然而在架構上最重要的一環，就屬 "服務發現" Service Discovery 這技術了。說他是微服務架構的靈魂也當之無愧，試想一下就不難理解:
當一個應用系統被拆分成多個服務，且被大量部署時，還有什麼比 "找到" 我想要呼叫的服務在哪裡，以及是否能正常提供服務還重要? 同樣的
有新服務被啟動時，如何讓其他服務知道我在哪? 人家說微服務考驗的就是你治理大量服務的能力，包含多種服務, 也包含多個 instances。
要做到這件事，Service Discovery 就是你要挑戰的第一關。


說到治理大量服務的能力，Nginx 官網有篇[文章](https://www.nginx.com/blog/nginmesh-nginx-as-a-proxy-in-an-istio-service-mesh/)
講得不錯，我就借他的圖用一用。裡面提到 Modern Apps 演進過程，從 1980 的 client / server, 到 2000+ 的 3-tiers, 到現在的 microservices..

![](/wp-content/uploads/2017/12/Modern-Apps-1024x564.png)

你就可以理解到, 走向微服務架構，有沒有能力管理好這麼多數量的 instance, 是你的 apps 能否成功的上線運作的關鍵因素之一。服務的數量
從小規模 (30+) 到大規模 (100+)，到你在書上看到的各種微服務成功案例 (10000+) 就知道，這種數量不大可能靠 IT 人員逐一設置固定 IP + PORT,
然後由 developer 設置 configuration file 逐一指定了。Service Discovery 就是解決這個問題的方法。


<!--more-->

{% include series-2016-microservice.md %}


> 不是我愛賣弄英文啊，不過有些名詞翻成中文，文章寫起來實在有點憋扭... 所以我先在這邊把幾個名詞先做中英對照，後面內文我就一律
> 以英文為主了..

- **Service Discovery**
- **Registry**
- **Service Mesh**
- 






# Service Discovery Concepts

Service Discovery 之所以重要，是因為它解決了 Microservices 最關鍵的問題: 如何精準的定位你要呼叫的服務在哪裡。不論你用哪一套服務來
提供 service discovery, 大致上都包含這三個動作組合成這個機制，分別是:

1. **Register**, 服務啟動時的註冊機制 (如前面所述)
1. **Query**, 查詢已註冊服務資訊的機制
1. **Healthy Check**, 確認服務健康狀態的機制

過程很簡單，大致上就是服務啟動時，自身就先去註冊本身的存在與附加資訊，並且定時回報 (或是定時被偵測) 服務是否正常運作。由 Service Discovery
的機制統一負責維護一份正確 (可用) 的服務清單。因此這服務就能隨時接受查詢，回報符合其他服務期望的資訊。只要彼此搭配的好，所有要跨越服務呼叫
的狀況下，就不用再擔心對方的服務再哪邊，或是服務是否還能正常運作等等議題了。要呼叫時，只管去 service discovery 查詢，然後呼叫就好。

觀念講起來非常簡單，我就直接拿一個大家都熟知，而且已經用了很久的例子: DNS + DHCP。現在的人上網，大概就是設備接上網路就可以使用了。背後用的
就是 DHCP + DNS, 已經默默運作幾十年，最老資格的 Service Discovery 機制。

就從你的 PC 接上網路那一刻開始說明吧! 接上網路那瞬間會發生這幾件事:

1. DHCP 配發 IP:  
首先，你的 PC 會對 LAN 廣播，詢問有誰能給它指派個可用的 IP address? 這時 LAN 若有 DHCP Server，就會回應可用 IP 給 PC，雙方溝通完成就順利取得 IP 並且可以開始上網了。DHCP Server 會記得在何時分配哪個 IP 給哪個設備 (根據 MAC Address)。

2. 對 DNS 註冊 HOST / IP:  
此時 DHCP server / PC client 也沒閒著，DHCP 順利的讓 PC 動態的取得 IP 之後，接下來就會跟 DNS 註冊這 PC 的 host name 以及對應的 IP 
(就是剛才 DHCP 分配的 IP)。有些組態，PC 可以自行跟 DNS 註冊；有些情況下 IT 人員不允許這功能，這時就會改由 DHCP server 配發 IP 後由 DHCP
server 來負責對 DNS 註冊。不論如何，註冊之後 DNS 就認得該 PC 的 Host Name 跟 IP 的對應關係了。這就已經完成上面講的第一個動作:
**register**。

3. 對 DNS 查詢:  
接著，網路上其他人怎麼找到這台 PC ? 很簡單，只要你知道這 PC 的名字 (host name) 就夠了。拿著 host name 到 DNS 去詢問，若登記有案的話，
DNS 就會回應正確的 IP address。若還要查詢服務的附加資訊，如其它註記，或是對應的 PORT 等等，DNS 也有 SRV 及 TXT record 可以對應。在
這階段就是前面提到的第二個動作: **query**。

4. 確認 HOST 是否存在:
當你要開始連線時，你可能會想先確認一下連線目標是否正常連線中? 最常用的方式，就是用 ping 這個指令來測試看看。ping 會送出封包，若 PC 有開啟
ICMP ECHO 的話，就會回應收到的封包。送出 ping 封包的一端收到回應 (echo), 就知道測試 PC 網路功能是正常的。這階段就是前面提到的第三個動作: **health check**。

雖然講到微服務，沒多少人會舉這個古董的 DHCP + DNS 例子來說明，不過這是最簡單易懂的案例，微服務的 Service Discovery 其實也是一樣的原理，
只不過不斷有新的做法來補 DNS 的不足而已。了解到這邊之後，接下來就來看看，常見的幾種 service discovery 機制是怎麼做的。這邊我推薦之前推
薦過的 nginx ebook, 介紹一系列的 microservices 的參考架構與做法，其中一個章節就是講到 service discovery patterns. 我節錄其中一段出來...

文章連結: [Service Discovery in a Microservices Architecture](https://www.nginx.com/blog/service-discovery-in-a-microservices-architecture/)



不論你用什麼方法，Service Discovery 想解決的問題情境，都可以用這張圖來表達:

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-1_difficult-service-discovery.png)

來回顧一下，已經運行數十年的 DNS 有哪些不足的地方? 在微服務架構下，我們預期內部的各個服務，都採取高度動態的前提進行部署。也許隨著流量的
變化，幾秒鐘之內就會有新的 instance 被啟動或是關閉，instance 的數量也可能從數十個到數千個不等。這種狀況下，DNS 無法有效的解決這幾個問題:

1. 服務清單精確度問題: DNS TTL 通常只到 hours 的等級
1. 無法很精準的判定服務的健康狀況
1. DNS 無法精準量測 server loading, 因此 DNSRR (DNS round robin) 沒辦法按照 loading 來進行 load balance
1. DNS 無法對每個 node 進行 healthy check (如: ping each nodes), 故障的 nodes 依然會出現在 DNSRR 回報的清單內
1. DNS 只供查詢，查詢的結果會被 cache 影響準確度, 同時 DNS 無法代替客戶端進行 request forwarding


其實要做到上述的需求，DNS 搭配其它對應的服務也許也能辦的到，但是你也必須額外建立其它的基礎建設，或是開發專屬的功能才能解決。
Service Discovery 為了解決這些問題, 發展出了幾種常見的模式，我就按照文章介紹的順序來說明這幾種 service discovery patterns:


# Service Registration Pattern(s)

先從單純的開始。整套 service discovery 機制要能順利運作，第一步就是先能維護一份可用的服務清單。包含負責處理 service 加入與移除動作的
registry, 以及負責確認這些服務健康狀態的 healthy check 機制。服務本身要如何對 registry "宣告" 自身的存在呢? healthy check 該如何
確認這些服務都維持在可用的狀態下? 作法大致上分兩大類:

1. **The Self‑Registration Pattern**  
自我註冊，顧名思義，上述這些動作，都由服務本身 (client) 自行負責。每個服務本身啟動之後 (有些靜態部署的狀況下，甚至就直接改改設定檔
就可以了)，只要到統一的服務註冊中心 (service register) 去登記即可。服務正常終止後也可以到 service register 去移除自身的註冊紀錄。
服務執行過程中，可以不斷的傳送 heartbeats 訊息，告知 service register 這個服務一直都在正常的運作中。register 只要超過一定的時間
沒有收到 heartbeats 就可以將這個服務判定為離線。

1. **The Third‑Party Registration Pattern**  
這個 pattern 採取另一種做法，healthy check 的動作不由服務本身 (client) 負責，改由其它第三方服務來確認。有時服務自身傳送 heartbeat 
的方式並不夠精確，服務本身已經故障，卻還不斷的送出 heartbeats 訊息，或是內部網路正常，但是對外網路已經故障，而 service register 卻
還能不斷的收到 heartbeats 訊息，導致控制中心都一直沒察覺到某些服務實際上已經對外離線的窘境。

這時要確認服務是否正常運作的 health check 機制，就不能只依靠 heartbeats, 你必須依賴其他第三方的驗證 (ping) 不斷的從
client side network 來確認服務的健康狀態。

這些都是有助於協助 registry 提高他手上的服務清單準確度的作法。能越精準的提高手上服務清單的正確性與品質 (清單上每個服務 end points 都是可用
的), 你的整套微服務架構的可靠度就會更高。這些方法不是互斥的，有必要的話可以搭配使用。不論如何，讓 registry 手上隨時能維護一份可用的服務清單
是很重要的，先讓這些資訊正確，才有後面可靠的 service discovery。




# The Client‑Side Discovery Pattern

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-2_client-side-pattern.png)

這種模式 (Client-Side Discovery Pattern) 的作法，主要是 client side 使用能跟 service registry 搭配運作的 Http Client (就是
圖中的 Registry-aware HTTP Client) ，在呼叫前先查詢好相關資訊，之後就可用來呼叫該服務的 REST API。Registry 會回報可用的服務 End Ponts
清單資訊，由 HTTP Client 自己決定要選擇哪一個 End Point.


**優點**:

那麼這種模式下，Load Balancing 通常是 Http Client 查詢服務的 end points 清單後，自己用自身的演算法，來從中挑選一個。好處是呼叫端可以
用最大的彈性來自訂負載平衡的機制，包含如何挑選最適當的 end point 等等。有時對服務等級要求很高的時候 (比如 VIP 要求有專屬的服務集群，或是
要有更精準的查詢方式等)，這個模式會更容易實作。

容易自訂化是這個方式的優點，另外 http client 通常也會做成 library 或是 SDK 的型態，直接引用到你的開發專案內，實際執行時這部分是
 in-process 的方式進行，語言間的整合程度最佳，執行效能也最佳，開發集除錯也容易，初期導入 service discovery 的團隊可以認真考慮這種模式。
有很多輕量化的 service discovery 也都採用這種模式。


**缺點**:

然而這也是這模式下的缺點。當這些調度的機制被控制在 client side, 往往也會有對應的風險。當這些機制要更新時，難以在短時間內同步更新，造成
有新舊的規則混雜在一起。因為這類 Registry-aware HTTP Client, 多半是以 runtime library 的形態存在，是用侵入式 (邏輯必須注入你的應用
程式中) 的方式存在於所有的 client 之間。要替換掉它，通常得重新編譯，重新部署服務才行。也因為它屬侵入式的解決方案，你也要確保你的專案開發
的技術或框架，有原生的 SDK or library 可以使用 (當然也得顧及到社群的生態，更新是否快速等等)。只是，對於服務調度邏輯這方面的隔離層級還
不夠，解耦也做的不夠，當你很在意這個部分時就得多加考慮。

另一個主要的缺點是, 這樣的設計，也導致你的 application 會跟特定的 registry 綁在一起了，將來換成別套 registry 則需要改寫 code, 你服務
的規模越大就越困難。這某種程度其實違背了微服務架構倡導的技術獨立性。

> 侵入式: 代表這部分的邏輯，會以 source code, library 或是 component 等等的形式，"侵入" 到你的服務程式碼內。這種型態的置入，通常
> 能提供最佳的效能及功能性，也能提供最大的自訂化彈性。不過這也是缺點；意思是這置入的部分一但有任何修正，你的服務是必須經過 更新 > 重新
> 編譯 > 重新部署 這幾個步驟的，往往越通用的套件，要更新都是件麻煩事。採用侵入式的解決方案時，請務必考量到更新與重新部署時的挑戰。


**案例**: Netflix Eurica  

Netflix 將自己的微服務基礎建設跟框架，都開源了，就是 Netflix OSS (Open Source Solutions), 其中 service discovery 的部分，就是
Netflix Eurica, 就是 service discovery 裡面的 registry. 而對應到這模式的 client, 則是 Netflix Ribbon, 專門設計跟 Eurica 搭配的
IPC client, 允許你直接在 application 裡面自訂專屬的 load balance logic.

**案例**: Consul  

Consul 是另一套類似的 solution, 不過他起步得比較晚, 整合度高，所以也有不錯的接受度。Consul 能夠很容易的架設起跨資料中心的 service discovery
機制，同時也內建了完善的 healthy check 機制，包含 client side 主動送出 heartbeats, 也包含了 registry 主動偵測 client 的設計。另外
為了雨季有系統相容，Consul 本身也提供了 DNS 的 protocol, 意思是傳統的 application 只要搭配正確的 TCP/IP 設定, 不需要特別改寫 code
也能夠搭配 Consul 一同運作。

提供 DNS 的介面，算是個不錯的設計，透過既有成熟的 DNS protocol, 巧妙的避開了 client side discovery pattern 的缺點: 需要搭配特定的
client (registry-aware http client)，直接使用標準的 http client 就好了；這方法最大化的提供技術獨立性。

另外的特色是，Consul 也整合了 key-value configuration。這是微服務架構另一個必要的基礎: 集中的組態管理。這部分我暫時不多談，後面我打算
寫一篇 service discovery labs 的實作文章，會直接採用 Consul + .NET application + Windows Container, 到時再來詳細介紹這些內容。







# The Server-Side Discovery Pattern

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-3_server-side-pattern.png)

既然有前面講到的 "Client-Side" discovery pattern 的存在，自然也有對應的 "Server-Side" discovery pattern... 很直覺的，就是把原本 client side 執行的 registry-aware http client 這部分拆出來，變成一個專屬的服務；對的，就是圖上標示的 "LOAD BALANCER"。

跟一般的 Load Balancer 不大一樣的地方是: 這個 Load Balancer 會跟 Registry 密切的配合 (registry aware)。Load Balancer 會即時的按照
Registry 提供的資訊，扮演 reverse proxy 的角色，來將 request 導引到合適的 end point. 相較於 registry aware client 的做法而言，
server-side discovery pattern 對 application 而言是透明的, service discovery 的邏輯, 都集中在 load balancer 身上。


## 優點:

相較於 client-side discovery pattern, 優點很明確, 就是 registry 對於 client side 來說是透明的，所有細節都被隔離在 load balancer 跟 service registry 之間了。不需要侵入式的 code 存在 client side, 因此也沒有前述的 language, library maintainess 等相關問題, 更新也
只要統一部署 load balancer & service registry 就足夠了。

## 缺點:

這樣一來，服務的架構等於多了一層轉送了。延遲時間會增加；整個系統也多了一個故障點，整體系統的維運難度會提高；另外最關鍵的，load balancer 
可能也會變成效能的瓶頸。想像一下，如果整套 application 存在 N 種不同的服務，彼此都會互相呼叫對方的服務，那麼所有的流量都會集中在 load balancer 身上。

這樣的任務，很容易跟微服務架構下其他的基礎建設混在一起。例如 service registry 跟 load balancer 的整合, 可能導致兩者必須採用同一套服務了；
再者, 轉送 (forward) 前端的服務請求 (request)，這角色要做的事情又跟 API gateway 高度的重疊，然而 API gateway 還有其他它要解決的問題啊，
最終可能會演變到這些服務，重複出現好幾次 (前端有 API gateway, 後端有另一套 load balancer, 或是每組服務都有自己的 load balancer 等等)。
如果你的規模不夠大，可能你還沒享受到它帶來的好處，你就先被它的複雜度與為運成本給搞垮了...。

回想一下，微服務化的最初用意，有這麼一項: 故障隔離，將整個系統切割為多個服務共同運作，若有某個服務無法正常運行，那麼整個應用系統只需停用
部分功能，其他功能要能正常運作。這樣做的方向就是要去中心化，不過 server side discovery pattern 就是集中式的做法啊.. 去中心化的作法，後面
在更極致的 service mesh 我會再進一步說明...。



## 案例:

AWS Elastic Load Balancer (ELB)

Nginx (reverse proxy) + Consul (use DNS interface)









# 結論










