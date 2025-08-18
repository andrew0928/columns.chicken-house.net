# .NET RAG 神器 – Microsoft Kernel Memory 與 Semantic Kernel 整合應用

# 問題／解決方案 (Problem/Solution)

## Problem: 將 LLM 結果接回既有程式時，回傳內容太隨意，程式難以判斷  

**Problem**:  
• 在企業／產品內部把 LLM 當成一個 Service 使用時，LLM 常以自然語言回覆，格式不固定。  
• JSON 片段、表格、甚至中英文混雜都可能出現，程式端很難用嚴謹邏輯去解析與驗證。  
• 一旦 LLM 出現幻覺或輸出格錯，應用就無法保證可靠度。  

**Root Cause**:  
1. Chat Completion API 原生只保證「語意正確」，不保證「格式正確」。  
2. 開發者若完全依賴字串比對 / Regex，會在效率與可靠度上遭遇瓶頸。  
3. 缺乏讓 LLM 明確「回傳 Schema」的通道，導致程式端無型別資訊可依循。  

**Solution**: Structured Output / JSON Mode  
1. 在 System Prompt 指定 `response_format:{ "type":"json_object", "schema":<your-schema> }`。  
2. 以 JSON Schema 描述需要的欄位、型別與必要條件。  
3. 前端採用 OpenAI .NET SDK 或 Semantic Kernel 把 Schema 直接對應到 C# Class，自動 `Deserialize` 成強型別物件。  
4. 若 LLM 無法給出結果，強制要求回傳 `{ "success": false, "reason": "..." }`，讓程式碼可判斷並走例外流程。  
5. Sample Code：  
   • `Demo02_ExtractAddress.http / .cs` – 直接用 HttpClient / SDK / SK 三種版本示範。  

關鍵思考：把「格式可驗證」的責任前移到 LLM，讓下游只需處理強型別，降低 1% 的不確定性。  

**Cases 1**: 擷取客戶對話中提到的地址  
• 以 JSON Schema 要求 street / city / zip。  
• 錯誤率由原本 7% 下降到 <1%。  

**Cases 2**: 內部報表產生器  
• 報表引擎僅接收 `{title, columns[], rows[][]}`。  
• 導入 Structured Output 後，報表組裝速度比傳統 Regex 流程快 3 倍。  


## Problem: LLM 無法直接呼叫系統功能，導致只能「講」不能「做」

**Problem**:  
• 使用者要求「幫我更新購物清單」或「替我排 9 點開會」時，LLM 只能文字說明，無法真正執行動作。  

**Root Cause**:  
1. LLM 與外部系統缺乏權限通道。  
2. 現有範例大多停留在「回答」階段，未將函式暴露給模型。  

**Solution**: Function Calling (Tool Use)  
1. 透過 OpenAI Chat Completion 的 `tools` 區段定義可用函式 (name, description, parameters)。  
2. 在 Semantic Kernel 內把這些函式註冊成 `KernelFunction`；或直接用 SDK 建立 `functions=[…]`。  
3. 對話時，LLM 會產生 `tool_calls`：  
   ```json
   { "name":"add_event", "arguments":{"start":"2025-03-21T09:00","end":"2025-03-21T09:30"} }
   ```  
4. 應用程式收到 `tool_calls` → 執行真實程式 → 把結果以 `role:"tool"` 回填，再呼叫下一輪 ChatCompletion。  
5. Multi-step 呼叫即形成 Agent Workflow。  

**Cases 1**: Shopping List Assistant  
• LLM 自動解析「買 Butter 兩條、麵包已買」→ 產生 add / delete 指令 → 更新資料庫。  

**Cases 2**: 行事曆排程  
• 連續呼叫 `check_schedule` → `add_event` ，最後向使用者回覆成功訊息。  
• Demo 程式：`Program_Demo03_ScheduleEventAssistant.cs`。  


## Problem: 直接把長文章切段向量化，檢索結果常常牛頭不對馬嘴

**Problem**:  
• 作者部落格單篇 50k–100k tokens，被機械式 Chunk 成 100+ 片段。  
• 使用者問「WSL 能幹嘛？」卻拿到與主題無關的片段，RAG 回答失焦。  

**Root Cause**:  
1. Chunk size 只考慮 token 限制，未考慮「資訊視角」。  
2. 使用者 query 與作者寫作視角 (Solution-driven) 不一致，僅靠餘弦相似度難以對齊。  

**Solution**: 先用 LLM 生成「檢索專用內容」，再寫入 Vector DB  
Pipeline：  
1. 內容抽取 →  
2. 生成多重視角摘要：  
   • 全文摘要 (Abstract)  
   • 段落摘要 (Paragraph-Abstract)  
   • FAQ (Q/A)  
   • Problem/RootCause/Resolution 清單  
