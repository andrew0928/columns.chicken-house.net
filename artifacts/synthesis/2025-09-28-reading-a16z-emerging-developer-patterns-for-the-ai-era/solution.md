以下內容基於你提供的文章與 FB 貼文彙整，萃取並結構化 18 個具教學價值的問題解決案例。每個案例都對應文章中的難題、根因、解法與效益敘述，並補上示範實作片段與練習建議，便於用於實戰教學、專題練習與能力評估。

## Case #1: AI-native Git 的「意圖可追溯」提交流程

### Problem Statement（問題陳述）
- 業務場景：AI coding 比重上升，團隊需要從運行中的 artifacts 回溯到「當時的需求與意圖」，並重建變更脈絡以便審核、追責與合規。單看程式碼 diff 已不足以理解變更真意，導致 code review 效率低下與風險升高。
- 技術挑戰：傳統 Git 只追蹤檔案行為級別的差異，缺乏對 prompt、tests、所用模型/agent 等上下文的原生支援，難以滿足 AI 開發的溯源與再現性。
- 影響範圍：工程生產力、審計合規、回歸修復、知識沉澱、AI-生成代碼品質保證。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Git 設計初衷針對人手撰寫的 source code，而非 AI 生成的 artifacts。
  2. 提交訊息缺乏結構化的 prompt/test/agent 來源紀錄，審查者看不到意圖。
  3. CI 僅驗證編譯與測試，未串接「意圖—生成—驗證」的閉環。
- 深層原因：
  - 架構層面：版本控制對象仍鎖定 code，未將需求文件與 prompt 納入「第一級公民」。
  - 技術層面：缺少提交前/後 hook 管線擴充，不能自動關聯 prompt、tests 與 artifacts。
  - 流程層面：開發規範未要求保留生成意圖與測試連結，review 缺失語義依據。

### Solution Design（解決方案設計）
- 解決策略：在 Git 工作流加入「gen-commit」層，將 prompt、tests、agent/模型、驗證結果「包裝成束」綁定到提交，並在 CI 內執行生成+測試校驗，實現「意圖—生成—驗證—產出」的可追溯閉環。

- 實施步驟：
  1. 提交增強（Git 層）
     - 實作細節：新增 git 子指令 gen-commit，記錄 prompt/tests、agent、bundle id，並觸發生成與測試。
     - 所需資源：Node/Python CLI、Git hooks、LLM API（如 Claude/OpenAI）、測試框架。
     - 預估時間：2-3 天 PoC，1-2 週導入團隊規範。
  2. CI 整合（Pipeline 層）
     - 實作細節：CI 拉取提交綁定的 bundle，重放生成、執行 tests、上傳 artifacts 與審核報告。
     - 所需資源：GitHub Actions/Azure DevOps、Artifact Registry。
     - 預估時間：3-5 天。

- 關鍵程式碼/設定：
```bash
# 假想 CLI：git gen-commit
git gen-commit \
  --prompt "Add a billing feature to my app" \
  --tests "billing.spec.ts" \
  --agent "claude-3-7-sonnet-latest"

# Hook: .git/hooks/prepare-commit-msg -> 將 metadata 注入 commit message
# commit-msg 片段（YAML front-matter）
---
agent: claude-3-7-sonnet-latest
bundle: bndl_f92e8
prompt_file: .ai/prompts/billing.md
tests:
  - tests/billing.spec.ts
validate: passed
human_review_required:
  - src/billing.ts
---
```

- 實際案例：文中引用 A16Z 模擬命令列，展示 gen-commit 將 prompt/tests/agent/validate 綁定提交並要求特定檔案 human review。
- 實作環境：Git、VSCode/Cursor、LLM API、CI（GitHub Actions/Azure DevOps）。
- 實測數據：
  - 改善前：review 只見 code diff，需手動詢問脈絡。
  - 改善後：提交即含意圖、測試、驗證結果，審查一次到位。
  - 改善幅度：以「意圖可追溯率」「一次通過率」為指標（文中未給數字，建議團隊追蹤）。

Learning Points（學習要點）
- 核心知識點：
  - AI-native 版控要素（prompt/tests/agent/artifact 綁定）
  - 提交前/後 hook 擴充與 CI 校驗閉環
  - 生成與測試的可重放性
- 技能要求：
  - 必備技能：Git、CI、測試框架、LLM API 調用
  - 進階技能：提交語義標準化、審計/合規設計
- 延伸思考：
  - 如何將「生成意圖」納入合規與事後稽核？
  - 多模型/多 agent 生成如何歸檔與比較？
  - 和包管理/Artifact Registry 的雙向追溯如何實現？

Practice Exercise（練習題）
- 基礎練習：為現有專案加上 gen-commit 腳本，將 prompt/tests 寫入 commit metadata（30 分鐘）。
- 進階練習：在 CI 中重放生成與測試，產生審核報告（2 小時）。
- 專案練習：將整個 repo 的提交歷史建立「意圖索引」，可從 artifact 反查到 prompt（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：提交綁定 prompt/tests/agent；CI 能重放與驗證
- 程式碼品質（30%）：腳本結構化、錯誤處理、可維護性
- 效能優化（20%）：生成/測試時間、CI 併發能力
- 創新性（10%）：提交語義可視化、審計報表呈現


