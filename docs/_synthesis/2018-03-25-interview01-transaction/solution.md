---
layout: synthesis
title: "架構面試題 #1, 線上交易的正確性"
synthesis_type: solution
source_post: /2018/03/25/interview01-transaction/
redirect_from:
  - /2018/03/25/interview01-transaction/solution/
postid: 2018-03-25-interview01-transaction
---

以下內容基於使用者提供的文章，提取與重構 15 個具完整教學價值的問題解決案例。每一案例均包含問題、根因、可落地的解法（含程式碼/流程）、實測或成效指標，以及可操作的練習與評估標準。案例間相互銜接，形成逐步擴展從單機到分散式的學習路徑。

## Case #1: 單機臨界區保護，避免並發時錯帳（C# lock）

### Problem Statement（問題陳述）
業務場景：單一應用執行緒內處理使用者儲值與交易明細紀錄（帳戶餘額與交易歷史）。為加速吞吐，系統在同一進程內開啟多個執行緒，模擬 N 個執行緒各執行 M 次存入 1.0 的交易，期望最後餘額增加 N×M。  
技術挑戰：並行讀寫 balance 與 history 的讀改寫（Read-Modify-Write）重疊，造成 lost update。  
影響範圍：錯帳、交易明細與餘額不一致、財務與稽核風險。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 發生競態條件（race condition）：多個執行緒同時讀取舊值並寫回，彼此覆蓋結果。  
2. 臨界區缺失：更新餘額與寫入交易明細是不可分割的原子操作卻未被綁定。  
3. 無同步機制：缺乏 lock/互斥量導致操作重疊。

深層原因：
- 架構層面：單機並行缺乏臨界區模型。  
- 技術層面：未運用語言級同步原語（lock/Monitor/Interlocked）。  
- 流程層面：缺少併發場景的單元測試與壓測驗證。

### Solution Design（解決方案設計）
解決策略：在單機範圍以語言級 lock 將「寫交易明細 + 更新餘額」包成臨界區，確保 ACID 中的一致性與隔離性（在進程內）。以共享同步物件序列化併發更新。

實施步驟：
1. 建立同步根物件  
- 實作細節：private object _syncroot = new object();  
- 所需資源：C# 語言內建 lock。  
- 預估時間：0.5 小時。

2. 將兩個寫入操作包入 lock 區塊  
- 實作細節：history.Add() 與 balance += amount 置於 lock(_syncroot) 中。  
- 所需資源：無。  
- 預估時間：0.5 小時.

關鍵程式碼/設定：
```csharp
public class LockAccount : AccountBase
{
    private decimal _balance = 0;
    private List<TransactionItem> _history = new List<TransactionItem>();
    private readonly object _syncroot = new object();

    public override decimal GetBalance() => _balance;

    public override decimal ExecTransaction(decimal transferAmount)
    {
        lock (_syncroot) // 臨界區，避免讀改寫重疊
        {
            _history.Add(new TransactionItem { Date = DateTime.Now, Amount = transferAmount });
            return _balance += transferAmount; // 與歷史寫入綁在一起
        }
    }
}
```

實際案例：單機多執行緒測試，history 與 balance 同步更新，交易正確。  
實作環境：.NET/C#（Console 專案），多執行緒模擬併發。  
實測數據：  
改善前：錯帳（見 Case #2）。  
改善後：PASS，Expected=20000, Actual=20000；1538461 trans/sec。  
改善幅度：正確率由不穩定提升到 100%；吞吐較無鎖略低但可接受。

Learning Points（學習要點）
核心知識點：
- 臨界區與競態條件  
- 語言級同步原語（lock）  
- 原子性、隔離性在單機層的落地

技能要求：
- 必備技能：C# 多執行緒、基本同步原語  
- 進階技能：效能分析與鎖競爭診斷

延伸思考：
- 何時可用細粒度鎖提升併發？  
- 若臨界區過大導致效能下降，有何替代策略？  
- 可否用 lock-free 結構？（在金額正確性要求下通常不建議）

Practice Exercise（練習題）
- 基礎練習：將 balance 與 history 的更新拆開與綁定，觀察測試結果差異。  
- 進階練習：改寫為細粒度鎖（不同帳號不同鎖）。  
- 專案練習：實作一個可切換「鎖策略」的帳務模組（NoLock/Lock），附壓測報表。

Assessment Criteria（評估標準）
- 功能完整性（40%）：併發下金額與明細皆正確  
- 程式碼品質（30%）：臨界區最小化、命名清晰  
- 效能優化（20%）：鎖競爭控制在可接受範圍  
- 創新性（10%）：提供可切換鎖策略與監控指標


## Case #2: 無鎖並發的錯帳重現與定位（Repro & Diagnose）

### Problem Statement（問題陳述）
業務場景：同 Case #1，但刻意拿掉 lock，模擬真實專案中未加同步保護的樂觀作法。  
技術挑戰：在高併發下發生錯帳，但偶發、難以重現與定位。  
影響範圍：金額消失（約 20%），稽核不過，信任損失。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Read-Modify-Write 重疊導致 lost update。  
2. 多執行緒同時操作共享變數。  
3. 改寫覆蓋彼此結果，無保證順序。

深層原因：
- 架構層面：共享資料缺乏同步策略。  
- 技術層面：未使用 lock/原子操作。  
- 流程層面：無壓測、無不變量（Invariant）驗證。

### Solution Design（解決方案設計）
解決策略：建立可重現場景的最小實驗；透過比較 Expected vs Actual 和吞吐數據，將「快但錯」的風險顯性化，驅動修正。

實施步驟：
1. 移除 lock，保留測試流程  
- 實作細節：保留相同的 N、M。  
- 所需資源：同測試程式。  
- 預估時間：0.5 小時。

