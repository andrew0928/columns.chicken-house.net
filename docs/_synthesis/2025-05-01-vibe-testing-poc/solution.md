---
layout: synthesis
title: "從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得"
synthesis_type: solution
source_post: /2025/05/01/vibe-testing-poc/
redirect_from:
  - /2025/05/01/vibe-testing-poc/solution/
postid: 2025-05-01-vibe-testing-poc
---
以下整理自原文，萃取出具教學價值的 16 個問題解決案例。每個案例都包含問題、根因、解決方案與可落地的實作要點，並附帶實作練習與評估標準，適合用於實戰教學、專案練習與能力評估。


## Case #1: 從 Intent 到 Assertion 的 LLM 驅動 API 自動化測試

### Problem Statement（問題陳述）
業務場景：團隊希望將需求驗收標準（AC）與領域情境（Given/When/Then）轉為可執行的 API 測試，避免傳統以人力撰寫測試腳本（Postman/腳本語言）與人工對照回應的繁瑣流程，縮短測試設計到執行的距離，並自動產生報告。  
技術挑戰：讓 LLM 根據高階情境自動決定「打哪個 API、要帶什麼參數、如何判斷結果」。  
影響範圍：測試自動化覆蓋率、需求驗證速度、測試工程維護成本。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 測試「意圖」無法直接執行：傳統自動化工具需要精確步驟與參數。
2. 測試腳本維護成本高：規格或 API 變動時需大量人力調整。
3. 測試回報非結構化：難以系統彙整、統計與追蹤。

深層原因：
- 架構層面：缺少可由工具化（Tool Use）直接理解與執行的接口與規格。
- 技術層面：缺乏 Function Calling 來將 LLM 的推論轉為 API 執行。
- 流程層面：測試案例編寫與系統規格分離，缺少自動對接機制。

### Solution Design（解決方案設計）
解決策略：以 Semantic Kernel 將 OpenAPI 轉為插件（Tool），用三段訊息模板指導 LLM：System（測試 SOP）、User（情境輸入）、User（報告格式），並強制僅以真實 API 回應作為判斷依據，輸出可讀報告與機器可讀 JSON。

實施步驟：
1. 建立 Kernel 與模型
- 實作細節：AddOpenAIChatCompletion 指定 o4-mini。
- 所需資源：Semantic Kernel、OpenAI API Key。
- 預估時間：0.5 小時

2. 將 OpenAPI 匯入為插件
- 實作細節：ImportPluginFromOpenApiAsync 暴露 16 個端點為工具。
- 所需資源：Swagger URL。
- 預估時間：0.5 小時

3. 設定 Prompt 與 Auto Function Choice
- 實作細節：三段訊息模板 + FunctionChoiceBehavior.Auto。
- 所需資源：Prompt 範本。
- 預估時間：1 小時

4. 產出報告（Markdown + JSON）
- 實作細節：Structured Output 與報告模板。
- 所需資源：LLM 輸出解析器。
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 建立 Kernel + 模型
var builder = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("o4-mini", OPENAI_APIKEY, HttpLogger.GetHttpClient(false));
var kernel = builder.Build();

// 匯入 OpenAPI 規格為 Plugin (Tool)
await kernel.ImportPluginFromOpenApiAsync(
    pluginName: "andrew_shop",
    uri: new Uri("https://andrewshopoauthdemo.azurewebsites.net/swagger/v1/swagger.json"),
    executionParameters: new OpenApiFunctionExecutionParameters {
        EnablePayloadNamespacing = true,
        HttpClient = HttpLogger.GetHttpClient(true),
        AuthCallback = (req, _) => {
            req.Headers.Add("Authorization", $"Bearer {userAccessToken}");
            return Task.CompletedTask;
        }
    }
);

// 啟用自動工具選擇並執行 Prompt
var settings = new PromptExecutionSettings {
    FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};
