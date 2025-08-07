# 替你的應用程式加上智慧! 談 RAG 的檢索與應用  

# 問答集 (FAQ, frequently asked questions and answers)

## Q: RAG (Retrieval-Augmented Generation) 的三大核心組件是什麼？
Ingestion (將文件切段並向量化後寫入索引)、Retrieval (用 Query 向量在索引裡找出 Top-K 相關片段)、Synthesis (把 Query 與檢索結果交給 LLM 組合成最終回答)。

## Q: 作者如何為「安德魯的部落格」建立對談式 AI？  
他在 ChatGPT 的 GPTs 平台上建立一隻客製化 GPT，前端負責 Synthesis，後端則用自架的 Azure App Service + Microsoft Kernel Memory 提供 /search 與 /ask API 進行 Retrieval；文章事先以 Kernel Memory (Serverless) 向量化並存成檔案 (SimpleVectorDB)。

## Q: Embedding 在這個系統裡扮演什麼角色？  
Embedding 會把一段文字轉為多維向量，使「語意」得以用數學方式表示；只要把 Query 和文件都投射在同一個向量空間，就能用向量的距離或餘弦相似度找出最相關內容。

## Q: 文章內示範使用的文字向量模型是哪一個？費用概念為何？  
作者選用 OpenAI 的 text-embedding-3-large (3072 維)。價格為 0.13 USD / 1M tokens；向量化 30 tokens 僅耗約 0.000004 USD，但若之後把 15 K tokens 餵給 GPT-4 生成答案，則約需 0.15 USD (以 GPT-4 Turbo 10 USD / 1M input tokens 計)。

## Q: 為什麼作者選擇用 GPTs 而不是自己寫一個 Web UI？  
1. GPTs 已內建對談上下文處理，快速完成 PoC。  
2. LLM 推理費用由 ChatGPT Plus 訂閱戶自行負擔，服務端只需承擔檢索 API 的費用。  
3. 透過 OpenAPI schema 就能讓 GPTs 自動呼叫外部檢索 API，開發量極小。

## Q: Kernel Memory 的 Tag 與 Filter 機制有什麼用途？  
每筆文件可加自訂 Tag (如 user-tags、categories、post-date 等)。檢索時可用 AND/OR 篩選 Tag 值，等同在向量搜尋前先做權限或屬性過濾，達成 ABAC 風格的存取控制。

## Q: 若要用 Kernel Memory 只提供「唯讀」檢索服務，需要哪些最少元件？  
1. 本機或 CI 流程以 MemoryServerless + SimpleVectorDB 將文件匯入並產生 memories 目錄。  
2. 把 memories 與簡化後的 Kernel Memory service 打包成 Docker 映像，部署到 Azure App Service。  
3. 讓 GPTs 透過 Custom Action (/search 或 /ask) 呼叫即可。

## Q: VectorDB 與傳統 RDB / NoSQL 的定位差異是什麼？  
RDB 著重「欄位」運算，NoSQL 著重「文件」運算，而 VectorDB 則著重「語意」運算；它通常與 RDB 或 NoSQL 並存：資料本體放 RDB/NoSQL，語意索引放 VectorDB。

## Q: 作者點出 RAG 目前仍有哪些研究與實務挑戰？  
• Data Ingestion 複雜度  
• 向量化效率  
• 向量資料庫選型與調校  
• Fine-Tuning 與泛化  
• 混合 Parametric / Non-Parametric 記憶  
• 知識更新機制

## Q: 「安德魯的部落格 GPTs」能替讀者帶來哪些功能？  
使用者可用自然語言：  
1. 快速找到 20 年、400 萬字、327 篇文章中最相關的段落。  
2. 要求條列式摘要、引用連結或跨語言導讀。  
3. 連續追問，GPT 會藉由上下文和 RAG 自動補充或深挖主題。