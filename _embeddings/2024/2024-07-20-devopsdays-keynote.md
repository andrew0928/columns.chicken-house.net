---
source_file: "_posts/2024/2024-07-20-devopsdays-keynote.md"
generated_date: "2025-01-03 17:30:00 +0800"
version: "1.0"
tools: github_copilot
model: claude_sonnet_3_5
---

# 從 API First 到 AI First - 生成內容

## Metadata

### 原始 Metadata

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
    - API First
    - AI First
    - DevOpsDays
    - GPTs
    - LLM
    - Function Calling
    - Tool Use
    - Prompt Engineering
    - Agent
    - Copilot
    - RAG
    - Semantic Kernel
  secondary:
    - OpenAI
    - ChatGPT
    - Azure OpenAI
    - Keynote
    - 安德魯小舖
    - 架構設計
    - 軟體開發
    - 使用者體驗
    - UX
    - AI DX
    - Developer Experience
    - Microservice
    - 意圖理解
    - 降維打擊

### 技術堆疊分析

tech_stack:
  languages:
    - C#
    - JSON
    - Markdown
  frameworks:
    - .NET
    - ASP.NET Core
    - Semantic Kernel
    - Kernel Memory
  tools:
    - Azure OpenAI
    - ChatGPT
    - Visual Studio
    - Git
    - Docker
  platforms:
    - Azure
    - Windows
    - GPTs
  ai_models:
    - GPT-4
    - GPT-4o
    - GPT-4o-mini
    - text-embedding-3-large
  concepts:
    - API First
    - AI First
    - Function Calling
    - Prompt Engineering
    - RAG
    - Agent Pattern
    - Copilot Pattern
    - JSON Mode
    - Workflow Automation
    - Vector Database
    - Text Embedding

### 參考資源

references:
  internal_links:
    - /2024/01/15/archview-llm/
    - /2024/02/10/archview-int-app/
    - /2024/03/15/archview-int-blog/
    - /2023/01/01/api-design-workshop/
  external_links:
    - https://docs.google.com/presentation/d/10o1VN0Q-97eTwYN_N-UP8pzLlxrxSBJbfXCcq0mTEDk/edit?usp=sharing
    - https://hackmd.io/@DevOpsDay/2024/%2F%40DevOpsDay%2FSylpzzOL0
    - https://chatgpt.com/g/g-Bp79bdOOJ-an-de-lu-xiao-pu-v5-2-0
    - https://chatgpt.com/g/g-F3ckJut37-an-de-lu-de-bu-luo-ge
    - https://platform.openai.com/docs/guides/function-calling
    - https://platform.openai.com/docs/guides/json-mode
    - https://docs.anthropic.com/en/docs/build-with-claude/tool-use
    - https://github.com/microsoft/kernel-memory
    - https://github.com/microsoft/semantic-kernel
    - https://medium.com/@remitoffoli/building-llm-powered-products-part-2-32d843bef590
  mentioned_tools:
    - GPTs
    - OpenAI API
    - Azure OpenAI
    - Semantic Kernel
    - Kernel Memory
    - Visual Studio
    - Git
    - ChatGPT
    - Function Calling
    - JSON Mode
    - Swagger/OpenAPI

### 內容特性

content_metrics:
  word_count: 65000
  reading_time: "180 分鐘"
  difficulty_level: "進階"
  content_type: "技術演講紀錄與深度分析"

## 摘要

本文是作者在 DevOpsDays Taipei 2024 擔任 Keynote 演講的完整紀錄與延伸內容，主題為「從 API First 到 AI First」。文章延續了作者 2022-2023 年談論的 API First 理念，進一步探討如何將 AI 技術整合到軟體開發流程中。作者透過四個實際的 DEMO 案例，展示了 LLM 在應用程式開發中的實際應用，包括自然語言購物介面、情緒偵測、Copilot 模式整合，以及 RAG 知識檢索系統。

### 段落摘要

**第 1 章 - 寫在前面**
介紹演講背景與前情提要，包含 2021-2024 年在 DevOpsDays 的系列演講脈絡，以及相關的四篇技術文章。說明當前 AI 討論多集中在模型、算力、工具，但缺乏實際應用開發的討論。

