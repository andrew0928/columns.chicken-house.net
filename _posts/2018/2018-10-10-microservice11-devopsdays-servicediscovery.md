---
layout: post
title: "DevOpsDays 專刊: Service Discovery, 微服務架構的基礎建設"
categories:
- "系列文章: 架構師觀點"
tags: []
published: false
comments: true
redirect_from:
logo: 
---

其實，類似的主題 ([微服務基礎建設 - Service Discovery](/2017/12/31/microservice9-servicediscovery/)) 去年底就已經寫過一篇了。不過這次有幸投稿 DevOpsDays Taipei 2018 有幸榮獲大會青睞，能上台講這個主題，加上工作上開始使用 Consul 也有一陣子了，對於 Service Discovery 的看法又有些進化了。於是決定趁著準備這次演講，除了 Slides 之外，也來個文字版的文章吧! 比起演講，我還是用寫文章的形式比較好發揮。

這次我換個角度，介紹 Service Discovery 的基本觀念，以及應用的方式。我分三個部分進行:

1. Basic: Service Discovery for Developers
1. Advanced: Case Study
1. Next: Service Mesh

<!--more-->


所有微服務相關的文章，可以直接參考下列的導讀。

{% include series-2016-microservice.md %}






# BASIC: Service Discovery for Developers


# ADVANCED: Case Study


# Next: Service Mesh









--------------------------------------------------------------------------------------------------------













從微服務化開始，面臨的第一個問題就是你該如何管理你旗下的這堆內外部服務? 要有條理的管理好這堆服務，可是件苦差事 (雖然技術上不是件難事)。這是你的服務能不能維持在一定複雜度之下持續發展茁壯的重要關鍵。對於 developer, 這是個較陌生的課題，因此在今年 DevOpsDays Taipei 2018, 我準備了這個 session, 準備從 developer 的角度來看待這件事，要介紹的就是 service discovery, 微服務架構下最重要的基礎建設。

DevOps 這議題，最難的都不在 Dev 或是 Ops, 而是在整合。微服務架構的興起，給這兩種專長的人很大的挑戰。越來越複雜與靈活的架構要求之下，只懂 Dev 或是 Ops 領域的技能很難在這個時代有所突破。因此這次我特別挑了這個主題: Service Discovery, 它是微服務架構下，必要的基礎建設。然而這些基礎建設並不是裝好拿來用就好了，開發人員必須充分的掌握它的特性，去思考如何更靈活的運用它才能更有效的解決你的問題。

這篇我不會從 service discovery 的基礎開始談起。想看基礎建紹的可以參考我去年寫的這篇: [微服務基礎建設 - Service Discovery](/2017/12/31/microservice9-servicediscovery/)。我這個 Session 會從應用面，來說明 developer 面對問題時應該如何解決? 該如何善用 service discovery 的服務 (我用 HashiCorp Consul 當作示範) ? 架構上該如何安排與規劃?

我會先假設參加這個 Session 的朋友們，或是看這篇文章的讀者們，已經有基本的分散式系統開發經驗。概念與架構的部分我會參考這本書: Designing Distributed Systems, Patterns and Paradigms for Scalable, Reliable Services; 由 O'reilly 發行的書籍。Microsoft Azure 也很佛心的提供免費電子書下載 ([free ebook download](https://azure.microsoft.com/en-us/resources/designing-distributed-systems/))，裡面涵蓋了各種分散式系統的參考架構, 你可以把它當成微服務版本的 design pattern 來閱讀。

<!--more-->

# 導讀: 微服務架構下，服務管理的挑戰

微服務的主要訴求，就是透過切割服務，將龐大複雜的系統，轉變為數個獨立自主的小型服務組成。每個服務專注且單一，複雜度隨之下降。微服務架構所有的好處都源自這個改變。切割得宜的話，每個團隊只需要負責維護各自的服務即可，降低了共同維護單一大型系統帶來的複雜度。服務的介面為各自定義的溝通介面 (interface)，在這個 interface 維持不變的前提下，各個服務與團隊，可以自行決定內部的實作方式與採用的 tech stack / language / framework, 面臨技術轉移的情況時，也能降低轉移與維護的複雜度。

