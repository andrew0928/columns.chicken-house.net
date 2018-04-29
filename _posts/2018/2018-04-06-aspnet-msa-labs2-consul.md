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

其實我平常不大寫特定服務的介紹文章的，總覺得那些事實作面的東西，知道目的再去查文件會比較有效率，在那之前只要搞清楚架構及目的就可以了。不過在微服務的應用上，Service Discovery + Configuration Management 實在太重要了, 許多微服務的特性及優勢，都需要靠他才能做的好。於是這次，我就花了篇文章的版面，決定好好介紹一下 Consul (源自 HashiCorp 的解決方案) 這套服務。我拿去年介紹容器驅動開發用的案例: IP2C Service, 重新搭配 Consul 來改寫，用 Consul 解決 Service Discovery, Health Checking 以及 Configuration Management 的問題。讓各位讀者清楚的了解該如何善用 Consul 提供的功能，來強化你的服務可靠度。

這個範例的精神在於，微服務是個很龐大的架構，往往難以入門。也因為架構龐大，很多團隊都在片面的了解下就跨進來，一開始就累積了不少技術債而不自覺。其實很多事情本來就沒辦法一次到位的，不過就如我之前在 CICD 那篇文章提到的，至少團隊要先看清楚全貌，然後在初期就只針對最關鍵的地方顧好就好。其餘只要先把架構作對，實作通通都可以先行省略 (例如先留好 interface)，這樣整體的進展就會平順的多。

這次的實作案例，為了讓各位能關注核心，我把重點擺在搭配 Consul 與 Container 這兩件事情身上。若 Developer 不夠了解它，往往很多善用它就能解決的問題，developer 會選擇自己硬做...，這是很可惜的。因此我會把主軸擺在如何善用 Consul + Container 的應用方式，其它部份我會簡化 (自己用最少的 code 完成)，而不採用其它的 framework。因此在範例程式內，我刻意拿掉一些我常用的第三方套件，例如命令列的參數 Parser (一般我會用 CommandParser 這套件)、相依注入 (Dependency Injection, 一般我慣用 Unity)、Log (一般我會用 NLog + ELK) 等等，目的是讓不熟這些套件的朋友們也都能第一時間掌握重點。

<!--more-->

在上一篇 [容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/) 我拿 IP 地區查詢服務當作範例，用容器驅動開發的觀念，實作了微服務版本的 IP2C Service。我提到的 "Container Driven Development" 概念，就是假設你將來 "一定" 會用容器化的方式來部署的話，那麼在架構設計之初就能盡可能的最佳化，能透過容器解決的問題就不用自己做了。極度的簡化，可以讓 Operation 的團隊更容易接手維護你的服務，Developer 也能更專注把精力用在核心的業務上。這次我會重構先前的飯粒程式，進一步的擴大 "Container Driven Development" 的概念，假設將來 "一定" 會用 Consul + Container 的方式部署。同樣的來看看，你可以如何建構這樣的 application?

我會分成下列幾個主軸來進行這次 hands-on lab:

1. 該採用 IIS hosting? 還是 Self hosting?
1. 每個服務該如何做好: Service register / de-register, health checking ?
1. 每個服務該如何做好: Configuration management ?


這篇開發案例與實作，延續了前面幾篇文章的內容。建議看下去之前先看一看底下會用到的幾個重要觀念:

* [.NET Conf 2017 - Container Driven Development, 容器驅動開發](https://www.facebook.com/andrew.blog.0928/videos/509145696127380/)
* [容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/)
* [微服務基礎建設 - Service Discovery](/2017/12/31/microservice9-servicediscovery/)

所有微服務相關的文章，可以直接參考下列的導讀。

{% include series-2016-microservice.md %}





# Consul 能替我們解決那些問題?

可以開始進入重點了。開始寫 code 之前，先重點摘要一下，微服務架構一定會碰到的三大問題:

1. 橫向擴充 (scale out)
1. 服務可用性偵測 (health check)
1. 組態管理 (configuration management)

上一篇的例子，這些問題其實都被大幅簡化，直接用 container 內建的機制處理掉了。每個服務都被包裝成獨立的 container, 啟動時 docker compose 就會自動指派 IP 給該 container, 同時會更新 docker network 的 DNS, 增加一筆 A record, 因此你只需要拿 service name 到 DNS 查詢，就能找到該 service 有多少 container 被啟動 (同時也可以找到對應的 IP address)。不過透過 DNS 做 load balance, 往往只能用基本的 DNS Round Robin...

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


# 改版目標: 提高可用度, 快速擴充

我先定義一下這次改版的目標，搞清楚後再來思考架構。切勿一開始就埋頭苦幹，這樣你可能沒把精力用在最關鍵的地方。

所謂的 "提高可用度"，簡單的來說，就是我要盡一切可能的排除所有會讓服務中斷或是不正常的狀況。提高可用度有好幾種手段，其中之一就是多用幾個 instances 來分散風險，這個在上一版，透過 docker-compose 調整 scale 的做法就已經能達成了。剩下的問題在於，如果這些服務掛掉一半 (也就是沒有當掉，但是無法正常服務) 的話怎麼辦?

由於這些已經不是基礎建設層面，或是 operation team 的角度能解決的問題了，這必須是 develop team 才能掌握的細節，因此解決這問題之前，我們需要精準的 service discovery 來掌握所有可用的服務 instances, 同時必須搭配可靠的 health checking, 確保所有清單內的 instances 都是可用的。

另一個要求 "快速擴充"，其實也是搭配的機制之一。除了效能擴充之外，若 operation 已經有能力立即排除有問題的 instances 時，那麼 infrastructure 勢必也要有能力快速的調用新的 instances 來補足效能的缺口，這時就需要快速擴充的機制了。這邊的要求是，operation team 最多只需要決定需要擴充的數量，其它若需要任何額外的設定或是組態調整都是不允許的，因此 develop team 在設計相關功能時要盡可能的自動化。

所以，上面的目標，列成明確的 stories:

1. 維運人員只要啟動新的 container, 待啟動完成後新的 container 就能加入服務, 過程不需要額外的設定調整。
1. IP2C API 若無法正確回應 health checking, 則在 5 sec 內就必須自動被隔離，不再接收新的 request。若 60 sec 內都沒有恢復，則直接剔除該 instance。
1. IP2C API 若無法自動回報 heartbeats 訊號, 則在 5 sec 內就必須自動被隔離，不再接收新的 request。若 60 sec 內都沒有恢復，則直接剔除該 instance。
1. Configuration Change (改變資料檔案位置) 後, 所有的 IP2C API 服務須確保 5 sec 後收到的 request 都會用新的設定提供服務
1. 若外部服務 (IP2C 資料庫更新服務) 無法使用，必須在 service discovery dashboard 上看到狀態，同時 worker 的更新動作必須暫停執行


在上一篇的例子裡，只用 docker-compose 內建的功能, 大概只能很勉強的做到 (1), 不需要 developer 額外的介入或規劃。(2), (3), (4), (5) 就沒辦法了。要處理到這些環節，勢必得在架構上做額外的設計才行。這些都屬 [服務發現] 的範疇，在 service level 導入 service discovery 機制，就能有效的解決這些問題。先來看看架構上的設計改變:


![](/wp-content/images/2018-04-06-aspnet-msa-labs2-consul/2018-04-27-22-29-53.png)
> 原本的架構


![](/wp-content/images/2018-04-06-aspnet-msa-labs2-consul/2018-04-27-22-29-24.png)
> 調整過的架構

原本的架構，是靠 docker 內建的 DNS 機制來協調 API，透過 Reverse-Proxy 提供統一對外的 endpoint。調整後的架構，改用 Service Discovery 的服務來取代內建的 DNS。因此服務啟動及終止時，都必須主動跟 Service Discovery 更新狀態；Service Discovery 也必須定期的對已註冊的服務進行可用性確認 (health check)，以隨時確保可用的服務清單是正確的。

為了搭配這個機制，呼叫服務的用戶端也必須稍做調整。原本的架構直接透過 DNS 查詢可用的服務端，新架構就得改成用戶端必須事先查詢 Service Discovery 才能決定該呼叫哪個服務 instance。因為這已經超出標準 TCP/IP 規範的機制了，因此 Reverse-Proxy 的位置，我改成 Demo Client, 示範如何在 Code 內 (我寫在 SDK 內) 自行處理。

如果 Service Discovery 的註冊及健康檢查的機制，能夠透過設定或是 API 的方式手動調整，那麼我們也可以替外部或是既有 (legacy system) 主動加上去，在無法改寫既有的服務的前提下，我們一樣能用同樣的機制照顧好這些舊有的服務，讓所有的 client (透過 SDK) 或是其它服務都能精準的偵測到外部服務是否正常運作。

接下來，我們需要另一個 Configuration Management 的服務，來處理整個微服務架構內的設定管理。我們需要集中的地方來存放設定資訊，同時也需要這些設定有異動時，能主動通知所有需要被告知的服務端。

講到這邊，Consul 提供的功能完全符合我們的需要 (service discovery, health checking, KV store)。架構圖上的兩個綠色框框 (service discovery + health check, config manage) 就可以合併簡化成單一一個 Consul 服務了。接下來就一步一步調整程式，把這個架構建立起來。



# STEP 1, IIS Host or Self Host?

其實這個問題，我在上一篇 container driven development 時我就想講了，不過這個牽涉太多實作的問題，當時就忍下來了。現在是適合的時間了，我特地拿出來探討一下這個問題。

對開發人員來說，沒有太大的不同，你就是好好的開發 ASP.NET MVC WebAPI application 而已啊，只是你的 WebAPI 是掛在 IIS 下執行，還是自己開發的 Console App 下執行? 我節錄這討論串，它列出了使用 IIS 可以得到的額外好處 (相對於 SelfHost):

* [Self hosting or IIS hosted?](https://forums.asp.net/t/1908235.aspx?Self+hosting+or+IIS+hosted+)

What I've found (basically just pros for IIS hosted):
1. You lose all of the features of IIS (logging, application pool scaling, throttling/config of your site, etc.)...
1. You have to build every single feature that you want yourself HttpContext?
1. You lose that since ASP.NET provides that for you. So, I could see that making things like authentication much harder WebDeploy?
1. IIS has some nice specific features in 8 about handling requests and warming up the service (self-hosted does not)
1. IIS has the ability to run multiple concurrent sites with applications and virtual directories to advanced topics like load balancing and remote deployments.

其中 (2), (3) 我先略過，這個在開發階段就可以避免了，或是改用 Owin / .NET Core 就不存在的問題 (HttpContext)。其它都屬於部署管理方面的問題；如果你還在用傳統的方式部屬或是管理 web application (例如手動安裝 server, 內部系統, 沒有太多自動化, 同一套 server 可能執行多個 application 等等)，我會強烈建議你繼續使用 IIS。因為上述的功能對你都很重要。但是如果是 microservices, 以上的假設不大可能繼續成立了，你一定會被迫採用 container 這類能高度自動化的方式來進行。這時我們竹條來看看採用 IIS 的優點，是否還真的是 *必要* 的功能?


> You lose all of the features of IIS (logging, application pool scaling, throttling/config of your site, etc.)...

微服務架構下，幾乎都會搭配 container 及 orchestration 的機制一起使用。上述功能大多有替代方案，一次管理上百個 instances. 這時每個 instance 其實不再需要透過 IIS 提供這些功能了。


> IIS has some nice specific features in 8 about handling requests and warming up the service (self-hosted does not)

同樣的，application 的 life cycle 管理，也一樣可以透過 orchestration 搞定。更細緻的 health checking 等等，就是這篇會提到的。也都有對應更適合 microservices 的解決方案了。


> IIS has the ability to run multiple concurrent sites with applications and virtual directories to advanced topics like load balancing and remote deployments.

container 的精神，就是一個 process 一個 container, 在 run time 再組合成你期望的樣子。因此在一個 domain / ip address 上面放置多個 web sites 的需求，其實都會被轉移到前端的 reverse proxy, 後端每個 application 至少都有一個以上的 container 提供對應的服務。這任務都會轉由 orchestration 或是 reverse proxy 解決，對於每個 container 本身已經不是必要的功能了。








// problem in IIS with container

- IIS / windows service not suitable for containers
- container's life cycle (service) NOT match with application's life cycle (app pool), servicemonitor.exe
- container : app pool NOT 1:1



// IIS vs Self Hosting

- app pool / worker process
- fast fail problem (replaced by service discovery & health checking)
- extra modules / handlers, extra unnecessary functions & restricts (containers with reverse-proxy is better?)
- IIS logging is better (docker logging is better?)
- IIS with web garden is better scability (multiple container with orchestration is better?)
- selfhost performance is better (consider 1000+ containers)


// How To: SelfHosting?


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

// kv store v.s. DNS txt / srv records


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


