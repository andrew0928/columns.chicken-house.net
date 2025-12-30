---
layout: synthesis
title: "微服務架構 - 從狀態圖來驅動 API 的實作範例"
synthesis_type: summary
source_post: /2022/04/25/microservices16-api-implement/
redirect_from:
  - /2022/04/25/microservices16-api-implement/summary/
---

# 微服務架構 - 從狀態圖來驅動 API 的實作範例

## 摘要提示
- 狀態機驅動: 以有限狀態機（FSM）統一收斂設計與實作，將行為、狀態與安全規則標註於狀態圖。
- 安全模型內建: 安全機制在設計期即融入（認證/授權/存取控制），以 Token + FSM 雙重把關。
- 分層與合約: Contracts/Core/WebAPI/CLI/Tests 清晰分工，Contracts 作為不可隨意破壞的介面合約。
- 簡化實作驗證: 以 in-memory repository、簡化 JWT 流程快速 PoC，聚焦架構與 API 設計驗證。
- Token 設計: 使用 JWT 承載 IdentityType/IdentityName 等，結合 Middleware 注入每次 Request 的 Scoped Token。
- FSM 稽核: MemberStateMachine 定義 action/起訖狀態/允許身分，統一以 CanExecute 驗證可否執行與轉移。
- 安全與一致性: SafeChangeState 封裝鎖定、驗證、轉移、事件，確保原子性與一致性（近似 AOP）。
- 單元測試導向: 以測試驅動驗證 API 規格與情境（註冊、啟用、登入失敗鎖定、客服協助重設等）。
- WebAPI 薄化: Controller 僅轉接參數與回傳結果；Middleware 先做 Token 解析與 FSM 前置檢核。
- 事件與擴展: 以 C# event 模擬事件通知，日後可替換為 MQ/Topic/Webhook 等分散式事件機制。

## 全文重點
本文延續「以狀態機驅動 API 設計」的方法，從概念落地到 .NET 實作，示範如何讓微服務在設計期就統一安全與行為約束，並以可運行的 PoC 驗證。作者先界定微服務中的會員領域服務，強調其主要服務對象為內部系統，並以 FSM 整合「狀態、行為、授權」：每個 action 在何狀態可執行、執行後轉往何狀態、允許哪些身分（USER/STAFF）呼叫。此 FSM 表述被轉化為程式內的資料結構與檢核方法，進而成為 API 規格與安全模型的單一真相來源。

工程上採 Contracts/Core/WebAPI/CLI/Tests 分層，Contracts 暨資料模型為合約；Core 負責領域行為、狀態機與安全機制整合；WebAPI 只承載通訊與注入；CLI 產生測試用 Token；Tests 以情境驗證規格。資料儲存簡化為 in-memory，但設計保留 Repository 與事件發送，將來可替換為資料庫與 MQ。安全機制以 JWT 承載 IdentityType（亦作授權）與 IdentityName（辨識操作者），藉 Middleware 於每個 HTTP Request 解析 Authorization: Bearer Token 並注入 Scoped Token，保證 Controller 與 Core 皆使用正確身分。配合 MemberServiceAction 屬性讓 Middleware 取得 actionName，先行依 FSM 做存取控制，實現 AOP 式的跨切關注點。

MemberStateMachine 用 tuple 列定 action/初末狀態/允許身分，提供 CanExecute 檢查；MemberService 以 SafeChangeState 封裝「鎖定→二次確認→執行業務→檢核狀態轉移→事件通知」的通用樣板，避免競態與不一致。單元測試完整演練註冊、啟用、登入錯誤達阈值鎖定、客服重發驗證碼與強制改密等情境，藉測試提早校正介面與規格；WebAPI 以極薄 Controller 直呼 Core，錯誤與安全由 Middleware 統一處理。最後以 Postman 驗證 STAFF/USER Token 在查詢/變更上的差異與 FSM 阻擋不合法序列。作者強調 API first/Spec first 應配合可運行的驗證與事件、日誌、追蹤等橫切設計，將抽象化與一致性落實於工程，為後續規模化與多團隊協作奠基。

## 段落重點
### 重新複習: 系統設計與狀態機
以會員領域為例，服務主要面向內部系統；作者主張以 FSM 將「狀態、行為、授權」收斂為單一模型，API 只是介面之一。對同一組 API，需區分 USER 與 STAFF 的可用行為與資料範圍。透過狀態圖與表格，使行為可被機器化解析與驗證：限制在合法狀態才能執行、執行後狀態如何轉移、誰被允許操作。這些標註將轉化為資料結構與程式檢核，成為後續實作與測試的規格基礎。設計重在抽象化到位：看得遠但只實作當下必要，保留未來替換實作而不破壞介面的空間。

