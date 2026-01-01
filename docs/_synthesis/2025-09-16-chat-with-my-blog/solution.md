---
layout: synthesis
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計"
synthesis_type: solution
source_post: /2025/09/16/chat-with-my-blog/
redirect_from:
  - /2025/09/16/chat-with-my-blog/solution/
postid: 2025-09-16-chat-with-my-blog
---
以下為基於文章內容所提取並結構化的 16 個問題解決案例。每個案例均遵循指定模板，涵蓋問題、根因、解法（含程式碼/工作流）、成效與教學要點。最後附上分類與學習路徑建議。

## Case #1: MCP-first 設計：工具不是 API

### Problem Statement（問題陳述）
業務場景：作者希望讓部落格內容能被 Agent 高效理解與運用，用於問答、解題、寫碼等情境。然而如果只把既有 REST API 直接包成 MCP，Agent 在實際工作流程中仍難以自然、正確地操作，導致檢索不精準、理解斷裂、行為不穩定。
技術挑戰：如何設計 MCP tools，使其貼合 Agent 的思考脈絡與工作流程（context + workflow），而非單純映射 API 端點。
影響範圍：影響整體 Agent 使用質量（準確度、穩定性）、問答解題的成功率與開發者體驗。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 工具介面以「API 對應」設計，而非「工作流程導向」，造成語義與操作意圖錯位。
2. MCP 工具回應偏向結構化 JSON，缺乏對 LLM 友善的標示（Markdown）與動態說明（instructions）。
3. 缺少對 Agent 的「使用規範引導」（如必須先學習/授權的 gating）。
深層原因：
- 架構層面：介面邏輯過度耦合應用 UI/既有 API，不符合 MCP 的「模型情境協定」精神。
- 技術層面：忽視 LLM 對上下文的依賴與推理方式（prompting/工具使用順序）。
- 流程層面：需求分析停留在功能清單，未抽象為使用者/Agent 的工作流程。

### Solution Design（解決方案設計）
解決策略：以 Workflow First 設計 MCP，依使用情境（訂閱、解答、解題、學習）拆解 Agent 的行動步驟，針對這些步驟設計最小必要、語義清晰、帶指引（instructions）的工具，並以 Markdown 作為主要回應載體以提高 LLM 理解準確度。

實施步驟：
1. 定義使用情境與工作流程
- 實作細節：分解訂閱/解答/解題/學習的操作序列與決策點
- 所需資源：需求梳理工作坊、對話樣本、過往文章集
- 預估時間：1-2 天

2. 設計 MCP 工具規格
- 實作細節：定義 Tools（GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts）之輸入/輸出、錯誤準則與回應格式
- 所需資源：MCP Host/Inspector、規格文件
- 預估時間：2-3 天

3. 回應格式優化（Markdown + 指令嵌入）
- 實作細節：在工具回應中夾帶使用說明、優先級、限制、後續操作建議
- 所需資源：模板引擎、測試 Agent（Claude、ChatGPT）
- 預估時間：1-2 天

4. 工作流驗證（小型用例）
- 實作細節：Q&A、解題、vibe coding 實測，觀察工具呼叫序列與結果
- 所需資源：VSCode + Copilot、ChatGPT Plus
- 預估時間：1-3 天

關鍵程式碼/設定：
```json
// MCP Tools Manifest (概念示例)
{
  "tools": [
    { "name": "GetInstructions", "input": {}, "outputFormat": "markdown" },
    { "name": "SearchChunks", "input": { "query": "string", "synthesis": ["origin","solution","faq","summary"], "limit": "int" } },
    { "name": "SearchPosts", "input": { "query": "string", "synthesis": "string", "limit": "int" } },
    { "name": "GetPostContent", "input": { "postid": "string", "synthesis": "string", "position": "int", "length": "int" } },
    { "name": "GetRelatedPosts", "input": { "postid": "string", "limit": "int" } }
  ]
}
```

實際案例：文章中作者將部落格資源服務化，以上述五個工具支援 Agent 的解答/解題/學習工作流。
實作環境：MCP Server（Streamable HTTP）、VSCode + Copilot、ChatGPT Plus（GPT-5 + Thinking）。
實測數據：
改善前：包 API 為 MCP，Agent 常呼叫不合時宜端點、上下文不連貫。
改善後：工具呼叫遵循工作流程，Q&A/解題過程穩定；實測案例中引用正確且無幻覺。
改善幅度：主觀可用性與準確性顯著提升（實例中錯誤率~0；文字潤飾差異但引文正確）。

Learning Points（學習要點）
核心知識點：
- MCP-first vs API-first 差異
- Workflow First 設計法
- Markdown 回應對 LLM 理解的優勢
技能要求：
- 必備技能：需求分析、API/工具介面設計、LLM 基本 Prompting
- 進階技能：Context Engineering、Agent 工具呼叫策略設計
延伸思考：
- 可用於任何要讓 Agent 操作的服務化介面
- 風險：工具過多/過細導致選擇困難；回應太冗長擴大 context
- 優化：分層工具（探索/規劃/執行）、強化 gating 與指令嵌入

Practice Exercise（練習題）
基礎練習：將一個查詢功能改為 Workflow First 的 MCP 工具（30 分鐘）
進階練習：為「查文件→取段落→取全文」設計三段式工具與指令（2 小時）
專案練習：將一個小型服務完整 MCP 化並設計 3 條工作流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：工具覆蓋工作流程關鍵步驟
程式碼品質（30%）：介面一致性、型別安全、容錯
效能優化（20%）：上下文控制（少量必要信息）
創新性（10%）：指令嵌入與分層設計巧思


## Case #2: GetInstructions 作為 Tool 的動態指引與 Gating

### Problem Statement（問題陳述）
業務場景：Agent 初次使用某服務時常不清楚該如何操作，容易跳過必要前置，導致後續工具呼叫失敗或行為偏離。
技術挑戰：如何讓 Agent 在每次使用前確保獲得最新的使用說明與必要上下文（例如 conversationId）。
影響範圍：影響所有後續工具的正確性與成功率，降低無效呼叫與資源浪費。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態說明文件不一定被載入到 context；Agent 可能忽略。
2. 不同會話需注入動態資訊（如 session/conversationId），用戶端難保證。
3. 工具之間缺少「執行順序」約束，造成亂序調用。
深層原因：
- 架構層面：缺乏「入口工具」作為工作流啟動點。
- 技術層面：工具回應未嵌入指令，LLM 難以在回應中獲取規則。
- 流程層面：無「必經步驟」控制，導致流程不規範。

### Solution Design（解決方案設計）
解決策略：將 GetInstructions 設計為工具而非描述，回應中嵌入「必須先呼叫」的強制規範與動態資訊（如 conversationId），並在其他工具中要求帶入該 id 才允許執行，以此達到 gating 效果。

實施步驟：
1. 設計 GetInstructions Tool
- 實作細節：回應 Markdown，包含「必須先呼叫」警告、會話 id、使用規則
- 所需資源：MCP 伺服器、模板引擎
- 預估時間：0.5-1 天

2. 在其他工具強制驗證 conversationId
- 實作細節：所有 tools 檢查必填的 id，缺少則返回錯誤與指引
- 所需資源：伺服端驗證邏輯
- 預估時間：0.5 天

3. 實測與追蹤
- 實作細節：使用不同 Agent 進行多輪測試，觀察順序與成功率
- 所需資源：ChatGPT Plus、VSCode + Copilot
- 預估時間：1 天

