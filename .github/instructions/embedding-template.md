# (文章標題) 從 API First 到 AI First──DevOpsDays Taipei 2024 Keynote 摘要

## Metadata

```yaml
# 原始 Front Matter:
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

# 自動識別關鍵字:
primary-keywords:
  - AI First
  - API First
  - DevOpsDays Taipei
  - Copilot / Agent 架構
  - LLM Function Calling
  - AI DX
  - RAG (Retrieval-Augmented Generation)
secondary-keywords:
  - Semantic Kernel
  - OpenAI GPTs
  - Vector Database
  - Prompt Engineering
  - 系統監控
  - Pipeline / GitOps
  - 零售業 AI 應用
  - UX Optimization

# 技術堆疊分析:
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

# 參考資源:
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

# 內容特性:
content_metrics:
  word_count: 13800
  reading_time: "45 分鐘"
  difficulty_level: "進階"
  content_type: "Conference Keynote 筆記"

```


## 文章摘要

作者分享了一個創新的實驗專案，探討如何利用 AI 的 Function Calling 能力來簡化 API 自動化測試的工作流程。這個被稱為 "Vibe Testing" 的概念，目標是實現從 "Intent"（意圖）到 "Assertion"（斷言）的全自動化測試過程。作者使用 Microsoft Semantic Kernel 框架，結合 OpenAI 的 Function Calling 能力，開發了一個 Test Runner 來自動執行 API 測試案例。實驗以作者先前開發的購物車 API 為測試對象，透過將 OpenAPI Spec 自動轉換為 Semantic Kernel Plugins，讓 AI 能夠理解並執行 API 呼叫。整個測試流程包括準備 domain 層級的測試案例、API 規格文件、以及設計適當的 Prompt 來指導 AI 執行測試。實驗結果證明 AI 能夠成功理解測試意圖，自動決定呼叫順序和參數，並生成詳細的測試報告。作者強調這種方法的關鍵在於 API 必須符合 "AI Ready" 的設計原則，包括按領域設計、精確的規格文件、以及標準化的認證機制。文章展示了 AI 在測試自動化領域的巨大潛力，同時也指出了實際應用時需要考慮的技術門檻和最佳實踐。

文中以四個 Demo 說明：
• Demo 1 「安德魯小舖 GPTs」：用自然語言完成下單流程，展示降維式 UX。
• Demo 2 「滿意度偵測」：LLM 從對話中抽取情緒並寫回資料庫，實現個人化。
• Demo 3 「Console Copilot」：用 Semantic Kernel 在傳統 CLI 旁插入 Copilot，展示 Controller + Copilot 互動。
• Demo 4 「部落格 RAG」：用 Kernel Memory 建立向量索引，強化 GPTs 的專域問答能力。

最後作者提出：AI 運算成本會急速下降，團隊應立即升級 API 設計與部署 Pipeline，預留 AI Agent、Engine 協作的擴充位。

## 關鍵要點

- LLM 已具備「選工具解任務」能力，API 若設計合理即可直接被 AI 使用。
- API DX 決定 AI DX：狀態機、Scope、Idempotent 是關鍵。
- Copilot 是 Controller 的副駕，Agent 則是進階型完全自駕。
- RAG 是目前最實用的 AI 模式：檢索 + 增強可快速擴充私有知識。
- 部署流程將從 3 條線（Code / Config / Env）擴展為 4 條線（+AI Pipeline）。
- 零售業案例證實：AI 強化的 UX 與推薦可直接轉換營收。

---

## 段落摘要 (每個段落一個 H3 標題)

### 構想: 拿 Tool Use 來做自動化測試

作者提出了從 "Intent" 到 "Assertion" 的測試自動化概念，認為過去測試需要大量人工處理的翻譯過程可以透過 AI 的 Function Calling 能力來解決。作者分析了人類執行測試的思考過程，識別出三個關鍵資訊：想要驗證的內容（AC）、領域知識、以及系統的確切規格設計。作者設計了一個清晰的架構圖，展示測試案例如何透過 AI Test Runner 轉換為實際的測試執行和報告生成。文章特別強調這種方法的擴展性，未來可能結合 Browser Use 或 Computer Use 等技術，實現跨不同介面（API、Web、Mobile）的統一測試案例執行。作者的企圖不僅是自動化測試執行過程，更是要釋放撰寫詳細測試文件和按文件執行測試的人力密集工作，類似於 vibe coding 對程式開發的影響。

