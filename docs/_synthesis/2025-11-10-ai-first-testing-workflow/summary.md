---
layout: synthesis
title: "AI-First Testing, 以 AI 為核心重新設計測試流程 - summary"
synthesis_type: summary
source_post: /2025/11/10/ai-first-testing-workflow/
redirect_from:
  - /2025/11/10/ai-first-testing-workflow/summary/
---

# AI-First Testing, 以 AI 為核心重新設計測試流程

## 摘要提示
- AI-First Testing: 從 AI 能力出發重構測試流程，避免僅是把 AI 塞進舊流程的局部最佳化
- 決策表 DTT: 以 Decision Table 收斂測試範圍與條件組合，先定義「對的測試」
- 左移策略: 文件維護與自動化執行左移，讓 AI 探索、由程式負責穩定重跑
- 成本與效能: 以量體與 Token 花費試算，證明「AI 直接跑測試」不可持續
- MCP 工具層: 以 MCP 隔離雜訊、抽象 API 操作，強化 Agent 探索效率與可控性
- 探索到自動化: 「探索步驟」與「產生測試程式碼」分離，將探索結果資產化
- 共用 Test Case: 同一份測試案例同時覆蓋 API 與 Web UI，降低文件與維護成本
- 無障礙設計: Web 無障礙語義成為 Agent 操作 UI 的關鍵規格與介面
- TestKit/SpecKit: 以 TestKit 封裝流程與資源，進階以 SpecKit落地生成一致程式碼
- 實作驗證: 以「安得魯小舖」API/Web 實測，驗證探索、差異與自動化可行性

## 全文重點
作者反思先前以 AI 自動執行 API 測試的嘗試，指出那是「把 AI 塞進舊流程」的局部最佳化：雖能減人力但無法應付測試量體膨脹、成本不可控、結果不穩定等結構性問題。本文提出 AI-First Testing 的新流程：以 AI 能力為中心重新分工與左移。第一步，用 Decision Table 系統化展開與收斂測試，聚焦有價值的條件與邊界；第二步，讓 AI 透過 MCP 進行「探索步驟」，從 test case 與操作規格出發，自動找出正確 API/UI 的操作序列並詳實記錄 session logs；第三步，將驗證過的探索結果轉為可重複執行的自動化測試程式碼，讓 CPU 接手回歸測試，降低成本與不確定性。

為支撐流程，作者實作 TestKit 指令集（gentest、api.run、api.gencode、web.run、web.gencode），並以「安得魯小舖」API/Web 為標的驗證。量體與成本試算顯示：若由 AI 直接反覆跑測試將產生高昂 Token 費用與時間成本；改用「一次探索 + 多次自動化」可把 40000 次 AI 任務降為 400 次探索 + 400 次產碼，其餘交由程式穩定執行。API 端透過 MCP 抽象操作（ListOperations、CreateSession、RunStep），隔離雜訊與 OAuth 等繁瑣流程，使 Agent 能專注在 test case 探索；Web 端以 Playwright MCP 驅動，並證實無障礙語義是 AI 可操作 UI 的關鍵。實測結果：API 測到空購物車應拒絕卻未拒絕（抓出缺陷）；Web 因 UI 設計在空購物車時移除結帳按鈕而通過。最後，將 session logs 與 test case 餵給生成器產出 .NET xUnit 自動化測試，4 秒內完成三項測試，驗證「探索到自動化」的成效。作者建議進一步以 SpecKit 將多源規格（OpenAPI、test management 規範、test case、API 步驟、環境變數）統合，強化跨團隊一致性。結論強調：AI 帶來的是流程變革，不只是效率改善；唯有重設分工與供應鏈，才能真正釋放 AI 的價值。

## 段落重點
### 1. AI-First Testing
作者檢討早先「用 AI 直接跑測試」的做法只是舊流程的替身，無法應對測試量體、成本與結果不穩定。以 OS 化的 Agent 視角重想測試分工：人腦負責判斷、AI 負責探索、程式碼負責重跑。以量體試算揭示問題：一個 AC 展開可達數百腳本、每年需跑上萬次，若全由 AI 執行將花費高額 Token 且緩慢。改良策略是左移：在前段用 Decision Table 收斂測試，在中段由 Agent 探索出穩定步驟，最後一次性生成自動化測試交給 CPU 重複執行。為此作者設計 TestKit 工作流與產物鏈，並以實作驗證其可行性。

