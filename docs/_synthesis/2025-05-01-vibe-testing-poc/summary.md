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
- Vibe Testing PoC: 以 LLM 的 Tool Use/Function Calling 驅動從意圖到斷言的 API 自動化測試，驗證概念可行
- 測試輸入分層: 將 domain 層級情境（Given/When/Then）與介面規格（OpenAPI）分離，再由 Test Runner 合併執行
- 技術路徑: 使用 .NET + Microsoft Semantic Kernel，將 OpenAPI 一鍵匯入成 Plugin，交由模型自動選工具
- 報告輸出: 同步生成人讀取的 Markdown 與系統整合用的 JSON（Structured Output）
- 認證處理: 以統一 Plugin 處理 OAuth2，將環境控制（user/locale/currency/timezone）從測試步驟抽離
- 典型案例: 購物車超過 10 件限制的負向測試，AI 正確呼叫 API 並回報「測試不過」
- AI Ready API: API 需具備領域導向設計與精確 OpenAPI 規格，否則自動化成效不佳
- 工程成熟度: 規模化需要 CICD 自動產生同步的 API Spec，否則將放大技術債
- 未來擴展: 同一組 domain 測試案例可望跨 UI/API、多端（Web/Android/iOS）以不同 Runner 執行
- 角色轉變: 測試價值在「決定測什麼」，而非撰寫腳本；工程師需擅用 Prompt、Function Calling、結構化輸出

## 全文重點
作者以 Side Project 驗證「從 Intent 到 Assertion」的自動化測試構想：讓 LLM 依據高層級的 domain 測試案例（Given/When/Then）與 API 規格（OpenAPI），自動決定應呼叫之 API、組合參數、執行步驟並生成測試報告。核心 Test Runner 以 .NET + Microsoft Semantic Kernel 開發，透過 Import OpenAPI → Plugin 的方式，讓模型以 Function Calling 自動選用工具，省去手工包裝每個端點的成本。測試報告同時輸出 Markdown（人讀）與 JSON（系統整合），並以統一 Plugin 處理 OAuth2 等環境因子，將認證、語系、幣別、時區等環境控制與測試步驟解耦。

在示範案例中，測試「購物車單品最多 10 件」的約束。Runner 自動建立空購物車、取得商品清單定位「可口可樂」ID，嘗試加入 11 件並查詢購物車；由於後端尚未實作限制，AI 確實執行 API 並回傳「測試不過」，符合先寫測試再補實作的 TDD/規格驅動思路。作者強調，要讓此法有效，API 必須 AI Ready：以領域為中心設計（而非單純 CRUD），並具備精確、可自動產生與同步的 OpenAPI 文件；否則 LLM 難以正確生成呼叫、案例容易發散，且工程管控成本過高。

技術面，作者提供三段關鍵 Prompt：系統指令定義測試鐵律與嚴禁臆測 API 結果、使用者訊息帶入測試案例、輸出報告格式要求；並以 FunctionChoiceBehavior.Auto 交由 Kernel 代管工具選擇與對話流程。執行時可清楚看到實際 API 請求與動態 Token。最後於「心得」中提出四大規模化前提：API 領域化設計、精準規格文件、認證授權標準化與環境插件化、報告結構化與彙整機制；否則 AI 反而加速技術債。展望未來，若 UI 自動操作（Browser Use/Computer Use）更穩定低成本，則同組 domain 測試案例可在不同介面規格與 Runner 下重用，實現跨 API/UI、多端一致驗證。作者並計畫續文探討「案例展開」與「規模化（含 MCP、認證）」，呼應測試角色應轉向「選擇與評估有意義的測項」以及工程師「引導 AI 把事做好」的新能力模型。

## 段落重點
### 前言與動機
作者回顧先前「安德魯小舖」的 API 驅動型 Agent 經驗，思考既然 LLM 已能可靠進行 Function Calling，是否可用於簡化 API 自動化測試腳本撰寫。PoC 成果證實可行：僅提供商業情境的正反案例，Test Runner 即能自動決定呼叫之 API 與參數並產生報告。此舉帶來「出一張嘴，測試自動跑」的體驗，也呼應業界對 DevOps 與工程流程被 AI 重塑的觀察。作者將焦點鎖定在驗證核心可行性而非產品化，並指出真正挑戰在於「讓 API AI Ready」與「如何自動化尚未 AI Ready 的 API」。

