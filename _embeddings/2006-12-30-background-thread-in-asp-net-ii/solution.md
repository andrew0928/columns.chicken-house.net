以下案例均圍繞文中同一主題「在 ASP.NET（IIS）環境中執行背景工作（background thread）」，將作者觀察的兩個關鍵問題（App Pool 空閒逾時導致背景執行緒終止、w3wp.exe 因例外停止）擴展為可教學、可實作的完整解決方案集。說明中的「實測數據」若非出自原文觀察（例如 20 分鐘即停、調整設定後跑了數小時），均以教學示意為主，實務請自行量測。

## Case #1: Idle Timeout 導致背景執行緒於 20 分鐘後被終止

### Problem Statement（問題陳述）
業務場景：團隊在 ASP.NET 應用程式中啟動一個長時間背景工作（例如每隔數秒寫入 log 或執行資料同步），晚上讓它自動跑。回來後發現 log 只記錄了約 20 分鐘就停止，背景工作悄悄消失，導致夜間任務未完成，隔天早上資料不同步，影響後續批量報表與對外 SLA 交付。
技術挑戰：IIS Application Pool 在無請求時會觸發 Idle Timeout，回收 w3wp.exe 或卸載 AppDomain，ASP.NET 中自行開的背景執行緒為 background thread，不會阻止程序結束，因此會被終止。
影響範圍：長任務中斷、資料不一致、重工與延遲、夜間任務無法完成。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. IIS Application Pool Idle Timeout 預設 20 分鐘，無請求即回收工作程序。
2. 背景執行緒未綁定生命週期，不會讓工作程序存活。
3. 沒有任務續跑或自動恢復設計，回收後工作直接消失。
深層原因：
- 架構層面：將長任務放在 ASP.NET 網站進程內，與網站請求同生命週期。
- 技術層面：使用 Thread/ThreadPool 而未處理 AppDomain 卸載與回收情境。
- 流程層面：缺少對 IIS App Pool 的運維設定與夜間行為監控流程。

### Solution Design（解決方案設計）
解決策略：調整 Application Pool Idle Timeout/Always On，讓進程不會因無請求而回收；同時建立背景工作的生命週期管理與心跳監控，確保即便發生回收也能偵測、告警與恢復。短期用設定解堵，長期應評估是否遷出至獨立背景工作服務。

實施步驟：
1. 停用或延長 Idle Timeout
- 實作細節：將 Idle Timeout 設為 0（停用）或大於任務時間；IIS 8+ 可開啟 AlwaysOn。
- 所需資源：IIS 管理工具、PowerShell 或 appcmd。
- 預估時間：0.5 小時。

2. 啟用心跳與告警
- 實作細節：每分鐘寫入心跳（檔案/DB），延遲超過閾值發送告警。
- 所需資源：Logging 套件（Serilog/NLog/ETW）、監控平台。
- 預估時間：1-2 小時。

3. 設定 Overlapped Recycling 與預熱
- 實作細節：確保回收時新舊進程重疊啟動，並加上應用預熱/保活。
- 所需資源：IIS 設定、warm-up job。
- 預估時間：1 小時。

關鍵程式碼/設定：
```powershell
# PowerShell (IIS 8+)
Import-Module WebAdministration
$appPool = "MyAppPool"
Set-ItemProperty "IIS:\AppPools\$appPool" -Name processModel.idleTimeout -Value ([TimeSpan]::Zero)  # 停用 Idle Timeout
Set-ItemProperty "IIS:\Sites\MySite" -Name applicationDefaults.preloadEnabled -Value True           # 啟用預載
```
```csharp
// 心跳寫入（每分鐘）
var timer = new System.Threading.Timer(_ => File.AppendAllText(@"D:\logs\heartbeat.log", DateTime.UtcNow + Environment.NewLine),
                                       null, TimeSpan.Zero, TimeSpan.FromMinutes(1));
```

實際案例：文中觀察到「20 分鐘內無新 request 即停」，調整 App Pool 設定後可「跑了幾個小時」。
實作環境：Windows Server 2003/IIS 6（2003 AppPool 畫面）、.NET 2.0 可能環境。
實測數據：
改善前：背景工作最多存活 20 分鐘。
改善後：持續數小時以上（至少超過 120 分鐘）。
改善幅度：至少 6x 以上（依實際時長而定）。

Learning Points（學習要點）
核心知識點：
- IIS Application Pool Idle Timeout 對進程/背景執行緒的影響
- ASP.NET 背景執行緒為 background thread，不會維持進程存活
- 基本的保活（預載、warm-up）與監控設計

技能要求：
必備技能：IIS 管理、基本 C# Threading、基礎監控/日志。
進階技能：自動化配置（PowerShell）、預熱腳本設計。

延伸思考：
- 可否以 Windows Service/Job 系統承載長任務？
- 停用 Idle Timeout 有資源消耗風險（閒置時仍佔用記憶體/CPU）。
- 後續可加入自我恢復與任務續跑機制。

Practice Exercise（練習題）
基礎練習：將 Idle Timeout 設為 0 並加入心跳檔案寫入，觀察 2 小時（30 分鐘）。
進階練習：實作預熱與 overlapped recycling，記錄回收前後心跳不中斷（2 小時）。
專案練習：建立簡易儀表板顯示心跳延遲並發送告警（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：Idle Timeout 設定生效、心跳與告警可用
程式碼品質（30%）：可測試、錯誤處理、日誌結構化
效能優化（20%）：低資源占用、無多餘輪詢
創新性（10%）：自動恢復或視覺化監控


## Case #2: 背景執行緒未攔截例外導致 w3wp.exe 停止

