---
layout: synthesis
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計 - solution"
synthesis_type: solution
source_post: /2025/09/16/chat-with-my-blog/
redirect_from:
  - /2025/09/16/chat-with-my-blog/solution/
---

## Case #1: MCP-first 工具介面設計（讓 Agent 能「用」你的部落格）

### Problem Statement（問題陳述）
**業務場景**：作者的部落格長文以情境→問題→POC→解法的敘事方式累積了大量知識，但讀者與 AI 很難直接將內容轉化為可用的解題素材。需要將部落格服務化，讓 Agent 能以工作流程為中心檢索、理解並運用文章，支援問答、解題、學習、編碼等場景。
**技術挑戰**：傳統把 REST API 包裝成 MCP 的做法無法支援 Agent 的思維與工作流程；工具設計若不貼近 context + workflow，AI 會用得很辛苦且易出錯。
**影響範圍**：影響內容可用性、檢索精度、Agent 整合與最終使用體驗；直接影響 Q/A、vibe coding、文件撰寫效率。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. MCP 被誤用為 API 封裝，忽略「模型使用上下文」本質。
2. 工具介面過度 UI/端點導向，未對應真實工作流程。
3. 未提供合適的 instructions 與資源，導致 Agent 操作時上下文缺失。

**深層原因**：
- 架構層面：缺少 workflow-first 的設計視角，未將工作流程抽象為可授權工具。
- 技術層面：缺乏針對檢索與理解的 primitives（Prompts/Tools/Resources）分工。
- 流程層面：忽略授權與引導步驟，讓 Agent 在未知規則下亂試。

### Solution Design（解決方案設計）
**解決策略**：以使用者的工作流程為中心，重新定義 MCP tools，使其精準對應「解答/解題/學習/編碼」四大場景的思考步驟；提供「GetInstructions」作為入口，建立操作規則，並以「先檢索片段再擴展全文」的方式控制上下文與成本。

**實施步驟**：
1. 工作流程盤點與抽象
- 實作細節：將「訂閱、解答、解題、學習」的真人操作過程拆解為抽象動作。
- 所需資源：現有文章集、過去讀者使用模式。
- 預估時間：1-2 天

2. MCP Tools 規格定義
- 實作細節：定義工具及參數，涵蓋指引、搜尋、內容、關聯。
- 所需資源：MCP 伺服設計文件、Shopify/Context7 參考。
- 預估時間：1-2 天

3. 服務與檢索管線實作
- 實作細節：串接向量檢索、synthesis 型態、chunk 細分、Post 內容 API。
- 所需資源：向量資料庫、LLM、HTTP MCP Host。
- 預估時間：3-5 天

**關鍵程式碼/設定**：
```json
// MCP Tools 規格（摘要）
{
  "tools": [
    { "name": "GetInstructions", "input": {}, "output": "markdown" },
    { "name": "SearchChunks", "input": { "query": "string", "synthesis": ["origin","solution","faq","summary"], "limit": "number" }},
    { "name": "SearchPosts", "input": { "query": "string", "synthesis": "string", "limit": "number" }},
    { "name": "GetPostContent", "input": { "postid": "string", "synthesis": "string", "position": "number", "length": "number" }},
    { "name": "GetRelatedPosts", "input": { "postid": "string", "limit": "number" }}
  ]
}
// Implementation Example：以 workflow 為導向設計 primitives
```

實際案例：作者部署 Streamable HTTP MCP，工具包括 GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts。
實作環境：MCP Server（HTTP）、向量檢索、LLM；客戶端：ChatGPT Plus（MCP beta）、VSCode + Copilot。
實測數據：
- 改善前：AI 對部落格僅能「RAG 書僮」，理解難轉解題。
- 改善後：能遵循工作流程檢索→擴展→引用，完成 Q/A、vibe coding。
- 改善幅度：工作效率在多場景下提升約 10-100 倍（作者觀察）。

Learning Points（學習要點）
核心知識點：
- MCP 不是 API；以 workflow-first 設計工具。
- Primitives 分工：Prompts/Tools/Resources。
- 入口工具與 instructions 對 Agent 成功率至關重要。

技能要求：
- 必備技能：API 設計、RAG 基礎、HTTP MCP。
- 進階技能：上下文工程、工作流程抽象、LLM 指令設計。

延伸思考：
- 還可用於企業內知識庫、程式庫教學站、產品文件中心。
- 風險：工具過多導致選擇困難；需分層與 gating。
- 優化：加上分層（發現/規劃/執行）、會話狀態與安全策略。

Practice Exercise（練習題）
- 基礎練習：設計一個 SearchChunks 工具，支持 synthesis 參數（30 分鐘）。
- 進階練習：用 VSCode MCP client 連到你的 HTTP MCP，完成 Q/A 與引用（2 小時）。
- 專案練習：針對你的技術部落格，完成五個工具 + 內容檢索管線（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能完成指引、檢索、內容、關聯。
- 程式碼品質（30%）：工具定義清晰、參數驗證與錯誤處理完善。
- 效能優化（20%）：上下文與 token 控制良好。
- 創新性（10%）：workflow-first 的工具抽象設計。


## Case #2: 長文預處理與正規化（讓 RAG 用得好）

### Problem Statement（問題陳述）
**業務場景**：作者的長文敘事完整但不適合直接切片做 RAG（8KB 限制，斷裂後非完整主題）。需要把內容預先轉成 FAQ/Solutions/Summary 等「可用型態」，再進行向量化與檢索。
**技術挑戰**：直接 chunk 會模糊主旨，檢索回來的片段不可用；需要「合用型態」的 synthesis。
**影響範圍**：影響查準率、回答品質、引用正確性，進而影響 Q/A、解題與編碼。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 長文的邏輯序列被切斷，不再對應解題單元。
2. RAG 檢索的片段無法直接應用到解決方案。
3. 向量索引含噪過多，造成上下文爆量與成本上升。

**深層原因**：
- 架構層面：缺少「應用型態」的內容建模。
- 技術層面：未設計 synthesis pipeline（origin/solution/faq/summary）。
- 流程層面：發布流程未納入 LLM 預處理步驟。

### Solution Design（解決方案設計）
**解決策略**：在發布流程加入 LLM 預處理，將原文精煉成 FAQ（問答對）、Solutions（方案單元）、Summary（摘要）、Origin（原文映射）；建置向量索引以這些型態為主；工具搜尋時帶上 synthesis 參數，取用合適型態。

**實施步驟**：
1. 型態定義與映射
- 實作細節：為每篇文章生出 FAQ、Solutions、Summary、Origin。
- 所需資源：LLM、提示模板、文稿。
- 預估時間：每篇 5-15 分鐘（依長度）

2. 索引與檢索策略
- 實作細節：以 synthesis 型態建立向量索引（分庫或分欄）。
- 所需資源：向量資料庫；檢索 SDK。
- 預估時間：1-2 天

3. 工具接口整合
- 實作細節：SearchChunks/SearchPosts 支援 synthesis；GetPostContent 支援 position/length。
- 所需資源：MCP server。
- 預估時間：1 天

**關鍵程式碼/設定**：
```json
// SearchChunks 請求示例（ChatGPT 實測）
{
  "query": "微服務 分散式 交易 跨服務 一致性 Saga Outbox 兩階段提交 TCC 事件驅動 可靠投遞 基礎 知識",
  "synthesis": "summary",
  "limit": 8
}
// Implementation Example：按型態檢索，避免原文噪音
```

