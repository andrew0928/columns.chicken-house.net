---
date: 2025-10-09
datetime: 2025-10-09T19:30:03+08:00
timestamp_utc: 1760009403
title: "補一下先前 PO 了很多篇的 A16Z 趨勢報告, 當時覺得 (5) 跟 (9) 沒什麼想法，就跳過"
---

補一下先前 PO 了很多篇的 A16Z 趨勢報告, 當時覺得 (5) 跟 (9) 沒什麼想法，就跳過了。這禮拜看完 OpenAI DevDays 2025 有了些新的想法, 就決定來補一下這兩篇。今天先聊聊 (9), 明天來補 (5), 報告中原標題分別是:

( 5 ). Beyond .env: Managing secrets in an agent-driven world
( 9 ). Abstracted primitives: Every AI agent needs auth, billing, and persistent storage

我把這題歸類在 **Agentic Application** 需要的基礎設施。這段闡述了 “基礎建設” 這件事未來的發展，例如計量 (Usage)，收費 (Billing, Payment)，通通都會被標準化，並且變成每個 Agent 都能通用的標準規格。

這話題，我腦袋裡剛好浮現這幾個實際的應用案例:

MCP Sampling:

這個談的是 Token 的集中處理的協定。MCP 有個有趣的規格: Sampling, 說真的這名字取的真爛, 但是這是個好東西。

通常 Token 指的是 "選用的模型" x "使用的算力", 而 Agent (ex: ChatGPT) 都是採訂閱制度, 頂多限定使用量而已，不會像 APIKEY 一樣精確地去計算一個 Token 多少錢。因此訂閱方案大都會有足夠的 Token 來使用。

當 Agent 呼叫 MCP tools, 而這 Tools 處理過程也需要 Token 的時候，MCP Sampling 提供一個類似 "Callback" 的做法，可以把 Prompt 丟回給 Agent, 處理好後再拿結果回來。這規範讓 MCP 不需要自己準備 Token，而是統一算在使用者的訂閱身上。使用者也有絕對控制權，包含是否允許，以及看到傳遞了什麼內容，就像現在你都可以決定對話過程要不要 call Tools, 以及可以看到 call Tools 的傳輸內容一樣。在 LLM / Token 的管理範圍上，已經統一了 Token 的 Usage / Billing 了。我覺得這趨勢正在發生中，方向也正好跟趨勢報告講的一致。

Agentic Commerce Protocol:

我貼的圖，就是 ACP 的 sequence diagram，有興趣可以參考 OpenAI 官網

這是兩個禮拜前, OpenAI 發表的規格，為了完成 Instant Checkout 的操作 ( 你可以在 ChatGPT 問問題，看到推薦商品後能在 ChatGPT 立即結帳完成購物 )，背後推出的技術規格: ACP, Agentic Commerce Protocol。

他背後是一組 API 的規範，規範了三種角色的標準行為:

1. **商家**, 要支援 **Checkout** 行為的 API ( 結帳交易的確認 )
2. **支付**, 要支援 **Payment** 行為的 API ( 金流的處理 )
3. **商家**, 要支援 **Product Feed** 行為的 API ( 商品資訊來源 )

細節就不多聊了，官網連結在這邊 (見留言)，有興趣自己研究。這是另一個具體的案例，過去 SaaS 很多服務都是由 Cloud Infrastructure 提供，例如 AWS, Azure 等。隨著趨勢的演進，應用程式逐漸往 Agentic Apps 靠攏了，未來提供這些 PaaS 的角色，會開始變成這些 AI 大廠。到目前為止，上面談的 MCP 來自 Anthropic, ACP 來自 OpenAI ... 大家都想統一這些 Agentic App 應用必要的基礎服務，這野心其實很明確.. 也完全符合趨勢報告談的 (9) 這題

其他我覺得也有可能發生，但是還沒看到的，就收在這邊一起聊好了。我覺得可能還會出現的標準:

由 SEO (Search Engine Optimize) 轉移到 AIO 的相關標準變化

Tracking:

這是廣告業務的大宗，過去都由 Google 主導。如果越來越多的應用轉移到 Agent 上的話，Sam 昨天才發表 Agent Kit ... 未來的流量開始會轉移到 Agent 手上，新的 Tracking 規範也許就會產生

由 Cloud Infrastruction 轉移到 Agent Infrastruction 的相關標準變化

Access Control:

用過 Cloud 的大概都不陌生，從 IAM 的角度有各式各樣的基礎設施，讓你控制你的應用程式認證跟授權的基礎建設。我拿 OpenAI 發表的內容當範例，如果以後你的 APP 都建立在他的平台上，使用者都有 OpenAI 的帳號，那麼從剛才提的 Tracking, 到使用者的 Access Control, 到 APP 的 Access Control, 可能都會有新的作法或標準出現..

Billing & Usage:

這更不用說了，舉個直白的例子，如果 MCP 繼續發展下去，未來可能就會出現: Tools 按照呼叫次數來計費 (就像 Token 一樣)。這時，需要每個 MCP 開發商都自己去發展一套帳務系統嗎? 如果不是的話，那 Agent Infrastructure 來做這些事情最自然不過了。這類帳務的基礎，不外乎是 Usage (使用量，知道你用了多少) 的追蹤，以及 Billing (帳務，計算你的使用量該付多少錢，以及付清了沒)。再加上已經看到 ACP 這樣的規範，我覺得 OpenAI 會發展成 Agent Platform 根本就是必然的事情了，難怪有人說 (忘了哪裡看到的)，OpenAI 的發展路線，就是 Agent 世界的 Microsoft ... 

這兩個章節，談的其實都是很基礎建設的主題，觀察現在市場的發展，以及趨勢報告的預測，隱約之間也看清楚了技術跟市場的發展脈絡，挺有意思的思考跟研究

--
花了點時間把這段補上了，我也順手把過去全部 A16Z 這篇趨勢報告的解讀跟我個人的想像，也都收錄到同一篇文章了。

這段的連結很多，我就不一一貼上了，有興趣請直接看我部落格文章的好讀版，歡迎分享＆討論，也歡迎給我回饋 :)

![](/images/facebook-posts/facebook-posts-attachment-2025-10-09-001-001.png)
