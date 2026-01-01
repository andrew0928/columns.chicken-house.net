---
layout: synthesis
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"
synthesis_type: solution
source_post: /2025/06/22/inside-semantic-kernel/
redirect_from:
  - /2025/06/22/inside-semantic-kernel/solution/
postid: 2025-06-22-inside-semantic-kernel
---
{% raw %}
以下為從文章中整理出的 18 個可教學、可實作、可評估的問題解決案例。每個案例皆包含問題、根因、解法設計、關鍵程式碼、實測指標與練習與評估標準。案例內容以文中 Demo、敘述與設計觀點為基礎彙整與結構化。

## Case #1: 建立 Chat Completion 基準型（Role/Context 正確使用）

### Problem Statement（問題陳述）
業務場景：團隊要在 .NET 內快速落地一個具備對話記憶與連續互動的 AI Chat 功能，支援從 HttpClient、OpenAI .NET SDK 到 Semantic Kernel（SK）的多種存取方式。需求是能穩定管理訊息角色（system/user/assistant）與上下文（context window），並形成可重複、易維護的呼叫模式。
技術挑戰：如何正確建構 Chat Completion 請求並管理對話歷史，使每次回應都能基於完整上下文且角色分明。
影響範圍：若上下文或角色錯誤，回應易漂移、錯誤率上升、不可控；影響所有後續進階功能（Function Calling/RAG）。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 對 messages 角色理解不足（system/user/assistant），導致 prompt 混淆。
2. 未妥善保存對話歷史，造成上下文遺失。
3. 請求參數（model/temperature）未合理設定，導致隨機性不控。
深層原因：
- 架構層面：缺少對話層的統一封裝與策略管理。
- 技術層面：未建立標準的 API 呼叫介面、DTO 與序列化策略。
- 流程層面：對話記錄與錯誤處理沒有一致流程（如重試與審計）。

### Solution Design（解決方案設計）
解決策略：建立 Chat Completion 基礎模板，統一角色與上下文管理；在 .NET 內抽象化呼叫層，支援 HttpClient、SDK、SK 三種模式，並提供一致的訊息保存與序列化策略。

實施步驟：
1. 統一請求抽象層
- 實作細節：定義 ChatRequest DTO、Message 結構、角色枚舉。
- 所需資源：OpenAI API、.NET、HttpClient 或 OpenAI .NET SDK。
- 預估時間：0.5 天
2. 對話歷史管理
- 實作細節：所有對話回合追加到 messages；確保 system prompt 置頂。
- 所需資源：記憶體或持久化存儲（DB）。
- 預估時間：0.5 天
3. 容錯與回應策略
- 實作細節：設定合理 temperature；加入重試與審計日誌。
- 所需資源：Polly（重試）、Logger。
- 預估時間：0.5 天

關鍵程式碼/設定：
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
```
Implementation Example（實作範例）

實際案例：Simple Chat（HttpClient / OpenAI .NET SDK / SK 三版本）
實作環境：.NET、OpenAI ChatCompletion API、gpt-4o-mini
實測數據：
改善前：無上下文統一規範，回應不穩定
改善後：統一角色與歷史管理，回應一致性提升
改善幅度：回應穩定性顯著提升（以人工驗證一致性為指標）

Learning Points（學習要點）
核心知識點：
- Chat Completion 的 roles 與上下文管理
- temperature 對隨機性的影響
- 抽象呼叫層的重要性
技能要求：
必備技能：HttpClient、JSON 序列化、.NET
進階技能：SDK 封裝、SK Kernel 管理
延伸思考：
- 可加入訊息審計與安全過濾
- 將對話歷史持久化，便於長期分析
- 引入多模型路由，提高穩定性

Practice Exercise（練習題）
基礎練習：以 HttpClient 完成一次對話（30 分鐘）
進階練習：以 OpenAI .NET SDK 重新封裝呼叫（2 小時）
專案練習：以 SK 建立可插拔的 Chat 模組（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：角色與歷史管理是否正確
程式碼品質（30%）：抽象層設計與可維護性
效能優化（20%）：呼叫延遲與重試策略
創新性（10%）：多模型路由與擴充性

---

## Case #2: 結構化輸出（JSON Mode + Schema）抽取地址

### Problem Statement（問題陳述）
業務場景：在應用程式中從大量對話文本抽取地址資訊（street/city/postal/country），需可直接反序列化為 C# 物件並判斷是否成功抽取，以便後續交給非 AI 程式碼進行地圖 API 或計算。
技術挑戰：LLM 輸出自由文本難以解析；需要明確成功/失敗標記與固定結構。
影響範圍：資料管道與下游系統（地圖 API）穩定性，錯誤解析會造成大量例外與不一致。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未使用 JSON Mode 或 Schema，輸出不可預期。
2. 無明確成功/失敗標記，程式端需猜測。
3. 混合多職責在一個 prompt，增加不確定性。
深層原因：
- 架構層面：AI 輸出缺乏合約（Contract）。
- 技術層面：缺乏標準序列化/反序列化設計。
- 流程層面：缺少輸出驗證與失敗分支處理。

### Solution Design（解決方案設計）
解決策略：導入 JSON Mode 與 Schema；在輸出中加入明確 success 欄位；單一職責只做抽取，後續資訊由程式碼處理。

實施步驟：
1. 定義 JSON Schema 與 DTO
- 實作細節：schema 包含 street_address/city/postal_code/country + success/notes。
- 所需資源：OpenAI JSON Mode、C# DTO。
- 預估時間：0.5 天
2. 設定 response_format 與驗證
- 實作細節：指定 json_schema 或 json_object；反序列化後檢查 success。
- 所需資源：OpenAI API；Json.NET。
- 預估時間：0.5 天
3. 分離職責
- 實作細節：抽取地址後，呼叫 Google Maps API 在程式端完成。
- 所需資源：地圖 API。
- 預估時間：0.5 天

關鍵程式碼/設定：
```http
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer {{OpenAI_APIKEY}}
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "response_format": { "type": "json_object" },
  "messages": [
    { "role": "system", "content": "Extract address into JSON. Include 'success': true|false." },
    { "role": "user", "content": "For the tea shop in Paris... number? 90, I guess." }
  ],
  "temperature": 0
}
```
Implementation Example（實作範例）

實際案例：Structured Output（HTTP/SDK/SK 版本）
實作環境：.NET、OpenAI、gpt-4o-mini
實測數據：
改善前：自由文本解析困難，錯誤率高
改善後：可直接反序列化，並以 success 欄位判斷是否抽取
改善幅度：可用性與自動化顯著提升（以解析成功率為指標）

Learning Points（學習要點）
核心知識點：
- JSON Mode 與 Schema 合約意識
- 單一職責與非 AI 環節分離
- 失敗明確標示策略
技能要求：
必備技能：Schema 設計、序列化
進階技能：錯誤分支控制、外部 API 整合
延伸思考：
- 引入 schema 版本控管
- 加入正規化/地理編碼後處理
- 以測試集建立抽取精度基準

Practice Exercise（練習題）
基礎練習：定義地址 DTO 與 JSON Mode 呼叫（30 分鐘）
進階練習：加入 success/notes 驗證管道（2 小時）
專案練習：串接地圖與地理編碼完整流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：抽取、判斷、後續整合
程式碼品質（30%）：DTO/Schema/模組化
效能優化（20%）：呼叫延遲與重試策略
創新性（10%）：失敗回復與建議策略

---

## Case #3: Function Calling（Basic）將自然語言轉為清單指令

### Problem Statement（問題陳述）
業務場景：讓使用者以自然語言維護購物清單（新增/刪除/數量），系統需將對話意圖轉換成動作序列，並在程式端執行，完成清單維護。
技術挑戰：將語意可靠地映射為可執行的 JSON 指令（action/item/quantity），避免自由文本。
影響範圍：若意圖解析不準確，清單維護會錯誤，破壞使用體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少明確工具/指令規格（動作約束）。
2. 意圖對齊困難，語句不一致。
3. 驗證與執行順序處理不足。
深層原因：
- 架構層面：工具定義與對話規約未形成。
- 技術層面：缺少動作模型與序列執行器。
- 流程層面：無執行結果回饋（成功/失敗/衝突）。

### Solution Design（解決方案設計）
解決策略：在 system prompt 定義動作格式；LLM 回傳 JSON 指令集；程式端執行，形成閉環的 Function Calling 基礎流程。

實施步驟：
1. 定義動作與輸出格式
- 實作細節：add/delete；item/quantity；使用 JSON 格式。
- 所需資源：OpenAI；Schema/DTO。
- 預估時間：0.5 天
2. 實作執行器
- 實作細節：解析 JSON 指令並依序執行；加入衝突檢查。
- 所需資源：C# 執行器模組。
- 預估時間：0.5 天
3. 執行回饋與審計
- 實作細節：為每步動作記錄結果；回覆成功與失敗。
- 所需資源：Logger；簡易存儲。
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
[
  { "action": "add", "item": "butter", "quantity": "1" },
  { "action": "add", "item": "zucchinis", "quantity": "2" },
  { "action": "delete", "item": "bread" }
]
```
Implementation Example（實作範例）

