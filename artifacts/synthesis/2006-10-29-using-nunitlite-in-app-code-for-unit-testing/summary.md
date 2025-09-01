# 利用 NUnitLite, 在 App_Code 下寫單元測試

## 摘要提示
- 背景動機: 以實務需求為導向，將環境與組態檢查納入單元測試，協助多站點部署與非開發人員安裝。
- 工具選擇: 使用 NUnitLite 在 ASP.NET 2.0 Web Application 中執行測試，避開 NUnit 在 Web 情境的限制。
- 測試介面: 以 ASP.NET 頁面作為簡易 test runner，將 Console 輸出導向瀏覽器回應。
- 實作步驟: 透過五步驟完成 Web Site 建置、參考組件、Runner 頁面、TestFixture、部署與驗證。
- 測試內容: 範例測試包含 Session 啟用檢查與 temp folder 的存取權限檢測。
- 程式重點: Console.SetOut(Response.Output) 與 ConsoleUI.Main(new[] {"App_Code"}) 是關鍵呼叫。
- 部署驗證: 部署後先執行 Runner 檢視結果，快速驗證環境設定正確性。
- IE 相容性: IE 可能將 text/plain 當作 XML 顯示，可透過 View Source 檢視輸出。
- 與 NUnit 比較: NUnit 組件多、載入 App_Code 不便、建立 AppDomain 與獨立執行緒不利 Web 應用。
- 使用建議: 大型嚴謹專案用 NUnit；中小型 Web 應用用 NUnitLite 簡潔有效。

## 全文重點
文章示範在 ASP.NET 2.0 Web Application 中，使用 NUnitLite 於 App_Code 下撰寫並執行單元測試，將「部署環境與組態檢查」納入測試流程。作者指出多站點安裝、由非開發人員部署的情境常見，因此像 Session 啟用、暫存目錄是否存在與具備寫讀刪權限等環境正確性，值得在啟用前透過自動化測試快速驗證。雖然這些檢查可在系統初始化或透過 trace/assert 完成，但現實中常被忽略；善用既有測試框架能以低成本補強。

技術路徑上，NUnit 有 GUI/Console runner，但在 Web 環境不便；NUnitLite 沒有現成 runner，故以 ASP.NET 頁面自製簡易 runner。核心程式邏輯為將 Response 設為 text/plain，並用 Console.SetOut(Response.Output) 導向輸出，再呼叫 NUnitLite 的 ConsoleUI.Main 指向「App_Code」組件，使其自動掃描並執行 TestFixture。測試範例包含兩項：檢查 HttpContext.Current.Session 非空以確認 Session 啟用；讀取 web.config 的 temp-folder 設定，驗證資料夾存在，並以 File API 進行寫入、讀取比對、刪除，確保實際存取權限。

部署後，先瀏覽 NUnitLiteTestRunner.aspx 即可看到 Console 風格輸出（在 IE 可能被錯當 XML，改看原始碼可解）。將 web.config 刻意關閉 Session 可驗證測試能如預期失敗。作者並比較 NUnit 與 NUnitLite：NUnit 組件多、無法直接載入 App_Code、會嚴格建立 AppDomain 並以獨立執行緒執行，對 Web 應用不友善；相對地，NUnitLite 輕量、易整合到 Web 頁面流程，適合中小型或快速迭代的 Web 專案。結論是依專案規模選用工具：大型嚴謹專案可用 NUnit；簡潔的 Web 應用以 NUnitLite 更實用。

## 段落重點
### 背景與動機：將環境組態納入單元測試
作者延續先前介紹，從實務需求出發，強調 Web 應用常面臨多站點部署且由非工程師安裝的情境，導致組態錯誤常成問題。因此提議把「環境是否就緒」也當作單元測試的一部分。例如 Session 是否開啟、暫存目錄是否可用等，若能在啟用前自動化檢查，可降低風險、提升部署品質。雖然理論上可在初始化流程或以 trace/assert 處理，但在中小型專案往往未落實；既然有測試框架可用，就應順手把這類檢查納入，成本低、回饋快、實用性高。

