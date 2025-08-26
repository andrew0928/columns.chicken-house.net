# 架構師觀點 - API Design Workshop

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 API First？
- A簡: API First 是先設計可執行的 API 規格，再進行前後端與實作，確保一致與正確。
- A詳: API First（或 Contract First）主張在任何程式實作之前，先用規格語言定義清晰、一致、可驗證的 API 合約（如 OpenAPI/Swagger），並以 Mock 驗證場景，使前後端與測試能在確定的契約下並行開發。其特點包括提早風險控管、減少返工、促進團隊協作、提升可維護性。常見場景：平台化產品、微服務整合、對外開放 API、跨組織協作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q9, B-Q1

Q2: 什麼是 Contract First？與 API First 有何關係？
- A簡: Contract First 即先定義可執行合約；API First 是其在 API 領域的實踐。
- A詳: Contract First 是以「合約」為中心的開發方法，先定義介面、資料模型、授權與錯誤語意，並透過 Mock 驗證。API First 是 Contract First 在 API 設計的具體落地，強調用規格驅動設計、實作與測試的一致性。特點：同步開發、明確責任邊界、可重現的設計討論。應用：微服務、SDK 生成、開發者平台。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, B-Q11

Q3: 為什麼 API 的成功七成取決於規格品質？
- A簡: 規格決定介面清晰、邊界穩定，降低錯誤與溝通成本，影響系統長期品質。
- A詳: 良好規格是對問題本質的高品質抽象，能讓使用者理解、讓實作者精準落地，並支撐測試與文件自動化。規格一旦正確，後續效能、可靠度等工程優化才有加分的基礎；反之規格錯誤，實作再好也無法挽救錯誤的方向。常見場景：對外開放 API，長期演進的企業平台，跨團隊協作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q12, C-Q10

Q4: 物件導向（OOP）思維如何幫助 API 設計？
- A簡: 以類別、介面、封裝思考，將物件操作對映成 API 規格，減少設計複雜度。
- A詳: OOP 的核心在抽象與封裝。用 Class/Interface 分析「主體、狀態、行為、事件」，將方法轉為 API 行動（Action）、屬性轉為 Entity 欄位，並以封裝確保狀態僅能透過行為改變。優點：易理解、易測試、對應清晰。應用：狀態機驅動的 API、對映為 REST 路徑與 HTTP 動詞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q11, B-Q10

Q5: 封裝（Encapsulation）在 API 設計中的核心價值是什麼？
- A簡: 封裝限制狀態只能由定義好的動作改變，保證一致性與安全性。
- A詳: 封裝將內部狀態與操作細節隱藏，只暴露受控的行為入口；在 API 中體現為禁止直接 CRUD 改寫關鍵欄位（如 state），改以明確 Action（如 verify、ban）觸發合法轉移。特點：維持不變式、降低耦合、便於授權與稽核。應用：FSM 驅動生命周期管理、交易/鎖定保證一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q3, D-Q1

Q6: 什麼是有限狀態機（FSM）？在 API 中扮演什麼角色？
- A簡: FSM 定義狀態與轉移規則，將流程具體化，驅動安全一致的 API 設計。
- A詳: FSM 用狀態節點與轉移邊表示生命週期與操作邏輯。API 以 FSM 為藍本，將可執行的動作（Action）對映到合法轉移，讓每個 API 背後的檢查、授權與事件釐清。特點：可視化、可驗證、便於討論；應用：會員、訂單、工單等生命周期管理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q2, C-Q7

Q7: 為什麼用 FSM 設計 API 通常優於單純 CRUD？
- A簡: FSM 明確流程與約束，避免任意改狀態，降低維護風險與安全缺口。
- A詳: CRUD 讓呼叫者自由改欄位，易破壞不變式（如未驗證卻標示 verified）。FSM 將變更包進 Action，先檢查前置狀態與條件，再原子轉移。好處：一致性、可稽核、權限好控、易於事件驅動。應用：需要嚴控流程的領域，如金融、會員、履約。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2, D-Q1

