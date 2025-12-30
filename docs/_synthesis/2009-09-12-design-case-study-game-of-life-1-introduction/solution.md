---
layout: synthesis
title: "[設計案例] 生命遊戲#1, 前言"
synthesis_type: solution
source_post: /2009/09/12/design-case-study-game-of-life-1-introduction/
redirect_from:
  - /2009/09/12/design-case-study-game-of-life-1-introduction/solution/
---

以下為根據文章所述的問題與解決方向，整理出的 15 個實戰型案例。由於本文為前言性質，未提供實測數據與完整程式碼，以下案例提供可落地的設計與最小可行實作（含關鍵碼／流程），并以定性效益描述為主。

## Case #1: 用 yield return 消弭「write-only」主迴圈

### Problem Statement（問題陳述）
業務場景：需開發生命遊戲模擬器。傳統實作以單一主迴圈交織各細胞邏輯，造成每個細胞的狀態計算被切成碎片，閱讀與維護困難。希望運用現代 C# 特性，讓每個細胞行為以可讀的流程展現，同時保有全局步進控制。
技術挑戰：將細胞行為以可中斷/續行方式表達，避免跨細胞交錯的流程碎片化。
影響範圍：可讀性、維護性、除錯效率、單元測試可行性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一主迴圈夾帶所有細胞邏輯，導致流程交錯。
2. 狀態轉換需分次完成，使邏輯被「切開」且難以追蹤。
3. 程式碼結構偏程序式，缺乏單元邊界與抽象。
深層原因：
- 架構層面：無明確的行為抽象與執行邊界。
- 技術層面：未善用 C# 的迭代器（yield）表達可恢復流程。
- 流程層面：過度依賴單一控制流與共享可變狀態。

### Solution Design（解決方案設計）
解決策略：使用 yield return 將「每個細胞一次步進」表達為一個可迭代的協作程序（coroutine），由中央排程器逐一推進各細胞的 MoveNext，使每個細胞行為集中在同一方法內，提升可讀性與可測性。

實施步驟：
1. 建立 Actor 介面
- 實作細節：IActor.Run() 回傳 IEnumerable<TimeSpan>，每次 yield 表示下一次喚醒間隔。
- 所需資源：.NET/C#，IEnumerable/yield。
- 預估時間：0.5 天

2. 實作中央排程器
- 實作細節：收集各細胞的 IEnumerator，輪詢 MoveNext，依 yield 的 TimeSpan 決定下次喚醒。
- 所需資源：Stopwatch、計時結構。
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public interface IActor
{
    IEnumerable<TimeSpan> Run();
}

public sealed class Cell : IActor
{
    private readonly Grid _grid;
    private readonly Point _pos;
    private readonly TimeSpan _period;
    public Cell(Grid grid, Point pos, TimeSpan period) { _grid = grid; _pos = pos; _period = period; }

    public IEnumerable<TimeSpan> Run()
    {
        while (true)
        {
            // 使用快照計算下一狀態（避免即時修改）
            var alive = _grid.CountAliveNeighborsSnapshot(_pos);
            var next = GameOfLifeRule.Apply(alive, _grid.Current[_pos]);
            _grid.StageNext(_pos, next); // 暫存到 next buffer
            yield return _period;        // 告知排程器下次喚醒間隔
        }
    }
}
```

實際案例：本文為前言，未提供具體案例數據；此解法緊扣作者提出「用 yield return 解決邏輯破碎」方向。
實作環境：.NET 6+/C# 10 或 .NET Framework 3.5+（語法需調整）
實測數據：
改善前：邏輯交錯、難以逐步除錯。
改善後：單元（細胞）行為集中、可逐步推進與測試。
改善幅度：未提供量化數據（定性改善顯著）。

Learning Points（學習要點）
核心知識點：
- 迭代器/yield 的協作式流程建模
- 將狀態更新表達為可中斷/續行的序列
- 階段性狀態計算與集中行為封裝
技能要求：
- 必備技能：C# 迭代器、基本集合
- 進階技能：協作程序設計、排程器概念
延伸思考：
- 還可應用於 AI 行為樹、遊戲 NPC 腳本
- 風險：誤用會造成控制流分散在多枚舉器
- 優化：加上可觀測事件與診斷鉤子

Practice Exercise（練習題）
基礎練習：用 yield 建立一個每秒打印時間的 Actor
進階練習：實作兩種不同週期的 Cell 並由排程器協同執行
專案練習：將生命遊戲整個步進改為 coroutine 化，支援暫停/繼續

Assessment Criteria（評估標準）
功能完整性（40%）：每個 Cell 可被獨立推進且結果正確
程式碼品質（30%）：行為集中、命名清楚、無共享可變狀態外洩
效能優化（20%）：排程器推進開銷可控
創新性（10%）：對 yield 的進一步抽象（事件、監控）



## Case #2: 以多型處理「不同更新頻率」細胞

### Problem Statement（問題陳述）
業務場景：生命遊戲為時間步進模擬，有的細胞每 1 秒更新，有的每 2 或 5 秒。若以單一主迴圈分支控制，條件判斷繁雜且分散，難以擴充新型態的更新節奏。
技術挑戰：支援異步進頻率的行為，同時保持邏輯內聚與擴充彈性。
影響範圍：可擴充性、維護性、錯誤率、排程負荷。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不同更新頻率被塞入主迴圈條件分支。
2. 更新頻率與行為耦合，導致修改頻繁。
3. 時間控制分散，增加理解負擔。
深層原因：
- 架構層面：缺乏型別多型抽象（策略/模板方法）。
- 技術層面：未將節奏（period）作為一級概念交由對象自管理。
- 流程層面：集中式條件驅動，缺少對象導向分工。

### Solution Design（解決方案設計）
解決策略：以抽象類別或介面定義 Cell 行為，將週期與規則封裝於子類或策略實例，排程器僅根據 yield 之 TimeSpan 喚醒對應細胞，達到行為與節奏解耦。

實施步驟：
1. 定義抽象 Cell
- 實作細節：抽象 Period 與 EvaluateNext，子類覆寫 Period。
- 所需資源：C# 繼承/介面
- 預估時間：0.5 天

2. 整合排程器
- 實作細節：Run() 使用 Period 決定 yield 間隔。
- 所需資源：Case #1 的排程器
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public abstract class CellBase : IActor
{
    protected readonly Grid Grid;
    protected readonly Point Pos;
    protected CellBase(Grid grid, Point pos) { Grid = grid; Pos = pos; }
    protected abstract TimeSpan Period { get; }
    protected abstract bool EvaluateNext();
    public IEnumerable<TimeSpan> Run()
    {
        while (true)
        {
            var next = EvaluateNext();
            Grid.StageNext(Pos, next);
            yield return Period;
        }
    }
}

public sealed class FastCell : CellBase
{
    public FastCell(Grid g, Point p) : base(g, p) { }
    protected override TimeSpan Period => TimeSpan.FromSeconds(1);
    protected override bool EvaluateNext() => GameOfLifeRule.Apply(Grid.CountAliveNeighborsSnapshot(Pos), Grid.Current[Pos]);
}
```

