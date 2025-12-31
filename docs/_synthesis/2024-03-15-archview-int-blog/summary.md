---
layout: synthesis
title: "替你的應用程式加上智慧! 談 RAG 的檢索與應用"
synthesis_type: summary
source_post: /2024/03/15/archview-int-blog/
redirect_from:
  - /2024/03/15/archview-int-blog/summary/
postid: 2024-03-15-archview-int-blog
---

# 替你的應用程式加上智慧! 談 RAG 的檢索與應用

## 摘要提示
- 目標與動機: 以自身20年、327篇、400萬字的部落格為知識庫，實作RAG讓讀者以對談方式高效檢索與運用內容
- Demo 展示: 透過自製 GPTs 搭配檢索服務，完成主題彙整、跨文章導讀、條列原則與引用來源的問答體驗
- 架構選型: 以前端 GPTs 做 Synthesis，後端 Kernel Memory 提供 Retrieval，離線批次完成 Ingestion
- RAG 三階段: Ingestion(切塊/嵌入/索引)、Retrieval(相似度與過濾)、Synthesis(LLM結合查詢與脈絡生成)
- 向量與嵌入: 用 text-embedding-3-large 將文字轉為3072維向量，透過 cosine similarity 找語意相近片段
- Kernel Memory 實作: 提供 /search 與 /ask API、Serverless/Service 模式、簡易向量檔案儲存與 Tags 過濾
- 成本與效能: 檢索便宜、生成昂貴；用 GPTs 由使用者承擔生成成本，或自架 /ask 由服務端付費
- 安全與過濾: 以 Tags + Filters 實作 ABAC 式授權過濾，建立使用者/類別/主題等多維檢索條件
- 資料觀點演進: 從 RDB(表格) → NoSQL(文件) → VectorDB(向量索引)，語意查詢標準化為向量搜尋
- 架構師視角: AI 時代的基礎能力轉移到 prompt、function calling、embedding、vector search 與 RAG 組裝

## 全文重點
作者以自身部落格作為知識庫，實作一個能對談檢索的 AI 助手，核心採 RAG 流程：以 Kernel Memory 離線完成文章切塊、向量化與索引(Ingestion)；線上以 /search 檢索語意相近片段(Retrieval)；並在前端由 GPTs 彙整結果並附上來源連結(Synthesis)。示範情境包含：回顧站點發展史、微服務主題彙整、家用網路/NAS 實作建議等，顯示語意檢索優於關鍵字，且能跨文連結、條列原則與回避臆造。

技術面，作者拆解 Retrieval 步驟：將使用者 Query 轉嵌入向量，於向量庫以 cosine similarity 取 Top-K，回復原文片段。以 OpenAI text-embedding-3-large 建立3072維空間，強化語意相近度。Synthesis 面以 GPTs 的 Custom Actions (OpenAPI/Swagger) 觸發自家 API，將檢索結果與 Query 合成可讀答案；亦可選擇 Kernel Memory 的 /ask 直出答案(但生成成本由服務方承擔)。成本上，檢索便宜、生成昂貴；若用 GPTs，LLM 成本由使用者訂閱負擔，否則需自付 GPT4 tokens。

Ingestion 面，作者用 Kernel Memory 的 Serverless 模式將 Markdown 轉純文字，設定 Tags(如 user-tags、categories、post-url/date/title)，以 SimpleVectorDB 儲存為 JSON，利於快速 PoC 與離線建索；未來以 CI/CD 併發佈網站與索引。Filters 以 AND/OR 組合實現 ABAC 式授權與主題過濾，文件強調以 Tags 作為安全與檢索的一致機制。

宏觀觀點，AI 正將資料檢索從「條件/關鍵字」轉為「語意/向量」，資料庫思維亦由 RDB(表格) → NoSQL(文件) → VectorDB(語意索引) 演進；向量是 AI 世界的共通索引，與文件/實體存放協作，形成語意檢索 + 精準過濾的新常態。應用模式亦由 App 搜尋轉向 Agent 對談與個人化操作；費用與個資策略因平台而異(GPTs/自架/端側)。對架構師而言，AI 世代的新基礎能力在於 RAG 組裝、模型接口、嵌入/向量庫、權限與成本設計，目標不是與 AI 競賽，而是駕馭其能力以創造更高價值。

