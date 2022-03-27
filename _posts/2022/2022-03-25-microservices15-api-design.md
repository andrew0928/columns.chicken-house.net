---
layout: post
title: "微服務架構 - 從 API 的設計來看微服務"
categories:
- "系列文章: 微服務架構"
tags: ["系列文章", "架構師的修練", "microservices"]
published: false
comments: true
redirect_from:
logo: 
---

這次我直接破題了。我想寫一篇從 State Machine 的分析為主軸，來驅動整個服務的 API 設計的文章。

![](/wp-content/images/2022-03-25-microservices15-api-design/2022-03-27-15-03-23.png)
> 圖片來源: https://www.giga.de/artikel/was-ist-eine-api-schnell-erklaert/



"Andrew, 我們服務的 API 設計很糟糕，怎樣才能設計出好的 API? 有沒有一些 SOP 或是準則可以給我參考?"

其實這個問題我已經被問到爛了，答案當然是 "沒有" 啊 XDDD, 如果有的話，這個問題根本就不會是個難題，也不會有這 FAQ 了。首先，API 的好壞，"設計" 占了九成以上啊! 設計問題是沒有正確答案的，既然是設計，就是帶有個人風格的，你會發現有些大師的設計就是既精準又靈活，看的到背後的巧思，每個環節都搭配的恰到好處，找不出一絲多餘的設計。指南 (Guideline) 通常是告訴你該做什麼，不該做什麼。它可以讓你設計出及格的 API，但是沒辦法讓你設計出理想的 API。要達到這個境界 (我也還不夠格) 需要依靠的是對 domain 更精準的掌握...。

雖然如此，不過如果你的服務要處理的 domain 是很明確的，要設計出理想的 API 倒也沒有那麼困難，掌握一些要領就能做到水準之上了。我這篇就是想聊聊這主題，最近工作上常常碰到 API 設計的這個課題，趁我記憶還猶新的時候把它寫下來好了。在服務導向的觀念未成熟的年代，一切都還是以資料庫為中心的設計。那個年代設計軟體的第一步是 ER Model, 或是任何從 DB schema 開始的設計。現在講求服務導向，重點就轉移到服務本身要處理的 domain 了。服務透過各種介面 (interface) 來解決 domain 相關問題, 資訊的傳遞就需要 model, 要從 domain 分析出這些可以系統化的資訊，方法論首推 DDD (Domain Driven Development)。

