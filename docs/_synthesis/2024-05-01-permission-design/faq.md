---
layout: synthesis
title: "xxxxx 架構面試題 #6: 權限管理機制的設計"
synthesis_type: faq
source_post: /2024/05/01/permission-design/
redirect_from:
  - /2024/05/01/permission-design/faq/
---

# xxxxx 架構面試題 #6: 權限管理機制的設計

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是「權限管理」？
- A簡: 定義誰能對哪些資源執行哪些操作的規範機制，兼顧精確度與管理成本。
- A詳: 權限管理是對「誰」（使用者/主體）能對「什麼」（資源/功能）做「什麼事」（操作）的制度化控管。其目的是防止未授權行為、降低資料外洩風險，並支持業務流程的正確運作。良好設計需在精確度（符合實際需求、不多給也不少給）與管理成本（規則可維護、可擴展）間取得平衡，常見作法有 RBAC、PBAC、ABAC、ACL、Claims 等。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q9, B-Q5

A-Q2: 為何權限管理應視為商業需求而非純技術需求？
- A簡: 因為它直接映射職務職責與決策風險，須服務業務流程與治理。
- A詳: 權限管理的邊界、粒度與審核流程，取決於職務職責、合規要求與風險承擔。角色與權限的設計應由產品與業務決策導引，工程只負責實作。若將其當作純技術問題交給使用者隨意配置，容易造成「權限泛濫」、風險升高與維運混亂，背離企業治理與最小授權原則。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q10, B-Q5

A-Q3: 認證（Authentication）與授權（Authorization）有何差異？
- A簡: 認證回答「你是誰」，授權回答「你能做什麼」；先認證後授權。
- A詳: 認證是確認主體身份的過程，常見憑證為帳密、OAuth/JWT、憑證。授權是在已可信的身份下，基於規則判斷其是否可執行特定行為。技術上常由 IIdentity/IPrincipal 承載身份與角色，授權則據此檢查權限。正確順序為先認證，再依授權政策判斷並執行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, A-Q15

A-Q4: 什麼是 RBAC（角色為基礎的存取控制）？
- A簡: 以角色承載權限，再將角色指派給使用者的授權模型。
- A詳: RBAC 用 Role 聚合 Permission，將 Role 指派給 Subject（使用者），以此間接賦予權限。核心關聯為 SA（Subject Assignment）與 PA（Permission Assignment）。RBAC 擅長映射組織職務，規則清晰、維護成本低，適合大多數企業應用。可延伸角色階層與多角色組合，以提升表達力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, A-Q6, A-Q13

A-Q5: RBAC 常用名詞 S/R/P/SE/SA/PA 是什麼？
- A簡: S 主體、R 角色、P 權限、SE 工作階段、SA 主體-角色指派、PA 角色-權限指派。
- A詳: S（Subject）是人或代理程式；R（Role）代表職務與權限等級；P（Permission）是對資源操作的准許；SE（Session）是當前登入上下文；SA（Subject Assignment）為使用者—角色的指派；PA（Permission Assignment）為角色—權限的指派。整體形成可審核的授權關係網。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q5, A-Q17

A-Q6: 角色（Role）與群組（Group）有何差異？
- A簡: 角色承載授權語意，群組多為分類；指派角色即意味授權。
- A詳: 角色與權限綁定，代表可執行哪些操作；加入角色即獲權限。群組通常僅為人員分類或目標對象管理，非必然承載權限語意。混用將導致「隱性授權」，讓管理與審計混亂。設計上應以角色映射職務職責，以群組處理通訊或目錄編組。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q9, D-Q8

A-Q7: 什麼是 Operation？為何引入 Operation 層？
- A簡: Operation 是對使用者曝光的功能單元；需對應多個 Permission。
- A詳: Operation 表示「能做的功能」，如報表、批次匯入、流程節點操作。它通常由多個 Permission 組合而成（如 CRUD+Query）。引入 Operation 層，可把「開發呈現的功能」與「底層權限原子」解耦，提高可維護性與測試性，也利於審計與 UI 控制顯示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q4, C-Q5