## 段落重點
### 0. 寫在前面
作者長年以較長、深度的技術文記錄解題與驗證，雖不易消化，但常年仍具參考價值。藉 GPTs 與 RAG，可將龐大舊文轉化為可對談使用的知識庫，彌補可讀性與檢索效率不足。部落格累積20年、327篇、400萬字，題材集中架構與軟體設計，具做 RAG 的完整資料掌控與格式優勢；此次以 ChatGPT 作為介面、Azure OpenAI 為模型、Kernel Memory 為後端檢索，實作部落格 GPTs，讓讀者能以對談方式完成查詢、導讀、彙整與多語表達。

### 1. "安德魯的部落格" GPTs - Demo
作者回顧部落格20年演進，盼以 AI 提供互動式知識輸出。Demo 展示三類場景：(1) 梳理站點發展史：跨系統遷移、轉址、擴充套件、網路/儲存方案等，AI 能整理無一致標籤的散文式記錄；(2) 微服務主題：從 API 化引發的報表、資料一致性、整合 SDK 等議題，AI 先提原則摘要，再補充文章連結；(3) 家用網路/NAS：以開發者身分需求，AI 提建置與容器服務建議並給出相關文章。整體回應準確且能避開臆造，但需在指示上強化「同時附連結」等行為。作者提供完整對話封存供參考。

### 2, 部落格檢索服務
作者採三段式 RAG：Synthesis 由 GPTs 負責(含指令與 Custom Actions)；Retrieval 用 Kernel Memory 提供 /search；Ingestion 以 Kernel Memory Serverless 離線建索。流程取材於 Applied LLMs Mastery 課程之 RAG 架構圖。GPTs 透過上傳的 OpenAPI/Swagger 學會呼叫檢索 API，將使用者 Query 與檢索結果組合生成答案；也可改用 Kernel Memory 的 /ask 直出回答。作者說明 RAG 挑戰(資料導入、嵌入效率、向量庫抉擇、知識更新等)，強調理解原理勝於依賴工具，並提醒成本與安全是工程評估重點。

### 2-1, RAG 資料檢索的應用（Synthesis）
對談中可見 GPTs 觸發外部 API(andrewblogkms.azurewebsites.net)，攜帶 query/minRelevance/limit 等參數。Swagger 的描述文字同時是 LLM 了解語意與使用時機的提示。檢索回來的是多筆 chunk(含text、relevance、tags)，GPTs 依 API 結構理解並彙整答覆。作者以手動 prompt 還原 Synthesis：將「ask/facts/answer」定型，要求以來源連結回覆，效果與 GPTs 相近。此過程展示了 Function Calling + 檢索增強的具體操作，也凸顯可在往後以程式碼將樣板自動化。

### 2-2, 語意的檢索 - 向量搜尋（Retrieval）
Retrieval 拆解為：Query → 向量化 → 相似度計算 → Top-K + 過濾 → 還原原文。關鍵在 embedding 將文字投影至多維語意空間；作者以圖例解釋「維度=語意」，相似度可用 cosine similarity。使用 OpenAI text-embedding-3-large(3072 維)，不同模型間向量不相容，需全庫一致。Kernel Memory 的 /search 接收 query/filters，回傳 citations/partitions；/ask 則多一步以 GPT4 合成答案。成本上：嵌入便宜、生成昂貴；用 GPTs 可把生成費用轉由用戶訂閱負擔，自架 /ask 則由服務端承擔，需留意 token 消耗。

