---
layout: synthesis
title: "替 App_Code 目錄下的 code 寫單元測試 ?"
synthesis_type: solution
source_post: /2006/10/29/writing-unit-tests-for-app-code-directory/
redirect_from:
  - /2006/10/29/writing-unit-tests-for-app-code-directory/solution/
---

以下為基於原文情境（ASP.NET 2.0 Web Site 模型、App_Code 動態編譯、NUnit/NUnitLite 測試）所整理的 15 個可落地、可教學、可實作的問題解決案例。每一案皆圍繞原文兩大難題（無固定 DLL、依賴 Hosting 環境/HttpContext）與作者最後採用的方向（NUnitLite 於同一 AppDomain/特殊環境可執行），並補足可操作的實作步驟與範例碼，供實戰練習與評估使用。

## Case #1: 在 ASP.NET Hosting 環境內嵌入 NUnitLite 執行 App_Code 單元測試

### Problem Statement（問題陳述）
- 業務場景：ASP.NET 2.0 Web Site 專案大量共用邏輯放在 App_Code，團隊希望為核心服務寫單元測試，並在開發/測試站即時執行，避免部署前才發現錯誤。因為 Web Site 採動態編譯，測試需要在與網站相同的 Hosting 環境與 AppDomain 執行，才能正確取用 HttpContext 等資源。
- 技術挑戰：傳統 NUnit/MSTest Runner 會在獨立 AppDomain 承載測試，無法取得 HttpContext；App_Code 無固定 DLL，外部 Runner 難以定位載入。
- 影響範圍：單元測試無法覆蓋與 HttpContext 相依的邏輯，缺口轉為手動回歸，導致錯誤延遲、風險上升。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. App_Code 無對應固定 DLL，僅存在於 Temporary ASP.NET Files，路徑不穩定。
  2. 傳統 Runner 使用獨立 AppDomain，測試時無法取得 Web Hosting 所提供之 HttpContext。
  3. NUnit 設計嚴謹、可擴充，改造成本高，維護自改版框架風險大。
- 深層原因：
  - 架構層面：Web Site 動態編譯模型與測試 Runner 分離式承載設計天生衝突。
  - 技術層面：對 HttpContext 等靜態存取的硬相依，降低可測性。
  - 流程層面：依賴外部 Runner 的習慣，缺少在網站內嵌測試的流程與工具。

### Solution Design（解決方案設計）
- 解決策略：將 NUnitLite 以原始碼形式加入 Web Site，由網站本身承載測試，確保與被測程式在同一 AppDomain、同一 Hosting 環境執行。建立簡易 TestRunner 頁面收斂啟動與輸出，使 HttpContext 依賴得以保留且被測。

- 實施步驟：
  1. 導入 NUnitLite 原始碼
     - 實作細節：將 NUnitLite Source（對應 .NET 2.0 版本）加入 App_Code\Testing\NUnitLite 下。
     - 所需資源：NUnitLite 原始碼
     - 預估時間：0.5 天
  2. 建立 TestRunner.aspx/.cs
     - 實作細節：於 Page_Load 呼叫 NUnitLite AutoRun 或 Runner API，將輸出寫回頁面。
     - 所需資源：System.Web、NUnitLite
     - 預估時間：0.5 天
  3. 標註測試類別
     - 實作細節：在 App_Code 建立 Tests 目錄，使用 [TestFixture]/[Test]。
     - 所需資源：NUnitLite Attributes
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// TestRunner.aspx.cs（示意，依實際 NUnitLite 版本 API 調整）
using System;
using System.IO;
using System.Web.UI;
// using NUnitLite; // 引入對應命名空間

