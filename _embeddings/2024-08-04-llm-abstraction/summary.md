# [架構師觀點] LLM 的抽象化介面設計

## 摘要提示
- 抽象化介面設計: 以抽象化思維推導 LLM 在應用架構中的角色與邊界，先定義介面再談實作。
- 工人智慧比喻: 把 LLM 想像成「真人」服務，對照「工人智慧」與 Uber 媒合模型，釐清聊天介面的本質。
- 對話模型: 以 IChatBot 介面與串流回覆模式，支援前端聊天體驗與逐步輸出。
- 調度與交換器: 導入 Operator/Switch 分層，實作「接線生」調度工人/模型，做到可拔換與可擴張。
- SessionState 管理: 把前後文、歷史與工具放進 SessionState，支撐多工與可擴展場景。
- Tool Use: 介面回傳文字與 ToolUsage 事件，為 Agent 能力預留鉤子。
- API 對照思維: 以 OpenAI Assistant API 作對照，辨識規格差異背後的意圖與應用邊界。
- 自製輪子法: 以 POC 發明輪子的方式學習，獲得與大廠等價的理解與框架設計能力。
- 可擴展與計費: 以 Uber 模式類比 worker 切換與 token 計費，提示無狀態工人與會話遷移需求。
- 架構師修練: 從「死背 API」轉向「活用脈絡」，培養對版本演進的預測與無痛升級能力。

## 全文重點
作者以「抽象化介面設計」為核心，討論若要在大規模系統中導入 LLM，應如何從角色定位與邊界切分開始，先定義合適的介面再落地實作。文章提出把 LLM 想成「真人」服務的觀點，延伸到「工人智慧」與 Uber 媒合平台的比喻：前端只是以對話（Prompt）溝通，背後可以是人或模型，介面保持一致即可。這個思路有助於將聊天機器人視為一種穩定的抽象介面，而非綁死於某家 API 的具體實作。

在技術面，作者從 IChatBot 介面出發，將回覆設計成可枚舉的串流輸出，滿足前端逐步顯示的需求；後端則引入 Operator（接線生）與 Switch（交換器）來調度 worker，將「媒合」能力標準化，便於替換真人、雲端 LLM、本地模型等不同的執行體。為支撐對話上下文與可擴展性，SessionState 被確立為核心結構，承載歷史紀錄、工具列表與狀態。為了實現 Agent 能力，回傳型別從單純文字擴展為「文字或 ToolUsage 事件」，使模型能在對話中觸發工具與行動。

作者說明此一設計練習的目的不在發布新規格，而在於用 POC 自我驗證，藉由與大廠方案（如 OpenAI Assistant API、Microsoft Semantic Kernel、LangChain、Ollama、ONNX Runtime 等）對照，理解差異是語法映射或模式差別，從而在架構層面做出正確選型。這種「自己發明輪子」的學習法能迅速累積對框架設計、並行與調度、狀態管理、工具編排等能力，讓工程師從死背 API 轉為掌握脈絡、提前預留設計空間，面對版本演進時能無痛升級並更精準地用對工具。

最後，作者以多年練習經驗總結：架構師的價值在於準確運用成熟元件，而準確來自於對設計意圖的抽象理解。當你能從第一性原理推導出與大廠相近的介面，你不僅用得對，也更能預測演進方向。這種能力一旦「湧現」，便能在專案中領先一步，將新版本的新能力自然地接上既有設計，提升整體系統的一致性與可維護性。

## 段落重點
### 寫在前面：工人智慧的介面設計
作者主張以「真人服務」的抽象來思考 LLM：使用者以聊天介面與服務互動，而背後可以是「工人智慧」（真人）或「人工智慧」（模型）。這種視角讓聊天機器人成為「穩定的抽象介面」，而實作者可自由替換。以 Uber 媒合為比喻：前端提出需求，平台將會話分派給可用「工人」，實現規模化與效率。此模式映射到 LLM 架構中，能解耦前端體驗與後端能力供應者，便於導入真人協作、模型混搭與資源調度，也自然對應未來的計費（token）與生產力度量。核心重點是先定義「對話介面」與「調度邊界」，再談具體模型或供應商。