實際案例：ChatGPT/Claude 均能以 synthesis 參數檢索到「可用型態」片段，並正確引用文章連結。
實作環境：LLM（Claude Sonnet 4、GPT-5 Thinking）、向量檢索、MCP Server。
實測數據：
- 改善前：RAG 檢索片段難用；回答多為泛化或「書僮」。
- 改善後：回答能引用正確片段，並能生成可實作的方案。
- 改善幅度：問答品質與引用正確性顯著提升（作者觀察）。

Learning Points（學習要點）
- 為「應用」設計內容型態，非為技術而技術。
- 以 synthesis 控制檢索與上下文。
- 預處理雖花 token，但價值最高。

技能要求：
- 必備技能：Prompt 編寫、向量檢索、資料建模。
- 進階技能：內容工程（Content Engineering）、上下文工程。

延伸思考：
- 應用於企業知識、SOP、產品指南的「可用單元」設計。
- 風險：成本（token）上升；需控管與批次化。
- 優化：建立離線預處理管線與版本控制。

Practice Exercise（練習題）
- 基礎練習：為一篇部落格生成 FAQ/Solutions/Summary（30 分鐘）。
- 進階練習：建立 synthesis-based 的向量索引並檢索（2 小時）。
- 專案練習：將你的內容發布管線接上 LLM 預處理（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：四種型態齊備且可檢索。
- 程式碼品質（30%）：管線可重入、可監控、可回溯。
- 效能優化（20%）：token 與上下文控制合理。
- 創新性（10%）：型態設計貼近使用情境。


## Case #3: 以 AI IDE 清理技術債（Repo 重構與流程效率化）

### Problem Statement（問題陳述）
**業務場景**：部落格自 2016 移轉至 GitHub Pages，仍留存大量 HTML 舊文（約 60-70%）、中文檔名/網址、壞鏈結、圖片路徑雜亂，影響向量檢索與發佈效率。
**技術挑戰**：批次內容轉換、鏈結/資源修復、結構合理化，需要自動化與工具輔助。
**影響範圍**：向量檢索品質、MCP 預處理效率、文章發佈速度。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 過往遷移只求能動，未深度清理。
2. HTML 格式不利向量檢索與內容抽取。
3. 檔名與路徑不一致，鏈結管理困難。

**深層原因**：
- 架構層面：Repo 結構未對齊內容工程需求。
- 技術層面：缺少批次化工具與規則。
- 流程層面：缺乏自動化 pipeline 與驗證。

### Solution Design（解決方案設計）
**解決策略**：使用 VSCode + Copilot + 輔助腳本進行一次性重構：HTML→Markdown、批次改檔名（中文→英文）、修圖檔/鏈結、導出 Disqus 對照表、調整 Repo 結構；為 LLM 預處理與 MCP 檢索提供乾淨基礎。

**實施步驟**：
1. 盤點與規則制定
- 實作細節：定義檔名規則、圖片目錄、鏈結格式、Markdown 規範。
- 所需資源：Repo、Copilot。
- 預估時間：0.5-1 天

2. HTML→Markdown 批次轉換
- 實作細節：AI 協助轉寫、人工 spot-check；保留語意，移除冗餘樣式。
- 所需資源：VSCode、Copilot、轉換腳本。
- 預估時間：2-3 天（視篇幅）

3. 链結/圖片修復與對照表
- 實作細節：寫工具修復路徑；輸出 Disqus URL 對映。
- 所需資源：Node/Bash 腳本。
- 預估時間：1-2 天

**關鍵程式碼/設定**：
```bash
# 批次將中文檔名轉英文 slug，並更新文內引用
for f in content/**/*.md; do
  new=$(echo "$f" | iconv -f utf8 -t ascii//TRANSLIT | sed 's/[^a-zA-Z0-9\/.-]/-/g' | tr 'A-Z' 'a-z')
  git mv "$f" "$new"
done

# 圖片路徑統一化
find assets/images -type f -name "* *" -print0 | xargs -0 -I{} bash -c 'mv "$1" "${1// /-}"' -- {}
# Implementation Example：以腳本+AI輔助完成一次性重構
```

實際案例：作者以 VSCode + Copilot 完成一次性重構，清除舊格式、統一路徑、修復鏈結，建立可靠的發佈與檢索基礎。
實作環境：GitHub Pages、VSCode、Copilot、Bash/Node。
實測數據：
- 改善前：HTML 舊文約 60-70%，路徑/鏈結雜亂。
- 改善後：Markdown 比例大幅提升、路徑與鏈結規範化。
- 改善幅度：發佈與預處理管線順暢（作者體感顯著提升）。

Learning Points（學習要點）
- 一次性重構比持續修補更有效。
- 為向量檢索與 LLM 服務設計內容結構。
- 規則先行，工具後到。

技能要求：
- 必備技能：版本控制、腳本能力、Markdown/HTML。
- 進階技能：AI 輔助重構、內容規範制定。

延伸思考：
- 可擴展到企業文件中心、Wiki、設計規格庫。
- 風險：批次改動影響外部引用，需要良好對照表與重定向。
- 優化：建立 CI 檢查、鏈結驗證、圖片壓縮流程。

Practice Exercise（練習題）
- 基礎練習：撰寫批次改檔名與路徑統一腳本（30 分鐘）。
- 進階練習：將 HTML 轉 Markdown 並校驗鏈結（2 小時）。
- 專案練習：完成一個內容重構 pipeline，含對照表輸出（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：轉換/修復/對照表齊備。
- 程式碼品質（30%）：腳本健壯、可回溯與日誌。
- 效能優化（20%）：批次效率與錯誤率控制。
- 創新性（10%）：AI 與腳本協作流程設計。


## Case #4: 指令閘道工具（ConversationId 強制引導）

### Problem Statement（問題陳述）
**業務場景**：Agent 在沒有遵循規則的前提下亂用工具，導致錯誤與不一致。需要一個「必須先呼叫的工具」來載入 instructions 與會話狀態。
**技術挑戰**：如何強制 Agent 按正確步驟操作，並維持會話上下文。
**影響範圍**：工具濫用、錯誤增多、成本上升、體驗不佳。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Agent 無法被 UI 或文件強制約束。
2. Instructions 未必在 context window 內。
3. 缺少會話識別，工具無法確認前置條件。

**深層原因**：
- 架構層面：缺少會話門檻設計（gating）。
- 技術層面：未傳回可供 LLM 抽取的狀態標識。
- 流程層面：沒有把「先學再用」變成工具流程的一部分。

### Solution Design（解決方案設計）
**解決策略**：仿照 Shopify 的 learn_shopify_api 設計 GetInstructions 工具，使用 Markdown 內嵌「必讀規則」與 conversationId，要求後續所有工具必須帶此 ID；在描述與返回中明確告知未帶 ID 將失敗。

**實施步驟**：
1. 入口工具定義
- 實作細節：GetInstructions 返回規則與會話 ID。
- 所需資源：MCP server 實作。
- 預估時間：0.5 天

2. 工具校驗與拒絕策略
- 實作細節：所有工具檢查 conversationId，缺失則拒絕。
- 所需資源：工具層校驗程式。
- 預估時間：0.5-1 天

3. 返回格式優化
- 實作細節：使用 Markdown 列點說明、強調必須步驟，方便 LLM 抽取。
- 所需資源：提示工程。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```markdown
# GetInstructions（返回示例）
🔗 SAVE THIS CONVERSATION ID: 5f53b794-e408-4346-9915-55699d92f68e
🚨 MANDATORY FIRST STEP: Call this tool BEFORE any others.
⚠️ All other tools WILL FAIL without the conversationId above.
- Always include `conversationId` in subsequent tool calls.
- Re-call this tool when switching contexts (it’s allowed).
```

