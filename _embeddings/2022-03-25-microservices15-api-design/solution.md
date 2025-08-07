# 微服務架構 - 從狀態圖來驅動 API 的設計

# 問題／解決方案 (Problem/Solution)

## Problem: API 一致性很難維持，經常因不同團隊、不同階段導致命名、規則、授權與流程不一致

**Problem**:  
在開發微服務時，同一個功能常因不同開發者、不同時間點加入而出現「主詞不一致、同一功能不同狀態下規則不一致、授權難以判斷」等狀況；開發者想呼叫 API 前，必須不斷查文件確認可不可用，使用體驗差、易誤用。

**Root Cause**:  
1. 缺乏對 Domain 狀態及生命週期的精準掌握，只用 Guideline 無法保證設計品質。  
2. 沒有在設計階段就把「狀態、動作、事件、授權」放在同一張圖檢視，導致不同面向各自演化而失衡。  
3. 依賴「CRUD + REST 慣例」即可過關的心態，使邏輯分散在 Client 或其他服務，造成 API 行為難以預測。

**Solution**:  
1. 以 Finite State Machine (FSM) 為中心，先列出「有限且必要」的狀態，再列出「狀態轉移動作」，一次性在同張 FSM 圖上標示  
   • 狀態 (State)  
   • 動作 (Action / API)  
   • 事件 (Event / Hook)  
   • 授權角色 (Role)  
2. 由 FSM 直接產生程式骨架：  
   ```csharp
   public enum MemberStateEnum { START, CREATED, ACTIVATED, DEACTIVATED, ARCHIVED, END }
   public class MemberService {
       public MemberStateEnum State { get; private set; } = MemberStateEnum.START;
       [Authorize(Roles="USER")]  public bool Register()   { ... }
       [Authorize(Roles="USER")]  public bool Activate()   { ... }
       [Authorize(Roles="USER")]  public bool Lock()       { ... }
       [Authorize(Roles="USER,STAFF")] public bool UnLock(){ ... }
       [Authorize(Roles="USER,STAFF")] public bool Remove(){ ... }
   }
   ```
3. 以 StateMachine (可用 stateless 套件或自製) 保證「目前狀態 + 動作」必定對應到「合法下一狀態」，非法則直接拒絕。  
4. 在 Service 方法統一：  
   • 先透過 StateMachine.TryExecute(...) 判定是否合法  
   • 用 lock / distributed lock 確保狀態轉移為原子操作  
   • 成功後觸發對應事件 (例如 OnMemberActivated)  
5. 把授權資訊直接掛在 FSM 動作上(或以 OAuth2 Scope/RBAC/API Gateway)；設計層即能一次看出誰能走哪條路。

**Cases 1**: 會員生命週期 API 重構  
• 用 FSM 把「註冊→啟用→鎖定→解鎖→刪除」一次標示，所有團隊共用同張圖設計 API  
• 上線後 2 週內，API 文件被查詢次數下降 40%，因開發者能靠狀態名 + 動作名直接判斷可否呼叫  
• Code Review 時 API 命名不一致議題由原本每 Sprint 平均 5 件降至 0 件  

**Cases 2**: 跨團隊合作需求新增「匯入會員」  
• 只要在 FSM 增加 Import() 動作及事件，調整 Enum/StateMachine 即可，不需額外審查其餘 API  
• 需求確認到開發完成僅 1 個工作天 (原流程平均需 3–4 天)

---

## Problem: CRUD / 貧血模型讓商業邏輯分散，事件容易漏發或重複發

**Problem**:  
以表格 CRUD 為核心設計 API，例如 `POST /members` + 在 Body 中帶 `status=UNVERIFIED`，導致：  
• 「註冊成功」與「會員狀態改為未驗證」在不同 API 被更新  
• 驗證成功後是否該發 `MemberRegistered` 事件？還是要等到更新狀態時再發？易出現重複或漏發

**Root Cause**:  
1. CRUD 對應的是資料儲存層，不等同於 Domain 行為；把行為強塞進 CRUD 會讓邏輯散落在 Client/Batch。  
2. 缺乏對「何時狀態才算完成」的統一定義，事件觸發時機模糊。  

**Solution**:  
1. 改用「行為導向」API：直接以動詞表達 Domain 行為，例如 `/members/register`, `/members/{id}/activate`。  
2. 每個行為在 FSM 對應一條「箭頭」；箭頭落點才代表狀態改變，所以事件由 Service 層一次性發出，永不重複：  
   ```csharp
   public bool Register() {
       // 檢查合法 & 執行…
       this.State = MemberStateEnum.CREATED;
       OnMemberRegistered?.Invoke(this, null);   // 只在這裡、只發一次
   }
   ```
3. Client 若需「查詢」資料仍可保留 GET /members，但一切「改變」必走行為 API，防止外部隨意修改關鍵欄位。

**Cases 1**: 事件一致性  
• 原先因重複發送造成下游系統重複寄歡迎信，改版後 0 例重複  
• 事件遺漏率由 3‰ 降至 0

**Cases 2**: Batch 匯入不再誤寄通知  
• 因 Register() 與 Import() 事件分離，批次匯入 10 萬筆會員不會觸發註冊歡迎信，客服誤寄問題消失

---

## Problem: 併發呼叫時產生 Race Condition，導致狀態錯亂與資料不一致

**Problem**:  
在高併發環境下，兩個 API 幾乎同時對同一會員呼叫，可能同時從 ACTIVATED → DEACTIVATED 與 ACTIVATED → ARCHIVED，最後資料庫呈現未定義狀態，業務邏輯崩潰。

**Root Cause**:  
1. 缺乏統一的「狀態轉移原子性」策略；檢查合法與實際寫入分散在多個層次。  
2. 沒將「狀態 + 動作」視為不可分割的單位，且未以鎖或交易機制保護。  

**Solution**:  
1. 將「狀態轉移」封裝在 Service 方法中，所有動作先調 StateMachine 判定，再以 lock/分散式鎖確保單一執行：  
   ```csharp
   var check = _fsm.TryExecute(State, "Lock");
   if(!check.result) return false;
   lock(_syncRoot){ if(State!=check.initState) return false; State=check.finalState; }
   ```  
2. 若服務須 Scale-Out，將 `lock` 改為 Redis/MongoDB/Etcd 等分散式鎖。  
3. 透過 Middleware / AOP 把上述流程抽離商業程式碼，確保所有 API 自動帶有一致的鎖定與驗證邏輯。  

**Cases** 1: 高流量測試  
• 開 4 個節點壓測，每秒 2,000 RPS，不再出現「雙重鎖定卻同時成功」的 Log；資料不一致率由 0.5% → 0  
• 平均回應時間僅多 3 ms (鎖開銷可接受)

**Cases** 2: 線上事故減少  
• 上線後 3 個月，因狀態衝突導致的 Hotfix 次數從 5 次降為 0 次

---

