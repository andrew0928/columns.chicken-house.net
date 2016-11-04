---
layout: post
title: "API Hosting @ Azure"
categories:
- "有的沒的"
tags: ["有的沒的"]
published: false
comments: true
redirect_from:
logo: /public/logo.png
---

寫到這邊，寫了那麼多 code, 你的 API 總該要上線了吧! 這篇就來探討一下，除了寫好 Code 之外，API 上線還要注意什麼? 
雲端時代當然就別再自己養機器了，這次的範例我就直接用 Azure 來示範。Microsoft 在 [Azure App Services](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-value-prop-what-is/)
中，包含了四大類的服務類型，其中之一就是 [API Apps](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-api-apps-why-best-platform/)
就是專門用來裝載 API 類型的服務。

<!--more-->

用 API Apps, 而不是自己從 VM 開始架設，當然可以替開發人員省掉不少維護上的困擾。當規模擴大，使用情境更複雜時，Azure 還更
進一步提供 API manager, 來替你轉送及管理後端多個及各種類型的 API。不過這篇我會把重點擺在單一一套 API service 的 hosting,
API manager 會等到後面 Microservice 的部署議題再來討論。

其實，就算你不打算用 Azure 來 hosting 你的服務，這個架構依然是很適合大型服務的部署的。上面提到 API Apps 的說明網頁，有張
圖很清楚的說明 API manager 跟 API Apps 之間的關係:

![API Apps v.s. API Manager](/wp-content/uploads/2016/11/apisdk04-apia-apim.png)


{% include series-2016-microservice.md %}


# 除了 API 之外，你還需要些什麼?

Developer 當久了，往往除了寫 code 之外其他都會忘掉... 這就是 developer 跟 stakeholder 的差別。
切記，永遠別忘了你寫的code 是要解決什麼問題，適時地跳出框框思考，你會有不一樣的答案。前面提過了，API 的使用者
就是其他的 developer, 寫 code 來呼叫你的 service。因此你要留意的是 DX (**D**eveloper e**X**perience)。DX 包含哪些東西? 

這篇文章 "[What is API Developer Experience and Why It Matters](https://www.infoq.com/news/2015/10/api-developer-experience#.WBtTAul_ScU.facebook)" 
寫的不錯，很扼要的點出 API DX 的四個要點，節錄這文章的片段:

> ... four key concerns that can help reach the goal of API excellence:
>
> * **Functionality**:
> what problem the API solves and how good it is at that. An API should not only strive for effectively solving a problem, it should also solve it very well.
> 
> * **Reliability**:
> a set of non-functional requirements such as availability, scalability, stability, etc. that can help build trust and represent a necessary ingredient in driving developers to use an API.
> 
> * **Usability**:
> how well does an API lend itself to discover and learn how its functionality can be used (intuitability)? How easily does it allow developers to create tests? What support does it provide for error handling?
> 
> * **Pleasure**:
> how enjoyable is an API to use?

看完原文，我補充一下我的看法:

在 hosting 階段，其實最有關聯的就是 Reliability 跟 Usability 這兩項了。Reliability 本來就是雲端服務的強項，很容易就能達到
良好的 Availability, Scalability, Stability 等等。這個後面直接看 case study 就能體會了。至於 Usability, 對於 API 這類應用
來說，具體的 Usability 指的是什麼? 

我試著由我過去的經驗，把 API 的 usability 分成這幾點來探討:

1. API 是否易於學習與了解?  

文件是最基本的需求了。但是傳統的提供 PDF 或是 WORD 應該不是個好方法，既難維護也難查閱，既然提供及使用的雙方都是 developer,
應該有更有效率的作法才對。古早的 Java Doc / C# comments doc 都是一樣的概念，code 跟 doc 一起維護，靠系統或是平台自動產生
對應的文件才是上策。能夠有系統的引導 developer 取得 sample code 則是個加分的服務。

> 評估你的 hosting 環境能否替你解決 API documentation 的問題?

2. API 是否易於呼叫及使用?

這一系列文章一直在探討的 SDK，其實就是要簡化 API 使用門檻的方法之一。除了 SDK 之外，若能在文件指引的地方，同時提供
能立即嘗試呼叫 API 的服務，那也是大加分。現在很多 RESTful API, 都直接可以用 HTML5 + Javascript 呼叫了，也因此有很多
說明頁面直接提供 "try this" 的按鈕，按了就能立即呼叫。

> 評估你的 hosting 環境能否改善這問題?

3. API 是否易於操作、測試、體驗?

API 使用的過程中，最討厭的就是 "測試" 了。正常情況下，我們都會把開發環境跟生產環境區分開來。但是 API 如果是別人提供的，
沒有辦法提供開發測試跟生產環境的話，你還能很方便的在上面測試嗎? 比如金流線上刷卡的服務，難道你測試時每次都要真的拿出信用卡
刷個 10 塊錢嗎?

> 

4. API 是否易於管理? 除錯? 追查 LOG? 

API 上線後想要快速知道使用狀況，包含呼叫頻率，失敗次數或比率，甚至是失敗之後能否提供 developer 後端的 logs ?

5. API 是否易於申請，管控，監控? 

API token 是否有個簡單明確的申請跟管理介面 (WEB UI)? 或是能否讓管理人員快速的啟用授權? (Azure AD?)

