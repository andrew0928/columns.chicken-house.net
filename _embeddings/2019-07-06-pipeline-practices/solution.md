以下為基於原文萃取與重組的 18 個完整教學案例，聚焦於平行任務處理、管線化（pipeline）、資源精準控制與效能度量。每個案例皆包含問題、根因、可複製的解決步驟與實測指標，便於實戰教學、專案練習與評估。

說明：本文所有「實作環境」皆沿用作者的實測平台（AMD Ryzen 9 3900X 12C/24T、64GB RAM、NVMe SSD、Windows 10、VS 2019），所有「實測數據」均取自作者公佈的 benchmark 表格。基準比較若無特別說明，皆以最基礎解法 AndrewBasicTaskRunner1（純序列執行）為「改善前」基準。

------------------------------------------------------------

## Case #1: 基準線建立：純序列執行（Baseline Runner）

### Problem Statement（問題陳述）
- 業務場景：一次需處理 1000 個 MyTask，每個任務需依序執行 Step1→Step2→Step3。真實後端場景中常見批次匯入、資料清洗與後續處理等流程，若僅以 for 迴圈序列化執行，雖能保證正確性，卻難以達到可接受的整體處理時間。
- 技術挑戰：如何建立可重現、可對照的基準線（baseline），作為後續並行與管線化優化之衡量基準。
- 影響範圍：整體處理時間（TTLT）極大；平均交期（AVG_WAIT）極差；資源（WIP、MEM）雖低但吞吐極差。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 全序列執行：所有任務與步驟逐一串行，無任何併行。
  2. 無 pipeline：無法在 Step1 進行時，同步推動後續 Step2/Step3。
  3. 資源閒置：CPU/執行緒與記憶體資源未被有效利用。
- 深層原因：
  - 架構層面：缺乏生產者/消費者與緩衝設計。
  - 技術層面：未使用 TPL/ThreadPool/Channel/BlockingCollection。
  - 流程層面：無 TTFT/TTLT/AVG_WAIT 指標對齊的性能目標。

### Solution Design（解決方案設計）
- 解決策略：建立可運行的最小正確解與監測指標（console + csv），固化「正確性」與「度量」為基礎，後續優化以此為對照組。

- 實施步驟：
  1. 建立 TaskRunner，for 迴圈依序執行 Step1→2→3
     - 實作細節：確保順序正確；輸出 console 與 csv
     - 所需資源：.NET Console、Practice Core
     - 預估時間：0.5 小時
  2. 執行 1000 筆並收集指標
     - 實作細節：關注 TTFT/TTLT/AVG_WAIT/WIP/MEM
     - 所需資源：Excel 視覺化
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```csharp
public class AndrewTaskRunner : TaskRunnerBase
{
    public override void Run(IEnumerable<MyTask> tasks)
    {
        foreach (var task in tasks)
        {
            task.DoStepN(1);
            task.DoStepN(2);
            task.DoStepN(3);
        }
    }
}
```

- 實際案例：AndrewDemo.AndrewBasicTaskRunner1
- 實作環境：同上
- 實測數據：
  - 改善前：無
  - 改善後（Baseline）：TTFT 1431.43 ms、TTLT 1,430,415.55 ms、AVG_WAIT 715,922.35 ms、WIP 1、MEM 13,824
  - 改善幅度：作為基準線

Learning Points（學習要點）
- 核心知識點：基準線思維；可觀測性建立；效能指標定義
- 技能要求：
  - 必備技能：C# 基礎、BCL、console I/O
  - 進階技能：Excel/圖表化分析
- 延伸思考：基準線與理論極限的差距？序列正確性與吞吐的取捨？何時需要並行與管線化？
- Practice Exercise：以本 Runner 跑 100/1000/10000 比較曲線（30 分）；加入簡單計時記錄（2 小時）；撰寫小專案封裝基準工具（8 小時）
- Assessment Criteria：功能完整性（能跑完且記錄指標）；程式碼品質（簡潔清楚）；效能優化（作為對照）；創新性（n/a）

------------------------------------------------------------

## Case #2: 反面教材：無上限併發的雪崩（WIP/MEM 爆炸）

### Problem Statement（問題陳述）
- 業務場景：嘗試一股腦把 1000 任務全部丟進併發，以為能更快完成，常見於誤用 Task.Run/Parallel.ForEach 而未設限。
- 技術挑戰：忽略 per-step 併發上限與記憶體配置，造成 WIP 及 MEM 峰值暴增、排程飢餓與 TTFT/AVG_WAIT 惡化。
- 影響範圍：使用者首個回應時間（TTFT）極差；平均交期、整體時間與資源成本大幅上升，易觸發 OOM。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 不受控併發：一次啟動 1000 任務，無 backpressure。
  2. 忽略步驟上限：Step1/2/3 的並行限制被突破，等待擁塞。
  3. 記憶體佔用：每步驟 allocate/free 不同步造成高峰。
- 深層原因：
  - 架構層面：缺乏 pipeline 與緩衝區策略。
  - 技術層面：未使用 Semaphore/BlockingCollection/Channel 管制。
  - 流程層面：無 TTFT/TTLT/WIP 作為驅動的 KPI。

### Solution Design（解決方案設計）
- 解決策略：示範反例，強化「先設計後並行」與「精準控併發」的重要性；再導入 per-step 限制與緩衝。

- 實施步驟：
  1. 觀察無控制併發的效果
     - 實作細節：Parallel.ForEach 無 WithDegreeOfParallelism；或每 task 建 3 個 Task
     - 所需資源：.NET/TPL
     - 預估時間：0.5 小時
  2. 套用 per-step 限制與背壓
     - 實作細節：引入 SemaphoreSlim/BlockingCollection 對應上限
     - 所需資源：並行基本元件
     - 預估時間：2 小時

