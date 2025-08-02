---
layout: post
title: "生產者 vs 消費者 - BlockQueue 實作"
categories:
- "系列文章: 多執行緒的處理技巧"
tags: [".NET","C#","作品集","作業系統","多執行緒","專欄","技術隨筆","有的沒的","物件導向"]
published: true
comments: true
permalink: "/2008/10/18/生產者-vs-消費者-blockqueue-實作/"
redirect_from:
  - /columns/post/2008/10/18/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx/
  - /post/2008/10/18/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx/
  - /post/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx/
  - /columns/2008/10/18/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx/
  - /columns/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx/
wordpress_postid: 57
---



過去寫了 [好幾篇跟執行緒相關的文章](/category/Threading.aspx)，講的都是如何精確控制執行緒的問題。不過實際上有在寫的人就知道，那些只是  "工具 "，最重要的還是你該怎樣安排你的程式，讓它能有效率的用到執行緒的好處，那才是重點。大部份能有效利用到多執行緒的程式，大都是大量且獨立的小動作，可以很簡單的撒下去給 ```ThreadPool``` 處理，不過當你的程式沒辦法這樣切，就要想點別的辦法了。 

開始看 code 前先講講簡單的概念。這篇要講的是另一種模式:  "**生產者 v.s. 消費者**"。這是個很典型的供需問題，唸過作業系統 (Operation System) 的人應該都被考過這個課題吧 @_@。簡單的說如果你的程式要處理的動作可以分為  "生產者 " (產生資料，載入檔案，或是第一階段的運算等等) 及消費者 (匯出資料，或是第二階段的運算等等) 這種模式，而前後兩個階段各自又適合用執行緒來加速的話，那你就值得來研究一下這種模式。第一手資料就是去看看作業系統的書，[恐龍書](http://www.google.com.tw/search?complete=1&hl=zh-TW&q=%E6%81%90%E9%BE%8D%E7%89%88%2B%E4%BD%9C%E6%A5%AD%E7%B3%BB%E7%B5%B1&btnG=%E6%90%9C%E5%B0%8B&meta=lr%3Dlang_zh-CN%7Clang_zh-TW&aq=f&oq=) 足足有一整章在講，足夠你研究了。本篇重點會擺在怎樣用 C# / .NET 實作的部份。 

舉個具體一點的例子，如果你想寫個程式，從網站下載幾百個檔案，同時要把它們壓縮成一個 ZIP 檔，在過去你大概只能全部下載完之後，再開始ZIP的壓縮動作。第一階段都是 IO (網路) bound 的程式，第二階段則是 CPU bound。如果是完全獨立的兩個程式，很適合擺在一起執行，因為它們需要的資源不一樣，不會搶來搶去。但是就敗在他們要處理的資料是卡在一起的。 

把這個動作想像成我們有兩組人分別負責下載及壓縮的動作，下載的部份可以多執行緒同時進行沒問題，但是下載好一個檔案，就可以先丟給後面的那組人開始壓縮了，不用等期它人下載完成。如果下載的暫存目錄空間有限，我們甚至可以這樣調整: 當 TEMP 滿了的話，下載動作就暫停，等到 TEMP 裡的東西壓縮好清掉一部份後再繼續。而壓縮的部份則相反，如果 TEMP 已經空了就暫停，等到有東西進來再繼續，直到完成為止。 

![](/wp-content/be-files/WindowsLiveWriter/vsBlockQueue_7B44/image_2.png)

前後兩階段該如何利用多執行緒，我就跳過去了， [過去那幾篇](/category/Threading.aspx) 就足以應付。這種模式的關鍵在於前後兩階段的進度該如何平衡。有些範例是有照規矩的把這模式實作出來，不過... 你也知道，看起來就是像作業的那種，完全不像是可以拿來正規的用途。 



我認定 "**好**" 的實作，是像 ```System.Collections.Generics``` 之於 DataStructure 那樣，能很漂亮的把細節封裝起來，很容易重複利用的才是我認為好的實作。不能容易的使用，那就只能像作業一樣寫完就丟...。這個問題看過有人用 ```Semaphore``` 來做，也是作的很棒，不過我比較推薦的是 Queue 的作法。 


 


從上圖來看，生產者跟消費者都很簡單，就是過去講的多執行緒或是執行緒集區就搞定，關鍵在於中間的控制。我的想法是把庫存管理的東西實作成佇列 (QUEUE)，生產者產出的東西就放到 QUEUE，而消費者就去 QUEUE 把東西拿出來。不過現成的 QUEUE 不會告訴你 QUEUE 滿了，QUEUE 空了也只會丟 EXCEPTION 而以。這次我做了個 ```BlockQueue``` 就是希望解決這個問題。 


 


我期望這個 QUEUE 能跟一般的 QUEUE 一樣使用，但是要有三個地方不一樣: 

1. 要設定大小限制，當 QUEUE 達到容量上限時 EnQueue 的動作會被暫停 (Block)，而不是丟出例外。
1. QUEUE 已經空了的時後，DeQueue 的動作會被暫停 (Block)，而不是丟出例外。
1. 要多個 QUEUE 關機的動作 (SHUTDOWN)，以免生產者都不出貨了，消費者還苦苦的等下去的窘況。

 


先看看這樣的 QUEUE 我希望它怎麼被使用。看一下簡單的範例程式 (主程式，不包含 ```BlockQueue```): 


**使用 BlockQueue 來實作的生產者/消費者範例**:

```csharp

public static BlockQueue<string> queue = new BlockQueue<string>(10);

public static void Main(string[] args)
{
    List<Thread> ps = new List<Thread>();
    List<Thread> cs = new List<Thread>();
    for (int index = 0; index < 5; index++)
    {
        Thread t = new Thread(Producer);
        ps.Add(t);
        t.Start();
    }
    for (int index = 0; index < 10; index++)
    {
        Thread t = new Thread(Consumer);
        cs.Add(t);
        t.Start();
    }
    foreach (Thread t in ps)
    {
        t.Join();
    }
    WriteLine("Producer shutdown. ");
    queue.Shutdown();
    foreach (Thread t in cs)
    {
        t.Join();
    }
}

public static long sn = 0;

public static void Producer()
{
    for (int count = 0; count < 30; count++)
    {
        RandomWait();
        string item = string.Format("item:{0} ", Interlocked.Increment(ref sn));
        WriteLine("Produce Item: {0} ", item);
        queue.EnQueue(item);
    }
    WriteLine("Producer Exit ");
}

public static void Consumer()
{
    try
    {
        while (true)
        {
            RandomWait();
            string item = queue.DeQueue();
            WriteLine("Cust Item: {0} ", item);
        }
    }
    catch
    {
        WriteLine("Consumer Exit ");
    }
}

private static void RandomWait()
{
    Random rnd = new Random();
    Thread.Sleep((int)(rnd.NextDouble() * 300));
}

private static void WriteLine(string patterns, params object[] arguments)
{
    Console.WriteLine(string.Format("[#{0:D02}]  ", Thread.CurrentThread.ManagedThreadId) + patterns, arguments);
}

```





 


 


主程式很簡單，你知道怎麼寫多執行緒程式的話那麼一看就懂了。一開始替 Producer / Consumer 各建立三個執行續，而每個 Producer 只作很簡單的事，就是連續生產 30 個字串放到 BlockQueue, 當所有的 Producer thread 都執行完後，會呼叫 ```queue.Shutdown( );``` 通知 QUEUE 已經全部生產完畢。 


Consumer 也很簡單，每個 Consumer 只是去 Queue 拿東西出來，顯示在 Console 上。直到 Dequeue 動作失敗，接到 Exception 之後就結束。 


要試試生產者/消費者模式的各種狀況，可以試著調整兩者的執行緒數量。舉例來說，調大 Producer 執行緒數量時 (P: 10 / C:5)，結果是這樣: 

![](/wp-content/be-files/WindowsLiveWriter/vsBlockQueue_7B44/image_7.png)


Producer 的進度大約就是領先 Consumer 的進度 10 筆資料左右，領先的幅度就暫停了，不會無止境的成長下去。證明卡在 QUEUE 內的數量受到控制。接下來再來看看調高 Consumer 的執行緒數量的結果: 


![](/wp-content/be-files/WindowsLiveWriter/vsBlockQueue_7B44/image_8.png)


好像 [iPhone 上市搶購熱潮](http://taiwan.cnet.com/crave/0,2000088746,20130427,00.htm) 一樣 @_@，供不應求，Producer 提供的資料馬上被搶走了...。 


 


效果不錯，看來這樣的實作有達成它的目的。最後來看的是 BlockQueue 的程式碼: 


```csharp

public class BlockQueue<T>
{
    public readonly int SizeLimit = 0;

    private Queue<T> _inner_queue = null;

    private ManualResetEvent _enqueue_wait = null;

    private ManualResetEvent _dequeue_wait = null;

    public BlockQueue(int sizeLimit)
    {
        this.SizeLimit = sizeLimit;
        this._inner_queue = new Queue<T>(this.SizeLimit);
        this._enqueue_wait = new ManualResetEvent(false);
        this._dequeue_wait = new ManualResetEvent(false);
    }

    public void EnQueue(T item)
    {
        if (this._IsShutdown == true) throw new InvalidCastException("Queue was shutdown. Enqueue was not allowed. ");

        while (true)
        {
            lock (this._inner_queue)
            {
                if (this._inner_queue.Count < this.SizeLimit)
                {
                    this._inner_queue.Enqueue(item);
                    this._enqueue_wait.Reset();
                    this._dequeue_wait.Set();
                    break;
                }
            }
            this._enqueue_wait.WaitOne();
        }
    }

    public T DeQueue()
    {
        while (true)
        {
            if (this._IsShutdown == true)
            {
                lock (this._inner_queue) return this._inner_queue.Dequeue();
            }

            lock (this._inner_queue)
            {
                if (this._inner_queue.Count > 0)
                {
                    T item = this._inner_queue.Dequeue();
                    this._dequeue_wait.Reset();
                    this._enqueue_wait.Set();
                    return item;
                }
            }
            this._dequeue_wait.WaitOne();
        }
    }

    private bool _IsShutdown = false;

    public void Shutdown()
    {
        this._IsShutdown = true;
        this._dequeue_wait.Set();
    }
}


```

 


重點只在重新包裝 Queue 的 Enqueue / Dequeue ，及追加的 ```Shutdown( )``` 裡做的執行緒同步機制。在 ```BlockQueue``` 尚未 Shutdown 之前，Enqueue / Dequeue 都不會引發 Exception, 取代的是用 ```ManualResetEvent``` 的 ```WaitOne( )``` 來暫停這個動作，直到另一端資料準備好為止。 


然而當 Shutdown 被呼叫過之後，Queue 就不再接受新的東西被塞進來了，而東西拿光因為不再補貨，所以就維持原本 Queue 的設計扔出 Exception。 


 

其實真的要挖的話，這個 Queue 可以進一步的改善，以資料結構來看，這種有固定 SIZE 上限的 QUEUE，最適合用 CircleQueue 來實作了。有興趣的朋友們可以換上回介紹過的 NGenerics 改看看，我就不再示範了。其實還有其它變型，像是 Priority Queue, 進去跟出來的順序不一定一樣，意思是你地位比較高的話是可以  "插隊 " 的，後加入 QUEUE 的物件，可以優先被拿出來。這些機制都是可以進一步改善  "生產者/消費者 " 模式的方法，有需要的讀者們可以朝這個方向思考看看! 

這篇只是個開始，運用這種機制，可以進一步延伸出 Pipeline 模式 (生產線)，甚至更進一步運用到串流 (Stream) 的應用。運氣好的話下個月應該看的到完整的探討跟解說吧 ...，敬請期待 :D 
