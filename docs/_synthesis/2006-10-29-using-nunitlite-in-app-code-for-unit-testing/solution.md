---
layout: synthesis
title: "利用 NUnitLite, 在 App_Code 下寫單元測試"
synthesis_type: solution
source_post: /2006/10/29/using-nunitlite-in-app-code-for-unit-testing/
redirect_from:
  - /2006/10/29/using-nunitlite-in-app-code-for-unit-testing/solution/
postid: 2006-10-29-using-nunitlite-in-app-code-for-unit-testing
---

以下為基於文章內容，萃取並擴展的 15 個可落地的問題解決案例，皆包含問題、根因、方案、實作示例與可評估的學習與實作指引。

## Case #1: 在 ASP.NET Web Site 內嵌一個 NUnitLite 測試執行器頁面

### Problem Statement（問題陳述）
- 業務場景：團隊主要開發 ASP.NET 2.0 Web 應用，常需要在多個站台部署。安裝人員不一定懂程式，導致部署後要快速驗證配置是否正確成為痛點。希望能在網站內放置一個可一鍵執行的測試頁，於上線前自動檢查關鍵環境與設定，避免功能初始化後才發現設定錯誤。
- 技術挑戰：NUnitLite 沒有內建 GUI/Console runner 且 Web Site 的 App_Code 為動態編譯，需在 Web 內部自行建立測試執行與結果呈現。
- 影響範圍：部署驗證、啟動前健康檢查、跨站台一致性與安裝體驗。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. NUnitLite 無 GUI/Console runner 可直接用在 Web 應用中。
  2. ASP.NET Web Site 的測試類別在 App_Code，需於執行時動態載入並執行。
  3. 瀏覽器僅能接收 HTTP 回應，Console 輸出需導回 Response。
- 深層原因：
  - 架構層面：網站執行脈絡與一般主控台程式差異，缺少現成執行容器。
  - 技術層面：NUnitLite 以 ConsoleUI 為主，需自行包裝為 Web 入口。
  - 流程層面：缺少部署後自動驗證機制，常仰賴人工檢查。

### Solution Design（解決方案設計）
- 解決策略：在網站建立 NUnitLiteTestRunner.aspx，於 Page_Load 設定回應為純文字、把 Console 輸出導向 Response，並以 ConsoleUI.Main 指定掃描 App_Code，達成「一鍵從瀏覽器執行並顯示測試結果」的能力。

- 實施步驟：
  1. 建立 Web Site 專案
     - 實作細節：新建 ASP.NET 2.0 Web Site 專案。
     - 所需資源：Visual Studio、.NET Framework 2.0。
     - 預估時間：0.5 小時
  2. 引用 NUnitLite.dll
     - 實作細節：從官方下載原始碼自建 dll 並引用。
     - 所需資源：NUnitLite 原始碼、MSBuild/VS。
     - 預估時間：0.5 小時
  3. 建立測試執行頁
     - 實作細節：在 Page_Load 設定 ContentType、導向 Console 輸出、執行 ConsoleUI。
     - 所需資源：ASP.NET。
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```csharp
// NUnitLiteTestRunner.aspx.cs
public partial class NUnitLiteTestRunner : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        Response.Clear();
        Response.ContentType = "text/plain"; // 以純文字輸出結果
        Console.SetOut(Response.Output);      // 導向 Console 輸出至 HTTP Response

        // 指定掃描 App_Code 下已動態編譯的測試型別
        ConsoleUI.Main(new string[] { "App_Code" });
        Response.End();
    }
}
```

- 實際案例：文中提供的 NUnitLiteTestRunner.aspx，瀏覽器開啟即可看到 Console runner 輸出。
- 實作環境：ASP.NET 2.0、.NET 2.0.50727.42、NUnitLite 0.1.0、Windows XP SP2。
- 實測數據：
  - 改善前：無自動化頁面可執行測試
  - 改善後：可一鍵顯示「NUnitLite version…」「2 Tests : 0 Errors, 0 Failures」
  - 改善幅度：部署驗證時間由人工數十分鐘降低為數秒（示例）

Learning Points（學習要點）
- 核心知識點：
  - 在 Web 環境中包裝 Console runner 的做法
  - ASP.NET Response 與 Console 輸出的轉接
  - App_Code 動態編譯與測試探索
- 技能要求：
  - 必備技能：ASP.NET 頁面生命週期、基本 C#
  - 進階技能：測試框架整合與回應管線掌握
- 延伸思考：
  - 可否改為 HttpHandler/Minimal API 以更輕量呈現？
  - 高併發存取時是否需限流或加權？
  - 是否需加上權限保護與審計？
- Practice Exercise（練習題）
  - 基礎練習：建立一個 Runner 頁面並能顯示「0 Tests」摘要（30 分鐘）
  - 進階練習：加入 2 個示範測試並觀察輸出摘要變化（2 小時）
  - 專案練習：製作可選擇測試分類/過濾關鍵字的 Runner 頁（8 小時）
- Assessment Criteria（評估標準）
  - 功能完整性（40%）：可正確執行測試並輸出摘要
  - 程式碼品質（30%）：結構清晰、錯誤處理完善
  - 效能優化（20%）：最小化額外資源消耗
  - 創新性（10%）：支援過濾、下載報告等附加功能

