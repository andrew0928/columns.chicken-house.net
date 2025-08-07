```markdown
# 架構面試題 #5: Re-Order Messages

# 問題／解決方案 (Problem/Solution)

## Problem: 高併發 API 下，訊息會「亂序」到達，後端卻必須保證照順序處理

**Problem**:  
當前端或多個服務在極短時間內透過 API 大量送入資料，常見做法是直接丟進 Message Queue。  
若傳輸過程 (網路延遲、併發寫入) 造成進 Queue 的順序被打亂，後端服務在消費時就會拿到「亂序訊息」，導致：
1. 狀態更新錯亂  
2. 下游服務收到錯誤結果  
3. 需人工補單／回滾  

**Root Cause**:  
1. 傳輸層 (HTTP/UDP/Message-Broker) 天生不保證訊息順序。  
2. 缺乏「序號」與「緩衝重排」機制，造成一收到就立刻處理 → 錯序。  

**Solution**:  
1. 強制所有訊息附帶可比較的順序欄位 (Position / Timestamp / Sequence No.)。  
2. 在真正執行前以程式端 Re-Order Buffer 先行重排：  
   ```csharp
   public interface IReOrderBuffer {
       bool Push(OrderedCommand data);   // 收到就先放進 Buffer
       bool Flush();                     // 結束時清空
       event CommandProcessEventHandler CommandIsReadyToSend; // 順序正確，可執行
   }
   ```  
3. 收到資料流程  
   a. 若 Position == nextIndex → 立即送出 (SEND_PASSTHRU)  
   b. 若 Position  > nextIndex → 暫存至 SortedSet Buffer  
   c. While(可以湊成連續序列) → 依序發送 (SEND_BUFFERED)  
4. Buffer 再由 Flush() 於結束或定時把殘留訊息清空、或標示為 SKIP。  
5. 透過事件把「已排序」資料交給 Handler → 確保執行端 100% 順序正確。  

**Cases 1**: 基本亂序 (#0,1,2,3,5,4,6..)  
Buffer=100，全部重新排序送出，Drop=0，AvgDelay≈0.13 ms。  

**Cases 2**: 亂序 + 網路噪音 (period=100 ms, noise=500 ms)  
Buffer=10，990 筆全數重排成功，Drop=0；MaxDelay≈1.24 s，透過 Metrics 可持續觀察尖峰。  

---

## Problem: 部分訊息在傳輸途中永久遺失，系統可能「無限等待」，造成整體延遲失控

**Problem**:  
若序列 #5 永久遺失，但 Buffer 一直等不到它，#6 之後全部卡住，最終 SLA 延遲爆表。  

**Root Cause**:  
1. 網路天生丟包 (Lost Rate)；  
2. 演算法只考慮「空間」沒考慮「時間」，Buffer 夠大就一直等 → 延遲線性上升。  

**Solution**:  
1. 為 Buffer 加入「容量上限」與「時間／空間退讓規則」：  
   • 若 _buffer.Count > _buffer_size 且 nextIndex < buffer.Min.Position → 直接 Skip(nextIndex)  
   • 也可再加「逾時 Timer」, 逾時就 Skip。  
2. 事件回拋 SKIP / DROP 給後端，後端可補償或寫死信佇列。  
3. 透過 Metrics：Push/Send/Drop/Skip/BufferMax/Delay，每秒 Reset 監控，持續調參。  

**Cases 1**: BufferSize=100、遺失 #5  
　• Skip=1、MaxDelay≈400 ms (等待到 Flush)  

**Cases 2**: BufferSize=3、遺失 #5  
　• Skip=1、MaxDelay≈300 ms (提早放棄)  
　• 驗證「Buffer 過大反而害延遲變高」→ 找到 5~10 之間為最佳。  

---

## Problem: 尚未上線前，無法評估「最佳 Buffer Size／SLO」與維運監控需求

**Problem**:  
若直接上生產環境試錯，風險高且成本大；架構師需要在 POC 階段就給出可運作、可觀測的模型。  

**Root Cause**:  
1. 傳統只寫演算法單元測試，缺乏整體流量、網路雜訊、丟包的「系統級」驗證。  
2. 沒有即時 Metrics，無法量化「延遲—掉包—資源」三者取捨。  

**Solution**:  
1. 自製 DateTime Mock + Command Generator  
   ```csharp
   foreach(var cmd in GetCommands(period, noise)){ buffer.Push(cmd); }
   ```  
   • period 控制發包頻率  
   • noise 模擬 0~N ms 隨機延遲  
   • 1% 模擬 Lost  
2. 把 Metrics 以 CSV 輸出到 STDERR，再用 Excel/Grafana 畫圖：  
   ```
   TimeInSec,Push,Send,Drop,Skip,BufferMax,Delay
   1,100,100,0,0,4,85
   ```  
3. 用批次腳本跑多組參數矩陣 (period, noise, buffer_size)，迅速得到決策表。  
4. 得到「Buffer=5 在 noise=500ms 時 Drop=0, MaxDelay≈777ms」等可交付指標，同時生成將來上線要接 APM 的 Metric 定義。  

**Cases 1**: 30 組自動化實驗，多數業務流量落在 (period=70ms, noise=300ms) 時，Buffer 5 就能穩定 0 Drop、MaxDelay<800ms。  
**Cases 2**: 透過圖表立即發現 Buffer=1 時 Drop>10%，提早避免錯誤配置進產線。  
```