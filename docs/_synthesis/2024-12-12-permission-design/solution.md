---
layout: synthesis
title: "(TBD) 權限管理機制的設計"
synthesis_type: solution
source_post: /2024/12/12/permission-design/
redirect_from:
  - /2024/12/12/permission-design/solution/
postid: 2024-12-12-permission-design
---

以下內容基於文章中對 RAG 檢索安全、向量資料庫缺少 record-level 授權、以 Tags + Filters 降維的設計思路，以及 RBAC/ABAC/PBAC 與資料/人/操作貼標的實務，重組為可落地的 16 個教學型案例。部分「實測數據」以文章示例或設計指標呈現（原文未提供具體量測值）。

## Case #1: 在向量檢索中實作 Record-level 授權（Tags + Filters + MKM）

### Problem Statement（問題陳述）
- 業務場景：企業內部儲存上萬份文件，文件依部門、角色甚至特定使用者管控閱讀權。透過 RAG/向量檢索支援快速搜尋（100ms 級），同時必須遵守文件 READ 控制，避免敏感內容外洩於搜尋結果與摘要。
- 技術挑戰：向量資料庫（Azure AI Search、Qdrant、Pinecone…）普遍不提供 record-level ACL，且相似度檢索預先索引使結果難以依個人化授權差異化。
- 影響範圍：若無法在檢索時套用授權過濾，將導致結果與摘要外洩，造成法遵與信任風險。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 向量庫優化相似度與吞吐，未原生支援 per-record 權限。
  2. 事前嵌入與索引忽略使用者上下文，天生非個人化。
  3. 檢索 API 默認只看相似度，未內建授權過濾能力。
- 深層原因：
  - 架構層面：檢索層與授權層耦合不足，缺少一致的過濾介面。
  - 技術層面：缺少統一的 Tag/Metadata 模型與可移植 Filters。
  - 流程層面：安全需求晚進入，未納入索引/檢索設計。

### Solution Design（解決方案設計）
- 解決策略：為每份文件與每位用戶附上規範化 Tags（如 tenant、role、catalog、userId…），查詢時以過濾器組合（Filters）強制約束檢索空間，使向量相似度只在「授權子集」內進行匹配。所有後續摘要/清單也僅使用過濾後結果。

- 實施步驟：
  1. 權限標籤體系設計
     - 實作細節：定義固定枚舉的 catalog、role、tenantId、user:xxx；避免高基數自由字串。
     - 所需資源：資料字典、資安/IAM 對齊會議
     - 預估時間：0.5-1 天
  2. 文件與使用者貼標
     - 實作細節：在文件向量化前寫入 tags；登入後計算 subject tags（角色、部門、租戶、個人）。
     - 所需資源：ETL/ingestion 流程、使用者目錄
     - 預估時間：1-2 天
  3. 檢索 Filter Builder
     - 實作細節：將 subject tags 轉為 Filters，對應各向量庫/服務的 metadata filter 語法。
     - 所需資源：MKM/SDK、向量庫驅動
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// C# pseudo for Microsoft Kernel Memory style search with filters
var subjectTags = new Dictionary<string, string[]>
{
  ["tenant"] = new[] { tenantId },
  ["role"]   = userRoles,            // e.g., ["R1","R3"]
  ["user"]   = new[] { $"U:{userId}" },
  ["catalog"] = allowedCatalogs      // from RBAC/ABAC expansion
};

var options = new SearchOptions
{
  Query = userQuery,
  Filters = subjectTags              // MKM 以 metadata/tags 過濾向量檢索
};

