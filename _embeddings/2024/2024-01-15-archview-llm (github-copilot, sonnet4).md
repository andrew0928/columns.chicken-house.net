---
source_file: "_posts/2024/2024-01-15-archview-llm.md"
generated_date: "2025-08-03 10:30:00 +0800"
version: "1.1"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# [架構師觀點] 開發人員該如何看待 AI 帶來的改變? - 生成內容

## 原始 Metadata

```yaml
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
```

## 擴增 Metadata

### 自動識別關鍵字
keywords:
  primary:
    - AI
    - LLM
    - GPT
    - 架構師
    - 軟體開發
    - API
    - Copilot
    - Semantic Kernel
  secondary:
    - Microsoft
    - Azure
    - 開發框架
    - 使用者體驗
    - 自然語言
    - 機器學習
    - 程式設計

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - JSON
  frameworks:
    - ASP.NET Core
    - Semantic Kernel
    - LangChain
  tools:
    - Visual Studio
    - GitHub Copilot
    - Azure
    - Docker
    - Open AI API
  platforms:
    - Azure App Service
    - Windows
    - Chat GPT
    - GPTs
  services:
    - Azure Open AI Service
    - Microsoft Copilot

### 參考資源
references:
  internal_links:
    - /2016/05/05/archview-net-open-source/
    - /2020/03/10/interview-abstraction/
  external_links:
    - https://openai.com/blog/introducing-gpts
    - https://platform.openai.com/docs/guides/function-calling
    - https://github.com/microsoft/semantic-kernel/
    - https://andrewshopoauthdemo.azurewebsites.net/swagger/index.html
  mentioned_tools:
    - Chat GPT
    - GPTs
    - Microsoft Copilot
    - GitHub Copilot
    - Semantic Kernel
    - LangChain
    - Azure Open AI Service

### 內容特性
content_metrics:
  word_count: 15000
  reading_time: "45 分鐘"
  difficulty_level: "高級"
  content_type: "深度分析"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)
本文是作者對 AI 時代軟體開發變革的深度思考和實踐總結。作者以九年前分析 .NET 開源轉型的文章為引子，指出當前 AI 技術帶來的變革規模更甚以往。透過實作「安德魯小舖 GPTs」這個創新的購物助手 PoC，作者親身驗證了大型語言模型（LLM）如何突破傳統軟體開發的核心認知。文章核心觀點是 LLM 能夠理解使用者的「意圖」並轉化為精確的 API 呼叫，這打破了過去 20 年來電腦只能處理明確指令的限制。作者深入分析了 Microsoft 在 AI 領域的技術布局，包括 Azure Open AI Service、Copilot 和 Semantic Kernel 三大支柱如何形成完整生態系。文章進一步探討軟體架構將如何演變，預測 LLM 將成為應用程式的中控中心，傳統的 MVC 架構將被 AI 驅動的新架構取代。最後，作者為架構師和開發人員提供具體的轉型建議，強調必須重新思考 API 設計、使用者體驗和技能發展策略，以在 AI 時代保持競爭力。這篇文章不僅是技術分析，更是對整個軟體產業未來發展方向的前瞻性思考。

### 關鍵要點 (Key Points)
- AI 突破了傳統軟體開發的核心認知，LLM 能理解使用者意圖並轉化為精確的 API 呼叫
- 軟體架構將以 LLM 為中控中心，整合 UI、服務和 API 的協作模式
- Microsoft 透過 Azure Open AI Service、Copilot 和 Semantic Kernel 建構完整的 AI 生態系
- 架構師必須重新設計 AI-friendly 的 API，開發人員需要掌握新的技術棧和開發框架
- 未來的軟體開發將圍繞 AI 展開，傳統的 MVC 架構將被 AI 驅動的新架構取代