var report = await kernel.InvokePromptAsync<string>(promptTemplate, new(settings){ ["test_case"]=caseText });
```

實際案例：購物車「單一商品上限 10 件」的測試，由 AI 自動決定呼叫 create cart、查產品、加購物車、查購物車，並比對斷言。  
實作環境：.NET Console App、Semantic Kernel、OpenAI o4-mini、AndrewShop API（Swagger）。  
實測數據：
- 改善前：需人工撰寫腳本與維護步驟。  
- 改善後：PoC 僅以 3 則訊息 + OpenAPI Tool 完成執行，單案例約 60 秒。  
- 改善幅度：測試腳本撰寫時間降低為「只寫情境文本」，自動化覆蓋 15 個案例的啟動成本顯著下降。

Learning Points（學習要點）
核心知識點：
- Function Calling/Tool Use 將「情境→執行→斷言」打通
- Prompt 分工（SOP/資料/格式）降低幻覺與偏軌
- 報告雙軌輸出（Markdown+JSON）同時滿足人/系統

技能要求：
- 必備技能：REST、OpenAPI、基本 Prompt 設計
- 進階技能：Semantic Kernel 工具鏈、LLM 報告結構化輸出

延伸思考：
- 如何適配 UI 測試（Browser/Computer Use）？
- LLM 決策穩定性與成本的平衡？
- 大量案例的排程與資源控管？

Practice Exercise（練習題）
- 基礎練習：以 1 則 Given/When/Then 驅動 1 個 API 測試，輸出 Markdown 報告（30 分鐘）
- 進階練習：同時輸出 JSON 結構化結果，包含步驟/狀態/說明（2 小時）
- 專案練習：接上你司 API 的 Swagger，自動化 10+ 案例與彙整儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能從情境自動執行並產生報告
- 程式碼品質（30%）：模組化、錯誤處理、可維護性
- 效能優化（20%）：單案例時延與 API 呼叫冪等控制
- 創新性（10%）：多格式輸出、可插拔的報告與環境控制


## Case #2: 用領域層級 Given/When/Then 取代技術細節腳本

### Problem Statement（問題陳述）
業務場景：產品經理與測試人員希望描述「要測什麼」而非「怎麼測」，用 BDD（Given/When/Then）寫出購物車行為規則，降低規格變動時對測試文本的影響，並保留充分的商業語意以利審核。  
技術挑戰：情境敘述需能被 LLM 轉譯為 API 操作序列與斷言。  
影響範圍：跨角色溝通效率、測試可讀性與穩定性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 測試文件過度耦合 API 細節導致頻繁重寫。
2. 團隊偏向「展開步驟」而忽略「該測什麼」。
3. UI/API 異動造成測試資產快速折舊。

深層原因：
- 架構層面：未區分「領域測試案例」與「介面規格」。
- 技術層面：缺少讓 LLM 將情境落地的 Tool Use。
- 流程層面：缺少 reviewer 對情境本身的檢視標準。

### Solution Design（解決方案設計）
解決策略：以 BDD 語法撰寫「領域層級」用例，隔離 UI/API 細節，並將其作為 Test Runner 唯一輸入，再由 LLM + OpenAPI 決定具體操作，確保測試資產「穩定、可審核、可遷移」。

實施步驟：
1. 編寫領域用例
- 實作細節：使用 Given/When/Then，只含商業規則。
- 所需資源：領域知識、AC。
- 預估時間：每案 10-20 分鐘

2. 用例審核流程
- 實作細節：由 PM/QA/架構師共審，確認無技術耦合。
- 所需資源：審核清單。
- 預估時間：每批 30 分鐘

關鍵程式碼/設定：
```plaintext
Given:
  - 測試前請清空購物車
  - 指定測試商品: 可口可樂
When:
  - 嘗試加入 11 件指定商品
  - 檢查購物車內容
Then:
  - step 1 應回 400 Bad Request（超過 10）
  - step 2 購物車應為空
```

實際案例：上例作為 Runner 的輸入，LLM 會自動決定 create cart、查產品、加購物車、查購物車與 Then 斷言。  
實作環境：文本文件 + Test Runner。  
實測數據：
- 改善前：測試文件常綁參數與端點寫法。
- 改善後：僅描述規則與預期；API/UI 變更時，案例多半無需改動。
- 改善幅度：案例文本修改次數顯著下降（以場景重用計，可重用至 API/UI 多介面）。

Learning Points
- BDD 文本是 AI 轉譯的最佳起點
- 案例與規格解耦提高資產壽命
- 案例審核聚焦「規則正確性」

Practice Exercise
- 基礎：為另一個購物規則寫 1 則 BDD（30 分鐘）
- 進階：設計 5 則 BDD 覆蓋正反案例（2 小時）
- 專案：把現有 API 測試腳本改寫為 BDD 集合（8 小時）

Assessment Criteria
- 功能完整性：BDD 能被 Runner 正確執行
- 程式碼品質：文本清晰、無技術耦合
- 效能優化：NA
- 創新性：用例可遷移至 UI 測試


## Case #3: 用 OpenAPI 一鍵匯入工具，替代 16 個端點包裝

### Problem Statement（問題陳述）
業務場景：現有 API 有 16 個端點，傳統作法需逐一包裝為可呼叫的函式/SDK，耗時且易錯。希望以最小工時讓 LLM 能直接使用所有 API。  
技術挑戰：自動將 Swagger 轉為可被 LLM 使用的工具，並正確處理驗證與命名空間。  
影響範圍：開發效率、錯誤率、維護性。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 手動包裝 API 端點繁瑣且易漏。
2. 需同步維護函式簽名與 Swagger。
3. 權杖與通訊客戶端須一致控制。

深層原因：
- 架構層面：缺少「規格即工具」的整合路徑。
- 技術層面：OpenAPI 解析與函式生成難度高。
- 流程層面：文件/程式不同步導致工具失效。

### Solution Design
解決策略：使用 Semantic Kernel 的 ImportPluginFromOpenApiAsync，直接把 Swagger 轉成 Tool，10 行內完成，並在 AuthCallback 統一掛 Token。

實施步驟：
1. 取得公開 Swagger URL
- 實作細節：確認對外可取用的 v1 文檔。
- 所需資源：API 主機。
- 預估時間：10 分鐘

2. 呼叫 ImportPluginFromOpenApiAsync
- 實作細節：EnablePayloadNamespacing、HttpClient、AuthCallback。
- 所需資源：Semantic Kernel。
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
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
    }
);
```

實際案例：一鍵暴露 16 個購物車相關 API 作為 Tool。  
實作環境：.NET、Semantic Kernel、OpenAPI。  
實測數據：
- 改善前：需為 16 端點逐一撰寫 wrapper。
- 改善後：10 行內完成工具化，立即可被 LLM 使用。
- 改善幅度：工具包裝工時降低 >90%，出錯面減少。

Learning Points
- OpenAPI 可直接變成 Tool，降低 Glue Code
- AuthCallback 統一處理權杖
- Namespacing 避免參數衝突

Practice Exercise
- 基礎：將你的 Swagger 匯入為 Plugin（30 分鐘）
- 進階：加入動態 AuthCallback 與多環境切換（2 小時）
- 專案：對比手工包裝與自動匯入的工時差異（8 小時）

