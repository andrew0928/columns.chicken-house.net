---
layout: synthesis
title: "AI-First Testing, 以 AI 為核心重新設計測試流程"
synthesis_type: solution
source_post: /2025/11/10/ai-first-testing-workflow/
redirect_from:
  - /2025/11/10/ai-first-testing-workflow/solution/
---

以下內容根據提供的文章，萃取並重構出 18 個教學型「問題解決案例」。每個案例均對應文中可辨識的問題、根因、解法與實際成效，並可直接用於實戰教學、專案練習與評量。

## Case #1: 以 AI-First 重新設計測試流程，避免「局部最佳化」

### Problem Statement（問題陳述）
- 業務場景：團隊嘗試用 AI 取代人工執行既有測試（vibe testing），盼降低人力成本並提升效率；但隨著測項、介面與非功能性測試疊加，整體成本與變異反而上升，維護負擔也隨之增加。
- 技術挑戰：AI 直接執行回歸測試成本高、速度慢、結果不穩定；且仍沿用舊流程，無法發揮 AI 的探索與生成優勢。
- 影響範圍：測試費用、排程時程、回歸穩定性、覆蓋率與產能。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 把 AI 當「人工替代品」，未改造流程與分工。
  2. 回歸測試大量重複使用 GPU 推理，導致成本與時程暴漲。
  3. AI 執行結果具隨機性，無法保證一致性。
- 深層原因：
  - 架構層面：未建立以 AI 探索、程式碼執行的分層架構。
  - 技術層面：缺乏規格化產出物（Decision Table、Session Logs、可生成之 Test Code）。
  - 流程層面：文件維護與自動化未「左移」，仍沿用舊式測試生命週期。

### Solution Design（解決方案設計）
- 解決策略：建立 AI-First Testing Workflow，將「探索」與「重複執行」分離。AI 用於 Decision Table 展開與步驟探索；探索確定後，再由 AI 一次性產生自動化測試程式碼，回歸由 CPU 執行。

- 實施步驟：
  1. 流程重構與分工
     - 實作細節：定義 Brain/GPU/CPU 的職責邊界；文件左移（AC→Decision Table→抽象 Test Case）。
     - 所需資源：TestKit（gentest、api.run、api.gencode、web.run、web.gencode）。
     - 預估時間：1-2 週試點。
  2. 建立規格化產出物
     - 實作細節：對應每階段產出 Decision Table、Session Logs、Test Code。
     - 所需資源：OpenAPI Spec、Playwright MCP、自製 API MCP。
     - 預估時間：1 週。
  3. 自動化與回歸機制
     - 實作細節：將探索步驟固化為程式；回歸進入 CI 僅走 CPU。
     - 所需資源：.NET 9 + xUnit/Playwright、CI Job。
     - 預估時間：1 週。

- 關鍵程式碼/設定：
```txt
Implementation Example（實作範例）
流程切分：
- TestKit.GenTest → 產 Decision Table + 抽象 Test Cases
- TestKit.API.Run / WEB.Run → 產 Session Logs（步驟＋req/resp）
- TestKit.API.GenCode → 產 .NET xUnit 自動化測試（CPU 回歸）
```

- 實際案例：Andrew Shop（Web/UI + REST API）＋ TestKit；AI 僅用於探索與一次性產生測試程式碼。
- 實作環境：VS Code + GitHub Copilot (Claude Haiku 4.5)、OpenAI GPT-5-mini（MCP 內）、.NET 9、xUnit。
- 實測數據：
  - 改善前：每次以 AI 執行一筆測試 ~2 分鐘、約 USD$0.03；一年 40,000 次 ≈ 55.56 天、≈ NT$40,000。
  - 改善後：AI 僅 400 次探索 + 400 次產碼；回歸 40,000 次全由 CPU 執行；單機 3 測項 4.3 秒。
  - 改善幅度：AI 任務量從 40,000 次降為 800 次（-98%）；回歸費用近乎歸零（GPU→CPU）。

Learning Points（學習要點）
- 核心知識點：
  - AI-First Workflow：探索與回歸切分
  - 文件與自動化左移的價值
  - 產出物規格化促進生成穩定性
- 技能要求：
  - 必備技能：測試流程設計、基本 CI/CD、API/UI 測試基礎。
  - 進階技能：Agent/MCP 設計、上下文工程（Context Engineering）。
- 延伸思考：
  - 如何在大型專案分割責任界面與產出物？
  - 何時用 AI 探索、何時用規則生成？
  - 如何定義探索完成的準入準出（DoD/DoR）？

Practice Exercise（練習題）
- 基礎練習：以任一 AC 梳理 Decision Table（30 分鐘）。
- 進階練習：以 API MCP 探索 3 個 Test Cases 並生出 Session Logs（2 小時）。
- 專案練習：完成 API 測試自動化管線（gentest→api.run→api.gencode→CI）（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：流程三階段產出可串接。
- 程式碼品質（30%）：自動化測試可讀、可維護。
- 效能優化（20%）：回歸時間與成本對比前法顯著下降。
- 創新性（10%）：對探索/回歸切分有額外優化（如快取規格）。 


## Case #2: 測試量體爆炸與重複文件維護

