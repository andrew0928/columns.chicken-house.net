---
layout: post
title: "不只是 TDD #2, 兩個版本自我驗證 + 執行期驗證"
categories:
- "系列文章: 如何學好寫程式"
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["專欄","技術隨筆","TDD","Microservices","架構師"]
published: true
comments: true
redirect_from:
logo: /images/2017-01-31-leetcode2-assert/leetcode2-logo.jpg
---

![LeetCode Logo](/images/2017-01-31-leetcode2-assert/leetcode2-logo.jpg)

接續 [上一篇](/2017/01/30/leetcode1-tdd/)，如果你以為要在本機解 LeetCode 的題目，只是把 test cases 改成 unit test 就結束的話，那
我就不需要寫這幾篇文章了。如果你的目標只擺在 "解題"，那的確看第一篇就夠了。如果這是老闆或是客戶給你的 "需求"，那
你得訂更高的目標去執行才行，包含正確性，執行效率之外，還有可維護性等等考量。

這篇就會跳出大家常看到的 "狹義" 的 TDD 做法。TDD 絕對不只是寫單元測試而已。你總是會有想像不到的狀況發生，我面對這問題時採取
兩個做法來解決:

1. 把單元測試，從開發階段延伸到執行階段
1. 自動化產生新的測試案例，讓機器隨機擴大測試案例的涵蓋範圍

(2) 可能抽象一點，我的想法是先創造一個 "**可敬的對手**"，再讓這個對手不斷隨機的產生測試案例來測試自己，同時由這個對手來告訴我做的對不對... 

