---
- source_file: /docs/_posts/2024/2024-07-20-devopsdays-keynote.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# (文章標題) 從 API First 到 AI First──DevOpsDays Taipei 2024 Keynote 延伸筆記

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "從 API First 到 AI First"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆","AI","DevOpsDays"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-07-20-devopsdays-keynote/2024-08-03-18-58-39.jpg

# 自動識別關鍵字
primary-keywords:
  - API First
  - AI First
  - DevOpsDays Taipei 2024
  - LLM / GPTs / Copilot
  - Function Calling & Tool Use
  - RAG (Retrieval-Augmented Generation)
  - AI DX
secondary-keywords:
  - Semantic Kernel
  - Kernel Memory
  - OpenAPI / Swagger
  - Prompt Engineering
  - Vector Database
  - OAuth2 / Scope / Idempotent
  - Controller + Copilot Pattern
  - Pipeline / GitOps / AI Pipeline

# 技術堆疊分析
tech_stack:
  languages:
    - C#
    - JavaScript / TypeScript
  frameworks:
    - ASP.NET Core
    - Semantic Kernel
  tools:
    - Azure OpenAI Service
    - ChatGPT / GPT-4o
    - GitHub Actions
    - Docker / Kubernetes
  platforms:
    - Azure
    - ChatGPT GPTs
  concepts:
    - API Design & State Machine
    - Function Calling / Tool Use
    - Copilot vs Agent
    - RAG Workflow
    - GitOps / CI-CD / AI Pipeline

# 參考資源
references:
  internal_links:
    - /2023/01/01/api-design-workshop/
    - /2024/01/15/archview-llm/
    - /2024/02/10/archview-int-app/
    - /2024/03/15/archview-int-blog/
  external_links:
    - https://platform.openai.com/docs/guides/function-calling
    - https://docs.microsoft.com/semantic-kernel
    - https://medium.com/@remitoffoli/building-llm-powered-products-part-2-32d843bef590
    - https://cloud.google.com/use-cases/retrieval-augmented-generation
    - https://blog.mickzh.com/blog/2024-devopsdays-taipei/
  mentioned_tools:
    - ChatGPT
    - GPT-4o-mini
    - Kernel Memory
    - Ollama
    - Stable Diffusion

# 內容特性
content_metrics:
  word_count: 18000
  reading_time: "約 55 分鐘"
  difficulty_level: "進階"
  content_type: "Conference Keynote 延伸文章"
