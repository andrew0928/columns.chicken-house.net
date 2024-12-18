---
layout: post
title: "[架構師觀點] LLM 的抽象化介面設計"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---

先說，這篇單純是我的抽象化思考練習，搭配一點 C# 的 code 來驗證想法而已。雖然提到 LLM，但是內容跟 AI 沒啥關聯......

會寫這篇，是我看了幾個不同平台提供的 LLM API / SDK 介面設計，發現各有巧妙...。回想兩年前開始在看 LLM 相關的 API 時，最後是把 LLM 想像成 "真人" 提供回答問題的服務 API，才開始想通整個 API 的設計脈絡。而其中又以 OpenAI 的 Assistant API 的設計我覺得最貼切。看到這裡，就開始想...

> 如果是我來定 LLM 的介面，我也會這樣開嗎? 如果不是，我會怎麼設計?

於是，就有了這篇。

<!--more-->

之前在 Build School 現場分享過這個主題: [架構師的修練] #1, 刻意練習 - 打好基礎, 也有把這內容寫成文章，都提到同樣的觀點。架構師最主要的任務就是精確地運用各種成熟的元件，而 "精確" 卻是件很困難的事情，你必須從這些元件 "為什麼" 這樣設計著手，你才能用的到位。掌握這些的捷徑，就是透過 "抽象化" 的思考。

所以，這篇，就是我自己在練習思考這題目的紀錄，重點是 "抽象化介面設計" 喔。如果有看懂，相信你未來再使用這些 API / SDK，能理解背後的設計脈絡，你應用起來就會更得心應手。

<!-- more -->

<!-- 
這篇是我個人的思考練習，我藉由自己 "嘗試" 制定 LLM 的介面設計的過程，到做出 POC 為止，試著自己發明輪子，不過我不打算把我發明的成果用在我的專案上 (用別人定義好的介面就可以了，不要自己開發)。自己做一次的目的是你會踩過主要的障礙，當你有了自己的一套做法後，可以跟成熟的方案做對比；跟別人做的一樣，你會知道你走對路了，而且你已經有走這條路的經驗值。跟別人做的不一樣，你也會知道你掉入陷阱了，你會有機會思考中間的落差，也有自己的 POC 當作基礎來調整 (你的 POC 你最熟悉，調整的進入門檻最低)，你會得到錯誤嘗試的經驗值，而最終你也會得到走對路的經驗。更有價值的是，你會有很高的機率，發現原來有更好的做法，而外界的解決方案還沒採用，很可能是這還未完成，往後的 release 才會提供。當你走到這一步，恭喜你，你的架構設計經驗其實已經追上領先者了。

這篇，就是我針對 LLM 的介面 (API, 或是 Framework) 的設計嘗試。如果你預期我會說明技術規格，或是看完了你就會用 XXX API，那你就錯了，我不會講那些東西。看完你會學到我思考問題的方法，你掌握了這技巧你會有機會提升自己的設計能力，並且用抽象化思考的方式解決未知問題。這在你要開發自己的 Framework 或是要建立大規模服務的 API 設計規格時是很重要的能力，抽象化沒做好，你會做出功能都能動，但是範圍一大就發現彼此之間的設計與主要結構都沒有一致性。 -->



# 寫在前面, "工人智慧" 的介面設計

再談 "人工智慧" 之前，先來聊聊 "工人智慧" 吧! 這對 LLM 的抽象思考很重要，原因後面說..

我在看 LLM 服務的時候，我都是想像 API 的背後，是個 "真人"。因為我認為他是真人，所以我會自然地用對話 ( Prompt ) 跟他溝通。在大約 2010 年代，網路、雲端計算、行動裝置都開始成熟了，Uber 這種大規模的 "媒合" 體系開始出現了。你想叫車，透過 APP 跟 Uber 演算法﹑把全世界想要叫車的乘客，跟全世界的出租車配在一起，顛覆了過去的計程車營運模式 (司機在路上亂逛，靠機率來攬客)。

