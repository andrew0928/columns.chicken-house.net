# 替你的應用程式加上智慧! 談 RAG 的檢索與應用

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 RAG（Retrieval-Augmented Generation）？
- A簡: RAG 將「檢索」與「生成」結合：先找語意相近內容，再用 LLM 依據上下文生成答案，無需重新訓練模型。
- A詳: RAG 是一種將外部知識檢索（Retrieval）與大語言模型生成（Generation）結合的應用模式。流程包含三步：Ingestion（內容切塊與向量化）、Retrieval（將查詢轉成向量，做相似度搜尋，取回 Top-K 片段）、Synthesis（把查詢與取回片段一起交給 LLM，生成可讀答案）。它的價值在於用即時、可更新的外部資料增強 LLM 的回覆，同時避免昂貴的模型微調。適用情境如企業知識庫問答、文件導讀、跨語言導讀、法規或技術文檔摘要等。文章中以 GPTs + Kernel Memory + Azure OpenAI 打造的部落格問答服務正是典型 RAG。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, B-Q1, B-Q2

Q2: 什麼是 Embedding 與 Embedding Space？
- A簡: Embedding 將文字轉成高維向量；Embedding Space 是語意坐標系，向量距離代表語意相近度。
- A詳: Embedding 是把字串（或其他資料型態）轉換為高維向量的過程，讓語意相似的內容在向量空間彼此接近。Embedding Space 可視為多維語意空間，每個維度代表某種語意特徵（實務上不具名），資料點（向量）位置描述其語意屬性。RAG 透過把內容（chunks）與查詢（query）都轉成向量，再用相似度（如 cosine similarity）比對，找出 Top-K 相關片段。文中示範使用 OpenAI text-embedding-3-large（3072 維、$0.13/1M tokens）將部落格文章轉向量並索引。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, A-Q4

Q3: 向量資料庫（Vector DB）是什麼？
- A簡: 儲存與索引向量的資料庫，用以高效相似度搜尋（Top-K），常搭配標籤過濾。
- A詳: 向量資料庫以嵌入向量為索引主體，支援高效的近鄰搜索（ANN/Top-K）。在 RAG 中，文件經切塊與向量化後寫入 Vector DB，查詢時將 query 向量與庫中向量比對，回傳最相關片段。同時可用標籤（Tags/Filters）進行屬性過濾（AND/OR）以提升精準度與安全性。Kernel Memory 支援 Azure AI Search、Qdrant、PostgreSQL、Elastic、Redis，亦有 SimpleVectorDB（開發/測試用）。實務上常「NoSQL 存原文 + VectorDB 存向量索引」協作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, A-Q14, B-Q5

Q4: RAG 的三大組件差在哪裡：Ingestion、Retrieval、Synthesis？
- A簡: Ingestion 建索引；Retrieval 找相似片段；Synthesis 用 LLM 生成答案，整合上下文。
- A詳: Ingestion 負責「準備資料」：文件切塊（Chunking）、向量化（Embedding）、寫入索引（Vector DB）。Retrieval 處理「精準找片段」：查詢向量化、相似度比對（如 cosine）、Top-K 擷取、依標籤過濾。Synthesis 則「整合與生成」：把 Query 與 Top-K 片段一併餵給 LLM，透過系統化提示（Facts + 指令 + Question）生成可讀答案。文中以 GPTs 做 Synthesis、Kernel Memory 提供 Retrieval、Serverless 程式將文章 Ingestion。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, B-Q7

Q5: 為什麼選 RAG 而非微調（Fine-tuning）？
- A簡: RAG 即時接入外部知識、成本低、維護簡單；微調昂貴且更新慢。
- A詳: 微調需重訓模型，成本高、迭代慢，且不易持續更新知識。RAG 則讓 LLM 在推論時外掛最新資料：資料變更只需重新 Ingestion，Retrieval 即可取回最新片段，Synthesis 再生成答案。對知識密集、變動頻繁的應用（文件庫、FAQ、內部規範），RAG 更具效益。文中部落格 RAG 以幾百篇文章為知識庫，透過 Embedding 與 Vector 檢索，無需動到模型權重即可持續擴充。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, B-Q8

Q6: 什麼是 Chunking？為什麼重要？
- A簡: Chunking 是切段策略，兼顧語意完整與模型長度限制，影響檢索精準度。
- A詳: Embedding 模型有最大輸入長度（如 8k tokens），長文須切段處理。良好 Chunking 應沿語意邊界切割（如段落），必要時做重疊（overlap），避免語意被切碎；也可先摘要再切。Chunking 影響三件事：向量語意品質、檢索精準度（Recall/Precision）、Synthesis 成本（Token 累積）。Kernel Memory 內建多種切塊策略並可擴充，文中 PoC 以預設值完成快速上線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, D-Q2, C-Q7

Q7: Cosine 相似度與距離有何不同？為何常用 Cosine？
- A簡: Cosine 比較夾角，反映方向相似度；距離比較座標距離，易受大小影響。
- A詳: 相似度可用距離（如歐式距離）或夾角（Cosine）。距離受向量長度影響，Cosine 著重方向（語意）一致性，更符合「語意相近」的直覺，常見於文本檢索。Cosine 值範圍 -1~1，越接近 1 代表越相似；0 代表正交（不相關）；-1 表相反方向（不代表最不相關只是反向）。RAG 檢索常用 Cosine 排序，再配合 minRelevance（閾值）與 Top-K 控制輸出量。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q2, B-Q2

