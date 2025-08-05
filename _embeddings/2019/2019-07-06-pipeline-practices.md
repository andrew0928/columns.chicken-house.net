---
- source_file: /docs/_posts/2019/2019-07-06-pipeline-practices.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# 後端工程師必備: 平行任務處理的思考練習 (0916補完)

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "後端工程師必備: 平行任務處理的思考練習 (0916補完)"
categories: []
tags: ["系列文章", "架構師", "Practices"]
published: true
comments: true
use_disqus: false
use_fbcomment: true
redirect_from:
logo: /wp-content/images/2019-07-06-pipeline-practices/logo.png

# 自動識別關鍵字
primary-keywords:
  - 平行任務處理
  - 生產者/消費者模型
  - Pipeline
  - WIP (Work In Progress)
  - TTFT / TTLT / AVG_WAIT
  - BlockingCollection
  - ThreadPool / Task
  - MyTask 三步驟
secondary-keywords:
  - SemaphoreSlim
  - PLINQ / TPL
  - System.Threading.Channels
  - Reactive Extensions (Rx)
  - Benchmark & Profiling
  - CSV Trace-Log
  - Code Review
  - GitHub Pull Request

# 技術堆疊分析
tech_stack:
  languages:
    - C#
  frameworks:
    - .NET Core / .NET 5+
    - Task Parallel Library (TPL)
    - Parallel LINQ (PLINQ)
    - Reactive Extensions (Rx)
  tools:
    - Visual Studio 2019
    - dotnet CLI
    - GitHub Actions / PR
    - CSV / Excel for Profiling
  concepts:
    - Producer-Consumer Queue
    - Concurrency Limit & Semaphore
    - Memory Footprint Control
    - Performance Metrics (Lead-Time, Throughput)
    - Thread vs Task vs ThreadPool
    - Pipeline Pattern

# 參考資源
references:
  internal_links:
    - /2019/06/15/netcli-pipeline/
    - /2019/06/20/netcli-tips/
  external_links:
    - https://github.com/andrew0928/ParallelProcessPractice
    - https://docs.microsoft.com/dotnet/standard/parallel-programming
    - https://www.dotnetcurry.com/dotnetcore/1509/async-dotnetcore-pattern
    - https://docs.microsoft.com/dotnet/standard/parallel-programming/custom-partitioners-for-plinq-and-tpl
  mentioned_tools:
    - Visual Studio Profiler
    - Csv Viewer / Excel

# 內容特性
content_metrics:
  word_count: 11500
  reading_time: "35 分鐘"
  difficulty_level: "中高階"
  content_type: "教學 + Code Review"
