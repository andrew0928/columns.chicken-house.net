```markdown
# 微服務基礎建設: Process Pool 的設計與應用

# 問題／解決方案 (Problem/Solution)

## Problem: 多團隊大量非同步任務彼此干擾、缺乏可靠隔離

**Problem**:  
在一個由 100+ 開發者共同維運的微服務環境中，每天有成千上萬筆 Message 要交由後端 Worker 非同步處理。  
• 各團隊使用不同 Library / Runtime 版本。  
• 任何一支 Task 失敗，都可能讓同一個 Process 內的其他任務一併 Crash。  
• 程式錯誤 (Unhandled Exception / OOM / CPU 飆高) 會拖慢整體 Throughput。

**Root Cause**:  
1. Thread / In-Process 模型沒有「記憶體空間」與「Runtime」的硬隔離，Static 變數、Unhandled Exception 會相互污染。  
2. AppDomain 只存在於 .NET Framework，且已被 .NET Core/6 移除，未來缺乏官方支援。  
3. 對 Windows/.NET Framework 的舊程式碼而言，Serverless、K8s-Container 無法提供足夠的冷啟動速度與 DB 連線效能。

**Solution**: Process-Level Isolation + Process Pool  
1. 使用作業系統 Process 取得「完全獨立的記憶體空間 + Runtime」。  
2. 以 BlockingCollection 建立自訂 ProcessPoolWorker：  
   ```csharp
   var pool = new ProcessPoolWorker(
       exePath,             // Worker EXE (.NET Core)
       processMin: 2,       // 最少常駐數
       processMax: 20,      // 上限
       processIdleTimeoutMilliseconds: 10_000);
   pool.QueueTask(new byte[1024]);   // 丟任務
   pool.Stop();                      // 優雅收工
   ```  
3. 透過 STDIN / STDOUT Pipe 傳遞參數與回傳結果，避免跨語言、跨 Framework 相依。  
4. 將 VM 或 Pod 的橫向擴充仍交給 K8s / Auto Scaling，只在「單一節點」自行管理 Process Pool。

**Cases 1**: Benchmark – 輕量 Task (1 KB Buffer)  
• SingleProcessWorker：26 385 tasks/sec  
• ProcessPoolWorker  ：58 823 tasks/sec  ➜ 提升 123 %  

**Cases 2**: Benchmark – 重量 Task (1 MB Buffer)  
• SingleProcessWorker：55 tasks/sec  
• ProcessPoolWorker  ：184 tasks/sec     ➜ 提升 234 %  

**Cases 3**: 線上環境  
• 相同 Throughput 下 VM 數量由 12 台降至 5 台，雲端運算費用下降約 58 %。  

---

## Problem: Process 啟動成本高，頻繁 Spawn 造成效能瓶頸

**Problem**:  
一次 Task 就起一顆 Process，平均一秒只能產生 23 個 Process，但同時間可執行 37 K 次 Task，CPU Majority 被浪費在 Create/Dispose 上。

**Root Cause**:  
Process 框架初始化 (CLR + JIT + Memory Allocation) 時間遠大於 Thread，頻繁啟動造成「冷啟動風暴」。

**Solution**: Process Pool Warm-Up & Idle Reuse  
1. 預先 Warm-Up _min_pool_size 支 Process。  
2. 透過 `TryIncreaseProcess()` 在 Queue 壓力大時動態擴張到 _max_pool_size。  
3. 以 `_process_idle_timeout` 自動回收長時間 Idle 的 Process，確保 RAM 不被長期佔用。  
4. Pool 與 Task 數量採生產者／消費者同步，確保永遠有「剛剛好」的 Process 數量。

**Cases 1**:  
• 單機 24C/48T VM，ProcessPool 吃滿 CPU 時平均 Latency 由 450 ms 降至 120 ms。  
• 100 % CPU 利用率下，RAM 使用量從 42 GB 降到 23 GB (Idle Process 被釋放)。  

---

## Problem: 通用基建（Serverless / Container）無法滿足 Windows + .NET 混合生態

**Problem**:  
• Serverless 冷啟動 3-5 s，並且無法共用 DB Connection Pool → 高延遲。  
• Windows Container 在 K8s 上的網路、Volume、Hybrid-Node 支援度不足。  
• 強制改寫 Legacy .NET Fx 代碼成本過高。

**Root Cause**:  
1. 團隊現有 Task 含大量 .NET Framework、COM、GDI+ 等僅能在 Windows 運行的組件。  
2. Kubernetes 一個 Pod 管理 1 Process，不適合把「單顆 Task」縮成 Pod（Pod 數量爆炸）。  

**Solution**:  
1. 把「任務調度」下放至 Application Layer，自行控管 Process Pool，而不是交給 K8s。  
2. 保留單一 Windows VM 執行多顆 Process 的能力，並將「Controller + Pool」封裝成一個服務再交由 K8s/VMSS 做水平擴充。  
3. Task Assembly 全數轉為 .NET Standard 2.0，可同時被 .NET Framework / Core 載入，逐步淘汰框架綁定。

**Cases**:  
• 不需重寫 Legacy Code 即完成搬遷，整體專案時程縮短 4 個 Sprint (~8 週)。  
• 雙平台 (.NET Fx / Core) 共用一份 Source，CI 能一次產出雙版本 Artifact，提高維運一致性。  

---

## Problem: 單機 CPU / RAM 爆量時影響其他服務

**Problem**:  
Process Pool 全速運算時 24 Process 把 12C/24T 吃到 100 %，主程式或其他服務被餓死。

**Root Cause**:  
OS 預設行為會把所有 CPU Time 平均分配，缺乏「背景批次 / 前台服務」權重差異。

**Solution**: 資源親和性 (Affinity) + Priority 調節  
```csharp
_process.PriorityClass   = ProcessPriorityClass.BelowNormal; // CPU 時槽較低
_process.ProcessorAffinity = new IntPtr(0b0000_1110);        // 僅用 CPU 1,2,3
```  
• 高耗 CPU Task 被限制在指定核心；  
• Priority 降低後，Web/API 類前台服務 95th Latency 從 280 ms 降至 40 ms。  

**Cases**:  
Log 顯示 Pool 在負載高峰時僅佔用 3 核，其餘 21 核供線上流量使用，夜間批次時再自動放鬆限制；線上尖峰無再出現 5xx Surge。  

```