public partial class TestRunner : Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        var sw = new StringWriter();

        // 若使用 NUnitLite AutoRun 模式（不同版本 API 可能不同）
        // new NUnitLite.AutoRun().Execute(new string[] { }, new NUnitLite.Runner.ExtendedTextWrapper(sw), Console.In, Console.Out);

        // 若版本 API 差異，可改為自寫極簡反射 Runner 或包裝 NUnitLite Runner 類別
        // 這裡僅示意寫出結果
        sw.WriteLine("NUnitLite executed in ASP.NET AppDomain.");

        Response.ContentType = "text/plain";
        Response.Write(sw.ToString());
    }
}
```

- 實際案例：原文作者選擇以 NUnitLite 取代外部 Runner，因其不啟用獨立 AppDomain、可在特殊/受限環境執行，恰符合 ASP.NET Hosting 下測試的需求。
- 實作環境：.NET Framework 2.0、ASP.NET 2.0 Web Site、IIS/Cassini、NUnitLite 0.x（或相容版本）
- 實測數據：
  - 改善前：無法測試 HttpContext 相依之程式碼
  - 改善後：可在站內一鍵執行測試，覆蓋 HttpContext 相依邏輯
  - 改善幅度：原文未提供；建議追蹤可測覆蓋率與失敗回歸時間

Learning Points（學習要點）
- 核心知識點：
  - Web Site 動態編譯與測試承載的關係
  - 測試在同一 AppDomain/Hosting 的必要性
  - 以源碼引入輕量測試框架的模式
- 技能要求：
  - 必備技能：ASP.NET Page/生命週期、基礎單元測試概念
  - 進階技能：框架原始碼整合、測試輸出與診斷
- 延伸思考：
  - 是否需要加上授權或內部網段限制 TestRunner？
  - 如何做類別或分類過濾以加速執行？
  - 和 CI 整合的拉取與解析格式為何？
- Practice Exercise（練習題）
  - 基礎練習：建立 TestRunner.aspx，輸出固定文字（30 分鐘）
  - 進階練習：讓 TestRunner 只執行特定命名空間/分類（2 小時）
  - 專案練習：將 NUnitLite 整合，執行並輸出測試報告至 App_Data（8 小時）
- Assessment Criteria（評估標準）
  - 功能完整性（40%）：可在站內啟動與查看測試結果
  - 程式碼品質（30%）：清晰分層、可讀性與註解
  - 效能優化（20%）：可篩選/分批執行
  - 創新性（10%）：輸出格式、易於整合的改造

---

## Case #2: 以 TestRunner.aspx 暴露 HTTP 觸發與過濾執行測試

### Problem Statement（問題陳述）
- 業務場景：QA/開發希望以瀏覽器或 CI 透過 URL 觸發測試，並支援按分類、名稱關鍵字篩選，以加速回歸與定位問題，同時保持在 Hosting 環境內執行。
- 技術挑戰：需在 ASP.NET 頁面上執行測試並接收查詢參數，動態選擇要執行的測試集合。
- 影響範圍：無法選擇性執行導致測試耗時；不易在 CI 以 HTTP 方式觸發站內測試。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 測試執行介面缺乏可參數化入口。
  2. 測試集合過大導致每次全量回歸耗時。
  3. 缺乏標準化輸出格式，CI 难以解析。
- 深層原因：
  - 架構層面：測試與呼叫端未有明確契約（輸入/輸出）。
  - 技術層面：未將分類、篩選內建進 Runner。
  - 流程層面：測試觸發/篩選規則未納入團隊開發流程。

### Solution Design（解決方案設計）
- 解決策略：在 TestRunner.aspx 解析 QueryString（如 category、name），使用 NUnitLite 或自定反射查詢過濾相符測試後執行；輸出純文字/JSON 供人讀與機讀。

- 實施步驟：
  1. 設計 URL 契約
     - 實作細節：/TestRunner.aspx?category=Service&name=Cart
     - 所需資源：無
     - 預估時間：0.5 天
  2. 加入過濾器
     - 實作細節：以反射或 Runner API 篩選 TestFixture/Test 方法名稱/Category
     - 所需資源：NUnitLite 或自寫過濾器
     - 預估時間：1 天
  3. 撰寫輸出格式
     - 實作細節：text/plain 與可選 JSON（狀態、通過/失敗、耗時）
     - 所需資源：序列化工具（可選）
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// TestRunner.aspx.cs（簡化反射示例）
string category = Request["category"];
string name = Request["name"];
var asm = System.Reflection.Assembly.GetExecutingAssembly();
var tests = from t in asm.GetTypes()
            where t.IsClass && Attribute.IsDefined(t, typeof(TestFixtureAttribute))
            from m in t.GetMethods()
            where Attribute.IsDefined(m, typeof(TestAttribute))
               && (string.IsNullOrEmpty(name) || m.Name.IndexOf(name, StringComparison.OrdinalIgnoreCase) >= 0)
               && (string.IsNullOrEmpty(category) || m.GetCustomAttributes(typeof(CategoryAttribute), true)
                                                     .Cast<CategoryAttribute>().Any(a => a.Name == category))
            select new { Type = t, Method = m };
```

- 實際案例：原文建議以站內執行測試；本案延伸為對外提供可參數化入口，便於 QA/CI 操作。
- 實作環境：同 Case #1
- 實測數據：原文未提供；建議記錄單次執行耗時、測試數、失敗數

Learning Points
- 核心知識點：HTTP 可觸發測試、過濾與狀態輸出契約化
- 技能要求：ASP.NET 處理 QueryString、反射/Runner API
- 延伸思考：是否需要斷路器（避免重度壓測）；如何做分頁/分片測試
- Practice Exercise：為 Runner 增加 category/name 過濾（2 小時）
- Assessment Criteria：
  - 功能完整性：過濾、輸出正確
  - 程式碼品質：查詢/反射安全
  - 效能優化：大集合篩選效率
  - 創新性：輸出格式可機器解析

---

## Case #3: 使用 aspnet_compiler 預編譯產出 App_Code DLL 以供外部 Runner 測試

### Problem Statement（問題陳述）
- 業務場景：團隊更偏好沿用現有外部 NUnit/MSTest 基礎設施（CI 上已有報表與掛鉤），希望將 Web Site 的 App_Code 預編譯為可被 Runner 載入之 DLL。
- 技術挑戰：App_Code 於開發期動態編譯，無固定 DLL；Temporary ASP.NET Files 目錄隨機化不利於自動化。
- 影響範圍：CI 測試無法直接載入被測程式碼；自動化鏈不完整。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 動態編譯與隨機臨時目錄。
  2. CI 需固定輸入（DLL 路徑）。
  3. 預設流程未包含預編譯步驟。
- 深層原因：
  - 架構層面：Web Site 模型非產出單一組件。
  - 技術層面：未使用 aspnet_compiler/merge 工具。
  - 流程層面：Build Pipeline 未整合 Web 專案預編譯。

### Solution Design
- 解決策略：在 Build/CI 中插入 aspnet_compiler，預編譯 Web Site 至輸出資料夾，取得 App_Code.dll（或與 aspnet_merge 合併），再交給外部 Runner 執行測試。