這情境有沒有很熟悉? 2016 的大事: [AlphaGo 打敗世界冠軍](https://www.twreporter.org/a/artificial-intelligence-go-game?gclid=Cj0KEQiA5bvEBRCM6vypnc7QgMkBEiQAUZftQBbf57xWCILjw3aiPBnX17nE_JorZ2v6zV9ioFdPqRUaAktx8P8HAQ)，背後一個關鍵成功因素，
就是 AlphaGo 沒日沒夜的跟自己對練，累積的經驗。我們面對的問題不像圍棋這麼複雜 (10<sup>170</sup> 種組合)，實作起來很容易的，
唯一的障礙是你想不想做而已...。

<!--more-->

延續上一篇的案例 [#214, Shortest Palindrome](https://leetcode.com/problems/shortest-palindrome/), 接著來看看要怎麼進行..



{% include series-2017-tdd.md %}


# 第二步: 雖然可恥確有用! 先寫出保守的版本!

LeetCode 上面的題庫，大都是以演算法為主。一個問題可能存在多種解法，每種解法都有它的時間複雜度。一般來說每種問題
都有所謂的 "最佳演算法"，也會有最佳的時間複雜度。

舉例來說，排序 (SORT) 就是個典型的例子。最容易實作的是泡泡排序法 ([bubble sort](https://en.wikipedia.org/wiki/Bubble_sort))，
時間複雜度是 O(n<sup>2</sup>)。平均來說最佳的演算法是快速排序 ([quick sort](https://en.wikipedia.org/wiki/Quicksort)), 時間複雜度
是 O(n log n)。

念過資料結構，都知道要用 quick sort, 這時就直接 implement 就好了。但是如果你碰到一個新問題，連正確性都還
搞不定時，或是還在思考怎麼設計解題的演算法時，我就非常建議採用這個章節要說明的做法: **先寫出保守的第一版**出來!


所謂的 "**保守**"，在這邊指的就是最容易實作，就能解開問題的作法，而不見得是最佳或是最有效率的作法。以前面的 sort 來說，bubble sort 
就屬於這種。不需要很高明的 coding skill 就能寫得出來。為何要這樣做? 這就是在準備 **可敬的對手**! 我們先看看 "迴文" 這案例的第一版:

```csharp
    public class BasicSolution
    {
        private string source = null;

        public string ShortestPalindrome(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            this.source = s;

            char target = s[0];
            for (int right = s.Length - 1; right >= 0; right--)
            {
                if (s[right] != target) continue;
                if (check(right) == true)
                {
                    // got it
                    return this.padtext(right);
                }
            }
            return null;
        }

        private bool check(int right)
        {
            for (int i = 0; i <= (right - i); i++) if (this.source[i] != this.source[right - i]) return false;
            return true;
        }

        private string padtext(int right)
        {
            StringBuilder sb = new StringBuilder();
            sb.Append(this.source.Substring(right + 1).Reverse().ToArray());
            sb.Append(this.source);
            return sb.ToString();
        }
    }
```

由於我目標訂得比較保守，暫時就不去追求最佳的時間複雜度了。這版的作法是，若原始字串 ```s``` 的長度是 ```n```, 我從最後一個字元 ```s[n-1]``` 往
前找，找到第一個 ```s[n-1] == s[0]``` 的位置，找到後就交由 ```check(int i) {...}``` 這函式接手，比對 ```s[1]``` 跟 ```s[n-2]```, 若也相同的話就
再繼續比對 ```s[2]``` 與 ```s[n-3]``` ..., 依此類推，直到 ```s[i]``` 跟 ```s[n-i-1]``` 重疊為止。

若 ```check(int i) {...}``` 的比對都通過，代表 ```s[0] ~ s[i]``` 這段既有的字串就是迴文了，剩下只要再把 ```s[i+1] ~ s[n]``` 後面的部分，字串
反轉後補到最前面，就是題目要求的 "最短迴文" 了。這就是 ```padtext(int i) {...}``` 在做的事情。



# 第三步: 如何 "可靠" 的改良演算法?

OK, 理所當然的，這個版本應該能順利通過已知的測試。不過問題來了... 測試案例實在太少了啊，效能可能也不好。
從 LeetCode 題目上拿到的 test cases 只有三個，加上我換個演算法，可能主軸的 code 都要改寫了。我如何在既有的基礎上，確保我的新版
是正確的? 寫新的 code 風險是很高的，想知道為什麼的朋友們可以看看這篇:

* [寫碼容易，讀碼難：工程師，千萬別重寫程式碼](https://www.inside.com.tw/2015/07/26/rework)

回到原題，我如何在既有的基礎上，用科學且有效率的方法寫出第二版? 我期望得到執行結果跟保守版一模一樣，但是效率好上好幾倍的版本...。
如果你充分了解 TDD 的精神，就能理解我的想法了。若新程式執行結果要跟保守版本一模一樣，那就代表所有測試案例，兩個版本的反應必須一模一樣。
既有的測試案例可以拿來測試新的版本，而如果你還能自動產生額外的測試案例，則保守版本的執行結果，你就能拿它來驗證新版本的執行結果是否 "正確" 
(正確與否的判定，就在於跟保守版本是否一致) 了。

因此，以這個案例，我可以大量隨機的產生各種字串，丟給兩個版本去比對。或是我可以在有限範圍內 (EX: 長度在 100 以內的字串) 用程式碼
跑出所有可能的結果 (26<sup>1</sup> + 26<sup>2</sup> + ... + 26<sup>100</sup> 種組合)，用最完整的涵蓋率來進行測試。如果能有足夠的
測試案例加單元測試，我就能更專注在改變演算法及做好最佳化的任務。我必須先解決眼前的問題是, **可執行的測試案例太少**:

1. **靜態的測試**: 別無他法，由人工來判斷 "最可能" 出錯的 input string, 手動加入 data source 內。
例如超長字串，或是 1000 個字的字串，999 個字元都一樣等等極端的狀況。

2. **動態的測試**: 透過程式產生測試的資料，再把這些資料餵給單元測試..
AlphaGo 跟 AlphaGo 自己對奕就是屬於這種 (硬要跟時事沾上邊)。例如我們可以產生 10000 組 test cases, 每組都隨機產生
長度在 100 chars 內, 隨機由 a ~ z 的字元組合的字串來進行測試。

(1) 其實還不難了解，就是在 .csv or .xml 內多加幾筆資料就是了。(2) 要寫隨機產生字串也不是難事。不過, 每筆測試案例都
需要 input, 還有 expected 預期的正確答案啊，如果 input 是隨機產生的, expected 怎麼來?

...

啊哈! 想到了嗎? 如果我們已經先有了一組 "保守"，"可靠"，"可恥但有用" 的解決方案的話，我們就有能力先用這組保守的版本計算出答案，
再來驗證新版的計算結果是否正確了。其實這技巧我們從小就在用了，每次數學課老師都說算完了要 **驗算** 一次，就是在做一樣的事情。
狹義的 "驗算" 只是同樣方法再重新計算一次而已，只能避免計算錯誤的狀況。不過電腦不會計算錯誤啊，錯的 code 算兩次，都會得到
一模一樣的錯誤結果... 我指的 "驗算" 比較廣義，是除了原本作法之外，用其他的做法來驗證結果的正確性。

接下來，單元測試就可以調整一下了，我追加了第二項測試: ```CheckingTestCases()```, 會隨機產生 100 組長度不超過 10000 字元，由 a ~ z 字元
組合的字串，並且比對兩個版本的執行結果。

原本的版本，我把 class name 從 ```Solution``` 改為 ```BasicSolution```, 新的解法則沿用 ```Solution``` 這個 class name, 目的很簡單，就是為了
將來要貼到 LeetCode 時不用再手動改 code.

```csharp
        
    [TestClass]
    public class UnitTest1
    {
        private Solution SubmitHost = null;
        private BasicSolution CheckingHost = null;
        private const string text = "abcdefghijklmnopqrstuvwxyz";
        private static Random rnd = new Random();

        [TestInitialize]
        public void Init()
        {
            // 產生我的解題程式 instance
            this.SubmitHost = new Solution();
            this.CheckingHost = new BasicSolution();
            
        }
      

        [TestMethod]
        public void CheckingTestCases()
        {
            foreach(string randomtext in GenRandomText(10000, 100))
            {
                Assert.AreEqual(
                    this.SubmitHost.ShortestPalindrome(randomtext),
                    this.CheckingHost.ShortestPalindrome(randomtext));
            }
        }

        /// <summary>
        /// 產生隨機的字串。
        /// 字串長度不超過 maxlength (隨機)，字串內容限定 a ~ z (小寫)，隨機出現
        /// </summary>
        /// <param name="maxlength"></param>
        /// <returns></returns>
        private static IEnumerable<string> GenRandomText(int maxlength, int run)
        {
            for (int index = 0; index < run; index++)
            {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < rnd.Next(maxlength + 1); i++)
                {
                    sb.Append(text[rnd.Next(26)]);
                }
                yield return sb.ToString();
            }
        }
    }

```

當然，如果新版本開發很複雜，不想每次都要花很多時間產生測試案例的話，你也可以改一下程式，另外寫個 console app,
用保守版本的 code, 產生 100 組測試案例, 產生靜態的 test cases, 加到 data source 內，把它當作 (1) 靜態的測試案例也可以。
操作方式不同，但是目的是一樣的。你一樣是透過第一組保守的程式，來驗證新的程式是否如預期般的運作。相信會看我文章的朋友都能了解這一點。




# 第四步, 在主程式中插入 "維護" (assert) 的程式碼

單元測試，不管是動態還是靜態，自動還是手動，對於測試的 "單元" 來說，他終究是黑箱測試啊... 雖然單元測試已經比 QA 人員能更
觸及程式內部的元件了，但是各種的測試終究是從外部來進行的。接下來要探討的是，"單元" 內部的測試怎麼做? 還有只有在 "RUNTIME"
才有可能碰到，或是各種預料之外的狀況如何預防?

先參考在我之前的這篇文章:

* [該如何學好 "寫程式" #5. 善用 TRACE / ASSERT](/?p=53) 03 Nov 2008

還是要再大推這本快 30 年的書了: write solid code, 很多讓你寫出好 code 的方針我到現在都還在用。書中提到 excel 試算表
的計算邏輯就是一例，用很笨很慢的版本，來驗證高度最佳化的版本這做法，我一直覺得這是很高明的手段... 花一點固定的時間成本，
換來往後這個範圍內的驗證都可以完全自動化不需要人工介入，實在是個很划算的投資。比起你聘請再多的測試人員，都不見得能達到
一樣的水準。

這文章有提到當年 C 的年代，就在使用的維護巨集: ASSERT，透過巨集 (Macro) 與條件式編譯 
([Conditional Compilation](https://en.wikipedia.org/wiki/Conditional_compilation))，只在 DEBUG 模式下啟用的
檢查機制。然而 Assert 引發的 Fail 代價太高無法讓 user 承受，因此它只存在於除錯用的版本，給開發人員及測試人員使用。
我一直認為他是 unit test 的老祖宗啊! 基本上它也是個微型的單元測試，讓你穿插在程式碼的每個地方，只要你認為需要就可以放。
放得越多越好，一旦程式在執行過程中觸發了某個 ASSERT 的條件，也許debugger 視窗就會跳出來，或是你的程式就會
碰到 unhandled exception 中止執行。Assert 維護巨集跟 UnitTest 單元測試的最大差別，就是單元測試僅止於 Dev / Build Time,
而維護巨集則可以延伸到 Runtime。

這觀念也就是軟體工程常講到的 ["Fail Fast"](https://en.wikipedia.org/wiki/Fail-fast), 一旦出錯了就立刻處理，你才能
用最低的成本解決他。也許很多狀況不是 unit test 能測得出來的，因此你必須把 ASSERT 埋在正式版本的 code 內。但是這些
code 埋太多勢必會影響效能，使用者也無法接受程式碼隨時會崩潰，因此一般而言都會用條件式編譯，讓你可以選擇是否要 Fast-Fail
的功能。一般常用的 Release / Debug Mode, 其中一個目的就是開關這些 Assert 。

這邊我要舉的例子，是 LeetCode 上的另一個題目 [ZumaGame](https://leetcode.com/problems/zuma-game/) 裡的案例。
ZumaGame, 就類似 Candy Crush 一樣，是個只有一維的消去遊戲 (Candy Crush 是二維)，這題目就是要你算出最少要幾個步驟才能消光
給定的牌組 (board)。由於計算過程較複雜，往往跑出來結果不如預期時，我必須花費很大的精力去觀察，到底是我的 code 有 bug, 還是
我的 algorithm 不正確? 能在第一時間先區分這兩者，能省下我不少的精力。

我的作法，就是在主要的解題程式中，穿插輔助 debug 及檢查各種狀態的 code。做這些準備的同時，我還不能讓它影響 submit 上去 LeetCode
的評比結果 (真虛榮..) XD。我的措施包括:

1. 搭配 Debugger, 自訂 ```ToString()``` 準備隨時要印出訊息的 code:
覆寫 (override) 物件的 ```ToString()```, 我就能在 debugger 上面直接看到對我有意義的物件狀態。如下圖，紅線的部分就是 ```ToString()``` 產生的

![debugger](/images/2017-01-31-leetcode2-assert/leetcode2-tostring.png)

但是這些 code, 在真正 submit 時又是多餘的, 因此我用 ```#if (...)``` 來控制他。我不用原本內建的 Debug / Release, 因為我不曉得
上傳後的 code, LeetCode 到底是用什麼模式編譯的? 因此為了保險起見，我自己宣告了一個 ```#define LOCAL_DEBUG```, 這樣就能確保
LeetCode 那邊絕對沒有這筆定義，上傳上去的 code, 這些 ```#if (...)``` 包起來的段落都會被剃除。我就能在同一份 code 內，兼顧效能與維護性了。

```csharp
#if (LOCAL_DEBUG)
            public override string ToString()
            {
                StringBuilder sb = new StringBuilder();
                foreach (Node n in this.CurrentBoard) sb.Append(n.ToString());
                return sb.ToString();
            }
#endif
```

2. 更複雜的例子, 程式碼中我運用了一些統計資料, 來協助我的演算法做決策。當結果不如預期時，我想要馬上就判斷是 Bug 還是演算法問題?
因此我在每個可能影響到統計資料的地方，都插入一段check, 確保統計資料跟原始資料是一致的, 若不一致，ASSERT 會馬上警告我。這小動作
可以讓我在除錯過程中的守備範圍大幅縮小，縮小到人腦能完全掌握的程度。

我先準備 ```AssertStatisticData()```, 正常狀況呼叫他什麼事都不會發生，但是若 ```LOCAL_DEBUG``` 有被定義，且統計資訊跟實際狀況
不一致的話，就會引發 ```Exception```:

```csharp
            private void AssertStatisticData()
            {
#if (LOCAL_DEBUG)
                Dictionary<char, int> stat = new Dictionary<char, int>() { { 'R', 0 }, { 'Y', 0 }, { 'B', 0 }, { 'G', 0 }, { 'W', 0 } };
                foreach (Node n in this.CurrentBoard)
                {
                    stat[n.Color] += n.Count;
                }
                foreach (char color in new char[] { 'R', 'Y', 'B', 'G', 'W' })
                {
                    if (stat[color] != this.CurrentBoardStatistic[color]) throw new Exception();
                }
#endif
            }
        }
```

至於呼叫 ```AssertStatisticData()``` 這個函示，以及其他零星的各種確認，就像底下的案例穿插在各個需要的地方:

```csharp
            private void ApplyStep(GameStep step)
            {
#if (LOCAL_DEBUG)
                // check
                if (this.CurrentBoard.Count <= step.Position) throw new Exception();
                if (this.CurrentHand[step.Color] == 0) throw new Exception();
#endif

                // check statistic here
                this.AssertStatisticData();

                if (this.CurrentBoard[step.Position].Color == step.Color)
                {
                    this.CurrentBoard[step.Position].Count++;
                }

                // ...

                // check statistic here
                this.AssertStatisticData();

```                

這作法好處很多，唯一的限制與缺點，就是你沒有事先埋好 ASSERT，那就不用想了...




# 結論

這系列短文，只寫了兩篇就寫完了 XD, 其實這兩篇講的觀念跟九年前 ["如何學好寫程式"](http://columns.chicken-house.net/tags/#系列文章-如何學好寫程式) 系列的觀念沒啥不同啊，只是
隨著時代跟工具的進步，落實的方法不大一樣而已。

現在有更多資源及更棒的工具，來支撐你寫出高品質的程式。但是這一路看下來，你會發現真正的瓶頸都不在於你會
那些 language, 會哪些 framework, 或是會哪些 skill? 重點還是在背後驅動你學習與做事的 knowledge 跟 concept。
這些才是我一直強調的 "基礎"。

其實這樣的技巧 (用新舊版本自我驗證) 是很有用的。我在將大型單一服務，切割成多個較小的服務，用微服務架構重構系統時，
這樣的方式也幫了我很多忙。重構的前提就是希望能改善程式碼體質，但是不應該影響任何可見的執行結果。這時如果你有針對
舊系統寫好測試，那就再好不過了! 若無也不用擔心，你可以在 runtime 比照這篇文章的方法，在各個地方都埋下新舊版本執行
結果的比對。有這些測試來護航，相信你的重構作業會順利的多!

資訊軟體業變化很快，變化的是這些工具及技術本身，但是這些 knowledge 跟 concept 其實變化不大。我九年前的文章
都還可以拿出來參考了，Microsoft 那本 Write Solid Code 都要三十年了，也是有值得參考的地方。其他 (跟本文無關)
我常拿出來參考的兩本書 (世紀末軟體革命, 物件導向設計模式) 也是。這些基礎有打好，新的技術你學了馬上就知道該怎麼用，
累積這些經驗跟能力才是走這行的核心競爭力啊。

又是碎碎念的兩篇文章，過年期間趁空檔整理這陣子玩 LeetCode 的心得，也分享我的經驗給想繼續在軟體業發展的朋友們!
祝大家新年快樂 :)






