---
layout: synthesis
title: "從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得 - faq"
synthesis_type: faq
source_post: /2025/05/01/vibe-testing-poc/
redirect_from:
  - /2025/05/01/vibe-testing-poc/faq/
---

# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Vibe Testing？
- A簡: 以「出一張嘴」的方式，從意圖到斷言全流程交給 AI，自動化完成 API 測試與報告產生。
- A詳: Vibe Testing 是一種以 LLM 的 Tool Use/Function Calling 為核心，把測試人員描述的情境（Intent）自動展開為具體的 API 呼叫與斷言（Assertion），並生成可閱讀與可機器處理的測試報告。它強調以領域層級的測試案例出發，將規格（如 OpenAPI/Swagger）與測試案例在執行前動態合併，讓 AI 自行決定要打哪些 API、怎麼組參數、如何核對預期結果，減少人工撰寫測試腳本的負擔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q12, B-Q1

A-Q2: 什麼是 Intent 與 Assertion？
- A簡: Intent 是要測什麼的意圖；Assertion 是檢查是否如預期的斷言。兩者構成測試核心。
- A詳: Intent（意圖）描述你希望驗證的商業行為或規則，如「加入超過 10 件應被拒」。Assertion（斷言）是具體檢查點，判斷實際系統行為是否滿足預期，例如「伺服器應回 400」「購物車維持空」。在 Vibe Testing 中，Intent 由人定義，Assertion 由 AI 根據過程回應自動驗證並彙整為報告。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q6, B-Q5

A-Q3: 為什麼要把測試從 Intent 到 Assertion 交給 AI？
- A簡: 降低人力密集的腳本撰寫與維護成本，縮短從需求到驗證的週期。
- A詳: 傳統自動化測試需人工將情境轉譯為精確步驟與參數，維護成本高且易隨規格變動而破碎。LLM 的 Function Calling 能理解規格、推導流程、填參數並發 API，快速將意圖轉為動作與斷言，並自動產出報告。這釋放人力去思考「該測什麼」而非「怎麼寫測試碼」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q12, B-Q1

A-Q4: 什麼是「domain 層級」的測試案例？
- A簡: 用業務語言描述情境與預期，不含具體 API 參數與技術細節。
- A詳: Domain 層級案例聚焦於商業規則與流程，例如購物車數量上限、拒絕策略與最終狀態，不涉及特定 API 名稱、路徑或參數。此層級更穩定、便於評審與長期維護，且可在執行時由 AI 依據規格自動展開成具體步驟，為跨介面（API/UI）重用鋪路。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q5, C-Q3

A-Q5: Given-When-Then（GWT）是什麼？如何應用？
- A簡: GWT 將測試分為前置(Given)、動作(When)、驗證(Then)，便於邏輯清晰與自動化。
- A詳: GWT 是行為驅動開發常用格式。Given 定義前置狀態（例：清空購物車、指定商品）；When 定義動作（例：加入 11 件）；Then 驗證預期（例：回 400、購物車為空）。在 Vibe Testing 中，GWT 是提示 LLM 正確拆解與執行測試的骨幹，並與報告結構一一對應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q4, C-Q3

A-Q6: 什麼是驗收準則（AC, Acceptance Criteria）？
- A簡: AC 是需求被視為完成的可驗證條件，主導案例設計與通過與否。
- A詳: AC 將需求落為可度量、可驗證的條件，例如「單品最多 10 件」。良好的 AC 能導引 AI 展開合適測試情境與斷言，並與報告中的成功/失敗結論直接對齊。AC 的品質決定測試的有效性與覆蓋面。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q5, D-Q5

A-Q7: 什麼是「AI Ready」的 API？為何關鍵？
- A簡: 易被 AI 理解與正確使用的 API，需有清晰領域模型與精準規格文件。
- A詳: AI Ready 意指 API 對 LLM 友善：以領域為中心的行為化接口（非純 CRUD）、高品質 OpenAPI 規格、錯誤語意一致、認證與環境一致化。這些使 LLM 能穩定推導呼叫序列與參數，減少誤用與漂移，提高測試可靠性與可維護性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q11, B-Q14