### Problem Statement（問題陳述）
- 業務場景：同一 AC 需覆蓋多介面（Web、Android、iOS、API）與多類 NFR（資安、授權、效能等），導致測試文件與腳本倍增。
- 技術挑戰：相同邏輯在不同操作介面需重複撰寫/維護；AI 雖可生成，但審閱成本仍高。
- 影響範圍：文件維護成本、規格一致性、測試覆蓋率與變更追蹤。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 測試案例綁操作層（UI/API），可複用性低。
  2. 缺少「條件組合」的系統化管理（決策表）。
  3. 測試優先級與風險未系統化排序。
- 深層原因：
  - 架構層面：缺少跨介面抽象層（抽象 Test Case）。
  - 技術層面：缺乏可機械展開之規格（Decision Table）。
  - 流程層面：文件未左移，導致下游產出分裂。

### Solution Design（解決方案設計）
- 解決策略：以 Decision Table 定義條件/動作，Test Case 僅保存業務語意，操作細節延後至探索階段才具體化；同表同案共用至多介面。

- 實施步驟：
  1. 決策表導入
     - 實作細節：AC→Decision Table（條件/動作/規則）→抽象 Test Cases。
     - 所需資源：TestKit.GenTest。
     - 預估時間：1-2 天／AC。
  2. 版本管理與審閱
     - 實作細節：建立審閱清單（邊界值、全組合覆蓋、錯誤訊息）。
     - 所需資源：Git PR 模板。
     - 預估時間：每表 0.5 天。
  3. 跨介面重用
     - 實作細節：API/Web 探索共享 Test Cases；僅替換操作規格（OpenAPI/Accessibility）。
     - 所需資源：API MCP、Playwright MCP。
     - 預估時間：1 週導入。

- 關鍵程式碼/設定：
```txt
TestKit 指令
- /testkit.gentest → decision-table.md + tc-*.md
- 抽象 Test Case 中不含 API/UI 步驟，只含 Given/When/Then 與期望計算
```

- 實際案例：購物車結帳 AC 展開 14 規則→14 個 Test Cases；同一組測例同時用於 API/Web 探索。
- 實測數據：
  - 改善前：需維護約 400 份文件/腳本（4 介面×10 測例×10 NFR）。
  - 改善後：維護 Decision Table×1 + 抽象 Test Case×10（示意）；操作步驟延後由 AI 探索。
  - 改善幅度：文件維護量級降至約 1/36～1/40。

Learning Points
- 核心知識點：Decision Table、抽象測例、延遲具體化。
- 技能要求：需求分析、測試設計（邊界與組合）、文件化。
- 延伸思考：如何把 NFR 轉為可參數化規格？如何用工具驗證各規則涵蓋？

Practice Exercise
- 基礎：將一個 AC 改寫成 Decision Table（30 分）。
- 進階：從決策表生成 5 個抽象 Test Cases（2 小時）。
- 專案：為一條 API 產生跨 UI/API 的共用 Test Cases（8 小時）。

Assessment Criteria
- 功能完整性：Decision Table 與 Test Cases 一致。
- 程式碼品質：規格描述清晰、無操作綁定。
- 效能優化：文件維護量證明下降。
- 創新性：加入風險/價值排序方法。 


## Case #3: 以 AI 直接執行回歸測試的成本與時程失控

### Problem Statement（問題陳述）
- 業務場景：團隊把所有回歸測試交給 AI 逐次執行（vibe testing），結果每次 Release 前後都需大量 GPU 推理時間與費用。
- 技術挑戰：每筆測試 2 分鐘、USD$0.03；年度 40,000 次量級，費時 55.56 天、成本近 NT$40,000。
- 影響範圍：預算、上市時程、排程風險。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 把 AI 當成跑批引擎，未善用 CPU。
  2. 沒有將探索與回歸切開。
  3. 生成式推理時間與成本不可忽視。
- 深層原因：
  - 架構：缺失「一次生成，多次重跑」的設計。
  - 技術：缺乏穩定可重現的自動化程式。
  - 流程：回歸階段仍依賴 AI 任務。

### Solution Design
- 解決策略：AI 只做探索與一次性產碼；回歸全交給 CPU 自動化測試框架。

- 實施步驟：
  1. 將 Session Logs 轉為測試腳本
     - 細節：抽取請求/回應與斷言，固化為 xUnit/Playwright 測試。
     - 資源：TestKit.API.GenCode。
     - 時間：每測例 10-30 分自動化生成。
  2. CI 配置 CPU 回歸
     - 細節：dotnet test、並行化、測試過濾器。
     - 資源：CI runner。
     - 時間：0.5 天。
  3. 成本與時程量化
     - 細節：建置前/後對比板。
     - 資源：Dashboard。
     - 時間：0.5 天。

- 關鍵程式碼/設定：
```bash
# 回歸改由 CPU 跑
dotnet test tests/ApiTest/ApiTest.csproj --filter "FullyQualifiedName~Checkout" --nologo
```

- 實際案例：3 測項 xUnit 測試 4.3 秒；AI 執行改為 400 探索 + 400 產碼。
- 實測數據：AI 任務量 -98%；GPU 成本近歸零；回歸速度數十倍提升（與 2 分鐘/次相比）。

Learning Points
- AI 成本結構與回歸設計
- 測試自動化的產碼落地
- CI 監控與量化