var results = await kernelMemory.SearchAsync(options);
// 後續摘要/顯示僅使用 results 中的授權文件
```

- 實際案例：文章引用 MKM 官方 security-filters 指南，建議以 Tags + Filters 限縮檢索空間，實現使用者差異化結果。
- 實作環境：.NET 8、Microsoft Kernel Memory、Azure AI Search/Qdrant/Pinecone
- 實測數據：
  - 改善前：無 record-level 過濾，存在摘要與清單外洩風險
  - 改善後：僅於授權子集合中檢索與摘要，外洩風險設計為 0
  - 改善幅度：外洩風險由「不可控」降為「可證明為 0（設計目標）」

Learning Points（學習要點）
- 核心知識點：
  - 向量庫 metadata/tags 過濾原理
  - RAG 安全：先過濾再檢索/生成
  - Tags 架構與可攜 Filters
- 技能要求：
  - 必備技能：向量檢索、後端 API、身份/會話管理
  - 進階技能：跨庫 Filter 語法適配、RAG pipeline 安全設計
- 延伸思考：
  - 可用於多租戶隔離、地區法遵隔離
  - 風險：高基數/自由字串 tag 造成索引退化
  - 優化：採用枚舉/階層展開、緩存 Filter
- Practice Exercise：
  - 基礎：為 3 類角色與 5 類目錄設計 tags 並執行一次檢索（30 分）
  - 進階：接上 MKM，將 subject tags 注入 Filters（2 小時）
  - 專案：完成端到端 RAG 安全檢索（ingest→filter→search→summary）（8 小時）
- Assessment Criteria：
  - 功能完整性（40%）：授權差異化結果與摘要
  - 程式碼品質（30%）：模組化 Filter Builder、錯誤處理
  - 效能優化（20%）：索引可用、P95 延遲可控
  - 創新性（10%）：多資料源與跨庫過濾整合

---

## Case #2: 防止搜尋結果與摘要外洩（先授權後顯示）

### Problem Statement（問題陳述）
- 業務場景：法遵部門要求搜尋結果清單、摘要、預覽片段都不可顯示未授權文件內容。RAG 回答也不得引用未授權材料，否則觸法。
- 技術挑戰：傳統搜尋常先取 TopK 再做 UI 過濾，導致 UI 隱藏但 API 已取回敏感內容；RAG 摘要若未先過濾語料，更會泄露。
- 影響範圍：任何 UI 或 LLM 回覆都可能成為洩漏面。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. UI 層才做授權判斷，資料早已取回。
  2. LLM 前置語料未經權限過濾。
  3. 底層檢索 API 未支援授權 Filter。
- 深層原因：
  - 架構：資料流缺乏「授權閘道」。
  - 技術：缺少一致的過濾中介層。
  - 流程：需求未落於檢索/生成步驟約束。

### Solution Design（解決方案設計）
- 解決策略：統一在檢索層以 Filters 先過濾，再返回結果；摘要/LLM 僅對已授權文檔進行分段與提示。UI 層不再承擔「最後一道」安全責任，而是前置於資料取得。

- 實施步驟：
  1. 封裝授權檢索服務
     - 實作細節：提供 searchAuthorized(query, subjectTags) 介面
     - 所需資源：後端服務、MKM/向量庫 SDK
     - 預估時間：1 天
  2. 摘要服務串接授權檢索
     - 實作細節：LLM prompt 僅注入授權文段，UI 預覽片段亦同
     - 所需資源：LLM/Prompt 層、RAG 組裝器
     - 預估時間：0.5-1 天

- 關鍵程式碼/設定：
```csharp
var authorizedDocs = await SearchAuthorizedAsync(query, subjectTags); // 已套過濾
var chunks = Chunker(authorizedDocs); // 只來自授權資料
var answer = await Llm.AnswerAsync(chunks, query); // LLM 不會接觸未授權內容
```

- 實際案例：文章強調「不能將片段內容顯示在搜尋結果、摘要、清單內」，本方案確保來源即受控。
- 實作環境：.NET 8、MKM/向量庫、LLM 服務
- 実測數據：
  - 改善前：UI 層隱藏但 API 已取回敏感片段
  - 改善後：API 階段即只返回授權資料，UI/LLM 零暴露
  - 改善幅度：外洩風險設計降至 0（設計準則）

Learning Points
- 核心知識點：授權閘道、RAG「先過濾後生成」
- 技能要求：API 設計、LLM 前置資料管線
- 延伸思考：支援審計與重放驗證；限制：Filters 表達力需與業務對齊；優化：最小必要片段抽取
- Practice：實作授權檢索與摘要串接（2 小時）；專案：端到端 UI/LLM 防外洩（8 小時）
- Assessment：功能（40）/品質（30）/效能（20）/創新（10）

---

## Case #3: 用 RBAC 將人×文件降維為角色×分類（從 500,000 到 100）

### Problem Statement（問題陳述）
- 業務場景：100 位員工、5000 份文件，若逐一記錄「誰可讀哪份」需 500,000 個布林狀態，維護成本爆炸。
- 技術挑戰：維護粒度太細造成配置與查詢難度極高；索引與快取不可行。
- 影響範圍：授權錯誤率高，營運與法遵風險大。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 權限未抽象成角色與分類。
  2. 配置分散無規則，無法索引。
  3. 無法快取，查詢慢且易錯。
- 深層原因：
  - 架構：缺乏角色與資源分類模型。
  - 技術：資料結構未為過濾優化。
  - 流程：授權設定無規則、難核對。

### Solution Design
- 解決策略：定義 5 角色與 20 分類，將個人與文件映射為 Role 與 Category，建立 (Role × Category) 設定矩陣，查詢時轉換為 Category IN (…) 條件或 tags 過濾，維護負擔從 500,000 組降為 100 組。

- 實施步驟：
  1. 角色與分類盤點
     - 實作細節：R1~R5、C01~C20，覆蓋業務需
     - 資源：部門訪談、資料字典
     - 時間：1 天
  2. 權限矩陣與查詢改寫
     - 實作細節：以矩陣得出可讀分類清單，加入查詢條件
     - 資源：DB/NoSQL schema 調整
     - 時間：1-2 天

- 關鍵程式碼/設定：
```sql
-- SQL 示例：以角色得到可讀分類，套入檢索
SELECT d.*
FROM docs d
WHERE d.category IN (SELECT c.category FROM role_category_allow c WHERE c.role = @role)
  AND /* 原本條件 */;
