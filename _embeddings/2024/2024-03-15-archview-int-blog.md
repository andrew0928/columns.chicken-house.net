---
source_file: "_posts/2024/2024-03-15-archview-int-blog.md"
generated_date: "2025-01-03 17:00:00 +0800"
version: "1.0"
tools: github_copilot
model: claude_sonnet_3_5
---

# 替你的應用程式加上智慧! 談 RAG 的檢索與應用 - 生成內容

## Metadata

### 原始 Metadata

layout: post
title: "替你的應用程式加上智慧! 談 RAG 的檢索與應用"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆", "AI", "Semantic Kernel"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-03-15-archview-int-blog/2024-03-10-00-46-41.jpg

### 自動識別關鍵字

keywords:
  primary:
    - RAG
    - Retrieval-Augmented Generation
    - GPTs
    - Semantic Kernel
    - Kernel Memory
    - Text Embedding
    - Vector Search
    - 向量搜尋
    - AI 應用開發
    - LLM 應用程式
  secondary:
    - Chat GPT
    - Azure OpenAI
    - OpenAI
    - Embedding Space
    - Vector Database
    - 向量資料庫
    - Custom Action
    - Function Calling
    - Prompt Engineering
    - 語意搜尋
    - 內容檢索
    - 知識庫

### 技術堆疊分析

tech_stack:
  languages:
    - C#
    - JSON
    - Markdown
  frameworks:
    - .NET
    - Semantic Kernel
    - Kernel Memory
  tools:
    - Azure App Service
    - Azure OpenAI
    - Visual Studio
    - Git
    - Docker
  platforms:
    - Azure
    - Chat GPT
    - GPTs
    - Windows
  ai_models:
    - GPT-4
    - text-embedding-3-large
  concepts:
    - RAG
    - Retrieval-Augmented Generation
    - Vector Search
    - Text Embedding
    - Natural Language Processing
    - AI Application Development
    - Prompt Engineering

### 參考資源

references:
  internal_links:
    - /2024/01/15/archview-llm/
    - /2024/02/10/archview-int-app/
    - /2016/09/16/blog-as-code/
    - /2021/03/01/practice-01/
    - /2022/04/25/microservices16-api-implement/
  external_links:
    - https://microsoft.github.io/kernel-memory/
    - https://github.com/microsoft/kernel-memory
    - https://areganti.notion.site/Applied-LLMs-Mastery-2024-562ddaa27791463e9a1286199325045c
    - https://openai.com/blog/new-embedding-models-and-api-updates
    - https://platform.openai.com/docs/guides/embeddings/embedding-models
    - https://openai.com/pricing
    - https://aws.amazon.com/tw/what-is/retrieval-augmented-generation/
    - https://chat.openai.com/g/g-F3ckJut37-an-de-lu-de-bu-luo-ge
    - https://github.com/microsoft/generative-ai-for-beginners
  mentioned_tools:
    - Kernel Memory
    - Semantic Kernel
    - Azure OpenAI
    - GPTs
    - Chat GPT
    - Vector Database
    - text-embedding-3-large
    - GPT-4
    - Azure AI Search
    - Qdrant
    - PostgreSQL
    - Elastic Search
    - Redis

### 內容特性

content_metrics:
  word_count: 27000
  reading_time: "90 分鐘"
  difficulty_level: "進階"
  content_type: "技術深度解析"

## 摘要

本文是 LLM 應用開發系列第三篇，深入探討 RAG (Retrieval-Augmented Generation) 的檢索與應用。作者以自己的部落格為例，展示如何運用 Kernel Memory、Azure OpenAI 等技術，建立一個能夠智慧檢索部落格內容的 GPTs。文章詳細介紹了 RAG 的三個核心組件：Ingestion（資料向量化）、Retrieval（語意檢索）、Synthesis（結果彙整），並深入分析從傳統關鍵字搜尋進化到語意搜尋的技術演進。

### 段落摘要

**第 0 章 - 寫在前面**
介紹作者部落格的背景：20 年來累積 327 篇文章、400 萬字內容，說明透過 AI 技術提升內容運用價值的動機。

**第 1 章 - "安德魯的部落格" GPTs Demo**
展示 GPTs 的實際應用效果，包括部落格發展史整理、特定主題彙整、經驗分享彙整等示範案例，證明 AI 輔助內容檢索的實用性。

