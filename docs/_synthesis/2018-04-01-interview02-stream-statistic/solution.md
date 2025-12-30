---
layout: synthesis
title: "架構面試題 #2, 連續資料的統計方式"
synthesis_type: solution
source_post: /2018/04/01/interview02-stream-statistic/
redirect_from:
  - /2018/04/01/interview02-stream-statistic/solution/
---

以下內容基於提供的文章，抽取並結構化 15 個具完整教學價值的問題解決案例。每個案例均包含問題、根因、解法（含關鍵程式碼/設定）、實測數據與練習/評估，便於用於實戰教學、專案練習與能力評估。

```markdown
## Case #1: 直接用資料庫 SUM 的滑動時間窗統計（基線做法）

### Problem Statement（問題陳述）
**業務場景**：電商網站每秒產生大量訂單，管理層希望即時查看「過去 60 秒/60 分鐘的成交金額」，並每秒更新。系統已有 WebAPI、Processing、DB 管線，要求在不打擾既有流程的前提下，於 Statistic 模組提供滑動視窗加總結果。
**技術挑戰**：在每秒大量新資料持續寫入時，用 SQL 每秒重新計算過去一段時間的 SUM，會因資料量成長、時間窗放大而導致效能崩潰。
**影響範圍**：DB CPU/IO 飆高、庫表鎖爭用、查詢延遲升高，導致即時指標延遲、其他交易受拖累。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 重複全量掃描：每秒對時間窗內資料做 SUM，運算量隨時間窗長度與資料成長線性上升。
2. 資料無封存：orders 表歷史資料持續累積，WHERE 篩選成本上升。
3. 無降階統計：未做預聚合或增量維護，造成重複計算。
**深層原因**：
- 架構層面：將即時計算耦合在交易 DB 上，缺乏分析/查詢與交易分離。
- 技術層面：僅依賴 SQL 聚合，缺少緩存、增量與時間窗資料結構。
- 流程層面：無資料生命週期管理（歸檔/分區），缺少效能基準與壓測流程。

### Solution Design（解決方案設計）
**解決策略**：在現有 DB 上快速落地，於時間欄位建索引，透過單條 SQL 以 BETWEEN 篩選 [now-60s, now]，立即產出統計。用此作為基線/對照組，為後續優化提供實測標杆。

**實施步驟**：
1. 建表與索引
- 實作細節：建立 orders(time, amount) 並對 time 建索引。
- 所需資源：SQL Server/MSSQL LocalDB
- 預估時間：0.5 天

2. 實作 InDatabaseEngine
- 實作細節：CreateOrders 插入資料；StatisticResult 執行 SUM(amount) WHERE time BETWEEN now-60s AND now。
- 所需資源：.NET 6+/Dapper
- 預估時間：0.5 天

3. 功能與負載驗證
- 實作細節：用測試程式每秒灌單、每 200ms 取統計，觀察數值穩定性與吞吐。
- 所需資源：測試主控台
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- Schema
CREATE TABLE [dbo].[orders]
(
  [Id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY DEFAULT newid(), 
  [time] DATETIME NOT NULL DEFAULT getdate(), 
  [amount] MONEY NOT NULL
);
GO
CREATE INDEX [IX_orders_Column] ON [dbo].[orders] ([time]);

-- 查詢滑動窗
SELECT SUM(amount) 
FROM [orders]
WHERE time BETWEEN DATEADD(second, -60, GETDATE()) AND GETDATE();
```

```csharp
public class InDatabaseEngine : EngineBase
{
    public override int StatisticResult =>
        this.GetSqlConn().ExecuteScalar<int>(
            @"select sum(amount) from [orders]
              where time between dateadd(second, -60, getdate()) and getdate();");

    public override int CreateOrders(int amount)
    {
        this.GetSqlConn().ExecuteScalar(
            @"insert [orders] (amount) values (@amount);", new { amount });
        return amount;
    }
    private SqlConnection GetSqlConn() => new SqlConnection("...LocalDB...");
}
```

實際案例：以每秒產單、每 200ms 查詢的測試程序，觀察數值在 1770 左右波動（時間邊界抖動所致）。
實作環境：Windows 10 Pro x64、.NET、SQL Server 2017 Dev、Intel i7-4785T/16GB/SSD
實測數據：
- 改善前：N/A（作為基線）
- 改善後：吞吐 17.0458 orders/msec（10 秒壓測）
- 改善幅度：N/A（作為基線，供後續對比）

Learning Points（學習要點）
核心知識點：
- 交易庫直接聚合的侷限與風險
- 時間欄位索引對 BETWEEN 查詢的作用
- 即時統計與 OLTP/OLAP 責任分離

技能要求：
- 必備技能：SQL/索引、.NET DB 連線與基本壓測
- 進階技能：查詢分析、分區/歸檔策略

延伸思考：
- 什麼時候應轉向增量/預聚合？
- 如何避免統計查詢影響交易？
- 可否用只寫入、只追加的事件流做來源？

Practice Exercise（練習題）
- 基礎練習（30 分鐘）：建立表與索引，插入 1 萬筆資料，執行時間窗 SUM。
- 進階練習（2 小時）：模擬每秒入單 1k，觀察查詢延遲與 CPU 使用率。
- 專案練習（8 小時）：實作簡單讀寫分離，量測對交易/查詢延遲的影響。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確回傳時間窗加總
- 程式碼品質（30%）：SQL 可讀性、參數化、安全
- 效能優化（20%）：建立索引、查詢計畫合理
- 創新性（10%）：提出可持續的資料生命週期治理方案
```

```markdown
## Case #2: 以 Queue + Buffer 的 In-Memory 滑動視窗（O(1) 解法）

### Problem Statement（問題陳述）
**業務場景**：需在單機服務中即時給出「最後 60 秒」加總，並承受極高 TPS（單機每秒百萬級事件），同時嚴格控制資源占用。
**技術挑戰**：要同時滿足高吞吐、低延遲、低資源與正確移除窗口外舊資料；傳統 SQL/掃描式方法無法滿足。
**影響範圍**：統計延遲或錯誤將直接影響營運決策與下游報表。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 重複掃描：每次查詢都掃描窗口資料，時間複雜度高。
2. 視窗剔除困難：準確移除超時資料難以做到 O(1)。
3. 記憶體與 GC 壓力：若用細粒度明細緩存，會造成高 GC。
**深層原因**：
- 架構層面：缺乏在應用層的預聚合/增量維護。
- 技術層面：未正確選擇資料結構（Queue/FIFO）。
- 流程層面：未設置性能基準與 O(1) 設計目標。

### Solution Design（解決方案設計）
**解決策略**：採用時間分桶（bucket）+ FIFO Queue 保存每個 interval 的聚合值，另以 buffer 累加當前間隔的數值，由背景 worker 週期性把 buffer 交換入隊、更新總和、並逐出過期桶；查詢時回傳 statistic + buffer，達成 O(1) 查詢與更新。

**實施步驟**：
1. 設計 bucket 與 Queue 結構
- 實作細節：每 interval 產生一個 bucket（_interval=0.1s ⇒ 600/分鐘），Queue 保存每個 bucket 的總額與時間。
- 所需資源：.NET/C#
- 預估時間：0.5 天

