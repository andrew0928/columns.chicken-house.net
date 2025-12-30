---
layout: synthesis
title: "Policy Injection Application Block 小發現..."
synthesis_type: solution
source_post: /2008/11/18/policy-injection-application-block-small-discovery/
redirect_from:
  - /2008/11/18/policy-injection-application-block-small-discovery/solution/
---

以下內容基於原文觀點與範例，聚焦於「Policy Injection Application Block (PIAB)」帶來的實作方式與效益，將可落地的問題—根因—解法—效益整理為 15 個可教學、可練習、可評估的案例。每個案例盡可能引用文中已提及的概念、行為與範例碼模式（AuthorizationCallHandler、Create/Wrap 代理、各種 Handler：Authorization/Caching/Exception/Logging/Performance Counter/Validation/Custom Pipeline），並以可操作的步驟與示例補齊教學需求。

## Case #1: 從 CAS 到 PIAB：讓自訂授權與橫切關注真正生效

### Problem Statement（問題陳述）
業務場景：團隊過去使用 .NET 的 Role-Based Security（CAS/PrincipalPermissionAttribute）在方法呼叫前檢查角色，程式碼漂亮但無法插入額外自訂行為（例如加上 Log、額外檢查）。隨著需求增加，需要能同時做授權、記錄、驗證等跨切邏輯，並保持宣告式與低侵入。
技術挑戰：CAS 層級由 CLR 支援，無法在呼叫途徑中插入自訂邏輯；自訂 Attribute 也不會被觸發。
影響範圍：安全控制與稽核分散在多處，難以維護；新需求（Log/驗證）無法宣告式整合。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. CAS 由 CLR 直接執行，呼叫時不會觸發自訂 Attribute。
2. 無可攔截的呼叫管線，無法在執行前/後插入邏輯。
3. 嘗試用 AOP/Remoting 過於繁瑣，難以實用化。

深層原因：
- 架構層面：缺少系統化的攔截/代理層。
- 技術層面：Attribute 只宣告，不綁定執行攔截器。
- 流程層面：橫切需求後置處理，沒有標準化介入點。

### Solution Design（解決方案設計）
解決策略：改用 PIAB，在物件建立時用 PolicyInjection.Create/Wrap 產生代理，透過 Call Handler（如 Authorization/Logging/Validation）在方法前後掛入行為，保留宣告式寫法，並以最小程式碼侵入達到擴充。

實施步驟：
1. 以 PIAB 產生代理
- 實作細節：用 PolicyInjection.Create/Wrap 取代 new，讓呼叫走攔截管線。
- 所需資源：Enterprise Library（PIAB）、C#
- 預估時間：0.5 天

2. 以 Attribute 宣告授權並測試
- 實作細節：加上 [AuthorizationCallHandler("operation-name")]，以宣告式控制授權。
- 所需資源：Security Application Block
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 既有 CAS（無法插入自訂行為）
[PrincipalPermissionAttribute(SecurityAction.Demand, Role="Supervisor")]
public void Foo() { /* ... */ }

// PIAB 授權（可插入更多行為）
[AuthorizationCallHandler("operation-name")]
public void Deposit(decimal depositAmount) { /* ... */ }

// 關鍵：以 PIAB 代理替代 new
var account = PolicyInjection.Create<Account>(new Account());
account.Deposit(100m);
```

實際案例：以 Deposit 方法示範以授權 Handler 在呼叫前檢查是否允許執行。
實作環境：.NET Framework、C#、Enterprise Library（PIAB + Security AB）
實測數據：
改善前：僅能做角色檢查，無法插入 Log/驗證。
改善後：呼叫前同時完成授權與可插拔橫切行為。
改善幅度：擴充性顯著提升（支援多種 Handler）。

Learning Points（學習要點）
核心知識點：
- CLR 原生 CAS 的限制與攔截式授權的差異
- 代理與攔截鏈（Call Handler Pipeline）
- 宣告式 Attribute 與執行期攔截的關聯

技能要求：
必備技能：C#、Attribute、基礎安全觀念
進階技能：代理/攔截、Enterprise Library 組態

延伸思考：
- 還可插入哪些橫切關注（快取、Perf、例外）？
- 攔截會否影響偵錯與堆疊？
- 如何控管 Handler 順序與開關？

Practice Exercise（練習題）
基礎練習：將既有 new 改為 PolicyInjection.Create 並成功呼叫。
進階練習：在一個方法上同時加入授權與記錄。
專案練習：將一個服務層全面改造為代理驅動，並加入兩種 Handler。

Assessment Criteria（評估標準）
功能完整性（40%）：授權與代理生效
程式碼品質（30%）：低侵入、結構清晰
效能優化（20%）：攔截成本可接受
創新性（10%）：多 Handler 串接設計


## Case #2: 角色判斷到授權規則：以 Operation 為核心的存取控制

### Problem Statement（問題陳述）
業務場景：金融類系統中，使用者屬於高權限角色（如 Administrators）並不代表能執行所有操作，實際上應受特定操作（operation）或 ACL 規則限制，例如禁止讀取某敏感檔案或執行特定交易。
技術挑戰：角色判斷（RBAC）過於粗糙，需要可驗證「此人是否被授權做此操作」的細緻規則。
影響範圍：誤授權風險、稽核追蹤困難、合規性風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 角色只代表預設能力，不代表特定資源/操作授權。
2. CAS 僅能驗證角色，不等同於授權規則。
3. 缺少可直接針對操作（operation）做授權檢查的機制。

深層原因：
- 架構層面：系統未內建以操作為中心的授權策略。
- 技術層面：未導入可擴充的授權 Handler。
- 流程層面：稽核與授權規則未集中管理。

### Solution Design（解決方案設計）
解決策略：使用 AuthorizationCallHandler 於方法呼叫前檢查特定 operation 的授權，將存取控制由「角色」轉為「操作」，提升精準度與合規性。

實施步驟：
1. 定義 operation 與規則
- 實作細節：在 Security AB 中定義 operation 與對應規則（可由企業規章導入）。
- 所需資源：Security AB
- 預估時間：1 天

2. 以 Attribute 套用授權
- 實作細節：在關鍵方法上加 [AuthorizationCallHandler("operation-name")]。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
[AuthorizationCallHandler("op.cash.deposit")]
public void Deposit(decimal amount) { /* 實作略 */ }

var svc = PolicyInjection.Create<AccountService>(new AccountService());
svc.Deposit(500m); // 呼叫前會檢查 op.cash.deposit 是否允許
```

