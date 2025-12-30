---
layout: synthesis
title: "替你的應用程式加上智慧! 談 RAG 的檢索與應用"
synthesis_type: solution
source_post: /2024/03/15/archview-int-blog/
redirect_from:
  - /2024/03/15/archview-int-blog/solution/
---

以下為針對原文萃取與重構的 18 個教學型問題解決案例，均依模板整理，涵蓋 RAG 全流程（Ingestion/ Retrieval/ Synthesis）、GPTs Custom Action 整合、成本/安全/效能/可維運性等核心議題，並附帶示範程式片段、操作步驟、實測觀察與練習題。

------------------------------------------------------------

## Case #1: 為部落格打造 RAG 檢索助理（GPTs + Kernel Memory）

### Problem Statement（問題陳述）
- 業務場景：作者擁有 20 年、327 篇共約 400 萬字的技術文章，讀者常因篇幅長、主題散而難以快速找到相關知識。希望提供「能問能答」的互動介面，將散落文章快速彙整為答案與來源，改善學習與查找效率。
- 技術挑戰：需要把自然語言問題轉為語意檢索、從多篇文章中找 Top-K 片段並由 LLM生成答案，兼顧成本、延遲與正確性。
- 影響範圍：讀者檢索效率、作者知識再利用度、平台價值感受；若無法落地，文章價值難被充分挖掘。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 關鍵字搜尋無法反映語意相似度，導致錯失相關內容。
  2. 文章長、結構不一，人工彙整成本高。
  3. 缺乏可直接問答、帶脈絡與來源的互動介面。
- 深層原因：
  - 架構層面：缺少 Ingestion/ Retrieval/ Synthesis 的端到端流與可被 LLM 呼叫的檢索 API。
  - 技術層面：未有向量化與向量資料庫；缺少 GPTs 的外部工具使用（Function Calling）。
  - 流程層面：沒有將內容「先索引、後檢索、再合成」的一貫流程與部署模式。

### Solution Design（解決方案設計）
- 解決策略：採用 GPTs 作為對談前端，透過 Custom Action 呼叫自建檢索服務（Kernel Memory Service），以 text-embedding-3-large 建立向量索引，/search 取得 Top-K，再由 GPTs 根據檢索結果進行 Synthesis，附上文章連結，形成可追溯的問答。

- 實施步驟：
  1. 設計 GPTs 與指令
     - 實作細節：撰寫角色指示，要求「回答需附來源連結、若不足回 INFO NOT FOUND」。
     - 所需資源：ChatGPT Plus（GPT-4）、GPTs Builder。
     - 預估時間：2 小時
  2. 建立檢索 API（/search）
     - 實作細節：以 Kernel Memory（Service 模式）部署 Azure App Service，掛上 embedding 與向量儲存。
     - 所需資源：.NET、Kernel Memory、Azure OpenAI、Azure App Service
     - 預估時間：4 小時
  3. 建索引（Ingestion）
     - 實作細節：以 Kernel Memory（Serverless）批量匯入 Markdown/HTML 純文，Chunking + Embedding + Index。
     - 所需資源：Console Tool、Azure OpenAI Embedding
     - 預估時間：3 小時
  4. GPTs 綁定 Custom Action
     - 實作細節：在 GPTs 內上傳 OpenAPI schema，描述路徑/參數語意。
     - 所需資源：Swagger JSON
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```json
// /search Request（GPTs 呼叫）
{
  "query": "微服務 資料一致性 維持作法",
  "filters": [],
  "minRelevance": 0.3,
  "limit": 5
}
```

實際案例：安德魯的部落格 GPTs 成功回答微服務一致性問題，且附上正確文章連結。
實作環境：C#/.NET、Kernel Memory（2024/03 pre-GA）、Azure OpenAI（text-embedding-3-large、GPT-4 1106 preview）、Azure App Service、SimpleVectorDB。
實測數據：
- 改善前：讀者人工查找 10–30 分鐘/題（估）。
- 改善後：RAG 問答 30–60 秒/題（示範）。
- 改善幅度：約 80–95%。

Learning Points（學習要點）
- 核心知識點：
  - RAG 三段式：Ingestion/ Retrieval/ Synthesis
  - GPTs Function Calling + OpenAPI schema
  - Embedding/Top-K/MinRelevance 的檢索思維
- 技能要求：
  - 必備技能：REST、Swagger、JSON、雲端部署
  - 進階技能：Prompt Engineering、向量索引設計、成本優化
- 延伸思考：
  - 可應用於內部知識庫、FAQ、自助客服。
  - 風險：內容過時、幻覺、授權控管。
  - 優化：調整 chunk 策略、rerank、加入 Hybrid Search。

Practice Exercise（練習題）
- 基礎練習：在 GPTs Instruction 中加入「回答需附來源連結」並測試（30 分鐘）
- 進階練習：替換 minRelevance 與 limit，觀察檢索差異（2 小時）
- 專案練習：完成一個小型文件庫（50 篇文章）端到端 RAG（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能問答並附來源連結
- 程式碼品質（30%）：API/配置清楚，錯誤處理完備
- 效能優化（20%）：檢索延遲與成本可控
- 創新性（10%）：有合理延伸（e.g. rerank、摘要對齊）

------------------------------------------------------------

## Case #2: 以 OpenAPI Schema 驅動 GPTs Custom Action 工具使用

### Problem Statement（問題陳述）
- 業務場景：希望 GPTs 能在對談中「自動判斷何時呼叫」自建的檢索 API，並正確帶入參數（query、minRelevance、limit），提供即時 Top-K 檢索結果作為後續回答依據。
- 技術挑戰：需要讓 LLM 理解 API 功能與參數語意、限制與預設值，否則不會正確呼叫或參數錯放。
- 影響範圍：若工具使用不正確，檢索落空或答非所問，整體體驗崩壞。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺乏標準化 API 描述，LLM 無從理解如何呼叫。
  2. 參數語義描述不足（缺 description）導致判斷錯誤。
  3. 缺同意流程（工具使用需經使用者同意）。
- 深層原因：
  - 架構層面：未把檢索服務以「工具（Action）」形式注入對談代理。
  - 技術層面：缺 OpenAPI/Swagger 規範與嚴謹描述。
  - 流程層面：缺少「何時應呼叫工具」的 Instruction 設計。

### Solution Design（解決方案設計）
- 解決策略：為 /search 提供完整 OpenAPI schema，清楚描述 path/參數與語意，將 schema 置入 GPTs 的 Actions。Instruction 中提示何時呼叫，以提升工具使用率與正確性。

- 實施步驟：
  1. 撰寫 Swagger/OpenAPI
     - 實作細節：對 query/minRelevance/limit 撰寫描述與範例。
     - 所需資源：Swagger Editor/Swashbuckle
     - 預估時間：1.5 小時
  2. 綁定 GPTs Action
     - 實作細節：在 GPTs Builder 上傳 schema，並加上「遇到與文章查詢相關需呼叫」。
     - 所需資源：GPTs Builder
     - 預估時間：0.5 小時

