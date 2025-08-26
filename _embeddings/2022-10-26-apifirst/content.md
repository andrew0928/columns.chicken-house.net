![](/images/2022-10-26-apifirst/slide01.png)

這篇的內容，是我在 DevOpsDays Taipei 2022 的 Keynote 演講的主題: DevOps 潮流下的 API First 開發策略。這場次的內容，正好是我近期正在努力的方向，演講的時間有限，沒能 100% 表達我想講的內容，於是我還是用我最習慣的方式: 文章，重新來闡述一次這個主題吧。

API First, 講的是在你的開發流程內，API 應該被擺在第一順位思考的開發策略。一開始就瞄準 API 為主軸的開發方式，你會發現整個流程跟思考方式都不一樣了，這就是我這篇想要傳達的主軸。我在第一部分先花了點篇幅，說明 API 為什麼應該要 "First" 的理由。API 是很講究事前的規劃與設計啊，有時候會讓人有跟 DevOps 闡述 "先交付價值，尋求回饋持續改善" 的快速循環有所衝突的錯覺。這並非是你要做出二擇一的選擇，而是在持續改善的循環中，有沒有掌握好長期的目標的差別；而 API 的設計往往就是容易被忽略的一環。

因此我多準備了一段: 就是 "架構師在敏捷團隊中該扮演的角色"，這是我在演講當下沒時間聊到的段落，我在文章內也把他補上了! 同樣的內容，除了 DevOpsDays Taipei 2022 Keynote (2022/09/16) 之外，我事後也跟保哥進行了一場同主題的線上直播 (2022/10/07)，相關連結我擺在文章最後面。你可以選擇你想要的方式來了解，不過我個人是最推薦看我部落格文章啦 :D

<!--more-->

OK, 以下正文開始..

這篇文章我交代了 API First 的開發策略改變。在這個年代我已經不需要告訴大家 API 有多重要了，其實關鍵字應該是在 First，而非 API 身上啊! 我想傳達的是: 既然 API 很重要，你的流程就應該要先確定 API 到底該解決什麼問題 (最主要就是規格了) 再繼續往下走啊! 雖然業界都朝向敏捷的精神 "持續交付、持續改善" 的脈絡在走，但是 API 的規格必須一開始就定義好，無法頻繁大規模異動的東西，因此花時間跟精神把它 (規格) 弄對是絕對需要的。在我的想法裡，API 規格的 "結構" 影響了大家怎麼使用你的服務，而每個 API 參數規格則影響了細部參數傳遞 ( Request / Response )。結構是絕對最重要的，這也是後面我會帶到狀態機驅動規格設計的主要原因。

結構確認後，接下來才是展開在這結構下的 API 規格該長甚麼樣子。所謂的規格，就是指 API 的 I (interface, 我喜歡稱呼它是 contract 更貼近這個概念) 先定義好，然後才開始把你的 code 寫完。雖然這順序非常的 "waterfall", 但是他強迫你最優先去面對你真正要解決的 domain / business 問題, 然後再來補上實做的工作方法。

其實資訊科學的領域中，很多方法都是互通的，只是在這個年代，這方法的熱門關鍵字是 "API First" 而已 (就像前面的 微服務 vs 分散式系統 一樣)。從當年我還是學生時代就在學的 OOP，到現在的 TDD，背後的觀念都是要你先訂出介面，驗證後再補上實做的作法 (甚至多型或是動態連結，還允許你事後再追加不同的實做) 啊。很多規畫或是設計的彈性，你需要用對的工作方法才能完全發揮出它的威力。這篇文章我把主題擺在 API First, 我就是想要來聊聊我在這陣子推動這些工作方法背後的心得。


{% include series-2016-microservice.md %}


# 寫在前面

既然我都有先準備投影片了，那寫文章我就圖文穿插就好了，有些內容適合用投影片來說明，但是有些脈絡或是想法則適合用文字來交代。這也是我想要這主題都現場 / 職播分享過後，還想要用文字的方式寫成文章的原因。文字，才是我認為最有效率的分享模式啊，你可以自己控制閱讀的節奏與速率，要筆記或是應用，複製貼上等等，文字的效率還是遠遠高於影片的。更別說是全文檢索，搜尋等等應用了，雖然感覺老派，但是這也是我堅持要寫成文章的主要原因。

這篇文章我大致會分成幾個段落來聊聊 API First 這主題:

1. 你的團隊有多 "期待" 推行 API First ?
- 了解團隊現在的狀態
- 老闆期待的: API 經濟
- **延伸: 架構師在敏捷團隊該扮演的角色** (只有文章才有的內容)
- 改變團隊的文化與能力
1. ~~API 的治理策略~~ (演講有提到，文章我把這段刪除了)
1. API 的開發策略 ?
- 開發流程的改變
- 設計方式的改變
- 從設計階段就考慮安全性
- 思考是否過度設計
1. **案例 & 故事分享** (只有文章才有的內容)
1. 總結

其中，(2) 治理策略我覺得這題目太遠了，雖然我在 DevOpsDays 演講有提到，但是寫這篇文章時我決定拿掉這段.. 而 (4) 案例分享則是在當場沒有時間分享的，我決定在文章內容把他補上。其餘的重點都會擺在 開發策略 這部分。我期待 API First 既然重心都擺在 interface 的設計上，那麼應該很多對 API 的期待，就必須在設計階段被確認並且驗證完成的才對。因此這段我會帶到流程、設計、安全性、跟自我檢視是否過度設計的面向。在結尾 (5) 的部分我也想補充一下我在這些場合跟現場參加的朋友之間互動的紀錄，以及整理大家事後給我的 feedback，我覺得收穫很大，也藉這機會再次感謝各位給我的回饋。