### Problem Statement（問題陳述）
業務場景：調整 Idle Timeout 後背景任務可連續執行數小時，但半夜某時刻 w3wp.exe 又停止，背景工作被迫終止。團隊推測是背景執行緒未處理的例外導致工作程序崩潰，造成中斷與資料不一致。
技術挑戰：在 .NET 2.0 起，非 UI 執行緒上的未處理例外可能終止整個 AppDomain/進程；在 ASP.NET 內，未處理例外也會影響 w3wp 稳定性。需確保背景工作所有路徑都能攔截並記錄例外。
影響範圍：進程中止、服務不可用、任務中斷、資料不一致、SLA 風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 背景工作主迴圈缺乏 try/catch 封鎖，例外未被攔截。
2. 未訂閱 AppDomain.UnhandledException/TaskScheduler.UnobservedTaskException。
3. 無集中式日誌/告警，例外發生時無情報。
深層原因：
- 架構層面：未建立統一錯誤處理與恢復策略。
- 技術層面：對 .NET 非同步/執行緒例外行為認知不足。
- 流程層面：缺少夜間運維與故障通報流程。

### Solution Design（解決方案設計）
解決策略：多層次例外攔截與記錄，主迴圈強制 try/catch；註冊 AppDomain 與 Task 的全域事件，確保記錄堆疊與上下文；搭配健康探測與重啟策略，避免單次例外造成長時間停擺。

實施步驟：
1. 主迴圈例外攔截
- 實作細節：封鎖 while(true) 工作回合，將所有子步驟包入 try/catch，避免冒泡到 process。
- 所需資源：C#。
- 預估時間：0.5 小時。

2. 全域例外事件
- 實作細節：訂閱 AppDomain.CurrentDomain.UnhandledException 與 TaskScheduler.UnobservedTaskException，記錄堆疊與上下文。
- 所需資源：Logging 工具。
- 預估時間：1 小時。

3. 健康檢查與自我復原
- 實作細節：例外次數超閾值時觸發自我重啟或通知。
- 所需資源：監控/告警系統。
- 預估時間：2 小時。

關鍵程式碼/設定：
```csharp
// 全域例外攔截
AppDomain.CurrentDomain.UnhandledException += (s, e) =>
{
    LogFatal("UnhandledException", (Exception)e.ExceptionObject);
};
TaskScheduler.UnobservedTaskException += (s, e) =>
{
    LogError("UnobservedTaskException", e.Exception);
    e.SetObserved();
};

// 主迴圈包裹
void WorkLoop(CancellationToken token)
{
    while (!token.IsCancellationRequested)
    {
        try
        {
            DoOneRound(); // 真正工作
        }
        catch (ThreadAbortException) { /* AppDomain unload, 應該儲存進度後退出 */ }
        catch (Exception ex)
        {
            LogError("WorkLoop", ex);
            Thread.Sleep(TimeSpan.FromSeconds(5)); // 退避避免打爆資源
        }
    }
}
```

實際案例：文中提到「IIS w3wp.exe 又停了」，作者準備處理 exception handling。
實作環境：IIS 6/7 + .NET 2.0/3.5 時代常見。
實測數據（教學示意）：
改善前：夜間 1 次未攔截例外即中止進程。
改善後：例外被捕捉並記錄，進程持續運行 ≥ 24 小時。
改善幅度：非預期停擺次數由每天 ≥1 次降為 0。

Learning Points（學習要點）
核心知識點：
- .NET 中未處理例外對 AppDomain/進程的影響
- 多層次例外處理（主迴圈 + 全域）
- 錯誤後退避與健康檢查

技能要求：
必備技能：C# 例外處理、日誌。
進階技能：故障注入測試、穩定性工程。

延伸思考：
- 是否需將致命錯誤視為「快速失敗 + 快速恢復」？
- 記錄 PII 資料的合規風險。
- 是否需要 Crash Dump 來根因分析？

Practice Exercise（練習題）
基礎練習：為主迴圈加上 try/catch 並寫入結構化日誌（30 分）。
進階練習：實作全域攔截與退避策略（2 小時）。
專案練習：加入健康檢查端點與自動重啟/告警（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：例外被攔截與記錄
程式碼品質（30%）：清晰結構、可測試
效能優化（20%）：退避策略不造成自旋
創新性（10%）：自我修復與可視化


## Case #3: 使用 IRegisteredObject 安全關閉與生命週期綁定

### Problem Statement（問題陳述）
業務場景：背景工作在 ASP.NET 進程內執行，當 Application Pool 回收或 AppDomain 卸載時若直接中止，可能出現資料損壞或重複處理。需要在關閉前保存進度、停止排程並釋放資源。
技術挑戰：ASP.NET 進程關閉與 AppDomain 卸載並非同步發生，ThreadAbortException 可能在任務中段丟出，需有可被主機叫停的機制。
影響範圍：資料完整性、併發一致性、外部系統狀態錯亂。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 背景工作未與 HostingEnvironment 綁定生命週期。
2. 無取消與停機鉤子，AppDomain 卸載時直接中止。
3. 無狀態保存/檢查點。
深層原因：
- 架構層面：缺乏服務化與生命週期抽象。
- 技術層面：未使用 IRegisteredObject 等 ASP.NET 提供的 hosting API。
- 流程層面：未定義安全停機流程。

### Solution Design（解決方案設計）
解決策略：以 IRegisteredObject 實作背景服務，註冊到 HostingEnvironment，於 Stop() 中接收取消通知，停止新任務、保存進度並釋放資源；搭配 CancellationToken 控制主迴圈，避免暴力中止。

實施步驟：
1. 建立 IRegisteredObject 實作
- 實作細節：Register/Unregister、Stop() 中取消 token、等待收尾。
- 所需資源：.NET Framework。
- 預估時間：1 小時。

2. 啟動與註冊
- 實作細節：在 Application_Start 或啟動程式碼中建立服務實例並註冊。
- 所需資源：Global.asax 或 OWIN 啟動。
- 預估時間：0.5 小時。

3. 狀態檢查點
- 實作細節：關閉前將最後處理 offset/游標落地。
- 所需資源：資料庫或檔案。
- 預估時間：1-2 小時。

關鍵程式碼/設定：
```csharp
public sealed class BackgroundService : IRegisteredObject
{
    private readonly CancellationTokenSource _cts = new();
    private Task _loopTask;

    public void Start()
    {
        HostingEnvironment.RegisterObject(this);
        _loopTask = Task.Run(() => LoopAsync(_cts.Token));
    }

    public void Stop(bool immediate)
    {
        _cts.Cancel(); // 通知停止
        try { _loopTask?.Wait(TimeSpan.FromSeconds(30)); } catch {}
        // TODO: 儲存檢查點與清理資源
        HostingEnvironment.UnregisterObject(this);
    }

    private async Task LoopAsync(CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            try { await DoOneRoundAsync(token); }
            catch (OperationCanceledException) { /* 正常關閉 */ }
            catch (Exception ex) { LogError("Loop", ex); await Task.Delay(5000, token); }
        }
    }
}
```

