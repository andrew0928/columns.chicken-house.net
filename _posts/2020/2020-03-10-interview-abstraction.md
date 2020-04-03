---
layout: post
title: "架構面試題 #4 - 抽象化設計, 折扣規則的設計機制"
categories:
- "系列文章: 架構師觀點"
- "系列文章: 架構面試題"
tags: ["系列文章", "架構師", "C#", "OOP"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2020-03-10-interview-abstraction/logo.jpg
---

![](/wp-content/images/2020-03-10-interview-abstraction/logo.jpg)  
[圖片來源](https://mobile-cuisine.com/marketing/why-offer-discount-coupons/)




最近看到好幾篇有內容的討論串，都提到 "抽象化思考" 是個很關鍵的能力。我就在想 "什麼才是正確的抽象化思考" 案例? 看了很多講理論的文章，也看了很多[定義](https://zh.wikipedia.org/wiki/%E6%8A%BD%E8%B1%A1%E5%8C%96), 我相信很多人還是一樣有看沒有懂，或是你真的理解抽象化的概念了，但是真正應用在工作上，你也不一定用的到位啊! 於是就有了寫這篇文章的念頭。我一樣不喜歡只講 "理論"，理論說的容易，要落實才是最難的那一步，因此我決定拿個實際上工作相關的案例來說明 "抽象化" 概念。

我就拿我在 [面試架構師常問的問題](/wp-content/images/2020-03-10-interview-abstraction/interview.png) 之一: "折扣機制的設計方式" 當作這篇文章的主題吧! 只要做過銷售網站，或是相關的系統，我相信一定都被這個主題弄得牙癢癢的，你想的再週全，你的客戶就是有辦法想出你意料不到的折扣規則來折磨你...。不過，這是個很好的例子啊，正好拿來驗證你的抽象化思考夠不夠到位。該說是職業病嗎? 從開始學寫 code 後，我就習慣在日常生活中，碰到大小事情，我都會在腦袋裡想一下 "這東西我該怎麼寫 code 來處理?" ...，就是這個折扣計算的問題，每次我在收銀機等結帳時就在想:

*這個第二件六折的折扣我該怎麼去計算?*

*這個第二件加一元我該怎麼設定才合理?*

*這個即期品半價優惠的機制我該怎麼設計，POS 機才能搞的定?*

*這麼多種折扣混在一起，結帳時怎麼用一致的規則來處理才不會算錯?*

這些問題我就這樣，在我腦袋裡面轉過好幾次了 XDD (所以一時之間想不出來的朋友們不用難過)。我就用這篇文章的篇幅來說明一下該如何將這問題抽象化，然後一步一步解決現在跟未來的問題。

<!--more-->

雖然這篇是 "架構面試題"，不過我也是把他歸類在 "微服務架構" 系列文章之內。原因很簡單，所謂的 "抽象化"，就是將事物的共通或是概念的部分 "抽離" 出來，丟開複雜的實作細節，只留下抽象的概念部分的過程。這除了是思考解決問題的重要過程之外，也是思考各種 interface 的關鍵啊! 只要跟 interface 扯上關係的技術，都跟抽象化能力有直接關聯，小到 class library 的設計，大到服務切割的邊界怎麼定義，都需要仰賴良好的抽象化思考能力。

因此，如何能精準明確的定義 interface，抽象化思考的能力絕對是關鍵。當你能掌握 interface 後，一切的 code 都變的很簡單了。剩下的實作只剩下工程問題，套入適當的工具或是框架就會迎刃而解。有相當多的技術都要仰賴 interface 才能運作，例如[相依性注入](https://en.wikipedia.org/wiki/Dependency_injection) (DI, Dependency Injection), 各種 API 相關技術 (API: Application Programming Interface), 各種服務呼叫的合約約束 (gRPC, Swagger, WCF 的 Service Contract / Data Contract 等等) 都是。你如果想要充分掌握這些技能，沒有搞懂抽象化，那你只是學到皮毛而以。

<!-- 微服務架構文章目錄 -->

{% include series-2016-microservice.md %}



# 問題: 折扣機制到底有多難搞?

開始進入本文，我們就直接來看折扣計算的問題吧! 這次我不自己想題目了，我直接跟現成的 DM 來取材。什麼東西的折扣機制最複雜? 我想就以超市為首選了 XDD, 我逛了逛最近很紅的全X超市，從他的官網首頁隨便挑幾個折扣的促銷資訊，同時在底下先標上我自己的註記:


> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-00-58-41.png)
> NOTE: 指定商品 (衛生紙) 一次買 6 捲便宜 100 元

> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-01-03.png)  
> NOTE: 指定商品 (蘋果) 單粒 23 元， 4 粒 88 元


> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-03-15.png)  
> NOTE: 指定商品 (雞湯塊) 單盒特價 145 元，第二件 5 折


> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-04-36.png)  
> NOTE: 指定商品 (沐浴乳) 買一送一


當然還有更複雜的，除了折扣外還送點數，或是你搭配點數可以折抵部分金額等等的玩法，這篇就不討論了 (再講我就透漏太多商業機密了 XDD)，我單純只談論 "折扣" 的部分就好。

大部分的 developer, 碰到這類的問題，第一個浮現的解法就是 "歸納" 法。簡單的說，就是把上面我寫的 NOTE，同樣句型的歸成一類，黑字的部分變成參數，就搞定了 (展示用的 POC code 後面再補)。這麼一來，上面的規則大概就被我規成四類了。每類寫一段計算折扣的邏輯就搞定了。我想大部分靠 coding 維生的人應該都不成問題。



接下來玩大一點，換一家店看看... 這次我們看全X便利商店:

> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-15-06.png)  
> NOTE: 指定商品 2 件 + 49 元送杯套一個

> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-16-09.png)  
> NOTE: 指定商品 同商品 加 10 元多 1 件

> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-17-23.png)  
> NOTE: 指定商品 任選兩件 第二件 6 折，不同價格以兩件 8 折計算


有發現嗎? 這些規則，乍看都跟前面的規則差不多，但是卻又有點差異... 舉例來說，如果沒有限定同商品的話，第二件六折，跟任選兩件八折就不一樣了，你在計算時就得區分這兩者的差異... 買一送一，也跟第二件免費 (0折) 不同，一個是直接送你 (你買了一件就會送你一件)，一個是你要自己拿進購物車 (你一次拿兩個第二個免費，不過你只要一個的話也無不可) 啊... 如果硬要歸類到同樣的規則，那你就得搭配許多額外的 "設定" 用的 flag(s) 才行。例如如果你實作了一個 "第 N 件 Y 折" 的計算程式，你就要在設定畫面多加這個選項:


> "折扣設定為 0 折時，是否自動將第 N 件商品加入購物車?"


這樣下去沒完沒了，不是說這樣設計不對，不過這些設定都是工程問題啊，不是商業問題；如果我是經營商店的老闆，看到這些設定一定會丈二金剛摸不著頭腦... 

> "我只是要啟動買一送一的優惠啊，為什麼有這麼多奇怪的設定? 這個 UX 很糟糕..."


頭開始痛了嗎? 還沒結束... 繼續往下看，很多超商還愛玩一種配對的折扣: 早餐 + 飲料 這種...

> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-30-14.png)  
> NOTE: 指定鮮食 + 指定飲料 特價 ( 39元, 49元, 59元 )


覺得有點難歸納了嗎? 別急，還沒結束... 再來一個:


> ![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-10-01-31-25.png)  
> NOTE: 任選主餐 + 指定副餐 折 5 元


真是夠了，零售業者就是有辦法想出你意料之外的折扣規則 XDD ... 你會發現，光靠 "歸納" 法，你已經無法應付 "現在 & 未來" 的問題了。歸納法則，可以讓你從 "已知" 的需求來歸納出解決做法，並且參數化，模組化之後能重複使用。不過，歸納法很難面對未知的問題啊! 你無法預測未知的問題會不會落在你歸納出來的法則範圍內。

算算看，上面列舉的這些折扣，你需要歸納成幾種優惠? 如果真的要開發的話，你會開發幾種折扣計算模組? 你會怎麼安排這些設定用的 flags ? 這些決策，都影響了你該怎麼開發與維護這套系統。如果再來個致命一擊，哪天老闆突然說，這每種規則又有區分會員價跟非會員的話...




# 抽象化: 隱藏細節、提取重點

好了，別再打擊各位了，例子我就舉到這邊就好 (你想知道的話還有更多變態的折扣規則可以聊)。我們回到這篇的主題: 抽象化。

先來看看抽象化的定義，很多定義都太生硬了，我比較喜歡這篇的說法:

> 「隱藏細節、提取重點」可以說是抽象化的核心精神。


