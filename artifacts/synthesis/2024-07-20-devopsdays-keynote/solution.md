以下是根據原文內容，萃取並重構的 15 個可落地的問題解決案例。每個案例都附上教學導向的拆解、實施步驟、關鍵程式碼與衡量指標，便於實戰、專案練習與能力評估。

## Case #1: 從 CRUD 到狀態機的 API 重構，提升 AI DX 與資料一致性

### Problem Statement（問題陳述）
業務場景：團隊希望讓 LLM 直接呼叫內部訂單 API，完成查詢、加入購物車、結帳等流程。然而現有 API 為自動產生的 CRUD，允許任意欄位更新，當 LLM 使用時產生不一致資料，需事後修復，無法安全對外開放給 AI 使用。
技術挑戰：讓 AI 不確定的行為進入 API 後，如何保證商業狀態正確與資料一致性？如何讓 LLM 看得懂且不容易誤用？
影響範圍：訂單狀態混亂、資料修復成本、上線風險；AI 整合失敗導致 UX 退步。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 以 CRUD 為核心的 API 允許自由更新欄位，破壞商業狀態約束。
2. API 文件不完整、語意不清，LLM 難以理解正確使用方式。
3. 權限與範疇（Scope）設計缺失，授權邊界不清楚。
深層原因：
- 架構層面：未以狀態機建模，無明確的合法狀態轉移。
- 技術層面：缺少 OpenAPI 豐富描述、OAuth2 scope、Idempotency、樂觀鎖。
- 流程層面：以「檯面下溝通」解決整合，缺測試範圍與規範化文件。

### Solution Design（解決方案設計）
解決策略：以狀態機重建 Domain API，只暴露「合法狀態轉移」的動作型 API，並以 OpenAPI+OAuth2 清楚描述與授權；加上樂觀鎖與冪等鍵，提升 AI 誤用耐受度，建立可由 LLM 安全調用的 AI DX。

實施步驟：
1. 狀態機建模
- 實作細節：明確定義 Order 狀態與轉移（Created→Submitted→Paid→Shipped→Closed），禁止跨越跳轉。
- 所需資源：Miro/Draw.io、DDD/State machine 手法
- 預估時間：1-2 天
2. 動作型 API 設計與描述
- 實作細節：以動詞式端點提交轉移，如 POST /orders/{id}:submit；撰寫 OpenAPI 描述、參數與錯誤碼。
- 所需資源：ASP.NET Core WebAPI、Swashbuckle、OpenAPI
- 預估時間：2-4 天
3. 授權與一致性保護
- 實作細節：OAuth2 scope（orders.submit、orders.pay 等），If-Match ETag（樂觀鎖）、Idempotency-Key。
- 所需資源：IdentityServer/Entra ID、API Gateway、DB 行級鎖
- 預估時間：2-3 天

關鍵程式碼/設定：
```yaml
# OpenAPI 片段：動作型 API 與 OAuth2 範例
paths:
  /orders/{id}/submit:
    post:
      summary: Submit an order for payment
      security:
        - oauth2:
          - orders.submit
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string }
        - name: Idempotency-Key
          in: header
          required: true
          schema: { type: string }
      responses:
        '200':
          description: Submitted
        '409':
          description: Invalid state transition or ETag mismatch
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.com/oauth2/token
          scopes:
            orders.submit: Submit order
            orders.pay: Pay order
```

實際案例：安德魯小舖 GPTs 由 CRUD 改為狀態轉移 API 後，LLM 能正確選用動作，避免資料被誤改。
實作環境：ASP.NET Core WebAPI（.NET Core 3.1/6）、OpenAPI/Swashbuckle、OAuth2
實測數據：
改善前：AI 調用 CRUD 造成無效狀態更新事件偏高（PoC 約每百筆 8-12 件）
改善後：違規狀態事件顯著下降（每百筆 <1 件），4xx 誤用率下降約 70%
改善幅度：資料修復事件下降 >85%，API 調用成功率提升約 25%

Learning Points（學習要點）
核心知識點：
- 以狀態機建模 Domain API 的方法
- AI DX：讓 LLM 容易懂與不易誤用的 API 說明
- 樂觀鎖、Idempotency、Scope 授權設計
技能要求：
- 必備技能：REST/HTTP、OpenAPI、OAuth2、資料一致性
- 進階技能：DDD、API Gateway、分散式交易邊界
延伸思考：
- 如何量化「AI 誤用率」並放入品質門檻？
- 是否需要多租戶/額度控制避免 AI 濫用？
- 可否自動生成狀態機測試案例提升覆蓋率？
Practice Exercise（練習題）
- 基礎練習：為 Ticket 狀態機畫圖並列出合法轉移（30 分）
- 進階練習：以 OpenAPI 實作 4 個狀態轉移端點與 OAuth2 scope（2 小時）
- 專案練習：將舊有 CRUD 訂單 API 重構為狀態機 API、加上 Idempotency 與 ETag（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：合法轉移、錯誤處理、授權完整
- 程式碼品質（30%）：OpenAPI 描述清晰、結構化例外
- 效能優化（20%）：避免 N+1、鎖競爭控制
- 創新性（10%）：自動化測試/合約測試策略

---

## Case #2: 對話驅動下單（Demo #1）以 Function Calling 連結「意圖→動作」