```

- 實際案例：文章以 500,000→100 的降維示例說明 RBAC 帶來可管理性。
- 實作環境：任意 RDB/NoSQL；可延伸至向量檢索 Filters
- 實測數據：
  - 改善前：組合量 500,000
  - 改善後：組合量 100
  - 改善幅度：降 99.98%

Learning Points
- 核心：降維思維、RBAC 基本模型
- 技能：資料建模、查詢優化
- 延伸：與 ABAC/PBAC 串接；限制：RBAC 靈活度有限；優化：搭配標籤與個人例外清單
- Practice：建 RBAC 矩陣並改寫查詢（2 小時）；專案：整合向量檢索（8 小時）
- Assessment：功能（40）/品質（30）/效能（20）/創新（10）

---

## Case #4: 在關聯式資料庫落地 RBAC 查詢過濾

### Problem Statement
- 業務場景：現有關聯式系統已保存文件與分類，需要在 SQL 查詢階段落地授權過濾。
- 技術挑戰：如何讓 RBAC 設定可被查詢器有效使用且可索引。
- 影響範圍：報表、API、檢索服務全受影響。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：未有 role_category_allow 關聯表；文件缺 category 欄位；使用者缺 role 欄位。
- 深層原因：
  - 架構：資料未以授權為一等公民設計
  - 技術：缺索引、缺外鍵約束
  - 流程：授權設定分散

### Solution Design
- 解決策略：在 users、docs 表補齊 role、category 欄位，建立 role_category_allow 表與索引，所有查詢加入 category IN (…) 條件。

- 實施步驟：
  1. Schema 調整與索引
     - 細節：ALTER TABLE、建立索引（docs.category, role_category_allow.role,category）
     - 時間：0.5 天
  2. Query Adapter
     - 細節：統一中介層在生成 SQL 時注入 IN (…) 條件
     - 時間：1 天

- 關鍵程式碼/設定：
```sql
CREATE TABLE role_category_allow (role nvarchar(20), category nvarchar(20), PRIMARY KEY(role, category));
CREATE INDEX IX_docs_category ON docs(category);

