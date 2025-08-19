---
layout: post
title: "[分散式系統 #1] Idempotency Key 的原理與實作 - 能安全 Retry 的 API 設計"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "架構師", ]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: 
---

好久沒寫微服務系列的文章了 (其實去年寫了兩篇，最後沒能把它寫完就沒發表了)，最近工作上又累積了不少處理的實作經驗，決定順手再來記錄一下。經歷過實作的過程後，才發現導入微服務的過程真是到處都是坑啊! 網路上看到的文章都在講怎麼切割才到位，不過實際上的狀況是，有很多工程師都還沒有足夠的經驗跟能力，能 "只" 靠 API 就把事情做好啊... 很多直接處理 DB 兩三下就能搞定的事情，換成 Http API 就變得困難重重。這些其實不是微服務的坑，而是分散式系統的坑啊...，於是決定開這系列文，第一篇就來談談如何在不可靠的網路上，確保遠端的 API 有正確的被執行的做法吧!

<!--more-->

透過網路的通訊，基本上都有些不穩定的因素存在。試想一個例子:

我要呼叫一個 API，呼叫成功就會從我的戶頭扣款 100 元。呼叫不論成功或失敗，API 都會明確的傳回執行結果。不過某次我還沒接到執行結果，連線就中斷了。雖然一瞬間網路連線就恢復了，但是這 API 到底有沒有執行成功? 我該不該重新 (retry) 呼叫一次 API ? 如果被扣了兩次款那該怎麼辦?

執行越重要的任務，越會碰到這類的問題。這已經是 FAQ 級的問題了，這篇就針對這個主題好好的來研究一下吧!



{% include series-2016-microservice.md %}



# 前言: 分散式系統的常見難題



# Retry? 我應該要重新呼叫 API 嗎?



# 關鍵字: Idempotent 的定義與原理



# 設計原生支援 Idempotent Safe 的 API



# 額外附加的 Idempotency Key 保護機制



# 