### 開始 coding：最小介面與串流回覆
在最小可行介面上，IChatBot 先被定為 Ask(question)；為支援打字機式輸出與更佳 UX，回傳型別改為 IEnumerable<string>，讓前端得以邊收邊顯示、可中斷。前端示例以迴圈讀取輸入並即時渲染回覆，形成最小聊天客戶端。後端著眼於「Uber-like」的服務：當前端有詢問，就媒合一位可用 worker 回應；會話中斷則釋放，允許 worker 服務下一個會話。此設計從一開始就為「串流回覆、可拔換 worker、資源共享」預留空間，也為之後的 SessionState、工具使用與多模型協作鋪路。

### 第一版實作：Uber-like 調度與類別圖（略）
作者提出以 Operator（接線生）與 Switch（交換器）建模後端調度。Operator 負責分派會話、選擇 worker；Switch 抽象底層連線與路由；Worker 則是實際回覆的執行單位（可是真人或模型）。雖然此段未展開實作細節，但指出類別圖已具體成形，具備可維護的層次：前端依賴 IChatBot；中間以 Operator/Switch 管理媒合與轉接；底層以 Worker 實作各種供應者。此分層使得「切換真人/模型、支援不同 API、增加計費與度量、實現故障轉移與會話遷移」變得自然，且與後續的 Session 狀態外置化一脈相承。

### 2024/08/02：LLM 抽象化動機與對照
作者回顧不同平台與框架的 API 差異（OpenAI Chat Completion/Assistant API、Semantic Kernel、LangChain、Ollama、Windows Copilot Runtime/ONNX 等），指出既有標準未完全收斂。為避免被規格牽著走，作者選擇以抽象化出發，自行 POC 一次，分辨何者只是語法差異可映射、何者是模式差異需選型。這種方法讓使用者不必死背 API，而是掌握設計脈絡；一旦理解本質，文件只是語法查詢。透過與大廠設計對照，若概念對齊則驗證方向正確；若不一致，則可調整或發掘更佳做法。這是作者長年以來在框架、並行、ORM、權限等主題上的學習套路。

### 定義：圖靈測試導向的 IIntelligence 與 SessionState
作者以「圖靈測試 App」倒推介面：定義 IIntelligence.Ask(question) 作為最小能力，並引入 SessionState 承載對話歷史與上下文。為能水平擴展與切換供應者，Session 需外部管理（工廠、LB、路由等）。延伸到 Tool Use，SessionState 內含可用工具（字典或委派），Ask 的回傳從單純文字提升為「文字或工具使用事件」的混合串流，以支援代理式行為、工具調用與可觀測。對應 Uber 類比，會話可在真人與 AI 間切換，關鍵在於 worker 無狀態、會話狀態可轉移，從而實現可靠調度、故障轉移與計費度量。

### 小節：從死背到活用的學習與架構師修練
作者強調，若只照文件學會使用新 API，短期可上手，長期難以靈活運用。以抽象化與自製輪子的方式學習，能培養對設計意圖與演進脈絡的判讀力，面對版本更新時不再焦慮，而是「等待自己早預期的能力被官方實現」。當理解深化，便能「預測」合理的設計變化，提早預留接口與擴充點；新版本到來時僅需替換實作即可無痛升級。在他人眼中像「提前布局」，本質是以抽象化築基、以 POC 驗證路徑、讓機率站在自己這邊的專業習慣。這正是架構師「精確運用成熟元件」的能力來源。

## 資訊整理

### 知識架構圖
1. 前置知識
   - 物件導向與介面設計：interface、抽象化、封裝、多型
   - 分散式系統基本概念：dispatch/load balancing、stateless/stateful、session 管理
   - API/SDK 基礎：HTTP/gRPC、金鑰授權、串流回應
   - LLM 基本概念：Prompt/對話脈絡、Tool Use、Token/計費
   - 軟體架構實務：POC、對照組設計、依賴注入與依賴管理

2. 核心概念
   - 抽象化介面（IChatBot/IIntelligence）：用「人機一體」的統一介面操作不同智慧體（人/LLM）
   - SessionState/對話脈絡：保存歷史、指令、可用工具，並支援跨 Worker 的轉移
   - Dispatcher/Operator/Switch：像 Uber 一樣媒合前端會話與後端 Worker（人力/模型）
   - Tool Use 能力：聊天以外的「做事」抽象（呼叫外部工具/函式）
   - 串流回應與可中斷：回應以 IEnumerable 流式輸出，支援前端即時呈現與中途停止
   - 以上概念的關係：前端透過抽象介面呼叫 → Operator 透過 Switch 派工到 Worker → Worker 依 SessionState 與 Tools 產生（串流）回應 → 計費/觀測