Q8: 什麼是 Top-K 檢索？minRelevance 有何用途？
- A簡: Top-K 取最相似的前 K 片段；minRelevance 設相似度下限過濾雜訊。
- A詳: 向量檢索會按相似度排序取前 K 個（如 K=5、10、30），稱 Top-K，數值越大可提升 Recall 但會增加 Synthesis 成本（更多 Tokens）。minRelevance 為相似度過濾閾值（如 0.3），可去除弱相關片段，提升 Precision。兩者互為拉鋸：K 太大與閾值太低會漲成本且易混入雜訊；K 太小或閾值太高會漏關鍵內容。文中示範常用 limit 與 minRelevance 作平衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q9, D-Q3

Q9: GPTs（OpenAI 自訂 GPT）在 RAG 裡扮演什麼角色？
- A簡: GPTs 提供對話介面與 Function Calling，能依 OpenAPI Schema 呼叫檢索 API。
- A詳: GPTs 允許設定角色說明（Instructions）與掛載 Custom Actions（OpenAPI/Swagger），模型可「看懂」 API 規格，自行組裝請求並在使用者同意下呼叫。文中讓 GPTs 負責 Synthesis 與對話串接；Retrieval 則由外部 Kernel Memory 服務（/search）完成。優點：快速上線、對話上下文、用戶端負擔 LLM 費用；限制：需 Plus 訂閱、控制力較低，需透過指示與 API 描述精調行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q2, C-Q8

Q10: Kernel Memory 是什麼？與 Semantic Kernel 關係？
- A簡: Kernel Memory 是微軟開源的 RAG「記憶」層，基於 Semantic Kernel，提供 ingestion、retrieval、ask/search API。
- A詳: Kernel Memory 專注在記憶管線（Ingestion→Retrieval→Synthesis Prompting），可作為服務（Service）或程式內（Serverless）使用。其底層整合 Azure OpenAI（Embedding/Chat）、多種向量儲存（Azure AI Search、Qdrant、Elastic、Redis、SimpleVectorDB），提供 /search（純檢索）與 /ask（檢索+生成）端點；Serverless 版本提供 MemoryServerless.AskAsync/SearchAsync 等 API。其實作依賴 Semantic Kernel，開發者可用 Builder 注入模型、儲存、分散式處理等元件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q7, B-Q12

Q11: 什麼是 OpenAPI + Function Calling？為何描述很重要？
- A簡: 以 OpenAPI 描述 API 後，LLM 能讀懂參數語意並自動組請求；描述文字即是「對 API 的提示」。
- A詳: GPTs/LLM 的 Function Calling 會解析 OpenAPI（Swagger）規格，理解路徑、參數、型別、描述，再根據對話上下文決定是否呼叫、如何填值。描述（description）欄位是模型理解語意的重要線索，等同於「教模型如何用 API 的 Prompt」。文中將 /search 的 query/minRelevance/filters/limit 皆以說明文字註明用途與語意，讓 GPTs 能正確選擇與填參數，大幅提升工具使用正確率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q2, D-Q4

Q12: RDB、NoSQL 與 VectorDB 差異？
- A簡: RDB 表格與關聯、NoSQL 文件與物件、VectorDB 向量與語意；三者互補非互斥。
- A詳: RDB 以表格/Schema/SQL 為核心，擅長精準關聯、交易一致性；NoSQL 以文件/集合為主，貼近物件模型，易擴展與分散式；VectorDB 則以語意為核心，用嵌入向量做相似度檢索（Top-K）。在 RAG 中常見組合是：NoSQL/RDB 儲存原文與屬性、VectorDB 儲存向量索引與做相似搜尋。它們互補：向量檢索找語意相近候選，傳統資料層做屬性過濾、權限控管與來源回溯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q12

Q13: 為什麼需要 Tags/Filters？與 ABAC 有何關聯？
- A簡: Tags/Filters 提供安全與精準過濾；ABAC 用屬性控權限，於檢索時強制過濾。
- A詳: 多數 VectorDB 不提供記錄層級權限，因此建議在 Ingestion 時為每段內容貼上標籤（如 user-id、類別、敏感等級），查詢時以 Filters 過濾。這與 ABAC（Attribute-Based Access Control）一致：人（身份/角色）+ 資源（屬性標籤）+ 規則（Policy）→ 控制可見內容。Kernel Memory 的 Filter 支援 AND/OR，JSON 結構簡潔；官方並建議把 Kernel Memory 當私有後端，使用 JWT 提取用戶 ID 並用 Tags 安全過濾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q13, D-Q9

Q14: 為什麼說「AI 改變了搜尋方式」？
- A簡: 從欄位/關鍵字搜尋，升級到語意搜尋；查詢語言從 SQL 走向自然語言與提示工程。
- A詳: 傳統搜尋依賴欄位/關鍵字/全文檢索，難以跨語意表達差異；Embedding + Vector Search 讓語意可計算：不同表達可被視作相近向量。開發的關鍵不再是拼查詢語法，而是：如何把資料與查詢都放入同一語意空間、如何設計 Chunking、設定 Top-K 與 Filters、如何設計 Synthesis Prompt。配合 LLM，查詢可用自然語言/對話，工程師聚焦於資料與意圖，而非繁瑣的查詢語言。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q2, C-Q8