實際案例：對應文中「application unload 就不見去了」的治理手段。
實作環境：ASP.NET（.NET 2.0+ 提供 HostingEnvironment API）。
實測數據（教學示意）：
改善前：回收時任務被中止，資料重複/遺失。
改善後：回收前完成收尾與保存，零資料損壞。
改善幅度：資料不一致事件由偶發降至 0。

Learning Points（學習要點）
核心知識點：
- IRegisteredObject 與 ASP.NET Host 生命週期
- CancellationToken 的正確用法
- 檢查點/續跑概念

技能要求：
必備技能：非同步程式設計、Token 取消模型。
進階技能：可靠的收尾與超時控制。

延伸思考：
- 需要多執行緒時如何安全停止？
- 碰到資料庫交易時的收尾策略？

Practice Exercise（練習題）
基礎練習：用 IRegisteredObject 包裝一個每 5 秒工作的背景服務（30 分）。
進階練習：加入檢查點，驗證回收後可從中斷點續跑（2 小時）。
專案練習：多工背景任務 + 安全停機 + 儀表板（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：可正常啟停、不中斷資料
程式碼品質（30%）：清晰、可測
效能優化（20%）：關閉等待不阻塞
創新性（10%）：可視化停機流程


## Case #4: 週期性回收與排程對齊（Overlapped Recycling）

### Problem Statement（問題陳述）
業務場景：IIS 為了穩定性，常設定固定時間回收（例如每日凌晨 3 點）。若背景任務在該時段執行，將被中斷或重複處理。需要讓回收與任務避開衝突，並確保回收過程不中斷服務。
技術挑戰：掌握 overlapped recycling、預熱與排程的搭配，確保回收時仍有存活進程提供服務，背景任務可安全停機。
影響範圍：夜間任務穩定性與網站可用性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 週期回收時間與任務執行時間衝突。
2. 未啟用 overlapped recycling 或預熱。
3. 任務無安全停機流程。
深層原因：
- 架構層面：未用任務對齊回收窗口。
- 技術層面：對 IIS 回收選項理解不足。
- 流程層面：無變更視窗制度。

### Solution Design（解決方案設計）
解決策略：調整回收時段避開任務；啟用 overlapped recycling 與預熱；在回收前後以健康探針驗證服務不中斷，同時利用 IRegisteredObject 做安全停機。

實施步驟：
1. 調整回收排程
- 實作細節：改到流量最低且避開任務窗口，或關閉固定回收。
- 所需資源：IIS 管理工具。
- 預估時間：0.5 小時。

2. 啟用 overlapped recycling 與預熱
- 實作細節：讓新進程先啟動、熱身完成後再卸舊進程。
- 所需資源：IIS 設定、warm-up URL。
- 預估時間：1 小時。

3. 任務避讓與停機
- 實作細節：回收前暫停新任務、等待當前回合完成。
- 所需資源：IRegisteredObject。
- 預估時間：1 小時。

關鍵程式碼/設定：
```cmd
:: appcmd（IIS 7+）
appcmd set apppool /apppool.name:"MyAppPool" /recycling.periodicRestart.time:00:00:00  :: 關閉固定回收
appcmd set apppool /apppool.name:"MyAppPool" /startMode:AlwaysRunning              :: 需搭配 Application Initialization
```

實際案例：與文中「跑了幾個小時」後又停，常見原因之一為週期回收衝突。
實作環境：IIS 7+。
實測數據（教學示意）：
改善前：每日任務中斷 1 次。
改善後：0 中斷，SLA 達成。
改善幅度：中斷次數由 1/天 降為 0。

Learning Points（學習要點）
核心知識點：
- Overlapped Recycling 與預熱
- 回收窗口與任務排程對齊
- 安全停機策略

技能要求：
必備技能：IIS 管理。
進階技能：流量分析與回收策略設計。

延伸思考：
- 多台機器與負載平衡時如何序列化回收？
- 與部署窗口整合。

Practice Exercise（練習題）
基礎練習：配置 overlapped recycling 並驗證熱身（30 分）。
進階練習：將任務與回收窗口避開（2 小時）。
專案練習：實作回收預檢與停機儀表板（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：回收不中斷服務
程式碼品質（30%）：配置與自動化腳本清晰
效能優化（20%）：熱身時間合理
創新性（10%）：智能排程避讓


## Case #5: 以 Keep-Alive/Warm-up 防止空閒回收

### Problem Statement（問題陳述）
業務場景：無法停用 Idle Timeout 或需節能，但夜間仍有背景任務。希望在無用戶請求時，以輕量保活請求讓應用保持活著，避免 App Pool 被回收。
技術挑戰：需要低負載且安全的保活策略，不影響安全並避免外部濫用。
影響範圍：夜間任務穩定性、資源利用率、安全。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Idle Timeout 啟用導致空閒回收。
2. 無內部流量讓應用存活。
3. 保活端點未設計可能帶來安全風險。
深層原因：
- 架構層面：背景任務依賴 Web 進程存活。
- 技術層面：未啟用預載/AlwaysOn。
- 流程層面：無保活檢查與告警。

### Solution Design（解決方案設計）
解決策略：建立只回傳 200 的健康端點並受限於內網/IP 白名單；用排程（Windows Task Scheduler）或監控系統每 5 分鐘 ping 一次；結合預載可減少首次冷啟代價。

實施步驟：
1. 新增健康端點
- 實作細節：/health 返回簡單 JSON，加入授權/白名單與快取控制。
- 所需資源：Web API。
- 預估時間：0.5 小時。

2. 建置保活排程
- 實作細節：Windows Task Scheduler/curl 定時呼叫。
- 所需資源：Windows 伺服器。
- 預估時間：0.5 小時。