實際案例：Shopping List（Function Calling Basic 對話）
實作環境：OpenAI ChatCompletion；JSON Mode；.NET
實測數據：
改善前：自由文本 → 難以執行
改善後：動作 JSON → 可直接執行
改善幅度：自動化與正確性顯著提升

Learning Points（學習要點）
核心知識點：
- 指令集與語意映射
- 序列執行器與回饋
- Function Calling 基礎閉環
技能要求：
必備技能：JSON 處理、清單邏輯
進階技能：衝突檢查與審計
延伸思考：
- 加入單位/價格等擴充
- 引入多語系意圖映射
- 工具集版本化管理

Practice Exercise（練習題）
基礎練習：定義 add/delete 格式並解析（30 分鐘）
進階練習：加入衝突與錯誤回覆（2 小時）
專案練習：清單管理 API 與前端整合（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：動作解析與執行閉環
程式碼品質（30%）：模組化與測試
效能優化（20%）：序列執行與重試
創新性（10%）：擴充性與回饋設計

---

## Case #4: Function Calling（Sequential）行程預約：查再寫的連續工具使用

### Problem Statement（問題陳述）
業務場景：幫使用者預約明天早上的 30 分鐘慢跑，需先查空檔（check_schedules）再新增活動（add_event），並回覆成功訊息。
技術挑戰：LLM 必須能在對話中觸發工具、消化工具回傳、做出下一步決策，直到任務完成。
影響範圍：若未處理工具結果與順序依賴，容易錯誤預約或重複執行。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 只完成「呼叫」未完成「回傳」與結果消化。
2. 工具與對話的三方溝通未被清楚建模。
3. 未妥善追加 tool-result 到歷史，導致上下文斷裂。
深層原因：
- 架構層面：缺少工具回合控制器（Tool Orchestrator）。
- 技術層面：未處理 tool_calls 與 tool-result 的正確序列。
- 流程層面：無成功/失敗的閉環與用戶回覆規範。

### Solution Design（解決方案設計）
解決策略：在 Chat Completion 內形成工具回合閉環：assistant → tool_calls → app 執行 → tool-result → assistant 決策，直到成功回覆。

實施步驟：
1. 定義工具列表
- 實作細節：tools: ["check_schedules", "add_event"]。
- 所需資源：SK Plugins 或自訂工具 API。
- 預估時間：0.5 天
2. 工具執行與回覆
- 實作細節：攔截 tool_calls，執行後追加 tool-result。
- 所需資源：工具執行器、SDK/Http。
- 預估時間：1 天
3. 任務完成回覆
- 實作細節：assistant 最終彙整為用戶可讀訊息。
- 所需資源：回覆模板與審計。
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
// 節錄對話輪廓（簡化）
1. system: tools: [ "check_schedules", "add_event" ]
2. user: find a 30 min slot for a run tomorrow morning
3. assistant: tool_calls: check_schedules(06:00-12:00)
4. tool-result: ["07:00-08:00...", "08:00-09:00...", "10:00-12:00..."]
5. assistant: tool_calls: add_event(09:00-09:30)
6. tool-result: ["success"]
7. assistant: "Morning run scheduled for tomorrow at 9am!"
```
Implementation Example（實作範例）

實際案例：Schedule Event Assistant（HTTP/SK）
實作環境：.NET、Semantic Kernel、OpenAI ChatCompletion
實測數據：
改善前：無工具回合閉環，容易中斷或誤操作
改善後：完整連續工具使用與成功回覆
改善幅度：任務完成率與正確性顯著提升

Learning Points（學習要點）
核心知識點：
- tool_calls / tool-result 對話序列
- 工具回合閉環控制
- 任務完成的彙整策略
技能要求：
必備技能：API 呼叫、序列控制
進階技能：SK 工具編排、狀態機
延伸思考：
- 加入行程衝突與提醒
- 增加取消/修改功能
- 引入規則與安全檢查

Practice Exercise（練習題）
基礎練習：實作 check_schedules 工具（30 分鐘）
進階練習：加入 add_event 與閉環回覆（2 小時）
專案練習：完整行程助理（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：查→寫→回覆
程式碼品質（30%）：工具編排與測試
效能優化（20%）：呼叫次數與延遲
創新性（10%）：多工具策略與提示工程

---

## Case #5: 以 Function Calling 觸發 RAG（搜尋引擎/外部資料）

### Problem Statement（問題陳述）
業務場景：回答需依賴最新的外部資訊（景點、天氣、位置），LLM 訓練知識落後，須在對話中自動觸發搜尋與檢索，並產生含來源的回覆。
技術挑戰：設計能讓 LLM 自主決定是否搜索，並生成正確查詢參數（query/limit/tags）。
影響範圍：無檢索會導致幻覺；無引用來源降低可信度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 只靠模型內知識，無法回應最新狀況。
2. 無檢索工具，無法產生查詢條件。
3. 無引用來源，缺乏可驗證性。
深層原因：
- 架構層面：未形成檢索增強生成（RAG）管道。
- 技術層面：缺乏工具定義與參數抽取。
- 流程層面：回答無附帶來源，缺少治理。

### Solution Design（解決方案設計）
解決策略：在 system prompt 說明任務與引用要求，注入 search/bing 等工具；用 JSON Mode 讓 LLM 生成查詢參數；回覆需包含來源連結。

實施步驟：
1. 定義檢索工具與參數模式
- 實作細節：search(query, limit, tags...)，並要求引用來源。
- 所需資源：Bing API、SK 插件。
- 預估時間：1 天
2. 對話策略與回覆規範
- 實作細節：當需要外部資訊時觸發 search；回覆包含 URL。
- 所需資源：Prompt 模板。
- 預估時間：0.5 天
3. 整合管道與審計
- 實作細節：記錄每次搜尋結果與引用。
- 所需資源：Logger、資料存儲。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// SK 伪代码：挂載 Bing Search
var kernel = Kernel.Create();
kernel.Plugins.Add(new BingSearchPlugin(apiKey));
var answer = await kernel.InvokeAsync("search", new { query = "city attractions", limit = 5 });
```
Implementation Example（實作範例）

