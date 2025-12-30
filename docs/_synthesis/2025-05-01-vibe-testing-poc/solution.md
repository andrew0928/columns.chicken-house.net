---
layout: synthesis
title: "從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得"
synthesis_type: solution
source_post: /2025/05/01/vibe-testing-poc/
redirect_from:
  - /2025/05/01/vibe-testing-poc/solution/
---

## Case #1: 從 Intent 到 Assertion 的 LLM 驅動 API 自動化測試

### Problem Statement（問題陳述）
業務場景：團隊需要在開發階段快速驗證購物車等核心業務的 AC，並希望僅用領域層級的 GWT 情境描述，就能自動選用 API、產生參數、執行測試並產出報告。傳統需工程師撰寫腳本、串接前後 API 參數與斷言，耗時易錯，難以在 CI 中批量運行。PoC 目標是在不改動後端的情況下驗證可行性。
技術挑戰：將抽象情境映射為具體 API 方案與參數、避免 LLM 幻覺、處理 OAuth2、統一測試狀態與報告格式。
影響範圍：測試效率、覆蓋率、工程人力成本、CI 穩定度與可追蹤性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 測試腳本撰寫與維護量大，情境到步驟的翻譯全靠人工。
2. API 參數傳遞與狀態綁定複雜，易產生耦合錯誤。
3. 測試報告格式不一難彙整，無法快速量化結果。
深層原因：
- 架構層面：業務邏輯分散在呼叫端，API 缺少高階動作封裝。
- 技術層面：未善用 LLM 的 Tool Use 與 Structured Output 能力。
- 流程層面：規格文件與測試資產分離，缺乏可機器理解的管道。

### Solution Design（解決方案設計）
解決策略：以 Semantic Kernel 將 OpenAPI 直接轉成插件（Tool），用三段式 Prompt（規則/GWT 案例/報告模板）驅動 LLM 自主選 API 和建參數、執行並產出 markdown+JSON 雙格式報告，搭配 OAuth2 自動注入與請求/回應日誌，構成可在 CI 觸發的 Test Runner。

實施步驟：
1. 測試案例整備（GWT）
- 實作細節：以 AC 展開情境，保持與實作規格解耦。
- 所需資源：案例庫（文字/MD）
- 預估時間：0.5-1 人日

2. 導入 API 工具（Plugin）
- 實作細節：ImportPluginFromOpenApiAsync 掛入 swagger 工具。
- 所需資源：Semantic Kernel、OpenAPI spec
- 預估時間：0.5 人日

3. Prompt 編排與設定
- 實作細節：System 規則、防幻覺、報告模板；FunctionChoiceBehavior.Auto。
- 所需資源：OpenAI Chat API（o4-mini）
- 預估時間：0.5 人日

4. 認證與日誌
- 實作細節：AuthCallback 注入 Bearer token；HTTP 日誌全記錄。
- 所需資源：OAuth2 Provider、HttpLogger
- 預估時間：0.5 人日

5. 執行與報告收斂
- 實作細節：同時輸出 markdown/JSON；歸檔與告警。
- 所需資源：檔案儲存/CI 工具
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
var builder = Kernel.CreateBuilder()
  .AddOpenAIChatCompletion("o4-mini", OPENAI_APIKEY, HttpLogger.GetHttpClient(false));
var kernel = builder.Build();

// 掛入 API 工具
await kernel.ImportPluginFromOpenApiAsync(
  "andrew_shop",
  new Uri("https://andrewshopoauthdemo.azurewebsites.net/swagger/v1/swagger.json"),
  new OpenApiFunctionExecutionParameters {
    EnablePayloadNamespacing = true,
    HttpClient = HttpLogger.GetHttpClient(true),
    AuthCallback = (req, _) => {
      req.Headers.Add("Authorization", $"Bearer {userAccessToken}");
      return Task.CompletedTask;
    }
  });

// Function Calling 自動啟用
var settings = new PromptExecutionSettings {
  FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};

// 三段式 Prompt 執行
var report = await kernel.InvokePromptAsync<string>(
"""
<message role="system">…GWT 規則、防幻覺要求…</message>
<message role="user">…貼上 test_case 內容…</message>
<message role="user">…報告模板（表格與狀態列示）…</message>
""", new(settings) { ["test_case"] = testCaseMarkdown });
```

實際案例：購物車加入 11 件「可口可樂」應回 400，實際回 200 → Then 失敗，測試不過，並輸出清晰報告與 JSON。
實作環境：.NET Console App、Semantic Kernel、OpenAI o4-mini、AndrewShop API（OAuth2）。
實測數據：
改善前：需工程師撰寫腳本與斷言、人工彙總報告。
改善後：單案例自動執行約 1 分鐘完成並產出雙格式報告。
改善幅度：實作關鍵碼<50 行；免寫 16 個 API wrapper。

Learning Points（學習要點）
核心知識點：
- LLM Tool Use 將情境自動化為 API 行動
- GWT 與 Prompt 承載測試規則與斷言
- 測試報告雙格式輸出與可追蹤性

技能要求：
必備技能：REST/OpenAPI、C#/.NET、SK 基礎、GWT 測試設計
進階技能：Prompt 設計、OAuth2、結構化輸出與 CI 整合

延伸思考：
- 同一 Domain Case 能否套到 UI 測試（Browser/Computer Use）？
- 風險：API 非 AI Ready 時路徑發散、成本/延遲控制
- 優化：分段執行、快取規格、並行化與重試策略

Practice Exercise（練習題）
基礎練習：為「加入商品超量」案例撰寫 GWT，產出報告。
進階練習：新增 3 個異常案例（未登入、缺貨、負數數量），完成報告與 JSON。
專案練習：將 Runner 接到 CI，批量跑 15 個案例並生成匯總頁。

Assessment Criteria（評估標準）
功能完整性（40%）：可從 GWT 自動執行並輸出雙格式報告
程式碼品質（30%）：模組化、日誌完備、錯誤處理清晰
效能優化（20%）：執行時間可控、重試與並發策略
創新性（10%）：Prompt/工具設計與報告呈現創新度


## Case #2: OpenAPI 一鍵轉 Plugin，免包 Function Wrapper

### Problem Statement（問題陳述）
業務場景：專案有 16 個以上 API 需被測試。若逐一手寫 Function Wrapper 供 LLM 使用，維護成本高且與 Swagger 易失同步，導致測試用工具常出錯。希望快速、正確把 OpenAPI 規格轉為 LLM 可直接調用的 Tool 集。
技術挑戰：自動解析 OpenAPI/Json Schema、處理認證與命名空間、維持與後端同步。
影響範圍：開發效率、規格同步性、測試正確性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 人工包裝 Wrapper 容易漏欄位、誤參數與落後更新。
2. Spec 變更頻繁，Wrapper 同步困難。
3. 認證與通用設定在多個 Wrapper 重複書寫。
深層原因：
- 架構層面：工具層未標準化，缺少自動生成功能。
- 技術層面：未善用 SK 的 OpenAPI→Plugin 能力。
- 流程層面：Spec 與測試工具建置流程未納入 CI。

### Solution Design（解決方案設計）
解決策略：使用 Semantic Kernel 的 ImportPluginFromOpenApiAsync，將 Swagger 直接導入為 Plugin，集中處理 Auth、HttpClient、命名空間，保證與後端規格一致並即時可用。

實施步驟：
1. 準備 Swagger
- 實作細節：確保 OpenAPI 正確且可公開讀取。
- 所需資源：後端服務/Swagger UI
- 預估時間：0.5 人日

2. 導入 Plugin 與設定
- 實作細節：設定 HttpClient、AuthCallback、EnablePayloadNamespacing。
- 所需資源：SK 套件
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
await kernel.ImportPluginFromOpenApiAsync(
  "andrew_shop",
  new Uri("https://andrewshopoauthdemo.azurewebsites.net/swagger/v1/swagger.json"),
  new OpenApiFunctionExecutionParameters {
    EnablePayloadNamespacing = true,
    HttpClient = HttpLogger.GetHttpClient(true),
    AuthCallback = (req, _) => {
      req.Headers.Add("Authorization", $"Bearer {userAccessToken}");
      return Task.CompletedTask;
    }
  });
```