於是，越來越多不同領域，也模仿了這樣的模式... 各種接案的網站也風行了，最典型的就是外送，有的需求更蝦，透過外送平台來找人手幫忙處理雜事...。在那個年代，有出現過幾個 "聊天機器人"，號稱是人工智慧，結果聊一聊被教壞了就下線了，或是被爆出來這些所謂的 "人工智慧"，其實背後是躲著一群真人，所謂的 "工人智慧" ...。

我講這個幹嘛? 在我看來，聊天機器人是 "人工智慧" 的抽象介面，使用者透過他來跟背後的 "人工智慧服務" 溝通。而實際上背後的 "工人智慧"，某種程度也能透過同樣的介面提供服務，只不過介面的實作是 "工人"，不是 "神經網路" ...

所以，我開始無聊了，如果我要 POC 這樣的結構，邊界跟介面該怎麼設計? 這就是我這篇的練習。


// demo 1, chat completion

// demo 2, switch with multiple worker & chat client

// demo 3, real world in 2010 - uber worker with gRPC client

// demo 3-1, switch worker, must keep and transfer instructions and histories to new workers. (stateless in worker side)

// demo 4, real world in 2024 - ollama

// demo 5, token billing

// demo 6, turing test

// compare gRPC api spec with openai chat completion api / assistant api



# 開始 coding ...



interface IChatBot
{
	string Ask(string question);
}


interface IChatBot
{
	IEnumerable<string> Ask(string question);
}


看來，這介面設計，足夠開發出前端的聊天介面了:


var chatbot = null;

bool stop = false;
do
{
	var line = Console.ReadLine();
	foreach(var answer in chatbot.Ask(line))
	{
		Console.WriteLine(answer);
		if (Console.ReadKey() == true) break;
	}
} while(!stop);


後端呢? 開始來設計 Uber Like 的服務吧! 我想要找廉價的人力，躲在背後充當工人智慧... 只要前面有人問問題，就會自動媒合一個沒事做的工人 ( Worker )，就由這個真人來負責回答問題... 如果前面沒繼續聊，那這個工人可以繼續去跟下一個人聊天，聊越多賺越多 (某種程度這也算是 token 的費用吧 XDD)


// worker design


這邊 Uber 的角色負責 dispatch, 我就簡單做就好了。就叫他 "接線生" (operator) 好了

// IOperator

接線生操作的是交換器，一樣訂個介面 ISwitch 

// ISwitch



看看設計，我用 class diagram 來看，還蠻有個樣子的:


// class diagram


# 第一版實作

















# 2024/08/02, LLM 抽象化

這篇的目的，起源自我一直在想 AI (主要是 LLM) 如果要大規模的放進應用程式的架構內，那我應該用什麼介面 (interface) 來操作他? 因為定義良好的介面，是軟體 (尤其是程式碼) 架構設計的基礎，所有軟體工程都是從這邊發展出來的。物件導向也是，各種測試框架與流程也是，依賴注入、依賴管理的結構也是...

然而，我在參考各大廠的規格時，發現大家做的都不大一樣，Open AI 有 Chat Completion, 後來換成 Assistant API, 然後很快就有 v2 ...; 開發框架這邊有 Microsoft Semantic Kernel, 其他開源的框架也有 LangChain 等，而能在本機跑 LLM 的 runtime 介面也多樣化，LM Studio 有 Open AI 相容介面 ( Chat Completion ), 而 Ollama 也有自己的 API, 而前陣子看完 Microsoft Build 大力推廣的 Copilot+ PC 架構, 裡面的 Windows Compilot Runtime 就用了 OnnxRuntime, 也有它自己的介面...

我知道這些規格終究會統一的，不過我不想等到那個時候才開始了解 AI 在幹嘛...，我想要先搞清楚這些介面是單純規格有各自衍生版本而已，還是在不同規格後面還有不同的意圖，或是要描述 LLM 不同的應用領域? 前者很容易有 mapping 就能轉換，後者則是模式的不同，一開始就要挑對。

於是，我覺得這主題夠重要，值得我花點時間 (就真的一點點而已，幾個晚上的讀書時間) 來想清楚。我拿出過去我對付這種設計議題的常用做法: 自己重新發明一次輪子。發明過一次後，你會想通背後的細節，並且確保他是能執行的 (POC 會動)。如同前面所說，完成後若能跟大廠設計對應，那你做對了 (同時你也能理解大廠背後的想法了)，如果跟大廠的不同，你可以進一步思考改進，你會從 POC 修正中學到經驗 (成本比大廠低太多)，或是發現更好的做法 (你已經跨入領先的族群了)

