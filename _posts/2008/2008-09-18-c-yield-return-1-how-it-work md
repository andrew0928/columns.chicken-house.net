---
layout: post
title: "[C#: yield return] #1. How It Work ?"
categories:
- "系列文章: Inside C# Yield Return"
tags: [".NET","C#","Tips","多執行緒","技術隨筆","物件導向"]
published: true
comments: true
permalink: "/2008/09/18/c-yield-return-1-how-it-work/"
redirect_from:
  - /columns/post/2008/09/18/C-yield-return-1-How-It-Work-.aspx/
  - /post/2008/09/18/C-yield-return-1-How-It-Work-.aspx/
  - /post/C-yield-return-1-How-It-Work-.aspx/
  - /columns/2008/09/18/C-yield-return-1-How-It-Work-.aspx/
  - /columns/C-yield-return-1-How-It-Work-.aspx/
wordpress_postid: 68
---

C# 常常拿來跟 Java 比較，在 .NET 1.1 時常常是不相上下，而 .NET 又因為較年輕 & 頂著 Microsoft 的名號，往往被當成玩具一樣，不過
Microsoft 的確是在 .NET 及 C# 下了很多功夫，作了很多 Sun 不願意在 Java 身上作的事，這次要探討
的 [yield return](http://msdn.microsoft.com/en-us/library/9k7k7cf0(VS.80).aspx) 及 
[IEnumerable<T>](http://msdn.microsoft.com/en-us/library/9eekhta0.aspx) 這搭配的 Interface 就是一例...。

Java 在過去的版本，往往為了跨平台，把修改 VM 規格視為大忌，連帶的連語法修改都一樣，即使不影響編譯出來的 bytecode 相容性也是
一樣不肯改。而 .NET 就為了語法簡潔，編譯器往往是讓步的一方，因此 C# 有相當多的 
[Syntax Sugar](http://en.wikipedia.org/wiki/Syntax_sugar)，讓你寫起 CODE 爽一點...。你只要寫簡單的 CODE，編譯器會幫你轉成
較煩雜的 CODE，有點像是文言文或是成語那樣的味道。古代文人常常用簡單的四個字，就有一大票引申的意義跑出來...，寫作文時只要
套上成語，就代表了成語背後的故事，寓意。

"yield return" 算是最甜的甜頭了，因為編譯器替你翻出來的 code 整整一大串。先來看個簡單的例子，如果我想實作 IEnumerator<T> 
Interface, 照順序輸出 1 ~ 100 的數字，正統的 C# code 看起來要像這樣:

**用 IEnumerator 依序傳回 1 ~ 100 的數字**

```csharp

public class EnumSample1 : IEnumerator<int>
{
    private int _start = 1;
    private int _end = 100;
    private int _current = 0;

    public EnumSample1(int start, int end)
    {
        this._start = start;
        this._end = end;
        this.Reset();
    }

    public int Current
    {
        get { return this._current; }
    }

    public void Dispose()
    {
    }

    object System.Collections.IEnumerator.Current
    {
        get { return this._current; }
    }

    public bool MoveNext()
    {
        this._current++;
        return !(this._current > this._end);
    }

    public void Reset()
    {
        this._current = 0;
    }
}

```
 

 

好不容易寫好 IEnumerator 之後，再來是拿來用，一筆一筆印出來:

**取得 IEnumerator 物件後，依序取出裡面的數字**

```csharp

EnumSample1 e = new EnumSample1(1, 100);

while (e.MoveNext())
{
    Console.WriteLine("Current Number: {0}", e.Current);
}

```

不過如果只是要列出 1 ~ 100，大部份的人都不會想這樣寫吧? 直接用計概第一堂教你的 loop 不就好了? 程式碼如下:


**送分題: 用 LOOP 印出 1 ~ 100 的數字**


```csharp

for (int current = 1; current <= 100; current++)
{
    Console.WriteLine("Current Number: {0}", current);
}

```
        

兩個範例都沒錯啊，那為什麼要用 IEnumerator ? 其實 IEnumerator 並不是 Microsoft 發明的，在四人幫寫的
經典書籍 (Design Patterns) 裡就有這麼一個設計模式: [Iterator](http://en.wikipedia.org/wiki/Iterator)，它的目的
很明確:

> "毋須知曉聚合物件的內部細節，即可依序存取內含的每一個元素。"

(摘自 物件導向設計模式 Design Patterns 中文版，葉秉哲 譯)

這裡指的 "聚合物件" 就是指 .NET 的 Collection, List, Array 等這類物件。意思是你不需要管 collection 裡每一個物件是怎麼
擺的，用什麼結構處理的，用什麼邏輯或演算法處理的，我就只管照你安排好的順序一個一個拿出來就好。沒錯，這就是它主要的目的。換
另一個說法，就是我們希望把物件巡訪的順序 (iteration) 跟依序拿到物件後要作什麼事 (process) 分開，那你就得參考 Iterator Pattern。
不用? 那只好讓你的 iteration / process 混在一起吧。

差別在那? 我們再來看第二個例子。如果題目改一下，要列出 1 ~ 100 的數字，但如果不是 2 的倍數，也不是 3 的倍數，就跳過去。先來
看看 Loop 的版本:


**進階送分題，用LOOP印出 1~100 之中，2 或 3 的倍數**

```csharp

for (int current = 1; current <= 100; current++)
{
    bool match = false;

    if (current % 2 == 0) match = true;
    if (current % 3 == 0) match = true;

    if (match == true)
    {
        Console.WriteLine("Current Number: {0}", current);
    }
}

```

再來看看 IEnumerator 的版本:


**用 IEnumerator 列出 1 ~ 100 中 2 或 3 的倍數**

```csharp

public class EnumSample2 : IEnumerator<int>
{
    private int _start = 1;
    private int _end = 100;
    private int _current = 0;

    public EnumSample2(int start, int end)
    {
        this._start = start;
        this._end = end;
        this.Reset();
    }

    public int Current
    {
        get { return this._current; }
    }

    public void Dispose()
    {
    }

    object System.Collections.IEnumerator.Current
    {
        get { return this._current; }
    }

    public bool MoveNext()
    {
        do {
            this._current++;
        } while(this._current %2 > 0 && this._current %3 > 0);
        return !(this._current > this._end);
    }

    public void Reset()
    {
        this._current = 0;
    }
}

```    

而扣掉 IEnumerator 的部份，要把數字印出來的程式碼則完全沒有改變:

**取出 IEnumerator 的每個數字，印到畫面上**


```csharp

EnumSample2 e = new EnumSample2(1, 100);

while (e.MoveNext())
{
    Console.WriteLine("Current Number: {0}", e.Current);
}

```

可以看的到，Loop 版本的確是把 iteration 跟 process 的 code 完全混在一起了，未來任何一方的邏輯要抽換都很
麻煩，而 IEnumerator 則不會，分的很清楚，不過... 這 Code 會不會太 "髒" 了一點啊...? 試問一下，有誰會這麼
勤勞，都用 IEnumerator 來寫 Code? 有的話請留個言，讓我崇拜一下...。


屁話講了一堆，最後就是要帶出來 "的確有魚與熊掌得兼的方法"，怎麼作? 來看看用 C# 的 yield return 版本的程式碼:


**傳回 IEnumerable 的 METHOD (不用再寫 CLASS，實作 IEnumerator 了)**

```csharp

public static IEnumerable<int> YieldReturnSample3(int start, int end)
{
    for (int current = 1; current <= 100; current++)
    {
        bool match = false;

        if (current % 2 == 0) match = true;
        if (current % 3 == 0) match = true;

        if (match == true)
        {
            yield return current;
        }
    }
}
    
```

**用 foreach 搭配 IEnumerable 印出每一筆數字**

```csharp

foreach (int current in YieldReturnSample3(1, 100))
{
    Console.WriteLine("Current Number: {0}", current);
}


```            


真是太神奇了，[安德魯](/)。如何? 完美的結合兩者的優點，這種 code 實在是令人挑不出什麼缺點... 真是優雅... 
不過念過 [系統程式](http://en.wikipedia.org/wiki/System_programming) 的人一定都會吶悶... 這樣的程式執行方式，不就
完全的違背了一般結構化程式典型的 function call / return 的鐵律了? 程式呼叫某個 function 就應該完全執行完
才能 return 啊，怎麼能 "yield" return 後，跑完一圈又回到剛才執行到一半的 function 繼續跑，然後再 "yield" return ? 
好像同實有兩段獨立的邏輯在運作... 還可以在兩者之間跳來跳去?

這就是 C# compiler 猛的地方了。搬出 reflector 來看看編譯出來的 code, 再被反組譯回來變成什麼樣子:




**反組譯 YieldReturnSample3**

```csharp

public static IEnumerable<int> YieldReturnSample3(int start, int end)
{
    <YieldReturnSample3>d__0 d__ = new <YieldReturnSample3>d__0(-2);
    d__.<>3__start = start;
    d__.<>3__end = end;
    return d__;
}

```



耶? 看到一個多出來的 class: <YieldReturnSample3>d__0 ... 再看看它的 class 長啥樣:




**編譯器自動產生的 IEnumerator 衍生類別**

```csharp

[CompilerGenerated]
private sealed class <YieldReturnSample3>d__0 : IEnumerable<int>, IEnumerable, IEnumerator<int>, IEnumerator, IDisposable
{
    // Fields
    private int <>1__state;
    private int <>2__current;
    public int <>3__end;
    public int <>3__start;
    private int <>l__initialThreadId;
    public int <current>5__1;
    public bool <match>5__2;
    public int end;
    public int start;

    // Methods
    [DebuggerHidden]
    public <YieldReturnSample3>d__0(int <>1__state)
    {
        this.<>1__state = <>1__state;
        this.<>l__initialThreadId = Thread.CurrentThread.ManagedThreadId;
    }

    private bool MoveNext()
    {
        switch (this.<>1__state)
        {
            case 0:
                this.<>1__state = -1;
                this.<current>5__1 = 1;
                while (this.<current>5__1 <= 100)
                {
                    this.<match>5__2 = false;
                    if ((this.<current>5__1 % 2) == 0)
                    {
                        this.<match>5__2 = true;
                    }
                    if ((this.<current>5__1 % 3) == 0)
                    {
                        this.<match>5__2 = true;
                    }
                    if (!this.<match>5__2)
                    {
                        goto Label_0098;
                    }
                    this.<>2__current = this.<current>5__1;
                    this.<>1__state = 1;
                    return true;
                Label_0090:
                    this.<>1__state = -1;
                Label_0098:
                    this.<current>5__1++;
                }
                break;

            case 1:
                goto Label_0090;
        }
        return false;
    }

    [DebuggerHidden]
    IEnumerator<int> IEnumerable<int>.GetEnumerator()
    {
        Program.<YieldReturnSample3>d__0 d__;
        if ((Thread.CurrentThread.ManagedThreadId == this.<>l__initialThreadId) && (this.<>1__state == -2))
        {
            this.<>1__state = 0;
            d__ = this;
        }
        else
        {
            d__ = new Program.<YieldReturnSample3>d__0(0);
        }
        d__.start = this.<>3__start;
        d__.end = this.<>3__end;
        return d__;
    }

    [DebuggerHidden]
    IEnumerator IEnumerable.GetEnumerator()
    {
        return this.System.Collections.Generic.IEnumerable<System.Int32>.GetEnumerator();
    }

    [DebuggerHidden]
    void IEnumerator.Reset()
    {
        throw new NotSupportedException();
    }

    void IDisposable.Dispose()
    {
    }

    // Properties
    int IEnumerator<int>.Current
    {
        [DebuggerHidden]
        get
        {
            return this.<>2__current;
        }
    }

    object IEnumerator.Current
    {
        [DebuggerHidden]
        get
        {
            return this.<>2__current;
        }
    }
}

```


耶? 不就完全跟之前手工寫的 IEnumerator 一樣嘛? 只不過這個 IEnumerator 是自動產生出來的，不是手寫的...。 畢竟是機器
產生的 CODE，總是沒那麼精簡。想到了嗎? 沒錯，這就是 C# compiler 送給你的 syntax sugar ...，你可以腦袋裡想像著計概課
入門時教你的 LOOP 那樣簡單的想法，compiler 就幫你換成 IEnumerator 的實作方式，讓你隨隨便便就可以跟別人宣稱:

> 看! 我的程式有用到 Iterator 這個設計模式喔...


聽起來好像很臭屁的樣子... 哈哈! 如果是在真的用的到 [Iterator Patterns](http://en.wikipedia.org/wiki/Iterator) 的
情況下，真的是可以很臭屁的拿出來炫耀一下。不過，我幹嘛突然講起 yield return ? 各位看的過程中有沒有聯想到
前幾篇 POST 講的 Thread Sync 那兩篇文章 ( [#1](/2008/08/14/thread-sync-1-概念篇-如何化被動為主動/), 
[#2](/2008/08/15/thread-sync-2-實作篇-互相等待的兩個執行緒/) ) ? IEnumerator 跟 Thread Sync 又有什麼關係? 賣個關子，下篇繼續!
