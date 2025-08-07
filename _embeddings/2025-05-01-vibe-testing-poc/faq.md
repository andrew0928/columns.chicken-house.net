# 從 Intent 到 Assertion #1：聊聊 Vibe Testing 實驗心得

# 問答集 (FAQ, frequently asked questions and answers)

## Q: AI 真的能取代工程師手寫 Script，直接自動化 API 測試嗎？
可以。作者用 Microsoft Semantic Kernel + OpenAI Function Calling 做了一個 Test Runner，讓 LLM 依測試情境自行決定要呼叫哪些 API、組出參數、執行並生成報告。PoC 成功跑完 15 個情境，證明「只出一張嘴就能完成 API 自動化測試」是可行的。

## Q: 什麼叫「從 Intent 到 Assertion」？
Intent 指「想驗證什麼」（業務意圖或 AC），Assertion 指「判斷結果是否符合預期」。理想狀態是：人類只負責描述 Intent，LLM 便能自動推論執行步驟、呼叫 API、收集結果並進行 Assertion，最終產生測試報告。

## Q: 這次 PoC 用到了哪些關鍵技術？程式量多嗎？
1. Microsoft Semantic Kernel  
2. OpenAPI ↔ Plugin 自動轉換（`ImportPluginFromOpenApiAsync`）  
3. OpenAI ChatCompletion（Function Calling, Structured Output）  
4. .NET 8 Console App  
總共約 50 行關鍵程式即可串起整個流程。

## Q: Test Runner 如何把 OpenAPI 規格變成 LLM 可用的工具？
透過 Semantic Kernel 內建的 `ImportPluginFromOpenApiAsync(...)`，把 Swagger 檔一次轉成 Plugin。Kernel 在推論過程中會自動決定何時呼叫這些 Plugin（即 API），工程師無須手動撰寫 16 支 API 的包裝函式。

## Q: 想用同樣方式測試自己的 API，需要具備哪些「AI Ready」條件？
1. API 必須以 Domain 思維設計，而非純 CRUD。  
2. 要有完整且精確的 OpenAPI/Swagger 文件，且能隨 CI/CD 自動產生。  
3. 認證／授權機制要標準化，方便在 Test Runner 裡一次處理（例如 OAuth2、JWT）。若缺任一條件，Function Calling 驅動的自動化測試將難以落地。

## Q: 為什麼作者同時要求輸出 JSON 結構化報告，而不只 Markdown？
Markdown 便於人閱讀；但真正在大量案例或 CI pipeline 中，需要機器可解析的統計與告警能力，因此額外要求 LLM 再輸出一份符合 JSON Schema 的結構化結果，方便後續系統整合與自動彙整。

## Q: 這種 Domain-level 測試案例未來能直接拿去測 UI 嗎？
原理上可以。只要 UI 也有標準化規格（例如 Browser Use、Computer Use 等工具準備就緒），再換一個對應的 Test Runner，即可用同一份情境去驗證 Web、Android、iOS 等多介面行為。

## Q: 這項實驗帶來的主要啟示是什麼？
1. LLM + Function Calling 已成熟到能接手「執行測試」這類高度模板化又勞力密集的工作。  
2. 真正的挑戰在「讓系統 AI Ready」：好的 API 設計、文件、自動化工程與環境控制。  
3. 開發者價值將從「寫程式快」轉向「更懂得如何引導 AI 把事做好」。