- 實施步驟：
  1. 加入預編譯命令
     - 實作細節：使用 aspnet_compiler -p -v
     - 所需資源：.NET SDK
     - 預估時間：0.5 天
  2. 配合 aspnet_merge（可選）
     - 實作細節：合併多 DLL 方便定位
     - 所需資源：aspnet_merge（Web Deployment Projects）
     - 預估時間：0.5 天
  3. CI 任務串接 Runner
     - 實作細節：nunit-console 指向產出 DLL
     - 所需資源：NUnit Console
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```cmd
:: 預編譯 Web Site（範例）
aspnet_compiler -p "C:\src\WebSite" -v / "C:\build\Precompiled"

:: 合併（可選，需安裝 Web Deployment Projects）
aspnet_merge "C:\build\Precompiled" -o "MySite"

:: 執行 NUnit（指向 App_Code 或合併後 DLL）
nunit-console "C:\build\Precompiled\bin\App_Code.dll"
```

- 實際案例：原文指出 App_Code 無 DLL 是痛點；本案以預編譯解決定位問題，保留外部 Runner 與 CI 既有流程。
- 實作環境：.NET 2.0 SDK、NUnit Console
- 實測數據：原文未提供；建議追蹤預編譯耗時、Runner 耗時與失敗率

Learning Points
- 核心知識點：aspnet_compiler/aspnet_merge 與 Web Site 模型
- 技能要求：命令列工具、CI 任務編排
- 延伸思考：預編譯對除錯便利性的影響；版本化與產物管理
- Practice Exercise：在本機跑一次預編譯+NUnit（2 小時）
- Assessment Criteria：產出正確、Runner 成功、腳本可重複

---

## Case #4: 抽離業務邏輯至 Class Library，降低 HttpContext 相依

### Problem Statement
- 業務場景：App_Code 中混有大量與 HttpContext 混雜的業務邏輯，導致測試難；團隊希望逐步提升單元測試比例，先將純邏輯抽出，保留 UI/環境耦合於 Web。
- 技術挑戰：辨識可抽離層次、重構邊界、維持既有功能。
- 影響範圍：架構演進、部署流程（額外 DLL）。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 服務層與 Web 層混雜。
  2. 靜態取用 HttpContext.Current 降低可測性。
  3. 無介面抽象與 DI 管線。
- 深層原因：
  - 架構層面：缺少明確分層（Domain/Service vs Web）。
  - 技術層面：缺少介面與可替換邏輯。
  - 流程層面：未建立重構與回歸機制。

### Solution Design
- 解決策略：建立 Class Library（Core/Services），將不需 Hosting 的業務規則移入；在 Web 層以 Adapter 連接 HttpContext 與服務；以外部 Runner 測試 Class Library。

- 實施步驟：
  1. 分析與標記可抽離邏輯
     - 實作細節：從無 HttpContext 依賴的方法開始
     - 所需資源：重構工具
     - 預估時間：1-2 天
  2. 建立介面與 DI 平替
     - 實作細節：IClock、IUserContext 等
     - 所需資源：無/輕量 DI
     - 預估時間：1 天
  3. 持續回歸與部署
     - 實作細節：WAP/WDP 或手動引用 DLL
     - 所需資源：CI/CD
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// Class Library
public interface ICartService { void Add(string sku, int qty); }
public class CartService : ICartService
{
    private readonly IClock _clock;
    public CartService(IClock clock) { _clock = clock; }
    public void Add(string sku, int qty) { /* 純邏輯，無 HttpContext */ }
}
```

- 實際案例：原文描述抽不動時採用 NUnitLite；本案為長期解法，逐步降低環境耦合。
- 實作環境：.NET 2.0、NUnit/MSTest
- 實測數據：原文未提供；建議追蹤可測覆蓋率、Bug 逃逸率

Learning Points：分層、抽象、可測性設計
- Practice Exercise：抽出一個服務並寫 5 個測試（8 小時）
- Assessment：分層正確、測試齊全、無回歸

---

## Case #5: 手動建立 HttpContext（Request/Response）供測試使用

### Problem Statement
- 業務場景：部分方法僅需 HttpContext.Items/Request/Response，無法於外部 Runner 取得環境，欲在同域測試或以自製 Runner 執行。
- 技術挑戰：在測試前手動建立 HttpContext，並避免污染其他測試。
- 影響範圍：測試獨立性、可靠性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 靜態 HttpContext.Current 取用。
  2. 無易注入之抽象層。
  3. 測試生命週期未重置上下文。
- 深層原因：
  - 架構層面：物件生命週期與環境耦合。
  - 技術層面：未知如何手動組 HttpContext。
  - 流程層面：未定義 SetUp/TearDown 規範。

### Solution Design
- 解決策略：於測試 SetUp 建立 HttpContext（HttpRequest/HttpResponse + StringWriter），測後清理，確保測試互不干擾。

- 實施步驟：
  1. 建立輔助工具
     - 實作細節：ContextFactory 建立/清理
     - 資源：System.Web
     - 時間：0.5 天
  2. 套用於測試生命週期
     - 實作細節：SetUp/TearDown 呼叫
     - 時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public static class HttpContextHelper
{
    public static void Create() {
        var request = new HttpRequest("test.aspx", "http://localhost/test.aspx", "");
        var response = new HttpResponse(new StringWriter());
        HttpContext.Current = new HttpContext(request, response);
    }
    public static void Cleanup() {
        HttpContext.Current = null;
    }
}

// 測試中使用
// [SetUp] public void Setup(){ HttpContextHelper.Create(); }
// [TearDown] public void Teardown(){ HttpContextHelper.Cleanup(); }
```

