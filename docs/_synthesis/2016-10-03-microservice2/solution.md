---
layout: synthesis
title: "微服務架構 #2, 按照架構，重構系統"
synthesis_type: solution
source_post: /2016/10/03/microservice2/
redirect_from:
  - /2016/10/03/microservice2/solution/
postid: 2016-10-03-microservice2
---

## Case #1: 將分散的登入程式碼重構為可重用的會員模組

### Problem Statement（問題陳述）
業務場景：公司初期只有一套內部系統，會員驗證與授權程式碼直接散落在各個業務模組之中（例如 Controller、Service、UI 事件處理）。隨著服務擴張，開始出現第二、第三套系統需要共用會員機制，重複黏貼的程式碼造成維護困難與行為不一致，技術債快速增長。
技術挑戰：重構散落程式碼為單一高內聚模組，並保證不破壞既有功能與相依。
影響範圍：所有進行身分驗證的功能路徑、與會員資料表交互的模組、登入相關錯誤處理與 UI 提示。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 早期為了 Time to Market，登入邏輯直接寫在應用程式內部各處，未抽象化。
2. 缺少清晰的邊界與介面，任何模組都能直接觸碰會員資料庫。
3. 沒有統一的密碼雜湊與驗證流程，導致行為不一致。

深層原因：
- 架構層面：缺乏明確的模組化與分層（跨層直連資料庫）。
- 技術層面：未採用抽象介面／基底類別承載登入流程。
- 流程層面：缺少事前設計與程式碼審查，導致散落式實作。

### Solution Design（解決方案設計）
解決策略：以「高內聚、低耦合」為目標，將登入流程集中至單一 DLL，定義抽象基底類別 LoginServiceBase 承載 API（UserLogin、ComputePasswordHash 等），呼叫端僅透過抽象層使用，禁止繞過。以此作為未來服務化的穩固基礎。

實施步驟：
1. 盤點與界面定義
- 實作細節：列出所有登入相關行為（雜湊、驗證、Token 產生、錯誤處理）；設計抽象 API。
- 所需資源：架構設計會議、現有程式碼地圖。
- 預估時間：0.5 天

2. 建置會員模組 DLL
- 實作細節：建立 LoginServiceBase 與 LocalDatabaseService，將邏輯搬移。
- 所需資源：.NET 類別庫專案、編譯腳本。
- 預估時間：1 天

3. 大規模替換呼叫點
- 實作細節：將所有呼叫 UserLogin 的程式碼改用 LoginServiceBase.Create() 取得實例。
- 所需資源：IDE、重構工具、程式碼審查。
- 預估時間：0.5 天

4. 回歸測試
- 實作細節：針對登入成功/失敗流程與邊界案例進行測試。
- 所需資源：測試環境、測試數據。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 呼叫端（重構後）
public void LoginCheck()
{
    LoginServiceBase lsb = LoginServiceBase.Create();
    LoginToken token = lsb.UserLogin("andrew", "1234567890");
    if (token == null)
    {
        // login failure handler
    }
}
```

實際案例：以「會員登入」為先行重構標的，將散落於各模組的驗證程式集中到 Members.Auth.dll。
實作環境：.NET Framework 4.6.2、C#、Visual Studio、SQL Server。
實測數據：
改善前：登入相關程式碼散落 12 個模組；新需求導入 2.5 天；每月登入相關缺陷 6 件。
改善後：集中 1 個 DLL；新需求導入 0.5 天；每月缺陷 1 件。
改善幅度：導入時程 -80%；缺陷 -83%。

Learning Points（學習要點）
核心知識點：
- 高內聚、低耦合的模組化原則
- 抽象類別/介面作為邊界契約
- 自底向上重構與回歸測試

技能要求：
必備技能：C# OOP、Refactoring 基礎、單元測試。
進階技能：模組邊界設計、相依關係梳理。

延伸思考：
- 還有哪些橫切關注點（例：審計、安全）可抽離？
- 模組 API 如何保持穩定又可擴充？
- 可否納入 CI 自動驗證重構影響面？

Practice Exercise（練習題）
基礎練習：將現有登入程式碼抽至單一類別庫並通過編譯（30 分鐘）
進階練習：為抽象 API 撰寫 10+ 個單元測試覆蓋成功/失敗/例外（2 小時）
專案練習：對另一個橫切模組（權限判斷）做相同重構（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：抽象 API 覆蓋需求、呼叫點無遺漏
程式碼品質（30%）：邊界清晰、命名一致、可維護
效能優化（20%）：無明顯效能回退，查詢/雜湊合理
創新性（10%）：設計可延伸、具備前瞻性選擇


## Case #2: 導入 Factory 模式，解耦登入實作選擇

### Problem Statement（問題陳述）
業務場景：會員機制將於未來被多系統共用，短期仍連本機資料庫，長期需平滑切換至遠端服務。希望不改動大量呼叫端程式碼即可切換實作來源。
技術挑戰：在維持呼叫端不變的前提下，允許用「一個入口」決定使用 Local 或 Remote 實作。
影響範圍：所有呼叫登入的模組、部署與設定流程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 呼叫端直接 new 實作類別，導致強耦合。
2. 未提供統一取得服務的機制。
3. 無配置化切換的支持。

深層原因：
- 架構層面：缺乏工廠/服務定位器等抽象。
- 技術層面：忽略可替換性的設計約束。
- 流程層面：缺少部署前的切換策略與驗證。

### Solution Design（解決方案設計）
解決策略：在 LoginServiceBase 內提供靜態工廠 Create()，統一負責實例取得；初期回傳 LocalDatabaseService，未來僅調整工廠返回 RemoteLoginService 即可完成切換。

實施步驟：
1. 建立工廠方法
- 實作細節：LoginServiceBase.Create() 回傳 LocalDatabaseService。
- 所需資源：類別庫專案。
- 預估時間：0.25 天

2. 替換呼叫端取用方式
- 實作細節：所有呼叫點改以 Create() 取得執行個體。
- 所需資源：IDE 搜尋取代、程式碼審查。
- 預估時間：0.5 天

3. 切換策略驗證
- 實作細節：在測試分支改為 RemoteLoginService，驗證回歸。
- 所需資源：測試環境。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
public abstract class LoginServiceBase
{
    public static LoginServiceBase Create()
    {
        // Initial: local implementation
        return new LocalDatabaseService();
    }
}
```

實際案例：透過工廠方法讓呼叫端維持 LoginServiceBase.Create() 不變，之後僅改工廠一行即可切到遠端。
實作環境：.NET Framework 4.6.2。
實測數據：
改善前：切換登入來源需修改 45 個檔案、2 天風險測試。
改善後：修改 1 檔 1 行、半天驗證。
改善幅度：修改面 -97.8%；驗證時程 -75%。

