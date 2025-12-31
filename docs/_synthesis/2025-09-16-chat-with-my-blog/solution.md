---
layout: synthesis
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計"
synthesis_type: solution
source_post: /2025/09/16/chat-with-my-blog/
redirect_from:
  - /2025/09/16/chat-with-my-blog/solution/
postid: 2025-09-16-chat-with-my-blog
---
以下為基於原文萃取與重構的 15 個可落地、可教學、可評估的實戰案例。每個案例均涵蓋問題、根因、方案（含實作步驟與程式碼/設定）、實測效益與學習/評估面向。

## Case #1: 從 API-first 轉向 MCP-first 的工作流程導向設計

### Problem Statement（問題陳述）
業務場景：作者希望讓部落格文章被各種 Agent 有效理解並用於解題、寫文件與寫程式。過去以 API-first 或 RAG 直接檢索的方式，讀者仍需大量人工對齊脈絡才能行動，從「看完文章」到「能拿來解題」中間隔著多個門檻。  
技術挑戰：若僅把 REST API 包裝成 MCP，就忽視 Agent 思考脈絡與工作流程，導致工具難以被可靠調用、檢索不精準、幻覺與誤用增加。  
影響範圍：讀者體驗、Agent 整合成效、文件/程式碼產出效率、整體 AI 應用價值。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 把 MCP 當 API 包裝，未針對 Agent 的 context/workflow 設計。  
2. 長文敘事式內容被粗暴切塊後，語義破碎，RAG 找不到「可直接用」的素材。  
3. API 設計偏向 UI 或特定場景，缺乏對領域問題的穩健抽象與防誤用邊界。

深層原因：
- 架構層面：靜態內容缺乏「工作流程優先」的服務層，沒有面向 Agent 的工具化抽象。  
- 技術層面：僅向量檢索與 naive chunking，未引入「合用型態」的內容正規化。  
- 流程層面：延續人類-人類的「檯面下溝通」與 UI 驅動習慣，未轉向 AI 使用者觀點。

### Solution Design（解決方案設計）
解決策略：以 Workflow First 為核心，從使用情境（訂閱/解答/解題/學習）逆推工具清單與交互順序，設計貼近 Agent 工作習慣的 MCP Tools（GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts），並結合前置內容正規化（synthesis）以提升檢索可用度與上下文精度。

實施步驟：
1. 使用情境分解與流程建模  
- 實作細節：盤點常見任務（解答/解題/學習），畫出「人類工程師」會怎麼做，再轉為 Agent 的工具呼叫序。  
- 所需資源：Miro/Whimsical、Notion/Confluence。  
- 預估時間：1-2 人日。

2. MCP Tools 規格擬定  
- 實作細節：定義 Tools 介面與入參（含 synthesis、position/length），讓 Tool 呼叫貼齊流程。  
- 所需資源：MCP 規格、MCP Host（Streamable HTTP）。  
- 預估時間：1 人日。

3. 前處理與索引設計（與 Case #4/#5 串接）  
- 實作細節：將文章蒐整為 origin/solution/faq/summary 等型態，建立檢索索引。  
- 所需資源：LLM、向量資料庫/全文檢索。  
- 預估時間：2-4 人日（視內容量）。

4. 集成與驗證（跨不同 Host / LLM）  
- 實作細節：在 ChatGPT、Claude、VSCode + Copilot 驗證一致性與效能。  
- 所需資源：上述 Hosts、MCP Inspector。  
- 預估時間：1-2 人日。

關鍵程式碼/設定：
```json
// MCP Tools 總覽（示意）
{
  "tools": [
    { "name": "GetInstructions", "description": "取得使用說明與行為準則（動態）" },
    { "name": "SearchChunks", "params": ["query", "synthesis", "limit"] },
    { "name": "SearchPosts", "params": ["query", "synthesis", "limit"] },
    { "name": "GetPostContent", "params": ["postid", "synthesis", "position", "length"] },
    { "name": "GetRelatedPosts", "params": ["postid", "limit"] }
  ]
}
```

實際案例：文內三個示範（問答、整理歷史、vibe coding）均以此工具組合達成。  
實作環境：MCP Host（Streamable HTTP）、ChatGPT Plus（GPT-5 + Thinking Beta）、Claude（Sonnet 4）、VSCode + GitHub Copilot。  
實測數據：  
改善前：RAG 常回傳破碎內容、需大量人工對齊。  
改善後：回答含正確引用連結、具可用片段，能直接產出代碼/文稿。  
改善幅度：作者描述 Q/A 與 coding 產出時間縮短至 1-3 分鐘，整體效率體感提升 10-100 倍。

Learning Points（學習要點）
核心知識點：
- MCP ≠ API：以 context + workflow 設計工具介面  
- 工作流程優先：以人類工程師實際動作抽象為工具  
- 合用型內容：先正規化再檢索，減少幻覺

技能要求：
- 必備技能：API 設計、RAG 基礎、向量檢索  
- 進階技能：Context Engineering、Agent Tooling 設計

延伸思考：
- 此設計可用於任何文件密集型產品（SaaS Docs、內部知識庫）。  
- 風險：若工具太細會造成選擇困難；太粗則無法表達流程。  
- 優化：引入工具分層（發現/規劃/執行）與使用次序約束。

Practice Exercise（練習題）
- 基礎練習：依你的產品列出 3 個核心情境並草擬對應 Tools（30 分鐘）。  
- 進階練習：為某一情境設計 end-to-end Tools 與呼叫序（2 小時）。  
- 專案練習：將一篇長文正規化並串接成可被 MCP 檢索的資源（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：是否覆蓋情境、可被 Agent 正確使用  
- 程式碼品質（30%）：規格清楚、錯誤處理完備  
- 效能優化（20%）：context 控制、檢索精度  
- 創新性（10%）：工具分層與流程設計巧思


## Case #2: 以 GetInstructions 動態注入規則，消滅「檯面下溝通」

