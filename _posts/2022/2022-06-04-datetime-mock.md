---
layout: post
title: "[架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用"
categories:
- "系列文章: 架構師的修練"
tags: ["系列文章", "架構師的修練", "刻意練習", "UnitTest", "PoC"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: /wp-content/images/2022-06-04-datetime-mock/2022-05-29-00-57-25.png
---

![](/wp-content/images/2022-06-04-datetime-mock/2022-05-29-00-57-25.png)
圖片來源: [動畫瘋, SPYxFAMILY #4](https://ani.gamer.com.tw/animeVideo.php?sn=29007)


這篇不打算寫那麼長，短篇就好，先聊聊一些比較直覺的實做技巧，同時也當作 PoC 這主題的起點。我想聊聊一件事: 就是在單元測試 / PoC (Proof Of Concept) 的過程中，怎麼處理 ```DateTime.Now``` 難以控制預期結果的問題?

```DateTime.Now``` 會傳回系統目前的時間，不過這很難預測 (你不知道何時程式才會啟動啊)，這也讓依賴 ```DateTime.Now``` 開發的程式碼難以精準的測試。要解決的方法也不難，只要用這些關鍵字 (**C#**, **DateTime**, **Mock**) 到 Google 查一下，應該就可以查到一堆。不過，如果只是要在單元測試過程中掌控 ```DateTime.Now``` 的行為，其實這樣就夠了。我在思考系統設計過程中，很常用 PoC 的技巧，也常常會面對時間的問題啊... 隨便舉個例子:

> 系統在接受客戶的訂單時，會立即傳送確認訊息，同時會排定在每個月 15 日的 02:00, 更新月結報... blah blah ...

如果我要寫這樣的 code, 難道每次測試或是 demo 都得要等一天嗎? 或是我就真的得調整系統時間嗎? 如果這些場合還有面臨 UI 等等元素的介入 (不只是單元測試)，我該怎麼做?

因為有這些延伸的需求 (反正 ```DateTime``` 的處理也不複雜)，我就決定捲起袖子自己弄了...


<!--more-->

# 前言: DateTime.Now 的問題

最主要的問題只有一個，就是 ```DateTime.Now``` 是 ```static property```, 你完全沒有機會用 "**正規**" 的手段換掉他啊... 當你在你的 code 內插入這段，就代表你告訴編譯器，我要呼叫 ```System.DateTime``` 這個 ```class``` 的 ```static property``` 的 ```get``` 來取得目前系統的時間。所謂的 ```static```, 就完全是靜態連結了，你完全沒機會用 dependency injection, 用 wrapper 等等技巧在不之不覺的情況下替換掉它...

找了一下 Google / Stackoverflow 上的各種做法，手段技巧各有不同，不過大都是讓 ```DateTime.Now``` (或是替換的 method) 從原本的行為 (傳回系統目前時間) 替換成可控制的行為 (測試啟動前設定的固定時間) 為主。

不過我希望能同時解決 PoC 的需求，除了把 ```DateTime.Now``` 傳回能掌控的時間之外，我還額外希望傳回值還是能跟著時間流動而變化 (例如程式執行一分鐘後，能傳回多一分鐘的數值回來)，另外我也想能夠連動的解決透過時間觸發的事件 (例如 ```System.Timer```)。


也因此，你可以找的到的 solution (用我上面的關鍵字: [C#, DateTime, Mock](https://www.google.com/search?q=C%23%2C+DateTime%2C+Mock&oq=C%23%2C+DateTime%2C+Mock&aqs=edge.0.69i59j0i512j0i8i30l5j69i58j69i64.372j0j1&sourceid=chrome&ie=UTF-8)) 找的到的方法，大致上有這三類:

1. 自己刻一個替代品, 例如 ```SystemTime.Now``` 這類做法。沒有改變架構，就單純是個你能控制的替代品
1. 用 interface 將 ```DateTime.Now``` 設計成可抽換的, 例如 ```IDateTimeProvider``` 這類的作法
1. 用 [Microsoft Facks](https://docs.microsoft.com/en-us/visualstudio/test/code-generation-compilation-and-naming-conventions-in-microsoft-fakes?view=vs-2022) , 透過 runtime 重新編寫的技巧, 來替你攔截原本呼叫 ```System.DateTime``` 的動作。


其中，(3) 看起來是最理想的方案 (因為你完全可以不用改你的 code)，但是也是我最不想用的方法。感覺做法不大~~優雅~~俐落啊，他就像葉克膜一樣，全身插了一堆管子，來達到目的，實在太不優雅了。也因為他動用到 runtime 環境，使用上也有些限制。一來環境需要 Visual Studio Enterprise Edition, 二來也會影響效能, 這些因素限制了他大概只適用於 unit test .. 對於我額外的 PoC 需求就有點力不從心了。不過, Microsoft 提供的這套 Fake Assembly 技巧也蠻有趣的, 還是值得了解一下啦，這邊我就貼連結跟 sample code 就好。簡單的說，就是在 ```ShimsContext``` 的範圍內，用固定的命名原則告訴 ```ShimsContext``` 你要攔截那些 method call, 並且換成你自己的 delegate:

* Reference Docs: [Using shims to isolate your application from other assemblies for unit testing](https://docs.microsoft.com/zh-tw/previous-versions/visualstudio/visual-studio-2015/test/using-shims-to-isolate-your-application-from-other-assemblies-for-unit-testing?view=vs-2015)


參考一段文章上的 Sample Code:

```csharp

[TestClass]
public class TestClass1
{
    [TestMethod]
    public void TestCurrentYear()
    {
        int fixedYear = 2000;
        using (ShimsContext.Create())
        {
            // Arrange:
            // Detour DateTime.Now to return a fixed date:
            System.Fakes.ShimDateTime.NowGet = () => { return new DateTime(fixedYear, 1, 1); };

            // Instantiate the component under test:
            var componentUnderTest = new MyComponent();

            // Act:
            int year = componentUnderTest.GetTheCurrentYear();

            // Assert:
            // This will always be true if the component is working:
            Assert.AreEqual(fixedYear, year);
        }
    }
}

```

剩下的 (1) 跟 (2) 實做方式各有優缺點，說實在話我的事業沒有大到要抽換多個不同的實做，但是如果能用很低的修改成本就做到能抽換的擴充性也不是壞事，最後我就自己實做一個折衷的版本了。跟上面列的三種實做方式不同，我另外找到了這篇文章，講了四種對應的策略。如果你對系統的設計有興趣，這篇文章不長，值得看一看。除了看他的做法，也可以看看作者的使用時機:

* Reference Docs: [4 Golden Strategies for Unit Testing DateTime.Now in C#](https://methodpoet.com/unit-testing-datetime-now/)

文中提到的 4 golden strategies 就是這四個:

> The most popular strategies for unit testing DateTime.Now in C# are:
> 
> 1. An interface that wraps the DateTime.Now
> 2. SystemTime static class
> 3. Ambient context approach
> 4. DateTime property on a class

跟前面 google 到的三大類方法，前兩個是重疊的，Microsoft Fakes 沒在上面的行列之中，後面兩種我覺得可以解讀成上面兩種做法的封裝技巧。我最終採用了 (3) 這個策略，就是 **Ambient context approach**. 不過我的做法跟他的 sample code 完全不一樣 XDD，我的 code 老早就寫好了，只是在寫文章時才發現這篇參考，正好他的描述比我精準的多，我就拿來參考而已。


# 設計: DateTimeUtil 介面定義

我先把我自己手刻的這個類別 ```DateTimeUtil``` 的簽章先貼一下好了，這樣後面說明比較清楚:

```csharp

public class DateTimeUtil
{
    public static DateTimeUtil Instance => _instance;
    public static void Init(DateTime expectedTimeNow) { ... }
    public static void Reset() { ... }

    public event EventHandler<TimePassEventArgs> RaiseDayPassEvent;
    public DateTime Now { get { ... } }
    public void TimePass(TimeSpan duration) { ... }

    // 以下的 method 只是為了使用方便的 method, 非必要。
    public void TimePass(DateTime expected) { ... }
    public DateTimeUtil GoNextDays(int days = 1) { ... }
    public DateTimeUtil GoNextHours(int hours) { ... }
}

```

我的目的是希望，他能夠像 ```DateTime.Now``` 一般，我不用特別注入或是傳遞物件，隨時就能取得目前的時間 (這也是 ```System.DateTime``` 採用 static property 最主要的動機)。我採取的是把它依附在特定的 context 下，在當下的環境能取得唯一的 instance. 按照慣例我應該命名為 ```DateTimeProviderContext.Current``` 這樣的用法，不過我的情境下就只有一個 context 啊 (就是整個系統)，因此我決定採用 singleton pattern 的想法來實做它, 弱化了 context 的想法, 直接用 ```DateTimeUtil.Instance``` 來替代。

抽換實做我就不提供了，反正我都有足夠的控制能力了，這架構下以後要抽換，只要換掉實做跟擴充 ```Init(...)``` 就夠了，這階段多餘的設計就先省掉。

跟單元測試用途，最大的不同是: 單元測試大多是 "讓時間凍結在指定的地方" 為目的，例如我要測試 Y2K 問題，我就讓所有的 ```DateTime.Now``` (或是對等的語法) 都固定傳回 ```2000/01/01 00:00:00``` 的數值。但是我有 PoC 的用途，我只希望鎖定程式啟動的時間是在固定的時間點，但是如果程式跑了 30 sec, 我會希望 ```DateTimeUtil.Instance.Now``` 傳回的是 ```2000/01/01 00:00:30``` 才對。這樣產生的資料，列印出來的訊息，記錄下來的 Log 等等時間欄位才有意義。



回顧一下，我在文章最前面描述的情境:

> 系統在接受客戶的訂單時，會立即傳送確認訊息，同時會排定在每個月 15 日的 02:00, 更新月結報... blah blah ...

另一個需求，就是能像時光機一樣，讓我直接穿梭到指定的時間點。比如上述的例子，我希望在操作下單時是正常時間，操作完之後能瞬間切換到下個 15 日 01:59 .. 這穿梭能力就是對應到 ```DateTimeUtil.Instance.TimePass(...)``` 這 method 身上了。

最後一個，是我可能在測試時，直接跳到三個月後。如果按照系統設計，應該這三個月之間每個月 15 日都該產生一份報表才對啊，我希望做時光跳躍時，這些過程仍能夠被精準的執行，因此在思考實做方式之前，我先思考怎麼定義他的 interface... 我決定用 event 的機制來觸發定期執行任務，只要在 ```TimePass(...)``` 的過程中能按照規矩觸發，這問題就解決了。因此為了這個目的，我定義了這個事件: 


```csharp

public event EventHandler<TimePassEventArgs> RaiseDayPassEvent;

```

對應的 ```EventArgs``` 長這樣，就是標記這次事件 "**應該**" 觸發的時間 (非 "**實際**" 觸發。可能有些微的延遲才合理):


```csharp

public class TimePassEventArgs : EventArgs
{
    public DateTime OccurTime;
}

```

通常，時間只會往前進，不會往後退的。如果能倒退，就天下大亂了啊 (時間到流，資料該回覆嗎? 已經觸發過的事件該重新觸發嗎?) 因此，```TimePass(...)``` 不接受時間倒流的要求。唯一能夠倒流的機會是整個重新 ```Reset(...)``` 並且重新 ```Init(...)``` 一次才行。當然這並不會解決前面的問題，只是明確的定義 interface 如何執行這件事，用 ```Reset(...)``` 讓用的人知道，這是整個重來了，不不是時光倒流。你要有清除或是還原環境的配套準備。

題外話，還記得[上一篇](/2022/04/25/microservices16-api-implement/#%E5%96%AE%E5%85%83%E6%B8%AC%E8%A9%A6%E6%A1%88%E4%BE%8B)的案例嗎? (認真調查有多少人看過上一篇落落長的文章...) 上一篇在交代 JWT 的 token 驗證，文內提到我預先產生的 token 期限我只發了三年... (意思是該單元測試三年後就會失敗了)


[上一篇](/2022/04/25/microservices16-api-implement/#%E5%96%AE%E5%85%83%E6%B8%AC%E8%A9%A6%E6%A1%88%E4%BE%8B)有這麼一段測試案例:

```csharp

[TestInitialize]
public void Init()
{
    this._repo = new MemberRepo();
    this._fsm = new MemberStateMachine();

    // token, user | webui | 2022/04/04 ~ +3 years
    MemberServiceToken token = MemberServiceTokenHelper.BuildToken("eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA");
    MemberService service = new MemberService(token, this._fsm, this._repo);

```

這段測試案例，由於預先產生的 JWT token 期限已經被限定在 ```2025/04/04``` 會失效，所以三年後這測試就會失敗了。這當然是很不妥的作法，當時我刻意忽略，只是不想讓已經寫不完的文章變得更肥而已。套用我現在的做法的話，這段測試應該加上:


```csharp

[TestInitialize]
public void Init()
{
    //
    //  NOTES: 加上這段, 設定測試情境的啟動時間點 (只針對 DateTimeUtil 有效)
    //
    DateTimeUtil.Init(new DateTime(2022, 05, 01, 00, 00, 00));

    this._repo = new MemberRepo();
    this._fsm = new MemberStateMachine();

    // token, user | webui | 2022/04/04 ~ +3 years
    MemberServiceToken token = MemberServiceTokenHelper.BuildToken("eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJVU0VSIiwic3ViIjoiV2ViVUkiLCJqdGkiOiJFNTMyM0FBNTU4MjY0OUQ3QUJDOUZFODQxMjkwMDFDMiIsImlhdCI6MTY0ODk5Njc0MS42MDQ1MTY1LCJleHAiOjE3NDM2OTExNDEuNjA0NzE2fQ.RynDs43NEjMXfnMPbAKqEr2MBqI1oub2X-4xEuve5Q21tMYcZAXPn60fe0wdJLO0uJUAeRTxS0HdBOR70zmAsA");
    MemberService service = new MemberService(token, this._fsm, this._repo);

    //
    // NOTES: 將執行環境 (Context) 的時間切到 5 年後..
    //
    DateTimeUtil.Instance.TimePass(TimeSpan.FromYears(5));

    // token 驗證會失效 ...

```


# 實作: Code Review

其實實做沒有太特別的地方。我花最多心思的地方都在前一段， ```DateTimeUtil``` 應該設計成什麼樣子，該怎麼被使用了。剩下的幾行 code 就搞定。大部分為了單元測試設計的 DateTime Mock, 大都回傳固定時間，因此內部設計自然是儲存那個時間的數值就結束了。我的期待有兩個:

1. ```DateTimeUtil.Instance.Now``` 要隨真實時間的移動而有所變化
1. ```DateTimeUtil``` 不論是真實時間的移動，或是手動指定 "**快轉**" ```TimePass()```, 都要在每日凌晨觸發事件

因此，內部結構我這樣設計:

1. 紀錄修正的時間差 ```TimeSpan _realtime_offset```:  
由於時間要隨著真實時間跟著移動，因此我儲存固定的 "時間差"，而非儲存我在 ```Init()``` 指定的起始時間。相對的，需要取得 ```DateTimeUtil.Instance.Now``` 的時候再當下計算即可。
1. 紀錄最後一次檢查事件發送的時間點 ```DateTime _last_check_event_time```:  
在時間的轉移，我抓兩個時間點來檢查。一個是明確呼叫 ```TimePass()``` 時，另一個是呼叫 ```DateTimeUtil.Instance.Now``` 取得目前時間時。每次檢查都會更新 ```_last_check_event_time```, 若更新的過程中跨越換日的時間點，就觸發 ```RaiseDayPassEvent``` 事件。

實際的 source code 我就不分段了，沒有幾行... 我就全貼了:

```csharp

public class DateTimeUtil
{
    private static DateTimeUtil _instance = null;

    public static DateTimeUtil Instance => _instance;
    public static void Init(DateTime expectedTimeNow)
    {
        if (_instance != null) throw new InvalidOperationException("DateTimeUtil was initialized. Call Reset() before re-init.");
        _instance = new DateTimeUtil(expectedTimeNow);
    }
    public static void Reset()
    {
        _instance = null;
    }

    /// <summary>
    /// 時間跨過每天的 00:00:00 時，會觸發 OnDayPass 事件
    /// 已知問題: 若在真實的時間軸 (例如執行 long running job, 或是 sleep) 進行度過跨日線的話, 不會立即觸發該日的事件。
    /// 精確觸發的時間點只有這兩個: 經過 .TimePass() 來移動時間軸，或是透過 DateTimeUtil.Instance.Now 存取目前時間。
    /// </summary>
    public event EventHandler<TimePassEventArgs> RaiseDayPassEvent;

    public class TimePassEventArgs : EventArgs
    {
        public DateTime OccurTime;
    }

    /// <summary>
    /// 封裝過的時間軸，與實際的時間軸的時間差
    /// </summary>
    private TimeSpan _realtime_offset = TimeSpan.Zero;

    private DateTime _last_check_event_time = DateTime.MinValue;

    private DateTimeUtil(DateTime expectedTime)
    {
        this._realtime_offset = expectedTime - DateTime.Now;
        this._last_check_event_time = expectedTime;

        this.RaiseDayPassEvent += (sender, args) => { Console.WriteLine($"- event: RaiseDayPassEvent({args.OccurTime}, {this.Now})"); };
    }

    public DateTime Now 
    {
        get
        {
            var result = DateTime.Now.Add(this._realtime_offset);
            this.Seek_LastEventCheckTime(result);
            return result;
        }
    }

    private void Seek_LastEventCheckTime(DateTime checkTime)
    {
        while(this._last_check_event_time < checkTime)
        {
            if (this._last_check_event_time.Date < checkTime.Date)
            {
                this._last_check_event_time = this._last_check_event_time.Date.AddDays(1);
                this.RaiseDayPassEvent?.Invoke(this, new TimePassEventArgs()
                {
                    OccurTime = this._last_check_event_time
                });
            }
            else
            {
                this._last_check_event_time = checkTime;
                break;
            }
        }
    }

    public void TimePass(TimeSpan duration)
    {
        if (duration < TimeSpan.Zero) throw new ArgumentOutOfRangeException();

        this._realtime_offset += duration;
        this.Seek_LastEventCheckTime(this.Now);
    }
}

```

改變時間的途徑就只有兩個，一個是隨著真實世界時間推移而改變，我沒辦法偵測。雖然我認真想過要不要開一個 background thread 來監控，不過用在這裡我覺得有點殺雞用牛刀了...，事件觸發我的定義也沒有要 100% 精準，這種非同步的事件處理應該要能容許些許延遲才對，因此我把偵測的時間點埋在每一次呼叫 ```DateTimeUtil.Instance.Now``` 的時候進行。

另一個就單純的多，隨著呼叫 ```DateTimeUtil.Instance.TimePass(...)``` 明確的進行時空跳躍，我只要在改變 ```_realtime_offset``` 之後統一檢查一次從 ```_last_check_event_time``` 到 ```Now``` 之間有沒有漏掉的事件未發送，補發而已。為了區別 ```event``` "應該" 觸發的時間，跟實際觸發的時間可能會有落差，我在 ```TimePassEventArgs``` 內定義了 ```OccurTime``` 來標示，讓接收事件的人知道是因為哪一天的 ```event``` 才觸發的。

當然這邊 ```OccurTime``` 跟 ```Now``` 的誤差也是有的，隨著你 ```TimePass()``` 一次時間跳躍的範圍越長，誤差越大。這邊我也認真考慮過要不要事先計算，把跳躍分成多次，一次跳一天，觸發完 ```event``` 後再跳躍一天，直到跳躍到目的時間點為止。不過這版本我就沒實做了，因為我的目的是 unit test / PoC 啊，只要 interface 定義的好，這些不影響 interface 的修正，我有需要時再補上就好。



# 使用情境

要講怎麼使用，直接來貼單元測試就好了。針對 ```DateTimeUtil``` 我準備了這幾個測試，正好可以從測試來看看 ```DateTimeUtil``` 的正確用法。我測了這三種情境:

1. ```TimePassTest```, 測試基本的 ```Init()``` / ```TimePass()``` 對於 ```DateTimeUtil.Instance.Now``` 結果的影響。
1. ```TimePassWithEventTest```, 搭配 ```TimePass()```, 測試 ```event``` 是否正確地觸發。
1. ```RealtimeEventTest```, 測試實際時間前進，是否正確觸發 ```event。```

直接來看這三段測試 (```[TestInitialize]``` 的部分我就一起貼在這段了):

## TimePassTest:

```csharp

[TestInitialize]
public void SetUp()
{
    DateTimeUtil.Reset();
}

[TestMethod]
public void TimePassTest()
{
    DateTimeUtil.Init(new DateTime(2002, 10, 26, 12, 0, 0));

    // 時間計算容許誤差範圍。因為會跟 realtime clock 有關，無法精準預期每台機器的執行時間誤差 (ms 等級)
    // 需要特別留意的是，若在 debug mode 下，單步執行會讓時間計算誤差擴大到分鐘 (看你操作的速度)。
    TimeSpan tolerance = TimeSpan.FromSeconds(1);

    // 10 sec 誤差
    Assert.IsTrue(DateTimeUtil.Instance.Now - new DateTime(2002, 10, 26, 12, 0, 0) < tolerance);

    DateTimeUtil.Instance.GoNextHours(3);
    Assert.IsTrue(DateTimeUtil.Instance.Now - new DateTime(2002, 10, 26, 12 + 3, 0, 0)< tolerance);

    DateTimeUtil.Instance.TimePass(TimeSpan.FromMinutes(15));
    DateTimeUtil.Instance.GoNextHours(1);
    Assert.IsTrue(DateTimeUtil.Instance.Now - new DateTime(2002, 10, 26, 12 + 3 + 1, 0, 0) < tolerance);

    Thread.Sleep(5 * 1000);
    Assert.IsTrue(DateTimeUtil.Instance.Now - new DateTime(2002, 10, 26, 12 + 3 + 1, 0, 0 + 5) < tolerance);
}

```

由於實際執行，往往有不可預測的情況發生。 ```DateTime``` 多個幾 msec 就會導致 ```Assert``` 判定失敗。因此與其判定時間數值完全精準，我選擇了誤差在 1 sec 內都算正確的判定方式。其他就沒啥好說明的了。```Init()``` 設定為 ```2002/10/26 12:00:00```, 隨後不斷的用 ```TimePass()``` 調整時間，並且用 ```Assert``` 判定時間是否切換到預期的數值。最後補上不用 ```TimePass()```, 改用 ```Thread.Sleep()```, 同樣用 ```Assert``` 判斷 ```.Now``` 讀取的時間是否正確。


## TimePassWithEventTest

```csharp

[TestMethod]
public void TimePassWithEventTest()
{
    DateTimeUtil.Init(new DateTime(2002, 10, 26, 12, 0, 0));

    int count = 0;
    DateTimeUtil.Instance.RaiseDayPassEvent += (sender, args) =>
    {
        count++;
    };

    count = 0;
    DateTimeUtil.Instance.GoNextHours(15).GoNextDays(35); // time pass: 35days + 15hours

    Assert.AreEqual(36, count);
}

```

延續前面的案例，這次來試試 ```TimePass()``` 跨日時，跨日事件 ```RaiseDayPassEvent``` 是否正確的觸發? 我給了一個很單純的 ```RaiseDayPassEvent``` Handler, 每觸發一次就讓 counter +1, 最後來檢查 ```TimePass()``` 後的 counter 是否如預期。起始時間訂在 ```2002/10/26 12:00:00```, 透過 ```TimePass()``` 將時間往後跳轉了 35 days 15 hours，理論上會跨 36 天才對。用了 ```TimePass()```, 並且透過 Event Handler 增加 counter 數值，最後用 ```Assert``` 判定結果。


## RealtimeEventTest

```csharp

[TestMethod]
public void RealtimeEventTest()
{
    DateTimeUtil.Init(new DateTime(2002, 10, 25, 23, 59, 58));

    int count = 0;
    DateTimeUtil.Instance.RaiseDayPassEvent += (sender, args) =>
    {
        count++;
    };

    count= 0;
    Thread.Sleep(5 * 1000);

    Assert.AreEqual(0, count);

    var x = DateTimeUtil.Instance.Now;
    Assert.AreEqual(1, count);

    DateTimeUtil.Instance.GoNextDays(1).TimePass(TimeSpan.FromSeconds(86400 - 2));
    Assert.AreEqual(2, count);

    Thread.Sleep(5 * 1000);
    Assert.AreEqual(2, count);

    var result = DateTimeUtil.Instance.Now;
    Assert.AreEqual(3, count);
}

```

第三個案例同上述，只是不靠 ```TimePass()``` 來做時空跳躍了。我先用 ```TimePass()``` 跳至跨日前 2 sec，確認 counter 數字是否正確 (理論上 RaiseDayPassEvent 應該還沒觸發)。用 ```Thread.Sleep()``` 等了 5 sec 後再測試一次，因為還未呼叫 ```TimePass()``` 或是 ```.Now```, 所以預期事件也還未被觸發，直到 ```.Now``` 被呼叫後就順利偵測到事件觸發的執行結果。

這邊示範了正確的 ```DateTimeUtil``` 的使用方式，要真的應用在你的專案上，只要在 ```Main()``` 啟動點加上 ```.Init()```, 設定正確的 offset (不設定就是跟真正的系統時間一致)。而 Event Handler 的用法就如同 C# 一般的 Event Handler 用法，用 ```+=``` 運算子掛上你自己的 Event Handler 即可。



# 延伸思考: PoC 的應用

開始聊之前，先貼一篇文章。這篇文章對 PoC 做了很精準的詮釋:

* Reference Docs: [3 Expert Tips for Developing a Successful Proof of Concept (PoC) in 2022](https://www.netsolutions.com/insights/proof-of-concept-PoC/)

文章最後，留一點時間來讓我聊聊 PoC 這檔事吧。如果只是單元測試的需求，我可能不會想動手自己刻 ```DateTimeUtil``` 來用... (其他選擇方便的多了，何況真正要大量產出測試的不是我，我寫的可能也不合其他 team member 的胃口)，另外真正的目的，是搭配 PoC 的需要，我必須有 ```DateTimeUtil``` 這樣的時光機，讓我能更方便的 PoC 跟時間有關的架構跟流程設計。

回到我最原始的初衷，在思考系統設計的過程中，我還蠻常利用 PoC 的技巧來驗證我腦袋裡的想法，尤其是在開始接觸微服務架構之後，這方法對我的幫助更大了。越複雜的架構，你要實做出來的障礙 (或是門檻) 也越高，哪有可能一個人能懂得那十八般武藝，還都能夠有足夠的技巧把它實做出來啊? 因此，把抽象化思考發揮到極致，任何可以省略的部分都先排除，只保留最關鍵的設計概念 (concept) 並且寫一段 code 出來驗證可行性，這樣的 PoC 就變成我日常工作的一部分了。

微服務架構，涵蓋了相當大範圍的技術領域，從 infrastructure, 到 devops, CI/CD, API design, 分散式系統等等通通都是難題, 要樣樣精通是不可能的，因此我常常用降維的方式來降低我大腦的負荷。舉例來說，API 的設計是微服務的關鍵，然而要寫出 client / server, 加上架設環境, 顧好安全問題與可靠度問題, 時間就花光了。因此我的應對方式就是: 直接從 C# (我最熟悉，能運用自如的語言) 的 interface 開始吧! API 設計最難的是結構，我只要能先用 C# interface 表達出我怎樣把這服務透過 interface 提供出來，剩下從 C# interface 對應到 HTTP API, 就是手工藝的問題了。因此，PoC 的過程中，我只要搞定 C# interface 即可，對我來說省下了很多驗證思考設計問題的成本。


## 降維打擊

> 想辦法把問題的複雜度降低一個維度，然後解決它

我所謂的 PoC, 就真的是專注在驗證 "concept"。對我而言，就是用 "降維打擊" 的手段，來面對複雜的系統架構設計。只要我能找出我應該專注的 "concept"，那麼 PoC 的過程中，我就可以撇除絕大部分的雜訊，讓我的設計工作的複雜度降低了好幾個維度。除了紙上談兵，畫畫架構圖來驗證之外，我希望能落實到 code 的層級也能降維打擊，因此我自己發展出了一套 PoC 的作法。

所謂的 "降維"，有好幾個層面的意思。一個是從真正的分散式系統，將分散的維度從 host 之間，降級到 thread 之間，這是一種降維的手段；我需要跨系統的呼叫 (RPC, Remote Procedure Call)，降級到語言間的呼叫 (LPC, Local Procedure Call)，這是一種降維的手段；我需要驗證演算法是否真的能在高流量下正確的處理資料，我不需要真正建立 cluster, 我只需要把問題降級成 multi-thread 就可以驗證了，這是一種降維的手段；我需要在 database 建立資料表並且建立測試資料，降級到語言內的 collection / query (感謝 Microsoft [Anders](https://en.wikipedia.org/wiki/Anders_Hejlsberg) 大神, 在 C# 內創造了很棒的 Linq, 以及 ```IEnumerable``` 的各種 collection 應用與語法糖)，省略了資料庫處理與 ORM 的處理，這是一種降維的手段；我需要用 event driven 被動觸發的模式來思考程式的結構，替代主動呼叫 + 排程執行的程式結構，我不需要大費周章地建立 message bus, 並且撰寫 producer / consumer 來驗證想法，我只需要降級到 C# 語言的 event 機制就可以了 (再次感謝 Microsoft 直接在 C# 內建了很優雅的 event 機制)，這是一種降維的手段。

以上這些，我能夠這樣 "降級" 的唯一條件是: 我必須很清楚真實維度跟我 PoC 的維度之間怎麼對應，並且我必須對對應的必要手段跟技巧有足夠的掌握能力，我就能享有這些好處。所以，各位在看我過去的文章，我會花很多功夫去鑽研平行處理，演算法等等理論背後的探討，就是這個原因。因為這裡累積下來的知識，在我設計更大型或是更複雜的系統時，這些努力的成效就被解放出來了。沒有過去的累積，我現在大概還只能停留在碼農的層級吧...。這就是我一直在練習的 "降維打擊" PoC 手法，也真的讓我能夠空出一些思考空間，讓我好好認真思考核心的問題解法。

## PoC 案例

藉這機會替我的舊文打一下廣告吧! 這幾篇文章，其實都用了類似的技巧，包括降維驗證想法，同時我會抓出關鍵的指標，協助我判斷解決方案的優劣。各位有興趣可以用這樣的觀點，重新讀一讀我過去的這些文章:

**Reference Article**(s):
- [API Design #1](/2016/10/10/microservice3/) 資料分頁的處理方式; 2016/10/10
- [API Design #2](/2016/10/23/microservice4/) 設計專屬的 SDK; 2016/10/23
- [API Design #5](/2016/12/01/microservice7-apitoken/) 如何強化微服務的安全性? API Token / JWT 的應用; 2016/12/01
- [API Design #6](/2022/03/25/microservices15-api-design/) 微服務架構 - 從狀態圖來驅動 API 的設計; 2022/03/25
- [API Design #7](/2022/04/25/microservices16-api-implement/) 微服務架構 - 從狀態圖來驅動 API 的實作範例 (ASP.NET Core); 2022/05/08
- [Part #2](/2018/06/10/microservice10-throttle/) 微服務基礎建設 - 服務負載的控制; 2018/06/10
- [Part #3](/2018/12/12/microservice11-lineup/) 微服務基礎建設 - 排隊機制設計; 2018/12/12
- [Part #4](/2019/01/01/microservice12-mqrpc/) 可靠的微服務通訊 - Message Queue Based RPC; 2019/01/01
- [Part #5](/2020/02/09/process-pool/) 非同步任務的處理機制 - Process Pool; 2020/02/15
- [架構面試題 #1](/2018/03/25/interview01-transaction/) 線上交易的正確性; 2018/03/25
- [架構面試題 #2](/2018/04/01/interview02-stream-statistic/) 連續資料的統計方式; 2018/04/01
- [架構面試題 #3](/2019/06/01/nested-query/) RDBMS 處理樹狀結構的技巧; 2019/06/01
- [架構面試題 #4](/2020/03/10/interview-abstraction/) 抽象化思考；折扣規則的設計機制; 2020/04/02


## 小結

回到這篇，我先從最單純的單元測試怎麼解決 ```DateTime.Now``` 的問題，帶出背後 PoC 的想法。我實際上應用 ```DateTimeUtil``` 的地方，當然不只是 unit test. 而是我在內部的某些 project, 直接在 prototype 的設計，就直接加上了 ```DateTimeUtil``` 的 UI。舉例來說，某系統的架構展示，我就在後台的右上角，直接加上了代表 ```.Now``` 的 lLabel (顯示目前系統 "認為" 的時間)，以及幾個相關的操作 ```TimePass(...)``` / ```GoNextHours(...)``` / ```GoNextDays(...)``` 的按鈕，按一下就代表系統時間往後快轉了多少，直接跳到隔天等等。對於溝通或驗證想法，幫助很大。尤其是有些難以說明或是想像的流程，這方法可以讓你眼見為憑，讓困難的問題可以真正看到能用程式碼漂亮的解決。

高度的抽象化思考，對很多人來說是困難的 (因為系統運作方式真的違反人類大腦的思考方式啊啊啊啊)。抽象化的思考，我覺得有兩類的問題是最容易讓腦筋打結的，一種就是跟時間序有關的 (尤其是有幾件事並行發生的)；另一種就是事件驅動，往往程序性語言都是從第一部做到最後一步，但是事件驅動把它打散了，一個事件觸發一個動作，你必須妥善安排每個事件，才能讓結果跟程序語言維持一致。前者就類似多執行緒的開發，你腦袋想的平行處理，換成 code 往往不是那麼一回事。而規則引擎就像防火牆，你想要的結果得先把它化成一堆 rules / event handler, 讓防火牆收到每個封包後按照你設定的 rules 一條一條執行 & 判斷，然後得到你最後想要的結果。

這些，都是我對 PoC 的想法。會想寫這篇，只是在某個複雜的案子 PoC 過程中，額外衍生出來的 micro side project 而已 XDD, 就從一個很簡單的設計: ```DateTime``` 物件的 Mock 開始吧! 這篇的主題 ```DateTimeUtil``` 其實非常單純，有需要的朋友直接複製文章內的 source code 就可以了，我就不另外開 GitHub Repo 來分享了。歡迎自由取用，後續我會再利用 PoC 的主題，介紹一下我為了 PoC 發展出來的這類小工具。