A-Q8: 為何不建議自行土炮安全機制？
- A簡: 安全細節繁雜且高風險，成熟方案更可靠；土炮易出漏洞。
- A詳: 認證、授權、Token、安全存放、時效、重放攻擊、審計等涉及大量細節。自行實作常忽略邊界與風險案例，易導致繞權、越權與資訊外洩。應優先採用成熟框架（如 ASP.NET Core AuthN/Z、業界 IdP），在其上擴充策略與規則，降低攻擊面與維護成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q1, D-Q10

A-Q9: 權限精確度與管理困難度如何取捨？
- A簡: 精細度高更精確但難管理；抽象化降低成本但需防精確度下滑。
- A詳: 逐人逐功能的 20×50 矩陣可達高精確，但管理 1000 組合困難；用 3 角色×5 功能降至 15 組合更易維護。需評估風險與變動頻率，選擇合適抽象層（Role、Permission、Operation），兼顧最小授權與調整成本，並以測試與審計確保精確度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, A-Q13

A-Q10: 為何角色應在設計階段定義，而非任意新增？
- A簡: 角色承載職務語意與風險邊界，屬產品規格，避免運行時氾濫。
- A詳: 角色映射業務流程與合規責任，應由產品/治理決策定義並審核。允許隨意新增易造成「角色蔓延」與規則衝突，導致最小授權破功。建議將角色清單與其 PA 視為憲法級規格，僅開放 SA（指派角色給人員）供日常運維。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q5, D-Q8

A-Q11: 從 Windows 內建角色可學到什麼？
- A簡: 產品在出廠時即定義好角色與行為邊界，使用者只做指派。
- A詳: Windows 預設 Users/Power Users/Administrators，並可延伸至 Domain 角色，充分示範「設計期定義角色與權限」。多數情境僅需正確指派即可滿足需求；進一步調整存在，但屬進階管理。此範式可作為企業應用 RBAC 的設計參考。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q5, D-Q6

A-Q12: 為何常以 CRUD/Query 定義 Permission？與狀態轉移法差異？
- A簡: CRUD/Query直覺且易落實；狀態轉移更貼業務但分析較重。
- A詳: 以實體為中心的 CRUD/Query 權限簡潔、可快速覆蓋大多數操作。若業務受狀態機制強約束（如審批流），以「狀態轉移」定義 Permission 更精準，如允許特定角色執行某條轉移。兩者可混用：核心流程用狀態轉移，輔助操作用 CRUD。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q6, D-Q4

A-Q13: Permission Assignment 與 Operation Assignment 差異？
- A簡: 前者定義角色擁有哪些權限；後者定義功能需要哪些權限。
- A詳: Permission Assignment（PA）描述 Role→Permission 的授予；Operation Assignment（OA，常未命名）描述 Operation→需要的 Permission 列表。兩表相乘可推導某使用者對某功能是否被允許。將 PA、OA分離能清晰對齊「業務職責」與「功能需求」兩條維度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q4, C-Q5

A-Q14: 為何通常只需把 SA（使用者→角色）存入資料庫？
- A簡: PA與OA屬設計期規格，穩定可寫入程式或設定；SA需動態管理。
- A詳: 使用者與角色的指派經常變動，需可查詢、審計與調整，因此適合存 DB。相對地，角色擁有的權限（PA）與功能需求（OA）應穩定、由設計決策產生，存程式碼或設定可簡化維運、避免違規更改。如需動態化，需加嚴變更流程與審核。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, D-Q8

