---
layout: post
title: ""
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---

太好了。下面我就依照你確認的結構，先給你 **主題一的正式文章第一版**（保留你原本觀點與語氣，但整理成正式文章；案例章節先預留）。

---

# Agent 的開發方式演進：從實驗到產品化，並建立 Agent 服務的 BizDevOps 循環

直到這個禮拜，我才真的有一種感覺：**Agent 的開發，最後一哩路終於打通了。**

我說的「最後一哩路」，指的是 **Claude Agent SDK（舊名 Claude Code SDK）** 與 **GitHub Copilot SDK** 的發布。它們讓我過去這幾個月摸索出來的做法，終於可以從 Prototype / MVP 順利延伸到正式服務，而不是停在 PoC 或 demo。

這篇文章想整理的是我這兩年來在 Agent 開發上的演進路徑，以及我現在比較穩定的一套做法：**先用通用 Coding Agent + Skills + MCP 快速驗證任務，再用 Agent SDK 整合到正式服務**。另外，我也想補上另一個我越來越在意的面向：**Agent 類型軟體開發，該怎麼建立 BizDevOps 的循環**。

我自己目前的感受是：AI 不只是讓我們寫 code 更快，它正在改變的是整個軟體服務的型態與開發方式。過去我們熟悉的是 application / UI；現在很多場景會逐步走向 agent / chat。這不只是介面換皮，而是連驗證、部署、迭代的方法都變了。

---

## 一、回顧：這兩年 Agent 開發方式怎麼一路演進過來

回顧我在 #webconf2025 的場次，我當時聊的其實就是 Agent 開發的想法：**把 MVP 流程極致落實**。只是那時候我還在摸索，很多拼圖還不完整。

如果從時間線回頭看，我大概是從 2023 年底開始，用 GPTs 做出「安得魯小舖」開始，就一路在鑽研 Agent 這題。中間我也試過很多技術路線，包含 Semantic Kernel 做 CLI 版 Shopping Agent、Google ADK / A2A（這個沒公開），一路踩坑到現在，才慢慢看清楚開發方式的演進。

### 1. 第一階段：Function Calling / MCP

當時主流做法是從 LLM API 出發，用 structure output、function calling 把整個 Agent 的行為串起來。後來 MCP 把 function calling 標準化，讓 tools 的整合速度快很多，這件事當然是大進步。

但本質上，它還是在解一樣的問題：**你要自己把 Agent 的行為與工具鏈路工程化地拼起來**。

我之前跟保哥辦過一場直播，從基礎 LLM API 的使用，一路講到 Semantic Kernel 的整合運用，再搭配 function calling 組合你的後端系統。這條路是走得通的，但我當時心裡一直有個感覺：

> 這門檻太高了，寫得出來的人沒幾個吧……

也就是說，它很適合少數能掌握整體工程複雜度的人，但不太像一條可以讓多數團隊快速上手、快速驗證需求的路。

### 2. 第二階段：A2A / Multi-Agent

接著業界開始往更高的抽象層級前進，Google 拋出 A2A（Agent-to-Agent）Protocol，開始談的不是 Agent 跟 tool 的互動，而是 Agent 跟 Agent 之間怎麼協作。

從工程視角來看，這是很自然的發展：多個 AI 各司其職，靠協定協同合作。問題是，實作時很容易走向過度設計：切出很多 Agent，但湊起來不一定真的比較會做事。

那種感覺其實很像當年微服務風潮：服務切得很漂亮，結果整體價值與交付效率不一定提升，甚至更糟。

我一樣認真嘗試過這條路，感想跟前一階段有些類似：門檻依然很高，而且很多「Multi-Agent 設計」，其實最後回頭看，**一個 Agent + 多個 Tools 就足以解決**。再加上 multi-agent 的 context 管理不容易，一旦工程技巧和治理策略跟不上，很容易變成災難。

### 3. 第三階段：Coding Agent + Skills + MCP

