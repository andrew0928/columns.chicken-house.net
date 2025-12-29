---
date: 2023-04-11
datetime: 2023-04-11T20:11:02+08:00
timestamp_utc: 1681215062
title: "AI 似乎也沒再管你問的問題難不難，反正有資料餵給它就行。反倒是你問了難題，它真的答出來你也要看的懂"
---

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

最後補個我先前那篇文章丟給大家練習的一個考題: 折扣互斥 (如果你中了一個折扣，就不能在繼續享用下一個折扣優惠..)

我問:

> 這些折扣規則我希望能互斥，如果符合其中一項，就應該忽略另一個折扣活動。
> 按照這需求重新給我 C# interface 定義

結果不意外 (前幾天還很震撼，現在已經不意外了 XDD)，ChatGPT 給了我很到位的設計，雖然跟我想的結構有出入，不過仔細看完他的方案，的確也是個可行的設計。礙於篇幅我就不繼續引導它修正出我要的答案了。有興趣看它的產出，請看截圖。

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

![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-002.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-003.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-004.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-005.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-006.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-007.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-008.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-009.png)
![](/images/facebook-posts/facebook-posts-attachment-2023-04-11-001-010.png)