2. 背景 worker 與原子交換
- 實作細節：定時 Interlocked.Exchange(buffer,0) 取值入隊，累加 statistic，並 while 逐出 time < now-period 的桶。
- 所需資源：.NET Threading
- 預估時間：0.5 天

3. 讀寫 API
- 實作細節：CreateOrders 使用 Interlocked.Add；StatisticResult 回傳 statistic + buffer。
- 所需資源：.NET
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public class InMemoryEngine : EngineBase
{
    private readonly TimeSpan _period = TimeSpan.FromMinutes(1);
    private readonly TimeSpan _interval = TimeSpan.FromSeconds(0.1);
    private readonly Queue<QueueItem> _queue = new();
    private int _statistic_result = 0;
    private int _buffer = 0;

    public InMemoryEngine()
    {
        Task.Run(() => {
            while (true) { Task.Delay(_interval).Wait(); _worker(); }
        });
    }

    public override int StatisticResult => _statistic_result + _buffer;
    public override int CreateOrders(int amount) => Interlocked.Add(ref _buffer, amount);

    private void _worker()
    {
        int buf = Interlocked.Exchange(ref _buffer, 0);
        _queue.Enqueue(new QueueItem { _count = buf, _time = DateTime.Now });
        _statistic_result += buf;

        while (true)
        {
            if (_queue.Peek()._time >= DateTime.Now - _period) break;
            var dq = _queue.Dequeue();
            _statistic_result -= dq._count;
        }
    }
    private class QueueItem { public int _count; public DateTime _time; }
}
```

實際案例：以每秒用 Now.Second 當 amount 的資料流，暖機後數值穩定在 1770（0+...+59），偶見邊界抖動。
實作環境：Windows 10、.NET、i7/16GB
實測數據：
- 改善前（DB 方案）：17.0458 orders/msec
- 改善後（InMemory）：3480.6296 orders/msec
- 改善幅度：約 204 倍吞吐提升

Learning Points（學習要點）
核心知識點：
- 時間分桶與滑動視窗設計
- Queue/FIFO 與 O(1) 增量維護
- Interlocked 原子操作用法

技能要求：
- 必備技能：C# 多執行緒、資料結構（Queue）
- 進階技能：效能分析、時間序列視窗設計

延伸思考：
- 如何選擇 _interval 的粒度以平衡精度/資源？
- 如何以 ring buffer 減少 GC？
- 當 period 很大（小時級）是否需要分級聚合（多層桶）？

Practice Exercise（練習題）
- 基礎（30 分）：把 _interval 調成 1s 與 0.05s 比較穩定性。
- 進階（2 小時）：改成 ring buffer 實作，量測 GC 與吞吐差異。
- 專案（8 小時）：支援多種聚合（sum/count/max）與多視窗（1m/5m/1h）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：視窗 sum 正確、可配置 period/interval
- 程式碼品質（30%）：無資料競態、易讀、單元測試
- 效能優化（20%）：O(1) 更新、低 GC
- 創新性（10%）：多層預聚合/可觀測性（metrics）
```

```markdown
## Case #3: 用 Interlocked 消除多執行緒統計遺失（3.97% → 0%）

### Problem Statement（問題陳述）
**業務場景**：在高併發入單（多執行緒/多 Task）下，統計引擎要保持精準；未妥善處理臨界區會出現「金額被吃掉」的現象。
**技術挑戰**：CreateOrders 與 worker 會同時存取/修改 buffer 與 statistic，要保證不可分割與順序一致。
**影響範圍**：統計值偏小，報表失真，造成商業決策誤判。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 非原子遞增：多執行緒 buffer += amount 產生 lost update。
2. 非原子交換：讀取 buffer 再清零，中間被插入寫入。
3. 無同步策略：未使用 lock/原子操作。
**深層原因**：
- 架構層面：未設計共享狀態的安全存取策略。
- 技術層面：缺乏對原子操作/記憶體模型理解。
- 流程層面：缺少併發場景的自動化驗證。

### Solution Design（解決方案設計）
**解決策略**：以 .NET Interlocked.Add 與 Interlocked.Exchange 保障加總與交換不可分割；以兩版本互驗測出差異，確保 0% 偏差。

**實施步驟**：
1. 導入 Interlocked
- 實作細節：CreateOrders 使用 Interlocked.Add；worker 使用 Interlocked.Exchange 清空 buffer 且取舊值。
- 所需資源：.NET Threading
- 預估時間：0.5 天

2. 雙版本驗證
- 實作細節：建立 use_lock=true/false 兩個 InMemoryEngine，同源灌流，對比結果。
- 所需資源：測試主控台
- 預估時間：0.5 天

3. 壓測與報告
- 實作細節：20 執行緒連續 10 秒灌流，記錄偏差百分比。
- 所需資源：.NET
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public override int CreateOrders(int amount)
    => Interlocked.Add(ref _buffer, amount);

int buffer_value = Interlocked.Exchange(ref _buffer, 0); // 取舊值且歸零
```

實際案例：同時跑兩個 InMemoryEngine（有鎖/無鎖）10 秒：
實作環境：Windows 10、.NET、i7/16GB
實測數據：
- 改善前（無鎖）：誤差率 3.97%（lost updates）
- 改善後（Interlocked）：誤差率 0.00%
- 改善幅度：-3.97% → 0%（完全消除）

Learning Points（學習要點）
核心知識點：
- 原子操作與不可分割性
- 臨界區最小化與 lock-free 思維
- 競態條件的驗證方法

技能要求：
- 必備技能：.NET 原子操作 API
- 進階技能：併發測試、分析記憶體序模型

延伸思考：
- 何時選用 lock、Interlocked、Concurrent* 容器？
- 如何在分散式下保持「等價的原子性」？

Practice Exercise（練習題）
- 基礎（30 分）：把無鎖版本改為 Interlocked 版，做 A/B 比對。
- 進階（2 小時）：加上手寫 lock 版與 Interlocked 版，比較延遲/吞吐。
- 專案（8 小時）：擴展到 max/min 等聚合，保證原子性。

Assessment Criteria（評估標準）
- 功能完整性（40%）：誤差率趨近 0%
- 程式碼品質（30%）：無共享狀態洩漏、命名清晰
- 效能優化（20%）：Interlocked 相對 lock 有優勢
- 創新性（10%）：提出 lock-free 改良或觀測指標
```

```markdown
## Case #4: 以 Redis 實作分散式滑動視窗（Lists + INCRBY/DECRBY/GETSET）

### Problem Statement（問題陳述）
**業務場景**：要把即時統計從單機擴展為分散式，支援多個應用節點共同寫入，並實現高可用；但仍需維持時間窗剔除與增量維護的 O(1) 優勢。
**技術挑戰**：分散式共享狀態需原子操作；自研分散式鎖複雜且昂貴。
**影響範圍**：統計正確性、可用性與延遲直接影響整體系統 SLA。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 多節點共享變數：buffer/statistic/queue 難以一致。
2. 競態與重入：多 worker 容易重複剔除、重複加總。
3. 自研鎖風險高：可靠的分散式鎖實作困難。
**深層原因**：
- 架構層面：缺少共享狀態的外部一致存儲。
- 技術層面：不熟悉存儲層原子指令。
- 流程層面：未規劃單工 worker 與多 producer 協作。