實際案例：本文舉出「1/2/5 秒」異步更新想定，解法對應。
實作環境：.NET 6+/C# 10
實測數據：
改善前：分支膨脹、難測試。
改善後：以多型擴充新頻率不需改核心。
改善幅度：未提供量化數據。

Learning Points
核心知識點：
- 多型解耦行為與節奏
- 將時間語義下放到對象
- 排程與行為的邊界設計
技能要求：
- 必備：OOP 基礎、繼承/介面
- 進階：策略/模板方法模式
延伸思考：
- 可支援動態調整 Period（自適應）
- 風險：類別過多可以策略化減少
- 優化：以組合替代繼承（Period 作為策略）

Practice Exercise
基礎：新增 SlowCell（5 秒）型別
進階：將 Period 改為動態計算（依鄰居密度）
專案：支援以組態檔定義多型 Cell

Assessment Criteria
功能完整性：異步頻率正確執行
程式碼品質：行為封裝、依賴倒置
效能優化：低排程開銷
創新性：Period 策略化



## Case #3: 避免「一細胞一執行緒」的 thread explosion

### Problem Statement（問題陳述）
業務場景：網格中可能有成千上萬個細胞。若為每個細胞建立一個 OS Thread，將導致極大的切換與記憶體負擔，且吞吐量急劇下降。
技術挑戰：在高併發場景下，以少數工作緒處理大量細胞的步進。
影響範圍：效能、資源使用、穩定性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. OS Thread 成本高（1:1 threading）。
2. Context switch 頻繁導致 CPU 時間浪費。
3. 大量阻塞等候造成資源閒置。
深層原因：
- 架構層面：未將工作以任務/協作程序抽象。
- 技術層面：忽視 ThreadPool/Task/協作式排程。
- 流程層面：以 Thread 代表活動單元的錯誤心智模型。

### Solution Design（解決方案設計）
解決策略：採用協作式 coroutine + 中央排程器（單或少數工作緒），加上資料層的分區並行（Task/ThreadPool）。細胞不直接對應 Thread，而由排程器驅動其枚舉器。

實施步驟：
1. 建置單執行緒排程器
- 實作細節：管理 IEnumerator 與時間，避免 Thread 炸裂。
- 所需資源：Case #1 基礎
- 預估時間：1 天

2. 加入分區任務平行化
- 實作細節：將網格切塊，以 Task/ThreadPool 平行計算 next buffer。
- 所需資源：TPL、Parallel.For
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public sealed class Scheduler
{
    private readonly SortedSet<ScheduledItem> _queue = new(...); // 依到期時間排序
    public void Add(IActor actor) { Schedule(actor.Run().GetEnumerator(), DateTime.UtcNow); }
    public void Run(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var now = DateTime.UtcNow;
            var item = _queue.Min; if (item == null || item.DueTime > now) { Thread.Sleep(1); continue; }
            _queue.Remove(item);
            if (item.Enumerator.MoveNext())
                Schedule(item.Enumerator, now + item.Enumerator.Current);
        }
    }
}
```

實際案例：對應作者「不能每個細胞開一個 thread」的顧慮與建議。
實作環境：.NET 6+/C# 10
實測數據：
改善前：大量 Thread、切換開銷高。
改善後：少數工作緒 + 協作程序，CPU 利用率更集中。
改善幅度：未提供量化數據。

Learning Points
核心知識點：
- 協作式排程 vs OS Thread
- TPL/ThreadPool 正確使用
- 演算法複雜度（heap O(log N)）
技能要求：
- 必備：Task/ThreadPool、基本同步概念
- 進階：自訂排程器、負載分攤
延伸思考：
- 適用於高數量 Actor 的遊戲/模擬
- 風險：排程器為單點，需監控與 fail-fast
- 優化：work-stealing、分層排程

Practice Exercise
基礎：以單執行緒排程 N=10k Actor
進階：加上分區平行計算 next buffer
專案：量測不同網格大小下的 CPU/延遲

Assessment Criteria
功能完整性：不以 Thread-per-cell 實作且運作穩定
程式碼品質：清楚的排程邏輯與同步邊界
效能優化：Thread 數可控、吞吐良好
創新性：自訂排程策略



## Case #4: UI 與模擬引擎的徹底解耦（Console 優先）

### Problem Statement（問題陳述）
業務場景：畫面處理往往淹沒核心邏輯，使初期架構難以聚焦。作者刻意選 Console 範例以免畫面碼干擾架構。
技術挑戰：確保渲染、輸入、模擬引擎三者解耦，便於替換 UI。
影響範圍：架構清晰度、可測性、可移植性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. UI 事件驅動與模擬步進耦合。
2. 渲染邏輯混入狀態更新。
3. 無適配層導致替換困難。
深層原因：
- 架構層面：缺少 Ports & Adapters。
- 技術層面：缺少穩定抽象（Renderer/Simulator）。
- 流程層面：過早優化 UI。

### Solution Design（解決方案設計）
解決策略：定義 ISimulationRenderer 與 ISimulator，採取 ConsoleRenderer 作為第一個 Adapter，核心引擎不依賴任何 UI 框架。

實施步驟：
1. 定義界面與模型
- 實作細節：ISimulator.Step()；ISimulationRenderer.Render(snapshot)
- 所需資源：介面、DTO
- 預估時間：0.5 天

2. Console 渲染器實作
- 實作細節：將 bool[,] 繪製成字元陣列，避免閃爍。
- 所需資源：Console API
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public interface ISimulator { bool[,] Snapshot(); void StepOnce(); }
public interface ISimulationRenderer { void Render(bool[,] snapshot); }

public sealed class ConsoleRenderer : ISimulationRenderer
{
    public void Render(bool[,] snapshot)
    {
        Console.SetCursorPosition(0, 0);
        // 快速組字串，減少 Console I/O 次數
        var sb = new StringBuilder();
        for (int y=0; y<snapshot.GetLength(0); y++)
        {
            for (int x=0; x<snapshot.GetLength(1); x++)
                sb.Append(snapshot[y, x] ? '■' : ' ');
            sb.AppendLine();
        }
        Console.Write(sb.ToString());
    }
}
```