-- 查詢注入
SELECT d.* FROM docs d
WHERE d.category IN (SELECT category FROM role_category_allow WHERE role = @role)
AND /* other conditions */;
```

- 實際案例：文章示範以 IN (…) 套用分類清單。
- 實作環境：SQL Server/PostgreSQL/MySQL 皆可
- 實測數據：
  - 改善前：查詢不可差異化授權或高風險
  - 改善後：查詢可根據角色過濾
  - 改善幅度：法遵風險→可控

Learning Points
- 核心：SQL 層授權過濾
- 技能：索引設計、查詢組裝
- 延伸：視圖或行級安全（RLS）對比；限制：跨庫一致性；優化：以物化視圖快取 allow 集合
- Practice：實作 schema+查詢（2 小時）；專案：接入應用層（8 小時）
- Assessment：功能/品質/效能/創新

---

## Case #5: 在 NoSQL/向量庫以 Tags 儲存與過濾

### Problem Statement
- 業務場景：文件儲存在 NoSQL/向量庫，需以標籤實現授權過濾。
- 技術挑戰：如何設計低基數、可索引的 tags 結構並跨供應商通用。
- 影響範圍：所有檢索與瀏覽 API。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：未定義 tags 結構；自由字串使索引退化；不同庫語法差異。
- 深層原因：
  - 架構：未統一 metadata 模型
  - 技術：缺少 filterable 字段設計
  - 流程：ingestion 未貼標

### Solution Design
- 解決策略：定義標準化 tags 欄位（tenant、catalog、role、user），以枚舉/代碼降低基數，查詢時傳 filters:{ catalog:[…] } 等語法。

- 實施步驟：
  1. Tag 結構與字典
     - 細節：documents.tags = { catalog:["C01"], tenant:["T1"]… }
     - 時間：0.5 天
  2. 查詢適配器
     - 細節：根據供應商輸出對應 filters JSON
     - 時間：1 天

- 關鍵程式碼/設定：
```json
{
  "id": "doc-123",
  "content": "...",
  "tags": {
    "tenant": ["T1"],
    "catalog": ["C01", "C05"],
    "audience": ["role:R1", "user:U:alice"]
  }
}
```

```js
// 檢索請求（示意）
{
  "query": "零件維修手冊",
  "filters": { "tenant": ["T1"], "catalog": ["C01"] }
}
```

- 實際案例：文章建議以 tags+filters 過濾（NoSQL 結構更容易）。
- 實作環境：Cosmos DB、Qdrant、Pinecone、Azure AI Search
- 實測數據：
  - 改善前：無法差異化結果
  - 改善後：同庫支持基本 filters
  - 改善幅度：安全可控、可審計

Learning Points
- 核心：tag 設計、跨庫 filters 適配
- 技能：NoSQL 模型、SDK 使用
- 延伸：keyword/term 類型設定；限制：供應商語義差異；優化：限制 tag 集合大小
- Practice：以 JSON tags 實作檢索（30 分、2 小時、8 小時）
- Assessment：功能/品質/效能/創新

---

## Case #6: ABAC（屬性式）授權降維為 Tags

### Problem Statement
- 業務場景：授權依「部門、地區、資安等級」等屬性決定，需套用到向量檢索。
- 技術挑戰：ABAC 條件動態多樣，如何映射為可索引 tags。
- 影響範圍：國際化、多部門場景。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：屬性條件以動態規則存在，無法直接索引。
- 深層原因：
  - 架構：缺少屬性→tag 映射層
  - 技術：時間/地點等條件難以預先貼標
  - 流程：屬性來源不一致

### Solution Design
- 解決策略：將 ABAC 屬性編碼為有限枚舉 tags（dept:HR、region:APAC、clearance:L2），文件與主體同維度貼標，查詢時取交集。

- 實施步驟：
  1. 屬性標準化
     - 細節：定義部門/地區/等級字典
     - 時間：1 天
  2. 映射實作
     - 細節：屬性→tags；時間條件以會話態參數或索引週期處理
     - 時間：1 天

- 關鍵程式碼/設定：
```csharp
// 屬性轉 tag
var userTags = new Dictionary<string,string[]>
{
  ["dept"] = new[] { user.DepartmentCode },  // e.g., "HR"
  ["region"] = new[] { user.RegionCode },    // e.g., "APAC"
  ["clearance"] = new[] { user.Clearance }   // e.g., "L2"
};
```

- 實際案例：文章指出以 tags+filters 可滿足個人化與安全期待。
- 實作環境：相同
- 實測數據：以設計指標衡量
  - 改善前：ABAC 規則無法落地到檢索
  - 改善後：以枚舉 tags 實作可檢索過濾
  - 幅度：可運行性從 0→可落地

Learning Points：ABAC→tags 的工程化、折衷
- Practice：部門/地區/等級映射（2 小時）
- Assessment：功能/品質/效能/創新

---

## Case #7: PBAC（政策式）編譯為可執行 Filters

### Problem Statement
- 業務場景：授權來自政策（例如「審計期間財務文件僅財務部門可讀」），需落地可執行的查詢過濾。
- 技術挑戰：政策語言到執行層的轉換，與 tags/filters 對齊。
- 影響範圍：合規季節性政策、臨時封鎖。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：政策為文字/規則，不可直接索引。
- 深層原因：
  - 架構：缺少 Policy→Filter 的編譯器
  - 技術：跨來源屬性聚合
  - 流程：政策發布無自動化

### Solution Design
- 解決策略：引入 Policy Evaluation（可用 OPA 或自製），將政策評估為「允許的 tag 集合」與「拒絕集合」，再生成 Filters；必要時預先標註文件的「policy flags」。

- 實施步驟：
  1. 政策解析與評估
     - 細節：將政策語句轉換為屬性條件集合
     - 時間：1-2 天
  2. Filter 生成與注入
     - 細節：policyEval(user, doc) → tags constraints → filters
     - 時間：1 天

- 關鍵程式碼/設定：
```csharp
var policyTags = PolicyEngine.Evaluate(userContext); // e.g., { "catalog": ["FIN"], "period": ["audit-2025Q1"] }
var filters = Merge(subjectTags, policyTags);
var results = await kernelMemory.SearchAsync(new SearchOptions { Query = q, Filters = filters });
```

- 實際案例：文章提到 PBAC（政策）作為常見模型之一。
- 實作環境：.NET 8、Policy 引擎（自製/OPA）
- 實測數據：設計指標
  - 改善前：政策無法控管檢索
  - 改善後：政策可轉 Filters 強制執行
  - 幅度：政策落地能力 0→1

Learning Points：PBAC 工程化、與 tags 橋接
- Practice：將 2 條政策轉為 filters（2 小時）
- Assessment：功能/品質/效能/創新

---

## Case #8: Ingestion 流水線自動貼標（資料貼標）

### Problem Statement
- 業務場景：大量文件持續進來，需保證每份文件含正確 tags。
- 技術挑戰：來源異質、欄位不齊、不一致命名。
- 影響範圍：所有檢索安全。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：手動貼標易漏、來源資訊缺漏。
- 深層原因：
  - 架構：缺貼標節點
  - 技術：抽取/映射規則缺乏
  - 流程：缺驗證與回饋

### Solution Design
- 解決策略：在 ingestion pipeline 加入「標籤擴充節點」，在向量化前完成必需 tags（tenant、catalog、audience 等），缺漏則拒收或打回。

- 實施步驟：
  1. 規則配置
     - 細節：來源欄位→標準化 codes
     - 時間：0.5 天
  2. 流程落地與驗證
     - 細節：CI/CD、抽樣稽核
     - 時間：1 天

- 關鍵程式碼/設定：
```python
# pseudo ingestion step
doc.tags["tenant"] = [source.tenant_code]
doc.tags["catalog"] = map_category(source.path)
doc.tags["audience"] = ["role:R2"] if source.dept=="Sales" else ["role:R3"]
save(doc)  # only after tags are complete
```

- 實際案例：文章主張在「資料」上貼標（5-1）。
- 實作環境：ETL/Worker、.NET/Python 皆可
- 實測數據：
  - 改善前：貼標缺漏、風險高
  - 改善後：標籤完整率提升為可驗證
  - 幅度：缺漏率顯著下降（以驗收準則）

Learning Points：貼標自動化、前置防錯
- Practice：為 100 份文件自動貼標（2 小時）
- Assessment：功能/品質/效能/創新

---

## Case #9: 在人與操作上貼標（Subject/Action Tags）

### Problem Statement
- 業務場景：同一用戶在不同操作（搜尋、摘要、下載）需不同權限；角色與個人例外需同時生效。
- 技術挑戰：將動作語意與個人例外轉為 tags 與 filters。
- 影響範圍：所有 API。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：缺「操作」層級的授權語意；個人例外四散。
- 深層原因：
  - 架構：Subject/Action 模型缺失
  - 技術：filters 不含 action 維度
  - 流程：例外審批無紀錄

### Solution Design
- 解決策略：為會話加入 subject tags（user、role、dept…）與 action tags（READ、SEARCH、SUMMARIZE），在 filter builder 中一併考量。

- 實施步驟：
  1. Action 枚舉與規則
     - 細節：READ/SEARCH/SUMMARIZE/EXPORT
     - 時間：0.5 天
  2. Filter Builder 擴充
     - 細節：行為→限制，例如 SUMMARIZE 僅允許更嚴格集合
     - 時間：1 天

- 關鍵程式碼/設定：
```csharp
var action = "SUMMARIZE";
var actionTags = new Dictionary<string,string[]>{ ["action"] = new[]{ action } };
var filters = Merge(subjectTags, actionTags);
```

- 實際案例：文章提到在「人」或「操作」貼標（5-2）。
- 實作環境：同上
- 實測數據：以設計準則
  - 改善前：操作無差異化
  - 改善後：操作敏感度不同可控
  - 幅度：風險→可控

Learning Points：行為敏感度控制
- Practice：SUMMARIZE 比 SEARCH 更嚴（2 小時）
- Assessment：功能/品質/效能/創新

---

## Case #10: 查詢當下用哪組標籤過濾？Filter Builder 策略

### Problem Statement
- 業務場景：不同情境需選擇不同過濾策略（如租戶必選、角色選配、個人例外合併）。
- 技術挑戰：如何一致、可測地構建 Filters。
- 影響範圍：所有檢索路徑。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：過濾規則散落於各服務。
- 深層原因：
  - 架構：缺 Filter Builder 中心
  - 技術：合併規則不一致
  - 流程：缺單元測試

### Solution Design
- 解決策略：建立 FilterBuilder，規範「必選（must）/可選（should）/禁止（must_not）」三類；租戶與分類為 must，角色/個人為 should，禁入名單為 must_not。

- 實施步驟：
  1. Builder 與規則表
     - 細節：策略配置化
     - 時間：1 天
  2. 單元測試
     - 細節：對多用例生成固定 Filters
     - 時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var fb = new FilterBuilder()
  .Must("tenant", tenantId)
  .Must("catalog", allowedCatalogs)
  .Should("audience", userRoles.Select(r=>$"role:{r}"))
  .Should("audience", new[]{ $"user:U:{userId}" })
  .MustNot("audience", new[]{ $"deny:U:{userId}" });
var filters = fb.Build();
```

