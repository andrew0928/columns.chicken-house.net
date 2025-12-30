---
layout: synthesis
title: "從 API First 到 AI First"
synthesis_type: summary
source_post: /2024/07/20/devopsdays-keynote/
redirect_from:
  - /2024/07/20/devopsdays-keynote/summary/
---

# 從 API First 到 AI First

## 摘要提示
- 核心觀點: 當程式碼可被量產時，決勝點回到抽象化設計品質與基礎架構決策
- UX 降維打擊: 以 LLM 直觀理解「意圖」+ 自動調用 API，比傳統 UI/流程在許多情境更有效
- AI DX: API 必須對 AI 友善（清楚、一致、可預測、可授權），否則成本與風險大增
- Copilot 架構: 以 Controller + LLM 並駕模式落地，把意圖理解交給 AI，精確計算交給程式
- Prompt 工程: Json Mode、Function Calling、Workflow 是工程落地三把斧
- RAG 能力: 檢索增強生成是知識應用的基礎設計模式與元件組合
- 架構演進: 從 API First（域驅 API）走向 AI First（Agent/Engine 協作）
- DevOps 與 AI: 傳統三條 Pipeline 之外，新增 AI Pipeline（資料、模型、算力）以 GitOps 管理
- 產業應用: 零售從「基本需求」走向「心理滿足」，AI 有機會放大業務員直覺型價值
- 行動建議: 先補足 API 設計品質與 AI 基礎功，再擘畫 Copilot/Agent 在產品中的位置

## 全文重點
作者以 DevOpsDays Taipei 2024 Keynote 延續多年「API First」主題，提出在生成式 AI 時代，軟體價值將更倚賴抽象化設計與架構決策。現階段 LLM 已具備理解意圖與使用工具（Function Calling/Tool Use）的能力，可將「對話」與「任務」串起來，於是以自然語言驅動操作成為可能。透過「安德魯小舖」GPTs，作者示範 AI 以對話完成推薦、加購、結帳、查詢與重構資訊呈現，並以第二個 DEMO 說明 AI 從上下文抽取喜好與情緒、推估滿意度，指出相比傳統 UI 優化、指標追蹤與問卷，這是一種不同維度的 UX 改善手段。

要讓 AI 穩健介入，API 設計務必回到 Domain，避免為了前端捷徑犧牲結構，並以狀態機、原子化轉移、明確授權（API Key/Scope）確保可靠。否則會在 Prompt 補救、文件負擔、測試爆炸與資料毀損中付出更高代價。工程落地上，Prompt Engineering 是新基礎：以 Json Mode 得到結構化輸出、以 Function Calling 讓 AI 主動選用 API、以 Workflow 拆解多步驟任務。架構面，作者提出 Controller（精確計算）+ Copilot（意圖理解）並駕，當 LLM 成熟可升級為 Agent 主導。另以 RAG 展示知識檢索與增強的標準流程與元件選型考量（Embed、VectorDB、托管位置與成本分攤）。DevOps 上，傳統 Application/Config/Environment Pipeline 之外，需建立 AI Pipeline 管理資料、模型與算力，同步導入 GitOps 思維。最後以零售應用呼應：AI Agent 面向顧客與店家交涉，背後倚賴各類 Engine（Knowledge/Recommendation/Assistance）。作者總結：現在就打好 API 設計與 AI 開發基本功，規劃 LLM 在產品、架構與 Pipeline 的位置，才能在 AI 盛行時代保持競爭力。

## 段落重點
### 1. 寫在前面
作者回顧 2021–2024 系列分享，將「API First」推進到「AI First」的落地。指出社群多聚焦模型、算力、工具，但真正價值在於「如何把 AI 嵌入產品」。拋出三問：模型更強時如何用？算力普及時產品如何運用？工具成熟後如何強化別人而非只強化自己？核心結論：AI 普及只會放大工程基礎的重要性，應回歸設計與架構基本功。

### 2. 示範案例: 安德魯小舖 GPTs
作者以 GPTs 連接後端購物 API，讓 AI 解析意圖並自動調用 API 完成任務。

#### 2-1 出一張嘴就能買東西的魔法
展示以自然語言完成推薦、加入購物車和結帳；AI 能依需求重構呈現與統計。強調「提出要求」≠「下指令」，LLM 會推理意圖並規劃行動（API 調用）。

#### 2-2 透過 AI 來提升使用者體驗
提出「降維打擊」：LLM 在理解意圖上遠比傳統 UI 流程有效，但非取代關係。UI 降低操作成本，AI 解決意圖辨識與自動代辦，兩者相輔相成。

#### 2-3 偵測購買滿意度的魔法
AI 從對話捕捉喜好並自動存取客戶註記；回訪時個人化推薦；結帳後摘要情緒、紀錄滿意度。相較傳統數據推測與問卷誘因，LLM 能直接從上下文判斷，但準確性仍待時間改善。