實際案例：對應作者刻意挑選 console-based 範例避免 UI 影響。
實作環境：.NET 6+ Console
實測數據：未提供；定性上提高模組化與測試性。

Learning Points
核心知識點：
- Ports & Adapters/Hexagonal 架構
- UI 與引擎的間接層
- 快照渲染策略
技能要求：
- 必備：介面、Console I/O
- 進階：雙向繪圖緩存避免閃爍
延伸思考：
- 之後可替換為 WPF/WinUI/Blazor
- 風險：快照過大影響 I/O
- 優化：只渲染差異區塊

Practice Exercise
基礎：製作簡單 ConsoleRenderer
進階：加入差異渲染
專案：替換 UI 到 WPF 而不改引擎

Assessment Criteria
功能完整性：UI 可替換且引擎獨立
程式碼品質：界面設計清晰
效能優化：Console I/O 次數控制
創新性：抽象層設計



## Case #5: 以雙緩衝避免讀寫衝突的狀態污染

### Problem Statement（問題陳述）
業務場景：同一輪步進中，需要依據當前快照計算下一狀態，若就地修改，將造成規則提前生效，結果錯誤。
技術挑戰：確保所有更新依據同一「上一輪快照」完成，並在最後一次性交換。
影響範圍：正確性、可重現性、並行安全。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 原地更新破壞「同輪」一致性。
2. 鄰居讀到已更新值，產生鏈式誤算。
3. 多執行緒下資料競爭。
深層原因：
- 架構層面：缺少狀態版本化策略。
- 技術層面：省略雙緩衝/快照。
- 流程層面：未設計明確的步進階段。

### Solution Design（解決方案設計）
解決策略：使用 current/next 兩個緩衝區，所有計算寫入 next，完成後進行指標交換；並在計算過程只讀 current 的快照。

實施步驟：
1. 設計狀態容器
- 實作細節：bool[,] current/next；StageNext/Swap
- 所需資源：封裝類別
- 預估時間：0.5 天

2. 整合 Actor 寫入 next
- 實作細節：Cell 只能呼叫 StageNext，禁止寫 current
- 所需資源：API 設計
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public sealed class Grid
{
    public bool[,] Current { get; private set; }
    private bool[,] _next;

    public void StageNext(Point p, bool alive) => _next[p.Y, p.X] = alive;

    public void Swap()
    {
        var tmp = Current;
        Current = _next;
        _next = tmp;
        Array.Clear(_next, 0, _next.Length);
    }

    public int CountAliveNeighborsSnapshot(Point p) => NeighborUtil.CountAlive(Current, p);
}
```

實際案例：對應本文「下一次狀態」的時間步進特性。
實作環境：.NET 6+
實測數據：未提供；正確性由設計保障。

Learning Points
核心知識點：
- 狀態版本化/快照
- 原子交換 vs 原地更新
- 多執行緒中的一致性邊界
技能要求：
- 必備：陣列/記憶體操作
- 進階：False sharing/快取友善佈局
延伸思考：
- 大網格可分塊雙緩衝
- 風險：清空 next 帶來成本
- 優化：位元壓縮、差異化清理

Practice Exercise
基礎：完成 Swap 機制
進階：度量不同網格大小下的 Swap 成本
專案：分塊雙緩衝 + 平行計算整合

Assessment Criteria
功能完整性：更新規則正確、無污染
程式碼品質：狀態 API 清晰
效能優化：Swap 開銷可控
創新性：差異清空策略



## Case #6: 用迭代器封裝鄰居枚舉，降低邊界錯誤

### Problem Statement（問題陳述）
業務場景：生命遊戲需頻繁取得 8 鄰居，重複寫 for 迴圈易出錯且難以重用，若日後切換邊界策略（捲繞/裁切）更易失誤。
技術挑戰：封裝鄰居枚舉，提升可讀性並便於替換策略。
影響範圍：可維護性、正確性、抽象重用。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 重複的索引計算與邊界檢查。
2. 魔術數字與座標處理分散。
3. 切換策略需全域修改。
深層原因：
- 架構層面：缺乏鄰居策略抽象。
- 技術層面：未善用 yield 封裝序列。
- 流程層面：程式碼重複無單一來源。

### Solution Design（解決方案設計）
解決策略：建置 NeighborProvider，提供 IEnumerable<Point> Neighbors(Point p)；透過不同實作支援捲繞或裁切。

實施步驟：
1. 實作枚舉器
- 實作細節：yield return 每個合法鄰居
- 所需資源：C# yield
- 預估時間：0.5 天

2. 整合規則計算
- 實作細節：規則端只關心序列，不處理邊界
- 所需資源：抽象注入
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public static IEnumerable<Point> NeighborsWrapped(Point p, int width, int height)
{
    for (int dy=-1; dy<=1; dy++)
        for (int dx=-1; dx<=1; dx++)
            if (dx != 0 || dy != 0)
                yield return new Point((p.X + dx + width) % width, (p.Y + dy + height) % height);
}
```