**第 2 章 - 部落格檢索服務 AndrewBlogKMS**
深入解析 RAG 架構的三個核心組件：
- Synthesis：使用 GPTs 進行結果彙整
- Retrieval：運用 Kernel Memory 進行語意檢索
- Ingestion：建立文章向量化的資料庫

**第 3 章 - AI 改變了內容搜尋方式**
探討從表格（RDB）、文件（NoSQL）到向量（VectorDB）的資料庫演進，以及從條件查詢到語意查詢的轉變。

## 問答對

### Q1: 什麼是 RAG？它的三個核心組件是什麼？
A1: RAG (Retrieval-Augmented Generation) 是檢索增強生成技術，包含三個核心組件：
1. **Ingestion（資料擷取）**：將文件分段並生成向量，存入索引
2. **Retrieval（檢索）**：利用向量相似性檢索最相關的文件片段
3. **Synthesis（合成）**：LLM 結合查詢和檢索結果，生成準確回應

### Q2: Text Embedding 的工作原理是什麼？
A2: Text Embedding 是將文字轉換成多維度向量的過程。每個維度代表不同的語意特徵，文字在這個向量空間中的位置表達其語意含義。相似語意的文字會在向量空間中靠近，透過計算向量間的相似度（如餘弦相似度）來找出語意相近的內容。

### Q3: 如何使用 Kernel Memory 建立檢索服務？
A3: 使用 Kernel Memory 的步驟包括：
1. 配置 Azure OpenAI 的 text embedding 和 chat completion 模型
2. 選擇向量儲存方式（如 SimpleVectorDB）
3. 使用 ImportTextAsync 方法匯入文章內容並生成向量
4. 透過 SearchAsync 或 AskAsync 提供檢索服務
5. 設定適當的 Tags 進行內容分類和權限控制

### Q4: GPTs Custom Action 如何與外部 API 整合？
A4: GPTs Custom Action 整合外部 API 的方式：
1. 提供符合 OpenAPI 規範的 API swagger 文件
2. 在 description 中詳細說明 API 的用途和參數意義
3. GPTs 會根據對話脈絡自動判斷何時呼叫 API
4. 透過 Function Calling 機制自動產生符合規格的請求
5. 將 API 回應結果整合到對話回應中

### Q5: 向量資料庫與傳統資料庫有什麼差異？
A5: 主要差異包括：
- **儲存方式**：向量資料庫儲存高維度向量，傳統資料庫儲存結構化資料
- **查詢方式**：向量資料庫使用相似度搜尋，傳統資料庫使用精確條件匹配
- **應用場景**：向量資料庫適合語意搜尋和 AI 應用，傳統資料庫適合事務處理
- **輔助關係**：向量資料庫通常搭配傳統資料庫使用，負責語意索引，傳統資料庫負責原始資料儲存

### Q6: 如何控制 RAG 應用的安全性和權限？
A6: 透過 Tags 機制實現安全控制：
1. **資料標記**：在 Ingestion 階段為每筆資料加上適當標籤
2. **查詢過濾**：在 Retrieval 時使用 filters 參數限制查詢範圍
3. **ABAC 原則**：實施屬性基礎存取控制，根據使用者角色設定可存取的標籤
4. **後端控制**：將 Kernel Memory 當作私有後端服務，透過應用程式層控制存取權限

### Q7: RAG 應用的成本結構是什麼？
A7: RAG 應用的主要成本包括：
1. **Embedding 成本**：文件向量化的一次性費用（如 text-embedding-3-large $0.13/1M tokens）
2. **查詢成本**：每次查詢時問題向量化的費用
3. **LLM 推理成本**：結果彙整時的 GPT-4 使用費用（$10/1M input tokens）
4. **儲存成本**：向量資料庫的儲存和運算費用
5. **API 呼叫成本**：各種 AI 服務的 API 使用費用

### Q8: 從 RDB 到 VectorDB 的演進代表什麼意義？
A8: 資料庫演進的三個階段代表處理層級的提升：
1. **RDB（表格）**：處理欄位級的變數，著重效率和精確度
2. **NoSQL（文件）**：處理物件級的文件，更貼近應用程式模型
3. **VectorDB（向量）**：處理語意級的向量，能夠理解內容的意義和關聯性
每個階段都不是取代，而是在更高層級上增強資料處理能力。