A-Q8: CRUD 風格 API 與領域導向 API 有何差異？對測試影響？
- A簡: CRUD 將決策外移、流程易發散；領域導向封裝規則，流程收斂，利於 AI 測試。
- A詳: 純 CRUD 要由呼叫端組裝商業決策，LLM 易受上下文微差影響，測試步驟與結果變動大。領域導向 API 將規則內聚，例如「加入購物車」內建上限檢查與錯誤語意，流程路徑穩定、斷言明確，AI 生成步驟更可預期，報告也更具可解釋性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q14, D-Q3

A-Q9: 什麼是 Function Calling/Tool Use？在測試中扮演什麼角色？
- A簡: 讓 LLM 呼叫外部工具/API 的機制，是 AI 自主執行測試步驟的基礎。
- A詳: Function Calling/Tool Use 透過結構化函式/工具描述（如 OpenAPI）讓 LLM 選擇並呼叫外部 API，傳遞參數並讀取回應。在測試中，LLM依據案例與規格，決定呼叫順序、構造請求、解讀回應並形成斷言與報告，實現從意圖到動作的自動化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q2, B-Q3

A-Q10: 什麼是 Semantic Kernel？為何選用？
- A簡: 微軟的 LLM 應用框架，提供 Plugins、Prompt 流程與 Function Orchestration。
- A詳: Semantic Kernel（SK）簡化 LLM 與工具的編排，支援將 OpenAPI 直接匯入成 Plugin、Auto Tool Choice、Prompt 模板、結構化輸出等。本文 Test Runner 以 SK 快速組裝最小可行架構，少量程式即可完成工具註冊、提示、執行與結果收集。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, C-Q1

A-Q11: OpenAPI/Swagger 在此方案中的角色是什麼？
- A簡: 提供精確 API 規格，讓 LLM 正確生成參數與呼叫流程的關鍵依據。
- A詳: OpenAPI 定義端點、方法、參數、Schema 與回應，SK 能將其匯入為 Plugin，LLM 因而可據此精確構造請求。無高品質規格，AI 難以可靠選擇工具與填參數，測試也易失效。理想上以 CI/CD 自動產生並維持同步。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q2, D-Q1

A-Q12: 什麼是 Test Runner？與傳統工具差異？
- A簡: 用 LLM+工具編排執行案例與產報告的最小程式，替代大量腳本維護。
- A詳: Test Runner 以 Prompt+Plugins 駕馭 LLM，從案例自動推導 API 呼叫與斷言、輸出報告。不同於傳統以腳本詳述每一步，Runner 讓 AI 依規格與情境自行決策，工程師轉而專注於 AC 與案例品質，減少細節綁定與維護成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1, C-Q5

A-Q13: 為何需要 Structured Output？Markdown 與 JSON 有何差異？
- A簡: Markdown便於人讀；JSON利於系統彙整、統計與警示，兩者常需並存。
- A詳: 測試量一大，需機器可讀的結果以做彙整、趨勢、警示與追蹤。Markdown 服務於人工審閱與溝通；JSON 服務於系統整合與自動決策。LLM 以結構化輸出（JSON Schema）可同步產兩者，使人用與機器用各得其所。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5, D-Q10

A-Q14: 測試中的「環境控制」是什麼？為何重要？
- A簡: 對使用者、語系、幣別、時區等做一致化設定，降低非功能性變因干擾。
- A詳: 若環境差異會影響 API 行為或輸出，需在測試前集中設定，並與 LLM 執行步驟解耦。可做成 Runner 的專用 Plugin（例如注入認證、文化設定），確保每次執行前備妥一致上下文，提升穩定性與可重現性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q12, C-Q6

A-Q15: 為什麼認證（OAuth2）要集中處理，而非交給 LLM？
- A簡: 認證非測試主體時應外置，避免增加不確定性，確保流程穩定與可控。
- A詳: 多數案例重點在授權後 API 行為。若把登入當步驟交給 LLM，將引入更多互動、非決定性與風險。集中處理可藉 Runner 預先取得 Access Token 並附加到每次呼叫，讓 LLM 聚焦情境與斷言，亦便於審計與故障排查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q7, D-Q4