2. 比對結果並記錄吞吐  
- 實作細節：印出 PASS/FAIL、Expected/Actual、trans/sec。  
- 所需資源：Stopwatch。  
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public override decimal ExecTransaction(decimal transferAmount)
{
    // lock(_syncroot) 移除以重現問題
    _history.Add(new TransactionItem { Date = DateTime.Now, Amount = transferAmount });
    return _balance += transferAmount; // 沒有同步 => Lost update
}
```

實際案例：WithoutLockAccount 測試  
實作環境：.NET/C#  
實測數據：  
改善前（無鎖）：FAIL，Expected 20000，Actual 16774；2000000 trans/sec。  
改善後（加鎖）：見 Case #1。  
改善幅度：正確率由不穩定變為 100%，吞吐下降約 23%（視機器而定）。

Learning Points（學習要點）
核心知識點：
- 如何重現並定位競態條件  
- 正確性 vs 吞吐的取捨  
- 以不變量驗證正確性

技能要求：
- 必備技能：多執行緒基礎、測試設計  
- 進階技能：效能監測與瓶頸分析

延伸思考：
- 若業務拒絕效能下降，還有其他方案（如分散式鎖、批次處理、事件溯源）嗎？  
- 在不同 CPU/核心數會否更嚴重？

Practice Exercise（練習題）
- 基礎練習：調整執行緒數與迴圈次數，觀察錯帳比例變化。  
- 進階練習：在無鎖情況加入 Thread.Sleep 以增加交錯概率，加深重現。  
- 專案練習：撰寫自動化腳本對比不同鎖策略的 PASS/FAIL 與 tps。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能穩定重現問題  
- 程式碼品質（30%）：測試可重複且參數化  
- 效能優化（20%）：提供吞吐觀測  
- 創新性（10%）：呈現錯帳占比等指標


## Case #3: 以單元測試風格的並發驗證（金錢守恆）

### Problem Statement（問題陳述）
業務場景：任何支付/儲值/遊戲幣系統都需遵守金錢守恆：封閉系統內不可憑空多/少錢。  
技術挑戰：如何快速驗證引擎在並發下仍滿足「N×M×1.0」的期望值。  
影響範圍：錯帳會導致對帳失敗、客訴、法遵風險。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 實務缺少可自動化的正確性驗證。  
2. 僅做靜態邏輯測試，未覆蓋併發場景。  
3. 無效能與正確性的統一檢視。

深層原因：
- 架構層面：缺少「不變量」導向的測試設計。  
- 技術層面：忽略高併發下的非決定性。  
- 流程層面：CI 未納入併發測試。

### Solution Design（解決方案設計）
解決策略：用 Console 取代測試框架快速構建壓測式單元測試，併發執行交易，再以 Expected vs Actual 比對並輸出 tps。

實施步驟：
1. 撰寫多執行緒測試器  
- 實作細節：可參數化 concurrent_threads、repeat_count。  
- 所需資源：C# Thread、Stopwatch。  
- 預估時間：1 小時。

2. 驗證輸出並納入 CI  
- 實作細節：PASS/FAIL、Expected/Actual、trans/sec。  
- 所需資源：CI Job。  
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
long concurrent_threads = 3, repeat_count = 1000;
decimal origin_balance = bank.GetBalance();
var threads = new List<Thread>();
for (int i = 0; i < concurrent_threads; i++)
{
    var t = new Thread(() => {
        for (int j = 0; j < repeat_count; j++) bank.ExecTransaction(1);
    });
    threads.Add(t);
}
var timer = Stopwatch.StartNew();
threads.ForEach(t => t.Start());
threads.ForEach(t => t.Join());
var expected = origin_balance + concurrent_threads * repeat_count;
var actual = bank.GetBalance();
Console.WriteLine($"Result: {(expected==actual?"PASS":"FAIL")}, " +
                  $"Expected={expected}, Actual={actual}, " +
                  $"Perf={concurrent_threads*repeat_count*1000/timer.ElapsedMilliseconds} tps");
```

實際案例：同文中 3 種實作的測試皆用此流程。  
實作環境：.NET/C# Console。  
實測數據（樣例）：  
- Lock：PASS，~1,538,461 tps  
- NoLock：FAIL，~2,000,000 tps（約 20% 金額遺失）  
- SQL Tx：PASS，~4,294 tps  
- Distributed Lock：PASS，~490 tps

Learning Points（學習要點）
核心知識點：
- 不變量（Invariant）導向測試  
- 併發測試與效能指標輸出  
- 正確性與吞吐的共視化

技能要求：
- 必備技能：多執行緒、基準測試  
- 進階技能：將此測試併入 CI/CD

延伸思考：
- 將測試擴展為多帳號、多貨幣的場景  
- 加入隨機延遲，模擬真實抖動

Practice Exercise（練習題）
- 基礎練習：把測試抽象成可重用的 Test Fixture。  
- 進階練習：加入不同鎖策略與資料層，產生對比報表。  
- 專案練習：將壓測與正確性測試接入 CI，生成趨勢圖。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能檢出錯帳  
- 程式碼品質（30%）：結構清晰、可重用  
- 效能優化（20%）：最小化測試開銷  
- 創新性（10%）：自動化報表


## Case #4: 同步保護兩步寫操作（餘額與交易明細原子性）

### Problem Statement（問題陳述）
業務場景：每次交易需同時寫入交易表（history）與更新帳戶餘額（balance）。  
技術挑戰：兩步驟必須被視為單一原子交易，任一步失敗都會造成不一致。  
影響範圍：交易明細與餘額不對賬，可能引發稽核問題。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多步寫入未被綁在同一臨界區或交易範圍中。  
2. 在競態條件下，history 與 balance 可能分離。  
3. 無隔離導致交錯執行。

