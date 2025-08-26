以下內容基於提供的文章，整理出 16 個具教學價值的問題解決案例，均包含問題、根因、解法、程式碼與實測效益等資訊，便於實戰教學、專案練習與能力評估。

## Case #1: 每個 Cell 一條專用執行緒導致 Thread Explosion

### Problem Statement（問題陳述）
- 業務場景：以 30x30 的生命遊戲模擬世界（900 個 Cell）為例，每個 Cell 各自以 Thread 控制其生命週期，並定期變更狀態與休眠，GameHost 只負責刷新畫面。此模式若應用於線上遊戲 Server，每個角色/怪物都分配專用執行緒，系統資源會被大量佔用。
- 技術挑戰：執行緒數量爆炸（903 條），CPU 使用率卻不到 5%；大量執行緒處於睡眠或切換狀態，帶來調度與記憶體負擔，且不具可擴充性。
- 影響範圍：伺服器無法隨玩家/實體成長而擴充；上下文切換成本高；穩定性下降，容易出現資源耗盡。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 每個 Cell 配一條專屬執行緒，數量隨實體線性增加。
  2. Thread.Sleep 阻塞執行緒，造成大量閒置。
  3. OS 的排程與上下文切換成本被放大。
- 深層原因：
  - 架構層面：以「一實體一執行緒」的錯誤並行模型。
  - 技術層面：Blocking 模式（Sleep）與未使用 ThreadPool 的資源濫用。
  - 流程層面：缺乏集中式排程器與共享執行緒池的策略。

### Solution Design（解決方案設計）
- 解決策略：將每個 Cell 的行為改寫為可切片的協同程序（yield return TimeSpan），由 GameHost 建立時間排序的 ToDoList，使用 ThreadPool 動態執行 Cell 的下一步，使工作共享少量執行緒，並讓 GameHost 睡到下一個喚醒點，避免忙等。

- 實施步驟：
  1. Cell 行為改寫為可迭代的時間片
     - 實作細節：用 IEnumerable<TimeSpan> + yield return 替代 Thread.Sleep。
     - 所需資源：C#、.NET、編譯器狀態機。
     - 預估時間：0.5 天。
  2. 建立時間排序的 ToDoList（近似優先佇列）
     - 實作細節：用 SortedList<DateTime, Queue<Cell>> 搭配 lock 實作 thread-safe。
     - 所需資源：.NET Collections、lock。
     - 預估時間：0.5 天。
  3. GameHost 使用 ThreadPool 排程
     - 實作細節：取出最早到期 Cell；未到期則 Sleep 到到期時間；用 ThreadPool.QueueUserWorkItem 執行。
     - 所需資源：ThreadPool、DateTime/TimeSpan。
     - 預估時間：0.5 天。
  4. 畫面刷新獨立執行緒
     - 實作細節：固定週期刷新，與邏輯解耦。
     - 所需資源：Thread。
     - 預估時間：0.2 天。

- 關鍵程式碼/設定：
```csharp
// Cell：以 yield return 取代 Thread.Sleep
public IEnumerable<TimeSpan> WholeLife(object state) {
    int generation = (int)state;
    for (int i = 0; i < generation; i++) {
        this.OnNextStateChange();
        yield return TimeSpan.FromMilliseconds(_rnd.Next(950, 1050));
    }
}

// GameHost：共享執行緒 + 時間驅動排程
while (_cq.Count > 0) {
    Cell item = _cq.GetNextCell();
    if (item.NextWakeUpTime > DateTime.Now) {
        Thread.Sleep(item.NextWakeUpTime - DateTime.Now);
    }
    ThreadPool.QueueUserWorkItem(RunCellNextStateChange, item);
}
```

- 實際案例：30x30 網格；每個 Cell 初始 OnNextStateChangeEx 後加入 ToDoList；GameHost 專職時間排程；畫面刷新由獨立執行緒負責。
- 實作環境：C#、.NET（含 ThreadPool、SortedList、yield）、命令列或主控台。
- 實測數據：
  - 改善前：專用執行緒 903 條；CPU usage < 5%（大多在 Sleep）。
  - 改善後：執行緒數約 9 條；畫面與規則行為一致。
  - 改善幅度：執行緒數 -99%；資源占用與切換負擔大幅下降。

Learning Points（學習要點）
- 核心知識點：
  - 一實體一執行緒的反模式與成本。
  - 協同程序（yield/state machine）降低阻塞與提升可組合性。
  - 優先佇列式排程（時間排序）與 ThreadPool 搭配。
- 技能要求：
  - 必備技能：C# 基礎、Thread/ThreadPool、集合與 lock。
  - 進階技能：排程器設計、非阻塞思維、資源監控。