---

## Case #2: 在 App_Code 中自動發現並執行測試

### Problem Statement（問題陳述）
- 業務場景：Web Site 專案的程式碼與測試類型放於 App_Code，動態編譯為匿名組件。需要讓測試執行器在不明確指定 DLL 名稱的情況下掃描並執行所有測試，減少部署時的組件管理與設定負擔。
- 技術挑戰：大多數測試執行工具依賴靜態組件名稱；App_Code 為動態組件，必須以特定方式讓 runner 能正確定位與探索測試。
- 影響範圍：測試發現、部署簡化、跨環境穩定性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. App_Code 由 ASP.NET 動態編譯，無固定檔名。
  2. 測試探索器常假定輸入為已命名的 DLL。
  3. Web Site 非 Web Application 專案，編譯模式不同。
- 深層原因：
  - 架構層面：Web 站台的動態編譯機制與一般組件發行差異。
  - 技術層面：Runner 的輸入參數需支援「邏輯組件」識別。
  - 流程層面：開發/部署未統一標準化測試載入流程。

### Solution Design（解決方案設計）
- 解決策略：在 ConsoleUI.Main 傳入 "App_Code" 作為需要掃描的目標，讓 NUnitLite 於執行時透過該邏輯名稱載入並探索測試。

- 實施步驟：
  1. 調整 Runner 參數
     - 實作細節：ConsoleUI.Main(new[] { "App_Code" });
     - 所需資源：NUnitLite
     - 預估時間：10 分鐘
  2. 驗證探索
     - 實作細節：加入至少一個 TestFixture，確認摘要顯示非 0 測試。
     - 所需資源：ASP.NET、C#
     - 預估時間：20 分鐘

- 關鍵程式碼/設定：
```csharp
// 指定 App_Code 為探索目標
ConsoleUI.Main(new string[] { "App_Code" });
```

- 實際案例：文中 Runner 以 "App_Code" 為參數，成功執行 2 項測試。
- 實作環境：ASP.NET 2.0 / NUnitLite 0.1.0。
- 實測數據：
  - 改善前：需手動定位組件或無法執行
  - 改善後：自動探索 App_Code 測試，顯示「2 Tests…」
  - 改善幅度：探索設定工作量近乎 0

Learning Points（學習要點）
- 核心知識點：App_Code 動態編譯與邏輯組件名稱；Runner 參數使用
- 技能要求：
  - 必備技能：C#、ASP.NET 編譯模型
  - 進階技能：測試探索原理
- 延伸思考：如何跨多資料夾或命名空間篩選？如何只跑特定分類？
- Practice Exercise：新增第三個測試類，驗證摘要顯示 3 Tests（30 分鐘）；擴充 Runner 支援含關鍵字的篩選（2 小時）；做一個帶篩選 UI 的 Runner（8 小時）
- Assessment Criteria：正確探索（40%）；程式碼結構（30%）；可維運性（20%）；擴充性（10%）

---

## Case #3: 將 Console 輸出導向瀏覽器以顯示測試結果

### Problem Statement（問題陳述）
- 業務場景：為了讓非技術安裝人員能快速讀取測試結果，需把測試框架的 Console 輸出轉成瀏覽器可讀的 HTTP 回應，達成無需命令列或工具的即時檢視。
- 技術挑戰：Console.Write 既定輸出至標準輸出，HTTP 回應需要透過 Response 流送；需建立輸出轉接。
- 影響範圍：測試可讀性、驗證效率、支援人員操作成本。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 測試框架預設輸出至 Console。
  2. 瀏覽器不會顯示標準輸出，只讀取 HTTP Response。
  3. 預設 ContentType 若不正確，格式會出錯。
- 深層原因：
  - 架構層面：I/O 通道不同步。
  - 技術層面：需用 Console.SetOut 導向 TextWriter。
  - 流程層面：缺少標準化的輸出轉接作法。

### Solution Design（解決方案設計）
- 解決策略：在 Page_Load 設定 Response.ContentType 為 text/plain，並以 Console.SetOut(Response.Output) 轉接輸出，確保所有 Console 寫入都能被瀏覽器收到。

- 實施步驟：
  1. 設定 ContentType
     - 實作細節：Response.ContentType = "text/plain";
     - 所需資源：ASP.NET
     - 預估時間：5 分鐘
  2. 輸出轉接
     - 實作細節：Console.SetOut(Response.Output);
     - 所需資源：.NET
     - 預估時間：5 分鐘

- 關鍵程式碼/設定：
```csharp
Response.ContentType = "text/plain";
Console.SetOut(Response.Output);
```

- 實際案例：文中 Runner 採此法輸出完整測試摘要至瀏覽器。
- 實作環境：ASP.NET 2.0
- 実測數據：
  - 改善前：瀏覽器無輸出或格式錯亂
  - 改善後：可讀純文字測試結果
  - 改善幅度：輸出可讀性大幅提升（質化）

