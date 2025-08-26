以下內容基於文章「容器化的微服務開發 #2, IIS or Self Host ?」萃取並結構化成可用於實戰教學、專案練習與能力評估的 16 個解決方案案例。

## Case #1: 以 Self-Host 對齊 Container 生命週期，解決註冊/反註冊時機不可控

### Problem Statement（問題陳述）
業務場景：在 Windows Container 上部署 .NET Framework Web API 微服務，服務需與 Service Discovery（如 Consul）整合：啟動時註冊、停止前移除、運作期間送心跳。若採 IIS Host，App Pool 啟停由 IIS 管理，難以精準掌控服務 start/end，造成註冊/反註冊時機不確定。
技術挑戰：IIS 是 Windows Service，容器需指定單一 entrypoint；IIS 還有 App Pool 延遲啟動（首個請求才啟動）等行為，使註冊時機與容器生命周期錯位。
影響範圍：導致 Service Discovery 註冊資訊不一致、重複註冊、或未註冊就接流量，進而引起路由錯誤與異常。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 容器需以單一 process 為 entrypoint，但 IIS 為 Windows Service，需 ServiceMonitor 轉接。
2. App Pool 由 IIS 管控，Application_Start 可能多次觸發且延遲啟動。
3. Developer 無法精準知道服務「何時啟動完成」與「何時即將終止」。
深層原因：
- 架構層面：IIS/App Pool 的生命周期與 Container 的 process 模式不一致。
- 技術層面：ASP.NET 在 IIS 下的生命週期事件（Application_Start/End）與容器 runtime 對 start/stop 的期望不匹配。
- 流程層面：Dev 與 Ops 的職責界線依賴傳統 IIS 能力，未對 Container 與 Orchestrator 重新分工。

### Solution Design（解決方案設計）
解決策略：改採 Self-Host（Console + OWIN），讓 Web API 與註冊/反註冊與心跳都在同一個 process 中，直接作為容器 entrypoint。以此精準掌握 start/end，將 IIS 的運維能力交由 Orchestrator/Reverse Proxy 承擔。

實施步驟：
1. 建立 Self-Host 啟動器
- 實作細節：使用 OWIN/WebApp.Start 啟動 Web API；於啟動後立即執行註冊。
- 所需資源：Microsoft.Owin.Hosting、System.Web.Http
- 預估時間：0.5 天
2. 實作關機攔截與反註冊
- 實作細節：以 SetConsoleCtrlHandler/HiddenForm 接收 OS 停止訊號；在反註冊後等待緩衝（例如 5 秒）。
- 所需資源：Win32 API、Windows Forms（Hidden Form）
- 預估時間：1 天
3. 容器化與啟動策略
- 實作細節：在 Dockerfile 指定 ENTRYPOINT 為 Self-Host 可執行檔；以 --restart always 等策略維持高可用。
- 所需資源：microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
class Program {
  static void Main(string[] args) {
    using (WebApp.Start<Startup>("http://localhost:9000/"))
    {
        Console.WriteLine("WebApp Started.");
        // 啟動後：在此執行 Service Discovery 註冊
        // 偵測停止（見 Case #7/#8/#9），再執行反註冊與 5 秒緩衝
    }
  }
}

public class Startup {
  public void Configuration(IAppBuilder app) {
    var config = new HttpConfiguration();
    config.Routes.MapHttpRoute("QueryApi","api/{controller}/{id}",
                               defaults: new { id = RouteParameter.Optional });
    app.UseWebApi(config);
  }
}
```

實際案例：文中 Docker 停止容器時，能看到「Deregister Services Here!!」與「Wait 5 sec...」的序列化輸出，證明時機可控。
實作環境：Windows 10 Pro 1803（Hyper-V container）、Windows Server 1709/1803；.NET Framework 4.7.2。
實測數據：
- 改善前：IIS 內部 Application_Start/End 事件不穩定（可能多次）、延遲啟動（需首個請求）。
- 改善後：Self-Host 啟動即註冊、停止即反註冊，單一 process、單點控制。
- 改善幅度：註冊/反註冊時機控制達 100% 可預期，避免重複註冊。

Learning Points（學習要點）
核心知識點：
- 容器以單一 process 為生命周期錨點
- OWIN Self-Host 與 ASP.NET Web API 整合
- 註冊/反註冊與心跳的嵌入時機
技能要求：
- 必備技能：C#、OWIN、Docker 基礎
- 進階技能：Service Discovery（如 Consul）整合、容器運維
延伸思考：
- 方案可應用於任何需精準 start/end 控制的微服務
- 風險：Console/OS 訊號攔截在不同 Windows 版本行為差異
- 優化：抽象成通用 Web Host Framework，統一納管

Practice Exercise（練習題）
- 基礎練習：建立最小 Self-Host Web API 並啟動（30 分鐘）
- 進階練習：在啟動/停止時輸出註冊/反註冊訊息，容器中用 docker stop 驗證（2 小時）
- 專案練習：封裝 Self-Host 基礎框架，可插拔 Consul/Etcd 註冊器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能啟動/停止並輸出註冊/反註冊
- 程式碼品質（30%）：清晰結構、適當抽象
- 效能優化（20%）：啟停延遲最小、無無謂阻塞
- 創新性（10%）：可插拔、跨專案可重用的框架設計


## Case #2: 移除「先有流量才啟動」的死結：先註冊、後接流

### Problem Statement（問題陳述）
業務場景：微服務需先在 Service Discovery 註冊後，API Gateway 才能將流量導入；但 IIS 預設延遲啟動 App Pool，需先有請求才會觸發 Application_Start，造成「註冊需啟動、啟動需請求、請求需註冊」的循環。
技術挑戰：在容器啟動時即完成註冊，且在未註冊前不應接收流量。
影響範圍：註冊延遲導致路由不到、或服務尚未 ready 即被呼叫。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. IIS App Pool 預設 lazy start：首個請求才啟動。
2. 註冊邏輯只能放在 Application_Start，時機不可控。
3. 服務未註冊前 Gateway 找不到可用實例。
深層原因：
- 架構層面：IIS 啟動策略與 Service Discovery 契約矛盾。
- 技術層面：Web API 生命週期綁在 IIS 事件。
- 流程層面：未建立啟動順序（Register → Heartbeat → Serve）。

### Solution Design（解決方案設計）
解決策略：在 Self-Host 啟動序列中，啟動 OWIN 後立即進行註冊，註冊完成後開始 heartbeats，最後才進入等待停止的循環，保證註冊先行。

實施步驟：
1. 啟動序列重排
- 實作細節：WebApp.Start 後立刻呼叫註冊；啟動心跳 Task；最後等待 WaitHandle。
- 所需資源：OWIN、自製註冊器
- 預估時間：0.5 天
2. 就緒/存活探針設計
- 實作細節：心跳啟動後才標記就緒，避免註冊未完成即接流。
- 所需資源：心跳實作、健康檢查端點（下篇延伸）
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
using (WebApp.Start<Startup>(baseAddress)) {
  Console.WriteLine("WebApp Started.");

  // 1) 註冊
  Console.WriteLine("Register Services Here!");

  // 2) 心跳
  bool stop = false;
  var heartbeats = Task.Run(() => {
    while(!stop) { Task.Delay(1000).Wait(); Console.WriteLine("Heartbeat..."); }
  });

  // 3) 等待停止
  int idx = WaitHandle.WaitAny(new WaitHandle[]{ close, _form.shutdown });

  // 4) 反註冊 + 緩衝
  Console.WriteLine("Deregister Services Here!!");
  stop = true; heartbeats.Wait();
  Task.Delay(5000).Wait();
}
```