### Solution Design（解決方案設計）
**解決策略**：將 queue/buffer/statistic 狀態遷至 Redis；使用 Lists 當 Queue，StringIncrement/Decrement 做總和，GetSet 做原子交換；僅保留單個 worker 處理搬運與逐出，其餘節點僅做寫入與查詢。

**實施步驟**：
1. 資料結構映射
- 實作細節：queue ⇒ Redis List；buffer/statistic ⇒ String；QueueItem 自行序列化。
- 所需資源：Redis、StackExchange.Redis
- 預估時間：0.5 天

2. 原子操作實作
- 實作細節：INCRBY/DECRBY/GETSET 替代 lock；ListRightPush/LeftPop 管理 FIFO。
- 所需資源：Redis
- 預估時間：0.5 天

3. 單工 worker 佈署
- 實作細節：一個節點啟動 worker，其餘關閉 worker（只生產/查詢）。
- 所需資源：多個應用實例
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public class InRedisEngine : EngineBase
{
    private IDatabase redis = ConnectionMultiplexer.Connect("host:6379").GetDatabase();
    private readonly TimeSpan _period = TimeSpan.FromMinutes(1);
    private readonly TimeSpan _interval = TimeSpan.FromSeconds(0.1);

    public InRedisEngine(bool start_worker = true)
    {
        if (start_worker)
            Task.Run(() => { while (true) { Task.Delay(_interval).Wait(); _worker(); } });
    }
    public override int StatisticResult =>
        (int)redis.StringGet("statistic") + (int)redis.StringGet("buffer");
    public override int CreateOrders(int amount) =>
        (int)redis.StringIncrement("buffer", amount);

    private void _worker()
    {
        int buf = (int)redis.StringGetSet("buffer", 0);
        redis.ListRightPush("queue", QueueItem.Encode(new QueueItem{ _count=buf, _time=DateTime.Now }));
        redis.StringIncrement("statistic", buf);

        while (true)
        {
            var head = QueueItem.Decode((string)redis.ListGetByIndex("queue", 0));
            if (head._time >= DateTime.Now - _period) break;
            var dq = QueueItem.Decode((string)redis.ListLeftPop("queue"));
            redis.StringDecrement("statistic", dq._count);
        }
    }
    public class QueueItem
    {
        public int _count; public DateTime _time;
        public static string Encode(QueueItem v) => $"{v._count},{(v._time - DateTime.MinValue).TotalMilliseconds}";
        public static QueueItem Decode(string s){ var a=s.Split(','); return new(){ _count=int.Parse(a[0]), _time=DateTime.MinValue+TimeSpan.FromMilliseconds(double.Parse(a[1]))}; }
    }
}
```

實際案例：10 個程式實例並行寫入，僅 1 個開啟 worker，分鐘統計約為單機 1770 的 10 倍（~17700）。
實作環境：Windows 10、.NET、Redis for Windows 3.2、i7/16GB
實測數據：
- 與 DB 比較吞吐：82.28 vs 17.0458 orders/msec（約 4.83 倍）
- 與 InMemory 比較：82.28 vs 3480.6296 orders/msec（慢 35.57 倍，但可分散/HA）
- 正確性：與 InMemory 對照誤差 0%

Learning Points（學習要點）
核心知識點：
- 利用存儲層原子操作落實分散式一致性
- Redis Lists 作為 Queue 的應用
- 單工 worker 與多 producer 模式

技能要求：
- 必備技能：Redis 指令、StackExchange.Redis
- 進階技能：分散式佈署、觀測與容錯

延伸思考：
- 如何容錯 worker（主從切換/leader election）？
- 需要 Lua script 嗎？何時需要 pipeline/transaction？

Practice Exercise（練習題）
- 基礎（30 分）：用 Lists/INCRBY/GETSET 寫出最小可行版本。
- 進階（2 小時）：10 個 producer + 1 worker，驗證分鐘統計 ≈10 倍。
- 專案（8 小時）：加上健康檢查/leader 選舉與高可用部署。

Assessment Criteria（評估標準）
- 功能完整性（40%）：分散式一致、正確逐出
- 程式碼品質（30%）：鍵命名、錯誤處理、可維運性
- 效能優化（20%）：減少 RTT、合理粒度
- 創新性（10%）：HA/leader election 設計
```

```markdown
## Case #5: 單工 Worker 的分散式協作模式（避免重複逐出/加總）

### Problem Statement（問題陳述）
**業務場景**：多個應用實例同時寫入共享 Redis 狀態，若每個實例都啟動 worker，會出現重複逐出或統計錯誤。
**技術挑戰**：如何在無分散式鎖的情況下，保證時間窗逐出只被執行一次。
**影響範圍**：重複扣減或重複入隊導致統計錯誤。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 多 worker 並行執行相同逐出邏輯。
2. 操作非冪等：重複執行造成數據錯誤。
3. 無共識/選主：無法指定唯一執行者。
**深層原因**：
- 架構層面：缺乏角色分工（producer/worker）。
- 技術層面：缺失冪等/去重設計。
- 流程層面：佈署策略未定義單工約束。

### Solution Design（解決方案設計）
**解決策略**：應用層配置只有 1 個實例啟動 worker，其餘實例以 producer 身分只負責寫入與讀取；藉此避開分散式鎖，引入最小變動即可正確運行。

**實施步驟**：
1. 啟動參數控制
- 實作細節：InRedisEngine(start_worker=false) 參數化。
- 所需資源：應用程式設定
- 預估時間：0.25 天

2. 佈署策略
- 實作細節：CI/CD/容器排程指定唯一 worker 節點。
- 所需資源：部署平台
- 預估時間：0.5 天

3. 監控與切換
- 實作細節：worker 健康檢查，故障時手動/自動切換。
- 所需資源：監控/告警
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// 啟動時注入 start_worker 參數
var engine = new InRedisEngine(start_worker: Environment.Get("ROLE") == "worker");
```

實際案例：10 個程式並行，9 個僅寫入，1 個執行 worker；每分鐘統計維持在約 17700（單機 1770 的 10 倍）。
實作環境：Windows 10、.NET、Redis
實測數據：
- 單機期望：1770/分鐘
- 10 節點合計：~17700/分鐘
- 偏差：小幅波動（時間邊界抖動）

Learning Points（學習要點）
核心知識點：
- 單工消費者/多生產者模式
- 冪等與避免重複執行
- 操作職責在佈署層落實

技能要求：
- 必備技能：應用設定、部署流水線
- 進階技能：健康檢查與自動切換

延伸思考：
- 是否需要自動 leader 選舉？
- worker 崩潰期間的數據一致性保障？

Practice Exercise（練習題）
- 基礎（30 分）：用啟動參數切換 worker/producer。
- 進階（2 小時）：加入簡易健康檢查與手動切換。
- 專案（8 小時）：用 Consul/etcd 做 leader 選舉自動化。

Assessment Criteria（評估標準）
- 功能完整性（40%）：僅一個 worker 在跑
- 程式碼品質（30%）：配置化、低耦合
- 效能優化（20%）：生產者不被 worker 阻塞
- 創新性（10%）：自動選主/切換方案
```

```markdown
## Case #6: 時間分桶 + 週期搬運（Buffer→Queue→Evict）工作流程