不過，在單體式應用 (monolitch) 轉移到微服務 (microservices) 的過程中，第一個面臨到的就是如何管理大量 (包含種類與個數) 問題。舉例來說，你應該會碰到:

1. 同時有這麼多 "種" 服務在運行，我如何隨時掌握每個服務能不能正常運作? 以便我做出正確的應變措施?
1. 每種服務同時有這麼多 "個" instance 在運行，我如何隨時掌握這些 instance 的狀態，以便決定要對哪個 instance 發出 request ?
1. 我如何快速又精準的找到我要呼叫的服務在哪裡? (service or instance, endpoint, address, port, ... etc)
1. 我如何確保這些服務的組態 (configuration) 是正確一致的? 組態改變時如何確保能立即生效?

更進階一點的問題:

1. 多租戶架構下，我如何保留固定的運算資源 (DB, 保留的 service instances) 給特定的用戶，提供不同等級的服務保證 (SLA, service level aggrement) ?
1. 我如何能更精準的調節服務之間的通訊? 而非透過統一的 API Gateway / Load Balancer, 避免這些匝道變成單一失敗節點, 或是效能瓶頸? (Service Mesh)
1. 如果以上問題都能透過 Service Discovery 處理，那我的服務啟動時，該如何找到 "服務發現" 的服務? 該如何找到 "組態管理" 的服務在哪裡?

這些問題，如果你都不知道怎麼做，或是怎麼做才到位? 那就是這篇文章主要要說明的內容。這些內容其實並不難，但是他橫跨了 Dev(開發) 與 Ops(維運) 兩種角色，這對大部分的團隊來說是一大挑戰。熟悉 Dev 的團隊，往往會傾向自行開發一整套的 framework 來解決這些問題，而忽略了目前已發展成熟的各種 OSS 解決方案。熟 Ops 的團隊往往過於熱衷用最新的服務搭建各種基礎建設，但是卻忽略了自身的 application 沒有辦法很好的整合或是充分利用這些優點....。

因此，我這篇文章的定位，主要的目的在於打破中間的隔閡，對象我定位在 Dev (開發人員)，我希望能從開發人員的角度，讓開發人員了解這一整套 Service Discovery 在架構上搭配的做法，同時反思該如何應用在自己的服務開發上。只有做好整合的環節，才能順利發揮最大的效益。

因此，下列的介紹我分三部分進行，分別是:

1. BASIC:    Service Discovery Overview, 重點複習 Service Discovery 的幾個重要觀念
1. ADVANCED: Consul 應用案例 (參考: DDS, Designing Distributd System)
1. FUTURE:   新一代的微服務架構, Service Mesh





## BASIC: Service Discovery Overview

先交代一下 Service Discovery 基礎的部分。這邊會跟後面的應用有關，我交代一下基本觀念。詳細的部分可以參考 [這篇] 的說明。在討論架構時，我喜歡倒回來講，先從目的來談，再來談作法。Service Discovery 的目的是替整套系統，維護並且提供一份完整的服務清單 (包含到每個 service instance)。你要呼叫任何其他服務之前，只要向它查詢後得知該服務 (精確到 instance) 的資訊，就能夠進行後續的服務調用的動作。

為了達成這個目的，有幾種常見的 design patterns 可以參考。通常有三個部分需要搭配:

1. 使用服務的部分 (client)
1. 被呼叫的服務 (service), 以及提供服務的個體 (service instance)
1. 協助雙方找到服務的基礎建設 (service discovery)

服務啟動的基本的流程是:

1. service instance 啟動, 向 service discovery 註冊自身的資訊 (service name, address, port)
1. service discovery 收到註冊資訊後，加入 service list。並且按照定義的 health check 方式，定期確認該 service instance 的健康狀態。
1. service instance 關閉或是超過約定時間都無法正常提供服務 (透過 health check 確認的資訊)，則將之從 service list 剔除。

若 client 需要調用 service 提供的服務時，基本流程是:

1. client 向 service discovery 查詢可用的 service list 資訊
1. 根據條件 (剔除無法提供服務的 instances) 隨機從 service list 中挑選一個 instance
1. 按照 service instance 登記的資訊 (如 address, port), 按照 API 的規範調用該服務

基本上，只要服務的註冊跟健康偵測有做好，這樣的流程就足以解決大部分的需求了。用 UML Sequency Diagram 來表達一下這過程:

// sequency diagram




## BASIC: Config Management

暫時先跳離 service discovery 這個主題，來談談微服務架構下另一個常面臨的問題: 組態管理 (configure management)。

組態管理，也算是治理眾多服務能力中的一環。就拿我熟悉的 .NET 為例就好。ASP.NET 多年前就標榜可以 "xcopy deploy", 將組態管理的責任，從當年盛行的 registry (windows 本機的註冊機碼) 中解放出來，改成從 files 就能完全解決的做法，我只要靠 xcopy 的指令，把所有的 code, contents, config file 部署到目標 server, 就能完成部署。

不過這樣的做法，是否依然還適用於微服務架構? 在一些更細膩的管理上，file based 的做法明顯不足。舉例來說:

1. 當我的組態資料庫多達數 MB 時，我還要每個 instance 都複製一次?
1. 當我採用 containers, 服務高達上千個 instances 時，我也需要都複製一次?
1. configuration 能否有更細膩的管理? 例如組態的權限管控，局部設定變更的通知，組態的異動 API ，甚至幾種常見的異動過程的 (如 lock)

在微服務架構下，面對數十種不同的服務，每個服務也都同時有數十個不等的 instance 在運行，這堆 instance 之間的組態管理看來也需要專屬的服務來維護了。常見的做法不外乎有某些專屬的服務來負責 config (例如 consul, etcd, zookeeper..), 同時每個服務按照這個程序:

1. 系統建置之初，就將組態管理是為整個微服務架構的基礎建設來看待。預先建立與載入組態設定。
1. 每個服務在啟動之初 (例如 container start, 或是 provision VM), 就應該向 config manager 註冊，並取得必要的組態資訊，啟動自身的服務。
1. 服務啟動後，註冊的目的是要能監聽重要的組態設定值是否異動? 有異動的話必須主動做出反應，或是應該立即安排重新啟動以便載入正確的設定值。
1. (3) 的情況也有可能反過來，是你的服務嘗試去修改特定的組態設定。這時應該透過 config manager 提供的 API 進行。

了解了這個過程，知道為何我會把 config management 跟 service discovery 兩個主題擺在一起講了嗎? 這兩者之間有不少共通點:

1. 都屬於建構微服務架構的 system 必要的基礎建設
1. 服務啟動的過程中，都需要向這些服務註冊與取得必要的資訊，才能順利啟動完成
1. 過去傳統應用系統的 config, 同時包含了 service definition, 跟其他的 config values (如 switch, mode selection, limit settings ... 等等)。這些內容因應維護與管理的方式不同，分別歸由 service discovery 與 config management 基礎服務分別管理。

也是因為兩這之間有這些共通點，大部分的 service discovery 都同時涵蓋這兩個領域，或是底層的 storage 都會採用有對等能力的分散式儲存系統。最典型的案例就是高整合度的 consul, 官網就直接標示四大特色 (service definition, failure detection, key-value store, multiple datacenter) 就直接包括在內。另外 etcd 也是個案例，甚至是直接由 config management 發展到跨界到 service discovery 這個領域。另外 Netflix OSS 提供的 Eureak, 底層也是藉由 Cassendra 來提供對等的機制。