實際案例：配合作者目標「程式結構不要亂」。
實作環境：.NET 6+
實測數據：未提供；錯誤率可望下降。

Learning Points
核心知識點：
- 邊界策略抽象
- yield 封裝迭代邏輯
- 關注點分離
技能要求：
- 必備：基礎集合/yield
- 進階：策略切換注入
延伸思考：
- 支援 Hex 網格、不同近鄰定義
- 風險：頻繁 yield 之效能
- 優化：預先快取鄰居表

Practice Exercise
基礎：實作裁切式 Neighbors
進階：以策略注入規則模組
專案：支援多種網格拓樸

Assessment Criteria
功能完整性：鄰居枚舉正確
程式碼品質：無魔術數字、可讀
效能優化：避免多餘裝箱
創新性：拓樸擴充性



## Case #7: 規則策略化，支援不同細胞自動機

### Problem Statement（問題陳述）
業務場景：除了康威規則，可能需要調整鄰居閾值或嘗試變體。硬編碼規則導致修改成本高、測試困難。
技術挑戰：將規則獨立為可替換策略。
影響範圍：擴充性、測試性、實驗效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 規則寫死在 Cell 內。
2. 測試需改動核心碼。
3. 難以比較不同規則結果。
深層原因：
- 架構層面：缺少策略模式
- 技術層面：規則與狀態耦合
- 流程層面：實驗流程不友善

### Solution Design（解決方案設計）
解決策略：定義 IRule.Apply(aliveCount, isAlive) => bool 作為策略，注入 Cell 或 Simulator，支援熱替換以便測試。

實施步驟：
1. 定義與實作策略
- 實作細節：ConwayRule、HighLifeRule 等
- 所需資源：介面、DI
- 預估時間：0.5 天

2. 接線注入
- 實作細節：Cell/Evaluator 注入 IRule
- 所需資源：建構子注入
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public interface IRule { bool Next(int aliveCount, bool isAlive); }
public sealed class ConwayRule : IRule
{
    public bool Next(int n, bool alive)
        => (alive && (n == 2 || n == 3)) || (!alive && n == 3);
}
```

實際案例：呼應作者「設計案例」與 OOP 應用。
實作環境：.NET 6+
實測數據：未提供；變體比較更容易。

Learning Points
核心知識點：
- 策略模式
- 輕量 DI
- 可測性提升
技能要求：
- 必備：介面/注入
- 進階：在 UI 上熱切換策略
延伸思考：
- 多規則混合（區域異質）
- 風險：策略炸裂，可參數化
- 優化：規則參數化組態

Practice Exercise
基礎：實作 ConwayRule
進階：新增 HighLife（B36/S23）
專案：規則可組態（JSON）

Assessment Criteria
功能完整性：策略可替換、結果正確
程式碼品質：依賴倒置、易讀
效能優化：策略呼叫開銷低
創新性：規則參數化



## Case #8: 穩定步進與時間漂移控制（real-time vs sim-time）

### Problem Statement（問題陳述）
業務場景：模擬需每隔固定時間步進。若單純以 Thread.Sleep 控制，會因處理時間與排程延遲造成漂移。
技術挑戰：使步進對齊理想時間軸，控制漂移累積。
影響範圍：視覺穩定、重現性、互動體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Sleep 未扣除已花費時間。
2. GC/排程延遲未補償。
3. 變動工時導致累積誤差。
深層原因：
- 架構層面：缺少時間源與步進政策
- 技術層面：未使用 Stopwatch 與 deadline 方式
- 流程層面：未定義 real-time/sim-time 優先順序

### Solution Design（解決方案設計）
解決策略：以 Stopwatch 追蹤時間，對每一 tick 計算目標 deadline；迴圈中用「剩餘時間」Sleep/Delay，並在長時間延遲時採取跳幀或補幀政策。

實施步驟：
1. 建立 TickLoop
- 實作細節：for(tick++) 計算 nextDeadline
- 所需資源：Stopwatch
- 預估時間：0.5 天

2. 漂移策略
- 實作細節：遲到超過閾值時捨棄渲染或補步進
- 所需資源：策略參數
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var sw = Stopwatch.StartNew();
var tick = 0;
var period = TimeSpan.FromMilliseconds(100);
while (running)
{
    var deadline = period * (tick + 1);
    simulator.StepOnce();
    var remaining = deadline - sw.Elapsed;
    if (remaining > TimeSpan.Zero) Thread.Sleep(remaining);
    else { /* 遲到：記錄/跳幀等策略 */ }
    tick++;
}
```

實際案例：對應作者強調「下一次狀態」與實時模擬。
實作環境：.NET 6+
實測數據：未提供；漂移期望顯著降低。

Learning Points
核心知識點：
- deadline-based scheduling
- real-time vs sim-time 抉擇
- 跳幀/補幀策略
技能要求：
- 必備：Stopwatch、時間運算
- 進階：自適應策略
延伸思考：
- 與 Case #3 的排程器整合
- 風險：過度補幀造成負載堆積
- 優化：動態步進時間

Practice Exercise
基礎：實作固定 100ms 步進
進階：測漂移並記錄
專案：加入跳幀/補幀策略

Assessment Criteria
功能完整性：步進頻率穩定
程式碼品質：時間計算清晰
效能優化：Sleep/計算比例合適
創新性：自適應時間策略



## Case #9: 網格分塊並行，提升多核利用

### Problem Statement（問題陳述）
業務場景：大型網格（如 2k x 2k）下，單執行緒遍歷計算成本高。需要在保證一致性的前提下利用多核。
技術挑戰：如何安全切塊、避免跨區域寫入衝突、維持雙緩衝正確性。
影響範圍：吞吐、延遲、CPU 利用率。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單執行緒無法吃滿 CPU。
2. 不當平行導致資料競爭。
3. 邊界區域需要正確讀快照。
深層原因：
- 架構層面：缺少分塊與同步邊界設計。
- 技術層面：平行寫入 next 的競爭未隔離。
- 流程層面：缺少工序（計算→交換）的屏障。

