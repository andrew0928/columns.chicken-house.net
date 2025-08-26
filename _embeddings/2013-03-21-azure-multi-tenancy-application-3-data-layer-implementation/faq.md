# [Azure] Multi-Tenancy Application #3, (資料層)實作案例

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是多租戶（Multi-Tenancy）應用？
- A簡: 一套系統服務多個客戶，各自隔離資料與設定，於同一基礎設施共享資源。
- A詳: 多租戶應用是指一套軟體同時服務多個獨立客戶（租戶），每個租戶擁有隔離的資料、配置與使用觀感。底層運算與儲存資源共用，以提升資源利用率與降低成本。設計重點在「資料隔離」、「路由與身分識別」、「資源共享與控管」以及「可觀測性」。對於 SaaS 營運尤為關鍵，因可快速擴展並統一維運。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, A-Q9

A-Q2: 為何在資料層實作租戶隔離？
- A簡: 於 DataContext 層落實隔離，讓上層以一般開發方式安全存取租戶資料。
- A詳: 在資料層（如 DataContext）預先處理租戶範圍，使所有查詢與寫入自動帶入租戶過濾，避免開發者於每次查詢手動加入條件，降低疏失風險並強化一致性。這能提供「像獨立資料庫」的體驗，同時維持共享資源的成本效率，並利於單元測試與維護。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q7

A-Q3: 什麼是租戶隔離（Tenant Isolation）？
- A簡: 確保各租戶資料、設定與行為互不干擾，避免跨租戶存取與洩漏。
- A詳: 租戶隔離確保不同客戶間的資料與操作彼此獨立。隔離可分為資料層（如分庫、分表、分割鍵）、應用層（路由與授權）與網路層（ACL、VNet）。本文主張於 DataContext 層實作行為性隔離，並搭配 MVC 路由在 URL 層清楚劃分租戶上下文，最終再以身分與授權管控入口。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, B-Q5

A-Q4: Hub 與 HubData 是什麼？
- A簡: Hub 指整體平台與共用能力；HubData 指各租戶（客戶）專區內的資料集合。
- A詳: 在本文的模型裡，Hub 代表整體系統（平台）與其跨租戶共用的能力與資源；HubData 則是每個租戶私有的資料，如會員、訂單等。HubDataContext 會在租戶範圍內提供 HubData 的查詢與操作，同時也提供不受租戶限制的全域資料存取，以滿足共享資料需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q6, B-Q21

A-Q5: HubData 與全域共用資料有何差異？
- A簡: HubData 屬單一租戶私有；全域資料跨租戶共用，無租戶過濾限制。
- A詳: HubData 承載與單一租戶直接相關的業務資料，需嚴格套用租戶過濾與授權；全域共用資料則由平台維護或跨租戶共享（如餐廳清單），通常不施加租戶範圍限制，但仍需權限控管與審計。設計上應明確分層，避免誤將共享資料套用租戶過濾造成查無資料或權限錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q6, D-Q8

A-Q6: 何謂 HubDataContext？
- A簡: 一個具租戶感知的資料存取介面，預先套用租戶範圍與過濾。
- A詳: HubDataContext 是可在取得時即鎖定當前租戶範圍的資料存取抽象。它對租戶資料提供已過濾的集合（如 IQueryable），確保不會誤取他人資料；對全域資料則提供無租戶限制的存取入口。此設計讓開發者以一般 LINQ 模式操作資料，同時維持隔離與正確性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q7, C-Q3

A-Q7: HubDataContext 應具備哪些核心能力？
- A簡: 鎖定租戶範圍、提供已過濾集合、允許全域資料存取、可測試性良好。
- A詳: 能力包含：1) 取得時即明確當前租戶（Client Scope）；2) 對租戶資料提供預過濾的集合以避免資料外洩；3) 對全域資料提供不受租戶限制的查詢介面；4) 良好抽象以利單元測試與替換儲存體；5) 與 Web 路由與身分系統無縫整合，形成端到端的一致租戶上下文。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q6, B-Q22

A-Q8: 何謂「模擬每租戶獨立儲存體」？
- A簡: 在同一實體儲存上，呈現如同每租戶各有獨立資料庫的體驗。
- A詳: 並非真的為每租戶建立獨立實體儲存，而是在資料層以分割鍵、命名空間與過濾邏輯，讓每個租戶的資料讀寫看起來像是專屬庫。此法降成本、好維運，並可保有強隔離的開發體驗。Azure Table Storage 可用 PartitionKey 充當租戶邊界，達成此目標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, C-Q4

A-Q9: 為什麼在網址層提供每租戶獨立 URL？
- A簡: 用路由切出 client 層，形成清楚租戶上下文與更佳使用者體驗。
- A詳: 以 /{client}/{controller}/{action} 或子網域呈現，能讓使用者、系統與記錄清楚辨識租戶上下文，有助快取、SEO、權限判斷與問題追蹤。亦可降低後端判定租戶的複雜度，將租戶識別作為整體請求的根本前提，與資料層隔離相呼應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, C-Q2