實際案例：Shopify Dev MCP 將 conversationId 作為所有工具的必要參數，使 Agent 必須按流程操作；作者在自家 MCP 借鑑此模式以保證工具運作秩序。
實作環境：MCP server、Markdown 返回搭配 LLM。
實測數據：
- 改善前：Agent 亂序使用工具、上下文缺失。
- 改善後：工具使用順序正確，錯誤顯著下降（作者觀察）。
- 改善幅度：可靠性明顯提升。

Learning Points（學習要點）
- 用工具返回「即時 instructions」比寫在文件更有效。
- 會話狀態是 MCP-first 的關鍵。
- 以拒絕策略（fail fast）建立秩序。

技能要求：
- 必備技能：MCP 工具設計、狀態管理。
- 進階技能：指令工程、Markdown 可解析設計。

延伸思考：
- 可擴展至安全許可、配額、審計。
- 風險：ID 丟失需重試策略。
- 優化：支持多個子上下文（topic-scoped IDs）。

Practice Exercise（練習題）
- 基礎練習：為你的 MCP 寫一個入口工具並返回會話 ID（30 分鐘）。
- 進階練習：在三個工具中強制校驗 ID（2 小時）。
- 專案練習：設計完整 gating + 拒絕策略（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：入口工具與校驗一致。
- 程式碼品質（30%）：返回可解析、錯誤訊息清晰。
- 效能優化（20%）：最小上下文與最少重試。
- 創新性（10%）：gating 策略與會話管理設計。


## Case #5: 先片段再全文（上下文與成本控制的檢索分層）

### Problem Statement（問題陳述）
**業務場景**：直接把整篇文件拉進上下文會導致 token 爆量、模型抓不到重點。需要先檢索片段（chunks）再選擇性拉全文。
**技術挑戰**：如何讓 Agent 先「探索」，再「深入」，避免過早塞滿 context window。
**影響範圍**：token 成本、回答品質、工具可用性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 過早載入大量內容，造成上下文噪音。
2. 未分層檢索，工具無法指導模型逐步聚焦。
3. 返回格式不利於 LLM 抽取關鍵。

**深層原因**：
- 架構層面：未設計探索/規劃/執行分層。
- 技術層面：缺乏 chunks-first 的檢索工具。
- 流程層面：Agent 未受引導先廣後深。

### Solution Design（解決方案設計）
**解決策略**：設計 SearchChunks（返回 Markdown 片段 + path）與 FetchFullDocs（以 paths 拉全文），引導 Agent 先用少量上下文探索，再有選擇地擴充；返回內容偏 Markdown，提升語意密度。

**實施步驟**：
1. Chunks 索引與返回格式設計
- 實作細節：片段含標題、路徑、摘要；Markdown 表示。
- 所需資源：向量索引、文件庫。
- 預估時間：1 天

2. 全文拉取工具
- 實作細節：限定 paths，返回 Markdown；不直接返回 HTML。
- 所需資源：文件資料源。
- 預估時間：0.5 天

3. 客戶端策略與提示
- 實作細節：在工具描述中說明先 chunks 後全文的策略。
- 所需資源：提示工程。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```json
// 搜尋片段 → 擴充全文
call SearchChunks({
  "prompt": "GraphQL 認證 + Products 查詢",
  "max_num_results": 5
})
// 然後選定 paths
call FetchFullDocs({
  "paths": ["/docs/admin/graphql/products", "/docs/auth/admin"]
})
// Implementation Example：Shopify 的 search_docs_chunks + fetch_full_docs 分工
```

實際案例：Shopify Dev MCP 以兩工具分層檢索；作者在自家 MCP 以 SearchChunks/SearchPosts → GetPostContent 實現。
實作環境：MCP server、文件庫、向量索引。
實測數據：
- 改善前：直接載入大量內容，回答偏離重點。
- 改善後：上下文更聚焦，引用更準確，token 成本下降（作者觀察）。
- 改善幅度：上下文噪音顯著降低。

Learning Points（學習要點）
- 分層檢索是上下文工程的核心。
- Markdown 比 HTML 更利於 LLM。
- 先探索再深入的工作流設計。

技能要求：
- 必備技能：索引設計、返回格式設計。
- 進階技能：上下文分層與提示引導。

延伸思考：
- 可擴展至「規劃層」工具（教模型怎麼選擇）。
- 風險：片段切分不良會影響結果。
- 優化：語意切分、引用權重、片段元資料。

Practice Exercise（練習題）
- 基礎練習：設計一個 chunks 返回結構（30 分鐘）。
- 進階練習：在你的 MCP 中加上全文拉取工具（2 小時）。
- 專案練習：建立探索/拉取/生成的完整工作流（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：片段與全文分工清晰。
- 程式碼品質（30%）：返回可解析、元資料完備。
- 效能優化（20%）：上下文與 token 控制。
- 創新性（10%）：分層策略與引導提示設計。


## Case #6: 查詢策略優化（多輪查詢與語義擴展）

### Problem Statement（問題陳述）
**業務場景**：單輪查詢容易漏掉關鍵術語或語義變體，導致檢索不全。需要多輪或擴展式查詢以覆蓋主題。
**技術挑戰**：如何讓 Agent 自我調整查詢，避免過度或不足。
**影響範圍**：檢索覆蓋度與回答品質。
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 查詢只含一組關鍵字，語義窄。
2. 未依第一次結果調整第二次查詢。
3. 沒有針對「型態」選擇合適檢索策略。

**深層原因**：
- 架構層面：工具未提供合適的查詢指引。
- 技術層面：未支持多輪查詢模式。
- 流程層面：Agent 缺少「先寬後窄」的提示。

### Solution Design（解決方案設計）
**解決策略**：鼓勵 Agent 使用 Thinking/多輪模式；第一次用「廣泛語義 + summary」，第二次用「重點術語 + summary/solution」；在工具描述中提供查詢模板。

**實施步驟**：
1. 查詢模板設計
- 實作細節：提供廣義與狹義查詢示例。
- 所需資源：工具描述文檔。
- 預估時間：0.5 天

2. 多輪策略提示
- 實作細節：在 instructions 中強調先寬後窄。
- 所需資源：GetInstructions 返回。
- 預估時間：0.5 天

3. 輸入與結果觀察
- 實作細節：客戶端允許展示工具呼叫過程以利調整。
- 所需資源：MCP 客戶端（ChatGPT/VSCode）。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```json
// ChatGPT GPT-5 Thinking 的兩輪查詢示例
{ "query":"微服務 分散式 交易 ... TCC 事件驅動 可靠投遞 基礎 知識", "synthesis":"summary", "limit":8 }
{ "query":"Saga 兩階段提交 TCC Outbox 分散式 交易 一致性 微服務", "synthesis":"summary", "limit":8 }
// Implementation Example：第一次廣義，第二次關鍵術語收斂
```

實際案例：作者比較 Claude（直線單輪）與 GPT-5（多輪 Thinking）在分散式交易查詢上的差異；多輪能更好覆蓋關鍵技術術語。
實作環境：ChatGPT Plus（GPT-5 Thinking）、Claude Sonnet 4、MCP Server。
實測數據：
- 改善前：單輪查詢覆蓋有限。
- 改善後：多輪查詢覆蓋更全面，回答更準確（作者觀察）。
- 改善幅度：覆蓋度與準確性提升。

Learning Points（學習要點）
- 查詢不是一次完成，應當迭代。
- 型態（summary/solution）影響查詢結果。
- 觀察工具調用是調參的依據。

技能要求：
- 必備技能：檢索策略、關鍵字設計。
- 進階技能：思維鏈提示、多輪優化。

