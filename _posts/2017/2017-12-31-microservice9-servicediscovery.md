---
layout: post
title: "微服務基礎建設 - Service Discovery"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "infra", "message queue", "api gateway", "service discovery"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/12/service-discovery.jpg
---

微服務系列文章停了幾個月，因為這系列的文章不好寫啊，很多內容有想法，但是沒有實做過一遍的話，寫出來的東西就只是整理網路上其他文章的觀點而以，那不是我想
做的 (這種事 google 做的都比我好)。經過這幾個月，自己私下 & 工作上又都累積了一些經驗，就又有素材繼續動筆了! 這次要補的是微服務必備的基礎建設之一: 服務註冊與發現機制 (Service Discovery)。

![](/wp-content/uploads/2017/12/service-discovery.jpg)

前面我一直在強調, 微服務並不是新技術，而是個架構設計的方針而已。實作上要用到的技術還是那些。然而要把一個服務拆分成數個獨立的服務，考驗的不是開發技巧，而是考驗
開發流程，以及你有沒有管理大量服務的能力。微服務化最明顯的衝擊，就是服務的數量變多了，同時服務的組態 (例如最基本的, 要從哪個 IP 跟 PORT 存取服務) 也從靜態變成動態的了。
這篇要探討的就是這些問題，當你的服務數量變多且會隨時動態調整時，你該如何 "管理" 它? 如何很快地找到提供服務的 End Point? 如何掌握每個服務 instance 的清單? 
如何掌握每個服務的健康狀態? 這麼多服務，組態的管理該如何進行? Service Discovery 服務發現的機制就是解決方案。


<!--more-->

{% include series-2016-microservice.md %}

--

# Service Discovery 的服務模式

架構類型的問題，最好都是先拋開實作的細節，先從問題處理的模式來思考，之後再來找合適的 solution 才不會走偏，否則很容易被特定的技術或是框架牽著鼻子跑。Service Discovery 這領域
的問題有幾種常見的解決方式，我分幾個段落先歸納整理一下，讓各位先搞清楚 Service Discovery 到底在做什麼。這個領域的服務很多，每個的用法又都不一樣，光是選擇 solution 這件事
就讓我吃盡苦頭。因此誠心建議各位，與其一開始就躁進要馬上裝一套來玩玩看的作法，在這邊是會踢到鐵板的，還是按部就班先了解一下 Service Discovery 葫蘆裡到底在賣什麼藥吧。

首先，我大推 NGINX 微服務系列的文章 (也有排版精美的電子書版本)。其中一個章節就把 Service Discovery 的概念講的很到位。我節錄裡面提到的幾種 Service Discovery 常見的服務模式:

文章連結: [Service Discovery in a Microservices Architecture](https://www.nginx.com/blog/service-discovery-in-a-microservices-architecture/)


不論你用什麼方法，Service Discovery 想解決的問題情境，可以用這張圖來表達:

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-1_difficult-service-discovery.png)

在微服務架構下 (假設你真的已經切割建置完成)，呼叫端 (可能是 API Gateway, 或是要呼叫某服務的其他服務 or Clients), 都會面臨這幾個問題，尤其是在這些服務的部署，都採取
高度動態的前提進行 (例如: 每個服務的 instance 數量會動態調整, 因此每個服務的 IP / PORTs 都會動態的指派) 的前提下更為困難:

1. 我如何知道服務在哪裡? 服務的 end point (ip address, service port) 為何?
1. 這個服務的健康狀況? (是否能正常提供服務? 負載是否正常?)
1. 該如何做負載平衡 (load balancing) ? 或是維持高可用性的運作 (high availability) ?


## DHCP / DNS

最傳統的方式，就是透過 DNS Round Robbin 以及 DHCP 的方式來進行。Server 開機或是接上網路後就跟 DHCP 取得 IP，然後跟 DNS 註冊。服務呼叫端要呼叫時就可以
到 DNS 查詢 (用 service host name)，如果存在一筆以上的 records, 就用輪流的方式傳回, 讓流量能夠分散。

