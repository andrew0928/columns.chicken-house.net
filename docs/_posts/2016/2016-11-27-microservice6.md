---
layout: post
title: "API & SDK Design #4, API 上線前的準備 - Swagger + Azure API Apps"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: API & SDK Design"
- "系列文章: 架構師觀點"
tags: ["API", "SDK", "microservice", "系列文章", "ASP.NET", "架構師", "Azure", "API Apps", "Swagger", "DX"]
published: true
comments: true
redirect_from:
logo: /images/2016-11-27-microservice6/apisdk04-logo.jpg
---

![](/images/2016-11-27-microservice6/apisdk04-logo.jpg)

寫到這邊，寫了那麼多 code, 你的 API 總該要上線了吧! 這篇就來探討一下，除了寫好 Code 之外，API 上線還要
注意什麼? API 這種東西不比一般的系統，API 的開發者是 developer, 使用者也是 developer，溝通可以用更有效率
(更宅? XD) 的方法，而不是只能靠傳統的文件~

這篇主題就擺在 API 開發完成後，要上線的考量。包括如何顧好 DX? 如何讓使用你 API 的 developer 有最好的
usability? 另外一個議題，就是如何挑選適合 hosting API service 的服務? 雲端時代就別再自己架設 server 了，
挑選個好的環境可以事倍功半，輕鬆容易就顧好 reliability.

