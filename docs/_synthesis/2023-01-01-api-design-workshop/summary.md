---
layout: synthesis
title: "架構師觀點 - API Design Workshop"
synthesis_type: summary
source_post: /2023/01/01/api-design-workshop/
redirect_from:
  - /2023/01/01/api-design-workshop/summary/
---

# 架構師觀點 - API Design Workshop

## 摘要提示
- API First: 以規格為先的開發流程，讓前後端與測試能並行，提前驗證與降低風險。
- OOP 思維: 用物件導向將 domain 抽象化，從 class/interface 對映到 API 規格。
- 狀態機驅動: 以有限狀態機（FSM）定義生命週期、行為與事件，避免 CRUD 式設計的鬆散與風險。
- 封裝與原子性: 透過封裝狀態轉移與鎖定確保一致性，將方法作為唯一改變狀態的入口。
- 合約先行: Contract First 透過 Mock/測試樣例，讓「先做對」再「做快」成為可能。
- 安全設計前置: 在設計階段納入角色、授權、傳輸、事件等安全考量（OAuth2 scope、最小授權）。
- 行為分類: 將 API 行為依是否需 ID、是否改變狀態、一筆/多筆操作分類，對應不同規格與風險。
- 事件驅動: 定義 Event Type/Payload/Subscribe，透過 webhook 或 message bus 延展行為。
- OpenAPI/AsyncAPI: 用 OpenAPI 定義同步 REST（含安全/資料模型），用 AsyncAPI 定義事件。
- 驗證情境: 用「大富翁式」推演在狀態圖上走流程，快速驗證可行性與設計正確性。

## 全文重點
文章聚焦 API First 的實作方法與設計思維，核心主張是以物件導向（OOP）和有限狀態機（FSM）作為 API 設計的起手式與骨幹。作者指出：API 的成敗七成以上決定於規格設計；若能以 OOP 的抽象化與封裝能力，將 domain 的 class/interface 清楚定義，便能直接映射為 API 規格，讓後續實作（效能、可靠度）成為加分項。具體方式是由 domain 的生命週期出發，畫出狀態圖，盤點會改變/不會改變狀態的行為、參與角色與事件，進而將其轉譯為 REST API 的資源與動作設計。

流程上主張 Contract First：先定義 API Spec 與可運作的 Mock，讓前後端、測試、技術文件與 SDK 開發並行；更重要的是能提前驗證核心抽象是否正確，避免走錯方向。作者示範如何以降級策略（移除 DB/框架依賴、用最小 C# 介面/資料結構與 Console I/O）快速驗證複雜邏輯可行性，強調「先把事情做對」的重要。

在具體設計工作坊中，以「會員註冊/管理」為例，從一般註冊流程抽象出會員資料的生命週期管理。先定義狀態（Unverified/Verified/Restricted/Banned 等）與行為（Register/Verify/Restrict/Allow/Ban/Permit/Remove），用封裝保證狀態只能透過合法方法轉移，並確保原子性。接著標示不改變狀態的操作（Login/ResetPassword/Get/Masked/Statistics），將不同角色（User/Staff/System/Partner）能執行的操作一一對齊，讓授權需求可落實到規格。事件方面，定義 state-changed、action-executing、action-executed 及其 payload，以 webhook 或 message bus 推動跨系統反應。

將分析結果轉成 API 規格時，分四塊：Entity（資料模型以 JSON 定義）、Action（REST 路徑與參數設計，並依特性分類）、Authorize（以 OAuth2 scope 表達最小授權單位，強調 Query/Export 類操作的列舉風險需獨立管控）、Event（事件型別/payload/訂閱）。同步指出 OpenAPI 適用於 REST，同步行為與安全模型；AsyncAPI 用於事件驅動與非同步通訊。最後採「大富翁式」在狀態圖上推演實際 user story，逐步驗證流程與狀態轉移、角色授權與事件觸發是否一致，確保設計可行。全文結語強調：以 OOP+FSM 作為 API First 的方法論，能將「世界的原則」抽象為穩定的合約，面對需求變動仍能保持韌性，並為後續安全與實作鋪路。

## 段落重點
### 前言: 習慣物件導向的思考方式
作者主張以少而精的基本功（OOP、狀態機等）組合解題，反對僵化依賴「方法論大全」。在 API 設計上，先用 OOP 理清 class/object/interface 與封裝抽象，再把介面翻譯為 API spec。示範從 class 到 REST 的映射規則：/api/{class}/[{id}]:{method}，參數/回傳對應 method 簽章。核心在先定義正確物件與狀態機：盤點狀態、會/不會改變狀態的操作、物件資訊及事件，寫得出 class 就完成 90%，再映射為 API。若不熟 OOP，建議補基本功；理解底層（如 vtable、COM/CORBA）更能將物件機制平移至 REST。本文後續即依此思路展開實作。

