---
source_file: "_posts/2025/2025-06-22-inside-semantic-kernel.md"
generated_date: "2025-08-03 16:00:00 +0800"
version: "1.0"
tools: github_copilot
model: claude_sonnet_3_5
---

# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用 - 生成內容

## Metadata

### 原始 Metadata

layout: post
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2025-06-22-inside-semantic-kernel/livecast-logo.png

### 自動識別關鍵字

keywords:
  primary:
    - Microsoft Semantic Kernel
    - Microsoft Kernel Memory
    - RAG
    - Function Calling
    - .NET RAG
    - Structured Output
  secondary:
    - OpenAI
    - Chat Completion API
    - JSON Mode
    - Vector Database
    - MCP
    - Model Context Protocol
    - Embedding
    - LLM Application

### 技術堆疊分析

tech_stack:
  languages:
    - C#
  frameworks:
    - .NET
    - Microsoft Semantic Kernel
    - Microsoft Kernel Memory
    - OpenAI .NET SDK
  tools:
    - Visual Studio
    - Docker
    - Claude Desktop
    - Bing Search API
  platforms:
    - Azure
    - Docker Hub
    - GitHub
  concepts:
    - RAG (Retrieval Augmented Generation)
    - Function Calling
    - Vector Search
    - Document Processing
    - AI Pipeline
    - Model Context Protocol

### 參考資源

references:
  internal_links: []
  external_links:
    - https://www.facebook.com/andrew.blog.0928/
    - https://www.youtube.com/watch?v=q9J1YzhW6yc
    - https://forms.gle/A2JUNYexvWRx7fa79
    - https://github.com/andrew0928/AndrewDemo.DevAIAPPs
    - https://docs.google.com/presentation/d/e/2PACX-1vQcfNQlTZlThjYD08LFnGhFfLd904W1ceX76A9Z8MQUSHmYSbRdSPykFX0eOzIipL-2v536guFhE7ro/pub
    - https://chatgpt.com/share/67e174b1-f734-800d-b904-08e1fa4c3b26
    - https://chatgpt.com/share/67e1754e-5afc-800d-b766-1158b4a7ced3
    - https://chatgpt.com/share/12GFiqp8MnL/
    - https://chatgpt.com/share/674e882a-5bb4-800d-a8e6-64b5e7395c9a
    - https://chatgpt.com/share/6747d8ca-2b10-800d-9696-ea8c24017d79
  mentioned_tools:
    - Microsoft Semantic Kernel
    - Microsoft Kernel Memory
    - OpenAI Chat Completion API
    - Docker
    - Claude Desktop
    - Bing Search API
    - Vector Database
    - MCP (Model Context Protocol)
    - JSON Schema
    - Entity Framework

### 內容特性

content_metrics:
  word_count: 25000
  reading_time: "60 分鐘"
  difficulty_level: "中高級"
  content_type: "技術教學"

## 摘要

### 文章摘要

這篇文章是作者與保哥合作直播的完整內容整理，系統性地介紹了 .NET 生態系中最重要的 AI 開發工具組合：Microsoft Semantic Kernel 與 Microsoft Kernel Memory。文章採用循序漸進的方式，從最基礎的 OpenAI Chat Completion API 開始，逐步深入到複雜的 RAG 應用和系統整合。作者強調了 AI 應用開發的三個核心技巧：Structured Output（JSON Mode）、Function Calling 和 RAG，並將這些技術比喻為 AI 時代的基礎流程控制技巧。文章特別詳細地說明了 Function Calling 的工作原理，從基本的指令解析到複雜的多步驟任務執行，展示了 LLM 如何從自然語言意圖轉換為具體的程式執行序列。在 RAG 部分，作者分享了實際應用 Microsoft Kernel Memory 處理部落格文章的經驗，包括如何透過 LLM 生成多重視角的檢索內容來提升 RAG 效果。文章也深入探討了不同的系統整合方式，包括 MCP（Model Context Protocol）的應用，並提供了大量的實作範例和程式碼。最後，作者還分享了直播問卷的統計結果，展現了社群對這些技術的關注程度和學習需求。

### 關鍵要點