Q15: text-embedding-3-large 有哪些特性與成本？
- A簡: 3072 維、高表現（MTEB 64.6%）、輸入上限約 8191 tokens，單價 $0.13/1M tokens。
- A詳: 文中使用的 OpenAI text-embedding-3-large 提供 3072 維度向量，能捕捉豐富語意特徵。最大輸入長度約 8k tokens，因此長文本需 Chunking。嵌入費用按輸入 Tokens 計價，成本遠低於 LLM 推論。Ingestion（一次性）與 Query（每次）都要產生嵌入，故要留意：問題精簡、合理 Chunk、避免不必要重算。模型一旦更換，舊向量需重建，請保持一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q9, D-Q10

Q16: RAG 的主要挑戰是什麼？
- A簡: 包含資料攝取複雜度、嵌入效率、向量庫選型、混合記憶、知識更新與泛化。
- A詳: 依文中引用課程，RAG 雖易上手，仍有開放性挑戰：1) Ingestion 複雜度（來源多樣、切塊策略、清洗） 2) 嵌入效率與成本 3) VectorDB 的擴展性、延遲、濾器能力 4) 泛化與精度（需 Prompt 與流程調教） 5) 混合記憶（參數/非參數的協作） 6) 知識更新機制（重嵌/重索引流程）。解法往往是工程與流程治理：離線批量、指標監控、可配置化 Chunk/Top-K/Filters 與 A/B 測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, D-Q2, D-Q3


### Q&A 類別 B: 技術原理類

Q1: RAG 的完整執行流程如何運作？
- A簡: 先切塊向量化，查詢時向量比對取 Top-K，再把查詢與片段交給 LLM 生成答案。
- A詳: 技術原理說明：RAG 由三段組成——Ingestion：資料切塊（Chunking）→ 使用 Embedding 模型轉向量 → 寫入 VectorDB 並保留 Tags。Retrieval：Query 經 Embedding 後在向量空間做相似度比對（常用 cosine），依 minRelevance 過濾並取 Top-K，必要時套用 Tags Filters（AND/OR）。Synthesis：將 Query 與 Top-K 片段（Facts）放入提示模板（含指令），交由 ChatCompletion 模型生成答案。關鍵步驟或流程：清洗/切塊→向量化→索引→查詢向量化→相似度排序→過濾→組 Prompt→生成。核心組件介紹：Embedding 模型、VectorDB、LLM、提示模板、過濾器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q4, B-Q2

Q2: Retrieval 在 RAG 中的技術流程是什麼？
- A簡: 查詢向量化→相似度計算→Top-K 過濾→取回對應原文片段，供 LLM 使用。
- A詳: 技術原理說明：Retrieval 以語意為核心，先將用戶查詢（自然語言）轉 Embedding 向量，再與索引中的向量計算相似度（常用 cosine），取前 K 名（Top-K），並可套用 Tags/Filters 與 minRelevance 提升精準度。關鍵步驟或流程：Query→Embedding→Similarity→Top-K→過濾→取回原文。核心組件介紹：Embedding 模型（如 text-embedding-3-large）、向量搜尋引擎（Azure AI Search/Qdrant/Elastic/Redis/SimpleVectorDB）、過濾語法（Kernel Memory 的 MemoryFilter）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q8, B-Q7

Q3: Chunking 的技術要點與影響？
- A簡: 需在語意邊界切塊、適度重疊、控制長度，影響召回率與成本。
- A詳: 技術原理說明：Embedding 模型有輸入上限，長文必須切塊。切塊若穿越語意邊界，會造成「語意破碎」導致檢索偏誤；適度重疊可降低割裂風險。過長會增加成本並使檢索粒度降低，過短則訊噪比差。關鍵步驟或流程：文本清洗→段落邊界偵測→重疊策略設定→切塊→嵌入。核心組件介紹：切塊器（可於 Kernel Memory 配置）、Tokenizer（影響長度計算）、Embedding 模型（影響維度與表現）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q2, C-Q7

Q4: 為何常用 Cosine 相似度？如何運作？
- A簡: Cosine 衡量向量方向相似，不受長度影響，符合語意相近特性。
- A詳: 技術原理說明：Cosine 相似度取兩向量夾角的餘弦值，範圍 [-1,1]。語意相近的向量方向相近，cos 值高；正交（0）代表無關；反向（-1）不是最不相關，只是方向相反。關鍵步驟或流程：正規化或直接計算點積 / 夾角→對全庫（或倒排索引）做近鄰搜索→排序→截取 Top-K。核心組件介紹：近鄰搜索引擎、相似度計算器、閾值與排序器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q2