### 實作: 準備測試案例 (domain)

作者展示了如何準備 domain 層級的測試案例，以購物車 API 為例設計了一個測試商品數量限制的案例。測試案例採用 Given-When-Then 的標準格式，Given 部分設定測試前置條件（清空購物車、指定測試商品），When 部分描述測試步驟（嘗試加入 11 件商品、檢查購物車內容），Then 部分定義預期結果（應回傳 400 錯誤、購物車應為空）。作者強調這種案例的特點是專注於商業邏輯層面，避免包含技術實作細節，使得案例能夠跨不同實作規格重複使用。作者特別提到這個測試案例包含了一個故意的限制（商品上限 10 件），而實際的 API 並未實作這個限制，這是為了模擬 TDD 開發流程中的紅燈階段。文章引用了敏捷三叔公的觀點，強調區分 "展開測試步驟" 和 "思考該測什麼" 的差異，建議將適合 AI 處理的工作交給 AI，讓人類專注於更有價值的決策。

### 實作: 準備 API 的規格 (spec)

作者詳細說明了如何準備 API 規格來支援自動化測試，使用先前開發的安德魯小舖購物車 API 作為測試對象。作者首先分析了測試案例中每個步驟對應的 API 呼叫，包括 Given 階段需要的建立購物車和取得商品清單 API，以及 When 階段的加入商品和查詢購物車 API。作者特別說明了由於 API 設計的限制（沒有搜尋功能），必須透過列舉所有商品來找到指定的測試商品。文章強調 API 規格文件的重要性，指出 AI 能夠精準決定 API 呼叫方式的關鍵在於擁有精確的 OpenAPI Spec。作者提醒讀者，如果 API 還無法提供精準的規格文件，就還沒有條件使用這種自動化測試方法，建議先投資於提升工程成熟度，實現 CI/CD 和自動產生 API 規格文件的能力。

### 實作: 挑選對應的技術來驗證

作者選擇使用 .NET Console Applications 搭配 Microsoft Semantic Kernel 來實作 Test Runner，並說明了技術選擇的考量。文章詳細介紹了 Semantic Kernel 的 OpenAPI 整合功能，展示了如何用僅 10 行程式碼將完整的 Swagger 規格轉換為 AI 可用的 Plugins。作者特別讚賞 Microsoft 在處理複雜的 JSON Schema 和 OpenAPI Spec 轉換上的工程成就。程式碼範例展示了 Kernel 建立、Plugin 匯入、以及 OAuth2 認證處理的完整流程。作者設計了三段式的 Prompt 結構：System 訊息定義處理原則、User 訊息包含測試案例內容、以及報告格式要求。文章強調了 FunctionChoiceBehavior.Auto 設定的重要性，這讓 Kernel 能夠自動處理 Function Calling 的複雜過程。最後作者展示了實際執行結果，包括 API 呼叫過程的詳細記錄和最終的測試報告生成。

### 心得

作者在總結中提出了實作過程中發現的五個重要議題。首先是 API 必須按照領域來設計，避免純 CRUD 式的設計，因為商業邏輯需要封裝在 API 內部才能讓 AI 正確理解和執行。其次是 API 必須有精確的規格文件，強調自動產生的 OpenAPI Spec 的重要性，手工維護的文件無法滿足開發階段頻繁測試的需求。第三是認證授權的標準化處理，作者特別設計了環境控制機制來處理 OAuth2 認證，避免將認證流程與主要測試邏輯混合。第四是需要系統化的測試報告彙整，建議同時產生人類閱讀的 Markdown 和系統整合的 JSON 格式報告。作者最後反思了 AI 對開發人員帶來的改變，認為關鍵是要善用 AI 技術開發更有價值的工具給其他人使用，而不只是談論工具本身有多厲害。文章強調了 Structured Output 和 Function Calling 等技巧的重要性，以及具備 coding 能力在系統整合應用中的優勢。

---

## 問答集 (每個問答集一個 H3 標題)