真正讓我轉向的，是 Claude Code 這類 Coding Agent 開始風行之後。

它本來是面向寫 code 的 Agent，但因為它的自訂能力很強（instructions、指令 prompt、自定流程），加上後來出現的 Skills，突然補上了一個關鍵缺口：**MCP 給了工具，但沒有給流程與使用知識；Skills 正好把這塊補起來**。

這個轉折一出現，我突然發現很多開發相關的流程問題都可以被很漂亮地解掉。甚至用熟之後，不只拿來寫 code，也能處理很多跟開發不直接相關的工作（例如我自己拿來整理筆記、每週工作摘要，真的很好用）。

也就是從那時候開始，我意識到：前面那幾種「從工程框架起手」的 Agent 開發方式，可能都不如 **用通用 Coding Agent 當作通用 Agent** 來得直覺、有效，而且更適合 MVP 驗證。

---

## 二、新方法：Agent 類型軟體開發的 MVP 路徑（從可行性到產品化）

最近幾個月，我在工作上剛好有需要開發「Agent 類型」的應用，就開始用這個想法去推動，並且越做越確定這條路是對的。

我的核心想法其實很簡單：

> **先驗證任務完成能力，再處理工程產品化。**

也就是說，不要一開始就手刻一整套 Agent framework、routing、orchestration、tool runtime，而是先把 Agent 當成一個可以快速驗證的能力載體，先確認它到底能不能把事情做好。

我目前的做法大致分成三個步驟。

### 1. 訪談：先搞清楚「專家」的解題流程

這是最重要的一步。

我現在越來越相信：**所有有價值的 Agent，本質上都在學習專家如何解決問題**。所以如果你連專家怎麼解題都沒搞清楚，就直接進工程實作，通常只會把不確定性放大。

我的做法是先訪談，把專家的解題流程拆開，再逐段用 ChatGPT 試試看：每一步是不是都在 AI 的能力範圍內？哪些步驟 AI 做得好？哪些步驟要靠工具補？哪些地方需要人工介入？

這一步的目標不是做出產品，而是先處理不確定性。

### 2. 原型：用 Coding Agent 把整個流程組合起來

接下來，我會用 Coding Agent（我自己習慣用 GitHub Copilot，也會用 Claude Code）把整個流程組起來。

該給的 instructions / prompt 就給，該給的 tools（CLI、MCP）就給足，該給的輸入資訊就放在 workspace 裡。讓 Agent 的輸出（例如 markdown、附檔）也都落在 workspace 下。這樣如果你用 VS Code / Cursor 之類的工具，直接就能打開看結果。

這一步最大的價值在於：**門檻大幅降低，而且你很快就能把成果拿給「專家」或「內部用戶」試用**。你拿到的是實際使用回饋，不是紙上談兵的意見。

這種 Prototype 在我看來，不只是 demo，而是可運作的驗證模型。

### 3. 大規模部署：用 Agent SDK 把已驗證流程搬進正式服務

做到這裡，你通常已經能回答一個關鍵問題：這個 Agent 真的有沒有價值、流程是否可行。

但接下來你一定會遇到現實問題：你不可能叫真正的客戶自己裝 Claude Code 或 GitHub Copilot CLI 才能用你的服務吧（笑）。

這就是我說的「最後一哩路」：你需要一種能夠自訂、能夠部署、能夠整合到既有系統的 Agent 執行方式。而 Claude Agent SDK / GitHub Copilot SDK，剛好把這個缺口補起來了。

換句話說，SDK 的角色不是讓你從零開始重造一個 Agent，而是讓你把在 Prototype 階段驗證過的流程與能力，**更平順地移植進產品服務**。

---

## 三、用「滑板車 → 腳踏車 → 機車/汽車」看 Agent 的 MVP 發展路徑

我在 #webconf2025 講 MVP 的時候，有用一張圖在說明「滑板車 → 腳踏車 → 機車 → 汽車」的發展路徑。當時我主要是在講 PO 如何用 prototype 溝通與驗證需求。