這也是為何我會在自己的專案上選擇 Consul 的原因了。Consul 是後起之秀，憑藉的是高整合度的服務，我不需要建置一堆基礎設施，就能開始建構微服務架構的系統了。Consul 內建這幾個主要功能:

1. Service Discovery
1. Health Checking
1. KV Store
1. Multi Datacenter
1. Secure Service Communication (新功能，後敘)

如果你有看完我前面講的那堆處理細節，你就不難想像: 這些機制都是在服務啟動的那瞬間，以及服務要被呼叫的那瞬間會發生的事情。如果這些機制都來自不同的基礎建設，那你會花多少心思在整合這些基礎建設身上? 這些不是我主要的目的啊! 因此當我自己都扮過黑手自己搞過一輪之後，我真正要用在 production 上的 solution, 自然是挑選整合度最高的解決方案；尤其是他來自 HashiCorp 這公司，也是在雲端服務的基礎建設領域頗有名氣的公司，旗下的 Consul 自然也有一定的水準與可靠度。

好，這篇其實不是葉佩雯，誇獎就到此為止。基本的概念介紹也到此為止，講這些只是為了交代我推薦他的原因而已。接下來下個段落，就來看看一些實際上的應用案例，體會一下 Service Discovery 如何解決你的問題。


# 應用案例

先從單純一點的架構開始吧。為了後面更進階的應用，我只打算把 API Gateway / Load Balancer 這類的服務用在對外的 endpoint 上。系統間服務與服務之間的呼叫會很頻繁，我就不再內部也採用這種集中管理的控制機制了。一來阻隔了內部更靈活的運用彈性，也容易造成單一節點失敗，或是造成通訊的瓶頸。

## client side discovery

如果不透過 load balancer, 那麼服務要如何調用其他的服務? 尤其是在被呼叫的服務同時有好幾個 instance 在運作中的狀況?

// 圖:   client [sd client] ---> target service(s)

// cache problem
// consul node loading : depends on client node(s), not request count(s)...
// health check 確保服務清單的正確性與可用性。如果 hc 的頻率是 5 sec, cache TTL 應訂在 1 sec 左右。


## client side discovery with taggings

接著來點變化題，如果我的客群就像一般的 SaaS 服務一樣，有 free / basic / premium 三種等級的用戶，我想要替這些客戶分別保留不同的運算資源 (有點類似電信公司分配流量的集縮比一樣的作法)，那該怎麼做? 如果照過去的搭配 load balancer, 那你現在只能架設三組了, 前端還必須分別打三個不同的 load balancer 的 end point... 如果更極端一點，有些客戶付了更多錢，要用專屬保留的運算資源怎麼辦? 這種狀況在 Azure 上很常見啊... 哈哈...

如同我一直在不同文章都在強調的，你不需要時時刻刻都重新發明輪子，但是軟體界的變化速度很快，尤其現在的服務拚的都是整合。你的業務需求很有可能無法由單一的 solution 獲得而來，這時你有沒有自己打造輪子的經驗跟能力就變的很重要了。過去如果你過度依賴基礎建設幫你搞定這些資源管理的問題，現在就會束手無策。我們來看看這個案例應該怎麼搭配 service discovery 來設計架構:

// 圖:   client [sd client + tag filtering] ----> service(s) with tag:A, tag:B, tag:C-0001, tag:C-0002...

看到 developer 能自己掌控這些基礎建設該如何運用的彈性了嗎? 這個例子的架構，其實跟上一個沒有差多少，就是在 query service list 跟決定要呼叫哪個節點的邏輯有些不同而已 (完全 Random with 過濾 taggings 後 random)，但是你能應用的範圍與彈性就瞬間大了許多。這類的應用，你要單純靠標準的基礎建設也不是辦不到，但是光是 product owner 要跟 developer 溝通規則，然後 developer 要再跟 infra operator 溝通這些規則怎麼變成硬體的設定... 怎麼看都是個大工程。



## side car model

