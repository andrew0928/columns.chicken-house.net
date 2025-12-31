---
date: 2025-03-20
datetime: 2025-03-20T22:46:07+08:00
timestamp_utc: 1742481967
title: ", LLM - Function Calling (Case Study)"
---

#3, LLM - Function Calling (Case Study)

昨天談完 Function Calling 的基本型態, 今天來看看實際上可以做出什麼類型的應用吧~

簡單的說，推理能力夠好的 LLM, 已經有辦法從:

1. 可用的指令規格
2. 你的意圖

直接產生符合 (1) 跟 (2) 的對等 "指令執行順序" ..., 如昨天所說, 這是將文字敘述的意圖, 翻譯成指令集執行順序的編譯器了。這在過去不靠 AI 是完全做不到的事情，我才會說所有 AI 神奇的應用，大半都是從 Function Calling 的能力累積而來的。

不過，昨天只談了一半，解譯出 "指令執行順序(含參數)"，只有 "Calling" 啊，Function 應該是有 Return 結果的，而且有時應該要有順序相依關係的 (你要執行完 Func1, 拿到結果後才決定怎麼執行 Func2 ..)

於是，來看看這頁簡報 (同樣是來自 .NET Conf 2024 我那場的簡報) 吧。這情境是:

User: find a 30 min slot for a run tomorrow morning
(幫我找明早 30min 空檔, 我要慢跑)

先省略中間過程，我期待 AI 能幫我處理好所有事情 ( 按照要求 Booking 行事曆 )，並且回覆我這段訊息:

AI: Morning run scheduled for tomorrow at 9am !
(已經幫您預約好明早 9:00 慢跑)

這神奇的結果，是怎麼靠 Function Calling 辦到的? 我就列出檯面上 & 檯面下的對談過程，你大概就能理解這整件事的來龍去脈了。

0) system: tools: [ "check_schedules", "add_event" ]
1) user: find a 30 min slot for a run tomorrow morning

送出這段歷程後, 第一次 AI 會回應:

2) tool: [ check_schedule( 03/21 06:00, 03/21 12:00 )]

收到這段回應後, 代表 AI 需要叫用 check_schedule 這工具, 並且給他時間範圍, 明天 (03/21) 的 06:00 ~ 12:00...

當你的應用程式, 代替 AI 執行完這段指令, 並且回覆結果 ( append 對話紀錄 )

3) tool-result: [ "07:00-08:00, 起床換裝", "08:00-09:00, 吃早餐", "10:00~12:00, 跟同事視訊會議" ]

送出後, AI 得到結果，判定思考後，會再次送出這回應:

4) tool: [ add_event( 03/21 09:00 - 09:30 )]

同上面的過程，AI 表達他需要使用 add_event 這工具。你的應用程式應該替他執行並且給 AI 執行結果:

5) tool-result: [ "success" ]

再次送出結果給 AI，最後 AI 判定任務完成，就彙整上面的過程，最後直接回應這訊息:

6) assistant: morning run scheduled for tomorrow at 9am!

以上就是完整的對話過程。這邊留意，我標示的 1) ~ 6), 是 chat history 的序號跟內容。每次呼叫 AI Chat Completion，都是把 history 當下為止的所有內容 (從 0 開始) 都送出去。

而 system 代表 system prompt, 最高優先權, 背景設定用；
而 user 則代表使用者直接輸入的訊息；
而 assistant 則代表 AI 要回應給使用者的訊息；

其中 tool 代表 AI 回應給 APP 的訊息, 需要 APP 檯面下替他執行這指令，而 tool-result 則是 APP 執行後在檯面下回覆 AI 執行結果的兩種特殊 message.

每次呼叫 AI Chat Completion, AI 就都能根據目前的前後文做出下一步的決定，直到完成任務為止。

--
是否很神奇? 原來這一連串不可思議的動作，其實拆解下來也很普通，就真的是昨天介紹的基本型態 function calling, 以及前天介紹的 structure output 的組合應用而已。

實際上的狀況是，你要寫這種應用程式不用那麼辛苦，跟我一樣土炮這整個過程... 這過程主要是研究用，當你搞清楚後，有很多成熟的 framework 可以讓你簡化這一連串的動作。

這部分我就不推薦直接使用 Http, 也不推薦直接用 OpenAI SDK 了, 因為你程式碼要處理的細節太多, 你可以直接選擇成熟的框架 ( 例如: Semantic Kernel )，成熟的 No Code 平台 ( 例如: n8n, dify )，或是成熟的 LLM Client + MCP server ( 例如: Claude Desktop, Cursor ... ), 其實都是在做同樣的事情。

連續三天，看到這邊，是否有解開一些疑問? 是否想通了 AI 這些神奇的能力是怎麼被創造出來的? 這三部分，我常常都稱他為 AI 時代的開發基礎技巧，它的重要性不亞於當年我剛開始學寫程式時，書上交給我的基本流程控制技巧 ( 例如: If, For Loop 等等 )。我強烈建議所有的 Developer, 應該把這些應用方式當作基礎能力, 確實的掌握清楚後再來學各種框架或是快速開發的技能。

想要實際看看這些 code 是怎麼運作的嗎? 雖然不推薦實戰使用, 但是為了教學目的, 我還是把各種框架下的 coding 範例準備好了。想親眼目睹這些過程的朋友，一樣請參加 03/25 的直播 XDDD

(每日業配: 直播連結請見第一則留言)

![](/images/facebook-posts/facebook-posts-attachment-2025-03-20-001-001.png)