現在回頭看，這個結構其實也非常適合用來描述 Agent 應用的開發路徑。

過去沒有 AI 輔助時，理想中的 MVP 路線很美，但實務上很難玩。因為每一階段看起來像是漸進式改良，實際在工程上卻常常接近重做，團隊沒有那麼多時間與成本。

但在 AI 時代，這條路突然變得可行，而且幾乎是理所當然。

如果套到我現在的做法，大概可以這樣對應：

* **滑板車**：用 ChatGPT + prompt 驗證基本可行性
* **腳踏車**：用 Coding Agent + instructions + skills + mcp 組出可試用原型
* **機車 / 汽車**：用 Agent SDK 把已驗證設計搬進正式產品服務

這條路的重點不是「有沒有用到最新工具」，而是你能不能用更低成本、更短週期，持續驗證與收斂你的任務流程與服務邊界。

這也是我現在對 Agent 開發最大的改觀：AI 不只改變了我們寫 code 的速度，更改變了產品驗證與工程落地之間的節奏。

---

## 四、Agent SDK 是最後一哩路：從 Prototype 到可部署服務

如果用一句話總結我這幾個月的做法，就是：

> **先用通用 Coding Agent + Skills + MCP 快速驗證，再用 Agent SDK 整合到正式服務。**

這代表我放棄了過去那種從 function calling / multi-agent 開始手刻的起手式。不是因為那條路不行，而是因為對我現在要解的問題來說，這條路太早進入工程細節，會把大量時間耗在 Agent plumbing 上。

而改成這條新路之後，我最大的感想是：

> 我真的開始在「解決領域問題」了，而不是寫一堆 code 在解決 Agent 的工程問題。

我現在大概有 80% 的時間，是在評估這些事情：

* 我需要準備哪些 Skills，Agent 才能穩定完成任務？
* 我該給 Agent 哪些 Tools（MCP、scripts），它才能代替我處理外部系統整合？
* 任務的成功條件與失敗邊界是什麼？
* 哪些地方應該自動化，哪些地方應該保留人工介入？

當這些都處理完之後，SDK 的工作反而變得很清楚：把這些能力整合回既有 service，串好 UI / API，處理部署與維運問題。工程上當然還是有挑戰，但焦點已經完全不同了。

這也是我覺得 SDK 很關鍵的原因：它讓 Prototype 階段累積下來的東西，不會在產品化時全部打掉重來。

---

## 五、GitHub Copilot SDK vs Claude Agent SDK：設計哲學與應用場景

這兩套 SDK 我覺得都很值得看，而且它們的設計哲學差異很大。
如果要一句話概括，我會說：

* **Claude Agent SDK 是減法**
* **GitHub Copilot SDK 是加法**

這個差異不只是實作細節，而是會直接影響你怎麼整合、怎麼部署、怎麼維運。

### 1. Claude Agent SDK（減法）：從 CLI 抽出 Agent Core

Claude Agent SDK 的路線，比較像是從 Claude Code 的成功經驗中，把 CLI 裡處理 Agent 的核心邏輯抽取出來，變成 SDK。

你可以把它理解成：官方 CLI 其實是用自己的 SDK 包出來的一層殼。當你拿掉 CLI 外殼，直接拿到 SDK，就可以更深入地做客製化調整，配合你的應用需求。理論上，你有能力在自己的服務內重現 Claude Code 的各種能力，而且掌握度更高。

這種模式的特性是：**Agent Core 會在你的 process 內運行**。它本質上是一個 code library，所以你的應用怎麼部署，它就跟著怎麼跑。

這帶來的好處是彈性很高、可控制範圍大；相對地，也意味著你要承擔更多整合與封裝工作。

### 2. GitHub Copilot SDK（加法）：用 SDK 遙控 CLI

GitHub Copilot SDK 走的是另一條路。它不是去拆 CLI 抽核心，而是在 CLI 上加一層通訊協定，讓 SDK 能更容易地「遙控」GitHub Copilot CLI 替你做事。

