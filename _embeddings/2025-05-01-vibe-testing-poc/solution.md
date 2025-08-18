# 從 Intent 到 Assertion ─ Vibe Testing PoC 實戰筆記

# 問題／解決方案 (Problem/Solution)

## Problem: 手動撰寫 API 測試腳本耗時又易漏

**Problem**:  
在日常開發流程中，工程師必須把「商業情境」(Intent) 轉換成可以執行的 API 測試腳本，再人工比對回應做 Assertion。流程包含：  
1. 詳列測試步驟及參數  
2. 撰寫／維護程式或 Postman Script  
3. 人工彙整測試報告  
整體高度仰賴人力，更新 API 或需求時維護成本極高。

**Root Cause**:  
‒ 傳統電腦無法理解高層次「意圖」，必須給出絕對明確的操作指令。  
‒ 過去 LLM 欠缺「Tool / Function Calling」能力，無法直接把意圖映射成 API 行為，只能由工程師手動翻譯。  

**Solution**:  
1. 建立 AI Test Runner：  
   • 以 Microsoft Semantic Kernel + OpenAI Function Calling 實作  
   • 讀取 Domain-level Test Case (Given/When/Then) + Swagger 產生的 OpenAPI 規格  
   • Kernel.ImportPluginFromOpenApiAsync(...) 10 行內快速將 16 支 API 轉成 LLM 可呼叫的 Tools  
2. 制定 Prompt SOP：  
   • System Prompt 描述 Given/When/Then 鐵律及禁止猜測回應  
   • User Prompt 傳入測試案例  
   • Output Prompt 要求產生 Markdown 報告  
3. LLM 自動：  
   • 決定呼叫哪支 API、帶哪些參數  
   • 執行 API → 收集真實 Response  
   • 完成 Assertion 並產出報告  

關鍵思考點：讓 LLM 只負責「推論＋呼叫 Plugin」，以標準化 API 規格及 Prompt 控制可重現性。

**Cases 1**: Andrew Shop 購物車 API  
‒ 投入 15 筆情境案例，Runner 全自動完成呼叫、驗證、報表匯出；核心程式碼 < 50 行。  
‒ 單一案例平均 1 分鐘完成，工程師只需 Review 報告。  
‒ 證實「加入 11 件可口可樂應失敗」的需求未被實作，Runner 回報 test_fail，符合預期。

---

## Problem: API 未「AI Ready」，AI 難以正確操作

**Problem**:  
若 API 僅提供 CRUD 介面、缺乏領域封裝或規格鬆散，AI 難以推理出正確的呼叫順序與參數，導致測試流程失敗或結果不可靠。

**Root Cause**:  
1. 商業規則散落在前端／呼叫端，API 本身無封裝。  
2. 缺少精確且同步的 OpenAPI (Swagger) 文件，AI 無法解析欄位與回傳結構。  

**Solution**:  
1. 依領域 (Domain) 設計 API，把商業邏輯封裝進端點，例如 CreateCart、AddItemToCart。  
2. 以 CICD 自動產生並發佈 Swagger，確保隨程式碼即時更新。  
3. 將 Swagger 直接轉成 Semantic Kernel Plugin，供 LLM 精準取得 schema。  
   → AI 只需讀文件即可形成正確 CallPath，降低 Prompt 複雜度。

**Cases 1**:  
Andrew Shop API 採 Domain-style 設計 + 自動產生 Swagger；LLM 成功解析 ProductId、CartId 等欄位並自行串接 4 支 API 完成整個流程。  

**Cases 2** (反例):  
將相同情境套用到僅有 /products/{id} PUT/POST 的 CRUD API，LLM 無法自動決定「超過 10 件」該如何表示，導致步驟發散失敗。  

---

## Problem: OAuth2 認證與環境因子阻礙自動化流程

**Problem**:  
正式 API 多需 OAuth2 / OIDC 認證，甚至與語系、幣別、時區等環境條件綁定。若每次測試都須人工登入或設定，將破壞全自動目標。

**Root Cause**:  
‒ OAuth2 典型流程需跳瀏覽器、人工輸入帳密。  
‒ 測試案例中常需切換不同身份與環境；若無集中機制，AI Prompt 會被雜訊淹沒。

**Solution**:  
1. 為 Test Runner 寫「Environment / Auth Plugin」：  
   • 自動執行 OAuth2 flow 取得 access_token  
   • 將 token 注入 Authorization Header，對 AI 透明化  
2. 以相同 Plugin 處理 locale / currency / timezone 等 Context，讓測試案例只關注商業意圖。

**Cases 1**:  
Runner 執行時每次自動取得新 Token，Request Header 顯示 `Authorization: Bearer <token>`，API 全數通過授權檢查；測試無需人工介入。  

---

## Problem: 大量測試報告難以彙整與監控

**Problem**:  
單次 PoC 可用 Markdown 逐份閱讀，但在 CI/CD 或 Regression 測數百案例時，人員無法即時判讀所有 Markdown 報告。

**Root Cause**:  
Markdown 僅為人類可讀格式，不利機器聚合、統計與警示。無結構化資料 → 很難做 Dashboard 或失敗警報。

**Solution**:  
1. 引入 LLM Structured Output (Json Mode + Schema)  
   • 於 Prompt 要求同時輸出 JSON 版測試結果  
   • Schema 內含 name / result / steps / context 等欄位  
2. CI Pipeline 收集 JSON → 寫入資料庫或統計服務 → 圖形化/告警。  

**Cases 1**:  
範例 JSON（見文末）可直接餵進 Elastic / Grafana 生成趨勢圖；當 test_fail 比例>閾值即發 Teams 警示。  

**Cases 2**:  
內部每日 Regression 300+ 筆案例，全自動彙總成功率、失敗 API Top10，節省測試團隊 90% 人工對帳時間。  

---

```markdown
(以上各組 Problem/Solution 可依實務再細拆或增補）
```

#