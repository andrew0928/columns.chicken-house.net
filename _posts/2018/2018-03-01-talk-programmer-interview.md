---
layout: post
title: "架構師觀點 - 面試題分享 #1, 線上交易的正確性"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師", "面試經驗"]
published: true
comments: true
redirect_from:
logo: 
---




最近一直在思考，團隊裡的後端工程師能力是否到位，是微服務架構能否成功的關鍵之一。該怎麼鑑別出面試者有沒有這樣的能力? 最有用的就是
出幾個實際的應用題，讓面試者在白板上面說明。最近這一輪面試，談了不下幾十位吧，索性就把我幾個常問的白板考題整理起來寫成這系列的文章，
也算是個新的嘗試。

我原本想說從 leetcode 之類的網站抄幾題來就夠用了，不過試了幾次之後發現沒有達到我預期的效果。Leetcode 考的是演算法，以及把你想法
寫成 code 的能力，但是我要的不是這樣啊! 我想要找的人選，應該是碰到實際的問題，能想出適合的解決方案的人。同樣的問題，不同的規模或是
環境，就會有不一樣的答案，也是常常有人說的 "沒有最好的架構，只有最適合的架構" 一樣，我就是想找出有這樣能力的人。

因此，我花了點時間思考我要考的問題，跟我想挑出有什麼樣能力的人選。交易的正確性、無法使用 RDBMS 時的交易處理及資料處理，API 的設計，
以及物件導向的觀念等等。其實這些都沒有標準答案，面試者大部分也沒辦法一次到位的就答出來，因此在溝通討論的過程中，可以看出面試者的思考
方式。同樣的問題，我也會試著擴大需求的規模 (EX: 從單機到 NLB，到微服務，從 SQL 到 NOSQL...)，來測驗看看面試者能處理的極限在哪裡。

這些問題其實也都是過去我自己空閒時拿來練習的題材，因此這些問題我自己也都實作過，底下我就順帶 PO 出我自己的版本供參考。第一篇先來試試
水溫，就先練習一下跟線上交易有關的問題吧! 

<!--more-->


# QUIZ: 線上交易的正確性

這題可以算是送分題了，如果連最基本的答案都答不出來，我又需要你處理跟錢 (代幣 / 遊戲幣我也算在內) 有關的問題時，我實在是不敢把這任務交給你啊!
題目很簡單，我先定義一個 C# 的 abstract class, 假設有個處理銀行帳戶的 engine 長的像這樣:

```csharp
public abstract class AccountBase
{
    /// <summary>
    /// 取得帳戶餘額
    /// </summary>
    /// <returns></returns>
    public abstract long GetBalance();


    /// <summary>
    /// 將指定金額轉入該帳戶
    /// </summary>
    /// <param name="transferAmount"></param>
    /// <returns></returns>
    public abstract long Transfer(long transferAmount);
}
```

請告訴我，要如何確保這 engine 不會算錯錢? 這裡補充一下，實際的世界裡，"錢" 這種東西，不應該憑空產生出來，也不會憑空消失的。就像能量守恆
定律一樣，在一個封閉系統內，錢只會從某個地方跑到另一個地方，整個系統的所有金額總和一定是不變的，除非有錢從外部的系統轉移進來，或是轉出去。
就如同 RDBMS 講的 ACID 一樣，沒有任何原因可以讓交易做一半，無論任何情況都應該保持上述的條件才對。

所以我會怎麼驗證呢? 我會用 unit test 的方式，寫幾個 test case 來驗證這個 engine。一些基本的邏輯測試我就省略了 (連邏輯都搞錯也不用談了)，
我直接跳到我最在意的交易一致性來看:

對 user 的戶頭, 分 10000 個 threads, 同時對這個戶頭進行存款，每次存 1 元，連續存 10000 次。理論上程式執行完畢後，這個戶頭應該會增加 100000000 元才對。

測試程式的片段如下。我暫時不打算跟 visual studio, mstest 等等 framework 綁的太緊, 因此 unit test 的部分我先用 console project 簡化,
DI (dependency injection) 的部分也先簡化略過:

```csharp
/// <summary>
/// NOTE: 同時建立 10000 個 threads, 重複對同一個 account 進行 10000 次的轉帳運算，每次轉入1元到帳號內。
/// 正確的情況下，原本餘額是0元的帳號，經過多次轉帳後，帳戶餘額應該有 1000000000 元才對。
///
/// 若未正確處理好 concurrent processing 的問題，測試結果會無法通過。這問題請在多核心的系統上面測試。
/// </summary>
static void Main(string[] args)
{
    // skip DI, 建立指定的 account 實做機制
    AccountBase bank = new SingleHost.SingleHostAccount();

    long concurrent_threads = 10000;
    long repeat_count = 10000;

    List<Thread> threads = new List<Thread>();

    for (int i = 0; i < concurrent_threads; i++)
    {
        Thread t = new Thread(() => { for (int j = 0; j < repeat_count; j++) bank.Transfer(1); });
        threads.Add(t);
        t.Start();
    }

    foreach (Thread t in threads) t.Join();


    long expected_balance = concurrent_threads * repeat_count;
    long actual_balance = bank.GetBalance();

    if (expected_balance == actual_balance)
    {
        Console.WriteLine($"Test PASS!");
    }
    else
    {
        Console.WriteLine($"Test FAIL! Expected Balance: {expected_balance}, Actual Balance: {actual_balance}");
    }


}
```

接下來，實作方式就有差別了，這系統可大可小，按照規模順序來看 (由小到大):



## 解法1. 單機運作 (只考基本觀念: Lock)

* 關鍵字: lock
* 對應層級: junior engineer

不需考慮 load balance, 也不需要考慮底層的 data storage, 資料的儲存直接用變數或是物件，例如 ```List<T>``` 之類的 collection 即可。
有點概念的話，這程度真的是放水了 XD，其實只要考驗你懂不懂 "lock" 的重要性而已...

參考版本的答案，只要知道要 "lock" 就輕鬆過關。可以自己用 C# 的 ```lock``` 指令，或是用 ```Interlocked``` 替代都可以:

```csharp
public class SingleHostAccount : AccountBase
{
    private long _balance = 0;


    public override long GetBalance()
    {
        return this._balance;
    }

    public override long Transfer(long transferAmount)
    {
        return Interlocked.Add(ref this._balance, transferAmount);
    }
}
```

```log
Test PASS! Total Time: 12842 msec.
```



另外準備個對照組，如果故意略過 lock 機制，隨便一跑就會發現有一堆錢在系統內憑空消失了 XD
這差距還不小，足足少了一半的錢... 雖然效能提升了五倍左右，但是這樣的 code 你敢用嗎??

```csharp
    public class SingleHostAccount : AccountBase
    {
        private long _balance = 0;


        public override long GetBalance()
        {
            return this._balance;
        }

        public override long Transfer(long transferAmount)
        {
            //return Interlocked.Add(ref this._balance, transferAmount);
            return this._balance += transferAmount;
        }
    }
```

```log
Test FAIL! Total Time: 2470 msec. Expected Balance: 100000000, Actual Balance: 53291163
```


通常面試考到這裡，我就會問問為何有這種現象? 基本上只要能答得出幾個關鍵字就算過關了。前面提到的 "lock" 是解決方法，真正的
原因是 ["racing condition"](https://en.wikipedia.org/wiki/Race_condition), 因為發生了同時做 "讀取" 後再 "寫入" 計算結果的動作，兩個動作重疊，就導致會有某些運算的結果被
別的執行續覆蓋掉了。

搭配 lock 的機制，則可以避免這種狀況。在 讀取 + 寫入 的動作尚未完成之前，其他並行的 讀取+寫入 動作會被擋在外面，直到前一個
進行中的動作結束後才能接著進行。

前面提到的 wiki 其實講的很清楚，看看這個 [範例說明](https://en.wikipedia.org/wiki/Race_condition#Example) 就知道了。



## 解法2. 搭配 SQL Transaction (資料庫交易的應用)

* 關鍵字: transaction
* 對應層級: junior engineer

其實這個 "對應層級" 我想了很久，照規模來看，透過 DB 應該是比較適用中型的規模，不過就難度而言，這個好像還比上一個用 ```lock``` 的直覺，想到最後
我決定把這兩個都歸在 junior engineer 的層級...

實際上的應用，跟錢有關的大概都會找個資料庫存起來。因為跟錢有關，大部分的人都會選擇支援交易的 RDBMS，這邊我就直接拿 SQL server 當作範例。

其實觀念很簡單，只要你知道要透過 SQL server 的 transaction 來處理，這樣就夠了。來看看這段 code:


```csharp

```




## 解法3. 搭配 NOSQL, 或是其他不支援交易的儲存體 (考分散式鎖定的應用)

* 關鍵字: distribution lock
* 對應層級: architect



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