## Case #2: 需求文件與 Prompt 的「語義 Diff」與變更解釋

### Problem Statement（問題陳述）
- 業務場景：需求文件與 prompt 成為「真正的 source」，但傳統行為式 diff 無法告訴審查者「語義上改了什麼要求」。
- 技術挑戰：line-based diff 無法反映語義新增/刪減/重寫；審查者閱讀成本高、誤解多。
- 影響範圍：需求審核、變更控制、交付品質、合規留痕。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 文字差異≠語義差異，尤其在長文件。
  2. 缺少自動化語義摘要流程。
  3. Diff 結果未與任務/測試關聯。
- 深層原因：
  - 架構層面：Repo 缺少「文件/Prompt」的一級資產化管理。
  - 技術層面：沒有 LLM 參與的語義比對與總結。
  - 流程層面：審查清單未納入「語義變更摘要」。

### Solution Design（解決方案設計）
- 解決策略：實作 git semdiff（或 PR Bot），先做文本 diff，再交由 LLM 產出「語義摘要與影響面清單」，綁入 PR/Commit 供審查使用。

- 實施步驟：
  1. 文本差異擷取
     - 實作細節：取舊/新文件，做最小差異切片（chunks）。
     - 所需資源：Diff 庫、Repo 讀取權限。
     - 預估時間：0.5 天。
  2. LLM 語義總結
     - 實作細節：將差異片段與上下文送入 LLM，產出「新增/刪除/修改需求點」「受影響測試」。
     - 所需資源：LLM API、PR Bot。
     - 預估時間：1-2 天。

- 關鍵程式碼/設定：
```python
# semdiff.py（簡化示例）
old, new = load_docs("docs/req_v1.md", "docs/req_v2.md")
diff_chunks = compute_text_diff(old, new)
summary = llm.summarize_diff(
  system="你是需求變更審查助手，輸出新增/刪除/修改點與風險。",
  user={"diff": diff_chunks, "context": load_related_tests()}
)
post_to_pr(summary)
```

- 實際案例：文中提出「以 RAG 式找出實際差異，再用 LLM 彙整語義差異」的構想。
- 實作環境：Git、Python/Node、LLM API、PR Bot（GitHub/Azure DevOps）。
- 實測數據：
  - 改善前：審查者逐行閱讀，耗時且易漏。
  - 改善後：有語義摘要與影響面清單，審查決策更快。
  - 改善幅度：建議追蹤「PR 審查用時」「遺漏需求缺陷率」（文中未提供數字）。

Learning Points
- 核心知識點：語義 diff、LLM 摘要、PR Bot 整合。
- 技能要求：LLM 提示設計、PR 自動化、文本切片。
- 延伸思考：如何將「語義 diff」與測試選擇性重跑（test selection）結合？

Practice Exercise
- 基礎：對兩版需求文件產出語義變更摘要（30 分鐘）。
- 進階：把語義 diff 自動貼到 PR 描述（2 小時）。
- 專案：語義 diff → 影響測試自動標記與重跑（8 小時）。

Assessment Criteria
- 功能完整性：正確擷取差異、摘要合理
- 程式碼品質：模組化、錯誤處理
- 效能：長文處理、token 控制
- 創新性：結合測試選擇、風險分級


## Case #3: 以「可擴縮沙箱」落地 Server-side Coding Agent

### Problem Statement（問題陳述）
- 業務場景：IDE+AI（pair programming）無法規模化；需要在 server 端以 agent 大量並行處理任務（issue→PR），減少人互動時間。
- 技術挑戰：agent 需要工作目錄、工具鏈、可部署/測試的基礎設施；代碼過度依賴真實資源（DB/Redis）。
- 影響範圍：交付節奏、成本、穩定性、資安。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 缺少標準化的「agent 工作空間」。
  2. 測試/部署依賴真實外部資源，難以自動化。
  3. 工具鏈不一致，重建環境成本高。
- 深層原因：
  - 架構層面：未採用可替換的 infra mocking/契約測試。
  - 技術層面：缺少容器化與 IaC。
  - 流程層面：任務編排與資源分配未自動化。

### Solution Design
- 解決策略：以容器化沙箱提供標準工作空間，內建工具鏈、mock/service-virtualization、可執行 build/test/deploy 的最小閉環，透過隊列觸發 agent。

- 實施步驟：
  1. 沙箱定義
     - 實作細節：DevContainer/Dockerfile 預裝 SDK、測試框架、CLI，注入 mock 設定。
     - 所需資源：Docker、Dev Containers、Test doubles。
     - 預估時間：3-5 天。
  2. 任務執行器
     - 實作細節：Webhook→Queue→Runner（拉取 repo→生成→測試→PR）。
     - 所需資源：消息隊列、Runner 集群、LLM API。
     - 預估時間：1-2 週。

- 關鍵程式碼/設定：
```Dockerfile
FROM node:20
RUN apt-get update && apt-get install -y git
WORKDIR /workspace
COPY package*.json ./
RUN npm ci
# 預裝測試、lint、mocks
RUN npm i -D vitest @types/node nock
```