Q8: API 設計的四大構件是什麼？為何重要？
- A簡: Entity、Action、Authorize、Event 四者形成完整契約與運作框架。
- A詳: Entity 定義資料模型與狀態欄位；Action 定義行為與輸入輸出；Authorize 以 Role/Scope 管控存取；Event 定義通知型態、負載與訂閱。四者相輔相成：資料被行為改變，受授權約束，並對外發出事件以支援整合。缺一會導致溝通與治理斷點。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q3, C-Q6

Q9: Code First 與 Contract First 有何差異？
- A簡: Code First先寫程式再補規格；Contract First先定規格並以 Mock 驗證。
- A詳: Code First 重心在「能動」，規格常滯後，易發生前後端協作不一致；Contract First 先對齊外部介面與需求，再並行開發與測試，變更成本更低。場景：多人協作、對外 API、產品化平台，宜採 Contract First；小型內部工具可用 Code First。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, C-Q10

Q10: 為什麼要在設計階段就考量安全性？
- A簡: 架構性安全設計可從根源移除風險，避免事後補救與權限濫用。
- A詳: 例如密碼僅存哈希、state 禁 CRUD 僅允許 Action 轉移、查詢與匯出需額外 Scope、Webhook 要簽章與版本。安全從設計落實，將敏感操作最小化並可稽核。應用：個資保護、金流、合作夥伴整合、API 產品化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q4, D-Q6

Q11: REST 路徑如何對映 OOP 類別與方法？
- A簡: 採 /api/{class}/[{id}]:{method}，靜態方法無 id，實例方法需 id。
- A詳: 以類別名對映資源集合，實例以 id 指定；動詞用動作尾碼表示，如 POST /api/members/{id}:verify。回應與輸入對映方法參數與回傳值。此設計使 OOP 思維得以工整映射，易讀易測。場景：FSM 驅動、動作導向的 API 設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q10, C-Q2

Q12: 角色（Role）與範圍（Scope）有何不同？
- A簡: 角色代表「誰」，範圍描述「能做什麼」，授權以 Scope 生效。
- A詳: Role（如 User、Staff、System、Partner）是身分分類；Scope 是最小權限單位（如 REGISTER、READ、STAFF）。OAuth2 流程頒發含 Scope 的 Token，API 依 Scope 授權。設計時將 Role 映到 Scope 組合，達到最小授權原則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q5, D-Q3

Q13: API 中的事件（Event）與 Webhook 是什麼？
- A簡: 事件描述狀態或行為發生；Webhook 是以回呼通知訂閱方的機制。
- A詳: 事件型態常見有 state-changed、action-executing、action-executed。Payload 含事件型別、實體識別、起訖狀態、動作與當下實體快照。Webhook 以 HTTP POST 推送，需簽章/Token 驗證與版本標示。用途：整合外部流程、非同步解耦。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q6, D-Q6

Q14: OpenAPI 與 AsyncAPI 有何差異？
- A簡: OpenAPI 描述 REST 介面；AsyncAPI 描述事件/訊息驅動介面。
- A詳: OpenAPI 聚焦請求/回應、路徑、模型與安全（含 OAuth2 Scopes）；AsyncAPI 描述 Topic、訂閱、訊息架構與通道（MQTT、AMQP、HTTP 回呼等）。兩者互補：行為同步以 OpenAPI，事件非同步以 AsyncAPI。用於規格驅動與工具鏈生成。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q9, C-Q3

Q15: Mock 在 Contract First 中扮演何種角色？
- A簡: Mock 讓規格可被調用，提早驗證情境並讓團隊並行開發。
- A詳: 以最小成本建立可呼叫的 API 假實作（固定或基於範例資料），用於驗證路徑、輸入輸出與授權流程，輔助撰寫自動化契約測試與文件。優點：降低風險、加速對齊、支援前端/SDK 提前開工。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q10, A-Q9

