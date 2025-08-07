```markdown
# 架構面試題 #2 ─ 連續資料的統計方式

# 問題／解決方案 (Problem/Solution)

## Problem: 在高併發電商網站中，每秒更新「過去一小時成交總額」  
**Problem**:  
• 網站每秒湧入數千~數萬筆訂單（>10 k orders/sec）。  
• 前端儀表板必須「每秒」顯示過去 1 hr 的成交金額。  
• 資料連續流入，系統沒有重算或停機時間；舊資料要能準時被剔除。  

**Root Cause**:  
1. 時間窗必須「移動」，每秒都要把剛進來的資料加入、把 1 hr 前的資料扣掉。  
2. 若使用傳統關聯式 DB，`sum()` 會不停掃描 3 600 萬(+) 筆資料；資料再累積到上億筆時 I/O 與 CPU 完全撐不住。  
3. 隨 Data Size 增長，查詢延遲線性上升，甚至影響交易寫入。  

### Solution 1 – 直接以資料庫 `SELECT SUM()` 計算  
**Solution**:  
```sql
SELECT SUM(amount)
FROM   Orders
WHERE  transaction_time BETWEEN DATEADD(hour,-1,GETDATE()) AND GETDATE();
```  
• 不需修改現有程式，只要下 SQL 即可回傳結果。  

**關鍵思考**:  
• 依賴資料庫引擎做全表掃描，未真正解決 Root Cause ②③ 的數量級問題。  

**Cases 1** – 單機 SQL Server 2017  
• 測試流量：10 k orders/sec  
• 未暖機前偶有誤差；暖機後能給出正確值，但效能僅 17 orders/ms (~1.7 × 10⁴ orders/sec)。  
• 表格持續增長，需另行做歸檔或分區才能勉強維運。  

---

## Problem: SQL 全表掃描效能不足，需要更輕量的即時統計機制  
**Problem**:  
現場驗證顯示 SQL 版無法負荷 >1.7 × 10⁴ ops/sec，延遲不可接受。  

**Root Cause**:  
• 重複掃描、重複加總，時間複雜度 O(N)。  
• 隨時間窗變大，計算量 ×60、×3600 地成長。  

**Solution – In-Memory Ring Buffer / Queue**  
1. 以「秒」為最小單位，先把 1 hr 3 600 萬筆訂單，預先收斂成 3 600 個「每秒統計」。  
2. 使用 Queue (FIFO) 維持 3 600 個 bucket；背景 Worker 每 0.1 sec 做：  
   • `buffer` ← 最新 0.1 sec 金額 (Interlocked.Add)  
   • 將 `buffer` 入佇列並累加 `statistic`  
   • 若 queue.head 已過期 (>60 sec) 就 Dequeue 並從 `statistic` 扣除  
3. 任何時刻 `Result = statistic + buffer`，時間複雜度 O(1)。  

```csharp
public override int StatisticResult => _statistic + _buffer;
public override int CreateOrders(int amt) => Interlocked.Add(ref _buffer, amt);
```  

**關鍵思考**:  
• 時間、空間皆 O(1)。  
• 利用 `Interlocked.Add / Exchange` 保證 atomic, 避免 race condition。  

**Cases 1** – 單機測試  
• Intel i7-4785T / 16 GB RAM  
• 吞吐：3.48 × 10⁶ orders/sec (3 480 orders/ms)  
• 正確率 100 %（與參考實作比對）。  
• 缺點：單機單點，無法 scale-out、無備援。  

---

## Problem: 單機 In-Memory 無法橫向擴充 & 缺乏高可用  
**Problem**:  
• 需要多台 Web/API 節點同時即時計算；單機 state 放在 RAM 不易共享，掛機就遺失。  

**Root Cause**:  
• `buffer / queue / statistic` 皆存在 process memory 中，缺乏集中狀態管理。  

**Solution – Redis 分散式狀態 + Atomic Operations**  
1. 將 `buffer`、`statistic` 存成 Redis String；`queue` 存成 Redis List。  
2. 利用內建 atomic 指令：  
   • `INCRBY`, `DECRBY` → 加減 `statistic`  
   • `GETSET buffer 0`     → 取值並歸零（取代 Exchange）  
   • `LPUSH/RPUSH`, `LPOP` → 維持 FIFO queue  
3. 只有「一個」背景 Worker 負責移窗，N 個 API 節點都可 `INCRBY buffer`。  
4. 支援 Redis Cluster 可進一步做 HA & Partition。  

```csharp
redis.StringIncrement("buffer", amount);              // 進單
int buf = (int)redis.StringGetSet("buffer", 0);       // Worker 取值歸零
redis.ListRightPush("queue", Encode(buf, now));
redis.StringIncrement("statistic", buf);              // 累計
```  

**關鍵思考**:  
• 所有狀態搬上 Redis，instance 數量可水平擴充。  
• Redis 指令天生 atomic，避免分布式鎖劣化。  

**Cases 1** – 10 個 TestConsole 並行  
• 正確率：0 % 誤差（與單機版比）。  
• 吞吐：8.2 × 10⁴ orders/sec（82 orders/ms），為 SQL 方案 6.8 × 速度。  
• 可透過 Redis Sentinel / Cluster 取得高可用。  

---

## Problem: 當統計種類更多、規模再放大，維運自管叢集成本過高  
**Problem**:  
• 企業級場景需要處理多種事件串流、複雜 Join、Session Window 等。  
• 自建 / 自維 Redis + Worker 需人力，擴充或容災流程複雜。  

**Root Cause**:  
• 裝置與維運層的隱含成本高；缺乏彈性擴充與即時查詢語言層支援。  

**Solution – 使用雲端串流分析服務 (Azure Stream Analytics)**  
1. 將事件匯入 Event Hub / IoT Hub → ASA Job。  
2. 以 SQL-like 語法撰寫 Window Aggregate：  
```sql
SELECT
    SUM(CAST(Amount AS BIGINT)) AS TotalAmt
INTO   Output
FROM   Orders TIMESTAMP BY TransTime
GROUP BY TumblingWindow(second, 3600);
```  
3. 平台自動分片、彈性擴充、內建 Checkpoint / 容錯。  
4. 分析結果可直接落地至 Cosmos DB、SQL、Power BI。  

**關鍵思考**:  
• 將維運、彈性、HA 全交由雲端服務；工程團隊專注商業邏輯。  
• SQL Window Function 天生支援滑動窗、跳動窗、Session 窗等模式。  

**Cases 1** (概念)  
• 多間大型零售客戶使用 ASA 將訂單即時匯總，減少 90 % 開發與維運工時。  
• 平台自動擴充至數十萬 events/sec 時仍維持 < 1 sec 延遲。  
```