參考來源: [運算思維的核心 — 抽象化](https://medium.com/orangeapple/%E9%81%8B%E7%AE%97%E6%80%9D%E7%B6%AD%E7%9A%84%E6%A0%B8%E5%BF%83-%E6%8A%BD%E8%B1%A1%E5%8C%96-c7e013f30c6)


不過，折扣機制的重點又是什麼? 有哪些是該被隱藏的細節? 因此，這定義我補充修飾一下，讓他更到位:

> 抽象化:  
> 提取重點；目的是讓你的主系統只依照被提取的重點設計流程；  
> 隱藏細節；目的是讓跟重點無關的細節不會影響主系統的設計；即使日後改變細節也不會影響到主系統的運作。


因為你決定了提取的 "重點" 是那些部分後，其他的細節自然就被隱藏起來了。隱藏細節的另一面其實就是隔離細節；適度隔離細節之後，你自然有能力對這些細節做調整，更動或是替換，而不會影響主系統。

區隔 "重點" 與 "細節" 的界線，就是介於兩者中間的 "介面" (interface) 了。因此我才會不斷的強調，抽象化的成果就是你定義的 interface 。這時，你就可以跟各種 OOP / 軟體工程 或是 微服務 提到的各種 interface 聯想在一起了。這些工具或是框架，就是支持你實現 interface 的做法，但是萬變不離其宗，定義好 interface 的內容，仍然要靠你良好的抽象化思考才辦的到。



# OOP 三大權杖: 封裝、繼承、多型

繼續之前，容我岔題一下。我們來聊聊 OOP 的三大權杖之一: [封裝](https://en.wikipedia.org/wiki/Encapsulation_(computer_programming))) (Encapsulation), 封裝其實跟抽象化是一體兩面。抽象化是你的目的，你想把你的 "重點" 概念表達出來，你就必須把其它不相關的細節隱藏起來。封裝是隱藏細節的作法，封裝後的成效就是抽象化。

如果跟我一樣，有點年紀的 developer, 大概都經歷過 C / C++ 那個 [ADT](https://zh.wikipedia.org/wiki/%E6%8A%BD%E8%B1%A1%E8%B3%87%E6%96%99%E5%9E%8B%E5%88%A5) (Abstract Data Type) 的年代吧! 把上面講的封裝概念，套用在你要描述的物件 (class) 或是資料 (struct) 上，創造出來的就是 "抽象資料型別" (ADT)。

OOP 的三大權杖分別是: [繼承](https://en.wikipedia.org/wiki/Inheritance_(object-oriented_programming)) (Inheritence), [封裝](https://zh.wikipedia.org/wiki/%E5%B0%81%E8%A3%9D_(%E7%89%A9%E4%BB%B6%E5%B0%8E%E5%90%91%E7%A8%8B%E5%BC%8F%E8%A8%AD%E8%A8%88)) (Encapsulation), [多型](https://en.wikipedia.org/wiki/Polymorphism_(computer_science)) (Polymorphism)... 這三者也是緊緊扣在一起的。當你要封裝一個資料類型，你會把細節隱藏在內部。當你有多個資料類型要封裝，你會開始把重複的部分題取出來，讓你可以一視同仁的看待這些不同的資料類型。要達成這一般化 (generalization) 的方法就是繼承。物件導向語言裡的繼承，都可以在語言的層次，把有繼承關係的物件用 is-a 的關係去看待他，從共同的類別衍生出來的類別都可以當成父類別看待，即使在強型別的系統內，你一樣可以用一致的型別來操作他。不同類別的物件，都被當成同樣父類別的物件看待，而每個物件卻都能對同樣的操作，有各自不同對應的行為表現，這就是多型。

穿插這 OOP 的說明，就是要讓大家知道，抽象化做的到位，OOP 的三大權杖你就應該也掌握的到位了。後續的應用就可以非常靈活的變化。相對的你如果覺得抽象化之後用的卡卡的，那請回頭重新思考，你的抽象化是否真的有做到「隱藏細節、提取重點」? 思考這類問題時別太在意對錯，這種思考題目是沒有對錯的。會發生的狀況是，你隱藏的細節，不是你解決的問題需要的；你提取的重點，也剛好不是你要解決的問題的重點；如此而以，只是適不適合的差別。因此要是覺得不對勁，請回頭重新想想。



# 思考: 將折扣機制抽象化

OK，再次回到我們的主題: 折扣機制。折扣機制的 "重點" 到底應該是什麼? 你該隱藏的 "細節" 又是什麼? 前面說到，你抽象化封裝應該要對齊你要解決的問題才對。來看看上面舉的這麼多案例，你要解決最 "頭痛" 的問題是什麼?

為了方便複習，我把這些折扣規則的 NOTE 列在一起方便思考:


> NOTE: 指定商品 (衛生紙) 一次買 6 捲便宜 100 元  
> NOTE: 指定商品 (蘋果) 單粒 23 元， 4 粒 88 元  
> NOTE: 指定商品 (雞湯塊) 單盒特價 145 元，第二件 5 折  
> NOTE: 指定商品 (沐浴乳) 買一送一



我的答案是: 對購物車而言，我想隱藏的細節是 "計算規則"，因為每種折扣的規則都不大一樣，對開發人員來說那是很煩人的事情。我真正在意的結果是最終的折扣金額。面對眼前要結帳的這些商品，購物車在意的是這點:

* 這些商品符合哪些折扣規則要求的條件? 符合的話會折抵多少金額?

如果這件事被我 "抽象化" 之後，我暫時假設我已經解決了，那麼購物車計算金額的過程就可以大幅簡化:

1. 計算要結帳的商品原價總金額 (未折扣)
1. 逐一確認每個折扣規則可以折抵的金額
1. 未折扣總金額 - 所有可折抵的金額 = 最後結帳的價格
1. 執行後續收款以及成立訂單或列印發票收據等等流程.

這就是個 "良好" 的抽象化結果，因為抽象化的界線，正好對應到我們要解決的問題點身上，因此我會覺得他是個 "好" 的抽象化。看看抽象化後的結帳流程，看起來不管商店老闆還想推出什麼折扣優惠，看來這個流程都能順利的執行啊! 如果我們寫的 code 真的能夠按照這架構去設計，也許我們真的能夠設計出一套不會被這些折扣活動搞死的系統架構。

是的，這就是我寫這篇的目的，我也會在後面的 code 來展示怎麼做到這點。經過這樣調整，購物車的程式設計就再也不需要被 "不同的折扣計算規則" 綁架了，從此就此解放；這就是我認為折扣規則抽象化之後的重點。

因此，我不打算去描述任何 "規則" 的細節，而是把重點擺在我要買的這整車 (購物車) 的商品，結帳的過程該怎麼跟每個折扣規則互動，完成結帳的動作。至於折扣的細節 (計算過程)，反正我怎麼列也列不完，就把它隱藏起來吧! 為了這目的，我們必須先定義一個折扣規則該有的 "介面"，應該長成什麼樣子才對? 購物車只要透過這個介面來溝通。其他所有的折扣規則，則是在這個介面規範以下的不同實作；完成這樣的架構，我們就能達到上述的理想。

當然，實際開發可能沒那麼簡單，在 C# 的定義上，有兩種技術都能支持這個架構要求，一個是 abstract class, 可以包含部分實作；另一個是 interface, 只允許介面定義，不支援任何實作。 (別跟我說 C# 8.0 開始支援的 [default implementation in interfaces](https://devblogs.microsoft.com/dotnet/default-implementations-in-interfaces/)..., 那是個詭異的東西, 我個人不大認同這設計...)




----

準備好了嗎? 所有的觀念說明到此告一段落! 如果還沒想通的話，請往前翻一翻重新思考一下。接下來就會進到 coding 的階段。

----







# 案例實作: 模擬實際的訂單計算

從這裡開始，我們就要用 code 來討論了。以下所有的 code 都放在我的 GitHub Repo: [Andrew.DiscountDemo](https://github.com/andrew0928/Andrew.DiscountDemo), 歡迎取用~

很多時候抽象化思考都必須倒回來想，假定抽象化都完成了，你可以開始在 high level 的角度來解決問題的話，你該怎麼做? 隱藏了折扣計算細節後，我的購物車結帳的 code 只要能正確描述 & 處理這些問題就夠了:

1. 描述商品資訊 (包含品名、標籤及售價)
1. 進行中的折扣計算
1. 結帳的收據明細顯示

邏輯很簡單，把 (1) 經過所有的 (2) 處理後，最後得到 (3) 就是了。我先跳過 (2), 用一個最簡單的無任何折扣的結帳案例開始，先來看看我怎麼定義商品。


## 步驟 1, 定義系統架構

首先，整個系統先從最關鍵的商品資訊 Entity 定義開始:

```csharp

public class Product
{
    public int Id;
    public string SKU;
    public string Name;
    public decimal Price;
    public HashSet<string> Tags;
}

```

應該簡單到不需要解釋了吧! Id, SKU, Name, Price 就是你想的那樣。比較特別的是我加了 Tags, 我打算用他來描述額外貼在商品上面的各種標籤，協助購物車判斷商品的屬性。實際用途後面碰到再說明，我先留個定義就好。

商品資訊定義好之後，結帳的過程應該就寫的出來了。我略過購物車或是 POS 等等角度的抽象化，直接寫在 ```Main()``` 裡面了，一個最陽春的結帳運算就寫好了:

```csharp

class Program
{
    static void Main(string[] args)
    {
        var products = LoadProducts();
        foreach(var p in products)
        {
            Console.WriteLine($"- {p.Name}      {p.Price:C}");
        }
        Console.WriteLine($"Total: {CheckoutProcess(products.ToArray()):C}");
    }


    static decimal CheckoutProcess(Product[] products)
    {
        decimal amount = 0;
        foreach(var p in products)
        {
            amount += p.Price;
        }
        return amount;
    }

    static IEnumerable<Product> LoadProducts()
    {
        return JsonConvert.DeserializeObject<Product[]>(File.ReadAllText(@"products.json"));
    }
}

```

其中，```LoadProducts()``` 負責傳回購物籃內所有的商品清單；而 ```CheckoutProcess()``` 則負責結帳，會傳回最終的結帳金額。```Main()``` 沒做啥事，就是呼叫這些 method, 同時負責顯示 (收據) 的功能而已。為了節省一點 code, 我另外建了一個 ```products.json``` 資料檔，直接把購物車的商品內容寫在裡面:

```json
[
  {
    "name": "乖乖(椰子口味)",
    "sku": "K0132",
    "price": 20
  },
  {
    "name": "乖乖(椰子口味)",
    "sku": "K0132",
    "price": 20
  },
  {
    "name": "乖乖(椰子口味)",
    "sku": "K0132",
    "price": 20
  }
]

```

為了簡化，我也省去了商品定義資料庫，跟我買了那些東西的 ID 關聯。我做了一點反正規劃的設計，直接列出我買的每一件商品的詳細資訊。同時買了 N 件，我不打算用 Qty 來標示數量，我選擇直接重複列 N 筆。這樣做的好處後面會看的到，我先定義資料檔案的格式，讓 POC 能夠順利推進下去。

這段 code 執行後應該就可以順利的列出收據內容:

```text

- 乖乖(椰子口味)      $20.00
- 乖乖(椰子口味)      $20.00
- 乖乖(椰子口味)      $20.00
Total: $60.00

```

這邊真的是初學者等級的，我就當作前置作業就好，應該不用多作說明吧? 接下來直接面對我們的主題: 折扣處理。




## 步驟 2, 定義折扣規則的抽象化介面

延續上面的示範程式，我要在這個基礎上開始添加折扣規則進去了。前面我找了很多線上購物的折扣規則說明，現在我直接舉一筆實際的交易案例，然後試著來實作看看怎麼寫出來。這是我自己在某網站上的交易明細 (這系統不是我開發的)，然後我試著揣摩一下他的設計方式，然後對他作抽象化。

我這筆交易，實際上買了這些東西:

![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-15-03-18-21.png)

在這交易內，我使用了這張折價券:

![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-15-03-22-55.png)


我買了一樣的三箱飲料，這飲料當時有個優惠活動: "任兩箱結帳88折"，同時我還有一張 "$100 現折券 (滿 $1000 可使用)" 的優惠券。其實湊四箱優惠更大，但是我不想買這麼多啊，因此我當時只買了三箱，湊到 1000 元，剛剛好符合折價券的要求。不過我事後查了一下電子發票，才發現廠商每箱都開了個別的電子發票給我，總共有三張。也因為如此，店員在結帳時還覺得奇怪，為何買一樣的東西買三箱，但是價格卻不一樣... XDD

我把三張發票都貼一下:

![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-15-03-24-29.png)

![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-15-03-24-42.png)

![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-15-03-25-02.png)



我們就從模擬這個例子，開始來探討看看該如何用抽象化思考的角度，來寫這段結帳程式吧。我不大想在這篇再去探討折價券管理跟核銷等等問題，我就暫時把折價券的優惠 (滿 $1000 折 $100) 簡化，當作一般的折扣活動來看待, 不管你有沒有折價券都能享用這優惠吧。同時加個限制: 每筆交易限用一次，意思是滿 $1000 我給你 $100 的優惠，但是滿 $2000 就沒有給你 $200 了，一樣只有 $100 的折扣。因此以下的程式碼就不再去處理優惠券的相關問題 (你有沒有這張折價券? 你這張卷用過了沒... 等等)。

"折扣" 應該要怎麼抽象化? 我的目的是希望結帳程序 (CheckoutProcess) 能用一樣的流程來結帳，計算過程中能夠順利的處理完各種折扣規則。因此我抽象化的重點，應該擺在:

1. 找出重點: 抽象化所有的折扣規則，用同樣的概念來描述 "所有" 的折扣活動
1. 隱藏細節: 包括跟重點無關的細節，以及不同折扣活動之間的差異，都應該被當作細節隱藏起來，才能用多型處理。

更重要的是，做完這些抽象化之後，我應該能讓購物車更簡單一致的處理這些千奇百怪的折扣規則了。因此我決定這樣往下推進，我認為每個折扣活動，都應該:

1. 能依據購物車上的所有商品 (input)，決定結帳後享有那些折扣 (output)，用統一的方式回報折扣資訊。
1. 在符合 (1) 的規範下，每個折扣活動可以有自己的計算邏輯實作。
1. 折扣活動彼此之間有先後順序，若商品同時滿足多種折扣活動，則按照順序進行。

按照這想法，我訂出第一版的活動的設計規範了:

```csharp

public abstract class RuleBase
{
    public int Id;
    public string Name;
    public string Note;
    public abstract IEnumerable<Discount> Process(Product[] products);
}

```

前面的 Id, Name, Note 我就不解釋了, 就是活動的 metadata 而已；關鍵在 ```IEnumerable<Discount> Process(Product[] products);``` 是驅動整個折扣計算的核心 method。他接受購物車上所有的商品當作輸入，同時輸出因為這個活動跟商品組合，最後計算出來符合的折扣結果，用 ```Discount``` 類別來描述。這個 method 可能會傳回多個 ```Discount```, 介面上我用 ```IEnumerable<Discount>``` 來當作傳回值。

接著再來看一下 ```Discount``` 的定義:

```csharp

public class Discount
{
    public int Id;
    public string RuleName;
    public Product[] Products;
    public decimal Amount;
}

```

一筆 ```Discount``` 資料，代表符合的一項折扣，也是將來會在收據上註記的一筆折扣。每一筆折扣結果，應該要標記這是來自哪個折扣規則 (```RuleName```), 是因為購買那些商品 (```Products```) 才享有這折扣? 最終折扣的金額 (```Amount```) 有多少?

這些跟折扣計算相關的界面都定義好了之後，抽象化的設計就算完成。接著我們就要讓每個折扣都能在這規範之下運作，在這規範之下填入自己的規則計算。如果這些都已備妥 (還是一樣，都要倒回來思考)，那麼購物車結帳時該怎麼使用它? 我把原本案例的 ```CheckoutProcess()``` 也做一番改造。改版後的結帳程序，要額外多接收一組折扣規則 (按照優先順序排序):


```csharp

static decimal CheckoutProcess(Product[] products, RuleBase[] rules)
{
    List<Discount> discounts = new List<Discount>();

    foreach(var rule in rules)
    {
        discounts.AddRange(rule.Process(products));
    }

    decimal amount_without_discount = CheckoutProcess(products);
    decimal total_discount = 0;

    foreach(var discount in discounts)
    {
        total_discount += discount.Amount;
        Console.WriteLine($"- 符合折扣 [{discount.RuleName}], 折抵 {discount.Amount} 元");
    }

    return amount_without_discount - total_discount;
}

```

有了 ```RuleBase``` 這樣抽象化界面來代表所有的折扣規則後，是不是購物車結帳的邏輯就清楚多了? 這幾行 code 應該不用解釋就看的懂了吧? 只有 20 行不到，大家自行體會 :D



## 步驟 3, 實作第一個折扣規則


接下來，我們就來實作第一個折扣規則 (任兩箱結帳88折) 看看:

```csharp

public class BuyMoreBoxesDiscountRule : RuleBase
{
    public readonly int BoxCount = 0;
    public readonly int PercentOff = 0;

    public BuyMoreBoxesDiscountRule(int boxes, int percentOff)
    {
        this.BoxCount = boxes;
        this.PercentOff = percentOff;

        this.Name = $"任 {this.BoxCount} 箱結帳 {100 - this.PercentOff} 折!";
        this.Note = "熱銷飲品 限時優惠";
    }

    public override IEnumerable<Discount> Process(Product[] products)
    {
        List<Product> matched_products = new List<Product>();

        foreach(var p in products)
        {
            matched_products.Add(p);

            if (matched_products.Count == this.BoxCount)
            {
                // 符合折扣
                yield return new Discount()
                {
                    Amount = matched_products.Select(p => p.Price).Sum() * this.PercentOff / 100,
                    Products = matched_products.ToArray(),
                    RuleName = this.Name,
                };
                matched_products.Clear();
            }
        }
    }

}

```

最後，把這些東西都在 ```Main()``` 裡面組起來:

```csharp

static void Main(string[] args)
{
    var products = LoadProducts();
    foreach(var p in products)
    {
        Console.WriteLine($"- {p.Name}      {p.Price:C}");
    }
    Console.WriteLine($"Total: {CheckoutProcess(products.ToArray(), LoadRules().ToArray()):C}");
}

static IEnumerable<Product> LoadProducts()
{
    return JsonConvert.DeserializeObject<Product[]>(File.ReadAllText(@"products.json"));
}

static IEnumerable<RuleBase> LoadRules()
{
    yield return new BuyMoreBoxesDiscountRule(2, 12);   // 買 2 箱，折扣 12%
}

```

果然執行後跑出我們期待的結果: 買了三箱，兩箱符合折扣，最後金額是 1104 元

```text

- [御茶園]特撰冰釀微甜綠茶 550ml(24入)      $400.00
- [御茶園]特撰冰釀微甜綠茶 550ml(24入)      $400.00
- [御茶園]特撰冰釀微甜綠茶 550ml(24入)      $400.00
- 符合折扣 [任 2 箱結帳 88 折!], 折抵 96 元
Total: $1,104.00

```

在這邊暫停一下，再繼續往下。其實算出正確答案並沒有很了不起，做過線上購物網站的朋友們，大概這都不會是問題。問題在於這段範例程式，真的做到 "抽象化" 了嗎? 真的有把各種折扣的細節隱藏起來了嗎? 我先提醒，我最終目的是不要修改購物車的主程式，就要能夠支援後面的各種折扣規則。至於折扣規則本身有沒有被抽象化，我從幾個角度來回答這問題:

**折扣規則的抽象化**: ```RuleBase```

程式碼我就不重新貼一次了，請大家往上捲，直接看 ```BuyMoreBoxesDiscountRule``` 這個類別。

除了這個類別，看的到跟這 [任 2 箱結帳 88 折!] 折扣的規則之外，其他完全沒看到，都只是外圍的結帳，或是收集所有規則的折扣，計算最後金額，還有處理顯示收據邏輯的 code 而已。稍後我們再示範複雜一點的組合，你就會發現封裝的威力。


**多型的應用**: CheckoutProcess

封裝後的東西，要用多型的方式去運用他，這邊就要看 ```decimal CheckoutProcess(Product[] products, RuleBase[] rules)``` 的實作了。受惠於 ```RuleBase``` 的抽象化, ```CheckoutProcess()``` 可以不需要理會所有折扣的規則細節。要計算折扣，它只需要按照步驟進行:

1. 把整車購物車購買的商品清單，按照順序交給每一個折扣規則 ```RuleBase``` 處理，並且收集每個 ```RuleBase``` 回報的折扣資訊 ```IEnumerable<Discount>```。
1. 計算未折扣的價格 (原價)，並且列印到畫面上。
1. 將步驟 (1) 收集到的所有折扣，按照順序列印到畫面上。
1. 完成，傳回最後結帳金額，顯示最終價格。

受惠於多型的便利，這段結帳的邏輯已經為未來的擴充做好所有的準備了。除了沒有碰觸到 [任 2 箱結帳 88 折!] 的所有特殊規則之外，還把未來的規則考慮進去了。多型就是該這樣應用啊，只要你不去碰觸 RuleBase 類別衍生的所有資訊，一律只透過 ```RuleBase``` 的定義來存取 ```Process()``` 的介面定義，剩下的計算，OOP 多型的機制自然會幫你重新導向到各個衍生類別自行定義的邏輯。

體會到了嗎? 如何拿捏好有哪些資訊是要放在 ```RuleBase``` ，有哪些資訊應該下放到衍生類別，這就是這次抽象化封裝的核心概念。封裝的範圍不多不少，剛剛好恰到好處是最完美的。拿捏好這個尺度，你就會發現邏輯收的很乾淨漂亮。


## 步驟 4, 重構

開始把後續的折扣加上去前，我調整一下原本的架構，讓外圍的邏輯收斂一些，讓後面的例子能夠更容易被理解。原本 ```RuleBase.Process()``` 定義的簽章，只接收 ```Product[]``` 的參數而已，對於這個折扣規則而言，輸入不大足夠。因為從 ```Product[]``` 並無法得知目前折扣後的金額為何。同時前一個版本在顯是資訊時也有點混亂，```Console.WriteLine()``` 的 code 分散在兩個地方，我先進行重構調整一下這些問題再繼續。

我打算用一個類別 ```CartContext```, 來把所有跟目前購物車的狀態資訊都封裝再一起，包含你買了那些東西，目前已經計算到多少折扣等等資訊。這邊我也會開始使用到前面保留未用的 Tags... 先來看看我重構後的 code (沒有增加任何功能，單純架構調整):

```csharp

class Program
{
    static void Main(string[] args)
    {
        CartContext cart = new CartContext();
        POS pos = new POS();

        cart.PurchasedItems.AddRange(LoadProducts());
        pos.ActivedRules.AddRange(LoadRules());

        pos.CheckoutProcess(cart);

        Console.WriteLine($"購買商品:");
        Console.WriteLine($"---------------------------------------------------");
        foreach(var p in cart.PurchasedItems)
        {
            Console.WriteLine($"- {p.Id,02}, [{p.SKU}] {p.Price,8:C}, {p.Name}, {p.TagsValue}");
        }
        Console.WriteLine();

        Console.WriteLine($"折扣:");
        Console.WriteLine($"---------------------------------------------------");
        foreach(var d in cart.AppliedDiscounts)
        {
            Console.WriteLine($"- 折抵 {d.Amount,8:C}, {d.Rule.Name} ({d.Rule.Note})");
            foreach (var p in d.Products) Console.WriteLine($"  * 符合: {p.Id, 02}, [{p.SKU}], {p.Name}, {p.TagsValue}");
            Console.WriteLine();
        }
        Console.WriteLine();

        Console.WriteLine($"---------------------------------------------------");
        Console.WriteLine($"結帳金額:   {cart.TotalPrice:C}");
    }


    static int _seed = 0;
    static IEnumerable<Product> LoadProducts(string filename = @"products.json")
    {
        foreach(var p in JsonConvert.DeserializeObject<Product[]>(File.ReadAllText(filename)))
        {
            _seed++;
            p.Id = _seed;
            yield return p;
        }
    }

    static IEnumerable<RuleBase> LoadRules()
    {
        yield return new BuyMoreBoxesDiscountRule(2, 12);   // 買 2 箱，折扣 12%
        yield break;
    }
}

public class CartContext
{
    public readonly List<Product> PurchasedItems = new List<Product>();
    public readonly List<Discount> AppliedDiscounts = new List<Discount>();
    public decimal TotalPrice = 0m;
}

public class POS
{
    public readonly List<RuleBase> ActivedRules = new List<RuleBase>();

    public bool CheckoutProcess(CartContext cart)
    {
        // reset cart
        cart.AppliedDiscounts.Clear();

        cart.TotalPrice = cart.PurchasedItems.Select(p => p.Price).Sum();
        foreach (var rule in this.ActivedRules)
        {
            var discounts = rule.Process(cart);
            cart.AppliedDiscounts.AddRange(discounts);
            cart.TotalPrice -= discounts.Select(d => d.Amount).Sum();
        }
        return true;
    }
}

public class Product
{
    public int Id;
    public string SKU;
    public string Name;
    public decimal Price;
    public HashSet<string> Tags;

    public string TagsValue { 
        get
        {
            if (this.Tags == null || this.Tags.Count == 0) return "";
            return string.Join(",", this.Tags.Select(t => '#' + t));
        }
    }
}

public class Discount
{
    public int Id;
    public RuleBase Rule;
    public Product[] Products;
    public decimal Amount;
}

public abstract class RuleBase
{
    public int Id;
    public string Name;
    public string Note;
    public abstract IEnumerable<Discount> Process(CartContext cart);
}

```



解釋我重構了什麼東西前，先看一下類別圖 (class diagram):

![](/wp-content/images/2020-03-10-interview-abstraction/2020-03-16-00-59-19.png)

我用了 ```POS``` 來代表結帳時的所有計算邏輯；目前商店有多少活動正在舉行中，應該是店家控制的，因此 ```Rules``` 掛在 ```POS``` 底下，是它的 properties 之一。

至於 ```CartContext```, 則收納了每個顧客，購物車裡的所有狀態，包含結帳後的發票資訊。這邊我就沒很嚴格的控制狀態了，結帳兩次以最後一次為準。也因此，購買的商品清單，以及總金額跟折扣明細都包含在內。

其他的規則沒有大改變，就是依照這架構調整，搬到正確的位置而已。因應這個改變，折扣規則的 ```RuleBase.Process()``` 簽章改成這樣:

```
public abstract IEnumerable<Discount> Process(CartContext cart);
```

其餘把這些都組合在一起的部分，就留在 ```Main()``` 裡面了。裡面唯一負責的職責，就是讓大家能跑起來。初始化正確的 ```POS``` 以及 ```CartContext``` 物件，將購物車的內容交給 ```POS``` 結帳，最後格式化的輸出訂單資訊:

```text

購買商品:
---------------------------------------------------
-  1, [DRINK-001201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入),
-  2, [DRINK-001201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入),
-  3, [DRINK-001201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入),

折扣:
---------------------------------------------------
- 折抵   $96.00, 任 2 箱結帳 88 折! (熱銷飲品 限時優惠)
  * 符合:  1, [DRINK-001201], [御茶園]特撰冰釀微甜綠茶 550ml(24入),
  * 符合:  2, [DRINK-001201], [御茶園]特撰冰釀微甜綠茶 550ml(24入),


---------------------------------------------------
結帳金額:   $1,104.00

```

輸出個格式也精準了一點，購買商品我在最後面印出了商品標籤 (後面會用的到)，折扣項目我也列出了每項優惠背後是因為你買了那些商品，方便解讀。



## 步驟 5, 擴充第二個規則

接下來，我打算把第二個折扣也加上去了。第二個折扣是: 折價券滿 1000 抵用 100, 每次交易限用一次。

由於前面的規劃，已經把 ```RuleBase``` 折扣規則的抽象化做的很到位了，因此接下來我們應該能無痛擴充才對。我開始前先許願一下，我期待抽象化帶來的成果是:

1. 開發新的 Rule (從 RuleBa```se 衍生出新類別)
1. 按照折扣的順序，把 (1) 的 ```RuleBase``` instance 加在 ```POS``` 的 ```ActivatedRules()``` 清單內

做完上面的動作後，**理論上我不需要更動任何其他的 code, 新的折扣就應該生效才對**。這點很重要，因為這就是我寫這一整篇的目的啊! 折扣規則抽象化之後，就能讓 ```POS``` 在結帳時能有一致的處理方式，即使需要擴充折扣規則，也不需更動 ```POS``` 既有的結帳程序。```POS``` 的 code 可以一行都不用改 (以後甚至希望能夠不需要重新編譯，不過這篇就略過這部份了) 就能生效。

若能達成這個目標，我們的抽象化才有意義，也才能把 OOP 的精神發揮到極致，這才是多型最有威力的地方啊! 接下來我們開始一步一步的擴充我們的 demo code。



上述的步驟 (1), 開發新的 Rule (從 ```RuleBase``` 衍生出新類別) :

```csharp

public class TotalPriceDiscountRule : RuleBase
{
    public readonly decimal MinDiscountPrice = 0;
    public readonly decimal DiscountAmount = 0;

    public TotalPriceDiscountRule(decimal minPrice, decimal discount)
    {
        this.Name = $"折價券滿 {minPrice} 抵用 {discount}";
        this.Note = $"每次交易限用一次";
        this.MinDiscountPrice = minPrice;
        this.DiscountAmount = discount;
    }

    public override IEnumerable<Discount> Process(CartContext cart)
    {
        if (cart.TotalPrice > this.MinDiscountPrice) yield return new Discount()
        {
            Amount = this.DiscountAmount,
            Rule = this,
            Products = cart.PurchasedItems.ToArray()
        };
    }
}

```

撇除設定的部分不看，真正處理折扣的地方就很簡單，只有一行啊... 跟文案要求的一模一樣，判斷一下目前總價是否超過 1000, 如果是的話就給 100 的折扣。

新的折扣 (```TotalPriceDiscountRule```) 定義好後，只要在 ```POS``` 啟用它即可。我多加了這行:

```csharp

static IEnumerable<RuleBase> LoadRules()
{
    yield return new BuyMoreBoxesDiscountRule(2, 12);   // 買 2 箱，折扣 12%
    yield return new TotalPriceDiscountRule(1000, 100); // 滿 1000 折 100
    yield break;
}

```




前面講的步驟 (1) (2) 都完成了，試著重新執行一次看看，以下是執行的結果:

```text

購買商品:
---------------------------------------------------
-  1, [DRINK-001201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入),
-  2, [DRINK-001201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入),
-  3, [DRINK-001201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入),

折扣:
---------------------------------------------------
- 折抵   $96.00, 任 2 箱結帳 88 折! (熱銷飲品 限時優惠)
  * 符合:  1, [DRINK-001201], [御茶園]特撰冰釀微甜綠茶 550ml(24入),
  * 符合:  2, [DRINK-001201], [御茶園]特撰冰釀微甜綠茶 550ml(24入),

- 折抵  $100.00, 折價券滿 1000 抵用 100 (每次交易限用一次)
  * 符合:  1, [DRINK-001201], [御茶園]特撰冰釀微甜綠茶 550ml(24入),
  * 符合:  2, [DRINK-001201], [御茶園]特撰冰釀微甜綠茶 550ml(24入),
  * 符合:  3, [DRINK-001201], [御茶園]特撰冰釀微甜綠茶 550ml(24入),


---------------------------------------------------
結帳金額:   $1,004.00

```

完全符合預期，這段 code 在不需要異動任何主程式的前提下，只是擴充了 ```TotalPriceDiscountRule``` 類別，以及在載入 Rules 將他排在最後順未加入清單，整個體系就串起來連動了，```POS``` 經過這樣調整後馬上可以計算出正確的折扣。



# 大亂鬥 - 挑戰更多折扣規則

解決第一個實際案例演練後，你可以開始回頭思考，如果你在工作上拿到一模一樣的 Requirement, 你是否也會用這樣的方式思考? 還是直接落入 "了解規格，然後歸納分類，接著就用一堆 if / else 或是 switch / case 開始實作起來" 的方法?

其實前面的案例很簡單，很多這樣設計的優點都還在封印內沒有解開。我接下來就舉幾個延伸的案例，讓大家深入一點體驗做好抽象化的威力。同樣的，後面所有的案例，我都維持同樣的原則:

> 我只擴充新的 Rule, 並且把它加到啟用的 Rules 清單內

只有你能堅持不為了 "新規則" 修改主流成的設計，規則的擴充才不會變成你的負擔。我就從前面到處蒐集來的各種折扣案例，挑幾個比較難搞的，來進行一個綜合測試吧!

我期望這些 POC 做完後，我能夠在同一筆交易內啟用這些折扣 (按照順序):

1. 指定商品 (衛生紙) 一次買 6 捲便宜 100 元
1. 指定商品 (蘋果) 單粒 23 元， 4 粒 88 元
1. 指定商品 (雞湯塊) 單盒特價 145 元，第二件 5 折
1. 指定商品 同商品 加 10 元多 1 件 (轉換: 同商品第二件 10 元)
1. 餐餐超值配, 指定鮮食 + 指定飲料 特價 ( 39元, 49元, 59元 )
1. 熱銷飲品, 限時優惠! 任 2 箱結帳 88 折!

<!-- 
我再額外追加一點規則，以上的折扣，如果有 "指定商品" 的條件出現，則不允許重複折扣。例如衛生紙已經是 "指定商品" 了，如果買 6 捲會享有折扣 -100, 這時最後的滿 1000 折 100 時就不應該再把這六捲衛生紙列入計算。但是如果我只買了 5 捲衛生紙，未符合指定商品折扣，則後面這 5 捲衛生紙就可以列入滿 1000 折扣的計算。

我相信這些規則，最難搞的就是這些限定商品跟互斥條件吧! 今天我們就一次把這些問題通通搞定。 -->




## 挑戰: 如何處理指定商品?

仔細看看這些規則，其實前四種都很類似，都是某些限制條件下的商品，符合購買的最低件數，就會有折抵現金、打折、或是優惠價格等等折扣。前面我們都沒有提到規則如何指定商品，這邊我們就花點篇幅來說明一下。

最典型的作法，要嘛替商品加上分類，然後折扣條件用分類來限定；或是設定折扣條件時，直接挑選符合的商品清單。兩種都沒有不好，但是都有麻煩的地方。第一種你的折扣規則會被商品分類所限制住，例如一種活動就需要建立一種商品，或是一種商品同時符合多種活動時，你的商品管理就會變得複雜...。

另一種就更麻煩了，當你商品數量一多的時候，建立活動就是建很痛苦的事情。挑選完活動上架後，你要是還有新的商品也要上架，同時加入折扣活動的優惠範圍內，那你要維護的工作就更多了...。

這邊我採用了雜貨店老闆常用的方式: 貼標籤!


我常在想，如果雜貨店老闆用低科技，都能很簡單的在結帳時搞清楚這些折扣，那為何系統不行呢? 傳統的雜貨店，沒有功能強大的 ```POS``` ，只有計算機而已，一樣能搞定這些優惠折扣。老闆只要事先在這些商品上面貼上標籤，說明這商品享有什麼折扣就可以了。不但客人看的清楚，老闆結帳時只要按照標籤一個一個算就可以了。同樣的情境，搬到系統上來比照辦理。先前 ```Product``` 類別定義保留的 ```Tags``` 現在派上用場了。我們用這機制替商品標上標籤，至於標籤的意義如何解讀，則交由 Rule 自行判斷。

舉例來說，第一條規則:

> 1. 指定商品 (衛生紙) 一次買 6 捲便宜 100 元

你可以在所有衛生紙的商品上，貼上 "買六捲折100!" 的標籤，或是貼上 "衛生紙" 的標籤，剩下的讓折扣規則自己去處理。認得這個標籤的折扣規則，自然會去處理。不認得的折扣規則應該就會忽略掉他，當作沒有貼任何標籤一樣的看待。同樣的 (2), (3) 這兩個折扣規則的限定商品，也都可以比照辦理 (只要標籤彼此錯開不要重複即可)。

第 (4) 個規則稍微有點不同:

> 4. 指定商品 同商品 加 10 元多 1 件 (轉換: 同商品第二件 10 元)

除了 "指定商品" 之外，還有限定 "同商品"。標籤可以負責 "指定商品" 的部分，而 "同商品" 則直接讓折扣規則本身去處理 SKU 即可。因此我們只要貼上 "同商品 加 10 元多 1 件" 即可，或是可以將標籤內容簡化一點，貼上 "同商品加購優惠" 就夠了。

至於第 (5) 個折扣規則:

> 5. 餐餐超值配, 指定鮮食 + 指定飲料 特價 ( 39元, 49元, 59元 )

如果我們有後面的規則可以搭配，那我只要貼上 "鮮食: 餐餐超值配(39元)" 以及  "飲料: 餐餐超值配(39元)" 就好了。一樣，識別標籤意義的部分交給後面的規則來接手，你也可以適度的簡化標籤內容: "餐餐超值配 39 / 鮮食" 、 "餐餐超值配 39 / 飲料"。

不過這折扣光是規則就沒那麼容易... 仔細看了一下活動規則，發現還真囉嗦:

![](/wp-content/images/2020-03-10-interview-abstraction/2020-04-02-22-09-02.png)

[來源網址](https://event.family.com.tw/food/39_49_59/)

(49 元貼標商品可加 10 元升級搭配 59 元飲品)
(可跨區任選 49、59 元鮮食，以咖啡或飲品價格決定餐促售價)

簡單的說，鮮食跟飲料都有分 39 / 49 / 59 三區，任意組合的話就按照飲料的價格為主。但是 39 元的不能跨區... 

例如:
- 39飲料 + 39鮮食 = 39 元
- 49飲料 + 49鮮食 = 49 元
- 49飲料 + 59鮮食 = 49 元
- 59飲料 + 49鮮食 = 59 元
- 59飲料 + 59鮮食 = 59 元

如果 39飲料 + 59鮮食 該怎麼算? 上面沒寫，我就當作不和折扣直接原價計算吧。

> 6. 熱銷飲品, 限時優惠! 任 2 箱結帳 88 折!

我直接沿用最前面的示範折扣，只要標記為 "熱銷飲品" 的標籤，湊滿兩箱就享有 88 折的折扣。不過如果你沒湊到剛剛好兩箱兩箱配對的話，就會有落單的飲料沒算進折扣了。這時挑選的順序就很重要。我補充一條規則，這種情況下就已對消費者最有利的情況來處理，從價格高的開始配對折扣。




## 綜合測試 - 生活用品採購

這些規則綜合起來運算的話，按照歸納法來開發，是得開上一堆欄位來描述啊... 不過為了凸顯抽象化的威力，我們就來寫看看怎麼處理這些折扣的 code。先來模擬一下，採買一些最近搶購的很兇的衛生紙，還有要配合居家隔離，我就多搬一點飲料吧。以下的商品資料，我實在掰不出來，我就順手在 PXHome 上面查一下這些品項跟價格，然後套用全X的折扣吧 (真是亂來)...

這次的購物清單如下 (```products3.json```):


```json
[
  {
    "sku": "TISU-00235",
    "name": "舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串)",
    "price": 179,
    "tags": [ "衛生紙" ]
  },
  {
    "sku": "TISU-00235",
    "name": "舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串)",
    "price": 179,
    "tags": [ "衛生紙" ]
  },
  {
    "sku": "TISU-00235",
    "name": "舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串)",
    "price": 179,
    "tags": [ "衛生紙" ]
  },
  {
    "sku": "TISU-00358",
    "name": "舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串)",
    "price": 139,
    "tags": [ "衛生紙" ]
  },
  {
    "sku": "TISU-00358",
    "name": "舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串)",
    "price": 139,
    "tags": [ "衛生紙" ]
  },
  {
    "sku": "TISU-00358",
    "name": "舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串)",
    "price": 139,
    "tags": [ "衛生紙" ]
  },
  {
    "sku": "SOUP-31423",
    "name": "《康寶》雞湯塊100g(10塊/盒)",
    "price": 45,
    "tags": [ "雞湯塊" ]
  },
  {
    "sku": "SOUP-31423",
    "name": "《康寶》雞湯塊100g(10塊/盒)",
    "price": 45,
    "tags": [ "雞湯塊" ]
  },
  {
    "sku": "FMCP-00102",
    "name": "FMC-小分子氣泡水",
    "price": 29,
    "tags": [ "同商品加購優惠" ]
  },
  {
    "sku": "FMCP-00102",
    "name": "FMC-小分子氣泡水",
    "price": 29,
    "tags": [ "同商品加購優惠" ]
  },
  {
    "sku": "FMCP-00102",
    "name": "FMC-小分子氣泡水",
    "price": 29,
    "tags": [ "同商品加購優惠" ]
  },
  {
    "sku": "FMCP-00102",
    "name": "FMC-小分子氣泡水",
    "price": 29,
    "tags": [ "同商品加購優惠" ]
  },
  {
    "sku": "FMCP-00102",
    "name": "FMC-小分子氣泡水",
    "price": 29,
    "tags": [ "同商品加購優惠" ]
  },
  {
    "sku": "DRNK-00159",
    "name": "《光泉》茉莉蜜茶300ml(24入/箱)",
    "price": 179,
    "tags": [ "熱銷飲品" ]
  },
  {
    "sku": "DRNK-01201",
    "name": "[御茶園]特撰冰釀微甜綠茶 550ml(24入)",
    "price": 400,
    "tags": [ "熱銷飲品" ]
  },
  {
    "sku": "DRNK-01201",
    "name": "[御茶園]特撰冰釀微甜綠茶 550ml(24入)",
    "price": 400,
    "tags": [ "熱銷飲品" ]
  }
]

```

如果你覺得 json 不大好看，我轉了一個表格版本的:


|SKU|NAME / #TAGS|PRICE|QTY|
|---|------------|----:|--:|
|TISU-00235|舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串) <br/>#衛生紙|$179|3|
|TISU-00358|舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串) <br/>#衛生紙|#139|3|
|SOUP-31423|《康寶》雞湯塊100g(10塊/盒) <br/>#雞湯塊|$45|2|
|FMCP-00102|FMC-小分子氣泡水 <br/>#同商品加購優惠|$29|5|
|DRNK-00159|《光泉》茉莉蜜茶300ml(24入/箱) <br/>#熱銷飲品|$179|1|
|DRNK-01201|[御茶園]特撰冰釀微甜綠茶 550ml(24入) <br/>#熱銷飲品|$400|2|




套用的折扣，就用上面列的那六項。現在來挑戰看看，只追加新的折扣規則，而不調整既有的購物車 code, 能否真正計算出最後的費用? 往下看結果之前，你可以先用心算算一次看看，你覺得結帳後應該是多少錢?

先來看看 code 算出來的結果:

```text

購買商品:
---------------------------------------------------
-  1, [TISU-00235]  $179.00, 舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串), #衛生紙
-  2, [TISU-00235]  $179.00, 舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串), #衛生紙
-  3, [TISU-00235]  $179.00, 舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串), #衛生紙
-  4, [TISU-00358]  $139.00, 舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串), #衛生紙
-  5, [TISU-00358]  $139.00, 舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串), #衛生紙
-  6, [TISU-00358]  $139.00, 舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串), #衛生紙
-  7, [SOUP-31423]   $45.00, 《康寶》雞湯塊100g(10塊/盒), #雞湯塊
-  8, [SOUP-31423]   $45.00, 《康寶》雞湯塊100g(10塊/盒), #雞湯塊
-  9, [FMCP-00102]   $29.00, FMC-小分子氣泡水, #同商品加購優惠
- 10, [FMCP-00102]   $29.00, FMC-小分子氣泡水, #同商品加購優惠
- 11, [FMCP-00102]   $29.00, FMC-小分子氣泡水, #同商品加購優惠
- 12, [FMCP-00102]   $29.00, FMC-小分子氣泡水, #同商品加購優惠
- 13, [FMCP-00102]   $29.00, FMC-小分子氣泡水, #同商品加購優惠
- 14, [DRNK-00159]  $179.00, 《光泉》茉莉蜜茶300ml(24入/箱), #熱銷飲品
- 15, [DRNK-01201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入), #熱銷飲品
- 16, [DRNK-01201]  $400.00, [御茶園]特撰冰釀微甜綠茶 550ml(24入), #熱銷飲品

