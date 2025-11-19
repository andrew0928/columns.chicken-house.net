# AI-First Testing, 以 AI 為核心重新設計測試流程

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 AI-First Testing？
- A簡: 以 AI 為核心重設測試流程，先用 AI探索步驟、再生成自動化程式，提升效率與一致性。
- A詳: AI-First Testing 是從 AI 的能力出發重新設計測試流程的思維。不是把 AI 當人力替代而直接執行所有測試，而是分工：讓 AI 先「探索」測試步驟、驗證情境與操作方式，然後把探索結果固化為「可重複執行的程式碼」。此流程左移文件維護（AC→Decision Table→Test Cases）與自動化設計，降低 GPU 成本與結果不一致問題，最終由程式碼（CPU）在 CI/CD 穩定回歸。核心價值在於高覆蓋、低成本與高穩定的跨介面（API/Web）測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1

A-Q2: 為何不直接用 AI 重複執行測試？
- A簡: 成本昂貴、速度偏慢、結果不穩定；應讓 AI 探索，重複執行交由程式碼。
- A詳: 直接以 AI 逐次執行測試會遇到三大問題：一是 GPU 成本高且累積測試次數巨大；二是速度不如程式化自動化；三是生成式模型的非決定性導致不同輪結果有偏差。最佳解是讓 AI 用於「探索」與「生成自動化測試程式碼」，將重複執行移交給 CPU 驅動的測試框架（如 xUnit、Playwright），兼顧性能、成本與一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q11, B-Q22

A-Q3: 在 AI 自動化語境中，什麼是「左移」？
- A簡: 把文件維護與自動化設計前置，減少後段執行成本與不確定性。
- A詳: 左移指將關鍵活動（規格澄清、決策表維護、測試設計、執行架構）前置到研發流程早期完成。AI-First Testing 中左移兩件事：一是文件左移（AC→Decision Table→抽象 Test Case），二是執行左移（先由 AI 探索步驟再生成測試碼）。這讓後段只需以程式碼穩定回歸，降低 GPU 依賴與不一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, B-Q12

A-Q4: Acceptance Criteria（AC）是什麼？
- A簡: 驗收條件，明確界定需求達成標準，是決策表與測試展開的源頭。
- A詳: AC 是從需求/用戶故事中提煉的驗收標準，界定何時視為完成。AI-First Testing 以 AC 為起點，透過 Decision Table 展開條件與行動組合形成測試範圍，再進一步轉為抽象 Test Case。良好 AC 讓 AI 易於探索、降低歧義並提升測試覆蓋與價值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q2, C-Q1

A-Q5: Decision Table 是什麼？
- A簡: 用條件與行動列出所有組合，系統化選擇測試覆蓋與優先順序。
- A詳: 決策表是一種以條件（Conditions）與動作（Actions）組合成規則（Rules）的分析工具，用於列舉所有可能的情境並清楚定義預期結果。在測試設計中，決策表能全面掌握組合覆蓋，並依風險與邊界排序測試優先。它適合商業規則與條件組合，但不適合效能、資安、併發、狀態機類型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q2, D-Q8

A-Q6: 為何用 Decision Table 收斂有價值的測試？
- A簡: 掌握全貌、辨識邊界與高風險情境，集中資源於最有價值測試。
- A詳: 測試量常呈通膨。用決策表能列出完整條件組合、識別高價值與高風險規則（如最小/最大邊界、限制破壞、混合情境），再依重要性選擇要展開的 Test Case。AI 可協助生成格式，但需人工審查確保正確計算與規則符合業務語義。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q20, C-Q2

A-Q7: AI 探索與測試執行有何不同？
- A簡: 探索是找正確操作與驗證法；執行是以程式碼穩定重複回歸。
- A詳: 探索是以 AI 根據測試案例與規格，反覆嘗試找到正確的操作序列、參數與驗證點；執行則將探索結果固化為測試程式，由 CPU 驅動在 CI/CD 穩定運行。把探索與回歸分離可兼顧靈活性與一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q1, B-Q22

A-Q8: 什麼是 TestKit？
- A簡: 封裝 AI-First Testing 的 prompts、文件與工具的工作套件。
- A詳: TestKit 是為 AI-First Testing 流程準備的套件化資源，包含指令（gentest、api.run、web.run、api.gencode、web.gencode）、必要 prompts、規格模板與工具設定。它將 AC→Decision Table→Test Case→探索→生成測試碼的供應鏈具體化，降低導入成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q17, C-Q1

