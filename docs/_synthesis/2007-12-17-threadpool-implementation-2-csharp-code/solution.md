---
layout: synthesis
title: "ThreadPool 實作 #2. 程式碼 (C#)"
synthesis_type: solution
source_post: /2007/12/17/threadpool-implementation-2-csharp-code/
redirect_from:
  - /2007/12/17/threadpool-implementation-2-csharp-code/solution/
postid: 2007-12-17-threadpool-implementation-2-csharp-code
---

以下為基於原文內容，提取並結構化的 16 個可用於實戰教學的解決方案案例。每一案皆聚焦於文章中明確提出的需求、關鍵設計與程式片段，並補足可操作的實作步驟、關鍵代碼與教學用的示例量測指標（示意數據，非來源文章的實測）。

注意：以下「實測數據」為教學示例（示意），用於幫助建立可量測的學習目標與評估方式；原文未提供實際統計數據。

## Case #1: 可組態化的自訂 ThreadPool 架設

### Problem Statement（問題陳述）
業務場景：在伺服器端或批次處理場景中，系統需要可控的併發度，以避免預設 .NET ThreadPool 的全域策略影響特定工作負載。團隊希望依工作性質調整 worker thread 數量、優先權及 idle timeout，並在程式碼層面明確掌握生命週期與關閉策略。
技術挑戰：.NET 預設 ThreadPool 難以針對個別工作負載設定 thread 優先權與 idle 回收等細節；需設計一個可組態且易用的 SimpleThreadPool。
影響範圍：若不可組態，易造成latency不可控、資源搶奪、在高峰時段 CPU/記憶體壓力不均。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 預設 ThreadPool 為全域共享，無法針對單一路徑設定專屬策略。
2. 缺乏對 worker 優先權與 idle timeout 的細緻控制。
3. 缺少可預期、可關閉（End/Cancel）的生命週期管理介面。
深層原因：
- 架構層面：共用 ThreadPool 對異質工作負載不友善。
- 技術層面：無獨立的 pool 實作封裝。
- 流程層面：測試與部署時無法針對不同場景微調並量測成效。

### Solution Design（解決方案設計）
解決策略：實作 SimpleThreadPool 類別，提供可設定的 thread 上限、優先權、idle timeout 與安全佇列閾值；暴露 QueueUserWorkItem、EndPool、CancelPool 等 API，並以事件同步原語管理 worker 生命週期。

實施步驟：
1. 定義可組態的建構式與欄位
- 實作細節：保存 _maxWorkerThreadCount、_priority、_maxWorkerThreadTimeout 等設定。
- 所需資源：C#, System.Threading
- 預估時間：1 小時
2. 實作 CreateWorkerThread 與 DoWorkerThread
- 實作細節：啟動背景執行緒，掛上指定 ThreadPriority。
- 所需資源：C#, Thread 類別
- 預估時間：2 小時
3. 提供 API（QueueUserWorkItem/EndPool/CancelPool/Dispose）
- 實作細節：確保 API 簡潔且具阻斷式等待或快速取消語意。
- 所需資源：ManualResetEvent/AutoResetEvent
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
public class SimpleThreadPool : IDisposable
{
    private readonly int _maxWorkerThreadCount;
    private readonly ThreadPriority _priority;
    private readonly int _maxWorkerThreadTimeout;

    public SimpleThreadPool(int threads, ThreadPriority priority, int idleTimeoutMs = 30000)
    {
        _maxWorkerThreadCount = threads;
        _priority = priority;
        _maxWorkerThreadTimeout = idleTimeoutMs;
        // 可在此預先建立初始 worker（可選）
    }

    private void CreateWorkerThread()
    {
        var t = new Thread(DoWorkerThread)
        {
            IsBackground = true,
            Priority = _priority,
            Name = $"STP-Worker-{Guid.NewGuid():N}"
        };
        lock (_workerThreads) _workerThreads.Add(t);
        t.Start();
    }

    public void Dispose() => EndPool(false);
}
```

實際案例：文章樣例以 SimpleThreadPool(2, BelowNormal) 執行 25 筆工作後 EndPool()。
實作環境：C#、.NET Framework 2.0+ 或 .NET 6+（Thread API 皆可用）
實測數據（示意）：
改善前：單執行緒處理 25 個 100ms 任務，總耗時 ≈ 2.5s
改善後：2 個 worker 處理，總耗時 ≈ 1.3s
改善幅度：≈ 48% 總時間下降

Learning Points（學習要點）
核心知識點：
- 自訂 ThreadPool 的必要性與設計責任
- ThreadPriority 的應用場景
- 可組態化對營運場景的價值
技能要求：
- 必備技能：C# Thread、委派、基本同步原語
- 進階技能：多執行緒設計與可測試性設計
延伸思考：
- 能否用 TaskScheduler 自訂替代？
- 與預設 ThreadPool 共存的策略？
- 如何熱更新組態？
Practice Exercise（練習題）
- 基礎：建立 SimpleThreadPool，提交 10 個工作並結束（30 分）
- 進階：加入 idle timeout 設定並測試回收（2 小時）
- 專案：封裝成 NuGet 套件與範例專案（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可組態、可啟動與關閉
- 程式碼品質（30%）：清晰 API、封裝、註解
- 效能優化（20%）：相對單執行緒有可量測改善
- 創新性（10%）：可擴展與異常處理設計

## Case #2: 依 Job Queue 安全範圍動態擴編 Worker

### Problem Statement（問題陳述）
業務場景：服務高峰期，請求突增導致任務在佇列堆積，單純固定 worker 數量無法消化高峰，需在安全範圍外彈性擴編至上限以降低等待時間。
技術挑戰：如何在不過度擴編（避免上下文切換風暴）且不延遲過久間取得平衡？
影響範圍：隊列積壓將造成 SLA 超時、使用者體感延遲上升。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. worker 數量固定，無法適應流量波動。
2. 佇列缺乏安全閾值與容量監控。
3. 信號與建線邏輯不一致，可能造成擴編延遲。
深層原因：
- 架構層面：缺乏彈性伸縮策略。
- 技術層面：未衡量 queue 長度與 worker 數關係。
- 流程層面：缺乏壓力測試與告警閾值。

### Solution Design（解決方案設計）
解決策略：引入 queue 安全範圍（soft threshold）。當 Count 超過閾值且未達最大 worker 時，動態建立新的 worker；同時維持上限約束以防過度擴編。

實施步驟：
1. 新增安全閾值欄位與建構式參數
- 實作細節：_queueSafeThreshold，並保留 _maxWorkerThreadCount
- 所需資源：C#
- 預估時間：30 分
2. 在入列時觸發擴編判斷
- 實作細節：入列操作與建線判斷以同一把鎖保護
- 所需資源：lock、Queue<T>
- 預估時間：1 小時
3. 壓測與調閾值
- 實作細節：以不同閾值校準等待時間與 CPU
- 所需資源：Benchmark 工具
- 預估時間：1.5 小時

關鍵程式碼/設定：
```csharp
private readonly int _queueSafeThreshold;

