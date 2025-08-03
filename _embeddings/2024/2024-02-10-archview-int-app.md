---
source_file: "_posts/2024/2024-02-10-archview-int-app.md"
generated_date: "2025-08-03 14:45:00 +0800"
version: "1.1"
tools: github_copilot
model: claude_sonnet_3_5
---

# 替你的應用程式加上智慧! 談 LLM 的應用程式開發 - 生成內容

## Metadata

### 原始 Metadata

layout: post
title: "替你的應用程式加上智慧! 談 LLM 的應用程式開發"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆", "AI", "Semantic Kernel"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-02-10-archview-int-app/2024-02-17-10-06-40.png

### 自動識別關鍵字

keywords:
  primary:
    - LLM
    - Semantic Kernel
    - AI 應用程式開發
    - 智慧化
    - 架構師觀點
    - Function Calling
    - Copilot
  secondary:
    - Azure OpenAI
    - RAG
    - Prompt Engineering
    - Vector Database
    - 系統架構
    - API 設計
    - 軟體框架
    - 自然語言處理
    - Agent
    - Memory

### 技術堆疊分析

tech_stack:
  languages:
    - C#
  frameworks:
    - .NET 8
    - Semantic Kernel
    - ASP.NET Core
  tools:
    - Azure OpenAI
    - Visual Studio
    - Chat GPT
  platforms:
    - Azure
    - Console Application
  concepts:
    - Large Language Model
    - Retrieval Augmented Generation
    - Function Calling
    - Vector Storage
    - Text Embedding
    - Prompt Engineering
    - AI Agent
    - Natural Language Processing

### 參考資源

references:
  internal_links:
    - /2024/01/15/archview-llm/
  external_links:
    - https://chat.openai.com/g/g-Bp79bdOOJ-an-de-lu-xiao-pu-v5-0-0
    - https://learn.microsoft.com/en-us/semantic-kernel/overview/
    - https://learn.microsoft.com/zh-tw/azure/ai-services/openai/overview
    - https://platform.openai.com/docs/guides/function-calling
    - https://platform.openai.com/docs/assistants/overview
    - https://github.com/andrew0928/AndrewDemo.NetConf2023
    - https://github.blog/2023-10-30-the-architecture-of-todays-llm-applications/
    - https://youtu.be/JhCl-GeT4jw
  mentioned_tools:
    - Semantic Kernel
    - Azure OpenAI
    - GPT4
    - Chat GPT Plus
    - Open AI Assistant API
    - LLaMa 2
    - Vector Database
    - RAG

### 內容特性

content_metrics:
  word_count: 23000
  reading_time: "70 分鐘"
  difficulty_level: "高級"
  content_type: "技術實作"

## 摘要

### 文章摘要

作者延續前一篇文章的 AI 思考，深入探討如何將 LLM 智慧整合到實際應用程式中。文章以「安德魯小舖」為例，展示了應用程式智慧化的四個發展階段：從標準操作模式，到使用 AI 評估操作意圖，再到全程輔助提示，最終實現完全對話式操作。作者使用 Azure OpenAI 和 Semantic Kernel 重新實作了購物系統，詳細說明了每個階段的技術實現方式和設計考量。文章深入分析了 LLM 應用的系統架構，包括短期記憶（Chat History）、長期記憶（RAG 知識庫）、技能系統（Function Calling）等核心組件，並詳細解釋了 Semantic Kernel 開發框架如何整合這些元件。作者特別強調了 Prompt Engineering 和 Skills 設計的重要性，認為這是運用 LLM 的兩大關鍵能力。最後，作者展望了程式開發的未來，認為自然語言可能成為未來的程式語言，而 LLM 將扮演新時代的執行環境角色。

### 關鍵要點

