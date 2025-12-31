---
date: 2025-03-19
datetime: 2025-03-19T22:04:29+08:00
timestamp_utc: 1742393069
title: ", LLM - Function Calling (Basic)"
---

#2, LLM - Function Calling (Basic)

昨天聊完 Json Mode, 今天繼續來聊聊 Function Calling... 同樣是我在 .NET Conf 2024 的簡報...

Function Calling (或稱為 Tool Use), 我覺得這是 LLM 普及以來, 威力最大的功能了。就因為 LLM 有了這能力，才開啟了各種 Agent 以及透過 AI 來主控各個週邊系統的能力。所有想要在你的 App 內應用 LLM 的 Developer, 請務必要搞清楚 Function Calling 是怎麼回事, 這我認為是下個世代最重要的基礎知識了。

我先分解動作，今天只聊基本動作，明天再來談連續動作...。昨天聊到 Json Mode, 當你問 LLM 問題，指定 LLM 要用你提供的 Json Schema 輸出 Json Object, 這能力其實是開啟了 LLM 跟 code 之間 (用 json) 資料交換的通訊基礎了。而 Function Calling, 則開啟了 LLM 跟 code 之間的函數呼叫 ( 正是 Function Calling ) 的通訊基礎。蹭一下最近不知道在紅什麼的 MCP, 其實就只是 Function Calling 的實體化通訊協定。

Function Calling 是在對話開始之前, 預先告知 LLM 你有那些 "Function" 可以使用? 然後在對談過程中，讓 LLM 自己決定他要告訴 User 結果 ( Text ), 或是他要先執行指令 ( Function ) 並看看結果後再決定 ( 繼續執行指令 Function , 或是直接給結果 Text ) ?

極度簡化過的基本型，就如這頁簡報，一開始的 system prompt, 我告訴 LLM:

--
Based on the following conversation, manage the shopping list, write your response in JSON using the following format:

[
  { "action": "add", "item": string,  "quantity": string },
  { "action": "delete", "item": string }
]
--

告知有哪些動作 ( action + parameters ) 可以用來維護購物清單後，接著就是給他需求:

Mmm, remember to buy some butter and a pair of zucchinis. But I already bought bread.

推理能力夠好的 LLM 就能夠解讀這段對話的意圖。知道這段對話要提醒你記得買奶油，兩個櫛瓜 (我今天才知道這字的意思 XDDD)，麵包我已經有了不用再買。

依靠強大的推理能力，跟前後文 (其實這裡也包含了昨天介紹 Json Mode 的能力)，LLM 已經能將這段對話的意圖，用你給他的指令集表達出來。某種程度，已經是自然語言跟你給他的指令集的編譯器了。這些對話，你貼在幾個主流的 LLM 都能得到一樣的答案:

--
[
  { "action": "add", "item": "butter", "quantity": "1" },
  { "action": "add", "item": "zucchinis", "quantity": "2" },
  { "action": "delete", "item": "bread" },
]
--

基本上這樣已經完成一大半了, 都已經用 Json 告訴你接下來該依序執行那些指令了, 剩下的只要寫一段 code, 依序真的執行這些指令就能真的完成任務了。

這就是 Function Calling 的基本原理, 當然實際應用不需要這麼土炮, API / Framework 層級都有更方便使用的模式, 不過 LLM 變化快速, 我高度建議大家還是要搞懂這原理。某些情況下 (例如你同時要 call 前端跟後端的 function)，你沒辦法用內建的機制來運作，或是你要處理更高層級的 Planning 時, 你都會需要自己手動下這樣的 Prompt..

回到 Function Calling, 其實到這裡為止, 你只完成了 "Call", 還沒完成 "Return" ... 更完整的應用案例，我留到明天第三頁簡報再來聊~

--
同樣的, 這些例子我都有準備 HTTP / OpenAI SDK / Semantic Kernel 的完整範例, 會在 03/25 的直播跟大家線上聊這些 code 的奧妙 ~

直播的連結我放在第一則留言

![](/images/facebook-posts/facebook-posts-attachment-2025-03-19-001-001.png)