- 關鍵程式碼/設定（反例示意）：
```csharp
// 反例：無限制地平行所有任務與步驟
Parallel.ForEach(tasks, t =>
{
    Task.Run(() => t.DoStepN(1));
    Task.Run(() => t.DoStepN(2));
    Task.Run(() => t.DoStepN(3));
});
```

- 實際案例：AndrewDemo.AndrewBasicTaskRunner2
- 實作環境：同上
- 實測數據：
  - 改善前（Baseline）：TTFT 1431.43、TTLT 1,430,415.55、AVG_WAIT 715,922.35、WIP 1、MEM 13,824
  - 改善後（反例）：TTFT 1,000,370.41、TTLT 1,430,364.68、AVG_WAIT 1,215,376.61、WIP 1000、MEM 1,028,480
  - 改善幅度：TTFT/AVG_WAIT/資源全數惡化（負面學習）

Learning Points（學習要點）
- 核心知識點：背壓（Backpressure）、WIP/MEM 受控必要性
- 技能要求：了解併發元件；認識資源峰值風險
- 延伸思考：如何設計每步驟的併發門檻？如何快取/釋放資源？
- Practice：以此反例改造為有上限的 pipeline（2 小時）
- Assessment：是否正確加入上限並觀測 WIP/MEM 下降

------------------------------------------------------------

## Case #3: CPU 數量當並行上限的誤用矯正（LexTaskRunner）

### Problem Statement（問題陳述）
- 業務場景：以 CPU 核心數作為 Semaphore 上限來控制 Task 併發，常見於「以為 CPU bound」的誤判。
- 技術挑戰：這題是 I/O/等待型與 per-step 上限綁定；以 CPU 數限制總併發不等於正確的 per-step 限制。
- 影響範圍：TTFT 稍弱、TTLT/AVG_WAIT 接近理想；可更精準但已具實用價值。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 全域上限錯置：Semaphore 以 ProcessorCount 控全域，不對 per-step。
  2. 排程非最短路徑：TTFT 因順序/啟動時機不夠「緊」而略差。
  3. 任務拆分方式產生額外排程開銷。
- 深層原因：
  - 架構層面：忽略 step-based pipeline 的真實瓶頸。
  - 技術層面：通用 ThreadPool 排程 vs. 任務專屬排程的差異。
  - 流程層面：TTFT 未被單獨優化。

### Solution Design（解決方案設計）
- 解決策略：保留簡潔的多工結構，將全域上限改為 per-step 上限；必要時用 pipeline 精準移交。

- 實施步驟：
  1. 以 Task 並行處理但加強 per-step 門檻
     - 實作細節：為每步驟獨立 Semaphore/Channel
     - 所需資源：SemaphoreSlim、Task
     - 預估時間：1 小時
  2. 收斂 TTFT
     - 實作細節：對首批任務順序/接棒做特化
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```csharp
public class LexTaskRunner : TaskRunnerBase
{
    private static readonly SemaphoreSlim _slim = 
        new SemaphoreSlim(Environment.ProcessorCount);

    public override void Run(IEnumerable<MyTask> tasks)
    {
        var processTasks = tasks.Select(processTask).ToArray();
        Task.WaitAll(processTasks);
    }

    private Task processTask(MyTask t)
    {
        _slim.Wait();
        return Task.Run(async () =>
        {
            await Task.Run(() => t.DoStepN(1));
            await Task.Run(() => t.DoStepN(2));
            await Task.Run(() => t.DoStepN(3));
            _slim.Release();
        });
    }
}
```

- 實際案例：LexDemo.LexTaskRunner
- 実作環境：同上
- 實測數據（對比 Baseline）：
  - 改善前：TTLT 1,430,415.55、AVG_WAIT 715,922.35
  - 改善後：TTLT 174,479.45（↓87.79%）、AVG_WAIT 86,654.78（↓87.89%）、TTFT 1443.48（↑0.84%）
  - 改善幅度：整體效能大幅改善；TTFT 略差

Learning Points（學習要點）
- 核心知識點：全域 vs. per-step 併發控管、任務排程與 TTFT
- 技能要求：Task 排程、SemaphoreSlim 運用
- 延伸思考：如何把 TTFT 壓回 1% 以內？是否改為 pipeline 控制更穩？
- Practice：以 per-step Semaphore 重構此解法（2 小時）
- Assessment：TTLT/AVG_WAIT 接近理論，TTFT 優化

------------------------------------------------------------

## Case #4: Pipeline 缺口：Step1 未平行導致 5 倍 TTLT（SeanRunner）

### Problem Statement（問題陳述）
- 業務場景：已建立三段式 pipeline，但 Step1 未被平行化，最慢關卡成瓶頸，導致整體時間爆長。
- 技術挑戰：最慢關的並行度必須達到上限，否則整條線被拖累。
- 影響範圍：TTLT/AVG_WAIT 約為理想值的 5 倍；TTFT尚可。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Step1 單執行緒：WIP1=1，使整體吞吐取決於 867ms/任務。
  2. 只平行了 Step2/Step3：治標不治本。
  3. 首關瓶頸未對準 5 的上限。
- 深層原因：
  - 架構層面：pipeline 節點間的並行度配置不均。
  - 技術層面：工作者（workers）未按 step 限制作業。
  - 流程層面：未用理論極限校準各 step 並發策略。

### Solution Design（解決方案設計）
- 解決策略：將 Step1 配置 5 個 worker（或等效），落實 step-based 並行限制；中間用 BlockingCollection 導入背壓。