### Q1: 什麼是 Vibe Testing，它要解決什麼問題？
Q: Vibe Testing 的核心概念是什麼？它想要改善測試過程中的哪些痛點？
A: Vibe Testing 是從 "Intent"（意圖）到 "Assertion"（斷言）的全自動化測試概念。它要解決的核心問題是過去測試過程中需要大量人工處理的翻譯工作，包括撰寫詳細測試文件和按文件執行測試。透過 AI 的 Function Calling 能力，系統能夠理解測試意圖，自動決定 API 呼叫順序和參數，並生成測試報告，釋放人力來專注於更有價值的決策工作。

### Q2: 為什麼選擇 Microsoft Semantic Kernel 作為實作框架？
Q: Semantic Kernel 在這個專案中扮演什麼角色？有什麼特殊優勢？
A: Semantic Kernel 提供了將 OpenAPI Spec 自動轉換為 AI Plugins 的強大功能，僅需 10 行程式碼就能將完整的 Swagger 規格轉換為 Function Calling 可用的工具。它內建支援複雜的 JSON Schema 處理、認證機制整合、以及 Function Calling 的自動化管理，大幅簡化了開發複雜度。相比自己實作 Function Calling 機制，Semantic Kernel 能夠自動處理與 LLM 的溝通過程。

### Q3: 什麼樣的 API 設計適合用於 AI 驅動的自動化測試？
Q: API 需要滿足哪些 "AI Ready" 的設計原則？
A: API 必須滿足三個關鍵原則：1) 按照領域來設計，將商業邏輯封裝在 API 內部，避免純 CRUD 式設計；2) 提供精確的 OpenAPI Spec 規格文件，最好是自動產生而非人工維護；3) 實作標準化的認證授權機制。如果 API 設計先天不良，AI 的不確定性會大幅影響測試執行效果，導致測試路徑混亂發散到無法掌控的程度。

### Q4: 如何處理 API 測試中的認證和環境控制問題？
Q: 在自動化測試中如何妥善處理 OAuth2 等認證機制？
A: 應該將認證機制視為 "測試環境控制" 而非測試步驟來處理。作者設計了專門的 Plugin 來處理環境控制，包括使用者認證、語系、幣別、時區等環境因素。對於 OAuth2 認證，系統會在背景自動完成認證流程並在每個 API 請求中附加 Access Token。這樣做的目的是讓 AI 專注於執行測試邏輯，而不是處理環境配置的複雜性。

### Q5: 測試案例應該如何設計才能發揮 AI 的最大效益？
Q: domain 層級的測試案例有什麼特色？如何避免技術細節干擾？
A: 測試案例應該專注於 domain 層級的商業邏輯，採用 Given-When-Then 格式，避免包含特定的技術實作細節。案例應該描述抽象的業務流程和預期結果，而不是具體的 API 呼叫方式。這樣的設計讓案例能夠跨不同實作規格重複使用，未來即使 UI 或 API 規格改變，同樣的測試案例仍能適用。關鍵是要讓人類專注於 "該測什麼" 的決策，而讓 AI 處理 "怎麼測" 的執行細節。

### Q6: 如何評估這種測試方法的可行性和限制？
Q: 這種 AI 驅動的測試方法在什麼情況下最有效？有哪些使用限制？
A: 這種方法最適合已經具備良好工程成熟度的團隊，包括 CI/CD、自動產生 API 規格文件、以及領域導向的 API 設計。主要限制包括：1) API 必須符合 AI Ready 的設計原則；2) 需要精確且自動維護的規格文件；3) 系統必須有標準化的認證機制。如果這些基礎條件不具備，建議先投資於提升工程成熟度，否則 AI 可能會加速技術債的累積而非提升生產力。


---

## 解決方案

### 問題: 如何實現從測試意圖到自動執行的完整流程
Problem: 傳統 API 測試需要大量人工撰寫詳細測試腳本和執行步驟，過程繁瑣且容易出錯
Root Cause: 測試工具無法理解高層級的測試意圖，需要人工將商業邏輯翻譯成具體的技術操作步驟
Solution:
- 使用 AI 的 Function Calling 能力來橋接測試意圖和具體執行
- 將 OpenAPI Spec 轉換為 AI 可理解的工具集合
- 設計三段式 Prompt 結構：系統原則、測試案例、報告格式
- 採用 Given-When-Then 格式來描述測試案例
- 讓 AI 自動決定 API 呼叫順序、參數生成和結果驗證