實際案例：文中以 Deposit 示範，強調「授權」高於「角色」的精度。
實作環境：.NET、C#、PIAB + Security AB
實測數據：
改善前：僅以角色判斷，無法細緻限制。
改善後：能以 operation 精準授權與拒絕。
改善幅度：合規性與最小權限落地。

Learning Points（學習要點）
核心知識點：RBAC 與 ABAC/operation-based 的差異、授權與角色的邏輯分離
技能要求：
必備技能：安全模型、Attribute 使用
進階技能：授權策略建模

延伸思考：可否結合資源屬性（ABAC）？如何導入審計？

Practice Exercise：為三個方法各自定義 operation 並驗證。
進階練習：為同一使用者賦與不同 operation 權限，逐一測試。
專案練習：把舊 RBAC 驗證改為 operation-based 管控。

Assessment Criteria：
功能完整性：授權規則正確攔阻/放行
程式碼品質：宣告式與集中設定
效能優化：授權查詢成本可控
創新性：與審計結合的設計


## Case #3: 以 Logging Handler 消滅樣板式記錄碼

### Problem Statement（問題陳述）
業務場景：營運要求所有服務方法需記錄呼叫軌跡與參數，過去在每個方法手寫 try-log，導致散落重複碼，且容易遺漏。
技術挑戰：如何用宣告式或集中設定的一次性機制，為所有方法統一加上記錄？
影響範圍：可維護性差、稽核資料不完整、除錯成本高。
複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏統一攔截點，無法自動注入記錄。
2. 重複樣板碼導致遺漏與不一致。
3. 記錄責任與商業邏輯耦合。

深層原因：
- 架構層面：缺乏橫切關注框架。
- 技術層面：未使用 Logging Handler。
- 流程層面：記錄政策未工程化落地。

### Solution Design（解決方案設計）
解決策略：透過 PIAB 的 Logging Handler，以 Attribute 或組態為目標方法注入呼叫前/後的記錄，維持商業方法乾淨。

實施步驟：
1. 啟用 Logging Handler
- 實作細節：在組態或以 Attribute 指定要記錄的方法與細節。
- 所需資源：PIAB、Logging AB
- 預估時間：0.5 天

2. 代理化物件、驗證紀錄
- 實作細節：PolicyInjection.Create/Wrap 讓攔截生效，驗證記錄輸出。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 示意：以 Attribute 標示需記錄（實際屬性名稱依版本/組態而異）
[/* LogCallHandler */]
public decimal GetBalance(string accountId) { /* ... */ }