A-Q10: 為何選擇 MVC Routing 實現客製化路由？
- A簡: MVC 路由可彈性插入 client 維度，擴充性高、易統一處理租戶識別。
- A詳: MVC 的路由系統提供自訂樣板、約束與處理程序，便於在 URL 的第一段導入租戶代碼，並能集中處理解析、驗證與落地到 Tenant Context。相較硬碼判斷或分散在各控制器，路由層統一處理更一致、可測試、可擴充，亦便於日後支援子網域或其他識別方式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q20, C-Q2, C-Q1

A-Q11: 何謂 Code First 與「無綱要」資料模型？
- A簡: 由程式碼定義資料結構，對應到儲存體，不需先建固定綱要。
- A詳: Code First 指先以程式碼定義實體類別與關係，再由框架產生或對應資料存放結構。Azure Table Storage 屬 schema-less，欄位以屬性動態儲存，必需欄位多為 PartitionKey/RowKey/Timestamp。此模式加速演進，但需自律治理欄位變更與相容性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, B-Q14, C-Q4

A-Q12: Azure Table Storage 適合多租戶的原因？
- A簡: 以 PartitionKey 做租戶邊界，成本低、擴展佳、批次同分割效率高。
- A詳: Table Storage 提供大規模鍵值/寬表存取。以租戶 ID 作為 PartitionKey，可自然形成租戶隔離邊界，支援同分割的批次交易與高效查詢。成本相對低廉，吞吐可水平擴展。惟不支援複雜 JOIN 與二級索引，需以設計換取查詢效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q15, D-Q4

A-Q13: 訂便當系統為何適合做成 SaaS？
- A簡: 服務團體訂餐情境，需求共通；多租戶共享平台資料帶來規模效益。
- A詳: 訂便當系統用戶多為團隊/部門，功能如每日訂單與簡單會員管理高度共通，適合以多租戶模式提供。平台可集中維護餐廳資訊與營運報表，讓客戶即開即用，並持續受益於平台演進與資料網路效應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q6, B-Q25

A-Q14: SaaS 營運對 Hosting 端的價值是什麼？
- A簡: 共用資料資產、合作商家導流、抽成與 BI 洞察，擴大營收模式。
- A詳: Hosting 端可集中管理餐廳與菜單等共用資料，降低客戶導入成本；與商家合作導流帶來抽成空間；透過跨租戶 BI 分析了解需求趨勢，優化供給與產品路線。亦可設計租戶共享/評價機制，強化平台網路效應與留存。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q25, D-Q8

A-Q15: 什麼是客戶範圍（Client Scope）？
- A簡: 一次請求或作業所屬的租戶識別與上下文，用於授權與過濾。
- A詳: Client Scope 是在應用處理流程中，用以識別當前租戶的上下文資訊，通常含租戶 ID、名稱、權限範圍與語系等。它在路由解析與驗證後建立，隨請求傳遞至資料層，驅動租戶過濾、審計與觀測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q9, C-Q1

A-Q16: 多租戶架構中 Web 與 Data 為何需緊密結合？
- A簡: 路由識別與資料過濾需一致，確保端到端正確租戶上下文。
- A詳: Web 層決定租戶識別（URL、Subdomain、Token），資料層負責落實租戶隔離。若兩者未對齊，易出現權限錯誤或資料外洩。將租戶上下文自路由一路傳遞至 DataContext，可確保一致性、簡化程式與提升可測試性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q2, C-Q2

A-Q17: EF 與 Azure Table Storage 有何差異？
- A簡: EF 為關聯式 ORM；Table 為無綱要寬表，強鍵值查詢、弱關聯。
- A詳: EF 針對關聯式資料庫，強關聯/交易/查詢語意；Table Storage 為非關聯、鍵值寬表，只有 PartitionKey/RowKey/Timestamp 與動態屬性，無 JOIN 與二級索引。設計需偏向冗餘與查詢導向資料模型，換取效能與成本優勢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q13, B-Q15

A-Q18: 什麼是應用層虛擬化（虛擬目錄）？
- A簡: 以路由/子網域讓每租戶呈現如同獨立應用的邏輯隔間。
- A詳: 應用層虛擬化透過路由或子網域，將單一應用邏輯分割為多個租戶視角的虛擬實例。每租戶擁有獨立 URL 空間與設定，提升體驗與治理；搭配資料層隔離與快取命名空間，形成端到端的租戶隔間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q20, C-Q2

A-Q19: 多租戶資料設計的常見策略差異？
- A簡: 分庫、分綱要、分表、共享表分割鍵，各有隔離與成本權衡。
- A詳: 策略包括：每租戶獨立資料庫（隔離強、成本高）、共庫分綱要/分表（隔離中等、管理較複雜）、共享表以分割鍵隔離（成本低、邏輯隔離）。選擇取決於合規、規模、IT 能力與成本。本文採共享表＋分割鍵方式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q5, D-Q3

A-Q20: 為何雲端應用需要更重視單元測試？
- A簡: 佈署與依賴外部資源複雜，測試降低風險並提升變更信心。
- A詳: 雲端應用牽涉分散式資源、網路延遲與一致性議題，錯誤排查成本高。完備的單元與整合測試可在本機或 CI 階段提早發現問題，確保租戶隔離、授權、查詢效能與例外處理正確。資深前輩經驗亦指出，測試投資在雲端回報更高。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q7, D-Q5

