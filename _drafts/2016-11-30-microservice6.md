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

寫到這邊，寫了那麼多 code, 你的 API 總該要上線了吧! 這篇就來探討一下，除了寫好 Code 之外，API 上線還要
注意什麼? API 這種東西不比一般的系統，API 的開發者是 developer, 使用者也是 developer，溝通可以用更有效率
(更宅? XD) 的方法，而不是只能靠傳統的文件~

這篇主題就擺在 API 開發完成後，要上線的考量。包括如何顧好 DX? 如何讓使用你 API 的 developer 有最好的
usability? 另外一個議題，就是如何挑選適合 hosting API service 的服務? 雲端時代就別再自己架設 server 了，
挑選個好的環境可以事倍功半，輕鬆容易就顧好 reliability.

這篇我分三個部分，第一部分仍然是講大道理為主，把我考量的思考過程花點篇幅寫出來。第二部分介紹
[swagger](http://swagger.io) 這套 API Framework 以及 tool chain, 靠他來跟其他 developer 聰明的溝通。
第三則是 hosting 環境的選擇，我會介紹 Azure 上的 [API Apps](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-api-apps-why-best-platform/), 
以及點到為止的介紹 API manager (後面的文章再深入介紹)。

<!--more-->


{% include series-2016-microservice.md %}


# 除了寫好 API service 之外，你還需要些什麼?

Developer 當久了，往往除了寫 code 之外其他都會忘掉... 這就是 developer 跟 stakeholder 的差別。
切記，永遠別忘了你寫的code 是要解決什麼問題，適時地跳出框框思考，你會有不一樣的答案。前面提過了，API 的使用者
就是其他的 developer, 寫 code 來呼叫你的 service。因此你要留意的是 DX (**D**eveloper e**X**perience)。
DX 包含哪些東西? 

這篇文章 "[What is API Developer Experience and Why It Matters](https://www.infoq.com/news/2015/10/api-developer-experience#.WBtTAul_ScU.facebook)" 
寫的不錯，很扼要的點出 API DX 的四個要點，節錄這文章的片段:

> ... four key concerns that can help reach the goal of API excellence:
>
> * **Functionality**:
> what problem the API solves and how good it is at that. An API should not only strive for effectively
> solving a problem, it should also solve it very well.
> 
> * **Reliability**:
> a set of non-functional requirements such as availability, scalability, stability, etc. that can help
> build trust and represent a necessary ingredient in driving developers to use an API.
> 
> * **Usability**:
> how well does an API lend itself to discover and learn how its functionality can be used (intuitability)? 
> How easily does it allow developers to create tests? What support does it provide for error handling?
> 
> * **Pleasure**:
> how enjoyable is an API to use?

看完原文，我補充一下我的看法:

在 hosting 階段，其實最有關聯的就是 Reliability 跟 Usability 這兩項了。Reliability 本來就是雲端服務的強項，
很容易就能達到良好的 Availability, Scalability, Stability 等等。Reliability 是單純架構面的選擇，API 這類的
服務跟 WEB 並沒有明顯的差別，這篇我就不在 Reliability 上多作討論。

至於 Usability, 尤其是對於 developer 的 usability 才是我考量的重點。對於 API 這類應用來說，具體的 Usability 
指的是什麼? 

我從我自己的經驗，把 API 的 usability 分成這幾點來探討:

## 1. API 是否易於學習與了解?  

提供適當的文件，是最基本的需求了。傳統的提供 PDF 或是 WORD 應該不是最好的方法，維護困難，查閱也不方便，我舉
最典型的例子，愛用 visual studio 的人都知道，我在寫 code 時如果有做好 C# code comments, 那麼編譯時就可以
產出 comments xml, 同時 visual studio 的 intelligent sense 在你用到該 method 時，也會自動帶出那些 comments.

這已經讓 *文件* 不再只是文件，而已經是 **自動化** 而且是 **可操作** 的文件了。API 的提供者與使用者都是 developer, 
其實可以有比傳統文件更好的呈現方式。能從開發 > 維護 > 更新文件 > 發行文件的過程中，緊密和服務的更新及上線搭配，
這是最理想的。

> **Action**: 是否有對應的 API documentation 解決方案? 這方案能否跟你的開發流程互相搭配?


## 2. API 是否易於學習及體驗?

使用者(developer)第一次要使用你的 API，進入障礙也是影響的因素之一。這一系列文章一直在探討的 SDK，其實就是要
簡化 API 使用門檻的方法之一。除了 SDK 之外，若能在呼叫 API 有文件以外更進一步的引導工具，讓開發者快速進入狀況的
方式都有幫助。

最常見的就是直接提供線上的 **體驗** 工具。API 不比網站服務，要怎麼 **體驗**? 我舉幾個比較知名的例子:

* Facebook [social plugins](https://developers.facebook.com/docs/plugins/):
我就拿最常見的，在你自己網站加上 "讚" 的按鈕，FB 提供了各種做法。在這個 
[示範頁面](https://developers.facebook.com/docs/plugins/like-button) 裡面，就包含這樣的工具:

![Facebook "讚" 按鈕配置工具](/wp-content/uploads/2016/11/apisdk04-fblike.png)

除了各種文件類型的指引之外，使用者可以在典型的 coding > update > testing 的過程開始之前，就能用最快速的方式
體驗你提供的 API 效果。

* 另外一個例子: Facebook [Javascript Test Console](https://developers.facebook.com/tools/javascript-console/):

Facebook 為了讓 developer 能最快速的使用他的服務，在學習過程中，完全免除 developer 要先下載安裝或是設定等等
工具的過程。這樣的線上體驗工具，我只要有瀏覽器，我就能開始體驗測試了。只要我看完文件，點了連結就能開始。

試想看看，若沒有這樣的線上測試環境，我要準備多少東西?

1. HTML (就算是 hello world 也要花個一分鐘)
2. WEB server (最基本的 nginx, iis express 也是要下個指令，同時確認一下防火牆有沒有打開)
3. Editor (visual studio 開個 web site project, 或是 vscode)

這些過程，跟直接 click link 就進入 javascript test console 真是天差地遠啊...
評估你的 hosting 環境或是開發工具，能否提供線上的方式直接呼叫 API 並觀察結果? 或是有哪些工具能提供這樣的機制? 
而不是自己從頭寫一個?



## 3. API 是否易於測試?

API 使用的過程中，最討厭的就是 "測試" 了。這裡指的測試，是指你在開發過程中，必須不斷的呼叫 API 確認執行結果。
包含 coding 過程驗證是否能正確執行，或是進行單元測試? 正常情況下，我們都會把開發環境跟生產環境區分開來。但是 API 
如果是別人提供的，沒有辦法提供開發測試跟生產環境的話，你還能很方便的在上面測試嗎? 比如金流線上刷卡的服務，難道
你測試時每次都要真的拿出信用卡刷個 10 塊錢嗎? 壓力測試若要短時間模擬 10000 人同時線上刷卡，難道你要銀行寄一疊
帳單給你嗎?

幾年前看過這篇文章: [那些讓人皺眉的 REST API](https://zonble.net/archives/2011_05/1475.php)，就提到 API 的
測試問題。我覺得這篇文章作者點到了我的痛點，尤其是這段話:

> *首先，很多的 API 規劃似乎都以為 client 軟體都不會出問題，都不需要測試，*
> *於是做出讓 client 端無法做自動測試的規劃。這種問題主要發生在開放 API 上，像有些服務一方面開放 API，*
> *一方面又設定了什麼禁止灌水、禁止廣告機器人、禁止濫發沒有意義內容干擾其他使用者…這類管理規則，*
> *但，client 軟體做自動測試時，必定需要發送一定數量的測試訊息不能灌水就等於無法測試，無法測試就等於無法開發。*

當我們都在講求 DevOps, 講求 TDD, 講求測試的涵蓋率等等流程優化的時候，你在 Hosting API 時是否有考量到
這些問題，並找出解決方法?

> **Action**: 或是 API design, 是否能提供測試隔離區域，讓 developer 進行測試不會受到阻礙? 



## 4. API 是否易於除錯? 追查 LOG? 

API 把複雜的機制隱藏在後端服務內，同時也把錯誤的細節隱藏起來了。碰到問題需要追查時，你的 API / SDK 是否能有效
的協助 developer 快速的界定問題?

提供妥善的 logging 機制是關鍵之一，妥善的 error handling 機制也是關鍵之一。常常為了安全問題，給 end user 看的
資訊不能太詳細。但是給 developer 則要越仔細越好，才能盡可能釐清錯誤原因。API 的提供者怎麼拿捏這些界線，也是考驗
之一。

> **Action**: 能否有效的管理 log? 是否有 exception handling 的配套機制?



## 5. API 是否易於管理? 監控? 

通常這類問題，是系統穩定上線一段時間後才會重視的問題了。API 的提供往往是個攻防戰，一方面你會希望 API 用的越多越好。
另一方面 API 太開放，可能會導致你的服務被濫用。例如 google maps API 就有每日呼叫的限制，Pokemon Go 大紅，所以一堆
寶可夢地圖服務跟官方就在玩攻防戰...

這裡我指的管理，包含:

1. 你的 API 授權給那些 developer 使用? 通常是用 API token 申請的機制來管控。而你有提供這服務嗎? 你需要自己開發使用你 API 時申請 KEY 的服務嗎?
2. 你的 API 使用狀況監控，是否有任何異常的使用狀況?
3. 如果呼叫次數跟費用有關，你的 API 在異常的狀況是否會 alert developer? 能否設定用量達上線後自行中斷，以免費用爆量?

> **Action**: 是否能提供或是簡化這些 API 使用狀況的管理及監控需求? 若沒有的話。是否有合適的套件簡化自行開發?


需求跟 Action 列了這些，我把同性質的規再一起，大致上可以區分成三大部分:

{% comment %}
> **Action**: 是否有對應的 API documentation 解決方案? 這方案能否跟你的開發流程互相搭配?
> **Action**: 能否提供線上的方式直接呼叫 API 並觀察結果? 或是有哪些工具能提供這樣的機制? 而不是自己從頭寫一個?
> **Action**: 或是 API design, 是否能提供測試隔離區域，讓 developer 進行測試不會受到阻礙? 
> **Action**: 能否有效的管理 log? 是否有 exception handling 的配套機制?
> **Action**: 是否能提供或是簡化這些 API 使用狀況的管理及監控需求? 若沒有的話。是否有合適的套件簡化自行開發?
{% endcomment %}

1. API Framework: 處理 API 文件、體驗介面與工具鏈的支援
2. API system service: 處理 Logs, Error Handling 等任務
3. API Operation: 處理監控，擴充與高可用性支援

評估的過程我直接略過了，從結果開始說明。(1) 我選擇 swagger。swagger 他類似當年的 WSDL 一樣，定義了一套 JSON 的
結構來描述 HTTP API。透過這個規格，往上 & 往下建構起一整套的工具鏈。包含各種語言的 client / sdk generator，也
包含了動態的文件產生器，還有動態的 API 呼叫介面。甚至往後端的開發工具，還有 swaggerhub 讓你儲存及發布 API def 
的 registry 都有... 充分運用 swagger, 其實就能解決 (1) 大部分的問題了。

如果你用的是 .NET, 那麼 Nuget 的 Swashbuckle.Core 這個套件更適合，可以讓你逆向從 code 自動產生適合的 swagger
json 定義檔，同時也能產生自帶的 swagger ui, 讓你當場查閱呼叫方式說明，甚至能現場測試 API。

(2) 比較單純的是挑選 Logging 與 Error handling 的套件而已，這邊我就選擇我慣用的 NLog + ELMAH .. 其實熟悉 .net
開發的讀者們，應該都比我還熟這些，我就不再這裡獻醜了。不過除了搭配這些套件之外，如何有效查閱及管理這些 log 也是
很重要的。這部分我選擇合適的套件 (NLog + ELMAH), 同時 Hosting 在 Azure API Apps 上面。他有很完善的介面讓我很快
的查閱及觀察 Logs.

(3) 我選擇一樣是 Azure 提供的 APP Services, 其中支援的 API Apps 這種類型的應用。他解決了各種監控、設定等等的問題，
也解決了部署，擴充 (scale out / scale up)，同時也支援多個 slot, 你可以放置不同版本或用途的 Apps 供正式上線，或是
測試用途的 Apps。Azure 上面的 App Services, 從第一版的 WebSites 2012 推出以來，已經快要五年了。舉凡各種型態的
Web Apps 維運需要的管理環境，Azure 差不多都幫你準備好了，算是相當完整的 Hosting 環境。

至於其他在 (3) 提到的進階功能，我會在後續其他文章內提到: Azure API Manager.
後面就直接來看 Swagger 跟 Azure API Apps 的實際使用方式吧


# Swagger, Best API Framework & Tool chain












# Microsoft Azure - API Apps

前面講了那些需求跟建議，評估過程我就省下來了，最終我挑選的方案就是使用 Swagger 這套件 + Microsoft Azure 的 API Apps. 
部分進階的服務則會在後面的文章再介紹 Azure 的另一個服務: API Manager.

Swagger 跟你的 Hosting 關聯性沒那麼大 (還是有一點啦)，想了解 [Swagger](http://swagger.io/) 是什麼東西的人可以參考他的[官網](http://swagger.io/)。
簡單的說，Swagger 就是描述 & 定義你的 API 的格式。有點類似之前講到的 API contract, 跟當年當紅的 SOAP, Web Service 用的 WSDL (web service definition language)
目的是一樣的。Swagger 則是針對目前的主流 HTTP API / RESTful API 用的定義格式。透過這個定義，延伸出各種工具及整合服務可以使用，
也進一步提供了 swaggerhub 這樣的 repository, 讓你統一發布你的 swagger def. Swagger 已經再 API 定義這個領域建立起他的 ECO system,
是個值得學習的技術。

再好的 implementation, 你總是要有個地方去把他供起來。這邊我推薦的是 Azure App Service 裡的四個成員之一: [API Apps](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-api-apps-why-best-platform/).

API Apps 是啥東西? 看官方的說明應該比我自己講還來的清楚，各位可以先參考這篇: [API Apps Overview](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-api-apps-why-best-platform/)
