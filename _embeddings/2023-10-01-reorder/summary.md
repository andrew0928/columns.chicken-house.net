# 架構面試題 #5: Re-Order Messages  

## 摘要提示
- 重排序需求: 大量 API Request 如需保持「到達即處理」且次序正確，就得自行實做 Re-Order Buffer。  
- 原理借鏡: TCP 對封包重組、分散式系統訊息排序與 QoS 的概念皆可套用於應用層。  
- 訊息設計: 必須包含 Sequence Number 或 Timestamp，以判斷先後與遺失。  
- 範圍界定: 需同時設計「可等待最長時間」與「可佔用最大緩衝」兩個邊界。  
- 緩衝策略: PUSH 時即判斷直送／緩存／丟棄／略過，並以事件回報。  
- 實驗模型: Command Source、Re-Order Buffer、Command Handler、Metrics 四大元件。  
- 度量指標: Push/Send/Drop/Skip 次數、Buffer Delay、Buffer Usage 讓設計可被量測。  
- 模擬環境: 以 Period、Noise、Lost Rate 產生亂序與遺失，並用 DateTime Mock 壓縮時間。  
- Buffer 尺寸效應: 緩衝太大→延遲飆高；太小→Drop 率升高，需依 SLO 找最佳值。  
- 架構心法: 以模型＋模擬先驗證 Dev 與 Ops 兩端可行性，縮短真實上線風險。

## 全文重點
作者以「收到大量 API 請求時如何確保依序處理」為題，示範一套從觀念、程式框架到監控量測的完整練習流程。  
首先強調「理解原理才能判斷是否重造輪子」，當遇到商業需求或技術限制，架構師必須具備自行實作必要機制的能力。  
訊息重新排序的核心，在於為每筆訊息加上可判斷先後的序號，並界定在時間及空間兩個維度可容忍的緩衝範圍。若先收到的訊息順序正確即直送，否則暫存於 Buffer；超時或超量則決定 Skip 或 Drop。  
作者建構四個元件：  
1. Command Source：持續產生帶序號的 OrderedCommand，並用隨機延遲及遺失模擬網路。  
2. Re-Order Buffer：實作 IReOrderBuffer 介面，負責 Push/Flush 與事件發送；內部以 SortedSet 維護暫存區，動態判斷 SEND_PASSTHRU、SEND_BUFFERED、DROP、SKIP。  
3. Command Handler：在收到正確順序後執行指令。  
4. Metrics：統計 Push、Send、Drop、Skip、Buffer Delay、Buffer Usage 等指標，並每秒輸出 CSV 以利觀察。  
接著利用 DateTime Mock 與批次腳本，對不同 period、noise、buffer_size 進行大量模擬。結果顯示：  
• Buffer 太大會因等待遺失訊息而拉長延遲；  
• Buffer 太小雖可降低延遲卻使 Drop 率暴增；  
• 當 command_noise = 500 ms、Buffer Size 介於 5~10 時，既能維持 0% Drop 又可將 Max Delay 控制於 ~800ms 內。  
最後指出尚未實作的「主動 timeout 機制」若補齊，可同時允許較大 Buffer 與受控延遲，並呼籲架構師在設計階段即以模型＋模擬驗證 Dev 與 Ops，才能把風險留在最早期。

## 段落重點
### 練習前的思考: 我需要了解這些機制嗎?
作者先回應「是否重造輪子」的疑慮：並非總要自己寫，但若屬關鍵職能便需懂原理與練習。唯有能評估並在必要時動手，才能保證系統不受現成工具限制。練習的價值是以最小投入換取未來的決策與風險控管能力。

### 1. 訊息排序的基本觀念
重排序屬「串流排序」而非一次性 sort；流程是先判斷訊息順序，正確立即處理，錯誤暫存等待。關鍵三要件：1) 訊息自帶序號或時間戳；2) 設定緩衝時間上限；3) 設定緩衝容量上限。若超限則 Skip／Drop，並透過事件告知下一層。作者提出三個元件（Source、Buffer、Handler）與 Metrics 架構並以程式介面描述之。

### 2-1. 模擬網路傳輸延遲 (隨機)
以 GetCommands(period, noise) 產生 1000 筆指令，period 為發送間隔，noise 為 0~N ms 隨機延遲。利用 Random + 固定種子保證可重現，並把 OccurAt 排序後逐筆 yield 以模擬亂序輸入。