```

## 文章層級摘要
本文是作者在 DevOpsDays Taipei 2024 Keynote 的延伸筆記，結合過去三年的 API First 探討與近半年的 LLM 實作經驗，說明軟體團隊如何從「API First」思維升級到「AI First」。作者以四段 Demo（安德魯小舖 GPTs、情緒/偏好偵測、Console Copilot、部落格 RAG）展示 LLM 已能透過 Function Calling 自主決定 API 呼叫、改善 UX、蒐集滿意度並提供個人化體驗。文章強調： 1) 當程式碼可被 AI 快速量產時，決勝點將是抽象設計與基礎架構品質；2) 高品質、以狀態機和 Scope 為核心的 API，是 AI 成功使用的前提 (AI DX)；3) 團隊應為 LLM 預留架構位置（Controller + Copilot），並在 DevOps Pipeline 中加入 AI Pipeline；4) RAG 與 Prompt Engineering 是開發 AI App 必備基礎；5) 零售業案例證實 AI 能直接轉換營收。適合軟體架構師、後端開發者與 DevOps 工程師，了解在 AI 普及前必須補齊的技術與流程。

## 段落層級摘要
### 1. 寫在前面  
作者回顧 2021–2023 在 DevOpsDays 分享 API First, CI/CD 等主題，並指出生成式 AI 讓「抽象設計」與「基礎建設」的重要性倍增。引用社群案例說明：有清晰架構與技術決策，才能真正放大 AI 產能。

### 2. 示範案例：安德魯小舖 GPTs  
Demo#1 展示使用自然語言下單、查紀錄與推論預算。LLM 能理解意圖並自主組合 API；好的 API 設計成為「降維式 UX」。作者比較傳統 UI 與 LLM UX，指出後者於意圖解析維度上有壓倒性優勢。

### 2-3. 情緒與喜好偵測  
Demo#2 透過 LLM 從對話抽取喜好、計算滿意度並寫回資料庫。對比傳統問卷/指標，此法屬「直接理解」而非統計推測，能捕捉長尾需求；但準確率仍須模型進步與資料標註。

### 3. 軟體開發還是你想像的樣貌嗎？  
分析 AI 已到「已知用火」階段：可用但易出錯，必須區分「精確計算」與「意圖理解」。提出兩大壞習慣：檯面下溝通與 UI-導向 API；要用狀態機、Scope、Idempotent 設計「AI Ready」API。

### 3-3. Prompt Engineering 與 Function Calling  
逐步解釋 Basic Prompt、JSON Mode、Function Calling、Workflow 四層用法，並以 ChatGPT 實測。強調開發者須掌握 prompt 來「用嘴巴寫程式」，並提供圖靈測試視角理解 LLM。

### 3-4. Console Copilot 架構  
Demo#3 在 Console App 旁插入 Copilot，採 Controller + Copilot Pattern：正常指令走傳統流程，AI 只在用戶卡關或提出複雜需求時介入。提出 MVC＋LLM 架構圖，說明未來從 Copilot 過渡到 Agent。

### 3-5. 部落格 RAG  
Demo#4 用 Kernel Memory 建立向量索引，ChatGPT GPTs 啟用 RAG 讀取作者所有文章並精準答題。解析 RAG 工作流程 (Retrieve→Augment→Generate) 與 AI 算力／資料管線部署考量。

### 4. 零售業 AI 應用情境  
引用 Happy Lee 在 GAIconf 分享的「四種銷售場景」，說明 Agent (前端) + Engine (後端) 協作如何提升心理滿足並直驅營收，呼應 API 與 AI 結合的重要性。

### 5. 寫在最後  
總結：1) 先想清楚產品要讓 AI 強化什麼；2) 補齊 AI Pipeline、算力部署與資料更新流程。附上大會問卷與社群心得回饋，鼓勵開發者練好「一階魔法」基礎。

## 問答集
### Q1 什麼是 AI DX？  
A: AI DX 指讓 AI（LLM/Agent）順利使用 API 的開發者體驗。包含領域導向設計、完整 OpenAPI Spec、穩固狀態機、標準 OAuth2/Scope 等。AI DX 好壞直接影響 LLM Function Calling 的成功率與 UX。

### Q2 API First 與 AI First 的關係？  
A: API First 專注把商業邏輯封裝成可重用且自說明的介面；AI First 讓 LLM 成為主要使用者。只有高品質 API 才能被 AI 正確解析並組合，API First 是落實 AI First 的基礎。

### Q3 為何 LLM 不適合做精確運算？  
A: LLM 透過機率分佈預測文字，擅長語義推理但非精確計算。四則運算、金額加總等應交由傳統程式或資料庫避免「幻覺」與高成本。

### Q4 如何判斷功能該丟給 Controller 還是 Copilot？  
A: 任務若需確定性、高效批次處理屬 Controller；需語意解析、跨系統意圖推論則交 Copilot。可先 Copilot-first 試驗，再回歸 Controller 如需穩定。

### Q5 RAG 與 Fine-tune 差別？  
A: Fine-tune 直接修改模型權重，成本高且更新慢；RAG 保持模型不變，於推論時檢索最新資料增強上下文，更新快速、隱私易控。

### Q6 Demo#1 如何處理付款安全？  
A: 支付流程仍走傳統 API，LLM 只組合參數。敏感資料驗證由後端支付閘道完成，LLM 不持有卡號或 Token。

### Q7 情緒偵測實務限制？  
A: 需大量標註資料校驗模型；不同文化語境會影響判斷；應在人機介面提醒使用者結果僅供參考，以避免誤判風險。

### Q8 Prompt Engineering 初學者建議？  
A: 先學三招：角色設定 (system)、範例示範 (few-shot)、輸出格式約束 (JSON Mode)。在 ChatGPT/Playground 迭代，確認再嵌入程式。

### Q9 為何需要 AI Pipeline？  
A: 除了程式碼、設定、環境，AI 專案還有資料集、模型、權限、算力。獨立 Pipeline 可版本化向量索引、監控模型漂移並自動回訓。

### Q10 Copilot 會取代 UI/UX 嗎？  
A: 不會。LLM 強於意圖解析，UI 強於精確操作。最佳體驗是兩者互補：簡單任務用 UI，一鍵難題交 Copilot。

### Q11 如何避免 LLM 誤用危險 API？  
A: 在 OpenAPI Spec 加入嚴謹的 Scope 與驗證。於 Kernel / Middleware 檢查 Function Call，未授權即阻斷，並回傳安全指示。

### Q12 中小團隊沒 GPU 能做 AI First？  
A: 可採雲端推論 (Azure OpenAI, Anthropic)、或用 GPT-4o-mini 等輕量模型。先專注 API 設計與 Prompt，再視流量決定自建算力。

## 問題與解決方案
### Problem 1 API 設計向 UI 偏斜造成 AI 難以使用  
Root Cause: 只為當前畫面提供「捷徑」API，缺少狀態機與授權設計  
Solution: 以 DDD/domain 劃分服務；使用狀態轉移圖列出最小原子 API；建立 OAuth2 Scope；自動產生 OpenAPI。  
Example: 將 /checkoutOneClick 拆成 /cart/create → /cart/addItem → /cart/confirm。

### Problem 2 LLM 幻覺導致數據錯誤  
Root Cause: 將精算任務交給語言模型  
Solution: Controller 處理計算，Copilot 僅收集意圖；使用 JSON Mode 強制輸出結構；加入校驗中介層。  
Example: LLM 回傳 {"qty":11} 時由後端驗證庫存限制。

### Problem 3 滿意度與喜好難以量化  
Root Cause: 傳統問卷/指標無法捕捉情境語境  
Solution: 以 Conversation Log + Embedding，交由 LLM 摘要情緒；結果寫回 Profile/Order；定期 AB Test 校正。  
Example: Chat 日誌 → embedding → GPT-4o 摘要 "滿意度2/5，原因：折扣資訊錯誤" → POST /orders/{id}/note。

### Problem 4 AI 部署成本與版本失控  
Root Cause: 模型、向量索引、算力與程式碼分散  
Solution: 建立 AI Pipeline (Data → Embedding → Model Deploy)；GitOps 管理 YAML/Weights；Prometheus + Grafana 監控 token 與延遲。  
Example: PR 觸發 GitHub Actions：更新文章 → 重新切 Chunk → Embedding → 上傳 Azure AI Search → Canary 測試。

## 版本異動紀錄
- 1.0.0 (2025-08-06)  
  • 首次依新版文章內容生成 Metadata、摘要、12 組 Q&A 與 4 組 Problem/Solution。