- 應用程式智慧化分為四個漸進式發展階段，每個階段都有其特定的應用場景和技術挑戰
- LLM 的核心價值在於語言理解能力，需要搭配適當的記憶和技能系統才能發揮實用價值
- Semantic Kernel 提供了完整的 AI 應用開發框架，抽象化了模型、記憶、技能等核心組件
- Prompt Engineering 是控制 LLM 行為的關鍵技術，需要精心設計和反覆測試調整
- Function Calling 讓 LLM 具備執行實際任務的能力，是 AI 從對話走向實用的重要突破
- RAG 技術解決了 LLM 知識範圍限制的問題，提供了可擴展的知識檢索機制
- API 設計在 AI 時代變得更加重要，需要考慮 AI 的理解和使用方式
- 未來程式開發可能朝向自然語言程式設計的方向發展，開發者的角色將重新定義

### 安德魯小舖的四階段進化

作者以「安德魯小舖」為實例，展示了應用程式智慧化的完整發展路徑。第一階段提供標準的選單式操作作為對照組；第二階段在關鍵環節（如結帳）使用 AI 評估操作意圖和風險，透過精心設計的 System Prompt 和 FAQ 清單，讓 AI 能夠識別不合理的購買行為並給出適當提醒；第三階段實現 Copilot 式的全程輔助，AI 會持續監控使用者的操作過程，適時提供建議和警告；第四階段達到完全對話式操作，使用者可以用自然語言描述需求，AI 會自動解讀意圖並呼叫對應的 API 完成任務。每個階段都展示了不同程度的智慧化水準和對應的技術實現方式。

### LLM 應用的系統架構設計

作者深入分析了 LLM 應用的核心架構組件。LLM 本身只是無狀態的語言模型，需要 Chat History 提供短期記憶能力，讓 AI 能夠理解對話的前後文關係。RAG（Retrieval Augmented Generation）技術提供長期記憶，透過 Text Embedding 將知識向量化儲存，使用時進行語意檢索，解決了 LLM 知識範圍有限的問題。Skills 系統透過 Function Calling 讓 LLM 具備執行實際任務的能力，AI 能夠理解自然語言需求，決定呼叫哪些 API 並提供適當參數。Persona 設定則定義了 AI 的角色和行為模式。這些組件整合後，形成了完整的智慧應用架構，能夠處理從意圖理解到任務執行的完整流程。

### Semantic Kernel 開發框架

Semantic Kernel 是 Microsoft 提供的 AI 應用開發框架，抽象化了 AI 應用的核心組件。Models 層支援多種 LLM 和 AI 模型的整合；State/Memories 層提供向量資料庫和記憶管理；Side Effects/Plugins 層定義了 AI 可以執行的技能。框架採用 Attribute 機制標記可供 AI 呼叫的函數，透過 Description 提供自然語言描述，讓 LLM 能夠理解函數的用途和參數。開發者只需要專注於業務邏輯的實現和 Prompt 的設計，框架會處理 LLM 與函數之間的橋接工作。這種設計模式讓傳統應用程式的智慧化變得更加簡單和標準化。

### Prompt Engineering 的重要性

作者強調 Prompt Engineering 是運用 LLM 的關鍵技術之一。不同於傳統程式設計的精確指令，Prompt 需要用自然語言描述 AI 的角色、任務和行為規則。作者在實作中設計了詳細的 System Prompt，包含店長的人物設定、標準作業流程和 FAQ 清單，讓 AI 能夠在不同情境下給出適當的回應。User Prompt 的設計也很重要，需要包含足夠的上下文資訊讓 AI 做出正確判斷。Prompt 的品質直接影響 AI 的表現，需要經過反覆測試和調整才能達到理想效果。這種基於自然語言的程式設計模式代表了軟體開發的新典範。

### 未來程式開發的展望

作者預測未來程式開發將朝向自然語言程式設計的方向發展。當 LLM 的運算效能和成本問題得到解決後，自然語言可能成為新的程式語言，而 LLM 則扮演新時代的執行環境角色。開發者的主要工作將從寫程式碼轉向設計 Prompt 和定義業務邏輯。這種轉變類似於從組合語言到高階語言的歷史發展，雖然增加了抽象層次和運算成本，但大幅提升了開發效率和程式的可理解性。AI 的不確定性問題可以透過適當的系統設計和容錯機制來處理，就像企業用人一樣接受一定程度的不完美但獲得更大的彈性和創造力。

## 問答集