Q16: 什麼是「降級」驗證法？為何有效？
- A簡: 以最少依賴（Console、List/Linq）快速驗證核心設計。
- A詳: 在設計階段，用最簡單的 C# Console 程式、記憶體集合（List/Dictionary）模擬 Repository，暫時移除 DI、Logging、Security 等非核心依賴，專注驗證 FSM 與計算邏輯正確性。好處：快速、可討論、易調整，降低探索成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q2, B-Q11

Q17: 為何以 JSON/NoSQL 思維建模 Entity？
- A簡: REST 資源導向貼近文件模型，避免過度正規化造成 API 易碎。
- A詳: REST 對應資源（Document），以完整實體為輸入輸出單位。採 JSON Schema 可清楚表達狀態欄位、遮罩欄位、統計欄位等。NoSQL 思維讓讀取優先、寫少讀多的 API 穩定，減少多表關聯導致的變更連鎖。搭配聚合寫入、分頁查詢。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q3, C-Q9, D-Q4

Q18: 靜態方法與實例方法如何對映 REST？
- A簡: 靜態方法無須 id；實例方法需 id 標定資源，再以動作尾碼呼叫。
- A詳: Static（如 Register）對映 POST /api/members:register；Instance（如 Verify）對映 POST /api/members/{id}:verify。參數映到 Body/Query/Path，回傳對映 Resource 或 Result。清楚分工有助安全與稽核，亦便於 SDK 映射。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q2, B-Q10

Q19: 本文中的角色 A～E 分別代表什麼？
- A簡: A 使用者、B 客服、C 客服主管、D 系統服務、E 外部夥伴。
- A詳: A（Guest/User）執行註冊、登入、驗證等個人操作；B（Staff）執行限制/允許、封鎖/解封等管理；C（Staff Manager）可覆核或高風險授權；D（System Service）進行排程、自動化；E（Partners）呼叫對外必要最小權限 API。用於設計 Role→Scope 對映。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q4, C-Q5

Q20: 如何避免 API 過度設計？判斷原則是什麼？
- A簡: 以最小可行合約與最小 Scope 出發，從實際場景回推需求。
- A詳: 原則：從 FSM 必要動作出發，先確保核心流程；Scope 只拆到能組合出全部需求的最小單位；Query/Export 另設 Scope；先列全量再刪減；用 Mock 與場景走查驗證；保留擴充欄位（如 fields）以便演進。避免過多組合 API 破壞一致性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q3, D-Q3

---

### Q&A 類別 B: 技術原理類

Q1: Contract First 的開發流程如何運作？
- A簡: 先定規格與 Mock，前後端並行，最後整合測試，以合約為中心。
- A詳: 技術原理說明：以 OpenAPI/AsyncAPI 定義 Entity/Action/Auth/Event。關鍵步驟：1) 擬定合約與範例；2) 建立 Mock；3) 前端/SDK、後端服務、QA 同步；4) 契約測試與整合。核心組件：Mock Server、契約測試框架、CI/CD、API 文件生成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q9, C-Q10

Q2: FSM 驅動的 API 執行流程為何？
- A簡: 檢查前置狀態→授權→執行動作→原子轉移→觸發事件。
- A詳: 技術原理說明：每個 Action 映射一條或多條合法轉移邊。關鍵步驟：1) 驗證輸入與當前狀態；2) 鎖定資源（悲觀或樂觀）；3) 執行商務邏輯；4) 更新狀態與資料；5) 發送事件（executing/executed/state-changed）。核心組件：狀態檢查器、鎖服務、事件總線/Webhook。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, C-Q8

Q3: 封裝如何保證狀態一致性與安全性？
- A簡: 將狀態改變僅暴露為 Action，搭配原子性鎖定，防止越權與競爭。
- A詳: 技術原理說明：把 state 標為只讀，禁止通用 UPDATE。關鍵步驟：1) 入口檢查 Scope；2) 狀態守衛；3) 鎖定資源；4) 僅由動作例程修改狀態；5) 稽核紀錄。核心組件：領域服務、Repository、授權中介層、AOP/Filter 審計。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q5, D-Q2, D-Q1