- 延伸思考：
  - 可否用 Timer 或 async/await 改寫？
  - 排程公平性與飢餓避免如何確保？
  - 畫面更新與邏輯更新的頻率如何協調？
- Practice Exercise（練習題）
  - 基礎練習：把 Thread.Sleep 改成 yield return，驗證能正確回報下一次時間（30 分）。
  - 進階練習：寫一個最小 ToDoList，支援 Add/Get/Check，並用 lock 保證 thread-safe（2 小時）。
  - 專案練習：完成整個 GameHost 重構，並量測執行緒數與 CPU 使用曲線（8 小時）。
- Assessment Criteria（評估標準）
  - 功能完整性（40%）：所有 Cell 能正確被喚醒、狀態正確演進。
  - 程式碼品質（30%）：結構清晰、資料結構選用合理、無競態。
  - 效能優化（20%）：執行緒數顯著降低、CPU 無忙等。
  - 創新性（10%）：額外加入監控與可視化、可配置排程策略。

## Case #2: 以 yield return TimeSpan 取代 Thread.Sleep 的協同切片

### Problem Statement（問題陳述）
- 業務場景：Cell 的生命週期原以迴圈 + Sleep 實作，專注在邏輯上，容易理解但會阻塞執行緒。希望保持「生物主動」的模型，同時避免阻塞。
- 技術挑戰：保留原有邏輯可讀性，同時改為非阻塞式，讓 GameHost 能接管時間驅動與執行緒統籌。
- 影響範圍：影響每個 Cell 的執行模型與整體排程方式。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Thread.Sleep 會掛起執行緒，資源被占住。
  2. 運算與時間控制綁死在同一條 Thread。
  3. 無法共享執行緒資源。
- 深層原因：
  - 架構層面：邏輯與時間控制耦合。
  - 技術層面：未使用編譯器生成的狀態機（yield）切片流程。
  - 流程層面：未定義「下一次喚醒時間」的回報契約。

### Solution Design（解決方案設計）
- 解決策略：把 WholeLife 改為 IEnumerable<TimeSpan>，每次狀態變更後用 yield return 回報下一次休眠時間，讓 GameHost 使用此契約排程喚醒。

- 實施步驟：
  1. 將 Thread.Sleep 改為 yield return TimeSpan
     - 細節：維持 for 迴圈與 OnNextStateChange，不阻塞執行緒。
     - 資源：C# 迭代器。
     - 時間：0.3 天。
  2. 調整 GameHost 呼叫方式
     - 細節：由 foreach 迭代取回 TimeSpan，換算 NextWakeUpTime 交 ToDoList。
     - 資源：DateTime、TimeSpan。
     - 時間：0.3 天。
  3. 測試與驗證
     - 細節：與舊版結果比對，確保邏輯一致。
     - 資源：單元測試或目視。
     - 時間：0.2 天。

- 關鍵程式碼/設定：
```csharp
// 修改後：協同切片
public IEnumerable<TimeSpan> WholeLife(object state) {
    int generation = (int)state;
    for (int i = 0; i < generation; i++) {
        this.OnNextStateChange();
        yield return TimeSpan.FromMilliseconds(_rnd.Next(950, 1050));
    }
}
```

- 實際案例：對所有 Cell 套用上述修改，GameHost 按契約排程。
- 實作環境：C#、.NET。
- 實測數據：
  - 改善前：Sleep 阻塞；必須 900+ Thread。
  - 改善後：可共享少量執行緒（約 9）；行為一致。
  - 改善幅度：執行緒 -99%。

Learning Points
- 核心知識點：yield 的狀態機、非阻塞與契約式排程、可中斷/可恢復的流程表達。
- 技能要求：C# 迭代器、時間控制。
- 延伸思考：可否用 async/await 回傳 Task<TimeSpan>？是否更易讀？
- Practice：將一段含 Sleep 的工作改寫為 IEnumerable<TimeSpan>（30 分）；在主程式迭代執行它（2 小時）；整合 ThreadPool（8 小時）。
- Assessment：契約正確性、無阻塞、效能與可讀性。

## Case #3: 建立時間排序的 ToDoList 排程器（近似優先佇列）

### Problem Statement（問題陳述）
- 業務場景：需要一個「時間表」管理 900 個 Cell 的下一次喚醒點，能以時間先後順序取出工作，並支援併發讀寫。
- 技術挑戰：正確排序、避免競態、提供 Add/Get/Check 介面，且效能足夠。
- 影響範圍：排程精準度、可擴充性、主迴圈的效率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺少集中式時間排程資料結構。
  2. FIFO 佇列無法滿足時間排序需求。
  3. 多執行緒存取易競態。