3. 監控與告警
- 實作細節：連續失敗 N 次觸發通知。
- 所需資源：監控平台。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 簡易健康端點（需加保護）
[Authorize] // 或內網 IP 限制
public IHttpActionResult Health() => Ok(new { status = "ok", time = DateTime.UtcNow });
```
```cmd
:: Windows 排程動作
curl -fsS https://yourapp/health >NUL 2>&1
```

實際案例：用於避免 20 分鐘無流量導致回收的保活替代方案。
實作環境：IIS 任意版本。
實測數據（教學示意）：
改善前：20 分鐘無請求被回收。
改善後：保活每 5 分鐘一次，進程持續。
改善幅度：夜間中斷由頻繁降至 0。

Learning Points（學習要點）
核心知識點：
- Keep-Alive 與安全（授權/白名單）
- Health Check 設計
- 預載/冷啟成本

技能要求：
必備技能：基本 Web API。
進階技能：網路安全控管。

延伸思考：
- Azure App Service 可用 Always On 替代。
- 濫用風險與頻率控制。

Practice Exercise（練習題）
基礎練習：新增健康端點並用 curl 保活（30 分）。
進階練習：加入 IP 白名單與速率限制（2 小時）。
專案練習：將保活整合監控告警（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：端點可用、保活成功
程式碼品質（30%）：安全保護、清晰
效能優化（20%）：低負載
創新性（10%）：與監控整合


## Case #6: 使用 QueueBackgroundWorkItem（QBWI）綁定應用生命週期

### Problem Statement（問題陳述）
業務場景：希望在 ASP.NET 內啟動短中長度的背景工作，且在 AppDomain 卸載時能獲得取消通知並安全結束，避免資料損壞。
技術挑戰：Thread/Task.Run 無法直接與 Host 生命週期協作，需要框架提供的隊列 API。
影響範圍：安全停機、穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 Thread/Task 無法自動獲得停機取消。
2. 無統一的工作佇列與取消 Token。
3. 缺少回收相容設計。
深層原因：
- 架構層面：背景工作生命週期管理不足。
- 技術層面：未使用 QBWI。
- 流程層面：未規範背景工作提交方式。

### Solution Design（解決方案設計）
解決策略：在 .NET 4.5.2+ 使用 HostingEnvironment.QueueBackgroundWorkItem 提交背景工作，框架會在 AppDomain 卸載時提供取消 Token，配合正確的取消與收尾，可安全結束。

實施步驟：
1. 封裝提交 API
- 實作細節：建立 BackgroundWorkQueue 包裝 QBWI，統一提交入口。
- 所需資源：.NET 4.5.2+。
- 預估時間：1 小時。

2. 實作可取消工作
- 實作細節：所有回合接收 CancellationToken，支援 OCE。
- 所需資源：C# async。
- 預估時間：1-2 小時。

關鍵程式碼/設定：
```csharp
public static class BgQueue
{
    public static void Queue(Func<CancellationToken, Task> work)
    {
        HostingEnvironment.QueueBackgroundWorkItem(ct => work(ct));
    }
}

// 使用
BgQueue.Queue(async ct =>
{
    while (!ct.IsCancellationRequested)
    {
        await DoOneRoundAsync(ct);
        await Task.Delay(1000, ct);
    }
});
```

實際案例：作為 IRegisteredObject 的替代/補充。
實作環境：ASP.NET 4.5.2+。
實測數據（教學示意）：
改善前：回收時暴力終止。
改善後：收到取消，安全結束。
改善幅度：資料不一致機率降至趨近 0。

Learning Points（學習要點）
核心知識點：
- QBWI 使用時機與限制（非無限長工、數量受限）
- 取消模型與 OCE
- 背景工作設計模式

技能要求：
必備技能：async/await。
進階技能：佇列抽象與封裝。

延伸思考：
- 長任務仍建議遷出至外部 Worker。
- QBWI 數量限制下的退避與排空策略。

Practice Exercise（練習題）
基礎練習：以 QBWI 排一個可取消工作（30 分）。
進階練習：封裝提交介面與重試策略（2 小時）。
專案練習：建立小型任務中心（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：可提交/取消
程式碼品質（30%）：抽象清晰
效能優化（20%）：避免自旋
創新性（10%）：重試/退避設計


## Case #7: 將長任務遷出至 Windows Service（或外部 Worker）

### Problem Statement（問題陳述）
業務場景：背景任務需長時間穩定執行（數小時～常駐），且不應受 Web 請求/回收影響。現有 ASP.NET 內執行的做法風險高、難維運。
技術挑戰：需要建立獨立常駐服務，與 Web 應用透過資料庫/佇列交互，提供高可用與監控。
影響範圍：穩定性、擴展性、SLA。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. IIS 會回收，ASP.NET 不適合常駐長任務。
2. 背景執行緒與 Web 請求競爭資源。
3. 缺少任務持久化與重試。
深層原因：
- 架構層面：未做職責拆分（Web vs Worker）。
- 技術層面：缺乏常駐服務與部署能力。
- 流程層面：運維未分離。

### Solution Design（解決方案設計）
解決策略：建立 Windows Service 或容器化 Worker，將任務與網站解耦，透過資料庫/訊息佇列（SQL/MSMQ/RabbitMQ/Azure Queue）傳遞工作與狀態，擁有獨立部署、監控與縮放能力。

實施步驟：
1. 設計工作佇列與狀態表
- 實作細節：Jobs、JobRuns、Retries，狀態機。
- 所需資源：資料庫/訊息佇列。
- 預估時間：1-2 天。

2. 建立 Windows Service/Worker
- 實作細節：ServiceBase 或 .NET Worker Service，處理工作、重試、退避。
- 所需資源：.NET、部署管線。
- 預估時間：1-2 天。

3. 監控與告警
- 實作細節：心跳、失敗率、處理延遲。
- 所需資源：APM/監控系統。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
// .NET Worker Service (Generic Host)
public class Worker : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var job = await DequeueAsync(stoppingToken);
            try { await ProcessAsync(job, stoppingToken); }
            catch (Exception ex) { await RecordFailureAsync(job, ex); }
        }
    }
}
```

