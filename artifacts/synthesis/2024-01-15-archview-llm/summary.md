# [架構師觀點] 開發人員該如何看待 AI 帶來的改變?

## 摘要提示
- GPTs x API 實作: 以「安德魯小舖」PoC 展示 LLM 搭配自建 API，可用對話完成導購、試算、結帳與查詢紀錄。
- LLM 理解意圖: LLM 可跨越「使用者意圖 vs 操作」的鴻溝，成為新一代 UX 的降維打擊。
- API 新標準: 未來 API 的主要使用者是 LLM，設計需一致、嚴謹、AI-friendly，強調狀態機與業務模型對應。
- Orchestration 中樞: LLM 將成為應用的中控（規劃、呼叫、彙整），UI 與服務圍繞其運作。
- Microsoft 佈局: 以 Azure OpenAI、Copilot、Semantic Kernel 三位一體建立模型、入口與開發框架。
- 開發框架演進: 從 MVC 邁向以 SK/LangChain 為核心的 AI 應用框架（Model/Memory/Plugins/Planner/Connector）。
- 架構師任務: 引領系統 AI Ready，釐清 LLM與計算邊界、設計精準 API、拆解 UI 為 Task、選對框架。
- 開發者升級: 善用 AI 工具、掌握 Prompt、向量資料庫、Semantic Kernel，深化 DDD/API 能力。
- UX 轉移: 以往由 UI/BL 承擔的體驗與流程將大量外移到 LLM/Copilot，APP 聚焦精準任務。
- 長短期策略: 短期用 AI 提效，長期重構架構與流程接軌 AI OS/AI PC 生態。

## 全文重點
作者以「安德魯小舖 GPTs」PoC 驗證：在不大幅增加新技術門檻的情況下，只要以自然語言定義角色、上傳知識、掛載符合 OpenAPI 的自建 API，GPTs 就能主動理解需求、規劃呼叫順序、彙整結果，完成導購、折扣試算、結帳、查詢歷史等操作。此過程的震撼點在於：AI 能補足過往軟體最困難的「意圖理解」，把 UI 難以涵蓋的彈性決策與跨情境推理交給 LLM，使 UX 優化迎來降維式革新。

由此作者提出關鍵觀點：未來應用的中樞是 LLM，UI 與服務將繞其編排。API 不再只是開發者之間的火星文，而是 LLM 主要的介面，要求高度一致性、嚴謹性與對商業模型的精準對應，尤其需以有限狀態機與標準化授權（如 OAuth2）確保流程可判別與可控。開發者應釐清「計算」與「意圖」邊界：精確、低成本、可測的交易/計算保留為傳統 API；多變、語意驅動、需彈性規劃的任務交給 LLM 來 orchestrate。過度依賴 LLM處理嚴謹步驟（如認證）會導致錯誤；改以標準協議與合理 API 設計能大幅降低困難。

在產業趨勢上，Microsoft 以 Azure OpenAI（模型與運算）、Copilot（系統級入口）、Semantic Kernel（AI 應用框架）形成三位一體。未來 Windows/AI PC 將內建 LLM 能力，Copilot 成為主入口，應用透過 SK/LangChain 以 Plugins/Planner/Memory/Connector 等構件整合模型與服務，逐步擴展至 OS 與雲端 PaaS/SaaS 的分層架構。對架構師而言，任務是引領團隊完成 AI Ready：分清意圖/計算邊界、設計 AI-friendly Domain API、以任務導向拆解 UI、挑選正確框架並放置元件到位。對開發者而言，短期用 AI 工具提效（GitHub Copilot、ChatGPT 等），中期掌握 Prompt、向量資料庫與 SK 實作，長期深化 DDD/API 能力，從 CRUD 升級到高品質領域實作。總結：AI 革命已至，短期先提效，長期重構與對齊新架構與生態，越早完成轉型，越不被 AI 淘汰。