### 1, 構想: 拿 Tool Use 來做自動化測試
核心理念是讓 LLM 從「意圖（Intent）」推導至「斷言（Assertion）」：由 Given/When/Then 的需求意圖，結合領域知識與系統規格，透過 Tool Use 自動展開執行步驟與驗證。作者將輸入分成三層：要驗證什麼（AC/意圖）、領域知識（概念/流程/狀態）、精確系統規格（UI 或 API）。Test Runner 僅接收「展開後的測試案例」並輸出報告。若未來 UI 操作（Browser Use/Computer Use）更成熟，則同一組 domain 測試案例可在不同介面規格與 Runner（API/UI/多端）重用，統一驗證商業規則。

### 2, 實作: 準備測試案例 (domain)
示例案例以購物車單品上限 10 件為約束，描述在空購物車加入 11 件「可口可樂」並檢查結果，Then 預期應被拒與購物車維持空。此為純粹的 domain 情境，刻意不含技術細節，利於跨介面重用與獨立審閱。作者強調「知道該測什麼」的能力仍在於人，AI 可列舉但需人工評估。此分層能使 Runner 在執行階段再合併規格與案例，降低規格變動的影響。

### 3, 實作: 準備 API 的規格 (spec)
使用「安德魯小舖」既有 API 與公開 Swagger。作者先「腦補」人會怎麼解題，轉化為提示策略：Given 以建立新購物車取代清空，並以「取得商品清單」找出可口可樂的 productId；When 則直接呼叫加入項目與查詢購物車。Then 僅做結果判斷無須額外 API。此步驟凸顯精確 OpenAPI 的價值：模型可據規格自動產生 URI/Headers/Payload，避免臆測。

### 4, 實作: 挑選對應的技術來驗證
作者以 .NET Console App 搭配 Microsoft Semantic Kernel 開發 Runner，聚焦 PoC 而非 MCP 規模化。Kernel 可直接將 OpenAPI 匯入為 Plugin，省去手工包裝端點。接著以三段 Prompt 驅動：系統訊息定義測試鐵律與禁止臆測 API 結果；使用者訊息傳入測試案例；最後指定 Markdown 報告格式。以 FunctionChoiceBehavior.Auto 讓 Kernel 自動處理工具選擇與多輪對話。執行過程可見實際 HTTP 請求與 Authorization Header；OAuth2 以專屬 Plugin 預先處理。

### 4-1, 將 OpenApi 匯入成為 Kernel Plugin
透過 Kernel.ImportPluginFromOpenApiAsync 直接載入 Swagger，內建處理 Json Schema、Function Schema 與 OpenAPI 映射，快速把 API 暴露為 Tools。再由模型依據任務自行決定何時呼叫哪些函式。此能力大幅降低將既有 API 變成 AI 可用工具的門檻，是落地自動化的關鍵加速器。

### 4-2, 準備 Prompts
三段訊息構成流程：System 定義 Given/When/Then 的執行規範、失敗分類，以及嚴禁產生虛構的 API 回應；User 以變數注入測試案例文本；最後要求輸出包含步驟、Request/Response、判定與總結的 Markdown 報告格式。以 Prompt Template 一次組裝，並設定 Auto Tool Choice，避免手動管理 ChatHistory 與函式選用細節。

### 4-3, 測試結果報告
因購物車屬普及概念，PoC 未額外提供領域知識文件。執行時可見每次請求的實際 OAuth Token，證明非快取或臆造。最終報告顯示：加入 11 件時未回 400，購物車亦非空，判定 test_fail。這與預期一致（後端尚未實作上限），呼應先寫規格/測試、紅燈再補實作的 TDD 範式。另提供同內容的 JSON 版本，便於集中彙整與系統指標。

### 5, 心得
作者歸納四大落地前提。其一，API 必須以領域為中心設計，避免讓呼叫端承擔商業邏輯導致路徑失控；其二，需具備可自動產生且與程式碼嚴格同步的 OpenAPI，否則 LLM 難以正確呼叫；其三，認證與環境設定要標準化與插件化，將「環境控制」自測試步驟抽離；其四，報告需結構化輸出以便彙整監控。最後強調工程師價值轉向「定義與引導」，善用 Structured Output、Function Calling 與良好 Prompt 思路，便能快速拼裝跨系統整合的測試能力。作者預告後續將深入「案例展開」與「規模化（含 MCP、認證）」。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 測試基本觀念與測試設計：Given/When/Then、Assertion、AC（Acceptance Criteria）
   - API 基礎：REST、OpenAPI/Swagger、OAuth2 認證與授權
   - LLM 能力：Function Calling/Tool Use、Structured Output（JSON Mode）
   - 微軟 Semantic Kernel 與 Plugins 基本用法

