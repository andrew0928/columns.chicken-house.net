# 替你的應用程式加上智慧! ─ RAG 檢索與實作案例

# 問題／解決方案 (Problem/Solution)

## Problem: 20 年、400 萬字內容無法被有效檢索與再利用  
**Problem**:  
‧ 部落格已累積 327 篇、400 萬字技術文章，涵蓋微服務、OOP、雲端等主題。  
‧ 文章篇幅長、跨系統遷移多次，並無一致分類／關鍵字。  
‧ 讀者（甚至作者本人）往往只能靠「關鍵字 + 人工翻頁」方式尋找資訊，閱讀及整理成本極高。  

**Root Cause**:  
1. 關鍵字搜尋只能比對字面 (Lexical) ，無法理解語意關聯。  
2. 文章年代久遠、標籤不一致，資料庫層級缺乏結構化索引。  
3. 缺少「摘要、彙整」等二次加工能力，使用者易被過量文字淹沒。  

**Solution**: AndrewBlog GPTs（RAG 檢索機器人）  
1. Ingestion ─ 以 Microsoft Kernel Memory Serverless 將 327 篇文章  
   • Markdown ⇒ 純文字 ⇒ Chunking (≈2–3KB/段)  
   • `text-embedding-3-large` 轉 3072 維向量  
   • SimpleVectorDB 落地 (≈2 MB/46 chunks/篇)  
2. Retrieval ─ 建立 `/search` API (Swagger)  
   • 依語意向量 + Tag Filter(分類/日期/自訂) 取 Top-K  
3. Synthesis ─ 透過 ChatGPT GPTs (GPT-4) Custom Action  
   • GPT 先判斷是否需呼叫 API → 取得 chunks → 依 instruction 產生摘要/條列/翻譯  
   • 回答同時附原文連結以利追溯  
4. 架構：Blog → CI/CD 產生 `memories/` → Docker → Azure App Service → GPTs  

**Cases 1**: 「整理 20 年換站歷程」  
‧ 查詢：*”請幫我列出我換 blog 系統的所有文章並摘要”*  
‧ GPTs 調用 `/search`，30 秒內回傳 15 篇搬遷文章之標題、時間、重點 & 連結。  
‧ 作者人工比對正確率 > 90%，比手動 Google 搜尋節省 30–40 分鐘。  

**Cases 2**: 「微服務資料一致性」  
‧ 問：*“有微服務之間維持資料一致性的作法嗎？”*  
‧ GPTs 回答 CAP、事件溝通、補償交易等 5 條原則，並附 8 篇實作文章。  
‧ 讀者三層追問後仍保持語境，無幻覺 (Hallucination) 。  

**Cases 3**: 「Home NAS 建議容器」  
‧ 問：*“家用 NAS 上適合 Web Developer 的 Container？”*  
‧ GPTs 先給 7 條建議 (Gitlab/Caddy/Portainer…)；追問自動列出 10 篇對應文章。  

---

## Problem: 自行打造 RAG 流程門檻高、開發週期長  
**Problem**:  
‧ RAG 需涵蓋「Chunking、Embedding、VectorDB、Retrieval、LLM Synthesis」五大環節；若全部自行開發，需處理大量 SDK、基礎設施與串接，PoC 難以在短期完成。  

**Root Cause**:  
1. 傳統全文檢索框架（Lucene/Elasticsearch）缺少 Embedding 與 LLM 整合。  
2. 市面多數 RAG 教學僅片段示範，缺乏「端到端」範例及開源骨架。  
3. 部署向量資料庫、佈線 AI Service (Azure OpenAI) 涉及多雲設定，易耗時。  

**Solution**: 採用 Microsoft Kernel Memory + Azure OpenAI 雲服務  
‧ `KernelMemoryBuilder()` 一行註冊 Embedding、ChatCompletion、VectorDB；支援  
  - Azure AI Search / Qdrant / Redis / SimpleVector  
