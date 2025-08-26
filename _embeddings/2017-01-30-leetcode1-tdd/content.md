![LeetCode Logo](/images/2017-01-30-leetcode1-tdd/leetcode-logo.png)

其實在這十幾年的工作期間，不時地都有人問我 coding 能力怎樣才能更上一層樓? 我的答案都是一樣的老生常談，就是 "要打好基礎"。
不過這實在很抽象啊! 最近有空就會上 [LeetCode.com](https://leetcode.com/) 來練習一下 coding 技巧，這其實是個練功的好方法，
你可以把 LeetCode 當成訓練 coding 能力的健身房。

我就拿這當作主題，分享一下我的作法，還有為什麼這樣做的道理吧! 其實用到的技巧都不算很新穎，但是卻很實用。幾個能提升 code 品質的
基本技巧 (尤其是 [TDD](https://zh.wikipedia.org/wiki/%E6%B5%8B%E8%AF%95%E9%A9%B1%E5%8A%A8%E5%BC%80%E5%8F%91)，以及測試相關的環節) 
若能徹底落實，你寫出來的 code 品質就會大幅提升。有心鑽研 coding 技巧的朋友們可以參考看看!


<!--more-->

{% include series-2017-tdd.md %}


# 核心問題: 我為何想要寫這篇?


其實我沒有收 LeetCode 的廣告費，用不著替它介紹這服務啊 XD，不過這不介紹後面就寫不下去了 XD。解 LeetCode 的題目，主要是鍛鍊資料結構
跟演算法的運用能力。不過這麼棒的題庫跟測試案例，其實可以做更好的利用啊! 我的想法是在解題的過程，是否也能思考如何練習寫程式的基本功?
而不是只專注在 "我解了幾題"，或是 "我的排名" 這些指標身上。

基本功夫練得好的話，對有心走這行的人是很有用的。王森在[這篇文章](https://whhnote.blogspot.tw/2011/02/blog-post_07.html)裡，有句話講得很到位:

*"神雕俠侶裡頭的獨孤求敗，晚年只會拿樹枝和別人比武，可是你拿再厲害的刀劍就是無法打敗他。"*

事實就真的是這樣啊! 本站的老讀者，大概都記得當年 (Orz, 九年前了...) 我寫過五篇文章 ["如何學好寫程式"](http://columns.chicken-house.net/tags/#系列文章-如何學好寫程式)，
就是在探討這些主題:

* [該如何學好 "寫程式" ??](/?p=65) 27 Sep 2008
* [該如何學好 "寫程式" #2. 為什麼 programmer 該學資料結構](/?p=62) ?? 01 Oct 2008
* [該如何學好 "寫程式" #3. 進階應用 - 資料結構 + 問題分析](/?p=60) 08 Oct 2008
* [該如何學好 "寫程式" #4. 你的程式夠 "可靠" 嗎?](/?p=56) 20 Oct 2008
* [該如何學好 "寫程式" #5. 善用 TRACE / ASSERT](/?p=53) 03 Nov 2008

這幾篇都是講基本功，講如何練好 coding 的本事，寫出高品質程式的必要觀念。不過當年的工具沒有現在這麼容易上手，同樣的觀念，在這個年代
有更有效率的做法。這篇文章等於是這系列的延伸，我就拿如何寫好 LeetCode 解題程式為目標，來探討看看如何有效率的把它做到最好。

會想寫這篇，主要的動機勉強能跟 Microservices 沾得上邊。Microservices 因為把單一系統拆分成多個獨立的服務，因此在工程及管理上的要求
會更嚴格。換句話說團隊的 coding 水準，還有團隊的開發流程 (比如版本控制，API 相容性，Code Quality 等等) 沒有達到一個水準的話，導入
Microservices 只會更痛苦而已。為了要扮演好架構師的角色，其實有必要先替團隊把這些環節理順，往後的開發才會順利。

簡單的說，如果你的 code 品質不夠好，硬上 Microservices, 將來碰到的 debug 狀況會更為棘手。當年剛開始研究 Azure 時，我還記得
Ruddy Lee 老師講的一句話 (特地跟 [Ruddy Lee](https://www.facebook.com/ruddyl.lee) 前輩致敬一下):

**"要上雲端，要先測試"**  
(導讀: [如果你認為Windows Azure 的Unittest 不 Work了，那你就錯了!](https://ruddyblog.wordpress.com/2011/01/))

其實 Ruddy Lee 老師真是先知，當年他闡述的很多雲端化的觀念跟架構，現在套用在 Microservices 一樣都適用。其實雲端的 PaaS / SaaS 使用
的架構，就是 Microservices 的前身啊，只是以前是雲端大廠在做 Microservices, 這兩年因為 Container 技術當道，打破大量快速佈署的門檻，
才讓 Microservices 走入每個開發團隊跟私有雲內部環境。因此我現在的想法跟當年 Ruddy Lee 老師一樣:

**"要導入 Microservices, 要先測試!"**

不過很多人其實都還不曉得自己要什麼。我想了很久，與其直接來介紹 TDD 的各種好處，不如替各位找個合適的切入點，讓讀者自己去體驗這樣
做的好處。有了動機，之後的學習就不再是個問題了。到 LeetCode 這類網站練習，其實就是 TDD 的最佳訓練場。我就分享一下我自己的進行方式。



# 番外篇: LeetCode (Online Judge Service) 是啥?

LeetCode.com 其實只是眾多 Online Judge Service 之一，這類網站目標用戶就是 software engineer，收集了各類練習題的題庫，也收集了各大軟體公司
 (Google, Microsoft, Facebook 等等) 的面試上機考題 (不過這部分要付費)。題庫，大致分為演算法 (algorithm), 資料庫 (database), 
腳本 (shell scripts) 等等這幾大類。網站提供的除了題庫之外，也提供線上測試的功能。你可以把你的 code 上傳 (submit)，網站會編譯你的 code, 
並且把題庫搭配的 test case 一個一個代進你的程式執行看看，確定你的code 是否真的能算出正確答案。

除了題庫及演練之外，這類網站也扮演了社群平台的角色，提供空間給同好討論各種解題的方式及技巧。我覺得很棒的地方是，上面的題目都專注在
問題本身，你只要挑選你熟悉的語言就可以開始解題了，不需要會太多的 framework, 因此進入門檻也不高。就如同之前我分享的，現在的工程師
跟市場都太在意 "功能"，因此大家學習的重點都擺在 framework 的使用，或是工具的使用上。但是這些技能也是最容易被淘汰的啊，沒有幾年就
換一輪了。有心從事軟體開發的朋友們，你們需要累積的是更基礎的觀念與知識，這些基礎打好再來學 framework 才會事半功倍。透過這些網站的練習，
也正好能讓你專注在這些基本功夫上，不會被眼花撩亂的 framework 干擾。

貢獻這些題目的人，還有其他的解題者，都可以貢獻測試案例 (test case), 測試案例會包含預期的正確答案。因此當你的 code submit 上去後，
網站服務就能靠這些測試案例來驗證你的 code 是否能正確的解出問題。其實這就跟 TDD (Test Driven Development) 的核心觀念一致，先寫測試
再寫程式。只是測試程式網站已經準備好了，你只要想辦法寫出能通過所有 test 的 code 即可。這是第二個我推薦 LeetCode 來練功的原因，很多
人嫌寫測試很麻煩，講破嘴他也不會動手寫測試... 現在有人幫你寫好測試，你總沒有理由拒絕了吧? 在這類網站上面練習，也能讓你在不知不覺之中
了解 TDD 帶來的好處，養成習慣後，往後你也會願意開始接受 TDD 的觀念與做法，code 的品質就自然提升了。

像 LeetCode 這樣的網站，題庫搭配的 test case 會隨著大家的貢獻不斷增加，你也無法事先知道所有的 test case, 唯一通過的方法就是
想辦法把 code 按照需求寫好而已。網站會依據幾個結果來判定你的 code 好壞:

1. **正確性**: 是否通過所有的 test case ? 你不會知道總共有多少 test case, 要作弊也沒辦法...
1. **效能**:   是否在指定的時間內 (CPU time) 完成所有的測試?
1. **排名**:   按照花費的時間 (CPU time), 與所有通過 (1) (2) 的其他對手對比，看看你的效能的名次百分比 (%)

因為重點在演算法，所以通常計較的不是你的 code 系統層面的問題 (比如多一層呼叫會比較慢之類的問題)，而是你的演算法好壞，選用的
資料結構是否合適，解題需要花費的[時間複雜度](https://zh.wikipedia.org/wiki/%E6%97%B6%E9%97%B4%E5%A4%8D%E6%9D%82%E5%BA%A6) (Time Complexity) 高低的影響比較大。

講這麼多實在有點抽象，貼幾個範例大概就懂了:

**[Two Sum](https://leetcode.com/problems/two-sum/)**  
題目很簡單，給你一個陣列 (```int[] nums```)，外加預期的結果 (```int target```), 你要從陣列中找出哪兩個數字加起來會等於 ```target```。
該題題目的畫面，大致上就長這個樣子:

![sample](/images/2017-01-30-leetcode1-tdd/leetcode-sample.png)

頁面上半就是題目及範例的測試案例，右上則是統計，你可以知道這題有多少人次上傳 code (total submissions), 有多少上傳 code 通過測試 (total accepted),
這題的難度以及題目的提供者等資訊。

下半就是一個簡單的 online source code editor, 支援 syntax highlight, 也會自動配對括號, **[Run Code]** 則會用預設的 test case
在 server side 編譯並執行你的 code, 按 **[Submit Solution]** 則會正式提交你的 code 去執行所有的 test case, 並且給你評估的結果:

![submission detail](/images/2017-01-30-leetcode1-tdd/leetcode-submission-details.png)




# 第一步: 把開發環境搬到 Visual Studio

> 其實，這類網站有個不成文的規定，就是你不應該公開討論，甚至分享你的 code。這樣會讓這些服務的公正性大打折扣。因此我只分享我解題的
> 進行過程跟技巧，讓大家能更善用工具及方法來練習自己 coding 的能力，而不會貼出題目完整的 code, 請各位諒解。

前面講過，這網站的題目就是用 TDD 的觀念來設計整個使用流程的，你的目標就是寫出一段 code, 能在一定的執行時間內通過所有的 test case.
但是在網站上寫 code, 也太辛苦了吧? 擺著地表最強 (沒有之一) 的開發工具 [Visual Studio](https://www.visualstudio.com/zh-hant/) 不用，實在有點說不過去... 

我換個複雜一點的題目 (難度: Hard) 來當範例，比較看得出效果。我挑的是這題: [#214, Shortest Palindrome](https://leetcode.com/problems/shortest-palindrome/)

> Palindrome 這個字是 "迴文" 的意思，也就是一個字串從左到右念，跟從右到左念都是一樣的。
> 題目簡單的說就是給你一個原始字串，要你找出最短要在左邊補上甚麼字串，才能讓原始字串變成蛔文。

首先，我開了 class library 的 project: **_214_ShortestPalindrome**, 把題目給我的 ```class Solution {...}``` 搬進來:


```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace _214_ShortestPalindrome
{

    // leetcode start ----------------------------------
    public class Solution
    {
        public string ShortestPalindrome(string s)
        {
            // ...
            throw new NotImplementException();
        }
    }
    // leetcode end ------------------------------------
}

```

接下來我要想辦法模擬網站如何執行我的 code 的作法。過去我是自己寫 console app, 不過太辛苦了。我直接加了個 Unit Test project,
在裡面填入如何 "測試" 我的 code.


```csharp
using System;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using _214_ShortestPalindrome;
using System.Text;
using System.Collections.Generic;

namespace _214_ShortestPalindromeTest
{
    [TestClass]
    public class UnitTest1
    {

        private Solution SubmitHost = null;

        [TestInitialize]
        public void Init()
        {
            // 產生我的解題程式 instance
            this.SubmitHost = new Solution();
        }

        [TestMethod]
        public void LeetCodeTestCases()
        {
            // 測試第一筆 test case
            Assert.AreEqual<string>(
                this.SubmitHost.shortestPalindrome("aacecaaa"), 
                "aaacecaaa");

            // 測試第二筆 test case
            Assert.AreEqual<string>(
                this.SubmitHost.shortestPalindrome("abcd"), 
                "dcbabcd");
        }
    }
}

```

Test Case 裡面的兩組測試數據，我是直接拿題目上的 Example 貼上來的。到這個階段，我就可以不透過網站的服務，Local PC
就能直接執行我的 code 了，如果你願意多打幾行 code, 也可以把測試拆成兩個，或是改成 Data Driven Test, 透過外部的資料檔
來驅動測試，你就可以用 visual studio 的 Test Manager 直接看到每一筆測試的結果:

![test result](/images/2017-01-30-leetcode1-tdd/leetcode-result.png)

從這個測試結果，我們可以看到幾個資訊，都忠實的呈現出來了:

1. 測試是否通過?
1. 測試執行的時間有多長?
1. 若測試有問題時，可以點 output 看看 (左上) 是哪一筆資料所驅動的測試失敗?

測試的 code 只要小改一點:

```csharp
[TestMethod]
        [DataSource("Microsoft.VisualStudio.TestTools.DataSource.XML", "parameters.xml", "add", DataAccessMethod.Sequential)]
        public void LeetCodeTestCases()
        {
            string given = this.TestContext.DataRow["given"] as string;
            string expected = this.TestContext.DataRow["expected"] as string;
            string actual = this.SubmitHost.ShortestPalindrome(given);

            this.TestContext.WriteLine($"given:    {given}");
            this.TestContext.WriteLine($"expected: {expected}");
            this.TestContext.WriteLine($"actual:   {actual}");

            Assert.AreEqual<string>(
                actual,
                expected);
        }
```

直接把所有的 test cases 放到資料檔 ```parameters.xml``` (XML):

```xml
<?xml version="1.0" encoding="utf-8" ?>
<tests>
  <add>
    <given>aacecaaa</given>
    <expected>aaacecaaa</expected>
  </add>
  <add>
    <given>abcd</given>
    <expected>dcbabcd</expected>
  </add>
  <add>
    <given>abbacd</given>
    <expected>dcabbacd</expected>
  </add>
</tests>
```

資料驅動的測試方式，我就不多說了 (這不是這篇的主題，略過)。有興趣的朋友可以參考這兩篇:

* [How To: Create a Data-Driven Unit Test](https://msdn.microsoft.com/en-us/library/ms182527.aspx)  
* [BACK TO BASICS : DATA DRIVEN UNIT TESTING](http://prasadhonrao.com/back-to-basics-data-driven-unit-testing/)


OK，做到這裡，我們已經把要開始對付 LeetCode 題庫的環境準備好了，接下來你可以盡情的在你 PC 上面思考怎麼解題了。
我刻意把整個環境弄到將來解題的 code 能夠一字不漏的從 visual studio 直接貼上 LeetCode 就能執行的程度。
如果你要 submit code 還要手動調整一堆 code, 你的開發過程一定會不順利，因為當你已經絞盡腦汁想演算法時，其他環節一定會搞錯，
因此環境的問題調整到越單純越好。這個原則在其他地方也都不變，這也是 CI / CD / DevOps 等等方法論的背後理念。

到這裡就結束了嗎? 還早... 我們就延續這個問題繼續走下去... 這篇先到這裡，祝大家新年快樂~ 也請大家繼續支持第二篇 :D

 * 第二篇: [不只是 TDD #2, 兩個版本自我驗證 + 執行期驗證](/2017/01/31/leetcode2-assert/)