### 專案分層說明
整體解決方案劃分為 WebAPI、CLI、Core、Contracts、Tests。Contracts 是跨專案合約與資料模型，須嚴格版本相容；Core 實作領域與商業邏輯，並落實 FSM 與安全驗證；WebAPI 專注通訊控制器；CLI 供產生 Token 與批次操作；Tests 驗證核心契約與行為。為專注設計與驗證，資料存取以 in-memory Repository 替代資料庫，認證授權以 jose-jwt 自行實作簡化 JWT 流程，強調未來在不破壞合約下可替換為正式方案。

### API 的安全機制 - Token
安全設計需在規格階段即納入，核心三要素是認證（你是誰）、授權（你能做什麼）、存取控制（做此事須具備哪些權限）。藉 JWT 的 MemberServiceToken 承載 IdentityType（USER/STAFF）與 IdentityName（操作者），實作上以對稱簽章簡化；CLI 提供示範 Token。在 FSM 上為各 action 標註允許身分，於執行時以 Token + FSM 決定可否執行。此模型讓行為與安全在同一張圖與同一份程式結構中保持一致，降低錯誤組合帶來的風險。

### StateMachine
以 enum 表達狀態，以 tuple（actionName, initState, finalState, allowIdentityTypes）清單表達轉移邊與授權，提供 CanExecute 查核。針對需指定會員的 action 回傳是否可執行及轉移後狀態；對非指定會員的服務（如 Import、查詢）則只檢查身分。FSM 成為可計算的規則庫，支援在程式內統一校驗操作合法性，並作為測試與文件的共同依據。

### Core Service
MemberService 集中領域行為（Activate/Lock/Reset…），在每個動作前後結合 FSM 與 Token 做合法性檢查。以 SafeChangeState 封裝共通模板：鎖定特定資料、二次驗證當前狀態與授權、執行業務邏輯、校驗狀態轉移符合 FSM、最後發出事件。單元測試以實際情境推導規格與介面（註冊→啟用→登入錯誤鎖定→客服協助重設），讓 API 設計在動手實作前先被驗證與修正，最終確保一致性與可演進性。

### 事件通知
透過 C# event 提供狀態變更事件，後續可替換為 MQ/Topic/Webhook 等分散式事件機制。事件屬於橫切關注點，與鎖定與轉移合併封裝於 SafeChangeState，保證一旦狀態變化就會有對應通知。建議以測試情境驗證事件定義與消費流程，確保架構擴展到跨程序/跨節點時仍維持同一套語義與約束。

### WebAPI, 從 Core 到 HTTP
WebAPI 層僅負責通訊轉接，Controller 以薄層直呼 Core。以 Middleware 於每個 Request 解析 Authorization Bearer Token，注入 Scoped Token，並讀取自訂屬性 MemberServiceAction 取得 actionName，在進入 Controller 前先做 FSM 檢核與錯誤統一回應，等同 AOP 前置攔截。DI 註冊 MemberRepo/MemberStateMachine 為 Singleton，Token/MemberService 為 Scoped，確保請求內身分一致且可被 Core 正確消費。以 Postman 驗證 USER/STAFF 權限差異與不合法序列被阻擋。

### 結論
以 FSM 驅動 API 能在單一模型內統一「狀態、行為、授權」，配合 Token 與 Middleware 實作跨切安全與一致性；Core 封裝 SafeChangeState 確保原子性與事件通知；測試先行用情境驗證規格，WebAPI 薄化專注通訊。這種 API first/Spec first 不是僅寫文件，而是以可運行的 PoC 驗證設計與工程落地。良好抽象化與合約穩定性使服務可持續擴展而不破壞相容，支撐多團隊協作與微服務規模化演進。附帶推薦持續 API 管理與 API Design Patterns 以深化方法論。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本 REST/HTTP 概念與狀態碼
- C#/.NET Core 基礎（類別、介面、委派、事件、DI）
- ASP.NET Core WebAPI、Controller、Middleware 基礎
- JWT/簽章與基本資安觀念（Authentication/Authorization）
- 資料結構與圖論中 FSM/State/Transition 概念
- 併發控制與交易基礎（樂觀/悲觀鎖、ACID）

2. 核心概念：本文的 3-5 個核心概念及其關係
- FSM 驅動的 API 設計：以狀態與動作（action）定義 API 可執行性與狀態轉移
- 安全模型三要素：認證（你是誰）+ 授權（你能做什麼）+ 存取控制（做事的條件）嵌入 FSM
- Token/JWT 作為執行身分載體：在 Token 中攜帶 IdentityType/IdentityName，供授權與稽核
- 分層與實作收斂：Contracts（合約）、Core（業務/安全/狀態）、WebAPI（通訊/轉接）、CLI（輔助）、Tests（驗證）
- AOP 化的防護與一致性：Middleware + Service 模板（SafeChangeState）統一檢查與事件驅動

