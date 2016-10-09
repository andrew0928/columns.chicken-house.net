---
layout: post
title: "微服務架構 #3, API & SDK Design"
categories:
- "專欄"
- "系列文章: .NET + Windows Container, 微服務架構設計"
tags: []
published: false
comments: true
# redirect_from:
logo: /wp-content/uploads/2016/10/microservice-webapi-design.jpg
---

上一篇講到 "重構"，不斷的進行重構，直到能夠將模組切割為服務為止。這篇就接續這個話題，展示一下
服務化之後的 API / SDK / APP 之間的關係，以及設計上要顧慮到的細節。我用最常碰到的資料查詢 API 的分頁機制
當作案例來說明這些觀念。資料分頁是個很煩人的東西，不論是在 UI 或是在 API 層面上都是。尤其是 client 端要把
分頁後的資料重新組合起來，就會有越來越多的 *義大利麵風格* 的 dirty code 被加進來..

這時 SDK 扮演很重要的角色，善用 C# 的 yield return 就能很漂亮的解決這問題。這篇就來示範幾個 API / SDK
的實作技巧 (C#)，之後微服務講到這部份時，可以再回頭參考這篇的內容。

<!--more-->

# 範例 Data API Service

這篇的應用範例，我從內政部的 open data 網站找了一個[範例](http://data.gov.tw/node/8340) 來當資料庫，
示範這樣的 API service 該如何設計，以及能動之後，怎麼樣的設計才是良好的 API service ? 觀察過很多台灣的
團隊，往往在這些實作的層面沒有仔細考量，造成維護上的困難。API 的生態，跟應用軟體的生態不大一樣。很多老闆
都會講服務應該快速推出，快速驗證市場需求；這是對的。不過 API 這種東西就完全不同，它的使用對象不是 End User,
而是 Developer. Developer 在意的不是 UX (User Experience), 而是 DX (Developer Experience - 開發者體驗)
啊.. 這篇我主要就是要探討 DX，因此重點會在 API 的定義跟 SDK 的包裝方式。

前面提到的 data service, 我想會 .NET 的人應該都沒問題吧? 開個 MVC WebAPI 的專案就可以搞定了。這邊我就直接
跳到第一版，提供其他的開發人員查詢台灣鳥類生態觀察的資料。不多說，直接看 code:

(接下來會有幾篇文章要延續這個範例，code 會不斷的修正。若要參考這篇文章提到的 sample code, 請參考 dev-SDK 這個分支)
GitHub Repo: https://github.com/andrew0928/SDKDemo/tree/dev-SDK






















