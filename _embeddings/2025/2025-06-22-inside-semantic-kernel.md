---
- source_file: /docs/_posts/2025/2025-06-22-inside-semantic-kernel.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# .NET RAG 神器 ── Microsoft Kernel Memory 與 Semantic Kernel 整合應用 摘要

## Metadata

```yaml
# 原始 Front Matter:
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

# 自動識別關鍵字:
primary-keywords:
  - Microsoft Kernel Memory (MSKM)
  - Semantic Kernel (SK)
  - RAG (Retrieval-Augmented Generation)
  - Function Calling / Tool Use
  - .NET AI Application Patterns
  - Structured Output / JSON Mode
secondary-keywords:
  - OpenAI Chat Completion API
  - OpenAI .NET SDK
  - Model Context Protocol (MCP)
  - Vector Database / Chunking
  - Summarization Pipeline
  - Kernel Memory Plugins
  - Bing Search Plugins
  - Claude Desktop
  - n8n / Dify

# 技術堆疊分析:
tech_stack:
  languages:
    - C#
  frameworks:
    - Microsoft Semantic Kernel
    - Microsoft Kernel Memory
    - OpenAI .NET SDK
    - MCP C# SDK
  tools:
    - OpenAI / Azure OpenAI Service
    - Bing Search API
    - Docker
    - GitHub Actions
    - n8n / Dify (No-Code Platforms)
  platforms:
    - Azure
    - ChatGPT GPTs
    - Claude Desktop
  concepts:
    - RAG Pipeline (Vectorization, Chunking, Retrieval)
    - Function Calling / Agent Pattern
    - Structured Output & JSON Schema
    - Long-Term Memory Management
    - AI Design Patterns

# 參考資源:
references:
  internal_links:
    - /2024/07/20/devopsdays-keynote/
    - /2024/03/15/archview-int-blog/
  external_links:
    - https://github.com/andrew0928/AndrewDemo.DevAIAPPs
    - https://www.youtube.com/watch?v=q9J1YzhW6yc
    - https://docs.google.com/presentation/d/e/2PACX-1vQcfNQlTZlThjYD08LFnGhFfLd904W1ceX76A9Z8MQUSHmYSbRdSPykFX0eOzIipL-2v536guFhE7ro/pub
    - https://platform.openai.com/docs/guides/function-calling
    - https://github.com/microsoft/kernel-memory
    - https://github.com/microsoft/semantic-kernel
  mentioned_tools:
    - ChatGPT
    - GPT-4o / GPT-4o-mini
    - DeepSeek R1
    - Ollama
    - SQLite

# 內容特性:
content_metrics:
  word_count: 18000
  reading_time: "55 分鐘"
  difficulty_level: "進階"
  content_type: "Livecast Recap + Tutorial"
```

## 文章摘要

作者以一場為期八天的直播與貼文為基礎，系統性地剖析如何在 .NET 生態系中使用 Microsoft Semantic Kernel（SK）與 Microsoft Kernel Memory（MSKM）打造 RAG 應用。內容由淺入深，先以 OpenAI ChatCompletion API 示範基本 Chat、JSON Mode 與 Function Calling，再逐步引入 RAG 流程、MSKM 作為「RAG-as-a-Service」的角色，最後展示 MCP、No-Code 平台與土炮 Prompt 技巧的多元整合。作者強調三大核心能力：  
1) 以 JSON Schema 強制輸出結構化資料，讓傳統程式碼能無縫銜接 LLM；  
2) 透過 Function Calling 讓 LLM 自主選擇並調用工具，進而實現 Agent 化工作流程；  
3) 以 MSKM 管理長期記憶、支援高效向量檢索，並可掛載為 SK Plugin 或獨立 Web Service。  
文章同時分享在大型部落格資料集上優化 RAG 的實戰心得：先用 LLM 生成摘要、FAQ、Problem/Solution 等多視角索引，再行向量化以改善召回品質。最後作者公布問卷統計與讀者回饋，證實 Function Calling、RAG Pipeline 與 MCP 整合是最受社群關注的主題。本篇適合欲在企業或個人專案導入 .NET AI 技術、提升 RAG 準確度與開發效率的開發者、架構師與技術領導者。

## 關鍵要點

