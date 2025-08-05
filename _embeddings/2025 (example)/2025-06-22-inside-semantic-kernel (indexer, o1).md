---
- source_file: /docs/_posts/2025/2025-06-22-inside-semantic-kernel.md
- generated_date: 8/5/2025 12:00:00 AM
- version: 1.0
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, via endpoint - https://app-azureopenai.openai.azure.com/
---
# .NET RAG 神器 ─ Microsoft Kernel Memory 與 Semantic Kernel 整合應用 ‑ 生成內容  

## Metadata  

### 原始 Metadata  
layout: post  
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"  
categories:  
- 系列文章: 架構師觀點  
tags: ["架構師觀點", "技術隨筆"]  
published: true  
comments_disqus: false  
comments_facebook: false  
comments_gitalk: true  
redirect_from:  
logo: /wp-content/images/2025-06-22-inside-semantic-kernel/livecast-logo.png  

### 自動識別關鍵字  
keywords:  
  primary:  
    - RAG (Retrieval Augmented Generation)  
    - Microsoft Kernel Memory (MSKM)  
    - Semantic Kernel (SK)  
    - Function Calling  
    - Json Schema / Structured Output  
    - Model Context Protocol (MCP)  
  secondary:  
    - .NET  
    - OpenAI ChatCompletion API  
    - Embedding  
    - Vector Store  
    - Agent / Plugins  
    - Bing Search API  
    - Claude Desktop  
    - n8n, Dify  

### 技術堆疊分析  
tech_stack:  
  languages:  
    - C# (.NET 8)  
  frameworks:  
    - Microsoft Semantic Kernel  
    - ASP.NET Core  
  tools:  
    - Microsoft Kernel Memory (Docker image & NuGet)  
    - OpenAI .NET SDK  
    - MCP C# SDK  
    - GitHub  
  platforms:  
    - Azure OpenAI / OpenAI  
    - Windows / Linux (Docker)  
  concepts:  
    - Retrieval-Augmented Generation  
    - Function Calling / Tool Use  
    - Vector DB & Embeddings  
    - Long-term Memory Pipeline  
    - Agentic Workflow  

### 參考資源  
references:  
  internal_links:  
    - Day 0–8 範例程式碼 (GitHub repository)  
  external_links:  
    - https://github.com/microsoft/semantic-kernel  
    - https://github.com/microsoft/kernel-memory  
    - https://platform.openai.com/docs/api-reference/chat  
    - https://modelcontext.org (MCP spec)  
    - https://github.com/andrew0928/AndrewDemo.DevAIAPPs  
  mentioned_tools:  
    - OpenAI / Azure OpenAI  
    - Bing Search  
    - SQLite  
    - Docker Hub  

### 內容特性  
content_metrics:  
  word_count: 22 000 +  
  reading_time: 約 75 分鐘  
  difficulty_level: 進階  
  content_type: 實作教學 + 直播筆記  

---

## 摘要  

### 文章摘要  
作者以八天的直播內容為主軸，完整示範從「Chat Completion API 基礎」到「以 Microsoft Kernel Memory 打造 RAG 服務」的完整實務流程。文章先闡述 Json Schema 與 Function Calling 兩大基礎技巧，再進一步說明如何利用 SK Plugins 與自訂 Pipeline 在 MSKM 中建立長期向量記憶。最後討論 MCP、No-Code 平台與土炮策略，展示多種整合管道，以及作者在部落格文章切片、摘要、FAQ 與解決方案重組上的經驗。全篇強調「架構思維 + DevOps 心法」，說明架構師應如何快速驗證並落地 AI 應用。  

### 關鍵要點  
- Json Schema 與 Function Calling 是 AI 應用開發的兩大基礎能力。  
- RAG 流程＝收斂問題 → 檢索相關內容 → Prompt Augmentation → 回答生成。  
- Microsoft Kernel Memory 將長期記憶抽象成獨立服務，可線上 (Web API) 或內嵌 (Serverless) 使用。  
- SK + MSKM 的組合可讓 LLM 直接以 Plugins 方式呼叫向量檢索。  
- 在匯入文件前先用 LLM 生成摘要、FAQ、Problem/Solution 等多視角訊息，可顯著提升檢索精度。  
- MCP 將 Function Calling 標準化，讓各種 Host (Claude Desktop、Cursor…​) 都能以 USB-C 模式接 AI 工具。  
- 架構師需由概念、模型、驗證到監控一次思考，才能真正做到 Dev + Ops。  

---

## 段落層級摘要  

1. Day 0 – Chat Completion API  
   說明單一 API 即可滿足大多數 LLM 對話需求，示範 HTTP、OpenAI SDK 與 SK 三種寫法，並拆解 request / response 結構。  
2. Day 1 – Structured Output (Json Mode)  
   強調開發者應要求 LLM 直接輸出符合 Json Schema 的結果，以便程式碼後續處理；談成功 / 失敗訊號與單一職責原則。  
3. Day 2 – Function Calling (Basic)  
   介紹 Tools 定義與 LLM 自主選擇呼叫時機的原理；用購物清單範例示範 action list 產生。  
4. Day 3 – Function Calling (Case Study)  
   解析多輪對話中 tool / tool-result 與 assistant / user 三方訊息互動，並以排程行事曆為例展示完整回合。  
5. Day 4 – RAG with Function Calling  
   把「檢索」視為一種 tool，使 LLM 能主動決定何時查詢並引用來源；示範 Bing Search + SK Plugins。  
6. Day 5 – MSKM: RAG as a Service  
   介紹 MSKM 架構、Pipeline 與與 SK 的互補關係；說明 Docker 與 NuGet 兩種部署模式。  
