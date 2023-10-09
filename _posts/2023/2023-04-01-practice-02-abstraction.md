---
layout: post
title: "[架構師的修練] #3, 刻意練習 - 如何鍛鍊你的抽象化能力"
categories:
- "系列文章: 架構師的修練"
tags: ["系列文章", "架構師的修練", "架構師觀點", "刻意練習", "抽象化"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: 
---



有人問了我一些問題，無意間翻到了過去的兩篇文章，聯想到這幾個月的熱門話題 "AI"，有了一些想法，就有了這 PO 文...

其中一篇文章，是 2016 寫的，當時意外得到不少迴響，標題是: "[架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?"
https://columns.chicken-house.net/2016/05/05/archview-net-open-source/

另一篇是講抽象化設計的文章，標題是: 架構面試題 #4 - 抽象化設計；折扣規則的設計機制
https://columns.chicken-house.net/2020/03/10/interview-abstraction/


第一篇，當時的時空背景是 Microsoft 正全面的轉型, 從封閉 (一切都是 Windows) 到開放 (擁抱 open source, 擁抱 linux)。從 .NET Framework 到 .NET Core, 開始有官方的支持, 能在 Linux 上面執行 (甚至效率還比 Windows 強)，到 SQL server 都推出 Linux 版本, 之後不管再看到什麼都不奇怪了的年代 (包括 windows 內建 linux shell, windows 支援 windows container / linux container, 推出 mac 版本的 visual studio 等等)，這篇當時受到不少歡迎，就是我表達了當時 Microsoft 生態的開發人員，怎麼適應這麼大的改變..

現在會重新想到這篇，是這幾個月紅到翻掉的 AI，讓我又有了當年被翻了一輪的感受。ChatGPT 出來後，每個人手邊的工具都強上了好幾倍，這時你過去習慣的工作模式，還會是最有效率的工作模式嗎? 於是，我挑了一個我認為最能凸顯資深人員價值的題目，來測試一下 ChatGPT, 這就是我貼第二篇文章: 抽象化設計 的原因了。

"設計"，一直都是需要思考的課題，也是高度具備個人風格的課題。這類任務往往都是電腦不容易做的好的領域。不過先說結論，這次 ChatGPT 的表現，的確讓我驚艷，因為這種困難的設計題，在我面試不下百人，能正確回答的比例不到 10% 的題目，ChatGPT 竟然能回答的很到位..，這是我驚豔的部分。我就摘要一下我的問題 (prompt) 跟得到的答案，對於完整過程有興趣的請直接參考截圖。

其實我只問了兩次，其餘都只是請他 "繼續" 而已。我略過過程，摘要如下:

我問:

定義 C# interface, 能滿足下列要求:
1. 零售業折扣計算, 要能擴充未知的規則
2. 計算的結果, 要包含折扣的清單 (因為那些規則，產生那些折扣的明細)
3. 計算的結果, 要包含折扣的提示 (那些規則，還差哪些步驟就能滿足的明細)

ChatGPT 回:

public interface IRetailDiscountCalculator
{
    CalculationResult CalculateDiscount(decimal originalPrice);
}

public class CalculationResult
{
    public decimal FinalPrice { get; set; }
    public List<Discount> AppliedDiscounts { get; set; }
    public List<string> DiscountHints { get; set; }
}

public class Discount
{
    public string Name { get; set; }
    public decimal Amount { get; set; }
}

這個介面有一個方法 CalculateDiscount，它接收一個 decimal 參數 originalPrice，並返回一個 CalculationResult 對象，表示原始價格經過折扣計算後的結果。


我的感想: 震撼

整個前後文只有三句話，但是 ChatGPT 卻已經回給我我那篇文章解法的關鍵部分設計了。雖然整個 code 的設計不如我寫的精巧，但是關鍵設計結構已經出來了啊! Interface 只有一個 method, 精準的表達 input (原始價格, 我的版本是整台購物車, 這裡只是一個數字) 與 output (折扣計算的結果, 足以輸出收據明細的內容, 包含最終金額、折扣清單、以及提示清單)。

不過，機器應該也是有限制的吧? 他可能不能靈活地運用 (我天真的認為)，所以我繼續問了第二個問題..


我再問:

上述介面設計，給我能夠抽換兩組折扣規則的範例程式

ChatGPT 回:

以下是一個範例程式，使用 IRetailDiscountCalculator 介面和 SeniorDiscountCalculator 和 CouponDiscountCalculator 類計算一個商品的最終價格。在此範例中，我們使用兩種折扣計算規則來計算商品的最終價格，並展示如何使用 IRetailDiscountCalculator 介面來實現抽象，以方便替換不同的折扣計算規則。

using System;
using System.Collections.Generic;

public class Program
{
    public static void Main()
    {
        decimal originalPrice = 100;
        
        var seniorDiscount = new SeniorDiscountCalculator();
        var couponDiscount = new CouponDiscountCalculator("ABC123");

        List<IRetailDiscountCalculator> discountCalculators = new List<IRetailDiscountCalculator>();
        discountCalculators.Add(seniorDiscount);
        discountCalculators.Add(couponDiscount);

        decimal finalPrice = CalculateFinalPrice(originalPrice, discountCalculators);

        Console.WriteLine($"Final Price: {finalPrice}");
    }

    public static decimal CalculateFinalPrice(decimal originalPrice, List<IRetailDiscountCalculator> discountCalculators)
    {
        decimal finalPrice = originalPrice;

        foreach (var calculator in discountCalculators)
        {
            var result = calculator.CalculateDiscount(finalPrice);
            Console.WriteLine($"Discount Name: {result.DiscountName}, Amount: {result.DiscountAmount}, Final Price: {result.FinalPrice}");
            finalPrice = result.FinalPrice;
        }

        return finalPrice;
    }
}

public interface IRetailDiscountCalculator
{
    CalculationResult CalculateDiscount(decimal originalPrice);
}

public class CalculationResult
{
    public string DiscountName { get; set; }
    public decimal DiscountAmount { get; set; }
    public decimal FinalPrice { get; set; }
}

public class SeniorDiscountCalculator : IRetailDiscountCalculator
{
    public CalculationResult CalculateDiscount(decimal originalPrice)
    {
        decimal discountRate = 0.2M;
        decimal discountAmount = originalPrice * discountRate;
        decimal finalPrice = originalPrice - discountAmount;

        return new CalculationResult
        {
            DiscountName = "Senior Discount",
            DiscountAmount = discountAmount,
            FinalPrice = finalPrice
        };
    }
}

public class CouponDiscountCalculator : IRetailDiscountCalculator
{
    private string couponCode;

    public CouponDiscountCalculator(string couponCode)
    {
        this.couponCode = couponCode;
    }

    public CalculationResult CalculateDiscount(decimal originalPrice)
    {
        decimal discountRate = 0.1M;
        decimal discountAmount = originalPrice * discountRate;
        decimal finalPrice = originalPrice - discountAmount;

        return new CalculationResult
        {
            DiscountName = $"Coupon {couponCode} Discount",
            DiscountAmount = discountAmount,
            FinalPrice = finalPrice
        };
    }
}



我的感想: 震撼 again

同樣的，範例程式並沒有我寫得漂亮 & 精巧，但是同樣的，已經把主要的問題解決了啊，至少他充分的展示了怎麼正確的使用這 interface 來計算折扣 (抽象化後的主流程)，也充分展示了怎麼正確的擴充(實做) interface 來插入未知的規則。

這時，我不禁思考，設計能力跟應用能力，AI 都做的這麼到位了，人類該怎麼轉型，才能善用 AI，相輔相呈，創造更有價值的產出?
有的，終究 AI 不是真人，特質不同。找的到互補，能雙贏的組合，你就能在這時代繼續發揮優勢了。這時，我開始慶幸我過去的學習過程，都沒有放棄的基礎知識跟刻意的練習，讓我現在面對突然出現的強大武器，仍然有駕馭的能力..

在參與系統開發的過程中，其實我經歷過不少類似的情境，每當有困難的題目出現，我思考了好一陣子，想出類似這題目的解法之後，一開始我以為問題已經解決了，結果才發現這只是剛開始。你有了好的解決方案，接下來的挑戰是推廣，以及要面對更多真實的需求案例，要套用到你思考的 solution 上。在 AI 還沒有全面普及的情況下，我猜這現象還會維持好幾年.. 如果你的系統不是獨立運作，你已經能掌握 AI 了，另一端呼叫你 API 的系統可能還是人寫的.. 這時跨系統間的協調與設計，還是要靠人類的經驗，一來才能取捨，一來才能溝通調整。

要做到這些事，如果你沒有讓自己刻意的練習，沒有讓自己習慣抽象化思考，你是無法快速掌握 AI 給你的 soluition 的.. 你不需要跟 AI 拚你寫的 code 比他好啊，你要拚的是當他寫得比你好的時候，你要有能力辨識的出來，並且善加運用他的本事來替你創造價值。以這個折扣計算的案例來說，有了 AI 輔助，我可以更早就確認這 solution 是否可行，我就可以花更多時間，把實際商業上的需求對應到這個架構下來進行開發。

ChatGPT 在這個案例下，幫我解決了幾件事:

1. 從需求 (就那三句話)，幫我萃取了程式邏輯中主要的 interface
1. 從應用 (就第二段問題)，幫我 POC 驗證了可行性

而我要能掌握這些武器，我必須有足夠的抽象化思考能力，才能把現實世界的商業需求，對應到這 interface 上有效正確的運用他。這些能力需要練習，人腦的特性就是這樣，只有練習後的成果才是你能靈活運用的。而系統涵蓋面更大的話，也許要與你配合的其他系統，已經不是你能掌控的了 (對方可能是人，也可能是 AI)。這時善用正確的 interface, 開出 API, 並且一切的溝通與協作都從 API 規格為優先 (對，就是我前面寫了一堆的 API first)，你的影響力就能從你負責的系統，再度擴大到與你相依的生態系。

這幾天連假，有些時間研究怎麼運用 AI 的輔助，也想通了這些環節，突然間我很慶幸，我能活在 AI 邁入實用階段的奇點經歷這過程 (而不是害怕我是否會被 AI 取代)。





// PART 2

電輔車, 體力 / 控制能力 / 經驗
AI 變成強大的工具，有多少人能夠駕馭?
https://skoda-eddie.blogspot.com/2022/03/blog-post_25.html?fbclid=IwAR0_KBoMshllXvadX0l6GMVqqx3CG9vhCbuHIIaHPJgj0Ue_79841pkGeQU


好的設計不容易推動，有 AI (對我) 可以降低推動門檻，因為我已經能掌控他
AI 是無差別的輾壓知識工作者，他不在乎問題的難易，只要有資料訓練。每個人在自己專業領域都該做到比 AI 還能判定優劣的地步

體力 => SKILL, 交給 AI
控制能力 => 你主要的技巧, 交給人 (協作, 跨系統, 監控, 整合)
經驗 => 刻意練習

如果你的目的:
- 解決問題: 用 AI，工具越強越好，用輾的 (也不用管你裡不理解，眼前問題能突破就好)
- 長期發展: 累積 (善用AI) 的能力，須具備基礎 & 練習 (你必須理解才能辨別優劣，做出適合當下的決策；AI 不見得比你能掌握當下狀況，他只能靠你給他對的 PROMPT)






接續第二篇..

AI 似乎也沒再管你問的問題難不難，反正有資料餵給它就行。反倒是你問了難題，它真的答出來你也要看的懂才行... AI 就像傳說級的紫武普及化了，但是你也是要等級夠才能拿的動...。我延續上一篇的例子，繼續追問下去:

(前情提要: 我只問了兩次，短短三個要求，ChatGPT 就已經給了我折扣計算的抽象化界面 跟 同時支援兩種折扣活動的範例程式碼)

> 這 interface 一次只能計算一件商品的折扣，不符合我的需求
> 將 C# interface 規格修正為整個購物車內的商品都需納入計算，同時也重新給我 interface code 跟兩種折扣的範例程式

回答一樣略過，我附上對答的截圖，有興趣可以自己看。

經過第三輪的追問，C# interface 越修正越精準了，計算引擎的 input 從原本的 decimal originalPrice 直接換成 List<CartItem> cartItems, 越來越有購物車的樣子了。厲害的是附帶的文字說明，還清楚的跟我標註前後兩段 code 的差異...

我決定加大應用範圍，多加了優惠券的要求:

> 如果我的折扣計算，想要包含消費者手上有優惠券才適用的情境，C# interface 該如何修正?
> 給我修正後的程式碼 以及應用範例

還真的難不倒它, 又修正了一版 interface 給我。我只貼 C# interface, 一樣其餘看截圖:

public interface IDiscountCalculator
{
    decimal CalculateDiscountedPrice(List<Product> products, decimal totalPrice, List<Discount> discounts);
    decimal CalculateDiscountedPriceWithCoupon(List<Product> products, decimal totalPrice, List<Discount> discounts, Coupon coupon);
}

上一個例子還用 List<CartItem> cartItems, 這次就知道要換成 List<Product> products, 同時也附加了 Coupon coupon 當作參數 (看來一次結帳只限定使用一張優惠券)。

挑個小毛病。前一次的範例，ChatGPT 給我的計算結果是傳回折扣陣列，這次變成傳回結帳金額，而折扣結果清單，換成丟空的 List<Discount> discounts 當參數，執行結束後自行到 discounts 去拿結果。這是完全可以 work 的做法，不過對於介面有潔癖的我來說不大能接受，在語意上應該有更好的表達方式，來強調他是 "輸出" 而非 "輸入"。例如用 out 修飾字，或是用 Touple 回傳多個值都還比較好。

不過瑕不掩瑜，AI 幫我展開的結構設計，除了我挑的小毛病這些層級的風格問題之外，他提供的解法是非常到為精準的。


// 以下心得

我開始對 AI 改觀了，我覺得這是場不同維度的競賽啊，GPT 無差別的接受大量資料訓練，其實他骨子裡也沒有甚麼困難跟簡單的區別，你只要問了問題它就回答你這樣而已。問題在於:

1. 你有問對問題嗎?
1. 你能掌握他給你的答案嗎?
1. 你能看懂他的答案，並且判定狀況繼續追問修正結果嗎?

寫到這裡，我自己回頭再看一次我問的問題，我發現，其實我無形之間也在引導 AI 把架構修正到我心裡想像的模型啊 (就是那篇折扣計算抽象化的文章)。ChatGPT 其實是遇強則強的工具，就像上面我列的，你要問對問題，看得懂答案，他才會幫你。所以，AI 不會取代任何人，他也不會讓你一夜之間從不會寫 code 就變成高手。當然你無腦亂問，叫他產生程式碼來編譯，就可以跑出結果，這是沒問題的，不過你沒有基本素養的話，到這裡就停了吧! 你不知道他給的答案哪裡不好，或是那裡跟你期待的不同，你就難以精準地叫他修正。

以我的例子，我腦袋裡其實已經有想法了，就能夠很容易的引導 AI 把我要的東西生出來。AI 是個強力的武器，但是不會讓你升級，你可以當作 AI 是在你等級內能使用的最好的武器了，但是你終究得拿它去打怪，賺到經驗值才能升級。升級的過程是省不掉的，但是有強力的武器會讓你過程輕鬆很多。

你不會因為有 AI，就能讓你瞬間變成專家，你必須有足夠的能力 AI 才會是你的助力。學習、練習 & 思考的過程即使在 AI 的年代還是省不掉的。可以省掉的是，你會有專業的隨身教練協助你。這讓我想到當年念書時，剛開始學 C 的時候... 沒有好用的 IDE，因此你除了理解，你也必須背誦一些基本的語法或是函示庫 (intelligent sense 是好幾年後才有的東西啊啊啊)，後來到了 internet 年代，有了好用的 IDE，也有了強大的 search engine, 你省掉翻書找資料的過程了, 但是你仍然需要學習與練習的過程。

現在就像那個年代再來一次了，只是你開始連搜尋也不用了，也不用看我分享的文章了 (咦?)，練習的內容，ChatGPT 可以馬上產生給你，並且陪著你一路練習下去。

AI 發展到某個成熟度之後，他有多厲害，已經不是模型的限制了，而是你駕馭它的能力..。會取代你的不是 AI，是比你還能掌握 AI 的人。這句話最近聽過很多人在講，不過我親自完整跑過一次才親身體驗到這句話的內涵。

因此，接下來這篇文章，我打算拿三年前的演講內容，重新詮釋一次。之前我想傳達的是刻意練習，練習抽象化的思考過程。我用同樣的主題，搭配 AI 的輔助再來練習一次。



















// My Points View Of AI

// In Next 5Y
AI 是個 powerful 的工具, powerful 到你只需要用自然語言, 明確的告知你期待的結果敘述 (就是給正確的 prompt), AI 就能用很低的成本 (相較於人工費用, 另外是速度從幾天縮短為幾秒), 做出夠理想的成果。

不過, 目前為止, 這幾個月看到那麼多關於 AI 的討論 (我的 SNS 都被 AI 洗版了), 我覺得在未來五年內, AI 都會是個很強的 "工具" 或是 "助理" 的形態存在。過去學校的教育，都是以 "技能" (Skill) 為主，這是工業時代延續下來的體系。Skill 類型的能力，越來越會往 AI 靠攏了。對我最直接的衝擊，就是各種 coding 的輔助, 例如 github copilot, 或是你詢問 chatgpt 要他寫各種 code 都是..。現在可能還有人說，他寫的 code 你要有能力判斷他寫的對不對，不過我相信再過一段時間 (我覺得還要一兩年，但是 AI 進步的速度已經超過我想像了，也許只要幾個月)，AI 寫的 code 正確性高到某個程度，就不需要判斷正確性了。

這時，試著想想: 如果 AI 發展到這種地步，那軟體開發還有哪些是需要 "我" 來做的部分?

我的答案是: (廣義的說) 開規格。

你要有規格，你才能寫得出正確的 prompt 告訴 AI 你要他幫妳寫什麼 code .. 你要判斷正確性, 最快的方法是拿著 spec, 讓 AI 產生對應的 test case, 這時你要驗證的不是檢察 AI 寫的 code 對不對 (你 code review 的速度應該跟不上 AI 吧)，更有效率的做法是你直接看 AI 產生的測試案例。如果是你期待的，剩下就讓這兩組 code 互相驗證了。

(人)
=> spec =(AI)=> code
=> spec => use case =(AI)=> auto tests
=> 1 + 2, self validate ..

看到關鍵了嗎? 在 AI 還沒辦法讓你用一句話，產生整套完整系統的 source code 之前 (也許十年後真的能到這個程度)，需求設計到變成規格的這個過程，仍然需要仰賴人的經驗與判斷，才能產出正確的規格。規格定義好之後，由規格產出 code, 由規格產出測試, 由規格產出 blah blah ... 往下展開的每一個環節，我相信 AI 介入的比例會越來越高。因此如果你問我，未來要注重的能力是什麼? 我會回答: 你一定要知道 WHY... 黃金圈的 WHY HOW WHAT, WHAT 是最早被取代的 (search engine 就已經取代了你要 "背" 的功夫了)，AI 現在會取代的是 HOW 的能力 (就是我前面講的 Skill)，你必須讓你自己維持掌握 WHY 的能力

所以，在軟體開發，就是 "定規格"。套到前面我寫了一堆 API First 的主題，重點也是在 "定規格" (API 的規格就是 interface)。而定規格背後最重要的思考能力，就是 "抽象化"


扯了這麼九，終於回到主題了。我想通了這些關聯之後，我才有這念頭，想要把兩年前的這場演講，重新拿現在的業界環境來重新詮釋一次。在抽象化的領域，我撇除了大部分需要機械化動作的環節，換個角度來說，還是以 "人" 為主要的交互對象。




// More Then 5Y




// for FB:

這篇欠了 2 年了吧 XDD，原本是 2020/12 .NET Conf 演講的內容，預計 2021/07 貼的文章.. 現在因為某些因素，我決定回過頭來
重新整理這系列 "刻意練習" 的內容了。這篇是 "抽象化" 的練習，包含了 "生命遊戲" 的實做練習。這題目除了把它寫出來之外，裡面有好幾個
我覺得很重要，值得好好思考的點可以寫下來的

也許這篇文章拖了兩年是件好事，這三個月，我想大家的版面都被 AI, 或是 ChatGPT 這些關鍵字喜版了吧! 這幾個月 AI 帶給大家的衝擊有多大我就不說了，也不斷的有 AI 會取代那些人，或是那些工作會消失的說法也不斷冒出來。我趁版面聊一下我的想法:

不論 AI 再強，現在靠的都是大量的素材訓練模型。因此短時間內好的演算法的 AI 一定會快速成長到有人類菁英的水準 (從 0 ~ 70 分)，但是到這程度，網路上衣錠也會充斥著一堆你分不出示人寫的還是 AI 寫的內容... 開始會有 AI 自己產生的內容又被自己拿去訓練了。這時要嘛發展趨緩，要嘛發展出只有 AI 看得懂的文化... AI 可能已經改變成要抓住 AI 的眼球，而不是人類的眼球了

這篇: 人類不再練習時，該如何培養創造力? 我覺得很有道理。缺乏有創造力的內容為給 AI 訓練的話，AI 又怎麼會成長呢? 在 AI 自己還沒創造力之前................。這是我想重新把這系列文章拿出來整理的動機之一。我其實在工作上已經不大寫 code 了，尤其是 production 的 code, 但是我仍然要看 code, 仍然要 review 部分的 code, 特別是 framework / library 的 public interface, 或是 API spec. 因此, 我的工作仍然離不開 code, 只是不再量產 code 而已。

因為我的工作性質, AI 對我是大大的助力, 我完全不會擔心 AI code 寫得比我好我會不會沒工作? 過去, 我會擔心我的 interface 定義的太 "精巧"，工程師是否寫得出來? AI 輔助，可以讓這機率大幅提升，我可以更盡情的發揮我的設計能力。

// 說明 "精巧"，手錶、引擎 都是案例

那麼，設計能力該從哪裡來? 除了邊做邊學，藉著大量從事相關工作累積下來的經驗，在這年代，你會因為 AI 讓你少掉很多練習機會了，要維持競爭力，跟維持經驗的累積，你開始需要更有效、更刻意的練習才行。抽象化是個很好的分水嶺，抽象化以上，仍然是要有經驗的人來操刀的領域，因為你要設計的是整個系統如何運作，之中可能是要解決人的問題，可能是要解決部門間、公司間、產業間的問題，是商業模式，協作模式的問題，是需要人來進行決策的

而抽象化以下，則是大量的實做，這是過去花費最多人力的場域，也是 AI 輔助後最能提升的領域。提升是件好事，可以讓一個人的效率增加，不過也可能讓市場需要能駕馭 AI 的人，而不是單純的瑪儂。如果你只會重複地把規格寫成 code, 那未來能發揮的空間勢必會越來越小。

因為這樣的刺激，我開始體會到過去我不斷的在進行的 "刻意練習"，還有 "抽象化" 的思考，原來在 AI 時代又重新找到它存在的價值。還好兩年前我沒有補完這篇文章，現在看到了產業跟世界的變化，重新來看當年的演講，我有了另一番體會。

我常在跟同事聊，AI 盛行，我們除了去了解 AI 之外，我們也得開始思考，在 AI 為主流的趨勢下，你如何讓你的系統跟 AI 能有最大效益? 我的答案就兩個: 做好 AI 的 input, 就是乾淨的資料，良好的資料處理流程跟 pipeline 是關鍵之一；另一個就是 API, 當 AI 可以替你做各種決策, 你要 AI 怎麼 "自動化"? 這時 API 的成熟度是關鍵，你的系統如果能顧好 DATA 跟 API，那麼在未來 AI 的年代，你會獲得加成的威力，反之你只能眼巴巴看著別人充分發揮 AI 的威能...

// 通用技能，容易被通用 AI 取代

// 不鼓勵思考的教育模式，未來何去何從?

// 有機物的思考效率，仍遠高於無機體


(導讀: Microsoft 的布局, 從 AI, 到 Microsoft Graph API, 互動 | 應用 | 整合資料, 互動: chatgpt, 應用 office, 整合 graph api)

如果兩年前你也聽過我這場演講，或是你有幸被我推坑，也做過這些練習，歡迎你重新讀一次我的文章。我相信事隔兩年，同樣主題你會有不同的收穫的 :D







Hello!

![](/wp-content/images/2023-04-01-practice-02-abstraction/slides/page02.png)

這系列第三篇，回到 "刻意練習" 這個主題。這篇我回到軟體工程師最重要的技巧: coding 的基礎該如何自我鍛鍊，以及我自己如何讓我的團隊有計畫的練習這些能力。有別於第一篇，同樣提到 "刻意練習" 的主題；第一篇講的是打好基礎，當你基礎夠札實的時候，你才有能力把不同的技能彼此串聯靈活運用的重要性。第二篇講的就是靈活運用不同領域技能的案例。第三篇我想講的就是回歸到開發人員的基礎，也就是最重要的抽象化能力該如何鍛鍊起來的主題。

我一直都很強調，比起你對於開發工具、程式語言、或是開發框架有多熟悉，那些都是 "加速" 這個維度的技能。然而你面對問題心理怎麼思考解決方式，則是另一個維度的鍛鍊。這個維度牽涉到解法，我把他歸類在 "架構" 的這個維度。當你進入到資深，甚至專精的這程度時，往往限制住你發展的都是 "架構" 這面向的能力，這些能力沒有捷徑，只能靠平日不斷的練習才能累積的。這篇的主題我就是要說明我自己的經歷跟做法。

<!--more-->

這篇文章，就對應到我跟我的 team member ( Fion Yu ) 在去年年底 .NET Conf 2020 Taiwan 分享的主題: 刻意練習：如何鍛鍊你的抽象化能力。這主題我打算拆成兩篇文章來寫，一篇 (就是這篇) 我打算說明觀念跟做法，而在現場分享時因為時間有限，所以我在演講時提到的練習題: 生命遊戲 的實作細節，大部分都被我略過了。這些被略過的細節我打算在第四篇專門來探討。各位可以自己挑適合的主題來閱讀，如果你想找實做的題目自己練習，或是你想找題目讓你的 team member 親自參與練習跟討論，請期待第四篇文章。配合前面三篇的說明，我相信做起練習題會更有手感。

{% include series-2021-practices.md %}



# 主題: 如何鍛鍊抽象化思考能力



# 1. 為什麼抽象化很重要?



# 2. 我想的作法真的都能寫成 code 嗎?



# 3. 我們團隊過去做過哪些練習?



# 4. 現在就開始寫 code 吧!



# 5. 練習的收穫


# 6. 小結