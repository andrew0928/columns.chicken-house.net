---
layout: post
title: "容器化的微服務開發 #3, Consul"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps", "Service Discovery", "Consul"]
published: false
comments: true
redirect_from:
logo: /wp-content/images/2018-04-06-aspnet-msa-labs2-consul/how_would_you_solve_the_icing_problem.png
---


現在的服務要維持 7x24 已經是基本要求了，大家在拚的是拚 SLA 後面有幾個 9 .. (SLA 99.99% 代表一年只停機 4 小時)。不過提高 SLA 是 Ops 還是 Dev 的責任? 在過去，SLA 都是賣 Ops 的肝換來的，24hr 輪班，弄了一堆 cluster, load balancer 或是 fail over 等等機制來提高可靠度。不過這樣往往是事倍功半，最有效率的方法，還是 Dev 在開發與設計架構之初，就把高可用性的需求考慮進去，直接開發出讓 Ops 容易維護的系統才是上策啊!

這篇要介紹的 Consul, 一套 Service Discovery 的服務，就是做這件事的基礎建設。




-----

knowledge: 如何發現服務發現服務? 如何偵測健康偵測服務的健康狀態?

knowledge: integration with legacy system (DNS or consul-template)

case 1: basic scenario, multi instance


case 2: different service level (normal vs VIP)

case 3: isolate failed service


case 3: A/B test