折扣:
---------------------------------------------------
- 折抵  $100.00, 滿件折扣1 (衛生紙滿6件折100)
  * 符合:  1, [TISU-00235], 舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串), #衛生紙
  * 符合:  2, [TISU-00235], 舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串), #衛生紙
  * 符合:  3, [TISU-00235], 舒潔 棉柔舒適捲筒衛生紙(280張x12捲/串), #衛生紙
  * 符合:  4, [TISU-00358], 舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串), #衛生紙
  * 符合:  5, [TISU-00358], 舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串), #衛生紙
  * 符合:  6, [TISU-00358], 舒潔 萬用輕巧包抽取衛生紙(120抽x10包/串), #衛生紙

- 折抵   $22.50, 滿件折扣3 (雞湯塊第二件5折)
  * 符合:  7, [SOUP-31423], 《康寶》雞湯塊100g(10塊/盒), #雞湯塊
  * 符合:  8, [SOUP-31423], 《康寶》雞湯塊100g(10塊/盒), #雞湯塊

- 折抵   $10.00, 同商品加購優惠 (加10元多一件)
  * 符合:  9, [FMCP-00102], FMC-小分子氣泡水, #同商品加購優惠
  * 符合: 10, [FMCP-00102], FMC-小分子氣泡水, #同商品加購優惠