A-Q16: 與 TDD 有何關係？
- A簡: 先寫規格與測試案例，讓測試先失敗，等功能補齊逐步轉綠燈。
- A詳: 本文示例先定義「單品上限 10」的 AC 與案例，API 尚未實作限制，Runner 執行即得「測試不過」。隨著功能補上，預期紅燈轉綠。此流程呼應 TDD 的「紅—綠—重構」節律，但測試由 LLM 執行與產報告。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q12, B-Q9

A-Q17: API 自動化與 UI 自動化的差異與共通點？
- A簡: 差異在介面；共通在從意圖展開步驟與斷言的原理。UI 需額外操作能力。
- A詳: API 自動化以 OpenAPI 為依據，Tool Use 已成熟；UI 自動化需 Browser/Computer Use 精準可控。兩者共通是以 domain 案例為起點，執行前與各自介面規格合併，由 AI 推導步驟並驗證結果。未來可望共用同組案例驗證多介面。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q4, B-Q11, C-Q10

A-Q18: 跨介面（API/Web/iOS/Android）共用案例可行性與價值？
- A簡: 以 domain 案例為核心，配合不同規格與 Runner，可驗證同一商規於多介面。
- A詳: 只要能提供對應介面的「可機器理解」規格與可靠的 Tool Use，domain 案例即可在不同 Runner 上展開為具體步驟，達到一次撰寫、多處驗證。其價值是降低案例重複、提升一致性、縮短回歸時間，利於大型多端產品線治理。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, B-Q11, C-Q10


### Q&A 類別 B: 技術原理類

B-Q1: LLM 驅動的 Test Runner 整體如何運作？
- A簡: 以 Prompt 規範任務，透過 Plugins 對接 API，LLM選擇工具、執行步驟並產報告。
- A詳: 原理: 將 GWT、約束與報告格式寫入 Prompt；匯入 OpenAPI 為 Plugins。流程: 讀入案例→LLM 解析→選擇/呼叫 API→收集回應→依 Then 斷言→輸出 Markdown/JSON。組件: Semantic Kernel、OpenAPI Plugin、環境控制 Plugin、報告器（結構化輸出）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q2, C-Q1

B-Q2: Semantic Kernel 如何把 OpenAPI 匯入為 Plugin？
- A簡: 以 ImportPluginFromOpenApi 匯入 Swagger，SK 產生工具描述供 LLM 調用。
- A詳: 原理: SK 解析 OpenAPI Schema，映射成可呼叫的 KernelFunction。步驟: 設定模型→呼叫 ImportPluginFromOpenApi→配置 HttpClient/命名空間/認證回呼。組件: Kernel、OpenApiFunctionExecutionParameters、AuthCallback。LLM 之後可依需求選用該 Plugin 的各 API。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, C-Q2

B-Q3: FunctionChoiceBehavior.Auto 的機制是什麼？
- A簡: 讓 SK 代管「何時用哪個工具」，自動進行多輪 Tool Use 與輸入輸出編排。
- A詳: 原理: 將工具選擇與多輪對話交給 SK 策略，模型可在需要時插入工具呼叫。流程: 評估訊息→計畫→挑工具→執行→整合回應→重試/下一步。組件: PromptExecutionSettings、FunctionChoiceBehavior.Auto、工具清單。可大幅降低自行實作 tool orchestration 的負擔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q1, C-Q8

B-Q4: 三段 Prompt 設計如何協同（system、testcase、report-spec）？
- A簡: system 定規則、testcase 供情境、report-spec 限輸出，三者共同約束行為。
- A詳: 原理: 以系統提示設定鐵律（GWT語意、不得臆測回應、結果標記），以使用者訊息提供案例，追加報告規格確保輸出一致。流程: 注入三段→模型解析→工具呼叫→依報告模板填值。組件: Prompt Template、KernelArguments、結構化報告 schema。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q3, C-Q5

B-Q5: LLM 如何從 GWT 推導 API 呼叫序列？
- A簡: Given 建上下文、When 映射動作到 API、Then 以回應比對預期形成斷言。
- A詳: 原理: 模型結合 OpenAPI 知識，將動作語句對齊 API 功能。流程: Given 找建置/查詢 API（建購物車、取商品）→When 執行操作（加商品、查購物車）→Then 比對回應碼/狀態。組件: 開放規格、語意規則、工具選擇策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q11, C-Q4

