---
layout: synthesis
title: "AI-First Testing, 以 AI 為核心重新設計測試流程"
synthesis_type: summary
source_post: /2025/11/10/ai-first-testing-workflow/
redirect_from:
  - /2025/11/10/ai-first-testing-workflow/summary/
postid: 2025-11-10-ai-first-testing-workflow
---
# AI-First Testing, 以 AI 為核心重新設計測試流程

## 摘要提示
- 流程再設計: 別把 AI 塞進舊流程，從 AI 能力出發重構測試工作流，分清 Brain/GPU/CPU 的分工與邊界
- 左移策略: 將「文件維護」與「自動化執行」左移，把 AC→決策表→抽象 Test Case 先定準
- 決策表驅動: 用 Decision Table 系統化展開條件組合，收斂「有價值的測試」與邊界
- 探索不執行: 讓 AI 做「探索步驟」而非「重複執行」，降低 GPU 成本與不確定性
- 生成測試程式: 以探索留下的 session log + 規格，精準生成可重複執行的測試程式碼
- 測試資產化: Test Case 抽象化可跨介面複用，同規格覆蓋 API 與 Web UI
- MCP 分層: 以 MCP 抽象 API/Browser 操作，隔離雜訊、縮小 context、提升 Agent 穩定性
- 成本試算: 由 4 萬次 AI 任務（GPU）收斂為「探索+產碼」800 次（GPU）+ 4 萬次 CPU 測試
- 可近用性: Web UI 無障礙設計成為 AI 操作「通用介面」，提升可自動化可操控性
- TestKit 實作: 以 TestKit 封裝 gentest/api.run/web.run/api.gencode 流程，展示端到端可行性

## 全文重點
本文聚焦「AI-First Testing」：不是把 AI 充當人工自動化，而是從 AI 的長處與限制出發，重新設計測試流程。作者反思先前「vibe testing」雖可省人工，但仍屬「局部最佳化」：用 AI 去重複執行測試既昂貴又不穩定，且流程瓶頸沒有根本改變。面對 coding agent 帶來的 10x 變化，真正的瓶頸轉移到需求與規格清晰度，測試也應承接這種「流程變革」。

核心改造有三點。第一，用 Decision Table 收斂出「有價值的測試」：從 AC 展開條件組合與邊界，用一張決策表對齊範圍與優先順序，再生成保持抽象的 Test Case。如此可避免因操作介面差異而維護多份冗餘案例，將文件量由 400 份級數降至可控規模。第二，把 AI 放在「探索步驟」而不是「重複執行」，以 Agent+MCP 對照 API Spec/無障礙 UI 標記來實際嘗試、修正與驗證，留下可讀的 session logs 與請求/回應快照，供後續自動化程式碼的「規格證據」。第三，將探索結果一次性轉成穩定可回歸的測試程式（CPU 執行）。如此把 4 萬次 GPU 任務降為「探索 400 次 + 產碼 400 次（GPU）」與「執行 4 萬次（CPU）」，同時解決速度、成本與一致性問題。

作者以 TestKit 整合整套流程：GenTest 由 AC 生成 Decision Table 與 Test Case；API/Web Run 以 MCP 探索並記錄步驟；API GenCode 以 session log + 規格生成 xUnit 自動化測試。示例系統為「安得魯小舖」API/Web。實測發現：API 端空車仍可結帳（預期應拒絕）而失敗；Web UI 因實作「空車不顯示結帳」而通過。這驗證了「同一 Test Case 可覆蓋 API/UI」，也顯示探索步驟能暴露後端規則缺口。

MCP 設計是關鍵：以 QuickStart/ListOperations/CreateSession/RunStep 四工具抽象 API 操作，避免把完整 Swagger 塞進 Agent 的 context，減少雜訊（context rot），讓主 Agent 專注於「按照 Test Case 完成任務」，由 MCP 子層 LLM 進行 text-to-call 解析與 OAuth 等瑣事。Web 端則以 Playwright MCP 搭配無障礙標記（Accessibility）作為「通用介面」，顯著提升可被 AI 操控的穩定度與成功率。

最後，作者建議未來大規模推行時導入 SpecKit 與 Test Management 規格，把「API 規格、測試內規、Test Case、探索步驟、環境秘密」統一為高品質規格後再生成程式碼，以確保跨專案一致性。總結而言：人腦決策選「測什麼」，AI 探索找「怎麼測」，程式碼負責「穩定重複執行」。AI 帶來的是流程變革而不只是工具改良；唯有先行試煉新流程，碰到舊流程瓶頸時才有替代方案。

