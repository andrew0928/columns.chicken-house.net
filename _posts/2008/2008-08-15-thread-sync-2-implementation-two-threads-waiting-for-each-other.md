---
layout: post
title: "Thread Sync #2. 實作篇 - 互相等待的兩個執行緒"
categories:
- "系列文章: 多執行緒的處理技巧"
tags: [".NET","Tips","作業系統","多執行緒","技術隨筆","物件導向"]
published: true
comments: true
redirect_from:
  - /2008/08/15/thread-sync-2-實作篇-互相等待的兩個執行緒/
  - /2008/08/15/thread-sync-2-實作篇-互相等待的兩個執行緒/
  - /columns/post/2008/08/15/Thread-Sync-2-e5afa6e4bd9ce7af87-e4ba92e79bb8e7ad89e5be85e79a84e585a9e5808be59fb7e8a18ce7b792.aspx/
  - /post/2008/08/15/Thread-Sync-2-e5afa6e4bd9ce7af87-e4ba92e79bb8e7ad89e5be85e79a84e585a9e5808be59fb7e8a18ce7b792.aspx/
  - /post/Thread-Sync-2-e5afa6e4bd9ce7af87-e4ba92e79bb8e7ad89e5be85e79a84e585a9e5808be59fb7e8a18ce7b792.aspx/
  - /columns/2008/08/15/Thread-Sync-2-e5afa6e4bd9ce7af87-e4ba92e79bb8e7ad89e5be85e79a84e585a9e5808be59fb7e8a18ce7b792.aspx/
  - /columns/Thread-Sync-2-e5afa6e4bd9ce7af87-e4ba92e79bb8e7ad89e5be85e79a84e585a9e5808be59fb7e8a18ce7b792.aspx/
wordpress_postid: 79
---