2. 核心概念：
   - Intent → Assertion：從測試意圖（商業規則層級）自動推導到可執行步驟與斷言
   - AI Ready API 設計：以領域為中心的 API（封裝商業邏輯）、精準規格（OpenAPI）、標準化認證
   - Function Calling Test Runner：以 LLM 工具使用能力串起「案例展開→API 呼叫→報告輸出」
   - Prompt 與結構化輸出：以 SOP 驅動 LLM 執行策略、同時生成給人讀的 Markdown與給系統讀的 JSON
   - 測試環境控制：使用者身份、語系/幣別/時區等上下文以插件統一處理

3. 技術依賴：
   - LLM（如 OpenAI o4-mini）→ 依賴 Semantic Kernel 的 Function Choice（Auto）→ 依賴 Plugins
   - OpenAPI/Swagger → 匯入 Semantic Kernel Plugin（ImportPluginFromOpenApiAsync）→ 由 LLM具體化 URI/Headers/Payload
   - OAuth2 認證 → 測試環境插件統一附加 Token → 供 API 呼叫使用
   - Prompt Template → 指示 Given/When/Then 流程與生成報告 → Structured Output（JSON Schema/模式化）供整合

4. 應用場景：
   - API 自動化測試（端到端情境測試、TDD 支援）
   - DevOps 測試流水線：自動收集測試報告、統計與告警
   - 多介面一致性驗證（未來延伸）：用同一套 Domain Test Case 驗證 API/UI（Browser Use/Computer Use）
   - 教育與研發：示範 LLM Tool Use 與測試工程融合、PoC 驗證新流程可行性

### 學習路徑建議
1. 入門者路徑：
   - 理解 Given/When/Then 與 Assertion 的測試語法與精神
   - 熟悉 OpenAPI/Swagger、基本 REST 呼叫（GET/POST）、認識 OAuth2 概念
   - 了解 LLM 的 Function Calling 與 Structured Output 是什麼、何時適用
   - 嘗試用現成 API 撰寫 1-2 個 Domain 層級測試案例（不含技術細節）

2. 進階者路徑：
   - 使用 Microsoft Semantic Kernel，練習 Import OpenAPI 為 Plugin，設定 FunctionChoiceBehavior=Auto
   - 設計 System/User Prompts：用 SOP 描述測試原則，輸入測試案例，要求 Markdown+JSON 報告
   - 建立環境控制插件：統一注入 OAuth2 Token、語系/幣別/時區等上下文
   - 練習將測試報告結構化輸出，串接測試管理系統或統計面板

3. 實戰路徑：
   - 選取一組「AI Ready」的領域式 API，導入到 CI/CD，自動產生最新 Swagger
   - 建立測試案例集（Domain 層級）、Test Runner（Console或服務），整合報告收集與告警
   - 規模化議題：處理多使用者、多環境、多語系；評估 MCP、Browser Use/Computer Use 的跨介面測試延伸
   - 持續改進：在 PoC 之上加上版本控管、測試覆蓋率、失敗案例追蹤與回歸測試流程

### 關鍵要點清單
- Intent→Assertion 自動化：用 LLM 將商業意圖轉譯為執行步驟與斷言，縮短測試腳本撰寫成本（優先級: 高）
- Domain 層級測試案例：以領域規則撰寫案例，避免耦合具體技術細節（優先級: 高）
- AI Ready API 設計：封裝商業邏輯於 API，避免純 CRUD 導致行為不確定（優先級: 高）
- 精準 OpenAPI 規格：讓 LLM可正確生成 URI/Headers/Payload，避免手動文件不同步（優先級: 高）
- 標準化認證與環境控制：OAuth2、語系/幣別/時區等上下文由插件統一處理（優先級: 高）
- Semantic Kernel Plugins：以 ImportPluginFromOpenApiAsync 快速把 Swagger 變成可用工具（優先級: 高）
- FunctionChoiceBehavior=Auto：讓 Kernel 代管工具選擇與往返細節，降低實作複雜度（優先級: 中）
- Prompt 設計 SOP：System Prompt明確規範 Given/When/Then 流程與不可造假原則（優先級: 高）
- 實際 API 呼叫原則：禁止生成/快取回應，測試必須基於真實呼叫（優先級: 高）
- 結構化測試報告：同時輸出 Markdown（給人看）與 JSON（系統整合）（優先級: 高）
- 測試報告彙整機制：集中收集、統計與告警，支援規模化測試管理（優先級: 中）
- TDD 式工作流：先有規格與案例，讓紅燈轉綠燈驅動開發與驗證（優先級: 中）
- 介面多樣化願景：同一套案例測 API/UI/Web/Android/iOS（依賴 Browser/Computer Use）（優先級: 低）
- 開發者能力轉型：重點是「更懂如何引導 AI 把事做好」，而非單純寫程式更快（優先級: 中）
- CI/CD 與規格自動化：確保每次測試前規格與實作同步，避免技術債擴張（優先級: 高）