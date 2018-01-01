---
layout: post
title: "微服務基礎建設 - Service Discovery"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "infra", "message queue", "api gateway", "service discovery"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/12/service-discovery.jpg
---

微服務系列文章停了幾個月，因為這系列的文章不好寫啊，很多內容有想法，但是沒有實做過一遍的話，寫出來的東西就只是整理網路上其他文章的觀點而以，那不是我想
做的 (這種事 google 做的都比我好)。經過這幾個月，自己私下 & 工作上又都累積了一些經驗，就又有素材繼續動筆了! 這次要補的是微服務必備的基礎建設之一: 服務註冊與發現機制 (Service Discovery)。

![](/wp-content/uploads/2017/12/service-discovery.jpg)

前面我一直在強調, 微服務並不是新技術，而是個架構設計的方針而已。實作上要用到的技術還是那些。然而要把一個服務拆分成數個獨立的服務，考驗的不是開發技巧，而是考驗
開發流程，以及你有沒有管理大量服務的能力。微服務化最明顯的衝擊，就是服務的數量變多了，同時服務的組態 (例如最基本的 IP 跟 PORT) 也從靜態 (Server 應該沒人在用 DHCP 吧) 變成動態的了。這篇要探討的就是這些問題，當你的服務數量變多且會隨時動態調整時，你該如何 "管理" 它? 一堆小型的服務，如何很快地找到提供服務的 IP 與 PORT ? 如何很快地掌握每個服務的健康狀態? 
這麼多服務，組態的管理該如何進行? Service Discovery 服務發現的機制就是解決方案。


<!--more-->

{% include series-2016-microservice.md %}

--

# Service Discovery 的服務模式

在進到實際操作前，還是先花點時間了解一下 "Service Discovery" 到底在做什麼吧。這個領域的服務很多，每個的用法又都不一樣，光是選擇這件事就讓我吃盡苦頭。因此誠心建議各位，與其
一開始就躁進要馬上裝一套來玩玩看的作法，在這邊是會踢到鐵板的，還是按部就班先了解一下 Service Discovery 葫蘆裡到底在賣什麼藥吧。

還是回到 NGINX 這系列的微服務文章 (也有排版精美的電子書版本)。其中一個章節就把 Service Discovery 的概念講的很到位。我節錄裡面提到的幾種 Service Discovery 常見的服務模式:

文章網址: http://


## The Client‑Side Discovery Pattern

## The Server-Side Discovery Pattern

## The Self‑Registration Pattern

## The Third‑Party Registration Pattern


# 其他的模式

## service mesh: envoy, side car

## The Service Registry (調整順序，放在最後面介紹)

* etcd
* consul
* zookeeper
* dhcp / dns !!!


# Consul 使用案例示範

## 服務註冊 (via code / definition)

## 健康偵測

## 服務查詢

## 組態查詢

## DNS integration (NGINX)