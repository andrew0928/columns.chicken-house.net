---
layout: synthesis
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用 - summary"
synthesis_type: summary
source_post: /2025/06/22/inside-semantic-kernel/
redirect_from:
  - /2025/06/22/inside-semantic-kernel/summary/
---

# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 摘要提示
- Chat Completion API: 以 OpenAI Chat Completion 為統一範例，說明 LLM 對話的最小可行模型與訊息結構。
- 結構化輸出: 善用 JSON Mode/Schema，讓 LLM 與程式以強型別資料對接，提升可靠度與可維護性。
- Function Calling 基礎: 將自然語意「編譯」為可執行指令與參數，奠定 Agent 能力的核心機制。
- Function Calling 連續調用: 以工具呼叫與回傳結果的多輪迭代，完成有順序依賴的工作流程。
- RAG 與工具鏈結: 用 Function Calling 觸發檢索與合成流程，使 LLM能「知道自己不知道並主動搜尋」。
- Microsoft Kernel Memory: 以「RAG as a Service」形式提供長期記憶管理、文件管線與大規模擴展能力。
- SK + MSKM 整合: SK 負責推理與外掛工具、MSKM負責長記憶與檢索，形成 .NET 生態的成熟組合。
- 進階 RAG 策略: 引入摘要、FAQ、解決方案等「為檢索而生」的合成內容，大幅提升召回與精準度。
- MCP/多實作管道: 透過 GPTs/Dify/MCP/SK 多種宿主與協定暴露工具規格，統一讓 LLM可調用企業資源。
- 土炮 Function Calling: 即使模型不支援工具呼叫，也能以訊息協議與規則化前綴模擬出等效流程。

## 全文重點
本文整理一系列直播與日更貼文，從最基本的 Chat Completion API 出發，逐步建立 AI 應用設計的「工程視角」。作者強調，LLM 的強大不在 API 本身而在設計模式：如何以結構化輸出讓 LLM 與程式碼協作、如何以 Function Calling 把語意轉成可執行的指令與連續流程、以及如何以 RAG 讓模型能「引用外部真值」來回答。文中以 OpenAI 規格作為示範，並平行展示 HttpClient、OpenAI .NET SDK 與 Microsoft Semantic Kernel（SK）的寫法，指出 SDK 相依帶來的便利與取捨。

RAG 部分先拆為「流程」與「觸發」兩個面向：流程包含問題收斂、檢索、整合生成；觸發則可透過 Function Calling 與工具描述（含 JSON Schema 參數）自動完成。進一步，作者引介 Microsoft Kernel Memory（MSKM）作為開源長期記憶/RAG 服務：它以獨立服務＋SDK交付，處理內容抽取、分段、向量化與儲存等完整文件管線；同時與 SK 天然對齊，既能掛為 SK 的 Memory Plugin，亦沿用 SK 的各種 AI 連接器。這讓 .NET 團隊可同時擁有推理、工具編排與高彈性的長記憶檢索能力。

在進階 RAG 策略上，作者以自身部落格的長文為例指出「僅靠分段與相似度」的天花板：使用者問題的視角常與原文寫作視角不對齊，導致檢索錯配。解法是「為檢索生成內容」：在管線中加入摘要（全篇與段落）、FAQ（Q/A）、解決方案（Problem/Root Cause/Resolution/Example）等多視角資訊，並恰當加標籤、向量化。這些資料在「生成一次、查詢多次」的成本結構下可用更強模型處理，顯著改善召回與最終答案品質。

整合層面，作者示範多種 Function Calling 宿主：ChatGPT GPTs＋Custom Actions（OpenAPI+OAuth）、No-Code 平台 Dify Custom Tools（OpenAPI）、Claude Desktop/Model Context Protocol（MCP）Server、以及 SK 原生插件。它們本質皆提供「工具規格暴露＋統一代執行回傳」兩件事，只是通訊方式不同。文末亦點出即使模型不原生支援 Function Calling，只要以訊息角色與規則化前綴（如「請執行指令」）也能「土炮」出近似流程，但正式生產仍建議使用標準機制與框架。

最後的問卷統計顯示，學員收穫集中於基礎原理梳理、Function Calling/RAG 實作細節、以及 SK/MSKM 的整合方法。多數建議希望看更多 MCP、商業情境與企業級落地案例。整體而言，本文將「AI 作為工程元件」的觀念落地為可複用的設計模式與工具鏈，對 .NET 開發者建立 LLM/RAG 的系統性能力極具參考價值。