### Problem Statement（問題陳述）
業務場景：Agent 是主要使用者，無法事先閱讀人類文件或遵循「默契」。若不把規則顯性化，Agent 可能亂用工具或順序錯誤，導致不可預期行為。  
技術挑戰：傳統將使用說明寫在文件中，LLM 不會主動讀；需把規則動態嵌入上下文且可被 LLM 即時理解。  
影響範圍：工具誤用率、回答一致性、可維護性與上線風險。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 設計仰賴人類閱讀文件，Agent 無法遵循。  
2. 缺少強制性「第一步」以初始化會話狀態與規則。  
3. 工具說明與結果分離，LLM 無法一眼獲得「如何使用」。

深層原因：
- 架構層面：缺乏會話級狀態與上下文啟動機制。  
- 技術層面：Tool response 不包含 instruction，導致 LLM 理解門檻高。  
- 流程層面：仍延續「人類讀文件→再寫程式」的舊習。

### Solution Design（解決方案設計）
解決策略：提供 GetInstructions 作為必叫 Tool，回傳帶有規範、步驟與關鍵參數的 Markdown，讓後續所有 Tool 依此上下文運行；參考 Shopify 的 learn_shopify_api 設計，將「需攜帶的 conversationId」一併注入。

實施步驟：
1. 設計 GetInstructions 回傳格式  
- 實作細節：包含「必須先做什麼」「允許的工具組合」「錯誤處理規範」。  
- 所需資源：LLM Prompt 工程、MCP Server。  
- 預估時間：0.5 人日。

2. 強制順序與校驗  
- 實作細節：要求其他 Tool 無 conversationId（或等價 token）即報錯。  
- 所需資源：Server 端驗證邏輯。  
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```markdown
# GetInstructions（回應示例）
🔗 IMPORTANT: Save session token: 9b2d1c3e-...
Rules:
1) Always call SearchChunks before fetching full content.
2) Pass session token to every tool call.
3) Prefer synthesis=["solution","faq"] for problem-solving.
Errors:
- Missing token -> return E001.
```

實際案例：作者與 Shopify 的「先學 API 再調用」模式一致，能迫使 Agent 遵循規則。  
實作環境：MCP Host、ChatGPT/Claude/VSCode。  
實測數據：  
改善前：偶發工具誤用與順序錯亂。  
改善後：觀察到 Agent 先呼叫 GetInstructions，再按規範操作，回答含正確連結、誤用率顯著下降（定性）。

Learning Points：
- Tool response 內嵌 instruction 的價值  
- 通过會話 token 強制執行順序

Practice Exercise：
- 基礎：撰寫你產品的 GetInstructions 回應草稿（30 分）。  
- 進階：為其他工具加上「缺 token 報錯」機制（2 小時）。  
- 專案：在三個 Host 上驗證初始化一致性（8 小時）。

Assessment Criteria：
- 功能（40%）：是否能一鍵注入規則/會話態  
- 品質（30%）：錯誤處理與文件一致  
- 效能（20%）：上下文最小化  
- 創新（10%）：可延伸性與跨 Host 適配


## Case #3: 兩段式檢索：SearchChunks → GetPostContent，提升精度與上下文控制

### Problem Statement（問題陳述）
業務場景：Agent 要在大量文章中快速找到可用片段，再決定是否拉全文。  
技術挑戰：直接載入全文會爆 context window，直接用 chunks 又難以回溯上下脈絡。  
影響範圍：檢索精度、Token 成本、響應延遲、幻覺風險。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 一次載入過多內容，導致上下文淹沒重點。  
2. HTML 雜訊影響 LLM 解讀。  
3. 查無相關片段時仍硬載入全文造成浪費。

深層原因：
- 架構層面：缺乏先檢索再拉全文的「節流」策略。  
- 技術層面：缺 synthesis 與 position/length 的精細抓取手段。  
- 流程層面：未形成「發現→精讀」的規範化流程。

### Solution Design（解決方案設計）
解決策略：仿 Shopify Docs 的 search_docs_chunks/fetch_full_docs，先以 SearchChunks 找精準片段（含 synthesis 過濾），必要時再用 GetPostContent 依 position/length 擷取局部，既保留上下文，又限制 Token。

實施步驟：
1. 設計 chunks 檢索  
- 實作細節：允許多次迭代查詢與不同 synthesis 組合。  
- 所需資源：向量檢索、全文索引。  
- 預估時間：1 人日。

2. 分段拉取內容  
- 實作細節：GetPostContent 支援 position/length，以小窗口載入。  
- 所需資源：MCP Tool handler。  
- 預估時間：0.5 人日。

3. Host 行為驗證  
- 實作細節：對比 Claude（一次檢索）與 GPT（兩次檢索）的行為差異。  
- 所需資源：兩組 LLM Host。  
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```json
// SearchChunks（實際示例之一）
{
  "query": "微服務 分散式 交易 Saga Outbox 兩階段提交",
  "synthesis": "summary",
  "limit": 8
}
```
```json
// GetPostContent 擷取局部（示意）
{
  "postid": "2019-06-15-netcli-pipeline",
  "synthesis": "solution",
  "position": 12000,
  "length": 2500
}
```

實際案例：ChatGPT（兩段檢索）與 Claude（單段檢索）皆能正確作答並附上引用連結。  
實作環境：ChatGPT Plus（GPT-5 + Thinking）、Claude Sonnet 4。  
實測數據：  
改善前：一次拉全文常超限、或資訊過量無重點。  
改善後：回答更精確，引用正確，未觀察到幻覺；回應延遲與 Token 使用可控（定性）。

Learning Points：
- 「先檢索再拉取」的節流策略  
- 以 synthesis 過濾片段，控制語義用途

Practice Exercise：
- 基礎：為你的文庫設計 chunks 結構與檢索 API（30 分）。  
- 進階：加入 position/length 的局部提取（2 小時）。  
- 專案：對比單次全文與兩段式檢索的 Token/延遲（8 小時）。

Assessment Criteria：
- 功能（40%）：檢索與提取是否可閉環  
- 品質（30%）：結果可用性與引用正確  
- 效能（20%）：上下文/Token 控制  
- 創新（10%）：檢索策略的自動化與迭代化


