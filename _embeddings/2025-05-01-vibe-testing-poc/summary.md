# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得

## 摘要提示
- Intent→Assertion: 以 LLM 的 Tool Use/Function Calling，嘗試把「測試意圖」自動推導為「可執行步驟＋可驗證斷言」
- Domain 測試案例: 先以商業語意撰寫 Given/When/Then，不綁定介面與參數，保留跨 API/UI 的可移植性
- API Ready: 要達到自動化，API 必須以領域導向設計，封裝商業邏輯，避免純 CRUD 帶來的控制混亂
- 精準規格文件: 需要可用的 OpenAPI/Swagger，讓模型能正確組出 URI/Headers/Payload，並隨程式自動同步
- 技術選擇: 使用 .NET Console + Microsoft Semantic Kernel，將 OpenAPI 一鍵匯入為 Plugin，驅動工具呼叫
- Prompt 策略: 以 system/user 堆疊任務規則、案例內容與報告格式，嚴禁模型「猜測」API 回應
- 認證與環境: 統一化 OAuth2 等認證流程與環境控制（語系/幣別/時區），在 Runner 層處理而非交由 AI 猜
- 結構化輸出: 同步輸出 Markdown（給人看）與 JSON（系統彙整），利於大量測試報告管理
- 實證結果: 以購物車測試範例跑通端到端流程，並如預期辨識出規格限制未實作而導致 test_fail
- 未來展望: 一套 domain-level 測試案例，搭配不同規格與 Runner，可平行驗證 API 與多端 UI

## 全文重點
本文以一個 PoC 級 Side Project 驗證：利用 LLM 的 Function Calling（Tool Use）能否把「測試意圖（Intent）」自動轉化為「可執行步驟與斷言（Assertion）」並產生測試報告。作者先以 domain 層級的 Given/When/Then 撰寫購物車情境，不預先綁定 API 參數；再把系統規格（OpenAPI/Swagger）交給 AI，讓模型自行決定呼叫何種 API、如何生成參數與組裝上下文，並以 .NET Console + Microsoft Semantic Kernel 將 OpenAPI 直接匯入為 Plugins，交由 Kernel 自動判定與調度工具。

在 Prompt 設計上，以 system prompt 界定測試鐵律：Given 處理前置、When 嚴格依步驟呼叫 API、Then 僅以實際回應驗證，不允許模型臆測或快取。用戶訊息注入測試案例；最終再以格式化要求生成 Markdown 報告（另同步輸出 JSON 以供系統化彙整）。測試範例驗證「單品數量不得超過 10 件」：Runner 依序建立新購物車、查詢商品、嘗試加入 11 件並檢視購物車，結果實際 API 未實作該限制，AI 正確判定為測試不過（test_fail），證明從「意圖到斷言」的自動化路徑可行。

實務心得強調三大前提：其一，API 必須以領域導向封裝商業邏輯而非純 CRUD，否則流程失控與 AI 不確定性會放大；其二，規格文件需精準且自動生成（OpenAPI 與程式同步），否則測試只會增混亂；其三，認證與環境（OAuth2、語系、幣別、時區）應由 Runner 統一處理，讓 AI 專注業務步驟推演。最後，作者展望：若 Browser/Computer Use 成熟，未來可讓同一套 domain 測試案例，透過不同規格與 Runner，平行驗證 API 與多端 UI，一次覆蓋一致的商業規則。本文為系列起點，後續將補充案例展開方法與規模化設計（含 MCP、認證等）。

## 段落重點
### 1, 構想: 拿 Tool Use 來做自動化測試
作者目標是把「Intent→Assertion」整段自動化：以 domain 層級意圖驅動，讓 AI 依據領域知識與系統規格，自行推論出可執行的測試步驟並完成驗證。LLM 的 Function Calling 能把「想要測什麼」翻譯為「要做哪些 API/UI 操作」，邏輯上等同先前作者以對話驅動 API 的購物案例。核心做法是將輸入拆為三塊：1) 你真正想驗證的 AC/意圖；2) 領域知識；3) 系統規格（API Spec 或 UI 規格）。Test Runner 接收的是已展開的測試案例，輸出則是結構化報告。作者並提出延伸想像：若未來 Browser/Computer Use 等 UI 操作更精準與低成本，則可用同一份 domain 測試案例，在不同介面規格（API、Web、Android、iOS）與對應 Runner 上執行，統一驗證同一套商業規則，達到跨介面的測試一致性與再利用。