## 段落重點
### 1, 安德魯小舖 GPTs - Demo
作者以自建的線上商店 API 與 OpenAI GPTs 整合，讓 GPT 充當店長，透過自然語言完成查詢商品、加入購物車、折扣試算、結帳與查詢歷史等流程。GPTs 能自主決定何時呼叫何 API，並將 JSON 結果彙整成人可讀摘要。實測中，GPT 能理解口語與同義詞、調整採購以符合預算與條件、處理不要酒類等需求，並在結帳流程中正確呼叫 API。其間亦暴露關鍵啟示：技術門檻低於想像，但整合思維與 API 設計品質成成敗關鍵；尤其當呼叫者是 LLM 而非人類開發者時，API 必須更合乎商業邏輯、可推理、可被文件化理解，並以狀態機保障流程可控。

### 1-1, (問) 店裡有賣什麼?
GPTs 自動呼叫 /api/products，將商品資訊摘要後呈現，展現從機器回應到人類可讀輸出的能力。此處顯示 GPTs 能在無需額外程式的情況下，將冗長描述化為關鍵摘要，降低資訊負擔。對 API 設計而言，只要提供正確規格，模型即可將資料翻譯為對話體驗，證明「以 LLM 為 UI 的資料呈現」可行。

### 1-2, (刁難) 預算 跟 折扣的處理
在僅提供單價與估價 API 的前提下，GPTs 透過多次呼叫試算與推演，找出符合預算與折扣（啤酒第二件六折）的組合。它也能處理口語修正與同義字（如用「啤酒」代指品名），並完成結帳流程。雖然偶有錯誤，但在回饋後可修正，顯示其在「意圖導向决策與規劃」的能力強於傳統 Chatbot 的指令式互動。

### 1-3, (刁難) 調整訂單, 不要酒類飲料
作者以隱含條件（有小孩不能喝酒）測試 GPTs 的語意理解與情境推理。GPTs 能據此修改購物車、重新分配數量、符合預算與「不同商品數量接近」等要求，並順利完成第二張訂單。此例顯示：LLM 可將需求與背景整合，轉化為一系列 API 操作步驟。

### 1-4, (刁難) 整理訂購紀錄
在查詢歷史訂單後，GPTs 不僅回傳原始資料，也主動彙整摘要並進一步依使用者要求製作統計表格。它能在不重打 API 的前提下，對既得資料做加工，展現 LLM 作為「結果編排與報告」工具的價值，減少後端為彙整開額外 API 的需求。

### 1-5, PoC 小結
此 PoC 的最大收穫是：LLM 能補足軟體「猜意圖」與「彈性決策」的長期缺口，使 API 可被自然語言驅動，讓應用流程得以由 LLM orchestrate。反過來，API 設計品質變得更重要：需標準化認證、提供 OpenAPI、描述清晰，讓 LLM 能「望文生義」；不合理的 API 靠文件與 Prompt 也難以補足，最後往往要回到改設計本身。

### 2, 軟體開發的改變
從「明確指令、確定計算」的電腦世界，邁向「理解意圖、彈性編排」的人機協作時代。LLM 成熟打破 UX 長年的瓶頸：不再只優化操作，而是理解意圖再回推操作。「LLM + API」成為新模式：LLM 接收自然語言與情境，轉譯為正確 API 呼叫與順序；應用架構需納入 LLM 作為中控。未來 API 仍重要，但對象改為 LLM，要求可理解、可推理、可編排。

### 2-1, 使用者體驗:
過往 UX 多在簡化「操作」，但「意圖到操作」的落差仍大（如長輩不知選Email還是Line）。LLM 能理解意圖，以語言為介面大幅縮短距離。未來 UX 的高峰不在按鈕與流程微調，而在讓 LLM 成為「用語意驅動行為」的入口，傳統僅靠 UI 的優化將難以企及。

### 2-2, 由大型語言模型 (LLM) 整合所有資源
LLM 可將自然語言轉為函數呼叫，決定何時呼叫何 API、如何組參數，並彙整回應。這使 LLM 成為「模糊語意」與「精確程式」之橋樑。從此 UI 不再是唯一入口，LLM 能跨檔案、情境、歷史對話整合資訊，產生正確的 API 執行序列，讓應用以對話式 Orchestration 前進。