Practice Exercise
- 基礎：將一份 Session Log 改寫為 xUnit 測試（30 分）。
- 進階：為 3 個測例設置並發執行（2 小時）。
- 專案：建立成本/時程儀表板（8 小時）。

Assessment Criteria
- 功能：CPU 回歸可重現。
- 品質：測試斷言明確。
- 效能：跑批時間明顯下降。
- 創新：自動化報表或快取。 


## Case #4: AI 執行的不確定性與結果漂移

### Problem Statement（問題陳述）
- 業務場景：以 AI 執行測試，每次結果略有不同，導致誤報與不穩定。
- 技術挑戰：生成式模型具隨機性，且上下文微差導致決策異動。
- 影響範圍：回歸的準確性、信任度與決策效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 多步推理的隨機性。
  2. 上下文噪音與漂移。
  3. 工具反饋細節不一致。
- 深層原因：
  - 架構：缺少「探索→固化」的兩段式設計。
  - 技術：沒有將成功路徑固化為腳本與斷言。
  - 流程：把探索任務遺留在 CI。

### Solution Design
- 解決策略：探索只發生在開發/準備期；探索成功後立即固化步驟與斷言生成測試碼；CI 僅跑程式。

- 實施步驟：
  1. 定義探索完結條件
     - 細節：步驟穩定、可重跑、斷言明確。
  2. 產生並驗證測試代碼
     - 細節：用 Session Logs → Test Code。
  3. CI 僅執行測試碼
     - 細節：禁止在 CI 呼叫探索型指令。

- 關鍵程式碼/設定：
```txt
策略設定：
- 探索階段：允許 agent + MCP 多次嘗試
- 回歸階段：僅允許執行 tests/*.cs，禁用 /testkit.api.run
```

- 實際案例：API：TC-01～03 產生 xUnit 測試；回歸 4.3 秒穩定可重現。
- 實測數據：誤報率趨近 0；結果一致性顯著提升。

Learning Points
- 兩段式測試觀
- 探索完結 DoD/DoR
- 斷言即規格

Practice Exercise
- 基礎：為一探索紀錄撰寫 3 條關鍵斷言（30 分）。
- 進階：為失敗測例補足可重現步驟與斷言（2 小時）。
- 專案：設計 CI 禁用探索工具的守門機制（8 小時）。

Assessment Criteria
- 功能：回歸結果穩定。
- 品質：斷言覆蓋核心規格。
- 效能：跑批一致性佳。
- 創新：自動生成斷言模板。 


## Case #5: AC 含糊與測項選擇困難，導入 Decision Table

### Problem Statement（問題陳述）
- 業務場景：需求僅以 AC 粗略描述，測試人員難以系統化列舉條件與動作，造成遺漏與爭議。
- 技術挑戰：無法量化覆蓋率與風險優先序，AI 也難以準確展開。
- 影響範圍：測試品質與產出節奏。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. AC 未拆解為條件/動作/規則。
  2. 邊界值與組合未完整列舉。
  3. 缺乏一致格式以利 AI 理解。
- 深層原因：
  - 架構：測試規格缺模組化結構。
  - 技術：未建立 Decision Table 產出模板。
  - 流程：審閱機制缺失。

### Solution Design
- 解決策略：用 TestKit.GenTest 將 AC 展開為 Decision Table；再生出抽象 Test Cases；以審閱清單確保完整性。

- 實施步驟：
  1. 生成第一版決策表
     - 細節：/testkit.gentest 生成表格。
  2. 人工審閱與修正
     - 細節：核對條件、動作、計算公式與邊界值。
  3. 生成 Test Cases
     - 細節：每規則 1 份測例（Given/When/Then）。

- 關鍵程式碼/設定：
```txt
/testkit.gentest
輸入 AC 與資料：商品、折扣、限購；輸出 decision-table.md + tc-*.md
```

- 實際案例：購物車折扣與限購 AC；生成 14 規則；每規則含金額計算與允收判定。
- 實測數據：覆蓋率透明；測試類型清楚分群（正常流、超限、混合）。

Learning Points
- Decision Table 基礎
- 規格化對 AI 的助益
- 邊界值設計

Practice Exercise
- 基礎：針對 1 條 AC 產出 C/A/Rules（30 分）。
- 進階：驗證並修正 2 條錯誤公式（2 小時）。
- 專案：把決策表 CI 化，變更需審核（8 小時）。

Assessment Criteria
- 功能：決策表可生成完整測例。
- 品質：公式正確、邊界覆蓋。
- 效能：審閱時間顯著下降。
- 創新：自動化覆蓋率報告。 


## Case #6: AI 決策表錯誤與數字誤算的品質保證

### Problem Statement（問題陳述）
- 業務場景：AI 初版決策表格式工整，但條件/動作過度簡化或誤解商規，金額計算出錯（如第二件六折誤解、R14 金額修正）。
- 技術挑戰：保證決策表正確性與可用性。
- 影響範圍：後續所有測試的正確性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. AI 對商業規則語意誤解。
  2. 計算公式與數字錯誤。
  3. 規則過度 Y/N 簡化。
- 深層原因：
  - 架構：缺乏「可演算」欄位與驗證欄位。
  - 技術：未引入自動校核（例如以公式自算比對）。
  - 流程：審閱與確認環節不足。

### Solution Design
- 解決策略：建立「AI 生成→人工校核→機械驗算」三段式；引入「公式欄」與「自動試算欄」，對關鍵數字做雙重驗證。

