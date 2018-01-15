---
layout: post
title: "微服務基礎建設 - Service Discovery & Service Mesh"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "infra", "message queue", "api gateway", "service discovery"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/12/service-discovery.jpg
---

![](/wp-content/uploads/2017/12/service-discovery.jpg)

微服務系列文章停了幾個月，因為這系列的文章不好寫啊，很多內容有想法，但是沒有實做過一遍的話，寫出來的東西就只是整理網路上
其他文章的觀點而以，那不是我想做的 (這種事 google 做的都比我好)。經過這幾個月，自己私下 & 工作上又都累積了一些經驗，就又有
素材繼續動筆了! 這次要補的是微服務必備的基礎建設之一: 服務註冊與發現機制 (Service Discovery)。

Microservices 先天就是個分散式系統，在開發領域上的門檻，主要就是各種呼叫遠端服務 RPC - Remote Procedure Call 的相關技術了。
然而在架構上最重要的一環，就屬 "服務發現" Service Discovery 這技術了。說他是微服務架構的靈魂也當之無愧，試想一下就不難理解:
當一個應用系統被拆分成多個服務，且被大量部署時，還有什麼比 "找到" 我想要呼叫的服務在哪裡，以及是否能正常提供服務還重要? 同樣的
有新服務被啟動時，如何讓其他服務知道我在哪? 人家說微服務考驗的就是你治理大量服務的能力，要做到這件事，Service Discovery 就是
你要挑戰的第一關。


<!--more-->

{% include series-2016-microservice.md %}


# 0, Service Registration Patterns

開始之前先來看看，服務本身要如何對 registry "宣告" 自身的存在呢? 作法分兩大類:

1. **The Self‑Registration Pattern**  
自我註冊，顧名思義，每個服務本身啟動之後，只要到統一的服務註冊中心 (service register) 去登記即可。服務正常終止後也可以到 service register 
去移除自身的註冊紀錄。服務執行過程中，可以不斷的傳送 heartbeats 訊息，告知 service register 這個服務一直都在正常的運作中。register 只要
超過一定的時間沒有收到 heartbeats 就可以將這個服務判定為離線。

1. **The Third‑Party Registration Pattern**  
不過，有時服務本身自己傳送的 heartbeat 並不夠精確，例如服務本身已經故障，卻還不斷的送出 heartbeats 訊息，或是內部網路正常，但是對外
網路已經故障，而 service register 卻還能不斷的收到 heartbeats 訊息，導致控制中心都一直沒察覺到某些服務已經離線的窘境。這時要確認服務
是否正常運作的 health check 機制，就不能只依靠 heartbeats, 你必須依賴其他第三方的驗證 (ping) 不斷的從 client side network 來確認服務的
健康狀態。

這些都是有助於協助 registry 提高他手上的服務清單準確度的作法。能越精準的提高手上服務清單的正確性與品質 (清單上每個服務 end points 都是可用
的), 你的整套微服務架構的可靠度就會更高。這些方法不是互斥的，有必要的話可以搭配使用。不論如何，讓 registry 手上隨時能維護一份可用的服務清單
是很重要的，先讓這些資訊正確，才有後面的 service discovery。


# 1, Service Discovery Patterns

Service Discovery 之所以重要，是因為它解決了 Microservices 最關鍵的問題: 如何精準的定位你要呼叫的服務在哪裡。不論你用哪一套服務來
提供 service discovery, 大致上都包含這三個動作組合成這個機制，分別是:

1. **Register**, 服務啟動時的註冊機制 (如前面所述)
1. **Query**, 查詢已註冊服務資訊的機制
1. **Healthy Check**, 確認服務健康狀態的機制

過程也很簡單易懂，大致上就是服務啟動時，自身就先去註冊，並且定時回報 (或是定時被偵測) 服務是否正常運作。讓 Service Discovery
維護一份正確的服務清單。因此這服務就能隨時接受查詢，回報符合其他服務期望的資訊。

其實觀念講起來非常簡單，拿一個大家都熟知，而且已經用了很久的例子: DNS + DHCP 就是個我知道最古早的例子。現在的人上網，不論你用有線還是
無線，大概就是網路接上就可以使用了。背後就是 DHCP + DNS, 這就是已經默默運作幾十年，最老資格的 Service Discovery 機制。

就從你的 PC 接上網路那一刻開始說明吧! 接上網路那瞬間，你的 PC 會廣播，詢問有誰能給它指派 IP address? 這時若區網內有 DHCP Server，就會
回報可用 IP 給 PC，雙方溝通完成就順利取得 IP 並且可以開始上網了。此時 DHCP server / PC client 也沒閒著，接下來就會跟 DNS 註冊，這 PC
的 host name 以及對應的 IP address (就是剛才 DHCP 分配的 IP)。不論是 PC client 主動跟 DNS 註冊，或是 DHCP server 分派 IP 時就
一起跟 DNS 註冊，總之這就已經完成上面講的第一個動作: register。