public SimpleThreadPool(int threads, ThreadPriority priority, int idleTimeoutMs, int queueSafeThreshold)
{
    _maxWorkerThreadCount = threads;
    _priority = priority;
    _maxWorkerThreadTimeout = idleTimeoutMs;
    _queueSafeThreshold = queueSafeThreshold;
}

public bool QueueUserWorkItem(WaitCallback callback, object state)
{
    if (_stop_flag) return false;
    var wi = new WorkItem { callback = callback, state = state };

    lock (_workitems)
    {
        _workitems.Enqueue(wi);
        if (_workitems.Count > _queueSafeThreshold && _workerThreads.Count < _maxWorkerThreadCount)
            CreateWorkerThread();

        // 僅在從 0 -> 1 時通知（詳見 Case #12）
        if (_workitems.Count == 1) enqueueNotify.Set();
    }
    return true;
}
```

實際案例：文章入列時檢查 Count 並 CreateWorkerThread 的設計思想。
實作環境：C#、.NET Framework/.NET
實測數據（示意）：
改善前：峰值時平均等待 120ms
改善後：安全閾值=5、最大 worker=4 時平均等待 45ms
改善幅度：≈ 62.5%

Learning Points（學習要點）
- 安全閾值（soft limit）與上限（hard limit）差異
- 擴編與鎖定範圍的一致性
- 以壓測調參
技能要求：
- 必備技能：基礎多執行緒、lock
- 進階技能：佇列負載建模與壓測
延伸思考：
- 可否根據歷史吞吐自動調整閾值？
- 高水位/低水位的回滾策略？
- 加入自動縮編策略？
Practice Exercise
- 基礎：加入 queueSafeThreshold 並測試擴編（30 分）
- 進階：利用 Stopwatch 量測等待時間，調不同閾值（2 小時）
- 專案：壓測腳本（如 BenchmarkDotNet 或自製）（8 小時）
Assessment Criteria
- 功能完整性（40%）：能擴編且不超過上限
- 程式碼品質（30%）：臨界條件處理
- 效能優化（20%）：等待時間可量測下降
- 創新性（10%）：參數自動化調整想法

## Case #3: Idle Timeout 與 Worker 回收

### Problem Statement（問題陳述）
業務場景：低谷期不需要維持大量空轉 worker；需在閒置超過 idle timeout 後自動回收，釋放資源。
技術挑戰：在不流失可用性的前提下，讓 worker 能「被喚醒」或「逾時自我結束」。
影響範圍：空耗 CPU/記憶體，降低效能/增加成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無阻塞等待，worker 會忙等。
2. 無 idle timeout，worker 不會自我回收。
3. 無隊列變化信號，worker 無法感知新任務。
深層原因：
- 架構層面：缺少生命週期策略。
- 技術層面：未善用 WaitHandle 超時功能。
- 流程層面：未定義 idle 策略與量測指標。

### Solution Design（解決方案設計）
解決策略：在 DoWorkerThread 中使用 WaitHandle.WaitOne(timeout)；被 Set 即喚醒，有新工作處理；逾時則 break 離場並從 worker 集合移除。

實施步驟：
1. 引入等待與逾時機制
- 實作細節：WaitOne(_maxWorkerThreadTimeout, exitContext:true)
- 所需資源：ManualResetEvent 或 AutoResetEvent
- 預估時間：30 分
2. 回收時移除 worker
- 實作細節：在 finally 或迴圈外移除 Thread.CurrentThread
- 所需資源：lock(_workerThreads)
- 預估時間：30 分
3. 壓測 idle 策略
- 實作細節：延遲不入列，觀察 worker 數變化
- 所需資源：Stopwatch, PerfMon
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
private void DoWorkerThread()
{
    while (true)
    {
        while (true)
        {
            WorkItem item = null;
            lock (_workitems)
            {
                if (_workitems.Count > 0) item = _workitems.Dequeue();
                else break;
            }
            try { item.Execute(); } catch { /* log */ }
            if (_cancel_flag) break;
        }

        if (_stop_flag || _cancel_flag) break;

        // 逾時離場
        if (!enqueueNotify.WaitOne(_maxWorkerThreadTimeout, true))
            break;
        // 被喚醒則繼續 loop
    }
    lock (_workerThreads) _workerThreads.Remove(Thread.CurrentThread);
}
```

實際案例：原文以 WaitOne(timeout) 控制 idle 回收。
實作環境：C#、.NET
實測數據（示意）：
改善前：常駐 4 個 worker，CPU idle 仍 8~10%
改善後：5 分鐘無新任務 -> 自動回收至 0，CPU idle ≈ 1~2%
改善幅度：CPU 空耗下降約 70~80%

Learning Points
- 以阻塞等待替代忙等
- idle timeout 與回收動作的安全性
- 退出時的集合一致性
技能要求：
- 必備：WaitHandle 用法
- 進階：多執行緒清理流程
延伸思考：
- Idle timeout 是否需分級（短期/長期）？
- 回收/擴編震盪如何避免？
- 逾時後是否快取 thread 物件（Thread reuse）？
Practice Exercise
- 基礎：設定 3s idle timeout 觀察回收（30 分）
- 進階：記錄 worker 數時間序列圖（2 小時）
- 專案：加入統計面板（8 小時）
Assessment Criteria
- 功能（40%）：確實逾時回收
- 品質（30%）：清理不遺漏
- 效能（20%）：空耗下降
- 創新（10%）：平滑化策略