### 2-2-1, Text Embedding
說明嵌入將文字映射至語意空間之向量，透過多維度表徵語意，進而以幾何方式比較相似度。以簡圖示意二維(風格/物種)理解，再過渡到實務：將長文切塊(chunking)後嵌入，查詢時將 Query 嵌入後比對最接近片段。相似度常以 cosine；需注意「相反方向不等於不相關」與「正交才是不相關」。最後指出模型輸入 token 上限與切塊策略的重要性，避免截斷語意；Kernel Memory 內建多種 chunking 策略可選。

### 2-2-2, Retrieval
以實際 API 範例演示 /search：Query「微服務 資料一致性 維持作法」→ 回傳多文件之 partitions(含 relevance 與文章 tags)。若改用 /ask，則由 Kernel Memory 在檢索後串 GPT4 直接生成答案，結構更精簡，但成本轉由服務端承擔。作者比較兩法：GPTs 前端體驗好且轉嫁生成成本；/ask 方便內嵌於自家系統。並提醒：一次回答可能含萬級 token，費用要精算，同時應控制上下文與 Top-K 數以降低開銷。

### 2-2-3, Start Coding
檢視 Kernel Memory Serverless 介面(SearchAsync/AskAsync)與資料結構(SearchResult/MemoryAnswer/Citation/Partition/MemoryFilter)。官方例程顯示：先 ImportText 建索，再 AskAsync 問答；底層會用檢索結果構成包含 Facts 的 prompt，再交給指定 LLM 生成。作者以相同 prompt 在 ChatGPT 測試，發現可微調語言/口吻等行為，利於在實作前快速驗證提示工程，縮短反覆開發成本。

### 2-3, 建立文章向量化的資料庫（Ingestion）
Ingestion 三步：Chunking、Embedding、Indexing。text-embedding-3-large 的輸入上限(8191 tokens)迫使需合理切塊；MTEB 指標與價格也影響模型選擇。作者採 SimpleVectorDB 以 JSON 存放嵌入，利於 PoC 與離線佈版；以 CI/CD 將部落格與索引同步釋出。程式方面，Serverless 模式用 KernelMemoryBuilder 設定 AzureOpenAI 文生/嵌入、Tokenizer 與 SimpleVectorDb，迭代讀取 Markdown，抽 Front Matter 為 Tags(user-tags/categories/post-url/date/title)後 ImportText。Filters 支援 AND/OR 組合，並據 Tags 實作 ABAC 式授權與主題過濾。

### 3, AI 改變了內容搜尋方式
作者從傳統關鍵字/全文檢索的侷限，轉向以嵌入空間進行語意檢索，將「語意」轉為可運算的向量，搜尋成為幾何近鄰問題。進而拓展應用：不僅問題找文本，也可用使用者向量找歌單(Spotify 的 two-tower)、電商個人化推薦等。RAG 正式將語意檢索標準化為向量搜尋；資料仍需以 RDB/NoSQL 保存原文與屬性，向量是 AI 世界的共通索引。對工程與產品而言，語意檢索降低了專用查詢語言門檻，促進用戶以自然語言獲取知識。

### 3-1, 從「表格」到「空間」的演進
三代資料思維：RDB(表格/Schema/Join，效率與精確優先)；NoSQL(文件/物件貼近應用，減少 Join，利分散式)；VectorDB(以向量為語意索引，配合文件/關聯儲存做內容還原與過濾)。新世代不是取代而是疊加：向量庫解決語意近鄰，NoSQL/RDB 提供精準屬性與交易一致性。向量讓語意搜尋標準化並與多媒體/多模態共用索引空間，形成「向量索引 + 文件狀態」的資料架構新常態。

### 3-1-1, RDB: 表格為主
以表格與 SQL 操作為核心，依賴 Schema 與正規化以追求一致性與效能；但應用側常須大量 Join 才能回到業務語義，模型與資料結構之間存在心智落差。此模式擅長結構明確與交易一致性強的場景，但在跨語意檢索與非結構化內容上負擔較重。