- 關鍵程式碼/設定（OpenAPI 片段）：
```json
{
  "paths": {
    "/search": {
      "post": {
        "summary": "Semantic search",
        "description": "Use embeddings to return Top-K relevant chunks",
        "parameters": [],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "properties": {
                  "query": { "type": "string", "description": "User query in natural language" },
                  "minRelevance": { "type": "number", "description": "0~1 cosine threshold, e.g. 0.3" },
                  "limit": { "type": "integer", "description": "Top-K results, e.g. 5" }
                },
                "required": ["query"]
              }
            }
          }
        }
      }
    }
  }
}
```

實際案例：GPTs 顯示「Talked to andrewblogkms.azurewebsites.net」，帶入 query「微服務 資料一致性 維持作法」、minRelevance 0.3、limit 5。
實作環境：Swagger/Swashbuckle、GPTs Builder、Azure App Service。
實測數據：
- 改善前：無法自動呼叫 API（0% 成功）。
- 改善後：指定範例中可正確呼叫與取回結果（100%）。
- 幅度：+100%。

Learning Points
- 核心知識點：OpenAPI 作為 LLM 工具使用提示；描述文字等於 Prompt。
- 技能要求：Swagger 寫作、API 設計、Prompt for Tool-Use。
- 延伸思考：可加入嚴格 schema/enum 限制；風險在於描述不足；可優化參數預設。

Practice Exercise
- 基礎：在 schema 中為每個欄位加入 description（30 分）
- 進階：加入 filters 結構與 enum 值（2 小時）
- 專案：為一組 3 個動作的 API 寫完整 OpenAPI+測試（8 小時）

Assessment Criteria
- 功能完整性（40%）：GPTs 能正確呼叫
- 程式碼品質（30%）：Schema 清晰、一致
- 效能優化（20%）：呼叫次數與負載管理
- 創新性（10%）：Schema 驗證/範例完善

------------------------------------------------------------

## Case #3: 語意檢索 /search 設計與 Top-K 整合

### Problem Statement（問題陳述）
- 業務場景：使用者以自然語言提問，系統須將 Query 轉向量並回傳 Top-K 最相關文章片段與標註，供 Synthesis 生成可讀答案與引用。
- 技術挑戰：Embedding、相似度計算（cosine）、Top-K 取捨、filters 過濾與回傳結構規劃。
- 影響範圍：檢索準確性與覆蓋率，直接影響答案正確性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 關鍵字搜尋無法捕捉語意距離。
  2. 多來源/長文需切片與標註。
  3. 缺少一致的 API 輸入/輸出定義。
- 深層原因：
  - 架構：未建立向量索引與檢索層，Synthesis 缺料。
  - 技術：未選定 embedding 模型與相似度。
  - 流程：未定義 minRelevance/limit/filters 溝通語意。

### Solution Design
- 解決策略：/search 接收 query、filters、minRelevance、limit；以 text-embedding-3-large 轉向量，在向量庫做 cosine 相似度排序，回傳含 partitions、tags、relevance 的 JSON 結構，供 LLM 彙整。

- 實施步驟：
  1. API 設計與回傳結構
     - 細節：Query->Vector、排序、Top-K、附 partitions.tags。
     - 資源：Kernel Memory Service
     - 時間：2 小時
  2. 嵌入與相似度
     - 細節：text-embedding-3-large，cosine 相似；minRelevance 控噪。
     - 資源：Azure OpenAI
     - 時間：1 小時

- 關鍵程式碼/設定：
```json
// /search Response（節錄）
{
  "query": "微服務 資料一致性 維持作法",
  "results": [{
    "documentId": "post-2022-04-25",
    "partitions": [{
      "text": "…狀態機驅動 API… racing condition…",
      "relevance": 0.48848,
      "tags": {
        "post-url": ["https://columns…/microservices16-api-implement/"],
        "post-title": ["微服務架構 - 從狀態圖來驅動 API 的實作範例"]
      }
    }]
  }]
}
```

實際案例：Top-5 結果皆對應作者文章且主題吻合。
實作環境：Kernel Memory Service、Azure OpenAI、SimpleVectorDB。
實測數據：
- 改善前：傳統搜尋常回傳無關連結果（示例觀察约 40% 命中）。
- 改善後：示範查詢 Top-5 命中率 100%。
- 幅度：+150%（40%→100%）。

Learning Points
- 核心：Top-K、minRelevance、filters 與向量相似度。
- 技能：API 設計、嵌入模型呼叫。
- 延伸：可加入 BM25 + 向量混合檢索；風險在過濾過度；優化以 rerank。

Practice Exercise
- 基礎：調整 limit=3/10 比較答案品質（30 分）
- 進階：加入 filters 篩「microservices」標籤（2 小時）
- 專案：建立含 rerank 的 /search+ /ask 混合策略（8 小時）

Assessment Criteria
- 功能（40%）：/search 正確回傳 Top-K
- 品質（30%）：結構/欄位/標註清楚
- 效能（20%）：延遲與吞吐可測
- 創新（10%）：Rerank/Hybrid

------------------------------------------------------------

## Case #4: Synthesis 提示工程模版（Facts/Question/Answer）與來源引用

### Problem Statement
- 業務場景：LLM 需以檢索結果為「事實」，生成答案且附連結；若不足則回 INFO NOT FOUND，避免亂編。
- 技術挑戰：如何穩定讓模型「只根據檢索內容」作答並附來源，且在語言（繁中/英）上可控。
- 影響範圍：答案可信度、可追溯性與使用者信任。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. LLM 易幻覺；未強化「只根據事實」。
  2. 輸出未要求附來源。
  3. 語言與風格未被約束。
- 深層原因：
  - 架構：缺 Synthesis Prompt 策略。
  - 技術：未建立模板化/結構化提示。
  - 流程：未定義不足資訊時的回覆規則。

### Solution Design
- 解決策略：使用固定模板「Facts（檢索片段）+ 指示 + Question + Answer:」，要求附來源超連結；不足時回 INFO NOT FOUND；需要時加上「用繁體中文回答」。

- 實施步驟：
  1. 設計通用 Synthesis Prompt
     - 細節：固定段落、清楚規範輸出行為。
     - 資源：GPT-4
     - 時間：1 小時
  2. 驗證與微調
     - 細節：測試有/無資料兩種情境；觀察幻覺。
     - 資源：ChatGPT/Playground
     - 時間：1 小時

- 關鍵程式碼/設定：
```text
Facts:
==== [File:...;Relevance:64.1%]:
{Top-K chunks here}
======
Given only the facts above, provide a comprehensive answer.
If insufficient, reply 'INFO NOT FOUND'.
Include sources as hyperlinks.
Question: {user question}
Answer: （用繁體中文回答）
```

