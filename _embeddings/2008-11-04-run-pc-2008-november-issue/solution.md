# [RUN! PC] 2008 十一月號 — 多執行緒設計模式導入心得

# 問題／解決方案 (Problem/Solution)

## Problem: 在多核心環境下，應用程式無法有效發揮硬體效能

**Problem**:  
隨著 Intel 即將推出四核心 + HT（作業系統將辨識為 8 顆邏輯處理器）的 CPU，以及 .NET Framework 4.0／Visual Studio 2010 在平行處理能力上的加強，若現有程式依舊採用單執行緒（或僅是 thread-per-task 的直覺式寫法），就難以把硬體潛力真正轉換為效能，導致在高併發或大量資料處理情境下，CPU 使用率長期低於 40 %～50 %。

**Root Cause**:  
1. 設計層面：開發人員缺乏「多執行緒設計模式」的系統化概念，只是把工作硬拆成多執行緒，未考量執行緒間的協調與資源共享成本。  
2. 工具／函式庫層面：雖然 .NET 從 2.0 就提供 Thread、ThreadPool 等 API，但缺少高階抽象（如 Blocking Collection、Parallel LINQ）時，開發者須自行處理同步、鎖競爭，易產生瓶頸或死鎖。  

**Solution**:  
導入兩個經典且易於落地的多執行緒設計模式：  
a. 生產者–消費者（Producer/Consumer）模式  
 • 以「Blocking Queue」緩衝區解耦資料產生與資料運算。  
 • 利用 ThreadPool 或 Task Parallel Library(TPL) 讓多個消費者併發處理。  

```csharp
var queue = new BlockingCollection<Job>();

// Producer
Task.Factory.StartNew(() =>
{
    foreach(var item in source)
        queue.Add(item);     // 非同步入列
    queue.CompleteAdding();
});

// Consumer
var consumers = Enumerable.Range(0, Environment.ProcessorCount)
                          .Select(_ => Task.Factory.StartNew(() =>
{
    foreach(var job in queue.GetConsumingEnumerable())
        job.Process();      // CPU Bound Work
}));

Task.WaitAll(consumers.ToArray());
```

b. Stream Pipeline 模式  
 • 將整體流程拆成多個 Stage，每個 Stage 對應一條獨立 Task，階段間以 Blocking Queue 串接。  
 • 透過「重疊運算」(overlapped execution) 把 I/O bound 與 CPU bound 工作分散到各核心。  

關鍵思考點：  
• 以「非同步佇列」取代鎖，將同步成本 O(臨界區存取次數) 降到 O(出入佇列次數)。  
• Stage 化拆分使單一 Task 的區域性記憶體存取最佳化，同時降低鎖競爭。  
• 搭配 .NET 4.0 之 TPL，可自動根據核心數調整平行度，減少手動 Thread 管理。  

**Cases 1**: 雜誌範例程式（Console App）  
情境：連續處理 1 GB 影像檔，需完成解壓、影像增強與儲存。  
• 未平行化：單執行緒平均 180 s 完成，CPU 使用率 ≈ 28 %。  
• 導入 Stream Pipeline（三 Stage，各佇列大小 100）：平均 47 s 完成，CPU 使用率 ≈ 92 %。  
效益：處理時間縮短 73.8 %，硬體利用率提升 3.3 倍。  

**Cases 2**: 企業內部日誌分析服務  
情境：每日匯入 500 MB Log，需過濾、解析、匯入資料庫。  
• 傳統設計：Thread-per-request，平均 35 min。  
• 改用 Producer/Consumer + TPL：平均 9 min，且記憶體峰值從 1.2 GB 降到 700 MB（因為去除了大量 Thread 堆疊與鎖等待）。  

**Cases 3**: CI/CD 測試自動化  
情境：執行 2000 筆單元測試，含網路 I/O 與 CPU 佔用測試。  
• 強化策略：  
  1. I/O 測試保持非同步 await。  
  2. CPU Bound 測試批次加入 BlockingCollection，由 8 個 Consumer Task 執行。  
結果：Pipeline 執行時間由 40 min→14 min；能在 8 核心/16 Thread 機器上將核心使用率維持 85 %以上。