A-Q21: 什麼是 POC 與 User Story 在此案例的角色？
- A簡: POC 驗證關鍵技術可行；Story 收斂範圍聚焦核心目標。
- A詳: POC（概念驗證）用於快速驗證多租戶資料層與路由可行性，避免過度設計。以 User Story 界定實作範圍與優先級，先交付租戶隔離/全域資料/路由整合等核心能力，再迭代擴展 BI、抽成等營運功能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q2, B-Q1

A-Q22: 什麼是全域共用資料的範疇？
- A簡: 平台維護、跨租戶可見的資料，如餐廳清單、菜單、公告等。
- A詳: 全域共用資料多為營運端整理、跨租戶有價值的內容，例如合作餐廳、菜單、促銷、公告、系統設定。其存取不受租戶過濾，但仍應控管角色權限、版控與審計，並提供租戶可選擇採用與覆寫的彈性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, B-Q8, D-Q8

A-Q23: 多租戶系統中的資料安全重點？
- A簡: 身分驗證、授權、租戶過濾、審計與加密，並防資料外洩。
- A詳: 安全關鍵包含：強固登入與租戶綁定、在資料層強制租戶過濾、審計每次跨界操作、靜態與傳輸加密、最小權限原則與密鑰管理。持續性自動化測試與觀測（告警/追蹤）可早期發現越權或洩漏風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, D-Q1, D-Q7

A-Q24: 何謂租戶感知（Tenant-aware）資料存取？
- A簡: 資料 API 會自動帶入租戶上下文，隱藏過濾細節避免疏漏。
- A詳: 租戶感知意味著開發者在使用資料存取介面時，無須手動加入租戶條件，框架自動依當前 Tenant Context 加上 PartitionKey 過濾或命名空間。此抽象可大幅降低跨租戶查詢風險並提升開發效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q7, C-Q3

A-Q25: 何謂在路由中加入 Client 層級的做法？
- A簡: 在 URL 模板新增 {client} 參數，統一解析租戶並傳遞下游。
- A詳: 透過 route template（如 "/{client}/{controller}/{action}/{id?}"）或 Attribute Routing，在最前段攜帶租戶代碼；自訂 RouteConstraint 驗證格式與存在性；在 Middleware/Filter 建立 Tenant Context，並注入到 DataContext 與服務層。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q20, C-Q2

### Q&A 類別 B: 技術原理類

B-Q1: HubDataContext 如何運作以確保租戶隔離？
- A簡: 於建立時注入 Tenant Context，對租戶集合預設過濾，對全域集合不過濾。
- A詳: 原理說明：HubDataContext 在建立時接收 ITenantProvider，取得當前租戶 ID。關鍵流程：1) 解析路由得 tenantId；2) 建立 Tenant Context；3) 建構 DataContext 時綁定 tenantId；4) 針對租戶資料類型提供已過濾 IQueryable；5) 全域資料則提供獨立入口。核心組件：ITenantProvider、TenantContext、IHubDataContext、儲存體存取器（如 CloudTableClient）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q7, C-Q3

B-Q2: 從 URL 到資料查詢的執行流程是什麼？
- A簡: 路由解析 client→驗證→建立 Tenant Context→注入 DataContext→執行查詢。
- A詳: 原理說明：將租戶識別提早到路由階段，成為請求上下文的根。關鍵步驟：1) 路由擷取 {client}；2) 驗證是否有效租戶；3) 建立 Tenant Context；4) 透過 DI 注入帶租戶的 DataContext；5) 應用層使用 LINQ 查詢；6) DataContext 轉為儲存體查詢。核心組件：Route/Constraint、AuthN/AuthZ、TenantMiddleware/Filter、DI 容器、IHubDataContext。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q3, C-Q1

B-Q3: MVC 路由如何設計以加入 client 段？
- A簡: 自訂路由模板與約束，確保 client 合法並可被全域存取。
- A詳: 原理說明：在 RouteConfig 或 Attribute Routing 設定 "/{client}/{controller}/{action}/{id?}"。關鍵步驟：1) 定義 client 參數；2) IRouteConstraint 驗證格式與存在；3) 在 ActionFilter/Middleware 建立 Tenant Context。核心組件：Route、IRouteConstraint、ActionFilter、ModelBinder（可選）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q2, B-Q20

B-Q4: 目前租戶是如何被判定的？
- A簡: 透過路由片段、子網域或權杖宣告，解析為租戶 ID。
- A詳: 原理說明：可用 path 段（client）、subdomain（client.example.com）或 JWT/Claims 中的 tenant_id。關鍵步驟：1) 擷取識別；2) 映射至內部租戶 ID；3) 驗證狀態；4) 建立上下文。核心組件：DNS/路由、Token 驗證、TenantResolver/Provider、快取以減少查表成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q2, C-Q1

B-Q5: Azure Table Storage 的 PartitionKey/RowKey 機制是什麼？
- A簡: 以 PartitionKey 分割資料，RowKey 唯一化排序；查詢與批次依此優化。
- A詳: 原理說明：PartitionKey 決定資料分割與擴展/交易邊界；RowKey 為分割內唯一鍵且排序依字典序。關鍵步驟：設計鍵以支援高效查詢（等值/範圍）與批次（同 PartitionKey）。核心組件：CloudTable、TableQuery、Transaction/Batches（同一 Partition 才支援）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q6, C-Q9

