---
- source_file: /docs/_posts/2024/2024-01-15-archview-llm.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# [架構師觀點] 開發人員該如何看待 AI 帶來的改變? —— 全文摘要

## Metadata

```yaml
# 原始 Front Matter
layout: post
title: "[架構師觀點] 開發人員該如何看待 AI 帶來的改變?"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-01-15-archview-llm/2024-01-20-12-29-24.jpg

# 自動擴增 Metadata
primary-keywords:
  - GPTs / Custom GPT
  - LLM (Large Language Model)
  - AI First / Copilot
  - API First / Domain API
  - Semantic Kernel
  - OAuth2
  - AI DX
  - Microsoft AI 佈局
secondary-keywords:
  - Function Calling
  - Vector Database / RAG
  - Planner / Skill / Memory
  - AI PC / NPU
  - UX & Intent
  - DDD / 狀態機
  - Headless API
  - Prompt Engineering

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
    - ChatGPT GPTs
    - Swagger / Swashbuckle
    - Docker / Azure App Service
  platforms:
    - Azure
    - Windows (AI PC)
  concepts:
    - API First / Business Model
    - Function Calling / Tool Use
    - Copilot Pattern
    - Orchestration vs. Calculation
    - OAuth2 / Token Flow
    - DDD / 限定狀態機

references:
  internal_links:
    - /2016/05/05/archview-net-open-source/
    - /2020/03/10/interview-abstraction/
  external_links:
    - https://andrewshopoauthdemo.azurewebsites.net/swagger/index.html
    - https://chat.openai.com/g/g-Bp79bdOOJ-an-de-lu-xiao-pu-v5-0-0
    - https://platform.openai.com/docs/guides/function-calling
    - https://github.com/microsoft/semantic-kernel
    - https://learn.microsoft.com/semantic-kernel/
    - https://github.com/andrew0928/AndrewDemo.NetConf2023
  mentioned_tools:
    - ChatGPT
    - GitHub Copilot
    - Visual Studio / VS Code
    - Azure AI Studio
    - LangChain

content_metrics:
  word_count: 18400
  reading_time: "55 分鐘"
  difficulty_level: "進階"
  content_type: "長篇技術評論 / 架構觀點"
  generated_at: "2025-08-05 23:59 (UTC+8)"
  version: "1.0.0"
```

---

## 文章層級摘要（10–20 句）

作者以「安德魯小舖 GPTs」的 PoC 為切入點，說明 AI 對軟體開發流程與角色分工的全面衝擊。  
1. PoC 展示透過 GPTs + OpenAPI，讓 AI 充當店員以自然語言完成選購、折扣計算、訂單調整與結帳。  
2. 實驗證明 LLM 能理解「意圖」並自動呼叫 API，但前提是 API 設計需 AI Friendly：領域導向、Swagger 完整、OAuth2 標準。  
3. 與傳統 UI/UX 相比，LLM 帶來「降維式 UX」，把意圖與操作翻譯的工作交給 AI，開發者須重構 API 而非堆 UI。  
4. 作者歸納四大開發變革：LLM 成為 OS 核心、Copilot 成為主要介面、Semantic Kernel 融入框架、所有服務皆圍繞 AI。  
5. Microsoft 在模型（Azure OpenAI）、入口（Copilot）、框架（Semantic Kernel）三層的布局被視為最完整的 AI 生態。  
6. 架構師需帶領團隊「AI Ready」：重新設計 Domain API、清楚劃分計算與意圖、讓 OAuth2 等基礎建設自動化。  
7. UI 端則應依 Task 拆解並暴露成 Plugins/Skills 供 Copilot 調用，而非再造複雜流程。  
8. 對開發者而言，Prompt Engineering、向量資料庫、SK/LangChain 是新必修課；GitHub Copilot 等工具能立即提升效率。  
9. 預期未來「Headless API + LLM」將取代許多傳統多頁式/多步驟應用，開發重心轉向核心商業邏輯與高品質 API。  
10. 結論：現在就應善用 AI 提升產能，同時為「AI First」世代累積技術與設計能力，否則風險在於被新范式淘汰。

---

## 段落層級摘要（每個 H2）

### 1. 安德魯小舖 GPTs – Demo
作者以自建購物 API + GPTs Custom Action 實作店長機器人。示範 AI 自動取得商品、試算折扣、修改訂單與列出訂購紀錄。過程暴露 API 認證、流程不直覺時 AI 理解度急遽下降；而當 OAuth2 與 Swagger 完整後，LLM 能補足業務規則並產出人性化摘要，驗證了「API First + LLM」的可行性與威力。

### 2. 軟體開發的改變
分析從鍵盤指令→GUI→Mobile 到 LLM 的 UX 演進。LLM 能真正理解「意圖」，不再單靠 UI 提示推論。未來 App 將由 LLM 做 Orchestration，API 需可被 AI 自主呼叫；不 AI-Ready 的 API 終將被淘汰。

### 3. 看懂 Microsoft 的 AI 技術布局
回顧 Microsoft 從 .NET Core 開源到投資 OpenAI，再到 Azure OpenAI、Copilot 與 Semantic Kernel 的三層佈局。預判 Windows 12 / AI PC 將整合 NPU 與本地 LLM 運算，形成新的 WinTel（或 AI-PC）生態。Semantic Kernel 預計上探 OS / PaaS 標準。