實際案例：Docker 停止時，觀察 log 順序為 Started → Register → Heartbeat → Deregister → Stop。
實作環境：同 Case #1。
實測數據：
- 改善前：IIS 預設啟動在首個請求之後。
- 改善後：容器啟動即註冊，避免死結。
- 改善幅度：路由可用性從不可預期提升為可預期（Ready-First）。

Learning Points（學習要點）
核心知識點：
- 啟動序列對 Service Discovery 的重要性
- Ready/Liveness 探針觀念
- Heartbeat 與反註冊的配合
技能要求：
- 必備技能：C#、Task 協作、事件處理
- 進階技能：健康檢查與就緒閘門設計
延伸思考：
- 可應用於任何需要先註冊後接流的場景
- 限制：外部註冊服務不可用時的重試策略
- 優化：加上註冊重試/backoff 與 ready 超時

Practice Exercise（練習題）
- 基礎：將註冊移到 Self-Host 啟動後立即執行（30 分）
- 進階：加入 ready 標誌，註冊成功後才返回 200（2 小時）
- 專案：完成註冊重試與 ready 超時退化策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：啟動順序正確
- 程式碼品質（30%）：錯誤處理與重試邏輯
- 效能優化（20%）：啟動時間最小化
- 創新性（10%）：就緒門檻與異常降級策略


## Case #3: 消除 App Pool 回收造成的重複註冊

### Problem Statement（問題陳述）
業務場景：在 IIS Host 下，App Pool 可能因 idle/超限/回收策略而多次回收重建。每次 Application_Start 觸發都會再註冊一次，導致重複註冊。
技術挑戰：保證每個容器實例僅有一次註冊記錄，且停止時能反註冊。
影響範圍：Registry 汙染、錯誤路由、觀測性混亂。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. App Pool 多次回收/並行，導致多次啟動事件。
2. 註冊邏輯綁在 Application_Start，且無唯一實例 ID。
3. 反註冊可能未被觸發（例如 App Pool 被終止）。
深層原因：
- 架構層面：多實例/多工與註冊模型衝突。
- 技術層面：在 IIS 事件中難以對容器實例級別控管。
- 流程層面：未定義唯一實例 ID 與對等反註冊。

### Solution Design（解決方案設計）
解決策略：採 Self-Host 單一 process 模式；在啟動時產生唯一 serviceID 並註冊，停止時確保反註冊；避免 IIS 多 App Pool 並發與回收干擾。

實施步驟：
1. 單進程 Self-Host
- 實作細節：避免 IIS 多 App Pool，單 process 對應一容器。
- 所需資源：OWIN
- 預估時間：0.5 天
2. 唯一實例 ID
- 實作細節：serviceID 使用 GUID，作為註冊鍵。
- 所需資源：Guid API
- 預估時間：0.2 天

關鍵程式碼/設定：
```csharp
string serviceID = $"IP2CAPI-{Guid.NewGuid():N}".ToUpper();
// 使用 serviceID 註冊；停止時用相同 serviceID 反註冊
```

實際案例：範例以 GUID 為實例 ID，避免重覆。
實作環境：同前。
實測數據：
- 改善前：IIS 多次 Application_Start，易致重複註冊。
- 改善後：Self-Host 單 process + GUID 實例 ID，觀察紀錄僅 1 次註冊/反註冊。
- 改善幅度：重複註冊問題歸零。

Learning Points（學習要點）
核心知識點：
- 實例唯一識別的重要性
- App Pool 回收行為
- 註冊/反註冊對等關係
技能要求：
- 必備：C#、GUID/ID 設計
- 進階：服務註冊鍵命名規則與衝突避免
延伸思考：
- 更嚴謹的 ID 組成（服務名+版本+節點+GUID）
- 風險：ID 洩漏或碰撞（極低）
- 優化：引入服務標籤與 metadata

Practice Exercise（練習題）
- 基礎：在啟動時打印 serviceID（30 分）
- 進階：用 serviceID 完成註冊與反註冊（2 小時）
- 專案：在 Service Discovery 中用 serviceID 查詢/下線實例（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：唯一 ID 正確使用
- 程式碼品質（30%）：封裝與測試
- 效能優化（20%）：ID 生成開銷低
- 創新性（10%）：ID 擴展字段設計


## Case #4: 移除 ServiceMonitor 疊層，直接以 Console 為 EntryPoint

### Problem Statement（問題陳述）
業務場景：使用官方 IIS 容器映像需借助 ServiceMonitor.exe 監控 w3svc，將 Windows Service 狀態轉為容器 entrypoint 結束條件，導致架構疊層複雜。
技術挑戰：容器需要單一 process 管控生命周期，避免多層轉接與不必要資源開銷。
影響範圍：Dockerfile 複雜、資源佔用增加、故障點增多。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. IIS 無法直接作為容器 entrypoint。
2. 需藉由 ServiceMonitor.exe 轉接 w3svc 狀態。
3. 監控/轉接多一層故障點與資源消耗。
深層原因：
- 架構層面：IIS 與容器單 process 模式不一致。
- 技術層面：Windows Service 與容器 entrypoint 的不相容。
- 流程層面：沿用傳統 IIS 模式未針對容器重構。

### Solution Design（解決方案設計）
解決策略：改為自有 Console Self-Host，Dockerfile 直接以該 exe 作為 ENTRYPOINT，讓容器與進程生命周期完全一致；使用 --restart always 取得類 Windows Service 行為。