實際案例：提問「分散式報表處理？」時，無足夠內容即未亂編；有內容時正確附上文章連結。
實作環境：ChatGPT GPT-4、Kernel Memory /search。
實測數據：
- 改善前：可能出現杜撰資料。
- 改善後：示範問答中無亂編、皆附來源。
- 幅度：顯著降低幻覺（示例查詢 0 次）。

Learning Points
- 核心：Grounding、來源引用、風格控制。
- 技能：Prompt Engineering、模板化。
- 延伸：可產出「來源段落片段」並加高亮；風險：模板過長耗 Token；優化：壓縮事實或改用 map-reduce 摘要。

Practice Exercise
- 基礎：加入「請列出 3 點要點」的指示（30 分）
- 進階：將來源以 [n] 參考文獻樣式列於文末（2 小時）
- 專案：做「多輪對話上下文 + 來源追蹤」SOP（8 小時）

Assessment Criteria
- 功能（40%）：輸出附來源、INFO NOT FOUND 規則有效
- 品質（30%）：語言/格式一致
- 效能（20%）：Token 成本可控
- 創新（10%）：自動引用整理

------------------------------------------------------------

## Case #5: Ingestion—Chunking 與 Token 限制處理

### Problem Statement
- 業務場景：單篇長文（Markdown/HTML）需切成片段以符合嵌入模型（8191 tokens）限制，並保有語意完整性供向量檢索。
- 技術挑戰：如何分段不切斷語意、是否需要重疊、如何儲存向量與原文關聯。
- 影響範圍：檢索精準度、索引大小、成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 嵌入模型有輸入 Token 上限。
  2. 長文結構不一致。
  3. 未設計索引的標註（tags）與關聯。
- 深層原因：
  - 架構：缺 Ingestion 流程與策略。
  - 技術：未有標準 chunker/overlap 策略。
  - 流程：無標準化匯入工具。

### Solution Design
- 解決策略：使用 Kernel Memory 既有 chunker（預設策略），將長文切成合宜片段，為每片段產生 embedding 與 tags，保存於向量儲存（SimpleVectorDB）與檔案系統。

- 實施步驟：
  1. 內容預處理
     - 細節：移除格式、擷取 Front Matter、抽出純文。
     - 資源：Markdown/HTML parser
     - 時間：1 小時
  2. Chunking+Embedding
     - 細節：預設 chunker；text-embedding-3-large；保留 tags。
     - 資源：Kernel Memory Serverless
     - 時間：1–2 小時

- 關鍵程式碼/設定（索引片段 JSON 節錄）：
```json
{
  "id": "d=post-2024-01-15//p=ccc1cff5...",
  "tags": {
    "user-tags": ["架構師觀點","技術隨筆"],
    "post-url": ["https://columns.../archview-llm/"],
    "post-title": ["[架構師觀點] 開發人員該如何看待 AI 帶來的改變?"]
  },
  "payload": { "text": "在 2023/11, OpenAI 的開發者大會..." },
  "vector": [ -0.0053, 0.0094, ... ] // 3072維
}
```

實際案例：單篇 59,638 bytes 被切為 46 chunks，索引體量約 1.94 MB；全站 2481 records、約 104 MB。
實作環境：Kernel Memory（Serverless）、Azure OpenAI Embedding、SimpleVectorDB。
實測數據：
- 改善前：超過 token 限制無法嵌入。
- 改善後：完整建立片段索引、可被檢索。
- 幅度：100% 解決不可嵌入問題。

Learning Points
- 核心：Chunking 策略、標註與關聯。
- 技能：內容預處理、嵌入調用。
- 延伸：考慮摘要壓縮、Overlap、章節切割；風險：索引膨脹；優化：壓縮與去噪。

Practice Exercise
- 基礎：比較 chunk 大小 500/1000 tokens 的檢索效果（30 分）
- 進階：加入重疊 10–20% 並評估品質（2 小時）
- 專案：為 100 篇文件製作 Ingestion Pipeline（8 小時）

Assessment Criteria
- 功能（40%）：可完整嵌入並檢索
- 品質（30%）：片段語意完整
- 效能（20%）：索引體量與成本
- 創新（10%）：摘要/Overlap 策略

------------------------------------------------------------

## Case #6: 向量儲存選型—以 SimpleVectorDB 完成輕量 PoC

### Problem Statement
- 業務場景：資料量不大（約 2.5k chunks/104MB），希望快速完成 PoC、無外部 DB 相依，壓低維運成本與部署複雜度。
- 技術挑戰：在無向量資料庫服務前提下，仍需支持 Top-K 檢索與 filters。
- 影響範圍：PoC 交付速度、部署便利性、雲端成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 向量 DB 部署/費用對 PoC 不划算。
  2. 量級可由檔案系統承載。
  3. 時間與資源有限。
- 深層原因：
  - 架構：PoC 偏重驗證流程與效果。
  - 技術：需簡化為單執行緒/檔案型索引。
  - 流程：先求可用再擴展。

### Solution Design
- 解決策略：採 Kernel Memory 的 SimpleVectorDB（檔案型），以 Serverless 匯入、Service 提供 /search，後續若放大再替換為 Azure AI Search/Qdrant/Redis。

- 實施步驟：
  1. Builder 建置
     - 細節：WithSimpleVectorDb("memories/")；嵌入與對話模型註冊。
     - 資源：Kernel Memory
     - 時間：1 小時
  2. 部署 Service
     - 細節：Azure App Service、唯讀部署（見 Case #16）。
     - 資源：Docker/.NET
     - 時間：2 小時

- 關鍵程式碼/設定：
```csharp
var memory = new KernelMemoryBuilder()
  .WithAzureOpenAITextGeneration(textCfg, new DefaultGPTTokenizer())
  .WithAzureOpenAITextEmbeddingGeneration(embedCfg, new DefaultGPTTokenizer())
  .WithSimpleVectorDb(@"d:\TempDisk\memories\")
  .Build<MemoryServerless>();
```

實際案例：完成部落格檢索服務，無需外部 DB。
實作環境：C#/.NET、Kernel Memory、Azure App Service。
實測數據：
- 改善前：需部署/管理向量 DB。
- 改善後：0 外部 DB 相依、快速交付。
- 幅度：部署/維運負擔大幅下降（質性）。

Learning Points
- 核心：儲存抽象化、PoC 優先策略。
- 技能：Builder 配置、無依賴部署。
- 延伸：之後切換正式 DB；風險：可靠性/效能有限；優化：引入快取/壓縮。

Practice Exercise
- 基礎：以 SimpleVectorDB 完成 50 篇文件索引（30 分）
- 進階：切換到 Qdrant 並比較延遲（2 小時）
- 專案：完成 DB 切換與資料遷移腳本（8 小時）

Assessment Criteria
- 功能（40%）：檢索可用
- 品質（30%）：配置清晰
- 效能（20%）：在 PoC 規模下穩定
- 創新（10%）：可熱插拔儲存

------------------------------------------------------------

