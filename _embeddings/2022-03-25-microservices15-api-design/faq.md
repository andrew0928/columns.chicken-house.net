# 微服務架構 - 從狀態圖來驅動 API 的設計

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 想把糟糕的 API 改良，有沒有一套 SOP 或萬用準則可以直接照做？
沒有放諸四海皆準的 SOP。API 的優劣九成以上取決於「設計」，而設計必須建立在對 Domain 的深度理解與設計者本身的功力。各種 Guideline 只能確保產品「及格」，無法保證「理想」。

## Q: 什麼樣的 API 才算是「好」的 API？
作者認為關鍵在「一致性」。包含：
1. 命名、視角、主詞一致  
2. 背後邏輯一致，不同 API 不應有互斥規則  
3. 使用者在呼叫前即可預期行為，減少翻文件  
此外，他用三個層次檢視 API 品質：  
(1) 結構設計是否清晰 (狀態、領域知識、一致性)  
(2) 規格是否符合業界慣例 (REST/gRPC 等)  
(3) 服務本身是否穩定可靠 (效能、錯誤率、安全性)

## Q: 為什麼作者建議用有限狀態機 (FSM) 來驅動 API 設計？
FSM 可以同時把「狀態、動作、事件、授權」集中在同一張圖思考，設計階段就能檢查一致性、避免遺漏；之後又能直接對應到程式碼，降低設計與實作脫鉤的風險。

## Q: 只提供 CRUD 的「貧血模型」API 會產生哪些問題？
1. 服務邏輯被丟給外部組合，無法精準控管  
2. 難以保證副作用一致（事件多發/漏發）  
3. 權限、驗證、流程管控都散落在多處，易出錯  
因此作者主張把「動作」(如 Register、Activate…) 明確做成 API，並以 FSM 控制合法狀態轉移。

## Q: 作者推薦的 API 設計流程是什麼？
1. 列出所有「狀態」  
2. 列出「動作」並畫出 FSM  
3. 把 FSM 對應到程式碼（enum、Service、StateMachine）  
4. 列出「事件」並與狀態轉移或動作綁定  
5. 在動作上標示可執行的「角色」(RBAC/Scope)  
6. 驗證案例，確保各角色在 FSM 上都有通路可走，再補上不影響狀態的額外動作或 hooks

## Q: 如何在程式碼中落實 FSM 與權限檢查？
作者示範：
1. 用 enum 表示狀態  
2. 用 Dictionary 或查表/轉移清單實作 StateMachine  
3. Service 每個動作先呼叫 StateMachine.TryExecute 判定是否合法  
4. 成功後以 lock 或分散式鎖確保狀態原子轉移  
5. 透過 C# event 觸發對應事件  
6. 以 Attribute 或 Thread.CurrentPrincipal.IsInRole 檢查角色；若用 ASP.NET Core 可直接套 `[Authorize(Roles="…")]`

## Q: FSM 圖上還要標示哪些資訊？
除了「狀態」與「動作」的箭頭，還建議：
• 每條箭頭旁加「事件」符號，代表狀態轉移時要發的事件  
• 動作旁標示可執行的「角色」(USER、STAFF…) 以便日後對應 RBAC、OAuth2 Scope、API Gateway Products 等授權機制

## Q: 在會員範例中，最終確認下來的核心狀態、動作與事件有哪些？
狀態：START → CREATED → ACTIVATED → DEACTIVATED → ARCHIVED → END  
動作：Register、Import、Activate、Lock、UnLock、Remove  
狀態事件：MemberCreated、MemberActivated、MemberDeactivated、MemberArchived  
額外 hooks：RegisterCompleted、PasswordValidated(成功/失敗)

## Q: 如何快速驗證自己的設計是否合理？
把每個 User Story 畫成「地圖路徑」，沿 FSM 走一次：  
• 若走到一半就斷路，代表狀態或動作漏掉  
• 若同一路徑需不同角色卻沒檢查，也要修正  
這種紙上演練能在寫程式前就揪出大部分低級錯誤。

## Q: 作者對想精進 API 設計者的建議是什麼？
先掌握設計思路，再談技術工具。工具（鑿子）再好，沒有對 Domain、流程與結構的深度理解，也無法雕出高品質 API；把 FSM 當核心地圖，讓設計與實作隨時可對應、快速迭代，才是長久之道。