# 在 .NET 中以 Policy Injection Application Block 解決橫切性需求

# 問題／解決方案 (Problem/Solution)

## Problem: 無法在 Role-Based Security Attribute 之外插入自訂行為

**Problem**:  
在開發企業系統時，常希望透過 Attribute 宣告方式，於方法呼叫前後自動執行「授權、Log、額外驗證」等邏輯。雖然 .NET 內建的 `PrincipalPermission` Attribute 能做角色驗證，但若想在同一位置再插入自訂安全機制或記錄行為，就會碰到瓶頸。  

情境：  
‧ 需求－方法呼叫前先驗證使用者權限 → 通過後還要寫 Log、更新統計、或做快取。  
‧ 困難－即使另外宣告自訂 Attribute，也不會在執行時被觸發。  

**Root Cause**:  
`PrincipalPermission` 等安全 Attribute 的攔截邏輯是由 CLR 直接實作，屬於「框架層支援」。  
1. CLR 只針對內建幾種 Security Attribute 做 Demand 檢查。  
2. 開發者自行宣告的 Attribute 在 CLR 階段不會自動執行。  
3. 缺乏攔截點（Hook）導致無法於呼叫前/後插入額外程式碼。  

**Solution**:  
使用 Enterprise Library 的「Policy Injection Application Block (PIAB)」。  
1. 以 `PolicyInjection.Create<T>()` 或 `PolicyInjection.Wrap(obj)` 產生「加料過」的 Proxy 物件。  
2. 在目標類別或方法標註 CallHandler Attribute，例如：  

   ```csharp
   [AuthorizationCallHandler("operation-name")]
   [LogCallHandler]
   public void Deposit(decimal amount) { ... }
   ```  
3. PIAB 在 Proxy 內部其實就是用 `System.Runtime.Remoting.Proxies.RealProxy` 技術，於 `IMessageSink` 中插入自訂邏輯，因此即使只在本機程式也能做到攔截。  
4. 開發者可撰寫或組態指定自訂 `ICallHandler`，把「授權→Log→例外處理→效能計數」串成 Pipeline。  

此方法直接解決「無攔截點」的根因：它不倚賴 CLR 內建安全檢查，而是透過動態 Proxy 讓任何 Attribute 都能觸發對應 Handler。

**Cases 1**:  
背景：銀行核心系統需要在 `Transfer`、`Deposit` 等方法執行前做「RBAC + AML 日誌」紀錄。  
‧ 過去寫在業務邏輯內，維護困難。  
‧ 導入 PIAB 後，僅在方法上加二個 Attribute：`AuthorizationCallHandler` 與 `LogCallHandler`。  
效益：  
‧ 安全稽核程式集中於一支 `AMLLogHandler`，重新部署一次即可套用到數百支 Service Method。  
‧ 程式碼行數下降 30%，後續新功能零改動即可享有相同稽核機制。

---

## Problem: 想加入 Logging / Caching / Performance Counter 等橫切性需求，卻導致程式散落重複碼

**Problem**:  
大型 .NET 應用程式常需要：  
‧ 執行時間過久的方法加入結果快取 (Caching)。  
‧ 關鍵交易寫 Log 與 Exception Handling。  
‧ 蒐集效能指標寫入 Windows Performance Counter。  
若在每個方法手動插入 try-catch、Stopwatch、Cache 讀寫等程式碼，將造成：  
1. 重複碼大量散落。  
2. 易與商業邏輯糾纏，影響可讀性與維護。  

**Root Cause**:  
橫切性（Cross-cutting）關注點與核心業務邏輯耦合：  
1. 缺乏統一攔截框架 → 只能複製貼上。  
2. 先前嘗試 AOP／Remoting 架構過於笨重或和專案技術棧不相容，導致無法落地。  

**Solution**:  
再次利用 Policy Injection Application Block 提供的「現成 Call Handlers」：  
‧ Authorization Handler  
‧ Caching Handler  
‧ Exception Handling Handler  
‧ Logging Handler  
‧ Performance Counter Handler  
‧ Validation Handler  
‧ 及任何自訂 Handler  

只需：  
1. 於組態檔（或 Attribute）定義欲套用的 Handler Pipeline。  
2. 以 `PolicyInjection.Create` 取得物件後正常呼叫；或於 DI 容器註冊時即以 PIAB Wrap。  
3. PIAB 於 MethodInvoked → 前置/後置自動執行 Handler，將結果回傳給呼叫端。  

該方案能將重複碼完全抽離，並集中於 Handler；相依注入點只剩下 Proxy 建立處。  

**Cases 1**: Caching 加速  
‧ 報表服務每次查詢需 3~5 秒。  
‧ 啟用 `CachingCallHandler`（滑動到期 30 秒）後，命中率 85%，平均回應縮短至 0.2 秒。  

**Cases 2**: 效能計數統計  
‧ 以 `PerformanceCounterCallHandler` 統計 API 呼叫次數、平均耗時。  
‧ 運維團隊可直接用 PerfMon 監控，不必另外寫診斷程式。  

**Cases 3**: 例外集中處理  
‧ 透過 `ExceptionCallHandler`，所有服務層例外依策略轉為 FaultContract。  
‧ 系統每週未處理例外數由 120 降至 5，並在 Log 中自動帶入 CorrelationId 方便追蹤。