- Microsoft Semantic Kernel 和 Kernel Memory 是 .NET 生態系最成熟的 AI 開發工具組合
- Structured Output、Function Calling 和 RAG 是 AI 應用開發的三大核心技巧
- Function Calling 實現了從自然語言意圖到程式執行序列的自動轉換
- RAG 的關鍵在於針對檢索需求優化內容，而非單純的文件分段
- Microsoft Kernel Memory 提供了從 serverless 到分散式系統的完整 RAG 解決方案
- MCP 協議為 AI 工具整合提供了標準化的通訊方式
- 透過 LLM 生成多重視角的檢索內容可以顯著提升 RAG 效果
- AI 應用開發需要理解底層原理才能做出合適的架構決策

### Chat Completion API 基礎

作者從最基本的 OpenAI Chat Completion API 開始介紹，強調這是所有 LLM 應用的基礎。API 的核心概念是將完整的對話歷史發送給模型，模型根據前後文生成下一個回應。作者詳細解釋了 API 的五個主要組成部分：認證標頭、模型參數（如 temperature）、訊息列表（包含不同角色的對話）、可選的工具定義，以及回應格式規範。作者特別強調了訊息角色的重要性，包括 system（系統提示）、user（使用者輸入）和 assistant（AI 回應）。這個基礎理解對於後續學習更複雜的 Function Calling 和 RAG 應用至關重要。作者提供了 HTTP、OpenAI .NET SDK 和 Semantic Kernel 三種不同的實作方式，讓開發者了解從低階到高階的不同抽象層級。

### Structured Output (JSON Mode)

作者深入討論了 JSON Mode 在 AI 應用開發中的重要性，將其比喻為 LLM 與程式碼之間的資料交換基礎。相較於在 ChatGPT 中隨意提問，在應用程式中使用 LLM 需要考慮三個關鍵問題：回應格式的標準化、失敗情況的明確處理，以及單一職責原則的應用。作者強調使用 JSON Schema 可以讓 LLM 輸出結構化資料，便於程式碼後續處理。同時建議在 JSON 輸出中明確標示執行結果的成功或失敗狀態，避免程式需要猜測結果。作者也提醒開發者應該讓 LLM 專注於其擅長的推理任務，而將格式轉換、數值計算等工作交給程式碼處理，這樣不僅效率更高，成本也更低。這種設計思維對於建構可靠的 AI 應用程式非常重要。

### Function Calling 基礎與進階

作者將 Function Calling 稱為 LLM 普及以來威力最大的功能，詳細說明了其工作原理。基礎的 Function Calling 包含三個要點：預先定義可用工具、區別三方對話（使用者、LLM、工具），以及讓 LLM 生成工具使用的指令和參數。作者用購物清單管理的例子說明基本原理，展示 LLM 如何將自然語言意圖轉換為結構化的指令序列。進階應用則展示了多步驟任務執行的完整流程，以行事曆預約為例，說明 LLM 如何透過連續的工具呼叫來完成複雜任務。整個過程包含七個步驟的對話歷史，從使用者需求到最終確認，LLM 需要理解前後文並做出合適的決策。作者強調這種連續互動的能力使得 AI Agent 和各種智能應用成為可能，是現代 AI 應用的核心技術基礎。

### RAG 與 Function Calling 的整合

作者闡述了 RAG（檢索增強生成）實際上是 Function Calling 的一種特殊應用。RAG 的基本流程包含三個步驟：將問題轉換為檢索條件、執行檢索操作，以及基於檢索結果生成答案。作者巧妙地指出，透過適當的 system prompt 和工具定義，LLM 可以自動判斷何時需要進行檢索，並自動生成檢索所需的查詢參數。這種設計讓 LLM 彷彿具備了使用搜尋引擎的能力，能夠在需要時主動查找資訊。作者提供了實際的範例，展示如何結合 Bing Search API 和其他工具，讓 LLM 能夠根據使用者位置查詢景點資訊並提供天氣建議。這種整合方式的關鍵在於選擇合適的檢索服務，作者推薦 Microsoft Kernel Memory 作為最適合的 RAG 服務基礎。

### Microsoft Kernel Memory 深度應用