### 0. 正文開始
從 .NET Conf Taiwan 2022 的 workshop 展開，延續「為什麼 API First」到「如何做」。聚焦四面向：規格優先的流程改變、設計方式標準化、從設計階段即納入安全、避免過度設計。以 OAuth2 授權畫面引導安全思維：在按下「同意」前，使用者需要對傳輸、實作品質、撤銷後的效力有信任；而作為 API 設計者，需在規格上提供可證明的保障。舉「密碼僅存 Hash」作為從設計保證安全的例子。API 設計難在無法預期呼叫時機與順序，因此需對 domain 有掌握，封裝正確的行為與資料，對齊「模擬世界；加以處理」，使 API 穩定、可重用，並能承受需求變化。

### 1. 開發流程上的改變
對比 Code First（先寫可動 code、再重構出 API、最後寫 client/SDK）與 Contract First（先定 API Spec 與能動的 Mock，同步開發前後端與測試文檔）。Contract First 的好處不僅在效率並行，更在於提早確認「做對的事」。作者展示以降級策略驗證抽象（移除 DB、框架依賴，使用最小 C# 結構與 Console I/O），在少量程式碼內證明核心可行，降低風險與溝通成本。各角色（架構師、RD/QA、技術寫手、開發者）可在規格定案後並行展開，尤其能用大量測試樣例先驗證關鍵邏輯（例：折扣引擎），避免等到首版 MVP 才返工。

### 2. API Design Workshop
以常見「會員註冊」為例，將需求提升到「會員生命週期管理」的 domain 抽象：API 的價值是公開資料/運算/流程的正確切面，而非把每個畫面動作直接 API 化。先定義狀態機，標示狀態、行為、角色、事件，等於完成類別的雛形（ID、State、方法、事件）。重點在封裝：狀態不可直接賦值，只能透過合法方法原子性轉移；同時考量授權與鎖定。此方式使 API 方法職責清晰，輸入/輸出明確，不再是鬆散的 CRUD 與雜湊校驗。後續將逐步把 FSM 轉為 API 規格，並用情境推演驗證。

### 2-1. 找出狀態圖
定義會員狀態：Unverified、Verified、Restricted、Banned，以及 Create/Deleted（概念狀態）。Unverified 尚未驗證、Verified 正式會員、Restricted 因管理/安全受限但可登入、Banned 無法登入需解鎖、Deleted 為移除後不應保存的終態。此生命週期圖成為後續設計的藍本，所有行為與授權皆須遵循；也示意初末狀態與過渡的可能性，為日後擴充保留彈性。

### 2-2. 標示能改變狀態的行為
將狀態轉移對應到行為：Register、Verify、Restrict/Allow、Ban/Permit、Remove。主張以行為驅動替代 CRUD：例如註冊成功是 Register→Unverified，再 Verify→Verified，而非任意 UPDATE 狀態欄位。透過封裝與條件檢查（例：Verify 僅允許於 Unverified），保證一致性與可維護性。Register 屬於 class-level（static）操作，內含建立與業務邏輯，不宜由 constructor 承擔；實務加入 repository/ORM 後，資料與行為會分離到不同層（entity/repo vs. BO/controller）。

### 2-3. 標示「不能」改變狀態的行為
將不影響狀態的操作（Login、ResetPassword、Get、Get-Masked、Get-Statistics）以「自回」箭頭標示於合法狀態（如 Verified/Restricted）。此步使類別介面齊備：哪些方法只是查詢或驗證、不涉及生命週期轉移；也利於後續區分 API 的鎖定與授權強度。遮罩資料（Masked）與統計（Statistics）特別指出不同資料切面與安全等級，便於之後在 Authorize/Security 上精細管控。

### 2-5. 標示相關角色
在狀態圖上為每個行為標示可執行角色（A 使用者、B 客服、C 主管、D 系統服務、E 協力廠商）。此舉把「誰能做什麼」從 domain 層就寫進規格，後續可映射到 API 的授權策略（API Key、JWT、IIdentity/IPrincipal/ClaimsPrincipal），並以 AuthorizeAttribute 等實作。重點是讓 domain expert 先定清楚語意，工程實作才能一致落地，避免把安全交給基礎設施「猜」。