## Case #4: 阻塞等待取代忙等（WaitHandle 喚醒）

### Problem Statement（問題陳述）
業務場景：以輪詢方式檢查佇列（忙等）容易造成高 CPU 使用與電力浪費；需在新任務抵達時才喚醒 worker。
技術挑戰：正確使用 WaitHandle 與 Set 通知，避免 CPU spin。
影響範圍：CPU 空耗高、散熱/電源成本上升。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無事件驅動機制（僅輪詢）。
2. 沒有入列時通知。
3. 沒有逾時離場。
深層原因：
- 架構層面：缺乏生產者-消費者同步。
- 技術層面：不熟悉 WaitOne/Set 模式。
- 流程層面：缺少效能觀測。

### Solution Design（解決方案設計）
解決策略：用 ManualResetEvent/AutoResetEvent 搭配 WaitOne；入列後 Set 喚醒 worker；worker 無任務時 WaitOne 阻塞至被喚醒或逾時。

實施步驟：
1. 建立同步原語
- 實作細節：private ManualResetEvent enqueueNotify = new(false);
- 所需資源：System.Threading
- 預估時間：10 分
2. 入列時 Set
- 實作細節：Enqueue 後 enqueueNotify.Set()
- 所需資源：C#
- 預估時間：10 分
3. worker WaitOne
- 實作細節：無任務時呼叫 WaitOne(timeout)
- 所需資源：C#
- 預估時間：10 分

關鍵程式碼/設定：
```csharp
// 入列通知
lock (_workitems)
{
    _workitems.Enqueue(wi);
    enqueueNotify.Set();  // 喚醒等待中的 worker
}

// worker 等待
if (!enqueueNotify.WaitOne(_maxWorkerThreadTimeout, true))
    break; // 逾時回收
```

實際案例：原文在入列後呼叫 Set，喚醒 WaitOne 中的 worker。
實作環境：C#、.NET
實測數據（示意）：
改善前：忙等輪詢 CPU ≈ 30%
改善後：事件喚醒模式 CPU ≈ 3~5%
改善幅度：CPU 空耗下降 ≈ 80~90%

Learning Points
- 事件驅動的生產者-消費者模型
- WaitOne/Set 的語意
- 逾時行為與回收
技能要求：
- 必備：WaitHandle 基礎
- 進階：不同事件類型的選擇
延伸思考：
- AutoResetEvent vs ManualResetEvent 的差異？
- 喚醒範圍過大會否產生「羊群效應」？
Practice Exercise
- 基礎：將忙等版改為 WaitOne/Set（30 分）
- 進階：計算 CPU 降幅（2 小時）
- 專案：繪製 Wait/Run 時間佔比（8 小時）
Assessment Criteria
- 功能（40%）：阻塞等待正常
- 品質（30%）：正確喚醒
- 效能（20%）：CPU 降低
- 創新（10%）：觀測與可視化

## Case #5: ManualResetEvent 的 Reset 策略與 AutoResetEvent 替代

### Problem Statement（問題陳述）
業務場景：使用 ManualResetEvent.Set 喚醒 worker，但若未適時 Reset，事件可能持續為 signaled，造成 worker 立即返回 WaitOne、迴圈空轉。
技術挑戰：設計正確的 Reset 時機或改用 AutoResetEvent。
影響範圍：CPU 浪費、工作爭搶帶來的喚醒風暴。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. ManualResetEvent 在 Set 後持續為 signaled。
2. 未 Reset 導致 WaitOne 立即返回。
3. 多 worker 覺醒造成空回圈。
深層原因：
- 架構層面：喚醒策略未定義。
- 技術層面：事件類型語意誤用。
- 流程層面：缺少壓測與觀測。

### Solution Design（解決方案設計）
解決策略：兩種選擇
- A. ManualResetEvent：在「確認佇列為空」時做 Reset，再進入等待。
- B. AutoResetEvent：Set 只喚醒一個等待者，由 OS 決定哪個覺醒，避免持續 signaled。

實施步驟：
1. 採用 ManualResetEvent + Reset
- 實作細節：在入列設為 Set，在無任務準備等待前 Reset
- 所需資源：ManualResetEvent
- 預估時間：30 分
2. 或改用 AutoResetEvent
- 實作細節：替換型別與語意
- 所需資源：AutoResetEvent
- 預估時間：20 分
3. 壓測覺醒行為
- 實作細節：觀察喚醒數與空轉
- 所需資源：記錄工具
- 預估時間：1 小時

關鍵程式碼/設定（ManualResetEvent Reset 策略）：
```csharp
// worker：準備等待前 Reset（僅在佇列為空時）
bool shouldWait;
lock (_workitems)
{
    shouldWait = _workitems.Count == 0;
    if (shouldWait) enqueueNotify.Reset(); // 防止已 signaled 導致立即返回
}
if (shouldWait && !enqueueNotify.WaitOne(_maxWorkerThreadTimeout, true)) break;

// AutoResetEvent 替代：
// private AutoResetEvent enqueueNotify = new(false);
// 不需要手動 Reset；每次 Set 喚醒一個等待者
```

實際案例：原文提及選用 ManualResetEvent 並引出「誰該醒來」議題。
實作環境：C#、.NET
實測數據（示意）：
Manual 模式（未 Reset）：CPU 偶發飆高至 ≈ 20%
Manual+Reset 或 Auto：CPU 降至 ≈ 3~5%
改善幅度：CPU 峰值壓制約 75~85%

Learning Points
- 事件類型的優劣與使用場合
- Reset 時機對行為的影響
- 喚醒風暴的識別與避免
技能要求：
- 必備：Manual/AutoResetEvent 差異
- 進階：正確 Reset 與覺醒控制
延伸思考：
- 何時要主動喚醒所有 worker？
- 以 Channel/BlockingCollection 取代？
Practice Exercise
- 基礎：手動 Reset 策略（30 分）
- 進階：切換 AutoResetEvent 並比較行為（2 小時）
- 專案：壓測兩種策略（8 小時）
Assessment Criteria
- 功能（40%）：無空轉
- 品質（30%）：代碼簡潔/一致
- 效能（20%）：CPU 峰值降低
- 創新（10%）：策略比較報告

