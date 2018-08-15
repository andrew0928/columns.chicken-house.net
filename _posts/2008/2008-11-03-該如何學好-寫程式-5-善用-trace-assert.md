---
layout: post
title: "該如何學好 \"寫程式\" #5. 善用 TRACE / ASSERT"
categories:
- "系列文章: 如何學好寫程式"
tags: [".NET","C#","作品集","專欄","技術隨筆","有的沒的","物件導向"]
published: true
comments: true
permalink: "/2008/11/03/該如何學好-寫程式-5-善用-trace-assert/"
redirect_from:
  - /columns/post/2008/11/03/e8a9b2e5a682e4bd95e5adb8e5a5bd-e5afabe7a88be5bc8f-5-e59684e794a8-debug-mode.aspx/
  - /post/2008/11/03/e8a9b2e5a682e4bd95e5adb8e5a5bd-e5afabe7a88be5bc8f-5-e59684e794a8-debug-mode.aspx/
  - /post/e8a9b2e5a682e4bd95e5adb8e5a5bd-e5afabe7a88be5bc8f-5-e59684e794a8-debug-mode.aspx/
  - /columns/2008/11/03/e8a9b2e5a682e4bd95e5adb8e5a5bd-e5afabe7a88be5bc8f-5-e59684e794a8-debug-mode.aspx/
  - /columns/e8a9b2e5a682e4bd95e5adb8e5a5bd-e5afabe7a88be5bc8f-5-e59684e794a8-debug-mode.aspx/
wordpress_postid: 53
---
哈哈，這篇拖的夠久了 :P

上篇扯太多，寫到一半寫不完就留到這篇了。寫出可靠的程式，這是軟體工程師的基本要求。上篇提到了 TRACE / ASSERT 的應用，來複習一下:

> TRACE: 原本是 C 的除錯用巨集，目的是用適合的方式輸出除錯用的訊息，用來跟一般的訊息輸出有所區別。因為用的是不同的方式輸出，可以很容易的統一關掉。隨著工具的進步，輸出的方式也越來越適合除錯，比如輸出到開發工具的除錯視窗，或是輸出成記錄檔等等。

> ASSERT: 也是除錯用巨集，它接受一個 bool 參數，輸入值為 TRUE 時一切正常，就像沒呼叫一樣，輸入 FALSE 則會中斷程式，或是輸出顯目的警告訊息。目的在於確保程式的每個步驟情況都如預料般的順利。

這兩個東西從 C 的巨集，衍生出各種語言及環境都有各自的版本。它的目的很簡單，就是 [Writing Solid Code] 裡提到的:

> 用同一套程式碼，同時維護兩個版本 (RELEASE / DEBUG)，讓錯誤自動跑出來。

<!--more-->
{% include series-2008-good-programmer.md %}


雖然這本書提到了不少技巧，正確的應用 TRACE / ASSERT 是最基本的。但是那些細節並不是主要的重點。重點是你在寫 CODE 時有時時刻刻記得要盡量減少 BUG 嗎? 你有正確的擬出對策嗎? 來看看上回最後一段範例程式:


加上 ASSERT 的算分程式碼:
```csharp
public static int ComputeQuestionScore(XmlElement quiz_question, XmlElement paper_question)
{
    int totalScore = 0;
    int itemCount = quiz_question.SelectNodes("item").Count;
    Trace.Assert(quiz_question != null);
    Trace.Assert(paper_question != null);
    Trace.Assert(paper_question.SelectNodes("item").Count == quiz_question.SelectNodes("item").Count);
    //
    //  如果都沒作答, 此題放棄
    //
    if (paper_question.SelectNodes("item[@checked='true']").Count == 0)
    {
        return 0;
    }
    //
    //  題目的配分
    //
    int quiz_score = int.Parse(quiz_question.GetAttribute("score"));
    //
    //  答對一個選項的分數
    //
    int item_score = quiz_score / itemCount;
    for (int itemPos = 0; itemPos &lt; itemCount; itemPos++)
    {
        XmlElement quiz_item = quiz_question.SelectNodes("item")[itemPos] as XmlElement;
        XmlElement paper_item = paper_question.SelectNodes("item")[itemPos] as XmlElement;
        //
        //  算成積
        //
        if (quiz_item.GetAttribute("correct") == paper_item.GetAttribute("checked"))
        {
            totalScore += item_score;
        }
        else
        {
            totalScore -= item_score;
        }
    }
    Trace.Assert(totalScore &gt;= (0 - quiz_score));
    Trace.Assert(totalScore &lt;= quiz_score);
    return totalScore;
}
```


各位仔細看一下加上 ASSERT 的地方。大家寫程式，通常都是腦袋裡想著 "**我要處理什麼問題**" ，很少人會去想錯誤處理的部份。沒錯，這部份的確是吃力不討好，以此例來說，光是傳進來的參數就有可能狀況百出了。正常的流程都寫不完了，誰還有力氣去把這些錯誤都擋下來?