### Problem Statement（問題陳述）
**業務場景**：連續資料流入無間斷，須以固定粒度將資料匯總入桶，並定時移除超時桶保證視窗正確。
**技術挑戰**：如何在不鎖全域的情況下，持續搬運並保持 O(1) 更新時間。
**影響範圍**：若搬運/逐出錯誤，統計會累積誤差。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未分桶導致資料量巨大難以搬運。
2. 未原子交換導致部分資料丟失。
3. 逐出條件錯誤導致視窗擠壓或膨脹。
**深層原因**：
- 架構層面：無明確 ETL/worker 管線。
- 技術層面：未合理選擇時間粒度。
- 流程層面：缺乏暖機與邊界容錯策略。

### Solution Design（解決方案設計）
**解決策略**：採用固定 _interval 分桶，worker 每 _interval 取出 buffer（原子交換）、入隊、累加總和，並用 while 持續檢查隊首是否超窗，超窗則出隊並扣減。

**實施步驟**：
1. 設計分桶與粒度
- 實作細節：_period=60s，_interval=0.1s ⇒ 600 桶。
- 所需資源：.NET
- 預估時間：0.25 天

2. 原子搬運
- 實作細節：Exchange 讀/清 buffer；入隊並加總；迴圈逐出。
- 所需資源：Threading
- 預估時間：0.25 天

3. 查詢合成
- 實作細節：讀取 statistic + buffer 即為當前視窗值。
- 所需資源：.NET
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```csharp
int buf = Interlocked.Exchange(ref _buffer, 0);
_queue.Enqueue(new QueueItem { _count = buf, _time = DateTime.Now });
_statistic_result += buf;
while (_queue.Peek()._time < DateTime.Now - _period) {
    var dq = _queue.Dequeue();
    _statistic_result -= dq._count;
}
```

實際案例：暖機後維持 1770，偶見 1717~1769 的邊界抖動。
實作環境：Windows 10、.NET
實測數據：
- 暖機後穩態：1770
- 邊界抖動：偶發較小值，下一輪恢復
- 吞吐：與 Case #2 相同（O(1)）

Learning Points（學習要點）
核心知識點：
- 視窗逐出條件與實作
- 分桶粒度影響精度與成本
- 暖機與邊界效應

技能要求：
- 必備技能：時間處理、FIFO
- 進階技能：按需動態粒度調整

延伸思考：
- Interval 自適應：低流量放大粒度、高潮量縮小粒度？
- 逐出可否批次化以減少迴圈開銷？

Practice Exercise（練習題）
- 基礎（30 分）：把 _interval 改為 0.2s，比較邊界抖動。
- 進階（2 小時）：逐出改批次化（每次最多逐出 N 桶）。
- 專案（8 小時）：做成可視化 Demo（視窗曲線/抖動觀測）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確搬運與逐出
- 程式碼品質（30%）：清晰可維護
- 效能優化（20%）：迴圈成本/GC 控制
- 創新性（10%）：自適應粒度或批次逐出
```

```markdown
## Case #7: 兩版本互驗（慢版作準 vs 快版受測）抓出一致性問題

### Problem Statement（問題陳述）
**業務場景**：需要一套可重複的驗證方法，確保快版（最佳化）統計在各種併發壓力下正確。
**技術挑戰**：單一實作難以自證正確；需要參考實作作為地面實況（ground truth）。
**影響範圍**：未驗證的最佳化可能帶入隱性誤差。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 測試僅看單值（1770）無法覆蓋併發問題。
2. 缺少對照組使誤差難以量化。
3. 無自動化量化誤差比率。
**深層原因**：
- 架構層面：缺少測試口徑與基準。
- 技術層面：未建立可比較的雙實作。
- 流程層面：無長時間/多執行緒壓測制度。

### Solution Design（解決方案設計）
**解決策略**：同時跑兩個引擎（如 InMemory vs InDatabase / InRedis），用同一資料流灌入，定期比對結果差距與誤差率，作為迭代基礎。

**實施步驟**：
1. 建立雙引擎管道
- 實作細節：兩引擎共用產生器（多執行緒灌流）。
- 所需資源：.NET
- 預估時間：0.5 天

2. 收斂誤差
- 實作細節：若誤差>0，定位到原子性/逐出/粒度等原因。
- 所需資源：Profiler/Logging
- 預估時間：1 天

3. 報告化
- 實作細節：輸出誤差百分比、吞吐。
- 所需資源：Console/Report
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
// 省略細節：雙引擎同源灌流、10 秒後比較
Console.WriteLine($"engine #1: {e1.StatisticResult} ({e1.GetType().Name})");
Console.WriteLine($"engine #2: {e2.StatisticResult} ({e2.GetType().Name})");
Console.WriteLine($"compare: {e1.StatisticResult == e2.StatisticResult}, diff: {diff:P2}");
```

實際案例：InMemory vs InDatabase（兩者相等，0% 差異）；InMemory（有鎖）vs InMemory（無鎖）出現 3.97% 差異。
實作環境：Windows 10、.NET
實測數據：
- 有鎖 vs 無鎖：誤差 3.97%
- InMemory vs InRedis：0% 差異
- InDatabase vs InMemory：0% 差異

Learning Points（學習要點）
核心知識點：
- 兩版本互驗策略
- 誤差量化與回歸
- 壓測覆蓋併發情境

技能要求：
- 必備技能：並發測試、記錄統計
- 進階技能：問題定位（原子性/視窗邏輯）

延伸思考：
- 如何把此策略常態化（CI 中長時間測）？
- 如何用 property-based testing 擴量測試輸入？

Practice Exercise（練習題）
- 基礎（30 分）：建立雙引擎比對框架。
- 進階（2 小時）：加入誤差報表輸出。
- 專案（8 小時）：整合到 CI，每日跑 1h 長測。

Assessment Criteria（評估標準）
- 功能完整性（40%）：誤差量化可用
- 程式碼品質（30%）：測試框架可維護
- 效能優化（20%）：測試不干擾引擎
- 創新性（10%）：自動化回歸與報表
```

