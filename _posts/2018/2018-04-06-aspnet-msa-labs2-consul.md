---
layout: post
title: "容器化的微服務開發 #2, 微服務基礎建設 Consul 使用範例"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps", "Service Discovery", "Consul"]
published: true
comments: true
redirect_from:
logo: 
---

[上一篇: 容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/) 我拿 IP 地區查詢服務當作範例，用我講的容器驅動開發的觀念，實作了微服務版本的 IP2C Service。微服務化一定會用到的 scale out 機制，我在這個範例使用 docker 內建的 DNS + 自行建置的 nginx (reverse proxy) 就處理掉了。不過當服務架構越來越複雜時，僅只靠內建的 DNS 難以負擔重責大任啊! 這篇我就把整個基礎建設，改用 Hashicorp 的開源專案: Consul 重新搭建一次這個服務吧! 這次我們來看看更精準的 Service Discovery + Healthy Check, 還有集中式的 Key-Value Configuration Management 能替我們解決多少微服務基礎建設的問題。

<!--more-->

開始之前，複習一下先前的內容吧~ 建議先看一下我在 .NET Conf 2017 介紹的 Container Driven Development 的觀念，還有上一篇的實作 Labs 說明。接著再看這篇如何進一步善用 Consul 的機制來簡化整個系統架構。

**STEP 1**. 先看這段 .NET Conf 2017: Container Driven Develop  
<iframe src="https://www.facebook.com/plugins/video.php?href=https%3A%2F%2Fwww.facebook.com%2Fandrew.blog.0928%2Fvideos%2F509145696127380%2F&show_text=1&width=560" width="560" height="685" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowTransparency="true" allowFullScreen="true"></iframe>  
  

**STEP 2**. 複習一下只用 container 提供的基礎建設: [容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/)


**STEP 3**. 複習一下服務發現 (Service Discovery) 在做什麼: [微服務基礎建設 - Service Discovery](/2017/12/31/microservice9-servicediscovery/)


{% include series-2016-microservice.md %}


# Consul 能替我們解決那些問題?

先重點摘要一下，微服務架構一定會碰到的三大問題:

1. 負載平衡 (load balance)
1. 服務可用性偵測 (health check)
1. 組態管理 (configuration management)

上一篇的例子，這些問題其實都簡化了，直接用 container 內建的機制處理掉了。每個服務都被包裝成獨立的 container, 啟動時 docker compose 就會自動指派 IP 給該 container, 同時會更新 docker network 的 DNS, 增加一筆 A record, 因此你只需要拿 service name 到 DNS 查詢，就能找到該 service 有多少 container 被啟動 (同時也可以找到對應的 IP address)。不過透過 DNS 做 load balance, 往往只能用基本的 DNS Round Robin...

至於可用性偵測，我們則暫時假設 container 活著，就代表服務可用，因此也可以從 DNS 查詢得知。若超出此範圍 (例如: 服務當掉了，但是 container 還在 running 狀態) 則無法因應。

最後，組態的管理，只能透過 container 的 environment 來指派；一旦 container 啟動後要變更，就得 restart container 才辦的到。如果是透過共用檔案 (mount volume) 的話，那只能自己寫 code 監控檔案異動。