A-Q15: .NET 的 IIdentity 與 IPrincipal 各代表什麼？
- A簡: IIdentity 表身份與認證狀態；IPrincipal 連結身份並可查角色。
- A詳: IIdentity 暴露 Name、AuthenticationType、IsAuthenticated；IPrincipal 暴露 Identity 與 IsInRole(role)。在 ASP.NET 中，認證中介軟體會建構 ClaimsPrincipal（IPrincipal 實作），並放入 HttpContext.User 供後續授權檢查與業務邏輯使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, C-Q2

A-Q16: ASP.NET 的 [Authorize] 做了什麼？
- A簡: 於動作執行前，據 HttpContext.User 比對角色/策略，允許或拒絕。
- A詳: [Authorize] 屬性在 MVC/Minimal API 管線中先行執行，讀取 HttpContext.User（IPrincipal/ClaimsPrincipal），依標註的 Roles/Policy/AuthenticationSchemes 進行授權檢查；不符則回應 401/403。透過此宣告式保護，將安全關切前移且集中。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q1, D-Q1

A-Q17: Session 在認證/授權中扮演何角色？
- A簡: 承載認證結果與使用者上下文，於存取時提供授權必要輸入。
- A詳: Session（或等價的 JWT/票證）保存已驗證的身份與授權相關資訊（如角色、租戶、到期時間）。授權決策依賴此上下文避免每次重查資料庫。Session 管理需處理時效、續存、撤銷與更新，使角色變更能及時生效且不造成安全窗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, D-Q3, C-Q10

A-Q18: 為何「批次匯入」可能成為權限漏洞？
- A簡: 若其內隱含建立/修改能力，可能繞過對單筆操作的限制。
- A詳: 批次功能常整合多種底層動作（如查詢、建立、更新）。若僅限制單筆建立而未限制批次匯入，基層角色可能以單筆內容檔案繞開規範。解法是將 Operation 正確拆權，明確標記批次匯入所需 Permission，並只授予到合適角色（如管理者）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q8, D-Q4


### Q&A 類別 B: 技術原理類

B-Q1: IIdentity/IPrincipal 在執行時如何運作？
- A簡: 登入建立 Identity/Principal，後續以 IsInRole 等進行授權判斷。
- A詳: 登入時，系統驗證憑證並建立 IIdentity（含名稱、認證型別、已認證），封裝於 IPrincipal（常為 ClaimsPrincipal）。主線程或 HttpContext 上保存該 Principal；應用程式在控制器或服務中呼叫 IsInRole/讀取 Claims 以決定是否允許操作，形成標準 AuthN→AuthZ 流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q15, C-Q2

B-Q2: ASP.NET Core 認證/授權管線的機制？
- A簡: 認證中介軟體產生 User；授權中介軟體據策略/角色評估後放行。
- A詳: 認證中介軟體（AuthenticationMiddleware）驗證 Cookie/JWT 等，建構 ClaimsPrincipal 放入 HttpContext.User。授權中介軟體（AuthorizationMiddleware）在每次請求根據政策或 [Authorize] 標註評估存取權。結果不符時回 401/403，否則進入後續端點執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q1, D-Q1

B-Q3: 屬性式（Attribute-based）授權的原理是什麼？
- A簡: 以宣告式標註角色/政策，於端點執行前攔截並作出決策。
- A詳: 控制器或端點以 [Authorize(Roles="...")] 或 [Authorize(Policy="...")] 宣告要求。框架在呼叫目標方法前解析要求，從 HttpContext.User 比對角色、聲明與自訂處理常式（IAuthorizationHandler），以決定允許與否。它將安全邏輯前置並集中管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q1, D-Q6

B-Q4: 抽象化授權機制（ICustom*）如何設計？
- A簡: 以 Operation 要求的 Permission 清單，搭配 Authorization 服務統一判定。
- A詳: 定義 ICustomPermission（可檢查 IsGranted）、ICustomOperation（列舉 RequiredPermissions）、ICustomAuthorization（匯總判定）。流程：取得 User（IPrincipal）→決定當前 Operation→比對所需 Permission→整體允許/拒絕。此分層降低耦合並提升可測試性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q13, C-Q4