開始來點變化題吧。藉由 service discovery 的協助，你的 application 能夠很快地掌握其他 service 的 endpoint, 以及他的健康狀態, 是否目前是否可用。那麼，你該如何找到 "服務發現" 服務在那裡? 以及他目前是否可用?

這是個雞生蛋蛋生雞的問題，解決的方式各家提供的方式也都有些差異，我就針對 Consul 為例來說明吧! Consul 很巧妙的利用 "side car" 的模式來打破這個無限自體循環...

首先，Consul 本身支援 client / server 兩種 mode, server 會真正保存資料，執行 health check (http or scripts), 也會回應 restapi 的各種查詢。client 就單純的多，單純只接受 restapi 的查詢，並且把 request forward 給 server 處理。

要讓每個 service 在什麼資訊都不知道的情況下，要精準的定位 Consul Server 是有點困難的，但是如果這問題縮小到 Consul Client / Server 要精準的定位 Server 就簡單的多，Consul 支援 LAN Gassip Protocol (翻譯: 八卦協定 XDD), 能用 broadcast message 的方式找到 Consul Server(s)。

技術細節就不管了，我們直接來看該怎麼配置與應用。如果 Consul Client 能自動找到最適合的 Consul Server 的話，那麼我只要在每台 Host (VM or Container 都可) 都部署一套 Consul Client, 那麼我的 application 只要從 http://localhost:8500 就能透過 Consul Client 聯繫到 Consul Server, 就能取得所有必要的啟動資訊 (service definition, KV store) 了啊! 這種每個 host 就搭配一個 client 的做法，就如同 side car 一般，每輛機車旁邊就掛一台小車一樣，也因此而得到 side car 這個稱呼。

只要 Consul Client 本身的 memory footprint 夠小，不造成負擔，這是個很方便的做法啊! 這可不是亂搞的，連 DSS 這本書 (Designing Distributed System) 裡面都有記載:

// P13, Figure 2-3. A sidecar example of managing a dynamic configuration

書上的這個範例，是藉由 sidecar, 讓不支援這些新技術的 legacy application, 能順利的透過 config management 取得組態並執行的做法。這架構藉由 sidecar 取得 config, 並且轉成 legacy application 能認得的 config file (EX: ASP.NET 的 web.config 就是一例), 讓老舊的 application 也能享受到 config managment 帶來的好處，不用改一行 code 就能集中管理 config。

同樣的模式，如果這個 sidecar 還能提供 service list query 的服務呢? 這就是 consul client 典型的部署方式。你的 application 連 consul server 的 IP 都不需要知道，就能搞定整個啟動程序了。這小動作有多大的效益?? 你如果經歷過要自己手動設定 IP address 才能上網的年代，你才能體會到有 DHCP 是多幸福的一件事，是同樣的道理。

回過頭來，Consul 能否像 DSS 這個案例一樣，讓我連 code 都不用改也能享用到 Consul 帶來的好處 (service discovery + health check + kv store) 呢? 有的。Consul 另外提供一個好用的 tools: Consul-Template。

你只需要先編好屬於你的 template, 交給 consul-template。這個工具會 watch consul server 的狀態，如果你的 template 內用到的變數有任何異動，就會觸發 consul-template 重新用新的數值，重新按照 template 更新 config file，需要的話也可以一起執行你指定的 script (例如 nginx -reload, 或是 iisreset ...)。這些機制搭配得宜，你的 legacy application 馬上就有自我組態的能力，你在進行大量部署時就會容易許多，要搭配 cloud 進行 auto scaling 就更容易了，你只需要把組態跟設定都般到 consul 就可以了...。




## service mesh

其實這幾個架構設計案例，這樣的介紹順序是有目的的；藉由 service discovery 建構起來的基礎，一步一步的從集中式的架構 (透過 LB or APIGW), 逐步進化到 service mesh。