### Q1: 應用程式智慧化的四個階段分別是什麼？
Q: 如何漸進式地為現有應用程式加入 AI 功能？
A: 四個階段分別是：(1)標準操作模式作為基礎；(2)在關鍵環節使用 AI 評估操作意圖和風險；(3)全程提供 Copilot 式輔助，監控操作過程並適時提醒；(4)完全對話式操作，使用者可用自然語言完成所有任務。建議從第二階段開始，在最需要智慧判斷的環節引入 AI，逐步擴展到其他功能。

### Q2: RAG 技術如何解決 LLM 的知識限制問題？
Q: RAG 的運作原理是什麼？如何實現知識檢索？
A: RAG 透過 Text Embedding 將知識文件向量化，儲存在向量資料庫中。使用時將使用者問題同樣向量化，在向量空間中搜尋相似的知識片段，將檢索結果作為上下文提供給 LLM 進行回答。這個過程模擬了人腦的聯想和記憶檢索機制，讓 LLM 能夠存取大量外部知識而不需要重新訓練模型。

### Q3: Function Calling 如何讓 LLM 具備執行能力？
Q: LLM 如何理解和呼叫 API 函數？
A: LLM 透過函數的自然語言描述（Description Attribute）理解函數的用途和參數。當使用者提出需求時，LLM 會分析意圖，決定需要呼叫哪些函數，並從對話內容中推導出所需的參數值。Semantic Kernel 框架會處理函數呼叫的技術細節，將 LLM 的決策轉換為實際的方法呼叫，並將結果回傳給 LLM 進行後續處理。

### Q4: Prompt Engineering 有哪些關鍵技巧？
Q: 如何設計有效的 Prompt 來控制 AI 行為？
A: 關鍵技巧包括：(1)清楚定義 AI 的角色和責任範圍；(2)提供詳細的工作流程和標準作業程序；(3)包含常見問題的處理方式（FAQ）；(4)設定明確的輸入輸出格式；(5)提供充足但不冗餘的上下文資訊。Prompt 需要經過反覆測試和調整，因為 LLM 的回應具有一定的不確定性。

### Q5: Semantic Kernel 框架的核心組件有哪些？
Q: Semantic Kernel 如何整合 AI 應用的各個部分？
A: 核心組件包括：Models（支援多種 LLM 和 AI 模型）、Memories（向量資料庫和記憶管理）、Plugins（定義 AI 可執行的技能）。框架透過統一的介面抽象化這些組件，開發者可以靈活選擇不同的實現方式。Kernel 負責協調各組件之間的互動，處理從自然語言到函數呼叫的完整流程。

### Q6: 如何平衡 AI 的彈性和系統的可靠性？
Q: 在企業應用中如何處理 AI 的不確定性？
A: 關鍵在於識別哪些任務適合用 AI 處理，哪些需要傳統精確計算。需要精確執行的功能（如交易、計算）仍使用傳統方式，而需要理解意圖的功能（如客服、推薦）則善用 LLM。建立完善的錯誤處理和回退機制，同時透過充分的測試和監控來提升系統可靠性。

## 解決方案

### 問題：如何為現有應用程式添加智慧功能
Problem: 現有應用程式缺乏智慧化功能，無法理解使用者意圖，操作體驗不夠直覺
Root Cause: 
- 技術面：缺乏 AI 整合的技術架構和開發經驗
- 流程面：不清楚智慧化的發展路徑和優先順序
- 人為面：團隊對 LLM 應用的理解程度不足

Solution:
- 採用四階段漸進式發展策略，從關鍵環節開始引入 AI
- 使用 Semantic Kernel 等成熟框架，降低 AI 整合的技術門檻
- 建立 Prompt Engineering 和 Function Calling 的開發規範
- 先從風險評估和操作輔助等輔助性功能開始實作
- 逐步發展到完全對話式的使用者介面

Example:
```csharp
// 階段2：關鍵環節的 AI 風險評估
[KernelFunction, Description("評估結帳前的風險和注意事項")]
public static async Task<string> EvaluateCheckoutRisk(
    [Description("購物車內容")] string cartItems,
    [Description("使用者備註")] string userNote)
{
    var prompt = $"我要進行結帳前確認，購物車內容：{cartItems}，備註：{userNote}";
    var result = await kernel.InvokePromptAsync(prompt);
    return result.ToString();
}
```

