```markdown
# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得

# 問答集 (FAQ, frequently asked questions and answers)

## Q: AI 真的能取代工程師手動撰寫 Script，直接自動化執行 API 測試嗎？
是的。作者以「安德魯小舖」購物車 API 為範例，利用 LLM 的 Function Calling 能力與自製 Test Runner 成功完成 15 筆測試情境的自動化執行與報告產生，證實「從 Intent 到 Assertion」全流程可由 AI 代勞。

## Q: 要讓 AI 正確地從 Intent 走到 Assertion，需要先備妥哪些資訊？
1. 驗證目標（Acceptance Criteria / 測試意圖）  
2. 領域知識（業務流程、狀態圖等）  
3. 系統的精確規格（OpenAPI/Swagger、UI 流程說明、呼叫範例）  
有了這三者，LLM 才能把高階意圖拆成具體 API 呼叫並判斷回應。

## Q: 作者是怎麼把 OpenAPI 規格變成 LLM 可使用的工具？
透過 Microsoft Semantic Kernel 內建的  
```csharp
kernel.ImportPluginFromOpenApiAsync(...)
```  
大約 10 行程式碼即可把 Swagger 轉成 Kernel Plugin，讓 LLM 在對話中直接呼叫對應 API。

## Q: 為何強調 API 必須「AI Ready」並依領域設計，而非單純 CRUD？
若 API 只有 CRUD，商業規則落在呼叫端，AI 必須自行拼裝複雜邏輯，容易導致測試流程失控；領域驅動的 API 既封裝商業規則又易於 LLM 理解，才能穩定地由 AI 進行自動化測試。

## Q: 這次 PoC 的實際測試結果如何？
以「嘗試一次加入 11 件可口可樂」為例，AI 依序建立購物車、抓出商品 ID、呼叫加入 API 並驗證結果。因原 API 未實作「同商品數量上限 10 件」限制，AI 報告判定測試失敗 (test_fail)，顯示 PoC 能準確抓出規格與實作不符之處。

## Q: 除了 API 本身，還有哪些環境面向需先標準化？
• 統一的認證／授權機制（作者以 OAuth2 實作並在 Test Runner 內集中處理 Token）  
• 測試環境控制（語系、幣別、時區等）  
• 系統化蒐集與統計測試報告（AI 同步輸出 Markdown 給人看、JSON 給系統整合）

## Q: 為什麼 PoC 先做成 .NET Console App，而不是直接上 MCP 等大型平台？
此階段目的是驗證核心可行性；MCP 牽涉大規模推廣與額外技術門檻，屬後續優化議題，暫時跳過以聚焦實驗重點。

## Q: 後續作者還打算深入哪兩大主題？
1. 測試案例如何從 AC 系統性展開  
2. 規模化細節：MCP 整合、權限設計與其他周邊問題  
敬請期待接續文章。
```