## Case #6: 讓 OS 決定「誰來搶工」的排程策略

### Problem Statement（問題陳述）
業務場景：多個 worker 同時等待新任務，只有一個工作進來；不希望自訂排程決策，而是交由 OS 決定哪個 worker 去執行，以減少自製排程邏輯的複雜度與風險。
技術挑戰：喚醒策略需避免自搶與競態，同時確保只有一個 worker 取到同一份工作。
影響範圍：錯誤的排程可能導致重複執行或長時間爭鎖。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 試圖由 thread pool 手動指派 worker。
2. 錯誤的同步導致重複取用。
3. 喚醒策略未設計好。
深層原因：
- 架構層面：不必要的自行排程。
- 技術層面：忽略 OS 調度器的既有能力。
- 流程層面：未定義簡化原則。

### Solution Design（解決方案設計）
解決策略：使用事件喚醒等待中的 worker，並以鎖保護佇列取用，讓 OS 決定覺醒順序；避免在 pool 層做「人為分配」。

實施步驟：
1. 入列後呼叫 Set（喚醒）
- 實作細節：不針對特定 worker 指派
- 所需資源：WaitHandle
- 預估時間：10 分
2. 以 lock 保護 Dequeue
- 實作細節：確保一次只有一人取到工作
- 所需資源：C#
- 預估時間：10 分
3. 壓測覺醒順序
- 實作細節：驗證無重複執行
- 所需資源：記錄工具
- 預估時間：40 分

關鍵程式碼/設定：
```csharp
// 喚醒所有等待者，由 OS 決定哪個先執行
enqueueNotify.Set();

WorkItem item = null;
lock (_workitems)
{
    if (_workitems.Count > 0)
        item = _workitems.Dequeue(); // 鎖保證唯一取用
}
```

實際案例：原文明確要求「由 OS 決定」覺醒的 worker。
實作環境：C#、.NET
實測數據（示意）：
改善前：自訂分配易出錯（重複執行率 ≈ 1% 測試樣本）
改善後：交由 OS + 鎖保護 -> 重複率 0、平均等待更穩定
改善幅度：錯誤率下降到 0

Learning Points
- 善用 OS 調度器
- 佇列的原子取用是核心
- 簡化策略有效降低錯誤
技能要求：
- 必備：lock、佇列操作
- 進階：設計簡化原則
延伸思考：
- 若要實作優先級佇列又如何保有簡化性？
Practice Exercise
- 基礎：以 OS 決策的喚醒模式（30 分）
- 進階：多 worker 壓測去重（2 小時）
- 專案：加入優先序佇列（8 小時）
Assessment Criteria
- 功能（40%）：無重複取用
- 品質（30%）：簡潔正確
- 效能（20%）：穩定度
- 創新（10%）：策略與驗證

## Case #7: 佇列入列/出列的執行緒安全

### Problem Statement（問題陳述）
業務場景：多個 worker 與多個生產者同時操作佇列，若未正確同步，可能導致資料競態或例外。
技術挑戰：如何在入列與出列兩端都保證一致性與正確性。
影響範圍：會造成 crash、重複/遺失工作。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Enqueue 未鎖定，Dequeue 只局部鎖定。
2. Count 檢查與實際操作非原子。
3. 線程間可同時修改集合。
深層原因：
- 架構層面：缺少明確臨界區定義。
- 技術層面：對非 thread-safe 集合誤用。
- 流程層面：缺少並發測試。

### Solution Design（解決方案設計）
解決策略：以同一把鎖保護 Queue 的所有讀寫；或改採 ConcurrentQueue 並以事件觸發代替 Count 基於鎖的判斷。

實施步驟：
1. 適用 lock 同步所有集合操作
- 實作細節：入列、出列、Count、Clear 皆需鎖
- 所需資源：lock
- 預估時間：30 分
2. 或改用 ConcurrentQueue
- 實作細節：TryDequeue 迴圈
- 所需資源：System.Collections.Concurrent
- 預估時間：1 小時
3. 壓測並發正確性
- 實作細節：啟動多 producer/consumer
- 所需資源：測試程式
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 鎖保護所有佇列操作
lock (_workitems)
{
    _workitems.Enqueue(wi);
    if (_workitems.Count == 1) enqueueNotify.Set();
}

// 消費端
WorkItem item = null;
lock (_workitems)
{
    if (_workitems.Count > 0)
        item = _workitems.Dequeue();
}
```

實際案例：原文 Dequeue 以 lock 保護；入列亦需相同策略。
實作環境：C#、.NET
實測數據（示意）：
改善前：並發壓測下偶發 InvalidOperationException 或丟件
改善後：0 例外，丟件率 0
改善幅度：正確性顯著提高

Learning Points
- 資料結構的執行緒安全使用
- Count 判斷與操作需同鎖
- 可替代為 Concurrent 集合
技能要求：
- 必備：lock、集合操作
- 進階：無鎖/併發集合
延伸思考：
- 多隊列/分片以降低鎖競爭？
Practice Exercise
- 基礎：以 lock 完整保護（30 分）
- 進階：替換 ConcurrentQueue（2 小時）
- 專案：對比壓測（8 小時）
Assessment Criteria
- 功能（40%）：無資料競態
- 品質（30%）：臨界區清晰
- 效能（20%）：鎖競爭控制
- 創新（10%）：替代設計比較

## Case #8: Worker 集合（_workerThreads）一致性與清理

### Problem Statement（問題陳述）
業務場景：動態建立/回收 worker，需維護 _workerThreads 的準確性，以利監控與優雅關閉。
技術挑戰：多處讀寫集合且無鎖，導致列舉或移除時發生例外或不一致。
影響範圍：造成 End/Cancel 阻塞、遺漏 thread 清理。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Add/Remove 未鎖定。
2. 關閉時列舉與修改併發進行。
3. Thread 物件引用外洩。
深層原因：
- 架構層面：缺少 thread 管理封裝。
- 技術層面：集合並發誤用。
- 流程層面：未測試極端關閉場景。

### Solution Design（解決方案設計）
解決策略：用同一鎖保護 _workerThreads 的增刪列舉；或改用 ConcurrentBag + 唯一 ID 映射；避免外部直接存取集合。

實施步驟：
1. 鎖保護增刪改查
- 實作細節：Create 時 Add、回收時 Remove 皆鎖定
- 所需資源：lock
- 預估時間：20 分
2. 關閉時複製快照列舉
- 實作細節：ToArray() 在鎖中快照，鎖外 Join
- 所需資源：C#
- 預估時間：30 分
3. 測試關閉流程
- 實作細節：高併發入列後關閉
- 所需資源：測試程式
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
private readonly List<Thread> _workerThreads = new();

private void CreateWorkerThread()
{
    var t = new Thread(DoWorkerThread) { IsBackground = true, Priority = _priority };
    lock (_workerThreads) _workerThreads.Add(t);
    t.Start();
}

private void RemoveCurrentWorker()
{
    lock (_workerThreads) _workerThreads.Remove(Thread.CurrentThread);
}
```

