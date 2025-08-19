---
layout: post
title: "[架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?"
categories:
- "系列文章: 架構師觀點"
tags: [".Net Core","Docker","專欄","技術隨筆"]
published: true
comments: true
permalink: "/2016/05/05/archview-net-open-source/"
redirect_from:
wordpress_postid: 1218
---

開始之前，先來看一個實際的案例... [StackOverflow](http://www.stackoverflow.com)，開發人員很愛用的網站，每隔幾年都會在官方的部落格上面公布他的系統架構。來看看 2016 版的架構演進成什麼樣子 (原文: [Stack Overflow: The Architecture - 2016 Edition](https://nickcraver.com/blog/2016/02/17/stack-overflow-the-architecture-2016-edition/))


![](/wp-content/uploads/2016/05/img_572b734171d80.png)

為何我特地拿 stackoverflow 網站的架構當作例子? 其實這個例子蠻特別的，導致我幾年前第一次看到就留下深刻的印象。這網站核心的部分，其實都是用 .NET 開發的，包含 Web Tier 跟 Service Tier 都是。理所當然的，資料庫也用 Microsoft SQL Server。但是這麼大規模的網站，也混搭了不少的 Linux Server, 負責 Search Server (Elastic Search) 跟 Cache Server (Redis), 前端的 Load Balancers 也沒有用 Microsoft IIS ARR (IIS Application Request Routing), 而是採用了 Linux + HAProxy..

令我好奇的是，這種混搭的架構，一定會讓它的複雜度提高。我相信他考量的絕對不是 Windows Server 比較貴這種層次的理由 (畢竟他為了這架構，連管理用的 AD 都包進去了，還會搭配 Linux 一起使用一定有更強烈的動機)。複雜度的問題，包含系統架構層面，開發人員的能力經驗層面，網站維運層面都是如此。那麼，這樣真的是個好的設計嗎? 什麼情況下我們需要這樣的設計? 這樣的設計會有甚麼困難跟挑戰?

<!--more-->

過去講到 .NET v.s. Java, 或是 Windows v.s. Linux, 總是會變成像藍綠對決一樣... 所以我總是避免談論這類話題，免得被捲入意識形態之爭，尤其是在 Microsoft 是由 [Steve Ballmer](https://en.wikipedia.org/wiki/Steve_Ballmer) 當家的那個年代。換上 [Staya Nadella](https://en.wikipedia.org/wiki/Satya_Nadella) 上任之後，果然能精準地抓住開發人員在想什麼，一瞬間 Microsoft 什麼東西都跟 Open Source / Linux 這兩個領域靠了...。

從 .NET Open Source, .NET Core 開始可以在 Linux / MacOS 執行；Visual Studio 可以開發各種平台的應用程式；Visual Studio Code 可以跨平台；到現在連 SQL Server 都要推出 Linux 版本了..

這時我常被問到的問題就是，過去都抱著 .NET + Windows 的這些族群，要如何才能跟上 Microsoft 規劃的 Roadmap ? 以下就是我自己個人對這個問題的看法，純個人觀點...

# STEP #1, 看懂 Microsoft 的定位及策略

其實我也不知道 Microsoft 這些策略背後的目的，不過有一點是很明確的，就是 Microsoft 希望抓住開發人員，不論你是甚麼平台的開發者，你通通都要用 Microsoft 的產品及服務就對了。這點還不難理解，我舉幾個例子:


## 1. 用 Visual Studio 開發所有平台的 APP  

舉凡 //Build/2015 發布的 [UWP + 四大 Bridge Projects](https://developer.microsoft.com/en-us/windows/bridges) (雖然 Astoria - Android 子系統 project 已經掛掉了)，不過 Microsoft 仍然致力於用 Visual Studio 就可以讓你把別的平台寫好的 APP 直接轉成 UWP，在 Windows 10 上面執行。

反過來看也一樣，用 Visual Studio 寫一次就能發行到各大平台的支援也沒少過，包含 Visual Studio 內建支援 Cordova (HTML5 + CSS3 + JavaScript 開發跨平台 APP)，已及 //Build/2016 才宣布 Visual Studio 將內建 Xmarian, 用 Native 的方式跨平台開發 APP。

另外，[上週才看到的消息](https://blogs.msdn.microsoft.com/vcblog/2016/03/30/visual-c-for-linux-development/)，Visual Studio 也開始支援開發及編譯出 Linux 能執行的 Code 了...


## 2. 用 .NET Core 開發所有平台的 Server Side Application  

Microsoft 除了開發工具要搶占市場之外，開發的平台及語言也沒閒著 (.NET Core / C#)。一樣在 //Build/2015 才大動作發表的 .NET Core, 現在已經 RC2 了。

包括 Runtime, 編譯器, BCL (Basic Class Library), 通通都 Open Source。不再需要靠第三方的 Mono Project，直接靠官方支援就已經可以直接在 Windows / Linux / MacOS 上執行 ASP.NET...


## 3. 用 Visual Studio Code 當作所有平台的 IDE 第一選擇

除了 Windows 平台上面的 Visual Studio 之外，Microsoft 也極力發展跨平台的 IDE: Visual Studio Code, 如果你有必要在其他平台 (非 Windows) 上面寫 Code, 那就是 VSCode 了，雖然才剛 1.0 release, 不過反應還不錯，再過一兩年應該大有可為

> 2017/11 更新: microsoft connect 2016 也 announce 了 visual studio for mac, visual studio code 也推出了 x64 的版本, visual studio 家族跨的平台也越來越豐富了

## 4. 用 Windows 10 / 2016 當作所有平台的開發環境

排除行動裝置，SERVER 端的執行環境就兩大派: Windows / Linux。封裝佈署方式現在最當紅的就是 Container (Docker)，這些也全都在 Microsoft 規劃的支援範圍內，你用 Windows 通通可以搞定..

Container, Windows 2016 開始支援 Windows Container, 以後 Windows Application 也可以開始用 DockerFile 來 Build Container Image, 用 Docker 的方式快速的佈署。對於 Linux Kernel 的 Container 支援也沒漏掉，Microsoft 與 Docker 也密切合作，Docker for Windows 也有大改版 (Beta Now, 無奈我一直都排不到 beta tester @@)，原生支援 Hyper-V 當作底層的虛擬化環境，為了讓使用體驗更好，Hyper-V 也開始加入了 Nested Hypervisor Support。

另外一個值得注意的趨勢是: Windows 10 將會內建 Linux Shell, 可以原生的執行 Linux ELF 格式的執行檔 ( under user mode only) 而不需要重新編譯。這部分我腦補一下，如果再發展下去，也許以後 Windows Container 也能執行 Linux 版本的 Container Image 也說不定...

> 2017/09 更新: 事實證明，我猜測的方向對了，只是最終 Microsoft 端出來的 Solution 猜錯了。Windows Server 2016 將來
> 的確可以直接執行 Linux Container 沒錯，只是他靠的不是 WSL (Windows Linux Subsystem), 而是靠 Hyper-V Container,
> 搭配 Linux Kit 直接在 Windows 上面執行 Linux Container。
>
> 參考今年四月份的消息: [DockerCon 2017: Powering new Linux innovations with Hyper-V isolation and Windows Server](https://blogs.technet.microsoft.com/hybridcloud/2017/04/18/dockercon-2017-powering-new-linux-innovations-with-hyper-v-isolation-and-windows-server/)


## 5. 用 Microsoft Azure 當作所有服務執行的平台

最後輪到雲端了，Azure 已經不向當年 2009 剛推出時的狀況，只支援 .NET 而已... 現在不僅可以直接 Create Linux VM, 甚至你需要各種 Linux / Open Source 的服務，都有整理好樣板給你使用，只要點幾下滑鼠，服務就已經佈署好等你使用..Azure 平台不再是只提供 Microsoft Solution, 而是你需要什麼上面都提供，只要你 Hosting 在 Azure 上面就好。

看到這邊，我開始了解 Staya 講的 "Mobile First, Cloud First" 是指什麼意思了。過去 Microsoft 都在把所有東西綁進自家的 "Platform"，但是現在更像是提供 "Applications &amp; Services"，因此 Microsoft 的策略，講的更白話一點應該是這樣:

從過去的 "Mobile (Platform) First, Cloud (Platform) First", 轉移到 "Mobile (Application &amp; Services) First, Cloud (Application &amp; Service) First" 才對。




# STEP #2, 個人該如何轉變?
這真是個大哉問，你得先知到目標在哪裡，才能知道你還欠缺什麼，也才能知道你該改變什麼，以及如何轉變...。我就先大膽假設一下好了。假設將來的環境，已經不再有 Windows / Linux 的隔閡，你可以盡你所能的挑選最棒的元件，用最適合的架構來規劃你的 service 時，你會怎麼做?

沒錯，這就是我一開始舉 StackOverflow 當作範例的原因。StackOverflow 很明顯的就是挑選他需要的領域內最棒的 Solution，來搭建他的服務。不過這樣的混搭設計，不論在開發、維運、測試及除錯等等的門檻都提高不少，有些規模或能力較差的團隊往往會望而卻步。

不過，如果 Microsoft 的策略成功，那麼以後像 StackOverflow 這樣的架構就是垂手可得的，不再有現在的高門檻...。不需要大規模佈署 (只有一台 Server 也行)，不用投入大量資源，開發團隊及維運團隊也不需要橫跨兩大陣營來打造服務 (只要熟悉 .NET Core 就行)。佈署及管理都可以在彈指之間完成... (只需要熟 Docker 就行)。

我就用我理想中的技術及架構，來重現同樣的組態吧:

![](/wp-content/uploads/2016/05/img_5728e4415f238.png)

如果你正好看過我前一篇文章 ([Rancher – 管理內部及外部 (Azure) Docker Cluster 的好工具](http://columns.chicken-house.net/2016/04/29/rancher-on-azure-lab/)) 的話，就會知道這環境非常容易就可以架設起來，這樣的架構是非常容易達成的。這其中有幾個關鍵技術，我個人非常推薦過去是 Microsoft 陣營的開發人員現在就去學習，包括 .NET Core、Open Source 常見的主流元件、以及容器化技術 Docker 。這三項分別代表了開發、主流元件、服務佈署三大領域。


以下我就分別從開發、IT架構、以及人員能力養成三個角度來探討:

## DEV: 開發架構上的考量 - 盡早轉移到 .NET Core

我挑選 StackOverflow 當例子，很大的原因是他 WEB 採用的是 C# / .NET 的 solution. 雖然目前 Open Source 都還是以 LAMP Stack 為大宗，開發語言 PHP 的能見度最高。不過單就 Language 來看，我覺得 C# / Java 才具備大型或是複雜的架構發展，主要原因就在於語言本身給你多大的發揮空間。然而 C# / Java 又受限於背後的老大: Microsoft / Oracle 投入多少資源去發展他。

既然我會在這邊寫這篇，我當然是看好 C# 語言本身的發展 (否則我也不會寫這篇了: [//build/2016 – The Future of C#](http://columns.chicken-house.net/2016/04/09/build2016_csharp7_preview/))。有 Andres 大神在背後支撐，加上地表最強的 IDE: Visual Studio，實在沒有不用的理由。為了後面的 IT 佈署考量，戰略上升級到 .NET Core 是絕對值得的，一來進可攻，你有機會直接佈署到 Linux 或是 Docker 的環境；二來退可守，你要留再 Windows Platform 也是很好的選擇。至少你的開發團隊就不用為了將來佈署的問題傷透腦筋。過去我看過太多例子，為了佈署問題而遷就不是最佳的開發技術。

架構中其他的服務，如 Cache (Redis, Memory Cached ... )、Reverse Proxy (Apache, Nginx, HA Proxy ...) 等等，對於開發人員來說，不熟 Linux 及 Redis 安裝設定也不再是個問題了，因為 Docker 已經幫你從安裝設定的地獄中解放出來，你只要挑選官方或是高手預先包裝好的 Container 就一切搞定。Redis 在此架構中是用來提高效能的服務，而非自己開發的服務。採用 Container 是最簡單的取得方式。

有了 Microsoft .NET Core 的背書，加上 SQL Server 也即將在 2017 推出 Linux 版本，這整個架構到底要挑選 Windows or Linux，突然間就單純的是需求問題，而不是政治問題了。你可以放心的使用 C# 來開發你的應用程式，佈署階段則可完全以維運為主要考量來評估。不論你選擇哪個平台，都會有對應的 Container 容器化的技術供你使用。

這段的最後補充一下參考資訊，StackOverflow 有三篇文章值得一看:

1. 系統架構設計: [Stack Overflow: The Architecture - 2016 Edition](https://nickcraver.com/blog/2016/02/17/stack-overflow-the-architecture-2016-edition/)
1. 硬體設備: [Stack Overflow: The Hardware - 2016 Edition](https://nickcraver.com/blog/2016/03/29/stack-overflow-the-hardware-2016-edition/)
1. 開發流程 CI 作法: [Stack Overflow: How We Do Deployment - 2016 Edition](https://nickcraver.com/blog/2016/05/03/stack-overflow-how-we-do-deployment-2016-edition/)





## IT: 架構設計上的考量 - 盡早採納容器化的佈署管理方式 (Docker)

前面看的出來，開發已經跟佈署脫鉤了，關鍵技術就是 Container (Docker)。因此在系統開發階段，只要確保每個服務都能夠容器化，包裝成 Docker Container 後，就萬事具備了! 接下來 IT 規劃就只要靠 Docker Swarm 來建立整套的 Docker Cluster，去承載這些 Containers。如果不敷使用，還有更進階的 Mesos，甚至是 DC/OS (Data Center OS) 可以使用。不想自己養機器? 這些服務也在 Microsoft Azure 上有現成的 Azure Container Service, 直接替你準備好環境。

至於這些 Containers 之間的關係，還有 Scale 等等組態，交給 Docker Compose 就可以了，有興趣的人用這關鍵字就可以知道詳細用法，我就不多說。這些都是縣在現有垂手可得的資源，不是遙不可及的技術。如果你需要的規模不大，也許實體的 Server (Docker Swarm Node) 只要兩三台就能搞定。如果你的資源足夠，也有大流量的需求，這規模擴大到上百台 Server 也不是問題。甚至你要擴充到上千台或是上萬台，用更進階的 DC/OS 也同樣的能滿足你的需求。

目前 Windows Server 2016 還尚未 Release, 截至目前為止也才 Tech Preview 5 而已，離正式發行還好一段時間。雖然 這版已經開始支援 Windows Container 的技術，也支援標準的 Docker API。雖然目前版本還有很多限制，Windows / Linux Container Image 也都還無法互相混用，不過上面的架構也已經開始有能力用 Windows 環境架設出來了，我相信在 Microsoft 未來的 Roadmap 裡一定會有更好的互通性，來進一步簡化這樣的架構建立及維護門檻。

上述架構的說明，我都是以 Docker 官方的技術為主 (Docker Swarm, Docker Compose) 來說明。如果你採用我上篇介紹的 Rancher，那麼整個架構跟組態就更容易了。有內建的 Load Balancer Service 可以使用，Scale Out 也只要在介面上直接按下你要的個數就結束。



## IDP: 個人的學習及發展計畫 - 趕緊熟悉這一切

看到這些技術整合起來的威力了嗎? 沒錯... 這些就是我在半年前初次接觸 Docker 時就看到的未來，也是因為看到這樣的威力，我才願意花時間去學習我原本一竅不通的 Linux ，學習怎麼使用 Docker，熟悉這個生態裡常用的 Apache / Nginx / HA Proxy / .... 等等服務，為的就是這一刻啊...

也是因為這樣，我思考了很久，我的目的並不是去跟 Linux 很強的人來競爭，我的目的是用最快最有效率的方式來進入這個領域。只要了解每個服務的特色及使用時機，我就有足夠的知識來調配最佳的架構。對於原本就是 Microsoft Solution 的人們，要跨入這樣混搭的最佳途徑就是熟悉這三件事:

1. 熟悉 Docker 容器技術 (不論將來你是用 Windows / MacOS / Linux 的 Docker Engine)
1. 熟悉 Open Source 架構的幾個重要服務 (如 Nginx, HA Proxy, MySQL, Redis ... 等等)
1. 盡快的將你的開發技能及開發平台，移轉到 .NET Core


# 結論
寫了這堆，難得沒貼到 Screen Capture，也沒貼到 Code .. 算是把過去半年我為何極力的轉換領域的原因做個整理，寫下來的心得。我想跟大家分享的是，過去這半年我不是漫無目的趕流行才研究 Docker 跟 .NET Core 的，而是看到未來的轉變，有計畫的進行。

其實我分享的這些內容，對我自身來說我也是初學者，所以論深度及廣度應該都比不上早在 Linux + Open Source 打滾多年的前輩。所以我鎖定的對象，是跟我一樣過去都是以 Microsoft 陣營為主的開發人員為主。我想我們會碰到的問題跟障礙都差不多，希望我的分享會對你們有幫助 :D
