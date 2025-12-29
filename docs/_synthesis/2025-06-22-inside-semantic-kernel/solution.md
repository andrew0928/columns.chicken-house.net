---
layout: synthesis
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用 - solution"
synthesis_type: solution
source_post: /2025/06/22/inside-semantic-kernel/
redirect_from:
  - /2025/06/22/inside-semantic-kernel/solution/
---

以下為基於文章內容所萃取與重構的問題解決案例。每個案例均包含問題、根因、方案與實作細節、關鍵程式碼/設定、實際案例與環境、學習要點與練習題，以及評估標準。共 16 個案例，覆蓋 Chat Completion 基礎、Structured Output、Function Calling、RAG、MSKM 與 MCP 整合等主題。

## Case #1: 正確實作 Chat Completion 對話循環

### Problem Statement（問題陳述）
- 業務場景：團隊要在 .NET 應用中實作長對話式助理（如 ChatGPT 類體驗），需要確保多輪對話能保持上下文一致，並可在不同存取方式（HTTP、OpenAI .NET SDK、Semantic Kernel）間切換。
- 技術挑戰：如何正確組織 messages（system/user/assistant）並每次帶上完整 chat history；如何在不同 SDK/框架下維持一致行為。
- 影響範圍：若未帶齊歷史訊息或 role 使用錯誤，將導致答非所問、上下文遺失與行為不一致。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未正確帶入完整 chat history：多輪時只傳最後一輪，導致模型無法延續上下文。
  2. 角色使用不當（system/user/assistant）：優先級與用途混淆，prompt 規約失效。
  3. 框架差異未抽象：HTTP、SDK、SK 的呼叫方式各異，缺乏共用封裝。
- 深層原因：
  - 架構層面：缺少對話狀態管理的抽象層。
  - 技術層面：對 Chat Completion 訊息結構與優先級理解不足。
  - 流程層面：未建立多輪對話的測試與驗證流程。

### Solution Design（解決方案設計）
- 解決策略：建立「對話狀態」抽象，統一封裝訊息序列化與角色管理；不論 HTTP/SDK/SK，皆以相同的 message list 作業，每次呼叫帶上完整歷史，確保可重放與一致性。