Q4: 角色-範圍-操作的授權模型如何設計？
- A簡: 以 Scope 為最小權限，將角色映射為 Scope 集合，於入口強制檢查。
- A詳: 技術原理：分離身分（Role）與能力（Scope）。關鍵步驟：1) 從 Action 清單推導 Scope；2) 建立 Role→Scope 對映；3) OAuth2/JWT 在 Token 內攜帶 Scopes；4) API 以 Authorize 檢查；5) 細緻到「本人」與「多筆列舉」特殊規則。核心組件：Identity Provider、Authorization Filter、策略授權。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q4, C-Q5

Q5: API Key 與 OAuth2 Scopes 機制有何差異？
- A簡: API Key驗身分簡單；OAuth2含範圍控制細緻，適合多方授權。
- A詳: 技術原理：API Key 多用於伺服器到伺服器的簡單認證，缺乏細粒度權限；OAuth2 支援第三方授權與 Scope，能表達最小權限與撤銷。關鍵步驟：OAuth2 包含授權碼流程、Token 發行、Scope 聲明。核心組件：Authorization Server、Resource Server、Token 驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q5, D-Q6

Q6: 事件機制的 Payload 與型態如何設計？
- A簡: 定義 state-changed 與 action 事件，載明實體、起訖狀態與動作。
- A詳: 技術原理：事件應可重放、可追溯。關鍵步驟：1) 列出事件型態；2) 設計 Payload（type、entity-id、origin/final、action、entity snapshot）；3) 嚴格簽章與版本號；4) 送交 Message Bus 或 Webhook。核心組件：事件格式規範、簽章器、訂閱管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q6, D-Q6

Q7: 中介軟體如何把 API Key/JWT 轉成 IPrincipal？
- A簡: Middleware 驗證憑證，產出 ClaimsPrincipal 注入上下文供授權判斷。
- A詳: 技術原理：Pipeline 中先驗證（API Key 或 JWT），再生成 IIdentity/IPrincipal。關鍵步驟：1) 解析 Header；2) 驗章與有效期；3) 轉 Scope 為 Claims；4) HttpContext.User 設定 ClaimsPrincipal。核心組件：ASP.NET Core Authentication Handler、Authorization Policy。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q5, A-Q12

Q8: OpenAPI 的安全與 Scope 如何宣告？
- A簡: 在 components.securitySchemes 定義 OAuth2，Paths 上宣告所需 Scope。
- A詳: 技術原理：OpenAPI 以 securitySchemes 定義 flows、tokenUrl、scopes；各 operation.security 指定需要的 scopes。關鍵步驟：1) 定義 OAuth2 Scheme；2) 標註 operation 的 scopes；3) 用範例/Mock 驗證。核心組件：OpenAPI YAML、工具（Swagger UI、Codegen）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, C-Q3, C-Q5

Q9: AsyncAPI 的核心架構與適用情境是什麼？
- A簡: 描述事件通道、主題與訊息結構，適用於事件驅動整合。
- A詳: 技術原理：AsyncAPI 定義 channels、messages、servers、operations（publish/subscribe）。關鍵步驟：1) 建立事件目錄；2) 定義 payload schema；3) 指定通道與安全；4) 生成文件/SDK。核心組件：Message Bus（Kafka、RabbitMQ）、Webhook 回呼。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, C-Q6, B-Q6

Q10: OOP 到 REST 的規則映射是什麼？
- A簡: 類別→資源、屬性→欄位、方法→動作路徑，回應對映回傳值。
- A詳: 技術原理：將 Class/Interface 的操作以動作尾碼表達，Static 不需 id，Instance 需 id；參數歸置 Body/Query/Path，結果以 2xx/4xx/5xx 表示。關鍵步驟：梳理狀態、動作、事件；定義 URI 與模型。核心組件：路由規範、模型繫結、狀態檢查器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q2, C-Q3

