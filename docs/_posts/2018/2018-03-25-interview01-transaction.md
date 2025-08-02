---
layout: post
title: "架構面試題 #1, 線上交易的正確性"
categories:
- "系列文章: 架構師觀點"
- "系列文章: 架構面試題"
tags: ["架構師", "面試經驗", "microservices"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2018/03/whiteboard-interviews.png
---

最近一直在思考，團隊裡的後端工程師能力是否到位，是微服務架構能否成功的關鍵之一。我該怎麼鑑別出面試者有沒有這樣的能力? 最有用的就是出幾個實際的應用題，讓面試者在白板上面說明。最近這一輪面試，談了不下幾十位吧，索性就把我幾個常問的白板考題整理起來，歸在微服務系列的文章裡的開發團隊篇，改善團隊成員的問題，也算是朝向微服務化的目標跨出一大步。

![](/wp-content/uploads/2018/03/whiteboard-interviews.png)
> 這書應該是惡搞的吧? 竟然還有恰恰 XD

<!--more-->

{% include series-2016-microservice.md %}

# 前言 & 導讀

在思考要考啥的過程中，我曾經考慮過像 leetcode 那樣的題庫，或是從各種架構問題 (如網友提供的資訊: [System Design Primer](https://l.facebook.com/l.php?u=https%3A%2F%2Fgithub.com%2Fdonnemartin%2Fsystem-design-primer&h=ATOBoA1AEZDD-BCyQX0joLXwbt8IszgoC-hx5OmukiZiSVh5EcpH36_4K7AB5-pRh80Rd8TAsPvqPLGpwz6KDtK8l0_TaAqDbKQa9XcZEwrHeFTpEw))，後來發現這樣考實在太 "硬" 了，都存在某種 "標準答案"。可是我覺得那不是我要考的，因為我不是要找跟我一樣的架構師啊，我想找的是有能力自己思考，也有能力實作微服務架構的工程師。他或許不需要有從無到有規劃與設計架構的能力，但是我會希望他碰到各種問題時，能以微服務(或是 cloud native) 的角度去思考解決方式。

因此，我重新想了一些題目，我改用 "應用題" 的方向，來測試看看應試者解決問題的思考過程。我試著先把題目 "抽象化"，先問問應試者解決問題的方向為何? 接著再問在不同規模的環境下 (EX: 從單機到 NLB，到微服務，從 SQL 到 NOSQL...)，會有那些不同的實作方式。這樣的測驗方式正好可以讓我瞭解應試者思考的規模極限在哪裡。題目的方向我想了交易的正確性、演算法的應用、巨量資料的處理策略、API 的設計、以及物件導向的觀念等等。其實這些都沒有標準答案，面試者大部分也沒辦法一次到位的就答出來，正好可以看出應試者的能力到哪裡。

很多人都說過: "沒有最完美的架構，只有最合適的架構"。這句話講的很有道理，可是對大部分的人來說都是打高空啊... 問題就在於要找出 "最合適" 的架構，本身就是件很困難的事情。因此這系列的白板題，我都是朝向這個方向去設計的。這些問題其實也都是過去我自己空閒時拿來練習的題材，因此這些問題我自己也都實作過，底下我就順帶 PO 出我自己的版本供參考。第一篇先來試試水溫，就先練習一下交易相關的問題吧! 


# 考題: 線上交易的正確性

這題可以算是送分題了，如果連最基本的答案都答不出來，我又需要你處理跟錢 (代幣 / 遊戲幣我也算在內) 有關的問題時，我實在是不敢把這任務交給你啊! 題目很簡單，就是帳務系統的設計過程中，你該如何避免交易不會發生錯誤，導致最後的金額不正確?

繼續探討題目前，我先定義一個 C# 的 abstract class, 假設有個處理銀行帳戶的 engine 長的像這樣:

```csharp

public abstract class AccountBase
{
    /// <summary>
    /// 帳戶擁有者的名字
    /// </summary>
    public string Name = null;

    /// <summary>
    /// 取得帳戶餘額
    /// </summary>
    /// <returns></returns>
    public abstract decimal GetBalance();

    /// <summary>
    /// 執行交易，將指定金額轉入該帳戶
    /// </summary>
    /// <param name="transferAmount"></param>
    /// <returns></returns>
    public abstract decimal ExecTransaction(decimal transferAmount);
}

```

請告訴我，要如何確保這 engine 不會算錯錢? 這裡補充一下，實際的世界裡，"錢" 這種東西，不應該憑空產生出來，也不會憑空消失的。我討論這類問題就常在講 "金錢守恆定律" 就是指這個，在一個封閉系統內，錢只會從某個地方轉移到另一個地方，整個系統的所有金額總和一定是不變的，除非有錢從外部的系統轉移進來，或是轉出去。沒有任何原因可以允許交易只做一半，一邊扣了錢，另一邊卻沒有拿到錢。無論任何情況都應該保持上述的條件才對。

這邊我暫時不去考慮較複雜的 "ROLLBACK" 機制，也先不去考慮系統 CRASH 等等這種意外狀況，我就先針對正常的交易執行過程中，必要的防護措施就夠了。我會驗證這個情境: 用 N 個 thread(s), 每個 thread 執行 M 次交易，每次只存 1.0 元到我的戶頭內。執行完畢後，我會預期我的戶頭應該要增加 N x M x 1.0 元才對。

所以我會怎麼驗證呢? 我會用 unit test 的方式，寫幾個 test case 來驗證這個 engine。一些基本的邏輯測試我就省略了 (連邏輯都搞錯也不用談了)。測試程式的片段如下。我暫時不打算跟 visual studio, mstest 等等 framework 綁的太緊, 因此 unit test 的部分我先用 console project 簡化, DI (dependency injection) 的部分也先簡化略過。面試考題主要的目的是看看應試者的思考過程，工程類的細節我在這系列的文章通通會略過。來看看測試程式:

```csharp

static void Main(string[] args)
{
    // skip DI, 建立指定的 account 實做機制
    //AccountBase bank = new Practices.LockAccount();
    //AccountBase bank = new Practices.WithoutLockAccount();
    //AccountBase bank = new Practices.TransactionAccount() { Name = "andrew" };
    AccountBase bank = new Practices.DistributedLockAccount() { Name = "andrew" };


    long concurrent_threads = 3;
    long repeat_count = 1000;
    decimal origin_balance = bank.GetBalance();

    List<Thread> threads = new List<Thread>();

    for (int i = 0; i < concurrent_threads; i++)
    {
        Thread t = new Thread(() => {
            for (int j = 0; j < repeat_count; j++)
            {
                bank.ExecTransaction(1);
            }
        });
        threads.Add(t);
    }

    Stopwatch timer = new Stopwatch();

    timer.Restart();
    foreach (Thread t in threads) t.Start();
    foreach (Thread t in threads) t.Join();


    decimal expected_balance = origin_balance + concurrent_threads * repeat_count;
    decimal actual_balance = bank.GetBalance();

    Console.WriteLine( "Test Result for {1}: {0}!", (expected_balance == actual_balance)?("PASS"):("FAIL"), bank.GetType().Name);
    Console.WriteLine($"- Expected Balance: {expected_balance}");
    Console.WriteLine($"- Actual Balance: {actual_balance}");
    Console.WriteLine($"- Performance: {concurrent_threads * repeat_count * 1000 / timer.ElapsedMilliseconds} trans/sec");
}

```

接下來，實作方式就有差別了，這系統可大可小，按照規模順序來看 (由小到大)，我對每個層級的工程師的期望:

|對應職級|系統規模|解決方案(關鍵字)|
|-------|--------|---------------|
|Junior Engineer|1 host|Lock, Racing Condition, Critical Section|
|Senior Engineer|10+ hosts|ACID, SQL Transaction|
|Architect|100+ hosts|Distributed Lock|


## 解法1. 單機運作 (考基本觀念: LOCK)

不需考慮 load balance, 也不需要考慮底層的 data storage, 資料的儲存直接用變數或是物件，例如 ```List<T>``` 之類的 collection 即可。有點概念的話，這程度真的是放水了 XD，其實只要考驗你懂不懂 "lock" 的重要性而已...

參考版本的答案，只要知道要 "lock" 怎麼應用就可以輕鬆過關。可以自己用 C# 的 ```lock``` 指令，或是用 ```Interlocked``` 替代都可以:

```csharp

public class LockAccount : AccountBase
{
    private decimal _balance = 0;
    private List<TransactionItem> _history = new List<TransactionItem>();
    private object _syncroot = new object();


    public override decimal GetBalance()
    {
        return this._balance;
    }

    public override decimal ExecTransaction(decimal transferAmount)
    {
        lock (this._syncroot)
        {
            this._history.Add(new TransactionItem()
            {
                Date = DateTime.Now,
                Amount = transferAmount,
                Memo = null
            });
            return this._balance += transferAmount;
        }
    }
}

```


執行結果:

```log

Test Result for LockAccount: PASS!
- Expected Balance: 20000
- Actual Balance: 20000
- Performance: 1538461 trans/sec

```


這邊的關鍵，在於執行交易 ```ExecTransaction()``` 的過程中，系統必須做兩件事:

1. 在交易紀錄 ```this._history``` 這個 ```TransactionItem``` 的集合裡面，加上一筆這次交易的資訊
1. 在帳戶資訊紀錄目前餘額 ```this._balance``` 的變數中，需要將這次的轉帳金額累加上去。

這組動作，必須符合 [ACID](https://zh.wikipedia.org/wiki/ACID) 的要求。最簡單的做法就是把它包裝成 [Critical Section; 臨界區](https://zh.wikipedia.org/wiki/%E8%87%A8%E7%95%8C%E5%8D%80%E6%AE%B5)。在 Critical Section 的範圍內，是不允許有並行的狀態的。單機的情況下，直接使用 C# language 或是 OS 本身的 Lock 機制就足夠了。上面的 sample code 就只有這樣而已。

我這邊另外準備個對照組，只拿掉 lock 那行而已，其他通通都不變。如果故意略過 lock 機制，隨便一跑就會發現有一堆錢在系統內憑空消失了 XD。這差距還不小，大約少了 20% 的錢... 雖然效能提升了一些，但是這樣的 code 你敢用嗎??

```csharp

public class LockAccount : AccountBase
{
    private decimal _balance = 0;
    private List<TransactionItem> _history = new List<TransactionItem>();
    private object _syncroot = new object();


    public override decimal GetBalance()
    {
        return this._balance;
    }

    public override decimal ExecTransaction(decimal transferAmount)
    {
        //lock (this._syncroot)
        {
            this._history.Add(new TransactionItem()
            {
                Date = DateTime.Now,
                Amount = transferAmount,
                Memo = null
            });
            return this._balance += transferAmount;
        }
    }
}

```

執行結果:

```log

Test Result for WithoutLockAccount: FAIL!
- Expected Balance: 20000
- Actual Balance: 16774
- Performance: 2000000 trans/sec

```

如果應試者能夠清楚的說明這些狀況跟原因，那麼這關就算通過了。很多工程師其實不善表達，或是表達的過程沒辦法很有系統的組織或說明，這時我只要聽到幾個關鍵字就夠了。包括:

* Lock
* Critical Section
* Racing Condition

前面提到的 "lock" 是解決方法，真正的原因是 ["racing condition"](https://en.wikipedia.org/wiki/Race_condition), 因為發生了同時做 "讀取" 後再 "寫入" 計算結果的動作，兩個動作重疊，就導致會有某些運算的結果被別的執行緒覆蓋掉了。

搭配 lock 的機制，則可以避免這種狀況。在 讀取 + 寫入 的動作尚未完成之前，其他並行的 讀取+寫入 動作會被擋在外面，直到前一個進行中的動作結束後才能接著進行。

Wiki 有篇文章: [Racing Condition](https://en.wikipedia.org/wiki/Race_condition#Example) 其實講的很清楚，看看文章內的範例就知道了。

![](/wp-content/uploads/2018/03/racing-condition-01.PNG)
> 正確的狀況，交易的結果正確

![](/wp-content/uploads/2018/03/racing-condition-02.PNG)
> 有問題的狀況，交易的過程發生交錯的讀取與寫入，交易結果不正確

各位讀者，這關你通過了嗎? :D



## 解法2. 搭配 SQL Transaction (資料庫交易的應用)

這個解法，因為實作容易，而且應用的情況比較普遍，雖然它適用於較大規模的情境 (跟上面的方法相比)，因此可能會有不少的應試者，答不出上一個解法 #1，反而答得出這個解法... 不過我還是按照我的排列順序，按照實際應用的規模上限來排序。

在實際上的應用，跟錢有關的大概都會找個資料庫存起來。因為跟錢有關，大部分的人都會選擇直接就支援交易的關聯式資料庫，這邊我就直接拿 SQL server 當作範例。其實觀念很簡單，只要你知道要透過 SQL server 的 transaction 來處理，這樣就夠了。來看看這段 code:

範例程式我挑選比較簡單明瞭的 [Dapper](https://github.com/StackExchange/Dapper), 沒有採用 Entity Framework。為了求簡潔，我也把 configuration 省掉了, 改成直接寫在code 裡面。阿北有練過，小朋友不要學...

```csharp

public class TransactionAccount : AccountBase
{
    private SqlConnection GetSqlConn()
    {
        return new SqlConnection(@"Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=AccountDB;Integrated Security=True;Connect Timeout=30;Encrypt=False;TrustServerCertificate=True;ApplicationIntent=ReadWrite;MultiSubnetFailover=False");
    }

    public override decimal GetBalance()
    {
        return this.GetSqlConn().ExecuteScalar<decimal>(
            @"select [balance] from [accounts] where userid = @name", 
            new { name = this.Name });
    }

    public override decimal ExecTransaction(decimal transferAmount)
    {
        return this.GetSqlConn().ExecuteScalar<decimal>(
            @"
begin tran
insert [transactions] ([userid], [amount]) values (@name, @transfer);
update [accounts] set [balance] = [balance] + @transfer where userid = @name;
select [balance] from [accounts] where userid = @name;
commit
",
            new { name = this.Name, transfer = transferAmount });
    }

}

```

超無腦的 code, 除了 ```ExecTransaction()``` 內的 SQL 加上了 transaction 之外 (其實你要用 .NET 提供的 ```TransactionScope``` 也可以，或是像這範例整個交易都集中在同一個 command 內的話，我記得 ADODB 預設也會把它包裝成一個 transaction 不需要特別另外處理)，就沒有特別的地方了。交易的處理完全不在 application server 端執行，整個交易都委託給 sql server 處理，所以相對程式碼就單純的多。只要你的交易都發生在同一組 DB 裡面，你就不用擔心交易結果的問題。DBMS 會確保你的交易正確性，也會確保你的指令符合 ACID 的原則。


直接來看看執行的結果:

```log

Test Result for TransactionAccount: PASS!
- Expected Balance: 176000.0000
- Actual Balance: 176000.0000
- Performance: 4294 trans/sec

```

背後的 table schema 長這樣 (對，我也把非關鍵的 Index / Constraint 都省掉了 XDDD):

```SQL

CREATE TABLE [dbo].[accounts] (
    [UserId]  NVARCHAR (50) NOT NULL,
    [Balance] MONEY         NOT NULL,
    PRIMARY KEY CLUSTERED ([UserId] ASC)
);

CREATE TABLE [dbo].[transactions] (
    [id]     UNIQUEIDENTIFIER DEFAULT (newid()) NOT NULL,
    [userid] NVARCHAR (50)    NOT NULL,
    [time]   DATETIME         DEFAULT (getdate()) NOT NULL,
    [amount] MONEY            NOT NULL,
    PRIMARY KEY CLUSTERED ([id] ASC)
);

```

DBMS transaction control, 這就是另一門學問了。害我想起當年在念書時，念到 DBMS (**D**ata**B**ase **M**anagement **S**ystem) 就有唸到 [concurrency control](https://en.wikipedia.org/wiki/Concurrency_control), 沒想到現在廿幾年後還能派上用場啊 :D

只是，這樣的設計，交易的範圍被限制在單一一組 DBMS 上啊! 以這個案例而言，我無法承受太多的連線數量。整個交易的上限，都限制在 DBMS 的處理能力。然而 RDBMS 就是這點最困難啊，由於 "關聯" 式資料庫，強調的就是關聯帶來的各種好處；相對的太多關聯就會難以切割，~~難以 scale out...~~ 當你需要 scale out 的時候，必須特別花心思去處理他，例如特別設置 partition (垂直 / 水平)，分表分庫，data sharding，甚至是直接在 application 層來處理。

~~這明顯違背 microservice / cloud native 的理念啊! 這也是為何服務的規模越大，越難看到 RDBMS 的原因。如果我們真的要邁向微服務，而且是 100+ instances 這種規模，這個作法是無法滿足需求的。要解決這樣的問題，那就繼續看下去...~~

**2021/03/06 修正**:

> 無意間發現這段敘述引起了熱烈的討論，我後面這段的說法容易讓人誤解，我做了點修正。RDBMS 強調 schema 的正規化, 藉由精準的 schema 定義，可以確保資料能進來的都是正確的，也能夠建立正確精準的索引來加速後續的應用。資料庫本身幫你處理掉大部分資料儲存及查詢，甚至組合的需求；也處理了交易的一致性，若要用 [CAP](https://zh.wikipedia.org/wiki/CAP%E5%AE%9A%E7%90%86) 來區隔，RDBMS 是把重心擺在 CA 兩個特性上 (也就是常聽到的 [ACID](https://zh.wikipedia.org/wiki/ACID))。  
>  
> 不過這是需要成本的啊，當你的應用需要更靈活的變化，需要比較靈活的變化 schema, 甚至是你需要結構化的資料 (例如 json / xml) 更甚於表格式資料 (table), 或是 CAP 三種特性你需要 CA 以外的組合，例如 AP (也就是 [BASE](http://c.biancheng.net/view/6495.html), Basically Available, Soft-state, Eventually Consistent) 等等，採用 NoSQL 會更適合。在 microsoervice / cloud native 的場景下，有些應用先天就必須面對這些問題，甚至有些 platform 的應用先天就無法在開發時期就定義全部的 schema 的應用，RDBMS 就不再是唯一的選擇。  
>  
> 事後想想，會造成誤會的應該是這段吧! 規模越大，包含服務量，也包含應用的複雜度，越來越容易踩到這類問題，越需要從 application 的設計角度來避免，無法單靠 DBA 在資料庫這端就解決掉。NoSQL 走相反的路線，專注在大量快速的儲存，相對查詢跟交易處理能力就弱了一些，需要 developer 花更多心思掌握 data structure 才能駕馭。在 cloud native 的應用情境下, 各個服務自行選擇合適的 DB 技術是很正常的，RDBMS / NoSQL 都有適合運用的場景，規模越大越容易碰到不得不用 NoSQL 的案例 (我原本要表達的是這意思)。這時開發人員就必須面對跨 DB 的問題，不論兩端是不是 RDBMS 或是 NoSQL, 包含下一段我要說明的分散式鎖定 (這也是分散式交易的基礎)。  
>  
> 所以熟悉 NoSQL 系列資料庫，搭配處理分散式交易或是鎖定的能力是必備的技能啊, 三年前寫這段腦袋其實是在想下一段的內容，因此簡單幾句帶過。既然被點名了，承認錯誤跟修正說明是必要的，我就保留原本的敘述 (加了刪除線的部分)，同時用註記的方式補上說明。



## 解法3. 搭配不支援交易的儲存體 (考分散式鎖定)

我會說問題必須先 "抽象化" 是有原因的。即使應用的情境，從單機版進化到 100+ instance(s) 的微服務版，觀念還是一樣的，就是你必須建立一個安全的臨界區 (critical section), 把不能分開執行的內容包在裡面。解法 #1 的 lock 如果作用範圍能擴大到所有的 100+ instance(s), 其實問題就解決了。

我這邊先假設，系統規模已經大到單一 SQL 資料庫無法負荷的地步，需要透過 elastic search / mongo 等等這類 no sql 的儲存機制時, 我該如何解決前面碰到的問題? 問題本身不難，關鍵仍然在如何做好 LOCK 而已，只是現在 LOCK 的範圍，必須從單機架構擴大到微服務架構時，實作的選擇就完全不同...

解決的關鍵，在於必須先解決分散式的鎖定機制 (distributed lock), 然後再用這個機制把更新的動作保護起來，確保沒有 racing condition 狀況發生。這邊我特地挑選 NOSQL 的代表 MongoDB 當作示範。MongoDB 不支援交易 (直到 2018/02 才釋出 4.0 會開始支援交易)，正好符合我期望的結果。LOCK 的部分若要擴大到 100+ instance(s), 其實只要找一個速度夠快的 storage, 讓所有的 instance(s) 共用來達到鎖定的目的就行了。高速的 share storage, 我直接挑選 Redis 來負責，同時搭配 RedLock 這個套件，可以把鎖定的機制，簡化成 IRedLock 物件就可以搞定了。這個 sample code 結構跟解法1 一樣，只是原本的一行可以解決的問題擴展為好幾行而已。來看看 code:

```csharp

public class DistributedLockAccount : AccountBase
{
    private RedLockFactory _redlock = null;

    private MongoCollection<AccountMongoEntity> _accounts = null;
    private MongoCollection<TransactionMongoEntity> _transactions = null;

    public DistributedLockAccount() : base()
    {
        MongoClient mclient = new MongoClient("mongodb://172.18.248.6:27017");
        MongoServer mserver = mclient.GetServer();
        MongoDatabase mongoDB = mserver.GetDatabase("bank");

        this._accounts = mongoDB.GetCollection<AccountMongoEntity>("accounts");
        this._transactions = mongoDB.GetCollection<TransactionMongoEntity>("transactions");
        this._redlock = RedLockFactory.Create(new List<RedLockEndPoint>() { new DnsEndPoint("172.18.254.68", 6379) });
    }

    public override decimal GetBalance()
    {
        var acc = this._accounts.FindOne(Query.EQ("Name", this.Name));
        return (acc == null)?(0):(acc.Balance);
    }

    public override decimal ExecTransaction(decimal transferAmount)
    {
        var resource = $"account-transaction::{this.Name}";
        var expiry = TimeSpan.FromSeconds(5);
        var wait = TimeSpan.FromSeconds(5);
        var retry = TimeSpan.FromMilliseconds(50);

        using (var redLock = this._redlock.CreateLock(resource, expiry, wait, retry))
        {
            if (redLock.IsAcquired)
            {
                AccountMongoEntity acc = this._accounts.FindOne(Query.EQ("Name", this.Name));
                if (acc == null)
                {
                    this._accounts.Insert(acc = new AccountMongoEntity()
                    {
                        _id = ObjectId.GenerateNewId(),
                        Name = this.Name,
                        Balance = transferAmount
                    });
                }
                else
                {
                    acc.Balance += transferAmount;
                    this._accounts.Save(acc);
                }

                this._transactions.Insert(new TransactionMongoEntity()
                {
                    _id = ObjectId.GenerateNewId(),
                    Date = DateTime.Now,
                    Amount = transferAmount
                });

                return acc.Balance;
            }
            else
            {
                throw new Exception();
            }
        }
    }
}

```


先看一下執行結果:

```log

Test Result for DistributedLockAccount: PASS!
- Expected Balance: 33574
- Actual Balance: 33574
- Performance: 490 trans/sec

```




至於環境的搭配，我這邊也是一樣，既然只是做 POC，我就一切從簡。前面的 SQL server 剛好我本機就有安裝 (.NET 陣營的人，機器裡有現成的 SQL Server 也是很正常的吧) 就沒另外準備了。這個例子用到的 Redis / Mongo, 我就直接用 Docker 直接建立。礙於其他的原因，我還是採用 windows container, 所幸 windows container 的接受度越來越高了，Redis 已經有好心人提供 windows 版本的 image, 而 Mongo 甚至是官方版本的 docker hub 就直接提供 windows 版本的 image..

自己寫 dockerfile 就可以省了，我直接用這兩行指令，準備我的測試環境:

```shell

docker run --rm -d -p 6379:6379 alexellisio/redis-windows:3.2

docker run --rm -d --name mongo -p 27017:27017 mongo:3.4-windowsservercore

```

不過，微服務架構的規模，只用單機來驗證，其實沒啥說服力啊。我本來想繼續把這個 sample code 改寫成微服務版本，然後真的開個 10 個 instance 來驗證，不過太多技術細節介入，會模糊掉重點 (還記得這篇文章是在講面試的白板題嗎? XD)

因此這邊的驗證，我就一切從簡了。只要能達到驗證的目的，讓你知道這樣的做法是可行的，其它能夠省略我就省略。這邊我改變一下測試方式，同樣的 code 我先編譯好 EXE，然後按照這樣的程序去測試:

1. 先用 mongo gui tools 查詢，確認測試前 andrew 帳戶的餘額 (balance)
1. 用 script (批次檔) 一次啟動 10 個 process 跑測試程式
1. 忽略測試程式本身的訊息，全部執行完畢後用 (1) 的步驟確認最終的餘額 (balance)
1. 比對 (1) 跟 (3) 的結果，確認一下最後收到的金額是否正確?


執行 (2) 之前查看 mongo db 的狀態, 帳戶餘額 **33574** 元
![](/wp-content/uploads/2018/03/mongo-before.png)


執行 (2) 之後查看 mongo db 的狀態, 帳戶餘額 **233574** 元
![](/wp-content/uploads/2018/03/mongo-before.png)


雖然前後大約執行了 7 分鐘，總共平行的處理掉 200000 筆交易，分成 10 process x 20 concurrent threads 平行處理，在
不支援交易的 MongoDB 仍然可以很精準的執行交易控制，連一塊錢都沒有算錯!

不過，在這邊的實作，地雷還是很多。這類鎖定或是平行處理的問題，其實都在資工的 "作業系統" 這門課裡面有交代... 很多細節我沒講到，建議有興趣的朋友們好好去翻一下課本...。我隨便舉個例子就好，你知道如何實作 "分散式鎖定" 的機制嗎? 你如何確保你用的 LOCK 機制是可靠的? OS 課本就會教到，要自己實做 critical section 一定要有個不可分割的 ["compare and swap / exchange"](https://en.wikipedia.org/wiki/Compare-and-swap) 指令才行。現今的 CPU 甚至內建這樣的指令，讓 OS 能拿來應用到多工的處理。如果你懂這些原理，你可以在你手邊尋找各種符合這要求的機制來實作。有這樣能力的人，隨手都能取得適當的資源來解決問題，從 storage server, share file system, database ... 等等大概都難不倒它。

相對的，你基礎不夠扎實的話，請盡量避開親自去實作這些很底層的機制，盡可能的挑選可靠的套件來使用。上面的例子我就是參考了這篇文章 [Distributed Lock for Redis](https://redis.io/topics/distlock)，從裡面挑選了 RedLock 這個基於 Redis 的 Distributed Lock 套件來使用。我使用的是這套: [RedLock.net](https://github.com/samcook/RedLock.net), 有興趣的朋友可以花點時間研究一下。

至於運作的原理，用上面講 racing condition 的兩張圖就足夠說明了。

![](/wp-content/uploads/2018/03/racing-condition-01.PNG)

執行的關鍵，就是在上圖中，執行 "read value" 之前先取得鎖定，在 "write back" 後再釋放鎖定就可以了。鎖定可能會取得失敗，因此需要 retry (上述 sample code 的 wait / retry 就是處理這件事)。如果你的 code 取得鎖定後就掛掉了，納為了避免這個鎖定永遠被占住，因此也會有所訂的時間限制，超過就會被強制釋放 (上述 sample code 的 expire 就是處理這件事)。

看到這邊，其實原理都一樣啊，只是每個環節都要找不同的實作方式替代而已。如果你的抽象化做的夠好，甚至你可以寫出大部分的 code 都能 reuse 前提下，做到各種規模都能適用的程式碼。



# 總結

寫到這邊，不管看這篇文章的人是面試主管想要找現成的面試考題題庫，還是你是想要找工作正在上網惡補的工程師都好，看完我寫的這篇不會讓你突然間就找到工作或是找到人 XD, 如果是想速成，看我的文章應該沒有用啦! 這也是我第一次跳開技術討論，以尋找人才為目的的面試心得文章。如果對這系列的內容有任何意見或看法，歡迎在 FB 或是在下方的 comments 留言給我，我會很感激的 :D

團隊是否到位，是微服務架構能否成功的關鍵之一。尤其是在台灣，普遍不重視這些基礎觀念的建立，要建構這樣的團隊更是困難，因此我也打算把這系列文章併到整個微服務架構的系列文章內，能幫助到找人的 team leader，或是能幫助到有心在軟體業發展的朋友們，都算是功德一件吧! 同時也想看看以後有沒有機會把這系列文章，集結成冊發行出書..

如果你是求職者，平日花些時間準備與思考這些問題，我相信真的遇到伯樂的話，你的表現一定會令面試官印象深刻的。就算不找工作，在開發的路上碰到問題，你也一定能更清楚的思考該怎麼解決它。

如果你是面試主管的話，也請斟酌使用，問的太深入，面試者答得出來你卻接不下去，那也是很尷尬的 XDD。平日多訓練自己思考這些問題，我想除了應用在找人，在平日系統的設計或是架構的規劃上一定也有幫助的。

對這篇文章提到的範例程式，可以到這邊下載:

[InterviewQuiz, tag:publish-2018-0325](https://github.com/andrew0928/InterviewQuiz/releases/tag/publish-2018-0325)

