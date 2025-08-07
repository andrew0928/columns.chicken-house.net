# 架構師觀點 - API Design Workshop

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼建議在 API 開發中採取「API/Contract First」而不是傳統的 Code First 流程？
API 的成敗有超過 70% 取決於規格本身的好壞。先確認 Contract 再動手實作，可帶來下列效益：  
1. 及早驗證「做的是否是對的事」，降低後期返工風險。  
2. 規格確定後，前端、後端、測試、技術寫手等角色可並行作業，加速交付。  
3. 可以用最少成本（Mock）先跑通關鍵情境，提早暴露設計問題。  
4. 後續只要遵守合約，效能、可靠度等實作層面的優化才真正「加分」，而非補救。

## Q: 物件導向（OOP）的概念在 REST API 中應如何對應與命名？
將一個 Class 視為一個 Resource：  
• 靜態行為（static method）→ 不含 instance id 的端點。  
• 物件行為（instance method）→ 需帶 instance id 的端點。  
對應範例規則：  
/api/{class-name}/[{instance-id}]:{method-name}  
例如：  
Man.Create() → POST /api/man:create  
Man.Get(id) → GET  /api/man/{id}  
m.Work()     → POST /api/man/{id}:work  
Method 的參數對應 Request Body / Query，回傳值對應 Response Body，如此即可把 OOP 的介面直譯成 REST API。

## Q: 在開始寫 API Spec 前，應先用有限狀態機 (FSM) 做哪些分析？
需先把「物件生命週期」完整盤點，包含：  
1. 狀態 (States) ：物件可能處於的每一種狀態。  
2. 會改變狀態的操作 (Operations with State Transition)。  
3. 不改變狀態的操作 (Read-only Operations)。  
4. 物件相關資訊 (Attributes／Properties)。  
5. 外界可能關注的事件 (Events)。  
完成 FSM 後，可依「狀態 × 行為 × 角色」產生：  
• API 端點與其約束（只能走合法轉移）。  
• 權限模型（哪些角色能呼叫哪些操作）。  
• 後續事件與 Webhook 需求。  
如此設計出的 API 更貼近實際業務流程，同時容易維護並具備擴充彈性。