Learning Points（學習要點）
- 核心知識點：Console 輸出導向；HTTP ContentType
- 技能要求：ASP.NET Response 管線、C# I/O
- 延伸思考：是否需同時寫檔留存（多目標 TextWriter）？
- Practice：將輸出同時寫入檔案（30 分鐘）／封裝一個 MultiTextWriter（2 小時）／製作下載結果的 API（8 小時）
- Assessment Criteria：正確輸出（40%）；代碼簡潔（30%）；可擴充（20%）；創意（10%）

---

## Case #4: 解決 IE 將 text/plain 誤判為 XML 的顯示問題

### Problem Statement（問題陳述）
- 業務場景：安裝人員在 IE 開啟測試頁時，雖已設為 text/plain，IE 仍以 XML 詮釋並報錯，導致無法直接閱讀測試結果，需要替代閱讀方式或改善標頭避免誤判。
- 技術挑戰：IE 內容嗅探機制可能忽略宣告的 MIME，需正確設置防嗅探與輸出格式以避免誤判。
- 影響範圍：測試可讀性、現場操作效率、支援成本。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. IE 可能執行 MIME 嗅探，忽略 ContentType。
  2. 回應內容格式被誤分析為 XML。
  3. 未設定禁嗅探標頭或其他相容性標頭。
- 深層原因：
  - 架構層面：不同瀏覽器對 MIME 的處理差異。
  - 技術層面：HTTP 標頭設定不足。
  - 流程層面：未考量前端相容性測試。

### Solution Design（解決方案設計）
- 解決策略：在回應加上 X-Content-Type-Options: nosniff，必要時加 Content-Disposition 與明確字元編碼，或提供「檢視原始碼」提示作為備援。

- 實施步驟：
  1. 加強標頭
     - 實作細節：Response.AddHeader("X-Content-Type-Options","nosniff");
     - 所需資源：ASP.NET
     - 預估時間：10 分鐘
  2. 明確呈現
     - 實作細節：可加上 Content-Disposition inline; filename=result.txt
     - 所需資源：ASP.NET
     - 預估時間：10 分鐘

- 關鍵程式碼/設定：
```csharp
Response.ContentType = "text/plain";
Response.AddHeader("X-Content-Type-Options", "nosniff");
Response.AddHeader("Content-Disposition", "inline; filename=\"nunitlite-result.txt\"");
```

- 實際案例：文中建議若 IE 誤判，改以「檢視原始碼」閱讀；此方案提供更穩健的自動化修正。
- 實作環境：ASP.NET 2.0 + IE
- 實測數據：
  - 改善前：IE 當作 XML 開啟並報錯
  - 改善後：以純文字正常顯示或可下載
  - 改善幅度：可讀性問題消失（質化）

Learning Points（學習要點）
- 核心知識點：MIME 嗅探、防嗅探標頭
- 技能要求：HTTP 標頭處理
- 延伸思考：是否提供 HTML 呈現版本以便閱讀？
- Practice：提供「純文字/HTML」雙模式切換（30 分鐘/2 小時），加入下載按鈕（8 小時）
- Assessment：相容性（40%）；易用性（30%）；健壯性（20%）；創意（10%）

---

## Case #5: 使用單元測試驗證 Session 狀態已啟用

### Problem Statement（問題陳述）
- 業務場景：多站台部署中，有環境可能因 web.config 設定或 IIS 設定導致 Session 未啟用，進而影響使用者狀態管理與登入流程。希望在上線前用測試快速驗證 Session 可用性。
- 技術挑戰：在測試中取得 HttpContext 並確認 Session 已初始化且非 null。
- 影響範圍：登入流程、購物車、使用者設定等需 Session 的功能。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. web.config 中 sessionState 關閉或設定錯誤。
  2. 頁面/路由設定未啟用 Session。
  3. 測試若於非同 AppDomain/Thread 執行，HttpContext 不存在。
- 深層原因：
  - 架構層面：Session 管理依賴 HTTP 與應用程式狀態。
  - 技術層面：Runner 需與網站同脈絡執行。
  - 流程層面：缺少環境驗證清單。

### Solution Design（解決方案設計）
- 解決策略：以 NUnitLite 測試在 Web 環境內執行，直接 Assert HttpContext.Current.Session 非 null，快速暴露 Session 設定問題。

- 實施步驟：
  1. 寫測試
     - 實作細節：Assert.NotNull(HttpContext.Current.Session);
     - 所需資源：NUnitLite、C#
     - 預估時間：10 分鐘
  2. 驗證環境
     - 實作細節：切換 web.config session 設定觀察通過/失敗
     - 所需資源：IIS/開發伺服器
     - 預估時間：20 分鐘

- 關鍵程式碼/設定：
```csharp
[Test]
public void SessionEnableTest()
{
    Assert.NotNull(HttpContext.Current.Session); // Session 應已啟用且可用
}
```

- 實際案例：文中藉由關閉 web.config 的 session 後測試失敗，驗證測試有效。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：Session 狀態問題上線後才發現
  - 改善後：測試立即失敗回報
  - 改善幅度：風險提前暴露（質化）