實施步驟：
1. 撰寫自有 Dockerfile
- 實作細節：選用 dotnet-framework runtime 映像；EXPOSE/ENTRYPOINT 指向 Self-Host exe。
- 所需資源：microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709
- 預估時間：0.5 天
2. 啟動策略
- 實作細節：docker run -d --restart always ...；容器失敗自動重啟。
- 所需資源：Docker CLI
- 預估時間：0.2 天

關鍵程式碼/設定：
```dockerfile
FROM microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709
WORKDIR c:/selfhost
COPY . .
EXPOSE 80
ENTRYPOINT IP2C.WebAPI.SelfHost.exe
```
```bash
docker run -d --restart always --name ip2c ip2c.selfhost:demo
```

實際案例：以自有 Dockerfile 啟動，容器 lifecycle 完全由 Self-Host 控制，停止時序可精準掌握。
實作環境：Windows 10/Server；Docker for Windows。
實測數據：
- 改善前：IIS + ServiceMonitor 疊層。
- 改善後：單層 Console 入口，降低資源與複雜度；配合 Case #5 亦帶來效能提升。
- 改善幅度：流程簡化、故障點減少（定性）。

Learning Points（學習要點）
核心知識點：
- 容器 entrypoint 與服務 lifecycle 關係
- Docker restart policy 應用
- Windows 容器基底選擇
技能要求：
- 必備：Dockerfile、Windows 容器
- 進階：CI/CD 與映像版控策略
延伸思考：
- 可應用於所有 .NET Framework 自架主機服務
- 限制：僅適用於 Windows Container
- 優化：多階段 build、縮小映像

Practice Exercise（練習題）
- 基礎：以 Self-Host exe 為 ENTRYPOINT（30 分）
- 進階：加入 --restart always 並測試自動重啟（2 小時）
- 專案：整合 CI 自動 build/push/run 自家映像（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：容器可正常啟停
- 程式碼品質（30%）：Dockerfile 清晰、可重複建置
- 效能優化（20%）：映像大小與啟動時間
- 創新性（10%）：自動化與最佳化技巧


## Case #5: Self-Host 相對 IIS 的效能優化（+17.5% RPS）

### Problem Statement（問題陳述）
業務場景：相同硬體/程式碼下，追求更高吞吐與更低延遲。
技術挑戰：IIS 具備額外功能與管理成本，可能降低純 API 場景效能。
影響範圍：整體 RPS、延遲、資源使用率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. IIS 提供額外安全/管理/多站台功能。
2. 為達成 App Pool 管控帶來額外 overhead。
3. 對單純微服務 API 場景為不必要負擔。
深層原因：
- 架構層面：功能重疊（IIS vs Orchestrator/Proxy）。
- 技術層面：IIS pipeline 與管理成本。
- 流程層面：未按 CDD 簡化最小可行運行環境。

### Solution Design（解決方案設計）
解決策略：採用 OWIN Self-Host 以減少中間層，保留純 API pipeline；將原本 IIS 的運維功能交給 Orchestrator/Proxy。

實施步驟：
1. 切換 Self-Host
- 實作細節：如 Case #1/#4。
- 所需資源：OWIN
- 預估時間：1 天
2. 基準測試
- 實作細節：相同程式碼下以 ab/wrk 或同等工具測 RPS/延遲。
- 所需資源：壓測工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
參考文章測試數據：
IIS 8: 4778.23 req/s, 20.928 ms/req
Self-Host: 5612.23 req/s, 17.818 ms/req
→ RPS +17.5%，延遲 -14.9%
```

實際案例：引用文中第三方測試（連結於原文）。
實作環境：Windows 8 時代測試基準（概念上於現代環境仍成立）。
實測數據：
- 改善前（IIS 8）：4778.23 req/s；20.928 ms/req
- 改善後（Self-Host）：5612.23 req/s；17.818 ms/req
- 改善幅度：RPS +17.5%，延遲 -14.9%

Learning Points（學習要點）
核心知識點：
- 最小化 pipeline 可提升效能
- 架構職責分離
- 壓測方法與指標
技能要求：
- 必備：壓測工具使用
- 進階：效能剖析、瓶頸定位
延伸思考：
- 是否需要 IIS 特性（如綜合認證、URL Rewrite）
- 風險：自架需補齊必要安全
- 優化：Kestrel/.NET Core 進一步提升

Practice Exercise（練習題）
- 基礎：對 Self-Host 跑簡單壓測（30 分）
- 進階：對 IIS 與 Self-Host 比較（2 小時）
- 專案：引入 APM 並分析瓶頸（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：壓測可執行
- 程式碼品質（30%）：測試腳本清晰
- 效能優化（20%）：能提出改進建議
- 創新性（10%）：多維度觀測方案


## Case #6: 修正「找不到 Controller」— 強制載入程序集或自訂 IAssembliesResolver

### Problem Statement（問題陳述）
業務場景：Self-Host 專案參考了 Web API 專案，但啟動時出現「No type was found that matches the controller named 'ip2c'」。
技術挑戰：Web API 的 Controller 所在 Assembly 可能尚未載入 AppDomain，預設 resolver 無法發現。
影響範圍：API 全面 404/500，服務不可用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. DefaultAssembliesResolver 僅檢視 AppDomain.CurrentDomain.GetAssemblies()。
2. 引用 Assembly 採延遲載入，未引用任何型別時不會載入。
3. Controller 未出現在掃描清單。
深層原因：
- 架構層面：多專案組件化與運行期載入策略。
- 技術層面：反射掃描策略依賴已載入程序集。
- 流程層面：未有顯式載入或自訂 resolver。

### Solution Design（解決方案設計）
解決策略：在 OWIN Startup 內用程式碼強制引用 Controller 型別以促使 Assembly 載入；或實作自訂 IAssembliesResolver，顯式加入目標 Assembly。

實施步驟：
1. 強制載入 Assembly
- 實作細節：以 typeof(ControllerType) 參考，確保載入。
- 所需資源：C#
- 預估時間：0.2 天
2. 可選：自訂 Resolver
- 實作細節：實作 IAssembliesResolver，Replace 內建實作。
- 所需資源：System.Web.Http.Dispatcher
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public void Configuration(IAppBuilder app) {
  var config = new HttpConfiguration();
  // 強制載入
  Console.WriteLine($"- Force load controller: {typeof(IP2CController)}");
  Console.WriteLine($"- Force load controller: {typeof(DiagController)}");
  app.UseWebApi(config);
}

// 可選：自訂 resolver
// config.Services.Replace(typeof(IAssembliesResolver), new MyAssembliesResolver());
```
```csharp
// 內建 resolver 摘要（來源於原始碼）
public class DefaultAssembliesResolver : IAssembliesResolver {
  public virtual ICollection<Assembly> GetAssemblies() =>
      AppDomain.CurrentDomain.GetAssemblies().ToList();
}
```