接著，網路上其他人怎麼找到這台 PC ? 很簡單，只要你知道這 PC 的名字 (host name) 就夠了。拿著 host name 到 DNS 去詢問，若登記有案的話，
DNS 就會回應正確的 IP address。若還要查詢服務的附加資訊，如其它註記，或是對應的 PORT 等等，DNS 也有 SRV 及 TXT record 可以對應。在
這階段就是前面提到的第二個動作: query。

當你要開始連線時，你可能會想先確認一下連線目標是否正常連線中? 最通用的方式，就是用 ping 這個指令來測試看看。ping 會送出封包，若 PC 有開啟
ICMP 的話，就會回應收到的封包。送出 ping 封包的一端收到回應 (echo), 就知道測試 PC 網路功能是正常的。這階段就是前面提到的第三個動作: health check。

微服務的 Service Discovery 其實也是一樣的原理，只不過不斷有新的做法來補 DNS 的不足而已。了解到這邊之後，接下來就來看看，常見的幾種
service discovery 機制是怎麼做的。這邊我推薦之前推薦過的 nginx ebook, 介紹一系列的 microservices 的參考架構與做法，其中一個章節
就是講到 service discovery patterns. 我節錄其中一段出來...

文章連結: [Service Discovery in a Microservices Architecture](https://www.nginx.com/blog/service-discovery-in-a-microservices-architecture/)



不論你用什麼方法，Service Discovery 想解決的問題情境，都可以用這張圖來表達:

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-1_difficult-service-discovery.png)

來回顧一下，已經運行數十年的 DNS 有哪些不足的地方? 在微服務架構下，我們預期內部的各個服務，都採取高度動態的前提進行部署。也許隨著流量的
變化，幾秒鐘之內就會有新的 instance 被啟動或是關閉，instance 的數量也可能從數十個到數千個不等。這種狀況下，DNS 無法有效的解決這幾個問題:

1. 服務清單精確度問題: DNS TTL 通常只到 hours 的等級
1. 無法很精準的判定服務的健康狀況
1. DNSRR (DNS round robin) 無法很精準的進行 load balance 或是 request routing

其實要做到上述的需求，DNS 也不是辦不到，但是你也必須額外建立其它的基礎建設，或是開發專屬的功能才能解決。在進行下去之前，我們就來看看
這篇文章介紹的幾種常見的 service discovery pattern(s):


# 2, The Client‑Side Discovery Pattern

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-2_client-side-pattern.png)

這種模式 (Client-Side Discovery Pattern) 的作法，主要是 client side 使用能跟 service registry 搭配運作的 Http Client (就是
圖中的 Registry-aware HTTP Client) ，在呼叫前先查詢好相關資訊，之後就可用來呼叫該服務的 REST API。Registry 會回報可用的服務 End Ponts
清單資訊，由 HTTP Client 自己決定要選擇哪一個 End Point.

## 優點:

那麼這種模式下，Load Balancing 通常是 Http Client 查詢服務的 end points 清單後，自己用自身的演算法，來從中挑選一個。好處是呼叫端可以
用最大的彈性來自訂負載平衡的機制，包含如何挑選最適當的 end point 等等。有時對服務等級要求很高的時候 (比如 VIP 要求有專屬的服務集群，或是
要有更精準的查詢方式等)，這個模式會更容易實作。

容易自訂化是這個方式的優點，另外 http client 通常也會做成 library 或是 SDK 的型態，直接引用到你的開發專案內，實際執行時這部分是
 in-process 的方式進行，語言間的整合程度最佳，執行效能也最佳，開發集除錯也容易，初期導入 service discovery 的團隊可以認真考慮這種模式。
有很多輕量化的 service discovery 也都採用這種模式。


## 缺點:

然而這也是這模式下的缺點。當這些調度的機制被控制在 client side, 往往也會有對應的風險。當這些機制要更新時，難以在短時間內同步更新，造成
有新舊的規則混雜在一起。因為這類 Registry-aware HTTP Client, 多半是以 runtime library 的形態存在，是用侵入式 (邏輯必須注入你的應用
程式中) 的方式存在於所有的 client 之間。要替換掉它，通常得重新編譯，重新部署服務才行。也因為它屬侵入式的解決方案，你也要確保你的專案開發
的技術或框架，有原生的 SDK or library 可以使用 (當然也得顧及到社群的生態，更新是否快速等等)。只是，對於服務調度邏輯這方面的隔離層級還
不夠，解耦也做的不夠，當你很在意這個部分時就得多加考慮。

> 侵入式: 代表這部分的邏輯，會以 source code, library 或是 component 等等的形式，"侵入" 到你的服務程式碼內。這種型態的置入，通常
> 能提供最佳的效能及功能性，也能提供最大的自訂化彈性。不過這也是缺點；意思是這置入的部分一但有任何修正，你的服務是必須經過 更新 > 重新
> 編譯 > 重新部署 這幾個步驟的，往往越通用的套件，要更新都是件麻煩事。採用侵入式的解決方案時，請務必考量到更新與重新部署時的挑戰。