- 實際案例：原文強調需要 Hosting 環境；在同域下可用此法提供最小上下文。
- 實作環境：.NET 2.0、ASP.NET
- 實測數據：原文未提供；建議追蹤測試穩定度（無共享污染）

Learning Points：HttpContext 手動建構、測試隔離
- Practice Exercise：為 3 個方法建立上下文測試（2 小時）
- Assessment：上下文正確、無交互污染

---

## Case #6: 以 Cassini/IIS Express 進行 HTTP 型整合測試（跨程序）

### Problem Statement
- 業務場景：需要端到端驗證，包含 ASP.NET 管線、Global Filters、HttpModules 的行為，並透過 TestRunner 頁面觸發。
- 技術挑戰：啟動開發伺服器、發送 HTTP、解析測試結果。
- 影響範圍：測試時間、可靠性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 單元測試不足以覆蓋管線行為。
  2. 需要跨程序但仍保有站內執行測試。
  3. 缺少結果解析格式。
- 深層原因：
  - 架構層面：系統層行為需 E2E 驗證。
  - 技術層面：啟動/連線/超時處理。
  - 流程層面：CI 如何拉起站點再測。

### Solution Design
- 解決策略：啟動 Cassini/IIS Express 承載站點，以 HTTP 請求打到 /TestRunner.aspx，返回純文字/JSON 供測試斷言。

- 實施步驟：
  1. 準備啟動腳本
     - 實作細節：啟動 IIS Express 指向目錄/port
     - 時間：0.5 天
  2. 撰寫整合測試
     - 實作細節：用 HttpWebRequest 拉取、斷言結果
     - 時間：0.5 天
  3. CI 串接與清理
     - 實作細節：啟動→測試→關閉
     - 時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var url = "http://localhost:8080/TestRunner.aspx?category=Smoke";
var req = (System.Net.HttpWebRequest)System.Net.WebRequest.Create(url);
using (var resp = req.GetResponse())
using (var sr = new System.IO.StreamReader(resp.GetResponseStream()))
{
    var text = sr.ReadToEnd();
    if (!text.Contains("PASS")) throw new Exception("Integration tests failed");
}
```

- 實際案例：原文以站內 Runner 為解；本案延伸為透過 HTTP 驗證整體行為。
- 實作環境：IIS Express/Cassini、.NET 2.0
- 實測數據：原文未提供；建議追蹤啟動耗時、E2E 測試通過率

Learning Points：E2E 測試與站內 Runner 結合
- Practice Exercise：寫 1 個整合測試調用 TestRunner（2 小時）
- Assessment：啟停正確、斷言可靠

---

## Case #7: 使用 Web Deployment Project 的 aspnet_merge 產出單一 DLL

### Problem Statement
- 業務場景：希望最終只處理一個 DLL 供掃瞄與測試，簡化 CI 與分析。
- 技術挑戰：預編譯後常產生多個組件，需要合併。
- 影響範圍：Build 產物、診斷流程。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 多組件輸出難以管理。
  2. 測試/掃描工具偏好單一輸入。
  3. 缺少合併步驟。
- 深層原因：
  - 架構層面：產物顆粒度零散。
  - 技術層面：未使用 aspnet_merge。
  - 流程層面：構建未標準化。

### Solution Design
- 解決策略：在預編譯後使用 aspnet_merge 合併為 MySite.dll，統一測試入口。

- 實施步驟：
  1. 預編譯（同 Case #3）
  2. 合併
     - 實作細節：aspnet_merge <precompiledPath> -o MySite
     - 時間：0.5 天
  3. 更新 Runner 目標
     - 實作細節：nunit-console 指向 MySite.dll
     - 時間：0.5 天

- 關鍵程式碼/設定：
```cmd
aspnet_merge "C:\build\Precompiled" -o "MySite"
nunit-console "C:\build\Precompiled\bin\MySite.dll"
```

- 實際案例：對應原文「無固定 DLL」痛點的另一種工程向解法。
- 實作環境：WDP、.NET SDK
- 實測數據：原文未提供；建議追蹤合併耗時與失敗率

Learning Points：產物合併與標準化
- Practice Exercise：完成一次合併並執行測試（2 小時）
- Assessment：單一 DLL、Runner 成功

---

## Case #8: 在 Global.asax 啟動條件式執行測試並持久化結果

### Problem Statement
- 業務場景：在測試環境，應用程式啟動即自動執行冒煙測試，並將結果存放 App_Data 供檢視/CI 抓取。
- 技術挑戰：避免影響正常流量；控制僅在測試模式執行。
- 影響範圍：啟動時間、資源使用。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 手動觸發容易遺漏。
  2. 結果不持久不利於追蹤。
  3. 無環境開關。
- 深層原因：
  - 架構層面：缺少測試啟動鉤子。
  - 技術層面：未設計條件執行與輸出。
  - 流程層面：測試環境管控鬆散。

### Solution Design
- 解決策略：在 Application_Start 判斷 web.config/appSettings 或機器環境變數為 Test=true 時執行輕量測試群組，結果寫至 App_Data，避免高成本套件。

- 實施步驟：
  1. 加入 appSettings：RunSmokeOnStart
  2. Global.asax 實作條件執行與結果儲存
  3. 監控檔案/健康檢查整合

- 關鍵程式碼/設定：
```csharp
// Global.asax
protected void Application_Start(object sender, EventArgs e)
{
    if (System.Configuration.ConfigurationManager.AppSettings["RunSmokeOnStart"] == "true")
    {
        var path = Server.MapPath("~/App_Data/startup-test.txt");
        System.IO.File.WriteAllText(path, "Smoke tests executed at " + DateTime.Now);
        // TODO: 呼叫站內 Runner/自製輕量測試
    }
}
```

- 實際案例：原文採站內執行；此案將其系統化至啟動管線。
- 實作環境：ASP.NET 2.0
- 實測數據：原文未提供；建議追蹤啟動耗時、冒煙失敗次數

Learning Points：條件啟動、結果持久化
- Practice：加入冒煙測試與檔案輸出（2 小時）
- Assessment：僅測試環境執行、檔案正確

---

## Case #9: 建立 HttpContext 包裝介面與注入點（降低靜態耦合）

### Problem Statement
- 業務場景：大量方法透過 HttpContext.Current 取資料，導致測試困難。欲透過自定介面與注入方式降低耦合。
- 技術挑戰：替代靜態依賴、遷移成本控制。
- 影響範圍：呼叫端與單元測試大幅受益。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 靜態依賴阻斷替身注入。
  2. 無協定抽象（Session/Items/Request）。
  3. 現有方法簽名固定。
- 深層原因：
  - 架構層面：缺少 Anti-Corruption Layer。
  - 技術層面：缺乏抽象/Adapter。
  - 流程層面：無重構規範。

### Solution Design
- 解決策略：定義 IAppContext（封裝需要的上下文存取），實作 WebAppContext 走 HttpContext.Current，測試時注入 FakeAppContext。

- 實施步驟：
  1. 定義介面/實作
  2. 改造方法簽名/組態注入點（或 Service Locator）
  3. 單元測試使用 Fake

- 關鍵程式碼/設定：
```csharp
public interface IAppContext
{
    object GetItem(string key);
    void SetItem(string key, object value);
}

