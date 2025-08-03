---
source_file: "_posts/2024/2024-01-15-archview-llm.md"
generated_date: "2025-08-03 14:30:00 +0800"
version: "1.1"
tools: github_copilot
model: claude_sonnet_3_5
---

# [架構師觀點] 開發人員該如何看待 AI 帶來的改變? - 生成內容

## Metadata

### 原始 Metadata

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

### 自動識別關鍵字

keywords:
  primary:
    - AI
    - LLM
    - 大型語言模型
    - 軟體開發
    - 架構師觀點
    - GPT
    - Copilot
  secondary:
    - API First
    - Semantic Kernel
    - Microsoft
    - Open AI
    - 軟體架構
    - DevOps
    - DDD
    - UX
    - 自然語言
    - 意圖理解

### 技術堆疊分析

tech_stack:
  languages:
    - C#
    - JavaScript
  frameworks:
    - .NET
    - ASP.NET Core
    - Semantic Kernel
  tools:
    - Visual Studio Code
    - GitHub Copilot
    - Chat GPT
    - Azure
  platforms:
    - Azure App Service
    - Windows
    - GPTs
  concepts:
    - Large Language Model
    - API Design
    - Natural Language Processing
    - Software Architecture
    - Domain Driven Design
    - Microservices
    - OAuth2
    - State Machine

### 參考資源

references:
  internal_links:
    - /2016/05/05/archview-net-open-source/
    - /2020/03/10/interview-abstraction/
  external_links:
    - https://chat.openai.com/g/g-Bp79bdOOJ-an-de-lu-xiao-pu-v5-0-0
    - https://andrewshopoauthdemo.azurewebsites.net/swagger/index.html
    - https://github.com/andrew0928/AndrewDemo.NetConf2023
    - https://platform.openai.com/docs/guides/function-calling
    - https://github.com/microsoft/semantic-kernel/
    - https://learn.microsoft.com/en-us/semantic-kernel/overview/
  mentioned_tools:
    - Open AI
    - GPTs
    - Azure Open AI Service
    - Microsoft Copilot
    - Semantic Kernel
    - LangChain
    - GitHub
    - Visual Studio

### 內容特性

content_metrics:
  word_count: 26000
  reading_time: "80 分鐘"
  difficulty_level: "高級"
  content_type: "技術觀點"

## 摘要

### 文章摘要

作者從一個實際的 GPTs 示範案例出發，深入探討 AI 對軟體開發帶來的根本性改變。作者開發了「安德魯小舖 GPT」，透過自然語言對話完成完整的購物流程，從中體認到 LLM 能夠理解使用者意圖並自動轉譯為 API 呼叫的革命性能力。文章分析了軟體開發的三大變革：使用者體驗由 LLM 整合所有資源、所有應用程式都會圍繞 AI 開發、各種角色的職責將重新定義。作者特別深入分析了 Microsoft 的 AI 技術布局，包括 Azure Open AI Service、Copilot 和 Semantic Kernel 三大核心，預測未來軟體開發將以 LLM 為中控中心，API 必須變得更加精準合理以支援 AI 的理解和使用。文章最後為架構師和開發人員提供了具體的轉型建議，強調必須分清楚 LLM 和傳統計算的邊界，掌握 AI 世代的開發框架，並深化領域設計能力來因應這波技術變革。

### 關鍵要點

- LLM 的成熟徹底改變了軟體與使用者的互動方式，能夠理解意圖並轉譯為精確的操作
- 未來軟體開發將以 LLM 為中控中心，負責意圖理解和 API 協調
- API 設計變得更加重要，必須做到 AI Friendly 才能被 LLM 有效使用
- Microsoft 的 AI 布局包含雲端服務、使用者入口和開發框架三個層面
- 架構師必須引領團隊將系統改造成 AI Ready 的應用程式
- 開發人員需要掌握 Prompt Engineering 和 Semantic Kernel 等新技能
- 領域驅動設計和 API First 的重要性將大幅提升
- UI/UX 的改善將大幅轉向 LLM 負責，傳統 UI 專注於特定操作

### 安德魯小舖 GPTs Demo

作者開發了一個完整的購物網站 API，並透過 GPTs 建立了能夠用自然語言完成購物的虛擬店員。這個 PoC 展示了 LLM 如何理解複雜的購物需求，包括預算限制、商品偏好、折扣計算等，並自動呼叫對應的 API 完成交易。最令人驚豔的是 GPTs 能夠「腦補」API 沒有提供的功能，如預算規劃和商品推薦，同時還能處理模糊的語言描述並轉化為精確的操作。整個 Demo 過程顯示，技術門檻相對較低，但需要重新思考應用程式的設計方式，特別是 API 的合理性和標準化變得極為重要。

### 軟體開發的改變

