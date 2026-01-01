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
- AI-First 思維: 不要把 AI 塞進舊流程做「局部最佳化」，而是從能力與成本結構出發重塑測試流程。
- 三段式流程: 先決定「測什麼」、再由 AI「探索怎麼測」、最後把結果「自動化成程式碼」。
- Decision Table: 用決策表收斂測試範圍與條件組合，降低文件與案例數量級並提升覆蓋掌控。
- 探索 vs 回歸: AI 適合探索與推理，不適合高頻重複執行；回歸應交給可重複的自動化測試（CPU）。
- 成本模型 Brain/GPU/CPU: 把判斷交給人腦、探索交給 AI、穩定重跑交給程式碼以壓低成本與不確定性。
- TestKit 封裝: 參考 SpecKit，把 prompts/doc/tools 封裝成 gentest/run/gencode 指令化工作流。
- MCP 抽象 API 操作: 用 MCP 隔離 swagger/認證等雜訊，避免塞爆 context window，提升 agent 成功率。
- Session Logs 資產化: 探索過程留存 session logs，供人工 review 與後續生成測試程式碼。
- 跨介面共用 Test Case: 同一份 test case 可同時用於 API 與 Web UI（探索層不同，自動化層可分流）。
- 無障礙=AI 介面: Playwright MCP 依賴 accessibility 標記，無障礙做得越好，網站越 AI-friendly、越可測。

## 全文重點
作者反思半年前「vibe testing：用 AI 直接重複跑 API 測試」的做法雖可行，但本質只是把「人力執行」換成「AI 執行」，並未改變測試 workflow，因此落入局部最佳化：測試量體一大（AC 展開多個 test case、再乘上多操作介面與 NFR），重複執行次數更驚人（例如一年上百輪），若用 AI 每次去跑，不僅昂貴、慢，結果也可能不穩定。作者借用「把 ChatGPT 當 OS」的觀點，主張應從 AI 的能力與資源邊界出發，重新配置 Brain/GPU/CPU：人負責判斷與決策、AI 負責探索與整理、程式碼負責穩定大量重跑。

基於此，他提出 AI-First Testing 的三步：第一步用 Decision Table 把驗收條件（AC）系統化展開成條件組合與預期行為，並透過人工 review 校正 AI 容易犯的規則誤解與算錯；第二步讓 AI agent 在清楚的操作規格（API spec / UI spec）與工具（MCP/Playwright）支持下「探索」可行的測試操作步驟，並把過程記錄成 session logs 供人檢核；第三步把「已驗證的 test case + 探索步驟」交給 AI 一次性生成自動化測試程式碼，讓後續回歸測試以 CPU 低成本、可重複且一致地執行。這樣 AI 任務次數由「每次回歸都要 AI」縮減為「每個案例探索一次、生成一次」，大幅降低成本與不確定性。

為了把流程落地，作者仿 SpecKit 做了 TestKit（gentest / api.run / api.gencode / web.run / web.gencode），並以「安得魯小舖」的購物車結帳折扣規則為案例：先用決策表定義 14 個規則/案例（含邊界與超限），再用 MCP 抽象化 API 操作（避免 swagger/認證雜訊影響 agent），完成探索並產出 session logs 與測試摘要；Web 端則示範同一份 test case 搭配 Playwright MCP 探索 UI 操作，並指出無障礙標記對 AI 操作與測試成功率至關重要。最後用 .NET + xUnit 示範依 session logs 生成可在 CI 重複跑的自動化 API 測試，成功抓出「空購物車仍可結帳」的缺陷。作者總結：AI 帶來的是流程變革而非單純改善，正確方向是用決策表收斂價值、用 AI 做探索、把成果資產化成可重複執行的測試程式。

## 段落重點

### 1. AI-First Testing
本章建立問題意識：直接讓 AI 取代人去「重複跑測試」會碰到量體、費用、速度、結果不一致等瓶頸，本質仍是舊流程的替身。作者以量體估算示例：1 個 AC 可能展開 10+ test cases，再乘上 4 種操作介面與 10 種 NFR，文件與腳本數量級爆炸；若每週 release、每次前後各測一次，年執行次數上萬，若用 AI 每次跑，Token 成本與時間都不合理。於是提出左移思路：把「AI 的價值」放在探索與產出，而不是高頻執行；把高頻回歸交給自動化測試程式碼（CPU）以確保一致與便宜。作者因此封裝出 TestKit 構想，流程分三步：GenTest（AC→Decision Table→Test Cases）、Run（AI+工具探索操作步驟並記錄）、GenCode（把 test case + steps 轉為可重複的 test code）。並說明成功關鍵在於：流程各階段都能產出高品質 spec（操作規格、測試案例、探索日志），使得後續生成穩定程式碼變得可控。最後以 side project（repo + 安得魯小舖 API/UI + OpenAPI）示範可行性，強調「先改善可，但更要研究新流程」，以因應舊流程瓶頸。