- 實際案例：文章（5-3）問「查詢當下要用甚麼標籤過濾？」即此主題。
- 實作環境：同上
- 實測數據：
  - 改善前：規則分散
  - 改善後：可測、可重用
  - 幅度：維護成本明顯下降

Learning Points：策略化 Builder
- Practice：寫 5 個用例測試（2 小時）
- Assessment：功能/品質/效能/創新

---

## Case #11: 多租戶隔離（Tenant Tag 強制）

### Problem Statement
- 業務場景：SaaS 多租戶環境，任何跨租戶資料瀏覽皆不可發生。
- 技術挑戰：在向量檢索層強制租戶隔離。
- 影響範圍：法遵/客戶信任。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：未強制 tenant tag。
- 深層原因：
  - 架構：未將 tenant 納入資料鍵
  - 技術：過濾條件非必選
  - 流程：測試覆蓋不足

### Solution Design
- 解決策略：所有文件與請求必含 tenant tag，FilterBuilder 中 tenant 為 must 條件；無 tenant 一律拒絕。

- 實施步驟：
  1. 強制貼標
     - 細節：tenant 為必填
     - 時間：0.5 天
  2. 中介層驗證
     - 細節：無 tenant 拒請；審計
     - 時間：0.5 天

- 關鍵程式碼/設定：
```csharp
if (!subjectTags.TryGetValue("tenant", out var t) || !t.Any())
  throw new UnauthorizedAccessException("Missing tenant");
// builder.Must("tenant", t) ...
```

