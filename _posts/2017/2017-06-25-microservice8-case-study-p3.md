---
layout: post
title: "架構師觀點 - 轉移到微服務架構的經驗分享 (Part 3)"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/05/
---

前面兩篇，分別介紹了微服務架構的規劃方向，還有實際切割的案例探討。這篇 (Part 3) 的重點就要擺在微服務到底該在甚麼樣的基礎建設上面
運行? 維運過去單體式架構的 application, 所需要的基礎建設，會跟微服務架構下可能會有數十個 service instances 同時執行，甚至上百個
service instances 一樣嗎?

我只能說，考量是完全不一樣的。因為細粒度的關係，也許你的使用規模並不算大，但是你仍然得面對十來個 service instances 維運的考量。
這篇則會針對這樣的狀況，來探討一下開發上的基礎建設，還有部署時的做法有何不同。

<!--more-->

{% include series-2016-microservice.md %}


--

# 微服務需要那些基礎建設?

在介紹基礎建設之前，我大力推薦 Nginx 的這本電子書:

![](2017-06-06-02-07-00.png)
[Microservices: From Design to Deployment, a Free Ebook from NGINX](https://www.nginx.com/blog/microservices-from-design-to-deployment-ebook-nginx/)

這本電子書的深度跟複雜度，拿捏得剛剛好。沒有深入到太多實作細節，也沒有淺顯到空談一堆你看完還是不知道怎麼做。
長度也剛好，只有 70 頁，不需要花很多時間就能看完。這 ebook 介紹了微服務系統中幾個關鍵的基礎建設，以及為何需要它的原因，
推薦大家都先去看一下這本書的內容。

想看網頁版也有.. 當初還沒出電子書時，我就是看網頁版連載的文章:
[Introduction to Microservices](https://www.nginx.com/blog/introduction-to-microservices/)

這份電子書裡面，提到跟 microservices infrastructure 有關的有這幾個部分:

* API Gateway
* IPC (Inter-Process Communication)
* Service Discovery
* Event-Driven

其他講微服務架構與觀念的，還有如何重構既有的 application, 我們在前面兩篇其實都帶到了，這裡就針對基礎建設來探討:


## Using An API Gateway



# Docker, 最佳的微服務部署方式

# Immutable Services