B-Q6: 如何設計鍵組合以達到每租戶隔離？
- A簡: 以租戶 ID 作 PartitionKey，RowKey 依查詢需求設計唯一鍵。
- A詳: 原理說明：使用 tenantId 作 PartitionKey，即可形成租戶邊界。關鍵步驟：1) 選擇 PartitionKey=tenantId；2) 依查詢習慣設計 RowKey（如日期+流水號）；3) 為跨維度查詢建立反向索引表。核心組件：鍵設計規則、時間排序、輔助索引表（如 UserIndexTable）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q5, D-Q3

B-Q7: 租戶過濾的 LINQ 查詢是如何實現的？
- A簡: 封裝租戶預過濾 IQueryable，透明加上 PartitionKey 條件。
- A詳: 原理說明：IHubDataContext 返回已綁定 PartitionKey 的 IQueryable<T>。關鍵步驟：1) 取得 tenantId；2) 生成 TableQuery 以 PartitionKey=tenantId 為基礎；3) 將上層 LINQ 表達式合併轉譯。核心組件：IQueryable Provider、Expression Visitor、TableQuery 轉譯器。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q24, C-Q5, D-Q1

B-Q8: 全域資料存取的機制與租戶資料有何不同？
- A簡: 全域資料不套租戶過濾，通常獨立表或特定 Partition 管理。
- A詳: 原理說明：全域資料使用獨立 CloudTable 或特殊 PartitionKey（如 “GLOBAL”），不受租戶上下文限制。關鍵步驟：1) 獨立 DataSet 入口；2) 權限檢查；3) 查詢不帶 tenant 過濾。核心組件：GlobalRepository、授權 Filter、審計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q6, D-Q8

B-Q9: 依請求建立租戶內容（Tenant Context）的架構是什麼？
- A簡: 由 Middleware/Filter 建立 TenantContext，並透過 DI 傳遞至下游。
- A詳: 原理說明：將租戶解析抽象為 ITenantResolver。關鍵步驟：1) 在請求起點解析租戶；2) 產生 TenantContext；3) 註冊到 DI 的 Scoped 生命週期；4) 下游服務取用。核心組件：ITenantResolver、TenantContext、DI Container（Scoped）、ActionFilter。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q1, C-Q8

B-Q10: 使用 DI 注入租戶提供者的設計是什麼？
- A簡: 定義 ITenantProvider，由容器以 Scoped 注入至 DataContext 與服務。
- A詳: 原理說明：以介面隔離租戶讀取行為，便於測試與替換。關鍵步驟：1) 定義 ITenantProvider；2) 在 Middleware 設定當前租戶；3) 以 Scoped 註冊；4) 於 HubDataContext 注入使用。核心組件：ITenantProvider、DI Container（Autofac/Unity）、Factory/Provider 模式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q8, B-Q1

B-Q11: 多租戶 Repository Pattern 的設計原理？
- A簡: Repository 內建租戶過濾與鍵設計，對外提供租戶安全 API。
- A詳: 原理說明：Repository 封裝儲存體細節與租戶過濾，提供聚合根的查詢與命令。關鍵步驟：1) 注入 HubDataContext；2) 實作 GetById/Find/Save 帶租戶過濾；3) 全域資料以獨立 Repository。核心組件：IRepository<T>、IHubDataContext、Unit of Work（選用）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q5, D-Q1

B-Q12: 單元測試如何模擬 Azure Table Storage？
- A簡: 以 Azurite/模擬器或 In-Memory Stub，隔離外部依賴與網路。
- A詳: 原理說明：將儲存體抽象為介面，允許測試替換。關鍵步驟：1) 將 CloudTableClient 包裝為介面；2) 測試注入 In-Memory 或 Azurite；3) 準備測試資料；4) 驗證租戶隔離與查詢行為。核心組件：Test Double、Azurite、Fixture/Factory。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q7, D-Q5

B-Q13: Table Storage 與 EF Code First 的對應心法？
- A簡: 類別即資料模型，但需以鍵與寬表設計取代關聯與遷移。
- A詳: 原理說明：類別代表寬表列，屬性即欄位。關鍵步驟：1) 設計 PartitionKey/RowKey；2) 將關聯拆為索引/冗餘；3) 以版本欄位管理相容性。核心組件：ITableEntity、序列化器、版本/相容性策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q4, D-Q4

B-Q14: Entity 與 TableEntity 的關係與序列化機制？
- A簡: ITableEntity 提供鍵與屬性字典，屬性被動態序列化到存放。
- A詳: 原理說明：Table SDK 以 ITableEntity 或 TableEntity 封裝 PartitionKey、RowKey、Timestamp 與屬性字典。關鍵步驟：1) 實作屬性對應；2) 透過 SDK 轉譯；3) 注意型別支援與 null 行為。核心組件：ITableEntity、EntityProperty、Edm 型別對應。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q5, D-Q6

B-Q15: 查詢與索引策略在 Table Storage 的原理？
- A簡: 依鍵查詢最有效；範圍查詢用 RowKey；其他需自建反向索引表。
- A詳: 原理說明：Table 僅對 PartitionKey/RowKey 最佳化。關鍵步驟：1) 盡量使用 PartitionKey 等值；2) RowKey 支援範圍排序；3) 自建輔助表（如 byUser、byDate）；4) 維護一致性。核心組件：輔助索引表、事件驅動同步、最終一致性設計。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q4, C-Q5, C-Q9