## 解決方案

### 問題：如何建立部落格的智慧檢索系統？

**情境**：擁有大量文章內容的部落格，需要提供比關鍵字搜尋更智慧的內容檢索功能

**解決方案**：
1. **選擇技術架構**：
   - 使用 Kernel Memory 作為 RAG 引擎
   - 選擇 Azure OpenAI 提供 embedding 和 LLM 服務
   - 透過 GPTs 提供使用者介面

2. **實施資料向量化**：
   ```csharp
   var memory = new KernelMemoryBuilder()
       .WithAzureOpenAITextGeneration(config)
       .WithAzureOpenAITextEmbeddingGeneration(embeddingConfig)
       .WithSimpleVectorDb(path)
       .Build<MemoryServerless>();
   
   await memory.ImportTextAsync(content, documentId, tags);
   ```

3. **建立檢索 API**：
   - 實作 /search 端點提供向量檢索
   - 實作 /ask 端點提供完整問答
   - 設定適當的 OpenAPI 文件

4. **整合 GPTs**：
   - 設定 Custom Action 連接檢索 API
   - 撰寫適當的 Instructions 指導 GPTs 行為
   - 測試和調整 prompt 效果

**相關工具/指令**：
- Kernel Memory NuGet 套件
- Azure OpenAI Studio
- GPTs Builder
- Swagger/OpenAPI 工具

**注意事項**：
- 注意 token 使用量和成本控制
- 選擇適當的 embedding 模型
- 設計合理的文件分段策略

### 問題：如何優化向量搜尋的準確性？

**情境**：RAG 系統建立後，搜尋結果的相關性不夠精確

**解決方案**：
1. **改善文件分段**：
   - 按照語意邊界分段，避免切斷完整概念
   - 保持段落間適當重疊
   - 控制每段文字長度在 token 限制內

2. **優化 Tags 設計**：
   ```csharp
   var tags = new TagCollection();
   tags.Add("categories", categories);
   tags.Add("topic", topics);
   tags.Add("difficulty", level);
   tags.Add("post-date", date);
   ```

3. **調整查詢參數**：
   - 設定適當的 minRelevance 閾值
   - 調整 limit 參數控制結果數量
   - 使用 filters 縮小搜尋範圍

4. **提升 prompt 品質**：
   - 在查詢前先處理和精煉使用者問題
   - 提供更多上下文資訊
   - 設計更好的結果彙整指令

**相關工具/指令**：
```json
{
  "query": "processed_user_question",
  "filters": [{"category": ["target_category"]}],
  "minRelevance": 0.3,
  "limit": 5
}
```

**注意事項**：
- 不同領域可能需要不同的相似度閾值
- 過度過濾可能遺漏相關內容
- 需要平衡準確性和涵蓋性

### 問題：如何控制 RAG 系統的權限和安全性？

**情境**：多使用者環境下需要確保使用者只能存取有權限的內容

**解決方案**：
1. **實施 ABAC 權限模型**：
   - 為每筆內容標記適當的存取屬性
   - 建立角色與屬性的對應關係
   - 在查詢時自動套用權限過濾

2. **設計 Tags 安全策略**：
   ```csharp
   // 資料匯入時加入權限標籤
   tags.Add("access-level", ["public", "members"]);
   tags.Add("department", ["engineering", "marketing"]);
   tags.Add("user-group", ["admin", "user"]);
   ```

3. **後端安全控制**：
   - 將 Kernel Memory 部署為私有服務
   - 透過應用程式層驗證使用者身分
   - 根據使用者角色動態組合查詢過濾條件

4. **API 安全設計**：
   ```csharp
   var userFilters = GetUserAccessFilters(userRole);
   var searchRequest = new SearchRequest
   {
       Query = query,
       Filters = userFilters,
       MinRelevance = 0.3
   };
   ```

**相關工具/指令**：
- Azure Active Directory 進行身分驗證
- 自定義中介軟體處理授權
- 設定 HTTPS 和 API 金鑰保護

**注意事項**：
- 權限標籤應在資料建立時就確定
- 避免在 runtime 動態修改權限標籤
- 定期審查和更新權限設定
