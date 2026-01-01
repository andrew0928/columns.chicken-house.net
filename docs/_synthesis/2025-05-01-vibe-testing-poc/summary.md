---
layout: synthesis
title: "從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得"
synthesis_type: summary
source_post: /2025/05/01/vibe-testing-poc/
redirect_from:
  - /2025/05/01/vibe-testing-poc/summary/
postid: 2025-05-01-vibe-testing-poc
---
# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得

## 摘要提示
- Intent→Assertion: 想把「知道要測什麼」一路自動化到「產出可判定的測試結果」。
- Tool Use / Function Calling: 把 LLM 當成會呼叫 API 的 Agent，替代人工寫 script 串接步驟與參數。
- Domain 測試案例: 以商業情境（Given/When/Then）描述要驗證的規則，刻意不綁 API 參數細節。
- Spec 驅動執行: 依賴精確 OpenAPI/Swagger，讓 AI 能決定該呼叫哪支 API、如何組 request。
- Test Runner PoC: 用 .NET Console + Microsoft Semantic Kernel Plugins 快速驗證核心可行性。
- OpenAPI→Plugin: Semantic Kernel 可直接把 Swagger 匯入成 Tools，省掉手工包裝多個函式。
- Prompt SOP: 用 system prompt 規範「不可編造 response、必須實呼叫 API」與報告格式。
- 測試報告產出: 同時產 markdown（給人看）與 json（給系統彙整/警示）的結構化輸出。
- AI Ready API: API 若只剩 CRUD、缺乏領域語意封裝，AI 執行測試會更混亂、可靠性差。
- 外圍挑戰: 認證授權、環境控制、報告彙整與規模化（MCP 等）是後續要補的重點。

## 全文重點
作者在做一個小型 PoC side project：利用 LLM 的 Function Calling/Tool Use 能力，把工程師原本需要寫腳本才能完成的 API 自動化測試流程，改成「用自然語言描述測試情境→AI 自行決定呼叫哪些 API、組出參數、執行→產出報告」。核心目標是讓測試從「Intent（測試意圖/驗收條件）」一路走到「Assertion（斷言/結果判定）」的翻譯與執行，盡可能由 AI 代勞，以減少大量人力投入在撰寫測試文件與手動/半自動執行的文書與腳本工作。

作者把整體拆解為三類輸入資訊：①你想驗證什麼（AC/Acceptance Criteria），②領域知識（流程、狀態、重要概念），③系統規格（UI 流程或 API spec、範例等）。本篇聚焦在右半部的 Test Runner：輸入已「展開」成 Given/When/Then 的 domain 測試案例（仍不含 API 細節），再結合精確 API 規格（OpenAPI/Swagger），由 LLM 推論每一步應呼叫的 API、前後資料如何傳遞（例如先建立購物車取得 cart id，再查商品清單找到可口可樂的 productId，最後加入商品並查詢購物車），並生成可閱讀的測試報告。作者也延伸想像：若未來 UI 操作型 agent 更成熟，同一份 domain 案例也可能在不同介面（API/Web/iOS/Android）上重複驗證相同商業規則。

實作上作者以「安德魯小舖」既有購物車 API 作為測試標的，準備一個刻意會失敗的案例：嘗試加入 11 件同商品，預期系統限制上限 10 件應回 400 且購物車仍為空，但實際 API 並未實作此限制，所以測試應該失敗。技術選型採 .NET Console + Microsoft Semantic Kernel，直接將 OpenAPI 匯入為 Kernel Plugin，讓 LLM 在 Auto tool choice 模式下呼叫 API；並以 system prompt 規範 Given/When/Then 的執行原則、禁止編造 API 回應、要求輸出固定格式報告。結果顯示 AI 確實逐步呼叫 API、處理 OAuth2 token、最後產出報告且判定「測試不過」，與作者預期一致，證明「用 LLM 驅動 API 測試執行與報告」在核心環節可行。