- 深層原因：
  - 架構層面：缺乏排程器抽象。
  - 技術層面：未利用排序結構如 SortedList。
  - 流程層面：缺少 thread-safe 設計規範。

### Solution Design（解決方案設計）
- 解決策略：以 SortedList<DateTime, Queue<Cell>> 實作 ToDoList；Add 會插入依時間排序；Get 取出最早到期；Check 允許窺視；全域 lock 保證 thread-safe。

- 實施步驟：
  1. 定義公開介面
     - 細節：AddCell/ GetNextCell/ CheckNextCell/ Count。
     - 資源：類別設計。
     - 時間：0.2 天。
  2. 以 SortedList 實作
     - 細節：鍵為 NextWakeUpTime；相同時間用 Queue。
     - 資源：SortedList、Queue。
     - 時間：0.5 天。
  3. 加入 lock 確保 thread-safe
     - 細節：方法級別或細粒度 lock。
     - 資源：lock。
     - 時間：0.2 天。

- 關鍵程式碼/設定：
```csharp
public class CellToDoList {
    private readonly SortedList<DateTime, Queue<Cell>> _data = new();
    private readonly object _sync = new();

    public void AddCell(Cell cell) {
        lock (_sync) {
            if (!_data.TryGetValue(cell.NextWakeUpTime, out var q)) {
                q = new Queue<Cell>();
                _data.Add(cell.NextWakeUpTime, q);
            }
            q.Enqueue(cell);
        }
    }

    public Cell GetNextCell() {
        lock (_sync) {
            if (_data.Count == 0) return null;
            var key = _data.Keys[0];
            var q = _data.Values[0];
            var cell = q.Dequeue();
            if (q.Count == 0) _data.RemoveAt(0);
            return cell;
        }
    }

    public Cell CheckNextCell() {
        lock (_sync) {
            if (_data.Count == 0) return null;
            return _data.Values[0].Peek();
        }
    }

    public int Count { get { lock (_sync) return _data.Sum(kv => kv.Value.Count); } }
}
```

- 實際案例：GameHost 以此 ToDoList 排程 900 個 Cell。
- 實作環境：C#、.NET、Collections。
- 實測數據：
  - 改善前：無集中式排程；必須專用 Thread。
  - 改善後：以時間排序取用，ThreadPool 動態執行；執行緒 ~9。
  - 改善幅度：執行緒 -99%；排程秩序明確。

Learning Points
- 核心知識點：優先佇列/時間輪設計、thread-safe 集合、鍵碰撞處理。
- 技能要求：集合運用、同步化。
- 延伸思考：是否改用二元堆或小根堆提升大量元素效率？
- Practice：以 Heap 重寫 ToDoList（2 小時）；壓測 Add/Get 延遲（8 小時）。
- Assessment：正確排序、無競態、效能表現。

## Case #4: 以 ThreadPool 取代自建工作執行緒

### Problem Statement（問題陳述）
- 業務場景：每個 Cell 的下一步邏輯短暫且可並行，專用 Thread 成本高且大多在睡眠。需改為共享執行緒。
- 技術挑戰：如何將 Cell 的工作以工作項目形式提交、由系統自動調節併發度。
- 影響範圍：資源使用、可擴充性與穩定度。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 專用 Thread 無法重複利用。
  2. 睡眠導致 Thread 空轉。
  3. 缺乏動態併發控制。
- 深層原因：
  - 架構層面：未採用池化資源。
  - 技術層面：未利用 ThreadPool。
  - 流程層面：缺乏工作項目制。

### Solution Design（解決方案設計）
- 解決策略：用 ThreadPool.QueueUserWorkItem 執行 OnNextStateChangeEx，完成後回報下一次喚醒時間並重新加入 ToDoList。

- 實施步驟：
  1. 封裝工作項
     - 細節：RunCellNextStateChange 接受 Cell，執行邏輯。
     - 資源：ThreadPool API。
     - 時間：0.2 天。
  2. 提交到 ThreadPool
     - 細節：GameHost 取到期 Cell 後，排入池中執行。
     - 時間：0.2 天。
  3. 收斂執行緒數
     - 細節：觀測 OS 動態調節併發度。
     - 時間：0.1 天。

- 關鍵程式碼/設定：
```csharp
private static void RunCellNextStateChange(object state) {
    var item = (Cell)state;
    TimeSpan? ts = item.OnNextStateChangeEx();
    if (ts != null) _cq.AddCell(item);
}

ThreadPool.QueueUserWorkItem(RunCellNextStateChange, item);
```