- 實施步驟：
  1. 調整 Step1 為 5 個 worker
     - 實作細節：每步驟設獨立消費 loop
     - 預估時間：1 小時
  2. 引入 BlockingCollection 作為緩衝並用 CompleteAdding 結束
     - 實作細節：避免 busy-wait，精準通知
     - 預估時間：1 小時

- 關鍵程式碼/設定（片段）：
```csharp
// 以 BlockingCollection 管線；每步驟啟動相對應 worker 數
var q1 = new BlockingCollection<MyTask>();
var q2 = new BlockingCollection<MyTask>();
var q3 = new BlockingCollection<MyTask>();

// Step1: 5 workers
for (int i = 0; i < 5; i++)
    Task.Run(() => { foreach (var t in q1.GetConsumingEnumerable()) { t.DoStepN(1); q2.Add(t); }});

// Step2: 3 workers
// Step3: 3 workers
```

- 實際案例：SeanDemo.SeanRunner（原始）
- 實作環境：同上
- 實測數據（原始 vs. Baseline）：
  - 原始：TTLT 867,875.35（仍↓39.34%）、AVG_WAIT 434,657.76（↓39.27%）、TTFT 1433.26
  - 重點：未平行 Step1 為根因；修正後預期可逼近 174,392 ms
  - 改善幅度：修正 Step1 後可望再↓約 5 倍

Learning Points（學習要點）
- 核心知識點：瓶頸步驟的並行度配置；背壓精準通知
- 技能要求：BlockingCollection、workers 模式
- 延伸思考：是否需 capacity 限制？如何避免中段倉庫爆量？
- Practice：把 Step1 worker 調到 5，觀察 TTLT 變化（2 小時）
- Assessment：TTLT 接近理論值 ±1%

------------------------------------------------------------

## Case #5: RX（Reactive Extensions）+ Semaphore 的管線化（Phoenix）

### Problem Statement（問題陳述）
- 業務場景：以 RX 表達資料流，透過 ContinueWith 與 Semaphore 控制每步驟上限，實作簡潔。
- 技術挑戰：在 RX 的流式語義下，精準落實 per-step 限制與及時移交。
- 影響範圍：TTLT/AVG_WAIT 接近理想；TTFT 稍慢（排程銜接時機）。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. ContinueWith + Task 排程的非決定性造成 TTFT 較大。
  2. RX 僅用於入口，後段仍以 Task 手動控制。
  3. 仍需 Semaphore 人工維持上限。
- 深層原因：
  - 架構層面：流式與工作者模型混用需拿捏。
  - 技術層面：RX operators 選用不夠徹底。
  - 流程層面：未對「首件交付」做特化優先。

### Solution Design（解決方案設計）
- 解決策略：以 IObservable 流入，分三段 map/concat 控制，搭配 SemaphoreSlim 控 per-step 並發，維持簡潔與穩定。

- 實施步驟：
  1. ToObservable + SelectMany 串三段
     - 實作細節：每段前後 acquire/release 對應步驟上限
     - 預估時間：2 小時
  2. 檢視 TTFT，必要時首批任務特化排程
     - 實作細節：先行 prefetch/預熱
     - 預估時間：1 小時

- 關鍵程式碼/設定（片段）：
```csharp
tasks.ToObservable()
  .Select(t => {
      sem1.Wait();
      return Task.Run(() => t.DoStepN(1))
                 .ContinueWith(_ => { sem2.Wait(); sem1.Release(); return t; });
  })
  .SelectMany(t => t)
  .Select(t => Task.Run(() => t.DoStepN(2))
                   .ContinueWith(_ => { sem3.Wait(); sem2.Release(); return t; }))
  .SelectMany(t => t)
  .Select(t => Task.Run(() => t.DoStepN(3))
                   .ContinueWith(_ => { sem3.Release(); return t; }))
  .SelectMany(t => t)
  .Wait();
```

- 實際案例：PhoenixDemo.PhoenixTaskRunner
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 174,511.24（↓87.80%）、AVG_WAIT 86,170.37（↓87.97%）、TTFT 1459.45（↑1.96%）
- 改善幅度：整體吞吐極佳；TTFT略遜

Learning Points（學習要點）
- 核心知識點：RX 流式建模、Semaphore 上限控制、ContinueWith 銜接
- 技能要求：Rx.NET、Task/ContinueWith、SemaphoreSlim
- 延伸思考：改用 Channel 全 async 是否更一致？能否對 TTFx 特化？
- Practice：把 RX 兩段改用 Channel 實作（2 小時）
- Assessment：TTLT/AVG_WAIT ≤ 101%，TTFT 收斂

------------------------------------------------------------

## Case #6: Channel（System.Threading.Channels）非阻塞管線（Julian）

### Problem Statement（問題陳述）
- 業務場景：用 Channel 取代 BlockingCollection，完整 async 生產者/消費者，維持 per-step 上限，追求低延遲背壓。
- 技術挑戰：在 async 模式下達到精準移交與低額外延遲，並觀察 TTFT 的排程間隙。
- 影響範圍：TTLT 接近理想；AVG_WAIT 略高於最佳；TTFT 有 600ms 延遲現象。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Step2 啟動延後（觀測到 ~600ms），首筆 TTFT 放大。
  2. 非同步排程順序不完全可控。
  3. 三段 ProcessStepN 為分離方法，優化空間在交接時機。
- 深層原因：
  - 架構層面：全 async 架構常見的排程「鬆動」。
  - 技術層面：Channel.TryWrite/WaitToWrite 的策略選用。
  - 流程層面：首批任務優先策略不足。

### Solution Design（解決方案設計）
- 解決策略：三段 Channel 串流，單 writer/reader 模式與 AllowSynchronousContinuations 取捨；針對 TTFT 觀測 gap 做首批任務特化。