### 2-6. 標示事件
定義何時要發出事件（EDA）：1) 狀態轉移完成（state-changed），2) 行為執行前（action-executing），3) 行為執行後（action-executed）。事件讓外部系統能「關注你」並在適當時機觸發後續處理（如寄信、審計）。即便各語言/平台支援度不同（delegate/event、Observer、Webhook、MQ），規格仍應清楚列出 Event Type 與 Payload，保證跨系統一致性與可測性。

### 2-7. 轉成 API Spec (REST) - A. Entity
以 JSON 設計 Entity，貼合 REST 的 resource 與 NoSQL 思維；以 _id、email、state 為核心，另分 fields、masked-fields、statistics-fields 三區，便於不同場景輸出與版本控管。提醒避免以 RDB 正規化思路硬套 REST；資料模型以消費端需求與資安切面為軸。state 欄位不可由 CRUD 任意修改，只能隨合法行為變化，這是規格的一部分。

### 2-7. 轉成 API Spec (REST) - B. Action
將行為分類設計路徑與風險分級：1) 無需指定 id 的單筆操作（Register/Login/Verify/ResetPassword）；2) 需指定 id 且改變狀態（restrict/allow/ban/permit/remove）；3) 需指定 id 且不改變狀態（get/masked/statistics）；4) 不指定 id 的批量操作（Query/Export，本例留白但點出高風險）。此分類有助於定義不同驗證、速率限制、交易鎖定與審計要求。

### 2-7. 轉成 API Spec (REST) - C. Authorize
提出以 OAuth2 scope 作為最小授權單位：基礎（CRUD 中收斂為 READ/DELETE）、建立（REGISTER、IMPORT）、異動（BASIC/STAFF/ADMIN 對應不同身分能做的變更）、系統（SYSTEM，給排程/自動化）。另強調 Query/Export 類操作需單獨 scope，避免資料被列舉爬走。部分授權語意需在 API 實作層面判斷（如「本人」），非僅靠 Gateway 開關可解。

### 2-7. 轉成 API Spec (REST) - D. Event
規格三要素：Event Type、Payload、Subscribe。列出 state-changed 與 action-executing/executed 的 payload 結構，並建議附上當下 entity 快照。若以 webhook 實作，需定義認證（token/signature）、版本（X-WebHook-Version）等 header，確保來源可信與升級可過渡。Subscribe 的機制可交由雲端 PaaS（EventGrid/SNS 等）或自建 MQ（Kafka/Rabbit/NATS）承接。

### 2-7. 轉成 API Spec (REST) - E. OpenAPI & AsyncAPI
區分規格標準適用範圍：OpenAPI 用於 REST 的資料模型、行為與安全（含 scope），AsyncAPI 用於事件驅動與非同步通訊。事件具 callback/訂閱/多協定與角色邏輯，OpenAPI 不足以完全描述，需以 AsyncAPI 補齊。作者以 ChatGPT 查證 scope 宣告與兩規範差異，建議將本案例拆成 OpenAPI（Entity/Action/Auth）與 AsyncAPI（Event）雙規格併行管理。

### 2-8, 用狀態機驗證情境
以「大富翁式」推演 user story：把每一步操作放到狀態圖上移動棋子，驗證起迄狀態、操作與角色是否吻合。案例涵蓋註冊（Register→Unverified）、寄信（action-executed: register 觸發外部寄送）、驗證（Verify→Verified）、下單查詢（Get）、協力廠商取貨資料（Get-Masked）。此方法快速、低成本且利於人與人溝通，可在實作前確認設計可行性，避免走錯方向。

### 2-9, 設計小結
至此已完成 State/Entity/Action/Authorize/Event 的分析與設計，可依實際技術選型（REST/GraphQL/gRPC 等）落地為規格文件與實作。安全分析將於後續篇幅延伸，並以 ASP.NET Core WebAPI 實作示範。總結重申：用 OOP+FSM 讓 API First 有方法可循，從「世界不變的原則」出發抽象 domain，配合 Contract First 與事件驅動，達到先做對、再做快、且能面對變化的 API 設計。

## 資訊整理

### 知識架構圖
1. 前置知識
   - 物件導向核心觀念：類別、物件、介面、封裝、抽象化、狀態與方法
   - REST/HTTP 基礎：資源、動詞、路徑設計、Request/Response、狀態碼
   - 狀態機（FSM）：狀態、轉移、觸發行為、事件
   - 基礎資安：OAuth2/JWT、API Key、Scope、最小權限
   - 規格與文件：OpenAPI、JSON Schema、（事件）AsyncAPI
