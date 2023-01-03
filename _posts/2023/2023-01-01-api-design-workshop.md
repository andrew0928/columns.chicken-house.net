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



# 寫在前面: 習慣物件導向的思考方式

我面對問題時，我很習慣先用 OO 的角度來思考這問題，該用什麼樣的類別，產生那些物件，然後讓他們交互作運作，來執行這個需求? 當這點我想通之後，我就開始有能力用各種我順手的 OOPL (我自認能掌握的語言只有這幾個: C#, Java, C++) 來做 POC 了。當我能定義出執行這些需求必要的 class, object, interface, 或是 struct 之後，這世界一切就都變得簡單了。API First? 對我來說只是 OOP 裡面提倡的 Interface 優先的思考方式而已 (簡單的講，就是 OOP 三大權杖之一的 "封裝")。

想清楚 interface / class 之後, 我開始能用很工整的對應方式, 開出 API spec 了。舉幾個例子:

```csharp

public class Man
{
    public static Man Create(...) {...}

    public int ID { get; set; }

    public string Name { get; set; }

    public decimal Balance { get; private set; }

    public decimal Work(TimeSpan duration) {...}
}

```

很簡單的例子，只是宣告一個類別，用 Man 這個 class 來表達這個類別能有哪些操作。其中包含了 static method, 包含了 properties, 也包含了 method .. 要對應成 API (我都用 RESTful 為主)，其實就是一對一的對應而已:

```

// 對應: static method
POST /api/users:create

// 對應: get instance
GET  /api/users/{id}

// 對應: 呼叫 work() method
POST /api/users/{id}:work

```

很工整的對應，static method 就是 /api/users:{static method}, 而 instance method 則加上 {id} 代表你這操作是綁定在某個 instance 身上.., GET 則是取出某個已經被建立好的 instance, 就用 json 傳回序列化過的物件即可..

當這些對應很容易做到時，我自然會把最複雜的設計議題，簡化成我最容易思考的 OOP 了。那麼我平常都怎麼分析該有哪些物件哪些類別的? 答對了，就是狀態機。因為狀態機控制了整個物件的生命週期，改變狀態的通常都是被封裝起來，並且是很重要的 method，於是，我就很習慣拿狀態機當作一切設計的起手式，從狀態機一路把我需要的資訊一一標記上去，並且先在腦袋裡面轉過幾個案例，確認可行後才開始花時間把程式碼跟規格寫出來...。

以上，就是我這篇 API Design Workshop 背後主要的思考脈絡。如果你看懂了我的思路，你就會發現這件事其實很容易啊，困難的是你有沒有掌握好 OOP 的基本精神跟設計方式。你也許會問:

> 那如果我 OO 觀念不好的話怎麼辦?

這... 認真說，如果你的 OO 觀念不好，那你應該先補足這個技能啊 XDD, 否則你可能連 C# 都沒辦法很精準的掌握...


前言寫到這裡，你大概明白我的想法了嗎? 其實，我在思考 API First 這題目時，我心底壓根沒在想 API 這回事啊 (喂... )，我想的只是 OOP 的基礎設計技巧而已。想通如何用物件與類別來組織你的領域問題時，最困難的問題已經被你解掉了，剩下的都只是翻譯與對應的手工藝而已。

再回來看一次我的思路: 我只是把任何需要被系統化處理的問題，我第一時間都先用 OO 的觀念來思考而已。

當年我真正搞懂 OOP，是大學時代 (當年我入門的 OOPL 是 C++) 看的那本 "世紀末軟體革命"，裡面有一句話我到現在還記的:

> 物件導向技術，就是模擬世界，加以處理

就是這句話，打通了我所有物件導向的觀念 (當年第一次接觸 OOP 時我是直接抱著 C++ 的語法來看，完全看不懂..) 整本書看懂這句話就值得了，看懂這句話，也跟著保障了我接下來廿幾年都有飯可以吃 XDD

如果看懂了，就繼續往下吧! 這篇我想延續 API First 這主題，來聊聊怎麼用狀態機定義出合理的 API Spec 的整個過程。上一篇把 API First 的 "WHY" 都交代過了，這篇我主要的用意在於說明 "HOW" 的部分。我看過太多用成熟的開發框架，寫出糟糕設計的 API 案例，因此才會想要分享這個主題。我的核心觀念是: API 就是用系統化的方式，把你的資料或是服務提供出來的標準化做法而已。當然其中包含很多安全，效率，網路通訊等等層次的問題，但是回到業務核心來看，就是用 OOP 把你的業務核心定義出來的過程而已。

我只拿我最熟悉的 C# / RESTful API 來當例子，但是不代表這方法只能這樣使用。你可以用同樣的方式，來定義不同風格或是通訊協定的 API Spec, 例如 GraphQL, gRPC 等等都可以。當年我幹過蠢事，就是刻意用非 OOPL 來寫 OOP，硬是把類別繼承 (我用 virtual table) 的機制實做出來, 也把 class method / instance method 實做出來。原來所謂的 this 指標就是這麼一回事, 每個 instance method 只要第一個參數隱含著一定要帶著 this 就可以了啊..

如果你想測試自己對 OO 有多了解，試著想看看只用 function + struct, 如果你還能很精準的實做出 OOP 的幾種重要機制 (封裝、繼承、多型；靜態類別、事件驅動、介面、多載...)，那我相信這些題目都難不倒你了。這不是我這篇想聊的啊，不過你有興趣的話歡迎在底下留言討論。

當你對 OOP 熟悉到這種程度，甚至可以熟練的用非 OOPL 也能寫出 OO 的 code 時候，這些對應的機制就再也難不倒你了。我上面不就示範了怎麼把物件對應成 REST API 規格了嗎? routing 內的 {id} 其實就是代表某個 instance 的指標啊 (廣義來看)。

如果你懶得看我落落長的文章，那看到這邊就夠了 XDD, 以上才是我認為本篇文章的精華, 我就先破題, 把重點都擺在前面了。如果你還是對實做的 workshop 過程有興趣，那歡迎繼續往下看 :D










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