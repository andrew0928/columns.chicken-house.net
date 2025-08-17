# 從 Intent 到 Assertion #1 ─ 聊聊 Vibe Testing 實驗心得

## 摘要提示
- Function Calling: 透過 LLM 的 Tool Use 能力，將「意圖→行動→斷言」全自動化執行 API 測試。
- Test Runner: 以 Microsoft Semantic Kernel + OpenAPI Plugin 打造不到 50 行核心程式的測試執行器。
- Domain Test Case: 先撰寫 Given/When/Then 的領域情境，不含技術細節，再交由 AI 展開步驟。
- OpenAPI 匯入: Swagger 規格一鍵轉 Plugin，讓 AI 自行決定 URI、Header 與 Payload。
- Prompt Engineering: System/User Prompt 區分測試鐵律、案例內容與報告格式，保證可重複性。
- Structured Output: 同步輸出 Markdown 與 JSON，便於人工閱讀與系統彙整。
- API Ready: 要有領域導向設計、精確規格、統一認證，否則自動化效益有限。
- OAuth2 處理: 以獨立 Plugin 先取得 Access Token，再由 AI 帶入每次呼叫。
- 結果驗證: 限購 10 件的案例如預期測試失敗，證明流程與報告皆可信。
- 未來方向: 規模化、跨介面測試（Web/UI）、MCP 整合與環境控制等將續篇探討。

## 全文重點
作者以「購物車 API 測試」為例，驗證 Large Language Model 的 Function Calling 能力能否從最上層「Intent（測試意圖）」一路完成「Assertion（驗證）」並產生報告。首先準備純領域敘事的 Given/When/Then 測試案例，再搭配完整 Swagger 規格與 OAuth2 認證資訊，交給用 Semantic Kernel 打造的 Test Runner。Kernel 利用「Import OpenAPI」將 16 個 API 轉成 Plugin，LLM 依據 System Prompt 所定義的鐵律決定呼叫順序、組裝參數並實際向遠端服務發送請求。執行過程中，Runner 動態插入 Access Token，並以 HTTP Logger 印出所有 request/response 以便追蹤。完成後 AI 依指示輸出 Markdown 報告與結構化 JSON，顯示「嘗試加入 11 件可口可樂」未收到 400，而購物車仍含 11 件，故判定 test_fail；此結果符合作者預設「功能尚未實作」的紅燈預期。實驗證實：只要 API 符合「AI Ready」條件（領域導向、規格精準、統一認證），AI 可取代大量腳本撰寫及手動維護成本；反之則應先提升工程成熟度。作者最後提出五點心得：API 要封裝商業邏輯、文件要自動生成、認證要標準化、報告要可彙整，並呼籲開發者從「使用 AI 工具」晉升到「用 AI 做工具」。後續文章將探討案例生成、規模化與多介面測試的細節。

## 段落重點
### 1. 構想：拿 Tool Use 來做自動化測試
作者觀察 LLM 已能充當 Agent，自然聯想到把 Function Calling 應用於 API 測試。人做測試會先理解 AC 和領域知識，再翻譯成操作與斷言；LLM 亦可透過 Tool Use 重現此流程，省去撰寫繁瑣腳本。同時若未來 Browser/Computer Use 成熟，單一 Domain Test Case 還可擴展至 Web、Android、iOS 等多介面驗證，真正實現「Write once, Test anywhere」。

### 2. 實作：準備測試案例 (Domain)
示範案例為「空購物車加入 11 件可口可樂」。Given 清空購物車並指定商品；When 加入 11 件再查詢；Then 期望 API 回 400 且購物車為空。作者強調先聚焦「測什麼」而非「怎麼測」，保持案例與介面規格解耦，便於未來 UI 與 API 同步使用。

### 3. 實作：準備 API 規格 (Spec)
沿用「安德魯小舖」購物車 API 與對應 Swagger。作者先人腦推演：用 CreateCart 取代清空、用 GetProducts 找商品，再依案例呼叫 AddItemToCart 與 GetCart。精確規格是 AI 能自行組裝呼叫的前提，人工維護則無法支持高頻測試。

### 4. 實作：挑選技術驗證
選 .NET Console + Semantic Kernel。  
4-1 將 OpenAPI 轉 Plugin：十行程式導入完整 API 並處理 OAuth2。  
4-2 Prompt 準備：System Prompt 定 SOP、User Prompt 放案例與報告格式；啟用 FunctionChoiceBehavior.Auto 讓 Kernel 自動挑選函式。  
4-3 測試報告：AI 確實呼叫 API、攜帶 Access Token，最後輸出 Markdown 與 JSON。結果顯示測試失敗，符合預期紅燈。

### 5. 心得
5-1 API 須領域導向避免 CRUD 失控；  
5-2 規格文件要自動產生保持同步；  
5-3 認證授權應統一並由 Runner 代管；  
5-4 報告需結構化以利統計與警示；  
5-5 小結：Function Calling + Structured Output + 正確 Prompt 已可組裝跨系統 Test Runner，未來將續談案例展開與規模化挑戰。