public class WebAppContext : IAppContext
{
    public object GetItem(string key) { return HttpContext.Current.Items[key]; }
    public void SetItem(string key, object value) { HttpContext.Current.Items[key] = value; }
}
```

- 實際案例：原文感嘆難抽出；本案提出可漸進落地的抽象法。
- 實作環境：.NET 2.0
- 實測數據：原文未提供；建議追蹤可測比例提升

Learning Points：抽象化與 DI 概念
- Practice：為 1 個服務導入 IAppContext（8 小時）
- Assessment：介面合理、替身可測

---

## Case #10: 以 Rhino Mocks 模擬 IAppContext，撰寫單元測試

### Problem Statement
- 業務場景：已有 IAppContext 抽象，需快速撰寫替身並驗證互動。
- 技術挑戰：.NET 2.0 時代使用可用的 Mock 框架（如 Rhino Mocks）。
- 影響範圍：測試速度、可靠性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺少輕鬆替身創建方式。
  2. 需驗證互動（呼叫/回傳）。
  3. 測試可讀性。
- 深層原因：
  - 架構層面：抽象已就緒，欠 Mock 策略。
  - 技術層面：熟悉 .NET 2.0 Mock 工具。
  - 流程層面：測試規範化。

### Solution Design
- 解決策略：使用 Rhino Mocks 建立 IAppContext 假物件，注入被測服務，撰寫互動式斷言。

- 實施步驟：
  1. 安裝 Rhino Mocks（相容 .NET 2.0）
  2. 撰寫 Mock 與測試案例
  3. 整合至 CI

- 關鍵程式碼/設定：
```csharp
// 以 Rhino Mocks 為例
// using Rhino.Mocks;
var mocks = new Rhino.Mocks.MockRepository();
var ctx = mocks.StrictMock<IAppContext>();
Rhino.Mocks.Expect.Call(ctx.GetItem("user")).Return("u1");
mocks.ReplayAll();

// 注入到被測服務，執行
// Assert 與 Verify
mocks.VerifyAll();
```

- 實際案例：延續 Case #9 的抽象，落實測試替身。
- 實作環境：.NET 2.0、Rhino Mocks
- 實測數據：原文未提供；建議追蹤測試撰寫效率

Learning Points：Mock 基礎、互動驗證
- Practice：針對 2 個依賴點寫 Mock 測試（2 小時）
- Assessment：互動正確、測試可讀

---

## Case #11: 在站內以 BuildManager 掃描與載入已編譯組件，反射執行測試

### Problem Statement
- 業務場景：不依賴外部 Runner，站內使用 BuildManager.GetReferencedAssemblies 找到當前 AppDomain 中的組件，反射執行具有 [Test] 的方法。
- 技術挑戰：僅篩選站內 App_Code 與測試型別、處理例外與輸出。
- 影響範圍：Runner 穩定性、可維護性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Temporary ASP.NET Files 路徑不穩定。
  2. 外部 Runner 不在同域。
  3. 需在站內取得組件與型別清單。
- 深層原因：
  - 架構層面：站內反射最貼近實際環境。
  - 技術層面：BuildManager API 未運用。
  - 流程層面：Runner 實作未標準化。

### Solution Design
- 解決策略：在 TestRunner.aspx 透過 BuildManager 擷取組件，找出 TestFixture 類別並執行 [Test] 方法，輸出結果。

- 實施步驟：
  1. 取得組件集合
  2. 反射尋找 Test 類與方法
  3. 執行與紀錄結果

- 關鍵程式碼/設定：
```csharp
var asms = System.Web.Compilation.BuildManager.GetReferencedAssemblies()
                                              .Cast<System.Reflection.Assembly>();
