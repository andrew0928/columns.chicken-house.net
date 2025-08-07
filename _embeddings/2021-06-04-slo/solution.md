```markdown
# 非同步系統服務水準（SLO）保證案例

# 問題／解決方案 (Problem/Solution)

## Problem: 驗證簡訊在行銷尖峰時段大量延遲，無法於 5 秒內送達

**Problem**:  
‧ 情境：同一支「簡訊推送服務」同時處理「會員驗證簡訊」與「行銷簡訊」。  
‧ 尖峰（如周年慶）行銷訊息暴增，Message Queue 堆積，造成驗證簡訊排隊。  
‧ 使用者常於 5 秒內等待驗證碼，超時即中斷註冊流程。

**Root Cause**:  
1. 不同優先級業務共用同一條 Message Queue 與同一批 Worker。  
2. 兩種流量特性不同，行銷訊息量大且可延遲，驗證訊息量小但需即時，導致資源競爭。  
3. 缺乏對「Queue 長度 / 處理延遲」等 SLI 的即時監控與告警。

**Solution**:  
1. 量化流程時間  
   ```text
   {A} = (2) - (1)  // 前端準備時間  
   {B} = (3) - (2)  // Queue 等待時間  
   {C1}= (4) - (3)  // Worker 執行時間
   SLO : {A}+{B}+{C1} ≤ 5 sec
   ```  
2. 在程式碼中於 (1)~(4) 位置寫入時間戳，使用 Azure Application Insights / CloudWatch `TrackMetric` API 上報。  
3. 新增 SLI：`QueueLength (D)`，建立儀表板 + 告警 (A+B>5s 或 D 達閾值)。  
4. 依據限制理論(TOC)拆出兩條產線  
   ‧ 「驗證簡訊 Queue」(高優先) → 獨立 Worker Pool。  
   ‧ 「行銷簡訊 Queue」(低優先) → 原 Worker Pool。  
5. 如 QueueLength(驗證) / Rate > 30s 自動觸發 Rope：  
   ‧ API 回傳「系統忙碌」給前端；或  
   ‧ Feature Toggle 換用備援驗證方案（語音撥號等）。

**Cases 1**:  
・雙十一尖峰：驗證 QueueLength 保持 < 300，99.8% 訊息 3.2 秒內送達；行銷訊息延遲允許至數分鐘仍全部完成。  

**Cases 2**:  
・Dashboard 監控：Received 15K/min，Dequeue-Over-SLO < 0.5%，紅燈比率由 12% ↓ 0.3%。  

---

## Problem: 一味 Scale-Out Worker 雖能止血，但雲端費用飆升

**Problem**:  
‧ 解決延遲後持續加開 Worker Instance，當日帳單暴漲 3 倍。  
‧ 成本壓力使方案不可持續。

**Root Cause**:  
1. 缺少「成本」維度的量化指標，無法即時觀測。  
2. 單純加機器同時也加速行銷簡訊，無差別燒錢。  
3. Worker 實例使用率低（CPU、RAM 閒置）。

**Solution**:  
1. 引入「相對成本單位」SLI  
   ```text
   CostUnit = 1 core + 2GB RAM + 1hr
   ```  
   每類任務上報消耗的 CostUnit 累計。  
2. Process Pool：多 Task 共用同一 VM，多進程動態配置核心 / 記憶體，提高單 VM 使用率。  
3. 依成本–效能曲線決策：  
   ‧ 驗證簡訊 SLO 5s → 保留 3 台高規 Worker。  
   ‧ 行銷簡訊改用 Spot/低規 VM。  
4. 在 CloudWatch 建立 CostUnit × SLO 雙軸圖，Ops 以「SLO 達 99% 且日成本 ≤ 1.2x 基準」為營運目標。

**Cases 1**:  
・同樣 5s SLO 前提下，Worker 台數 18→6，月成本 下降 58%。  

**Cases 2**:  
・Process Pool 上線首月 CPU 利用率由 22% ↑ 71%，仍維持驗證訊息 5 秒內達標。

---

## Problem: 優化局部後觸發新瓶頸，資料庫被交易後處理 Worker 壓垮

**Problem**:  
‧ 交易後處理 Task Worker Scale-Out 後處理量大增，DB 連線飆滿，反而拖慢線上交易。  

**Root Cause**:  
1. 真正瓶頸是共享 Database，但監控指標只到 Worker 出口。  
2. 局部最佳化使非關鍵任務過度消耗瓶頸資源。  
3. 缺乏對 DB 負荷的「Protection／Buffer／Rope」機制。

**Solution**:  
1. 追加 DB 指標：連線數、Avg Query Time，辨識新瓶頸。  
2. 在交易後處理 Worker 實作 Rate Limiter  
   ```csharp
   var semaphore = new SemaphoreSlim( maxOpsPerSec );
   await semaphore.WaitAsync();
   try { /* DB work */ }
   finally { semaphore.Release(); }
   ```  
   或使用 Token Bucket/Leaky Bucket 演算法限制 QPS。  
3. 設置 Buffer：交易後處理獨立 Queue，QueueLength 上限 → 超限自動降速/丟回重排。  
4. 建立 Rope：當 DB Avg Query > 閾值自動下調 Worker 併發，釋放資源給交易系統。

**Cases 1**:  
・限制 Worker 併發後，DB CPU 從 90% ↓ 55%，交易 API P95 Latency 從 1.2s ↓ 220ms。  

**Cases 2**:  
・整體日訂單量 +18%，交易後處理仍可於 5 分鐘 SLA 內完成，且未新增 DB 伺服器。

---

## Problem: 團隊無法明確定義、量測 SLO，導致「說不清、管不到、救不了」

**Problem**:  
‧ 「時間維度」需求（延遲、成功率）寫不進 spec；  
‧ 監控只看 CPU/Mem，無法回應業務「到底會不會超時？」的問題。

**Root Cause**:  
1. 缺乏將「服務品質」分解為可量測 SLI 的方法論。  
2. 沒有在開發階段就設計探針 (Instrumentation) 與 Metrics API。  
3. Dev 與 Ops 斷鏈，無法用同一套資料說話。

**Solution**:  
1. SLO → SLI 拆分流程  
   ‧ 列步驟 → 標時間點 → 計算差值。  
2. 開發者模板：  
   ```csharp
   var t1 = Stopwatch.GetTimestamp();
// ...
   telemetry.TrackMetric("SMS_Time_A", (t2-t1)/TicksPerMs);
   ```  
   封裝成共用 SDK，所有微服務引用。  
3. 建立標準 Dashboard & Alert：  
   ‧ P99 Latency, Error Rate, QueueLength, CostUnit。  
4. 把指標寫進 Definition of Done；Pull Request 未補指標不允許 Merge。  
5. 週會 Review SLO vs SLA vs Cost 曲線，形成 DevOps 迴圈。

**Cases 1**:  
・導入後一個月，平均每個新功能新增 3 個自定義 Metrics，事故回報 MTTR 由 80 分鐘 ↓ 18 分鐘。  

**Cases 2**:  
・SLA 合規率（依客戶合約）從 97.2% ↑ 99.6%，客訴量減 60%。  

```