Assessment Criteria
- 功能完整性：Tool 全數可呼叫、簽名正確
- 程式碼品質：最少樣板、易維護
- 效能優化：初始化時間與失敗回復策略
- 創新性：自動熱更新規格


## Case #4: 防止 LLM 幻覺，強制「只接受真實 API 回應」

### Problem Statement
業務場景：為確保測試可信度，必須禁止 LLM 生成「看起來正確」的回應，僅能依據實際 HTTP Response 判斷。  
技術挑戰：LLM 容易憑經驗補齊或生成 JSON；需要策略性 Prompt 與可驗證的網路日誌。  
影響範圍：測試準確度、誤報/漏報、合規性。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. LLM 具生成能力，可能省略實呼叫。
2. 測試指令未明確禁止「猜結果」。
3. 缺乏可核對的請求/回應證據。

深層原因：
- 架構層面：未將網路層證據納入報告。
- 技術層面：未設計反幻覺的 System Prompt。
- 流程層面：未建立「無實呼叫即失敗」的準則。

### Solution Design
解決策略：System Prompt 明確規範「所有 request/response 只能來自真實呼叫」，搭配 HTTP 日誌（HttpLogger）留存證據，報告內附上 Request/Response。

實施步驟：
1. 設計 Anti-Fabrication System Prompt
- 實作細節：明確禁止生成，要求逐步列出 API 與回應。
- 所需資源：Prompt 模板。
- 預估時間：30 分鐘

2. 開啟 HTTP 日誌
- 實作細節：自訂 HttpClient，完整記錄 request/response。
- 所需資源：HttpLogger。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```plaintext
System Prompt（節錄）：
所有標示 api 的 request / response 內容，請勿直接生成，
或啟用任何 cache 機制替代直接呼叫 api。我只接受真正呼叫 api 取得的 response。
```

實際案例：報告中每個步驟都有 request/response，並與日誌可交叉驗證。  
實作環境：Semantic Kernel + 自訂 HttpClient。  
實測數據：
- 改善前：可能出現「以為有呼叫其實沒呼叫」的假陽性。
- 改善後：每步驟皆可追溯，幻覺機率大幅下降。
- 改善幅度：測試可信度顯著提升（以「必須有日誌證據」為判定門檻）。

Learning Points
- System Prompt 可成為測試遵循的「規章」
- 證據導向的報告能被審核與稽核
- 工具化與日誌化是反幻覺的兩大利器

Practice Exercise
- 基礎：把 Request/Response 也輸出到報告（30 分鐘）
- 進階：加入 request-id 對應到 HTTP 日誌（2 小時）
- 專案：建立「無日誌即判 fail」的驗證器（8 小時）

Assessment Criteria
- 功能完整性：任何步驟未呼叫即標示失敗
- 程式碼品質：日誌易讀、可關聯
- 效能優化：日誌量控與旋轉
- 創新性：自動附證據附件（如 cURL）  


## Case #5: API 缺少 EmptyCart，如何仍完成「清空購物車」

### Problem Statement
業務場景：案例要求「清空購物車」，API 沒有 EmptyCart 端點。希望仍能以既有端點達成等效效果。  
技術挑戰：在不改後端的情況下，以組合式流程實現「清空」。  
影響範圍：案例可執行性、覆蓋率。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. Spec 缺少 EmptyCart。
2. 測試需依賴購物車為空的前置狀態。
3. 用例要求通用性與穩定性。

深層原因：
- 架構層面：API 粒度與用例不完全對齊。
- 技術層面：需以現有端點合成目標狀態。
- 流程層面：前置條件設計缺少替代方案。

### Solution Design
解決策略：用 CreateCart 取代 EmptyCart，並以 GetProducts 查出指定商品的 productId 供後續使用。

實施步驟：
1. 建立新購物車
- 實作細節：POST /api/carts/create
- 所需資源：andrew_shop Tool
- 預估時間：5 分鐘

2. 取得商品並定位指定品項
- 實作細節：GET /api/products → 過濾「可口可樂」
- 所需資源：andrew_shop Tool
- 預估時間：5 分鐘

關鍵程式碼/設定：
```plaintext
POST /api/carts/create
GET  /api/products  // 從清單挑出「可口可樂」，記下 productId 用於後續步驟
```

實際案例：Given 階段完成「空購物車 + 已知 productId」。  
實作環境：OpenAPI Plugin + LLM 決策。  
實測數據：
- 改善前：缺少 EmptyCart 造成用例無法落地。
- 改善後：以 CreateCart 等效滿足需求。
- 改善幅度：用例可執行率由 0% → 100%（此前置條件）。

Learning Points
- 以「狀態導向」拆解前置條件
- 用既有 API 組合出等效狀態
- 用例不必等於 API 名稱

Practice Exercise
- 基礎：為另一個缺功能的前置條件設計替代流程（30 分鐘）
- 進階：用 LLM 自動挑選替代端點並說明理由（2 小時）
- 專案：建立前置條件模式庫（8 小時）

Assessment Criteria
- 功能完整性：能完成前置狀態
- 程式碼品質：流程簡潔、可重用
- 效能優化：最少 API 呼叫
- 創新性：自動化檢測可替代路徑


## Case #6: OAuth2 互動式登入在自動測試中的處理

### Problem Statement
業務場景：API 使用 OAuth2，需要互動式登入取得 Access Token；自動化測試需在無人工介入下穩定執行。  
技術挑戰：如何在 Tool Use 流程中篩入權杖，確保每次呼叫都帶正確 Authorization header。  
影響範圍：測試可用性、安全性。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. OAuth2 正常需跳瀏覽器登入。
2. 測試流程無法每次人工輸入。
3. 權杖需安全且動態地注入每個請求。