這篇講的東西比較瑣碎，我分三個部分進行:  
**第一部分**: 以需求為主，把我考量的思考過程花點篇幅寫出來。  
**第二部分**: 介紹 [swagger](http://swagger.io) 這套 API Framework 以及 tool chain, 靠他來跟其他 developer 聰明的溝通。  
**第三部分**: Hosting 環境的選擇，我會介紹 Azure 上的 [API Apps](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-api-apps-why-best-platform/)，選用他可以替我們解決那些問題。

<!--more-->


{% include series-2016-microservice.md %}


# 除了寫好 API service 之外，你還需要些什麼?

Developer 當久了，往往除了寫 code 之外其他都會忘掉... 這就是 developer 跟 stakeholder 的差別。
切記，永遠別忘了你寫的code 是要解決什麼問題，適時地跳出框框思考，你會有不一樣的答案。前面提過了，API 的使用者
就是其他的 developer, 寫 code 來呼叫你的 API service。因此你要留意的是對這些開發者的使用體驗 - DX (**D**eveloper e**X**perience)。
DX 包含哪些東西? 

我參考了這篇文章: "[What is API Developer Experience and Why It Matters](https://www.infoq.com/news/2015/10/api-developer-experience#.WBtTAul_ScU.facebook)" 
這篇寫的不錯，很扼要的點出 **API DX** 的四個要點，截錄這文章的片段:

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
挑對服務商就很容易達到良好的 Availability, Scalability, Stability 等等。Reliability 是單純架構面的選擇，API 這類的
服務跟 WEB 並沒有明顯的差別，這篇我就不在 Reliability 上做太多討論。

至於 Usability, 尤其是對於 developer 的 usability 才是我考量的重點。對於 API 這類應用來說，具體的 Usability 
指的是什麼? 

我從我自己的經驗，把 API 的 usability 分成這幾點來探討:

## 1. API 是否易於學習與了解?  

要學會你的 API 怎麼用，提供適當的文件，是最基本的需求了。傳統的提供 PDF 或是 WORD 應該不是最好的方法。這年頭應該沒人
會把 API 文件印出來看了吧? 用 PDF 維護困難，查閱也不方便，我舉最典型的例子，用 Visual Studio 的人都知道，我在寫 code 時如果有做好 C# code comments, 那麼編譯時就可以
產出 comments xml, 同時 Visual Studio 的 intelligent sense 在你用到該 method 時，也會自動帶出那些 comments.

這已經讓 *文件* 不再只是文件，而已經是 **自動化** 而且是 **可操作** 的文件了。在 coding 的過程中，這些文件的資訊就能
自動帶出，輔助 coding 過程的進行。API 的提供者與使用者都是 developer, 其實可以有比傳統文件更好的呈現方式。能從
開發 > 維護 > 更新文件 > 發行文件的過程中，緊密和服務的更新及上線搭配，這是最理想的。

> **Action**: 是否有對應的 API documentation 解決方案? 這方案能否跟你的開發流程互相搭配?


## 2. API 是否易於學習及體驗?

使用者(developer)第一次要使用你的 API，進入障礙也是影響的因素之一。這一系列文章一直在探討的 SDK，其實就是要
簡化 API 使用門檻的方法之一。除了 SDK 之外，若能在呼叫 API 有文件以外更進一步的引導工具，讓開發者快速進入狀況的
方式都有幫助。

最常見的就是直接提供線上的 **體驗** 工具。API 不比網站服務，要怎麼 **體驗**? 我舉幾個比較知名的例子:

* Facebook [social plugins](https://developers.facebook.com/docs/plugins/):
我就拿最常見的，在你自己網站加上 "讚" 的按鈕，FB 提供了各種做法。在這個 
[示範頁面](https://developers.facebook.com/docs/plugins/like-button) 裡面，就包含這樣的工具:

---

![Facebook "讚" 按鈕配置工具](/images/2016-11-27-microservice6/apisdk04-fblike.png)

---


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

評估的過程我直接略過了，從結果開始說明:  

**(1) 我選擇 swagger。**  
swagger 他類似當年的 WSDL 一樣，定義了一套 JSON 的
結構來描述 HTTP API。透過這個規格，往上 & 往下建構起一整套的工具鏈。包含各種語言的 client / sdk generator，也
包含了動態的文件產生器，還有動態的 API 呼叫介面。甚至往後端的開發工具，還有 swaggerhub 讓你儲存及發布 API def 
的 registry 都有... 充分運用 swagger, 其實就能解決 (1) 大部分的問題了。

如果你用的是 .NET, 那麼 Nuget 的 Swashbuckle.Core 這個套件更適合，可以讓你逆向從 code 自動產生適合的 swagger
json 定義檔，同時也能產生自帶的 swagger ui, 讓你當場查閱呼叫方式說明，甚至能現場測試 API。

**(2) 比較單純的是挑選 Logging 與 Error handling 的套件**:  
這邊我就選擇我慣用的 NLog + ELMAH。  
其實熟悉 .net 開發的讀者們，應該都比我還熟這些，我就不再這裡獻醜了。不過除了搭配這些套件之外，如何有效
查閱及管理這些 log 也是很重要的。這部分我選擇合適的套件 (NLog + ELMAH), 同時 Hosting 在 Azure API Apps 上面。
他有很完善的介面讓我很快的查閱及觀察 Logs.

**(3) 我的選擇是 Azure 提供的 APP Services**:  
其中支援的 API Apps 這種類型的應用。他解決了各種監控、設定等等的問題，
也解決了部署，擴充 (scale out / scale up)，同時也支援多個 slot, 你可以放置不同版本或用途的 Apps 供正式上線，或是
測試用途的 Apps。Azure 上面的 App Services, 從第一版的 WebSites 2012 推出以來，已經快要五年了。舉凡各種型態的
Web Apps 維運需要的管理環境，Azure 差不多都幫你準備好了，算是相當完整的 Hosting 環境。

至於其他在 (3) 提到的進階功能，我會在後續其他文章內提到: Azure API Manager.
後面就直接來看 Swagger 跟 Azure API Apps 的實際使用方式吧




# Swagger, Best API Framework & Tool chain

在前面的文章，花了不少篇幅在講 API contract 的重要，所以我也一直在找合適的技術，能夠擔任這個任務。到目前為止，
我找到兩個最合我需求的技術，一個就是 [WCF](https://msdn.microsoft.com/zh-tw/library/dd456779%28v=vs.110%29.aspx?f=255&MSPPError=-2147217396), 
原生的用 .NET 的 interface, 來當作 operation contract。我只要控制
好這個 interface 的 .cs 檔案，我就能完全的掌握 API interface 是否有異動。不過 WCF 實在有點年紀了，另外他也不是
目前 API 的主流技術，有點可惜...

另一個就是今天的主角: [swagger](http://swagger.io/)

swagger, 最基本的就是他用一組 json 來描述該怎麼呼叫你的 HTTP API 的規範而已。但是光憑這一點，swagger 就建立起
整套 API 定義的 EcoSystem 了。從 API 的定義格式開始，延伸了一系列的 tools chain, 包括:

1. **Swagger Editor, server code generator, client code generator**:    
從 swagger definitions 的線上編輯器，匯入匯出及格式轉換工具，到產生 client / server side code, 各大熱門的語言與平台都有提供。
1. **Swagger UI**:  
HTML based API document & API test runner。從 swagger definitions 產生一組 HTML UI, 能夠直接查閱 API 的說明及用法，
甚至包含線上的測試工具，讓你直接免工具就可呼叫 API 看看結果。 
1. **Tools & Integration**:  
其他的 tool chain, 有興趣的可以直接參考[官方的清單](http://swagger.io/open-source-integrations/)

這邊我就簡單的把這個範例程式，套用 swagger 來示範吧! 不過篇幅有限，我只會用最基本的設定讓各位知道他是做什麼用的就好了。

在 ASP.NET WebAPI 這邊，我用的是這個 NuGet 套件: [Swashbuckle](https://www.nuget.org/packages/Swashbuckle), 
搭配 ASP.NET MVC 使用。一般我看其他人在用 swagger, 大都是先
直接或間接準備好 swagger definitions 後，才開始 generate client / server side code, 才開始開發。我這邊的用法剛好
反過來，直接寫 API code, 靠這套件動態的產生 swagger definitions json, 以及直接在 API service 上面產生 swagger ui.

我打算用 swagger 完成的順序是:

1. coding, 正確的設定及啟用 Swashbuckle, 產生正確的 swagger definitions
1. 產生對應的 swagger ui ，讓我直接在 UI 上測試 API 及查閱文件說明
1. 藉由上個步驟產生的 swagger definitions, 產生對應的 client code.

首先，我用的 project 類型是 Azure API Apps, 預設就幫我加入了 Swashbuckle 套件了。要手動加入的只要到 NuGet 安裝
這個套件: [Swashbuckle for WebAPI](https://www.nuget.org/packages/Swashbuckle)

```powershell
NuGet PM> Install-Package Swashbuckle
```

加入之後，會看到多一個啟動時會執行的設定: ```~/App_Start/SwaggerConfig.cs```。裡面的東西預設都是關掉的，你必須
手動啟用你需要的功能。以我最少的需求，我開啟了這幾項:

## 1. 指定 xml comments 檔案路徑

C# 支援你在程式碼裡面，用 ```///``` 的方式寫註解，編譯器會把這些註解的內容輸出成 XML，能串到後續的 document automation 流程。
這邊有指定的話，Swagger UI 就可以直接呈現你在程式碼的註解，非常方便!

首先，去 project property page 的 output 設定中，啟用 Xml documentation file:  
![project settings](/images/2016-11-27-microservice6/apisdk04-xmlcommentoutput.png)


接著，在 ```~/App_Start/SwaggerConfig.cs``` 啟用這段 code, 指定 xml documentation file 路徑:

```csharp
// If you annotate Controllers and API Types with
// Xml comments (http://msdn.microsoft.com/en-us/library/b2s063f7(v=vs.110).aspx), you can incorporate
// those comments into the generated docs and UI. You can enable this by providing the path to one or
// more Xml comment files.
//
c.IncludeXmlComments(System.Web.Hosting.HostingEnvironment.MapPath("~/bin/Demo.ApiWeb.XML"));
```                        

## 2. 排解 api action 衝突

ASP.NET WebAPI 支援的各種呼叫型態中，不是所有的型態 swagger 都能夠精確描述的。像我在 Get() 這邊用了 query string
做分頁，跟其他 API 混在一起時，這個套件無法正確對應，就會有兩個以上的 API 衝突。
這邊就是插入一段 code 讓你決定 swagger ui 要以哪個為主 (基本上就是要你選一個).. 我直接用預設的挑第一個.. Orz..

```csharp
// In contrast to WebApi, Swagger 2.0 does not include the query string component when mapping a URL
// to an action. As a result, Swashbuckle will raise an exception if it encounters multiple actions
// with the same path (sans query string) and HTTP method. You can workaround this by providing a
// custom strategy to pick a winner or merge the descriptions for the purposes of the Swagger docs 
//
c.ResolveConflictingActions(apiDescriptions => apiDescriptions.First());
```


## 3. 啟用 swagger ui support

文件及測試 API 的介面 (swagger ui) 預設是被停用的。把這段 code 的註解拿掉就可以啟用了。啟用之後可以用瀏覽器
開啟 ```/swagger``` 就可以看到 UI:

```csharp
// ***** Uncomment the following to enable the swagger UI *****
    })
.EnableSwaggerUi(c =>
    {
        
```

## 4. 其他的用法

其實 Swashbuckle 還有很多其他功能，以後有機會再介紹。需要的可以參考官網，或是直接到他的 GitHub 去看:

https://github.com/domaindrivendev/Swashbuckle





## 5. 測試 swagger ui

上述動作改完，重新編譯後就可以執行了。原本的 webapi 網站的網址，後面加上 /swagger/ 就可以看到畫面了:

![swagger ui](/images/2016-11-27-microservice6/apisdk04-swagger-ui.png)

果然我們在程式碼上面對 API 寫的註解，都被同步顯示到 swagger ui 上了，這些 API 你也可以直接在 swagger ui 上面
直接輸入參數，按下 [Try it out!] 當場就能看到呼叫的結果，非常方便。

至於 swagger definition 呢? 最上面的 input box 寫著一串網址，那個就是了:

```http://localhost:56648/swagger/docs/v1```

來看看產生的內容:

```json
{
    "swagger": "2.0",
    "info": {
        "version": "v1",
        "title": "Demo.ApiWeb"
    },
    "host": "localhost:56648",
    "schemes": [
        "http"
    ],
    "paths": {
        "/api/Birds": {
            "get": {
                "tags": [
                    "Birds"
                ],
                "summary": "按照指定條件，傳回符合的資料列。同時會在 HEADER 內標示總比數、從哪一筆開始、這次總共傳回幾筆\r\n$start: 指定從第幾筆開始回傳\r\n$take:  指定最多傳回幾筆 (上限 10 筆)",
                "operationId": "Birds_Get",
                "consumes": [],
                "produces": [
                    "application/json",
                    "text/json"
                ],
                "responses": {
                    "200": {
                        "description": "OK",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/BirdInfo"
                            }
                        }
                    }
                }
            },
// 後略
```

## 6. 測試 swagger code generator

這份 json 就可以拿來後續的 tool chain 做其他的應用了。我直接用 swagger editor 來簡單測試一下，看看效果...

先連到這個網址，[swagger editor online](http://editor.swagger.io/)

![](/images/2016-11-27-microservice6/apisdk04-swagger-editor.png)

把剛才從我們自己的 code 產生出來的 swagger definitions json 貼上來就可以用了。跳過各種編輯提示及預覽的功能，直接
跳到選單: Home > Generate Server > Aspnet5, 網站會讓我們下載一包 ASP.NET MVC5 WebAPI 的空白 project:

整包 project build 起來，你就有個 asp.net 版本相容 API 的空殼子了，code 都要自己填。我就貼一段最關鍵的 API controller, 看看
他替我們產生出來的 code:

```csharp
/// <summary>
/// 
/// </summary>
public class BirdsApiController : Controller
{ 

    /// <summary>
    /// 按照指定條件，傳回符合的資料列。同時會在 HEADER 內標示總比數、從哪一筆開始、這次總共傳回幾筆  $start: 指定從第幾筆開始回傳  $take:  指定最多傳回幾筆 (上限 10 筆)
    /// </summary>
    
    /// <response code="200">OK</response>
    [HttpGet]
    [Route("/api/Birds")]
    [SwaggerOperation("BirdsGet")]
    [SwaggerResponse(200, type: typeof(List<BirdInfo>))]
    public virtual IActionResult BirdsGet()
    { 
        string exampleJson = null;
        
        var example = exampleJson != null
        ? JsonConvert.DeserializeObject<List<BirdInfo>>(exampleJson)
        : default(List<BirdInfo>);
        return new ObjectResult(example);
    }


    /// <summary>
    /// HEAD: 不傳回資料，只透過 HEADER 傳回資料總筆數，方便前端 APP 預知總比數，計算進度及分頁頁數。
    /// </summary>
    
    /// <response code="204">No Content</response>
    [HttpHead]
    [Route("/api/Birds")]
    [SwaggerOperation("BirdsHead")]
    public virtual void BirdsHead()
    { 
        throw new NotImplementedException();
    }

```

大致上符合預期，連註解 code comments 都替我們搬過來了 XDD。

接下來，看看 client code generator 吧，一樣用 swagger editor, 選單 Home > Generate Client > C# .NET 2.0, 完成後會讓你
下載整個 project. 這次不看 code 了 (好多行...), 看 project 的結構:

![](/images/2016-11-27-microservice6/apisdk04-client-code-gen.png)

其實 gen 出來的 code 架構很有水準喔，我們前面講的 SDK 要注意的細節通通考慮到了。幫你把 API 還有 Model 都 Gen 出對應的
class, 如果你懶得像我一樣手工自己慢慢刻 SDK, 用 swagger editor gen 出來當作起點是個不錯的選擇。



## 7. Swagger 使用心得

平心而論，swagger 是個好東西，就 API definition, 還有搭配的 tool chain 其實做得非常完整。在這個領域上你應該不需要
傷腦筋是否要挑別的工具了，就用下去就對了。

不過要是回到我更前面講的目的，要能讓開發團隊掌控 API 相容性等等的問題，我就還沒有找到很順暢的方式搭配 Swagger 來完成他。
原先我的如意算盤是，透過 API contract, 去嚴格的控制 client / server 在長時間改版的階段都能維持相容性。若 API contract
本身也需要改版，那麼有單一的點，能在 source control 上面追蹤他的異動，這是最理想的方法。

每件事都有正反兩面。反面就是:
> 萬一 client / server side 的實作 **不小心** 違背了 API contract 的規範，造成 swagger definition 跟你的 code 行為表現不同步，
> 那麼是否有辦法透過任何工具，在編譯階段抓出問題?

這對我來說是很重要的一點。為何團隊要執行 CI (continuous integration) ? 目的就是靠 daily build 等等工具的協助，讓整合
會碰到的問題盡早自動的被發現。對於 API 沒有按照 contract 開發的話，就應該是在 CI 階段就要被抓出來的問題。不過我到目前為止
還沒找到搭配 Swagger 能很簡單做到這點的方法，實在可惜...

目前掌握的流程，有幾種可行的方式 (名字我自己編的，別拿它去 google 啊):

1. Server Side Code First:
    先寫好 server side code, 用 swashbuckle 自動產生對應的 swagger 各種應用
    - C# WebAPI code
        - (同步) Swagger definitions
        - (Code Gen) SDK client  
1. Swagger Definition First:
    先寫好 swagger definition, 用 swagger code generator 產生對應的 client / server / documentation
    - Swagger definition
        - (Code Gen) C# WebAPI code
        - (Code Gen) C# SDK code
        - (同步) API documentation

但是不管怎麼做，Code Gen 註定是要從頭來的，我沒辦法 Gen Code 出來開發到一段時間後，重新再 Gen 一份新的 Code, 然後
還能很容易的 Merge 舊的 Code 跟新的 Contract.. 另外現有的 code 跟 contract 不相容，我也還沒辦法讓他自動化檢測..

現階段還沒找到很好的搭配，變通的作法就是，既然 build time 查不出來，那我只好在 unit test 的階段多下點功夫，至少都
還在 CI 的範圍內。只是 unit test 考驗的是你測試涵蓋率的問題，效率跟精確度不如 WCF 用 interface, 靠編譯器直接幫你
檢查語法來的俐落。

若各位讀者有什麼其他的好建議，歡迎提供啊 :D





# Azure API Apps, 專為 API 設計的 hosting environment

接下來就是挑選一個合適的 Hosting 環境了。雲端時代就別再自己裝 server 架設了，之前在路上看到有人穿著一件 T-Shirt,
上面寫著:

> "Friends Don’t Let Friends Build Data Centers"

哈哈，挺有梗的 XD，不過這句話講得沒錯啊... 是朋友就別鼓吹你自己建機房.. 不知道哪家服務商想出來的點子... 
除非你很清楚這樣做的效益，否則直接用雲端大廠的服務吧，帶來的效益是不能比的。

說到 Hosting, 尤其是 API 的 hosting, 我還蠻推薦 Microsoft Azure 上面的 API Apps. 它是 Azure App Service 裡的
四個成員之一: [API Apps](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-api-apps-why-best-platform/).

官方的說明應該比我自己講還來的清楚，各位可以先參考這篇: [API Apps Overview](https://azure.microsoft.com/zh-tw/documentation/articles/app-service-api-apps-why-best-platform/)

API Apps 其實就是標準的 Web Apps, 只是 Visual Studio 的 Project Template 有專門替他準備一個樣板，替你把不必要的東西都
拿掉了，是個蠻適合的起點。這邊的考量，主要都是以減少開發者的負擔為主。你只管把 API 服務本身開發好就好，其他的能靠 Hosting 
解決就不要自己做了。直接用 Azure API Apps, 我覺得最棒的是能替你省下這幾件事:


## 1. 內建 https 支援

SSL 對於 API 服務來說，遠比一般網站還重要。在 Azure App Service 上的服務，都會提供預設的 http://{你的名字}.azurewebsites.net
這個 domain name, 同時 Microsoft 也早已準備好對應的 SSL cert 給你用了。如果你不是很在意 domain name 是不是自己的，其實
不用花費任何功夫，你就擁有 https 了。即使你挑選的是 free service plan, 也一樣提供。

## 2. API settings (swagger, cors) 支援

在 Azure Portal 上面，對於 API Apps 有專屬的 API settings 設定畫面。目前支援兩個相關設定，分別是:

1. API Definition:
![](/images/2016-11-27-microservice6/apisdk04-azure-apisettings.png)
直接讓你指定 swagger definition 的位址。如果你有用前面說明的 swashbuckle 套件，那你直接貼網址進來就好了。
這個設定不是給你用的，而是其他服務如果需要 discover api services, 那 azure 的環境就會知道要到這邊取得你的 API 定義。
你可以透過 swashbuckle 套件產生，或是另外指定預先產生的 json file 都可以。
1. CORS:
![](/images/2016-11-27-microservice6/apisdk04-azure-cors.png)
如果你的 API 是拿來讓網頁上的 script 呼叫使用的話，那麼瀏覽器會遵循多源政策，參考 CORS 的宣告，決定允不允許
其他網站的 script 來你這邊呼叫 API。這其實不靠 Azure 也做得到，不過 Azure 把他從 web.config 解放出來，你要調整
CORS 設定不需要重新 deploy api apps, 只要來 portal 更改設定即可。

## 3. 內建 logging, alert, diagnoistic 的支援

API 沒有畫面，要追查問題及除錯更需要後端管理的支援。如果我自己的 code 都沒有埋任何 log or error handling 機制，那 Azure
websites 仍然提供這些機制讓我查問題。舉個例來說，這個 sample code 我第一次佈署上去就出問題:

![](/images/2016-11-27-microservice6/apisdk04-azure-nopermission.png)

當我摸不著頭腦時，我想到了 azure websites diagnoistic 的功能:

![](/images/2016-11-27-microservice6/apisdk04-azure-diagsettings.png)

這些選項打開就會有 log files 了。我只是 demo 用，沒有 scale out 的需求，就直接把 log file 放在 VM 的 file system 上了。
省掉再開一組 storage 的功夫。

接下來發生的事件，就會被記錄在 file system 底下的 log file 了。不過要查閱 log 還有更方便的介面，就是直接用 log stream,
可以直接像 console 一樣，即時看到從開啟 log stream 畫面後的即時訊息:

![](/images/2016-11-27-microservice6/apisdk04-azure-logstream.png)

當然你想查閱過去的 log 也行, 直接把 logfile 下載回來看就是了。從這些 log 發現，原來我先前只在 debug build 啟用 xml documentation,
佈署到 azure 上面的是 release build, 沒有 xml documentation, 所以 swagger ui 抓不到就丟出 exception 了。解決後
重新佈署就可以正常運作了。

在 Monitor 的區塊內，還有其他的功能，包含查閱 event log, 查閱及時 http traffic 等等工具，還有讓你能在程式內埋好 log 後傳回
server 統計分析的 application insight, 都是很實用的功能。這些其實不影響你的 API 開發，但是當你的 API 要正式上線時，少了
這些 hosting environment 的支援，相信你一定會被這些瑣事分掉不少注意力。



## 4. 支援多個測試區域及組態，可以快速切換上線的 Deployment Slots

介紹最後一個功能。既然是開發，那你一定免不了要更新版本 (尤其現在 DevOps / CD 喊的這麼熱)。新版本上線永遠會有狀況發生。
因此最後上線前能有機會驗證，還有發生問題後能夠快速切換回之前正常的版本是很重要的。當年 2010 開始用 Azure 的 Cloud Service,
就一直很喜歡這個功能，同時讓你維持 production / staging deployment 都在線上 (各有各的 URL)。你可以測試 OK 後，按個
switch, 就在幾秒內將兩者對調，就切換上線了。一旦碰到問題，再切換一次就換回來了。有了這個功能，服務上線就變得非常簡單，
不用像過去一樣嚴陣以待那麼緊張。

同樣的功能，在 API Apps 就是 deployment slots, 你可以建立任意個數的 "slots", 讓你在上面佈署你的 code. 你可以給他
不同的 code version, 或是給他不同的 configuration. 測到你高興為止, 按下 swap, 這個選定的版本就上線了。

這邊我額外建立了 test 的 slot:

![](/images/2016-11-27-microservice6/apisdk04-azure-deployslot.png)


針對這個 test slot, 有一組獨立的 URL 跟組態設定畫面:

![](/images/2016-11-27-microservice6/apisdk04-azure-testslot.png)

正式服務的網址應該是: http://demoapiweb.azurewebsites.net

而 test slot 的服務網址，則是這個: http://demoapiweb-test.azurewebsites.net

按下 switch 後，兩個網址連接到的後端服務就會對調，新版的服務就直接上線了。佈署的過程簡化成這樣，DevOps 就有可能落實。
Azure 已經最大幅度的把操作的門檻降低了，讓專注於開發的 developer 也能進行更版。

這個 deployment slots 很好用，我通常拿它來解決我兩個問題:
1. **新版上線前的測試**:  
典型的用法，上線前先在 beta slot 上面，用正式環境的 configuration, beta code 來驗證看看有無任何使用上的問題?
沒問題就切換上線，出問題就可以倒退回上一個正常的版本。
1. **提供開發者的測試體驗區**:  
為了方便其他使用我的服務的開發者，能有測試的區域而設立的環境。開發過程中要不斷地呼叫我的 API，但是又不能一直用正式
環境的資料。否則訂單一直下訂又一直取消，我也很困擾 XD。這時典型的用法就是，設置一個 eval slot, 用正式環境的 code,
另外設置體驗環境的 configuration, 讓 developer 有個核子試爆場，可以盡情的測試看看呼叫 API 的結果。


## 5. Azure API Apps 使用心得

其實還有很多其他功能，我沒辦法一一介紹。Azure 的 App Service 已經是個很成熟的 hosting 環境，舉凡你要把 website 放上去
會用到的功能大概都已經備妥了。挑選一個適合的 hosting 環境是很重要的，畢竟維運服務，就像柴米油鹽醬醋茶一樣，只要你進了廚房
就是得面對它。能挑選一個合適的 hosting 環境，會大幅影響你的人力分配，讓你能花更多時間在改善你的服務本身，而不是在系統維護
這類維運的問題上。



# 結論

寫到這裡，這篇竟然花了一個月.. Orz. 雖然這篇講的都跟如何開發你的服務沒有直接關聯，都是講到外圍的環境或工具搭配。
但是這些環節處理得好，是能大幅提高你的 API 的開發者體驗的 (DX)。挑對了工具，用對方法，知道這些工具要幫你解決甚麼問題，
就會事倍功半。這麼一來你的 API 也開始有國際大廠的服務水準了。

寫到這裡，API 終於上線了! 接下來面臨的挑戰就是從 ver 1.0 升級到 1.1, 1.2, 2.0 了。
下一篇來談談: 在升級的過程中該如何確保你的服務能同時顧及所有應該要支援的 client ? 