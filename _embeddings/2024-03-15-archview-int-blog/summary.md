# 替你的應用程式加上智慧! 談 RAG 的檢索與應用

## 摘要提示
- RAG 架構: 透過 Ingestion、Retrieval、Synthesis 三段流程，讓 LLM 能引用外部知識並生成答案。
- GPTs + Custom Action: 利用 GPTs 的 function calling 連接自建 API，將檢索結果注入聊天上下文。
- Kernel Memory: 微軟開源專案，一站式包辦向量化、索引與查詢，可用 Serverless 或 Service 兩種模式。
- 向量資料庫: 以向量作為語意索引，支援 Tag 過濾以實作 ABAC 安全模型。
- Text-Embedding 模型: 選用 OpenAI text-embedding-3-large，提供 3072 維向量，費用與 token 控管需評估。
- Chunking 策略: 受模型 token 限制，須將長文切段並重疊，兼顧語意完整與成本。
- Demo 成果: 「安德魯的部落格 GPTs」能列舉文章、摘要主題、跨對話追問並引用正確連結。
- 開發成本: 實作時間極短，一天內可重建；昂貴部分為 LLM 推論與嵌入費用。
- 應用趨勢: 資料查詢已從 SQL 表格、NoSQL 文件邁向 Vector 空間，未來 APP 形態將走向智能 Agent。
- 架構師定位: 與其與 AI 競爭，應掌握 Prompt、Embedding、Vector Search 等基礎，做正確技術組合。

## 全文重點
本文由作者二十年部落格內容出發，實作一套「智慧檢索」服務，說明如何以 Retrieval-Augmented Generation（RAG）讓大型語言模型具備自家知識庫。核心流程分三段：Ingestion 先將文章切塊、嵌入向量並存入向量資料庫；Retrieval 透過向量相似度與 Tag 過濾，快速找出語意相關片段；Synthesis 由 GPT-4 彙整查詢與片段，產生最終回覆。作者採用 Microsoft Kernel Memory 範本，離線匯入 Markdown 後，以 SimpleVectorDB 存放 JSON 向量檔，再將 /search API 透過 GPTs Custom Action 暴露給 ChatGPT 使用者，達成對談式問答。示範案例包含整理部落格改版史、微服務資料一致性與家用 NAS 佈署等情境，皆能列出條列原則與對應文章連結。

文章並檢視技術選型：向量資料庫可用 Azure AI Search、Qdrant、PostgreSQL 等；嵌入模型選 text-embedding-3-large，但需留意 8191 token 限制及 $0.13/100 萬 token 費率；GPT-4 彙整一次問答約花 1.5 萬 token，成本約 0.15 美元。為降低門檻，作者把 GPTs 當前端，推論費由使用者的 ChatGPT Plus 吸收，自身僅負擔嵌入與檢索。文末總結資料庫演進：RDB 注重表格結構，NoSQL 著眼文件物件，而 VectorDB 以語意向量為索引，三者互補；查詢方式亦從條件語法、串流管線邁向自然語言。架構師應把握 Prompt、Embedding、Vector Search 等新基礎，將 AI 視為武器而非對手，才能在未來十年持續創造價值。

## 段落重點
### 0. 寫在前面
作者回顧二十年寫作歷程，累積 327 篇、400 萬字的技術文章，但長文難以閱讀；隨 ChatGPT 興起，他想用 AI 為部落格加「智慧」，讓讀者能用對談方式快速取得知識。選定以 GPTs 為介面、Azure OpenAI 為雲端，並自建 RAG 檢索服務，期望補足閱讀門檻，彰顯舊文章的新價值。

### 1. 「安德魯的部落格」GPTs ‑ Demo
示範三組對話：1) 整理部落格改版史，AI 列出 15 篇相關文章；2) 深入微服務資料一致性、報表與 SDK，AI 段落式回答並提供連結；3) 家用 NAS 服務建議，AI 同樣條列清單與文章來源。過程中可見 GPTs 自動呼叫檢索 API，再把結果寫回對談。作者評估體驗精準但尚需優化回覆格式，並提供完整對話檔以供驗證。

### 2. 部落格檢索服務
2-1 Synthesis：解析 GPTs function-calling 機制，說明如何以 OpenAPI Schema 描述 /search，讓 GPT-4 在對談中自動產生參數並調用。  
2-2 Retrieval：拆解 Query→Embedding→向量比對→Top-K→還原文本流程；介紹 cosine similarity 原理與 Kernel Memory /search、/ask 兩種 API，對比成本差異。  
2-3 Ingestion：展示匯入程式碼，將 Markdown 文章切段、向量化、加 Tag（categories、user-tags、post-url 等）後存為 JSON；說明 Tag 可實作 ABAC 權限，且可用 AND/OR 過濾。並討論向量資料庫選型、嵌入模型成本與 Chunking 策略，最後以 Docker 封裝只讀服務部署至 Azure。

### 3. AI 改變了內容搜尋方式
從 RDB（表格）、NoSQL（文件）到 VectorDB（向量）三世代演變闡述：向量空間讓「語意」成為第一層索引，SQL 與關鍵字搜尋將讓位於自然語言對談。嵌入、向量查詢與 LLM 彙整形成新基礎，開發者不再只寫複雜 Query，而是設計 Prompt、選模型與控制成本。同時比較 APP 與 Agent 兩種模式：使用 GPTs 可把 LLM 成本轉嫁給用戶；若自建 UI，則需自付推論費；未來智慧代理（Siri、Copilot 等）將更強調個人化與整合。

### 4. 結論
AI 時代把基礎技能推升到 Prompt Engineering、Embedding、Vector Search 等層級；架構師要聚焦如何組合強大武器而非與 AI 競賽。作者以三個月業餘時間完成兩支 GPTs 與一套 RAG 服務，體會到「微開發、大威力」的趨勢，並鼓勵同行提早熟悉新工具，為下一個十年做準備。