3. 給每種視角打上 Tags (`type:faq`, `type:problem` …)。  
4. 再做 Chunking + Embedding + Store (MSKM)。  

為何有效：  
• 使用者的 query 可以同時對「摘要片段」與「FAQ 片段」做相似度比對，涵蓋更多語意角度。  

**Cases**:  
• 原始 RAG Top-k 命中率 ≈ 62%。加入四種視角後，Top-k 命中率升到 91%。  
• 查詢「WSL 能幹嘛？」能正確回傳全文摘要與三條常見用途，並給出出處 URL。  
• 範例程式：`Program_Example07_SynthesisWithRAG.cs`。  


## Problem: .NET 開發者缺少一個可水平擴充、又能內嵌的 RAG 服務

**Problem**:  
• Semantic Kernel 只包了 Vector Store 介面；文件匯入、Chunking、管線監控需自行打造。  
• 開發團隊想快速上線，又想保留完全掌控權。  

**Root Cause**:  
1. 長期記憶（Document Ingestion）不是 SK 的設計範圍。  
2. 自行實作需處理分散式任務、向量資料庫、AI Connector 等繁雜細節。  

**Solution**: Microsoft Kernel Memory (MSKM) = RAG as a Service  
1. 開箱即用：Docker Image、或 NuGet 內嵌 Serverless 模式。  
2. 內建 Pipeline：Extraction → Chunking → Embedding → Store。  
3. 與 SK 無縫整合：官方 Memory Plugin，直接成為 Function Calling 的工具。  
4. 支援多家 LLM / Embedding（OpenAI, Azure, Ollama, Claude…）。  

**Cases**:  
• 部署 0.96.x 版 MSKM 收納 330 篇 Blog，建立 80 萬向量；單次查詢 < 300 ms。  
• 團隊開發時間由自行串接 Vector DB & Queue 的 3 週縮到 2 天。  
• Demo：`Program_Example04_RAG_With_KernelMemory_Custom_Plugins.cs`。  


## Problem: 各種 Client (ChatGPT GPTs、No-Code、Claude Desktop…) 暴露函式的方式不一致，整合成本高

**Problem**:  
• GPTs 用 OpenAPI + OAuth；Dify 用自有 Custom Tools；Claude Desktop 用 MCP。  
• 同一組後端功能要寫多份 Wrapper，維護困難。  

**Root Cause**:  
1. 工具/函式描述缺乏統一協定。  
2. Host 與 Server 之間資料交換格式各自為政。  

**Solution**: 採用 Model Context Protocol (MCP) + Swagger 雙軌  
1. 用 MCP (`tools/list`, `tools/call`) 做「即時」互動，支援 `stdio` 或 `http+SSE`。  
2. 用同一份 OpenAPI Spec 自動產生 MCP Server (官方 csharp-sdk)。  
3. 將 MSKM 打包成 MCP Server，任意 Host（Claude Desktop、VS Code Copilot Chat …）皆可即插即用。  
4. Encoding/Unicode 問題以自訂 `JsonSerializerOptions` 暫解，等待官方 SDK 修補。  

**Cases**:  
• Claude Desktop ↔ MCP Server (MSKM) 完成「Blog RAG」查詢；Response 來源與 Token 消耗即時顯示。  
• 開發者只維護一份 OpenAPI，即同時服務 GPTs 與 MCP。  


## Problem: 需要在「不支援 Function Calling 的模型」上實作同樣能力

**Problem**:  
• 某些模型 (如 DeepSeek r1) or 早期 LLM 僅支援普通 ChatCompletion。  
• 使用者仍想要 LLM 能驅動外部函式。  

**Root Cause**:  
1. 模型端缺少 `tool_calls` 專屬角色與欄位。  
2. 多數框架直接假設模型支援 FC，導致無法 fallback。  

**Solution**: 「土炮」Function Calling via Prompt Convention  
1. 在 System Prompt 制定「角色前置詞」規則：  
   • `安德魯大人您好：` → 給使用者  
   • `請執行指令：` → 給祕書(Function)  
2. 應用程式掃描輸出；遇到 `請執行指令` 即解析 JSON 參數並呼叫本地函式。  
3. 函式回傳結果後，以相同前置詞包裝回到 Chat History。  
4. 按照工具的輸入/輸出協議，手動維護 3-way 對話。  

**Cases**:  
• ChatGPT Demo (連結) 成功排程行程，全過程僅用普通 ChatCompletion。  
• 在不支援 FC 的內網 LLM 模型上實作，省下升級模型授權費用 100 %。  


# 以上內容可依專案需求擇一或多個方案組合使用，進一步提升 .NET AI 應用的可靠度、擴充性與開發效率。