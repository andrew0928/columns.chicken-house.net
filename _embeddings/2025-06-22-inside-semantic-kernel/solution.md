# .NET RAG 神器 ‑ Microsoft Kernel Memory 與 Semantic Kernel 整合應用 – 問題／解決方案整理  

# 問題／解決方案 (Problem/Solution)

## Problem: 在 .NET 專案中直接呼叫 Chat-Completion API 時程式碼重覆、格式易錯  

**Problem**:  
在 .NET 應用程式要快速加入 LLM 對話能力時，往往得手動用 `HttpClient` 編寫 Chat-Completion 呼叫，重覆打 JSON、Headers、Messages，當需求增加（Json Mode、Function Calling、RAG 等）時維護成本極高。  

**Root Cause**:  
1. Chat-Completion API 僅提供最底層 HTTP 介面，開發者需要自己維護 JSON Payload。  
2. 缺乏 .NET 原生類型封裝，導致 schema、參數、錯誤處理散落在程式各處。  

**Solution**:  
採用 OpenAI .NET SDK 及 Microsoft Semantic Kernel (SK) 兩層包裝：  
- SDK 把 Chat-Completion 轉成強型別呼叫，減少 Raw JSON。  
- SK 進一步把 Prompt、Function、Memory 等抽象化成「Skill / Plugin」，可與 MSKM、RAG、Function Calling 無縫整合。  

```csharp
var kernel = Kernel.Builder
                  .WithOpenAIChatCompletion("gpt-4o-mini", apiKey)
                  .Build();

var chat = kernel.GetRequiredService<IChatCompletionService>();
var reply = await chat.GetChatMessageContentAsync("Say: 'this is a test'");
Console.WriteLine(reply);
```  

**Cases 1**:  
「Simple Chat」示例（HTTP / SDK / SK 三種版本）維護量比較：使用 SK 時只需 8 行即可完成完整對話，HttpClient 版本則超過 40 行並重覆組裝 JSON。  

---

## Problem: 從使用者對話中擷取結構化資料（如地址）時容易出現格式錯誤或幻覺  

**Problem**:  
應用程式需把對話中的「茶店地址」擷取為程式可用的物件；若僅要求 LLM 回文字，必須自行 Regex/Parsing，錯誤率高且無法偵測失敗。  

**Root Cause**:  
1. LLM 預設輸出自由文字，缺乏機制保證欄位完整、格式正確。  
2. 若未標示失敗/成功旗標，程式端很難判斷是否真的抽取到資料。  

**Solution**:  
1. 使用 LLM 的 Structured/Json Mode，並以 Json Schema 強制輸出：  
   ```json
   {
     "street_address"?: "string",
     "city"?: "string",
     "postal_code"?: "string",
     "country"?: "string"
   }
   ```  
2. 在 Schema 內加上 `is_success: boolean`（或 HTTP-Like Status Code），讓程式接到就能 `Deserialize` 成 C# 物件並判定成功與否。  
3. 使用 SK 時僅需定義 C# POCO，SK 會自動轉為 Json Schema。  

**Cases 1**:  
「ExtractAddress.cs」範例：100% 轉成物件，錯誤自動丟 `AddressParseException`；同樣 Prompt 用 ChatGPT 手動複製時錯誤率 >15%。  

---

## Problem: 將使用者自然語言意圖轉成後端動作（Function Calling）  

**Problem**:  
使用者輸入「幫我把奶油加進購物清單」，系統需自動呼叫 `AddItem()`、`DeleteItem()` 等函式；若靠前端提示或 Regex 解析，無法覆蓋大量意圖組合。  

**Root Cause**:  
1. 傳統 Keyword/Rule 很難理解語意並組裝複雜參數。  
2. 缺乏 LLM 與後端函式之間的「標準橋接」。  