實際案例：RAG with Bing Search
實作環境：.NET、Semantic Kernel、Bing Search API
實測數據：
改善前：回覆常過時或幻覺
改善後：可用最新檢索並附來源
改善幅度：可信度顯著提升（引用比例作為指標）

Learning Points（學習要點）
核心知識點：
- RAG 的觸發機制（Function Calling）
- 查詢參數與 JSON Mode
- 引用治理
技能要求：
必備技能：SK 插件、外部 API
進階技能：查詢策略與可觀測性
延伸思考：
- 根據場景改用自家知識庫
- 加入來源可靠度評分
- 設計查詢降級策略

Practice Exercise（練習題）
基礎練習：以 SK 呼叫搜尋工具（30 分鐘）
進階練習：生成查詢參數並引用來源（2 小時）
專案練習：多工具編排的旅遊建議助理（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：觸發搜尋與引用
程式碼品質（30%）：插件整合與測試
效能優化（20%）：查詢延遲與結果整合
創新性（10%）：查詢策略與來源評分

---

## Case #6: RAG with Kernel Memory Plugins（MSKM 即插即用）

### Problem Statement（問題陳述）
業務場景：將企業或部落格知識庫暴露為 RAG 服務，讓前端 Chat/Agent 直接查詢 MSKM 的內容並生成回答。
技術挑戰：需要一套支援大規模 ingestion、檢索、引用的獨立服務，並能被 SK 當工具使用。
影響範圍：知識檢索可用性、整合便利性、維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. SK Memory 僅涵蓋 Vector Store CRUD 與相似搜尋，不含完整 ingestion pipeline。
2. 自建 RAG 管線成本高且易踩坑。
3. 無統一工具集與框架整合。
深層原因：
- 架構層面：長期記憶（long-term memory）未獨立服務化。
- 技術層面：文件抽取/分段/向量化/存儲缺少標準管線。
- 流程層面：檢索治理（tags/來源/引用）未內建。

### Solution Design（解決方案設計）
解決策略：採用 MSKM 作為 RAG 服務，透過其 NuGet 與 SK Plugin 將 MSKM 能力加入工具箱；前端只需直接調用。

實施步驟：
1. 部署 MSKM
- 實作細節：Docker 啟動或嵌入服務；配置 AI connector。
- 所需資源：MSKM Docker/NuGet；OpenAI/Azure OpenAI 等。
- 預估時間：0.5-1 天
2. 掛載 SK 的 Memory Plugin
- 實作細節：在 SK 中加入 MSKM Plugin；暴露檢索功能。
- 所需資源：Semantic Kernel。
- 預估時間：0.5 天
3. 前端 Chat/Agent 整合
- 實作細節：RAG query → MSKM → 生成回答（含引用）。
- 所需資源：Chat 應用。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// SK 掛載 MSKM Plugin（伪代码）
var kernel = Kernel.Create();
kernel.Plugins.Add(new KernelMemoryPlugin(mskmClient)); // 提供 search/lookup 等工具
```
Implementation Example（實作範例）

實際案例：RAG with Kernel Memory Plugins（官方/自訂插件）
實作環境：.NET、MSKM、SK
實測數據：
改善前：自行打造管線耗時且不完整
改善後：服務化 + 插件化，快速整合
改善幅度：開發效率與穩定性顯著提升

Learning Points（學習要點）
核心知識點：
- 長期記憶服務化
- SK 插件與工具暴露
- 連接器與相容性
技能要求：
必備技能：Docker/SDK
進階技能：SK 插件開發與治理
延伸思考：
- 權限控制與分域索引
- MSKM 與監控/告警整合
- 檢索策略與引用模板

Practice Exercise（練習題）
基礎練習：啟動 MSKM 並用 SK 搜索（30 分鐘）
進階練習：自訂 MSKM 插件並加標籤（2 小時）
專案練習：企業知識庫 RAG 服務（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：RAG 搜索與引用
程式碼品質（30%）：插件封裝與測試
效能優化（20%）：索引/查詢性能
創新性（10%）：治理與可觀測性

---

## Case #7: MSKM 部署選型：Web Service 與嵌入式（Serverless）

### Problem Statement（問題陳述）
業務場景：不同規模下選擇合適的 MSKM 部署方式：以 Web Service 供多方使用，或直接嵌入應用程式（非 localhost HTTP），滿足不同維運與擴展需求。
技術挑戰：兼顧擴展性、維護成本與開發效率；確保管線可運作。
影響範圍：部署架構、維運流程、資源成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一部署模式無法覆蓋所有場景。
2. 自建服務缺乏標準化；嵌入式易失去跨系統可用性。
3. 未考慮長任務處理與管線治理。
深層原因：
- 架構層面：RAG 管線服務化設計未被納入。
- 技術層面：Connector 與管線元件配置複雜。
- 流程層面：維運策略（版本、回滾、監控）未成體系。

### Solution Design（解決方案設計）
解決策略：提供兩種標準部署模式（Service/Embedded）；以 Docker 快速起服或 NuGet 嵌入；建立版本與監控策略。

實施步驟：
1. Web Service 部署
- 實作細節：拉取 Docker image；配置 AI 連接器。
- 所需資源：Docker、MSKM image。
- 預估時間：0.5 天
2. 嵌入式部署
- 實作細節：NuGet 內嵌；不走 HTTP；直接調用核心。
- 所需資源：MSKM NuGet。
- 預估時間：0.5 天
3. 版本與監控
- 實作細節：版本 pin、健康檢查、日誌與告警。
- 所需資源：監控平台。
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# Docker 啟動（示意）
docker run -d --name mskm -p 8080:8080 mskm:latest
```
Implementation Example（實作範例）

