# API & SDK Design #3 – API 的向前相容機制

# 問題／解決方案 (Problem/Solution)

## Problem: API 升版後舊版 SDK 無法繼續使用

**Problem**:  
在微服務環境中，API 維持「僅保留最新版本」的策略最能節省維運成本。但一旦開發人員修改或移除任何既有 API 介面 (method/parameter/URI)，所有仍在執行中的舊版 SDK 便可能產生「You shall NOT pass!」式的失效，大量使用者瞬間掛點。

**Root Cause**:  
1. RESTful API 天生缺少 WCF 那種 compile-time contract 檢查；開發者在 Controller 上「手癢」改了 signature，CI/CD 就把不相容的版本推上線。  
2. 團隊沒有明確的版本識別與向前相容政策，無從判斷「這次改動」能不能與舊版 SDK 共存。  

**Solution**:  
建構「三道檢查點」來保證 Compatible Versioning。  
a. API Contract：  
   • 以 `IApiContract` 標示所有對外介面 (例如 `IBirdsApiContract`)。  
   • 以 `ContractCheckActionFilter` 在 runtime 檢查 Controller 的公開 Method 必須出現在 Contract 介面中，違反即 throw `NotSupportedException`。  
b. 版本識別：  
   • 依 `major.minor.build.revision` 制定規則：Major 不相容、Minor 可向前相容 (只增不減)、Build/Revision 留給 Build Server 自動產生。  
   • 透過 AssemblyVersion 或硬碼字串「唯一」標示 API 版號。  
c. 相容性政策：  
   • 嚴格禁止「刪除或修改」既有介面，只能新增。  
   • 若非得不相容，必須提升 Major 版號，舊 SDK 透過檢查流程立即被阻擋。  

**Cases 1**:  
‒ 開發者誤把 `Get(string serialNo)` 改成 `Get(Guid id)`。CI 測試環節啟動 WebAPI，`ContractCheckActionFilter` 立即丟出 `NotSupportedException`，Build fail，問題在進 Production 前被攔截。  

**Cases 2**:  
‒ API 從 10.26 → 12.0 需刪除舊資源。Major 版號遞增。舊版 SDK 在初始化時比對 version 不符 (`10.x` vs `12.x`) 直接拋 `InvalidOperationException`，使用者得到明確訊息而非執行期 500 Error。

---

## Problem: SDK 在初始化時不知道 Server 的實際版本，無法事先判斷是否相容

**Problem**:  
Client 端安裝了某版 SDK，但只有文件告訴他「理論上支援」。若 Server 端早已升級到不相容的版本，SDK 直到第一次真正呼叫 API 時才會炸掉。

**Root Cause**:  
缺乏一條「正式管道」讓 SDK 啟動時就取得 Server 端 API 版號並做比對，導致不相容錯誤延遲到 runtime。

**Solution**:  
1. 在 Contract 內新增 `Options()` 行為 (或任何輕量資源)：  
   ```csharp
   interface IBirdsApiContract : IApiContract {
       string Options();      // 回傳 "10.26.0.0"
   }
   ```  
2. Controller 實做 `Options` 回傳版本字串。  
3. SDK `Client` 在 constructor 透過 `HttpClient` 發 OPTIONS 呼叫，取得 `_actual_API_version`，並與 `_require_API_version` 比對：  
   ```csharp
   if (required.Major != actual.Major) throw new InvalidOperationException();
   if (required.Minor >  actual.Minor) throw new InvalidOperationException();
   ```  
4. 不符即停止執行並回報清楚錯誤。

**Cases 1**:  
API 從 10.26 → 10.30 (Minor 增、相容)。舊 SDK (require 10.0) 取回 10.30，比對通過，繼續執行。  

**Cases 2**:  
API 升到 12.0。舊 SDK (require 10.0) 在建構過程取得 12.0；Major 不一致，自動丟出例外，開發者於啟動階段就能得知不相容。

---

## Problem: SDK 物件長時間存活，API 途中升版仍可能造成相容性問題

**Problem**:  
許多服務把 `SDK.Client` 實例緩存在 static 或 IoC Container，中途 Server 端可能已升級。若只在 SDK 建構時檢查一次版本，後續呼叫仍有失效風險。

**Root Cause**:  
版本檢查點只做在 SDK 初始化；缺少「每次呼叫時」的保護機制。  

**Solution**:  
1. SDK 於建構時把「最低需求版號」寫入所有 Request Header：  
   ```csharp
   _http.DefaultRequestHeaders.Add("X-SDK-REQUIRED-VERSION", _require_API_version.ToString());
   ```  
2. Server 端以 `SDKVersionCheckActionFilter` 於 Action 執行前：  
   • 讀 `X-SDK-REQUIRED-VERSION` → `required_version`  
   • 讀 AssemblyVersion → `current_version`  
   • 比對 Major / Minor，不符即 throw `InvalidOperationException`，並回傳 JSON 錯誤訊息。  

3. 因為在真正執行 Action 之前就檢查，避免「先執行不相容邏輯，再報錯」的浪費。  

**Cases 1**:  
‒ SDK 1.2 (要求 10.0) 長駐服務。一天後 API 熱昇級到 10.26 → 相容，`SDKVersionCheckActionFilter` 檢查通過，不影響線上服務。  

**Cases 2**:  
‒ API 再次升到 12.0。舊 SDK 每一次 Request 都會被 ActionFilter 擋下並回傳 JSON Error，服務層捕捉後可導向降級邏輯或提示使用者更新。  

**Cases 3**:  
‒ 同一集群同時跑 A/B 版本。Filter 讓 Server 可以根據 `required_version` 做動態路由 (ex: 支援舊版 Path、回傳降級資料)，大幅降低灰度發布風險。

---

## Problem: 團隊無法準確追蹤 API 何時、何人、改動了哪些介面

**Problem**:  
API 介面改動如果只靠「口頭 + 文件」，事後很難追查誰、在哪個 Commit 改壞相容性；也難以限制只有架構師可動 Contract。

**Root Cause**:  
缺乏「可追蹤且受權限控管」的 Contract 版本證據；REST Controller 直接被修改卻沒有 compile-time 防護。  

**Solution**:  
1. 以 Git 流程將 `*.Contract.cs` 或 `IApiContract` 介面獨立成專案/資料夾，並在 Repo 設定 CODEOWNERS，限制僅核心架構師可 Merge。  
2. CI Pipeline 內加入 Contract 對比工具或執行前述 `ContractCheckActionFilter` Unit Test，任何差異立即 Fail Build。  
3. 透過 Pull Request Review + Pipeline Report，自動生成「API 介面差異清單」，提供 PM、QA、文件人員統一追蹤。

**Cases 1**:  
三人小組同時開發。成員 A 提 PR 欲修改 `Birds/Get` 參數；Pipeline 因 Contract 破壞向前相容自動 Fail，並向 Slack 發警告。A 重新設計為新增新 API，整體向前相容性維持 100%。  

**Cases 2**:  
法遵掃描要求稽核 API 變動歷史。專案直接輸出 Contract 版本 Diff Report (由 Git 與工具生成)，滿足稽核文件需求，省下 80% 手動整理的時間。

---

# 備註  

• 範例完整程式碼皆收錄於 GitHub `andrew0928/SDKDemo`，可檢視 `dev-VER` 分支。  
• 下一篇將在「SDK 最佳化」過程中示範如何無縫進行 API 升版並驗證上述機制的可靠性。