- 實際案例：文中點名 server-side agent 的四要件（workspace、修改、build、部署/測試）。
- 實作環境：Docker/K8s、消息隊列、Azure DevOps/GitHub、LLM Agent。
- 実測數據：
  - 改善前：依賴人機互動、無法並行。
  - 改善後：任務可在沙箱並行處理；人僅負責驗收。
  - 改善幅度：建議追蹤「issue→PR 平均時間」「併發度」「人機互動次數」（文中未給數字）。

Learning Points
- 核心知識點：可重現工作空間、mock/virtualization、任務隊列。
- 技能要求：容器化、CI/CD、契約測試。
- 延伸思考：如何在沙箱中安全處理 secrets（見 Case 16）？

Practice/Assessment 略（同格式）。


## Case #4: Generative UI「動態儀表板」工具化

### Problem Statement
- 業務場景：傳統儀表板資訊龐雜，使用者需自行篩選；希望 AI 依用戶意圖動態組合與呈現。
- 技術挑戰：缺乏可被 AI 調用的 widget 工具模型；畫面語義/狀態無法進入 LLM 的決策流程。
- 影響範圍：決策效率、可用性、學習成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. UI 元件未工具化（無 function calling 規格）。
  2. 無標準輸出（markdown/mermaid）協助說明與視覺化。
  3. 沒有資料查詢工具（log、error、deploy）供 AI 使用。
- 深層原因：
  - 架構層面：缺少「Agent-ready UI 層」。
  - 技術層面：工具 schema 未定義、無狀態同步。
  - 流程層面：仍以「事前設計」而非「意圖驅動」。

### Solution Design
- 解決策略：將常用 widget 定義為 tool（可參數化），提供資料查詢工具，AI 決策後以 markdown + mermaid 輸出/或直接 tool 調用更新畫面。

- 實施步驟：
  1. 工具模型化
     - 細節：以 JSON schema 定義 widget 工具與可調參數。
     - 資源：前端框架、LLM function calling。
     - 時間：3-5 天。
  2. 查詢工具化
     - 細節：log.query / error.search / deploy.history 作為工具。
     - 資源：觀測平台 API、工具封裝。
     - 時間：3-5 天。

- 關鍵程式碼/設定：
```json
{
  "tools": [
    {
      "name": "widget.lineChart",
      "description": "呈現趨勢折線圖",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "series": {"type": "array", "items": {"type": "number"}}
        },
        "required": ["title", "series"]
      }
    }
  ]
}
```

- 實際案例：文中三圖（傳統/動態/Agent-ready）與以 markdown+mermaid 產生圖表的經驗。
- 實作環境：前端框架（React/Vue）、LLM（function calling）、觀測 API。
- 實測數據：建議追蹤「任務完成時間」「點擊深度」「轉化率」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #5: MVC + LLM 的「控制器共駕」與使用者行為通報

### Problem Statement
- 業務場景：僅用聊天無法掌握用戶上下文；需要在正常 UI 操作與對話並存時，AI 能理解當下意圖並主動協助。
- 技術挑戰：Controller 未對 AI 回報操作事件；AI 無從感知狀態，難以做對的建議/動作。
- 影響範圍：體驗品質、任務完成率、導購/防呆。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無行為遙測至 LLM。
  2. 缺少 function calling 對控制器的操作通道。
  3. 無系統化的上下文（history/instruction/personalization）。
- 深層原因：
  - 架構層面：MVC 未擴展 AI 共駕接口。
  - 技術層面：事件語義缺失、調用未授權。
  - 流程層面：未定義 AI 介入時機與規則。

### Solution Design
- 解決策略：Controller 對 LLM 連續通報「user_action」事件；LLM 以 function calling 指揮 Controller 啟用 UI 模組/提示，用系統提示約束介入規則。

- 實施步驟：
  1. 事件上報
     - 細節：定義事件 schema，如「加入 購物車 可樂 x5」。
     - 資源：遙測 SDK、LLM API。
     - 時間：2-3 天。
  2. 控制回調
     - 細節：暴露受控函數（如 show_modal, apply_coupon），驗證授權。
     - 資源：前端/後端 function registry。
     - 時間：3-5 天。

- 關鍵程式碼/設定：
```typescript
// Controller -> LLM: user action telemetry
await llm.chat({
  system: sysPrompt,
  messages: [{role: "user", content: "使用者在購物車中 [加入][可樂] x 5"}],
  tools: [showModalTool, applyCouponTool]
});

// LLM -> Controller: function call 回調
function showModal({title, body}) { ui.showModal(title, body); }
```

- 實際案例：作者在「安德魯小舖」實作此架構，在 DevOpsDays 2024 分享。
- 實作環境：前端（React/Vue）、Node/Go 後端、LLM function calling。
- 實測數據：建議追蹤「AI 介入成功率」「提示被採納率」「錯誤操作減少率」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #6: 用 LLM 直接推論 UX 滿意度（1~10）並留存原因