深層原因：
- 架構層面：認證流程與測試流程耦合。
- 技術層面：權杖需由工具層統一處理。
- 流程層面：環境控制責任不清。

### Solution Design
解決策略：在 ImportPluginFromOpenApi 時提供 AuthCallback，於 HTTP 層統一注入 Authorization: Bearer <token>；將「指定 user」視為測試環境設定而非測試步驟。

實施步驟：
1. 取得測試用使用者的 Access Token
- 實作細節：前置流程取得 token（或以自動方式）。
- 所需資源：身分系統。
- 預估時間：視環境而定（PoC 30 分鐘）

2. 在 AuthCallback 注入 Token
- 實作細節：所有 API 呼叫自動帶入。
- 所需資源：Semantic Kernel
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
AuthCallback = (request, cancel) => {
    request.Headers.Add("Authorization", $"Bearer {userAccessToken}");
    return Task.CompletedTask;
}
```

實際案例：日誌中每次 API 皆帶不同 token，證明每輪測試均經過完整認證。  
實作環境：OpenAPI Plugin + OAuth2。  
實測數據：
- 改善前：需人工登入，不可持續化。
- 改善後：100% 呼叫自動帶權杖，無人工介入。
- 改善幅度：自動化可用度由低 → 高（可無人值守）。

Learning Points
- 認證屬「環境控制」非「測試步驟」
- 權杖應由工具層統一注入，避免洩漏與遺漏
- 對外顯示最少認證細節，聚焦行為測試

Practice Exercise
- 基礎：將固定 token 注入每次呼叫（30 分鐘）
- 進階：支援多 user/多租戶切換（2 小時）
- 專案：建立環境控制 Plugin（locale/currency/timezone/user）（8 小時）

Assessment Criteria
- 功能完整性：全呼叫帶權杖
- 程式碼品質：權杖管理不外洩、可替換
- 效能優化：權杖更新與快取策略
- 創新性：環境模板化管理


## Case #7: 讓 LLM 自動處理跨步驟參數與狀態傳遞

### Problem Statement
業務場景：多步驟測試需跨步驟傳遞 cartId、productId 等參數，傳統腳本需手動變數管理。  
技術挑戰：以 Tool Use 將「查到的值」自動餵入後續 API，避免人工 Glue Code。  
影響範圍：腳本維護成本、易錯性。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 多端點之間存在資料依賴。
2. 傳統測試需手寫變數綁定。
3. 規格變動導致變數綁定脆弱。

深層原因：
- 架構層面：缺乏可交由對話狀態維持的抽象。
- 技術層面：未知如何將 tool 回傳值注入下一個 tool。
- 流程層面：案例與具體參數相互污染。

### Solution Design
解決策略：使用 SK 的 Auto Function Choice，讓模型在對話狀態中保存回傳資料並動態組裝下一個 request payload；Prompt 只描述意圖，不指定參數。

實施步驟：
1. 啟用 FunctionChoiceBehavior.Auto
- 實作細節：由模型自行挑選工具並串接輸入。
- 所需資源：Semantic Kernel。
- 預估時間：10 分鐘

2. 在報告中印出每步的 Request/Response
- 實作細節：可驗證模型有正確傳值。
- 所需資源：報告模板。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
var settings = new PromptExecutionSettings {
    FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};
```

實際案例：GetProducts 取得「可口可樂」的 id=2，後續 AddItemToCart 自動帶入 productId=2。  
實作環境：SK + OpenAPI Plugin + 報告模板。  
實測數據：
- 改善前：需手工管理變數。
- 改善後：0 行 Glue Code，參數自動傳遞。
- 改善幅度：Glue Code 減少接近 100%。

Learning Points
- 對話狀態即可作為「流程上下文」
- 報告中的 request/response 是最佳驗證
- 提示語應避免硬編參數

Practice Exercise
- 基礎：跨兩步驟傳遞一個參數（30 分鐘）
- 進階：三步驟以上多參數傳遞（2 小時）
- 專案：建立可視化「參數流向圖」（8 小時）

Assessment Criteria
- 功能完整性：正確傳遞所有依賴參數
- 程式碼品質：無硬編參數
- 效能優化：最小化往返次數
- 創新性：參數血緣追蹤


## Case #8: 使用 Then 斷言捕捉未實作的商業規則

### Problem Statement
業務場景：規格要求「同商品最多 10 件」，實際 API 未實作此規則。需要在測試中準確判斷「不符合規格」而非「測試錯誤」。  
技術挑戰：將實際行為與規格期望清楚對照，分類為 test_fail。  
影響範圍：需求驗證、產品品質迭代。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. API 尚未落實規則。
2. 用例已明訂預期。
3. 實測結果與預期不符。

深層原因：
- 架構層面：需求與實作存在落差。
- 技術層面：需要一致的失敗分類規則。
- 流程層面：TDD 思維尚未貫徹。

### Solution Design
解決策略：Then 階段僅比對實測與期望，將此用例標示為 test_fail（非執行或起始失敗），並於報告中清楚描述差異與影響。

實施步驟：
1. 設計失敗分類字彙
- 實作細節：start_fail/exec_fail/test_fail/test_pass。
- 所需資源：報告模板。
- 預估時間：20 分鐘

2. 於報告產生器中映射
- 實作細節：Then 結果直出 test_fail。
- 所需資源：LLM 報告描述。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```plaintext
Then:
- 預期 step 1 回 400，但實際回 200 → test_fail
- 預期購物車為空，但仍含 11 件 → test_fail
```