Learning Points（學習要點）
- 核心知識點：Session 初始化時機、HttpContext 使用
- 技能要求：ASP.NET sessionState 設定
- 延伸思考：跨進程 Session（StateServer/SQL）如何驗證？
- Practice：加入 Session 寫讀測試（30 分鐘），測不同模式（2 小時），完整 Session 健康檢查（8 小時）
- Assessment：覆蓋充分（40%）；穩健性（30%）；效能（20%）；創新（10%）

---

## Case #6: 以單元測試驗證暫存資料夾存在與可讀寫刪

### Problem Statement（問題陳述）
- 業務場景：系統依賴 appSettings["temp-folder"] 指定暫存路徑，部署時常因目錄不存在或權限不足導致功能失敗。希望透過測試自動檢查該目錄是否存在且具備寫入、讀取與刪除能力。
- 技術挑戰：在 Web 環境中執行檔案 I/O 測試並回報明確錯誤訊息。
- 影響範圍：檔案上傳、報表匯出、影像處理等功能。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未建立目錄或配置錯誤。
  2. 應用程式帳號無存取權限。
  3. 設定鍵名錯誤導致取值為 null。
- 深層原因：
  - 架構層面：I/O 相依於部署環境。
  - 技術層面：權限與錯誤處理不足。
  - 流程層面：缺少部署後檢查清單。

### Solution Design（解決方案設計）
- 解決策略：撰寫測試檢查目錄存在性，寫入暫存檔、讀回比對、刪除並驗證操作無例外；若鍵值缺失，回報明確錯誤。

- 實施步驟：
  1. 檢查存在性
     - 實作細節：Assert.True(Directory.Exists(path));
     - 所需資源：System.IO
     - 預估時間：10 分鐘
  2. 寫讀刪驗證
     - 實作細節：File.WriteAllText/ReadAllText/Delete
     - 所需資源：System.IO
     - 預估時間：20 分鐘

- 關鍵程式碼/設定：
```csharp
[Test]
public void TempFolderAccessTest()
{
    var path = ConfigurationManager.AppSettings["temp-folder"];
    Assert.False(string.IsNullOrEmpty(path), "appSettings['temp-folder'] 未設定");
    Assert.True(Directory.Exists(path), "暫存資料夾不存在");

    var file = Path.Combine(path, "test.txt");
    var content = "12345";
    File.WriteAllText(file, content);              // 可寫
    Assert.AreEqual(File.ReadAllText(file), content); // 可讀且一致
    File.Delete(file);                             // 可刪
}
```

- 實際案例：文中示例即此，成功於部署前檢查。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：I/O 問題上線後才爆出
  - 改善後：測試即時發現配置/權限問題
  - 改善幅度：缺陷前移（質化）

Learning Points（學習要點）
- 核心知識點：I/O 權限、應用程式身分、appSettings 讀取
- 技能要求：檔案系統 API、配置管理
- 延伸思考：大檔/鎖檔情境如何測？
- Practice：加入建立目錄與 ACL 設定腳本（2 小時）；建 I/O 壓力測（8 小時）
- Assessment：測試完整性（40%）；清晰錯誤訊息（30%）；健壯性（20%）；創意（10%）

---

## Case #7: 部署前的配置自檢頁（Pre-flight Check）流程

### Problem Statement（問題陳述）
- 業務場景：產品需安裝到多個站台，安裝人員不一定懂程式。若無標準化「啟用前自檢」流程，配置問題常延後到使用者操作時才被發現。需要一個可指引安裝人員的自檢頁流程，集中執行關鍵測試。
- 技術挑戰：將多個環境測試整合成一鍵執行並易讀的輸出，並提供失敗時的明確指引。
- 影響範圍：部署品質、回報效率、支援成本。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺乏標準化自檢頁。
  2. 測試分散，無整體摘要。
  3. 非技術人員缺乏判讀指引。
- 深層原因：
  - 架構層面：未預留可觀測性機制。
  - 技術層面：測試輸出未友善呈現。
  - 流程層面：部署清單與驗證缺失。

### Solution Design（解決方案設計）
- 解決策略：以 Runner 頁整合 Session、暫存目錄等測試，顯示摘要與建議處理方式，形成標準部署自檢步驟。

- 實施步驟：
  1. 集中測試
     - 實作細節：將配置檢查測試集中於 App_Code/Tests
     - 所需資源：NUnitLite
     - 預估時間：1 小時
  2. 說明指引
     - 實作細節：在頁面加上「如何解讀輸出」簡述
     - 所需資源：ASPX
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```csharp
// 可在頁面加上簡述（文字或連結）說明如何處理常見失敗項目
// 例如：Session 失敗 -> 檢查 web.config <sessionState>
// 暫存資料夾失敗 -> 建立目錄並賦予應用程式帳號寫入權
```

- 實際案例：文中步驟 Step 5 即建議啟用前先點 Runner 頁檢查。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：無自檢流程
  - 改善後：「2 Tests : 0 Errors, 0 Failures」清楚回饋
  - 改善幅度：部署失誤顯著下降（質化）