B-Q16: 高併發下的分割與熱點避免原理？
- A簡: 分散 PartitionKey、控制鍵散佈與批次大小，平衡熱點與一致性。
- A詳: 原理說明：單一 PartitionKey 容易成熱點。關鍵步驟：1) 規劃鍵散佈（如租戶+日期）；2) 寫入節流與重試；3) 依 workload 調整批次；4) 監控吞吐/錯誤。核心組件：鍵設計、重試策略、遙測監控（Metrics/Logs）。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q3, D-Q4, C-Q9

B-Q17: 多租戶快取的命名空間化原理？
- A簡: 以租戶 ID 作為快取鍵前綴，避免跨租戶污染與擊穿。
- A詳: 原理說明：快取需與租戶綁定，避免資料混淆。關鍵步驟：1) 定義 cacheKey=tenantId:logicalKey；2) 設定不同 TTL；3) 失效策略含租戶維度。核心組件：CacheProvider、KeyBuilder、觀測告警（命中率）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, D-Q1, D-Q4

B-Q18: 租戶層級的日誌追蹤與相互關聯？
- A簡: 日誌與追蹤內含 tenantId/correlationId，便於跨層排錯。
- A詳: 原理說明：將 tenantId、correlationId 注入 Log Scope。關鍵步驟：1) 請求建立時生成 correlationId；2) 綁定 tenantId；3) 於各層記錄；4) 查詢與告警基於兩者。核心組件：Logging Scope、分散式追蹤、結構化日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2, A-Q20

B-Q19: 使用 Claims 載入租戶資訊的機制？
- A簡: 於 JWT/Claims 設置 tenant_id，於授權與資料層統一取用。
- A詳: 原理說明：身分提供者在 Token 內發出 tenant_id。關鍵步驟：1) 驗證 Token；2) 從 Claims 取出 tenant_id；3) 交由 TenantProvider；4) 與路由比對一致性。核心組件：OpenID Connect/JWT、ClaimsPrincipal、Authorization Handler。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, B-Q4, C-Q1

B-Q20: 自訂 RouteConstraint 與 Attribute Routing 原理？
- A簡: 以 IRouteConstraint 驗證 client；Attribute Routing 提供細粒度控制。
- A詳: 原理說明：IRouteConstraint 可檢查 client 格式與存在性；Attribute Routing 在控制器上標註 {client} 參數。關鍵步驟：1) 建立 Constraint；2) 註冊路由；3) 於動作方法接 client。核心組件：IRouteConstraint、RouteAttribute、ActionFilter。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q3, A-Q25

B-Q21: Hub 與 HubData 的邏輯邊界如何設計？
- A簡: Hub 提供共用能力；HubData 專注租戶資料，兩者明確分層依賴。
- A詳: 原理說明：以分層架構將平台通用功能（Hub）與租戶資料域（HubData）分離。關鍵步驟：1) 定義邊界與介面；2) HubData 僅依賴 Hub 契約；3) 嚴格限制跨界存取。核心組件：Domain/Module 邊界、接口契約、依賴反轉。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q22, C-Q3

B-Q22: HubDataContext 介面設計要素有哪些？
- A簡: WithTenantScope、HubSet<T>()、GlobalSet<T>()、提交與批次支援。
- A詳: 原理說明：介面需同時支持租戶資料集合與全域集合。關鍵步驟：1) 定義 HubSet<T> 回傳過濾集合；2) GlobalSet<T> 不過濾；3) Save/Batch APIs；4) 可替換的儲存實作。核心組件：IHubDataContext、IQueryable Provider、批次操作封裝。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q3, C-Q9

B-Q23: 建立可替換的儲存體實作如何設計？
- A簡: 以抽象封裝 SDK，透過工廠或 DI 切換 Emulator/正式環境。
- A詳: 原理說明：包裝 CloudTableClient 為介面；以組態決定連線。關鍵步驟：1) 定義 ITableStore；2) 讀取連線字串；3) 於啟動註冊不同實作；4) 測試時注入 stub。核心組件：Factory、DI、設定管理（appsettings）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, B-Q12, C-Q8

B-Q24: Azure Table 批次操作與事務範圍原理？
- A簡: 同 PartitionKey 才能批次；批次內具原子性，超出則無事務。
- A詳: 原理說明：Batch 需同一 PartitionKey，最大 100 筆，具原子性。關鍵步驟：1) 分群資料；2) 建立 TableBatchOperation；3) 提交與重試。核心組件：Batch API、重試策略、冪等設計（避免重送副作用）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q6, B-Q5

B-Q25: 備份、匯入與跨租戶共享資料的原理？
- A簡: 以租戶為單位導出/匯入，或維護全域表由平台控管共享。
- A詳: 原理說明：備份可按租戶分割 Partition 匯出；共享資料放置全域表。關鍵步驟：1) 導出 partition 範圍；2) 匯入時重建鍵；3) 權限審計；4) 資料血緣追蹤。核心組件：匯入匯出工具、審計、目錄（Catalog）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6, D-Q9

### Q&A 類別 C: 實作應用類

