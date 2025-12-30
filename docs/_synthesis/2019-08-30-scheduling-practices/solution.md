---
layout: synthesis
title: "後端工程師必備: 排程任務的處理機制練習 (12/01 補完)"
synthesis_type: solution
source_post: /2019/08/30/scheduling-practices/
redirect_from:
  - /2019/08/30/scheduling-practices/solution/
---

以下為基於原文萃取與擴充的 18 個結構化解決方案案例。每個案例均對應文中實際出現的問題、根因、方案與成效指標，並補上可直接動手的實作步驟與練習。

## Case #1: 基準解 — 朴素輪詢式排程（AndrewDemo）

### Problem Statement（問題陳述）
- 業務場景：網站支援使用者預約在特定時間執行工作。限制為資料庫僅能被動查詢、不可用主動通知。需在多實例（高可用）情境下，確保每筆工作在允許延遲內準時且僅執行一次。
- 技術挑戰：在只能輪詢的前提下，平衡資料庫負載與啟動精準度；多實例搶鎖避免重複執行；優雅停機避免遺失已鎖工作。
- 影響範圍：DB 查詢放大、延遲波動大、峰值工作處理不均，導致 SLA 與成本惡化。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 固定週期掃描（每 10 秒）導致延遲波動大（依賴掃描相位）。
  2. 未在準點前預計執行，導致鎖定與執行時間都算入延遲。
  3. 一旦清單為空就長休眠，易錯失剛插入的近時程任務。
- 深層原因：
  - 架構層面：單一「查清單→遍歷嘗試鎖定→處理→再睡」循環，無法針對尖峰與秒級精準度優化。
  - 技術層面：缺乏提前鎖定與等待、缺乏併行處理結構、無 de-jitter 機制。
  - 流程層面：僅以固定 sleep 控制輪詢，不考慮 fetch 花費時間與實際工作節奏。

### Solution Design（解決方案設計）
- 解決策略：以最簡單可行的輪詢實作為基準，驗證基線分數（COST 與 EFFICIENT），作為後續迭代優化比較的對照組。

- 實施步驟：
  1. 建立背景服務循環
     - 實作細節：每輪呼叫 repo.GetReadyJobs()，對每筆嘗試 AcquireJobLock 後 ProcessLockedJob。
     - 所需資源：.NET Generic Host、JobsRepo
     - 預估時間：0.5 天
  2. 空清單延遲
     - 實作細節：若本輪無任務可執行，Delay(JobSettings.MinPrepareTime)。
     - 所需資源：CancellationToken 與 Task.Delay
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 朴素輪詢，無提前鎖、無 de-jitter
foreach (var job in repo.GetReadyJobs())
{
    if (repo.AcquireJobLock(job.Id))
    {
        repo.ProcessLockedJob(job.Id);
        Console.Write("O");
    }
    else
    {
        Console.Write("X");
    }
}
await Task.Delay(JobSettings.MinPrepareTime, stoppingToken); // 空清單則休息
```

- 實際案例：SubWorker.AndrewDemo
- 實作環境：.NET Core Generic Host、MSSQL 2017、Windows 10 Pro for Workstations (1903)
- 實測數據：
  - 改善前：無
  - 改善後（Baseline）：1726 筆、Avg Delay 4343 ms、Stdev 2858.52、Delay Too Long 46、ACQUIRE_FAILURE 4916、QUERYLIST 702、COST_SCORE 119360、EFFICIENT_SCORE 7201.52
  - 改善幅度：作為基準分數（後續案例均以此為對照）

Learning Points（學習要點）
- 核心知識點：
  - 輪詢型排程的成本/精準度權衡
  - Exactly-once 的鎖定語義
  - 指標驅動優化（Cost/Efficient）
- 技能要求：
  - 必備技能：.NET 背景服務、SQL 索引與查詢
  - 進階技能：多執行緒、爭用與退避策略
- 延伸思考：
  - 何時應切換到外部排程框架？
  - 如何在雲端託管環境下觀測與調參？
  - 能否動態調整輪詢間隔以自適應流量？

Practice Exercise（練習題）
- 基礎練習：啟動 baseline，收集 10 分鐘統計報表
- 進階練習：把空清單 sleep 由固定改為可配置，觀察分數變化
- 專案練習：擴充 Logs，將每輪耗時、命中/落空詳列

Assessment Criteria（評估標準）
- 功能完整性（40%）：能跑完並產生統計
- 程式碼品質（30%）：結構清晰、可讀性高
- 效能優化（20%）：合理索引與查詢
- 創新性（10%）：有利於後續優化的可觀測性


## Case #2: 最終解 — 提前鎖定 + 抽樣抖動 + 準點等待（AndrewSubWorkerBackgroundService2）

### Problem Statement（問題陳述）
- 業務場景：需要在秒級啟動精準度下維持低 DB 負載與高可用，能平滑尖峰（一次 20 筆/13 秒）且妥善關機。
- 技術挑戰：多實例搶鎖碰撞降低、降低延遲均值與標準差、確保關機時不遺失已鎖任務。
- 影響範圍：SLA、DB 成本、叢集穩定性（尤其在重啟/升級時）。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 朴素輪詢把鎖定/建立連線時間算入延遲，均值/波動偏高。
  2. 多實例同步掃描，Acquire 撞鎖成本高。
  3. 早鎖占用過久，停機時易遺失工作。
- 深層原因：
  - 架構層面：單循環負責所有動作，缺少前置準備與後端併行消化的分層。
  - 技術層面：無抖動、無動態補償（扣除 fetch 耗時），無限制提前鎖窗口。
  - 流程層面：停機時未確保隊列排空、提前鎖時間無上限導致關機風險。

### Solution Design（解決方案設計）
- 解決策略：將「提前鎖定 + 抖動」與「準點等待 + 併行消化」結合，前端只在 RunAt 前 300~1700ms 內鎖定，並補償 fetch 耗時，後端以多線程平行 ProcessLockedJob，停機時關閉入列並等待出列完畢。

- 實施步驟：
  1. 前端 fetch 與提前鎖定
     - 實作細節：GetReadyJobs(MinPrepareTime)，若距離 RunAt > 隨機預測窗則 Delay；再 GetJob 確認未處理後 AcquireJobLock，若未達 RunAt 再 Delay 到準點再入列。
     - 所需資源：JobsRepo、CancellationToken、Stopwatch
     - 預估時間：1 天
  2. 後端平行處理
     - 實作細節：BlockingCollection 作為隊列，啟 10 條工作執行緒，GetConsumingEnumerable() 直到 CompleteAdding。
     - 所需資源：BlockingCollection、Thread
     - 預估時間：0.5 天
  3. 停機協調
     - 實作細節：收到取消訊號→停止入列→CompleteAdding→Join 工作執行緒
     - 所需資源：Generic Host、CancellationToken
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 提前鎖定 + 抽樣抖動（300~1700ms）
int predict = rnd.Next(300, 1700);
if (job.RunAt - DateTime.Now > TimeSpan.FromMilliseconds(predict))
    await Task.Delay(job.RunAt - DateTime.Now - TimeSpan.FromMilliseconds(predict), stoppingToken);

if (repo.GetJob(job.Id).State != 0) continue;
if (!repo.AcquireJobLock(job.Id)) continue;

if (DateTime.Now < job.RunAt)
    await Task.Delay(job.RunAt - DateTime.Now, stoppingToken); // 準點開始
_queue.Add(job);

// fetch 迴圈的動態補償休息：MinPrepareTime - 本輪耗時
await Task.Delay((int)Math.Max(
    (JobSettings.MinPrepareTime - timer.Elapsed).TotalMilliseconds, 0),
    stoppingToken);
```