### 工具與策略：選擇 NUnitLite 並以頁面作 Runner
NUnit 有 GUI/Console runner，但在 Web 情境使用並不便利；NUnitLite 輕量，適合嵌入 Web。由於 App_Code 最容易以 ASP.NET 頁面觸發執行，作者採用一個自製的 TestRunner 頁面：設定 Response 為純文字輸出，將 Console 輸出導向 Response，然後呼叫 NUnitLite 的 ConsoleUI.Main 指向 App_Code，便可在瀏覽器中得到類似 console 的測試結果。這種方式不需額外工具或主機設定，讓開發與部署現場能快速檢查。

### 實作流程 Step 1–3：建置專案與 Runner 頁面
- Step 1 建立 Web Site 專案（文中提供範例下載供參考）。
- Step 2 參考 NUnitLite.dll（需至官網下載原始碼自行編譯）。
- Step 3 撰寫 NUnitLiteTestRunner.aspx：在 Page_Load 設定 Response.ContentType = "text/plain"，以 Console.SetOut(Response.Output) 將輸出導至瀏覽器，最後呼叫 ConsoleUI.Main(new[] {"App_Code"})。此三步構成最小可行的 Web 測試執行器。頁面開啟即自動掃描 App_Code 下的 TestFixture 並執行，輸出即時顯示在瀏覽器中，達到零額外工具的運行體驗。

### 實作流程 Step 4：在 App_Code 撰寫測試
作者提供 ConfigurationTest 範例，含兩個測試：
- SessionEnableTest：透過 Assert.NotNull(HttpContext.Current.Session) 檢查 Session 是否啟用，快速發現 web.config 的 sessionState 設定是否正確。
- TempFolderAccessTest：從 ConfigurationManager.AppSettings["temp-folder"] 讀取暫存資料夾設定，依序驗證目錄存在、可寫入測試檔、可讀出且內容相符、可刪除不拋例外。此測試不僅檢查路徑存在，更實測 I/O 權限，能在部署環境提早暴露存取權限或目錄設定錯誤。

### 實作流程 Step 5：部署與驗證、IE 顯示問題
部署 Web 並調整組態後，先開啟 NUnitLiteTestRunner.aspx 檢視測試結果；若一切正確，會看到類似 console 的測試總結（Tests/Errors/Failures/Not Run）。作者指出 IE 可能無視 text/plain 將結果誤判為 XML 而報錯，遇到此情況可改用「檢視原始碼」查看輸出，不影響測試本身運作。也建議故意關閉 Session 以驗證測試的有效性，確保測試能在錯誤設定下確實失敗，提升對測試覆蓋與可靠度的信心。

### 與 NUnit 比較與建議：何時選 Nunit、何時選 NUnitLite
作者實測指出，用 NUnit 在 Web 環境執行測試的阻力較大：組件數量多、無法直接載入 App_Code、嚴格建立 AppDomain 與以獨立執行緒跑測試，這些特性在 Web 應用中可能導致相容性與行為差異問題，除非非常熟悉其影響，否則不建議。相對來說，NUnitLite 輕量、整合簡單，能直接在 Web 頁面中驅動測試，對中小型、快速迭代的 Web 專案相當實用。整體建議是：大型且需要高度嚴謹與隔離的專案採用 NUnit；一般 Web 應用可用 NUnitLite 以較低成本獲得足夠的測試與部署驗證能力。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 C# 與 .NET Framework 2.0 程式開發
   - ASP.NET Web Site 專案結構與 App_Code 的運作機制
   - 單元測試概念與 NUnit/NUnitLite 基本用法
   - 基本 I/O、設定讀取與 ASP.NET 生命週期（HttpContext/Session）

2. 核心概念：
   - 在 ASP.NET 中以 NUnitLite 執行單元測試：用自訂 ASPX 當作 test runner，讓瀏覽器直接看到測試結果
   - 把環境與設定檢查納入單元測試：例如 Session 是否啟用、temp 目錄是否可存取
   - 透過 Console 重導輸出到 HTTP 回應：Console.SetOut(Response.Output)，以文字輸出測試結果
   - 目標測試組件為 App_Code：ConsoleUI.Main(new[] {"App_Code"}) 掃描並執行測試
   - 選擇 NUnitLite 而非完整 NUnit：避開 AppDomain/執行緒隔離與多組件依賴，較適合輕量級 Web 情境