深層原因：
- 架構層面：未定義不可分割的「寫模型」。  
- 技術層面：缺少 lock 或 DB 交易。  
- 流程層面：缺少對兩表一致性驗證。

### Solution Design（解決方案設計）
解決策略：在單機方案中，將兩步寫在同一 lock 區塊；在 DB 方案中，用單一 DB 交易包起 insert + update。

實施步驟：
1. 單機：兩步寫入置於 lock 內  
- 實作細節：見 Case #1 程式碼。  
- 所需資源：C# lock。  
- 預估時間：0.5 小時。

2. DB：以 BEGIN TRAN 包覆兩步寫入  
- 實作細節：見 Case #5 程式碼。  
- 所需資源：SQL Server。  
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 單機：在同一 lock 中執行
lock(_syncroot) {
    _history.Add(new TransactionItem{ Date=DateTime.Now, Amount=transferAmount });
    _balance += transferAmount;
}
```

實際案例：單機與 DB 交易兩路皆 PASS，兩表一致。  
實作環境：.NET/C#，或 SQL Server。  
實測數據：見 Case #1、#5。

Learning Points（學習要點）
核心知識點：
- 原子性不僅是單表寫入，還包含跨結構的一致性  
- 臨界區與 DB Transaction 的對應關係

技能要求：
- 必備技能：臨界區/交易設計  
- 進階技能：將一致性驗證納入測試

延伸思考：
- 若 history 寫入失敗如何補償？  
- 需要將寫入設計為「先寫事件」再 materialize balance 嗎？

Practice Exercise（練習題）
- 基礎練習：在 lock 區塊中刻意插入延遲，觀察是否仍一致。  
- 進階練習：DB 端模擬 deadlock，調整交易隔離等級。  
- 專案練習：加入事件溯源（Event Sourcing）作為替代設計。

Assessment Criteria（評估標準）
- 功能完整性（40%）：兩表一致  
- 程式碼品質（30%）：邏輯清楚、錯誤處理妥當  
- 效能優化（20%）：臨界區足夠小  
- 創新性（10%）：補償或溯源方案


## Case #5: 使用 SQL Server 交易（ACID 落地）

### Problem Statement（問題陳述）
業務場景：10+ Hosts 的後端服務共用 RDBMS 儲存帳務資料，需保證每筆交易 ACID。  
技術挑戰：在多進程/多主機下維持一致性與串接性。  
影響範圍：交易錯帳、庫存/結算對不攏。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多語句更新未置於 DB 交易中。  
2. 依賴應用層同步在多主機下不可靠。  
3. 忽略 DBMS 提供的併發控制機制。

深層原因：
- 架構層面：將一致性責任錯置於 App，而非 DBMS。  
- 技術層面：未使用 transaction/隔離級別。  
- 流程層面：未在測試中比對交易結果。

### Solution Design（解決方案設計）
解決策略：用 DB 內交易包覆「插交易明細 + 更新餘額 + 查餘額」，以 ACID 管控一致性，應用僅提交意圖。

實施步驟：
1. 撰寫交易 SQL 並以 Dapper 執行  
- 實作細節：BEGIN TRAN…COMMIT。  
- 所需資源：SQL Server，Dapper。  
- 預估時間：1 小時。

2. 驗證效能與正確性  
- 實作細節：沿用 Case #3 測試。  
- 所需資源：Console 測試器。  
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
public override decimal ExecTransaction(decimal transferAmount)
{
    return GetSqlConn().ExecuteScalar<decimal>(@"
begin tran
insert [transactions] ([userid], [amount]) values (@name, @transfer);
update [accounts] set [balance] = [balance] + @transfer where userid = @name;
select [balance] from [accounts] where userid = @name;
commit",
    new { name = this.Name, transfer = transferAmount });
}
```

實際案例：TransactionAccount PASS。  
實作環境：SQL Server LocalDB + Dapper。  
實測數據：Expected=176000, Actual=176000；~4,294 trans/sec。

Learning Points（學習要點）
核心知識點：
- ACID 與交易邊界  
- Dapper 執行交易 SQL  
- DBMS 的併發控制

技能要求：
- 必備技能：T-SQL、交易控制  
- 進階技能：隔離級別與死鎖處理

延伸思考：
- 如何在多資料庫、多分片中維持一致性？  
- 交易長度與鎖競爭的平衡

Practice Exercise（練習題）
- 基礎練習：改用 TransactionScope 實作。  
- 進階練習：對照不同隔離級別的效能與一致性。  
- 專案練習：設計含分片的帳務服務，衡量 DB 負載。

Assessment Criteria（評估標準）
- 功能完整性（40%）：交易正確  
- 程式碼品質（30%）：SQL 清晰、參數化  
- 效能優化（20%）：控制交易時間  
- 創新性（10%）：隔離級別選擇與監控


## Case #6: 帳務資料表設計（accounts + transactions）

### Problem Statement（問題陳述）
業務場景：需要同時保有「即時餘額」與「交易稽核明細」。  
技術挑戰：資料模型需支持交易原子性、查詢效能、稽核可追溯。  
影響範圍：報表不一致、查詢慢、對帳困難。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單表難以同時兼顧聚合值與明細稽核。  
2. 缺少 PK/Index 設計影響效能。  
3. 未在交易內更新兩表導致不一致。

深層原因：
- 架構層面：資料模型未對齊讀寫模式。  
- 技術層面：缺少交易控制與索引規劃。  
- 流程層面：無 schema 驗證與壓測。

### Solution Design（解決方案設計）
解決策略：兩表模型：accounts（UserId, Balance）為聚合視圖，transactions（id, userid, time, amount）為事件明細；所有更新由交易包起。

實施步驟：
1. 建立兩表與 PK  
- 實作細節：UserId 為 accounts PK，transactions 以 GUID 為 PK。  
- 所需資源：SQL Server。  
- 預估時間：0.5 小時。

