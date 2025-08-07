# 從 API First 到 AI First

## 摘要提示
- AI First: 生成式 AI 已成為軟體開發的新基礎元件，必須預留在架構設計中。
- API 設計品質: 高品質、符合 Domain 的 API 是 AI 能否可靠使用服務的核心。
- AI DX: 良好的 API 規格與說明能降低 AI 調用風險，提升「AI 使用者體驗」。
- Copilot/Agent: 先以 Copilot 模式輔助 Controller，未來邁向全自動 Agent。
- Prompt Engineering: 開發者需熟悉 Json-mode、Function Calling、Workflow 等提示技巧。
- RAG 模式: 檢索增強生成可為知識庫注入智慧，Embedding 與 VectorDB 是關鍵元件。
- DevOps + AI: 傳統 App / Config / Infra Pipeline 之外，還需要 AI Pipeline 管理模型與資料。
- UX 降維: LLM 能直接理解意圖並執行任務，為使用者體驗帶來跨維度提升。
- 實務 PoC: 透過「安德魯小舖」等示範驗證 AI 在購物、推薦、滿意度追蹤的可行性。
- 技術基礎: 架構思維、抽象化設計、資料與模型治理將決定 AI 時代的競爭力。

## 全文重點
本文源自 DevOpsDays Taipei 2024 Keynote，作者以三年來「API First」的推廣經驗為底，探討生成式 AI 與 LLM 崛起後，軟體產品如何轉向「AI First」。作者指出：當 LLM 已能理解自然語言意圖並自行呼叫 API，未來決勝點不再是程式碼量產速度，而是抽象化設計與基礎建設的品質。  
文章首先展示「安德魯小舖 GPTs」：使用者僅透過對話即可完成選品、加購、結帳；系統亦能從對話中統計購買紀錄、判斷情緒並自動記錄滿意度，體現 AI 對 UX 的「降維打擊」。接著作者說明要讓 AI 成為可靠元件，首先必須以狀態機思維落實 API First，確保介面「合情合理」且「防呆可靠」，否則 AI 的不確定性將被無限放大。  
在開發層面，新的基礎功夫包括：Prompt Engineering（模板化提示、Json-mode、Function Calling、Workflow）、RAG 架構（Embedding、向量資料庫、知識檢索）、以及如何在 MVC 中嵌入 LLM 形成 Copilot。作者以 .NET + Semantic Kernel 重寫購物流程，示範 Controller 與 Copilot 如何協作。  
基礎建設亦需升級：除了傳統的程式、設定、環境 Pipeline，還要增加 AI Pipeline 來治理資料、模型與推論算力的部署。最後作者引用零售業案例，說明未來銷售將由多個 AI Agent 與後端 Engine 協作，開發者如今最該做的是鞏固 API 設計、部署流程與 AI 開發技能，為即將到來的 AI 全通路時代奠定競爭力。

## 段落重點
### 1. 寫在前面
作者回顧 2021–2023 在 DevOpsDays 闡述 API First 的歷程，今年延伸到 AI First。指出生成式 AI 帶來的新需求：軟體開發者必須把 AI 視為強大的新元件，若想在未來保持競爭力，基礎功夫（設計、架構、數據治理）更形重要。並整理近年相關演講、文章與 DEMO，為後文鋪陳。

### 2. 示範案例：安德魯小舖 GPTs
以上架 GPT Store 的購物助理為例，示範三大情境：純對話完成下單、即時格式轉換與統計、AI 自主推薦並結帳。進一步延伸至情緒偵測與個人化：GPTs 能從對話歸納顧客偏好、評分滿意度並寫回系統。作者強調：LLM 直攻「意圖解析」層，與傳統 UI/UX 手法不同維度，能產生乘法效益；但要成功，API 描述與權限控制必須完善。

### 3. 軟體開發還是你想像的樣貌嗎？
AI 已具備「已知用火」能力，能理解意圖並使用工具。開發者須分清何時用精確計算、何時交給 AI 推論。作者提醒兩大壞習慣——檯面下溝通與 UI 導向 API——在 AI 時代將造成災難，因此需回到 Domain 驅動、狀態機為本的 API First。隨後闡述開發者的新基本功：Prompt Engineering 多種模式、Copilot 架構融入 MVC、RAG 設計模式與 AI/DevOps Pipeline，並透過 .NET Console 與 Semantic Kernel 的 Copilot DEMO、部落格 RAG DEMO 詳加說明。

### 4. Ref: 零售業的 AI 應用情境
引用老闆 Happy Lee 在 GAICONF 的「零售業四種銷售場景」與「Agent + Engine」模型，說明 AI 代理人可同時代表消費者與店家，透過後端 Recommendation、Knowledge 等 Engine 交互協作，滿足「心理需求」導向的購物體驗。這與作者強調的 API / AI DX 完全對應，證明良好服務介面是 AI 應用規模化的前提。

### 5. 寫在最後
作者總結：AI 將滲透開發、架構、流程與角色，決定競爭力的是抽象化設計及持續交付能力。建議團隊立即評估產品如何被 AI 強化，補齊 API、模型、資料與算力治理。文末分享大會問卷回饋與參會者心得，期許讀者把握 AI 時代的「基礎魔法」——設計思維、良好 API、Prompt 與 DevOps——成為下一階的魔法師。