7. Day 6 – 進階 RAG：生成檢索專用資訊  
   分享作者為 300+ 篇長文自動產出摘要、段落摘要、FAQ、Problem/Solution 等多種 Chunk，提高向量檢索精度的經驗。  
8. Day 7 – MSKM 與外部系統整合  
   展示 MCP Server 封裝 MSKM，供 Claude Desktop 直接調用；說明 OpenAPI、No-Code 工具與 MCP 的異同。  
9. Day 8 – 土炮 Function Calling  
   演示在不支援原生 Function Calling 的模型 (如 DeepSeek) 上，用「前置詞協議」仍可手動實作同樣流程。  
10. 問卷統計與反饋  
    彙整 90 + 名觀眾的回饋，顯示 Function Calling/RAG 為最受用主題，也收錄對未來課程的建議。  

---

## 問答集  

(Q1) 什麼是 Microsoft Kernel Memory？  
A: MSKM 是一套開源「Long-term Memory Platform」，負責文件擷取、切片、向量化與儲存，可透過 HTTP API 或嵌入式方式被 Semantic Kernel、No-Code 平台或 MCP Host 調用，用來實作 RAG 或 Agent 長期記憶。  

(Q2) Json Schema 對 LLM 開發有何幫助？  
A: 透過 Json Schema，開發者可要求 LLM 生成嚴格結構化輸出，後端即可直接反序列化成物件，避免模糊解析與幻覺，並可嵌入 success/fail 欄位作為顯式錯誤訊號。  

(Q3) RAG 流程中的「Chunk Size」要怎麼決定？  
A: 需參考 Embedding 模型最佳輸入長度 (如 text-embedding-large3 建議 512 tokens)。太長會稀釋語意，太短則造成脈絡不足；一般可 256–1024 tokens 再依實測調整。  

(Q4) 為何要先用 LLM 生成摘要或 FAQ 再存入向量庫？  
A: 使用者的查詢視角未必與原文一致，直接檢索可能找不到相關 Chunk。先生成摘要 / FAQ / Problem Statement 等多視角資料，可提高相似度匹配機率，減少牛頭不對馬嘴的結果。  

(Q5) MCP 與傳統 Function Calling 有何差別？  
A: MCP 將 tools/list、tools/invoke… 等動作定義為 JSON-RPC 協定並支援 stdio 與 SSE，使 LLM Host 與工具之間像 USB-C 一樣可熱插拔，與 OpenAI 格式化訊息相比更語言與模型中立。  

(Q6) 如果使用的模型不支援原生 Function Calling，如何替代？  
A: 可在 system prompt 定義「角色前綴」或關鍵字規則，要求 LLM 以特定格式輸出欲呼叫的函數與參數；由應用程式解析並執行後再把結果回寫對話，即可土炮實現同樣效果。  

(Q7) MSKM 與純粹 Vector DB 的差異是什麼？  
A: Vector DB 只提供向量儲存與相似度查詢；MSKM 則包含文件擷取、分段、標籤、向量化 Pipeline、索引版本管理與與 SK Plugins 整合的完整解決方案，更貼近「RAG 平台」。  

(Q8) 為什麼作者強調 DevOps 思維在 AI 應用中的重要性？  
A: 架構師須在最短時間驗證解決方案可行性；若半年後才發現設計失誤，代價過高。透過模型、模擬、監控指標 (Push/Send/Drop/Latency…​) 等手段，可在 POC 階段就獲得運維層面的真實回饋。  

---

## 解決方案整理  

### 問題：如何在 .NET 專案中快速導入高精度 RAG  
情境：現有知識庫為 Markdown 長文，需讓客服 Bot 可即時回答。  
解決方案：  
1. 使用 MSKM Docker Image 部署向量服務。  
2. 以 SK ImportText API，並自訂 Pipeline：TextExtraction → Summarization → Chunking → Embedding → Store。  
3. 在匯入前先用 LLM 生成摘要、FAQ、Problem/Solution 四種視角。  
4. 前端以 SK ChatKernel + MSKM Memory Plugin 實作檢索 → Augment Prompt → Answer。  

相關指令：  
```bash
docker run -d -p 9001:9001 mskm/kernel-memory:0.96.3
km.cli import-text --file wsl.md --pipeline advanced.json
```  
注意事項：調整 chunk_size 與 overlap，以防中文 token 切割異常。  

---  

### 問題：在不支援原生 Function Calling 的模型上仍要執行外部工具  
情境：團隊購買 DeepSeek r1，無 tool use 支援。  
解決方案：  
- System Prompt 宣告兩個「前綴詞」：  
  • 「[CMD]」＝工具呼叫； • 「[USR]」＝回覆給使用者  
- 應用程式監聽訊息，遇到 [CMD] 解析 JSON 參數並執行相應 REST API，再用 [RES] 格式回寫結果。  
- 迴圈至任務完成。  

範例 Prompt 片段：  
```
你可以用兩種方式輸出：
[CMD] { "tool": "search", "query": "...", "limit": 3 }
[USR] 請貼給使用者看的最終答案
```  

---

### 問題：提升多模組 Agent 的可插拔性  
情境：需讓 Claude Desktop、Cursor 等多種 Host 共用公司內部工具。  
解決方案：  
1. 以 MCP C# SDK 將內部 REST API 封裝為 MCPServer。  
2. 實作 tools/list 與 tools/invoke，轉接至現有微服務。  
3. 在 Host 端匯入 .well-known/ai-plugin.json 或直接連線 `http://tools.company/mcp`.  
4. 透過 stdio 或 SSE 持續服務其他 LLM。  

注意事項：MCP JSON-RPC 若含中文字需使用 `\uXXXX` 編碼，等待官方修正。  

---

## 版本異動紀錄  

- v 1.0 (2025-07-24) – 首版摘要、Q&A、解決方案整理並加入自動化關鍵字/技術堆疊。  