不過最容易出錯的地方也在這裡。我常在跟其它工程師說，正確的資料 (參數) 傳進來，本來就應該有正確的答案傳出去。難的是錯誤的資料傳進來，你還得回應 "正確" 的錯誤訊息回去，這才真的是個挑戰。這時 ASSERT 的效果就出來了。你可以把 ASSERT 想像成 "宣告" 的子句。以 line 5 ~ 7 行為例:

確保傳入參數是正確的:
```csharp
Trace.Assert(quiz_question != null);
Trace.Assert(paper_question != null);
Trace.Assert(paper_question.SelectNodes("item").Count == quiz_question.SelectNodes("item").Count);
```


這三行看在我眼裡，意思就是:

> 這兩個參數不能是 NULL，而且兩個 XML ELEMENT 都要有一樣數量的子節點 (Element)，否則就不惜代價警告我

同樣的，在程式的中間，還有傳回值之前，也都可以用同樣的方式來替你的程式 "把關"。再來看看算完成績後，要把值傳回去之前的 CODE:

確保傳回值的範圍正確的程式碼:
```csharp
Trace.Assert(totalScore >= (0 - quiz_score));
Trace.Assert(totalScore <= quiz_score);
return totalScore;
```

這兩行的意思就是:

> 不管成績怎麼算，每張答案卷最後的總分一定介於 0 ~ 滿分之間。一樣，有例外的話就不惜代價警告我。


聽起來蠻狠的，不惜代價...，不過使用 ASSERT 的話就真的是這樣。通常碰到 ASSERT 後，程式不是進 DEBUGGER 就是直接關掉了。不過請大家注意一下，並不是到處加上 ASSERT 你的程式就沒問題了。要搞清楚加上它的目的是什麼。它要抓的是你程式的 BUG，不是執行期的錯誤 (比如 USER 輸入錯誤的值，或是必填的資料沒填等等)。執行期的錯誤，你還是得乖乖的寫程式，不能用 ASSERT 替代。

舉例來說，如果最後算出來的分數是負的，則會觸動 return 前的 ASSERT。有些有點經驗又有點兩光的 PROGRAMMER 可能會自己顯示一些錯誤訊息。但是這跟本不干 USER 的事啊! 會出現這種情況，錯的一定是 "程式" 本身，也就是你看到 ASSERT 警告後就該來改程式抓 BUG 了。加上 ASSERT 的目的就是在你的程式到處布下眼線，任何一個地方偵測到不對勁，馬上通知你來處理。

當你有心把程式寫好時，你才會覺的這樣作是必要的，而不是累贅。你眼線布的越多，BUG就越難藏在你的程式裡。相對的，如果傳進來的參數就不對了，那應該怎麼辦?

這時就要小心分清楚你要抓的是 BUG 還是做錯誤處理了。如果參數是 USER 直接輸入的，那收到 NULL 或是錯誤的值本來就有可能 (吃芝蔴那有不掉燒餅的...)，你需要的是老老實實寫好錯誤處理的流程。但是如果你的 API 早已嚴格定義不接受 NULL，卻還是有白目的工程師硬把 NULL 傳給你的 API，那這時就是 BUG 了，應該用 ASSERT 抓出來，然後找到冤大頭叫他改程式。

不過這樣的 CODE 可不能交到 USER 手上。想像一下如果你正在用 WORD 打文件，結果碰到一個小 BUG，ASSERT 就跳出警告訊息要中止程式，你連存檔都來不及，大概會抓狂吧。這時就是一份程式碼兩種版本的作法發威的地方了。交給 USER 的程式，就應該是切到 RELEASE MODE (或是關掉 ASSERT / TRACE) 編譯的版本。這時所有的 TRACE / ASSERT 好像完全消失一樣，程式就如同一般情況運作。

當 USER 回報一些很難抓到的 BUG 時，這時就可以打開 ASSERT 或是改用 DEBUG BUILD 的版本，再讓 USER 去重現 BUG，這時如果你都有老老實實加上 ASSERT 的話，BINGO，問題在那就一目了然。看看是那一道 ASSERT 指令被觸發，就知道是什麼問題了。抓 BUG 最麻煩的就是找出錯在那裡，而善用 ASSERT 就可以讓 BUG 自己跳出來告訴你出了什麼問題，只要你養成好習慣。


再舉一個應用例。看到 Steve Maguire 先生舉這個例子，真是想拍手叫好。他舉了他們在開發 EXCEL 時的例子。EXCEL就是要替試算表作一堆運算，當年還在 DOS 時代，CPU怎樣都不夠快，RAM怎樣都不夠多，程式設計師無不絞盡腦汁，要榨出所有的運算能力，最佳化做到無所不用其極的地步。不過這種東西是錯不得的啊，少算了一塊錢還得了? 碰到這種問題你該怎麼辦?