在上個範例中，sidecar 的做法，是在每個 host 都部署一個 service discovery 的服務，來解決該如何找到 service discovery 服務的問題。找到 service discovery 服務之後，接下來的動作仍然一樣，需要查詢服務清單，並且用安排好的規則挑選一個出來，定位要呼叫的服務資訊之後，進行 API 的調用。

這些過程過度依賴開發人員在 application 內撰寫相關邏輯，屬於侵入式的作法。其實在上一篇文章就有提到，侵入式的作法有幾個明顯的缺點:

1. 更新困難。需要重新編議與部署相關服務
1. 全面更新需要時間，無法一次全部到位
1. 技術相依，若系統混用不同的開發技術或是框架，相關邏輯需要分別撰寫，難以維護維持絕對的一致性

雖然採用 LB / APIGW 沒有這些缺點，但是過度集中式的管理也造成擴展的限制與瓶頸。不過如果把 APIGW 跟 sidecar 結合在一起應用呢?

這就是 service mesh 的概念了。來複習一下，配合 service discovery 每個服務的生命週期都要做好這些事:

1. reg
1. dereg
1. health check

要調用其他服務，每個服務都要進行這些程序:

1. query service list, get end points
1. invoke

上述這些事情，能否統一都交由 sidecar 代勞? 試想一下，如果 sidecar 本身就能代為處理 reg / dereg / hc, 同時 sidecar(s) 之間能精準的互相溝通與定位 (query service list, get end points), 若 sidecar 還能代理雙向發布搭配的服務與被呼叫的服務 (如同 APIGW / reverse proxy 一般)，那麼對 application 而言:

1. service discovery 服務就在我家 (localhost), 我不需要再花費功夫處理啟動的程序，也不需要花功夫處理 config mgmt 的問題。
1. 透過 side car 來代理我的服務，我不用再擔心別人如何找到我
1. 若 sidecar 也能代理其他人的服務，我在 localhost 就能直接調用
1. sidecar 之間的溝通，因為都是同一套系統，sidecar 也非侵入式的 solution, 因此也沒有跨平台或是不同開發技術的問題

這麼一來，開發人員可以不需要花費太多力氣去處理這些細節，相對的開發團隊就能更輕易的掌握 service mesh 這樣複雜動態的架構了。服務之間的通訊可以完全由基礎建設來掌控，通訊自動加密，自動調度，非集中式的通訊，也避免了單一節點失敗造成系統可靠度下降，或是單一環節變成整體的瓶頸等等問題。

回到實際的案例來，Consul 也提供了對應的功能，叫做 Consul Connect: 


// references




# 結論

寫到這邊，我這篇文章其實想表達的概念，就是:

身為 developer / architect, 我想讓大家了解，很基本的 service discovery, 在 architect 的手中若能妥善規劃與應用，搭配你的開發能力 (而非只是改改設定或是架設網路)，其實能夠解決非常多棘手的問題的。在這個什麼都講求整合的時代，這樣的知識與技能格外重要。我這篇文章就是想從 service discovery 的架構設計案例角度切入，帶出這些 patterns。

只看 patterns 其實很虛，因此我在思考這些 design 時，我都會找一些實際的工具或是服務來驗證是否可行。Consul 就是我在研究與學習過程中挑選出來的一套。我會推崇這套 service discovery 的服務，原因有這幾個:

1. 平台支援友善 (linux, mac, windows), 開發技術支援友善 (SDK include: .NET Java ...)
1. 工具支援友善 (EMS, consul-template)
1. Legacy Application 支援友善 (support DNS interface, support consul-template for config file based system)
1. 服務本身整合度高 (UI, include KV-store, health check, support multi-datacenter)
1. 架構延伸性高 (sidecar, connect), 未來性強 (service mesh)