### 2. 用 Decision Table 定義「有價值的測試」
本章聚焦第一步：如何用最少文件決定真正有價值的測試。作者採用 Decision Table（決策表）把條件組合、預期行為系統化展開，藉此掌握覆蓋率、分類與優先順序；但也提醒決策表非萬能，對效能、安全、壓力、狀態機等測試未必適用。實作上，作者用 gentest 輸入簡化 AC：購物車結帳需依折扣規則（指定商品第二件六折）、商品單價與限購（每種最多 10）正確計算。AI 先產出「格式正確但內容粗糙」的表（Y/N 過度簡化），作者要求重構為以「各商品數量」為條件、以「優惠組數/總額/折扣/結帳金額/是否允許」為動作，並列出 14 條規則含邊界與超限。過程中也揭露 AI 風險：可能誤解規則（把第二件六折誤當第二件起都六折）或算錯數字，因此必須人工 review 校正。決策表定案後，AI 依規則批次生成 14 份 test case（Given-When-Then、輸入輸出、金額明細、驗證點、API 序列建議、重要性），把文書工作自動化，為後續探索與自動化鋪路。

### 3. 讓 AI 探索並記錄 API 的執行步驟
本章是第二步核心：AI 在「test case + API spec + MCP 工具」的 context 下探索如何正確呼叫 API 完成測試，並產出可 review、可再利用的 session logs。作者詳細說明 MCP 的必要性：若直接把 swagger/請求回應細節塞進 agent，context window 會被噪音塞爆，且 OAuth2 等機械流程不適合交給 agent；因此自建 MCP 抽象化 API 呼叫，只暴露「可用 operation 摘要」與「RunStep（operation+action+context）」介面，並在 MCP 內以另一個 LLM 負責 text→function calling→HTTP 請求，達到分層與降噪。流程上 agent 先 QuickStart、ListOperations，挑出 CreateCart/GetCart/EstimatePrice/CreateCheckout 等操作，再 CreateSession（含認證與 token），最後用 RunStep 執行並留下兩層紀錄：一是 request/response 原始足跡（可追溯），二是 session-logs.md 的抽象敘述（給人 review、給後續產 code 用）。作者用 TC-01 空購物車結帳示範：探索確實按步驟建立空車、試算為 0、嘗試結帳，並判定結果與預期不符（API 未拒絕），進而產生 suite 摘要報告與缺陷定位。並強調「探索」屬於找出正確測試步驟的前置工作，不應放在 CI/CD 回歸階段高頻執行。

### 4. 共用 Test Case, 同時探索 API / Web
本章延伸「test case 抽象化」的好處：同一份 test case 可跨操作介面復用，作者以 Web UI + Playwright MCP 示範同樣跑 R1-R6。準備的 context 改為 test case + UI spec（無障礙）+ Playwright MCP。雖然作者未像 API 那樣自建 MCP 以 session/req-res 記錄，只用 prompt + shell 產生較簡化的文字紀錄，但仍能讓 agent 自動操作瀏覽器、完成登入、加入商品、結帳等流程。結果上 Web 測試 6 個案例全通過，原因是 Web UI 端額外做了「空購物車不能結帳」（直接隱藏按鈕），與 API 行為不同，這也凸顯同一商業情境在不同介面可能存在不同驗證點與實作落差。作者特別強調無障礙設計的重要性：AI/Playwright 常遇到「按鈕就在眼前卻找不到」的問題，影像辨識太慢、讀完整 HTML 又太肥；Playwright MCP 透過 accessibility 標記把 DOM 精簡成可用結構，無障礙做得越好，網站越容易被 AI 正確理解與操作，成為「AI 時代的通用介面」。