- 實施步驟：
  1. 建立 ch1/ch2，三段 ProcessStepN
     - 實作細節：SingleWriter/SingleReader、AllowSynchronousContinuations
     - 預估時間：2 小時
  2. 追蹤首筆任務在 T1/T2/T3 的交接位置
     - 實作細節：CSV 讀取 T1~T30 欄位
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```csharp
var ch1 = Channel.CreateBounded<MyTask>(
  new BoundedChannelOptions(1){ SingleWriter=true, SingleReader=true,
                                AllowSynchronousContinuations=true });
var ch2 = Channel.CreateBounded<MyTask>(/* 同上 */);

static async Task ProcessStep1(ChannelWriter<MyTask> w, IEnumerable<MyTask> tasks)
{
    var ts = tasks.Select(async t => await Task.Run(() => { t.DoStepN(1); 
        while (await w.WaitToWriteAsync()) { if (w.TryWrite(t)) break; }}));
    Task.WaitAll(ts.ToArray());
    w.Complete();
}
```

- 實際案例：JulianDemo.TaskRunner
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 174,467.72（↓87.80%）、AVG_WAIT 87,715.99（↓87.75%）、TTFT 1448.28（↑1.18%）
- 改善幅度：吞吐優；TTFT 可再收斂

Learning Points（學習要點）
- 核心知識點：Channel async 背壓、同步延續（AllowSynchronousContinuations）影響
- 技能要求：Channel API、CSV 診斷
- 延伸思考：Channel capacity 對 WIP/TTFT 的影響？是否需首批預留快路徑？
- Practice：將 ch1/ch2 capacity 做敏感度測試（2 小時）
- Assessment：TTLT 接近理論、TTFT gap 降低

------------------------------------------------------------

## Case #7: 工作者過少導致吞吐受限（Gulu）

### Problem Statement（問題陳述）
- 業務場景：自製 ConcurrentQueue + 多工作者模型，但全系統 threadCount 僅 3，遠低於各步驟上限總和，導致整體吞吐不足。
- 技術挑戰：找到合理的工作者數，並避免 busy-wait 與公平性問題。
- 影響範圍：TTLT/AVG_WAIT 約為理想值 2.7 倍；TTFT 表現良好；WIP 低。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. threadCount=3 遠小於步驟上限總和（5+3+3=11）。
  2. 生產/消費節奏失衡，WIP 過低。
  3. 缺乏每步驟的獨立並發配置。
- 深層原因：
  - 架構層面：一組工作者執行全部步驟，無法匹配各步驟速率。
  - 技術層面：缺乏背壓通知（靠 Count/polling）。
  - 流程層面：未先計算理論上限以設定 worker。

### Solution Design（解決方案設計）
- 解決策略：將工作者分配到各步驟（5/3/3），導入 BlockingCollection/Channel 與通知式背壓。

- 實施步驟：
  1. 將單一 worker pool 拆為 per-step pools
     - 實作細節：Step1=5, Step2=3, Step3=3
     - 預估時間：1 小時
  2. 用 BlockingCollection 取代 Count polling
     - 預估時間：1 小時

- 關鍵程式碼/設定（片段）：
```csharp
// 原架構用 ConcurrentQueue + 自製 Producer/Consumer
// 建議：改為每步驟 BlockingCollection + GetConsumingEnumerable()
```

- 實際案例：GuluDemo.GuluTaskRunner
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 477,727.39（↓66.6%）、AVG_WAIT 234,824.64（↓67.2%）、TTFT 1432.03
- 改善幅度：修正後可望逼近 1.0x 理想

Learning Points（學習要點）
- 核心知識點：workers 對吞吐的敏感度、背壓機制
- 技能要求：BlockingCollection/Channel、pipeline 拆解
- 延伸思考：per-step worker 是否動態伸縮？如何設定倉庫容量？
- Practice：將 threadCount=3 改為 per-step 配置（2 小時）
- Assessment：TTLT/AVG_WAIT 明顯下降

------------------------------------------------------------

## Case #8: ThreadPool 調優 + 三段管線創最佳 AVG_WAIT（JW）

### Problem Statement（問題陳述）
- 業務場景：以 BlockingCollection 串三段管線，背後用 ThreadPool，並設定 Min/MaxThreads，上限貼齊需求。
- 技術挑戰：以通用排程達到低 AVG_WAIT 與接近理論的 TTLT，同時維持簡潔性。
- 影響範圍：TTLT 100.06%、AVG_WAIT 排名最佳（100% 基準），TTFT 100.52%。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. ThreadPool 事前調優（Min/MaxThreads），避免擴張延遲。
  2. per-step 並發（5/3/3）正確，BlockingCollection 精準通知。
  3. 結尾用 ManualResetEvent 等待完成。
- 深層原因：
  - 架構層面：pipeline + 通用排程的務實折衷。
  - 技術層面：ThreadPool 參數化降低隊列延遲。
  - 流程層面：指標導向（AVG_WAIT 最優）。

### Solution Design（解決方案設計）
- 解決策略：在 pipeline 固定模式下，把 ThreadPool 調到合適工作數，避免排程抖動；兼顧吞吐與平均等待。

- 實施步驟：
  1. 設定 ThreadPool 上下限 = 5+3+3 (+buffer)
     - 實作細節：SetMinThreads/SetMaxThreads
     - 預估時間：0.5 小時
  2. 建立三段 workers 與倉庫，分別消費/生產
     - 預估時間：1.5 小時

