# 從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得

## 摘要提示
- AI-Ready API: API 若具備完善的領域封裝與 OpenAPI 規格，LLM 才能精準執行 Function Calling。
- Intent→Assertion: 以 LLM 取代人工，從「測什麼」到「怎麼判斷」的整段流程自動化。
- Test Runner PoC: 用 .NET + Semantic Kernel 匯入 Swagger 成 Plugin，僅約 50 行核心碼即可跑通。
- Given/When/Then: 透過 System Prompt 將 BDD 模式固化，AI 依步驟呼叫 API 並生成報告。
- OAuth2 插件化: 事先處理統一認證，讓測試專注於業務邏輯而非登入流程。
- 結構化輸出: Markdown 給人讀，JSON 給系統整合，方便大量測試統計與警示。
- 領域案例抽離: 測試案例描述僅含業務語意，與 UI 或 API 參數脫鉤，利於多介面重用。
- AI Ready 門檻: 沒有標準化規格與認證機制，再好的 LLM 也難以自動化測試。
- DevOps 新養成: 未來比拼的不再是手寫腳本，而是誰能更好地引導 AI 把事做對。
- 後續計畫: 將再撰文探討案例展開與規模化議題，包含 MCP 與大規模報告彙整。

## 全文重點
作者以「Vibe Testing」為名，驗證以 LLM + Function Calling 取代傳統腳本，完成 API 自動化測試的可行性。核心想法是把測試拆成三層：1) 業務意圖與驗收標準（Intent/AC）；2) 領域測試案例（Given/When/Then）；3) 具體執行步驟與 Assertion。過去第二、三層須人工撰寫腳本，如今藉由 LLM 的 Tool Use 能力，自動從案例推論要呼叫哪些 API、生成參數、比對結果並出報告。

實作上，作者沿用先前「安德魯小舖」購物車 API，準備一組「加入 11 件可口可樂應回 400」的案例。藉由 .NET Console + Microsoft Semantic Kernel，僅用十多行就把 Swagger 匯成 Plugin，並透過三段 Prompt（System、TestCase、Report）驅動模型。Kernel 自動決定何時呼叫 API、填入 OAuth2 Token、串接前後步驟結果，最終同時輸出 Markdown 與 JSON 報告。測試失敗符合預期，證明流程通順。

作者歸納 AI 自動化測試的前提：API 必須按照領域建模、提供精確且自動產生的 OpenAPI 文件、統一認證授權機制，並需要系統化收斂測試報告。若基礎工程不足，AI 只會放大技術債。文章最後提醒開發者思考「如何用 AI 做工具」而非僅「用 AI 寫程式」，並預告後續將深入案例展開與規模化實務。

## 段落重點
### 構想：拿 Tool Use 來做自動化測試
作者將「從 Intent 到 Assertion」視為人腦轉譯測試的過程，思考以 LLM 取代人工。只要具備 AC、領域知識與 API 規格，LLM 透過 Function Calling 便能自行決定要呼叫的 API 及參數，完成驗證並輸出報告。未來若 Browser Use 等技術成熟，理論上同一份案例可同時驗證 Web、App、API 多種介面。

### 實作：準備測試案例 (domain)
示範案例要求在空購物車中加入 11 件商品應被拒絕並保持空車。案例刻意抽象化，只描述商業行為與期望結果，避免與任何 UI 或參數綁死，利於重用與 Review。寫好案例後，由 LLM 自行展開具體步驟。

### 實作：準備 API 的規格 (spec)
沿用「安德魯小舖」購物車 Swagger，手動推演：建立購物車→查商品→嘗試加購→查詢購物車。這些呼叫將由 LLM 完成。作者強調若缺乏精確 Spec，LLM 無從生成正確 Request，測試將無法自動化。

### 實作：挑選對應的技術來驗證
以 .NET Console + Semantic Kernel 實作 Test Runner。1) Import PluginFromOpenApi 省去手寫 16 個函式；2) 三段 Prompt 固化流程與報告格式；3) PromptExecutionSettings 設為 Auto 讓 Kernel 自動處理 Function Calling 往返。OAuth2 透過 Plugin 先行解決，執行約 1 分鐘生成報告。Markdown 便於閱讀；JSON 便於系統整合。

### 心得
AI 自動化測試的關鍵瓶頸在「AI Ready」。API 若是單純 CRUD、文件不精確、認證雜亂，就無法仰賴 LLM。作者建議：1) 以領域驅動設計 API；2) 依 CICD 自動產生 Swagger；3) 將環境控制（認證、語系、貨幣）插件化；4) 用結構化輸出收攏大量結果。透過 Structure Output + Function Calling，工程師能快速組裝跨系統整合工具。本文僅揭露約三成內容，後續將補充測試案例展開與大規模化實務。