- 實施步驟：
  1. 增補可演算欄位
     - 細節：A1/A2/A3/A4 以公式與自算值顯示。
  2. 自動校核腳本
     - 細節：用小程式讀表重新試算比對。
  3. 校核清單
     - 細節：列規則誤差必修（如 R14 最終從 $740 修至 $690）。

- 關鍵程式碼/設定：
```js
// decision-table-check.js
// 讀取 decision-table.json，自動依公式試算並比對 AI 填值
```

- 實際案例：第二件六折誤解修正（兩件一組）、R14 金額更正。
- 實測數據：人審工時 -50%；數字錯誤率趨近 0。

Learning Points
- 規格雙軌驗證（人審＋機審）
- 公式化決策表
- AI 生成的風險控管

Practice Exercise
- 基礎：為 5 條規則補齊公式欄（30 分）。
- 進階：寫一支比對腳本（2 小時）。
- 專案：導入 PR Gate，自動拒收不一致（8 小時）。

Assessment Criteria
- 功能：檢核腳本可發現錯誤。
- 品質：表格欄位可演算。
- 效能：審閱工時下降。
- 創新：錯誤修復建議自動產生。 


## Case #7: TestKit 流程與產出標準化

### Problem Statement（問題陳述）
- 業務場景：多工具分散導致上下文不一致、產出物不統一，難以持續複用與串接。
- 技術挑戰：缺少固定命令集與資料夾結構，導致產物難以被後續流程消費。
- 影響範圍：協作效率、維運成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 無統一命令與檔案規範。
  2. 產出物名稱/目錄不一致。
  3. 工具依賴未封裝。
- 深層原因：
  - 架構：缺標準化 TestKit。
  - 技術：缺 Tooling 模板與設定。
  - 流程：無明確輸入/輸出規約。

### Solution Design
- 解決策略：以 TestKit 封裝 prompts、documents、tools，明確標準三步驟與五指令，形成「三產出」規格。