作者指出 LLM 打破了過去 20 年來軟體開發的基礎認知。傳統軟體需要明確指令，而 LLM 能夠理解對話內容背後的意圖，這是降維打擊式的改變。未來的軟體將由 LLM 整合所有資源，扮演自然語言與函數呼叫之間的轉換器。使用者體驗的改善將不再依賴傳統 UI/UX 優化，而是透過 LLM 理解意圖來實現。所有應用程式都將圍繞 AI 開發，API 不再是給開發者看的火星文，而是要能被 AI 理解和正確使用。這要求 API 設計必須更加合理、標準化和嚴謹，因為無法預測或約束 AI 的呼叫方式。

### Microsoft 的 AI 技術布局

作者分析了 Microsoft 的三大 AI 核心布局：Azure Open AI Service 提供雲端 AI 運算能力和模型服務；Copilot 作為作業系統層級的使用者入口，將演變成整個設備的控制中心；Semantic Kernel 作為 AI 應用的主要開發框架，定義了未來軟體開發的生態系統。這三者緊密相扣，共同構建了從雲端服務到本地應用的完整 AI 生態。作者預測 Windows 12 將整合更多 AI 基礎建設，LLM 會變成作業系統的核心元件，Copilot 將成為主要的操作介面，而 Semantic Kernel 將主導未來的軟體開發模式。

### 架構師的職責變化

架構師必須引領團隊將系統逐步改造成 AI Ready 的應用程式。關鍵在於分清楚哪些問題用「計算」解決，哪些用「意圖」解決。需要精準執行的任務如交易處理仍應使用傳統方式，而需要理解意圖的任務如客服對話則應善用 LLM。API 設計必須精準合理，要麼完全符合現實世界的運作邏輯，要麼做到邏輯無懈可擊。UI 應該以 Task 為單位拆解，配合 Copilot 的擴充機制。架構師還必須挑選正確的軟體開發框架，掌握 Semantic Kernel 等 AI 整合框架的精神，並正確地將系統元件擺在框架的適當位置上。

### 開發人員的轉型建議

開發人員需要熟悉能提高工作效能的 AI 工具，如 GitHub Copilot 和 Chat GPT，但同時要確保理解工具給出的建議而不是盲目接受。技術棧方面需要掌握 Prompt Engineering、Vector Database 和 Semantic Kernel 的實作能力。最重要的是深化領域的設計與開發能力，因為 UI 和流程的比重降低後，剩下的核心 API 開發會變得更加重要。所有領域都會去蕪存菁，不需要經驗的範本程式碼將被 AI 取代，留下的都是需要高度經驗和精準開發能力的工作。DDD、API First 等領域相關設計將成為 Backend Developer 的主戰場。

## 問答集

### Q1: 為什麼說 LLM 的成熟是「降維打擊」？
Q: LLM 相比傳統 UX 優化有什麼根本性的不同？
A: 傳統 UX 改善都是在「操作」層面讓指令變簡單，但使用者仍需清楚「指令」與「結果」的對應關係。LLM 的突破在於能夠理解對話內容背後的「意圖」，直接解決了使用者意圖與操作之間的隔閡。這是用截然不同的方式解決問題，傳統 UX 優化無論如何努力都跟不上 LLM 的進步。

### Q2: 什麼是 AI Friendly 的 API 設計？
Q: 如何設計讓 AI 能夠正確理解和使用的 API？
A: AI Friendly 的 API 必須具備兩個特質：一是設計合情合理，完全符合現實世界的運作邏輯，讓 LLM 能夠望文生義；二是邏輯無懈可擊、滴水不漏，無論 AI 用什麼順序呼叫都不會發生意料之外的結果。關鍵在於精準對應 Business Model，使用有限狀態機控制行為，並提供清楚的文件說明。

### Q3: Semantic Kernel 在 AI 應用開發中扮演什麼角色？
Q: Semantic Kernel 如何改變傳統的軟體開發模式？
A: Semantic Kernel 是 AI 世代的 MVC 框架，將 LLM 整合到應用程式的標準架構。它區分了 Kernel、Skill、Planner、Memory、Connector 等元件，讓 LLM 扮演 Controller 或更精確地說是 Orchestration 的角色。LLM 負責理解自然語言背後的意圖，翻譯成精確指令轉發給後端服務，是「精確運算」與「模糊語意分析」之間的橋樑。

### Q4: 為什麼說 API First 在 AI 時代變得更重要？
Q: AI 如何改變了 API 在軟體架構中的地位？
A: 在 AI 時代，LLM 會分掉 UI/UX 的大部分工作，應用程式變成 API First 而非 UI First。呼叫 API 的不再是其他開發者，而是無法預測行為的 AI。如果 API 無法被 AI 善用，服務就會變成孤島。因此 API 必須變得更加標準化、合理化，成為 LLM 的 Plugins，這讓 API 設計的重要性大幅提升。

### Q5: 開發人員需要掌握哪些新技能來適應 AI 時代？
Q: 面對 AI 變革，開發人員應該學習什麼技術？
A: 主要包含三個方面：一是 Prompt Engineering 能力，作為 LLM 與 API 之間的黏著劑；二是技術棧如 Vector Database、NoSQL Database 和 Semantic Kernel 的實作能力；三是深化領域設計能力，特別是 API First、DDD 和微服務設計，因為未來只會剩下核心關鍵的 API 開發，而且會越來越重要。