實際案例：加入強制載入後，API 正常回應。
實作環境：Self-Host + Web API 分離專案。
實測數據：
- 改善前：啟動後路由不到 Controller，回 404。
- 改善後：Controller 能被解析，路由成功。
- 改善幅度：可用性由 0% → 100%。

Learning Points（學習要點）
核心知識點：
- AppDomain 與延遲載入
- Web API 組件解析流程
- Startup 管線與相依裝載
技能要求：
- 必備：C# 反射/載入概念
- 進階：自訂 Web API 服務拓展點
延伸思考：
- 可用 Assembly Scanning 策略（白名單/黑名單）
- 風險：硬編碼型別依賴
- 優化：以設定/命名規約自動載入

Practice Exercise（練習題）
- 基礎：加入 typeof 強制載入修復錯誤（30 分）
- 進階：撰寫自訂 IAssembliesResolver（2 小時）
- 專案：建立可配置的程序集掃描器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：錯誤成功修復
- 程式碼品質（30%）：擴展性與可測試性
- 效能優化（20%）：掃描成本控制
- 創新性（10%）：自動化載入機制


## Case #7: 用 SetConsoleCtrlHandler 捕捉停機訊號，確保反註冊得以執行

### Problem Statement（問題陳述）
業務場景：容器停止常由 orchestrator 或 docker stop 觸發，非互動式；若不攔截 OS 訊號，反註冊與收尾可能無法執行。
技術挑戰：Console.ReadLine 只適合互動開發，需改為處理 CTRL_C/CTRL_BREAK/CTRL_SHUTDOWN 事件。
影響範圍：殘留註冊、心跳未停止、請求中斷。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 預設沒有訊號處理，進程被直接終止。
2. 反註冊/收尾程式碼無法被執行。
3. Console.ReadLine 不適用於生產容器。
深層原因：
- 架構層面：需以 OS 訊號驅動關閉流程。
- 技術層面：Windows Console 訊號處理需 Win32 API。
- 流程層面：缺乏停機事件統一入口。

### Solution Design（解決方案設計）
解決策略：以 SetConsoleCtrlHandler 註冊處理常見控制訊號，喚醒主執行緒執行反註冊與緩衝收尾。

實施步驟：
1. 設置 Console Ctrl Handler
- 實作細節：捕捉 CTRL_C/CTRL_BREAK/CTRL_CLOSE/CTRL_LOGOFF/CTRL_SHUTDOWN。
- 所需資源：Win32 API
- 預估時間：0.5 天
2. 主執行緒等待訊號
- 實作細節：以 ManualResetEvent/WaitHandle 協調。
- 所需資源：System.Threading
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
[DllImport("Kernel32")] static extern bool SetConsoleCtrlHandler(EventHandler handler, bool add);
delegate bool EventHandler(CtrlType sig);
enum CtrlType { CTRL_C_EVENT=0, CTRL_BREAK_EVENT=1, CTRL_CLOSE_EVENT=2,
                CTRL_LOGOFF_EVENT=5, CTRL_SHUTDOWN_EVENT=6 }

private static ManualResetEvent close = new ManualResetEvent(false);
private static bool ShutdownHandler(CtrlType sig) {
  close.Set();
  Console.WriteLine($"EVENT: ShutdownHandler({sig})");
  return true;
}

// 註冊/解除
SetConsoleCtrlHandler(ShutdownHandler, true);
// ... WaitHandle.WaitAny(new WaitHandle[]{ close, _form.shutdown });
SetConsoleCtrlHandler(ShutdownHandler, false);
```

實際案例：在 Windows Server 1803 可攔到 CTRL_SHUTDOWN_EVENT；Log 顯示捕捉到事件並完成反註冊。
實作環境：Windows 10/Server；差異見 Case #8/#9。
實測數據：
- 改善前：docker stop 後常直接中斷，收尾未執行。
- 改善後：成功捕捉訊號與反註冊，完成 5 秒緩衝。
- 改善幅度：收尾可預期與完整度顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- Windows Console 訊號處理
- 主/子執行緒協同
- 關閉流程設計
技能要求：
- 必備：P/Invoke、執行緒同步
- 進階：跨作業系統訊號抽象
延伸思考：
- 非 Windows 平台的信號對應（SIGTERM/SIGINT）
- 風險：版本差異（見 Case #8）
- 優化：抽象成可重用模組

Practice Exercise（練習題）
- 基礎：攔截 CTRL_C 並打印訊息（30 分）
- 進階：攔截訊號並執行反註冊+緩衝（2 小時）
- 專案：封裝訊號處理中介層（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：訊號皆可捕捉
- 程式碼品質（30%）：模組化與測試
- 效能優化（20%）：無阻塞風險
- 創新性（10%）：多平台抽象


## Case #8: 以 HiddenForm 捕捉 WM_QUERYENDSESSION，補齊 1709 的停機攔截

### Problem Statement（問題陳述）
業務場景：在 Windows Server 1709 環境，SetConsoleCtrlHandler 對 docker stop 的攔截不穩，需另闢途徑捕捉 OS 關機/登出訊息。
技術挑戰：Console 模式下無訊息泵浦，需建隱藏視窗攔截 WM_QUERYENDSESSION。
影響範圍：停機流程不完整、反註冊可能遺漏。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 1709 上 docker stop 不一定觸發 Console 控制訊號。
2. Console 無視窗訊息迴圈，無法直接收消息。
3. 反註冊時間窗受 OS 限制（~10 秒）。
深層原因：
- 架構層面：版本差異導致信號機制不一致。
- 技術層面：需建立 Message Loop 才能攔截 WM_QUERYENDSESSION。
- 流程層面：未兼容多來源停機訊號。

### Solution Design（解決方案設計）
解決策略：啟動隱藏窗體（HiddenForm），在 WndProc 處理 WM_QUERYENDSESSION；用 ManualResetEvent 與主執行緒協調停機流程。

實施步驟：
1. 啟動隱藏窗體
- 實作細節：Application.Run(hiddenForm) 於背景 Task；設定不顯示。
- 所需資源：Windows Forms
- 預估時間：0.5 天
2. 攔截 WM_QUERYENDSESSION
- 實作細節：覆寫 WndProc，Set ManualResetEvent。
- 所需資源：WinMsg
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
_form = new HiddenForm { ShowInTaskbar=false, Visible=false, WindowState=FormWindowState.Minimized };
Task.Run(() => Application.Run(_form));

public class HiddenForm : Form {
  public ManualResetEvent shutdown = new ManualResetEvent(false);
  protected override void WndProc(ref Message m) {
    if (m.Msg == 0x11) { // WM_QUERYENDSESSION
      m.Result = (IntPtr)1;
      Console.WriteLine("winmsg: WM_QUERYENDSESSION");
      shutdown.Set();
      while(!this._form_closing) Thread.SpinWait(100); // 爭取處理時間（見 Case #9）
      return;
    }
    base.WndProc(ref m);
  }
  private bool _form_closing = false;
  protected override void OnClosing(CancelEventArgs e) { _form_closing = true; }
}
```