實際案例：案例最終標示 test_fail，說明「規則未落實」。  
實作環境：Runner 報告模板。  
實測數據：
- 改善前：失敗原因常被混淆。
- 改善後：能分辨「規格未落實」與「測試執行失敗」。
- 改善幅度：失敗歸因精確度顯著提升。

Learning Points
- 失敗分類是測試治理的基礎
- Then 的角色是「驗收比對」非「執行」
- 報告必須可讀、可追溯

Practice Exercise
- 基礎：為另一個規則寫 Then 斷言（30 分鐘）
- 進階：加入多個斷言點與聚合結論（2 小時）
- 專案：失敗分類對應看板（8 小時）

Assessment Criteria
- 功能完整性：分類準確、結論清晰
- 程式碼品質：模板化輸出一致
- 效能優化：NA
- 創新性：根因自動摘要


## Case #9: 雙軌報告：Markdown（給人）＋ JSON（給系統）

### Problem Statement
業務場景：單純 Markdown 報告無法被系統彙整與統計；需要結構化結果供儀表板與警示。  
技術挑戰：在不犧牲可讀性的前提，輸出機器友好的結構化資料。  
影響範圍：測試治理、自動化運維、品質量化。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. Markdown 難以程式解析。
2. 測試量大時無法彙總。
3. 缺少統一 JSON Schema。

深層原因：
- 架構層面：沒有報告結構標準。
- 技術層面：LLM 需產生可驗證的 JSON。
- 流程層面：缺少彙整與儀表板。

### Solution Design
解決策略：同時產出 Markdown 與 JSON；JSON 包含 name/result/context/steps 等欄位，便於系統整合。

實施步驟：
1. 設計 JSON Schema（邏輯）
- 實作細節：name/result/context/steps。
- 所需資源：Schema 文件。
- 預估時間：30 分鐘

2. 在 Prompt 中要求雙輸出
- 實作細節：Markdown + JSON 區塊。
- 所需資源：Prompt 模板。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```json
{
  "name": "TC-05 (非法上界)",
  "result": "test_fail",
  "comments": "AddItemToCart 未回傳 400，且購物車不為空",
  "context": { "shop":"shop123", "user":{ "access_token":"***", "user":"andrew" } },
  "steps": [
    { "api": "CreateCart", "request":{}, "response":{"id":57,"lineItems":[]},"test-result":"pass" },
    { "api": "GetProducts", "request":{}, "response":[{"id":2,"name":"可口可樂® 350ml"}], "test-result":"pass" },
    { "api": "AddItemToCart", "request":{"id":57,"productId":2,"qty":11}, "response":{...}, "test-result":"fail"},
    { "api": "GetCart", "request":{"id":57}, "response":{...}, "test-result":"fail" }
  ]
}
```

實際案例：PoC 同步輸出兩種格式，便於人/系統各取所需。  
實作環境：同 Case #1。  
實測數據：
- 改善前：無法機器彙整。
- 改善後：100% 可解析 JSON，可直接入庫與告警。
- 改善幅度：報告可用性大幅提升。

Learning Points
- 報告是產品化關鍵：給人/給機器雙滿足
- JSON 結構應穩定且可演進
- 結構化輸出可搭配 Schema 驗證

Practice Exercise
- 基礎：把現有 Markdown 報告加上 JSON 區塊（30 分鐘）
- 進階：撰寫匯入器與儀表板原型（2 小時）
- 專案：與 CI 整合，自動彙總與告警（8 小時）

Assessment Criteria
- 功能完整性：雙輸出一致無偏差
- 程式碼品質：JSON 結構清楚、向後相容
- 效能優化：報告大小與壓縮
- 創新性：Schema 驗證與版本管理


## Case #10: 用 FunctionChoiceBehavior.Auto 降低工具編排複雜度

### Problem Statement
業務場景：手動決定每一步要用哪個 Tool、如何回填參數，維護成本高且容易出錯。  
技術挑戰：需要讓模型自動判斷何時用何工具、如何串參數。  
影響範圍：開發效率、測試穩定度。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 手工 orchestration 容易遺漏。
2. 端點數多時流程複雜。
3. 規格變動需要重寫流程。

深層原因：
- 架構層面：未善用模型自身的工具規劃能力。
- 技術層面：缺少 Auto 模式。
- 流程層面：流程硬編碼。

### Solution Design
解決策略：啟用 FunctionChoiceBehavior.Auto，交由模型決定工具與參數注入，程式碼只負責順序與輸出。

實施步驟：
1. 建立設定
- 實作細節：PromptExecutionSettings 中指定 Auto。
- 所需資源：SK API。
- 預估時間：10 分鐘