A-Q9: TestKit 的核心指令有哪些？
- A簡: gentest、api.run、web.run、api.gencode、web.gencode 五組指令。
- A詳: 五組指令對應三階段兩介面：gentest 生成決策表與案例；api.run/web.run 讓 AI 探索 API/WEB 操作步驟並記錄 Session；api.gencode/web.gencode 以探索結果生成 API/WEB 的自動化測試程式碼。此分工支持跨介面共用 Test Case。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q1, C-Q3

A-Q10: MCP（Model Context Protocol）是什麼？
- A簡: 為 Agent提供工具與分層上下文管理的協議/實作框架。
- A詳: MCP 提供 Agent 外接工具、資料與行為的標準。本文用 MCP 將 API 呼叫抽象為「operation/action/context」，並內置 LLM 解析 text→function calling→HTTP。好處是隔離噪音、分層處理 OAuth2 與規格、避免主 Agent 的上下文爆炸。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q7, D-Q6

A-Q11: 什麼是 Context Engineering？
- A簡: 設計與管理 Agent 上下文內容，控制噪音與重點，提升推理品質。
- A詳: Context Engineering 指導入哪些資料、如何編排與精簡，使 Agent 能聚焦於任務。本案將冗長 swagger 規格改為 ListOperations 摘要、OAuth2 置於 MCP，避免上下文被冗餘細節污染，減少「context rot」並提升穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q7, D-Q6

A-Q12: 什麼是「context rot」？
- A簡: 上下文被雜訊與冗餘污染導致推理表現持續劣化的現象。
- A詳: Context rot 指上下文的品質因噪音、冗餘、非必要細節逐步惡化，讓 Agent 難以聚焦與準確推理。本案避免將整份 swagger 長文塞入 Agent，改用 MCP 分層、摘要操作名單與 session 記錄，維持上下文精簡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, D-Q6

A-Q13: 為何要抽象化 API 呼叫給 MCP？
- A簡: 降噪與分層，主 Agent專注測試推理，MCP負責參數與呼叫細節。
- A詳: 抽象化可用 operation 名稱呈現行為；用 action/context 說明意圖與背景。MCP 內部承擔 OAuth2、OpenAPI 對應、參數推導、HTTP 請求與足跡記錄，讓主 Agent 不被低階細節牽制，提升成功率與穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, D-Q4

A-Q14: 「Brain/GPU/CPU」資源分工的核心價值？
- A簡: 判斷交人腦、探索交AI、重複交程式，達成本與效能的最優化。
- A詳: 人腦（Brain）擅長判斷與審查，AI（GPU）擅長探索與生成，程式（CPU）擅長穩定重複。照此分工設計流程可降低成本（Brain≫GPU≫CPU）、提升速度與穩定性，避免把高成本的 AI 用在回歸執行上。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q22, D-Q1

A-Q15: 覆蓋率在此流程扮演什麼角色？
- A簡: 衡量條件組合的驗證比例，指導測試優先順序與風險控管。
- A詳: 覆蓋率顯示在決策表列出的情境中，測試實際踩到哪些組合。透過系統化展開與排序（邊界、高風險、常見場景），可聚焦有限資源到最有價值的測試上，並追蹤進度與缺口。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q20, C-Q2

A-Q16: API 測試與 Web UI 測試有何差異？
- A簡: API偏資料與協定，UI偏互動與可達性；可共用同一組抽象 Test Case。
- A詳: API 測試重資料結構、協定與授權；Web UI 測試重視使用流程、元素可定位性與可達性（Accessibility）。抽象 Test Case 將操作細節留待探索，使同一業務情境能跨介面複用，降低文件維護量。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q21, C-Q8, D-Q9

A-Q17: 為何「無障礙（Accessibility）」是 AI 操作網頁的關鍵？
- A簡: AI 依 ARIA/語義標記理解元素，能穩定定位與操作，提升成功率。
- A詳: 相較人類視覺，Agent 依賴語義化標記（ARIA role、aria-label、name、semantic HTML）與 Playwright MCP 的精簡結構。良好的無障礙設計使元素可被語義定位、行為可預期，降低影像辨識依賴與上下文負載。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q9, D-Q5

A-Q18: 什麼是 Session Log？
- A簡: 探索過程的抽象流程與 API 足跡記錄，供生成測試碼與審查。
- A詳: Session Log 包含操作序列、意圖（action/context）、HTTP request/response 快照、總結與下一步建議。它是 AI 探索的工件，連接 Test Case 與測試碼生成，為後續 SpecKit/生成器提供高品質範例與規格。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q4, C-Q5

