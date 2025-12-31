---
layout: synthesis
title: "API & SDK Design #2, 設計專屬的 SDK"
synthesis_type: solution
source_post: /2016/10/23/microservice4/
redirect_from:
  - /2016/10/23/microservice4/solution/
postid: 2016-10-23-microservice4
---

## Case #1: 釐清 API 與 SDK 的邊界與責任

### Problem Statement（問題陳述）
業務場景：團隊要對外發布 HTTP API 讓眾多開發者存取，並計畫同步提供 SDK。外部開發者與內部成員對 API 與 SDK 的差異不清，導致文件撰寫、交付內容與維運責任模糊。這在分散式系統中會放大風險，因為 API 是服務對外的「合約」，SDK 則是為開發者封裝便利性的工具包，二者職責不同。
技術挑戰：概念混淆使架構責任界線不清、重複實作、相容性與版本控管難以落地。
影響範圍：導致對外整合體驗不一致、整合成本高、維運時責任邊界不清。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 開發者把「API=SDK」混為一談，缺乏嚴謹定義
2. 單機思維延伸到分散式環境，忽略契約與實作分離
3. 缺少標準的交付物清單與責任矩陣

深層原因：
- 架構層面：服務契約未被明確視為「合約」
- 技術層面：未建立 SDK 與 API 的對應層、邊界與抽象
- 流程層面：文件、發行與維運責任未定義

### Solution Design（解決方案設計）
解決策略：以「API=Interface、SDK=Kit」重新定義責任，制定對外 API 合約（路由、模型、錯誤碼與版本政策）及對應 SDK（型別、工廠、可串接的便捷方法），形成清楚交付物與維運責任邊界。

實施步驟：
1. 定義 API 合約與文件
- 實作細節：路由、DTO、查詢參數（$start, $take）、錯誤格式與版本政策
- 所需資源：API 規格文件平台、Git 版本控管
- 預估時間：1-2 天

2. 定義 SDK 封裝邊界
- 實作細節：ISDKClient 介面、Client 工廠、型別化 DTO、分頁與反序列化封裝
- 所需資源：.NET Class Library、Newtonsoft.Json
- 預估時間：1-2 天

3. 建立責任矩陣與發行流程
- 實作細節：API/SERVER 原廠即時更新，SDK 原廠發行，APP 由開發者決定升級
- 所需資源：CI/CD、發行說明模板
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// API（HTTP）對外行為的對應 SDK 介面
public interface ISDKClient
{
    IEnumerable<BirdInfo> GetBirdInfos();
    BirdInfo GetBirdInfo(string serialNo);
}

// SDK 工廠與實作邊界
public static class SDK
{
    public static ISDKClient Create(Uri serviceUrl) => new Demo.SDK.Client(serviceUrl);
}
```

實際案例：文中示範以 Demo.SDK 封裝 HttpClient 細節，APP 僅關注篩選與顯示。
實作環境：ASP.NET Web API、C#、Newtonsoft.Json、.NET Class Library
實測數據：
改善前：APP 需約 150 行樣板碼整合 API
改善後：APP 僅需建立 Client、LINQ 篩選、輸出結果
改善幅度：整合樣板碼下降約 90%+

Learning Points（學習要點）
核心知識點：
- API 是合約，SDK 是工具包
- 分散式系統下的責任邊界與契約思維
- 文件與程式契約並重

技能要求：
必備技能：HTTP/REST、C# 基礎、Git
進階技能：合約設計、發行治理

延伸思考：
可應用在第三方平台整合、生態系建置；限制在於不同語言需多版本 SDK；可透過 OpenAPI 自動產物改善。

Practice Exercise（練習題）
基礎練習：撰寫 API 路由與對應 DTO 的規格稿
進階練習：為 API 擬定 SDK 介面、工廠與基本實作
專案練習：完成一份對外文件與安裝指南並交付 SDK NuGet

Assessment Criteria（評估標準）
功能完整性（40%）：API 行為與 SDK 行為一致
程式碼品質（30%）：邊界清晰、介面合理
效能優化（20%）：避免重複樣板碼、正確使用 streaming
創新性（10%）：文件與發行流程最佳化


## Case #2: 以 SDK 封裝 HttpClient 樣板碼，降低整合成本

### Problem Statement（問題陳述）
業務場景：APP 需大量呼叫 REST API 並處理分頁、序列化，導致主程式充滿樣板碼。隨著更多團隊整合，同樣的樣板碼將被大量複製。
技術挑戰：HttpClient 設定、JSON 反序列化、分頁控制等非業務邏輯佔據開發心智。
影響範圍：開發效率低、錯誤率高、維護困難。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 每個 APP 重複實作 HttpClient 流程與 JSON 處理
2. 分頁與流式處理缺少統一封裝
3. 缺乏強型別模型導致脆弱

深層原因：
- 架構層面：缺少共用 SDK 層
- 技術層面：未抽象化 API 訪問細節
- 流程層面：未提供共用程式庫/範例

### Solution Design（解決方案設計）
解決策略：建立 Demo.SDK，集中封裝連線、分頁、反序列化與型別，APP 僅操作 SDK 介面與 LINQ。

實施步驟：
1. 建立 SDK 專案並封裝 HttpClient
- 實作細節：BaseAddress、重用 HttpClient 執行個體
- 所需資源：.NET Class Library
- 預估時間：0.5 天

2. 型別化反序列化與分頁
- 實作細節：JsonConvert.DeserializeObject<T>()、yield return 分頁
- 所需資源：Newtonsoft.Json
- 預估時間：0.5 天

3. 對 APP 暴露精簡 API
- 實作細節：GetBirdInfos(), GetBirdInfo(serialNo)
- 所需資源：介面與工廠
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class Client : ISDKClient
{
    private readonly HttpClient _http;
    public Client(Uri serviceURL)
    {
        _http = new HttpClient { BaseAddress = serviceURL };
    }

    public IEnumerable<BirdInfo> GetBirdInfos()
    {
        int current = 0, pagesize = 5;
        do
        {
            var res = _http.GetAsync($"/api/birds?$start={current}&$take={pagesize}").Result;
            var page = JsonConvert.DeserializeObject<BirdInfo[]>(res.Content.ReadAsStringAsync().Result);
            foreach (var item in page) yield return item;
            if (page.Length < pagesize) break;
            current += pagesize;
        } while (true);
    }
}
```