- 實施步驟：
  1. 建立 ConversationStore
  - 實作細節：保存 system、user、assistant、(tool/tool-result 見 Case #5/#17) 訊息序列。
  - 所需資源：本地記憶體或持久化儲存（Redis/DB）
  - 預估時間：0.5 天
  2. 封裝 ChatClient
  - 實作細節：提供 SendAsync(messages)；針對 HTTP/SDK/SK 實作多個 adaptor。
  - 所需資源：OpenAI API key、OpenAI .NET SDK、Semantic Kernel
  - 預估時間：1 天
  3. 加入最小化測試
  - 實作細節：用固定 script 驗證各 adaptor 回應一致性。
  - 所需資源：xUnit/NUnit
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```http
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer {{OpenAI_APIKEY}}
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "messages": [
    { "role": "system", "content": "you are a tester, answer me what I ask you." },
    { "role": "user", "content": "Say: 'this is a test'." }
  ],
  "temperature": 0.2
}
// Response: choices[0].message.content => "This is a test."
```

- 實際案例：Day 0, Simple Chat（HTTP/SDK/SK 三種示範）
- 實作環境：OpenAI Chat Completions（gpt-4o-mini）；.NET（HTTP、OpenAI .NET SDK、Semantic Kernel）
- 實測數據：
  - 改善前：多輪對話易遺失上下文
  - 改善後：統一封裝後對話可重放、行為一致
  - 改善幅度：定性改善（文章未量化）

- Learning Points（學習要點）
  - 核心知識點：
    - Chat Completion 三種角色與優先權
    - 每輪帶上完整 messages 的重要性
    - 封裝 adaptor 以統一行為
  - 技能要求：
    - 必備技能：HTTP API、.NET 序列化、基本單元測試
    - 進階技能：抽象化設計、可測性設計
  - 延伸思考：
    - 如何持久化 chat history（DB/Cache）？
    - 如何在 tool calling 場景擴展（見 Case #5/#17）？
    - 是否需要記錄 token 使用量以控成本？

- Practice Exercise（練習題）
  - 基礎練習：用 HTTP 重現 Simple Chat（30 分）
  - 進階練習：以 OpenAI SDK 與 SK 各實作一次（2 小時）
  - 專案練習：撰寫一個可切換 Provider 的 ChatClient（8 小時）

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：可支援多輪與三種 adaptor
  - 程式碼品質（30%）：清晰封裝、單元測試到位
  - 效能優化（20%）：控制 messages 長度與 token
  - 創新性（10%）：可插拔式 Provider 設計

---

## Case #2: 用 JSON Mode 擷取地址並可判定成功/失敗

### Problem Statement（問題陳述）
- 業務場景：在企業應用中需從大量對話記錄擷取地址，供後續地圖/物流系統使用，要求輸出可被程式安全解析並能判定是否成功擷取。
- 技術挑戰：自由文字輸出難以可靠解析；當 LLM 無法判定地址時需可明確失敗，避免程式猜測。
- 影響範圍：若無結構化 output 與成功旗標，將造成大量解析錯誤與例外處理成本。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 自然語言輸出不可預期：無 JSON schema 約束，格式不穩。
  2. 無明確成功/失敗：無法直接判斷是否有足夠資訊。
  3. 需求混雜：同時讓 LLM 查景點或其他工作增加成本與錯誤。
- 深層原因：
  - 架構層面：缺少資料交換契約（schema-first）。
  - 技術層面：未使用 JSON Mode/Schema。
  - 流程層面：未採單一職責，導致後續流程耦合。

### Solution Design（解決方案設計）
- 解決策略：使用 JSON Mode 並提供 JSON Schema，強制 LLM 產出可反序列化的結構；加入 success 與 reason 欄位；下游系統（如 Google Maps）由程式碼處理，職責分離。

- 實施步驟：
  1. 定義輸出 Schema
  - 實作細節：street_address/city/postal_code/country + success + reason
  - 所需資源：JSON schema、C# DTO
  - 預估時間：0.5 天
  2. 設定 ChatCompletion 的 response_format/schema
  - 實作細節：HTTP/SDK/SK 皆可；SK 可用 C# type 映射
  - 所需資源：OpenAI ChatCompletion
  - 預估時間：0.5 天
  3. 反序列化與驗證
  - 實作細節：若 success=false 則走補救流程（人工/重試）
  - 所需資源：System.Text.Json / Newtonsoft.Json
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
{
  "messages":[
    {"role":"system","content":"Extract address from text; respond as JSON per schema."},
    {"role":"user","content":"- For the tea shop in Paris ... 90, I guess."}
  ],
  "response_format":{
    "type":"json_schema",
    "json_schema":{
      "name":"address_extraction",
      "schema":{
        "type":"object",
        "properties":{
          "success":{"type":"boolean"},
          "reason":{"type":"string"},
          "street_address":{"type":["string","null"]},
          "city":{"type":["string","null"]},
          "postal_code":{"type":["string","null"]},
          "country":{"type":["string","null"]}
        },
        "required":["success","reason"]
      }
    }
  }
}
```

- 實際案例：Day 1, Structured Output（HTTP/SDK/SK 全套）
- 實作環境：OpenAI（支援 JSON Schema 的模型，如 GPT-4o-mini）
- 實測數據：
  - 改善前：自由文字解析不穩，例外多
  - 改善後：可直接反序列化，流程分支可控
  - 改善幅度：定性改善（文章未量化）

- Learning Points（學習要點）
  - 核心知識點：JSON Mode/Schema；可機器判讀的成功旗標；單一職責
  - 技能要求：JSON schema、反序列化、例外流程設計
  - 延伸思考：是否需要信心分數？如何設計重試或人工校對流？

- Practice Exercise（練習題）
  - 基礎練習：為地址擷取補上 success/reason 欄位（30 分）
  - 進階練習：串接地圖 API 僅在 success=true 時執行（2 小時）
  - 專案練習：批次處理 10k 筆對話並產出地址清單（8 小時）

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：JSON schema 限制與錯誤分支
  - 程式碼品質（30%）：DTO 與驗證清楚
  - 效能優化（20%）：批次/並行處理
  - 創新性（10%）：補救策略（自動校正/多模型）

---

## Case #3: 單一職責設計，降低 Token 成本與錯誤率

### Problem Statement（問題陳述）
- 業務場景：批量資料處理場景下，若把查詢/計算/格式轉換等通通交給 LLM，成本與錯誤率升高。
- 技術挑戰：將純程式就能高效完成的工作從 LLM 中抽離，以 JSON 作為 LLM 與程式的邊界。
- 影響範圍：成本被放大至百萬級呼叫；錯誤可傳染下游系統。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 一次 Prompt 做完所有事導致 Token 高、錯誤多。
  2. 沒有任務拆分標準，職責不清。
  3. 程式可處理的需求交由 LLM 處理。
- 深層原因：
  - 架構層面：未定義清楚子系統責任。
  - 技術層面：缺乏 schema-first 的資料交換設計。
  - 流程層面：缺少成本監控與效能度量。

### Solution Design（解決方案設計）
- 解決策略：採取 LLM 專責抽取/推理，所有搜尋/計算/格式化都移回程式；以 JSON 封裝交換資料，並在輸出加上成功旗標。

- 實施步驟：
  1. 任務拆分與圖譜化
  - 實作細節：以流程圖標註哪些步驟是 LLM-only
  - 所需資源：流程設計工具
  - 預估時間：0.5 天
  2. 實作 JSON 出口與程式入口
  - 實作細節：同 Case #2 schema；後續 code 呼叫外部 API（Google Maps 等）
  - 所需資源：OpenAI/SDK、外部 API Key
  - 預估時間：1 天
  3. 監控與成本對比
  - 實作細節：度量每步 Token 與費用
  - 所需資源：Logging/Telemetry
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 1) LLM: Extract address only
var addr = await ExtractAddressAsync(chat);

// 2) Code: Call Maps only when success
if (addr.Success)
{
    var loc = await Maps.GeocodeAsync(addr);
    // proceed...
}
```

- 實際案例：Day 1 中對單一職責與成本的強調
- 實作環境：OpenAI ChatCompletion + 自行後端程式
- 實測數據：
  - 改善前：LLM 一次做到底，成本高
  - 改善後：LLM 只做必要部分，程式接手剩餘任務
  - 改善幅度：定性改善（文章未量化）

- Learning Points
  - 核心知識點：任務拆分、邊界設計、成本意識
  - 技能要求：API 整合、流程設計
  - 延伸思考：如何以工作流引擎控制任務編排？

- Practice Exercise
  - 基礎：把一個混雜 Prompt 改為 LLM 抽取 + 程式後處理（30 分）
  - 進階：加上成本與 Token 監控（2 小時）
  - 專案：將三個外部 API 的串接改為工具鏈（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：任務拆分正確
  - 程式碼品質（30%）：分層清晰
  - 效能優化（20%）：Token/費用下降
  - 創新性（10%）：可重用的模板/框架

---

## Case #4: Function Calling（Basic）把自然語言轉為可執行指令

### Problem Statement（問題陳述）
- 業務場景：使用者以自然語言維護購物清單，系統需自動解析意圖、轉換為 add/delete 指令供後端執行。
- 技術挑戰：設計可機器處理的指令格式與參數並讓 LLM 自動輸出。
- 影響範圍：若解析不準會錯加錯刪，造成實際業務錯誤。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺少標準化工具規範（action/args）。
  2. 未定義固定 JSON 輸出格式，難以解析。
  3. 只完成「Call」，未思考「Return」。
- 深層原因：
  - 架構層面：缺少工具規格與通用執行器。
  - 技術層面：未善用 JSON Mode 搭配工具參數。
  - 流程層面：無指令執行結果回饋流程。

### Solution Design
- 解決策略：先定義可用的 action 與參數，要求 LLM 以 JSON 指令清單輸出；程式端依序執行；此為「呼叫前半段」基礎（回傳見 Case #5）。

- 實施步驟：
  1. 設計 action schema
  - 實作細節：add/delete、item、quantity
  - 所需資源：JSON schema
  - 預估時間：0.5 天
  2. Prompt 與測試
  - 實作細節：以例句驗證多模型一致輸出
  - 所需資源：ChatGPT/SDK
  - 預估時間：0.5 天
  3. 指令執行器
  - 實作細節：把 JSON 轉為實際清單操作
  - 所需資源：後端程式
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
[
  { "action": "add", "item": "butter", "quantity": "1" },
  { "action": "add", "item": "zucchinis", "quantity": "2" },
  { "action": "delete", "item": "bread" }
]
```

- 實際案例：Day 2, Function Calling（Basic）
- 實作環境：OpenAI ChatCompletion + 自行後端
- 實測數據：
  - 改善前：需要人工解析自然語言
  - 改善後：自動產生機器可執行指令
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：工具設計、JSON 指令化
  - 技能要求：結構化輸出與解析
  - 延伸思考：如何加入錯誤/衝突處理？

- Practice Exercise
  - 基礎：把聊天輸出轉成固定 JSON 指令（30 分）
  - 進階：加入基本驗證與衝突處理（2 小時）
  - 專案：做一個 Shopping List Bot（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：完整 add/delete 流
  - 程式碼品質（30%）：解析器與執行器清晰
  - 效能優化（20%）：批次處理與重試
  - 創新性（10%）：自動合併/去重邏輯

---

## Case #5: Function Calling（Sequential）以工具結果驅動下一步

### Problem Statement（問題陳述）
- 業務場景：行程助理需查行程空檔後自動建立事件並回覆使用者，過程包含多次工具調用與依賴前一步結果。
- 技術挑戰：三方對話（user/assistant/tools）的訊息管理；正確傳遞 tool 與 tool-result。
- 影響範圍：若遺漏訊息或循環控制不佳，任務會卡住或答非所問。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 未將 tool 與 tool-result 併入 chat history。
  2. HTTP/SDK 手動管理太多細節，易錯。
  3. 缺少有狀態的多輪控制迴圈。
- 深層原因：
  - 架構層面：對話狀態機制不足。
  - 技術層面：tool_calls 與 result 對接不熟悉。
  - 流程層面：未設計「直到完成」的 loop。

### Solution Design
- 解決策略：落實 tool/tool-result 訊息，建立「推進迴圈」：assistant 要工具 -> app 執行 -> tool-result 回填 -> 再呼叫模型；直到 assistant 輸出面向使用者的最終訊息。

- 實施步驟：
  1. 設計 Tool Registry 與執行器
  - 實作細節：check_schedules, add_event
  - 所需資源：插件/服務
  - 預估時間：1 天
  2. 建立對話推進迴圈
  - 實作細節：偵測 tool_calls；執行並回填 tool-result
  - 所需資源：Chat client
  - 預估時間：1 天
  3. 加入錯誤與終止條件
  - 實作細節：最大迭代、超時、工具錯誤處理
  - 所需資源：Logging/Policy
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
// 歷史摘要（節錄）：
// 1) system: tools [check_schedules, add_event]
// 2) user: find a 30 min slot...
// 3) assistant: tool_calls -> check_schedules(06:00~12:00)
// 4) tool-result: ["07:00-08:00...", "08:00-09:00...", "10:00-12:00..."]
// 5) assistant: tool_calls -> add_event(09:00-09:30)
// 6) tool-result: ["success"]
// 7) assistant: "Morning run scheduled for tomorrow at 9am!"
```

- 實際案例：Day 3, Schedule Event Assistant（HTTP + Semantic Kernel）
- 實作環境：OpenAI ChatCompletion；Semantic Kernel 工具框架
- 實測數據：
  - 改善前：只完成「Call」無「Return」的單步指令
  - 改善後：可連續決策與執行，產出面向使用者的最終結果
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：tool_calls/tool-result 模式；狀態驅動循環
  - 技能要求：對話狀態管理、錯誤處理
  - 延伸思考：如何做規模化的多工具規劃（Planning）？

- Practice Exercise
  - 基礎：實作單一工具的 tool->result 回填（30 分）
  - 進階：加入第二個工具並串聯結果（2 小時）
  - 專案：完成行程助理（含錯誤與超時）（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：能從詢問到建立事件
  - 程式碼品質（30%）：清楚的 loop 與訊息處理
  - 效能優化（20%）：控制迭代與 token
  - 創新性（10%）：可視化對話流程

---

## Case #6: 用框架（Semantic Kernel/No-Code）簡化多工具協作

### Problem Statement（問題陳述）
- 業務場景：需要多工具的連續調用（RAG、行程、天氣等），用純 HTTP/SDK 管理 tool_calls 細節成本高且易錯。
- 技術挑戰：統一工具規格、快速註冊/暴露工具、處理多輪對話的複雜性。
- 影響範圍：若自行土法煉鋼，維護性與交付速度受阻。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 沒有共通的工具註冊/調用機制。
  2. 手寫 loop 與 message 管理出錯機率高。
  3. 工具組態與安全未標準化。
- 深層原因：
  - 架構層面：缺少統一的 Agent/Tool 宿主。
  - 技術層面：忽略成熟框架（SK、Dify）。
  - 流程層面：缺乏工具生命週期治理。

### Solution Design
- 解決策略：採用 Semantic Kernel（或 Dify 等）承載工具、規格、與多輪控制；以 OpenAPI/Swagger 直接注入工具；減少樣板碼。

- 實施步驟：
  1. 工具註冊
  - 實作細節：SK 載入原生/HTTP/Swagger 工具
  - 所需資源：SK、OpenAPI 規格
  - 預估時間：0.5 天
  2. 對話執行
  - 實作細節：使用 SK Orchestration 取代手寫 loop
  - 所需資源：SK Kernel
  - 預估時間：0.5 天
  3. 安全與觀測
  - 實作細節：API Key、Rate Limit、Log/Trace
  - 所需資源：內建或外掛
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var builder = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("gpt-4o-mini", apiKey)
    .AddOpenApiSkillFromFile("BingSearch", "bing-search.yaml"); // Swagger 直載

var kernel = builder.Build();
var result = await kernel.InvokePromptAsync("附近景點與出門準備？");
```

- 實際案例：Day 3 建議（SK/No-Code/Dify 等）
- 實作環境：Semantic Kernel；OpenAPI 工具
- 實測數據：
  - 改善前：大量自寫樣板碼與錯誤
  - 改善後：快速接工具、治理一致
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：工具注入（Swagger）、Orchestration
  - 技能要求：SK 使用、OpenAPI
  - 延伸思考：如何抽象多宿主（SK、MCP、GPTs）共用一套工具？

- Practice Exercise
  - 基礎：在 SK 中掛載一個 Swagger 工具（30 分）
  - 進階：同時掛兩個工具並串聯結果（2 小時）
  - 專案：以 SK 完成一個多工具助理（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：工具載入與調用完整
  - 程式碼品質（30%）：設定清楚且可重用
  - 效能優化（20%）：降低冗餘回合
  - 創新性（10%）：工具治理策略

---

## Case #7: 用 Function Calling 觸發 RAG 檢索與回答

### Problem Statement（問題陳述）
- 業務場景：要回答最新/專域知識，LLM 需先檢索外部來源（搜尋引擎或內部知識庫），並附上來源。
- 技術挑戰：讓 LLM 自主決定何時使用「搜尋」工具與生成查詢參數。
- 影響範圍：若不先檢索，易幻覺；若參數生成不當，檢索品質差。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 倚賴內建知識造成過時/幻覺。
  2. 無工具觸發機制，無法外部查詢。
  3. 查詢參數（query/limit/tags）生成不穩。
- 深層原因：
  - 架構層面：未納入檢索工具鏈。
  - 技術層面：未結合 Function Calling 與 JSON Mode。
  - 流程層面：未要求引用來源。

### Solution Design
- 解決策略：在 system prompt 中要求「需使用檢索工具並附來源」，提供 search 工具規格；讓 LLM 自動產生 query 與限制條件；完成後再統整回答。

- 実施步驟：
  1. 定義 search 工具
  - 實作細節：query, limit, tags
  - 所需資源：Bing API/MSKM 查詢 API
  - 預估時間：0.5 天
  2. 設定 RAG 回答規則
  - 實作細節：強制附上來源 URL
  - 所需資源：System prompt
  - 預估時間：0.5 天
  3. 測試與調參
  - 實作細節：限制最大工具呼叫次數
  - 所需資源：實測
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
"tools":[
  {
    "type":"function",
    "function":{
      "name":"search",
      "description":"Search knowledge base or web",
      "parameters":{
        "type":"object",
        "properties":{
          "query":{"type":"string"},
          "limit":{"type":"integer","default":3},
          "tags":{"type":"array","items":{"type":"string"}}
        },
        "required":["query"]
      }
    }
  }
]
```

- 實際案例：Day 4（RAG with Custom Prompt、Bing Search Plugin）
- 實作環境：OpenAI ChatCompletion + Bing Search or MSKM
- 實測數據：
  - 改善前：過時/幻覺
  - 改善後：可附來源、更新即時
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：RAG 基本流程、工具觸發
  - 技能要求：工具設計、Prompt 治理
  - 延伸思考：如何以 MSKM 取代外部搜尋？

- Practice Exercise
  - 基礎：撰寫 search 工具並要求附來源（30 分）
  - 進階：加入 tags/filters（2 小時）
  - 專案：做一個「本地知識庫 RAG」助理（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：可檢索且附來源
  - 程式碼品質（30%）：工具/參數清楚
  - 效能優化（20%）：限制工具回合與內容長度
  - 創新性（10%）：查詢改寫/擴展

---

## Case #8: 以 MS Kernel Memory（MSKM）提供 RAG-as-a-Service

### Problem Statement（問題陳述）
- 業務場景：需要長期記憶（Long-term Memory）與可規模化的文件匯入、分段、向量化與檢索，且要與 .NET/SK 緊密整合。
- 技術挑戰：SK Memory 僅抽象 Vector Store，缺少完整 ingestion pipeline 與服務化能力。
- 影響範圍：自行打造 ingestion 成本高，缺乏彈性與可運營性。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. SK Memory 僅處理儲存與檢索，缺少文件處理流水線。
  2. 大量文本處理需要可擴展的任務機制。
  3. 多模型/Connector 管理複雜。
- 深層原因：
  - 架構層面：缺少獨立的記憶服務。
  - 技術層面：需要多 Connector 與 Plugin 支援。
  - 流程層面：需要 DevOps 化部署與治理。

### Solution Design
- 解決策略：採用 MSKM 以「服務」方式提供長期記憶與 RAG Ingestion Pipeline；以 SDK/HTTP 使用；同時在 SK 端掛入 MSKM 的 Memory Plugin 供 LLM 使用。

- 實施步驟：
  1. 部署 MSKM
  - 實作細節：Docker 拉取官方 image 或 source build
  - 所需資源：Docker、配置檔
  - 預估時間：0.5~1 天
  2. 整合 SK
  - 實作細節：載入 MSKM Memory Plugin 至 SK
  - 所需資源：NuGet/設定
  - 預估時間：0.5 天
  3. 匯入與查詢
  - 實作細節：透過 MSKM API 匯入文件、查詢
  - 所需資源：MSKM SDK/HTTP
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```bash
# 以 Docker 運行（版本參考 Case #15 注意中文 chunking）
docker run -p 8000:8000 kernelmemory:0.96.x
```

- 實際案例：Day 5（RAG with Kernel Memory Plugins、Custom Plugins、官方 Demo）
- 實作環境：MSKM（Docker/SDK）、Semantic Kernel、OpenAI/Embedding/Connector
- 實測數據：
  - 改善前：自行處理 ingestion 流程繁雜
  - 改善後：服務化與插件化，快速上線
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：MSKM 與 SK 的互補關係
  - 技能要求：Docker、.NET SDK、插件整合
  - 延伸思考：如何做多租戶與權限治理？

- Practice Exercise
  - 基礎：啟動 MSKM 並以 HTTP 匯入一段文本（30 分）
  - 進階：在 SK 掛上 MSKM Memory Plugin 並查詢（2 小時）
  - 專案：完成一個文件到答案的端到端 RAG（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：匯入/檢索/整合 SK
  - 程式碼品質（30%）：設定與錯誤處理清楚
  - 效能優化（20%）：批次與併發匯入
  - 創新性（10%）：自訂 handler/插件

---

## Case #9: 以 LLM 先行生成「檢索專用資訊」提升 RAG 精度

### Problem Statement（問題陳述）
- 業務場景：文章很長（50k~100k 字），僅靠分段與相似度檢索，面對廣義問題（如「WSL 能幹嘛」）時會取到不對焦分段。
- 技術挑戰：資訊密度與視角不匹配，難以在分段中找到最合適上下文。
- 影響範圍：RAG 回答品質差，使用體驗不佳。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 單靠 chunking 難涵蓋摘要與概覽。
  2. 查詢視角與原文寫作視角不一致。
  3. 僅有原始分段向量化，缺少派生資料。
- 深層原因：
  - 架構層面：缺乏多視角資料層（摘要/FAQ/案例）。
  - 技術層面：未運用 LLM 生成檢索友善內容。
  - 流程層面：匯入流程未加入內容合成步驟。

### Solution Design
- 解決策略：在匯入前以 LLM 生成：全篇摘要、段落摘要、FAQ（Q/A）、解決方案案例（problem/root cause/solution/example），加上 tags 後再向量化入庫；查詢時可優先命中摘要或問答粒度更合適的內容。

- 實施步驟：
  1. 設計合成規格
  - 實作細節：定義四類派生內容與標籤策略
  - 所需資源：Prompt 模板
  - 預估時間：1 天
  2. 生成與入庫
  - 實作細節：用較強推理模型（如 o1）生成，再送 MSKM
  - 所需資源：SK + MSKM
  - 預估時間：1~2 天
  3. 查詢策略
  - 實作細節：優先檢索摘要/FAQ/案例，再補原文片段
  - 所需資源：檢索組合策略
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 以 SK 生成摘要 -> 再送 MSKM
var abstractText = await Llm.GenerateAsync("為下文產生<=1000字摘要: ...原文...");
await Mskm.ImportAsync(new MemoryRecord{
    Text = abstractText, Tags = new[]{"type:abstract","topic:WSL"}
});
```

- 實際案例：Day 6（Synthesize Content for RAG；Multiple Plugins Demo）
- 實作環境：SK + MSKM；OpenAI o1（文章示範用）
- 實測數據：
  - 改善前：向量檢索命中段落常不對焦
  - 改善後：優先命中摘要/FAQ/案例，品質顯著提升
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：生成式增強檢索（先生成後向量化）
  - 技能要求：Prompt 設計、標籤策略
  - 延伸思考：如何以自動化 Pipeline 量產派生內容？

- Practice Exercise
  - 基礎：為一篇文章產生 500 字摘要並入庫（30 分）
  - 進階：為每段產生段落摘要與 FAQ（2 小時）
  - 專案：建立自動化合成+入庫流水線（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：四類派生內容與檢索策略
  - 程式碼品質（30%）：可重入與錯誤復原
  - 效能優化（20%）：批次/快取/重用
  - 創新性（10%）：動態 rerank 或混檢索

---

## Case #10: 嵌入模型與 Chunk 尺寸對齊（Embedding Strategy）

### Problem Statement（問題陳述）
- 業務場景：使用 text-embedding-3-large 進行向量化，需設定合適 chunk 尺寸以提升語意檢索效果。
- 技術挑戰：模型建議輸入 512 tokens（上限 8191），若 chunk 不佳會影響相似度。
- 影響範圍：向量檢索失準，RAG 效果打折。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 未依模型建議設定 chunk 長度。
  2. 中文/多語 token 計數差異。
  3. 忽略重疊策略造成邊界資訊流失。
- 深層原因：
  - 架構層面：缺少可配置 chunker。
  - 技術層面：不熟 tokenization 差異。
  - 流程層面：無 A/B 測試不同 chunk 策略。

### Solution Design
- 解決策略：以 512 tokens 為目標 chunk size；針對中文加入重疊（如 10%）；提供可配置化 chunker 並對不同文類進行 A/B 測試。

- 實施步驟：
  1. 設定 chunker
  - 實作細節：target=512,max=800；overlap=10~15%
  - 所需資源：Tokenizer/Chunker
  - 預估時間：0.5 天
  2. A/B 測試
  - 實作細節：不同 chunk size/overlap 對比
  - 所需資源：簡單測試集
  - 預估時間：1 天
  3. 上線與觀測
  - 實作細節：收集查詢成功率與用戶回饋
  - 所需資源：Telemetry
  - 預估時間：1 天

- 關鍵程式碼/設定：
```json
// 假想的 chunk 設定
{
  "chunker": {
    "targetTokens": 512,
    "maxTokens": 800,
    "overlapRatio": 0.1,
    "language": "zh"
  }
}
```

- 實際案例：Day 6 對模型建議長度的說明
- 實作環境：OpenAI text-embedding-3-large；MSKM/自建 chunker
- 實測數據：
  - 改善前：檢索不穩定
  - 改善後：命中率提升（定性）
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：chunk size/overlap 對檢索影響
  - 技能要求：tokenization、A/B
  - 延伸思考：多語場景如何自適應？

- Practice Exercise
  - 基礎：用 512 tokens chunk 一篇文章（30 分）
  - 進階：比較 256/512/1024 命中差異（2 小時）
  - 專案：自動化 chunk 調參（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：可配置 chunker
  - 程式碼品質（30%）：參數可追蹤
  - 效能優化（20%）：批次向量化
  - 創新性（10%）：動態 chunking

---

## Case #11: 非文本內容（PDF/圖片）匯入與自訂 Handler

### Problem Statement（問題陳述）
- 業務場景：需將 PDF/圖片等非文本內容進行 OCR/文字擷取後再做 RAG。
- 技術挑戰：建立可擴展 pipeline：content extraction -> chunking -> embedding -> store。
- 影響範圍：若無法處理多媒體內容，知識覆蓋不足。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 僅處理純文字，忽略前處理。
  2. 缺乏可插拔 handler。
  3. OCR/擷取品質不控。
- 深層原因：
  - 架構層面：管線無標準化。
  - 技術層面：缺少多媒體處理經驗。
  - 流程層面：未定義清洗與檢核。

### Solution Design
- 解決策略：使用 MSKM pipeline（或自訂外部 pipeline）加入 Content Extraction handler（PDF->Text、Image->OCR），後續照 RAG 流程處理；可擴展自訂 handler。

- 實施步驟：
  1. 啟用 content extraction
  - 實作細節：為 PDF/圖片配置對應 handler
  - 所需資源：MSKM/外部服務
  - 預估時間：0.5~1 天
  2. 清洗與格式化
  - 實作細節：移除雜訊、表格/標題處理
  - 所需資源：文字處理工具
  - 預估時間：1 天
  3. 入庫與驗證
  - 實作細節：少量驗證品質後批量匯入
  - 所需資源：SDK/HTTP
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
{
  "pipeline": {
    "handlers": [
      "ContentExtractionHandler",
      "ChunkingHandler",
      "EmbeddingHandler",
      "StoreHandler"
    ]
  }
}
```

- 實際案例：Day 6 對 handler 與 pipeline 的說明
- 実作環境：MSKM pipeline、自訂 handler
- 實測數據：
  - 改善前：非文本無法納入 RAG
  - 改善後：多媒體可檢索
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：處理鏈設計、OCR 品質控制
  - 技能要求：文件處理、規則清洗
  - 延伸思考：如何記錄來源座標以精準引用？

- Practice Exercise
  - 基礎：將 PDF 轉文字並入庫（30 分）
  - 進階：加入 OCR 與清洗規則（2 小時）
  - 專案：通用文件匯入器（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：支援多格式
  - 程式碼品質（30%）：可插拔、容錯
  - 效能優化（20%）：批次並發
  - 創新性（10%）：版面保留與引用

---

## Case #12: 多插件組合回答複合問題（地點+天氣+搜尋）

### Problem Statement（問題陳述）
- 業務場景：查「我在這附近有什麼景點、出門帶什麼」，需用地點/天氣/搜尋三工具聯動。
- 技術挑戰：LLM 要能自行規劃工具順序與參數。
- 影響範圍：單一工具無法產生完整答案。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺少多工具協作設計。
  2. 參數（城市、日期）需自動抽取。
  3. 無法將工具結果綜合成最終回答。
- 深層原因：
  - 架構層面：工具組合規劃未設計。
  - 技術層面：未用框架承載工具鏈。
  - 流程層面：未設計引用來源規則。

### Solution Design
- 解決策略：在 SK 掛載 Location/Weather/BingSearch 三工具；以 Function Calling + JSON Mode 自動抽取參數；最後統整回答，附來源。

- 實施步驟：
  1. 掛載三工具
  - 實作細節：Location, Weather, Search（Swagger 或原生）
  - 所需資源：API 金鑰與規格
  - 預估時間：0.5 天
  2. 對話治理
  - 實作細節：要求附來源並說明建議
  - 所需資源：Prompt
  - 預估時間：0.5 天
  3. 測試與微調
  - 實作細節：邊界情境（無網、無城市）
  - 所需資源：測試集
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
kernel.Plugins.Add(LocationPlugin);
kernel.Plugins.Add(WeatherPlugin);
kernel.Plugins.Add(SearchPlugin);

var answer = await kernel.InvokePromptAsync(
  "請問我現在這邊有哪些值得逛的景點？出門要帶什麼？請附來源。"
);
```

- 實際案例：Day 4（RAG with Bing Search；多工具組合）
- 實作環境：Semantic Kernel + 多工具
- 實測數據：
  - 改善前：單工具回答不完整
  - 改善後：多源整合、實用性提升
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：多工具規劃與協作
  - 技能要求：工具註冊、參數抽取
  - 延伸思考：如何透過規劃（planning）最少步驟達成？

- Practice Exercise
  - 基礎：註冊兩個工具完成簡單任務（30 分）
  - 進階：加入第三工具並整合結果（2 小時）
  - 專案：打造旅遊建議 Agent（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：完整回答且附來源
  - 程式碼品質（30%）：工具管理清晰
  - 效能優化（20%）：步驟最少化
  - 創新性（10%）：智慧規劃策略

---

## Case #13: 以 MCP 將 MSKM 能力帶進 Claude Desktop

### Problem Statement（問題陳述）
- 業務場景：希望在桌面 LLM（Claude Desktop）直接使用本地/私有 RAG（MSKM）能力。
- 技術挑戰：不同客戶端需一致協定；需支援工具列出/呼叫、資源列表、提示等。
- 影響範圍：若無通用協定，整合成本高且不可移植。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 缺少通用協定連接 LLM 客戶端與後端工具。
  2. 每家客戶端整合方式不同。
  3. 中文傳輸編碼與通訊細節（見 Case #14）問題。
- 深層原因：
  - 架構層面：缺少標準化 Host-Server 協定。
  - 技術層面：不了解 JSON-RPC + stdio/SSE。
  - 流程層面：沒有工具生命週期管理。

### Solution Design
- 解決策略：實作 MCP server（csharp-sdk/自製），實作 initialize、tools/list、tools/call、resources/list 等；以 stdio 或 SSE 連 Claude Desktop；將 MSKM 查詢/匯入包裝為 MCP 工具。

- 實施步驟：
  1. 建立 MCP server 專案
  - 實作細節：引用官方 csharp-sdk 或 MCPSharp
  - 所需資源：Repo 範例
  - 預估時間：1 天
  2. 實作 tools/list/call
  - 實作細節：包裝 MSKM 檢索/匯入
  - 所需資源：MSKM SDK
  - 預估時間：1 天
  3. 連線與測試
  - 實作細節：console+stdio、Claude Desktop 連線
  - 所需資源：測試 Prompt（文章提供）
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
{"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"claude-ai","version":"0.1.0"}},"jsonrpc":"2.0","id":0}
{"method":"tools/list","params":{},"jsonrpc":"2.0","id":2}
{"method":"tools/call","params":{"name":"search","arguments":{"query":"SDK design","limit":3}},"jsonrpc":"2.0","id":9}
```

- 實際案例：Day 7（MCP Server 整合示範與截圖）
- 實作環境：Claude Desktop + MCP csharp-sdk/MCPSharp + MSKM
- 實測數據：
  - 改善前：桌面端無法直接用私有 RAG
  - 改善後：一鍵接入，像「AI 的 USB-C」
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：MCP 協定（JSON-RPC、tools、resources、prompts）
  - 技能要求：stdio/SSE、協定落地
  - 延伸思考：MCP 與 SK/GPTs 的關係與取捨

- Practice Exercise
  - 基礎：用 stdio 直連自製 MCP server（30 分）
  - 進階：在 MCP 暴露 MSKM 搜尋工具（2 小時）
  - 專案：完成「Claude x MSKM」查詢解決方案（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：工具列出/呼叫完整
  - 程式碼品質（30%）：協定實作清晰
  - 效能優化（20%）：串流與資源管理
  - 創新性（10%）：工具組合與資源快取

---

## Case #14: 修正 MCP csharp-sdk 中文 JSON 編碼相容性

### Problem Statement（問題陳述）
- 業務場景：MCP 回應包含中文 JSON，Claude Desktop 偶發無法解析，需確保跨端相容。
- 技術挑戰：csharp-sdk 預設序列化對中文處理不符客戶端預期，需強制 Unicode escape。
- 影響範圍：中文資料傳輸失敗，整體整合無法實測。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. JSON 編碼未轉為 \uXXXX 形式。
  2. 客戶端對非 ASCII JSON 支援不穩。
  3. SDK 尚未修正（文章時點）。
- 深層原因：
  - 架構層面：跨端編碼約定缺失。
  - 技術層面：序列化選項未客製。
  - 流程層面：缺乏編碼一致性測試。

### Solution Design
- 解決策略：暫時自行 build SDK 或替換 JsonSerializerOptions，將 Encoder 設為僅允許 BasicLatin，使非 ASCII 以 \uXXXX 轉義；待官方修正後回歸。

- 實施步驟：
  1. 客製序列化選項
  - 實作細節：Encoder=JavaScriptEncoder.Create(UnicodeRanges.BasicLatin)
  - 所需資源：System.Text.Encodings.Web
  - 預估時間：0.5 天
  2. 回歸測試
  - 實作細節：含中文資料的 tools/call 回應驗證
  - 所需資源：測試用例
  - 預估時間：0.5 天
  3. 追蹤官方修補
  - 實作細節：待 SDK 更新後回退客製
  - 所需資源：版本管理
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var options = new JsonSerializerOptions{
  Encoder = JavaScriptEncoder.Create(UnicodeRanges.BasicLatin) // 非 Latin 將被 \uXXXX 轉義
};
```

- 實際案例：Day 7（作者回報 issue 並暫解）
- 實作環境：MCP csharp-sdk + Claude Desktop
- 實測數據：
  - 改善前：中文 JSON 偶發無法處理
  - 改善後：以 \uXXXX 表示可穩定解析
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：JSON 編碼/轉義與跨端相容
  - 技能要求：.NET 序列化客製
  - 延伸思考：是否需內容壓縮/簽章？

- Practice Exercise
  - 基礎：將含中文的物件序列化為 \uXXXX（30 分）
  - 進階：為 MCP 回應管線加入統一 Encoder（2 小時）
  - 專案：端到端中文相容測試套件（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：中文資料可通
  - 程式碼品質（30%）：封裝 Encoder 與注入
  - 效能優化（20%）：序列化成本可控
  - 創新性（10%）：多語支援策略

---

## Case #15: 回退 MSKM 版本以避開中文 chunking「晶晶體」Bug

### Problem Statement（問題陳述）
- 業務場景：MSKM 新版本（2025/02 附近）重寫 chunking，中文出現疊字「晶晶體」現象，影響檢索品質。
- 技術挑戰：需快速恢復可用環境並等待官方修復。
- 影響範圍：中文內容品質下降、引用錯誤。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 以 token 斷句的 chunking 新實作未妥善處理中文。
  2. 版本更新缺少中文測試覆蓋。
- 深層原因：
  - 架構層面：語言特性未納入 chunking 設計考量。
  - 技術層面：tokenizer/segmenter 選擇不當。
  - 流程層面：多語回歸測試缺失。

### Solution Design
- 解決策略：臨時回退到 0.96.x 版本維持穩定；持續追蹤官方 issue 與修復進度。

- 實施步驟：
  1. 鎖定版本
  - 實作細節：Docker image 指定 0.96.x
  - 所需資源：部署管線
  - 預估時間：0.5 天
  2. 驗證匯入
  - 實作細節：抽樣檢查中文內容品質
  - 所需資源：測試集
  - 預估時間：0.5 天
  3. 後續升級策略
  - 實作細節：待官方修復後灰度上線
  - 所需資源：版本管理
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```bash
# 指定拉舊版 image（實際 image 名稱以官方為準）
docker pull kernelmemory:0.96.x
docker run -p 8000:8000 kernelmemory:0.96.x
```

- 實際案例：Day 7（作者提醒回退版本）
- 實作環境：MSKM Docker
- 實測數據：
  - 改善前：中文疊字
  - 改善後：恢復正常
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：版本治理與回退策略
  - 技能要求：Docker/DevOps
  - 延伸思考：如何建立多語自動化回歸測試？

- Practice Exercise
  - 基礎：回退並驗證一段中文匯入（30 分）
  - 進階：建立多語煙囪測試腳本（2 小時）
  - 專案：版本灰度發布與監控（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：能回退並穩定運行
  - 程式碼品質（30%）：部署腳本清晰
  - 效能優化（20%）：回退切換時間
  - 創新性（10%）：驗證自動化

---

## Case #16: 在不支援 Function Calling 的模型上「土炮」實作工具調用

### Problem Statement（問題陳述）
- 業務場景：希望使用 DeepSeek r1 等未支援 FC 的模型實現工具調用，探索替代方式。
- 技術挑戰：無 tools/parameters 機制，需用純文字約定驅動程式攔截。
- 影響範圍：若約定不穩，可能誤觸或混淆。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 模型不支援 tool use。
  2. 缺乏標準工具管道。
  3. 對話規約未定義。
- 深層原因：
  - 架構層面：功能依賴模型能力。
  - 技術層面：需以約定代替協定。
  - 流程層面：需嚴格測試避免誤判。

### Solution Design
- 解決策略：在 system prompt 自定雙角色標記（例如「安德魯大人您好」=回覆用戶、「請執行指令」=給秘書/工具）；應用程式攔截「請執行指令」開頭訊息，執行並把結果再餵回模型，循環至最終回答。

- 實施步驟：
  1. 設計對話規約
  - 實作細節：兩種前綴詞與格式
  - 所需資源：Prompt 模板
  - 預估時間：0.5 天
  2. 攔截與執行
  - 實作細節：程式檢測前綴，分流給工具
  - 所需資源：後端程式
  - 預估時間：0.5 天
  3. 測試與防呆
  - 實作細節：避免誤判，加入校驗碼
  - 所需資源：測試集
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```text
System Prompt 範例（節錄）：
- 若回覆使用者，請以「安德魯大人您好」開頭。
- 若要請秘書執行指令，請以「請執行指令」開頭，並附上 JSON 參數。

App 偵測：
if (msg.StartsWith("請執行指令")) { ExecuteTool(...); } else { ShowToUser(...); }
```

- 實際案例：Day 8（土炮 Function Calling）
- 實作環境：任一 ChatCompletion 相容模型；應用程式攔截器
- 實測數據：
  - 改善前：不可使用工具
  - 改善後：可藉由約定達到類 FC 的行為
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：協定 vs 約定；循環驅動
  - 技能要求：Prompt 規約、字串攔截
  - 延伸思考：正式環境仍建議使用支援 FC 的模型與框架

- Practice Exercise
  - 基礎：用前綴詞觸發一個假工具（30 分）
  - 進階：加入 JSON 參數與結果回填（2 小時）
  - 專案：做一個簡易排程助理（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：可呼叫與回填
  - 程式碼品質（30%）：攔截與解析穩定
  - 效能優化（20%）：循環回合控制
  - 創新性（10%）：防呆與校驗

---

## Case #17: 完整傳遞 tool/tool-result 訊息防止決策中斷

### Problem Statement（問題陳述）
- 業務場景：多輪工具流程常因未帶齊 tool/tool-result 訊息導致模型遺失上下文或無法判定下一步。
- 技術挑戰：每次呼叫都需帶上從 0 開始的完整歷史（含 tool 與 result）。
- 影響範圍：決策中斷、無效迴圈、誤用工具。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 僅帶 user/assistant，不帶 tool/result。
  2. 回合間丟失關鍵上下文。
  3. 未抽象對話歷程管理。
- 深層原因：
  - 架構層面：缺少對話記錄儲存設計。
  - 技術層面：不熟 message schema。
  - 流程層面：測試場景覆蓋不足。

### Solution Design
- 解決策略：制定訊息儲存規約；每輪都將最新 tool_calls 與 tool-result 追加至 messages 並回送模型；以「直到 assistant 給出最終回覆」為終止條件。

- 實施步驟：
  1. 擴充 ConversationStore
  - 實作細節：支援 tool 與 tool-result 角色與序號
  - 所需資源：儲存層
  - 預估時間：0.5 天
  2. 建立推進函式
  - 實作細節：回應中檢測 tool_calls -> 執行 -> 追加 result -> 再呼叫
  - 所需資源：client/adaptor
  - 預估時間：0.5 天
  3. 測試與保證
  - 實作細節：確保可重放與一致性
  - 所需資源：自動測試
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```json
"messages":[
  {"role":"system","content":"...tools spec..."},
  {"role":"user","content":"find a 30 min slot..."},
  {"role":"assistant","tool_calls":[{"name":"check_schedules","args":{...}}]},
  {"role":"tool","content":"[...]","name":"check_schedules"},
  {"role":"assistant","tool_calls":[{"name":"add_event","args":{...}}]},
  {"role":"tool","content":"[\"success\"]","name":"add_event"}
]
```

- 實際案例：Day 3（完整對話歷程）
- 實作環境：OpenAI ChatCompletion + 任一框架
- 實測數據：
  - 改善前：遺失上下文導致中斷
  - 改善後：可穩定走完任務
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：全歷程回放的重要性
  - 技能要求：訊息序列管理
  - 延伸思考：如何壓縮歷史以控 token？

- Practice Exercise
  - 基礎：把一輪 tool/result 補回 messages（30 分）
  - 進階：寫一個「直到完成」的驅動 loop（2 小時）
  - 專案：封裝通用對話驅動器（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：可重放且完成
  - 程式碼品質（30%）：封裝得宜
  - 效能優化（20%）：歷史壓縮策略
  - 創新性（10%）：歷史摘要化

---

## Case #18: MSKM 部署模式抉擇：服務化 vs 嵌入式

### Problem Statement（問題陳述）
- 業務場景：需在不同規模（本地內嵌/雲端服務）下運行 RAG，如何選擇 MSKM 運行模式。
- 技術挑戰：在擴展性、延遲、運維成本間取得平衡；避免 localhost-HTTP 的折衷方案。
- 影響範圍：影響開發效率、部署複雜度與成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 忽略服務化帶來的擴展與治理優勢。
  2. 小型場景又不想引入外部依賴。
  3. 不清楚 MSKM 既可服務化也可內嵌。
- 深層原因：
  - 架構層面：未做容量與延遲評估。
  - 技術層面：對兩種模式的優缺點不熟悉。
  - 流程層面：Dev/Prod 治理策略未制定。

### Solution Design
- 解決策略：小規模/離線測試採用嵌入式（同進程）；正式環境採用服務化（Docker/K8s）；以相同 SDK 抽象呼叫，降低切換成本。

- 實施步驟：
  1. 定義場景
  - 實作細節：根據 QPS、資料量、整合對象評估
  - 所需資源：測試報告
  - 預估時間：0.5 天
  2. 兩套樣板
  - 實作細節：Service 與 Embedded 啟動腳本/程式
  - 所需資源：模板專案
  - 預估時間：1 天
  3. 切換策略
  - 実作細節：以設定檔切換 BaseUrl/內嵌實例
  - 所需資源：設定管理
  - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Service 模式
var client = new KernelMemoryClient(baseUrl: "http://mskm:8000");

// Embedded 模式（示意）
var mskm = new KernelMemoryEmbedded(options);
```

- 實際案例：Day 5（兩種應用方式示意）
- 實作環境：MSKM（Service/Embedded）、.NET
- 實測數據：
  - 改善前：單一路徑無法適應不同規模
  - 改善後：可按場景切換
  - 改善幅度：定性改善（未量化）

- Learning Points
  - 核心知識點：部署拓撲與取捨
  - 技能要求：雲原生基礎、.NET 嵌入
  - 延伸思考：如何做藍綠/灰度與回退（見 Case #15）？

- Practice Exercise
  - 基礎：同專案支援兩模式切換（30 分）
  - 進階：K8s 部署 Service 模式（2 小時）
  - 專案：生產級 RAG 服務治理方案（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：兩模式皆可運行
  - 程式碼品質（30%）：抽象與設定清楚
  - 效能優化（20%）：延遲/QPS 測量
  - 創新性（10%）：自動化切換


========================
案例分類
========================

1) 按難度分類
- 入門級（適合初學者）
  - Case 1（Chat Completion 基礎循環）
  - Case 2（JSON Mode 擷取地址）
  - Case 3（單一職責降成本）
  - Case 4（Function Calling 基礎）