3. 技術依賴：相關技術之間的依賴關係
- Contracts 定義模型/介面 → Core 實作（MemberService/StateMachine/TokenHelper）
- Core 依賴 jose-jwt（JWT 簽章/驗證）與 C# 語言特性（event/tuple/delegate）
- WebAPI 依賴 ASP.NET Core（Controller、Middleware、DI、Model Binding）
- Middleware 於請求前解析 Authorization Bearer Token → 建構 MemberServiceToken（Scoped）→ 以 Attribute 取得 actionName → 呼叫 FSM 檢查
- Repository（示例為 in-memory）提供資料存取；SafeChangeState 對其進行鎖定與狀態變更
- Tests/CLI 輔助生成測資與 token，驗證流程與規格（API first/Spec first）

4. 應用場景：適用於哪些實際場景？
- 微服務中的「會員領域服務」對內 API（前台 USER、後台 STAFF 差異權限）
- 以 FSM 控制流程的領域（註冊、啟用、鎖定、刪除、密碼重設等）
- 需要統一安全模型與跨層一致性的系統（Token 驗證、授權、可執行性）
- 需避免過度設計、以 PoC/MVP 快速驗證設計與規格的一體化團隊
- 日後可延展到分散式事件（消息佇列）、分散式鎖、多租戶等進階議題

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 REST/HTTP 與基本狀態碼
- 熟悉 C# 基礎與 ASP.NET Core 建立最小 WebAPI
- 認識 JWT 結構（Header/Payload/Signature）與 Bearer 授權
- 以簡單案例畫出 FSM（狀態/動作）與合法轉移

2. 進階者路徑：已有基礎如何深化？
- 實作 MemberStateMachine（狀態/動作/允許身分）和 CanExecute 判斷
- 設計 MemberService 與 SafeChangeState 模板（鎖定、驗證、轉移、事件）
- 建立 Middleware 注入 Token 與以 Attribute 取得 actionName 做前置檢查
- 撰寫單元測試（流程驅動，API first/spec first）驗證行為一致性

3. 實戰路徑：如何應用到實際專案？
- 以 Contracts 封裝合約並嚴管相容性（NuGet/版本）
- 將 in-memory Repo 換為實際 DB，導入樂觀鎖/版本號
- 將事件從 C# event 擴展到 MQ（Topic/Queue）與工作者
- 補齊標準化錯誤響應、稽核/追蹤（RequestId/CorrelationId/Logs）
- 以 Postman/自動化整合測試覆蓋 USER/STAFF 權限差異與 FSM 邊界

### 關鍵要點清單
- FSM 驅動 API 設計: 用狀態/動作明確定義可執行性與狀態轉移，讓規格可機器驗證 (優先級: 高)
- 安全三要素模型: 認證（是誰）、授權（能做什麼）、存取控制（何時能做）融於 FSM 與 API (優先級: 高)
- JWT/Token 設計: 在 Token 中攜帶 IdentityType/IdentityName/時間戳，作為執行身分與稽核依據 (優先級: 高)
- MemberStateMachine.CanExecute: 以動作+起始狀態+身分判定是否允許並給出終態 (優先級: 高)
- SafeChangeState 模板: 統一鎖定、再次檢查、執行業務、驗證狀態、發事件的原子流程 (優先級: 高)
- 分層與合約（Contracts/Core/WebAPI/CLI/Tests）: 以 Contracts 為中心，Core 實作，WebAPI 轉接，Tests 驗證 (優先級: 高)
- Middleware+AOP 檢查: 於進入點解析 Token、解析 actionName（Attribute）、前置 FSM 檢查與統一錯誤 (優先級: 高)
- DI 生命週期策略: Token/Service 使用 Scoped，FSM/Repo 使用 Singleton 的注入規劃 (優先級: 中)
- USER/STAFF 權限模型: 以 IdentityType 區分前後台能力，搭配 FSM 控制 API 面 (優先級: 高)
- Repository 與鎖: 先用 in-memory + C# lock，實戰需轉 DB（樂觀鎖/交易）與分散式鎖 (優先級: 中)
- 事件通知與可觀測性: 狀態改變觸發事件，後續可擴展 MQ、稽核與追蹤（RequestId） (優先級: 中)
- API first/Spec first with Tests: 先畫 FSM/定義介面，用測試驅動確認規格與使用情境 (優先級: 高)
- Controller 薄化: 控制器僅負責參數綁定與呼叫 Service，錯誤/安全前置由 Middleware/Service 承擔 (優先級: 中)
- Postman/整合測試: 以實際 HTTP 請求驗證 Token 權限差異與 FSM 防呆（例如禁止未啟用登入） (優先級: 中)
- 技術債與過度設計平衡: 以 PoC/MVP 驗證抽象設計正確性，逐步替換強化實作（例如 JWT、鎖、事件） (優先級: 中)