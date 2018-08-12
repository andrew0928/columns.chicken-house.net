---
layout: post
title: "DevOpsDays 專刊: 從 Developer 的角度看 Service Discovery"
categories:
- "系列文章: 架構師觀點"
tags: []
published: false
comments: true
redirect_from:
logo: 
---


從微服務化開始，面臨的第一個問題就是你該如何管理你旗下的這堆內外部服務? 要有條理的管理好這堆服務，可是件苦差事 (雖然技術上不是件難事)。這是你的服務能不能維持在一定複雜度之下持續發展茁壯的重要關鍵。對於 developer, 這是個較陌生的課題，因此在今年 DevOpsDays Taipei 2018, 我準備了這個 session, 準備從 developer 的角度來看待這件事，要介紹的就是 service discovery, 微服務架構下最重要的基礎建設。

這篇我不會從 service discovery 的基礎開始談起。想看基礎建紹的可以參考我去年寫的這篇: 






















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