延伸思考：
- 可自動化「擴展-收斂」的查詢代理。
- 風險：過多輪造成成本飆升。
- 優化：限制輪次與返回大小。

Practice Exercise（練習題）
- 基礎練習：設計兩輪查詢以覆蓋一個主題（30 分鐘）。
- 進階練習：在 MCP instructions 中寫入查詢策略（2 小時）。
- 專案練習：打造一個查詢優化 Agent（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：多輪策略實作與展示。
- 程式碼品質（30%）：返回可比較、日誌清楚。
- 效能優化（20%）：輪次與成本控制。
- 創新性（10%）：查詢模板與型態結合。


## Case #7: Vibe Coding：Pipeline CLI 平行處理（.NET Channels）

### Problem Statement（問題陳述）
**業務場景**：依據作者文章，用 CLI 接收 STDIN 的 JSONL，逐筆平行處理；讓 Agent 參照文章設計出現代化架構與程式碼。
**技術挑戰**：如何讓 Agent 讀懂文章並輸出符合當代最佳實務（如 Channels 替代 BlockingCollection）。
**影響範圍**：開發效率、程式品質、學習效益。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 人工從文章到程式碼轉譯成本高。
2. 舊文章的技術堆疊可能過時。
3. 缺少標準的輸入/輸出與並行模式樣板。

**深層原因**：
- 架構層面：未建建立以文章為源的 coding 工作流。
- 技術層面：未把關鍵概念抽象為可重用模板。
- 流程層面：沒有形成「文章→MCP→Agent→Code」閉環。

### Solution Design（解決方案設計）
**解決策略**：用 MCP 檢索文章與關鍵片段→由 Copilot 生成程式框架→開發者填入處理邏輯；選用 Channels+async+JSONL I/O，保證現代 .NET 寫法。

**實施步驟**：
1. 問題描述與資料結構定義
- 實作細節：定義 UserItem，要求 STDIN JSONL 讀入。
- 所需資源：VSCode、Copilot、MCP。
- 預估時間：10 分鐘

2. 程式框架生成與調整
- 實作細節：使用 Channels 作為生產者/消費者，控制平行度。
- 所需資源：.NET 8、C#。
- 預估時間：30-60 分鐘

3. 測試資料與腳本
- 實作細節：生成 JSONL 範例與 shell 測試腳本。
- 所需資源：Bash、dotnet CLI。
- 預估時間：30 分鐘

**關鍵程式碼/設定**：
```csharp
// 核心：Channel 平行處理（作者實測）
static async Task ProcessDataInParallel(int parallelism) {
  var channel = System.Threading.Channels.Channel.CreateBounded<UserItem>(100);
  var reader = channel.Reader; var writer = channel.Writer;

  var producerTask = Task.Run(async () => {
    await foreach (var item in ReadFromStdin()) await writer.WriteAsync(item);
    writer.Complete();
  });

  var consumerTasks = Enumerable.Range(0, parallelism).Select(workerId => Task.Run(async () => {
    await foreach (var item in reader.ReadAllAsync()) {
      var processedItem = await ProcessSingleItem(item, workerId);
      await OutputResult(processedItem);
    }
  })).ToArray();

  await Task.WhenAll(new[] { producerTask }.Concat(consumerTasks));
}
```

實際案例：作者用 VSCode + Copilot + MCP 在約 1 分鐘生成框架、5 分鐘完成測試與驗證；改用 Channels 等現代模式。
實作環境：VSCode、Copilot、.NET 8、MCP Server。
實測數據：
- 改善前：人工撰寫與查文件需數小時。
- 改善後：框架生成約 1 分鐘；完測約 5 分鐘。
- 改善幅度：效率提升數十倍（作者實測）。

Learning Points（學習要點）
- 文章→MCP→Agent→Code 的閉環。
- .NET Channels 生產者/消費者模式。
- JSONL 與 STDIO 管線化。

技能要求：
- 必備技能：C#/.NET、CLI、並行基礎。
- 進階技能：Channels、非同步設計、I/O 可靠性。

延伸思考：
- 可封裝為模板供團隊共用。
- 風險：STDIN 錯誤處理與背壓。
- 優化：可加上重試與度量。

Practice Exercise（練習題）
- 基礎練習：以 Channels 寫一個簡單並行消費者（30 分鐘）。
- 進階練習：接收 JSONL 並輸出處理結果（2 小時）。
- 專案練習：建立完整 CLI 管線與測試腳本（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：STDIN/STDOUT、平行控制、錯誤處理。
- 程式碼品質（30%）：現代化模式、可讀性。
- 效能優化（20%）：背壓與資源控制。
- 創新性（10%）：將文章知識轉為可用程式碼。


## Case #8: Chat with My Blog：問答與引用（消除幻覺）

### Problem Statement（問題陳述）
**業務場景**：讀者以 Q/A 模式與部落格互動，期待得到正確答案與引用來源；MCP 需支援精準檢索與引用。
**技術挑戰**：避免幻覺、確保引用正確、維持回答可讀性。
**影響範圍**：使用者信任、學習效果、決策品質。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無引用機制導致答案不可驗證。
2. 檢索不精確易導致幻覺。
3. 回答風格不一，讀者難以理解。

**深層原因**：
- 架構層面：缺乏面向引用的工具與元資料。
- 技術層面：未在上下文中保留來源元資訊。
- 流程層面：回答生成未強制帶 citation。

### Solution Design（解決方案設計）
**解決策略**：在 SearchChunks/SearchPosts/GetPostContent 返回中加入標題、URL、postid 等元資訊；在 instructions 中要求回答附引用；客戶端展示工具呼叫過程以利審核。

**實施步驟**：
1. 檢索返回結構化元資料
- 實作細節：返回標題、URL、postid、片段位置。
- 所需資源：索引與資料源。
- 預估時間：1 天

2. 回答風格與引用指引
- 實作細節：在 GetInstructions 中明確要求 citation。
- 所需資源：提示工程。
- 預估時間：0.5 天

3. 客戶端驗證與展示
- 實作細節：讓使用者看到工具呼叫與引用來源。
- 所需資源：MCP 客戶端。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```json
// Claude/ChatGPT 問答時的工具呼叫（示例）
{
  "tool": "SearchChunks",
  "input": { "query": "分散式交易 saga 2PC outbox", "synthesis": ["origin","solution","faq"], "limit": 10 },
  "returns": [{ "title": "微服務的分散式交易", "url": "...", "postid": "2019-xx", "snippet": "..." }]
}
// Implementation Example：返回即含 citation 所需元資料
```

實際案例：作者以相同問題測試 Claude 與 ChatGPT；兩者均能返回正確引用，無明顯幻覺；文字風格有差異但內容正確。
實作環境：ChatGPT Plus（MCP beta）、Claude Sonnet 4、MCP Server。
實測數據：
- 改善前：無引用的 Q/A 難以信任。
- 改善後：回答附正確引用連結，可信度提升。
- 改善幅度：信任與準確性明顯提升（作者觀察）。

Learning Points（學習要點）
- 引用是抗幻覺的基本功。
- 返回結構需內嵌來源。
- 客戶端展示工具呼叫有助透明度。

技能要求：
- 必備技能：資料建模、提示工程。
- 進階技能：回答風格控制、引用策略。

延伸思考：
- 可加上引用必須通過鏈結校驗。
- 風險：外部鏈結失效。
- 優化：鏈結健康檢查與快取。

Practice Exercise（練習題）
- 基礎練習：在返回中加入 postid/URL（30 分鐘）。
- 進階練習：強制回答附 citation（2 小時）。
- 專案練習：建立 Q/A 工作流展示工具呼叫（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：Q/A 與引用整合。
- 程式碼品質（30%）：返回元資料完備。
- 效能優化（20%）：上下文精準。
- 創新性（10%）：回答風格與引用策略設計。