B-Q6: 如何在流程中傳遞 cartId、productId 等跨步驟變數？
- A簡: 由模型從回應抽取關鍵欄位，存為上下文，供後續 API 參數使用。
- A詳: 原理: 工具回應即模型的上下文來源，模型以語意對齊抽取 id/欄位。流程: CreateCart→取 cartId；GetProducts→選商品 id；AddItemToCart→使用兩者；GetCart→驗證。組件: LLM 記憶（短期上下文）、報告器同步輸出 request/response 以追蹤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q8, D-Q6

B-Q7: Test Runner 如何注入 OAuth2 Access Token？
- A簡: 以 AuthCallback 或環境 Plugin 預先完成授權，再自動附加 Authorization 標頭。
- A詳: 原理: 認證外置，Runner 先與 IdP 互動取得 Token。流程: 啟動 Runner→互動式或憑證式取得 Token→在 OpenAPI Plugin 呼叫前於 Header 加上 Bearer Token。組件: AuthCallback、環境控制 Plugin、安全儲存。避免把登入交給 LLM，減少不確定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q2, C-Q7

B-Q8: Markdown 與 JSON 報告如何同步生成？
- A簡: 模型同時遵循兩種輸出規格，分別產出人讀與機器讀的結果。
- A詳: 原理: 在 Prompt 指定兩份輸出（Markdown、JSON Schema），模型完成步驟後以同一執行脈絡填兩份模板。流程: 執行→彙整→輸出雙格式→存檔/上傳。組件: Structured Output（JSON）、報告模板、儲存與彙整服務。利於統計與審閱並行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q5, D-Q10

B-Q9: 測試結果分類規則（start_fail/exec_fail/test_fail/test_pass）如何運作？
- A簡: 依 G/W/T 三段的失敗點將結果歸類，便於定位問題層次與責任歸屬。
- A詳: 原理: 若 Given 未完成則無法執行（start_fail）；When 執行流程中斷（exec_fail）；Then 與預期不符（test_fail）；全部符合為 test_pass。流程: 模型在每步記錄 pass/fail 與原因，最後彙總。組件: 錯誤分類規則、報告器、告警閾值。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q16, D-Q5

B-Q10: 如何避免模型「臆測」API 回應或使用快取？
- A簡: 在 system prompt 明令禁止生成回應並關閉快取，強迫實打 API。
- A詳: 原理: 透過明確約束提示（不得生成 request/response、不得用 cache）與觀察器記錄 HTTP 往返。流程: 設定鐵律→開啟 HTTP logging→比對回應與報告→遇違規重試/終止。組件: system prompt 規則、HTTP 記錄、審計與校驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q2, D-Q1

B-Q11: 將 Tool Use 擴張到 UI（Browser/Computer Use）的原理？
- A簡: 以可控的瀏覽器/桌面工具作為新插件，讓 LLM 操作 UI 元素完成步驟。
- A詳: 原理: 提供 DOM/視窗操作 API 讓 LLM 以「工具」方式控 UI。流程: 載入 UI 插件→模型根據案例與 UI 規格選擇操作→取得狀態→斷言。組件: Browser Use/Computer Use、UI 規格/選擇子描述、穩定定位策略。尚需成本與精準度成熟。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, A-Q18, C-Q10

B-Q12: 為何認證與環境控制要做成獨立 Plugin？
- A簡: 降低耦合、提升可重用與可治理，並讓 LLM 聚焦業務步驟。
- A詳: 原理: 將非業務但影響行為的設定前置且標準化。流程: 啟動 Runner→設定使用者/語系/時區/幣別→附加 Token→執行案例。組件: 環境 Plugin、設定檔、審計紀錄。使測試更可重現且易於跨系統共享。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q15, C-Q6

B-Q13: API 規格與程式碼如何保持同步（CI/CD）？
- A簡: 以自動化在建置/部署階段產生與發布 Swagger，避免人工脫鉤。
- A詳: 原理: 將 OpenAPI 由程式註記或 Controller 自動產生，於 CI 產出並上傳；CD 發布版本化規格。流程: 編譯→產 Swagger→驗證→發布→Runner 拉取最新規格。組件: Swagger 產生器、CI/CD、規格託管。是 AI 測試可靠度前提。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q1, C-Q9