### 2, 實作: 準備測試案例 (domain)
案例以購物車為場景：Given 建立空車且指定商品「可口可樂」；When 嘗試加入 11 件並檢查購物車；Then 預期加入步驟應回 400，最終購物車應為空。此案例刻意站在 domain 層思考，不指定 API 細節，目的在保持案例對介面與參數的鬆綁，提升可移植性與長期維護性。作者也刻意設定「同商品最多 10 件」的業務限制，預期目前 API 尚未實作而導致測試失敗。重點在於「懂得該測什麼」：可以用 AI 展開案例，但人的審視不可少。區隔 domain 案例與實作規格，有助於在 Runner 階段再將兩者合併，讓案例本身在 UI/API 規格變動時保持穩定，只在核心商業概念改變時才需更新。

### 3, 實作: 準備 API 的規格 (spec)
作者沿用「安德魯小舖」的 OpenAPI 規格（Swagger）作為測試目標。先以人腦拆解案例：Given 階段用「建立新購物車」替代「清空購物車」，並以「取得商品清單」找出「可口可樂」的 productId，因 API 無搜尋功能；When 階段直接用新增明細與查詢購物車兩支 API；Then 階段則只根據前述回應判斷是否符合預期。此處強調：要讓 AI 正確決定 URI、Headers 與 Payload，精準且可機器解析的 OpenAPI 規格是前提；沒有精準規格，AI 就難以可靠地執行測試，也難以在開發過程中持續回歸。

### 4, 實作: 挑選對應的技術來驗證
作者以 .NET Console 進行 PoC，聚焦驗證核心流程，不先追求 MCP 等大規模落地議題。技術主軸為 Microsoft Semantic Kernel 搭配 Plugins 來驅動 Function Calling。OpenAPI 可一鍵匯入為 Plugin，讓 Kernel 自動調度工具呼叫；再以設計良好的 Prompt 規範測試原則與輸出格式。整體流程：Kernel 載入 Plugins → 注入測試案例與規則 → Kernel 自動判斷並使用工具 → 回填實際 API 回應 → 生成測試報告。此方式讓工程師免於手寫繁瑣串接腳本，專注在案例與規則本身。

### 4-1, 將 OpenApi 匯入成為 Kernel Plugin
Semantic Kernel 內建把 OpenAPI 轉為 Plugins 的能力，大幅降低整合成本。作者示範以 o4-mini 作為模型，使用 ImportPluginFromOpenApiAsync 直接載入 Swagger，並在 executionParameters 設定認證回呼、HTTP 設定等。如此 Kernel 即能把每個 API 端點包裝成工具，交給模型在需要時呼叫。這種「OpenAPI 一鍵成工具」的做法，避免手刻 16 支 API 的函式定義與序列化樣板，讓時間花在測試邏輯與報告品質上，並為後續規模化鋪路。

### 4-2, 準備 Prompts
Prompt 分三段：1) system prompt 定義測試鐵律（Given/When/Then 的行為準則、失敗分類、嚴禁臆測 API 回應）；2) user prompt 注入測試案例（Runner 的輸入）；3) user prompt 規範輸出格式（Markdown 報告表格與結果區塊）。執行時以 PromptExecutionSettings 啟用 FunctionChoiceBehavior.Auto，讓 Kernel 自動處理工具選擇與多輪調用的雜務。此設計確保「流程嚴謹、回應可核對、報告可閱讀」，同時保障每個 request/response 皆為真實 API 回傳，避免生成式模型以想像資料填洞。

### 4-3, 測試結果報告
作者實測將所有 API 呼叫與回應列印驗證，並處理了 OAuth2 流程（Runner 於 Header 自動附上動態 Access Token）。在案例「加入 11 件可口可樂」下，實際 API 回傳 200 並加入成功，與規格「不得超過 10 件」相悖，最終 Then 判為 test_fail。測試報告同時支援 Markdown 與 JSON：前者便於人工閱讀與分享，後者方便系統彙整與統計。此例驗證了「用 domain 案例先亮紅燈，待實作補齊再轉綠」的 TDD 式思維，也證明 AI 能正確從實際回應推論結論，而非依語意想像。

