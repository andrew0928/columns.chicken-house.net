# 生命遊戲：有效率的使用執行緒

# 問題／解決方案 (Problem/Solution)

## Problem: 單一 Cell 採一條 Thread，導致執行緒過量、效能低落

**Problem**:  
在 30×30 的生命遊戲範例中，作者採「一個 Cell 一條 Thread」的寫法。程式一跑就產生 903 條執行緒，但 CPU 使用率卻不到 5%。若此模式被搬到線上遊戲 Server，每個玩家／怪物都綁一條 Thread，機器很快就會因為大量 Idle Thread 而崩潰。

**Root Cause**:  
1. 每條 Thread 內部用 `Thread.Sleep(...)` 進行被動等待 → Thread 處於阻塞 (Blocking) 狀態，無法被 ThreadPool 重複利用。  
2. Windows / CLR 為大量 Idle Thread 維護 TCB、堆疊等資源 → 記憶體、排程開銷極大。  
3. Context switch 次數隨 Thread 數線性增加，帶來額外 CPU Overhead。  

**Solution**:  
1. 把 `Thread.Sleep(...)` 改成 `yield return TimeSpan.FromMilliseconds(...)`，把「等待多久」改由函式回傳。  
2. 由 GameHost 實作小型排程器：  
   - 使用 thread-safe 的 `CellToDoList` (內部為 `SortedList<DateTime, Cell>`) 依下一次喚醒時間排序。  
   - GameHost 單一迴圈 `while(List.Count>0)`：  
     a. 取出最近要被叫醒的 Cell。  
     b. 若還沒到時間 → `Thread.Sleep(remaining)`。  
     c. 時間到時，將該 Cell 的邏輯丟進 ThreadPool (`QueueUserWorkItem`)。  
     d. Cell 執行完再回傳下一個 `TimeSpan`，GameHost 重新排程。  
3. 另外僅用 1 條 Thread 持續更新畫面 (`RefreshScreen`)。  
4. 實際程式 (精簡)：  

```csharp
// Cell: 把等待時間交給 GameHost
public IEnumerable<TimeSpan> WholeLife(object state)
{
    for (int i = 0; i < (int)state; i++)
    {
        OnNextStateChange();
        yield return TimeSpan.FromMilliseconds(_rnd.Next(950,1050));
    }
}

// GameHost: 單一排程器 + ThreadPool
static CellToDoList _cq;
static void YieldReturnGameHost()
{
    _cq = new CellToDoList();
    ... // 建立 world 與所有 cell，初始排程

    new Thread(RefreshScreen).Start(world);

    while (_cq.Count > 0)
    {
        Cell cell = _cq.GetNextCell();
        if (cell.NextWakeUpTime > DateTime.Now)
            Thread.Sleep(cell.NextWakeUpTime - DateTime.Now);

        ThreadPool.QueueUserWorkItem(RunCellNextStateChange, cell);
    }
}
```

關鍵思考點：  
• 透過 `yield return` 將「等待多久」資訊外移，Thread 不再阻塞；排程權交由 GameHost 決定，ThreadPool 可重複使用 Worker Thread。  
• `CellToDoList` 以時間排序，確保下一筆要被喚醒的工作永遠在最前端，降低搜尋及鎖定成本。  

**Cases 1**: 30×30 生命遊戲  
• 原始實作：903 Threads，CPU≈5% (大多 Idle)。  
• 新實作：9 Threads（含畫面更新），CPU 使用率維持 5% 左右，但記憶體消耗、Context Switch 次數大幅降低，Thread 數減少 99%。  

**Cases 2**: 模擬大型線上遊戲伺服器  
• 假設 5,000 個「生物」同時在線：  
  – 原始模型：5,000 Threads，OS 無法承受。  
  – 排程器模型：8~16 Threads（依 ThreadPool 動態調整），CPU 核心可充分被利用，伺服器可再向上擴充。  

--------------------------------------------------------------------

## Problem: Cell 需於不同時間被喚醒，缺乏可共享的時間排程機制

**Problem**:  
改用 `yield return` 後，每個 Cell 只回傳「下一次喚醒間隔」，但原程式設計並沒有一個元件能把「多個 Cell、各自不同的喚醒時間」有效排序與管理。

**Root Cause**:  
1. 傳統 Queue 為 FIFO，無法依時間優先級存取。  
2. 非同步環境下多 Thread 同時存取資料結構，需要 Thread-Safe 保護。  
3. 若無統一排程機制，GameHost 無法知道下一個該叫醒誰，勢必退回「一個 Cell 一條 Thread」的做法。

**Solution**:  
• 實作 `CellToDoList`：  
  – Public API：`AddCell(Cell)`, `GetNextCell()`, `CheckNextCell()`, `int Count`。  
  – 內部使用 `SortedList<DateTime, List<Cell>>` 或 `PriorityQueue`，Key 為下一次喚醒時間。  
  – 透過 `lock` 或 `Monitor` 保證並行安全。  
• GameHost 只負責：  
  1. 不斷 `GetNextCell()` 取得最近到期工作；  
  2. `Thread.Sleep(remaining)`；  
  3. 將 Cell 邏輯丟進 ThreadPool；  
  4. Cell 執行完畢後把自己附帶下一次時間重新 `AddCell()`。  

如此將「計時」與「執行」分離：時間表→`CellToDoList`；執行→ThreadPool Worker，實現少量 Thread 服務海量 Cell。

**Cases 1**:  
• 喚醒 900 Cells → `CellToDoList.Count = 900`，單一鎖定即可完成排序插入；GameHost 每次只喚醒一顆 Cell，不需線性掃描所有元素。  
• 喚醒時間越零碎，排程器優勢越明顯：在 1ms ~ 3s 隨機區間測試，仍只需要固定量 Worker Thread。  

--------------------------------------------------------------------

## Problem: 畫面必須即時刷新，但不能干擾排程流程

**Problem**:  
生命遊戲需要定期在 Console (或 UI) 更新地圖，若把畫面刷新邏輯與排程邏輯混在同一個 Thread，勢必拖慢整體排程節奏或導致 FPS 不穩。

**Root Cause**:  
排程循環需等待「下一顆 Cell 被叫醒」的時間點，可能間隔 1~2 秒；畫面更新最好固定 16ms~500ms 內刷新一次，二者節奏與優先級不同。

**Solution**:  
• 將畫面更新獨立 Thread：  

```csharp
private static void RefreshScreen(object state)
{
    while (true)
    {
        Thread.Sleep(500);      // 固定 2 FPS
        (state as World).ShowMaps("");
    }
}
```

• GameHost 啟動時即 `new Thread(RefreshScreen).Start(world);`，使排程邏輯與 UI 邏輯解耦。  

• 利用 read-only `World` snapshot 或加 ReaderLock，確保畫面讀資料時不阻塞排程。

**Cases 1**:  
– 排程迴圈最長 Sleep 2 秒，畫面仍能 0.5 秒更新一次，肉眼觀感流暢；排程效能亦不受影響。  

--------------------------------------------------------------------

```text
最終成效摘要
• Thread 數：903 ↓ 9 (-99%)
• CPU Idle Thread Switch 降低，系統能承載更多使用者／Cell
• 邏輯、排程、UI 三層拆分，程式可維護度提升
• 架構可直接沿用到線上遊戲 / 互動模擬等高併發場景
```

持續演進：在底層排程器穩固後，可進入 OOP 繼承／多型階段，擴充更多「生物」行為，打造真正的「模擬世界」。