Q11: Mock Server/SDK/文件如何形成工具鏈？
- A簡: 以規格為源生成 Mock、SDK、文件，驅動契約測試與並行開發。
- A詳: 技術原理：規格單一真相（SSOT）。關鍵步驟：1) 維護 OpenAPI；2) 自動生成 Mock/SDK/Docs；3) 在 CI 執行契約測試；4) 版本發佈與相容檢查。核心組件：OpenAPI Generator、Prism（Mock）、Swagger UI、Schemathesis（測試）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, C-Q10, D-Q5

Q12: 為何要標準化 Entity/Action/Authorize/Event 四構件？
- A簡: 清楚分工與治理邊界，方便演進、稽核與平台化擴張。
- A詳: 技術原理：將資料、行為、權限、通知分層描述，減少交叉耦合。關鍵步驟：1) Entity 用 JSON Schema；2) Action 用 OpenAPI；3) Authorize 用 OAuth2 Scope；4) Event 用 AsyncAPI/Webhook。核心組件：規格倉庫、審查流程、變更記錄。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, C-Q3, D-Q9

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何用 C# 定義 Member 狀態列舉與類別骨架？
- A簡: 建立列舉與類別，封裝狀態欄位與對應動作方法。
- A詳: 具體步驟：1) 定義 enum MemberStateEnum { UNVERIFIED, VERIFIED, RESTRICTED, BANNED }；2) 建立 Member 類別，State/Id/Email 屬性唯讀；3) 實作動作 Register/Verify/Restrict/Allow/Ban/Permit/Remove。程式碼片段：public bool Verify(string code){ if(State!=UNVERIFIED) return false; State=VERIFIED; return true;} 注意事項：狀態只允許由動作改變；檢查與鎖定需原子化；方法回傳清晰結果或錯誤碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2, C-Q8

Q2: 如何將 Register/Verify 對映成 REST API 路徑？
- A簡: 採用動作尾碼規則，靜態無 id，實例需 id 指定。
- A詳: 實作步驟：1) 規範路徑 /api/members:register（POST），Body 帶 email；2) /api/members/{id}:verify（POST），Body 帶 code；3) 回傳 Entity 或簡化結果。範例：POST /api/members:register；POST /api/members/123:verify。注意事項：對應 FSM 合法轉移；驗證輸入與狀態；明確錯誤碼（400/403/409）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q10, C-Q3

Q3: 如何以 OpenAPI 建立基本規格與範例？
- A簡: 在 components 定義 schema，paths 定義動作與回應。
- A詳: 步驟：1) 定義 Member schema（id、email、state、fields…）；2) 定義路徑 /api/members:register 與 /api/members/{id}:verify；3) 加入範例與錯誤回應；4) 生成 Swagger UI。程式片段：components.schemas.Member…；paths: … 注意：資料欄位/狀態只讀設計；以 examples 提升一致性；規範版本管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q8, C-Q10

Q4: 如何在 ASP.NET Core 設定 JWT 與 AuthorizeAttribute？
- A簡: 加入認證中介、設定 JWT 驗章，使用 [Authorize] 檢查 Scope。
- A詳: 步驟：1) services.AddAuthentication().AddJwtBearer(...); 2) services.AddAuthorization(o=>o.AddPolicy("scope:READ",p=>p.RequireClaim("scope","READ"))); 3) 控制器/動作上標註 [Authorize(Policy="scope:REGISTER")]。程式片段：builder.Services…；注意：時鐘偏差、金鑰輪替；以 Claims 映射 Scope；對公/私鑰保護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q4, D-Q6

Q5: 如何設計 OAuth2 Scope 並在 OpenAPI 宣告？
- A簡: 先自底向上列出 Action 對應最小 Scope，再於規格標註需求。
- A詳: 步驟：1) 列出 REGISTER/READ/DELETE/STAFF/SYSTEM/EXPORT…；2) 定義角色對映 Scope；3) OpenAPI components.securitySchemes.oauth2.flows.authorizationCode.scopes 定義；4) 在 operation.security 標示。設定片段：securitySchemes: oauth2: type: oauth2 … scopes: read: … 注意：避免過細；定期審核最小權限；文件化策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q8, D-Q3