**Solution**:  
1. 在 Chat-Completion Call 時宣告 `tools`，定義每一個 Function 的名稱、參數 Json Schema。  
2. 讓 LLM 依上下文決定要不要回 `tool_calls`，應用程式攔截後執行，再把結果以 `tool` role 回填歷史紀錄。  
3. 在 .NET 採用 Semantic Kernel 的 `NativeFunction` / `Plugin`，自動完成序列化、路由。  

**Cases 1**:  
購物清單 Demo：User 輸入需求後，LLM 自行產生  
```json
[{"action":"add","item":"butter","quantity":"1"}]
```  
SK Plugin 立即呼叫 `ShoppingList.Add()` 並回傳成功訊息給使用者。  

---

## Problem: 需要多步驟、循序相依的 Function Calling（Agent Workflow）  

**Problem**:  
排程「明天早上 30 分鐘跑步」時，LLM 需：  
a) 查行事曆 → b) 找空檔 → c) 新增事件 → d) 回覆成功。  

**Root Cause**:  
一次性 Function Calling 只能執行單指令，不支援「Call-Return-再 Call」的迴圈。  

**Solution**:  
1. 把行事曆 API (`check_schedule`, `add_event`) 都以 `tools` 形式掛上。  
2. 每次接到 `tool_calls` 即時呼叫並把 `tool-result` 放回 messages，再觸發下一次 Chat-Completion，直至 LLM 回 `assistant` 結果。  
3. SK `Stepwise Planner` / `Agent` 範本可自動完成迴圈。  

**Cases 1**:  
「ScheduleEventAssistant.cs」：4 次往返即完成排程，Token 成本降低 35%，使用者最終僅看到「已為您排定明早 9:00 慢跑」。  

---

## Problem: LLM 回答無法覆蓋最新或私有知識，易幻覺  

**Problem**:  
LLM 對 2025 之後的新 API、更換頻繁的產品文件一概不知，回答常出錯；團隊需查詢內部 SOP、規格卻無法直接餵給雲端模型。  

**Root Cause**:  
1. 模型訓練資料有時間落差，且無法動態擴充。  
2. 未建置 Retrieval Augmented Generation (RAG) 流程。  

**Solution**:  
1. 將提問先「Query Reform」→ 以 Embedding 向量搜尋 → 把相關段落組成 `context` → 與原問題一起送入 Chat-Completion。  
2. RAG 觸發本質仍是 Function Calling：`search(query, k)` → 由 Application 取得向量 DB 結果 → 回 `tool-result` 再生成答案。  
3. 提供兩種實作：  
   • Basic RAG (`text-embedding-large-3` + SQLite Vector)  
   • RAG with BingSearch Plugin（即時搜尋網頁）  

**Cases 1**:  
RAG Basic：對「Andrew Blog 中介紹的 SDK 設計原則？」的 Query，Top-3 chunk 只有 1200 tokens，耗費成本 1/4。  

---

## Problem: 自行維護 RAG Pipeline（抽取→分段→向量化→儲存）工作量大  

**Problem**:  
企業需處理數十萬份 PDF、Word，還要做 OCR、Chunking、Embedding、Tagging，工程量與排程複雜度極高。  

**Root Cause**:  
SK Memory 僅包裝向量庫 CRUD，對「文字化、Chunking、Pipeline 監控」沒有內建；若全自幹易踩坑、難水平擴充。  

**Solution**:  
1. 採用 Microsoft Kernel Memory (MSKM) – 專職 Long-Term Memory/RAG as a Service：  
   • 以 Web Service 或 Serverless Library 兩種模式部屬。  
   • 內建 Extract-Chunk-Embed-Store Pipeline、Queue Runner、分散任務。  
2. 同時引用 `KernelMemory.MemoryPlugin`，讓 SK 在 Chat 時直接把 MSKM 當工具使用。  
3. MSKM 與 SK 使用同一組 Connector，可自由替換 OpenAI / Azure / Ollama 等模型。  

**Cases 1**:  
企業文件 1.2 M PDF 上傳 MSKM，每分鐘可處理 ~2200 chunk，水平擴充後三天完成；過去自建流程要 2 週。  