Q5: Kernel Memory 的 Tags/Filters 怎麼工作？
- A簡: 在 Ingestion 打標籤，查詢時用 AND/OR 過濾；支援多值與多鍵組合。
- A詳: 技術原理說明：每段內容可攜帶 TagCollection（Key→[Values]）。Retrieval 時以 filters 陣列指定過濾條件：同一鍵的多值→AND；多個鍵物件→OR，能表達（A AND B）OR（C）等複合邏輯。關鍵步驟或流程：Ingestion 時寫入必要標籤（類別、作者、user-id、機密等）→查詢時組 filters JSON→向量引擎先過濾再算相似或先算後過濾（依實作）。核心組件介紹：MemoryFilter、TagCollection、支持原生過濾的 VectorDB。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q6, D-Q6

Q6: GPTs 如何透過 Custom Action 呼叫外部 API？
- A簡: 提供 OpenAPI Schema，模型讀懂參數語意，自動組請求；用戶同意後發送。
- A詳: 技術原理說明：在 GPTs 設定頁掛載含路徑/參數/描述的 OpenAPI。LLM 依對話上下文比對工具用途，決定呼叫與參數填值。展示給用戶確認後執行，回應 JSON 再交模型總結。關鍵步驟或流程：撰寫 Swagger→上傳至 GPTs→在指示中說明用法→對談中觸發→回傳結果→二次生成。核心組件介紹：OpenAPI/Swagger、Function Calling、允許外呼的 GPTs 設定頁。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q11, C-Q2

Q7: /search API 的輸入與輸出結構是什麼？
- A簡: 輸入 query/minRelevance/filters/limit；輸出 results 陣列，含 Citation 與 Partitions。
- A詳: 技術原理說明：/search 接收 JSON：query（字串）、minRelevance（相似度閾值）、filters（Tag 過濾）、limit（Top-K）。回傳 SearchResult：包含 results，每筆為 Citation（documentId、fileId、link、sourceName），內含 Partitions（Text、Relevance、PartitionNumber、Tags）。關鍵步驟或流程：Query→Embedding→相似度排序→過濾→組結果。核心組件介紹：SearchResult、Citation、Partition、MemoryFilter。此結構便於後續在 Synthesis 中以 Facts 豐富上下文。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q11, C-Q5

Q8: /ask 與 /search 的差異？
- A簡: /search 只做檢索；/ask 檢索後再用 Chat 模型生成答案，回傳文本與來源。
- A詳: 技術原理說明：/ask 包含 Retrieval + Synthesis，會根據 question 生成 Answer（text/result）並附 RelevantSources（同 /search 的片段）。關鍵步驟或流程：Question→Retrieval→組 Prompt（Facts + 指令 + Question）→ChatCompletion 生成→回傳。核心組件介紹：MemoryAnswer、Chat 模型（如 GPT-4）、Prompt 模板。成本上 /ask 會消耗大量 LLM tokens（如範例約 15k input tokens），相較 /search 只產生 Embedding 成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q1, D-Q3

Q9: MemoryServerless 是什麼？與 Service 模式差異？
- A簡: Serverless 將 KM 內嵌程式中直接用，Service 模式則提供 HTTP API 給外部存取。
- A詳: 技術原理說明：MemoryServerless 允許在程式中直接呼叫 AskAsync/SearchAsync，不需獨立 Web 服務；Service 模式則啟動 Web API（/search、/ask）供 GPTs 或其他客戶端使用。關鍵步驟或流程：用 Builder 設定模型與存儲→Serverless 匯入與查詢→或以 Service 架站提供端點。核心組件介紹：KernelMemoryBuilder、AzureOpenAIText/Embedding、SimpleVectorDB 或其他後端、InProcessPipelineOrchestrator。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q3, C-Q4

Q10: Azure OpenAI 模型在此扮演哪些角色？
- A簡: Embedding 模型負責向量化；Chat 模型負責生成答案與總結上下文。
- A詳: 技術原理說明：文中使用 text-embedding-3-large 做 Ingestion 與 Query 嵌入（$0.13/1M tokens），GPT-4 作 Synthesis（約 $10/1M input、$30/1M output）。關鍵步驟或流程：Ingestion（批量嵌入）→Query（即時計價）→Synthesis（組 Prompt 輸入 Chat 模型）。核心組件介紹：Azure OpenAI Resource、部署 Embedding 與 Chat 模型、API 金鑰與費用計量。模型需一致性（嵌入端），避免檢索失準。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, C-Q9, D-Q10

Q11: Synthesis 的 Prompt 範本長怎樣？
- A簡: 常見為「Facts（來源片段）+ 指令（限制/風格）+ Question → Answer」。
- A詳: 技術原理說明：Kernel Memory 在 /ask 會組典型模板：先羅列 Facts（片段文本、來源、相似度），中段放入系統指令（只根據事實作答、不足回 INFO NOT FOUND、語氣/語言要求），再附上原始 Question，讓 Chat 模型生成 Answer。關鍵步驟或流程：取 Top-K→清理→排序→拼接→生成。核心組件介紹：Prompt Template、Answer Post-Processing。文中亦示範手工把 /search 結果轉為「Facts 模板」送入 Chat，效果接近 /ask。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, C-Q8, D-Q2