## Case #4: 內容正規化（synthesis）讓長文變成「可用」素材

### Problem Statement（問題陳述）
業務場景：作者文章常以完整思路（情境→問題→PoC→解法）書寫，對人易懂、對 RAG 難用。  
技術挑戰：切塊後語義破碎，無法對應具體工作需要。  
影響範圍：檢索精度、Agent 產出品質、整體體驗。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 長文敘事性強，切塊未對齊任務單位。  
2. 缺少面向「解答/解題/FAQ」的可用結構。  
3. 過度依賴原文片段與向量相似度。

深層原因：
- 架構層面：缺少內容層「用途導向」的語義變形。  
- 技術層面：未引入 LLM 預生成（synthesis）層。  
- 流程層面：發布流程未包含正規化步驟。

### Solution Design（解決方案設計）
解決策略：在發布管線中，以 LLM 將長文抽煉為 origin/solution/faq/summary 等用途導向的結構化單位，索引時以 synthesis 為主要檢索條件，顯著提升可用度與對答精準度。

實施步驟：
1. 定義 synthesis schema  
- 實作細節：字段包含 type、source_postid、title、body、tags、citations。  
- 所需資源：Schema 設計。  
- 預估時間：0.5 人日。

2. 設計抽煉 Prompt 與流程  
- 實作細節：以「用途」為核心生成內容，保留引用鏈接。  
- 所需資源：LLM + 批量處理。  
- 預估時間：1-2 人日。

3. 建立索引與檢索  
- 實作細節：以 synthesis type + 向量/關鍵詞雙檢索。  
- 所需資源：向量 DB/全文索引。  
- 預估時間：1 人日。

關鍵程式碼/設定：
```json
// synthesis 單元（示例）
{
  "type": "solution",
  "source_postid": "2024-07-20-devopsdays-keynote",
  "title": "API -> AI First 的兩大原則",
  "body": "做到合情合理與足夠可靠...（略）",
  "citations": ["https://.../2024/07/20/devopsdays-keynote/"],
  "tags": ["API設計","AI First"]
}
```
```markdown
// 生成 Prompt（片段）
請將以下長文萃取為 solution 與 faq 兩種型態：
- 每個條目不超過 200 字，附原文引用 URL
- solution 側重可執行步驟；faq 側重快問快答
```

實際案例：作者以此法完成正規化並稱「花不少 token，但很值得」。  
實作環境：LLM（Azure 額度支援）、索引服務。  
實測數據：  
改善前：RAG 拉回內容「不可直接用」。  
改善後：Q/A 與 coding 產出品質顯著提升，引用準確；體感 10-100 倍效率（定性）。

Learning Points：
- 以「用途」為核心的內容工程  
- 抽煉與引用鏈接同時保留

Practice Exercise：
- 基礎：為一篇技術文生成 5 個 faq/solution 單元（30 分）。  
- 進階：建立可重複的抽煉腳本與索引（2 小時）。  
- 專案：為 10 篇文章完成正規化與檢索（8 小時）。

Assessment Criteria：
- 功能（40%）：能檢索到合用單元  
- 品質（30%）：內容正確、引用完整  
- 效能（20%）：索引/查詢延遲  
- 創新（10%）：synthesis schema 設計巧思


## Case #5: 發布即抽煉：將正規化併入發行管線

### Problem Statement（問題陳述）
業務場景：每次發文都要手動整理與抽煉，成本高且不穩定。  
技術挑戰：如何在「發布」當下即完成 LLM 抽煉與索引，降低互動時延。  
影響範圍：維運成本、品質穩定度、互動體驗。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 抽煉流程與發行脫鉤，造成遺漏與延遲。  
2. 手動流程易出錯，品質不一。  
3. 查詢時才動態抽煉，延遲高、成本不可控。

深層原因：
- 架構層面：缺 CI/CD 化的內容處理流水線。  
- 技術層面：缺批量 LLM 任務與索引更新腳本。  
- 流程層面：發行流程未納入 AI 任務。

### Solution Design（解決方案設計）
解決策略：在文章發布 Pipeline（如 GitHub Pages/Actions）加入抽煉 Job：渲染前抓原文→LLM 生成 synthesis 單元→寫入索引→驗證引用，確保「發佈即可用」。

實施步驟：
1. 設計發佈流程 Hook  
- 實作細節：提交 PR → Actions 觸發抽煉 → 更新索引。  
- 所需資源：CI/CD。  
- 預估時間：0.5-1 人日。

2. 批量抽煉與索引更新  
- 實作細節：並行處理多篇、失敗重試。  
- 所需資源：LLM、索引服務。  
- 預估時間：1-2 人日。

關鍵程式碼/設定：
```yaml
# .github/workflows/publish.yml（示意）
jobs:
  synthesize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run synthesis
        run: |
          python tools/synthesize.py --post ${{ github.sha }}
      - name: Update index
        run: |
          python tools/update_index.py
```

實際案例：作者指出「在發布文章時預先用 LLM 處理」，提升 MCP+Agent 的效果。  
實作環境：GitHub Pages/Actions（或等效）、LLM、索引。  
實測數據：  
改善前：互動時才抽煉，延遲高。  
改善後：互動即回應、引用齊全、品質穩定（定性）。

Learning Points：
- 將 AI 任務納入 CI/CD  
- 預算（token）與時延的前置換後

Practice Exercise：
- 基礎：為單篇文章串接一個抽煉步驟（30 分）。  
- 進階：對 10 篇文章批量抽煉與索引（2 小時）。  
- 專案：建立完整「發佈即抽煉」管線（8 小時）。

Assessment Criteria：
- 功能（40%）：發佈後可檢索合用單元  
- 品質（30%）：索引一致性、失敗重試  
- 效能（20%）：互動延遲  
- 創新（10%）：自動化與監控設計


## Case #6: 控制 Context Window：position/length 的精細提取