foreach (var asm in asms)
{
    foreach (var t in asm.GetTypes())
    {
        if (!Attribute.IsDefined(t, typeof(TestFixtureAttribute))) continue;
        var inst = Activator.CreateInstance(t);
        foreach (var m in t.GetMethods().Where(x => Attribute.IsDefined(x, typeof(TestAttribute))))
        {
            try { m.Invoke(inst, null); /* PASS */ }
            catch (Exception ex) { /* FAIL: ex.InnerException */ }
        }
    }
}
```

- 實際案例：原文強調站內執行；本案提供不依框架的反射方案。
- 實作環境：ASP.NET 2.0
- 實測數據：原文未提供；建議追蹤測試數、錯誤細節輸出率

Learning Points：BuildManager 與站內反射
- Practice：完成一個最小 Runner（2 小時）
- Assessment：可列出並執行測試

---

## Case #12: 自建極簡 Test Attribute 與 Runner（DIY）以免外部依賴

### Problem Statement
- 業務場景：NUnitLite 某版本無法編譯或不便整合，需自建最小測試框架支援 [MyTest] 屬性與簡單斷言。
- 技術挑戰：實作 Attribute、反射、結果輸出與例外處理。
- 影響範圍：僅用於站內自測或過渡期。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 輕量框架不可用。
  2. 又要在站內同域執行。
  3. 仍需最小可用測試功能。
- 深層原因：
  - 架構層面：最小可行產品（MVP）思維。
  - 技術層面：反射/屬性基礎。
  - 流程層面：過渡策略。

### Solution Design
- 解決策略：定義 [MyTest] 屬性，掃描 App_Code 型別，逐一呼叫方法，捕捉例外與輸出 PASS/FAIL。

- 實施步驟：
  1. 定義屬性與斷言工具
  2. 反射執行與輸出
  3. 測試頁整合

- 關鍵程式碼/設定：
```csharp
[AttributeUsage(AttributeTargets.Method)]
public class MyTestAttribute : Attribute {}

public static class MiniAssert
{
    public static void IsTrue(bool cond, string msg) { if (!cond) throw new Exception(msg); }
}

// Runner 片段
foreach (var t in asm.GetTypes())
foreach (var m in t.GetMethods())
    if (Attribute.IsDefined(m, typeof(MyTestAttribute))) {
        var o = Activator.CreateInstance(t);
        try { m.Invoke(o, null); Write("PASS"); }
        catch (TargetInvocationException ex) { Write("FAIL: " + ex.InnerException.Message); }
    }