### 2-3, 所有應用程式都會圍繞著 AI 而開發
API 的 AI 友善性決勝：需一致、合理、明確流程與錯誤辨識（建議有限狀態機）、嚴謹授權與規格描述。當使用者變成 LLM，文件與設計好壞將直接影響可用性。遇到不合理設計，優先封裝或改寫而非冀望 Prompt 補救；訓練專屬模型成本更高，通常改 API 更便宜有效。

### 2-4, 各種角色的職責變化
三個預期：LLM 成為 OS 一環（AI OS/AI PC）、融入主流開發框架（Plugins 擴充技能）、Copilot 成為作業系統主要入口（文字/語音/視覺協作）。各角色必須理解並推動這些變化：能加速變革者將不會被 AI 淘汰。

### 3, 看懂 Microsoft 的 AI 技術布局
Microsoft 把握 GenAI 時機，以 Azure OpenAI、Copilot、Semantic Kernel 形成模型、入口、框架三層佈局，從 OS 到雲再到開發者工具全線推進。回顧從 .NET、雲與開源到 GenAI 的多次轉身，作者認為這次是結構性變革：Windows 有望在 AI OS 階段再現價值，開發框架和雲端基建將隨之成形。

### 3-1, 大型語言模型 (LLM) 服務
Azure OpenAI 讓 Microsoft 得以第一時間將模型化為產品與平台。當模型可在邊緣端運行、硬體支援（NPU）成熟，OS 勢必內建 LLM 能力，形成新一代 Wintel 式生態（供應商版圖未定）。LLM 成為 OS 服務後，應用不需各自整套模型，改由 OS 統一管理與調度。

### 3-2, 輔助工具 / 引導工具 (Copilot)
Copilot 會是系統級入口與中控：使用者以語意描述任務，Copilot 決定搜尋、調用 API 或啟動 APP。當主流服務以 GPTs/Plugins 方式整合，入口效應將更明顯。相較獨立平台，作業系統廠商更有條件提供一致且低摩擦的入口體驗，目前以 Microsoft 最被看好。

### 3-3, AI 應用的開發框架
MVC 不再足以承載語意驅動的流程，需以 Semantic Kernel/LangChain 等框架讓 LLM 擔任 Orchestrator，透過 Planner/Plugins/Memory/Connector 管理對話、工具、記憶與外部資源。未來將上探 OS 層（登錄能力/協定）與雲端 PaaS（AI原生基建）。應用變小而精準，LLM 負責體驗與流程編排。

### 3-4, 整合三者的應用模式
Semantic Kernel 提供把模型、記憶、工具與入口串成一體的開發藍圖：Model 負責生成，Memory 管上下文，Plugins 是能力擴充，Connector 通往雲或本地模型。若將安德魯小舖以 SK 改寫，API 即 Plugins，UI 相當於 Copilot，基座由本地或雲端模型提供。這構成 AI 應用的標準分層。

### 4, 架構師、資深人員該怎麼看待 AI ?
架構師的核心任務是把系統導向 AI Ready：先以最小可行 API 搭 LLM 驗證價值，再回頭修 API 與流程，讓 LLM 能可靠編排。關鍵在釐清 AI 的用武之地、以狀態機與標準協議保障流程、用任務導向重構 UI。LLM 很貴，必須用在意圖理解與多步推理的刀口，嚴謹計算留給傳統程式。

### 4-1, 分清楚 LLM / API 的邊界:
以「計算/交易」與「意圖/規劃」做邊界切分。對精確性與成本敏感的功能（如金流、交易、定價）採 API 計算；需情境推理與多變組合的任務交給 LLM。PoC 顯示預算規劃用 LLM 有時會「偷懶」或非最優，若該功能需穩準快，應改回 API 算法並讓 LLM 呼叫。

### 4-2, API 的設計必須精準合理:
AI 時代是 API First。呼叫者是 LLM，因此 API 必須契合領域模型、流程可判別（有限狀態機）、授權標準（OAuth2）、規格清楚（OpenAPI + 描述），讓 LLM 吃得懂、用得穩。體驗與流程將由 LLM 分擔，API 聚焦核心 Domain，越發精煉且關鍵。