也就是說，你一樣有機會在自己的服務內重現 Copilot CLI 的能力，但背後實際執行工作的，就是 CLI 本體。

這種模式的特性是：**SDK 與 Agent 執行核心先天就是分離 process**。你的 code 與 Copilot CLI 可以分開部署，天然比較接近 remote-control / service orchestration 的架構。

對某些應用來說，這會讓分散式部署與維運切分變得更自然。

---

### 3. 架構差異帶來的部署差異（實務上真的有感）

這兩者最大的差異，我覺得不是 API 長相，而是運行模型：

* Claude：偏 in-process library
* Copilot：偏 out-of-process remote control（CLI server mode）

以 GitHub Copilot CLI 來說，它內建 server mode（例如 `--headless --port 1234`），這對想偷懶的我來說是大加分。因為這代表它從一開始就有一種「可被服務化」的形狀，你可以比較自然地把它當成一個獨立可部署元件來管理。

### 4. 為什麼在我的情境下，Copilot SDK 特別順手

我自己的主力語言是 .NET，這件事會明顯影響選型。

對我來說，GitHub Copilot SDK 的路線有幾個實務優勢：

1. **.NET 整合比較順**
   Claude SDK 原生偏 Node / Python；如果我要在 .NET 生態使用，通常得再封裝一層 API server。Copilot 這種 CLI + 通訊協定的做法，等於先天就幫我把這層抽象準備好了。

2. **Prototype 與 Production 環境一致性高**
   我想要的是「無腦搬移」：Prototype 跟 Production 都跑同一套 CLI，差別只是我直接操作還是透過 SDK。這種一致性很有價值，因為它降低了遷移時的變數。

3. **跨語言支援比較容易擴展**
   因為架構上是 remote control，支援多種語言通常比較直覺。我慣用的 .NET 在這種模式下省了不少麻煩。

4. **部署與更新策略更單純**
   我可以直接把 CLI 封裝進 container。由於沒有自己多包一層客製 runtime，部署與更新流程就更單純，也比較容易跟主服務版本解耦。

### 5. 補充：兩者其實不是互斥，而是適用情境不同

雖然我目前在自己的情境下比較偏 Copilot SDK，但我不會把它講成唯一答案。

如果你的需求是要深度客製 Agent 組態、掌握 Agent core 的 lifecycle、把能力深度嵌入應用內部流程，而且團隊主力本來就在 Node / Python 生態，那 Claude Agent SDK 很可能更對味。

相對地，如果你要的是快速把 CLI 驗證過的流程搬進服務、重視 Prototype / Production 的一致性、偏好多語言整合與獨立部署的運行模型，那 Copilot SDK 會很順手。

重點不是選哪一套，而是你要先搞清楚：**你要解的是什麼型態的產品化問題**。

---

## 六、Agent 類型軟體開發，怎麼建立 BizDevOps 循環

這是我最近越想越覺得重要的部分。

如果是傳統 application / UI 型產品，我們對 Biz、Dev、Ops 的分工與循環其實已經有一套很成熟的心智模型：需求定義、功能開發、上線、監控、優化、迭代。

但 Agent 類型的服務不太一樣。它的品質不只是在看「功能有沒有做完」，而是還要看：

* 任務成功率高不高？
* 失敗時的體驗可不可接受？
* 成本（token / tools / 執行時間）能不能承受？
* 使用者是否信任結果？
* 什麼情況應該人工接手？

這些問題讓 Biz、Dev、Ops 不再只是接力，而是變得更像一個高度耦合的循環。

### 1. Biz：商業與產品在 Agent 服務中的角色，變得更像「任務定義者」

在 Agent 服務裡，Biz（或產品）不只是定義畫面與流程，而是要先回答一些更根本的問題：