### 1-2. TestKit 的構想
工作流分三步：1) 由 AC 生成 Decision Table 與 test cases（GenTest）；2) 由 Agent 探索 API/Web 的執行步驟並記錄 session logs（API.Run / WEB.Run）；3) 依 test case + 步驟 + 規格生成測試程式碼（API.GenCode / WEB.GenCode）。產物對應：決策表與測試案例（定範圍）、探索紀錄（定正確性）、測試程式（定穩定性）。技術要點：以 MCP 作為工具層、以 SpecKit 思維準備規格與上下文、將探索產物轉化為可依賴的生成輸入；如此可把 AI 能力集中用在「探索」與「產碼」兩個高價值點。

### 2. 用 Decision Table 定義「有價值的測試」
決策表能系統化列出條件組合、分類風險與排序優先級，是抑制測試通膨的首要手段。實作上，先由 AI 草擬，再由人嚴格 Review 修正條件與動作，避免誤解規則或計算錯誤。本文以購物車結帳為例，將條件精確化為各商品數量，動作包含優惠組數、總金額、總優惠、結帳金額與是否允許結帳，並涵蓋空車、門檻邊界、混合購物、超限等情境，最終展開 14 條規則及相對應 test cases。提醒：Decision Table 適合條件組合類測試，非功能性如效能、資安、併發需另設計。

### 3. 讓 AI 探索並記錄 API 的執行步驟
此步是核心：由 Agent 根據 test case 與 OpenAPI 規格，透過 MCP 抽象化工具（QuickStart、ListOperations、CreateSession、RunStep）探索出正確 API 呼叫序列。MCP 內部負責 OAuth 與參數解析、記錄 request/response 與高層步驟摘要，避免把雜訊灌入 Agent 的 context window。以空購物車案例為例，Agent 按步驟建立空車、試算、嘗試結帳並記錄預期不符結果（API 未拒絕），產出可審核的 session logs 作為後續產碼依據。此階段強調「探索是測試的一環，不是回歸的一環」。

### 4. 共用 Test Case，同時探索 API / Web
同一份 test case 可同時覆蓋 API 與 Web UI。Web 端以 Playwright MCP 操作，雖速度較慢，但可重放人機情境；實測結果顯示 Web 在空購物車時移除結帳按鈕，因此測試通過，與 API 的失敗形成對照，驗證同案不同介面的一致性與差異觀察。關鍵洞見：無障礙設計（Accessibility）是 AI 操作 UI 的「規格介面」，語義標記讓 Agent 穩定定位元素、減少上下文噪音；與以圖像辨識或原始 HTML 全量輸入相比，此路徑更務實與可擴展。

### 5. 將探索結果自動化
最後一步將探索成果資產化：以 session logs + test case + OpenAPI 生成可重跑的測試程式。本文示範以 .NET 9 + xUnit 產生 API 自動化測試，4 秒內完成三項測試，並正確揭露空購物車未拒絕的缺陷。進一步建議導入 SpecKit，把多源規格（OpenAPI、測試管理規範、test case、API 步驟、環境機密）統合，提升跨專案一致性與可維運性；在大規模使用與與 test management 整合時特別重要。

### 6. 總結
AI-First Testing 的本質是流程變革：用 Decision Table 把測試變「對」，用 AI 做「探索」，用程式做「穩定重跑」。分工原則是 Brain 判斷、GPU 探索、CPU 重複。若僅將 AI 當快工具塞入舊流程，終將遭遇成本與維運的天花板；唯有重新設計供應鏈（規格、工具、產物）與工作流，AI 的潛力才會釋放。正確的新流程沒有標準答案，需要持續實驗與落地；本文以 TestKit 的實作與「安得魯小舖」案例，證實「探索到自動化」的可行性與效益。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 軟體測試基本概念（AC/Acceptance Criteria、Test Case、Coverage、NFR）
   - 決策表（Decision Table Testing, DTT）方法與邊界值思維
   - API 基礎與 OpenAPI/Swagger 規格閱讀
   - 自動化測試框架（xUnit、Playwright）與 CI/CD 基本操作
   - AI Agent 與 MCP（Model Context Protocol）基本原理、Context Window 管理
   - OAuth2 授權流程與測試環境變數/Secret 管理

