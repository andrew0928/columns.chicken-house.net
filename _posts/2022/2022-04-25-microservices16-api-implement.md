---
layout: post
title: "微服務架構 - 從狀態圖來驅動 API 的實作範例"
categories:
- "系列文章: 微服務架構"
tags: ["系列文章", "架構師的修練", "microservices"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2022-03-25-microservices15-api-design/2022-03-27-15-03-23.png
---

微服務 API 的設計與實作，來到第二篇。

![](/wp-content/images/2022-03-25-microservices15-api-design/2022-03-27-15-03-23.png)
> 圖片來源: https://www.giga.de/artikel/was-ist-eine-api-schnell-erklaert/


會有這篇，其實是有感現在講架構的文章太多了, 但是每個人看了同樣的文章, 最後實作出來的落差都很大啊。很多架構類的文章都是標竿大型系統的設計，不過還沒有對應經驗的人，看了這類文章是沒辦法從小規模的系統經驗，直接跨過那道鴻溝啊，所以往往有些看的多的人，在專案上拿捏不好設計的力道，不知不覺就做了過度的設計 (過度可能是超出期待太多，或是超出能力範圍太多都算)。因此我在講完架構的設計概念後，我都會希望能搭配實作的驗證，PoC 也好, MVP 也好，總之能夠真正用能運作的方式，把要解決的情境用你想的架構實際推演一次。架構實作一定是複雜的，有很多工程問題要解決，因此能否在這階段盡可能的排除非必要的實作，又能達到驗證的目的，就是抽象化能力的考驗了。Do the right thing 比 do the things right 同樣重要，但是不先看清楚 right thing 的話會讓你後面的 do the thing right 功虧一簣，因此有了這篇文章，來驗證上一篇我介紹的方法: 用狀態機來驅動 API 設計。

所以，第二篇的主軸，我決定把內容重心擺在理想的設計，該如何搭配成熟的技術實作出來? 架構師最難的課題就是做好技術選型。你必須在整體的系統內找到背後統一的脈絡，做到每個子系統之間的協作是具有一致性的，而不是單純的從各個領域挑出最酷的技術來用就好了。例如最常見是安全機制，要在跨服務協作的前提下，讓大家的安全機制都標準化才能互通。同樣的道理，除了安全機制，其他在 Logging 處理，Configuration 的處理，認證授權的管控等等都是一樣。這些設計必須貫通整個系統，從前台 (面對 enduser)、後台 (面對客戶的管理者 staff)、中台 (面對外部開發商與營運商本身 developer / operator) 、甚至面對內部的核心系統其他 (微) 服務等等情況都是。

這些都是微服務架構設計的難題啊，我在第一篇提到如何用狀態機來收斂你的設計 (不論你用甚麼方法分析，DDD 也好，UML 也好..)，將設計與實作都能擺在狀態機上面用一樣的方式驗證。這篇，我想延續狀態機的想法，當你有了很好很收斂的設計之後，我想完整的用 .NET 的生態系走過這整個從設計到實作的過程，期待能兼顧商業需求、架構與工程的需求都能兼顧。這篇會牽涉到很多實作的細節，涵蓋實作一個完整功能的微服務必要的架構跟設計。


<!--more-->

{% include series-2016-microservice.md %}



# 重新複習: 系統設計與狀態機

既然這篇都要講到實作，那我先在這個段落先交代好需求跟全貌吧。理解全貌你才會知道你設計的力道要掌握在哪裡才是剛剛好。過度設計會浪費資源，反之則會埋下技術債。我的原則是設計要看得夠遠，但是你可以只實作你需要的部分。這是天平的兩端，要拿捏得好唯一的方式是抽象化要做的到位。抽象化作的好，你的結構就會符合實際的結構，對應夠精準就能跟得上變化 (因為邏輯結構都跟實際的一樣)。抽象化的夠精準，你就能夠在同樣的介面下，先實作基本的功能，未來有需要的話才能維持同樣的介面，但是將背後的實作水準提升到另一個檔次。

所以，關鍵就是上一篇提到的介面設計了，我用 API 涵蓋這個介面，但是實際上介面設計包含 API，以及 API 背後的邏輯跟規則等等相關機制，所以上一篇才會用狀態機 (FSM, Finite State Machine) 來收斂 API 的結構。這次我要示範的是大部分系統都會有的會員機制。我先用這張架構圖，定義一下，在微服務架構下，所謂的 "會員" 這領域的內部服務 (或是有的公司都愛稱呼他 "中台")，應該長什麼樣子?

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-05-01-35-35.png)

我想像的微服務，不是直接對外開放的 API，而是同時要服務內部其他團隊或是系統的 API 才對。因此需求主要是來自內部其他系統需要怎麼處理 "會員" 這 domain 的需求。這些 API 應該要能降低或是取代每個系統直接存取會員資料庫的要求，從 direct database access 換成 member service API access 才是，因此 API 的設計都針對內部怎麼看待 "會員" 的分析，而不是對外的各種功能或是畫面的需求。從上面這張圖來看，會員服務就是中間虛線框起來的範圍。

待會我們就拿上一篇的 FSM 以及分析出來的結果來對應了。這些 API 我力求精簡，有很多需求，其實不一定每個需求都要開新的 API。有些可以合併既有的 API (多呼叫幾次)，有些是呼叫端可以自己處理或加工，有些是需要呼叫端自己額外建立 DB 或是 local storage 就能處理的非核心需求等等。除非有分散式交易，或是大量連續呼叫 (批次處理) 有效能或回應時間的考量，否則我一律精簡的處理，力求開放的面積最小化為原則。

還記得上一篇最後的 FSM 嗎? 來複習一下, 同時先定義一下名詞:

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-05-01-43-54.png)

會員服務背後最核心的資料 (這邊我稱作 Entity), 就是一個一個會員的帳號紀錄了。每一個會員，都會有一個自己獨立運作的狀態。會員帳號資料的主要狀態，就是該帳號在系統內的啟用與停用等。狀態是會改變的，促使狀態轉移的就是 FSM 上的箭頭；每一個箭頭都代表一個動作 (action), 這通常是 API 最主要的來源。FSM 上面用狀態 (點) 跟動作 (線) 組合起來的就是狀態圖，你必須在對的狀態下才能呼叫該 API 處理該筆會員資料，只要 FSM 上沒有標示的就應該明確的禁止呼叫 (例如 HTTP API 就應該回應 403 或是 500)。呼叫的過程可能會促使狀態發生改變，連帶地就會觸發事件通知 (event)。最後就是安全問題，並不是每個人，每套系統，每個團隊拿到 API 都可以任意改變狀態的。有些是從你能存取那些範圍的資料來限定，有些事你能替這些資料做那些事來限定。這邊我舉最明確的一個來示範: 同一組 API 我要能區分是來自前台 (Web Site / BFF) 的呼叫，或是來自後台 (Admin Console) 的呼叫。兩者能操作的 API 應該有區別才對。

> 對於 API 的授權管控問題，其實遠比這裡複雜。這篇我就先交代到內外部使用者觸發的 API 呼叫的範圍就好。外部的我統一以官方網站 (user, 代表 public web_site) 的身分代表，內部的我統一以內部系統 (staff, 代表 backoffice) 為代表。下一篇我再專文說明微服務要面對的安全管理機制，該如何擴大到外部與內部的其他系統的授權管控方式。

這些資訊，其實在上一篇文章，都已經在狀態圖上面標示清楚了。為了清楚一點呈現，我把他列成表格:

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-05-01-53-17.png)

我按照行為來分類，分成三區，後面要對應 FSM 的實作會容易一些。第一區的 action, 是執行後會直接改變會員資料的狀態，因此我定義了 action, init state, final state 欄位, 來標示只有該筆資料處於 {init state} 時才能執行 {action} 動作，並且執行完畢後狀態會轉為 {final state}。同時，這動作只有列在 {Granted Identity Type} (有的系統會用 Role 來表示同樣的意義) 清單內的認證類型才能執行。這邊的 "USER" 就是指來自前台，直接對應 End User 操作所需要呼叫的 API，而 "STAFF" 則是對應後台，對應管理者操作所需要呼叫的 API。兩者功能需求就有明顯的差別了，尤其是在能做的事情上後者權限大很多。即使都是呼叫同一組 Member Service API, 至少你發給這兩者的 access token 也要有所區別才行。

看懂這張表之後，後面就好辦了。能表格化，就能變成資料結構，就能用 code 來處理。除了第一張表格收納了會影響狀態的 action(s) 之外，第二張表收的 action(s) 跟第一張表類似，要在特定狀態下才能對該使用者呼叫執行，只是執行後他的狀態不需要改變，因此 final state 欄位我就用灰色表示。第三張表就更單純了，只跟授權 ( USER or STAFF ) 有關，不針對特定使用者，或是不在意特定使用者狀態的 API 都屬於這區。