### Problem Statement（問題陳述）
業務場景：LLM 上下文窗限制與「爆量」資訊會拖垮回答品質。  
技術挑戰：如何只載入「必要片段」，又保留足夠脈絡避免誤解。  
影響範圍：回答精準度、Token 成本、回應時間。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 一次性載入全文造成資訊淹沒。  
2. 缺少局部提取機制。  
3. 對 HTML/格式雜訊無節制。

深層原因：
- 架構層面：缺精準內容切片策略。  
- 技術層面：Tool 入參不支持窗口化。  
- 流程層面：未規範「先檢索後提取」的最小上下文原則。

### Solution Design（解決方案設計）
解決策略：GetPostContent 支援 position/length 以「視窗」抽取局部內容，搭配 SearchChunks 定位切入點；原始內容使用 Markdown 提高訊息密度、減少格式雜訊。

實施步驟：
1. 定位與視窗化  
- 實作細節：先以 chunk 命中位置，計算窗口（含上下文 buffer）。  
- 所需資源：索引帶位移訊息。  
- 預估時間：0.5 人日。

2. Markdown 優先  
- 實作細節：內容正規化輸出 Markdown，降低 HTML 雜訊。  
- 所需資源：轉換工具。  
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```json
{
  "tool": "GetPostContent",
  "args": { "postid": "2024-01-15-archview-llm", "position": 8000, "length": 2000, "synthesis": "origin" }
}
```

實際案例：作者強調避免「爆量」資訊灌入 context，回答品質與效率更穩定。  
實作環境：MCP Tools。  
實測數據：  
改善前：回覆冗長卻不聚焦。  
改善後：回答緊扣重點、引用正確，Token 可控（定性）。

Learning Points：
- 視窗化策略與上下文工程  
- Markdown 作為 LLM 友善格式

Practice Exercise：
- 基礎：為某文章實作 2 個不同窗口提取（30 分）。  
- 進階：根據 chunk 命中結果自動計算窗口（2 小時）。  
- 專案：建立端到端窗口化檢索流程（8 小時）。

Assessment Criteria：
- 功能（40%）：能準確抽取局部且可重現  
- 品質（30%）：回答聚焦與引用  
- 效能（20%）：Token 與時延控制  
- 創新（10%）：窗口計算策略


## Case #7: 清理技術債：HTML→Markdown、修圖徑、中文檔名正規化

### Problem Statement（問題陳述）
業務場景：歷史文章中大量 HTML、破損圖片連結、中文檔名、URL 混亂，阻礙 RAG 與 MCP 工具穩定運行。  
技術挑戰：規模化轉換與修復，且不破壞既有內容與 SEO。  
影響範圍：檢索精度、管線穩定、作者日常寫作效率。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 早期遷移「能動就好」留下技術債。  
2. 非結構化 HTML 與錯誤路徑破壞可檢索性。  
3. 中文檔名與多來源圖片路徑難以批次處理。

深層原因：
- 架構層面：Repo 結構與命名未標準化。  
- 技術層面：缺少批量轉換與連結校驗工具。  
- 流程層面：未將資料清理納入發佈前必經步驟。

### Solution Design（解決方案設計）
解決策略：利用 AI IDE（VSCode + Copilot）與腳本進行一次性重構：HTML→Markdown、檔名英文化、圖片/內外鏈校正、建立轉址對照表；同步整理 Repo 結構與本地/雲端路徑。

實施步驟：
1. 批次轉換與檔名正規化  
- 實作細節：HTML→Markdown（保留語意塊）、中文→英文檔名。  
- 所需資源：pandoc/自製腳本、Copilot。  
- 預估時間：1-2 人日。

2. 連結修復與對照表  
- 實作細節：生成 URL Mapping（含 Disqus/舊域名）。  
- 所需資源：Python/Node 腳本。  
- 預估時間：1 人日。

關鍵程式碼/設定：
```python
# rename_fix.py（片段）
import re, os, unicodedata

def slugify(name):
    nfkd = unicodedata.normalize('NFKD', name)
    return re.sub(r'[^a-zA-Z0-9._-]+', '-', nfkd).strip('-').lower()

for root, _, files in os.walk("posts"):
    for f in files:
        nf = slugify(f)
        if nf != f:
            os.rename(os.path.join(root, f), os.path.join(root, nf))
```

實際案例：作者以 AI IDE 完成一次性重構，寫作體驗提升。  
實作環境：VSCode + Copilot、Python/Node。  
實測數據：  
改善前：約 60-70% 舊文為 HTML、連結常壞，發佈與檢索不穩。  
改善後：管線順暢、檢索更準、作者寫作阻力大幅下降（定性）。

Learning Points：
- 技術債清理優先順序  
- 借力 AI IDE 提升批處效率

Practice Exercise：
- 基礎：選 5 篇 HTML 文章轉成 Markdown（30 分）。  
- 進階：寫腳本自動修圖徑與內鏈（2 小時）。  
- 專案：全站轉換與 URL 映射表產生（8 小時）。

Assessment Criteria：
- 功能（40%）：轉換完整、鏈接可用  
- 品質（30%）：Markdown 語意保留  
- 效能（20%）：批處卓越性  
- 創新（10%）：IDE + 腳本協作策略


## Case #8: 「Chat with My Blog」：問答型代理應用的落地

### Problem Statement（問題陳述）
業務場景：使用者希望以聊天方式查詢作者對微服務分散式交易的觀點與解法，並獲得可用引用。  
技術挑戰：LLM 必須精準引用，避免幻覺，並能跨 Host（ChatGPT、Claude）穩定工作。  
影響範圍：讀者體驗、Agent 信任度、傳播效果。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直接 RAG 容易抽到破碎片段。  
2. 工具誤用或順序錯亂導致回答偏移。  
3. HTML 雜訊與過度上下文。

深層原因：
- 架構層面：缺 synthesis 與兩段式檢索。  
- 技術層面：未以工具設計貼齊問答流程。  
- 流程層面：初始化規則未注入。