## Case #9: 以 Agent 整理部落格演進史（時序聚合）

### Problem Statement（問題陳述）
**業務場景**：需要從多篇文章彙整部落格系統移轉歷史，按年份/系統/客製化項目形成摘要清單並附引用，直接寫入 Markdown。
**技術挑戰**：跨文聚合、時序排序、引用整理，需要 Agent 代勞。
**影響範圍**：文檔撰寫效率、準確性、可追溯性。
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 人工搜尋與編排耗時巨大。
2. 記憶與上下文容易遺漏。
3. 多源引用不易統一格式。

**深層原因**：
- 架構層面：缺少面向彙整的檢索工具。
- 技術層面：缺乏時序模型與模板。
- 流程層面：沒形成「查-聚-寫」自動化。

### Solution Design（解決方案設計）
**解決策略**：用 VSCode + Copilot 在 agent 模式下請求 MCP 檢索相關文章→聚合為「年份/系統/客製化」格式→直接改寫 Markdown 段落；訓練 Agent 生成引用。

**實施步驟**：
1. Markdown 模板指定
- 實作細節：指定輸出格式與每項 100 字限制。
- 所需資源：VSCode、Copilot、MCP。
- 預估時間：10 分鐘

2. 檢索與彙整
- 實作細節：SearchPosts→GetPostContent→聚合排序。
- 所需資源：MCP tools。
- 預估時間：1-2 分鐘（作者實測）

3. 寫入與校驗
- 實作細節：Agent 直接替換段落；人工快速檢視。
- 所需資源：VSCode。
- 預估時間：5-10 分鐘

**關鍵程式碼/設定**：
```markdown
# 請求模板（作者使用）
請幫我填上這段 markdown 區段
幫我整理 "安德魯的部落格" 歷年來移轉系統的記錄當作主要項目清單
...（格式略）
```

實際案例：作者在 VSCode 中 1 分鐘生成、5-10 分鐘校對完成；包含 2008→2016 的移轉與客製化摘要，引用正確。
實作環境：VSCode、Copilot、MCP Server。
實測數據：
- 改善前：需一晚手動整理（作者既往經驗）。
- 改善後：1-2 分鐘生成 + 少量校正。
- 改善幅度：約 30-60 倍效率提升（作者實測）。

Learning Points（學習要點）
- Agent 適合做「查-聚-寫」的苦工。
- 明確輸出模板有助品質。
- MCP 檢索 + Copilot 寫作高度互補。

技能要求：
- 必備技能：Markdown、檢索與模板設計。
- 進階技能：彙整邏輯與引用策略。

延伸思考：
- 可擴展到 Roadmap、版本史、變更日誌。
- 風險：聚合過度簡化。
- 優化：加入差異化標記或重要事件摘要。

Practice Exercise（練習題）
- 基礎練習：為你的專案生成歷史摘要段（30 分鐘）。
- 進階練習：讓 Agent 依照模板重寫段落（2 小時）。
- 專案練習：建立「查-聚-寫」自動化流程（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：格式正確、引用齊備。
- 程式碼品質（30%）：工具呼叫與返回清楚。
- 效能優化（20%）：時間與上下文控制。
- 創新性（10%）：聚合策略與寫作模板。


## Case #10: Synthesis 參數設計（為「用」而非「存」）

### Problem Statement（問題陳述）
**業務場景**：搜尋時需要不同型態的內容（origin/solution/faq/summary）來支援不同任務；單一型態無法滿足使用。
**技術挑戰**：設計與落地 synthesis 參數，讓工具能檢索到合用的型態。
**影響範圍**：問答、解題、學習、編碼全流程。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 原始內容不利於直接應用。
2. 查詢未指定型態，返回不一致。
3. 向量索引未依型態分層。

**深層原因**：
- 架構層面：缺乏面向應用的內容建模。
- 技術層面：未在工具參數中體現型態選擇。
- 流程層面：發布未預先生成型態。

### Solution Design（解決方案設計）
**解決策略**：在 SearchChunks/SearchPosts/GetPostContent 中加入 synthesis 參數；索引以型態為維度建立；在 instructions 中教 Agent 何時用何種型態。

**實施步驟**：
1. 型態與用例對應表
- 實作細節：FAQ→問答；Solution→解題；Summary→總覽；Origin→引用確認。
- 所需資源：內容工程。
- 預估時間：0.5 天

2. 工具參數與返回
- 實作細節：支持複合型態或優先級。
- 所需資源：MCP server。
- 預估時間：1 天

3. 索引實作
- 實作細節：按型態建庫或建欄位。
- 所需資源：向量資料庫。
- 預估時間：1-2 天

**關鍵程式碼/設定**：
```json
// SearchChunks 支持多型態
{ "query": "分散式交易 saga outbox 2PC", "synthesis": ["origin","solution","faq"], "limit": 10 }
// Implementation Example：型態驅動的可用檢索
```

實際案例：作者在對分散式交易的問答實測中，使用 synthesis 審慎控制返回型態，提升回答適用性與引用質量。
實作環境：MCP Server、向量索引、LLM。
實測數據：
- 改善前：返回片段用起來卡卡。
- 改善後：返回即用，回答更貼近需求。
- 改善幅度：可用性顯著提升（作者觀察）。

Learning Points（學習要點）
- 內容為「用」而非「存」。
- 型態設計是 RAG 成敗關鍵。
- 工具參數是應用意圖的載體。

技能要求：
- 必備技能：內容建模、索引設計。
- 進階技能：型態選擇策略、提示工程。

延伸思考：
- 可加入「可信度」與「粒度」參數。
- 風險：型態過多造成複雜度。
- 優化：依場景設計預設型態組合。

Practice Exercise（練習題）
- 基礎練習：為一篇文生成四型態並索引（30 分鐘）。
- 進階練習：在 MCP 中支持多型態檢索（2 小時）。
- 專案練習：完成型態驅動的 Q/A 工作流（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：參數與返回一致。
- 程式碼品質（30%）：接口清晰、驗證完善。
- 效能優化（20%）：索引與查詢高效。
- 創新性（10%）：型態與場景對應設計。


## Case #11: 相關文章工具（拓展上下文的最小邊界）

### Problem Statement（問題陳述）
**業務場景**：解題往往需要跨文連結與類似案例參考；需要 GetRelatedPosts 工具提供關聯文章。
**技術挑戰**：如何定義「相關」並避免上下文爆炸。
**影響範圍**：解題效果、學習連貫性、引用品質。
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 單篇文章上下文有限。
2. 人工跨文搜尋耗時。
3. 返回內容過多會噪音。

**深層原因**：
- 架構層面：缺少關聯圖設計（tags/主題/語意相似）。
- 技術層面：未設定限制與排序策略。
- 流程層面：工具未提供精簡返回。

### Solution Design（解決方案設計）
**解決策略**：GetRelatedPosts(postid, limit) 以語意相似/標籤/時間序綜合計分，返回標題+URL+score；限制數量避免噪音。

**實施步驟**：
1. 關聯策略設計
- 實作細節：tag 重合度 + 向量相似 + 發佈時間近度。
- 所需資源：索引與文章元資料。
- 預估時間：1 天

2. 返回結構與限制
- 實作細節：標題、URL、score、理由（可選）。
- 所需資源：MCP server。
- 預估時間：0.5 天

