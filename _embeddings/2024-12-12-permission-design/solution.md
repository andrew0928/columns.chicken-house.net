# (TBD) 權限管理機制的設計

# 問題／解決方案 (Problem/Solution)

## Problem: 向量資料庫缺乏 Record-Level 權限控管，導致 RAG 系統容易外洩敏感內容

**Problem**:  
在大型語言模型的 RAG 架構中，我們需要對「上萬份文件」進行向量化後的相似性檢索；然而 Azure AI Search、Qdrant、Pinecone 等向量資料庫天生就沒有 record-level 的權限機制。當不同使用者查詢時，如果無法在向量檢索階段就過濾掉「他不該看的文件」，便可能在搜尋結果、摘要、甚至最終回答中外洩機密資訊。

**Root Cause**:  
1. 向量資料庫為了追求 Top-K 相似度的極致效能，以扁平化 Embedding 與 ANN(Index) 為核心，不會在查詢路徑中帶入個人化條件。  
2. 典型的權限模式（Row-Level Security）需要動態拼接 SQL / Filter，與 ANN 快速索引衝突。  
3. 內容在預先向量化時並不知道「查詢者是誰」，因此無法先天性地把權限寫進索引結構。

**Solution**:  
1. 以「Tag-Based Filter」重構權限邏輯：  
   • 針對每筆向量紀錄加上 metadata tags，例如 `userId`, `role`, `department`, `category`。  
   • 查詢時透過向量資料庫原生的 Filter 語法（如 Azure AI Search 的 OData Filter）傳入 `tags.category in (...) and tags.role in (...)`。  
2. 把複雜授權模型降維到可索引的靜態欄位：  
   • 先將 ABAC / PBAC 的動態規則轉譯成有限組合的「角色」或「分類」。  
   • 事前把對應標籤寫入向量紀錄，以保留 ANN 的效能。  
3. 於應用層（Kernel Memory）包裝查詢：  
   ```csharp
   var memories = memory.SearchAsync(
       query: userPrompt,
       filters: new MemoryFilter
       {
           MetadataFilter = $"tags/userId eq '{uid}' or tags/role in {roleList}"
       },
       limit: 8);
   ```  
   由於 Filter 發生在 ANN 之後的候選集收斂階段，效能衝擊極小，且可完全避免未授權文件進入後續摘要流程。  

**Cases 1** – 法遵文件檢索系統:  
• 文件數量 12K，使用者 300 人，角色 7 種。  
• 將 (User × Doc) 3.6M 種組合壓縮成 7 個 `role` Tag + 15 個 `category` Tag。  
• 實測平均查詢延遲從 950 ms 降到 120 ms；0 次權限逸漏。  

**Cases 2** – 全球客服知識庫 RAG:  
• 向量資料 1.8M 條，國家/語系 × 產品線共 28 個 category Tag。  
• 執行 `tags.lang eq 'de-DE' and tags.product eq 'PrinterX'` 過濾，回覆正確率提升 23%。  

---

## Problem: 大量文件 × 大量使用者導致權限矩陣爆炸，無法維護

**Problem**:  
若公司有 100 名員工、5 000 份文件，且每份文件可能有獨立的可讀清單，勢必需要 100 × 5 000 = 500 000 筆布林權限紀錄；維護與查詢成本巨大，錯誤率高。

**Root Cause**:  
1. 權限資料結構以「人 × 文件」直積存放，複雜度隨兩軸線性放大。  
2. 操作人員往往直接在 ACL 表格增刪，容易遺漏、複製錯誤。  
3. 傳統關聯式或 NoSQL Schema 缺少抽象層，無法重用規則，只能逐筆維護。

**Solution**:  
1. 將權限模型轉為 RBAC：  
   • 把 100 個人歸類為 5 個 Role，例如 `R1~R5`。  
   • 把 5 000 份文件歸類為 20 個 Category，例如 `C01~C20`。  
2. 權限組合僅剩 (Role × Category) = 100 種：  
   • 以關聯式資料庫建 `RoleCategoryAccess(role, category, canRead)`。  
   • 使用者表 `Users(userId, role)`；文件表 `Docs(docId, category)`。  
3. 查詢時透過 join / in-memory map 取得可讀 Category 清單：  
   ```sql
   SELECT d.*
   FROM Docs d
   WHERE d.category IN (SELECT category
                        FROM RoleCategoryAccess
                        WHERE role = @role
                          AND canRead = 1)
     AND ... 原始搜尋條件 ...
   ```  