A-Q19: 什麼是 SpecKit？何時該使用？
- A簡: 規格驅動生成工具，適合大量一致化的測試碼產出與治理。
- A詳: 當測試碼需滿足內部管理規範（命名、報告、參數注入、治理），應以 SDD/SpecKit 將規格化資料（接口規格、案例、步驟、環境）系統化，一次生成一致化測試碼。它比單純 prompt 更可控且可維運。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q16, C-Q10, D-Q10

A-Q20: SDD 與 AI-First Testing 的關聯是什麼？
- A簡: SDD提供嚴謹規格，AI依此生成穩定程式，提升一致性與治理。
- A詳: 規格驅動設計（SDD）讓 AI 有明確的輸入（接口、環境、案例、步驟、報告等），生成的程式更一致可控。AI-First Testing 在探索後以 SDD/SpecKit 規範化，避免 prompt 驅動的隨機性與偏差。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q19, B-Q16, C-Q10

A-Q21: 舊流程與新流程的本質差異？
- A簡: 舊流程以人力中心；新流程以 AI探索+程式回歸，重設分工與供應鏈。
- A詳: 舊流程只是把人換成 AI，未改變瓶頸。新流程重設資源分工與資訊供應鏈：左移文件與自動化設計、AI 專注探索、程式負責穩定回歸，並以 MCP 降噪與分層。這才真正發揮 AI 能力。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q12, D-Q1

A-Q22: 為什麼把 AI 當 OS 使用會改變測試？
- A簡: Agent 成為主要工作介面，工具與上下文視為作業層，流程需重構。
- A詳: 年輕開發者把 AI 當 OS 使用，所有工作（寫碼、文檔、自動化）在 Agent 端完成。這要求測試流程（工具、上下文、規格）以 Agent 為中心重構，形成可供 AI 高效操作的「作業層」。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, A-Q11

A-Q23: 什麼是「探索步驟」的產出物？
- A簡: 操作序列、參數、驗證點、HTTP快照與摘要，供生成測試碼。
- A詳: 探索產物包含：operation 列表、各步驟意圖與背景（action/context）、API request/response 快照、正負向斷言與誤差分析、總結與建議。這些構成測試碼生成的規格，確保回歸一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q6, C-Q5

A-Q24: 決策表的限制是什麼？
- A簡: 適合條件組合；不適合效能、資安、壓力、併發與狀態機等測試。
- A詳: 決策表善於條件/行動組合分析；但效能、資安、併發、狀態機、壓力測試需要其他方法（負載模型、風險矩陣、狀態轉移圖）。需搭配多種設計手段才能完整覆蓋不同測試目標。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q20, D-Q8, C-Q2

A-Q25: 為何要做測試成本估算？
- A簡: 指導選擇 AI探索+程式回歸策略，避免用 AI 重複執行造成通膨。
- A詳: 粗估每年測試輪次與案例數量，計算 GPU token 成本與時間負擔，通常高於程式碼回歸。估算能說服改走「AI 探索→程式化回歸」以降成本、提速與穩定，避免落入局部最佳化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q1, B-Q12

A-Q26: 為何要共用 Test Case 跨介面（API/WEB）？
- A簡: 減少重複文件維護，提升一致性與覆蓋，保障業務語義一致。
- A詳: 用抽象 Test Case 不含操作細節，讓 AI 視介面探索出步驟。這樣可同一案例覆蓋 API/WEB，減少規格份數，避免邏輯分叉。探索結果再生成各介面測試碼，保持一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q8, D-Q9

A-Q27: 為何將 OAuth2 放在 MCP 內？
- A簡: 自動處理授權與 token，避免上下文爆炸與步驟干擾。
- A詳: OAuth2 是機械性流程，塞入主 Agent 上下文增加噪音且易出錯。放進 MCP 以程式碼處理，縮短探索時間、提升成功率，且可記錄足跡供審計與重現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q7, C-Q3

A-Q28: 什麼是 A2A（Agent-to-Agent）協議在本文的意涵？
- A簡: 主 Agent 與 MCP 以 operation/action/context 三元組簡化互通。
- A詳: A2A 是 Agent 間交流約定。本文用主 Agent→MCP 的三元組：指定 operation（API 名）、action（意圖）、context（背景），由 MCP 內 LLM 解析 function calling 與 HTTP。這大幅降低上下文負荷與溝通成本。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q18, B-Q3, B-Q4


### Q&A 類別 B: 技術原理類

