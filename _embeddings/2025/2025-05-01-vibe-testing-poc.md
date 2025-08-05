---
- source_file: /docs/_posts/2025/2025-05-01-vibe-testing-poc.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2025-05-01-vibe-testing-poc/logo.jpg

# 自動識別關鍵字
primary-keywords:
  - Vibe Testing
  - Intent-to-Assertion
  - API 自動化測試
  - LLM Function Calling
  - Semantic Kernel Test Runner
  - AI-Ready API
  - Andrew Shop API
  - Domain Test Case
secondary-keywords:
  - OpenAPI / Swagger
  - Structured Output (JSON Mode)
  - Plugin Import
  - OAuth2
  - FunctionChoiceBehavior
  - TDD / PoC
  - Browser-Use / Computer-Use
  - MCP Server
  - RAG with SK / KM
  - .NET Console App

# 技術堆疊
tech_stack:
  languages:
    - C#
  frameworks:
    - .NET 8 Console
    - Microsoft Semantic Kernel
  tools:
    - Azure/OpenAI Chat Completions
    - Swagger / Swashbuckle
    - Postman (對照)
    - GitHub Copilot / Cursor (輔助開發)
  platforms:
    - Azure App Service
    - Windows / VS Code
  concepts:
    - Function Calling / Tool-Use
    - Intent → Action → Assertion Pipeline
    - Domain-Driven API Design
    - Structured Output & JSON Schema
    - OAuth2 Token Injection
    - Test-Driven Development (TDD)

# 參考資源
references:
  internal_links:
    - /2024/07/20/devopsdays-keynote/
    - /2023/01/01/api-design-workshop/
    - /2022/10/26/apifirst/
    - /2024/01/15/archview-llm/
  external_links:
    - https://andrewshopoauthdemo.azurewebsites.net/swagger/index.html
    - https://docs.browser-use.com/introduction#overview
    - https://docs.anthropic.com/en/docs/agents-and-tools/computer-use
    - https://agile3uncles.com/2025/05/05/genai-end-testing/
    - https://www.youtube.com/watch?v=q9J1YzhW6yc
  mentioned_tools:
    - ChatGPT / GPT-4o-mini
    - Microsoft Semantic Kernel
    - Kernel Memory
    - GitHub Copilot
    - Cursor / Windsurf

# 內容特性
content_metrics:
  word_count: 9800
  reading_time: "32 分鐘"
  difficulty_level: "中-高階"
  content_type: "Technical PoC / 架構實驗筆記"