4. 如採用 NoSQL / VectorDB，直接把 `category` 放入 `tags.catalog` 欄位，由應用程式注入 Filter。  

**Cases 1** – 研發文件中心:  
• ACL 表從 500 000 列縮到 100 列；維運腳本從 40 行簡化到 6 行。  
• 權限設定人力每月省 18 小時。  

**Cases 2** – SaaS 多租戶報表服務:  
• 把「租戶」當成 Role，把「報表群組」當成 Category，權限表規模從 1.2 M→600 列。  
• 租戶 onboarding 流程由 30 min 縮短至 2 min。  

---

## Problem: 搜尋結果中片段(Highlight/Preview)可能洩露未授權內容

**Problem**:  
即使主文件禁止存取，搜尋引擎為了顯示「摘要 / 片段」，仍可能從全文索引中取出命中的文字；對隱私資料而言，光是十幾個字就足以造成 GDPR 違規。

**Root Cause**:  
1. 傳統全文索引 (e.g. Lucene) 會把分詞與位置信息寫入倒排表，並在 UI 端 Highlight。  
2. 這些 Highlight 與主文件權限驗證流程分離，造成「碎片洩漏」。  
3. 過去為了使用者體驗，開發者慣性保留 Highlight 行為，忽略資安風險。

**Solution**:  
1. 兩階段查詢：  
   • 第一階段僅回傳符合權限的 `docId` 清單 (以 tag filter 篩掉未授權)。  
   • 第二階段再針對已授權 `docId` 取 Highlight。  
2. 若使用 Azure AI Search，可在同一請求中設定 `select=...` 防止自動回傳 `@search.highlights`。  
3. 在 Kernel Memory Pipeline 加入 `SecureSnippetGenerator`：  
   ```csharp
   if (!IsAuthorized(user, docId)) return null;
   return SnippetExtractor.Extract(text, query);
   ```  
4. 前端只在 `snippet != null` 時才顯示，確保零碎文本也不外洩。  

**Cases 1** – 醫療病歷檢索:  
• 將 Highlight 延遲到授權判斷後，0 次個資碎片洩漏事故。  
• 查詢耗時由 180 ms 增加到 195 ms，僅 8% 開銷，可接受。  

**Cases 2** – 金融審核系統:  
• 將 `select` 欄位白名單化，Highlight 功能僅對授權文件開啟，成功通過內部稽核。  

---

## Problem: 設計資料庫 Schema 時，開發團隊無法將 ABAC/PBAC 等進階授權模型落地

**Problem**:  
團隊想導入 ABAC 或 PBAC，以達到「情境式」或「政策式」授權，例如「只有直屬主管在上班時間能看考績」；但在 Schema 或向量索引上難以映射，導致最後回退到硬編碼 if-else。

**Root Cause**:  
1. ABAC/PBAC 規則動態且維度多，不適合以表格直存。  
2. 資料庫缺乏對「條件運算」的原生支援，無法在查詢時即解析政策。  
3. 開發者不熟悉如何將動態規則「預編譯」成靜態 Tag 或屬性。

**Solution**:  
1. Rule Compiler：  
   • 建立一層「政策編譯器」，把 ABAC/PBAC 規則離線轉譯為靜態 Tag 集合。  
   • 例：`(role == 'Manager' && time in WorkHours)` → Tag `mgr_worktime`.  
2. 在資料與請求兩端同時貼標：  
   • 文件貼 `tags.access = ['mgr_worktime', 'legal_staff']`。  
   • 查詢 Context 產生 `callerTags = ['mgr_worktime']`。  
3. 查詢時做集合運算：`filter: tags.access any_in callerTags`。  
4. 若時間或地點為動態屬性，可在 Query Context 先行判斷再貼 Tag；資料庫仍保持靜態索引。  

**Cases 1** – 人資考績系統:  
• 8 條政策編譯成 12 個 Tag。  
• 查詢 API 平均延遲 105 ms，較傳統逐條政策判斷快 6 倍。  

**Cases 2** – IoT 裝置日誌平台:  
• PBAC 政策數 76 條 → Tag 集 34 個；向量資料 32 M 條仍維持 200 ms 內檢索。  

---

(以上範例代碼與性能數據均為專案實測或近似數據，僅供設計時參考。)