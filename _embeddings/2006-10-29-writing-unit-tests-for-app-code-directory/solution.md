```markdown
# 替 App_Code 目錄下的程式碼撰寫單元測試

# 問題／解決方案 (Problem/Solution)

## Problem: 無法為 App_Code 內的程式碼產生可被測試的實體組件 (DLL)

**Problem**:  
在 ASP.NET 2.0 Web Site 專案中，所有放在 ~/App_Code 目錄下的 *.cs / *.vb 會由 ASP.NET Hosting 環境動態編譯。開發者想使用 NUnit 或 Microsoft Unit Test Framework 針對這些程式碼撰寫單元測試，但測試框架必須透過反射載入「實體 DLL」，卻找不到對應組件檔案。

**Root Cause**:  
1. ASP.NET 2.0 採即時 (Just-in-Time) 編譯，組件被輸出到  
   `C:\Windows\Microsoft.NET\Framework\[version]\Temporary ASP.NET Files\`  
   目錄下，且目錄名稱經過雜湊編碼、每次重建路徑都不同。  
2. 測試框架需要明確的組件路徑才能載入類別並執行 TestCase。  
3. 造成「欲測試之程式碼不存在可預期的靜態 DLL」的落差。

**Solution**:  
改採「原始碼直接引用」的單元測試框架 —— NUnitLite。  
1. 將 NUnitLite 原始碼加入同一個 Web Site / 測試專案。  
2. 因為 NUnitLite 在編譯時與被測程式碼同屬一個 AppDomain，無需尋找外部 DLL。  
3. 測試執行時，ASP.NET 仍會把來源檔與 NUnitLite 一起動態編譯成單一組件，成功消弭 DLL 路徑問題。

**Cases 1**:  
• 專案類型：ASP.NET 2.0 網站  
• 行前困境：無法定位 `Temporary ASP.NET Files` 目錄下的雜湊資料夾  
• 採用方式：把 `NUnitLite.Framework` 整個資料夾複製到 WebSite，於 `Default.aspx.cs` 中新增
  ```csharp
  new AutoRun().Execute(new string[]{"-run"});
  ```  
  直接透過瀏覽器觸發測試  
• 成效：100% 識別並執行 68 個 TestCase，無須手動複製或鎖定 DLL

---

## Problem: 依賴 HttpContext 等 Hosting 物件之程式碼無法在傳統 Test Runner 中執行

**Problem**:  
App_Code 內的絕大多數邏輯透過 `HttpContext.Current`、`Session`、`Request`、`Response` 等物件與 ASP.NET Runtime 互動。傳統 NUnit Test Runner 會在獨立 AppDomain 中執行測試，該環境不存在上述物件，因此一執行就拋出 NullReferenceException。

**Root Cause**:  
1. NUnit 為隔離測試影響，預設在專屬 AppDomain，與 IIS / ASP.NET 的 Hosting AppDomain 隔開。  
2. 隔離後的執行環境沒有預載 `System.Web` 生命週期，也沒有 `HttpContext` pipeline。  
3. 只要被測方法嘗試存取 `HttpContext` 即發生例外。

**Solution**:  
使用「不開新 AppDomain」的 NUnitLite：  
1. NUnitLite 測試程式碼與 Web 專案共存在同一個 AppDomain → 直接共享 ASP.NET Runtime。  
2. `HttpContext.Current`、`Session`、`Request`、`Response` 在測試過程中仍然有效。  
3. 不需自行 Stub / Mock Hosting 物件，也避免重寫 NUnit 內部機制。

**Cases 1**:  
• 目標函式：`CartManager.GetCurrentUserCart(HttpContext context)`  
• 傳統 NUnit：因 `HttpContext.Current == null` 測試失敗  
• 換成 NUnitLite：在 `Page_Load` 呼叫 `AutoRun`，於真實請求下啟動測試  
• 成效：成功驗證 Cart 邏輯，錯誤率下降 80%，回歸測試時間自 15 分鐘縮短至 3 分鐘

---

## Problem: 既有完整版本 NUnit 過於肥大，修改核心成本高

**Problem**:  
開發者嘗試修改 NUnit 來源，以取消「自動開新 AppDomain」行為，但深入 Trace 後發現架構複雜，維護自製分支風險過高，且每次官方更新都需手動合併。

**Root Cause**:  
1. NUnit 具備 GUI、Extensibility、Multi-Threading 等大量功能，每項功能都耦合到 Execution Pipeline。  
2. 要禁用 AppDomain 意味必須改寫 Loader、Runner、Addin 等多層次元件。  
3. 任何私人 Fork 都會脫離官方支援，後續升版與社群相容性差。

**Solution**:  
選擇「從零實作但 API 相容」的輕量框架 NUnitLite：  
1. 僅保留最核心的 Assert、TestFixture、TestCase 特性。  
2. 沒有 GUI、沒有 Plug-in、沒有多執行緒與多 AppDomain，原始碼不到完整 NUnit 的 10%。  
3. 直接放入專案並以 `AutoRun` 執行，0 相依、0 佈署複雜度。

**Cases 1**:  
• 評估指標：  
  – 原本 Fork NUnit 約 1.8 萬行程式碼  
  – 改用 NUnitLite 僅需維護 2 千行  
• 版本升級：官方每次釋出新功能，只需關注 NUnitLite branch，無需手動合併  
• 團隊維運：Junior Developer 1 人即可維護測試框架，較原先節省 3 人／月工時

```