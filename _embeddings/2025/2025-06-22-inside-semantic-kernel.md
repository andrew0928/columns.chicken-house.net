---
- source_file: /docs/_posts/2025/2025-06-22-inside-semantic-kernel.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
## 1. Metadata  
```yaml
layout: post
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"
categories: ["系列文章: 架構師觀點"]
tags: ["架構師觀點", "技術隨筆"]
published: 2025-06-22
logo: /wp-content/images/2025-06-22-inside-semantic-kernel/livecast-logo.png

primary-keywords: ["Microsoft Kernel Memory", "Semantic Kernel", "RAG", "Function Calling", ".NET"]
secondary-keywords: ["LLM", "Chat Completion API", "JSON Mode", "Vector Store", "MCP", "Bing Search"]
tech_stack:
  languages: [C#]
  frameworks: [".NET 8", "Microsoft Semantic Kernel", "Microsoft Kernel Memory"]
  platforms: ["OpenAI", "Azure OpenAI", "Docker"]
  tools: ["HttpClient", "OpenAI .NET SDK", "Visual Studio", "CLAUDE Desktop"]
  concepts: ["Retrieval Augmented Generation", "Function Calling", "Agent Pattern", "向量資料庫"]
references:
  external_links:
    - https://www.youtube.com/watch?v=q9J1YzhW6yc
    - https://github.com/andrew0928/AndrewDemo.DevAIAPPs
  internal_links: []
  mentioned_people: ["Andrew Wu", "保哥"]
  mentioned_tools: ["ChatGPT", "Bing Search", "Claude Desktop"]
content_metrics:
  word_count: "≈12000"
  reading_time: "≈30 min"
  difficulty_level: "Intermediate-Advanced"
  content_type: "Live Demo + Technical Guide"
```

## 2. 全文重點（≈1000 字）  
本文以八天分段直播內容為主軸，逐步說明如何在 .NET 生態系中利用 Microsoft Semantic Kernel（SK）與 Microsoft Kernel Memory（MSKM）打造高品質 RAG（Retrieval Augmented Generation）應用。首先從最核心的 Chat Completion API 切入，闡述 LLM 僅需單一端點即可完成各類對話任務。接著介紹 JSON Mode 與 Function Calling，示範如何讓 LLM 以結構化輸出回傳資料或主動產生函式呼叫，奠定 AI 與程式碼協作的基礎。進一步以購物清單與行事曆範例，展示多輪、帶結果回傳的 Function Calling 流程，說明「工具調用 → 執行 → 回填」的往返模式。  
在此基礎上，文章進入 RAG 領域：先說明「問題收斂 → 向量檢索 → 依據依存範本生成答案」三步驟，並以 SK Plugins ＋ Bing Search 實作 Search-GPT 式查詢體驗。之後聚焦 MSKM，解析其「Pipeline → Handlers → Vector Stores」設計，強調可獨立部署為 Web Service，也能內嵌於 .NET 程式。作者以自身部落格資料為實例，示範大型文章長度、切片策略與摘要生成對 RAG 精準度的影響，證明預先產出 Abstract、FAQ、Problem/Solution 等多視角內容，可顯著提升檢索涵蓋率。  
後段延伸至 MCP（Model Context Protocol）生態，示範把 MSKM 打包成 MCPServer，並透過 Claude Desktop 完成端對端 RAG 查詢，佐以土炮範例說明即使模型原生不支援 Function Calling，仍可藉「角色前置詞＋程式攔截」實現同等效果。最後作者公開問卷統計，回收社群對各主題的反饋，印證 LLM 應用已從概念驗證走向工具鏈整合與工程化最佳實務。整篇文章提供完整範例程式、影片與投影片，讓開發者能即學即用，並對未來進階課程提出方向建議。

## 3. 段落重點  

### 2-1 相關資源與連結  
作者列出直播影片、Facebook 貼文、Google 表單、簡報與 GitHub 範例程式等外部資源，方便讀者在閱讀文章時快速跳轉到原始材料或範例碼。此段凸顯「邊直播邊釋出片段，再回收整理成文」的新寫作流程，以因應 AI 領域日新月異的資訊汰換速度，並透過持續收集社群 feedback 迭代內容。

### 2-2 Day 0：Chat Completion API  
首先介紹 LLM 最基本的 Chat Completion 呼叫模式，從 HttpClient → OpenAI .NET SDK → Semantic Kernel 三種寫法展示同一簡單對話過程。重點在於 messages、model 參數、temperature 與 tools / response_format 的結構；以及如何在多輪對話中持續傳遞上下文。作者強調理解這個「單一 API 解萬用需求」的本質，才能進入後續設計模式思考。

### 2-3 Day 1：Structured Output（JSON Mode）  
說明 LLM 支援 JSON Schema 後對開發者的重要性：統一輸出格式、成功／失敗旗標、單一職責分工、程式端能直接 deserialize 為 C# 物件。以茶店地址抽取為案例，對比「讓 LLM 一次包辦所有雜事」與「LLM 專注抽取，後續交由傳統 API」的成本差異，突顯結構化輸出的工程效益。