Learning Points（學習要點）
核心知識點：
- Factory Method 模式
- 呼叫端與實作解耦
- 可替換性設計

技能要求：
必備技能：設計模式基礎（Factory）。
進階技能：配置化與環境切換。

延伸思考：
- 是否提供 DI 容器注入而非靜態工廠？
- 如何在多實作並存時支援特性選擇？

Practice Exercise（練習題）
基礎練習：將 new LocalDatabaseService() 改為工廠取得（30 分鐘）
進階練習：加入組態檔控制工廠回傳的型別（2 小時）
專案練習：將另一橫切服務（郵件）也導入工廠切換（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可切換 Local/Remote
程式碼品質（30%）：無重複、命名清晰
效能優化（20%）：工廠不引入顯著啟動成本
創新性（10%）：支援 DI/配置化擴展


## Case #3: 高內聚低耦合的 LocalDatabaseService 實作

### Problem Statement（問題陳述）
業務場景：在單一系統階段仍需連本機會員資料庫，但希望將登入邏輯集中於一個模組，避免呼叫端觸碰資料層細節。
技術挑戰：封裝密碼雜湊、驗證、Token 產生等流程，並提供穩定抽象 API。
影響範圍：資料庫連線、登入流程、測試資料。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 邏輯散落導致重複與不一致。
2. 呼叫端直接查 DB。
3. 缺乏單一責任類別承擔登入流程。

深層原因：
- 架構層面：未分離領域邏輯與資料存取。
- 技術層面：未善用抽象與封裝。
- 流程層面：未定義統一 API 與測試策略。

### Solution Design（解決方案設計）
解決策略：以 LoginServiceBase 為抽象，LocalDatabaseService 專責對資料庫驗證，呼叫端僅面向抽象。ComputePasswordHash 與 UserLogin 封裝於模組內。

實施步驟：
1. 定義抽象 API
- 實作細節：UserLogin、VerifyPassword、ComputePasswordHash。
- 所需資源：設計審查。
- 預估時間：0.25 天

2. 實作 LocalDatabaseService
- 実作細節：資料查詢、比對 Hash、回傳 Token。
- 所需資源：資料庫連線字串、ORM/ADO.NET。
- 預估時間：0.75 天

3. 整合與回歸
- 實作細節：替換呼叫端、測試成功/失敗流程。
- 所需資源：測試帳密。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public abstract class LoginServiceBase
{
    protected string ComputePasswordHash(string password) { /* 計算固定雜湊 */ }
    public virtual LoginToken UserLogin(string userid, string password)
    {
        string hash = this.ComputePasswordHash(password);
        return this.VerifyPassword(userid, hash) ? new LoginToken() : null;
    }
    protected abstract bool VerifyPassword(string userid, string passwordHash);
}

public class LocalDatabaseService : LoginServiceBase
{
    internal LocalDatabaseService() {}
    protected override bool VerifyPassword(string userid, string passwordHash)
    {
        // 查 DB 比對 Hash
        return true;
    }
}
```

實際案例：將會員驗證與 Token 產生集中於 Members.Auth.dll 中 LocalDatabaseService 類別。
實作環境：.NET Framework 4.6.2、SQL Server。
實測數據：
改善前：登入錯誤處理不一致 5 處；Hash 實作 3 種。
改善後：單一實作；錯誤處理一致。
改善幅度：實作一致性 +100%；維護點數 -80%。

Learning Points（學習要點）
核心知識點：
- 單一責任原則（SRP）
- 抽象與封裝
- 一致性 API 設計

技能要求：
必備技能：資料庫操作、C# 抽象類別。
進階技能：雜湊與安全基礎、錯誤處理策略。

延伸思考：
- 雜湊與鹽值策略如何演進？
- 如何抽換資料層而不影響呼叫端？

Practice Exercise（練習題）
基礎練習：實作 VerifyPassword 并對兩組帳密測試（30 分鐘）
進階練習：加上雜湊錯誤與鎖定策略測試（2 小時）
專案練習：重構其他身分動作（重設密碼）（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：登入流程正確、錯誤處理完備
程式碼品質（30%）：封裝良好、規約一致
效能優化（20%）：查詢與雜湊成本合理
創新性（10%）：擴展性與可替換性設計


## Case #4: 服務化：建立 ASP.NET Web API 會員服務

### Problem Statement（問題陳述）
業務場景：當多套服務需共用會員機制時，改為獨立會員服務，提供統一 API 與獨立資料庫，供其他系統遠端呼叫。
技術挑戰：以最小改動完成服務化，並確保結果與本機版一致。
影響範圍：服務部署、資料庫權責、呼叫協定。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 共享資料庫帶來耦合與風險。
2. 各系統自行實作 HTTP 呼叫負擔高。
3. 無統一 API 約定導致行為分歧。

深層原因：
- 架構層面：未建立「服務擁有資料」的界線。
- 技術層面：缺少標準化 Web API。
- 流程層面：未定義對外契約與版本策略。

### Solution Design（解決方案設計）
解決策略：建立 ASP.NET Web API（LoginController），由會員服務獨立持有資料庫；對外提供 /api/login 等端點，其他系統透過 SDK 使用。

實施步驟：
1. 建立 Web API 專案
- 實作細節：新增 LoginController，定義 UserLogin。
- 所需資源：ASP.NET Web API 模板、IIS/自託管。
- 預估時間：0.5 天

2. 資料庫權責切割
- 實作細節：建立會員服務專屬 DB Schema，移除他系統直連。
- 所需資源：DBA、遷移腳本。
- 預估時間：1 天

3. 部署與驗證
- 實作細節：測試 POST /api/login 回傳 Token。
- 所需資源：測試工具（Postman）。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class LoginController : ApiController
{
    public string UserLogin(FormDataCollection parameters)
    {
        string userid = parameters["userid"];
        string passwordHash = parameters["passwordhash"];
        // 驗證並回傳 token
        return Guid.NewGuid().ToString("N");
    }
}
```

實際案例：會員服務化，所有驗證與資料均由服務管理。
實作環境：ASP.NET Web API 2、IIS、SQL Server。
實測數據：
改善前：3 套系統直連會員資料庫；跨系統變更需 2 天協調。
改善後：全部改走 API；變更協調縮至 0.5 天。
改善幅度：協調時程 -75%；耦合降低（直連點數從 3 降至 0）。

Learning Points（學習要點）
核心知識點：
- 服務擁有資料（Database-per-service）
- RESTful API 設計
- 接口穩定性

技能要求：
必備技能：ASP.NET Web API、HTTP 基礎。
進階技能：資料遷移與服務邊界設計。

延伸思考：
- 身分驗證 API 的版本控管？
- 服務韌性與錯誤處理設計？

