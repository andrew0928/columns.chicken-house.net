---
layout: post
title: "容器化的微服務開發 #2, API Service 容器化的選擇: IIS or Self Host ?"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps", "Service Discovery", "Consul"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2018-04-06-aspnet-msa-labs2-consul/how_would_you_solve_the_icing_problem.png
---


在微服務的應用上，[service discovery](/2017/12/31/microservice9-servicediscovery/) 實在太重要了, 許多微服務的特性及優勢，都需要靠他才能做的好。於是這次我就花了篇文章的版面，決定好好介紹一下 [Consul](https://www.consul.io/) (源自 [HashiCorp](https://www.hashicorp.com/) 的解決方案) 這套服務。我拿去年介紹容器驅動開發用的案例: [IP2C Service](/2017/05/28/aspnet-msa-labs1/), 重新搭配 consul 來改寫，用 consul 解決 service discovery, Health Checking 以及 Configuration Management 的問題。讓各位讀者清楚的了解該如何善用 Consul 提供的功能，來強化你的服務可靠度。

![](/wp-content/images/2018-04-06-aspnet-msa-labs2-consul/how_would_you_solve_the_icing_problem.png)

不過在開始之前，我想了很久，決定先追加這篇。在其他平台上，微服務有類似 [Spring Cloud](http://projects.spring.io/spring-cloud/) 這樣一整套的 framework / toolset 可以參考，然而 .NET 這塊的選擇就少的多。雖然仍然有很多 framework 可以選擇，不過都還在百家爭鳴的階段，同時容器化的部署相較之下也還沒那麼到位 (windows container 才一歲多)。團隊如果採用 .NET 同時又打算在這時間轉移到微服務架構，最好都要先對這些基礎建設能有較高的掌握度。因此，搭配上一篇講到 [CDD](https://www.facebook.com/andrew.blog.0928/videos/509145696127380/) (Container Driven Development) 的概念與實作，我決定在這篇文章裡示範一下怎麼自己把這些缺口補起來。這樣做的目的，不是要你拿去用在 production 環境上，而是體驗過之後你會更清楚怎麼選擇，也能在初期就做好抽象化，降低將來轉移的風險。

你有想過你的 API service 該怎麼封裝成容器嗎? 掛在 IIS 下執行，還是用 Self Host ? Docker 是從 Linux 上面發展起來的，對於上面的服務反而沒太多這類的問題；不過長年在 Windows 環境下的開發者都被 Microsoft 照顧得好好的，要妥善運用 Docker / Windows Container 反而就沒辦法那麼得心應手。我強烈建議每個有心使用 windows container 的團隊能夠看一下這篇，試著從無到有親手跑過一次，了解整個容器化的過程。即便往後很多東西都會有現成的解決方案，找機會讓自己的團隊體驗一下重新造輪子的過程絕對有幫助的。




<!--more-->

雖然微服務跟容器化是兩回事，不過兩者搭配起來是絕佳組合啊，所以我決定先花點篇幅，先搞定 web api 容器化的問題 (self-host or IIS host)。過去都是 operation team 解決掉了，不需要 development team 傷腦筋。現在微服務需要更密切的整合，必須要同時能掌握 development 跟 operation 的 know how, 才能正確的拿捏該捨掉那些東西。這篇就是從這角度，告訴你 IIS 與 Self Host 該如何取捨。我先說明一下採用 Self-Host 的考量，同時也會示範一下如何開發一個通用的 Self-Host class library, 微服務的應用上，你勢必會有很多大量的服務需要開發，先把這個通用的 Self-Host 架構搞定，加上與 consul 的整合，可以替整個團隊省下不少功夫。

在上一篇 [容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/) 我拿 IP 地區查詢服務當作範例，用容器驅動開發的觀念，實作了微服務版本的 IP2C Service。我提到的 "**C**ontainer **D**riven **D**evelopment" 概念，就是假設你將來 "一定" 會用容器化的方式來部署的話，那麼在架構設計之初就能盡可能的最佳化，能透過容器解決的問題就不用自己做了。極度的簡化，可以讓 Operation 的團隊更容易接手維護你的服務，Developer 也能更專注把精力用在核心的業務上。這次我會重構先前的範例程式，進一步的擴大 "Container Driven Development" 的概念，假設將來 "一定" 會用 consul + container 的方式部署。同樣的來看看，你可以如何建構這樣的 application?

建議看下去之前先看一看底下會用到的幾個重要觀念:

* [.NET Conf 2017 - Container Driven Development, 容器驅動開發](https://www.facebook.com/andrew.blog.0928/videos/509145696127380/)
* [容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/)

所有微服務相關的文章，可以直接參考下列的導讀。

{% include series-2016-microservice.md %}


# IIS Host or Self Host?

其實這個問題，我在上一篇 container driven development 時我就想講了，不過一直拖到現在。我特地拿出來探討一下這個問題，因為這個決策，會直接影響到後續 (下一篇) 如何跟 Consul 做後續的整合方式，不可不慎。因此我把他擺在第一個步驟。

對開發人員來說，選擇 IIS 或是 Self Host 其實沒有太大的不同，你就是好好的開發 ASP.NET MVC WebAPI application 而已啊，只是你的 WebAPI 是掛在 IIS 下執行，還是自己開發的 Console App 下執行? 在執行階段或是部署階段，考量的方向有幾個:

1. 架構考量: IIS 是 windows service, 與 container 是以 process 為主的模式有出入，要配合 container 的生命週期管理較困難 (後敘)
1. 環境考量: IIS 提供完整的 web hosting 環境，可提供很多不需要自己開發就有 web site 必要功能 (後敘)
1. 效能考量: Hosting 再 IIS 下需要花費較多系統資源，但是也可能因為較佳的資源管理而受益 (後敘)

接下來我就分別就這三個方向，分享一下我自己的看法。這些只是優劣的判斷，並非絕對的選擇，各位採納前還是要評估自己的狀況再決定。

> 有些解決方案，例如 asp.net core 提供的 kestrel, nancy fx, 或是之前 .net framework 的 cassini dev server, 都是介於 IIS 與 self-hosting 的中間解決方案。這類方案我會把他當作其它的 open source project, 把 self-hosting 的功能做好給你直接使用而已。在以下的討論內，kestrel 這種 solution 我會把他歸在 self-hosting 那一類看待。

* [ASP.NET Core Web Servers: Kestrel vs IIS Feature Comparison and Why You Need Both](https://stackify.com/kestrel-web-server-asp-net-core-kestrel-vs-iis/)


## STEP 1, 架構考量

這裡指的 "架構考量"，其實就是指 windows service 跟 console application 運作方式的不同。因為這些差異，連帶的影響到容器化的作法。因為落差實在太大，我覺得有必要在一開始就考量清楚。

簡單的說，container 的生命週期，是依附在 entrypoint 指定的 process .. container start, 就會啟動該 process... 直到該 process 執行結束，container 就會自動停止 (stop) 執行，結束整個 container 的生命週期。

這邊對於 ASP.NET 的開發者來說，有兩個很頭痛的地方:

1. IIS 是 windows service, 無法指定為 entrypoint
1. ASP.NET 的生命週期又跟 IIS 不同，中間還卡一層 APP POOL (受 IIS 管理調度)

這些差異會導致 dockerfile 很難寫，除此之外，下一篇要講到的 service discovery with consul, registry & de-registry service 的時間點非常難掌握。我簡單畫兩張 time diagram 來說明比較清楚:


**IIS host**:

![](wp-content/images/2018-05-12-msa-labs2-selfhost/2018-05-17-17-42-57.png)

這張是目前 Microsoft 官方提供的 ASPNET container image 為基礎，我把啟動到結束的過程畫成 time diagram 。由左到右是時間，每個藍色的 Bar 代表一個 process, 下列的敘述中的 (n) 就代表圖內的綠色數字。IIS 有良好的 app pool management 能力，每個 asp.net application 都會在 app pool 內執行。IIS 啟動之後，會等到第一個 http request (1) 進來後才會啟動該 web application (2)。這時定義在 asp.net global.asax 內的 application_start event (3) 就會被觸發。App pool 有各種情況可能會被回收或是終止(4) (如 idle 超過指定時間，使用資源如 CPU 或是 MEMORY 超過限制等等)，這時會觸發 application_end event (5), 等待下一個 http request, 或是主動啟動另一個新的 app pool 來替代。

較特別的是為了配合 docker 的規定 (必須指定一個 entrypoint process), Microsoft 提供了 ServiceMonitor.exe 會監控 IIS (w3wp.exe) 執行狀況，若 IIS 停止服務，則 ServiceMonitor.exe 也會跟著終止，這時 container 就會跟著進入 stop 狀態。


這樣的設計，對於絕大部分的 web application 都能很正確的運作，沒有什麼大問題。這也是 Microsoft 官方提供給所有 developer 的用法，你只需要把你的 asp.net application 在 build image 時，放到 c:\inetpub\wwwroot 就大功告成，直到我要拿這個方式示範 microservices 的 service discovery 機制時才碰到釘子...


**架構上難以解決的問題**:

這個架構，麻煩的地方在於，developer 對整個 service 的運作控制能力非常有限；影響最大的部分在於 developer 無法很精準的掌控 container 啟動與結束執行的時間點。要能掌握這兩個時間點，才能正卻的跟 service discovery 註冊與反註冊服務資訊啊!

第一個問題，在於圖中的 application start / end events, 在同一個 container 內可能被觸發多次，甚至可能有多個 app pool 平行運行。這會影響註冊資訊的正確性。

第二個問題，在於 app pool 必須等到外來的 http request 進來後才會啟動，然後才會觸發 application start event；但是實際的狀況是，我們必須先到 service discovery 機制去註冊，才有可能有 http request 進來啊，這是互相衝突的兩個期望，不可能同時滿足。(雖然這可以透過調整 IIS config 改變，不過這卻不是預設行為)


**Self host**:

如果換個角度，我們跳出 IIS 的框架，改用 self host 的角度重新思考這問題的話...

![](wp-content/images/2018-05-12-msa-labs2-selfhost/2018-05-17-21-25-51.png)

整個處理程序都變的超級簡單了啊，就是單一一個 process, 直接指定為 docker container 的 entrypoint, 能夠很精準的讓開發人員掌握 start / end 的時間點；同時只有一個 process, 也沒有多個 app pool 同時並行的困擾。至於原本 IIS 幫我們做的 app pool / resource management 呢? 這交給 container orchestration 統一管理就好了啊 (下一段說明)。


**架構考量的結論**:

因此，在架構上的考量，放棄 IIS host, 改用 Self host 有他的優點。

這些問題的起點，都在於 container 適合封裝 process, 但是 IIS 是 windows service, 兩者先天的運作模式就有很大的差異。在過去廿幾年來，這種模式在 windows 一直運作得很好，直到 docker 的盛行... 如果你要封裝的主要服務，是以 windows service 的形態存在，這就變得多此一舉 (例如此案例的 ServiceMonitor.exe)。其實透過 docker 的協助, console application 就能表現的跟 windows service 幾乎一模一樣的效果了。你只要用 docker run -d --restart always .... 來啟動你的 container, 它就完全是個 windows service 了 (還不需要註冊)。只要你的 console application 有好好的處理 OS shutdown event (或是 unix 系列的 signal), 你一樣能完美的透過 docker start / stop / pause / unpause 指令來操作 (對應到 windows service 的 start / stop / pause / continue)。

接著看一下 Microsoft 提供的 [IIS](https://hub.docker.com/r/microsoft/iis/) container image, [dockerfile](https://github.com/Microsoft/iis-docker/blob/master/windowsservercore-1709/Dockerfile) 是怎麼寫的:

```dockerfile

# escape=`
FROM microsoft/windowsservercore:1709

RUN powershell -Command `
    Add-WindowsFeature Web-Server; `
    Invoke-WebRequest -UseBasicParsing -Uri "https://dotnetbinaries.blob.core.windows.net/servicemonitor/2.0.1.3/ServiceMonitor.exe" -OutFile "C:\ServiceMonitor.exe"

EXPOSE 80

ENTRYPOINT ["C:\\ServiceMonitor.exe", "w3svc"]

```

就如同前面說明，主要就是靠 c:\ServiceMonitor.exe 來串聯 windows service 跟 container 的生命週期而已。Microsoft 前陣子也將這個公具直接 open source 了:

https://github.com/Microsoft/IIS.ServiceMonitor

直接看它的說明:

-----

Microsoft IIS Service Monitor

**ServiceMonitor** is a Windows executable designed to be used as the entrypoint
process when running IIS inside a Windows Server container.

ServiceMonitor monitors the status of the `w3svc` service and will exit when the
service state changes from `SERVICE_RUNNING` to either one of `SERVICE_STOPPED`,
`SERVICE_STOP_PENDING`, `SERVICE_PAUSED` or `SERVICE_PAUSE_PENDING`.

-----

其實這些多包一層的架構，都是為了相容性而已。如果我們不需要依賴 IIS，這些多餘的包裝都可以省略的... 換個角度來思考，如果我現在要開發新服務的話，還要繼續這樣兜圈子 (windows service + service monitor) 嗎? 或是我可以直接用 docker 原生的方式來開發 (console application) 就好?

看到這邊，大家可以配合我去年在 .NET Conf 2017 分享的 Container Driven Develop (容器驅動開發) 那個 session 講到的做法一起看。如果你很肯定將來一定是透過 docker 來部署，我強烈建議開發人員可以盡量簡化開發方式，就直接用 console application 模式來開發就好了。其餘系統層面的事情，就交給 docker 去處理就好了。






## STEP 2, 環境考量

接下來，從執行環境與開發人員的配合來看這兩種方式的考量吧。開始之前，我先找了其它參考資訊，看看 IIS hosting 跟 Self hosting 在功能上的差別。我節錄這討論串，它列出了使用 IIS 可以得到的額外好處 (相對於 SelfHost):

* [Self hosting or IIS hosted?](https://forums.asp.net/t/1908235.aspx?Self+hosting+or+IIS+hosted+)

What I've found (basically just pros for IIS hosted):
1. You lose all of the features of IIS (logging, application pool scaling, throttling/config of your site, etc.)...
1. You have to build every single feature that you want yourself HttpContext?
1. You lose that since ASP.NET provides that for you. So, I could see that making things like authentication much harder WebDeploy?
1. IIS has some nice specific features in 8 about handling requests and warming up the service (self-hosted does not)
1. IIS has the ability to run multiple concurrent sites with applications and virtual directories to advanced topics like load balancing and remote deployments.

其中 (2), (3) 我先略過，這個在開發階段就可以避免了，或是改用 Owin / .NET Core 就不存在的問題 (HttpContext)。其它都屬於部署管理方面的問題；如果你還在用傳統的方式部屬或是管理 web application (例如手動安裝 server, 內部系統, 沒有太多自動化, 同一套 server 可能執行多個 application 等等)，我會強烈建議你繼續使用 IIS。因為上述的功能對你都很重要。但是如果是 microservices, 以上的假設不大可能繼續成立了，你一定會被迫採用 container 這類能高度自動化的方式來進行。這時我們竹條來看看採用 IIS 的優點，是否還真的是 *必要* 的功能? 是否在你的 microservices infrastructure 底下，都有替代的功能了?


> You lose all of the features of IIS (logging, application pool scaling, throttling/config of your site, etc.)...

微服務架構下，幾乎都會搭配 container 及 orchestration 的機制一起使用。上述功能大多有替代方案，一次管理上百個 instances. 這時每個 instance 其實不再需要透過 IIS 提供這些功能了。


> IIS has some nice specific features in 8 about handling requests and warming up the service (self-hosted does not)

同樣的，application 的 life cycle 管理，也一樣可以透過 orchestration 搞定。更細緻的 health checking 等等，就是這篇會提到的。也都有對應更適合 microservices 的解決方案了。


> IIS has the ability to run multiple concurrent sites with applications and virtual directories to advanced topics like load balancing and remote deployments.

container 的精神，就是一個 process 一個 container, 在 run time 再組合成你期望的樣子。因此在一個 domain / ip address 上面放置多個 web sites 的需求，其實都會被轉移到前端的 reverse proxy, 後端每個 application 至少都有一個以上的 container 提供對應的服務。這任務都會轉由 orchestration 或是 reverse proxy 解決，對於每個 container 本身已經不是必要的功能了。


我先下個簡單的結論: 在微服務化 + 容器化部署的前提下，IIS 都不再是絕對必要的組件了。如果其它考量有更好的選擇，就去做吧!



## STEP 3, ASP.NET Application Life Cycle

前面架構面就有提到 app pool life cycle, 我這邊再追加一些前面沒談到的細節:

App Pool 的管理，其實在 IIS6 就開始提供了 (windows 2003), 年代久遠, 有介紹的文章已經不多了，我找到一篇: [IISRESET vs Recycling Application Pools](https://fullsocrates.wordpress.com/2012/07/25/iisreset-vs-recycling-application-pools/), 各位可以看看他對 recycle 的部分說明，講的蠻到位的。

任何 web application (包含 asp.net webform, mvc, webapi 等等都算), 在 IIS 都會被丟到 app pool 內執行。由於 web 都屬於被動觸發的模式，也就是有 request 進來，丟給 application 處理，處理完成後回應 response 即可。因此 IIS 花了不少功夫在處理 app pool 這件事，讓你的 application 長期運作下能夠耗用最少的系統資源，提供最佳的整體效能，還有最佳的可靠度。

IIS 的對應做法不少，包含延遲啟動 (第一個 request 進來才啟動 app pool)，連續一段時間都沒有 request 就結束 app pool, 或是同時啟用多個 worker 擴大處理能力，或是自動重新啟用可能有問題的 app pool 等等。

為何我要在這邊特別提出這點? 在單機版的情況下，有 IIS 幫我們處理這些事情是很幸福的，開發人員跟運維人員其實都不用傷腦筋；但是同樣的目的，類似的處理過程，container / microservice infra (包含這次要介紹的 Consul) 也都做了，我們又面臨同樣的狀況，是否還需要 IIS 在每個 container 內都做一次重複的事情?

除了這點之外，更重要的一點是: developer 的控制範圍只在 app pool 內。舉例來說，ASP.NET 可以監聽 application event, 在 Application_Start / Application_End 等等事件去做對應的動作.. 但是各位讀者可以先看看這篇 Service Discovery 的內容，試想一下這個矛盾的情境:

1. service 啟動之後，要對 service registry 註冊
1. service 啟動並完成註冊後，會定期對 registry 發送 heartbeats, 確保 service 正常運作
1. api gateway 接到新的 request 後，就會查詢 registry 找出合適的 instance 來服務

上述這些程序，經過 IIS 的包裝之後，會變的很難處理。上述的步驟，你沒發現 (1) 跟 (3) 是衝突的嗎? 沒有 (3) 怎麼會觸發 (1) ? 可是沒有 (1) 的話 (3) 怎麼會找的到新的 instance? (1) (3) 沒搞定的話，(2) 也不用做了...

其它更別提，container / IIS 沒有改變的情況下，app pool 可能會被摧毀及重新建立好幾次，如果照標準的寫法，這個服務就被重新註冊好幾次了，這些都是多餘的部分。當然我知道 IIS 可以關掉這些機制，或是設置成 IIS 一起動就自動 warm up 你的 application, 但是這麼一來，我們需要 IIS 存在的目的又更低了，不是嗎?

這種情況，反而我們用 Self-Hosting 的方式就異常簡單了 XD (如前面架構面討論的)。許多這類問題，都是我一直想在 CDD (Container Driven Develop) 裡面強調的，善用 container 的特性，你其實可以非常大幅的簡化你的開發方式，又不損你的功能及彈性。這是充分了解 containerize 之後帶來的好處，但是前提是團隊的架構師要清楚的瞭解這點才行。

剩下唯一的考量，就是: 當我們拿掉 IIS 之後，連帶的 IIS 額外提供的優點也被拿掉了。我們要重新檢視的是，這些功能是否再我們 microservices infrastructure 裡都有其他替代做法了? 如果都有，就放心的拿掉他吧! 這部分的結論也是: 沒有其它非用 IIS 不可的前提下，用 Self Hosting + Container 的作法反而能更漂亮的控制這些狀況。





## STEP 4, 效能考量

這邊我就不花太多篇幅說明了。簡單的說，IIS 負責了基本的 web server, 與額外提供的各種安全與管理的功能。整體來說，效能只會更差不會更好。我正好有找到一篇文章，雖然有點舊了，但是架構上就是說明 IIS vs SelfHosting 的 benchmark 差異，讓各位感受一下:

* [Performance comparison: IIS 7.5 and IIS 8 vs. self-hosted mvc4 web api](http://blog.bitdiff.com/2012/06/performance-comparison-iis-75-and-iis-8.html)

測試的內容我就不說了，我直接貼一下他的測試結果:

|                       | Requests (#/sec)  | Time per request (ms) |
|-----------------------|-------------------|-----------------------|
|IIS 8 (windows 8)      |4778.23            |20.928                 |
|Self-Host (windows 8)  |5612.23            |17.818                 |

IIS 7 的數據我就不貼了，效能差異更大。在 IIS 8 的測試基準來看，用 self-host 的效能可以好上 17.5%

這部分的結論是: 微服務的架構下，是分工更細緻的規劃。如果 IIS 額外處理的部分都有更專屬的設備或是服務在負責時，拋開 IIS 這層是件好事，你可以用同樣的 source code, 同樣的設備，搾出更高的效能。




# 微服務架構下的 Self-Host 實作

終於來到要寫 code 的階段了。為了這部分，我上周特地多寫了一篇 [Tips: 在 .NET Console Application 中處理 Shutdown 事件](), 就是為了這個範例。所有跟 consul 搭配的 code, 我都留到下一篇, 這篇我只先處理掉 Self-Host 的部分就好。為了搭配 service discovery 機制，有三件事是你必須對你自己的服務能精準的掌控的:

1. 服務何時啟動? (需要進行註冊的動作)
1. 服務何時終止? (需要進行註冊資訊移除的動作)
1. (1) ~ (2) 之間，需要穩定可靠的 background task (必須持續的送出心跳資訊)

延續前面那段 "IIS Host vs Self Host" 的討論，於是，在這個範例我大膽地做了點改變，我決定不用 IIS 來 hosting ASP.NET MVC WebAPI application, 改用自己開發的 Self Hosting Console App 來替代 IIS，同時由這個 Self Host App 來負責 Consul 的 Reg / DeReg 等任務，API 本身要執行的商務邏輯，維持在 ASP.NET 裡面處理就好。

接下來的範例我們就直接採用 Self Host 的模式來寫 code, 避開 IIS 對於 App Pool 的各種管理與優化動作，藉以更精準的執行註冊機制，以及接下來要探討的 Health Checking 的機制。


## 1. 將 Web Project 改為 SelfHost 模式

首先，我想在改動最小的前提下，另外一個 Self-Host 的 console application, 來啟動原本的 ASP.NET WebAPI project:

```csharp

class Program {
  static void Main(string[] args) {
    using (WebApp.Start<Startup>("http://localhost:9000/"))
    {
        Console.WriteLine($"WebApp Started.");
        Console.ReadLine();
    }
  }
}

public class Startup
{
    // This code configures Web API. The Startup class is specified as a type
    // parameter in the WebApp.Start method.
    public void Configuration(IAppBuilder appBuilder)
    {
        // Configure Web API for self-host. 
        HttpConfiguration config = new HttpConfiguration();

        config.Routes.MapHttpRoute(
            name: "QueryApi",
            routeTemplate: "api/{controller}/{id}",
            defaults: new { id = RouteParameter.Optional }
        );

        config.Routes.MapHttpRoute(
            name: "DiagnoisticApi",
            routeTemplate: "api/{controller}/{action}/{text}",
            defaults: new { id = RouteParameter.Optional }
        );

        // do nothing, just force app domain load controller's assembly
        Console.WriteLine($"- Force load controller: {typeof(IP2CController)}");
        Console.WriteLine($"- Force load controller: {typeof(DiagController)}");

        appBuilder.UseWebApi(config);
    }
}

```

絕大部分的 code, 你會 ASP.NET MVC 就看的懂了，不再贅述。我只挑特別修改過的地方說明。當你定義完 routing 之後，第一個碰到的，就是 ASP.NET 有可能會找不到你的 controller 在哪裡 (如下圖)。

![](wp-content/images/2018-04-06-aspnet-msa-labs2-consul/2018-05-07-21-01-35.png)

> No type was found that matches the controller named 'ip2c'.

主要原因就是，過去 IIS Host 會幫你 "搜尋" 可能的 controller types, 現在在 self host 就得自己來了。這個動作是透過 IAssembliesResolver 這個介面在進行的。預設值會搜尋 AppDomain 所有已經載入的 Assemblies 清單。不過我們的狀況有點尷尬，這清單是會延遲載入的，我們 Project 已經 Reference IP2C.WebAPI 這個 project, 但是啟動 SelfHost 時，如果 code 都還沒有任何地方用到這個 IP2C.WebAPI 的 class, 那麼當下的 AppDomain 是不會有我們的 controller 的...

既然 .NET 大部分的 source code 都已經開源了，就挖出來求證一下:

https://github.com/aspnet/AspNetWebStack/blob/master/src/System.Web.Http/Dispatcher/DefaultAssembliesResolver.cs

```csharp

namespace System.Web.Http.Dispatcher
{
    /// <summary>
    /// Provides an implementation of <see cref="IAssembliesResolver"/> with no external dependencies.
    /// </summary>
    public class DefaultAssembliesResolver : IAssembliesResolver
    {
        /// <summary>
        /// Returns a list of assemblies available for the application.
        /// </summary>
        /// <returns>A <see cref="Collection{Assembly}"/> of assemblies.</returns>
        public virtual ICollection<Assembly> GetAssemblies()
        {
            return AppDomain.CurrentDomain.GetAssemblies().ToList();
        }
    }
}

```

因為我是直接用 add reference 的方式，去參考原本的 web project, 你可以直接把 code 搬過來 (這樣就變成同一個 assembly 了)，如果不想改，要解決這個狀況，最簡單的方式，就是在啟動 SelfHost 之前，隨便加幾行 code 確保這 assembly 會在 resolver 之前被用到就好了。所以我在 Startup 這個 class 裡面加了這兩行。這兩行目的是在 Configuration 階段，就確保所有需要的 Controller 的 Assembly 都已經被載入 AppDomain。你可別看到他沒做啥事 (只是印出 message), 就把它拿掉...

```csharp
            // do nothing, just force app domain load controller's assembly
            Console.WriteLine($"- Force load controller: {typeof(IP2CController)}");
            Console.WriteLine($"- Force load controller: {typeof(DiagController)}");
```

當然，你要講究一點的話，可以改寫自己專屬的 IAssembliesResolver 物件，並且在 config.Services.Replace(typeof(IAssembliesResolver), new MyAssembliesResolver()) 裡面用自己的版本替換掉。你就可以更精準的用你的邏輯來處理這些問題。




## 2, 處理 "啟動" 與 "終止" 的動作


接下來就單純多了。既然都 SelfHost 自己處理了，我們就可以很精準的掌握到服務啟動與結束的時機了。原本的 SelfHost 長這樣:

```csharp

class Program {
  static void Main(string[] args) {
    using (WebApp.Start<Startup>("http://localhost:9000/"))
    {
        Console.WriteLine($"WebApp Started.");

        // TODO: 服務啟動完成。註冊的相關程式碼可以放在這裡。

        Console.ReadLine();

        // TODO: 服務即將終止。移除註冊資訊的相關程式碼可以放在這裡。
    }
  }
}

```

要插入註冊資訊沒太大問題，比較需要留意的是服務即將終止的那段。目前 SelfHost 的設計是，在 Console 模式下，Console.ReadLine() 會 Block 前景程式的運行，直到你按下 ENTER 之後才會繼續。按下 ENTER 就代表 SelfHost 即將進入終止的程序，你必須先移除註冊資訊後才能正常結束 SelfHost 。

不過實際的狀況下，你不可能要求 user 要先用 terminal 連進來按 ENTER 吧，我們需要更精準的偵測服務停止的事件。


## 3, 處理系統關機的事件

目前服務是等 user 在 console 按下 ENTER 就結束了，實際部署的情況不會是這樣，大都是 orchestration 或是 op team 直接把這個 container 或是 process 砍掉。所以我們要花點功夫，去攔截 OS shutdown 的動作，取代掉原本的 Console.ReadLine() 。相關作法的討論，都在 [Tips: 在 .NET Console Application 中處理 Shutdown 事件]() 這篇有詳細的說明了，這邊就直接看 sample code:

```csharp


    class Program
    {
        static void Main(string[] args)
        {
            string baseAddress = @"http://localhost:9000/";

            #region init windows shutdown handler
            SetConsoleCtrlHandler(ShutdownHandler, true);

            _form = new HiddenForm()
            {
                ShowInTaskbar = false,
                Visible = false,
                WindowState = FormWindowState.Minimized
            };

            Task.Run(() =>
            {
                //Application.EnableVisualStyles();
                //Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(_form);
            });

            Console.WriteLine($"* Press [CTRL-C] to exit WebAPI-SelfHost...");
            #endregion


            // Start OWIN host 
            Console.WriteLine($"Starting WebApp... (Bind URL: {baseAddress})");
            using (WebApp.Start<Startup>(baseAddress))
            {
                Console.WriteLine($"WebApp Started.");

                {

                    #region register services
                    //
                    // TODO: #1, 服務啟動完成。註冊的相關程式碼可以放在這裡。
                    //
                    #endregion


                    #region send heartbeats to consul
                    bool stop = false;
                    Task heartbeats = Task.Run(() =>
                    {
                        while (stop == false)
                        {
                            Task.Delay(1000).Wait();

                            //
                            // TODO: #2, Send Heartbeats to service discovery server
                            //
                        }
                    });
                    #endregion


                    // wait until process shutdown (ctrl-c, or close window)
                    int shutdown_index = WaitHandle.WaitAny(new WaitHandle[]
                    {
                        close,
                        _form.shutdown
                    });
                    Console.WriteLine(new string[]
                    {
                        "# user press CTRL-C, CTRL-BREAK or close window...",
                        "# system shutdown or logoff..."
                    }[shutdown_index]);


                    //
                    // TODO: #3, 服務即將終止。移除註冊資訊的相關程式碼可以放在這裡。
                    //

                    stop = true;
                    heartbeats.Wait();

                    // wait 5 sec and shutdown owin host
                    Task.Delay(5000).Wait();
                }
            }

            #region init windows shutdown handler
            SetConsoleCtrlHandler(ShutdownHandler, false);
            _form.Close();
            #endregion
        }

        #region shutdown event handler
        private static ManualResetEvent close = new ManualResetEvent(false);

        [DllImport("Kernel32")]
        static extern bool SetConsoleCtrlHandler(EventHandler handler, bool add);

        delegate bool EventHandler(CtrlType sig);
        //static EventHandler _handler;
        enum CtrlType
        {
            CTRL_C_EVENT = 0,
            CTRL_BREAK_EVENT = 1,
            CTRL_CLOSE_EVENT = 2,
            CTRL_LOGOFF_EVENT = 5,
            CTRL_SHUTDOWN_EVENT = 6
        }
        private static bool ShutdownHandler(CtrlType sig)
        {
            //Console.WriteLine("Shutdown Console Apps...");
            //brs.StopWorkers();
            close.Set();
            Console.WriteLine($"Shutdown WebHost...");
            return true;
        }

        private static HiddenForm _form = null;
        #endregion
    }



```


有兩種事件是我打算處理的，一個是 user interactive 的動作 (包含 CTRL-C, CTRL-BREAK, CLOSE WINDOW ...), 我用 Win32 API: [SetConsoleCtrlHandler()](https://docs.microsoft.com/en-us/windows/console/setconsolectrlhandler) 來處理。MSDN 的官方文件有說明，我截錄片段:

> Each console process has its own list of application-defined HandlerRoutine functions that handle CTRL+C and CTRL+BREAK signals. The handler functions also handle signals generated by the system when the user closes the console, logs off, or shuts down the system. Initially, the handler list for each process contains only a default handler function that calls the ExitProcess function. A console process adds or removes additional handler functions by calling the SetConsoleCtrlHandler function, which does not affect the list of handler functions for other processes. When a console process receives any of the control signals, its handler functions are called on a last-registered, first-called basis until one of the handlers returns TRUE. If none of the handlers returns TRUE, the default handler is called.


我這邊的設計，是配合 ManualResetEvent shutdown, 由上面的 handler routine, 在偵測到對應事件之後，來喚醒主程序用的。因此，你只要把原本的 Console.ReadLine(), 換成 shutdown.WaitOne() 就可以了。各位可以自行測試一下這段 code 的效果，我也不再多做介紹。加上這段 code 之後，大概只剩下機器直接被拔掉電源，或是管理者用工作管理員直接 kill process 無法攔截之外，其它大概都能夠處理了。這部分的 code 可以參考 Main() 的頭尾兩部分，都有一段呼叫 SetConsoleCtrlHandler() 的 code, 就是處理這段的 code。


另一種是 OS 層級的事件，前面的 API 在 console mode 下不支援，因此我在 [Tips: 在 .NET Console Application 中處理 Shutdown 事件] 這篇文章內用 hidden window 來接收 message, 攔截 WM_QUERYENDSESSION。這邊我也把它包裝成 form.shutdown 這個 ManualResetEvent 來處理。在 Main() 中間有這麼段 code, 就是為了準備 hidden window, 好接收 shutdown message:

```csharp
            _form = new HiddenForm()
            {
                ShowInTaskbar = false,
                Visible = false,
                WindowState = FormWindowState.Minimized
            };

            Task.Run(() =>
            {
                //Application.EnableVisualStyles();
                //Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(_form);
            });

```

實際的 HiddenForm 則定義在這邊:

```csharp
    public partial class HiddenForm : Form
    {
        public HiddenForm()
        {
            InitializeComponent();
        }

        public ManualResetEvent shutdown = new ManualResetEvent(false);

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == 0x11) // WM_QUERYENDSESSION
            {
                m.Result = (IntPtr)1;
                Console.WriteLine("winmsg: WM_QUERYENDSESSION");
                this.shutdown.Set();
            }

            //Console.Write('.');
            base.WndProc(ref m);
        }
    }
```    

這兩種狀況，任意發生其中一種，我就會執行終止的動作。因此我用了 WaitHandle.WaitAny(new WaitHandle[] { close, _form.shutdown }) 來等待。任一個 ManualResetEvent 被 Set 之後，這段 code 就會被喚醒，後續的 shutdown 動作就會被執行。

```csharp
                    // wait until process shutdown (ctrl-c, or close window)
                    int shutdown_index = WaitHandle.WaitAny(new WaitHandle[]
                    {
                        close,
                        _form.shutdown
                    });
```



# STEP 3, Health Checking

接下來，如果我期望服務運作過程中，能持續定期發送通知 (心跳訊號 heartbeats), 告知外部系統我還健在，我們仍然可以很容易的在這架構下插入這段 code (這邊只展示該擺在哪裡，實際配合 consul 的 health checking 請等下一篇):

```csharp
                    #region send heartbeats to consul
                    bool stop = false;
                    Task heartbeats = Task.Run(() =>
                    {
                        IP2CController ip2c = new IP2CController();
                        while (stop == false)
                        {
                            Task.Delay(1000).Wait();

                            try
                            {
                                var result = ip2c.Get(0x08080808);
                                if (result.CountryCode == "US")
                                {
                                    consul.Agent.PassTTL($"service:{serviceID}:2", $"self test pass.");
                                }
                                else
                                {
                                    consul.Agent.WarnTTL($"service:{serviceID}:2", $"self test fail. query 8.8.8.8, expected: US, actual: {result.CountryCode}({result.CountryName})");
                                }
                            }
                            catch(Exception ex)
                            {
                                consul.Agent.FailTTL($"service:{serviceID}:2", $"self test error. exception: {ex}");
                            }
                        }
                    });
                    #endregion

```

若主程式已經盡到 shutdown 的部分，則這段 code 會設定 stop flag, 然後等待 heartbeats 的部分執行完畢:

```csharp
                    stop = true;
                    heartbeats.Wait();
```



# STEP 5, DEMO

最後，搞了這堆東西總是要上戰場的，既然一開始都講了 CDD 容器驅動開發了，總是要把最後一步走完。我補上這幾個服務的 dockerfile:


**Consul**:

```dockerfile
FROM microsoft/windowsservercore:1709

WORKDIR consul

COPY . .

EXPOSE 8500 8600 8600/udp

ENTRYPOINT consul.exe agent -dev -client 0.0.0.0
```

基本上，就是包起來而已... 沒太多技巧在裡面。


**TestConsole**:

```dockerfile
FROM microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709

WORKDIR   c:/IP2C.Console
COPY . .


ENV CONSUL_URL=http://consul:8500

ENTRYPOINT IP2CTest.Console.exe -consul %CONSUL_URL%

```

同上，就是包起來而已... 只是把 consul 的網址拉出來當作環境變數而已。


**WebAPI.SelfHost**:

```dockerfile
FROM microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709

WORKDIR c:/selfhost
COPY . .

ENV CONSUL_URL=http://consul:8500
ENV NETWORK=0.0.0.0/0

EXPOSE 80
ENTRYPOINT IP2C.WebAPI.SelfHost.exe -network %NETWORK% -consul %CONSUL_URL%
```