最後，交代一下我做投影片的習慣... 我的簡報都走很簡潔的風格，就只有截圖、文字跟簡單的標示而已。我是個 developer 出身的人，文字的用法也看的到很多 coding 的影子，簡報的黑字是我要表達的主題，淺色的字樣 (前面會加上註解 // 的起始字串) 則代表我心裡的 OS 或是我的碎碎念..., 實際的簡報會用動畫控制，碎碎念會在後面才顯示，放在文章的版本就直接一次呈現了。

OK, 都準備好了, 那就開始進入主題吧! API First 的開發策略 !!



# 1, 你的團隊有多 "期待" 推行 API First


![](/images/2022-10-26-apifirst/slide05.png)

做任何事情前先講目的，這樣你才知道如何取捨，那些該堅持，那些可以放。我先從團隊對 API First 的 "期待"，來看看大家推行 API First 的目的是什麼。從字面上來看，API First 指的是在系統開發的過程中，API 應該被擺在第一順位來考量。與其講一堆落落長的定義，我先從幾個問題來測試看看你的答案為何，來判定你們的期待:

1. (從產品的角度)  
你們的服務是先設計 (product) UI, 還是先設計 (service) API ?
1. (從技術的角度)  
你們的系統是先求能運作 (product) 後再抽離 (重構) 出客戶需要的 API? 還是先訂好 API 的規格 (contract) 後同時開發 APP 跟 API ?
1. (從經營的角度)  
你們的 API 是其他產品的附帶功能 (一個產品線就有一組對應的 API, 產品的功能永遠領先 API)? 還是是當成產品來看待 (有 API 的商業模式，有發展策略)?


## 1.1, 了解團隊現在的狀態

這些問題，都有左右兩種選擇，當你的回答是左邊那組答案，就代表你的團隊越偏向產品導向；回答右邊的越偏向 API 導向。別太在意你是哪一派的，這不是對錯的選擇，這只是幫助你自己看清 API 在目前你的團隊重要性有多高而已。產品發展的成熟度，團隊能力成熟度，還有市場的競爭，跟發展策略其實都會影響你的決定。

清楚自己目前的狀態後，來看看標題講的 "期待" 吧! 如果你要認真推動 API First, 那麼就代表在這些角度來看, 你要做的選擇應該是這樣:

1. **從產品的角度**:  
你應該先做好 API (優先顧好 DX, Developer Experience), 再來做好 Product (UX, User Experience). 這意思不是說你應該照顧 DX 而放棄 UX, 意思是你應該優先把 DX 顧好, 這裡指的 developer 可能是你團隊裡的另一組人，要來用你的 API 開發 Product 的人。顧好它們的 DX，他們才有足夠的心力來做好 UX。這是執行次序的問題，不是選擇的問題。

2. **從技術的角度**:  
系統間應該明訂通訊的方式 (後面會提到，甚至要把它當作合約的層級來看待)，這通訊方式的約定，就是指系統提供的 API spec (也就是指 API 的 I, interface)。套入康威定律，你的系統發展結構會跟組織的結構相同，所以這同時也會是團隊之間溝通協作的介面。當你覺得 API 規格開的很糟糕，卻又無法 (可能是因為職責分工等因素考量) 優化改善，那就代表你們需要調整的可能是組織分工，而不是單純的 API 規格開的不好這類技術問題。  
這邊衍伸一個有趣的問題，留給各位思考 (有興趣討論可以在底下留言): 為何業界的趨勢是走向微服務架構? 而不是早期典型的三層式架構發展? 除了純技術的考量之外，還有其他原因嗎? (提示: 可以思考微服務跟三層式架構切割的維度，哪一種比較適合大規模的團隊分工運作)

3. **從團隊協作角度**:  
團隊各自發展的系統有多少種溝通管道? 除了 REST API 可能還有 share storage, share database, ETL, sync job ... 等等, 這些是好的方法嗎? 如果要聚焦在 API 的話，是 "提供" 服務的一方來定義 API 規格? 還是 "使用" 服務的一方來提出 API 需求規格? 為什麼? 不論規格怎麼來，雙方約定好之後會變成什麼形式定案執行? 口頭約定? 把原則寫成文件? 或是用技術規格 (例如 open api, 或是 gRPC IDL, 或是程式語言能直接處理的結構, 例如 C# interface, 或是 json schema 等等)? 你們會如何確保雙方都有確實遵守合約?

以上，其實都是我點出的 API first 推行可能要面對的選擇。這邊我跳離一下思考的脈絡，看一下別人怎麼講:

![](/images/2022-10-26-apifirst/slide09.png)

這篇文章: API-First Approach 中間提到這段，就是我 slide 標黃字的兩句話，是我覺得特別有代表性的部分:

> API-first means designing products around an API from the ground up, rather than building a product and adding an API later.

這段講的就是前面我問的，你是先開發你的應用程式 (products)? 還是先開發 API 然後再基於 API 來開發應用程式?

> Starting with an API contract allows you to better plan the design of your API and get feedback from stakeholders before writing any code.

這段則是呼應上面那段，如果你先做 API 再來做應用程式，你會有更好的機會來規畫你的開發流程。你可以在寫任何一行 code 前 (不論是 API 的 code, 還是應用程式的 code)，就能先拿 API contract (就是指 API 規格) 跟你的客戶代表 (stakeholders) 取得設計上的回饋。取得回饋的方式很多，我後面會舉例。這樣的好處是你在很早期的設計階段，就能取得回饋來修正設計跟你的整個發展計畫。這很符合敏捷的原則，但是帶來這好處的不是因為 API，而是 API 是你要解決的 business domain service 抽象化的系統通訊界面，這流程協助你更早期更精準的驗證你的 business domain service 而已。

切記這些好處，真正的來源是你確實的把你的 domain 轉化成 API, 並且把它擺在第一位來驗證設計可行性換來的。如果你沒把重點擺在 domain problem 的話，整個流程都會淪於形式，沒有辦法發揮實質的效用。

舉一個 anti-patterns, 如果你不去認真看待你的 API 是否正的能描述你要解決的商業領域問題, 而把關鍵擺在你的 API 設計是否符合命名、開發、安全規範等等實做細節，那注定會失敗的。你會得到一個完全通過所有規範的 API design, 但是解決不了任何商業需求的 API ...。正面面對 domain 問題並且用 API 來表達，同時在整個開發流程中集中所有的資源優先確認 API design 才是 API first 能成功並且帶來價值的核心想法，這點切記! 也因為這樣，後面我會花一半的篇幅來說明該怎麼從 domain 需求導引出 API 的設計方法。



## 1.2, 老闆期待的 API 經濟

![](/images/2022-10-26-apifirst/slide10.png)

我直接用投影片來說明這段吧。老闆的層級到某個位階以上時，他會在意的就是做這件事到底能替公司帶來什麼效益? 有短期有長期的，投入也有短期有長期的，老闆自然會依據這些資訊來判斷投入多少資源。這時，先來看看，就算你能 100% 完美的推行 API First 好了，在老闆眼裡這些事情的商業價值會是什麼?

我想第一個會聯想到的，就是 **標準化** 跟 **規模化** 帶來的影響力 & 經濟效益吧。

我廣義一點來描述 API, API 是系統間通訊的規格；每個系統提供的是處理特定領域問題的 "服務" 或是 "資訊"；而 API 則是取得這些東西的標準方式。每家公司都有他有價值的服務，只有透過 API 的方式對外公開才能標準化，這也是自動化的基礎，做到這些也才有規模化的空間。規模化到極致，就是生態系的結果了。

只有標準化，才能做到高度整合；所謂的整合，就是把你的服務，應用在別人的系統內 (可能是客戶自己的系統)，帶來更便利更精準的運作，也帶來效率與自動化的改善。若應用範圍從廠商 - 客戶間的系統整合，再次擴大到多個廠商 - 客戶間的整合，就是生態系的建立了。這個層次你可以進一步帶來新客群，生態系也會刺激更多的開發者去發掘不同的應用，你也有機會讓你的服務藉由這樣的過程發掘出新的應用空間，也會直接地帶來新的客戶。

這些都是經營者或決策者的思路，而 API 則是打通這條路的關鍵技術。軟體公司 (B2B) 的每個客戶都需要你的專業服務，不過客戶都是期待你的服務能融入它們的流程內，而不是他們換掉既有流程通通改用你的系統。這時，所有軟體開發團隊，都得面對 標準化(產品化) 與 客製化 的抉擇，能兼顧你才有能力服務規模比你大好幾倍的客戶。合理的作法是，用 API 抽象化收斂封裝你的服務，讓外圍的團隊能充分地應用重新組合，才會有這些綜效。就如同樂高積木一樣，你可以像疊積木一樣的創造你想組合的東西出來。但是換個角度想想，積木的製造門檻在哪裡? 我自己給小孩買過樂高積木，令我印象很深刻的是:

1. **製造品質**:  
樂高積木本身的製造品質非常好, 漂亮、耐用、尺寸精準
1. **設計品質**:  
樂高積木的規格設計擴充性非常好, 最令我意外的是小小孩玩的系列 (Duplo, 比較大顆) 跟中高齡小孩 (甚至大人) 玩的系列 (Classic, 常看到的就是這系列) 竟然是相容的.. (你可以把兩種系列的積木組合在一起玩)
1. **降低門檻**:  
樂高積木基於良好的品質跟設計, 創造了不少經典主題系列, 例如星際大戰、蝙蝠俠等等。在這些規格基礎之上，只要再生產一些特殊造型的積木，同時打包生產，製作這些主題系列的說明書，消費者買回去照說明書就能組合出千年鷹號...

這不就是軟體開發的理想嗎? 對應到軟體開發，(1) 就是你的開發能力，交付的程式碼可靠度穩定度執行效率等等品質類的要求都屬這種；而 (2) 則是你的設計能力，我一直在強調的 domain knowledge 設計規格類的要求就屬這種，(3) 則是你的工具鏈跟整合能力是否到位，如何最大化的發揮 (1) + (2) 的綜效。

所以我才舉了這些例子，我們自己也把零售業的系統服務能力，拿來應用在不同產業的案例 (餐飲業)。跨領域有很多細節是不同的，舉例來說: 零售業的線上銷售，是庫存，交易，運送等領域的組合問題；而餐飲業則有很大的不同，除了零售業的流程之外，庫存 (食材) 跟最後賣出去的商品 (餐點) 很可能是不一樣的東西啊，中間甚至包含了製作 (烹調) 過程的管理，也加入了更多消費者客製化餐點需求的選項 (例如: 不要香菜，要加辣等等)。這些差異都考驗了我們的系統，該如何進軍不同領域的挑戰，這些都考驗了我們如何把過去擅長的服務 (例如線上交易，高流量，高併發等等) 重新在新的產業重組的能力。

回想一下，這不就是上面樂高的情況嗎? 如果你只想拿標準的積木去應付特殊需求 (例如組出一台千年鷹號) 是很困難的，你應該在標準化積木的基礎上，適度的加上部分相容但是是特殊造型的零件才能完成。這不就是你自己用 API 來擴充你的系統嗎? 也因為這樣，我們內部很認真地看待 API First 這件事，也因為參與其中，才有我這次的 keynote speech. 掌握正確精準的 API, 你才能同時滿足每個客戶對你規模化與高度客製化的期待。


![](/images/2022-10-26-apifirst/slide11.png)

我再把題目帶回到產品開發團隊內部。在團隊從小變到大的過程中，一定是先從幾個人開始，把第一版產品做出來，接著逐步擴大，才有各種分工。過程中開始要面對 API 跟 APP 的分界是最困難的，直接就把 APP 開發出來就好了啊。然而 API 背後就是 "服務"，APP 背後就是 "應用"。怎麼拿捏 API / APP 該處理的範圍就很令人頭痛，API 過度往 APP 偏斜，不論是 UI 或是流程都會被 APP 的設計過度綁定；當你的 API 要應用在不同的領域時，你就會發現 API 派不上用場 (想想前面我講的 "餐飲電商" 案例)，這結果就背離你當初 API First 的目的了，不是嗎?

因此，拿捏分界，是很重要的。API 並不是開的越多越好，而是越少越好，你必須避免把過多的細節塞到 API 內。如果你想讓 API 更 "好用" 一點，其實還有很多其他手段，而不是過度把複雜度都加到 API 的設計內。例如我最常用的一招就是: 維持精簡的 API，但是複雜的組合應用我可以提供 SDK, code template, 或是 BFF 來降低前端 APP 開發的門檻，兼顧兩者的平衡。剩下的難題就是: 誰來決定這些邊界?

這就很因團隊而異了，即使我已經工作 2x 年，我仍然沒有清楚的答案，因團隊不同，每個團隊應該都有決策的核心人物，有的團隊是產品長扮演這角色、有的是技術長、技術總監、或是架構師等等都有可能。但是，不管是任何一個角色來負責，都會面對一種發展的趨勢，就是 M 型化的發展。

你的團隊開始需要專人負責 API 的設計開發，他必須越來越專精，設計開發的品質要求越來越高，人的技能跟經驗要求也越來越高，這是無可避免的，這組人會往 M 的一端發展。有了這些武器，你需要越來越多的團隊來打仗，開發更多應用，擴展更多的領域，甚至有內部團隊跟外部合作的協力廠商等等。擴大的必要條件就是降低門檻，最近很熱門的關鍵字 Low Code / No Code 就是應用在這種場合，因為門檻越來越低，這些角色會越來越偏向 M 行的另一端。這兩者的平衡，GIPI 的一篇 FB 貼文正好很洽當的闡述了模組化跟客製化的光譜。我先給連結，後面的段落我會再提到一次，到那邊在來聊聊這個題目。

GIPI: [模組化與客製化](https://www.facebook.com/gipi.net/posts/pfbid0E6PW6rXWC4HYb6LZKzb9YPiEMX46qQdJJ7jhqkzuaeNX2yVkp7ZEHbd9ryR5oQsnl)

> 模組化與客製化中間的思考與選擇對很多人來說一直都是一個難題。
> 
> 對工程師來說，多數時候我們會希望盡可能的模組化，但過度的模組化，超過了當前業務的需求時，那就會變成過度設計。開發資源反而沒有用在真正重要的任務上，沒有對齊公司當前的狀況，以及需要解決的問題。
> 
> 其實模組化與客製化是個光譜，完全模組化或完全客製化都不是長期經營應該思考的方向。
> ...

![](/images/2022-10-26-apifirst/2022-11-17-02-36-45.png)





從產品發展的角度來看，這裡列的這幾點，不就也是前面提到 API / APP 的取捨嗎?


講到這裡，我再把角度拉回產品開發團隊身上。如果真的要轉向 API First (我假設前面的 WHY & HOW 都想清楚了)，那麼工程團隊有那些問題需要克服，有哪些思考方式需要改變?

我自己認為最重要的，還是康威定律。API First 代表一切都是從 API 開始，包含提供 API 的角色，也包含使用 API 的角色。其中更包含管理 / 治理 API 的中心單位的角色。在這所有事情內，我把硬題目 (開發) 跟軟題目 (設計) 往後擺一點，後面的段落在說明，我先聊聊康威定律。既然系統跟組織是對應的，那就代表系統間的溝通約定 (API) 也會是團隊間的溝通約定，因此內部團隊需要先具備用 API 溝通協作的能力。

我就舉最具代表性的案例好了: AWS (Amazon Web Service) 的前 CEO 貝佐斯, 他也是帶領 AWS 走到今天這步的最大功臣。他在 2002 年的時候 ( Orz, 20 年前就有這遠見 )，在內部發布了一份備忘錄。內容主要是工程團隊所有服務都應該以對外開放的標準提供 API，跨團隊間 API 是唯一的溝通管道，沒有例外。我把他的備忘錄內容列在這頁投影片:

![](/images/2022-10-26-apifirst/slide14.png)

看到了嗎? 早在 20 年前，貝佐斯就有這樣的看法。他不限定 API 的技術規範 ( HTTP, CORBA 皆可... 有人還知道 CORBA 是啥東西嗎? 我當年研究所念過 XDD, CORBA: Common Object Request Broker Architecture ... )，但是你一定得用通訊的方式來協作，不能直接共享資料庫等等這種暴力的手段來跨團隊通訊。這也間接強迫了 AWS 要及早面對分散式架構的挑戰，你也可以理解成 20 年前它們就在面對微服務架構的各種問題了，也因此 AWS 內部能發展出各式各樣成熟的 PaaS, 可以協助大型系統的通訊與協作，我想跟他們很早就需要面對這樣的挑戰脫離不了關係吧。

![](/images/2022-10-26-apifirst/slide16.png)

從這份備忘錄，表面上我看到了貝佐斯訂了很嚴格的要求，要所有開發團隊遵守，避免不好的通訊方式 (例如: 共用資料庫) 造成技術債。

但是長遠背後的涵義，我看到了幾點，我想這才是他真正的目的:

公司的價值一定是在特定領域能提供的服務或是資訊，既然 API 是取得這些服務最合適的方式，那就該被保障 (所以才會要求所有團隊都要遵守 API first)。API 串聯起內外部種種的服務，這才是商業運作的骨幹。UI 只是這些背後運作的服務，需要墊上一層人能操作的介面 (UI) 而已，主體應該是背後一群靠 API 協作的龐大系統。由於這些實在太重要了 (尤其是對於 AWS 的未來而言，當時)，因此貝佐斯才會附加最後一條強硬的規定: 沒有討價還價的餘地，不遵守規定的人一律開除。





## 1.3, 架構師在敏捷團隊該扮演的角色


回到前面我提到哪個角色該拿捏 API 跟 APP 的分界，我又找了篇老外的文章 XDD, 這篇我找的主題是: 架構師在 Agile Team 裡該扮演的角色... ( Ref: Role of Architect in Agile Development), 裡面提到:

![](/images/2022-10-26-apifirst/slide12.png)

(我只列出我 highlight 的四句話，其他各位有興趣請直接看原文)

Challenges in Agile Development

1. Visibility, no end to end visibility on long term client road map (tech & domain)
1. Multiple teams working on different features and different parts of the code base
1. ..... the approach is to prioritize all the "visible" requirements first .....
1. Technical debt, technical considerations are getting lower priority in product backlogs compared to business features.

我自己的解讀是: 不論是 agile, 或是 devops, 講求的都是藉由快速地交付跟回饋, 快速的修正, 不斷的貼近客戶需求的過程。在這過程中，很容易就忽略掉長期的目標。架構師在 agile team 就是扮演讓團隊顧好長期目標這樣的角色, 看看上面列的要點: 要看到 client long term road map (tech, domain), 要跨越多個團隊 (涵蓋不同 code base, 可能是 repo, 可能是 product line), 要能平衡看的到的與看不到的需求, 要能平衡技術(債)與商業需求... 都屬於這類。

其實這也是我想要帶出來的主軸: 沒有好好的抓住長期目標 (尤其是非功能性的需求，例如技術債，架構設計，或是 API 設計等等這類議題) 的話，很容易在短期快速的循環下就被忽略掉了。時間管理的方法也常常提到類似的情境: 重要但是不緊急的事情，往往很容易被忽略掉；因為不緊急，就不會排在這個 SPRINT 進行，因為每個 SPRINT 永遠都有更緊急的需求要處理啊! 久而久之真正重要的需求就被 "無限期" 的擱置了。這是人的通病，解決方式是如果你認定是真正重要的需求，即使他不緊急，你都應該保留固定資源去推動他。有的團隊是保留 20% 的人力，有的團隊是固定 3 SPRINT 後休耕 1 個 SPRINT 來處理這類需求，都是不錯的做法。

這凸顯了識別這類需求的角色的重要性。典型的 SCRUM team ( stakeholder, scrum master, product owner, team member ) 大都是把這職責分攤到 stakeholder / product owner 身上了。不過當系統規模大的時候，或是有跨越多個團隊之間的系統需求需要統一對齊的時候，光靠這兩種角色應該應付不來的，一般都是由架構師來擔任這角色。這樣的矛盾我也面對過，看了不少文章，建議大致都相同。我挑一篇我認為講的最到位的:

* [Where does an Architect fit in a Scrum Team?](https://premieragile.com/where-does-an-architect-fit-in-scrum/)

我節錄其中一段:

>
> What is an Agile Architect?
> 
> An Agile Architect is responsible for defining and maintaining the structure of the solution by making sure that the product and the Product Increments meet the requirements. The Agile Architect helps the team to work together in Agile fashions such that they jointly own the solution and interface well with other parts of the organization. The responsibilities of an Agile Architect include:
> 
> * Understanding the requirements: 
> Agile Architects have to identify the Stakeholders, help them to analyze the requirements for the Product Increment, and extract those requirements concerning the Architectural significance.
> 
> * Design Formulation: 
> Creating a structure of solutions that can meet all the various requirements, balance goals, and constraints on the solution.
> 
> * Communication of Architecture:
> Have to make sure that everyone is on the same page and understands the Architecture. As several people may have different viewpoints, the Agile Architect has to present various views of the system to different audiences. 
> 
> * Support the Developers: 
> The Agile Architects should ensure that the Developers can realize the Architecture which could be done by a combination of mentoring and direct involvement. 
> 
> Verification of the implementation: Agile Architects make sure that the delivered system is consistent with the Architecture that was agreed initially and meets all the requirements as discussed.
>

換我自己的看法來解讀這段:

Agile Architect (以下簡稱架構師) 架構師負責系統的結構，要同時確保每次產品的改善都能符合需求，也要確保這些 solution 在組織內的各個單位 (或是系統?) 能夠順利的協同運作。為了達到這個成果，架構師需要負責這幾件事: 了解需求、設計公式 (後面說明)、溝通架構、支持開發人員。

除了字面上的意義之外，也有延伸的涵義。其中有一項 "design formulation" (設計公式) 大部分的人可能會覺得一頭霧水，不過這我倒是感受很強烈。架構師最能發揮價值的地方 (對比於 product owner / tech leader 這類執行者的角色) 在於看到需求背後的脈絡，並且正確的進行抽象化。想像一下，對於一套系統的特定功能，若 stakeholder 有十幾個不同的需求，典型的做法是 PO 列出了相對應的 stories, 團隊逐步拆解為 tasks, 按照節奏逐步完成。若能看出背後的脈絡，做法也許就會不同，你會先設計出能支援背後脈絡的核心機制，然後再這之上搭建能滿足這些需求的 "客製化" (相對於核心機制而言的客製化) 功能。

兩者之間的差別在於，核心機制若設計得當，應該都不會需要大幅修改，規則也應該都夠簡單明確。但是核心機制不是直接客戶能使用的東西，需要靠其他 developer 包裝後給客戶使用。有了核心機制，developer 就能快速的修正 "包裝" 部分的程式碼，調整出客戶需要的流程或是功能。比起從一開始就按照規格開發，你多了能累積的基礎 (核心機制)，也降低了每一個功能開發的成本 (邊際效益)。通用性的優化 (例如正確性，可靠度，效率，安全性等等)，也能直接受益。核心機制因為介面較收斂，通常都更容易測試，優化的過程中也更可靠不容易出錯。

翻譯成白話，這就是所謂的 "產品或服務" 背後支撐的 API。實現這些 API 的就是所謂的核心機制。架構師如果面對這些需求的組合，能識別出背後應該要有的核心機制，同時對所有的團隊與相關人員 (例如 PO) 都用同樣的架構來溝通，讓大家都在這個基礎上發展，同時也協助每個開發團隊正確的使用他 (甚至規畫各種降低使用門檻的工具，SDK，套件，開發框架等等) 對我的解讀而言，就是做到了 "了解需求、設計~~公式~~核心機制、溝通架構、支持開發人員" 的目的。

這整個過程，最重要的能力就是 "抽象化" 了。我舉一篇我自己在說明抽象化很有代表性的文章: [抽象化設計；折扣規則的設計機制](/2020/03/10/interview-abstraction/) 來當案例:

![](/images/2022-10-26-apifirst/2022-11-06-17-00-23.png)


在面對 stakeholder 需要多樣且複雜的折扣需求時，我做了幾件事情來降低整件事情的難度，其中最關鍵的環節，就是上面提到的 "設計公式"。

我設計了什麼 "公式"? 我定義了所有折扣 "計算" 的規則，一律是把要買的東西都裝進購物車內 (包含商品，會員卡，以及你這次要使用的折價券等資訊)，交給計算引擎來計算。由於計算方式千百種，我只規範了計算規則的 input / output，而不去規定計算規則該怎麼設計。所有的功能只要想辦法收集購物車的資訊 (input)，同時有能力處理計算引擎的結果 (output)，就能實做出整套系統了。同時能滿足多種期待: 折扣規則可以不斷擴充，購物車等 UI 介面不需要跟著不斷修改，核心機制長期可以穩定可靠的發展 (不會因為需求一直需要變異)。


最後定義出來的 interface, 可以直接參考文章的範例: [模擬實際的訂單計算](/2020/03/10/interview-abstraction/#%E6%A1%88%E4%BE%8B%E5%AF%A6%E4%BD%9C-%E6%A8%A1%E6%93%AC%E5%AF%A6%E9%9A%9B%E7%9A%84%E8%A8%82%E5%96%AE%E8%A8%88%E7%AE%97)



定義 ```Product```, 定義 ```RuleBase```, 設計這些基礎之上的 ```CheckoutProcess()```, 讓整個架構能順利運作；同時用這樣的架構來跟開發人員溝通，給予需要的支持，就能打造完整的運作體系。

在這體系之下，勢必有許多任務需要進行，這裡才會下放到各個團隊，按照資源跟需求的重要性重新調整每個 SPRINT 的目標，有計畫地交付，並且持續接收回饋修正接下來的交付。用這個案例，是否更清楚的理解架構師在團隊內扮演的角色了嗎? 想想看這個過程，跟這篇的主軸 "API First" 的關聯是什麼... 因為架構師的參與，找出了 "公式"，定義出來的核心機制，就會有系統實做時要參照的介面 (interface), 這介面就是所謂的 API spec ..

好的 API spec, 會被期待是能長期穩定運作的。這裡指的 "穩定" 是指介面的穩定，不應該隨著時間或需求的異動而大幅變更。因為 API 規格的變更是會影響所有跟他通訊的系統的，如果有避免不掉的變更，你就必須做到像前相容。這改變的成本是很高的 (尤其是用你的 API 的人越多越是如此)，因此你找出來的 "公式" 是否真正代表該領域的核心機制，影響就很大了。甚至我會說，這才是決定 API First 能否成功的唯一關鍵。其他的因素，技術或是實做的技巧都是讓你少犯明顯的錯誤，讓你少扣分而已。

剛才那篇文章 (講架構師在敏捷團隊扮演角色的那篇)，後面還有一段，就接著往下看吧! 我依樣節錄片段:


> 
> Here are a few factors to consider while choosing the place for an Architect in the Scrum Team:
> 
> * Product Owners who also perform the roles of an Architect are best suited for products which are technical or Architectural. Products in these cases are designed keeping the priorities in mind from the Architect's perspective.
> 
> * Architects who are advisers outside the Scrum Team or a Quality Assurance reviewer or Stakeholders are usually selected whenever the Scrum Team does not have an Architectural skilled member in the team. Also such Architects may be appointed whenever the team needs an enterprise influence in their activities. 
> 
> * Agile approach requires the Architect to develop an Agile culture in the organization that supports all the members of the organization to deliver > high business value. This has to be the main priority whenever an Architect is placed in the Scrum Team. 
> 

前面是描述架構師該負責的任務，這段則是進一步說明架構師應該如何安排進團隊? 中間有一大段說明，描述了該讓架構師擔任 PO, 或是 stakeholder, 或是 scrum master / QA 甚至是 developer 等等的安排。這其中有很多跟你產品類型，或是團隊狀況的情境需要取捨。有興趣直接看原文，我直接跳到後面的小結:

1. 如果你的產品，本身就是有著很強的技術或架構要求時，這團隊的 PO (Product Owner) 適合由架構師來兼任。這種類型的產品在設計時，會從架構的角度優先思考，最適合這樣安排 (切記: 前提是 PO 擁有必要的架構師技能，同時產品的屬性也需要這樣安排。千萬別硬是把相關任務強押在 PO 的身上)。
1. 如果你的團隊，缺乏擁有架構能力的成員時 (你可以拿上述的折扣計算案例，試想在你的團隊是否有人能用這樣的方式思考來判定)，通常會選擇團隊以外的人來擔任架構師的角色；或是把相關的角色擺在團隊外圈，例如 QA (quality assurance) reviewer, 或是直接扮演關係者 (stakeholder)。
1. 架構師在敏捷團隊內，其實是要引導大家發展出敏捷文化的角色，支持組織 (多個團隊) 所有成員交付高業務價值的人。不論架構師用何種角色進入團隊，都應該要把發展敏捷文化當作主要優先事項。

以上是我對於架構師在團隊內的角色扮演的補充。我覺得這段的思維，其實貫穿了這整篇的主題。API First 就是要用良好的 API 設計，來貫穿整個開發部署跟維運的流程啊! 核心關鍵是這個 API 的設計該從何而來，這對我而言就是架構設計的議題，不是開發或是工具選擇的議題。在演講的當下這段完全被我省略了，還好我還有機會藉著寫文章把這段想法交代清楚。

其他值得一讀的類似主題參考文章，我也一起列在下方:

* [Where does an Architect fit in a Scrum Team?](https://premieragile.com/where-does-an-architect-fit-in-scrum/)
* [Architects & Scrum: 4. What is the role of the architect in Scrum?](https://xebia.com/blog/architects-scrum-4-what-is-the-role-of-the-architect-in-scrum/)
* [Do we need a software architect in our agile team?](https://www.workingsoftware.dev/do-we-need-a-software-architect-in-our-agile-team/)
* [SOFTWARE ARCHITECTURE IN THE AGILE WORLD](https://www.planetgeek.ch/2019/10/18/software-architecture-in-the-agile-world-part-7-changing-requirements-and-technologies/) – PART 7: CHANGING REQUIREMENTS AND TECHNOLOGIES



## 1.4, 改變團隊的文化與能力

寫到這邊，我想對於 API First 的 "期待"，跟背後的想法，應該都交代的差不多了。在進到下一個主題前的最後一段，我想提一下這些思維跟流程的改變，文化跟能力的準備是很重要的啊! 所有改變都是困難的，因為你必須面對團隊過去習慣的做法跟想法。沒有足夠的準備跟動機，這些傳統是會持續維持下去的。講了這麼多的 API First 期待，我想這些都是 "動機" 的部分，而能力的準備，只能靠有系統的吸收他人的經驗了，最好的方式是讀書會，有系統的透過研讀其他成功的案例來獲取經驗跟能力。

![](/images/2022-10-26-apifirst/slide18.png)

我們自己的做法就是資深人員 (具備一定影響力的成員) 參加固定舉行的讀書會來提升這些經驗跟能力，在老師的帶領下我們也會花時間討論，書上講的案例跟方法怎麼應用在我們實際的狀況。我就介紹一下我們讀過 (包含正在讀) 的三本書:

**Continuous API Management (持續 API 治理)**:

[這本書](https://www.tenlong.com.tw/products/9789865021078), [第二版](https://www.tenlong.com.tw/products/9786263243224?list_name=trs-o) 講的是你如果有大規模的 API 需要發布，維護與管理的話，那你需要的是 API 的 "治理" 方法，而不是只有單純的設計跟開發而已。一組 API 可能只是個專案或是產品，但是所有產品線的 API 集合要好好的管理他，可能就不是那麼簡單的事情了。書上把這堆 API 稱為 API 叢林。這本書提到的 API 生命週期五個階段，把 API 開發出來能正常運作，那只是剛開始而已 (大部分的工程師會認為這樣就結束了 XDD)。書上講了不同階段的執行策略，也提到了你怎麼有系統的更版，讓 API 的生命週期得以不斷地延續下去的手段。書上也提到了推動 API 叢林的發展，業務跟技術團隊各需要那些角色，各需要負責那些任務。有心大規模經營 API 的團隊值得好好讀一下這本書。

天瓏書店有放上[這本書](https://www.tenlong.com.tw/products/9786263243224?list_name=trs-o) 的目錄，貼給各位參考:

```
第一章 管理 API 的挑戰與承諾
第二章 API 治理
第三章 API 即產品
第四章 API 產品的十大支柱
第五章 持續改善 API
第六章 API 風格
第七章 API 產品週期
第八章 API 團隊
第九章 API 園林
第十章 API 園林之旅
第十一章 在持續演變的園林中管理 API 週期
第十二章 繼續這趟旅程
```

**API Design Patterns**:

[這本書](https://www.tenlong.com.tw/products/9781617295850) 講的是 API 常見的設計模式，作者 JJ Geewax 是 Google 的工程師，負責 GCP 跟 API design 的任務，Google 開放的 API 在設計上跟實做上都有一定的水準，作者的背景來講這個主題再適合不過了。這本書比較偏向實做跟規格設計面的探討。我們讀的順序是先讀 Continuous API Management 再讀這本 API Design Patterns 的；不過事後回來看，兩本書的順序反過來比較合適。

在 amazon.com 上的[介紹](https://www.amazon.com/API-Design-Patterns-JJ-Geewax/dp/161729585X)有這本書的目錄，我把他列在底下，各位比較能想像這本書能解決你哪些類型的 API 介面設計困擾:

```
Table of Contents

PART 1: INTRODUCTION
1. Introduction to APIs
2. Introduction to API design patterns

PART 2: DESIGN PRINCIPLES
3. Naming
4. Resource scope and hierarchy
5. Data types and defaults

PART 3: FUNDAMENTALS
6. Resource identification
7. Standard methods
8. Partial updates and retrievals
9. Custom methods
10. Long-running operations
11. Rerunnable jobs

PART 4: RESOURCE RELATIONSHIPS
12. Singleton sub-resources
13. Cross references
14. Association resources
15. Add and remove custom methods
16. Polymorphism

PART 5: COLLECTIVE OPERATIONS
17. Copy and move
18. Batch operations
19. Criteria-based deletion
20. Anonymous writes
21. Pagination
22. Filtering
23. Importing and exporting

PART 6: SAFETY AND SECURITY
24. Versioning and compatibility
25. Soft deletion
26. Request deduplication
27. Request validation
28. Resource revisions
29. Request retrial
30. Request authentication
```

這本書強調的都是 API 的介面該怎麼設計，那些情況下適用的設計模式，書上總共列舉了卅種 patterns (參考上面的目錄). 如果我狹義一點的定義 API 就是 REST HTTP API 的話，那的確有很多情況下不適合直接一個要求就對應一個 API 的，例如匯出大量資料 (ex: 百萬筆)，你就必須有分頁 (Pagination) 的設計，也延伸了你如何取得下一頁的做法，也探討了更進階的實做議題，例如你有多少時限能取得分頁內容? 你一分鐘後才拿後面的分頁，你該拿到一分鐘前的內容，還是即時的內容? 你在分頁查詢的過程中也許來源資料也已經異動了等等，這類問題都是你的服務，API 化之後必須面對的問題 (本來只是你在 code 內使用，或是直接在 database 操作根本不用擔心的狀況)。書上有系統的告訴你在設計 API 碰到這種狀況發生時，你應該制定出怎麼樣的 "interface" 才能清楚地描述。

這本書非常推薦給已經有足夠的實做能力，但是尚未有足夠經驗定義出理想的 API 規格的團隊來研讀。



**Software Engineering at Google**:

這本書我幫保哥打一下廣告，這是本好書，在還沒有中文版的時候，保哥就釋出了一版中英對照版本，放在線上公開給大家免費閱讀。目前已經有中文版的書籍了，若需要更精準的翻譯，推薦大家去買這本書 :D

保哥的翻譯版本: [電子書](https://software-engineering-at-google.gh.miniasp.com/)

這本書講了 Google 的軟體工程，包含團隊文化，包含知識共享，還有許多從 Google 角度的軟體技術決策。從 Google 的視角 (因為 Google 在很多領域已經沒有對手了) 他們會正式它們任何決策對世界的影響力，因此也引發它們在決策時的思考脈絡。

這本書內容很廣，深度也夠。我們也還在閱讀中，我會推薦在務實面的問題都解決到某個程度時，或是你們已經有某些領域在業界已經是領先的團隊時，可以看看 Google 在這樣的高度怎麼看待軟體跟技術的開發決策，帶出它們背後如何用這樣的想法推動內部的軟體工程，來塑造 Google 的文化。





# 第一部分小結

寫到這邊，第一部份就算告一段落了。我把開始 "設計" API spec 前的動機跟效益都先交代過一遍了。這裡對應到演講內容，應該涵蓋了前面 20 min 的部分。我把相關的資源都列在這邊，有興趣的可以參考:

DevOpsDays Taipei 2022 Keynotes:
* 議程連結 - [DevOps 潮流下的 API First 開發策略](https://devopsdays.tw/speaker-page/115)
* [投影片連結](https://www.facebook.com/andrew.blog.0928/posts/pfbid02Du2gpZ8nD3XPmfULAyHNs4DBAGDKHsHKpNP84QhBTN7NJ9UUr4nGzoKeCjhHj4wPl)
* [大會共筆](https://hackmd.io/@DevOpsDay/2022/%2F%40DevOpsDay%2FryaejF6ei)

Will 保哥的技術交流中心 直播
* [活動預告](https://www.facebook.com/andrew.blog.0928/posts/pfbid0Wyto3M72tzCgCinmDXJtumgUwQpYJ6dQUKoLoKULJxPJCAKPvzxveXTbX4x9znSBl)
* [直播錄影](https://www.facebook.com/andrew.blog.0928/posts/pfbid0wsyjsDxvjG8b2VpvtgQxjkcnaZsE5LF4FJDW18yCUdU2oGkvQDDPSPdBMxqv7pe7l)

原本我是打算一口氣，一篇寫完的... 不過因為補上了在台上被我刪掉的內容，看了看要塞在一篇實在太拚了，就決定分成兩篇來寫。先把觀念的部分都交代告一段落，下一篇就會從實際推動 API First 的流程，一切以 Contract 為準的做法探討，同時也會說明以狀態機為主來設計 API 規格的作法。不知道有沒有機會，有合適的場合的話這段設計的過程其實很適合弄成 workshop... 等不及的朋友們也可以先看投影片 + 直播的錄影，也請期待下一篇文章 :)