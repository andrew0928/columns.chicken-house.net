---
layout: synthesis
title: "架構面試題 #2, 連續資料的統計方式"
synthesis_type: summary
source_post: /2018/04/01/interview02-stream-statistic/
redirect_from:
  - /2018/04/01/interview02-stream-statistic/summary/
postid: 2018-04-01-interview02-stream-statistic
---

# 架構面試題 #2, 連續資料的統計方式

## 摘要提示
- 滾動時間窗: 需即時計算「過去一小時」累計金額並每秒更新，重點在準確剔除過期資料。
- 連續資料流: 設計需可持續運作、不中斷，避免重算與資源暴衝。
- 資料庫直算限制: 以 SQL sum + time filter 的解法正確但不可擴展，成本與效能受限。
- 資料結構解法: 以 Queue + buffer + 累計變數，將每秒聚合，O(1) 時間與空間複雜度。
- 原子操作: 使用 Interlocked/Redis INCR/DECR/GETSET 確保多執行緒/分散式下數據正確。
- 分散式方案: 將 queue 與統計狀態搬至 Redis，支援多實例寫入、單 worker 滾動窗口。
- 驗證方法: 以雙版本互驗與高併發壓測，檢出 race condition 與量化誤差。
- 效能對比: InMemory > Redis > Database，效能差距數十到數百倍。
- 串流分析: 以 Azure Stream Analytics 等服務用窗口函式（TumblingWindow）做即時聚合。
- 面試鑑別: 此題可區辨演算法/資料結構/併發與架構能力，適合評估架構師潛力。

## 全文重點
本文以「每秒產生大量訂單，需即時計算過去一小時成交總額並每秒更新」為面試情境，說明連續資料的統計設計。問題核心在「滾動時間窗」與「永續處理」：既要持續攝入新資料、低延遲給出結果，也要精準剔除已過窗的舊資料，且不能依賴暴力重算與無限制堆疊歷史數據。

作者先點出台灣面試常見回答：以資料庫對 orders 直接 sum(amount) 並用時間條件過濾。此法雖然結果正確，但在高流量（數千萬筆/小時）下，查詢成本、索引掃描與 I/O 會迅速失控；時間窗加大亦倍增算量；歷史累積使 where 範圍查找成本持續升高。即便施加快取、封存或讀寫分離，本質仍是重複重算、不可長期擴展的解法。

更優做法來自資料結構與演算法：將「秒級精度」作為前處理，將 3600 萬筆/小時的原始資料先聚合為 3600 筆每秒總額。以 Queue 維護固定長度的滑動窗口；以 buffer 暫存當前 interval 的累積；以 statistic_result 維護窗口內總和。每個 interval（例 0.1 秒）由 worker 執行：將 buffer 以 GETSET/Exchange 歸零並入隊、累加到 statistic、剔除超窗項並減回 statistic。讀取結果時回傳 statistic + buffer。此法在新增、讀取與滾動上皆為 O(1)；空間也為 O(1)（與 period/interval 成常數比）。正確性需以 atomic operations 確保，.NET 用 Interlocked，避免 race condition 吃掉數據。

為支援多實例與高可用的分散式場景，把 queue 與兩個累積變數搬到 Redis，藉 Lists、INCRBY/DECRBY、GETSET 取得原子语义，多個 writer 可並行寫入，僅需單 worker 負責滾動窗口維護。作者亦示範多進程壓測，統計能線性疊加，驗證設計可擴展。

驗證方面，作者採用「兩版本互驗」：以慢但正確的版本為對照，與最佳化版本同時吃相同流量，計算期末統計是否一致，並以多執行緒高併發測出未加鎖寫法約 3.97% 錯漏。效能對比顯示：InMemoryEngine 約 340 萬 ops/s，Redis 約 8.2 萬 ops/s，Database 約 1.7 萬 ops/s。InMemory 極快但單機、無備援；Redis 兼顧擴展性與可用性；資料庫直算最不理想。

最後，文章將此題延展至雲端串流分析服務，如 Azure Stream Analytics，以類 SQL 語法和窗口函式（TumblingWindow）在資料流上即時計算總和。作者建議面試時以此題辨別工程師是否具備資料結構、併發控制與系統選型能力：能否在不同規模下選對方法，才是走向微服務與可擴展架構的關鍵。