2. 在 DB 交易內更新  
- 實作細節：Case #5 的 SQL。  
- 所需資源：同上。  
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```sql
CREATE TABLE [dbo].[accounts] (
    [UserId] NVARCHAR(50) NOT NULL PRIMARY KEY,
    [Balance] MONEY NOT NULL
);
CREATE TABLE [dbo].[transactions] (
    [id] UNIQUEIDENTIFIER NOT NULL DEFAULT newid() PRIMARY KEY,
    [userid] NVARCHAR(50) NOT NULL,
    [time] DATETIME NOT NULL DEFAULT getdate(),
    [amount] MONEY NOT NULL
);
```

實際案例：搭配 Case #5 交易 SQL，帳務正確。  
實作環境：SQL Server。  
實測數據：PASS（同 Case #5）。

Learning Points（學習要點）
核心知識點：
- 聚合值表 + 事件明細表  
- 原子更新與稽核可追溯  
- PK/索引的最小設計

技能要求：
- 必備技能：基本資料建模  
- 進階技能：分區、索引調優

延伸思考：
- 大表下 transactions 的分區策略  
- 歷史歸檔與查詢效能

Practice Exercise（練習題）
- 基礎練習：補上合理索引並測試查詢效能。  
- 進階練習：依 UserId 分區並評估效能。  
- 專案練習：建立對帳報表從明細重建餘額並驗證一致性。

Assessment Criteria（評估標準）
- 功能完整性（40%）：模型可支持正確更新與查詢  
- 程式碼品質（30%）：Schema 清晰、約束合理  
- 效能優化（20%）：查詢與更新無明顯瓶頸  
- 創新性（10%）：分區/索引策略


## Case #7: 單一資料庫交易邊界的伸縮性限制

### Problem Statement（問題陳述）
業務場景：服務持續擴張，單一 RDBMS 成為連線與交易吞吐瓶頸。  
技術挑戰：交易強一致性受限於單庫邊界，不易水平擴展。  
影響範圍：高延遲、阻塞、無法承載更多實例。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 所有交易集中於同一 DB 實例，連線/鎖競爭上升。  
2. 跨庫交易難度高（兩階段提交成本）。  
3. 資料模型高關聯度阻礙分片。

深層原因：
- 架構層面：CA（ACID）導向的集中式設計。  
- 技術層面：未實施分片/分區/拆庫。  
- 流程層面：未預先設計 scale-out 路徑。

### Solution Design（解決方案設計）
解決策略：在可控風險下將一致性的一部分移至應用層（如分散式鎖），或對資料層進行分片；依業務選擇 RDBMS 與 NoSQL 混合。

實施步驟：
1. 量測現況與瓶頸  
- 實作細節：以 Case #3 測試，記錄 tps。  
- 所需資源：壓測工具。  
- 預估時間：1-2 天。

2. 設計 Scale-Out 策略  
- 實作細節：帳號分片、跨庫路由、或應用層鎖（見 Case #8）。  
- 所需資源：路由層、鎖服務。  
- 預估時間：1-2 週。

關鍵程式碼/設定：
```text
基準數據（文中）：
- SQL Transaction: ~4,294 tps（單庫）
- Distributed Lock + Mongo: ~490 tps（單環境驗證，易水平擴展）
```

實際案例：本文展示將一致性搬到應用層（Case #8）。  
實作環境：SQL Server、Mongo、Redis。  
實測數據：如上。

Learning Points（學習要點）
核心知識點：
- ACID 與 BASE/CAP 取捨  
- 單庫邊界與擴展策略

技能要求：
- 必備技能：資料庫擴展基礎  
- 進階技能：應用層一致性設計

延伸思考：
- 哪些交易必須強一致？哪些可最終一致？  
- 交易分區鍵如何選擇（如 UserId）？

Practice Exercise（練習題）
- 基礎練習：以帳號做水平分片，驗證路由正確性。  
- 進階練習：加入跨分片轉帳，設計補償流程。  
- 專案練習：評估 SQL Tx 與應用層鎖方案在不同負載的 tps/cost。

Assessment Criteria（評估標準）
- 功能完整性（40%）：在分片或應用鎖下仍正確  
- 程式碼品質（30%）：分層清晰、耦合低  
- 效能優化（20%）：吞吐與延遲可量測  
- 創新性（10%）：混合存儲策略


## Case #8: 以 Redis RedLock 保護 MongoDB 更新（分散式鎖）

### Problem Statement（問題陳述）
業務場景：100+ 服務實例，資料層使用不支援交易的 MongoDB（pre-4.0），需保證轉帳正確性。  
技術挑戰：跨實例的臨界區，需要分散式鎖以避免 lost update。  
影響範圍：全域錯帳風險、無法對賬。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. NoSQL 缺乏多語句 ACID。  
2. 多實例同時更新同一使用者餘額。  
3. 無全域同步機制。

深層原因：
- 架構層面：分散式環境缺臨界區抽象。  
- 技術層面：不了解分散式鎖定演算法（如 RedLock）。  
- 流程層面：缺跨程序壓測驗證。

### Solution Design（解決方案設計）
解決策略：採用 Redis RedLock 分散式鎖，以「帳戶為鎖資源」取得租約（expiry/wait/retry），在鎖內執行 upsert 與新增交易明細，完成後釋放鎖。

實施步驟：
1. 連線 Redis 與 Mongo  
- 實作細節：RedLockFactory 建鎖、Mongo 連線與集合。  
- 所需資源：Redis、Mongo。  
- 預估時間：1 天。

2. 在鎖內執行更新  
- 實作細節：read -> insert/update -> insert transaction，最後回傳 balance。  
- 所需資源：RedLock.net。  
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
var resource = $"account-transaction::{this.Name}";
var expiry = TimeSpan.FromSeconds(5);
var wait = TimeSpan.FromSeconds(5);
var retry = TimeSpan.FromMilliseconds(50);