### Solution Design（解決方案設計）
解決策略：以雙緩衝為前提，將網格切為非重疊分塊。每個分塊只寫入 next 中自己的區域。使用 Parallel.For 或 Task 並在結束後使用 Barrier/CountdownEvent 進行同步，再做 Swap。

實施步驟：
1. 分塊策略
- 實作細節：Block[y, x] 指派給工作
- 所需資源：區塊規劃
- 預估時間：0.5 天

2. 平行與屏障
- 實作細節：Parallel.ForEach(blocks, ComputeBlock); 完成後 Swap
- 所需資源：TPL、Barrier
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
Parallel.For(0, blocks.Count, i =>
{
    var b = blocks[i];
    for (int y=b.Y0; y<b.Y1; y++)
      for (int x=b.X0; x<b.X1; x++)
      {
          var p = new Point(x,y);
          var n = NeighborUtil.CountAlive(grid.Current, p);
          grid.StageNext(p, rule.Next(n, grid.Current[p]));
      }
});
// 全部分塊完成後
grid.Swap();
```

實際案例：回應作者「並行問題適合多執行緒，但要避免資源耗盡」。
實作環境：.NET 6+、TPL
實測數據：未提供；多核可見提升。

Learning Points
核心知識點：
- 資料分區與無共享寫入
- Barrier/同步點
- 快照讀/寫隔離
技能要求：
- 必備：Parallel.For、避免共享寫
- 進階：分塊大小與 CPU cache 友善
延伸思考：
- Work-stealing、動態負載平衡
- 風險：小區塊造成調度開銷
- 優化：熱區優先、動態分割

Practice Exercise
基礎：對 512x512 進行分塊平行
進階：測不同分塊大小的效能
專案：實作動態熱區切塊

Assessment Criteria
功能完整性：結果與單執行緒一致
程式碼品質：清楚分塊界線
效能優化：CPU 利用率提升
創新性：動態負載策略



## Case #10: 以協作程序化簡除錯流程

### Problem Statement（問題陳述）
業務場景：傳統主迴圈交錯邏輯使逐步除錯困難。團隊希望能針對單一細胞逐步執行與觀察其演化。
技術挑戰：提供可針對單一 Actor 的 step-by-step 調試能力。
影響範圍：除錯效率、教學與示範、缺陷定位速度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 控制流交錯難以設置中斷點。
2. 狀態來源分散。
3. 無法重現單體行為。
深層原因：
- 架構層面：缺乏行為單元邊界。
- 技術層面：未使用可續行的枚舉器。
- 流程層面：除錯過程不友善。

### Solution Design（解決方案設計）
解決策略：每個 Cell 的 Run() 提供 IEnumerator；測試/除錯時可單獨 MoveNext() 推進，觀察 StageNext 的輸出，並用小型快照替換整體網格。

實施步驟：
1. 暴露可測 API
- 實作細節：CellTester 接收 IActor，回傳每步輸出
- 所需資源：測試輔助類別
- 預估時間：0.5 天

2. 除錯腳手架
- 實作細節：在 MoveNext 前後打印
- 所需資源：記錄器
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public sealed class ActorStepper
{
    private readonly IEnumerator<TimeSpan> _it;
    public ActorStepper(IActor actor) => _it = actor.Run().GetEnumerator();
    public bool StepOnce() => _it.MoveNext(); // 可在此下斷點，觀察 Grid.StageNext 的效果
}
```

實際案例：呼應「write only code 難以維護/除錯」。
實作環境：.NET 6+
實測數據：未提供；除錯可觀性大幅提升。

Learning Points
核心知識點：
- 協作程序的可觀測性
- 單體行為重現
- 測試鉤子的設計
技能要求：
- 必備：迭代器、單元測試
- 進階：可視化除錯工具
延伸思考：
- 將步進事件輸出到 UI
- 風險：測試鉤子污染生產碼
- 優化：條件編譯/DI 注入 logger

Practice Exercise
基礎：對單一 Cell 逐步推進三次
進階：在每次 Step 記錄鄰居與結果
專案：建置簡易可視化步進工具

Assessment Criteria
功能完整性：可單步與觀察
程式碼品質：測試輔助隔離清楚
效能優化：除錯模式可關閉
創新性：可視化思路



## Case #11: 用優先佇列管理不同喚醒時間（min-heap）

### Problem Statement（問題陳述）
業務場景：不同 Actor 有不同喚醒時間。若每輪掃描所有 Actor 判斷是否到期，成本為 O(N)。
技術挑戰：以 O(log N) 管理下一個到期的任務。
影響範圍：排程效能、延遲穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 逐一掃描成本高。
2. Actor 數量大造成延遲抖動。
3. 無法準確把握「最早到期」。
深層原因：
- 架構層面：缺乏事件時間序結構。
- 技術層面：未使用 heap/SortedSet。
- 流程層面：排程邏輯與時間混雜。

### Solution Design（解決方案設計）
解決策略：使用 min-heap（或 SortedSet）儲存（DueTime, Enumerator），每次取最小者執行；MoveNext 後再依 yield 的 TimeSpan 入堆。

實施步驟：
1. 定義 ScheduledItem
- 實作細節：IComparable by DueTime
- 所需資源：SortedSet/Heap
- 預估時間：0.5 天

2. 排程主迴圈
- 實作細節：取堆頂、執行、重排程
- 所需資源：計時
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
record ScheduledItem(DateTime DueTime, IEnumerator<TimeSpan> Enumerator);
var queue = new SortedSet<ScheduledItem>(Comparer<ScheduledItem>.Create(
    (a,b) => a.DueTime != b.DueTime ? a.DueTime.CompareTo(b.DueTime) : a.GetHashCode().CompareTo(b.GetHashCode())));