最後作者整理幾點關鍵心得：要讓這類作法成功，API 必須更「AI Ready」——用領域語意封裝行為而非只有 CRUD，並且必須有精準且能與程式同步的 API Spec（最好由 CI/CD 自動產生），否則 LLM 無法可靠組 request；此外認證授權與環境控制應標準化並在 runner 層處理，避免把不必要的環境因素混進測試步驟；當測試量放大時，報告需要可彙整的結構化輸出（如 JSON）以便統計與告警。作者表示本文只涵蓋整體想法約三成，後續會補上「如何從 AC/領域知識展開案例」與「如何規模化（含 MCP、認證等設計）」。

## 段落重點

### 1, 構想: 拿 Tool Use 來做自動化測試
作者提出「從 Intent 到 Assertion」的願景：測試最難的是掌握要驗證的意圖（AC），而不是把意圖翻成一堆細碎的操作指令；傳統自動化測試之所以人力密集，是因為電腦需要非常明確的步驟與判定點，導致大量測試文件與腳本都靠人手翻譯與串接。作者觀察到人之所以能憑意圖執行測試，是因為腦中具備領域知識與系統規格，能把意圖翻譯成行動；而這正是 LLM 的 Function Calling/Tool Use 的可用之處：在提供足夠規格（例如 API spec）時，LLM 可以自行決定要用哪些工具、怎麼組參數、怎麼依序完成任務。本文聚焦在 Test Runner 的 PoC：輸入是 domain 層級測試案例（不是直接 AC），輸出是測試報告。作者也提出更大的想像：若未來 UI 操作 agent 技術更精準且低成本，同一份 domain 案例可搭配不同介面規格與 runner，對 API/UI（Web/Android/iOS）做一致的商業規則驗證。

### 2, 實作: 準備測試案例 (domain)
作者示範一則 domain 測試案例（Given/When/Then）：測試前清空購物車、指定商品可口可樂；步驟嘗試加入 11 件並檢查購物車；預期加入時應回 400（超過 10）且購物車仍為空。作者強調此層級案例刻意不寫 API 細節，只描述商業情境與期望，目的是讓案例能在 UI 或 API 規格改動時保持穩定，降低撰寫與 review 成本。產生案例可以讓 AI 列舉，但人仍需負責「測什麼才有意義」的判斷與審核，避免把重點錯放在展開操作步驟。作者也引用敏捷三叔公的觀點：GenAI 不會讓測試消失，而是讓「思考測什麼」變得更重要，適合交給 AI 的文書與展開工作應盡快外包給 AI，人去做更有價值的決策。

### 3, 實作: 準備 API 的規格 (spec)
作者使用「安德魯小舖」的既有購物車 domain API，並依賴其 OpenAPI/Swagger 作為 AI 可理解且可精準呼叫的規格來源。作者先以「人類如何解題」的方式腦補流程，再用以設計 prompt：Given 中「清空購物車」因無 EmptyCart API，改用 CreateCart 建立新車；指定商品「可口可樂」因無搜尋 API，必須先 GetProducts 列舉後找出 productId。When 的步驟則直接對應 AddItemToCart 與 GetCart。Then 則是針對前述回應做斷言，不一定需要新 API 呼叫。這段意在說明：domain 測試案例雖不綁定細節，但在 runner 執行時仍必須結合「精確規格」把情境落地成可執行的 API 序列與資料傳遞。

### 4, 實作: 挑選對應的技術來驗證
作者以 PoC 為目標選擇 .NET Console App，採用 Microsoft Semantic Kernel（SK）+ Plugins 來實作 OpenAI Function Calling 的工具呼叫流程；是否做成 MCP 屬於「規模化推廣」階段才需要處理的問題，因此先略過。核心實作包含三部分：其一，利用 SK 內建能力將 OpenAPI Spec 直接匯入成 Kernel Plugin，省下把多支 API 手工轉成 functions 的大量工作；其二，設計 prompts（system + user messages）作為「測試 SOP」與輸出格式：system prompt 定義 Given/When/Then 的處理規則、失敗分類（無法執行/執行失敗/測試不過/測試通過），並嚴格要求不得臆造 request/response、必須實際呼叫 API；user prompt 分別提供測試案例與報告 markdown 模板；其三，設定 FunctionChoiceBehavior=Auto 讓 kernel 自動處理 tool selection 與多輪 function calling 細節，最後用 InvokePromptAsync 直接取得報告文字。執行結果顯示 AI 真的完成 API 呼叫流程，且作者補充 runner 內另外處理 OAuth2：每次測試自動取得 token 並附加到 Authorization header；最後 AI 產出報告並判定測試失敗，符合作者刻意設計的「先紅燈」TDD 式驗證（規格/案例先行，功能尚未實作限制）。