2. 核心概念（3-5個）
   - OOP → API 對應：以物件的介面與方法翻譯為 API Spec（封裝＝抽象化的合約）
   - 狀態機驅動的 API 設計：以狀態與轉移為基礎設計 API，而非單純 CRUD
   - Contract First/Mock First 流程：先定規格與可運行 Mock，並行開發與驗證
   - 安全性從設計入手：角色/Scope/操作對齊，權責分離與最小權限
   - 四分面規格：Entity/Action/Authorize/Event 的完整定義
3. 技術依賴
   - OOP 分析 → REST 路徑規則對應（/api/{class}/[{id}]:{method}）
   - Entity（JSON Schema/NoSQL）與 Action（OpenAPI Operation）綁定
   - 身分與授權：API Key/JWT → Middleware → IIdentity/IPrincipal/AuthorizeAttribute
   - 事件驅動：Domain Event → Webhook/Message Bus → AsyncAPI/回呼安全
   - 資料與行為分離：Entity/Repository/ORM 與 Controller/Domain Service 的責任劃分
4. 應用場景
   - 會員註冊/驗證/登入/權限控管的 API 設計與外包整合
   - 對外合作（Partners）以 API 發佈最小必要能力（安全遮罩資訊）
   - 產品化平台：前後端、SDK、技術寫手、QA 並行開發
   - 事件驅動整合（驗證信、工作流觸發、審計）

### 學習路徑建議
1. 入門者路徑
   - 學 OOP 基本功（封裝/抽象/介面/類別與方法）
   - 熟悉 REST/HTTP 與基本 API 設計習慣
   - 練習以簡單類別（如 Man/Member）映射成 API（路徑+方法+參數/回應）
   - 初探狀態機：為簡單流程畫出狀態圖與轉移
2. 進階者路徑
   - 以 FSM 驅動 API：把會/不會改變狀態的操作標注在狀態圖
   - 設計四分面規格：Entity/Action/Authorize/Event
   - 建立角色/Scope/Operation 對應表，落到 OpenAPI（含 security）
   - 加入 Mock 驗證、大量測試案例，驗證抽象設計（POC）
3. 實戰路徑
   - 以 Contract First 建置 Mock Server，同步開發前端/SDK/後端/文件/測試
   - ASP.NET Core：Middleware 注入 JWT/API Key → AuthorizeAttribute 控制
   - Repository/ORM 導入與交易/鎖定，確保狀態轉移的原子性與一致性
   - 事件化：定義 Event Type/Payload/Subscribe，實作 Webhook 或 MQ 訂閱
   - 規格化：OpenAPI（同步）+ AsyncAPI（事件），持續維運與版本治理

### 關鍵要點清單
- OOP → API 對應規則: 以類別介面/方法翻譯成 API，路徑模式 /api/{class}/[{id}]:{method} (優先級: 高)
- 封裝與狀態不可直改: 狀態只能由定義好的操作改變，禁止呼叫端直接 CRUD 狀態欄位 (優先級: 高)
- 狀態機驅動設計: 先找出狀態、轉移、觸發行為，再決定 API，避免 CRUD 導致規格失控 (優先級: 高)
- Contract First/Mock First: 先定合約與可呼叫的 Mock，使前後端/測試/文件並行 (優先級: 高)
- 安全性從設計開始: 以角色/Scope/操作三者對齊定義最小權限與邊界 (優先級: 高)
- 原子性/鎖定: 狀態轉移須具原子性（悲觀/樂觀鎖），避免競態導致不一致 (優先級: 高)
- Entity/Action/Authorize/Event 四分面: 用此模型完整描述 API 規格與責任 (優先級: 高)
- 角色與 Scope 的設計: 從角色職責推導 Scope，避免只靠 Gateway 粒度過粗 (優先級: 中)
- NoSQL 心態設計 Entity: 以資源為中心，避免過度正規化，對齊 REST 的資源觀 (優先級: 中)
- 事件與 Webhook: 定義 Event Type/Payload/Subscribe，支援 action-executing/executed/state-changed (優先級: 中)
- OpenAPI 與 AsyncAPI: 同步操作用 OpenAPI，事件驅動用 AsyncAPI，分工清楚 (優先級: 中)
- 組合操作的原則: 允許組合 API 以提升體驗，但不可違背狀態圖語意 (優先級: 中)
- 驗證方法（大富翁法）: 以情境步驟在狀態圖移動棋子，快速驗證可行性 (優先級: 中)
- 資料與行為分離: Entity/Repository/ORM 管資料，Controller/Domain Service 管商業邏輯 (優先級: 中)
- 安全資料取用範式: 提供遮罩資料/統計資料接口，讓外部僅取最小必要資訊 (優先級: 中)