**第 2 章 - 示範案例: 安德魯小舖 GPTs**
透過「安德魯小舖」GPTs 展示四個核心應用場景：
- DEMO #1: 自然語言購物體驗，展示從「下指令」到「提出要求」的 UX 革命
- DEMO #2: AI 偵測購買滿意度與個人化推薦，展示 AI 在使用者體驗改善上的「降維打擊」效果

**第 3 章 - 軟體開發還是你想像的樣貌嗎？**
深入分析 AI 在軟體開發中的角色變化：
- 從 API First 設計品質的重要性談起
- 介紹 Prompt Engineering 的三個層級：基本型、JSON Mode、Function Calling
- DEMO #3: Copilot 設計架構，展示 Controller + LLM 的協作模式
- DEMO #4: RAG 基礎元件與設計模式，展示知識檢索與增強生成的應用

**第 4 章 - 零售業的 AI 應用情境**
引用 Happy Lee 在生成式 AI 年會的分享，說明零售業四種銷售場景的 AI 應用，展示 Agent + Engine 協作模式在實際商業場景中的應用。

**第 5 章 - 寫在最後**
總結 AI 對軟體開發各環節的影響，包括架構設計、開發流程、部署管線的變化，以及大會滿意度回饋與網友參加心得分享。

## 問答對

### Q1: 什麼是從「API First」到「AI First」的轉變？
A1: API First 強調透過高品質的 API 設計來提供商業價值和擴充性。AI First 則是在此基礎上，將 AI (特別是 LLM) 作為應用程式的核心元件，利用 AI 的意圖理解能力來改善使用者體驗。兩者不是取代關係，而是疊加關係 - 好的 API 設計讓 AI 能更有效運用，而 AI 則提供了全新的互動維度。

### Q2: 為什麼作者說 AI 改善 UX 是「降維打擊」？
A2: 傳統改善 UX 的方法是透過大量訪談、流程設計、介面設計來「猜測」使用者意圖。而 AI 可以直接從對話中理解使用者真正的意圖，這是完全不同維度的做法。就像三次元生物看二次元生物一樣，AI 能夠處理傳統 UI/UX 方法無法觸及的語意層面問題，因此是「降維打擊」。

### Q3: Function Calling 的工作原理是什麼？
A3: Function Calling 是讓 AI 能夠自主判斷並呼叫 API 的機制。開發者提供 API 規格給 LLM，LLM 從使用者對話中解析意圖，判斷需要呼叫哪些 API，並自動產生符合規格的請求參數。整個過程包含：意圖解析 → API 選擇 → 參數生成 → API 呼叫 → 結果整合回應。

### Q4: Copilot 模式與 Agent 模式有什麼差別？
A4: Copilot 模式是以傳統 Controller 為主，AI 為輔的架構設計。使用者主要透過傳統 UI 操作，AI 在旁邊提供輔助和建議。Agent 模式則是以 AI 為主導，能完全自主執行複雜任務。目前因為 LLM 推理能力還不夠成熟，Copilot 模式更適合現階段使用，未來隨著 AI 發展可能逐步轉向 Agent 模式。

### Q5: RAG 在 AI 應用開發中扮演什麼角色？
A5: RAG (Retrieval-Augmented Generation) 是檢索增強生成技術，讓 AI 能夠利用外部知識庫回答問題。工作流程是：使用者提問 → AI 判斷關鍵問題 → 透過 API 檢索相關資料 → 將檢索結果與問題合併成 prompt → LLM 彙整回答。這解決了 LLM 知識截止日期的限制，也讓 AI 能夠回答特定領域的專業問題。

### Q6: 在 AI 時代，API 設計需要注意什麼新的考量？
A6: 傳統 API 設計考慮的是 DX (Developer Experience)，現在還需要考慮 AI DX。具體包括：
1. **合情合理**：API 邏輯要符合常理，因為 LLM 是用常理訓練出來的
2. **足夠可靠**：要能承受 AI 的胡亂呼叫，守住安全邊界
3. **完整描述**：OpenAPI 文件要詳細，讓 AI 能正確理解 API 用途和參數
4. **狀態機設計**：確保 API 操作的原子性和一致性