這些需求若只用內建的 docker-compose 提供的功能，都只是點到為止，當你想做精準一點的控制時就顯得力不從心了。這時找個專門的服務來彌補這些缺口，是個明智的決定。其實這類 solution 還蠻多的，我沒辦法每個都介紹，我就介紹一個我自己有在用的: [Consul](https://www.consul.io/)。


介紹文我就懶得自己打了，先節錄一下[官網的說明](https://www.consul.io/intro/index.html#what-is-consul-):

----

**What is Consul?**
Consul has multiple components, but as a whole, it is a tool for discovering and configuring services in your infrastructure. It provides several key features:

**Service Discovery**: Clients of Consul can provide a service, such as api or mysql, and other clients can use Consul to discover providers of a given service. Using either DNS or HTTP, applications can easily find the services they depend upon.

**Health Checking**: Consul clients can provide any number of health checks, either associated with a given service ("is the webserver returning 200 OK"), or with the local node ("is memory utilization below 90%"). This information can be used by an operator to monitor cluster health, and it is used by the service discovery components to route traffic away from unhealthy hosts.

**KV Store**: Applications can make use of Consul's hierarchical key/value store for any number of purposes, including dynamic configuration, feature flagging, coordination, leader election, and more. The simple HTTP API makes it easy to use.

**Multi Datacenter**: Consul supports multiple datacenters out of the box. This means users of Consul do not have to worry about building additional layers of abstraction to grow to multiple regions.

Consul is designed to be friendly to both the DevOps community and application developers, making it perfect for modern, elastic infrastructures.

----

我只能說，開發 Consul 的團隊，把它的關鍵功能拿捏得很好。這些功能不多不少，剛剛好都是我在建構微服務時最在意的基礎建設。微服務考驗的就是你治理大量服務的能力啊，就 "治理" 本身，需要的功能恰恰好就是上面提到的四個。搞清楚 Service Discovery / Health Checking 在做什麼，就是上一篇介紹的。至於應用與架構的規劃，我後面再說。接下來直接先看 Labs 應用案例吧。


# Case Study: IP 查詢服務 (進階版)

先前的版本，完全沒有針對可用性做進一步的規劃。在主要功能維持不變的前提下，要追加下列提高可用性的架構面需求。主要目標有:

1. 要能動態 (不中斷服務) 新增或是移除服務 instances  
1. 要能應付 api service fail 的狀況，服務掛掉的 1 sec 內要能自動隔離失敗的 instance  
1. 要能應付 configuration change (改變資料庫檔案版本)
1. 要能確認外部服務 (例: IP資料庫下載) 是否可用

在上一篇的例子裡，只用 docker-compose 內建的功能, 大概只能很勉強的做到 (1), 不需要 developer 額外的介入或規劃。(2), (3), (4) 就沒辦法了。要處理到這些環節，勢必得在架構上做額外的設計才行。這些都屬 [服務發現] 的範疇，在 service level 導入 service discovery 機制，就能有效的解決這些問題。先來看看架構上的設計改變:


![](/wp-content/images/2018-04-06-aspnet-msa-labs2-consul/2018-04-27-22-29-53.png)
> 原本的架構



![](/wp-content/images/2018-04-06-aspnet-msa-labs2-consul/2018-04-27-22-29-24.png)
> 調整過的架構

原本的架構，是靠 docker 內建的 DNS 機制來協調 API，透過 Reverse-Proxy 提供統一對外的 endpoint。調整後的架構，改用 Service Discovery 的服務來取代內建的 DNS。因此服務啟動及終止時，都必須主動跟 Service Discovery 更新狀態；Service Discovery 也必須定期的對已註冊的服務進行可用性確認 (health check)，以隨時確保可用的服務清單是正確的。

為了搭配這個機制，呼叫服務的用戶端也必須稍做調整。原本的架構直接透過 DNS 查詢可用的服務端，新架構就得改成用戶端必須事先查詢 Service Discovery 才能決定該呼叫哪個服務 instance。因為這已經超出標準 TCP/IP 規範的機制了，因此 Reverse-Proxy 的位置，我改成 Demo Client, 示範如何在 Code 內 (我寫在 SDK 內) 自行處理。

如果 Service Discovery 的註冊及健康檢查的機制，能夠透過設定或是 API 的方式手動調整，那麼我們也可以替外部或是既有 (legacy system) 主動加上去，在無法改寫既有的服務的前提下，我們一樣能用同樣的機制照顧好這些舊有的服務，讓所有的 client (透過 SDK) 或是其它服務都能精準的偵測到外部服務是否正常運作。

做了這些調整，基本上上述的需求，就已經能解決 (1) (2) (4) 這三項了。接下來，我們需要另一個 Configuration Management 的服務，來處理整個微服務架構內的設定管理。我們需要集中的地方來存放設定資訊，同時也需要這些設定有異動時，能主動通知所有需要被告知的服務端。作法我後面在介紹，若假設這些機制也都能成功執行的話，那麼我們就能進一步解決 (3) 的問題。


講到這邊，Consul 提供的功能完全符合我們的需要 (service discovery, health checking, KV store)。架構圖上的兩個綠色框框 (service discovery + health check, config manage) 就可以合併簡化成單一一個 Consul 服務了。接下來就一步一步調整程式，把這個架構建立起來。







# STEP 0, IIS or SelfHost?

最基本的就是服務註冊機制了。為了確保服務的清單正確性 (先忽略服務不正常終止的狀況)，我們必須在服務啟動即結束時通知 Consul。尷尬的是，在 windows 的架構下，ASP.NET MVC application 預設是掛在 IIS 以下的，整個服務的過程中，ASP.NET 的生命週期是受到 IIS 的管控的。IIS 會視情況來決定該如何管理 ASP.NET app pool；例如:

* 延遲啟動: 在第一個 request 進來之後才啟動 app pool
* 回收: 經過一段時間 (預設 20 分鐘) 沒有任何 request, IIS 會選擇回收 app pool, 節省資源；直到下一個 request 進來，IIS 會啟動新的 app pool 來服務它
* 失敗回復: 若 IIS 偵測到某個 app pool 運作出了問題，IIS 會另外啟動一個新的 app pool, 由他來受理之後收到的 request, 原本的 app pool 則會嘗試正常終止，若經過一段時間還無法終止，則會強制停掉 app pool
* 定期回收: 透過排程，定期執行 "回收" 的動作

其實這些機制，對於 IIS server 的可用性有很大的幫助，早期我們自己管理 server 的情況下，這些機制真的能很有效的運用 server 上的資源，也真的能提高服務的可靠度，讓一些設計上不是那麼嚴謹的 application, 也能有最好的可靠度。不過，在一切都容器化的環境下，這些機制反而變的很累贅，多此一舉了。我隨便舉幾個在 container 的環境下，這類 "脫褲子放屁" 的例子:

IIS 是 windows service, 開機啟動，關機才停用，屬於很標準的背景服務。不過 container 的生命週期是跟著主要的 process 啊，container 啟動後，會執行 entrypoint 當作主要的 process, 當她結束就會停止整個 container。這兩個放在一起很矛盾啊，container 啟動後，到底要啟動什麼東西 (IIS 不用透過 container 就會執行了)?  另外 container 到底要等哪個 process 結束才能停止? 沒有 entrypoint, container 一啟動就會結束了... Microsoft 為了解決這個問題，只好開發了一個工具: ServiceMonitor.exe .. 它執行後就會一直掛在那邊，不斷的監控指定的服務 (IIS) 是否還在執行中? 如果服務停止了，那麼 ServiceMonitor.exe 也會停止。拿它來當作 container entrypoint 就可以解決上述問題了。

不過整個過程就是一整個怪啊，多了很多多於的動作... 我接著再舉幾個 IIS 在 containerize app / microservices 下很多餘的案例:

前面提到的服務註冊/移除，本來很單純的只要在這個 process 的頭尾加一段 code 通知 consul 就好了，現在變得很複雜了，因為 IIS 的關係，可能 container 已經起來了，但是我們的 app pool 根本沒有起來 (因為沒有觸發它的 request).. 當然我們可以寫個 script 做這件事，或是 IIS 自己也有設定可以做這件事，但是這麼一來 IIS 存在的理由又少了一個...

如果我們在 app pool 啟動與停止 (對應到 ASP.NET Global.asax 內的 Application_Start / Application_End 的事件) 通知 consul 執行 service register / de-register 的動作的話，前面說到 IIS 的一些題高可用性的設計，就會干擾 consul 的運作了...

另外，在微服務架構下，通常這些服務都不會直接對外的，要對外都會透過 API gateway, Reverse proxy 或是 Edge service, 因此 IIS 很多功能 (例如權限，整合試驗證, mime-type 控制, ... 等等功能，完全被前端的 reverse-proxy 給取代了...

怎麼看都覺得 IIS 在容器化的時代是個很多餘的東西啊，就算你真的需要，只要在 Edge service 架個 IIS 或是 Nginx 當作 reverse proxy, 就一切搞定了。你依樣可以在這個位置啟用你想要的功能，而不用在背後每個 instance 都裝一套 IIS 執行一樣的功能...


於是，在這個範例我大膽地做了點改變，我決定不用 IIS 來 hosting ASP.NET MVC WebAPI application, 改用自己開發的 Self Hosting Console App 來替代 IIS，同時由這個 Self Host App 來負責 Consul 的 Reg / DeReg 等任務，API 本身要執行的商務邏輯，維持在 ASP.NET 裡面處理舊好。



# STEP 3, Health Checking






# STEP 4, Consul Aware SDK





# STEP 5, DEMO




# STEP 6, ADD EXTERNAL SERVICE into Health Checking



# STEP 7, WORKER update datafile



# STEP 8, Configuration Management With Consul




# STEP 9, DEMO













// tools query SD, call IP2C
// IP2C.API reg / dereg with SD
// SD do health check every sec
// IP2C.Worker update new version of data file, update config to SD
// SD notify every IP2C.API, update





1. webapi: 從 IIS hosting 改為 self hosting.
  1. 強化效能, selfhosting 效能遠高於 IIS hosting
  1. 更符合容器使用方式, windows service 反而不適合容器的生命週期。Microsoft 甚至為了讓 windows service 適合在容器運作，額外開發了 servicemonitor.exe, 有點多此一舉。
  1. 改用 self hosting 更適合啟動時自動執行 registry, 結束時自動執行 de-registry
1. worker 要能自動偵測來源網站是否可連線
1. 統一透過集中管理的設定來決定要使用的資料庫版本
1. 透過 IP hash 自動選用 webapi instance





## 服務註冊

## 服務健康偵測

## 服務查詢

## 組態管理

// 作用中的 IP 資料庫檔案

// 事件通知: IP資料庫檔案切換通知
// 事件通知: JOB手動啟動通知
// LOCK

// consul-template

## SDK 封裝

## 成果驗收

// 動態切換 IP 資料庫

// 在非計畫時間啟動 JOB

// 高附載測試



# 結論

// 如何進階到 service mesh ?

// legacy system support? using consul DNS

// health check for external services?

// health check for legacy services?

// compare to other service discovery services?