### 2-4 Day 2：Function Calling（Basic）  
定義 action = add/delete 的購物清單，示範在 system prompt 宣告可用函式與參數，LLM 依 user 意圖自動生成 JSON 指令集。重點在「自然語言 → 指令序列」的自動轉譯能力，及其對 Agent 場景的啟發。作者提醒開發者理解原理，以便在框架不支援或場景複雜時手動編寫 Prompt。

### 2-5 Day 3：Function Calling（Case Study）  
延伸到多步驟、帶結果回填的行事曆範例：check_schedule → add_event → assistant 總結。詳細拆解 tool / tool-result message 如何插入歷史紀錄，使 LLM 持續取得最新世界狀態。並比較 Http 土炮、SDK、SK 的便利性，引導讀者選擇合適抽象層來管理複雜對談。

### 2-6 Day 4：RAG with Function Calling  
定義搜尋工具為 Plugin，透過 Function Calling 自動觸發「檢索 → 回答」流程，說明 RAG 的三大步驟與 Json Mode 在產生查詢參數時的角色。以 Bing Search ＋ SK 打造 Search-GPT，示範 LLM 在不知道答案時可自行決定外部查找，回應精準且附來源網址。

### 2-7 Day 5：MSKM ‑ RAG as a Service  
介紹 Microsoft Kernel Memory 架構：可 dockerize 為服務，也能 serverless 內嵌；Pipeline 切分 TextExtraction → Chunking → Embedding → Storage；內建 SK Memory Plugin 與多家 AI Connector。作者強調 MSKM 聚焦「長期記憶」治理，與 SK 的「短期對話」互補，是 .NET 世界最完整的 RAG 組合。

### 2-8 Day 6：進階 RAG 應用—生成檢索專用資訊  
分享作者將 330 篇、每篇 50k+ 字文章導入 MSKM 的實務：若僅以固定長度 Chunk 檢索，長文資訊密度失衡；改以 LLM 先產製 Abstract、Paragraph-Abstract、FAQ、Problem/Solution 等多視角內容，再行向量化可大幅提升召回率與精準度。此段凸顯「內容前處理」才是 RAG 成敗關鍵。

### 2-9 Day 7：MSKM 與其他系統整合  
解析 MCP (USB-C for AI) 協定如何列舉 tools/list 與 tools/invoke；示範把 MSKM 封裝成 MCPServer，Claude Desktop 透過 stdio/SSE 連線即可呼叫自建知識庫。並分享當前 MSKM docker 及 MCP SDK 中文編碼 bug 的臨時解法，提醒讀者留意版本相依問題。

### 2-10 Day 8：土炮 Function Calling  
證明即使模型不原生支援 Function Calling，也能靠「角色前置詞 + 程式攔截」土炮實現。作者用「安德魯大人您好 / 請執行指令」區分 assistant 與 tool，並在應用層解析執行，說明三核心要件：宣告工具、三方對話、產生參數。鼓勵開發者理解低階機制以備不時之需。

### 2-11 問卷回饋  
統計 93 份問券，收斂社群對「RAG 進階處理、Function Calling、MSKM」等主題需求最大，並彙整「後續想看 MCP、Agent Group、實際商務流程」等建議。整體評分多集中 4-5 星，顯示內容深度與實務價值獲得肯定。

## 4. 問答集  
- **Q1. 為何僅靠 Chat Completion API 就能開發各式 AI 應用？**  
  **A:** Chat Completion 具備一組 messages array，可承載任何上下文；再透過 system prompt、工具宣告等擴充欄位，就能動態調整模型行為。換言之，API 本身保持極簡，複雜度被轉移到 prompt 與對話結構設計，讓開發者能用同一端點實現聊天、資料抽取、函式呼叫、RAG 等多種場景。

- **Q2. JSON Mode 與純文字輸出的差異在哪裡？**  
  **A:** JSON Mode 允許開發者為輸出定義 Schema，模型會嚴格遵循欄位名稱與型別。這帶來兩大好處：一是程式端可直接反序列化成強型別物件，提高可靠度；二是可以在 Schema 中加入 success/fail 欄位，明確界定模型是否找到答案，減少猜測與後續例外處理。

- **Q3. Function Calling 為何被視為 Agent 技術的基礎？**  
  **A:** Agent 需要能規劃、呼叫並根據結果調整後續步驟。Function Calling 提供 LLM 與外部世界互動的「函式呼叫-回傳」機制，讓模型可在推理過程中自行決定下一個行動並取得觀測結果，形成閉環控制，這正是 Agent 迴圈的核心。

- **Q4. MSKM 與傳統向量資料庫差別？**  
  **A:** 傳統向量 DB 僅提供向量寫入與相似度查詢。MSKM 進一步囊括資料前處理 Pipeline（抽取、分段、摘要、標籤）、長任務佇列、版本治理與 SK Plugin 整合，屬「RAG 即服務」。它關注資料流，而非僅是儲存格式。