C-Q1: 如何實作 ITenantProvider 與 per-request 租戶解析？
- A簡: 建立 ITenantProvider，於 Middleware/Filter 解析 client 並以 Scoped 注入。
- A詳: 具體實作步驟：1) 定義 ITenantProvider.GetTenantId(); 2) 建立 TenantMiddleware 解析路由的 {client} 或 Claims；3) 設定到 HttpContext.Items 或 Provider；4) 於 DI 註冊 Scoped。程式碼片段:
  public interface ITenantProvider{string TenantId{get;}}
  // 在中介軟體設定 provider.TenantId = routeData["client"]
  注意事項：驗證 client 合法性、提供預設/拒絕策略、記錄 correlationId。最佳實踐：將解析與驗證分離、提供快取減少查表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q9, B-Q10

C-Q2: 如何在 MVC 設計 /{client}/{controller}/{action} 路由？
- A簡: 設定路由模板與 IRouteConstraint，統一從 URL 擷取 client。
- A詳: 具體實作步驟：1) RouteConfig.MapRoute("Tenant","{client}/{controller}/{action}/{id}", new{action="Index",id=UrlParameter.Optional}, new { client=new ClientConstraint()}); 2) ClientConstraint 驗證格式/存在；3) 在 ActionFilter 建立 Tenant Context。程式碼:
  routes.MapRoute("Tenant","{client}/{controller}/{action}/{id}", ...);
  注意事項：避免與靜態檔案衝突；為未帶 client 的路由設計導向。最佳實踐：提供子網域模式的可切換性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q20, A-Q25

C-Q3: 如何實作 HubDataContext（Azure Table）與租戶過濾？
- A簡: 在建構時注入 ITenantProvider，HubSet<T>() 回傳已綁定 PartitionKey 的查詢。
- A詳: 步驟：1) 定義 IHubDataContext.HubSet<T>(), GlobalSet<T>(); 2) 於建構子注入 ITenantProvider 與 CloudTableClient；3) HubSet 內建 PartitionKey=tenantId；4) Save/Batch 需代入租戶鍵。程式碼片段:
  public IQueryable<T> HubSet<T>() where T:ITableEntity => table.AsQueryable().Where(e=>e.PartitionKey==_tenantId);
  注意：不可外洩 TableClient；全域資料請用 GlobalSet。最佳實踐：以 Factory 建立對應表。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q22, C-Q8

C-Q4: 如何定義租戶資料實體（Order, Member）的鍵？
- A簡: PartitionKey=tenantId；RowKey 以查詢需求設計，如 yyyyMMdd-流水號。
- A詳: 步驟：1) 類別實作 ITableEntity；2) 設定 PartitionKey=tenantId；3) 設計 RowKey=日期+ID 或 GUID；4) 建輔助索引表（如 byUser）。程式碼:
  class Order:ITableEntity{ public string PartitionKey{get;set;} public string RowKey{get;set;} /*...*/ }
  注意：RowKey 排序影響查詢順序；避免過長鍵。最佳實踐：時間序用可排序字串，避免熱點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q14, B-Q15

C-Q5: 如何查詢某租戶的訂單清單？
- A簡: 透過 HubSet<Order>() 直接 LINQ 篩選，底層已套用 PartitionKey。
- A詳: 步驟：1) 注入 IHubDataContext；2) 使用 var q=ctx.HubSet<Order>().Where(o=>o.Date==today); 3) ToListAsync(); 程式碼:
  var orders = await ctx.HubSet<Order>()
     .Where(o=>o.Date==today).ToListAsync();
  注意：避免跨租戶條件（不需再加 tenantId）；善用 RowKey 範圍提高效率。最佳實踐：建立必要輔助表加速非鍵查詢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q15, D-Q4

C-Q6: 如何建立全域共用的餐廳清單並存取？
- A簡: 建立 GlobalTable，使用固定 PartitionKey（GLOBAL），不套租戶過濾。
- A詳: 步驟：1) 建立餐廳表 Restaurants；2) 實體 PartitionKey="GLOBAL"；3) 於 IHubDataContext.GlobalSet<Restaurant>() 提供查詢；4) 管理端維護資料。程式碼:
  var list = await ctx.GlobalSet<Restaurant>().ToListAsync();
  注意：權限控管只允許平台維護；租戶可引用或覆寫。最佳實踐：審計全域變更、提供快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, A-Q22, B-Q25

C-Q7: 如何撰寫單元測試驗證跨租戶隔離？
- A簡: 使用 In-Memory/Azurite，建立兩租戶資料，驗證互查不到對方資料。
- A詳: 步驟：1) 注入測試用 ITableStore；2) 建立 ctxA(tenantA)、ctxB(tenantB)；3) 分別寫入訂單；4) 從對方 ctx 查詢應為空；5) 驗證全域資料兩邊皆可見。程式碼:
  Assert.Empty(ctxA.HubSet<Order>().Where(o=>o.RowKey==orderB));
  注意：測試隔離、清理資料；考慮最終一致性。最佳實踐：以 Fixture 建立測試資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q20, D-Q5

