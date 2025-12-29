---
date: 2019-04-19
datetime: 2019-04-19T00:02:49+08:00
timestamp_utc: 1555603369
title: "Container for .NET Developers 課程錄影公開"
---

想了很久，最後我挑了 3/27 這場的錄影，當作這次連開三場的課程代表: Container for .NET Developers. 感謝各位的熱烈支持，這次已經加開到三場了 (30 x 3 = 90), 票還是一樣都被搶光了..

這是微服務基礎建設系列的第二個主題，我的目標是讓 developer 了解為何該用 container 來發布你的 application., 更進一步的是了解如何配合 container 來調整你的 application 的設計方式。

因為團隊的需要，所以 demo 跟 sample code 我特地選用較冷門的 windows container, 因為這個環境才有辦法支撐目前團隊用的主流 .net framework.

整個內容，其實背後的理念，都是依照 12 factors app 的準則來設計的 (其實只是充分運用 container 的概念而已)。我用這樣的環境，示範了幾個常見的封裝的型態:

1. 被動的服務 (webapi): self hosting, 及 iis hosting
2. 背景服務: 用 console application + container ( 啟用 --restart always ) 來替代開發 windows service project
3. 服務的組態設計: application 開發時不需要過度考慮 configuration / port / volume / logging 的處理, 封裝成 container 時充分運用 ENVIRONMENT, port mapping 等等機制即可

中間也示範了 process / hyperv isolation 的差異，點出了 container 的安全性問題，process 的隔離層級，host 很容易透過 core dump 就把你的 application 記憶體內藏有那些東西摸透透了，需要高度隔離的應用應該採用 hyper-v isolation 來部署。同時也說明了 immutable server 的概念，與流程上的差異，如何讓 dev / ops 的權責與分工更明確。

最後，展示了幾個架構應用的情境:

1. 示範本機環境下，啟用正規的架構 (reverse proxy + 多個 webapi + worker + share storage)
2. 示範 scale out (reverse proxy 透過 dns roundrobin 來分散流量)
3. 示範 scale out (透過 consul - service discovery 來分散流量)
4. 示範 scale out (透過 message queue + worker 來分散流量)

其實這些東西要塞進 2hr 有點難啊，因此很多東西都是點到為止，我把主軸都擺在架構設計概念上，展示的案例只是讓大家眼見為憑而已，沒有太多時間逐一交代 source code. 這些細節若有機會另外規劃 workshop, 應該會在開另外的場次吧!

最後，這些其實都是為了下一次的內容作準備。去年我在 DevOpsDays 2018 介紹了 service discovery 的演進，一路介紹到當紅的 service mesh. 目前公司內的基礎建設也逐漸往這個方向轉移中。我們正準備把大型微服務的治理機制 (service discovery 及 configuration management) 都建置在 consul 上面, 這過程中沒有搭配 container 的話會很痛苦的，因此我才在中間安插了這場課程。

感謝這三場前來捧場的朋友們，沒報到名的也歡迎直接看影片。這些內容其實就是我們的內訓課程，如果你不只是想上課，還想要親自參與開發的話，我們也歡迎志同道合的朋友加入我們的團隊 :D。

若需要當日我的簡報，以及我示範的 IP2C 完整 source code, 可以直接 clone 我的 git repo:

Slides: https://github.com/andrew0928/Meetup/tree/master/20190320.ContainerForDevelopers

IP2C Services: https://github.com/andrew0928/IP2C.NET.Service

----
最後，預告一下下一次的內容，會以 service discovery 為基礎，介紹我們 91APP 內部如何搭建起跨不同開發團隊 (.net fx, .net core, node js) 的服務框架，整合 artifact management / configuration management / infra (as code) 的整合設計。有興趣的朋友們可以先參考我去年 DevOpsDays 2018 的錄影: https://www.facebook.com/andrew.blog.0928/videos/893802841007321/