繼[上篇](/post/Thread-Sync-1-e6a682e5bfb5e7af87-e5a682e4bd95e58c96e8a2abe58b95e782bae4b8bbe58b95.aspx)，[有人](http://www.michadel.net/)跟我講太深奧了... Orz, 其實不會，只是還沒看到 Code 而以...。就先來幫[黑暗魔人賽](http://blog.darkthread.net/blogs/darkthreadtw/archive/2008/07/21/win-a-vsts-2008.aspx)說明一下程式碼...。首先來看的是黑暗大魔王: GameHost..

**GameHost 呼叫 Player 的片段**

```csharp
public void Start(Player p)
{
    // 略...
    int[] guess = p.StartGuess(_maxNum, _digits);
    // 略...
    Hint hint = compare(guess);
    // 略...
    while (hint.A != _digits)
    {
        // 略...
        guess = p.GuessNext(hint);
        // 略...
        hint = compare(guess);
    }
    p.Stop();
    // 略...
}
```

這段程式完全是老闆的角度在思考。抓到 PLAYER 後就叫它開始猜 StartGuess()，然後拼命的叫 PLAYER 再猜 GuessNext(), 直到猜中才可以休息 Stop()

很典型的多型 ( Polymorphism ) 應用，實際上會 RUN 什麼 CODE，就看繼承 PLAYER 的人是怎麼寫的...。這次我們再從弱勢勞工的角度來看看 PLAYER 該怎麼實作 (以 darkthread 附的 DummyPlayer 為例):

**Player 實作的範例 ( DummyPlayer )**

```csharp
public class DummyPlayer : Player
{
    private int[] _currAnswer = null;
    private Random _rnd = new Random();

    private void randomGuess()
    {
        List<int> lst = new List<int>();
        for (int i = 0; i < _digits; i++)
        {
            int r = _rnd.Next(_maxNum);
            while (lst.Contains(r))
                r = _rnd.Next(_maxNum);
            lst.Add(r);
            _currAnswer[i] = r;
        }
    }

    public override int[] StartGuess(int maxNum, int digits)
    {
        base.StartGuess(maxNum, digits);
        _currAnswer = new int[digits];
        randomGuess();
        return _currAnswer;
    }
    public override int[] GuessNext(Hint lastHint)
    {
        randomGuess();
        return _currAnswer;
    }
}
```

因為 CODE 不多，我就不刪了，全文照貼。另一個原因是我想讓各位看看拆成好幾段的 CODE 是不是還能夠一眼就還原成原來的邏輯? 如果只看這段 CODE 十秒鐘，沒有看註解或說明，誰能馬上回答這段 CODE 解題的邏輯是什麼?

別誤會，不是指這 CODE 不易讀，而是因為呼叫的方式邏輯被迫配合 GameHost 而被切散了，你得再重新把它拼湊起來。它的邏輯很簡單，甚至簡單到連問題的答案都被忽略掉了，不過就每次都隨機丟個數字回去，在 StartGuess( ) 及 GuessNext( ) 都是。

可憐的勞動階級要站起來啊~ 先幻想一下，如果勞工 (PLAYER) 才是老闆，那麼程式可以改成怎麼樣? 這也才是我們本篇的主角。先來看看成果再回頭來看怎麼實作。這次看的是修改後的版本: AsyncDummyPlayer.

**換 PLAYER 的角度思考的邏輯: AsyncDummyPlayer**

```csharp
public class AsyncDummyPlayer : AsyncPlayer
{
    private int[] _currAnswer = null;
    private Random _rnd = new Random();
    private void randomGuess()
    {
        List<int> lst = new List<int>();
        for (int i = 0; i < _digits; i++)
        {
            int r = _rnd.Next(_maxNum);
            while (lst.Contains(r))
                r = _rnd.Next(_maxNum);
            lst.Add(r);
            _currAnswer[i] = r;
        }
    }
    protected override void Init(int maxNum, int digits)
    {
        _currAnswer = new int[digits];
    }
    protected override void Think()
    {
        while (true)
        {
            this.randomGuess();
            Hint h = this.GameHost_AskQuestion(this._currAnswer);
            if (h.A == this._digits) break;
        }
    }
}
```

程式碼也沒比較少，都差不多。不過是那堆 CODE 換個地方擺而以。但是仔細看看，這個版本的邏輯清楚多了，PLAYER 一開始就是執行 Init( ) 的部份，而 GameHost 叫 Player 開始解題時， Player 就開始思考 (Think)，而這個無腦的 Player 也很直接，就一直執行 while (true) { .... } 這個無窮迴圈，直到亂猜猜中為止。

如果 Player 在思考的時，不管在那裡它都可以適時的呼叫 GameHost_AskQuestion( .... ) 來跟 GameHost 問答案。什麼時後該猜數字? 該猜什麼數字? 這正是整個 Player 的核心，也就是 "怎麼猜" 這件事。以人的思考方式一定會分階段，比如一開始先把所有數字猜一輪，有個概念後再想想怎麼猜能更逼近答案，最後才是致命的一擊，找出正確答案送出去，贏得比賽。

這樣的作法，如果套在 DummyPlayer (原版本)，每個階段都要塞在一個大的 switch case, 放在 GuessNext( ) 裡。而現在是那個階段? 只能靠 instance variable 了，先存著等到下次又被呼叫時再拿出來回想一下，上回作到那...。

而第二個版本，則完全沒這個問題，就把它當作一般程式思考就夠了，第一階段就是一個 LOOP，有它自己用的一些變數。第一階段處理完畢就離開 LOOP 繼續執行後面的 CODE... 直到最後離開 Think( ) 這個 method (認輸) 或是猜中答案光榮返鄉...。

兩者的差別看出來了嗎? DummyPlayer 像是被動的勞工，老闆說一動他就作一動。第一動作完就拿個筆計記下來，等著下次老闆再叫他，他就翻翻筆記看看之前做到那，這次繼續...。

而 AsyncDummyPlayer 這個主動的勞工呢? 老闆交待給他一件任務後，他就自己思考起該怎麼做了。中間都不需要老闆下令。反而是過程中勞工需要老闆的協助時，老闆再適時伸出援手就可以了，一切雜務都由這位主動優秀的勞工自己處理掉。

有沒有差這麼多? 這麼神奇? 是怎麼辦到的? 先來看看類別關系圖:

![ThreadSync](/wp-content/be-files/WindowsLiveWriter/ThreadSync2_2849/ThreadSync_3.png)

上圖中，AsyncPlayer 就是改變這種型態的關鍵類別。AsyncPlayer 會用我們在上一篇講到的關念，化被動為主動，轉換這兩種呼叫模式。先來看看這個類別的程式碼到底變了什麼把戲，可以讓弱勢的勞工也有自主的權力?

**AsyncPlayer 實作: 化被動為主動**

```csharp
public abstract class AsyncPlayer : Player
{
    public override int[] StartGuess(int maxNum, int digits)
    {
        base.StartGuess(maxNum, digits);
        Thread thinkThread = new Thread(this.ThinkCaller);
        thinkThread.Start();
        this._host_return.WaitOne();
        return this._temp_number;
    }
    public override int[] GuessNext(Hint lastHint)
    {
        this._temp_hint = lastHint;
        this._host_call.Set();
        this._host_return.WaitOne();
        return this._temp_number;
    }
    public override void Stop()
    {
        base.Stop();
        this._temp_hint = new Hint(this._digits, 0);
        this._host_call.Set();
        this._host_end.WaitOne();
        this._host_complete = true;
    }
    private void ThinkCaller()
    {
        try
        {
            this.Init(this._maxNum, this._digits);
            this.Think();
        }
        catch (Exception ex)
        {
            Console.WriteLine("Player Exception: {0}", ex);
        }
        finally
        {
            this._host_end.Set();
        }
    }
    protected abstract void Init(int maxNum, int digits);
    protected abstract void Think();
    private AutoResetEvent _host_call = new AutoResetEvent(false);
    private AutoResetEvent _host_return = new AutoResetEvent(false);
    private AutoResetEvent _host_end = new AutoResetEvent(false);
    private bool _host_complete = false;
    private int[] _temp_number;
    private Hint _temp_hint;
    protected Hint GameHost_AskQuestion(int[] number)
    {
        if (this._host_complete == true) throw new InvalidOperationException("GameHost stopped!");
        lock (this)
        {
            try
            {
                this._temp_number = number;
                this._host_return.Set();
                this._host_call.WaitOne();
                return this._temp_hint;
            }
            finally {
                this._temp_number = null;
                this._temp_hint = new Hint(-1, -1);
            }
        }
    }
}
```

這段程式碼長了一點，內容也都刪不得，各位請耐心點看。上一篇我畫了張概念性的時序圖，這次我們再拿同一張圖，不過這次會標上程式碼:

![ThreadSync2](/wp-content/be-files/WindowsLiveWriter/ThreadSync2_2849/ThreadSync2_6.png)

請注意一下各個箭頭的上下順序。由上往下代表時間的進行，如果應該在後面執行的 CODE 不巧先被呼叫了，則動作較快的那個 THREAD 會被迫暫停，等待另一邊的進度跟上。先來看看 StartGuess( ) 怎麼跟 Think( ) 互動:

**StartGuess(...)**

```csharp
public override int[] StartGuess(int maxNum, int digits)
{
    base.StartGuess(maxNum, digits);
    Thread thinkThread = new Thread(this.ThinkCaller);
    thinkThread.Start();
    this._host_return.WaitOne();
    return this._temp_number;
}
```

GameHost 呼叫 Player.StartGuess( ) 有兩個目的，一個是給 Player 題目範圍，讓 Player 做好準備動作。另一個則是準備好之後 GameHost 要取得 Player 傳回的第一個問題。

程式碼很忠實的做了一樣的事，只不過 StartGuess( ) 建立了新的執行緒來負責。新的執行緒會執行 ThinkCaller( )，啟動之後 GameHost 這邊就什麼都不作，等待 _host_return 這個 WaitHandle 被叫醒，代表另一邊已經做好了，可以從共用變數 _temp_number 取得問題傳回去。

既然 GameHost 在等待某人通知它，我們就來看看是誰會通知他題目已經準備好了:

**GameHost_AskQuestion(...)**

```csharp
protected Hint GameHost_AskQuestion(int[] number)
{
    if (this._host_complete == true) throw new InvalidOperationException("GameHost stopped!");
    lock (this)
    {
        try
        {
            this._temp_number = number;
            this._host_return.Set();
            this._host_call.WaitOne();
            return this._temp_hint;
        }
        finally {
            this._temp_number = null;
            this._temp_hint = new Hint(-1, -1);
        }
    }
}
```

就在 GameHost 正在等題目的時後，另一個執行緒正在進行 "思考" 的動作，直到有結論後會呼叫 GameHost_AskQuestion( ... ) 送出問題。這時這個問題會被放到 _temp_number, 而下一步就是 _host_return.Set( ), 通知另一個執行緒，正在等這個結果的人: "喂! 東西已經準備好了，可以來取貨了!!"

整個機制就這樣串起來了。GameHost 那邊怎麼把答案傳回來? 同樣的作法，反過來而以。GameHost 會藉著呼叫 Player.GuessNext(...) 把答案傳回來，而這時就觸動一樣的機制，讓另一邊 Player Thread 呼叫的 GameHost_AskQuestion( ... ) 醒過來，把答案拿走， RETURN 回去。

這樣一直重複下去，剩下最後一個同步的點，就是結束遊戲的地方。說穿了也是一樣的把戲，只是這次是藉著 GameHost 呼叫 Player.Stop( )，而另一邊 Player Thread 執行完 Think( ) 後，兩邊就一起結束遊戲了。

總算講完了。其實 thread 能解決的問題還真是五花八門。每次當我想出這些方法來簡化問題時，我就會覺的很有成就感。雖然寫出這個不會讓我贏得比賽，反而因為同步的關係，AsyncDummyPlayer 執行的速度還遠遠落後 DummyPlayer (我的機器跑起來，大概差了四~五倍 ...) 。不過我知道我簡單的頭腦，不先把問題簡化的話，我大概解決不了太複雜的問題...。也許是缺了這種能力，才讓我更有動力去想簡化問題的方式吧?

最後，為什麼每次講到 thread 的文章，都是 code 一點點，文章跟圖一大堆? 咳咳... 難道我也到了靠一張嘴混日子的地步了嘛? Orz... 本系列到此結束，以後還會有什麼主題? 想到再說啦~~ 今天各位記得去拜拜~~ 下回見!