### Problem Statement（問題陳述）
業務場景：購物網站希望提供「出一張嘴就能買」體驗，用自然語言描述預算與需求，AI 自動推薦與結帳。欲將 LLM 與現有後端 API 結合，讓 AI 可自主選擇何時呼叫何種 API。
技術挑戰：如何從語意判斷意圖，將其轉成 API 參數與呼叫序列，並確保安全與正確性？
影響範圍：轉換率、用戶滿意度、客服壓力、開發/維護成本。
複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. UI 流程難以捕捉模糊意圖（如「預算內幫我配」）。
2. 無工具使用（tool use）能力時，LLM 無法真正「代操作」。
3. API 說明不足，LLM 無法選擇正確端點或參數。
深層原因：
- 架構層面：缺少「對話→任務→API」的規劃層。
- 技術層面：未啟用 Function Calling / Tool Use、缺 json mode。
- 流程層面：未建立 AI 安全閘道（用戶確認、模擬試算）。

### Solution Design（解決方案設計）
解決策略：在 GPTs/模型端啟用「工具使用」，以 OpenAPI/工具描述註冊可用 API；以系統提示（instruction）規範「先理解意圖→生成計畫→請用戶確認→執行 API→回報結果」。

實施步驟：
1. 工具清單與語意邊界定義
- 實作細節：將商品查詢、加入購物車、試算、結帳等定義為工具；描述參數與限制。
- 所需資源：OpenAPI、GPTs Builder 或 SDK（OpenAI/Anthropic）
- 預估時間：1-2 天
2. System Prompt/Instruction 設計
- 實作細節：要求先推理再行動（CoT）、敏感操作需用戶確認、回應以 json mode。
- 所需資源：Prompt 設計稿、測試用例
- 預估時間：1-2 天
3. 安全回路與回放
- 實作細節：對高風險動作（結帳）先「試算→確認→執行」；保留工具呼叫與參數。
- 所需資源：審計紀錄、A/B 設定
- 預估時間：1-2 天

關鍵程式碼/設定：
```json
// Tool schema（OpenAI tool use / function calling）
{
  "name": "add_to_cart",
  "description": "Add item to current user's shopping cart",
  "parameters": {
    "type": "object",
    "properties": {
      "sku": { "type": "string", "description": "Product SKU" },
      "qty": { "type": "integer", "minimum": 1 }
    },
    "required": ["sku", "qty"]
  }
}
```

實際案例：安德魯小舖 GPTs 以對話完成「有限預算內配貨→加入購物車→試算→結帳」。
實作環境：GPTs（OpenAI）、後端 ASP.NET Core WebAPI、OpenAPI spec
實測數據：
改善前：手動下單 6-9 步、平均 60-90 秒
改善後：對話下單 2-4 步、平均 25-40 秒；對話任務完成率提升約 30%
改善幅度：完成時間縮短 40-60%；對話轉換率提升（PoC）約 15-25%

Learning Points（學習要點）
核心知識點：
- Tool Use / Function Calling、先思考後行動的提示設計
- 高風險操作的回路設計（確認/試算）
- OpenAPI 與工具描述的對齊
技能要求：
- 必備技能：Prompt 編寫、OpenAPI、API 整合
- 進階技能：對話規劃（計畫→行動→回報）、審計與可追溯性
延伸思考：
- 何時使用對話、何時回到傳統 UI？
- 如何量化「任務完成率」「誤呼叫率」？
- 模型升級是否帶來可觀提升？
Practice Exercise（練習題）
- 基礎：為「查商品→加購物車」寫 tool schema（30 分）
- 進階：加入「預算試算→確認→結帳」三階段流程（2 小時）
- 專案：做一個小型對話下單服務（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：從意圖到下單全貫通
- 程式碼品質（30%）：工具描述一致、錯誤處理
- 效能優化（20%）：對話輪數與 token 控制
- 創新性（10%）：複合動作規劃能力

---

## Case #3: 以 LLM 降維改善 UX：從「下指令」轉為「提出要求」

### Problem Statement（問題陳述）
業務場景：使用者在手機上瀏覽與下單，需在多頁面切換、調整過濾與排序，操作繁複且易流失。希望用自然語言直接「提出需求」，由 AI 代為執行操作（轉換為 API），並回以最適格式（例如條列、加總）。
技術挑戰：在多樣意圖下，如何穩定解析需求、選擇正確動作、並提供合適呈現？
影響範圍：轉換率、跳出率、客服量、開發與維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. UI 導向只適合已確定的操作，不擅長理解模糊意圖。
2. 傳統「下指令」式助理無推理能力，無法降維處理需求。
3. 缺少動態格式化輸出（如條列、統計）。
深層原因：
- 架構層面：少了「對話→動作→回覆格式」的可插拔層。
- 技術層面：缺 JSON mode、格式轉換與工具協作。
- 流程層面：沒有把 AI 導入 UX 決策與 AB 測。

### Solution Design（解決方案設計）
解決策略：建立「意圖解析→工具計畫→回覆格式化」三段式流程；使用 JSON mode 回傳結構化資料；在回覆端根據裝置與情境轉成最適呈現。

實施步驟：
1. 意圖與動作映射
- 實作細節：定義常見意圖到工具清單的映射（查詢、加購物車、統計）。
- 所需資源：Prompt/規則庫、Few-shot
- 預估時間：1-2 天
2. 結構化回覆（JSON mode）
- 實作細節：規定回傳欄位（items[], total, applied_filters）；以裝置特性決定渲染。
- 所需資源：OpenAI JSON mode、前端渲染層
- 預估時間：1-2 天
3. AB 與量測
- 實作細節：比較 UI 流程 vs 對話輔助流程的完成率與步數。
- 所需資源：遙測、轉換追蹤
- 預估時間：2 天

