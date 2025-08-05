# (文章標題) 從 API First 到 AI First──DevOpsDays Taipei 2024 Keynote 摘要

## Metadata

### 原始 Front Matter
layout: post
title: "從 API First 到 AI First"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆", "AI", "DevOpsDays"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-07-20-devopsdays-keynote/2024-08-03-18-58-39.jpg

### 自動識別關鍵字
keywords:
  primary:
    - AI First
    - API First
    - DevOpsDays Taipei
    - Copilot / Agent 架構
    - LLM Function Calling
    - AI DX
    - RAG (Retrieval-Augmented Generation)
  secondary:
    - Semantic Kernel
    - OpenAI GPTs
    - Vector Database
    - Prompt Engineering
    - 系統監控
    - Pipeline / GitOps
    - 零售業 AI 應用
    - UX Optimization

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - JavaScript / TypeScript
  frameworks:
    - ASP.NET Core
    - Semantic Kernel
  tools:
    - Azure OpenAI Service
    - GitHub Copilot
    - GitHub Actions
    - Docker / Kubernetes
  platforms:
    - Azure
    - ChatGPT GPTs
  concepts:
    - API Design (OpenAPI / Swagger)
    - Function Calling / Tool Use
    - Copilot Pattern
    - Agent-Engine 協作
    - RAG Pipeline
    - GitOps / CI-CD

### 參考資源
references:
  internal_links:
    - /2023/01/01/api-design-workshop/
    - /2024/02/10/archview-int-app/
    - /2024/03/15/archview-int-blog/
  external_links:
    - https://platform.openai.com/docs/guides/function-calling
    - https://github.com/microsoft/semantic-kernel
    - https://cloud.google.com/use-cases/retrieval-augmented-generation
    - https://hackmd.io/@DevOpsDay/2024
    - https://blog.mickzh.com/blog/2024-devopsdays-taipei/
  mentioned_tools:
    - ChatGPT
    - GPT-4o
    - Kernel Memory
    - OpenAI Embedding
    - Stable Diffusion

### 內容特性
content_metrics:
  word_count: 13800
  reading_time: "45 分鐘"
  difficulty_level: "進階"
  content_type: "Conference Keynote 筆記"

---

## 文章摘要

作者以 DevOpsDays Taipei 2024 Keynote 為例，說明軟體團隊如何從「API First」的思維演進到「AI First」。演講聚焦三件事：

1. 把大型語言模型（LLM）視為「意圖理解介面」，在系統架構中與 Controller 並列，形成 Controller + Copilot 的新 MVC。
2. 高品質的 Domain API 是 AI DX 的基礎。若 API 設計不合理，將消耗大量 prompt 成本並增加錯誤風險。
3. 開發者必須掌握四項基礎功：API First、架構規劃（Copilot / Agent 擺位）、LLM 基礎元件（Embedding、Vector DB、Prompt）、常用 AI 設計模式（RAG、推薦系統）。

文中以四個 Demo 說明：
• Demo 1 「安德魯小舖 GPTs」：用自然語言完成下單流程，展示降維式 UX。
• Demo 2 「滿意度偵測」：LLM 從對話中抽取情緒並寫回資料庫，實現個人化。
• Demo 3 「Console Copilot」：用 Semantic Kernel 在傳統 CLI 旁插入 Copilot，展示 Controller + Copilot 互動。
• Demo 4 「部落格 RAG」：用 Kernel Memory 建立向量索引，強化 GPTs 的專域問答能力。

最後作者提出：AI 運算成本會急速下降，團隊應立即升級 API 設計與部署 Pipeline，預留 AI Agent、Engine 協作的擴充位。

### 關鍵要點

- LLM 已具備「選工具解任務」能力，API 若設計合理即可直接被 AI 使用。
- API DX 決定 AI DX：狀態機、Scope、Idempotent 是關鍵。
- Copilot 是 Controller 的副駕，Agent 則是進階型完全自駕。
- RAG 是目前最實用的 AI 模式：檢索 + 增強可快速擴充私有知識。
- 部署流程將從 3 條線（Code / Config / Env）擴展為 4 條線（+AI Pipeline）。
- 零售業案例證實：AI 強化的 UX 與推薦可直接轉換營收。

---

## 段落摘要

### 1. 寫在前面
回顧 2021–2023 演講脈絡，從 CI/CD→API First→DevOps for Architect 走到 AI First，核心都是「基礎功」。

### 2. Demo 1：降維式購物 UX
對話 + Function Calling 讓使用者「提出需求」而非「下指令」，LLM 負責意圖解析及 API 呼叫。

### 3. Demo 2：情緒偵測與個人化推薦
LLM 自動摘要使用者喜好並寫入客戶註記；交易完成後評估滿意度。展示 AI 取代傳統量化指標。

### 4. Demo 3：Copilot 架構
將 LLM 置於 CLI 側邊，示範 Controller → Copilot → Domain API 的三段式流程，成本低且易導入。