- 實際案例：文章示例的 tags+filter 天然支援多租戶。
- 實作環境：同上
- 實測數據：
  - 改善前：有跨租戶風險
  - 改善後：強制 tenant must
  - 幅度：風險→可控/可證明

Learning Points：強制條件與審計
- Practice：寫租戶缺失拒請測試（30 分）
- Assessment：功能/品質/效能/創新

---

## Case #12: 個人例外清單（Allow/Deny）與 RBAC 疊加

### Problem Statement
- 業務場景：除角色外，特定人需讀特定文件或被排除。
- 技術挑戰：如何在 tags 中表達個人 allow/deny 並與角色疊加。
- 影響範圍：精細授權。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：僅靠角色難覆蓋個例。
- 深層原因：
  - 架構：缺合併規則
  - 技術：向量庫對「包含」語義各異
  - 流程：例外核准散落

### Solution Design
- 解決策略：將 audience 設為多值 tags，含「role:R*」「user:U:*」「deny:U:*」。FilterBuilder 使用 Should 合併允許、MustNot 排除。

- 實施步驟：
  1. audience tag 規範
     - 細節：字首區分 role/user/deny
     - 時間：0.5 天
  2. 查詢合併
     - 細節：角色 Should + 個人 Should，Deny MustNot
     - 時間：0.5 天

- 關鍵程式碼/設定：
```json
"audience": ["role:R1","role:R3","user:U:alice","deny:U:bob"]
```

- 實際案例：文章建議以標籤組合降維處理複雜權限。
- 實作環境：同上
- 實測數據：以設計準則
  - 改善前：無法精細控制
  - 改善後：可細緻 allow/deny
  - 幅度：覆蓋率顯著提升

Learning Points：例外處理與語義設計
- Practice：加入 3 個個人例外（30 分）
- Assessment：功能/品質/效能/創新

---

## Case #13: 階層式分類的展開與過濾（C01.* → 叶節點）

### Problem Statement
- 業務場景：分類具階層（C01、C01.01、C01.01.03…），授權在父節點時需涵蓋子節點。
- 技術挑戰：如何在 tags 與查詢層實作展開與一致性。
- 影響範圍：查詢精準度與效能。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：直接匹配父分類將漏子分類。
- 深層原因：
  - 架構：缺展開表或預計算
  - 技術：filters 不支援前綴匹配
  - 流程：分類治理不足