- 實際案例：全數 Cell 的下一步運算均透過 ThreadPool 執行。
- 實作環境：C#、.NET ThreadPool。
- 實測數據：
  - 改善前：903 專用 Thread。
  - 改善後：~9 Thread（池化調整）；功能一致。
  - 改善幅度：執行緒 -99%。

Learning Points
- 核心知識點：ThreadPool 適用性、工作項提交與回收、避免阻塞池執行緒。
- 技能要求：ThreadPool、非阻塞設計。
- 延伸思考：是否需要自建自調節的 Task Scheduler？
- Practice：把一組短工作改用 ThreadPool 執行並量測併發（2 小時）。
- Assessment：池化利用率、無阻塞、正確回報下一輪時間。

## Case #5: 睡到下一個喚醒點，避免 Busy-Wait

### Problem Statement（問題陳述）
- 業務場景：GameHost 在等待下一個 Cell 的執行時間時，若用輪詢易造成 CPU 忙等；需精準睡眠到下一喚醒點。
- 技術挑戰：如何避免 busy-wait 同時不影響準確性。
- 影響範圍：CPU 使用率、電力與效能。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 輪詢 CheckNextCell 造成忙等。
  2. 未充分利用阻塞式睡眠。
- 深層原因：
  - 架構層面：主迴圈等待策略不當。
  - 技術層面：未根據 NextWakeUpTime 計算 Sleep 時長。
  - 流程層面：無等待策略規範。

### Solution Design（解決方案設計）
- 解決策略：對即將到期的 Cell 計算剩餘時間，直接 Thread.Sleep(remaining) 至到期，然後提交到 ThreadPool 執行。

- 實施步驟：
  1. 取出最早到期 Cell
     - 細節：使用 ToDoList.GetNextCell。
  2. 計算剩餘時間
     - 細節：remaining = NextWakeUpTime - DateTime.Now。
  3. 阻塞到點
     - 細節：Thread.Sleep(remaining)；到時間後提交執行。
- 關鍵程式碼/設定：
```csharp
Cell item = _cq.GetNextCell();
if (item.NextWakeUpTime > DateTime.Now) {
    Thread.Sleep(item.NextWakeUpTime - DateTime.Now);
}
ThreadPool.QueueUserWorkItem(RunCellNextStateChange, item);
```

- 實作環境：C#、.NET。
- 實測數據：
  - 改善前：可能 busy-wait。
  - 改善後：CPU 閒置時幾乎不耗用；執行緒 ~9。
  - 改善幅度：Idle CPU 浪費顯著下降。

Learning Points
- 核心知識點：時間驅動主迴圈、忙等的危害、精準睡眠。
- 技能要求：時間計算、非忙等等待。
- 延伸思考：系統時間跳變如何處理？可用 Stopwatch/單調時鐘。
- Practice：實作睡到時的等待策略，與輪詢相比較 CPU 使用（2 小時）。
- Assessment：CPU 穩定、時間準確、無過度喚醒。

## Case #6: 以獨立執行緒解耦畫面刷新與邏輯運算

### Problem Statement（問題陳述）
- 業務場景：需要每 500ms 刷新畫面，同時邏輯運算由排程器負責；兩者耦合會互相阻塞。
- 技術挑戰：避免畫面更新阻塞邏輯，或邏輯運算阻塞畫面。
- 影響範圍：使用者體驗、反應時間。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 共享相同執行緒導致互阻。
  2. 特定刷新頻率與非同步邏輯無法對齊。
- 深層原因：
  - 架構層面：職責未分離。
  - 技術層面：未使用獨立 Thread。
  - 流程層面：缺少固定頻率更新的 loop。

### Solution Design（解決方案設計）
- 解決策略：開一條獨立的 RefreshScreen 執行緒，固定 Thread.Sleep(500)，持續渲染 World。

- 實施步驟：
  1. 建立刷新執行緒
     - 細節：Thread t = new Thread(RefreshScreen)；t.Start(world)。
  2. 固定頻率刷新
     - 細節：Thread.Sleep(500)；World.ShowMaps("")。
  3. 避免與邏輯共享狀態
     - 細節：必要時加鎖或快照。
- 關鍵程式碼/設定：
```csharp
private static void RefreshScreen(object state) {
    while (true) {
        Thread.Sleep(500);
        (state as World).ShowMaps("");
    }
}
```

- 實作環境：C#、.NET。
- 實測數據：
  - 改善後：畫面更新平穩，無阻塞邏輯；執行緒總數 ~9。