實際案例：避免文中 Idle/回收/例外造成的中斷。
實作環境：Windows Service 或容器化環境。
實測數據（教學示意）：
改善前：夜間任務中斷頻繁。
改善後：任務 24x7 穩定，無關 Web 流量。
改善幅度：SLA 達成率顯著提升。

Learning Points（學習要點）
核心知識點：
- Web/Worker 解耦
- 佇列/重試/退避
- 監控與可觀測性

技能要求：
必備技能：.NET 服務開發、資料庫設計。
進階技能：訊息佇列、中介軟體。

延伸思考：
- 容器與水平擴充
- 任務去重與鎖競

Practice Exercise（練習題）
基礎練習：建立最小 Worker 從表格取任務（30 分）。
進階練習：加入重試與退避（2 小時）。
專案練習：完整任務中心 + 儀表板（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：任務處理/重試
程式碼品質（30%）：模組化、可測
效能優化（20%）：佇列吞吐
創新性（10%）：可視化監控


## Case #8: 使用 Hangfire 在 Web 中安全執行持久化背景工作

### Problem Statement（問題陳述）
業務場景：需要任務排程、重試、儀表板與持久化，仍希望簡化部署且沿用現有 Web 專案。
技術挑戰：自行開發任務中心成本高，需採用成熟框架。
影響範圍：維運效率、可靠性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 自製背景框架成本高、風險大。
2. 缺少儀表板與持久化。
3. 例外與回收場景處理不足。
深層原因：
- 架構層面：需要可觀測與持久化的任務系統。
- 技術層面：未導入現成框架。
- 流程層面：無統一任務管理。

### Solution Design（解決方案設計）
解決策略：導入 Hangfire（SQL 持久化），使用 Dashboard 管理任務，內建重試/退避，與 ASP.NET 整合；生產環境建議分離進程或使用 Hangfire Server 專用節點。

實施步驟：
1. 安裝與配置
- 實作細節：安裝 Hangfire.Core/SqlServer，啟用儀表板與 Server。
- 所需資源：SQL Server。
- 預估時間：2 小時。

2. 定義任務與排程
- 實作細節：RecurringJob/BackgroundJob API。
- 所需資源：C#。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
GlobalConfiguration.Configuration.UseSqlServerStorage("DefaultConnection");
app.UseHangfireDashboard("/hangfire"); 
app.UseHangfireServer();

RecurringJob.AddOrUpdate("nightly-sync", () => DoSync(), Cron.Daily(2, 0)); // 每日 2:00
```

實際案例：取代手寫 Thread 模式，降低回收/例外風險。
實作環境：ASP.NET/OWIN。
實測數據（教學示意）：
改善前：任務中斷、無持久化。
改善後：任務持久化與可視化，重試自動化。
改善幅度：失敗任務遺失率降為 0。

Learning Points（學習要點）
核心知識點：
- 任務持久化與重試
- 儀表板監控
- 與 Web 解耦部署

技能要求：
必備技能：NuGet/SQL。
進階技能：多節點部署。

延伸思考：
- 與分散式鎖搭配避免多活。
- 安全保護儀表板。

Practice Exercise（練習題）
基礎練習：建立一個 Recurring Job（30 分）。
進階練習：失敗重試與告警（2 小時）。
專案練習：Hangfire + 多節點 + 儀表板（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：任務/排程/重試
程式碼品質（30%）：設計清晰
效能優化（20%）：佇列配置
創新性（10%）：儀表板擴充


## Case #9: 使用 Quartz.NET 實作可持久化的排程與關閉

### Problem Statement（問題陳述）
業務場景：需要複雜排程（Cron、Misfire 設定）與持久化，並控制關閉時安全結束任務。
技術挑戰：自行排程器難度高，需導入 Quartz.NET。
影響範圍：可靠性、功能性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 自製排程器不可靠。
2. 任務狀態未持久化。
3. 關閉時無安全機制。
深層原因：
- 架構層面：排程與任務需要框架化。
- 技術層面：無 Quartz.NET。
- 流程層面：部署與回收未考慮排程器。

### Solution Design（解決方案設計）
解決策略：導入 Quartz.NET + ADO.NET Store，配置 Misfire 與 ShutdownHook，確保回收時 broker 停止調度，執行中的任務可控地結束。

實施步驟：
1. 安裝與配置
- 實作細節：Quartz + ADO.NET Store、連線設定。
- 所需資源：DB。
- 預估時間：2 小時。

2. 任務與關閉處理
- 實作細節：IJob 實作、IScheduler.Shutdown(waitForJobsToComplete: true)。
- 所需資源：C#。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
var props = new NameValueCollection {
  ["quartz.scheduler.instanceName"] = "MyScheduler",
  ["quartz.jobStore.type"] = "Quartz.Impl.AdoJobStore.JobStoreTX, Quartz",
  ["quartz.jobStore.driverDelegateType"] = "Quartz.Impl.AdoJobStore.SqlServerDelegate, Quartz",
  ["quartz.jobStore.tablePrefix"] = "QRTZ_",
  ["quartz.jobStore.dataSource"] = "default",
  ["quartz.dataSource.default.connectionString"] = "...",
  ["quartz.threadPool.threadCount"] = "3"
};
var schedulerFactory = new StdSchedulerFactory(props);
var scheduler = await schedulerFactory.GetScheduler();
await scheduler.Start();
// 關閉
await scheduler.Shutdown(waitForJobsToComplete: true);
```

實際案例：替代 Thread 直跑，降低中斷。
實作環境：.NET Framework。
實測數據（教學示意）：
改善前：任務錯過/中斷。
改善後：持久化/安全關閉。
改善幅度：排程成功率達 99.9%+。

Learning Points（學習要點）
核心知識點：
- Misfire 策略
- 安全關閉
- 持久化 Store

技能要求：
必備技能：Quartz 使用。
進階技能：叢集模式。

延伸思考：
- 多機叢集 + 分散式鎖。
- 任務隔離與租戶化。

Practice Exercise（練習題）
基礎練習：Cron 任務與 Misfire 設定（30 分）。
進階練習：Shutdown 等待任務完成（2 小時）。
專案練習：Quartz 持久化 + 儀表板（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：排程/持久化/關閉
程式碼品質（30%）：配置清晰
效能優化（20%）：執行緒池調優
創新性（10%）：監控擴展