這方法我自己默默執行了 2x 年了，有兩個好處，受用無窮:

1. 你有能力自己推導出同等於大廠規格的能力:  
因為你已經自己摸索過一次。你會有能力正確且精準的使用大廠的 solution 解題 (你不會拿槌子去釘螺絲釘)
2. 你有能力設計自己的 Framework:  
世界級大廠設計服務的能力，其中最難訓練的各種 framework, class library, SDK 等等的設計技巧就屬於這種。這能力對於你開發大型系統有絕對的優勢，因為你會很清楚知道怎麼梳理大量雜亂且複雜的程式碼..

我這樣嘗試過的題目不少，列舉幾個:

1. (DOS 年代) Turbo C 那種文字模式的視窗介面  
當年其實我自己寫了很鳥的版本 (學生時代，技巧還不純熟)，後來看了世紀末軟體革命附的 windows 視窗 class library, 就是用這種自己重新發明輪子的角度去寫的，是個很好的學習對象
1. Stack Machine ( 以 stack 為基礎的 CPU 設計, 不同於現在 x86 以暫存器為主的設計)   
當年跑去修資工系課程的作業，CPU 指令不複雜，但是該有的結構都有了。作業內容是自己用 C 開發能順利執行該 CPU 組合語言 (指令) 的模擬器，後來出來工作後才發現 JVM / .NET CLR 都是這種結構，某次面試的上機考也有這題 (結果當然輕鬆過關)
2. 各種 ORM 的設計技巧  
我自己開發過 XML -> RDBMS 的 ORM, 也開發過典型的 Object -> RDBMS 的 ORM, 有這些經驗我也開始搞懂複雜的物件導向特性該怎麼對應到 RDBMS 的技巧 (封裝、繼承、多型等等)，而出社會後面對過 XML Database, 或是現在的 NoSQL ( Json Database ), 背後都是同樣的理念。有這些經驗，我看過 NoSQL DB 的 API 後，就能理解背後再做什麼了，我也能比其他人更清楚的知道應用程式該如何 "合理" 的使用 NoSQL，用法跟 RDBMS 有何不同? 為何會有這些差異等等的基本知識
4. Thread Pool 的設計技巧  
起源來自我剛出社會時某個工作，有個很厲害的資深前輩 (同為交大學生，前輩也才大我一屆而已，怎麼實力贏我這麼多...) 教我們用 100 行的 code 就實做出功能完整的 thread pool, 我花了幾周自己做一次, 搞懂後所有的平行處理問題，時序問題 (衍伸到後來微服務，Message Queue 等等需要精確思考平行處理時序問題)，未來這些領域的問題都難不倒我了。各位可以看我的架構面試題，大多是處理這類難題的。
5. 工作排程，排隊，限流，管線 ( pipeline ) 等等的處理技巧  
同上，是平行處理技巧的延伸，這些知識都來自於 thread 的控制技巧訓練。我從來沒有在工作上真的用自己開發的 ThreadPool, 但是這經驗讓我解決了不少難題。
6. 權限控制 (RBAC, PBAC, ABAC, ACL…)  
略，接下來有機會我想聊聊這主題。這也是過去自己發明過輪子才有的經驗，我嘗試在資料庫中用這些授權管理模型，來管控資料庫內每一筆資料的權限，並且把查詢與處理的 Class Library 控制在合理有效率的範圍內。我覺得在 NoSQL / VectorDB 越來越重要的年代這會是個重要的能力


這是過去幾個月，我都在思考的題目；趁著我記憶猶新，就寫了這篇來記錄一下。我在想的是 LLM 如何應用在我的服務內，因此抓出 LLM 要扮演的角色，替他定義合適的介面，就是我想的第一個題目。我拿來對照的大廠設計 (對照組)，是 Open AI 的 Assistant API …。過程撞了不少牆，我就把最後順利通關的過程寫下來吧。