B-Q1: AI-First Testing 工作流程如何運作？
- A簡: AC→Decision Table→Test Case→AI探索→Session→生成測試碼→程式回歸。
- A詳: 流程分三段：1) 文件左移：由 AC 展開 Decision Table，收斂高價值規則，產生抽象 Test Case。2) 探索：主 Agent 搭配 MCP（QuickStart、ListOperations、CreateSession、RunStep），依 Test Case 與規格探索操作步驟、記錄 Session。3) 自動化：用 TestKit 的 api.gencode/web.gencode 或 SpecKit，將探索結果生成測試碼，以程式化邏輯穩定回歸。在此架構中，資料供應鏈與分層上下文管理是成功關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q3, C-Q6

B-Q2: 決策表如何展開成 Test Case？
- A簡: 根據條件/行動規則，選高價值組合轉為 Given-When-Then 案例。
- A詳: 先定義 Conditions（如各商品數量）與 Actions（金額、折扣、允許結帳等），形成 Rules。再依風險與邊界挑選要測的規則，轉為 Test Case：列出前置（Given）、步驟（When）、預期（Then）、驗證點與計算明細。AI 可生成草稿，務必人工審查計算與語義正確。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q2, D-Q8

B-Q3: MCP 工具設計與作用機制是什麼？
- A簡: 以工具提供列表、建會話、跑步驟，分層處理 API 探索與呼叫。
- A詳: MCP 提供四工具：QuickStart（使用指引）、ListOperations（可用操作摘要）、CreateSession（建會話、處理 OAuth2、資源初始化）、RunStep（執行指定 operation）。主 Agent 以 operation/action/context 呼叫 MCP，MCP 內 LLM 解析與 function calling、呼叫 HTTP，再把足跡寫入 Session，形成規格化工件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q13, B-Q4

B-Q4: Text-to-Calls 的執行流程為何？
- A簡: 解析意圖→映射操作→推導參數→function calling→HTTP→記錄。
- A詳: 主 Agent 給出 action/context，MCP 內 LLM 以規則/範例將文字意圖映射到 operation，推導所需參數（包含 id、payload）後透過 function calling 產生結構化呼叫，HTTP 客戶端執行，回應被摘要成文字並存檔 request/response。此分層減少上下文噪音並提高成功率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q6, C-Q4

B-Q5: CreateSession 內的 OAuth2 流程如何設計？
- A簡: 在 MCP 以程式碼處理授權與存 token，主 Agent 無需參與細節。
- A詳: CreateSession 建立測試會話，讀取憑證，執行 OAuth2（如 client credentials 或 authorization code），取得 access token 存於 session context，後續 RunStep 自動附帶。這避免主 Agent 被冗長授權細節污染上下文。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q27, D-Q7, C-Q3

B-Q6: Session Logs 架構與內容如何設計？
- A簡: 步驟摘要、意圖、背景、HTTP足跡、結果與後續指示，供生成與審查。
- A詳: 每一步包含：action、context、HTTP（request/response 檔名）、摘要（結果、驗證、偏差）、instructions（下一步建議）與 summary。另有原始足跡檔（openapi 快照、OAuth 日誌）。此架構支持審查與生成測試碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q5, C-Q6

B-Q7: Context 管理策略與降噪機制？
- A簡: 摘要操作、分層授權、外移冗長規格，保上下文精簡聚焦。
- A詳: 不將整份 swagger 塞入 Agent；改用 ListOperations 摘要操作名，授權流程放 MCP；HTTP 細節以檔案保留、僅摘要入上下文。此策略減少 context rot，提升推理品質與成功率。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, A-Q12, D-Q6

B-Q8: API Operation 映射與步驟範例？
- A簡: 以 CreateCart→EstimatePrice→CreateCheckout 序列驗證空車情境。
- A詳: 例：TC-01 空購物車。步驟：CreateCart 建空車→EstimatePrice 試算金額（應為 0）→CreateCheckout 檢查是否拒絕。每步錄 request/response。若行為與預期不符（如未拒絕），標記為缺陷並在測試碼中斷言失敗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q3, B-Q6

B-Q9: Web UI 探索在 Playwright MCP 的機制？
- A簡: 解析頁面為精簡結構，依無障礙語義定位元素執行操作。
- A詳: Playwright MCP 將 DOM 精簡為 YAML 式結構，保留可訪問性語義（role/name/label）與關鍵層級，使 Agent 能以語義選取器定位。這比影像辨識更高效、比完整 HTML 更輕量，提升探索穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q8, D-Q5

B-Q10: Accessibility 標記如何被 Agent 使用？
- A簡: 依 ARIA role/name/label 形成語義選取器，提升定位與操作成功率。
- A詳: 以 semantic HTML 與 ARIA 屬性讓元素具可辨識語義，例如 role="button"、aria-label="Checkout"、可計算 name。Agent 透過 Playwright 使用 getByRole/getByLabel 等語義選取器定位，避免視覺坐標不穩問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q5, B-Q9

