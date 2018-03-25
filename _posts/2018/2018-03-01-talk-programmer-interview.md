---
layout: post
title: "架構師觀點 - 面試題分享 #1, 線上交易的正確性"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師", "面試經驗"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2018/03/whiteboard-interviews.png
---

![](/wp-content/uploads/2018/03/whiteboard-interviews.png)

最近一直在思考，團隊裡的後端工程師能力是否到位，是微服務架構能否成功的關鍵之一。我該怎麼鑑別出面試者有沒有這樣的能力? 最有用的就是出幾個實際的應用題，讓面試者在白板上面說明。最近這一輪面試，談了不下幾十位吧，索性就把我幾個常問的白板考題整理起來寫成這系列的文章，改善團隊成員的問題，也算是朝向微服務化的目標跨出一大步。

在思考要考啥的過程中，我曾經考慮過像 leetcode 那樣的題庫，或是從各種架構問題 (如網友提供的資訊: [System Design Primer](https://l.facebook.com/l.php?u=https%3A%2F%2Fgithub.com%2Fdonnemartin%2Fsystem-design-primer&h=ATOBoA1AEZDD-BCyQX0joLXwbt8IszgoC-hx5OmukiZiSVh5EcpH36_4K7AB5-pRh80Rd8TAsPvqPLGpwz6KDtK8l0_TaAqDbKQa9XcZEwrHeFTpEw))，後來發現這樣考實在太 "硬" 了，都存在某種 "標準答案"。可是我覺得那不是我要考的，因為我不是要找跟我一樣的架構師啊，我想找的是有能力自己思考，也有能力實作微服務架構的工程師。他或許不需要有從無到有規劃與設計架構的能力，但是我會希望他碰到各種問題時，能以微服務(或是 cloud native) 的角度去思考解決方式。

因此，我重新想了一些題目，我改用 "應用題" 的方向，來測試看看應試者解決問題的思考過程。我試著先把題目 "抽象化"，先問問應試者解決問題的方向為何? 接著再問在不同規模的環境下 (EX: 從單機到 NLB，到微服務，從 SQL 到 NOSQL...)，會有那些不同的實作方式。這樣的測驗方式正好可以讓我瞭解應試者思考的規模極限在哪裡。題目的方向我想了交易的正確性、演算法的應用、巨量資料的處理策略、API 的設計、以及物件導向的觀念等等。其實這些都沒有標準答案，面試者大部分也沒辦法一次到位的就答出來，正好可以看出應試者的能力到哪裡。

很多人都說過: "沒有最完美的架構，只有最合適的架構"。這句話講的很有道理，可是對大部分的人來說都是打高空啊... 問題就在於要找出 "最合適" 的架構，本身就是件很困難的事情。因此這系列的白板題，我都是朝向這個方向去設計的。這些問題其實也都是過去我自己空閒時拿來練習的題材，因此這些問題我自己也都實作過，底下我就順帶 PO 出我自己的版本供參考。第一篇先來試試水溫，就先練習一下交易相關的問題吧! 

<!--more-->


# QUIZ: 線上交易的正確性

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

            if (expected_balance == actual_balance)
            {
                Console.WriteLine($"Test PASS! Total Time: {timer.ElapsedMilliseconds} msec.");
            }
            else
            {
                Console.WriteLine($"Test FAIL! Total Time: {timer.ElapsedMilliseconds} msec. Expected Balance: {expected_balance}, Actual Balance: {actual_balance}");
            }
        }
```

接下來，實作方式就有差別了，這系統可大可小，按照規模順序來看 (由小到大)，我對每個層級的工程師的期望:

|職級|規模|解決方案(關鍵字)|
|===|====|===============|
|Junior Engineer|1 host|Lock, Racing Condition, Critical Section|
|Senior Engineer|10+ hosts|ACID, SQL Transaction|
|Architect|100+ hosts|Distributed Lock|


## 解法1. 單機運作 (只考基本觀念: Lock)

* 關鍵字: lock
* 對應層級: junior engineer

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

        public override IEnumerable<TransactionItem> GetHistory()
        {
            return this._history;
        }
    }
```


執行結果:

```log
```


這邊的關鍵，在於執行交易時 (```ExecTransaction()```) 的過程中，系統必須做兩件事:

1. 在交易紀錄 ```this._history``` 這個 ```TransactionItem``` 的集合裡面，加上一筆這次交易的資訊
1. 在帳戶資訊紀錄目前餘額 ```this._balance``` 的變數中，需要將這次的轉帳金額累加上去。

這組動作，必須符合 [ACID](https://zh.wikipedia.org/wiki/ACID) 的要求。最簡單的做法就是把它包裝成 [Critical Section; 臨界區](https://zh.wikipedia.org/wiki/%E8%87%A8%E7%95%8C%E5%8D%80%E6%AE%B5)。在 Critical Section 的範圍內，是不允許有並行的狀態的。單機的情況下，直接使用 C# language 或是 OS 本身的 Lock 機制就足夠了。上面的 sample code 就只有這樣而已。

我這邊另外準備個對照組，只拿掉 lock 那行而已，其他通通都不變。如果故意略過 lock 機制，隨便一跑就會發現有一堆錢在系統內憑空消失了 XD。這差距還不小，足足少了一半的錢... 雖然效能提升了五倍左右，但是這樣的 code 你敢用嗎??

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
Test FAIL! Total Time: 2470 msec. Expected Balance: 100000000, Actual Balance: 53291163
```

如果應試者能夠清楚的說明這些狀況跟原因，那麼這關就算通過了。很多工程師其實不善表達，或是表達的過程沒辦法很有系統的組織或說明，這時我只要聽到幾個關鍵字就夠了。包括:

* Lock
* Critical Section
* Racing Condition

前面提到的 "lock" 是解決方法，真正的原因是 ["racing condition"](https://en.wikipedia.org/wiki/Race_condition), 因為發生了同時做 "讀取" 後再 "寫入" 計算結果的動作，兩個動作重疊，就導致會有某些運算的結果被別的執行緒覆蓋掉了。

搭配 lock 的機制，則可以避免這種狀況。在 讀取 + 寫入 的動作尚未完成之前，其他並行的 讀取+寫入 動作會被擋在外面，直到前一個進行中的動作結束後才能接著進行。

Wiki 有篇 [文章](https://en.wikipedia.org/wiki/Race_condition#Example) 其實講的很清楚，看看文章內的範例就知道了。

![](/wp-content/uploads/2018/03/racing-condition-01.PNG)

![](/wp-content/uploads/2018/03/racing-condition-02.PNG)


各位讀者，這關你通過了嗎? :D



## 解法2. 搭配 SQL Transaction (資料庫交易的應用)

這個解法，因為實作容易，而且應用的情況比較普遍，雖然它適用於較大規模的情境 (跟上面的方法相比)，因此可能會有不少的應試者，答不出上一個解法 #1，反而答得出這個解法... 我還是按照我的排列順序，按照實際應用的規模上限來排序。

在實際上的應用，跟錢有關的大概都會找個資料庫存起來。因為跟錢有關，大部分的人都會選擇直接就支援交易的關聯式資料庫，這邊我就直接拿 SQL server 當作範例。其實觀念很簡單，只要你知道要透過 SQL server 的 transaction 來處理，這樣就夠了。來看看這段 code:

範例程式我挑選比較簡單明瞭的 Dapper, 沒有採用 Entity Framework。為了求簡潔，我也把 configuration 省掉了, 改成直接寫在code 裡面。阿北有練過，小朋友不要學...

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

超無腦的 code, 除了 ```ExecTransaction()``` 內的 SQL 加上了 transaction 之外 (其實你要用 .NET 提供的 ```TransactionScope``` 也可以)，就沒有特別的地方了。交易的處理完全不在 application server 端執行，整個交易都委託給 sql server 處理，所以相對程式碼就單純的多。只要你的交易都發生在同一組 DB 裡面，你就不用擔心交易結果的問題。DBMS 會確保你的交易正確性，也會確保你的指令符合 ACID 的原則。


直接來看看執行的結果:

```log
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

DBMS transaction control, 這就是另一門學問了。害我想起當年在念書時，念到 DBMS (DataBase Management System) 就有念到 transaction control, 沒想到現在廿幾年後還能派上用場啊 :D

只是，這樣的設計，交易的範圍被限制在單一一組 DBMS 上啊! 以這個案例而言，我無法承受太多的連線數量。整個交易的上限，都限制在 DBMS 的處理能力。然而 RDBMS 就是這點最困難啊，由於 "關聯" 式資料庫，強調的就是關聯帶來的各種好處；相對的太多關聯就會難以切割，難以 scale out...

這明顯違背 microservice / cloud native 的理念啊! 這也是為何服務的規模越大，越難看到 RDBMS 的原因。如果我們真的要邁向微服務，而且是 100+ instances 這種規模，這個作法是無法滿足需求的。要解決這樣的問題，那就繼續看下去...





## 解法3. 搭配 NOSQL, 或是其他不支援交易的儲存體 (考分散式鎖定的應用)

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

        public class TransactionMongoEntity : TransactionItem
        {
            public ObjectId _id { get; set; }
        }

        public class AccountMongoEntity : AccountItem
        {
            public ObjectId _id { get; set; }
        }
    }

```    

這邊的實作，地雷很多。我不曉得會看這篇文章的，是面試的主管? 還是要應徵工作的人? 這類鎖定或是平行處理的問題，其實都在資工的 "作業系統" 這門課裡面有交代... 很多細節我文章其實都沒交代到，建議有興趣的朋友們好好去翻一下課本...。我隨便舉個例子就好，你知道如何實作 "分散式鎖定" 的機制嗎? 你如何確保你用的 LOCK 機制是可靠的? OS 課本就會教到，要時做 critical section 一定要有個不可分割的 ["compare and swap / exchange"](https://en.wikipedia.org/wiki/Compare-and-swap) 指令才行。如果你懂這些原理，你可以在你手邊尋找各種符合這要求的機制來實作。有這樣能力的人，隨手都能取得適當的資源來解決問題，從 storage server, share file system, database ... 等等大概都難不倒它。

相對的，你基礎不夠扎實的話，請盡量避開親自去實作這些很底層的機制，盡可能的挑選可靠的套件來使用。上面的例子我就是參考了這篇文章 [Distributed Lock for Redis](https://redis.io/topics/distlock)，從裡面挑選了 RedLock 這個基於 Redis 的 Distributed Lock 套件來使用。我使用的是這套: [RedLock.net](https://github.com/samcook/RedLock.net), 有興趣的朋友可以花點時間研究一下。

至於運作的原理，用上面講 racing condition 的兩張圖就足夠說明了。

![](/wp-content/uploads/2018/03/racing-condition-01.PNG)

執行的關鍵，就是在上圖中，執行 "read value" 之前先取得鎖定，在 "write back" 後再釋放鎖定就可以了。鎖定可能會取得失敗，因此需要 retry (上述 sample code 的 wait / retry 就是處理這件事)。如果你的 code 取得鎖定後就掛掉了，納為了避免這個鎖定永遠被占住，因此也會有所訂的時間限制，超過就會被強制釋放 (上述 sample code 的 expire 就是處理這件事)。

看到這邊，其實原理都一樣啊，只是每個環節都要找不同的實作方式替代而已。如果你的抽象化做的夠好，甚至你可以寫出大部分的 code 都能 reuse 前提下，做到各種規模都能適用的程式碼。











-----------
* 關鍵字: distribution lock
* 對應層級: architect

步驟:

1. 先取得鎖定
1. 執行交易
1. 解開鎖定

不用 SQL 處理整個交易
只用 REDIS 處理 LOCK，其餘交易可以透過 MONGO









NOSQL 交易要自己處理

最基本的處理方式，就是 LOCK (悲觀的鎖定)


有效率的處理方式，樂觀的鎖定





# 評分標準

[ ] Junior Engineer
基本上能答出關鍵字 ```lock``` 就算過關了，任何型態的 lock 都可以。
能講出 lock 我就認為是孺子可教，有機會晉級繼續深入的問下去...

[ ] Senior Engineer
能夠精準的把交易封裝在 SQL script 內，或是講出關鍵字 ```transaction``` 就算過這關了。












# 2. 分散式交易的處理 (2pc)







<!--more-->

其實我不大喜歡考那種有標準答案的，尤其是找的到線上題庫的那種。會想寫這系列文章，老實說我也不擔心面試者先練習在來應付...。我在乎的
是背後的思考過程，如果先看完這幾篇文章還能答得出背後的觀念，那也算是有吸收進去，我寫這些文章救多造福一個人了。

這些都是很典型的應用，現在大概有做 B2C 網站或是 APP，有扯到付費服務等等的，或多或少都會碰到一些這類問題。我問題設計的方向都是先給
一個情境，問問面試者，如果這問題丟給你，你會打算怎麼解決他?

這些問題當然也有現實的環境需要考量，因此也沒有標準答案。同樣的問題，套用在一天 1000 筆交易的網站，跟一秒鐘 1000 筆交易的網站，處理
方式是完全不同的。底下我盡可能地從各種不同規模的應用，來說明我的想法。

# 1. 線上交易測驗

# 2. 帳務處理測驗 (銀行帳戶利息計算)

# 3. 大量資料串流分析測驗

# 4. OOP - Sort

# 5. OOP - Game Of Life