- ChatCompletion API 是萬用入口，LLM 真正的複雜度在「設計案例」而非 API 本身。  
- JSON Mode + JSON Schema 能顯著降低程式與 LLM 的解析成本。  
- Function Calling 讓 LLM 擔任「意圖 → 指令」編譯器，是 Agent 崇高能力的基石。  
- RAG ≠ 系統，而是一組設計模式；優秀的 RAG 需客製化切片策略與檢索專用索引。  
- MSKM 提供 RAG 全流程（抽取、分段、向量化、儲存、查詢）且可橫向擴充。  
- SK 與 MSKM 共享團隊，Memory Plugin 無縫銜接，支援多家 LLM／Embedding 服務。  
- MCP 將 Function Calling 抽象為「AI 的 USB-C」，打通各類 Host 與工具。  
- 土炮 Prompt 亦能模擬 Function Calling，關鍵在角色切分與訊息協議。  
- 向量檢索品質取決於「資訊密度對齊」；摘要、FAQ、Problem/Solution 可大幅增準確率。  
- 問卷顯示：Function Calling 基礎、RAG 進階與框架整合是開發者最急需的能力提升點。

---

## 段落摘要 (每個段落一個 H3 標題)

### Day 0 – Chat Completion API 基礎
作者以「Simple Chat」為例，從純 HTTP Request 起手，逐步轉到 OpenAI .NET SDK 與 Semantic Kernel。說明 ChatCompletion API 的五大區塊（headers、model 參數、messages、tools、response format），強調理解訊息歷史與上下文對話機制是後續一切進階應用的根基。

### Day 1 – Structured Output
聚焦 JSON Mode 與 JSON Schema。作者指出開發者應要求 LLM 直接輸出符合 Schema 的 JSON，並額外標示成功/失敗欄位，以便程式快速反序列化與錯誤處理。示範 C# Type ↔︎ Schema 自動轉換，闡述「單一職責」原則：讓 LLM 處理語意推理，其他計算與 API 呼叫交回傳統程式碼。

### Day 2 – Function Calling (Basic)
介紹 Function Calling 基本概念：先宣告可用指令，再讓 LLM 依意圖產生 action + 參數。以購物清單案例展示 LLM 如何生成 add/delete 指令列表，說明其本質是把自然語言「編譯」成程式可執行的指令序列，是 Agent 化的第一步。

### Day 3 – Function Calling (Case Study)
進階範例「排程晨跑」。詳列七步訊息流程（system, user, assistant/tool, tool-result），展示 LLM 如何多輪呼叫 check_schedule 與 add_event，最終回覆人類可讀結果。強調成熟框架（SK、n8n、dify）可大幅簡化開發，但理解原理仍屬必要。

### Day 4 – RAG with Function Calling
從 Function Calling 過渡到 RAG。說明三步驟：問題收斂、檢索、生成。示範把 BingSearch 以 Plugin 方式掛給 SK，使 LLM 能自動決定何時發起搜尋並組合結果回答。指出 RAG 讓 LLM 彷彿「會用 Google」，因此可輕鬆打造 Search GPT 或私有知識庫問答。

### Day 5 – MSKM: RAG as a Service
首次聚焦 Microsoft Kernel Memory。解析其兩種部署模式（Web Service / Serverless Embed），以及與 SK 的兩層關係：a) Memory Plugin 互操作；b) 共用 Connector。MSKM 旨在解決長期記憶與大規模文件導入，內建可擴充的 Pipeline 與 Vector Store 抽象，是目前 .NET 生態最成熟的 RAG 後端。

### Day 6 – 進階 RAG：生成檢索專用資訊
在大型部落格資料集上測試 MSKM 預設 Chunking 後發現召回不足，於是先用 LLM 生成「全文摘要」「段落摘要」「FAQ」「Problem/Solution」等多視角內容，再向量化存入 MSKM。結果大幅提升語意對齊與檢索精度，示範 RAG 必須根據資料特性調整 Pipeline。

### Day 7 – MSKM 與其他系統整合
比較四種 Function Calling 管道：ChatGPT GPTs、No-Code Platform、MCP Host（Claude Desktop）、SK Native。介紹 MCP 協定（stdio 與 SSE 通道）與官方 C# SDK，並展示將 MSKM 封裝成 MCPServer 供 Claude Desktop 調用的完整流程與除錯注意事項。

### Day 8 – 土炮 Function Calling
回應直播提問，示範在「不支援 Function Calling」的模型中以純 Prompt 模擬三方對話：使用前置詞區分人類與工具訊息，再由應用程式攔截「請執行指令」段落即可完成手動工具呼叫。藉此強調理解協議重於依賴特定模型。

### 問卷統計與社群回饋
彙整 93 份問卷：最受歡迎主題為 Function Calling、RAG 進階與框架整合；多數開發者透過 SDK 或 No-Code 平台存取 LLM；時間安排與層次分明獲高評價。建議集中在更多 MCP、Agent、實務案例與工作坊形式。

---

## 問答集

### 概念解釋

Q1: 什麼是 Microsoft Kernel Memory？  
A1: MSKM 是微軟開源的長期記憶服務，提供文件抽取、分段、向量化、儲存與檢索等完整 RAG Pipeline。它可以獨立部署為 Web Service，也可嵌入 .NET 應用，並內建 Semantic Kernel Memory Plugin 以支援 Function Calling。