B-Q14: 領域導向 API 如何封裝商業規則？
- A簡: 將決策搬入 API（語意端點、錯誤碼/回應明確），以降低呼叫端複雜度。
- A詳: 原理: 以用例為中心設計端點（如 AddItemToCart）與邊界檢查（上限、庫存、授權）。流程: 定義意圖→模型→端點/回應語意→規格文件化→一致錯誤處理。組件: 用例端點、錯誤語意、OpenAPI 描述、審核流程。利於 AI 正確推導步驟。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q7, A-Q8, D-Q3

B-Q15: 測試管理與結果彙整的架構如何設計？
- A簡: 以 JSON 結構化輸出串接彙整服務，統計趨勢、告警與追蹤。
- A詳: 原理: Runner 產 JSON→集中存儲→以儀表板/查詢分析覆蓋率、失敗率、回歸趨勢。流程: 執行→收集→聚合→可視化→告警。組件: 結構化報告、儲存（DB/湖）、BI/監控、通知通道。Markdown 用於人審閱，JSON 用於治理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, C-Q5, D-Q10

B-Q16: 如何以 Plugin 模型連接其他系統（報表/工單/缺陷）？
- A簡: 將外部系統 API 也匯為 Plugins，讓 LLM 在失敗時自動報案或開單。
- A詳: 原理: 多插件協作，測試結束觸發「行動」插件（如建立 Ticket）。流程: 執行→判定失敗→填寫缺陷內容→呼叫工單 API。組件: 報表/缺陷管理 OpenAPI、SK 多插件、權限與審計。可把測試融入 DevOps 流程。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q15, D-Q10

B-Q17: 成本與延遲如何取捨（模型/批次/快取策略）？
- A簡: 選用性價比模型、批次執行、最小化上下文；避免回應臆測式快取。
- A詳: 原理: 模型如 o4-mini 兼顧 Tool Use 能力與成本；合併案例、並行執行降低牽滯；縮小 Prompt 與輸出。流程: 分層模型選擇→批次排程→觀測費用/時延→持續調優。組件: 模型路由、併發控制、費用監測。務必保留「真打 API」原則。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, D-Q9, B-Q10

B-Q18: 失敗容忍與重試策略如何設計？
- A簡: 對暫態錯誤重試，對業務失敗準確分類；流程中保留可恢復檢查點。
- A詳: 原理: 可恢復錯誤（超時、429）重試；不可恢復錯誤（權限、規格不符）及時中止並標記。流程: 觀測錯誤→分類→決策（重試/中止）→報告。組件: 重試策略（退避）、錯誤分類器、檢查點、遙測。提升穩定性與可診斷性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q7, D-Q4, B-Q9


### Q&A 類別 C: 實作應用類

C-Q1: 如何用 Semantic Kernel 建立最小可行 Test Runner？
- A簡: 建 Kernel、加 Chat 模型、匯入 OpenAPI、設定 Auto 工具選擇、Invoke Prompt 即可。
- A詳: 步驟: 1) 建 Kernel 並設定模型; 2) ImportPluginFromOpenApi; 3) 設 PromptExecutionSettings.FunctionChoiceBehavior.Auto; 4) 準備三段 Prompt（system/testcase/report）; 5) InvokePromptAsync 執行。程式碼片段:
  - AddOpenAIChatCompletion(...); 
  - await kernel.ImportPluginFromOpenApiAsync(...); 
  - new PromptExecutionSettings { FunctionChoiceBehavior = Auto() }。注意: 啟用 HTTP logging 便於驗證真打 API。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, B-Q3

C-Q2: 如何匯入 OpenAPI 並加入認證 AuthCallback？
- A簡: 使用 ImportPluginFromOpenApiAsync 並在 executionParameters 設 AuthCallback 附 Token。
- A詳: 步驟: 1) 準備 Swagger URL; 2) 呼叫 kernel.ImportPluginFromOpenApiAsync(pluginName, uri, new OpenApiFunctionExecutionParameters{ HttpClient, AuthCallback=... }); 3) 在回呼中 request.Headers.Add("Authorization","Bearer {token}")。注意: Token 取得與更新要安全、可審計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q7, A-Q11