Learning Points（學習要點）
- 核心知識點：部署自檢設計、測試摘要判讀
- 技能要求：測試組織化、文件化指引
- 延伸思考：是否接入報警或記錄？
- Practice：加入更多配置檢查（30 分鐘/2 小時）；寫一份自檢 SOP（8 小時）
- Assessment：覆蓋率（40%）；可讀性（30%）；可操作性（20%）；創新（10%）

---

## Case #8: 為什麼選擇 NUnitLite 而非 NUnit 於 Web 應用

### Problem Statement（問題陳述）
- 業務場景：團隊嘗試用 NUnit 跑 Web Site 測試，遇到 App_Code 無法載入、組件相依多、獨立 AppDomain 與 Thread 導致 HttpContext/Session 等 Web 相依無法使用的問題。需要評估改用 NUnitLite。
- 技術挑戰：在 Web 環境內讓測試與網站同脈絡執行，避免 AppDomain/Thread 隔離副作用。
- 影響範圍：測試可行性、穩定性、維運成本。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. NUnit 組件較多，部署複雜。
  2. 無法直接載入 App_Code 動態組件。
  3. 預設以分離 AppDomain/Thread 執行。
- 深層原因：
  - 架構層面：NUnit 設計以獨立執行為主。
  - 技術層面：Web 相依上下文無法跨域穿透。
  - 流程層面：測試工具選型與場景不合。

### Solution Design（解決方案設計）
- 解決策略：在 Web 應用中選用輕量的 NUnitLite，以 Runner 頁同域執行，簡化相依與提升相容性。

- 實施步驟：
  1. 替換框架
     - 實作細節：移除 NUnit 相依，引入 NUnitLite
     - 所需資源：NUnitLite
     - 預估時間：1 小時
  2. 建 Runner
     - 實作細節：Case #1 的 Runner 頁
     - 所需資源：ASP.NET
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```csharp
// 保持同 AppDomain/Thread 的簡單做法：在 ASP.NET 頁面中直接呼叫
ConsoleUI.Main(new string[] { "App_Code" });
```

- 實際案例：文中點出 NUnit 的限制並推薦在 Web 場景採用 NUnitLite。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：NUnit 無法載入 App_Code、上下文丟失
  - 改善後：NUnitLite 正常執行、可用 HttpContext/Session
  - 改善幅度：相容性顯著提升（質化）

Learning Points（學習要點）
- 核心知識點：測試框架選型與場景契合
- 技能要求：理解 AppDomain/Thread 模型
- 延伸思考：何時仍應選擇 NUnit（大型專案、CI）？
- Practice：以兩者各實作一次對比（2 小時）；撰寫選型建議（8 小時）
- Assessment：論證完整（40%）；實證對比（30%）；可行性（20%）；洞察（10%）

---

## Case #9: 從原始碼建置並引用 NUnitLite.dll

### Problem Statement（問題陳述）
- 業務場景：NUnitLite 提供原始碼，需要自行建置 dll 並在 Web Site 中引用，確保相依輕量與可控版本。
- 技術挑戰：取得對應 .NET 版本的可用組件，並納入專案參考。
- 影響範圍：相依性管理、部署體積、版本一致性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 需手動從原始碼建置。
  2. 版本需與 .NET 2.0 相容。
  3. 發佈流程需納入第三方組件管理。
- 深層原因：
  - 架構層面：自建以控管相依。
  - 技術層面：建置工具、設定。
  - 流程層面：依賴管理策略未落地。

### Solution Design（解決方案設計）
- 解決策略：下載官方原始碼，使用 VS 或 MSBuild 編譯，將生成的 NUnitLite.dll 加入 Web Site 參考並檢入版本控管。

- 實施步驟：
  1. 下載與建置
     - 實作細節：開啟解決方案，針對 .NET 2.0 編譯
     - 所需資源：VS/MSBuild
     - 預估時間：0.5 小時
  2. 導入專案
     - 實作細節：Bin 夾放置 dll、加入參考
     - 所需資源：ASP.NET
     - 預估時間：10 分鐘

- 關鍵程式碼/設定：
```
// 建置流程（示意）：以 VS 開啟 -> 設定 .NET 2.0 -> Build -> 取得 NUnitLite.dll
// 將 NUnitLite.dll 放入 WebSite/bin，於專案中加入參考
```

- 實際案例：文中 Step 2 指示自行下載並建置。
- 實作環境：.NET 2.0、NUnitLite 0.1.0
- 實測數據：
  - 改善前：無可用組件
  - 改善後：可在 Web Site 中引用並執行
  - 改善幅度：完成基本相依管理（質化）

Learning Points（學習要點）
- 核心知識點：第三方原始碼建置與引用
- 技能要求：VS/MSBuild 基本能力
- 延伸思考：要不要封裝 NuGet（較新平台）？
- Practice：寫一份建置腳本（2 小時）；產出版本控管策略（8 小時）
- Assessment：可重現性（40%）；文件完整（30%）；流程簡潔（20%）；創新（10%）

---

## Case #10: 在多站台部署下以測試確保設定一致性

### Problem Statement（問題陳述）
- 業務場景：相同系統需佈署到多個獨立站台，每站台的路徑、權限、Session 設定可能不同。若無一致性驗證，容易在不同客戶環境出現不可預期的錯誤。
- 技術挑戰：以最小成本讓每個站台上線前跑同一套環境測試。
- 影響範圍：穩定性、支援成本、交付品質。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 每站台配置差異大。
  2. 安裝人員不一定熟悉設定。
  3. 無自動化一致性檢查。
