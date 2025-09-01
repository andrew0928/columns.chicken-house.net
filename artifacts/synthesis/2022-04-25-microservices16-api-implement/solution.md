以下為基於原文內容萃取、整理的 18 個可落地且具教學價值的問題解決案例。每案均包含問題、根因、解法設計、步驟、關鍵程式碼、實測與學習要點等，便於用於實戰教學、專案練習與能力評估。

## Case #1: 用狀態機（FSM）收斂 API 設計，避免過度或不足設計

### Problem Statement（問題陳述）
- 業務場景：團隊閱讀許多大型系統的架構文章後直接套用，導致過度設計（功能超過實際需要或超出團隊能力），或不足設計（缺乏安全與一致性），規格與實作經常反覆修改，造成時程與品質風險。
- 技術挑戰：如何將抽象設計具體落實為可驗證的 API 介面，同時保持設計簡潔、可演進？
- 影響範圍：API 穩定性、跨團隊協作、上線時程、技術債累積。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 太早受實作技術影響導致設計偏離需求。
  2. 規格不清，導致開發過程中頻繁變更。
  3. 缺乏能驗證設計對不對的方法（僅有文件，沒有可執行驗證）。
- 深層原因：
  - 架構層面：缺少統一抽象（沒有可貫穿各子系統的設計語言）。
  - 技術層面：未將狀態、權限規則具象化到可運算的結構。
  - 流程層面：缺少 PoC/MVP 驗證與 Spec-first 的節奏。

### Solution Design（解決方案設計）
- 解決策略：以有限狀態機（FSM）作為 API 設計的統一抽象；所有動作（action）、狀態轉移、可執行角色都標示於 FSM。先以 PoC 驗證 FSM 與介面，再逐步演進，避免過早實作細節卡死設計。

- 實施步驟：
  1. 建構狀態圖與行為清單
     - 實作細節：辨識 Entity（會員）、狀態（START/CREATED/ACTIVATED/...）、動作（register/activate/...）、可執行身分（USER/STAFF）。
     - 所需資源：UML/FSM 工具、需求用例。
     - 預估時間：0.5-1 天
  2. 將 FSM 轉為資料結構與驗證介面
     - 實作細節：定義 state enum、邊（action/起訖狀態/允許身分）集合；提供 CanExecute 查詢。
     - 所需資源：.NET、C#、LINQ。
     - 預估時間：0.5 天
  3. 以測試案例驗證 FSM 與 API 行為
     - 實作細節：撰寫典型生命週期與錯誤路徑測試，校驗規格與設計一致。
     - 所需資源：xUnit/MSTest、Postman。
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// 狀態定義
public enum MemberState { UNDEFINED, START, CREATED, ACTIVATED, DEACTIVED, ARCHIVED, END }

// FSM 資料結構（邊）
private List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)> _fsmext
    = new();

// 部分轉移規則
_fsmext.Add(("register",  MemberState.START,    MemberState.CREATED,   new[] { "USER" }));
_fsmext.Add(("activate",  MemberState.CREATED,  MemberState.ACTIVATED, new[] { "USER" }));
_fsmext.Add(("lock",      MemberState.ACTIVATED,MemberState.DEACTIVED, new[] { "USER","STAFF" }));
```

- 實際案例：會員服務 FSM 驅動的 API 設計，將 USER/STAFF 可執行行為標示於邊，行為即 API 來源。
- 實作環境：.NET 6、C# 10、ASP.NET Core、MSTest、jose-jwt。
- 實測數據：
  - 改善前：規格常變更、行為邊界不清晰（文件無法驗證）。
  - 改善後：以測試案例驗證 FSM 規則，行為一致；API 變更集中於 FSM。
  - 改善幅度：規格確認時間可下降（以 PoC 為準，回合數顯著降低）；單元測試通過率 100%。

Learning Points（學習要點）
- 核心知識點：
  - FSM 作為 API 設計的抽象語言
  - 行為（action）= 邊；狀態（state）= 點
  - Spec-first：以測試案例驗證設計
- 技能要求：
  - 必備技能：UML/FSM 基礎、C# enum/集合、單元測試
  - 進階技能：需求抽象化、API 規格設計
- 延伸思考：
  - 可應用於訂單、工單、風險審批等強狀態域
  - 風險：過度簡化 FSM 造成例外流程無法覆蓋
  - 優化：以資料驅動 FSM（可配置化），配合 Codegen 產出樣板

Practice Exercise（練習題）
- 基礎練習：為「訂單」畫 FSM，標示行為與可執行身分（30 分）
- 進階練習：將 FSM 轉為 C# 結構並實作 CanExecute（2 小時）
- 專案練習：以 FSM 驅動的訂單 API（CRUD+狀態轉換）與單元測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：FSM 覆蓋主流程與錯誤流程
- 程式碼品質（30%）：清晰的 enum/資料結構與命名、一致的檢查介面
- 效能優化（20%）：CanExecute 查詢效率、可維護性
- 創新性（10%）：將 FSM 與測試、Swagger 或 Codegen 整合

---

## Case #2: 移除跨系統直連資料庫，改用 Member Service API 解耦

### Problem Statement（問題陳述）
- 業務場景：多個前台/後台/中台系統都需要存取會員資料，過往直接連 DB 造成耦合、權限難控與一致性風險。
- 技術挑戰：在不影響既有流程下，導入統一的會員 API，對內對外一致。
- 影響範圍：資料一致性、安全合規、維運風險、變更成本。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 各系統直連 DB，權限分配粗糙。
  2. 業務規則散落於多處，難以一致進化。
  3. 無清楚的對外合約（Contracts）。
- 深層原因：
  - 架構層面：缺乏中台/服務化邊界。
  - 技術層面：無 API first 合約與版本治理。
  - 流程層面：跨團隊指令鬆散、權責不清。

### Solution Design（解決方案設計）
- 解決策略：建立多專案分層（Contracts/Core/WebAPI/CLI/Tests），以 Contracts 發佈跨專案介面標準；WebAPI 作為唯一對外入口，所有讀寫透過 Core 的 MemberService。

- 實施步驟：
  1. 建立 Contracts 與 Core
     - 實作細節：Contracts 定義模型/介面；Core 實作商業邏輯。
     - 所需資源：.NET Solution、多專案模板。
     - 預估時間：1 天
  2. 將直連 DB 逐步替換為 API
     - 實作細節：WebAPI 對接 Core；逐步抽換呼叫點，導流至 API。
     - 所需資源：ASP.NET Core、DI。
     - 預估時間：2-3 天（視存量）
  3. 強制安全檢查（FSM + Token）
     - 實作細節：Middleware 檢查 Authorization + MemberServiceAction。
     - 所需資源：jose-jwt、Attribute。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// WebAPI Controller 簽章（薄控制器）
[HttpPost]
[Route("{id:int:min(1)}/activate")]
[MemberServiceAction(ActionName = "activate")]
public IActionResult Activate(int id, [FromForm] string number) {
    _service.Activate(id, number);
    return Ok();
}
```