## 段落重點
### 導言：從「自動執行」到「流程變革」
作者反思半年前的 vibe testing 實驗：用 AI 取代人工執行測試雖有效，但落入舊流程的局部最佳化。受 Sam Altman「把 AI 當 OS 使用」啟發，作者轉向以 AI 能力為中心來重塑測試工作流，辨識 Brain/GPU/CPU 三種資源的邊界與分工。coding 變 10x 後，真正瓶頸移到需求/規格清晰度，測試也需重構。本文提出 AI-First Testing 策略與 TestKit 實作，聚焦三步：決定測什麼（Decision Table）、決定怎麼測（AI 探索步驟）、決定如何自動化（生成測試程式），並讓 Test Case 跨 API/Web 複用。

### 1. AI-First Testing
以 AC→Test Case→執行為軸，估算量體：單一 AC 展開可能導致 400 份腳本、一年 4 萬次執行，若全用 AI 執行成本高且不穩定。解法是「左移」：文件左移（AC→Decision Table→抽象 Test Case，減量）、自動化左移（AI 專注探索，確定方案後一次性生成測試程式，執行交給 CPU）。提出三步驟流程與對應產出（Decision Table/Test Case、Session Log/Summary、Test Code），以 TestKit 指令封裝。資源包含操作規格（API Spec/無障礙 UI）、Test Case、探索 Session Log，三者即是生成可靠測試程式的完整規格來源。

### 1-1. Workflow Design Concept
詳列測試量體與瓶頸：測項數量、探索步驟、執行次數與成本試算，證明「每次用 AI 跑測試」不可擴。提出新配置：AI 專注探索（400 次）、AI 產碼（400 次）、CPU 回歸（4 萬次），把不確定性降到可控。文件左移用 Decision Table 收斂有價值測項，Test Case 抽象化以便跨介面複用。以流程圖說明新舊差異，指出下一步要用實例驗證。

### 1-2. TestKit 的構想
參考 SpecKit，設計 TestKit 五組指令：GenTest、API.Run、API.GenCode、WEB.Run、WEB.GenCode。三步各自輸出：Decision Table/Test Case、探索 Session Log、Test Code。執行策略：AI 協助專家決策（產出 Decision Table/Test Case）、MCP 協助 AI 探索並記錄步驟、AI+SpecKit 生成大量一致的自動化測試。強調規格充分：操作規格、Test Case、操作範例（Session Log）即足以生成穩定程式碼。

### 1-3. Init TestKit
說明開發環境（VS Code + Copilot/Haiku 4.5）與範例專案（AndrewDemo.TestKitTemplate）。測試標的為「安得魯小舖」API/Web/Swagger。接下來章節將依 TestKit 工作流逐步實作：先決策表與 Test Case，再用 MCP 探索 API/Web，最後生成 API 測試程式。

### 1-4. AI-First Workflow 小結
AI-First 不只改善，更需新流程。要點：把 Agent 所需 context 與 Tools（MCP）配置好；先行試作才能在舊流程遇瓶頸時無縫轉換。本文後續以小舖 API 為例，演練整個端到端流程，驗證可行性與效益。

### 2. 用 Decision Table 定義「有價值的測試」
以 GenTest 從 AC 展開 Decision Table，核心是用系統化條件組合掌握覆蓋範圍、邊界與優先級，避免測試通膨。AI 可協助生成格式，但 Criteria/Action/Rule 需人工審視與修正（AI 常誤解商業規則或算錯）。Decision Table 適合條件組合，不適合效能/安全/壓測/狀態機/高併發等類型。

### 2-1. Prepare and Review
輸入 AC（購物車結帳、優惠規則、限購 10 件、帳密），AI 初版 Decision Table 過度簡化，經對談調整為以三商品數量為條件，產出 14 條規則，明確定義優惠組數、總金額、總優惠、結帳金額與是否允許結帳，並給每條規則的測試企圖與重要性（涵蓋空車、臨界值、超限、混合等）。過程中糾正 AI 對「第二件六折」的誤解與數值計算錯誤。

### 2-2. Generate All Test Cases
依決策表自動展開 14 份 Test Case（含 G/W/T、輸入與預期、金額明細、驗證點、API 呼叫序列與重要性）。展示 R2 範例，品質達標。此階段完成後，進入探索步驟。

### 3. 讓 AI 探索並記錄 API 的執行步驟
以 TestKit.API.Run 啟動探索：context 由 Test Case、API Spec 與 text-to-calls MCP 組成。先以 MCP 的 QuickStart/ListOperations 供 Agent 查操作，再 CreateSession（含 OAuth2），最後 RunStep（operation+action+context 抽象指令，由 MCP 內層 LLM 解析並呼叫 API）。所有 request/response 與抽象步驟記錄於 session 目錄與 session-logs.md，為後續產碼提供可追溯依據。

