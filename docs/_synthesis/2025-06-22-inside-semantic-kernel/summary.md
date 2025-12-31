---
layout: synthesis
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"
synthesis_type: summary
source_post: /2025/06/22/inside-semantic-kernel/
redirect_from:
  - /2025/06/22/inside-semantic-kernel/summary/
postid: 2025-06-22-inside-semantic-kernel
---
# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 摘要提示
- Chat Completion 基礎: 以 OpenAI Chat Completion 為核心通訊模型，掌握 roles、messages、tools、response format 等要素。
- 結構化輸出: 以 JSON/Json Schema 強化可解析性，搭配成功/失敗旗標與單一職責分工，利於工程化串接。
- Function Calling 基礎: 把自然語言意圖編譯成動作與參數，形成可執行的操作序列。
- Function Calling 進階: 透過 tool 與 tool-result 的循環，實作多步驟、具依賴順序的流程。
- RAG 啟動機制: 以 Function Calling 觸發檢索，Json Mode 產生查詢參數，形成 Search GPT 類體驗。
- MS Kernel Memory: 專攻長期記憶/RAG as a Service，與 Semantic Kernel 深度整合且可內嵌或服務化部署。
- 進階 RAG 策略: 先行生成摘要/FAQ/案例等檢索專用內容，提高語義對齊與召回品質。
- 多通路整合: 以 GPTs/Custom Action、No-code、MCP、Semantic Kernel 等多種 host/協定落實工具使用。
- 土炮 Function Calling: 在不支援 FC 的模型上以對話協議與規約字首模擬 tools 呼叫回合。
- 實作與回饋: 提供完整程式碼/影片/投影片；問卷顯示 Function Calling、RAG、MSKM 最受用。

## 全文重點
本文從最基本的 Chat Completion API 出發，層層建立開發者視角下的 AI 應用設計方法論：先以 roles/messages/tools/response format 搭起溝通基礎，再以 Json Mode/Json Schema 讓輸出可機械化處理、可反序列化與錯誤可判定，並以單一職責把「可用 code 處理的任務」從 LLM 中抽離，兼顧成本與穩定性。進一步導入 Function Calling，讓模型把自然語言意圖轉譯為動作與參數，並經由 tool 與 tool-result 的多回合交互完成複合任務。RAG 部分則拆成兩層：檢索/生成流程與觸發機制。前者包含抽問題、檢索、組 prompt 生成，後者以 Function Calling + Json Mode 自動產出查詢條件並驅動外部檢索，使系統具備 Search GPT 類能力。

Microsoft Kernel Memory（MSKM）被定位為 RAG/長期記憶的專業服務：它補上從內容抽取、切塊、向量化到儲存與查詢的整套管線，可服務化部署或內嵌使用，並與 Semantic Kernel（SK）在兩端整合（MSKM 內建 SK Memory Plugin；MSKM 亦基於 SK，承襲其連接器生態）。在實務最佳化上，作者以自身部落格為例，證明單純切塊的召回難對齊使用者問題語境，因而於匯入前先用 LLM 生成摘要、段落摘要、FAQ、問題-根因-解法等多視角素材並標註，再向量化入庫，顯著提升檢索精度。

整合路徑多元：可用 GPTs + Custom Actions（OpenAPI）、No-code 平台（如 Dify）、MCP（Claude Desktop 與標準協定）或直接以 SK 做 native FC。文中亦點出 MCP 協定要點及 demo 踩雷（MSKM 某版本中文 chunk 與 MCP C# SDK Unicode 編碼議題）。最後以問卷蒐整回饋：多數聽眾對 Function Calling、進階 RAG、MSKM 架構與工程化觀念最有收穫，並期盼後續更進階、更多實務案例與 MCP 深化應用。

## 段落重點
### 相關資源與連結
作者提供直播回放、Facebook 貼文串、Google 表單問卷、完整範例原始碼與 .NET Conf 2024 簡報等入口，鼓勵讀者以「先看觀念文字、再按興趣進影片與程式」的方式吸收，並持續回填問卷供後續內容調整。此區作為知識地圖與索引，讓讀者能快速定位到實作、投影片、示例 API 呼叫檔與 SK/MSKM 程式碼，建立理論—實作—反饋的閉環。