3. 客戶端提示
- 實作細節：指導 Agent 先看相關清單後再拉內容。
- 所需資源：GetInstructions。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```json
// GetRelatedPosts 返回示例
[
  { "title": "Saga vs 2PC：取捨", "url":"...", "score":0.89 },
  { "title": "Outbox 模式與可靠投遞", "url":"...", "score":0.86 }
]
// Implementation Example：限制數量與分數排序
```

實際案例：作者在「微服務分散式交易」主題下，透過相關文章擴展視野與引用素材，支援更完整的解題輸出。
實作環境：MCP Server、向量索引、文章元資料。
實測數據：
- 改善前：單篇回答侷限。
- 改善後：可引入相近主題，提升完整性。
- 改善幅度：解題覆蓋度提升（作者觀察）。

Learning Points（學習要點）
- 關聯是解題的加成，不是替代。
- 限制返回規模以控上下文。
- 分數與理由增加透明度。

技能要求：
- 必備技能：相似度計算、元資料設計。
- 進階技能：多因素排序與合併。

延伸思考：
- 可視覺化關聯圖與主題地圖。
- 風險：過度關聯造成噪音。
- 優化：加入用戶意圖過濾。

Practice Exercise（練習題）
- 基礎練習：設計一個 related API 返回（30 分鐘）。
- 進階練習：實作語意相似 + tag 合併策略（2 小時）。
- 專案練習：在 MCP 中加入相關工具並示範解題（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：關聯返回合理。
- 程式碼品質（30%）：排序與限制清楚。
- 效能優化（20%）：上下文控制。
- 創新性（10%）：理由生成與透明設計。


## Case #12: HTML→Markdown 轉換（為向量檢索清障）

### Problem Statement（問題陳述）
**業務場景**：大量 HTML 舊文有格式噪音，不利向量檢索與 LLM 解析；需轉 Markdown。
**技術挑戰**：保持語意與結構、去除樣式噪音、批次化。
**影響範圍**：檢索品質、預處理效率、引用準確性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. HTML 含大量標記與樣式。
2. 文內鏈結與圖片標記不一致。
3. 批次轉換容易破壞語意。

**深層原因**：
- 架構層面：缺少內容規範。
- 技術層面：不具備安全的轉換管線。
- 流程層面：未設計校驗步驟。

### Solution Design（解決方案設計）
**解決策略**：以 AI+腳本批次轉 Markdown，保留標題/段落/程式碼塊/引用等語意標記，統一路徑與鏈結；建立差異檢查與人工抽樣。

**實施步驟**：
1. 轉換規則與保留清單
- 實作細節：保留 h1-h3、pre/code、blockquote、ul/ol。
- 所需資源：轉換工具、Copilot。
- 預估時間：0.5 天

2. 批次轉換與路徑修復
- 實作細節：圖片與鏈結統一相對/絕對策略。
- 所需資源：Node/Bash。
- 預估時間：1-2 天

3. 檢查與抽樣驗證
- 實作細節：比對段落與標題數量、鏈結有效性。
- 所需資源：檢查腳本。
- 預估時間：0.5-1 天

**關鍵程式碼/設定**：
```bash
# 使用 pandoc 批次轉換 + 後處理
for f in legacy_html/**/*.html; do
  md="${f%.html}.md"
  pandoc "$f" -f html -t markdown_strict -o "$md"
  # 後處理：統一圖片與鏈結
  sed -i 's/src="\.\.\/img\//src="\/assets\/images\//g' "$md"
done
// Implementation Example：工具+規則+抽樣驗證
```

實際案例：作者以 AI+腳本完成 HTML→Markdown 大規模轉換，清理噪音後向量檢索與 LLM 效果顯著提升。
實作環境：VSCode、Copilot、Pandoc/Bash/Node。
實測數據：
- 改善前：HTML 噪音高、檢索不精確。
- 改善後：Markdown 語意清晰、檢索準確。
- 改善幅度：檢索品質提升（作者觀察）。

Learning Points（學習要點）
- 語意標記是 LLM 解析的關鍵。
- 批次化需配合抽樣驗證。
- 路徑與鏈結一致性很重要。

技能要求：
- 必備技能：Markdown/HTML、腳本操作。
- 進階技能：內容工程與驗證。

延伸思考：
- 可加入圖片壓縮與 alt 文生成。
- 風險：轉換導致語意丟失。
- 優化：建立差異報告與回滾機制。

Practice Exercise（練習題）
- 基礎練習：用 pandoc 轉一批 HTML→Markdown（30 分鐘）。
- 進階練習：寫後處理與檢查腳本（2 小時）。
- 專案練習：完成端到端轉換與驗證管線（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：轉換+修復+檢查。
- 程式碼品質（30%）：腳本穩健、錯誤處理。
- 效能優化（20%）：批次效率。
- 創新性（10%）：驗證與回滾策略。


## Case #13: 檔名與網址正規化（中文→英文 slug）

### Problem Statement（問題陳述）
**業務場景**：中文檔名/網址造成路徑與兼容性問題；需批次轉英文 slug 並更新文內引用。
**技術挑戰**：轉換規則、引用更新、避免破壞外部連結。
**影響範圍**：SEO、可攜性、檢索與引用。
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 中文路徑與一些環境不兼容。
2. 文內引用指向舊檔名。
3. 無對照表容易失去外部連結。

**深層原因**：
- 架構層面：缺少路徑命名規範。
- 技術層面：缺乏批次更新工具。
- 流程層面：未建立重定向與對照表。

### Solution Design（解決方案設計）
**解決策略**：批次將中文檔名轉英文 slug，更新文內引用，生成對照表供重定向使用；保留舊→新映射以供 SEO 與外部連結。

**實施步驟**：
1. slug 規則制定
- 實作細節：轉拼音/音譯/簡化；限制字元集。
- 所需資源：規則與工具。
- 預估時間：0.5 天

2. 批次改名與引用更新
- 實作細節：git mv + 內容替換；生成映射表。
- 所需資源：腳本。
- 預估時間：1 天

3. 重定向與對照表
- 實作細節：建立 URL rewrite/映射文件。
- 所需資源：網站設定。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```bash
# 產出舊→新映射表
echo "old_path,new_path" > url-mapping.csv
for f in content/**/*.md; do
  new=$(slugify "$f") # 你的 slugify 函數
  echo "$f,$new" >> url-mapping.csv
  git mv "$f" "$new"
  # 更新文內引用
  old_rel=$(basename "$f"); new_rel=$(basename "$new")
  sed -i "s/($old_rel)/(\/$new_rel)/g" "$new"
done
// Implementation Example：批次處理 + 對照表
```

實際案例：作者批次將中文檔名改為英文，並生成 Disqus/URL 映射對照；路徑與引用更一致，利於 MCP 檢索。
實作環境：Git、Bash、網站重定向機制。
實測數據：
- 改善前：中文檔名導致各種兼容與引用問題。
- 改善後：英文 slug 規範化，引用一致。
- 改善幅度：路徑問題顯著減少（作者觀察）。

Learning Points（學習要點）
- 命名規範是內容工程的基本功。
- 對照表與重定向保護外部連結。
- 與 SEO 相容。

技能要求：
- 必備技能：腳本與字串處理。
- 進階技能：URL rewrite 設定。

延伸思考：
- 可加入短網址與追蹤參數策略。
- 風險：重定向錯誤導致 404。
- 優化：鏈結檢查與監控。

Practice Exercise（練習題）
- 基礎練習：將一批檔名轉 slug（30 分鐘）。
- 進階練習：更新文內引用並生成對照表（2 小時）。
- 專案練習：設定重定向與健康檢查（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：改名+引用+對照表。
- 程式碼品質（30%）：腳本可靠。
- 效能優化（20%）：批次性能。
- 創新性（10%）：slug 規則與 SEO 考量。