### Problem Statement
- 業務場景：AI 驅動 UI 流程動態，傳統固定追蹤點對 UX 評估失真；需要在交易關鍵時刻即時判定滿意度並記因。
- 技術挑戰：如何可靠地取得情境+決策軌跡，並讓 LLM 以一致準則評分。
- 影響範圍：體驗度量、AB/改版迭代、問題定位。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 固定 tracking 對動態流程覆蓋不足。
  2. 無「當下語境」可供評估。
  3. 評分標準不一致。
- 深層原因：
  - 架構層面：缺少事件/上下文歸檔。
  - 技術層面：未將評分工具化、無 schema。
  - 流程層面：未定義評分時機/準則。

### Solution Design
- 解決策略：在「訂單成立」等關鍵節點調用 LLM，輸入上下文（對話、行為、錯誤），要求依統一規則標註滿意度1-10與原因，工具化寫入數據湖。

- 實施步驟：
  1. 評分規則化
     - 細節：在 system prompt 定義各分數層級準則。
     - 資源：LLM、事件存儲。
     - 時間：1 天。
  2. 工具寫入
     - 細節：定義 record_satisfaction 工具，保存 score/reason。
     - 資源：MCP/內部 API。
     - 時間：1-2 天。

- 關鍵程式碼/設定：
```json
{
  "tools": [{
    "name": "record_satisfaction",
    "description": "保存交易滿意度",
    "parameters": {
      "type": "object",
      "properties": {
        "orderId": {"type":"string"},
        "score": {"type":"integer","minimum":1,"maximum":10},
        "reason": {"type":"string"}
      },
      "required": ["orderId","score"]
    }
  }]
}
```

- 實際案例：作者於「安德魯小舖」實作，讓 LLM 依定義標註分數與文字並落庫。
- 實作環境：LLM、事件資料、後端存儲/MCP。
- 實測數據：建議對照傳統追蹤指標，關聯滿意度波動與缺陷熱點（文中無數字）。

Learning/Practice/Assessment 略。


## Case #7: Document as Code：以 repo 為 AI/人共用的單一事實源

### Problem Statement
- 業務場景：AI 與人需共享需求/spec/rules；聊天複製貼上冗餘且易失真；需要低成本、可版控、可重用的文件工作流。
- 技術挑戰：將 instructions、需求、設計、任務、結果一致收斂，並納入開發/生成閉環。
- 影響範圍：知識再用、交付一致性、可維護性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 指示分散在聊天歷史，無法重用。
  2. 文檔與代碼不同步。
  3. AI 缺少穩定的上下文入口。
- 深層原因：
  - 架構層面：沒有將文檔視為「第一級產出物」。
  - 技術層面：缺少 repo 結構/規約與發布管線。
  - 流程層面：未定義「先文檔後生成」的步驟。

### Solution Design
- 解決策略：將 instructions.md、/docs 需求、/src 代碼、/tests 測試統一版控；以 CI 發布靜態站；AI 以 repo 為虛擬 context 入口。

- 實施步驟：
  1. 結構化現有知識
     - 細節：建立 /docs、/src、/.github/instructions.md。
     - 資源：Git、靜態站工具。
     - 時間：1-2 天。
  2. IDE 整合
     - 細節：啟用 AI IDE（Copilot/Cursor）索引 repo；允許 @ 檔案。
     - 資源：IDE 插件。
     - 時間：0.5 天。

- 關鍵程式碼/設定：
```text
repo/
  .github/instructions.md
  docs/requirements.md
  docs/design.md
  src/...
  tests/...
```

- 實際案例：文中從「Prompt → Document」的演進，instructions.md 成為常態。
- 實作環境：Git、CI、AI IDE。
- 實測數據：建議追蹤「AI 回答規範一致率」「文件覆蓋率」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #8: Context Engineering：以文件作「虛擬記憶體」

### Problem Statement
- 業務場景：LLM 視窗有限，長任務需在不同階段動態裝載/釋放資訊；需要可持久化的上下文載體（todo/dev-notes）。
- 技術挑戰：何時寫回文件、何時載入上下文、如何讓 AI 自主維護長期記憶。
- 影響範圍：長任務穩定性、可重入性、協作效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 上下文丟失導致重複詢問與偏離。
  2. 指令與進度無持久化。
  3. 工具未與文件打通。
- 深層原因：
  - 架構層面：缺少「文件即記憶」的設計。
  - 技術層面：未使用 MCP/FS 讀寫。
  - 流程層面：未定義「階段性落稿/載入」規則。

### Solution Design
- 解決策略：建立 tasks_md（todo list）、dev-notes（開發日誌），以 instructions 規定關鍵節點自動寫入，透過 MCP/FS 動態讀寫。

- 實施步驟：
  1. 文件/規則建立
     - 細節：定義「告一段落/重大變更」時寫入 dev-notes。
     - 資源：IDE 指令模板。
     - 時間：0.5 天。
  2. 工具化
     - 細節：MCP filesystem server/內部 FS API 讀寫。
     - 資源：MCP/FS。
     - 時間：1-2 天。

- 關鍵程式碼/設定：
```markdown
# instructions.md（片段）
當我完成一個階段或有重大變更，請將時間與摘要寫入 docs/dev-notes/README.md。
```