### 3-1-2, NoSQL: 文件為主
以文件/物件為中心，資料模型貼近應用，減少 Join 與 ORM 摩擦；支援大規模水平擴展與靈活 Schema 演進，適合雲原生與高併發應用。查詢多為投影/過濾/管線化，降低複雜查詢語法依賴，但對「語意」仍需外部機制補強。

### 3-1-3, VectorDB: 以向量為索引
將文本/圖像等嵌入為向量索引，解決「語意近鄰」問題，檢索以相似度而非關鍵字；但無法還原原文，需結合 RDB/NoSQL 提供內容與屬性過濾。向量庫不取代傳統庫，而是使語意檢索標準化，特別適合與文件型存儲協作成「語意檢索 + 精準過濾」。

### 3-1-4, 資料庫世代的改變
三者對應操作單位：RDB(欄位/變數)、NoSQL(文件/物件)、VectorDB(語意/向量)。AI 時代的基礎元件是：嵌入模型、向量資料庫、LLM 生成；RAG 將其組裝成可用的檢索增強解決方案。工程重心從自製搜尋演算法轉移到模型選擇與資料編目、成本/安全策略。

### 3-2, 從「條件」到「語意」的查詢
RDB 查詢依賴 SQL 與嚴密 Schema；NoSQL 則強調投影/過濾與管線處理。進入向量世界後，查詢轉為「問題/使用者/物件」的嵌入再比對，技術重點從語法轉為「嵌入與模型」品質；自然語言/Prompt 成為主要接口。工程師需關注 Top-K、過濾條件、上下文長度與成本，將語意檢索與屬性過濾合理拼裝。

### 3-3, 從「APP」到「AGENT」的操作
介面選擇影響能力與成本：Chat 介面自帶上下文與個人化但需控管 token；自建問答 UI 較易控費但體驗較單向。費用分擔亦不同：用 GPTs 由使用者訂閱負擔生成費，自架 /ask 由服務端承擔，端側 LLM 則轉為用戶算力/電費。趨勢上，從 App 檢索走向 Agent 個人化協作，各大平台(GPTs/Copilot/Siri/Assistant)競逐；若要快速驗證與導入，先以平台化整合 API 是高效選擇。

### 4, 結論
AI 時代的基礎能力已升級：從資料結構/演算法與 OOP，擴展到 prompt engineering、function calling、embedding、vector search 與 RAG 組裝。架構師價值在於選擇與編排正確組合，而非與 AI 競速。作者以一季時間完成多個 PoC，驗證以 GPTs + Kernel Memory 打造「可對談的知識庫檢索」行得通，並在成本、安全、效能、維運與體驗間取得平衡。AI 不會淘汰長年技術累積，反能放大既有內容價值；關鍵是用對方法，讓 AI 成為你最強大的工具與夥伴。

## 資訊整理

### 知識架構圖
1. 前置知識
- 基礎 NLP/LLM 概念（Prompt、Token、Embedding）
- 向量與相似度（內積、Cosine similarity 的直覺）
- 雲端與 API 基礎（OpenAPI/Swagger、REST、認證）
- 基本資料庫觀念（RDB/NoSQL 與索引觀念）
- .NET/C# 與 Azure（若要重現文中 PoC）

2. 核心概念（3-5 個）
- RAG 三階段：Ingestion（切塊與向量化）→ Retrieval（語意搜尋）→ Synthesis（LLM 生成與彙整）
- Embedding 與向量檢索：以語意空間比對 Query 與文件 chunk 的相近度（Top-K）
- GPTs + Custom Actions：以 OpenAPI 模式讓 GPTs 調用外部檢索 API
- Kernel Memory：提供檔案匯入/向量化/檢索的服務與 Serverless 模式（/search、/ask）
- Tags/Filters 與安全：以標籤做 ABAC 式授權與查詢過濾（AND/OR）

