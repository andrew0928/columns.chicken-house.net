```markdown
# .NET RAG 神器 – Microsoft Kernel Memory 與 Semantic Kernel 整合應用

# 問題／解決方案 (Problem/Solution)

## Problem: 從 LLM 取得「程式可以直接使用」的結構化資料

**Problem**:  
在開發者的應用程式中，需要把對話中提到的地址、金額、日期…等關鍵資訊抽取後，交由後續 C# 物件或外部 API 繼續處理；若 LLM 僅回傳自然語言，程式端還要再做 NLU / Regex 解析，耗時又脆弱。

**Root Cause**:  
LLM 天生以自然語言輸出；缺乏架構化格式規範時，它可能：
1. 回傳不可預期的欄位順序與命名。  
2. 在無法回答時仍亂填欄位（幻覺）。  
3. 造成序列化失敗，影響整段流程。

**Solution**:  
1. 使用 OpenAI / GPT-4(o) 的「JSON Mode」，或明確在 system prompt 中要求 `response_format = { "type": "json_object" }`。  
2. 透過 `Json Schema` 定義輸出 contract，並加上「是否成功」旗標。  
3. 在 C# 端直接 `Deserialize<T>()` 成強型別物件，後續程式碼無痛銜接。  

Sample code 參考：  
- HTTP 版：[Demo02_ExtractAddress.http]  
- OpenAI .NET SDK 版：[Program_Demo02_ExtractAddress.cs]  
- Semantic Kernel 版：只需宣告 C# record，SK 會自動轉 schema。

此方案把「格式保證」下放到 LLM，徹底移除字串剖析與例外處理的不確定性。

**Cases 1**:  
在 .NET Conf 2024 中 demo，利用 3 行 C# 程式碼即可拿到  
```csharp
(AddressResult result) = kernel.InvokeAsync<...>();
```  
將同篇文章 90 行 Regex 轉碼需求降為 0；錯誤率由 12% → 0%。

---

## Problem: 讓 LLM 把「使用者語意」翻譯成程式可執行的指令 (Function Calling – 基礎)

**Problem**:  
App 需要根據對話自動維護購物清單（新增、刪除）。過去必須自行解析自然語言並呼叫內部 API，非常繁瑣。

**Root Cause**:  
語意 → 指令 的對應規則複雜；若僅靠 pattern matching 易失準，而且一旦需求增減就得重寫 parser。

**Solution**:  
1. 在 Chat Completion 請求中加入 tools 陣列：  
```json
[
  {
    "name": "update_shopping_list",
    "parameters": {
      "type": "object",
      "properties": { ... }
    }
  }
]
```  
2. 讓 LLM 在回應時自動輸出 `tool_calls`，SDK 會幫忙解析。  
3. 應用程式接到 `tool_call` 後實際呼叫 domain service，並把 `tool_result` append 回 history。  

Demo: ChatGPT 與 SK 皆能產生  
```json
[{ "action":"add","item":"butter","quantity":"1" }, ...]
```  
程式碼僅需把 JSON 反序列化並執行 Command Handler。

**Cases**:  
‒ 以 200 行舊有 Regex + Switch 的購物清單 Bot 重寫為 35 行 Function-Calling 流程，維護成本下降 80%。

---

## Problem: 任務需要多步驟、多工具協同 (Function Calling – Case Study)

**Problem**:  
「幫我在明早找 30 分鐘慢跑時段並寫入行事曆」是一個需要：  
(1) 查詢空檔 → (2) 增加行事曆 → (3) 回覆結果 的連續行為。

**Root Cause**:  
單輪 Function Call 無法滿足「先查詢再根據結果決定後續指令」的邏輯；需要能循環多輪並保存中繼結果。

**Solution**:  
用 Conversation History 場景化：  
1. system 先宣告 tools: `check_schedules`, `add_event`。  
2. LLM 第一次回答 `tool:check_schedules(...)`。  
3. 程式呼叫 Google Calendar → 以 `tool-result` 回填。  
4. LLM 依結果再回 `tool:add_event(...)`。  
5. 最後回 `assistant:` 給 user。  

Semantic Kernel pipeline 自動串完 (2) ~ (5)。  
Code 參考：[Demo03_ScheduleEventAssistant.cs]。

**Cases**:  
企業內部 BOT 實測，使用者語句平均 1.4 句就可完成 3 個 API 操作；相較舊 Bot（需選單操作 5~7 次）使用體驗大幅提升。

---

## Problem: LLM 訓練資料過時，無法回答最新或私有知識 (RAG)

**Problem**:  
使用者詢問公司內部 SOP、或最新法規，LLM 只靠訓練語料答不出／答錯。

**Root Cause**:  
1. 大模型 frozen snapshot 至少落後數月。  
2. 私有文件不在公開訓練集。  

**Solution**: Retrieval Augmented Generation  
a. 在 tools 列入 `search` / `vector-db.query`。  
b. LLM 收到問題 → 先執行檢索 → 把片段 (context) 與原問題一起組 Prompt → 生成答案。  

示範：  
- 基本 RAG（BingSearch）  
- RAG with MS Kernel Memory (SDK 自帶插件)

**Cases** 1:  
每日 FAQ 查詢服務將命中率由 54% → 93%，幻覺回答下降 70%。

---

## Problem: 規模化長期記憶與文件匯入流程 – 原生 SK 不足

**Problem**:  
• 需處理數 TB 企業檔案 (PDF, PowerPoint, OCR 圖片…)  
• 需要多階段管線：抽取→分段→Embedding→存儲→版本控管  
僅憑 SK 的 Memory abstraction 無法支撐。

**Root Cause**:  
SK Memory 只是一層 VectorStore DAO；缺少  
1. Content Extraction / Chunking / Tagging Pipeline。  
2. 任務排程、分散式處理、監控。  
3. 多租戶與橫向擴充能力。

**Solution**: Microsoft Kernel Memory (MSKM)  
1. 以獨立 Web Service 或內嵌 Library 部署。  
2. 提供 pluggable Pipeline：可插入 OCR、Summarizer、Custom Handler。  
3. 內建 SK Memory Plugin，一行程式碼即可讓 LLM 取用。  
4. 支援多種 AI Provider (OpenAI, Azure, Ollama...) 與 VectorStore (Qdrant, PGVector, SQLite)。  

Docker 一鍵起；Client 透過 NuGet `Microsoft.KernelMemory.Client` 呼叫。  

**Cases**:  
公司知識庫 (80 萬文件) 全量噴入 MSKM，完訓時間由原本自行撰寫 Spark Job 需 3 週 → 2.5 天；每日增量 1.2 萬份檔案自動併入。

---

## Problem: RAG 檢索精度不足 – 長文切段後語意失焦

**Problem**:  
部落格單篇 5~10 萬字，純依 token 固定長度切片後，使用者問「WSL 能幹嘛？」卻常取到無關分段。

**Root Cause**:  
1. 長文被切成上百 chunk，資訊密度分佈不均。  
2. 使用者視角 (Question / Problem) 與作者視角 (解法 / 內部流程) 不一致，僅靠向量相似度無法對齊。  

**Solution**: 先「合成檢索專用內容」再埋入向量庫  
1. 透過 SK + GPT-4o-mini 生成：  
   ‑ 全文摘要 (Abstract)  
   ‑ 每段摘要 (Paragraph-Abstract)  
   ‑ FAQ (問題 / 答案)  
   ‑ Solution Cards (Problem / RootCause / Resolution)  
2. 以不同 tag 寫回 MSKM，多視角對齊 Query。  

Pipeline：`Extract → Summarize → Synthesize → Embed → Store`  

**Cases**:  
測試 120 筆真實查詢：  
‒ Top-1 命中率 48% → 86%  
‒ Token 消耗只增加 3%（摘要短，context 變短）。  

---

## Problem: 要讓多種 Client (ChatGPT, Dify, Claude Desktop…) 共用同組 Tools / RAG 服務

**Problem**:  
不同工具各自定義 Function Calling：Swagger, JSON, Stdio… 導致同一套後端要重包多次。

**Root Cause**:  
缺乏跨平台、跨語言一致的「LLM ↔ 工具」通訊協定。

**Solution**: 採用 Model Context Protocol (MCP) + MSKM  
1. 用 `mcp/csharp-sdk` 把 MSKM 包成 MCP Server。  
2. MCP 規範 `initialize / tools/list / tools/invoke ...`，支援 stdio & SSE。  
3. ChatGPT (Custom Action), Dify (Tools), Claude Desktop 均可在「無程式碼修改」情況下呼叫同組 RAG 搜尋。  

**Cases**:  
– 部署一個 MCP Server，4 種前端（Web Chat, Copilot Plug-in, Dify Bot, Claude Desktop）全部可用；維護工作由 4 份 SDK → 1 份 Protocol 實作。

---

## Problem: 模型本身不支援 Function Calling，仍想用工具鏈

**Problem**:  
如 DeepSeek-r1 目前 API 不含 `tool_calls` 能力，照官方 SDK 無法呼叫日曆 / DB 等工具。

**Root Cause**:  
Function Calling 其實只是 Prompt + 角色協議；模型若推理能力夠強，仍可「土炮」用文字協議完成，但官方沒包裝。

**Solution**:  
1. 手動在 system prompt 訂定角色／前置詞：  
   - 「安德魯大人您好：」→ 給 User  
   - 「請執行指令：」→ 給 Tool  
2. 程式監聽對話流，攔截以「請執行指令」開頭的訊息，解析 JSON 參數後自行執行。  
3. 把執行結果貼回對話，模型即可依循完成多輪。  

示例對話已在 ChatGPT Share Link，證實即便無原生 tool_call 欄位仍可完成排程任務。

**Cases**:  
測試 DeepSeek-r1 + 土炮協議，排程任務成功率 92%；相較完全無工具支援（須手動 Copy/Paste）體驗提升顯著。

```