作者詳細介紹了 Microsoft Kernel Memory（MSKM）的設計理念和應用方式。MSKM 解決了 AI 應用中長期記憶管理的複雜問題，提供了從文件處理到向量檢索的完整 pipeline。與 Semantic Kernel 的 Memory 抽象不同，MSKM 處理了文件匯入的整個流程，包括內容提取、文字分段、向量化和儲存。作者特別讚賞 MSKM 的彈性設計，既可以作為獨立的網路服務部署，也可以直接內嵌在應用程式中使用。MSKM 與 Semantic Kernel 的整合特別緊密，內建支援 SK 的 Memory Plugin，同時也支援 SK 的各種 AI 服務連接器。作者強調 MSKM 適合有一定 AI 應用開發基礎的開發者使用，需要具備前面介紹的基礎技巧才能充分發揮其價值。

### 進階 RAG 優化策略

基於實際應用經驗，作者分享了顯著提升 RAG 效果的優化策略。傳統的文件分段方式在處理長文章時效果不佳，特別是當查詢角度與文章撰寫角度不一致時。作者提出了透過 LLM 生成多重視角檢索內容的解決方案，包括全文摘要、段落摘要、FAQ 清單，以及問題解決方案案例。這種方法解決了使用者查詢視角與作者撰寫視角不匹配的問題。作者實際測試了用 OpenAI o1 模型生成這些檢索專用內容，再標記適當的標籤後加入向量資料庫。這種做法的成本效益很高，因為內容生成只需要在文章發布或更新時執行一次，而使用者查詢次數與此無關。作者強調 RAG 更像是設計模式而非固定產品，需要根據具體應用場景進行客製化調整。

### 系統整合與 MCP 協議

作者介紹了 LLM Function Calling 的多種整合方式，包括 ChatGPT Custom Action、No Code 平台、Claude Desktop MCP，以及 Semantic Kernel 本地整合。這些方式的核心都是解決兩個問題：告知 LLM 可用的 function 規格，以及提供統一的 function 執行機制。作者特別深入介紹了 MCP（Model Context Protocol）這個新興標準，將其比喻為 AI 的 USB-C。MCP 透過標準化的通訊協定，支援 stdio 和 HTTP（基於 SSE）兩種通訊方式，讓不同語言和平台都能與 LLM 進行標準化整合。作者實際演示了使用 MCP C# SDK 將 MSKM 封裝成 MCP Server，並整合 Claude Desktop 進行 RAG 應用。雖然在實作過程中遇到了中文編碼和 JSON 處理的問題，但這些都是可以解決的技術細節。

### 土炮 Function Calling 原理

作者回應了社群關於不支援 Function Calling 的模型如何實現相似功能的疑問，詳細說明了土炮 Function Calling 的實作原理。關鍵在於理解 Function Calling 只是 Chat Completion API 的特殊應用模式，透過擴展訊息角色定義來實現。作者設計了一個有趣的例子，透過 system prompt 定義三個角色的對話規則：使用者（安德魯大人）、AI 助理（管家）和工具執行者（秘書）。AI 透過不同的訊息前綴來區分對話對象，應用程式則攔截特定格式的訊息來執行相應的功能。這種方法雖然比較土炮，但確實可以在不支援原生 Function Calling 的模型上實現類似功能。作者強調這個例子主要是為了幫助理解底層通訊過程，實際應用中還是建議使用支援 Function Calling 的模型和成熟的框架。

## 問答集

### Q1: 為什麼說 Structured Output、Function Calling 和 RAG 是 AI 應用開發的基礎技巧？
Q: 這三個技術在 AI 應用開發中扮演什麼樣的角色？為什麼如此重要？
A: 這三個技術解決了 AI 應用開發的核心問題：Structured Output 建立了 LLM 與程式碼之間的資料交換基礎，讓 AI 輸出能夠被程式直接處理；Function Calling 實現了 AI 與外部系統的互動能力，讓 AI 能夠執行具體的操作而不只是回答問題；RAG 則解決了 AI 的知識時效性和專業領域知識不足的問題。作者將它們比喻為 AI 時代的 if、for loop 等基礎流程控制，是每個 AI 應用開發者都必須掌握的核心技能。

