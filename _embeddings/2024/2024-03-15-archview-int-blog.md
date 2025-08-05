---
- source_file: /docs/_posts/2024/2024-03-15-archview-int-blog.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# 替你的應用程式加上智慧! 談 RAG 的檢索與應用 — 文章摘要

## Metadata

```yaml
# 原始 Front Matter:
layout: post
title: "替你的應用程式加上智慧! 談 RAG 的檢索與應用"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆","AI","Semantic Kernel"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-03-15-archview-int-blog/2024-03-10-00-46-41.jpg

# 自動識別關鍵字:
primary-keywords:
  - RAG (Retrieval-Augmented Generation)
  - Kernel Memory
  - Semantic Kernel
  - Embedding / Vector Search
  - GPTs / ChatGPT
  - Azure OpenAI Service
  - Text-Embedding-3-Large
secondary-keywords:
  - Vector Database (Azure AI Search, Qdrant, Redis, PostgreSQL)
  - Tagging / ABAC 安全過濾
  - Two-Tower Recommendation
  - Function Calling
  - .NET / C#
  - GitHub Pages
  - AI Explorer / Copilot
  - NoSQL vs RDB vs VectorDB

# 技術堆疊分析:
tech_stack:
  languages:
    - C#
    - Markdown / JSON
  frameworks:
    - Microsoft Semantic Kernel
    - Kernel Memory (Serverless / Service)
  tools:
    - Azure OpenAI (GPT-4, text-embedding-3-large)
    - ChatGPT GPTs
    - GitHub / GitHub Actions
    - VS Code
  platforms:
    - Azure App Service
    - GitHub Pages
  concepts:
    - RAG Pipeline (Ingestion, Retrieval, Synthesis)
    - Embedding Space
    - Vector Similarity (cosine)
    - Tag-Based Security (ABAC)
    - AI DX / Prompt Engineering

# 參考資源:
references:
  internal_links:
    - /2024/01/15/archview-llm/
    - /2022/04/25/microservices16-api-implement/
    - /2016/09/16/blog-as-code/
  external_links:
    - https://github.com/microsoft/kernel-memory
    - https://github.com/microsoft/semantic-kernel
    - https://platform.openai.com/docs/guides/embeddings
    - https://areganti.notion.site/Applied-LLMs-Mastery-2024-562ddaa27791463e9a1286199325045c
  mentioned_tools:
    - ChatGPT
    - GPT-4
    - Azure AI Search
    - Qdrant
    - Redis

# 內容特性:
content_metrics:
  word_count: 15500
  reading_time: "50 分鐘"
  difficulty_level: "進階"
  content_type: "Architecture & PoC 實作筆記"
```

---

## 文章摘要（1000 字內）

作者以 20 年、400 萬字的個人部落格為案例，完整示範如何用 Microsoft Kernel Memory + Azure OpenAI 建立「RAG 檢索服務」，再透過 ChatGPT GPTs 變成一位能對談、能引用原文出處的知識助理。文章先用三段 Demo 呈現 GPTs 如何幫讀者整理部落格歷史、彙整微服務文章、甚至抓出作者都快忘記的 NAS 實作文；接著循 RAG 三階段解析：

1. Synthesis—在 GPTs 內設定 Instruction 與自訂 OpenAPI Action，讓 GPT 能看懂 swagger、決定何時呼叫 /search，並把檢索結果重寫成對談答案。  
2. Retrieval—說明向量搜尋流程（Query→Embedding→Similarity→Top-K→回原文），並比較 /search 與 /ask 兩種 API 用法與成本差異。  
3. Ingestion—展示 .NET 程式批次掃描 Markdown、分段(chunk)→text-embedding-3-large 轉向量→TagCollection 寫入 SimpleVectorDB；同時闡述 Tag-based Filter 可實作 ABAC 安全過濾。

作者再從「表格→文件→向量」的演進談資料庫世代，強調向量索引並非取代 RDB / NoSQL，而是為 AI 搜尋加上一層語意座標。最後比較「網站搜尋」(App) 與「對談代理」(Agent) 的定位與費用分攤，指出未來 AI DX 需要掌握 Prompt Engineering、Embedding、VectorDB 等新基礎能力；資深架構師不該和 AI 競賽，而要善用 AI 作為威力強大的副手。

---

## 關鍵要點

- RAG Pipeline＝Ingestion(向量化)＋Retrieval(向量搜尋)＋Synthesis(LLM 回答)。  
- Kernel Memory 以 OpenAPI 暴露 /search 與 /ask，配合 GPTs 的 Function Calling 可零程式碼串接。  
- 向量資料庫缺乏 row-level ACL，需用 TagCollection + Filter 建 ABAC 安全機制。  
- text-embedding-3-large 每 1M tokens 僅 US$0.13，但 GPT-4 彙整答案成本高 100 倍，需精簡 context。  
- RDB→NoSQL→VectorDB 映射「變數→物件→語意」層級；向量索引將成為新常態。  
- Demo 證實：20 年 327 篇文章，可在 1 天內完成向量化並上線 Chat 知識庫。  
- 架構師必須將 AI DX 納入 CI/CD 與安全模型，形成「第 4 條 Pipeline」。

---

## 段落摘要（依 H2）