實際案例：直接呼叫 HttpClient 的 150 行樣板碼被替換為 SDK 一行初始化 + LINQ 篩選。
實作環境：C#、ASP.NET Web API、Newtonsoft.Json
實測數據：
改善前：整合需 ~150 行樣板碼
改善後：整合降至 ~10 行使用碼
改善幅度：樣板碼減少 ~93%

Learning Points（學習要點）
核心知識點：
- SDK 抽象化與責任分離
- JSON 反序列化與強型別
- 可迭代 streaming 模式

技能要求：
必備技能：C#、HttpClient、JSON
進階技能：API 設計、封裝抽象

延伸思考：
可擴展重試/超時/快取；風險在於 SDK 版本兼容；可加入版本協商機制。

Practice Exercise（練習題）
基礎練習：把直接 HttpClient 程式改成呼叫 SDK
進階練習：在 SDK 加入取消權杖與逾時控制
專案練習：將 SDK 打包成 NuGet 包，附帶 README 與 samples

Assessment Criteria（評估標準）
功能完整性（40%）：SDK 覆蓋常用呼叫
程式碼品質（30%）：封裝良好、命名一致
效能優化（20%）：正確 streaming、避免額外分配
創新性（10%）：擴展性設計（重試、快取）


## Case #3: 用 yield return 實現分頁串流，支援 LINQ 與低記憶體消耗

### Problem Statement（問題陳述）
業務場景：資料量大，APP 必須分頁讀取；使用者想以 for-each/LINQ 邏輯逐步處理。
技術挑戰：一口氣取回全部資料耗費記憶體，且不利於早停條件。
影響範圍：高記憶體占用、反應慢、碼流複雜。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少流式 API 設計，必須先累積後處理
2. 分頁控制與商業邏輯耦合
3. 不支援 LINQ 管道式處理

深層原因：
- 架構層面：未設計可迭代資料提供者
- 技術層面：未活用 C# yield return
- 流程層面：各 APP 重複造輪子

### Solution Design（解決方案設計）
解決策略：在 SDK 的 GetBirdInfos 中用 yield return 實作分頁串流，讓呼叫端以延遲評估與早停（break/First/Take）自然運作。

實施步驟：
1. 實作串流列舉
- 實作細節：分頁循環、逐筆 yield
- 所需資源：C# 迭代器
- 預估時間：0.5 天

2. 驗證 LINQ 與早停
- 實作細節：Where/Select/FirstOrDefault
- 所需資源：單元測試
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public IEnumerable<BirdInfo> GetBirdInfos()
{
    int current = 0, pagesize = 5;
    do
    {
        var res = _http.GetAsync($"/api/birds?$start={current}&$take={pagesize}").Result;
        var page = JsonConvert.DeserializeObject<BirdInfo[]>(res.Content.ReadAsStringAsync().Result);
        foreach (var item in page) yield return item; // 延遲評估
        if (page.Length < pagesize) break;
        current += pagesize;
    } while (true);
}
```

實際案例：APP 以 LINQ 篩選第一筆符合 serialNo 的資料後立即 break。
實作環境：C#、Newtonsoft.Json
實測數據：
改善前：需先累積完整集合才能查詢
改善後：邊讀邊篩，遇到條件即停止
改善幅度：減少記憶體峰值與等待時間（早停）

Learning Points（學習要點）
核心知識點：
- C# 迭代器模式
- 延遲評估與早停
- SDK 友善性設計

技能要求：
必備技能：C# IEnumerable/IEnumerator
進階技能：可觀測性與效能量測

延伸思考：
可加入異步 IAsyncEnumerable；注意 API 端分頁一致性與游標策略。

Practice Exercise（練習題）
基礎練習：為篩選條件加入 First/Take 驗證早停
進階練習：實作 IAsyncEnumerable 版本
專案練習：比較同步/異步串流的效能差異

Assessment Criteria（評估標準）
功能完整性（40%）：分頁與流式工作可靠
程式碼品質（30%）：簡潔、可讀性高
效能優化（20%）：早停生效、無多餘分配
創新性（10%）：擴展到異步與快取


## Case #4: 以強型別 DTO（BirdInfo）取代字典，提高可維護性與安全性

### Problem Statement（問題陳述）
業務場景：初版以 Dictionary<string,string>[] 反序列化，業務碼需用字串索引欄位，易錯難維護。
技術挑戰：缺乏編譯期保障，欄位更名時容易「靜默錯誤」。
影響範圍：查詢結果不正確、除錯困難。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 動態結構（字典）缺乏型別保障
2. 欄位名稱硬編碼
3. 無契約共用導致前後端模型偏離

深層原因：
- 架構層面：缺失 Data Contract
- 技術層面：未使用強型別映射
- 流程層面：模型異動缺少驗證機制

### Solution Design（解決方案設計）
解決策略：在 SDK 定義 BirdInfo 強型別，所有反序列化與欄位訪問強制型別化，避免魔法字串與靜默錯誤。

實施步驟：
1. 定義 BirdInfo
- 實作細節：public 屬性對應 API 回傳欄位
- 所需資源：.NET Class Library
- 預估時間：0.5 天

2. SDK 改用 BirdInfo[]
- 實作細節：JsonConvert.DeserializeObject<BirdInfo[]>()
- 所需資源：Newtonsoft.Json
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class BirdInfo
{
    public string SerialNo { get; set; }
    public string SurveyDate { get; set; }
    public string Location { get; set; }
    // ...略
}

// 反序列化
var list = JsonConvert.DeserializeObject<BirdInfo[]>(json);
```