- 實際案例：GET /members 由 STAFF 成功（200），USER 被拒（500 + FSM Rule fail），證明解耦與權限隔離。
- 實作環境：.NET 6、ASP.NET Core、Postman。
- 實測數據：
  - 改善前：USER 端可讀全表（潛在越權）或分散查詢規則。
  - 改善後：USER 讀全表被 FSM 阻擋；只有 STAFF 可執行。
  - 改善幅度：未授權存取 0 件（以 PoC 測試路徑）；跨系統耦合降低（統一進入點）。

Learning Points（學習要點）
- 核心知識點：
  - 合約（Contracts）與服務邊界
  - API first + 中台化治理
  - 安全檢查前置於 API 層
- 技能要求：
  - 必備技能：ASP.NET Core Controller/DI
  - 進階技能：服務化改造策略、版本治理
- 延伸思考：
  - 可應用於客戶、商品、訂單等共用域
  - 風險：改造期需雙軌維護
  - 優化：以 API Gateway/Service Mesh 管理流量與安全

Practice Exercise（練習題）
- 基礎：將某現有查詢改為呼叫 Core 服務（30 分）
- 進階：為新 API 加入 Contracts、測試與中台檢查（2 小時）
- 專案：將兩個直連 DB 的功能改造為 API（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可完成同等功能
- 程式碼品質（30%）：分層清晰、合約穩定
- 效能優化（20%）：未引入顯著延遲
- 創新性（10%）：灰度切換/回滾策略

---

## Case #3: 統一安全模型：認證/授權/存取控制三段式，JWT 內嵌身分

### Problem Statement（問題陳述）
- 業務場景：跨前台/後台/中台的 API 需一致管理安全，避免 UI 限制失效導致任意呼叫。
- 技術挑戰：安全模型要簡單、可規格化、可測試且能內嵌於設計中。
- 影響範圍：資安、法規合規、客戶信任、風險控管。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 將安全視為「上線前再加」的附加品。
  2. 設計文件與實作脫節，規範不可測。
  3. 身分與權限未標準化傳遞。
- 深層原因：
  - 架構層面：缺乏安全模型與 API 設計的融合。
  - 技術層面：沒有標準化 Token（內含身份/授權）。
  - 流程層面：缺乏測試可驗證的安全規範。

### Solution Design（解決方案設計）
- 解決策略：以 JWT 作為統一安全載體；MemberServiceToken 內嵌 IdentityType（USER/STAFF）與 IdentityName。FSM 的每條邊標示 allowIdentityTypes，即為存取控制規格；以 Middleware 實作一致檢查。

- 實施步驟：
  1. 設計 Token 模型
     - 實作細節：IdentityType/IdentityName/iat/exp/jti/scopes。
     - 所需資源：jose-jwt、JWT 規格。
     - 預估時間：0.5 天
  2. 發行與驗證 Token
     - 實作細節：CreateToken/BuildToken（簽章與驗章）；PoC 可用 HS512，正式環境建議 RSA。
     - 所需資源：金鑰管理。
     - 預估時間：0.5-1 天
  3. 將 Token 注入每次請求
     - 實作細節：Middleware 解析 Authorization: Bearer；以 DI Scoped 提供。
     - 所需資源：ASP.NET Core Middleware、DI。
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public class MemberServiceToken {
    public string IdentityType { get; internal set; } // USER / STAFF
    public string IdentityName { get; internal set; } // WebUI / {staff}...
    public string ID { get; internal set; }           // jti
    public DateTime CreateTime { get; internal set; } // iat
    public DateTime ExpireTime { get; internal set; } // exp
}
```

- 實際案例：用 STAFF Token 成功 GET /members（200）；改用 USER Token 返回 500（FSM rule fail），安全規則可驗證。
- 実作環境：.NET 6、jose-jwt、Postman。
- 實測數據：
  - 改善前：規格不可測；越權風險高。
  - 改善後：安全模型與 FSM 融合；越權呼叫被拒絕。
  - 改善幅度：未授權呼叫阻擋率 100%（以 PoC 用例）。

Learning Points（學習要點）
- 核心知識點：Authentication/Authorization/Access Control 聯動；JWT Claim 設計
- 技能要求：Token 發行/驗證、Middleware
- 延伸思考：多租戶與跨系統憑證串接；Key rotation 與金鑰保護

Practice Exercise（練習題）
- 基礎：用 jose-jwt 產生並驗證 JWT（30 分）
- 進階：在 Middleware 注入 Token 並於 Controller 使用（2 小時）
- 專案：把 API 安全規則嵌入 FSM，寫測試驗證（8 小時）

Assessment Criteria
- 功能完整性：Token 解析/驗證、失效處理
- 程式碼品質：封裝良好、internal set、不可偽造
- 效能優化：中度負載下解析效能
- 創新性：將 FSM 作為安全規格承載

---

## Case #4: 在 FSM 邊上標示授權（allowIdentityTypes）以實作存取控制

### Problem Statement（問題陳述）
- 業務場景：需要明確規範哪些行為可由 USER/STAFF 執行，並可在程式中自動檢查。
- 技術挑戰：授權規則必須內嵌到設計並可被機器檢查。
- 影響範圍：安全、維護成本、回歸測試。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：授權規則散落於控制器或服務內的 if/else，難以維護。
- 深層原因：
  - 架構層面：缺乏統一的授權描述語言。
  - 技術層面：授權與狀態/行為未關聯。
  - 流程層面：測試難以完整覆蓋授權情境。

### Solution Design
- 解決策略：FSM 每條邊新增 allowIdentityTypes；CanExecute 檢查時同時驗證狀態與身分；服務呼叫前統一檢查，避免重複判斷。

- 實施步驟：
  1. 在 FSM 中加入 allowIdentityTypes
     - 實作細節：以 string[] 儲存，供查詢檢查。
     - 資源：C# tuple/list。
     - 時間：0.5 天
  2. 實作 CanExecute 判斷
     - 實作細節：以 LINQ 過濾 actionName/initState/identityType。
     - 時間：0.5 天

- 關鍵程式碼：
```csharp
_fsmext.Add(("activate", MemberState.CREATED, MemberState.ACTIVATED, new[] { "USER" }));
_fsmext.Add(("lock",     MemberState.ACTIVATED, MemberState.DEACTIVED, new[] { "USER", "STAFF" }));