### 4-3, UI 應該以 Task 為單位拆解
UI 要能被 Copilot/LLM「接管與協作」，因此需以任務單元拆解並定義邊界、輸入輸出與前置條件。以 PoC 為鑑，將認證改為標準 OAuth2 後，LLM 才能穩定地銜接與操作，證明不把 LLM硬塞進不合理流程，而是用標準化協定與清楚任務設計配合。

### 4-4, 挑選正確地軟體開發框架
以 Semantic Kernel 等框架把 Kernel、Skills(Plugins)、Planner、Memory、Connector 放到正確位置，逐步累積可重用元件。架構師需先親手實作、再上升到抽象設計視角，帶領團隊沿框架長出可維護的 AI 能力，而非只停留在 PoC。

### 5, 開發人員該怎麼看待 AI ?
短期用 AI 工具（GitHub Copilot、ChatGPT 等）提升效率，但務必理解產出邏輯而非盲貼。中長期學會寫 Prompt、使用向量資料庫（支援 RAG）、熟悉 Semantic Kernel/LangChain 實作，並深化 DDD/API 能力。未來 CRUD/畫面型工作比重下降，精準的領域實作與高品質 API 成為主戰場。

### 5-1, 熟悉能提高工作效能的工具
把 AI 當生產力助推器：以 Copilot 代替零碎查詢、用生成工具寫文檔/郵件/測試初稿，並循環詢問以理解背後機制。工具帶來顯著提效，但知識需內化，不可放棄基礎能力。

### 5-2, 熟悉必要的 Tech Stack
三類核心能力：Prompt 編寫（把需求轉為可行策略）、向量/NoSQL 資料庫（索引與語意檢索）、Semantic Kernel（以 Plugins/Planner/Memory/Connector 實作 AI 應用）。這些將是 AI 原生開發的日常基礎。

### 5-3, 深化領域的設計與開發能力
Headless 真正由 LLM 推動：沒有 API 的服務將成孤島。DDD/API 設計能力將更吃香，UI/流程大量由 LLM/Copilot 承接，後端需專注少而精的核心 Domain API。從模板化 CRUD 升級為高品質設計與嚴謹實作，方能在新生態中保有競爭力。

### 6, 結論
AI 已從「更好的工具」走向「重塑架構與流程」：短期先用 AI 提效，長期必須把 LLM 置於應用中樞，重構 API、UI 與開發框架，對齊 Microsoft 等廠商的 AI OS/Cloud/Framework 生態。對架構師與開發者而言，現在就是改變與準備的時刻；越早理解並實作 AI Ready 的系統，就越能在下一個世代持續創造價值。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 軟體工程基礎：HTTP/REST、JSON、Web API 設計與測試
- 認證與授權：OAuth2/OIDC、API Key、Token 流程
- API 規格與文件：OpenAPI/Swagger、狀態機設計、錯誤處理
- LLM 基礎：Prompt engineering、Function calling/Tools、RAG 概念
- 領域建模：OOP、DDD、Business Model、API First 思維
- 基礎資料儲存：NoSQL、向量資料庫（選修）

2. 核心概念：本文的 3-5 個核心概念及其關係
- LLM 作為意圖解讀與流程編排的中控（Orchestrator）：把自然語言轉成可執行的 API 調用與步驟
- API First 與 AI-Friendly API 設計：面向 LLM 的一致、可預測、可理解、狀態機嚴謹的 API
- 分界原則「意圖 vs 計算」：模糊意圖交給 LLM；精準計算留給傳統程式/API
- Copilot 作為主要互動介面：以自然語言驅動應用與作業系統資源
- 新一代開發框架（Semantic Kernel 等）：將 Memory/Planner/Plugins/Connectors 模組化整合