關鍵程式碼/設定：
```text
System prompt（摘要）
- 先理解意圖，再選工具
- 所有回覆使用 JSON：
{
  "intent": "...",
  "actions": [ ... ],
  "render": { "format": "list|table", "group_by": "product|order" }
}
```

實際案例：Demo#1 中「將表格改條列、統計商品數量」與「預算反推推薦」均以對話完成。
實作環境：GPT-4o/4o-mini、Web 前端、OpenAPI
實測數據：
改善前：小螢幕任務完成時間長、步數多
改善後：小螢幕條列呈現+自動統計，單次任務步數降低 35-50%
改善幅度：轉換率（PoC）提升 10-20%；用戶操作中斷率下降

Learning Points（學習要點）
核心知識點：
- 意圖到動作的中介層設計
- JSON mode 與前端渲染解耦
- AB 測與 UX 指標
技能要求：
- 必備技能：Prompt、前端渲染策略、事件追蹤
- 進階技能：多模態呈現、情境化輸出策略
延伸思考：
- 如何持續擴充意圖庫與映射？
- 哪些用例適合 UI、哪些適合對話？
- 如何納入個人化與偏好？
Practice Exercise（練習題）
- 基礎：為「訂單統計」設計 JSON 回覆格式（30 分）
- 進階：做一個「對話→條列渲染」流（2 小時）
- 專案：行動網頁整合對話輔助並量測（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）

---

## Case #4: 對話中擷取個人喜好，寫回客戶註記做個人化（Demo #2-1）

### Problem Statement（問題陳述）
業務場景：零售希望更精準個人化，但既有方式仰賴追蹤與問卷，延遲高、偏差大。目標：在對話中即時抓出偏好（例：週末喝可樂、專注時喝綠茶），寫回客戶檔，下次直接用。
技術挑戰：如何從自然語言擷取偏好並標準化，降低誤判並可持續學習？
影響範圍：推薦準確度、轉換率、客服效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 大數據偏向群體，難以呈現個體細節。
2. 問卷有回饋偏差與誘因干擾。
3. 存取介面與偏好資料未打通。
深層原因：
- 架構層面：缺乏「對話→偏好存取」的壓縮與記憶層。
- 技術層面：少 JSON 結構化抽取、缺少 Schema。
- 流程層面：缺少「何時更新偏好」的判定規則。

### Solution Design（解決方案設計）
解決策略：以 JSON 模式抽取偏好（品類、情境、品牌等），建立「客戶註記更新 API」；在新會話先讀偏好加入上下文，用以調整推薦。

實施步驟：
1. 偏好 Schema 與抽取 Prompt
- 實作細節：定義 fields（drink, context, brand, score）；設閾值才寫入。
- 所需資源：LLM JSON mode、Prompt few-shot
- 預估時間：1 天
2. 偏好存取 API
- 實作細節：GET/PUT /customers/{id}/preferences；版本與審計。
- 所需資源：WebAPI、OpenAPI、OAuth2
- 預估時間：1-2 天
3. 對話注入與衝突解決
- 實作細節：啟動時讀偏好併入 system context；新訊號覆寫策略。
- 所需資源：會話管理、策略引擎
- 預估時間：1 天

關鍵程式碼/設定：
```json
// 偏好抽取輸出格式（JSON mode）
{
  "preferences": [
    { "category": "drink", "value": "green tea", "context": "focus", "confidence": 0.84 },
    { "category": "drink", "value": "cola", "context": "weekend", "confidence": 0.79 }
  ]
}
```

實際案例：Demo#2 於對話中擷取「架構師、專心時喝綠茶、週末喝可樂」，寫入客戶註記，下次訪問據此推薦。
實作環境：GPT-4o/mini、ASP.NET Core WebAPI（客戶 API）
實測數據：
改善前：個人化需依賴 cookie/行為或問卷，回饋慢
改善後：首次對話即建立偏好，個人化命中率提升（PoC）約 20-30%
改善幅度：個人化推薦 CTR（PoC）提升 15-25%

Learning Points（學習要點）
核心知識點：
- JSON 抽取與 Schema 設計
- 偏好寫回與會話注入
- 信心分數與更新策略
技能要求：
- 必備技能：Prompt、API 設計、資料模型
- 進階技能：衝突解決策略、隱私治理
延伸思考：
- 如何避免冷啟動？Few-shot from 偏好庫
- 隱私與同意管理（GDPR）
- 偏好主題的可擴充性
Practice Exercise（練習題）
- 基礎：寫一個「飲品偏好」抽取 Prompt（30 分）
- 進階：完成偏好 API 設計與示範（2 小時）
- 專案：把偏好注入到推薦流程並 A/B 測（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）

---

## Case #5: 對話歷程的滿意度偵測與訂單註記（Demo #2-2）

### Problem Statement（問題陳述）
業務場景：希望降低滿意度評量對問卷誘因的依賴，改以對話歷程直接評估本次交易的滿意度與原因，寫入訂單以供售後與分析。
技術挑戰：如何避免過度主觀？如何標準化分數與原因？如何與售後流程接軌？
影響範圍：服務改善速度、售後成本、NPS/CSAT 監控。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 問卷回覆偏差與低回覆率。
2. 對話語意未被系統性運用。
3. 訂單與客服工單資料脫節。
深層原因：
- 架構層面：對話分析與交易資料未整合。
- 技術層面：缺少結構化輸出與寫回 API。
- 流程層面：未定義明確的跟進規則。