C-Q3: 如何撰寫 System Prompt 規範執行（GWT、禁止臆測）？
- A簡: 明確定義 GWT 職責、失敗分類與輸出規範，並禁止生成 request/response。
- A詳: 步驟: 1) 在 system prompt 說明 Given/When/Then 職責與失敗標記（start/exec/test）；2) 嚴格規範不得直接生成 API 回應且禁用快取；3) 指示只接受實際 API 回應。最佳實踐: 以條列鐵律、短句清晰、與報告模板一致。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q10, A-Q5

C-Q4: 如何把測試案例作為外部輸入傳入 PromptTemplate？
- A簡: 以 KernelArguments 將 testcase 變數注入 Prompt Template 的 user 訊息段。
- A詳: 步驟: 1) 使用多段訊息模板（system/user/user）; 2) 在第二段 user 插入 {test_case}; 3) 呼叫 kernel.InvokePromptAsync<string>(template, new(settings){ ["test_case"]=案例文字 })。注意: 案例保持 domain 層級、語句清晰、避免含糊。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q4, A-Q6

C-Q5: 如何同時輸出 Markdown 與 JSON 結構化報告？
- A簡: 在 Prompt 同時規範兩種輸出或分兩次呼叫，使用 JSON Schema 保障格式。
- A詳: 步驟: 1) 在 prompt 指定 Markdown 範本（表格/條列）; 2) 另定 JSON 欄位 schema（name,result,steps...）; 3) 請模型一次產雙輸出或先 JSON 再轉 Markdown。注意: 驗證 JSON schema、防止遺漏欄位，落盤或上傳以利彙整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q15, A-Q13

C-Q6: 如何實作環境控制 Plugin（user/locale/currency/timezone）？
- A簡: 建一個非業務 Plugin 暴露設定/查詢方法，Runner 先行設定再執行案例。
- A詳: 步驟: 1) 設計 EnvironmentPlugin（SetUser, SetLocale, SetTimeZone, SetCurrency, GetContext）; 2) 在執行前呼叫設定；3) 在報告 Context 區塊輸出環境；4) AndrewShop API 呼叫時自動帶入必要標頭。注意: 與 LLM 步驟解耦、保持可重現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q14, D-Q8

C-Q7: 如何處理 OAuth2 互動式登入並自動附加 Token？
- A簡: 以外部流程換取 Access Token，Runner 緩存並自動注入 Authorization。
- A詳: 步驟: 1) 互動式導引使用者完成登入（或使用機器人帳戶流程）；2) 安全儲存短效 Token；3) 在 AuthCallback 加入 Bearer；4) Token 過期時自動刷新。注意: 不要讓 LLM 操作登入頁；記錄審計、避免洩漏憑證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, A-Q15, D-Q4

C-Q8: 如何讓 LLM 正確選用 API（降低誤用）？
- A簡: 提供高品質 OpenAPI、清晰端點語意、必要前置步驟示例與系統約束。
- A詳: 步驟: 1) 精修 OpenAPI（描述/示例/錯誤碼）；2) system prompt 強化邊界條件；3) 在 Given 示範常見前置（建購物車、取商品）；4) 設置 Auto tool choice；5) 監控與回饋修正規格。注意: 端點命名以意圖為主、避免歧義。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q5, A-Q7

C-Q9: 如何將 Test Runner 納入 CI/CD pipeline？
- A簡: 以工作節點拉取最新 Swagger 與案例，批量執行並上傳 JSON 報告統計。
- A詳: 步驟: 1) CI 產生並發布 Swagger；2) Pipeline 抓取規格與案例版本；3) 以併發策略執行 Runner；4) 上傳 JSON 到儲存與儀表板；5) 設定閾值（失敗率、關鍵用例）觸發失敗/警示。注意: 成本控制與重試策略、環境隔離。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q15, D-Q9

C-Q10: 如何初步擴充到 UI 自動化（Browser/Computer Use）？
- A簡: 引入可操作瀏覽器/桌面的插件，提供 UI 元素規格，沿用同組案例執行。
- A詳: 步驟: 1) 選擇 Browser Use/Computer Use；2) 準備 UI 規格（可選擇定位/流程描述）；3) 擴展 Runner 載入 UI 插件；4) 在 GWT 映射到 UI 操作；5) 斷言以畫面元素/狀態為準。注意: 穩定定位、等待策略、成本與安全沙箱。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, A-Q17, A-Q18