實際案例：MSKM 作為 Web Service 與嵌入式
實作環境：Docker/.NET/MSKM
實測數據：
改善前：部署方式不一致，維運困難
改善後：兩種模式可選；快速起服與嵌入
改善幅度：維運效率與穩定性提升

Learning Points（學習要點）
核心知識點：
- 服務 vs 嵌入式選型
- Connector 配置與維運
- 版本與監控治理
技能要求：
必備技能：Docker、NuGet
進階技能：監控、版本策略
延伸思考：
- 多租戶與隔離
- Serverless 成本治理
- 可靠性工程（SLO/SLI）

Practice Exercise（練習題）
基礎練習：以 Docker 起一個 MSKM（30 分鐘）
進階練習：以 NuGet 嵌入應用（2 小時）
專案練習：建立監控與版本策略（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：兩種模式可用
程式碼品質（30%）：配置與封裝
效能優化（20%）：資源使用與延遲
創新性（10%）：治理策略

---

## Case #8: 長文檢索精度不佳：以合成檢索資訊提升（摘要/FAQ/PSR）

### Problem Statement（問題陳述）
業務場景：部落格長文（50k~100k chars、單篇 100+ chunks）以基本 chunking+embedding 檢索時，對偏抽象問題（如「WSL 能幹嘛？」）常取不到對的段落；需要提升語意對齊。
技術挑戰：查詢視角與內容視角不一致；單純相似度難組合正確答案。
影響範圍：檢索品質、用戶體驗、生成答案可信度。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 長文缺少高層次摘要，檢索落在細節段落。
2. 使用者以問題視角查詢，與作者內容視角不一致。
3. 向量檢索資訊密度不對齊（chunk 太多、語義分散）。
深層原因：
- 架構層面：RAG 管線缺少語意增益（semantic synthesis）。
- 技術層面：未生成適合檢索的高階結構（摘要/FAQ/PSR）。
- 流程層面：標籤與分域策略缺失。

### Solution Design（解決方案設計）
解決策略：在 ingestion 前用 LLM 生成檢索專用內容：全文摘要、段落摘要（paragraph abstract）、FAQ（Q/A）、問題/根因/解法（PSR），加標籤後向量化，再交給 MSKM；前端 RAG 直接查詢這些視角對齊素材。

實施步驟：
1. 合成檢索素材
- 實作細節：使用更強推理模型（如 o1）生成 abstract/FAQ/PSR。
- 所需資源：SK 調用模型；標籤策略。
- 預估時間：1-2 天
2. 標籤與入庫
- 實作細節：為素材加 tags（type:abstract/FAQ/PSR、topic、date 等）。
- 所需資源：MSKM ingestion；vector store。
- 預估時間：1 天
3. 檢索策略與回覆模板
- 實作細節：優先召回摘要/FAQ/PSR，再補原文片段；引用來源。
- 所需資源：查詢管道；回覆合成。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 伪代码：合成摘要/FAQ/PSR 後送入 MSKM
var abstracts = await kernel.InvokeAsync("summarize", new { text = article });
var faqs = await kernel.InvokeAsync("buildFAQ", new { text = article });
var psr = await kernel.InvokeAsync("extractPSR", new { text = article });
// 加 tags 後批量送入 MSKM
await mskmClient.ImportAsync(new[]{ abstracts, faqs, psr }, tags: new[]{ "type:abstract","type:FAQ","type:PSR" });
```
Implementation Example（實作範例）

實際案例：Synthesize Content for RAG（SK→MSKM）
實作環境：.NET、SK、MSKM、OpenAI（o1 用於生成）
實測數據：
改善前：長文檢索易取錯段，回答牛頭不對馬嘴
改善後：視角對齊素材提升召回與精度
改善幅度：檢索相關性顯著提升（以人工審查與命中率為指標）

Learning Points（學習要點）
核心知識點：
- 向量檢索的語意對齊
- 合成素材（abstract/FAQ/PSR）
- 標籤治理
技能要求：
必備技能：Prompt 設計、SK 調用
進階技能：RAG 查詢策略設計
延伸思考：
- 依領域客製視角集合
- 引入多路召回（multi-retriever）
- 指標化精度評估

Practice Exercise（練習題）
基礎練習：為一篇長文生成摘要並入庫（30 分鐘）
進階練習：生成 FAQ/PSR 並設計 tags（2 小時）
專案練習：完整視角對齊 RAG 管線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：合成→入庫→檢索→引用
程式碼品質（30%）：管線封裝與測試
效能優化（20%）：批量處理與入庫性能
創新性（10%）：視角設計與指標化評估

---

## Case #9: MSKM Pipeline 加入 Summarization Handler

### Problem Statement（問題陳述）
業務場景：文章無摘要時，檢索常命中細節段落，缺乏高層次對齊；需要在 MSKM pipeline 內自動生成摘要以提升召回質量。
技術挑戰：在 ingestion 中自動生成摘要後再 chunk/embedding/store。
影響範圍：索引品質與查詢精度，影響整體 RAG 效果。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 原文缺乏摘要，無高階概述用於檢索。
2. 單純 chunking 以長度為主，忽略語義層次。
3. pipeline 缺少合成步驟。
深層原因：
- 架構層面：管線未內建語義增益元件。
- 技術層面：未加 Summarization handler。
- 流程層面：未定義摘要生成與標籤規則。

### Solution Design（解決方案設計）
解決策略：在 MSKM Import pipeline 中啟用 Summarization handler，生成摘要並入庫，標記為摘要類型，供檢索優先召回。

實施步驟：
1. Pipeline 配置
- 實作細節：啟用 Summarization handler；設 handler 次序。
- 所需資源：MSKM pipeline 設定。
- 預估時間：0.5 天
2. 標籤與存儲
- 實作細節：摘要以 "type:abstract" 標記；入庫。
- 所需資源：MSKM 存儲。
- 預估時間：0.5 天
3. 檢索策略更新
- 實作細節：查詢優先命中摘要，提升回答準確性。
- 所需資源：Query pipeline。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 伪代码：MSKM ImportText 使用自訂 pipeline 啟用 Summarization
var pipeline = new Pipeline()
  .Use(new ContentExtraction())
  .Use(new Summarization())
  .Use(new Chunking())
  .Use(new Embedding())
  .Use(new Store());

await mskm.ImportTextAsync(text, pipeline);
```
Implementation Example（實作範例）

實際案例：MSKM 預設管線 + Summarization
實作環境：.NET、MSKM
實測數據：
改善前：無摘要，召回多落在細節段落
改善後：摘要優先召回，回覆更貼題
改善幅度：精度提升（以人工審查為指標）

