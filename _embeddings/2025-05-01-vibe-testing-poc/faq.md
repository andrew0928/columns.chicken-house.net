# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者想用 AI 來簡化 API 自動化測試？
作者觀察到近兩年 LLM 的 Function Calling / Tool Use 能力已經十分成熟，AI 不只可以完成對話式購物等 Agent 工作，也應該能把「測試意圖 (Intent)」轉成實際呼叫 API 並比對結果 (Assertion) 的流程自動化，省去工程師撰寫測試腳本與手動維運的時間。

## Q: 什麼是「從 Intent 到 Assertion」？
「Intent」指測試者真正想驗證的行為或商業規則；「Assertion」則是驗證結果是否符合預期的斷言。作者的目標是讓 AI 讀懂高層次的測試意圖，自己決定該呼叫哪些 API、組合哪些參數，最後自動生成斷言與報告，完整覆蓋這段流程。

## Q: 這次 PoC 用了哪些主要技術？
1. .NET Console App  
2. Microsoft Semantic Kernel + Plugins  
3. 透過 `ImportPluginFromOpenApiAsync()` 把 Andrew Shop 的 OpenAPI Spec 直接轉成可呼叫的 Kernel Plugin  
4. OpenAI 模型 (o4-mini) 負責 Function Calling 與推論  
5. 自訂 Prompt Template（含 System/User 多段訊息）與 Structured Output 產生 Markdown / JSON 雙格式報告

## Q: PoC 的測試案例是什麼？結果如何？
案例：在空購物車加入 11 件「可口可樂」，預期 API 應回 400 Bad Request（因單品上限 10 件），且購物車最終應為空。  
結果：AI 正確依序呼叫 `CreateCart`、`GetProducts`、`AddItemToCart`、`GetCart`，但 API 回傳 200 並將 11 件商品加入購物車，測試標記為 `test_fail`，驗證 API 尚未實作此限制。

## Q: 要讓 AI 驅動的 Test Runner 順利運作，API 端需要滿足哪些條件？
1. 依領域概念設計，避免純 CRUD，讓商業邏輯封裝在 API 內 (Domain Driven, AI Ready)。  
2. 提供精確且與程式碼同步的 OpenAPI/Swagger 規格，否則 AI 無法正確組裝呼叫。  
3. 認證/授權機制需標準化並可由 Test Runner 統一處理（例如 OAuth2 取 token 後自動掛 Header）。  
4. 需要結構化輸出測試報告 (JSON) 供系統彙整，再產生易讀的 Markdown 給人查看。

## Q: 這項實驗帶來哪些啟示？
AI 已能可靠地處理「呼叫多支 API 並串連參數」這類中低複雜度邏輯，只要 API 與環境「AI Ready」，就能把大量撰寫測試腳本、維護資料與產出報告的工作交給 LLM，自動化效益將遠超過傳統錄製/回放或手寫 Script 的方式。