- 深層原因：
  - 架構層面：環境相依明顯。
  - 技術層面：缺少可移植的測試入口。
  - 流程層面：部署流程未標準化。

### Solution Design（解決方案設計）
- 解決策略：把環境檢查測試（Session、暫存目錄等）打包在站台內，提供 Runner 頁做一鍵自檢，確保跨站一致性。

- 實施步驟：
  1. 測試打包
     - 實作細節：所有站台同樣包含 App_Code 測試
     - 所需資源：NUnitLite
     - 預估時間：1 小時
  2. 上線前驗證
     - 實作細節：安裝指引中加入 Runner 頁檢查步驟
     - 所需資源：文件
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```csharp
// 重用 Case #1、#5、#6 的測試集合，形成一致性檢查套件
```

- 實際案例：文中即描述多站台部署情境與自檢作法。
- 實作環境：多站台 IIS
- 實測數據：
  - 改善前：跨站台隨機性問題
  - 改善後：上線前統一檢核，輸出一致
  - 改善幅度：一致性顯著提升（質化）

Learning Points（學習要點）
- 核心知識點：可移植的環境測試套件
- 技能要求：部署流程設計
- 延伸思考：是否集中回傳結果到中央？
- Practice：做一份跨站台檢查清單（30 分鐘/2 小時/8 小時）
- Assessment：覆蓋性（40%）；流程簡潔（30%）；可複用（20%）；創新（10%）

---

## Case #11: 缺少 appSettings["temp-folder"] 的健全性處理

### Problem Statement（問題陳述）
- 業務場景：部署時常見忽略設定某些必要鍵。若 temp-folder 未設定，測試直接讀取會得到 null，可能造成 NullReference 或誤導性的失敗訊息。
- 技術挑戰：在測試中加入對必填設定鍵的健全性檢查並提供清楚錯誤描述。
- 影響範圍：可診斷性、部署體驗。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺少必填鍵檢查。
  2. 失敗訊息不清楚。
  3. 測試未覆蓋鍵缺失情境。
- 深層原因：
  - 架構層面：設定管理不夠嚴謹。
  - 技術層面：錯誤處理不足。
  - 流程層面：未提供設定樣板與說明。

### Solution Design（解決方案設計）
- 解決策略：在測試前先確認鍵存在與非空，若缺失，回報具體訊息與修復建議。

- 實施步驟：
  1. 鍵檢查
     - 實作細節：string.IsNullOrEmpty 檢查並 Assert.Fail
     - 所需資源：C#
     - 預估時間：10 分鐘
  2. 可讀訊息
     - 實作細節：錯誤訊息附上修復步驟
     - 所需資源：—
     - 預估時間：10 分鐘

- 關鍵程式碼/設定：
```csharp
[Test]
public void TempFolderSettingExists()
{
    var path = ConfigurationManager.AppSettings["temp-folder"];
    Assert.False(string.IsNullOrEmpty(path), 
        "缺少 appSettings['temp-folder']，請在 web.config 加入對應鍵值（例如 C:\\Temp）");
}
```

- 實際案例：延伸文中 I/O 測試，加入鍵存在性檢查。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：Null 造成誤導錯誤
  - 改善後：明確指出缺少設定鍵
  - 改善幅度：診斷效率提升（質化）

Learning Points（學習要點）
- 核心知識點：設定健全性與可診斷訊息
- 技能要求：測試可讀性設計
- 延伸思考：是否建立設定 schema 驗證？
- Practice：為所有必填鍵加測試（30 分鐘/2 小時）；產出設定樣板（8 小時）
- Assessment：錯誤訊息品質（40%）；覆蓋度（30%）；可維護（20%）；創新（10%）

---

## Case #12: 暫存資料夾權限不足導致 IO 失敗的診斷與修復

### Problem Statement（問題陳述）
- 業務場景：即使設定了 temp-folder，仍可能因應用程式帳號無權限而導致寫入失敗。需透過測試快速判斷是不存在還是權限不足，並提供修復建議。
- 技術挑戰：在測試中捕捉 UnauthorizedAccessException 並回報精準原因。
- 影響範圍：所有需要 I/O 的功能。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 應用程式身分缺乏寫入權限。
  2. 目錄被防毒或系統鎖定。
  3. 路徑指到受限制區域。
- 深層原因：
  - 架構層面：權限設計不一致。
  - 技術層面：例外處理與診斷不足。
  - 流程層面：未納入權限設置步驟。

### Solution Design（解決方案設計）
- 解決策略：在 I/O 驗證測試加入 try/catch 區分不存在與權限問題，並輸出賦權建議（如對應 App Pool Identity）。

- 實施步驟：
  1. 捕捉權限例外
     - 實作細節：catch UnauthorizedAccessException
     - 所需資源：.NET
     - 預估時間：15 分鐘
  2. 建議修復
     - 實作細節：輸出賦權指引（IIS App Pool 帳號）
     - 所需資源：文件
     - 預估時間：15 分鐘