Q12: Kernel Memory 支援哪些向量儲存？選型考量？
- A簡: 支援 Azure AI Search、Qdrant、PostgreSQL、Elastic、Redis、Simple；依成本/延遲/維運選擇。
- A詳: 技術原理說明：KM 抽象化向量後端，讓你以設定切換。SimpleVectorDB 僅適合開發測試；Azure AI Search 提供雲端託管、支援 OCR；Qdrant/Elastic/Redis 有各自優勢（延遲、擴展、既有棧整合）。關鍵步驟或流程：評估資料量、QPS、延遲、過濾能力、安全隔離→挑選後端→設定 Builder。核心組件介紹：VectorDB Provider、儲存抽象、索引建置。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q3, C-Q10, D-Q5

Q13: RAG 的安全最佳實踐是什麼？
- A簡: 將 KM 當私有後端、以用戶身分標籤內容、所有查詢強制用 Tags 過濾。
- A詳: 技術原理說明：KM 建議以內網或保留 IP 方式部署，僅供後端服務存取；以 AAD/JWT 驗證用戶，從憑證取 user-id，將其作為內容標籤；所有讀/寫均帶上 User Tag，確保檢索結果不越權。關鍵步驟或流程：認證（JWT）→授權（ABAC 規則）→Ingestion 標籤→Retrieval 過濾→審計。核心組件介紹：Tags/Filters、API Gateway、憑證管理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, D-Q9

Q14: 如何控制 RAG 的效能與成本？
- A簡: 調整 Chunk 大小/重疊、Top-K、minRelevance、過濾先後，離線批量嵌入。
- A詳: 技術原理說明：成本主要在三處：Ingestion 嵌入（一次性）、Query 嵌入（每次）、Synthesis Tokens（每次且昂貴）。關鍵步驟或流程：優化 Chunk（避免過長/過短）、合理設定 K 與閾值、先以 Tags 過濾縮小候選、只把必要片段送入 LLM、以 /search + Chat 客戶端組 Facts 減少不必要 /ask。核心組件介紹：Tokenizer、Retriever、Prompt Composer、成本監控儀表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q9, D-Q3


### Q&A 類別 C: 實作應用類

Q1: 如何用 GPTs + Kernel Memory 打造部落格 RAG（端到端）？
- A簡: 前端用 GPTs 對話與 Actions，後端 KM 提供 /search；離線程式做 Ingestion 建索引。
- A詳: 實作步驟：1) 準備文章（Markdown→純文字） 2) 用 KM Serverless（C#）匯入：Chunk→Embedding（text-embedding-3-large）→SimpleVectorDB（或其他後端） 3) 部署 KM Service（/search、/ask），文中以 Azure App Service、只讀打包 memories 4) 在 GPTs 掛載 OpenAPI（描述 /search 參數與語意）5) 在指示中要求回覆時附上 post-url 超連結 6) 對話時 GPTs 依上下文決定呼叫 /search，回傳結果再總結。程式碼片段：參考 MemoryServerless.ImportTextAsync 與 Builder 設定。注意事項：模型一致、Filters 正確、成本控管（Top-K/閾值）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q6, C-Q2

Q2: 如何在 GPTs 設定 Custom Action（OpenAPI）讓模型自動呼叫 /search？
- A簡: 撰寫 Swagger，清楚描述參數語意，於 GPTs Actions 上傳並啟用。
- A詳: 實作步驟：1) 撰寫 OpenAPI：定義 POST /search，參數含 query、minRelevance、limit、filters（含結構示例與語意說明） 2) 在 GPTs→Configure→Actions 上傳 3) 於指示說明何時使用 /search，回覆需附來源連結。程式碼/設定片段：Swagger YAML/JSON 範例與 description 欄位。注意事項：描述越清楚越能讓模型正確填值；回應結構亦要描述，方便二次總結；測試多輪對話確保能穩定觸發工具。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, D-Q4

Q3: 如何用 C#（Serverless）把 Markdown 文章匯入 Kernel Memory？
- A簡: 解析 Front Matter 與正文，組 Tags，呼叫 ImportTextAsync 建索引。
- A詳: 實作步驟：1) 解析 Markdown Front Matter（標題、日期、分類、標籤、URL） 2) 轉純文字正文 3) 用 KernelMemoryBuilder 設定 AzureOpenAIText/Embedding 與 SimpleVectorDB 4) 為每篇建立 TagCollection（user-tags、categories、post-url、post-date、post-title） 5) 呼叫 memory.ImportTextAsync(content, documentId, tags)。關鍵程式碼片段：Builder 與 ImportTextAsync 迴圈（如文中 Program.cs）。注意事項：模型/Tokenizer 一致；避免重複匯入；觀察 Chunk 數量與檔案大小。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q3, C-Q6

Q4: 如何將 Kernel Memory 服務部署為「只讀」檢索服務？
- A簡: 先離線建 memories，打包部署；在雲端只開 /search（或 /ask），不開匯入管道。
- A詳: 實作步驟：1) 在開發機執行Serverless匯入，產生 memories（JSON 向量檔） 2) 於建置流程將 memories 夾帶進 Docker Image 或部署包 3) 於 Azure App Service 部署 KM Service，移除寫入 API（只保留 /search、必要時 /ask） 4) 維護流程：內容變更→重新 Ingestion →重新佈署。設定片段：KM Service 啟動設定、關閉匯入端點。注意事項：確保模型版本一致；控制外部存取（私有端點/防火牆）；版本化 memories 以利回滾。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, B-Q13