- 實際案例：同事專案（taiwan-holiday-mcp）以 dev-notes 自動沉澱過程筆記。
- 實作環境：Cursor/VSCode、MCP FS、LLM。
- 實測數據：建議追蹤「重啟任務所需時間」「上下文遺失次數」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #9: 以 TDD 導引 Vibe Coding，降低走偏

### Problem Statement
- 業務場景：vibe coding 容易「一次寫太多」與偏題；需要可分段驗收的節拍與守門機制。
- 技術挑戰：如何讓 AI 先產出介面、再產測試、最後補實作，並以測試紅→綠收斂？
- 影響範圍：品質、速度、review 成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺乏分段目標與可執行檢查點。
  2. 審查一次面對大包變更。
  3. 工具缺少自動 gate。
- 深層原因：
  - 架構層面：未定義 TDD 產物在 repo 中的位置。
  - 技術層面：測試框架/腳本未集成。
  - 流程層面：沒有標準節拍（接口→測試→實作）。

### Solution Design
- 解決策略：強制三步—生成 interface、生成測試（紅）、實作補齊（變綠），每步以 CI gate 驗收，避免大步快跑。

- 實施步驟：
  1. 節拍化腳本
     - 細節：提供 ai-gen interface、ai-gen test、ai-impl 三命令。
     - 資源：CLI、測試框架。
     - 時間：1-2 天。
  2. CI Gate
     - 細節：禁止跳步、測試紅不允許 merge。
     - 資源：CI 配置。
     - 時間：0.5 天。

- 關鍵程式碼/設定：
```ts
// example.spec.ts（AI 先產紅測試）
import {sum} from './lib';
test('sum works', () => { expect(sum(1,2)).toBe(3); });
```

- 實際案例：文中提出 TDD 導引 vibe coding 的具體節奏。
- 實作環境：Node/pytest 等測試框架、CI、AI IDE。
- 實測數據：建議追蹤「PR 迭代次數」「一次通過率」「測試覆蓋率」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #10: 以 SDK 封裝複雜基礎設施，減少生成代碼量

### Problem Statement
- 業務場景：啟新專案需申請多個雲資源且命名/規則複雜；AI 生成代碼量大、易錯。
- 技術挑戰：如何用 SDK 封裝 infra 複雜性，使 AI 只需填 config 即可正確部署？
- 影響範圍：可維護性、成本、上線速度。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 直接暴露細節導致樣板與重複。
  2. 命名規則/安全策略分散。
  3. 生成代碼膨脹、難 review。
- 深層原因：
  - 架構層面：缺乏「平台式 SDK」。
  - 技術層面：未建立標準 config → 生成/部署流程。
  - 流程層面：沒有 SDK 的維護責任歸屬。

### Solution Design
- 解決策略：設計平台 SDK + 低維度 config，把規範「寫進 SDK」，AI 只需生成薄層代碼與配置。

- 實施步驟：
  1. SDK 設計
     - 細節：封裝資源命名、連線、觀測、授權；導出簡單 API。
     - 資源：語言 SDK、雲 API。
     - 時間：2-3 週（平台工程）。
  2. 指南整合
     - 細節：在 instructions.md 告知 AI 優先使用 SDK。
     - 資源：文檔/規範。
     - 時間：0.5 天。

- 關鍵程式碼/設定：
```ts
// app.ts
import {Platform} from '@org/platform-sdk';
const db = Platform.db('orders'); // 命名/連線策略均封裝
```

- 實際案例：作者分享自製 template/SDK 的經驗與反思（template 可被替代，SDK 長期有效）。
- 實作環境：語言 SDK、雲供應商、CI/CD。
- 實測數據：建議追蹤「生成代碼行數」「部署成功率」「MTTR」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #11: 用無障礙語義（ARIA）提升 Agent 的 UI 自動化可靠度

### Problem Statement
- 業務場景：使用 Playwright MCP 時，AI 常「看得見按鈕卻點不到」；自動化脆弱、重試多。
- 技術挑戰：Playwright 會將 HTML 壓縮為 YAML 並依無障礙語義重建；若頁面語義不全，AI 定位困難。
- 影響範圍：端對端測試、RPA、Agent UI 操作成功率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 缺 ARIA 屬性/語義標註。
  2. 受壓縮的 YAML 丟失關鍵結構。
  3. 測試選擇器不穩定。
- 深層原因：
  - 架構層面：UI 未以「Agent 可理解」為目標設計。
  - 技術層面：未遵循 a11y 最佳實踐。
  - 流程層面：未在測試門檻納入 a11y。

### Solution Design
- 解決策略：為關鍵交互元素加上語義正確的 role、aria-label、name 屬性；以角色/名稱為主選擇器。

- 實施步驟：
  1. 標註補強
     - 細節：登入/提交/主要導航皆加 role/name/label。
     - 資源：a11y lint、設計指引。
     - 時間：0.5-1 天。
  2. 測試修正
     - 細節：以 getByRole/getByLabelText 等取代脆弱選擇器。
     - 資源：Playwright。
     - 時間：0.5 天。

- 關鍵程式碼/設定：
```html
<button role="button" aria-label="登入">登入</button>
<!-- Playwright -->
await page.getByRole('button', { name: '登入' }).click();
```