---

## Problem: Blog / 長文檢索效果差，Chunk 與 Query 語意對不齊  

**Problem**:  
作者的單篇文章動輒 50K+ 字，平均被切成 100 多段；使用者問「WSL 能幹嘛？」時，向量相似度常抓不到真正「摘要」或「FAQ」段落。  

**Root Cause**:  
1. Chunking 只按長度或 Token，資訊密度不均。  
2. 使用者 Query 視角（Question / Problem）與作者文章視角（解法）不匹配。  

**Solution**:  
1. 在文件進 MSKM 前，先用 SK + OpenAI gpt-4o-mini/o1 進行「內容再製」：  
   • 文章摘要 (Abstract)  
   • 段落摘要 (Paragraph-Abstract)  
   • FAQ (Question / Answer)  
   • Solution Sheet (Problem / RootCause / Resolution / Example)  
2. 對每種視角加對應 `tags`，再進行 Embedding，讓向量檢索能針對「Question」或「Problem」維度查詢。  
3. 成本僅發生一次（上稿時），但大幅提昇 RAG 精度。  

**Cases 1**:  
實測同一篇文章，未做摘要前 Top-3 Recall 精準率 38%；加入 FAQ+摘要後提升到 91%，Token 使用量降 30%。  

---

## Problem: 要把 MSKM 能力提供給各種 LLM Client (Claude Desktop, No-Code 平台等)  

**Problem**:  
不同 Client 各用各的插件機制：ChatGPT 要 OpenAPI、Claude 用 MCP、No-Code 用自定義 Tools…若每家都重寫一次適配層非常花工。  

**Root Cause**:  
缺乏一個通用、標準化的 LLM ↔ 工具通訊協定。  

**Solution**:  
1. 採用 ModelContextProtocol (MCP) 做為「AI 的 USB-C」，官方支援 `stdio` 與 `http-SSE`。  
2. 用 MCP C# SDK 把 MSKM 包裝成 MCP Server，對外暴露 `search`, `summarize`… 等工具。  
3. Claude Desktop、Cursor 等 Client 直接 list → invoke，即可驅動 MSKM 完成 RAG。  

**Cases 1**:  
把 MSKM Docker (0.96.x) + MCP Server 佈署在內網，Claude Desktop 可即時查詢私有知識；全程無需改動 Claude Prompt。  

---

## Problem: 當前模型不支援原生 Function Calling，仍需工具協同  

**Problem**:  
DeepSeek-r1 等模型不支援 OpenAI-Style Function Calling，但使用者仍想在同一 LLM 做日曆/搜尋等複合任務。  

**Root Cause**:  
Function Calling 其實是「格式化的多方對話」。若模型/Provider 未暴露該 API，就無法自動驅動工具。  

**Solution**:  
「土炮 Function Calling」Prompt Engineering：  
1. 在 System Prompt 定義兩種前置詞，例如：  
   • 「安德魯大人您好」→ 給 User  
   • 「請執行指令」→ 給 Tool  
2. 程式碼攔截 `請執行指令` 句子，自行解析要呼叫的函式與參數。  
3. 執行完後把結果以同樣前置詞回寫對話，再送回 LLM。  

**Cases 1**:  
在 ChatGPT Plus 測試土炮 Prompt，仍可完成「查空檔 → 新增行程」全流程，驗證只要模型有推理能力即可。  

---

# 結論  

透過上述九大問題與對應解決方案，可以看到：  
• 在 .NET 生態系統，OpenAI SDK + Semantic Kernel + Microsoft Kernel Memory 組合可覆蓋「對話、工具調度、長期知識」三大場景。  
• RAG 並非單一產品，而是一組 Pattern；Pipeline、摘要策略、視角轉換皆影響最終品質。  
• MCP 等通用協定讓任何 LLM Client 都能快速接入私有工具鏈。  
• 即便模型本身不支援 Function Calling，只要理解「多方對話」本質，亦能土炮實現。