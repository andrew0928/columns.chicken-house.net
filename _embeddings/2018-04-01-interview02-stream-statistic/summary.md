# 架構面試題 #2, 連續資料的統計方式

## 摘要提示
- 滑動時間窗: 需求是在高頻交易環境下，每秒更新「過去一小時成交金額」，考驗 time-window 統計設計。
- SQL 直算: 直接對 orders table 做 `SUM()` 是最直覺也最慢的基線解，僅適合小流量。
- In-Memory Queue: 以 Queue＋兩個暫存變數（buffer / statistic）與週期性 worker 實現 O(1) 時間、空間複雜度。
- Atomic 操作: 正確性仰賴 `Interlocked`、`INCRBY`、`GETSET` 等原子指令避免 racing condition。
- Redis 分散式: 把 Queue 與計數器搬上 Redis，可多節點寫入、單 worker 彙總，支援水平擴充。
- Stream Analytics: 企業級可直接採 Azure Stream Analytics 等服務，用 SQL-like 語法完成滑窗聚合。
- 效能對比: In-Memory 3.4M OPS/s ＞ Redis 82K OPS/s ＞ DB 17K OPS/s，差異達兩百倍以上。
- 面試鑑別: 題目能快速分出只會寫 SQL 的 junior 與能設計可擴張解的 architect。
- 資料結構價值: 當需求超出現成框架時，懂基本 DS/Algo 的工程師才能土炮出高效方案。
- 技術選型: 能說明各解法適用場景與限制者，才具備架構師應有的判斷力。

## 全文重點
本文以「每秒更新過去一小時成交總額」為情境，說明連續資料統計的多種解法並用 C# 範例與測試程式驗證。首先，題目要求系統在大量訂單湧入時仍可即時計算且不重複掃描巨量資料。大多數面試者只會提出 `SELECT SUM()` 之類 SQL 直算方案，雖簡單但在數千萬筆資料下無法及時回應，也難以長期執行。

作者進而示範以資料結構思維設計的 In-Memory 解法：用 Queue 保存 60 秒內的秒級聚合，配合 worker 週期性將 buffer 歸零並更新統計值，刪除逾期資料。此方法新增訂單、取得統計與內部維護皆為 O(1)，資源佔用固定，足以支撐每秒百萬筆流量。為確保多執行緒正確性，須以 `Interlocked` 實作加總與交換，或在分散式情境下利用 Redis 的 `INCRBY / DECRBY / GETSET` 搭配 Lists 指令完成原子排隊與計數。Redis 版本可讓多個 API 併發寫入，由單一 worker 滑窗維護，具可水平擴充與高可用性。

若組織已有大規模即時分析需求，可直接採用 Azure Stream Analytics 這類雲端服務，用 SQL-like 查詢撰寫 `TUMBLINGWINDOW` 等語句即可完成滑窗聚合，省去自行維護分散式鎖與儲存的成本。文末作者做效能大亂鬥，結果顯示 In-Memory 解法 3.4M orders/sec、Redis 82K、SQL 17K，性能差距數百倍。透過此題可快速鑑別 engineer 的資料結構基礎、平行處理觀念與系統設計深度，也再次強調「基礎知識＋正確技術選型」對可擴張架構的重要性。

## 段落重點
### 前言 & 導讀
作者說明選題目的用意：在高流量電商網站中即時計算滑動時間窗統計，是檢驗演算法運用與系統可擴張能力的典型問題。85% 面試者僅能用 SQL 重算，無法處理百萬級流量，展示演算法思維的重要性。

### 考題 & 測試程式
提供 Contracts、TestConsole 及 DummyEngine 範本。測試程式每秒產生一筆金額＝秒數的訂單，同時每 200ms 讀統計值，預期暖機後結果固定為 1770。實作者需完成 Engine 讓測試穩定通過並兼顧性能。

### 解法1 直接資料庫計算
Junior 常見方案：對 orders table 下 `SUM()` 查詢。雖結果正確，但資料量成長會拖垮效能；時間窗越大、未封存資料越多，查詢成本線性攀升。即使加 cache、分表、讀寫分離，仍屬治標，無法長期支撐高頻流量。

### 解法2 程式內統計（In-Memory）
以 Queue 儲存 60 秒秒級聚合，buffer 暫存當前秒資料，worker 週期性將 buffer 入隊並移除過期項；statistic 變數維護總和。新增訂單、讀統計皆 O(1)，空間固定，支援高流量且資源極低。透過 `Interlocked.Add/Exchange` 保證多執行緒安全。

### 解法3 分散式統計（Redis）
將 Queue、buffer、statistic 搬上 Redis，利用 Lists、`INCRBY/DECRBY/GETSET` 等原子指令維持一致性，多節點可併發寫入，由單 worker 處理滑窗。效能優於 DB 且可擴充；需注意 worker 只需一份及 HA 架構配置。

### 加分題：Atomic Operations
透過雙版本自我驗證法比較有無 lock 的 In-Memory 與 DB、Redis 版結果。無 lock 版本在高併發下誤差近 4%；有 lock 或 Redis 版則與基準完全一致。示範原子操作對資料正確性的關鍵。

### 加分題：使用串流分析
介紹 Azure Stream Analytics 架構，可用 `TUMBLINGWINDOW` 等 SQL-like 語法做滑窗聚合，並將結果寫入儲存或 BI。若公司已進入雲端且需求多，可省去自行維運分散式統計的複雜度。

### 總結
效能測試顯示 In-Memory 3.4M OPS/s、Redis 82K、DB 17K，差距數百倍。選對資料結構與架構可大幅提升吞吐並降低資源。面試官透過此題能分辨具備演算法、併發控制與系統設計能力的人才；工程師亦應扎實基礎，才能在無現成框架時自造高效解。