```markdown
## Case #8: 效能壓測腳本（LoadTest）與結果解讀

### Problem Statement（問題陳述）
**業務場景**：需要客觀比較三種方案（DB、InMemory、Redis）的吞吐能力，支持架構選型。
**技術挑戰**：建立一致可重複的壓測方法，並避免測試本身成為瓶頸。
**影響範圍**：錯誤結論會導致不當投資與運維成本。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無統一壓測腳本與參數。
2. 無一致硬體/環境基準。
3. 未量化 orders/msec 指標。
**深層原因**：
- 架構層面：缺失性能基線流程。
- 技術層面：測試工具缺乏。
- 流程層面：未將效能測試納入決策。

### Solution Design（解決方案設計）
**解決策略**：以相同程式碼模板（20 執行緒、連續 10 秒灌入 CreateOrders(1)），對單一引擎分別測試，取得 orders/msec 指標，對照硬體環境。

**實施步驟**：
1. 撰寫壓測方法
- 實作細節：固定執行緒數、時間長度、負載型態。
- 所需資源：.NET
- 預估時間：0.5 天

2. 固定環境
- 實作細節：相同硬體/OS/Redis/SQL 版本。
- 所需資源：實驗室主機
- 預估時間：0.5 天

3. 統計輸出
- 實作細節：輸出總筆數與 orders/msec。
- 所需資源：Console
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```csharp
static void LoadTest()
{
    EngineBase e1 = new InRedisEngine(); // 依序換成各引擎
    bool stop = false;
    int thread_count = 20;
    var threads = new List<Thread>();
    for (int i = 0; i < thread_count; i++)
    {
        var t = new Thread(() => { while (!stop) { Thread.Sleep(0); e1.CreateOrders(1); } });
        threads.Add(t); t.Start();
    }
    var duration = TimeSpan.FromSeconds(10);
    Thread.Sleep(duration); stop = true; threads.ForEach(t => t.Join());
    Console.WriteLine($"performance: {e1.StatisticResult / duration.TotalMilliseconds} orders/msec");
}
```

實際案例：三引擎測試結果
實作環境：Windows 10、i7/16GB、SSD、SQL 2017 Dev、Redis 3.2
實測數據：
- InMemory：3480.6296 orders/msec
- InRedis：82.28 orders/msec
- InDatabase：17.0458 orders/msec

Learning Points（學習要點）
核心知識點：
- 一致性壓測設計
- 單位（orders/msec）可比較性
- 環境固定的重要性

技能要求：
- 必備技能：並發程式、計量輸出
- 進階技能：效能歸因（CPU/IO/RTT）

延伸思考：
- 如何用 BenchmarkDotNet/PerfView 深入？
- 如何避免 JIT/GC 影響（預熱/長測）？

Practice Exercise（練習題）
- 基礎（30 分）：跑三引擎，收集 orders/msec。
- 進階（2 小時）：加入 1 分鐘長測與方差輸出。
- 專案（8 小時）：自動化效能儀表板（時序圖）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可重複測試輸出一致單位
- 程式碼品質（30%）：參數化/封裝良好
- 效能優化（20%）：測試本身開銷低
- 創新性（10%）：圖表化與比較分析
```

```markdown
## Case #9: 從 O(N) 掃描到 O(1) 增量維護（數量級優化）

### Problem Statement（問題陳述）
**業務場景**：即時查詢每秒觸發，交易流量極大，必須讓每次查詢/更新成本固定，否則會被時間窗與資料量拖垮。
**技術挑戰**：避免每次查詢掃描整個時間窗內的所有明細。
**影響範圍**：吞吐與延遲直接取決於時間複雜度。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. SQL SUM 每次都是 O(K)（K=窗內筆數）。
2. 時間窗越長，掃描越慢。
3. 筆數越高，IO/CPU/鎖競爭加劇。
**深層原因**：
- 架構層面：未將聚合與存取分離。
- 技術層面：未使用 Queue/分桶 O(1) 方案。
- 流程層面：未設定演算法複雜度目標。

### Solution Design（解決方案設計）
**解決策略**：採用 Case #2 的分桶/Queue 與統計總和增量維護，查詢時 O(1) 讀取 statistic + buffer；每個 interval O(1) 搬運一次。

**實施步驟**：
1. 明確複雜度目標
- 實作細節：查詢/更新/逐出皆盡量 O(1)。
- 所需資源：設計評審
- 預估時間：0.25 天

2. 實作分桶增量
- 實作細節：Queue + buffer + statistic。
- 所需資源：.NET
- 預估時間：0.5 天

3. 驗證與對比
- 實作細節：與 SQL 方案壓測對比 orders/msec。
- 所需資源：壓測工具
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public override int StatisticResult => _statistic_result + _buffer; // O(1)
public override int CreateOrders(int amount) => Interlocked.Add(ref _buffer, amount); // O(1)
```

實際案例：InMemory（O(1)） vs DB（O(K)）吞吐差異顯著。
實作環境：同上
實測數據：
- DB：17.0458 orders/msec
- InMemory：3480.6296 orders/msec
- 改善幅度：約 204 倍

Learning Points（學習要點）
核心知識點：
- 複雜度對吞吐的決定性作用
- 分桶/Queue 的降階思想
- 增量維護 vs 全量掃描

技能要求：
- 必備技能：資料結構/演算法
- 進階技能：效能建模與預估

延伸思考：
- 再加一層分級（秒→分）是否可支撐更大 period？
- 對於 percentile/unique 等如何做近似？

Practice Exercise（練習題）
- 基礎（30 分）：寫出 O(1) 查詢/更新 demo。
- 進階（2 小時）：加入 count/max，證明仍為 O(1)。
- 專案（8 小時）：寫一份設計說明，推導複雜度與容量邊界。

Assessment Criteria（評估標準）
- 功能完整性（40%）：指標正確
- 程式碼品質（30%）：清晰證明 O(1)
- 效能優化（20%）：吞吐提升顯著
- 創新性（10%）：更通用的聚合介面
```

```markdown
## Case #10: 邊界時間抖動的誤差管理與驗證

### Problem Statement（問題陳述）
**業務場景**：時間窗邊界上，部分事件因時間誤差可能落入或落出視窗，導致瞬時值偶有偏差。
**技術挑戰**：如何驗證與容忍誤差，避免誤判為功能錯誤。
**影響範圍**：監控/自動化測試穩定性。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 取樣時刻與事件時間不一致。
2. 系統延遲與 timer 精度限制。
3. 事件時間戳不穩定（寫入延遲）。
**深層原因**：
- 架構層面：未定義時間語義（event time vs processing time）。
- 技術層面：timer 與等待策略不嚴謹。
- 流程層面：測試未設暖機與容忍區間。

### Solution Design（解決方案設計）
**解決策略**：在測試中加入暖機（>1 視窗長度）後再判定；觀察數值落在期望值（1770）附近時視為可接受；將斷言調整為人工/寬容比對。

**實施步驟**：
1. 暖機期
- 實作細節：啟動後等待滿一個視窗長度再開始判定。
- 所需資源：測試調整
- 預估時間：0.25 天

2. 寬容比對
- 實作細節：允許小範圍偏差，不做硬性 assert。
- 所需資源：測試程式
- 預估時間：0.25 天

3. 記錄與觀察
- 實作細節：列印當前/預期，人工核對。
- 所需資源：Console 日誌
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```csharp
// 測試輸出（略）：statistic: {current}, expected: 1770, test: {current == expected}
// 實作上避免硬性 Assert，觀察邊界抖動。
```

實際案例：在 InMemory/DB/Redis 測試時，偶見 1717~1769 等值，但多數時間維持 1770。
實作環境：同上
實測數據：
- 觀測值：1770 為主，偶見 1752/1751/1749/1717 等
- 措施：採寬容判定、以長時間平均為準

Learning Points（學習要點）
核心知識點：
- event time vs processing time
- 暖機與邊界效應
- 驗證中的容忍策略

技能要求：
- 必備技能：測試設計
- 進階技能：時間序列驗證與可觀測性

延伸思考：
- 若能取得事件時間，是否應採 watermark 判定？
- 是否需要雙通道（raw vs aggregated）比對？

Practice Exercise（練習題）
- 基礎（30 分）：加入暖機後再輸出判定。
- 進階（2 小時）：做出允許 ±X% 的容忍比對。
- 專案（8 小時）：引入 event time 與 watermark 的測試框架。

Assessment Criteria（評估標準）
- 功能完整性（40%）：誤報顯著減少
- 程式碼品質（30%）：測試清晰、易調整
- 效能優化（20%）：測試執行開銷低
- 創新性（10%）：引入先進時間語義
```

```markdown
## Case #11: Orders 表設計與時間索引支援區間查詢