### Q2: Microsoft Kernel Memory 相比其他 RAG 解決方案有什麼優勢？
Q: MSKM 的設計理念和技術優勢是什麼？適合什麼樣的應用場景？
A: MSKM 的主要優勢在於其完整性和彈性。它提供了從文件處理到向量檢索的完整 pipeline，而不只是向量資料庫的抽象層。MSKM 可以從 serverless 模式內嵌到應用程式，也可以擴展為分散式系統，滿足不同規模的需求。與 Semantic Kernel 的緊密整合讓 .NET 開發者可以無縫使用各種 AI 服務連接器。MSKM 特別適合需要處理大量文件、要求高度客製化 RAG pipeline，以及希望保持對整個處理流程控制權的開發團隊。

### Q3: 如何透過 LLM 生成多重視角的檢索內容來提升 RAG 效果？
Q: 傳統文件分段的問題是什麼？如何透過生成多重視角內容來解決？
A: 傳統文件分段的問題在於查詢視角與內容撰寫視角的不匹配。例如使用者問「WSL 能幹嘛」，但文章內容都是具體的技術細節，向量檢索很難找到合適的摘要性內容。解決方案是透過 LLM 為每篇文章生成多種視角的內容：全文摘要、段落摘要、FAQ 清單、問題解決方案等。這些生成的內容會標記適當的標籤並加入向量資料庫，讓檢索系統能夠從不同角度找到相關資訊。這種方法的成本效益很高，因為內容生成只需在文章發布時執行一次。

### Q4: Function Calling 的工作原理是什麼？如何實現連續的多步驟任務？
Q: Function Calling 如何讓 LLM 從理解意圖到執行具體操作？
A: Function Calling 的核心是讓 LLM 能夠在對話過程中呼叫預定義的工具。工作原理包含三個要點：1）預先定義可用工具的規格和參數；2）LLM 在對話中判斷何時需要使用工具；3）LLM 生成工具呼叫的指令和參數。對於多步驟任務，LLM 會根據每次工具執行的結果來決定下一步動作，形成完整的對話歷史。例如預約行事曆的例子中，LLM 先呼叫查詢行事曆工具，根據查詢結果找到空檔，再呼叫新增事件工具完成預約。整個過程體現了 LLM 強大的推理和規劃能力。

### Q5: MCP（Model Context Protocol）協議的意義和應用前景如何？
Q: MCP 解決了什麼問題？對 AI 工具整合有什麼影響？
A: MCP 解決了 AI 工具整合標準化的問題，被作者比喻為「AI 的 USB-C」。它定義了標準的通訊協定，包括工具列表、工具呼叫、資源管理等操作，支援 stdio 和 HTTP 兩種通訊方式。MCP 讓不同語言、不同平台的工具都能以統一的方式與 LLM 整合，大大降低了系統整合的複雜度。例如透過 MCP，同一個 RAG 服務可以同時被 Claude Desktop、VS Code、Cursor 等不同的 AI 應用程式使用，而不需要為每個平台開發專門的整合程式碼。這將促進 AI 工具生態系的發展和標準化。

### Q6: 在什麼情況下需要「土炮」Function Calling？如何實作？
Q: 當模型不支援原生 Function Calling 時，如何實現類似功能？
A: 當使用不支援原生 Function Calling 的模型時，可以透過精心設計的 system prompt 來實現類似功能。核心原理是利用 LLM 的推理能力和對話理解能力，透過特定的訊息格式來區分不同的對話對象。例如定義「安德魯大人您好」開頭的訊息是給使用者看的，「請執行指令」開頭的訊息是要執行的工具呼叫。應用程式攔截特定格式的訊息並執行相應操作，再將結果加入對話歷史。雖然這種方法比較土炮，但確實可以在推理能力足夠的模型上實現 Function Calling 的效果。不過實際應用中還是建議使用原生支援的模型和成熟框架。

## 解決方案

### 問題: 如何選擇合適的 LLM 整合技術棧
Problem: 在眾多的 AI 開發框架和工具中，如何選擇最適合的技術組合來開發 LLM 應用
Root Cause: AI 開發領域變化快速，工具繁多，缺乏清晰的技術選擇指導原則
Solution:
- 對於 .NET 開發者，優先選擇 Microsoft Semantic Kernel + Kernel Memory 的組合
- 根據應用複雜度選擇不同的整合方式：簡單應用使用 HTTP Client，複雜應用使用 SK
- 了解底層 Chat Completion API 的工作原理，以便在需要時進行客製化
- 掌握 Structured Output、Function Calling、RAG 三大核心技巧
- 選擇工具時考慮生態系整合度、文件完整性和社群支援

