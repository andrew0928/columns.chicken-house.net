---
date: 2025-06-27
datetime: 2025-06-27T20:30:03+08:00
timestamp_utc: 1751027403
title: "A16Z, AI 趨勢報告的第四項, Templates to generation: Vibe c"
---

A16Z, AI 趨勢報告的第四項, Templates to generation: Vibe coding replaces create-react-app 

--
週五下班，先來談這題比較不燒腦的 templates to generation 好了, 過去起始一個新專案的基本動作: 從 project template 生成一個初始專案的作法，會完全被 AI coding 取代.. 。這點我完全認同，甚至覺得不只是 project template, 連帶的各種形式的 code generator, 各種 search & copy / paste code 的服務 ( stackoverflow... T_T ) 都有一樣的命運。

這些工具或是服務，廣義上來說都是 code generation .. 而藉由 LLM 來 gen code 效果比起其他方式好太多, 最主要的原因就是 LLM 能理解你的意圖, 而這些能力讓你能用敘述，或是用文件，就足以產生夠精準品質夠好的程式碼，讓其他樣板類型技術完全沒有任何利用的價值..

文章的敘述則是更精確了，比起 project template 是給你一個 "通用"，並且搭配接受度高的 framework ( 泛指 tech stack 選擇 ) 的起始專案樣板，而透過 AI 生成，你可以自己選擇 framework / tech stack，精確自訂，符合你使用情境與需求的起始專案。兩者之間的差別只是幾分鐘的時間差，我想每個人都知道該選 AI coding …

繼續往下前，我摘要一段文章的內容:

This unlocks a new distribution model in the ecosystem. **Instead of a few frameworks sitting at the head of the long tail, we may see a wider spread of composable, stack-specific generations** where tools and architectures are mixed and matched dynamically.

換了方法，你多了自主性。你不再會被 template 限制了你的技術選擇 ( 不會被迫選擇主流 framework, 對 tech stack 有選擇與替換的彈性 )。這些能力甚至放大到極致，如果你專案初期還無法決定 tech stack, 你甚至可以用很低的成本，把你專案需求用每種 framework / tech stack 都生一份出來驗證看看再決定… ( 反正就幾十分鐘的事情)。

看趨勢報告，對各位而言可不是選擇題，決定挑選 AI coding 就結束了，後半部我分享一下這主題延伸的經驗跟想法。過去我們團隊做了類似的事情: 自訂 project template ...，其中一個要解決的問題就是，每個新專案，都要申請一大堆 infra 服務，而這些服務很難懂 (一堆 naming rule 要遵守)，於是我們搭配開發了 SDK, 把部分規範寫在 SDK 內，另外留個 config, 把申請後的資訊填進去，SDK 就會自動轉譯那些難搞的部分，讓專案能 ASAP 就順利完成部署上線測試。

這樣的做法的確有效，而缺點是我們必須花費心力去維護這 project template.. 雖然從上面的結論來看，以後都改用 vibe coding 就好了，但是投資在 SDK 身上仍然是必要的，因為 SDK 封裝了很多複雜的規則，即使不需要 template，他仍然能精簡你的作業流程，也能讓 vibe coding 能少處理這些需求，少產了一大段 code，效率跟正確性也都會提升。

當你越依賴 AI 生成 code, 你就越需要花費心力來提高 AI coding 的成效，透過各種手段降低需要產生的程式碼數量，以及降低需要解決需求的複雜度，都是很有效的手段，不論你是不是用 AI coding。我覺得是看這類趨勢報告必要的思路。除了 SDK，如果流程上若也能對應調整 (我最推的是 TDD)，讓 vibe coding 過程能合理的分段產生 + 人工確認，則能在另一個面向大幅降低 AI 繞錯路的機會。

兩個月前我貼過一篇 PO 文，大意是 vibe coding 的技巧, 講的就是搭配 TDD 的精神來引導 AI 寫出你要的 code. 先讓 AI 替你寫出 interface，你驗證 interface 是否如預期。再來則是針對 interface 產生測試 (同樣你要確認)，這時測試應該會失敗 (紅燈)。再來是讓 AI 把 code 寫完，過程中讓每個測試從紅燈變綠燈。這流程會有效，主要原因都是針對 vibe coding 的弱項 (其實也是人類 coding 的弱項啊)..

1. 一次寫越多 code 越容易錯，TDD 有系統有結構的切成多個步驟分別進行
2. 一次 review 越大包的 code 越難抓出問題，你越早準備好測試，TDD 就能分攤你 review 的負擔
3. TDD 的切法分成 interface, test code, test result .. 都能跟工具對應，每個階段都能 build / run test，你可以第一時間靠工具就抓出低級錯誤

這段比較輕鬆一點，我就寫到這邊，提到幾篇過去我聊過的題目，相關連結我就放留言

- AI Coding + TDD
- A16Z 趨勢報告 (4)

如果你想知道我以前聊過什麼 SDK, 可以看這幾個研討會的簡報

- DevOpsDays Taipei 2021 簡報
- .NET Conf Taiwan 2019 簡報, 大規模微服務導入 #1, #2

![](/images/facebook-posts/facebook-posts-attachment-2025-06-27-001-001.png)