B-Q11: 測試成本模型與資源分工架構？
- A簡: AI 探索（GPU）一次性+測試碼回歸（CPU）多次，總成本最低。
- A詳: 直接用 AI 執行 N 次測試成本高且不穩。改為：AI 探索 M 次（每案例一次或少數）+AI 生成測試碼 M 次，之後由 CPU 回歸 N 次。當 N≫M 時，總成本顯著下降且一致性提升。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q14, D-Q1

B-Q12: 左移前後流程差異？
- A簡: 前：人/AI反覆執行；後：先探索設計、後程式化回歸，穩定高效。
- A詳: 左移後文件與自動化設計在早期完成，探索產出規格工件（Session、步驟、斷言）。回歸靠程式碼，避免每次用 AI。此改造兼顧速度、成本與一致性，支撐長期維護。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q21, D-Q1

B-Q13: 跨介面案例複用架構？
- A簡: 抽象 Test Case 不含操作細節，由介面探索解構成步驟。
- A詳: Test Case 只描述業務意圖與預期（Given-When-Then）。API/WEB 各用 Agent+MCP 探索步驟與驗證，再各自生成測試碼。用此架構避免為不同界面維護多份案例。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q26, C-Q8, D-Q9

B-Q14: 生成 API 測試碼的技術原理？
- A簡: 用規格工件（OpenAPI、Test Case、Session）生成 xUnit 等測試程式。
- A詳: 把接口規格、案例、探索步驟、HTTP 快照組合為生成器輸入，產出測試類、斷言、資料準備與環境注入（token、端點）。程式碼以純 CPU 回歸，保證一致性與速度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q10, B-Q17

B-Q15: 測試碼與 Test Management 整合架構？
- A簡: 規格化命名、標籤、報告與參數治理，生成器內建標準。
- A詳: 若需對接測試管理系統（用例編號、屬性、報告格式、環境變數），應以 SDD/SpecKit 錨定規格，生成器按標準輸出，確保跨專案一致治理與報告可讀性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, C-Q10, D-Q10

B-Q16: SpecKit 與 SDD 的技術關係？
- A簡: 以規格驅動生成，讓 AI 有一致、完整的輸入與產出。
- A詳: SDD 提供嚴謹規格；SpecKit 實作規格→程式碼生成。相較 prompt 式生成，SDD/SpecKit 可保證一致性、可維護性與合規性，在測試碼治理場景尤為重要。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q20, B-Q15, C-Q10

B-Q17: Artifact 流與資料供應鏈設計？
- A簡: AC→Decision Table→Test Case→Session→OpenAPI快照→測試碼。
- A詳: 供應鏈包括：AC（需求）、Decision Table（條件/行動）、Test Case（抽象案例）、Session Logs（步驟與足跡）、OpenAPI 快照、生成測試碼。每步產物有明確質量檢核與審查責任。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q18, C-Q5

B-Q18: A2A 三元組設計背後機制？
- A簡: 最小充分訊息集，降低上下文負荷並保留意圖與背景。
- A詳: operation/action/context 保留要做什麼、為什麼、在什麼情境。MCP 內 LLM 以此推導參數、執行呼叫並記錄。此設計促進 Agent 間協作與可擴充性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q28, B-Q3, B-Q4

B-Q19: OpenAPI 規格在流程的角色？
- A簡: 提供操作參考與參數對應，MCP 摘要操作並保留快照。
- A詳: OpenAPI 是操作與資料契約的權威來源。為降噪不直接塞入上下文，MCP 提供 ListOperations 摘要，並保留原始快照供審計。生成器再用快照確保程式碼與契約一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q17, C-Q6

B-Q20: 覆蓋率計算與決策表的關聯？
- A簡: 規則數就是理論組合，已展開案例數即為覆蓋率分子。
- A詳: 決策表的規則集是理論覆蓋全集；選擇展開的規則數即為實際覆蓋分子。可依風險、重要性加權，形成加權覆蓋率，反映資源配置合理性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q2, D-Q8

B-Q21: Web 與 API 差異對 Agent 策略影響？
- A簡: API 重協定與授權；Web 重語義定位與流程，需不同 MCP 策略。
- A詳: API 探索需重參數推導與授權；Web 探索依賴無障礙語義與流程控制。MCP 設計應調整工具與摘要策略，使上下文最小充分，避免冗餘。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q9, C-Q8