關鍵程式碼/設定：
```markdown
# GetInstructions 回應範例（嵌入 gating 與會話資訊）

🚨 MANDATORY FIRST STEP: 請先呼叫本工具，後續所有工具必須帶入 conversationId。
🔗 Conversation ID（保存於上下文）：`f2c9e3f1-...-abcd`

使用規則：
1. 先呼叫本工具以載入最新指引與會話資訊
2. 往後工具呼叫請在參數中包含 `conversationId`
3. 如需切換主題，請再次呼叫本工具以刷新指引（維持同一 conversationId）
```

實際案例：作者受 Shopify MCP 啟發，設計了工具化的 instructions，降低亂序呼叫與誤用；以此方式讓 Agent 保持規範。
實作環境：MCP Server；ChatGPT Plus；VSCode + Copilot。
實測數據：
改善前：偶有工具亂序呼叫、缺少前置資訊導致失敗。
改善後：先呼叫 GetInstructions 成為常態，後續工具成功率提升。
改善幅度：流程錯誤顯著下降（定性描述），測試對話中未再出現缺少前置導致的錯誤。

Learning Points（學習要點）
核心知識點：
- 工具化 instructions 與 gating 思想
- 在回應中嵌入對 LLM 友善的規範
技能要求：
- 必備技能：MCP 工具設計、上下文管理
- 進階技能：會話狀態控制、錯誤設計
延伸思考：
- 可用於涉及認證/版本/租戶資訊的所有工具
- 風險：過度強制可能降低靈活度
- 優化：分層 gating、允許在特定場景放寬約束

Practice Exercise（練習題）
基礎練習：為現有工具加入「必須先呼叫指引工具」的檢查（30 分鐘）
進階練習：設計 conversationId 驗證與刷新機制（2 小時）
專案練習：為一組文件檢索工具設計完整 gating 與錯誤回應策略（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：gating 流程覆蓋所有工具
程式碼品質（30%）：狀態管理清晰、錯誤一致
效能優化（20%）：指令回應精簡有效
創新性（10%）：指令嵌入與驗證機制巧思


## Case #3: 文章正規化：LLM 合成為 RAG 友善的型態

### Problem Statement（問題陳述）
業務場景：作者文章多為「情境→問題→PoC→解法」的長文，直接做 RAG 因切片後每片非完整主題，檢索出來難以應用，導致回答不準、解題效率低。
技術挑戰：如何在發布前將文章預處理為「合用」的型態，提升向量檢索精確度與應用效果。
影響範圍：影響 Q&A 準確率、解題成功率與 Agent 用文效率。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 長文切片後的內容斷裂，單片上下文不足。
2. 直接向量化 HTML/Markdown 雜訊多，語義密度低。
3. 檢索結果無法對映到「解法/FAQ/原理」等可用形態。
深層原因：
- 架構層面：缺少發佈前的內容管線（pre-generation/synthesis）。
- 技術層面：未定義細粒度且語義化的內容結構（origin/solution/faq/summary）。
- 流程層面：未將內容正規化納入編輯/發布流程。

### Solution Design（解決方案設計）
解決策略：建立內容預處理管線，使用 LLM 將長文生成為多種「可用型態」（origin, solution, faq, summary），並以結構化片段（chunks）保存，用於後續向量檢索與精準 RAG。

實施步驟：
1. 定義 synthesis schema
- 實作細節：規範各型態的欄位與最小上下文需求
- 所需資源：Schema 設計、範例文章
- 預估時間：1 天

2. 建立 LLM 預生成流程
- 實作細節：以 prompt+model 批量轉換文章為多型態片段
- 所需資源：Azure OpenAI 額度、批次工具
- 預估時間：2-3 天

3. 向量化與索引
- 實作細節：針對各型態片段向量化並建立檢索索引
- 所需資源：向量資料庫
- 預估時間：1-2 天

4. MCP 介面擴充（synthesis 參數）
- 實作細節：SearchChunks/Posts 支援按型態檢索
- 所需資源：MCP Server 修改
- 預估時間：0.5-1 天

關鍵程式碼/設定：
```json
// Synthesis 片段結構（概念範例）
{
  "postId": "2019-06-15-netcli-pipeline",
  "type": "solution", // origin|solution|faq|summary
  "title": "CLI + Pipeline 的並行處理解法",
  "content": "以 STDIO 接收 JSONL，使用 Channel 實作生產者-消費者...",
  "tags": ["pipeline","CLI","parallel","C#"],
  "embedding": "[向量]",
  "references": ["..."]
}
```

實際案例：作者為長文建立 synthesis，以「solution/faq」型態提供檢索；實測顯示 Q&A 能引用正確且有用的內容片段。
實作環境：Azure OpenAI（MVP 額度）、MCP Server、向量索引。
實測數據：
改善前：RAG 片段非完整主題，答案可用性低。
改善後：能依型態查到可直接使用的片段，回答準確、解題更順。
改善幅度：問答可用性與準確度顯著提升（定性），實例中引文正確且無幻覺。

Learning Points（學習要點）
核心知識點：
- Content Synthesis（LLM 預生成）
- 型態化檢索（origin/solution/faq/summary）
- 向量索引策略
技能要求：
- 必備技能：Prompt 設計、資料建模、向量化
- 進階技能：批次處理、成本控管（token）
延伸思考：
- 可應用於企業知識庫、手冊、規範文件
- 風險：生成品質不一、token 成本高
- 優化：採樣驗證、增量更新、模型/提示調優

Practice Exercise（練習題）
基礎練習：為一篇長文生成 summary 與 faq 片段（30 分鐘）
進階練習：設計片段 schema 並向量化建立索引（2 小時）
專案練習：為 50 篇文章批量生成 4 型態片段並接入 MCP（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：片段型態覆蓋與檢索對應
程式碼品質（30%）：資料結構與索引一致性
效能優化（20%）：成本與速度平衡
創新性（10%）：片段語義設計與應用巧思


## Case #4: 查詢設計：SearchChunks + synthesis 精準檢索

### Problem Statement（問題陳述）
業務場景：Agent 需在多主題文章中快速找到「可用片段」，若查詢語彙與片段型態不匹配，可能返回噪音或不完整資訊。
技術挑戰：設計查詢參數與語彙，使模型能精準對應到可用片段（solution/faq/origin/summary）。
影響範圍：影響問答與解題的精準度與生成品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 查詢語彙籠統，沒有指向特定片段型態。
2. Limit/語彙調校不佳，返回範圍偏離意圖。
3. 未分模型調校（Claude vs GPT）導致行為差異。
深層原因：
- 架構層面：未在工具層支援型態化檢索。
- 技術層面：未設計模型差異化的查詢模板。
- 流程層面：缺少查詢/回應迭代（先粗後精）的流程。

### Solution Design（解決方案設計）
解決策略：在 SearchChunks 加入 synthesis 參數，規範查詢語彙與型態；並針對不同模型設計查詢模板與迭代策略（第一次廣域、第二次聚焦）。

實施步驟：
1. 增加 synthesis 參數
- 實作細節：SearchChunks 支援 ["origin","solution","faq","summary"]
- 所需資源：MCP Server
- 預估時間：0.5 天

2. 設計查詢模板（模型別）
- 實作細節：Claude 用「分散式交易 + 型態」查詢；GPT 用「兩段查詢」迭代
- 所需資源：實測對話樣本
- 預估時間：1 天

3. 設計迭代流程
- 實作細節：先粗略查詢→根據回應再精細查詢
- 所需資源：Agent 配置
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
// Claude 查詢範例（文章提供）
{
  "limit": 10,
  "query": "分散式交易 distributed transaction saga 兩階段提交 2PC 微服務 跨服務交易",
  "synthesis": ["origin","solution","faq"]
}