Q5: 客戶端如何呼叫 /search 並組合 Facts Prompt 給 Chat？
- A簡: 送出 query，取回 Partitions，組「Facts + 指令 + 問題」，餵給 Chat 模型生成。
- A詳: 實作步驟：1) POST /search：{ query, minRelevance, filters, limit } 2) 解析 results[].partitions[]，把 text、relevance、post-url（Tag）整理成 Facts 區塊 3) 在指令中要求「僅根據 Facts 回答，不足回 INFO NOT FOUND，並附來源超鏈」 4) 加上使用者原始問題 5) 呼叫 Chat Completion（如 GPT-4）生成。關鍵程式碼片段：Facts 模板組裝。注意事項：控制片段數量；去除重複；保留關鍵 Tags；語言/風格要求寫明。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q11, C-Q8

Q6: 如何在匯入時設計 Tags 以支持未來過濾與安全？
- A簡: 為類別、標籤、日期、URL、標題、user-id 等加標籤，查詢時以 Filters 強制過濾。
- A詳: 實作步驟：1) 盤點未來過濾維度（分類、主題、語言、敏感等級、擁有者） 2) 在 Ingestion 產生 TagCollection：如 user-tags、categories、post-url、post-date、post-title、（可選）owner-id 3) 查詢時用 filters：同鍵多值為 AND；多鍵物件為 OR 4) 在安全需求下必帶 user-id 過濾。設定片段：Filters JSON 範例（AND/OR）。注意事項：標籤應反映「意圖」且儘量靜態；避免依賴動態外部條件改寫標籤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q13, D-Q6

Q7: 如何調整 Chunking（大小/重疊）？
- A簡: 以語意段落為主、適度重疊；依模型上限與成本試調，觀察精準度與召回。
- A詳: 實作步驟：1) 觀察文本結構，以段落/標題/小節為切點 2) 參考 Token 上限，先以中等長度（如 300–800 tokens）測試 3) 設定 10–20% 重疊避免斷裂 4) 評估 K 與 minRelevance 配合效果 5) A/B 測試不同組合，看 /search 的 Relevance 與最終答案品質。設定片段：KM 切塊器配置。注意事項：避免過細（噪音多）與過大（粒度太粗）；多語言文本可視需要不同策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, D-Q2, A-Q6

Q8: 如何寫 GPTs 指示，讓回答一定附來源連結？
- A簡: 在指示明確要求「僅依檢索事實作答，並以 post-url 超連結附上來源」。
- A詳: 實作步驟：1) 在 GPTs Instructions 指定：回覆必須附上來源（以 post-url 值為超連結）、如資訊不足回「INFO NOT FOUND」；2) 建議二段式：先檢索摘要，追問才列來源（或一次列出）；3) 針對常見歧義提供示例。設定片段：指示範本文字。注意事項：描述要具體可執行，避免模糊；搭配 OpenAPI 描述欄位，讓模型識別哪個 Tag 是 URL。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q11, C-Q5

Q9: 如何優化成本（Embedding 與 LLM Tokens）？
- A簡: 批量離線嵌入、降低 Top-K、提高閾值、先過濾再生成、控制段落長度與語言。
- A詳: 實作步驟：1) Ingestion 一次到位（離線），避免重複嵌入 2) Query 嵌入成本低，但 Synthesis 昂貴，先用 Filters 縮小候選 3) 調小 K（如 5–10）、提高 minRelevance（如 0.3–0.5）4) 僅將必要片段送入 LLM 5) 精簡指示與輸出格式 6) 監控 token 消耗。設定片段：/search limit 與 minRelevance 範例。注意事項：模型費率：嵌入 $0.13/1M；GPT-4 輸入 $10/1M；輸出 $30/1M。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, A-Q15, D-Q3

Q10: 如何從 SimpleVectorDB 平滑遷移到雲端向量庫？
- A簡: 維持 KM 抽象接口，切換 Builder 設定與連線，重建索引即可。
- A詳: 實作步驟：1) 在開發以 SimpleVectorDB 快速驗證 2) 評估資料量/QPS/延遲，選定 Azure AI Search 或 Qdrant/Elastic/Redis 3) 修改 KernelMemoryBuilder：改用目標向量後端 4) 重新 Ingestion（或匯出/匯入）以建立新索引 5) 壓測與回歸測試。設定片段：Builder 配置切換。注意事項：確保嵌入模型一致；若改模型需全量重嵌；檢查 Filters 相容性（不同後端的過濾能力差異）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q4


### Q&A 類別 D: 問題解決類

Q1: 遇到 /search noResult=true 怎麼辦？
- A簡: 放寬條件：降低 minRelevance、增大 Top-K、檢查 Filters 與索引是否齊全。
- A詳: 問題症狀描述：/search 回傳 noResult 或 results 為空。可能原因分析：閾值過高、limit 太小、Filter 過嚴、內容未匯入或模型不一致（嵌入時與查詢時不同）。解決步驟：1) 降低 minRelevance（如 0.2–0.3）2) 增加 limit（如 10–30）3) 暫時移除 Filters 確認是否為過濾造成 4) 確認匯入流程與模型版本一致 5) 檢視索引資料量與 Tags。預防措施：建立匯入驗證（計數/抽檢）、模型版本鎖定、查詢前先顯示即將使用的 Filters。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q9