Q2: RAG 與傳統全文搜尋最大的差別是？  
A2: RAG 先將內容向量化，再以嵌入向量衡量語意相似度，能跨同義詞與語意變體找到關聯段落；此外 RAG 會將檢索結果回填到 Prompt，讓 LLM 基於即時資料生成答案，而不僅是關鍵字配對。

### 操作指導

Q3: 在 SK 中如何把 MSKM 掛成 Plugin？  
A3: 引用 `Microsoft.KernelMemory.SemanticKernel` 套件後，一行程式呼叫 `builder.AddKernelMemory(memoryClient)` 即可；SK 會自動將 MSKM 暴露的 `search`, `upload`, `delete` 等函數註冊為可供 LLM 呼叫的 Tools。

Q4: 若想修改 MSKM 的 Chunking 規則怎麼做？  
A4: 自訂 Pipeline YAML，移除預設 `chunking` handler，換成自寫 Handler 或調整 `max_tokens`、`overlap` 參數；再於 `km import` 時指定 `--pipeline myPipeline.yaml`。

### 問題排除

Q5: 部署官方 Docker 映像後中文產生「晶晶體」怎麼辦？  
A5: 先降版至 0.96.x 或自行 build master 分支後 patch 中文分段邏輯；也可在 Vectorization 前以自訂 Handler 先做斷詞與 UTF-8 標準化。

Q6: MCP C# SDK 回傳含中文 JSON Claude 解析失敗？  
A6: 目前需手動設定 `JsonSerializerOptions.Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping` 或等待官方修正；臨時做法是將中文轉 Unicode `\uXXXX`。

### 比較分析

Q7: SK Plugins 與 GPTs Custom Action 哪裡不同？  
A7: 前者在應用程式內執行，LLM 透過內部 Function Calling 操作；後者在 ChatGPT Host 側，由 OpenAI Server 轉發 HTTP 請求。前者延遲低、可離線；後者部署快、易分享。

Q8: MSKM vs. 自己直連向量資料庫？  
A8: MSKM 多了文件處理 Pipeline、增量索引與多模型 Connector，適合大量文件與多人協作；直連向量庫較輕量，但需自行管理抽取與同步機制。

### 進階思考

Q9: 為何作者強調「資訊密度對齊」？  
A9: 如果檢索片段與提問語意層次差距過大，向量相似度不易命中。先生成摘要或 FAQ 可把長文壓縮為高密度知識片段，提高召回精度並降低 Prompt Token 成本。

Q10: 在不支援 Function Calling 的模型上實作工具調度可行嗎？  
A10: 可行。以 Prompt 協議指定角色與指令前綴，再由應用程式解析並執行對應工具，即可手動完成 Function Calling 流程，只是開發維護成本較高。

---

## 解決方案

### 問題 1：純分段 RAG 準確度低  
Root Cause: 長文被機械式切片，相似度搜尋難以對齊提問語意。  
Solution: 導入 LLM-Based 預處理，為每篇文章生成摘要、FAQ、Problem/Solution 等多視角索引，再向量化存入 MSKM。  
Example:
```csharp
var summary = await kernel.InvokePromptAsync<string>(summarizePrompt, docText);
await memory.ImportTextAsync(summary, docId, tags: ["abstract"]);
```

### 問題 2：跨平台 Function Calling 協議不一致  
Root Cause: 各家 Host 採用不同機制，導致工具重複包裝。  
Solution: 採用 Model Context Protocol (MCP) 封裝工具；MSKM 可被包成 MCPServer，ChatGPT GPTs、Claude Desktop 等 Host 皆可共用。  
Example:  
```json
{"method":"tools/call",
 "params":{"name":"search","arguments":{"query":"RAG chunking","limit":5}},
 "jsonrpc":"2.0","id":10}
```

### 問題 3：長期記憶管理難與應用程式解耦  
Root Cause: 將 Vector Store 及 Pipeline 硬寫進業務碼，日後難以橫向擴充。  
Solution: 以 MSKM 作為獨立 Memory Service；應用程式透過 SDK 或 REST 調用，並在 Semantic Kernel 端以 Memory Plugin 存取，實現關注點分離。  
Example (SK):
```csharp
builder.AddKernelMemory("https://km-api:9001", apiKey);
var answer = await kernel.InvokePromptAsync<string>("{{search question}}", vars);
```

---

## 版本異動紀錄
- 1.0.0 (2025-08-05)  初版生成：含 Metadata 擴增、文章摘要、段落摘要、10 組 Q&A 與 3 套解決方案。