### Solution Design（解決方案設計）
解決策略：以 GetInstructions 初始化、SearchChunks 精準檢索（synthesis=origin/solution/faq）、必要時 GetPostContent 視窗提取；跨模型測試比較思考路徑差異但保證輸出一致性。

實施步驟：
1. 啟動與檢索  
- 實作細節：先 GetInstructions，後 SearchChunks（兩次迭代亦可）。  
- 所需資源：MCP Tools。  
- 預估時間：即時。

2. 引用與回答生成  
- 實作細節：答案附引用鏈接，避免幻覺。  
- 所需資源：LLM。  
- 預估時間：即時。

關鍵程式碼/設定：
```json
// ChatGPT 的兩次查詢（節錄）
{ "query":"微服務 分散式 交易 ... 可靠投遞", "synthesis":"summary", "limit":8 }
{ "query":"Saga 兩階段提交 TCC Outbox ...", "synthesis":"summary", "limit":8 }
```

實際案例：兩個 Host 回答皆正確且附引用；ChatGPT 表述更潤飾、Claude 更工整。  
實作環境：ChatGPT Plus（GPT-5 + Thinking）、Claude Sonnet 4。  
實測數據：  
改善前：需要人工 Google + 筛選。  
改善後：1 分鐘內獲得可用答案與正確引用，未觀察到幻覺（定性）。

Learning Points：
- 不同 LLM 行為差異與工具設計的穩定化作用  
- 引用鏈接在建立信任中的關鍵性

Practice Exercise：
- 基礎：為你的文庫設計一則問答並附 3 個引用（30 分）。  
- 進階：在兩個不同 Host 驗證一致性（2 小時）。  
- 專案：完成可重放的問答測試套件（8 小時）。

Assessment Criteria：
- 功能（40%）：準確回答 + 引用  
- 品質（30%）：可讀性與一致性  
- 效能（20%）：回應時間與 Token  
- 創新（10%）：跨 Host 驗證方法


## Case #9: 研究整理任務自動化：生成「部落格演進史」

### Problem Statement（問題陳述）
業務場景：作者想在 20 週年回顧中整理多次系統改版歷程，手工蒐集與編排耗時且易漏。  
技術挑戰：需在 VSCode 內直接完成蒐整、過濾、編排與引用。  
影響範圍：寫作效率、正確性、可讀性。  
複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 訊息分散於多篇文章與年份。  
2. 手工 Google/Finder 成本高。  
3. 編排標準不一致。

深層原因：
- 架構層面：缺少針對「編年整理」的檢索工具。  
- 技術層面：未充分利用 MCP 在 IDE 內的整合。  
- 流程層面：寫作與蒐整未一體化。

### Solution Design（解決方案設計）
解決策略：在 VSCode + Copilot 的 Agent 模式下，使用 MCP 蒐整目標主題的文章，生成統一 Markdown 清單（年份/主題/子項/引用），直接貼入當前文稿。

實施步驟：
1. 提供結構化指令  
- 實作細節：指定輸出格式（年份 → 主項 → 子項 → 參考文章）。  
- 所需資源：MCP + Copilot。  
- 預估時間：1 分鐘。

2. 自動插入與人工校對  
- 實作細節：AI 產出後在編輯器中微調。  
- 所需資源：VSCode。  
- 預估時間：3-5 分鐘。

關鍵程式碼/設定：
```markdown
// VSCode Agent 指令（實際片段）
請幫我填上這段 markdown 區段
幫我整理 "安德魯的部落格" 歷年來移轉系統的記錄當作主要項目清單
...（略，見原文）
```

實際案例：1 分鐘完成初稿，品質「蠻正確」，過去需一個晚上人工完成。  
實作環境：VSCode + GitHub Copilot + MCP。  
實測數據：  
改善前：人工蒐整/編排需數小時。  
改善後：1-3 分鐘完成初稿並可立即校對，效率數十倍提升（定性）。

Learning Points：
- 將「研究蒐整」變成 IDE 內嵌工作流  
- 以格式約束引導 Agent 產出

Practice Exercise：
- 基礎：為任一主題產生時間序彙整（30 分）。  
- 進階：加入引用連結與摘要（2 小時）。  
- 專案：生成「專題索引頁」並自動維護（8 小時）。

Assessment Criteria：
- 功能（40%）：清單完整與引用正確  
- 品質（30%）：結構一致、可讀  
- 效能（20%）：產出速度  
- 創新（10%）：IDE 工作流設計


## Case #10: Vibe Coding：用文章驅動 Code 生成（C# Pipeline CLI）

### Problem Statement（問題陳述）
業務場景：讀者想依作者文章（.NET CLI + Pipeline 平行處理）快速做出可運行的 PoC。  
技術挑戰：將文章概念對應到現代語法與最佳實踐（例：Channel 取代 BlockingCollection），並自動產出可測試腳本與假資料。  
影響範圍：學習曲線、PoC 速度、代碼質量。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 讀者將概念落地為碼存在門檻。  
2. 舊文技術棧與現在有差距。  
3. 測試資料與腳本準備繁瑣。

深層原因：
- 架構層面：缺 MCP 幫讀者快速找到「可用片段」。  
- 技術層面：未把「code 生成」納入工作流。  
- 流程層面：學習→實作→驗證未一體化。

### Solution Design（解決方案設計）
解決策略：在 VSCode + Copilot 中，以 MCP 搜尋相關文章與 chunks，將重點片段放入上下文，要求 Agent 生成現代 C# 程式碼（Channel + async）、測試資料（JSONL）與測試腳本（bash），讀者只需補上處理邏輯。

實施步驟：
1. 檢索與上下文佈局  
- 實作細節：SearchPosts → GetPostContent(solution) → SearchChunks（關鍵詞）。  
- 所需資源：MCP + Copilot。  
- 預估時間：1 分鐘。

2. 生成與試跑  
- 實作細節：生成 Program.cs、JSONL 與 shell；本機直接跑。  
- 所需資源：.NET SDK。  
- 預估時間：5 分鐘。