### 3-1. 讓 MCP 負責處理 API call
說明不直接餵 Swagger 的原因：雜訊多、塞爆 context、含不適合動作（如 OAuth2）。MCP 抽象化 API 操作，主 Agent 聚焦任務，由 MCP 子 LLM 做 text-to-call；RunStep 接收 operation/action/context，對應多次 API 呼叫並落檔。此為分層式 A2A 協作，降低 context rot 風險，強化穩定性。

### 3-2. Session Logs
以 TC-01（空車應拒絕）展示探索紀錄：建立空購物車、估價為 0、嘗試結帳時實際並未被拒絕，符合「預期應失敗」。Session Log 清楚紀錄步驟、回應與後續建議，便於人工 Review 與調整。

### 3-3. Test Suite Result
針對 R1–R6 執行結果：TC-01 失敗（API 未拒絕空車），TC-02–06 通過。AI 報告對失敗原因給出清楚判讀。所有歷程（OAuth、Spec 快照、每次呼叫）均落檔。這些材料將用於生成自動化測試程式碼。

### 3-4. AI 探索測試步驟－小結
探索是「嘗試直到找到理想步驟」，不追求靜態一次到位。該階段屬前置驗證，不應放進 CI/CD 的反覆執行；真正要反覆的是「探索完後生成的測試程式」。將探索與回歸分離，是穩定性與成本的關鍵。

### 4. 共用 Test Case，同時探索 API / Web
以 Test Case 跨介面複用，改用 TestKit.WEB.Run + Playwright MCP 操作小舖 Web。步驟包含啟動、OAuth 登入、加入商品、結帳驗證等。雖然執行較慢，但 R1–R6 全數通過；原因在 Web UI 以「空車隱藏結帳按鈕」實作了規則，和 API 的缺口形成對照，凸顯跨介面驗證價值。

### 4-1. 無障礙設計的重要性
Web 端可靠自動化的關鍵是無障礙（Accessibility）。Playwright MCP 以精簡的可存取性樹作為「通用介面」讓 Agent 感知與操作；相較逐畫面影像辨識（慢）或完整 HTML（context 過肥），無障礙標記提供高訊噪比的選擇。結論：做好無障礙，即是對 AI 友善的產品設計。

### 5. 將探索結果自動化
最後一步：以 TestKit.API.GenCode 將 session logs + 規格生成 xUnit 測試。示例生成三個測試並以環境變數提供 token，執行顯示 TC-01 失敗、TC-02/03 通過，用時 4.3 秒，達成「CPU 穩定回歸」。Web + Playwright 自動化亦可行，但足跡與例外較多，本文聚焦 API。

### 5-1. 生成 API TEST 測試專案
展示專案結構與完整 TC01 程式碼：依 Session Log 邏輯步驟（CreateCart→EstimatePrice→TryCreateCheckout→檢查行為），在 API 允許空車結帳時回報失敗，否則通過。實測證明「探索→產碼→穩定反覆執行」閉環成立。

### 5-2. 進階用途，改用 SpecKit 替代
若要規模化，建議導入 Test Management 與 SpecKit，把「API 規格、測試內規、Test Case、API 呼叫步驟、環境設定」形成高品質規格，一次性生成符合團隊標準的測試程式碼，提升跨專案一致性與可維運性。

### 6. 總結
回應開題：AI-First Testing 的關鍵在流程再設計。三原則：用 Decision Table 收斂有價值測試；讓 AI 專注探索而非執行；把探索結果固化為可重複的測試資產。以 Brain/GPU/CPU 清楚分工：人決策、AI 探索、程式碼重複。AI 帶來的是「變革」非「改善」；沒有所謂標準新流程，唯有實作與驗證才能在舊流程撞牆時拿得出替代解。文末附多篇參考資料（Sam Altman、A16Z、context-rot 研究、DTT 文章等）供延伸閱讀。

## 資訊整理

### 知識架構圖
1. 前置知識
- 了解軟體測試的基本類型與流程：功能/非功能測試、回歸測試、測試覆蓋率、邊界值分析
- 決策表（Decision Table）與 DTT 方法：如何以條件/動作/規則展開測試範圍
- API/WEB 測試基礎：OpenAPI/Swagger、OAuth2、Playwright、xUnit 等
- Agent 與 MCP 概念：LLM 驅動的探索代理、工具層（MCP）與 context 管理
- Spec 驅動開發（SDD/SpecKit）思維：以高品質規格生成穩定程式碼