Learning Points
- 核心知識點：職責分離、雙主迴圈（邏輯/渲染）。
- 技能要求：Thread 管理、狀態一致性。
- 延伸思考：GUI 框架需在 UI Thread 更新，如何封送？
- Practice：將渲染/邏輯拆線程並量測卡頓（2 小時）。
- Assessment：無互阻、更新穩定。

## Case #7: 被動 Callback 模式改為主動 Execute 模式

### Problem Statement（問題陳述）
- 業務場景：先前採固定時間喚醒（callback）模式，不符合「生物主動」的建模需求；改為主動執行（execute）更貼近領域。
- 技術挑戰：轉換執行模型，讓每個 Cell 以主動形式進行，仍需統一時間管控。
- 影響範圍：邏輯表達、可讀性、可維護性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Callback 難以表達主動行為。
  2. 時間管控分散。
- 深層原因：
  - 架構層面：責任歸屬不明確。
  - 技術層面：缺少協同契約（yield）。
  - 流程層面：無中央排程器。

### Solution Design（解決方案設計）
- 解決策略：Cell 以主動邏輯迭代自身，透過 yield 告知下一次行動時間；GameHost 集中喚醒與執行。

- 實施步驟：
  1. Cell：主動 OnNextStateChange + yield 時間。
  2. Host：根據回報時間排程。
  3. ThreadPool：執行 Cell 下一步。
- 關鍵程式碼/設定：
```csharp
// 主動模型：每步主動變更後回報下一次時間
public IEnumerable<TimeSpan> WholeLife(object state) { /* 同 Case #2 */ }
```

- 實測數據：功能與舊版一致；執行緒 ~9；可讀性提升。
Learning Points
- 核心知識點：建模與執行模型一致性、集中式時間管控。
- 技能要求：OOP 與流程設計。
- 延伸思考：以多型擴充不同生物的行為。
- Practice：將 callback 範式改為 execute + yield（2 小時）。
- Assessment：語義一致、維護性高。

## Case #8: ToDoList 的 thread-safe 設計與 lock 應用

### Problem Statement（問題陳述）
- 業務場景：GameHost 與多個 ThreadPool 工作同時讀寫 ToDoList，需保證正確性與一致性。
- 技術挑戰：避免競態條件、避免死鎖、在鎖下仍維持合理效能。
- 影響範圍：穩定性、資料一致性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 多執行緒並發讀寫。
  2. 非原子操作（取首元素、刪除）。
- 深層原因：
  - 架構層面：共用可變狀態。
  - 技術層面：未加鎖或鎖粒度不當。
  - 流程層面：未定義存取規範。

### Solution Design（解決方案設計）
- 解決策略：用單一內部鎖保護所有結構性操作；在 Get/Check/Count/新增與刪除中以最小臨界區完成。

- 實施步驟：
  1. 設計內部鎖物件
  2. 保護所有修改或讀取流程
  3. 嚴格審視臨界區長度
- 關鍵程式碼/設定：
```csharp
private readonly object _sync = new();
public int Count { get { lock (_sync) return /* 計算總數 */; } }
public void AddCell(Cell c) { lock (_sync) { /* 插入並排序 */ } }
public Cell GetNextCell() { lock (_sync) { /* 取最早到期 */ } }
```

- 實際案例：穩定運作無競態異常。
- 實作環境：C#、.NET。
- 實測數據：運作穩定；未見死鎖與資料錯亂。
Learning Points
- 核心知識點：臨界區、鎖粒度、集合一致性。
- 技能要求：lock、併發設計。
- 延伸思考：可否用 Concurrent 結構或 ReaderWriterLockSlim？
- Practice：壓測併發 Add/Get 操作，驗證正確性（2 小時）。
- Assessment：無競態、吞吐穩定。

## Case #9: 降低大量執行緒帶來的 Context Switch 開銷

### Problem Statement（問題陳述）
- 業務場景：900+ 執行緒大量處於 Sleep 或就緒狀態，OS 頻繁上下文切換造成效能浪費。
- 技術挑戰：在行為不變的前提下降低切換次數與排程負擔。
- 影響範圍：整體系統效能與穩定度。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 執行緒數過多，遠超核心數。
  2. Sleep/喚醒造成排程揀選負擔。
- 深層原因：
  - 架構層面：錯誤的併發模型。
  - 技術層面：阻塞式等待。
  - 流程層面：無池化策略。

### Solution Design（解決方案設計）
- 解決策略：將阻塞等待轉為 yield 回報；以 ThreadPool 限制工作執行緒數；Host 睡到「單一」下一時點。

- 實施步驟：
  1. 去阻塞（yield）
  2. 使用池化（ThreadPool）
  3. 單點睡眠（Host）