Q6: 如何撰寫 Webhook 接收端並驗證簽章？
- A簡: 建立回呼端點，驗證 Token/簽章，再處理事件 Payload。
- A詳: 步驟：1) 建立 POST /webhook/member；2) 驗證 Header Token/簽章（HMAC）與時間戳；3) 解析 event.type、entity-id；4) 依型態觸發流程（如寄信）；5) 回 2xx。程式片段：驗證 X-Signature=HMAC(secret, body)。注意：重放防護（nonce/時效）、冪等處理、版本相容。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q6, D-Q6

Q7: 如何用 List/Dictionary 模擬 Repository 驗證 FSM？
- A簡: 以記憶體集合存放實體，快速驗證轉移與案例，不依賴資料庫。
- A詳: 步驟：1) 建立 Dictionary<int,Member> store；2) 在 Action 中讀寫 store；3) 撰寫單元測試覆蓋狀態轉移；4) Console 輸入輸出觀察結果。程式片段：var store=new Dictionary<int,Member>(); store[id]=member; 注意：聚焦驗證邏輯；避免引入 DI/ORM；測試多執行緒情境可加鎖模擬。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q2, D-Q2

Q8: 如何實作狀態變更的悲觀與樂觀鎖？
- A簡: 悲觀鎖先鎖後改；樂觀鎖用版本比對，衝突時重試或失敗。
- A詳: 步驟：悲觀鎖：資料庫 SELECT … FOR UPDATE 或分散鎖，確保單一路徑修改；樂觀鎖：Entity 帶 version，UPDATE where version=old，影響行數=1 才成功。程式片段：UPDATE member SET …,version=version+1 WHERE id=@id AND version=@ver。注意：熱點選擇策略、超時與重試、避免死鎖。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q2, B-Q3, D-Q2

Q9: 如何設計 Get/Masked/Statistics 的資料遮罩？
- A簡: 區分完整資料與遮罩視圖，依 Scope 與角色輸出最少必要資訊。
- A詳: 步驟：1) 在 Entity 設計 masked-fields、statistics-fields；2) 於 API 實作依 Scope 選取輸出；3) 遮罩策略如姓名首字＋*、電話末三碼；4) 加入審計紀錄。程式片段：if(!HasScope("READ_FULL")) return maskedView(member); 注意：避免在前端遮罩；防止資料拼湊；明確文件化欄位差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, A-Q12, D-Q8

Q10: 如何用 Postman/Mock Server 驗證合約與情境？
- A簡: 以規格生成 Mock，撰寫場景測試集合，驗證路徑、輸入輸出與授權。
- A詳: 步驟：1) 用 Prism/Stoplight 根據 OpenAPI 啟動 Mock；2) Postman 匯入規格產生請求範本；3) 建立情境流程（Register→Verify→Get-Masked）；4) 加入 Token/Scope 測試；5) 整合 CI 執行。注意：資料一致性（Mock 資料夾層）、錯誤碼覆蓋、版本差異管理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q11, D-Q5

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 若有人嘗試直接修改 state 欄位怎麼辦？
- A簡: 禁止通用更新，僅允許透過 Action 改變狀態，並記錄稽核。
- A詳: 症狀：API/DB 層可見不合規狀態。可能原因：暴露 CRUD、缺少封裝/授權檢查。解決步驟：1) 移除通用 UPDATE；2) 僅保留 Action 端點；3) DB 設定限制（如觸發器/檢查約束）；4) 審計與告警。預防：以 FSM 驅動設計、契約測試覆蓋非法操作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q7, B-Q3

Q2: 兩個動作並發導致狀態競爭如何處理？
- A簡: 使用悲觀或樂觀鎖，確保轉移原子性，衝突時重試或回退。
- A詳: 症狀：狀態跳躍、覆寫。可能原因：缺乏鎖定或版本控制。解決步驟：1) 導入鎖策略；2) 在 Action 重新檢查狀態；3) 衝突回 409；4) 規畫重試機制。預防：交易邊界清晰、避免長交易、熱點拆分。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q2, C-Q8, A-Q5

