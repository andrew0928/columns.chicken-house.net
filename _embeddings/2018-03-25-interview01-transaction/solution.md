# 線上交易的正確性：從單機到微服務的三種解法

# 問題／解決方案 (Problem/Solution)

## Problem: 單機多執行緒下餘額計算錯誤  

**Problem**:  
在一台機器（一個 Process）內，用 N 個 thread 併發地對同一個 `Account` 物件做存款 (`ExecTransaction(1)`)。理論上帳戶餘額應等於 `N * M * 1`，但實際跑完後金額少了好幾成，無法保證「金錢守恆」。

**Root Cause**:  
1. Race Condition：複數執行緒同時執行「讀取 → 計算 → 寫回」流程，彼此覆蓋結果。  
2. 缺少 Critical Section：`_balance` 與 `_history` 更新不是原子操作，無序交錯導致遺失更新。

**Solution**:  
將「更新餘額＋寫入交易紀錄」包進 Critical Section。以 C# `lock(obj)` 或 `Interlocked` 確保同時間只有一條執行緒可進入，滿足 ACID 中的 Atomic 與 Isolation。  

```csharp
public override decimal ExecTransaction(decimal transferAmount)
{
    lock(_syncroot)
    {
        _history.Add(new TransactionItem{ Amount = transferAmount });
        return _balance += transferAmount;
    }
}
```

**Cases 1**:  
• 測試條件：3 threads × 1000 次存款（共 3000 元）  
• 結果：`PASS`，餘額正確；效能 ≈ 1.5M trans/sec  

**Cases 2** (未加鎖對照組):  
• 結果：`FAIL`，只剩 ~80% 金額；效能雖提升到 2M trans/sec，但正確性崩潰。  

---

## Problem: 多主機併發寫入同一 RDBMS 時的交易一致性  

**Problem**:  
服務擴充到 10+ Hosts，所有請求都寫同一個 SQL Server。若每一條 SQL 只完成「扣款」或「加款」其中一步，即會產生不一致餘額，甚至出現孤兒交易。

**Root Cause**:  
1. 應用層無法再用 in-process lock；互斥需交由集中式元件處理。  
2. 若在資料庫中將「寫入交易紀錄」與「更新餘額」拆成兩個 Statement，任何一條失敗都會破壞一致性。

**Solution**:  
利用 RDBMS 內建 Transaction 將多個 SQL 指令包在同一批次，DBMS 透過兩階段鎖、Redo/Undo log 滿足 ACID。以 Dapper 範例：

```csharp
using(var conn = GetSqlConn())
{
    conn.Execute(@"
      begin tran
        insert into transactions(userid, amount) values(@u, @amt);
        update accounts set balance = balance + @amt where userid = @u;
      commit",
      new {u = userId, amt = transferAmount});
}
```
RDBMS 代管鎖定與回滾，應用層僅需確保所有修改在同一 Transaction 內。

**Cases 1**:  
• 3 threads × 1000 次 → `PASS`，餘額精準。  
• 效能 ≈ 4 k trans/sec（瓶頸轉移到 DB 連線數與磁碟 IO）。  

**Cases 2**:  
• 若忘記 `BEGIN TRAN/COMMIT`，模擬網路閃斷/逾時時會留下「扣款成功、寫帳失敗」的殘局，被 DBA 回收。  

---

## Problem: 微服務 (100+ Instances) + NoSQL（無原生交易）環境下的金額錯亂  

**Problem**:  
系統再擴大，單一 RDBMS 已成瓶頸；改用 MongoDB（4.0 之前不支援跨文件交易）並部署 100+ 容器。併發寫入同一帳戶時，因 Lack of Transaction 造成金額計算錯誤。

**Root Cause**:  
1. NoSQL 無 Multi-Document Transaction。  
2. 多個服務節點同時更新同一筆文件，`read-modify-write` 仍會產生 Lost Update。  
3. 單機鎖與 DB 交易皆無法跨節點協調。

**Solution**:  
實作「分散式鎖」(Distributed Lock)；本例採 Redis + RedLock 演算法。流程：  
a. 服務先向 Redis 嘗試取得 `account-<userid>` 鎖（設定 TTL，避免死鎖）。  
b. 取得鎖後執行：  
   • 更新 Mongo `accounts.balance`  
   • 寫入 `transactions` 紀錄  
c. 完成後釋放鎖。若鎖取得失敗則重試／回傳錯誤。

```csharp
using(var redLock = redlockFactory.CreateLock(resource, expiry, wait, retry))
{
    if(!redLock.IsAcquired) throw new BusyException();
    var acc = accounts.FindOne(Query.EQ("Name", Name)) ?? new Account{Name=Name};
    acc.Balance += transferAmount;
    accounts.Save(acc);
    transactions.Insert(new Transaction{Amount = transferAmount});
}
```

**Cases 1**: 單機 3 threads × 1000 次  
• `PASS`，餘額正確；效能 ≈ 490 trans/sec (Redis 往返 + Mongo I/O)

**Cases 2**: 10 個 Process × 20 threads × 1000 次（總 200 000 筆）  
• 前後以 Mongo Shell 查詢餘額，金額精準增加 200 000。  
• 全程約 7 分鐘完成，證明 RedLock 能跨 10 個微服務實例維持一致性。

**Cases 3**: 故意殺掉持鎖 Process  
• Redis TTL 到期後鎖自動釋放，其餘節點可繼續處理，避免永久阻塞。  

---

以上三組方案說明了在不同規模、不同基礎設施（In-Memory / RDBMS / NoSQL）下，維持「交易正確性」必須解決的根本問題——Race Condition 與一致性，並示範了相對應的工程手段：  
• 單機 Critical Section  
• 集中式 ACID Transaction  
• 分散式鎖 (Redis/RedLock)  

讀者可依據自身系統規模、資料存取特性選擇合適的實施方式。