2. 核心概念
- AI-First Testing：從 AI 能力出發重設測試流程，分工「人（判斷）/AI（探索）/程式碼（重複執行）」
- 左移策略：把「文件維護」與「自動化生成」前置，降低執行成本與不確定性
- Decision Table 驅動：以決策表收斂有價值的測試，抽象化 Test Case 以提升複用
- 探索與自動化分離：AI負責探索測試步驟，穩定重複交由自動化測試程式
- 共用測試資產：同一 Test Case 覆蓋 API / Web UI，以規格與探索足跡生成對應 Test Code

3. 技術依賴
- LLM/Agent 平台（Copilot/Claude 等）依賴 MCP（API/Playwright）工具層抽象化操作
- API 測試依賴 OpenAPI 規格、OAuth2 授權、Session/Log 步驟記錄
- Web 測試依賴 Playwright MCP 與無障礙（Accessibility）語意結構以穩定定位操作元素
- 程式碼生成依賴高品質規格輸入：Test Case、Session Logs、API Spec、內部測管規範
- 規格驅動（SpecKit/SDD）整合測試管理系統與環境密鑰管理

4. 應用場景
- 大量回歸測試與頻繁發版（週更/日更）下的成本與穩定性控制
- API 與 Web UI 並存的產品，期望一份測試定義覆蓋多介面
- 邊界條件與業務規則複雜（折扣、限購、授權）的功能驗證
- CI/CD 流水線中將探索成果沉澱為可重複執行的測試資產
- 導入測試管理與規格化生成以提升跨專案一致性

### 學習路徑建議
1. 入門者路徑
- 學會 Decision Table（條件/動作/規則）並能手工展開簡單業務情境
- 熟悉基本 API/Web 測試；理解 OpenAPI、OAuth2、Playwright 基礎操作
- 初步認識 Agent/MCP 角色分工與 context 管理概念
- 以小案例（單一 AC）練習從 AC → Decision Table → Test Case 的轉換

2. 進階者路徑
- 實作 AI 探索流程：用 MCP 封裝 API/Playwright，記錄 Session Logs
- 練習抽象化 Test Case（不含操作細節），提升跨介面複用率
- 建立測試覆蓋策略與優先級（邊界值、風險、價值），控制測試通膨
- 導入自動化測試生成（xUnit/Playwright），驗證穩定性與成本模型

3. 實戰路徑
- 以 SpecKit/SDD 整合測試管理規範：報告格式、環境參數、密鑰管理
- 將探索足跡（Session Logs、API Request/Response）標準化為生成輸入
- 在 CI/CD 中分離「探索（AI/GPU）」與「執行（CPU）」：探索一次、重複萬次
- 建立共用 Test Case 資產庫，覆蓋 API/Web 並維持規格一致性與版本控制

### 關鍵要點清單
- AI-First Testing 分工心法: 人判斷、AI探索、程式碼重複執行，重設流程以發揮 AI 潛力 (優先級: 高)
- 左移策略（文件與自動化）: 將 AC 展開與程式碼生成前置，降低執行階段成本與不確定性 (優先級: 高)
- Decision Table 驅動測試: 以條件/動作/規則系統性收斂有價值的測試範圍 (優先級: 高)
- 抽象化 Test Case: 減少介面耦合，讓同一案例可覆蓋 API/Web 多介面 (優先級: 高)
- AI 探索步驟（非執行）: 讓 AI 用 MCP 嘗試並記錄步驟，避免用 AI做大量回歸 (優先級: 高)
- MCP 作為工具層抽象: 以簡化 operation/action/context協議，隔離規格噪音 (優先級: 高)
- Session Logs 作為規格資產: 詳實保留 request/response與抽象步驟，供後續生成測試碼 (優先級: 中)
- OpenAPI 與 OAuth2 管理: API 測試的必要規格與授權流程需在 MCP/程式層處理 (優先級: 中)
- Web 無障礙設計（Accessibility）: 以語意結構讓 Playwright/Agent能可靠定位操作 (優先級: 高)
- 成本模型（Brain > GPU > CPU）: 以探索少次（GPU）、執行多次（CPU）取代大量AI執行 (優先級: 高)
- 覆蓋率與邊界值優先級: 以風險/價值/邊界條件排序，抑制測試通膨 (優先級: 中)
- Spec 驅動生成（SDD/SpecKit）: 多規格整合生成一致的測試碼與報告整合 (優先級: 中)
- 介面共用與一致性: 單一 Test Case 驅動 API/Web 測試，減少重複維護 (優先級: 中)
- Context 管理與降噪: 控制規格注入量，避免 LLM能力因噪音下降（context rot） (優先級: 高)
- CI/CD 實務落地: 探索在開發階段完成，回歸在流水線用CPU穩定運行 (優先級: 中)