- 關鍵程式碼/設定：
```csharp
int max = (5 + 3 + 3) + 3;
ThreadPool.SetMinThreads(max, max);
ThreadPool.SetMaxThreads(max, max);

// 三段 JobWorker，對應 5/3/3，間用 BlockingCollection 交接
```

- 實際案例：JW.JWTaskRunnerV5
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 174,496.77（↓87.80%）、AVG_WAIT 85,855.17（↓88.00%，最佳）、TTFT 1436.46（↑0.35%）
- 改善幅度：整體極佳，AVG_WAIT 最優

Learning Points（學習要點）
- 核心知識點：ThreadPool 調優、BlockingCollection 管線化
- 技能要求：ThreadPool API、管線設計
- 延伸思考：是否自管 threads 更可控？TTFT 可否再壓？
- Practice：嘗試不同 maxThreads 對 TTFT/AVG_WAIT 的影響（2 小時）
- Assessment：AVG_WAIT ≤ 101%、TTLT ≤ 101%

------------------------------------------------------------

## Case #9: TPL 平行 + per-step Semaphore（Andy）

### Problem Statement（問題陳述）
- 業務場景：使用 Parallel.ForEach 對 tasks 並行，對每步驟以 Semaphore 限制並行，維持簡潔與可讀性。
- 技術挑戰：在通用 TPL 上正確落實每步驟上限，避免過度或不足的併發。
- 影響範圍：TTLT/AVG_WAIT 良好（104.8% / 101.7%）；TTFT在 100.30%。
- 複雜度評級：低-中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 在任務內控 Semaphore 有些延後（task 被啟動才受控）。
  2. Parallel.ForEach 背後對 threads 數量估策不透明。
  3. 欠缺 per-step 的「隊列邊界」控制。
- 深層原因：
  - 架構層面：交由 TPL 決策排程，少量非決定性。
  - 技術層面：Semaphore 控制點位置較晚。
  - 流程層面：未對 TTFT 特化。

### Solution Design（解決方案設計）
- 解決策略：保留 TPL 便利性，將 per-step 控制點提前到排隊邊界（Queue/Channel）而非 task 內。

- 實施步驟：
  1. 使用 Parallel.ForEach 保持簡潔
     - 預估時間：0.5 小時
  2. 把 Semaphore 放在進入步驟前的 gating 階段
     - 預估時間：1.5 小時

- 關鍵程式碼/設定：
```csharp
Parallel.ForEach(tasks, t=>{
  sem1.Wait(); t.DoStepN(1); sem1.Release();
  sem2.Wait(); t.DoStepN(2); sem2.Release();
  sem3.Wait(); t.DoStepN(3); sem3.Release();
});
```

- 實際案例：AndyDemo.AndyTaskRunner
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 182,791.88（↓87.22%）、AVG_WAIT 87,302.68（↓87.80%）、TTFT 1433.35（↑0.14%）

Learning Points（學習要點）
- 核心知識點：TPL 的便利與侷限；控制點前移
- 技能要求：Parallel.ForEach、SemaphoreSlim
- 延伸思考：改為 Channel/BlockingCollection 是否更精準？
- Practice：加入 .WithDegreeOfParallelism 對照（2 小時）
- Assessment：TTLT 接近 105% 以內

------------------------------------------------------------

## Case #10: PLINQ Partitioner 切片並行（Maze）

### Problem Statement（問題陳述）
- 業務場景：利用 Partitioner 將輸入切段，並為每段啟動平行處理；每任務內仍序列 Step1→3，兼顧簡潔與效能。
- 技術挑戰：避免切分不均；不使用顯性 Semaphore 也能控制資源。
- 影響範圍：TTLT 100.12%、AVG_WAIT 102.20%、TTFT 100.25%；表現穩定。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Partitioner 以 ProcessorCount 切片，但步驟上限非直接對齊。
  2. 任務內序列化降低了 WIP 與 MEM 峰值。
  3. 沒明確 per-step 上限，但整體接近理想。
- 深層原因：
  - 架構層面：以輸入切片替代 per-step 管線。
  - 技術層面：PLINQ + Partitioner 的切片策略。
  - 流程層面：以簡勝繁，維護成本低。

### Solution Design（解決方案設計）
- 解決策略：使用 Partitioner.Create + GetPartitions 分配分區，各自 ForEach 任務。任務內步驟序列化以降低複雜度。

- 實施步驟：
  1. 依 CPU 切片並啟動 partition 任務
     - 預估時間：1 小時
  2. 每 partition 逐一執行 Step1→3
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```csharp
var tasklist = Task.WhenAll(
  Partitioner.Create(tasks).GetPartitions(Environment.ProcessorCount)
    .Select(p => Task.Run(() => {
      using (p) while (p.MoveNext()) {
        var t = p.Current; if (t==null) continue;
        t.DoStepN(1); t.DoStepN(2); t.DoStepN(3);
      }
    })));
tasklist.GetAwaiter().GetResult();
```

- 實際案例：MazeDemo.MazeTaskRunner
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 174,593.59（↓87.79%）、AVG_WAIT 87,746.53（↓87.74%）、TTFT 1432.57（↑0.08%）

Learning Points（學習要點）
- 核心知識點：PLINQ Partitioner 的切片並行
- 技能要求：Partitioner/TPL、PLINQ
- 延伸思考：是否需要 per-step 管線替代？切片策略可否自訂？
- Practice：嘗試自訂分割策略（2 小時）
- Assessment：TTLT 101.5% 以內

------------------------------------------------------------

## Case #11: 專屬 threads + BlockingCollection 精準管線（AndrewPipelineTaskRunner1）

