---
layout: post
title: "容器化的微服務開發 #2, API Service 容器化的選擇: IIS or Self Host ?"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps", "Service Discovery", "Consul"]
published: false
comments: true
redirect_from:
logo: /wp-content/images/2018-04-06-aspnet-msa-labs2-consul/how_would_you_solve_the_icing_problem.png
---


在微服務的應用上，Service Discovery 實在太重要了, 許多微服務的特性及優勢，都需要靠他才能做的好。於是這次，我就花了篇文章的版面，決定好好介紹一下 Consul (源自 HashiCorp 的解決方案) 這套服務。我拿去年介紹容器驅動開發用的案例: IP2C Service, 重新搭配 Consul 來改寫，用 Consul 解決 Service Discovery, Health Checking 以及 Configuration Management 的問題。讓各位讀者清楚的了解該如何善用 Consul 提供的功能，來強化你的服務可靠度。

不過在開始之前，我想了很久，決定先追加這篇，搭配上一篇講到 CDD (Container Driven Develop) 的概念與實作。你有想過你的 API service 該怎麼封裝成容器嗎? 掛在 IIS 下執行，還是用 Self Host ? Docker 是從 Linux 上面發展起來的，對於上面的服務反而沒太多這類的問題；不過長年在 Windows 環境下的開發者都被 Microsoft 照顧得好好的，要妥善運用 Docker / Windows Container 反而就沒辦法那麼得心應手。我強烈建議每個有心使用 windows container 的團隊能夠看一下這篇，試著從無到有親手跑過一次，了解整個容器化的過程。即便往後很多東西都會有現成的解決方案，找機會讓自己的團隊體驗一下重新造輪子的過程絕對有幫助的。

![](/wp-content/images/2018-04-06-aspnet-msa-labs2-consul/how_would_you_solve_the_icing_problem.png)
> Tony Stark 就是自己從無到有打造鋼鐵裝，才知道有那些坑要解決... 撿現成的技術，危急時刻就沒有應變能力...

跨到微服務的世界，這類的細節其實到處都是。其實這些問題都不難，難的地方在於過去都是 operation team 解決掉了，不需要 development team 傷腦筋。現在微服務需要更密切的整合，必須要同時能掌握 development 跟 operation 的 know how, 才能正確的拿捏該捨掉那些東西。這篇就是從這角度，告訴你 IIS 與 Self Host 該如何取捨。這些問題解決完畢之後，就可以開始進入 Consul 的使用方式。

<!--more-->

在上一篇 [容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/) 我拿 IP 地區查詢服務當作範例，用容器驅動開發的觀念，實作了微服務版本的 IP2C Service。我提到的 "Container Driven Development" 概念，就是假設你將來 "一定" 會用容器化的方式來部署的話，那麼在架構設計之初就能盡可能的最佳化，能透過容器解決的問題就不用自己做了。極度的簡化，可以讓 Operation 的團隊更容易接手維護你的服務，Developer 也能更專注把精力用在核心的業務上。這次我會重構先前的飯粒程式，進一步的擴大 "Container Driven Development" 的概念，假設將來 "一定" 會用 Consul + Container 的方式部署。同樣的來看看，你可以如何建構這樣的 application?

建議看下去之前先看一看底下會用到的幾個重要觀念:

* [.NET Conf 2017 - Container Driven Development, 容器驅動開發](https://www.facebook.com/andrew.blog.0928/videos/509145696127380/)
* [容器化的微服務開發 #1, IP查詢架構與開發範例](/2017/05/28/aspnet-msa-labs1/)

所有微服務相關的文章，可以直接參考下列的導讀。

{% include series-2016-microservice.md %}


# STEP 1, 環境選擇，IIS Host or Self Host?

其實這個問題，我在上一篇 container driven development 時我就想講了，不過一直拖到現在。我特地拿出來探討一下這個問題，因為這個決策，會直接影響到後續 (下一篇) 如何跟 Consul 做後續的整合方式，不可不慎。因此我把他擺在第一個步驟。

對開發人員來說，選擇 IIS 或是 Self Host 其實沒有太大的不同，你就是好好的開發 ASP.NET MVC WebAPI application 而已啊，只是你的 WebAPI 是掛在 IIS 下執行，還是自己開發的 Console App 下執行? 在執行階段或是部署階段，考量的方向有幾個:

1. 架構考量: IIS 是 windows service, 與 container 是以 process 為主的模式有出入 (後敘)
1. 環境考量: IIS 提供完整的 web hosting 環境，可提供很多不需要自己開發就有的功能 (後敘)
1. 效能考量: Hosting 再 IIS 下需要花費較多系統資源 (後敘)

接下來我就分別就這三個方向，分享一下我自己的看法。這些只是優劣的判斷，並非絕對的選擇，各位採納前還是要評估自己的狀況再決定。

> 有些解決方案，例如 asp.net core 提供的 kestrel, 或是之前 .net framework 的 cassini dev server, 都是介於 IIS 與 self-hosting 的中間解決方案。這類方案我會把他當作其它的 open source project, 把 self-hosting 的功能做好給你直接使用而已。在以下的討論內，kestrel 這種 solution 我會把他歸在 self-hosting 那一類看待。

* [ASP.NET Core Web Servers: Kestrel vs IIS Feature Comparison and Why You Need Both](https://stackify.com/kestrel-web-server-asp-net-core-kestrel-vs-iis/)


## 1. 架構考量

用過 docker 的朋友們大概都知道這個概念: container 的生命週期，就是跟隨著 entrypoint 指定的那個 process ... docker run 就會在 container 內啟動 entrypoint 指定的 process, 如果該 process 執行完畢，則該 container 會自己結束，進入 stopped 狀態。服務類型 (如 web server) 也是一樣，唯一的差別是啟動這類 container 時，我們會 docker run -d 多加一個 -d (daemon) 的參數，告訴 docker engine 不用在 console 端等待他結束而已。docker engine 會在 background 繼續讓這個 container 持續運作，直到自己結束或是被 stop 為止。

然而 windows 下的 application 執行方式，硬是多了好幾種 console 以外的模式，windows service 就是其中之一。windows service 本身就有專屬的 project type, 編譯出來就是 service mode, 必須透過註冊的方式, 隨後 windows 就會在是當時機自主啟動它在背景執行。你要控制它的運作，windows 也有專屬的工具對 service 進行 start / stop / continue / pause / restart ( == stop + start ) 等等操作。

在過去廿幾年來，這種模式在 windows 一直運作得很好，直到 docker 的盛行... 如果你要封裝的主要服務，是以 windows service 的形態存在，這就變得多此一舉。其實透過 docker 的協助, console application 就能表現的跟 windows service 幾乎一模一樣的效果了。你只要用 docker run -d --restart always .... 來啟動你的 container, 它就完全是個 windows service 了 (還不需要註冊)。只要你的 console application 有好好的處理 OS shutdown event (或是 unix 系列的 signal), 你一樣能完美的透過 docker start / stop / pause / unpause 指令來操作 (對應到 windows service 的 start / stop / pause / continue)。

所以，你有想過 Microsoft 如何把 IIS 這種 windows service 打包成 container image 嗎? 這樣的 dockerfile 你該怎麼寫? 你到底要在 entrypoint 擺什麼? 執行起來的狀態才是你期待的?

看一下 Microsoft 提供的 [IIS](https://hub.docker.com/r/microsoft/iis/) container image, [dockerfile](https://github.com/Microsoft/iis-docker/blob/master/windowsservercore-1709/Dockerfile) 是怎麼寫的:

```dockerfile

# escape=`
FROM microsoft/windowsservercore:1709

RUN powershell -Command `
    Add-WindowsFeature Web-Server; `
    Invoke-WebRequest -UseBasicParsing -Uri "https://dotnetbinaries.blob.core.windows.net/servicemonitor/2.0.1.3/ServiceMonitor.exe" -OutFile "C:\ServiceMonitor.exe"

EXPOSE 80

ENTRYPOINT ["C:\\ServiceMonitor.exe", "w3svc"]

```

很簡單，才幾行而已。看到 C:\ServiceMonitor.exe, 這是啥? Microsoft 剛好開源了這個工具，有興趣的可以直接 clone 下來研究:
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

搞半天，就是多包一層而已。Windows service 還是照原本的樣子執行，container 啟動後就像是 VM 開機一樣，啟動完成就會自己把 IIS 跑起來。不過 container 的 life cycle 怎麼管理? Microsoft 多開發一個工具，本身不做什麼事情，就是不斷監控 IIS 而已，IIS 還活著，ServiceMonitor.exe 就不會結束。這時 dockerfile 的 entrypoint 只要指向 ServiceMonitor.exe, 就能完美的把這落差補起來了。這樣是能解決舊系統容器化的障礙，不過... 有點脫褲子放屁啊! 如果我現在要開發新服務的話，還要繼續這樣兜圈子 (windows service + service monitor) 嗎? 或是我可以直接用 docker 原生的方式來開發 (console application) 就好?

看到這邊，大家可以配合我去年在 .NET Conf 2017 分享的 Container Driven Develop (容器驅動開發) 那個 session 講到的做法一起看。如果你很肯定將來一定是透過 docker 來部署，我強烈建議開發人員可以盡量簡化開發方式，就直接用 console application 模式來開發就好了。其餘系統層面的事情，就交給 docker 去處理就好了。




## 2. 環境考量

接下來，從執行環境與開發人員的配合來看這兩種方式的考量吧。開始之前，我先找了其它參考資訊，看看 IIS hosting 跟 Self hosting 的差別。我節錄這討論串，它列出了使用 IIS 可以得到的額外好處 (相對於 SelfHost):

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

container 的精神，就是一個 process 一個 container, 在 run time 再組合成你期望的樣子。因此在一個 domain / ip address 上面放置多個 web sites 的需求，其實都會被轉移到前端的 reverse proxy, 後端每個 application 至少都有一個以上的 container 提供對應的服務。這任務都會轉由 orchestration 或是 reverse proxy 解決，對於每個 container 本身已經不是必要的功能了。我先下個簡單的結論: 在微服務化 + 容器化部署的前提下，IIS 都不再是絕對必要的組件了。如果其它考量有更好的選擇，就去做吧!



## 3. ASP.NET Application Life Cycle

不過，在結束這個段落之前，因為這篇文章後半會用到，我再追加另一個環境控制上的考量: (app pool) life cycle

這部分其實在 IIS6 就開始提供了 (windows 2003), 年代久遠, 有介紹的文章已經不多了，我找到一篇: [IISRESET vs Recycling Application Pools](https://fullsocrates.wordpress.com/2012/07/25/iisreset-vs-recycling-application-pools/), 各位可以看看他對 recycle 的部分說明，講的蠻到位的。

任何 web application (包含 asp.net webform, mvc, webapi 等等都算), 在 IIS 都會被丟到 app pool 內執行。由於 web 都屬於被動觸發的模式，也就是有 request 進來，丟給 application 處理，處理完成後回應 response 即可。因此 IIS 花了不少功夫在處理 app pool 這件事，讓你的 application 長期運作下能夠耗用最少的系統資源，提供最佳的整體效能，還有最佳的可靠度。

IIS 的對應做法不少，包含延遲啟動 (第一個 request 進來才啟動 app pool)，連續一段時間都沒有 request 就結束 app pool, 或是同時啟用多個 worker 擴大處理能力，或是自動重新啟用可能有問題的 app pool 等等。

為何我要在這邊特別提出這點? 在單機版的情況下，有 IIS 幫我們處理這些事情是很幸福的，開發人員跟運維人員其實都不用傷腦筋；但是同樣的目的，類似的處理過程，container / microservice infra (包含這次要介紹的 Consul) 也都做了，我們又面臨同樣的狀況，是否還需要 IIS 在每個 container 內都做一次重複的事情?

除了這點之外，更重要的一點是: developer 的控制範圍只在 app pool 內。舉例來說，ASP.NET 可以監聽 application event, 在 Application_Start / Application_End 等等事件去做對應的動作.. 但是各位讀者可以先看看這篇 Service Discovery 的內容，試想一下這個矛盾的情境:

1. service 啟動之後，要對 service registry 註冊
1. service 啟動並完成註冊後，會定期對 registry 發送 heartbeats, 確保 service 正常運作
1. api gateway 接到新的 request 後，就會查詢 registry 找出合適的 instance 來服務

上述這些程序，經過 IIS 的包裝之後，會變的很難處理。上述的步驟，你沒發現 (1) 跟 (3) 是衝突的嗎? 沒有 (3) 怎麼會觸發 (1) ? 可是沒有 (1) 的話 (3) 怎麼會找的到新的 instance? (1) (3) 沒搞定的話，(2) 也不用做了...


其它更別提，container / IIS 沒有改變的情況下，app pool 可能會被摧毀及重新建立好幾次，如果照標準的寫法，這個服務就被重新註冊好幾次了，這些都是多餘的部分。當然我知道 IIS 可以關掉這些機制，或是設置成 IIS 一起動就自動 warm up 你的 application, 但是這麼一來，我們需要 IIS 存在的目的又更低了，不是嗎?

這種情況，反而我們用 Self-Hosting 的方式就異常簡單了 XD, Self-Hosting 就是個標準的 console application, 有很明確的啟動 (進入 Main()) 與結束 (Main() return) 的時間點。而 console application 的啟動與結束，又直接跟 container 綁在一起。因此我們只需要在 Main() 的頭尾，去做上述的 (1) (2) (3) 就完成了。許多這類問題，都是我一直想在 CDD (Container Driven Develop) 裡面強調的，善用 container 的特性，你其實可以非常大幅的簡化你的開發方式，又不損你的功能及彈性。這是充分了解 containerize 之後帶來的好處，但是前提是團隊的架構師要清楚的瞭解這點才行。

同樣的，這部分的結論也是: 沒有其它非用 IIS 不可的前提下，用 Self Hosting + Container 的作法反而能更漂亮的控制這些狀況。








## 4. 效能考量

這邊我就不花太多篇幅說明了。簡單的說，IIS 負責了基本的 web server, 與額外提供的各種安全與管理的功能。整體來說，效能只會更差不會更好。我正好有找到一篇文章，雖然有點舊了，但是架構上就是說明 IIS vs SelfHosting 的 benchmark 差異，讓各位感受一下:

* [Performance comparison: IIS 7.5 and IIS 8 vs. self-hosted mvc4 web api](http://blog.bitdiff.com/2012/06/performance-comparison-iis-75-and-iis-8.html)

測試的內容我就不說了，我直接貼一下他的測試結果:

|                       | Requests (#/sec)  | Time per request (ms) |
|-----------------------|-------------------|-----------------------|
|IIS 8 (windows 8)      |4778.23            |20.928                 |
|Self-Host (windows 8)  |5612.23            |17.818                 |

IIS 7 的數據我就不貼了，效能差異更大。在 IIS 8 的測試基準來看，用 self-host 的效能可以好上 17.5%

這部分的結論是: 微服務的架構下，是分工更細緻的規劃。如果 IIS 額外處理的部分都有更專屬的設備或是服務在負責時，拋開 IIS 這層是件好事，你可以用同樣的 source code, 同樣的設備，搾出更高的效能。



<!-- 
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






// How To: SelfHosting? -->

# STEP 2, Self-Host 實作

微服務架構裡最基本的基礎建設，就是服務註冊機制了。在你熟悉 Consul 的 API 之前，有三件事是你必須對你自己的服務能精準的掌控的:

1. 服務何時啟動? (需要進行註冊的動作)
1. 服務何時終止? (需要進行註冊資訊移除的動作)
1. (1) ~ (2) 之間，需要穩定可靠的 background task (必須持續的送出心跳資訊)

延續前面那段 "IIS Host vs Self Host" 的討論，於是，在這個範例我大膽地做了點改變，我決定不用 IIS 來 hosting ASP.NET MVC WebAPI application, 改用自己開發的 Self Hosting Console App 來替代 IIS，同時由這個 Self Host App 來負責 Consul 的 Reg / DeReg 等任務，API 本身要執行的商務邏輯，維持在 ASP.NET 裡面處理就好。

接下來的範例我們就直接採用 Self Host 的模式來寫 code, 避開 IIS 對於 App Pool 的各種管理與優化動作，藉以更精準的執行註冊機制，以及接下來要探討的 Health Checking 的機制。


## 1. 改為 SelfHost 模式

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

絕大部分的 code, 你會 ASP.NET MVC 就看的懂了，不再贅述。我只挑特別修改過的地方說明。當你定義完 routing 之後，第一個碰到的，就是 ASP.NET 會找不到你的 controller 在哪裡 (如下圖)。

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

要解決這個狀況，最簡單的方式，就是在啟動 SelfHost 之前，隨便加幾行 code 確保會被用到就好了。所以我在 Startup 這個 class 裡面加了這兩行。這兩行目的是在 Configuration 階段，就確保所有需要的 Controller 的 Assembly 都已經被載入 AppDomain。你可別看到他沒做啥事 (只是印出 message), 就把它拿掉...

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

目前服務是等 user 在 console 按下 ENTER 就結束了，實際部署的情況不會是這樣，大都是 orchestration 或是 op team 直接把這個 container 或是 process 砍掉。所以我們要花點功夫，去攔截 OS shutdown 的動作，取代掉原本的 Console.ReadLine() 。直接看 sample code:

```csharp


        #region shutdown event handler
        private static AutoResetEvent shutdown = new AutoResetEvent(false);

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
            shutdown.Set();
            Console.WriteLine($"Shutdown WebHost...");
            return true;
        }

        #endregion


```

用 DLLImport 的方式，呼叫 Kernel32 提供的 Win32 API: [SetConsoleCtrlHandler()](https://docs.microsoft.com/en-us/windows/console/setconsolectrlhandler), 來指定幾種終止程式執行的事件 (包括: CTRL-C, CTRL-BREAK, CLOSE WINDOW, LOGOFF, SHUTDOWN) 的處理程序 (handler routine)。MSDN 的官方文件有說明，我截錄片段:

> Each console process has its own list of application-defined HandlerRoutine functions that handle CTRL+C and CTRL+BREAK signals. The handler functions also handle signals generated by the system when the user closes the console, logs off, or shuts down the system. Initially, the handler list for each process contains only a default handler function that calls the ExitProcess function. A console process adds or removes additional handler functions by calling the SetConsoleCtrlHandler function, which does not affect the list of handler functions for other processes. When a console process receives any of the control signals, its handler functions are called on a last-registered, first-called basis until one of the handlers returns TRUE. If none of the handlers returns TRUE, the default handler is called.

同一篇的另外這段也要留意:

> The system generates CTRL_CLOSE_EVENT, CTRL_LOGOFF_EVENT, and CTRL_SHUTDOWN_EVENT signals when the user closes the console, logs off, or shuts down the system so that the process has an opportunity to clean up before termination. Console functions, or any C run-time functions that call console functions, may not work reliably during processing of any of the three signals mentioned previously. The reason is that some or all of the internal console cleanup routines may have been called before executing the process signal handler.

我這邊的設計，是配合 AutoResetEvent shutdown, 由上面的 handler routine, 在偵測到對應事件之後，來喚醒主程序用的。因此，你只要把原本的 Console.ReadLine(), 換成 shutdown.WaitOne() 就可以了。各位可以自行測試一下這段 code 的效果，我也不再多做介紹。加上這段 code 之後，大概只剩下機器直接被拔掉電源，或是管理者用工作管理員直接 kill process 無法攔截之外，其它大概都能夠處理了。


------------------------
https://docs.microsoft.com/en-us/windows/console/handlerroutine

CTRL_LOGOFF_EVENT 5	
A signal that the system sends to all console processes when a user is logging off. This signal does not indicate which user is logging off, so no assumptions can be made.

Note that this signal is received only by services. Interactive applications are terminated at logoff, so they are not present when the system sends this signal.

CTRL_SHUTDOWN_EVENT 6	
A signal that the system sends when the system is shutting down. Interactive applications are not present by the time the system sends this signal, therefore it can be received only be services in this situation. Services also have their own notification mechanism for shutdown events. For more information, see Handler.

This signal can also be generated by an application using GenerateConsoleCtrlEvent.





https://msdn.microsoft.com/en-us/library/microsoft.win32.systemevents.sessionending.aspx

note:
This event is only raised if the message pump is running. In a Windows service, unless a hidden form is used or the message pump has been started manually, this event will not be raised. For a code example that shows how to handle system events by using a hidden form in a Windows service, see the SystemEvents class.




https://msdn.microsoft.com/en-us/library/microsoft.win32.systemevents.aspx?f=255&MSPPError=-2147217396

see example 2 (using hidden form)










# STEP 3, Health Checking

接下來要進入重頭戲了。除了服務啟動與結束時註冊之外，我們有無其它更精準的方式確認該服務正常運作? 有的，這就是我愛用 Consul 的重點了。他整合了很完善的 Health Checking 機制，讓你很容易的做好這件事。

開始改 code 前，大家可以先看一下 Consul 的官方說明: [Checks](https://www.consul.io/docs/agent/checks.html), 裡面有說明所有支援的 health checking 的方式。我們這邊採用兩種基本的:

1. 由 consul 主動對特定的 URL 做 http test, 如果一定時間內得不到正確的回應，就會判定該服務失敗
1. 由 service 主動定時回報狀態, 如果一定時間內無法回報，consul 就會判定該服務失敗

來看看怎麼在時做上處理 health checking 的問題吧! 先看註冊的部分:

```csharp

            // Start OWIN host 
            Console.WriteLine($"Starting WebApp... (Bind URL: {baseAddress})");
            using (WebApp.Start<Startup>(baseAddress))
            {
                Console.WriteLine($"WebApp Started.");
                string serviceID = $"IP2CAPI-{Guid.NewGuid():N}".ToUpper(); //Guid.NewGuid().ToString("N");

                // ServiceDiscovery.Register()
                using (ConsulClient consul = new ConsulClient(c => { if (!string.IsNullOrEmpty(consulAddress)) c.Address = new Uri(consulAddress); }))
                {

                    #region register services
                    consul.Agent.ServiceRegister(new AgentServiceRegistration()
                    {
                        Name = "IP2CAPI",
                        ID = serviceID,
                        Address = baseAddress,
                        Checks = new AgentServiceCheck[]
                        {
                            new AgentServiceCheck()
                            {
                                DeregisterCriticalServiceAfter = TimeSpan.FromSeconds(30.0),
                                HTTP = $"{baseAddress}api/diag/echo/00000000",
                                Interval = TimeSpan.FromSeconds(1.0)
                            },
                            new AgentServiceCheck()
                            {
                                DeregisterCriticalServiceAfter = TimeSpan.FromSeconds(30.0),
                                TTL = TimeSpan.FromSeconds(5.0)
                            }
                        }
                    }).Wait();
                    #endregion


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
                                if (result.CountryCode == "USA")
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

                    // wait until process shutdown (ctrl-c, or close window)
                    shutdown.WaitOne();

                    stop = true;
                    #endregion

                    // ServiceDiscovery.UnRegister()
                    consul.Agent.ServiceDeregister(serviceID).Wait();
                }
            }


```


我在註冊的地方，加上了這兩筆 health check 的定義:

```csharp
                        Checks = new AgentServiceCheck[]
                        {
                            new AgentServiceCheck()
                            {
                                DeregisterCriticalServiceAfter = TimeSpan.FromSeconds(30.0),
                                HTTP = $"{baseAddress}api/diag/echo/00000000",
                                Interval = TimeSpan.FromSeconds(1.0)
                            },
                            new AgentServiceCheck()
                            {
                                DeregisterCriticalServiceAfter = TimeSpan.FromSeconds(30.0),
                                TTL = TimeSpan.FromSeconds(5.0)
                            }
                        }
```

第一筆是 http test, 意思是我要 consul 每 1.0 sec, 就到 /api/diag/echo/00000000 戳一下，拿到 HTTP 200 就算正常。沒有的話服務會被標記為 FAIL。如果超過 30 sec 都 FAIL，那直接移除註冊資訊 (DeregisterCriticalServiceAfter)。

http test 端看你希望 consul 到哪個 RESTFul api 來測? 我的案例是另外寫一組 diagnoistic api controller, 專門給 consul 測試:

```csharp
    public class DiagController : ApiController
    {
        [HttpGet]
        public string Echo(string text)
        {
            return text;
        }
    }
```

這邊你可以在 code 裡面填上有意義的 code, 例如以我習慣，我如果想隨時測試 SQL 連線是否正確? 我會在 code 裡面執行這類沒啥意義的 SQL 指令 (```select 9527 as TEST;```)，目的只是 ping SQL 而已，確保 SQL 能正確回應給我。這類測試其實不限定只能安排一組，你可以視你的需要安排多組沒問題。只要別寫的走火入魔，在裡面做太多事情，自己被自己的 health checking request 給搞垮就好...

第二筆是 heartbeats, 用 TTL (time to live) 的方式定義, 服務本身要想辦法在 5.0 sec 內回報他自己的狀態是正確的，如果 consul 超出這時間還收不到通知，就會把服務標記為 FAIL。超過 30 sec 都還沒收到通知，則移除註冊資訊。我的做法，是在服務啟動的同時，另外跑個 thread, 平行的不斷每秒回應 consul ... 回應的動作直到服務終止之後才會停止。

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

                    // wait until process shutdown (ctrl-c, or close window)
                    shutdown.WaitOne();

                    stop = true;
                    #endregion


```

當然，這邊你也可以做一些基本的自我檢測，我的例子是直接查詢 Google DNS 的 IP (8.8.8.8) 的地區是否是 ```US``` (United State) ? 如果是我才回報 OK。這邊很多單元測試的技巧也可以搬到這裡來用。也一樣，別走火入魔，這裡是 **Runtime** test, 別測過頭把系統的效能或是穩定度給搞垮了就得不嘗失。

對 Consul 的回報不是只能回報 OK，你可以自己決定要回報 OK (PassTTL)，WARN (WarnTTL) 還是 FAIL (FailTTL)。回報也可以加上一些 notes, consul 可以把他回應給其它查詢的人參考... (WEB UI 也可以看的到)

如果這些都做到位，執行起來後你會發現，consul 的 console 不斷的會顯示這些 logs:

```logs
    2018/05/07 22:53:18 [DEBUG] agent: Check "service:IP2CAPI-B7ED24CBDAD64D318135D83F86982780:1" is passing
    2018/05/07 22:53:18 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:1" is passing
    2018/05/07 22:53:19 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:2" status is now passing
    2018/05/07 22:53:19 [DEBUG] agent: Service "IP2CAPI-B7ED24CBDAD64D318135D83F86982780" in sync
    2018/05/07 22:53:19 [DEBUG] agent: Service "IP2CAPI-42818506E5D24DE8861FDBE753682F19" in sync
    2018/05/07 22:53:19 [DEBUG] agent: Check "service:IP2CAPI-B7ED24CBDAD64D318135D83F86982780:1" in sync
    2018/05/07 22:53:19 [DEBUG] agent: Check "service:IP2CAPI-B7ED24CBDAD64D318135D83F86982780:2" in sync
    2018/05/07 22:53:19 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:1" in sync
    2018/05/07 22:53:19 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:2" in sync
    2018/05/07 22:53:19 [DEBUG] agent: Node info in sync
    2018/05/07 22:53:19 [DEBUG] http: Request PUT /v1/agent/check/pass/service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:2?note=self%20test%20pass. (4.9717ms) from=127.0.0.1:53991
    2018/05/07 22:53:19 [DEBUG] agent: Check "service:IP2CAPI-B7ED24CBDAD64D318135D83F86982780:1" is passing
    2018/05/07 22:53:19 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:1" is passing
    2018/05/07 22:53:20 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:2" status is now passing
    2018/05/07 22:53:20 [DEBUG] agent: Service "IP2CAPI-B7ED24CBDAD64D318135D83F86982780" in sync
    2018/05/07 22:53:20 [DEBUG] agent: Service "IP2CAPI-42818506E5D24DE8861FDBE753682F19" in sync
    2018/05/07 22:53:20 [DEBUG] agent: Check "service:IP2CAPI-B7ED24CBDAD64D318135D83F86982780:1" in sync
    2018/05/07 22:53:20 [DEBUG] agent: Check "service:IP2CAPI-B7ED24CBDAD64D318135D83F86982780:2" in sync
    2018/05/07 22:53:20 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:1" in sync
    2018/05/07 22:53:20 [DEBUG] agent: Check "service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:2" in sync
    2018/05/07 22:53:20 [DEBUG] agent: Node info in sync
    2018/05/07 22:53:20 [DEBUG] http: Request PUT /v1/agent/check/pass/service:IP2CAPI-42818506E5D24DE8861FDBE753682F19:2?note=self%20test%20pass. (2.9934ms) from=127.0.0.1:53991
```

同樣的，即時的狀態也能在 Consul UI 上面看的到:

![](wp-content/images/2018-04-06-aspnet-msa-labs2-consul/2018-05-07-22-56-29.png)


# STEP 4, Consul Aware SDK

Server 端的準備已經萬事俱備，最後一關就是所有的 client 在使用 IP2C 服務之前，不要直接從靜態的 endpoint (也不要從 configuration 取得) 呼叫 IP2C 的服務，改成透過 Consul Client, 查詢可用的服務清單，從中取得服務的 endpoint 後再進行呼叫。

不過，如果這是對外的服務，這樣的做法其實並不洽當。對外應該有其它的 Edge Service, 或是 API gateway 等等服務來處理這些問題。這些機制較適合的場景，是內部服務之間的互相調用。這時要每個呼叫你的服務的 service, 都要自己寫一套查詢的邏輯其實不大合理，由該服務的開發團隊，自行準備 SDK 是較理想的做法。當然如果整個團隊共同使用一套通用的 service client 搭配 DI (dependency injection) 也是個做法。這邊我暫時拋開各種 http client 的最佳化 (例如 cache, reuse connect 等等) 還有 DI framework，先來示範這個做法:



```csharp

    public class ServiceClient
    {
        public static string ConsulAddress
        {
            get;
            private set;
        }

        public static void Init(string consulAddress)
        {
            ConsulAddress = consulAddress;

        }

        public static HttpClient GetServiceHttpClient(string serviceName)
        {
            // ToDo: add cache
            // ToDo: reuse httpclient for the same service instance

            using (ConsulClient consul = new ConsulClient(c => { if (!string.IsNullOrEmpty(ConsulAddress)) c.Address = new Uri(ConsulAddress); }))
            //using (ConsulClient consul = new ConsulClient())
            {
                var result = consul.Health.Service(serviceName).Result.Response;

                if (result.Count() == 0)
                {
                    throw new Exception($"找不到服務: {serviceName}.");
                }

                var list = (from x in result where x.Checks.AggregatedStatus().Status == "passing" select x).ToList();

                if (list == null || list.Count == 0)
                {
                    throw new Exception($"Service: {serviceName} was not found.");
                }

                Random rnd = new Random();
                int index = rnd.Next(list.Count);
                return new HttpClient()
                {
                    BaseAddress = new Uri(list[index].Service.Address) //new Uri($"http://{list[index].Service.Address}:{list[index].Service.Port}")
                };
            }
        }
    }

```

ServiceClient 最主要要解決的問題，就是在 GetServiceHttpClient() 這個部分。你只要傳入你想要呼叫的服務 ServiceName, 就可以取得 **可用** 的 HttpClient 物件。過程中 ServiceClient 會連線到 Consul 去查詢該服務是否存在? 同時也會確認該服務的 Health Checking 確認結果為 pass 的可用清單為何。最後如果有一個以上的清單被傳回來，目前的實作，是隨機挑選一個可用的 service instance, 按照他的資訊，傳回以初始化完成的 HttpClient 物件。

這邊尚未做任何最佳化處理，實際上的運用，health checking 結果的精確度應該在一秒以上，如果你有瞬間大量的查詢需求，其實可以透過 cache, 原則上一秒查詢一次就夠了，不需要每秒去 consul 查詢上千次... 但是隨機挑選的部分則最好每次都進行，這樣負載才會分配的夠平均。如果你有進一步的資訊，例如平均回應時間或是效能指標等等的統計資訊，你也可以改成更精密的挑選效能最佳的 instance, 而非單純的隨機挑選。

原本的 SDK 做一點調整，配合 ServiceClient 運作就可以了。我們可以初步測試一下效果是否如預期? 測是步驟我們可以這樣進行:

1. 啟動 Consul, 備妥 service discovery 與 health checking 的環境, 確認 consul webui 是否能正常連線?  
指令: ```consul.exe agent --dev```
1. 啟動一組 webapi, 確認 consul webui, 是否接收到 webapi #1 的註冊資訊，並且確認 health check 的結果都回報 pass ?  
指令: ```IP2C.WebAPI.SelfHost.exe -url http://localhost:9001```
1. 啟動一組 test-console, 確認是否都能正常呼叫 webapi 的功能?  
指令: ```IP2CTest.Console.exe```
1. 再啟動一組 webapi #2, 重複 (2) 的動作  
指令: ```IP2C.WebAPI.SelfHost.exe -url http://localhost:9002```
1. 停止 webapi #1 (按下 CTRL-C), 確認 consul webui 是否已經移除 webapi #1 的資訊? 同時觀察 test-console 的運作是否中斷?






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

這裡比較要留意的地方是，即使是容器化，你的 dockerfile 也不能亂包。要以這個服務能被彈性調度與重新組合為前提。其實在 SelfHost 的 code 裡面，我還加了一些 docker frinendly 的設計, 像是會自動偵測 container IP 的設計 (要註冊前總要知道自己的 IP 吧)。其實這些你要在 script 裡面處理 (powershell) 也不是不行，但是如果你有好幾個服務要容器化，會增加不少撰寫 dockerfile 的門檻。我實際上的做法是，SelfHost 會變成基礎建設的 base library 之一，所有需要使用的人只要 nuget 套件抓下來使用即可。標準化的作業，可以大幅降低容器化的過程 (撰寫 dockerfile) 碰到的困難。

這邊的 dockerfile, 我把 consul 的網址，與所在的網段 (network id, 用 192.168.100.0/24 這種格式) 拉出來當作環境變數來處理。自動偵測 IP 的困難在於，很多情況下你的 host 會有多個 IP，甚至除了 IPv4 之外還有 IPv6... 設定這個參數的目的是，讓程式自動從所有綁定的 IP 裡面，挑出符合該網段的那一個。預設是 0.0.0.0/0, 意思是所有 IP 都會符合，那麼我的偵測程式會挑出第一個。如果真的沒有符合的，就會用 loopback (127.0.0.1 或是 localhost) 來代替。

偵測 IP 的 code 我就不貼了 (再貼下去這篇內容就要爆了)。基本上用預設值就沒啥問題了。

接下來你熟悉 docker 的話，應該很容易就可以讓他跑起來了。我這邊準備了個簡單的 docker-compose.yml, 一次整組的跑起來:

```yml
version: '2.1'
services:

  consul:
    image: wcshub.azurecr.io/ip2c.consul:latest

  webapi:
    image: wcshub.azurecr.io/ip2c.webapi.selfhost:latest
    environment:
      - CONSUL_URL="http://consul:8500"
      - NETWORK="0.0.0.0/0"
    depends_on:
      - consul

  console:
    image: wcshub.azurecr.io/ip2c.console:latest
    environment:
      - CONSUL_URL="http://consul:8500"
    depends_on:
      - consul
      - webapi

networks:
  default:
    external:
      name: nat

```

細節就不多說了，實際跑整個環境起來看看 (webapi 跑 3 個 instance):

```shell
docker-compose up -d --scale webapi=3
```

這邊我沒有特別去設定 reverse-proxy, 也沒有設定 port mapping, 因此你想看 consul web ui 的話，在本機範圍內，用 docker inspect 的指令查一下跑 consul 這個 container 的 IP address 就能知道 IP 了，再開瀏覽器就能看到。

執行起來的結果跟前面一模一樣啊!






<!-- 

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

 -->