- 關鍵程式碼/設定：
```csharp
[Test]
public void TempFolderWritePermissionTest()
{
    var path = ConfigurationManager.AppSettings["temp-folder"];
    Assert.False(string.IsNullOrEmpty(path), "未設定 temp-folder");
    Assert.True(Directory.Exists(path), "資料夾不存在");
    var file = Path.Combine(path, "perm.txt");

    try
    {
        File.WriteAllText(file, "ok");
        File.Delete(file);
    }
    catch (UnauthorizedAccessException)
    {
        Assert.Fail("無寫入權限，請賦予應用程式帳號（AppPool Identity）對 {0} 的寫入/刪除權限", path);
    }
}
```

- 實際案例：延伸文中 I/O 測試做權限診斷。
- 實作環境：IIS + ASP.NET 2.0
- 實測數據：
  - 改善前：只看到泛用 I/O 失敗
  - 改善後：精準指出權限問題與修復方向
  - 改善幅度：故障定位效率提升（質化）

Learning Points（學習要點）
- 核心知識點：I/O 權限診斷、App Pool 身分
- 技能要求：IIS 知識、例外處理
- 延伸思考：自動化賦權腳本？
- Practice：寫 PowerShell 設 ACL（2 小時）；整合至部署流程（8 小時）
- Assessment：診斷準確（40%）；可操作性（30%）；安全性（20%）；創新（10%）

---

## Case #13: 在測試輸出中呈現執行環境資訊以利除錯

### Problem Statement（問題陳述）
- 業務場景：跨站台部署時 OS、.NET 版本不同可能導致差異行為。希望在測試摘要中附帶環境資訊，支援遠距支援與問題比對。
- 技術挑戰：以最小成本取得版本資訊並輸出隨測試結果。
- 影響範圍：支援效率、問題重現。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 不同環境版本差異。
  2. 回報缺少上下文。
  3. 難以比對問題現象。
- 深層原因：
  - 架構層面：環境與行為耦合。
  - 技術層面：資訊收集未標準化。
  - 流程層面：回報格式不一致。

### Solution Design（解決方案設計）
- 解決策略：利用 NUnitLite 預設輸出包含 OS/.NET 版本，確保支援人員可憑此交叉驗證；必要時補充自定義資訊。

- 實施步驟：
  1. 確認輸出
     - 實作細節：Runner 顯示 Runtime Environment 區塊
     - 所需資源：NUnitLite
     - 預估時間：10 分鐘
  2. 追加資訊
     - 實作細節：附加應用程式版本、組態名稱
     - 所需資源：C#
     - 預估時間：20 分鐘

- 關鍵程式碼/設定：
```csharp
// 可在執行前輸出自定義資訊（必要時）
Console.WriteLine("App Version: {0}", typeof(Global).Assembly.GetName().Version);
```

- 實際案例：文中輸出示範含 OS/.NET 版本摘要。
- 實作環境：Windows XP SP2 / .NET 2.0.50727.42
- 實測數據：
  - 改善前：問題回報缺少環境資訊
  - 改善後：摘要自帶環境資訊
  - 改善幅度：支援效率提升（質化）

Learning Points（學習要點）
- 核心知識點：可觀測性、版本資訊收集
- 技能要求：反射、輸出格式化
- 延伸思考：是否上傳到集中日誌？
- Practice：加上更多組態輸出（30 分鐘/2 小時）；集中收集（8 小時）
- Assessment：資訊完整（40%）；整合度（30%）；易用性（20%）；創意（10%）

---

## Case #14: 避免跨 AppDomain 執行造成 HttpContext/Session 失效

### Problem Statement（問題陳述）
- 業務場景：使用某些測試執行器（如 NUnit）時，因跨 AppDomain/Thread 執行導致 HttpContext 不存在，測試中無法使用 Session 等 Web 物件，造成環境檢查無法落地。
- 技術挑戰：確保測試與 Web 在同一 AppDomain/Thread 脈絡執行。
- 影響範圍：所有 Web 相依測試。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Runner 分離 AppDomain。
  2. 測試在非 ASP.NET 管線 Thread 執行。
  3. HttpContext 不流程傳遞。
- 深層原因：
  - 架構層面：測試架構與 Web 管線差異。
  - 技術層面：上下文傳遞限制。
  - 流程層面：選型不符場景。

### Solution Design（解決方案設計）
- 解決策略：採用 NUnitLite 由 ASP.NET 頁面直接呼叫，確保同域執行；或調整測試設計避免依賴 HttpContext。

- 實施步驟：
  1. 同域呼叫
     - 實作細節：Page_Load 直接呼叫 ConsoleUI
     - 所需資源：ASP.NET
     - 預估時間：0.5 小時
  2. 測試分層
     - 實作細節：將純函式邏輯與 Web 依賴拆分
     - 所需資源：設計重構
     - 預估時間：2 小時

- 關鍵程式碼/設定：
```csharp
// 同域執行：避免跨 AppDomain 的 runner
ConsoleUI.Main(new string[] { "App_Code" });
```

