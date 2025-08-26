---
layout: post
title: "[設計案例] 生命遊戲 #6, 抽像化 (Abstraction)"
categories:
- "系列文章: 生命遊戲"
tags: ["C#","Tips","技術隨筆","物件導向","系列文章: 生命遊戲"]
published: true
comments: true
redirect_from:
  - /2009/10/03/設計案例-生命遊戲-6-抽像化-abstraction/
  - /columns/post/2009/10/03/e8a8ade8a888e6a188e4be8b-6-e68abde5838fe58c96.aspx/
  - /post/2009/10/03/e8a8ade8a888e6a188e4be8b-6-e68abde5838fe58c96.aspx/
  - /post/e8a8ade8a888e6a188e4be8b-6-e68abde5838fe58c96.aspx/
  - /columns/2009/10/03/e8a8ade8a888e6a188e4be8b-6-e68abde5838fe58c96.aspx/
  - /columns/e8a8ade8a888e6a188e4be8b-6-e68abde5838fe58c96.aspx/
wordpress_postid: 27
---

原定 [#4](/post/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b2-4-e69c89e69588e78e87e79a84e4bdbfe794a8e59fb7e8a18ce7b792.aspx) 就提到的 "抽像化"，竟然被我連拖兩期，拖到 #6 才提到它... 人老了果然比較囉唆... 在前面的幾篇，重點都在如何 "具體" 的描述 "生命遊戲" 裡的細胞。不過現在要把這程式擴大到能容納各種不同的生物，先作好抽像化的工作是必要的...。

一般物件導向所指的 "抽像化"，是指你對某些事物的一般概念。比如有人問你:

*"你會開車嗎?"*

你腦袋裡想的應該是一般印像中的車子，有方向盤，排檔打下去，油門踩了就會前進，煞車踩了就會停下來...，這就是你對 "車子" 的抽像化。你不會去管車子是什麼牌的，什麼顏色，是二門跑車，或是休旅車之類的細節... 而你 "會" 開的車，也不會因為這些細節，有太大的不同。

這樣的抽像化概念，套用到考駕照這件事來說，你只要知道方向盤，油門等等的用法，同時也練習過，能正確的控制教練車，通過測驗，監理所就會發張駕照給你，證明你會開一般的車子。就算是在你學會開車後十年才上市發表的新車也是一樣。

看起來沒什麼了不起的描述，在電腦的世界裡可不是這麼一回事。Microsoft Word 1.0 想要順利開啟 Microsoft Word 6.0 的檔案，大概想都不用想，因為 1.0 版設計之初，有太多 6.0 版的變化是無法事先預料的，自然無法設計出能正確操作的程式，這現像在電腦的世界很正常。不過如果你兩年前考到的駕照，碰到兩年後的新車你就不會開了，甚至監理所還要求你重考張新的架照... 那這駕照等於一點用都沒有。中間的差別，就在於駕駛者對於開車的認知，跟實際的車子，中間是隔著一層 "抽像化" 的概念，而只要能掌握這抽像化的定義，就能順利操作未來的車種。

因此物件技術不斷的想要模擬這樣的關係，就發展出繼承這樣的方式，來表達這個概念。先用一個類別 (base class) 或是介面 (interface) 來表達這個 "抽像化" 的概念，而不表達細節。其它要跟它互動的程式，只能透過這個抽像化型別來溝通，而其它的細節或實作，則被藏在裡面，或是衍生類別。中間的故事我就不再多說了，再說我就直接去寫 OOP 的書好了 =_=，有興趣可以參考這本經典 [[世紀末軟體革命](/post/e4b896e7b580e69cabe8bb9fe9ab94e99da9e591bde5bea9e588bbe78988.aspx)]，有復刻版喔。套用到我們的 "生命遊戲" 裡，要定義的就是 "世界" 如何跟 "生命" 互動? 之間的關係是什麼? 另外就是 "生命" 有各種不同的型態，所有的 "生命" 型態是否都能順利的在同一個 "世界" 裡生存?

先試著用簡單文字來描述吧。在我們的定義裡，世界是個 M * N 的棋盤，每一格都能放一個生物。每個生物有自己的狀態 (生/死)，也會隨著時間與環境的不同，讓生物的狀態產生變化。畫成 UML 的 class diagram, 大概就像這樣 (手邊沒工具，用 power point 大概畫一下… Orz):

![image](/images/2009-10-03-design-case-study-game-of-life-6-abstraction/image.png)

我們在撰寫程式時，就必需思考題目中講到的生物各種特性，那些是所有的生命共有的特色? 這部份要把它定義在 Life … 另一部份是某種細胞特有的，則要放在衍生類別 Cell 裡。而世界必需要能跟生命作適當的互動，讓生命的進行能繼續下去。這樣的架構好處是，未來如果有第二種 Cell 或是其它的生物，只要是從 Life 繼承下來，都能很順利的在 World 裡活著，因為物件導向技術的 "抽像化" 概念，保證這樣程式的可行性。

好，我們就以需要跟 World 接觸跟互動的部份為主，把原程式的 Cell 抽離出來，放到它的上層類別 Life 裡。這也是物件技術裡常提到的 "generalization" (一般化)，越一般的特性要越往上層類別移動，而越往下就是 "specialization" (特殊化)，底層的類別要去實作特殊的部份，或是特有的細節。

先把原程式作好調整吧。原 Cell 的程式碼，部份被搬移到 Life, 同時這兩個類別有了繼承關係，如下:

![ClassDiagram1](/images/2009-10-03-design-case-study-game-of-life-6-abstraction/ClassDiagram1.png)

Life 的部份，定義了所有 Life 都該表達出來的特性，也就是我們對於 Life 的認知，都應該描述在裡面，像是 Life 活在 World (CurrentWorld) 裡，會有它的座標 (PosX, PosY), 也會有它在這個棋盤內顯示的方式 (DisplayText) 等。而跟 World 互動的方面，Life 則透過 GetNextWorldTask( ) 來讓 World 來讓 Life 驅動它生命的進行。

在 World 的這邊，不管是那種 Life 衍生類別的物件，一律都當成 Life 的 "抽像概念" 來操作。這樣的優點，在還不曉得未來這世界到底還有多少種不同的 Life 會在裡面生活時，主要程式就能開發了。未來 Life 可以一直擴充，衍生出多種不同的 Life 子類別，而 Life / World 之間的互動及規範，則可以完全不用修正。

接下來就要讓這遊戲的規則，變的更真實一點了。實際的情況下，應該是我們已經知道會有那些不同的生物，經過歸納 (一般化及特殊化) 之後，可以設計出我們需要的類別架構。不過實際寫起程式來可沒這麼好命 (就像 USER 永遠不會一次給你完整確定的需求一樣)，很多時後你得去 "猜" 或是 "假設"，因此跟本沒有 "一般化" 這回事，你得預先去猜測未來要應付什麼問題，而在細節都還不清楚時就先定義出上層類別。

我們開始來試看看，我們定義的夠不夠抽像吧! 如果助教看你這麼快就把生命遊戲的作業交出來，覺的很沒面子，想把題目變難一點，加上有病毒感染的情況。於是原題目的四條規則追加一條，變成這樣:

1. *孤單死亡：如果細胞的鄰居小於一個，則該細胞在下一次狀態將死亡。*
2. *擁擠死亡：如果細胞的鄰居在四個以上，則該細胞在下一次狀態將死亡。*
3. *穩定：如果細胞的鄰居為二個或三個，則下一次狀態為穩定存活。*
4. *復活：如果某位置原無細胞存活，而該位置的鄰居為三個，則該位置將復活一細胞。*
5. ***感染：正常的細胞有 ( 1 + 受感染的鄰居數量 x5 )% 的機率受到病毒感染。已感染的細胞在 3 次狀態改變後會痊癒。受感染的狀況下，有 10% 的機率會死亡。***

我們的程式該怎麼配合它改變? (對，機車的 USER 就都是這樣臨時修改規格...) 先來看看執行的結果，畫面上已經分的出來活著的 Cell 跟受感染的 Cell ... 除了看到 Cell 活著與死亡的變化之外，也看的到病毒擴散的狀況是怎麼樣。執行的畫面如下:

![image](/images/2009-10-03-design-case-study-game-of-life-6-abstraction/image.png)

圖例: ◎受感染的細胞，●活著的正常細胞，○死亡的細胞

接著，來看看改版後的程式碼:

```csharp
public bool IsInfected
{
    get
    {
        return this.InfectedCount > 0;
    }
}
private int InfectedCount = 0;
public override string DisplayText
{
    get
    {
        if (this.IsAlive == true) return "●";
        else if (this.IsInfected == true) return "◎";
        else return "○";
    }
}
protected override IEnumerable<TimeSpan> WholeLife()
{
    yield return TimeSpan.FromMilliseconds(_rnd.Next(800, 1200));
    for (int index = 0; index < int.MaxValue; index++)
    {
        int livesCount = 0;
        int infectsCount = 0;
        foreach (Cell item in this.FindNeighbors())
        {
            if (item.IsAlive == true) livesCount++;
            if (item.IsInfected == true) infectsCount++;
        }
        bool? value = _table[this.IsAlive ? 1 : 0, livesCount];
        if (value.HasValue == true)
        {
            this.IsAlive = value.Value;
        }
        if (this.IsInfected == true)
        {
            this.InfectedCount--;
            if (this.InProbability(10) == true) this.IsAlive = false;
        }
        else
        {
            if (this.InProbability(1 + infectsCount * 5) == true) this.InfectedCount = 3;
        }
        yield return TimeSpan.FromMilliseconds(_rnd.Next(800, 1200));
    }
    this.Dispose();
    yield break;
}
```

細節我就不多介紹了。這裡的重點是經過抽像化的動作後，把 Life / Cell 之間的邏輯做明確的劃分。World 的類別程式碼完全沒有出現任何有關 Cell 的 Code, 只有出現 Life 而已。除了在主程式 GameHost 有這麼一段，明確的把 Cell 建立起來，把它放進 World:

```csharp
static void Main(string[] args)
{
    int worldSizeX = 30;
    int worldSizeY = 30;
    World realworld = new World(worldSizeX, worldSizeY);
    Random _rnd = new Random();
    for (int x = 0; x < worldSizeX; x++) {
        for (int y = 0; y < worldSizeY; y++) {
            Cell item = new Cell();
            realworld.PutOn(item, x, y);
        }
    }            
    // ...

}
```

這樣的作法，其實已經引含了 "動態聯結" 的特性了。在開發主程式的階段 (指 World / Life 這兩個主要的 class), 都還沒有 Cell 的相關細節，而事後執行的程式碼卻可以依照 Cell 裡的邏輯來執行。這代表了我們不需要改主程式的設計，就能不斷的加入新的規責，甚至是新的生物進來一起運作。

如何? 物件技術的 "抽像化" 能力，的確很有效的解決了這樣的變化需求。下一篇會沿用一樣的架構，但是執行的範例會完全不一樣 (這次不用細胞了，直接用草原上的生態: 草、羊、虎) 的生命及規則，來套進這個框架，看看它能怎麼模擬出一個新的生態系統。

這樣的架構可以應付未來未知的變化，只要你的抽像化概念不變的前題下都沒問題。這種保留彈性，卻又不用在 design time 去多做不必要的實作，才是物件技術強大的地方。我舉個反例，很多剛入行的軟體工程師，你給他一個需求，他會想太多... 一個簡單的輸入 1 + 1 要顯示 2 的結果，他會這麼想:

*USER 需不需要列印啊? 我先把這需求放進去好了，然後加個 config 預設關掉它，以免以後需要我還得大改程式...*

*只能算 1 + 1? 如果以後 USER 要算 3 * 5 怎麼辦? 好吧，我把 + 用一個 mode 來代表好了，以後 USER 需要括充為支援 +-*/ 就不用大改程式了...*

...

碰到這些狀況，我只能誇獎這位年青有為的程式設計師一句話:

*"你很認真... 辛苦了..."*

不過我心裡會苦笑... 只不過要你寫個 1 + 1 = 2，搞這麼一大包? 多作考慮，預留未來可能需要的功能，不是件壞事。不過既然是未知的需求，你又如何保證你能夠正確的 "預知" ，然後進一步 "預留" ? 何況這些多做的需求，未來真正會用上的有多少? 用不到的話，只是開發成本的浪費，及讓你的架構複雜性提高，維護的困難增加而已。物件技術真的解決的了這種問題嗎? 下一篇的目標，我們會定在不修改 World / Life 的設計為前題，把生命遊戲的模擬內容換成草原的生態模擬。敬請期待續集 :D