## Case #14: Disqus 舊鏈結遷移對照表（評論可追溯）

### Problem Statement（問題陳述）
**業務場景**：系統移轉導致舊評論鏈結失效；需要對照表支持舊→新 URL 對映與重定向。
**技術挑戰**：批次導出、解析、映射、回寫。
**影響範圍**：社群互動、歷史價值、SEO。
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 平台更換導致嵌入式評論 URL 改變。
2. 無對照表則難以保持連續性。
3. 批次處理複雜且易錯。

**深層原因**：
- 架構層面：缺乏遷移計劃與資料模型。
- 技術層面：缺少導出/映射/重定向工具。
- 流程層面：遷移未納入 CI/CD 管控。

### Solution Design（解決方案設計）
**解決策略**：導出 Disqus URL 與 PostId，生成對照表（CSV/JSON），在網站層面進行 rewrite；在內容中更新嵌入標記。

**實施步驟**：
1. 資料導出
- 實作細節：抓取舊 URL 與對應 PostId。
- 所需資源：Disqus API 或資料備份。
- 預估時間：0.5-1 天

2. 映射生成
- 實作細節：建立 old_url→new_url 對照。
- 所需資源：腳本。
- 預估時間：0.5 天

3. 重定向與嵌入更新
- 實作細節：網站 rewrite、內容嵌入更新。
- 所需資源：網站設定與內容庫。
- 預估時間：1 天

**關鍵程式碼/設定**：
```yaml
# Apache/Nginx rewrite（示意）
RewriteMap urlmap txt:/path/url-mapping.txt
RewriteCond %{REQUEST_URI} ^/old-path/(.*)$
RewriteRule ^.*$ ${urlmap:%1} [R=301,NE,L]
// Implementation Example：URL 對照表配合 RewriteMap
```

實際案例：作者提及生成 Disqus 連結遷移對照表；在系統更換時保留評論可追溯性與外部連結可用性。
實作環境：網站伺服器（Apache/Nginx）、腳本、Disqus 資料。
實測數據：
- 改善前：舊評論失聯。
- 改善後：評論鏈結保留，重定向正常。
- 改善幅度：社群資產保全（作者觀察）。

Learning Points（學習要點）
- 遷移時保留社群與 SEO 是重要非功能性需求。
- 對照表是關鍵 artefact。
- 重定向需測試與監控。

技能要求：
- 必備技能：Web 伺服器 rewrite。
- 進階技能：資料導出與映射。

延伸思考：
- 可擴展到其他嵌入服務。
- 風險：重定向迴圈與錯誤。
- 優化：加上健康檢查與告警。

Practice Exercise（練習題）
- 基礎練習：產生一個 URL 對照表（30 分鐘）。
- 進階練習：設定 RewriteMap 並測試（2 小時）。
- 專案練習：完成完整遷移（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：導出+映射+重定向。
- 程式碼品質（30%）：映射檔可維護。
- 效能優化（20%）：重定向效率與正確性。
- 創新性（10%）：遷移策略設計。


## Case #15: 上下文工程（避免爆量與抓重點）

### Problem Statement（問題陳述）
**業務場景**：模型的 context window 有限；如果上下文爆量，回答將失焦且成本上升。需要精準控制帶入內容。
**技術挑戰**：如何在工具與流程層面管理上下文與 token。
**影響範圍**：回答品質、成本、效能。
**複雜度評級**：中-高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 直接塞全文造成噪音。
2. 未建立「先檢索再讀取」的流程。
3. 工具未對上下文與 token 進行控制。

**深層原因**：
- 架構層面：缺少上下文管理策略。
- 技術層面：工具返回過大、參數欠缺。
- 流程層面：未在 instructions 中設定上下文規則。

### Solution Design（解決方案設計）
**解決策略**：以「learn/gating→chunks→full→generate」四段式工作流，配合 synthesis 與 limit 參數；工具返回以 Markdown 的高語意密度降低 token；必要時要求引用而非全文。

**實施步驟**：
1. 工作流定義
- 實作細節：入口→探索→拉取→生成；清楚分步。
- 所需資源：工具與提示。
- 預估時間：0.5 天

2. 參數與限制
- 實作細節：synthesis/limit/tokens/paths 等把控。
- 所需資源：MCP server。
- 預估時間：1 天

3. 客戶端觀察與回饋
- 實作細節：展示工具呼叫、調整參數。
- 所需資源：MCP 客戶端。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```json
// 控制上下文示例
{ "tool":"SearchChunks", "input":{ "query":"...", "synthesis":"summary", "limit":8 } }
{ "tool":"GetPostContent", "input":{ "postid":"...", "synthesis":"solution", "position":0, "length":1024 } }
// Implementation Example：分段拉取 + 限制長度
```

實際案例：作者以 Shopify 的分層工具作參考，自家 MCP 中強調「先檢索再讀取」，避免上下文爆量；在 Q/A 與 coding 中取得更佳結果。
實作環境：MCP Server、LLM、客戶端。
實測數據：
- 改善前：上下文爆量，失焦且成本高。
- 改善後：上下文精準，回答抓重點，成本下降（作者觀察）。
- 改善幅度：品質與成本雙提升。

Learning Points（學習要點）
- 上下文工程是 MCP-first 的靈魂。
- 工具參數是控制槓桿。
- 分段式工作流最有效。

技能要求：
- 必備技能：提示與上下文設計。
- 進階技能：成本與品質折衝。

延伸思考：
- 可加上動態 token budget 管理。
- 風險：過度切分導致語意丟失。
- 優化：片段元資料與引用策略。

Practice Exercise（練習題）
- 基礎練習：為工具加入 limit/length 控制（30 分鐘）。
- 進階練習：實作四段式工作流（2 小時）。
- 專案練習：建立上下文度量與報表（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：分段流程與參數控制。
- 程式碼品質（30%）：返回可解析、限制嚴謹。
- 效能優化（20%）：token 與成本管理。
- 創新性（10%）：上下文工程策略。


## Case #16: MCP 發布與易用性（Streamable HTTP、跨客戶端）

### Problem Statement（問題陳述）
**業務場景**：希望一般使用者與開發者皆能快速接入 MCP；降低採用門檻，提高使用率。
**技術挑戰**：協議支持、無需 API key、簡化安裝流程。
**影響範圍**：採用率、體驗、社群擴散。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 安裝複雜導致阻力。
2. 認證與金鑰管理造成成本。
3. 客戶端兼容性差。

**深層原因**：
- 架構層面：過度安全/配置，阻礙體驗。
- 技術層面：未選擇通用傳輸方式。
- 流程層面：缺少一步到位的安裝指引。

### Solution Design（解決方案設計）
**解決策略**：使用 Streamable HTTP 發布 MCP，無需登入與 API key；提供簡單 URL 安裝指引；在 VSCode/ChatGPT 等主流 MCP Host 上快速接入。

**實施步驟**：
1. 傳輸/協議選型
- 實作細節：採用 Streamable HTTP。
- 所需資源：MCP Host 支援列表。
- 預估時間：0.5 天

2. 安裝指引與範例
- 實作細節：提供 VSCode 安裝步驟、ChatGPT 使用。
- 所需資源：文檔與截圖。
- 預估時間：0.5 天

3. 測試與兼容性驗證
- 實作細節：在兩個以上客戶端驗證工具運行。
- 所需資源：ChatGPT Plus、VSCode。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```text
Transport: Streamable HTTP
URL: https://columns-lab.chicken-house.net/api/mcp/  （結尾 / 不可省略）

VSCode：F1 → MCP: Add Server → HTTP → 輸入 URL → 命名 → OK
ChatGPT：啟用 MCP（beta），新增 HTTP MCP Server
// Implementation Example：一步到位的安裝與接入
```