### Q&A 類別 D: 問題解決類

D-Q1: Swagger 不完整或不同步，LLM 產生錯參數怎麼辦？
- A簡: 導入 CI/CD 自動產生與發布 Swagger，增補範例與約束，版本化管理。
- A詳: 症狀: 參數缺漏/型別不符/端點不見。原因: 人工維護、缺少約束。解法: 以程式自動產生 OpenAPI、在 CI 驗證 Schema、加示例與錯誤碼說明。預防: 版本化規格、在 Runner 執行前做規格健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, A-Q11, C-Q9

D-Q2: 模型未實際呼叫 API、直接「編造」回應怎麼辦？
- A簡: 在 system prompt 禁臆測、啟用 HTTP logging，必要時加校驗器攔截。
- A詳: 症狀: 報告與伺服器日誌不符。原因: 模型為求完成輸出而猜測。解法: 明令「不得生成 request/response/快取」、檢視請求日誌、加「回應雜湊/序號」比對。預防: 以工具層強制真打 API，違規即失敗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q3, B-Q1

D-Q3: CRUD API 造成流程不穩定、測試難以收斂怎麼辦？
- A簡: 重構為領域導向 API，將規則內聚於端點與語意化錯誤。
- A詳: 症狀: 模型需組裝許多步驟且路徑分歧。原因: 業務決策外洩給呼叫端。解法: 以用例設計端點（如 AddItemToCart）、明確錯誤語意、更新 OpenAPI。預防: API 設計評審與門禁，維持 AI Ready 水準。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q14, A-Q7, A-Q8

D-Q4: OAuth2 認證失敗或 Token 過期影響測試？
- A簡: 認證外置與自動刷新，失敗時分類為 start/exec 失敗並重試。
- A詳: 症狀: 401/403、流程卡住。原因: Token 過期、時鐘偏差、範圍錯誤。解法: Runner 預先取 Token、支援自動刷新、時間同步；失敗分類為 start_fail（前置）或 exec_fail（中途）。預防: 監控 Token 壽命、使用測試專用客戶端。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q7, B-Q9

D-Q5: 測試案例描述含糊，導致結果不一致？
- A簡: 強化 AC 與 GWT 的可驗證性，用語明確、界定範圍與預期。
- A詳: 症狀: 模型選擇不同端點/路徑、斷言不一。原因: 案例語意模糊。解法: 用「可測量」的 Then、在 Given 補齊必要前置、提供關鍵術語定義。預防: 審查機制、案例範本、對齊業務詞彙。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q5, B-Q5

D-Q6: 連續呼叫中的變數傳遞錯誤（cartId/productId）？
- A簡: 在報告同步輸出每步 request/response，設上下文抽取與校驗。
- A詳: 症狀: 後續呼叫 404/400。原因: 未正確抽取 id。解法: 在 Prompt 要求顯式記錄關鍵欄位；加入「字段缺失即失敗」規則。預防: 規格示例標明 id 來源、以斷言確認 id 合法後再進下一步。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q5, B-Q9

D-Q7: API 速率限制或配額導致執行失敗？
- A簡: 實作重試與退避、排程批次、觀測速率，必要時與供應端協調配額。
- A詳: 症狀: 429/503。原因: 同時測試過多、短時間高併發。解法: 加指數退避、限流、分批；失敗分類 exec_fail 並重試。預防: 尖峰前錯開、監控配額、在 CI 動態調整並發數。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q18, B-Q17, C-Q9

D-Q8: 測試不穩定（時間/環境/非決定性）怎麼處理？
- A簡: 環境控制前置化、固定測試資料、時間凍結/模擬、縮小隨機性。
- A詳: 症狀: 時好時壞。原因: 語系/時區/資料波動。解法: 環境 Plugin 統一設定；使用種子資料；模擬時間或依相對時間；Then 放寬不可控欄位。預防: 隔離測試環境與資料、事前健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6, B-Q12