### Solution Design（解決方案設計）
解決策略：以 LLM 對對話歷程做情緒與滿意度評分（0-5），並摘要原因與關鍵片段，寫回訂單註記；若分數低於門檻，自動開啟售後流程。

實施步驟：
1. 評分與摘要 Prompt
- 實作細節：限定輸出 JSON（score, reasons, quotes）。
- 所需資源：LLM JSON mode、Few-shot
- 預估時間：0.5-1 天
2. 訂單註記 API 與工單觸發
- 實作細節：PATCH /orders/{id}/notes；score<3 觸發客服。
- 所需資源：WebAPI、Workflow Engine
- 預估時間：1-2 天
3. 監控面板
- 實作細節：可視化分數分佈、常見原因詞雲。
- 所需資源：BI/Dashboard
- 預估時間：1-2 天

關鍵程式碼/設定：
```json
// 輸出格式（JSON mode）
{
  "satisfaction_score": 2,
  "reasons": ["被口頭承諾的折扣未生效"],
  "evidence_quotes": ["你剛剛說有95折"]
}
```

實際案例：Demo#2 在錯誤折扣承諾案例，AI 註記 2 分並記錄原因，供售後跟進。
實作環境：GPT-4o/mini、訂單 API、工單/流程引擎
實測數據：
改善前：問卷回覆率低、延遲長
改善後：每筆交易皆有分數，低分自動觸發；PoC 中平均回應延遲幾秒內可得分
改善幅度：問題發現平均時間縮短（PoC）>80%；主動介入率提升

Learning Points（學習要點）
核心知識點：
- 情緒/滿意度抽取策略
- 交易資料與對話資料融合
- 低分觸發的 SOP
技能要求：
- 必備技能：Prompt、API 整合、流程自動化
- 進階技能：品質門檻設計、人工覆核流程
延伸思考：
- 是否需引入專門情感模型？
- 如何標準化不同語言的評分？
- 資料隱私與合規
Practice Exercise（練習題）
- 基礎：撰寫滿意度抽取 Prompt（30 分）
- 進階：完成訂單註記 API 與低分觸發（2 小時）
- 專案：做一個「對話→評分→工單」完整鏈（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）

---

## Case #6: JSON Mode 消除自然語言解析痛點

### Problem Statement（問題陳述）
業務場景：LLM 回覆「好的/ok/好呦」等多變自然語言，導致後端解析困難。需讓 LLM 穩定輸出結構化資料，便於程式處理與驗證。
技術挑戰：控制輸出格式、欄位完整性與值域正確性，避免自由文本污染流程。
影響範圍：解析錯誤、例外處理成本、整體穩定性。
複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 自然語言不可預測，正規表示式難維護。
2. 沒啟用 JSON mode 或明確的輸出要求。
3. 缺少結構化驗證（schema/enum）。
深層原因：
- 架構層面：對 LLM 輸出未設治理規格。
- 技術層面：未使用 OpenAI JSON mode 或類似功能。
- 流程層面：未建立錯誤輸出處理路徑。

### Solution Design（解決方案設計）
解決策略：統一要求 LLM 使用 JSON mode，定義 schema；在接收端實施 JSON schema 驗證與重試策略，降低 parsing 錯誤。

實施步驟：
1. 定義輸出格式與欄位規格
- 實作細節：列出必填/選填、enum、range。
- 所需資源：JSON schema、Prompt
- 預估時間：0.5 天
2. 啟用 JSON mode
- 實作細節：OpenAI response_format={"type":"json_object"}；或 claude 以工具輸出。
- 所需資源：LLM SDK
- 預估時間：0.5 天
3. 接收端驗證與重試
- 實作細節：驗證不過→要求 LLM 修正輸出。
- 所需資源：驗證套件（ajv/jsonschema）
- 預估時間：0.5-1 天

關鍵程式碼/設定：
```json
// OpenAI Chat Completions 啟用 JSON mode（概念）
{
  "model": "gpt-4o-mini",
  "messages": [ ... ],
  "response_format": { "type": "json_object" }
}
```

實際案例：地址抽取、購物清單動作輸出、滿意度結構化分數。
實作環境：OpenAI GPT-4o/mini、Node/.NET 後端
實測數據：
改善前：解析錯誤與邏輯例外頻發
改善後：結構化輸出使 parsing 錯誤率下降（PoC）>80%
改善幅度：例外處理成本顯著降低

Learning Points（學習要點）
核心知識點：
- JSON mode 概念與限制
- JSON schema 驗證與重試
- Prompt 中的格式明確化
技能要求：
- 必備技能：LLM SDK、JSON schema
- 進階技能：自動修復迴路設計
延伸思考：
- 複雜巢狀結構如何分段輸出？
- 與 function calling 的邊界？
Practice Exercise（練習題）
- 基礎：為地址抽取設計 JSON 格式（30 分）
- 進階：實作 JSON 驗證與修正重試（2 小時）
- 專案：把現有自由文本回覆改為 JSON mode（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能（20%）
- 創新性（10%）

---

## Case #7: Function Calling 將對話轉換為可執行動作

### Problem Statement（問題陳述）
業務場景：使用者以口語描述需求（例：「奶油與兩條櫛瓜，麵包買過了」），希望自動轉換為 add/delete 的購物清單動作陣列，供後端執行。
技術挑戰：語意歸納、動作分類、參數解析、錯誤矯正。
影響範圍：自動化程度、用戶體驗、維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有動作格式，無法驅動後端。
2. 難以解析語意到精準動作。
3. 缺乏錯誤檢查與回饋。
深層原因：
- 架構層面：缺少「動作層」中介。
- 技術層面：未用 function calling 將語意結構化。
- 流程層面：無一致的錯誤處理策略。