// GPT-5 Thinking 查詢迭代（文章提供）
{
  "query":"微服務 分散式 交易 跨服務 一致性 Saga Outbox 兩階段提交 TCC 事件驅動 可靠投遞 基礎 知識",
  "synthesis":"summary",
  "limit":8
}
```

實際案例：作者兩種模型皆成功找到正確片段，回答正確且有引用；GPT 進行兩輪查詢再生成。
實作環境：ChatGPT Plus（GPT-5 + Thinking）、Claude Sonnet 4。
實測數據：
改善前：單輪查詢易返回不完整/不精準片段。
改善後：指定型態與迭代查詢，返回片段可直接使用。
改善幅度：回答準確性與貼近度顯著提升（定性）；無幻覺且引用正確。

Learning Points（學習要點）
核心知識點：
- 型態化查詢與迭代流程
- 模型差異化調校
技能要求：
- 必備技能：查詢語彙設計、工具參數設計
- 進階技能：模型行為觀察與 A/B
延伸思考：
- 可用於大型文庫檢索
- 風險：模板過度擬合某模型
- 優化：動態根據回應調整下一輪查詢

Practice Exercise（練習題）
基礎練習：為一組主題設計 synthesis 查詢（30 分鐘）
進階練習：針對兩種模型設計不同查詢迭代策略（2 小時）
專案練習：建立查詢模板庫與自動化選擇策略（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：查詢覆蓋與型態對應
程式碼品質（30%）：參數設計一致性
效能優化（20%）：迭代次數與結果密度
創新性（10%）：模型特性導向的策略設計


## Case #5: 解題工作流：SearchPosts → GetPostContent → GetRelatedPosts

### Problem Statement（問題陳述）
業務場景：解題情境下，使用者需要先找線索，再定位原文，最後擴展相近主題以形成完整解法。
技術挑戰：將「尋線索→取原文→找相關」流程工具化，讓 Agent 無縫代辦。
影響範圍：影響解題效率、解法完整度與引用正確性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 工具設計未對應「尋線索→取原文→擴展」流程。
2. 檢索結果無法快速連到全文與相關文。
3. Agent 難以自動形成「步驟序列」。
深層原因：
- 架構層面：工具缺少互補與串接意圖。
- 技術層面：缺少必要標識（postid）與元資料。
- 流程層面：未定義多步驟的標準操作序列。

### Solution Design（解決方案設計）
解決策略：提供 SearchPosts、GetPostContent、GetRelatedPosts 三工具，分別負責尋線索、取得原文、擴展相近主題，並在回應中嵌入下一步建議以引導 Agent。

實施步驟：
1. 設計工具規格
- 實作細節：postid 為主鍵；GetPostContent 支援 synthesis/position/length
- 所需資源：MCP Server
- 預估時間：0.5-1 天

2. 回應嵌入下一步建議
- 實作細節：在 SearchPosts 回應中附「建議呼叫 GetPostContent(postid)」
- 所需資源：模板引擎
- 預估時間：0.5 天

3. 整體流程測試
- 實作細節：以「微服務交易」案例實測三步驟串接
- 所需資源：ChatGPT/VSCode
- 預估時間：1 天

關鍵程式碼/設定：
```json
// 呼叫序列（概念示例）
1) SearchPosts { "query": "微服務 分散式 交易 Saga 2PC", "limit": 5 }
→ 返回 [ { "postid": "2019-06-15-netcli-pipeline", "title": "...", ... }, ... ]

2) GetPostContent { "postid": "2019-06-15-netcli-pipeline", "synthesis": "solution" }

3) GetRelatedPosts { "postid": "2019-06-15-netcli-pipeline", "limit": 5 }
```

實際案例：作者在 vibe coding 場景中使用該串接流程；Agent 正確抓到原文與相關文，並生成符合文章精神的程式碼。
實作環境：MCP Server；VSCode + Copilot；ChatGPT Plus。
實測數據：
改善前：人工 Google +手動整理，耗時且易遺漏。
改善後：Agent 串接三工具自動完成，生成與引用準確。
改善幅度：作業時長從數小時降至數分鐘（>10x）。

Learning Points（學習要點）
核心知識點：
- 多工具串接與回應引導
- postid/元資料設計
技能要求：
- 必備技能：工具規格與串接
- 進階技能：回應嵌入下一步建議
延伸思考：
- 可擴展「取全文」前先「看 chunks」節流 context
- 風險：相關文過度擴展造成上下文爆量
- 優化：限制 limit/權重排序

Practice Exercise（練習題）
基礎練習：為任一主題設計三步驟工具串接（30 分鐘）
進階練習：實作回應中的下一步建議與序列自動化（2 小時）
專案練習：建立完整解題工作流並測試三種主題（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：工具串接覆蓋流程
程式碼品質（30%）：回應一致性與錯誤處理
效能優化（20%）：上下文控制與 limit 策略
創新性（10%）：回應引導設計


## Case #6: Chat with My Blog：微服務分散式交易知識問答

### Problem Statement（問題陳述）
業務場景：開發者需要理解微服務中跨服務交易（Saga、2PC、Outbox、TCC 等）之基礎知識與注意事項。
技術挑戰：在大量文章中快速提取正確且引用完整的答案，避免幻覺與錯引。
影響範圍：影響學習效率、錯誤理解風險、工程設計品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 知識分散在多篇文章與片段。
2. 長文內容直做 RAG 檢索不精準。
3. 模型回答若無引用易產生幻覺。
深層原因：
- 架構層面：缺少可用型態片段（faq/summary/solution）。
- 技術層面：查詢語彙未指向正確片段型態。
- 流程層面：回答缺少引用標準化。

### Solution Design（解決方案設計）
解決策略：使用 SearchChunks（含 synthesis）精準檢索，並在回答中要求附上標題與連結；若必要，二輪查詢以提升聚焦。

實施步驟：
1. 以 summary/faq 查詢基礎知識
- 實作細節：指定 synthesis，提高答案密度
- 所需資源：ChatGPT Plus
- 預估時間：10 分鐘

2. 二次查詢 solution 片段
- 實作細節：針對關鍵術語再查一次
- 所需資源：同上
- 預估時間：10 分鐘

3. 生成答案並附引用
- 實作細節：回答附「標題+連結」
- 所需資源：同上
- 預估時間：5 分鐘

關鍵程式碼/設定：
```json
// 問題（文章提供）
"開發分散式的系統，實作微服務架構，面臨跨服務的交易問題；身為開發人員，我有哪些基礎的底層知識需要具備？"