### Solution Design
- 解決策略：建立分類樹與展開表，將父節點授權展開為所有子節點代碼；文件 tags 同時包含自身及所有祖先，支持雙向策略。

- 實施步驟：
  1. 分類樹與展開
     - 細節：materialized path 或 adjacency list
     - 時間：1 天
  2. 查詢策略
     - 細節：以 IN (…) 供 RDB；以多值 tags 供向量庫
     - 時間：0.5 天

- 關鍵程式碼/設定：
```sql
-- 取父節點 C01 的所有子節點
SELECT child.category FROM category_closure WHERE parent='C01';
```

```json
// 文件同時貼祖先
"catalog": ["C01","C01.01","C01.01.03"]
```

- 實際案例：文章建議以 tags 降維到可過濾集合。
- 實作環境：RDB + 向量庫
- 實測數據：
  - 改善前：授權漏匹配
  - 改善後：覆蓋所有子節點
  - 幅度：覆蓋率 100%

Learning Points：階層資料建模
- Practice：為 3 層分類實作展開（2 小時）
- Assessment：功能/品質/效能/創新

---

## Case #14: Filters 的可索引性與效能優化

### Problem Statement
- 業務場景：需要在 100ms 級回應內完成授權過濾與相似度檢索。
- 技術挑戰：filters 若不可索引或基數過大會拖慢查詢。
- 影響範圍：使用者體驗與成本。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：自由字串 tags、未設 filterable/keyword 型別。
- 深層原因：
  - 架構：未將效能納入標籤設計
  - 技術：漏索引/錯誤型別
  - 流程：缺 P95 目標

### Solution Design
- 解決策略：全部 filter 欄位設定為可索引（keyword/term/collection），嚴控 tag 基數與長度；使用枚舉碼表；在供應商層設置 filterable（例如 Azure AI Search 的 filterable:true）。

- 實施步驟：
  1. 型別與索引修正
     - 細節：設 keyword/term、filterable:true
     - 時間：0.5 天
  2. 基數治理
     - 細節：採碼表；拒絕自由字串
     - 時間：0.5 天

- 關鍵程式碼/設定：
```json
// Azure AI Search index field example
{ "name":"catalog", "type":"Collection(Edm.String)", "filterable": true, "facetable": true, "searchable": false }
```

- 實際案例：文章點出效能與個人化的衝突，需以標準化 filters 化解。
- 實作環境：Azure AI Search/Qdrant/Pinecone
- 實測數據：
  - 改善前：查詢延遲不可控
  - 改善後：P95 可達 100ms 目標（設計目標）
  - 幅度：穩定性提升

Learning Points：索引/型別對效能的影響
- Practice：建立索引並壓測（2 小時）
- Assessment：功能/品質/效能/創新

---

## Case #15: 在 RAM 快取 RBAC 矩陣與可讀分類清單

### Problem Statement
- 業務場景：每次查詢需計算可讀分類清單，頻繁 DB 讀取造成延遲。
- 技術挑戰：如何在應用層快取，兼顧一致性。
- 影響範圍：整體延遲與成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：每次查詢即時計算 allow 集合。
- 深層原因：
  - 架構：無快取層
  - 技術：缺 TTL 與失效策略
  - 流程：角色異動通知缺失

### Solution Design
- 解決策略：以 MemoryCache/分散式快取，緩存 role→category 清單與 user→extraAllow/deny；設定 TTL 與變更事件失效。