## 段落重點
### 相關資源與連結
彙整直播與文章的外部資源：Facebook 專頁、YouTube 錄影、回饋問卷、GitHub 範例與 .NET Conf 2024 簡報。讀者可按主題回看影片與程式碼，並在社群互動中取得補充討論。作者採「先釋出片段、後整合成文」的方式，因應 AI 生態快速演進，讓內容更即時。

### Day 0, Chat Completion API
以 OpenAI Chat Completion 作為基準，說明對話訊息結構（system/user/assistant）、模型與參數（如 temperature）、可選 tools 與 response_format 等要點。對話每輪皆需帶上完整歷史，模型產生下一段回覆；若要仿 ChatGPT 對話，只需重複此迭代。作者提供 HttpClient、OpenAI SDK 與 SK 版本的「Simple Chat」示例，強調理解基礎協議是後續所有能力（JSON Mode、Function Calling、RAG）的起點。

### Day 1, Structured Output
針對「開發者如何善用 LLM」提出三個工程化要點：以 JSON（最好有 JSON Schema）輸出並直接反序列化為型別；在輸出中明確標示成功/失敗狀態以降低不確定性；堅持單一職責，將搜尋、計算、格式轉換等交回程式碼處理，LLM 只做不可替代的推理。作者以「從對話抽取地址」為例，展示 JSON Mode 的必要性及 SDK 間差異：用 SK 時可用 C# 型別抽象 JSON Schema，顯著降低負擔。

### Day 2, Function Calling（Basic）
Function Calling 讓 LLM 在對話中自行決定何時呼叫工具或直接回答，開啟 Agent 的基礎。以「管理購物清單」為例，LLM 根據使用者語意產出 add/delete 指令與參數，等同把自然語言編譯成可執行的指令序列。作者強調理解原理重於框架封裝：當場景跨前後端或需高階規劃，手寫 Prompt/協議更有彈性。此篇先講「Call」，將「Return 與連續依賴」留待下一篇。

### Day 3, Function Calling（Case Study）
以「幫我排明早 30 分鐘慢跑」為例，完整展開多輪工具調用：AI 先要求 check_schedule，根據回傳時段再呼叫 add_event，最終以自然語言回覆用戶。逐條列示對話歷程中的 system/user/assistant/tool/tool-result 角色與時序，說明每次呼叫都帶完整歷史。作者指出此流程即「結構化輸出＋工具呼叫」的組合，實務上宜用 SK、No-code 平台（n8n/dify）或支援 MCP 的客戶端以簡化實作。

### Day 4, RAG with Function Calling
RAG 的本質是「用外部檢索結果來生成答案」，基本流程為問題收斂、檢索、整合生成。作者將「觸發」視為 Function Calling 的應用：透過 system prompt 與工具定義，LLM 會自行決定先檢索再作答，並用 JSON 參數化查詢條件。示範以 Bing Search 作為插件，搭配其他工具（定位、天氣）讓 LLM 規劃多步操作，近似「Search GPT」。奠定之後以 MSKM 取代通用搜尋，接入自家知識庫的可能。

### Day 5, MSKM: RAG as a Service
介紹 Microsoft Kernel Memory（MSKM）：與 Semantic Kernel 出自同團隊，提供長期記憶與文件處理的獨立服務與 SDK，既可 Web Service 也可內嵌應用。MSKM 聚焦文件管線（抽取、分段、貼標、向量化、儲存、檢索），彌補 SK Memory 只抽象向量庫的不足。兩大整合亮點：MSKM 內建 SK Memory Plugin，讓 LLM 直接操作記憶；MSKM 本身沿用 SK 的連接器，支援多家 LLM/Embedding 服務。此組合被定位為 .NET 領域搭建企業級 RAG 的成熟解。

### Day 6, 進階 RAG 應用：生成檢索專用資訊
面對長文與多視角查詢，單靠分段與相似度常失準。作者以個人長文實測，提出「先合成、再檢索」策略：在匯入前以強模型生成多視角資訊（全篇摘要、段落摘要、FAQ 問答、解決方案四件組），加上標籤後一併向量化。此舉對齊使用者問題視角，大幅改善召回。因屬一次性離線處理，可承受較高模型成本。實戰流程可用 SK 先合成、MSKM 檢索，最終由前端 Agent/RAG Chat 組合答案。