3. 技術依賴
- 模型：Text Embedding（OpenAI text-embedding-3-large）、ChatCompletion（GPT‑4）
- 基礎設施：Azure OpenAI、Azure App Service（部署檢索服務）
- 檢索框架：Microsoft Kernel Memory（Service 模式與 Serverless 模式）
- 向量儲存：Azure AI Search/Qdrant/Elastic/Redis/PostgreSQL 或 SimpleVectorDB（PoC）
- OpenAPI/Swagger：讓 GPTs 正確 Function Calling 到 /search 或 /ask

4. 應用場景
- 企業知識庫/FAQ/文件問答的語意檢索與總結
- 技術部落格/產品文件的主題彙整、導讀與多語回覆
- 微服務與開發治理文件的查詢輔助（原則、模式、連結）
- 具資料授權需求的內部檢索（以 Tags/Filters 施作 ABAC）

### 學習路徑建議
1. 入門者路徑
- 了解 RAG 概念與流程（Ingestion/Retrieval/Synthesis）
- 實測一個 Embedding API，把短文轉向量並做 cosine 相似度比對
- 用 Kernel Memory 的 /search 範例啟動最小可行檢索服務
- 讀 Applied LLMs Mastery 2024：Week 4 RAG 章節

2. 進階者路徑
- 練習 Chunking 策略（段落切分、重疊、摘要化）與 Top‑K 調參
- 導入 Tags/Filters，嘗試 ABAC 式授權與多條件過濾
- 在 GPTs 中掛 Custom Actions（OpenAPI schema 描述周全），優化指令與回答模板
- 比較不同向量庫（Azure AI Search/Qdrant/Elastic/Redis）成本與效能

3. 實戰路徑
- 建立資料管線：離線 Ingestion（向量化、索引）→ 上線 Retrieval API → 前端 GPTs 或自有 UI
- 成本治理：量測 Embedding/GPT-4 token 消耗，控制 minRelevance、limit、facts 上限
- 部署與維運：Azure App Service + CI/CD，確保只讀檢索服務、資料更新流程
- 安全與稽核：使用 Tags 施作 user-based 檢索過濾，規劃存取與記錄

### 關鍵要點清單
- RAG 三階段管線: Ingestion、Retrieval、Synthesis 的清楚分工與邊界 (優先級: 高)
- Embedding 模型選擇: text-embedding-3-large（3072 維、8k tokens 輸入上限、較高準確度但成本較高） (優先級: 高)
- Chunking 策略: 依段落/重疊切塊，避免語意斷裂並兼顧 token 上限 (優先級: 高)
- 相似度與 Top-K: 使用 cosine similarity 與 minRelevance、limit 調參以控品質/成本 (優先級: 高)
- Kernel Memory 核心 API: /search 做檢索、/ask 做檢索+生成（含引用來源） (優先級: 高)
- GPTs Custom Actions: 以 OpenAPI/Swagger 讓 GPTs 自主決定何時呼叫外部 API (優先級: 高)
- Tags/Filters 與 ABAC: 以標籤做使用者層級的檢索過濾，支援 AND/OR 組合 (優先級: 高)
- 成本治理: Embedding 便宜、GPT-4 昂貴；控制 facts 數量與上下文長度 (優先級: 高)
- Serverless 與 Service 模式: MemoryServerless（本機匯入/測試）與雲端檢索服務的取捨 (優先級: 中)
- 向量庫選型: Azure AI Search/Qdrant/Elastic/Redis/PostgreSQL vs SimpleVectorDB（PoC） (優先級: 中)
- Prompt/Synthesis 模板: 將 facts、原則與問題組合成穩定回覆格式（含來源鏈結） (優先級: 中)
- 安全最佳實務: 將 KM 當私有後端、以使用者身分標記與過濾、HTTPS/網段限制 (優先級: 中)
- 微服務文件用例: 以語意檢索彙整一致性、報表、SDK 等跨文檔主題 (優先級: 中)
- 架構決策與依賴: GPTs 作前端對談、KM 作檢索、Azure OpenAI 提供模型 (優先級: 中)
- 未來趨勢: 查詢從條件到語意、介面從 App 到 Agent，資料層從表格到向量索引 (優先級: 低)