實際案例：原文於結束時 Remove(Thread.CurrentThread)，需補齊鎖。
實作環境：C#、.NET
實測數據（示意）：
改善前：偶發 InvalidOperationException（集合被修改）
改善後：0 例外
改善幅度：穩定性大幅提升

Learning Points
- 集合操作一致性
- 關閉流程的快照技巧
- 封裝避免外部誤用
技能要求：
- 必備：lock 與集合
- 進階：快照與 Join 策略
延伸思考：
- 是否需要 thread-safe set（HashSet+鎖）？
Practice Exercise
- 基礎：加鎖增刪（30 分）
- 進階：快照關閉流程（2 小時）
- 專案：暴力壓測（8 小時）
Assessment Criteria
- 功能（40%）：無例外
- 品質（30%）：封裝良好
- 效能（20%）：鎖衝突低
- 創新（10%）：快照設計

## Case #9: EndPool 等待所有 Job 完成的同步機制

### Problem Statement（問題陳述）
業務場景：需要提供「等全部完成再關閉」的 API（EndPool），避免資料不一致或中斷任務。
技術挑戰：如何在多 worker 下準確判定「所有工作已完成」，並阻塞至完成。
影響範圍：若判斷不準，會提早退出導致漏處理。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未追蹤「待處理數」（包含隊列+執行中）。
2. 無同步事件代表「全部完成」。
3. 關閉旗標與完成判斷交互複雜。
深層原因：
- 架構層面：缺少完成屏障（completion barrier）。
- 技術層面：無原子計數。
- 流程層面：缺乏完成語意的測試。

### Solution Design（解決方案設計）
解決策略：以原子計數 pending 記錄總待處理數；入列 +1，工作完成 -1；當降為 0 時 Set 完成事件；EndPool 設 stop_flag，喚醒所有 worker 然後 Wait 完成事件。

實施步驟：
1. 新增 pending 與完成事件
- 實作細節：int _pending；ManualResetEvent _allDone
- 所需資源：Interlocked, WaitHandle
- 預估時間：40 分
2. 入列/完成時維護計數
- 實作細節：+1/-1 並在 0 時 Set
- 所需資源：C#
- 預估時間：40 分
3. EndPool 等待屏障
- 實作細節：設 stop_flag、Set 通知、Wait
- 所需資源：C#
- 預估時間：40 分

關鍵程式碼/設定：
```csharp
private int _pending = 0;
private ManualResetEvent _allDone = new(false);

public bool QueueUserWorkItem(WaitCallback cb, object state)
{
    if (_stop_flag) return false;
    var wi = new WorkItem { callback = cb, state = state };
    Interlocked.Increment(ref _pending);
    _allDone.Reset();
    lock (_workitems)
    {
        _workitems.Enqueue(wi);
        if (_workitems.Count == 1) enqueueNotify.Set();
    }
    return true;
}

private void CompleteOne()
{
    if (Interlocked.Decrement(ref _pending) == 0)
        _allDone.Set();
}

private void DoWorkerThread()
{
    // ... 取出 item 後
    try { item.Execute(); } finally { CompleteOne(); }
}

public void EndPool()
{
    _stop_flag = true;
    enqueueNotify.Set(); // 喚醒閒置 worker 退場
    _allDone.WaitOne();  // 等到所有工作完成
}
```

實際案例：原文提及 EndPool 需阻塞至處理完所有 job。
實作環境：C#、.NET
實測數據（示意）：
改善前：偶發提早關閉造成漏處理（1/1000 測試）
改善後：0 漏處理
改善幅度：正確性明顯提升

Learning Points
- 完成屏障與原子計數
- 等待語意的正確設計
- 關閉與處理的交織
技能要求：
- 必備：Interlocked、事件
- 進階：屏障與資源清理
延伸思考：
- 需要 per-item completion 回呼嗎？
Practice Exercise
- 基礎：加入 pending 與 _allDone（30 分）
- 進階：壓測 1e5 任務（2 小時）
- 專案：加入任務進度回報（8 小時）
Assessment Criteria
- 功能（40%）：正確等待
- 品質（30%）：計數正確
- 效能（20%）：無顯著開銷
- 創新（10%）：可觀測性

## Case #10: CancelPool 快速關閉（丟棄佇列中未執行任務）

### Problem Statement（問題陳述）
業務場景：遇到維運緊急狀況或關閉視窗，需快速取消：正在執行的可收尾，佇列中未執行的直接丟棄。
技術挑戰：如何安全地清空佇列、喚醒 worker 並結束執行？
影響範圍：若實作不當，可能造成卡死或重入問題。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. cancel_flag 未被 worker 觀察到。
2. 佇列清空與 worker 競爭。
3. 未喚醒等待中的 worker。
深層原因：
- 架構層面：缺少快速關閉路徑。
- 技術層面：旗標可見性與記憶體模型。
- 流程層面：未考慮中途取消。

### Solution Design（解決方案設計）
解決策略：設定 cancel_flag 後，鎖內 Clear 佇列並喚醒所有 worker；worker 檢測到 cancel_flag 則結束內部迴圈並退出。

實施步驟：
1. 設定 cancel_flag 並清空佇列
- 實作細節：lock(_workitems) -> Clear -> enqueueNotify.Set()
- 所需資源：lock
- 預估時間：20 分
2. worker 尊重 cancel_flag
- 實作細節：每輪與每次完成後檢查
- 所需資源：C#
- 預估時間：20 分
3. 關閉等待
- 實作細節：Join 所有 worker
- 所需資源：C#
- 預估時間：40 分

