```markdown
# 架構面試題 #3 ‑  RDBMS 處理樹狀結構的技巧

# 問題／解決方案 (Problem/Solution)

> 本文的三種做法（Self-Join、固定 Path 欄位、Nested Set Model）其實都是在回應「如何用傳統 RDBMS 可靠、有效率地儲存並操作樹狀資料」這個核心痛點。以下依照每一種做法分別列出它所要解決的「問題 ➜ 根本原因 ➜ 解決方案 ➜ 實際效益」。

---

## Problem: Self-Join 結構在深層查詢與遞迴操作時效能低落

**Problem**:  
在僅以「上一層目錄 ID (Parent_Id)」來描述樹狀關係的結構下，  
‧ 需要遞迴搜尋 (ex: `dir /s …`) 時必須不斷 self-join。  
‧ 當不確定深度時，要嘛硬寫多層 join，要嘛依賴 DB 特定語法 (T-SQL CTE/Oracle CONNECT BY)。  
結果導致 SQL 難維護，又容易因遞迴而拖垮效能。

**Root Cause**:  
1. 關聯式資料模型天然只擅長「集合運算」，不擅長「遞迴」。  
2. SQL 標準缺乏原生遞迴語法，必須靠 vendor 延伸功能；可攜性差。  
3. 每往下一層就多一次 Join，複雜度與 I/O 成線性或次方增長。

**Solution**:  
保留 Parent_Id 結構，必要時以「DB 端遞迴語法」(MS-SQL CTE 示範) 取代應用程式遞迴，讓  
‧ 單層查詢、Insert、Move、Delete 都非常直覺；  
‧ 複雜遞迴查詢仍能在純 SQL 中完成。  
Sample Code – 查出 *C:\Windows\System32* 下所有 *.ini* 檔：  

```sql
;WITH DIR_CTE(ID, NAME) AS(
    SELECT ID, NAME FROM DIRINFO WHERE PARENT_ID = @root
    UNION ALL
    SELECT D.ID, D.NAME FROM DIRINFO D JOIN DIR_CTE C ON D.PARENT_ID = C.ID
)
SELECT F.NAME ,F.SIZE
FROM DIR_CTE C JOIN FILEINFO F ON F.DIR_ID = C.ID
WHERE F.EXT = '.ini';
```

關鍵思考：把遞迴留在 DB 內部執行，以減少多趟 round-trip，但仍維持資料一致性與 ACID。

**Cases 1 – 單層列目錄**  
• 執行時間 0.279 s；Estimated Subtree Cost 0.516  
**Cases 2 – 遞迴列 *.ini***  
• 0.547 s (System32)；放大範圍 (*.dll*) → 8.138 s  
**Cases 3 – Move / Delete**  
• Move 0.026 s；Delete 整棵 22.536 s  

> 優點：結構最單純、異動（Insert/Move/Delete）最方便  
> 缺點：深層查詢效能劣，跨 DBMS 可攜性差

---

## Problem: 需要大幅提升遞迴查詢速度，但不重視階層動態變動

**Root Cause**:  
遞迴帶來的多次 Join 是效能瓶頸，若能「一次就定位」比對關鍵欄位就可消除遞迴開銷。

**Solution – 固定 Path 欄位 (方案 2)**:  
1. 事先在表上開 `ID01 … ID20` (或更高) 欄位，分別存放各階層的節點編號。  
2. 查詢時直接以「第 N 層欄位 = value」篩選；不需遞迴、不需 Join。  
3. 只做單一 UPDATE/INSERT 就能回應大多數搜尋。  

Sample – 取 *C:\Windows\System32* 全域 *.ini*：

```sql
SELECT F.NAME,F.SIZE
FROM FILEINFO F
JOIN DIRINFO D ON F.DIR_ID=D.ID
WHERE D.ID03 = 189039   -- system32
  AND F.EXT='.ini';
