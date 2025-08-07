# 後端工程師必備：排程任務的處理機制練習

# 問題／解決方案 (Problem/Solution)

## Problem: Web Application 無法主動在指定時間執行工作

**Problem**:  
在傳統的 Web Application（Request / Response 被動模式）裡，若使用者想「預約」系統在未來某個時間執行工作，框架本身沒有主動觸發能力。最常見的做法是：  
1. 將工作資訊寫入資料庫  
2. 由背景排程程式定期掃描資料庫 (polling) 看是否有到期任務  
然而：  
• 若每分鐘掃一次，精度只有分鐘級，容易超時  
• 若改成每秒掃一次，精度雖高，但資料庫瞬間增加 60 倍負載  

**Root Cause**:  
• Web Framework 偏向「被動回應」設計，缺乏時間驅動 (time-driven) 能力  
• Message Queue 雖可配合 worker，但 queue 天生適合「立即」消化訊息，對「一小時後才要執行」的訊息並不合適  
• 因此只能回到「資料庫 + 輪詢」模式，形成「高精度 vs DB 負載」天秤難題  

**Solution**:  
1. 以資料表 `Jobs` 維護排程工作  
   ```
   | Id | RunAt | ExecuteAt | State |
   |----|-------|-----------|-------|
   | PK | 預定  | 實際      | 0:未執行
                        1:執行中
                        2:已完成 |
   ```  
2. 強迫所有排程工作符合  
   • MinPrepareTime >= 10s：建立後至少提早 10 秒寫入  
   • MaxDelayTime  <=30s：最晚需在 RunAt + 30 秒內開始  
3. 背景排程程式流程：  
   a. 以「可調輪詢間隔」（預設 10 秒）查詢 `RunAt <= Now+MinPrepareTime` 之未執行工作  
   b. 取得工作後先嘗試 `AcquireJobLock(jobId)` 更新狀態 = 1，確保只被一個 worker 執行  
   c. 倒數至 RunAt（可 busy wait 或 await Delay），時間到後呼叫 `ProcessLockedJob()`，狀態 = 2  
4. 透過多個 instance 部署 (generic host / container / Windows Service / systemd)，並支援 graceful-shutdown：  
   • CancellationToken 傳遞給 polling 與 worker  
   • 關機時先收尾正在執行的 job，未執行 job 解鎖或回到 queue  

5. 以評量指標量化方案優劣：  
   • Cost Score = 查清單次數×100 + Lock 失敗次數×10 + 查單筆次數×1  
   • Efficient Score = 平均延遲 + 延遲標準差  

核心思路：  
• 先以 MinPrepareTime 做「粗篩」降低 Query 次數  
• 再用 Lock + Delay 精確控制秒級啟動  
• 對 DB 而言，輪詢間隔固定成本；透過鎖定機制確保「只執行一次」並支援分散式 HA  

**Cases 1**:  
測試工具於 10 分鐘內連續排入 1,700+ Job，在 5 個 instance 執行情境下：  
• 平均延遲 ≈ 4.3 秒，標準差 ≈ 2.8 秒  
• Cost Score ≈ 119,360  
顯示在「硬秒級」需求下仍能滿足 MaxDelayTime 要求，且所有 Job 均僅被執行一次。  

**Cases 2**:  
將 polling 間隔改為 1 秒：  
• 平均延遲下降至 0.5~1 秒區間  
• 但 Cost Score 飆升 60 倍 (≈ 7,000,000)  
驗證「頻率提升 → 精度↑但成本↑」的 trade-off。  

**Cases 3**:  
在 5 個 instance 同時運行時，模擬隨機 kill 3 個 instance (HATEST)：  
• 其餘 2 個 instance 接手 queue，無任何重複執行或遺漏  
• 完成率 100%，符合高可用性目標  


## Problem: 單一排程服務無法高可用且易重複執行

**Problem**:  
一台排程服務掛掉，未完成或已鎖定的 Job 可能永遠得不到處理；多台服務若無協調機制又會產生「同一筆資料被多次執行」的悲劇。  

**Root Cause**:  
• 缺乏分散式鎖（Distributed Lock）與 Job State 管理  
• 排程服務停止時若未釋放資源，其他節點無法得知 Job 已失效  

**Solution**:  
1. 在 `Jobs` 表設計狀態碼：0=未執行、1=執行中、2=已完成  
2. AcquireJobLock(jobId) 以 `UPDATE … WHERE State=0` 一次性原子鎖定  
3. 如服務意外中斷，Lock 仍停留在 1；由 Watchdog 或下次 Polling 判斷 `RunAt + MaxDelayTime` 已過仍為 1 時，重設為 0 重新排入  
4. 部署多 Instance；每支程式皆只輪詢「未鎖定」工作，確保至多一個 Worker 取得鎖  
5. 以檔案或訊號量 (Semaphore) 控制單機 Thread 上限 (避免本機過度平行)  

**Cases**:  
• 5 Instance 連續 10 分鐘，每台隨機 Ctrl-C 模擬異常，共停掉 3 台，所有 Job 依序 fail-over 給存活機器，無重複執行現象。  


## Problem: 缺少客觀指標比較各種排程策略

**Problem**:  
單憑「感覺」優化容易流於口說無憑，不易量化「DB 負載」、「任務準確度」何者較佳。  

**Root Cause**:  
• polling / lock / query 次數往往散落在程式碼各角落，若無統計機制就難以得知真實負擔  
• 延遲精確度若只看「平均」易忽略尾端分佈，不利 SLA 管控  

**Solution**:  
1. 在 JobsRepo 中統一包裝所有 DB 操作並記錄 Log  
2. 於測試工具收斂四個指標：  
   • QueryList 次數 (重)  
   • Acquire 失敗次數 (中)  
   • QueryJob 次數 (輕)  
   • Job 延遲(平均、標準差)  
3. 定義  
   Cost Score = QL×100 + LockFail×10 + QJ×1  
   Efficient Score = AvgDelay + StdevDelay  
4. 實驗框架自動跑兩輪：  
   • Reliability Test (隨機 kill)  
   • Benchmark Test (固定 10 min)  
   測試完自動算分，輸出排行榜與 EXCEL 報表  

**Cases**:  
• 第一版 Naïve Solution (每秒 polling)：  
  Cost ≈ 7,000,000 / Efficient ≈ 500 ms  
• 優化版 (10s polling + 智慧 Lock)：  
  Cost ≈ 20,000 / Efficient ≈ 140 ms  
量化結果清楚證明「低頻 + 聰明鎖定」在成本/精度取得更佳平衡。