### 2-2. 模擬網路傳輸丟失請求
加入固定機率隨機「消失」的封包，Create Test Case 演示中間缺 #5 的情況，對比 Buffer Size 大小不同時系統如何產生 SKIP 與延遲差異，驗證緩衝策略對效能及可靠度的影響。

### 2-3. 用 Buffer 串接來源與目的地
示範如何在程式中將 Source→ReOrderBuffer→Handler 串起。透過 foreach 驅動 Push，並在 CommandIsReadyToSend 事件呼叫 ExecuteCommand；Flush 於結束時清空 buffer，確保所有暫存被處理。

### 2-4. 模擬監控機制
使用 DateTime Mock 每秒觸發事件，將 Metrics 以 CSV 形式寫至 stderr，再用 shell 重導輸出檔；結合 Excel 即可快速畫出 Push/Send/Delay 等曲線，提前設計未來的監控 Dashboard。

### 3-1, 用 Buffer 來 Re-Order Command 的規則
說明串流排序演算法：維護 current_next_index 與 SortedSet 緩衝；若收到正確序號即直送，否則暫存；當 Buffer 滿且缺口仍未補齊時，優先 Skip 未到達的序號以釋放空間，再將 buffer 中連續訊息一次送出。

### 3-2, Buffer Size 越大越好嗎?
以單元測試比較 Buffer=100、3 的情境：大 Buffer 零 Drop 卻導致 Max Delay 飆高；小 Buffer 延遲低但需承擔 Skip/Drop 風險。顯示需依業務 SLO 取捨。

### 3-3. 資料結構
核心結構包含 _current_next_index、SortedSet<OrderedCommand> 及 _buffer_size。SortedSet 透過自定 IComparer 依 Position 排序並避免重複，為後續集合運算與刪除提供效率。

### 3-4, 監控指標 Metrics
定義 Push/Send/Drop/Skip 計數、buffer_max 與 buffer_delay，藉 Interlocked 保證執行緒安全並提供 ResetMetrics 同步讀清，方便外部定期拉取。

### 3-5. Push() , 驅動 Buffer 運作的引擎
Push 流程：1) 更新 metrics；2) 判斷過號直接 Drop；3) 若為當前序號即 SEND_PASSTHRU；4) 其餘進 buffer；5) 若 buffer 超量則循序 Skip 缺口；6) 依序取出可連續訊息 SEND_BUFFERED，迴圈直至容量符合限制。

### 3-6, Adapters 串聯事件機制
封裝 Send/Drop/Skip 三方法，同步更新統計並發出對應事件。外部可以註冊回呼，自由決定寫入日誌、丟入 Message Queue 或直接執行。

### 3-7. DateTime Mock
自製 DateTimeUtil 提供 Now、TimeSeek、RaiseSecondPassEvent 等能力，可任意「快轉」時間，讓單機模擬不需真實等待，亦能驗證 timeout 行為與定期度量。

### 4-1, 模擬測試 (100, 500, 10)
預設條件下 990 Push、0 Drop，Max Delay 約 1.2s。圖表顯示大部分延遲落在 100ms 內，八個高峰對應網路遺失後等待 Flush 的情境。

### 4-2, 模擬測試 (100, 100, 10)
將 noise 從 500→100，Max Delay 降至 1.13s、平均延遲減半。亂序程度降低，Delay 曲線只剩等待遺失封包的高峰。

### 4-3, 模擬測試 (100, 500, 5~1)
比較 Buffer 10→5→3→2→1：延遲隨容量遞減，但 Drop 率由 0%→0%→0.2%→3%→14%，顯示最佳 Buffer 約 5；過小就無法達成 0 Drop SLO。

### 4-4, 改善
指出仍缺「主動 timeout」機制：若搭配高精度定時器定期檢查並強制 Skip/DROP 超時訊息，可同時使用較大 Buffer 又限制延遲，真正落實以 SLO 為核心的可靠度設計。

### 5, 總結
結語回扣 DevOpsDays Keynote：架構師須以模型化＋模擬在最早階段驗證可行性，否則問題將延後數月才暴露。本文範例示範如何把 Dev（介面、演算法、測試）與 Ops（監控指標、容量/延遲評估）提前融合，將風險留在紙上與程式中解決，而非上線後才踩雷。