### Problem Statement（問題陳述）
- 業務場景：每步驟建立專屬 threads，數量直接對齊上限（5/3/3），中間以 BlockingCollection 作為倉庫，達到最精準的調度與背壓。
- 技術挑戰：在最少控制點下達成最接近理論極限的成績。
- 影響範圍：TTLT/AVG_WAIT/TTFT 皆貼近理論極限（皆 ~100.0x%）。
- 複雜度評級：中-高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 避免 ThreadPool 行為不確定，直接管理 threads。
  2. per-step workers 與 BlockingCollection 的精準搭配。
  3. 明確 CompleteAdding 與 Join 保證閉合。
- 深層原因：
  - 架構層面：典型 Producer/Consumer pipeline 最佳實踐。
  - 技術層面：精準 thread 控制與同步關閉。
  - 流程層面：以理論上限為目標倒推設計。

### Solution Design（解決方案設計）
- 解決策略：每步驟啟動等於上限數量的 threads；完成後立即移交下一段隊列；最後逐段 CompleteAdding + Join 收尾。

- 實施步驟：
  1. 建立三段隊列與 workers（5/3/3）
     - 預估時間：1 小時
  2. 投入所有 tasks 至 q1，逐段 CompleteAdding，逐批 Join
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```csharp
for (int step=1; step<=3; step++)
  for (int i=0; i<counts[step]; i++)
    { var th = new Thread(DoAllStepN); th.Start(step); threads.Add(th); }

foreach(var t in tasks) queues[1].Add(t);

for (int step=1; step<=3; step++)
{
  queues[step].CompleteAdding();
  for (int i=0; i<counts[step]; i++) { threads[0].Join(); threads.RemoveAt(0); }
}
```

- 實際案例：AndrewDemo.AndrewPipelineTaskRunner1
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 174,450.21（↓87.80%）、AVG_WAIT 85,880.53（↓88.00%）、TTFT 1431.96（↑0.037%）
- 改善幅度：貼近理論極限

Learning Points（學習要點）
- 核心知識點：專屬 thread 與 BlockingCollection 的黃金組合
- 技能要求：thread/sync、BlockingCollection、管線化
- 延伸思考：是否改 Channel 更簡潔？如何首件最短（TTFT）？
- Practice：把此法移植成 Channel 版本（8 小時）
- Assessment：TTLT/AVG_WAIT ≤ 100.5%

------------------------------------------------------------

## Case #12: 管線以 PLINQ 取代自管 threads 的代價（AndrewPipelineTaskRunner2）

### Problem Statement（問題陳述）
- 業務場景：將原本自管 threads 的管線，改用 PLINQ 以求簡潔，但 TTLT 出現明顯退化。
- 技術挑戰：通用排程 vs. 精準自管的效能落差。
- 影響範圍：TTLT 約 132.46%（相比理論值）；AVG_WAIT 131.83%；TTFT 正常。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 交由 PLINQ 的排程在本題型不是最佳。
  2. per-step 精準控制降級，交接時機鬆動。
  3. 容易產生非最短的整體路徑。
- 深層原因：
  - 架構層面：精準度 vs. 簡潔度的取捨。
  - 技術層面：PLINQ 的負載平衡與 per-step 上限不吻合。
  - 流程層面：未特化瓶頸步驟（Step1/Step3）。

### Solution Design（解決方案設計）
- 解決策略：若採 PLINQ，須補 per-step gating 與「交接時機」的強化；否則維持自管 threads。

- 實施步驟：
  1. 以 PLINQ 架起 ForAll，內部以 ContinueWith 維持順序
  2. 補 per-step 界面（Queue/Semaphore）避免失控

- 關鍵程式碼/設定（概念近似 AndrewThreadTaskRunner2，下案提供）：

- 實際案例：AndrewDemo.AndrewPipelineTaskRunner2
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 231,005.40（↓83.86%）、AVG_WAIT 113,182.32（↓84.19%）、TTFT 1431.63（+0.01%）
- 改善幅度：雖優於 Baseline，但顯著劣於自管 threads 管線

Learning Points（學習要點）
- 核心知識點：精準控制的重要性；PLINQ 適用範圍
- 技能要求：PLINQ、ContinueWith、併發邊界
- 延伸思考：如何在 PLINQ 下補 per-step pipeline？
- Practice：補 per-step Channel 後再測（2 小時）
- Assessment：TTLT 至少拉回 ≤105%

------------------------------------------------------------

## Case #13: PLINQ + ContinueWith 鏈式步驟（AndrewThreadTaskRunner2）

### Problem Statement（問題陳述）
- 業務場景：用 AsParallel + WithDegreeOfParallelism 控總體並發，在 ForAll 內以 ContinueWith 串 Step1→3，讓 .NET 排程依關聯順序優化。
- 技術挑戰：在保持高可讀性的同時，取得接近最佳的吞吐。
- 影響範圍：TTLT 102.79%；AVG_WAIT 102.05%；TTFT 100.64%。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. ContinueWith 傳遞依賴，利於 .NET 安排鄰近執行。
  2. WithDegreeOfParallelism 讓排程不失控。
  3. 仍有 .NET 排程非決定性，TTFT 略高。
- 深層原因：
  - 架構層面：單層並發 + 內部鏈式保障順序。
  - 技術層面：PLINQ 資源調度優勢。
  - 流程層面：以低複雜度換可接受結果。

### Solution Design（解決方案設計）
- 解決策略：一行式平行＋鏈式步驟，交由 .NET 排程，適合實戰快速落地。

- 實施步驟：
  1. 建立 AsParallel + WithDegreeOfParallelism
  2. ForAll 內用 ContinueWith 串步驟，最後 Wait