Learning Points（學習要點）
核心知識點：
- MSKM pipeline 設計
- Summarization 的召回價值
- 檢索策略的重要性
技能要求：
必備技能：MSKM 配置
進階技能：管線調優
延伸思考：
- 自訂多種摘要形態（標題摘要、段落摘要）
- 階層化檢索策略（HNSW + reranker）
- 加入引用治理

Practice Exercise（練習題）
基礎練習：在 pipeline 中加入 Summarization（30 分鐘）
進階練習：標籤與檢索策略調整（2 小時）
專案練習：多層摘要與檢索（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：管線合成與檢索
程式碼品質（30%）：設定封裝與測試
效能優化（20%）：管線吞吐
創新性（10%）：摘要策略

---

## Case #10: 多插件協作（位置/天氣/搜尋）旅遊建議

### Problem Statement（問題陳述）
業務場景：使用者詢問「我現在這邊有什麼景點？出門前要準備什麼？」需綜合位置、天氣、搜尋結果，給出建議並提醒。
技術挑戰：LLM 必須在多插件間規劃順序（先取得位置→查天氣→搜尋景點→合成回覆）。
影響範圍：回覆完整性與實用性；多工具協作可靠性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單工具無法滿足多面向資訊。
2. 無編排策略，工具呼叫易混亂。
3. 無回覆模板，資訊散亂。
深層原因：
- 架構層面：缺少工具編排與狀態管理。
- 技術層面：多插件輸入/輸出格式不一致。
- 流程層面：無引用與提醒規範。

### Solution Design（解決方案設計）
解決策略：以 SK 掛載多插件（Location/Weather/Search），在 system prompt 中指示工具使用策略；合成回覆時引用來源並給出提醒。

實施步驟：
1. 插件掛載
- 實作細節：SK 掛 Location/Weather/BingSearch。
- 所需資源：各 API。
- 預估時間：1 天
2. 使用策略與回覆模板
- 實作細節：先位置→天氣→搜尋→合成；引用 URL；提醒攜帶物品。
- 所需資源：Prompt 模板。
- 預估時間：0.5 天
3. 編排與審計
- 實作細節：記錄工具呼叫次序與結果。
- 所需資源：Logger。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 伪代码：多插件協作
kernel.Plugins.Add(new LocationPlugin());
kernel.Plugins.Add(new WeatherPlugin(apiKey));
kernel.Plugins.Add(new BingSearchPlugin(apiKey));
var result = await kernel.InvokeAsync("travelAdvisor", new { ask = "what to visit and prepare?" });
```
Implementation Example（實作範例）

實際案例：Multiple Plugins Demo
實作環境：.NET、SK、多外部 API
實測數據：
改善前：單一資料源導致回答片面
改善後：多工具合成，資訊完整與實用
改善幅度：可用性提升（以用戶滿意度與引用比為指標）

Learning Points（學習要點）
核心知識點：
- 多工具編排策略
- 引用與提醒模板
- 可觀測性與審計
技能要求：
必備技能：多 API 整合
進階技能：編排與狀態機
延伸思考：
- 加入價格與時間預估
- 工具健康檢查與降級
- 回覆品質指標化

Practice Exercise（練習題）
基礎練習：掛載兩個插件並呼叫（30 分鐘）
進階練習：三插件編排與引用（2 小時）
專案練習：旅遊建議助理（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：多工具合成與引用
程式碼品質（30%）：封裝與測試
效能優化（20%）：呼叫延遲與降級
創新性（10%）：編排策略

---

## Case #11: 自訂 Kernel Memory 插件（領域特化檢索）

### Problem Statement（問題陳述）
業務場景：需將特定領域（例如內部 SOP/異常案例庫）的檢索功能以插件暴露，讓 LLM 能直接操作 MSKM 進行領域檢索與引用。
技術挑戰：需以自訂插件介面包裝 MSKM 特定功能與查詢條件，支援 tags 與分域查詢。
影響範圍：檢索精度與整合便利性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 通用插件不足以滿足領域的查詢條件。
2. 無法以 tags/屬性做分域檢索。
3. 無引用模板與治理。
深層原因：
- 架構層面：缺乏領域化插件介面。
- 技術層面：MSKM 查詢參數未被封裝。
- 流程層面：查詢與回覆一致性不足。

### Solution Design（解決方案設計）
解決策略：以自訂 MSKM 插件包裝查詢介面，提供領域特化方法（searchByTag/searchByTopic），並在 SK 中注入，形成工具列表。

實施步驟：
1. 插件封裝
- 實作細節：C# 封裝 mskmClient.SearchAsync(tag/topic/limit)。
- 所需資源：MSKM SDK、SK。
- 預估時間：1 天
2. Prompt 與引用模板
- 實作細節：回覆必附來源與 tags；限制回答範圍。
- 所需資源：模板。
- 預估時間：0.5 天
3. 測試與指標化
- 實作細節：以測試集評估召回與精度。
- 所需資源：標註資料。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public class KernelMemoryDomainPlugin {
  private readonly IMskmClient _client;
  public Task<IEnumerable<Result>> SearchByTagAsync(string tag, int limit)
    => _client.SearchAsync(new Query{ Tag = tag, Limit = limit });
}
```
Implementation Example（實作範例）

實際案例：RAG with Kernel Memory Custom Plugins
實作環境：.NET、MSKM、SK
實測數據：
改善前：通用檢索精度不足
改善後：領域特化檢索，召回品質提升
改善幅度：精度提升（以人工審查與命中率為指標）

Learning Points（學習要點）
核心知識點：
- 插件封裝與領域化查詢
- 引用與回答範圍治理
- 指標化評估
技能要求：
必備技能：SDK 封裝
進階技能：領域知識與標註
延伸思考：
- 多維度標籤與權重
- 與 reranker 結合
- 引入安全與權限

Practice Exercise（練習題）
基礎練習：封裝一個 searchByTag（30 分鐘）
進階練習：加入引用模板（2 小時）
專案練習：領域 RAG 工具集（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：封裝與查詢可用
程式碼品質（30%）：介面與測試
效能優化（20%）：查詢性能與快取
創新性（10%）：領域策略

---

## Case #12: MCP Server 整合 MSKM 與 Claude Desktop（跨平台工具協定）

### Problem Statement（問題陳述）
業務場景：希望在 Claude Desktop 等 MCP Host 內使用 MSKM 作 RAG，需以 MCP 協定暴露工具（tools/list、tools/invoke），讓不同語言與平台統一存取。
技術挑戰：實作 MCP server（stdio/SSE），正確處理 initialize/notifications，並支援工具清單與呼叫。
影響範圍：跨工具互通、整合效率、可移植性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 各家 Function Calling 介面不同，整合成本高。
2. MCP JSON-RPC 需正確實作與編碼處理。
3. 未解決中文編碼與顯示問題。
深層原因：
- 架構層面：缺乏統一工具協定（MCP）。
- 技術層面：通訊與編碼不一致。
- 流程層面：版本與相容性治理不足。

