---
date: 2025-06-26
datetime: 2025-06-26T21:57:49+08:00
timestamp_utc: 1750946269
title: "繼續這題: Emerging Developer Patterns for the AI Era /"
---

繼續這題: Emerging Developer Patterns for the AI Era / 3, Docs are evolving ...

* * * * *

前一篇談了這兩年大家用法的改變 (從 prompt 逐漸轉移到 document) 的過程, 再來我想舉個實際的使用案例來說明。這類案例我碰過好幾種，今天先談一個: document as code ...

其實我推 “document as code” 的想法很久了, 簡單的說就是把文件當作 code 一樣處理。用寫 code 的工具跟流程來寫 document ( 工具挑 vscode 之類的, 格式用 markdown 首選 )；版控跟儲存則直接沿用 git ，文件的發行則直接用 ci/cd pipeline 發行靜態網站，一切都很合情合理。

不過在過去，這樣做的效益就是統一 code 跟 document 的工作流程與工具鏈而已，從效益來看也是有賺，大約可以達到 1 + 1 = 3 的效益，爆炸性成長就還不至於, 也因此 "document as code" 也還未成為 "must have" 的流程。

不過這兩年開始不同了，就是因為 AI coding。知道為何我上一篇要花時間聊 “document” 如何逐漸變成 prompt 的載體嗎? 因為越來越多資訊要餵給 AI (agent)。你一句話要跟別人說，你會用講的。你要跟 100 個人說，要說 100 次，你會寫文件叫對方看。把 AI 當作人來看待，這也是一樣的道理。LLM 的 context windows 不需要長期都放著整份文件內容，只要放 filename，搭配合適的機制 ( RAG or FileSystem MCP 之類的工具 )，LLM 就可以像虛擬記憶體般，在 LLM 有需要的時候再載入 (現在進階到 LLM 生成的資料也可以寫在 document 暫存了, 後面對話有需要再靠 MCP 拿出來..)。

於是，現今絕大部分的人，在使用 github copilot / cursor 這類 AI IDE 的時候都這麼做了，若算上 "虛擬記憶體" 的機制，整個 repo 邏輯上都可以當作 "virtual" context window 了。把常用的 prompt / rules 放在 repo 內 ( 當作跟著 repo 的設定 )，把開發相關的需求與規格文件放在 repo 的 /docs 下，把對應的程式碼放在 repo 的 /src 下，整份專案一起版控，一起發布。AI 就不斷的在 /docs 跟 /src 之間替你 "翻譯" 與驗證，逐步完成開發的任務。

當 AI 能有效處理 documents / source code 之間的對應時, 就開始有 1 + 1 = 10 的效益了。現今的 vibe coding 對應的 repo, 文件都占很重要的比例，因為日常開發的流程改變了，大致上變成這樣:

--

1. 我要開始開發一個功能，我先看文件，找出 requirement 在哪邊，告訴 coding agent 按照這需求來實作..

2. 文件沒說的，我用 agent mode 直接說 ( 或是 create issue ) 告訴 coding agent 該做甚麼..

3. agent 處理完之後，會直接產生文件或程式碼告訴你處理結果 ( report, issue, message 等 )

4. 你會先 review 文件，來確認結果是你要的，再來 review code 看看是否真的是那麼回事，沒問題並且通過 unit test, 就 merge / commit ..

--

過去很難整套都吞下來的軟體工程流程，尤其是大量的文件跟測試這部分，現在都垂手可得了, 要落實他不再是奢侈的行為 (人力很貴啊)。這改變我覺得回不去了，改變的速度只會越來越快而已。標準的軟體工程 (甚麼都要有文件，文件跟程式碼要維持一至) 會越來越普及，將來任何一個小團隊都有能力做得到。

如果文件開始能跟程式碼有效的 "翻譯" ( 叫 AI 按照需求文件寫成程式碼，我覺得就是在 "翻譯"，把 document 翻譯成 code 的過程就是 vibe coding )，逐漸的每個人就只會想講 "母語" (自然語言) 了。程式語言 對大部分的人來說都是外來語 / 外星語，那是機器世界的母語，不是人類的。當翻譯能力成熟到某個程度，文件就是溝通的工具了。跟 "誰" 溝通? 當然是 "真人" ( developer, user, product owner ), 以及 AI agent, 以及各式各樣的 tools ... 我想這才是這個 "趨勢" 想要表達的, "docs are evolving", "documents are becoming a combination of tools, indices, and interactive knowledge bases".

實際上, 我自己跟 AI 協作的方式就已經是這樣用了, 不知不覺文件的產生數量變多了, 心態上也改變了, 我不是為了 "要寫文件" 而寫, 而是為了 "要讓 AI 一次能讀懂我要什麼"，並且要重來的時候不用再從對話複製貼上一大串文字... 無形之間就變成這樣的結果: 靠文件溝通。

* * * * *

有機會的話 (懶 XDD)，下一篇來聊聊我自己的用法, 也聊一下我看到同事的用法.. 某同事靠 document 跟 agent 的協作, 真是用的出神入化 XDD, 各位值得期待一下..

--
相關參考資訊我放留言
1. A16Z 趨勢報告 (3)
2. 我九年前的舊文章 - Blogging as code