// 關鍵：以 PIAB 代理呼叫
var svc = PolicyInjection.Create<AccountService>(new AccountService());
var balance = svc.GetBalance("A-001");
```

實際案例：文中列出「Logging Handler」作為可即用的加料項。
實作環境：.NET、C#、PIAB + Logging AB
實測數據：
改善前：多處重複 try-log；有遺漏。
改善後：記錄統一、覆蓋率提升。
改善幅度：維護與稽核品質明顯提升。

Learning Points：橫切關注解耦、宣告式記錄的落地
技能要求：C#、PIAB、記錄政策設計
延伸思考：敏感參數如何遮罩？失敗重試如何記錄？

Practice：為兩個方法啟用記錄並驗證輸出。
進階：為例外與慢呼叫加上不同級別的記錄。
專案：替整個應用的服務層導入統一記錄策略。

Assessment：
功能完整性：記錄覆蓋與正確性
程式碼品質：低侵入、清晰
效能：記錄開銷控制
創新性：記錄與稽核串接


## Case #4: Exception Handling Handler：集中化例外政策

### Problem Statement（問題陳述）
業務場景：各方法各自捕捉與處理例外，風格不一，導致錯誤訊息不一致、難追蹤與難以對外呈現一致錯誤模型。
技術挑戰：如何以集中政策決定記錄、包裝、重拋或轉換例外？
影響範圍：穩定性、可觀測性、客戶體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無統一政策與攔截點。
2. 方法內 try-catch 散落。
3. 記錄與轉譯行為不一致。

深層原因：
- 架構層面：缺少可組合的例外管線。
- 技術層面：未導入 Exception Handling Handler。
- 流程層面：例外分類與應對策略未制度化。

### Solution Design（解決方案設計）
解決策略：以 Exception Handling Handler 在攔截層集中化處理，統一記錄、分類、轉譯與重拋策略，讓業務方法保持精簡。

實施步驟：
1. 設計例外政策
- 實作細節：定義哪些例外需記錄/轉譯/重拋。
- 所需資源：Exception Handling Handler
- 預估時間：1 天

2. 代理與驗證行為
- 實作細節：以 PIAB 代理執行，模擬例外並驗證政策。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 示意：標記需套用例外處理（實際屬性依版本）
[/* ExceptionCallHandler */]
public void Transfer(string from, string to, decimal amount)
{
    // 模擬可能拋出的例外
}

// 代理
var svc = PolicyInjection.Create<TransferService>(new TransferService());
svc.Transfer("A", "B", 100m);
```

實際案例：文中列出「Exception Handling Handler」可即用。
實作環境：.NET、C#、PIAB
實測數據：
改善前：例外處理不一致。
改善後：集中化與一致化。
改善幅度：可觀測性與可維護性提升。

Learning Points：策略化例外處理、橫切與業務解耦
技能要求：例外分類、PIAB
延伸思考：與記錄、告警整合？

Practice：為兩類例外設計不同策略。
進階：依方法類型套用不同政策。
專案：建立組態驅動的例外處理中心。

Assessment：
功能完整性：策略正確應用
程式碼品質：簡潔
效能：攔截開銷合理
創新性：策略可配置化


## Case #5: Performance Counter Handler：方法級執行度量

### Problem Statement（問題陳述）
業務場景：營運方希望在 Windows PerfMon 觀察方法被呼叫次數等統計，不希望侵入每個方法加統計碼。
技術挑戰：以低侵入方式收集方法級別計數並可視化。
影響範圍：營運觀測、容量規劃。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無可攔截的統計注入點。
2. 自寫統計分散且易漏。
3. 缺少與 PerfMon 的標準整合。

深層原因：
- 架構層面：未導入統一度量機制。
- 技術層面：未使用 Performance Counter Handler。
- 流程層面：缺乏標準化指標定義。

### Solution Design（解決方案設計）
解決策略：用 Performance Counter Handler 在方法呼叫時自動戳 performance counter，透過 PerfMon 即可觀測。

實施步驟：
1. 啟用 Handler 與計數器
- 實作細節：建立/設定計數器，對目標方法啟用 Handler。
- 所需資源：PIAB
- 預估時間：0.5 天

2. 驗證 PerfMon
- 實作細節：以 PerfMon 觀察呼叫次數曲線。
- 所需資源：Windows PerfMon
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 示意：標記需度量的方法
[/* PerformanceCounterCallHandler */]
public void CloseAccount(string id) { /* ... */ }

