---
layout: synthesis
title: "xxxxx 架構面試題 #6: 權限管理機制的設計"
synthesis_type: summary
source_post: /2024/05/01/permission-design/
redirect_from:
  - /2024/05/01/permission-design/summary/
---

# xxxxx 架構面試題 #6: 權限管理機制的設計

## 摘要提示
- 商業導向的權限觀: 先定義老闆期待與使用情境，再決定技術機制，衡量「精確度」與「管理難度」的取捨。
- 例子驅動設計: 以 B2B 訂單系統為例，從使用者/功能盤點，導出角色與權限的分層管理。
- 角色與權限模型: 使用者分類為「角色」，功能分類為「權限」，以組合降低複雜度（乘法→加法）。
- 認證與授權基礎: .NET 的 IIdentity/IPrincipal 分離「你是誰」與「你能做什麼」，AuthorizeAttribute 簡化檢查。
- 介面抽象化: 以 ICustomRole/Permission/Operation/Authorization 建立可驗證、可替換的授權模型。
- RBAC 核心觀念: 以 Role-Permission 的 PA 關係為核心，操作（Operation）由多個 Permission 組合而成。
- Role ≠ Group: Role 代表被授權的職能，設計時應對準業務流程，非任意由管理者新建。
- 訂單系統設計: 明確定義角色（主管/專員/系統管理）、權限（CRUD/Query）、操作（報表/輸入/批次）。
- 實作策略: 只將 User-Role 存 DB，其他對照可寫死於程式或設定；登入階段載入至 Session。
- 反模式警示: 過度彈性的「讓用戶任意改 R/P/PA」會破壞治理，權限規格應視為產品憲法。

## 全文重點
本文將「權限管理」視為商業需求的設計題而非單純技術題，先用 B2B 訂單系統說明決策者對不同身分（業務助理、主管、系統管理）之可見與可為的期待。作者以「結果導向」評估兩個面向：一是精確度（系統賦權是否與預期一致），二是管理難度（配置組合數量）。若逐人逐功能配置雖最精確，但管理成本爆炸；若以角色與權限抽象化，能顯著減複雜度，前提是角色與權限定義要貼合業務。

基礎上，認證（Authentication）回答「你是誰」，授權（Authorization）回答「你能做什麼」。.NET 的 IIdentity/IPrincipal 正好體現分工：IIdentity 暴露名稱、認證型別、是否認證；IPrincipal 暴露 IsInRole 檢查角色。Web 端可透過 AuthorizeAttribute 在 Controller/Action 層面做宣告式授權。為便於跨機制比較，作者定義 ICustomRole/Permission/Operation/Authorization 介面，並借用 RBAC 名詞集（Subject/Role/Permission/Session/SA/PA）建立模型：Operation 需若干 Permission 才能執行，Permission 與 Role 的 PA 關係是治理核心。

在 RBAC 章節，作者強調 Role 與 Group 的差異：Role 代表職能授權，應在產品設計期確立，非讓管理者任意新增。以訂單系統示例，定義角色（system-admin、sales-manager、sales-operator）、權限（order CRUD、orders-query），與操作（報表、輸入、處理、批次匯入）。以兩張表治理：Permission Assignment（Role↔Permission）與 Operation Assignment（Operation 需求哪些 Permission）。由此可推導 Role↔Operation 的「結果表」，以驗證是否有安全漏洞（如批次匯入意外賦予建立能力）。實作上僅 User-Role 關聯需存 DB 並於登入載入 Session；Role-Permission 與 Operation-Permission 的對照可內建於程式或設定，以降低查詢負擔與維運成本。作者提醒避免「過度彈性」的自定義權限畫面，否則治理失效。文末預告 PBAC、ABAC、Claim、ACL 與應用（審計、Session、API Scope、合約與功能旗標）將在後續延伸。

## 段落重點
### 0. 權限管理是在做什麼?
- 將權限管理視為商業需求：先用訂單系統案例闡述不同角色的可見/可為與風險控制（避免基層批次匯出、避免主管造假、避免系統管理閱覽業績）。  
- 以「結果表」評估設計：逐人逐功能（20×50）精準但難管理；以角色×功能類別（3×5）易管理但需審慎定義，否則犧牲精確度。  
- 導入 Role（使用者分類）與 Permission（功能分類）概念；將「精確度」與「管理難度」作為權限機制優劣的量化指標。  
- 強調本段不涉技術，專注在系統目的與評估基準，為後續機制比較奠基。