### 4. 架構師／資深人員的角色
架構師須：
1) 劃分「計算 vs. 意圖」邊界；  
2) 以 DDD 設計精準、有限狀態機的 Domain API；  
3) 把 UI 拆成 Task，賦能 Copilot；  
4) 選擇正確框架（SK/LangChain），並指導團隊組裝 Skill/Planner/Memory。

### 5. 開發人員的自我升級
短期使用 ChatGPT / GitHub Copilot 提升工作效率；中長期學習 Prompt Engineering、向量資料庫、Semantic Kernel。持續深化領域建模與 API 抽象能力，因為 LLM 將取代許多「樣板程式」，真正留下的是高價值的 Domain Logic。

### 6. 結論
透過 PoC 與一年反思，作者確信 AI 已是軟體業的新臨界點。立即行動：善用工具、改良 API、導入框架。最終目標是在 AI 世代保持競爭力而非被動適應。

---

## 問答集（共 10 組）

### Q1. 什麼是「降維式 UX」？
A: 降維式 UX 指以自然語言取代多重 UI 操作，讓使用者直接描述意圖，由 LLM 負責解析並呼叫後端 API。這樣的體驗省去導覽與表單填寫，使複雜流程以聊天一次完成。

### Q2. API 要符合哪些「AI Friendly」原則？
A: 1) 領域導向：API 與業務邏輯一一對應；  
2) 完整規格：Swagger/OpenAPI 描述要素與錯誤碼；  
3) 限定狀態機：可預期的流程與失敗路徑；  
4) 標準認證：OAuth2 或 API Key，便於自動取得 Token。

### Q3. 為何 OAuth2 需由程式自動處理而非寫在 Prompt？
A: 認證流程屬「計算」且需高可靠度，交給 LLM 解析變數容易出錯。改由專用 Plugin 或中介元件自動加簽可避免 AI 失控並簡化 Prompt。

### Q4. Semantic Kernel 的核心構件有哪些？
A: Kernel（協調）、Skill（封裝功能）、Planner（推理與拆解任務）、Memory（上下文/向量儲存）、Connector（模型&外部服務介接）。開發者只要實作 Skill 與 Planner，其餘交由 Kernel 管理。

### Q5. 架構師如何判斷某功能應交給 LLM 還是 API？
A: 依「容錯率」與「成本」：需高精度、低延遲者留給傳統 API；需彈性解讀或多策略嘗試者交由 LLM Orchestration。

### Q6. 什麼是 AI PC？對開發者有何意義？
A: AI PC 指內建 NPU 且 OS 內含 LLM 運算管線的設備。開發者可離線執行私域模型、降低雲端成本，並透過 Copilot API 與系統級 LLM 互動。

### Q7. 如何在現有專案導入「AI Ready」？
A: 從 API 整理開始：補 Swagger、自動化測試、統一 OAuth2；再撰寫最小 Prompt 與 GPTs/Kernel 試行；逐步把複雜流程遷出 UI，驗證 ROI 後再擴展。

### Q8. Vector Database 在本篇扮演什麼角色？
A: 當應用需讓 LLM 檢索企業知識（RAG），向量資料庫存儲向量化文本，提供語意查詢。雖 PoC 未用到，但作者建議開發者預先熟悉。

### Q9. AI 時代 UI 工程師會被取代嗎？
A: UI 不會消失，但重心轉向「Task 封裝」與「多模態介面」設計。工程師需懂如何把零散操作包成 Copilot 可調用的最小工作單位，而非僅製作表單。

### Q10. GPTs 偶爾給錯誤答案要如何處理？
A: 透過「結構化回報 + 二次驗證」。API 回傳狀態/結果需可被程式檢查；若 LLM 回傳不一致，啟動副 Planner 或再試一次；必要時將關鍵運算下放 API 以保證正確性。

---

## 問題與解決方案整理

Problem 1: 傳統 UI 難以滿足語意複雜的「意圖操作」。  
Root Cause: UI 操作與使用者思維脫節。  
Solution: 以 LLM 作 Orchestrator，把自然語言轉成 API 呼叫；API 精準封裝商業邏輯。  
Example: 安德魯小舖 GPTs 直接透過對話完成選購與結帳。

Problem 2: API 設計雜亂導致 AI 無法正確調用。  
Root Cause: 缺 Swagger、狀態不嚴謹、認證自訂。  
Solution: 引入 DDD、限定狀態機、標準 OAuth2；自動生成 OpenAPI。  
Example: 作者重寫 OAuth2 Flow 後，GPTs 呼叫成功率提升至 98%。

Problem 3: LLM 運算成本高且有隨機性。  
Root Cause: 把可預測計算錯交給 AI。  
Solution: 劃分「計算 vs. 意圖」，將嚴格計算寫死於 API；LLM 只負責決策。  
Example: 折扣計算放 API，預算規劃交 GPTs 推理。

Problem 4: 團隊對新框架陌生。  
Root Cause: 不懂 SK/LangChain 架構。  
Solution: 架構師先 PoC、小步導入；開發者學 Prompt & Skill；CI 加入 AI 測試。  
Example: 作者計劃以 SK 重構 Demo，並寫教學文分享。

---

## 版本紀錄

- 1.0.0 (2025-08-05) 初版：完成 Metadata 擴增、全文摘要、6 段落摘要、10 Q&A、4 Problem/Solution。