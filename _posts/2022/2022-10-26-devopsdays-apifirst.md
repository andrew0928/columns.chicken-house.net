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


這篇，我把它擺在 API 設計系列的第一篇，同時也是我在 DevOpsDays Taipei 2022 Keynotes 講的內容。會擺在第一篇，因為這篇我收整了 API Frist 的動機，以及落實的經驗談。早先寫的兩篇則是實際設計的過程。隔兩周也跟保哥合作，用線上直播的方式重新分享了一次這個主題。不過，不同的分享方式都有不同的交流管道啊! 我個人最喜歡的，還是我已經默默做了快 20 年的方式: 寫 BLOG 文章。

寫文章，還是最能表達我思考脈絡的方式，閱讀的節奏也方便自己掌控 (直播或是演講，時間都固定了，節奏是講者掌握，不是聽眾掌握)，對於筆記、搜尋、資訊的再利用，文章的圖文，也遠比簡報分享，或是影片分享來的有效率..

於是我就把同樣主題用文章重新整理了一次，也補上了一些我在直播或是演講略過的內容。











--
你真的需要 CRUD 的 API / 微服務嗎?

CRUD，是 DB access domain 的用語, 你當然可以這樣定義你的 service, 但是這也代表你主要的目的就是 "操作" 資料而已，而且是把它當成 storage 的角度在操作，並非有商業意義的操作。因為 CRUD 就是 data access 的 domain 用語。

換個角度想，這樣做背後的目的，就是把原本 database / storage access protocol, 從專屬的 protocol / api, 提升到 http api 而已。這沒有不對，是選擇問題，如果你要的真的是這樣，這是好的做法。如果你真的要的是 CRUD，甚至有很多 code gen + ORM 都做得比你好，你不一定要自己從頭開始做。







--
這次直播，你覺得最大的收穫是什麼?

4

Anonymous
從狀態圖來驅動 API ，這套方法有次序有架構的疏理 api 的建構並且同時涵蓋了 CDC & access control 的設計，感謝大大的整理與分享也是借這個機會才看到你的 blog 有非常多很好的文章，感謝你的分享！

Anonymous
謝謝Andrew 大哥, API 1st 的觀念讓我處在長久以來受到打帶跑組織文化的開發型態(UI + schema)，茅塞頓開，獲得啟發的感覺。之後我會嘗試反芻出具體適合我工作場域的模式。

Anonymous
Andrew 好強

Anonymous
了解真正的 API First 設計方式該從哪個角度切入設計





--
Anonymous
 2
 7 Oct, 9:48pm



以scrum兩週為一週期，可以談談api First在定義期 開發期 整合期 測試期在流程順利下，大致上的占比嗎


Anonymous
 1
 7 Oct, 9:55pm



要如何測試api資安風險, 當內部沒專業資安人員時


Anonymous
 0
 7 Oct, 10:13pm



請問 API first 的開發方式也適用於 to C 的產品上嗎？


Anonymous
 0
 7 Oct, 10:15pm



根據p.43 要改成API FIRST，並且做到功能權限分則，會需要捨棄RESTful API嗎


Anonymous
 0
 7 Oct, 10:37pm



1. 請問API first，會做成每個API是一個MicroService嗎？還是會相關API放在同一個MicroService


Anonymous
 0
 7 Oct, 10:38pm



Contract First的模式下 與前端討論時還是希望以業務邏輯組裝對應的API，需要怎麼說服API的擴充與拓展性優先


Anonymous
 0
 7 Oct, 10:43pm



若本身非該領域的專家，要怎麼確認自己在規劃系統的時候考慮的是極大值而不是落在某些最大值? 極大值會因為系統在未來加入了一個新領域的商業需求而改變嗎? 如果會的話請問要怎麼因應呢? 謝謝! p.57

Anonymous
 0
 7 Oct, 9:36pm


理想很豐滿，現實很骨感。可以分享些導入 91 時遇到的困難嗎？


Anonymous
 1
 7 Oct, 9:56pm


何種人格特質適合當架構師？


Anonymous
 1
 7 Oct, 9:56pm


開發出api時, 團隊要如何溝通接口, 用類似Swagger建立的REST API文件嗎？ 還是用其他工具


Anonymous
 1
 7 Oct, 9:54pm


Contract First 的規格要設計承受多少請求量？會不會發生過度設計？


Anonymous
 1
 7 Oct, 9:54pm


lmpl 全名是?


Anonymous
 1
 7 Oct, 9:39pm


在使用Kong、Axway、APIC、Apigee等API管理平台，管理公司內部API(先排除對外API) 需要定義甚麼規範讓公司API開發團隊遵守?這樣規劃有什麼坑要注意的? 在規劃內部API的API developer portal給業務單位或有跨單位開發需求時，有什麼建議設計嗎?


Anonymous
 2
 7 Oct, 10:38pm


Api First 的設計開發模式，在收到老闆的需求後，以貴公司來講，討論 Api 的流程是以 PM 發起的嗎？還是這樣的開發流程會是需要以 RD 來主導 RD來規劃，QA也會參與這樣的討論嗎？


o
on
 2
 7 Oct, 9:51pm


Contract First 的流程，很容易卡在後端開發人員說 DB 沒欄位，生不出資料，還有另外 100 種理由。



https://hackmd.io/@DevOpsDay/2022/%2F%40DevOpsDay%2FryaejF6ei


https://docs.google.com/presentation/d/1yN8SlMwqoPpO_69dwxsAxWRwLdUB0pmBXCpioxMK-5g/edit#slide=id.g1616bfd0567_0_57


https://netflixtechblog.com/timestone-netflixs-high-throughput-low-latency-priority-queueing-system-with-built-in-support-1abf249ba95f