### 1. 權限基礎: 認證與授權
- 以 .NET IIdentity/IPrincipal 說明「你是誰」與「是否在某角色」，示範 Console 與 ASP.NET MVC/AuthorizeAttribute 用法。  
- 認證結果通常存在 Session（如 Cookie/JWT），框架於 Pipeline 自動還原為 HttpContext.User（IPrincipal）。  
- 授權檢查流程：登入成功→將 IPrincipal 放入 Thread/HttpContext→在功能點用 IsInRole 或 Authorize 斷言。  
- 核心主張：介面先行、實作後置，以相同模型比對各種授權機制；理解 interface 能讓你迅速看懂不同廠商解法。

### 抽象化授權機制
- 問題分兩面：前台「如何檢查」與後台「如何儲存/運作」。檢查需三要素：你是誰（Subject）、要做什麼（Operation/Permission）、權限設定（資料來源）。  
- 導入 RBAC 名詞與結構圖，定義 S/R/P/Session/SA/PA；將 Operation 視為對使用者呈現的功能，需若干 Permission 組合才可執行。  
- 自定義介面：ICustomRole、ICustomPermission（IsGranted）、ICustomOperation（RequiredPermissions）、ICustomAuthorization（IsAuthorized）。  
- 說明組織、階層、群組與 Session 的角色；預告將用此模型貫穿後續 PoC 與機制比較。

### 2. RBAC, Role based access control
- Role 是職能授權而非純分類；應在產品設計期定義並與流程/職務說明對齊，交付時只開放 User-Role 指派即可。  
- Windows 角色（Users/Power Users/Administrators、Domain Roles）為佳例：產品團隊預先內建角色與權能集合。  
- 訂單系統示例：  
  - 角色：system-admin（帳號/安全設定）、sales-manager（全域查詢/報表）、sales-operator（輸入/單筆維護）。  
  - 權限：order-create/read/update/delete、orders-query。  
  - 操作：Sales_Report、Sales_DailyReport、Orders_Create、Orders_Process、Orders_BatchImport…  
- 以 Permission Assignment 與 Operation Assignment 兩表治理，推導 Role↔Operation 結果表以驗證漏洞。  
- 實作上僅 User-Role 存 DB；其他對照寫入程式/設定，登入載入至 Session。提供 OrdersAuthorization 思路，強調減少 DB 查詢與維運成本。

### xxx 2. RBAC, Role based access control（重申與補充）
- 再次引用 RBAC 名詞集與關係圖，強化 R/P/PA 的語意與例子。  
- 以 Manager/Operator × CRUD/Query 的 PA 表展示賦權邏輯；操作（如主管報表）由多個 Permission 組合。  
- 提醒將必要檢查封裝進核心功能（如 Create 內部自行必要查詢），避免於應用層重複分散邏輯。  
- 強調反模式：提供使用者任意改 R/P/PA 會使治理失效；R/P/PA 應列為產品憲法，所有功能不得違背之。  
- Windows 再例證：預設角色與權能組合滿足多數需求，額外調整留給高權管理者。

### 3. PBAC
- 預告章節，未展開內容。可推知將以「策略」描述授權規則，適合更動態或跨多維條件的場景。

### 4. ABAC
- 預告章節，未展開內容。可推知將以「屬性」（主體/資源/環境）組合做判斷，解決細粒度與情境化需求。

### 5. Claim
- 預告章節，未展開內容。可推知將說明以 ClaimPrincipal 搭配 Token 之宣告式授權的實務。

### 6. ACL
- 預告章節，未展開內容。可推知將對比以資源為中心的存取控制名單做法與 RBAC 的差異。

### 6. 應用（審計/Session/API Scope/合約與功能旗標）
- 預告章節，未展開內容。將延伸到審計日誌、登入 Session 管理、API Scope、合約授權與 Feature Flag 的整合實務。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本資訊安全觀念：認證(Authentication)與授權(Authorization)的差異
- 軟體系統分析與抽象化能力：把需求拆成使用者/功能/規則三塊
- .NET 基礎（選用技術線）：IIdentity、IPrincipal、AuthorizeAttribute、Middleware/HttpContext/Session
- 資料建模入門：角色、權限、操作、指派關係的資料結構
- 基本 Web/後台系統開發常識：功能選單、按鈕、報表、API

2. 核心概念：本文的 3-5 個核心概念及其關係
- 認證 vs 授權：先確認你是誰(IIdentity)，再決定你能做什麼(IPrincipal.IsInRole + 授權規則)
- RBAC 基本模型：Subject-Role-Permission-Operation 及 SA/PA（使用者-角色指派、權限-角色指派）
- Permission 與 Operation 分離：Permission 為最小授權單位，Operation 為對使用者呈現的功能；Operation 需要一組 Permissions
- 管理複雜度 vs 精確度：以「乘法 vs 加法」思維減複雜度，規劃良好的 Role/Permission 可兼顧精確與可管控
- Session 與載體：登入後將 IPrincipal 置於 Session/HttpContext，降低授權查詢開銷