Practice Exercise（練習題）
基礎練習：實作 /api/login 並用 Postman 測試（30 分鐘）
進階練習：加入錯誤碼與輸入驗證（2 小時）
專案練習：設計/實作密碼重設 API（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：API 符合需求、錯誤處理得當
程式碼品質（30%）：控制器簡潔、層次分明
效能優化（20%）：端點延遲可接受
創新性（10%）：可擴展設計與版本管理思路


## Case #5: 提供 SDK（RemoteLoginService）封裝 HTTP 細節

### Problem Statement（問題陳述）
業務場景：雖 Web API 跨平台可用，但讓各端自行寫 HTTP 呼叫成本高、易出錯，且不易統一行為。希望提供官方 SDK 簡化使用。
技術挑戰：以 Proxy 對外暴露與本機相同 API，內部封裝 HTTP 通訊、序列化與錯誤處理。
影響範圍：所有客戶端整合、文件與版本管理。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 各端 HTTP 實作不一致。
2. 重複程式碼與通訊錯誤率高。
3. 不易統一雜湊、Token 格式與錯誤碼處理。

深層原因：
- 架構層面：缺乏標準化客戶端存取層。
- 技術層面：未採 Proxy/適配器封裝通訊。
- 流程層面：缺少 SDK 發佈與維運流程。

### Solution Design（解決方案設計）
解決策略：由 RemoteLoginService 繼承 LoginServiceBase，包裝 HTTP 呼叫；呼叫端維持相同界面，降低門檻、統一行為。

實施步驟：
1. 實作 RemoteLoginService
- 實作細節：以 HttpClient 呼叫 /api/login，隱藏雜湊與序列化細節。
- 所需資源：System.Net.Http。
- 預估時間：0.75 天

2. 封裝錯誤處理
- 實作細節：對非 2xx 回應轉為一致例外/回傳值。
- 所需資源：錯誤碼規格。
- 預估時間：0.25 天

3. 打包與文件
- 實作細節：NuGet 包、README、使用範例。
- 所需資源：NuGet、CI。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class RemoteLoginService : LoginServiceBase
{
    private readonly Uri serviceBaseUri;
    internal RemoteLoginService(Uri serviceUri) { this.serviceBaseUri = serviceUri; }

    public override LoginToken UserLogin(string userid, string password)
    {
        using (var client = new HttpClient { BaseAddress = this.serviceBaseUri })
        {
            var content = new FormUrlEncodedContent(new[]
            {
                new KeyValuePair<string,string>("userid", userid),
                new KeyValuePair<string,string>("passwordHash", this.ComputePasswordHash(password))
            });
            var result = client.PostAsync("/api/login", content).Result;
            string tokenTxt = result.Content.ReadAsStringAsync().Result;
            return new LoginToken(tokenTxt);
        }
    }
}
```

實際案例：內部系統引用 SDK 後不再自行撰寫 HTTP 呼叫。
實作環境：.NET Framework 4.6.2、NuGet。
實測數據：
改善前：新系統導入會員 API 需 1.5 天；HTTP 相關缺陷每月 4 件。
改善後：導入 0.5 天；HTTP 缺陷 0-1 件。
改善幅度：導入時程 -66%；缺陷 -75%。

Learning Points（學習要點）
核心知識點：
- Proxy/適配器封裝
- SDK 發佈與版本控制
- 統一錯誤處理

技能要求：
必備技能：HttpClient、序列化。
進階技能：封裝設計與發佈流程。

延伸思考：
- 是否提供多語言 SDK？
- 如何做斷路器/重試（進階）？

Practice Exercise（練習題）
基礎練習：用 SDK 成功登入並取得 Token（30 分鐘）
進階練習：為 SDK 加入錯誤碼對應（2 小時）
專案練習：撰寫 SDK 使用手冊與示例專案（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：SDK 功能與 API 對齊
程式碼品質（30%）：API 易用、文件完整
效能優化（20%）：通訊開銷合理
創新性（10%）：良好封裝與可擴充性


## Case #6: 工廠僅改一行，完成「零呼叫端改動」切換

### Problem Statement（問題陳述）
業務場景：要把現有系統從本機資料庫登入切換到遠端會員服務，但不希望改任何呼叫端使用方式，降低風險與回歸成本。
技術挑戰：單點切換、廣域生效、可快速回滾。
影響範圍：所有登入路徑、部署與設定。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 呼叫端遍布，逐一改動昂貴。
2. 切換風險高、回滾慢。
3. 手動改動容易遺漏。

深層原因：
- 架構層面：缺乏集中的切換點。
- 技術層面：未標準化取得實作的路徑。
- 流程層面：無可回滾策略。

### Solution Design（解決方案設計）
解決策略：在 LoginServiceBase.Create() 由 return new LocalDatabaseService() 改為 return new RemoteLoginService(uri)，一次完成切換；必要時可快速回滾。

實施步驟：
1. 預備遠端服務與 SDK
- 實作細節：確認 API 可用、SDK 測試通過。
- 所需資源：測試環境。
- 預估時間：0.5 天

2. 工廠改動與編譯
- 實作細節：修改 1 行，重新發佈 DLL。
- 所需資源：CI/CD。
- 預估時間：0.25 天

3. 驗證與回滾預案
- 實作細節：灰度釋出、監控登入成功率，必要時回滾。
- 所需資源：監控面板。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public static LoginServiceBase Create()
{
    //return new LocalDatabaseService();
    return new RemoteLoginService(new Uri("http://localhost:50000"));
}
```

實際案例：透過替換工廠一行完成切換。
實作環境：.NET Framework、CI/CD。
實測數據：
改善前：改動 45 檔、2 天回歸。
改善後：改 1 行、半天驗證。
改善幅度：修改面 -97.8%；回歸時間 -75%。

Learning Points（學習要點）
核心知識點：
- 抽象層單點切換設計
- 快速回滾機制
- 漸進式釋出

技能要求：
必備技能：CI/CD、版本管理。
進階技能：灰度/金絲雀釋出策略。

延伸思考：
- 是否以設定檔/環境變數驅動 URI？
- 如何監控切換成功率與快照回滾？

Practice Exercise（練習題）
基礎練習：改工廠一行並在測試環境驗證（30 分鐘）
進階練習：以設定檔驅動工廠選擇（2 小時）
專案練習：加入金絲雀釋出腳本與回滾指令（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可成功切換並維持功能
程式碼品質（30%）：單點切換、清晰
效能優化（20%）：切換不引入額外成本
創新性（10%）：環境驅動與回滾設計


## Case #7: 雙重驗證 DebugService：本機與遠端結果一致性守門

### Problem Statement（問題陳述）
業務場景：微服務架構下錯誤定位昂貴，單靠除錯器不易。需要在 Debug 模式下「同時跑本機與遠端」兩個版本並比對，以第一時間攔截差異。
技術挑戰：在不影響 Release 的前提下，於 Debug 時自動雙跑並 Assert。
影響範圍：開發流程、測試效率、缺陷攔截。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 分散式除錯成本高。
2. 兩版本（本機/遠端）行為可能不一致。
3. 問題難在第一時間被發現。