- 關鍵程式碼/設定：同 Case #1/#2/#5。

- 實測數據：
  - 改善前：903 執行緒；大量切換。
  - 改善後：~9 執行緒；切換大幅減少。
  - 改善幅度：執行緒 -99%，排程成本顯著降低。

Learning Points
- 核心知識點：上下文切換代價、池化與限流。
- 技能要求：ThreadPool、非阻塞設計。
- 延伸思考：對高核心數機器與 NUMA 的影響？
- Practice：以 Perf 工具觀測 Context Switch（8 小時）。
- Assessment：切換次數下降、延遲穩定。

## Case #10: 保留每個 Cell 的隨機時間行為

### Problem Statement（問題陳述）
- 業務場景：每個 Cell 以 950~1050ms 的隨機間隔演進。改為集中排程後需維持此隨機性以反映真實性。
- 技術挑戰：避免因集中排程導致所有 Cell 同步化或週期化。
- 影響範圍：模擬真實度、可玩性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 時間控制集中後，若未保留隨機性，易同步。
- 深層原因：
  - 架構層面：隨機性責任應留在 Cell。
  - 技術層面：隨機延遲需回報給 Host。
  - 流程層面：契約需攜帶時間資訊。

### Solution Design（解決方案設計）
- 解決策略：Cell 在每步 OnNextStateChange() 後 yield return 隨機 TimeSpan，由 Host 將它轉為 NextWakeUpTime。

- 實施步驟：
  1. 在 Cell 內產生隨機毫秒
  2. yield return 該時間
  3. Host 接收並計算下一次喚醒
- 關鍵程式碼/設定：
```csharp
yield return TimeSpan.FromMilliseconds(_rnd.Next(950, 1050));
```

- 實測數據：視覺與行為與舊版一致；未出現同步化。
Learning Points
- 核心知識點：隨機性封裝、時間契約。
- 技能要求：TimeSpan、隨機數生成。
- 延伸思考：用不同分佈（正態/指數）模擬更真實行為。
- Practice：替不同 Cell 類型定義不同延遲分佈（2 小時）。
- Assessment：隨機性保真、分佈正確。

## Case #11: 啟動暖機：預先設定首個 NextWakeUpTime

### Problem Statement（問題陳述）
- 業務場景：ToDoList 需要每個 Cell 的 NextWakeUpTime 來排程；若不先產生，排程器無法工作。
- 技術挑戰：初始化過程需為所有 Cell 建立第一個到期點。
- 影響範圍：啟動正確性、第一輪排程。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. NextWakeUpTime 未設定。
- 深層原因：
  - 架構層面：初始化責任未界定。
  - 技術層面：首次 OnNextStateChangeEx 未被觸發。

### Solution Design（解決方案設計）
- 解決策略：在建立世界時，對每個 Cell 呼叫一次 OnNextStateChangeEx 以產生首個 ts，並加入 ToDoList。

- 實施步驟：
  1. 遍歷所有 Cell
  2. 呼叫 OnNextStateChangeEx 取得 ts
  3. 加入 ToDoList
- 關鍵程式碼/設定：
```csharp
for (int x = 0; x < worldSizeX; x++)
for (int y = 0; y < worldSizeY; y++) {
    var cell = realworld.GetCell(x, y);
    cell.OnNextStateChangeEx();
    _cq.AddCell(cell);
}
```

- 實測數據：第一輪排程如期運作；不需專用 Thread。
Learning Points
- 核心知識點：系統啟動序、狀態預熱。
- 技能要求：初始化流程設計。
- 延伸思考：是否需要快照或重放機制？
- Practice：設計可重啟後恢復的初始化（8 小時）。
- Assessment：啟動穩定、第一輪準確。

## Case #12: CheckNextCell 先看不取的 API 以提升可觀測性

### Problem Statement（問題陳述）
- 業務場景：GameHost 偶爾需要知道下一個將被喚醒的 Cell 與時間，以便除錯或監控，但不應影響排程順序。
- 技術挑戰：提供窺視功能且不破壞資料結構不變式。
- 影響範圍：可觀測性、除錯效率。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 無法得知下一個到期項目而不取出。
- 深層原因：
  - 架構層面：API 設計不足。
  - 技術層面：未封裝 Peek 行為。

### Solution Design（解決方案設計）
- 解決策略：提供 CheckNextCell() 回傳下一個到期 Cell 的窺視，不移除節點。

- 實施步驟：
  1. 在 ToDoList 新增 CheckNextCell
  2. 以 Peek 實作
  3. 加鎖保障一致性
