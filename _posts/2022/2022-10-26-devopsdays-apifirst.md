---
layout: post
title: "架構師觀點 - API First 的開發策略 (DevOpsDays Taipei 2022 Keynotes)"
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


<!--more-->

{% include series-2016-microservice.md %}



# 前言:




--
你真的需要 CRUD 的 API / 微服務嗎?

CRUD，是 DB access domain 的用語, 你當然可以這樣定義你的 service, 但是這也代表你主要的目的就是 "操作" 資料而已，而且是把它當成 storage 的角度在操作，並非有商業意義的操作。因為 CRUD 就是 data access 的 domain 用語。

換個角度想，這樣做背後的目的，就是把原本 database / storage access protocol, 從專屬的 protocol / api, 提升到 http api 而已。這沒有不對，是選擇問題，如果你要的真的是這樣，這是好的做法。如果你真的要的是 CRUD，甚至有很多 code gen + ORM 都做得比你好，你不一定要自己從頭開始做。