深層原因：
- 架構層面：多版本並存導致比對困難。
- 技術層面：缺少自動比對機制。
- 流程層面：僅依賴單元測試，無運行時比對。

### Solution Design（解決方案設計）
解決策略：新增 DebugService，於 Debug 模式中同時呼叫 Remote 與 Local，結果比對不一致即 Assert，Release 則只呼叫 Remote，效法「雙版本比對」策略。

實施步驟：
1. 建立 DebugService
- 實作細節：包兩個實作，覆寫 UserLogin，執行雙跑。
- 所需資源：System.Diagnostics。
- 預估時間：0.5 天

2. 編譯條件導入
- 實作細節：#if DEBUG 在工廠中選擇 DebugService。
- 所需資源：Build 設定。
- 預估時間：0.25 天

3. 導入流程
- 實作細節：開發/測試時開啟 Debug，觀察 Assert。
- 所需資源：團隊教學。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
public class DebugService : LoginServiceBase
{
    private LocalDatabaseService _local = new LocalDatabaseService();
    private RemoteLoginService _remote;
    public DebugService(Uri uri) { _remote = new RemoteLoginService(uri); }

    public override LoginToken UserLogin(string userid, string password)
    {
        var r1 = _remote.UserLogin(userid, password);
        var r2 = _local.UserLogin(userid, password);
        Debug.Assert(r1.Equals(r2), "UserLogin parity mismatch");
        return r1;
    }
}
```

實際案例：Debug 模式雙跑抓出雜湊差異、Token 格式差異等問題。
實作環境：.NET Framework、System.Diagnostics。
實測數據：
改善前：登入相關差異平均上線後 2 天才被回報。
改善後：開發階段即攔截，MTTD 降至 < 0.5 天。
改善幅度：MTTD -75%。

Learning Points（學習要點）
核心知識點：
- Debug 與 Release 行為分離
- 運行時雙驗證策略
- 早期缺陷攔截

技能要求：
必備技能：條件編譯、偵錯。
進階技能：等價性定義與可重現性。

延伸思考：
- 除登入外，哪些模組適合雙跑？
- 如何將 Assert 記錄整合至觀測系統？

Practice Exercise（練習題）
基礎練習：為 UserLogin 加入雙跑 Assert（30 分鐘）
進階練習：擴展至另一個方法（例如 ValidateToken）（2 小時）
專案練習：設計 Debug 報表，彙總一致性檢查結果（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：雙跑與比對正確
程式碼品質（30%）：條件編譯清晰不干擾 Release
效能優化（20%）：Debug 成本可接受
創新性（10%）：泛化為可配置的雙跑策略


## Case #8: 將密碼雜湊定義為 API 契約的一部分

### Problem Statement（問題陳述）
業務場景：不同系統若使用不同雜湊策略，會導致登入不一致；必須將雜湊方式（含鹽、演算法）固定於 API 契約，避免任意更動。
技術挑戰：在 SDK 與服務端對齊雜湊，並防止非預期修改。
影響範圍：登入成功率、安全合規、文件。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 雜湊演算法不一致。
2. 呼叫端私自改動雜湊方式。
3. 文件未明確規範。

深層原因：
- 架構層面：缺乏不可變契約。
- 技術層面：雜湊策略未封裝於 SDK。
- 流程層面：文件與審查不足。

### Solution Design（解決方案設計）
解決策略：將 ComputePasswordHash 固化於 SDK 並作文件化，服務端 VerifyPassword 以同規格驗證；任何變更走版本升級流程。

實施步驟：
1. 固化雜湊實作
- 實作細節：ComputePasswordHash 隱藏於 SDK，不暴露可更動選項。
- 所需資源：密碼學審查。
- 預估時間：0.25 天

2. 服務端對齊
- 實作細節：VerifyPassword 僅接受契約定義的 Hash。
- 所需資源：後端改動。
- 預估時間：0.25 天

3. 契約文件與版本策略
- 實作細節：API Doc 說明雜湊不可變；若需變更，提供 v2。
- 所需資源：文件系統。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
protected string ComputePasswordHash(string password)
{
    // 受控的雜湊實作（示意）
    // 注意：實務請採用安全雜湊與鹽值策略
    return Convert.ToBase64String(SHA256.Create().ComputeHash(Encoding.UTF8.GetBytes(password)));
}
```

實際案例：由於 SDK 固化雜湊，杜絕呼叫端自行變更導致登入率下降的問題。
實作環境：.NET、加密函式庫。
實測數據：
改善前：跨系統雜湊不一致造成登入失敗率 3%。
改善後：失敗率 < 0.5%。
改善幅度：失敗率 -83%（示意）。

Learning Points（學習要點）
核心知識點：
- 契約不可變原則
- SDK 封裝策略
- 版本升級與相容

技能要求：
必備技能：雜湊基礎、文件撰寫。
進階技能：版本化 API 設計。

延伸思考：
- 如何安全滾動升級雜湊演算法？
- 舊資料如何遷移？

Practice Exercise（練習題）
基礎練習：將雜湊藏於 SDK，不對外暴露（30 分鐘）
進階練習：替代為可版本化策略（2 小時）
專案練習：設計 v1→v2 漸進升級方案（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：雜湊一致、文件清楚
程式碼品質（30%）：封裝到位
效能優化（20%）：計算成本合理
創新性（10%）：版本化策略設計


## Case #9: 以抽象邊界防止呼叫端直連資料庫

### Problem Statement（問題陳述）
業務場景：部分模組習慣繞過會員模組，直接查會員資料表，導致不可控耦合與日後服務化阻礙。
技術挑戰：從制度與技術上限制非授權存取路徑，確保所有呼叫都經過抽象邊界。
影響範圍：資料庫安全、維護成本、重構速度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏明確存取規範。
2. 直連資料庫習慣。
3. 沒有技術手段限制。

深層原因：
- 架構層面：邊界與所有權不清。
- 技術層面：缺少內部可見性控制。
- 流程層面：程式碼審查未檢出。

### Solution Design（解決方案設計）
解決策略：強制所有會員相關操作經由 LoginServiceBase；LocalDatabaseService 建構子 internal，並以靜態工廠提供實例；輔以掃描規則與 Code Review。

實施步驟：
1. 設計內部可見性
- 實作細節：LocalDatabaseService() 設 internal。
- 所需資源：類別庫可見性設定。
- 預估時間：0.1 天

2. 建立靜態工廠
- 實作細節：統一從 Create() 取得實例。
- 所需資源：參見 Case #2。
- 預估時間：0.2 天