- **Q5. 何時該自行切段，何時交給 MSKM 預設？**  
  **A:** 若文件結構單純、長度平均，預設 token-based chunking 已足夠；若內容篇幅落差大或資訊密度不均，最好在導入前先生成摘要、FAQ 等語義豐富片段，再行向量化，以免檢索結果失焦。

- **Q6. MCP 對開發者的價值？**  
  **A:** MCP 規範工具列舉、調用、資源傳遞等 JSON-RPC 操作並支持 stdio/SSE，使任何程式都能像「USB-C」般被 LLM 熱插拔。對開發者而言，可一次對接多家 LLM Host（Claude Desktop、Cursor…）而不需重寫橋接層。

- **Q7. 若模型不支援 Function Calling，有替代方案嗎？**  
  **A:** 可以在 system prompt 定義「訊息前置詞協議」，要求模型用特定前綴標示要給工具的指令，再由應用層攔截解析。雖不若原生支援嚴謹，卻能在緊急或資源受限時提供可行替代。

- **Q8. 如何評估摘要品質是否足以用於 RAG？**  
  **A:** 可透過 A/B Test：一組僅用原始分段，另一組加入摘要後比對回傳答案之完整度、引用率與 hallucination 次數。若摘要組在多數查詢下能降低「無關片段」且提升引用涵蓋率，即代表摘要策略有效。

- **Q9. SK 與 MSKM 整合時的常見陷阱？**  
  **A:** (1) 向量維度須與 LLM embedding model 一致；(2) Memory Plugin 名稱與 system prompt 工具呼叫名稱需對齊；(3) 若使用 docker 版 MSKM，記得檢查語系與編碼設定，避免中文亂碼造成 chunk 不可讀。

- **Q10. 如何在企業場域部署 MSKM？**  
  **A:** 可以先以 docker-compose 方式在私有雲落地，搭配企業版 OpenAI 或 Azure OpenAI 取得合規模型；如需彈性擴充，可改用 Kubernetes＋外部向量 DB（如 Azure AI Search）。透過 SK Memory Plugin 就能快速接軌既有 .NET 微服務或函式應用。

## 5. 問題／解決方案  

### Problem 1：長文 RAG 準確率低  
- Problem：面對 5–10 萬字文章，用固定長度 chunk 造成檢索片段與提問語義錯位。  
- Root Cause：文字密度不均，向量空間相似度難以捕捉高層次主題。  
- Solution：導入 LLM Synthesis Pipeline，先為全文及段落生成摘要與主題標籤，再一併寫入向量庫。  
- Example/Case Study：作者部落格 50 k 字 WSL 文章加入「1000 字摘要＋FAQ」後，對「WSL 能做什麼」的查詢從原先命中率 20 % 提升至 85 %，hallucination 次數顯著下降。

### Problem 2：Function Calling 多步驟流程易卡死  
- Problem：LLM 在長對話中可能遺漏必要 tool-result，導致應用端無法判斷下一步。  
- Root Cause：歷史訊息過多，關鍵狀態被截斷或模型選擇不回傳結果。  
- Solution：於每次 tool-result 後插入簡短 assistant acknowledge，並在 system prompt 加入「未完成指令需回復 progress flag」。  
- Example/Case Study：行事曆助理實裝後，透過 progress 標記使 LLM 在第 2 步漏回 add_event 結果時自動重試，成功率由 70 % 提升至 95 %。

### Problem 3：多來源 Plugins 管理混亂  
- Problem：Bing Search、Weather、Location 等插件同時存在時，LLM 易挑錯工具或參數。  
- Root Cause：tool descriptions 相似，缺少明確命名與分群。  
- Solution：採命名空間規則（如 search.bing, data.weather）、並在系統提示加入「僅使用最符合描述之工具」。  
- Example/Case Study：重構 Plugin Manifest 後，旅行助理在「帶傘？」提問時改用 weather 而非 search，降低多餘 token 消耗 30 %。

### Problem 4：MSKM Docker 中文亂碼  
- Problem：2025/02 版 MSKM 以 token 切段導致中文產生「晶晶體」。  
- Root Cause：分段器未處理 UTF-16 surrogate pair。  
- Solution：回退 0.96.x 版本或自編 custom chunker；同時向官方提交 PR。  
- Example/Case Study：社群回報後改用自訂 chunker，並以 unit test 驗證中文字斷詞完整，成功避免向量偏差。

### Problem 5：MCP JSON 編碼衝突  
- Problem：Claude Desktop 解析 MCPServer 傳回含中文的 JSON-RPC 時出現亂碼。  
- Root Cause：官方 csharp-sdk 未設定 Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping。  
- Solution：Fork SDK、修改 JsonSerializerOptions，或待官方合併修正。  
- Example/Case Study：作者自行 build 修正版 DLL，於直播現場成功展示「search andrew's blog」RAG 查詢，全程無亂碼，中英混排正常。

## 6. 版本異動  
- **v1.0.0**（2025-08-06）：初始重組版本，依五段式模板輸出 Metadata、全文重點、段落重點、問答集、問題／解決方案。尚無前版可對照。