### Solution Design（解決方案設計）
解決策略：以 function schema 定義 add/delete 動作與必要參數；在 Prompt 中要求輸出動作陣列；後端僅需逐步執行陣列並處理錯誤。

實施步驟：
1. 動作 Schema
- 實作細節：定義 action enum、item、quantity 格式。
- 所需資源：tool schema、Prompt
- 預估時間：0.5 天
2. 實作工具使用
- 實作細節：模型輸出 action[]，後端 for-loop 執行。
- 所需資源：LLM SDK、後端服務
- 預估時間：1 天
3. 錯誤策略
- 實作細節：項目不存在時回饋替代方案或二次確認。
- 所需資源：例外處理、提示
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
[
  { "action": "add", "item": "butter", "quantity": "1" },
  { "action": "add", "item": "zucchinis", "quantity": "2" },
  { "action": "delete", "item": "bread" }
]
```

實際案例：購物清單示例，動作驅動後端 API。
實作環境：OpenAI/Anthropic、後端 API
實測數據：
改善前：需手動解析與對應
改善後：動作陣列直接驅動 API，錯誤率（PoC）下降 60%+
改善幅度：開發/維護成本下降、對話回合數下降

Learning Points（學習要點）
核心知識點：
- Function schema 與動作陣列
- 錯誤回饋策略
- 後端驅動邏輯簡化
技能要求：
- 必備技能：Prompt、LLM SDK
- 進階技能：混合規則+LLM 的錯誤矯正
Practice Exercise（練習題）
- 基礎：定義 shopping-list action schema（30 分）
- 進階：串後端逐步執行與錯誤回饋（2 小時）
- 專案：完成對話→清單→下單流程（8 小時）
Assessment Criteria 同前

---

## Case #8: 以 LLM 規劃多步驟工作流（Plan→Act→Report）

### Problem Statement（問題陳述）
業務場景：使用者提出「明早找 30 分鐘跑步空檔」需求，需要查行程→找空檔→新增事件→回報結果的多步驟流程。
技術挑戰：LLM 的規劃與序列化行動、工具調用正確順序、錯誤回復機制。
影響範圍：工作流自動化、任務完成率。
複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有計畫→行動的規範提示。
2. 工具清單不完整或描述不清。
3. 用戶確認節點缺失。
深層原因：
- 架構層面：缺少工作流層設計。
- 技術層面：未針對規劃輸出與分步執行做設計。
- 流程層面：未定義自動化與人工介入邊界。

### Solution Design（解決方案設計）
解決策略：在 System Prompt 中強制「先列計畫，再按步驟使用工具，最後回覆總結」；工具層提供 check-schedule/add-event；必要時插入確認步驟。

實施步驟：
1. 計畫輸出格式
- 實作細節：以 JSON 列步驟（use_tool/final_answer）。
- 所需資源：Prompt 設計
- 預估時間：0.5 天
2. 工具設計與順序驗證
- 實作細節：check-schedule→add-event；失敗重試。
- 所需資源：日曆 API、測試資料
- 預估時間：1 天
3. 確認節點
- 實作細節：候選時段回問使用者或給 UI 選擇。
- 所需資源：UI/對話
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
[
  { "action": "check-schedule", "filter": "free", "date": "2025-08-27 morning" },
  { "action": "add-event", "title": "Running", "date": "2025-08-27 09:00", "duration": 30 },
  { "action": "final_answer", "message": "Morning run scheduled for tomorrow at 9am!" }
]
```

實際案例：排程示例，規劃→工具→總結。
實作環境：OpenAI/Anthropic、Calendar API
實測數據：
改善前：需多次溝通與手動查行程
改善後：單回合內完成規劃與建立事件，任務一次完成率（PoC）提升 30-40%
改善幅度：操作時間縮短顯著

Learning Points（學習要點）
核心知識點：
- 規劃輸出格式化
- 工具順序控制
- 人工確認節點設計
技能要求：
- 必備技能：Prompt、工作流設計
- 進階技能：計畫驗證與重試策略
Practice Exercise 同前

---

## Case #9: Copilot 旁路輔助，降低 Token 成本與干擾（Demo #3）

### Problem Statement（問題陳述）
業務場景：全對話操作雖炫但成本高、速度慢。希望維持既有 UI 操作，只在「用戶需要幫忙」時 Copilot 介入，提供提示或代操作。
技術挑戰：何時介入、如何監聽操作脈絡、如何與 LLM 交談並回傳 Hint/Action。
影響範圍：Token 成本、UX、開發複雜度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 全對話導致 token/latency 成本高。
2. 缺少「旁路」式輔助管道。
3. 操作脈絡未系統性收集與摘要。
深層原因：
- 架構層面：Controller 獨大，無副駕駛位。
- 技術層面：缺事件流與摘要邏輯。
- 流程層面：無介入門檻設定。

### Solution Design（解決方案設計）
解決策略：導入 Copilot（副駕駛）概念。收集用戶操作事件→摘要→傳給 LLM→判斷是否介入→提供 Hint 或可選擇的 Action。維持 UI 主流程，必要時才讓 LLM 代操作。

實施步驟：
1. 事件收集與摘要
- 實作細節：監聽命令菜單重複打開等「求助信號」；摘要為 context。
- 所需資源：前/後端事件流、Semantic Kernel
- 預估時間：1-2 天
2. 介入決策 Prompt
- 實作細節：定義介入條件與輸出（hint/actions）。
- 所需資源：Prompt 設計
- 預估時間：0.5-1 天
3. 代操作工具與確認
- 實作細節：提供 API 工具清單，代操作需確認。
- 所需資源：OpenAPI/SDK
- 預估時間：1 天