var svc = PolicyInjection.Create<AccountService>(new AccountService());
svc.CloseAccount("A-001");
// 在 PerfMon 觀察對應計數器
```

實際案例：文中提及「呼叫時戳 perf counter，可在 performance monitor 觀察呼叫次數」。
實作環境：.NET、C#、PIAB、Windows PerfMon
實測數據：
改善前：無一致度量。
改善後：PerfMon 可觀察呼叫數。
改善幅度：可觀測性與營運透明度提升。

Learning Points：方法級度量、PerfMon 使用
技能要求：Windows PerfMon 基礎、PIAB
延伸思考：加入耗時直方圖？與 APM 整合？

Practice：為兩個方法加上呼叫計數。
進階：區分成功/失敗計數。
專案：建立服務層的標準化度量面板。

Assessment：
功能完整性：計數正確
程式碼品質：低侵入
效能：無明顯開銷
創新性：自訂更多指標


## Case #6: Caching Handler：讓慢方法命中快取即回傳

### Problem Statement（問題陳述）
業務場景：查詢或計算昂貴，重複參數的呼叫造成延遲與資源浪費。過去常手寫「查無快取就 insert」樣板碼。
技術挑戰：以宣告式與低侵入方式引入結果快取。
影響範圍：效能、成本、使用者體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 快取樣板碼重複、易錯。
2. 無統一快取策略與過期機制。
3. 無攔截點可共用快取邏輯。

深層原因：
- 架構層面：缺乏跨切快取框架。
- 技術層面：未導入 Caching Handler。
- 流程層面：快取生命周期不一致。

### Solution Design（解決方案設計）
解決策略：用 Caching Handler 在呼叫時先查快取，命中則直接回傳；未命中再執行與回存，移除方法內快取樣板碼。

實施步驟：
1. 設定快取策略
- 實作細節：定義鍵生成、過期時間、區分參數。
- 所需資源：PIAB
- 預估時間：1 天

2. 啟用攔截與驗證命中
- 實作細節：以 Attribute 或組態啟用 Handler，測試重複參數命中。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 示意：為昂貴查詢開啟快取
[/* CachingCallHandler */]
public Report GetMonthlyReport(int year, int month) { /* ...昂貴運算... */ }

var svc = PolicyInjection.Create<ReportService>(new ReportService());
var r1 = svc.GetMonthlyReport(2025, 8);
var r2 = svc.GetMonthlyReport(2025, 8); // 第二次命中快取直接回傳
```

實際案例：文中指出 Caching Handler 可使已在快取的結果直接回傳，且減少手寫「不在快取就 insert」的樣板碼。
實作環境：.NET、C#、PIAB
實測數據：
改善前：每次皆執行昂貴計算。
改善後：重複參數命中快取直接返回。
改善幅度：相同輸入的回應延遲大幅降低。

Learning Points：快取鍵、過期、命中策略
技能要求：快取與一致性概念、PIAB
延伸思考：快取與一致性衝突如何處理？參數序列化策略？

Practice：替慢查詢加上快取，驗證第二次命中。
進階：為不同參數組合設計鍵策略。
專案：為整個查詢層建立快取政策。

Assessment：
功能完整性：命中回傳正常
程式碼品質：移除樣板碼
效能：明顯縮短延遲
創新性：鍵與過期策略設計


## Case #7: Validation Handler：參數驗證宣告化

### Problem Statement（問題陳述）
業務場景：方法入口參數需校驗（非空、範圍、格式），過去在每個方法加防禦式程式碼，冗長且不一致。
技術挑戰：以宣告式統一參數驗證，避免業務方法膨脹。
影響範圍：可靠性、可讀性、維護性。
複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 重複手寫驗證導致不一致。
2. 缺乏集中化驗證與報錯機制。
3. 無攔截機制在進入點先驗證。

深層原因：
- 架構層面：未用 Validation Handler。
- 技術層面：驗證規則未宣告式化。
- 流程層面：驗證政策未標準化。

### Solution Design（解決方案設計）
解決策略：利用 Validation Handler 在方法前驗證參數，失敗即擋下，方法內不再重複寫防禦式程式。

實施步驟：
1. 宣告驗證規則
- 實作細節：以 Attribute 或規則定義參數限制。
- 所需資源：Validation Handler
- 預估時間：0.5 天

2. 代理化與驗證
- 實作細節：以 PIAB 代理生效，測試不合法參數被攔下。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 示意：為參數驗證啟用 Handler
[/* ValidationCallHandler */]
public void RegisterUser(string email, int age) { /* ... */ }

var svc = PolicyInjection.Create<UserService>(new UserService());
svc.RegisterUser("bad-email", -1); // 會在進入點被攔下
```

實際案例：文中列出 Validation Handler。
實作環境：.NET、C#、PIAB
實測數據：
改善前：參數驗證分散。
改善後：驗證集中、宣告式。
改善幅度：程式碼可讀性提升。

Learning Points：入口驗證、宣告式規則
技能要求：PIAB、驗證規則設計
延伸思考：本地化錯誤訊息？與 UI 驗證對齊？

Practice：替三個方法加上驗證。
進階：針對複合物件驗證。
專案：建立共用的驗證規則庫。

Assessment：
功能完整性：不合法輸入被攔阻
程式碼品質：清晰乾淨
效能：開銷可接受
創新性：規則可重用


## Case #8: 自訂 Pipeline Handler：插入專屬橫切邏輯

### Problem Statement（問題陳述）
業務場景：內建 Handler 無法涵蓋特定治理需求（如要求每次呼叫前注入相同追蹤 ID 或動態特判）。
技術挑戰：如何開發自訂攔截器並以宣告式方式套用？
影響範圍：治理能力、審計、可運維性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 需求超出內建 Handler 範疇。
2. 缺少在呼叫前/後執行自訂邏輯的機制。
3. 無可維護的注入點。

深層原因：
- 架構層面：需建立可插拔攔截鏈。
- 技術層面：未實作自訂 ICallHandler 與 Attribute。
- 流程層面：自訂邏輯未標準化套用。

### Solution Design（解決方案設計）
解決策略：擴充自訂 Call Handler 與對應 Attribute，透過 PIAB 攔截鏈執行，保持宣告式。

實施步驟：
1. 開發自訂 Handler 與 Attribute
- 實作細節：撰寫 ICallHandler（次序、前後邏輯）與繫結的 HandlerAttribute。
- 所需資源：PIAB
- 預估時間：1-2 天

2. 代理與驗證
- 實作細節：以 Attribute 套用到方法，並以代理驗證生效。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 示意：自訂 Handler（簡化）
public class TraceIdHandler : ICallHandler {
  public IMethodReturn Invoke(IMethodInvocation input, GetNextHandlerDelegate getNext) {
    // 前置：注入追蹤 ID
    // 呼叫下一個 Handler
    var result = getNext()(input, getNext);
    // 後置：記錄/清理
    return result;
  }
}

// 示意：套用自訂 Handler 的 Attribute
[/* TraceIdHandlerAttribute */]
public void AnyOperation() { /* ... */ }

// 代理呼叫
var svc = PolicyInjection.Create<AnyService>(new AnyService());
svc.AnyOperation();
```