## 段落重點
### 前言 & 導讀
作者定義系統背景：既有 WebAPI、Processing、DB 流程不變；新增 Statistic 模組需在訂單建立事件到來時即時統計過去一小時金額且每秒更新。難點一是時間窗的精準剔除，難點二是連續資料的不中斷持續處理與資源穩定。此題可有效區辨只會直覺用 SQL 的一般解法與能運用資料結構/演算法的工程師，適合用來面試鑑別具架構思維的人才。

### 考題 & 測試程式
提供 Contracts 與測試程式：EngineBase 暴露 CreateOrders 與 StatisticResult；測試每秒生成一筆訂單，金額為秒數，理論上過一分鐘後，任一時刻的窗內總和為 0..59 之和 1770。測試每 200ms 列印統計與預期值，由於邊界時間誤差以人工判定。此測試模式用於驗證解法是否能在連續流與滾動窗口下正確、穩定更新。

### 解法1, 直接使用資料庫的原始資料來計算
以 SQL sum + time filter 自 orders 表直接重算。優點是實作簡單、結果正確；缺點是不可擴展：每秒量不確定、窗口放大成倍增加算量、歷史累積拖慢篩選。即使加快取、封存、讀寫分離，本質仍是重複掃描原始資料且成本高昂。適用小規模/短期；在高流量長時間運行下會崩潰。作者把此歸為 junior 級解法，提醒應避免把昂貴的資料庫當即時計算引擎。

### 解法2, 在程式內直接統計
核心是滑動窗口的資料結構設計：以秒為精度做前處理，將海量原始資料彙總成每秒統計；用 Queue 維護固定長度窗口、用 buffer 累積當前 interval、用 statistic_result 持有窗口總和；worker 週期性歸零 buffer 入隊並剔除過期元素，讀取時回傳 statistic + buffer。以 Interlocked 確保原子性，避免 race condition。此法新增、讀取、滾動皆 O(1)，空間 O(1)，資源極低且長時間穩定，屬 senior/architect 可達之解答。

### 解法3, 分散式的統計
將 Queue 與累積變數搬上 Redis，以 Lists 實作隊列，以 INCRBY/DECRBY/GETSET 完成原子加減與交換，確保分散式原子性。多實例可並行寫入，由單一 worker 維護窗口剔除與累加，避免競態。作者以多進程壓測顯示統計線性擴展。此法兼顧可擴展與可用度，難度較高，需要同時掌握資料結構與系統架構，是 architect 等級解法。

### 加分題: atomic operations
強調多執行緒/分散式場景下的原子操作重要性。以兩版本互驗法（慢而正確 vs 快而最佳化）在執行期自我驗證；多執行緒壓測顯示未加鎖寫法誤差約 3.97%。比較 InMemory vs InDatabase 一致性與效能差距，證明正確性需靠原子性與正確鎖控，效能則取決於是否避免重算和重 I/O。

### 加分題, 使用串流分析
介紹 Azure Stream Analytics 的管線：前端收集、即時分析、結果入庫，使用 SQL 類語法與窗口（如 TumblingWindow）在流上即時計算 SUM。此法適合成熟規模與雲端環境。作者視其為技術選型加分題：需先理解資料結構與併發，再談托管服務的適用時機、優缺點與成本。

### 總結
以 10 秒壓測比較三方案：InMemory 約 340 萬 ops/s，Redis 約 8.2 萬，Database 約 1.7 萬。InMemory 極致效能但單機不可擴；Redis 兼顧可擴展與高可用，仍有優化空間；Database 方案效率最差且昂貴。作者最後強調：此題能有效鑑別工程師在資料結構、併發控制與架構選型上的能力，對打造可擴展微服務團隊尤其關鍵。

## 資訊整理

### 知識架構圖
1. 前置知識
   - 時間視窗統計概念：Tumbling/Sliding window、時間戳與誤差
   - 資料結構與演算法：Queue/FIFO、時間與空間複雜度、O(1) 更新
   - 併發控制：race condition、lock 與 lock-free、atomic operations
   - 儲存系統基礎：關聯式資料庫索引/聚合、快取/記憶體儲存（Redis）
   - 測試與效能：壓測、對照驗證（雙版本比對）、計時與吞吐量