- 實際案例：AndrewSubWorkerBackgroundService2（作者最終方案）
- 實作環境：同 Case #1
- 實測數據：
  - 改善前（Baseline）：Avg 4343ms / Stdev 2858.52、COST 119360、EFFIC 7201.52
  - 改善後（最佳實測擇優）：在 WORKERS02 配置下 EFFICIENT_SCORE 145.40、COST_SCORE 20337；在作者選用的「極致效能」配置下亦為全場 EFFIC 最佳且 COST 居前段
  - 改善幅度：EFFIC 相對基準顯著下降（> 98%）；COST 相對基準大幅下降（> 80% 等級）

Learning Points（學習要點）
- 核心知識點：
  - 提前鎖定窗口與關機風險的平衡
  - 抖動（jitter）降低多實例同步碰撞
  - 動態補償避免輪詢節奏漂移
- 技能要求：
  - 必備技能：多執行緒與生產者/消費者、可中斷延遲
  - 進階技能：停機協調、可觀測性、效能調參
- 延伸思考：
  - 如何自動根據延遲統計調整提前窗口與執行緒數？
  - 不同 VM/容器 CPU 性能下如何適配？
  - Acquire 與 GetJob 的比例如何動態最佳化？

Practice Exercise（練習題）
- 基礎練習：加入「提前鎖定 + 抖動」，觀察 EFFIC/Cost 變化
- 進階練習：比較 5/10/15 執行緒的 EFFIC/Cost 曲線
- 專案練習：實作配置中心，動態調整提前窗口與執行緒數

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確達成 Exactly-once 與停機不遺失
- 程式碼品質（30%）：模組化、可測試
- 效能優化（20%）：EFFIC/Cost 顯著優於基準
- 創新性（10%）：自適應調參或可觀測改良


## Case #3: 以 GetJob() 先驗狀態，降低 Acquire 碰撞與成本

### Problem Statement（問題陳述）
- 業務場景：多個實例同時嘗試 AcquireJobLock，導致大量失敗嘗試與 DB 負載飆升。
- 技術挑戰：Acquire 失敗成本（權重 10）遠高於 QueryJob（權重 1），需要先驗狀態以降低無效 Acquire。
- 影響範圍：COST_SCORE 大幅升高、DB 資源被鎖競爭與重試吞沒。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未先查單筆狀態，直接 Acquire 造成高失敗率。
  2. 多實例同步掃描，同步觸發 Acquire 撞鎖。
  3. 沒有抖動導致競爭高峰重疊。
- 深層原因：
  - 架構層面：缺少「先驗—再鎖」的 guard。
  - 技術層面：忽略成本函數（Acquire x10 vs Query x1）。
  - 流程層面：無降碰撞策略（時間錯開、亂數退避）。

### Solution Design（解決方案設計）
- 解決策略：對每筆候選任務先 repo.GetJob(job.Id)，僅在狀態為未處理時才嘗試 Acquire；搭配抖動或延遲錯峰。

- 實施步驟：
  1. 實作先驗查詢
     - 實作細節：GetJob(job.Id).State == 0 時才 AcquireJobLock
     - 所需資源：JobsRepo
     - 預估時間：0.5 天
  2. 增加錯峰抖動
     - 實作細節：在嘗試 Acquire 前加入隨機短延遲（數十至數百 ms）
     - 所需資源：System.Random
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var current = repo.GetJob(job.Id);
if (current.State == 0) // 先驗狀態，避免無效 Acquire
{
    if (repo.AcquireJobLock(job.Id))
    {
        repo.ProcessLockedJob(job.Id);
    }
}
```

- 實際案例：PR1/PR3/PR5/PR7 均採用此策略；PR3（jwchen-dev）為全場最低 COST_SCORE
- 實作環境：同 Case #1
- 實測數據：
  - 改善前（Baseline）：ACQUIRE_FAILURE 4916、COST 119360
  - 改善後：COST_SCORE 顯著下降（PR3 全場最低）
  - 改善幅度：相對 Baseline 由「墊底等級」下降至「全場最低等級」

Learning Points（學習要點）
- 核心知識點：
  - 成本函數驅動的 API 呼叫順序調整
  - 先驗狀態降低碰撞與重試
  - 隨機退避/抖動的應用
- 技能要求：
  - 必備技能：DB 查詢與鎖定語義
  - 進階技能：爭用理論與退避策略
- 延伸思考：
  - 能否以批次查詢（IN 子句）合併 GetJob？
  - Acquire 成功率能否作為調參依據？

Practice Exercise（練習題）
- 基礎練習：加入先驗查詢，記錄 Acquire 失敗數變化
- 進階練習：加入隨機退避，測試不同退避範圍的 COST/碰撞
- 專案練習：實作成本監測儀表板（Query/Acquire 次數與比率）

Assessment Criteria（評估標準）
- 功能完整性（40%）：先驗後鎖邏輯正確
- 程式碼品質（30%）：清楚抽象、可觀測
- 效能優化（20%）：Acquire 失敗顯著下降
- 創新性（10%）：退避策略自動調整


## Case #4: 忙等（Busy Waiting）轉精準等待（Task.Delay / WaitHandle）

### Problem Statement（問題陳述）
- 業務場景：任務需準點啟動，開發者以 while 迴圈不斷檢查 DateTime.Now，造成 CPU 空轉與效能問題。
- 技術挑戰：在不犧牲精準度的前提下，移除忙等造成的 CPU 壓力。
- 影響範圍：CPU 高負載、其他服務受影響、效能波動。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 以 Thread.Sleep(短) 或 while 迴圈檢查時間。
  2. 未使用可中止的等待原語（CancellationToken、WaitHandle）。
  3. 停機時無法提前打斷忙等。
- 深層原因：
  - 架構層面：缺少統一的時間等待抽象。
  - 技術層面：忽略 OS 提供的定時與中斷機制。
  - 流程層面：停機流程未與等待整合。

### Solution Design（解決方案設計）
- 解決策略：以 Task.Delay(到 RunAt - now) 或 WaitHandle.WaitAny(Delay/Stop) 取代忙等，配合 CancellationToken 可中止。

- 實施步驟：
  1. 改寫等待機制
     - 實作細節：Task.Delay(timeout, token)，或 WaitAny(DelayTask, StopHandle)
     - 所需資源：CancellationToken/AutoResetEvent
     - 預估時間：0.5 天
  2. 整合停機流程
     - 實作細節：收到取消時立即中止等待，釋放資源
     - 所需資源：Generic Host
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 可中止、精準的等待到 RunAt
var wait = job.RunAt - DateTime.Now;
if (wait > TimeSpan.Zero)
{
    var idx = Task.WaitAny(
        Task.Delay(wait, stoppingToken),
        Task.Run(() => _stopHandle.WaitOne())); // 可立即停機
    if (idx == 1) return; // 停機優先
}
```