B-Q22: 程式化自動化如何保證重複一致性？
- A簡: 測試碼固化步驟與斷言，脫離模型不確定性，CPU 穩定回歸。
- A詳: 將探索步驟與驗證點固化成測試程式，環境由變數注入避免硬編碼。回歸由測試框架執行，杜絕模型隨機性，保證每輪一致、可比對與可審計。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, C-Q7, D-Q10


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 TestKit.GenTest 建立購物車決策表？
- A簡: 撰寫 AC，執行 gentest，生成 Decision Table 與初始 Test Cases。
- A詳: 步驟：1) 在 TestKit 中撰寫 AC（如折扣規則、商品清單、限制）。2) 呼叫 /testkit.gentest，AI 產出 Decision Table（條件/動作/規則）與測試企圖分類。3) 人工審查與修正計算與語義，定案後保存 decision-table.md。注意：AI 常算錯折扣或誤解規則，務必核對邊界。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q2, D-Q8

C-Q2: 如何審查與修正 Decision Table？
- A簡: 核對條件/動作定義、邊界值與計算公式，修訂後重展案例。
- A詳: 步驟：1) 檢查 Conditions/Actions 是否貼近業務域。2) 逐規則驗算金額、折扣、允許判定。3) 補足最小/最大邊界、違規與混合情境。4) 修訂表後用 gentest 展開所有 Test Case，形成 tc-xx 檔。注意：標註重要性以利後續優先執行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q20, D-Q8

C-Q3: 如何設定 MCP 並執行 TestKit.API.Run？
- A簡: 安裝 MCP，配置 OAuth 憑證，執行 /testkit.api.run 開始探索。
- A詳: 步驟：1) 安裝 MCP 並註冊工具（QuickStart、ListOperations、CreateSession、RunStep）。2) 準備 OAuth2 憑證於環境或配置檔。3) 在 Agent 執行 /testkit.api.run 指定要跑的規則集（如 R1-R6）。4) MCP 會建 session、列操作、依 Test Case 探索並記錄。注意：端點與 token 需有效，避免 401/403。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q5, D-Q7

C-Q4: 如何為 API 探索建立 Session 並記錄足跡？
- A簡: 呼叫 CreateSession，MCP 內完成授權並初始化會話目錄。
- A詳: 步驟：1) 在 /testkit.api.run 中讓 Agent 先用 CreateSession。2) MCP 讀憑證，完成 OAuth2，保存 access token。3) 每次 RunStep 寫入 session-logs.md 及 HTTP 快照檔（api-request/response）。4) 結束時回報摘要。注意：session 命名含日期場次便於回溯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q5, A-Q18

C-Q5: 如何從 Session Logs 萃取 API 步驟成規格？
- A簡: 摘出操作序列、參數與斷言，成為生成測試碼的輸入。
- A詳: 步驟：1) 讀 session-logs.md 的 action/context 摘要。2) 對照 HTTP 快照，確立參數與期望回應。3) 蒐集斷言（成功/失敗訊息、金額、折扣、允許判定）。4) 整理成生成器所需規格。注意：含已知缺陷亦需轉為負向斷言。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q14, D-Q3

C-Q6: 如何生成 .NET xUnit 的 API 測試碼？
- A簡: 執行 /testkit.api.gencode，以 Session 與規格生成測試類與斷言。
- A詳: 步驟：1) 準備 openapi-spec.json、Test Case、session-logs.md。2) 呼叫 /testkit.api.gencode 指定場次。3) 生成 xUnit 專案與測試類（Arrange/Act/Assert）。4) 以環境變數注入 ACCESS_TOKEN。示例：在 Shell 設置 export ACCESS_TOKEN=xxx；dotnet test。注意：勿在測試碼內硬編碼憑證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, B-Q19, D-Q10

C-Q7: 如何在 CI/CD 執行自動化 API 測試？
- A簡: 於流水線注入環境變數與端點，執行 dotnet test 並收斂報告。
- A詳: 步驟：1) 在 CI 設定機密（ACCESS_TOKEN、API_BASE_URL）。2) 邏輯：restore→build→test，收集測試報告（trx 或 junit）。3) 異常時回傳失敗並附帶摘要。注意：定期以最新規格重生成測試碼，避免契約漂移。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, D-Q10, B-Q15

C-Q8: 如何用 TestKit.WEB.Run 進行 Web 測試？
- A簡: 安裝 Playwright MCP，確保頁面無障礙標記，執行探索並記錄。
- A詳: 步驟：1) 安裝 Playwright MCP，配置瀏覽器。2) 在 TestKit 執行 /testkit.web.run 指定規則集。3) MCP 以語義選取器操作頁面（登入、加購、結帳）。4) 記錄語義操作日誌。注意：頁面需具備 role/name/label，否則定位失敗或耗時激增。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, D-Q5