### Q7: Prompt Engineering 有哪些核心技巧？
A7: 主要有三個層級：
1. **基本型**：設計 prompt template，將使用者輸入的參數套入後送給 LLM
2. **JSON Mode**：讓 LLM 回應結構化的 JSON 格式，便於程式處理
3. **Function Calling**：讓 LLM 自主判斷要執行的動作，並呼叫對應的 API
每個層級都需要透過實際測試來調整 prompt 效果，確保 AI 能正確理解指令並執行任務。

### Q8: AI 應用程式的部署架構需要考慮哪些新因素？
A8: 除了傳統的 Application、Configuration、Environment 三大部署面向，還需要增加第四個面向：AI。包括：
1. **資料管理**：訓練資料的收集、更新、版本控制
2. **模型部署**：訓練好的模型部署上線、版本管理
3. **算力調度**：GPU/NPU 資源的分配和調度
4. **成本控制**：Token 使用量、API 呼叫費用的監控
這些都需要專屬的 CI/CD Pipeline 來管理，才能建立成熟的 AI 應用程式執行環境。

## 解決方案

### 問題：如何設計適合 AI 使用的 API？

**情境**：現有的 API 主要為前端 UI 設計，需要重新設計讓 AI 能有效使用

**解決方案**：
1. **遵循 Domain 導向設計**：
   - 按照業務領域設計 API，而非配合特定 UI 需求
   - 使用狀態機來定義核心業務流程
   - 確保每個 API 都對應一個原子操作

2. **強化 API 文件品質**：
   ```yaml
   paths:
     /products/{id}/add-to-cart:
       post:
         summary: "Add product to user's shopping cart"
         description: "Adds a specified quantity of product to the user's cart. 
                      Validates product availability and user permissions."
         parameters:
           - name: id
             description: "Product ID to add to cart"
   ```

3. **實施嚴格的安全控制**：
   - 使用 SCOPE 和 APIKEY 控制存取權限
   - 確保 API 能承受異常呼叫而不損壞資料
   - 實施 rate limiting 和 input validation

**相關工具/指令**：
- OpenAPI 3.0 規範文件
- Swagger UI 進行 API 測試
- 狀態機設計工具

**注意事項**：
- API 設計要符合常理，讓 AI 容易理解
- 避免過度為 UI 客製化而犧牲通用性
- 定期檢查 API 的 AI 可用性

### 問題：如何在現有應用程式中整合 Copilot 功能？

**情境**：想要在傳統的操作介面中加入 AI 輔助功能，但不想完全改變現有操作方式

**解決方案**：
1. **雙軌並行的架構設計**：
   ```csharp
   public class ApplicationController 
   {
       private readonly ICopilot _copilot;
       
       public async Task<ActionResult> ProcessUserAction(UserAction action)
       {
           // 正常業務邏輯處理
           var result = await ProcessBusinessLogic(action);
           
           // 同時通知 Copilot 記錄操作歷程
           await _copilot.LogUserInteraction(action, result);
           
           return result;
       }
   }
   ```

2. **設定觸發條件**：
   - 定義什麼情況下 Copilot 應該主動介入
   - 提供使用者直接向 Copilot 求助的管道
   - 設計適當的 instruction 指導 AI 行為

3. **保持操作習慣**：
   - 不強制使用者改變既有操作流程
   - Copilot 只在需要時提供建議或協助
   - 確保傳統操作方式仍然可用

**相關工具/指令**：
- Semantic Kernel for .NET
- Azure OpenAI API
- 自定義的 instruction 設計

**注意事項**：
- Copilot 的建議要準確，避免造成困擾
- 要有明確的開關機制讓使用者控制
- 注意 AI 呼叫的成本控制

### 問題：如何實作 Function Calling 機制？

**情境**：需要讓 AI 能夠自主判斷並呼叫適當的 API 來完成使用者任務