- 實際案例：文中指出 Playwright MCP 依 a11y 重建結構；補 a11y 後 AI 可精準操作。
- 實作環境：前端、Playwright MCP、a11y 檢測工具。
- 實測數據：建議追蹤「自動化一次成功率」「重試次數」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #12: 取得 OS 無障礙權限，讓 Agent 操作桌面應用

### Problem Statement
- 業務場景：Agent 需操作非瀏覽器桌面程式（Computer Use）；若無 OS a11y 權限，無法讀取可存取樹/觸發行為。
- 技術挑戰：不同 OS 權限模型差異；需安全到位、可審計。
- 影響範圍：桌面自動化、RPA、內部工具整合。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 未申請 OS a11y 權限（macOS、Windows UIA）。
  2. 權限聲明/提示不足。
  3. 缺乏審計/最小許可。
- 深層原因：
  - 架構層面：桌面代理缺最小權限設計。
  - 技術層面：未熟悉 OS a11y API。
  - 流程層面：未設立審批與日誌保存。

### Solution Design
- 解決策略：在桌面 agent 進程加入 a11y 權限宣告與申請流程，周邊配套審計與最小化授權。

- 實施步驟：
  1. 權限宣告
     - 細節：macOS entitlements、Windows UIA 設定。
     - 資源：OS 文檔、簽章。
     - 時間：1-2 天。
  2. 安全日誌
     - 細節：操作軌跡記錄、敏感操作審批。
     - 資源：日誌/審計平台。
     - 時間：1-2 天。

- 關鍵程式碼/設定：
```xml
<!-- macOS Entitlements (示意) -->
<key>com.apple.security.automation.apple-events</key><true/>
<key>com.apple.security.accessibility</key><true/>
```

- 實際案例：文中指出未取得 a11y API 導致 agent 無法有效理解 UI 狀態。
- 實作環境：桌面 OS、簽章、審計系統。
- 實測數據：建議追蹤「桌面步驟成功率」「權限申請通過率」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #13: 非同步 Agent 工作流：Issue → 自動 PR → 人工驗收

### Problem Statement
- 業務場景：需要把開發任務「外包給 agent」在背景運行，降低人力同步互動成本。
- 技術挑戰：將任務輸入（prompt/spec）結構化；觸發 agent；沙箱生成測試；提交 PR 並更新 issue 狀態。
- 影響範圍：吞吐量、交付節奏、成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 現有工具偏向互動 IDE。
  2. 缺 webhook/runner 串接。
  3. 缺標準任務模板。
- 深層原因：
  - 架構層面：協作平台與 agent 未整合。
  - 技術層面：沙箱與 pipeline 缺少連接。
  - 流程層面：缺少異步驗收節奏。

### Solution Design
- 解決策略：在 Azure DevOps/GitHub 上以「建立 task/issue」觸發 webhook→agent-runner，在沙箱生成/測試/PR，標準化 15~30 分鐘的任務週期，次日人工審核合併。

- 實施步驟：
  1. 任務模板
     - 細節：issue 內含需求/prompt/測試需求。
     - 資源：Issue 模板。
     - 時間：0.5 天。
  2. Runner
     - 細節：webhook→queue→沙箱工作→PR→更新 issue。
     - 資源：Actions/DevOps、Runner、LLM。
     - 時間：3-5 天。

- 關鍵程式碼/設定：
```yaml
# GitHub Actions: on issue labeled "agent"
on:
  issues:
    types: [labeled]
jobs:
  run-agent:
    if: github.event.label.name == 'agent'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: node scripts/run-agent.js "$ISSUE_URL"
```

- 實際案例：文中二位講者示範 Azure DevOps：task → agent → 15~30 分 → PR。
- 實作環境：Azure DevOps/GitHub、Runner、LLM、沙箱。
- 實測數據：
  - 改善前：人機同步互動耗時，難並行。
  - 改善後：多 issue 並行執行，次日批量驗收。
  - 改善幅度：以「任務週期（15~30 分）」「每日處理量」為指標（文中與案例敘述）。

Learning/Practice/Assessment 略。


## Case #14: 多 Agent 併發與自動擴縮

### Problem Statement
- 業務場景：同時存在大量 issue；需要自動擴縮 agent 執行資源以達到吞吐量目標。
- 技術挑戰：排程/佇列、runner 池、資源與成本控制、任務隔離。
- 影響範圍：交付吞吐、雲成本、穩定性。
- 複雜度評級：中-高

### Root Cause Analysis
- 直接原因：
  1. 單節點 runner 容量有限。
  2. 無任務佇列與背壓機制。
  3. 缺失任務隔離（彼此干擾）。
- 深層原因：
  - 架構層面：未採用雲原生擴縮策略。
  - 技術層面：缺少 HPA/工作隊列。
  - 流程層面：無 SLO 與排程策略。

### Solution Design
- 解決策略：使用佇列（如 SQS/RabbitMQ）+ K8s runner（HPA），每個任務一個暫態工作空間，按隊列深度擴縮，完結即銷毀。

- 實施步驟：
  1. 佇列化
     - 細節：issue→queue→runner 取工單。
     - 資源：消息佇列。
     - 時間：1-2 天。
  2. 擴縮
     - 細節：K8s 部署 runner，HPA 依 CPU/隊列深度擴縮。
     - 資源：K8s、HPA。
     - 時間：3-5 天。