- 實際案例：PR2（JolinDemo）展示以 WaitHandle + Delay 組合，停機可精準退出
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：忙等造成 CPU 佔用高、不可中止
  - 改善後：CPU 空轉消失，停機時可即時中止等待
  - 改善幅度：穩定性與資源佔用顯著改善（質性）

Learning Points（學習要點）
- 核心知識點：
  - 忙等的風險與反模式
  - 可中止等待原語（Delay/WaitHandle）
- 技能要求：
  - 必備技能：Task/Thread、CancellationToken
  - 進階技能：停機協調
- 延伸思考：
  - 高精度需求下是否需改用計時器輪（Timer wheel）？
  - 大量任務同秒準點的等待策略最佳化？

Practice Exercise（練習題）
- 基礎練習：以 Task.Delay 取代忙等
- 進階練習：加入 WaitHandle，測試 CTRL-C 中止
- 專案練習：將等待封裝成抽象介面並注入

Assessment Criteria（評估標準）
- 功能完整性（40%）：等待正確、可中止
- 程式碼品質（30%）：抽象清楚
- 效能優化（20%）：CPU 降低
- 創新性（10%）：等待策略可測試化


## Case #5: 中央隊列（BlockingCollection）取代分片隊列，避免負載不均

### Problem Statement（問題陳述）
- 業務場景：以固定分片（mod）方式將工作分配到各 worker 專屬佇列，當某 worker 慢/卡死，該分片工作積壓。
- 技術挑戰：併行利用率與公平性低，出現局部壅塞。
- 影響範圍：延遲標準差上升、SLA 不穩、資源浪費。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 靜態分片無動態調整與搶佇列機制。
  2. 無工作竊取（work stealing）。
  3. 快慢 worker 不均導致整體延遲惡化。
- 深層原因：
  - 架構層面：隊列設計不利於動態平衡。
  - 技術層面：ThreadPool 長佔用執行長任務易引發副作用。
  - 流程層面：缺乏 backpressure 與飽和控制。

### Solution Design（解決方案設計）
- 解決策略：改用單一 BlockingCollection 為中央隊列，後端多 worker 以 GetConsumingEnumerable() 均衡取件，提高吞吐與公平性。

- 實施步驟：
  1. 建立中央隊列
     - 實作細節：BlockingCollection<JobInfo>，生產者 Add，消費者 GetConsumingEnumerable
     - 所需資源：BlockingCollection
     - 預估時間：0.5 天
  2. 停機時 CompleteAdding
     - 實作細節：停止入列→CompleteAdding→等待所有消費者退出
     - 所需資源：CancellationToken
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 中央隊列 + 多 worker 消費
var queue = new BlockingCollection<JobInfo>();

// Producer
foreach (var job in readyJobs)
    queue.Add(job);

// Consumers
foreach (var job in queue.GetConsumingEnumerable(stoppingToken))
{
    repo.ProcessLockedJob(job.Id);
}
```

- 實際案例：作者最終方案、PR5（BorisDemo）、PR7（AndyDemo）均以中央隊列達成平滑消化
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：分片不均、併行利用率低
  - 改善後：延遲標準差降低、尖峰更平滑；PR5/PR7 在 EFFIC/COST 均有不錯排名
  - 改善幅度：EFFIC 標準差顯著下降（質性）

Learning Points（學習要點）
- 核心知識點：
  - 生產者/消費者模式
  - 中央隊列 vs 分片佇列的取捨
- 技能要求：
  - 必備技能：BlockingCollection
  - 進階技能：停機排空與流量控制
- 延伸思考：
  - 何時需要 bounded queue 以限制上游壓力？
  - 是否加入優先級佇列支援？

Practice Exercise（練習題）
- 基礎練習：以中央隊列改寫分片隊列版本
- 進階練習：引入 bounded capacity，比較 EFFIC/Cost
- 專案練習：為尖峰（20/13s）設計壓力測試並觀測延遲分布

Assessment Criteria（評估標準）
- 功能完整性（40%）：隊列行為正確
- 程式碼品質（30%）：併發安全與可讀性
- 效能優化（20%）：延遲分布改善
- 創新性（10%）：壓力下的退讓策略


## Case #6: 多實例高可用與優雅停機（Generic Host + HATEST）

### Problem Statement（問題陳述）
- 業務場景：同服務多實例部署以確保高可用，隨時可能滾動重啟。需保證已鎖任務不遺失、未鎖任務可被其他實例接手。
- 技術挑戰：Windows Console 無標準 SIGTERM，停機需可程式化控制，避免強殺。
- 影響範圍：資料一致性（Exactly-once）、SLA、維運風險。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 不當使用 Task.Wait 導致聚合例外（TaskCanceledException）。
  2. 停機時未停止入列、未排空隊列、未 Join 工作者。
  3. 提前鎖定但未處理完即退出造成孤兒鎖。
- 深層原因：
  - 架構層面：缺乏停機協調邏輯。
  - 技術層面：Windows 無直接信號，需自行 Start/Stop 模擬。
  - 流程層面：未設計 HATEST 自動化驗證腳本。

### Solution Design（解決方案設計）
- 解決策略：使用 .NET Generic Host 統一管理 Start/Stop；HATEST 以 Host.Start/Stop 迭代模擬隨機重啟；停機序：停止入列→CompleteAdding→等待工作執行緒完成→退出。

- 實施步驟：
  1. 主機化背景服務
     - 實作細節：HostBuilder + BackgroundService，注入 CancellationToken
     - 所需資源：Microsoft.Extensions.Hosting
     - 預估時間：0.5 天
  2. 停機協調
     - 實作細節：Stop 時設置停止旗標、CompleteAdding、Join 工作執行緒
     - 所需資源：BlockingCollection、Thread
     - 預估時間：0.5 天
  3. HATEST 腳本
     - 實作細節：5 實例、10 分鐘測試、每實例隨機 10~30 秒間隔停止再啟動
     - 所需資源：測試 runner（作者已提供）
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var host = new HostBuilder()
    .ConfigureServices(s => s.AddHostedService<MyBackgroundService>())
    .Build();

host.Start();         // 測試程式控制 Start
// ... 隨機時間後
await host.StopAsync(); // 模擬優雅停機，觸發 CancellationToken
```

- 實際案例：多數 PR 通過 HATEST；PR4（LeviDemo）因過早執行（Early Exec）失格
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：強殺導致資料遺失與例外
  - 改善後：HATEST PASS 且統計正常（Exactly-once）
  - 改善幅度：可靠度顯著提升（質性）