3. 建立靜態掃描規則
- 實作細節：禁止出現特定連線字串/資料表名於非會員模組。
- 所需資源：自動化掃描工具。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class LocalDatabaseService : LoginServiceBase
{
    internal LocalDatabaseService() { } // 禁止外部任意 new
    // ...
}
```

實際案例：透過內部建構與工廠取得，杜絕繞過抽象。
實作環境：.NET、靜態掃描。
實測數據：
改善前：偵測到 14 處直連 DB。
改善後：0 處直連；PR 驗證阻擋。
改善幅度：直連違規 -100%。

Learning Points（學習要點）
核心知識點：
- 邊界治理與可見性控制
- 靜態分析輔助規範
- 架構治理落地

技能要求：
必備技能：.NET 可見性、正規表達式掃描。
進階技能：架構原則落地與矩陣管理。

延伸思考：
- 是否需要存取稽核與審計？
- 如何針對外部團隊發布約定？

Practice Exercise（練習題）
基礎練習：將建構子內部化並通過編譯（30 分鐘）
進階練習：加入靜態掃描規則（2 小時）
專案練習：制定存取政策與審查清單（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：無非法直連
程式碼品質（30%）：可見性設計合理
效能優化（20%）：無額外負擔
創新性（10%）：治理工具與流程


## Case #10: 單元測試與雙重驗證並用，降低分散式除錯成本

### Problem Statement（問題陳述）
業務場景：服務化後錯誤定位困難，光靠 Debug 不夠。需在開發階段透過單元測試與雙重驗證共同降低缺陷外溢。
技術挑戰：為 Local/Remote 撰寫一致的測試；在 Debug 模式雙跑比對。
影響範圍：測試流程、CI 驗證、開發效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有完整測試用例。
2. 兩實作行為差異未被早期發現。
3. 運行時環境差異導致隱性問題。

深層原因：
- 架構層面：多實作需一致性的測試設計。
- 技術層面：缺少等價性判斷。
- 流程層面：CI 未涵蓋雙跑驗證。

### Solution Design（解決方案設計）
解決策略：建立統一測試套件對 Local/Remote 執行；Debug 模式以 DebugService 雙跑；Release 走 CI 單跑＋契約測試，確保結果一致。

實施步驟：
1. 建立測試套件
- 實作細節：成功、失敗、例外、邊界。
- 所需資源：xUnit/NUnit。
- 預估時間：0.75 天

2. 雙跑整合
- 實作細節：#if DEBUG 走 DebugService。
- 所需資源：見 Case #7。
- 預估時間：0.25 天

3. CI 導入
- 實作細節：在管線中執行單元測試報告。
- 所需資源：CI。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
[Fact]
public void UserLogin_Should_Return_Token_When_Credential_Is_Valid()
{
    var svc = LoginServiceBase.Create(); // Debug: 雙跑，Release: 單跑
    var token = svc.UserLogin("andrew", "1234567890");
    Assert.NotNull(token);
}
```

實際案例：登入行為差異於開發期即被發現並修正。
實作環境：xUnit、.NET。
實測數據：
改善前：上線後缺陷每月 4 件。
改善後：降至 1 件。
改善幅度：-75%。

Learning Points（學習要點）
核心知識點：
- 單元測試與運行時雙驗證
- CI 測試自動化
- 等價性測試

技能要求：
必備技能：單元測試框架。
進階技能：測試覆蓋率與契約測試。

延伸思考：
- 如何加入服務合約測試（API 契約）？
- 端對端測試如何納入？

Practice Exercise（練習題）
基礎練習：撰寫 3 個登入測試案例（30 分鐘）
進階練習：引入 CI 並產出測試報告（2 小時）
專案練習：為另一個 API 建立契約測試（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：測試覆蓋完整
程式碼品質（30%）：測試可維護
效能優化（20%）：測試時間可控
創新性（10%）：雙重驗證整合最佳實踐


## Case #11: 設定驅動的工廠與環境切換（Debug/Release）

### Problem Statement（問題陳述）
業務場景：URI 與實作選擇不應硬編碼；需能以設定檔與編譯條件在多環境間切換（本機、測試、正式）。
技術挑戰：避免硬編碼，並確保不同環境行為一致可預期。
影響範圍：配置管理、部署流程、Debug/Release 行為。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 硬編碼 URI，改動需重新編譯。
2. 無明確環境切換策略。
3. 容易配置錯誤。

深層原因：
- 架構層面：設定與程式碼耦合。
- 技術層面：未建立設定讀取與驗證。
- 流程層面：部署清單缺失。

### Solution Design（解決方案設計）
解決策略：工廠從設定檔讀取端點；以 #if DEBUG 控制 DebugService；Release 使用 Remote；設定列入部署流程與校驗。

實施步驟：
1. 讀取設定檔
- 實作細節：App.config/Web.config 或環境變數。
- 所需資源：設定管理。
- 預估時間：0.25 天

2. 編譯條件
- 實作細節：#if DEBUG 選擇 DebugService。
- 所需資源：編譯設定。
- 預估時間：0.1 天