## Case #7: 用 Tags/Filters 實作 ABAC 權限與範圍過濾

### Problem Statement
- 業務場景：向量 DB 不提供 record-level 權限。需避免檢索跨越使用者應見範圍，並可依主題/分類篩選（如 user-tags、categories）。
- 技術挑戰：如何在檢索階段以 tags 實作過濾，滿足 ABAC。
- 影響範圍：資料外洩風險、查詢噪音、合規。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 向量 DB 無 row-level perm。
  2. 索引需攜帶可過濾 metadata。
  3. 缺 filters 語法與布林運算。
- 深層原因：
  - 架構：需以 Tag 為 ABAC 基礎。
  - 技術：Filters → AND/OR 合成。
  - 流程：在 Ingestion 階段決定標記策略。

### Solution Design
- 解決策略：在 ImportText 時寫入 TagCollection（如 user-tags、categories、post-date、post-url），/search 以 filters 實作 AND/OR 過濾，讓不同使用者/主題得到限定結果。

- 實施步驟：
  1. 標籤策略設計
     - 細節：定義關鍵 tags 與授權對應。
     - 資源：ABAC 概念
     - 時間：1 小時
  2. Filters 應用
     - 細節：同物件多值=AND，不同物件=OR。
     - 資源：Kernel Memory filters
     - 時間：0.5 小時

- 關鍵程式碼/設定（Filters 範例）：
```json
// AND：同一物件多值
{ "user-tags": ["microservice", "ASP.NET"] }
// OR：拆成兩個物件
[
  { "user-tags": ["microservice"] },
  { "user-tags": ["ASP.NET"] }
]
```

實際案例：查 OOP 與加上「架構師觀點」過濾後，結果由 30 筆縮至 1 筆。
實作環境：Kernel Memory、SimpleVectorDB、Azure OpenAI。
實測數據：
- 改善前：無過濾，噪音大。
- 改善後：範圍顯著縮小（30→1）。
- 幅度：-96.7% 噪音（示例）。

Learning Points
- 核心：ABAC、Tagging、Filters 布林運算。
- 技能：Tag 規劃與落地。
- 延伸：套用到 user-id 權限；風險：標記策略不當；優化：Ingestion 即寫入權限 Tags。

Practice Exercise
- 基礎：為文件加上 categories 過濾（30 分）
- 進階：表達 (A AND B) OR C 的複合條件（2 小時）
- 專案：導入 user-id 隔離檢索範圍（8 小時）

Assessment Criteria
- 功能（40%）：能限定結果
- 品質（30%）：Tag 結構一致
- 效能（20%）：過濾不明顯拖慢
- 創新（10%）：ABAC 與 filters 結合

------------------------------------------------------------

## Case #8: 成本優化—將 Synthesis 成本轉移至 GPTs（User Pays）

### Problem Statement
- 業務場景：/ask 會把 Top-K 大量文本丟入 GPT-4 生成答案，單次可能 15k tokens，成本昂貴。希望控制後端成本。
- 技術挑戰：如何在不犧牲體驗下縮減供應端支出。
- 影響範圍：營運成本、可持續性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. GPT-4 input $10/1M tokens，輸出 $30/1M tokens。
  2. 單次 /ask 約 15k tokens ≈ $0.15。
  3. 流量一大成本不可控。
- 深層原因：
  - 架構：將 Synthesis 放在後端。
  - 技術：未利用 GPTs Plus 用戶自付機制。
  - 流程：成本未分層。

### Solution Design
- 解決策略：改由 GPTs 前端執行 Synthesis，後端僅提供 /search（嵌入成本低且固定），將大宗推理成本讓使用者的 ChatGPT Plus 訂閱承擔。

- 實施步驟：
  1. 關閉 /ask，僅保留 /search
     - 細節：API 層不使用後端 LLM。
     - 資源：Kernel Memory
     - 時間：0.5 小時
  2. GPTs Instruction 調整
     - 細節：要求每次取回 /search 結果再合成。
     - 資源：GPTs Builder
     - 時間：0.5 小時

- 關鍵程式碼/設定：
```json
// 嵌入成本示例（約 30 tokens）
{ "query": "微服務 資料一致性 維持作法" }
// 30 tokens @ $0.13/M ≈ $0.0000039
```

實際案例：示範查詢由後端 /ask 改為 GPTs+ /search，後端支出幾乎僅嵌入費用。
實作環境：Azure OpenAI、GPTs。
實測數據：
- 改善前：單次 /ask ≈ $0.15 USD。
- 改善後：單次 /search 嵌入 ≪ $0.001 USD。
- 幅度：>99% 成本下降（供應端）。

Learning Points
- 核心：成本拆分、誰付錢模型。
- 技能：路徑切換、成本監控。
- 延伸：企業內部改為部門或人別計費；風險：Plus 限制（3 小時 40 次）；優化：快取與摘要。

Practice Exercise
- 基礎：紀錄單次 /ask 與 /search tokens（30 分）
- 進階：加入快取，重複問答不再重算（2 小時）
- 專案：建立成本儀表板（8 小時）

Assessment Criteria
- 功能（40%）：成本可觀測
- 品質（30%）：路徑切換清楚
- 效能（20%）：延遲不惡化
- 創新（10%）：快取/配額

------------------------------------------------------------

## Case #9: 檢索精準度控制—minRelevance 與 limit 調參

### Problem Statement
- 業務場景：不同問題需要不同廣度/嚴謹度，需調整 minRelevance（閾值）與 limit（Top-K）取捨召回/精準。
- 技術挑戰：如何在雜訊與覆蓋間平衡，避免過多不相關或漏掉關鍵。
- 影響範圍：答案品質與成本（K 越大 Synthesis 越貴）。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 閾值過低→雜訊多；過高→漏召回。
  2. K 過大→成本/延遲高。
  3. 問題難度不同需動態調參。
- 深層原因：
  - 架構：缺全局參數策略。
  - 技術：未搭配 filters。
  - 流程：未建立調參準則。

### Solution Design
- 解決策略：提供預設 minRelevance=0.3 與 limit=5；針對模糊題調低閾值、精準題調高；必要時搭配 filters 縮範圍。

- 實施步驟：
  1. 預設策略與 UI/Instruction
     - 細節：在 Instruction 引導輕度調參。
     - 資源：GPTs/前端
     - 時間：0.5 小時
  2. 觀測與修正
     - 細節：記錄查詢與命中率、人工標註樣本。
     - 資源：Log/簡報
     - 時間：1–2 小時

- 關鍵程式碼/設定：
```json
// 嚴謹查詢（提高精準）
{ "query": "一致性寫模型實作", "minRelevance": 0.5, "limit": 3 }
// 探索查詢（擴大召回）
{ "query": "微服務 報表", "minRelevance": 0.25, "limit": 8 }
```

實測數據（示例）：
- 調高閾值：不相關片段數明顯下降。
- 調低閾值：涵蓋主題更全，但需搭配 filters。
- 幅度：品質與成本可按需調控。