### 5, 心得
作者歸納幾點實務關鍵：1) API 要以領域導向設計與封裝商業規則，純 CRUD 會讓流程不確定性上升，測試失控；2) 規格文件需精準且自動產生，與程式持續同步，否則自動化形同添亂；3) 認證與環境控制應在 Runner 層統一化，讓 AI 專注業務流程；4) 報告需同時提供 Markdown 與 JSON，以支援大量測試結果的彙整、告警與趨勢分析；5) 善用 Structured Output 與 Function Calling，加上清楚的 Prompt 思路，工程師能組裝出現有工具做不到的整合能力。最後展望：當 UI Tool Use 更成熟，同一套 domain 測試案例可跨 API/UI 平行驗證一致的商業規則。本文為系列起點，後續將補上「案例如何從 AC 展開」與「規模化（含 MCP、認證）設計」。 

### 5-1, API 必須按照領域來設計
若 API 僅是 CRUD，呼叫端需自行拼裝商業規則，AI 的不確定性會放大，測試流程難以控制。相反地，以領域行為設計 API（封裝業務邏輯、清晰語意與狀態轉換），AI 得以憑規格與文件準確地選擇端點與組裝參數。當 API 說明成為高品質的「Prompt」，整個 Function Calling 的可預測性、可重複性與可追蹤性才成立。否則，與其勉強 AI 自動化，不如先用半自動或手動測試，直到 API 設計達到 AI Ready 水準。

### 5-2, API 必須有精確的規格文件
模型要準確組出 URI/Headers/Payload，離不開精確的 OpenAPI。若規格由人工維護且無法與程式自動同步，開發過程中頻繁變更會讓測試結果失真甚至誤判。為避免「假自動化、真增負擔」，應以 CI/CD 自動產生與發佈 Swagger，確保每次測試都對應正確版本。否則，AI 的加速只會製造更多技術債與溝通成本，讓測試與文件雙雙漂移。

### 5-3, API 必須標準化處理認證授權
多數系統需要 OAuth2 等認證，建議在 Runner 層統一處理取得 Token 與注入 Header，而非把「登入」當成每個案例的測試步驟。除非認證本身是受測對象，否則應把它視為環境控制的一環，與語系、幣別、時區等設定一起抽象化，減少 AI 在非業務邏輯上的試探。如此能讓測試更穩健、可重複，並利於跨案例共享一致的前置條件。

### 5-4, 你需要有系統的彙整所有的測試報告
大量測試需要可彙整、可查詢、可告警的報告機制。建議同時輸出 Markdown（人讀）與 JSON（系統整合），並採用 Structured Output（Json Mode + Json Schema）確保資料結構穩定，便於指標彙總、歷程追蹤與品質看板。作者示例的 JSON 包含案例名稱、結果、上下文、每步 API 的 request/response 與說明，利於持續分析與自動化後續動作。

### 5-5, 小結
本 PoC 展現：以 Semantic Kernel 的 OpenAPI Plugin + 精心設計的 Prompt + 結構化輸出，就能把「出一張嘴」的意圖轉成可執行、可驗證、可追蹤的 API 測試流程。工程師若善用 Function Calling 與 Structured Output 的組合，加上清楚的架構思路，能打造現成工具難以覆蓋的跨系統整合解法。本文僅述約 30% 的全貌；後續將補充「從 AC 展開測試案例的左半部方法論」與「規模化（MCP、認證）等實作細節」，最終目標是讓同一套 domain 測試能跨 API 與多端 UI 一致驗證商業規則。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本軟體測試觀念：Given/When/Then、Assertion、AC(驗收準則)
- API 基礎：REST、HTTP、OAuth2、OpenAPI/Swagger
- LLM 能力與介面：Function Calling/Tool Use、Prompt 設計、Structured Output(JSON)
- .NET 與 Semantic Kernel 基礎：Kernel、Plugin、PromptExecutionSettings
- 產品/領域分析：以概念/流程思維撰寫 domain 層級測試案例

2. 核心概念：本文的 3-5 個核心概念及其關係
- Intent-to-Assertion：以「意圖→行動→斷言」串起自動化測試全流程
- Domain-level Test Cases：用領域語言描述情境，與技術規格解耦
- AI Ready API：以領域導向設計與精確規格(OpenAPI)讓 AI 可可靠呼叫
- Tool Use/Function Calling：將 API 規格轉成可被 LLM使用的工具集合
- Test Runner：整合 Prompt、Plugins、環境控制與報告輸出，執行端到端自動化