Example:
```csharp
await kernel.ImportPluginFromOpenApiAsync(
    pluginName: "andrew_shop",
    uri: new Uri("https://api.example.com/swagger.json"),
    executionParameters: new OpenApiFunctionExecutionParameters()
    {
        EnablePayloadNamespacing = true,
        FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
    }
);

var report = await kernel.InvokePromptAsync<string>(promptTemplate, arguments);
```

### 問題: 如何設計 AI Ready 的 API 來支援自動化測試
Problem: 現有的 API 設計可能不適合 AI 理解和自動執行測試
Root Cause: API 設計過於技術導向，缺乏領域邏輯封裝，或規格文件不夠精確
Solution:
- 採用領域驅動設計（DDD）原則設計 API，將商業邏輯封裝在服務端
- 實作完整且精確的 OpenAPI Spec，最好透過程式碼自動產生
- 提供清晰的 API 文件說明，這些文件會成為 AI 理解的 Prompt
- 避免純 CRUD 式的 API 設計，因為會讓測試邏輯過於分散
- 確保 API 的錯誤處理和狀態管理符合業務規則

Example:
```yaml
# OpenAPI Spec 範例
paths:
  /api/carts/{cartId}/items:
    post:
      summary: "新增商品到購物車"
      description: "將指定數量的商品加入購物車，會檢查庫存和數量限制"
      parameters:
        - name: cartId
          required: true
        - name: productId
          required: true
        - name: qty
          required: true
          maximum: 10  # 明確的業務規則
```

### 問題: 如何處理測試環境中的認證和配置管理
Problem: API 測試需要處理複雜的認證流程和環境配置，這些與核心測試邏輯無關但又必須處理
Root Cause: 認證機制和環境配置被混入測試步驟中，增加了測試案例的複雜度
Solution:
- 設計專門的環境控制 Plugin 來處理認證、語系、時區等配置
- 將認證視為測試環境的一部分，而非測試步驟
- 實作自動化的 OAuth2 認證流程，在背景處理 Access Token 管理
- 使用 Semantic Kernel 的 AuthCallback 機制統一處理 API 認證
- 為不同的測試使用者或角色提供統一的認證介面

Example:
```csharp
executionParameters: new OpenApiFunctionExecutionParameters()
{
    AuthCallback = (request, cancel) =>
    {
        var api_context = APIExecutionContextPlugin.GetContext();
        request.Headers.Add($"Authorization", $"Bearer {userAccessToken}");
        return Task.CompletedTask;
    }
}
```

### 問題: 如何生成有用的測試報告並支援系統整合
Problem: 測試執行後需要產生人類可讀的報告，同時也要支援系統自動化處理
Root Cause: 單一格式的報告無法同時滿足人類閱讀和系統處理的需求
Solution:
- 同時產生 Markdown 和 JSON 兩種格式的測試報告
- Markdown 格式提供詳細的測試步驟和結果說明，便於人類檢視
- JSON 格式提供結構化資料，支援後續的統計分析和警示系統
- 在報告中包含完整的 API 呼叫記錄，包括 Request、Response 和執行結果
- 使用 LLM 的 Structured Output 能力確保 JSON 格式的一致性

Example:
```json
{
  "name": "TC-05 (非法上界)",
  "result": "test_fail", 
  "steps": [
    {
      "api": "AddItemToCart",
      "request": {"productId": 2, "qty": 11},
      "response": {"id": 57, "lineItems": [{"productId": 2, "qty": 11}]},
      "test-result": "fail",
      "test-comments": "未回傳 400，實際加入 11 件"
    }
  ]
}
```



---

## 版本異動紀錄 (從 v1.0 開始, 每次遞增 0.1, 並在每次更新時記錄變更內容)
- 1.1.0 (2025-08-07)  
  • 新增「段落摘要」與「問答集」以提升可讀性。  
  • 擴充「Demo 1」與「Demo 2」的具體實作細節。  

- 1.0.0 (2025-08-05)  初版生成，含 Metadata 擴增、摘要、8 組 Q&A 與 3 套解決方案。