Learning Points（學習要點）
- 核心知識點：
  - Windows 下的停機模擬與服務化
  - 優雅停機序列設計
- 技能要求：
  - 必備技能：Generic Host、CancellationToken
  - 進階技能：HATEST 腳本設計
- 延伸思考：
  - 容器環境（K8s preStop、terminationGracePeriod）如何對應？
  - 早鎖策略下的停機 SLA 如何界定？

Practice Exercise（練習題）
- 基礎練習：將服務以 Generic Host 啟動並可 StopAsync
- 進階練習：停機時序列出所有未處理任務
- 專案練習：撰寫 HATEST runner，自動報告 PASS/FAIL 指標

Assessment Criteria（評估標準）
- 功能完整性（40%）：HATEST PASS
- 程式碼品質（30%）：停機協調完整
- 效能優化（20%）：停機延遲可控
- 創新性（10%）：HATEST 自動化擴展


## Case #7: 提前鎖定 vs 準點鎖定的架構抉擇

### Problem Statement（問題陳述）
- 業務場景：為降低延遲並避免競爭，考慮在 RunAt 前提前鎖定；但提前太早會增加停機風險。
- 技術挑戰：如何在 Cost/Effic 與停機風險間取得平衡。
- 影響範圍：EFFIC 減少、COST 減少、但可能導致停機時孤兒鎖。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 準點鎖定：延遲高、競爭高。
  2. 提前鎖定：停機風險高、需排空隊列。
  3. 無上限的提前窗口：不可控。
- 深層原因：
  - 架構層面：缺少提前窗口上限與停機匹配策略。
  - 技術層面：沒有 de-jitter，碰撞仍可能集中。
  - 流程層面：停機 SLA 未與提前策略對齊。

### Solution Design（解決方案設計）
- 解決策略：設定提前鎖定窗口（如 300~1700ms）+ 抖動；停機時在 1.7 秒內可安全退出；若需更長提前，配合必停機等待與隊列排空。

- 實施步驟：
  1. 設定提前窗口
     - 實作細節：以亂數決定提前毫秒數，作為鎖定門檻
     - 所需資源：Random、Delay
     - 預估時間：0.5 天
  2. 停機對齊
     - 實作細節：記錄最大提前值，停機時等待該值（或排空）
     - 所需資源：配置與監控
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
int early = rnd.Next(300, 1700); // 提前鎖定窗口
if (job.RunAt - now > TimeSpan.FromMilliseconds(early))
    await Task.Delay(job.RunAt - now - TimeSpan.FromMilliseconds(early), token);
if (repo.AcquireJobLock(job.Id)) { ... }
```

- 實際案例：作者最終方案採 300~1700ms；PR5/PR7 於 fetch 階段即鎖定，取得良好 EFFIC/COST，但需小心停機
- 實作環境：同 Case #1
- 實測數據：
  - 改善前（Baseline）：EFFIC 高、COST 高
  - 改善後：EFFIC/COST 顯著下降（作者最終方案、PR5/PR7 均表現優）
  - 改善幅度：質性為顯著

Learning Points（學習要點）
- 核心知識點：
  - 早鎖策略與停機的聯動風險
  - 抖動 vs 碰撞
- 技能要求：
  - 必備技能：時間視窗控制
  - 進階技能：停機 SLA 設計
- 延伸思考：
  - 以歷史延遲自適應調整提前窗口
  - 邊際情況（長準備時間）如何處理

Practice Exercise（練習題）
- 基礎練習：嘗試 100/500/1000ms 提前窗口
- 進階練習：停機時測最大等待時間 vs 遺失率
- 專案練習：增加自適應提前窗口（根據最近 N 次 EFFIC）

Assessment Criteria（評估標準）
- 功能完整性（40%）：不遺失；Exactly-once
- 程式碼品質（30%）：窗口與停機策略清晰
- 效能優化（20%）：EFFIC 降低
- 創新性（10%）：自適應機制


## Case #8: 去同步化（De-synchronization）— 隨機化掃描/休眠

### Problem Statement（問題陳述）
- 業務場景：多實例同一節奏掃描，集體在同秒 Acquire 撞鎖，導致 COST 爆增與 EFFIC 惡化。
- 技術挑戰：需打散多實例在掃描與鎖定上的時間相位。
- 影響範圍：Acquire 失敗高、DB 負載、延遲波動。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 固定節奏掃描（如每 10 秒起始）。
  2. 無抖動（jitter）。
  3. 同步查詢窗口與排序導致集中處理。
- 深層原因：
  - 架構層面：缺少退避與抖動策略。
  - 技術層面：Delay 與 Sleep 無亂數化。
  - 流程層面：多實例共同部署同時啟動。

### Solution Design（解決方案設計）
- 解決策略：掃描與提前鎖定加入亂數化延遲；延遲補償時亦可加入小幅抖動，打散 Acquire 衝擊。

- 實施步驟：
  1. 掃描時間抖動
     - 實作細節：sleepSpan = 隨機（MinPrepareTime ± x）
     - 所需資源：Random
     - 預估時間：0.5 天
  2. 鎖定時間抖動
     - 實作細節：見 Case #7
     - 所需資源：Random
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 掃描抖動（PR3 示意）
TimeSpan baseWait = TimeSpan.FromSeconds(10);
TimeSpan randomJitter = TimeSpan.FromMilliseconds(rnd.Next(0, 1500));
await Task.Delay(baseWait + randomJitter, token);
```

- 實際案例：PR3（jwchen-dev）在 1 實例時 EFFIC 較差（5924.54），但實例數增加後迅速改善；COST_SCORE 全場最低
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：多實例 Acquire 撞鎖，COST 高
  - 改善後：COST 顯著下降（全場最低），EFFIC 隨實例數提升而快速改善
  - 改善幅度：質性為顯著

Learning Points（學習要點）
- 核心知識點：
  - 抖動在分散式系統中的應用
  - 延遲 vs 碰撞的權衡
- 技能要求：
  - 必備技能：隨機化設計
  - 進階技能：叢集級效能觀測
- 延伸思考：
  - 在容器編排下，是否需在 Probe 也加入抖動？
  - 抖動範圍如何自動調參？

Practice Exercise（練習題）
- 基礎練習：在掃描處加入 ±1.5 秒抖動
- 進階練習：嘗試不同抖動分布（均勻/高斯）
- 專案練習：依 Acquire 失敗率動態調整抖動幅度

Assessment Criteria（評估標準）
- 功能完整性（40%）：全程正常
- 程式碼品質（30%）：抖動可配置
- 效能優化（20%）：COST 明顯下降
- 創新性（10%）：自適應抖動


## Case #9: 查詢窗口對齊 MinPrepareTime，避免誤差累積

### Problem Statement（問題陳述）
- 業務場景：MinPrepareTime = 10 秒，卻用 15 秒查詢窗口，造成新插入的 10~15 秒任務晚一輪才處理，白白增加延遲。
- 技術挑戰：窗口過大或過小都影響效率與精準度。
- 影響範圍：平均延遲上升、標準差擴大、COST 增加（多餘掃描）。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 查詢窗口大於 MinPrepareTime。
  2. 缺少排序與去重校正。
  3. 無動態補償（扣掉 fetch 耗時）。