Q2: 檢索結果不準（內容相關性差）怎麼改善？
- A簡: 調整 Chunking（語意切點/重疊）、提高閾值、健全 Tags，檢視嵌入模型一致性。
- A詳: 問題症狀描述：Top-K 片段常與問題無關或斷裂。可能原因：切塊穿越語境、重疊不足、K 太大引入雜訊、minRelevance 太低、Tags 未分流主題、嵌入模型或語言不一致。解決步驟：1) 以段落為切點並加重疊 2) 提高 minRelevance（0.3→0.5）3) 降低 K（30→10）4) 加強 Tags 與 Filters 5) 確認嵌入模型一致。預防措施：A/B 測試 Chunk 策略、建立檢索品質指標、定期重嵌長期積累的內容。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q7

Q3: 成本暴衝（Tokens 很高）如何處理？
- A簡: 先過濾後生成、調小 Top-K、提高閾值、減少片段長度與回覆長度。
- A詳: 問題症狀描述：/ask 或 Synthesis 時 Token 消耗過高（如 15k input/t）。可能原因：K 過大、片段過長、Filters 未使用、指示冗長、輸出過度詳盡。解決步驟：1) 優先 /search + 客戶端組 Facts 2) 降 K、提閾值 3) 維持短指示 4) 控制回答長度與格式 5) 監控 Token 並調參。預防措施：預設審慎的 K/閾值、在 GPTs 指示中設定輸出長度、對常見任務定義精簡模板。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q9

Q4: GPTs 沒有觸發 Custom Action（API 未被叫）？
- A簡: 檢查 OpenAPI 描述、參數語意與指示，確保工具用途與觸發時機清晰。
- A詳: 問題症狀描述：明明需要檢索，GPTs 卻未呼叫 /search。可能原因分析：OpenAPI 缺描述、參數命名不清、指示未說明何時使用 Action、回應已能靠上下文生成。解決步驟：1) 在 OpenAPI 加上明確 description 2) 在 GPTs 指示加入「需要外部知識時呼叫 /search」與輸出規則 3) 在對話中示範一次 4) 檢查網路權限與 CORS。預防措施：提供高品質 Schema、以測試對話驗證觸發率、監控工具使用紀錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q2

Q5: 發生 API 超時或頻率限制該怎麼辦？
- A簡: 降低 K、先過濾、加快序列化、啟用快取、排程離線重建索引。
- A詳: 問題症狀描述：/search 或 /ask 回應慢、Timeout 或被限流。可能原因：Top-K 過大、無 Filters、序列化/反序列化成本過高、後端向量庫壓力過大。解決步驟：1) 降 K 並提閾值 2) 使用 Filters 縮小候選 3) 檢查輸出結構，避免過度龐大 4) 引入快取（同 Query/Filters） 5) 擴容或更換向量庫。預防措施：壓測、設上限參數、建立退避與重試策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q9

Q6: Filters 沒生效（過濾失敗或誤解）怎麼排查？
- A簡: 檢查 JSON 結構、鍵名/值、AND/OR 規則，驗證 Tag 寫入是否一致。
- A詳: 問題症狀描述：設定了 Filters 仍看到不該出現的內容，或相反過濾過頭。可能原因：JSON 結構錯、鍵名不符、值大小寫/語系不一致、誤解 AND/OR 規則、Ingestion 時未寫入該 Tag。解決步驟：1) 用最小測試驗證單一鍵值過濾 2) 依序增量加條件 3) 驗證資料上是否存在該 Tag 4) 檢查 KM 過濾語義。預防措施：Tag 鍵/值標準化，建立 Ingestion 驗證與查核工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q6

Q7: 中英夾雜或中文斷詞可能影響檢索嗎？
- A簡: 高品質嵌入模型能跨語言；建議問題清楚、適度同義詞，並優化切塊。
- A詳: 問題症狀描述：中文或中英混雜查詢出現落差。可能原因：文本/查詢語言不一致、切塊導致語意破碎。解決步驟：1) 試以同義詞或更清楚的描述 2) 觀察改變語言是否改善 3) 優化 Chunking（避免切斷標點與專用名詞） 4) 留意模型的跨語言能力。預防措施：重要關鍵字保持一致、在 Ingestion 階段做多語言清洗與正規化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q2

Q8: /ask 與 GPTs 生成答案不一致怎麼辦？
- A簡: 差異源自 Prompt 與上下文處理不同；統一模板與片段數量以收斂結果。
- A詳: 問題症狀描述：同一問題，/ask 與 GPTs 的答案風格/細節不同。可能原因：/ask 使用 KM 既定 Prompt；GPTs 用你自訂的指示與對話上下文。解決步驟：1) 觀察 /ask 的 Facts 與指令 2) 在 GPTs 指示中模擬 /ask 模板（Facts + 指令） 3) 控制片段數量與語言/風格 4) 減少多輪上下文干擾。預防措施：規範一組組織化 Prompt，建立回覆一致性標準。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q11, C-Q8