### Day 0, Chat Completion API
以 OpenAI Chat Completion 作為共同分母說明 LLM 應用的最小可行接口：請求包含 headers（apikey）、model/parameters（如 temperature）、messages（context window：system/user/assistant）與可選 tools、response_format。每回合把完整歷史與新問題一起送出，獲得下一段回覆，周而復始。重點在「API 很單純，複雜在應用設計」，因此學習重心是設計模式：如何建構 prompt、管理對話史、結構化輸出、引入工具，以及在多回合中保持狀態一致性與可控性。文中以 HTTP、SDK、SK 三種寫法對照，讓讀者理解從裸呼叫到框架封裝的差異。

### Day 1, Structured Output
從工程角度反思「讓 LLM 變成 App 模組」的三原則：用 JSON/Schema 定義輸出並直反序列化成強型別物件；在輸出中明確標註成功/失敗與不可判定，避免靠字串猜測；單一職責與成本意識，把搜尋、格式轉換、計算等交回傳統程式碼。此法讓 LLM 成為「提供語義決策與提取」的服務而非萬能黑盒。作者示例以地址抽取為題，展示 HTTP、OpenAI .NET SDK 與 Semantic Kernel 的對比，指出 SK 以 C# 型別直推 Schema 的生產力優勢，凸顯「設計先行、技術選型其次」的開發者思維。

### Day 2, Function Calling (Basic)
揭示 Function Calling 的本質：讓 LLM 以語義推理把人類意圖編譯為「動作 + 參數」序列。以購物清單範例說明：給定可用動作（add/delete）與 JSON 格式，模型從自然語言指示中產出結構化操作清單。此階段仍屬「Call 而未 Return」，即尚未涉及基於執行結果的後續決策。重點是建立開發者心智模型：LLM 擅長「從自然語言到機器協定」的翻譯，程式負責真實執行與狀態管理，兩者以 JSON 為介面解耦。

### Day 3, Function Calling (Case Study)
延伸到多回合「先查再辦」的真實工作流：以行程預約為例，完整展示 system/user/assistant/tool/tool-result 的交織歷程。LLM 先提出需使用 check_schedule 的 tool 與參數，應用側執行後回傳結果；模型基於結果再呼叫 add_event，直至回覆「任務完成」。關鍵在 chat history 的逐步擴展與每次完整上下文的送出。作者建議正式開發採用框架/平台（Semantic Kernel、No-code、MCP host 等）以降低細節負擔，但強調理解原理有助於跨場景與跨端設計。

### Day 4, RAG with Function Calling
拆解 RAG 為流程與觸發兩面：流程含問題收斂、檢索、帶來源生成；觸發則以 Function Calling + Json Mode 讓 LLM 自行推導查詢參數與時機。如此，對話從「只憑模型內知識」升級為「會查再答」的 Search GPT 類體驗，且可換成私域知識庫。作者以 Bing Search 作為外掛示例，讓模型結合定位/天氣/搜尋多工具自動編排。此處奠定隔日主角 MSKM 登場的脈絡：穩健檢索服務是 RAG 的核心配角。

### Day 5, MSKM: RAG as a Service
MSKM 專注長期記憶與 RAG 管線：從抽取、切塊、貼標、向量化到儲存與查詢皆可配置，既可 Web Service 也可內嵌。相較 SK 的 Memory 僅抽象向量存取，MSKM 以獨立服務與 SDK 補齊大規模文件處理與任務管線。與 SK 的兩大關係：其一，MSKM 內建 SK Memory Plugin，掛入後 LLM 可直接用 tools 操作 MSKM；其二，MSKM 以 SK 為基底，承接其連接器生態（OpenAI、Azure OpenAI、Ollama、Claude 等）。此組合為 .NET 生態中兼顧靈活與擴展的 RAG 實踐路徑。

### Day 6, 進階 RAG 應用：生成檢索專用資訊
面對長文與多視角查詢，單純切塊常導致語義對不齊。以作者部落格（單文 5–10 萬字）實測，僅靠向量相似度難抓住「使用者問題視角」。解方是在匯入前先用 LLM 生成多種「檢索友善」素材：全文摘要、段落摘要、FAQ（Q/A）、問題-根因-解法-例子等，並標註 tags 後向量化入庫。查詢時即可從多視角召回，顯著提升精度。這些離線一次性成本可用更強模型（如 o1）換品質。作者強調：RAG 更像設計模式而非成品系統，需理解語料、查詢行為與工具箱（SK、MSKM、No-code）組合以場景化調校。