不過這是很古早的做法了。在過去不是那麼高度動態變化的環境，這不失為一個簡便的方式，而且它實作在網路層，對於很多既有的服務是透明的，不需要任何改變就可以套用。
只是在很多進階的場景下，這套機制有很多限制，例如更新不夠及時 (DNS TTL, client cache), 沒辦法精準的處理 health check, 斷線偵測問題, 也無法精準的分配流量..
最後它是建立在 IP 的基礎上設計的，通常是以 server (vm) 為單位，要細緻到 service 以服務為單位，這架構就難以勝任了。

Docker Swarm / Docker Compose 內建支援 DNS support, 不過因為上述原因，DNS / DHCP 的搭配我只是單純介紹，實際上我不會把它納入評估清單中。

## The Client‑Side Discovery Pattern

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-2_client-side-pattern.png)

Service Discovery 的第一步，是每個服務被啟動後，自己要向服務註冊中心 (圖中的 Service Registry) 註冊，並提供自身的 End Point 等等資訊。之後其他人需要
調用這個服務的 API 時，就必須來 Service Registry 查詢。

Client-Side Discovery Pattern 的作法，就是 client side 使用能跟 service registry 搭配運作的 Http Client (就是圖中的 Registry-aware HTTP Client) ，在呼叫前
先查詢好相關資訊，之後就可用來呼叫該服務的 REST API。


優點:

那麼這種模式下，Load Balancing 是怎麼做的? 通常就是 Http Client 查詢服務的 end points 清單後，自己用自身的演算法，來從中挑選一個。好處是呼叫端可以最大化的
自訂各種機制，包含如何挑選最適當的 end point 等等。有時對服務等級要求很高的時候 (比如 VIP 要求有專屬的服務集群，或是要有更精準的查詢方式等)，這個模式會更容易實作。
容易自訂化是這個方式的優點，另外 http client 通常也會做成 library 或是 SDK 的型態，直接引用到你的開發專案內，實際執行時這部分是 in-process 的方式進行，語言間的
整合程度最佳，執行效能也最佳，開發集除錯也容易，初期導入 service discovery 的團隊可以認真考慮這種模式。


缺點:

然而這也是這模式下的缺點。當這些調度的機制被控制在 client side, 往往也會有對應的風險。當這些機制要更新時，難以在短時間內同步更新，造成有新舊的規則混雜在一起。因為這類
Registry-aware HTTP Client, 多半是以 runtime library 的形態存在，是用侵入式的方式存在於所有的 client 之間。要替換掉它，通常得重新編譯，重新部署服務才行。也因為它
屬侵入式的解決方案，你也要確保你的專案開發的技術或框架，有原生的 SDK or library 可以使用 (當然也得顧及到社群的生態，更新是否快速等等)。只是，對於服務調度邏輯這方面的
隔離層級還不夠，解耦也做的不夠，當你很在意這個部分時就得多加考慮。


案例:

Netflix Eurica




## The Server-Side Discovery Pattern

![](/wp-content/uploads/2017/12/Richardson-microservices-part4-3_server-side-pattern.png)

既然有前面講到的 "Client-Side" discovery pattern 的存在，自然也有對應的 "Server-Side" discovery pattern... 很直覺的，就是把原本 client side 執行的 registry-aware http client 這部分拆出來，變成一個專屬的服務；對的，就是圖上標示的 "LOAD BALANCER"。

這裡的 Load Balancer 不一定是一般常聽到的 Hardware Load Balancer, 也不一定是常見的 Software Load Balancer (如 NGINX, HA-Proxy 等)。就算自行開發的也行，重點在於這個 LB
必須是 "registry aware" 的... 它必須能搭配 service registry 提供的資訊，做正確的判讀，回應正確的資訊給 client, 或是直接扮演 reverse proxy, 直接替 client 轉送對應的 request,
給後端適當的 service instance.




優點:

相較於 client-side discovery pattern, 優缺點其實也很明確, 這種做法的好處, 就是 service discovery 這件事, 對於 client side 來說是透明的, 在他眼裡就只有 load balancer 而已。
所有細節都被隔離在 load balancer 跟 service registry 之間了。沒有侵入式的 code 存在 client side, 因此也沒有前述的 language, library maintainess 等相關問題, 更新也只要統一
部署 load balancer & service registry 就足夠了。