### 問題：如何設計有效的 LLM 應用架構
Problem: 不知道如何將 LLM、記憶、技能等組件有效整合成完整的智慧應用
Root Cause:
- 技術面：對 LLM 應用架構的核心組件認識不足
- 流程面：缺乏系統化的設計方法和最佳實務
- 人為面：混淆了 LLM 和傳統程式設計的邊界

Solution:
- 建立 LLM + Memory + Skills + Persona 的核心架構
- 使用 RAG 技術實現可擴展的知識管理
- 透過 Function Calling 讓 AI 具備實際執行能力
- 設計清楚的短期記憶（Chat History）和長期記憶（Knowledge Base）
- 定義明確的 AI 角色和行為規範

Example:
```csharp
// 建立完整的 AI 應用架構
var builder = Kernel.CreateBuilder()
    .AddAzureOpenAIChatCompletion(deploymentName, endpoint, apiKey);

// 註冊技能
builder.Plugins.AddFromType<ShopFunctions>();

// 建立記憶
builder.Services.AddSingleton<IMemoryStore, VolatileMemoryStore>();

var kernel = builder.Build();

// 設定角色
var systemPrompt = @"你是安德魯小舖的助理店長，負責協助客人完成購物...";
```

### 問題：如何掌握 Prompt Engineering 的關鍵技巧
Problem: 不知道如何設計有效的 Prompt 來控制 AI 的行為和輸出品質
Root Cause:
- 技術面：缺乏自然語言程式設計的經驗和技巧
- 流程面：沒有建立 Prompt 設計、測試、優化的標準流程
- 人為面：仍以傳統程式設計思維來設計 AI 互動

Solution:
- 建立 System Prompt 設計的標準模板和檢核清單
- 定義明確的角色設定、任務描述和行為規則
- 建立 FAQ 和 SOP 來處理常見情境
- 實作 A/B 測試機制來評估不同 Prompt 的效果
- 建立 Prompt 版本控制和效果追蹤機制

Example:
```csharp
var systemPrompt = @"
你是安德魯小舖的助理店長，負責協助客人完成購物。

主要任務：
1. 結帳前的風險評估
2. 操作過程的輔助提醒
3. 回應客人的問題和需求

工作流程：
- 沒問題回覆 'OK'，有注意事項回覆 'HINT: 具體說明'
- 檢查購買行為是否合理安全
- 提醒相關法律限制和健康建議

FAQ 清單：
1. 購買酒類：提醒年齡限制和酒駕風險
2. 大量購買：確認是否為正常需求
...
";
```

### 問題：如何實現 Function Calling 的技能系統
Problem: 不知道如何讓 LLM 正確理解和呼叫應用程式的 API 函數
Root Cause:
- 技術面：不熟悉 Function Calling 的實作機制和最佳實務
- 流程面：API 設計沒有考慮 AI 的使用方式和理解需求
- 人為面：函數描述不夠清楚，參數定義不夠精確

Solution:
- 使用 Attribute 標記可供 AI 呼叫的函數
- 為每個函數和參數提供詳細的自然語言描述
- 確保函數設計符合單一職責原則，功能明確
- 實作適當的錯誤處理和參數驗證機制
- 建立函數測試和效果評估機制

Example:
```csharp
[KernelFunction, Description("將指定商品和數量加入購物車")]
public static bool AddItemToCart(
    [Description("要加入的商品ID，必須是有效的商品編號")] int productId,
    [Description("要加入的數量，必須是正整數")] int quantity)
{
    // 實作購物車邏輯
    if (productId <= 0 || quantity <= 0) return false;
    
    var product = GetProduct(productId);
    if (product == null) return false;
    
    Cart.AddItem(product, quantity);
    return true;
}
```

## 版本異動紀錄

### v1.1 (2025-08-03)
- 初始版本生成
- 完整分析 LLM 應用程式開發的技術架構和實作方法
- 提供 Semantic Kernel 框架的詳細說明和使用範例
- 包含 Prompt Engineering 和 Function Calling 的實務指南