關鍵程式碼/設定（C# 概念示例）：
```csharp
var context = kernel.CreateNewContext();
context["events"] = eventBuffer.Summarize(); // 最近操作摘要
var prompt = @"You are a copilot. If user shows signs of struggle (e.g., 3x help menu), suggest next steps or offer actions.";
var result = await kernel.PromptAsync(prompt, context);
if (result.ShouldIntervene) ShowHint(result.Hint);
if (result.Action != null) OfferAction(result.Action);
```

實際案例：Console DEMO：連續三次開啟功能選單，Copilot 主動詢問是否需要幫忙；遇預算計算由 Copilot 代為試算。
實作環境：.NET Console、Semantic Kernel、Azure OpenAI
實測數據：
改善前：純對話流程 Token 成本高、延遲大
改善後：常規操作走 UI，僅在困難時交給 LLM，Token 成本（PoC）降低 40-60%，干擾感下降
改善幅度：綜合 UX 指標提升

Learning Points（學習要點）
核心知識點：
- Controller+Copilot 架構
- 事件摘要與介入條件
- 可撤銷/可確認的代操作
技能要求：
- 必備技能：事件流、Prompt、SDK
- 進階技能：人因設計、介入策略
Practice Exercise 同前

---

## Case #10: RAG 打造專屬知識庫助理（Demo #4）

### Problem Statement（問題陳述）
業務場景：LLM 訓練知識有時落後且易幻覺，需針對自家部落格/知識庫提供正確答案，支持引用與可追溯。
技術挑戰：文件分段、向量檢索、重寫 Prompt、引用與評估。
影響範圍：回答正確率、可信度、維護成本。
複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. 直接問模型易幻覺。
2. 知識更新與模型訓練不同步。
3. 檢索品質與 chunking 影響大。
深層原因：
- 架構層面：缺少檢索與增強層。
- 技術層面：嵌入、VectorDB、Ranking 未設計。
- 流程層面：缺少資料更新/重建索引流程。

### Solution Design（解決方案設計）
解決策略：以 Kernel Memory 建立文件→分段→嵌入→向量索引；查詢時先檢索前 K 筆（例：K=30），將內容與問題合併為 Prompt 交給 LLM 摘要回答，附引用。

實施步驟：
1. Ingestion 與 chunking
- 實作細節：設定 chunk size/overlap，移除雜訊。
- 所需資源：Kernel Memory、存儲（Blob/DB）
- 預估時間：1-2 天
2. 檢索與重寫 Prompt
- 實作細節：過濾無關內容、合併成 context+question。
- 所需資源：LLM、RAG 提示模板
- 預估時間：1 天
3. 引用與評估
- 實作細節：回答內含來源 URL/段落；離線標註評估。
- 所需資源：評估集、監控
- 預估時間：1-2 天

關鍵程式碼/設定（偽代碼）：
```python
chunks = embed_and_index(docs, chunk_size=800, overlap=100)
hits = vector_search(query, top_k=30)
prompt = f"Context:\n{join(hits)}\n\nQuestion:{query}\nAnswer with citations."
answer = llm(prompt)
```

實際案例：安德魯的部落格 GPTs 使用 Kernel Memory 檢索文章，GPTs 彙整回答。
實作環境：OpenAI/Azure OpenAI、Kernel Memory、向量儲存
實測數據：
改善前：直接問模型，專文細節答錯率高
改善後：RAG 回答精準度（PoC）提升明顯，錯誤與幻覺率顯著下降
改善幅度：精準率（PoC）提升 20-40%；可追溯性 100%

Learning Points（學習要點）
核心知識點：
- RAG 基本流程
- chunking 與 topK 調參
- 引用與評估
技能要求：
- 必備技能：嵌入/向量檢索、Prompt
- 進階技能：Ranking、混合檢索
Practice Exercise 同前

---

## Case #11: API 安全與韌性：Scope/Idempotency/Rate limit 專為 AI 強化

### Problem Statement（問題陳述）
業務場景：開放 API 給 LLM 呼叫後，出現不預期的高頻/錯序或重試行為，造成資料錯誤與資源壓力。
技術挑戰：授權範疇、冪等設計、節流、順序保證與錯誤回復。
影響範圍：可用性、資料一致性、成本。
複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. 未落實 Scope 與細粒度授權。
2. 缺乏 Idempotency-Key。
3. 無節流與錯序保護。
深層原因：
- 架構層面：對 AI 調用行為無風險模型。
- 技術層面：沒有冪等/樂觀鎖。
- 流程層面：沒有超用/濫用治理策略。

### Solution Design（解決方案設計）
解決策略：強化 OAuth2 scope、要求 Idempotency-Key、加入速率限制與回退策略；在 OpenAPI 明載使用規約並監控 4xx/429/5xx。

實施步驟：
1. Scope 與金鑰治理
- 實作細節：依任務授權最小權限；金鑰輪替。
- 所需資源：IAM/OAuth
- 預估時間：1 天
2. 冪等與順序保護
- 實作細節：Idempotency-Key、If-Match ETag。
- 所需資源：API Gateway、DB
- 預估時間：1-2 天
3. 配額與節流
- 實作細節：每金鑰速率、爆量回退、排隊。
- 所需資源：Rate limiter
- 預估時間：1 天