B-Q5: RBAC 的資料關聯如何表達（SA/PA 與 Operation）？
- A簡: SA 存使用者-角色；PA 存角色-權限；Operation 需權限集合。
- A詳: 將「誰擁有何角色」（SA）存入 DB；「角色擁有哪些權限」（PA）與「功能需哪些權限」（OA）由設計期決定並固化於程式/設定。判斷流程：User→Roles（SA）→Permissions（PA）↔Operation 所需→綜合允許。此法兼顧性能與治理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q5, D-Q5

B-Q6: 何時把 PA/OA 寫在程式或設定，何時放資料庫？
- A簡: 穩定規格寫程式/設定；需動態調整與審核者才放資料庫。
- A詳: PA/OA 屬產品規格，變更頻率低，寫在程式或設定可降低查詢成本與錯誤面。若組織要求運行時調整（如合約化授權），需嚴格審批、版本化、審計與快取失效策略，否則將引入複雜度與風險。SA 一般必須在 DB 持久化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q8, C-Q5

B-Q7: 如何用「乘法 vs 加法」思維優化授權複雜度？
- A簡: 拆分維度，把多組合的乘法空間改為可快取的加法查詢。
- A詳: 逐人×逐功能×逐客戶×多可能性帶來龐大組合。以 Session 聚合使用者上下文、以 Module 聚合同批功能需求，將每次判斷轉為「一次查詢，多次使用」。同時透過 Role 將人×權限關係降維，降低查詢頻率並利於快取與預運算。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, A-Q9, B-Q8

B-Q8: 模組化權限查詢與快取如何運作？
- A簡: 以（SessionCtx, ModuleCtx）取得整組許可，快取結果減少重複判斷。
- A詳: 將功能分群為模組（如訂單維護模組），一次回傳模組內各操作的允許/拒絕集合。快取鍵可用 SessionId+ModuleId，有效期與 Session 同步。此法將多次細粒度判斷合併為一次，顯著降低延遲與資料存取次數。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q10, D-Q5

B-Q9: 角色階層與組織單位（OU）如何融入 RBAC？
- A簡: 以角色繼承與部門/職稱關聯，提升可表達性與管理便利。
- A詳: 角色可具階層，如 Manager 繼承 Operator 權限。亦可將角色與組織 OU/職稱對齊，支援自動指派。需注意避免過度複雜與繼承鑽孔；變更需審計。實作上在解析 User→Roles 時展開繼承鏈，並應用租戶/部門等屬性過濾。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, D-Q7, C-Q3

B-Q10: Permission 的最小粒度如何決定？
- A簡: 以風險邊界與變更頻率為依據，兼顧可測試與可組合性。
- A詳: 粒度過細導致管理爆炸；過粗不能精準控管。以業務風險（資料外洩、造假）與演進需要（變更多）衡量，優先把高風險操作獨立為 Permission；常態操作用 CRUD/Query；流程核心用狀態轉移。維持可組合、可審計、易測試的平衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q6, D-Q6

B-Q11: 為何 TDD/單元測試適合驗證授權設計？
- A簡: 能以案例覆蓋角色×功能矩陣，提前發現越權與缺權。
- A詳: 將關鍵情境寫為測試：給定使用者角色集合與目標 Operation，期望 Allow/Deny。測試集可直接對齊 PA/OA 規格，變更時快速回歸，防止回歸缺陷與規則漂移。授權屬高風險領域，測試能顯著提升信心與合規證據。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, A-Q13, D-Q6