2. 核心概念（3-5 個）
   - 滑動時間視窗聚合：只維持視窗內數據，持續加入新值、剔除過期值
   - 資料化簡與分桶（bucketing）：高頻原始事件先彙總成秒級/子秒級桶，再在視窗內 O(1) 更新
   - O(1) 狀態維護：使用 Queue + buffer + statistic_result，定期 worker 轉移與過期淘汰
   - 原子操作確保正確性：用 Interlocked（程式內）或 Redis 原子指令（分散式）避免競態
   - 架構選型與擴展：單機記憶體版、Redis 分散式版、雲端 Stream Analytics 的取捨

3. 技術依賴
   - 解法1（DB 聚合）：SQL SUM + time 索引；受限於筆數、視窗長度與重複計算
   - 解法2（程式內）：Queue、背景 worker、Interlocked.Add/Exchange；固定小狀態、O(1) 更新
   - 解法3（分散式）：Redis Strings（INCRBY/DECRBY/GETSET）、Lists（RPUSH/LPOP）實作 Queue；必要時分散式鎖
   - 托管串流分析：Azure Stream Analytics（Event Hub/Queue 作輸入、SQL-like 視窗函式、輸出到儲存/DB）

4. 應用場景
   - 即時訂單/營收儀表板、點擊/UV/PV 監控
   - 物聯網感測資料的移動平均/最大值/異常偵測
   - 速率限制（rate limiting）、告警觸發、SLA/延遲監控
   - 多服務實例彙總的跨節點即時統計

### 學習路徑建議
1. 入門者路徑
   - 釐清 Tumbling vs Sliding window 與時間戳處理
   - 用 SQL 做最簡單的「近一小時 SUM」原型，觀察隨筆數增長的效能瓶頸
   - 動手寫單機 InMemory 版本：Queue + buffer + statistic_result + worker，完成 O(1) 視窗維護

2. 進階者路徑
   - 深入併發安全：Interlocked、lock-free 思維、競態案例與修復
   - 增加時間精度/桶大小控制（interval/period），評估準確度與資源折衷
   - 建立壓測與雙版本對照驗證（慢版 vs 快版）以確保正確性

3. 實戰路徑
   - 上 Redis 實作分散式狀態：鍵設計、Lists 作 Queue、INCRBY/GETSET/DECRBY 原子序列
   - 佈署與監控：容器化、HA、度量（吞吐、延遲、偏差率）、時鐘偏差處理
   - 導入雲端 Stream Analytics 評估成本/維運，選擇自管（Redis）或托管（ASA）的方案

### 關鍵要點清單
- 滑動時間視窗統計: 只維持視窗內資料並即時更新加總/剔除過期值 (優先級: 高)
- 分桶/化簡（bucketing）: 以秒/子秒為桶先局部彙總，大幅降低計算量 (優先級: 高)
- O(1) 視窗維護: Queue + buffer + statistic_result + worker 週期處理 (優先級: 高)
- 併發與原子性: 使用 Interlocked 或等效原子操作避免競態 (優先級: 高)
- Redis 原子指令: INCRBY/DECRBY/GETSET 提供分散式原子更新 (優先級: 高)
- Redis Lists 當 Queue: RPUSH/LPOP 實作 FIFO 保存每桶與時間戳 (優先級: 中)
- 視窗參數設計: period（視窗長度）與 interval（精度）影響準確度與資源 (優先級: 中)
- 時間戳與誤差: 邊界事件、延遲/時鐘偏差造成統計抖動的處理 (優先級: 中)
- SQL 直算的限制: 重複加總、筆數與視窗放大導致效能崩潰 (優先級: 中)
- 複雜度分析: 單機 O(1) 時間/空間（對桶數固定），可長時穩定運行 (優先級: 中)
- 驗證方法: 雙版本比對（正確但慢 vs 最佳化版）檢出錯誤與偏差率 (優先級: 高)
- 效能比較洞見: InMemory ≫ Redis ≫ DB，對應可用性/擴展性差異 (優先級: 中)
- 分散式注意事項: 單一 worker、狀態集中於 Redis、必要時分散式鎖 (優先級: 中)
- 監控與容量規劃: 吞吐、延遲、記憶體/鍵數、過期清理策略 (優先級: 中)
- 托管串流分析: Azure Stream Analytics 以 SQL-like 視窗函式快速落地 (優先級: 低)