```

實際案例：呼應「時間步進與不同節奏」的需求。
實作環境：.NET 6+
實測數據：未提供；理論複雜度降低。

Learning Points
核心知識點：
- 優先佇列
- 事件排程
- 時間複雜度分析
技能要求：
- 必備：資料結構/比較器
- 進階：自製二元堆
延伸思考：
- 大規模 Actor 的 GC 壓力
- 風險：相同 DueTime 比較衝突
- 優化：群組執行同到期 Actor

Practice Exercise
基礎：排程 1k Actor，確保順序正確
進階：測 O(N) 掃描 vs heap 的差異
專案：加入群組執行與批次處理

Assessment Criteria
功能完整性：到期順序正確
程式碼品質：比較器正確、無碰撞
效能優化：明顯優於 O(N) 掃描
創新性：群組化策略



## Case #12: 正確的同步點與資料競爭防護

### Problem Statement（問題陳述）
業務場景：多執行緒計算 next buffer 時，若跨分塊寫入或在 Swap 前後競爭，會出現資料競賽與破壞一致性。
技術挑戰：定義清晰的同步點與臨界區。
影響範圍：正確性、穩定性、避免偶發 bug。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 同輪寫入 next 衝突。
2. Swap 與寫入同時進行。
3. 鄰居讀取跨緩衝。
深層原因：
- 架構層面：缺同步階段定義。
- 技術層面：Barrier 使用不當。
- 流程層面：無「計算→同步→交換」工序。

### Solution Design（解決方案設計）
解決策略：嚴格三階段：讀 current 計算 → 全部完成 → Swap。以 CountdownEvent/Barrier 確保所有任務完成後再交換。

實施步驟：
1. 任務劃分與同步
- 實作細節：CountdownEvent 初始為工作數
- 所需資源：System.Threading
- 預估時間：0.5 天

2. 原子交換
- 實作細節：所有工作完成後，單執行緒呼叫 Swap
- 所需資源：Grid.Swap()
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var done = new CountdownEvent(blocks.Count);
foreach (var b in blocks) Task.Run(() => { ComputeBlock(b); done.Signal(); });
done.Wait(); // 所有寫入 next 的工作完成
grid.Swap();
```

實際案例：與 Case #5/#9 搭配確保一致性。
實作環境：.NET 6+
實測數據：未提供；正確性提升。

Learning Points
核心知識點：
- Barrier/CountdownEvent
- 工序同步化
- 避免讀寫交疊
技能要求：
- 必備：同步原語
- 進階：不可變快照
延伸思考：
- 以 Channel 化流水線
- 風險：死鎖/饑餓
- 優化：批次同步減少阻塞

Practice Exercise
基礎：以 CountdownEvent 管控兩個工作
進階：將分塊計算接入同步點
專案：以 Channel 實作三階段流水線

Assessment Criteria
功能完整性：無競爭且結果一致
程式碼品質：同步點清晰
效能優化：阻塞時間可控
創新性：管線化思路



## Case #13: 可中止與資源釋放（CancellationToken）

### Problem Statement（問題陳述）
業務場景：模擬需支持暫停/停止，否則可能導致資源（工作緒、排程器）無法回收或產生不一致狀態。
技術挑戰：讓排程器與工作安全地觀察取消並釋放資源。
影響範圍：穩定性、可操作性、測試流程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無取消機制。
2. 工作緒可能卡住或無法退出。
3. 資源（計時器、列舉器）未釋放。
深層原因：
- 架構層面：缺少生命週期管理。
- 技術層面：未使用 CancellationToken。
- 流程層面：關閉流程未定義。

### Solution Design（解決方案設計）
解決策略：排程器主迴圈接收 CancellationToken；Actor/工作在合適點檢查 Token；所有可釋放資源實作 IDisposable。

實施步驟：
1. 令牌串接
- 實作細節：Run(ct) 中檢查 ct.IsCancellationRequested
- 所需資源：CancellationTokenSource
- 預估時間：0.5 天

2. 資源釋放
- 實作細節：列舉器/Timer 於 finally 中 Dispose
- 所需資源：IDisposable
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
using var cts = new CancellationTokenSource();
var task = Task.Run(() => scheduler.Run(cts.Token));
Console.ReadKey();
cts.Cancel();
task.Wait();
```

實際案例：符合作者對穩健多執行緒的要求。
實作環境：.NET 6+
實測數據：未提供；關閉流程可靠。

Learning Points
核心知識點：
- 取消模型
- 資源生命週期
- 可預期關閉
技能要求：
- 必備：CancellationToken
- 進階：可中斷等待（WaitHandle）
延伸思考：
- 超時取消
- 風險：不回應取消導致卡死
- 優化：中斷點設計

Practice Exercise
基礎：在 3 秒後取消排程器
進階：Actor 尊重取消（在 yield 前檢查）
專案：UI 綁定取消/恢復

Assessment Criteria
功能完整性：可可靠停止
程式碼品質：IDisposable 正確
效能優化：關閉耗時小
創新性：恢復與續跑設計



## Case #14: Timer/Task.Delay 驅動的替代型排程

### Problem Statement（問題陳述）
業務場景：不想自建時間輪迴圈，可用 .NET Timer/Task.Delay 實作簡化版排程。但需避免大量定時器造成壓力。
技術挑戰：平衡定時器數量與準確性。
影響範圍：複雜度、維護成本、資源使用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 大量 Timer 會造成回呼壅塞。
2. Timer 精度有限。
3. 難以集中協調。
深層原因：
- 架構層面：分散式時間源
- 技術層面：忽視 Timer 限制
- 流程層面：缺少聚合層

### Solution Design（解決方案設計）
解決策略：使用單一高精度 loop 搭配 Task.Delay，或使用少量 Timer 群組處理；避免 per-cell 一個 Timer；Actor 仍以 coroutine 表達。

實施步驟：
1. 單一 Task.Delay 迴圈
- 實作細節：await Task.Delay(粒度) + 執行 due actor
- 所需資源：async/await
- 預估時間：0.5 天

2. 群組化
- 實作細節：將相近到期的 Actor 批次執行
- 所需資源：batching
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
while (!ct.IsCancellationRequested)
{
    var due = scheduler.DrainDue(DateTime.UtcNow); // 取出到期批次
    foreach (var it in due) it.MoveNext();
    await Task.Delay(TimeSpan.FromMilliseconds(5), ct);
}
```