public (bool result, MemberState? initState, MemberState? finalState)
    CanExecute(MemberState currentState, string actionName, string identityType)
{
    var q = from r in _fsmext
            where r.actionName == actionName
              && (r.initState == null || r.initState == currentState)
              && r.allowIdentityTypes.Contains(identityType)
            select r;
    var x = q.FirstOrDefault();
    return x.actionName != null ? (true, currentState, x.finalState) : (false, null, null);
}
```

- 實際案例：USER 可 activate/lock 自己；STAFF 可 lock 任意會員。
- 實作環境：.NET 6、C#。
- 實測數據：
  - 改善前：授權判斷散落多處。
  - 改善後：授權判斷集中到 FSM；一致且可測。
  - 改善幅度：授權變更只需改 FSM，重測範圍縮小。

Learning Points
- FSM 作為授權規格載體
- 將授權從流程控制搬到資料驅動
- A/B 比較：散落 if/else vs 單點規則查詢

Practice
- 基礎：為新 action 加上 allowIdentityTypes 並測試（30 分）
- 進階：支援多身分組合（2 小時）
- 專案：為訂單子域加入角色授權（8 小時）

Assessment
- 功能：授權場景覆蓋
- 品質：規則清晰一致
- 效能：CanExecute 快速
- 創新：規則資料化與可視化

---

## Case #5: 用 Tuple List 建模 FSM，快速實作 CanExecute（查詢型）

### Problem Statement
- 業務場景：需低成本地把狀態圖轉為程式結構，供查詢與驗證。
- 技術挑戰：不引入過多第三方套件，保持可讀與易改。
- 影響範圍：開發速度、可維護性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：傳統 FSM 套件過重或語義不合。
- 深層原因：實作成本高讓團隊抗拒狀態機。

### Solution Design
- 解決策略：以 C# ValueTuple 表達邊；以 enum 表達點；以 LINQ 查詢；滿足「能否執行？」「會轉到哪？」兩個問題。

- 實施步驟：
  1. 定義 enum 與 tuple list
  2. 提供兩種 CanExecute（有/無特定 member）

- 關鍵程式碼：
```csharp
public enum MemberState { START, CREATED, ACTIVATED, DEACTIVED, ARCHIVED, END }
private List<(string actionName, MemberState? initState, MemberState? finalState, string[] allowIdentityTypes)> _fsmext;

public bool CanExecute(string actionName, string identityType) =>
    _fsmext.Any(r => r.actionName == actionName && r.allowIdentityTypes.Contains(identityType));