B-Q12: Claims 與 Roles 的關係是什麼？
- A簡: Role 常以 Claim 表達；Claims 攜帶更廣泛屬性供策略化授權。
- A詳: 在現代 IdP/JWT 模式下，Role 常以「role」或「roles」Claim 傳遞。除角色外，Claims 還可攜帶租戶、部門、職稱等屬性，支援策略化授權（PBAC/ABAC）。在 ASP.NET Core 中，ClaimsPrincipal 統一承載，授權處理可同時比對角色與自訂 Claims。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q3, D-Q7


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 ASP.NET Core 以 [Authorize(Roles="manager")] 限制功能？
- A簡: 啟用認證後以 Authorize 標註端點角色，未符即回 401/403。
- A詳: 
  - 實作步驟: 
    1) 設定 Authentication/Cookie 或 JWT。2) 在 Program/Startup 加 AddAuthorization。3) 於控制器/端點標註 [Authorize(Roles="manager")]. 
  - 程式碼: 
    services.AddAuthentication(...).AddCookie();
    services.AddAuthorization();
    [Authorize(Roles="manager")] public IActionResult Sales_Report(){...}
  - 注意: 角色名稱一致性（大小寫/來源），匿名端點需 [AllowAnonymous]，測試登入流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q2, D-Q1

C-Q2: 如何用 IPrincipal.IsInRole() 於程式內進行授權判斷？
- A簡: 由 Thread.CurrentPrincipal 或 HttpContext.User 取使用者再判斷角色。
- A詳: 
  - 步驟: 1) 登入成功建立 ClaimsPrincipal。2) 設置 Thread.CurrentPrincipal（Console）或使用 HttpContext.User（Web）。3) 在關鍵邏輯 if (user.IsInRole("manager")) 決定行為。
  - 程式碼:
    var user = Thread.CurrentPrincipal; if(user.IsInRole("manager")){...}
  - 注意: 測試需設置模擬 Principal；避免邏輯分散，建議封裝於服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q1, D-Q2

C-Q3: 如何設計並載入 SA（User→Role）資料表到 ClaimsPrincipal？
- A簡: 建表 user, role, user_role；登入時讀取角色轉成 role Claims。
- A詳: 
  - 步驟: 建表 users(id, name, …), roles(id, name), user_roles(user_id, role_id)。 
    登入驗證帳密→查 user_roles→將角色以 Claim(ClaimTypes.Role, roleName) 加入 ClaimsIdentity。 
  - 程式碼片段: new ClaimsIdentity(claims, "cookie"); claims.Add(new Claim(ClaimTypes.Role,"manager"));
  - 注意: 角色同步/大小寫一致、快取與失效策略、審計指派變更。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q12, D-Q3

C-Q4: 如何實作 ICustomPermission/Operation 與 AuthorizationService？
- A簡: 定義 Permission 檢查介面與 Operation 需求，集中由服務判斷。
- A詳: 
  - 步驟: 定義 ICustomPermission{bool IsGranted(IPrincipal)}；ICustomOperation{IEnumerable<Permission>}；AuthorizationService.IsAuthorized(user, op)→all op.RequiredPermissions.All(p=>p.IsGranted(user))。
  - 程式碼: bool IsAuthorized(IPrincipal u, ICustomOperation o)=>o.RequiredPermissions.All(p=>p.IsGranted(u));
  - 注意: Permission 實作可讀取 user.Roles；封裝於 DI 容器；撰寫單元測試覆蓋主要情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q7, C-Q7

C-Q5: 如何將 PA/OA 對應寫在程式或設定檔？
- A簡: 以常數或設定映射 Role→Permissions、Operation→Permissions。
- A詳: 
  - 步驟: 定義字典：rolePermissions = { "manager":[orders.query], "operator":[order.crud] }；operationRequirements = {"Sales_Report":[orders.query], "Orders_Create":[order.create, order.read, order.update]}。
  - 程式碼: var can = operationRequirements[op].All(p=>rolePermissions[userRole].Contains(p));
  - 注意: 保持不可變、版本化設定、變更需通過審核與自動化測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q6, D-Q6

