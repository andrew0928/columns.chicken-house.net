---
layout: post
title: "微服務架構 - API 的安全管控模型"
categories:
- "系列文章: 微服務架構"
tags: ["系列文章", "架構師的修練", "microservices"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---

前面寫了兩篇 API 設計的文章，也寫了一篇 PoC 的心得，接下來就延續 API 這個議題，來聊聊 API 的安全機制設計吧。資訊安全，通常都是要從下到上，每個環節都能顧到才算安全，只要你有一個環節沒做好，就會有人從你最弱的一環來入侵。這篇我不談基礎建設層面的資訊安全 (例如防火牆，DDoS 等等這些 infrastructure 層面的安全機制)，我想聊的是來自你的 API 設計相關的安全性。

舉例來說，如果你開發後台管理系統，那你應該會聽過 OAuth2, 或是 RBAC 等等相關名詞。但是 API 呢? 在 cloud, 各大雲都有專為 API 設計的管理機制。例如 Azure 有 API Management, 而 AWS / GCP 也有對等的服務。這些服務大都提供基本的 API-KEY 管理機制，同時在這把 KEY 的背後，就能提供 IP 白名單, Rate Limit 之類的。但是你的商業邏輯呢?

這些情況，往往會隨著你的商業模式，越來越複雜。越複雜的情境，你就越難只靠這些基礎建設來管理。目前越來越多服務，是以 SaaS 的型態提供，如果你的 API 是分別提供給不同的客戶，再開放給這些客戶的 IT 人員，或是再轉發出去的外包服務商呢?

恐嚇就到此為止，其實這些情境，你只要靜下心好好的想清楚他們需要的安全管理模型，其實實做起來一點都不困難。我會在最開始提到另一篇談 PoC 的文章是有原因的，尤其是這種規格設計議題吃重的題目。這些架構或規格的設計，我自己很講求要先找對模型，用對模式來解決問題；之後才是根據你的規模跟實際使用的 tech stack 或是 hosting environment, 再來找合適的解決方案。如果規模小, 也許你可以找找合適的 package, 直接在你的 application 內用 AOP 的方式來做好安全機制 (例如 ASP.NET Core 的 Middleware, 上一篇實做我就是用這技巧)。如果你必須面對大流量，或是你不想動用寶貴的 application 運算資源，你就得找能夠在 API Gateway / Reverse Proxy 這層次注入你的判定邏輯的解決方案。Azure 的 API Manager + Azure Functions, 或是自己在 reverse proxy 外掛你的檢查邏輯 ( Ocelot, YARP 等等這類你能掌控 source code 的 open source project ) 來做到 offloading 都是不錯的解法。

不過，要做到這樣靈活的彈性，你必須先想清楚安全模型才行 (甚至你必須定義出 protocol)，抽象化到這個層次，你才有可能達到這樣的靈活程度。

<!--more-->