2. 驗證多步驟案例
- 實作細節：檢查 request/response 正確性。
- 所需資源：測試用例。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
var settings = new PromptExecutionSettings {
    FunctionChoiceBehavior = FunctionChoiceBehavior.Auto()
};
```

實際案例：LLM 自行選擇 create cart → get products → add → get cart。  
實作環境：同前。  
實測數據：
- 改善前：需自行 orchestrate 多步驟。
- 改善後：模型自動編排，維護負擔下降。
- 改善幅度：編排樣板碼下降 >80%。

Learning Points
- Auto 模式是 Tool Use 的加速器
- 報告中的證據用於驗證 Auto 決策
- Prompt 需明確限制與期望

Practice Exercise
- 基礎：以 Auto 模式完成兩步驟測試（30 分鐘）
- 進階：引導模型選擇特定工具順序（2 小時）
- 專案：支援多 Plugin 並行決策（8 小時）

Assessment Criteria
- 功能完整性：能正確完成流程
- 程式碼品質：低耦合、易調整
- 效能優化：減少無效工具嘗試
- 創新性：Auto 決策可視化


## Case #11: 三段式 Prompt（SOP/用例/報告）提升可控性

### Problem Statement
業務場景：LLM 容易偏題或產出不可用報告，需要一個高可控的 Prompt 佈局。  
技術挑戰：將規範、資料與輸出格式清楚分工。  
影響範圍：輸出一致性、可重現性。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 混雜的 Prompt 導致模型混淆。
2. 報告格式不穩定。
3. SOP 缺失導致執行尺度不一。

深層原因：
- 架構層面：Prompt 未模組化。
- 技術層面：缺少「格式驅動輸出」。
- 流程層面：無明確對話角色分工。

### Solution Design
解決策略：以 System（SOP）、User（用例）、User（報告範本）三段式訊息模板，並用變數注入用例。

實施步驟：
1. 設計 SOP
- 實作細節：Given/When/Then 的執行準則與失敗分類。
- 所需資源：Prompt 文檔。
- 預估時間：30 分鐘

2. 報告模板化
- 實作細節：欄位與表格格式固定。
- 所需資源：模板。
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
var report = await kernel.InvokePromptAsync<string>(
"""
<message role="system">…SOP 與反幻覺規則…</message>
<message role="user">以下為要執行的測試案例…</message>
<message role="user">生成 markdown 格式的測試報告…</message>
""", new(settings){ ["test_case"]=caseText });
```

實際案例：PoC 報告重現性高，格式一致。  
實作環境：SK Prompt Template。  
實測數據：
- 改善前：輸出品質不穩。
- 改善後：報告穩定一致，便於自動解析。
- 改善幅度：重試次數明顯下降。

Learning Points
- 角色分工讓模型「有上下文的紀律」
- 報告模板是輸出品質保證
- 變數注入利於自動化

Practice Exercise
- 基礎：把你的 SOP 寫成 System Prompt（30 分鐘）
- 進階：加入報告欄位與分類規則（2 小時）
- 專案：一鍵替換多種 SOP（回歸/壓測/安全）（8 小時）

Assessment Criteria
- 功能完整性：輸出完整且一致
- 程式碼品質：模板清楚、可維護
- 效能優化：NA
- 創新性：多語系報告模板


## Case #12: AI Ready 的領域驅動 API 設計，避免 CRUD 陷阱

### Problem Statement
業務場景：若 API 只提供 CRUD，商業規則下放到呼叫端，導致 LLM 難以掌控正確流程與資料一致性。  
技術挑戰：讓商業語意封裝在 API 中，使 LLM 容易理解與正確執行。  
影響範圍：測試穩定性、流程可控性、AI 友好度。  
複雜度評級：高

### Root Cause Analysis
直接原因：
1. CRUD 導致行為分散。
2. 商業規則無 API 級封裝。
3. 測試步驟容易發散且難以驗證。

深層原因：
- 架構層面：缺乏領域導向的 API 設計。
- 技術層面：語意貧乏的端點讓 LLM 難決策。
- 流程層面：無「AI Ready」的設計標準。

### Solution Design
解決策略：以領域語意命名與行為化端點設計（如 AddItemToCart、CreateCart），搭配精準 Swagger 描述副作用與約束，讓 LLM 易於 Tool Use。

實施步驟：
1. 盤點與重構端點
- 實作細節：將 CRUD 重構為行為語意端點。
- 所需資源：API 設計準則。
- 預估時間：視系統而定

2. 強化 OpenAPI 描述
- 實作細節：描述欄位語意、錯誤碼、範例。
- 所需資源：Swagger 設定。
- 預估時間：數天

關鍵程式碼/設定：
```plaintext
// 將「/carts/{id}/items (POST)」清楚描述為「加入指定商品到購物車」並定義約束/錯誤碼
```

實際案例：Andrew Shop 的行為式端點使 LLM 能直接串接流程。  
實作環境：OpenAPI + 文檔治理。  
實測數據：
- 改善前：流程發散、依賴呼叫端判斷。
- 改善後：LLM 可可靠推理與執行。
- 改善幅度：流程可控性大幅提升（定性）。

Learning Points
- AI Ready = 語意豐富的行為式 API
- OpenAPI 是給 AI 的 Prompt
- 測試與設計相輔相成

Practice Exercise
- 基礎：把 1 個 CRUD 端點改為行為式（30 分鐘）
- 進階：強化 3 個端點的 Swagger 描述（2 小時）
- 專案：為整個子域建立 AI Ready 準則（8 小時）

Assessment Criteria
- 功能完整性：端點語意完整
- 程式碼品質：文檔精準、例子齊全
- 效能優化：NA
- 創新性：設計規範可複製


## Case #13: 精準 OpenAPI 與 CI 產出，否則無法 Tool Use

### Problem Statement
業務場景：若 Swagger 與實作不同步，LLM 將無法正確呼叫 API；測試自動化會變成製造問題。  
技術挑戰：維持 Swagger 精準、可持續且可被工具讀取。  
影響範圍：整體可用性、準確性。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 人工維護 Swagger 容易落差。
2. 開發期需頻繁測試。
3. Tool Use 依賴精準規格。

深層原因：
- 架構層面：Spec 與 Code 分離。
- 技術層面：缺少 CI 產出與發布。
- 流程層面：無「規格即產品」的治理。

### Solution Design
解決策略：將 Swagger 產出與發佈納入 CI，提供穩定 URL 給 Runner 匯入；以「規格不準 = 測試不跑」作為守門。