using (var redLock = _redlock.CreateLock(resource, expiry, wait, retry))
{
    if (!redLock.IsAcquired) throw new Exception("Lock not acquired");
    var acc = _accounts.FindOne(Query.EQ("Name", this.Name));
    if (acc == null) {
        _accounts.Insert(new AccountMongoEntity { _id=ObjectId.GenerateNewId(), Name=this.Name, Balance=transferAmount });
    } else {
        acc.Balance += transferAmount; _accounts.Save(acc);
    }
    _transactions.Insert(new TransactionMongoEntity {
        _id=ObjectId.GenerateNewId(), Date=DateTime.Now, Amount=transferAmount
    });
}
```

實際案例：DistributedLockAccount PASS。  
實作環境：C#、Mongo、Redis（RedLock.net）。  
實測數據：Expected=33574, Actual=33574；~490 trans/sec。多程序壓測 200,000 筆交易正確（見 Case #10）。

Learning Points（學習要點）
核心知識點：
- 分散式鎖與租約（TTL、Wait、Retry）  
- 在鎖內的最小更新區域  
- NoSQL + 應用層一致性

技能要求：
- 必備技能：Redis、Mongo 基本操作  
- 進階技能：分散式協定與鎖算法

延伸思考：
- RedLock 的容錯設計與多 Redis 節點策略  
- 鎖失效與補償策略

Practice Exercise（練習題）
- 基礎練習：調整 expiry/wait/retry，觀察吞吐與成功率。  
- 進階練習：模擬鎖超時與重試。  
- 專案練習：以 k8s 部署多實例，觀察在 Redis 雙活下的行為。

Assessment Criteria（評估標準）
- 功能完整性（40%）：跨實例仍無錯帳  
- 程式碼品質（30%）：鎖內邏輯最小且防呆  
- 效能優化（20%）：鎖參數調優  
- 創新性（10%）：多節點容錯設計


## Case #9: 分散式鎖的租約與重試策略（expiry/wait/retry）

### Problem Statement（問題陳述）
業務場景：高併發下，鎖競爭激烈、進程可能崩潰，須避免永久鎖死或飢餓。  
技術挑戰：確保鎖可回收、可重試且公平。  
影響範圍：系統停頓、吞吐下滑、交易積壓。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 鎖未設 TTL，崩潰後無法釋放。  
2. 沒有重試/等待策略導致飢餓或大量失敗。  
3. 鎖競爭未被觀測。

深層原因：
- 架構層面：忽略鎖生命週期管理。  
- 技術層面：對 RedLock 參數缺少理解。  
- 流程層面：缺少壓測與參數調優流程。

### Solution Design（解決方案設計）
解決策略：設定合理的 expiry（租約到期自動釋放）、wait（等待鎖時間）與 retry（重試間隔），以在高競爭下保持前進性與穩定性；在壓測下調優。

實施步驟：
1. 設定鎖參數  
- 實作細節：expiry=5s, wait=5s, retry=50ms（文中配置）。  
- 所需資源：RedLock.net。  
- 預估時間：0.5 小時。

2. 壓測與觀測  
- 實作細節：Case #10 的多程序壓測；紀錄總耗時/失敗率。  
- 所需資源：測試器、監控。  
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
var expiry = TimeSpan.FromSeconds(5);
var wait = TimeSpan.FromSeconds(5);
var retry = TimeSpan.FromMilliseconds(50);
using (var redLock = _redlock.CreateLock(resource, expiry, wait, retry))
{
    if (!redLock.IsAcquired) throw new Exception();
    // 關鍵更新...
}
```

實際案例：200,000 筆交易約 7 分鐘完成，無死鎖、無錯帳（見 Case #10）。  
實作環境：C#、Redis（RedLock）。  
實測數據：穩定完成；正確率 100%。

Learning Points（學習要點）
核心知識點：
- 鎖租約（Lease/TTL）  
- 重試與退避策略  
- 壓測下調參

技能要求：
- 必備技能：併發控制、基本監控  
- 進階技能：以指標驅動配置（成功率/延遲/飽和）

延伸思考：
- 如何動態調整鎖參數以適應負載變化？  
- 是否需要鎖競爭率/等待時間的監控面板？

Practice Exercise（練習題）
- 基礎練習：在不同 retry 間隔下比較完成時間。  
- 進階練習：引入抖動（jitter）以降低同步放大。  
- 專案練習：加入監控與告警，超過某等待時長告警。

Assessment Criteria（評估標準）
- 功能完整性（40%）：無死鎖、可回收  
- 程式碼品質（30%）：防呆可觀測  
- 效能優化（20%）：成功率/等待時間可控  
- 創新性（10%）：自適應參數


## Case #10: 跨程序壓測驗證分散式鎖（10 個 process × 20 線程）

### Problem Statement（問題陳述）
業務場景：為接近微服務實際情況，以多進程並發驗證分散式鎖與 NoSQL 更新正確性。  
技術挑戰：如何快速啟動多個程序、產生並發負載、驗證最終餘額。  
影響範圍：若不驗證，多實例部署可能帶來隱性錯帳。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單進程測試說服力不足。  
2. 未模擬跨程序/跨節點的併發。  
3. 無最終狀態的外部驗證。

深層原因：
- 架構層面：缺壓測設計與自動化腳本。  
- 技術層面：不熟多程序併發產生器。  
- 流程層面：缺少驗收步驟。

### Solution Design（解決方案設計）
解決策略：編譯可執行檔，批次啟動 10 個 Process，各自再開 20 threads；執行後以 Mongo GUI 比對測試前後餘額差（應等於交易數）。

實施步驟：
1. 準備執行檔與啟動腳本  
- 實作細節：批次檔同時啟動 10 個進程。  
- 所需資源：Windows 批次或 PowerShell。  
- 預估時間：1 小時。

