---
- source_file: /docs/_posts/2024/2024-05-01-permission-design.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# xxxxx 架構面試題 #6: 權限管理機制的設計 ── 文章摘要

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "xxxxx 架構面試題 #6: 權限管理機制的設計"
categories:
- "系列文章: 架構師的修練"
tags: ["系列文章", "架構師的修練", "架構師觀點", "刻意練習", "抽象化"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 

# 自動識別關鍵字
primary-keywords:
  - 權限管理
  - RBAC (Role-Based Access Control)
  - PBAC (Policy-Based Access Control)
  - ABAC (Attribute-Based Access Control)
  - IIdentity / IPrincipal
  - 授權 (Authorization)
  - 認證 (Authentication)
secondary-keywords:
  - Permission / Operation
  - Role / Group
  - Session / Cookie
  - Claims-Based Identity
  - ACL
  - Audit Log
  - .NET 8 Authorize Attribute
  - Windows 內建角色

# 技術堆疊分析
tech_stack:
  languages:
    - C#
  frameworks:
    - .NET 6 / 8
    - ASP.NET MVC / Minimal API
  tools:
    - Visual Studio / VS Code
  platforms:
    - Windows
  concepts:
    - Role & Permission Matrix
    - Secure by Design
    - Session Management
    - Policy Engine
    - Domain-Driven Design (DDD)

# 參考資源
references:
  internal_links: []
  external_links:
    - https://en.wikipedia.org/wiki/Role-based_access_control
    - https://learn.microsoft.com/aspnet/core/security/authorization/roles
    - https://github.com/microsoft/referencesource (IIdentity / IPrincipal)
  mentioned_tools:
    - JWT
    - Active Directory
    - SQL Server

# 內容特性
content_metrics:
  word_count: 9800   # 估算值
  reading_time: "30 ~ 40 分鐘"
  difficulty_level: "進階"
  content_type: "Architecture Interview Drill"
  last_generated: "2025-08-06 00:03"
  version: "1.0.0"
```

## 文章摘要
本文以「面試實戰題」的方式，帶領讀者系統化拆解「權限管理機制」的設計思路。作者首先強調「權限」是一種業務需求，而非純技術議題；若缺乏對商業流程的理解，任何再炫的技術實作都可能導致漏洞。文章以 B2B 銷售系統為例，闡述業務助理、業務主管、系統管理員三種角色對訂單資料的不同存取需求，進而引出「管理難度」與「精確度」兩大評估面向。  
接著作者回溯 .NET 自 1.1 版本即內建的 IIdentity 與 IPrincipal 兩個介面，說明它們如何天然支持認證與最基礎的角色查核。為了更高階的授權需求，文中定義了 ICustomRole、ICustomPermission、ICustomOperation 與 ICustomAuthorization，示範如何把「使用者—角色—權限—操作」四層模型抽象化。  
在 RBAC 章節，作者引用 Wiki 圖示說明 Subject、Role、Permission、Session 等名詞，並透過表格推導角色與權限的交叉矩陣，展示在程式碼層可如何「寫死」角色／權限映射以降低複雜度，並用 OrdersAuthorization PoC 佐證。  
文章後段預留 PBAC、ABAC、Claim 與 ACL 等進階章節，點出這些模型如何藉由「乘法→加法」的方式，把 1.5 兆種組合的授權判斷降到可維運的數量級，也提醒開發團隊應避免把所有彈性留到 Runtime，否則權限機制形同虛設。  
整篇以實務落點、程式碼片段與常見誤區貫穿，適合作為架構師面試對談、亦能指引團隊在 .NET 生態中落地安全設計。

## 關鍵要點
- 權限是商業需求，需先明確定義「好」的驗證標準：精確度 × 管理成本。  
- 認證（IIdentity）與授權（IPrincipal）可在 .NET 原生介面上自然銜接。  
- 「角色×權限」矩陣若於設計期定案，可大幅減少 DB 查詢與管理難度。  
- RBAC 易於理解且部署快速，但須嚴謹規劃 Role / Permission 以免越權。  
- PBAC / ABAC 透過政策或屬性把 n 維度問題拆為相加關係，專門解決大規模組合爆炸。  
- 過度「彈性」的管理介面常使客戶把所有權限全開，反而削弱安全性。  
- Session / Claim / Audit Log 等配套機制同樣是安全體系的一環。  
- 實作策略：先 PoC 小矩陣驗真，再抽象化介面，最後才接企業級服務（AD、OAuth、Policy Engine）。  

---

## 段落摘要（依主要 H2）

### 0. 權限管理是在做什麼?
作者以零售業務流程舉例，定義權限管理的衡量標準：管理難度＝要維護的設定組合數量；精確度＝實際行為與老闆期望之差距。透過 20×50 與 3×5 矩陣對比，說明「抽象分類」能顯著降低維運負擔。

### 1. 權限基礎：認證與授權
回顧 .NET IIdentity / IPrincipal 介面設計，說明 Name、IsAuthenticated、AuthenticationType 與 IsInRole 的實用性；並展示 Console 與 ASP.NET MVC 中 Thread.CurrentPrincipal 與 AuthorizeAttribute 的實戰流程。

### 抽象化授權機制
提出四大介面（ICustomRole／Permission／Operation／Authorization），將 Subject-Role-Permission-Operation 連結拆為可測試單元，並透過 DDD 與接口分離原則避免 Fat Service。

### 2. RBAC, Role-Based Access Control
深入解析 Wiki RBAC 圖，列舉 Windows 內建角色為例，強調 Role 設計應於開發期確定；提供訂單系統的 Role-Permission-Operation 表格及 OrdersAuthorization PoC，示範如何硬編碼映射以提升效能與可預測性。

### 3. PBAC（占位）
指出 PBAC 以政策規則為核心，能動態計算權限；後續將補充如何以 JSON Policy 或 OPA 實作。

### 4. ABAC（占位）
提及 ABAC 透過「使用者屬性＋環境屬性＋操作屬性」定義 access matrix，可解決多租戶與資料層級權限問題。

### 5. Claim（占位）
說明 Claims-Based Identity 在 JWT / SAML 中的角色，如何把複雜屬性封裝進 Token 降低查表壓力。

### 6. ACL（占位）
簡介 ACL 以資源為中心，常用於檔案系統與網路設備，適合靜態資源權限但不易應對高維度業務規則。

### 6. 應用
列舉 Audit Log、Login Session、API Scope、Feature Flag 等週邊議題，強調「Secure by Design」需貫穿整個開發生命週期。

---

## 問答集

1. Q: 為什麼作者主張「權限管理首先是商業需求」？  
   A: 因為權限目的在於保障商業流程與機密，而非滿足技術炫技；若未對齊商業目標，機制再複雜也可能讓不該看的資料外露或阻斷核心流程。

2. Q: IIdentity 與 IPrincipal 各負責什麼？  
   A: IIdentity 表示「我是誰」並保存認證狀態；IPrincipal 代表「我有哪些角色」，並透過 IsInRole 快速檢查授權。

3. Q: RBAC 的核心優缺點是什麼？  
   A: 優點是概念直覺、實作簡單、效能佳；缺點是角色爆炸或流程變動頻繁時，難以維護大量 Role / Permission 映射。

4. Q: 為何作者將 Role / Permission 映射「寫死」在程式碼？  
   A: 若映射在開發期已確定且 seldom 變動，硬編碼能降低 DB 負擔、避免 Runtime 誤設定，也迫使設計團隊在早期就釐清職責分界。

5. Q: PBAC 與 RBAC 的最大差異？  
   A: PBAC 以「政策條件」動態判斷權限，不必事先定義固定角色；RBAC 依賴靜態 Role-Permission 對照，維運成本隨角色數線性增長。

6. Q: 在 .NET Web API 如何快速啟用角色驗證？  
   A: 透過 `[Authorize(Roles="roleName")]` Attribute；框架會自動從 HttpContext.User 取出 IPrincipal 並呼叫 IsInRole 決定是否 403。

7. Q: 為何過度彈性的「自己定義角色」介面可能有風險？  
   A: 客戶常因方便而把所有權限打開，造成權限漂移；缺乏設計期的原則約束將使安全機制失效。

8. Q: ABAC 適用哪些場景？  
   A: 高維度、多租戶、資料等級細分（Row-Level Security）需求，如 SaaS 平台或政府系統，需要依屬性動態計算權限。

9. Q: Claim-Based 身分與 Session Cookie 有何差別？  
   A: Claims 將授權屬性直接打包進 Token，可於 stateless 環境快速驗證；Session 需伺服器儲存並維護狀態，延展性較差。

10. Q: 如何衡量「管理難度」與「精確度」？  
    A: 管理難度＝需維護的設定數；精確度＝實際授權行為 vs. 業務期望的一致度。理想機制能在兩者取得平衡。

---

## 問題與解決方案

Problem 1: 權限矩陣組合爆炸，維運困難  
Root Cause: 直接以「使用者 × 功能」儲存 1,000+ 組態  
Solution: 引入 RBAC，把 20×50 組態降成 3×5；在程式碼中硬編碼 Role-Permission 表，DB 僅保存 User-Role 指派  
Example: `OrdersAuthorization.IsAuthorized(user, operation)` 先比對角色，再映射 Permission

Problem 2: 工程師將權限彈性完全交給後台 UI，導致越權  
Root Cause: 缺乏設計期的商業規則，Runtime 隨意新增 Role / Permission  
Solution: 在需求評審即凍結角色清單；後台僅允許 User-Role 指派，不開放新增 Role  
Example: Windows 預設 Administrators/Users 即為固定腳色

Problem 3: 查詢密集功能導致授權查表頻繁  
Root Cause: 每次 Action 都赴 DB 查 Role/Permission  
Solution: 登入時將 Role 列表寫入 JWT/Session，授權層僅讀記憶體  
Example: 在 ASP.NET Middleware 解析 Cookie → ClaimsPrincipal → HttpContext.User

Problem 4: 大型 SaaS 需 Row-Level Security  
Root Cause: RBAC 無法細分到資料層  
Solution: 引入 ABAC，將 TenantId、OwnerId 等欄位作為屬性，於 LINQ/SQL 加條件過濾  
Example: `WHERE TenantId = @UserTenantId`

Problem 5: 權限異動無審計紀錄  
Root Cause: 缺 Audit Log Pipeline  
Solution: 在 Role/Permission 變更 API 寫入 Append-Only Log，並同步 SIEM  
Example: `INSERT INTO audit(access_change, operator, before, after, timestamp)`  

---

## 版本異動紀錄
- 1.0.0 (2025-08-06)  首次生成：完成 Metadata、段落摘要、10 組 Q&A、5 組問題-解決方案。