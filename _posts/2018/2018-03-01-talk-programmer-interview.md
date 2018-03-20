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

其實我一直認為，就算再不起眼的小事，認真的做好還是會看到成效的。最近一直在進行後端工程師的招募與面試，深深覺得考應用題，請面試者
在白板上說明他的解決方法是很重要的。想想後端工程師的能力是否到位，也是微服務架構能否成功的關鍵之一，索性就把我幾個常問的白板考題
整理起來寫成這系列的文章，也算是個新的嘗試。

從畢業退伍後開始工作到現在，眼看就要邁入第 20 年了... 這十幾年來，我沒有仔細算過，不過面談過的工程師應該有好幾百人了吧?
在面試這件事我雖然稱不上專業，但是在評估一個工程師有沒有把 code 寫好的能力還是有的，因此我決定在紀念 20th 這天到來之前，能完成
這系列的文章。

我先就過去的經驗，大致把我常問的問題分類一下。我不大會去考很細的語法，或是工具的操作 (因為我自己也不見得會 XDDD)，另外有畫面的
技術也不是我擅長的，因此我大多圍繞在 API 的設計，系統架構的設計，大流量或是大量資料的處理，還有物件導向的觀念，以及各種 source code 
寫法的優缺點等等角度來判斷。這些其實都沒有標準答案，有些也是我主觀的看法而已。如果這些經驗剛好是你需要的，盡管拿去用沒關係，我都寫出來了
就是要分享的..

這些問題其實也都是過去我自己空閒時拿來練習的題材，因此這些問題我自己也都實作過，底下我就順帶 PO 出我自己的版本供參考。第一篇先來試試
水溫，就先練習一下跟線上交易有關的問題吧! 

<!--more-->

> 我知道我的 code 寫的不夠好，請別鞭我 XD, 這些 sample code 只是為了解釋觀念而已, 我刻意省略很多細節, 也省略很多必要的檢查。純粹為了表達觀念而已，也別因為我的 code 就嫌棄 windows 跟 .net 都是爛東西... 我應該還沒有這種影響力 XDD

這系列的考題跟說明，我都會用同樣的模式進行。我會舉個實際的應用情境 (不是像 leetcode 或是單純考演算法那種)，然後聽聽看面試者的思考過程。
這些題目其實都不算難，套用在不同的規模，也會有不同的解決方式。通常單機，多機 (load balance)，或是大規模、大資料量、大流量的情況下各應該
怎麼處理。各位就把他當成能否勝任 junior engineer / senior engineer / architect 的標準吧!


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












# 2. 分散式交易的處理







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