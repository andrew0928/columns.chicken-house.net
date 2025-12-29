---
date: 2025-03-27
datetime: 2025-03-27T22:11:22+08:00
timestamp_utc: 1743084682
title: ", 土炮 function calling"
---

#8, 土炮 function calling

前天直播的時候, 在 zoom chat 看到一段話, 不過直播當下沒辦法分神去回應那些訊息... 事後想起來，我就補了 #8 來聊聊這題吧...

聊天室是這樣講的: 

"某些MCP Client有支援Deepseek r1，但是Deepseek r1並沒有支援function calling，他們會是怎麼實現的@@? 好好奇"

其實，只要模型本身的推理能力夠強，之不支援 function calling 只是封裝的 API 問題而已，認真要土炮，懂得原理的還是變得出來的...  我在 .NET Conf 2024 有示範這件事耶，只是當時只有 40min，根本沒辦法好好的講這題，我猜當下也沒多少人聽得懂我要表達的意思吧... 

不過，直播當天我有好好地交代這個案例 (我特地把 function calling 整個過程的 Http Traffic 都 Dump 出來給大家看過程)。在 OpenAI Chat Completion API 替所有的訊息定義了幾種角色 (role), 常見的有這三個:

- system ( 用作 system prompt, 規範整個對話層級用的 prompt )
- user ( 由使用者端直接發出的訊息 )
- assistant ( 由 LLM 端發出, 給 user 閱讀的訊息 )

而加上了 function calling, 訊息結構也擴充了。除了 request payload 多了一段 tools 的定義之外，訊息也多了 tools 溝通專用的模式:

- assistant ( +tool_calls , 由 LLM 端發出, 指示需要調用的 tool 資訊 )
- tool ( 由 tool 執行後回應的訊息內容 )

其實抽象化之後，所謂的 Function Calling，只有三個要點:

1. 要先定義好有哪些 tools 可以給 LLM 使用
2. 對話就變成三方對話，LLM 要區別 user 以及 tools 的對話
3. LLM 要生成該使用哪個 tool, 以及使用 tool 必要的參數

而 Chat Completion API, 則只是把這三個要點，精確的定義成 API / Message 的格式定義而已。

想像成你是老闆 (role: user)，旁邊有幫他辦事的秘書 (role: tool)，老闆的行事曆控制全掌握在秘書手上，因此管家 (role: assistant) 要替老闆安排活動的話，應該聽完老闆要求，私下跟祕書協調後，最後回報老闆任務完成。

圖一是案例，直播時候已經說明過了。圖二是土炮的 system prompt, 我用白話文, 自己定義了兩個角色，要 LLM 用不同的前置詞來區別 LLM 是要跟誰對話。如果訊息最前面是 "安德魯大人您好" ，就代表這句話是給我看的。如果訊息最前面是 "請執行指令"，則代表這是給秘書看的訊息。

對話原則 setup 好了之後，對話過程就是圖三 了。你只要眼不見為淨，忽略掉中間灰色不是跟我對話的區段，其實整個過程就通了。如果你要在不支援 Function Calling 的 LLM 土炮 Function Calling 功能，只要用 Chat Completion API 照順序呼叫，並且由你的 Application 攔截這些 "請執行指令" 開頭的訊息就夠了。

每次我在說明這個例子，當下就覺得很羞恥.. (我是多期待大家叫我 "安德魯大人您好" 啊啊啊啊...) XDD，不過，這個例子我原封不動貼在 Chat GPT 上，還真的能夠正常運作，當然正規場合你別這麼土炮，乖乖地用支援 Function Calling 的模型，搭配 Semantic Kernel 這種能幫你處理 Function Calling 的框架就好。貼在 Chat GPT 上，只是為了讓大家理解背後的通訊過程而已。

--
直播結束, 今天沒葉配了，想看直播回放的，請看上一則 PO 文
想看完整 Chat GPT 對談紀錄的，我把連結放第一則留言

![](/images/facebook-posts/facebook-posts-attachment-2025-03-27-002-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-03-27-002-002.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-03-27-002-003.png)