實際案例：作者公開 MCP URL，使用者可在 VSCode/ChatGPT 快速接入，降低體驗門檻。
實作環境：HTTP MCP Server、VSCode、ChatGPT。
實測數據：
- 改善前：需要自建或複雜設定。
- 改善後：直接接入即可使用。
- 改善幅度：採用率與體驗提升（作者觀察）。

Learning Points（學習要點）
- 易用性是擴散的前提。
- 無鍵接入降低阻力。
- 主流客戶端覆蓋重要。

技能要求：
- 必備技能：MCP 部署與配置。
- 進階技能：客戶端兼容與測試。

延伸思考：
- 後續可加上 API key 與配額。
- 風險：無鍵可能濫用。
- 優化：速率限制與審計。

Practice Exercise（練習題）
- 基礎練習：發布一個 HTTP MCP（30 分鐘）。
- 進階練習：在兩個客戶端測試工具（2 小時）。
- 專案練習：建立安裝指引與疑難排解文檔（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可接入並可用。
- 程式碼品質（30%）：配置清晰。
- 效能優化（20%）：連線穩定。
- 創新性（10%）：指引與體驗設計。


## Case #17: 可靠性與安全邊界（AI 不可預測下的工具防護）

### Problem Statement（問題陳述）
**業務場景**：AI 會以不可預測方式呼叫工具；若缺乏邊界與驗證，易引發錯誤與風險。
**技術挑戰**：守住工具合法性與安全性，避免被 AI「找漏洞」。
**影響範圍**：服務穩定性、安全、信任。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 工具缺乏參數驗證與邊界檢查。
2. 無速率限制與拒絕策略。
3. 未對返回敏感資訊做過濾。

**深層原因**：
- 架構層面：工具設計未達「可靠」標準。
- 技術層面：缺乏輸入/輸出驗證。
- 流程層面：未設計濫用防護與審計。

### Solution Design（解決方案設計）
**解決策略**：為工具加上嚴格參數驗證、limit/length 邊界、速率限制、錯誤訊息標準化；返回僅必要資訊；在 instructions 中載明限制。

**實施步驟**：
1. 參數與邊界驗證
- 實作細節：必填檢查、範圍限制、型態檢查。
- 所需資源：工具層驗證庫。
- 預估時間：1 天

2. 速率限制與拒絕策略
- 實作細節：per-session/per-IP 限制；清楚錯誤碼。
- 所需資源：伺服器中介層。
- 預估時間：1 天

3. 返回過濾與最小化
- 實作細節：返回只含必要元資料；敏感資訊過濾。
- 所需資源：工具層。
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```typescript
// 參數驗證與邊界（示意）
function validateSearchChunks(input) {
  if (!input.query || typeof input.query !== 'string') throw new Error('query required');
  const limit = Math.min(Math.max(input.limit ?? 5, 1), 20); // 1..20
  const allowed = ['origin','solution','faq','summary'];
  const synth = Array.isArray(input.synthesis) ? input.synthesis.filter(s => allowed.includes(s)) : [input.synthesis];
  return { query: input.query.trim(), synthesis: synth, limit };
}
// Implementation Example：守住參數與返回邊界
```

實際案例：作者在「API 必須可靠」的原則下，為 MCP 工具設計守邊界與拒絕策略，防止 AI 任意呼叫造成異常。
實作環境：MCP server、中介層。
實測數據：
- 改善前：工具可被亂用、易出錯。
- 改善後：錯誤率與濫用情形下降（作者觀察）。
- 改善幅度：可靠性明顯提升。

Learning Points（學習要點）
- MCP-first 同時要「合情合理」與「可靠」。
- 拒絕策略是安全的一部分。
- 返回最小化減少風險。

技能要求：
- 必備技能：驗證與錯誤處理。
- 進階技能：速率限制、審計。

延伸思考：
- 可加入權限與多租戶隔離。
- 風險：過度限制降低可用性。
- 優化：基於風險分級的限制。

Practice Exercise（練習題）
- 基礎練習：為一個工具加入參數驗證（30 分鐘）。
- 進階練習：加入速率限制與錯誤碼（2 小時）。
- 專案練習：設計完整安全與可靠策略（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：驗證/限制/拒絕齊備。
- 程式碼品質（30%）：錯誤訊息清楚一致。
- 效能優化（20%）：限制不影響正常使用。
- 創新性（10%）：安全策略設計。


--------------------------------
案例分類
--------------------------------

1. 按難度分類
- 入門級（適合初學者）
  - Case #9（演進史彙整）
  - Case #16（MCP 發布與易用性）
  - Case #13（檔名與網址正規化）
- 中級（需要一定基礎）
  - Case #5（片段→全文分層）
  - Case #6（查詢策略優化）
  - Case #8（Q/A 與引用）
  - Case #11（相關文章工具）
  - Case #12（HTML→Markdown 轉換）
  - Case #14（Disqus 對照表）
  - Case #15（上下文工程）
  - Case #17（可靠性與安全邊界）
- 高級（需要深厚經驗）
  - Case #1（MCP-first 工具介面設計）
  - Case #2（長文預處理與正規化）
  - Case #3（Repo 重構與流程效率化）
  - Case #4（指令閘道工具）
  - Case #7（Pipeline CLI 平行處理）

2. 按技術領域分類
- 架構設計類
  - Case #1、#2、#4、#5、#15、#17
- 效能優化類
  - Case #5、#7、#12、#15
- 整合開發類
  - Case #3、#7、#8、#9、#11、#16
- 除錯診斷類
  - Case #4、#5、#6、#17
- 安全防護類
  - Case #4、#17、#14

3. 按學習目標分類
- 概念理解型
  - Case #1、#2、#5、#15
- 技能練習型
  - Case #7、#12、#13、#14、#16
- 問題解決型
  - Case #3、#6、#8、#9、#11、#17
- 創新應用型
  - Case #4、#5、#7、#15


--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------

- 先學哪些案例？
  - 起點：Case #1（理解 MCP ≠ API，workflow-first）
  - 內容工程：Case #2（synthesis 型態）、Case #12（HTML→Markdown）
  - 檢索分層：Case #5（chunks→全文）、Case #6（查詢策略）
  - 上下文工程：Case #15（上下文管控）

- 案例之間的依賴關係
  - Case #1 → Case #4（入口工具/指令閘道）→ Case #5（分層檢索）→ Case #8（Q/A 引用）
  - Case #2 → Case #10（synthesis 參數）→ Case #5（檢索分層）
  - Case #12 → Case #3（Repo 重構）→ Case #11（相關文章）→ Case #9（演進史彙整）
  - Case #1/#2/#5 → Case #7（vibe coding）→ 實戰產出
  - Case #4/#17 → 全部案例（可靠性與安全邊界）

- 完整學習路徑建議
  1. 概念與架構：Case #1 → Case #2 → Case #15
  2. 檢索與上下文：Case #5 → Case #6 → Case #10
  3. 基礎工程清理：Case #12 → Case #13 → Case #14 → Case #3
  4. 工具與可靠性：Case #4 → Case #17 → Case #11
  5. 實戰應用：Case #8（Q/A）→ Case #9（彙整）→ Case #7（vibe coding）→ Case #16（發布）
  6. 綜合演練：將以上整合為你的 MCP-first 知識庫與開發助手

以上 17 個案例均依據本文內容抽取與重構為具教學價值的解決方案，涵蓋從理念到落地、從內容到代碼、從檢索到上下文工程、從易用性到可靠性。