C-Q6: 如何用 CRUD/Query 定義訂單系統的 Permission 並套用多個 Operation？
- A簡: 定義 order.create/read/update/delete、orders.query，按需組合到功能。
- A詳: 
  - 步驟: 建立 5 個 Permission；為 Sales_Report 指定 orders.query；Orders_Process 指定 order.read/update；Orders_BatchImport 指定 orders.query+order.create/update。
  - 程式碼: op["Orders_Process"].Req = [OrderRead, OrderUpdate];
  - 注意: 避免批次匯入內隱繞權；核心高風險動作獨立權限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q18, D-Q4

C-Q7: 如何撰寫授權單元測試（TDD）？
- A簡: 以多案例覆蓋角色×功能，斷言 Allow/Deny 與規格一致。
- A詳: 
  - 步驟: 1) 準備模擬 User（含角色）。2) 準備 Operation（含必需權限）。3) 呼叫 AuthorizationService.IsAuthorized。4) 斷言期望。 
  - 程式碼: Assert.True(auth.IsAuthorized(manager, Sales_Report)); Assert.False(auth.IsAuthorized(operator, Sales_Report));
  - 注意: 覆蓋高風險功能與邊界情境；加入回歸套件並在 CI 執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q4, D-Q6

C-Q8: 如何設計批次匯入避免繞過權限？
- A簡: 將批次匯入單獨成 Operation，需求明確權限並限縮授權對象。
- A詳: 
  - 步驟: 定義 Operation: Orders_BatchImport；RequiredPermissions=[orders.query, order.create, order.update]；在 PA 僅授予 manager。 
  - 程式碼: [Authorize(Roles="manager")] public IActionResult BatchImport(){...}
  - 注意: 檔案大小/筆數限制、風險審核、審計紀錄與事前預檢（dry run）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q4, C-Q6

C-Q9: 如何加上授權稽核（Audit Log）？
- A簡: 於授權決策點記錄使用者、功能、結果與理由，支援追溯。
- A詳: 
  - 步驟: 在 AuthorizationService.IsAuthorized 中記錄 userId、roles、operation、requiredPermissions、decision、timestamp、requestId。 
  - 程式碼: logger.LogInformation("auth {u} {op} {dec}", uid, op, allow);
  - 注意: 避免敏感資訊洩漏、設置保留策略與查詢索引，結合異常告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, B-Q5, A-Q8

C-Q10: 如何用快取優化權限檢查？
- A簡: 快取（sessionId, moduleId）→permission_sets，降低重複計算/查詢。
- A詳: 
  - 實作: 設計 CheckModulePermission(sessionCtx, moduleCtx) 回傳整組結果，快取於 Memory/Distributed Cache，失效與 Session 同步。 
  - 程式碼: cache.GetOrCreate(key, _=>ComputeModulePerms(...));
  - 注意: 權限變更時的快取失效、租戶隔離、避免過期帶來的越權窗口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q5


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 403/未授權但應該有權限怎麼辦？
- A簡: 檢查認證狀態、角色載入、角色名對齊與 [Authorize] 設定。
- A詳: 
  - 症狀: 已登入卻被 403/401 拒絕。
  - 可能原因: 未通過認證、角色未載入為 Role Claim、角色大小寫/名稱不一致、策略名稱誤用、Schemes 錯誤。
  - 解法: 確認 HttpContext.User.Identity.IsAuthenticated、檢視 Claims、比對設定與代碼、開啟授權日誌。
  - 預防: 登入流程測試、角色常數化、端到端自動化測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, C-Q1, C-Q3

D-Q2: User.IsInRole() 總是回傳 false？
- A簡: 多因未使用 Role Claim、類型映射錯誤或主體未設置。
- A詳: 
  - 症狀: 即使有角色也判斷失敗。
  - 原因: 角色未存為 ClaimTypes.Role、角色提供者未設定、Thread.CurrentPrincipal 未設、Cookie 設定不正確。
  - 解法: 確認 ClaimsBuilding 使用 Role Claim、配置 RoleClaimType、於測試中手動設置 Principal。
  - 預防: 統一角色建立流程與測試覆蓋。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q1, C-Q3