### Day 7, MSKM 與其他系統的整合應用
盤點四種 Function Calling 宿主與管道：ChatGPT GPTs＋Custom Action、No-code Dify Custom Tools、Claude Desktop＋MCP Server、以及 SK 原生插件。它們共同提供「工具規格暴露＋代執行回傳」兩件事，差別在通訊協定（如 OpenAPI/Swagger、MCP stdio/SSE）。作者以 C# MCP Server 實作串接 Claude Desktop 與 MSKM，展示本機 RAG；同時分享對 MSKM 新版中文 chunking 與 MCP SDK 中文序列化的實測注意事項與 Issue 回報。

### Day 8, 土炮 Function Calling
回答「DeepSeek R1 不支援工具呼叫如何實現？」：只要模型推理力足夠，即可用訊息協議「土炮」出等效流程。作法：以 system prompt 制定對話規範與前綴（如「請執行指令」給工具、「安德魯大人您好」給使用者），由應用程式攔截工具指令並執行，再把結果接續加入對話。此法說明 Function Calling 的本質是三要素：工具規格、三方對話、參數生成。雖可行但正式環境仍建議用原生 Function Calling 與 SK 框架。

### 問券回饋（統計至 2025/06/22）
回收 93 份回饋。多數認為最大收穫在於：基礎原理梳理（LLM 運作、JSON/Function Calling）、RAG 與 MSKM 的實作細節、以及 SK 的工程化應用。許多建議希望更深入 MCP、企業級案例、向量細節與實務流程，也期待更多工作坊與商務情境示範。整體評分高，印證「從底層協議到框架整合」的教學路徑能有效幫助開發者把 LLM 視為工程元件，落地至可維護、可擴展、可觀測的 AI 應用。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本 LLM 概念與 Chat Completion 通訊模型（system/user/assistant 訊息、context window、temperature）
- REST/HTTP、JSON 與 JSON Schema（序列化/反序列化）
- C#/.NET 基礎與 HttpClient、OpenAI .NET SDK 使用
- 向量化與相似度檢索概念（embeddings、向量資料庫）
- 容器與部署基礎（Docker、環境變數、API 金鑰管理）

2. 核心概念：本文的 3-5 個核心概念及其關係
- Structured Output（JSON/JSON Schema）：讓 LLM 輸出機器可讀的結構化資料，是程式與 LLM 資料交換的基礎
- Function Calling（Tool Use）：讓 LLM 規劃並呼叫外部工具，形成多步驟任務的「呼叫—回傳—續步驟」迭代
- RAG（檢索增強生成）：以檢索內容強化回答，用於最新、私有與長期知識；與 Function Calling 結合形成可控的檢索—生成流程
- Semantic Kernel（SK）：.NET 智能中介框架，簡化 JSON 模式、工具定義、插件整合；可掛接 MSKM 當記憶/檢索工具
- Microsoft Kernel Memory（MSKM）：RAG as a Service；負責長期記憶、文件導入（pipeline/handlers）、嵌入與查詢；與 SK 深度整合
關係：Structured Output 與 Function Calling 是對 LLM 的「IO與控制面」，RAG 提供知識來源，MSKM提供RAG基礎設施，SK 負責在應用程式中銜接 LLM、工具與 MSKM。

3. 技術依賴：相關技術之間的依賴關係
- LLM 供應者（OpenAI/Azure OpenAI/本地模型）→ Chat Completion、JSON Mode、Tool Use
- Embedding 模型（如 text-embedding-3-large）→ 產生向量 → 向量資料庫/索引（由 MSKM 抽象/管理）
- MSKM（服務/SDK/Docker）→ 文件管線（抽取/分段/向量化/儲存/查詢）→ SK Memory Plugin（讓 LLM 調用）
- SK（Kernel + Plugins）→ 對接 LLM、定義工具（含 Swagger/MCP/Native）、掛接 MSKM、Bing Search 等外掛
- 外部整合：Bing Search、GPTs Custom Actions（OpenAPI）、No-code（Dify Tools）、MCP（Claude Desktop 等）