# 1. 定義: 圖靈測試, 如果我真的要寫成圖靈測試 APP, 那 interface 會長啥樣?

IIntelligence

```jsx
interface IIntelligence
{
		string Ask(string question);
}
```

- ArtfactIntelligence : IIntelligence
- HumanIntelligence : IIntelligence

對話很複雜，有前後文.. 所以引入 SessionState

```jsx
public class SessionState
{
	public IEnumerable<string> GetHistory() { ... }
}

interface IIntelligence
{
	string Ask(string question, SessionState session);
}
```

如果圖靈測試 APP 要 scale out … 就要有 SessionState 的管理機制 ( Factory, Dispatch / LB / Proxy / Router … )

```jsx
//
```

所以，Uber 時代，用平台化的規模，把全世界的 "人力” 高效率的分配:

```jsx
// dispatch session to Human(s)
```

而 AI 時代，不用那麼麻煩… ( APIKEY / Token 的錢花下去就對了 )

```jsx
//
```

除了聊天，要有做事能力 ( Tool Use ), SessionState 應該包含可用的 Tools

```jsx
SessionState:
- Dictionary<string, Func> Tools

Ask 從 return string, 換成 return IEnumerable< string | ToolUsage >
```
























—

(小節)

如果，你追 OpenAI 的新技術，看到 Assistant API 的規格就拿來啃，你會很熟練這應該沒問題，你會使用他應該也沒問題，但是你可能無法非常靈活的運用他 (太新，你找不到太多洗鍊的應用案例，大多是 How to 這種快速的)。這樣的學習方式就像拿著字典學英文.. 

我花了點時間 (其實也只有幾個晚上而已) 想通這些，再來看他的 API 規格，因為背後道理都懂了，茶規格就很理所當然，解決了我 "背" 不起來那麼多 API 的困擾，但是脈絡我都掌握了，我只需要看規格確認語法。這就像我已經會講英文，也熟悉外國的文化，只是需要時還是要查一下字典確認拼字…

哪種效果好? (我英文很破，拿這當例子真是心虛) 當然是後者啊，講白了就是死讀書跟活用的差別

從此之後，你面對你熟悉的 "主題"，你也是這領域的專家了 (因為你已經經歷過從無到有的 "創業" 過程，只是你的規模很小而以)。因為你有這經驗，你完全可以理解這領域 "應該" 做什麼，"應該” 怎麼做…

所以，面對版本更新，你的態度會是:

> 太棒了，我想了很久的功能終於出來了
> 

> 我一直覺地這裡應該要有個 XXX 才對，現在 v5 OOO 團隊終於實現了，我自己捕的功能終於可以換成官方版本
> 

而不會是:

> 又有新功能? 不要再改了，我城市要重翻一輪 (因為你的脈絡跟人家不一樣)
> 

> 這新功能幹嘛用的? 我原本的用法用得好好地現在不能動了 (因為你的用法不是人家的設計用法)
> 

所謂 "架構設計" 其實就是這麼回事，很多人覺得我怎麼都 "猜" 的道以後會有甚麼，可以提前做好準備?其實說穿了不值錢，就相關主題我做過這樣的練習而已，習慣成自然之後，自己領域的問題我也開始有能力這樣思考罷了

這些能力到某個程度就會 "湧現”，外人會覺得很神奇，因為你開始可以 "猜" 的很準了，例如:

> 照這想法，OOO 應該也會有 XXX 的設計才對。我翻翻文件看看是不是真的有這東西?
> 

你的猜測，翻完文件後高機率還真的會有，或是會寫這版還不提供，下一版會有… 你已經不知不覺有了精準的預測能力。

這樣的預測能力，當你用在你的專案，預先留好別人三個版本後才會 release 的設計空間，等到新版本出來，人家都還在摸索研究，你只要把某個 method 的實作換掉就搞定… 不但無痛升級，而且完全善用新版的能力

在別人眼裡，這就是厲害的設計了 (不過其實完全不是這麼回事啊，我只是賭對了而已 XDD)。雖說是賭對了，但是專業的賭徒就是讓機率站在你這邊不是嗎?

—