#### 2-4 再來一次, 你覺得 UX 夠好嗎?
強調兩路並行：既有統計/監控/推薦繼續運作，LLM 補足「當下」情境判斷與個人化；像資深業務員的直覺被大模型規模化，形成不同維度的方法論。

#### 2-5 小結
AI 會主動判斷並調用 API，AI DX 成為關鍵。高品質 API（描述清楚、授權嚴謹、一致可預測）能降低 AI 不確定性與成本。以 AI 強化 UX 時，善用 LLM 抽象層，讓效益「乘法」放大。

### 3. 軟體開發還是你想像的樣貌嗎?
AI 已能理解意圖與用工具，但仍不穩定；應把「精確計算」交給程式，把「意圖理解」交給 LLM，正確切割場景是第一課。

#### 3-1 從 API First（設計品質）開始
批判「檯面下溝通」與「為 UI 取捷徑犧牲 Domain」的壞習慣。以狀態機設計 API、原子化轉移、明確授權，確保可靠與可測。否則將付出額外 Prompt、文檔、測試與事故代價。

#### 3-2 你該練習的基本功夫
以「魔法使」比喻：隱藏實力（技術選擇）、基礎訓練（PoC 到維運）、想像力（架構思考）。AI 基礎功包括：API First、架構擺位、基礎元件（Embed/VectorDB/Prompt）與設計模式（RAG/推薦）。

#### 3-3 Prompt Engineering
以三招落地：基本型（在程式中包裝 Prompt）、Json Mode（要求結構化輸出，便於處理）、Function Calling（讓 LLM 產生可執行動作）。進一步以 Workflow 拆解多步驟任務，LLM 擬定計畫、逐步調用工具，模型選擇與提示設計決定效果。

#### 3-4 Copilot 的設計架構
以 Console + Semantic Kernel 自建 Copilot：不改既有操作，AI 在旁輔助、主動關懷、接受直接詢問並代操作。架構上，從 MVC 進化為 Controller（正駕）+ Copilot（副駕），待 LLM 成熟再邁向 Agent 優先。

#### 3-5 RAG 基礎元件與設計模式
以「部落格 GPTs」示範：用檢索結果增強 LLM 回答，流程含檢索、合併上下文、回答。實作需考量嵌入模型、向量庫、託管成本與 Token 分攤，RAG 本質是特化的工作流。

#### 3-6 小結
兩大功課：決定 LLM 在架構中的位置（Copilot→Agent 演進）與將 LLM 納入 CI/CD/GitOps（新增 AI Pipeline 管理資料、模型、算力）。把 LLM 當作「意圖理解」介面的實作，實踐依賴介面設計。

### 4. Ref: 零售業的 AI 應用情境
引用 Happy 的「零售四種銷售場景」：零售販賣「心理滿足」，AI 有機會擬真地理解意圖與情緒。提出 Agent（面向顧客/店家）+ Engine（知識/推薦/助理）的協作圖景；API First 即是讓 Engine 以良好介面供 Agent 高效取用。

### 5. 寫在最後
AI 將改變架構、流程與角色；當 code 量產化，價值在於設計、決策與高品質 API。思考產品如何用 AI 強化（Agent/Copilot/RAG），以及技術架構哪些元件要補齊（模型選型、算力佈署、Pipeline）。附上大會回饋與參加者心得，呼應主軸：打好基礎，才能在 AI 時代維持競爭力。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 軟體工程與系統設計基礎（MVC/分層架構、OOP、交易一致性）
- API 設計（REST/HTTP、OpenAPI/Swagger、OAuth2/SCOPE、API Key、錯誤設計）
- 狀態機思維（狀態轉移、原子操作、授權與邊界）
- DevOps/CI-CD 基礎（GitOps、部署/環境/設定三循環）
- JSON/序列化、雲端與成本概念（Token、GPU/NPU/CPU 推論）
- Prompt 基礎與 LLM 能力/限制（推理 vs 精確計算）

2. 核心概念：本文的 3-5 個核心概念及其關係
- API First：以業務領域為中心設計高品質、可復用的 API，是之後 AI 使用「工具」的地基
- AI First：把 LLM 視為系統中的關鍵元件，用於意圖理解、推理、工具使用（function calling）
- AI DX（面向 AI 的開發者體驗）：API 要讓 LLM 易懂、可安全與穩定地調用（描述清楚、邊界嚴謹）
- Copilot → Agent 演進：先以副駕（Copilot）輔助 Controller，待 LLM 成熟後逐步擴權到 Agent
- RAG：以檢索增強生成讓 LLM 用最新/專有知識回答，補足模型訓練的知識缺口