實際案例：對應作者「多執行緒技巧」但避免過度。
實作環境：.NET 6+
實測數據：未提供；複雜度下降。

Learning Points
核心知識點：
- async 驅動輪詢
- Timer 精度認知
- 批次排程
技能要求：
- 必備：async/await
- 進階：取消傳遞
延伸思考：
- 高負載時的批次大小
- 風險：延遲顫動
- 優化：自動調整粒度

Practice Exercise
基礎：以 Task.Delay 驅動 100 個 Actor
進階：批次化處理到期 Actor
專案：比較 heap+sleep vs delay 的抖動

Assessment Criteria
功能完整性：到期執行正確
程式碼品質：async 錯誤處理
效能優化：適當粒度
創新性：批次策略



## Case #15: 建立模式樣例測試（blinker、glider）

### Problem Statement（問題陳述）
業務場景：需驗證規則實作正確，並能以固定種子重現結果。經典樣例如 blinker、glider 可作為回歸測試。
技術挑戰：構造初始狀態、跑固定步數、比對快照。
影響範圍：品質保證、回歸信心、教學示範。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無基準測試，改動後無法確信正確。
2. 不易重現錯誤。
3. 測試資料散亂。
深層原因：
- 架構層面：缺少測試點與快照 API。
- 技術層面：未序列化/比對快照。
- 流程層面：缺少回歸測試文化。

### Solution Design（解決方案設計）
解決策略：提供載入/序列化快照能力；建立多個經典模式案例與期望快照；自動跑 N 步後比對。

實施步驟：
1. 快照序列化
- 實作細節：bool[,] <-> string/List<Point>
- 所需資源：序列化工具
- 預估時間：0.5 天

2. 測試案例集
- 實作細節：blinker 2 步循環、glider 斜移
- 所需資源：單元測試框架
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
[Fact]
public void Blinker_Oscillates()
{
    var grid = TestGrids.Blinker();
    var sim  = new Simulator(grid, new ConwayRule());
    var s0 = sim.Snapshot();
    sim.StepOnce(); var s1 = sim.Snapshot();
    sim.StepOnce(); var s2 = sim.Snapshot();
    Assert.True(Snapshot.Equals(s0, s2));
}
```

實際案例：對應作者關注「教學案例」的方向。
實作環境：.NET 6+、xUnit/NUnit
實測數據：未提供；回歸保障。

Learning Points
核心知識點：
- 基準樣例、可重現性
- 快照比對
- 單元測試實務
技能要求：
- 必備：單元測試
- 進階：測試資料生成
延伸思考：
- 隨機種子測試
- 風險：快照比對成本
- 優化：哈希摘要比對

Practice Exercise
基礎：撰寫 blinker 測試
進階：撰寫 glider 位移測試
專案：建立 10 個模式回歸集

Assessment Criteria
功能完整性：測試涵蓋典型模式
程式碼品質：測試可讀、資料化
效能優化：快照比對高效
創新性：自動生成測例



## Case #16: 配置管理與可調參數化（大小、節奏、邊界）

### Problem Statement（問題陳述）
業務場景：不同實驗需不同網格大小、步進時間、邊界策略、規則。硬編碼不利於調整與試驗。
技術挑戰：將重要參數外部化且熱可讀。
影響範圍：實驗效率、部署便利、可重現性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 常數散落程式中。
2. 變更需重新編譯。
3. 難以記錄試驗配置。
深層原因：
- 架構層面：缺少配置層
- 技術層面：未使用 Options/Binding
- 流程層面：試驗記錄不足

### Solution Design（解決方案設計）
解決策略：建立 SimulationOptions（大小、period、邊界、規則），支援 JSON/命令列注入；引擎只依賴 Options 而非常數。

實施步驟：
1. 建立 Options
- 實作細節：POCO + JSON 綁定
- 所需資源：System.Text.Json
- 預估時間：0.5 天

2. 注入與驗證
- 實作細節：建構子注入 Options，啟動時驗證
- 所需資源：DI
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public sealed class SimulationOptions
{
    public int Width { get; init; } = 80;
    public int Height { get; init; } = 25;
    public int TickMs { get; init; } = 100;
    public string Boundary { get; init; } = "Wrapped"; // or Clamped
    public string Rule { get; init; } = "Conway";
}
```

實際案例：對應作者想做「設計案例」與可擴充方向。
實作環境：.NET 6+
實測數據：未提供；實驗效率提升。

Learning Points
核心知識點：
- Options 模式
- 組態即文件
- 可重現試驗設定
技能要求：
- 必備：JSON/命令列參數
- 進階：熱載入/驗證
延伸思考：
- 多檔合併、環境變數覆寫
- 風險：配置不一致
- 優化：Schema 驗證

Practice Exercise
基礎：從 JSON 載入大小與 Tick
進階：命令列覆寫配置
專案：UI 顯示當前配置並可熱調整

Assessment Criteria
功能完整性：配置可影響行為
程式碼品質：Options 注入清晰
效能優化：讀取負擔低
創新性：熱載入機制



## Case #17: 以記錄/診斷改善「古典程式」可觀測性

### Problem Statement（問題陳述）
業務場景：傳統 C/Java 習寫法缺乏診斷鉤子。現代化重構後需建立可觀測性，以利定位效能/正確性問題。
技術挑戰：在不干擾核心邏輯的情況下，收集關鍵指標。
影響範圍：維運、除錯、優化決策。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少統一記錄策略。
2. 無指標（tick 耗時、更新數量）。
3. 問題難重現。
深層原因：
- 架構層面：未預留診斷通道。
- 技術層面：沒有事件/度量上報。
- 流程層面：缺乏監控流程。

### Solution Design（解決方案設計）
解決策略：引擎暴露事件（OnTick, OnSwap, OnChunkCompleted），收集 tick 耗時、更新數量、渲染時間；以簡易 logger 或 EventSource 輸出。

實施步驟：
1. 度量點定義
- 實作細節：Stopwatch 包住 Step/Render
- 所需資源：計時器、事件
- 預估時間：0.5 天