Learning Points
- 核心：召回 vs 精準 vs 成本。
- 技能：觀測與調參。
- 延伸：自適應閾值；風險：過擬合某題型；優化：按主題設置預設值。

Practice Exercise
- 基礎：對同一問題測三組參數（30 分）
- 進階：加入 filters 後比較效果（2 小時）
- 專案：自動化 Grid-Search 小工具（8 小時）

Assessment Criteria
- 功能（40%）：參數生效可觀察
- 品質（30%）：有記錄與結論
- 效能（20%）：成本/延遲平衡
- 創新（10%）：自適應策略

------------------------------------------------------------

## Case #10: 輸出品質控制—強制附來源連結與語言控制

### Problem Statement
- 業務場景：使用者希望答案可追溯（附連結）且以指定語言（繁中）輸出；GPTs 有時未主動附連結或以英文回答。
- 技術挑戰：在 Synthesis 階段精準規範輸出格式與語言。
- 影響範圍：可讀性、信任感、本地化體驗。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Instruction 未明言「附來源」與「語言」。
  2. LLM 默認根據上下文語言回覆。
  3. 來源欄位需對應 tags 中 post-url。
- 深層原因：
  - 架構：無標準輸出規格。
  - 技術：未建立輸出格式模版。
  - 流程：未對每回合強制檢查。

### Solution Design
- 解決策略：在 Instruction/Synthesis Prompt 明確要求「用繁體中文回答並附來源超連結（post-url）」；若找不到則 INFO NOT FOUND。

- 實施步驟：
  1. Instruction 調整
     - 細節：將語言與連結做為硬性規則。
     - 資源：GPTs
     - 時間：0.5 小時
  2. 範例回覆模板
     - 細節：提供回答示例，提醒模型遵循格式。
     - 資源：Prompt
     - 時間：0.5 小時

- 關鍵程式碼/設定：
```text
請用繁體中文回答，並在每個重點後附上來源超連結（使用 post-url）。
若無足夠資訊，請回 INFO NOT FOUND。
```

實際案例：之後不須追問「有這些主題的相關文章？」即可一次產出答案+連結。
實測數據：
- 改善前：常需第二輪追問才補連結。
- 改善後：單輪完成率大幅提升（示例觀察接近 100%）。
- 幅度：對話輪數減半（2→1）。

Learning Points
- 核心：輸出約束、可追溯性。
- 技能：Prompt 模版化。
- 延伸：加入「來源引用編號」；風險：過嚴導致回 INFO NOT FOUND；優化：允許合理補充背景。

Practice Exercise
- 基礎：加上「條列 5 點」並附來源（30 分）
- 進階：輸出中同時給中文摘要與英文關鍵詞（2 小時）
- 專案：定義並實作多種輸出版型（8 小時）

Assessment Criteria
- 功能（40%）：一次回合附連結
- 品質（30%）：語言與格式一致
- 效能（20%）：輪次變少
- 創新（10%）：多版型輸出

------------------------------------------------------------

## Case #11: /ask API—打造不依賴 GPTs 的獨立問答服務

### Problem Statement
- 業務場景：部分場景無法依賴 GPTs（Plus 限制/平台政策），需要自有 UI + /ask 後端完成 RAG 問答。
- 技術挑戰：需自行負擔 Synthesis 成本，並處理延遲/錯誤。
- 影響範圍：產品授權模式、成本、可用性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 平台綁定限制。
  2. 成本從使用者轉回後端。
  3. 需實作完整問答流程。
- 深層原因：
  - 架構：RAG 全包於後端。
  - 技術：/ask 需搭配 ChatCompletion。
  - 流程：監控與配額。

### Solution Design
- 解決策略：使用 Kernel Memory /ask，自動依據檢索結果組合 Facts Prompt，透過 GPT-4 生成，前端顯示答案與來源，建立自有限流與計費。

- 實施步驟：
  1. 問答 API
     - 細節：POST /ask，question、filters、minRelevance。
     - 資源：Kernel Memory Service
     - 時間：1 小時
  2. 前端 UI
     - 細節：輸入問題→loading→答案+來源。
     - 資源：Web 前端
     - 時間：3 小時

- 關鍵程式碼/設定：
```json
// /ask Request
{ "question": "微服務一致性怎麼做？", "filters": [], "minRelevance": 0.3 }
```

實測數據：
- 單次 /ask 約 15k input tokens（示例），≈$0.15。
- 回答品質與 GPTs 類似，但成本由供應端承擔。
- 幅度：可用性↑（不依賴 Plus），成本↑（後端）。

Learning Points
- 核心：獨立服務、成本權衡。
- 技能：API 設計、前後端整合。
- 延伸：企業內部布署；風險：高成本；優化：問題壓縮、快取。

Practice Exercise
- 基礎：製作簡易問答頁面（30 分）
- 進階：加入 filters 與來源顯示（2 小時）
- 專案：建流控與計費模組（8 小時）

Assessment Criteria
- 功能（40%）：問答順暢
- 品質（30%）：錯誤與空結果處理
- 效能（20%）：延遲/吞吐
- 創新（10%）：快取/重用

------------------------------------------------------------

## Case #12: 嵌入模型選型—text-embedding-3-large（3072 維）

### Problem Statement
- 業務場景：需要高品質語意檢索，模型要兼顧準確度與成本，支援 3072 維向量，8k token 輸入上限。
- 技術挑戰：模型品質（MTEB）、維度、價格（$0.13/1M tokens）。
- 影響範圍：檢索品質、索引體量與成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 低品質嵌入→檢索失準。
  2. 維度不足→語意表達受限。
  3. 價格與吞吐需平衡。
- 深層原因：
  - 架構：需統一全站 embedding 模型。
  - 技術：維度不相容問題。
  - 流程：模型升級需重建索引。

### Solution Design
- 解決策略：選 text-embedding-3-large 作為全站統一嵌入，之後一致用此模型產生/查詢；版本升級時整批重嵌入。

- 實施步驟：
  1. 模型評估與決策
     - 細節：MTEB 分數/價格/維度。
     - 資源：OpenAI Docs
     - 時間：0.5 小時
  2. 模型固化與索引建立
     - 細節：一致性嵌入；記錄模型版本。
     - 資源：Ingestion 工具
     - 時間：1–2 小時

- 關鍵程式碼/設定：
```csharp
.WithAzureOpenAITextEmbeddingGeneration(embedCfg, new DefaultGPTTokenizer())
// embedCfg 指向 text-embedding-3-large 部署
```

實測數據：
- 品質：示範查詢回傳高相關片段（0.48 相似度等）。
- 成本：索引階段為一次性；查詢僅對 query 嵌入課費。
- 幅度：檢索品質穩定提升（質性）。

Learning Points
- 核心：單一模型一致性、維度與成本。
- 技能：模型管理、版本治理。
- 延伸：改小模型+rerank；風險：換模型需重建；優化：分層索引。