實際案例：PoC 直接把 AndrewShop 的 16 個 API 匯入，無需自建 Wrapper。
實作環境：.NET + SK + OpenAPI。
實測數據：
改善前：需為 16 個 API 各寫 Wrapper。
改善後：10 行內完成匯入；關鍵整合碼<50 行。
改善幅度：Wrapper 實作工時幾近歸零，規格同步即時。

Learning Points（學習要點）
核心知識點：
- OpenAPI→Plugin 自動化
- 統一處理認證/HTTP 設定
- 命名空間與函式選擇行為

技能要求：
必備技能：OpenAPI/Swagger、SK 基礎
進階技能：AuthCallback/HTTP 客製化

延伸思考：
- 如何在 CI 中自動重新匯入最新規格？
- Spec 破壞性變更的回溯與告警機制？
- 減少重複匯入的快取策略

Practice Exercise（練習題）
基礎練習：匯入任一公開 Swagger 成 Plugin。
進階練習：加入自訂 AuthCallback 與 Request 日誌。
專案練習：建置自動匯入工作（CI），規格更新即重建 Plugin。

Assessment Criteria（評估標準）
功能完整性（40%）：Plugin 可被 LLM 成功呼叫
程式碼品質（30%）：設定集中、易維護
效能優化（20%）：匯入與執行耗時可控
創新性（10%）：自動化與快取設計


## Case #3: GWT 規則落地與防幻覺策略（只接受真實 API 回應）

### Problem Statement（問題陳述）
業務場景：測試需嚴格遵循 GWT，且結果必須來自真實 API 回應以確保可信度。若 LLM 擅自生成 Response 或使用快取，將導致斷言失真與誤判，影響產品決策與回歸驗證。
技術挑戰：在 Prompt 中有效約束模型行為，避免生成式回應污染測試。
影響範圍：測試準確度、信任度與合規性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. LLM 具生成傾向，可能假造 Response。
2. 無明確失敗分類導致結果難以追蹤。
3. 測試規則未標準化，易被模型忽略。
深層原因：
- 架構層面：缺少統一的測試規則層。
- 技術層面：Prompt 未顯性禁止生成 Response。
- 流程層面：未以標準狀態碼彙整失敗類型。

### Solution Design（解決方案設計）
解決策略：以 System Prompt 定義 GWT 準則與「禁止生成/快取 Response」鐵律，並引導以 start_fail/exec_fail/test_fail/test_pass 四態出具報告，確保出錯可追蹤可歸因。

實施步驟：
1. 制訂 System 規則
- 實作細節：清楚定義 GWT 意義、失敗訊號與禁止生成。
- 所需資源：Prompt 模板
- 預估時間：0.5 人日

2. 報告模板嵌入
- 實作細節：固定欄位與狀態欄，避免自由發揮。
- 所需資源：報告 Markdown/JSON 模板
- 預估時間：0.5 人日

關鍵程式碼/設定：
```text
// Implementation Example（實作範例：System Prompt 節選）
依照我給你的 test case 執行測試:
- Given/When/Then 各自責任與失敗標記…
所有標示 api 的 request/response 內容, 請勿直接生成,
或啟用任何 cache 機制替代直接呼叫 api。
我只接受真正呼叫 api 取得的 response。
```

實際案例：購物車超量案例，所有 Response 皆來自真實呼叫；日誌佐證。
實作環境：同 Case #1。
實測數據：
改善前：存在幻覺風險，難追蹤。
改善後：本案例未出現虛構回應；報告與日誌一致。

Learning Points（學習要點）
核心知識點：
- GWT 與失敗分類
- 防幻覺 Prompt 技巧
- 報告欄位定型化

技能要求：
必備技能：Prompt 清單化規則設計
進階技能：測試狀態設計與日志對帳

延伸思考：
- 可否以工具層強制 API 呼叫（封鎖模型生成通道）？
- 引入結構化輸出強化可解析性？
- 在高失敗率場景下的自動重試策略

Practice Exercise（練習題）
基礎練習：撰寫禁止生成 Response 的 System Prompt。
進階練習：為 2 個案例產出四態報告，附上日誌比對。
專案練習：實作報告與日誌自動核對工具。

Assessment Criteria（評估標準）
功能完整性（40%）：四態明確且能覆蓋主要失敗
程式碼品質（30%）：模板化、可重用
效能優化（20%）：核對流程耗時合理
創新性（10%）：防幻覺與核對手段創新


## Case #4: 從領域情境自動選 API 與參數綁定

### Problem Statement（問題陳述）
業務場景：測試案例僅以「加入 11 件可口可樂」等領域語句描述，不包含 API 與參數細節。需讓 LLM 自行決定呼叫哪些端點、如何取得 productId、如何清空購物車，再執行斷言。
技術挑戰：從「可口可樂」語義映射出 productId、以「建立新購物車」替代「清空」、正確串接前後狀態。
影響範圍：測試可用性、跨介面重用性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Domain Case 與 API Spec 有語義落差。
2. API 無搜尋與清空購物車端點。
3. 步驟間狀態依賴無人處理易出錯。
深層原因：
- 架構層面：Domain 與介面耦合度高。
- 技術層面：缺少自動化的語義→規格映射。
- 流程層面：案例審核未區分「概念」與「介面」。

### Solution Design（解決方案設計）
解決策略：在 Prompt 中要求模型以 Given/When 拆解前置與操作，先 CreateCart 再 GetProducts 選 Coca-Cola productId，繼而 AddItemToCart、GetCart 驗證，達到從語義自動綁定參數與端點。

實施步驟：
1. 定義替代策略
- 實作細節：「清空購物車」→「建立新購物車」。
- 所需資源：Spec 條目與說明
- 預估時間：0.25 人日

2. 映射產品識別
- 實作細節：GetProducts→以名稱匹配取得 productId。
- 所需資源：產品清單回應
- 預估時間：0.25 人日

