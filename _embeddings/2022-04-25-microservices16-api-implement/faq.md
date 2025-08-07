# 微服務架構 - 從狀態圖來驅動 API 的實作範例

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在設計微服務會員系統的 API 時，首要工作是先建立「有限狀態機 (FSM)」？
使用 FSM 先把「資料狀態」與「可允許的行為」全部標示出來，可以：
1. 讓 API 介面直接源自於狀態轉移，避免過度或不足設計。  
2. 把存取控制(誰能在什麼狀態呼叫哪個 Action)明確地標在圖上，後續程式碼只要照圖驗證即可。  
3. 提供一致的驗證點：所有 API 呼叫都能先交給 FSM 判斷是否可執行，再真正動到資料，確保一致性與可預期性。

## Q: API 的安全機制應該什麼時候考慮？核心要素有哪些？
安全機制必須在「設計階段」就與 API 規格一起思考，不能等到功能完成後才補。  
核心要素只有三件事：  
1. 認證 (Authentication)：你是誰？  
2. 授權 (Authorization)：你被賦予了哪些權限？  
3. 存取控制 (Access Control)：要執行某功能需要具備哪些權限與條件？  
在文章的實作中，以 JWT Token 承載「IdentityType(USER/STAFF)」與「IdentityName」來解決認證與授權，再把 Token 與 FSM 結合，於 Middleware 統一檢查存取控制，達到安全模型與 API 設計的一致性。

## Q: 為什麼示範專案要拆成 Contracts、Core、WebAPI、CLI、Tests 等多個 Project？
1. Contracts：定義跨服務、跨專案都要遵守的介面與資料模型(合約)；一旦發布需長期相容。  
2. Core：實作真正的 Domain Logic (FSM、會員行為、Repository 等)，讓其他層只負責「如何呼叫」。  
3. WebAPI：把 Core 行為包裝成 HTTP 端點，處理通訊格式、Middleware 與錯誤轉換。  
4. CLI：提供批次或命令列工具，重用相同的 Core 邏輯做管理或測試。  
5. Tests：用單元測試佐證 Contracts 與 Core 的行為正確，也當作最精準的使用範例。  
如此分層可以讓 Domain 邏輯與通訊技術解耦，方便重用、測試與後續演進。

## Q: WebAPI 層如何集中處理安全驗證與 FSM 規則，而不把檢查程式散落在每支 API？
做法是自訂一個 `MemberServiceMiddleware`：  
1. 讀取 HTTP Header 的 Bearer Token → 解析並驗證 JWT → 注入 `MemberServiceToken`(Scoped)。  
2. 透過路由與自訂 `MemberServiceAction` Attribute 取得「ActionName」、「MemberId」，呼叫 FSM 先行驗證。  
3. 若驗證失敗在 Middleware 就回傳 403/500，成功才交由 Controller 執行。  
如此 Controller 只需呼叫 Core 的 Service，安全與狀態檢查集中於 Middleware 與 Core，不重複撰寫。

## Q: 如何在還沒寫完整系統前就驗證 API 規格的正確性與可用性？
文章示範「先寫測試再實作」：  
1. 依照真實情境把註冊、登入、鎖帳號…等流程寫成 Unit Tests。  
2. 若測試過程發現輸入/輸出資訊不足，立刻回頭調整 Core 介面或 Contracts。  
3. 測試一綠燈，代表 API 規格及其安全／狀態檢查能支援實際業務流程。  
這種方式能在 PoC 階段就把規格問題暴露並修正，降低日後「破壞性改版」的機率。