到這邊，需求都清楚了嗎? 沒問題的話就開始實作了! 以下所有的 code 都來自這個 project: [AndrewDemo.MemberServiceDesign](https://github.com/andrew0928/AndrewDemo.MemberServiceDesign/tree/article2), 這篇文章跟上一篇文章共用同一份 source code, 為了區隔，請參考 article2 這個 branch 才是這篇實作範例的部分。有興趣的可以自行到我的 GitHub Repo, 自行 fork 出去研究。


# 專案分層說明

我為這次的示範，開了一個 git repo / branch, 先說明一下整個示範的結構。我的想法是，在某個大型系統下應該會有個專屬的團隊來負責特定 domain 的 "服務"。這裡指的服務是比較廣義的，例如這篇文章的主題: 會員服務，處理這個領域問題的系統開發我都包含在內，而不是只有狹義的 "API service" 而已。

因此，除了最主要對其他團隊提供的 HTTP Rest API ( WebAPI ) 專案之外，應該也包含其他的專案。從終端地應用往內部收斂，這次我示範了這幾種類型的專案:

1. **WebAPI**:  
最終提供 HTTP API endpoint 的 code project ( asp.net core )

1. **CLI**:  
提供批次或是命令列工具操作相關指令的 code project ( console app )

1. **Core**:  
提供 (1), (2) 的共通邏輯的 share library, 包含 domain object, business logic 等等實作內容。 ( class library )

1. **Contracts**:  
跨專案共用的介面，或是對外公開的介面與模型定義 ( interface, c# ) 定義。這邊的介面定義視為 "合約"，沒有正式公告的話是不能任意更改的，就算要更動也必須顧及相容性，不能讓按照先前合約開發的系統運作失敗。這邊包含 interface / data model 的定義。作為橫跨各個專案溝通的標準規格。你可以想像所有專案應該都透過 contracts 來溝通，而 (3) 提供的 core library 則是實作這個 contracts 的 implementation. 一般而言這個 project 需要特別被列管, 異動這專案就代表異動了介面, 必須做好相容性的管理與發佈的管理。 ( class library )

1. **Tests**:  
測試專案。整個 solution 的核心關鍵是透過 (4) 定義的 interface 所發布的 (3) core library 組合而成的, 因此我也準備了 unit test project 來確保這些 core / contracts 符合我預期的運作方式執行。 ( unit test )


實際的 solution 結構跟命名如下，各位就自行對應:

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-30-16-53-36.png)


弄清楚了每個 project 存在的目的後, 哪邊有問題你就知道要查哪個 project 的 code 了。另外，也特別說明一下，在這個案例裡面我想表達的是 "API 規格的設計"，提供實作的案例是想讓各位理解這些東西怎麼被實作出來。所以在這份 code 裡面我也刻意省略了一些實作的過程，我想會對我文章有興趣的朋友們都有一些實作的能力，我就略過不丟人現眼了 XDD。

我省略的有這些地方:

1. **資料存取** (Repository):  
說實在話，在這個案例 PoC 中的 database access 完全不是我的重點，為了把資料庫加進來，我會多一堆 code 來處理 repository 跟 unit test 以及其他分層帶來的額外負擔，所以在這個案例內我就刻意簡化 repository 的設計，略過資料庫，簡化成 in memory 的資料結構。只要完全能支援 contracts 定義的要求就可以了。省略了 database access, 但是我仍然提供了 repository 的設計, 也提供了 import / export json 的設計做為替代。資料處理中有必要使用 transaction 的地方，我會在 code 裡面用對應的 lock 機制，或是用樂觀鎖定 (optimistic lock) 的方式來處理作為替代。

1. **認證授權設計**:  
這也是另一個我刻意跳過的，就是 ASP.NET Core 內建的 ```ClaimPrincipal``` 這套支援 JWT 等規範的宣告式授權設計，取而代之的是我自己花了十幾行 code 刻出來的 middleware。同樣的維持 contracts 的要求, 也維持 HTTP API 的規範，略過標準的作法，原因是 ASP.NET Core 這套機制其實背後的架構很龐大，整套弄進來我很難在一篇文章內交代完整個設計跟實作的脈絡，同時 Microsoft 的 JWT 為了整合整個 Framework 的安全體系，要顧慮到的實作細節也變多了，我選擇 [jose-jwt](https://www.nuget.org/packages/jose-jwt/) 這套件來取代...。加上微服務的使用情境不完全是單一用途的 API，授權也有區分對內對外等等不同模式，因此選擇我掌握度比較高的作法自己實作。

這些被我省略的地方，各位真正要用在實際的專案時，請自行替換成合適的 solution, 切記切記!


# API 的安全機制 - Token

威力越強，越開放，越通用的設計，對應的安全機制就越重要。如果你設計的是 Application (包含使用者介面), 你還有很多機會可以 (防呆) 約束你的系統被使用的方式。但是你一但開放成 API，代表你就無法約束別人 "應該" 怎麼呼叫你的 API 了。所有技術上可行的組合都有可能被呼叫，你無法像 UI 一樣預期或引導使用者該怎麼用。這種靈活的組合背後，很容易就凸顯出不嚴謹的設計產生的安全漏洞 (還有效能問題，阻斷攻擊等等狀況都會被放大)。

因此，我講求的是 API 背後的安全模型也應該跟 API 規格一樣，應該要有個簡單明確，貫穿全系統，而且是完全不能有例外的模型在背後支撐，你才能對抗那些奇怪的呼叫順序衍生出來的漏洞。而且這些模型必須在 API 規格的設計階段就考慮進去。安全機制，一樣屬於設計議題，你可以先實作一部分，但是不能不先設計。如果你抱持著 "功能先能動，先上線，有使用量之後再來修正安全問題"，那就太晚了... 因為我看過很多哭笑不得的設計，在規格本身前後就已經有衝突了 (也就是規格本身就有安全問題，規格本身就間接允許不安全的操作)，因此自然無法通過一些安全或是滲透的測試。被抓到了要修正就更困難了，因為是設計問題，規格已經對外公開了，所以改好他可能會造成不相容 (破壞規格)，不改好他可能會有風險...。

所以我的對應方式，安全問題一樣要先找到一個對的模型，在設計階段就先決定作法，融入在規格內。在這前提下你仍然可以分段逐步交付，一樣可以先做重要的功能，安全機制也一樣可以先開發關鍵的部分。但是跟前面案例的差異在於: 你有正確的規劃，你知道一開始能省甚麼，不能省甚麼，因此你的做法就更能避開上面的窘境，這就是差別。

我自己在思考這問題，背後的脈絡很簡單。所有的安全問題，其實最終都歸納成三大要素的組合跟判斷:

1. 你是誰 (**認證**: 證明你是誰, Authentication)
1. 你能做什麼 (**授權**: 該給你甚麼權限, Authorization)
1. 使用這功能需要什麼條件 (**存取控制**: 完成這件事需要要求那些權限, Access Control)

這邊我所謂的 "安全模型"，就是在你的應用情境內，你怎麼描述上述的三件事? 你描述的細節是否都能在文件上交代清楚變成規格? 如果可以，那麼這份規格就是以後所有測試案例的 "expacted" 的部分，你程式碼實際執行的結果 "actual" 就必須跟它一致。不一致就會觸發 "assertion" 讓測試失敗。

舉例來說，還記得上一篇文章分析到最後的 FSM 嗎?

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-05-01-43-54.png)

在這張狀態圖上面，我特地自己加了一些標示上去。其中一個就是安全模型。各位看一下上圖，從 ```START``` 到 ```CREATED``` 狀態的箭頭上，有個 ```Register()``` 這個 Action, 底下標示著 ```USER```。這標示背後的涵義就是:

1. 只有先通過系統認證機制 (例如帳號密碼登入)，取得認證的證明 (例如: session token) 或是核發給該系統的 API token，讓 Member Service API 能確認你的身分是 ```USER``` 或是 ```STAFF``` 。這裡的 ```USER``` / ```STAFF``` 包含兩個面向的意義，一個是你是哪種身分 ( ```USER``` or ```STAFF``` )，另一個是你實際上是誰 ( andrew? peter? nancy? )。
1. 在這邊我簡化授權的模型，到目前為止我只需要知道身分就足夠了 (可能下一篇我就會打破這前提了)，只要你的身分是 ```USER```，你能做的事情都一樣 (只能存取自己的資料)，沒有等級的差別；只要你的身分是 ```STAFF```，你能做的事情都一樣 (沒有系統管理員或是其他角色的差別)。因此在這前提下，```Identity Type``` ( ```USER``` or ```STAFF``` ) 同時就可以代表授權的定義了。
1. Register() 的動作上標示著 USER，就是最基本的存取控制 (Access Control) 了。意思是: "只要要執行 Register() 這動作的人，有被授予 USER 的權限，都能夠被允許執行 Register() 這動作"。

這就是我在這套 API 設計背後的安全模型。因為我按照我的需求適度簡化了，所以簡化後的規則可以很清楚的直接標示在 FSM 的 action 上面。這張加上標示過的 FSM，同時也能替我檢核安全機制了。如果 FSM 是張地圖，地圖上的每一條路都有標示誰才能走，最後按著地圖來移動就很一目了然了。

機制清楚後，只要後續的程式碼實作能精準地呈現這期待，就大功告成了。有了精準的安全模型在背後替你把關，你可以不用擔心系統有哪些意外的呼叫組合，會產生你意料之外的結果...。也許最終的系統不一定能 100% 的阻擋，但是當出問題時，至少你會有很明確的原則，判定這是 bug 還是這是合理的行為 (有時現場你一時之間會分不清楚 bug / feature / requirement change ..)，才能決定正確的處理方式。

支撐這些安全模型，背後很關鍵的就是上述三件事 (認證、授權、存取控制) 在你系統上是如何表達的? 我先破題，待會各位直接看 code 才不會一頭霧水。

1. ```MemberServiceToken```:  
認證有各種型態，使用者的登入 (檢查帳號密碼) 是一種型態，人工額外產生一把 API Key / Access Token 都算。我這邊使用的是後者，各位在 code 裡面看到 ```MemberServiceToken``` 這東西就是了。核發 token 的動作代表你相信呼叫端，所以給他一把權杖 (token) 當作信物代表你對他的信任跟授權。將來呼叫方憑著這把 token 就能行使對應的功能。這 Token 我用了 JWT 搭配數位簽章的演算法來保護，在裡面記載了認證 (你是誰) 跟授權 (你的身分) 兩個資訊，藉由 JWT 的設計，他有基本的防偽造功能 (我就當作看到對的 Token 就信任他了，不額外做其他檢查)。

我貼片段的 ```Token``` 定義給各位看，各位先自行想像一下:


> File: /AndrewDemo.Member.Contracts/MemberServiceToken.cs

```csharp

public class MemberServiceToken
{
    public bool IsInitialized { get; internal set; }

    // JWT claim: iss, issuer
    // type, USER | STAFF
    public string IdentityType { get; internal set; }

    // JWT claim: sub, subject
    // who, iosapp | androidapp | webui | {staff}@chicken-house.net
    public string IdentityName { get; internal set; }

    // 其他省略

```


其中 ```IdentityType``` 就是我所謂的身分 (在這案例我直接當作授權來使用)，而 ```IdentityName``` 則是代表你是誰 (認證)。


2. ```MemberStateMachine```:  
在設計的過程中，我刻意完全都紙上作業，我不希望太早就決定我的實作方式，反過來在不之不覺之間就影響了我的設計 (這很常見，過早考慮實作，你的設計會不自覺地挑選好實作的那個方案，但是他不一定是最適合的方案)。因此這部分我就設計了 ```MemberStateMachine``` 這類別，用程式碼與資料結構來建立 FSM。這個 ```MemberStateMachine``` 能夠完全跟 FSM 對應，因此上面的說明中，FSM 加上正確的標示就已經足以表達 Access Control 的目的了，只要我能夠將 FSM 在 code 上面重建即可。看一下下面這段 code 你大概就能想像了:


> File: /AndrewDemo.Member.Core/MemberStateMachine.cs

```csharp

public class MemberStateMachine
{
    private List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)> _fsmext = new List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)>();

    public MemberStateMachine()
    {
        this._fsmext.Add(("register", MemberState.START, MemberState.CREATED, new string[] { "USER" }));
        this._fsmext.Add(("activate", MemberState.CREATED, MemberState.ACTIVATED, new string[] { "USER" }));
        this._fsmext.Add(("lock", MemberState.ACTIVATED, MemberState.DEACTIVED, new string[] { "USER", "STAFF" }));

        // 以下省略

```

到這裡先告一段落，Code 我後面會重新交代一次，不用急著看完每一行 code. 有抓到精神即可。以上就是我對安全機制的設計，以及跟 code 的對應。

跟微服務安全機制相關，還有 Token 的操作與應用的相關主題，其實我過去也有寫過幾篇，相關文章跟參考連結我整理在這邊:

**API Token / JWT**:
- [API & SDK Design #5](/2016/12/01/microservice7-apitoken/) 如何強化微服務的安全性? API Token / JWT 的應用; 
- 讀書會 [錄影](https://www.facebook.com/andrew.blog.0928/videos/345280552513896/), [投影片](http://www.slideshare.net/chickenwu/api-token?qid=7bd09d0a-587f-4ed6-826d-d12c71f0b252&v&b&from_search=1), [Code](https://github.com/andrew0928/MeetUp.ApiTokenDemo)
- [JWT](https://jwt.io/introduction/), Json Web Token

**系列文章: "授權碼" 如何實作?**:
1. [需求與問題](/2016/02/17/casestudy_license_01_requirement/), 2016/02/17
1. [序列化](/2016/02/24/casestudy_license_02_serialization/), 2016/02/24
1. [數位簽章](/2016/02/24/casestudy_license_03_digital_signature/), 2016/02/24
1. [金鑰的保護](/2016/03/19/casestudy_license_03_appendix_key_management/), 2016/03/19



# StateMachine

開始進入主題了，有限狀態機 FSM (Finite State Machine)。前面我們都還在紙上作業，重點都在如何把資訊標示在 FSM 圖形上面。但是現在是要寫 code 了，所以除了我想辦法把圖形轉成正確的資料結構 (graph, 呈現 node 跟 transmission) 之外，我也要開始定義: 你期待狀態機回應那些問題?

這些期待，才是你要如何設計狀態機的 interface 啊! 不清楚我的問題的話，我舉個例子:

* 我想知道從目前的狀態 ```{state}```，我的身分是 ```{role}```，我能否執行 ```{action}``` 這個動作?
* 承上，如果可以，他會轉移到哪個狀態 ```{state}``` ?

當然還有其他更複雜的應用，不過我暫時不往下展開了，暫時用不到；我就先聚焦在這裡。如果我能夠儲存 FSM，同時還能回應上述問題，那我就能把 code 寫出來了。我直接把寫好的 code 給大家看:


> File: /AndrewDemo.Member.Contracts/MemberState.cs

```csharp

public enum MemberState : int
{
    UNDEFINED = 0,
    START,
    CREATED,
    ACTIVATED,
    DEACTIVED,
    ARCHIVED,
    END
}

```



> File: /AndrewDemo.Member.Core/MemberStateMachine.cs

```csharp

public class MemberStateMachine
{
    private List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)> _fsmext 
        = new List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)>();

    public MemberStateMachine()
    {
        this._fsmext.Add(("register", MemberState.START, MemberState.CREATED, new string[] { "USER" }));
        this._fsmext.Add(("activate", MemberState.CREATED, MemberState.ACTIVATED, new string[] { "USER" }));
        this._fsmext.Add(("lock", MemberState.ACTIVATED, MemberState.DEACTIVED, new string[] { "USER", "STAFF" }));
        this._fsmext.Add(("unlock", MemberState.DEACTIVED, MemberState.ACTIVATED, new string[] { "USER", "STAFF" }));
        this._fsmext.Add(("soft-delete", MemberState.ACTIVATED, MemberState.ARCHIVED, new string[] { "USER", "STAFF" }));
        this._fsmext.Add(("soft-delete", MemberState.DEACTIVED, MemberState.ARCHIVED, new string[] { "STAFF" }));
        this._fsmext.Add(("delete", MemberState.START, MemberState.END, new string[] { "STAFF" }));
                        
        this._fsmext.Add(("generate-validate-number", MemberState.CREATED, null, new string[] { "USER", "STAFF" }));
        this._fsmext.Add(("generate-validate-number", MemberState.START, null, new string[] { "USER", "STAFF" }));
        this._fsmext.Add(("generate-validate-number", MemberState.DEACTIVED, null, new string[] { "STAFF" }));

        this._fsmext.Add(("reset-password-with-old-password", MemberState.ACTIVATED, null, new string[] { "USER" }));
        this._fsmext.Add(("reset-password-with-validate-number", MemberState.ACTIVATED, MemberState.ACTIVATED, new string[] { "USER" }));
        this._fsmext.Add(("reset-password-with-validate-number", MemberState.DEACTIVED, MemberState.ACTIVATED, new string[] { "USER" }));
        this._fsmext.Add(("force-reset-password", MemberState.ACTIVATED, null, new string[] { "STAFF" }));
        this._fsmext.Add(("force-reset-password", MemberState.DEACTIVED, null, new string[] { "STAFF" }));
        this._fsmext.Add(("check-password", MemberState.ACTIVATED, null, new string[] { "USER" }));

        this._fsmext.Add(("import", null, null, new string[] { "STAFF" }));
        this._fsmext.Add(("get-members", null, null, new string[] { "STAFF" }));
        this._fsmext.Add(("get-member", null, null, new string[] { "USER", "STAFF" }));
    }


    // only for major API, major API without state change
    public virtual (bool result, MemberState? initState, MemberState? finalState) CanExecute(MemberState currentState, string actionName, string identityType)
    {
        foreach(var x in (from r in this._fsmext where r.actionName == actionName && (r.initState == null || r.initState == currentState) && r.allowIdentityTypes.Contains(identityType) select r))
        {
            return (true, currentState, x.finalState);
        }

        Console.WriteLine($"* FSM: can not execute action({actionName}) in current member state({currentState}) with token identity type({identityType}) and specified init state({currentState})");
        return (false, null, null);
    }


    // only for non specified member API
    public virtual bool CanExecute(string actionName, string identityType)
    {
        foreach (var x in (from r in this._fsmext where r.actionName == actionName && r.allowIdentityTypes.Contains(identityType) select r))
        {
            return (true);
        }

        Console.WriteLine($"* FSM: can not execute action({actionName}) in current token identity type({identityType})");
        return false;
    }
}
    
```

這次就直接貼全部的 code 了，我沒有省略，想仔細了解狀態機設計方式的人可以直接看。幾個重點有抓到就好:

## 資料結構設計:  

其實資訊科系大學的課程就教過了，學生時代沒太混的應該都念過，只是你有沒有抓到應用的時機而已。FSM 其實就是資訊科學的 Graph 而已。要表達 Graph 只要把 "點" 跟 "線" 交代清楚就好。總共有多少點紀錄清楚，哪個點跟哪個點中間有線連起來標示清楚就好。

要表達 "點" 很簡單，我宣告一個 ```enum``` 型別，把所有的狀態列上去就好了。請直接參考 ```MemberStateEnum``` 這段 code 即可。

至於 "線" 的部分，來看看這段 code 用到的型別 (我直接用 [tuple types](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/value-tuples) 了，用語法糖省掉多宣告一個類別):



```csharp

(
    string actionName, 
    MemberState? initState, 
    MemberState? finalState, 
    string[] allowIdentityTypes
)

```

1. ```actionName```:  
代表動作的名字，例如前面提到的 Register() 就是

1. ```initState```:  
代表箭頭起始那端的狀態

1. ```finalState```:  
代表箭頭終點那端的狀態

1. (其他):  
其餘你想要額外標示在箭頭上面的資訊，通通都可以加在後面。我這邊的案例我只加上 ```allowIdentityTypes```, 型別是 ```string[]```, 就是標示執行這個動作需要的授權。

因此，把整張 FSM 圖上的每個箭頭，都這樣表達，存成一個 ```List<T>``` 就可以了，就是你在上述程式碼看到的 contstructor 那段 code 在做的事情。


## 狀態機操作:

狀態機在系統上真正要發揮作用的，就是 "交通警察" 而已。我唯一需要的是在每次的 API 呼叫時，真正執行 API 的動作前，能有統一的機制，到狀態機上面確認一下這個動作能不能執行而已。能執行就放行，當作甚麼事都沒發生；不能執行就阻擋下來，直接回應錯誤代碼或是 throw exception... 。因此我設計了這個 method:

```csharp

public virtual bool CanExecute(string actionName, string identityType) { ... }

```

簡單明瞭，傳入 ```actionName``` 跟 ```identityType```, 傳回 ```bool``` 就好了。這是用來對付某些 API 並沒有特定針對某一筆會員資料的，例如 ```Import()``` 就是一例。因為沒有指定特定某一筆資料，自然也不會有該會員的狀態。這類無狀態的判斷很容易，檢查身分是否符合就夠了。至於查詢方式，靠上面儲存的資料結構，應該足以回答正確的答案了 (先不管效率跟演算法了，其實比數只有兩位數，又是 in-memory, 演算法的影響其實不大)。


接著看處理特定會員資料的動作，我設計了這個 method:

```csharp

public virtual (bool result, MemberState? initState, MemberState? finalState) CanExecute(MemberState currentState, string actionName, string identityType)
{
    // 此處省略
}

```

傳入的參數除了 ```actionName```, ```identityType``` 之外，多了第一個參數 ```currentState```, 詢問 FSM 目前的起始狀態跟身分，能否執行這個動作?

回應也擴充了一些，除了 ```bool result``` 回答可不可以之外，也多回答了如果可以，那會從哪個狀態 ```initState``` 轉移到哪個狀態 ```finalState``` ? 其實這邊有點多餘，回傳的 ```initState``` 一定就是傳入的 ```currentState```, 我之所以會這麼雞婆，原因很簡單，在後面我需要從這組結果來做樂觀鎖定的更新機制。為了能夠好好的封裝，我多傳了一個 ```initState``` 回來。

這麼一來，狀態機的部分就實作完成了。你會發現，只要你想得夠清楚，其實寫成 code 沒幾行就能搞定的。Google 找一找 state machine 你會發現有一堆套件可以用，我也不反對你找現成的，但是不見得比較簡單啊，挑了不是當的套件，往後可能也會帶來相依性的問題。是否要自己寫就請各位自行判斷了。我要說明設計，我選擇自己寫。過程容易掌握，也好說明脈絡，也不需要解釋過多跟主軸無關的套件相關議題。





# Core Service

寫到這邊，其實準備動作大概都做得差不多了，可以開始來真正面對與商業相關的部分了。到目前為止，我們完成了:

1. 繪製正確的狀態機 (FSM)
1. 設計好正確的安全模型 (```MemberServiceToken```)
1. 設計好正確的狀態機資料結構，以及回應的狀態轉移與授權檢查 (```MemberStateMachine```)

接下來的實作，我的想法是，要處理會員相關問題，至少有兩種公開的方式 ( WebAPI 跟 CLI ), 我決定把實作的部分集中到 Core 這邊處理，讓 WebAPI / CLI 單純處理操作介面的問題就好。因此設計出來的 action, 實際執行要如何更新 repoistory, 以及執行期間要如何藉由 FSM 來確認是否遵循 FSM 設計，都在 Core 這個專案內。我們就先從這個 project 開始。

先讓大家看看全貌，整個會員服務的主軸，就在這個類別 ```MemberService``` 身上。我先略過實作，讓大家看看它應該怎麼被使用:

> File: /AndrewDemo.Member.Core/MemberService.cs

```csharp

public class MemberService
{
    public event EventHandler<MemberServiceEventArgs> OnStateChanged;
    public MemberService(MemberServiceToken token, MemberStateMachine fsm, MemberRepo repo) { ... }

    // major API(s), 執行後狀態會因而改變
    public bool Activate(int id, string validateNumber) { ... }
    public bool Lock(int id, string reason) { ... }
    public bool UnLock(int id, string reason) { ... }
    public bool SoftDelete(int id, string reason) { ... }
    public bool Delete(int id, string reason) { ... }


    // domain / aggraton API(s), 會因為狀態決定能否執行，不會直接改變狀態 (除非內部呼叫了 major APIs)
    public string GenerateValidateNumber(int id) { ... }
    public bool CheckPassword(int id, string password) { ... }
    public bool ResetPasswordWithCheckOldPassword(int id, string newPassword, string oldPassword) { ... }
    public bool ResetPasswordWithValidateNumber(int id, string newPassword, string validateNumber) { ... }
    public bool ForceResetPassword(int id, string newPassword) { ... }

    public MemberModel Register(string name, string password, string email) { ... }
    public MemberModel Import(MemberModel member) { ... }
    public MemberModel GetMember(int id) { ... }
    public MemberModel GetMemberByName(string name) { ... }
    public MemberModel GetMemberByEmail(string email) { ... }

    public IQueryable<MemberModel> GetMembers() { ... }
}

```

有發現跟 FSM 的關聯嗎? 這裡列的 public method, 幾乎就是 FSM 上面分析盤點出來的所有 action 列表，我只是把它寫成 class definition 而已。不過在分析的時候並沒有分析到 input parameters, 也沒分析出 return value 的部分，在這邊我就直接按照需求補上去了。這邊我並不是以最終要開出來的 HTTP API 規格來開的，而是以 domain 的操作來開的，要對應到 HTTP，後面的 WebAPI 那層再來處理就好。

因為這些 method 已經可以跟 FSM 對照著看了，所以我期待每個 method 的行為，最好也能跟 FSM 描述的一致。 ```MemberService``` 是被動的呼叫，我並不能控制其他人該怎麼呼叫 ```MemberService``` 提供的 method, 但是我可以做的是當別人不按照 FSM 規矩來呼叫時 (例如: 在不對的狀態下呼叫不對的 method, 或是不對的身分呼叫 method) 就應該主動且明確的阻擋下來 (例如: ```throw InvalidOperationExcpeption```)，基本上我的服務就已經有很棒的行為一致性了。

接下來，其實想辦法填入一些 code, 讓這些 method 都能回應正確的結果，其實就收工了對吧! 如果你看到這邊就開始埋頭苦幹，那就要留意了，這通常也是大部分工程師的作法。不過，前面我們都花了那麼多心思，先用 FSM 做好設計了，該怎麼善用前面的準備動作，讓這裡的開發可以更專注在商業邏輯上面?

首先，我們有兩件事要做:

1. 其中一個是這時就該開始準備單元測試了  
(因為介面規格都訂出來了，先寫測試可以提早修正介面設計問題)
1. 接著要把安全機制跟狀態機整進去

兩者都完成後，第三步才是填上我們的商業邏輯 (主要是透過 repository 異動資料，以及發出對應的 event)，同時通過所有的測試案例。


## 整合安全機制與狀態確認

前面講了那麼多安全機制，甚麼認證、授權、存取控制 blah blah 的，講道理大家都會，但是要精準地變成 code 則沒那麼容易，你真的沒有把每個環節都想清楚的話，你是寫不出來的 (或是寫出來就是怪怪的)。因此，這邊我特地在實作的地方，花了一點篇幅來說明這段。

一樣，先從 ```MemberService``` 的介面設計開始看，架構問題我一向是 top down 的方向來思考，把 code 填上去我永遠是擺在後面再做。 ```MemberService``` 的 constructor 我是這樣定的:



```csharp

public class MemberService
{
    public MemberService(MemberServiceToken token, MemberStateMachine fsm, MemberRepo repo) { ... }

    // 我只列出幾個 method 當作 action 的代表
    public bool Activate(int id, string validateNumber) { ... }
    public bool Lock(int id, string reason) { ... }
    public bool UnLock(int id, string reason) { ... }
    // 以下省略

```


這個設計，某個部份是搭配 DI，以及 ASP.NET Core 的 Controller 要使用而設計的。我希望 controller 被建立的時候，DI 能夠替我注入 ```MemberService``` 進去，因此一個 ```MemberService``` instance 的生命週期我就控制在單一一個 request 內，所以我可以大方的在 ```MemberService``` constructor 內注入代表身分的 ```MemberServiceToken```, 因為在單一一個 instance 的生命週期內，使用該服務的身分應該維持不變才對。透過 DI 在 ctor 時就注入，我就可以不用在每個 method 呼叫時都還要傳一次身分資訊。一來 Microsoft 的 DI 還沒辦法很簡單的在 method invoke 時做依賴注入，二來這樣也有點蠢，我會搞得到處都有跟 domain / business 不相干的資訊進出, 有違 clean code 的各種原則。

因此，注入的三個要素分別是:
1. ```MemberServiceToken```,  
代表使用這個服務的身分資訊
1. ```MemberStateMachine```,  
代表協助服務驗證每個 method 執行正確性的 FSM
1. ```MemberRepo```,  
代表存取後端儲存的 repository (這個案例我只是簡單的寫入記憶體內而已，正規使用應該在這裡改成寫入 database)

現在，可以回頭看看前面只看了片段的 ```MemberServiceToken``` 了:

> File: /AndrewDemo.Member.Contracts/MemberServiceToken.cs

```csharp

public class MemberServiceToken
{
    public bool IsInitialized { get; internal set; }

    // JWT claim: iss, issuer
    // type, USER | STAFF
    public string IdentityType { get; internal set; }

    // JWT claim: sub, subject
    // who, iosapp | androidapp | webui | {staff}@chicken-house.net
    public string IdentityName { get; internal set; }

    // JWT claim: jti, JWT ID
    public string ID { get; internal set; }

    // JWT claim: iat, issue at
    public DateTime CreateTime { get; internal set; }

    // JWT claim: exp, expiration
    public DateTime ExpireTime { get; internal set; }

    // JWT claim: scope, api scopes, space seperate string
    public string[] Scopes { get; internal set; }
}

```

我盡可能的搭配 JWT / RFC 的規範，來定義 Token 的內容。在這個 Token 內，最關鍵的資訊就是前面提到的 ```IdentityType``` 了，它代表了驗證資訊的來源，剛好在這個服務案例裡也代表了你的執行身分是前端使用者 (USER)，還是後端的員工 (STAFF)。如果你是使用者 (USER)，那麼我會限制你只能存取自己的資訊。例如你用 andrew 登入，拿到 session token，憑這 token 我只能讓你存取 andrew 的資訊，如果你拿這把 token 要存取 nancy 的資料，我應該在服務的內部就該阻擋下來。只要你用正確的方式操作 ```MemberService``` 的話，你應該沒有任何機會透過他取得不合法資料才對。這時依靠的就是 ```IdentityName```.

另一種情況是員工雖然被授權存取整個會員服務的資料庫，但是應該也要有嚴格的稽核紀錄，這時依賴的也是 ```IdentityName```, 我們如果可以在每個 method 被呼叫時記錄下 action, identity name 等等資訊，就是個很有力的證明資訊。其餘 ID, CreateTime, ExpireTime, Scopes 這次暫時用不到，就當作設計慣例來用就好。後面需要時我在另外說明。

你也許會問，我還是可以隨便指定啊! 我自己 create 一個假的 token 不就好了? 這邊我有幾個假設前提，我盡可能地在實作層面防範這些問題:

1. ```MemberServiceToken``` 的 property 設計，只允許 internal set
1. ```MemberServiceToken``` 應該透過獨立的套件發行 (NuGet), 理想情況下應該搭配數位簽章等等機制，確保你拿到的版本是正式管道發出的
1. 唯一正規拿到 ```MemberServiceToken``` 物件的管道，只有透過 ```MemberServiceTokenHelper.BuildToken(string tokenText)``` 才能取得，而 ```tokenText``` 就是 JWT, 具備簽章驗證的能力，基本上可能會被竊聽，但是不用擔心被偽造。

所以，一切的關鍵，都來自 ```tokenText``` 的內容是從哪裡來的? 我另外準備了一個 method: ```MemberSErviceTokenHelper.CreateToken(...)``` 就能發出一把你自訂內容的 token 了，你拿到 Core 這包套件就能夠用，不過前提是你必須要有正確的 KEY ..., 才能簽出別人無法偽造，但是卻又能夠驗證的數位簽章。

這邊科普一下數位簽章的概念。JWT 如果你挑選的是非對稱式加密的演算法 ( 例如: [RSA](https://zh.wikipedia.org/zh-tw/RSA%E5%8A%A0%E5%AF%86%E6%BC%94%E7%AE%97%E6%B3%95) )，你應該就要有一對 key (public + private)。你可以用你的 private key 替 token 簽章。別人拿到 token 只要拿跟你是同一對的 public key 就能驗證通過 (或是反過來也一樣行得通)。驗證通過證明這 token 就是用同一隊 private key 發行的，理論上全世界只有你手上才有 private key, 因此全世界的人可以相信這份 token 的內容沒有被竄改。

有沒有例外? 當然有。一種是暴力破解，有大量運算能力的機構可能可以創造出另一把內容不一樣，但是卻可以通過驗證的 token ..., 但是以現在的運算能力而言，也許你要花好幾百年才算得出來。在有限的時間內你可以把它當作是安全的。另一種可能，就是你的 KEY 沒保管好，別人偷走你的 private key 就能輕易的發行造假的 token ...

基本原理就是這樣，因此你只要正確的管理 key, 並且只透過有限的管道發行，例如正確地通過帳號密碼驗證後自動發放一把限期 30 min 的 token .. 時間過了就再換一把即可。這些都是 JWT 很成熟的應用了，我簡單點出原理就好。不過，在我這次的實作，因為我沒有真的去做帳號登入的動作，所以我就偷懶了一點... 我省略的地方有兩個:

1. 加解密的演算法我沒有選用 RSA，我直接選對稱式的演算法: ```JwsAlgorithm.HS512```, 用同一把 key 來簽章跟驗證 (並且我直接把 KEY 寫在 code 內，叔叔有練過，好孩子不要學...)
1. 再來，為了方便展示與測試，我在 CLI 產生了我後面 POC 需要的 token, 因此後面的實驗我都會直接用這 CLI 產生出來的 token 繼續往下測試。你需要產生自己的 token 可以改 CLI 並且執行他，自己把結果 COPY 下來使用。我在 unit test 裡面用到的 token 都是這樣來的。

交代一下這些偷懶的地方吧 (再次強調: 好孩子不要學.. ):

> File: /AndrewDemo.Member.CLITools\Program.cs

```csharp

static void GenToken()
{
    foreach(var pair in new (string type, string name)[] {
        ("USER", "WebUI"), 
        ("STAFF", "andrew") 
    })
    {
        Console.WriteLine($"Token({pair.type}, {pair.name}):");
        Console.WriteLine("".PadRight(80, '='));
        Console.WriteLine(MemberServiceTokenHelper.CreateToken(pair.type, pair.name));
        Console.WriteLine();
    }
}

```        

以上這段 code, 可以在 CLI 這個 project 內找到。他會產生兩組 token, 第一組是 USER 身分, WebUI .. 第二組是 STAFF 身分, andrew 帳號登入。翻過 source code 的人就會看到這兩行註解，沒錯，註解裡面的就是 token 的內容:

**Token 1**, (staff, andrew, 2022/04/04 ~ +3 years)
> eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJTVEFGRiIsInN1YiI6ImFuZHJldyIsImp0aSI6IkFERTQzOUM0MjQyQjQwNEQ4NDAyRjQ0MjVEMDJDMkVGIiwiaWF0IjoxNjQ4OTk1MzY2Ljg3OTM3NiwiZXhwIjoxNzQzNjg5NzY2Ljg3OTM3ODZ9.BJbVQE2gHEpu39cz-9PQix8bHn5-GFBOriP80bi6fpo18T2nG636EeApFNd9sgcTAyf-9vYFEetUACALSU27qA

**Token 2**, (user, webui, 2022/04/04 ~ +3 years)
> eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA




至於 HS256 的 KEY 我放在 ```TokenHelper``` 的 source code 內:

> File: /AndrewDemo.Member.Core/MemberServiceTokenHelper.cs

```csharp

// 6741, base64: BgcEAQ==
private static readonly byte[] _jwt_key = new byte[] { 0x06, 0x07, 0x04, 0x01 };   

```            

我隨手挑了 6741 這串數字 (公司的某個代號) 當作 KEY, 用 16 進位來表達，就是 ```0x06070401``` 這 4 bytes 的內容 ... 註解後面我方便各位，先把 ```0x06070401``` 這串資料用 base64 編碼處理過了，擺在註解裡面。如果各位無聊的話，可以把上面的 JWT token 跟 key 都貼到 [jwt.io](https://jwt.io) 這網站上面，用線上的工具試看看:

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-30-23-39-46.png)

把 token 貼在左邊的格子內，把 base64 編碼過的 key 貼在右邊的 secret 內，你會看到右邊有解開的 json header / payload 內容，左下角有 "Signature Verified" 驗證通過的訊息。熟練一點的話，你可以用這 key, 自己修改 payload 內容，你就可以得到新的 token, 當然也可以貼到我的 code 跑看看，會有你預期的結果的。

其實 key 永遠都是資訊安全裡面最重要的一環，不論你用了多強的演算法，因為演算法都是公開的，就算不公開，Source Code 某種程度也算是半公開的 (就算你不 open source, 公司內妳總是會 pair programming, 或是 code review 吧，總是有其他人會看到妳的 code，防護等級遠遠不及密碼的防護等級)，你很難透過 "別人才猜不出來我怎麼加密的" 這種土炮演算法來保護資料的...。選對加密演算法，選擇合適的金鑰長度，同時保護好你的 key, 才是安全的關鍵。

講了這麼多，目的只有一個: 就是透過正確管道拿到 jwt token, 並且以他為基礎來設計你的安全機制是可靠的。往後的案例就在這基礎上面進行。

我先偷跑，貼一小段後面單元測試的 code, 讓看到這裡的各位體會一下，最終你該怎麼使用 ```MemberService``` 這 code:

> File: /AndrewDemo.Member.Core.Tests/MemberServiceTest.cs

```csharp

// 前台的 token, 供 user 操作使用的授權
MemberServiceToken web_token = MemberServiceTokenHelper.BuildToken("eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA");
MemberService service_for_web = new MemberService(web_token, this._fsm, this._repo);

// brian 註冊新帳號, 取得驗證碼
var m = service_for_web.Register("brian", "1234", "brian@gogo.go");
Assert.IsNotNull(m);
Assert.IsFalse(string.IsNullOrEmpty(m.ValidateNumber));
Assert.AreEqual(m.State, MemberState.CREATED);

int id = m.Id;
string number = m.ValidateNumber;
m = null;

// 尚未通過驗證，無法登入
Assert.IsFalse(service_for_web.CheckPassword(id, "1234"));

```

看懂了嗎? 你用了某一把 token 產生的 ```MemberService``` instance, 之後你用這個 instance 執行的所有動作，都會算在這個 token 代表的身分。至於這段 code 的意義，我就不說明了，各位可以看註解跟 assert 來反推背後的意義。

進行到這一步，最後我總結一下:

安全機制的三大要素: **認證** (token), **授權** (此例剛好 token 也包含了), **存取控制** (此例包含在 state machine 內) 都湊齊了，並且都注入到 ```MemberService``` 內部。因此剩下的只剩下實作把它做出來。這部分我就附上 source code 給各位慢慢研究就好。懶得 trace code 的話，你們就可以當作友人都按照規格把它實作完成，反正單元測試都能通過了 XDD，就繼續往下看文章吧。



## 單元測試案例

即使我已經很努力的簡化每個環節了，把不必要的實作都先排除，把重心擺在會員服務的介面設計上。即使如此，要面對的面向太多，狀態，身分，安全，應用情境，實作 in-memory 版本的 repository, 實作 token 驗證機制... 不斷的切換終究會有遺漏，所以在寫這段 sample code 的過程中，我覺得我做了一個正確的決定，就是隔離出明確的 contracts, 並且先寫測試再完成 ```MemberService``` 的開發。

不過，別誤會，我這個段落不是在教大家怎麼寫單元測試，我單純的是借用撰寫測試的過程，帶出使用的情境而已。好的單元測試，不只是測試而以，好的測試能清楚的帶出正確與錯誤的使用方式。比起文件跟範例程式，測試案例能帶來更好的說明與示範效果。你的文建會列出所有正確地與錯誤的 input / output 嗎? 通常都不會，單元測試能比文件帶來更精準的使用範例。你的文件能讓你真正執行看看嗎? 通常不會，單元測試為了發揮效果，都會對於繁瑣的部分簡化，或是用 Mock 替代 (例如 DB)。若照著文件，你必須先通過一連串不一定很 "Quick" 的 Quick Start 才能開始寫第一行 code ... 你的文件能讓你用 debugger 一步一步偵錯，讓你的腦袋跟上 code 跑過一遍嗎? 通常不行，但是單元測試可以，只要 CTRL-R + CTRL-T 透過 debugger 啟動測試即可...

所以我這邊就拿一個測試案例就好。這個案例在整個 solution 裡面也有，他示範了一個會員透過網站註冊，到連絡客服從後台處理的整個過程，該如何呼叫 API 都用 code 示範了一遍。我就藉這段 code 來說明一下我懶得建構完的整套系統運作方式。

首先，我先用前面放過的這張架構圖，讓大家想像一下這案例適用的情境:

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-05-01-35-35.png)


如上圖，整套系統會存取會員服務的路徑其實有好幾個。使用者註冊，一定是先匿名，透過官網進來的。這時官網應該用的是官網系統本身的身分，就是對應到測試案例的 ```web_token``` 為代表。在官網裡面就是透過 ```web_token``` 取得的 ```service_for_web``` 這個 ```MemberService``` instance 來做官網端的操作。

然而，使用者碰到問題，透過其他管道跟客服人員聯繫上之後，客服人員應該是登入後台，從後台進行進階操作來替使用者解決問題的。這時，客服人員登入後台，後台使用的身分就是以 ```staff_token``` 為代表，而後台系統應該也需要透過 ```MemberService``` 來存取會員資料，他使用的就是 ```service_for_staff``` 。

這邊我一樣適度做了簡化，實際上應該是拿 token 執行 HTTP API 才對，我在單元測試省略了這段通訊的過程，直接縮短到 token 直接取得 service 就開始測試案例了。HTTP API 的部分我延後到下個段落，說明 ASP.NET Core 的部分再來補充。

看完架構圖，能開始想像測試案例的情境後，接著就逐段來看看 test case 程式碼:


首先，初始化測試的部分:

> File: /AndrewDemo.Member.Core.Tests/MemberServiceTest.cs

```csharp

[TestInitialize]
public void Init()
{
    this._repo = new MemberRepo();
    this._fsm = new MemberStateMachine();

    // token, user | webui | 2022/04/04 ~ +3 years
    MemberServiceToken token = MemberServiceTokenHelper.BuildToken("eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA");
    MemberService service = new MemberService(token, this._fsm, this._repo);

    MemberModel m = null;

    // andrew
    m = service.Register("andrew", "0000", "andrew@123.net");
    if (m != null) service.Activate(m.Id, m.ValidateNumber);

    // nancy
    m = service.Register("nancy", "0000", "nancy@456.com");
    if (m != null) service.Activate(m.Id, m.ValidateNumber);

    // peter
    m = service.Register("peter", "0000", "peter@789.idv.tw");

    // annie
    m = service.Register("annie", "0000", "annie@012.org");
}

```

這段 code 會初始化後面測試案例的 ```MemberRepo``` 物件 (可以把它視為資料庫的 Mock)，初始化的過程就是取得代表對外網站的 token, 透過這身分對 ```MemberService``` 連續進行四個使用者 (andrew, nancy, peter, annie) 的註冊 + 啟動 動作。初始化完成後，後面的測試案例都可以在有四個會員資料的初始化 DB 開始進行測試案例。


接著來看看典型的一個會員可能會經歷的生命週期，過程中會發生甚麼事? 怎麼對應到實際的 API 互動? 我要驗證的是新會員註冊過程中一連串的操作。我試著把情境用文字寫下來:

1. 使用者 Brian 註冊新帳號 (ID: Brian, PWD: 1234, Email: brian@gogo.go)；註冊成功預期要取得 ```MemberModel```:
- 不應該傳回 ```NULL```
- 應該包含驗證碼 (不應該是 ```NULL``` 或是空字串)
- 會員狀態應該是 ```MemberState.CREATED```
1. 使用者 Brian 在尚未確認驗證碼之前，登入應該會失敗，無法登入
1. 使用者 Brian 用 (1) 得到的驗證碼，透過正常程序驗證 (例如: 點選包含驗證碼的網址) 成功後，狀態應該變為 ```MemberState.ACTIVATED```
1. 使用者 Brian 重複執行 (2) 登入動作，這次應該就會成功登入

雖然還是很饒舌，但是我已經試著白話一點了... 上面這段過程，寫成測試案例就是下面這段:



```csharp

[TestMethod]
public void BasicScenario1_NewMemberLifeCycleTest()
{
    // 前台的 token, 供 user 操作使用的授權
    MemberServiceToken web_token = MemberServiceTokenHelper.BuildToken("eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA");
    MemberService service_for_web = new MemberService(web_token, this._fsm, this._repo);

    // brian 註冊新帳號, 取得驗證碼
    var m = service_for_web.Register("brian", "1234", "brian@gogo.go");
    Assert.IsNotNull(m);
    Assert.IsFalse(string.IsNullOrEmpty(m.ValidateNumber));
    Assert.AreEqual(m.State, MemberState.CREATED);

    int id = m.Id;
    string number = m.ValidateNumber;
    m = null;


    // 尚未通過驗證，無法登入
    Assert.IsFalse(service_for_web.CheckPassword(id, "1234"));

    // 通過驗證，重新登入
    Assert.IsTrue(service_for_web.Activate(id, number));
    Assert.AreEqual(service_for_web.GetMember(id).State, MemberState.ACTIVATED);
    Assert.IsTrue(service_for_web.CheckPassword(id, "1234"));
    number = null;

```

接著來試試看，粗心的 Brian 記錯密碼，連續登入失敗的情境:

1. 使用者 Brian 記錯密碼 (正確密碼: ```1234```, 登入時輸入: ```5678```), 登入第一次失敗
- ```CheckPassword()``` 傳回 ```false```
- 第一次失敗後的狀態應該維持 ```MemberState.ACTIVATED```
1. 使用者 Brian 記錯密碼, 登入第二次失敗
- ```CheckPassword()``` 傳回 ```false```
- 第二次失敗後的狀態應該維持 ```MemberState.ACTIVATED```
1. 使用者 Brian 記錯密碼, 登入第三次失敗
- ```CheckPassword()``` 傳回 ```false```
- 第三次失敗後，由於失敗連續三次，狀態應該改為 ```MemberState.DEACTIVED```



對應的測試案例程式碼:

```csharp

// 輸入錯誤密碼三次，帳號會被鎖定
Assert.IsFalse(service_for_web.CheckPassword(id, "5678"));
Assert.AreEqual(service_for_web.GetMember(id).State, MemberState.ACTIVATED);

Assert.IsFalse(service_for_web.CheckPassword(id, "5678"));
Assert.AreEqual(service_for_web.GetMember(id).State, MemberState.ACTIVATED);

Assert.IsFalse(service_for_web.CheckPassword(id, "5678"));
Assert.AreEqual(service_for_web.GetMember(id).State, MemberState.DEACTIVED);

```


接著，Brian 試圖聯絡客服人員，客服從後台重新發送一次新的驗證碼給 Brian, 以確認他能收到註冊的 email 內容。Brian 能夠透過這組驗證碼，重設新的密碼的過程:

1. 客服收到 Brian 的要求 (透過其他管道，略過)，從後台發送新的驗證碼給 Brian.
1. Brian 收到驗證碼，能透過網站用驗證碼替他的帳號重設新的密碼 (新密碼: ```8888```)
1. Brian 用新密碼 (```8888```) 嘗試登入，登入成功
1. Brian 重新取回帳號後，再次用正常程序，進入密碼修改畫面，提供舊密碼 (```8888```) 設定新密碼 (```9527```) 成功
1. Brian 再次用新密碼 (```9527```) 登入成功



對應的測試案例程式碼:

```csharp

// 後台的 token, 供 staff 操作使用的授權
MemberServiceToken staff_token = MemberServiceTokenHelper.BuildToken("eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJTVEFGRiIsInN1YiI6ImFuZHJldyIsImp0aSI6IkFERTQzOUM0MjQyQjQwNEQ4NDAyRjQ0MjVEMDJDMkVGIiwiaWF0IjoxNjQ4OTk1MzY2Ljg3OTM3NiwiZXhwIjoxNzQzNjg5NzY2Ljg3OTM3ODZ9.BJbVQE2gHEpu39cz-9PQix8bHn5-GFBOriP80bi6fpo18T2nG636EeApFNd9sgcTAyf-9vYFEetUACALSU27qA");
MemberService service_for_staff = new MemberService(staff_token, this._fsm, this._repo);


// Brian 聯絡客服，克服從後台重新發送驗證碼
number = service_for_staff.GenerateValidateNumber(id);
Assert.IsFalse(string.IsNullOrEmpty(number));

// 取得新驗證碼，重設密碼
Assert.IsTrue(service_for_web.ResetPasswordWithValidateNumber(id, "8888", number));
Assert.IsTrue(service_for_web.CheckPassword(id, "8888"));

// 一切正常，Brian 只是單純要改密碼
Assert.IsTrue(service_for_web.ResetPasswordWithCheckOldPassword(id, "9527", "8888"));
Assert.IsTrue(service_for_web.CheckPassword(id, "9527"));

```


最後一段案例了: 客服發現使用者有違規行為發生 (略過)，決定用客服後台，將他的帳號鎖定，並且強制修改密碼。被鎖帳號後的 Brian 無論用新舊密碼都無法再登入成功。

1. 客服使用 ```.Lock()``` 的功能，鎖定 Brian 的帳號，並且標示標記: "bad user"
1. 客服使用 ```.ForceResetPassword()``` 修改密碼 (不需要舊密碼或是驗證碼，STAFF 才允許執行這動作)
1. 自此之後，Brian 無法正常登入系統。嘗試新密碼 (```8888```) 登入失敗
1. Brian 嘗試舊密碼 (```0000```, Brian 又記錯了) 登入失敗
1. Brian 無腦亂試，又連續四次用新密碼 (```8888```) 嘗試登入，都失敗

對應的測試案例程式碼:


```csharp

// 發生狀況，Brian 被客服認定為違規使用者，鎖定帳號，強制改掉密碼
Assert.IsTrue(service_for_staff.Lock(id, "tag as bad user"));
Assert.IsTrue(service_for_staff.ForceResetPassword(id, "0000"));

// 無論用新舊密碼都無法登入
Assert.IsFalse(service_for_web.CheckPassword(id, "8888"));
Assert.IsFalse(service_for_web.CheckPassword(id, "0000"));
Assert.IsFalse(service_for_web.CheckPassword(id, "8888"));
Assert.IsFalse(service_for_web.CheckPassword(id, "8888"));
Assert.IsFalse(service_for_web.CheckPassword(id, "8888"));
Assert.IsFalse(service_for_web.CheckPassword(id, "8888"));

```

單元測試的部分到此告一段落。重申依次，我想表達的不是教你寫測試，而是想要藉著測試案例的 code, 讓你更了解前面這串過程，設計出來的 API 應該怎麼被使用? 藉由這些案例跟程式碼的對應，我相信這樣比單純看 API spec 告訴你 input (parameters) 定義，跟 out (return value) 會更清楚明瞭。就像你念書是念課本，但是念過後忘了你會查字典一樣的意思。字典是拿來讓你查 (規格) 用的，不是讓你從不會到會的過程使用的。

其實在我真正寫這段 code 的過程，我是先畫設計圖 (FSM)，然後用最短時間先寫出 contracts 跟 ```MemberService``` 的 class 定義 (code 通通都是 ```throw new NotImplementException()``` 而已)。準備到這裡我就可以開始想像這些情境，然後就把 test case 寫出來了。

這段過程是修正 API 設計很重要的一環。因為透過真正寫案例，我會從呼叫者的角度來思考 API 的設計 ( input / output ) 是否洽當? 我如果前面的步驟少傳了一些 return value 回來，會不會讓我後面的案例拿不到必要的參數，導致跑不下去? 如果是，我就可以在這時候回頭修正 ```MemberService``` 的定義，再回頭來繼續寫完 test case. 不斷的重複這過程，理論上我可以拿到一份能 "合理" 的讓測試案例寫完的 API 設計規格了。當然這時案例一定都還是紅燈，之後你慢慢補完讓他一個一個變成綠燈就好。

當然，這過程中我只交代了這個完整案例，其實既然叫做 "單元" 測試，就應該還有其他更小單位的測試才對。例如 Token 怎麼產生的，State Machine 的運作細節等等，這些我就略過了 (抱歉我連這部分的 source code 也都略過了沒有示範)，這才是我一直強調我沒打算在這邊做單元測試教學，因此這段就被我略過了。有興趣的朋友可以找找其他大師們的部落格，這部分很多高手都做得比我好，我就不獻醜了 :D

到這個步驟為止，我才真正認為 API 的規格設計到此告一段落。上一篇文章我的重點都擺在 FSM + 註記，那是在抓出整個 API 的結構。你會發現上一篇完全沒談 "規格"，也就是完全沒談 API 的輸入輸出等等規格文建會看到的東西，只談狀態跟 API 呼叫的關係，以及從設計之初就考慮安全機制的部分。這邊透過實作 + 測試案例，在你花時間寫完整套系統前，盡可能的把 API 規格確認的前置作業降到最低。因為你越早能確認規格，你就越不會碰到需要打掉重練的風險。一切以規格 (合約) 為優先的設計，這才是 API (Spec) first 理念的精隨。規格確認的越精準，你後面越能同步開發 (實作規格 跟 使用規格開發應用)，團隊的生產力在這邊就會看到改善。API first, Spec first 是需要方法的，不是要你單純的 waterfall 先把規格寫完再坐後面的事情，如果沒有配套的方法，你怎麼確定你花時間寫的規格是對的? 希望我這些案例能讓各位體會到這點。





## 整合 State Machine

寫到這邊，終於可以回到 ```MemberService``` 本身了，開始來寫第一段 domain 相關的邏輯。其時這些邏輯，大部分都是對應更新或讀取 database 就結束了。不過這次的設計加上了 FSM，我開始需要在每個 public method (大約 20 個左右) 前後都包一層 check state machine 的 code, 這邊我是選擇先包裝一層 domain service, 然後後段才放上 ASP.NET Core.

這類 "要在每一個 method 呼叫前後都加上檢查" 的需求，就是很典型的 [AOP](https://en.wikipedia.org/wiki/Aspect-oriented_programming) (Aspect Oriented Programming) 啊。這是需要靠 language + framework 才能處理得漂亮的設計。ASP.NET 從遠古時代的 WebForm, MVC, 到現在 ASP.NET Core 通通都支援，只是做法各有不同而已。不過我切出 Core 這層，封裝成 domain service, 一方面不想依賴過多不必要的套件，同時又不想要寫一堆重複的 code, 於是我就自己刻了一套簡易的版本。

以下我就拿上面測試案例不斷出現的 ```Activate( )``` 這個 action 當作例子來示範好了，我先貼片段的 ```MemberService``` 實作的程式碼:

> File: /AndrewDemo.Member.Core/MemberService.cs

```csharp

public class MemberService
{
    private readonly MemberServiceToken _token;
    private readonly MemberStateMachine _fsm;
    private readonly MemberRepo _repo;

    public event EventHandler<MemberServiceEventArgs> OnStateChanged;

    public MemberService(MemberServiceToken token, MemberStateMachine fsm, MemberRepo repo)
    {
        this._token = token;
        this._fsm = fsm;
        this._repo = repo;

        // for degug only
        this.OnStateChanged += MemberService_OnStateChanged;
    }


    public bool Activate(int id, string validateNumber)
    {
        bool result = this.SafeChangeState(id, "activate", (m) =>
        {
            if (m.ValidateNumber == null || m.ValidateNumber != validateNumber) return false;

            m.State = MemberState.ACTIVATED;
            m.ValidateNumber = null;
            return true;
        });
        if (result == false) return false;
        return true;
    }

    // 以下省略

```

一樣，這是寫文章，不相關的 code 我就刪掉了，想看直接去看 source code ... 我純手工在每個 method 前後都加了一段 check state machane 的 code 後，我就放棄了。果然懶惰才是技術進步的動力，我開始掌握到底要檢查甚麼，還有要處理甚麼了。我把這段的重點擺在:

1. ```SafeChangeState()``` 要解決甚麼問題?
1. ```SafeChangeState()``` 怎麼實作?

回顧一下 FSM (對，跟前面同一張，不用捲回去比對):

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-04-05-01-43-54.png)

執行期間的思考順序是反過來的。某個 API ( action or method, 都是一樣的意思 ) 被呼叫時，你才知道現在呼叫的人想要執行哪個 action, 同時透過參數取得關鍵的 ID 之後，當下才有辦法去 database 查詢目前的狀態。這兩個資訊到手後，下一步才是到狀態圖確認看看 (確認狀態是否能轉移，確認身分是否正確)，這條路行不行得通? 

確認可行後，接下來是執行狀態轉移，這部分完全就是商業邏輯，狀態圖管不到這段的，這段一定要讓負責開發 ```MemberService``` 的人自己來寫才行。執行完畢後，除了更新會員本身的資料之外，最重要的是要將會員的狀態，按照狀態機的指示，轉移到正確的下個狀態。

然而，這同時間還得面對其他棘手的問題，例如平行處理一定會碰到的 racing condition, 如果同時有兩個 client 在同一瞬間要做狀態轉移，誰會成功? 總不能兩者都成功吧! 那麼這些機制該怎麼處理?

這邊不管誰負責，DB 也好，AP 也好，或是 Core Library 負責也好，總是要有人負責擔任協調者，只能讓其中一個 client 成功執行。其他要明確接受到錯誤訊息，並且阻擋他執行到一半。這部分沒做好，流量一大，你會發現有很多幽靈的資訊，狀態也許正確，但是關聯的資料錯誤，這些問題越晚越難追查，到最後就變成一個不夠可靠的系統... 這種程度的服務是無法架構出具規模的微服務架構的..

一旦確定能執行該 action 並且執行成功後，後面的就單純一些了 (我沒說容易喔)。後面就剩下要 "保證" 後續的處理一定會被觸發就好，這邊最典型的就是觸發 "狀態已改變" 的事件通知。我這邊就用 C# 的 event 機制來代替了。C# 用 event handler 來代表，實際上如果你有分散式的需求，應該被改寫成發送訊息到 message queue, 並且在 queue 的另一端安排對應的 worker 來接收並且處理訊息。

想到這些難題，頭就痛起來了 XDD, 不過越頭痛的問題, 就越有集中處理的價值，因為你只要搞定了，所有環節都會有一樣的處理水準。我就是這念頭才會寫這兩篇的 (咦?)。歸納一下所有狀態轉移一致的處理模式後，就來看看 ```SafeChangeState()``` 葫蘆裡面賣什麼藥:

首先畫成流程圖，上面的描述應該要有這幾個段落:

1. A.  查詢與確認目前狀態 (option)
1. B.  鎖定該筆資料
1. C.1 在順利鎖定的狀態下，再次確認 (1), 確保 (1) -> (2) 之間狀態被改變了
1. C.2 至此為止，你才算正式取得修改的鎖定權力，開始執行寫在 lambda 由呼叫端指定的更新動作。更新必須符合 [ACID](https://en.wikipedia.org/wiki/ACID) 原則，失敗時必須完全還原。
1. C.3 更新完畢，統一按照狀態機的指示，更新狀態，解除鎖定
1. D.  發送事件

其中，其實 (1) 不做也無所謂，只是不做的話你會發生過多的無效鎖定 (鎖定之後發現狀態根本不對，白白浪費鎖定的資源了)。來看看對應的 code，為了方便說明，我把上面的步驟用註解貼在 code 上:


```csharp

private bool SafeChangeState(int id, string actionName, Func<MemberModel, bool> func)
{
    // A.  查詢與確認目前狀態 (option)
    if (this._repo._members.ContainsKey(id) == false) throw new MemberServiceException($"MS: id({id}) not exist.");

    MemberState initState;
    MemberState finalState;

    // B.  鎖定該筆資料
    lock (this._repo._members_syncroot[id])
    {
        // C.1 在順利鎖定的狀態下，再次確認 (1), 確保 (1) -> (2) 之間狀態被改變了
        var check = this._fsm.CanExecute(
            this._repo._members[id].State,
            actionName,
            this._token.IdentityType);
        if (check.result == false) return false;

        // C.2 至此為止，你才算正式取得修改的鎖定權力，開始執行寫在 lambda 由呼叫端指定的更新動作。
        var model = this._repo._members[id].Clone();
        initState = model.State;

        if (func(model) == false)
        {
            Console.WriteLine($"* SafeChangeState Fail: func() return false. model was not updated.");
            throw new MemberServiceException($"* SafeChangeState Fail: func() return false. model was not updated.");
        }

        if (model.State != check.finalState)
        {
            Console.WriteLine($"* SafeChangeState Fail: state change was not match FSM. model was not updated.");
            //return false; //throw new InvalidOperationException("state change was not allowed by FSM.");
            throw new MemberServiceException($"* SafeChangeState Fail: state change was not match FSM. model was not updated.");
        }

        this._repo._members[id] = model.Clone();
        finalState = model.State;
    }
    // C.3 更新完畢，統一按照狀態機的指示，更新狀態，解除鎖定


    // D.  發送事件
    if (initState != finalState)
    {
        this.OnStateChanged?.Invoke(this, new MemberServiceEventArgs()
        {
            EventType = "StateChange",
            ActionName = actionName,
            InitState = initState,
            FinalState = finalState,
            AssoicatedMember = this._repo._members[id].Clone()
        });
    }

    return true;
}

```

這邊其實有點過度複雜了，因為我想把狀態的更新，跟商業邏輯的更新，在 code 就完全隔離開來，跨越 database 的交易執行，要分開兩段邏輯本來就不大好處理。但是我覺得這是必須學習去面對的一門課 (尤其是你必須要面對微服務架構的情況下)，因為你不學會怎麼面對它，你就拋不開一切都交給 DB 處理的限制。這是兩面刃，甜頭是一切都用 begin trans / commit 就可以搞定了，苦頭是你的瓶頸永遠會留在 database 身上，包含邏輯被迫留在 SQL 指令裡面，包含你有一定的機率是跳過 code 直接到 database 處理...。

因此，當你了解了 database 怎麼執行交易的原理時 (真該好好感謝研究所時期有認真念 DBMS, **D**ata**b**ase **M**anagement **S**ystem 這堂課)，必要的時候你才會有機會用別的方式來解決他。我在這邊的範例是直接偷懶，用 C# 的 lock .., 這方式對 database 其實是完全行不通的，因為我在這個案例的 repository 是 in-memory, 只支援單機, 完全不支援 scale out, 我才在這邊用相同語意的 lock 來代表，我只是這樣來提醒我，將來這邊應該換成分散式版本的 lock .. (畢竟這篇文章的重點仍然是在 API 設計，不是 production 的實作教學)

> 想要複習一下分散式鎖定嗎? 可以參考一下我之前的文章: 架構面試題

當這個版本的 ```SafeChangeState()``` 已經能解決我前面提到的需求時，我就能用來埋在 ```MemberService``` 的每個 action 的實作了。重新回來看我們的主角: ```Activate()``` 的 code:



```csharp

public bool Activate(int id, string validateNumber)
{
    bool result = this.SafeChangeState(id, "activate", (m) =>
    {
        if (m.ValidateNumber == null || m.ValidateNumber != validateNumber) return false;

        m.State = MemberState.ACTIVATED;
        m.ValidateNumber = null;
        return true;
    });
    if (result == false) return false;
    return true;
}

```


搭配 C# 的語法靈活的彈性，善用 delegate, code 寫起來就很精簡了。完全按照前面對 ```SafeChangeState()``` 的期待: 告訴他你現在要處理誰(ID)的資料? 要呼叫哪個 action? 前後標準化的驗證跟鎖定機制就統一被 ```SafeChangeState``` 處理掉了，剩下的，你只要用 delegate 把你要做的事情填進去就好。

後面會雞婆，多個 if 是因為我想把這段 code 變成一個樣板，讓所有的 action 直接拿去用。而有些 action 需要有自訂的錯誤處理機制，這裡剛好沒有，就會顯得有點累贅。



## 事件通知

最後，來到相對整個段落來說最單純的部分了，狀態改變的事件處理。

事件處理，在早期語言或是執行環境不支援的時候，寫起來是很麻煩的。不知有沒有朋友寫過 windows 3.1 (你沒看錯，就是 windows 3.1) 那個年代，用 windows SDK 一行一行 code 慢慢寫出一個視窗的年代? 那個年代的 windows application, 通通都是事件處理的體系在驅動的，寫 code 的第一件事就是處理 message loop... 一路卅年發展至今，C# 要處理 event 已經濃縮成 language 的一個修飾字就搞定了...。

同樣的我這邊是想表達，設計出來的 API 規格應該包含事件處理這種 callback 型態的對應機制，在語言層級就 C# 的 event 就能很妥善的處理了。當你想要擴大到 process 層級，或是 node (network) 層級的處理方式，你可以有很多標準的技術選擇。例如公司內部分散式的事件處理，你也許可以選用支援 topic 的 message queue 來用 (例如 Kafka)，如果你是跨公司或是跨系統的層級，你也許可以內部使用 message queue + worker, 對外用 webhook callback 的方式處理。

就如同前一個段落我把 "鎖定" 的概念從語言層級的 C# lock, 到 database 內建的 transaction, 到跨系統的 distributed lock, 觀念是一致的, 影響範圍不同就會有不同的技術來支持。搞清楚這些對應關係後，你就不會被特定的工具或是 tech stack 綁住了，你可以自由自在的切換這些技術，但是背後沿用同樣的設計。

回到事件的處理，我這邊正好沒有放在測試案例內，但是善用我這邊測試案例的作法，你能夠很快地從實際案例取得設計的回饋。你如果有些複雜的應用，不確定事件定義的好不好，就把它寫成測試案例吧! 如果你發現一切都簡化的情況下 (從分散式環境，縮減到同樣設計，但是在單一 process 單一語言的範圍內) 你還無法把這段 code 用測試案例表達出來，那代表你的設計跟你的需求是有偏差的。

我這邊指埋了一個事件的應用，就是當作 logger, 只要有事件觸發，就在 console 印出一行訊息而已。用法就在 ```MemberService``` 的 constructor 內，你看得懂 C# 的 event 大概就沒問題了。這裡是事件處理的部分:



```csharp

public event EventHandler<MemberServiceEventArgs> OnStateChanged;

public MemberService(MemberServiceToken token, MemberStateMachine fsm, MemberRepo repo)
{
    this._token = token;
    this._fsm = fsm;
    this._repo = repo;

    // for degug only
    this.OnStateChanged += MemberService_OnStateChanged;
}

private void MemberService_OnStateChanged(object sender, MemberServiceEventArgs e)
{
    Console.WriteLine($"* OnStateChanged Event: Member({e.AssoicatedMember.Id}) state({e.InitState} => {e.FinalState}) via action({e.ActionName}).");
}

```



若要看事件發送的部分，其實在前面 ```SafeChangeState()``` 最後一段就是了:



```csharp

// D.  發送事件
if (initState != finalState)
{
    this.OnStateChanged?.Invoke(this, new MemberServiceEventArgs()
    {
        EventType = "StateChange",
        ActionName = actionName,
        InitState = initState,
        FinalState = finalState,
        AssoicatedMember = this._repo._members[id].Clone()
    });
}

```

中間的機制，就是 C# 內建的機制模擬出來的，你可以省略繁瑣的架設 message queue 等等囉嗦的過程就能在單一系統內實作 pub / sub 的事件處理機制。



## Core - 小結


這邊我小結一下，當你所有的 API 都能保證改變狀態是個 atom 的動作，你絕對不會因為同時有兩個 client 要改同一筆資料的狀態而導致資料異常，同時又能保證每個 API 的狀態轉移都能按照 FSM 的設計，同時執行時的 token 也都能夠符合 FSM 上面標示的存取控制要求，透過這系列的設計，程式碼的撰寫也有一致的樣板可以規範，再加上善用 FSM 做好 API 的規格設計，那麼你的 API 基本上已經有專業團隊的水準了!








# WebAPI, 從 Core 到 HTTP

當 Core 的部分都能藉由 CLI 或是 Unit Test 完成大部分的情境需求時，剩下的就很簡單了，我只需要再建立一個 ASP.NET Core 的 project, 透過 HTTP API 的方式提供 Core 的服務就好了。安全機制也有了 (token), API 設計也有了 (FSM)，連規格都準備好了，其實剩下的就是把它組裝起來的工程而已。

因此，這個段落其實要講的不多，我分幾個部分來交代:

1. ```Controller```
1. ```Middleware```
1. PostMan 整合測試

## Controller

首先，先來看 WebAPI 專案的主體: controller, 我只列出簽章 (我偷懶，直接用 ```[FromForm]``` 來 Binding 參數), 實作的部分我後面同樣挑 ```Activate(...)``` 代表說明:


File: D:\CodeWork\github.com\AndrewDemo.MemberServiceDesign\AndrewDemo.Member.WebAPI\Controllers\MembersController.cs

```csharp

[ApiController]
[Route("[controller]")]
public class MembersController : ControllerBase
{
    public MembersController(MemberServiceToken token, MemberService service) { ... }

    [HttpPost]
    [Route("register")]
    [MemberServiceAction(ActionName = "register")]
    public IActionResult Register([FromForm]string name, [FromForm] string password, [FromForm] string email) { ... }

    [HttpPost]
    [Route("{id:int:min(1)}/activate")]
    [MemberServiceAction(ActionName = "activate")]
    public IActionResult Activate(int id, [FromForm]string number) { ... }

    [HttpPost]
    [Route("{id:int:min(1)}/lock")]
    [MemberServiceAction(ActionName = "lock")]
    public IActionResult Lock(int id, [FromForm] string reason) { ... }

    [HttpPost]
    [Route("{id:int:min(1)}/unlock")]
    [MemberServiceAction(ActionName = "unlock")]
    public IActionResult UnLock(int id, [FromForm] string reason) { ... }

    [HttpPost]
    [Route("{id:int:min(1)}/soft-delete")]
    [MemberServiceAction(ActionName = "soft-delete")]
    public IActionResult SoftDelete(int id, [FromForm] string reason) { ... }

    [HttpPost]
    [Route("{id:int:min(1)}/delete")]
    [MemberServiceAction(ActionName = "delete")]
    public IActionResult Delete(int id, [FromForm] string reason) { ... }

    // 以下省略
}

```

我先貼簽章給各位看，目的是因為熟悉 ASP.NET Core 的朋友，應該看了簽章就能對應 API 的規格了。本來我想要雞婆多列出 swagger, 不過看起來似乎沒那個必要，有 source code 對於 .NET 領域的各位應該更直覺一點。

基本上，簽章訂好了，剩下的就是把 code 填進去了 ( 就是我程式碼  { ... } 的部分 )。其實內容都雷同，都同一個樣板刻出來的，我只貼一個就好:


```csharp

[HttpPost]
[Route("{id:int:min(1)}/activate")]
[MemberServiceAction(ActionName = "activate")]
public IActionResult Activate(int id, [FromForm]string number)
{
    this._service.Activate(id, number);
    return this.Ok();
}

```

由於我們在 Core 的專案已經把大部分的任務都處理完了，這邊 ```Controller``` 真的只是做一點剪刀糨糊的手工藝而已。在 controller ctor 就注入的 ```MemberService _service```, 直接把 WebAPI 接到的參數 id / number 轉進去，並且把傳回直接到 response 就結束了。當然你需要追加參數檢查，或是額外的錯誤訊息處理，就自行追加就好。


## DI 注入

不過，在 controller 的範圍內，完全沒看到安全管控這件事，他藏到哪裡去了? 另外，有個沒看過的 attrib: ```MemberServiceAction```, 這是幹嘛用的?

前面提到, ASP.NET Core 其實已經是個完整的 framework 了，你需要 AOP 的支援也難不倒他。這個 attrib, 跟安全機制其實背後是有關連的。我們從 DI 的處理順序開始看:

首先，在 Startup.cs 裡面，藏了這段 code:


File: /AndrewDemo.Member.WebAPI/Startup.cs

```csharp

// This method gets called by the runtime. Use this method to add services to the container.
public void ConfigureServices(IServiceCollection services)
{
    services.AddControllers();

    services.AddSingleton<MemberRepo>(new MemberRepo(0, @"init-database.jsonl"));
    services.AddSingleton<MemberStateMachine>();
    services.AddScoped<MemberServiceToken>();
    services.AddScoped<MemberService>();
}

```

按照 ASP.NET Core 的慣例, 在這裡把你需要的 DI 注入都先準備好。我注入了幾個物件，供後面的 code 需要時可以 resolve:

1. ```MemberRepo```, Signleton
1. ```MemberStateMachine```, Singleton
1. ```MemberServiceToken```, Scoped
1. ```MemberService```, Scoped

特別留意一下 (3), (4), 因為 HTTP 執行過程中，最小單位是 request, 在 request 執行過程中不可能替換呼叫者的身分，因此跟安全相關的 token 以及需要依賴它的 service 都註冊為 scoped. 這邊註冊完成後，自然在 controller ctor 建立物件時就能夠取的到。

那麼問題來了，整個安全機制最關鍵的 token 是從哪邊來的? 我們往下看下一段: Middleware / AOP


## Middleware

Microsoft 的 ASP.NET Core 有很好的擴充機制設計，其中我最喜歡的一個就是 Middleware. 可以先看一下官方的文件，我取用了文章內的一張圖來說明:

[ASP.NET Core Middleware](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/middleware/?view=aspnetcore-6.0)

![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-05-02-21-55-40.png)



```Middleware```, 就像的接力賽一樣，每個 HTTP Request 進入處理程序後，會依序交由註冊過的 middleware 逐一處理。處理過後才會交給下一棒。當然，這些 request, 最終會交給 controller 處理。掌握好 middleware 的運作方式，你就有能力在適當的地方先把 request 的前置作業處理好。

我的想法就是，先用一個自訂的 middleware, 在 controller 還沒被執行時就先處理好 token, 讓每個 request 執行時，透過 DI 取出的 token 就已經是正確的內容，宣告成 scoped 可以確保同一個 request 拿到的 token 一定是同一個，所以我只需要在 middleware 搶先處理完成就好了。

一路再往前追，我在這邊註冊了我自己開發的 middleware, 註冊後我的 middleware 就會被安排到上圖的串列裡面了:


```csharp

public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
{
    // 以上省略

    app.UseMiddleware<MemberServiceMiddleware>();

    // 以下也省略
}

```

至於 middleware 藏在哪? 我花了點心機，我把它藏在 Core 這專案內。原因很單純，我思考了封裝的方式，既然我都準備了 Core 這個 project 來收斂所有相關的邏輯，Middleware 雖然是 ASP.NET Core 特有的技術，但是裡面也包含我想收斂的邏輯啊，我們的團隊都是以 .NET 為主力開發的，也許我會碰到多個不同用途的 ASP.NET Core 專案，都需要透過我的 Core 提供不同用途的 API, 這時讓 Middleware 能夠重複使用，並且由統一的團隊 (負責 Core 的團隊最適合了) 來維護也是很合理的... 尤其有些封裝我還需要用到 C# 的 ```internal``` 這防護層級，種種原因都讓我決定把 ```MemberServiceMiddleware``` 擺在 Core 這個專案。

交代完結構跟思考背景，接著先來看 code:


> File: /AndrewDemo.Member.Core/MemberServiceMiddleware.cs

```csharp

public class MemberServiceMiddleware
{
    private readonly RequestDelegate _next;
    private const string _bearerText = "Bearer ";

    public MemberServiceMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    // if return false, bypass next middleware chain.
    private bool PreProcessMemberService(HttpContext context, MemberServiceToken token, MemberStateMachine fsm, MemberService service)
    {
        if (context.Request.Headers.TryGetValue("authorization", out var values) == false) return true;
        if (string.IsNullOrEmpty(values.FirstOrDefault())) return true;
        if (values.FirstOrDefault().StartsWith(_bearerText, StringComparison.OrdinalIgnoreCase) == false) return true;

        var tokenText = values.FirstOrDefault().Substring(_bearerText.Length);
        MemberServiceTokenHelper.BuildToken(token, tokenText);

        // Members only
        if (context.Request.RouteValues["controller"] as string != "Members") return true;

        int? id = null;
        if (context.Request.RouteValues.ContainsKey("id"))
        {
            id = int.Parse(context.Request.RouteValues["id"] as string);
        }

        string actionName = null;
        var ep = context.GetEndpoint();
        if (ep != null)
        {
            MemberServiceActionAttribute action = (
                from x in ep.Metadata
                where x is MemberServiceActionAttribute
                select x as MemberServiceActionAttribute).FirstOrDefault();
            Console.WriteLine($"Action: {action.ActionName}");
            actionName = action.ActionName;
        }

        service.FSMRuleCheck(id, actionName);
        return true;
    }

    public async Task Invoke(HttpContext context, MemberServiceToken token, MemberStateMachine fsm, MemberService service)
    {
        try
        {
            if (this.PreProcessMemberService(context, token, fsm, service))
            {
                await _next(context);
            }
        }
        catch (MemberServiceException e)
        {
            context.Response.StatusCode = 500;
            await context.Response.WriteAsync("MemberStateMachineException: " + e.Message);
        }
    }
}

```

這個 Middleware 主要的任務，就是按照 JWT 的規格，從 HTTP Request Header 取得 token 內容後，交給前面單元測試就看過的物件: ```MemberServiceTokenHelper``` 來處理。經過檢驗簽章，解析出 payload, 並且轉成對應的 ```MemberServiceToken``` 後，更新 DI scope 內的 token (特地宣告成 ```internal```, 就是要確保只有 ```Middleware``` 能夠更新 token), 一切就大功告成。這麼一來我就能確保 controller 在處理過程中，拿到的 ```MemberService``` 背後都是用到正確的 token, 自然我就能信賴背後的狀態機及安全機制檢驗了。

那麼，另一個還沒交代到的: ```MemberServiceAttribute``` 又是幹嘛的?

重新來看看這段 ```Activate``` 的 code:


```csharp

[HttpPost]
[Route("{id:int:min(1)}/activate")]
[MemberServiceAction(ActionName = "activate")]
public IActionResult Activate(int id, [FromForm]string number)
{
    this._service.Activate(id, number);
    return this.Ok();
}

```

這個 attrib 的用意很單純，就是宣告這個 HTTP API 綁定的 actionName 是 activate, Middleware 後段個 code 就會拿這個 ```ID``` / ```ActionName``` 先到 ```StateMachine``` 檢查一下，不合理的 Request 呼叫順序就先阻擋下來了。

其實，在 ```this._service.Activate(id, number)``` ```被呼叫時，MemberService``` 內部的實作就知道你要執行的 ```actionName``` 了。不大需要如此大費周章地在宣告一次啊。我最終決定在這裡重複處理兩次 FSM 檢查，最主要的差別在於: 

1. ```Middleware``` 處理的範圍是全域的，可以統一處理所有 request 的檢查
1. ```Middleware``` 統一處理，也能夠統一處理 error response 的格式
1. 有些情況下， ```Controller``` 的 API 跟 ```MemberService``` 不見得是 1 : 1 的。我可能為了方便額外開出多合一的 API。 ```MemberService``` 回應的規格是 C# 的慣用方式 (例如 throw exception)，而 ```Controller``` 要回應的方式卻是 HTTP 慣用的方式 (例如: 有標準規範的 errpr response body / code), 用 middleware 能統一處理
1. 最重要的一點，Middleware 優先順序比 controller 還早，處理得當你可以完全不必依賴 controller, 如果職責的區分真的分成 Core 團隊 (負責開發 Core 這個 project)，跟 Feature Team 團隊 (負責開發 ASP.NET Core WebAPI) 的話，提早在 ```Middleware``` 處理完畢的好處是說不完的

因此，我才會額外開了這條路，還記得前面講資訊安全的三大判斷因素嗎? 在 middleware 需要取得**你是誰** (token)，你**要做什麼** (id, action)，你被**授權**了甚麼 (state machine).. 這三件事就差了 action name, 因此我用 ```MemberServiceAttrib``` 這方式來解決，只要開發 WebAPI 團隊的人記得按照規矩標上正確的 attrib, 就能把整串安全機制的防護網搭建起來。

這整套的做法，其實也是 .NET 領域很常見的做法。早在當年 .NET Framework 的年代就已經是標準做法了，這也是我很常拿來處理 AOP 的手段。


## 整合測試 (PostMan)

寫到這邊，總算把我心裡想像中，理想的微服務實作方式都交代了一輪了。最後講了那麼多，我當然要用 HTTP 的方式來驗證看看。我們就用 ```PostMan``` 跑一次前面的測試案例吧! 步驟太多，我就是範入門的用法，其他各位有興趣我相信你有能力自己依樣畫葫蘆完成他的。

前面提到的所有案例，都沒有示範到不影響狀態的 API，例如 ```GetMembers(...)``` 這些，最後我就拿 ```GetMember(...)``` / ```GetMembers(...)``` 當作示範案例吧。

會員服務這類應用，因為牽涉到個資 (不論是 ID, Email, 密碼等等)，沒有做好管控，直接或是間接都有可能造成資訊外洩的。因此安全機制我優先處理。前面提到所有的安全機制都來自三大要素，之一就是: 你現在用哪個身分來存取 API ?

在系統上，這就是 token 的責任範圍了。我直接用前面 unit test 用到的 token 來示範:

> eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJTVEFGRiIsInN1YiI6ImFuZHJldyIsImp0aSI6IkFERTQzOUM0MjQyQjQwNEQ4NDAyRjQ0MjVEMDJDMkVGIiwiaWF0IjoxNjQ4OTk1MzY2Ljg3OTM3NiwiZXhwIjoxNzQzNjg5NzY2Ljg3OTM3ODZ9.BJbVQE2gHEpu39cz-9PQix8bHn5-GFBOriP80bi6fpo18T2nG636EeApFNd9sgcTAyf-9vYFEetUACALSU27qA

這把 token 的身分是 STAFF, 理論上用它就能取得客服角色能執行的權限。裡面的 Payload (你可以貼到 https://jwt.io 就看的到) 是:

```json

{
  "iss": "STAFF",
  "sub": "andrew",
  "jti": "ADE439C4242B404D8402F4425D02C2EF",
  "iat": 1648995366.879376,
  "exp": 1743689766.8793786
}

```

JTI 其實是 GUID，用來當作 unique id 用的，可以不用理他；IAT / EXP 則是指這個 token 建立跟過期的時間，是跟格林威治時間 ```1970/01/01 00:00:00``` 的秒差來換算的。你懶得自己換算的話，這個 [網站](https://www.unixtimestamp.com/) 可以應應急 XDD。這 token 預計會在 ```2025/04/03 22:16:06 (+8)``` 過期，如果你看這篇文章已經超過的話，記得自己重新用我的 code (CLI) 重新產生一把新的來用..

按照慣例，這種認證用的 token 都是放在 Http Request Header: ```Authorization``` 來傳遞的，會用 ```Bearer``` 字串當作前置。第一個案例我就用這個 HTTP Request 試著呼叫看看:

```http

GET /members/ HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJTVEFGRiIsInN1YiI6ImFuZHJldyIsImp0aSI6IkFERTQzOUM0MjQyQjQwNEQ4NDAyRjQ0MjVEMDJDMkVGIiwiaWF0IjoxNjQ4OTk1MzY2Ljg3OTM3NiwiZXhwIjoxNzQzNjg5NzY2Ljg3OTM3ODZ9.BJbVQE2gHEpu39cz-9PQix8bHn5-GFBOriP80bi6fpo18T2nG636EeApFNd9sgcTAyf-9vYFEetUACALSU27qA

```

得到的 HTTP Response:

```http

HTTP/1.1 200 OK
Date: Fri, 06 May 2022 17:58:24 GMT
Content-Type: application/json; charset=utf-8
Server: Kestrel
Transfer-Encoding: chunked

```

為了讓大家看得舒服一點，我把 HTTP Response Body 用 Json 格式美化之後貼在這裡:

```json
[
    {
        "id": 1,
        "name": "andrew",
        "email": "andrew@123.net",
        "passwordHash": "sgnevoy5D+/57YtwFyE3gA==",
        "state": 3,
        "failedLoginAttemptsCount": 0,
        "validateNumber": null
    },
    {
        "id": 2,
        "name": "nancy",
        "email": "nancy@456.com",
        "passwordHash": "sgnevoy5D+/57YtwFyE3gA==",
        "state": 3,
        "failedLoginAttemptsCount": 0,
        "validateNumber": null
    },
    {
        "id": 3,
        "name": "peter",
        "email": "peter@789.idv.tw",
        "passwordHash": "sgnevoy5D+/57YtwFyE3gA==",
        "state": 2,
        "failedLoginAttemptsCount": 0,
        "validateNumber": "26076378"
    },
    {
        "id": 4,
        "name": "annie",
        "email": "annie@012.org",
        "passwordHash": "sgnevoy5D+/57YtwFyE3gA==",
        "state": 2,
        "failedLoginAttemptsCount": 0,
        "validateNumber": "42850300"
    }
]

```

這是列出整個 DB 的動作，允許 STAFF 做這動作是合理的。如果我們都不改，只是換掉 token 呢? 這次我換另一把代表 USER 身分的 token:

> eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA


這把 token 的 JWT payload 如下:

```json

{
  "iss": "USER",
  "sub": "WebUI",
  "jti": "E5323AA5582649D7ABC9FE84129001C2",
  "iat": 1648996741.6045165,
  "exp": 1743691141.604716
}

```

過期時間是 ```2025/04/03 22:39:01 (+8)```, 換這把 token 打同一個 API (https://localhost:5000/members/):


```http

GET /members/ HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA
User-Agent: PostmanRuntime/7.29.0
Accept: */*
Postman-Token: 366b056b-cdeb-4f79-a2cb-ee79610be087
Host: localhost:5000
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
 
```

得到的回應如下:

```http

HTTP/1.1 500 Internal Server Error
Date: Fri, 06 May 2022 18:02:13 GMT
Server: Kestrel
Transfer-Encoding: chunked
 
MemberStateMachineException: * FSM: FSM rule check fail.

```

這次，被阻擋下來了。WebAPI 直接回應 ```500 Internal Server Error```, 拒絕回應所有會員的資料清單。雖然這只是個簡單的測試，但是你可以回想看看，在前面的 code 裡面，你有花很多時間，在每個環節都寫 code 去 check 權限嗎? 其實並沒有。花最多時間的都只是在設計狀態機，把設計的資訊標示在狀態機上，同時寫 code 運用 AOP 的技巧在集中的部分 (Core) 統一處理相關的流程跟安全問題，商業邏輯的部分 (更新資料庫) 則是很乾淨的隔離在旁邊。

透過這個試驗，證明這個機制有發揮預期的效果。接著我們再來測試一下不按照規矩更新資料，FSM 是否能夠阻擋下來?

先提示一下等等要執行的測試順序:
1. 註冊新帳號 (brian) => 預期: **成功**
1. 嘗試登入 => 預期: **失敗** (未通過驗證)
1. 啟用帳號 => 預期: **成功**
1. 嘗試登入 => 預期: **成功**

這個測試，用一般 USER 的身分就夠了，因此我沿用同一把 token，跑一次上面的測試案例。


(1) 首先，呼叫 ```Register(...)``` API。接下來我就以容易解說為主，直接貼 RAW Http Request / Response。


HTTP Request:

```http

POST /members/register HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA
User-Agent: PostmanRuntime/7.29.0
Accept: */*
Postman-Token: b2a4831d-6830-4943-adb8-868b6403351f
Host: localhost:5000
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 46
 
name=brian&password=1234&email=brian%40gogo.go

```


HTTP Response:

```http

HTTP/1.1 200 OK
Date: Fri, 06 May 2022 18:03:35 GMT
Content-Type: application/json; charset=utf-8
Server: Kestrel
Transfer-Encoding: chunked

```

HTTP Response Body (原回應照貼，只有調整 json 格式讓他好看一點):

```json

{
  "id": 5,
  "name": "brian",
  "email": "brian@gogo.go",
  "passwordHash": "DwN1hMmef9T0+MWVUPj1Bw==",
  "state": 2,
  "failedLoginAttemptsCount": 0,
  "validateNumber": "49589975"
}

```

(2) 嘗試登入 => 成功的因為狀態不正確而被阻擋

HTTP Request:

```http

POST /members/check-password HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA
User-Agent: PostmanRuntime/7.29.0
Accept: */*
Postman-Token: 14cdb498-2749-4df1-b690-1cfec75f24be
Host: localhost:5000
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 24
 
name=brian&password=1234

```

HTTP Response:

```http

HTTP/1.1 403 Forbidden
Date: Fri, 06 May 2022 18:04:42 GMT
Content-Type: application/problem+json; charset=utf-8
Server: Kestrel
Transfer-Encoding: chunked
 
{"type":"https://tools.ietf.org/html/rfc7231#section-6.5.3","title":"Forbidden","status":403,"traceId":"|99413c78-492ca5741b023c3e."}

```

(3) 用 (1) 取得的驗證碼 (```49589975```) 呼叫 ```Activate(...)``` => 啟用成功

HTTP Request:

```http

POST /members/5/activate HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA
User-Agent: PostmanRuntime/7.29.0
Accept: */*
Postman-Token: ff3a542d-b3c9-49f2-aaac-02e4ae2990be
Host: localhost:5000
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 15
 
number=49589975

```

HTTP Response:

```http

HTTP/1.1 200 OK
Date: Fri, 06 May 2022 18:05:17 GMT
Server: Kestrel
Content-Length: 0

```


(4) 再次嘗試登入 => 帳號密碼驗證通過

HTTP Request:

```http

POST /members/check-password HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA
User-Agent: PostmanRuntime/7.29.0
Accept: */*
Postman-Token: 08bdeab0-cae1-414d-a25f-bb50b909cb33
Host: localhost:5000
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 24
 
name=brian&password=1234

```

HTTP Response:

```http

HTTP/1.1 200 OK
Date: Fri, 06 May 2022 18:05:26 GMT
Server: Kestrel
Content-Length: 0

```

## WebAPI - 小結

由於前面有做好邏輯層的分層，把真正處理會員相關資料的領域動作 (action) 都封裝了起來，讓 WebAPI 這層就真的很單純處理通訊規格的部分。這邊的重點都在 Middleware 如何在集中的地方處理每個 API 共通的規則 (對應 StateMachine)，而 Controller 這邊則處理了最終開出去的 HTTP API 與 MemberService 對應的問題。

其實前面 (上一篇) 在講設計的時候，我為了專注主題 ( Entity 與 State Machine ) 我避開了很多外圍的細節。例如 State Machine 是標示影響狀態的行為，但是行為不一定跟 API 是完全的 1 對 1 啊! 很多時候為了方便，我們會額外開了方便使用的 API 規格 (例如合併兩個常常需要一起呼叫的 action)，或是有些動作是對整個服務下達的指令，而不是對特定資料 (例如用條件過濾，查詢符合的會員列表) 相關的 API 等等。

還有這次沒有示範的 logs 跟 tracking 也是，如果 log 的機制都封裝在 MemberService 內 (封裝 logs 機制在 MemberService 內是必要的，但不應該是唯一的)，那麼 MemberService 以外的問題就都追不到了。一般典型的作法會在 WebAPI 這層指定識別的 ID (通常是 request id, 可以貫穿全系統的用途) 方便服務與服務之間追蹤使用。

以上這些，都需要額外邏輯來讓 WebAPI 跟 MemberService, 甚至直接對應 MemberRepo 的可能性都存在，這就是 WebAPI 這層主要的存在目的了。更複雜的組合也會讓安全機制更為複雜，這些都是 Middleware 與 WebAPI Controller 有更大的發揮空間。掌握好這些不同的責任範圍，你就會對於那些需求應該擺在哪個專案內實作更清楚了。想清楚這些你就不用擔心你的服務越長越大就越難掌控。


# 結論

本來這篇實作篇，我是打算寫完 code 就盡早說明結束就收掉這篇的，沒想到 Markdown 的檔案，一寫也是寫了 100kb 以上的大小 (幾萬字跑不掉吧)...。我是秉持著我講得出來的設計，一定要是我做得出來的設計。因為業界有太多人是看了某些文章就講得頭頭是道的，為了有所區隔，我都會要求自己先做過 PoC, 確定想通了每個關鍵後, 再把自己消化過的東西寫出來。這樣的內容才算是我自己的內容啊，否則我只是替大家做好整理筆記的功夫而已。

在業界大型團隊擔任架構師，考驗的就是會講的東西做不做的出來而已。有很多環節你不去實際動手寫 code 你是不會體驗到的。像是這篇前半段我提到的 Token 安全機制，實際寫 code 才會發現，微服務之間的認證授權沒有那麼容易的。想想看你要控制的維度，有資料之間的存取授權 (例如 A 會員登入後能不能存取 B 會員的資料?)，也有服務與服務之間的授權 (例如對外網站能否存取後台才能操作的功能?) 當你的商業模式是 SaaS (Software As A Service)，系統的結構已經演進到多租戶的架構 (Multi-Tenancy) 時，認證 / 授權 / 存取控制 的關係就更複雜了，你如何在 API 層面就管理好他?

這些都是 PoC 後才能了解的細節，否則你只是單純 google "微服務", "API", "安全管控" 等等關鍵字，你是找不到這些資訊的。我想這些 PoC 架構設計的精神，才是我這篇想做的，承接上一篇的設計理念，兩篇加起來才算是完整表達我心裡想的微服務架構。

回到這兩篇的主軸: API 設計，看到這邊各位可以回想一下，過去你如果有開發過自己的 WebAPI, 你的 API 規格是怎麼出來的? 我跟不少人聊過，這幾種答案都有:

* **佛系設計**: 不用特別規劃，用到哪裡需要什麼功能，就開什麼 API 出來就好
* **外貿協會**: 一切以功能或 UI 為主。功能先做好，再重構或是重新封裝，把需要 reuse 的部分作成 API
* ...

其他也有抄別人的 (例如同業的 API 規格)，或是客戶直接幫你開好規格等等都有。試想一下良好 API 最在意的是什麼吧! 除了目的與一要清楚之外，介面規格要長時間穩定發展也是很重要的。你可以不斷地擴張新功能，但是你一定得顧好早期就使用你的 API 發展的客戶。一旦你過度頻繁的推出不相容的更新，你的客戶會被你趕跑的。因此找出一個體系能不斷的安全擴充與發展是很重要的，這些不靠良好的架構設計是半不到的。這次我用的狀態機，就是其中一種方式。

只有把這些基礎先做好，你才能享受各種快速開發與不斷的迭代改善的循環 (試想: 你每次的迭代如果都造成 breaking change, 那還算是好的服務嗎?)

講到這，我推薦一下，其實這兩篇文章提到很多內容的想法，都來自於公司內部舉辦的讀書會。近期我們有兩本書正在研讀中，得到不少收穫，有興趣的朋友們也可以去讀看看這些內容。我提供書名就好，購買管道就各自想辦法了，這不是葉佩雯，我就不貼購買連結了，單純提供書名就好:

**持續 API 管理**:  
![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-05-08-02-20-07.png)


**API Design Patterns**:  
![](/wp-content/images/2022-04-25-microservices16-api-implement/2022-05-08-02-18-32.png)


最後回到本文: API 其實就是你對於要解決的領域，抽象化的結果。你抽象化的切入點在哪，完全就影響了你的 API 怎麼設計。怎麼說? 以 C# 來說，完全的抽象化，在語言上就是用 interface 來表達了，而 API 的 "I" 就是 interface 啊! 你要表達的層次是一樣的，只是 C# 是在語言層級處理 interface, 微服務 API 則是在通訊的層級處理 interface, 差別只在如此而已。

因此，想通背後的脈絡，一直是我認為最重要的一環，那麼龐大的系統你要維持一致，你就必須做好抽象化，訂好規則，所有團隊用各自擅長的技術來配合。架構師不可能自己搞懂所有細節，原因其實很單純，因為根本不可能。如果你的團隊不大，大約 5 ~ 10 個以內，那你的確有可能摸透所有團隊採用的 tech stack, 但是這種規模的團隊通常有能力夠好的工程師就能運作順利。當團隊多到 50 - 100 甚至更多時，你不可能摸透所有的細節的 (尤其你的團隊能力越好的時候越是如此)，你能做的是訂好架構讓大家來遵循。

雖然都說是 "微" 服務了，但是不代表它就可以省略一些環節。微服務的 "微" 是指每個服務都負責單純專一的領域，是精簡，而不是簡陋。因此每個服務本身的設計考量一個都沒有少。看到這裡，你是否對於微服務 API 該怎麼設計有更精確的理解了嗎?