2. 前後狀態比對  
- 實作細節：用 Mongo GUI 或查詢比對餘額。  
- 所需資源：Mongo 工具。  
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```text
測試流程：
1) 讀取 andrew 帳戶初始 Balance（例：33,574）
2) 啟動 10 個進程 × 每進程 20 threads × 每執行緒多次存入
3) 完成後再查 Balance（例：233,574）
4) 差值 = 寫入總次數（約 200,000）×1.0 元
```

實際案例：多進程壓測約 7 分鐘完成，最終餘額與期望一致。  
實作環境：Windows、C#、Mongo、Redis。  
實測數據：200,000 筆交易，正確率 100%，約 7 分鐘完成。

Learning Points（學習要點）
核心知識點：
- 跨程序併發負載產生  
- 測前/測後狀態比對  
- 黑箱驗證

技能要求：
- 必備技能：腳本與自動化  
- 進階技能：壓測與報表

延伸思考：
- 可否用容器啟動多副本壓測？  
- 如何引入延遲與錯誤注入？

Practice Exercise（練習題）
- 基礎練習：將進程數調為 5/20 比較完成時間。  
- 進階練習：在壓測期間重啟部分進程，觀察鎖行為。  
- 專案練習：以 k6/JMeter 產生 API 層負載，串接後端鎖方案。

Assessment Criteria（評估標準）
- 功能完整性（40%）：最終餘額正確  
- 程式碼品質（30%）：腳本穩定可重複  
- 效能優化（20%）：負載與時間可量測  
- 創新性（10%）：容器化壓測


## Case #11: 用 Docker 快速建立 Redis 與 Mongo 測試環境

### Problem Statement（問題陳述）
業務場景：需要快速啟動 Redis 與 Mongo 以進行分散式鎖 + NoSQL POC。  
技術挑戰：降低安裝成本，避免影響本機環境。  
影響範圍：環境準備慢造成驗證時程延宕。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 手動安裝/設定耗時。  
2. 版本不一致易出錯。  
3. 本機污染風險。

深層原因：
- 架構層面：缺少可復現的基礎設施即程式碼。  
- 技術層面：未善用容器。  
- 流程層面：環境管理未自動化。

### Solution Design（解決方案設計）
解決策略：以 Docker 啟動 Redis/Mongo，--rm 臨時容器，port mapping 直連；用最少命令完成環境就緒，聚焦應用驗證。

實施步驟：
1. 啟動 Redis 與 Mongo 容器  
- 實作細節：兩行 docker run。  
- 所需資源：Docker Desktop（Windows 容器）。  
- 預估時間：0.5 小時。

2. 連線測試  
- 實作細節：App 連接字串指向 localhost 對應埠。  
- 所需資源：App 設定。  
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```shell
docker run --rm -d -p 6379:6379 alexellisio/redis-windows:3.2
docker run --rm -d --name mongo -p 27017:27017 mongo:3.4-windowsservercore
```

實際案例：文中以此環境完成分散式鎖 POC 與壓測。  
實作環境：Windows 容器。  
實測數據：2 條命令完成環境；後續壓測 200,000 筆交易成功。

Learning Points（學習要點）
核心知識點：
- 容器快速啟動依賴服務  
- 臨時容器避免污染  
- 可復現環境

技能要求：
- 必備技能：Docker 基礎  
- 進階技能：容器網路與資料卷

延伸思考：
- 切換為 Linux 容器與官方 Redis 映像是否更穩定？  
- 以 docker-compose 管控多服務？

Practice Exercise（練習題）
- 基礎練習：改以 docker-compose.yml 啟動兩服務。  
- 進階練習：加上 Redis 密碼與 Mongo 資料卷。  
- 專案練習：建立一鍵啟停與健康檢查腳本。

Assessment Criteria（評估標準）
- 功能完整性（40%）：環境可用  
- 程式碼品質（30%）：腳本清晰可重用  
- 效能優化（20%）：啟動時間與資源佔用可控  
- 創新性（10%）：引入 IaC 概念


## Case #12: 以成熟套件取代自研鎖原語（RedLock.net）

### Problem Statement（問題陳述）
業務場景：團隊需在短期內上線分散式鎖保證交易正確，但自研鎖風險高。  
技術挑戰：自行實作需掌握 CAS/Compare-And-Swap 與分散式一致性細節。  
影響範圍：自研錯誤導致全域錯帳或死鎖。  
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏不可分割原語支撐（CAS）。  
2. 未考慮鎖租約、時鐘偏移、節點故障。  
3. 測試覆蓋不足。

深層原因：
- 架構層面：低估分散式正確性的難度。  
- 技術層面：未遵循既有演算法與實踐（如 Redis 官方建議）。  
- 對流程層面：未引入成熟套件與社群驗證。

### Solution Design（解決方案設計）
解決策略：採用 RedLock.net 實踐 Redis 官方分散式鎖設計，提供 API（CreateLock）並內建租約/等待/重試，降低自研風險。

實施步驟：
1. 引入 RedLock.net  
- 實作細節：RedLockFactory.Create(endpoints)。  
- 所需資源：NuGet、Redis。  
- 預估時間：0.5 天。