D-Q3: 角色變更不生效（仍沿用舊權限）怎麼處理？
- A簡: 問題在 Session/JWT 未更新；需強制重新簽發或撤銷。
- A詳: 
  - 症狀: 調整 SA 後，使用者仍舊權限。
  - 原因: Session/JWT 快取舊角色；缺乏撤銷機制。
  - 解法: 設計「版本號」或「安全印章」檢查；角色變更時標記失效並要求重新登入。
  - 預防: 制定變更策略、縮短高敏感用戶的 Token TTL、實作黑名單/回收清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q10, B-Q2

D-Q4: 批次匯入被濫用繞過建立限制怎麼辦？
- A簡: 將批次匯入獨立權限，只授權管理者；加上風險控制。
- A詳: 
  - 症狀: 基層以單筆檔案批次匯入新增訂單。
  - 原因: 未將批次匯入獨立為 Operation 與獨立 Permission。
  - 解法: 拆權（orders.query + order.create/update）、限定角色、審核與配額限制。
  - 預防: 在設計期以 OA/PA 模型檢查、測試覆蓋繞權情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q8, A-Q13

D-Q5: 授權查詢導致效能不佳如何優化？
- A簡: 模組化查詢、Session/Module 快取、降頻資料庫往返。
- A詳: 
  - 症狀: 高頻授權判斷引發延遲。
  - 原因: 每次逐筆查詢 SA/PA/OA。
  - 解法: 以 CheckModulePermission 聚合查詢、記憶化結果、將 PA/OA 固化於程式/設定。
  - 預防: 設計期降維、引入快取與快取失效策略、監控命中率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, C-Q10

D-Q6: 操作員誤得全域報表權限如何修補？
- A簡: 調整 PA/OA 拆權，移除高風險權限並補測用例。
- A詳: 
  - 症狀: Operator 可看 Sales_Report。
  - 原因: OA 錯把 orders.query 給所有角色或 PA 過度授權。
  - 解法: 限定 orders.query 僅給 manager；修正 OA；回歸測試。
  - 預防: 高風險權限專屬角色、審計變更、需求評審含安全檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q6, B-Q11

D-Q7: 多租戶環境出現跨租資料外洩如何診斷？
- A簡: 強化租戶屬性過濾，導入 ABAC/Claims，從查詢層防護。
- A詳: 
  - 症狀: 使用者看到他租資料。
  - 原因: 缺少租戶過濾或僅用角色控制未考慮屬性。
  - 解法: 在 Claims 中帶 tenantId；查詢層強制 where tenantId = user.tenantId；策略加租戶驗證。
  - 預防: 預置租戶攔截器、資料庫層 Row-Level Security、合規測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q12, B-Q9, C-Q3

D-Q8: RBAC 過度彈性導致「角色蔓延」怎麼處理？
- A簡: 回歸設計期治理，鎖定 PA/OA，僅允許 SA 調整。
- A詳: 
  - 症狀: 客戶自行增改角色/權限致安全失控。
  - 原因: 將產品規格交給運行時自由變動。
  - 解法: 將 PA/OA 固化；變更走審批；角色目錄治理；落地最小授權。
  - 預防: 設計憲法化、版本化管控、審計與報表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q6, A-Q6

D-Q9: 單元測試偶發失敗因 Principal 未設定？
- A簡: 測試前設置 Thread.CurrentPrincipal 或注入模擬 User。
- A詳: 
  - 症狀: 本地通過、CI 偶發失敗。
  - 原因: 測試環境未設置 IPrincipal；測試彼此汙染。
  - 解法: 測試前 new ClaimsPrincipal 並賦值；或以 DI 注入 ICurrentUser 抽象。
  - 預防: 測試隔離、基底測試類統一設置、移除對靜態環境依賴。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q7, B-Q11