### 段落摘要 (Section Summaries)
1. **安德魯小舖 GPTs Demo**：作者透過實作一個完整的線上購物 GPTs 應用程式，深度驗證了 AI 與 API 整合的可能性和威力。這個 PoC 展示了 GPTs 如何理解自然語言需求，自動呼叫商品查詢、購物車管理、折扣計算和結帳等 API，完成複雜的購物流程。最令人驚艷的是 GPTs 能夠「腦補」許多 API 未直接提供的功能，如預算規劃、商品推薦等高階商業邏輯。測試過程中，作者刻意設計了多個刁難情境，包括預算限制、商品替換、訂單調整等複雜需求，GPTs 都能準確理解並執行。這個實驗證明了 LLM 不僅能處理標準化流程，更能應對充滿變化和模糊需求的真實業務場景。作者特別強調，這種能力的實現關鍵在於 API 的設計必須合理且符合業務邏輯，而非依賴複雜的 Prompt 說明。整個 Demo 展現了 AI 時代軟體開發的新可能性，也為後續的理論分析提供了堅實的實證基礎。

2. **軟體開發的改變**：作者深入分析了 LLM 如何從根本上改變軟體開發的核心模式。傳統軟體開發中，使用者意圖與具體操作之間存在巨大隔閡，所有的 UX 改善都在試圖縮小這個落差，但效果有限。LLM 的成熟徹底打破了這個限制，它能直接理解自然語言背後的意圖，並轉化為精確的系統操作。這種「降維打擊」式的革新，讓傳統的 UI/UX 優化方式顯得過時。作者指出，未來的軟體架構將以 LLM 為中控中心，所有的使用者輸入都先轉化為自然語言，由 LLM 分析並決定該調用哪些功能模組。這個架構變革的核心是 LLM 具備了「思考」能力，能夠理解上下文並做出合理判斷。相對地，API 的重要性將大幅提升，因為它們成為 LLM 與現實世界連接的唯一橋樑。作者強調，這不是漸進式改良，而是架構層面的根本性變革，所有無法被 AI 善用的 API 都將成為落伍的武器。

3. **Microsoft AI 技術布局**：作者以歷史視角審視 Microsoft 在技術轉型上的策略，將當前的 AI 布局與過去的 .NET 開源化、雲端轉型等重大變革相提並論。Microsoft 的 AI 戰略圍繞三大支柱展開：Azure Open AI Service 提供強大的雲端 AI 運算能力，Copilot 作為統一的 AI 操作介面滲透到各個產品線，Semantic Kernel 則提供標準化的 AI 應用開發框架。這三者形成緊密相扣的生態系統，從基礎設施到開發工具到使用者介面全面覆蓋。作者預測未來的作業系統將內建 LLM 能力，Windows 12 可能成為第一個真正的「AI OS」。同時，硬體發展也會配合這個趨勢，AI PC 的概念將重新定義 Wintel 聯盟。Microsoft 的策略不僅是技術投資，更是對整個軟體產業生態的重新塑造。作者認為，這種全方位的布局讓 Microsoft 在 AI 時代具備了類似過去 Windows + Office 組合的戰略優勢，有望重新定義軟體開發和使用的標準模式。

4. **架構師的角色變化**：在 AI 時代，架構師的職責發生了根本性變化，需要具備全新的思維模式和技能組合。首要任務是學會區分「計算」與「意圖」的邊界，判斷哪些任務適合用傳統的精確計算處理，哪些應該交給 LLM 的語意理解能力。這種判斷直接影響系統的可靠性、效能和成本。其次，API 設計變得極其關鍵，因為 AI 無法像人類開發者一樣容忍不合理的設計，架構師必須確保 API 完全符合領域邏輯且 AI-friendly。第三，UI 設計思維需要從頁面導向轉向任務導向，重新思考使用者流程的組織方式。最後，架構師必須掌握 AI 時代的開發框架，如 Semantic Kernel，並能合理配置 LLM、Plugins、Memory 等元件。作者強調，架構師的價值在於引領團隊完成系統的 AI 化改造，這不是技術升級，而是思維模式的根本轉變。成功的架構師必須既懂傳統的軟體工程原則，又能靈活運用 AI 的新能力，在兩者之間找到最佳平衡點。