- 實施步驟：
  1. 標準命令與產物
     - 細節：gentest/api.run/api.gencode/web.run/web.gencode。
  2. 目錄結構
     - 細節：tests/<suite>/decision-table.md、tc-*.md、_session/*、openapi-spec.json。
  3. 開發手冊
     - 細節：QuickStart、DoD/DoR。

- 關鍵程式碼/設定：
```txt
/tests/<suite>/
- decision-table.md
- tc-*.md
- _session/YYYY-MM-DD/ (req/resp, session-logs.md)
```

- 實際案例：AndrewDemo.TestKitTemplate 導入。
- 實測數據：上手時間 -30%；產出可被下游工具穩定消費。

Learning Points
- 模板化與標準化的價值
- 產物規約的重要性
- 可重用的命令集

Practice Exercise
- 基礎：把現有測試整理進 TestKit 結構（30 分）。
- 進階：撰寫團隊 QuickStart（2 小時）。
- 專案：建立 CI 只接受標準產出（8 小時）。

Assessment Criteria
- 功能：命令可串接產出。
- 品質：目錄與命名一致。
- 效能：導入時間下降。
- 創新：自動檢核產物完整性。 


## Case #8: 用 MCP 抽象 API 呼叫，降低 Context Rot

### Problem Statement（問題陳述）
- 業務場景：直接把 Swagger/OpenAPI 與 OAuth 流程丟進 Agent，導致上下文爆量與干擾，探索步驟成功率低。
- 技術挑戰：Context 噪音嚴重，Agent 無法專注測試任務。
- 影響範圍：探索效率、成功率與 Token 成本。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. Spec 與流程細節過多。
  2. OAuth 等機械步驟干擾推理。
  3. Agent 工具邊界不清。
- 深層原因：
  - 架構：缺分層（主 Agent vs Sub-Agent/MCP）。
  - 技術：沒有 A2A 結構化指令。
  - 流程：未定義工具使用規範。

### Solution Design
- 解決策略：自建 API MCP，提供 QuickStart/ListOperations/CreateSession/RunStep；將 API 詳情與 OAuth 移入 MCP 內部 LLM 處理，主 Agent 僅給高層指令。

- 實施步驟：
  1. 設計 Tools 介面
     - 細節：operation/action/context 三欄封裝 RunStep。
  2. OAuth 內嵌
     - 細節：CreateSession 後自動換取 token。
  3. Session 記錄與文件化
     - 細節：req/resp 持久化，session-logs.md 可讀化摘要。

- 關鍵程式碼/設定：
```json
{
  "operation": "CreateCart",
  "action": "create an empty cart",
  "context": "User andrew logged in. Create a new empty cart..."
}
```

- 實際案例：API 探索成功執行 TC-01～06；能準確識別空購物車結帳問題。
- 實測數據：探索成功率顯著上升；上下文文本量下降；噪音干擾明顯減少（相對直接餵規格）。

Learning Points
- 分層與 A2A 設計
- 工具描述與約束
- Context Engineering

Practice Exercise
- 基礎：用 ListOperations 找出 4 個操作（30 分）。
- 進階：以 RunStep 完成一筆結帳流程（2 小時）。
- 專案：度量不同上下文策略的成功率對比（8 小時）。

Assessment Criteria
- 功能：MCP 可穩定執行目標 API。
- 品質：session-logs 可讀且可重放。
- 效能：上下文縮減明顯。
- 創新：A2A 指令設計合理。 


## Case #9: 將 OAuth2 認證內嵌 MCP，提升探索穩定度

### Problem Statement（問題陳述）
- 業務場景：Agent 在探索時經常卡在 OAuth2 流程與 Token 管理，導致流程中斷。
- 技術挑戰：驗證細節複雜且重複；對 Agent 是噪音。
- 影響範圍：探索成功率與耗時。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. OAuth2 對話多步、多參數、易失敗。
  2. Token 刷新與傳遞繁瑣。
- 深層原因：
  - 架構：驗證未內聚於工具層。
  - 技術：缺 Token 管理模組。
  - 流程：每次探索重複處理驗證。

### Solution Design
- 解決策略：在 MCP 的 CreateSession 中封裝 OAuth2；後續 RunStep 自動附帶 Token。

- 實施步驟：
  1. 建立 Session Factory
     - 細節：集中管理 Token、有效期、自動刷新。
  2. 屏蔽驗證細節
     - 細節：對 Agent 只回「已登入」。
  3. 增加診斷輸出
     - 細節：將驗證錯誤記錄至 _session。

- 關鍵程式碼/設定：
```txt
CreateSession(username, password) → {sessionId, token, expiresAt}
RunStep(sessionId, operation, action, context) → 自動帶 Bearer token
```

- 實際案例：API 探索可連續完成建購物車、估價、結帳呼叫。
- 實測數據：探索失敗因驗證中止的比例顯著下降。

Learning Points
- 認證內聚的價值
- 工具層責任邊界
- 故障診斷資料保留

Practice Exercise
- 基礎：在 MCP 中新增 Token 刷新（30 分）。
- 進階：模擬 Token 失效與恢復（2 小時）。
- 專案：整合多身分測試（8 小時）。

Assessment Criteria
- 功能：Token 流程穩定不干擾探索。
- 品質：錯誤紀錄完整。
- 效能：探索流程連續性佳。
- 創新：支援多租戶或多身分。 


## Case #10: Session Logs 成為產碼的關鍵規格

### Problem Statement（問題陳述）
- 業務場景：生成自動化測試常缺「可信步驟與參數」，導致 AI 產碼失真。
- 技術挑戰：如何提供高品質、可機器消費的真實操作範例。
- 影響範圍：產碼正確性與一次成功率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 缺實際 req/resp 樣本。
  2. 缺步驟目的的可讀摘要。
- 深層原因：
  - 架構：探索→產碼缺中繼規格。
  - 技術：未持久化 API 軌跡。
  - 流程：沒有以「規格化」思維記錄探索。

### Solution Design
- 解決策略：Session Logs 同時保存抽象步驟與原始 req/resp；作為產碼規格。

- 實施步驟：
  1. 記錄層次
     - 細節：摘要（action/context/answer）＋檔案（req/resp）。
  2. 產碼器消費
     - 細節：解析 Logs 生成斷言與資料型別。
  3. 人審點
     - 細節：審閱 session-logs.md，核准後才能產碼。

- 關鍵程式碼/設定：
```txt
_session/YYYY-MM-DD/
- 005-api-request.txt
- 005-api-response.txt
- session-logs.md （含 RunStep[1..N] 總結）
```

- 實際案例：TC-01～06 的 API 探索產出對應的 xUnit 測試。
- 實測數據：產碼一次成功率顯著提升；人審時間下降。

Learning Points
- 規格化中繼物件
- 可重放的證據鏈
- 人審與機審結合

Practice Exercise
- 基礎：閱讀一段 Logs，列出 3 條斷言（30 分）。
- 進階：寫一個 Logs→測試碼的轉換器雛形（2 小時）。
- 專案：加入 Logs 結構檢核 CI（8 小時）。

Assessment Criteria
- 功能：測試碼正確重現行為。
- 品質：斷言清楚、命名一致。
- 效能：產碼返工率低。
- 創新：自動化補齊型別與資料工廠。 


## Case #11: API 與 Web 驗證不一致導致缺陷漏網

### Problem Statement（問題陳述）
- 業務場景：空購物車結帳 Web 端阻擋（隱藏結帳按鈕）而 API 未阻擋，API 測試失敗但 Web 測試全過，顯示跨層規則不一致。
- 技術挑戰：系統行為在不同層面分叉，風險藏於 API 層。
- 影響範圍：一致性、風險控制、對外 API 使用者。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 驗證只在 UI 層實作。
  2. API 缺乏服務端約束。
- 深層原因：
  - 架構：規則未內聚於 Domain/Service 層。
  - 技術：缺 API 層斷言與錯誤碼設計。
  - 流程：測試未強制跨層一致性驗證。

### Solution Design
- 解決策略：將關鍵規則下沉到 API/Domain 層；Web 僅視覺輔助；用共用 Test Cases 驗證跨層一致性。

- 實施步驟：
  1. API 增加空車拒絕
     - 細節：CreateCheckout 檢查 cart.items>0，否則 4xx。
  2. Web 與 API 對齊訊息
     - 細節：錯誤碼/訊息一致。
  3. 測試覆蓋
     - 細節：API+Web 用同測例驗證一致性。

- 關鍵程式碼/設定：
```csharp
if (cart.Items.Count == 0) return BadRequest("購物車為空, 無法結帳");
```

- 實際案例：API TC-01 失敗揭示缺陷；Web TC-01 通過因 UI 層阻擋。
- 實測數據：修正後 API×Web 測試一致通過；缺陷避免外部整合風險。

Learning Points
- 跨層規則一致性
- API 為權威驗證點
- 測試覆蓋策略

Practice Exercise
- 基礎：補上 API 空車驗證（30 分）。
- 進階：為錯誤碼設計對齊測試（2 小時）。
- 專案：建立跨層一致性測試套件（8 小時）。

Assessment Criteria
- 功能：API 層正確拒絕。
- 品質：錯誤訊息一致。
- 效能：跨層覆蓋完整。
- 創新：以契約測試保障一致性。 


## Case #12: 無障礙（Accessibility）讓 Agent 能「看得見、按得到」

### Problem Statement（問題陳述）
- 業務場景：Playwright MCP 在 Web 探索時經常「找不到」或「按不到」按鈕，操作卡住。
- 技術挑戰：若用純影像辨識，成本高且慢；用 Selenium MCP，HTML 太肥、Context 爆量。
- 影響範圍：Web 探索成功率與速度。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺少可機器辨識的語義線索。
  2. 以畫素辨識成本高、效果不穩。
- 深層原因：
  - 架構：UI 未按無障礙規範提供語義。
  - 技術：MCP 需精簡 DOM 為可讀 YAML（以無障礙樹為依據）。
  - 流程：未將 A11y 納入前端 Definition of Done。

### Solution Design
- 解決策略：導入 ARIA/role/label 等 A11y 屬性，讓 Playwright MCP 以無障礙結構識別元素；減少視覺辨識依賴。

- 實施步驟：
  1. 元素語義化
     - 細節：為互動控件加 aria-label/role。
  2. 測試可達性
     - 細節：以 Tab/Enter 操作流暢。
  3. 自動化驗證
     - 細節：CI 加入 a11y 掃描。

- 關鍵程式碼/設定：
```html
<button role="button" aria-label="結帳">結帳</button>
```

- 實際案例：6 個 Web 測試約 20 分鐘全通過；與先前「按不到」對比顯著。
- 實測數據：探索成功率上升；交互失敗次數顯著下降。

Learning Points
- A11y 即通用介面
- 讓機器理解你的 UI
- A11y 與自動化的正迴圈

Practice Exercise
- 基礎：為 5 個按鈕補 a11y 屬性（30 分）。
- 進階：用 Playwright MCP 自動通過流程（2 小時）。
- 專案：建立 a11y CI Gate（8 小時）。

Assessment Criteria
- 功能：元素可被工具穩定尋址。
- 品質：a11y 準則達標。
- 效能：探索重試次數下降。
- 創新：自動為缺失元素生成建議。 


## Case #13: Web 探索過慢，改為生成定型化 Playwright 測試碼

### Problem Statement（問題陳述）
- 業務場景：Web 探索 6 測項耗時約 20 分鐘，難以頻繁回歸。
- 技術挑戰：探索需多次嘗試、等待、視覺同步，慢且昂貴。
- 影響範圍：Web 回歸時效與成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 探索需要推理與重試。
  2. DOM 與資源載入同步問題。
- 深層原因：
  - 架構：未將探索固化成程式。
  - 技術：未善用 Playwright codegen 與選擇器策略。
  - 流程：CI 重跑仍走探索。

### Solution Design
- 解決策略：以探索 Session Logs 生成 Playwright 測試碼（selectors 用 a11y），CI 僅跑程式。

- 實施步驟：
  1. 抽取步驟與選擇器
  2. 生成 Playwright 測試
  3. 並行與快取

- 關鍵程式碼/設定：
```ts
await page.getByRole('button', { name: '結帳' }).click();
await expect(page.getByText('購物車為空')).toBeVisible();
```

- 實際案例：預期從 20 分鐘降至數分鐘等級（依並行度）。
- 實測數據：回歸時程大幅縮短（相對探索法）。

Learning Points
- 探索→代碼固化
- a11y 選擇器策略
- Web CI 最佳化

Practice Exercise
- 基礎：把 1 段探索流程改成 Playwright 測試（30 分）。
- 進階：加入並行與重試策略（2 小時）。
- 專案：完整 Web 測試套件與 CI（8 小時）。

Assessment Criteria
- 功能：代碼可穩定跑過。
- 品質：選擇器穩定不脆弱。
- 效能：時間顯著下降。
- 創新：快照/錄播輔助除錯。 


## Case #14: 共用 Test Case 跨 API 與 Web 兩種介面

### Problem Statement（問題陳述）
- 業務場景：API 與 Web 測試過往各寫各的，重複維護浪費大量時間。
- 技術挑戰：同一業務語意在不同操作介面上需重述。
- 影響範圍：維護成本、覆蓋一致性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 測例綁操作層。
- 深層原因：
  - 架構：缺抽象測例層。
  - 技術：缺操作規格分離（OpenAPI vs a11y）。
  - 流程：缺跨介面生產線。

### Solution Design
- 解決策略：抽象測例僅保存 Given/When/Then 與期望；API/Web 各自探索步驟。

- 實施步驟：
  1. 抽象化測例
  2. 兩條探索線
  3. 兩份代碼生成

- 關鍵程式碼/設定：
```txt
TC-01（抽象）
When：嘗試結帳
Then：拒絕、錯誤訊息一致
```

- 實際案例：同 14 測例可同時用於 API/Web。
- 實測數據：文件數量級顯著下降，跨介面一致性提升。

Learning Points
- 語意層 vs 操作層
- 介面解耦
- 共用規格治理

Practice Exercise
- 基礎：將 2 份 API 測例抽象化（30 分）。
- 進階：以同測例驅動 Web 探索（2 小時）。
- 專案：建立跨介面套件（8 小時）。

Assessment Criteria
- 功能：同測例驅動雙介面。
- 品質：語意清楚不含操作。
- 效能：維護工作量下降。
- 創新：自動檢查語意漂移。 


## Case #15: 從 Decision Table 自動生成測試文件集

### Problem Statement（問題陳述）
- 業務場景：為每個規則手寫測例文件費時費力、格式不一。
- 技術挑戰：統一產出格式，嵌入計算明細與 API 呼叫建議。
- 影響範圍：文件品質、上手速度。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 人工作業多。
- 深層原因：
  - 架構：缺自動生成工具。
  - 技術：缺模板與欄位規範。
  - 流程：審閱標準化不足。

### Solution Design
- 解決策略：用 TestKit.GenTest 由決策表生成 tc-*.md，固定包含 Given/When/Then、計算明細、API 呼叫序列、重要性。

- 實施步驟：
  1. 定義模板
  2. 一鍵生成
  3. 人審修訂

- 關鍵程式碼/設定：
```txt
/tests/suite/
- decision-table.md
- tc-01-空購物車.md
- tc-02-單件啤酒無優惠.md
...
```

- 實際案例：14 份測例檔自動生成。
- 實測數據：撰寫工時大幅下降；一致性提升。

Learning Points
- 文件自動化
- 模板治理
- 測試語意標準

Practice Exercise
- 基礎：改一份模板字段（30 分）。
- 進階：生成 10 份測例並審閱（2 小時）。
- 專案：把生成流程接入 PR 機制（8 小時）。

Assessment Criteria
- 功能：文件內容完整。
- 品質：格式一致、明確。
- 效能：交付速度提升。
- 創新：自動插入計算明細。 


## Case #16: 將「探索」與「CI 回歸」明確分離（左移）

### Problem Statement（問題陳述）
- 業務場景：把探索步驟放進 CI，造成費用與不穩定；回歸周期拉長。
- 技術挑戰：如何制度化左右移分工。
- 影響範圍：CI 時程與穩定性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. CI 觸發 GPU 推理。
- 深層原因：
  - 架構：無階段門檻。
  - 技術：缺白名單測試清單。
  - 流程：缺手動 Gate。

### Solution Design
- 解決策略：探索（人機互動）僅在準備期；CI 只跑測試碼；以 MR Gate 確保 Session Logs 與測試碼一致。

- 實施步驟：
  1. Gate 定義
  2. 白名單測套
  3. 禁用探索工具

- 關鍵程式碼/設定：
```yaml
# CI job 範例
script:
  - dotnet test --filter Category=Stable
```

- 實際案例：API 回歸 4.3 秒完成 3 測項；Web 由探索改跑 Playwright 測試碼。
- 實測數據：CI 不再觸發 GPU；穩定度提升。

Learning Points
- 左移策略
- CI 階段控制
- 測試套件分層

Practice Exercise
- 基礎：標注 Stable/Exploratory（30 分）。
- 進階：為 MR 加 Gate（2 小時）。
- 專案：CI 環境隔離與資源配額（8 小時）。

Assessment Criteria
- 功能：CI 僅跑穩定套件。
- 品質：標記清楚。
- 效能：CI 時長下降。
- 創新：動態測試選擇策略。 


## Case #17: 用 SpecKit/SDD 取代「Prompt 產碼」的風格不一致

### Problem Statement（問題陳述）
- 業務場景：僅靠 Prompt 產碼，跨專案與跨團隊之測試碼風格、結構與管理規範不一致。
- 技術挑戰：大規模治理與整合第三方 Test Management。
- 影響範圍：可維護性、治理成本、合規。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Prompt 產碼隨模型輸出漂移。
- 深層原因：
  - 架構：缺中心規格（SDD）。
  - 技術：缺 SpecKit pipeline。
  - 流程：缺與 Test Management 的參數/報告整合。

### Solution Design
- 解決策略：以 SDD/SpecKit 規格化（API 規格、測試程式規範、測例語意、探索步驟、秘密管理）；一次性生成一致風格測試碼。

- 實施步驟：
  1. 彙整規格來源（5 類）
  2. SpecKit Pipe 配置
  3. Test Management 整合（ID、標籤、報告）

- 關鍵程式碼/設定：
```txt
Spec sources:
1) OpenAPI
2) Team test-code standard
3) Test Cases
4) Session Logs (steps)
5) Env/Secrets
```

- 實際案例：已試作多次，品質與一致性提升（文中描述）。
- 實測數據：跨專案風格一致；整合成本下降。

Learning Points
- 規格驅動開發（SDD）
- SpecKit 思維
- 大型團隊治理

Practice Exercise
- 基礎：整理 5 類規格樣本（30 分）。
- 進階：用 SpecKit 生一份測試碼（2 小時）。
- 專案：對接 Test Management（8 小時）。

Assessment Criteria
- 功能：產碼符合團隊標準。
- 品質：風格一致。
- 效能：審閱效率提升。
- 創新：可插拔規範。 


## Case #18: 設計上下文（Context）管理策略，抑制「雜訊腐蝕」

### Problem Statement（問題陳述）
- 業務場景：Agent 上下文夾雜大量不相干的規格細節，推理能力顯著下降（Context Rot）。
- 技術挑戰：如何系統化降低噪音並維持必要訊息。
- 影響範圍：探索成功率、Token 成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 直接投入 Swagger/HTML 全量。
  2. 將機械步驟交給 Agent 處理。
- 深層原因：
  - 架構：缺分層與摘要策略。
  - 技術：缺壓縮與 A2A Protocol。
  - 流程：缺上下文設計規範。

### Solution Design
- 解決策略：以 MCP 做分層與摘要（ListOperations 精簡 API 能力）；主 Agent 僅收斂到 operation/action/context；細節在 MCP 內層 LLM。

- 實施步驟：
  1. 確立上下文白名單
  2. 以工具輸出指示（QuickStart）
  3. 持續度量（成功率 vs Token）

- 關鍵程式碼/設定：
```txt
A2A Protocol（簡化）：
- operation: API 名稱（ID）
- action: 自然語言目標
- context: 簡述前置條件/期望
```

- 實際案例：API 探索成功完成 R1～R6；上下文縮減。
- 實測數據：探索成功率提高；Token 消耗下降（相對直接餵規格）。

Learning Points
- Context Engineering
- A2A 協定設計
- 摘要與壓縮策略

Practice Exercise
- 基礎：把一份 Swagger 摘要為 ListOperations（30 分）。
- 進階：設計 A2A schema（2 小時）。
- 專案：度量兩種上下文策略的成功率與成本（8 小時）。

Assessment Criteria
- 功能：成功執行目標操作。
- 品質：上下文精煉。
- 效能：Token/成功率表現佳。
- 創新：自動化上下文裁剪。 


-----------------------------
案例分類
-----------------------------

1) 按難度分類
- 入門級：Case 7, 10, 12, 14, 15, 16
- 中級：Case 2, 3, 4, 5, 6, 9, 13, 18
- 高級：Case 1, 8, 11, 17

2) 按技術領域分類
- 架構設計類：Case 1, 2, 8, 11, 16, 17, 18
- 效能優化類：Case 3, 4, 13, 16
- 整合開發類：Case 7, 9, 10, 14, 15, 17
- 除錯診斷類：Case 6, 11, 18
- 安全防護類：Case 9, 11（驗證下沉到 API/Domain 層）

3) 按學習目標分類
- 概念理解型：Case 1, 2, 5, 12, 18
- 技能練習型：Case 7, 9, 10, 13, 15, 16
- 問題解決型：Case 3, 4, 6, 8, 11, 14
- 創新應用型：Case 17（SpecKit/SDD 大規模治理）


-----------------------------
案例關聯圖（學習路徑建議）
-----------------------------
- 起步階段（概念與基礎）
  1. Case 1（AI-First 全貌）→ 建立整體觀與分工概念
  2. Case 2（量體與文件左移）→ 認識 Decision Table 的價值
  3. Case 5（用 Decision Table 定義測項）→ 學會從 AC 展開測試
  4. Case 7（TestKit 標準化）→ 掌握指令與產物

- 探索與上下文設計
  5. Case 8（MCP 抽象與 A2A）→ 學會分層與工具化
  6. Case 9（OAuth 內嵌）→ 讓探索更穩定
  7. Case 18（Context Engineering）→ 提升成功率與成本效益

- 產出與固化
  8. Case 10（Session Logs 規格化）→ 為產碼打基礎
  9. Case 3（成本時程優化）→ 理解 GPU→CPU 的關鍵
  10. Case 4（穩定性策略）→ 防止結果漂移

- 跨介面與 Web 能力
  11. Case 12（A11y 與可操作性）→ 讓 Web 探索可行
  12. Case 13（Web 產碼固化）→ 把探索轉為可跑回歸
  13. Case 14（共用 Test Case）→ 建立跨介面協同
  14. Case 11（跨層一致性）→ 用測試驅動規則下沉與一致

- 規模化治理
  15. Case 15（文件自動生成）→ 文件治理
  16. Case 16（探索與 CI 分離）→ 落地在交付管線
  17. Case 17（SpecKit/SDD）→ 大型團隊與長期治理

依賴關係提示：
- Case 1 是總入口，Case 2/5/7 為文件與工具基礎。
- Case 8/9/18 是探索成功的必要條件。
- Case 10 是產碼關鍵中繼物，支撐 Case 3/4/13。
- Case 12 是 Web 線路先決，之後才能進入 Case 13。
- Case 11 需要 API 與 Web 兩線皆通才可驗證。
- Case 17 建議在前述能力成熟後導入。

完整學習路徑建議：
- 基礎（1→2→5→7）→ 探索（8→9→18）→ 產碼固化（10→3→4）→ Web 與跨介面（12→13→14→11）→ 規模化治理（15→16→17）。
- 完成後可在任一新 AC 上以 TestKit 三步驟快速落地並納入 CI，持續擴大覆蓋率與降低成本。