關鍵程式碼/設定：
```http
// Implementation Example（實作步驟的端點序列）
POST /api/carts/create
GET  /api/products
POST /api/carts/{cartId}/items   // body: { productId, qty: 11 }
GET  /api/carts/{cartId}
```

實際案例：可口可樂 11 件案例，模型自行選端點與產生參數，並完成 Then 檢驗。
實作環境：同 Case #1。
實測數據：
改善前：需測試工程師撰寫腳本綁定 productId 與 cartId。
改善後：LLM 自動推理取得，整段自動化。
改善幅度：端到端綁定無需人工維護腳本。

Learning Points（學習要點）
核心知識點：
- 語義到規格映射
- 前後步驟狀態傳遞
- 用替代策略補規格缺口

技能要求：
必備技能：REST 與資料模型理解
進階技能：Prompt 中的映射指引

延伸思考：
- 名稱匹配易受文案影響，是否加入相似度/別名表？
- UI 層如何類比映射（button→action）？
- 產品多語系名稱的處理策略

Practice Exercise（練習題）
基礎練習：用名稱匹配取得 productId。
進階練習：設計缺少 Search API 下的映射策略。
專案練習：為 3 個不同商品各自從名稱推 productId 並加入購物車。

Assessment Criteria（評估標準）
功能完整性（40%）：可自動完成全流程參數綁定
程式碼品質（30%）：映射邏輯清晰且可重用
效能優化（20%）：步驟最小化、避免冗餘呼叫
創新性（10%）：映射策略設計與容錯


## Case #5: OAuth2 無人值守認證注入

### Problem Statement（問題陳述）
業務場景：AndrewShop API 受 OAuth2 保護，正常流程需瀏覽器互動登入。自動化測試需在無 UI 的 Runner 中完成授權，並能指定測試使用者，確保各案例能以正確身份執行。
技術挑戰：取得 access token 並安全注入每次 API 呼叫，避免中斷測試流程。
影響範圍：測試可用性、安全性與可重現性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 認證流程要求人機互動，阻塞自動化。
2. 測試需切換不同使用者上下文。
3. token 與過期管理無策略。
深層原因：
- 架構層面：認證未抽象為測試環境控管。
- 技術層面：未集中注入 Authorization。
- 流程層面：測試資料與使用者管理缺位。

### Solution Design（解決方案設計）
解決策略：以 Plugin 方式統一管理測試使用者上下文，先行取得 access token，並透過 ImportPluginFromOpenApiAsync 的 AuthCallback 在每次呼叫自動注入 Authorization: Bearer，讓測試流程不受阻。

實施步驟：
1. 測試使用者上下文
- 實作細節：以 APIExecutionContextPlugin 管理 user/token。
- 所需資源：測試帳號、OAuth2 設定
- 預估時間：1 人日

2. AuthCallback 注入
- 實作細節：集中設定 Authorization Header。
- 所需資源：SK OpenAPI 執行參數
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
await kernel.ImportPluginFromOpenApiAsync(
  "andrew_shop",
  new Uri(swaggerUri),
  new OpenApiFunctionExecutionParameters {
    HttpClient = HttpLogger.GetHttpClient(true),
    AuthCallback = (req, _) => {
      var ctx = APIExecutionContextPlugin.GetContext(); // 自訂：取得目前測試使用者
      req.Headers.Add("Authorization", $"Bearer {ctx.AccessToken}");
      return Task.CompletedTask;
    }
  });
