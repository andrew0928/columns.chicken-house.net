---
date: 2025-06-16
datetime: 2025-06-16T19:58:29+08:00
timestamp_utc: 1750075109
title: "今天繼續來談談 A16Z 趨勢報告的第二個主題: AI-driven interfaces."
---

今天繼續來談談 A16Z 趨勢報告的第二個主題: AI-driven interfaces.

這題是很好討論的題目, UI 比起 Git (第一個主題: AI Native Git) 而言更具體了，要實現它的技術都已經出現，要 PoC 的話已經完全不是問題，只差在你多快能實現它，多快能運用在你的系統或產品身上而已。

我選擇用副標題 (AI-driven interfaces) 為主,  而不是原文的主標題 (Dashboards → Synthesis), 因為我更認同副標題的意念。而 Dashboard 變成合成 (Synthesis) 產生，則是理所當然的結果而已。為何用 Dashboard 來說明? 因為它最複雜, 理解的門檻很高, Dashboard 的設計用意是讓你一目了然某系統運作的全貌，但是你關注的重點往往高度跟你的腳色及意圖相關，而這是使用階段才決定的事，難以在設計階段決定，因此造就了這些使用落差..

談到 AI driven interfaces, 我正好有點經驗可以拿來說嘴 XDD, 在 2023 年底的時候，我嘗試 "安德魯小舖" 的過程中，就碰到這題目，當時我在思考 "對話" 的操作方式會取代 "UI" 嗎? 最後我的答案是 "不會"，因為 UI 仍然有他擅長發揮的場合，全部都變成對話也很怪。而去年我在 DevOpsDays 2024 的 Keynote 也聊了這個主題，我切入的是 AI 帶來 UX 的改變，當時我是這麼說的:

----
傳統 APP 的 UX 高度仰賴設計師大量的事前訪談，猜測使用者操作當下的情境，給予最合適的操作介面。猜對了就有好 UX。而 AI 走的是另一條路，藉由對話來掌握當下使用者的意圖，給予最合適的操作介面與資訊。這是降為打擊，設計階段永遠處理不了執行階段才發生的所有狀況 (尤其是少數特例)，但是有了意圖理解能力的 AI 可以 (只要模型持續進步)..
----

所以，未來的 UI 應該會模組化，不會像 Wizard 一樣從頭到尾都靠 UI，而是會變成模組化，切割成單一任務 (例如檢閱商品，結帳等等)，然後由 AI 來主控，引導你逐一完成每個步驟。UI 元件，會化身成 AI 可以調用的 tools, 當使用者需要時，AI 可以調整 UI (用 tools + parameters)，呈現出當下使用者需要的畫面內容。

而呈現的方式，這篇趨勢報告用了三張圖，很貼切的表達了我當時的想法 (我也很慶幸我的想法有在發展的主流軌道上 XDD)。這三張圖分別代表 過去 / 現在 / 未來 的可能樣貌:

圖1: [傳統] Traditional dashboards: complex and hard to search for information

圖2: [動態] Dynamic dashboards: AI agent Q&A and actions

圖3: [代理] Agent-ready dashboards: providing information for humans and agents at the same time

而這些背後需要的技術基礎，文章沒提到，不過我已經可以串起來了，接下來我花點篇幅來聊聊這部分我的看法，各位也可以想一想你未來需要累積或是準備什麼技能。

圖2 [動態] 的 dashboard, 其實跟傳統的沒兩樣，只是透過 agent 協助, 能幫你省掉一些操作, 幫你找到你該在 dashboard 看的資訊而已。LLM 的 tools use 技術早已成熟, 只是這些 tools 不是 API, 而是 dashboard 上面的 widget, LLM 透過對話掌握你的意圖後, 在允許的 tools (widget) 清單內挑出合適的項目，幫你設定好 (tool parameters) 呈現在你面前。現今的系統其實不需要大規模調整就足以實現。

圖3 [代理] 則層次更進階了。這已經不是 "預設" 的 widget 直接拿來用就好, 需要的可能是更細緻的元件, 讓 AI 能動態組成你現在想看的資訊。如果硬要跟現在成熟的技術當作對比，我覺得 markdown + mermaid 這類技術其實更貼近這樣的想像。試想你現在正在使用 cursor / vscode + github copilot 的工具，並且用 agent mode 讓 AI 幫你整理許多資料, 輸出成 markdown, 當下打開預覽…

文字的敘述，資訊的摘要與彙整，用 Markdown 來處理文字格式，表格，都已經不是問題。AI 對於 markdown 的理解能力也足夠。但是圖表呢? 我常用的技巧，就是讓 AI 產生 mermaid scripts, 並且放在 markdown 文件內，這時支援度夠好的 markdown viewer 就能在文件內嵌這些圖表。

這邊舉的例子: mermaid 只是其中一個案例, SVG 等等其他格式也都沒問題, 甚至你要自訂都可能。只要你的 viewer 認得, 只要你的 AI 懂得語法能替你把 "資訊" 翻譯成 "Script" 就沒問題。這時，你的意圖就能更精準的，用更合適的介面 (UI) 呈現在使用者面前。

要做到這樣的應用，你的系統需要更 “AI Ready” 才行。兩年前大家在談的是 RAG，談的是在 Agent 對話介面，如何整合後端搜尋檢索 (最常見的是向量資料庫)，動態生成文字訊息的回應。而這樣的 UI 對我來說，就是同樣的技術，但是整合更多元的技巧，協力完成的結果。

舉例來說 (我就按照圖三，看圖說話)，當我詢問了 Agent: 今天的 API Gateway 系統運作狀況如何?

- AI 會按照上下文，動態生成 Log Query ( 或是對應的 Log Query Tool Call ), 找到對應的查詢結果
- AI 會按照上下文，動態生成 Error Message Query , 找到對應的查詢結果
- AI 會按照上下文，Call Tools 查詢 Deployment 紀錄
- 這些蒐集到的資訊，都彙整到 context windows 中，讓 LLM 直接生成結果輸出

聊到這邊，我才發現，各家 LLM 都不約而同，早就拿 markdown 當作通用的輸出介面，真是有遠見。是巧合還是精心規劃設計的結果? 我猜這些跑在前面的人，早就料想到這些了，這一切其實都規化的很清楚，只要逐步推進，等待每個環節技術成熟，這件事就到位了。

一開始我就提到，就技術而言，現在已經完全可以實現這樣的能力了，我想這份趨勢報告講這點的用意，已經不是在講技術突破，而是在講，未來 UI 的演進方向會朝這方向邁進了。對於開發人員，我想你需要掌握的是，你是否有能力實現它? 它背後需要的系統架構會是甚麼?

對於產品設計人員，你需要掌握的是，你能否掌握這樣的使用習慣，替使用者規劃最合適的產品功能? 當你的開發團隊已經有這樣的實作能力時，你是否開得出夠好的規格讓它們發揮? 使用者給你的回饋，你是否能善用這樣的能力給它們更好的體驗?

AI-Driven UI 這主題，也是個很精彩的趨勢預測，令我更開心的是它也驗證了我過去在不同場合分享過的多個觀點。這次的參考資訊有點多，我統一收在第一個留言下的回覆。

![](/images/facebook-posts/facebook-posts-attachment-2025-06-16-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-06-16-001-002.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-06-16-001-003.png)