// SearchChunks 查詢（Claude/GPT 範例已在 Case #4）
```

實際案例：作者於 ChatGPT Plus（GPT-5 + Thinking）與 Claude 測試，兩者均引用正確、無幻覺；GPT 展現二輪查詢再生成的行為。
實作環境：ChatGPT Plus；Claude；MCP Server。
實測數據：
改善前：單靠模型知識或一般 RAG 易不完整/出錯。
改善後：引用正確、內容準確、無幻覺。
改善幅度：答案可靠性顯著提升（定性），查詢-回答總時長 <2 分鐘。

Learning Points（學習要點）
核心知識點：
- 問答場景的型態化檢索
- 引用規範與抗幻覺
技能要求：
- 必備技能：查詢語彙與 synthesis 選擇
- 進階技能：多輪查詢與回應結構化
延伸思考：
- 可用於企業 FAQ 與標準作業
- 風險：過度依賴片段，忽略整體語境
- 優化：必要時 fetch_full_content 做二次核對

Practice Exercise（練習題）
基礎練習：針對一組術語進行 faq/summary 查詢並回答（30 分鐘）
進階練習：二輪查詢與引用格式化輸出（2 小時）
專案練習：建立特定領域的問答代理，接入 MCP（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：問答與引用完整
程式碼品質（30%）：查詢與回應模板清晰
效能優化（20%）：查詢輪次與時間
創新性（10%）：回答結構與引用設計


## Case #7: Vibe Coding：用文章驅動 CLI + Pipeline 程式碼生成

### Problem Statement（問題陳述）
業務場景：開發者希望依照作者文章的實作思路，快速建立 CLI 程式，以 STDIO 接收 JSONL 並平行處理每筆資料。
技術挑戰：如何讓 Agent 透過 MCP 讀取文章精華，生成符合現代 .NET 寫法的並行處理架構。
影響範圍：影響開發效率、程式品質與學習體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 人工 Google +閱讀+手寫耗時。
2. 舊文用法（BlockingCollection）與新語法（Channel）差異。
3. 無法快速構成完整程式骨架。
深層原因：
- 架構層面：缺少由「文章」到「程式骨架」的工作流。
- 技術層面：Agent 對文章片段的抽取與重組。
- 流程層面：缺乏「指定資料型別+目標行為」的明確指令。

### Solution Design（解決方案設計）
解決策略：在 VSCode + Copilot 下安裝 MCP，使用 SearchPosts→GetPostContent（solution）→SearchChunks 的串接，配合 Agent 指令（STDIO JSONL + parallelism）生成程式骨架，再由人補入業務邏輯。

實施步驟：
1. 準備專案與型別
- 實作細節：建立 console app，定義 UserItem 類別
- 所需資源：.NET SDK、VSCode
- 預估時間：10 分鐘

2. Agent 指令與 MCP 串接
- 實作細節：要求 STDIO JSONL + 並行處理；Agent 自動查文與抽取
- 所需資源：Copilot、MCP Server
- 預估時間：1 分鐘生成

3. 測試資料與腳本
- 實作細節：生成測試用 JSONL 與 shell 腳本，執行驗證
- 所需資源：bash/PowerShell
- 預估時間：5 分鐘

關鍵程式碼/設定：
```csharp
// 文章提供之核心並行處理片段（.NET Channel）
static async Task ProcessDataInParallel(int parallelism)
{
    var channel = System.Threading.Channels.Channel.CreateBounded<UserItem>(100);
    var reader = channel.Reader;
    var writer = channel.Writer;

    var producerTask = Task.Run(async () =>
    {
        try { await foreach (var item in ReadFromStdin()) await writer.WriteAsync(item); }
        finally { writer.Complete(); }
    });

    var consumerTasks = Enumerable.Range(0, parallelism)
        .Select(workerId => Task.Run(async () =>
        {
            await foreach (var item in reader.ReadAllAsync())
            {
                var processedItem = await ProcessSingleItem(item, workerId);
                await OutputResult(processedItem);
            }
        })).ToArray();

    await Task.WhenAll(new[] { producerTask }.Concat(consumerTasks));
}
```

實際案例：作者以 VSCode + Copilot，1 分鐘生成骨架，5 分鐘補測試與驗證；程式以 Channel 取代舊寫法，符合現代 .NET。
實作環境：VSCode + Copilot、.NET（近年版本）。
實測數據：
改善前：人工查文與實作需數小時。
改善後：程式骨架生成與測試僅需 6 分鐘左右。
改善幅度：時間縮短約 20-30x。

Learning Points（學習要點）
核心知識點：
- STDIO + JSONL 的流式處理
- Channel 生產者/消費者模式
技能要求：
- 必備技能：.NET 並行、CLI IO 基礎
- 進階技能：Agent 指令與工具串接
延伸思考：
- 可擴展為多階段 pipeline（過濾/轉換/聚合）
- 風險：平行度設定不當造成資源飽和
- 優化：加上背壓、錯誤重試、監控

Practice Exercise（練習題）
基礎練習：實作 ReadFromStdin 與 OutputResult（30 分鐘）
進階練習：加入重試與超時機制（2 小時）
專案練習：打造完整 CLI pipeline（過濾→驗證→入庫）（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：STDIO 流式與並行
程式碼品質（30%）：錯誤處理、資源管理
效能優化（20%）：平行度、背壓策略
創新性（10%）：Agent 引導與文章對應應用


## Case #8: 用 Agent 整理部落格演進史（Markdown 自動填寫）

### Problem Statement（問題陳述）
業務場景：作者希望依時間序整理 20 年的系統改版紀錄，包含主要項目與客製化子項並附標題與鏈接。手動整理耗時且易遺漏。
技術挑戰：如何讓 Agent 以 MCP 檢索文章、抽取要點、依格式填入 Markdown。
影響範圍：影響文稿編輯效率與完整性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 資訊散落在多篇文章與年份。
2. 手動 Google +編排耗時。
3. 格式化輸出需一致且附引用。
深層原因：
- 架構層面：未定義「整理→摘要→格式化」流程。
- 技術層面：Agent 對格式化輸出控制。
- 流程層面：編輯與檢索未整合。

### Solution Design（解決方案設計）
解決策略：在 VSCode 的 Agent 模式下，使用 SearchPosts/Chunks 檢索資料，並以「填入指定 Markdown 區段」的指令生成項目清單與引用，完成編輯。

實施步驟：
1. 設計輸出格式模板
- 實作細節：年份主項+子項+參考文章 [title](url)
- 所需資源：Markdown 範本
- 預估時間：0.5 天

2. Agent 指令與檢索
- 實作細節：指定「時間排序」「100 字以內」「附引用」
- 所需資源：VSCode + Copilot、MCP
- 預估時間：1 分鐘生成

3. 人工審核與微調
- 實作細節：核對年份、標題、URL 正確性
- 所需資源：編輯器
- 預估時間：10-20 分鐘

關鍵程式碼/設定：
```markdown
// Agent 指令（文章提供）
請幫我填上這段 markdown 區段，整理「安德魯的部落格」歷年移轉系統記錄。
- 按時間排序
- 每項 100 字內
- 附「參考文章：[title](url)」

(2008) 系統移轉: 改用 BlogEngine.NET
- ...
- 參考文章: [換到 BlogEngine.Net 了!](...)
```

實際案例：作者於 VSCode + Copilot 直接完成 Markdown 填寫；1 分鐘生成結果，人工微調即可。
實作環境：VSCode + Copilot；MCP Server。
實測數據：
改善前：過去需「一整晚」手工整理。
改善後：生成用時約 1 分鐘，微調約 10-20 分鐘。
改善幅度：時間縮短 ~30-60x。

Learning Points（學習要點）
核心知識點：
- 以 Agent 進行資料蒐集與格式化
- 引用標準化輸出
技能要求：
- 必備技能：資料抽取指令、Markdown 控制
- 進階技能：大量文章的主題歸納
延伸思考：
- 可用於週報、年報、變更紀錄
- 風險：年份或標題抽取誤差
- 優化：加入「年份解析」規則與校驗

Practice Exercise（練習題）
基礎練習：把 5 篇文章整理成時間序清單（30 分鐘）
進階練習：自動抽摘要+引用並填入既有 Markdown（2 小時）
專案練習：打造「變更史生成器」並接入 MCP（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：輸出符合模板且完整
程式碼品質（30%）：指令與流程清晰
效能優化（20%）：生成與微調時間
創新性（10%）：格式與引用設計


## Case #9: AI IDE 一次性重構 Repo：清除技術債

### Problem Statement（問題陳述）
業務場景：部落格 60-70% 文章仍為 HTML、中文檔名/網址、圖檔路徑雜亂、連結壞掉，影響後續向量檢索與發布管線。
技術挑戰：如何快速重構大量內容與結構，為內容正規化與 MCP 應用建立工程基礎。
影響範圍：影響整體內容品質、檢索可用性、發布效率。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 歷史遺留格式不一致（HTML vs Markdown）。
2. 非 ASCII 檔名/網址導致各種工具相容性問題。
3. 圖檔與連結未系統化維護。
深層原因：
- 架構層面：缺少統一內容與路徑規範。
- 技術層面：未建立批次修復工具與流程。
- 流程層面：Publishing Pipeline 未設品質門檻。

### Solution Design（解決方案設計）
解決策略：使用 AI IDE（VSCode + Copilot）與小工具一次性重構，包括 HTML→Markdown、批次改名、圖檔處理、連結修復、Disqus 對照表匯出；同步整理 repo 結構與本地/雲端驗證環境。

實施步驟：
1. 清單盤點與規範制定
- 實作細節：檔案型態、命名規範、路徑策略
- 所需資源：Repo 分析腳本
- 預估時間：0.5-1 天

2. 批次轉換與改名
- 實作細節：HTML→Markdown、中文→英文、路徑統一
- 所需資源：Copilot、轉換腳本、正則工具
- 預估時間：1-2 天

3. 連結與圖檔修復
- 實作細節：掃描/重寫連結、移除無用圖檔
- 所需資源：Node/Python 工具
- 預估時間：1 天

4. 發布與驗證
- 實作細節：本地跑 + GitHub Pages 驗證
- 所需資源：CI/CD 或手動驗證
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# 檔名正規化（概念範例）
find content -name "*[一-龥]*" -print0 | while IFS= read -r -d '' f; do
  new=$(echo "$f" | iconv -f UTF-8 -t ASCII//TRANSLIT | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
  git mv "$f" "$new"
done
```