- 深層原因：
  - 架構層面：掃描節奏與插入節奏未對齊。
  - 技術層面：硬編碼窗口值。
  - 流程層面：未明確定義準備時間語義。

### Solution Design（解決方案設計）
- 解決策略：GetReadyJobs(JobSettings.MinPrepareTime)，確保一輪涵蓋「從現在往前/後」正確窗口，並以 MinPrepareTime - 本輪耗時作為休息基準。

- 實施步驟：
  1. 對齊窗口
     - 實作細節：repo.GetReadyJobs(JobSettings.MinPrepareTime)
     - 所需資源：JobSettings
     - 預估時間：0.5 天
  2. 動態補償
     - 實作細節：Delay(MinPrepareTime - timer.Elapsed)
     - 所需資源：Stopwatch
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var start = Stopwatch.StartNew();
foreach (var job in repo.GetReadyJobs(JobSettings.MinPrepareTime))
{
    // ... 處理
}
await Task.Delay((int)Math.Max(
    (JobSettings.MinPrepareTime - start.Elapsed).TotalMilliseconds, 0), token);
```

- 實際案例：PR1 因 15 秒窗口產生不必要延遲；作者最終方案使用 MinPrepareTime 並動態補償
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：EFFIC 偏高
  - 改善後：EFFIC 明顯改善（質性）
  - 改善幅度：質性為顯著

Learning Points（學習要點）
- 核心知識點：
  - 查詢窗口與準備時間語義
  - 補償避免漂移
- 技能要求：
  - 必備技能：時間窗口計畫
  - 進階技能：準時性控制
- 延伸思考：
  - 窗口可否依流量動態擴縮？
  - 與 DB 索引（RunAt,State）配合的最佳策略

Practice Exercise（練習題）
- 基礎練習：由 15 秒改為 MinPrepareTime
- 進階練習：加入補償並觀測延遲分布
- 專案練習：設計窗口自動調參策略（根據負載）

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確涵蓋窗口
- 程式碼品質（30%）：明確可配置
- 效能優化（20%）：延遲下降
- 創新性（10%）：自動化調參


## Case #10: 使用 Channel（System.Threading.Channels）導入純 Async 生消模式

### Problem Statement（問題陳述）
- 業務場景：BlockingCollection 提供同步 API，用於 Async 堆疊時需多層包裝；希望以 Channel 實現端到端 Async。
- 技術挑戰：錯誤配置 Channel（多個小容量單讀寫 Channel）會導致實際併行下降。
- 影響範圍：EFFIC 未達預期，尖峰時序列化瓶頸。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 多 Channel + 容量 1、SingleReader/SingleWriter，易造成實際單執行緒瓶頸。
  2. 投遞時逐一輪詢 Channel Writer，實際都寫入第一個。
  3. 無統一中央 Channel，不利於公平併行。
- 深層原因：
  - 架構層面：未以共享 Channel 作為單一真實隊列。
  - 技術層面：Channel 選項誤用。
  - 流程層面：尖峰流量測試下不足。

### Solution Design（解決方案設計）
- 解決策略：使用單一共享 Channel（BoundedCapacity > 1），多消費者 Each 調度，提高吞吐；必要時以 ChannelReader.TryRead 快速取件。

- 實施步驟：
  1. 共享 Channel
     - 實作細節：Channel.CreateBounded<JobInfo>(new BoundedChannelOptions(N){SingleWriter=false,SingleReader=false})
     - 所需資源：System.Threading.Channels
     - 預估時間：0.5 天
  2. 多消費者
     - 實作細節：N 個消費者 await reader.ReadAsync(token)
     - 所需資源：Task.Run
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
var ch = Channel.CreateBounded<JobInfo>(new BoundedChannelOptions(100)
{
    SingleReader = false,
    SingleWriter = false,
    AllowSynchronousContinuations = true
});

// Producer
await ch.Writer.WriteAsync(job, token);

// Consumers
for (int i = 0; i < workers; i++)
{
    _ = Task.Run(async () =>
    {
        await foreach (var j in ch.Reader.ReadAllAsync(token))
            repo.ProcessLockedJob(j.Id);
    });
}
```

- 實際案例：PR6（JulianDemo）採用 Channel，但多 Channel + cap=1 造成併行受限，EFFIC 未入前段；COST 在 300% 內
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：序列化瓶頸
  - 改善後（建議配置）：尖峰可平滑消化（質性）
  - 改善幅度：質性為顯著

Learning Points（學習要點）
- 核心知識點：
  - Channel vs BlockingCollection
  - Bounded 容量與公平併行
- 技能要求：
  - 必備技能：Async/await
  - 進階技能：背壓控制
- 延伸思考：
  - 多優先級 Channel 如何實作？
  - 與提前鎖策略結合的最佳容量

Practice Exercise（練習題）
- 基礎練習：以共享 Channel 取代 BlockingCollection
- 進階練習：測試 cap=10/100/1000 的 EFFIC/Cost
- 專案練習：加入優先級與超時移除

Assessment Criteria（評估標準）
- 功能完整性（40%）：端到端 Async
- 程式碼品質（30%）：併發安全
- 效能優化（20%）：尖峰吞吐提升
- 創新性（10%）：背壓策略


## Case #11: 在 fetch 步驟就鎖定（PR5/PR7 路線）

### Problem Statement（問題陳述）
- 業務場景：在掃描到待執行清單時，直接 AcquireJobLock，避免準點再鎖引發競爭。
- 技術挑戰：停機時需確保已鎖任務不遺失；提前鎖窗口可能長達 MinPrepareTime。
- 影響範圍：COST 降低、EFFIC 降低、但停機等待時間可能拉長。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 準點鎖定碰撞嚴重。
  2. 提前鎖定可化解碰撞但延長持鎖時間。
  3. 若不排空隊列即退出，造成已鎖未執行。
- 深層原因：
  - 架構層面：停機序缺少「排空所有已鎖作業」。
  - 技術層面：無最大等待時間保障。
  - 流程層面：運維停機無配套。

### Solution Design（解決方案設計）
- 解決策略：fetch 階段即「先驗→Acquire」，隨後等待 RunAt 入列後端；停機時停止入列、排空隊列、再退出。