實際案例：1709 上以 HiddenForm 成功攔截 docker stop，並完整執行反註冊與 5 秒緩衝。
實作環境：Windows Server 1709。
實測數據：
- 改善前：docker stop 幾乎無法攔截，收尾多半失敗。
- 改善後：捕捉 WM_QUERYENDSESSION，收尾成功，約有 10 秒上限。
- 改善幅度：停機收尾成功率顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- Win32 視窗訊息與關機流程
- Console 與 Forms 併用技巧
- 版本差異的兼容策略
技能要求：
- 必備：WinForm/Win32 訊息處理
- 進階：時間窗管理與非阻塞設計
延伸思考：
- 非 GUI 環境下如何實作訊息循環（Native）
- 風險：SpinWait 設計與 CPU 佔用
- 優化：限時處理與降載策略

Practice Exercise（練習題）
- 基礎：建立 HiddenForm 並攔截 WM_QUERYENDSESSION（30 分）
- 進階：與主程序 WaitHandle 協同收尾（2 小時）
- 專案：包裝多來源停機訊號中介層（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：1709 能成功攔截
- 程式碼品質（30%）：非阻塞與可維護性
- 效能優化（20%）：SpinWait 的影響控制
- 創新性（10%）：跨版本適配策略


## Case #9: 停機期間避免阻塞呼叫，保住 5–10 秒收尾時間窗

### Problem Statement（問題陳述）
業務場景：OS 停機給應用的時間有限（1709 約 10 秒、1803 約 5 秒）。若使用 Thread.Sleep、Task.Wait 等阻塞操作，常在 1 秒內就被強制終止，導致收尾未完成。
技術挑戰：在有限時間窗內完成反註冊與任務終止，不可被阻塞。
影響範圍：註冊遺留、請求中斷、資料不一致。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 阻塞操作易被 OS 視為無回應而強制終止。
2. docker stop -t 的 timeout 與 Windows 上限不一致。
3. 版本差異導致可用時間窗不同。
深層原因：
- 架構層面：停機流程時間窗管理。
- 技術層面：阻塞式等待在停機期不可靠。
- 流程層面：缺乏「快速響應、有限度忙等」策略。

### Solution Design（解決方案設計）
解決策略：在停機訊號處理期間避免 Sleep/Wait；使用 SpinWait 或短輪詢快速響應；優先完成反註冊與關鍵任務，最後以固定緩衝等待。

實施步驟：
1. 替換阻塞等待
- 實作細節：由 Thread.Sleep/Task.Wait 改為 SpinWait 或微小間隔輪詢。
- 所需資源：System.Threading
- 預估時間：0.2 天
2. 定序關鍵任務
- 實作細節：先反註冊、停心跳，再緩衝等待。
- 所需資源：程式碼調整
- 預估時間：0.2 天

關鍵程式碼/設定：
```csharp
// 在 HiddenForm.WndProc 停機時：用 SpinWait 爭取處理時間
while (!this._form_closing) Thread.SpinWait(100);

// 在主流程：反註冊 → 停心跳 → 緩衝
Console.WriteLine("Deregister Services Here!!");
stop = true; heartbeats.Wait();
Task.Delay(5000).Wait();
```

實際案例：1709/1803 以非阻塞設計，能在 5–10 秒內完成反註冊與心跳停止。
實作環境：Windows Server 1709/1803。
實測數據：
- 改善前：Sleep/Wait 常於 ~1 秒被中止。
- 改善後：SpinWait/快速回應可維持到 5–10 秒。
- 改善幅度：收尾成功率大幅提升（定性）。

Learning Points（學習要點）
核心知識點：
- 停機時限與阻塞操作風險
- 非阻塞/忙等策略
- 收尾任務優先順序
技能要求：
- 必備：多執行緒、同步
- 進階：時間窗內任務排程
延伸思考：
- 用 CancellationToken 取代旗標
- 風險：SpinWait CPU 消耗
- 優化：自適應等待策略

Practice Exercise（練習題）
- 基礎：以 SpinWait 取代 Sleep（30 分）
- 進階：完成「反註冊→停心跳→緩衝」次序（2 小時）
- 專案：評估不同等待策略的 CPU/時效（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：停機流程完整
- 程式碼品質（30%）：並發安全
- 效能優化（20%）：等待策略平衡
- 創新性（10%）：自適應設計


## Case #10: 用 WaitHandle.WaitAny 串接多來源停機事件

### Problem Statement（問題陳述）
業務場景：停機可能來自使用者（CTRL-C、關閉視窗）或 OS（關機/登出）。需統一等待並正確分類處理。
技術挑戰：同時監聽多個事件來源並保證單次收尾序列。
影響範圍：重複觸發、收尾順序錯亂。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多來源事件無統一協調。
2. 主執行緒等待邏輯混亂。
3. 可能多次執行收尾。
深層原因：
- 架構層面：停機事件聚合缺失。
- 技術層面：跨執行緒事件同步不完善。
- 流程層面：缺乏單次執行的保證。

### Solution Design（解決方案設計）
解決策略：以 WaitHandle.WaitAny 等待「使用者事件」與「OS 事件」兩個 ManualResetEvent 任一；喚醒後執行單次收尾。

實施步驟：
1. 建立多事件等待
- 實作細節：ManualResetEvent close 與 _form.shutdown；WaitAny。
- 所需資源：System.Threading
- 預估時間：0.2 天
2. 單次收尾保障
- 實作細節：喚醒後立即切換狀態避免重入。
- 所需資源：程式碼調整
- 預估時間：0.2 天

關鍵程式碼/設定：
```csharp
int shutdown_index = WaitHandle.WaitAny(new WaitHandle[] { close, _form.shutdown });
Console.WriteLine(new string[] {
  "EVENT: User press CTRL-C, CTRL-BREAK or close window...",
  "EVENT: System shutdown or logoff..."
}[shutdown_index]);
// → 反註冊 → 停心跳 → 緩衝
```