缺點:

缺點也是很明顯，這樣一來，服務的架構等於多了一層轉送了 (load balancer 的角色就如同 reverse proxy)。多了一層服務，延遲時間會增加；同時整個系統也多了一個故障點，整體系統的維運難度
會提高；另外最關鍵的，load balancer 可能也會變成效能的瓶頸。想像一下，如果整套 application 存在 N 種不同的服務，彼此都會互相呼叫對方的服務，那麼所有的流量都會集中在 load balancer 身上。

這樣的任務，很容易跟微服務架構下其他的基礎建設混在一起。例如 service registry 跟 load balancer 的整合, 可能救導致兩者合而為一套服務了；再者, 轉送 (forward) 前端的服務請求 (request)，這角色要做的事情又跟 API gateway 高度的重疊，然而 API gateway 還有其他它要解決的問題啊，最終可能會演變到這些服務，重複出現好幾次 (前端有 API gateway, 後端有另一套 load balancer, 或是每組服務都有自己的 load balancer 等等)。如果你的規模不夠大，可能你還沒享受到它帶來的好處，你就先被它的複雜度與為運成本給搞垮了...。

回想一下，微服務化的最初用意，有這麼一項: 故障隔離，將整個系統切割為多個服務共同運作，若有某個服務無法正常運行，那麼整個應用系統只需停用部分功能，其他功能要能正常運作。這樣做的
方向就是要去中心化，不過 server side discovery pattern 就是集中式的做法啊.. 去中心化的作法，後面在更極致的 service mesh 我會再進一步說明...。



案例:

AWS Elastic Load Balancer (ELB)



## service mesh: envoy, side car

Service Mesh, 其實在 NGINX 這系列文章內沒有提到，但是我自己很欣賞他的做法，因此我特地安插了這段，擺進來一起比較... 要了解什麼叫做 "service mesh" ?
看看這張意示圖就了解了:

![service mesh](/wp-content/uploads/2017/12/mesh3.png)

先排除要對外的 public API, 先只考慮內部眾多 (micro)services 之間相互的 API 調用，client-side discovery pattern 其實做的比較好；它能真正做到如這張圖所示的點對點架構，
每個呼叫都是直連，沒有任何一絲浪費；然而它的缺點是侵入式的 service discovery。

我們試著想一想: 如果結合 server-side 跟 client-side 的做法會如何? 我們把每個 service 都跟一個 load balancer 一對一的搭配 (就是所謂的 side car 模式) 接著來看看這張圖:

![side car](/wp-content/uploads/2017/12/service_mesh.png)

優點:

優點是很顯而易見的；如果我們把每個 service node, 都擺一個該 instance 專屬的 load balancer, 呼叫端只要很無腦的把它要
呼叫其他 service 的 request, 轉交給專屬的 load balancer, 其他都不用煩惱了。由於這是 process 層級的隔離，中間的通訊只是 local network 或是 IPC (inter procedure call)，跟你用的是什麼開發技術也沒有太大關連了。也因為如此，如果哪天 load balancer 的部分需要異動，也很簡單，這部分重新部署就好了，原本的服務完全不受影響。


缺點:

service mesh 的概念, 透過 side car 的方式, 把侵入式的運作邏輯這項大缺點給移除了, 在架構上完全達到兼顧 client-side / server-side discovery pattern 的優點；唯獨透過轉送，仍然
會造成依定程度的延遲，在效能及使用的資源上仍有些許程度的影響。


案例:

lyft: envoy



## The Self‑Registration Pattern

## The Third‑Party Registration Pattern


# 其他的模式

## The Service Registry (調整順序，放在最後面介紹)

* etcd
* consul
* zookeeper
* dhcp / dns !!!


# Consul 使用案例示範

## 服務註冊 (via code / definition)

## 健康偵測

## 服務查詢

## 組態查詢

## DNS integration (NGINX)