- 關鍵程式碼/設定：
```csharp
tasks.AsParallel()
  .WithDegreeOfParallelism(11)
  .ForAll(t =>
  {
      Task.Run(()=>t.DoStepN(1))
       .ContinueWith(_=> t.DoStepN(2))
       .ContinueWith(_=> t.DoStepN(3))
       .Wait();
  });
```

- 實際案例：AndrewDemo.AndrewThreadTaskRunner2
- 實作環境：同上
- 實測數據（對比 Baseline）：
  - TTLT 179,261.11（↓87.47%）、AVG_WAIT 87,612.93（↓87.76%）、TTFT 1438.07（↑0.47%）

Learning Points（學習要點）
- 核心知識點：PLINQ + ContinueWith 的秩序提示
- 技能要求：PLINQ/TPL、ContinueWith
- 延伸思考：若 per-step 上限需強制，如何整合 Channel？
- Practice：分別測 7/11/15 併發度差異（2 小時）
- Assessment：TTLT 105% 以內、程式碼簡潔

------------------------------------------------------------

## Case #14: Pipeline 變體（Nathan）：接近理想的通用解

### Problem Statement（問題陳述）
- 業務場景：採用管線化並對齊每步驟併發上限，實作上與 JW/Phoenix 類似但具不同實務取捨。
- 技術挑戰：在通用排程與自管之間平衡。
- 影響範圍：TTLT 100.05%；AVG_WAIT 102.00%；TTFT 100.23%。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：per-step 並發落實；背壓/交接掌握良好。
- 深層原因：
  - 架構層：經典 pipeline 最佳實務。
  - 技術層：通用排程的微幅不確定。
  - 流程層：平均等待略高於最佳。

### Solution Design（解決方案設計）
- 解決策略：BlockingCollection/Channel + per-step workers；必要時加 ThreadPool 調參。

- 實施步驟：
  1. 建三段倉庫與工作者
  2. 完成後通知/關閉

- 關鍵程式碼/設定：同 Case #11/#8 概念（略）

- 實際案例：NathanDemo.NathanTaskRunner
- 實作環境：同上
- 實測數據：
  - TTLT 174,471.30（↓87.80%）、AVG_WAIT 87,571.79（↓87.76%）、TTFT 1432.23

Learning Points
- 核心知識點：管線穩態最佳化
- 技能要求：BlockingCollection or Channel
- Practice：嘗試 capacity 調整（2 小時）
- Assessment：TTLT/AVG_WAIT ≤ 102%

------------------------------------------------------------

## Case #15: Pipeline 變體（Boris）：極接近理想

### Problem Statement（問題陳述）
- 業務場景：同屬管線化範式，整體指標幾乎貼齊理想值，作為穩健範本。
- 技術挑戰：維持穩態下少量調度抖動。
- 影響範圍：TTLT 100.03%；AVG_WAIT 102.10%；TTFT 100.48%。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：per-step 並發落實；移交/背壓正確。
- 深層原因：微幅非決定性調度。

### Solution Design（解決方案設計）
- 解決策略：同 Case #11/#8，框架化可複用。

- 實施步驟：同上（略）

- 實際案例：BorisDemo.BorisTaskRunner
- 實作環境：同上
- 實測數據：
  - TTLT 174,442.46（↓87.80%）、AVG_WAIT 87,657.74（↓87.76%）、TTFT 1435.82

Learning Points
- 核心知識點：穩定度 vs. 最佳化
- Practice：壓 TTFT 的策略（2 小時）
- Assessment：TTLT ≤ 101%

------------------------------------------------------------

## Case #16: Pipeline 變體（Jolin）：穩健但 TTFT/AVG_WAIT 稍高

### Problem Statement（問題陳述）
- 業務場景：管線化策略成熟，整體穩健，但 TTFT/AVG_WAIT 略高於最佳。
- 技術挑戰：首件回應與平均等待的微調。
- 影響範圍：TTLT 100.17%；AVG_WAIT 102.37%；TTFT 100.32%。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：交接/排程有極小延遲。
- 深層原因：通用排程的特性；未特化首件。

### Solution Design（解決方案設計）
- 解決策略：針對第一批任務專路徑；其餘維持穩定管線。

- 實施步驟：
  1. 對前 5 件（Step1 上限）優先級特化
  2. 其餘正常流

- 實際案例：JolinDemo.JolinTaskRunner
- 實作環境：同上
- 實測數據：
  - TTLT 174,680.88、AVG_WAIT 87,885.69、TTFT 1433.53

Learning Points
- 核心知識點：TTFT 優化對 UX 的影響
- Practice：加入首批快速通道（2 小時）
- Assessment：TTFT ≤ 100.1%

------------------------------------------------------------

## Case #17: Pipeline 變體（Levi）：TTFT 明顯偏高

### Problem Statement（問題陳述）
- 業務場景：整體 TTLT 接近理想，但 TTFT 偏高（107.17%），顯示首件回應有顯著延遲。
- 技術挑戰：如何在不犧牲 TTLT 下壓低 TTFT。
- 影響範圍：TTLT 100.18%；AVG_WAIT 102.59%；TTFT 107.17%。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：首件未走最短路徑；初期啟動延遲。
- 深層原因：排程預熱/擴張、首批未特化、併發度 ramp-up。

### Solution Design（解決方案設計）
- 解決策略：首批預熱；優先保證 Step1→2→3 的直通路徑，保證 TTFB/TTFT。

- 實施步驟：
  1. 預先建立（warm up）Step2/Step3 的 worker 與緩衝
  2. 對第一個任務以同步連貫方式處理

- 實際案例：LeviDemo.LeviTaskRunner
- 實作環境：同上
- 實測數據：
  - TTLT 174,711.30、AVG_WAIT 88,077.96、TTFT 1531.44