```

**為何可解決**  
‧ 將「多層條件」預降維到固定欄位 → 任一深度的比較都變成 O(1)。  
‧ 完全吃到 B-Tree Index 效能。  

**Cases 1 – 單層列目錄**  
• 0.157 s  
**Cases 2 – 遞迴 *.ini***  
• 0.407 s；*.dll* 查詢僅 0.067 s  
**Cases 3 – Move**  
• 0.758 s（需 20 欄位 shift right）  
**Cases 4 – 刪除整棵**  
• 20.305 s  

> 優點：搜尋速度 10× 提升，SQL 語法極簡  
> 缺點：  
> 1. 最大層級被欄位數限制，超過即需變更 Schema。  
> 2. 每次 Move/Insert 需同步「整列欄位」更新，維護成本極高。  
> 3. 動態 SQL 難避免，易埋 SQL Injection 風險。

---

## Problem: 同時要高速遞迴查詢、又要可彈性搬移且不限階層

**Root Cause**:  
固定 Path 欄位帶來維護地獄；Self-Join 又查不到效能。需要能在「查詢」與「異動維護」之間取得平衡的新索引策略。

**Solution – Nested Set Model (方案 3)**:  
1. 以 Depth-First Traversal 方式為每個節點標註 `(Left, Right)` 兩個整數。  
2. `Left < child.Left  AND  child.Right < Right` 即代表「被涵蓋」。  
3. 單純 `BETWEEN` 比對即可完成不限深度查詢；只需兩欄索引且層級無上限。  

Sample – 查 *C:\Windows* 下所有 *.dll*：

```sql
SELECT F.NAME,F.SIZE
FROM FILEINFO F
JOIN DIRINFO D ON D.ID = F.DIR_ID
WHERE F.EXT = '.dll'
  AND D.LEFT_INDEX BETWEEN 303068 AND 437609;   -- windows 範圍
```

4. Insert/Move/Delete 只需批次平移區段的 `(Left,Right)` 值：  
   • Insert：對右邊所有節點 `+2`；把兩個空洞留給新節點。  
   • Move：三步驟（搬到暫存區、收縮洞、搬回）。  

**為何可解決**  
‧ 查詢時永遠只做一次區間比對 + Index Seek → 接近最佳效能。  
‧ 不用固定層級欄位，深度無限制，Schema 不變。  
‧ 維護成本僅集中在「批次 Shift 數值」，可封裝於 Stored Procedure。  

**Cases 1 – 深層 *.dll* 查詢**  
• 0.546 s（僅慢方案 2 微量，遠優於方案 1 的 8.138 s）  
**Cases 2 – Move 整棵 (Users ➜ Backup)**  
• 0.550 s 完成（含三段 Update）  
**Cases 3 – 刪除整棵**  
• 9.158 s（為三方案中最快）  
**Cases 4 – 單層列目錄**  
• 2.5 min（若無 Depth/Parent 欄位需多步 NOT EXISTS 排除；若加上 Parent_Id 可降至與方案 1 相同的 0.2 s 等級）

> 優點：  
> • 查詢幾乎與方案 2 同速；可攜性高（只用標準 SQL）  
> • 任意深度、不受 Schema 影響  
> • Move/Delete 仍落在可接受範圍  
> 缺點：  
> • 需要在任何異動時同步維護 `(Left,Right)`，實作較抽象，需要良好封裝。  
> • 如果僅查「直屬子節點」且不加 Parent/Depth 欄位，語法較冗長。

---

# 結論

1. 若 **異動頻繁** 且 **層級不深** → Self-Join(方案1) 最直覺，但要忍受遞迴查詢慢 & Vendor lock-in。  
2. 若 **幾乎只查詢、不搬移**，且能鎖死層級上限 → 固定 Path 欄位(方案2) 可給到極致查詢效能，但維護代價高。  
3. 多數 Web / Cloud 應用需「不限層級、高速查詢、偶爾搬移」→ Nested Set Model(方案3) 在效能、擴充性、維運成本間取得最佳平衡。  

> 「預先為資料建立最容易被使用的索引，並將維護成本前移至異動階段」，  
> 正是架構師面對大量階層資料時的關鍵思考。
```