實際案例：文中列出「Custom Pipeline Handlers」。
實作環境：.NET、C#、PIAB
實測數據：
改善前：特定治理邏輯散落。
改善後：以宣告式統一注入。
改善幅度：治理與稽核能力提升。

Learning Points：攔截鏈模型、Handler 開發
技能要求：PIAB 深入、設計模式（Proxy/Decorator）
延伸思考：Handler 順序管理、相依關係處理

Practice：開發一個注入追蹤 ID 的 Handler。
進階：建立兩個 Handler 並控制先後順序。
專案：為組織治理需求建立標準 Handler 套件。

Assessment：
功能完整性：自訂邏輯正確注入
程式碼品質：可維護、可配置
效能：攔截開銷可控
創新性：靈活的攔截鏈設計


## Case #9: Attribute 加了卻沒生效？關鍵在 Create/Wrap 代理

### Problem Statement（問題陳述）
業務場景：開發者在方法上標註了 Handler Attribute，但執行時毫無作用。
技術挑戰：找出為何 Attribute 不觸發攔截。
影響範圍：誤判框架不可用、延誤進度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 物件以 new 建立，未經 PIAB 代理。
2. 呼叫未通過攔截鏈。
3. 忽略 PIAB 的建立方式（Create/Wrap）。

深層原因：
- 架構層面：代理/攔截是必要條件。
- 技術層面：不理解 RealProxy 機制。
- 流程層面：缺乏導入規範。

### Solution Design（解決方案設計）
解決策略：統一改用 PolicyInjection.Create 或 Wrap 取得代理實例，所有對外可見呼叫都經過攔截鏈。

實施步驟：
1. 搜尋替換 new
- 實作細節：以 Create/Wrap 取代直接 new，或集中於工廠/DI 容器。
- 所需資源：PIAB
- 預估時間：0.5-1 天

2. 自動化檢查
- 實作細節：加入程式碼規範或靜態分析，避免遺漏。
- 所需資源：CI 工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 錯誤：直接 new 導致攔截不生效
var svc = new AccountService();

// 正確：以 PIAB 取得代理
var svc2 = PolicyInjection.Create<AccountService>(new AccountService());
// 或包裝既有物件
var svc3 = PolicyInjection.Wrap(new AccountService());
```

實際案例：文中明確指出「要透過 Create 或 Wrap」。
實作環境：.NET、C#、PIAB
實測數據：
改善前：Attribute 無效。
改善後：攔截生效。
改善幅度：功能按設計運作。

Learning Points：代理必要性
技能要求：C#、PIAB
延伸思考：與 DI/IoC 整合集中建立代理。

Practice：把一組類別建立改為代理。
進階：封裝工廠/DI 確保全域一致。
專案：導入靜態分析規則檢查 new 的使用。

Assessment：
功能完整性：攔截全數生效
程式碼品質：建立路徑一致
效能：無額外不必要代理
創新性：規範與工具化


## Case #10: 「在本機用 .NET Remoting」：理解 RealProxy 攔截模型

### Problem Statement（問題陳述）
業務場景：團隊對「為何不遠端也用到 .NET Remoting/RealProxy」存疑，影響採用。
技術挑戰：釐清 PIAB 底層攔截是以 RealProxy/Remoting 概念於本機實現。
影響範圍：認知落差造成抗拒或誤用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 認為 Remoting 僅用於遠端。
2. 不理解本機代理亦可攔截呼叫。
3. 忽略 PIAB 的設計是「本機使用 Remoting 概念」。

深層原因：
- 架構層面：代理與封送呼叫概念未普及。
- 技術層面：RealProxy 機制陌生。
- 流程層面：缺乏設計說明與培訓。

### Solution Design（解決方案設計）
解決策略：以設計說明與實作演示強化理解：PIAB 在本機以 RealProxy 包裹物件，呼叫經代理攔截，再還原呼叫至真實物件。

實施步驟：
1. 讀碼與示教
- 實作細節：展示攔截前後行為與堆疊。
- 所需資源：教學範例
- 預估時間：0.5 天

2. 驗證攔截點
- 實作細節：加上簡單 Handler 證明攔截。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 以代理呼叫觀察堆疊變化與攔截點
var svc = PolicyInjection.Create<DemoService>(new DemoService());
svc.DoWork(); // 在 Handler 中下中斷點觀察
```