D-Q10: 從土炮 ACL 轉 RBAC 的遷移步驟？
- A簡: 盤點操作→萃取 Permission→設計 Role/PA/OA→分階段切換。
- A詳: 
  - 症狀: ACL 複雜、難維護。
  - 解法: 1) 盤點功能與風險。2) 定義 Permission（CRUD/狀態轉移）。3) 設計 Role 與 PA。4) 映射 Operation 與 OA。5) 撰寫測試。6) 以影子模式比對結果。7) 逐租戶/模組切換。 
  - 預防: 版本化與回滾策略、審計到位。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q5, C-Q5


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是「權限管理」？
    - A-Q2: 為何權限管理應視為商業需求而非純技術需求？
    - A-Q3: 認證與授權的差異？
    - A-Q4: 什麼是 RBAC？
    - A-Q5: RBAC 常用名詞 S/R/P/SE/SA/PA 是什麼？
    - A-Q6: 角色與群組的差異？
    - A-Q11: 從 Windows 內建角色可學到什麼？
    - A-Q15: .NET 的 IIdentity 與 IPrincipal 各代表什麼？
    - A-Q16: ASP.NET 的 [Authorize] 做了什麼？
    - C-Q1: 在 ASP.NET Core 以 [Authorize] 限制功能
    - C-Q2: 使用 IPrincipal.IsInRole 檢查角色
    - D-Q1: 403/未授權但應該有權限怎麼辦？
    - D-Q2: User.IsInRole 總是回傳 false？
    - A-Q9: 精確度與管理困難度如何取捨？
    - B-Q1: IIdentity/IPrincipal 如何運作？

- 中級者：建議學習哪 20 題
    - A-Q7: 什麼是 Operation？為何引入？
    - A-Q12: CRUD/Query 與狀態轉移法差異
    - A-Q13: PA 與 OA 的差異
    - A-Q14: 為何只需把 SA 存 DB？
    - A-Q17: Session 的角色
    - A-Q18: 批次匯入可能成為漏洞
    - B-Q2: ASP.NET Core 認證/授權管線
    - B-Q3: 屬性式授權原理
    - B-Q4: 抽象化授權機制（ICustom*）
    - B-Q5: RBAC 的資料關聯（SA/PA/OA）
    - B-Q6: 程式/設定 vs 資料庫的取捨
    - B-Q7: 乘法 vs 加法優化思維
    - B-Q8: 模組化權限與快取
    - B-Q11: 為何用 TDD 驗證授權
    - B-Q12: Claims 與 Roles 的關係
    - C-Q3: 載入 SA 至 ClaimsPrincipal
    - C-Q4: 實作 AuthorizationService
    - C-Q5: 將 PA/OA 寫在程式/設定
    - C-Q6: 以 CRUD/Query 套用多個 Operation
    - C-Q7: 撰寫授權單元測試

- 高級者：建議關注哪 15 題
    - B-Q9: 角色階層與 OU 融入 RBAC
    - B-Q10: Permission 的最小粒度決策
    - C-Q8: 設計批次匯入避免繞權
    - C-Q9: 加上授權稽核（Audit Log）
    - C-Q10: 使用快取優化權限檢查
    - D-Q3: 角色變更不生效的處理
    - D-Q4: 批次匯入濫用的修補
    - D-Q5: 授權查詢效能優化
    - D-Q6: 操作員誤得全域報表的修補
    - D-Q7: 多租戶跨租資料外洩診斷
    - D-Q8: 角色蔓延的治理
    - D-Q9: 單元測試 Principal 未設定
    - D-Q10: 從土炮 ACL 轉 RBAC 的遷移
    - A-Q10: 角色應在設計階段定義
    - A-Q8: 為何不建議土炮安全機制