## Case #10: 心跳監控與早期告警（含安全防護）

### Problem Statement（問題陳述）
業務場景：背景任務曾因 20 分鐘空閒回收或例外停止，需要建立「早發現、早處理」的心跳監控與告警機制，並確保監控端點不被濫用。
技術挑戰：心跳過於頻繁會增加負載；監控端點若未保護，可能成為攻擊面。
影響範圍：可用性、安全性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無心跳，停擺無法即時得知。
2. 監控端點未授權或缺少速率限制。
3. 告警鏈路缺失。
深層原因：
- 架構層面：可觀測性不足。
- 技術層面：未設計安全監控端點。
- 流程層面：無 24x7 值守告警流程。

### Solution Design（解決方案設計）
解決策略：背景任務每分鐘上報心跳；監控系統拉取或被動接收；端點加上授權/IP 白名單/速率限制；告警策略基於延遲/失敗次數。將心跳與任務健康（失敗率/延遲）結合。

實施步驟：
1. 實作心跳與任務統計
- 實作細節：DB/檔案記錄，包含 LastSeen、LastJobLag。
- 所需資源：Log/DB。
- 預估時間：1 小時。

2. 監控與告警
- 實作細節：Prometheus/ELK/Azure Monitor。
- 所需資源：監控平台。
- 預估時間：2 小時。

3. 端點安全
- 實作細節：Auth、IP 白名單、速率限制。
- 所需資源：反向代理/WAF。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 心跳更新
await db.ExecuteAsync("UPDATE Worker SET LastSeen=@utcNow", new { utcNow = DateTime.UtcNow });

// 安全端點（示例）
[Authorize(Roles="Monitor")]
[HttpGet, Route("health/worker")]
public IHttpActionResult WorkerHealth() => Ok(new { lastSeenUtc = GetLastSeen() });
```

實際案例：輔助文中問題的早期偵測。
實作環境：任意。
實測數據（教學示意）：
改善前：停擺發生後隔日才察覺。
改善後：3 分鐘內告警。
改善幅度：MTTD 從小時級降至分鐘級。

Learning Points（學習要點）
核心知識點：
- 可觀測性指標設計
- 端點安全
- 告警疲勞與閾值設計

技能要求：
必備技能：日誌/監控。
進階技能：WAF/反向代理策略。

延伸思考：
- 服務等級目標（SLO）與告警門檻。
- 異常噪音抑制。

Practice Exercise（練習題）
基礎練習：新增心跳記錄（30 分）。
進階練習：監控面板與告警（2 小時）。
專案練習：整體 SLO 儀表板（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：心跳/告警有效
程式碼品質（30%）：安全可維護
效能優化（20%）：低負載
創新性（10%）：可視化與預測


## Case #11: 以 DebugDiag/Crash Dump 追查 w3wp 停止根因

### Problem Statement（問題陳述）
業務場景：w3wp.exe 夜間停止但日誌不足，需抓取當下狀態（Dump）分析是否為未攔截例外、Access Violation 或外部模組導致。
技術挑戰：Dump 設置、收集與分析門檻高，需要標準化流程。
影響範圍：根因分析效率與修復速度。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 未取得當下執行緒堆疊。
2. 無 Crash/Exception 規則。
3. 缺少分析工具與技巧。
深層原因：
- 架構層面：觀測性不足。
- 技術層面：不熟 Dump 工具。
- 流程層面：無故障處置手冊。

### Solution Design（解決方案設計）
解決策略：使用 DebugDiag 或 ProcDump 設定規則（Unhandled Exception/Crash）；產生 Dump；使用 WinDbg/DebugDiag 分析報告，找出崩潰執行緒與例外堆疊，定位問題元件。

實施步驟：
1. 部署 DebugDiag/ProcDump
- 實作細節：針對 w3wp 設 Crash 規則。
- 所需資源：系統管理權限。
- 預估時間：1 小時。

2. 收集與分析
- 實作細節：產生 Dump，使用分析模板。
- 所需資源：WinDbg/DebugDiag。
- 預估時間：2 小時。

關鍵程式碼/設定：
```cmd
:: ProcDump 例：未處理例外產生 Dump
procdump -e -ma w3wp.exe c:\dumps
```

實際案例：支援文中「w3wp.exe 又停了」的根因追查。
實作環境：Windows/IIS。
實測數據（教學示意）：
改善前：無法定位崩潰原因。
改善後：可定位到來源方法/模組。
改善幅度：修復週期由數天降至數小時。

Learning Points（學習要點）
核心知識點：
- Crash/Exception Dump
- 執行緒堆疊分析
- 工具鏈 DebugDiag/WinDbg

技能要求：
必備技能：基本系統管理。
進階技能：Dump 讀取與分析。

延伸思考：
- 線上 Dump 的磁碟與隱私風險。
- 自動清理策略。

Practice Exercise（練習題）
基礎練習：安裝 ProcDump 並設規則（30 分）。
進階練習：分析模擬崩潰 Dump（2 小時）。
專案練習：建立故障處理 runbook（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：可產生與分析 Dump
程式碼品質（30%）：處置手冊清晰
效能優化（20%）：最小干擾
創新性（10%）：自動化收集


## Case #12: 多實例/多進程下的重複執行與分布式鎖

### Problem Statement（問題陳述）
業務場景：網站有多台機器或 Web Garden，背景任務可能被多個實例同時執行，造成重複處理或競爭條件。
技術挑戰：需要全域鎖或租約機制，確保同一任務在同時間僅一個持有者。
影響範圍：資料一致性、外部 API 限額。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多實例同時啟動相同任務。
2. 缺少分散式鎖。
3. 無持續租約續租機制。
深層原因：
- 架構層面：未設計單例執行策略。
- 技術層面：對分散式協定不了解。
- 流程層面：部署擴展未考慮任務單例性。

### Solution Design（解決方案設計）
解決策略：使用 SQL 鎖（sp_getapplock）或鎖表 + 唯一索引，或用 Redis 分布式鎖（RedLock），保證單實例執行；加上租約到期續租與失效回收。

實施步驟：
1. 選擇鎖方案
- 實作細節：SQL/Redis，視環境決定。
- 所需資源：DB/Redis。
- 預估時間：1 小時。

2. 實作鎖與租約
- 實作細節：獲鎖才執行；定期續租；失敗釋放。
- 所需資源：C#。
- 預估時間：2 小時。

關鍵程式碼/設定：
```csharp
// SQL 單例執行（簡化）
using var conn = new SqlConnection(cs);
await conn.OpenAsync();
using var cmd = new SqlCommand("EXEC sp_getapplock @Resource, 'Exclusive', 'Session', 60000", conn);
cmd.Parameters.AddWithValue("@Resource", "job:nightly");
var rc = (int)await cmd.ExecuteScalarAsync();
if (rc < 0) return; // 未取鎖，不執行
try { await DoJobAsync(); }
finally { await new SqlCommand("EXEC sp_releaseapplock @Resource", conn)
                    { Parameters = { new("@Resource", "job:nightly") } }.ExecuteNonQueryAsync(); }