實際案例：文中直言「它ㄨ的!! 原來只是在 Local 使用 .NET Remoting」。
實作環境：.NET、C#、PIAB
實測數據：
改善前：誤解技術機制。
改善後：掌握代理攔截概念。
改善幅度：採用阻力降低。

Learning Points：RealProxy、IMessage 攔截概念
技能要求：.NET 代理/反射基礎
延伸思考：此模型對序列化、跨 AppDomain 的影響？

Practice：以自訂 Handler 打印呼叫前/後訊息。
進階：在 Handler 中讀取方法資訊與參數。
專案：撰寫一份設計說明文件供團隊共用。

Assessment：
功能完整性：攔截證明充分
程式碼品質：簡潔清楚
效能：示例可量測
創新性：教學與觀測手法


## Case #11: 放棄手作 IMessageSink：用 PIAB 實現 AOP 實用化

### Problem Statement（問題陳述）
業務場景：曾研究過以 .NET Remoting 的 IMessage/IMessageSink 手作攔截，但過於繁瑣難落地，需求延宕。
技術挑戰：以可維護、可重用且低門檻方式實現 AOP 攔截。
影響範圍：開發效率、可靠性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手寫 Remoting 攔截樣板多且易錯。
2. 無統一可插拔 Handler 模型。
3. 測試與維護成本高。

深層原因：
- 架構層面：缺乏框架級 AOP 支援。
- 技術層面：Remoting 細節複雜。
- 流程層面：無標準工具鏈。

### Solution Design（解決方案設計）
解決策略：使用 PIAB 的攔截/Handler 機制，將 AOP 需求以 Handler 實作，降低門檻，提升可重用性。

實施步驟：
1. 將自製攔截切換到 Handler
- 實作細節：重寫為 ICallHandler/Attribute。
- 所需資源：PIAB
- 預估時間：1-2 天

2. 測試與文件化
- 實作細節：為 Handler 加單測與使用說明。
- 所需資源：測試框架
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 將原本 IMessageSink 方案改為 ICallHandler（見 Case #8 範式）
// 使用方式不變：以 Attribute 套用 + 代理呼叫
```

實際案例：文中描述過去 Remoting-based 方法很不實際，PIAB 讓作法可落地。
實作環境：.NET、C#、PIAB
實測數據：
改善前：攔截落地困難。
改善後：以 Handler 模型快速落地。
改善幅度：開發維護成本降低。

Learning Points：框架化 AOP 的優勢
技能要求：PIAB、單元測試
延伸思考：與其他 AOP 解法比較（如 PostSharp）

Practice：將既有攔截代碼重寫為 Handler。
進階：抽象共通輔助函式供 Handler 共用。
專案：建立組織級攔截器庫。

Assessment：
功能完整性：行為一致
程式碼品質：模組化、可測試
效能：攔截成本可接受
創新性：生產級落地方案


## Case #12: 最小侵入導入：只改建構方式就能插入行為

### Problem Statement（問題陳述）
業務場景：系統龐大，擔心導入新框架會大規模改動；希望最小侵入導入橫切行為。
技術挑戰：如何在不改業務方法的前提下，導入授權、記錄等？
影響範圍：改造風險、時程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 不理解 PIAB 只需改建立方式。
2. 高估導入改動範圍。
3. 缺乏注入點集中設計。

深層原因：
- 架構層面：缺少工廠/DI 集中化建立。
- 技術層面：對 Create/Wrap 機制不熟。
- 流程層面：導入策略未規劃。

### Solution Design（解決方案設計）
解決策略：以工廠或 DI 容器統一改為 PolicyInjection.Create/Wrap，方法本身只加 Attribute，達成最小侵入導入。

實施步驟：
1. 建立物件工廠
- 實作細節：集中建立服務的地方，改用 Create/Wrap。
- 所需資源：PIAB
- 預估時間：0.5 天

2. 漸進式導入
- 實作細節：先導入一層或一模組，逐步擴展。
- 所需資源：計畫與回歸測試
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
public static class ServiceFactory {
  public static T Create<T>(T impl) where T : class {
    return PolicyInjection.Create<T>(impl);
  }
}
var account = ServiceFactory.Create(new AccountService());
```