Q3: Scope 設計過細或過粗怎麼調整？
- A簡: 以最小可組合原則回推，合併低使用率細粒度，拆分高風險功能。
- A詳: 症狀：授權難管理/濫權。原因：未以 Action 推導 Scope。解決：1) 盤點 Action→Scope；2) 蒐集使用與風險資料；3) 合併或拆分；4) 更新 Role→Scope 映射；5) 文件化遷移。預防：定期審核、變更管控與版本化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q4, C-Q5

Q4: 過度正規化導致 API 易碎如何改善？
- A簡: 以資源為中心改為文件模型，將讀取優先的資料聚合輸出。
- A詳: 症狀：頻繁跨資源取數、多端點耦合。原因：將 DB 正規化直接搬到 API。解決：1) 以用例回推視圖；2) 在 Entity 聚合；3) 加入只讀統計欄位；4) 明確版本策略。預防：採 JSON/NoSQL 思維，讀多寫少場景優先聚合。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q17, C-Q3, C-Q9

Q5: SDK/前端與規格不一致怎麼辦？
- A簡: 導入契約測試，生成 SDK，自動比對規格與實作差異。
- A詳: 症狀：欄位/路徑/錯誤碼不對。原因：手動同步、規格滯後。解決：1) 規格為單一真相；2) 自動生成 SDK/Mock/Docs；3) CI 契約測試；4) 發行前破壞性變更檢查。預防：規格審查制度、版本化與棄用周期。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q3, C-Q10

Q6: Webhook 被偽造或重放攻擊怎麼處理？
- A簡: 導入 HMAC 簽章與時效驗證，實作冪等與重放防護。
- A詳: 症狀：未授權回呼、重複處理。原因：缺簽章/時戳/nonce。解決：1) HMAC(body, secret)、驗證時效與 nonce；2) 冪等鍵去重；3) 僅 HTTPS；4) IP 白名單。預防：文件化安全要求、定期輪替密鑰與演練。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q6, B-Q6

Q7: Query/Export 被濫用爬資料怎麼防範？
- A簡: 專屬 Scope、分頁與速率限制，並加入稽核與異常偵測。
- A詳: 症狀：資料批次外流。原因：缺少專屬權限與限制。解決：1) 為列舉操作設置 EXPORT/QUERY Scope；2) 分頁、速率與配額；3) 欄位最小化與遮罩；4) 異常行為告警。預防：審批流程、臨時憑證、最小可行期間。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, C-Q9, B-Q4

Q8: 密碼或敏感資料外洩風險如何降低？
- A簡: 採不可逆哈希、欄位遮罩、最小輸出與嚴格稽核。
- A詳: 症狀：資料庫或日誌洩漏。原因：明碼儲存、過量輸出。解決：1) 密碼哈希+鹽；2) 嚴禁回傳敏感欄位；3) Masked 視圖；4) 加密靜態與傳輸；5) 權限與稽核。預防：設計階段落實最小可見，安全測試與演練。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q9, D-Q6

Q9: 合約變更如何兼顧版本相容？
- A簡: 採版本化路徑/標頭，提供過渡期，文件標示差異與棄用。
- A詳: 症狀：客戶端突發故障。原因：破壞性變更未管理。解決：1) v1/v2 或 Accept-Version；2) 變更日誌與遷移指南；3) Feature Flag；4) 雙發佈與過渡期限。預防：契約審查、破壞性變更流程、回溯測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q3, C-Q10