- 中級（需要一定基礎）
  - Case 6（用框架簡化多工具）
  - Case 7（以 FC 觸發 RAG）
  - Case 10（Embedding/Chunk 對齊）
  - Case 11（PDF/OCR Handler）
  - Case 12（多插件組合）
  - Case 17（tool/tool-result 完整傳遞）
  - Case 18（MSKM 部署抉擇）
- 高級（需要深厚經驗）
  - Case 5（Sequential FC 排程）
  - Case 8（MSKM 作為服務）
  - Case 9（生成檢索專用內容）
  - Case 13（MCP 整合 Claude Desktop）
  - Case 14（MCP 中文編碼修正）
  - Case 15（版本回退與中文 bug）

2) 按技術領域分類
- 架構設計類
  - Case 3, 6, 8, 9, 18
- 效能優化類
  - Case 3, 10, 17
- 整合開發類
  - Case 6, 7, 11, 12, 13, 18
- 除錯診斷類
  - Case 14, 15, 17
- 安全防護類
  -（本篇未直接聚焦安全，可在工具治理與部署時延伸：Case 6, 18）

3) 按學習目標分類
- 概念理解型
  - Case 1, 2, 4, 7, 10
- 技能練習型
  - Case 6, 11, 12, 17, 18
- 問題解決型
  - Case 3, 5, 8, 9, 14, 15