D-Q9: 成本或延遲過高如何優化？
- A簡: 選模型、合併案例批次、並行與快取規格、縮短 Prompt/輸出。
- A詳: 症狀: Pipeline 緩慢、費用飆升。原因: 模型昂貴、案例零碎。解法: 換性價比模型（如 o4-mini 類）、批次執行、共用規格快取、只輸出必要欄位。預防: 監控成本/時延、設定門檻與自動降級。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q17, C-Q9, B-Q1

D-Q10: 多人多案報告格式難統一？
- A簡: 以 JSON Schema 規範欄位，Runner 產結構化輸出並集中彙整。
- A詳: 症狀: 報告欄位不齊、難統計。原因: 自由格式。解法: 設計報告 JSON Schema（name/result/context/steps...），在 Prompt 強制；集中文件湖與儀表板。預防: 版本化 schema、驗證器把關、PR 檢查。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q15, C-Q5


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Vibe Testing？
    - A-Q2: 什麼是 Intent 與 Assertion？
    - A-Q5: Given-When-Then（GWT）是什麼？如何應用？
    - A-Q4: 什麼是「domain 層級」的測試案例？
    - A-Q6: 什麼是驗收準則（AC, Acceptance Criteria）？
    - A-Q12: 什麼是 Test Runner？與傳統工具差異？
    - A-Q9: 什麼是 Function Calling/Tool Use？在測試中扮演什麼角色？
    - A-Q10: 什麼是 Semantic Kernel？為何選用？
    - A-Q11: OpenAPI/Swagger 在此方案中的角色是什麼？
    - B-Q1: LLM 驅動的 Test Runner 整體如何運作？
    - C-Q1: 如何用 Semantic Kernel 建立最小可行 Test Runner？
    - C-Q3: 如何撰寫 System Prompt 規範執行（GWT、禁止臆測）？
    - C-Q4: 如何把測試案例作為外部輸入傳入 PromptTemplate？
    - D-Q2: 模型未實際呼叫 API、直接「編造」回應怎麼辦？
    - D-Q5: 測試案例描述含糊，導致結果不一致？

- 中級者：建議學習哪 20 題
    - A-Q7: 什麼是「AI Ready」的 API？為何關鍵？
    - A-Q8: CRUD 與領域導向 API 差異與影響
    - A-Q13: 為何需要 Structured Output？Markdown 與 JSON
    - A-Q14: 測試中的「環境控制」是什麼？
    - A-Q15: 為什麼認證（OAuth2）要集中處理？
    - A-Q16: 與 TDD 有何關係？
    - B-Q2: SK 如何把 OpenAPI 匯為 Plugin？
    - B-Q3: FunctionChoiceBehavior.Auto 的機制
    - B-Q4: 三段 Prompt 設計如何協同？
    - B-Q5: LLM 如何從 GWT 推導 API 序列？
    - B-Q6: 跨步驟變數如何傳遞？
    - B-Q7: Runner 如何注入 OAuth2 Token？
    - B-Q8: 如何同步生成雙報告？
    - B-Q9: 測試結果分類規則
    - B-Q10: 如何避免臆測/快取？
    - C-Q2: 匯入 OpenAPI 並加入 AuthCallback
    - C-Q5: 同時輸出 Markdown 與 JSON
    - D-Q1: Swagger 不完整或不同步怎麼辦？
    - D-Q4: OAuth2 認證失敗或 Token 過期？
    - D-Q6: 變數傳遞錯誤如何處理？

- 高級者：建議關注哪 15 題
    - A-Q17: API 自動化與 UI 自動化的差異與共通
    - A-Q18: 跨介面共用案例的可行性與價值
    - B-Q11: Tool Use 擴張到 UI 的原理
    - B-Q12: 認證與環境控制為何獨立 Plugin
    - B-Q13: 規格與程式碼同步（CI/CD）
    - B-Q14: 領域導向 API 封裝商業規則
    - B-Q15: 測試管理與結果彙整架構
    - B-Q16: Plugin 連接報表/工單系統
    - B-Q17: 成本與延遲取捨
    - B-Q18: 失敗容忍與重試策略
    - C-Q6: 實作環境控制 Plugin
    - C-Q9: Runner 納入 CI/CD pipeline
    - C-Q10: 擴充到 UI 自動化
    - D-Q7: 速率限制與配額風險
    - D-Q8: 測試不穩定與環境噪音対策