```

實際案例：每次測試皆獲不同 token；HTTP 日誌可見 Authorization Header；API 正常授權執行。
實作環境：同 Case #1。
實測數據：
改善前：需手動登入、難自動化。
改善後：全自動注入；不同案例可指定不同使用者。
改善幅度：無 UI 條件下完成端到端授權流程。

Learning Points（學習要點）
核心知識點：
- OAuth2 測試自動化策略
- AuthCallback 集中注入
- 使用者上下文管理

技能要求：
必備技能：OAuth2 基礎、HTTP Header
進階技能：測試使用者資料與租約管理

延伸思考：
- token 刷新與過期的容錯策略？
- 憑證/機密管理（Vault）？
- 單測與整批測試切換使用者的設計

Practice Exercise（練習題）
基礎練習：以固定 token 注入並呼叫受保護 API。
進階練習：設計簡易 Context Plugin 載入不同使用者。
專案練習：實作 token 刷新與過期重試機制。

Assessment Criteria（評估標準）
功能完整性（40%）：受保護 API 可自動授權呼叫
程式碼品質（30%）：授權邏輯集中、可測試
效能優化（20%）：token 取得/刷新開銷可控
創新性（10%）：上下文與安全策略設計


## Case #6: 雙軌輸出：Markdown 給人看、JSON 給系統用

### Problem Statement（問題陳述）
業務場景：單次測試可用閱讀友善的報告，但在批量與回歸場景，需要可被系統彙整、統計與告警的結構化輸出。需同時產出可讀性與可整合性兼具的結果。
技術挑戰：讓 LLM 同步輸出一致且可解析的 JSON。
影響範圍：測試平台整合、趨勢分析與警示。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Markdown 難機械解析。
2. 報告欄位不一致。
3. 測試平台需要結構化資料。
深層原因：
- 架構層面：輸出未定義 Schema。
- 技術層面：未啟用 Structured Output。
- 流程層面：缺少集中彙整與可視化。

### Solution Design（解決方案設計）
解決策略：在 Prompt 中同時要求 Markdown 與 JSON；JSON 套用固定欄位（name/result/context/steps…），利於後續存檔、搜尋與匯總。

實施步驟：
1. JSON Schema 設計
- 實作細節：固定欄位與型別，對齊報告欄位。
- 所需資源：Schema 定義
- 預估時間：0.5 人日

2. 輸出管線
- 實作細節：分檔輸出（.md/.json），檔名含案例代碼。
- 所需資源：檔案系統/DB
- 預估時間：0.5 人日

關鍵程式碼/設定：
```json
// Implementation Example（實作範例：實際 JSON）
{
  "name": "TC-05 (非法上界)",
  "result": "test_fail",
  "comments": "AddItemToCart 未回傳 400，且購物車不為空",
  "context": { "shop":"shop123", "user": { "access_token":"...", "user":"andrew" } },
  "steps": [
    { "api": "CreateCart", "request": {}, "response": {"id":57,"lineItems":[]}, "test-result": "pass" },
    { "api": "GetProducts", "request": {}, "response": [ { "id":2, "name":"可口可樂® 350ml" } ], "test-result":"pass" },
    { "api": "AddItemToCart", "request": {"id":57,"productId":2,"qty":11}, "response":{"id":57,"lineItems":[{"productId":2,"qty":11}]}, "test-result":"fail" }
  ]
}
```

實際案例：與 Markdown 報告對應一致，可直接寫入報表系統。
實作環境：同 Case #1。
實測數據：
改善前：無法自動彙整。
改善後：可直接聚合、統計、告警。
改善幅度：回歸分析與趨勢追蹤難度大幅下降。

Learning Points（學習要點）
核心知識點：
- Structured Output 設計
- 報告雙軌輸出策略
- 後續可視化與告警

技能要求：
必備技能：JSON/Schema 設計
進階技能：LLM 結構化輸出與驗證

延伸思考：
- 在 LLM 端強化 JSON 嚴格模式？
- 上游 Schema 自動生成（基於欄位字典）？
- 與測試管理系統整合（如 TestRail/Jira）

Practice Exercise（練習題）
基礎練習：為現有報告新增 JSON 同步輸出。
進階練習：撰寫 Schema 驗證器驗收 JSON。
專案練習：建置報告匯總 Dashboard 與告警規則。

Assessment Criteria（評估標準）
功能完整性（40%）：雙輸出一致且可解析
程式碼品質（30%）：輸出模組化、測試涵蓋
效能優化（20%）：大量輸出效能可控
創新性（10%）：視覺化與告警設計


## Case #7: AI Ready 的領域導向 API 設計，替代純 CRUD

### Problem Statement（問題陳述）
業務場景：若 API 僅提供 CRUD，業務規則需由呼叫端拼裝，AI 在測試時需做大量推理與狀態管理，錯誤率與不可預期性提高。需以領域動作封裝商業規則，讓測試路徑穩定。
技術挑戰：從資料導向轉為行為導向，維持語意清晰與一致。
影響範圍：可測性、可靠度、AI 理解成本。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. CRUD 無法承載完整商業規則。
2. 呼叫端需組裝大量前後置邏輯。
3. 測試路徑發散且難重現。
深層原因：
- 架構層面：缺少 Domain 操作層與邊界。
- 技術層面：API 設計缺乏語義命名與約束。
- 流程層面：未以 AC/Domain 驅動 API 設計。

### Solution Design（解決方案設計）
解決策略：將核心規則內聚於 API（如 AddItemToCart 應處理數量上限邏輯），讓文件成為可供 LLM 理解的 Prompt，減少呼叫端組裝與測試不確定性。

實施步驟：
1. 規則內聚
- 實作細節：把限購、庫存、授權等邏輯收斂到動作端點。
- 所需資源：AC、狀態圖
- 預估時間：中期重構

2. 文件強化
- 實作細節：OpenAPI 描述語義、錯誤碼與範例。
- 所需資源：文件產線/CI
- 預估時間：持續性投入

關鍵程式碼/設定：
```text
// Implementation Example（設計指引）
POST /api/carts/{id}/items  // 負責：驗證上限、存量、授權、邏輯回應碼
// 文件中清楚描述 400 情境：「同商品上限 10 件」
```

實際案例：當規則未落於 API，測試顯示加入 11 件仍成功（應回 400），暴露設計缺陷。
實作環境：AndrewShop API（示範缺口）。
實測數據：
改善前：AI 測試不穩定、路徑發散。
改善後：規則落入 API 後，錯誤可由 Then 精準捕捉。
改善幅度：AI 測試可預測性大幅提升。

Learning Points（學習要點）
核心知識點：
- DDD 與 API 設計
- 規則內聚與錯誤碼策略
- 文件即 Prompt

技能要求：
必備技能：API 設計準則
進階技能：領域建模與錯誤處理設計

延伸思考：
- 既有 CRUD 如何漸進式重構？
- 向前兼容與版本策略？
- 文件與測試共演（合同測試）

Practice Exercise（練習題）
基礎練習：為 1 個 CRUD 端點提出領域動作版。
進階練習：定義錯誤碼矩陣與範例。
專案練習：重構購物車關鍵端點為領域導向。

Assessment Criteria（評估標準）
功能完整性（40%）：動作語義與規則完整
程式碼品質（30%）：清晰邊界與錯誤處理
效能優化（20%）：不引入額外冗餘呼叫
創新性（10%）：文件與 AI 友善度設計


## Case #8: 精準 OpenAPI 與 CI 產生，防規格漂移

### Problem Statement（問題陳述）
業務場景：LLM 依賴準確的 OpenAPI 做 Tool Use。若 Spec 與程式不同步，測試會失真甚至無法執行。需要在 CI 中自動產生與發佈最新規格，避免人工維護造成偏差。
技術挑戰：將 Spec 產線化、版本化與變更告警化。
影響範圍：測試可信度、開發效率、回歸品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 人工維護 Swagger 易落後。
2. 無版本與差異比對。
3. 測試與 Spec 無自動耦合。
深層原因：
- 架構層面：缺少文件產線。
- 技術層面：未把 Spec 作為契約資產。
- 流程層面：CI 未加入規格步驟。

### Solution Design（解決方案設計）
解決策略：以 CI 自動產生 OpenAPI（由程式/註解生成）、簽入制品庫、版本標記並發布 URL，Test Runner 只讀取 CI 輸出的規格，保證一致性。

實施步驟：
1. 生成規格
- 實作細節：以程式註解/屬性自動生成 OpenAPI。
- 所需資源：Swagger 工具/CI
- 預估時間：1-2 人日

2. 發佈與告警
- 實作細節：版本化、差異比對、破壞性變更警示。
- 所需資源：制品庫/Slack 或郵件
- 預估時間：1 人日

關鍵程式碼/設定：
```text
// Implementation Example（流程）
CI Pipeline:
- Build → Generate OpenAPI → Publish swagger.json
- Diff 與版本標記 → 通知
- 提供穩定 URL 給 Test Runner
```

實際案例：PoC 直接從線上 Swagger 載入規格，確保與後端一致。
實作環境：CI/CD + Swagger 生成。
實測數據：
改善前：人工維護易失真。
改善後：CI 生成，Runner 直接信任規格源。
改善幅度：規格漂移風險顯著降低。

Learning Points（學習要點）
核心知識點：
- Spec 作為契約與制品
- 規格版本與差異比對
- Runner 與 Spec 的引用邏輯

技能要求：
必備技能：CI 基礎、Swagger 產生
進階技能：規格差異檢測與告警

延伸思考：
- 以合同測試鎖住行為一致性？
- 破壞性變更自動阻擋合併？
- 多環境規格切換策略

Practice Exercise（練習題）
基礎練習：在 CI 產生並上傳 swagger.json。
進階練習：加入規格 diff 與警示。
專案練習：建立版本化規格倉庫供 Runner 使用。

Assessment Criteria（評估標準）
功能完整性（40%）：CI 可產出與發布規格
程式碼品質（30%）：可維護的生成設定
效能優化（20%）：產線穩定與快速
創新性（10%）：差異比對與通知方案


## Case #9: 環境控制 Plugin：語系/時區/幣別/使用者上下文

### Problem Statement（問題陳述）
業務場景：API 行為可能受語系、幣別、時區、使用者角色影響。若將此類控制混入測試步驟，將導致案例複雜且難重用。需要獨立的環境控制層，在執行前統一設定。
技術挑戰：在 Runner 中分離「環境」與「測試步驟」，並使報告含有 context 以利追蹤。
影響範圍：案例重用性、可維護性、可追溯性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 環境變數分散在各步驟。
2. 測試與設定耦合，難切換。
3. 報告缺少上下文，難重現。
深層原因：
- 架構層面：缺乏測試環境層。
- 技術層面：無集中上下文管理。
- 流程層面：案例與環境未分離維護。

### Solution Design（解決方案設計）
解決策略：建立 Environment/Context Plugin，先設定 user/token、locale、timezone、currency，再啟動 Test Runner；報告中輸出 context 節點，便於統計與重現。

實施步驟：
1. Context 模型
- 實作細節：定義 shop/user/location 結構。
- 所需資源：資料模型
- 預估時間：0.5 人日

2. 初始與注入
- 實作細節：Runner 啟動時載入；AuthCallback 讀取。
- 所需資源：Plugin 與注入點
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作概念）
public class ApiExecutionContext {
  public string Shop { get; set; }
  public string AccessToken { get; set; }
  public string User { get; set; }
  public string Locale { get; set; } = "zh-TW";
  public string TimeZone { get; set; } = "UTC+8";
  public string Currency { get; set; } = "TWD";
}
```