2. 以最小鎖區執行關鍵更新  
- 實作細節：與 Case #8 類似。  
- 所需資源：App 代碼。  
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
_redlock = RedLockFactory.Create(new List<RedLockEndPoint> {
    new DnsEndPoint("172.18.254.68", 6379)
});
using (var redLock = _redlock.CreateLock(resource, expiry, wait, retry))
{
    if (!redLock.IsAcquired) throw new Exception();
    // 關鍵區塊...
}
```

實際案例：在此基礎上通過 200,000 筆交易壓測，無錯帳（見 Case #10）。  
實作環境：C#、Redis。  
實測數據：PASS；~490 tps。

Learning Points（學習要點）
核心知識點：
- 為何不要自研鎖原語  
- 演算法與實作選型  
- 用 API 抽象臨界區

技能要求：
- 必備技能：NuGet 管理、Redis  
- 進階技能：閱讀演算法白皮書與實作對照

延伸思考：
- 需要多 Redis 節點來提高容錯嗎？  
- 何時需要替換為 ZooKeeper/etcd 鎖？

Practice Exercise（練習題）
- 基礎練習：在本地 Redis 下改寫為 RedLock.net。  
- 進階練習：切換到多 endpoint，模擬節點故障。  
- 專案練習：封裝鎖 API，提供統一觀測。

Assessment Criteria（評估標準）
- 功能完整性（40%）：鎖可靠可用  
- 程式碼品質（30%）：封裝良好  
- 效能優化（20%）：鎖競爭可觀測  
- 創新性（10%）：容錯架構


## Case #13: 正確性與效能的取捨基準（Lock vs NoLock vs SQL Tx vs DistLock）

### Problem Statement（問題陳述）
業務場景：需要在不同技術選擇間平衡正確性與效能。  
技術挑戰：如何用數據對比各方案的吞吐與正確性。  
影響範圍：錯誤決策導致過早優化或風險暴露。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少量化基準。  
2. 以主觀經驗選型。  
3. 測試場景不一致。

深層原因：
- 架構層面：無 SLO 對齊的指標。  
- 技術層面：未系統化壓測。  
- 流程層面：缺標準測試套件。

### Solution Design（解決方案設計）
解決策略：用同一測試器（Case #3）在同樣參數下量測 4 方案，對比正確性與 tps，做為選型依據。

實施步驟：
1. 建立標準測試流程  
- 實作細節：固定 N、M、硬體。  
- 所需資源：測試器、報表。  
- 預估時間：1 天。

2. 對比與決策  
- 實作細節：以正確性為前提，評估 tps 與開發/維運成本。  
- 所需資源：決策會議。  
- 預估時間：0.5 天。

關鍵程式碼/設定：
```text
對比（文中樣例）：
- NoLock: FAIL, ~2,000,000 tps
- Lock(單機): PASS, ~1,538,461 tps
- SQL Tx(單庫): PASS, ~4,294 tps
- DistLock+Mongo: PASS, ~490 tps（可水平擴展）
```

實際案例：以此數據作為不同規模（1/10+/100+ hosts）對應策略。  
實作環境：同文。  
實測數據：如上。

Learning Points（學習要點）
核心知識點：
- 用數據選型  
- 正確性底線 + 效能上限  
- 適配規模的策略

技能要求：
- 必備技能：壓測方法  
- 進階技能：TCO/風險量化

延伸思考：
- 在更大規模下 DistLock 方案如何橫向擴展以提升 tps？  
- SQL Tx 透過分片能否提升整體吞吐？

Practice Exercise（練習題）
- 基礎練習：重現四種方案的測試數據。  
- 進階練習：引入不同硬體與參數，產生雷達圖。  
- 專案練習：建立自動化基準倉庫與儀表板。

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試可重複  
- 程式碼品質（30%）：測試與報表清晰  
- 效能優化（20%）：能比較與分析  
- 創新性（10%）：視覺化呈現


## Case #14: 取得鎖失敗時的 Fail-Fast 策略

### Problem Statement（問題陳述）
業務場景：分散式鎖在高競爭場景下可能取得失敗。  
技術挑戰：若未處理即繼續執行，會造成並發寫入衝突。  
影響範圍：錯帳、數據污染。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 鎖取得結果未檢查。  
2. 失敗時仍繼續更新。  
3. 缺乏異常處理與重試策略。

深層原因：
- 架構層面：錯誤處理策略缺失。  
- 技術層面：未遵循鎖 API 的契約。  
- 流程層面：未在測試中覆蓋失敗分支。

### Solution Design（解決方案設計）
解決策略：嚴格檢查 redLock.IsAcquired，失敗即拋出異常（或回傳可重試狀態），不進入臨界區；將錯誤納入監控。

實施步驟：
1. 加入取得鎖檢查  
- 實作細節：if (!IsAcquired) throw。  
- 所需資源：既有代碼。  
- 預估時間：0.2 小時。

2. 監控與重試  
- 實作細節：紀錄失敗率，必要時重試/退避。  
- 所需資源：監控系統。  
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
using (var redLock = _redlock.CreateLock(resource, expiry, wait, retry))
{
    if (!redLock.IsAcquired) throw new Exception("Lock acquisition failed");
    // 僅在取得鎖後執行關鍵更新
}
```

實際案例：文中即採 Fail-Fast，壓測無錯帳。  
實作環境：C#、Redis。  
實測數據：正確率 100%。

Learning Points（學習要點）
核心知識點：
- Fail-Fast 思維  
- 異常即早回報，避免隱性污染  
- 可重試與退避

技能要求：
- 必備技能：異常處理  
- 進階技能：重試策略設計

延伸思考：
- 是否需要降級（排隊/稍後再試）？  
- 未取得鎖是否記錄審計事件？

Practice Exercise（練習題）
- 基礎練習：模擬鎖高競爭，記錄失敗率。  
- 進階練習：實作重試與退避策略。  
- 專案練習：在 API 層設計標準錯誤碼與告警。

Assessment Criteria（評估標準）
- 功能完整性（40%）：失敗不進入臨界區  
- 程式碼品質（30%）：錯誤處理清晰  
- 效能優化（20%）：重試不致雪崩  
- 創新性（10%）：降級策略


## Case #15: 帳戶粒度的鎖資源命名（避免全域阻塞）