### 5. 將探索結果自動化
本章進入第三步：把探索出的 steps 轉成可重複執行的自動化測試程式碼，將回歸從 GPU 任務移轉為 CPU 執行。作者示範 API 自動化：用 testkit.api.gencode 指定 session logs 來源，要求產生 .NET 9 + xUnit 測試專案，並規定 access token 由環境變數提供、不要在測試碼中重做 OAuth2 登入。AI 依 session logs 生成多個測試檔（如 TC01_EmptyCart），包含清楚的 Arrange/Act/Assert、log 輸出與斷言；實跑結果僅數秒即完成，TC01 如預期失敗（抓到空購物車仍可建立結帳交易的缺陷），其他案例通過，達成「快速、穩定、可重跑」目標。作者也指出若要正式導入，需面對 test management 整合、報告回拋、參數/規範一致性等需求，單靠 prompt 難以擴充；更理想做法是把內部規範與外部規格（OpenAPI）、工作流產物（test case、api call steps、secrets 管理）整理成完整 spec，改用 SDD/SpecKit 產生更一致的測試程式碼。

### 6. 總結
作者回到起點：問題不是「AI 能不能幫你跑測試」，而是「從 AI 能力出發，測試該怎麼做才不只是把 AI 塞進舊流程」。他收斂為三個結論：用 Decision Table 收斂有價值的測試；讓 AI 負責探索而非重複執行；把探索成果資產化為可重複執行的自動化測試。並用 Brain/GPU/CPU 分工概括新流程：人做判斷（測什麼）、AI 做探索（怎麼測）、程式做穩定回歸（反覆驗證）。文章強調 AI 帶來的是變革，不是改善；若只用新工具優化舊戰術，很快撞上成本/效能/維護天花板。因為「正確的新流程」仍在摸索，作者以 side project 實驗與多個外部參考（Sam Altman 訪談、context 噪音研究、無障礙趨勢、決策表測試文章等）鼓勵讀者持續試驗，及早建立能因應 AI 時代的流程設計能力。

## 資訊整理

### 知識架構圖
1. **前置知識**：學習本主題前需要掌握什麼？
   - 軟體測試基本概念：AC(驗收條件)、Test Case、回歸測試、NFR(非功能性需求)。
   - Decision Table / DTT（Decision Table Testing）：用條件組合系統化展開測試範圍與涵蓋率。
   - API 測試與規格：OpenAPI/Swagger、OAuth2/Access Token、HTTP Request/Response。
   - 自動化測試框架：API（例：.NET + xUnit）、UI（例：Playwright）。
   - AI agent 與工具鏈概念：coding agent、prompt/Spec、MCP（工具調用/分層處理/紀錄 session log）、context window 與雜訊管理。

2. **核心概念**：本文的 3-5 個核心概念及其關係
   - **AI-First Testing**：不是「把 AI 塞進舊流程」，而是以 AI 能力重新設計 workflow。
   - **三段式流程（TestKit）**：  
     (1) 用 **Decision Table** 收斂測試範圍 → 產出可複用的抽象 test case；  
     (2) 讓 **AI 探索測試步驟**（透過 MCP/工具實際操作系統）→ 產出 session logs；  
     (3) 用 **AI 一次性生成自動化測試程式碼** → 由 CPU 穩定重複執行回歸。
   - **運算資源分工**（Brain/GPU/CPU）：判斷交給人、探索交給 AI、重複執行交給程式。
   - **可複用 test case**：同一份 test case 可套用不同介面規格（API / Web UI），降低文件與案例倍增。
   - **Context Engineering / 雜訊隔離**：MCP 抽象化 API/操作細節，避免塞爆 context，提升 agent 探索成功率。

3. **技術依賴**：相關技術之間的依賴關係
   - AC/需求 →（AI + 人 review）→ Decision Table → Test Cases（抽象、介面無關）
   - Test Cases + 介面規格（OpenAPI / UI 可存取性標記）→ AI Agent 探索 → Session Logs（可追溯足跡）
   - Session Logs + Test Cases + 內部測試規範 → AI 生成 Test Code（xUnit / Playwright 等）
   - MCP（API 工具層）依賴：OpenAPI 摘要/操作清單、OAuth2 token 管理、紀錄 request/response、session 管理
   - UI 探索依賴：Playwright MCP + **Accessibility 標記**（可讓 agent 更可靠定位與操作 UI 元件）