4. 應用場景：適用於哪些實際場景？
- 企業知識庫/產品文件的問答與助理（內外部文件、FAQ、解決方案手冊）
- 排程/行事曆助理（多步驟 Function Calling：查空檔→新增事件→回覆）
- 搜尋強化助理（Search GPT 類體驗：地點/天氣/搜尋引擎/私有知識整合）
- 技術部落格/長文檢索（摘要、FAQ、問題-原因-解法等多視角索引）
- 多客戶端整合（GPTs、Dify、Claude Desktop via MCP）以相同工具集驅動多入口

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 Chat Completion 基本模式；用 HttpClient 呼叫一次完整請求/回應
- 嘗試 OpenAI .NET SDK 與 SK 撰寫「簡單對話」與「JSON Mode（結構化輸出）」並反序列化為 C# 型別
- 練習基本 Function Calling（單步）：將自然語言轉為指令 JSON，程式端實作對應動作

2. 進階者路徑：已有基礎如何深化？
- 多步驟 Function Calling：引入工具回傳（tool-result）並以歷史上下文推進決策
- 建立基本 RAG 流程：以 MSKM Docker 起服務→匯入文件→查詢→整合至 SK 插件
- 擴充導入管線：嘗試摘要（summarization）、FAQ、問題/原因/解法等多視角合成以改善檢索
- 與外部工具整合：Bing Search、Swagger 注入至 SK，或以 GPTs/Dify 註冊工具

3. 實戰路徑：如何應用到實際專案？
- 架設 MSKM（Docker/雲端）並規劃資料域、標籤策略、存取權限與API金鑰管理
- 設計內容生成管線：摘要、段落摘要、FAQ、案例（Problem/Root Cause/Resolution/Example）
- 在 SK 中掛載 MSKM 與其他工具，設計系統提示/策略（只回答來源內容、必附引用）
- 規劃多入口策略：GPTs Actions、Dify Tools、MCP Server（C# SDK）讓不同端共享同一工具集
- 監控與成本優化：模型選型（推理/嵌入）、Tokens/延遲/失敗重試、觀測日誌與評測迴路

### 關鍵要點清單
- Chat Completion 基本模型: 理解 system/user/assistant 與完整對話歷史回傳機制，是一切應用的基礎 (優先級: 高)
- Structured Output（JSON Mode）: 以 JSON Schema 約束輸出，直接反序列化為強型別，讓非AI程式碼無縫接手 (優先級: 高)
- 失敗顯式標示: 在結構化輸出中加入成功/失敗旗標，避免以字串解析判錯 (優先級: 中)
- Function Calling 基本型: 在對話前宣告可用工具與參數，讓 LLM 決定要輸出文字或呼叫工具 (優先級: 高)
- 多步驟工具回圈: 處理 tool/tool-result 與順序相依（先查再寫），直到完成任務 (優先級: 高)
- RAG 基本流程: 問題收斂→檢索→以檢索內容生成回答並附引用，避免幻覺 (優先級: 高)
- RAG 觸發與工具化: 以 Function Calling 方式觸發檢索，LLM 自動組裝查詢參數 (優先級: 高)
- MSKM 作為 RAG 服務: 文件管線（抽取/分段/嵌入/儲存/查詢）與 SDK/HTTP 介面，易於擴充與部署 (優先級: 高)
- SK 與 MSKM 整合: 以 SK Memory Plugin 讓 LLM 可「直接使用」MSKM 功能，並重用 SK 連接器 (優先級: 高)
- 內容合成強化檢索: 先離線生成摘要、段落摘要、FAQ、問題-原因-解法等多視角資料再向量化 (優先級: 高)
- Chunking 與嵌入選型: 根據模型最佳 token 長度與語言特性調整切片策略與重疊 (優先級: 中)
- 工具生態整合: 以 Swagger（OpenAPI）供 ChatGPT/Dify/SK 使用，或以 MCP 提供跨客戶端的工具存取 (優先級: 中)
- 成本與效能治理: 推理模型/嵌入模型分工、批次導入、快取與監控，避免把可程式化工作丟給 LLM (優先級: 中)
- 安全與來源控制: 僅以檢索到的內容回答並附來源，設定權限域與標籤（tags）過濾 (優先級: 中)
- 土炮 Function Calling 原理: 即使模型不支援工具介面，也可用訊息協議與應用層攔截實作概念驗證 (優先級: 低)