實施步驟：
1. CI 產出 Swagger JSON
- 實作細節：Build 成功即發佈 swagger.json。
- 所需資源：CI 腳本。
- 預估時間：半天

2. Runner 以 URL 匯入 Tool
- 實作細節：ImportPluginFromOpenApiAsync 指向固定 URL。
- 所需資源：同 Case #3。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
await kernel.ImportPluginFromOpenApiAsync("andrew_shop",
    new Uri("https://.../swagger/v1/swagger.json"), new OpenApiFunctionExecutionParameters { ... });
```

實際案例：PoC 直接使用雲端 Swagger URL，測試即時可用。  
實作環境：CI + Swagger Host。  
實測數據：
- 改善前：規格錯位導致測試失效。
- 改善後：規格與程式同步，工具穩定。
- 改善幅度：測試可用度顯著提升（定性）。

Learning Points
- 規格不準寧可不測，避免錯誤結論
- 規格 URL 是測試關鍵資產
- 規格要素（錯誤碼/範例）決定 LLM 表現

Practice Exercise
- 基礎：提供穩定的 swagger.json URL（30 分鐘）
- 進階：CI 失敗時阻擋規格發布（2 小時）
- 專案：規格變更通知 Runner（8 小時）

Assessment Criteria
- 功能完整性：規格與實作一致
- 程式碼品質：CI 腳本可靠
- 效能優化：NA
- 創新性：規格版本化與回滾


## Case #14: 可稽核的 HTTP 呼叫與可視化步驟證據

### Problem Statement
業務場景：需要向團隊證明「AI 真的有呼叫 API 且照流程走」。  
技術挑戰：提供可視化 HTTP 日誌與步驟表格化輸出。  
影響範圍：信任、審計、問題定位。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 測試由 AI 執行，需證據提高信任。
2. BUG 需快速定位哪個步驟失敗。
3. 需對應 Request/Response 與報告。

深層原因：
- 架構層面：少量可視化設計。
- 技術層面：日誌與報告關聯不足。
- 流程層面：審核需「看得見」證據。

### Solution Design
解決策略：使用 HttpLogger 記錄，報告中列出表格化步驟（API/Request/Response/結果/說明），讓人可快速對照。

實施步驟：
1. 啟用 HttpLogger
- 實作細節：在 Plugin 與 Kernel 客戶端都使用。
- 所需資源：自訂 HttpClient。
- 預估時間：30 分鐘

2. 報告表格化
- 實作細節：Given/When 各有步驟表格。
- 所需資源：報告模板。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
.AddOpenAIChatCompletion("o4-mini", OPENAI_APIKEY, HttpLogger.GetHttpClient(false));
executionParameters.HttpClient = HttpLogger.GetHttpClient(true);
```

實際案例：文中貼圖顯示 Given/When 每步呼叫內容。  
實作環境：同前。  
實測數據：
- 改善前：無法證明是否有呼叫。
- 改善後：一眼看出每步請求與回應。
- 改善幅度：問題定位時間大幅縮短（定性）。

Learning Points
- 可視化證據提升信任
- 表格化讓跨角色讀者都能理解
- HTTP 日誌對應報告欄位

Practice Exercise
- 基礎：在報告加入 Request/Response 摘要（30 分鐘）
- 進階：提供 cURL 重現片段（2 小時）
- 專案：建立呼叫時序圖（8 小時）

Assessment Criteria
- 功能完整性：每步均有證據
- 程式碼品質：日誌具辨識度
- 效能優化：日誌量控
- 創新性：一鍵重現工具


## Case #15: 模型選型與性能：o4-mini 約 1 分鐘完成單案例

### Problem Statement
業務場景：測試需要在合理時間內完成；模型要兼顧工具使用能力與成本。  
技術挑戰：在 reasoning 能力與延遲之間取捨。  
影響範圍：CI 時延、成本、吞吐量。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 模型越大越慢。
2. 測試步驟多、端點多。
3. 成本與效能需要平衡。

深層原因：
- 架構層面：未建立模型選型準則。
- 技術層面：缺測試型工作負載的基準。
- 流程層面：CI 時間窗限制。

### Solution Design
解決策略：選用 o4-mini 作為 Tool Use 主力模型，單案例約 1 分鐘；將壓力留給 API，不在模型上追求過度 reasoning。

實施步驟：
1. 選型試跑
- 實作細節：比較 2-3 種模型的完成時間。
- 所需資源：模型 API。
- 預估時間：1-2 小時