### Solution Design（解決方案設計）
解決策略：使用 MCP 官方 csharp-sdk 實作 MCP server，暴露 MSKM 搜索工具為 MCP tools；以 stdio 或 SSE 與 Host 連線；修正編碼。

實施步驟：
1. MCP server 骨架
- 實作細節：initialize、notifications/initialized、tools/list。
- 所需資源：csharp-sdk。
- 預估時間：1 天
2. tools/invoke 封裝 MSKM
- 實作細節：name:"search" → mskmClient.Search(query,limit)。
- 所需資源：MSKM SDK。
- 預估時間：0.5 天
3. 編碼修正與測試
- 實作細節：中文以 \uXXXX 編碼；Claude Desktop 測試。
- 所需資源：JsonSerializerOptions。
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
{"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"claude-ai","version":"0.1.0"}},"jsonrpc":"2.0","id":0}
{"method":"tools/list","params":{},"jsonrpc":"2.0","id":2}
{"method":"tools/call","params":{"name":"search","arguments":{"query":"SDK design","limit":3}},"jsonrpc":"2.0","id":9}
```
Implementation Example（實作範例）

實際案例：KernelMemory_MCPServer（官方/自製 SDK 兩版）
實作環境：.NET、MSKM、Claude Desktop、MCP csharp-sdk
實測數據：
改善前：跨平台工具整合困難
改善後：MCP 統一協定；可在 Claude 中直接查 MSKM
改善幅度：整合效率顯著提升

Learning Points（學習要點）
核心知識點：
- MCP 協定與工具暴露
- stdio/SSE 通訊
- JSON-RPC 與編碼治理
技能要求：
必備技能：通訊協定、序列化
進階技能：工具封裝與跨平台測試
延伸思考：
- 加入 resources/prompts 列表
- 安全與權限的 MCP 擴展
- 觀測與告警

Practice Exercise（練習題）
基礎練習：實作 tools/list（30 分鐘）
進階練習：封裝 search 並於 Claude 測試（2 小時）
專案練習：多工具 MCP server（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：MCP 基本方法與工具可用
程式碼品質（30%）：通訊實作與測試
效能優化（20%）：傳輸與序列化
創新性（10%）：跨平台擴展

---

## Case #13: MCP 中文 JSON 編碼問題修正（\uXXXX）

### Problem Statement（問題陳述）
業務場景：在 Claude Desktop 呼叫 MCP server 時，包含中文的 JSON 內容顯示或解析異常，需要轉為 \uXXXX 編碼以正常顯示與解析。
技術挑戰：正確設定 JsonSerializationOptions，保證中文安全輸出。
影響範圍：使用者體驗、工具可用性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Host 對中文直接輸出處理不佳。
2. 預設序列化未轉換為 \uXXXX。
3. 無測試用例覆蓋中文場景。
深層原因：
- 架構層面：跨平台編碼策略缺失。
- 技術層面：序列化配置未調整。
- 流程層面：版本相容測試不足。

### Solution Design（解決方案設計）
解決策略：調整 JSON 序列化配置，強制將非 ASCII 字元轉為 \uXXXX；以 Claude Desktop 實測驗證。

實施步驟：
1. 序列化設定
- 實作細節：使用 Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping 或自訂策略。
- 所需資源：System.Text.Json。
- 預估時間：0.5 天
2. 中文測試用例
- 實作細節：建立含中文的工具回應測試。
- 所需資源：測試框架。
- 預估時間：0.5 天
3. Host 驗證
- 實作細節：Claude Desktop 實測。
- 所需資源：Claude Desktop。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var options = new JsonSerializerOptions {
  Encoder = JavaScriptEncoder.Create(UnicodeRanges.BasicLatin, UnicodeRanges.CjkUnifiedIdeographs)
};
var json = JsonSerializer.Serialize(data, options); // 確保中文轉碼安全
```
Implementation Example（實作範例）

實際案例：MCP 官方 SDK 手動調整序列化後暫時可用
實作環境：.NET、MCP csharp-sdk、Claude Desktop
實測數據：
改善前：中文顯示/解析異常
改善後：\uXXXX 編碼下正常
改善幅度：可用性恢復（以人工驗證為指標）

Learning Points（學習要點）
核心知識點：
- JSON 編碼策略
- Host 相容性實測
- 跨平台序列化治理
技能要求：
必備技能：序列化設定
進階技能：跨平台相容測試
延伸思考：
- 自動偵測 Host 能力切換編碼策略
- 建立編碼健康檢查
- 上游 SDK issue 追蹤

Practice Exercise（練習題）
基礎練習：輸出含中文 JSON 並驗證（30 分鐘）
進階練習：封裝編碼策略（2 小時）
專案練習：加入編碼健康檢查（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：中文可正常顯示與解析
程式碼品質（30%）：封裝與可測試性
效能優化（20%）：序列化性能
創新性（10%）：自適應策略

---

## Case #14: MSKM 版本回退避免中文 chunk「晶晶體」

### Problem Statement（問題陳述）
業務場景：MSKM 2025/02 版按 token 分段的 chunking 對中文處理不佳，出現疊字「晶晶體」；需回退至 0.96.x 版本以恢復正常。
技術挑戰：在不影響其他功能的前提下進行版本回退；控制部署風險。
影響範圍：中文索引品質、檢索精度、整體 RAG 有效性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 新版 chunking 演算法未處理中文 token 化特殊性。
2. 未有修復版本釋出。
3. 生產環境未 pin 版本。
深層原因：
- 架構層面：版本策略與回滾機制不足。
- 技術層面：文本處理演算法變更風險。
- 流程層面：中文場景測試不足。

### Solution Design（解決方案設計）
解決策略：暫時回退至 0.96.x；建立版本 pin 與升級前測試流程；追蹤 issue 直至修復。

實施步驟：
1. 版本回退
- 實作細節：Docker 標記指定版本；NuGet 指定版本。
- 所需資源：部署系統。
- 預估時間：0.5 天
2. 測試覆蓋中文場景
- 實作細節：長文中文分段與檢索測試。
- 所需資源：測試集。
- 預估時間：0.5 天
3. 版本策略與告警
- 實作細節：pin 版本；升級前灰度測試；告警。
- 所需資源：CI/CD。
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# 指定 Docker 版本
docker pull mskm:0.96.x
docker run -d --name mskm -p 8080:8080 mskm:0.96.x
```
Implementation Example（實作範例）

實際案例：直播示範時建議回退至 0.96.x 避免中文疊字
實作環境：Docker、MSKM
實測數據：
改善前：中文 chunk 出現疊字，檢索失真
改善後：回退版本後中文正常
改善幅度：中文檢索品質恢復

Learning Points（學習要點）
核心知識點：
- 版本管理與回滾
- 文本處理演算法風險
- 灰度測試與告警
技能要求：
必備技能：部署與版本管理
進階技能：測試策略與可觀測性
延伸思考：
- 升級前自動化健康檢查
- 演算法差異可視化
- 多語系測試集建立

Practice Exercise（練習題）
基礎練習：版本回退操作（30 分鐘）
進階練習：中文長文測試（2 小時）
專案練習：建立版本策略（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：中文處理正常
程式碼品質（30%）：版本控制與腳本
效能優化（20%）：部署穩定性
創新性（10%）：升級治理

---

## Case #15: 土炮 Function Calling（不支援 FC 的模型）

### Problem Statement（問題陳述）
業務場景：某些 MCP Client 支援 Deepseek r1，但模型不支援原生 Function Calling；需要在不換模型情況下模擬工具呼叫。
技術挑戰：以 prompt 規約與應用邏輯攔截來模擬工具回合，維持任務閉環。
影響範圍：功能覆蓋範圍、可靠性、維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 模型不支援 FC，無 tool_calls/tool-result 結構。
2. 無角色化約定，難以區分對誰說話。
3. 應用端缺少攔截與執行器。
深層原因：
- 架構層面：缺乏工具回合協議。
- 技術層面：對話規約不清晰。
- 流程層面：任務閉環缺失。

### Solution Design（解決方案設計）
解決策略：以 system prompt 規約兩種前置詞（給使用者 vs 給秘書/工具），應用端攔截「請執行指令」訊息並執行，結果再追加到對話，直到任務完成。

實施步驟：
1. Prompt 規約
- 實作細節：定義「安德魯大人您好」→給使用者；「請執行指令」→給工具。
- 所需資源：Prompt 模板。
- 預估時間：0.5 天
2. 攔截與執行器
- 實作細節：應用端攔截工具訊息，執行並追加結果。
- 所需資源：執行器模組。
- 預估時間：1 天
3. 任務完成回覆
- 實作細節：以人類可讀訊息結案。
- 所需資源：回覆模板。
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
System prompt（節錄）：
- 若是「安德魯大人您好：...」，此段為給使用者的回覆。
- 若是「請執行指令：...」，此段為給秘書（工具）執行的指令，請列出執行參數。
```
Implementation Example（實作範例）

實際案例：土炮 FC 對話紀錄（ChatGPT 測試）
實作環境：.NET、任意 ChatCompletion 模型
實測數據：
改善前：無法呼叫工具
改善後：透過規約模擬工具回合
改善幅度：功能覆蓋提升（以任務完成率為指標）

Learning Points（學習要點）
核心知識點：
- 對話規約設計
- 攔截與執行回合
- 任務閉環
技能要求：
必備技能：Prompt 設計
進階技能：狀態管理與編排
延伸思考：
- 正規場合仍建議用原生 FC
- 與 MCP/SDK 結合可提升可靠性
- 風險：prompt 對抗性

Practice Exercise（練習題）
基礎練習：設計前置詞規約（30 分鐘）
進階練習：攔截工具訊息並執行（2 小時）
專案練習：完整任務編排（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可模擬工具回合
程式碼品質（30%）：攔截與封裝
效能優化（20%）：回合延遲
創新性（10%）：規約設計

---

## Case #16: SK Memory vs MSKM（長期記憶管線的正確選擇）

### Problem Statement（問題陳述）
業務場景：SK 提供 Memory 抽象與 Vector Store CRUD，但 RAG ingestion（抽取/分段/向量化/儲存/查詢）需完整管線；需正確選擇工具。
技術挑戰：理解 SK Memory 與 MSKM 的分工，避免誤用導致功能缺失。
影響範圍：長期記憶可用性與維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 認為 SK Memory 足以勝任完整 RAG。
2. 忽略 ingestion 管線的複雜性。
3. 未評估長任務處理需求。
深層原因：
- 架構層面：長期記憶服務化缺失。
- 技術層面：管線元件未組裝。
- 流程層面：數據治理缺失。

### Solution Design（解決方案設計）
解決策略：以 MSKM 提供完整 RAG 服務與 SDK；SK 作為前端工具編排；兩者分層協作。

實施步驟：
1. 角色分工
- 實作細節：SK 做對話/工具編排；MSKM 做長記憶管線。
- 所需資源：SK、MSKM。
- 預估時間：0.5 天
2. 整合接口
- 實作細節：SK 掛 MSKM Plugin；前端直接用工具。
- 所需資源：MSKM NuGet。
- 預估時間：0.5 天
3. 治理與監控
- 實作細節：對 ingestion 成功率與索引品質做監控。
- 所需資源：Logger/監控。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 分工示意：SK 為 Orchestrator，MSKM 為 LTM Service
kernel.Plugins.Add(new KernelMemoryPlugin(mskmClient));
```
Implementation Example（實作範例）

實際案例：RAG as a Service（MSKM）與 SK 整合
實作環境：.NET、SK、MSKM
實測數據：
改善前：誤用 SK Memory 導致管線缺失
改善後：分工清晰，服務化落地
改善幅度：架構健壯性提升

Learning Points（學習要點）
核心知識點：
- Memory vs LTM Service 分工
- 插件化整合
- 管線治理
技能要求：
必備技能：架構設計
進階技能：服務化思維
延伸思考：
- 以事件驅動串連 ingestion
- 指標化索引品質
- 多模型支持

Practice Exercise（練習題）
基礎練習：繪製分工架構圖（30 分鐘）
進階練習：SK+MSKM 整合 PoC（2 小時）
專案練習：完整 LTM 管線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：分工與整合到位
程式碼品質（30%）：封裝與依賴清晰
效能優化（20%）：管線吞吐
創新性（10%）：治理策略

---

## Case #17: 成本治理：單一職責與 Code vs LLM 的正確分工

### Problem Statement（問題陳述）
業務場景：開發者傾向把可由程式完成的任務交給 LLM（搜尋、格式轉換、計算），導致成本高、延遲大且品質不穩；需將 LLM 僅用於不可替代任務。
技術挑戰：建立單一職責策略與成本感知管道，降低 tokens 花費與不必要的 API。
影響範圍：雲端費用、性能與品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 便利性導致過度使用 LLM。
2. 未評估 Azure Function vs ChatCompletion 的成本差。
3. 需求混合在一個 prompt，無法分離。
深層原因：
- 架構層面：無責任分界與治理。
- 技術層面：缺少成本追蹤與路由策略。
- 流程層面：無標準化任務分解。

### Solution Design（解決方案設計）
解決策略：單一職責分解：LLM 處理抽取/理解/規劃；程式碼處理查詢/計算/格式；建立成本指標與路由策略。

實施步驟：
1. 任務分解
- 實作細節：將需求分拆為 LLM 任務與 Code 任務。
- 所需資源：設計審查。
- 預估時間：0.5 天
2. 成本監控
- 實作細節：記錄 tokens、API 成本、延遲。
- 所需資源：Logger/監控。
- 預估時間：1 天
3. 路由策略
- 實作細節：能由程式完成則路由至 code；否則用 LLM。
- 所需資源：策略引擎。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
if (CanCodeHandle(task)) {
  return ExecuteByCode(task); // 低成本高可靠
} else {
  return CallLLM(task); // 僅限不可替代任務
}
```
Implementation Example（實作範例）

實際案例：地址抽取 → LLM；地圖查詢 → Code
實作環境：.NET、OpenAI、外部 API
實測數據：
改善前：混合任務全部交 LLM，成本高
改善後：路由分工，成本與延遲降低
改善幅度：成本治理顯著（以 tokens 與延遲為指標）

Learning Points（學習要點）
核心知識點：
- 單一職責原則
- 成本感知與路由
- 指標化治理
技能要求：
必備技能：架構設計
進階技能：策略引擎
延伸思考：
- 以 A/B 測試優化路由
- 自動化成本預估
- 加入品質門檻（如引用比例）

Practice Exercise（練習題）
基礎練習：將一需求分解為 LLM/Code（30 分鐘）
進階練習：記錄成本指標（2 小時）
專案練習：建立路由策略引擎（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：分工與路由落地
程式碼品質（30%）：封裝與可測
效能優化（20%）：成本與延遲
創新性（10%）：自動化治理

---

## Case #18: 以 OpenAPI/Swagger 管理工具規格（SK/GPTs/Dify/MCP）

### Problem Statement（問題陳述）
業務場景：需在不同宿主（ChatGPT GPTs、Dify、SK、Claude MCP）中暴露同一套工具，避免重做規格；希望用 OpenAPI（Swagger）作為統一合約。
技術挑戰：多平台工具規格一致與自動生成客戶端；以最小成本暴露功能。
影響範圍：整合效率、維護成本、相容性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 各平台工具定義方式不同。
2. 無統一合約導致重複工作。
3. 缺少自動化生成客戶端。
深層原因：
- 架構層面：工具合約管理缺失。
- 技術層面：缺乏標準接口描述。
- 流程層面：版本一致性與測試不足。

### Solution Design（解決方案設計）
解決策略：以 OpenAPI Spec 作工具合約；在 SK 注入 Swagger；在 GPTs/Dify/MCP 中以相同規格暴露；統一生成客戶端。

實施步驟：
1. OpenAPI Spec 編寫
- 實作細節：定義 /search、/lookup、/add_event 等端點與 schema。
- 所需資源：Swagger Editor。
- 預估時間：1 天
2. 注入至各宿主
- 實作細節：SK 支援注入 Swagger；GPTs/Dify 以 Custom Action/Tool。
- 所需資源：各平台配置。
- 預估時間：1 天
3. 客戶端生成與測試
- 實作細節：生成 C# 客戶端；跨平台測試。
- 所需資源：OpenAPI Generator。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// SK 注入 Swagger（伪代码）
kernel.Plugins.Add(PluginFactory.FromOpenApi("MyTools", "openapi.yaml"));
```
Implementation Example（實作範例）

實際案例：ChatGPT GPTs + Custom Action、Dify Custom Tools、SK 注入 Swagger、MCP 對應工具
實作環境：.NET、SK、OpenAPI/GPTs/Dify/MCP
實測數據：
改善前：各平台重複定義工具
改善後：以 OpenAPI 作為單一合約
改善幅度：整合效率與一致性顯著提升

Learning Points（學習要點）
核心知識點：
- 工具合約管理（OpenAPI）
- 多宿主注入方法
- 客戶端生成與版本治理
技能要求：
必備技能：OpenAPI/Swagger
進階技能：多平台整合
延伸思考：
- 加入 OAuth 安全
- 版本化與相容性測試
- 自動化文檔生成

Practice Exercise（練習題）
基礎練習：撰寫一個 /search 的 OpenAPI（30 分鐘）
進階練習：在 SK 注入並呼叫（2 小時）
專案練習：多宿主工具整合（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：工具合約與跨平台注入
程式碼品質（30%）：Spec 與客戶端生成
效能優化（20%）：呼叫延遲與錯誤處理
創新性（10%）：治理與自動化

---

案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #1、#2、#13、#14
- 中級（需要一定基礎）
  - Case #3、#5、#6、#7、#16、#17、#18
- 高級（需要深厚經驗）
  - Case #4、#8、#9、#10、#11、#12、#15

2. 按技術領域分類
- 架構設計類
  - Case #6、#7、#16、#17、#18
- 效能優化類
  - Case #4、#8、#9、#10、#14、#17
- 整合開發類
  - Case #3、#5、#6、#10、#11、#12、#18
- 除錯診斷類
  - Case #13、#14、#15
- 安全防護類
  - Case #18（OAuth 可延伸）

3. 按學習目標分類
- 概念理解型
  - Case #1、#2、#16
- 技能練習型
  - Case #3、#5、#6、#9、#10、#11
- 問題解決型
  - Case #4、#8、#12、#13、#14、#15、#17
- 創新應用型
  - Case #18、#10、#11

案例關聯圖（學習路徑建議）
- 先學：
  - Case #1（Chat 基礎）
  - Case #2（JSON Mode/Schema）
- 再學：
  - Case #3（FC 基礎）
  - Case #4（FC 連續工具）
- 進入 RAG：
  - Case #5（以 FC 觸發檢索）
  - Case #6（MSKM 作為 RAG 服務）
  - Case #7（部署選型）
- 提升檢索品質：
  - Case #9（Summarization handler）
  - Case #8（合成檢索素材）
  - Case #11（自訂領域插件）
  - Case #10（多插件協作）
- 跨平台整合：
  - Case #12（MCP server 與 Claude）
  - Case #18（OpenAPI 合約）
- 穩定性與除錯：
  - Case #13（中文編碼）
  - Case #14（版本回退）
- 成本治理與特例：
  - Case #17（單一職責與成本）
  - Case #15（土炮 FC，作為備援）

依賴關係：
- Case #1、#2 → Case #3、#4（FC）
- Case #3、#4 → Case #5（觸發 RAG）
- Case #5 → Case #6、#7（MSKM）
- Case #6、#7 → Case #9、#8、#11（品質提升）
- Case #6 → Case #12、#18（跨平台工具）
- Case #12 → Case #13（編碼修正）
- Case #6 → Case #14（版本治理）
- Case #2、#17 → 全案（分工與成本）

完整學習路徑建議：
1. 打底：Case #1 → #2（理解 Chat/JSON 合約）
2. 工具：Case #3 → #4（掌握 FC 與連續工具）
3. 檢索：Case #5 → #6 → #7（以 FC 觸發 RAG、導入 MSKM）
4. 品質：Case #9 → #8 → #11 → #10（摘要/合成/領域插件/多工具協作）
5. 跨平台：Case #18 → #12 → #13（OpenAPI 合約 → MCP 整合 → 中文編碼修正）
6. 穩定性：Case #14（版本治理）、#17（成本治理）
7. 特例：Case #15（土炮 FC，當模型不支援 FC 時的備援策略）

以上案例可直接對應文中 Demo、敘事與設計觀點，以利教學、實作與評估。
{% endraw %}