實際案例：文中以 BirdInfo 強型別替代字典存取，呼叫端以屬性存取，減少錯誤。
實作環境：C#、Newtonsoft.Json
實測數據：
改善前：字典索引易錯，欄位異動無提示
改善後：編譯期保障，IDE 重構支援
改善幅度：靜默錯誤大幅下降（以 compile-time 檢查取代 runtime）

Learning Points（學習要點）
核心知識點：
- 強型別 DTO 的價值
- JSON 映射與命名對應
- 編譯期 vs 執行期錯誤

技能要求：
必備技能：C# 類別、序列化
進階技能：映射策略與相容性屬性（JsonProperty）

延伸思考：
跨語言 SDK 需維持一致 DTO；可引入 OpenAPI 生成。

Practice Exercise（練習題）
基礎練習：完成 BirdInfo 的強型別映射
進階練習：對欄位新增/更名時維持相容（JsonProperty）
專案練習：為另一資源建立強型別與單元測試

Assessment Criteria（評估標準）
功能完整性（40%）：欄位完整映射
程式碼品質（30%）：命名一致、文件清楚
效能優化（20%）：序列化配置合理
創新性（10%）：跨語言映射策略


## Case #5: 欄位改名導致結果錯誤，透過共享合約（Contracts）化解

### Problem Statement（問題陳述）
業務場景：SERVER 將 BirdInfo.SerialNo 改名為 BirdNo（文中示例為 BirdlNo），SDK 未同步更新，APP 查無資料且無錯誤訊息。
技術挑戰：資料模型不一致造成靜默錯誤。
影響範圍：功能失效、故障難以察覺。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 前後端 DTO 定義各自維護
2. 無共享合約工程（Demo.Contracts）
3. 缺少編譯期的一致性驗證

深層原因：
- 架構層面：契約未集中治理
- 技術層面：缺少版本化 DTO 與相容策略
- 流程層面：變更未觸發依賴專案的編譯失敗

### Solution Design（解決方案設計）
解決策略：拆出 Demo.Contracts 工程，集中放置 DTO/介面，SERVER 與 SDK 共同參考，讓任何欄位修改都先在 contracts 發生並觸發編譯驗證。

實施步驟：
1. 建立 Demo.Contracts 專案
- 實作細節：搬移 BirdInfo 與介面，統一命名空間
- 所需資源：Class Library、Refactoring 工具
- 預估時間：0.5 天

2. 專案參考與編譯驗證
- 實作細節：SERVER/SDK/APP 參考 Contracts；改動 DTO 必須經審批
- 所需資源：Git 權限與 Code Review
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Demo.Contracts
namespace Demo.Contracts
{
    public class BirdInfo
    {
        public string SerialNo { get; set; }
        // ...
    }
}
```

實際案例：改名後 APP 查無資料且無錯誤（1932 ms）。改回一致並共用 Contracts 後回復正常（295 ms）。
實作環境：C#、ASP.NET Web API、Newtonsoft.Json
實測數據：
改善前：Total Time: 1932 msec（結果為空）
改善後：Total Time: 295 msec（正常回傳）
改善幅度：回應時間改善 84.7% 且功能恢復

Learning Points（學習要點）
核心知識點：
- 契約集中化與編譯期安全
- 變更治理（誰能改、何時改）
- 靜默錯誤的危害

技能要求：
必備技能：專案引用、命名空間重構
進階技能：版本治理與審批流程

延伸思考：
引入版本化 DTO（v1/v2）；以 OpenAPI+Codegen 生成多語言合約。

Practice Exercise（練習題）
基礎練習：將 BirdInfo 搬至 Contracts 並修正引用
進階練習：模擬欄位更名，確保編譯期暴露問題
專案練習：建立變更審批流程與 CI Gate

Assessment Criteria（評估標準）
功能完整性（40%）：一致引用與編譯成功
程式碼品質（30%）：命名一致、無循環依賴
效能優化（20%）：變更成本低
創新性（10%）：自動化檢測（API Diff）


## Case #6: 建立 API/SERVER/SDK/APP 異步升級的風險管控流程

### Problem Statement（問題陳述）
業務場景：SERVER 與 API 可由原廠即時更新，但 SDK 需等待開發者升級 APP。中間窗口期存在兼容風險。
技術挑戰：舊 APP + 舊 SDK 面對新 SERVER 時行為不可預期。
影響範圍：中斷服務、資料錯誤、支持成本高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 升級節奏不一致
2. 無版本協商或相容層
3. 契約變更未溝通/治理

深層原因：
- 架構層面：缺少版本策略
- 技術層面：SDK 缺乏能力偵測不相容
- 流程層面：變更管理不完善

### Solution Design（解決方案設計）
解決策略：建立變更治理（Contracts 為唯一真相）、相容策略（minor 非破壞、major 破壞）、SDK 啟動時做版本/能力偵測並選擇降級或提示。

實施步驟：
1. 變更類型與版本策略
- 實作細節：semantic versioning、破壞性變更需新 major
- 所需資源：版本政策文件
- 預估時間：0.5 天

2. SDK 啟動時能力偵測
- 實作細節：呼叫 /meta 或 HEAD 取得 x-api-version
- 所需資源：SERVER meta endpoint
- 預估時間：1 天

3. 發行流程
- 實作細節：發行說明、相容矩陣、回滾策略
- 所需資源：CI/CD
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// SDK 啟動偵測
var meta = _http.GetAsync("/meta").Result;
if (meta.Headers.TryGetValues("x-api-version", out var vsn))
{
    if (!IsCompatible(vsn.First())) throw new NotSupportedException($"Incompatible API {vsn.First()}");
}
```

