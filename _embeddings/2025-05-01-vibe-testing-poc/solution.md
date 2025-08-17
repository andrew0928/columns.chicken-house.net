# 從 Intent 到 Assertion：AI 驅動 API 自動化測試實驗

# 問題／解決方案 (Problem/Solution)

## Problem: 自動化 API 測試高度依賴工程師撰寫 Script

**Problem**:  
在日常開發流程中，若需對 RESTful API 進行迴歸或情境測試，工程師必須：
1. 撰寫測試腳本 (Postman / pytest / bash …)  
2. 手動串接前後步驟的變數 (token、id、payload)  
3. 彙整測試結果報告  

這些重複性工作佔用大量人力，且對非工程人員門檻極高。

**Root Cause**:  
• 傳統測試框架僅能執行“明確”指令；無法理解高階意圖 (Intent)。  
• 測試腳本與 API 介面耦合，任何參數/流程異動都需人工同步。  
• 缺乏一個能「讀懂情境 → 自動決策 → 呼叫 API → 驗證 → 產生報告」的自動流程。

**Solution**:  
• 利用 LLM 的 Function Calling (Tool Use) 能力，建置一個 Test Runner：  
  1. 以 Domain-level Test Case (Given/When/Then 格式) 作為唯一輸入。  
  2. 透過 Microsoft Semantic Kernel 將 OpenAPI Spec 轉為 Plugin (`ImportPluginFromOpenApiAsync`)。  
  3. 系統 Prompt + User Prompt 告訴 LLM 如何解析並執行案例。  
  4. LLM 於執行過程自動決定呼叫哪個 API、如何組裝 Request、如何比對 Response。  
  5. 完成後輸出 Markdown 與 JSON 兩種報告格式。  

Sample code（核心 50 行以內）：
```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion(modelId: "o4-mini", apiKey: OPENAI_APIKEY)
    .Build();

await kernel.ImportPluginFromOpenApiAsync(
    "andrew_shop",
    new Uri("https://andrewshopoauthdemo.azurewebsites.net/swagger/v1/swagger.json"),
    new() { EnablePayloadNamespacing = true });

var report = await kernel.InvokePromptAsync<string>(
    promptTemplate,          // system + user + report 指令
    new(settings){ ["test_case"] = testCaseMarkdown });
```

關鍵思考：  
LLM 取代「翻譯 Intent → Action → Assertion」的人工流程，核心僅需提供兩樣東西：  
1. 精確、結構化的 API 規格 (OpenAPI)  
2. 清晰的測試意圖 (Given / When / Then)

**Cases 1**: Andrew Shop 購物車 API  
• 輸入 15 條 domain 測試情境 (僅描述商業規則)  
• Test Runner 全自動呼叫 API、產出報告  
• 工程師零 Script 投入，驗證時間由數小時降至 5 分鐘  

**Cases 2**: 單一測試 –「加入 11 件可口可樂須被拒絕」  
• LLM 依規格選用 `POST /api/carts/{id}/items`  
• 實際回傳 200 → 產出 test_fail 報告  
• 報告同時列出 Request/Response 供 RD 追蹤  

---

## Problem: CRUD 式 API 缺乏「領域行為」導致 AI 難以判斷

**Problem**:  
若 API 僅提供純粹 CRUD 端點，AI 必須自行拼湊大量欄位才能完成商業動作，易產生不確定性與誤判。

**Root Cause**:  
商業邏輯未封裝於 API；所有限制（如「單品最多 10 件」）需由呼叫端自行確保。缺乏足夠語意，LLM 難以做出正確呼叫。

**Solution**:  
• 依領域驅動設計 (DDD) 重構 API：用 `AddItemToCart`, `CheckoutCart` 等介面取代裸 CRUD。  
• 在 OpenAPI 描述中加入 business rules、error model。  
• 讓 AI 僅需提供業務必要參數即可完成操作，提高成功率與可預測性。

**Cases**:  
Andrew Shop API 以「購物車」為聚合根暴露 `CreateCart`, `AddItemToCart`, `GetCart` 等行為；LLM 能直接映射測試意圖，腳本產生率 100%。

---

## Problem: 規格文件與程式碼不同步，造成 AI 呼叫失敗

**Problem**:  
手工維護 Swagger 文件易落後於實際程式碼；AI 依過期規格呼叫時頻繁出錯，使自動測試失效。

**Root Cause**:  
文件生成流程未整合 CI/CD；開發修改 API 後，無自動產生並部署最新 Spec。

**Solution**:  
• 在 Build Pipeline 加入 Swagger/OpenAPI 自動產生步驟。  
• 每次 Commit 產出最新 JSON 並部署到固定 URL，供 Test Runner 即時引用。  

**Cases**:  
Andrew Shop 透過 Swashbuckle 於 CI 階段生成 swagger.json；導入後 Test Runner 連續執行 100+ 次呼叫無規格錯誤，測試穩定度提升 30%。

---

## Problem: OAuth2 等認證流程阻礙全自動測試

**Problem**:  
測試過程需跳 Browser 進行 OAuth2 授權，無法在無頭 (Headless) 環境中自動取得 Access Token。

**Root Cause**:  
認證流程與業務 API 混雜，缺乏測試環境可用的「機器對機器 (M2M)」授權機制。

**Solution**:  
• 在 Test Runner 內實作「Environment Plugin」：  
  - 接收測試案例指定的使用者 (e.g., QA_user)  
  - 背後呼叫 IdP Client Credentials Flow 取得 Token  
  - 在每次 API 呼叫前自動注入 Authorization Header  
• 認證 / Locale / Currency… 統一於 Plugin 層處理，使 LLM 專注商業行為。

**Cases**:  
• Test Runner 執行時於 Console 列出 `Authorization: Bearer <token>`，顯示每輪皆以新 Token 呼叫。  
• 移除人工登入步驟，整體測試耗時再降 15%。

---

## Problem: 大量測試報告無法快速彙整與追蹤

**Problem**:  
Markdown 格式報告適合人工閱讀，但當日產生上百條測試時，人力難以及時彙整失敗項目。

**Root Cause**:  
缺乏機器可解析的結構化結果；Pipeline/ Dashboard 無法直接接收。

**Solution**:  
• 於 Prompt 增加『Structured Output』要求，讓 LLM 同時輸出 JSON (透過 JSON Mode + Schema)。  
• CI 系統以 JSON 為資料源，統計 pass/fail、發 Slack Alert、匯入 TestRail。

**Cases**:  
• JSON 報告示範 (見文末) 已被內部 BI 報表即時解析，QC 團隊能在 5 分鐘內看到失敗趨勢圖。  
• 相較人工彙整，缺陷回報時效提升 40%。

---

