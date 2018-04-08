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

先前的版本，完全沒有針對可用性做進一步的規劃。先來計畫一下這版預計要改進那些地方:

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


