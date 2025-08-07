# 微服務架構 - 從狀態圖來驅動 API 的實作範例

## 摘要提示
- 狀態機設計: 以 FSM 抽象會員帳號生命週期，統一標註動作、狀態與授權。
- 分層架構: Solution 切分 Contracts、Core、WebAPI、CLI、Tests 五層，明確責任邊界。
- 安全模型: 以 JWT 作為 MemberServiceToken，結合認證、授權與存取控制。
- AOP 與鎖定: 透過 SafeChangeState 與 Middleware 統一檢查 FSM 與競態鎖定。
- 單元測試驅動: 先寫測試案例驗證 API 規格，再補齊實作降低重工。
- 事件機制: 以 C# Event 做內部 Pub/Sub，方便改寫成 MQ 或 Webhook。
- Middleware: 在 HTTP Pipeline 解析 Token、套用狀態機規則、統一錯誤格式。
- Controller 最小化: 僅負責參數繫結與呼叫 Core，維持乾淨介面。
- 可擴充授權: USER/STAFF 雙身分示範，保留多租戶與外部系統授權空間。
- 實戰 PoC: 提供 GitHub 專案與 Postman 範例，完整走通註冊、啟用、鎖定流程。

## 全文重點
作者承接前一篇理論，示範如何把「用狀態機驅動 API」落地成 .NET 微服務。首先以會員帳號為 Domain，利用 FSM 抽象 START→CREATED→ACTIVATED→DEACTIVED→ARCHIVED→END 等狀態，並將每條轉移線附帶 action 名稱與可執行身分（USER/STAFF）。接著將 Solution 拆為 Contracts(合約)、Core(商業邏輯)、WebAPI(通訊)、CLI(工具)與Tests(驗證)，在 Core 內定義 MemberService 與 MemberStateMachine。安全機制採 JWT，將身分與授權寫入 MemberServiceToken；Middleware 於每次 HTTP 進來時解析 Authorization Bearer，產生 scoped Token 注入 DI，再透過自製 Attribute 取得 action 名稱，呼叫 FSM 先行檢查，若違規即回 403/500。

資料一致性則以 SafeChangeState 封裝：先鎖定資料、再二次比對狀態、執行 lambda 內的業務更新、最後統一改狀態並觸發 OnStateChanged 事件，可延伸為 MQ。單元測試先寫完整場景（註冊→驗證→登入→連錯三次鎖帳→客服解鎖等），讓 API 介面在 code 被動態檢視與修正。WebAPI Controller 僅做 Model Binding；Postman 測試證明 STAFF 可查全庫，USER 受限於 FSM 規則。作者強調：微服務雖「微」，但設計、安全、日誌、事件一個都不能少；抽象化與一致性比炫技術更重要。

## 段落重點
### 重新複習: 系統設計與狀態機
說明會員服務在微服務中的定位：服務內部系統而非直接對外 UI；用 FSM 收斂需求，點為狀態、線為動作，線上標註可執行身分，形成後續 API 清單與授權基礎。

### 專案分層說明
介紹五個 Project：Contracts 定義合約；Core 實作 Domain 與 Business；WebAPI 提供 HTTP；CLI 產生 Token 與批次；Tests 驗證。示範刻意省略 DB 與標準 JWT Middleware，以 In-Memory Repo 與 jose-jwt 精簡 PoC。

### API 的安全機制 - Token
將認證、授權、存取控制三要素落入實作：JWT 承載 IdentityType/Name；TokenHelper 產生與驗證簽章；CLI 產出 USER、STAFF 範例 Token。闡述金鑰管理與對稱/非對稱選擇。

### StateMachine
用 Enum 列舉狀態、Tuple 描述轉移(action, init, final, allowRoles)。提供 CanExecute 方法回答「此身分能否在此狀態執行動作」並回傳最終狀態，成為中樞警察。

### Core Service
MemberService 透過 DI 注入 Token、FSM、Repo；公開方法即 FSM Action。SafeChangeState 封裝鎖定、雙檢、狀態改寫與事件觸發；樂觀鎖處理競態；OnStateChanged 事件方便外送 MQ。

### 單元測試案例
先寫測試推導 API：模擬 USER 註冊、驗證失敗/成功、連錯鎖帳、客服解決等全流程，Assert 驗證狀態與權限。透過測試調整介面，確保 Spec first 而非後補。

### 整合 State Machine 與事件
講解 SafeChangeState 內部流程與 AOP 思路；事件用 C# event 實作 logger，日後可換 MQ/Webhook。強調集中處理帶來的一致性與維護性。

### WebAPI: 從 Core 到 HTTP
Controller 以 Attribute 標 action，僅轉呼 Core；Startup 註冊 Singleton/Scoped；Middleware 解析 Bearer Token、套用 FSM、統一錯誤。示範 Postman 測試 STAFF 查詢成功、USER 被 403，以及完整註冊至登入場景。

### 結論
透過 FSM + JWT + 分層實踐，展示專業團隊應具備的 API 設計與落地能力。微服務需「精簡而不簡陋」，抽象化正確才能安全迭代。附兩本書《持續 API 管理》《API Design Patterns》與 GitHub 原始碼供深入。