- 實際案例：文中指出 NUnit 的分離域特性不建議用於 Web 應用。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：HttpContext 為 null
  - 改善後：Session 可用、測試可跑
  - 改善幅度：可行性恢復（質化）

Learning Points（學習要點）
- 核心知識點：AppDomain、Thread 與 HttpContext 關係
- 技能要求：Web 測試策略設計
- 延伸思考：如何在 CI 中重現同域行為？
- Practice：對比不同 runner 行為（2 小時）；重構測試降低耦合（8 小時）
- Assessment：可行性（40%）；設計品質（30%）；穩健性（20%）；創新（10%）

---

## Case #15: 讓非技術人員也能操作的測試結果閱讀體驗

### Problem Statement（問題陳述）
- 業務場景：測試輸出為純文字摘要，對非技術安裝/客服人員不夠友善。需要最小改動地提升可讀性，使其能快速判讀「是否可上線」與「若失敗該做什麼」。
- 技術挑戰：在不影響測試執行的前提下，提供簡單易懂的輔助說明或替代表現形式。
- 影響範圍：上線效率、支持溝通。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 純文字輸出不直觀。
  2. IE 可能誤判 MIME（見 Case #4）。
  3. 缺少指引性語句。
- 深層原因：
  - 架構層面：輸出未設計面向操作人員。
  - 技術層面：無切換輸出模式。
  - 流程層面：缺少 SOP/指引。

### Solution Design（解決方案設計）
- 解決策略：保留 text/plain，同頁（或相鄰頁）附上「如何解讀」簡述與常見問題對應，必要時提供 HTML 視圖或「檢視原始碼」提示。

- 實施步驟：
  1. 指引區塊
     - 實作細節：在 aspx 頁頂加入簡短說明（或連結）
     - 所需資源：ASPX
     - 預估時間：0.5 小時
  2. HTML 替代視圖（可選）
     - 實作細節：提供將文字輸出包裹 <pre> 或簡單 HTML 的版本
     - 所需資源：ASPX
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```csharp
// 提示：若看到亂碼或 XML 錯誤，請按右鍵「檢視原始碼」或改用 Chrome/Edge 開啟。
// 可另建 RunnerHtml.aspx，將結果以 <pre> 包裹呈現以提升可讀性。
```

- 實際案例：文中建議 IE 可用「檢視原始碼」作為備援。
- 實作環境：ASP.NET 2.0
- 實測數據：
  - 改善前：非技術人員難以判讀
  - 改善後：有明確「如何解讀／如何修復」指引
  - 改善幅度：判讀效率顯著提升（質化）

Learning Points（學習要點）
- 核心知識點：易用性與可讀性設計
- 技能要求：最小 UX 介入
- 延伸思考：是否需要本地化/多語系？
- Practice：寫一份常見失敗指引（30 分鐘/2 小時）；加 HTML 視圖（8 小時）
- Assessment：可讀性（40%）；覆蓋度（30%）；簡潔（20%）；創意（10%）

---

# 案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #2, #3, #4, #5, #9, #11, #15
- 中級（需要一定基礎）
  - Case #1, #6, #7, #8, #10, #12, #13, #14
- 高級（需要深厚經驗）
  - 無（本文聚焦於實務整合與流程化，難度多為入門至中級）

2) 按技術領域分類
- 架構設計類
  - Case #7, #8, #10, #14
- 效能優化類
  - 無直接效能議題（可延伸至輸出與 I/O 測試優化）
- 整合開發類
  - Case #1, #2, #3, #9, #13, #15
- 除錯診斷類
  - Case #4, #5, #6, #11, #12, #13, #14
- 安全防護類
  - Case #4（nosniff 可視為安全相容的一環）

3) 按學習目標分類
- 概念理解型
  - Case #8, #13, #14
- 技能練習型
  - Case #1, #2, #3, #4, #9
- 問題解決型
  - Case #5, #6, #10, #11, #12
- 創新應用型
  - Case #7, #15

# 案例關聯圖（學習路徑建議）
- 建議先學：
  - Case #1（Runner 基礎）→ Case #2（App_Code 探索）→ Case #3（輸出導向）
- 依賴關係：
  - Case #5、#6、#11、#12 依賴 Runner 能正常執行（Case #1-3）
  - Case #4、#15 建立在 Runner 輸出呈現之上（Case #3）
  - Case #8、#14 為選型與執行脈絡的理論支撐（可在實作後理解）
  - Case #7、#10 整合為部署流程（建立在所有基礎測試之上）
  - Case #9、#13 為支援性議題（建置與可觀測性），可隨時補充
- 完整學習路徑：
  1) Case #1 → 2 → 3（建立可執行與可見的測試基礎）
  2) Case #5 → 6 → 11 → 12（完成 Session 與 I/O 配置驗證）
  3) Case #4 → 15（優化可讀性與相容性）
  4) Case #8 → 14（理解選型與執行脈絡）
  5) Case #7 → 10（沉澱為部署前自檢流程）
  6) Case #9、#13（補齊建置與可觀測性，利於維運與支援）

以上案例與路徑，完整覆蓋文章中提及的問題、根因、解法與效益，並轉化為可教學、可實作、可評估的練習素材。