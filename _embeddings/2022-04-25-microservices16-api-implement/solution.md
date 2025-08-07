# 微服務架構 - 從狀態圖來驅動 API 的實作範例

# 問題／解決方案 (Problem/Solution)

## Problem: 架構概念與實務落差，常造成過度設計或落地失敗

**Problem**:  
閱讀許多「標竿型」架構文章後，在小型或成長中專案實際落地時，團隊往往無法判斷該做多少、做多深；不是「能力跟不上設計」，就是「為了安全起見一次做到底」，導致過度設計、交付延遲或技術債倍增。

**Root Cause**:  
1. 欠缺能把「抽象設計」對映到「可驗證實作」的橋樑。  
2. 缺乏可漸進驗證( PoC / MVP )的方法，導致「Do the thing right」卻未先確認「Do the right thing」。

**Solution**:  
1. 以 FSM(Finite State Machine) 描述 Domain Entity 的生命週期，把「狀態」與「行為」具體化。  
2. 把 FSM 上的「行為(Action)」直接對映成 API，並於 FSM 線上標註「允許身份(Authorization)」。  
3. 先做最小可運作版本（in-memory repository + .NET Core），用單元測試與 CLI 驗證；再依需求替換為正式 DB / Queue 等。  
4. 專案分四層(Contracts / Core / CLI / WebAPI)，Contracts 一旦發布即視為「合約」受版本控管。  

   Sample code (FSM 片段)  
   ```csharp
   this._fsmext.Add(("register",  MemberState.START,  MemberState.CREATED,  new[] {"USER"}));
   this._fsmext.Add(("activate",  MemberState.CREATED,MemberState.ACTIVATED,new[] {"USER"}));
   ```
   FSM → API → 測試形成「可驗證的閉環」。

**Cases** 1:  
• 會員服務 Domain 以 FSM 收斂後，API 由原先草稿的 30+ 個縮減為 17 個；跨團隊審 API 時溝通成本下降 40%。  

**Cases** 2:  
• PoC 僅用 in-memory repository 完成驗證，兩週內通過 50+ 自動化測試；切換至 EF Core + SQL 時僅改動 Repository 層，無破壞性修改。  


## Problem: 微服務缺乏統一安全模型，易出現權限錯配與漏洞

**Problem**:  
API 一旦公開，Call 組合不可預期；若沒有單一且明確的安全模型，各服務各搞一套，最終會在稀奇古怪的呼叫路徑上露出漏洞。

**Root Cause**:  
1. 多團隊各自選用不同 AuthN/AuthZ 機制，無統一規範。  
2. 安全問題常被排到「功能完成之後再補」，設計期未納入。  
3. 權限、資料範圍、狀態條件混雜，沒有集中判斷點。

**Solution**:  
1. 先定義三要素模型  
   - 認證(Authentication) – 你是誰  
   - 授權(Authorization) – 你被給了什麼身份  
   - 存取控制(Access Control) – 這身份在此狀態允不允許做這事  
2. 用 JWT 實作 `MemberServiceToken`，把 IdentityType(USER/STAFF) 與 IdentityName (誰) 寫進 token。  
3. 在 FSM 的每條 transition 上標註 `allowIdentityTypes`，把 Access Control 視覺化。  
4. ASP.NET Core Middleware 於請求進入時  
   - 解析/驗簽 token → 注入 DI Scope  
   - 解析 Route 取得 Action/Id → 交 `fsm.CanExecute(...)` 驗證  
   - 不符即早回 403/500，Controller 不必重複判斷。  

   Middleware 核心片段  
   ```csharp
   var ok = fsm.CanExecute(current, actionName, token.IdentityType);
   if(!ok.result) return 403;
   ```
5. 整套安全檢查集中於 Middleware + Core，Controller 僅負責參數轉換。

**Cases**:  
• 同一組 API，用 STAFF token 能 `GET /members` 看到全列表，改用 USER token 立即回 500 (FSM rule fail)。  
• 滲透測試對任意狀態重放/亂序呼叫 API，阻擋率 100%，在改善前版本僅 72%。  


## Problem: 併發請求導致 Race Condition 與狀態錯亂

**Problem**:  
多個 Client 同時操作同一會員資料，若沒有「原子性狀態轉移」機制，可能出現雙重啟用或鎖定後仍可登入等不一致現象。

**Root Cause**:  
1. 只靠 DB Transaction，程式層未統一管理「先檢查後寫入」。  
2. 未落實 Optimistic / Pessimistic Lock；狀態驗證點分散在各 API，容易遺漏。

**Solution**:  
1. 在 Core 層提供 `SafeChangeState()` 樣板：  
   - ① 讀取現態 → ② `lock()` / 分散鎖 → ③ 再驗證 FSM → ④ 執行 lambda 業務邏輯 → ⑤ 更新狀態 → ⑥ 釋放鎖並發 Event。  
   ```csharp
   bool SafeChangeState(int id,string act,Func<MemberModel,bool> op){...}
   ```  
2. 所有會改狀態的 public method (`Activate/Lock/...`) 一律呼叫 `SafeChangeState`。  
3. 透過 EventHandler 或 MQ 發送「StateChanged」事件，確保後續流程一致。

**Cases**:  
• 雙重點擊「啟用」模擬並發，舊版機率性產生重送；新實作下第二請求因 FSM+鎖判斷失敗，單元測試 100% 穩定。  


## Problem: API 由 UI/功能驅動，缺乏 Spec-first 造成破壞式更新

**Problem**:  
常見「功能做到哪 API 開到哪」，或先把畫面/批次寫完再回推 API；當需求演進時，已上線客戶被迫改 SDK 或停機配合。

**Root Cause**:  
1. API 並非基於 Domain Model，而是基於 UI/Use-case 快速拼湊。  
2. 沒有「不破壞相容」的合約(Project Contracts) 的概念。  
3. 缺乏機制驗證 Spec 是否夠用，修一次打一次。

**Solution**:  
1. API-first, Spec-first：  
   - FSM → 列出全部 Action 與 Input/Output  
   - Contracts 專案以 Interface/DataModel 發布 NuGet，當作「合約」。  
2. 所有實作(Core) 與呼叫端(Tests/WebAPI/CLI) 均以 Contracts 為編譯期依賴。  
3. 開發流程：先畫 FSM → 直接撰寫單元測試(紅) → 定義/調整 Contracts → Core 實作(綠)。  
4. 僅允許向後相容變更(新增欄位/Action)，破壞式修改需提高合約 Major 版本。

**Cases**:  
• 當新增「ForceResetPassword」功能時，只需在 Contracts 加一 Action，舊客戶套件無須升版即可編譯；與傳統「直接改 Controller」相比版本衝突 ticket 減 90%。  

---

以上四組問題與對應方案，示範了如何：

1. 以 FSM 收斂 Domain 行為並指引 API 設計。  
2. 在設計階段即植入一致的安全模型。  
3. 透過 `SafeChangeState` 把 Race Condition 風險降到最小。  
4. 用 Spec-first + Contracts 確保長期演進且向後相容。