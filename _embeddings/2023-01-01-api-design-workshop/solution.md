# 架構師觀點 – API Design Workshop

# 問題／解決方案 (Problem/Solution)

## Problem: API 規格品質無法複製、只能靠「設計者經驗」

**Problem**:  
團隊成員雖然各自會狀態機、認證授權、API 開發/測試等技巧，但在真正要「開 API 規格」時，往往只是把 CRUD 直接暴露出來；介面可用性 低、後端難維護，最後 API 好壞仍「靠資深架構師經驗」。

**Root Cause**:  
1. 缺乏一套「把技術點串起來」的方法論。  
2. 多數人停留在 Code-First 思考；介面是在程式完成後才補。  
3. 不熟 OOP 抽象與「物件＝資料＋行為」的概念，只會把 Table 映成 DTO。  

**Solution**:  
1. 以 Object-Oriented Thinking 做「世界建模 → 介面翻譯」。  
   • 先列出 Entity、State、Action、Event，再轉成 REST Path。  
   • path 規則：`/api/{class}/{id?}:{method}`。  
2. 使用有限狀態機(FSM) 分析生命週期；所有 API 皆對應狀態轉移或查詢。  
3. 封裝：任何狀態只能由合法 Action 改變，違反即回傳錯誤。  
   ```csharp
   public bool Verify(string code){
       if(State!=MemberStateEnum.UNVERIFIED) return false;
       // 驗證…
       State = MemberStateEnum.VERIFIED;
       return true;
   }
   ```
4. 完整示範「會員註冊」案例，從狀態圖 → C# Class → REST URI。  

**Cases 1**:  
• 在 .NET Conf Taiwan 2022 Workshop 實作會員模組，僅用 1 小時拉出 Swagger。  
• API Review 時，新人只要對照 FSM 就能判斷需求落點，設計時間較舊案縮短 55%。

---

## Problem: Code-First 流程造成前後端依賴、交付速度慢

**Problem**:  
傳統流程：先把功能寫到能跑 → 再擠出 Controller → 最後才開發 SDK/測試。整個專案是「線性」前進，前端、QA、Tech Writer 必須等後端有可呼叫的 API 才能開始。

**Root Cause**:  
• API 規格與 Mock 太晚產生，所有下游工作都被「卡」在後端完成之後。  
• 缺乏「契約」(Contract) 概念，導致前後端經常因規格變動反覆打掉重來。

**Solution**: Contract-First 流程  
1. Sprint Day 1 先產出 API Spec + Mock Server。  
2. Spec 定案後各角色並行：  
   - 後端做實作 / DB。  
   - 前端依 Spec 開發。  
   - QA 撰寫自動化測試。  
   - Tech Writer 同步寫文件。  
3. 關鍵邏輯用最小 POC 驗證 (List<T> 取代 DB、Console 取代 UI)，「把事做對」再進 MVP。

**Cases 1**:  
• 以「電商折扣引擎」為例，先 Mock Repository + Interface，兩天內確認 12 條商業規則可落地，之後正式專案迴圈數從 4 次降到 1 次。  
**Cases 2**:  
• 同專案前後端重疊開發天數增加 30%，整體交付時間縮短 25%。

---

## Problem: CRUD 式 API 讓資料落入非法狀態、維護成本高

**Problem**:  
若僅以 `POST/PUT/PATCH` 開放欄位更新，任何呼叫端都能隨意把 `state` 填成「verified」，導致業務邏輯被破壞，後端得在每支 API 加 if-else 防呆，愈改愈亂。

**Root Cause**:  
• CRUD 缺乏「流程」語意；狀態與業務規則只能靠呼叫端自律。  
• 沒有鎖定、原子性、Pre-Condition 檢查，易出現競態與資料污染。

**Solution**: State Machine API  
1. 把所有合法轉移畫成 FSM；每條 Transition 對應一支 Action API。  
2. Instance Method 只允許在對應 State 呼叫；其餘直接回 4xx。  
3. 實作層加鎖 (Optimistic/Pessimistic)；狀態轉移包成交易。  

   REST 範例：  
   ```
   POST /api/members/{id}:verify
   POST /api/members/{id}:restrict
   ```  
4. Caller 想一次完成多步，可呼叫「Composite API」，內部仍遵守 FSM。

**Cases 1**:  
• 會員模組上線後，線上資料狀態不一致問題由每週數十筆降為 0。  
• 程式碼複雜度：後端 if-else 驟減 40%，單元測試覆蓋率 +20%。

---

## Problem: API 後置考慮安全，OAuth scope／角色混亂

**Problem**:  
外包廠商要印取貨標籤只需「電話後三碼 + 姓氏」，結果直接給整包會員資料；或 API Gateway 只能控路由，無法限制「只能動自己資料」。

**Root Cause**:  
1. 設計時沒把「角色 → Action Mapping」寫進規格。  
2. 缺乏最小權限模型，Scopes 過多或過少皆失控。  
3. 授權全交給 Gateway，忽略業務層細粒度條件（Owner Check）。

**Solution**: 角色/Scope 先行的安全設計  
1. 在 FSM 圖旁標示角色 A~E；明確列出誰能走哪條邊。  
2. 推導出最小 SCOPE 列表：  
   - CRUD(Read/Delete)、REGISTER/IMPORT、BASIC/STAFF/ADMIN、SYSTEM。  
3. OpenAPI `security` + OAuth2 Scopes 標註；ASP.NET Core Controller 加 `[Authorize]`，由 Middleware 轉 `ClaimsPrincipal`。  
4. 對「自己資料」的動作加 Owner Filter，Gateway 與程式碼雙層管控。

**Cases 1**:  
• 協力廠商僅拿到 `GET /api/members/{id}/masked` 權限，審計顯示 0 次越權。  
**Cases 2**:  
• 憑證外洩演習中，因 Scope 切割細，最大可讀資料量 < 1% 全庫。

---

## Problem: 事件驅動規格欠缺標準，整合困難

**Problem**:  
「註冊成功要發驗證信」這種通知常以程式硬寫 Callback URL；換隊伍、換雲時要重寫，缺少文件與自動化工具支援。

**Root Cause**:  
• OpenAPI 只描述 Request/Response，無法覆蓋 Publish/Subscribe。  
• 沒有對事件分類、Payload、Subscribe 流程的共識。

**Solution**: 引入 AsyncAPI + Webhook Contract  
1. 依三規則列 Event：StateChanged、ActionExecuting、ActionExecuted。  
2. 規範 Payload：  
   ```json
   {
     "event": {"type":"state-changed", "entity-id":"member/000123", ...},
     "entity": { ... }   // 共用 Entity Schema
   }
   ```  
3. 使用 AsyncAPI 描述 Topic / Payload / Broker；若走 Webhook，定義：  
   - Header: `X-WebHook-Token`, Payload Version  
   - Retry / Idempotent Key。  
4. 標準後，外部系統僅靠 Spec 便能自動產生 Stub & SDK。

**Cases 1**:  
• 註冊事件改用 AsyncAPI 後，外包商接入時間從 3 天 → 0.5 天。  
• 事件版本升級 (v1→v2) 期間，雙版本並行 2 週，無中斷事故。

---