4. **應用場景**：適用於哪些實際場景？
   - 需求/規格不夠清楚、測試量體爆炸（多介面、多 NFR、多組合）需要「收斂測試價值」的團隊。
   - 需要快速把「探索出來的操作步驟」沉澱成可重跑資產（回歸測試）的專案。
   - 同一套商業流程同時提供 API + Web/App UI，希望共用測試意圖、避免多份案例維護。
   - 需要降低「每次用 AI 直接跑測試」的成本與不穩定性（結果漂移、token 成本、耗時）。

---

### 學習路徑建議
1. **入門者路徑**：零基礎如何開始？
   1) 補測試基本詞彙：AC、Test Case、回歸測試、NFR。  
   2) 學會 Decision Table（DTT）：用 1 個小需求練習展開條件/規則/動作。  
   3) 了解 API 測試：用 Postman 或 curl 跑過 OAuth2 + 2~3 個 API 操作。  
   4) 用 LLM 先做「文件整理」：把 AC → decision table → 3~5 個 test case，練習人工 review 找錯。

2. **進階者路徑**：已有基礎如何深化？
   1) 建立「抽象 test case」寫法：介面無關（不綁 API endpoint / UI selector），把操作細節留給探索階段。  
   2) 練習「探索 vs 回歸」分離：探索階段允許 AI 試錯並產 log；回歸階段只跑 deterministic code。  
   3) 強化 context 管理：學習把規格摘要化、把噪音隔離到工具層（MCP/子代理）。  
   4) 建立可追溯的 session logs 格式：能還原步驟、對照預期、支援後續產碼。

3. **實戰路徑**：如何應用到實際專案？
   1) 從「單一 AC」挑一段最痛的流程（如結帳/折扣/權限）建立 decision table 與 10~15 個案例。  
   2) 針對 API：用 MCP/工具層封裝 OAuth2、列 operation、RunStep、request/response 紀錄。  
   3) 針對 Web：先把 UI 做好 Accessibility（role/name/label），再用 Playwright agent 探索。  
   4) 以 session logs + test case 生成測試碼（xUnit/pytest 等），把回歸測試納入 CI。  
   5) 規模化時導入 SpecKit/SDD：把「測試程式的內部規範、報告、參數、secret 管理」明文化成 spec 再生成。

---

### 關鍵要點清單
- AI-First Testing: 以 AI 能力重新設計測試流程，而非替換人力跑舊流程 (優先級: 高)
- 測試量體通膨模型: AC × 操作介面 × NFR × 測試規則，導致文件/案例倍增不可維護 (優先級: 高)
- Brain/GPU/CPU 分工: 判斷交給人、探索交給 AI、穩定重複交給程式碼以降成本提可靠性 (優先級: 高)
- Decision Table 收斂測試範圍: 用條件/動作/規則系統化展開組合並排序重要性 (優先級: 高)
- Decision Table 需要人類 review: AI 產表常出現規則誤解/算錯，表格品質直接決定後續測試品質 (優先級: 高)
- 抽象化 Test Case: 維持「測什麼」而非「怎麼操作」，讓案例可跨 API/UI 複用 (優先級: 高)
- 探索(Exploration) vs 回歸(Regression)切分: 探索是找步驟與驗證可行性，不應放進每次 CI 重跑 (優先級: 高)
- Session Logs 作為資產: 將探索過程沉澱為可追溯規格，支援後續產碼與除錯 (優先級: 高)
- MCP 抽象化 API 操作: 以 ListOperations/CreateSession/RunStep 隔離 OAuth2 與 request/response 細節，減少 context 雜訊 (優先級: 高)
- Context 雜訊管理: 過多 spec/response 會塞爆 context window，降低 agent 成功率，需分層處理 (優先級: 中)
- 成本估算觀念: 直接用 AI 跑 4 萬次測試會變昂貴且慢；轉成「少量探索 + 一次產碼 + 大量 CPU 執行」 (優先級: 高)
- UI 測試的 Accessibility 關鍵性: Playwright agent 依賴無障礙標記定位元件，提升可操作性與穩定性 (優先級: 中)
- 自動化測試碼生成策略: 用 test case + session logs + 介面規格生成 deterministic 測試碼（例 .NET+xUnit） (優先級: 高)
- 規模化需 SpecKit/內部規範: 測試碼要一致性/整合 test management 時，應把規格外顯並用 SpecKit 生成 (優先級: 中)
- 缺陷偵測示範價值: 透過流程抓到「空購物車/超限未拒絕」等未實作規則，證明流程能有效找問題 (優先級: 中)