關鍵程式碼/設定：
```csharp
public void CancelPool()
{
    _cancel_flag = true;
    lock (_workitems) _workitems.Clear();
    enqueueNotify.Set(); // 喚醒所有 worker
    Thread[] snapshot;
    lock (_workerThreads) snapshot = _workerThreads.ToArray();
    foreach (var t in snapshot) t.Join();
}

private void DoWorkerThread()
{
    // ...
    if (_cancel_flag) break; // 每輪檢查
}
```

實際案例：原文提供 CancelPool() 與 EndPool(bool cancelQueueItem) 概念。
實作環境：C#、.NET
實測數據（示意）：
改善前：快速關閉耗時 ≈ 800ms
改善後：清空佇列並喚醒 -> ≈ 150ms 完成
改善幅度：關閉時間下降 ≈ 80%

Learning Points
- 快速取消與優雅關閉的差異
- 清空佇列的臨界區
- 喚醒所有等待者的重要性
技能要求：
- 必備：鎖、事件喚醒
- 進階：關閉流程與 Join 策略
延伸思考：
- 應否回報被丟棄的項目？
Practice Exercise
- 基礎：實作 CancelPool（30 分）
- 進階：取消壓測與時間統計（2 小時）
- 專案：取消回報機制（8 小時）
Assessment Criteria
- 功能（40%）：快速釋放
- 品質（30%）：無遺漏
- 效能（20%）：關閉時間短
- 創新（10%）：取消回報

## Case #11: WorkItem 例外隔離與回報

### Problem Statement（問題陳述）
業務場景：任務內拋出例外不應導致 worker 崩潰或整個程式終止；需隔離並回報。
技術挑戰：捕捉例外、不中斷後續工作、提供回報機制。
影響範圍：未處理的例外會中止 thread 或程序，造成服務不穩。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. item.Execute() 無防護。
2. 例外造成 thread 提前結束。
3. 無上報或重試設計。
深層原因：
- 架構層面：缺乏容錯機制。
- 技術層面：未提供錯誤流。
- 流程層面：監控與告警缺失。

### Solution Design（解決方案設計）
解決策略：Try/Catch 包覆 Execute；提供 OnWorkItemFailed 事件或 ILogger；避免吞例外無痕。

實施步驟：
1. 包覆 Execute
- 實作細節：catch(Exception ex) 並上報
- 所需資源：C#
- 預估時間：10 分
2. 事件/記錄機制
- 實作細節：public event Action<Exception, object> OnWorkItemFailed;
- 所需資源：委派/日誌
- 預估時間：30 分
3. 測試異常任務
- 實作細節：注入會 throw 的工作
- 所需資源：單元測試
- 預估時間：30 分

關鍵程式碼/設定：
```csharp
public event Action<Exception, object> OnWorkItemFailed;

try
{
    item.Execute();
}
catch (Exception ex)
{
    OnWorkItemFailed?.Invoke(ex, item.state);
    // 可選：重試或標記
}
```

實際案例：原文在 catch 處留 ToDo，提示需實作 handler。
實作環境：C#、.NET
實測數據（示意）：
改善前：未處理例外導致 1/500 任務使 worker 中止
改善後：0 中止，例外全記錄
改善幅度：穩定性顯著提升

Learning Points
- 例外的隔離與上報
- 不吞沒例外與可觀測性
- 重試與死信策略
技能要求：
- 必備：例外處理
- 進階：事件/日誌
延伸思考：
- 加入重試策略與熔斷？
Practice Exercise
- 基礎：實作事件上報（30 分）
- 進階：失敗重試一次（2 小時）
- 專案：整合 ILogger（8 小時）
Assessment Criteria
- 功能（40%）：不中斷服務
- 品質（30%）：上報清晰
- 效能（20%）：無顯著影響
- 創新（10%）：重試/熔斷

## Case #12: 信號去抖動與「0→1」轉換觸發

### Problem Statement（問題陳述）
業務場景：高頻入列時重複 Set 事件造成不必要喚醒；希望只在佇列由「空」變為「非空」時觸發通知。
技術挑戰：避免丟訊號的同時減少喚醒次數。
影響範圍：喚醒風暴造成上下文切換成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 每次入列都 Set，造成頻繁喚醒。
2. ManualResetEvent 長期 signaled，喚醒無效增多。
3. 無狀態轉換的判斷。
深層原因：
- 架構層面：缺乏去抖動設計。
- 技術層面：不了解信號合併特性。
- 流程層面：缺乏負載下觀測。

### Solution Design（解決方案設計）
解決策略：在鎖內判斷 Count==1 時才 Set（代表由 0→1 的轉換）；消費端在空時 Reset 再 Wait。

實施步驟：
1. 入列端 0→1 觸發
- 實作細節：同 Case #2 代碼
- 所需資源：lock
- 預估時間：20 分
2. 消費端空時 Reset
- 實作細節：同 Case #5 Reset 策略
- 所需資源：ManualResetEvent
- 預估時間：20 分
3. 壓測喚醒次數
- 實作細節：記錄 WaitOne 返回次數
- 所需資源：計數器
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 入列端
lock (_workitems)
{
    _workitems.Enqueue(wi);
    if (_workitems.Count == 1) enqueueNotify.Set(); // 0→1 才喚醒
}