- 創新應用型
  - Case 13, 16

========================
案例關聯圖（學習路徑建議）
========================
- 建議先學：
  1) Case 1（Chat Completion 基礎對話循環）
  2) Case 2（JSON Mode/Schema）
  3) Case 4（Function Calling 基礎）
- 依賴關係：
  - Case 5（Sequential FC）依賴 Case 1/4 與 Case 17（完整歷史）
  - Case 7（以 FC 觸發 RAG）依賴 Case 2/4
  - Case 6（用框架簡化）建立於 Case 4/5/7 之上
  - Case 8（MSKM 服務）可獨立，但與 Case 6/7 結合最佳
  - Case 9（生成檢索資訊）強依賴 Case 8
  - Case 10（Chunk/Embedding）與 Case 8/9 同步優化
  - Case 11（Handler）串接於 Case 8 管線
  - Case 12（多插件）建立於 Case 6/7
  - Case 13（MCP）可在 Case 8 打底後整合
  - Case 14/15 屬運維/除錯，與 Case 13/8 分別耦合
  - Case 16（土炮 FC）可在 Case 4 理解後作為替代方案
  - Case 18（部署抉擇）貫穿 Case 8/9/11/13

- 完整學習路徑建議：
  - 基礎層：Case 1 → 2 → 4 → 17（建立對話與工具基礎與歷史處理）
  - 進階層：Case 5 → 6 → 7 → 12（多工具規劃與以工具觸發 RAG）
  - RAG 層：Case 8 → 10 → 11 → 9（搭建 MSKM，優化 chunk/embedding，處理多媒體，最後用生成式方法提升檢索）
  - 整合層：Case 18（部署策略）→ Case 13（MCP 整合）
  - 運維/除錯層：Case 14（編碼）→ Case 15（版本回退）
  - 特殊技巧：Case 16（在不支援 FC 的模型上土炮）作為補充

說明
- 本整理完整對齊文章的示例與觀念，實測數據部分文章多為定性描述，未提供量化數字，故以定性改善註記。所有實作細節與 demo 來源均對應文中 Day 0~8 說明與 GitHub 連結所示範例。