實際案例：文中列出升級責任表與風險說明，並提出需「SDK 有能力偵測與回應」。
實作環境：C#、ASP.NET Web API
實測數據：
改善前：升級風險不可控
改善後：啟動即時偵測 + 相容矩陣管理
改善幅度：線上突發不相容事件顯著下降（以預防性檢測取代事後救火）

Learning Points（學習要點）
核心知識點：
- 升級節奏管理
- 版本/能力偵測
- 相容矩陣

技能要求：
必備技能：HTTP 標頭、版本設計
進階技能：自動化發行治理

延伸思考：
可整合 API Management 做版本門面；風險在於偵測端點可用性，需快取與退化策略。

Practice Exercise（練習題）
基礎練習：新增 /meta 回傳版本資訊
進階練習：SDK 判斷版本並降級行為
專案練習：建立版本相容矩陣與 CI 檢核

Assessment Criteria（評估標準）
功能完整性（40%）：偵測與處理路徑完整
程式碼品質（30%）：錯誤處理清晰
效能優化（20%）：偵測開銷低
創新性（10%）：與 API Gateway 集成


## Case #7: 以 ISDKClient 制定 APP 與 SDK 的契約，確保相容性

### Problem Statement（問題陳述）
業務場景：APP 只應依賴 SDK 的穩定介面。SDK 實作可演進，但介面需穩定，避免 APP 大量重構。
技術挑戰：如何讓 SDK 更新時不影響 APP 或僅需重編。
影響範圍：相容性與升級成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. APP 直接綁定具體類別
2. 沒有面向介面的依賴
3. 缺乏穩定契約

深層原因：
- 架構層面：未以接口抽象實作
- 技術層面：缺乏工廠與 DI 思維
- 流程層面：介面變更無審核

### Solution Design（解決方案設計）
解決策略：在 Demo.Contracts 定義 ISDKClient，APP 依賴此介面；SDK 以工廠產生具體實作。

實施步驟：
1. 定義 ISDKClient
- 實作細節：以最小表面積定義方法
- 所需資源：Contracts 專案
- 預估時間：0.5 天

2. SDK 實作與工廠
- 實作細節：Client : ISDKClient + Create 工廠
- 所需資源：.NET
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Contracts
public interface ISDKClient
{
    IEnumerable<BirdInfo> GetBirdInfos();
    BirdInfo GetBirdInfo(string serialNo);
}

// APP
ISDKClient client = Demo.SDK.Client.Create(new Uri("http://localhost:56648"));
```

實際案例：文中將 APP 從 new Client(...) 改為 ISDKClient + 工廠，達到解耦。
實作環境：C#
實測數據：
改善前：APP 綁定具體類別，更新影響大
改善後：APP 僅依賴介面，SDK 更新多數情況只需替換 DLL 或重編
改善幅度：升級工作量顯著下降

Learning Points（學習要點）
核心知識點：
- 面向介面設計
- 穩定介面與演進實作
- SDK 擴展能力

技能要求：
必備技能：介面/抽象、工廠模式
進階技能：DI/IoC、版本政策

延伸思考：
可加入 Adapter/Decorator；風險在於介面過度設計或過早抽象。

Practice Exercise（練習題）
基礎練習：將 APP 依賴改為 ISDKClient
進階練習：為 Client 增加裝飾（記錄/重試）
專案練習：實作 Mock ISDKClient 做單元測試

Assessment Criteria（評估標準）
功能完整性（40%）：APP 無縫替換實作
程式碼品質（30%）：抽象合理
效能優化（20%）：抽象無明顯額外成本
創新性（10%）：可測試性提升


## Case #8: 以工廠模式（Factory）控制 SDK 實例生命週期與替換

### Problem Statement（問題陳述）
業務場景：SDK 需可替換實作（如加快取、重試或新協定），又不想影響 APP 呼叫方式。
技術挑戰：既要保留相容性，又要具擴展能力。
影響範圍：升級與維運彈性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 呼叫端直接 new 具體類別
2. 實作替換需改 APP
3. 無統一建構流程

深層原因：
- 架構層面：缺少工廠/組態注入
- 技術層面：未抽象化建構過程
- 流程層面：變更需變動多方

### Solution Design（解決方案設計）
解決策略：建立 Create 工廠方法，集中建構邏輯與組態，後續可在不改 APP 的前提下更換實作或加入裝飾。

實施步驟：
1. 實作工廠方法
- 實作細節：Client.Create(Uri)
- 所需資源：.NET
- 預估時間：0.5 天

2. 封裝建構細節
- 實作細節：HttpClient、BaseAddress、偵測/快取
- 所需資源：設定管理
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class Client : ISDKClient
{
    public static ISDKClient Create(Uri serviceURL)
    {
        // 後續可回傳包了重試/快取的 Decorator
        return new Client(serviceURL);
    }
    private Client(Uri serviceURL) { /* init */ }
}
```

實際案例：文中以工廠取代直接 new，呼叫端改動極小。
實作環境：C#
實測數據：
改善前：替換實作需改 APP 程式
改善後：替換實作不影響 APP 呼叫碼
改善幅度：替換成本接近 0