## 案例:

Netflix Eurica




# 3, The Server-Side Discovery Pattern

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











# 5, 結論







































## service mesh: envoy, side car

Service Mesh, 其實在 NGINX 這系列文章內沒有提到，但是我自己很欣賞他的做法，因此我特地安插了這段，擺進來一起比較... 要了解什麼叫做 "service mesh" ?
看看這張意示圖就了解了:

![service mesh](/wp-content/uploads/2017/12/mesh3.png)

![side car](/wp-content/uploads/2017/12/service_mesh.png)


搞不清楚這張圖要表達的意義的話，搭配這段說明一起看:
出處: https://jimmysong.io/posts/what-is-a-service-mesh/

> A service mesh is a dedicated infrastructure layer for handling service-to-service communication. It’s responsible for the reliable 
> delivery of requests through the complex topology of services that comprise a modern, cloud native application. In practice, the service mesh is typically 
> implemented as an array of lightweight network proxies that are deployed alongside application code, without the application needing to be aware.

明白的講，service mesh 其實就是微服務負責處理 service to service 之間通訊的基礎建設。它可以用複雜先進的拓樸結構，可靠的把 request 傳遞給目的服務。
實務上，service mesh 通常會時做成輕量化的 network proxy, 跟每個服務一起部署。服務本身只要透過 proxy 就能聯繫到目的的服務，而不用理會通訊過程的細節。

補: 藉由這種架構，也容易對整個微服務的系統架構作監控，紀錄與管控等等任務。因為整個通訊的機制其實都由 service mesh 管控, 實作跟管理都相對容易的多；一對一的部署方式，也避開了
client-side discovery pattern 侵入式的部署方式，維運起來有更大的彈性與方便性。



優點:

優點是很顯而易見的；如果我們把每個 service node, 都擺一個該 instance 專屬的 load balancer, 呼叫端只要很無腦的把它要
呼叫其他 service 的 request, 轉交給專屬的 load balancer, 其他都不用煩惱了。服務之間的通訊細節與過程，對於服務的開發人員來說都是透明的，部署也非常容易，只需要在每個服務
所屬的 container or virtual machine, 同時搭配一個 service mesh node 即可。由於服務與 proxy 中間的通訊只是 local network 或是 IPC (inter procedure call)，跟你用的
是什麼開發技術並沒有太大關連。也因為如此，如果哪天 load balancer 的部分需要異動，也很簡單，這部分重新部署就好了，原本的服務完全不受影響。

服務之間的通訊該如何管理? service mesh 有足夠的資訊，做的比單純的 client side / server side discovery pattern 還更好；service mesh control panel 可以密切的監控與管理
整個 service mesh network 的運作狀況，聰明的調配服務間的溝通方式，達到整體效率的最佳化。這種層級的監控與管理，是前面介紹兩種模式遠遠不可及的。


缺點:

service mesh 的概念, 透過 side car 的方式, 把侵入式的運作邏輯這項大缺點給移除了, 在架構上完全達到兼顧 client-side / server-side discovery pattern 的優點；唯獨透過轉送，仍然
會造成依定程度的延遲，在效能及使用的資源上仍有些許程度的影響。


service mesh 是個很新穎與有深度的技術，算是新一代微服務架構的核心，以我的程度實在難以在短短的幾句話內就交代清楚，我在底下放幾個參考資訊連結，有興趣的朋友可以花點時間研究看看，
非常值得!

案例:

lyft: envoy








# Consul 使用案例示範

## 服務註冊 (via code / definition)

## 健康偵測

## 服務查詢

## 組態查詢

## DNS integration (NGINX)




--
UV










前面我一直在強調, 微服務並不是新技術，而是個架構設計的方針而已。實作上要用到的技術還是那些。然而要把一個服務拆分成數個獨立的服務，
考驗的不是開發技巧，而是考驗開發流程，以及你有沒有管理大量服務的能力。微服務化最明顯的衝擊，就是服務的數量變多了，同時服務的組態 
也從靜態變成動態的了。最基本要解決的問題, 就是如何找到你要存取的那個服務的 IP 及 PORT ? 這篇要探討的就是這些問題，當你的服務數量
變多且會隨時動態調整時，你該如何 "管理" 它? 如何很快地找到提供服務的 End Point? 如何掌握每個服務 instance 的清單? 如何掌握每個
服務的健康狀態? 這麼多服務，組態的管理該如何進行? Service Discovery 服務發現的機制就是解決方案。

然而 Service Mesh 又是什麼? Service Discovery 提供一系列註冊，健康偵測及查詢的機制，讓每個服務之間能找到彼此；而 Service Mesh
則是更進一步，用去中心化的機制，讓眾多服務能更快更有效率的找到最佳化的存取路徑，甚至可以進一步的中央控管與監控服務之間的通訊狀況。
這篇我就先不講太多實作，也不會太深入挖掘技術細節，我就只針對架構面來探討一下這兩個技術: Service Discovery / Service Mesh。
