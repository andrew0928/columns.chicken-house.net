# 生產者 vs 消費者 - BlockQueue 實作

## 摘要提示
- 多執行緒模式: 文章從「工具」轉向「模式」，說明生產者/消費者是將執行緒能力落實在程式架構上的典型做法。  
- 供需平衡: 強調兩階段工作（產生、處理）速度不一致時，必須用機制平衡，才能真正提高效能。  
- 範例情境: 以「大量下載檔案並即時壓縮」示範 IO-bound 與 CPU-bound 交錯運作的需求。  
- BlockQueue 目的: 在 .NET 中建立一個可「阻塞」而非「丟例外」的佇列，管理暫存容量。  
- 主要特性: 容量上限、空佇列/滿佇列自動阻塞、Shutdown 通知三大功能。  
- 實作技術: 以 Queue 搭配 ManualResetEvent 實作同步，封裝成泛型 BlockQueue<T>。  
- 使用方式: 生產者呼叫 EnQueue、消費者呼叫 DeQueue，主程式在所有生產完畢後呼叫 Shutdown。  
- 實測結果: 透過調整 Producer/Consumer 執行緒數量，證明隊列容量成功限制緩衝區大小。  
- 延伸改良: 建議可用 CircularQueue、Priority Queue 甚至 Pipeline、Stream 等概念再進化。  
- 實務價值: 封裝良好的 BlockQueue 能像 System.Collections.Generic 一樣可重複利用，脫離「只為作業」的範疇。  

## 全文重點
作者延續先前多執行緒技巧，進一步討論如何在實務上運用「生產者/消費者（Producer-Consumer）」模式。當工作流程可拆為前後兩段且各自適合多執行緒時，最難的是平衡兩段速度。如下載檔案與即時壓縮，下載端屬 IO bound，可用多執行緒並行；壓縮端屬 CPU bound，也可用 ThreadPool，但兩者共用暫存區，若缺乏管制便可能溢出或閒置。  
為解此題，作者實作 BlockQueue：  
1. 容量限制：當佇列滿時 EnQueue 會阻塞而非擲例外；  
2. 空佇列阻塞：DeQueue 於無資料時阻塞；  
3. 關閉機制：Shutdown 讓生產者結束後通知消費端不再等待。  
BlockQueue 內部以 Queue<T> 存資料，透過兩個 ManualResetEvent 控制「可寫」與「可讀」。EnQueue 與 DeQueue 皆用 lock 保護佇列，並依狀態設定/重置事件；若條件不符便呼叫 WaitOne() 進入阻塞。Shutdown 設定旗標並喚醒所有等待中的 DeQueue。  
範例程式啟動多個 Producer 與 Consumer 執行緒，各自隨機 sleep 以模擬不均速。測試顯示 Producer 執行緒多時，佇列長度被限制在 sizeLimit 左右；Consumer 多時則立即取空，顯示供需平衡生效。  
作者指出此實作可再優化，例如用環狀佇列取代 Queue 以降低記憶體移動，或加入 Priority 機制改變出隊順序；更可延伸為 Pipeline 或 Stream。文末預告將於後續深入探討。  

## 段落重點
### 引言：從工具到模式
作者回顧自己先前的執行緒文章僅談「精確控制」技巧，但真正能提高效能的關鍵在於如何將程式架構分段並導入正確模式；生產者/消費者正是典型例子，熟讀作業系統的讀者應不陌生。

### 實務情境：下載與壓縮
以「同時下載數百檔並立即壓縮成 ZIP」為例：下載屬 IO bound、壓縮屬 CPU bound，兩段不搶資源卻需共用檔案暫存。若無緩衝控管，一端快、一端慢便造成磁碟爆滿或閒置。

### 架構構想：用 Queue 管庫存
比較 Semaphore 與 Queue 後，作者選擇以 Queue 做核心，因為佇列自然符合「先進先出」的緩衝需求，只需補上容量偵測與阻塞行為即可滿足模式需求。

### BlockQueue 設計目標
1) 可設定固定大小；2) 佇列滿/空時不要拋例外而應阻塞執行緒；3) 提供 Shutdown 讓所有等待執行緒安全結束。此三點使 BlockQueue 能被重複利用，如同泛型集合一樣容易上手。

### 範例程式：生產者與消費者
主程式建立 5 個 Producer、10 個 Consumer，共用一個容量 10 的 BlockQueue。Producer 產生 30 筆資料後結束；全部 Producer 結束時呼叫 queue.Shutdown() 通知停機；Consumer 在捕捉到例外後離開。

### 測試與結果觀察
1) 當 Producer 多於 Consumer 時，佇列長度穩定維持在接近 10，證明滿佇列會阻塞；  
2) 當 Consumer 多時，資料一入佇列即被搶空，顯示空佇列阻塞解除後立刻消費，達成供需協調。

### BlockQueue 核心程式碼
內部維護 Queue<T>、兩個 ManualResetEvent 及一個 Shutdown 旗標。EnQueue 在滿佇列時 WaitOne，DeQueue 在空佇列時 WaitOne；事件的 Set/Reset 由對方操作完成後觸發，使兩端互相喚醒。Shutdown 將旗標設 True 並 Set 可讀事件，讓等待中的消費者取完剩餘資料後離開。

### 可改進方向與結語
若將內部佇列改成 CircularQueue 可避免元素搬移；加入 PriorityQueue 可支援插隊；更可組成多段 Pipeline 甚至 Stream 化處理。作者預告將在後續文章深入探討，鼓勵讀者自行嘗試並思考更多變形。