# 架構面試題 #2 ─ 連續資料的統計方式

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這個面試題要解決的核心需求是什麼？
在高流量購物網站中，以「每秒更新」的方式即時顯示「過去一小時的總成交金額」，且系統必須長時間不中斷地運行。

## Q: 此需求最麻煩的兩個技術難點是哪些？
1. 必須同時累加新資料並精準剔除超過時間窗（一小時）的舊資料。  
2. 資料源源不絕地湧入，沒有任何停機整理的空檔，處理流程不能造成大量暫存或瞬間吃光資源。

## Q: 直接在資料庫執行 `SELECT SUM(...)` 的作法有什麼問題？
隨著訂單量、時間窗及歷史資料筆數增大，查詢必須重算大量 row data，I/O 與 CPU 耗用快速上升，無法在高併發、大時間窗、長時間執行下維持性能；因此只適合小規模、屬於 junior-level 的解法。

## Q: 程式內(In-Memory)統計的核心概念是什麼？
把「一小時」切成 3600 個「每秒」桶(slot)，用 Queue(FIFO) 只保存這 3600 筆彙總資料，並維護一個 running total：  
‧ 新訂單先累加到 `buffer`  
‧ 週期性 worker 把 `buffer` 值入隊、加到 running total，再把過期值出隊並扣除  
‧ 讀取時回傳 `running total + buffer`  
所有操作時間複雜度 O(1)，記憶體亦固定，效能極佳。

## Q: In-Memory 解法的詳細步驟為何？
1. 用 `buffer` 累加同一個 interval(例 0.1 秒) 內的訂單金額。  
2. 週期性 worker  
   2-1. `buffer` 透過 atomic 交換設為 0 並取得舊值  
   2-2. 舊值入隊(Queue)並加到 `statistic_result`  
   2-3. 將 Queue 中超過 60 秒的項目出隊並從 `statistic_result` 扣除  
3. 任何時刻的統計值為 `statistic_result + buffer`。

## Q: 為什麼必須使用 Atomic Operations？在 .NET 可以怎麼做？
多執行緒或多機同時寫入時，若 `buffer`、`statistic_result` 等共享變數在讀改寫過程被打斷，會造成資料遺失或重算。  
在 .NET 可使用 `System.Threading.Interlocked` 之 `Add`、`Exchange` 等方法保證單一步驟不可分割。

## Q: 分散式統計(以 Redis 為例)的設計重點是什麼？
把 `buffer`、`queue`、`statistic_result` 等狀態搬到 Redis：  
‧ 使用 Lists + `LPUSH/RPUSH/LPOP` 實作 Queue  
‧ 使用 `INCRBY`、`DECRBY`、`GETSET` 實作累加、扣除與交換，都具備 atomic 特性  
‧ 只需一個 worker 處理過期資料，其餘 Instance 專心寫入，便可水平擴充並具備高可用特性。

## Q: 三種方案的適用職級、場景與效能測試結果為何？
1. 資料庫直接統計  
   ‑ Junior 級 ‑ 小流量/簡易場景 ‑ 約 17K orders/sec  
2. In-Memory 統計  
   ‑ Senior/Architect 級 ‑ 單機但高效能 ‑ 約 3.48M orders/sec  
3. Redis 分散式統計  
   ‑ Architect 級 ‑ 多機、高可用 ‑ 約 82K orders/sec (可再透過擴充提升)

## Q: 若系統規模更大，為何可以考慮使用 Azure Stream Analytics？
Azure Stream Analytics 提供托管式串流分析服務，可對持續進入的資料以 SQL-LIKE 語法撰寫窗口函式 (例如 `TumblingWindow`) 即時統計，並將結果輸出到多種儲存或訊息系統，不用自行維運基礎設施；在需要處理多條資料流或更複雜聚合時是理想選擇。

## Q: 面試官透過這題主要想評估候選人的哪些能力？
1. 是否能辨識不同規模下的瓶頸並選擇合適解法  
2. 資料結構與演算法應用的深度  
3. 對多執行緒、分散式環境中資料一致性的理解  
4. 架構選型與效能、成本、可維運性的綜合考量