實際案例：作者藉助 AI 一次性重構，清掉 HTML、中文檔名、錯誤連結與亂七八糟圖檔；整理 repo 結構並建立雙環境驗證。
實作環境：VSCode + Copilot、GitHub Pages、本地驗證。
實測數據：
改善前：向量檢索困難、發布容易出錯、編輯不順。
改善後：內容結構統一，寫作與檢索明顯順暢。
改善幅度：編輯/發布效率顯著提升（定性），向量化可行性大幅提高。

Learning Points（學習要點）
核心知識點：
- 技術債盤點與批次重構
- 發布管線品質門檻
技能要求：
- 必備技能：腳本處理、路徑/命名規範
- 進階技能：AI 助理驅動的重構策略
延伸思考：
- 可拓展至產品文件庫或內部知識庫
- 風險：批次改動可能導致歷史引用失效
- 優化：建立對照表與自動重定向

Practice Exercise（練習題）
基礎練習：清理 50 個中文檔名與錯誤連結（30 分鐘）
進階練習：完成 HTML→Markdown 批次轉換（2 小時）
專案練習：建立完整重構計畫與驗證清單（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：重構範圍與規範覆蓋
程式碼品質（30%）：腳本健壯性與日誌
效能優化（20%）：批次速度與風險控制
創新性（10%）：AI 助理運用策略


## Case #10: HTML → Markdown 轉換：提升向量檢索可用性

### Problem Statement（問題陳述）
業務場景：HTML 內容含大量格式噪音，不利向量化與 LLM 理解；需轉為 Markdown 提升語義密度與檢索效果。
技術挑戰：批量準確轉換 HTML 為 Markdown，保留語意結構與引用。
影響範圍：影響向量檢索品質與 RAG 應用表現。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. HTML 標籤/樣式帶來噪音。
2. 文章結構未明確表達語意層級。
3. 圖片與連結在轉換後易失效。
深層原因：
- 架構層面：缺乏內容轉換管線。
- 技術層面：未選擇合適轉換工具與規則。
- 流程層面：缺少轉換後的驗證與修復。

### Solution Design（解決方案設計）
解決策略：使用轉換工具（如 pandoc 或 html2text）搭配規則，批量將 HTML 轉為 Markdown，並在後處理中修復圖片連結與引用。

實施步驟：
1. 選擇工具與規則
- 實作細節：確定標題/段落/列表等映射
- 所需資源：pandoc/html2text
- 預估時間：0.5 天

2. 批量轉換
- 實作細節：遍歷 HTML 檔，輸出 MD 檔
- 所需資源：批次腳本
- 預估時間：1 天

3. 後處理修復
- 實作細節：修正圖片相對路徑、引用格式
- 所需資源：Node/Python 工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# 使用 pandoc 轉換（概念示例）
for f in content/**/*.html; do
  out="${f%.html}.md"
  pandoc "$f" -f html -t markdown_strict -o "$out"
done
```

實際案例：作者重構中將大比例 HTML 文章改為 Markdown；後續向量檢索與 RAG 效果改善。
實作環境：轉換工具、腳本環境。
實測數據：
改善前：HTML 噪音導致向量檢索不精準。
改善後：Markdown 語義密度提升，檢索精準度顯著改善（定性）。
改善幅度：RAG 可用性明顯提升。

Learning Points（學習要點）
核心知識點：
- Markdown 對 LLM 的友善性
- 轉換規則設計
技能要求：
- 必備技能：批次腳本、文件格式轉換
- 進階技能：後處理修復
延伸思考：
- 可用於內部維基或文檔系統的 AI 化
- 風險：轉換造成語意丟失
- 優化：抽樣人工審查與自動測試

Practice Exercise（練習題）
基礎練習：將 10 篇 HTML 轉為 Markdown（30 分鐘）
進階練習：修復圖片與內部引用（2 小時）
專案練習：建立全站轉換管線與驗證（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：轉換覆蓋與正確性
程式碼品質（30%）：腳本穩定度
效能優化（20%）：轉換速度與後處理
創新性（10%）：規則設計與驗證流程


## Case #11: 中文檔名/網址正規化：提升相容性與管線穩定度

### Problem Statement（問題陳述）
業務場景：中文檔名/網址造成多工具相容性問題（路徑、編碼、部署），影響發布與檢索。
技術挑戰：批量將中文檔名/網址轉為英文/ASCII 並維持引用一致性。
影響範圍：影響部署穩定度、向量化與外部工具呼叫。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 路徑與編碼在不同環境表現不一致。
2. 搜索與向量化對非 ASCII 支援不佳。
3. 引用/連結更新量大易出錯。
深層原因：
- 架構層面：未定義命名規範。
- 技術層面：缺少批量改名與引用重寫工具。
- 流程層面：無重定向與對照表維護。

### Solution Design（解決方案設計）
解決策略：建立批次正規化腳本，將中文檔名轉為英文 slug，並重寫引用；同步生成對照表與重定向規則。

實施步驟：
1. 定義命名規範
- 實作細節：小寫、破折號、無空白/特殊字
- 所需資源：規範文檔
- 預估時間：0.5 天

2. 批次改名與引用重寫
- 實作細節：遍歷 repo、更新所有引用
- 所需資源：Node/Python 腳本
- 預估時間：1 天

3. 對照表與重定向
- 實作細節：舊→新映射表，站點重寫規則
- 所需資源：Nginx/Apache/前端路由
- 預估時間：0.5 天

關鍵程式碼/設定：
```python
# Python 檔名 slug 化（概念示例）
import os, re, unicodedata
def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9\-\.]+','-', s).lower()
    return s.strip('-')

for root,_,files in os.walk("content"):
    for f in files:
        if re.search(r'[\u4e00-\u9fff]', f):
            nf = slugify(f)
            os.rename(os.path.join(root,f), os.path.join(root,nf))