- 關鍵程式碼/設定：
```csharp
public Cell CheckNextCell() {
    lock (_sync) {
        if (_data.Count == 0) return null;
        return _data.Values[0].Peek();
    }
}
```

- 實測數據：監控/除錯更容易；不影響排程。
Learning Points
- 核心知識點：API 可觀測性設計、Peek/Pop 分離。
- 技能要求：集合封裝。
- 延伸思考：暴露下一到期時間供監控 UI 顯示。
- Practice：建立簡易監控面板顯示下一到期工作（2 小時）。
- Assessment：不破壞排序、資訊充足。

## Case #13: 用 SortedList 打造近似優先佇列（按時間）

### Problem Statement（問題陳述）
- 業務場景：需依到期時間順序處理工作；同一時間可能多個 Cell 同時到期。
- 技術挑戰：同鍵衝突處理、維持穩定排序。
- 影響範圍：排程正確性與一致性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 多元素具有相同 DateTime 鍵。
- 深層原因：
  - 架構層面：未定義同時到期的處理策略。
  - 技術層面：SortedList 不允許重複鍵。

### Solution Design（解決方案設計）
- 解決策略：鍵為 DateTime；值為 Queue<Cell>。同一鍵存放隊列以保持穩定性；空隊列即移除鍵。

- 實施步驟：
  1. Add：若無鍵則新增 Queue，否則 Enqueue
  2. Get：從最小鍵的 Queue.Dequeue
  3. 清理：Queue 空則 RemoveAt(0)
- 關鍵程式碼/設定：同 Case #3。

- 實測數據：同時到期時仍正確順序處理；穩定性佳。
Learning Points
- 核心知識點：穩定排序、鍵衝突解。
- 技能要求：集合設計。
- 延伸思考：使用二元堆結構的優缺點比較。
- Practice：改用小根堆實作，壓測插入/取出（8 小時）。
- Assessment：排序正確、吞吐穩定。

## Case #14: 以 IEnumerable<TimeSpan> 實作協同程序（Coroutine）切片長流程

### Problem Statement（問題陳述）
- 業務場景：Cell 的生命流程是長周期且重複的，需切片為可交錯執行的段落，以利共享執行緒。
- 技術挑戰：在不增加複雜度下切片，並保留流程上下文。
- 影響範圍：可讀性、維護性、效能。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 傳統函式一次性執行，難以中斷/恢復。
- 深層原因：
  - 架構層面：缺少協同程序概念。
  - 技術層面：未利用 C# 迭代器生成狀態機。

### Solution Design（解決方案設計）
- 解決策略：用 yield 讓編譯器生成狀態機，自動保存當前索引與局部狀態；每次 MoveNext() 進行一小步。

- 實施步驟：
  1. 改函式回傳 IEnumerable<TimeSpan>
  2. 在迴圈中使用 yield return
  3. Host 控制 MoveNext 時機
- 關鍵程式碼/設定：同 Case #2。

- 實測數據：行為一致；共享執行緒；維護性提升。
Learning Points
- 核心知識點：C# 迭代器、狀態機。
- 技能要求：序列化流程設計。
- 延伸思考：對比 async/await 的優缺點。
- Practice：把另一段長流程改成 IEnumerable 協同程序（2 小時）。
- Assessment：流程可中斷恢復、語意清晰。

## Case #15: 達到 #2 範例相同視覺效果，但以更有效率方式實現

### Problem Statement（問題陳述）
- 業務場景：在不改變生命遊戲效果的前提下，需顯著降低執行緒與資源耗用。
- 技術挑戰：功能等價但實作效率更高。
- 影響範圍：效能成本、可擴充性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 舊版以高執行緒數達成效果。
- 深層原因：
  - 架構層面：錯誤的資源模型。
  - 技術層面：缺少排程器與池化。

### Solution Design（解決方案設計）
- 解決策略：綜合採用 yield、ToDoList、ThreadPool 與精準睡眠，以少量執行緒提供與 #2 相同效果。

- 實施步驟：
  1. 契約改造（yield）
  2. 時間排程（ToDoList）
  3. 共享執行（ThreadPool）
  4. 解耦渲染（獨立 Thread）
- 關鍵程式碼/設定：同 Case #1。

- 實測數據：
  - 改善前：903 Thread；CPU < 5%。
  - 改善後：~9 Thread；畫面一致。
  - 改善幅度：執行緒 -99%。

Learning Points
- 核心知識點：等價轉換、效能導向重構。
- 技能要求：重構與驗證、基準測試。
- 延伸思考：如何自動化驗證「效果等價」？
- Practice：建立效能基線與等價測試（8 小時）。
- Assessment：功能等價、資源顯著下降。