3. 技術依賴
   - Chat Client 依賴 IChatBot/IIntelligence 抽象
   - IChatBot 依賴 SessionState（歷史/工具）與 Dispatcher（派工）
   - Dispatcher 依賴 Switch（路由/選擇策略）與 Worker 池（Human/LLM）
   - Worker 依賴外部 LLM/Runtime（OpenAI Assistant/Chat Completion、Ollama、ONNX Runtime）或真人通道
   - 橫切關注：金鑰/Token 計費、觀測/日誌、錯誤恢復、協定（HTTP/gRPC）與串流

4. 應用場景
   - 多模型/多供應商切換的企業級聊天/助理系統
   - 需要「人機混合」服務（工人智慧與人工智慧並用）的客服/審核/標註
   - 具工具呼叫能力的任務自動化（RAG、函式呼叫、工作流）
   - Turing Test/教學與研究性實驗（驗證抽象介面與系統邊界）
   - 成本/計費可觀測的內嵌式 LLM 功能（token 追蹤、限流）

### 學習路徑建議
1. 入門者路徑
   - 從單一介面開始：實作 IChatBot/IIntelligence.Ask(question) 的同步版本
   - 加入串流回應：將回傳型別改為 IEnumerable<string>，做一個 Console 聊天 demo
   - 基本 SessionState：保存最簡對話歷史，體會脈絡的必要性

2. 進階者路徑
   - 引入 Dispatcher/Operator/Switch：支援多 Worker，嘗試路由策略（輪詢/最空閒）
   - Worker 無狀態化：將歷史與指令完全放在 SessionState，支援 Worker 之間切換
   - Tool Use：於 SessionState 註冊工具（Dictionary<string, Func>），回應型別擴充為文字與工具呼叫事件
   - 比對大廠規格：將抽象對照 OpenAI Chat Completion/Assistant API、Ollama API

3. 實戰路徑
   - 串接真實供應商：實作 OpenAI/Ollama Adapter；切到 gRPC/HTTP 串流
   - 觀測與計費：新增 token 計費估算、日誌追蹤、重試與超時控制
   - 安全與治理：API Key 管理、配額/限流、審計（誰叫了什麼工具）
   - Turing Test/PoC：做一個可切換 Human/LLM 的 app，驗證抽象的普適性

### 關鍵要點清單
- 抽象介面優先: 用 IChatBot/IIntelligence 隔離具體供應商與實作差異，降低耦合 (優先級: 高)
- 串流回應模型: 將 Ask 回傳 IEnumerable<string> 以支援即時呈現與中斷控制 (優先級: 高)
- SessionState 設計: 將對話歷史、指令、工具清單集中管理，支援可攜式脈絡 (優先級: 高)
- Worker 無狀態化: 將狀態外移到 SessionState，實現 Worker 熱切換與彈性伸縮 (優先級: 高)
- Dispatcher/Switch 路由: 以 Operator/Switch 媒合會話與 Worker，支援策略化派工 (優先級: 中)
- 人機同構抽象: 將 Human/LLM 都視為 IIntelligence 的實作，驗證界面普適性 (優先級: 中)
- Tool Use 抽象: 將工具以函式表註冊並由回應流觸發，擴展「能聊天也能做事」 (優先級: 高)
- 計費與 Token 觀測: 在抽象層納入 token 計費與成本追蹤，便於治理 (優先級: 中)
- 供應商切換能力: 以 Adapter 連接 OpenAI/Ollama/本地 Runtime，支援熱切換 (優先級: 高)
- 協定與串流選型: 視場景選擇 HTTP SSE/gRPC 串流，兼顧效能與互通性 (優先級: 中)
- 擴展點與版本演進: 為 Assistant/Function Calling 等能力預留擴展面 (優先級: 中)
- 錯誤與重試機制: 超時、重試、降級與回退策略內建於抽象層 (優先級: 中)
- 安全與治理: API Key 管理、配額、審計與資料最小揭露 (優先級: 中)
- POC 驅動學習: 以自製小輪子對照大廠規格，建立設計直覺與映射能力 (優先級: 高)
- 架構一致性: 隨規模擴大仍維持一致的介面與結構語言，減少技術債 (優先級: 高)