3. 技術依賴：相關技術之間的依賴關係
- 認證層：產出 IIdentity/IPrincipal（例如 Cookie/JWT 經由 Middleware 解析）
- 授權層：IPrincipal.IsInRole + 自訂 ICustomAuthorization/ICustomOperation/ICustomPermission 判斷流程
- 設定/資料層：User-Role 指派必須持久化（DB），Role-Permission/Operation-RequiredPermissions 多為設計期決定（程式碼或設定檔）
- 框架整合：ASP.NET MVC/Minimal API 以 AuthorizeAttribute/Policies 在管線中攔截
- 組織/階層擴展：Role Hierarchy、Group、OU/LDAP 可延伸（非必要）

4. 應用場景：適用於哪些實際場景？
- 企業後台/管理系統：銷售/訂單/客戶資料管理
- Web API/微服務：以角色或權限控管端點
- 桌面/作業系統級：Windows Users/Power Users/Administrators 典型 RBAC
- SaaS 多租戶後台：以角色模組化授權，降低運維成本
- 報表/批次功能：高風險操作需要嚴格角色/權限組合

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解認證與授權的差異與流程
- 在 .NET 用 IIdentity/IPrincipal 撰寫最小範例（Thread.CurrentPrincipal / HttpContext.User）
- 嘗試 AuthorizeAttribute 控制 Controller/Action
- 為一個功能定義 Permissions，手動在程式內檢查 RequiredPermissions

2. 進階者路徑：已有基礎如何深化？
- 設計 RBAC 模型：Subject/Role/Permission/Operation 與 SA/PA
- 完成 Operation-RequiredPermissions 與 Role-Permission 的兩張對映表，建立驗證矩陣
- 將 User-Role 指派持久化（DB），其餘對映以程式或設定檔維護
- 引入 Session/JWT 快取授權判斷，降低 DB 查詢頻率
- 研究 PBAC/ABAC 的差異與擴充點（儘管文中未展開）

3. 實戰路徑：如何應用到實際專案？
- 以業務流程定義角色（對準 Job Function/職責），避免「讓使用者自訂所有規則」
- 從主要實體(Entity)導出 Permission（CRUD + Query 或狀態轉移）
- 將 Operation 映射到 Permission 組合，產生 Role-Operation 的檢核結果表做需求驗收
- 登入時載入 User-Role（DB），放入 Session/Claims；授權在中介層/Filter 統一檢查
- 實作稽核（Audit Log）、Session 期限、敏感操作審批/雙人覆核等加值控制

### 關鍵要點清單
- 認證與授權分工：先確認身分(IIdentity)，再檢查能否執行(IPrincipal/授權規則)（優先級: 高）
- IIdentity/IPrincipal：.NET 內建介面，承載名稱、認證型態、是否已認證與角色查詢（優先級: 高）
- RBAC 核心元件：Subject、Role、Permission、Operation、SA、PA 的關係與流程（優先級: 高）
- Permission-Operation 分離：以最小授權單位組合出功能，降低規則數量與複雜度（優先級: 高）
- 兩張關聯表：Role-Permission（PA）與 Operation-RequiredPermissions（OA）是驗證與落地關鍵（優先級: 高）
- 管理複雜度 vs 精確度：用「乘法轉加法」的設計降低維護成本，同時維持足夠精確度（優先級: 中）
- 設計期決策優於執行期彈性：角色與權限應在產品設計期定案，避免把風險外包給使用者（優先級: 高）
- Session/Claims 載體：登入後載入使用者授權上下文，減少每次往返資料庫（優先級: 中）
- AuthorizeAttribute 實務：在 ASP.NET 中以宣告式方式攔截未授權請求（優先級: 中）
- Role vs Group：Role 代表授權語意，Group 僅為分類，混用會導致規則歪斜（優先級: 中）
- 以業務流程定義角色：對準職責(Job Function)設計角色，避免技術導向失真（優先級: 高）
- 由實體或狀態轉移導出 Permission：比單純 CRUD 更貼近業務風險控制（優先級: 中）
- 嚴慎對待高風險 Operation：如批次匯入/匯出需更嚴格權限組合與稽核（優先級: 高）
- 僅 User-Role 持久化：其餘對映優先以程式/設定檔維護，減輕 DB 初始化與維護（優先級: 中）
- 稽核與合規：對敏感操作與授權決策留存審計紀錄（優先級: 中）