```

## 文章摘要
本文以一個「三步驟 MyTask × 1000」的實戰練習，帶領後端工程師體驗如何在嚴格的併發限制、記憶體上限與效能目標下，精準地設計並驗證平行任務處理方案。作者先公布題目與評分指標：每步驟最大並行數、記憶體配置、WIP、TTFT、TTLT 及平均等待時間，並提供最基礎的 for-loop Demo 做為墊底基準。透過 Console 與 CSV Trace，可視覺化觀察執行緒使用、記憶體曲線與 Task 佈局，協助參與者自我診斷。  
接著解析指標背後的意義，計算理論極限 (TTLT ≈ 174.4s；AVG_WAIT ≈ 87.9s) 以做為優化參考。9/16 公布的 Part II 彙整 13 份 PR，將解法分為三大類：1) 純多工 (Thread/Task/PLINQ)；2) 明確的 Pipeline/BlockingCollection/Channel；3) 其他實驗性實作。作者逐一 Code Review，說明優缺點與適用情境，並以自己的 PipelineThread 版本示範如何同時在三項關鍵指標都落於理論值 0.5% 內。  
文章最後提醒：掌握「期望行為 → 理論極限 → 量化指標 → 精準驗證」的思維，比熟記任何框架都重要；當你能快速用簡潔程式碼逼近極限，就能把雲端成本與維運風險降到最低。

## 段落摘要

### 1. 寫在前面
承接前兩篇 CLI/Pipeline 文章，作者提出「精準控制」的練習題，目的讓工程師重新審視多執行緒與平行處理的基礎功，而非倚賴外部框架救火。

### 2. 題目與限制說明
透過 `MyTask` (Step1~3) ×1000，要求順序執行、步驟並行上限、各步驟耗時與記憶體配置，並公開可自訂的 `PracticeSettings.cs` 參數。

### 3. 評量指標與輸出格式
定義 Max WIP、Memory Peak、TTFT、TTLT、Avg Wait，搭配 Console Summary 及 CSV Trace，方便用 Excel 畫圖了解行為。

### 4. 品質指標意義
說明 WIP 代表資源佔用，TTFT 關係使用者體驗，TTLT 代表整體吞吐，AvgWait 平衡兩端；不同場景需挑選最重要指標先優化。

### 5. 理論極限推導
以每步驟耗時與並發上限計算瓶頸，推得 TTLT 最佳值約 174 392 ms，AvgWait 約 87 868 ms；先掌握極限才能判斷優化是否值得。

### 6. Solution Review & Benchmark
收錄 13 份 PR，共 18 組 Runner；分類為「無腦多工」、「Pipeline / BlockingCollection / Channel」、「其他」。提供總表並依序評論每位參與者的設計、陷阱與改進點。

### 7. 作者示範解法
展示 `AndrewPipelineTaskRunner1`：為每步驟各開固定 Thread 群＋BlockingCollection 緩衝，精準交棒，將三項指標都逼至理論值 0.5% 內。

### 8. 結語與延伸
真正關鍵在於「找出問題本質 → 量化 → 持續驗證」，不是框架選型。鼓勵讀者將練習題 Fork 下來，調整參數、重跑 Benchmark，體驗性能調校思維。

## 問答集

Q1（概念）什麼是 WIP，為何要控制？  
A: WIP 指任務處於「進行中但尚未完成」的數量。每個 WIP 都持續佔用記憶體與其他資源，若無限制平行啟動，可能造成 OOM 或上下文切換成本暴增，因此需在吞吐與資源之間取得平衡。

Q2（操作）CSV Trace 檔中的 `T1~T30` 欄位代表什麼？  
A: 這 30 欄分別對應最多 30 條工作執行緒，值為「TaskId#Step」。透過時間序列可觀察 Thread 何時空檔、併發限制是否達標，以及步驟是否依序銜接。

Q3（排除）TTFT 特別大但 TTLT 正常，常見原因？  
A: 多半是第一批 Task 未立即銜接 Step1→Step2→Step3，或序列化前置動作佔用過久 (e.g. 先建立大量 Task/Thread)。針對首批任務可預熱 ThreadPool 或改用同步呼叫減少暖機成本。

Q4（操作）如何用 BlockingCollection 建立雙向流？  
A: 建立三個 `BlockingCollection<MyTask>` 代表三段，第一段完成後 `Add()` 至第二段。各段使用 `GetConsumingEnumerable()` 迴圈消費；完成後 `CompleteAdding()` 通知下游收尾。

Q5（比較）ThreadPool 與自管 Thread 有何取捨？  
A: ThreadPool 易用且動態調整，但難保證啟動順序與核心佔用；自管 Thread 可精準綁定並行數與專責任務，適合瓶頸已知且指標要求嚴格的關鍵路徑。

Q6（概念）為什麼要先估理論極限？  
A: 沒有目標值就難衡量優化成效，也可能在已貼近極限時仍投入大量心力。先算極限可判定方法是否可行，並避免過度優化。

Q7（比較）Pipeline vs 無腦多工何時選？  
A: Pipeline 可精準掌握順序、限制與資源，適合長鏈式作業；無腦多工 (TPL/PLINQ) 開發快、泛用度高，適合步驟間耦合低、資源充裕的場合。

Q8（排除）平行度調太高導致效能下降怎麼診斷？  
A: 觀察 WIP 與 Memory Peak 是否暴增、CSV 中 Thread 空轉是否大量存在；降低 `DegreeOfParallelism` 或使用 Semaphore 限制並發並重測。

Q9（概念）TTLT 與 AvgWait 差距很大代表什麼？  
A: 代表前段 Pipeline 長時間塞車，導致後段大批任務集中收尾。需檢查瓶頸步驟是否平行數不足或工作分配不均。

Q10（操作）如果想改用 Channel 實作，要注意哪些設定？  
A: 建議使用 `BoundedChannelOptions` 設定容量以避免無邊際緩衝，並開啟 `SingleWriter/SingleReader` 及 `AllowSynchronousContinuations` 以降低 context-switch 開銷。

## 問題與解決方案整理

### 問題一：無法兼顧 TTFT 與 TTLT
Root Cause  
1. 首批任務等待 ThreadPool 暖機  
2. 步驟間未即時交棒

Solutions  
1. 在 `Main` 啟動前呼叫 `ThreadPool.Preheat()` 或先跑 Dummy Task  
2. 改用 Pipeline＋BlockingCollection，在 `ContinueWith` 中立即推送至下一步

Example  
```csharp
ThreadPool.SetMinThreads(16, 16);
BlockingCollection<MyTask> q1 = new(100);
```

### 問題二：WIP 暴增導致記憶體爆表
Root Cause  
大量 Task 同時排進 ThreadPool，未考量每步驟記憶體配置

Solutions  
1. 以 SemaphoreSlim 精確限制每步驟併發  
2. 為每步驟建立專屬 Thread 群並設定固定 Queue 容量

Example  
```csharp
static readonly SemaphoreSlim s1 = new(5);
await s1.WaitAsync(); // before DoStep1
```

### 問題三：Pipeline 吞吐不足
Root Cause  
1. 步驟 1 與步驟 3 處理時間懸殊  
2. 中繼緩衝區過小導致上下游頻繁等待

Solutions  
1. 依瓶頸計算 thread 數與 queue size，例如 Step1 5 threads、Buffer ≥ 15  
2. 定期以 CSV Trace 觀察排程空洞並調整 `BoundedCapacity`

Example  
```csharp
var ch = Channel.CreateBounded<MyTask>(new BoundedChannelOptions(20){ SingleReader=true });
```

## 版本異動紀錄
- 1.0.0 (2025-08-05)  初版生成，含 Metadata、段落摘要、10 組 Q&A 與 3 套問題-解決方案