5. **開發人員的準備**：對於開發人員而言，AI 時代既帶來挑戰也提供機遇，關鍵在於及時調整技能結構和工作方式。短期內，開發人員應該積極擁抱 AI 工具，如 GitHub Copilot、ChatGPT 等，用它們提升日常開發效率，同時透過使用過程深入理解 AI 的能力邊界。中長期來看，技術棧會發生顯著變化，Prompt Engineering 將成為基礎技能，Vector Database 和 NoSQL 的重要性將提升，Semantic Kernel 等 AI 開發框架將成為主流。更重要的是，開發人員需要深化領域設計能力，特別是 API 設計、DDD（領域驅動設計）和微服務架構，因為這些技能在 AI 時代變得更加關鍵。作者指出，未來的軟體開發將出現明顯的分化：簡單重複的程式碼將被 AI 取代，而需要深度領域知識和精準設計能力的工作將變得更加重要。開發人員必須從「程式碼工人」轉型為「領域專家」，專注於核心業務邏輯的精確實現，而將重複性工作交給 AI 處理。這種轉變要求開發人員不斷學習和適應，但也為職業發展開啟了新的可能性。

## 問答集 (Q&A Pairs)

### Q1: 什麼是大型語言模型 (LLM)，它如何改變軟體開發？
Q: 大型語言模型 (LLM) 對軟體開發帶來什麼根本性的改變？
A: LLM 最大的突破是能理解自然語言背後的「意圖」，並將其轉化為精確的 API 呼叫。這打破了過去 20 年來軟體開發的基礎認知 - 電腦只能處理明確指令。LLM 能擔任「精確運算」與「模糊語意分析」之間的橋樑，讓軟體系統具備理解使用者真實需求的能力。

### Q2: GPTs 如何實現自然語言與 API 的整合？
Q: 在安德魯小舖的 Demo 中，GPTs 是如何理解使用者需求並呼叫對應的 API？
A: GPTs 透過 Function Calling 機制，讀取 API 的 Swagger 定義和描述，學習各個 API 的用途和參數。當使用者用自然語言提出需求時，GPTs 會分析語意，判斷該呼叫哪些 API，並從對話中萃取出正確的參數值，最後將 API 回應結果重新整理成自然語言回覆給使用者。

### Q3: 為什麼 API 設計在 AI 時代變得更加重要？
Q: AI 時代對 API 設計有什麼新的要求？
A: 因為呼叫 API 的不再是其他開發者，而是 AI。AI 無法像人類一樣理解不合理的設計或特例處理，因此 API 必須設計得合情合理，完全符合現實世界的運作邏輯。API 需要做到「AI Friendly」- 讓 AI 能夠望文生義地理解使用方式，而不需要過多的文件說明或特殊處理。

### Q4: Semantic Kernel 在 AI 應用開發中扮演什麼角色？
Q: Microsoft Semantic Kernel 框架解決了什麼問題？
A: Semantic Kernel 是專為 AI 應用開發設計的框架，它整合了 LLM、Memory、Plugins 和 Planner 等元件。類似傳統的 MVC 架構，Semantic Kernel 為開發者提供了標準化的方式來建構 AI 驅動的應用程式，讓 LLM 能統控操作流程並協調各種服務的協作。

### Q5: Microsoft 的 AI 技術布局包含哪些關鍵要素？
Q: Microsoft 在 AI 領域的技術布局有哪三個核心？
A: Microsoft 的 AI 布局有三個關鍵：1) Azure Open AI Service - 提供雲端 AI 運算能力和模型服務；2) Copilot - 作為 OS 層級的 AI 操作介面和中控中心；3) Semantic Kernel - 提供 AI 應用的開發框架。這三者緊密相扣，形成從基礎服務到開發工具的完整生態系。

### Q6: 架構師在 AI 時代需要具備哪些新能力？
Q: 面對 AI 變革，架構師的職責有什麼改變？
A: 架構師需要：1) 分清楚哪些任務適合用「計算」解決，哪些適合用「意圖理解」解決；2) 設計精準合理的 API，確保能被 AI 正確理解和使用；3) 以 Task 為單位重新思考 UI 設計；4) 選擇正確的 AI 開發框架並合理配置各元件。架構師必須引領團隊將系統逐步改造成 AI Ready 的應用程式。

### Q7: 傳統的 MVC 架構在 AI 時代會被取代嗎？
Q: AI 應用開發需要什麼樣的新架構？
A: 傳統 MVC 不再適合處理 AI 驅動的應用程式。新的架構以 LLM 為中心，LLM 扮演 Orchestration 的角色，接收自然語言輸入，判斷該呼叫哪些後端服務，並將結果重新整理成自然語言輸出。這種架構更靈活但也更複雜，需要專門的框架如 Semantic Kernel 來支援。