- 折抵   $10.00, 同商品加購優惠 (加10元多一件)
  * 符合: 11, [FMCP-00102], FMC-小分子氣泡水, #同商品加購優惠
  * 符合: 12, [FMCP-00102], FMC-小分子氣泡水, #同商品加購優惠

- 折抵   $96.00, 滿件折扣6 (滿熱銷飲品二件結帳9折)
  * 符合: 15, [DRNK-01201], [御茶園]特撰冰釀微甜綠茶 550ml(24入), #熱銷飲品
  * 符合: 16, [DRNK-01201], [御茶園]特撰冰釀微甜綠茶 550ml(24入), #熱銷飲品

---------------------------------------------------
結帳金額:   $1,929.50

```

答案跟你想的一樣嗎? 接著繼續來看，我如何在抽象化的規範之下，實作這幾個折扣吧! 我把有用到的折扣 source code 一個一個列出來看 (請看折扣那段輸出):

1. 首先，符合六件標記為 ```#衛生紙``` 的商品，獲得 $100.00 的折扣；接著符合兩件 ```#雞湯塊``` 的商品，獲得 $22.50 的折扣，這些都沒有問題。  

1. 再來，我的購物車內有五件標示 ```#同商品加購優惠``` 的商品，但是同商品第二件 10 元啊，因此只湊了兩組，得到 $10.00 的折扣兩次，剩下一件落單的就沒有折扣了。  