通常，我們都會先有個安全的版本，算的不快，但是因為邏輯簡單，比較不容易出錯。這種版本寫出來後才開始想盡辦法，去改善程式讓速度加快。馬先生 (ㄜ... 是馬奎爾先生... ) 就充份應用了 ASSERT，隨時都要把 BUG 逼出來的精神，真的把 "驗算" 的方法應用上來。它的作法很簡單，同一張試算表，用兩份不同的程式碼各計算一次，最後再來比對一下結果 (驗算)。只要兩者得到的答案不一樣，那就是出問題了! 當然也有可能是安全的版本寫錯了，不過你至少多了個機會抓到問題，因為不一樣的話，一定 "至少" 有一邊是錯的!


沒有這樣的前題的話，各位看到可能都會在心裡想:

> 有沒有搞錯，程式都寫不完了，還要寫兩種演算法來驗算?? 老闆又不會多給我一點薪水...

沒錯，這的確是成本較高的方法，每套系統應該都有關鑑的地方，只要有絕對不能失誤的地方，就值得用這種作法。速度的問題怎麼辦? 很簡單。你只要在 DEBUG MODE 才啟用這 "驗算" 的機制，測試人員輸入各種數值做黑箱測試，如果每次測試的過程中發現驗算錯誤，則 "黑箱" 測試就能幫助你抓到只有 "白箱" 測試才有可能抓到的 BUG !


我寫的這個範例程式 (算成績) 其實也準備了兩個版本。上一篇貼的是基本的作法，結果比較可靠。而為了效率我也寫了另一份程式碼，用的是位元運算，希望藉著位元運算，一次就把多選題的答案給算出來。開發的過程中就用了 ASSERT + 驗算的技巧，它不會加快我寫程式的速度，但是它可以加速我找到 BUG 跟解決 BUG 的時間!

有沒有覺的這跟單元測試其實很像? 沒錯。單元測試就是一樣的觀念演變出來的作法，所以你用的單元測試 FRAMEWORK 也延用一樣的 ASSERT 使用慣例。你會發現其實之間的觀念都是相通的，只不過單元測試更進一步的把它系統化了，由原本四處藏在程式碼中的 ASSERT，抽出來成為一個一個獨立的 TEST CASE，由原本被動的執行時期檢查，演變為主動執行所有測試的 UNIT TEST。我覺的 Kent 在 XP (extreme programming) 裡舉了一個例子來說明單元測試，比喻的很貼切，我覺的也一樣能拿來比喻 ASSERT:

> 車子裝了煞車，是要讓車子能開的更快!

聽起來好像很蠢? 煞車明明是讓車子停下來的... 其實不然。想像一下如果你的車子沒煞車，你敢開多快? 了不起就是撞到不會怎麼樣的速度，或是油門放開就停下來的程度而以。有了煞車讓你有信心，碰到危險時你隨時能把車子停下來，你才敢把車子開上高速公路...

很有道理的比喻，ASSERT 跟 UNIT TEST 大部份人都覺的是 "煞車"，是拖慢你速度用的，但是也因為有這些 "煞車"，你才能放心的衝更快。當你有充份運用 ASSERT 的話，你就能很放心的寫程式，沒有後顧之憂。其實類似的關念，Steve Maguire 的書還有提到很多，只不過它的範例都是用 C 寫的 (還不是 C++ ...)，看起來會吃力一點。範例程式可能對現今大部份的人都用不到，但是裡面的觀念跟作法還是很有參考價值的，手上還有這本書的人不妨拿起來翻一翻。

講到這裡，花了兩篇才講完第一個部份，主要的重點就是用 TRACE / ASSERT 來說明，要讓你的程式夠穩定，第一個要改進的就是你寫程式的想法，觀念及態度。各位不妨以這兩篇的例子，自己回想看看，你做到那幾項:

1. 你寫程式有考慮到這些問題嗎?
1. 如果你寫程式有用這些方法，有多少你曾解過的棘手 BUG 會變的迎刃而解的?
1. 加上 ASSERT 之後，你是否對你程式更有信心了?
1. 你是否更認同單元測試的必要了?

想法跟觀念有了改變，才有可能開發出優良的軟體。你開始認同這樣的想法了嗎? 恭喜你，你已經跨出第一步了。不過光是 BUG FREE 還不足以成為優秀的軟體工程師，這只是必要條件之一而以。除了把程式寫的 "可靠" 之外，接下來的挑戰是如何把程式寫的 "漂亮" ? 下回要開始來探討如何構思你程式碼的結構。什麼樣的結構，什麼樣的方式去分析你的問題，才寫的出架構漂亮的程式? 別急，請期待續篇 :D


--

註: 範例程式很多 CODE 被我跳過去了，有興趣的人可以抓回去研究看看... 請點 [這裡](/wp-content/be-files/GoodProgram4.zip) 下載。