```

實際案例：作者在重構中批量將中文檔名/網址改為英文，並生成對照表以便遷移。
實作環境：腳本環境、站點路由。
實測數據：
改善前：部署/檢索/向量化出現不穩定。
改善後：路徑相容性改善，整體管線更穩定。
改善幅度：部署與檢索錯誤明顯下降（定性）。

Learning Points（學習要點）
核心知識點：
- 命名規範與路徑相容性
- 重定向與遷移管理
技能要求：
- 必備技能：字元處理、引用重寫
- 進階技能：站點路由重寫策略
延伸思考：
- 可用於國際化站點遷移
- 風險：改名造成外部引用失效
- 優化：維持舊鏈接映射

Practice Exercise（練習題）
基礎練習：將 100 個中文檔名 slug 化（30 分鐘）
進階練習：重寫 Markdown 中的引用（2 小時）
專案練習：建立完整映射與路由重定向（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：改名覆蓋與引用一致性
程式碼品質（30%）：腳本健壯性與日誌
效能優化（20%）：批次速度與錯誤率
創新性（10%）：遷移策略設計


## Case #12: 圖檔路徑修復與清理：穩定內容引用

### Problem Statement（問題陳述）
業務場景：歷史圖檔路徑雜亂、壞連結多，影響文章呈現與檢索。
技術挑戰：批量修復圖片路徑、移除無用圖檔並維持引用正確。
影響範圍：影響內容完整性與用戶體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不一致的路徑策略與相對/絕對引用混用。
2. 重構後檔案移動造成引用失效。
3. 無圖片清理策略。
深層原因：
- 架構層面：未定義多媒體資產規範。
- 技術層面：缺少掃描/修復工具。
- 流程層面：無發布前資產驗證。

### Solution Design（解決方案設計）
解決策略：建立圖片掃描與修復腳本，統一路徑策略（/images/...），批量更新 Markdown 引用，移除孤兒檔案。

實施步驟：
1. 路徑規範與目錄結構
- 實作細節：定義圖檔集中目錄與引用規則
- 所需資源：規範文檔
- 預估時間：0.5 天

2. 批量掃描與修復
- 實作細節：解析 Markdown，重寫圖片路徑
- 所需資源：Node/Python 腳本
- 預估時間：1 天

3. 孤兒檔清理
- 實作細節：找出未被引用的圖檔並移除
- 所需資源：掃描工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```node
// Node 修復 Markdown 圖片路徑（概念示例）
const fs = require('fs');
const path = require('path');
function fixImageLinks(md) {
  return md.replace(/!\[.*?\]\((.*?)\)/g, (_,p)=> {
    const fname = path.basename(p);
    return `![image](/images/${fname})`;
  });
}
```

實際案例：作者在重構中統一圖檔路徑與清理無用資產，文章呈現與引用更穩定。
實作環境：Node/Python 腳本。
實測數據：
改善前：圖檔常壞、呈現不完整。
改善後：引用一致且穩定，閱讀體驗提升。
改善幅度：壞連結顯著減少（定性）。

Learning Points（學習要點）
核心知識點：
- 多媒體資產管理
- Markdown 引用修復
技能要求：
- 必備技能：文本解析與重寫
- 進階技能：資產清理策略
延伸思考：
- 可用於大型文檔系統清理
- 風險：錯誤重寫造成新壞鏈接
- 優化：加上路徑存在性檢查

Practice Exercise（練習題）
基礎練習：修復 50 篇文章的圖片路徑（30 分鐘）
進階練習：孤兒檔掃描與報表生成（2 小時）
專案練習：建立資產管線與 CI 檢查（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：修復覆蓋與一致性
程式碼品質（30%）：解析準確與健壯性
效能優化（20%）：批次速度與錯誤率
創新性（10%）：資產清理策略


## Case #13: Disqus 連結遷移對照表：評論延續性保障

### Problem Statement（問題陳述）
業務場景：系統移轉造成文章 URL 變更，Disqus 等評論系統需維持對應，避免歷史評論失聯。
技術挑戰：生成舊→新 URL 對照表並批量更新評論對應。
影響範圍：影響社群互動延續性與 SEO。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. URL 變更未同步評論系統。
2. 缺少對照表與批量更新工具。
3. 手動更新量大。
深層原因：
- 架構層面：遷移計畫未覆蓋第三方系統。
- 技術層面：缺少映射表生成與應用程式。
- 流程層面：未建立「遷移前/後」核對清單。

### Solution Design（解決方案設計）
解決策略：匯出歷史 URL，建立舊→新映射表，批量更新 Disqus 對應或設置重定向，確保評論串連續。

實施步驟：
1. URL 收集與映射生成
- 實作細節：掃描舊文章生成映射 JSON/CSV
- 所需資源：腳本
- 預估時間：0.5-1 天

2. 批量更新評論系統
- 實作細節：依 Disqus API/設定進行更新
- 所需資源：API 金鑰/管理介面
- 預估時間：0.5 天

3. 重定向規則
- 實作細節：站點設置 301/RewriteMap
- 所需資源：站點服務配置
- 預估時間：0.5 天

關鍵程式碼/設定：
```csv
# old_to_new_url_map.csv（概念示例）
old_url,new_url
https://old.example.com/2015/11/06/apache-rewritemap-urlmapping-case-study/,https://columns.chicken-house.net/2015/11/06/apache-rewritemap-urlmapping-case-study/
...
```

實際案例：作者在重構中「匯出 Disqus 連結遷移對照表」，保障評論延續。
實作環境：腳本、站點配置。
實測數據：
改善前：評論串失聯風險高。
改善後：評論延續與 SEO 更穩定。
改善幅度：遷移風險顯著降低（定性）。

Learning Points（學習要點）
核心知識點：
- 第三方服務遷移管理
- URL 映射與重定向
技能要求：
- 必備技能：資料匯出、CSV/JSON 處理
- 進階技能：SEO 與站點規則
延伸思考：
- 可用於任何外部系統對應（Analytics/Ads）
- 風險：映射錯誤造成錯重定向
- 優化：加入校驗與抽樣測試

Practice Exercise（練習題）
基礎練習：生成 100 條 URL 對照表（30 分鐘）
進階練習：調用第三方 API 批量更新（2 小時）
專案練習：完整遷移與測試計畫（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：映射覆蓋與更新成功
程式碼品質（30%）：匯出與處理健壯性
效能優化（20%）：批次速度與錯誤率
創新性（10%）：遷移策略與校驗設計


## Case #14: MCP Server（Streamable HTTP）上線與使用說明

### Problem Statement（問題陳述）
業務場景：讓外部 Agent 能即時使用部落格 MCP 服務，需選擇通用傳輸並提供簡明使用指南。
技術挑戰：以 Streamable HTTP 部署 MCP，並讓使用者快速接入與測試。
影響範圍：影響使用者接入門檻與試用體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 傳輸協定選擇影響 MCP Host 支援度。
2. 使用指南不清晰則影響接入率。
3. 初次使用需引導呼叫 GetInstructions。
深層原因：
- 架構層面：服務對外發布策略。
- 技術層面：HTTP Stream 與工具回應渲染。
- 流程層面：新手引導與操作提示。

### Solution Design（解決方案設計）
解決策略：選用 Streamable HTTP 作為對外發布協定，提供簡明使用步驟（VSCode/ChatGPT），並在需要時以命令方式強制執行 GetInstructions。

實施步驟：
1. MCP Server HTTP 啟用
- 實作細節：暴露工具端點與流式回應
- 所需資源：MCP 實作框架
- 預估時間：1 天

2. 使用指南撰寫
- 實作細節：VSCode 安裝步驟、ChatGPT 設定、測試命令
- 所需資源：文檔
- 預估時間：0.5 天

3. 強制指令支持
- 實作細節：/mcp GetInstruction 命令提示
- 所需資源：Host 支援/說明
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
Transport: Streamable HTTP
URL: https://columns-lab.chicken-house.net/api/mcp/  (請保留結尾 /)

VSCode 安裝：F1 -> MCP: Add Server... -> HTTP -> 輸入 URL -> 命名 -> OK
測試：/mcp GetInstruction
```