- 關鍵程式碼/設定：
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 50
  metrics:
  - type: Pods
    pods:
      metric:
        name: queue_depth
      target:
        type: AverageValue
        averageValue: "5"
```

- 實際案例：文章建議走「非同步+可擴縮」之路，對應多 agent 並行。
- 實作環境：K8s、Queue、Runner、LLM。
- 實測數據：建議追蹤「併發度」「平均等待時間」「成本/任務」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #15: MCP-first 設計：讓 Agent 用你的服務像用工具

### Problem Statement
- 業務場景：服務只提供 REST API，agent 使用成本高、語義不明；需要讓 agent 即插即用。
- 技術挑戰：如何用 MCP 暴露工具、資料源、索引、並最小化 token 成本與誤用風險。
- 影響範圍：整合深度、生態覆蓋、轉化率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. API 規格對「人」友好，不等於對「agent」友好。
  2. 缺少上下文導向的操作。
  3. 認證/授權粒度過粗。
- 深層原因：
  - 架構層面：未 MCP 化（工具/資源/事件）。
  - 技術層面：缺 OAuth/OIDC 與最小權限。
  - 流程層面：未定義 agent 使用規約。

### Solution Design
- 解決策略：實作 MCP server，聚焦高價值操作（工具）、資料檢索（索引）、上游 OAuth 委任授權，並提供範例意圖/回應（few-shot）。

- 實施步驟：
  1. 工具建模
     - 細節：根據業務上下文拆 tool，控制參數與回傳。
     - 資源：MCP SDK、OpenAPI→MCP 轉換。
     - 時間：1-2 週。
  2. 安全治理
     - 細節：OAuth/OIDC、審計、速率、配額。
     - 資源：IdP、API Gateway。
     - 時間：1 週。

- 關鍵程式碼/設定：
```json
{
  "tools": [{
    "name": "orders.create",
    "description": "建立訂單（已根據使用者會話預設參數）",
    "auth": "oauth2",
    "parameters": {"type":"object","properties":{"sku":{"type":"string"},"qty":{"type":"integer"}},"required":["sku","qty"]}
  }]
}
```

- 實際案例：文中引用 Shopify Storefront MCP，設計精巧、上下文友好。
- 實作環境：MCP SDK、IdP/OAuth、API 平台。
- 實測數據：建議追蹤「Agent 成功任務率」「token/任務」「錯用率」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #16: 超越 .env：以 OAuth 授權與短期憑證保護 Agent 工具

### Problem Statement
- 業務場景：把長期 token 放在 .env 給 agent 風險高；需要最小權限、可回收、可審計的安全模式。
- 技術挑戰：將 agent 操作轉為「按需授權」，token 短期有效且作用域限縮。
- 影響範圍：資安、合規、事故半徑。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 靜態金鑰長期有效、作用域過大。
  2. 無審計與吊銷機制。
  3. 多工具共用同一憑證。
- 深層原因：
  - 架構層面：未採用 OAuth/OIDC 委任模式。
  - 技術層面：缺少密鑰管理/輪替。
  - 流程層面：授權與使用未解耦。

### Solution Design
- 解決策略：以 OAuth/OIDC 為 MCP 工具授權基礎；由 agent runner 在任務開始時換發短期 token；統一密鑰管理（Vault/KMS）。

- 實施步驟：
  1. 工具改造
     - 細節：在 MCP 工具定義中標示 oauth2；後端支持 token 驗證。
     - 資源：IdP、OAuth。
     - 時間：3-5 天。
  2. 密鑰管控
     - 細節：使用 Vault/KMS、審計、輪替策略。
     - 資源：祕鑰管理系統。
     - 時間：3-5 天.

- 關鍵程式碼/設定：
```yaml
# tool 定義（節選）
auth: oauth2
scopes:
  - orders.read
  - orders.write