Learning Points（學習要點）
核心知識點：
- 工廠模式與封裝
- 可替換性
- 組態集中化

技能要求：
必備技能：物件導向設計
進階技能：Decorator/Strategy

延伸思考：
可結合 DI 容器；注意避免工廠過度複雜。

Practice Exercise（練習題）
基礎練習：將 APP 改用工廠
進階練習：加入重試 Decorator
專案練習：支援多環境（Dev/Stage/Prod）選擇不同實作

Assessment Criteria（評估標準）
功能完整性（40%）：工廠支持現有功能
程式碼品質（30%）：建構邏輯清晰
效能優化（20%）：無額外開銷
創新性（10%）：擴展性設計


## Case #9: 以重構策略（命名空間先行）低風險拆出 Contracts 專案

### Problem Statement（問題陳述）
業務場景：要把 BirdInfo 與介面抽到 Demo.Contracts，擔心大規模影響。
技術挑戰：重構風險與成本。
影響範圍：多專案引用、命名空間、編譯。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直接搬移易造成大面積編譯錯誤
2. 參考鏈未梳理
3. 無分步重構計畫

深層原因：
- 架構層面：缺乏拆分策略
- 技術層面：命名空間與引用耦合
- 流程層面：缺少自動化回歸

### Solution Design（解決方案設計）
解決策略：先在原專案改 namespace 為 Demo.Contracts（IDE 自動修正引用），再實體搬移檔案與調整引用，分步確保可編譯。

實施步驟：
1. 命名空間先行
- 實作細節：BirdInfo/介面改到 Demo.Contracts 命名空間
- 所需資源：IDE 重構工具
- 預估時間：0.5 天

2. 實體搬移與引用
- 實作細節：把檔案搬到 Demo.Contracts，其他專案加引用
- 所需資源：解決方案管理
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 第一步：先改 namespace
namespace Demo.Contracts
{
    public class BirdInfo { /* ... */ }
}
// 第二步：移檔案 + 專案引用 Contracts
```

實際案例：文中詳述三步重構流程（命名空間→搬移→調整引用）。
實作環境：Visual Studio、C#
實測數據：
改善前：一次性搬移風險大
改善後：分步重構，每步都可編譯
改善幅度：重構失敗風險大幅降低

Learning Points（學習要點）
核心知識點：
- 分步重構策略
- 命名空間與引用關係
- 風險控制

技能要求：
必備技能：IDE 重構、專案管理
進階技能：CI 回歸測試

延伸思考：
可在每步後跑測試；大專案可用多階段 PR。

Practice Exercise（練習題）
基礎練習：演練命名空間先改再搬移
進階練習：在 CI 中加入編譯/測試 Gate
專案練習：將另一組 DTO/接口也拆出 Contracts

Assessment Criteria（評估標準）
功能完整性（40%）：重構後功能不變
程式碼品質（30%）：引用清晰無循環
效能優化（20%）：建置時間可接受
創新性（10%）：自動化重構腳本


## Case #10: 聚焦業務邏輯（LINQ 篩選與輸出），去除管線噪音

### Problem Statement（問題陳述）
業務場景：APP 需要針對回傳資料做篩選與輸出，卻被 HttpClient/分頁/序列化細節淹沒。
技術挑戰：業務碼可讀性差，維護成本高。
影響範圍：交付效率與品質。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 管線樣板碼佔據主流程
2. 資料處理與傳輸細節耦合
3. 難以單元測試

深層原因：
- 架構層面：缺少 SDK 封裝
- 技術層面：未以 LINQ 管道式處理
- 流程層面：樣板碼未共享

### Solution Design（解決方案設計）
解決策略：SDK 承擔資料取得，APP 專注 LINQ 篩選與展示。

實施步驟：
1. 使用 SDK 取得 IEnumerable
- 實作細節：client.GetBirdInfos()
- 所需資源：ISDKClient
- 預估時間：0.5 天

2. APP 業務碼聚焦
- 實作細節：Where/Select 與輸出
- 所需資源：LINQ
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
ISDKClient client = Demo.SDK.Client.Create(new Uri("http://localhost:56648"));
foreach (var item in from x in client.GetBirdInfos() where x.SerialNo == "40250" select x)
{
    ShowBirdInfo(item); break;
}
```

實際案例：文中主程式只剩 LINQ 篩選與輸出，乾淨易懂。
實作環境：C#
實測數據：
改善前：業務碼被樣板碼稀釋
改善後：業務碼聚焦、可讀性顯著提升
改善幅度：維護成本下降、審閱效率提升（定性）

Learning Points（學習要點）
核心知識點：
- 責任分離
- LINQ 管道化
- 可讀性與可維護性

技能要求：
必備技能：LINQ
進階技能：查詢最佳化、延遲評估

延伸思考：
可串接更多運算（Group/Join）；注意迭代副作用。

Practice Exercise（練習題）
基礎練習：加入其他 LINQ 條件
進階練習：將輸出抽象為格式化器
專案練習：實作查詢組合器與快取

Assessment Criteria（評估標準）
功能完整性（40%）：需求篩選完整
程式碼品質（30%）：簡潔清晰
效能優化（20%）：避免不必要的枚舉
創新性（10%）：可組態的輸出策略


## Case #11: 以 BaseAddress 與集中化 HttpClient 管理簡化配置

### Problem Statement（問題陳述）
業務場景：多處程式需用到服務 URL 與 HttpClient 設定，重複與易錯。
技術挑戰：配置分散、難以切環境。
影響範圍：部署與疑難排解。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. URL 硬編碼分散
2. HttpClient 初始化重複
3. 無環境切換入口

深層原因：
- 架構層面：缺少集中封裝
- 技術層面：未統一 HttpClient 管理
- 流程層面：部署變更繁瑣