- 實施步驟：
  1. 快取鍵設計
     - 細節：role:{role}、user:{id}
     - 時間：0.5 天
  2. 失效策略
     - 細節：管理後台變更觸發清除
     - 時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var categories = await cache.GetOrCreateAsync($"role:{role}", async _ =>
{
  _.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10);
  return await db.GetAllowedCategoriesAsync(role);
});
```

- 實際案例：文章建議小表可放 RAM 內，程式直接產生。
- 實作環境：.NET MemoryCache/Redis
- 實測數據：
  - 改善前：每請求查 DB
  - 改善後：命中快取，查詢時間穩定
  - 幅度：查詢開銷顯著降低

Learning Points：快取設計與一致性
- Practice：為 role→category 實作快取（1 小時）
- Assessment：功能/品質/效能/創新

---

## Case #16: RAG 摘要僅基於授權文段（生成前授權門控）

### Problem Statement
- 業務場景：RAG 需要組裝多來源文段讓 LLM 回答，但必須確保文段來源皆為授權集合。
- 技術挑戰：如何在 chunking、rerank、合併過程保持授權約束。
- 影響範圍：最終回答安全。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：組裝階段未檢查授權；Rerank 可能引入非授權來源。
- 深層原因：
  - 架構：RAG pipeline 缺授權檢查點
  - 技術：無 docId 白名單
  - 流程：無集成測試覆蓋

### Solution Design
- 解決策略：以「授權檢索→chunk→rerank（僅授權集合內）→LLM」的封裝流程實作；任何外部片段合併需驗證 docId 在白名單中。

- 實施步驟：
  1. Pipeline 封裝
     - 細節：單一 use case 可重用流程
     - 時間：1 天
  2. 集成測試
     - 細節：未授權文檔必不進入 prompt
     - 時間：0.5-1 天

- 關鍵程式碼/設定：
```csharp
var authorized = await SearchAuthorizedAsync(q, subjectTags);
var chunks = Chunk(authorized);
var reranked = RerankWithin(chunks); // 僅對 chunks 操作
var answer = await Llm.AnswerAsync(reranked, q);
```

- 實際案例：文章強調「不能將文件片段顯示在摘要」，此為實作落地。
- 實作環境：同上
- 實測數據：
  - 改善前：RAG 可能引入未授權片段
  - 改善後：LLM 僅接觸授權文段
  - 幅度：外洩風險→可控

Learning Points：RAG 安全管線
- Practice：寫 3 條測試驗證未授權不進 prompt（2 小時）
- Assessment：功能/品質/效能/創新

--------------------------------
案例分類
--------------------------------
1. 按難度分類
- 入門級：
  - Case 3（RBAC 降維）
  - Case 4（RDB 過濾）
  - Case 5（NoSQL/Tags 過濾）
  - Case 11（多租戶隔離）
  - Case 15（RBAC 快取）
- 中級：
  - Case 2（防外洩：先授權後顯示）
  - Case 8（Ingestion 貼標）
  - Case 9（Subject/Action Tags）
  - Case 10（Filter Builder）
  - Case 13（階層分類展開）
  - Case 14（可索引性與效能）
- 高級：
  - Case 1（MKM 向量檢索授權）
  - Case 6（ABAC→Tags）
  - Case 7（PBAC 編譯）
  - Case 16（RAG 生成前門控）

2. 按技術領域分類
- 架構設計類：Case 1, 2, 3, 6, 7, 10, 16
- 效能優化類：Case 14, 15
- 整合開發類：Case 4, 5, 8, 9, 11, 13
- 除錯診斷類：Case 2, 10, 16（驗證與測試）
- 安全防護類：全部（重點：1,2,6,7,11,16）

3. 按學習目標分類
- 概念理解型：Case 3, 6, 7, 13
- 技能練習型：Case 4, 5, 8, 9, 10, 15
- 問題解決型：Case 1, 2, 11, 14, 16
- 創新應用型：Case 7, 10, 13, 16

--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 先學哪些案例？
  1) RBAC 降維（Case 3）→ 2) RDB/NoSQL 過濾（Case 4, 5）→ 3) 多租戶隔離（Case 11）
- 依賴關係：
  - Case 1（MKM 向量授權）依賴：Case 3/4/5/10/11
  - Case 2（防外洩）依賴：Case 1、Case 16
  - Case 6（ABAC）依賴：Case 3（理解降維思想）
  - Case 7（PBAC）依賴：Case 6（屬性治理）
  - Case 10（Filter Builder）依賴：Case 4/5（查詢/filters 基礎）
  - Case 13（階層分類）依賴：Case 3（分類治理）
  - Case 14（效能）依賴：Case 4/5/10（可索引 filters）
  - Case 15（快取）依賴：Case 3/4（可讀集合來源）
  - Case 16（RAG 門控）依賴：Case 1、Case 2

- 完整學習路徑建議：
  1) Case 3（理解降維與 RBAC 基礎）
  2) Case 4, 5（把授權帶進 SQL/NoSQL/向量 tags）
  3) Case 11（建立多租戶強制隔離觀念）
  4) Case 10（學會統一的 Filter Builder）
  5) Case 13（處理階層分類與展開）
  6) Case 14（學會以索引/型別保證效能）
  7) Case 15（學會用快取控制延遲）
  8) Case 6（將 ABAC 屬性工程化）
  9) Case 7（將政策 PBAC 編譯為 Filters）
  10) Case 1（把以上要素接到 MKM/向量檢索）
  11) Case 2（把安全閘道前移到結果與摘要）
  12) Case 16（確保生成階段僅用授權語料，完成安全 RAG）