實際案例：JSON 報告含 context 區塊（user、locale、currency…），可作為查詢維度。
實作環境：同 Case #1。
實測數據：
改善前：環境切換需改動步驟。
改善後：一處設定，多處受益；報告可追蹤。
改善幅度：案例複用度提升，維護成本下降。

Learning Points（學習要點）
核心知識點：
- 測試環境分層
- 上下文注入點設計
- 報告可追蹤性

技能要求：
必備技能：設定管理、序列化
進階技能：多租戶/多使用者測試設計

延伸思考：
- 將 context 與測試資料版本同步？
- 敏感資訊管理（token masking）？
- 跨區域時區一致性測試

Practice Exercise（練習題）
基礎練習：為 Runner 新增 locale/時區設定。
進階練習：報告輸出 context 並可搜尋。
專案練習：支援多使用者批量測試並聚合結果。

Assessment Criteria（評估標準）
功能完整性（40%）：環境可配置並影響執行
程式碼品質（30%）：結構清晰、可測試
效能優化（20%）：初始化與注入開銷可控
創新性（10%）：上下文與報告串接設計


## Case #10: 啟用 FunctionChoiceBehavior.Auto，讓工具自動被選用

### Problem Statement（問題陳述）
業務場景：若未正確配置 Function Calling，自動化測試會退化為純文字對答，無法實際呼叫 API。需要讓 LLM 自動挑選與調用已匯入的 OpenAPI 函式。
技術挑戰：確保模型在適當時機做 tool call 並回填結果。
影響範圍：測試是否可執行、結果真實性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設未開啟自動工具選擇。
2. Prompt 未誘發 tool call。
3. 內部流程不可見，難除錯。
深層原因：
- 架構層面：呼叫通道未正確配置。
- 技術層面：參數設定缺失。
- 流程層面：缺乏運行層日誌。

### Solution Design（解決方案設計）
解決策略：設定 PromptExecutionSettings.FunctionChoiceBehavior.Auto，並在 Prompt 清楚要求「呼叫 API 驗證」，同時開啟 HTTP 日誌輔助除錯。

實施步驟：
1. 啟用 Auto
- 實作細節：以 SK 設定 FunctionChoiceBehavior.Auto()。
- 所需資源：SK
- 預估時間：0.1 人日

2. 除錯日誌
- 實作細節：HttpLogger 啟用，對照日誌與報告。
- 所需資源：自訂 HttpClient
- 預估時間：0.25 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
var settings = new PromptExecutionSettings {
  FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};
var result = await kernel.InvokePromptAsync<string>(prompt, new(settings));
```

實際案例：PoC 中模型可自動選用 CreateCart/GetProducts/AddItemToCart。
實作環境：同 Case #1。
實測數據：
改善前：不會呼叫 API、僅文字回覆。
改善後：自動調用工具並填入真實回應。
改善幅度：可執行性由 0→1。

Learning Points（學習要點）
核心知識點：
- 工具自動選擇機制
- Prompt 與設定聯動
- 日誌對照除錯

技能要求：
必備技能：SK 設定
進階技能：Function 使用痕跡診斷

延伸思考：
- 多工具衝突如何裁決？
- 限制可用函式範圍？
- 執行計畫先行產出（思維鏈→工具）

Practice Exercise（練習題）
基礎練習：在範例中開啟 Auto 後驗證 API 呼叫。
進階練習：限制函式白名單並觀測影響。
專案練習：紀錄工具選擇與結果對照表。

Assessment Criteria（評估標準）
功能完整性（40%）：確實調用工具並返回結果
程式碼品質（30%）：設定簡潔、可維護
效能優化（20%）：避免不必要的工具呼叫
創新性（10%）：工具選擇策略


## Case #11: 三段式 Prompt 編排與報告模板化

### Problem Statement（問題陳述）
業務場景：需要可重用的 Prompt 策略，讓模型按 GWT 執行、產生一致格式報告，並可將用例內容作為外部輸入替換。目標是提高規模化運行與維護效率。
技術挑戰：將規則、用例與輸出格式分離而協作。
影響範圍：可維護性、可移植性、可擴充性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一 Prompt 難以覆蓋規則、用例、輸出三責。
2. 報告格式無模板，難標準化。
3. 用例嵌在 Prompt 中，無法替換。
深層原因：
- 架構層面：Prompt 職責未分層。
- 技術層面：缺少參數化注入。
- 流程層面：無模板化產線。

### Solution Design（解決方案設計）
解決策略：以三段 Message（System 規則、User 用例、User 報告模板）組合，並將 test_case 作為 KernelArguments 注入以利替換；模板固定欄位，保障一致性。

實施步驟：
1. 規則/用例/報告拆分
- 實作細節：三段 Message；用例外部注入。
- 所需資源：Prompt 模板
- 預估時間：0.5 人日

2. 參數化與測試
- 實作細節：多用例替換驗證一致性。
- 所需資源：不同案例集
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
var report = await kernel.InvokePromptAsync<string>(
"""
<message role="system">…GWT 規則…</message>
<message role="user">以下為要執行的測試案例…{{test_case}}…</message>
<message role="user">生成 markdown 格式報告…（表格模板）…</message>
""", new(settings) { ["test_case"] = testCaseMarkdown });
```

實際案例：PoC 以相同模板執行 15 個情境，報告結構一致。
實作環境：同 Case #1。
實測數據：
改善前：報告格式與敘述不一。
改善後：報告結構一致，可程式解析。
改善幅度：可規模化運行。

Learning Points（學習要點）
核心知識點：
- Prompt 分層設計
- 參數化注入
- 報告模板化

技能要求：
必備技能：Prompt 工程
進階技能：模板產線與版本控制

延伸思考：
- 報告模板版本化與相容性？
- 多語系報告模板？
- 模板與 JSON Schema 對齊

Practice Exercise（練習題）
基礎練習：用模板跑 2 個案例。
進階練習：替換模板欄位並確保一致輸出。
專案練習：建立模板版本管理流程。