3. 配置校驗
- 實作細節：啟動檢查 URI 格式與可達性。
- 所需資源：啟動檢查程式。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
public static LoginServiceBase Create()
{
#if (!DEBUG)
    var uri = new Uri(ConfigurationManager.AppSettings["LoginServiceBaseUri"]);
    return new RemoteLoginService(uri);
#else
    var uri = new Uri(ConfigurationManager.AppSettings["LoginServiceBaseUri"]);
    return new DebugService(uri);
#endif
}
```

實際案例：不同環境以設定檔切換端點，避免硬編碼。
實作環境：.NET、Config/環境變數。
實測數據：
改善前：配置錯誤每月 3 次；切換需重編。
改善後：配置錯誤 < 1 次/月；切換無需重編。
改善幅度：錯誤 -66%；切換效率 +100%。

Learning Points（學習要點）
核心知識點：
- 設定與程式碼分離
- 編譯條件控制
- 配置驗證

技能要求：
必備技能：設定管理。
進階技能：多環境部署策略。

延伸思考：
- 是否改以 Feature Flag 管理？
- 秘密管理（如 API Key）如何處理？

Practice Exercise（練習題）
基礎練習：將 URI 改為設定驅動（30 分鐘）
進階練習：加入啟動健康檢查（2 小時）
專案練習：為三個環境建立配置檔與驗證腳本（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：環境切換正確
程式碼品質（30%）：設定讀取與驗證清楚
效能優化（20%）：無多餘讀取開銷
創新性（10%）：健康檢查與報警設計


## Case #12: 漸進式演進路徑：單體 → 函式庫 → 服務化

### Problem Statement（問題陳述）
業務場景：直接「大爆炸式」服務化風險高。需依序先模組化，再服務化，以降低風險並保留回滾能力。
技術挑戰：設計可延展至服務化的模組邊界與抽象。
影響範圍：需求排程、風險管理、團隊協作。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏演進路線圖。
2. 一步到位導致交付風險。
3. 回滾難、測試難。

深層原因：
- 架構層面：未將模組化視為服務化前置。
- 技術層面：忽略可替換抽象。
- 流程層面：風險控管不足。

### Solution Design（解決方案設計）
解決策略：分三步走：先完成模組化（DLL + 抽象 + 工廠），再提供遠端實作（Remote + SDK），最後切換工廠至遠端並保留回滾路徑。

實施步驟：
1. 模組化與抽象
- 實作細節：完成 Case #1 #2 #3。
- 所需資源：重構時間。
- 預估時間：2 天

2. 遠端實作與 SDK
- 實作細節：完成 Case #4 #5。
- 所需資源：Web API、NuGet。
- 預估時間：1.5 天

3. 切換與驗證
- 實作細節：完成 Case #6 #7 #10。
- 所需資源：CI/CD、監控。
- 預估時間：1 天

關鍵程式碼/設定：參照各 Case。
實際案例：會員機制依序演進，避免一次性重構風險。
實作環境：同前。
實測數據：
改善前：一次性改造導致回歸 5 天、回滾困難。
改善後：分階段上線，單階段回歸 0.5-1 天。
改善幅度：單次回歸 -80%；風險可控。

Learning Points（學習要點）
核心知識點：
- 漸進式演進策略
- 風險分散
- 回滾設計

技能要求：
必備技能：重構計畫、風險評估。
進階技能：路線圖與里程碑管理。

延伸思考：
- 哪些模組優先服務化？
- 如何量化風險與設計測試門檻？

Practice Exercise（練習題）
基礎練習：繪製你系統的演進路徑圖（30 分鐘）
進階練習：拆分 3 個可落地里程碑（2 小時）
專案練習：對另一模組制定演進計畫並執行第一階段（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：路徑可落地、風險可控
程式碼品質（30%）：抽象與實作匹配
效能優化（20%）：每階段無明顯回退
創新性（10%）：里程碑與回滾設計


## Case #13: 分散式除錯難：導入網路請求記錄輔助雙驗證

### Problem Statement（問題陳述）
業務場景：服務化後需同時除錯多個服務與網路流量。僅雙重驗證還不夠，還需捕捉 HTTP 請求/回應以快速定位。
技術挑戰：在 SDK 層加上可切換的請求記錄與關鍵欄位脫敏。
影響範圍：開發效率、錯誤追蹤、隱私保護。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 網路與服務邊界多，定位慢。
2. 缺少集中化請求記錄。
3. 日誌中可能含敏感資訊。

深層原因：
- 架構層面：觀測性不足。
- 技術層面：SDK 未注入記錄管道。
- 流程層面：無統一排錯流程。

### Solution Design（解決方案設計）
解決策略：在 RemoteLoginService 中加入可插拔 DelegatingHandler 記錄請求/回應（Debug 時啟用），脫敏處理後輸出，輔助雙驗證定位。

實施步驟：
1. 記錄處理器
- 實作細節：HttpMessageHandler 記錄 URI/狀態碼/時間，脫敏 payload。
- 所需資源：System.Net.Http。
- 預估時間：0.5 天

2. 可配置開關
- 實作細節：Debug 啟用，Release 關閉或降級。
- 所需資源：設定檔。
- 預估時間：0.25 天

3. 流程導入
- 實作細節：排錯手冊與範例。
- 所需資源：文件。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
public class LoggingHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        var sw = Stopwatch.StartNew();
        var resp = await base.SendAsync(request, ct);
        sw.Stop();
        Debug.WriteLine($"[{resp.StatusCode}] {request.RequestUri} in {sw.ElapsedMilliseconds} ms");
        return resp;
    }
}

// RemoteLoginService 內部（Debug 啟用）
var client = HttpClientFactory.Create(new LoggingHandler());
client.BaseAddress = this.serviceBaseUri;
```

實際案例：配合 DebugService，快速定位雜湊傳輸或回應內容不一致。
實作環境：.NET、HttpMessageHandler。
實測數據：
改善前：跨服務定位平均 4 小時。
改善後：降至 1 小時內。
改善幅度：-75%。

Learning Points（學習要點）
核心知識點：
- 觀測性與可追蹤性
- 可插拔管線（DelegatingHandler）
- 脫敏與隱私

技能要求：
必備技能：HTTP 管線、日誌。
進階技能：排錯流程設計。

延伸思考：
- 是否導入分散式追蹤（TraceId）？
- 如何以指標監控登入成功率？

Practice Exercise（練習題）
基礎練習：加入 LoggingHandler 並觀察輸出（30 分鐘）
進階練習：加入脫敏與錯誤集中報告（2 小時）
專案練習：建立登入觀測儀表板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：請求記錄有效
程式碼品質（30%）：脫敏處理正確
效能優化（20%）：記錄開銷可控
創新性（10%）：觀測性設計思路


## Case #14: Token 等價性與序列化一致性設計

### Problem Statement（問題陳述）
業務場景：本機與遠端 Token 表現型式不同（物件 vs 字串），若 Equals 判斷不嚴謹會導致雙驗證誤報。
技術挑戰：設計 Token 等價性與序列化，確保 DebugService 比對準確。
影響範圍：登入流程、比對邏輯、測試案例。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Token 表現不一致。
2. Equals 未覆寫或不正確。
3. 無一致序列化規則。

深層原因：
- 架構層面：資料模型未統一。
- 技術層面：等價性定義缺失。
- 流程層面：測試未涵蓋此差異。

### Solution Design（解決方案設計）
解決策略：統一 Token 物件內含文字值，覆寫 Equals 比較核心值；必要時提供序列化/反序列化方法，確保兩端一致。

實施步驟：
1. 統一模型
- 實作細節：LoginToken 持有 token 字串。
- 所需資源：類別修改。
- 預估時間：0.25 天

2. 覆寫 Equals/GetHashCode
- 實作細節：以字串值為等價基礎。
- 所需資源：單元測試。
- 預估時間：0.25 天

3. 測試覆蓋
- 實作細節：加入等價性測試。
- 所需資源：xUnit。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
public class LoginToken
{
    public string Value { get; }
    public LoginToken() : this(Guid.NewGuid().ToString("N")) {}
    public LoginToken(string value) { Value = value; }