// 消費端（準備等待）
lock (_workitems)
{
    if (_workitems.Count == 0) enqueueNotify.Reset();
}
```

實際案例：原文在入列後 Set，延伸出最佳化策略。
實作環境：C#、.NET
實測數據（示意）：
改善前：喚醒次數/秒 ≈ 2000（壓測）
改善後：喚醒次數/秒 ≈ 150（僅轉換時）
改善幅度：喚醒減少 ≈ 92.5%

Learning Points
- 事件與狀態機的結合
- 喚醒去抖動的典型手法
- 減少上下文切換
技能要求：
- 必備：鎖、事件
- 進階：狀態轉換設計
延伸思考：
- AutoResetEvent 是否更簡潔？
Practice Exercise
- 基礎：實作 0→1 觸發（30 分）
- 進階：計數喚醒次數（2 小時）
- 專案：與 AutoResetEvent 比較（8 小時）
Assessment Criteria
- 功能（40%）：正確觸發
- 品質（30%）：簡潔
- 效能（20%）：喚醒減少
- 創新（10%）：觀測報表

## Case #13: ThreadPriority 控制與工作隔離

### Problem Statement（問題陳述）
業務場景：背景任務（如日誌上傳/同步）不應干擾前台互動；需降低 worker 優先權。
技術挑戰：如何在 pool 內部統一套用 priority 並驗證影響。
影響範圍：不當優先權可能造成互動延遲。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設 Normal 優先權與前台競爭。
2. 無法 per-workload 設定優先權。
3. 未量測對互動的影響。
深層原因：
- 架構層面：無隔離策略。
- 技術層面：未使用 ThreadPriority。
- 流程層面：缺乏互動壓測。

### Solution Design（解決方案設計）
解決策略：在 CreateWorkerThread 統一設定 priority（BelowNormal/Lowest）；可根據場景暴露設定。

實施步驟：
1. 建構式接收 priority
- 實作細節：保存在 _priority
- 所需資源：C#
- 預估時間：10 分
2. CreateWorkerThread 套用
- 實作細節：t.Priority = _priority
- 所需資源：C#
- 預估時間：10 分
3. A/B 測試互動延遲
- 實作細節：度量 UI thread FPS 或回應時間
- 所需資源：量測工具
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var t = new Thread(DoWorkerThread)
{
    IsBackground = true,
    Priority = ThreadPriority.BelowNormal
};
```

實際案例：原文建構式 SimpleThreadPool(2, BelowNormal)。
實作環境：C#、.NET
實測數據（示意）：
改善前：互動延遲 p95 ≈ 120ms
改善後：p95 ≈ 70ms
改善幅度：≈ 41.7%

Learning Points
- 優先權對互動的影響
- 背景/前景工作隔離
- A/B 測試必要性
技能要求：
- 必備：ThreadPriority
- 進階：效能量測
延伸思考：
- 核心綁定（affinity）是否有幫助？
Practice Exercise
- 基礎：設定 BelowNormal（30 分）
- 進階：壓測互動延遲（2 小時）
- 專案：動態調整優先權（8 小時）
Assessment Criteria
- 功能（40%）：可設定
- 品質（30%）：介面清晰
- 效能（20%）：互動改善
- 創新（10%）：動態化策略

## Case #14: 停止/取消旗標的記憶體可見性與檢查點

### Problem Statement（問題陳述）
業務場景：EndPool/CancelPool 設定旗標後，worker 需能迅速感知狀態變更並退出或完成。
技術挑戰：確保多執行緒間對 _stop_flag/_cancel_flag 的可見性，並在正確的檢查點做決策。
影響範圍：旗標不可見會導致卡住或延遲關閉。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 旗標非 volatile，可能被快取。
2. 檢查點過於稀疏。
3. 未喚醒等待中的 worker。
深層原因：
- 架構層面：關閉語意不清。
- 技術層面：記憶體模型與可見性不足。
- 流程層面：未測試關閉延遲。

### Solution Design（解決方案設計）
解決策略：將旗標宣告為 volatile；在內外迴圈與完成點檢查旗標；End/Cancel 設旗標後 Set 喚醒所有 worker。

實施步驟：
1. volatile 宣告
- 實作細節：private volatile bool _stop_flag, _cancel_flag;
- 所需資源：C#
- 預估時間：10 分
2. 檢查點設計
- 實作細節：取出項目前後、內外迴圈處
- 所需資源：C#
- 預估時間：20 分
3. 喚醒等待中的 worker
- 實作細節：enqueueNotify.Set()
- 所需資源：C#
- 預估時間：10 分

關鍵程式碼/設定：
```csharp
private volatile bool _stop_flag;
private volatile bool _cancel_flag;

if (_stop_flag || _cancel_flag) break;
// 每一輪與每次完成後都檢查
```

實際案例：原文在迴圈中檢查 _stop_flag/_cancel_flag。
實作環境：C#、.NET
實測數據（示意）：
改善前：關閉延遲 p95 ≈ 500ms
改善後：p95 ≈ 80ms
改善幅度：≈ 84%

Learning Points
- volatile 與記憶體可見性
- 關閉檢查點佈局
- 喚醒對關閉的影響
技能要求：
- 必備：volatile 語意
- 進階：記憶體模型
延伸思考：
- 是否需 Interlocked.Exchange？
Practice Exercise
- 基礎：宣告 volatile 並驗證（30 分）
- 進階：關閉延遲量測（2 小時）
- 專案：加上超時關閉策略（8 小時）
Assessment Criteria
- 功能（40%）：快速感知旗標
- 品質（30%）：檢查點清晰
- 效能（20%）：延遲下降
- 創新（10%）：超時策略

## Case #15: API 易用性：QueueUserWorkItem 多載與 Dispose 模式

### Problem Statement（問題陳述）
業務場景：呼叫端期望以最小樣板碼提交工作，且能用 using/Dispose 自動收攤。
技術挑戰：設計多載（有/無 state），正確實作 Dispose 呼叫 EndPool。
影響範圍：降低使用成本、減少遺漏收攤風險。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 僅提供單一 API 導致冗長。
2. 呼叫端易忘記 EndPool。
3. 缺少 using 模式。
深層原因：
- 架構層面：API 設計不友好。
- 技術層面：未實作 Dispose 模式。
- 流程層面：使用規範不一致。

### Solution Design（解決方案設計）
解決策略：提供 QueueUserWorkItem(cb) 與 QueueUserWorkItem(cb, state) 多載；實作 IDisposable，在 Dispose 中呼叫 EndPool(false)。

實施步驟：
1. 多載方法
- 實作細節：無 state 版本轉呼叫有 state 版本
- 所需資源：C#
- 預估時間：10 分
2. Dispose 模式
- 實作細節：Dispose() => EndPool(false)
- 所需資源：C#
- 預估時間：10 分
3. 範例與文件
- 實作細節：示例 using
- 所需資源：README
- 預估時間：20 分