不過我還是提醒，別被工具綁住了。你一但被工具約束了，你就是工匠，而不是架構師了。務必在思考解決方案時能保持技術的中立性。這整篇文章介紹的架構，雖然我都拿 Consul 當作實際應用參考，但是不代表只有 Consul 做的到。只要你對其他 service discovery 服務的掌握度夠高，同樣的架構你搭配 Eureka, Etcd, Envoy, zookeeper..., 甚至更底層的 K8S, docker swarm, DC/OS 等等其時也都能達成同樣目的，差別只在於整合過程中你需要花費多少 effort 而已。

身為架構師，最有成就感的就是，你的一念之間，你的設計與決定，可以影響到整個團隊。你決策的品質，直接影響了團隊能用多小的資源，解決多大的問題。這也是促使我持續鑽研這些 know how 的動力來源。看完這篇，你是否對 service discovery 的應用與威力有所改觀? 你的能力是否能成為扭轉局勢的那位關鍵人物? 任何想法都歡迎留言討論 :)























--------------





我時常拿現實生活的例子當比喻，來說明系統架構中如何解決各種管理問題。例如講到 Message Queue, 我就會舉銀行會用取號碼的機制，來引導顧客跟櫃台之間的流量。同樣的，如果把某個服務當作一間工廠的話，每個 service instance 就像一個員工，那麼 service discovery 就像是行政部門一樣，必須顧好每個員工的出缺勤狀況，並且及時讓工廠或是產線能隨時掌握人力的狀況並且做各種調度。

廠長需要哪些資訊，才能充分掌握人力狀況? 試想最基本的部分:

1. 出缺勤人數: 實到/應到
1. 這些人目前的工作狀況: 是否輪班，或是休息，或是因為任何原因暫時無法在工作崗位上

行政單位該怎麼掌握這些資訊? 其實方法也很簡單，做好下列幾件事，行政單位就能隨時有一份精確的人力清單:

1. 實施打卡制，上班打卡，下班打卡，上生產線刷卡，暫離刷卡...
1. 定期點名，巡視，抽查，定期回報...

回到微服務的治理，如果搭配 cloud service 提供各種機制 (如 auto scaling), 只要你出得起錢，給你多少 instances 都沒問題，問題在於你有辦法好好的運用它們嗎? 試想你的服務基礎建設中，誰能來扮演這個 "行政單位" 的角色? 你的 application 能否及時掌握一份完整且精確的清單，有所有 service instance 的 address / port / availability 的清單嗎? 如果有，你是如何做到的?

上一篇文章就簡單的介紹到 DHCP + DNS, 是大家熟知且行之有年的機制。有新的服務加入，DHCP 就能幫他分配好 IP 等等環境配置。其他人只要透過 DNS 查詢就能夠找的到他。只是 DHCP + DNS 維護的資料庫不夠精確，維護的資訊也不足以應付現今的需求。取而代之的，就是微服務架構常會聽到的 Service Discovery 機制了。

雖然後面的案例我都會拿 Consul 來說明，但是大部分的 Service Discovery 運作方式都很類似。每個服務啟動時，只要把自身的資訊 (address, port ... etc) 自動向 Service Discovery 服務進行註冊 (register)，要停掉前自動移除註冊 (deregister)，外加定期的確認該服務是否還正常運作中 (health check), 基本上這份服務清單就已經能滿足基本要求了。



# ADV: 分散式系統應用案例 (with HashiCorp Consul)



















-----------------------------------------------------------------------------------------------------------------------------
// 微服物化之後

// 你會有內部 N 個服務 x M 個 instance, 也會有 O 個外部服務 (with P 個 instance)... 
// 那你有多少複雜度需要管理?

// infrastructure 不能幫你解決甚麼問題?


// 組織: 管理所有人力的是行政部門 (出缺勤，打卡，新人到職，新人訓練... etc)

// 服務發現: 微服務的人資行政單位 (總管理處)
// 系統: 管理所有服務的是 Service Discovery (reg/dereg, health check, heartbeats, service database, service query, provision service and get config ...)


// 基本 service discovery 應用

// 進階 service discovery 變化應用

// 從 application developer 的角度來看 service discovery