**解決方案**：
1. **定義 Function Schema**：
   ```json
   {
     "name": "add_to_cart",
     "description": "Add a product to user's shopping cart",
     "parameters": {
       "type": "object",
       "properties": {
         "product_id": {
           "type": "string",
           "description": "The ID of the product to add"
         },
         "quantity": {
           "type": "integer", 
           "description": "Number of items to add"
         }
       },
       "required": ["product_id", "quantity"]
     }
   }
   ```

2. **設計執行流程**：
   ```csharp
   var response = await openAIClient.GetChatCompletionsAsync(
       new ChatCompletionsOptions()
       {
           Messages = { userMessage },
           Functions = { addToCartFunction },
           FunctionCall = FunctionCall.Auto
       });
   
   if (response.Value.Choices[0].Message.FunctionCall != null)
   {
       var functionCall = response.Value.Choices[0].Message.FunctionCall;
       var result = await ExecuteFunction(functionCall.Name, functionCall.Arguments);
   }
   ```

3. **處理執行結果**：
   - 解析 AI 產生的 function call
   - 執行對應的業務邏輯
   - 將執行結果回饋給 AI 繼續對話

**相關工具/指令**：
- OpenAI Function Calling API
- JSON Schema 驗證工具
- 錯誤處理和重試機制

**注意事項**：
- Function description 要寫得夠清楚
- 要處理 AI 產生錯誤參數的情況
- 實施適當的權限檢查和安全控制

### 問題：如何建立 RAG 檢索系統？

**情境**：需要讓 AI 能夠檢索特定領域的知識庫來回答問題

**解決方案**：
1. **建立向量資料庫**：
   ```csharp
   var memory = new KernelMemoryBuilder()
       .WithAzureOpenAITextEmbeddingGeneration(embeddingConfig)
       .WithAzureOpenAITextGeneration(completionConfig)
       .WithSimpleVectorDb(vectorDbPath)
       .Build<MemoryServerless>();
   
   await memory.ImportTextAsync(documentContent, documentId, tags);
   ```

2. **實作檢索邏輯**：
   ```csharp
   public async Task<string> SearchKnowledge(string query)
   {
       var searchResults = await memory.SearchAsync(
           query: query,
           limit: 5,
           minRelevance: 0.3);
       
       return string.Join("\n", searchResults.Results.Select(r => r.Partitions[0].Text));
   }
   ```

3. **整合到對話流程**：
   - 從使用者問題中識別檢索關鍵字
   - 執行向量相似度搜尋
   - 將檢索結果與原問題合併送給 LLM

**相關工具/指令**：
- Microsoft Kernel Memory
- Azure OpenAI Embedding Models
- Vector Database (如 Qdrant, PostgreSQL + pgvector)

**注意事項**：
- 適當的文件分段策略很重要
- 需要調整相似度閾值以平衡準確性和涵蓋性
- 考慮檢索結果的排序和重要性權重

### 問題：如何控制 AI 應用的成本？

**情境**：AI 應用上線後需要控制 Token 使用量和 API 呼叫費用

**解決方案**：
1. **實施使用量監控**：
   ```csharp
   public class TokenUsageTracker
   {
       public async Task<ChatResponse> CallLLM(string prompt, string userId)
       {
           var response = await openAIClient.GetChatCompletions(prompt);
           
           await LogUsage(userId, response.Usage.PromptTokens, response.Usage.CompletionTokens);
           
           return response;
       }
   }
   ```

2. **設定使用限制**：
   - 為不同使用者類型設定不同的額度
   - 實施 rate limiting 防止濫用
   - 快取常見問題的回答減少重複呼叫

3. **優化 Prompt 設計**：
   - 精簡 prompt 內容減少 input token
   - 使用更便宜的模型處理簡單任務
   - 考慮本地模型降低雲端 API 成本

**相關工具/指令**：
- Azure Monitor 進行用量追蹤
- Redis 實作 rate limiting
- 成本分析儀表板

**注意事項**：
- 要平衡成本控制和使用者體驗
- 建立預警機制避免突發超額費用
- 定期檢討和調整成本策略