```

- 實際案例：呼應原文中「NUnitLite 最新 release 還不能 build」之窘境，提供過渡方案。
- 實作環境：ASP.NET 2.0
- 實測數據：原文未提供；建議追蹤用例通過率

Learning Points：Attribute/反射/最小斷言
- Practice：實作 MyTest 與 MiniAssert（2 小時）
- Assessment：能執行/報告結果

---

## Case #13: 在同一 AppDomain 下的測試隔離（重置 HttpContext 與狀態）

### Problem Statement
- 業務場景：站內 Runner 同一 AppDomain 執行多測試，容易共用 Items/Application/自訂單例，需確保互不干擾。
- 技術挑戰：制定隔離策略與生命週期掛鉤。
- 影響範圍：測試穩定性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 共享狀態未清理。
  2. 測試順序影響結果。
  3. 無 SetUp/TearDown。
- 深層原因：
  - 架構層面：共享資源管理缺失。
  - 技術層面：缺少隔離鉤子。
  - 流程層面：測試規範未建立。

### Solution Design
- 解決策略：為 Runner 增加每測試的鉤子，建立新 HttpContext、清空 Items/自訂靜態/單例，測後還原。

- 實施步驟：
  1. 制定隔離 API
  2. 套用於 Runner 執行前後
  3. 監控 flaky 測試

- 關鍵程式碼/設定：
```csharp
void BeforeEach() { HttpContextHelper.Create(); /* 清理自訂單例 */ }
void AfterEach()  { HttpContextHelper.Cleanup(); /* 重置靜態 */ }
```

- 實際案例：原文站內執行隱含同域；本案強化隔離。
- 實作環境：ASP.NET 2.0
- 實測數據：原文未提供；建議追蹤 flaky 率下降

Learning Points：測試隔離策略
- Practice：為 Runner 加入 Before/After（1 小時）
- Assessment：重跑穩定

---

## Case #14: 將測試結果輸出至 App_Data 並供 CI 拉取解析

### Problem Statement
- 業務場景：CI 需要可機讀的測試結果，站內 Runner 應輸出檔案供後續流程分析。
- 技術挑戰：定義簡單可解析格式（如 JSON/CSV），避免權限問題。
- 影響範圍：可觀測性、追蹤性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 僅頁面輸出不利於機器讀取。
  2. 多人同時觸發結果混雜。
  3. 權限/目錄路徑。
- 深層原因：
  - 架構層面：缺乏可觀測性設計。
  - 技術層面：檔案輸出與命名策略。
  - 流程層面：CI 取檔與清理。

### Solution Design
- 解決策略：於 TestRunner 增加寫檔選項，輸出至 App_Data/test-results-{timestamp}.json，CI 以 HTTP 拉取或 SMB 讀取。

- 實施步驟：
  1. 定義輸出模式
  2. 編碼寫檔與並發命名
  3. CI 解析與清理

- 關鍵程式碼/設定：
```csharp
var path = Server.MapPath("~/App_Data/test-results-" + DateTime.Now.ToString("yyyyMMddHHmmss") + ".txt");
System.IO.File.WriteAllText(path, "PASS=10, FAIL=0, DURATION=1234ms");
```

- 實際案例：原文無數據輸出；本案補齊可觀測性。
- 實作環境：ASP.NET 2.0
- 實測數據：原文未提供；建議追蹤歷史趨勢

Learning Points：結果落地與 CI 整合
- Practice：輸出並由外部腳本解析（2 小時）
- Assessment：檔案正確、CI 可讀

---

## Case #15: 保護 TestRunner 安全性與環境開關（避免上線暴露）

### Problem Statement
- 業務場景：TestRunner 僅應於測試/內網可用，避免在正式環境暴露測試入口。
- 技術挑戰：環境區分、程式碼與組態的雙重防護。
- 影響範圍：安全性、誤觸風險。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 公開 URL 易被誤用。
  2. 環境未分流。
  3. 無授權/白名單。
- 深層原因：
  - 架構層面：缺少安全邊界。
  - 技術層面：未檢查 Request.IsLocal/自訂旗標。
  - 流程層面：部署規範不足。

### Solution Design
- 解決策略：TestRunner 加入程式檢查（僅本機/測試旗標），web.config 或 IIS 限制；發佈時預處理刪除 Runner。

- 實施步驟：
  1. 程式內檢查
  2. web.config 限制
  3. 發佈流程移除 Runner

- 關鍵程式碼/設定：
```csharp
// TestRunner.aspx.cs
protected void Page_Load(object sender, EventArgs e)
{
    if (!Request.IsLocal && System.Configuration.ConfigurationManager.AppSettings["EnableTestRunner"] != "true")
    {
        Response.StatusCode = 403; Response.End(); return;
    }
    // ... 執行測試
}
```

- 實際案例：原文提及站內執行；本案補強安全/環境控制。
- 實作環境：ASP.NET 2.0、IIS
- 實測數據：原文未提供；建議追蹤阻擋率/誤用事件為 0

Learning Points：測試入口安全防護
- Practice：加上 403 與 web.config 限制（30 分鐘）
- Assessment：正式環境不可達、測試環境可用

---

## Case #16: 以 Web Application Project（WAP）替代 Web Site，恢復 DLL 為測試輸入

### Problem Statement
- 業務場景：團隊願意調整專案模型，從 Web Site 改為 WAP，以獲得可預測的組件輸出並使用標準 Runner。
- 技術挑戰：升級/轉換成本、相容性調整。
- 影響範圍：專案結構、Build/部署。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. Web Site 動態編譯導致無 DLL。
  2. 測試工具期望固定輸出。
  3. 現行流程難結合。
- 深層原因：
  - 架構層面：專案模型選擇。
  - 技術層面：WAP 與 Web Site 差異。
  - 流程層面：版本控制與部署策略需調整。

### Solution Design
- 解決策略：將專案轉為 WAP，透過 MSBuild 產生單一 Web 專案 DLL，與 Class Library 同等對待，方便外部 Runner 執行與分析。

- 實施步驟：
  1. 建立 WAP 並導入現有檔案
  2. 修正差異（命名空間/CodeBehind 指定）
  3. CI 建置與 Runner 串接

- 關鍵程式碼/設定：
```xml
<!-- WAP csproj 中可設定輸出組件名稱 -->
<PropertyGroup>
  <AssemblyName>MyWebApp</AssemblyName>
