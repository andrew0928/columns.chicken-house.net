---
date: 2023-04-08
datetime: 2023-04-08T00:05:08+08:00
timestamp_utc: 1680883508
title: "有人問了我一些問題，無意間翻到了過去的兩篇文章，聯想到這幾個月的熱門話題 AI，有了一些想法，就"
---

有人問了我一些問題，無意間翻到了過去的兩篇文章，聯想到這幾個月的熱門話題 "AI"，有了一些想法，就有了這 PO 這篇...

其中一篇文章，是 2016 寫的，當時意外得到不少迴響，標題是: 

[架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?
https://columns.chicken-house.net/2016/05/05/archview-net-open-source/

另一篇，是 2020 的文章，講抽象化設計，標題是: 

架構面試題 #4 - 抽象化設計；折扣規則的設計機制
https://columns.chicken-house.net/2020/03/10/interview-abstraction/

第一篇，當時的時空背景是 Microsoft 正全面的轉型, 從封閉 (一切都是 Windows) 到開放 (擁抱 open source, 擁抱 linux)。從 .NET Framework 到 .NET Core, 開始有官方的支持, 能在 Linux 上面執行 (甚至效率還比 Windows 強)，到 SQL server 都推出 Linux 版本, 之後不管再看到什麼都不奇怪了的年代 (包括 windows 內建 linux shell, windows 支援 windows container / linux container, 推出 mac 版本的 visual studio 等等)，這篇當時受到不少歡迎，就是我表達了當時 Microsoft 生態的開發人員，怎麼適應這麼大的改變..

現在會重新想到這篇，是這幾個月紅到翻掉的 AI，讓我又有了當年熟悉的業界被翻了一輪的感受。ChatGPT 出來後，每個人手邊的工具都強上了好幾倍，這時你過去習慣的工作模式，還會是最有效率的工作模式嗎? 於是，我挑了一個我認為最能凸顯資深人員價值的題目，來測試一下 ChatGPT, 這就是我貼第二篇文章: 抽象化設計 的原因了。

"設計"，一直都是需要思考的課題，也是高度具備個人風格的課題。這類任務往往都是電腦不容易做的好的領域。不過先說結論，這次 ChatGPT 的表現，的確讓我驚艷，因為這種困難的設計題，在我面試不下百人，能正確回答的比例不到 10% 的題目，ChatGPT 竟然能回答的很到位..，這是我驚豔的部分。我就摘要一下我的問題 (prompt) 跟得到的答案，對於完整過程有興趣的請直接參考截圖。

其實我只問了兩次，其餘都只是請他 "繼續" 而已。我略過過程，摘要如下:

我問:
----------------------------------------------------------
定義 C# interface, 能滿足下列要求:
1. 零售業折扣計算, 要能擴充未知的規則
2. 計算的結果, 要包含折扣的清單 (因為那些規則，產生那些折扣的明細)
3. 計算的結果, 要包含折扣的提示 (那些規則，還差哪些步驟就能滿足的明細)
----------------------------------------------------------

ChatGPT 回:
----------------------------------------------------------
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
----------------------------------------------------------

不過，機器應該也是有限制的吧? 他可能不能靈活地運用 (我天真的認為)，所以我繼續問了第二個問題..

我再問:
----------------------------------------------------------
上述介面設計，給我能夠抽換兩組折扣規則的範例程式
----------------------------------------------------------

ChatGPT 回:
----------------------------------------------------------
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
----------------------------------------------------------

我的感想: 震撼 again

同樣的，範例程式並沒有我寫得漂亮 & 精巧，但是同樣的，已經把主要的問題解決了啊，至少他充分的展示了怎麼正確的使用這 interface 來計算折扣 (抽象化後的主流程)，也充分展示了怎麼正確的擴充(實做) interface 來插入未知的規則。

這時，我不禁思考，設計能力跟應用能力，AI 都做的這麼到位了，人類該怎麼轉型，才能善用 AI，相輔相呈，創造更有價值的產出?
有的，終究 AI 不是真人，特質不同。找的到互補，能雙贏的組合，你就能在這時代繼續發揮優勢了。這時，我開始慶幸我過去的學習過程，都沒有放棄的基礎知識跟刻意的練習，讓我現在面對突然出現的強大武器，仍然有駕馭的能力..

在參與系統開發的過程中，其實我經歷過不少類似的情境，每當有困難的題目出現，我思考了好一陣子，想出類似這題目的解法之後，一開始我以為問題已經解決了，結果才發現這只是剛開始。你有了好的解決方案，接下來的挑戰是推廣，以及要面對更多真實的需求案例，要套用到你思考的 solution 上。在 AI 還沒有全面普及的情況下，我猜這現象還會維持好幾年.. 如果你的系統不是獨立運作，你已經能掌握 AI 了，另一端呼叫你 API 的系統可能還是人寫的.. 這時跨系統間的協調與設計，還是要靠人類的經驗，一來才能取捨，一來才能溝通調整。

要做到這些事，如果你沒有讓自己刻意的練習，沒有讓自己習慣抽象化思考，你是無法快速掌握 AI 給你的 soluition 的.. 你不需要跟 AI 拚你寫的 code 比他好啊，你要拚的是當他寫得比你好的時候，你要有能力辨識的出來，並且善加運用他的本事來替你創造價值。以這個折扣計算的案例來說，有了 AI 輔助，我可以更早就確認這 solution 是否可行，我就可以花更多時間，把實際商業上的需求對應到這個架構下來進行開發。

ChatGPT 在這個案例下，幫我解決了幾件事:

1. 從需求 (就那三句話)，幫我萃取了程式邏輯中主要的 interface
2. 從應用 (就第二段問題)，幫我 POC 驗證了可行性

而我要能掌握這些武器，我必須有足夠的抽象化思考能力，才能把現實世界的商業需求，對應到這 interface 上有效正確的運用他。這些能力需要練習，人腦的特性就是這樣，只有練習後的成果才是你能靈活運用的。而系統涵蓋面更大的話，也許要與你配合的其他系統，已經不是你能掌控的了 (對方可能是人，也可能是 AI)。這時善用正確的 interface, 開出 API, 並且一切的溝通與協作都從 API 規格為優先 (對，就是我前面寫了一堆的 API first)，你的影響力就能從你負責的系統，再度擴大到與你相依的生態系。

這幾天連假，有些時間研究怎麼運用 AI 的輔助，也想通了這些環節，突然間我很慶幸，我能活在 AI 邁入實用階段的奇點經歷這過程 (而不是害怕我是否會被 AI 取代)。

![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-002.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-003.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-004.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-005.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-006.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-007.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-08-001-008.png)