### Problem Statement（問題陳述）
**業務場景**：在 DB 方案中，需要讓「時間區間」過濾和 SUM 儘可能高效。
**技術挑戰**：時間序列表會快速長大，掃描與 I/O 成本高。
**影響範圍**：查詢延遲、交易衝擊。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無索引導致全表掃描。
2. 單表累積無封存。
3. 金額型態與聚合成本。
**深層原因**：
- 架構層面：OLTP/OLAP 未分離。
- 技術層面：索引策略缺失。
- 流程層面：未建立歸檔/分區週期。

### Solution Design（解決方案設計）
**解決策略**：在 time 欄位建立索引，保證 WHERE time BETWEEN 的篩選走索引；同時保留此為基線，推導轉向預聚合的必要性。

**實施步驟**：
1. 建立索引
- 實作細節：對 [time] 建非聚集索引。
- 所需資源：SQL Server
- 預估時間：0.25 天

2. 查詢優化
- 實作細節：確保查詢符合索引使用（避免函數包裹 time 欄位）。
- 所需資源：查詢分析器
- 預估時間：0.25 天

3. 建立基準
- 實作細節：跑壓測取得 orders/msec 基線。
- 所需資源：測試腳本
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
CREATE INDEX [IX_orders_Column] ON [dbo].[orders] ([time]);
SELECT SUM(amount) FROM [orders]
WHERE time BETWEEN DATEADD(second, -60, GETDATE()) AND GETDATE();
```

實際案例：加入索引後仍然受限於全量掃描與 SUM 聚合成本。
實作環境：同上
實測數據：
- DB：17.0458 orders/msec（索引存在）
- 對照（InMemory）：3480.6296 orders/msec
- 結論：DB 方案不適合長期/高頻視窗統計

Learning Points（學習要點）
核心知識點：
- 時間欄位索引與 BETWEEN
- 聚合與篩選的成本
- 索引不是萬靈丹

技能要求：
- 必備技能：SQL/索引
- 進階技能：查詢計畫分析

延伸思考：
- 分區表/歸檔策略如何落地？
- 何時切換至流式預聚合方案？

Practice Exercise（練習題）
- 基礎（30 分）：建立與移除索引，觀察查詢計畫。
- 進階（2 小時）：嘗試分區表，量測效果。
- 專案（8 小時）：模擬歸檔流程，限制表大小。

Assessment Criteria（評估標準）
- 功能完整性（40%）：查詢可用
- 程式碼品質（30%）：無 SQL 注入，索引命名清楚
- 效能優化（20%）：能讀懂計畫並調整
- 創新性（10%）：提出分區/CDC 等方案
```

```markdown
## Case #12: 以存儲層原子操作取代分散式鎖

### Problem Statement（問題陳述）
**業務場景**：分散式統計需要跨節點一致的遞增/遞減/交換；自建分散式鎖風險大且複雜。
**技術挑戰**：如何確保操作原子性與正確性，同時維持高效能。
**影響範圍**：錯誤的分散式鎖會導致死鎖/資料錯亂。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 多步操作不可分割。
2. 自研鎖難以正確處理失敗/超時。
3. Redis/DB 原子能力沒被利用。
**深層原因**：
- 架構層面：未善用基建能力。
- 技術層面：對命令原子性認知不足。
- 流程層面：未評估鎖與原子指令差異。

### Solution Design（解決方案設計）
**解決策略**：用 Redis 的 INCRBY/DECRBY/GETSET/ListPush/Pop，保證操作不可分割；避免引入分散式鎖，降低系統複雜度與風險。

**實施步驟**：
1. 命令選型
- 實作細節：選定 INCRBY/DECRBY/GETSET/List*。
- 所需資源：Redis 文檔
- 預估時間：0.25 天

2. API 封裝
- 實作細節：封裝為 Engine 方法，隔離實作。
- 所需資源：.NET
- 預估時間：0.5 天

3. 正確性驗證
- 實作細節：與 InMemory 作對照，驗證 0% 誤差。
- 所需資源：測試框架
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
redis.StringIncrement("buffer", amount);    // INCRBY
int buf = (int)redis.StringGetSet("buffer", 0); // GETSET
redis.StringIncrement("statistic", buf);    // INCRBY
redis.ListLeftPop("queue");                 // LPOP
```

實際案例：InRedis 與 InMemory 結果 0% 差異，免去自建鎖。
實作環境：同上
實測數據：
- 正確性：0% 差異
- 吞吐：82.28 orders/msec
- 對比 DB：提升約 4.83 倍

Learning Points（學習要點）
核心知識點：
- 原子指令優先於分散式鎖
- 操作冪等與錯誤處理
- 封裝與依賴反轉（易於替換）

技能要求：
- 必備技能：Redis 命令
- 進階技能：故障注入測試

延伸思考：
- 何時需要 Lua script 以組合原子操作？
- 是否需要 Redis Cluster？鍵分片影響？

Practice Exercise（練習題）
- 基礎（30 分）：替換某一步 lock 為原子命令。
- 進階（2 小時）：用 Lua 把多步封裝成一個原子腳本。
- 專案（8 小時）：鍵分片版本，驗證一致性。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確且一致
- 程式碼品質（30%）：封裝良好
- 效能優化（20%）：RTT/指令數低
- 創新性（10%）：容錯與災備設計
```

```markdown
## Case #13: Redis 隊列項目的序列化策略（時間+數值）

### Problem Statement（問題陳述）
**業務場景**：需要把 QueueItem（count + timestamp）存入 Redis List；Redis List 儲存字串，需自定編碼。
**技術挑戰**：序列化/反序列化正確性、時間精度、跨語言互通。
**影響範圍**：解碼錯誤會導致逐出判斷錯誤。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. List 僅支援字串元素。
2. 時間格式不統一有時區/精度問題。
3. JSON/XML 序列化過重。
**深層原因**：
- 架構層面：無統一序列化規範。
- 技術層面：時間表示選擇不當。
- 流程層面：缺少互通測試。

### Solution Design（解決方案設計）
**解決策略**：採用「count,毫秒值」的簡單字串格式，以 DateTime.MinValue 為原點存 milliseconds，兼顧精度與輕量；Decode 時切割轉回。

**實施步驟**：
1. 格式設計
- 實作細節：「{count},{millisSinceMinValue}」。
- 所需資源：.NET
- 預估時間：0.25 天

2. 編解碼實作
- 實作細節：Encode/Decode 靜態方法。
- 所需資源：.NET
- 預估時間：0.25 天

3. 測試
- 實作細節：不同時區/語系下來回轉換驗證。
- 所需資源：單元測試
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
public static string Encode(QueueItem v)
  => $"{v._count},{(v._time - DateTime.MinValue).TotalMilliseconds}";

