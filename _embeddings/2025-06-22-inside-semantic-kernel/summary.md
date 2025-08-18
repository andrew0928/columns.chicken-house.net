# .NET RAG 神器 ─ Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 摘要提示
- LLM基礎：透過 Chat Completion API 示範 .NET 開發者必備的對話呼叫流程與訊息結構。  
- Json Mode：以 Json Schema 讓 LLM 輸出結構化資料，利於程式後續反序列化與錯誤判斷。  
- Function Calling：說明工具（tool）宣告、呼叫與回傳機制，是 Agent 工作流程的核心。  
- 連續呼叫案例：以「排程晨跑」範例拆解多輪 tool-call 與回應的完整對談。  
- RAG觀念：檢索增強生成將外部知識庫檢索結果納入 Prompt，提高回答新穎度與正確度。  
- Microsoft Kernel Memory：定位為「RAG as a Service」，負責文件抽取、分段、向量化與儲存。  
- Semantic Kernel：提供 Plug-in 與 Memory 介面，與 MSKM 天然互補、開箱即可使用。  
- 進階RAG：利用 LLM 先行產生摘要、FAQ、Problem/Solution 等多視角內容，改善相似度檢索品質。  
- MCP整合：示範將 MSKM 封裝成 MCP Server，讓 Claude Desktop 等支援 MCP 的 Host 可直接調用。  
- 社群回饋：問卷顯示 Function Calling、RAG 與 MSKM 架構最受開發者關注，整體評價近滿分。  

## 全文重點
本文整理作者於直播與系列貼文中，從基礎到進階系統化介紹 .NET 生態中建構 LLM 應用的完整流程。首先以 OpenAI Chat Completion API 為範例，說明訊息角色、模型參數與呼叫模式，奠定後續所有範例基礎。接着介紹 Json Mode，在 Prompt 中宣告 Json Schema 以取得結構化輸出，解決程式與 LLM 溝通的不確定性；再進一步闡述 Function Calling（Tool Use），透過 tools 定義與 assistant/tool 雙向訊息，讓 LLM 能主動決定何時呼叫程式函式以及如何處理回傳結果。

在掌握 Json Mode 與 Function Calling 的實務用法後，文章切入 RAG（Retrieval Augmented Generation）。作者先解析 RAG 的一般流程：問題重寫、檢索、組 Prompt 再生成答案；再示範如何把檢索動作本身做成 tool，讓 LLM 自行觸發，於是 RAG 與 Function Calling 自然整合。為解決資料匯入、分段與長期存取的工程痛點，Microsoft Kernel Memory（MSKM）被引介為「RAG as a Service」。MSKM 以獨立服務或 Serverless 套件針對文件做抽取、chunking、向量化、標籤與寫入，可直接透過 NuGet 套件掛成 Semantic Kernel 的 Memory Plug-in，並支援多家 Embedding/LLM 連接器。

作者進一步分享自身部落格文章的實驗：僅以預設 chunk 設定向量化，對長文或抽象問題效果不佳；因此於匯入前先用 LLM 生成多種檢索導向資訊（全文摘要、段落摘要、FAQ、問題/解決方案等），並加上 tags 再寫入 MSKM，大幅提升檢索準確率。文中亦展示多種整合情境：SK + MSKM 在程式內原生 Function Calling、透過 OpenAPI 或 No-Code 平台、以 MCP Protocol 封裝 MSKM 供 Claude Desktop 直接呼叫，證明同一組工具鏈能對應不同 Host 與開發場景。

最後，作者公布直播問卷統計，Function Calling、RAG 與 MSKM 架構最受歡迎；多數聽眾期待進一步的 MCP、Agent、商務案例與工作坊，整體評分接近滿分。結論指出，RAG 與 Function Calling 並非單一產品，而是 AI APP 的設計模式；唯有充分理解底層原理並善用 SK、MSKM 等工具，才能打造可維運、可擴充、具成本效益的 LLM 應用。

## 段落重點
### 相關資源與連結  
列舉直播影片、投影片、範例程式碼與問卷等外部資源，方便讀者回顧與實作。

### Day 0 Chat Completion API  
詳解 OpenAI Chat Completion 基本呼叫模式、訊息角色、headers 與可選工具定義；示範以 HTTP Client、OpenAI .NET SDK、Semantic Kernel 實作簡易聊天。

### Day 1 Structured Output  
說明 Json Mode 重要性：用 Schema 約束輸出格式、標示成功與否欄位、單一職責分離；比較直接寫 HTTP、SDK 與 SK 的便利差異。

### Day 2 Function Calling (Basic)  
介紹 Function Calling 概念與簡化流程；透過購物清單案例展示 LLM 如何把自然語言轉為 action/parameter JSON，為後端程式執行。

### Day 3 Function Calling (Case Study)  
以排程晨跑為例，拆解多輪 tool-call：check_schedule → add_event → 回報；強調 tool 與 tool-result 訊息在 chat history 中的角色與順序。

### Day 4 RAG with Function Calling  
解釋 RAG 基本流程及如何把「檢索」做成 tool；示範掛 BingSearch Plug-in，讓 LLM 自動決定查詢並引用來源，打造類 Search GPT 效果。

### Day 5 MSKM: RAG as a Service  
介紹 Microsoft Kernel Memory 的定位、部署選項與與 SK 的互補關係；強調其解決長期記憶匯入、分段與向量儲存的工程痛點。

### Day 6 進階 RAG 應用  
分享將長文先行摘要、FAQ 化、Problem/Solution 化等多視角內容後再向量化，可顯著提升相似度檢索品質；展示自定 pipeline 與成本取捨。

### Day 7 MSKM 與其他系統整合  
梳理多種 Function Calling 執行環境：ChatGPT GPTs、No-Code Dify、MCP Server、SK 原生；示範用 MCP/csharp-sdk 封裝 MSKM 供 Claude Desktop 使用並提出實務踩坑。

### Day 8 土炮 Function Calling  
證明即使模型本身不支援 tool-call，只要在 prompt 中定義角色與格式，也能「土炮」出相同流程；提醒正式環境仍建議使用原生支援工具。

### 問券回饋  
統計 93 份回覆，Function Calling、RAG、MSKM 架構最被看重；聽眾期望更多 MCP、Agent 及商業案例，整體評價高。