1. 最後，我搬了三箱飲料，都符合 ```#熱銷飲品``` 的條件，這邊我發現計算的順序會影響折扣的金額，因為是兩件 88 折，會落單一件。如果挑選對消費者有利的算法，應該是讓便宜的那箱落單，貴的兩箱優先湊折扣才是。這邊我以最佳折扣為前提，因此兩箱 $400.00 的挑出來套用折扣，獲得 $96.00 的折扣。

加總一下，最後結帳金額: $1929.50 ...



## 程式碼架構解析


接下來就看 code 該怎麼寫了。主程式都跟前面一樣，除了初始化購物清單跟折扣規則兩個地方之外，其他我都沒有改，我就不重貼了。程式碼有異動的地方如下:

1. 初始化折扣規則
1. 開發每個折扣規則的邏輯

先來看初始化的部分:

```csharp

static IEnumerable<RuleBase> LoadRules()
{
    yield return new DiscountRule1("衛生紙", 6, 100);
    yield return new DiscountRule3("雞湯塊", 50);
    yield return new DiscountRule4("同商品加購優惠", 10);
    yield return new DiscountRule6("熱銷飲品", 12);

    yield break;
}

```

原諒我偷個懶，我略過這次用不到的折扣，我只寫了 1, 3, 4, 6 這四個折扣活動... 初始化的部分沒啥好看的，按照順序填進去而已。重要的是後面的折扣開發方式。我英文不大好，程式設計師最痛苦的就是命名啊 T_T , 沒在國外生活過，這種生活英文實在不怎麼樣，我只好用 ```DiscountRule1``` 這種 code generator 生出來的命名了  XDD。