實際案例：log 顯示能辨識兩種來源並進入相同收尾序列。
實作環境：同前。
實測數據：
- 改善前：不同來源各自處理，易重入。
- 改善後：統一入口與序列，收尾一次性。
- 改善幅度：一致性提升、風險降低（定性）。

Learning Points（學習要點）
核心知識點：
- WaitHandle 與同步原語
- 多來源事件聚合
- 單次收尾保障
技能要求：
- 必備：執行緒同步
- 進階：事件去重與重入控制
延伸思考：
- 擴展更多訊號來源（健康探針 failfast）
- 風險：事件漏接
- 優化：註冊事件與取消訂閱時機

Practice Exercise（練習題）
- 基礎：WaitAny 監聽兩事件（30 分）
- 進階：加入重入保護（2 小時）
- 專案：封裝停機事件匯流排（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：多來源均可處理
- 程式碼品質（30%）：無重入、清晰
- 效能優化（20%）：無 Busy Loop 濫用
- 創新性（10%）：通用化封裝


## Case #11: 心跳背景任務的可靠終止與協同

### Problem Statement（問題陳述）
業務場景：Service Discovery 需持續心跳；停機時需先停心跳，避免誤判或心跳殘留。
技術挑戰：心跳任務需與停機事件協作，以旗標或取消令終止。
影響範圍：健康檢查誤判、監控噪音。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 心跳任務獨立執行，若不終止會持續發送。
2. 停機時若未先停心跳，可能產生不一致。
3. 阻塞等待導致無法及時終止。
深層原因：
- 架構層面：背景任務與主流程協作欠缺。
- 技術層面：取消機制使用不當。
- 流程層面：停機序列未定義。

### Solution Design（解決方案設計）
解決策略：啟動心跳任務時以 stop 旗標/取消令控制；停機訊號到時先設旗標、等待任務退出，再進入緩衝。

實施步驟：
1. 啟動心跳任務
- 實作細節：以 Task.Run + while(!stop) + Delay。
- 所需資源：Task
- 預估時間：0.2 天
2. 停機時終止
- 實作細節：stop=true；heartbeats.Wait()；再緩衝。
- 所需資源：任務協同
- 預估時間：0.2 天

關鍵程式碼/設定：
```csharp
bool stop = false;
var heartbeats = Task.Run(() => {
  Console.WriteLine("Start heartbeats.");
  while(!stop) { Task.Delay(1000).Wait(); Console.WriteLine("Heartbeat..."); }
  Console.WriteLine("Stop heartbeats.");
});

// 停機
stop = true;
heartbeats.Wait();
```

實際案例：log 顯示停機時心跳能按序停止。
實作環境：同前。
實測數據：
- 改善前：心跳可能在停機時仍發送。
- 改善後：心跳任務可控終止。
- 改善幅度：一致性提升（定性）。

Learning Points（學習要點）
核心知識點：
- 背景任務協同
- 取消模式（旗標/CancellationToken）
- 停機序列設計
技能要求：
- 必備：Task/同步
- 進階：取消令、例外處理
延伸思考：
- 使用 CancellationToken 替代旗標
- 風險：阻塞等待
- 優化：非阻塞終止

Practice Exercise（練習題）
- 基礎：實作心跳任務（30 分）
- 進階：可取消並等待退出（2 小時）
- 專案：統一封裝 BackgroundService（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：心跳可正確啟停
- 程式碼品質（30%）：可讀/可測試
- 效能優化（20%）：無不必要輪詢
- 創新性（10%）：可重用封裝


## Case #12: 建立最小 Windows 容器映像，對應 Self-Host 的部署需求

### Problem Statement（問題陳述）
業務場景：將 Self-Host Web API 打包為 Windows Container 部署。
技術挑戰：選擇合適基底映像、設定 ENTRYPOINT、暴露埠、處理 OS 版本兼容（1709/1803）。
影響範圍：部署可靠性、啟動時間、跨環境一致性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. .NET Framework 僅能用 Windows 容器。
2. 主機/容器 OS 版本需一致（否則需 Hyper-V 容器）。
3. 映像過大與多層影響啟動速度。
深層原因：
- 架構層面：映像與執行環境契合度。
- 技術層面：Dockerfile 編寫與最佳化。
- 流程層面：測試/生產一致性。

### Solution Design（解決方案設計）
解決策略：採用 microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709 作基底；EXPOSE/ENTRYPOINT 配置 Self-Host；按目標 OS 版本選擇對應基底。

實施步驟：
1. 撰寫 Dockerfile（見 Case #4）
- 實作細節：WORKDIR/COPY/EXPOSE/ENTRYPOINT。
- 所需資源：Docker
- 預估時間：0.5 天
2. 版本匹配
- 實作細節：主機 1803 → 基底 1803；主機 1709 → 基底 1709。
- 所需資源：對應映像
- 預估時間：0.2 天

關鍵程式碼/設定：
```dockerfile
FROM microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709
WORKDIR c:/selfhost
COPY . .
EXPOSE 80
ENTRYPOINT IP2C.WebAPI.SelfHost.exe
```

實際案例：於 Windows 10 Pro（Hyper-V container）啟動約 30 秒；Windows Server 約 5 秒。
實作環境：Win10 Pro 1803、Windows Server 1709/1803。
實測數據：
- 改善前：IIS 映像啟動較複雜。
- 改善後：Self-Host 映像啟動更簡單。
- 改善幅度：啟動時間在 Server 約 5 秒；Win10 Hyper-V 約 30 秒（觀察數據）。

Learning Points（學習要點）
核心知識點：
- Windows 容器與 OS 版本匹配
- Dockerfile 基本結構
- 映像啟動時間觀測
技能要求：
- 必備：Docker 基礎
- 進階：多階段 build、映像最佳化
延伸思考：
- 針對 .NET Core 可改用 Nano/Kestrel
- 風險：映像過大
- 優化：以 CI/CD 自動建置

Practice Exercise（練習題）
- 基礎：撰寫 Dockerfile 並本地啟動（30 分）
- 進階：測試不同 OS 版本映像（2 小時）
- 專案：建置/推送/部署流水線（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：映像可啟動
- 程式碼品質（30%）：Dockerfile 清晰簡潔
- 效能優化（20%）：啟動時間與大小
- 創新性（10%）：版本管理策略


## Case #13: 跨環境驗證（Win10/Server/1709/1803）與行為差異