實際案例：文中強調「除了 Create 的方式不同，其它通通一樣」。
實作環境：.NET、C#、PIAB
實測數據：
改善前：預期大改。
改善後：僅改建立路徑與加 Attribute。
改善幅度：改造風險顯著降低。

Learning Points：導入策略、集中建立
技能要求：工廠/DI 設計
延伸思考：與 IoC 容器整合（例如在容器擴充點套用 Create）

Practice：為現有專案加入 ServiceFactory。
進階：把一層服務改走統一工廠。
專案：完成一個模組的漸進導入計畫與驗收。

Assessment：
功能完整性：攔截行為生效
程式碼品質：集中與一致
效能：無多餘代理
創新性：導入策略設計


## Case #13: 可觀測性落地：以 PerfMon 指標驗證導入成效

### Problem Statement（問題陳述）
業務場景：需要一個「可被營運觀測」的導入成效指標，而不僅是口頭描述。
技術挑戰：用具體指標呈現方法呼叫次數與行為。
影響範圍：決策與持續優化。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏可觀測指標。
2. 無法量化導入成效。
3. 稽核資料不一致。

深層原因：
- 架構層面：度量未工程化。
- 技術層面：未用 Performance Counter Handler。
- 流程層面：缺乏觀測流程。

### Solution Design（解決方案設計）
解決策略：啟用 Performance Counter Handler，將方法呼叫次數等輸出到 PerfMon，作為導入驗收與日常觀測依據。

實施步驟：
1. 為關鍵方法加指標
- 實作細節：套用 Handler，確認 PerfMon 可讀取。
- 所需資源：PIAB、PerfMon
- 預估時間：0.5 天

2. 建立儀表板與警報
- 實作細節：依指標建儀表板與基本告警。
- 所需資源：Windows/監控平台
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
[/* PerformanceCounterCallHandler */]
public void PayBill(string id) { /* ... */ }
// 攔截需用代理建立（同前案例）
```

實際案例：文中說明可用 PerfMon 觀測方法呼叫次數。
實作環境：.NET、C#、PIAB、PerfMon
實測數據：
改善前：無觀測數據。
改善後：PerfMon 可見呼叫曲線。
改善幅度：可量化驗收成效。

Learning Points：指標化驗收
技能要求：PerfMon、PIAB
延伸思考：把指標接到 APM/Logging 以統一觀測。

Practice：為兩個方法建立 PerfMon 觀測。
進階：加入 SLA/閾值警報。
專案：建立完整觀測儀表板。

Assessment：
功能完整性：指標輸出正確
程式碼品質：低侵入
效能：計數器開銷可控
創新性：觀測與治理結合


## Case #14: 安全範疇澄清：即便是 Admin 也可能被 ACL 拒絕

### Problem Statement（問題陳述）
業務場景：企業誤以為把使用者加進 Administrators 就可做所有事，忽略 ACL 規則仍可拒絕某些操作或資源。
技術挑戰：建立「角色≠授權」的正確安全模型，避免誤授權。
影響範圍：資安風險與合規。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 將角色當作萬能通行證。
2. 未定義資源或操作層級的授權。
3. 忽略 ACL 與操作授權的限制。

深層原因：
- 架構層面：安全模型過度簡化。
- 技術層面：未導入授權 Handler。
- 流程層面：權限稽核缺失。

### Solution Design（解決方案設計）
解決策略：導入 Authorization Handler，以 operation（或資源）為中心決定是否放行，補齊角色模型的不足，降低誤授權。

實施步驟：
1. 建立敏感操作清單
- 實作細節：明確需要授權的操作。
- 所需資源：Security AB
- 預估時間：1 天

2. 宣告式授權
- 實作細節：在敏感方法套用 AuthorizationCallHandler。
- 所需資源：PIAB
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
[AuthorizationCallHandler("op.file.deleteSensitive")]
public void DeleteSensitiveFile(string path) { /* ... */ }
```

實際案例：文中以 Windows ACL 舉例，說明角色不等於授權。
實作環境：.NET、C#、PIAB
實測數據：
改善前：角色即放行。
改善後：需符合操作授權才放行。
改善幅度：降低誤授權風險。

Learning Points：角色與授權的邏輯切分
技能要求：安全模型
延伸思考：審計與告警串接。

Practice：為三個敏感操作加授權。
進階：建立 deny 規則並測試。
專案：完成授權矩陣與測試用例。

Assessment：
功能完整性：正確攔阻未授權
程式碼品質：宣告清晰
效能：查詢成本可控
創新性：合規落地設計


## Case #15: 移除「資料不在快取就 insert」樣板：用 Caching Handler 收斂策略

### Problem Statement（問題陳述）
業務場景：系統中充斥「查快取→若無→執行→回存」樣板碼，增加維護負擔且策略不一致。
技術挑戰：以統一機制處理快取填充與回傳，避免業務層污染。
影響範圍：維護性、效能一致性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手寫快取流程冗長且分散。
2. 快取鍵與過期策略不一致。
3. 無法統一調整策略。