關鍵程式碼/設定：
```csharp
// 片段（見原文）
static async Task ProcessDataInParallel(int parallelism) {
    var channel = System.Threading.Channels.Channel.CreateBounded<UserItem>(100);
    ...
}
```
```bash
# 測試腳本（片段）
cat test-data.jsonl | dotnet run --project src/pipeline-cli/ -- 2 2>/dev/null | head -n 3
```

實際案例：不到 1 分鐘生成程式碼，總計 5 分鐘內完成測試。  
實作環境：VSCode + Copilot、.NET。  
實測數據：  
改善前：學習→實作→測試需數小時。  
改善後：5 分鐘內可跑，語法/框架更新到當代最佳實踐（定性）。

Learning Points：
- 用文章驅動 Code 生成  
- 讓 Agent 補齊測試資料與腳本

Practice Exercise：
- 基礎：為 CLI 加入錯誤重試/重排（30 分）。  
- 進階：加入背壓與超時策略（2 小時）。  
- 專案：封裝成可重用的 Pipeline SDK（8 小時）。

Assessment Criteria：
- 功能（40%）：可運行且易擴展  
- 品質（30%）：現代語法與錯誤處理  
- 效能（20%）：並行與資源控制  
- 創新（10%）：生成到測試一體化


## Case #11: 工具爆炸問題的洋蔥式分層（發現/規劃/執行）

### Problem Statement（問題陳述）
業務場景：當工具數量龐大，LLM 難以選擇正確工具與順序，導致效率與可靠性下降。  
技術挑戰：需要在多工具間展現「先發現→再規劃→後執行」的可解釋路徑。  
影響範圍：Agent 工具選擇正確率、回答質量、可維護性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 工具平鋪直敘，無層次與約束。  
2. 缺乏「先學再做」的強制步驟。  
3. 缺少工具之間的依賴描述。

深層原因：
- 架構層面：工具體系缺分層與引導。  
- 技術層面：未在 Tool response 提供使用策略。  
- 流程層面：忽視 LLM 的規劃/反思階段。

### Solution Design（解決方案設計）
解決策略：引入洋蔥式分層——發現（GetInstructions/learn_*）、規劃（SearchChunks/resolve-*）、執行（GetPostContent/fetch_*），在工具描述中嵌入使用策略與示例。

實施步驟：
1. 工具分層設計  
- 實作細節：為發現層工具返回會話 token/指引。  
- 所需資源：MCP。  
- 預估時間：0.5 人日。

2. 工具說明豐富化  
- 實作細節：以 Markdown 在回應中內嵌「怎麼選」「怎麼串」。  
- 所需資源：文檔與模板。  
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```markdown
// 發現層 response（示意）
Step 1: Use SearchChunks to find candidates.
Step 2: For top-2 posts, call GetPostContent with a 2KB window.
Step 3: If code examples are needed, include synthesis=["solution"].
```

實際案例：參考 Block/Shopify 的最佳實踐。  
實作環境：MCP + LLM Hosts。  
實測數據：  
改善前：工具誤選、冗餘呼叫。  
改善後：觀察到更穩定的選擇與序列（定性）。

Learning Points：
- 把「使用指南」放進工具回應  
- 層次化工具體系降低選擇困難

Practice Exercise：
- 基礎：為你的工具集劃分三層（30 分）。  
- 進階：為發現層工具撰寫可操作指南（2 小時）。  
- 專案：建立工具序列驗證器（8 小時）。

Assessment Criteria：
- 功能（40%）：分層清晰且可執行  
- 品質（30%）：說明可被 LLM 理解  
- 效能（20%）：冗餘呼叫減少  
- 創新（10%）：序列驗證策略


## Case #12: 會話級防護：conversationId 強制初始化（借鏡 Shopify）

### Problem Statement（問題陳述）
業務場景：確保 Agent 先讀規則、再用工具，否則其他工具報錯，避免「亂跑」。  
技術挑戰：如何在無人監管下強制執行正確起手式。  
影響範圍：可靠性、安全邊界、誤用率。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. LLM 可能直接調用執行層工具。  
2. 缺少會話級狀態限制。  
3. 工具間無共通約束。

深層原因：
- 架構層面：未設計會話憑證鏈。  
- 技術層面：工具缺依賴參數（token/id）。  
- 流程層面：初始化規則未被強制。

### Solution Design（解決方案設計）
解決策略：仿 Shopify learn_shopify_api，GetInstructions 返回 conversationId，所有其他工具必須帶此 id，否則回傳錯誤；同時以 Markdown 明確說明此規則。

實施步驟：
1. 生成與驗證  
- 實作細節：會話建立返回 id，後續工具驗證。  
- 所需資源：MCP Server。  
- 預估時間：0.5 人日。

2. 報錯與指引  
- 實作細節：缺 id 時返回 E001 並引導「先呼叫 GetInstructions」。  
- 所需資源：錯誤碼規格。  
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```markdown
// GetInstructions（節錄）
🔗 Save conversationId: 5f53b794-...
⚠️ ALL OTHER TOOLS WILL FAIL without this id.
```

實際案例：Shopify 工具明確採此策略；作者自家 MCP 採用類似精神（必先讀規則）。  
實作環境：MCP Hosts。  
實測數據：  
改善前：偶發誤用。  
改善後：實測中觀察到先調用初始化工具再進行下一步，誤用顯著下降（定性）。

Learning Points：
- 以會話級憑證構建「流程閘門」  
- 異常即教育：錯誤訊息也是 instructions

Practice Exercise：
- 基礎：為你的工具集加入 conversationId（30 分）。  
- 進階：為缺 id 狀況設計可修復錯誤（2 小時）。  
- 專案：加入會話續存/超時策略（8 小時）。

Assessment Criteria：
- 功能（40%）：強制初始化生效  
- 品質（30%）：錯誤提示引導性  
- 效能（20%）：誤用率降低  
- 創新（10%）：會話管理策略


## Case #13: 在 Tool 回應中嵌入使用指引（借鏡 Context7）