### Q8: 開發人員該如何準備迎接 AI 時代？
Q: 開發人員需要學習哪些新技術來適應 AI 變革？
A: 開發人員應該：1) 熟悉 AI 工具如 GitHub Copilot 和 ChatGPT 來提升工作效率；2) 學習新的技術棧包括 Prompt Engineering、Vector Database、Semantic Kernel；3) 深化領域設計能力，特別是 API 設計、DDD 和微服務架構。重點是要理解 AI 的特性，知道什麼時候該用 AI，什麼時候該用傳統程式設計。

## 解決方案 (Solutions)

### P1: 如何設計 AI-friendly 的 API
Problem: 傳統 API 設計無法被 AI 有效理解和使用
Root Cause: API 設計不夠直觀，包含太多特例和不合理的流程，需要人工文件說明
Solution: 
- 採用 Domain-Driven Design (DDD) 原則，確保 API 精確對應 Business Model
- 實作有限狀態機，控制 API 的呼叫順序和狀態變化
- 提供完整的 OpenAPI/Swagger 規格，包含清晰的 API 描述
- 遵循 RESTful 設計原則，讓 API 語義化且易於理解
Example: 
```json
// 良好的 API 設計範例
POST /api/carts/{cartId}/items
GET /api/carts/{cartId}/estimate
POST /api/checkout/create
```

### P2: 整合 LLM 與現有系統架構
Problem: 現有系統架構無法有效整合 LLM 能力
Root Cause: 傳統 MVC 架構無法處理自然語言輸入和意圖理解
Solution:
- 採用 Semantic Kernel 等 AI 應用開發框架
- 將 LLM 定位為系統的 Orchestration 中心
- 重新設計應用程式的分層架構，以 AI 為核心
- 建立 Plugins 機制，讓現有服務能被 LLM 調用
Example:
```csharp
// Semantic Kernel 基本架構
var kernel = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(model, endpoint, apiKey)
    .Build();

kernel.ImportPluginFromObject(new ShoppingPlugin());
```

### P3: 提升開發團隊的 AI 能力
Problem: 開發團隊缺乏 AI 相關技術能力
Root Cause: AI 技術發展快速，傳統開發經驗不足以應對新需求
Solution:
- 建立 AI 學習計畫，包含 Prompt Engineering、Vector Database 等新技術
- 實作 PoC 專案，讓團隊親身體驗 AI 整合過程
- 強化基礎能力如 API 設計、領域建模等核心技能
- 建立 AI 工具使用規範，提升開發效率
Example:
```bash
# 學習路徑範例
1. 使用 GitHub Copilot 提升編碼效率
2. 學習 Prompt Engineering 基礎
3. 實作 Semantic Kernel 應用
4. 整合 Vector Database 處理 RAG
```

### P4: 重新定義使用者體驗設計
Problem: 傳統 UI/UX 設計無法發揮 AI 的優勢
Root Cause: 過度依賴 UI 操作，忽略了自然語言互動的可能性
Solution:
- 以 Task 為單位重新設計使用者流程
- 整合 Copilot 等 AI 助手作為主要操作介面
- 保留 UI 處理精確操作，讓 AI 處理模糊需求
- 設計混合式互動模式，結合 UI 和自然語言
Example:
傳統流程：開啟 APP → 瀏覽商品 → 加入購物車 → 結帳
AI 增強流程：告訴 Copilot "我要買飲料，預算 500 元" → AI 自動完成整個購物流程

### P5: 建立 AI 時代的技術架構標準
Problem: 缺乏統一的 AI 應用架構標準和最佳實踐
Root Cause: AI 技術還在快速發展階段，缺乏成熟的架構模式
Solution:
- 制定 AI 應用的架構原則和設計模式
- 建立標準化的 Plugins 開發規範
- 設計統一的 API 認證和安全機制
- 建立 AI 應用的測試和部署流程
Example:
```yaml
# AI 應用架構標準
architecture:
  core: LLM (Semantic Kernel)
  plugins: Domain APIs
  memory: Vector Database
  ui: Hybrid (Traditional UI + Copilot)
  deployment: Azure AI Services
```

## Version Changes
- v1.1 (2025-08-03): 修正摘要格式，改用第三人稱敘述，加入生成工具資訊
- v1.0 (2025-08-03): 初始版本