Assessment Criteria（評估標準）
功能完整性（40%）：多用例輸出一致
程式碼品質（30%）：模板清晰可維護
效能優化（20%）：模板解析與注入高效
創新性（10%）：模板治理策略


## Case #12: 模型與成本配置：用 o4-mini 控延遲與花費

### Problem Statement（問題陳述）
業務場景：Function Calling 常需多輪交互與多次 HTTP 呼叫，若模型過大、回應冗長，會產生高延遲與高成本。目標是在可接受準確度下，壓低單案執行時間與成本。
技術挑戰：在能力與成本間取得平衡，並觀測效益。
影響範圍：測試吞吐量、CI 時間、雲成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 大模型延遲高。
2. Function 回合數多。
3. 回應冗長造成額外 token。
深層原因：
- 架構層面：未對成本/延遲設目標。
- 技術層面：模型選擇與提示控制鬆散。
- 流程層面：無成本追蹤度量。

### Solution Design（解決方案設計）
解決策略：選擇 o4-mini 等中輕量模型，控制 Prompt 與回報格式長度，必要時拆步執行，將每案執行壓到~1 分鐘等級以適配 CI。

實施步驟：
1. 模型選擇與觀測
- 實作細節：以 o4-mini 起跑，記錄時間/成本。
- 所需資源：計費與時序記錄
- 預估時間：持續

2. 提示與報告瘦身
- 實作細節：模板精簡、裁減多餘欄位。
- 所需資源：Prompt 調整
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
.AddOpenAIChatCompletion(
  modelId: "o4-mini",
  apiKey: OPENAI_APIKEY,
  httpClient: HttpLogger.GetHttpClient(false));
```

實際案例：PoC 單案例執行約 1 分鐘完成（含多次 API 呼叫與報告生成）。
實作環境：同 Case #1。
實測數據：
改善前：未優化模型，延遲偏高（預估）。
改善後：o4-mini 控制在 ~1 分鐘級別。
改善幅度：可用於開發期與 CI 的節奏。

Learning Points（學習要點）
核心知識點：
- 模型選擇與成本/延遲
- Prompt/輸出瘦身
- 分段與重試策略

技能要求：
必備技能：基本雲成本意識
進階技能：延遲剖析與優化

延伸思考：
- 批次測試的並行化？
- 模型自動降級/升級策略？
- 針對不同案例選不同模型

Practice Exercise（練習題）
基礎練習：以 o4-mini 執行一案並記錄耗時。
進階練習：精簡報告模板比較耗時。
專案練習：並行跑 10 案觀測吞吐量與成本。

Assessment Criteria（評估標準）
功能完整性（40%）：在限時內完成並正確輸出
程式碼品質（30%）：記錄與監控完善
效能優化（20%）：明顯延遲/成本下降
創新性（10%）：模型/並行策略


## Case #13: 無 EmptyCart API 的前置條件實現

### Problem Statement（問題陳述）
業務場景：用例要求「清空購物車」，實際 API 無對應端點。需要在不改後端的前提下達成等效前置狀態，以確保測試可執行。
技術挑戰：以替代流程達到同等狀態且保持穩定。
影響範圍：案例可執行性、前置一致性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 規格不完整（缺少清空端點）。
2. 直接刪除每項商品成本高且易漏。
3. 既有資料會污染測試。
深層原因：
- 架構層面：狀態初始化未抽象。
- 技術層面：缺少標準前置策略。
- 流程層面：前置需求未入 API 設計。

### Solution Design（解決方案設計）
解決策略：改以「建立新購物車」替代「清空購物車」，保證初始狀態一致；若受限，則列舉項目後逐一刪除。

實施步驟：
1. 建立新購物車
- 實作細節：POST /api/carts/create
- 所需資源：API Spec
- 預估時間：即用

2. 備援：逐項清除
- 實作細節：GET /api/carts/{id} → DELETE items（若有）
- 所需資源：刪除端點
- 預估時間：依數量而定

關鍵程式碼/設定：
```http
// Implementation Example（實作步驟）
POST /api/carts/create  // 回傳全新 cartId
// 備援方案：逐項清除（若規格支援）
GET  /api/carts/{id}
DELETE /api/carts/{id}/items/{itemId}
```

實際案例：PoC 以建立新購物車達成 Given 初始條件。
實作環境：同 Case #1。
實測數據：
改善前：無法保證初始乾淨狀態。
改善後：前置狀態穩定與一致。
改善幅度：案例可執行性顯著提升。

Learning Points（學習要點）
核心知識點：
- 前置條件策略
- 等效狀態達成
- 缺口補齊方法

技能要求：
必備技能：API 巡覽能力
進階技能：冪等性與狀態控制

延伸思考：
- 是否需要「Reset Fixture」端點？
- 對 UI 測試的等效初始策略？
- 測試資料隔離與命名

Practice Exercise（練習題）
基礎練習：以 CreateCart 達成空購物車。
進階練習：實作逐項清空流程。
專案練習：建立通用前置策略模組。

Assessment Criteria（評估標準）
功能完整性（40%）：能可靠達成初始狀態
程式碼品質（30%）：策略清晰、可重用
效能優化（20%）：步驟最少化
創新性（10%）：前置策略設計


## Case #14: PoC 選擇 Console App 而非 MCP 的權衡

### Problem Statement（問題陳述）
業務場景：目標是驗證「Intent→Assertion」核心可行性，若一開始就投入 MCP 與大規模整合，將受限於生態與實作門檻，延誤 PoC。需選擇最輕量路徑快速驗證。
技術挑戰：平衡可擴充性與開發速度。
影響範圍：時程風險、範圍控制、學習曲線。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. MCP 涉及多端整合與協議成本。
2. 非核心問題會佔據開發時間。
3. PoC 目標是核心可行性非產品化。
深層原因：
- 架構層面：過早最佳化。
- 技術層面：堆疊選擇不當。
- 流程層面：目標界定不清。

### Solution Design（解決方案設計）
解決策略：以 .NET Console App + SK 直連 OpenAI、OpenAPI，快速打通流程；將 MCP 等規模化議題留待後續專文與產品化階段處理。

實施步驟：
1. 最小可行架構
- 實作細節：Console App 組合 SK 與模型/Plugin。
- 所需資源：.NET、SK
- 預估時間：1-2 人日

2. 輕量驗證與迭代
- 實作細節：聚焦 Prompt、工具、報告。
- 所需資源：案例集
- 預估時間：持續

關鍵程式碼/設定：
```text
// Implementation Example（策略）
.NET Console App → Semantic Kernel → OpenAPI Plugin → OpenAI ChatCompletion
// 聚焦最短路徑驗證
```

實際案例：PoC 以不到 50 行關鍵碼打通主要環節。
實作環境：同 Case #1。
實測數據：
改善前：若採 MCP 初期設置時間長。
改善後：快速驗證核心路徑可行。
改善幅度：時程風險明顯降低。

Learning Points（學習要點）
核心知識點：
- PoC 範圍控制
- 技術堆疊選擇
- 漸進式擴展

技能要求：
必備技能：最小可行產品思維
進階技能：風險拆解與排程

延伸思考：
- 何時轉向 MCP/產品化？
- 模組化為未來擴展留接口？
- 里程碑切割方式

Practice Exercise（練習題）
基礎練習：以 Console App 打通單案例。
進階練習：抽象化報告與工具層。
專案練習：規劃 MCP 遷移路線圖。

Assessment Criteria（評估標準）
功能完整性（40%）：PoC 能跑通
程式碼品質（30%）：結構簡潔
效能優化（20%）：啟動成本小
創新性（10%）：路徑選擇合理


## Case #15: 測試狀態標準化與失敗分類

### Problem Statement（問題陳述）
業務場景：大量測試時，缺乏統一狀態會造成結果難比較與追蹤。需要標準化狀態碼與欄位，讓失敗可快速定位（起始失敗/執行失敗/斷言失敗）。
技術挑戰：設計簡潔但涵蓋面足夠的分類。
影響範圍：問題定位效率、報警精度、迭代速度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 結果敘述自由，難以聚合。
2. 失敗原因不清，一律「失敗」。
3. 報警容易誤判。
深層原因：
- 架構層面：缺少統一定義。
- 技術層面：報告欄位不一致。
- 流程層面：未形成追蹤鏈。

### Solution Design（解決方案設計）
解決策略：在 Prompt 報告模板中內建四態：start_fail、exec_fail、test_fail、test_pass，並要求在每步驟列明 pass/fail 與說明，最終給出總結狀態。

實施步驟：
1. 狀態定義
- 實作細節：文件化定義各狀態與判準。
- 所需資源：測試準則
- 預估時間：0.25 人日

2. 模板固化
- 實作細節：欄位固定，工具端檢查。
- 所需資源：模板與驗證器
- 預估時間：0.5 人日

關鍵程式碼/設定：
```text
// Implementation Example（模板片段）
**測試結果**: 無法執行(start_fail) | 執行失敗(exec_fail) | 測試不過(test_fail) | 測試通過(test_pass)
```

實際案例：超量購物案例標記為 test_fail，並逐步標示 step1/step2 的 fail 原因。
實作環境：同 Case #1。
實測數據：
改善前：失敗難定位。
改善後：可快速判斷失敗層級與原因。
改善幅度：問題定位效率明顯提升。

Learning Points（學習要點）
核心知識點：
- 失敗分類設計
- 模板化輸出
- 與告警系統的對接

技能要求：
必備技能：測試管理基礎
進階技能：報告校驗器設計

延伸思考：
- 是否需要 error code 與 link to run logs？
- 與缺陷管理系統串接？
- 自動重跑策略（針對 exec_fail）

Practice Exercise（練習題）
基礎練習：為 2 個案例標記四態執行。
進階練習：寫一個狀態校驗器。
專案練習：將不同狀態映射到不同告警通道。

Assessment Criteria（評估標準）
功能完整性（40%）：四態使用正確
程式碼品質（30%）：模板與校驗結構良好
效能優化（20%）：聚合與查詢高效
創新性（10%）：告警與追蹤設計


## Case #16: 全量請求/回應日誌讓測試可追蹤

### Problem Statement（問題陳述）
業務場景：AI 自動執行測試有黑盒風險。需要把每次 API 的 Request/Response、Header（含 Authorization）完整記錄，支援審計與問題追溯。
技術挑戰：在不干擾執行的前提下，收集足夠訊息並與報告對上。
影響範圍：可追蹤性、合規性、故障排查效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏一致的 HTTP 日誌。
2. 認證與上下文不可見。
3. 報告與日誌無鏈接。
深層原因：
- 架構層面：日誌層未標準化。
- 技術層面：HttpClient 未統一註冊。
- 流程層面：調查資料不足。

### Solution Design（解決方案設計）
解決策略：以自訂 HttpClient（如 HttpLogger.GetHttpClient(true)）統一攔截記錄請求/回應，並在報告中附關鍵資訊（cartId、productId、token 摘要）對齊。

實施步驟：
1. 日誌中介
- 實作細節：委派 Handler 記錄 method/url/body/headers。
- 所需資源：HttpClient 工廠
- 預估時間：0.5-1 人日

2. 報告對齊
- 實作細節：在步驟中輸出 request/response 節錄。
- 所需資源：模板調整
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
.AddOpenAIChatCompletion("o4-mini", OPENAI_APIKEY, HttpLogger.GetHttpClient(false));
await kernel.ImportPluginFromOpenApiAsync(... new OpenApiFunctionExecutionParameters {
  HttpClient = HttpLogger.GetHttpClient(true), // 開啟 HTTP 記錄
  AuthCallback = ...
});
```