### Problem Statement（問題陳述）
業務場景：多帳戶同時交易時，若採用全域鎖會造成整個系統序列化，吞吐驟降。  
技術挑戰：在保證單一帳戶內部一致性的前提下，盡可能提升系統併發。  
影響範圍：吞吐瓶頸、延遲上升。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 鎖資源命名過於粗糙（全域）。  
2. 不必要的跨帳戶阻塞。  
3. 無法利用獨立帳戶間的天然並行性。

深層原因：
- 架構層面：鎖粒度設計缺失。  
- 技術層面：未將業務鍵（UserId）映射為資源鍵。  
- 流程層面：未做並發下的粒度測試。

### Solution Design（解決方案設計）
解決策略：以帳戶名稱（UserId）作為鎖資源鍵，例如 "account-transaction::{UserId}"，確保僅對同一帳戶的交易互斥，不同帳戶可並行。

實施步驟：
1. 設計資源鍵命名規範  
- 實作細節：resource = $"account-transaction::{Name}"。  
- 所需資源：應用程式碼。  
- 預估時間：0.2 小時。

2. 以案例驗證  
- 實作細節：（文中示範單帳戶），可延伸至多帳戶壓測。  
- 所需資源：測試器。  
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
var resource = $"account-transaction::{this.Name}"; // 鎖粒度=帳戶
using (var redLock = _redlock.CreateLock(resource, expiry, wait, retry))
{
    // 只互斥同帳戶，不阻塞其他帳戶交易
}
```

實際案例：文中以單帳戶展示；此命名策略為擴展多帳戶併發的基礎。  
實作環境：C#、Redis。  
實測數據：單帳戶壓測正確；多帳戶時理論上可並行提升吞吐（建議自行壓測）。

Learning Points（學習要點）
核心知識點：
- 鎖粒度設計  
- 資源鍵與業務鍵映射  
- 併發與一致性的平衡

技能要求：
- 必備技能：鍵設計、命名規範  
- 進階技能：基於鍵的分片與路由

延伸思考：
- 交易跨帳戶（轉帳）需要雙鎖或順序鎖策略如何處理？  
- 熱點帳戶（hot keys）如何緩解？

Practice Exercise（練習題）
- 基礎練習：設計多帳戶壓測腳本，觀察吞吐提升。  
- 進階練習：設計跨帳戶轉帳的雙鎖順序（避免死鎖）。  
- 專案練習：為熱點帳戶加入排隊或令牌桶。

Assessment Criteria（評估標準）
- 功能完整性（40%）：鎖僅作用於同帳戶  
- 程式碼品質（30%）：命名清晰一致  
- 效能優化（20%）：多帳戶吞吐提升  
- 創新性（10%）：熱點治理策略


-----------------------------
案例分類
-----------------------------

1) 按難度分類
- 入門級（適合初學者）
  - Case 1（單機 lock）
  - Case 2（無鎖重現）
  - Case 3（並發驗證）
  - Case 11（Docker 環境）
- 中級（需要一定基礎）
  - Case 4（兩步寫原子性）
  - Case 5（SQL 交易）
  - Case 6（資料表設計）
  - Case 7（單庫邊界與擴展）
  - Case 9（鎖租約/重試）
  - Case 10（跨程序壓測）
  - Case 14（Fail-Fast）
  - Case 15（鎖粒度）
- 高級（需要深厚經驗）
  - Case 8（分散式鎖 + Mongo）
  - Case 12（用成熟套件取代自研）
  - Case 13（方案基準與選型）

2) 按技術領域分類
- 架構設計類：Case 6, 7, 12, 13, 15  
- 效能優化類：Case 1, 3, 9, 10, 13  
- 整合開發類：Case 5, 8, 11  
- 除錯診斷類：Case 2, 3, 14  
- 安全防護類（資料一致性）：Case 1, 4, 5, 8, 9, 15

3) 按學習目標分類
- 概念理解型：Case 1, 4, 5, 7, 13, 15  
- 技能練習型：Case 3, 10, 11, 14  
- 問題解決型：Case 2, 8, 9  
- 創新應用型：Case 6, 12

-----------------------------
案例關聯圖（學習路徑建議）
-----------------------------
- 建議先學：
  - Case 1（單機臨界區）→ Case 2（無鎖重現）：先理解正確性底線與競態。  
  - Case 3（並發驗證）：建立不變量思維與測試能力。

- 依賴關係：
  - Case 4（兩步寫原子性）依賴 Case 1/3 基礎。  
  - Case 5（SQL 交易）依賴 Case 4 對原子性理解。  
  - Case 6（資料表設計）依賴 Case 5 的交易語義。  
  - Case 7（單庫邊界）建立轉向分散式的動機。  
  - Case 8（分散式鎖）依賴 Case 7 的動機 + Case 1/4 的臨界區概念。  
  - Case 9（租約/重試）與 Case 14（Fail-Fast）是 Case 8 的健壯性補強。  
  - Case 10（跨程序壓測）驗證 Case 8/9/14 的落地。  
  - Case 11（Docker 環境）支撐 Case 8/10 的快速搭環境。  
  - Case 12（用成熟套件）是 Case 8 的工程化選型。  
  - Case 13（基準對比）整合 Case 1/5/8 的數據，支撐選型。  
  - Case 15（鎖粒度）優化 Case 8 的可擴展性。

- 完整學習路徑：
  1) 單機並發與驗證：Case 1 → Case 2 → Case 3 → Case 4  
  2) DB 交易與資料模型：Case 5 → Case 6 → Case 7  
  3) 分散式一致性與工程化：Case 11 → Case 8 → Case 9 → Case 14 → Case 10 → Case 12  
  4) 選型與優化：Case 13 → Case 15

完成此路徑後，可在從單機到 100+ 實例的環境中，穩健地保證「線上交易的正確性」，並具備以數據做選型與工程化落地的能力。