關鍵程式碼/設定：
```csharp
public bool QueueUserWorkItem(WaitCallback callback) =>
    QueueUserWorkItem(callback, null);

public void Dispose() => EndPool(false);
```

實際案例：原文提供兩種多載與 Dispose 呼叫 EndPool(false)。
實作環境：C#、.NET
實測數據（示意）：
改善前：忘記 EndPool 的比例 ≈ 5%（內部測）
改善後：using 自動收攤 -> 幾近 0
改善幅度：可用性大幅提升

Learning Points
- API 設計與開發者體驗（DX）
- Dispose 模式與資源釋放
- 以多載減低樣板碼
技能要求：
- 必備：IDisposable
- 進階：API 設計原則
延伸思考：
- 加入 IAsyncDisposable？
Practice Exercise
- 基礎：完成多載與 Dispose（30 分）
- 進階：using 模式範例（2 小時）
- 專案：文件/範本（8 小時）
Assessment Criteria
- 功能（40%）：正確釋放
- 品質（30%）：易用
- 效能（20%）：無額外成本
- 創新（10%）：DX 提升

## Case #16: 文章樣例重現與驗證（25 筆任務 + EndPool）

### Problem Statement（問題陳述）
業務場景：依文章樣例，建立 2 個 worker 提交 25 個任務並在結尾 EndPool 等待完成，用以驗證正確性與量測吞吐。
技術挑戰：確保提交/等待語意正確，並觀察擴編與 idle 回收行為（若設定）。
影響範圍：作為教學與回歸測試樣板。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未對樣例進行完整驗證。
2. 未收集可量測指標。
3. 無回歸測試基準。
深層原因：
- 架構層面：缺少基準案例。
- 技術層面：未建立量測方法。
- 流程層面：缺乏自動化測試。

### Solution Design（解決方案設計）
解決策略：重現樣例程式，加入 Stopwatch 量測總耗時、平均等待；作為最小可運作驗證（MVV）。

實施步驟：
1. 實作樣例
- 實作細節：2 worker，提交 25 任務，EndPool
- 所需資源：C#
- 預估時間：20 分
2. 加入量測
- 實作細節：Stopwatch、列印耗時
- 所需資源：System.Diagnostics
- 預估時間：20 分
3. 多組參數測試
- 實作細節：變更 worker=1,2,4 比較
- 所需資源：C#
- 預估時間：40 分

關鍵程式碼/設定：
```csharp
var stp = new SimpleThreadPool(2, ThreadPriority.BelowNormal);
var sw = Stopwatch.StartNew();

for (int i = 0; i < 25; i++)
{
    stp.QueueUserWorkItem(state => {
        Thread.Sleep(100); // 模擬工作
        Console.WriteLine(state);
    }, $"STP1[{i}]");

    Thread.Sleep(new Random().Next(10, 30)); // 模擬間隔
}
stp.EndPool();
sw.Stop();
Console.WriteLine($"Total Elapsed: {sw.ElapsedMilliseconds} ms");
```

實際案例：原文相同用法（25 筆 + EndPool）。
實作環境：C#、.NET
實測數據（示意）：
worker=1：總耗時 ≈ 2500ms
worker=2：總耗時 ≈ 1300ms
worker=4：總耗時 ≈ 750ms（含切換開銷）
改善幅度：2 worker 較 1 worker ≈ 48% 降幅

Learning Points
- 樣例作為回歸測試基準
- 量測方法建立
- 參數對吞吐的影響
技能要求：
- 必備：C# 基礎
- 進階：效能量測
延伸思考：
- 加入 queue 閾值與 idle timeout 的影響測試
Practice Exercise
- 基礎：重現樣例（30 分）
- 進階：不同 worker 參數對比（2 小時）
- 專案：建立自動化基準測試（8 小時）
Assessment Criteria
- 功能（40%）：樣例可跑通
- 品質（30%）：量測清楚
- 效能（20%）：趨勢合理
- 創新（10%）：可視化報告


案例分類

1. 按難度分類
- 入門級：Case #4, #6, #8, #13, #15, #16
- 中級：Case #1, #2, #3, #7, #9, #10, #12, #14
- 高級：無（本篇聚焦基礎到中階並行設計；若加入優先序隊列/無鎖結構可升級）

2. 按技術領域分類
- 架構設計類：Case #1, #2, #9, #10, #14, #15
- 效能優化類：Case #3, #4, #5, #12, #13
- 整合開發類：Case #16（樣例/量測整合）
- 除錯診斷類：Case #7, #8, #11
- 安全防護類（穩定性/容錯）：Case #10, #11, #14

3. 按學習目標分類
- 概念理解型：Case #4, #5, #6, #13
- 技能練習型：Case #7, #8, #15, #16
- 問題解決型：Case #2, #3, #9, #10, #11, #14
- 創新應用型：Case #1, #12

案例關聯圖（學習路徑建議）
- 建議起點（基礎概念與最小實作）
  1) Case #4（阻塞等待）→ 2) Case #6（OS 決策）→ 3) Case #7（佇列安全）
- 進階到完整功能
  4) Case #1（可組態池）→ 5) Case #2（動態擴編）→ 6) Case #3（idle 回收）
- 關閉與穩定性
  7) Case #14（旗標與可見性）→ 8) Case #9（EndPool 完成屏障）→ 9) Case #10（CancelPool 快關）
- 容錯與觀測
  10) Case #11（例外隔離）→ 11) Case #12（信號去抖動）
- 體驗與效能
  12) Case #13（優先權）→ 13) Case #15（API/Dispose）
- 驗證與實戰
  14) Case #16（樣例重現與量測）

依賴關係：
- Case #7（佇列安全）是 Case #2/#3/#9 的前置
- Case #5（事件 Reset 策略）關聯 Case #4/#12
- Case #14（旗標可見性）是 Case #9/#10 的前置
- Case #1（可組態池）提供基底供所有擴展

完整學習路徑：
Case #4 → #6 → #7 → #1 → #2 → #3 → #14 → #9 → #10 → #11 → #5 → #12 → #13 → #15 → #16

說明：
- 此路徑先打底同步與資料安全，再進入可組態/伸縮/回收，接著完成關閉語意與容錯，最後強化效能與易用性，並以樣例驗證收束。