### 實作: 指定商品 X 件折扣 Y 元

來看第一個折扣: ```DiscountRule1```, 指定商品 (衛生紙) 一次買 6 捲便宜 100 元

```csharp

public class DiscountRule1 : RuleBase
{
    private string TargetTag;
    private int MinCount;
    private decimal DiscountAmount;

    public DiscountRule1(string targetTag, int minBuyCount, decimal discountAmount)
    {
        this.Name = "滿件折扣1";
        this.Note = $"{targetTag}滿{minBuyCount}件折{discountAmount}";
        this.TargetTag = targetTag;
        this.MinCount = minBuyCount;
        this.DiscountAmount = discountAmount;
    }

    public override IEnumerable<Discount> Process(CartContext cart)
    {
        List<Product> matched = new List<Product>();
        foreach(var p in cart.PurchasedItems.Where( p => p.Tags.Contains(this.TargetTag) ))
        {
            matched.Add(p);
            if (matched.Count == this.MinCount)
            {
                yield return new Discount()
                {
                    Amount = this.DiscountAmount,
                    Products = matched.ToArray(),
                    Rule = this
                };
                matched.Clear();
            }
        }
    }
}

```

看到目前為止，你可能會發現，這跟典型在 DB 內計算的思維其實完全不同啊，一路看下來，每個折扣規則的 code 真的都很平淡無奇，就是照著字面上的意思寫成 code 而已，但是這些折扣規則卻又很容易的被組合起來，讓 ```POS``` 能完成複雜的折扣計算! 這就是抽象化的威力啊，抽象化這層做的到位，你就能把很複雜的問題簡化到這種程度。