```

- 實際案例：import/get-members 這類無特定成員的 API 使用 CanExecute(action, identity)。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：無一致查詢介面。
  - 改善後：統一以 CanExecute 檢查；查詢可重用。
  - 改善幅度：程式碼重複顯著下降。

Learning Points
- 資料結構的威力：圖 = 點+邊
- 先滿足 80% 場景的極簡設計
- 避免過早依賴重框架

Practice
- 基礎：新增一條邊與測試（30 分）
- 進階：支援多條邊匹配（例如條件覆蓋）（2 小時）
- 專案：為另一個子域重現同模式（8 小時）

Assessment
- 功能：CanExecute 覆蓋率
- 品質：資料結構清晰
- 效能：查詢效率
- 創新：以資料驅動規格

---

## Case #6: 規格先行 + 單元測試驅動（Spec-first/TDD）驗證 API 行為

### Problem Statement
- 業務場景：API 輸入輸出細節與流程邏輯若只寫在文件，實作時容易走樣。
- 技術挑戰：如何在開發前期就發現規格落差，降低返工。
- 影響範圍：時程、品質、回歸成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：規格與程式不同步；文件不可執行與不可驗證。
- 深層原因：缺乏以測試表達規格的文化與機制。

### Solution Design
- 解決策略：先定義 MemberService 介面（可先 throw NotImplemented），立即撰寫測試（註冊->驗證->登入->鎖定->客服流程），用測試引導輸入輸出與錯誤行為，最後實作讓測試轉綠。

- 實施步驟：
  1. 介面定義與測試撰寫
  2. PoC 以 in-memory repo 快速跑通
  3. 持續補齊錯誤路徑與安全測試

- 關鍵程式碼：
```csharp
// 測試：註冊->未驗證登入失敗->啟用->登入成功
var m = service_for_web.Register("brian","1234","brian@gogo.go");
Assert.IsNotNull(m); Assert.AreEqual(MemberState.CREATED, m.State);
Assert.IsFalse(service_for_web.CheckPassword(m.Id,"1234"));
Assert.IsTrue(service_for_web.Activate(m.Id, m.ValidateNumber));
Assert.IsTrue(service_for_web.CheckPassword(m.Id,"1234"));
```

- 實際案例：BasicScenario1_NewMemberLifeCycleTest 覆蓋會員生命週期。
- 實作環境：.NET 6、MSTest。
- 實測數據：
  - 改善前：規格易歧義。
  - 改善後：可執行規格，測試全綠即通關。
  - 改善幅度：規格確認時間縮短，回歸可自動化。

Learning Points
- 測試既是範例，也是規格
- 以測試倒逼 API 輸入/輸出清晰
- 先避開外部相依（in-memory/mock）

Practice
- 基礎：再寫一個負向測試（30 分）
- 進階：針對錯誤碼與訊息寫測試（2 小時）
- 專案：用測試驅動兩個完整用例（8 小時）

Assessment
- 功能：正負向測試覆蓋
- 品質：測試可讀性、獨立性
- 效能：測試時間、穩定性
- 創新：測試即文件、即範例

---

## Case #7: 封裝狀態改變的原子性與併發控制（SafeChangeState）

### Problem Statement
- 業務場景：多個請求同時操作同一會員（如同時驗證/重置密碼），可能導致資料不一致或幽靈狀態。
- 技術挑戰：確保狀態轉移符合 FSM，並以原子方式更新，避免競態。
- 影響範圍：資料一致性、服務可靠度、風險事件。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：缺乏統一的前置檢查與鎖定機制。
- 深層原因：
  - 架構層面：未明確劃分「流程控制」與「商業邏輯」。
  - 技術層面：缺少樂觀/悲觀鎖策略。
  - 流程層面：無統一樣板，各處自行處理易出錯。

### Solution Design
- 解決策略：以 SafeChangeState 包裹所有狀態改變；進入臨界區前後檢查 CanExecute；封裝鎖定、商業邏輯委派、狀態落盤與事件觸發；日後可替換為分散式鎖與交易型儲存。

- 實施步驟：
  1. 建立 SafeChangeState 樣板
     - 實作細節：鎖定、前後檢查、委派更新、狀態一致性驗證、觸發事件。
     - 時間：1 天
  2. 全 action 導入此樣板
     - 實作細節：以 delegate 傳入具體更新邏輯。
     - 時間：1-2 天

- 關鍵程式碼：
```csharp
private bool SafeChangeState(int id, string actionName, Func<MemberModel,bool> func) {
    lock (_repo._members_syncroot[id]) {
        var check = _fsm.CanExecute(_repo._members[id].State, actionName, _token.IdentityType);
        if (!check.result) return false;

        var model = _repo._members[id].Clone();
        var initState = model.State;
        if (!func(model)) throw new MemberServiceException("func failed");
        if (model.State != check.finalState) throw new MemberServiceException("state mismatch with FSM");

        _repo._members[id] = model.Clone();
        // 觸發事件...
    }
    return true;
}
```

- 實際案例：Activate/Lock/Unlock/SoftDelete 均經 SafeChangeState。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：偶發狀態不一致（理論風險）。
  - 改善後：狀態改變具原子性；違規會丟出一致的錯誤。
  - 改善幅度：避免併發下的幽靈狀態（以 PoC 為前提）。

Learning Points
- AOP 思維：流程控制與業務邏輯分離
- 樂觀驗證：前後一致性檢查
- 從單機鎖走向分散式鎖的演化

Practice
- 基礎：將另一個 action 接入 SafeChangeState（30 分）
- 進階：引入版本號（樂觀鎖）驗證（2 小時）
- 專案：以 Redis/DB 行鎖替換 C# 鎖（8 小時）

Assessment
- 功能：所有狀態改變均經樣板
- 品質：錯誤處理一致
- 效能：臨界區微小
- 創新：可插拔鎖策略設計

---

## Case #8: 事件驅動：狀態改變事件（OnStateChanged）與未來 MQ 替換

### Problem Statement
- 業務場景：狀態改變後需發送通知、審計紀錄、發送 Email 等。
- 技術挑戰：如何在不耦合業務的情況下擴充後置處理？
- 影響範圍：跨服務協作、審計與營運自動化。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：後置處理分散於多處，難以擴充與觀測。
- 深層原因：
  - 架構層面：未建立可靠事件總線。
  - 技術層面：缺少通用事件模型。
  - 流程層面：事件未成為規格的一部分。

### Solution Design
- 解決策略：在 MemberService 內定義 OnStateChanged 事件；SafeChangeState 成功後觸發；先以本機 event；未來可替換 Kafka/RabbitMQ/Webhook。

- 實施步驟：
  1. 定義事件與事件參數
  2. 在 SafeChangeState 最後統一觸發
  3. 訂閱者先做 Logger，之後替換為 MQ

- 關鍵程式碼：
```csharp
public event EventHandler<MemberServiceEventArgs> OnStateChanged;

