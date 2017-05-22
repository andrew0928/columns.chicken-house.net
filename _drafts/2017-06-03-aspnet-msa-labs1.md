---
layout: post
title: "容器化的服務開發 #1, 架構與概念"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps"]
published: true
comments: true
redirect_from:
logo: 
---

總算把包含架構與觀念的實際案例篇寫完了，前面也寫完了微服務化一定會面臨的 API 開發設計問題，那接下來可以開始
進入有趣一點的部分了。微服務架構是由很多獨立的小型服務組合而成的，這次我們直接來看看每一個服務本身應該怎麼開發。

既然要講到實作，那就不能不提讓微服務可以實現的容器技術。我一直覺得很可惜的是，不管國內或國外的文章，以開發者的
角度來介紹容器技術的案例實在不多啊 (還是我關鍵字下的不對? @@) 大部分的文章都是在強調容器在架構面的好處 (微服務)，
不然就是一堆操作技巧，教你怎樣把既有的 application 包裝成容器，再者就是容器的管理技巧等等。但是當容器已經普及了
之後，你的服務開發方向，是否能夠針對容器做最佳化?

我從小就是靠 Microsoft Solution 吃飯長大的，C# 我也從當年還是 Visual J# 的年代，一路到 .NET framework 1.0 就
開始用到現在，既然 Windows Container 也都問世了，那這次的示範我就用 Windows Container + .NET Framework + Azure
來做吧! 

我這次挑選的主題，就用前陣子我實際上碰到的 case: 用 IP 查詢來源國家的服務當作例子。這功能很符合微服務的定義: 
"小巧，專心做好某一件事"，剛好前陣子 Darkthread 也寫了一篇 "[用 100 行 C# 打造 IP 所屬國家快速查詢功能](http://blog.darkthread.net/post-2017-02-13-in-memory-ip-to-country-mapping.aspx)"，我就沿用 Darkthread
貢獻的 Source Code, 把它包裝成微服務，用容器化的方式部署到 Azure 上吧! 


<!-- more -->


## IP查詢服務，該有哪些元件?

別以為一個 "IP 查詢服務"，就真的只是一個服務而已。既然微服務的設計準則包含這條: "能獨立自主運作的服務"，那麼你要開發
的就不只 webapi 這麼一個而已。我先把需求列一下:

1. High Availability + Scalability
1. Auto Update IP Database
1. Include Client SDK (with client side cache)
1. DX (Developer Experience, 要對使用我的服務的開發者友善)

綜合這些需求，我規劃了這樣的架構，如果都能實作出來，應該就能同時滿足上述這幾項了吧? 來看看設計圖:







很典型的架構，前端用一組 reverse proxy, 來把流量平均分配到後端的多組 IP2C web servers, 來達到 HA + Scale out 的要求。
然而 IP query 最重要的就是資料庫的更新，因此另外安排了一個 worker, 定期到官網的下載頁面定期更新資料檔。下載後會自動
解壓縮，同時先對這個資料檔做好基本的單元測試，通過後才會部署到 share storage，供其他的 IP2C web servers 使用。同時為了
方便其他的 developer 充分使用我的 IP2C service, 我也打算提供一組 SDK, 方便他們直接呼叫我的服務。這 SDK 除了方便呼叫
web api 之外，我也加上了 client side cache, 同一個 IP 在時間內查詢多次, 則會直接透過 cache 傳回。

除了營運環境的部分之外，對於我自己的 DevOps 流程我也做了簡單的需求規劃:

1. Code 修改完成 Push 到 Git Repository 之後，觸發 CI 進行編譯、單元測試
1. 通過測試與編譯的 code, 則將 web server 與 worker 透過 build 成 docker image, 放到 docker registry
1. SDK 則在編譯之後，自動進行 nuget package 與 nuget push ，放上 nuget server 發行這份 SDK
1. 決定要上版的時候，就透過預先編好的 docker compose 定義檔，從 docker registry 更新 server 上的版本

這兩部分都完成後，各位可以盤點一下，是否原先的需求都已經達成了? 整個藍圖設計好之後，接下來就是一步一步完成他了。

> 這次主要重點在開發，因此 DevOps 環境的建置部分我會略過，只會帶到如何自動化的 script 而已，篇幅有限，請見諒 :D


## IP2C.WebAPI

// code

// dockerfile




## IP2C.Worker

// code

// dockerfile

// container 簡化 service 的開發 (only console application)


## Run IP2C Services (WebAPI + Worker) on Local PC

// dev-env, no scale out, no HA, use docker only, not docker-compose



## IP2C.SDK

// webapi wrapper

// performance turning, 別指望其他 developer 會替你最佳化 (cache)

// DX



## Summary

// 看看你寫了那些 code ? 都只是必要的
// 其他都省略了 (尤其是 worker)

// next step?