### 0. 寫在前面  
說明撰寫長篇技術文章的價值與難讀缺點，期待借助 GPTs 提升可用性，並提出本次 PoC 目標：打造部落格智慧檢索助手。

### 1. 「安德魯的部落格」GPTs Demo  
用三個示範展示 GPTs 的實際體驗：  
1-1 整理 20 年系統遷移史；1-2 彙整微服務相關文；1-3 抓出家用 NAS 文章。觀察 GPTs 能切題引用但偶爾需追加指令。

### 2. 部落格檢索服務  
概述整體架構：GPTs 前端＋Kernel Memory 後端＋Azure OpenAI。並對照 Applied LLMs Mastery 課程，對應 RAG 三組件。

#### 2-1 RAG 資料檢索的應用 (Synthesis)  
解析 GPTs 如何透過自訂 Action 自動產生 /search payload，再以三段 Prompt (System/User/Format) 整合回答。

#### 2-2 語意檢索—向量搜尋 (Retrieval)  
深入講解 Embedding → Vector Similarity → Top-K，對比 /search 與 /ask 差異、費用試算、cosine 與 distance 的意義。

#### 2-3 建立文章向量資料庫 (Ingestion)  
示範 .NET 批次把 Markdown 轉向量，存 SimpleVectorDB；介紹 chunk 策略、TagCollection 與 OR/AND Filter 語法。

### 3. AI 改變了內容搜尋方式  
從資料庫世代、查詢方式、交互模式三面向，論述 RDB→NoSQL→VectorDB 的定位及對架構師能力模型的衝擊。

### 4. 結論  
總結三篇 LLM 系列心得：AI 使基礎技能上移；架構師須掌握 Prompt、Embedding、Vector Search，並思考如何「善用 AI」而非「被取代」。

---

## 問答集

### Q1 什麼是 RAG？  
A: Retrieval-Augmented Generation 將「向量檢索」與「大型語言模型生成」串成流水線，先找出語意相近內容，再交由 LLM 組成答案，兼具即時性與私有知識覆蓋率。

### Q2 Kernel Memory 與 Semantic Kernel 有何關係？  
A: Semantic Kernel 提供 AI Chain；Kernel Memory 在其上加值實作 RAG，內建 Ingestion、VectorDB 及 Web API，兩者同屬 Microsoft OSS，可獨立或整合使用。

### Q3 /search 與 /ask 差在哪？  
A: /search 只做 Retrieval，回傳 Top-K chunks；/ask 再附一層 LLM 彙整 (Synthesis)。/ask 方便但需額外 GPT 成本並維護 prompt。

### Q4 如何控制不同使用者只能看授權內容？  
A: 在 Ingestion 階段為每筆資料加上 user-id 或 role 標籤，查詢時在 filters 帶入同樣 tag，Kernel Memory 會轉成底層 VectorDB 的過濾語法。

### Q5 text-embedding-3-large 與 GPT-4 成本差多少？  
A: 1M tokens 嵌入僅 US$0.13；同量 GPT-4 輸入要 US$10，輸出更高，約相差百倍。

### Q6 Chunk 應如何切割？  
A: 必須 < 8191 tokens；宜以段落為界並可重疊，避免語意斷裂，同時降低 LLM 回答時 context size。

### Q7 GPTs 為何適合 PoC？  
A: 免寫前端、內建 Function Calling、成本由訂閱者負擔，能快速驗證知識庫品質及回覆體驗。

### Q8 VectorDB 會取代 RDB 嗎？  
A: 不會。Vector 索引負責語意相似度；原始文件、欄位過濾仍依賴 RDB/NoSQL，兩者互補。

### Q9 何時考慮改用本地 LLM？  
A: 當對隱私、延遲或成本有嚴格要求且硬體允許，可封裝自有模型，將雲端費用轉為設備 CAPEX。

### Q10 架構師在 AI 時代的新任務？  
A: 決定「何處用 AI、用哪種模型、資料如何向量化及保護」，並將 AI Pipeline 納入 CI/CD 與治理流程。

---

## 問題-解決方案整理

### Problem 1：長尾技術文章難以被讀者快速運用  
Root Cause: 關鍵字搜尋無法抓語意，文章量大且跨年代分類不一。  
Solution: 建立私有 RAG 服務，GPTs 前端 + Kernel Memory 後端；文章向量化並加標籤，讓讀者用自然語言提問即可得到摘要與連結。  
Example: /search API + GPTs 回覆 Demo 1-1~1-3。

### Problem 2：向量資料庫缺乏細粒度權限  
Root Cause: VectorDB 原生不支援 Row ACL。  
Solution: 以 TagCollection 在 Ingestion 階段刻入 user / role 標籤；搜尋時帶 filters；配合 ABAC 策略。  
Example: filters=[{ "user-tags":["microservice"] }].

### Problem 3：GPT-4 彙整成本過高  
Root Cause: Top-K chunk 全丟 LLM，token 耗用大。  
Solution: 1) 調整 chunk size；2) 先用 GPT-3.5 做初步摘要；3) 動態 Top-K + relevance 閥值。  
Example: minRelevance=0.45 + limit=5 → token 減少 60%。

---

## 版本異動紀錄
- 1.0.0 (2025-08-06)  初版生成：含 Metadata、文章/段落摘要、10 組 Q&A 與 3 組問題-解決方案。