實際案例：作者已上線 MCP Server，使用者可直接接入並測試，無需登入與 API Key。
實作環境：MCP Server；VSCode；ChatGPT Plus（Beta 支援 MCP）。
實測數據：
改善前：無可用服務，讀者無法體驗。
改善後：零配置體驗，大幅降低接入門檻。
改善幅度：初次接入時間 < 2 分鐘。

Learning Points（學習要點）
核心知識點：
- MCP 發布協定選擇
- 新手引導設計
技能要求：
- 必備技能：HTTP 流式、Host 設定
- 進階技能：工具回應渲染與錯誤提示
延伸思考：
- 可擴展認證與租戶隔離
- 風險：公共開放帶來濫用風險
- 優化：節流、速率限制、日誌審計

Practice Exercise（練習題）
基礎練習：在 VSCode 接入並呼叫 GetInstructions（30 分鐘）
進階練習：自建簡易 MCP HTTP 服務（2 小時）
專案練習：發布含 5 個工具的 MCP Server 並撰寫指南（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：工具可用性與回應正確
程式碼品質（30%）：HTTP 流式與錯誤處理
效能優化（20%）：初次接入效率
創新性（10%）：引導與命令設計


## Case #15: 分層檢索（探索→取段→取全文）：控制 Context Window

### Problem Statement（問題陳述）
業務場景：模型 context window 有上限，若一次塞入過量資料（全文/多文），易造成關鍵訊息淹沒與效果下降。
技術挑戰：在工具層設計「先檢索片段，再按需取全文」的分層流程。
影響範圍：影響生成品質、速度與成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直接塞入全文造成上下文爆量。
2. 片段檢索不精準導致重取多次。
3. 未定義 context 控制策略。
深層原因：
- 架構層面：工具未分層（探索/規劃/執行）。
- 技術層面：缺少 tokens 上限控制與回應裁剪。
- 流程層面：無「先片段→再全文」的標準步驟。

### Solution Design（解決方案設計）
解決策略：引入探索/規劃/執行分層工具（參考 Shopify Dev MCP），以 SearchDocsChunks（探索）→FetchFullDocs（執行）模式，在必要時才讀取全文；工具回應以 Markdown 精簡呈現，避免噪音。

實施步驟：
1. 工具分層設計
- 實作細節：探索（chunks）、取全文（markdown）
- 所需資源：MCP Server
- 預估時間：1 天

2. tokens/limit 策略
- 實作細節：限制返回片段數與全文大小
- 所需資源：工具參數
- 預估時間：0.5 天

3. 回應裁剪與標註
- 實作細節：重點標註、來源引用
- 所需資源：回應模板
- 預估時間：0.5 天

關鍵程式碼/設定：
```pseudo
# 分層檢索流程（概念）
results = SearchChunks(query, synthesis="solution", limit=5)
if need_full_doc:
  docs = FetchFullDocs(paths_from(results), format="markdown", max_tokens=2000)
  use(docs)
```

實際案例：作者在 Shopify/Context7 案例分析中採用分層檢索思想，並在自身 MCP 設計中控制帶入的必要資訊。
實作環境：MCP Server；Agent。
實測數據：
改善前：上下文容易爆量、效率不佳。
改善後：只帶必要資訊進入 context，效果提升。
改善幅度：上下文密度與生成質量顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- Context Engineering 與分層檢索
- tokens/limit 控制
技能要求：
- 必備技能：工具分層與參數策略
- 進階技能：回應裁剪與高亮
延伸思考：
- 可用於任何大型文庫檢索任務
- 風險：過度裁剪丟失必要上下文
- 優化：動態根據回應信心調整擷取

Practice Exercise（練習題）
基礎練習：為工具加入 limit/tokens 控制（30 分鐘）
進階練習：設計分層檢索並量測上下文大小（2 小時）
專案練習：在自有文庫部署分層檢索 MCP（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：分層工具與策略完整
程式碼品質（30%）：回應裁剪與標註清晰
效能優化（20%）：上下文控制成效
創新性（10%）：分層與引導設計


## Case #16: GraphQL 安全生成：Introspection + Validation（參考 Shopify Dev MCP）

### Problem Statement（問題陳述）
業務場景：Agent 生成 GraphQL 查詢/變更時可能使用不存在欄位或版本不符，導致錯誤與幻覺。
技術挑戰：如何在工具層保證生成的 GraphQL 片段合法且符合版本。
影響範圍：影響開發者生產力、API 使用正確性與穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 模型基於舊訓練資料生成過時 API。
2. 無 schema 驗證與版本檢查。
3. 回應未經工具級驗證。
深層原因：
- 架構層面：工具未提供 introspect/validate 能力。
- 技術層面：缺少版本參數與過濾。
- 流程層面：生成後無驗證步驟。

### Solution Design（解決方案設計）
解決策略：提供 introspect_graphql_schema（查詢 schema）與 validate_graphql_codeblocks（驗證代碼片段）兩工具；生成流程為「查 schema→產出→驗證→執行」。

實施步驟：
1. 引入 introspect 工具
- 實作細節：指定 API/版本/查詢範圍
- 所需資源：MCP 工具設計
- 預估時間：1 天

2. 加入 validate 工具
- 實作細節：將生成片段送驗
- 所需資源：驗證器
- 預估時間：1 天

3. 流程落地
- 實作細節：在 Agent 工作流中加入「生成→驗證」步
- 所需資源：Agent 配置
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
// validate_graphql_codeblocks（概念）
{
  "conversationId":"...",
  "api":"admin",
  "version":"2025-01",
  "codeblocks":[
    {
      "language":"graphql",
      "code":"{ products(first:25){ nodes{ title description } } }"
    }
  ]
}
```

實際案例：作者分析 Shopify Dev MCP 設計；以工具級驗證防止幻覺/版本錯誤。
實作環境：MCP Host；GraphQL 服務。
實測數據：
改善前：生成查詢常出現不存在欄位/版本不符。
改善後：驗證通過後再執行，錯誤率顯著下降。
改善幅度：生成正確率提升（定性）。

Learning Points（學習要點）
核心知識點：
- 生成前 introspect 與生成後 validate
- 版本控制
技能要求：
- 必備技能：GraphQL schema/驗證工具
- 進階技能：Agent 生成流程編排
延伸思考：
- 可擴展至 REST/SQL 的 schema 檢查
- 風險：驗證延長延遲
- 優化：快取 schema、局部驗證

Practice Exercise（練習題）
基礎練習：設計一個 validate 工具接口（30 分鐘）
進階練習：將生成-驗證流程接入 Agent（2 小時）
專案練習：為內部 API 建立完整生成保護鏈（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：introspect + validate 覆蓋
程式碼品質（30%）：接口清晰與容錯
效能優化（20%）：快取與延遲控制
創新性（10%）：生成保護流程設計


## Case #17: Context7 模式：Library ID 解析 + 版本化文件拉取避免過時與幻覺

### Problem Statement（問題陳述）
業務場景：LLM 生成依賴舊訓練資料，容易產生過時範例或幻覺 API；需拉取最新且版本匹配的官方文件/範例。
技術挑戰：如何解析「一般名稱」為標準 Library ID，並拉取對應主題與 tokens 限制的文件片段。
影響範圍：影響代碼可執行性與準確性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 模型內建知識過時。
2. 沒有對應到官方與版本特定文件。
3. 拉取內容無 tokens 控制造成上下文爆量。
深層原因：
- 架構層面：工具未提供「解析→拉取」兩段式流程。
- 技術層面：未設計版本/主題/限制參數。
- 流程層面：缺少「先問是什麼→再拉內容」的規範。

### Solution Design（解決方案設計）
解決策略：提供 resolve-library-id（一般名稱→ID）與 get-library-docs（ID→主題文件）兩工具；回應中嵌入使用規則與信任分數，指導 Agent 選擇與拉取。

實施步驟：
1. ID 解析工具
- 實作細節：返回候選庫、信任分數、片段數
- 所需資源：MCP 工具實作
- 預估時間：1 天

2. 文件拉取工具
- 實作細節：支持 topic/tokens 參數控制
- 所需資源：文件索引
- 預估時間：1 天

3. 回應嵌入指引
- 實作細節：在回應中說明使用規則與版本選擇注意
- 所需資源：模板
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
// resolve-library-id 回應（文章提供之概念）
{
  "results":[
    {
      "title":"Shopify Functions",
      "id":"/websites/shopify_dev_api_functions",
      "snippets":643,
      "trustScore":7.5
    }
  ],
  "instructions":"選擇基於名稱匹配、trustScore、snippet 覆蓋的庫；如用戶提供版本才選版本。"
}
```