Practice Exercise
- 基礎：以 3-large 建立 10 篇索引（30 分）
- 進階：比較 3-small vs 3-large 命中率（2 小時）
- 專案：設計模型升級與回滾流程（8 小時）

Assessment Criteria
- 功能（40%）：索引與查詢一致
- 品質（30%）：相關性觀察
- 效能（20%）：成本體感
- 創新（10%）：分層策略

------------------------------------------------------------

## Case #13: 用 Swagger 描述作為 LLM 的「API 使用 Prompt」

### Problem Statement
- 業務場景：LLM 需理解 API 功能/參數語意，否則無法正確使用工具；希望藉由 Swagger 描述提升工具使用成功率。
- 技術挑戰：將人讀的 API 說明轉為 LLM 能「理解」的提示。
- 影響範圍：工具使用率、錯誤呼叫率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Swagger 缺描述→LLM 無從判斷。
  2. 缺範例→無法推斷輸入格式。
  3. 無語義說明→亂帶參數。
- 深層原因：
  - 架構：把 API 說明當 Prompt。
  - 技術：描述用語需自然語言清楚。
  - 流程：維護 Swagger 即維護 Prompt。

### Solution Design
- 解決策略：在 Swagger 中為每個 path/參數加上清楚 description、範例與限制，作為 LLM 工具使用「說明文件 + 提示」。

- 實施步驟：
  1. 撰寫描述
     - 細節：強調語意、閾值範圍、Top-K 含義。
     - 資源：Swagger Editor
     - 時間：1 小時
  2. 測試驗證
     - 細節：多題測試工具呼叫是否合理。
     - 資源：GPTs Builder
     - 時間：1 小時

- 關鍵程式碼/設定：
```yaml
description: "Use this endpoint to retrieve Top-K semantically relevant chunks (0-1 cosine threshold via minRelevance)."
```

實作環境：Swagger/Swashbuckle、GPTs。
實測數據：
- 改善前：工具使用失敗或參數錯置。
- 改善後：帶入 query/minRelevance/limit 正確（示例）。
- 幅度：成功率顯著提升。

Learning Points
- 核心：描述=Prompt；文件即行為。
- 技能：語意化描述、範例。
- 延伸：加入 JSON Schema 驗證；風險：描述含糊；優化：加 usage hints。

Practice Exercise
- 基礎：為一參數撰寫清楚描述（30 分）
- 進階：加入錯誤碼與限制說明（2 小時）
- 專案：對 3 個 API 完成完整 YAML（8 小時）

Assessment Criteria
- 功能（40%）：工具可用性↑
- 品質（30%）：描述清楚
- 效能（20%）：減少錯誤回合
- 創新（10%）：文件即 Prompt 思維

------------------------------------------------------------

## Case #14: Filters 的布林運算（AND/OR）組合查詢

### Problem Statement
- 業務場景：需要表達「(A AND B) OR C」等複合過濾條件，縮小結果範圍。
- 技術挑戰：filters 的表達方式須簡潔且可跨 DB 落地。
- 影響範圍：查詢可控性、噪音抑制。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 缺統一 AND/OR 表達。
  2. 符號化語法不易被 API/LLM 理解。
  3. 需與 Tag 結構一致。
- 深層原因：
  - 架構：filters 要抽象跨 DB。
  - 技術：物件內多值=AND、陣列多物件=OR。
  - 流程：規格化為前後端共識。

### Solution Design
- 解決策略：採 Kernel Memory filters 方案：同一物件內多值為 AND；filters 陣列中的多物件為 OR；以 JSON 原生表達布林邏輯。

- 實施步驟：
  1. 規則宣告
     - 細節：寫在 API 描述與文件。
     - 資源：Swagger/文件
     - 時間：0.5 小時
  2. 範本與示例
     - 細節：提供 3 種常見組合範例。
     - 資源：Postman/Gists
     - 時間：0.5 小時

- 關鍵程式碼/設定：
```json
// ( "microservice" AND "ASP.NET" ) OR ( "架構師觀點" )
{
  "filters": [
    { "user-tags": ["架構師觀點"] },
    { "user-tags": ["microservice", "ASP.NET"] }
  ]
}
```

實測數據：
- 範圍縮減顯著（示例從 30 → 少數）。
- 幅度：噪音下降、精準度上升（質性）。

Learning Points
- 核心：布林邏輯 JSON 化。
- 技能：通用規格制定。
- 延伸：NOT/排除；風險：過濾過度；優化：預設組合模板。

Practice Exercise
- 基礎：用 filters 找出「分類=微服務」的文（30 分）
- 進階：實作 (A AND B) OR (C AND D)（2 小時）
- 專案：前端條件生成器 UI（8 小時）

Assessment Criteria
- 功能（40%）：條件可表達
- 品質（30%）：語意一致
- 效能（20%）：過濾延遲可接受
- 創新（10%）：條件產生器

------------------------------------------------------------

## Case #15: Serverless 索引器—批量匯入 327 篇文章

### Problem Statement
- 業務場景：需快速將 GitHub Pages 上的 Markdown/HTML 文章批量匯入、轉純文、標註 Tags、嵌入並存入向量庫。
- 技術挑戰：內容抽取、Front Matter 解析、批量處理與錯誤復原。
- 影響範圍：索引完整性、日後維運。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 來源格式多元。
  2. 需批量與可重入。
  3. 必須附帶 tags/metadata。
- 深層原因：
  - 架構：建 Ingestion Console 工具。
  - 技術：Serverless 內嵌 Embedding 與向量存取。
  - 流程：版控/CI 整合。

### Solution Design
- 解決策略：以 KernelMemoryBuilder 建 MemoryServerless，解析文章→抽純文→寫 Tags→ImportTextAsync；輸出 memories 檔案樹供部署。

- 實施步驟：
  1. 解析器
     - 細節：Front Matter、純文、URL。
     - 資源：Markdown/HTML Parser
     - 時間：2 小時
  2. 匯入器
     - 細節：TagCollection（user-tags/categories/post-url/title/date）。
     - 資源：Kernel Memory
     - 時間：2 小時

- 關鍵程式碼/設定（節錄）：
```csharp
var tags = new TagCollection();
tags.Add("user-tags", post.Tags.ToList());
tags.Add("categories", post.Categories.ToList());
tags.Add("post-url", post.URL.ToString());
tags.Add("post-date", post.PublishDate.ToString("yyyy-MM-dd"));
tags.Add("post-title", post.Title);

await memory.ImportTextAsync(
  post.Content,
  $"post-{post.PublishDate:yyyy-MM-dd}",
  tags, null, null);
```

實際案例：全站建立 2481 records、約 104MB 索引。
實作環境：.NET Console、Kernel Memory Serverless、Azure OpenAI。
實測數據：
- 改善前：無索引。
- 改善後：完整索引可檢索。
- 幅度：達成可用性 100%。

