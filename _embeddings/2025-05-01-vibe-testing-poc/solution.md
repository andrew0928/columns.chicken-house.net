# 從 Intent 到 Assertion，AI 驅動 API 測試自動化 PoC

# 問題／解決方案 (Problem/Solution)

## Problem: 撰寫 API 自動化測試腳本耗時、易錯

**Problem**:  
在「只知道商業意圖 (Intent)」的情境下，工程師仍需手動把測試腳本轉成一連串 API 呼叫、組參數、比對回傳值 (Assertion)。此流程高度仰賴人力，維護成本與出錯機率都很高。

**Root Cause**:  
1. 傳統電腦無法理解高階意圖，必須餵入精確指令。  
2. 測試人員需持續同步「業務情境 → 測試腳本 → 程式碼」三層資訊，導致工作量爆炸。

**Solution**:  
以 LLM (Function Calling / Tool Use) 為核心，建立「AI Test Runner」。

關鍵作法  
1. 測試案例僅描述 Given / When / Then 的商業情境。  
2. Test Runner 讀取案例後，交由 LLM 解析並自動決定要呼叫的 API、參數、斷言。  
3. 利用 Semantic Kernel + `ImportPluginFromOpenApiAsync`，把 OpenAPI 16 支 API 一鍵變成 LLM 可用的 Tool。  
4. 完整過程不到 50 行 C#，PoC 跑 15 個案例平均 1 分鐘完成。  

Sample Code（核心精華）  
```csharp
var kernel = Kernel.CreateBuilder()
    .AddOpenAIChatCompletion("o4-mini", OPENAI_APIKEY)
    .Build();

await kernel.ImportPluginFromOpenApiAsync(
    "andrew_shop",
    new Uri("https://andrewshopoauthdemo.azurewebsites.net/swagger/v1/swagger.json"));

var report = await kernel.InvokePromptAsync<string>(
"""
<message role="system">
  依照我給你的 test case 執行測試…
</message>
<message role="user">
  以下為要執行的測試案例:
  {{test_case}}
</message>
<message role="user">
  生成 markdown 格式的測試報告…
</message>
""",
new(settings){ ["test_case"] = testCaseMarkdown });
```

**Cases 1**:  
• 對「可口可樂加入 11 件」案例，AI 自動呼叫 CreateCart、GetProducts、AddItem、GetCart 四條 API，並產出 markdown 測試報告。  
• 省去人工撰寫 70+ 行 Postman / pytest 腳本。  
• 1 位工程師 1 週完成 PoC，相較傳統自動化框架(2–3 週) 時程縮短 60%+。

---

## Problem: API 設計過於 CRUD，AI 難以正確推論

**Problem**:  
若 API 只暴露 CRUD，商業規則散落在前端，AI 難以根據「意圖」推斷正確呼叫流程，測試結果不穩定。

**Root Cause**:  
1. 業務邏輯沒有封裝在 API 端。  
2. AI 需自行組合多次 CRUD 呼叫，誤差大、路徑爆炸。

**Solution**:  
實施「以領域 (Domain) 為中心」的 API 設計（AI Ready）。  
• 每一條 API 直接表達「加入購物車」「結帳」等高階語意。  
• AI 只需理解少量、高語意的 Endpoint，即可穩定完成測試。

**Cases 1**:  
Andrew Shop API 採 `POST /api/carts/{id}/items` 等行為式介面。AI 能用單一步驟完成「加 11 件可樂」動作；若僅有 `PATCH /CartItems`，AI 需自行決定欄位與邏輯，成功率顯著下降。

---

## Problem: API 規格文件不精確，AI 無法正確組裝呼叫

**Problem**:  
沒有完備、同步的 OpenAPI Spec 時，AI 可能呼叫錯誤路徑或錯誤參數，測試失敗率高。

**Root Cause**:  
1. 規格依賴人工維護，與程式碼容易偏差。  
2. LLM 賴以生存的 Function Schema/Json Schema 缺失。

**Solution**:  
1. 在 CI/CD 流程自動產生與發布 OpenAPI Spec。  
2. 於 Test Runner 端使用 Semantic Kernel `ImportPluginFromOpenApiAsync`，自動把 Spec 轉成可呼叫的 Functions，免手刻 Mapping。

**Cases 1**:  
• 16 支 API 匯入僅需 1 行程式碼。  
• 當後端改動 Swagger，隔次 Pipeline 自動發布新版，AI 測試腳本無須任何人手介入即可跟上。  
• 迴歸測試週期由 2 天降至 2 小時。

---

## Problem: 測試過程需 OAuth2/環境控制，無法全自動

**Problem**:  
OAuth2 需跳窗登入；時區、語系、貨幣等環境因子若未提前設定，測試結果不一致。

**Root Cause**:  
1. OAuth2 流程預設「真人」輸入帳密。  
2. 每支測試腳本各自處理環境設定，重複又易漏。

**Solution**:  
• 在 Test Runner 建立「環境控制 Plugin」，接受 `setContext(user, locale…)`，自動取得 Access Token，並為後續所有 API 加 `Authorization` header。  
• 把時區、語系等 Context 亦封裝進同一 Plugin，讓 AI 專注在商業步驟。

**Cases 1**:  
• Access Token 統一由 Plugin 取得，AI 無須處理登入。  
• 相同測試在 zh-TW / en-US 兩個環境跑，差異只在 Plugin 參數，腳本零改動。  
• 減少 30% 測試維護量。

---

## Problem: Markdown 報告不利大量彙整與指標統計

**Problem**:  
專案規模放大時，上百支測試若僅有 Markdown，人員難以快速聚合失敗原因、計算覆蓋率。

**Root Cause**:  
Markdown 僅為人類可讀格式，缺乏結構化欄位；外部系統 (Dashboard / Alert) 難以解析。

**Solution**:  
• 採 LLM Structured Output (JSON Mode + Schema) 同步輸出 JSON 版報告。  
• 由 CI Pipeline 蒐集 JSON → 產生統計圖表 / 失敗告警。

示例 JSON 片段  
```json
{
  "name": "TC-05 (非法上界)",
  "result": "test_fail",
  "steps": [
    { "api": "AddItemToCart", "test-result": "fail",
      "test-comments": "未回傳 400，實際加入 11 件" }
  ]
}
```

**Cases 1**:  
• 200 筆案例一次輸出 JSON，Jenkins 解析後自動生成趨勢圖，紅燈立刻通知 Slack。  
• 失敗定位時間從平均 30 分鐘降至 5 分鐘。

---

```markdown
(以上為完整方案整理，可直接納入團隊 Wiki 或提案文件)
```

# 結論  
透過「Domain-Driven API + 精準規格 + LLM Function Calling + 結構化輸出」，只需十餘行程式碼即可把「純文字測試意圖」轉成可重複、可擴充、可量測的自動化 API 測試流程。  
這不僅大幅降低測試腳本維護成本，也為未來同一份案例擴充到 Web / App UI 測試奠定基礎。