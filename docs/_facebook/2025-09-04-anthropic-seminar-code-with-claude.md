---
date: 2025-09-04
datetime: 2025-09-04T22:10:02+08:00
timestamp_utc: 1756995002
title: "延續之前分享過, 來自 Anthropic 今年五月的研討會: Code w/ Claude - M"
---

延續之前分享過, 來自 Anthropic 今年五月的研討會: Code w/ Claude - MCP201 這場演講, 還有來自其他資訊觀察到的 MCP 相關設計的想法, 通通都收在這篇一起聊...

MCP 這規範的設計, 源自 Anthropic 團隊觀察人 (user) 跟 AI (agent) 以及其他服務 (service) 如何互動的方式, 抽象化而設計出來的 protocol . 我覺得有意思的是這個 protocol, 他幫助我想像了未來軟體服務的樣貌。為了說明這個，我從這場演講中擷取了這頁簡報當代表..

User 跟 Agent 互動時, 通常都是這樣開始:

1. User 對 Agent 下 Prompt 開啟對話, 跟 Agent 溝通他想要做什麼
( prompts, user driven )

2. User 跟 Agent 溝通過程中, User 想要取得特定的內容, 告訴 Agent 他想要依據這些內容做什麼事情 ( User Add Context, App Request Access To Resources )

3. Agent 了解上下文 ( context ) 之後, 開始思考該如何替 User 完成任務。過程中可能產生資訊，也可能需要與外部系統互動 ( Action, Model driven ), 將互動的結果也加入 context, 持續這些步驟到完成目的為止

這整個互動的過程, 涉及 User + Agent + ( Prompts, Resources, Tools ) 的交互作用，而後面 ( ) 刮起來互動的對象，可能是一個獨立的系統。而 Agent 可能會視 User 需求得跟多個系統同時互動, 因此將這些互動方式標準化的協定，就是 MCP。

也因為如此, Prompts / Resources / Tools 才會被 Anthropic 列為 Agent 世界的 "原語" ( Primitives )，這也會是模塑未來軟體服務重要的基礎。

--

前情提要到此為止，我覺得重要的不是 MCP 這 "規格"，而是 MCP 團隊在這演講中，要表達的未來以 Agent 為主的世界裡, User - Agent - Service 互動的具體模型。這點對我很重要，讓我想得更清楚軟體服務 ( SaaS ) 會如何演變。

過去，軟體從單機進展到分散式系統，RPC ( Remote Procedure Call ) 算是最重要的模型了，所有的 API 都是從這模型發展出來，而 "Call" 這動作也進一步從單向 ( User 主動 Call Service ), 發展出雙向 ( Callback / Webhook )，以及一對多 ( Pub-Sub / Event Driven ) 等模式，而造就了現在的 SaaS 生態。因此 SaaS 的服務是否成功，其中一個指標就是看他的 API 做得好不好，用他的 API 整合的其他系統多不多而定。

而到了 Agent 的世界，這通訊模型就更複雜了。通訊會是 User - Agent 的互動 ( 主要是 Chat , 各種型態的 Chat 都算 )，而 Agent 則會代替 User 跟多個 Service 進行互動。這時 MCP 所描述的互動方式，就會逐漸變成未來 Agent 為主的應用情境下，主要的通訊協定了。

所以做個對比，現在成功的 SaaS 必定會有優秀的 API ( 呼應了我之前一直在談的 API First )，那以後呢? 我想以後會變成: 成功的 SaaS 必定會有優秀的 MCP ( 去年我談 API First -> AI First, 當時還沒有 MCP, 但是基本上就是這概念了 )

因此，我進一步想:

API First, 其實有一套設計良好的 API 的方法，以 Domain 為主，分析狀態的變化，推演出 API Spec / State / Role + Permission 的設計，來打造良好的 API 體系。

到了 MCP 時代，這方法應該是什麼? 我還在思考，不過最近開始有點手感了。把 Agent 也當作真人來看待的話，兩個人 ( User x Agent ) 不斷溝通 ( Chat ) 要有效率的完成任務，其實就是一連串的 Workflow 了。從這個 Workflow 來分析，什麼時候 User 會驅動它啟動? 那你就該要有對應的 Prompt。Workflow 啟動後就會在 context 不斷有資訊進出, 需要由 Agent App 主動存取的內容, 給 User / 給 Context 進行下一步的, 就是必要的 Resource, 而為了讓 Workflow 能順利進行, 盤點出所有必要的 Action, 由 Agent 主動決定何時需要發動調用, 就是你需要的 Tools.

對比 SaaS, 過去從主要的 Domain 分析出必須的 API specs, 未來的軟體服務則是從主要的 Workflow 分析出必須 MCP specs ( 包含 prompts, resources, tools ) 是所有軟體服務團隊必須面對的課題，也是未來架構師必須掌握的技能

--
其實這些 "知識"，上半年看了很多文章，都看到會背了，不過總覺得 "就是那樣" 而已，沒有什麼特別的感覺。但是自從上個月，看到這段影片，加上自己的 side project ( 我自己部落格的 MCP ) 真正按照這過程想過一輪，突然就覺得不一樣了。

按照需求來分析，設計正確的規格，一直都很重要。過去 SaaS 重視的是 Domain, Service 提供服務的型態是 API, 未來 Agent 重視的是執行 Workflow, Service 提供服務的型態是 MCP.

因此, 千萬不要把 MCP 當作是另一種技術規格的 API, 雖然會動, 但是對 Agent 來說絕對不是個理想的設計。請用 Agent 的角度思考, 用 Workflow 的需求來思考, User 才會從 Agent 那邊得到最理想的服務體驗。

對 MCP 設計有興趣的人可以想想看這些議題, 我把我參考過的相關資訊都放在留言, 歡迎討論

![](/images/facebook-posts/facebook-posts-attachment-2025-09-04-001-001.png)