private void MemberService_OnStateChanged(object s, MemberServiceEventArgs e) {
    Console.WriteLine($"* OnStateChanged: {e.InitState} -> {e.FinalState} via {e.ActionName}");
}
```

- 實際案例：Activate 成功觸發 OnStateChanged，Console 記錄事件。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：後置處理難以統一擴充。
  - 改善後：事件化，易替換 MQ。
  - 改善幅度：擴充新行為不需改核心流程。

Learning Points
- 事件作為擴充點
- 本機 event -> MQ 的演化路徑
- 邏輯去耦：核心流程更穩定

Practice
- 基礎：新增一個事件訂閱者記錄到檔案（30 分）
- 進階：替換為發送到 MQ（2 小時）
- 專案：實作狀態改變寄送郵件（8 小時）

Assessment
- 功能：事件正確觸發
- 品質：訂閱者與核心解耦
- 效能：非同步處理不阻塞
- 創新：可插拔傳輸層

---

## Case #9: 多專案分層（Core/Contracts/WebAPI/CLI/Tests）與責任切分

### Problem Statement
- 業務場景：單一專案混雜介面、邏輯、通訊、測試，導致修改影響面大。
- 技術挑戰：如何在團隊協作下，清楚劃分責任邊界與可重用性？
- 影響範圍：維護成本、協作效率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：專案缺乏明確分層。
- 深層原因：
  - 架構層面：合約管理未成文化。
  - 流程層面：缺乏版本與相容性管理。

### Solution Design
- 解決策略：建立 5 類專案：WebAPI（HTTP）、CLI（工具/批次）、Core（商業邏輯）、Contracts（跨專案介面/模型）、Tests（測試）；Contracts 視為合約，集中治理。

- 實施步驟：
  1. 建立 Solution 分層與參考關係
  2. 在 Core 落實 FSM/Token/Service
  3. WebAPI 與 CLI 僅作為接入層

- 關鍵程式碼/設定：
```csharp
// Startup.cs DI
services.AddSingleton<MemberRepo>(new MemberRepo(0, "init-database.jsonl"));
services.AddSingleton<MemberStateMachine>();
services.AddScoped<MemberServiceToken>();
services.AddScoped<MemberService>();
```

- 實際案例：WebAPI 與 CLI 共用 Core；Contracts 作為穩定合約，避免破壞相容。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：跨層耦合，修改牽動多處。
  - 改善後：分層清楚，重用度提升。
  - 改善幅度：變更影響面可預期且縮小。

Learning Points
- 合約優先：Contracts 受管控
- 可重用 Core，接入層可多樣
- 減少跨層耦合

Practice
- 基礎：將一段邏輯從 WebAPI 移至 Core（30 分）
- 進階：以 CLI 驗證 Core 功能（2 小時）
- 專案：建立簡易 Contracts 套件發佈（8 小時）

Assessment
- 功能：分層正確、相依清楚
- 品質：合約穩定、避免破壞性修改
- 效能：重用提高、部署簡化
- 創新：多入口共用同核心

---

## Case #10: 以 In-memory Repository 取代資料庫，加速 PoC 與測試

### Problem Statement
- 業務場景：初期 PoC 不需要連 DB，但又要驗證流程/安全/狀態。
- 技術挑戰：如何快速可測且可替換？
- 影響範圍：開發速度、測試穩定性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：資料庫相依使測試脆弱且成本高。
- 深層原因：過早引入基礎建設。

### Solution Design
- 解決策略：Repository 以 in-memory 結構 + JSON 匯入/匯出；以 DI 提供，未來可替換為 DB 實作。

- 實施步驟：
  1. 實作 in-memory 結構與同步機制
  2. 增加 JSON 匯入初始資料能力
  3. 以介面封裝，便於替換

- 關鍵程式碼/設定：
```csharp
// Startup.cs: 以 JSON 檔初始化 repo
services.AddSingleton<MemberRepo>(new MemberRepo(0, @"init-database.jsonl"));
```

- 實際案例：單元測試與 Postman 測試無需 DB 環境即可執行。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：搭 DB 才能測，流程慢。
  - 改善後：測試快速穩定、可離線。
  - 改善幅度：測試回饋時間顯著下降。

Learning Points
- PoC 要點：去除非必要相依
- 替換點設計：介面與 DI
- JSON 作為輕量資料源

Practice
- 基礎：加一個匯出 JSON 功能（30 分）
- 進階：以介面抽出 Repo（2 小時）
- 專案：替換為 EF Core/InMemory Provider（8 小時）

Assessment
- 功能：讀寫正確
- 品質：可替換、無內洩
- 效能：小資料量快速
- 創新：環境無相依測試

---

## Case #11: 用 ASP.NET Core Middleware 前置安全檢查與 FSM 規則校驗

### Problem Statement
- 業務場景：每個 API 都要檢查 Token 與 FSM 規則，若散落於控制器易失誤。
- 技術挑戰：如何統一前置檢查與錯誤回應？
- 影響範圍：安全、維護成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：檢查散落、重複程式碼多。
- 深層原因：缺乏 AOP 思維在 WebAPI 的落地。

### Solution Design
- 解決策略：建立 MemberServiceMiddleware：解析 Authorization Bearer，注入 MemberServiceToken；讀取 MemberServiceAction attribute 取得 actionName；在 Controller 前先執行 FSM 檢查，統一拋錯與回應。

- 實施步驟：
  1. 註冊 Middleware 與 DI
  2. 在 Middleware 中解析 Token 與 Action
  3. 呼叫服務的 FSMRuleCheck（或 CanExecute）驗證

- 關鍵程式碼：
```csharp
public async Task Invoke(HttpContext ctx, MemberServiceToken token, MemberStateMachine fsm, MemberService svc){
    // 取 Authorization: Bearer <JWT>
    var tokenText = ctx.Request.Headers["authorization"].FirstOrDefault()?.Substring("Bearer ".Length);
    MemberServiceTokenHelper.BuildToken(token, tokenText);

    // 讀取 MemberServiceAction(ActionName)
    var actionAttr = ctx.GetEndpoint()?.Metadata.OfType<MemberServiceActionAttribute>().FirstOrDefault();
    svc.FSMRuleCheck(id, actionAttr?.ActionName); // 若不符，拋 MemberServiceException

    await _next(ctx);
}
```

- 實際案例：USER 呼叫 GET /members 於 Middleware 即被拒。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：控制器重複檢查，易漏。
  - 改善後：檢查集中、錯誤回應一致。
  - 改善幅度：重複碼下降；安全一致性提高。

Learning Points
- AOP/Middleware 模式
- Attribute 作為規則標註
- 前置檢查與統一錯誤處理

Practice
- 基礎：為新 API 標上 MemberServiceAction（30 分）
- 進階：提供客製錯誤格式（2 小時）
- 專案：統一審計紀錄於 Middleware（8 小時）

Assessment
- 功能：檢查覆蓋率
- 品質：錯誤處理一致
- 效能：開銷可控
- 創新：宣告式規則 + 中介鏈

---

## Case #12: 正確的 DI 生命週期（Scoped/Singleton）以避免身分外洩

### Problem Statement
- 業務場景：身份 Token 應與 Request 對應，避免跨請求共享誤用。
- 技術挑戰：如何設定 DI 生命週期避免資安事故與 Thread 安全問題？
- 影響範圍：資安、穩定性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：不當將 Token/Service 註冊為 Singleton。
- 深層原因：對 DI 生命週期認識不足。

### Solution Design
- 解決策略：MemberRepo/MemberStateMachine 為 Singleton（全域參考/規則）；MemberServiceToken/MemberService 為 Scoped（每請求一份）。

- 實施步驟：
  1. Startup.cs 設定生命週期
  2. 於 Middleware 注入 Scoped 物件並填入 Token

- 關鍵程式碼：
```csharp
services.AddSingleton<MemberRepo>();
services.AddSingleton<MemberStateMachine>();
services.AddScoped<MemberServiceToken>();
services.AddScoped<MemberService>();
```

- 實際案例：每次請求的 Token 由 Middleware 填入，控制器取得當前請求專屬 Token。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：跨請求錯用身分風險。
  - 改善後：每請求隔離，安全確保。
  - 改善幅度：身分外洩風險趨近 0（設計級防範）。

Learning Points
- DI 生命週期語義
- Token/Service 與 Request 關係
- 組態即安全

Practice
- 基礎：故意改成 Singleton 體驗錯誤（30 分）
- 進階：新增 Transient 服務理解差異（2 小時）
- 專案：設計一張 DI 相依圖與說明（8 小時）

Assessment
- 功能：生命週期正確
- 品質：無跨請求污染
- 效能：合理實例數量
- 創新：設計即防呆

---

## Case #13: 薄控制器（Thin Controller）將邏輯下沉至 Core

### Problem Statement
- 業務場景：控制器若堆疊商業邏輯，易造成可讀性差與重複實作。
- 技術挑戰：如何讓 WebAPI 僅專注於輸入輸出與協定，避免邏輯散落。
- 影響範圍：可維護性、重用性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：控制器承載過多責任。
- 深層原因：分層界線不清。

### Solution Design
- 解決策略：控制器只負責 Model Binding、呼叫 Core 服務、回傳結果；所有流程/檢查/狀態/事件在 Core。

- 實施步驟：
  1. 移除控制器內業務判斷
  2. 以 Core MemberService 提供動作方法（Activate/Lock/...）

- 關鍵程式碼：
```csharp
[HttpPost]
[Route("{id:int:min(1)}/activate")]
[MemberServiceAction(ActionName = "activate")]
public IActionResult Activate(int id, [FromForm]string number) {
    _service.Activate(id, number);
    return Ok();
}
```

- 實際案例：控制器即轉發，行為一致由 Core 管。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：控制器難以測試。
  - 改善後：控制器薄且穩定。
  - 改善幅度：重用度與測試性上升。

Learning Points
- 分層責任原則
- 輸入/輸出與業務流程分離
- 減法設計提升品質

Practice
- 基礎：將一段 if/else 下沉至 Core（30 分）
- 進階：控制器回傳標準差錯格式（2 小時）
- 專案：完成 5 個端點薄控制器重構（8 小時）

Assessment
- 功能：行為無回退
- 品質：控制器簡潔
- 效能：無多餘開銷
- 創新：高重用性介面

---

## Case #14: Token 發行與驗證：PoC 先用 HS512，正式改 RSA

### Problem Statement
- 業務場景：PoC 需要可用 Token 流程；正式環境需更強金鑰與管理。
- 技術挑戰：平衡簡化與安全，便於切換。
- 影響範圍：資安風險、Key 管理。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：PoC 常將 Key 寫死於程式碼。
- 深層原因：缺乏 Key 管理策略與演算法選擇。

### Solution Design
- 解決策略：PoC 採對稱（HS512）+ jose-jwt，Key 硬編碼（僅 PoC）；正式切換至 RSA/ECDSA，私鑰妥善保護、金鑰輪替；以 Helper 集中 Token 產生/解析，便於替換演算法。

- 實施步驟：
  1. CLI 產生 Token 以便測試
  2. Middleware 解析 Token into MemberServiceToken
  3. 替換演算法與 Key 來源（祕密管理系統）

- 關鍵程式碼：
```csharp
// PoC key (僅示範，不建議正式使用)
private static readonly byte[] _jwt_key = new byte[] { 0x06, 0x07, 0x04, 0x01 };