public static QueueItem Decode(string s)
{
    var a = s.Split(',');
    return new QueueItem {
        _count = int.Parse(a[0]),
        _time = DateTime.MinValue + TimeSpan.FromMilliseconds(double.Parse(a[1]))
    };
}
```

實際案例：在 InRedisEngine 中使用此序列化，正確逐出窗口外的桶。
實作環境：同上
實測數據：
- 正確性：與 InMemory 對照 0% 差異
- 效能：輕量字串，List 操作快速

Learning Points（學習要點）
核心知識點：
- 輕量序列化策略
- 時間編碼的選擇與精度
- Redis List 的元素型別限制

技能要求：
- 必備技能：字串處理
- 進階技能：跨語言時間互通

延伸思考：
- 是否改用 protobuf/MessagePack 並存為 byte[]
- 使用 RPOPLPUSH 做原子轉移？

Practice Exercise（練習題）
- 基礎（30 分）：寫 Encode/Decode 測試。
- 進階（2 小時）：替換為二進位序列化，量測差異。
- 專案（8 小時）：跨語言（Node.js/C#）互通測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確來回轉換
- 程式碼品質（30%）：健壯性（錯誤輸入）
- 效能優化（20%）：序列化效能
- 創新性（10%）：可擴充格式設計
```

```markdown
## Case #14: 秒值序列驗證法（0..59 求和=1770）快速驗證滑動窗

### Problem Statement（問題陳述）
**業務場景**：需要快速建立一個可驗證滑動窗邏輯正確的測試資料流。
**技術挑戰**：確保「任何 60 秒視窗」內的總和都一致，便於判斷正確性。
**影響範圍**：縮短迭代週期，快速發現錯誤。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 隨機數據難以推導期望值。
2. 邊界漂移難以穩定判定。
3. 單元測試難以覆蓋連續場景。
**深層原因**：
- 架構層面：測試數據設計不足。
- 技術層面：缺少可閉合的數學特性。
- 流程層面：未固化測試法。

### Solution Design（解決方案設計）
**解決策略**：每秒用 DateTime.Now.Second 作為 amount，任何完整的 60 秒窗都應等於 (0+59)*60/2=1770；以此作為期望值對照。

**實施步驟**：
1. 產流器
- 實作細節：每秒 e.CreateOrders(DateTime.Now.Second)。
- 所需資源：.NET
- 預估時間：0.25 天

2. 取樣器
- 實作細節：每 200ms 取一次統計結果。
- 所需資源：.NET
- 預估時間：0.25 天

3. 對照輸出
- 實作細節：輸出 current/expected/test。
- 所需資源：Console
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```csharp
Task.Run(() => {
    while (!stop) { Task.Delay(1000).Wait(); e.CreateOrders(DateTime.Now.Second); }
});
int expected = (0 + 59) * 60 / 2; // 1770
Task.Run(() => {
    while (!stop) { Task.Delay(200).Wait();
        Console.WriteLine($"statistic: {e.StatisticResult}, expected: {expected}, test: {e.StatisticResult == expected}");
    }
});
```

實際案例：InMemory/DB/Redis 均以此驗證，暖機後多數時間為 1770。
實作環境：同上
實測數據：
- 期望值：1770
- 實測：大多數相等，偶有邊界抖動

Learning Points（學習要點）
核心知識點：
- 測試資料設計的數學閉合性
- 驗證滑動窗的簡捷方法
- 暖機的重要性

技能要求：
- 必備技能：測試腳本
- 進階技能：構造可預期的資料流

延伸思考：
- 是否可設計其他閉合序列（如循環三角波）？
- 轉為自動化斷言門檻（±閾值）？

Practice Exercise（練習題）
- 基礎（30 分）：以 0..59 序列驗證。
- 進階（2 小時）：加入其他函數序列（正弦波）並推導期望。
- 專案（8 小時）：測試場景模版化與報表。

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試可重複
- 程式碼品質（30%）：清晰易用
- 效能優化（20%）：測試不影響引擎
- 創新性（10%）：更多閉合序列設計
```

```markdown
## Case #15: 架構選型決策：InMemory vs Redis vs Database

### Problem Statement（問題陳述）
**業務場景**：需要在性能、可用性、成本、複雜度間做平衡，選出合宜的統計架構。
**技術挑戰**：不同解法在吞吐、可擴展、可用性與成本上有巨大差異。
**影響範圍**：關乎長期可擴展與維運。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. DB 方案吞吐低、影響交易。
2. InMemory 方案快但單機、無 HA。
3. Redis 方案分散式但吞吐較低、增加外部依賴。
**深層原因**：
- 架構層面：未定義非功能性需求（SLO/SLA）。
- 技術層面：缺乏量化比較。
- 流程層面：選型未引入壓測數據。

### Solution Design（解決方案設計）
**解決策略**：以統一壓測數據為依據，映射到需求優先級：單機極致吞吐選 InMemory；需分散式與 HA 選 Redis；DB 僅作原型或對照組。

**實施步驟**：
1. 定義需求權重
- 實作細節：吞吐/HA/成本/可維運。
- 所需資源：架構會議
- 預估時間：0.25 天

2. 數據對照
- 實作細節：引入 Case #8 數據。
- 所需資源：報表
- 預估時間：0.25 天

3. 決策與路線圖
- 實作細節：短期/長期雙路徑（先 InMemory，後 Redis）。
- 所需資源：Roadmap
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```text
無（決策與比較說明）
```

實際案例：基於測得吞吐與一致性，選擇 InMemory 作為嵌入式統計（單機），Redis 作為分散式與 HA 版本（中長期）。
實作環境：同上
實測數據（orders/msec）：
- InMemory：3480.6296（最快）
- Redis：82.28（分散式/HA）
- DB：17.0458（基線/不建議長期）

Learning Points（學習要點）
核心知識點：
- 架構選型需數據驅動
- 非功能性需求映射
- 漸進式演進

技能要求：
- 必備技能：分析/溝通
- 進階技能：Roadmap 與風險控管

延伸思考：
- Redis 方案的水平擴展與觀測如何做？
- 是否引入 Kafka/ASA 等作更大規模處理？

Practice Exercise（練習題）
- 基礎（30 分）：列出團隊需求權重並排序。
- 進階（2 小時）：用數據撰寫選型報告。
- 專案（8 小時）：制定落地與遷移路線圖。

Assessment Criteria（評估標準）
- 功能完整性（40%）：決策合理有據
- 程式碼品質（30%）：N/A（文檔品質）
- 效能優化（20%）：選型能滿足指標
- 創新性（10%）：提出可演進選項
```