```

## 文章摘要
作者延續 2023「安德魯小舖」的經驗，嘗試將 LLM 的 Function Calling 能力用於 API 自動化測試，目標是把「Intent-to-Assertion」全流程交給 AI。  
做法如下：  
1. 先以 ChatGPT 生成 15 筆 domain-level 測試案例（Given / When / Then），避免落入 UI 或參數細節。  
2. 使用 Microsoft Semantic Kernel 的 OpenAPI 匯入功能，將 Andrew Shop Swagger 一鍵轉成 Plugin，讓 LLM 能直接呼叫 16 支 API。  
3. 撰寫僅 50 行左右的 Test Runner（.NET Console），透過三段 Prompt（System、User、User）驅動 Function Calling，自動登入 OAuth2、串接步驟、收集 Response。  
4. 要求雙格式報告：Markdown 方便人讀、JSON 方便系統彙整；LLM 以 Structured Output 技巧同時產出。  
5. 首個測試案例「嘗試加入 11 件可口可樂」如預期失敗（API 尚未實作商品上限），驗證 PoC 可行。  

作者並歸納五點心得：  
A) API 必須 Domain-Driven，避免純 CRUD；B) 必須維持精確且自動生成的 OpenAPI Spec；C) 認證/環境控制須統一抽象；D) 報告需結構化以利統計與警示；E) AI 帶來的是「寫工具的能力」而非僅用工具。整體證明，在 AI-Ready 的條件下，API 測試從腳本撰寫到結果彙整皆可自動化，大幅解放工程師人力。

## 關鍵要點
- LLM Tool-Use + 精確 OpenAPI Spec = 「零腳本」API 測試。  
- Semantic Kernel 內建 ImportPluginFromOpenApiAsync，10 行碼完成 16 支 API 的 Tool 封裝。  
- 測試案例保持在 Domain 層級（Intent），UI / API 規格變動時僅需重展步驟。  
- OAuth2 Token 透過自訂 Plugin 注入，避免 LLM 虛構或重複登入。  
- Markdown 報告給人看，JSON 報告給系統整合；Structured Output 是關鍵技巧。  
- 問題不在技術，而在「API 是否 AI-Ready」：Domain-Driven、狀態明確、Spec 自動化。  
- 未來可延伸同一份案例到 Web / Mobile UI 測試，只要替換對應規格與 Runner。  

---

## 段落摘要

### 1. 構想：用 Tool-Use 驅動 Intent → Assertion
作者將傳統手動編寫測試腳本的流程重新拆解：先定義 AC，再交由 LLM 解析 Spec、選 API、執行並斷言，讓 AI 取代「翻譯意圖 → 指令」的人力。

### 2. 實作（一）：準備 Domain-Level 測試案例
以「單商品限購 10 件」為例，寫出 Given / When / Then；完全不含參數細節，只描述商業意圖，確保案例對 UI / API 介面變動免疫。

### 3. 實作（二）：準備 API 規格
沿用 Andrew Shop Swagger；人腦推演需呼叫 CreateCart、GetProducts、AddItem、GetCart 等 API，並列出對應 URI、Headers、Payload，作為 Prompt 提示。

### 4. 實作（三）：建置 Test Runner
4-1 匯入 OpenAPI → SK Plugin；4-2 編寫三段 Prompt（System 規則、User 案例、User 報告格式）；4-3 執行並生成 Markdown + JSON 報告，驗證案例失敗顯示紅燈。

### 5. 心得與限制
5-1 API 必須 Domain-Driven；5-2 Spec 必須自動同步；5-3 認證/環境需統一抽象；5-4 報告需結構化；5-5 AI 讓開發者從「寫測試程式」轉向「寫測試工具」。

---

## 問答集

Q1（概念）什麼是「Intent-to-Assertion」？  
A: 指從測試意圖（驗證條件）到最終斷言結果的完整鏈條。過去需工程師寫腳本對應 API 及檢查點，現在可交由 LLM 自動解析並執行。

Q2（操作）如何把 Swagger 變成 LLM 可用 Tool？  
A: 在 Semantic Kernel 呼叫 `ImportPluginFromOpenApiAsync`，傳入 swagger.json URL，即會自動轉成 Kernel Plugins，無需手動定義每支函式。

Q3（排除）若 API 規格與程式碼不同步會怎樣？  
A: LLM 會依 Spec 組請求，若實際 API 參數不同將導致 4xx/5xx，測試被標為「執行失敗」。因此 Spec 必須由 CI/CD 自動產生。

Q4（比較）Postman 錄製腳本與本方案差在哪？  
A: Postman 靠錄製重播，仍需工程師手動處理變數；LLM 方案依 Domain 案例即時推理每一步，不需硬編參數，也能適應 API 介面調整。

Q5（概念）什麼是 AI-Ready API？  
A: 指 Domain-Driven、狀態明確、參數自描述的 API，具備完整 OpenAPI Spec，使 LLM 能零提示猜測地正確呼叫。

Q6（操作）如何處理 OAuth2 登入？  
A: 透過自訂 `APIExecutionContextPlugin` 先取得 Access-Token，再由 ExecutionParameters 於每次呼叫自動附加 Authorization Header。

Q7（問題排除）LLM 回傳快取結果怎麼辦？  
A: 在 System Prompt 明確禁止「假資料」或 Cache，並在 Plugin Execution 打開 HTTP Debug，確保每次請求直連 API。

Q8（比較）Domain-Case 與 UI-Case 差別？  
A: Domain-Case 聚焦商業規則，與介面無關；UI-Case 聚焦元素定位與視覺驗證。前者一份案例可映射多介面，後者須為每介面獨寫。

Q9（策略）為何要同時輸出 JSON 報告？  
A: Markdown 便於閱讀，但難以聚合統計。JSON 與 Schema 配合，可被 CI Pipeline 收集，生成趨勢圖或觸發警示。

Q10（未來）何時能擴展到 Web UI 測試？  
A: 待 Browser-Use / Computer-Use 成本下降、穩定度提高，即可用相同測試案例 + UI 規格，換接不同 Runner 進行跨平台驗證。

---

## 問題與解決方案

### 問題 1：測試腳本撰寫耗時、維護成本高  
Root Cause：參數硬編、流程改動即失效  
Solution：以 Domain Intent 編寫案例，交由 LLM 根據最新 OpenAPI Spec 動態決定步驟；透過 SK Plugin 自動更新函式簽章  
Example：示範「11 件商品」案例，Prompt 僅 10 行，無需任何硬編腳本。

### 問題 2：API 不符合 AI-Ready，LLM 難以正確呼叫  
Root Cause：CRUD 式設計缺乏狀態語意  
Solution：重構為狀態機導向 API；明確動詞、Idempotent、錯誤碼；Spec 自動產生並上版號  
Example：將 `AddItemToCart` 拆成 `AddItem` / `UpdateQty` / `RemoveItem`，並於 Spec 加註限制條件。

### 問題 3：OAuth2 流程阻斷自動化  
Root Cause：瀏覽器互動需人工  
Solution：事先於 Runner 植入「UserContext Plugin」：CLI 取得 Token → 設定全域 Header；LLM 僅負責業務 API  
Example：Plugin 先打 `/oauth/token` 取得 JWT，再於每次 Function Call 注入。

---

## 版本異動紀錄
- 1.0.0 (2025-08-05)  
  • 初版生成：含 Metadata、段落摘要、10 組 Q&A、3 項問題-解決方案。  