// 產生 Token（CLI）
Console.WriteLine(MemberServiceTokenHelper.CreateToken(type, name));
```

- 實際案例：生成 USER/STAFF 兩種 Token，Postman 測試通過。
- 實作環境：.NET 6、jose-jwt。
- 實測數據：
  - 改善前：無法測試安全流程。
  - 改善後：PoC 可運行；易於切換到 RSA。
  - 改善幅度：開發效率提升；安全可演進。

Learning Points
- Token 演算法選型
- Key 管理（祕密管理、輪替）
- 階段性安全策略

Practice
- 基礎：用 CLI 生成 Token 並驗證於 jwt.io（30 分）
- 進階：改為 RSA 與私鑰存放（2 小時）
- 專案：Key 旋轉與版本相容策略（8 小時）

Assessment
- 功能：可生成/驗證
- 品質：Helper 封裝完善
- 效能：驗證開銷可接受
- 創新：可平滑升級

---

## Case #15: 密碼重置三條路徑的狀態化設計

### Problem Statement
- 業務場景：密碼重置有多種情境：舊密碼、驗證碼、客服強制；需狀態與身分限制。
- 技術挑戰：在 FSM 中正確表達與限制，避免濫用。
- 影響範圍：安全、客訴處理效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：不同情境混用或缺少限制。
- 深層原因：邏輯未與狀態、身分綁定。

### Solution Design
- 解決策略：FSM 針對三條動作標示狀態與身分要求；Core 提供對應方法並走 SafeChangeState（如有狀態改變）。

- 實施步驟：
  1. 在 FSM 定義三條邊
  2. 實作對應 API：ResetPasswordWithCheckOldPassword()、ResetPasswordWithValidateNumber()、ForceResetPassword()

- 關鍵程式碼：
```csharp
_fsmext.Add(("reset-password-with-old-password", MemberState.ACTIVATED, null, new[] { "USER" }));
_fsmext.Add(("reset-password-with-validate-number", MemberState.DEACTIVED, MemberState.ACTIVATED, new[] { "USER" }));
_fsmext.Add(("force-reset-password", MemberState.DEACTIVED, null, new[] { "STAFF" }));
```

- 實際案例：USER 以驗證碼在 DEACTIVED 狀態恢復為 ACTIVATED；STAFF 可在 DEACTIVED 強制改密碼。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：重置行為可能繞過驗證。
  - 改善後：路徑分明、狀態/身分限制明確。
  - 改善幅度：不當重置被阻擋（PoC 測試）。

Learning Points
- 行為與狀態/身分的綁定
- 安全敏感流程的規則化
- 測試覆蓋多情境

Practice
- 基礎：為一條重置路徑寫測試（30 分）
- 進階：補充錯誤碼與訊息（2 小時）
- 專案：整合寄信/簡訊驗證碼（8 小時）

Assessment
- 功能：三路徑皆可運作
- 品質：規則一致、可測
- 效能：流程簡潔
- 創新：FSM 驅動敏感流程

---

## Case #16: 連續登入失敗三次自動鎖定與解鎖流程

### Problem Statement
- 業務場景：暴力嘗試密碼需防範；自動鎖定與客服解鎖是常見 SOP。
- 技術挑戰：把失敗次數與狀態轉移整合，避免繞過。
- 影響範圍：資安、用戶體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：登入失敗計數與狀態無整合。
- 深層原因：缺乏在服務層統一處理。

### Solution Design
- 解決策略：CheckPassword() 內維護失敗次數；達閾值轉 DEACTIVED；Unlock() 與 STAFF 操作整合 SafeChangeState。

- 實施步驟：
  1. 在 MemberModel 增加 failedLoginAttemptsCount
  2. CheckPassword 失敗則累加，達 3 次改 DEACTIVED
  3. 提供 UnLock() 由 USER/STAFF 視情境解鎖

- 關鍵程式碼（測試片段）：
```csharp
Assert.IsFalse(service_for_web.CheckPassword(id,"5678"));
Assert.IsFalse(service_for_web.CheckPassword(id,"5678"));
Assert.IsFalse(service_for_web.CheckPassword(id,"5678"));
Assert.AreEqual(MemberState.DEACTIVED, service_for_web.GetMember(id).State);
```

- 實際案例：Brian 三次失敗鎖定 -> 客服發驗證碼 -> 用驗證碼重設恢復。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：可持續撞密碼。
  - 改善後：自動鎖定機制生效。
  - 改善幅度：暴力破解難度上升（PoC）。

Learning Points
- 安全與狀態機整合
- 業務 SOP 規範化
- 測試覆蓋負向路徑

Practice
- 基礎：為解鎖流程寫測試（30 分）
- 進階：加入指數退避與延遲（2 小時）
- 專案：加入 IP 黑名單與風控（8 小時）

Assessment
- 功能：鎖定/解鎖正確
- 品質：流程一致、可測
- 效能：阻擋攻擊成本提升
- 創新：與風控資料結合

---

## Case #17: 最小 API 面積原則（Minimal Surface Area）

### Problem Statement
- 業務場景：需求多樣易導致端點爆炸；維護困難、攻擊面增大。
- 技術挑戰：如何收斂 API，透過複用與組合滿足需求？
- 影響範圍：維運負擔、資安、升級成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：為每個需求新開 API。
- 深層原因：缺乏「組合式」思維與狀態機設計。

### Solution Design
- 解決策略：能以多次呼叫完成者不新增端點；非核心資料由呼叫端自行存放；僅在需要批次/效能/交易才擴充端點；以 FSM 辨識真正的「行為」。

- 實施步驟：
  1. 盤點需求，能組合者標記
  2. 僅為真正行為擴充（FSM 邊）
  3. 审視批次/交易需求再增強

- 關鍵程式碼：無（設計原則）
- 實際案例：ResetPassword 拆成三條路徑覆蓋多情境，而非每變種一個 API。
- 實作環境：—
- 實測數據：
  - 改善前：端點顆粒太多。
  - 改善後：端點精煉，維護簡化。
  - 改善幅度：攻擊面減少、文件簡潔。

Learning Points
- 行為優先，非畫面導向
- 組合式思維
- 用 FSM 驅動 API 增長

Practice
- 基礎：檢視既有端點可合併者列清單（30 分）
- 進階：設計批次端點與條件（2 小時）
- 專案：重構 3 個冗餘端點（8 小時）

Assessment
- 功能：不失功能的精簡
- 品質：規格清晰
- 效能：降低維護成本
- 創新：API 生態穩定

---

## Case #18: 一致化的錯誤回應與安全回應（403/500 + Middleware）

### Problem Statement
- 業務場景：不一致的錯誤碼/格式增加整合與排錯成本。
- 技術挑戰：如何集中處理並保持一致？
- 影響範圍：用戶體驗、排錯效率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：錯誤處理散落各層。
- 深層原因：缺乏統一錯誤策略與集中處理點。

### Solution Design
- 解決策略：於 Middleware 捕捉 MemberServiceException 與 FSM 檢核錯誤，統一回應 403/500 與 Problem+JSON 錯誤體；控制器保持乾淨。

- 實施步驟：
  1. Middleware try/catch 包裹管線
  2. 定義錯誤映射與 body 格式
  3. 補測試覆蓋負向路徑

- 關鍵程式碼：
```csharp
catch (MemberServiceException e) {
    context.Response.StatusCode = 500;
    await context.Response.WriteAsync("MemberStateMachineException: " + e.Message);
}
```

- 實際案例：USER 調 GET /members 回 500 + FSM rule fail；未啟用登入回 403。
- 實作環境：.NET 6、Postman。
- 實測數據：
  - 改善前：錯誤回應不一致。
  - 改善後：統一由 Middleware 輸出。
  - 改善幅度：整合與排錯效率提升。

Learning Points
- 統一錯誤策略
- Middleware 為最佳集中點
- 錯誤碼/格式標準化

Practice
- 基礎：擴充為 RFC7807 Problem+JSON（30 分）
- 進階：區分 401/403/409/422（2 小時）
- 專案：建置全域錯誤處理與追蹤 ID（8 小時）

Assessment
- 功能：錯誤覆蓋
- 品質：格式一致
- 效能：開銷可控
- 創新：與追蹤/日誌整合

---

## Case #19: 無特定會員之服務級行為（import/get-members）的 FSM 檢查

### Problem Statement
- 業務場景：有些 API 不是針對單一會員（如匯入、查列表），仍需基於身分限制。
- 技術挑戰：如何在 FSM 中表達與檢查？
- 影響範圍：安全、一致性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：以為 FSM 只能管個體狀態。
- 深層原因：未建立「無狀態/服務級」的規則描述。

### Solution Design
- 解決策略：在 FSM 以 null init/final state 表示不關聯特定會員；提供 CanExecute(action, identity) 檢查。

- 實施步驟：
  1. 加入無狀態邊（init/final = null）
  2. 呼叫簡化版 CanExecute

- 關鍵程式碼：
```csharp
_fsmext.Add(("import", null, null, new[] { "STAFF" }));
_fsmext.Add(("get-members", null, null, new[] { "STAFF" }));