實際案例：作者解析 Context7 MCP 的兩工具設計，成功拉取主題範例（如 Admin GraphQL 認證+查商品）。
實作環境：Context7 MCP；Agent。
實測數據：
改善前：生成代碼過時或幻覺 API。
改善後：直接拉官方且版本化範例，代碼可執行性大幅提升。
改善幅度：可用性顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- 兩段式解析與拉取
- 版本/主題/tokens 控制
技能要求：
- 必備技能：文件索引與工具設計
- 進階技能：回應嵌入指引
延伸思考：
- 可自建企業內部「Context7 類」文件服務
- 風險：ID 解析誤選
- 優化：加入更多評估指標（更新日期、作者權威）

Practice Exercise（練習題）
基礎練習：為 3 個庫設計 ID 解析工具（30 分鐘）
進階練習：設計 topic/tokens 的拉取工具（2 小時）
專案練習：在自有文檔部署解析+拉取 MCP（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：解析與拉取工具覆蓋
程式碼品質（30%）：回應格式與錯誤處理
效能優化（20%）：tokens 控制與上下文密度
創新性（10%）：指引與評估指標設計


## Case #18: API-first → AI-first 的介面原則落地

### Problem Statement（問題陳述）
業務場景：服務介面面向 AI 使用者（Agent）而非人類開發者；需避免 UI 導向與檯面下溝通，並做到合情合理且可靠。
技術挑戰：如何落地 AI-first 介面原則進 MCP 設計，使 AI 能「看得懂、用得對」。
影響範圍：影響 Agent 使用成效與安全性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 介面過度受 UI 影響。
2. 隱性約定未顯式化，AI 難理解。
3. 邊界未收斂，錯誤與濫用風險高。
深層原因：
- 架構層面：未對應領域問題而是 UI 行為。
- 技術層面：未顯式規範常理與可靠性。
- 流程層面：缺少防濫用設計。

### Solution Design（解決方案設計）
解決策略：以領域問題為核心設計 MCP 工具；在回應中顯式表達常理與邊界；引入錯誤防護與必要的 gating；避免 UI 導向的端點。

實施步驟：
1. 梳理領域問題與常理
- 實作細節：以「合情合理」設計規範
- 所需資源：領域專家/文章
- 預估時間：1 天

2. 鞏固邊界與錯誤策略
- 實作細節：工具錯誤返回與限制
- 所需資源：伺服器端保護邏輯
- 預估時間：0.5 天

3. 去 UI 化工具設計
- 實作細節：以 domain service 角度提供工具
- 所需資源：規格設計
- 預估時間：1 天

關鍵程式碼/設定：
```markdown
# 工具回應嵌入常理/邊界（概念示例）
- 此工具僅處理「文章片段檢索」，不提供 UI 行為模擬。
- 請以「領域術語」下查詢，並指定 synthesis 型態。
- 超過 limit 將被截斷；請根據回應建議進行下一步。
```

實際案例：作者引用 2024/07/20 與 2024/01/15 文章的原則，落地於 MCP 工具設計。
實作環境：MCP 設計與回應模板。
實測數據：
改善前：AI 誤解介面或濫用端點。
改善後：回應清晰、邊界明確，誤用顯著下降。
改善幅度：可靠性提升（定性）。

Learning Points（學習要點）
核心知識點：
- AI-first 介面原則
- 合情合理與可靠性
技能要求：
- 必備技能：領域建模、錯誤策略
- 進階技能：指令嵌入與防濫用
延伸思考：
- 可用於任何面向 Agent 的服務
- 風險：過度限制降低靈活度
- 優化：針對場景動態放寬策略

Practice Exercise（練習題）
基礎練習：將一個 UI 導向端點改為領域工具（30 分鐘）
進階練習：設計 3 條常理與邊界規則（2 小時）
專案練習：為一組工具制訂 AI-first 規範與模板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：領域工具覆蓋問題
程式碼品質（30%）：錯誤與邊界一致性
效能優化（20%）：誤用下降成效
創新性（10%）：規範與模板設計


## 案例分類

1. 按難度分類
- 入門級（適合初學者）：Case 10, 11, 12, 14
- 中級（需要一定基礎）：Case 4, 5, 6, 8, 15, 16, 17, 18
- 高級（需要深厚經驗）：Case 1, 2, 3, 7, 9

2. 按技術領域分類
- 架構設計類：Case 1, 2, 5, 15, 16, 17, 18
- 效能優化類：Case 15, 7, 10, 9
- 整合開發類：Case 5, 6, 7, 8, 14
- 除錯診斷類：Case 12, 13, 16
- 安全防護類：Case 2, 16, 18

3. 按學習目標分類
- 概念理解型：Case 1, 15, 18
- 技能練習型：Case 10, 11, 12, 14
- 問題解決型：Case 4, 5, 6, 7, 8, 9, 13, 16, 17
- 創新應用型：Case 2, 3, 15, 17


## 案例關聯圖（學習路徑建議）

- 建議先學的案例：
  - Case 1（MCP-first：工具不是 API）：建立整體觀念
  - Case 18（API-first → AI-first 原則）：釐清介面設計準則
  - Case 15（分層檢索/Context Engineering）：掌握上下文控制核心

- 依賴關係：
  - Case 2（GetInstructions/Gating）依賴 Case 1 的工具觀念
  - Case 3（內容正規化）依賴 Case 1/15 的設計思想
  - Case 4（查詢設計）依賴 Case 3 的 synthesis 型態
  - Case 5（解題工作流）依賴 Case 1/4 的工具與查詢設計
  - Case 6/7/8（實作/應用）依賴 Case 5 的工作流
  - Case 9/10/11/12/13（重構與資料清理）支撐 Case 3 的內容正規化與後續檢索
  - Case 16（GraphQL 安全生成）與 Case 17（Context7 模式）為 Case 1/15 的外部設計延伸

- 完整學習路徑建議：
  1) 觀念建立：Case 1 → Case 18 → Case 15
  2) 工具與內容：Case 2 → Case 3 → Case 4 → Case 5
  3) 實作應用：Case 6 → Case 7 → Case 8
  4) 工程基礎：Case 9 → Case 10 → Case 11 → Case 12 → Case 13
  5) 外部最佳實務：Case 16 → Case 17
  6) 綜合回顧：回到 Case 1/15，審視自己 MCP 的分層與上下文策略，進行優化

如需我把以上任一案例展開為可執行的範例專案或提供更多程式碼細節，請告訴我欲優先練習的案例編號。