關係：API First 提供可被 LLM 使用的工具，AI DX 決定 LLM 使用工具的可靠性；在架構上先落地 Copilot 模式，RAG 提供資料增強；最終形成 AI First 應用。

3. 技術依賴：相關技術之間的依賴關係
- LLM 能力 →（需要）Prompt/Instructions/Json Mode →（驅動）Function Calling/Tool Use
- Function Calling →（依賴）高品質 API + OpenAPI 規格 + 穩固的認證授權（API Key/OAuth2/SCOPE）
- RAG →（依賴）Embedding → 向量資料庫（Vector DB）→ 檢索/重排序 → 增強 Prompt
- Copilot/Agent →（依賴）事件/上下文蒐集、策略指示（policies/guardrails）→ 執行工作流（Workflow/Orchestration）
- 落地與營運 →（依賴）AI Pipeline（資料/模型/算力）+ 傳統 CI/CD（App/Config/Env）+ 成本/監控/安全

4. 應用場景：適用於哪些實際場景？
- 電商客服/店長 Agent（意圖理解、商品推薦、代辦操作、結帳）
- UX 降維強化（自然語言操作、上下文理解、彈性呈現）
- 個人化與情緒/滿意度偵測（從對話抽取偏好與評分）
- 工作流助理（排程、資訊蒐集、多步驟任務規劃）
- 知識庫助理與文件問答（站內搜尋 + RAG）
- 內部 Copilot（輔助操作、主動提示、規則/政策導引）

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 REST/HTTP/JSON 與 OpenAPI，閱讀優良 API 規格
- 使用 ChatGPT/GPTs 體驗 instructions、function calling、json mode
- 做一個小 PoC：以公開 API + GPTs 連動完成簡單任務（查詢→轉成 API 呼叫）

2. 進階者路徑：已有基礎如何深化？
- 以狀態機重構既有服務 API：原子化轉移、嚴格授權/邊界、完善文件
- 導入 AI DX：優化 OpenAPI 描述、錯誤碼、參數語意、範例與用法說明
- 實作 Copilot 模式：在既有 App 中加入 LLM 提示/求助通道與工具使用
- 導入 RAG：建立 Embedding/向量庫/檢索流程與增強 Prompt

3. 實戰路徑：如何應用到實際專案？
- 架構圖落地：Controller + Copilot 分工，清楚定義哪些交給 LLM、哪些保留給精確計算
- 建置 AI Pipeline：資料蒐集/清洗→Embedding/索引→模型/推論資源配置（雲/邊緣/自建）
- GitOps 化：App/Config/Env + AI（資料/模型/算力）四條流水線與監控告警
- 安全與治理：API 授權策略、Prompt/工具使用 Guardrails、成本監控與測試基準

### 關鍵要點清單
- API First（以域為中心）: 以業務語意與狀態機設計 API，避免 UI 偏斜與臨時捷徑 (優先級: 高)
- AI DX: 讓 API 對 LLM 友好（清楚描述、範例、錯誤語意、OpenAPI 完整） (優先級: 高)
- 狀態機與原子轉移: 以狀態轉移定義最小正確操作，守住資料一致與授權邊界 (優先級: 高)
- Function Calling/Tool Use: 讓 LLM 能自主選擇並調用 API 來完成任務 (優先級: 高)
- Prompt Engineering（Instructions/Json Mode）: 用策略化提示與結構化輸出提高可靠性 (優先級: 高)
- Copilot 架構: 以副駕模式輔助 Controller，先落地、可監督、可回退 (優先級: 高)
- Agent 工作流（Multi-step Planning）: 讓 LLM 規劃多步驟並分批調用工具 (優先級: 中)
- RAG（檢索增強生成）: 用 Embedding + 向量庫把專有知識接到 LLM (優先級: 高)
- 個人化與情緒偵測: 從對話抽取偏好/滿意度，改善體驗與服務決策 (優先級: 中)
- 分工：精確計算 vs 意圖理解: 把可計算、需嚴格正確的交給程式；含糊/推理交給 LLM (優先級: 高)
- 安全與授權（OAuth2/SCOPE/API Key）: 工具可用但邊界不可破，避免順序漏洞與越權 (優先級: 高)
- 成本與部署（雲/自建/邊緣）: 權衡 Token/GPU 成本與體驗，彈性選擇推論位置 (優先級: 中)
- AI Pipeline/GitOps: 在 App/Config/Env 之外增設 AI（資料/模型/算力）流水線 (優先級: 高)
- 可觀測性與測試: 為不確定性建立評測集、回放/對比、成本與品質監控 (優先級: 中)
- UX 降維強化: 用自然語言介面+工具使用補足傳統 UI 的意圖理解盲點 (優先級: 中)