2. 核心概念及關係：
   - AI-First Testing：以 AI 的能力重新分工測試流程，改變「人/AI/程式碼」的角色定位
   - 左移策略：將「文件維護」與「自動化準備」前置，減少重複與高成本的 AI 執行
   - 決策表→Test Case→探索→自動化：四階段串接，從測試範圍到可重複執行資產
   - Context Engineering：以 MCP 抽象化 API/UI 操作，隔離雜訊，提升探索成功率
   - 跨介面複用：用同一組抽象 Test Case 同時覆蓋 API 與 Web UI

3. 技術依賴：
   - AI Agent（Copilot/Claude）依賴 MCP 工具層（API MCP、Playwright MCP）
   - MCP 內部依賴 OpenAPI 規格、Function Calling、OAuth2、Session/Logs 管理
   - 自動化測試生成依賴高品質規格（Test Case、Session Logs、API Spec）
   - 進階整合依賴 SpecKit/SDD 與 Test Management（報告、參數集中、規範一致性）
   - Web UI 探索依賴無障礙標記（Accessibility）以提升元素可辨識性

4. 應用場景：
   - 需要大規模測試覆蓋但人力有限的產品團隊
   - 同時提供 API 與 Web/App 介面的服務，欲共享測試設計
   - 高頻率發版（每週/每日）的 CI/CD 流程，加速回歸測試
   - 需控管成本與一致性的企業級測試（GPU 成本轉為 CPU 可重複執行）
   - 建置測試資產（規格+程式碼）以長期維運與審計合規

### 學習路徑建議
1. 入門者路徑：
   - 了解 AC 與 Test Case 基礎，練習用 Decision Table 展開條件組合
   - 學會閱讀 OpenAPI/Swagger，手動用 Postman/HTTP 客戶端對照操作
   - 跑通一個簡單的 xUnit 或 Playwright 測試，理解 Given-When-Then

2. 進階者路徑：
   - 實作 MCP 抽象化 API 操作（ListOperations、RunStep、CreateSession）
   - 練習 Context Engineering：控制提交給 Agent 的資訊量與雜訊隔離
   - 將探索產物（Session Logs、API Requests/Responses）標準化存檔
   - 將 Test Case 抽象化以跨介面複用（API/Web），導入 Accessibility 慣例

3. 實戰路徑：
   - 建立 TestKit 命令集（GenTest、API.Run、API.GenCode、WEB.Run、WEB.GenCode）
   - 用 AI 生成 Decision Table、Review 修正，再批次生成 Test Cases
   - 驅動 AI 探索 API/Web 步驟、落地 Session Logs，人工把關重點案例
   - 以規格生成測試程式碼，導入 CI/CD；進階導入 SpecKit 與 Test Management 整合

### 關鍵要點清單
- AI-First Testing 分工: 人判斷、AI探索、程式碼執行（左移） (優先級: 高)
- 決策表（DTT）: 用系統化條件組合鎖定「有價值的測試」 (優先級: 高)
- Test Case 抽象化: 去操作細節，支援跨介面複用（API/Web） (優先級: 高)
- Context Engineering: 控制 Agent 的資訊邊界與雜訊，提升成功率 (優先級: 高)
- MCP 抽象層: 用工具封裝 API/UI 操作，隔離規格噪音 (優先級: 高)
- 成本模型: Brain ≫ GPU ≫ CPU，將重複執行轉為程式碼（CPU） (優先級: 高)
- 探索與自動化分離: AI負責探索，生成後交由測試程式重複執行 (優先級: 高)
- Session Logs 資產化: 保留操作步驟、請求/回應，供產碼與審計 (優先級: 中)
- OpenAPI 規格品質: 操作可追溯、對應清晰，利於 Function Calling (優先級: 中)
- OAuth2 與 Secret 管理: 測試環境安全且可配置（.env/變數） (優先級: 中)
- Web Accessibility: 提升 AI 對元素辨識與操作成功率 (優先級: 高)
- 覆蓋率與邊界測試: 最小觸發、最大合法、最小違規邊界 (優先級: 中)
- 進階整合 SpecKit/SDD: 規格驅動生成，提高一致性與可維護性 (優先級: 中)
- Test Management 整合: 參數集中、報告回傳、標準化治理 (優先級: 中)
- 跨介面差異治理: API vs UI 行為差異（例：空購物車 UI 阻止 vs API 接受） (優先級: 低)