### 5, 心得
作者整理 PoC 之後的幾個關鍵結論與門檻。第一，API 設計需以領域行為封裝，若只提供 CRUD，商業邏輯與狀態控制落在呼叫端，會讓 AI 執行路徑發散、可靠性變差；因此「AI Ready」本質多在設計而非技術。第二，必須有精確且同步的 API Spec：LLM 能精準組出 URI/headers/payload 是建立在 Swagger/OpenAPI 的嚴謹描述上；若 spec 需人工維護，開發迭代下幾乎不可能與程式一致，反而讓自動化測試製造更多麻煩，應先把 CI/CD 與自動產 spec 的工程成熟度補齊。第三，認證授權與環境控制要標準化：測試通常關心「認證後的行為」，而非把登入流程當成每個案例步驟，因此作者在 runner 以 plugin 方式處理 user 與 token，並指出語系/幣別/時區等環境因素也應有類似處理模式。第四，報告需要可彙整：markdown 適合人讀，但大量測試需要 JSON 等結構化輸出做統計與告警，作者提供了同一份報告的 JSON 範例並提到 Structured Output 技巧。最後作者總結：工程師的價值在於把 AI 技術包裝成可用工具，善用 Structured Output + Function Calling + 正確 prompt 思路即可做出現成工具做不到的整合型能力；本文僅覆蓋整體構想的一部分，後續將補完「案例展開」與「規模化細節（含 MCP、認證等）」两篇。

## 資訊整理

### 知識架構圖
1. **前置知識**：學習本主題前需要掌握什麼？
   - API 自動化測試基本觀念：Given/When/Then、Assertion、測試報告、TDD 心法（先紅再綠）
   - OpenAPI / Swagger 基礎：端點、參數、Schema、認證（OAuth2）在 spec 的表達方式
   - LLM Tool Use / Function Calling 概念：模型如何「選擇工具→組參數→呼叫→讀回應→推論下一步」
   - .NET 與整合能力：Console App、HTTP 呼叫、日誌、基本 CI/CD 與文件自動生成觀念
   - Prompting 基礎：System/User message 分工、約束「不得瞎猜」、輸出格式要求（Markdown/JSON）

2. **核心概念**：本文的 3-5 個核心概念及其關係
   - **Intent → Action → Assertion**：把「要測什麼(意圖)」透過 LLM 的推論轉成「可執行的 API 行動」，最後再產出「斷言與報告」
   - **Domain 測試案例 vs Spec**：測試案例維持在「商業/領域層級」；執行時再結合「精確 API 規格」展開成可呼叫步驟
   - **AI Test Runner（LLM 驅動執行器）**：由 LLM 依案例決定要打哪些 API、如何串參數、如何判斷結果並輸出報告
   - **AI Ready API 的門檻**：要讓 AI 能穩定測試，API 必須是領域導向、文件精準、認證授權可標準化處理
   - **報告雙格式**：Markdown 給人讀；JSON 給系統彙整、統計與告警（Structured Output / JSON Schema）

3. **技術依賴**：相關技術之間的依賴關係
   - LLM（支援 Tool Use / Function Calling 的模型，如 o4-mini）
     → Semantic Kernel（負責對話/工具協調、Auto tool choice）
     → OpenAPI Spec（輸入給 SK 匯入成 Plugin 的依據）
     → API 服務（實際被呼叫的端點，含 OAuth2）
     → 測試輸出（Markdown/JSON）→ 測試彙整系統（後續規模化需求）
   - 認證授權（OAuth2）
     → Test Runner 的環境控制 Plugin（代管 token / user / locale 等 context）
     → 每次 API 呼叫自動附帶 Authorization header