```

實際案例：避免「跑了幾個小時」後多進程重複執行的風險。
實作環境：多台 Web/IIS。
實測數據（教學示意）：
改善前：重複執行率 > 10%。
改善後：重複執行率 ~ 0%。
改善幅度：一致性問題消失。

Learning Points（學習要點）
核心知識點：
- 分散式鎖原理與陷阱
- 鎖租約與續租
- 故障恢復

技能要求：
必備技能：資料庫/Redis 操作。
進階技能：分散式一致性。

延伸思考：
- 網路分區與鎖誤判。
- 任務冪等性設計。

Practice Exercise（練習題）
基礎練習：SQL 單例任務（30 分）。
進階練習：加入續租與超時（2 小時）。
專案練習：分散式鎖封裝庫（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：單例保證
程式碼品質（30%）：清晰可靠
效能優化（20%）：低延遲鎖
創新性（10%）：租約策略


## Case #13: ThreadAbortException 與檢查點續跑

### Problem Statement（問題陳述）
業務場景：AppDomain 卸載或回收時，執行緒可能收到 ThreadAbortException，若未正確處理，將導致資料遺失或重複。需要設計檢查點機制。
技術挑戰：在不影響效能下頻繁保存進度、並於重啟後從最近進度點繼續。
影響範圍：資料完整性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無檢查點保存。
2. 未捕捉 ThreadAbortException。
3. 回收時暴力中止。
深層原因：
- 架構層面：缺少可恢復流程。
- 技術層面：不熟異常語意。
- 流程層面：未演練中斷恢復。

### Solution Design（解決方案設計）
解決策略：在處理批次時定期保存 offset/游標；捕捉 ThreadAbortException 後落地最後安全點；重啟後從檢查點繼續；配合 IRegisteredObject/QBWI 盡量避免暴力中止。

實施步驟：
1. 設計檢查點資料結構
- 實作細節：表格儲存 last_id / last_timestamp。
- 所需資源：DB。
- 預估時間：1 小時。

2. 插入保存點
- 實作細節：每 N 筆/每 T 秒保存。
- 所需資源：C#。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
try
{
    foreach (var item in Batch())
    {
        Process(item);
        if (++count % 100 == 0) SaveCheckpoint(item.Id);
    }
}
catch (ThreadAbortException)
{
    SaveCheckpoint(lastProcessedId); // 最後安全點
    Thread.ResetAbort(); // 視需求，避免吞掉關閉流程
}
```

實際案例：對應文中卸載造成的中斷風險。
實作環境：ASP.NET 經典。
實測數據（教學示意）：
改善前：重啟後重複/遺失。
改善後：從檢查點續跑。
改善幅度：資料錯誤率降至 ~0。

Learning Points（學習要點）
核心知識點：
- ThreadAbortException 行為
- 檢查點策略
- 恢復與冪等

技能要求：
必備技能：資料模型。
進階技能：效能/一致性權衡。

延伸思考：
- 檢查點頻率與成本。
- 與分散式鎖結合。

Practice Exercise（練習題）
基礎練習：每 100 筆保存檢查點（30 分）。
進階練習：模擬中斷與恢復（2 小時）。
專案練習：可配置檢查點策略（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：可續跑
程式碼品質（30%）：結構清晰
效能優化（20%）：保存頻率合理
創新性（10%）：冪等設計


## Case #14: 控制資源使用，避免與 Web 請求競爭

### Problem Statement（問題陳述）
業務場景：背景任務與前台請求共用執行緒池/CPU/IO，夜間尚可，白天高峰時造成延遲。需限制並發度與資源使用。
技術挑戰：平衡吞吐與服務品質，避免資源飢餓。
影響範圍：用戶體驗、SLA。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 背景任務未限流。
2. ThreadPool 飆升造成 GC 壓力。
3. 無高峰閃避。
深層原因：
- 架構層面：未分離資源池。
- 技術層面：缺少限流/節流。
- 流程層面：無高峰策略。

### Solution Design（解決方案設計）
解決策略：使用 SemaphoreSlim 限制並發，白天降級或停用；合理設定 ThreadPool 最小執行緒；對 IO 操作做批次與退避；必要時分離至獨立 App Pool/主機。

實施步驟：
1. 並發限制
- 實作細節：SemaphoreSlim(maxConcurrency) 包裹工作。
- 所需資源：C#。
- 預估時間：0.5 小時。