Q10: 團隊不熟 OOP/FSM 導致落地困難怎麼辦？
- A簡: 以範例與走查教學，從簡單 FSM 入手，配合工具與稽核導入。
- A詳: 症狀：規格難以維護、實作不一致。原因：缺乏共同模型。解決：1) 範例庫（Member FSM）與模板；2) 設計工作坊與狀態走查；3) 規格評審與契約測試；4) 工具鏈導入。預防：建立設計指南、Pair Review、定期演練。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q15, B-Q11

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 API First？
    - A-Q2: 什麼是 Contract First？與 API First 有何關係？
    - A-Q3: 為什麼 API 的成功七成取決於規格品質？
    - A-Q6: 什麼是有限狀態機（FSM）？在 API 中扮演什麼角色？
    - A-Q7: 為什麼用 FSM 設計 API 通常優於單純 CRUD？
    - A-Q9: Code First 與 Contract First 有何差異？
    - A-Q11: REST 路徑如何對映 OOP 類別與方法？
    - A-Q12: 角色（Role）與範圍（Scope）有何不同？
    - A-Q13: API 中的事件（Event）與 Webhook 是什麼？
    - A-Q15: Mock 在 Contract First 中扮演何種角色？
    - C-Q2: 如何將 Register/Verify 對映成 REST API 路徑？
    - C-Q3: 如何以 OpenAPI 建立基本規格與範例？
    - C-Q10: 如何用 Postman/Mock Server 驗證合約與情境？
    - D-Q5: SDK/前端與規格不一致怎麼辦？
    - D-Q10: 團隊不熟 OOP/FSM 導致落地困難怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q4: 物件導向（OOP）思維如何幫助 API 設計？
    - A-Q5: 封裝在 API 設計中的核心價值是什麼？
    - A-Q10: 為什麼要在設計階段就考量安全性？
    - A-Q16: 什麼是「降級」驗證法？為何有效？
    - A-Q17: 為何以 JSON/NoSQL 思維建模 Entity？
    - A-Q18: 靜態方法與實例方法如何對映 REST？
    - A-Q19: 本文中的角色 A～E 分別代表什麼？
    - B-Q1: Contract First 的開發流程如何運作？
    - B-Q2: FSM 驅動的 API 執行流程為何？
    - B-Q3: 封裝如何保證狀態一致性與安全性？
    - B-Q4: 角色-範圍-操作的授權模型如何設計？
    - B-Q6: 事件機制的 Payload 與型態如何設計？
    - B-Q7: 中介軟體如何把 API Key/JWT 轉成 IPrincipal？
    - C-Q1: 如何用 C# 定義 Member 狀態列舉與類別骨架？
    - C-Q4: 如何在 ASP.NET Core 設定 JWT 與 AuthorizeAttribute？
    - C-Q5: 如何設計 OAuth2 Scope 並在 OpenAPI 宣告？
    - C-Q6: 如何撰寫 Webhook 接收端並驗證簽章？
    - C-Q7: 如何用 List/Dictionary 模擬 Repository 驗證 FSM？
    - D-Q1: 若有人嘗試直接修改 state 欄位怎麼辦？
    - D-Q2: 兩個動作並發導致狀態競爭如何處理？

- 高級者：建議關注哪 15 題
    - A-Q14: OpenAPI 與 AsyncAPI 有何差異？
    - A-Q20: 如何避免 API 過度設計？判斷原則是什麼？
    - B-Q5: API Key 與 OAuth2 Scopes 機制有何差異？
    - B-Q8: OpenAPI 的安全與 Scope 如何宣告？
    - B-Q9: AsyncAPI 的核心架構與適用情境是什麼？
    - B-Q10: OOP 到 REST 的規則映射是什麼？
    - B-Q11: Mock Server/SDK/文件如何形成工具鏈？
    - B-Q12: 為何要標準化四構件？
    - C-Q8: 如何實作狀態變更的悲觀與樂觀鎖？
    - C-Q9: 如何設計資料遮罩？
    - D-Q3: Scope 設計過細或過粗怎麼調整？
    - D-Q4: 過度正規化導致 API 易碎如何改善？
    - D-Q6: Webhook 被偽造或重放攻擊怎麼處理？
    - D-Q7: Query/Export 被濫用爬資料怎麼防範？
    - D-Q9: 合約變更如何兼顧版本相容？