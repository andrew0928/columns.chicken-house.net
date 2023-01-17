---
layout: post
title: "架構師觀點 - API First, 從 Design Workshop"
categories:
- "系列文章: 微服務架構"
tags: ["系列文章", "架構師的修練", "microservices"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: /wp-content/images/2022-10-26-apifirst/slides/slide01.png
---

![](/wp-content/images/2023-01-01-api-design-workshop/slides/slides-01.png)

<!--
API FIRST #2

// 摘要 first, 別寫太長

// OOP concepts in API design

OOP, 封裝, 繼承, 多型
=> 時事題，德國架構師說不要用繼承 blah blah blah

封裝就是設計 API 最重要的事情
封裝是原則，設計概念來自抽象化 (ADT, Abstract Data Type)

抽象化帶來封裝的設計，就需要有介面。介面的實作階層上下關係就是繼承
繼承的目的是帶來多型的操作，多型式期待的對外效果，繼承是提供這效果的內部機制

三件事都是一體的，指示是從不同角度來看。
	=> API

	   封裝

     繼承	多型

=> Impl		=> callback, different service
=> Backward	=> same API
   Capability	=> 相容的服務, API 的規格標準 blah blah
-->

最近這陣子，我對外分享的主題，其實都集中在 "API First" 身上。碰到一些朋友給我的 feedback, 我覺得挺有趣，我挑一個，放在這篇實做篇的最前面:

> Andrew 你談的技巧 (例如: 狀態機, 認證授權, API 開發與測試) 其實我都懂，但是為何你能把這些技巧串再一起? 用這方法來開 API Spec, 我連想都沒想過，而且外面也沒多少人是像你這樣組合起來用的... blah blah (以下省略閒聊的 800 字)

是啊，這老兄講得沒錯啊，這的確是我自己的經驗談。我很擅長的就是只靠幾樣精通的基本功夫，善加利用組合，就能拿來面對許多未知的問題。先前一篇聊職涯發展的文章，我就談到 "知識的連結"，這就是我展現出來的應用。當你每一項技巧都熟練到某種程度以上，你就有自由變化的能力了。能夠達到這種層次的技能不用太多，但是你只要多掌握一個，你能應付的範圍就是別人的好幾倍。我拿來應用在 API First 這主題，就是其中一個案例。

<!--more-->


{% include series-2016-microservice.md %}


# 0. 習慣物件導向的思考方式

先講, 其實我是很討厭一堆方法論的人, 我往往都只用最基本的理論或是技巧, 屬於只練基本功夫那種類型的人。因為我覺得大部分的問題這樣就足以解決了，其他的方法或是工具，就像背公式一樣，只是拿來加速過程的捷徑。因為如此，有好的方法論我當然會用他，但是當我發現他不適用時，我也可以很果斷的放棄他，改用我的基本技能來修正或是補足。

因此，我面對問題時，相對於 DDD 等這些方法論，我更習慣先用物件導向 (OO, Object Oriented) 的角度來思考這問題，該用什麼樣的類別，產生那些物件，然後讓他們交互作運作，來執行這個需求? 當這點我想通之後，我就開始有能力用各種我順手的 OOPL (我自認能掌握的語言只有這幾個: C#, Java, C++) 來做 POC 了。當我能定義出執行這些需求必要的 class, object, interface, 或是 struct 之後，這世界一切就都變得簡單了。API First? 對我來說只是 OOP 裡面提倡的 Interface 優先的思考方式而已 (簡單的講，就是 OOP 三大權杖之一的 "封裝")。

想清楚 interface / class 之後, 我開始能用很工整的對應方式, 開出 API spec 了。舉幾個例子:

```csharp

public class Man
{
    public static Man Create(...) {...}

    public static Man Get(int id) {...}

    public int ID { get; set; }

    public string Name { get; set; }

    public decimal Balance { get; private set; }

    public decimal Work(TimeSpan duration) {...}
}

```

很簡單的例子，只是宣告一個類別，用 Man 這個 class 來表達這個類別能有哪些操作。其中包含了 static method, 包含了 properties, 也包含了 method .. 在把它對應成 API 之前，先別急，示範一下我怎麼 "使用" 這個 class:

```csharp

var m = Man.Create(...);
Console.WriteLine($"Hello {m.Name}(id: {m.ID}), your balance: {m.Balance}.");
m.Work(...);

```

或是:

```csharp

var m = Man.Get(100);
Console.WriteLine($"Hello {m.Name}(id: {m.ID}), your balance: {m.Balance}.");
m.Work(...);

```

只有幾行，代表了我怎麼操作這個 class ... 如果我對應成 REST API, 那麼大概就長得像這樣:


```
// Man.Create()
POST /api/man:create

// Man.Get()
GET  /api/man/{id}

// m.Work()
POST /api/man/{id}:work

```

當你找到對應的邏輯時，就不難理解這對應的規則了。首先，這個 class 包含了兩個 static method ( Create / Get ), 所謂的 static method (或是 C++ 的說法, class method), 就是代表呼叫這 method 時, 你不必知道是對哪一個 instance 呼叫, 你只需要知道是對哪個 class 即可..

所以 Man.Create(...), 直接對應成 /api/man:create 即可。因為你不需要額外的資訊了 (尤其是 id 這層參數)。

至於 Man.Get(id), 他是特別的存在, 在 REST API 的慣例中, /api/man/100 是有特殊意義的, 代表你要取得指定 id 的 instance 回來..
我該怎麼表達 instance? 我很無腦，直接把 Man 的 instance 用 json 序列化之後傳回就好了 (有沒有這麼懶)

第三個, 我想呼叫某個 Man 類別的 instance 的 .Work() 時, 我必須先取得該物件才能呼叫, 對應到 REST API 就長這樣: /api/man/100:work .., 路徑上的 {id} 就代表了我要先取得這個物件, 最後才呼叫他的 method: work.

這邊我用了 google 的慣例, :work 代表 method, 有的人用 /work 也代表一樣的意思, 這沒對錯, 純粹個人喜好而已。我傾向讓 /work 保留給存取名為 work 的 sub-resources.

回到主題，當這些對應很容易做到時，我自然會把最複雜的設計議題，簡化成我最容易思考的 OOP 了。反正 C# 的 class 寫得出來，要對應成 REST API 的規格就沒那麼困難了 (想要功夫一點，甚至你寫出 code gen 也沒問題)。所以核心問題剩下，我如何定義出正確的 class 該長成什麼樣子? 答對了，就是從分析物件的狀態機開始。因為狀態機控制了整個物件的生命週期，改變狀態的通常都是被封裝起來，並且是很重要的 method，於是，我就很習慣拿狀態機當作一切設計的起手式，從狀態機一路把我需要的資訊一一標記上去，並且先在腦袋裡面轉過幾個案例，確認可行後才開始花時間把程式碼跟規格寫出來...。

我在意的資訊不外乎這幾類: 資料屬性、改變狀態的動作、不會改變狀態的動作、事件、允許呼叫的對象。這些都能輕鬆的用 C# class 來標示。寫的出 class, 剩下的就不是問題了。以上，就是我這篇 API Design Workshop 背後主要的思考脈絡。如果你看懂了我的思路，你就會發現這件事其實很容易啊，困難的是你有沒有掌握好 OOP 的基本精神跟設計方式。你也許會問:

> 那如果我 OO 觀念不好的話怎麼辦?

這... 認真說，如果你的 OO 觀念不好，那你應該先補足這個技能啊 XDD, 否則你可能連 C# 都沒辦法很精準的掌握...



前言寫到這裡為止，其實，我在思考 API First 這題目時，我心底壓根沒在想 API 這回事啊 (喂... )，我想的只是 OOP 的基礎設計技巧而已。想通如何用物件與類別來組織你的領域問題時，最困難的問題已經被你解掉了，剩下的都只是翻譯與對應的手工藝而已。

再回來看一次我的思路: 我只是把任何需要被系統化處理的問題，我第一時間都先用 OO 的觀念來思考而已。

當年我真正搞懂 OOP，是大學時代 (當年我入門的 OOPL 是 C++) 看的那本 "[世紀末軟體革命](https://www.ithome.com.tw/article/38577)"，裡面有一句話我到現在還記的:

> 物件導向技術，就是模擬世界，加以處理

就是這句話，打通了我所有物件導向的觀念 (當年第一次接觸 OOP 時我是直接抱著 C++ 的語法來看，完全看不懂..) 整本書看懂這句話就值得了，看懂這句話，也跟著保障了我接下來廿幾年都有飯可以吃 XDD

如果看懂了，就繼續往下吧! 這篇我想延續 API First 這主題，來聊聊怎麼用狀態機定義出合理的 API Spec 的整個過程。上一篇把 API First 的 "WHY" 都交代過了，這篇我主要的用意在於說明 "HOW" 的部分。我看過太多用成熟的開發框架，寫出糟糕設計的 API 案例，因此才會想要分享這個主題。我的核心觀念是: API 就是用系統化的方式，把你的資料或是服務提供出來的標準化做法而已。當然其中包含很多安全，效率，網路通訊等等層次的問題，但是回到業務核心來看，就是用 OOP 把你的業務核心定義出來的過程而已。

我只示範了如何從 C# class definition 對應到 REST API，但是不代表只能這樣用而已。如果你能理解這些語言背後如何描述 "物件" 的話，其實很多通訊協定都能對應出來啊! 不只 REST，你想要對應 GraphQL, gRPC 等等都不是問題。想當年我還刻意用不支援 OO 的語言，硬是實做出繼承等等 OOP 的核心機制 (我是自己實做 [virtual table](https://www.learncpp.com/cpp-tutorial/the-virtual-table/))... 阿北有練過，小朋友不要亂學...

當你對 OOP 熟悉到這種程度時，這些對應的機制就再也難不倒你了。如果你懶得看我落落長的文章，那看到這邊就夠了 XDD, 以上才是我認為本篇文章的精華, 我就先破題, 把重點都擺在前面了。如果你還是對實做的 workshop 過程有興趣，那歡迎繼續往下看 :D





# 1. 正文開始

前面那段 OOP - REST 對應的心得，是我臨時起義加上去的，正式的演講時間有限，沒有篇幅讓我扯這些有的沒的啊! 所以算是支持我部落格文章的朋友們賺到了 XDD, 接下來的內容，我就用我在 .NET Conf Taiwan 2022 的投影片為主來說明吧, 反正都已經是做好現成的素材了。這個場次，是延續我在 DevOpsDays Taipei 2022 的內容，我特別針對 API Spec Design 的部分擴展的內容。內容是連貫的，但是這個場次的內容比較完整，最理想的方式是直接看文章，想要快速瀏覽的，就直接翻投影片。

上一篇講完 "為什麼 (WHY)" 需要 API First, 這篇的重點就轉移到 "如何 (HOW)" 做 API First 了。因為設計的方式不同，API 的規格變成第一順位，流程上就完全不同了。這篇我從這四個面向:

![](/wp-content/images/2023-01-01-api-design-workshop/slides/slides-08.png)

1. 規格優先: 開發流程上的改變
1. 設計方式的改變與標準化
1. 從設計階段就考慮安全性
1. 思考是否過度設計



<!--
![](/wp-content/images/2023-01-01-api-design-workshop/slides/slides-09.png)

流程改了，順序改了 (改成一切先從 API 的規格設計優先)，作法就完全不一樣了。對我而言，開發順序的改變，代表背後的決策順序通通都不同了。
從最明顯的一點來看，規格 (contract) 優先，跟過去的需求 (requiremnt) 優先，差別在哪?

以我自己而言，如果我把需求擺在第一位，我想的一定是 "這個需求我該怎麼實做出來" ? 我心裡會想的是一連串的流程圖、演算法、資料結構等等實做的細節，或是一般通稱的系統設計 (system design) 的細節。我會不自覺地開始思考，那我的 database schema 該怎麼設計... 等等這類問題，然後整個思路就朝向 bottom up 的方向發展了。然而，API (spec) First 的思維，是 top down 從上而下啊，你先思考介面規格後再來想實做 (包含介面之後怎麼實做 API 的方式，也包含介面之前怎麼使用 API 的方式)。

把 contract 擺在第一位思考，就是要你確認 contract 內容都確認無誤了之後再開始開發。其他領域這樣做也是很合理的作法對吧? 你要外包工程，不也是要先把合約簽訂好 (有法律效力) 之後才開始動工不是嗎? 有了合約所有協力廠商才有保障，才能開始投入資源協作。這是效率的起源。

因此，進一步思考，那你需要怎樣才能確認 contract 內容? 記得前面提到的 OOP 對應 REST 的觀念嗎? 物件行為的 contract, 其實就是 interface / class 定義，裡面包含了 data model, 也包含了 object 的行為 ( action ), 分析 domain 的 action + model 才是第一步。第一步沒有想清楚，你就先跨入 database schema + function 的話，你就走偏了。

回到 OOP 的觀念來看，先訂 contract / interface, 另一個角度來看，就是封裝 (encapsulation)。定義 contract, 就是約定了 API 應該履行的 input / output, request / response, parameters / result 啊，至於背後是怎麼做到的就不重要了，這就是封裝要表達的精神，也是 OOP 的三大支柱之一。從 interface 隱藏背後的實做細節，稱為封裝；換個角度來看，我想要把我面對的 domain 行為抽象化，只定義出我想表達的重點行為，而忽略掉實做的細節，這角度看來 "封裝" 其實就是 "抽象化" 的實踐。

唯有適度的封裝，在設計上強迫阻斷不必要的資訊洩漏 (例如 private fields, 單純內部使用的資訊不應該外露)，阻斷不必要的溝通管道 (例如不應該公開資料庫存取權限給外部系統，透過 API 是唯一取得資料的途徑)，是降低系統耦合度的不二法門。

-->

原本演講的內容，我還是不免俗套的講了一堆前言，這邊就跳過了。我就拿這個案例來破題吧! 我截了一個畫面，各位可以思考一下背後隱含的問題與思考的要點:

![](/wp-content/images/2023-01-01-api-design-workshop/slides/slides-10.png)

這種授權確認的畫面，我想大家都不陌生吧! 當你選擇用 Google Account 登入其他平台的服務時，會跳出這確認畫面。

有些人對於資訊安全是敏感的，資訊安全除了技術上的考量之外 (有沒有加密，有沒有遮罩等等)，另一部分也是你對開發者的信任 (這公司取得了我的個資會拿去幹嘛)。這畫面上的內容，代表徵求授權的廠商 (XiaoMi) 想要取得你放在 Google 上面的個人資訊 (包含上面標註的欄位內容)，而 Google 接到這請求，要回應 access token 給小米之前，必須先取得你的確認。當你按下 [繼續] 之後，Google 就會提供 access token 給小米。小米拿到 access token 就能夠取得你的授權資訊 (按照畫面，包含: 姓名, email, 語言偏好設定, 個人資料相片)。那麼... 在你按下 [繼續] 之前，我試問這幾個問題:

1. 你是否相信個資擺在 Google 是安全的?
1. 你是否願意把 Google 的個資透過系統轉移給 XiaoMi 使用?
1. Google 傳輸的方式你放心嗎? Google 的 API 是否真的能精準控制，給 XiaoMi 的 access token 就只能剛剛好存取你同意的範圍? 如果授權畫面複雜一點 (有的情況下你可以自己勾選要授權那些欄位)，Google API 是否也能如實的控制?
1. 當你反悔後，Google 是否真的能精準控制，不再讓 XiaoMi 繼續使用你的個資?
1. 當你反悔後，XiaoMi 是否真的會刪除先前已取得的個資?

我會有這些疑問，不是我在找碴啊，而是這些一切的行為跟資訊的流動，在我按下按鈕之後完全都看不到啊，也無法驗證，也就是我一切都只能建立在我對 Google / 小米 的信任了。我必須信任 Google 的 API 真的如設計般的安全，我必須信任小米真的如宣告般的妥善使用我的個資，足夠信任了我才放心按下 [繼續] ...

最後，我換個角度，如果 API 不是 Google 開發的，而是你開發的，你該如何設計，你才有信心對你的使用者作出一樣的保證?

回頭看看我自己試問的幾個問題，真正跟 API 有關的，就是 (3) 這點，也是這篇的主題，API 的設計。資安有分很多層面，有些是基礎建設管理問題 (例如主機是否有被入侵的可能)，但是有些單純是設計問題，這裡的 API 安全就屬於這種，你的 API 是否在設計階段就考慮好安全性?

舉個類似的案例，很多社群常常都會討論，哪些網站會儲存你的密碼 "明碼"，這類網站都會被視為不夠安全的網站。不夠安全，不是代表他一定會洩漏你的密碼，而是他的設計，密碼是有機會被還原的，因此就存在一定的風險。如果設計上你就只儲存密碼的 Hash (也許 Hash 計算之前還有加上 Salt)，至少你的設計上就已經避免了絕大部分可能的密碼洩漏風險。這就是從設計或是架構上就考慮安全性的例子。

API 也是，如果你想要讓其他的開發者，或是使用者相信你的設計是安全的，也有類似這樣的基本要素必須顧好，這是我後面想談的主題之一。除了安全問題，該如何組織整組 API 的設計結構，也是我想談論的重點，會需要用到前面提到的 OOP 設計思考的範圍。API 困難的地方不再於你把 code 寫出來，而是你不見得能預期別人要拿你的 API 做甚麼事情，或是別人會用甚麼順序 & 組合來呼叫你的 API，也因此你很難從 "精確" 的需求來推導 API 設計；你必須對於你要開放的服務領域 (後面通稱 domain) 有一定的掌握，直接思考這些 domain service / data 如果要開放，你需要提供什麼操作行為，從這角度來設計 API spec 才會到位。

這些，不就都回到前面談的 OOP 了嗎? 你有那些 object? 你該如何開出 class / interface 的介面? 你該封裝那些運作的細節? 你該開放那些細節別人才能使用? 最有效的方式，就是世紀末軟體革命那本書講的那句話:

> 模擬世界；加以處理

只要你模擬的夠到位，現實世界運作的原則不大會改變，但是客戶的需求會改變。如果你對齊的是世界運作的原則，而不是只對準需求，那麼你的 API 就有某種適應能力，能適應未知的需求變化 (因為需求也是圍繞著世界運作的原則)。掌握這點非常重要，因為你開發的是 API，SDK，或是核心元件等等類型 (需要被高度重複使用)，這種適應能力就特別重要。這點做到位，你才能確保你的 API 規格能夠適用各種情境，而不是換一個客戶就要改一次 API ... (你看過哪個 "好" 的 API 是這樣做的)。

也因此，我才會從一開始就強調 OOP 的重要，而接下來的整個推演的方法，只是先做好 OO 的設計，再對應成 REST API 規格的步驟而已。

如果你看懂了，那就繼續往下吧! 還沒體會的可以先停在這邊，多看幾次仔細思考消化一下。如果你有心好好掌握 API 設計的技巧的話，花時間想通這脈絡是絕對有幫助的。




# 2. 開發流程上的改變

![](/wp-content/images/2023-01-01-api-design-workshop/slides/slides-11.png)

大部分的人，都是從 "Hello World" 開始學寫 code 的... 每個人都是先讓 code 會動，才開始學怎麼把重複的程式碼封裝成 function 等等的步驟開始學程式語言的。也因此，要學習先忘掉實做，先訂介面在寫程式，對所有 developer 都是需要適應的過程的。API 先從 "規格" 開始定義，勢必也會需要改變一些你習慣的流程。這段就是要來聊聊 API First 背後的 Contract First, 在開發流程上帶來哪些改變。

我拿 Ruddy 老師，在他的部落格上有一篇文章，就是在講 Contract First, 我拿這頁當案例來說明:

![](/wp-content/images/2023-01-01-api-design-workshop/slides/slides-12.png)

左半部是一般的做法，標上 1,2,3 是順序。如我這段一開始講的，最直覺的開發方式是:

1. 先寫 code, 讓他會動, 功能正常
1. 接著開始重構, 拆出 function, 拆出 API, 補上 WebAPI Controller 之類的 code 讓外部能透過 HttpClient 使用你的 API
1. 接著再開發要使用你 API 的 Client Side Code, 可能是直接開發 Client, 或是有的團隊功夫一點會先開發 SDK ..

這是典型的作法，並沒有一個通用的名字來代表這方法，我就自己取 "Implement First" 來代表好了..


而右半部，說明的就是 API-First 的模式，或是用我更習慣的用語: Contract First, 你先訂好 "合約"，並且花一點時間確定合約能夠運作，把合約定案下來後，前後端再按照合約，各自進行 Client / Server 兩端的開發，最後再合併一起進行整合測試的過程，就是所謂的 Contract First.

一樣，右半部標記的是執行順序，有些不同:

1. 先定義 API Spec, 同時用最少的資源來準備 Mock, 讓這個 API 是真的能被呼叫使用的 (可能傳回值是假的，只是看起來能按照規格動作而已)
2. 完成 Contract & 能動的 Mock, 前後端就能同時行動了，因此都包含在 (2) 這項。後端開始按照 Contract 來實做 database / service, 前端可以按照 Contract 來開發 SDK / Client








<!--


# 2, API 的開發策略

![](/wp-content/images/2022-10-26-apifirst/slides/slide26.png)

![](/wp-content/images/2022-10-26-apifirst/slides/slide27.png)

## 2.1, 開發流程的改變

![](/wp-content/images/2022-10-26-apifirst/slides/slide28.png)

## 2.2, 設計方式的改變 & 標準化

![](/wp-content/images/2022-10-26-apifirst/slides/slide34.png)

## 2.3, 從設計階段就考慮安全性

![](/wp-content/images/2022-10-26-apifirst/slides/slide42.png)

## 2.4, 思考是否過度設計

![](/wp-content/images/2022-10-26-apifirst/slides/slide48.png)


# 3, 那些我經歷過 API 相關的故事

# 4, 總結 & 寫在最後..

![](/wp-content/images/2022-10-26-apifirst/slides/slide52.png)












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

https://netflixtechblog.com/timestone-netflixs-high-throughput-low-latency-priority-queueing-system-with-built-in-support-1abf249ba95f

-->