第一個折扣 ```DiscountRule1``` 就是把條件抽出來變成參數而以，折扣的對象只要是有標上 ```#衛生紙``` 這標籤的商品都算，符合的商品湊到 6 件，就折抵 100 元。這三個參數都透過 .ctor 取得，然後在 ```Process()``` 內挑出符合商品，用 for loop 湊滿 6 件後就傳回一筆 100 元的 ```Discount``` 物件。如果湊滿後還有剩，就繼續往下湊湊看是否能湊到第二組折扣。



### 實作: 指定商品第二件 N 折

接著看第三個折扣: ```DiscountRule3```, 指定商品 (雞湯塊) 單盒特價 145 元，第二件 5 折

```csharp

public class DiscountRule3 : RuleBase
{
    private string TargetTag;
    private int PercentOff;
    public DiscountRule3(string targetTag, int percentOff)
    {
        this.Name = "滿件折扣3";
        this.Note = $"{targetTag}第二件{10-percentOff/10}折";

        this.TargetTag = targetTag;
        this.PercentOff = percentOff;
    }
    public override IEnumerable<Discount> Process(CartContext cart)
    {
        List<Product> matched = new List<Product>();
        foreach (var p in cart.PurchasedItems.Where(p => p.Tags.Contains(this.TargetTag)))
        {
            matched.Add(p);
            if (matched.Count == 2)
            {
                yield return new Discount()
                {
                    Amount = p.Price * this.PercentOff / 100,
                    Products = matched.ToArray(),
                    Rule = this
                };
                matched.Clear();
            }
        }
    }
}

```

寫法有點千篇一律，跟前面的差不多，只是計算規則從固定金額改成打折而以... 我就略過不說明了。