C-Q9: 如何設計無障礙屬性讓 Agent 能操作？
- A簡: 使用 semantic HTML 與 ARIA 屬性，提供可辨識的 role/name/label。
- A詳: 步驟：1) 元素用語義標籤（button、nav、form）。2) 加 aria-label="Checkout" 或明確文字。3) 用 getByRole('button', { name: 'Checkout' }) 便於選取。4) 隱藏時避免僅用 CSS，提供禁用或狀態語義。注意：測試頁面進入點應可見且可焦點。
- 關聯概念: B-Q10, D-Q5, A-Q17
- 難度: 中級
- 學習階段: 核心

C-Q10: 如何導入 SpecKit 產生一致化測試碼？
- A簡: 彙整規格（接口、案例、步驟、環境），以 SpecKit 一次生成。
- A詳: 步驟：1) 將 OpenAPI、Test Case、Session 步驟、環境與報告要求整理為 SDD。2) 用 SpecKit 映射到目標框架（xUnit/Playwright）。3) 生成測試碼並接入管理系統。注意：治理需求（命名、標籤、報告）以規格固定，避免手工偏差。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, B-Q16, D-Q10


### Q&A 類別 D: 問題解決類（10題）

D-Q1: AI 測試太慢且昂貴怎麼辦？
- A簡: 讓 AI 僅做探索與生成，回歸改用程式碼執行，降低成本與時間。
- A詳: 症狀：每次 AI 執行耗時長、token 費用高。原因：過度依賴 AI 重複執行。解法：左移探索，生成測試碼，改以 CPU 在 CI 回歸。步驟：規格化、Session、生成器。預防：成本估算、嚴格分工 Brain/GPU/CPU。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, A-Q2, B-Q12

D-Q2: AI 探索結果不一致如何處理？
- A簡: 控制上下文與降噪，分層到 MCP，固化為規格與測試碼。
- A詳: 症狀：不同輪探索步驟或判斷不一致。原因：上下文噪音、規格冗餘。解法：MCP 抽象 operation，授權流程移入 MCP，OpenAPI 用快照+摘要；審查 Session 成規格，生成測試碼。預防：Context Engineering、A2A 協議。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, A-Q28

D-Q3: 空購物車可結帳的缺陷如何修復？
- A簡: 症狀：系統未拒絕空車。修正：API 加限制與驗證，測試碼斷言拒絕。
- A詳: 症狀：TC-01 顯示空車仍能 CreateCheckout。原因：業務規則未實作。解法：API 加購物車非空檢查；錯誤碼與訊息明確。步驟：修 API→更新 OpenAPI→重生成測試碼。預防：決策表納入邊界規則、UI 同步禁用結帳。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q6, A-Q26

D-Q4: MCP 找不到 API 參數怎麼診斷？
- A簡: 檢查 operation 摘要與規範，補齊參數描述，調整 action/context。
- A詳: 症狀：RunStep 失敗或參數缺失。原因：operation 或 action/context 不足、規格不明。解法：強化 ListOperations 描述、提供範例 payload、在 Session 指明意圖。預防：維持 OpenAPI 清晰、為常用操作提供範例卡片。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q5

D-Q5: Playwright 無法點擊按鈕怎麼辦？
- A簡: 增加無障礙語義（role/name/label），用語義選取器定位按鈕。
- A詳: 症狀：看得見按鈕但點不到。原因：缺語義標記或被隱藏。解法：用 semantic HTML 與 ARIA；getByRole('button',{name})。預防：UI 以可達性為標準設計、避免純視覺坐標識別。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q9, A-Q17

D-Q6: 上下文溢出導致模型錯誤怎麼辦？
- A簡: 不塞完整 swagger，改用摘要與分層，將細節移入 MCP。
- A詳: 症狀：回答漂移、操作失敗。原因：上下文超載、噪音過多。解法：ListOperations 摘要、Session 保存細節、MCP 解析 function call。預防：Context Engineering、限制提交長文。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q7, A-Q13

D-Q7: OAuth2 錯誤導致測試失敗怎麼辦？
- A簡: 在 MCP 完成授權，於會話存 token，測試碼用環境變數注入。
- A詳: 症狀：401/403 或 token 過期。原因：授權在 Agent 混亂或硬編碼。解法：CreateSession 內處理 OAuth2；token 放 session；測試碼用 ACCESS_TOKEN 注入。預防：token 管理與刷新策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q6, C-Q7