實際案例：日誌中可見 Authorization: Bearer xxxx 與每次 API 的完整請求/回應。
實作環境：同 Case #1。
實測數據：
改善前：黑盒、難追蹤。
改善後：可精準對照每步驟資料。
改善幅度：故障排除時間顯著縮短。

Learning Points（學習要點）
核心知識點：
- HTTP 日誌與審計
- 報告與日誌對帳
- 資安與遮罩

技能要求：
必備技能：HTTP 客製
進階技能：敏感欄位遮罩、合規

延伸思考：
- Token/PII 遮罩策略？
- 失敗自動回放（replay）？
- 日誌存留與存取控制

Practice Exercise（練習題）
基礎練習：建立可開關的 HTTP 日誌。
進階練習：將日誌和報告連結（RunId）。
專案練習：實作失敗回放工具。

Assessment Criteria（評估標準）
功能完整性（40%）：全請求/回應可追蹤
程式碼品質（30%）：遮罩與結構良好
效能優化（20%）：日誌開銷可控
創新性（10%）：回放與對帳工具


## Case #17: 以單一 Domain Case 橫跨多介面（API/UI/多端）

### Problem Statement（問題陳述）
業務場景：同一商業規則需在 API、Web、Android、iOS 等介面驗證。若每介面各寫一套用例，維護成本高且易不一致。目標是維持 Domain 級案例不變，依介面規格展開步驟。
技術挑戰：將「概念案例」與「介面規格」解耦，以不同 Runner 展開。
影響範圍：測試一致性、覆蓋率、維護成本。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 用例混雜介面細節。
2. 介面差異導致重複與分叉。
3. 規格變動影響用例本體。
深層原因：
- 架構層面：案例層次未分離。
- 技術層面：缺少界面規格與 Runner 映射。
- 流程層面：無跨介面治理。

### Solution Design（解決方案設計）
解決策略：維持 Domain Case（GWT）作為單一真實來源，為各介面提供對應規格（OpenAPI、UI 元件規格等），搭配不同 Runner（API Runner、Browser/Computer Use）展開相同行為驗證。

實施步驟：
1. 分層資產
- 實作細節：Domain 案例庫獨立；介面規格各自維護。
- 所需資源：案例庫、規格庫
- 預估時間：持續

2. 多 Runner 策略
- 實作細節：API Runner 先落地；UI Runner 後續引入。
- 所需資源：Browser Use/Computer Use 等
- 預估時間：分期