### Day 7, MSKM 與其他系統的整合應用
總結多種 Function Calling 宿主形態：GPTs + Custom Actions（OpenAPI + OAuth）、No-code（Dify Custom Tools）、MCP host（Claude Desktop + MCP server）、或以 SK 進行 native FC。其共通二要素：提供 function 規格給模型、與代替模型統一執行並回傳結果。文中解構 MCP 協定（initialize、tools/list|call、resources、prompts；通訊含 stdio 與 SSE over HTTP），展示以官方 C# SDK 實作 MSKM 的 MCP server 並接入 Claude。亦提醒兩處踩雷：MSKM 某版中文切塊瑕疵與 MCP C# SDK 中文 JSON 編碼需調整，並給出暫行修正策略與示範。

### Day 8, 土炮 Function Calling
回答「無 FC 模型如何實現 FC」：抓住本質（三要素：tool 定義、區分 user/tool 對話、產生 tool 與參數），即可用對話協議與規約字首模擬。作者示例以 system prompt 規範兩種開頭詞分流給「使用者」與「秘書」，應用程式攔截「請執行指令」區段執行並回填結果，達成 tool/tool-result 的效果。此為教學用法，正式場景仍建議用原生 FC 與 SK 等框架；但理解此原理可應對模型/協定限制並強化故障轉移設計。

### 問券回饋（統計至 2025/06/22）
回收 93 份，受眾對 Function Calling、RAG、MSKM 架構與工程化觀念反饋最佳；多數認為從底層 API 到 SDK/框架的對照、以及進階 RAG 的切塊與合成內容策略最實用。後續期望含 MCP 更深入、產業落地案例、Agent/Process、工作坊與多模態等。亦有對節奏、投影片、向量原理講解深度與商務應用的建議。整體評價高，顯示「先打底原理、再上框架與平台、最後場景化調優」的教學路徑能有效落地到工程實作。

## 資訊整理

### 知識架構圖
1. 前置知識
   - 基礎 HTTP 與 REST API 操作（Request/Response、Header、Payload）
   - OpenAI Chat Completion API 基本參數與訊息格式（model、temperature、messages）
   - .NET 生態系基礎（HttpClient、OpenAI .NET SDK、Semantic Kernel）
   - 向量與嵌入（Embeddings）概念、向量相似性檢索
   - JSON Schema 與序列化/反序列化（C# 型別對映）
   - 事件/工作流思維（多步驟、回傳值、錯誤處理）

2. 核心概念
   - Chat Completion 基本型：所有 AI 對話與應用的底層通道（messages + roles）
   - Structured Output（JSON Mode/Schema）：讓 LLM 以可程式化的結構輸出，降低幻覺與提升後續自動化
   - Function Calling（Tool Use）：LLM 主動規劃並呼叫外部函式/工具，完成多步驟任務
   - RAG（Retrieval Augmented Generation）：以檢索補強 LLM 的知識與時效性，將外部內容納入回答
   - Microsoft Kernel Memory（MSKM）與 Semantic Kernel（SK）整合：RAG as a Service + Plugins，提供長期記憶、文件管線與工具化能力
   - MCP（Model Context Protocol）：標準化工具列表與呼叫通道（tools/resources/prompts），跨語言跨宿主的 Agent 通訊協定

   核心概念關係：
   - Chat Completion 是通道；Structured Output 與 Function Calling 是能力增強；RAG 是解題模式；
   - MSKM 提供 RAG 服務化與文件管線；SK 提供工具掛載與規劃；MCP 提供跨宿主的標準通訊；
   - JSON Mode 支撐 Function Calling 的參數抽取；Function Calling 觸發 RAG 檢索；RAG 的檢索結果回灌 Chat Completion 生成最終回答。

3. 技術依賴
   - OpenAI/LLM 服務：Chat Completion、Embeddings
   - .NET 技術棧：HttpClient、OpenAI .NET SDK、Semantic Kernel（Kernel + Plugins）
   - MSKM 服務：Docker 部署/SDK、文件管線（抽取/分段/向量化/儲存）
   - 向量資料庫或檢索服務：內建於 MSKM 或外部服務（亦可使用 Bing Search 等）
   - MCP Host/Client：Claude Desktop、MCP C# SDK（Stdio / HTTP(SSE)）
   - JSON Schema／C# 型別映射：在 SK/SDK 中簡化 schema 管理

