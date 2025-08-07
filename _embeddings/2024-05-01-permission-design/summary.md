# xxxxx 架構面試題 #6: 權限管理機制的設計

## 摘要提示
- 商業導向: 權限管理的本質是滿足商業流程而非單純技術問題，衡量指標是「管理困難度」與「精確度」。
- 認證與授權: 先確認「你是誰」(IIdentity) 再決定「你能做什麼」(IPrincipal)，是一切安全機制的基石。
- .NET範例: Thread.CurrentPrincipal 與 AuthorizeAttribute 可輕鬆在 Console 或 ASP.NET MVC 中完成角色檢查。
- 抽象模型: 以 Subject、Role、Permission、Operation、Session 五要素封裝為介面，形成可擴充的授權框架。
- RBAC核心: 透過 Role-Permission 對應表 (PA) 把 乘法組合 轉成 加法管理，大幅降低設定量。
- 案例解析: 銷售訂單系統示範如何定義業助、主管、系管三角色與訂單 CRUD/Query 五權限。
- 設計原則: 角色與權限應在產品設計階段鎖定，避免讓使用者於執行期隨意增刪，導致安全機制失靈。
- 資料存放: 只有使用者與角色對應需進資料庫，其他靜態對照可寫死於程式或放在設定檔。
- 程式實踐: OrdersAuthorization 只需實作 IsAuthorized，即可依 RBAC 規則回覆 Allow/Deny。
- 後續比較: 文章後段將續談 PBAC、ABAC、ACL 等方案，說明何時該升級到更動態的策略模型。

## 全文重點
本文以「權限管理」為主題，先指出它是商業需求而非技術需求，衡量良窳的標準在於設定的複雜度與授權的精確度。作者以銷售訂單系統為例，說明若直接對 20 位使用者與 50 個功能做 1000 種配對，精確度雖高但難以維護；若先抽出三種角色與五類功能，則僅需管理 15 種組合即可兼顧彈性與效率。  
架構上必須先有「認證」再談「授權」。在 .NET 世界中，IIdentity 負責標識當前使用者並記錄認證方式；IPrincipal 則包裝多個角色並提供 IsInRole 方法，讓程式能快速判斷使用者是否具備某角色。作者示範了 Console App 與 ASP.NET MVC 兩種簡易做法，強調現成框架已將繁瑣細節隱藏。  
為了通用化，文章將 Subject、Role、Permission、Operation 以及 Session 抽象化成介面，並定義 ICustomAuthorization 只剩一個 IsAuthorized 方法。接著以 RBAC 為主要範型，解釋 Wiki 圖中的 S、R、P、PA 與 SA 概念，並重申「Role 代表已被授權的職責」不可與 Group 混用。  
在訂單系統案例中，業務主管需查詢業績且不得改動資料；業務助理需維護訂單但不應批次匯出；系統管理員僅可調整安全設定。根據這些需求可得到三角色、五權限，再由開發團隊把功能(Operations)與權限對映寫死於程式或設定檔，只把使用者與角色對應放進資料庫，登入時載入到 Session 中。此設計可保證流程正確性，同時讓管理界面簡潔。  
作者提醒，過度追求「彈性」導致讓管理者在執行期自由增刪角色或權限，往往使機制形同虛設；權限結構應在產品設計期即與商業流程一起確定。文章最後預告後續將比較 PBAC、ABAC、ACL 等更進階方案，並討論 Audit Log、Session 控制與 Feature Flag 等延伸議題。

## 段落重點
### 0. 權限管理是在做什麼?
作者將權限管理視為商業問題，透過銷售訂單系統例子說明「管理困難度」與「精確度」兩大評估指標；直接對人 × 功能做配置雖最精確卻難維運，透過角色與功能分群可大幅減少組合數。權限機制的好壞取決於是否在最小設定量下滿足業務需求且避免非預期行為。

### 1. 認證與授權基礎
闡述任何安全機制都先有認證再談授權，.NET 內建 IIdentity/IPrincipal 已提供穩健基礎；Console App 可透過 Thread.CurrentPrincipal 手動放入角色資訊，MVC 更能用 AuthorizeAttribute 自動檢查。作者示例程式碼詳細演示如何在不同層次攔截與核對角色。

### 抽象化授權機制
為了支援不同策略，作者把 Subject、Role、Permission、Operation、Authorization 五塊抽象為介面，並定義 ICustomAuthorization.IsAuthorized 來回答「某人能否執行某操作」。此模型可延伸至 RBAC、PBAC、ABAC 等實作，亦方便將資料庫、快取或設定檔做彈性替換。

### 2. RBAC：角色為基礎的權限控制
深入解析 RBAC 架構：Subject 綁定多個 Role，Role 再對映多個 Permission，系統再把多個 Permission 組合成 Operation。以訂單系統為例，定義業助、主管、系管三角色與訂單 CRUD/Query 五權限，並舉出兩張對照表(角色-權限、權限-功能)來驗證設計是否符合需求。實務上僅需在資料庫儲存 User-Role 關聯，其餘靜態關係可寫在程式；OrdersAuthorization 只要實作 IsAuthorized 就能完成 RBAC 檢查。作者強調角色與權限須在產品設計期定案，不可讓使用者於 Runtime 任意調整，以免破壞安全邊界。