2. 日誌/事件匯出
- 實作細節：ILogger/EventSource
- 所需資源：內建記錄
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public event Action<TickMetrics>? OnTick;
public void StepOnce()
{
    var sw = Stopwatch.StartNew();
    ComputeNext();
    grid.Swap();
    OnTick?.Invoke(new TickMetrics(sw.Elapsed, _updatedCount));
}
```

實際案例：對應作者「用現代技術提升效益」的訴求。
實作環境：.NET 6+、ILogger
實測數據：未提供；可據以量測。

Learning Points
核心知識點：
- 可觀測性設計
- 指標選型與收集
- 事件化架構
技能要求：
- 必備：Stopwatch、事件
- 進階：EventSource/ETW
延伸思考：
- 導出到 Prometheus
- 風險：過度紀錄影響效能
- 優化：抽樣與節流

Practice Exercise
基礎：記錄每 tick 耗時
進階：統計每 tick 更新的細胞數
專案：提供簡易效能儀表板

Assessment Criteria
功能完整性：指標可用
程式碼品質：記錄與業務分離
效能優化：記錄開銷可控
創新性：觀測與策略聯動



## Case #18: 以分層/模組化結構重寫「Java 版 C 程式」

### Problem Statement（問題陳述）
業務場景：現存範例多為程序式、單檔、難以擴充。需要以現代 .NET/C# 的分層/模組化方式重構，以便後續加入多執行緒與策略。
技術挑戰：定義清晰模組邊界（引擎、規則、排程、渲染、配置）。
影響範圍：架構穩健性、團隊協作、長期維護。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 程式碼單體化。
2. 關注點混雜。
3. 測試困難。
深層原因：
- 架構層面：缺乏分層與接口
- 技術層面：未採用現代語言特性
- 流程層面：無模組邊界規範

### Solution Design（解決方案設計）
解決策略：定義核心模組（Grid、Rule、Scheduler、Simulator、Renderer、Options），各自獨立測試；以接口連接，支援替換與擴充。

實施步驟：
1. 模組劃分
- 實作細節：專案資料夾與命名空間
- 所需資源：解決方案結構
- 預估時間：0.5 天

2. 介面設計
- 實作細節：IGrid、IRule、IScheduler、ISimulator
- 所需資源：C# interface
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 模組邊界（示意）
public interface ISimulator { void StepOnce(); bool[,] Snapshot(); }
public interface IScheduler { void Add(IActor a); void Run(CancellationToken ct); }
```

實際案例：對應作者對「Java 版 C 程式碼」的反思與現代化。
實作環境：.NET 6+
實測數據：未提供；結構清晰度提升。

Learning Points
核心知識點：
- 分層與關注點分離
- 介面導向設計
- 可替換與測試
技能要求：
- 必備：模組化/命名空間
- 進階：契約測試
延伸思考：
- 以 NuGet 套件化模組
- 風險：過度抽象
- 優化：從用例驅動抽象

Practice Exercise
基礎：拆出 Rule/Renderer 模組
進階：為 Scheduler 撰寫契約測試
專案：以套件方式重用模組

Assessment Criteria
功能完整性：模組獨立可替換
程式碼品質：耦合度低、清晰
效能優化：抽象開銷可接受
創新性：模組化發布



-----------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #4（UI 解耦）
  - Case #6（鄰居迭代器）
  - Case #10（協作程序除錯）
  - Case #15（樣例測試）
  - Case #16（配置管理）

- 中級（需要一定基礎）
  - Case #1（yield 協作程序）
  - Case #2（多型頻率）
  - Case #5（雙緩衝）
  - Case #7（規則策略）
  - Case #8（時間漂移控制）
  - Case #11（min-heap 排程）
  - Case #12（同步點防護）
  - Case #14（Task.Delay 排程）
  - Case #18（模組化重構）

- 高級（需要深厚經驗）
  - Case #3（避免 thread explosion）
  - Case #9（分塊並行與快取友善）

2. 按技術領域分類
- 架構設計類：#4, #7, #16, #18
- 效能優化類：#3, #5, #8, #9, #11, #12, #14
- 整合開發類：#2, #4, #16, #18
- 除錯診斷類：#1, #6, #10, #15, #17
- 安全防護類（並行安全/資源安全視為廣義安全）：#5, #12, #13

3. 按學習目標分類
- 概念理解型：#1, #2, #4, #7, #18
- 技能練習型：#5, #6, #8, #11, #14, #16
- 問題解決型：#3, #9, #12, #13, #15
- 創新應用型：#10, #17

-----------------------------
案例關聯圖（學習路徑建議）

- 先學哪些？
  - 基礎抽象與結構：Case #4（UI 解耦）→ #6（鄰居迭代器）→ #5（雙緩衝）
  - 行為建模：Case #1（yield 協作程序）→ #2（多型頻率）→ #7（規則策略）→ #16（配置）

- 依賴關係
  - #1 依賴 #4 的關注點分離概念
  - #2 依賴 #1 的行為建模與排程對接
  - #5 是 #9、#12 的前置（並行前必須保證一致性）
  - #8、#11、#14 與 #1/#2 的排程模型互補（時間控制與到期管理）
  - #3、#9 建立在 #1/#5/#11 之上（協作程序 + 雙緩衝 + 優先佇列）
  - #15 建立在 #4/#5/#7（可測快照 + 規則策略）
  - #13 橫切所有執行流（取消/釋放）
  - #17 依賴 #4/#18 的模組化，便於插入觀測鉤子
  - #18 是全局結構整合，串起前面所有抽象

- 完整學習路徑建議
  1) 結構化基礎：#4 → #6 → #5  
  2) 行為與時間建模：#1 → #2 → #7 → #8  
  3) 排程與可伸縮：#11 → #14 → #3 → #9 → #12  
  4) 工程能力補強：#16 → #15 → #13 → #17 → #18

此路徑從可讀性與正確性出發，逐步加入時間/排程與並行伸縮，最後以工程化與觀測性收束，與文章「用現代 .NET/C# 技術改寫古典生命遊戲」之主旨相符。