</PropertyGroup>
```

- 實際案例：原文鎖定 Web Site；本案提供工程治理取徑。
- 実作環境：VS2005/2008 WAP、MSBuild
- 實測數據：原文未提供；建議追蹤轉換工時與測試穩定度提升

Learning Points：專案模型對可測性的影響
- Practice：建立 WAP 範例並執行 Unit Test（8 小時）
- Assessment：成功產生 DLL、Runner 通過

---

## Case #17: 以 HttpRuntime.CodegenDir 或路徑規則定位 Temporary ASP.NET Files（不建議但可救急）

### Problem Statement
- 業務場景：需在站外臨時定位 App_Code 編譯產物，進行反射掃描或拋轉至分析器。
- 技術挑戰：路徑隨機化、不穩定；需容錯掃描。
- 影響範圍：脆弱性與維護成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 臨時路徑含雜湊。
  2. 使用者/應用程式目錄層級繁多。
  3. 權限問題。
- 深層原因：
  - 架構層面：臨時輸出不保證穩定。
  - 技術層面：僅供 runtime 使用。
  - 流程層面：救急需求導向權衡。

### Solution Design
- 解決策略：在站內透過 HttpRuntime.CodegenDir 確認根目錄，再輔以站點識別掃描 App_Code.*.dll；僅用於除錯或臨時分析。

- 實施步驟：
  1. 取得 CodegenDir
  2. 搜尋對應目錄/檔案
  3. 載入反射與清理

- 關鍵程式碼/設定：
```csharp
var codegen = System.Web.HttpRuntime.CodegenDir; // 站內可用
var dlls = System.IO.Directory.GetFiles(codegen, "App_Code*.dll", SearchOption.AllDirectories);
// 警告：脆弱且版本/部署相關，僅臨時用途
```

- 實際案例：對應原文對臨時目錄抱怨；此為救急法。
- 實作環境：ASP.NET 2.0
- 實測數據：原文未提供；建議僅做臨時分析，不計入常規

Learning Points：認識 CodegenDir 與風險
- Practice：列出找到的 DLL 清單（30 分鐘）
- Assessment：知悉限制、避免濫用

---

## Case #18: 規劃測試分類與回歸策略，提升可測範圍與效率

### Problem Statement
- 業務場景：站內執行測試可能數量龐大，需要分類（Unit/Smoke/Integration）與選擇性回歸，兼顧速度與覆蓋。
- 技術挑戰：標註分類、Runner 支援、CI 流程配置。
- 影響範圍：開發者體驗、交付速度。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 測試無分類。
  2. 每次全量執行慢。
  3. CI 無差異化管線。
- 深層原因：
  - 架構層面：測試策略缺位。
  - 技術層面：Runner 未支援分類旗標。
  - 流程層面：回歸規範未制定。

### Solution Design
- 解決策略：使用 Category 標註，Runner 解析 category/name 參數（見 Case #2），CI 分成 PR 觸發跑 Smoke、夜間跑全量。

- 實施步驟：
  1. 標註 Category
  2. Runner 支援過濾
  3. CI 配置兩階段

- 關鍵程式碼/設定：
```csharp
[Category("Smoke")]
[Test] public void Cart_Add_Should_Succeed() { /* ... */ }
```

- 實際案例：原文無分類；本案補齊測試作戰策略。
- 實作環境：NUnit/NUnitLite
- 實測數據：原文未提供；建議追蹤回歸時間縮短

Learning Points：測試分層策略
- Practice：為 10 個用例加標籤並分批執行（2 小時）
- Assessment：回歸時間下降、覆蓋維持

---

案例分類
1) 按難度分類
- 入門級（適合初學者）
  - Case #14（結果輸出與解析）
  - Case #15（安全性與環境開關）
  - Case #18（測試分類策略）
- 中級（需要一定基礎）
  - Case #1（嵌入 NUnitLite）
  - Case #2（HTTP 觸發與過濾）
  - Case #3（aspnet_compiler 預編譯）
  - Case #5（手動建立 HttpContext）
  - Case #6（HTTP 整合測試）
  - Case #7（aspnet_merge 合併）
  - Case #11（BuildManager 反射）
  - Case #13（同域隔離）
- 高級（需要深厚經驗）
  - Case #4（抽離業務邏輯）
  - Case #8（Global 啟動測試）
  - Case #9（介面與注入）
  - Case #10（Mock 策略）
  - Case #16（WAP 轉換）
  - Case #17（Temporary Files 導航，僅救急）

2) 按技術領域分類
- 架構設計類：Case #4, #9, #16, #18
- 效能優化類：Case #2, #18（選擇性回歸）
- 整合開發類：Case #1, #2, #3, #6, #7, #8, #11, #14
- 除錯診斷類：Case #5, #13, #17
- 安全防護類：Case #15

3) 按學習目標分類
- 概念理解型：Case #1, #4, #9, #16, #18
- 技能練習型：Case #2, #3, #5, #6, #7, #11, #14, #15
- 問題解決型：Case #1, #3, #5, #6, #8, #13, #17
- 創新應用型：Case #2, #8, #11, #12, #14

案例關聯圖（學習路徑建議）
- 先學哪些案例？
  - 先從概念與站內執行切入：Case #1（嵌入 NUnitLite）、Case #2（HTTP Runner）
  - 補充基礎工具與站內上下文：Case #5（手動建立 HttpContext）、Case #11（BuildManager 反射）
  - 強化觀測與安全：Case #14（結果輸出）、Case #15（安全開關）
- 依賴關係
  - Case #2 依賴 Case #1（或 #11）提供站內執行能力
  - Case #10 依賴 Case #9 的抽象
  - Case #6 依賴 Case #2 的 HTTP Runner
  - Case #7 依賴 Case #3 的預編譯產物
  - Case #13 依附於任一站內 Runner（#1/#11）以做隔離
  - Case #12 可在 #1 不可用時替代
- 完整學習路徑建議
  1) 站內測試能力：Case #1 → Case #2 → Case #14 → Case #15  
  2) 測試上下文與隔離：Case #5 → Case #13  
  3) 外部/CI 整合路徑 A（保留 Web Site）：Case #3 → Case #7 →（可選）Case #6  
  4) 架構演進路徑 B（提昇可測性）：Case #4 → Case #9 → Case #10 →（可選）Case #16  
  5) 例外/救急與擴展：Case #11 → Case #12 → Case #17 → Case #18

說明
- 實測數據：原文未提供具體數據，故各案例均以「建議追蹤指標」描述；實務上可量測覆蓋率、執行耗時、失敗率與回歸時間。
- 程式碼：依 .NET 2.0/ASP.NET 2.0 為基準撰寫，NUnitLite API 可能因版本差異需調整。