不過這些方法論，對大部分的團隊來說門檻是高的，我自己嘗嘗試著找出一些平衡的做法，這篇我想介紹的就是我自己愛用的手段: 先從狀態圖的分析開始 (正規的名詞: 有限狀態機, [Finite State Machine](https://zh.wikipedia.org/wiki/%E6%9C%89%E9%99%90%E7%8A%B6%E6%80%81%E6%9C%BA), 以下都簡稱 FSM)。大部分的服務都不是單純的功能，而是都會針對某個主體 (Entity) 來提供相關服務。提供的方式有 API (主動呼叫) 或是 Event / WebHook (回呼), 這些服務的運作也需要有基本的授權管控。我認為 API 的設計，狹義的就是 API 規格了，廣義的是上述這些 (狀態、操作、事件、授權) 整個應該是一體，一致的設計，最後才實作成一個微服務。

這篇我就從 FSM 開始，以 FSM 為主導出整個服務介面設計的過程給大家參考。

<!--more-->

在開始之前，還是要提一下。既然是 "設計" 題，就代表沒有絕對的做法。參考我的方法前，請先判斷一下你的情況是否適合...。如果你的服務，有特定處理的主要實體 (Entity), 而這些實體也有主要的狀態轉移需要控制，並且你的服務並不希望只是提供 CRUD (資料庫的基本操作, Create / Read / Update / Delete)，而是要提供有意義的行為 (Behavior, Method, Operation 等等)，最後是實體的操作也希望能夠有系統地發出事件 (Event, 包含各種形式的 callback, 例如 webhook)。這些前提都符合的話，那可以繼續往下讀看看是否合適。

{% include series-2016-microservice.md %}

# 前言

微服務，溝通的管道，就是要靠 API。但是什麼才是 "理想" 的 API 設計?

我現在的主要角色，是在公司的產品開發團隊擔任架構師，架構的設計我是擺第一位。API 的設計結構一旦複雜，他被使用的方式或順序就會難以預測，一不小心就會被有 "創意" 的人惡意使用，結果就往往會出乎你意料之外 (當然造成的後果跟損失也會意料之外)，然後資安或是漏洞就發生了。最近公司相關專案也在推動 API 的改善，我趁著記憶還清楚的時候紀錄一下我們自己團隊的作法好了。我通常用這幾個層次，來評斷 API 設計的品質:

1. 結構 (state machine, ddd,)
2. 慣例 (resource / rpc style, rest / graphql, grpc...)
3. 流程 (spec, swagger, api docs, ...)

結構，是我最在意的，也是我這篇的主題，這是很抽象層面的設計，跟你使用的語言或是通訊協定沒有太大關係。我挑選的切入點，是從狀態著手，用 FSM 的機制往下展開。你也許會問，如果我連狀態都還分析不出來怎麼辦? 這樣的話代表你對你自身面對的 domain 掌握還不夠清楚，這是沒有捷徑的...。傳統的角度從 data model, 或是前面提到的從 domain 著手 (DDD) 都是個不錯的做法。我從 FSM 當切入點的原因之一，是事前大部分主流的分析方法，不論是哪一套，大都會給你主要的資料 Model 以及狀態的改變定義，這些都是 FSM 的起點。我希望能夠從一個正確的 FSM，就能夠導出整個服務完整的介面設計，包含 API, Event 等等一整套的設計。

在正式開始前，我先舉一個反例:

現今幾乎所有的服務都需要註冊會員才能使用，背後一定會有一組會員相關的資料。每一筆會員資料都有主要的狀態欄位，例如 [停用], [未驗證]... 等等。其中一種設計，就是所謂的 "貧血模型"，你開出來的 API 大概就是透過 HTTP 執行 CRUD, 介面規格遵循 RESTful 的要求, 網址結構對應 resource (table), 對應 http command 的慣例來操作 resource ... 

這種設計方式，能夠應付以資料操作為主的服務類型。但是你很難精準的管控你的服務內容。舉例來說，註冊新會員，你要翻譯成 CRUD 的語言，才能呼叫 API:

> 我要透過 RESTful API 建立一筆會員資料，同時把她的狀態設為 [未驗證]

如果註冊時有額外的機制需要驗證，或是有事件要發出通知其他外部系統，那你的實作就有點難收斂了。你是要在 C(reate) 就發出事件，還是在 C(reate) 跟 U(pdate) 都做一些判斷，確認狀態跟資料內容都對了才發出事件? 會不會一不小心在某些狀況下不會發出事件，某些狀況下發出了兩次? blah blah ...

這些都是貧血模型的缺點，背後的關鍵是你只管 CRUD，你就間皆的把這些邏輯判斷都交給外人了。跟貧血模型對應的，就是所謂的充血模型。

另一種設計方式，就是我不開放 CRUD 這層級的 API，改用分析出來的 "動作" 來開 API。舉例來說，會員 "註冊" 就是個很明確的動作，我會有對應的 register API, 必要的輸入跟輸出，要那些狀態下才能呼叫? 呼叫後的狀態應該變成? 這些實作就會變得很明確，執行 register 成功後發出 registered 的事件也很理所當然，不多不少，就發一次，成功後立即發出，也不需要安排排程來處理。

在這例子內，你就看到幾個關鍵的要素了，狀態 是會員資料的主控資訊，他決定了那些狀態你能做那些事 (能呼叫那些 API), 這能用有系統的方式阻擋不合理的 API 呼叫情境，藉由明確的狀態跟動作定義，你也能清楚的定義相關的事件。你會發現這些關鍵因素都圍繞在狀態周圍，因此你只要弄清楚 FSM，狀態、動作、事件的關係都清楚了，彼此的一致性就高，不會發生狀態跟事件之間互相矛盾等等狀況。設計清楚後，在往下的步驟就都有現成的工具或服務可以接手了，這就可以看各個團隊的喜好自己決定，我會在文章快速帶過不會細說。我只會把重心擺在前面的設計階段。

如果你碰到上面的反例描述的狀況，那就繼續往下看吧! 我就延續同一個主題: 會員機制當例子，來貫穿整篇文章要講的內容。這個案例，就是一般網站會員註冊，驗證，啟用的功能，包含密碼錯誤太多次被鎖定等等流程。我試著列出幾個我期待這 API 要能達成的 user story:

1. 會員本身可以透過網站頁面或是 API, 提供基本的資料, 完成註冊會員的動作。註冊後必須完成 email 的驗證程序，該帳號才能開始正常登入並且使用網站的功能。
1. 網站的登入功能僅限已啟用的帳號使用。以啟用帳號如果連續三次輸入錯誤的帳號密碼，則會被系統自動鎖定。
1. 鎖定的帳號有兩種解除方式，其一是使用忘記密碼功能，透過 email 重設密碼，會員本身使用新密碼就能重新登入系統
1. 另一種解除方式，是聯繫客服，確認核對個人資料後，由客服人員自後台重新設定密碼並且解鎖，會員本身將可用新密碼登入系統
1. 會員本人可以刪除自己的帳號。

看起來是再普通不過的需求了，我就拿這個案例，跑一次我的 API 設計過程，各位可以體會一下如何善用 state machine 來貫穿整個微服務的對外公開介面設計過程。




# 第一步，找出所有的狀態

要從需求到導引出狀態圖，是需要一些過程的。不過這些過程並不困難，許多有經驗的 SA 或是 Engineer 都能很快地給出第一版 (先不論是否完全正確) FSM。我就先從既有的 FSM 開始，即使不一定完全正確。我刻意保留了一些缺失，在後面的步驟里示範怎麼修正。因此若你覺得不對勁，或是想要回報錯誤都非常歡迎，不過請先看完文章在回報 XDD

因為這例子大家都很熟悉了，初次使用新的服務，大都需要你註冊帳號，並且經過基本的驗證後才能啟用，然後你才能真正開始使用這個網站的服務。我就直接先從我的認知，畫出第一版 FSM，並且列出所有可能的狀態清單:

狀態清單:
* (start)
* Registered (已註冊)
* Verified (已驗證)
* Locking (鎖定中)
* Archived (已封存)
* (end)

為什麼我會說這是 "可能" 的狀態? 因為很多人容易把 "狀態" 跟 "屬性" 混在一起。有時候你認為的狀態，其實只要是個屬性，或是個 flag 就足夠了。硬把他當成狀態，等等你會發現往下很難推進，例如啟用或是停用。當它不適合當作狀態時，你會發現每個目前盤點出來的狀態都要 x2, 通通都多了停用跟啟用兩個版本... 然後就失控了 XDD。拿捏好 "絕對必要" 的狀態，這是控制複雜度的第一關。以會員為例，如果這個網站有會員等級制，那請問，等級 (LV1 ~ LV5, VIP, VVIP) 是否該包括在狀態內? 如果需要，上面我列的狀態該怎麼展開? 鎖定中的狀態還要分 LV1鎖定 & LV2 鎖定嗎?

這沒有標準答案，有些情況下 LV 的確應該視為狀態，如果我要處理的核心領域是會員的升降等機制的話這就是對的設計。但是這邊我想處理的核心業務是會員生命週期，因此我判定應該切掉等級這一段。因此決策的主要考量，端看會員等級之間的變化轉移，是不是你的核心業務邏輯。這不是件容易的決定，大家的習慣都是加進去的東西越多越完整越好，但是我在這邊強調，既然是設計題，既然是要抓出主軸，要的是越精簡、越關鍵越好。你需要懂得剔除非關鍵的資訊，剔除他不代表你放棄這些功能，只是你不在這個層級處理它而已。

狀態圖是由一堆 "狀態" (點) 加上狀態 "轉移" (箭頭) 所組成的。之所以稱為 "有限" 狀態機，是因為他必須有明確的起點跟終點，你狀態轉移都會被侷限在這範圍內，不會無限擴張。前面列完狀態，現在接著來列 "轉移" 的動作:

action list:
* 申請帳號
* EMAIL 驗證
* 撤銷帳號
* 輸入錯誤密碼三次
* 忘記密碼 (重設密碼)


綜合上面的狀態與轉移，來看一下第一版的 FSM:

![](/wp-content/images/2022-03-25-microservices15-api-design/2022-03-27-15-34-30.png)



其實，狀態圖畫到這邊，基本上你的服務主軸，跟對應的 API 已經有雛型了。本來我想用 swagger 寫個範例，不過後來想想，我還是回到我最熟悉的 C# 好了。我用 C# 來表達這些介面設計，最後再把這介面對應成 HTTP API 就好。思考階段我喜歡用越直覺越沒負擔的表達方式，直到我腦袋中確認結構後，再用合適的工具與技術，轉為符合工程期待的規格。

知道為何我要把清單跟圖分開放嗎? 因為這些清單都能跟程式碼一一對應。首先先來看狀態，每一筆被建立起來的會員資料 (entity), 都應該明確標示他的狀態。FSM 上面的狀態，我可以用 C# 的 enum 程式碼來對應，如下:

```csharp

    public enum MemberStateEnum : int
    {
        START = 0,
        END = 1,

        REGISTERED,
        VERIFIED,
        LOCKING,
        ARCHIVED
    }

```

再來，我們列出來的 動作 清單呢? 他就應該對應到 會員 能被呼叫的動作 (method), 對應到 C# 的程式碼，應該對應到 MemberService 的 Method. 於是按照上面的設計，我可以寫出這個 abstract class:

```csharp

    public class MemberService
    {
        public MemberStateEnum State { get; private set; } = MemberStateEnum.START;

        public bool Register() { ... }
        public bool ValidateEmail() { ... }
        public bool CheckPassword(string username, string password) { ... }
        public bool ResetPassword() { ... }
        public bool Remove() { ... }
    }


```


我怎麼看待這張狀態圖? 我把它當作一張地圖來看待。每個 class 的 instance, 都會標示該 instance 目前的狀態，也就是該 instance 在這張地圖的所在位置。這些箭頭就像是道路一樣，我在目前位置呼叫了某個 API (選擇走某一個箭頭)，我的狀態就應該按照地圖指示，轉移到下一個狀態。

這裡開始呈現出結構了，反過來想，不符合這張圖的狀態與呼叫，都應該被禁止。你無法在不對的狀態下執行不對的操作，舉例來說，當你帳號還在 (未驗證) 的情況下，你根本不該執行 (忘記密碼) 的動作。你該怎麼擋下這些情況? 當你的狀態越來越複雜的時候，靠 if / else 是列舉不完的，你需要靠更有系統的做法來檢查。狀態圖本身已經足以表達這些資訊了，你需要的是把它對應到程式碼的手段。



# 第二步，FSM 對應到程式碼的結構

接下來，設計的過程暫停一下，我還蠻注重設計與開發能夠緊密搭配的程序的，兩者不能合而為一，就容易變成打高空，弄了一個方法論但是卻難以實作，在這講究快速迭代的時代，不能持續整合的方法很容易淪為理想的。因此，這個步驟我們先來做 FSM 跟程式碼的對應。

FSM 其實很有結構的收整了很全面的資訊，包含前面講的狀態與動作清單。除此之外，我認為更關鍵的是，FSM 把狀態跟動作之間的連動關係表達得很清楚。其中一個重要的資訊是: 在特定的狀態下，你能執行那些動作。這些動作執行完畢後，狀態應該轉移到哪一個新的狀態。很多系統的 BUG 其實都是沒寫好這些邏輯造成的，例如會員已經停用了卻還是可以使用某某功能等等，如果你在設計之初就有正確的 FSM，你的程式碼也都照 FSM 執行，在設計跟實作階段就能夠完全避開這種低階錯誤的。甚至你的技巧高段一點的話，這些設計還能用 AOP ( [Aspect-Oriented Programming](https://zh.wikipedia.org/wiki/%E9%9D%A2%E5%90%91%E5%88%87%E9%9D%A2%E7%9A%84%E7%A8%8B%E5%BA%8F%E8%AE%BE%E8%AE%A1), 又譯作面向方面的程式設計、面向切面的程式設計 ) 的方式實作，你可以在統一管控的層次 (例如 ASP.NET Core 的 Middleware) 就控制好這些流程，不用每一段程式碼都加一堆檢查。


先來看看，FSM 表達的資訊，怎麼換成系統化的檢查邏輯吧。這其實已經有很多現成的套件可以使用，我為了說明方便，我會在範例內自己實作一個簡單的版本，你若認真要使用，可以去找別人的套件來用。我個人推薦 [stateless](https://github.com/dotnet-state-machine/stateless)，封裝得不錯，有興趣的可以用看看。

先來看看檢查的演算法，最普遍的兩種我簡單介紹一下:

1. 查表
1. 轉移清單檢查

這兩種方法，都能很有系統的把狀態圖轉成能執行的程式邏輯。你可以很明確地輸入目前狀態 + 你想要執行的動作，用這演算法幫你確認這動作能否執行。在說明原理前，先想一下你要怎麼運用 state machine? 以前面的案例，不外乎輸入目前的狀態，跟你想要執行的動作，由 state machine 回應給你能不能執行? 另外進階一點的是回報確認要執行了，但是要控制好 racing condition 的狀況。

查表法就是很直覺暴力的，把 (目前狀態) 跟 (所有的動作) 展開成一張大表格，表格裡面填的是執行後的狀態。若 state machine 這張地圖沒告訴你有這條路能走，那麼對應的格子就是 NULL。拿我們現在這個例子，表格應該長這樣:

|state\action	|Register()		|VerifyEmail()	|CheckPassword()	|ResetPassword()	|Remove()	|
|---------------|---------------|---------------|-------------------|-------------------|-----------|
|(START)		|REGISTERED		|				|					|					|			|
|REGISTERED		|				|VERIFIED		|					|					|			|
|VERIFIED		|				|				|*LOCKING			|					|ARCHIVED	|
|LOCKING		|				|				|					|VERIFIED			|			|
|ARCHIVED		|				|				|					|					|			|
|(END)			|				|				|					|					|			|

其中有一格沒那麼明確，我先打星號後面再補充，其他應該沒有太大問題。查表法最明顯的優點就是: 簡單明確，效率又高，實作也很容易。缺點是狀態跟動作多的話，初始化其實有點辛苦，你需要填 N x M 比設定。而實際狀態不見得需要這麼多種組合，有些複雜度會因為表格的放大而被凸顯出來。另外這表格在狀態設計調整時，也不是那麼容易維護，因此有了另一種作法。


第二種就是條列轉移清單。簡單的說你一條一條 (目前狀態) + (動作) => (轉移後狀態) 的列出清單就好。State Machine 照著搜尋，有找到就中，沒有就是為地圖沒這條路。同樣拿我們的案例，由於 action 都很單純，因此圖上幾個箭頭就列幾行...

| init state | action | final state |
|------------|----------|-----------|
|(START)|Register()|REGISTERED|
|REGISTERED|VerifyEmail()|VERIFIED|
|VERIFIED|CheckPassword()|LOCKING|
|VERIFIED|Remove()|ARCHIVED|
|LOCKING|ResetPassword()|VERIFIED|
|????|????|(END)|


這作法好處是 init 的過程更貼近邏輯思考的結構，通常 state machine 都是設計階段就確定的，這些組態大都直接寫在 code 裡面就夠了，不需要特地拉出來放在 config 或是 database。缺點就是當你狀態圖複雜的時候，初始化跟查詢的過程會比第一個方法複雜。你可以是你自己的情況，團隊內部的使用工具來評估使用。雖然各有優缺點，但是都沒有到無法克服的步驟。這些優缺點都可以因為搭配的工具而被改善，其實不需要太在意。

總之，這邊我就定義 StateMachine 的介面就好，不論你用哪一種實作方式，最終使用的介面是相同的。實作大家可以自己研究看看，很簡單不困難的。需要找現成的，可以參考我上面推薦的: [stateless](https://github.com/dotnet-state-machine/stateless) 封裝得不錯，有興趣的可以用看看。



以下是我自己訂的 interface, 後續的 demo 我都以這個 interface 為準。State Machine 只負責查詢 FSM, 並不處理實際狀態改變的邏輯。先來看看 FSM 的定義:

```csharp

    public abstract class StateMachineBase<TEnum>
    {
        public abstract (bool result, TEnum finalState) TryExecute(TEnum currentState, string actionName);
    }

    public class MemberStateMachine : StateMachineBase<MemberStateEnum>
    {
        public override (bool result, MemberStateEnum finalState) TryExecute(MemberStateEnum currentState, string actionName)
        {
            throw new NotImplementedException();
        }
    } 

```

至於狀態實際上該怎麼被改變? 如果你的服務需要考慮到高流量，高併發等等問題，那麼請記好一件事: 狀態的轉移請把它當作 atom operation 來看待

意思是，如果你的某一筆資料目前是狀態 A, 執行兩個不同的 API 分別會讓他的狀態從 A => B, A => C, 那麼你要做好交易的控制，同一瞬間只能有一個 API 能執行成功。

平行處理的文章我寫過很多篇了，不外乎是 (分散式) 鎖定機制運用得當就可以了。所有這些問題關鍵都可以濃縮成一小段 critical section, 判定有沒有搶到 lock 後就能決定該不該繼續執行，這就應該包括在狀態機來控制。只要狀態轉移不被許可。一般沒好好規劃 FSM 的團隊，開出來的 API 很容易在流量大的時候就栽在這個環節。知道為何前面我提 AOP 嗎? 如果你團隊的實作能力已經能用 AOP 來專職處理 FSM 相關限制的話，這題就很簡單了。交給有能力的工程師處理這段，他就能在不影響商業邏輯的狀況下，幫你解決所有 API 的狀態轉移 atom operation 問題。

流程走到這邊，知道為何我那麼強調狀態圖了嗎? 簡單的狀態圖，背後就能代表這些基礎的結構設計了，而且能很精準很一致地轉換成程式碼。我很講求每一個階段的設計跟最終系統或程式碼的對應關係夠不夠直接，越直接越簡單，代表你最終的系統越容易跟你的設計維持一致。無形之間，這就是你系統設計的品質。


綜合上面所討論的，這個 domain service 的實作應該要長這樣才對:

```csharp

    public class MemberService
    {
        public MemberStateEnum State { get; private set; } = MemberStateEnum.START;

        // event(s)
        public delegate void MemberServiceEventHandler(object sender, EventArgs e);

        public event MemberServiceEventHandler OnMemberRegistered;
        public event MemberServiceEventHandler OnMemberEmailVerified;
        public event MemberServiceEventHandler OnMemberLocked;
        public event MemberServiceEventHandler OnMemberArchived;
        public event MemberServiceEventHandler OnMemberActivated;



        public bool Register()
        {
            if (this.TryExecute("Register") == false) return false;
            try
            {
                // TODO: do domain action here.

                this.CompleteExecute();
                this.OnMemberRegistered?.Invoke(this, null);
                return true;
            }
            catch
            {
                this.CancelExecute();
                throw;
            }
        }

		// 其他 Action Method 我都略過，請參考 Register() 即可



        private Mutex _state_mutex = new Mutex();
        private MemberStateEnum _state_from = MemberStateEnum.UNDEFINED;
        private MemberStateEnum _state_to = MemberStateEnum.UNDEFINED;
        private MemberStateMachine _state_machine = new MemberStateMachine();

        private bool TryExecute(string actionName)
        {
            var check = this._state_machine.TryExecute(this.State, actionName);
            if (check.result == false) return false;
            if (this._state_mutex.WaitOne(0) == false) return false;

            // enter mutex
            this._state_from = this.State;
            this._state_to = check.finalState;
            return true;
        }

        private bool CompleteExecute()
        {
            if (this.State != this._state_from) return false;   // optimistic lock

            this.State = this._state_to;

            this._state_from = this._state_to = MemberStateEnum.UNDEFINED;
            this._state_mutex.ReleaseMutex();
            return true;
        }

        private bool CancelExecute()
        {
            this._state_from = this._state_to = MemberStateEnum.UNDEFINED;
            this._state_mutex.ReleaseMutex();
            return true;
        }
    }



```

上面的邏輯，我用一致的 patterns 來處理每個 action 執行前後，狀態改變與事件的發送。狀態改變我用 Mutex 來控制，意思是同一個 member 只要有任何一個會改變狀態的 method 在執行中，就必須透過 Mutex 管控，同時間一個 member 只能有一個這種 action 在執行。做好這個防護之後，就可以用一樣的邏輯來查詢 FSM, 執行完畢後統一更新 State, 並且發送對應的事件。

在這段範例內，其他 method 只要改掉這三個部分:

```csharp
        public bool Register()
        {
            if (this.TryExecute("Register") == false) return false;
            try
            {
                // TODO: do domain action here.

                this.CompleteExecute();
                this.OnMemberRegistered?.Invoke(this, null);
                return true;
            }
            catch
            {
                this.CancelExecute();
                throw;
            }
        }
```

1. 改掉 actionName: "Register"
1. 改掉 // TODO 你自己的執行邏輯
1. 改掉 OnMemberRegistered 觸發事件的部分 (換成你自己定義的事件)
(事件的部分我先偷跑了，如何定義是建請看下一段 XDD)

除了上面三個部分要每個 action 都改一次之外，其他就照抄就好。這邊我為了容易理解，而且不想跟太多 framework 綁在一起，就用比較醜的方式來寫這段 code 了。如果你這段 code 很明確是綁訂在 ASP.NET Core 身上， (1) 其實可以換成在 Method 上面標示 Attrib, 同時 (1) 頭尾控制的邏輯都可以轉移到對應的 Middleware 執行，你的主體只要留下 (2) + (3) 就好了。

經過這樣一路繪製 State Machine, 到很工整的產生這段 code, 其實你的 API 已經有很好的結構了。這些過程熟練後，你就能將抽象畫的層級往上拉一層，以後只要用 State Machine 討論，就能修正好對應的程式碼了。


這段我小結一下:

不要以為每次的設計都能一次到位。現代的軟體開發方法論，都很講求快速驗證，快速修正。你越快能夠評估你的設計是否正確，你就越快能進行改善。前面提到我把狀態圖當作地圖來看待，那麼每一個情境或是使用案例，就應該是地圖上的一段軌跡。試著拿每個案例自己在狀態圖上面走一次，就能很快的驗證初一些低級錯誤。例如有些情境根本在地圖上找不到路，或是有些狀態根本無路可通，那就代表你前面兩個步驟的設計，要嘛缺了一些狀態沒列上去，要嘛過多的狀態都擠在一起；或是某些關鍵的轉移動作沒被你盤出來需要補上等等。

這樣來回幾次，應該就能收斂你的設計了。我在替別的團隊 review API design 時，用這個方法很容易在早期階段，就點出設計上的缺失。因為我是從全貌跟結構下去 review 的，而大部分工程師的 API，則是像寫 code 一樣，我需要什麼就開什麼，覺得太多了再參數化合併；這樣不是不對，只是你很容易有盲點，你的設計只會過度集中在你踩過的範圍。你未知的部分很難有機會被找出來，直到系統上線後用的人多了才...


# 第三步，列出事件清單

前面兩個步驟的分析設計結束後，接著開始來看看事件驅動。終於忍到這步驟了，我先發一點牢騷....

微服務架構，是以特定服務為目的，高度內具實作的一個設計。例如 DB 也自己管理，程式邏輯也自己管理，總之以這案例來說，會員資訊的大小事都歸你自己管就對了。這是很高度內聚的設計，其實也跟 OOP 講的封裝是同一件事。只是 OOPL 的封裝，是在語言層次上面落實的，微服務架構，則是在物理層級上落實封裝的精神。封裝的手段，就是對外只暴露 API，其餘一概不開放。

但是這邊的 API，廣義的說是指透過公開的介面通訊，型態不只是 HTTP REST API 一種啊! API 是被動的呼叫，有些狀況是要主動觸發的，因此會有事件驅動這面向的介面或規範要定義。事件一樣是種概念的宣告，實際上的呈現可能是 webhook callback, 也可能是 message bus 的 publish / subscribtion 等等。在狀態圖上面，我該怎麼呈現 "事件"?

通常，你不大需要特別標示 "事件" 有哪些，狀態改變就發出事件，就已經能滿足大部分的需求了 (因為前面的分析都抓出狀態改變是 domain 的主軸了)。其他外圍有些模糊地帶，例如你重設密碼時，不論狀態改變成功與否，都有些動作或是 callback 想要處理，那就只是單純的 hook 而已，不一定要拉在事件的層級。我把它定義在外圈，先分析完狀態改變相關的事件，之後再補上這些外圍的類事件的定義。有層次對設計而言是好事，你可以很清楚知道你的主軸在哪裡，有哪些設計是依定要環環相扣，嚴謹的檢視，用高標準對待的；有些只是補上附屬規格即可。你不需要放棄這些設計，只要能保有標準的擴充方式就行，一定要處理的是直接跟狀態改變對應的事件定義。

因此，從這狀態圖，我們可以列出會員生命週期有這些事件:
(狀態通常是進行式或是某個靜止的狀態，而事件是過去式，動作則是動詞，命名時可以參考這原則)

event list:
* Member Registered
* Email Verified
* Account Locked
* Account Archived

* Account Activated


這時，我發現我的業務需求，Actived 跟 Verified 是有差別的，不該混為一談。但是狀態上兩者沒有區分，都是 Verified, 這現象刺激了我重新檢視這段的設計是否合理，於是我做了主觀的決定，追加了一個狀態，並且把對應的動作也調整了一次。嚴格的說，Verify 是動作，完成這動作的狀態，最後我決定是 Activated 比較合理，他代表目前會員停留在可正常操作全部功能的狀態中。通過驗證，只是達成這狀態的其中一個路線而已，因此我把 Verified 這狀態修正為 Activated, 而對照的 Locked 則修正為 Deactived.

前面的 sample code 也實作了一個密碼錯誤三次的 method: CheckPasswordFailOverLimit(), 我也把它對應成一個更明確的動作: Lock()
重設密碼 method: ResetPassword() 也是，他應該是個單純的 domain 相關的操作，真正抽出來會影響狀態的那個動作，應該改為 Enable() 更為適合。

所以來看看修正過的 state machine:


![](/wp-content/images/2022-03-25-microservices15-api-design/2022-03-27-00-03-24.png)


我刻意在前面的步驟，示範了錯誤的的分析，而在後面的步驟對 state machine 做出修正的這過程，就是我所謂的快速驗證。所有設計跟驗證的環節，都圍繞著狀態圖，以及狀態圖標示的資訊列出來的清單。在這情況下，你還很容易修正設計，更好的地方在於你修正了狀態，你會連同動作等等環節都一併修正 (否則多一個狀態，可能地圖上的路就斷了)，你很容易能夠顧及全局，不會出現改了狀態結果忘了改行為等等這種蠢事 (如果你在實作階段才改，就很容易這樣)。這些環節是否彼此緊密搭配，才是影響 API 設計品質的最大主因。

如果看到這邊，你開始能體會，那恭喜你妳升級了 :D, 設計階段這些問題沒處理好，你就很容易在這個 domain 碰到用戶端提出 "合理" 的需求，你的 API 卻必須大改才辦的到的場合。這並不是客戶無理，而是你的設計還不夠 "合理" 造成的。設計的品質在這邊有顧好的話，你的 API 才有可能 "穩定"。很多工程師跟我聊的時候會說:

> 如果我們是 google, 那我們講話就夠大聲；那 developer 就會以我們的 API 為標準了，不合用時他們會自己改，不會要求我們改 API ...

不過，事實完全不是這樣啊! 我不會要求 google 亂改他們的 API 來配合我的需求，是因為它們的 API 真的下過功夫，設計是合理的。我做不到的狀況，通常是多想幾回，就能找到合理的作法，因為 google 等等大廠的 API 有這樣的設計品質，它們才能夠用不變的 API 來應付廣大的 developer 各種需求。


最後，這個步驟做完，如何把事件反映到你的程式碼? 這邊我直接用 C# 語言的 event 來對應，你可以自行擴充，延伸到實體物理層級的事件觸發機制，例如 webhook / callback, 或是實際對 message bus 送出 topic ...


```csharp

    public class MemberService
    {
        public MemberStateEnum State { get; private set; } = MemberStateEnum.START;

        // event(s)
        public delegate void MemberServiceEventHandler(object sender, EventArgs e);

        public event MemberServiceEventHandler OnMemberRegistered;
        public event MemberServiceEventHandler OnMemberEmailVerified;
        public event MemberServiceEventHandler OnMemberLocked;
        public event MemberServiceEventHandler OnMemberArchived;
        public event MemberServiceEventHandler OnMemberActivated;

        public bool Register()
        {
            if (this.TryExecute("Register") == false) return false;
            try
            {
                // TODO: do domain action here.

                this.CompleteExecute();
                this.OnMemberRegistered?.Invoke(this, null);
                return true;
            }
            catch
            {
                this.CancelExecute();
                throw;
            }
        }


```


# 第四步，列出角色，並且標示在動作上面

接下來，就是主軸設計的最後一步了。把狀態圖上的動作，都標示上可以執行他的角色。如果換成地圖來思考，你可以想像這條路有誰可以走? 有誰必須被禁止? 這直接影響到你的安全管控機制。

以這個例子來說，角色很單純，就會員本身，或是網站官方的客服人員而已。這段還蠻單純的，標上去就好:

// 圖

同樣的，我用條列方式，標示可執行的角色:

* Register(),		USER
* ValidateEmail(),	USER
* CheckPassword(),	USER
* ResetPassword(),	USER, STAFF
* Remove(),			USER, STAFF


同樣的，標上去之後，前面的案例自己再地圖上跑一次驗證看看。有沒有哪些情境套上角色後是達不到目的地的? 有的話同樣的從整張圖重新檢視一次，看看是狀態少了，還是動作少了? 每個環節都有可能遺漏。修正後直到所有情境你都覺得合理為止。

有聯想到為何要標示可用角色，並且同樣的在 FSM 上面驗證嗎? 用肉眼在 FSM 上驗證能否執行是很容易的，就像在看 google map 一樣照走一次就好。如果標上角色同時也都驗證通過，那代表這設計是合理的。標上角色的方式，其實就跟業界授權管理慣例的 RBAC (Role Based Access Control) 是一樣的啊! 

先來看看 ASP.NET Core 對於 RBAC 的作法: [ASP.NET Core 中以角色為基礎的授權](https://docs.microsoft.com/zh-tw/aspnet/core/security/authorization/roles?view=aspnetcore-6.0)

Microsoft 的做法很漂亮優雅啊，其實當年在 .NET Framework 2.0 的年代，就已經是這樣做了。如果這次的 sample code 是寫成 ASP.NET Core 的 Controller 的話, 那這幾個 method 就只要標記上對應的 AuthorizeAttribute, 就完成宣告授權的任務了。隨後在每個 Request 呼叫時, ASP.NET 都會替你做好授權檢查:

```csharp

    public class MemberService
    {
        public MemberStateEnum State { get; private set; } = MemberStateEnum.START;

		[Authorize(Roles = "USER")]
        public bool Register() { ... }

		[Authorize(Roles = "USER")]
        public bool ValidateEmail() { ... }

		[Authorize(Roles = "USER")]
        public bool CheckPassword(string username, string password) { ... }

		[Authorize(Roles = "USER,STAFF")]
        public bool ResetPassword() { ... }

		[Authorize(Roles = "USER,STAFF")]
        public bool Remove() { ... }
    }


```

很神奇嗎? 其實一點也不，這就是 C# 語言優雅的地方，可以透過 Attribute 標上標記，然後你就有機會在外圍 (例如 Middleware) 用 Reflection 的方式預先做檢查。這其實是很典型的 AOP 作法，讓你可以隔離不同層級的邏輯。Attribute 其實只是負責 "標記"，真正的判斷藏在你看不到的地方。

當然，設計規設計，沒有人限制你這樣的設計一定要用 ASP.NET Core / RBAC 的方式實作。舉例來說，如果 USER / STAFF 會由完全不同的系統呼叫 API, 甚至連網路環境都是隔離的話 (前後台的網路環境實體隔離很常見)，你該做的可能就不是自己寫 code 處理了。你該做的可能是直接分成兩組 API, 有兩組不同的 endpoint, 分開發行。給 USER 的那組只會提供標示 USER 的 API，而給 STAFF 的那組也比照辦理。這些都是按照設計，在實作時自己按照當時情境找出合適的方式執行。

除了用 ASP.NET Core 支援的 RBAC, 或是物理隔離成兩個獨立的 endpoint, 還有其他方法嗎? 有的。第三個我們拿 Azure API Management 來說明。
通常會動用到基礎建設的層級 (例如 Azure API Management 或是 AWS API Gateway 之類的產品)，大概對安全性跟實體隔離都有一定的要求。因此你可以選擇這樣對應:

1. 替每個使用 Member Service 的第三方開發商，建立獨立的定用帳戶 (Subscriptions)
1. 按照 USER / STAFF 分別建立兩個 Products, 並且按照 FSA 上面的標記來設定 Products 發行的 API
1. 按照 Products 給予 Subscriptions 正確的授權

參考連結: [Subscriptions in Azure API Management](https://docs.microsoft.com/en-us/azure/api-management/api-management-subscriptions)


最後一個，講一下認證授權的公開標準: OAuth2
在 API 的世界內，認證跟授權是分得很清楚的。任正式確認你是不是本人，而授權則是我受予權力讓你做哪些事情。授權對於 "人"，就是前面講的 RBAC 的 R (Role), 授權對於第三方，就是用 OAuth2 提到的 Scope. 標準的作法就是，你在後端上的服務，可以替每個 API 或是資源，自己宣告需要的 "Scope", 而 OAuth2 在進行認證時, 一次性地取得目前這個人 (或是系統，組織等等) 被授權使用那些 Scopes, 並且標記關聯在 token 上。在每個 Request 執行時動態的檢查依附在 token 上的 scopes 與該資源宣告需要的 scope 是否有交集。其實名詞換一換，結構上跟我們在 FSA 上標記的 "角色" 都是同樣的授權模型，很容易一對一的對應的。

舉了這幾種例子，我的目的還是一樣，我想把 "設計" 跟 "實作" 清楚的分開。設計的結構對了，你的實作應該都不是問題，甚至你會意外的發現，合理的設計，就能無痛的直接跟業界標準串接再一起。上面的例子就說明了 FSA 的標記方式，完全可以用 ASP.NET Core Authorize / RBAC / Azure API Management Subscriptions / OAuth2 Scopes 等等不同的管理方式對應。

實作的決定權在各位手上，但是不管你決定怎麼實作，設計階段應該要很明確的標示出來才是上策。


# 第五步，補上其他不影響狀態的動作，並且標示角色

設計的步驟走到這邊，其實到第四步應該已經都完成了。第五步是選用的，畢竟前面我一切都用 FSA 為主軸，強迫自己先忘掉跟狀態無關的環節，因為我必須優先抓準最關鍵的部分設計。這過程中，也許有其他不會改變狀態的動作 (actions), 或是非狀態改變的事件 (events, 或是退化的 action - hooks)。這些其實也能用一樣的實作方式發行。我選擇在最後步驟再來考慮它們，是因為我想等主結構都修正收斂好了後才來追加。這樣能最大幅度降低調整設計的困難。

其實這段對於設計來說就沒有太特別的了。你只需要重新檢視，有哪些 actions 需要一起標上來的? 標出 action name, 並且在 FSA 上面標示那些 state 下才能呼叫?

事件的部分也是一樣，追加標示出來即可。

把這些資訊都標記在 FSA 上面有個好處，FSA 是集中設計結構的地方，你可以統一由 FSA 對應到你程式碼的骨架，當作後續開發的 template. FSA 在系統上的實作, 也能藉由 AOP 的方式先幫你檢驗這些 API 呼叫的行為是否符合 FSA 的順序。

配合我這次使用的案例，，我補了下列的動作跟事件。我把完整的清單重新列了一次，加上星號的就是我追加的項目:

action:
* 驗證密碼
* (使用正式會員的功能)

events:
* 驗證密碼完成(成功/失敗)



我也跟著重新修正一次我產出的程式碼:



# 參考

API design 的幾個參考資源:

1. framework design
1. api design patterns
1. resources 為主的 API design guidelines (ex: HTTP RESTful)
1. rpc (remote procedure call) 為主的 API design guidelines (ex: SOAP, gRPC, HTTP API)
1. query 為主的 API design guidelines & patterns (ex: GraphQL, OData)




# 結語

記得當年我第一次開始寫這些比較 思考 設計 面的文章時，當年我寫的這系列，其實我印象很深刻。很多朋友給我的 feedback 是感謝我，說我讓他們想通了，為何他們寫的 code 都會動，也都符合規範，也都通過測試；但是寫起來就是覺得 "怪怪的"，有種是湊答案的感覺。當時我告訴大家的是要搞清楚背後的資料結構與演算法。

時至今日，現在的程式碼，不再只等於 資料結構 + 演算法 了 ( Pascal 大師: code = data structure + algorithm ), 我開始擴大為 service = state + action, 其中 state 就包含了資料結構，action 就是所有相關的程式邏輯與演算法。衍伸出來的是整個服務的設計，包含主動(外界呼叫)，跟被動(回呼)，自動(排程) 的行為介面。工程師依定要掌握十座的技巧，但是如果背後沒有設計的思路輔助，你很容易拿了上等的工具，但是做不出偉大的作品的。我想到在 FB 看到的一句話，不過忘了出處了:

> 我給你一把鑿子了，可是為什麼妳還沒變成米開朗基羅?

你跟大師之間的距離，不是差在那把鑿子啊! 差別在於你對你作品的想法。