```markdown
## Case #16: 參數調校：Period/Interval 的精度與資源取捨

### Problem Statement（問題陳述）
**業務場景**：不同場景對精度與資源的要求不同，需調整 period/interval 以平衡精度、延遲與資源使用。
**技術挑戰**：interval 越小，搬運頻率越高；interval 越大，精度與邊界抖動變差。
**影響範圍**：準確性/延遲/CPU 使用率/GC。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. interval 決定桶數與 worker 開銷。
2. period/interval 比例決定 Queue 長度。
3. 過小 interval 帶來高頻系統呼叫。
**深層原因**：
- 架構層面：未定義精度需求。
- 技術層面：未量化資源/精度曲線。
- 流程層面：缺少調參流程與基準。

### Solution Design（解決方案設計）
**解決策略**：以 O(1) 設計為基礎，公式化評估空間複雜度=O(period/interval)；透過實測不同 interval（如 1s / 0.1s / 0.05s）對邊界抖動與 CPU 的影響，選定平衡點。

**實施步驟**：
1. 目標定義
- 實作細節：設定精度/延遲/CPU 目標。
- 所需資源：SLO
- 預估時間：0.25 天

2. 參數掃描
- 實作細節：在固定 period=60s 下掃描 interval 參數。
- 所需資源：壓測腳本
- 預估時間：0.5 天

3. 曲線擬合
- 實作細節：產出 interval→抖動/CPU 曲線，選擇平衡點。
- 所需資源：數據分析工具
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```csharp
private readonly TimeSpan _period = TimeSpan.FromMinutes(1);
// 嘗試不同 interval
private readonly TimeSpan _interval = TimeSpan.FromSeconds(0.1); // or 1s / 0.05s
```

實際案例：文中使用 0.1s interval（每分鐘 600 桶），暖機後穩態表現良好。
實作環境：同上
實測數據：
- 空間複雜度：~period/interval × sizeof(QueueItem)
- 抖動：interval 越小越抑制（觀察值）
- 吞吐：維持 O(1) 水準

Learning Points（學習要點）
核心知識點：
- period/interval 與資源/精度關係
- 以 O(1) 為前提的調參
- 用實測曲線做決策

技能要求：
- 必備技能：實驗設計與分析
- 進階技能：系統調參方法論

延伸思考：
- 自適應 interval：根據負載動態調整？
- 與 GC/排程器互動的最佳做法？

Practice Exercise（練習題）
- 基礎（30 分）：比較 interval=1s 與 0.1s 的輸出差異。
- 進階（2 小時）：加入 CPU/GC 採樣，建立曲線。
- 專案（8 小時）：做成配置化與動態調整 PoC。

Assessment Criteria（評估標準）
- 功能完整性（40%）：參數化可運行
- 程式碼品質（30%）：配置清晰
- 效能優化（20%）：找到平衡點
- 創新性（10%）：自適應策略雛形
```

```markdown
## Case #17: 以 Azure Stream Analytics TumblingWindow 實作托管串流分析（加分題）

### Problem Statement（問題陳述）
**業務場景**：團隊希望使用雲端託管服務處理連續資料，簡化維運，並以 SQL 類語法表達時間窗聚合。
**技術挑戰**：快速上雲且維持可觀測性，接入多來源並輸出多目的地。
**影響範圍**：可維運性與可擴展性提升。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 自建方案維護成本高。
2. 異質來源/匯出需求多。
3. 需要事件時間窗與內建操作子。
**深層原因**：
- 架構層面：趨向託管化/平台化。
- 技術層面：熟悉流式 SQL 語法。
- 流程層面：佈署/監控/調參平台化。

### Solution Design（解決方案設計）
**解決策略**：採用 Azure Stream Analytics，以 TumblingWindow 寫視窗聚合；前接 Queue/Event Hub/Kafka，後寫 Storage/DB/Power BI；以托管服務承擔擴展與監控。

**實施步驟**：
1. 管線串接
- 實作細節：設定 Input（事件來源）與 Output（存放/可視化）。
- 所需資源：Azure 訂閱
- 預估時間：1 天

2. 查詢編寫
- 實作細節：以 SQL 類語法寫 SUM + TumblingWindow。
- 所需資源：ASA 工作
- 預估時間：0.5 天

3. 監控與擴展
- 實作細節：設定作業單位、scale、警示。
- 所需資源：Azure 監控
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
SELECT
  Make,
  SUM(CAST(Weight AS BIGINT)) AS Weight
FROM
  Input TIMESTAMP BY Time
GROUP BY
  Make,
  TumblingWindow(second, 10);
```

實際案例：使用 ASA 以 TumblingWindow(second,10) 完成 10 秒窗加總。
實作環境：Azure Stream Analytics
實測數據：
- 功能性：以 SQL 語法快速表達時間窗
- 性能/吞吐：本文未提供量化數據（依實際方案配置而定）
- 成效：維運/擴展/整合成本下降（定性）

Learning Points（學習要點）
核心知識點：
- 流式 SQL：Tumbling/Sliding 視窗
- 托管服務的取捨
- 事件時間/時間戳處理

技能要求：
- 必備技能：Azure 服務操作
- 進階技能：流式查詢設計、監控

延伸思考：
- 何時選 ASA vs 自建 Redis/InMemory？
- 與 Event Hub/Kusto/Databricks 的整合？

Practice Exercise（練習題）
- 基礎（30 分）：建立簡單 10 秒窗 SUM 作業。
- 進階（2 小時）：新增多輸出（Blob + Power BI）。
- 專案（8 小時）：端到端串流管線 PoC（事件→ASA→儲存→視覺化）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確視窗聚合
- 程式碼品質（30%）：查詢清晰、時序處理正確
- 效能優化（20%）：合理配置單位與輸出
- 創新性（10%）：與監控/警示整合
```
```

案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case #1, #10, #11, #13, #14
- 中級（需要一定基礎）
  - Case #2, #3, #5, #6, #7, #8, #9, #15, #16
- 高級（需要深厚經驗）
  - Case #4, #12, #17

2. 按技術領域分類
- 架構設計類：#2, #4, #5, #9, #12, #15, #16, #17
- 效能優化類：#2, #8, #9, #16
- 整合開發類：#4, #11, #13, #17
- 除錯診斷類：#3, #6, #7, #10, #14
- 安全防護類：本篇未涵蓋傳統安全，但 #12 涉及一致性/原子性的「資料安全」

3. 按學習目標分類
- 概念理解型：#1, #9, #10, #11, #15
- 技能練習型：#2, #3, #6, #8, #13, #16
- 問題解決型：#4, #5, #7, #12, #14
- 創新應用型：#17（雲端托管串流）

案例關聯圖（學習路徑建議）
- 建議先學：
  - Case #14（秒值序列驗證法）：快速建立直覺與測試方法
  - Case #1（DB 基線）：理解基線與其侷限
  - Case #11（索引）：了解 DB 端可做而有限
- 再學（資料結構與 O(1) 思維）：
  - Case #2（InMemory O(1) 解法）
  - Case #6（搬運與逐出工作流）
  - Case #9（複雜度優化）
- 併發正確性與驗證：
  - Case #3（Interlocked）
  - Case #7（兩版本互驗）
  - Case #10（邊界抖動管理）
  - Case #8（壓測）
- 分散式落地與演進：
  - Case #12（原子操作取代鎖）
  - Case #5（單工 worker）
  - Case #4（Redis 分散式）
  - Case #16（參數調校）
- 架構選型與雲端托管：
  - Case #15（選型決策）
  - Case #17（Azure Stream Analytics）

依賴關係：
- #2 依賴 #14/#1（測試/基線）與 #6（流程）
- #3 依賴 #2（共享狀態情境）
- #4 依賴 #2/#12（原子操作概念）與 #5（單工 worker）
- #12 依賴 Redis 指令概念，可先讀 #4 的原理段
- #17 可在完成 #4/#15 後學，理解取捨

完整學習路徑建議：
- 第一階段（基礎與測試）：#14 → #1 → #11 → #10
- 第二階段（核心解法）：#2 → #6 → #9 → #3 → #7 → #8
- 第三階段（分散式化）：#12 → #5 → #4 → #16
- 第四階段（選型與上雲）：#15 → #17

說明：此路徑從基線與測試開始，建立可驗證的學習土壤；再掌握 O(1) 解法與正確性保障；之後邁向分散式能力與參數調校；最後做架構選型與雲端實踐，完成從單機到分散式、從理論到實戰的完整閉環。