4. **應用場景**：適用於哪些實際場景？
   - 以「領域情境」快速生成/執行 API 端到端（或整合）測試 PoC
   - 規格先行（或類 TDD）：先定規格與測試案例，再用 Runner 持續驗證 API 是否逐步符合
   - API First / AI First 團隊：OpenAPI 自動生成、文件同步成熟，適合導入「AI 驅動測試」
   - 未來延伸：同一份 domain 測試案例 + 不同介面規格（API/UI/Web/APP）+ 對應 Runner，做跨介面一致性驗證（本文先聚焦 API）

---

### 學習路徑建議
1. **入門者路徑**：零基礎如何開始？
   - 先補測試語言：Given/When/Then、Assertion、測試報告怎麼讀
   - 了解 OpenAPI/Swagger：能看懂端點、request/response schema、認證宣告
   - 理解 LLM Function Calling / Tool Use 的工作流程（工具選擇與參數生成）
   - 跑通最小 PoC：用現成 OpenAPI + 2~3 個測試案例，產 Markdown 報告

2. **進階者路徑**：已有基礎如何深化？
   - 用 Semantic Kernel 匯入 OpenAPI 成 Plugin（ImportPluginFromOpenApiAsync）
   - 設計 Prompt 結構：System 放 SOP 與約束、User 放 testcase、再一段要求報告格式
   - 加入 Structured Output：同時輸出 JSON（方便彙整）+ Markdown（方便閱讀）
   - 補齊環境控制：把 user/token/locale/timezone/currency 抽成 context 與專用 Plugin

3. **實戰路徑**：如何應用到實際專案？
   - 先盤點「AI Ready」缺口：API 是否領域導向、Spec 是否自動同步、認證是否一致
   - 建立測試資料與環境策略：測試帳號、token 取得、資料重置（Given 的可重複性）
   - 導入 CI：每次 build 自動產 spec、觸發 runner、收集 JSON 報告、做趨勢與告警
   - 規模化治理：測試案例版本控管、報告彙整平台、失敗分類（start_fail/exec_fail/test_fail）

---

### 關鍵要點清單
- Intent→Assertion 目標: 希望從「測試意圖」到「斷言/報告」都交給 AI 推進 (優先級: 高)
- Domain 層級測試案例: 用商業情境描述「測什麼」，避免綁死 API/UI 細節 (優先級: 高)
- Spec 驅動展開步驟: 透過精確 OpenAPI 讓 AI 能決定要打哪些端點與參數 (優先級: 高)
- LLM Tool Use/Function Calling: 讓模型能選工具、呼叫 API、讀回應再決定下一步 (優先級: 高)
- Test Runner 的定位: 輸入測試案例，輸出測試報告；PoC 先打通核心流程 (優先級: 高)
- Semantic Kernel Plugins: 把可呼叫的 API 包成工具給 LLM 使用，降低 Function Calling 雜務 (優先級: 高)
- OpenAPI→Plugin 匯入: SK 內建 ImportPluginFromOpenApiAsync 可大幅省去手工包 16 個 API (優先級: 中)
- Prompt SOP（System message）: 明確規範 Given/When/Then、失敗分類、禁止瞎猜 response (優先級: 高)
- FunctionChoiceBehavior=Auto: 交給 SK 自動處理 tool selection 與多輪呼叫流程 (優先級: 中)
- 認證授權標準化: OAuth2 不適合每次讓 AI「自己登入」；應由 Runner 統一處理並注入 token (優先級: 高)
- API 必須領域導向設計: CRUD 導致呼叫端承擔商業邏輯，AI 測試路徑易發散失控 (優先級: 高)
- Spec 必須精準且同步: 文件若靠人工維護，開發期頻繁變更會使自動化測試變成負擔 (優先級: 高)
- 報告雙格式策略: Markdown 給人看、JSON 給系統彙整統計與告警（Structured Output）(優先級: 中)
- 先紅再綠（類 TDD）: 規格/案例先寫，Runner 先驗證失敗，功能補齊後逐步轉綠 (優先級: 中)
- 未來擴展想像: 同一份 domain 案例可對 API/UI/Web/iOS/Android 用不同 Runner 驗證一致商規 (優先級: 低)