### 5. Demo 4：RAG 與知識強化
利用向量搜尋把部落格文章嵌入 GPTs 上下文，說明 RAG workflow：Query→Embed→Retrieve→Generate。

### 6. 架構與 Pipeline
提出「MVC +AI」架構圖與 GitOps + AIOps 四線 Pipeline，呼應 2021 年 CI/CD 議題。

### 7. 零售業應用串聯
結合 Happy Lee「四種銷售場景」理論，說明 Agent/Engine 如何在實體零售落地。

### 8. 總結
AI 降維打擊並非口號，關鍵在於：API 設計、Prompt Engineering、LLM Ops 及成本優化。

---

## 問答集

### Q1 （概念）什麼是「AI DX」？
A: AI DX 指的是「提供給 AI 使用的開發者體驗」。若 API 命名、參數與狀態轉移符合常理，LLM 便能以最少 Prompt 正確呼叫；反之會導致 Token 浪費與錯誤率上升。

### Q2 （操作）如何讓 GPTs 自動呼叫我的 API？
A: 需在 GPTs 設定頁貼上 OpenAPI spec，並於 Prompt 說明何時使用何種 Function；GPTs 會先思考工具鏈，再輸出 arguments 以 JSON 傳回後端，由系統實際發送 HTTP。

### Q3 （排除）LLM 回答錯誤數值怎麼辦？
A: 對於需精確計算的邏輯，應改由後端服務完成並把結果回寫巨模型；Prompt 中要明確要求「僅用工具計算，不自行推估」。

### Q4 （比較）Agent 與 Copilot 有何差別？
A: Copilot 以人為主，AI 輔助；Agent 以 AI 為主，可自主拆解任務。取決於 LLM 推理能力與 API 完整度。

### Q5 （設計）為何作者主張「狀態機導向 API」？
A: 狀態機將 Domain 行為拆成原子轉移，可天然對應 HTTP 動詞與 Idempotency，避免 CRUD 無限制修改導致資料損毀，更利於 AI 理解流程。

### Q6 （模式）RAG 必要元件有哪些？
A: 有五項
1) 向量化模型（Embedding）
2) Vector Store（搜尋 Top-k）
3) Retriever（加權/排序）
4) Generator（LLM 完成回答）
5) Optional Ranking Model 強化精度。

### Q7 （成本）如何控制 LLM Token 花費？
A: 採取三層策略：
1) Prompt 壓縮（少上下文 + Only 必要字段）
2) 小模型前置（GPT-4o-mini→GPT-4o）
3) 將資料檢索下放到自建向量庫，LLM 僅做摘要。

### Q8 （流程）AI Pipeline 與 CI/CD 如何整合？
A: 建議另建 AI Repo：data → train → eval → serve 流；完成後同步版本號至 App Config Repo，由 GitOps 將模型 URI 與算力配置推上線。

---

## 解決方案整理

### 問題：如何在現有系統導入 Copilot 而不重寫 UI？
**情境**：CLI / Web App 想保留既有操作流程，但希望使用者可隨時求助 AI。
**解決方案**：
- 在 Controller 旁新增 Copilot Service，持續串流使用者操作摘要給 LLM。
- 設計三類觸發事件：Frequent-help、Error-occur、User-ask。
- Copilot 僅回傳建議或已簽署的 API Command，不直接改資料。
**工具/指令**：Semantic-Kernel Planner、Azure OpenAI chat.completions。
**注意事項**：過度頻繁提示會造成干擾；須以 UI 設計節流。

### 問題：API 設計凌亂，AI 無法正確調用
**情境**：舊系統僅有 CRUD，無明確狀態。
**根因**：Domain 行為未抽象，角色/許可混雜。
**解決方案**：
- 以狀態機列出所有轉移；拆成 _Create / _Update/{State} 原子 API。
- 在 Swagger 加註 x-role / x-scope 描述。
- 提供批量 Action API 便利 UI，但標示 "helper" 避免 AI 調用。
**相關工具**：AspNetCore.OpenAPI-Filer、Swashbuckle Filter。
**注意事項**：重構期間需版號並行，勿影響舊客戶端。

### 問題：RAG 查不到最新文章
**情境**：Blog 文章每日發布，向量庫未即時更新。
**根因**：缺少增量 Ingestion Pipeline。
**解決方案**：
- 以 GitHub Actions 每 push 觸發 KM Index rebuild 或增量 update。
- 使用 Embedding Cache 判斷內容變動再刷新。
- 將向量庫與文章 Git commit 綁定版本號，方便回溯。
**指令**：`kmservice index --path posts/2024 --since ${{ github.sha }}`
**注意事項**：分批寫入避免向量庫鎖表，記得做 ANN 重建。

---

## 版本異動紀錄

- v1.0 (2025-08-05)  初版生成，含 Metadata 擴增、摘要、8 組 Q&A 與 3 套解決方案。