2. 高峰策略
- 實作細節：白天僅查詢狀態，夜間全量。
- 所需資源：排程配置。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
var gate = new SemaphoreSlim(2); // 同時最多兩個
await gate.WaitAsync(ct);
try { await ProcessAsync(job, ct); }
finally { gate.Release(); }
```

實際案例：避免「讓 worker thread 多做事」卻拖慢網站。
實作環境：任意。
實測數據（教學示意）：
改善前：P95 延遲 > 1s。
改善後：P95 回落至 < 300ms。
改善幅度：延遲改善 70%+。

Learning Points（學習要點）
核心知識點：
- 限流/節流
- ThreadPool 調整
- 高峰降級

技能要求：
必備技能：非同步與並發。
進階技能：容量規劃。

延伸思考：
- 自動化高峰探測與切換。
- A/B 對照量測。

Practice Exercise（練習題）
基礎練習：加入 SemaphoreSlim 限流（30 分）。
進階練習：高峰降級策略（2 小時）。
專案練習：容量/延遲儀表板（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：限流有效
程式碼品質（30%）：清晰可靠
效能優化（20%）：延遲下降
創新性（10%）：自適應策略


## Case #15: ASP.NET Auto-Start/Application Initialization 自動啟動工作

### Problem Statement（問題陳述）
業務場景：網站部署或回收後，希望背景任務立即啟動，不需等待第一個使用者請求，以減少冷啟延遲與任務空窗。
技術挑戰：ASP.NET 傳統需請求才載入 AppDomain；需要啟用自動啟動並在啟動流程中安全地拉起背景服務。
影響範圍：可用性、任務時效。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未啟用預載/自動啟動。
2. 背景任務需人工觸發。
3. 冷啟耗時。
深層原因：
- 架構層面：啟動流程未設計。
- 技術層面：未使用 Auto-Start/Application Initialization。
- 流程層面：缺少部署後驗證。

### Solution Design（解決方案設計）
解決策略：IIS 8+ 開啟 Application Initialization，站台設 preloadEnabled=true；ASP.NET 4.0+ 可配置 serviceAutoStartProviders 自動啟動型別，在啟動時註冊背景服務（IRegisteredObject/QBWI）。

實施步驟：
1. 啟用預載
- 實作細節：preloadEnabled、startMode: AlwaysRunning。
- 所需資源：IIS 8+。
- 預估時間：0.5 小時。

2. 自動啟動提供者
- 實作細節：web.config 設定 serviceAutoStartProviders。
- 所需資源：ASP.NET 4.0+。
- 預估時間：1 小時。

關鍵程式碼/設定：
```xml
<system.applicationHost>
  <applicationPools>
    <add name="MyAppPool" startMode="AlwaysRunning" />
  </applicationPools>
</system.applicationHost>

<system.webServer>
  <applicationInitialization doAppInitAfterRestart="true" />
</system.webServer>

<system.web>
  <serviceAutoStartProviders>
    <add name="MyStarter" type="MyApp.Startup, MyApp" />
  </serviceAutoStartProviders>
  <applicationPool enableServiceAutoStart="true" />
</system.web>
```

實際案例：避免「放著跑」卻因未預載而啟動延遲。
實作環境：IIS 8+/ASP.NET 4.0+。
實測數據（教學示意）：
改善前：冷啟等待首個請求。
改善後：部署/回收後自動啟動。
改善幅度：任務空窗時間 → 0。

Learning Points（學習要點）
核心知識點：
- IIS 預載/自動啟動
- 啟動流程中的背景服務註冊
- 與 QBWI/IRegisteredObject 協同

技能要求：
必備技能：IIS 配置。
進階技能：啟動序列設計。

延伸思考：
- 與 CI/CD 整合自動驗證健康。
- 啟動過程錯誤處理。


--------------------
案例到此共 15 則，完整涵蓋文中觀察到的兩個核心問題（Idle Timeout 導致背景執行緒終止、未處理例外導致 w3wp 停止）及其延伸的實務解法：生命週期綁定、排程/持久化、可觀測性、安全與現代化替代方案。

### 案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #1 Idle Timeout/保活基礎
  - Case #2 例外處理與全域攔截
  - Case #5 Keep-Alive/Warm-up
  - Case #10 心跳監控與安全
- 中級（需要一定基礎）
  - Case #3 IRegisteredObject 生命週期
  - Case #4 週期回收與排程對齊
  - Case #6 QBWI 綁定生命週期
  - Case #9 Quartz.NET
  - Case #14 資源限流
  - Case #15 Auto-Start/Initialization
- 高級（需要深厚經驗）
  - Case #7 外部 Worker/Windows Service
  - Case #8 Hangfire（多節點/持久化）
  - Case #11 Crash Dump 根因分析
  - Case #12 分散式鎖
  - Case #13 檢查點續跑

2. 按技術領域分類
- 架構設計類：#7, #8, #9, #12, #13, #15
- 效能優化類：#1, #4, #14
- 整合開發類：#6, #8, #9, #15
- 除錯診斷類：#2, #11, #13
- 安全防護類：#5, #10

3. 按學習目標分類
- 概念理解型：#1, #2, #3, #6
- 技能練習型：#4, #5, #10, #14, #15
- 問題解決型：#7, #8, #9, #11, #12, #13
- 創新應用型：#8, #9, #12, #14, #15

### 案例關聯圖（學習路徑建議）

- 建議先學
  - Case #1（Idle Timeout/保活基礎）→ 建立對 IIS 行為的核心認知
  - Case #2（例外處理）→ 確保不因未攔截例外而崩潰
  - Case #5（Keep-Alive/Warm-up）→ 快速降低停擺風險
  - Case #10（心跳監控）→ 具備早期告警能力

- 依賴關係
  - Case #3（IRegisteredObject）依賴 #1/#2 的基礎認知
  - Case #4（回收對齊）依賴 #3 的安全停機能力
  - Case #6（QBWI）與 #3 可互補替代
  - Case #12（分散式鎖）依賴 #7/#8/#9（任務外部化/框架化）或至少 #3/#6（在站內執行時）
  - Case #13（檢查點）應與 #3/#6 搭配
  - Case #11（Dump 分析）可在 #2 之後進一步深挖
  - Case #14（資源限流）建立在任務穩定執行後的優化階段
  - Case #15（Auto-Start）與 #1/#5 配合，縮短冷啟空窗

- 完整學習路徑建議
  1) 基礎穩定：#1 → #2 → #5 → #10
  2) 生命週期與回收相容：#3 → #4 → #6 → #13
  3) 功能化與可觀測：#9 或 #8（擇一或並學）→ #12 → #14
  4) 外部化與現代化：#7（外部 Worker）→ #15（Auto-Start，若仍在站內）→ #11（進階診斷）
  
  如以最穩健路線：完成 1) → 2) 後，直接進入 4) 的 #7（遷出至外部 Worker），再回補 3) 的監控/鎖/效能最佳化，達成可用與可運維的最終狀態。