- 實施步驟：
  1. fetch 時即鎖
     - 實作細節：GetReadyJobs → GetJob → Acquire → Delay 到 RunAt → queue.Add
     - 所需資源：JobsRepo、BlockingCollection
     - 預估時間：1 天
  2. 停機排空
     - 實作細節：CompleteAdding、Join 消費者
     - 所需資源：CancellationToken
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
foreach (var job in repo.GetReadyJobs(JobSettings.MinPrepareTime))
{
    if (repo.GetJob(job.Id).State == 0 && repo.AcquireJobLock(job.Id))
    {
        var wait = job.RunAt - DateTime.Now;
        if (wait > TimeSpan.Zero) await Task.Delay(wait, token);
        queue.Add(job); // 後端立即 ProcessLockedJob
    }
}
```

- 實際案例：PR5（BorisDemo）、PR7（AndyDemo）此路線 EFFIC/COST 取得平衡且表現不錯
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：準點鎖、COST/EFFIC 高
  - 改善後：兩項指標均進前段
  - 改善幅度：質性為顯著

Learning Points（學習要點）
- 核心知識點：
  - 持鎖時間與停機風險
  - fetch 時鎖定的時序控制
- 技能要求：
  - 必備技能：BlockingCollection、Delay
  - 進階技能：停機序設計
- 延伸思考：
  - 若 MinPrepareTime 可變，如何保證停機上限？
  - 與抖動結合減少撞鎖

Practice Exercise（練習題）
- 基礎練習：實作 fetch 即鎖路線
- 進階練習：停機時列出已鎖但未入列作業
- 專案練習：長準備時間（60 分鐘）模擬測試停機策略

Assessment Criteria（評估標準）
- 功能完整性（40%）：Exactly-once、停機不遺失
- 程式碼品質（30%）：時序清晰
- 效能優化（20%）：EFFIC/COST 平衡
- 創新性（10%）：持鎖上限控制


## Case #12: DB 索引設計（RunAt, State）支援低成本掃描

### Problem Statement（問題陳述）
- 業務場景：必須頻繁掃描「尚未處理且到期」的工作，若缺索引將全表掃描拖垮 DB。
- 技術挑戰：在高頻輪詢下仍需維持低 DB 負載。
- 影響範圍：DB CPU/IO 飆升、整體系統受拖累。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未對 RunAt/State 建索引。
  2. 查詢條件未對齊索引最左前綴。
  3. 無覆蓋索引導致回表。
- 深層原因：
  - 架構層面：忽略讀密集特性。
  - 技術層面：索引設計不良。
  - 流程層面：未監控查詢計畫。

### Solution Design（解決方案設計）
- 解決策略：建立非聚簇索引 IX_Table_Column(RunAt, State)；查詢按 RunAt ASC、State ASC 適配索引。

- 實施步驟：
  1. 建立索引
     - 實作細節：見下 SQL
     - 所需資源：DBA/SQL 權限
     - 預估時間：0.5 天
  2. 校正查詢
     - 實作細節：where state = 0 and runat < getdate() order by runat asc
     - 所需資源：Dapper/ORM
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```sql
CREATE NONCLUSTERED INDEX [IX_Table_Column]
    ON [dbo].[Jobs]([RunAt] ASC, [State] ASC);
```

- 實際案例：原始練習提供此索引；多方案在 DB 成本均可控
- 實作環境：MSSQL 2017 開發版
- 實測數據：
  - 改善前：全表掃描（推定）
  - 改善後：索引掃描，COST 分數可控
  - 改善幅度：DB 資源消耗顯著下降（質性）

Learning Points（學習要點）
- 核心知識點：
  - 查詢模式驅動的索引設計
  - 最左前綴與排序
- 技能要求：
  - 必備技能：SQL 索引與查詢計畫
  - 進階技能：效能監控
- 延伸思考：
  - 是否需要包含列（INCLUDE）做覆蓋索引？
  - 執行歷史統計是否需分表？

Practice Exercise（練習題）
- 基礎練習：建立索引並比較掃描計畫
- 進階練習：加入包含列以避免回表
- 專案練習：建立慢查詢監控

Assessment Criteria（評估標準）
- 功能完整性（40%）：查詢正確
- 程式碼品質（30%）：SQL 可維護
- 效能優化（20%）：掃描效率提升
- 創新性（10%）：覆蓋索引/分表策略


## Case #13: 尖峰負載消化 — 短時間大量任務的平滑處理

### Problem Statement（問題陳述）
- 業務場景：每 13 秒插入 20 筆相同 RunAt 的工作，同時混合隨機單筆插入；需保持低延遲與低波動。
- 技術挑戰：避免在準點鎖定時發生嚴重碰撞；後端需平行消化避免排隊時間增加。
- 影響範圍：延遲均值與標準差、吞吐瓶頸。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 準點鎖定大量集中 Acquire。
  2. 無中央隊列與平行處理，序列化瓶頸。
  3. 無抖動，所有實例同相位。
- 深層原因：
  - 架構層面：需前後端分層與多工處理。
  - 技術層面：缺早鎖與抖動。
  - 流程層面：尖峰未納入測試設計。

### Solution Design（解決方案設計）
- 解決策略：提前鎖定 + 抖動 + 中央隊列 + 多工作者；確保 ProcessLockedJob 得以平行。

- 實施步驟：
  1. 提前鎖定 + 抖動
     - 實作細節：參考 Case #7/8
     - 所需資源：Random、Delay
     - 預估時間：0.5 天
  2. 中央隊列 + 多工作者
     - 實作細節：參考 Case #5
     - 所需資源：BlockingCollection
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 提前 lock + 準點入列 + 多工作者消化
if (repo.AcquireJobLock(job.Id))
{
    if (DateTime.Now < job.RunAt)
        await Task.Delay(job.RunAt - DateTime.Now, token);
    queue.Add(job); // worker 立刻平行處理
}
```

- 實際案例：作者最終方案、PR5/PR7 能在尖峰下維持良好 EFFIC
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：尖峰序列化、延遲高
  - 改善後：延遲均值/標準差下降（質性）
  - 改善幅度：質性為顯著

Learning Points（學習要點）
- 核心知識點：
  - 尖峰流量與退避
  - 併行消化模式設計
- 技能要求：
  - 必備技能：併行與同步
  - 進階技能：壓力測試設計
- 延伸思考：
  - 是否需要節流（throttling）防突刺？
  - 如何動態擴展工作者數量？

Practice Exercise（練習題）
- 基礎練習：重放尖峰插入，觀測延遲分布
- 進階練習：擴增工作者數，繪製延遲 vs 工作者
- 專案練習：以負載自動調整工作者數

Assessment Criteria（評估標準）
- 功能完整性（40%）：尖峰無失誤
- 程式碼品質（30%）：結構清晰
- 效能優化（20%）：尖峰延遲改善
- 創新性（10%）：自動擴縮


## Case #14: 停機無例外 — 改善 Task.Wait 造成的 AggregateException

### Problem Statement（問題陳述）
- 業務場景：停機時常見 TaskCanceledException 被聚合拋出，雖不影響結果但影響可觀測性與清爽度。
- 技術挑戰：將阻塞呼叫改為可中止等待，避免硬 Wait。
- 影響範圍：噪音例外、誤判健康狀態。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Task.Wait/Result 阻塞等候造成聚合例外。
  2. BlockingCollection.TryTake 以固定 Timeout 迴圈而非 token 中止。
  3. Host.StopAsync 未正確串聯到所有等待點。
- 深層原因：
  - 架構層面：混用同步/非同步等待。
  - 技術層面：未傳遞 CancellationToken。
  - 流程層面：停機流程未整合等待點。