關鍵程式碼/設定：
```text
// Implementation Example（流程構想）
Domain Case (GWT)
 + API Spec → API Runner（現已實作）
 + UI Spec  → UI Runner（Browser/Computer Use，規劃中）
```

實際案例：目前先實現 API Runner；UI Runner 為規劃方向，原理一致。
實作環境：SK + OpenAPI（現）、UI Tooling（未來）。
實測數據：
改善前：各端重複撰寫用例。
改善後：案例一次撰寫，多介面展開。
改善幅度：長期維護成本與一致性顯著改善。

Learning Points（學習要點）
核心知識點：
- 用例分層與多 Runner
- 規格化思維
- 跨介面一致性

技能要求：
必備技能：GWT 與規格化
進階技能：UI 自動化工具/Agent

延伸思考：
- UI 規格如何形成可供工具使用的標準？
- Runner 之間的共用模組？
- 介面差異帶來的斷言差異管理

Practice Exercise（練習題）
基礎練習：寫 1 個 Domain Case 與對應 API 步驟。
進階練習：設計同用例的 UI 步驟草案。
專案練習：建立 Domain Case→API/UI 的映射規則。

Assessment Criteria（評估標準）
功能完整性（40%）：案例分層清晰
程式碼品質（30%）：映射規則可落地
效能優化（20%）：避免重複與分叉
創新性（10%）：跨介面統一方法


## Case #18: 測試報告集中化與結構化收斂

### Problem Statement（問題陳述）
業務場景：當案例量擴大（如 15+），若僅有單案 Markdown 報告，團隊無法快速掌握整體通過率、失敗趨勢與高風險模組。需集中化存放並可聚合分析。
技術挑戰：報告結構統一、存取與查詢效率、可視化與告警。
影響範圍：決策速度、風險控管、回歸效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 報告分散、難搜尋。
2. 格式不一、無法聚合。
3. 缺乏可視化與告警連動。
深層原因：
- 架構層面：無集中存放層。
- 技術層面：無結構化資料與索引。
- 流程層面：無週期回顧機制。

### Solution Design（解決方案設計）
解決策略：以 JSON 結構輸出為主，集中存入資料庫/檔案倉，建立聚合任務與 Dashboard，對關鍵狀態（如 test_fail）建立告警規則。

實施步驟：
1. 存放與索引
- 實作細節：按 name/date/version 建檔；或入庫加索引。
- 所需資源：DB/檔案系統
- 預估時間：1 人日

2. 聚合與可視化
- 實作細節：通過率、失敗分佈、Top 失敗端點。
- 所需資源：BI 工具或自製頁面
- 預估時間：1-2 人日

關鍵程式碼/設定：
```text
// Implementation Example（策略）
- 產出 *.json → 存放 /reports/YYYY-MM-DD/{caseId}.json
- 建立匯總 Job → 產出 daily-summary.json → Dashboard 呈現
```

實際案例：PoC 已輸出 JSON，可直接作為集中化的基礎。
實作環境：同 Case #6。
實測數據：
改善前：僅 Markdown，難聚合。
改善後：結構化資料可直接統計與告警。
改善幅度：品質追蹤效率顯著提升。

Learning Points（學習要點）
核心知識點：
- 結構化報告治理
- 指標與可視化
- 告警與 SLO

技能要求：
必備技能：資料建模、簡易 BI
進階技能：趨勢分析與預警

延伸思考：
- 與 Issue 系統自動產生工單？
- 長期趨勢與風險雷達？
- 引入服務品質門檻（品質閘）

Practice Exercise（練習題）
基礎練習：集中存放 JSON 並以腳本匯總。
進階練習：畫出每案例通過率趨勢圖。
專案練習：建立失敗自動告警與鏈接至缺陷管理。

Assessment Criteria（評估標準）
功能完整性（40%）：集中存放與匯總
程式碼品質（30%）：資料結構與命名規則
效能優化（20%）：聚合效率與可擴充性
創新性（10%）：視覺化與告警方案



### 案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #10（Auto 工具啟用）
  - Case #13（前置條件替代）
  - Case #14（PoC 架構權衡）
- 中級（需要一定基礎）
  - Case #2（OpenAPI→Plugin）
  - Case #3（GWT 與防幻覺）
  - Case #4（語義→API 映射）
  - Case #6（雙軌輸出）
  - Case #8（Spec 與 CI）
  - Case #9（環境控制 Plugin）
  - Case #11（三段式 Prompt）
  - Case #12（模型與成本）
  - Case #16（請求/回應日誌）
  - Case #18（報告集中化）
- 高級（需要深厚經驗）
  - Case #1（端到端 Runner）
  - Case #5（OAuth2 無人值守）
  - Case #7（AI Ready API 設計）
  - Case #17（跨介面用例解耦）

2. 按技術領域分類
- 架構設計類：#1, #7, #14, #17
- 效能優化類：#12, #18
- 整合開發類：#2, #4, #5, #8, #9, #10, #11, #13, #16
- 除錯診斷類：#3, #15, #16
- 安全防護類：#5, #16, #9

3. 按學習目標分類
- 概念理解型：#7, #14, #17
- 技能練習型：#2, #10, #11, #13
- 問題解決型：#1, #3, #4, #5, #6, #8, #9, #12, #15, #16, #18
- 創新應用型：#1, #6, #17, #18



### 案例關聯圖（學習路徑建議）
- 先學：
  - Case #10（啟用 Auto 工具）→ 打開工具使用能力的關鍵開關
  - Case #2（OpenAPI→Plugin）→ 確保有可用工具
  - Case #11（三段式 Prompt）→ 建立規則/用例/報告的模板方法
- 進階依賴：
  - Case #13（前置條件策略）→ 支援穩定 Given
  - Case #3（GWT 與防幻覺）→ 確保結果真實可信
  - Case #6（雙軌輸出）→ 為後續集中化鋪路
  - Case #16（請求/回應日誌）→ 建立可追蹤性
- 核心整合：
  - Case #5（OAuth2 無人值守）→ 安全前提
  - Case #9（環境控制 Plugin）→ 穩定上下文
  - Case #1（端到端 Runner）→ 打通 Intent→Assertion
- 工程化與最佳實務：
  - Case #8（Spec 與 CI）→ 規格契約自動化
  - Case #12（模型與成本）→ 控制延遲/成本
  - Case #15（狀態標準化）→ 便於告警與分析
  - Case #18（集中化收斂）→ 團隊層級價值
- 觀念深化與擴展：
  - Case #7（AI Ready API）→ 從根本提升可測性
  - Case #14（PoC→產品化權衡）→ 漸進式落地
  - Case #17（跨介面用例）→ 擴展到 UI/多端

完整學習路徑建議：
1) #10 → #2 → #11 → #13 → #3 → #6 → #16
2) 之後串接 #5、#9，整合成 #1 的端到端 Runner
3) 工程化：#8 → #12 → #15 → #18
4) 架構與擴展：#7 → #14 → #17

此路徑由底層能力到整合落地，再進入工程化與長期架構演進，對應從 PoC 到規模化推廣的實際需求。