### Q6: 未來的軟體架構會如何改變？
Q: LLM 將如何重塑軟體系統的整體架構？
A: 未來軟體將以 LLM 為中控中心，所有操作先轉化為自然語言交給 LLM「思考」該調用哪些功能。LLM 會變成作業系統的核心元件，Copilot 成為主要操作介面，而開發框架也會配合這樣的架構抽象化。應用程式會圍繞 LLM 開發，UI 專注於特定操作，而 LLM 負責統控操作流程和意圖理解。

## 解決方案

### 問題：如何設計能被 AI 有效使用的 API 架構
Problem: 傳統 API 設計無法有效支援 AI 的理解和使用，導致 LLM 難以正確呼叫或產生錯誤結果
Root Cause: 
- 技術面：API 設計不夠標準化，缺乏一致性的介面規範
- 流程面：沒有考慮 AI 使用情境，仍以人類開發者為主要使用者
- 人為面：架構師對 AI Friendly 設計的認知不足

Solution:
- 採用領域驅動設計（DDD）確保 API 精準對應 Business Model
- 實作有限狀態機控制所有可能的操作流程和狀態轉換
- 提供詳細的 OpenAPI/Swagger 文件，包含清楚的自然語言描述
- 使用標準化的認證方式（OAuth2、API Key）
- 確保 API 設計合情合理，符合現實世界的運作邏輯
- 實作嚴謹的錯誤處理和驗證機制

Example:
```csharp
[ApiController]
[Route("api/[controller]")]
public class OrderController : ControllerBase
{
    /// <summary>
    /// 建立新訂單。需要有效的購物車，且購物車不能為空。
    /// 建立後訂單狀態為 'Created'，需要後續呼叫付款 API 完成交易。
    /// </summary>
    [HttpPost("create")]
    public async Task<OrderResponse> CreateOrder([FromBody] CreateOrderRequest request)
    {
        // 實作狀態機驗證邏輯
        if (!await _cartService.IsValidCart(request.CartId))
            throw new InvalidOperationException("購物車無效或為空");
            
        return await _orderService.CreateOrder(request);
    }
}
```

### 問題：如何在團隊中導入 AI 驅動的開發模式
Problem: 團隊缺乏 AI 整合的經驗和框架，不知道如何開始改造現有系統
Root Cause:
- 技術面：缺乏 AI 整合的開發框架和最佳實務
- 流程面：現有開發流程未考慮 AI 組件的整合和測試
- 人為面：團隊成員對 AI 技術的理解程度不一

Solution:
- 採用 Semantic Kernel 等成熟的 AI 應用開發框架
- 建立 Plugins 機制，將現有 API 逐步包裝為 AI 可用的元件
- 實作 Prompt Engineering 規範和測試流程
- 建立 Memory 和 Connector 的標準架構
- 分階段改造，優先處理適合 AI 的使用場景
- 建立 AI 組件的監控和品質管控機制

Example:
```csharp
// Semantic Kernel Plugin 範例
public class ShoppingPlugin
{
    [KernelFunction("add_to_cart")]
    [Description("將商品加入購物車")]
    public async Task<string> AddToCart(
        [Description("商品ID")] int productId,
        [Description("數量")] int quantity)
    {
        // 呼叫現有的購物車 API
        var result = await _cartService.AddItem(productId, quantity);
        return $"已將 {quantity} 件商品 {productId} 加入購物車";
    }
}
```

### 問題：如何平衡 LLM 和傳統計算的使用邊界
Problem: 不清楚什麼情況下應該使用 LLM，什麼時候應該使用傳統程式邏輯
Root Cause:
- 技術面：對 LLM 的能力限制和成本考量認識不足
- 流程面：缺乏評估 AI 適用性的決策流程
- 人為面：傾向過度依賴或完全排斥 AI 技術

Solution:
- 建立「計算」vs「意圖」的分類標準
- 精準執行的任務（如交易、計算）使用傳統程式邏輯
- 需要理解意圖的任務（如客服、推薦）使用 LLM
- 考慮執行成本，LLM 用於省開發時間而非 runtime 成本
- 建立 fallback 機制，LLM 失敗時有傳統邏輯接手
- 持續監控和評估各種任務的處理效果

Example:
```csharp
public class OrderService
{
    // 精準計算：使用傳統邏輯
    public decimal CalculateDiscount(Cart cart)
    {
        // 確定性的折扣計算邏輯
        return _discountEngine.Calculate(cart);
    }
    
    // 意圖理解：使用 LLM
    public async Task<List<Product>> RecommendProducts(string naturalLanguageRequest)
    {
        // 讓 LLM 理解使用者需求並推薦商品
        var prompt = $"根據需求推薦商品：{naturalLanguageRequest}";
        return await _llmService.GetRecommendations(prompt);
    }
}
```

## 版本異動紀錄

### v1.1 (2025-08-03)
- 初始版本生成
- 完整分析文章的 AI 觀點和技術變革內容
- 提供架構師和開發人員的轉型建議
- 包含 Microsoft AI 技術布局分析