### Problem Statement（問題陳述）
業務場景：相同 Self-Host 在不同 Windows 版本與容器模式（Hyper-V vs Process）有不同啟動時長與停機事件行為。
技術挑戰：建立跨環境一致的驗證流程，理解差異。
影響範圍：SLA 估算、就緒探針設定、收尾策略。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Hyper-V 容器啟動慢（Win10 約 30 秒）。
2. 1709/1803 對停機訊號攔截差異。
3. docker stop -t 設定與實際時間窗不一致。
深層原因：
- 架構層面：部署環境差異。
- 技術層面：容器模式與 OS 信號機制差別。
- 流程層面：缺乏跨環境驗證腳本與基準。

### Solution Design（解決方案設計）
解決策略：設計統一驗證步驟（pull/run/logs/stop/logs）；收集啟動耗時、停機訊號來源、收尾成功率；據此校準就緒與停機策略。

實施步驟：
1. 驗證腳本
- 實作細節：docker pull/run/logs/stop；間隔秒數控制。
- 所需資源：PowerShell/Docker CLI
- 預估時間：0.5 天
2. 數據整理
- 實作細節：記錄起停時間、事件類別、是否完成收尾。
- 所需資源：日誌蒐集工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
docker run -d --name demo ip2c.selfhost:demo
powershell sleep 10
docker logs -t demo
docker stop demo
powershell sleep 5
docker logs -t demo
```

實際案例：
- Win10 Pro 1803（Hyper-V）：啟動約 30 秒；可攔到 CTRL_SHUTDOWN_EVENT。
- Server 1709：啟動約 5 秒；需 HiddenForm 攔 WM_QUERYENDSESSION。
實測數據：
- 改善前：未掌握差異。
- 改善後：明確就緒/停機策略與時間窗。
- 改善幅度：跨環境可預期性提升（定性）。

Learning Points（學習要點）
核心知識點：
- 容器模式差異
- OS 版本行為比較
- 驗證腳本與觀測
技能要求：
- 必備：Docker/PowerShell
- 進階：日誌與指標蒐集
延伸思考：
- 引入 Ready/Liveness 探針
- 風險：在新版本仍有差異
- 優化：自動化回歸驗證

Practice Exercise（練習題）
- 基礎：手動跑驗證步驟（30 分）
- 進階：寫 PowerShell 腳本自動化（2 小時）
- 專案：建立跨環境回歸測（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：驗證步驟可重現
- 程式碼品質（30%）：腳本可靠
- 效能優化（20%）：測試時間合理
- 創新性（10%）：可視化報表


## Case #14: 將 IIS 能力轉移至 Orchestrator/Reverse Proxy，簡化服務責任

### Problem Statement（問題陳述）
業務場景：IIS 提供 logging、throttling、warm-up、多站台等能力；於微服務+容器架構下，這些多由 Orchestrator/Reverse Proxy 承擔，IIS 顯冗餘。
技術挑戰：界定職責邊界，避免功能重疊導致複雜與成本。
影響範圍：可維護性、資源使用、部署複雜度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Orchestrator 已能做擴縮、部署、監控。
2. Reverse Proxy 能做路由、多站台、TLS 終結等。
3. 在容器內再放 IIS 重複投資。
深層原因：
- 架構層面：微服務職責拆分。
- 技術層面：平台化能力的利用。
- 流程層面：持續交付/自動化流程設計。

### Solution Design（解決方案設計）
解決策略：遵循「一容器一進程」，以 Self-Host 實作最小 API；由 Orchestrator 管理擴縮/部署/健康，由 Reverse Proxy 管多站台/路由/TLS；日誌/限流以平台方案實作。

實施步驟：
1. 職責盤點
- 實作細節：列出 IIS 功能 → 映射至 Orchestrator/Proxy/Observability。
- 所需資源：系統設計討論
- 預估時間：0.5 天
2. 流程重構
- 實作細節：CI/CD、Service Discovery、網路拓撲設計。
- 所需資源：DevOps 工具鏈
- 預估時間：2–3 天

關鍵程式碼/設定：
```text
Workflow（示意）：
Client → Reverse Proxy(API Gateway) → Service Discovery 查詢 → Self-Host Service (1 process/container)
↑ Logs/Tracing → Observability Stack
↑ Scale/Deploy/Health → Orchestrator
```

實際案例：文章指出 IIS 功能與 Orchestrator/Reverse Proxy 重疊，建議以平台能力取代。
實作環境：K8s/Swarm + Proxy（Nginx/Traefik/Envoy）可比照。
實測數據：
- 改善前：IIS + 容器雙重管理。
- 改善後：單職責 Self-Host，平台承擔運維。
- 改善幅度：複雜度下降、資源利用更優（定性）。

Learning Points（學習要點）
核心知識點：
- 微服務職責劃分
- 平台 vs 應用邊界
- 基礎設施即程式（IaC）思想
技能要求：
- 必備：架構設計
- 進階：DevOps/平台工程
延伸思考：
- 可應用於跨語言微服務
- 風險：平台能力不足時的補位
- 優化：標準化 Sidecar 能力

Practice Exercise（練習題）
- 基礎：列出 IIS 功能與平台對應（30 分）
- 進階：畫出完整請求路徑與職責圖（2 小時）
- 專案：將一個 IIS 應用遷移為 Self-Host + Proxy（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：職責圖清晰
- 程式碼品質（30%）：流程文件化
- 效能優化（20%）：減少重疊成本
- 創新性（10%）：平台選型合理性


## Case #15: 反註冊後保留 5 秒緩衝，實現安全 Drain 流量

### Problem Statement（問題陳述）
業務場景：反註冊後，仍可能有尚未更新路由的請求或在途請求；需保留短暫緩衝避免硬中斷。
技術挑戰：在有限停機時間窗內安排適當緩衝，同時保障完整收尾。
影響範圍：用戶請求中斷、錯誤率上升。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Client/Proxy 更新服務列表有延遲。
2. 在途請求需時間完成。
3. 停機時間窗有限（見 Case #9）。
深層原因：
- 架構層面：服務發現的最終一致性。
- 技術層面：關閉序列設計。
- 流程層面：缺少緩衝考量。

### Solution Design（解決方案設計）
解決策略：反註冊完成後，等待固定 5 秒緩衝，讓在途請求完成、路由更新；再停止 Self-Host。

實施步驟：
1. 增加緩衝時間
- 實作細節：Task.Delay(5000).Wait() 於收尾末段。
- 所需資源：程式碼調整
- 預估時間：0.1 天
2. 規劃探針
- 實作細節：反註冊後標記不就緒，拒新請求。
- 所需資源：健康檢查/就緒標誌
- 預估時間：0.3 天

關鍵程式碼/設定：
```csharp
Console.WriteLine("Deregister Services Here!!");
stop = true; heartbeats.Wait();
Console.WriteLine("Wait 5 sec and stop web self-host.");
Task.Delay(5000).Wait();
Console.WriteLine("web self-host stopped.");
```

實際案例：Log 顯示在 deregister 後保留 5 秒再停止。
實作環境：同前。
實測數據：
- 改善前：立即停止，易中斷在途請求。
- 改善後：5 秒緩衝降低中斷風險。
- 改善幅度：穩定性提升（定性）。

Learning Points（學習要點）
核心知識點：
- 優雅關閉（Graceful Shutdown）
- 服務發現一致性延遲
- 探針與流量閘門
技能要求：
- 必備：多執行緒/時間控制
- 進階：與 Gateway 協調的 Drain 流程
延伸思考：
- 緩衝時間動態化（依請求 SLA）
- 風險：停機時間窗不足
- 優化：先標記不就緒再反註冊

Practice Exercise（練習題）
- 基礎：加入 5 秒緩衝（30 分）
- 進階：支援可配置緩衝（2 小時）
- 專案：與 Gateway 一致的 Drain 策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：關閉順序正確
- 程式碼品質（30%）：可配置與測試
- 效能優化（20%）：緩衝時間合理
- 創新性（10%）：自適應策略


## Case #16: 以 GUID 生成唯一 Service 實例 ID，避免碰撞與殘留

### Problem Statement（問題陳述）
業務場景：Service Discovery 需要唯一實例 ID；重啟或水平擴展時若 ID 重複或重用，可能導致殘留或覆蓋。
技術挑戰：在每次啟動時產生唯一且可追蹤的 ID。
影響範圍：監控混亂、誤下線、路由錯誤。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有唯一實例識別。
2. 手動命名易造成重複。
3. 反註冊需要精準對應。
深層原因：
- 架構層面：實例級別可觀測性。
- 技術層面：ID 生成與命名規範。
- 流程層面：啟動/停止規範未制定。

### Solution Design（解決方案設計）
解決策略：以 GUID 生成實例 ID，並以服務前綴標識，如「IP2CAPI-{GUID:N}」。啟動時註冊，停止時用同一 ID 反註冊。

實施步驟：
1. ID 生成與打印
- 實作細節：Guid.NewGuid():N，轉大寫與前綴。
- 所需資源：C#
- 預估時間：0.1 天
2. 全流程使用
- 實作細節：註冊/反註冊以 ID 為鍵；日誌記錄。
- 所需資源：Service Discovery SDK
- 預估時間：0.3 天

關鍵程式碼/設定：
```csharp
string serviceID = $"IP2CAPI-{Guid.NewGuid():N}".ToUpper();
// 註冊時使用 serviceID；停止時以相同 serviceID 反註冊
```

實際案例：示範程式採用 GUID 實例 ID。
實作環境：同前。
實測數據：
- 改善前：ID 重複/覆蓋風險。
- 改善後：每實例唯一，反註冊對應精準。
- 改善幅度：碰撞風險趨近 0。

Learning Points（學習要點）
核心知識點：
- 實例識別設計
- 命名規則與可觀測性
- 與登錄/下線關聯
技能要求：
- 必備：C#
- 進階：ID 與標籤/Metadata 設計
延伸思考：
- 加上節點/版本/環境標籤
- 風險：過長 ID 與顯示/查詢
- 優化：ID/Name/Tags 分層

Practice Exercise（練習題）
- 基礎：打印實例 ID（30 分）
- 進階：以 ID 完成註冊/下線（2 小時）
- 專案：ID 規範與查詢 API（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：ID 正確生成與使用
- 程式碼品質（30%）：封裝與測試
- 效能優化（20%）：生成成本可忽略
- 創新性（10%）：ID 規範延展性


----------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 10（WaitAny 多事件）
  - Case 11（心跳任務協同）
  - Case 15（關閉緩衝）
  - Case 16（GUID 實例 ID）
- 中級（需要一定基礎）
  - Case 2（啟動序列重排）
  - Case 3（避免重複註冊）
  - Case 4（Console EntryPoint）
  - Case 5（效能對比）
  - Case 6（Controller 載入）
  - Case 12（容器映像）
  - Case 13（跨環境驗證）
  - Case 14（職責轉移）
- 高級（需要深厚經驗）
  - Case 1（Lifecycle 對齊）
  - Case 7（Console 訊號攔截）
  - Case 8（HiddenForm 攔截）
  - Case 9（停機非阻塞策略）

2) 按技術領域分類
- 架構設計類
  - Case 1, 2, 3, 4, 5, 14, 15, 16
- 效能優化類
  - Case 5
- 整合開發類
  - Case 6, 11, 12, 13
- 除錯診斷類
  - Case 7, 8, 9, 10, 13
- 安全防護類
  -（本文未著重安全，相關脈絡在 Case 14 的平台權責）

3) 按學習目標分類
- 概念理解型
  - Case 1, 4, 5, 14
- 技能練習型
  - Case 6, 7, 8, 10, 11, 12, 15, 16
- 問題解決型
  - Case 2, 3, 9, 13
- 創新應用型
  - Case 1, 4, 14（職責重構與平台化）

----------------------------
案例關聯圖（學習路徑建議）

- 建議先學：
  - Case 4（Console EntryPoint、Dockerfile 基礎）
  - Case 12（Self-Host 容器化與 OS 版本匹配）
- 其後學習：
  - Case 1（Lifecycle 對齊的核心思想）
  - Case 2（啟動序列：註冊→心跳→服務）
  - Case 3（避免重複註冊與實例唯一性，含 Case 16）
  - Case 6（Controller 載入問題排除）
- 停機處理（相依 Case 1/2/3）：
  - Case 7（Console 訊號）
  - Case 8（HiddenForm 適配 1709）
  - Case 9（非阻塞策略）
  - Case 10（多事件 WaitAny）
  - Case 15（5 秒緩衝）
- 效能與平台化（平行補強）：
  - Case 5（效能對比）
  - Case 14（IIS 職責轉平台）
- 跨環境驗證與落地：
  - Case 13（Win10/Server/1709/1803 驗證）

完整學習路徑建議：
1) 先掌握容器化 Self-Host 的基本（Case 4 → 12）。
2) 進入核心架構設計與啟動序列（Case 1 → 2 → 3 → 16 → 6）。
3) 深入停機處理與優雅關閉（Case 7 → 8 → 9 → 10 → 15）。
4) 進行效能優化與平台職責重構（Case 5 → 14）。
5) 最後做跨環境驗證與穩定性確認（Case 13）。

此學習路徑由基礎環境與部署開始，逐步走向生命周期治理、錯誤/停機與效能，最終完成跨環境實證，能有效支撐 Windows Container 上 .NET Framework 微服務的工程落地。