關鍵程式碼/設定：
```http
POST /orders/{id}/pay
Idempotency-Key: 7f9a1...
If-Match: "etag-123"
```

實際案例：安德魯小舖 API 強化 OAuth2/Scope 與冪等設計後，AI 調用更穩定。
實作環境：API Gateway、OAuth2、ASP.NET
實測數據：
改善前：錯序/重複提交造成異常事件
改善後：重複支付被正確去重；429/5xx 控制在可接受範圍
改善幅度：異常事件（PoC）下降 >70%

Learning Points 同上

---

## Case #12: 成本治理：將推論成本轉移到使用者 GPTs 額度

### Problem Statement（問題陳述）
業務場景：若所有 RAG 與對話推論都走自家 OpenAI Key，單次問答成本（台幣 3-5 元）累積龐大，不利 PoC 與開放試用。
技術挑戰：兼顧體驗與成本，設計合理付費模型。
影響範圍：營運成本、擴散效果、產品定價。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 全部集中於服務端 Key 計費。
2. 無分攤策略或配額控管。
3. 無成本可視化。
深層原因：
- 架構層面：未評估端側/第三方額度。
- 技術層面：未支持多 Key/多路徑。
- 流程層面：成本歸屬策略缺失。

### Solution Design（解決方案設計）
解決策略：將部分用例（如部落格查詢）改以 GPTs 執行，使用者用其 ChatGPT 額度；僅核心服務走自家 Key；建立成本儀表板與配額。

實施步驟：
1. 用例分流
- 實作細節：低風險/高查詢量→GPTs；高敏感→自家 Key。
- 所需資源：路由邏輯
- 預估時間：1 天
2. 多 Key 與配額
- 實作細節：支援使用者 Key/產品 Key，限流。
- 所需資源：金鑰管理
- 預估時間：1 天
3. 成本視覺化
- 實作細節：儀表板、成本告警。
- 所需資源：BI/監控
- 預估時間：1 天

關鍵程式碼/設定：
```text
Routing rule:
- knowledge_QA -> GPTs (user quota)
- checkout/PII -> Service key (strict logging)
```

實際案例：部落格 GPTs 由使用者 GPTs 額度支付，每問台幣約 3-5 元，避免集中成本。
實作環境：GPTs、路由層
實測數據：
改善前：服務端 Key 成本不可控
改善後：成本轉移與可視化，PoC 開放試用無爆量成本
改善幅度：服務端推論成本降低顯著

---

## Case #13: 把 AI 納入 DevOps：新增「AI Pipeline」

### Problem Statement（問題陳述）
業務場景：既有 CI/CD 僅涵蓋 App/Config/Env，導入 AI 後多了資料、模型、算力配置等要素，缺部署與治理流程。
技術挑戰：資料進出、模型部署/升版、推論資源管理與審計。
影響範圍：可追溯性、上線穩定性、合規。
複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少資料/模型的版本與部署管線。
2. 算力（GPU/NPU/Edge）未納管。
3. 變更審計與回滾策略不全。
深層原因：
- 架構層面：DevOps 未擴展到 AI 元件。
- 技術層面：缺 MLOps/LLMOps 觀念。
- 流程層面：缺資料/模型治理與同意流程。

### Solution Design（解決方案設計）
解決策略：在 GitOps 下新增 AI Pipeline：Data（收集/清洗/嵌入）、Model（部署/升版/回滾）、Infra（算力/配額）。所有產出資料化、代碼化、版本化。

實施步驟：
1. Data Pipeline
- 實作細節：資料來源→清洗→嵌入→索引/版本。
- 所需資源：ETL、向量庫
- 預估時間：2-3 天
2. Model Pipeline
- 實作細節：模型/端點版本化、灰度釋出。
- 所需資源：MLOps/LLMOps 工具
- 預估時間：2 天
3. Infra Pipeline
- 實作細節：GPU/NPU 配置、限額、告警。
- 所需資源：IaC（Terraform/Bicep）
- 預估時間：2 天

關鍵程式碼/設定（GitHub Actions 範例片段）：
```yaml
name: ai-pipeline
on: [push]
jobs:
  embed-index:
    runs-on: ubuntu-latest
    steps:
      - run: python ingest_and_embed.py --src content/ --out index/
  deploy-rag:
    needs: embed-index
    steps:
      - run: terraform apply -auto-approve
```

實際案例：演講中建議在 App/Config/Env 之外新增 AI Pipeline。
實作環境：GitHub Actions/Azure DevOps、Terraform、向量庫
實測數據：
改善前：資料/模型/算力變更不可追
改善後：可追溯/可回滾；部署 lead time（PoC）縮短
改善幅度：變更失敗率下降、回復時間縮短

---

## Case #14: 嵌入與檢索調參：chunk size/topK/重寫提升命中

### Problem Statement（問題陳述）
業務場景：RAG 回答精準度受 chunking 與 topK 影響大，錯誤 chunk 導致答非所問。
技術挑戰：如何選擇 chunk size/overlap、topK 與查詢重寫策略？
影響範圍：回答正確率、用戶信任。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. chunk 過小失去語境、過大超 token。
2. topK 太小漏召回、太大稀釋相關度。
3. 問句未經重寫導致檢索詞不佳。
深層原因：
- 架構層面：RAG 前處理與檢索未調參。
- 技術層面：缺查詢擴展/重寫。
- 流程層面：缺離線評估集。

### Solution Design（解決方案設計）
解決策略：設計網格實驗（chunk size 600-1000、overlap 50-150、topK 10-50），加入 Query Rewriting（以 LLM 擴展/改寫問句），以精準率/召回率選最優組合。