token_ttl: "15m"
```

- 實際案例：文中趨勢（Beyond .env / secrets management）。
- 實作環境：IdP、OAuth、Vault、MCP。
- 實測數據：建議追蹤「憑證洩漏事件」「作用域異常使用」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #17: Agent 抽象基元：身份、計費、持久化的通用層

### Problem Statement
- 業務場景：各式 agent 產品都需要統一的「身份映射、用量計費、長期儲存」；每家重造輪子成本高。
- 技術挑戰：如何提供共用的 Agent Gateway（Auth/Billing/Storage）供多 agent 復用。
- 影響範圍：上線速度、運營成本、生態一體化。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 身份/授權/計量/儲存四散。
  2. 每個 agent 各自實作，缺統一治理。
  3. 難以跨產品統一對賬與合規。
- 深層原因：
  - 架構層面：缺少「Agent PaaS」抽象層。
  - 技術層面：計費度量與事件模型不一。
  - 流程層面：沒有通用運營標準。

### Solution Design
- 解決策略：建立 Agent Gateway：統一 OIDC 登入、JWT actor claim、用量事件（token/工具次數/任務時長）、持久化（向量/文檔/KV）。

- 實施步驟：
  1. 身份與 actor 映射
     - 細節：最終用戶→agent→工具的委任關係寫入 JWT。
     - 資源：IdP、API Gateway。
     - 時間：1 週。
  2. 計費與存儲
     - 細節：度量事件匯集、對帳、儲存抽象（S3/DB/向量）。
     - 資源：遙測/計費平台、存儲。
     - 時間：2-3 週。

- 關鍵程式碼/設定：
```json
// JWT payload（示意）
{
  "sub": "user-123",
  "actor": "agent-abc",
  "scp": ["orders.write"],
  "exp": 1712345678
}
```

- 實際案例：文中趨勢（Every AI agent needs auth, billing, and persistent storage）。
- 実作環境：IdP、API GW、計費平台、存儲服務。
- 實測數據：建議追蹤「上線時間縮短」「跨產品對帳準確率」（文中無數字）。

Learning/Practice/Assessment 略。


## Case #18: 以工具鏈綁定的「狀態總結」：Log/Error/Deploy → Markdown + Mermaid

### Problem Statement
- 業務場景：SRE/開發需快速了解「今天 API Gateway 狀態如何？」；靜態儀表板資訊噪音大、難聚焦。
- 技術挑戰：AI 需能生成查詢（log/error/deploy）、彙整上下文、輸出可視化報告。
- 影響範圍：可觀察性、問題定位、決策效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺乏查詢工具；AI 無法自助拉數據。
  2. 報告無標準格式，難以閱讀/分享。
  3. 未把部署變更關聯到事件。
- 深層原因：
  - 架構層面：觀測工具未 MCP 化。
  - 技術層面：缺少標準的輸出（markdown/mermaid）。
  - 流程層面：未有「問題→自助查詢→輸出報告」節拍。

### Solution Design
- 解決策略：提供 log.query、error.search、deploy.history 工具；AI 拉取後以 markdown + mermaid 生成「一次性報告」給人/agent 共讀。

- 實施步驟：
  1. 工具封裝
     - 細節：封裝查詢語言/範圍/聚合。
     - 資源：觀測平台 API、MCP。
     - 時間：2-3 天。
  2. 報告模板
     - 細節：生成標準章節、圖表（mermaid）。
     - 資源：模板/渲染器。
     - 時間：1 天。

- 關鍵程式碼/設定：
```markdown
# 今日 API Gateway 健康報告
## 錯誤趨勢
```mermaid
xychart
  title "5xx errors per 15m"
  x-axis [09:00,09:15,09:30]
  y-axis "count"
  series "5xx" [12, 34, 18]
```
```

- 實際案例：文中描述 agent 會動態生成 log query、error query、部署記錄並彙整輸出。
- 實作環境：觀測平台（ELK/CloudWatch/Datadog）、MCP、Markdown viewer。
- 實測數據：建議追蹤「問題定位耗時」「一次報告採納率」（文中無數字）。

Learning/Practice/Assessment 略。


--------------------------------
案例分類
--------------------------------

1) 按難度分類
- 入門級：#11, #12, #7, #6
- 中級：#1, #2, #4, #5, #8, #9, #10, #13, #18
- 高級：#3, #14, #15, #16, #17

2) 按技術領域分類
- 架構設計類：#3, #5, #7, #8, #14, #17
- 效能優化類：#14, #18
- 整合開發類：#1, #2, #4, #9, #10, #13, #15, #16
- 除錯診斷類：#11, #18
- 安全防護類：#12, #16, #17

3) 按學習目標分類
- 概念理解型：#4, #5, #7, #8, #15, #17
- 技能練習型：#1, #2, #6, #9, #10, #11, #12, #18
- 問題解決型：#3, #13, #14, #16
- 創新應用型：#5, #8, #15, #17

--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 建議先學（基礎鋪墊）：
  - #7 Document as Code → #8 Context Engineering（文件/上下文基礎）
  - #11 無障礙語義 → #12 OS 無障礙權限（Agent 操作 UI 的基礎）
  - #1 AI-native Git → #2 語義 Diff（版本控制思維轉換）

- 依賴關係與進階：
  - #7/#8 → 支撐 #4 Generative UI、#5 MVC+LLM、#9 TDD Vibe Coding
  - #1/#2 → 支撐 #13 非同步工作流的可追溯審核
  - #11/#12 → 提升 #18 狀態總結與 #13 自動化流程的可靠度
  - #3 沙箱 → 是 #13/#14 大規模 agent 外包的前置條件
  - #15 MCP-first → 是 #4/#18/所有 agent 工具化的標準底座
  - #16 Secrets、#17 抽象基元 → 構成整個 agent 平台的安全與運營支撐

- 完整學習路徑建議：
  1) 基礎與思維轉換：#7 → #8 → #1 → #2 → #11 → #12
  2) 構建 AI-first 應用：#4 → #5 → #9 → #10
  3) 從單機到平台：#3 → #13 → #14
  4) 生態與安全：#15 → #16 → #17
  5) 可觀察與總結：#18（貫穿運營）

按此路徑，你將從文件/上下文與版控思維完成 AI 時代的基礎轉型，進而掌握 AI 驅動 UI 與 TDD 的工程節奏，最後建構可擴縮、可營運、可觀察的 agent 平台能力。