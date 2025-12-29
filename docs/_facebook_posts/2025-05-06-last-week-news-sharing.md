---
date: 2025-05-06
datetime: 2025-05-06T02:33:42+08:00
timestamp_utc: 1746470022
title: "再來 PO 一則上週的舊聞..."
---

再來 PO 一則上週的舊聞... 

Anthropic 發布 Claude 開放 Custom Integrations 了，這是啥? 簡單的說就是 Claude Web 版本, 也能支援 Remote MCP Server 了。

對大部分的 developer 來說, 這沒啥特別的, 就是 claude desktop 的功能也開放到 web 版而已, 不過我覺得這對 MCP 的應用來說, 跨出這一步，等於是面對非 developer 族群，以及非 desktop 終端設備的敲門磚。因為 web 版可以支援, 也代表 mobile app 也能支援了, 整個生態系開始有機會發展起來。

回顧一年多前我寫的這篇文章:

"[架構師觀點] 開發人員該如何看待 AI 帶來的改變?"

當時我預測過這樣的發展，沒想到 AI 世代進步的速度太快了，一年多就足夠回來 review "上個世代" 的 PO 文... 當時我是這麼預測的:

--
3-4, 整合三者的應用模式

應用程式只要用 Semantic Kernel 開發, 甚至變成 OS 內建的服務，安裝軟體會變成安裝 Plugins / Planner, 而 AI OS / AI PC 則提供了足夠的 LLM 運算能力，讓你的 Application 能充分使用這些 AI 資源；最後 Copilot 變成作業系統的標準 (主要) 操作介面，統合起本地端與雲端的各種資源…
--

當時想像的是, 如果 AI PC, AI phone 變成主流 ( X, 當時我看好的 Copilot+ PC, 現在連個影子都沒有... ), 當設備本身都有足夠的運算能力的時候, LLM + Agent ( Copilot ) 會變成主要的介面, 而到時的應用程式, 就是 Agent 的 Plugins ..

換成通用一點的名詞來講, 就是各位的手機 / 電腦, 打開就是一個 Agent ( 類似 ChatGPT ) 的介面, 而各式各樣的應用軟體, 就是這個 Agent 的 Tools.. 沒錯, 現在最接近這概念的標準, 就是 Claude + MCP ..

不過，目前的 MCP 發展離我想像的還差一大步 (技術已經跟上了，但是生態系還沒)。我想像的 Agent, 應該是內建在 OS 的角色, 地位就像 Siri 那樣, 有足夠語言與推理能力的 LLM, 並且能夠安全的使用我個人的資訊。

為了 PoC, 好好體驗這應用能做出什麼變化，其實我寫過這麼一個展示用的 MCP server, 它只做一件事, 就是專門出賣我的個資 (咦?)。當然這太危險了，所以我只是做個空殼子，永遠都是傳回固定的罐頭訊息，沒有真正傻傻的撈我的個資給 AI。

我提供了這些 tools:

- GetCurrentUTCDateTime
- GetMyProfiles
- GetMyName
- GetMyLocation
- GetMyBirthday

對，全部都是在出賣我的個人資訊，包含設備上的時區，時間，我的個人喜好，姓名，所在地區 (GPS)，我的生日 (年紀)... 等等，然後掛上 Claude Desktop.

同時 Claude 上我也起用了這幾個 Integrations:

- Web Search
- Google Drive
- Gmail Search
- Calendar Search

這些通通都整合在一起, 能做什麼事? 試試看在 Claude Desktop 問 AI 這些問題...

---
你知道我的個人相關資訊嗎?
---

不意外的, 透過 MCP 我的基本資訊就被摸透了 (結果請看圖一)。
我繼續問:

---
幫我找找網路上有無我相關訊息
---

果然很精準地把我在網路上的資訊都搜了出來... (請看圖二)
接著再問一個問題:

---
找找我所在地區的重點新聞給我參考
---

果然，再次很精準地把台北地方的新聞頭條都找出來了... (請看圖三)

想像一下, 如果 Siri 聰明一點, Apple Intelligence 爭氣一點 (或是 Copilot 也爭氣一點)，這些場景早就實現了。全手機上的 APP, 跟網路上的所有服務都能這樣被使用... 這就是我當時想像, 未來必然會有某家大廠 (當時我猜的是: Microsoft / Google / Apple), 而 AI 大廠 ( OpenAI / Ahthropic 等 ) 也有機會，但是它們缺了個資跟終端設備, 應該會居於劣勢... 結果反而現在是 Anthropic 跑最快, 憑藉著 LLM 的能力 + MCP 標準的制定, 目前是最接近我想像的未來樣貌...

為何要都這麼遠來介紹 Claude Integrations 呢? 如果你是使用者, 可以開始謹慎的開放這些 Integrations ( 其實就是官方內建的 remote mcp servers ) 了。小心謹慎的使用, 你會發現你使用網路的體驗完全不同了。

如果你是開發者, 那更有意思了。這真正開始驗證了我那篇文章，提到的: 

---
4-2, API 的設計必須精準合理:

架構師必須清楚，API 該如何對應領域的問題，用統一並解精準的設計開放服務介面，掛上 LLM 的擴充機制
---

以後你開發的網路服務，請認真思考如何成為 AI 的 tools, 包含你的 API，包含你的 UI 設計，都應該開始認真考慮如何跟 Agent 搭配。MCP 的規範是一個很好的起點，以前你要遵循 Open API spec, 現在你該認真考慮是不是要遵循 MCP spec 了。

個人化的認證機制也是，你該開始認真考慮全面遵循 OAuth2 的規範了，因為，MCP spec ( 2025/03/26 更新 ) 也正式把 OAuth2 當作 MCP 內建的使用者端認證機制了...

覺得世界變太快了嗎? 你要習慣，這就是這個時代的變化速度...
準備好迎接這改變吧~

--
PO 文內提到我去年寫的文章, 連結請見第一則留言

![](/images/facebook-posts/facebook-posts-attachment-2025-05-06-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-05-06-001-002.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-05-06-001-003.png)