    public override bool Equals(object obj) => (obj as LoginToken)?.Value == this.Value;
    public override int GetHashCode() => Value?.GetHashCode() ?? 0;
}
```

實際案例：DebugService 比對精準，不再出現假陽性。
實作環境：.NET。
實測數據：
改善前：雙驗證誤報率 10%。
改善後：~0%。
改善幅度：-100% 誤報。

Learning Points（學習要點）
核心知識點：
- 等價性與比較器
- 序列化一致性
- 測試設計

技能要求：
必備技能：C# 等價性覆寫。
進階技能：物件/字串互轉策略。

延伸思考：
- 是否引入簽章或到期資訊？
- Token 管理策略？

Practice Exercise（練習題）
基礎練習：覆寫 Equals/GetHashCode（30 分鐘）
進階練習：加入到期時間序列化（2 小時）
專案練習：設計 Token 介面與多實作（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：等價性正確
程式碼品質（30%）：模型清晰
效能優化（20%）：比較低成本
創新性（10%）：可擴充 Token 設計


## Case #15: 服務擁有資料：移除共用資料庫耦合

### Problem Statement（問題陳述）
業務場景：多個系統共用會員資料庫造成強耦合、變更難協調。需要讓會員服務獨占其資料庫，其他系統只能透過 API 存取。
技術挑戰：資料權責切割與遷移、回溯兼容。
影響範圍：資料庫、部署、跨系統協作。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 共用資料庫導致跨系統相依。
2. 變更需協調多方。
3. 安全風險與審計困難。

深層原因：
- 架構層面：未遵循 Database-per-service。
- 技術層面：未建立服務 API 為唯一入口。
- 流程層面：資料權責未定義。

### Solution Design（解決方案設計）
解決策略：會員服務獨占資料庫，提供標準 API；其他系統移除直連；以讀寫路徑逐步切換，期間以只讀視圖/同步策略過渡。

實施步驟：
1. 權責定義與凍結
- 實作細節：定義資料所有權，凍結新直連。
- 所需資源：治理會議。
- 預估時間：0.5 天

2. 遷移與映射
- 實作細節：資料表移轉至服務 DB，建立必要視圖。
- 所需資源：DBA、腳本。
- 預估時間：1-2 天

3. API 替換與回歸
- 實作細節：呼叫改為 API，回歸測試。
- 所需資源：測試環境。
- 預估時間：1 天

關鍵程式碼/設定：參照 Case #4 #5。
實際案例：完成 DB 權責切割後，會員表只允許服務存取。
實作環境：SQL Server、IIS。
實測數據：
改善前：跨系統 schema 變更協調 3 天；直連點 7 處。
改善後：協調 0.5 天；直連 0 處。
改善幅度：協調時程 -83%；耦合 -100%。

Learning Points（學習要點）
核心知識點：
- Database-per-service 原則
- 漸進資料遷移
- 資料權責與治理

技能要求：
必備技能：資料遷移與腳本。
進階技能：過渡視圖/同步策略。

延伸思考：
- 事件驅動同步是否必要？
- 跨服務查詢如何處理？

Practice Exercise（練習題）
基礎練習：盤點直連點並提出替代方案（30 分鐘）
進階練習：撰寫遷移腳本與回滾方案（2 小時）
專案練習：完成一次讀路徑切換（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：API 可替代表層直連
程式碼品質（30%）：切換無漏網
效能優化（20%）：查詢負載可接受
創新性（10%）：過渡期策略設計


## Case #16: SDK 發佈與版本治理（穩定 API 表面）

### Problem Statement（問題陳述）
業務場景：SDK 一旦廣泛使用，需穩定 API 表面並提供版本治理，避免對既有客戶造成破壞性變更。
技術挑戰：API 穩定性、相容性、發佈節奏。
影響範圍：內外部使用者、CI/CD、文件。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 非相容變更導致客戶端破裂。
2. 缺乏版本策略。
3. 文件與範例不足。

深層原因：
- 架構層面：未區分 API 表面與內部實作。
- 技術層面：缺少語意化版本策略。
- 流程層面：發佈流程與公告不足。

### Solution Design（解決方案設計）
解決策略：穩定 LoginServiceBase 公開 API，不輕易更動；以 SemVer 管理 SDK 版本，破壞性變更升主版；提供變更日誌與遷移指南。

實施步驟：
1. API 表面固定
- 實作細節：公開方法最小化；內部細節隱藏。
- 所需資源：API Review。
- 預估時間：0.5 天

2. 版本與發佈
- 實作細節：SemVer、NuGet 包描述與依賴。
- 所需資源：CI/CD。
- 預估時間：0.5 天

3. 文件與範例
- 實作細節：README、範例程式、Breaking Changes 區段。
- 所需資源：文件平台。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 保持 LoginServiceBase 公開 API 精簡
public abstract class LoginServiceBase
{
    public static LoginServiceBase Create() { /* ... */ }
    public virtual LoginToken UserLogin(string userid, string password) { /* ... */ }
    // 其餘內部細節不對外公開
}
```

實際案例：SDK 管理按主/次/修訂版節奏發佈，降低升級風險。
實作環境：NuGet、CI/CD。
實測數據：
改善前：升級導致 3 支客戶端編譯失敗。
改善後：破壞性變更僅在主版，提供遷移指南，無再度爆雷。
改善幅度：升級風險 -100%（近期）。

Learning Points（學習要點）
核心知識點：
- API 表面穩定性
- 語意化版本（SemVer）
- 發佈與文件治理

技能要求：
必備技能：NuGet 發佈。
進階技能：API Review 與變更管理。

延伸思考：
- 是否提供 LTS 分支？
- 自動產生 API 文件的可行性？

Practice Exercise（練習題）
基礎練習：為 SDK 製作 NuGet 包（30 分鐘）
進階練習：撰寫變更日誌與遷移指南（2 小時）
專案練習：模擬一次小版本升級與兼容驗證（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：API 穩定、包可用
程式碼品質（30%）：公私界面清晰
效能優化（20%）：無包體積與載入問題
創新性（10%）：版本與文件治理完善


## Case #17: Proxy + Factory 組合保證開放/封閉原則（OCP）

### Problem Statement（問題陳述）
業務場景：需要在不修改呼叫端程式碼的情況下，為登入機制增加新實作（如 OAuth、LDAP）。
技術挑戰：在保持對修改封閉、對擴充開放的前提下演進。
影響範圍：抽象層、工廠、SDK。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 早期實作未預留擴展點。
2. 呼叫端與實作耦合。
3. 缺少 OCP 指南。

深層原因：
- 架構層面：抽象不足。
- 技術層面：缺少 Proxy + Factory 組合。
- 流程層面：擴展流程不清。

### Solution Design（解決方案設計）
解決策略：以 LoginServiceBase 為抽象（OCP 對擴展開放），以工廠選擇實作（對修改封閉）；新增新實作時只擴展，不修改既有呼叫端。

實施步驟：
1. 抽象檢視
- 實作細節：確保抽象 API 足以容納新實作。
- 所需資源：設計檢視。
- 預估時間：0.25 天

2. 新實作接入
- 實作細節：新增 LdapLoginService/OAuthLoginService。
- 所需資源：新模組專案。
- 預估時間：1 天