Q9: 如何避免權限外洩（越權檢索）？
- A簡: 把 KM 當私有後端；Ingestion 打上 user-id 等安全標籤；所有查詢強制帶 Filters。
- A詳: 問題症狀描述：用戶能看到非授權內容。可能原因：未以 ABAC 設計 Tags、查詢時未強制帶安全 Filters、KM 對外開放。解決步驟：1) 將 KM 部署在私有網 2) 用 JWT/OIDC 取得 user-id，Ingestion 與查詢都帶上 3) 在 API Gateway 強制加安全 Filters 4) 加審計與偵測。預防措施：標準化 Tag 策略、每次查詢驗證 Filter 注入、滲透測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q13, C-Q6

Q10: 為何檢索效果忽好忽壞？可能是模型不一致？
- A簡: 嵌入模型需前後一致；更換模型要全量重嵌，否則相似度失真。
- A詳: 問題症狀描述：相同 Query 時好時壞，或更新後全面品質下降。可能原因：Ingestion 與查詢使用不同嵌入模型或版本。解決步驟：1) 確認模型名稱與版本一致 2) 若變更，重做 Ingestion（重嵌所有內容） 3) 建立模型版本標記與資料夾版本化。預防措施：鎖定模型版本、對模型遷移制定 SOP 與回滾策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q10, C-Q10


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 RAG（Retrieval-Augmented Generation）？
    - A-Q2: 什麼是 Embedding 與 Embedding Space？
    - A-Q4: RAG 的三大組件差在哪裡：Ingestion、Retrieval、Synthesis？
    - A-Q3: 向量資料庫（Vector DB）是什麼？
    - A-Q5: 為什麼選 RAG 而非微調（Fine-tuning）？
    - A-Q6: 什麼是 Chunking？為什麼重要？
    - A-Q8: 什麼是 Top-K 檢索？minRelevance 有何用途？
    - A-Q9: GPTs 在 RAG 裡扮演什麼角色？
    - A-Q11: 什麼是 OpenAPI + Function Calling？為何描述很重要？
    - A-Q12: RDB、NoSQL 與 VectorDB 差異？
    - A-Q14: 為什麼說「AI 改變了搜尋方式」？
    - A-Q15: text-embedding-3-large 有哪些特性與成本？
    - B-Q1: RAG 的完整執行流程如何運作？
    - B-Q2: Retrieval 在 RAG 中的技術流程是什麼？
    - C-Q8: 如何寫 GPTs 指示，讓回答一定附來源連結？

- 中級者：建議學習哪 20 題
    - B-Q3: Chunking 的技術要點與影響？
    - B-Q4: 為何常用 Cosine 相似度？如何運作？
    - B-Q5: Kernel Memory 的 Tags/Filters 怎麼工作？
    - B-Q6: GPTs 如何透過 Custom Action 呼叫外部 API？
    - B-Q7: /search API 的輸入與輸出結構是什麼？
    - B-Q8: /ask 與 /search 的差異？
    - B-Q9: MemoryServerless 是什麼？與 Service 模式差異？
    - B-Q10: Azure OpenAI 模型在此扮演哪些角色？
    - B-Q11: Synthesis 的 Prompt 範本長怎樣？
    - B-Q14: 如何控制 RAG 的效能與成本？
    - C-Q1: 如何用 GPTs + Kernel Memory 打造部落格 RAG（端到端）？
    - C-Q2: 如何在 GPTs 設定 Custom Action（OpenAPI）讓模型自動呼叫 /search？
    - C-Q3: 如何用 C#（Serverless）把 Markdown 文章匯入 Kernel Memory？
    - C-Q4: 如何將 Kernel Memory 服務部署為「只讀」檢索服務？
    - C-Q5: 客戶端如何呼叫 /search 並組合 Facts Prompt 給 Chat？
    - C-Q6: 如何在匯入時設計 Tags 以支持未來過濾與安全？
    - C-Q7: 如何調整 Chunking（大小/重疊）？
    - C-Q9: 如何優化成本（Embedding 與 LLM Tokens）？
    - D-Q1: 遇到 /search noResult=true 怎麼辦？
    - D-Q2: 檢索結果不準（內容相關性差）怎麼改善？

- 高級者：建議關注哪 15 題
    - A-Q13: 為什麼需要 Tags/Filters？與 ABAC 有何關聯？
    - A-Q16: RAG 的主要挑戰是什麼？
    - B-Q12: Kernel Memory 支援哪些向量儲存？選型考量？
    - B-Q13: RAG 的安全最佳實踐是什麼？
    - C-Q10: 如何從 SimpleVectorDB 平滑遷移到雲端向量庫？
    - D-Q3: 成本暴衝（Tokens 很高）如何處理？
    - D-Q4: GPTs 沒有觸發 Custom Action（API 未被叫）？
    - D-Q5: 發生 API 超時或頻率限制該怎麼辦？
    - D-Q6: Filters 沒生效（過濾失敗或誤解）怎麼排查？
    - D-Q7: 中英夾雜或中文斷詞可能影響檢索嗎？
    - D-Q8: /ask 與 GPTs 生成答案不一致怎麼辦？
    - D-Q9: 如何避免權限外洩（越權檢索）？
    - D-Q10: 為何檢索效果忽好忽壞？可能是模型不一致？
    - B-Q1: RAG 的完整執行流程如何運作？
    - B-Q14: 如何控制 RAG 的效能與成本？