Example:
```csharp
// 簡單場景：直接使用 OpenAI SDK
var client = new OpenAIClient(apiKey);
var response = await client.GetChatCompletionsAsync(model, messages);

// 複雜場景：使用 Semantic Kernel
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(model, apiKey)
    .Build();
await kernel.ImportPluginFromOpenApiAsync("api", swaggerUrl);
```

### 問題: 如何設計高效的 RAG 系統
Problem: 傳統的文件分段和向量檢索方式在實際應用中效果不佳，特別是長文件和複雜查詢
Root Cause: 使用者查詢視角與文件撰寫視角不匹配，單純的文件分段無法提供合適的檢索粒度
Solution:
- 使用 LLM 為文件生成多重視角的檢索內容（摘要、FAQ、解決方案等）
- 建立合適的標籤系統來區分不同類型的檢索內容
- 選擇支援完整 pipeline 的 RAG 服務如 Microsoft Kernel Memory
- 在文件更新時重新生成檢索內容，而非在查詢時處理
- 根據應用場景調整檢索策略和相關性算法

Example:
```csharp
// 使用 Semantic Kernel 生成多視角內容
var summaryPrompt = "為以下文章生成結構化摘要...";
var faqPrompt = "將以下文章轉換為FAQ格式...";

var summary = await kernel.InvokePromptAsync(summaryPrompt, arguments);
var faq = await kernel.InvokePromptAsync(faqPrompt, arguments);

// 將不同視角的內容加入 Kernel Memory
await memory.ImportTextAsync(summary, tags: ["type:summary"]);
await memory.ImportTextAsync(faq, tags: ["type:faq"]);
```

### 問題: 如何實現複雜的 AI Agent 工作流程
Problem: 需要 AI 能夠自動執行多步驟任務，涉及多個外部系統的協調和決策
Root Cause: 單純的 prompt 無法處理複雜的流程控制和狀態管理
Solution:
- 使用 Function Calling 讓 AI 能夠調用外部工具和服務
- 設計清晰的工具接口和參數規範（使用 OpenAPI Spec）
- 實作適當的錯誤處理和重試機制
- 使用 Semantic Kernel 的 Plugin 系統來組織和管理工具
- 建立完整的對話歷史來維護任務執行的上下文

Example:
```csharp
[KernelFunction]
public async Task<string> CheckSchedule(DateTime startTime, DateTime endTime)
{
    // 檢查行事曆邏輯
    return JsonSerializer.Serialize(events);
}

[KernelFunction] 
public async Task<string> AddEvent(DateTime startTime, int duration, string title)
{
    // 新增事件邏輯
    return "success";
}

// AI 會自動決定調用順序和參數
var result = await kernel.InvokePromptAsync(
    "幫我找明早30分鐘的空檔安排慢跑", arguments);
```

### 問題: 如何標準化 AI 工具的系統整合
Problem: 不同的 AI 應用和平台有不同的整合方式，缺乏統一的標準
Root Cause: AI 工具生態系發展初期，各平台都有自己的整合協議
Solution:
- 採用 MCP（Model Context Protocol）作為標準化的整合協議
- 設計可重用的 MCP Server 來封裝核心 AI 功能
- 使用 OpenAPI Spec 來定義工具接口，支援多種整合方式
- 建立適當的抽象層來隔離不同平台的差異
- 確保工具能夠在多個 AI 應用中重複使用

Example:
```csharp
// 實作 MCP Server
public class KernelMemoryMCPServer : IServer
{
    public async Task<ToolResponse> InvokeTool(string name, JsonNode arguments)
    {
        return name switch
        {
            "search" => await SearchKnowledgeBase(arguments),
            "upload" => await UploadDocument(arguments),
            _ => throw new NotSupportedException()
        };
    }
}

// 同時支援 Semantic Kernel Plugin
[KernelFunction]
public async Task<string> SearchKnowledgeBase(string query, int limit = 5)
{
    return await _memoryService.SearchAsync(query, limit);
}
```

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本