Learning Points
- 核心知識點：TTFT 代表 UX 體感；預熱/直通路徑
- Practice：加入 warmup 與首件直通（2 小時）
- Assessment：TTFT 降回 ≤101%

------------------------------------------------------------

## Case #18: 以 CSV 可觀測性查出 600ms 排程間隙（TTFT 微調）

### Problem Statement（問題陳述）
- 業務場景：即使整體吞吐接近理想，TTFT 仍偏高；需定位 Step 交接延遲來源。作者提供 csv（TS/MEM/WIP/THREADS/ENTER/EXIT/T1~T30）供精準診斷。
- 技術挑戰：從多維度資料定位「第一個」任務的跨步驟延遲（如 Julian 案的 ~600ms）。
- 影響範圍：TTFT 偏高；平均等待略升；整體吞吐不受影響。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Step1→2 的交接未立即被排程。
  2. ThreadPool/Task 排程的非決定性插入其他工作。
  3. 首批任務未被優先。
- 深層原因：
  - 架構層面：缺乏首件優先策略。
  - 技術層面：缺少同步連續（sync continuation）保障。
  - 流程層面：缺乏專注 TTFT 的 KPI 驅動。

### Solution Design（解決方案設計）
- 解決策略：用 csv 可視化 T1~T30，鎖定首件 Task Id 在各 TS 的位置；引入首件特化（同步直通或高優列）。

- 實施步驟：
  1. 以 Excel 繪圖/條件格式框出 TaskId#Step 的時序
     - 預估時間：0.5 小時
  2. 對首件加入同步連貫或專用 worker
     - 預估時間：1 小時

- 關鍵程式碼/設定（示意）：
```csharp
// 若偵測到第一個任務，使用同步直通確保 TTFT
var first = tasks.First();
first.DoStepN(1); first.DoStepN(2); first.DoStepN(3);
// 其餘走一般管線
```

- 實際案例：Julian 範例中觀測首件 Step2 延遲 ~600ms
- 實作環境：同上
- 實測數據：
  - 改善前：TTFT 約 1448.28 ms（+1.18%）
  - 改善後：預期可收斂至 ≤100.5%（依策略）
  - 改善幅度：視策略而定，常可降 0.5~1.0%

Learning Points（學習要點）
- 核心知識點：可觀測性 → 問題定位 → 精準微調
- 技能要求：CSV 解析、Excel 圖表、時間序列閱讀
- 延伸思考：能否以 tracing/profiler 自動化此過程？
- Practice：用 csv 多組對照找出各案 TTFT gap（2 小時）
- Assessment：能舉證定位延遲點且提出修正策略

------------------------------------------------------------

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 1（Baseline）
  - Case 2（反例：無上限併發）
  - Case 9（TPL + Semaphore）
- 中級（需要一定基礎）
  - Case 3（CPU 核誤用矯正）
  - Case 4（Pipeline 缺口修正）
  - Case 5（RX + Semaphore）
  - Case 6（Channel Async 管線）
  - Case 7（工作者數量調校）
  - Case 8（ThreadPool 調優）
  - Case 10（PLINQ Partitioner）
  - Case 12（PLINQ 管線退化）
  - Case 13（PLINQ + ContinueWith）
  - Case 14/15/16/17（多種管線變體）
  - Case 18（CSV 診斷 TTFT）
- 高級（需要深厚經驗）
  - Case 11（自管 threads + BlockingCollection 精準管線）

2) 按技術領域分類
- 架構設計類：Case 1, 4, 7, 8, 10, 11, 12, 14-17
- 效能優化類：Case 3, 5, 6, 8, 11, 13, 18
- 整合開發類：Case 5（RX）、Case 6（Channel）、Case 10/13（PLINQ/TPL）
- 除錯診斷類：Case 18（CSV）、Case 3/4/6（TTFT gap 診斷）
- 安全防護類：不適用（本題聚焦效能/資源）

3) 按學習目標分類
- 概念理解型：Case 1, 2, 11（baseline/反例/理想實踐）
- 技能練習型：Case 5, 6, 10, 13（RX/Channel/PLINQ）
- 問題解決型：Case 3, 4, 7, 8, 12, 18（對症下藥）
- 創新應用型：Case 8, 11（ThreadPool 調優、精準自管 threads）

案例關聯圖（學習路徑建議）
- 先學哪些案例？
  1) Case 1（Baseline）→ 2（反例）→ 3（修正觀念）  
  2) Case 11（精準管線的理想）作為心中目標與範本
- 依賴關係：
  - Case 4（平行缺口修正）依賴管線概念（Case 11）
  - Case 5/6（RX/Channel）依賴基本管線概念（Case 11）
  - Case 8（ThreadPool 調優）依賴 pipeline 與背壓（Case 11）
  - Case 10/13（PLINQ/TPL）依賴並行概念（Case 3）
  - Case 18（CSV 診斷）貫穿所有案例
- 完整學習路徑建議：
  - 階段一（基礎）：Case 1 → Case 2 → Case 3
  - 階段二（管線核心）：Case 11 → Case 4 → Case 8
  - 階段三（技術分支）：Case 6（Channel）/ Case 5（RX）/ Case 10（PLINQ）
  - 階段四（落地比對）：Case 14/15/16/17（多案對照）→ Case 12/13（取捨）
  - 階段五（觀測與微調）：Case 18（CSV）反覆迭代，將 TTFT/TTLT/AVG_WAIT 壓至目標

備註
- 理論值（文內推導）：TTFT ≈ 1429ms；TTLT ≈ 174,392ms；AVG_WAIT 以 JW 成績 85,855.17ms 為 100% 基準。上述各案之「%」與數值引用自文內表格或推導。