### Problem Statement（問題陳述）
業務場景：LLM 在得到工具回應時，若同時拿到「如何挑選/下一步怎麼做」的指南，能即時決策。  
技術挑戰：回應需同時承載結果與指令，且被 LLM 易讀。  
影響範圍：工具接力效率、回答穩定性、幻覺率。  
複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 工具回應只給結果，不教怎麼用。  
2. LLM 無法在同輪次內學到規則。  
3. JSON 雖結構化但不利人/LLM 閱讀策略。

深層原因：
- 架構層面：忽視回應內嵌指引的設計空間。  
- 技術層面：缺少 Markdown 格式指引。  
- 流程層面：未將「回答即是操作說明」融入設計。

### Solution Design（解決方案設計）
解決策略：參考 Context7「resolve-library-id」回應，同步返回「如何選擇」「信任分數」「下一步建議」的 Markdown，使 LLM 立即在同一輪中做決策。

實施步驟：
1. Response 模板設計  
- 實作細節：結果 + 使用規則 + 排序依據（score）。  
- 所需資源：Markdown 模板。  
- 預估時間：0.5 人日。

2. LLM 驗證  
- 實作細節：確保模型能抽取關鍵字段並遵循建議。  
- 所需資源：Host 測試。  
- 預估時間：0.5 人日。

關鍵程式碼/設定：
```markdown
Available Libraries (top matches):
- ID: /mongodb/docs | Snippets: 120 | Trust: 9.0
Usage:
- Pick by name match + trust score + snippet coverage.
Next:
- Call get-library-docs with selected ID.
```

實際案例：作者用 MCP Inspector 檢視 Context7，發現其回應即為行動指引。  
實作環境：MCP + LLM Hosts。  
實測數據：  
改善前：二次查詢策略不一、接力不穩。  
改善後：在同輪中完成決策與調用，穩定性提升（定性）。

Learning Points：
- Markdown 作為可被 LLM 直接「閱讀」的指令載體  
- 在結果中摻入策略性提示

Practice Exercise：
- 基礎：為一個查詢工具加入「下一步建議」（30 分）。  
- 進階：為結果集加入評分與排序依據（2 小時）。  
- 專案：建立回應模板庫並套用至 3 個工具（8 小時）。

Assessment Criteria：
- 功能（40%）：結果與指引兼備  
- 品質（30%）：LLM 易讀/易用  
- 效能（20%）：接力成功率  
- 創新（10%）：評分/排序設計


## Case #14: 即時取用版本正確、來源可靠的官方文件（借鏡 Context7）

### Problem Statement（問題陳述）
業務場景：LLM 基於舊訓練資料易產生過期/幻覺 API。  
技術挑戰：需要「當下版本、來源可信」的文件與程式碼片段。  
影響範圍：代碼可運行性、正確性、開發效率。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 模型知識陳舊。  
2. 官方文件與範例分散。  
3. 缺乏版本與主題聚焦檢索。

深層原因：
- 架構層面：缺官方來源的即時拉取能力。  
- 技術層面：版本/主題入參未暴露。  
- 流程層面：開發中需人工切換頁籤。

### Solution Design（解決方案設計）
解決策略：參考 Context7：先用 resolve-library-id 找到對應文庫 ID，再以 get-library-docs 帶入主題/Token 上限抓取對應片段與程式碼；將這一思路套入自家 MCP 或集成 Context7 作輔助源。

實施步驟：
1. 庫 ID 解析  
- 實作細節：使用名稱 → ID，並帶信任分數。  
- 所需資源：Context7 MCP。  
- 預估時間：即時。

2. 主題化抓取  
- 實作細節：指定 topic 與 tokens 上限。  
- 所需資源：Context7 MCP。  
- 預估時間：即時。

關鍵程式碼/設定：
```json
// resolve-library-id（片段）
{ "libraryName": "shopify functions" }
```
```json
// get-library-docs（片段）
{ "context7CompatibleLibraryID": "/shopify/function-examples", "topic": "admin api graphql product query auth", "tokens": 4000 }
```

實際案例：Context7 返回帶來源與語言標註的可用程式碼片段。  
實作環境：Context7 MCP。  
實測數據：  
改善前：LLM 產生過期或不存在的 API。  
改善後：回傳即用、來源可信、減少幻覺（定性）。

Learning Points：
- 外掛官方文庫即時檢索  
- 以 topic/tokens 精準控制

Practice Exercise：
- 基礎：用 Context7 拉取 2 個庫的 3 段範例（30 分）。  
- 進階：把結果整合回你的工具流（2 小時）。  
- 專案：做一個「官方文庫助理」MCP 插件（8 小時）。

Assessment Criteria：
- 功能（40%）：正確拉取與聚焦主題  
- 品質（30%）：來源可信與版本正確  
- 效能（20%）：Token 控制  
- 創新（10%）：集成策略


## Case #15: API First → AI First：以領域問題為核心的介面與邊界

### Problem Statement（問題陳述）
業務場景：未來 API 的主要調用者是 AI，不能再假定是懂業務的人類工程師。  
技術挑戰：介面需「合情合理」且「可靠」，即便被亂調用也守得住邊界。  
影響範圍：平台長期可用性、整合生態、開發成本。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. UI 導向設計導致介面偏斜。  
2. 以人類默契補足的缺陷在 AI 前不成立。  
3. 邊界檢查鬆散。

深層原因：
- 架構層面：未以 Domain Service 思維開放能力。  
- 技術層面：缺少一致錯誤碼、驗證、節流。  
- 流程層面：未以 AI 為第一使用者設計。

### Solution Design（解決方案設計）
解決策略：以領域問題抽象介面，建立一致驗證（如 conversationId）、錯誤碼與限制策略；工具描述語義清晰、貼近常理，讓 LLM「一看就懂」。

實施步驟：
1. 介面重設  
- 實作細節：針對「解答/解題/學習」定義標準查詢與資源提取。  
- 所需資源：Domain 建模。  
- 預估時間：1 人日。