// 如何發現 "服務發現" 的資訊?
// 如何確保服務是健康的? 註冊/移除/心跳/健康偵測
// APP 啟動之後，一定要做的事: 註冊,取得設定 (那為何不作再一起?)

// service instance 能否自我標記 (tagging)? 以利後續更進階的應用, service tagging with service query

// 外部服務的 endpoint(s) 應該如何管理? config? 如何確認服務狀態?
=> 看來也是 service discovery 應用的好時機 -> 靜態註冊 + health check
=> + tagging, 如果有多個備援方案可以選擇的話

// 更靈活的運用: 不透過 load balancer, 游 client 自行決定
// - 侵入式
// - 避開 LB 單點失敗，也避開 LB 的效能瓶頸
// - 支援點對點的通訊，不過複雜度加注再 application 身上...

// 更進一步解決複雜度: service mesh + side car
// -> 如果我需要找到 service discovery, 然後載入 configuration (或是取得更新通知), 再透過 service discovery 找到通訊的對象, 又不響綁太多 logic 再我的 application ....
// -> 改成 side car, 一次搞定所有問題

// 高度整合的 service discovery 服務: consul



# stories ...

微服務考驗的是你對 "大量服務" 的治理能力。所謂的 "大量" 服務，包含服務的種類很多，服務的個數很多...
同時也包含內部及外部服務...

這些問題當然可以靠 infrastructure (ex: DHCP + DNS, reverse proxy, load balancer, firewall ... etc) 來處理。如果你開發的是 SaaS 服務，如果你的 application 無法充分掌握這些資訊，你也會失去了進一步的整合能力。

我定義一下:

- STEP 1, 具體掌握你的服務狀態 (服務, 個數, 健康)
- STEP 2, 具體掌握外部服務的狀態 (服務, 健康) (個數你碰不到)
- STEP 3, 靈活運用, 充分調度你能掌握的服務資源

掌握現狀，永遠是第一步。當你的 SaaS application 背後有 N 個服務，平均有 M 個 service, 你就有 N x M 個 instance 需要被管理了。再談任何更深入的應用時，你應該要先掌握:

1. 這 N x M 個 instance 的健康狀態? (紅黃綠燈)
1. 這 N 個 service 的健康狀態 (紅綠燈)
1. 這 O 個 external service 的健康狀態 (紅綠燈)

你該如何管理與更新這些資訊? 用 config ? 用 database ? 你需要的是個能提供正確 service status 的 database, 最好還能同時提供 service (instance) reg / de-reg, health check (push / pull) 的服務 => service discovery.

# SD-BASIC

有了 service discovery 能精準掌握資訊後，接下來你就有很多方式能提高服務的效能與可靠度，靠的是更精準有效率的分配資源。

最基本的是 registry aware load balancer:

再來是進階的 registry aware http client:

我個人是大推 registry aware http client

# SD-ADV







-----------------------------------------------------------------------------



現在的服務要維持 7x24 已經是基本要求了，大家在拚的是拚 SLA 後面有幾個 9 .. (SLA 99.99% 代表一年只停機 4 小時)。不過提高 SLA 是 Ops 還是 Dev 的責任? 在過去，SLA 都是賣 Ops 的肝換來的，24hr 輪班，弄了一堆 cluster, load balancer 或是 fail over 等等機制來提高可靠度。不過這樣往往是事倍功半，最有效率的方法，還是 Dev 在開發與設計架構之初，就把高可用性的需求考慮進去，直接開發出讓 Ops 容易維護的系統才是上策啊!

這篇要介紹的 Consul, 一套 Service Discovery 的服務，就是做這件事的基礎建設。




-----

knowledge: 如何發現服務發現服務? 如何偵測健康偵測服務的健康狀態?

knowledge: integration with legacy system (DNS or consul-template)

case 1: basic scenario, multi instance


case 2: different service level (normal vs VIP)

case 3: isolate failed service


case 3: A/B test