‧ Serverless 模式：無須啟動獨立服務即可在本機匯入 (`ImportTextAsync`)。  
‧ Service 模式：自帶 REST + OpenAPI；對接 GPTs 只需貼 Swagger。  
‧ 完整 PoC *“重做一次不到一天”*：  
  ```csharp
  var memory = new KernelMemoryBuilder()
       .WithAzureOpenAITextGeneration(cfgText)
       .WithAzureOpenAITextEmbeddingGeneration(cfgEmb)
       .WithSimpleVectorDb("memories/")
       .Build<MemoryServerless>();
  ```

**Cases 1**: 單機匯入 327 篇文章僅花 25 分鐘 (含 Embedding)；記憶體峰值 < 1.2 GB。  
**Cases 2**: 部署至 Azure Linux App Service (B1) + Docker 映像，服務冷啟 < 10 秒。  
**Cases 3**: 開源範例 (E=mc²) 10 行程式即可演示 Ask+Search+Citation，全員複製即用。  

---

## Problem: LLM 推論成本高，難以長期營運  
**Problem**:  
‧ 單次 RAG 回應需：  
  1) 使用者 Query Embedding (≈30 tokens)  
  2) GPT-4 讀取 Top-K chunks 整合 (≈15 000 tokens)  
‧ 若由網站自付 GPT-4，月流量 10 000 次將超過 USD 1 500，部落格難以承擔。  

**Root Cause**:  
1. GPT-4 turbo 價格：$10 / 1M input tokens、$30 / 1M output tokens。  
2. 使用者提問無配額限制時，易產生「閒聊式大量呼叫」。  
3. 一般檢索純 Embedding 其實極低價，但最終回答仍必須 LLM 彙整。  

**Solution**:「Cost-Share + Prompt & Chunk 策略」  
A. Cost-Share：  
   • 將前端介面放在 OpenAI GPTs，使用者需自備 ChatGPT Plus 訂閱。  
   • 部落格僅負責 `/search` Embedding 端費用 (約 0.13USD / 1M token)。  
B. Prompt & Chunk：  
   • 預設 Top-K = 5，`minRelevance = 0.3`，避免丟入過多 chunk。  
   • Server 端加入 `maxTokens`、`system` prompt 預設，約束輸出長度。  
C. 將日後 on-prem LLM 納入規劃，必要時轉自有 GPU 降低邊際成本。  

**Cases**  
1. 實測一次完整問答總成本 ≈ USD 0.15，由使用者訂閱內額度承擔。  
2. 嵌入查詢僅 USD 0.0000039，可接受度高；即使 1 000 筆/天僅 0.12 美金。  
3. 3 小時 / 40 次 ChatGPT Plus 預設配額，自然限制濫用。  

---

## Problem: Vector DB 缺乏 Record-Level 權限機制  
**Problem**:  
‧ 若未控管，任何 Query 皆可能取回未授權文件，造成資訊外洩。  

**Root Cause**:  
向量儲存僅支援「相似度檢索」，本身不儲存 ACL 欄位。  

**Solution**: Tag-based ABAC (Attribute-Based Access Control)  
‧ 每筆 Document 在 Ingestion 階段寫入 `tags`：  
  - `user-tags` / `categories` / `post-date`…  
‧ `/search`、`/ask` 參數加入 `filters`：  
  ```json
  "filters":[ { "user-tags":["架構師觀點"] },
              { "user-tags":["microservice","ASP.NET"] } ]
  ```  
‧ Kernel Memory 於 Redis/AISearch/Qdrant 層自動轉成本地 Filter 語句。  

**Cases**  
‧ 測試 (microservice ∧ ASP.NET) OR (架構師觀點) 僅回傳符合 3 筆，權限絕無外溢。  

---

以上四組問題與對應解決方案，展示了如何在最短時間內，運用 RAG + GPTs + Kernel Memory，將一個「長期部落格」升級為「可對談、可語意檢索」的智慧內容平台，同時兼顧開發效率、營運成本與安全控管。