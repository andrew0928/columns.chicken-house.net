---
date: 2025-07-21
datetime: 2025-07-21T20:09:19+08:00
timestamp_utc: 1753099759
title: "繼續這題: Emerging Developer Patterns for the AI Era /"
---

繼續這題: Emerging Developer Patterns for the AI Era / 3, Docs are evolving ...

--

Document, 在 Vibe Coding 當道的年代 (也不過才半年) 突然之間變成顯學。兩年前 ChatGPT 爆紅, 當時大家談的是 Prompt Engineering, 現在談的是 Context Engineering, 差別在哪? 差別在於模型理解能力，跟使用工具的能力都變強了。Prompt 寫得好不好重要性越來越低，更重要的是 "對的資訊" 有沒有被放到 Context Windows 內? 跟 RAG 奮鬥過的各位應該知道我在講什麼 XDD

AI 要能處理越來越複雜的任務，相對你要給他的 context 就越來越多。你有可能在 “Prompt” 內把所有資訊都打完嗎? 對比人跟人的溝通，複雜度到某個層次，就會從跟你交代事情始末 (用講的)，變成給你看文件 (都寫在這裡了，你看完我們再討論)。於是，驅動 AI 完成任務的 context 來源，就從 prompt 逐漸轉移到 document.

所以，現今你看到大部分的 AI (尤其是 vibe coding) 工作流程，工作方法，都在強調 context 跟 document. 上禮拜 AWS 推出的 Kiro, 就是一套以文件驅動開發而設計的 IDE。

文件已經變成開發流程的 context 了, 有點像古董的作業系統會有的 "virtual memory", document 跟 context windows 的角色也類似。文件可以儲存無限的內容，而模型的 context window 有限，當下不重要的資訊就可以從 context windows 移除 (寫回檔案)；當後面步驟需要時可以再透過 (MCP) tools 把資訊從檔案放回 context, 因此你工作的每個步驟，如何精確的掌控這步驟要 "載入” 那些內容就很重要了，這也是 context engineering 在談的技巧。

而文件, 尤其是 markdown, 容易閱讀也容易編輯 (還方便版控), 就成為首選的格式了。你可以拿 document 當作 requirement, 也可以當作 design, 甚至可以當作 tasks ( todo list ), 當你決定變更設計，Agent 可以先幫你列出 100 個工作項目 ( 先存放在 tasks_md ) 就不會被忘掉了，之後 AI 不時來 tasks_md 查看，一個一個任務幫你完成後銷掉, 直到完成任務。這時 tasks_md 就能扮演 "長期記憶" 的角色，不但記得，而且目的很明確 (就是 todo list)。各種用途的文件, 組合起來讓 AI 能夠隨時讀取, 隨時修正任務目標。Agent 就能從過去只能依據 128k context window 的資訊給你答案，提升到 (體感) 能從幾百 mb 文件內的資訊給你答案。

實際上的應用，我看過同適用到爐火純青的案例… 有同事在 instructions_md 寫了這麼一段:

----
(濃縮內容)
當我工作到一個段落，或是有重大變更的時候，請幫我把時間，以及摘要資訊紀錄在 dev-notes_md 內。(何謂 “告一段落" 或是 "重大變更"，他另外有定義，我就略過了)。
----

這時 cursor (其他 IDE 也一樣) 就搖身一變，變成開發祕書了，你改了一堆 code, 他就在背後默默的幫你摘要筆記下來了。這跟 Git Commit 不同，有時候我寫失敗的東西我不會 commit, 但是會留下工作日誌為何失敗，哪裡失敗，作為下次重來的參考…

分享一下他的某個 side project, 這些 dev-notes 就是這樣來的:

GitHub Repo: / lis186 / taiwan-holiday-mcp
(同事寫的 MCP, 台灣假日查詢..., 完整連結我放留言)

這類例子還有很多，例子舉不完，就點到為止就好。包含前陣子我提的 vibe testing, 也是用同樣概念把整個流程串起來的。”文件在進化 / Docs are Evolving… “ 確實如此。單純看趨勢報告，我的感受其實不會那麼強烈，而是實際經歷過這些變化，再來看報告整理，就會有一種突然想通的感覺，原來我一直在嘗試的就是這麼一回事啊..

看趨勢報告，是個很好的練習。如果你能找到一份你正在努力領域的趨勢報告，別看完就放掉了，好好地往下挖。趨勢報告描述的場景，你如果能一步一步拆解推演，直到跟你現在在做的事情連貫起來，那麼這領域你大概就能想的夠透徹了，這些經驗跟手感才會是你的。

這也是我為何看到這篇報告，會願意花時間，一項一項地把我自己經驗貼出來，因為想通了，這些累積的經驗就是我的了，希望留下這些訊息，也能讓更多人想通這些脈絡。

一樣，相關連結我放留言，文件在進化的主題就到這邊，請期待下個主題  :D

![](/images/facebook-posts/facebook-posts-attachment-2025-07-21-001-001.png)