public bool CanExecute(string actionName, string identityType) =>
    _fsmext.Any(r => r.actionName == actionName && r.allowIdentityTypes.Contains(identityType));
```

- 實際案例：STAFF 可 get-members；USER 被拒。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：無一致檢查。
  - 改善後：服務級規則清楚可檢查。
  - 改善幅度：安全一致性提升。

Learning Points
- FSM 非僅個體狀態，也可表達服務級動作
- 提供兩類 CanExecute
- 清楚描述權限邊界

Practice
- 基礎：新增一個服務級行為（30 分）
- 進階：加入條件（如 scope）（2 小時）
- 專案：實作批次匯入與權限檢查（8 小時）

Assessment
- 功能：檢查正確
- 品質：規則清晰
- 效能：查詢快速
- 創新：FSM 廣義化

---

## Case #20: 單一 API 集合服務多種身分（USER/STAFF）的差異化權限

### Problem Statement
- 業務場景：同一組 API 給前台/後台使用，但權限需完全不同。
- 技術挑戰：如何避免為身分分裂端點、仍保持一致性？
- 影響範圍：文件、整合、安全。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：不同身分開不同 API，導致爆炸式增長。
- 深層原因：缺乏以 Token+FSM 區分身分的設計。

### Solution Design
- 解決策略：以單一 API 集合，使用 Token.IdentityType 區分身分；FSM allowIdentityTypes 控制可執行範圍；Middleware 根據 Attribute+FSM 先行阻擋。

- 實施步驟：
  1. 定義身分型別與 Token 載荷
  2. 在 FSM 標示不同行為允許的身分
  3. 以 Middleware 檢查

- 關鍵程式碼：
```csharp
// FSM 範例
_fsmext.Add(("get-member", null, null, new[] { "USER","STAFF" })); // 可限制 USER 只能查自己（由 IdentityName 對應）
```

- 實際案例：兩把 Token（USER/STAFF）呼叫相同 API，得到差異化結果/限制。
- 實作環境：.NET 6。
- 實測數據：
  - 改善前：端點分裂、文件複雜。
  - 改善後：單一 API 集合，權限分明。
  - 改善幅度：文件與維護成本下降。

Learning Points
- 身分以 Token 承載
- 行為以 FSM 限制
- 單一 API 集合服務多角色

Practice
- 基礎：為某 API 加上身分差異測試（30 分）
- 進階：限制 USER 僅能查自己（2 小時）
- 專案：完成一組 USER/STAFF 共用 API（8 小時）

Assessment
- 功能：權限差異正確
- 品質：文件簡潔
- 效能：維護成本降低
- 創新：最小 API 集合最大覆蓋

---

案例分類
1) 按難度分類
- 入門級：
  - Case 5, 9, 10, 12, 13, 17, 19
- 中級：
  - Case 1, 2, 3, 4, 6, 14, 15, 16, 18, 20
- 高級：
  - Case 7, 8, 11

2) 按技術領域分類
- 架構設計類：Case 1, 2, 9, 17, 20
- 效能優化類：Case 7, 10, 12（效能/穩定面向）
- 整合開發類：Case 11, 13, 14, 19
- 除錯診斷類：Case 6, 18
- 安全防護類：Case 3, 4, 15, 16, 20

3) 按學習目標分類
- 概念理解型：Case 1, 3, 4, 5, 9, 12, 17
- 技能練習型：Case 6, 10, 13, 14, 19
- 問題解決型：Case 2, 7, 11, 15, 16, 18, 20
- 創新應用型：Case 8（事件/MQ 演進）、Case 7（可插拔鎖策略）

案例關聯圖（學習路徑建議）
- 起步（概念與基礎）
  1) 先學：Case 1（FSM 驅動 API 設計）、Case 5（FSM 實作）
  2) 其次：Case 3（安全三段式）、Case 4（FSM 授權）
  3) 分層：Case 9（多專案結構）、Case 12（DI 生命週期）

- 中段（落地與整合）
  4) 服務層：Case 13（薄控制器）、Case 10（In-memory Repo）
  5) 規格驗證：Case 6（測試驅動）
  6) 安全前置：Case 11（Middleware 前置檢查）
  7) Token 流程：Case 14（Token 生成/驗證）

- 領域與安全強化
  8) 領域場景：Case 15（重置密碼三路徑）、Case 16（失敗鎖定）
  9) 服務級行為：Case 19（無狀態動作）
  10) 權限差異：Case 20（單一 API 多身分）

- 進階與運營
  11) 併發與一致性：Case 7（SafeChangeState）
  12) 事件化：Case 8（OnStateChanged→MQ）
  13) 錯誤一致：Case 18（錯誤處理）
  14) API 生態：Case 17（最小面積原則）

- 依賴關係要點
  - Case 7（SafeChangeState）依賴：Case 5（FSM）、Case 3/4（安全/授權）
  - Case 11（Middleware）依賴：Case 3/4（Token/FSM）、Case 12（DI）
  - Case 15/16（密碼/鎖定）依賴：Case 5（FSM）、Case 7（原子性）
  - Case 8（事件）依賴：Case 7（狀態變更鉤子）

完整學習路徑建議
- 第一階段（1-2 週）：Case 1, 5, 3, 4, 9, 12
- 第二階段（1-2 週）：Case 13, 10, 6, 11, 14
- 第三階段（1-2 週）：Case 15, 16, 19, 20
- 第四階段（1-2 週）：Case 7, 8, 18, 17

此路徑由概念→基礎實作→安全與領域→併發與營運化，逐步加深，亦與原文的設計與實作節奏相呼應。