3. 技術依賴：相關技術之間的依賴關係
- Domain Test Cases → 需結合 → API Spec(OpenAPI) → 轉為 → Semantic Kernel Plugins
- Semantic Kernel → 依賴 → LLM(Function Calling、自動工具選擇) → 呼叫 → API(受 OAuth2/環境控制)
- Prompt(策略/格式) → 驅動 → 測試步驟執行與報告( Markdown + JSON Structured Output )
- 報告彙整系統 → 依賴 → 結構化輸出(JSON) 與測試管理平台/管線(CI/CD)

4. 應用場景：適用於哪些實際場景？
- API 自動化回歸測試與 TDD 驅動的契約驗證
- 多介面一致性驗證：同一組 domain 測試套件擴展至 API/UI/Web/Android/iOS
- 開發早期的規格驗證與 PoC 迭代
- DevOps/平台工程：大規模測試報告收斂與品質門禁
- 需要快速從業務意圖生成測試與報告的團隊

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 BDD/Gherkin 的 Given/When/Then 與基本 HTTP/API 概念
- 讀一份簡單的 Swagger，練習用 Postman/HTTPie 手打請求
- 嘗試用現成 LLM 產生簡單測試情境(純文字)，練習審閱測什麼才有意義
- 安裝 .NET 與 Semantic Kernel，跑通「從 OpenAPI 匯入 Plugin 並呼叫一個 API」的最小樣例

2. 進階者路徑：已有基礎如何深化？
- 設計 domain-level 測試案例並與 API 規格解耦，練習轉成 Prompt
- 練習 Function Choice Auto、工具鏈選擇與錯誤回復策略
- 實作 OAuth2/環境控制的專用 Plugin，讓測試邏輯與環境解耦
- 讓 LLM 同步輸出 Markdown 報告與 JSON Structured Output，接到你的測試儀表板

3. 實戰路徑：如何應用到實際專案？
- 將現有服務的 OpenAPI 接到 Test Runner，選幾個高風險路徑先落地
- 在 CI 中加入自動執行與報告收集，建立失敗警示與追蹤機制
- 逐步推動「AI Ready」重構：領域導向 API、規格自動產生、認證標準化
- 探索 UI 自動化擴展(Browser Use/Computer Use)與 MCP/Agent 架構的規模化方案

### 關鍵要點清單
- Intent-to-Assertion 流程：以意圖驅動測試並自動完成斷言的端到端思維 (優先級: 高)
- Domain-level 測試案例：用領域語言描述情境，避免與介面/參數耦合 (優先級: 高)
- AI Ready API 設計：以領域導向行為封裝而非純 CRUD，降低測試路徑發散 (優先級: 高)
- 精確 OpenAPI 規格：讓 LLM 能準確決定 URI/Headers/Payload，避免猜測 (優先級: 高)
- Semantic Kernel Plugins：以 Import OpenAPI→Plugin 快速提供可用工具 (優先級: 高)
- Function Choice Auto：交由模型自動選用工具以簡化呼叫流程與狀態管理 (優先級: 中)
- Prompt 策略與格式：System 規則、案例輸入、報告模板分離，明確邊界 (優先級: 高)
- OAuth2 與環境控制插件：統一管理認證、語系、幣別、時區等測試上下文 (優先級: 高)
- 結構化輸出(Structured Output)：同時產出 Markdown 與 JSON，服務人與系統 (優先級: 高)
- 報告彙整與可觀測性：集中化收集結果、統計與警示，支撐決策 (優先級: 中)
- TDD/契約先行：先寫規格與測試，允許早期失敗，驅動正確實作 (優先級: 中)
- UI 擴展的可行性：以相同 domain 案例，結合 Browser/Computer Use 驗證多介面 (優先級: 中)
- CICD 自動產生規格：避免人工維護 Swagger 失真，確保測試可信度 (優先級: 高)
- 錯誤處理與回復策略：對非 2xx/預期外行為給出可診斷的報告與追蹤 (優先級: 中)
- 規模化與 MCP/Agent：當跨系統與角色增多時，以 MCP/Agent 方式治理 (優先級: 低)