### 實作: 同商品加 N 元多 1 件

第四個折扣: ```DiscountRule4```, 指定商品 同商品 加 10 元多 1 件 (轉換: 同商品第二件 10 元)

```csharp

public class DiscountRule4 : RuleBase
{
    private string TargetTag;
    private decimal DiscountAmount;

    public DiscountRule4(string tag, decimal amount)
    {
        this.Name = "同商品加購優惠";
        this.Note = $"加{amount}元多一件";
        this.TargetTag = tag;
        this.DiscountAmount = amount;
    }
    public override IEnumerable<Discount> Process(CartContext cart)
    {
        List<Product> matched = new List<Product>();
        foreach (var sku in cart.PurchasedItems.Where(p=>p.Tags.Contains(this.TargetTag)).Select(p=>p.SKU).Distinct())
        {
            matched.Clear();
            foreach(var p in cart.PurchasedItems.Where(p=>p.SKU == sku))
            {
                matched.Add(p);
                if (matched.Count  == 2)
                {
                    yield return new Discount()
                    {
                        Products = matched.ToArray(),
                        Amount = this.DiscountAmount,
                        Rule = this
                    };
                    matched.Clear();
                }
            }
        }
    }
}

```

還是一樣，差不多的邏輯，比較特別的是他限定 "同商品"，因此搜尋的 for loop 稍微變化了一下，第一圈先挑出購物車內有幾種 SKU 符合條件，然後再每種都掃一輪看看中幾組折扣。



### 實作: 指定商品 X 件 Y 折


第六個折扣: ```DiscountRule6```, 熱銷飲品, 限時優惠! 任 2 箱結帳 88 折!

```csharp

public class DiscountRule6 : RuleBase
{
    private string TargetTag;
    private int PercentOff;
    public DiscountRule6(string targetTag, int percentOff)
    {
        this.Name = "滿件折扣6";
        this.Note = $"滿{targetTag}二件結帳{10 - percentOff / 10}折";

        this.TargetTag = targetTag;
        this.PercentOff = percentOff;
    }
    public override IEnumerable<Discount> Process(CartContext cart)
    {
        List<Product> matched = new List<Product>();
        foreach (var p in cart.PurchasedItems.Where(p => p.Tags.Contains(this.TargetTag)).OrderByDescending(p=>p.Price))
        {
            matched.Add(p);
            if (matched.Count == 2)
            {
                yield return new Discount()
                {
                    Amount = matched.Sum(p => p.Price) * this.PercentOff / 100,
                    Products = matched.ToArray(),
                    Rule = this
                };
                matched.Clear();
            }
        }
    }
}

```

還是一樣沒幾行，唯一一個要注意的就是: 若要以消費者最優惠的角度來計算，我在湊折扣時先用售價來排序，從價格高的開始湊折扣... 其他還是一樣的做法。



## 大亂鬥 - 小結

整個計算看到這邊，你體會到抽象化的威力了嗎? 最前面的 RuleBase 這邊，決定好抽象化的範圍，把主程式 (```POS``` 端) 結帳的流程固定下來之後，其他折扣規則都靠抽象類別 ```RuleBase``` 隔開，分別繼承後補上各別的實作，就完成了...。

這才是抽象化的威力啊，關鍵的一刀切對地方，整組程式碼的複雜度瞬間下降到初學者都能搞的定的層級，你不需要懂很多技巧就能完成這個計算需求。物件導向最具威力的就是這種情境，面對多樣的複雜度，如果你能在思考架構時做出正確的抽象化，那麼搭配 OOPL 的對應語法，你能夠不費吹灰之力就把這樣複雜的計算寫成 code. 這是其他程序性語言所遠遠不及的。我相信有用 store procedure 做過類似計算的朋友們，大概就可以理解我的想法了。

這邊我特地花了不少篇幅，把抽象化思考的觀念，到實作案例，都從頭到尾跑了一遍，親自示範面面俱到的作法應該怎麼做。






# 進階挑戰 - 配對折扣 & 折扣排除

我保留一點彩蛋給耐心看到這裡的朋友們 XDD, 眼尖的朋友可能會發現，我還有一個折扣規則 (鮮食 + 飲料 搭配折扣) 沒有實作啊!! 我的目的是在這邊停頓一下，讓各位有點時間思考一些架構問題。是不是 "所有" 的折扣規則，都不需要更動主程式就能擴充? 其實並不完全這樣。我這邊就保留了兩個正反兩面的案例，讓大家思考看看。



其中一個是正面的例子，就是上面大亂鬥中的第 (5) 項:

> 5. 餐餐超值配, 指定鮮食 + 指定飲料 特價 ( 39元, 49元, 59元 )

這是跟前面其他折扣比起來，是個相對複雜的 case, 不過你只要能在 RuleBase 的規範下寫出實作，掛上主程式，其實一點都不難。這邊有些技巧 (商品標籤的標示方式) 要想一下，還有那個折扣規則包含加價可以搭配高一階的商品也要留意...，其他就沒什麼困難的了。

另一個例子是反面的 (沒辦法只靠擴充規則): 如果我的折扣規則，已經跨出我抽象化的那個邊界了呢? 舉例來說，我如果想要指定某些商品，在享用 A 折扣後，如果還符合 B 折扣活動，我想要讓他折上加折是否有辦法? 或是我摳一點，已經享有 A 折扣之後，即使符合條件，你也必須放棄 B 折扣的優惠... 

類似像這樣的擴充規格，已經屬於多個折扣規則之間的交互作用了，這樣的結帳程式又該如何在這樣的架構下擴充進行，你的抽象化的邊界又應該訂定在什麼地方?



這實作我就先保留一下，我留點時間讓大家思考。我打算再開放一次讓大家發 PR 的機會，歡迎有興趣的朋友歡迎發 PR 給我。規則跟之前相同，我預計 2020/05/01 00:00 勞動節截止收件。在那之前給我 PR 的朋友們，你們的 code 我會放在文章內解說，並且給各位我的 feedback 當作回報。這次是架構題，結果只有結帳金額正不正確一種而已，剩下就是相對主觀的 code 夠不夠簡潔漂亮，不像之前還有 benchmark 等等比較的標準。寫法的好壞，我就保留我自己個人主觀認定了。

這篇文章的 source code, 我都放在我的 GitHub Repo: [Andrew.DiscountDemo](https://github.com/andrew0928/Andrew.DiscountDemo) 內，歡迎取用! 有興趣挑戰看看的朋友們歡迎發 PR 給我~



# 進階挑戰 (預計 5/1 補完)










# 小結

雖然我最後文章留了段尾巴，不過我還是先做個小結吧! 我一直很推崇 OOP，雖然很多人都說現在 OOP 已經不流行了 blah blah ..., 我自己是不這麼認為的，因為 OOP 是你如何用運算的角度來看待現實世界的一種觀點啊。抽象化，就是 OOP 的核心，適度的把事物抽象化，你就能用更精簡的方式來描述這個世界。描述的越精確，你的 code 就越能跟實際的世界對應。對應帶來的好處就是直覺，一旦你要處理的問題有任何變化，因為完整的對應了，你的 code 就能夠很容易的適應變化。

也許你會說，現在 OOPL 越來越不是主流了啊，主流的語言如 Python, Go, Java Script 等等，都不算是 OOPL 啊! 不過我強調的是 "精神" 啊，你不用 OOPL，你總會面對到 API 吧? 任何扯到 "介面" (interface) 或是 "約定" (contracts) 的機制，核心觀念還是會回到抽象化。把 interface 找出來並且先定義好他，永遠都是資訊界的關鍵，不論軟硬體都一樣。定義 interface 的過程其實就是抽象化，只不過 OOPL (如: C# or Java) 更積極地把這樣的觀念融入語言本身而已。

這次，我挑了一個所有購物網站都很頭痛的問題: 折扣計算 來當作範例。因為他夠令人頭痛，而他也在現實世界運作的夠普遍，因此背後應該是有些脈絡可循的。你能掌握到他的關鍵，你就能做好抽象化。抽象化的能力如果到位，你就會發現你的程式碼瞬間變得簡單易懂好維護。這不就是所有軟體工程師追求的願景嗎? 其實這一點都不難啊，只要你在解決問題前有好好的思考。

希望藉由這個例子，還有這些 sample code, 我能用很簡單的邏輯，用很少量的程式碼就把這個折扣計算的問題解決掉，就是要證明抽象化思考的重要性。好好思考程式碼的結構，帶來的效果，絕對比你亂寫一通後再來優化有效! 經過仔細思考，用更簡單的方式解決問題，這樣的精簡才真正的會發揮效益，包括速度快，程式碼好理解，好維護等等。讓系統保持簡潔，才是所有軟體工程追求的極致! 希望這篇文章能讓大家體會到這點 :)