### Solution Design（解決方案設計）
- 解決策略：全鏈路改用 await + token；BlockingCollection 使用 GetConsumingEnumerable(token)；所有 Delay/IO 均傳遞 token。

- 實施步驟：
  1. 非同步化
     - 實作細節：移除 Task.Wait/Result，改 await
     - 所需資源：C# async/await
     - 預估時間：0.5 天
  2. 可中止等待
     - 實作細節：Delay/ReadAsync/GetConsumingEnumerable 皆傳 token
     - 所需資源：CancellationToken
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 不用 Task.Wait，改用 await，並傳入 token
await Task.Delay(wait, stoppingToken);

// BlockingCollection 可中止枚舉
foreach (var job in queue.GetConsumingEnumerable(stoppingToken))
{
    // ...
}
```

- 實際案例：PR5/PR6/PR7 停機時有零星 AggregateException；建議此優化
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：停機時例外訊息噴出
  - 改善後：停機乾淨、日誌整潔
  - 改善幅度：質性改善

Learning Points（學習要點）
- 核心知識點：
  - 同步/非同步混用的陷阱
  - 停機可中止等待
- 技能要求：
  - 必備技能：async/await
  - 進階技能：全鏈路傳遞 token
- 延伸思考：
  - 在多層呼叫的傳遞與取消語義

Practice Exercise（練習題）
- 基礎練習：消除所有 Task.Wait
- 進階練習：為隊列消費加入 token
- 專案練習：建置停機清單檢查器，保證所有等待點可中止

Assessment Criteria（評估標準）
- 功能完整性（40%）：停機無例外
- 程式碼品質（30%）：async 一致性
- 效能優化（20%）：等待合理
- 創新性（10%）：停機診斷工具


## Case #15: 工作者數量調參 — 超過 ProcessLockedJob 的內部並發限制

### Problem Statement（問題陳述）
- 業務場景：ProcessLockedJob 內部並發上限 5，但工作執行緒不只執行 Process，還有等待/入列等操作。
- 技術挑戰：如何找到最佳工作者數量，而非被 5 這個數字誤導。
- 影響範圍：吞吐/EFFIC 指標。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 誤認為工作者數量 = ProcessLockedJob 內部上限。
  2. 忽略等待/鎖定也是佔用。
- 深層原因：
  - 架構層面：缺少系統性調參。
  - 技術層面：無基準與對照實驗。
  - 流程層面：未長時間觀測。

### Solution Design（解決方案設計）
- 解決策略：以指標驅動（Avg/Stdev/COST）測試不同工作者數（如 5/10/15），選取整體最優；實測作者最終方案為 10 條。

- 實施步驟：
  1. 調參實驗
     - 實作細節：固定其他參數，掃描工作者數
     - 所需資源：統計/報表
     - 預估時間：0.5 天
  2. 設定最優值
     - 實作細節：留可配置，預設為實測最優
     - 所需資源：配置管理
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 啟動 N 條處理執行緒（作者用 10）
for (int i = 0; i < processThreads; i++)
    new Thread(ProcessThread).Start();
```

- 實際案例：作者最終方案選 10 條，EFFIC 全場最佳
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：工作者數量不足，EFFIC 偏高
  - 改善後：EFFIC 顯著下降
  - 改善幅度：質性為顯著

Learning Points（學習要點）
- 核心知識點：
  - 指標導向調參
  - 不同階段的佔用分析
- 技能要求：
  - 必備技能：基準測試
  - 進階技能：自動化掃參
- 延伸思考：
  - 依機器規格自適應調參

Practice Exercise（練習題）
- 基礎練習：5/10/15 工作者比較
- 進階練習：自動掃參腳本
- 專案練習：隨機尖峰下的掃參

Assessment Criteria（評估標準）
- 功能完整性（40%）：可配置
- 程式碼品質（30%）：參數化清晰
- 效能優化（20%）：EFFIC 降低
- 創新性（10%）：自動化


## Case #16: 以 QueryJob/QueryList 次數為目標的成本最小化

### Problem Statement（問題陳述）
- 業務場景：COST_SCORE = QueryList x100 + AcquireFailure x10 + QueryJob x1；需以此式為目標函數最小化。
- 技術挑戰：平衡三者次數，避免單一面向過度優化。
- 影響範圍：DB 成本、整體吞吐。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. QueryList 次數極貴（x100）。
  2. Acquire 失敗居中（x10）。
  3. QueryJob 便宜（x1），可當先驗。
- 深層原因：
  - 架構層面：掃描節奏不當導致 QueryList 過多。
  - 技術層面：未先驗導致 Acquire 失敗多。
  - 流程層面：無指標導向的微調。

### Solution Design（解決方案設計）
- 解決策略：對齊 MinPrepareTime 的掃描週期 + 先驗 QueryJob + 去同步化降低 Acquire 撞鎖。

- 實施步驟：
  1. 控制 QueryList
     - 實作細節：每輪涵蓋 MinPrepareTime，動態補償
     - 所需資源：Stopwatch
     - 預估時間：0.5 天
  2. 降低 Acquire 失敗
     - 實作細節：先驗 QueryJob + 抖動
     - 所需資源：Random
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 以 QueryJob 當便宜先驗，避免昂貴 Acquire 失敗
var j = repo.GetJob(job.Id);
if (j.State == 0 && repo.AcquireJobLock(job.Id))
{
    // ...
}
```

- 實際案例：PR3（jwchen-dev）COST_SCORE 全場最低；Baseline COST 119360 作為對照
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：COST 高（Baseline 119360）
  - 改善後：COST 降至全場最低（PR3）
  - 改善幅度：等級顯著下降

Learning Points（學習要點）
- 核心知識點：
  - 成本函數分解與優先順序
  - 指標回饋驅動迭代
- 技能要求：
  - 必備技能：記錄與分析
  - 進階技能：A/B 測試
- 延伸思考：
  - 動態切換策略（低流量 vs 高流量）

Practice Exercise（練習題）
- 基礎練習：加入成本統計儀表
- 進階練習：實驗不同掃描週期與先驗策略
- 專案練習：以成本函數自動調整參數

Assessment Criteria（評估標準）
- 功能完整性（40%）：成本統計完整
- 程式碼品質（30%）：易於實驗
- 效能優化（20%）：COST 降低
- 創新性（10%）：自動化調優


## Case #17: 防偷跑 — 嚴守 RunAt 前不執行（Early Exec=0）

### Problem Statement（問題陳述）
- 業務場景：不可在 RunAt 到達前執行任務，否則不符合規格；但提前鎖定或錯誤計時可能導致偷跑。
- 技術挑戰：在提前鎖定策略下仍嚴格控制執行點。
- 影響範圍：規格違反（Fail）、被排除評分。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 僅判斷可鎖即可執行，未等待至 RunAt。
  2. 計時誤差或忙等導致提前觸發。
- 深層原因：
  - 架構層面：缺「準點閘口」。
  - 技術層面：時間計算與等待未校正。
  - 流程層面：缺自動化 Early Exec 檢測。

### Solution Design（解決方案設計）
- 解決策略：即便已鎖定，仍需 Delay 到 RunAt 才入列到處理；加入 Early Exec 監控。

- 實施步驟：
  1. 準點等待
     - 實作細節：if (now < runAt) await Delay(runAt-now, token)
     - 所需資源：CancellationToken
     - 預估時間：0.5 天
  2. 監控 Early Exec
     - 實作細節：若 Process 時間 < RunAt 記錄違規
     - 所需資源：Log/報表
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
if (DateTime.Now < job.RunAt)
    await Task.Delay(job.RunAt - DateTime.Now, token); // 嚴守準點
queue.Add(job); // 到這裡才可 ProcessLockedJob
```