Learning Points
- 核心：Ingestion 工具化與版控。
- 技能：批量解析與匯入。
- 延伸：CI/CD 自動索引；風險：內容變動需重嵌入；優化：增量索引。

Practice Exercise
- 基礎：匯入 20 篇並生成 tags（30 分）
- 進階：處理 HTML→純文（2 小時）
- 專案：CI 觸發重建索引與部署（8 小時）

Assessment Criteria
- 功能（40%）：批量可用
- 品質（30%）：標註正確
- 效能（20%）：時間可控
- 創新（10%）：自動化流水線

------------------------------------------------------------

## Case #16: 以唯讀部署與「烘焙索引」降低攻擊面（Read-only Service）

### Problem Statement
- 業務場景：不希望雲端服務暴露「匯入/寫入」入口，避免非授權上傳或索引污染；希望把 memories 檔案直接打包進映像後唯讀部署。
- 技術挑戰：剝離寫入 API，確保 /search 仍正常運作。
- 影響範圍：安全性、維運風險、合規。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 公網服務若可寫入→高風險。
  2. 不需線上寫入。
  3. 部署流程可烘焙索引。
- 深層原因：
  - 架構：讀寫分離；本機建索引，上線唯讀。
  - 技術：移除 import 路由。
  - 流程：CI 打包 memories。

### Solution Design
- 解決策略：本機以 Serverless 工具產生 memories/ 索引，Docker 映像包含該目錄；服務端只保留 /search（與 /ask 視情況），刪除寫入路由並權限封鎖寫入路徑。

- 實施步驟：
  1. API 精簡
     - 細節：刪除/關閉 import 類路由。
     - 資源：服務程式碼
     - 時間：1 小時
  2. 映像打包
     - 細節：將 memories/ 加入映像、唯讀掛載。
     - 資源：Dockerfile
     - 時間：1 小時

- 關鍵程式碼/設定（概念）：
```dockerfile
COPY ./memories /app/memories  # 內含索引檔
# 以唯讀方式掛載，或容器啟動用 RO 權限
```

實作環境：Docker、Azure App Service。
實測數據：
- 改善前：雲端可被寫入（風險高）。
- 改善後：只讀部署、攻擊面收斂。
- 幅度：風險顯著下降（質性）。

Learning Points
- 核心：讀寫分離、攻擊面管理。
- 技能：部署策略、安全控制。
- 延伸：搭配 WAF/IP 白名單；風險：索引更新頻度高時流程負擔；優化：增量索引＋版本控管。

Practice Exercise
- 基礎：建立唯讀容器（30 分）
- 進階：寫入路由熔斷與測試（2 小時）
- 專案：建索引→打包→部署流水線（8 小時）

Assessment Criteria
- 功能（40%）：服務可用
- 品質（30%）：無寫入入口
- 效能（20%）：部署穩定
- 創新（10%）：版本與回滾

------------------------------------------------------------

## Case #17: 相似度計算—Cosine Similarity 小工具

### Problem Statement
- 業務場景：需理解向量相似度的意義（夾角越小越相似、cos 越近 1），校驗檢索相似度與分數意義。
- 技術挑戰：避免「距離最遠」誤解成「最不相關」；正交才是不相關（cos=0）。
- 影響範圍：調參與結果判讀。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 對向量幾何誤解。
  2. cos 值解讀混淆。
  3. 未有校驗工具。
- 深層原因：
  - 架構：需有基礎工具支援分析。
  - 技術：數學概念落地。
  - 流程：教學化文檔不足。

### Solution Design
- 解決策略：提供簡易 cosine 工具函式與測例，用於排查與校準 minRelevance 的意義與範圍。

- 實施步驟：
  1. 撰寫函式
     - 細節：dot/(||a||*||b||)。
     - 資源：C# 或 Python
     - 時間：0.5 小時
  2. 測例對照
     - 細節：相同/正交/反向向量。
     - 資源：單元測試
     - 時間：0.5 小時

- 關鍵程式碼/設定（C# 範例）：
```csharp
double Cosine(double[] a, double[] b) {
  double dot=0, na=0, nb=0;
  for (int i=0;i<a.Length;i++){ dot+=a[i]*b[i]; na+=a[i]*a[i]; nb+=b[i]*b[i]; }
  return dot / (Math.Sqrt(na)*Math.Sqrt(nb) + 1e-9);
}
```

實測數據：
- 正交測例 cos≈0；同向 cos≈1；反向 cos≈-1。
- 有助於設定 minRelevance（如 0.3）。

Learning Points
- 核心：cosine 幾何意義。
- 技能：基礎數學與工具化。
- 延伸：比較 Inner Product/距離；風險：高維現象；優化：標準化向量。

Practice Exercise
- 基礎：對三組向量計算 cos（30 分）
- 進階：以隨機高維向量測試分布（2 小時）
- 專案：做相似度可視化工具（8 小時）

Assessment Criteria
- 功能（40%）：計算正確
- 品質（30%）：程式簡潔
- 效能（20%）：高維仍穩定
- 創新（10%）：視覺化

------------------------------------------------------------

## Case #18: 避免多餘 Query 重寫與成本爆炸

### Problem Statement
- 業務場景：有人想先用 GPT-4 對 Query 做「智慧重寫」再去嵌入檢索；但 GPT-4 重寫本身就昂貴，得不償失。
- 技術挑戰：平衡「更好 Query」 vs 「成本/延遲」。
- 影響範圍：每次查詢成本、響應時間、平台承載。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. GPT-4 重寫一次就可能上千 tokens。
  2. 嵌入成本原本極低（幾十 tokens）。
  3. 得不償失。
- 深層原因：
  - 架構：多餘步驟未審視。
  - 技術：未用低成本模型/規則處理。
  - 流程：未定準入門檻。

### Solution Design
- 解決策略：預設不做重寫；確有必要時用更低成本規則化方法（停用詞移除/簡短化），或以便宜模型改寫。嚴格度→靠 minRelevance/filters 調。

- 實施步驟：
  1. 關閉預設重寫
     - 細節：Pipeline 不啟用 GPT-4 重寫。
     - 資源：後端配置
     - 時間：0.5 小時
  2. 最小必要優化
     - 細節：關鍵詞抽取/去雜訊。
     - 資源：輕量 NLP
     - 時間：1 小時

- 關鍵程式碼/設定（概念）：
```text
// Do: stop words removal, length cap
// Avoid: GPT-4 paraphrase before embedding
```

實測數據：
- 改善前：重寫成本遠高於嵌入本身。
- 改善後：單次查詢成本近似嵌入成本。
- 幅度：>99% 成本節省（相對重寫策略）。

Learning Points
- 核心：成本覺察、步驟消減。
- 技能：極簡 NLP、規則處理。
- 延伸：以便宜模型改寫；風險：查全率略降；優化：必要時人工同義詞表。

Practice Exercise
- 基礎：對 Query 做停用詞移除（30 分）
- 進階：比較改寫/不改寫的召回（2 小時）
- 專案：做成本/品質 A/B 測（8 小時）