* 這個 Agent 到底要完成什麼任務？
* 什麼叫做「完成得夠好」？
* 哪些錯誤可以接受，哪些不行？
* 失敗成本有多高？
* 何時要切換到人工處理？

也就是說，產品需求不再只是 UI spec，而是任務完成標準與風險邊界的定義。

### 2. Dev：開發工作的重心，從功能實作轉向能力設計與整合

在這種模式下，Dev 的重心也會移動。除了傳統的程式開發外，還要處理更多 Agent 特有的工作：

* 專家流程訪談與能力拆解
* Skills / MCP / prompts / guardrails 設計
* Prototype 與正式服務之間的能力搬運
* SDK 整合、權限、系統串接、版本管理
* 部署架構與運行邊界設計

也就是說，開發對象從「功能模組」逐漸轉成「任務完成系統」。

### 3. Ops：營運與維運工作的重點，從系統穩定擴展到行為品質治理

Agent 服務的 Ops，除了基礎的服務穩定性之外，還要多看一層「行為品質」：

* 任務成功率 / 失敗型態
* 人工接手率
* 成本與耗時
* tools 調用失敗與外部系統整合錯誤
* 不同類型輸入造成的品質差異

這些觀測資料不是只有拿來報表，而是會直接回頭影響 Skills、prompts、tools 配置，甚至產品邊界設計。

### 4. Agent 版 BizDevOps 循環（我目前的理解）

如果用文字描述，我目前認為比較合理的 Agent 服務循環會像這樣：

**商業目標 / 使用場景定義 → 專家流程拆解 → Prototype 驗證 → SDK 整合部署 → 真實使用觀測 → 失敗案例分析 → 調整 Skills / Tools / 流程 → 再部署**

這裡最關鍵的差異在於：
Agent 服務的迭代核心，不只是改 UI 或修 bug，而是持續調整 **任務流程、能力配置、人機分工邊界**。

這也正是我認為 application / UI 與 agent / chat 兩種服務型態最大的差異之一。

---

## 七、（預留）實際案例：用 SDK 開發 Agent 應用的方式與心得

這一段我先保留，之後會補上我實際用 SDK 開發 Agent 應用的案例。
我希望到時候能整理成比較完整的 PoC / demo，包含：

* 問題背景與成功標準
* Prototype 階段（Coding Agent + Skills + MCP）的做法
* SDK 產品化整合方式（Copilot / Claude 的取捨）
* 部署與維運策略
* 實戰中的踩坑與修正方式

等我整理好，再補回這篇或拆成系列文下一篇分享。

---

## 八、結論：Agent / Chat 不是 UI 替換，而是新一代軟體服務模式

回頭看我這兩年的嘗試，從 GPTs、Function Calling / MCP、A2A / Multi-Agent，到現在的 Coding Agent + Skills + MCP + SDK，我最大的感想是：

**AI 不只是加速了寫 code，而是開始重寫軟體服務的開發流程。**

對我來說，真正的改變不只是效率提升，而是：

* 驗證方式變了（先驗證任務完成能力）
* 產品化路徑變了（Prototype → SDK 整合）
* 維運重點變了（從功能穩定到行為品質治理）
* 團隊協作方式也變了（Biz / Dev / Ops 更早、更緊密地共同定義任務與邊界）

如果你對 Agent 開發有興趣，我會給一個很務實的建議：
**先不要急著糾結框架或 Multi-Agent 架構，先從你的任務、專家流程與 MVP 驗證開始。** 把 SDK 放在產品化階段使用，通常會順很多。

背後想法上，我很推薦 Anthropic 那場演講：

**Don’t Build Agents, Build Skills Instead – Barry Zhang & Mahesh Murag, Anthropic**

如果懶得看影片，iHower 的龍蝦整理也很值得看（逐字稿、摘要、翻譯、重點都很完整）。

這個領域現在討論與分享其實還不算多，我自己也還在持續整理方法與案例。等我把實戰 PoC 整理好，再貼上來跟大家交流。歡迎一起分享心得。