- 實際案例：PR4（LeviDemo）因 Early Exec 大量發生而 FAIL
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：Early Exec > 0（FAIL）
  - 改善後：Early Exec = 0（PASS）
  - 改善幅度：由 FAIL 轉 PASS

Learning Points（學習要點）
- 核心知識點：
  - 規格邊界檢查
  - 時間等待語義
- 技能要求：
  - 必備技能：Delay 與 token
  - 進階技能：指標告警
- 延伸思考：
  - 系統時間漂移如何影響準點？

Practice Exercise（練習題）
- 基礎練習：加入 Early Exec 計數器
- 進階練習：模擬時鐘偏移測試
- 專案練習：加入 NTP 漂移保護（容差）

Assessment Criteria（評估標準）
- 功能完整性（40%）：Early Exec=0
- 程式碼品質（30%）：時間處理嚴謹
- 效能優化（20%）：無副作用
- 創新性（10%）：時間漂移防護


## Case #18: 測試流程與評分體系（可靠度 + 成本/精準 指標）

### Problem Statement（問題陳述）
- 業務場景：需在統一測試框架下公平比較不同方案的優劣。
- 技術挑戰：同時驗證可靠度（Exactly-once、延遲門檻）與「成本/精準」兩大面向。
- 影響範圍：研發評估、決策品質、可持續優化。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺統一測試負載與資料初始化流程。
  2. 無成本/精準的量化計分。
  3. 無 HA 測試（重啟/中斷）。
- 深層原因：
  - 架構層面：無觀測驅動。
  - 技術層面：無自動化腳本。
  - 流程層面：缺績效基準。

### Solution Design（解決方案設計）
- 解決策略：建立統一測試程式（10 分鐘、尖峰插入、隨機插入、即時插入），可靠度先決（全部完成、MinPrepareTime、MaxDelayTime），再以 COST/EFFIC 計分；HATEST 驗證 HA。

- 實施步驟：
  1. 基準測試
     - 實作細節：初始化 DB、啟動 5 實例、跑滿 10 分鐘
     - 所需資源：既有測試程式
     - 預估時間：1 天
  2. HATEST
     - 實作細節：隨機 Stop/Start，各自 10~30 秒間隔
     - 所需資源：Host 控制器
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 產生測試負載（節錄）
TimeSpan duration = TimeSpan.FromMinutes(10);
DateTime since = DateTime.Now.AddSeconds(10);
// 每 3 秒 1 筆、每 13 秒 20 筆、1~3 秒隨機 1 筆、實時每 1~3 秒預約 10 秒後執行
```

- 實際案例：各 PR 與作者方案皆依此流程評分
- 實作環境：同 Case #1
- 實測數據：
  - 改善前：無法比較、定性為主
  - 改善後：有 COST/EFFIC 分數、HATEST PASS/FAIL
  - 改善幅度：決策品質顯著提升

Learning Points（學習要點）
- 核心知識點：
  - 測試設計與評分
  - HA 測試的重要性
- 技能要求：
  - 必備技能：自動化測試
  - 進階技能：負載建模
- 延伸思考：
  - 不同硬體/雲環境的可比性如何維繫？

Practice Exercise（練習題）
- 基礎練習：跑滿 10 分鐘測試並出報表
- 進階練習：修改插入分布觀測分數變化
- 專案練習：建立 CI 中自動 Benchmark 工作

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試可重現
- 程式碼品質（30%）：腳本清晰
- 效能優化（20%）：指標可比較
- 創新性（10%）：自動化與報表化



案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 4（忙等轉 Delay）
  - Case 12（索引設計）
  - Case 14（停機無例外）
- 中級（需要一定基礎）
  - Case 1（基準解）
  - Case 3（先驗狀態）
  - Case 5（中央隊列）
  - Case 6（HA 與停機）
  - Case 8（去同步化抖動）
  - Case 9（窗口對齊）
  - Case 10（Channel）
  - Case 11（fetch 即鎖）
  - Case 13（尖峰消化）
  - Case 15（工作者調參）
  - Case 16（成本最小化）
  - Case 17（防偷跑）
  - Case 18（測試與評分）
- 高級（需要深厚經驗）
  - Case 2（最終解：提前鎖+抖動+準點等待）

2) 按技術領域分類
- 架構設計類：Case 2, 5, 6, 7, 11, 13, 18
- 效能優化類：Case 2, 3, 8, 9, 10, 12, 13, 15, 16
- 整合開發類：Case 6, 10, 18
- 除錯診斷類：Case 14, 17
- 安全防護類：（本主題較少傳統安全面向；可將 Exactly-once 與規格遵循視為一致性「安全」）Case 6, 17

3) 按學習目標分類
- 概念理解型：Case 1, 12, 18
- 技能練習型：Case 4, 5, 6, 9, 10, 14
- 問題解決型：Case 2, 3, 7, 8, 11, 13, 15, 16, 17
- 創新應用型：Case 2, 8, 16, 18



案例關聯圖（學習路徑建議）
- 先學哪些案例？
  - 入口基礎：Case 1（基準）→ Case 12（索引）→ Case 4（等待原語）
  - 再學：Case 5（中央隊列）→ Case 6（HA/停機）→ Case 18（測試/評分）
- 依賴關係：
  - Case 2（最終解）依賴 Case 3/5/6/7/8/9/15/16 的組合技巧
  - Case 11（fetch 即鎖）需搭配 Case 6 的停機排空策略
  - Case 10（Channel）可替代 Case 5 的 BlockingCollection，但需先理解生消模式
  - Case 17（防偷跑）依賴 Case 4 的準點等待
- 完整學習路徑：
  1) Case 1 → 12 → 4（建立基礎）
  2) Case 5 → 6 → 18（隊列、HA、測試體系）
  3) Case 3 → 8 → 9（成本與抖動與窗口）
  4) Case 11 → 7 → 15 → 16（鎖定策略與調參）
  5) Case 13（尖峰處理）→ Case 10（Channel 可選）
  6) Case 17（規格邊界）
  7) 彙整至 Case 2（最終解），以同一測試體系驗證並與基準對照

以上 18 個案例覆蓋了文中出現的所有關鍵問題、根因、方案與效益指標，並提供可操作的實作與評測路徑，便於教學、實戰練習與能力評估。