D-Q8: Decision Table 計算錯誤如何修正？
- A簡: 逐規則驗算，修正公式與邊界，重展案例並標註重要性。
- A詳: 症狀：折扣或金額錯算。原因：AI 誤解規則或計算失誤。解法：手動驗算；修正 A1-A4 公式；確立邊界與違規情境；重生成 Test Case。預防：提供清楚規則與範例、審查機制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q20, C-Q2

D-Q9: 跨介面測試不一致如何診斷？
- A簡: 比較 API/WEB 探索步驟與規則，找出邏輯差異並統一規格。
- A詳: 症狀：API 與 Web 測試結論不同。原因：UI 有額外檢查或 API 缺失。解法：對照 Session；統一業務規則（如空車禁結帳）；更新 OpenAPI 與 UI 行為。預防：共用 Test Case、跨介面審查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q13, C-Q8

D-Q10: 測試碼隨需求改變而失效如何避免？
- A簡: 以 SpecKit 重生成，來源規格更新，測試碼自動一致。
- A詳: 症狀：契約或流程變更使測試碼過時。原因：手工維護難一致。解法：更新 OpenAPI、Test Case、Session 規格；以 SpecKit 重生成。預防：治理規範、版本化規格與生成流水線。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, B-Q16, C-Q10


### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 AI-First Testing？
    - A-Q2: 為何不直接用 AI 重複執行測試？
    - A-Q3: 在 AI 自動化語境中，什麼是「左移」？
    - A-Q4: Acceptance Criteria（AC）是什麼？
    - A-Q5: Decision Table 是什麼？
    - A-Q6: 為何用 Decision Table 收斂有價值的測試？
    - A-Q15: 覆蓋率在此流程扮演什麼角色？
    - A-Q16: API 測試與 Web UI 測試有何差異？
    - A-Q18: 什麼是 Session Log？
    - A-Q26: 為何要共用 Test Case 跨介面（API/WEB）？
    - B-Q1: AI-First Testing 工作流程如何運作？
    - B-Q2: 決策表如何展開成 Test Case？
    - B-Q12: 左移前後流程差異？
    - C-Q1: 如何用 TestKit.GenTest 建立購物車決策表？
    - D-Q1: AI 測試太慢且昂貴怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q10: MCP（Model Context Protocol）是什麼？
    - A-Q11: 什麼是 Context Engineering？
    - A-Q12: 什麼是「context rot」？
    - A-Q13: 為何要抽象化 API 呼叫給 MCP？
    - A-Q17: 為何「無障礙」是 AI 操作網頁的關鍵？
    - A-Q21: 舊流程與新流程的本質差異？
    - B-Q3: MCP 工具設計與作用機制是什麼？
    - B-Q4: Text-to-Calls 的執行流程為何？
    - B-Q5: CreateSession 內的 OAuth2 流程如何設計？
    - B-Q6: Session Logs 架構與內容如何設計？
    - B-Q7: Context 管理策略與降噪機制？
    - B-Q9: Web UI 探索在 Playwright MCP 的機制？
    - B-Q10: Accessibility 標記如何被 Agent 使用？
    - B-Q11: 測試成本模型與資源分工架構？
    - B-Q14: 生成 API 測試碼的技術原理？
    - B-Q21: Web 與 API 差異對 Agent 策略影響？
    - C-Q3: 如何設定 MCP 並執行 TestKit.API.Run？
    - C-Q6: 如何生成 .NET xUnit 的 API 測試碼？
    - C-Q8: 如何用 TestKit.WEB.Run 進行 Web 測試？
    - D-Q5: Playwright 無法點擊按鈕怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q19: 什麼是 SpecKit？何時該使用？
    - A-Q20: SDD 與 AI-First Testing 的關聯是什麼？
    - A-Q28: 什麼是 A2A 協議在本文的意涵？
    - B-Q15: 測試碼與 Test Management 整合架構？
    - B-Q16: SpecKit 與 SDD 的技術關係？
    - B-Q17: Artifact 流與資料供應鏈設計？
    - B-Q18: A2A 三元組設計背後機制？
    - B-Q19: OpenAPI 規格在流程的角色？
    - B-Q22: 程式化自動化如何保證重複一致性？
    - C-Q7: 如何在 CI/CD 執行自動化 API 測試？
    - C-Q10: 如何導入 SpecKit 產生一致化測試碼？
    - D-Q2: AI 探索結果不一致如何處理？
    - D-Q4: MCP 找不到 API 參數怎麼診斷？
    - D-Q6: 上下文溢出導致模型錯誤怎麼辦？
    - D-Q10: 測試碼隨需求改變而失效如何避免？