深層原因：
- 架構層面：未以 Handler 管理快取。
- 技術層面：未抽象鍵/過期策略。
- 流程層面：缺乏統一治理。

### Solution Design（解決方案設計）
解決策略：用 Caching Handler 承擔「命中即回傳、未命中執行後回存」的責任，方法內移除快取分支，統一策略於攔截層。

實施步驟：
1. 制定快取政策
- 實作細節：鍵規則、TTL、清除策略。
- 所需資源：PIAB
- 預估時間：1 天

2. 清理樣板碼
- 實作細節：移除方法內快取分支，交由 Handler 處理。
- 所需資源：重構工具/代碼評審
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
// 移除方法內 if(cache) 分支，改由 Handler 處理
[/* CachingCallHandler */]
public ProductDetail GetProduct(string id) { /* 僅實作資料取得 */ }

var svc = PolicyInjection.Create<ProductService>(new ProductService());
var p = svc.GetProduct("P-001"); // 未命中→取得→回存
var p2 = svc.GetProduct("P-001"); // 命中→直接回傳
```

實際案例：文中點名此類樣板碼的普遍性與可由 Caching Handler 取代。
實作環境：.NET、C#、PIAB
實測數據：
改善前：樣板分散且難改。
改善後：策略收斂、行為一致。
改善幅度：維護性與效能一致性顯著提升。

Learning Points：快取策略集中化
技能要求：重構、PIAB
延伸思考：與分散式快取/一致性策略整合。

Practice：重構三個含樣板碼的方法。
進階：實作依參數組合的鍵策略。
專案：建立全站快取政策與監控。

Assessment：
功能完整性：命中/未命中行為正確
程式碼品質：樣板碼清除
效能：一致且可預期
創新性：策略抽象與統一


--------------------------------
案例分類

按難度分類
- 入門級：Case 3, 5, 7, 9, 10, 12, 13
- 中級：Case 1, 2, 4, 6, 14, 15
- 高級：Case 8, 11

按技術領域分類
- 架構設計類：Case 1, 2, 8, 10, 11, 12, 14, 15
- 效能優化類：Case 5, 6, 13, 15
- 整合開發類：Case 3, 4, 6, 7, 8, 12, 15
- 除錯診斷類：Case 3, 4, 5, 10, 13
- 安全防護類：Case 1, 2, 14

按學習目標分類
- 概念理解型：Case 1, 2, 5, 7, 10, 13, 14
- 技能練習型：Case 3, 4, 6, 7, 9, 12, 15
- 問題解決型：Case 1, 2, 4, 6, 9, 11, 14
- 創新應用型：Case 8, 11, 15

案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 9（Create/Wrap 基礎）→ 確保攔截能生效
  - Case 10（理解 RealProxy 模型）→ 建立正確心智模型
- 進一步：
  - Case 1（CAS 限制與 PIAB 導入）→ 打通導入動機
  - Case 12（最小侵入導入策略）→ 制定導入路徑
- 橫切基礎能力：
  - Case 3（Logging）、Case 4（Exception）、Case 7（Validation）→ 建立常用橫切
- 效能與觀測：
  - Case 5（Perf Counter）→ 指標化
  - Case 13（PerfMon 驗收）→ 觀測體系
  - Case 6（Caching）→ 實質效能提升
  - Case 15（移除快取樣板）→ 策略收斂
- 安全深化：
  - Case 2（Operation-based 授權）
  - Case 14（角色≠授權的實務）
- 進階與擴展：
  - Case 11（將手作攔截遷移到 PIAB）
  - Case 8（自訂 Pipeline Handler）

依賴關係：
- Case 9 是多數案例的前置（代理建立）。
- Case 10 為概念前置，幫助理解所有攔截行為。
- Case 1 與 Case 12 為導入策略總綱，後續 Handler 案例（Case 3-7, 15）依賴此導入方式。
- Case 5 與 Case 13 串接，先啟用計數器，再用 PerfMon 觀測與驗收。
- Case 8 依賴已具備 Handler 使用經驗（Case 3/4/6/7 任一）。

完整學習路徑建議：
1) Case 9 → 10 → 1 → 12（建立代理與導入策略認知）
2) Case 3 → 4 → 7（完成常見橫切）
3) Case 5 → 13 → 6 → 15（建立觀測→快取效能→收斂樣板）
4) Case 2 → 14（安全深化到授權/ACL 實務）
5) Case 11 → 8（從替代舊攔截到自訂 Pipeline 擴展）

以上 15 個案例皆對應原文所提之問題、根因（CAS 限制、AOP 不實用、Local Remoting/RealProxy 攔截）、解法（PIAB 的 Create/Wrap + 各種 Handler）、與成效描述（授權前置、Log 注入、PerfMon 指標、快取命中即回傳、移除樣板碼）。各案例均附帶可實作步驟、示例碼與可評估重點，便於課程、專案實作與評量。