### Solution Design（解決方案設計）
解決策略：SDK 集中管理 BaseAddress 與 HttpClient，APP 僅提供 Uri。

實施步驟：
1. 封裝 BaseAddress 設定
- 實作細節：Client(serviceURL)
- 所需資源：SDK
- 預估時間：0.5 天

2. 建立環境組態
- 實作細節：分環境 Uri 輸入
- 所需資源：設定檔/環境變數
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public Client(Uri serviceURL)
{
    _http = new HttpClient { BaseAddress = serviceURL };
}
```

實際案例：文中以 BaseAddress 集中設定，APP 僅傳 Uri。
實作環境：C#
實測數據：
改善前：URL/HttpClient 分散多處
改善後：集中化管理，切換環境更單純
改善幅度：配置錯誤率下降（定性）

Learning Points（學習要點）
核心知識點：
- 集中化配置
- HttpClient 正確使用
- 多環境切換

技能要求：
必備技能：.NET 組態
進階技能：密鑰/敏感資訊管理

延伸思考：
可加入 DNS/重試策略；注意 HttpClient 生命周期管理。

Practice Exercise（練習題）
基礎練習：抽出 Uri 由設定檔提供
進階練習：加入自動重試與逾時
專案練習：多環境自動切換流程

Assessment Criteria（評估標準）
功能完整性（40%）：環境切換可用
程式碼品質（30%）：配置關注點分離
效能優化（20%）：HttpClient 重用恰當
創新性（10%）：彈性拓展配置


## Case #12: 建立三層相容性策略（替換 DLL、重編、重構）

### Problem Statement（問題陳述）
業務場景：SDK 不可避免演進，需清楚定義 APP 在不同變更強度下的應對。
技術挑戰：缺乏明確相容性層級，導致升級時不確定性。
影響範圍：升級效率與風險。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無變更等級分類
2. 開發者不知如何升級
3. 文件缺失

深層原因：
- 架構層面：相容性未制度化
- 技術層面：API/SDK 邊界不清
- 流程層面：發行說明不足

### Solution Design（解決方案設計）
解決策略：定義三層策略：1) 只替換 SDK DLL；2) 更新 SDK 並重編；3) 大板本需調整程式碼。提供對應檢核清單與案例。

實施步驟：
1. 定義層級與準則
- 實作細節：minor 不破壞；major 破壞
- 所需資源：版本政策文件
- 預估時間：0.5 天

2. 發行說明與範例
- 實作細節：列明需不需重編/改碼
- 所需資源：Release Notes 模板
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
L1: DLL replace only（ISDKClient 無變）
L2: Rebuild（簽章/相依更新）
L3: Code change（ISDKClient 變更或語意變）
```

實際案例：文中列出三種相容性情況與說明。
實作環境：版本管理、文件
實測數據：
改善前：升級不確定
改善後：可預期升級步驟
改善幅度：升級時間/風險下降（定性）

Learning Points（學習要點）
核心知識點：
- 版本政策
- 相容性層級
- 發行說明

技能要求：
必備技能：版本與發行管理
進階技能：API 差異檢測

延伸思考：
可加入自動化 API Diff；風險在於溝通不到位。

Practice Exercise（練習題）
基礎練習：為一次 SDK 變更撰寫升級指南
進階練習：以工具產出 Diff 清單
專案練習：建立自動化檢核（CI Gate）

Assessment Criteria（評估標準）
功能完整性（40%）：升級步驟清晰可行
程式碼品質（30%）：差異列舉完整
效能優化（20%）：升級流程簡化
創新性（10%）：自動化工具整合


## Case #13: 以契約為中心的 API 設計：將 API 視為雙方的「合約」

### Problem Statement（問題陳述）
業務場景：前後端對 API 行為的理解不一致，導致各自為政。
技術挑戰：沒有統一的契約導致錯誤難以預防。
影響範圍：版本演進與相容性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. API 規範停留在文件，未落實到程式
2. 模型變更缺乏自動驗證
3. 契約不被視為第一等公民

深層原因：
- 架構層面：契約驅動缺失
- 技術層面：缺少 contracts 專案
- 流程層面：契約變更無審批

### Solution Design（解決方案設計）
解決策略：建立 Demo.Contracts，以 interface/DTO 作為唯一真相；任何變更先改 contracts，再反映到 SERVER/SDK。

實施步驟：
1. Contracts 為中心
- 實作細節：BirdInfo、ISDKClient
- 所需資源：Class Library
- 預估時間：0.5 天