3. 技術依賴：相關技術之間的依賴關係
- LLM（雲/端）→ Function Calling/Tools → API（OpenAPI/Swagger、OAuth）→ 後端服務/資料庫
- Semantic Kernel/LangChain → 封裝 LLM + Plugins + Planner + Memory → App/Service
- 作業系統/裝置（AI PC/NPU）↔ Copilot（系統入口）↔ 應用程式（以 Plugins 能力註冊/擴充）
- RAG/向量資料庫（可選）→ 增強知識存取與回覆品質

4. 應用場景：適用於哪些實際場景？
- 會話式電商/客服：用聊天完成搜尋、加購、估價、結帳與售後
- 企業流程助理：請假/報銷/採購等以自然語言發起、驗證與落單
- 知識彙整/摘要：從多個 API 結果與文件萃取、彙總、轉表格/報表
- Copilot in-app：在既有產品中提供任務導向引導、錯誤自我修復
- API 現代化：將既有系統重構為 AI 可用的 Plugins/Actions

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 LLM 與 Prompt 基礎；熟悉 ChatGPT/Copilot 的日常工作用法
- 學會撰寫與閱讀 OpenAPI/Swagger；用 Postman/Swagger UI 測 API
- 以簡單 REST API 搭配 GPTs/Function Calling 做第一個 PoC（查詢→加入購物車→結帳）

2. 進階者路徑：已有基礎如何深化？
- 設計 AI-Friendly API：一致資源模型、嚴謹狀態機、明確錯誤碼與訊息
- 導入 OAuth2/OIDC 標準授權流；將 API 描述與說明文字優化為「給 LLM 看」的文件
- 研讀與實作 Semantic Kernel/LangChain：Plugins、Planner、Memory、Connectors
- 練習分工：讓 LLM 做意圖編排；將精準計算/合規檢核固化在後端

3. 實戰路徑：如何應用到實際專案？
- 選定單一高價值場景（如客服/訂單彙整）做 Copilot 化 PoC
- 盤點既有 API，補齊/改寫為 AI-Friendly；補上 OpenAPI 與範例
- 建立組織級 Prompt 樣式庫與評測流程；以自動化對話測試驗證穩定度
- 規劃 OS/Cloud 整合：Azure OpenAI、Semantic Kernel、身分/金流等關鍵外掛

### 關鍵要點清單
- LLM Orchestration：LLM 負責將自然語言轉成一連串 API 調用與參數抽取（優先級: 高）
- 意圖 vs 計算分界：模糊意圖交給 LLM，嚴謹交易與計算交給傳統程式（優先級: 高）
- AI-Friendly API 設計：一致資源模型、嚴謹狀態機、清楚文件與範例（優先級: 高）
- OpenAPI/Swagger 作為「LLM 文件」：完善描述與例子，幫助 LLM 正確使用 API（優先級: 高）
- 標準化授權（OAuth2/OIDC）：避免「靠 Prompt 補洞」，用標準協定降風險（優先級: 高）
- Copilot 作為主要介面：將自然語言互動前置，UI 只保留必要精準操作（優先級: 中）
- Semantic Kernel/LangChain 框架：以 Plugins/Planner/Memory 建構 AI 原生應用（優先級: 高）
- Prompt Engineering 作為膠水：將業務規則與 API 使用方式清晰表述給 LLM（優先級: 高）
- API First 與 Domain API：以商業模型為核心開 API，減少流程/邏輯耦合於 UI（優先級: 高）
- 狀態機與錯誤可預測性：有限狀態機避免 LLM 任意順序呼叫造成失控（優先級: 高）
- RAG/向量資料庫（選用）：當需要知識擴充與長內容檢索時再導入（優先級: 中）
- 對話測試與回歸：以自動化對話腳本驗證 LLM 穩定度與「腦補」邊界（優先級: 高）
- Microsoft AI 版圖：Azure OpenAI + Copilot + Semantic Kernel 的端到端路徑（優先級: 中）
- UI 以任務單元拆解：將可被 Copilot 觸發的任務清楚封裝與註冊（優先級: 中）
- 開發者能力升級：工具（Copilot/ChatGPT）、框架（SK）、資料（NoSQL/Vector）三線並進（優先級: 中）