2. 防禦性設計  
- 實作細節：節流、錯誤碼、一致驗證。  
- 所需資源：MCP Server。  
- 預估時間：0.5-1 人日。

關鍵程式碼/設定：
```json
// SearchPosts（Domain 對齊示例）
{
  "query": "分散式交易 Saga TCC Outbox",
  "synthesis": ["solution","faq"],
  "limit": 10
}
```

實際案例：作者列出兩大原則（合情合理、可靠），並在自家 MCP 落地。  
實作環境：MCP Host。  
實測數據：  
改善前：AI 調用不可預期、錯誤隱性。  
改善後：調用行為可預期、回覆品質穩定（定性）。

Learning Points：
- 以 AI 為主要使用者的介面設計  
- 常理導向與防禦性實踐

Practice Exercise：
- 基礎：重寫 1 個 UI 導向 API 成 Domain 導向（30 分）。  
- 進階：加入錯誤碼/節流與文檔（2 小時）。  
- 專案：以 AI First 為準則重繪子系統介面（8 小時）。

Assessment Criteria：
- 功能（40%）：介面完整與易懂  
- 品質（30%）：防禦性與一致性  
- 效能（20%）：穩定與延遲  
- 創新（10%）：規範化與可移植性


## Case #16: 多 Host/模型一致性設計：兼容 ChatGPT、Claude、VSCode + Copilot

### Problem Statement（問題陳述）
業務場景：使用者可能在不同 Host（ChatGPT/Claude/VSCode）使用同一 MCP；設計需保證行為一致與產出可用。  
技術挑戰：不同模型思考路徑不同（如一次 vs 兩次檢索），工具要容忍差異且引導到正確答案。  
影響範圍：產品可用性、跨平台體驗、維運成本。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不同 Host 的工具使用策略有差異。  
2. 若工具接口設計脆弱，易被「不同風格」誤導。  
3. 缺乏跨 Host 的一致性驗證。

深層原因：
- 架構層面：工具設計未對齊「共同最小集合」。  
- 技術層面：缺 fallback 與多輪檢索容忍。  
- 流程層面：未建立跨 Host 測試。

### Solution Design（解決方案設計）
解決策略：工具入參與回應保持簡潔清晰（query/synthesis/limit/position/length），允許多輪檢索、視窗提取；以初始化指令統一工作流；在三個 Host 上進行行為回放測試。

實施步驟：
1. 工具穩健性  
- 實作細節：參數命名直觀、容忍冪等與多輪檢索。  
- 所需資源：MCP。  
- 預估時間：0.5 人日。

2. 跨 Host 測試  
- 實作細節：同題回放於 ChatGPT/Claude/VSCode。  
- 所需資源：三個 Host。  
- 預估時間：0.5-1 人日。

關鍵程式碼/設定：
```json
// SearchChunks（通用入參）
{ "query": "微服務 分散式 交易", "synthesis": ["origin","solution","faq"], "limit": 10 }
```

實際案例：作者以同題測試三 Host，皆得到正確與引用完整的回答/產出。  
實作環境：ChatGPT、Claude、VSCode + Copilot。  
實測數據：  
改善前：跨平台體驗不一致。  
改善後：產出一致、引用正確、可用性高（定性）。

Learning Points：
- 設計「共同最小集合」工具  
- 為差異建立容錯與回放測試

Practice Exercise：
- 基礎：在兩個 Host 回放同題（30 分）。  
- 進階：設計跨 Host 驗收腳本（2 小時）。  
- 專案：建立跨 Host CI 回放（8 小時）。

Assessment Criteria：
- 功能（40%）：跨 Host 可用  
- 品質（30%）：入參清晰、結果一致  
- 效能（20%）：延遲/成本可控  
- 創新（10%）：回放測試設計


--------------------------------
案例分類
--------------------------------

1) 按難度分類  
- 入門級（適合初學者）：Case 8, 9, 13, 14  
- 中級（需要一定基礎）：Case 2, 3, 5, 6, 10, 11, 12, 16  
- 高級（需要深厚經驗）：Case 1, 4, 7, 15

2) 按技術領域分類  
- 架構設計類：Case 1, 11, 12, 15, 16  
- 效能優化類：Case 3, 5, 6, 7  
- 整合開發類：Case 8, 9, 10, 14  
- 除錯診斷類：Case 12, 16（流程與誤用防護、跨 Host 一致性）  
- 安全防護類：Case 12, 15（流程閘門、邊界約束）

3) 按學習目標分類  
- 概念理解型：Case 1, 11, 15  
- 技能練習型：Case 3, 5, 6, 7, 10, 13, 14  
- 問題解決型：Case 2, 8, 9, 12, 16  
- 創新應用型：Case 4（synthesis）、Case 11（分層）、Case 12（會話級防護）


--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 建議先學：  
  1) Case 1（MCP-first/Workflow-first 全局觀）  
  2) Case 15（API→AI First 的介面原則）  
  3) Case 11（工具分層的設計哲學）  
  這三者建立整體方法論與設計直覺。

- 依賴關係：  
  - Case 2（GetInstructions）與 Case 12（conversationId）依賴 Case 1/15 的理念。  
  - Case 3（兩段式檢索）依賴 Case 4/5/6 的內容工程與 context 控制。  
  - Case 8/9/10（應用示範）依賴 Case 1-6 的工具與內容基礎。  
  - Case 16（跨 Host 一致性）需先完成工具設計與分層（Case 1/11/12）。

- 完整學習路徑建議：  
  1) 理念與介面：Case 1 → 15 → 11  
  2) 起手與防護：Case 2 → 12  
  3) 內容工程與上下文：Case 4 → 5 → 6 → 3  
  4) 技術債與資料清理：Case 7  
  5) 應用實戰：Case 8 → 9 → 10  
  6) 外部文庫與強化：Case 13 → 14  
  7) 跨平台穩定性：Case 16

以上 15 個案例均可獨立教學或組合成專題實作課程，涵蓋從理念到工程、從內容到工具、從單 Host 到跨 Host 的全鏈路實戰。