4. 應用場景
   - 企業內知識庫問答（技術文件、FAQ、解決方案庫）
   - 工作助理／行事曆代理（查空檔、預約事件、串接企業系統）
   - 搜尋增強助理（Search GPT 類型：地點/天氣/即時資訊）
   - 長文內容檢索（部落格、白皮書、PDF 專業文檔）
   - 多宿主 Agent 整合（MCP 與桌面客戶端/No-Code 平台）
   - 進階 RAG：事前合成檢索專用內容（摘要、FAQ、Problem-Resolution、段落摘要）

### 學習路徑建議
1. 入門者路徑
   - 了解 Chat Completion API 基本用法與 messages/roles
   - 練習 Structured Output：要求 LLM 以 JSON Schema 回覆，於 C# 反序列化
   - 使用 HttpClient 與 OpenAI .NET SDK 各寫一個簡單聊天範例
   - 了解溫度、模型選擇與 token 觀念與成本

2. 進階者路徑
   - 學會 Function Calling（工具定義、呼叫與回傳）與多步驟規劃
   - 在 SK 中掛載 Plugins（如 Bing Search、自訂工具），理解與原生 HTTP 差異
   - 實作 RAG 基本流程：問題收斂→檢索→生成回答
   - 導入 MSKM：以 Docker 快速部署、以 SDK 存取，串接 SK Memory Plugins

3. 實戰路徑
   - 設計文件管線：抽取、分段、向量化、儲存，調整 chunking 策略（長度、重疊、符號）
   - 以 LLM 事前生成檢索專用內容（摘要、FAQ、Problem/RootCause/Resolution/Examples、段落摘要），標記合適 tags
   - 將 MSKM 作為 RAG 服務化入口，前端以 SK 或 MCP Host 調用
   - 評估與迭代：準確率、召回率、成本與延遲；加入回溯來源 URL、失敗訊號（成功/失敗欄位）
   - 針對不支援 Function Calling 的模型，以「土炮 Function Calling」模式模擬三方對話規則並攔截執行

### 關鍵要點清單
- Chat Completion 基本型: 善用 messages（system/user/assistant）與上下文窗管理，是所有應用的底層通道 (優先級: 高)
- Structured Output（JSON Mode）: 以 JSON Schema 明確規範輸出，降低幻覺並便於程式接管 (優先級: 高)
- 明確成功/失敗旗標: 回覆中加入可判斷的執行結果（像 HTTP status），避免以猜測處理錯誤 (優先級: 高)
- 單一職責分離: LLM 做推理與語意對齊；查詢、計算、格式轉換交給程式碼與外部 API (優先級: 高)
- Function Calling（Tool Use）: 在對話前定義工具規格，讓 LLM 自主決定呼叫順序與參數 (優先級: 高)
- 多步驟工具回傳: 工具的「呼叫」與「回傳」需完整串接，維持三方對話的歷程一致性 (優先級: 高)
- RAG 基本流程: 問題收斂→檢索（向量或搜尋引擎）→生成回答並附來源 (優先級: 高)
- MSKM（Kernel Memory）: 提供長期記憶與文件管線，支援 SK Plugins 與多家 LLM/Embedding 連接器 (優先級: 高)
- SK（Semantic Kernel）: 以 Plugins 方式掛工具，簡化 JSON Schema 與工具定義，提升 .NET 整合效率 (優先級: 高)
- 事前合成檢索內容: 用 LLM 生成摘要、FAQ、Problem-Resolution 等不同視角內容，顯著提高檢索精準度 (優先級: 高)
- Chunking 策略調整: 控制分段長度/重疊/符號，與 embedding 模型建議大小對齊，避免資訊密度失衡 (優先級: 中)
- 成本與延遲控管: 將可程式化計算交給程式；評估 Azure Function 與 Chat API 的成本差距 (優先級: 中)
- MCP 協定整合: 以標準化 tools/resources/prompts 通訊，跨宿主（如 Claude Desktop）使用自訂服務 (優先級: 中)
- 土炮 Function Calling: 對不支援工具用的模型，透過約定前置詞與回應管線手動實現三方對話 (優先級: 中)
- 來源可追溯性: RAG 回答需包含引用 URL 或來源標註，保障可信度與審計需求 (優先級: 中)