C-Q8: 如何以 DI 容器注入 HubDataContext？
- A簡: 於組態註冊 IHubDataContext 為 Scoped，依租戶建立實例。
- A詳: 步驟：1) services.AddScoped<ITenantProvider, TenantProvider>(); 2) services.AddScoped<IHubDataContext, HubDataContext>(); 3) 在 HubDataContext 注入 CloudTableClient 與 TenantProvider；4) 控制器/服務取用。程式碼:
  services.AddScoped<IHubDataContext, HubDataContext>();
  注意：生命週期用 Scoped；避免單例持有租戶狀態。最佳實踐：以 Factory 產生表參照。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, B-Q23, C-Q3

C-Q9: 如何使用批次寫入同租戶多筆資料？
- A簡: 將同 PartitionKey 的實體分批（<=100）加入 Batch，一次提交。
- A詳: 步驟：1) 按租戶分群；2) 將每 100 筆建立 TableBatchOperation；3) ExecuteBatchAsync；4) 重試策略。程式碼:
  var batch=new TableBatchOperation();
  batch.InsertOrReplace(entity);
  await table.ExecuteBatchAsync(batch);
  注意：同一批需相同 PartitionKey；控制批次大小。最佳實踐：冪等設計與失敗重送。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q24, B-Q5, D-Q6

C-Q10: 如何設定 Azure 儲存連線與本機 Azurite 測試？
- A簡: 使用連線字串切換本機/雲端，透過 DI/設定檔統一管理。
- A詳: 步驟：1) appsettings.json 設定 "UseAzurite" 與連線字串；2) 啟動時讀取設定選擇端點；3) Azurite: UseDevelopmentStorage=true；4) 正式：使用 Azure 儲存連線字串。程式碼:
  var conn = cfg["Storage:ConnectionString"];
  var acct = CloudStorageAccount.Parse(conn);
  注意：避免將密鑰入庫；使用 Key Vault。最佳實踐：區分環境設定與健康檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q23, B-Q12, D-Q4

### Q&A 類別 D: 問題解決類

D-Q1: 遇到跨租戶資料外洩怎麼辦？
- A簡: 先停用可疑功能，檢查路由與 DataContext 過濾，補測試與審計。
- A詳: 症狀：A 租戶可見 B 租戶資料。可能原因：租戶過濾遺漏、GlobalSet 被誤用、快取未命名空間化。解決步驟：1) 熱修補停用相關路由；2) 稽核查詢點；3) 強制 HubSet 過濾；4) 修正快取鍵；5) 增補單元/整測。預防：租戶感知抽象、靜態分析與安全測試、審計與告警。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q17, A-Q23

D-Q2: 路由無法解析 client 造成 404 怎麼辦？
- A簡: 檢查路由順序、Constraint 與保留路徑，提供預設導向與錯誤頁。
- A詳: 症狀：正確 URL 返回 404。原因：路由順序不當、Constraint 拒絕、靜態路徑衝突。解法：1) 將租戶路由置前；2) 放寬或修正 Constraint；3) 排除靜態資源；4) 未帶 client 時導向登入/挑選租戶。預防：路由測試、記錄路由配對日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q20, C-Q2

D-Q3: 分割鍵設計不當導致熱點怎麼辦？
- A簡: 重新設計鍵散佈（加時間/哈希），分批遷移並監控吞吐。
- A詳: 症狀：單租戶/單鍵高延遲或限流。原因：大量寫入集中單一 PartitionKey。解法：1) 重新設計鍵（tenantId+yyyyMMdd/哈希前綴）；2) 建新表並雙寫；3) 後台搬遷舊資料；4) 切換讀寫。預防：負載測試、容量規劃、指標告警。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, B-Q6, B-Q24

D-Q4: Azure Table 查詢效能不佳的原因？
- A簡: 未用鍵查詢、範圍設計不當或缺輔助索引，導致全表掃描。
- A詳: 症狀：查詢慢、費用上升。原因：無 PartitionKey 等值條件、RowKey 範圍不利、缺輔助表。解法：1) 以鍵重寫查詢；2) 新增索引表（byUser/byDate）；3) 加入快取；4) 監控與調整。預防：設計前定義查詢模式，建立對應資料投影。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q5, C-Q10

D-Q5: 單元測試不穩定（最終一致性）怎麼辦？
- A簡: 使用 Azurite 或 In-Memory，加入重試與延遲，隔離測試資料。
- A詳: 症狀：偶爾查不到剛寫入資料。原因：雲端最終一致性與網路延遲。解法：1) 本機使用 Azurite；2) 測試加入等待/重試；3) 測試資料命名隔離；4) 測試後清理。預防：分離單元與整測、以契約測試確保行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q7, A-Q20

D-Q6: 批次寫入失敗顯示 PartitionKey 不一致？
- A簡: 確認同一批資料 PartitionKey 相同，控制批次大小與重試。
- A詳: 症狀：Batch 提交拋例外。原因：批次內含不同 PartitionKey、超量或單筆無效。解法：1) 依 PartitionKey 分批；2) 每批<=100；3) 驗證鍵與資料長度；4) 重試策略。預防：在應用層分群批次、加前置驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q24, C-Q9, B-Q5

D-Q7: 使用者登入後被導向錯誤租戶怎麼辦？
- A簡: 對齊路由 client 與 Claims 租戶，修正綁定與授權檢查。
- A詳: 症狀：登入成功但進入他租戶頁面。原因：Claims 與 URL 不一致、Session 汙染、快取鍵未隔離。解法：1) 登入後強制選擇租戶；2) 比對 URL 與 Claims；3) 校正 TenantProvider；4) 清快取。預防：單一事實來源、於 Filter 檢查一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, B-Q4, A-Q23