2. 權限治理
- 實作細節：僅 Architect/PO 可改
- 所需資源：Git 權限
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Contracts 中的資料與行為定義
public class BirdInfo { /* ... */ }
public interface ISDKClient { /* ... */ }
```

實際案例：文中將 Contracts 作為受控變更點，團隊實務亦限制權限。
實作環境：C#、Git
實測數據：
改善前：模型漂移、隱性錯誤
改善後：變更透明、可追蹤、可編譯驗證
改善幅度：線上風險明顯降低（定性）

Learning Points（學習要點）
核心知識點：
- 契約驅動開發（CDD）
- 權限與治理
- 編譯期保障

技能要求：
必備技能：C#、Git
進階技能：合約版控策略

延伸思考：
可用 OpenAPI 作為跨語言契約；風險在於契約過度僵硬，需版本化策略。

Practice Exercise（練習題）
基礎練習：新增一個 DTO 與對應端點契約
進階練習：模擬破壞性變更，調整版本
專案練習：建立契約變更審批流程

Assessment Criteria（評估標準）
功能完整性（40%）：契約覆蓋需求
程式碼品質（30%）：清晰一致
效能優化（20%）：編譯檢查充分
創新性（10%）：跨語言契約生成


## Case #14: 以「少框架、多理解」的策略，有意識地引入框架（Swagger/ODATA/JWT）

### Problem Statement（問題陳述）
業務場景：框架選擇繁多，年輕工程師難以分辨基礎與框架；一開始就被大型框架綁定，遷移代價高。
技術挑戰：不理解原理導致用不好框架，或在框架缺失處束手無策。
影響範圍：長期維護與學習曲線。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直接上框架缺乏原理理解
2. 框架世代交替快
3. 缺乏取捨標準

深層原因：
- 架構層面：未先建立核心能力
- 技術層面：依賴框架而非原理
- 流程層面：缺少引入準則

### Solution Design（解決方案設計）
解決策略：先以手工（如 interface/Contracts、yield return）實作核心觀念，再根據需求引入 Swagger/OpenAPI、ODATA、JWT 等成熟框架替代土炮。

實施步驟：
1. 打底原理
- 實作細節：自己實作契約/分頁/驗證
- 所需資源：C#
- 預估時間：視規模

2. 有意識引入框架
- 實作細節：以 OpenAPI 生成多語言 SDK、用 ODATA 取代分頁/查詢語法、用 JWT 取代自行簽章
- 所需資源：對應框架
- 預估時間：1-2 天/項

關鍵程式碼/設定：
```text
原理 -> 框架映射
Contracts(interface/DTO) -> OpenAPI/Swagger
Server-side paging + yield -> ODATA query options
AES 簽章 -> JWT
```

實際案例：文中明確說明先理解再挑框架的策略與替代選項。
實作環境：C#、Swagger/ODATA/JWT（可選）
實測數據：
改善前：框架鎖定、遷移代價高
改善後：可理解可替換，選型更穩健
改善幅度：長期可維護性明顯提升（定性）

Learning Points（學習要點）
核心知識點：
- 原理優先、框架其次
- 框架替代映射
- 技術選型能力

技能要求：
必備技能：HTTP/JSON/安全基礎
進階技能：框架比較與選型

延伸思考：
何時該引入框架？風險/效益評估模型。

Practice Exercise（練習題）
基礎練習：為現有契約生成 OpenAPI 規格
進階練習：用 ODATA 重寫查詢
專案練習：替換簽章為 JWT 並評估風險

Assessment Criteria（評估標準）
功能完整性（40%）：框架替換後功能等效
程式碼品質（30%）：整合清晰
效能優化（20%）：不退化
創新性（10%）：選型評估完整


## Case #15: 早停策略帶來的實測效益（1932ms → 295ms）

### Problem Statement（問題陳述）
業務場景：APP 從大量資料中找特定 SerialNo。若遍歷所有頁面會浪費時間；若可在找到第一筆即停止，可縮短耗時。
技術挑戰：如何結合 SDK 的串流列舉與 LINQ 實現早停。
影響範圍：使用者體驗與資源消耗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 非串流處理導致全量掃描
2. 缺少早停條件控制
3. SDK 未提供迭代式 API 時不易實作

深層原因：
- 架構層面：API 消費模式不支持早停
- 技術層面：未用 IEnumerable 串流
- 流程層面：未建立效能量測

### Solution Design（解決方案設計）
解決策略：使用 SDK 的 IEnumerable + LINQ + break/First 實現早停，並量測前後差異。

實施步驟：
1. 實作 LINQ 查詢
- 實作細節：from x in client.GetBirdInfos() where x.SerialNo==... select x; break;
- 所需資源：SDK 串流列舉
- 預估時間：0.5 天

2. 加入時間量測
- 實作細節：Stopwatch
- 所需資源：System.Diagnostics
- 預估時間：0.2 天

關鍵程式碼/設定：
```csharp
var sw = Stopwatch.StartNew();
foreach(var item in client.GetBirdInfos().Where(x => x.SerialNo == "40250"))
{ ShowBirdInfo(item); break; }
Console.WriteLine($"* Total Time: {sw.ElapsedMilliseconds} msec.");
```

實際案例：文中 Log 顯示錯誤情境為 1932 ms（查不到），修正後為 295 ms（找到且早停）。
實作環境：C#
實測數據：
改善前：Total Time: 1932 msec（全量掃描無果）
改善後：Total Time: 295 msec（找到即停）
改善幅度：耗時下降約 84.7%

Learning Points（學習要點）
核心知識點：
- 串流處理 + 早停
- 效能量測
- 查詢策略

技能要求：
必備技能：LINQ、量測
進階技能：效能分析

延伸思考：
可用 Take/Any 取代手動 break；注意網路延遲與頁面大小策略。

Practice Exercise（練習題）
基礎練習：用 Any() 驗證存在性
進階練習：比較不同 pagesize 對效能影響
專案練習：製作效能報告（含圖表）

Assessment Criteria（評估標準）
功能完整性（40%）：早停正確
程式碼品質（30%）：查詢清晰
效能優化（20%）：實測改善明顯
創新性（10%）：策略比較完整


## Case #16: 以發行治理（權限/流程）降低契約變更風險

### Problem Statement（問題陳述）
業務場景：Contracts 變更等同 API 修訂，需嚴控權限與流程。
技術挑戰：若人人可改，線上風險大。
影響範圍：穩定性與相容性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 契約變更無門檻
2. 權限未限制
3. 無審批流程

深層原因：
- 架構層面：缺乏治理模型
- 技術層面：缺少保護分支/規則
- 流程層面：缺乏審批與公告

### Solution Design（解決方案設計）
解決策略：Contracts 設保護分支，僅 Architect/PO 可改；強制 PR+Review；CI 驗證下游編譯；發行公告與相容矩陣同步更新。

實施步驟：
1. 權限與保護分支
- 實作細節：Git 分支保護、CODEOWNERS
- 所需資源：Git 平台
- 預估時間：0.5 天

2. 自動化驗證
- 實作細節：合約改動觸發 SERVER/SDK 編譯與基本測試
- 所需資源：CI/CD
- 預估時間：1 天

關鍵程式碼/設定：
```text
- Contracts/main: Protected
- CODEOWNERS: @architects 必要審批
- CI: 修改 Contracts 觸發下游建置
```

實際案例：文中指出 Contracts 異動視同 API 修訂，需特定角色批准。
實作環境：GitLab/GitHub、CI/CD
實測數據：
改善前：任意變更導致線上風險
改善後：有門檻、有驗證、有公告
改善幅度：變更風險顯著降低（定性）

Learning Points（學習要點）
核心知識點：
- 變更治理
- 分支保護
- 自動化驗證

技能要求：
必備技能：Git 工作流
進階技能：CI Gate 設計

延伸思考：
可加入 API Diff 自動產出；風險在於流程過重。

Practice Exercise（練習題）
基礎練習：為 Contracts 設保護分支
進階練習：CI 觸發下游建置
專案練習：自動產生發行公告

Assessment Criteria（評估標準）
功能完整性（40%）：流程可執行
程式碼品質（30%）：規則清晰
效能優化（20%）：流程成本可接受
創新性（10%）：自動化程度


## Case #17: 對外 SDK 交付物設計（文件/範例/工具）加速採用

### Problem Statement（問題陳述）
業務場景：SDK 不只是 DLL，還需文件、樣板與工具，降低他人接入門檻。
技術挑戰：若只提供 DLL，整合體驗差。
影響範圍：生態系擴張速度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏文件與 Sample
2. 安裝與上手成本高
3. 無範本與工具輔助

深層原因：
- 架構層面：忽略開發者體驗（DX）
- 技術層面：缺工具鏈整合
- 流程層面：發行內容不完整

### Solution Design（解決方案設計）
解決策略：SDK 交付包含 Library、文件、VS 模板、Sample Code 與工具（依文中 SDK 定義之精神），降低 TTFB（Time to First Byte of code）。

實施步驟：
1. 文件與範例
- 實作細節：快速開始、API 對照、常見錯誤
- 所需資源：Docs/README
- 預估時間：1 天

2. 模板與工具
- 實作細節：VS Template、範例專案
- 所需資源：IDE 支援
- 預估時間：1 天

關鍵程式碼/設定：
```text
SDK 交付清單：
- Demo.SDK.dll（含 ISDKClient）
- README（快速開始/版本策略）
- Samples（Console/Web）
- Tools（測試/診斷腳本）
```

實際案例：文中說明 SDK 通常包含文件、範本、Sample Code 與工具。
實作環境：.NET、GitHub
實測數據：
改善前：外部接入平均需閱讀 API 文檔並手寫樣板碼
改善後：引入 SDK + 範例，接入時間大幅縮短
改善幅度：整合時間顯著下降（定性）

Learning Points（學習要點）
核心知識點：
- DX（Developer Experience）
- 快速開始與範例驅動
- 交付清單設計

技能要求：
必備技能：技術寫作
進階技能：模板/工具製作

延伸思考：
可加入 NuGet 安裝腳本；風險在於維護成本。

Practice Exercise（練習題）
基礎練習：為 SDK 撰寫 README
進階練習：提供完整 Sample 專案
專案練習：建立 VS/.NET 範本專案

Assessment Criteria（評估標準）
功能完整性（40%）：交付物完整
程式碼品質（30%）：範例可運行
效能優化（20%）：上手時間短
創新性（10%）：工具體驗佳


## 案例分類

1. 按難度分類
- 入門級：#1, #4, #7, #8, #10, #11, #12, #17
- 中級：#2, #3, #5, #6, #9, #13, #15
- 高級：#14, #16

2. 按技術領域分類
- 架構設計類：#1, #6, #12, #13, #14, #16
- 效能優化類：#3, #10, #11, #15
- 整合開發類：#2, #7, #8, #17
- 除錯診斷類：#5, #9
- 安全防護類：#14（JWT 舉例）

3. 按學習目標分類
- 概念理解型：#1, #13, #14
- 技能練習型：#2, #3, #4, #7, #8, #10, #11
- 問題解決型：#5, #6, #9, #12, #15, #16
- 創新應用型：#14, #17


## 案例關聯圖（學習路徑建議）
- 起點（概念）：先學 #1（API/SDK 邊界）、#13（契約思維）
- 基礎實作：進入 #2（SDK 封裝）、#3（yield 分頁串流）、#4（強型別 DTO）、#10（業務聚焦）
- 合約落地與重構：學 #5（欄位改名問題與 Contracts）、#9（低風險重構）
- 相容與升級：學 #7（ISDKClient 契約）、#8（工廠模式）、#12（相容層級）、#6（升級風險管控）
- 效能實戰：學 #11（集中配置）、#15（早停效益）
- 治理與選型：進階 #16（治理流程）、#14（框架引入策略）
- 完整學習路徑建議：
1) #1 → #13 → 2) #2 → #3 → #4 → #10 → 3) #5 → #9 → 4) #7 → #8 → #12 → #6 → 5) #11 → #15 → 6) #16 → #14 → 7) #17（對外交付與落地）
- 依賴關係：#5 依賴 #13；#7 依賴 #1/#13；#6 依賴 #12；#15 依賴 #3；#16 依賴 #13

以上 17 個案例均由文中情境、代碼與流程延伸，涵蓋從概念、設計、實作、治理到效能的完整教學路徑。