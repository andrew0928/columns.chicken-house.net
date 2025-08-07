# xxxxx 架構面試題 #6: 權限管理機制的設計

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 權限管理在系統中真正要解決的是什麼問題？
權限管理是為了滿足「商業期待」，也就是「讓對的人，在對的情境下，只能做該做的事，不能做不該做的事」。它透過規範「誰 (Subject)」「在什麼功能 (Operation)」上「擁有哪些許可 (Permission)」，來避免資料外洩、流程被破壞或決策被扭曲等風險。

## Q: 為什麼大部分情況下不建議自行從零實作安全／授權機制？
現成的安全服務和框架已歷經大量驗證與攻防，直接使用能降低邏輯漏洞及維運風險。自行土炮若對原理不熟，容易「安全沒顧好，還自己搞出漏洞」，導致整個系統最不安全的反而是安全機制本身。

## Q: 在示範的銷售系統案例中，如何衡量一套權限規劃的「好壞」？
1. 管理困難度：需要設定的「使用者 × 功能」組合越多，維護成本越高。  
2. 精確度：實際授權結果與老闆期望是否一致。理想狀態是 100% 精確且組合數最少。

## Q: 文章如何定義 Role 與 Permission？
• Role：以工作職能 (Job Function) 為基礎，代表「被授權執行某類任務」的身分。  
• Permission：對系統內某資源、某操作被核准的最小單位，例如「訂單-Create / Read / Update / Delete / Query」。

## Q: Role 與 Group 有何根本差異？
Role 帶有「授權」意涵，將 Role 指派給使用者就等同賦予其執行某些操作的權力；Group 只是分類，本身不代表任何權限，除非後續再綁定其他規則。

## Q: .NET 平台中，哪兩個介面提供了最基礎的認證與角色檢查能力？它們各自負責什麼？
• IIdentity：描述「我是誰」，包含 Name、IsAuthenticated、AuthenticationType。  
• IPrincipal：描述「我擁有哪些角色」，可透過 IsInRole(roleName) 檢查當前身分是否具備指定角色。

## Q: 若只需進行「使用者是否在角色內」的簡單檢查，基本流程是什麼？
1. 登入成功後，把 IPrincipal 放進 Thread.CurrentPrincipal 或 HttpContext.User。  
2. 在程式碼中取出目前使用者的 IPrincipal。  
3. 呼叫 IsInRole("roleName") 判定是否允許執行功能。

## Q: 一個完整的授權機制判斷「能否執行功能」最少需要哪些輸入？
1. 你是誰 (IPrincipal / Subject)。  
2. 你現在要做什麼 (Operation / 或欲執行的功能資訊)。  
3. 權限設定資料 (在何處儲存並供機制查詢的對應規則)。

## Q: RBAC 名詞 S、R、P 分別代表什麼？PA、SA 又是什麼？
S (Subject) = 使用者或代理程式  
R (Role) = 角色／職務  
P (Permission) = 存取資源的許可  
SA (Subject Assignment) = 使用者與角色的對應  
PA (Permission Assignment) = 角色與權限的對應

## Q: 為何 RBAC 中的角色應在系統設計階段就決定，而非讓管理者於執行期隨意新增？
角色若可在執行期任意增減，最終可能導致「每個角色什麼都能做」，權限管控形同虛設；設計階段先把角色與流程對齊，才能確保整體安全模型不被破壞。

## Q: RBAC 機制有哪些主要優點？
1. 結構簡單、直覺，易於溝通。  
2. 若規劃妥當，只需將「使用者-角色」對應存 DB，其餘對照可寫死或放設定檔，降低資料庫查詢負擔。  
3. 讓開發流程、產品功能無法輕易繞過預先定義的安全邊界。

## Q: 工程師常見的授權設計誤區是什麼？
過度追求「彈性」，提供 UI 讓客戶自行增刪 Role/Permission/PA。結果常演變成所有限制被拿掉；真正該做的是在服務設計階段就把安全規則定死，再提供「指派角色給使用者」這類受控操作給管理者。

## Q: ICustomAuthorization 模型中，Operation 與 Permission 的關係為何？
Operation 是最終呈現給使用者的一個功能，通常需要 0~n 個 Permission 才能執行；Operation 透過 RequiredPermissions 列舉其依賴的 Permission 清單，授權機制則檢查當前使用者是否取得這些 Permission 後決定 Allow / Deny。

## Q: 為什麼將 Permission 切得足夠小、Operation 做組合，能降低整體複雜度？
把大型乘法 (User × Function) 轉成較小的多項加法 (User × Role + Role × Permission + Permission × Operation) 可大幅減少需要維護的組合數，讓管理與快取優化更容易，同時維持授權的精確度。