2. 設定逾時與重試策略
- 實作細節：避免偶發網路造成整批失敗。
- 所需資源：HTTP 設定。
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
.AddOpenAIChatCompletion(modelId: "o4-mini", apiKey: OPENAI_APIKEY, httpClient: ...);
```

實際案例：文中指出單案例約 1 分鐘完成。  
實作環境：OpenAI o4-mini。  
實測數據：
- 改善前：模型未定、延遲不可預測。
- 改善後：單案 ~60 秒，可估計排程。
- 改善幅度：可預測性提升（定性）。

Learning Points
- 測試場景偏「工具協作」，不必追極致 reasoning
- 模型選型需以延遲與成本導向
- 逾時/重試是工程必備

Practice Exercise
- 基礎：測量你 API 的單案耗時（30 分鐘）
- 進階：替換模型比較延遲（2 小時）
- 專案：建立模型選型決策表（8 小時）

Assessment Criteria
- 功能完整性：選型能達時延目標
- 程式碼品質：逾時/重試配置良好
- 效能優化：耗時統計與告警
- 創新性：動態選模策略


## Case #16: 先做 PoC Console，再規劃 MCP/規模化落地

### Problem Statement
業務場景：外界詢問為何不直接做 MCP；但在 PoC 階段應聚焦驗證「核心價值是否打通」。  
技術挑戰：MCP 涉及更多協定、端到端整合與生產級治理，PoC 容易被分散。  
影響範圍：時程、風險控管、目標聚焦。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. MCP 導入成本高。
2. 還有認證、規格、治理等外圍工作。
3. PoC 首要是驗證技術可行性。

深層原因：
- 架構層面：需要成熟的服務化介面。
- 技術層面：多代理/多工具協調。
- 流程層面：分階段推進的路線圖缺失。

### Solution Design
解決策略：先以 .NET Console + SK 快速驗證「Intent→Assertion」主幹路徑；待核心穩定後，再規劃 MCP Server、權限、佈署與觀測。

實施步驟：
1. PoC 聚焦
- 實作細節：50 行內打通核心；完成報告與證據鏈。
- 所需資源：Console/SDK。
- 預估時間：1-2 天

2. 規模化路徑
- 實作細節：MCP Server、鑑權、佈署、監控、租戶化。
- 所需資源：平臺與 SRE。
- 預估時間：數週

關鍵程式碼/設定：
```plaintext
// PoC 主幹：Import OpenAPI → Prompt（SOP/用例/報告）→ Auto Tool Use → 報告（MD+JSON）
```

實際案例：作者以 Console App 完成 PoC，核心程式約 50 行。  
實作環境：.NET Console、SK、OpenAI。  
實測數據：
- 改善前：若同時做 MCP，風險/時程難控。
- 改善後：主幹快速驗證通過。
- 改善幅度：PoC 成功率與速度大幅提升（定性）。

Learning Points
- PoC 要專注「最小可行證據」
- 規模化需額外考量鑑權/部署/監控
- 分階段路線圖降低風險

Practice Exercise
- 基礎：用 Console 打通最小路徑（30 分鐘）
- 進階：加上 JSON 報告與日誌（2 小時）
- 專案：擬 MCP 化設計與風險清單（8 小時）

Assessment Criteria
- 功能完整性：PoC 能跑通用例
- 程式碼品質：簡潔、可演進
- 效能優化：NA
- 創新性：清晰的規模化藍圖



====================

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 5（EmptyCart 替代）
  - Case 10（Auto 工具選擇）
  - Case 11（三段式 Prompt）
  - Case 14（日誌與表格化證據）

- 中級（需要一定基礎）
  - Case 2（BDD 領域用例）
  - Case 3（OpenAPI 一鍵匯入）
  - Case 6（OAuth2 權杖注入）
  - Case 7（跨步驟參數傳遞）
  - Case 8（Then 斷言與失敗分類）
  - Case 9（Markdown+JSON 報告）
  - Case 13（精準 OpenAPI 與 CI）
  - Case 15（模型選型與性能）

- 高級（需要深厚經驗）
  - Case 1（Intent→Assertion 全流程）
  - Case 12（AI Ready 領域 API 設計）
  - Case 16（PoC→MCP 規模化路線）

2) 按技術領域分類
- 架構設計類：Case 1, 12, 13, 16
- 效能優化類：Case 15
- 整合開發類：Case 3, 6, 7, 9, 10, 11, 14
- 除錯診斷類：Case 4, 8, 14
- 安全防護類：Case 6, 13

3) 按學習目標分類
- 概念理解型：Case 1, 2, 12, 16
- 技能練習型：Case 3, 5, 6, 7, 10, 11, 14
- 問題解決型：Case 4, 8, 9, 13, 15
- 創新應用型：Case 1, 12, 16



案例關聯圖（學習路徑建議）
- 建議先學順序：
  1) Case 11（三段式 Prompt 基礎）
  2) Case 3（OpenAPI 一鍵匯入 Tool）
  3) Case 10（Auto 工具選擇）
  4) Case 4（反幻覺與證據要求）
  5) Case 5（前置條件替代模式）
  6) Case 7（跨步驟參數傳遞）
  7) Case 9（報告雙軌輸出）
  8) Case 6（OAuth2 與環境控制）
  9) Case 14（可視化證據與診斷）
  10) Case 2（BDD 領域用例）
  11) Case 8（Then 斷言與失敗分類）
  12) Case 15（模型與性能）
  13) Case 13（OpenAPI 與 CI 治理）
  14) Case 12（AI Ready API 設計）
  15) Case 1（整體打通）
  16) Case 16（規模化與 MCP）

- 依賴關係：
  - Case 3 → Case 10 → Case 7/4/5（工具匯入是自動編排與跨步驟傳遞的前提）
  - Case 11 → Case 9/8（良好 Prompt 才能有穩定報告與斷言）
  - Case 13 → Case 3（精準 OpenAPI 是工具匯入前提）
  - Case 12 → Case 1（AI Ready 設計提升整體可行性）
  - Case 6/14 為橫切關注（安全與可觀測）支撐所有案例

- 完整學習路徑建議：
  - 先以 Case 11/3/10/4 奠定最小可行骨幹（Prompt、Tool、Auto、反幻覺）
  - 接著學 Case 5/7/9/6/14 強化用例執行力（前置條件、參數、報告、安全、證據）
  - 之後補上 Case 2/8/15/13 提升治理與效率（BDD、斷言、性能、CI 規格）
  - 最後攻克 Case 12/1/16 打通全流程與規模化（AI Ready、整體串接、MCP 路線）

以上 16 個案例均源自原文脈絡，附有可操作的程式碼、流程與實證輸出，能直接用於教學、實作與評估。