## Case #16: 從單機範例推廣到線上遊戲 Server 的可擴充性

### Problem Statement（問題陳述）
- 業務場景：若每個玩家/怪物均以專用 Thread 控制，玩家數稍增即導致伺服器不穩甚至掛掉。
- 技術挑戰：在多人與多實體的情境下保持低執行緒數與即時回應。
- 影響範圍：服務容量、成本、SLA。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 一實體一執行緒無法擴充。
- 深層原因：
  - 架構層面：缺乏中央排程與時間輪。
  - 技術層面：使用阻塞式 Sleep。
  - 流程層面：運維無法承受高 Thread 數。

### Solution Design（解決方案設計）
- 解決策略：以本文模型推廣為伺服器內核：實體行為協同化（yield 時間契約）+ 時間排序排程 + ThreadPool 執行 + 渲染/網路 IO 解耦，達到高併發下低執行緒與穩定延遲。

- 實施步驟：
  1. 實體行為契約化
  2. 時間排程器服務化
  3. ThreadPool 與限流策略
  4. 監控與背壓
- 關鍵程式碼/設定：同前述總和。

- 實測數據（參照本文趨勢）：
  - 專用 Thread 架構：人數成長即失衡。
  - 協同 + 池化：執行緒隨工作量平滑調整；總 Thread 維持低量級。
Learning Points
- 核心知識點：可擴充併發模型、背壓與限流。
- 技能要求：服務化、監控、容量規劃。
- 延伸思考：分散式排程、多機時間同步。
- Practice：以本文核心設計出微型遊戲伺服器框架（8 小時）。
- Assessment：容量擴充性、穩定性、監控完備。

————————————

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #5 避免 Busy-Wait
  - Case #6 畫面刷新解耦
  - Case #10 保留隨機行為
  - Case #12 CheckNextCell API
- 中級（需要一定基礎）
  - Case #1 Thread Explosion 治理
  - Case #2 yield 取代 Sleep
  - Case #3 時間排序 ToDoList
  - Case #4 ThreadPool 應用
  - Case #7 模型轉換（Callback→Execute）
  - Case #8 thread-safe 設計
  - Case #9 降低 Context Switch
  - Case #13 SortedList 優先佇列
  - Case #14 協同程序切片
  - Case #15 功能等價更高效
- 高級（需要深厚經驗）
  - Case #16 推廣到線上遊戲 Server（可擴充性設計）
  - Case #11 啟動暖機與恢復（若加入快照/重放設計延伸則屬高級）

2) 按技術領域分類
- 架構設計類
  - Case #1、#3、#6、#7、#11、#12、#13、#16
- 效能優化類
  - Case #2、#4、#5、#8、#9、#10、#14、#15
- 整合開發類
  - Case #4、#6、#11、#12、#15、#16
- 除錯診斷類
  - Case #12、#8、#5
- 安全防護類
  - 無（本文情境未涉及）

3) 按學習目標分類
- 概念理解型
  - Case #7、#14、#1
- 技能練習型
  - Case #2、#3、#4、#5、#6、#8、#13
- 問題解決型
  - Case #1、#9、#10、#11、#12、#15
- 創新應用型
  - Case #16

————————————

案例關聯圖（學習路徑建議）
- 先學哪些案例？
  - 基礎建議順序：Case #2（yield 概念）→ Case #5（時間等待策略）→ Case #4（ThreadPool）→ Case #3（ToDoList/排序結構）→ Case #6（渲染解耦）。
- 依賴關係
  - Case #1 依賴 #2/#3/#4/#5 的綜合應用。
  - Case #7 建模思想，最好在 #2 後學。
  - Case #8/#13 建立在 #3 之上。
  - Case #9 是 #1 的效能視角延伸。
  - Case #11 啟動流程依賴 #3。
  - Case #12 可在 #3 之後加強可觀測性。
  - Case #15 是 #1 的功能等價驗證延伸。
  - Case #16 建立在所有前述案例的綜合能力上。
- 完整學習路徑建議
  1) 概念與基礎：#2 → #5 → #4  
  2) 資料結構與排程：#3 → #8 → #13 → #12  
  3) 架構與模型：#7 → 綜合應用 #1 → 效能與驗證 #9/#15  
  4) 系統化與擴充：啟動流程 #11 → 渲染/邏輯解耦 #6 → 隨機行為 #10  
  5) 產業級應用：#16

說明：以上 16 個案例均以文中實際的重構為核心，具備問題、根因、解法與效益；關鍵程式碼直接來源於文章或其結構化延伸，並以可練習、可評估的方式呈現，便於教學、實作與評量。