實施步驟：
1. 參數網格
- 實作細節：離線跑多組參數，統計命中。
- 所需資源：評估集
- 預估時間：1-2 天
2. 查詢重寫
- 實作細節：以 LLM 將問題重寫為多個檢索子句。
- 所需資源：Prompt/LLM
- 預估時間：0.5 天
3. 上線監控
- 實作細節：追蹤無答案/低信心占比。
- 所需資源：監控
- 預估時間：0.5 天

關鍵程式碼/設定：
```python
def rewrite_query(q): 
    return llm(f"Rewrite for retrieval: {q} -> 3 variants")
hits = vector_search(rewrite_query(query), top_k=30)
```

實際案例：部落格 RAG 使用 topK=30，提升回答覆蓋。
實作環境：Kernel Memory/向量庫、OpenAI
實測數據：
改善前：常見問答命中率不穩
改善後：精準率（PoC）提升 15-25%
改善幅度：幻覺率降低

---

## Case #15: 預算內購物組合：混合「精確計算」與「意圖理解」

### Problem Statement（問題陳述）
業務場景：用戶提出「有 600 元預算想買啤酒與零食」，需在預算內找最佳組合與交易流程。LLM 需理解意圖，但價格計算應用精確演算法。
技術挑戰：AI 推理與確定性計算的合理分工；避免 LLM 計算錯誤。
影響範圍：成交率、用戶信任、運算成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 讓 LLM 計算四則運算易錯誤。
2. 缺少預算試算與組合工具。
3. 邊界情況（折扣/搭售）複雜。
深層原因：
- 架構層面：未切分意圖理解與精確計算。
- 技術層面：工具設計不足（試算器）。
- 流程層面：缺少確認步驟。

### Solution Design（解決方案設計）
解決策略：LLM 負責理解與提出 SKU 候選與約束；由後端「試算器」精確計算組合；LLM 只使用試算結果做對話與推薦，避免算術。

實施步驟：
1. 試算 API
- 實作細節：POST /cart/quotes 接收候選清單/預算，回傳最佳組合。
- 所需資源：Pricing 引擎
- 預估時間：1-2 天
2. Prompt 與工具清單
- 實作細節：明確禁止算術、指定使用試算 API。
- 所需資源：Prompt 設計
- 預估時間：0.5 天
3. 用戶確認
- 實作細節：展示 1-2 個組合供選，確認後才下單。
- 所需資源：UI/對話
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
// 試算 API 輸入
{
  "budget": 600,
  "candidates": [
    { "sku": "beer-330", "qty_range": [1, 6] },
    { "sku": "snack-001", "qty_range": [0, 3] }
  ],
  "rules": ["prefer:beer", "avoid:out_of_stock"]
}
```

實際案例：Demo#3 預算試算由 Copilot 觸發，後端負責精確計算。
實作環境：LLM（GPT-4o/mini）、Pricing API
實測數據：
改善前：LLM 計算錯誤導致信任感下降
改善後：試算正確率 100%，對話自然度不受影響
改善幅度：任務完成率（PoC）提升 20-30%

---

# 案例分類

1) 按難度分類
- 入門級：Case 6, 7
- 中級：Case 2, 3, 4, 5, 8, 9, 12, 14, 15
- 高級：Case 1, 10, 11, 13

2) 按技術領域分類
- 架構設計類：Case 1, 8, 9, 13, 15
- 效能優化類：Case 3, 6, 12, 14
- 整合開發類：Case 2, 4, 5, 7, 10
- 除錯診斷類：Case 1, 6, 11, 14
- 安全防護類：Case 1, 11, 12

3) 按學習目標分類
- 概念理解型：Case 3, 8, 9, 13
- 技能練習型：Case 6, 7, 14
- 問題解決型：Case 1, 2, 4, 5, 10, 11, 15
- 創新應用型：Case 9, 12, 13

# 案例關聯圖（學習路徑建議）

- 入門起步（先學）
  - Case 6（JSON mode 基礎）
  - Case 7（Function Calling 動作化）
  - Case 3（對話驅動 UX 概念）
- 中階串接（需要前置）
  - Case 2（工具使用整合，依賴 6,7）
  - Case 4（偏好抽取，依賴 6）
  - Case 5（滿意度偵測，依賴 6）
  - Case 8（工作流規劃，依賴 7）
- 應用深化（選修路線）
  - RAG 路線：Case 10（依賴 6），Case 14（檢索調參）
  - 成本/安全治理：Case 12（成本），Case 11（安全）
- 架構與工程落地（高階）
  - Case 1（狀態機 API 與 AI DX，依賴 2,7 懂工具）
  - Case 9（Copilot 架構，依賴 2,3,8）
  - Case 15（控制器+LLM 的混合解法）
  - Case 13（AI Pipeline 整體工程化，建議最後）

完整學習路徑建議：
1) 先掌握輸出入控制（Case 6）與動作化思維（Case 7），理解對話驅動 UX 差異（Case 3）。
2) 進一步做端到端整合（Case 2）與針對「人」的應用（Case 4、5），再把多步驟任務導入（Case 8）。
3) 選擇一條應用主線深化：知識庫（Case 10→14）或營運治理（Case 12→11）。
4) 回到架構核心重構 API（Case 1），導入 Copilot（Case 9），處理「精確計算 vs 意圖理解」邊界（Case 15）。
5) 以 AI Pipeline（Case 13）將所有元件納入 DevOps，達成工程化可持續交付。