3. 技術依賴：
   - ASP.NET Page（System.Web.UI.Page）與 HttpContext/Session
   - NUnitLite ConsoleUI（測試發現與執行）
   - System.Configuration.ConfigurationManager 讀取 appSettings
   - System.IO（Directory/File/Path）進行檔案與目錄操作
   - 瀏覽器端輸出（Response.ContentType 設定、文字輸出）

4. 應用場景：
   - Web 應用需部署到多個網站或由非開發人員安裝，需快速驗證環境/設定是否正確
   - 在啟用系統前進行自檢（pre-flight check）
   - 輕量化的測試需求，不想引入完整 NUnit 執行架構
   - 臨時性/內部用測試頁面，快速回報測試結果

### 學習路徑建議
1. 入門者路徑：
   - 建立 ASP.NET Web Site 專案，新增 App_Code
   - 下載並建置 NUnitLite，加入引用
   - 建立 NUnitLiteTestRunner.aspx，設定 Response.ContentType 與 Console.SetOut
   - 在 App_Code 撰寫第一個 [TestFixture]/[Test]（例如簡單的 Assert.True）

2. 進階者路徑：
   - 撰寫與環境相關的測試：Session 啟用、目錄/檔案存取、必要 AppSettings 是否存在
   - 使用 SetUp/TearDown 管理測試資源（建立/清理暫存檔）
   - 結構化測試輸出與錯誤處理，改善可讀性
   - 了解 NUnit 與 NUnitLite 的差異與限制，選擇合適工具

3. 實戰路徑：
   - 在目標環境部署網站與設定（web.config 的 session、temp-folder）
   - 透過 NUnitLiteTestRunner.aspx 先行驗證各站台安裝是否合規
   - 發現問題時，透過測試失敗訊息快速定位（權限、路徑、設定鍵名）
   - 對測試頁加上存取保護或只在非生產環境啟用，避免曝露

### 關鍵要點清單
- 使用 NUnitLite 作為 Web 測試執行器: 以輕量化方式在 ASP.NET 中跑測試，避開完整 NUnit 的複雜依賴 (優先級: 高)
- 自訂 ASPX 當 Test Runner: 建立 NUnitLiteTestRunner.aspx，於 Page_Load 啟動 ConsoleUI.Main (優先級: 高)
- 重導 Console 輸出到 HTTP 回應: Console.SetOut(Response.Output) 讓測試結果顯示於瀏覽器 (優先級: 高)
- 設定純文字輸出: Response.ContentType = "text/plain" 以避免瀏覽器誤判格式 (優先級: 中)
- 指定掃描目標為 App_Code: ConsoleUI.Main(new[] {"App_Code"}) 掃描並執行該組件內測試 (優先級: 高)
- 在 App_Code 放置 TestFixture: Web Site 專案自動編譯 App_Code 供測試發現 (優先級: 中)
- 環境/設定即測試: 將 Session 啟用、目錄存取等納入單元測試流程 (優先級: 高)
- Session 檢查範例: Assert.NotNull(HttpContext.Current.Session) 驗證 Session 啟用 (優先級: 中)
- 檔案系統存取測試: 目錄存在、寫入/讀取/刪除檔案以驗證 temp 目錄權限 (優先級: 高)
- 設定讀取: 使用 ConfigurationManager.AppSettings["temp-folder"] 取得路徑 (優先級: 中)
- 部署前自檢流程: 上線前先執行 Runner 頁面確認環境正確 (優先級: 高)
- 瀏覽器相容性小問題: IE 可能誤判為 XML，必要時以檢視原始碼查看 (優先級: 低)
- 為何不用完整 NUnit: 多組件依賴、無法載入 App_Code、AppDomain/Thread 隔離不利於 Web 環境 (優先級: 中)
- 安全性與可見性: 測試頁僅於開發/測試環境或加保護避免外部存取 (優先級: 高)
- 建置取得 NUnitLite.dll: 自官方原始碼建置並加入引用 (優先級: 中)