D-Q8: 全域資料被誤套租戶過濾怎麼排除？
- A簡: 使用 GlobalSet/獨立 Repository，於程式與測試明確界定。
- A詳: 症狀：查不到全域餐廳等資料。原因：使用 HubSet 錯誤過濾。解法：1) 導入 GlobalSet API；2) 程式碼審查；3) 加測試驗證全域可見性。預防：介面命名清晰、靜態分析/規則阻擋誤用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q6, B-Q22

D-Q9: 變更 PartitionKey 導致資料遷移風險如何處理？
- A簡: 採雙寫與後台搬遷，灰度切換讀路徑，確保一致性與回滾。
- A詳: 症狀：需改鍵以解熱點或新查詢。風險：離線時間、資料不一致。解法：1) 建新表/鍵；2) 寫入同時寫新舊；3) 背景搬遷舊資料；4) 切換讀；5) 觀察與回滾機制。預防：前期鍵設計與負載預估、資料血緣紀錄。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, B-Q25, C-Q9

D-Q10: 刪除資料遇到衝突（412 Precondition Failed）？
- A簡: 使用 ETag 比對，遇衝突先讀取最新版本再重試或放棄。
- A詳: 症狀：刪除/更新拋 412。原因：ETag 不匹配，併發更新。解法：1) 先查最新 ETag；2) 重試刪除；3) 必要時採條件覆寫；4) 記錄衝突。預防：樂觀鎖、清晰併發策略、UI 呈現版本衝突。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q24, C-Q5, B-Q14

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是多租戶（Multi-Tenancy）應用？
    - A-Q3: 什麼是租戶隔離（Tenant Isolation）？
    - A-Q2: 為何在資料層實作租戶隔離？
    - A-Q5: HubData 與全域共用資料有何差異？
    - A-Q9: 為什麼在網址層提供每租戶獨立 URL？
    - A-Q10: 為何選擇 MVC Routing 實現客製化路由？
    - A-Q11: 何謂 Code First 與「無綱要」資料模型？
    - A-Q12: Azure Table Storage 適合多租戶的原因？
    - A-Q13: 訂便當系統為何適合做成 SaaS？
    - A-Q20: 為何雲端應用需要更重視單元測試？
    - C-Q2: 如何在 MVC 設計 /{client}/{controller}/{action} 路由？
    - C-Q6: 如何建立全域共用的餐廳清單並存取？
    - C-Q8: 如何以 DI 容器注入 HubDataContext？
    - D-Q2: 路由無法解析 client 造成 404 怎麼辦？
    - D-Q5: 單元測試不穩定（最終一致性）怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: 何謂 HubDataContext？
    - A-Q7: HubDataContext 應具備哪些核心能力？
    - A-Q15: 什麼是客戶範圍（Client Scope）？
    - A-Q16: Web 與 Data 為何需緊密結合？
    - A-Q17: EF 與 Azure Table Storage 有何差異？
    - A-Q25: 何謂在路由中加入 Client 層級的做法？
    - B-Q1: HubDataContext 如何運作以確保租戶隔離？
    - B-Q2: 從 URL 到資料查詢的執行流程是什麼？
    - B-Q3: MVC 路由如何設計以加入 client 段？
    - B-Q4: 目前租戶是如何被判定的？
    - B-Q5: Table 的 PartitionKey/RowKey 機制是什麼？
    - B-Q8: 全域資料存取的機制與租戶資料有何不同？
    - B-Q10: 使用 DI 注入租戶提供者的設計是什麼？
    - B-Q11: 多租戶 Repository Pattern 的設計原理？
    - B-Q13: Table 與 EF Code First 的對應心法？
    - C-Q1: 如何實作 ITenantProvider 與 per-request 租戶解析？
    - C-Q3: 如何實作 HubDataContext 與租戶過濾？
    - C-Q4: 如何定義租戶資料實體的鍵？
    - C-Q5: 如何查詢某租戶的訂單清單？
    - D-Q4: Azure Table 查詢效能不佳的原因？

- 高級者：建議關注哪 15 題
    - A-Q8: 何謂「模擬每租戶獨立儲存體」？
    - A-Q23: 多租戶系統中的資料安全重點？
    - B-Q6: 如何設計鍵組合以達到每租戶隔離？
    - B-Q7: 租戶過濾的 LINQ 查詢是如何實現的？
    - B-Q12: 單元測試如何模擬 Azure Table Storage？
    - B-Q15: 查詢與索引策略在 Table Storage 的原理？
    - B-Q16: 高併發下的分割與熱點避免原理？
    - B-Q17: 多租戶快取的命名空間化原理？
    - B-Q18: 租戶層級的日誌追蹤與相互關聯？
    - B-Q24: Azure Table 批次操作與事務範圍原理？
    - B-Q25: 備份、匯入與跨租戶共享資料的原理？
    - C-Q9: 如何使用批次寫入同租戶多筆資料？
    - D-Q1: 遇到跨租戶資料外洩怎麼辦？
    - D-Q3: 分割鍵設計不當導致熱點怎麼辦？
    - D-Q9: 變更 PartitionKey 導致資料遷移風險如何處理？