Assessment Criteria
- 功能（40%）：步驟可開關
- 品質（30%）：品質影響可量測
- 效能（20%）：成本降低
- 創新（10%）：輕量替代方案

------------------------------------------------------------

## Case #19: 提升 GPTs 主動性—一次回合完成「答案+連結」

### Problem Statement
- 業務場景：GPTs 常先給摘要，待追問才附文章清單，導致多輪互動；希望一次就給答案與連結。
- 技術挑戰：讓模型主動在第一輪就同時整合。
- 影響範圍：對話效率、用戶體驗。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Instruction 未明確要求「同時給答案+連結」。
  2. 模型採「二段式回覆」習慣。
  3. 未強制工具呼叫時機。
- 深層原因：
  - 架構：交互策略不足。
  - 技術：Prompt 未明訂 SLA。
  - 流程：未監看對話輪數。

### Solution Design
- 解決策略：在 GPTs Instruction 明確要求「每次回答同步附上來源連結，且必要時立即呼叫檢索 API」，並給範例回覆格式。

- 實施步驟：
  1. Instruction 加強
     - 細節：一句話要求同回合給出清單。
     - 資源：GPTs Builder
     - 時間：0.5 小時
  2. 模板示例
     - 細節：答案＋連結並列。
     - 資源：Prompt
     - 時間：0.5 小時

- 關鍵程式碼/設定：
```text
請在每次回答中，同步提供摘要與來源連結列表（以 post-url 超連結呈現），不需等待追問。
```

實測數據：
- 改善前：常需兩回合。
- 改善後：一次回合完成率顯著提升。
- 幅度：對話輪數減半（示例）。

Learning Points
- 核心：交互 SLA 與 Prompt 對齊。
- 技能：Instruction 設計。
- 延伸：條列化與排序；風險：過度嚴格導致 INFO NOT FOUND；優化：允許降級策略。

Practice Exercise
- 基礎：為常見題型撰寫模板（30 分）
- 進階：加入「排序規則」（最相關優先）（2 小時）
- 專案：分析前後輪數與滿意度（8 小時）

Assessment Criteria
- 功能（40%）：一次回合含連結
- 品質（30%）：輸出一致
- 效能（20%）：輪數下降
- 創新（10%）：排序與版型

------------------------------------------------------------

## Case #20: Demo 到生產的決策—GPTs 介面 vs 自建 UI

### Problem Statement
- 業務場景：選擇以 GPTs 作為介面（Plus 用戶自付）或自建 UI（後端承擔成本），關係到擴散速度、成本與掌控度。
- 技術挑戰：兩者在行為、成本、可維護性的取捨。
- 影響範圍：用戶觸達、治理、未來擴充。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. GPTs 有 Plus 門檻與配額。
  2. 自建 UI 需承擔 /ask 成本。
  3. 對談上下文處理難度不同。
- 深層原因：
  - 架構：前後端責任切割。
  - 技術：對談上下文與工具調用控制。
  - 流程：成本與授權政策。

### Solution Design
- 解決策略：PoC/小範圍先用 GPTs（快速、低後端成本），大規模或受限於平台時再轉自建 UI + /ask；並同時準備 /search 作為公共檢索能力。

- 實施步驟：
  1. PoC 上線（GPTs）
     - 細節：Instruction+Action 完成。
     - 資源：GPTs
     - 時間：1 天
  2. 生產規劃（自建）
     - 細節：/ask、流控、計費、監控。
     - 資源：後端/前端/FinOps
     - 時間：視規模

- 關鍵程式碼/設定：
```json
// 兩路並存：/search（公共） + /ask（內部/特權）
```

實測數據：
- PoC：快速擴散、零後端 Synthesis 成本。
- 生產：高掌控、可客製、但成本回到供應端。
- 幅度：取捨依目標而定。

Learning Points
- 核心：路徑選擇與時機。
- 技能：平台化 vs 自營。
- 延伸：Agent 化整合；風險：依賴單一平台；優化：雙軌維持。

Practice Exercise
- 基礎：整理兩種模式的優缺點（30 分）
- 進階：設計成本模型與門檻（2 小時）
- 專案：實作雙軌方案與降級機制（8 小時）

Assessment Criteria
- 功能（40%）：兩種模式皆可行
- 品質（30%）：決策依據明確
- 效能（20%）：成本/體驗平衡
- 創新（10%）：雙軌/降級設計

------------------------------------------------------------

案例分類
1) 按難度分類
- 入門級（適合初學者）
  - Case 6, 9, 10, 12, 13, 14, 16, 18, 19
- 中級（需要一定基礎）
  - Case 1, 2, 3, 5, 7, 11, 15, 20
- 高級（需要深厚經驗）
  - Case 4, 8

2) 按技術領域分類
- 架構設計類：Case 1, 6, 11, 16, 20
- 效能優化類：Case 5, 8, 9, 18
- 整合開發類：Case 2, 3, 13, 15
- 除錯診斷類：Case 4, 9, 16, 17, 19
- 安全防護類：Case 7, 16, 14

3) 按學習目標分類
- 概念理解型：Case 3, 5, 12, 17
- 技能練習型：Case 2, 6, 9, 10, 13, 14, 15
- 問題解決型：Case 1, 4, 7, 8, 11, 16, 18, 19
- 創新應用型：Case 20

------------------------------------------------------------

案例關聯圖（學習路徑建議）
- 建議先學：
  1) Case 12（嵌入模型與維度/成本概念）
  2) Case 17（cosine 相似度與分數解讀）
  3) Case 5（Chunking 與 Ingestion 基礎）
- 接著：
  4) Case 15（Serverless 索引器，完成批量匯入）
  5) Case 6（SimpleVectorDB 選型，快速 PoC）
  6) Case 3（/search 設計與 Top-K 回傳）
  7) Case 13（Swagger 作為工具使用 Prompt）
  8) Case 2（GPTs Custom Action 整合）
- 再強化：
  9) Case 10（輸出品質：語言＆來源）
  10) Case 9（minRelevance/limit 調參）
  11) Case 14（Filters 布林運算）
  12) Case 7（ABAC 與安全過濾）
- 完整端到端：
  13) Case 1（整體 RAG 助理落地）
  14) Case 4（Synthesis 模板防幻覺）
- 規模化與成本：
  15) Case 8（成本優化：User Pays）
  16) Case 16（唯讀部署與攻擊面縮減）
  17) Case 19（一次回合完成：體驗優化）
  18) Case 11/20（/ask 獨立服務 與 路徑決策）

依賴關係提示：
- Ingestion（Case 5/15）→ Retrieval（Case 3/6/14/7/9/13）→ Synthesis（Case 4/10/19）
- 成本與部署（Case 8/16）與路徑決策（Case 11/20）在端到端跑通後再優化。

以上 18 個案例以實戰為導向，涵蓋從概念、實作到運維與成本治理的完整學習路徑。