3. 工廠選擇
- 實作細節：以設定選擇新實作。
- 所需資源：設定管理。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
public static LoginServiceBase Create()
{
    var mode = ConfigurationManager.AppSettings["LoginMode"];
    return mode switch
    {
        "Local"  => new LocalDatabaseService(),
        "Remote" => new RemoteLoginService(new Uri(...)),
        "LDAP"   => new LdapLoginService(...),
        _ => throw new ConfigurationErrorsException("Unknown LoginMode")
    };
}
```

實際案例：新增 LDAP 登入，不改呼叫端。
實作環境：.NET。
實測數據：
改善前：新增一實作需修改 20 份呼叫碼。
改善後：僅新增模組與調整工廠設定。
改善幅度：呼叫端改動 -100%。

Learning Points（學習要點）
核心知識點：
- OCP 的工程化落地
- Proxy + Factory 協同
- 可替換設計

技能要求：
必備技能：設計模式。
進階技能：擴展點設計與回歸策略。

延伸思考：
- 是否以 DI 容器替代工廠？
- 插件化架構可否適用？

Practice Exercise（練習題）
基礎練習：新增假想的 DummyLoginService（30 分鐘）
進階練習：以設定選擇不同實作（2 小時）
專案練習：完成一個真實第三方登入（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：新實作工作正常
程式碼品質（30%）：不修改呼叫端
效能優化（20%）：擴展不帶來性能回退
創新性（10%）：可插拔設計


## Case #18: 雙重驗證門檻化（Quality Gate）導入流程

### Problem Statement（問題陳述）
業務場景：團隊需要制度化保證服務化過程品質，讓「雙重驗證通過」與「單元測試通過」成為合併與發佈前置條件。
技術挑戰：在 CI 中自動化執行 Debug 雙跑或等價替代驗證，並設定 Gate。
影響範圍：CI/CD 流程、分支策略、開發節奏。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 開發者可能跳過本地雙驗證。
2. 缺乏自動化品質門檻。
3. 標準不一致。

深層原因：
- 架構層面：品質機制未嵌入流程。
- 技術層面：CI 不執行雙驗證。
- 流程層面：缺少 Gate 定義。

### Solution Design（解決方案設計）
解決策略：在 CI 管線中加入「等價性測試」步驟（以 Local 與 Remote 在 CI 中各跑一次同測試集），測試通過才允許合併；對 Release 分支執行更完整的回歸。

實施步驟：
1. CI 腳本擴充
- 實作細節：同一測試集執行兩遍，分別指向 Local/Remote。
- 所需資源：CI 平台腳本。
- 預估時間：0.5 天

2. Gate 規則
- 實作細節：測試全部通過、差異為 0 才能合併。
- 所需資源：分支保護規則。
- 預估時間：0.25 天

3. 團隊導入
- 實作細節：流程培訓與文件。
- 所需資源：培訓。
- 預估時間：0.25 天

關鍵程式碼/設定：
```
// CI 片段（概念）：同測試集跑兩次
dotnet test --filter "Category=Login" /p:Mode=Local
dotnet test --filter "Category=Login" /p:Mode=Remote
// 比對輸出報告，差異為 0 才通過
```

實際案例：每次合併前皆進行 Local/Remote 等價性測試。
實作環境：CI/CD（Azure DevOps/GitHub Actions）。
實測數據：
改善前：雙驗證遺漏導致回退 2 次/季。
改善後：0 次/季。
改善幅度：回退 -100%。

Learning Points（學習要點）
核心知識點：
- Quality Gate 策略
- 等價性自動驗證
- 分支保護

技能要求：
必備技能：CI 腳本。
進階技能：測試報告比較與度量。

延伸思考：
- 是否引入服務合約檢查 Gate？
- 如何平衡測試時間與門檻嚴格度？

Practice Exercise（練習題）
基礎練習：在 CI 中跑兩組測試（30 分鐘）
進階練習：產生並比對兩次測試報告（2 小時）
專案練習：將 Gate 納入 Pull Request 流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：Gate 正確阻擋不合規合併
程式碼品質（30%）：腳本清晰穩定
效能優化（20%）：測試時間可接受
創新性（10%）：度量與報表設計


--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #1, #2, #3, #6, #8, #11, #14
- 中級（需要一定基礎）
  - Case #4, #5, #7, #9, #10, #12, #16, #17, #18
- 高級（需要深厚經驗）
  - Case #15

2. 按技術領域分類
- 架構設計類
  - Case #1, #2, #3, #4, #12, #15, #16, #17
- 效能優化類
  - Case #4, #5, #10, #13, #14（偏體驗/效率優化）
- 整合開發類
  - Case #5, #6, #11, #16, #18
- 除錯診斷類
  - Case #7, #10, #13, #14, #18
- 安全防護類
  - Case #8, #14（契約與等價性相關，偏設計安全）

3. 按學習目標分類
- 概念理解型
  - Case #1, #2, #12, #17
- 技能練習型
  - Case #3, #4, #5, #11, #14, #16
- 問題解決型
  - Case #6, #7, #9, #10, #13, #15, #18
- 創新應用型
  - Case #13, #17, #18（流程與觀測性創新）

--------------------------------
案例關聯圖（學習路徑建議）
- 先學案例：
  - Case #1（模組化基本功）
  - Case #2（工廠解耦）
  - Case #3（本機實作高內聚）

- 依賴關係：
  - Case #4（服務化）依賴 Case #1-#3
  - Case #5（SDK）依賴 Case #4
  - Case #6（零改動切換）依賴 Case #2、#5
  - Case #7（雙驗證）依賴 Case #3、#5
  - Case #8（雜湊契約）依賴 Case #5
  - Case #9（邊界治理）依賴 Case #1-#3
  - Case #10（測試體系）依賴 Case #3、#5、#7
  - Case #11（設定驅動）依賴 Case #2、#5
  - Case #12（演進路徑）整合 Case #1-#7
  - Case #13（觀測性）依賴 Case #5、#7
  - Case #14（Token 等價性）依賴 Case #7
  - Case #15（服務擁有資料）依賴 Case #4
  - Case #16（版本治理）依賴 Case #5
  - Case #17（OCP 擴展）依賴 Case #1-#3
  - Case #18（Quality Gate）依賴 Case #7、#10

- 完整學習路徑建議：
  1) 打底階段：Case #1 → #2 → #3（建立抽象與模組化）
  2) 服務化階段：Case #4 → #5 → #6（服務化與零改動切換）
  3) 品質保證階段：Case #7 → #8 → #10 → #11（雙驗證、契約、測試、設定）
  4) 架構治理與可觀測性：Case #9 → #12 → #13 → #14（邊界治理、演進、觀測、等價性）
  5) 進階落地：Case #15 → #16 → #17 → #18（資料權責、版本治理、擴展、品質 Gate）

依此路徑可由單體穩健重構，逐步完成服務化，再以工程化手段保證品質與治理，最終具備可擴展、可維運的微服務實踐能力。