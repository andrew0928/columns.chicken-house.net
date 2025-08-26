以下內容根據文章中點出的主題與線索（多執行緒、Thread Sync 概念與實作、yield return 的原理與替代同步做法、GameHost/Player 誰主誰次的架構討論、猜數字比賽程式的實作）所歸納與重構，整理為可供實戰教學、專案練習與能力評估的案例。每個案例均包含問題、根因、解法、實作重點與練習評估項。

注意：文中未提供實際數據與完整程式碼，我們以可重現的教學專案方式給出可度量的指標與驗收準則，便於在你的環境中自行量測與對照。

## Case #1: 化被動為主動：以 WaitHandle 取代輪詢的多執行緒同步

### Problem Statement（問題陳述）
業務場景：在猜數字比賽的程式中，GameHost 與 Player 需交替進行回合。初版實作採用輪詢機制（Player 不斷檢查是否輪到自己行動），導致 CPU 無謂消耗且無法準確控制時序，偶發不同步、延遲累積，影響比賽迴圈效能與穩定性。
技術挑戰：如何在兩個執行緒間精準交握，消除輪詢與睡眠帶來的延遲與資源浪費？
影響範圍：高 CPU 佔用、回合切換不穩定、偶發「互等」與卡頓。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 Thread.Sleep 輪詢狀態，未使用同步基元，造成 CPU 空轉與不精確延遲。
2. 回合權限變更沒有通知機制，Player/Host 不知道何時該動作。
3. 共享旗標未做好記憶體可見性保障，造成可見性與競態問題。
深層原因：
- 架構層面：缺乏明確的回合控制與訊號模型。
- 技術層面：未善用 AutoResetEvent/ManualResetEvent/Monitor 等同步工具。
- 流程層面：缺少壓力測試與負載下的行為驗證。

### Solution Design（解決方案設計）
解決策略：用事件驅動取代輪詢。建立兩個 AutoResetEvent，分別代表 HostTurn 與 PlayerTurn；以 Set/WaitOne 準確交棒。引入記錄與超時保護，避免執行緒無限等待。

實施步驟：
1. 建立交握事件
- 實作細節：HostTurn 初值 signaled、PlayerTurn 初值 non-signaled。
- 所需資源：.NET WaitHandle、AutoResetEvent。
- 預估時間：0.5 小時
2. 替換輪詢迴圈
- 實作細節：以 WaitOne() 等待輪到自己；執行完畢後 Set() 對方事件。
- 所需資源：C# 執行緒/Task API。
- 預估時間：1 小時
3. 加入超時與日誌
- 實作細節：WaitOne(timeout) + 超時處理；紀錄狀態轉換。
- 所需資源：Stopwatch、Logging。
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// Host 與 Player 的交握
var hostTurn = new AutoResetEvent(true);
var playerTurn = new AutoResetEvent(false);
var cts = new CancellationTokenSource();

var host = new Thread(() => {
    while (!cts.IsCancellationRequested) {
        if (!hostTurn.WaitOne(TimeSpan.FromSeconds(2))) throw new TimeoutException("Host wait");
        // 評分、產出提示
        // ...
        playerTurn.Set(); // 交棒給 Player
    }
});

var player = new Thread(() => {
    while (!cts.IsCancellationRequested) {
        if (!playerTurn.WaitOne(TimeSpan.FromSeconds(2))) throw new TimeoutException("Player wait");
        // 計算下一個猜測
        // ...
        hostTurn.Set(); // 交棒給 Host
    }
});

host.Start();
player.Start();
```

實際案例：猜數字程式的回合交替（Host 判分、Player 猜測）
實作環境：C# 8+/ .NET 6+（.NET 3.5 也可用 WaitHandle）；Windows/Linux 均可
實測數據：
- 可量測指標：CPU 使用率、每回合平均延遲、最大等待時間、丟失交棒次數（應為 0）
- 目標範圍：CPU 降至低負載（<5% 基準程式）、回合切換 95p < 2ms、無超時例外

Learning Points（學習要點）
核心知識點：
- WaitHandle/AutoResetEvent 的用法與語意
- 事件驅動 vs 輪詢的差異
- 超時與錯誤處理策略
技能要求：
- 必備技能：C# 執行緒、WaitHandle API
- 進階技能：故障注入與壓測
延伸思考：
- 若有多 Player，如何擴充事件模型？
- 遇到跨程序（IPC）時如何辦？
- 是否可用 Channel/BlockingCollection 替代？
Practice Exercise（練習題）
- 基礎練習：將輪詢程式改為 AutoResetEvent 交握（30 分鐘）
- 進階練習：加入超時機制與重試策略（2 小時）
- 專案練習：完成可配置回合控制與紀錄儀表板（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：交握正確、無丟棒
- 程式碼品質（30%）：清晰、無共享狀態隱患
- 效能優化（20%）：CPU 降低、延遲穩定
- 創新性（10%）：可觀測性與擴充性設計

---

## Case #2: 互相等待的兩個執行緒：死結的協定化排除

### Problem Statement（問題陳述）
業務場景：Host 與 Player 彼此等待對方信號才動作，偶發兩邊都在 WaitOne，造成回合卡死。
技術挑戰：建立不會因初始態或競態而死結的雙向握手協定。
影響範圍：回合停滯、需要重啟才能恢復。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 初始事件狀態設錯，導致雙方同時等待。
2. 缺乏超時處理，無法及時偵測與恢復。
3. 單一事件多重語意，訊號被誤用或吞掉。
深層原因：
- 架構層面：未定義明確的角色主從與狀態機。
- 技術層面：事件選型與使用錯誤（Auto vs ManualResetEvent）。
- 流程層面：未做混沌/競態測試。

### Solution Design（解決方案設計）
解決策略：規範「單責任單向事件」與「固定初始狀態」，引入雙事件握手（A->B, B->A），所有 Wait 都有超時，並在超時時進行協調重試或重置。

實施步驟：
1. 設計雙事件握手與初始狀態
- 實作細節：HostTurn 初值 true、PlayerTurn 初值 false；只傳遞單一方向語意。
- 所需資源：AutoResetEvent
- 預估時間：0.5 小時
2. 加入超時與協調重試
- 實作細節：統一使用 WaitOne(TimeSpan)；超時則紀錄並重置信號。
- 所需資源：Logging、度量工具
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
AutoResetEvent hostTurn = new AutoResetEvent(true);
AutoResetEvent playerTurn = new AutoResetEvent(false);

bool WaitTurn(AutoResetEvent e, string who, TimeSpan timeout) {
    if (!e.WaitOne(timeout)) {
        // 記錄並嘗試恢復
        Console.Error.WriteLine($"{who} timeout; attempting recovery");
        // 恢復策略：由 Host 作為主控，重置為 HostTurn
        hostTurn.Set(); // 強制回到 Host 主導
        return false;
    }
    return true;
}
```

實際案例：猜數字回合等候死結排除
實作環境：C# / .NET 6 或 .NET Framework 3.5
實測數據：
- 可量測指標：死結次數/小時、超時次數、恢復耗時
- 目標範圍：死結 0、超時 < 0.1 次/千回合、恢復 < 10ms

Learning Points（學習要點）
核心知識點：
- AutoResetEvent vs ManualResetEvent 差異
- 初始狀態與單向語意的重要性
- 超時治理策略
技能要求：
- 必備技能：WaitHandle 運用、例外處理
- 進階技能：錯誤復原設計
延伸思考：
- 是否能以單執行緒事件迴圈避免整類問題？
- 用 Barrier 或 Channel 能否更簡單？
Practice Exercise（練習題）
- 基礎練習：雙事件握手與超時復原（30 分鐘）
- 進階練習：隨機注入延遲驗證恢復能力（2 小時）
- 專案練習：製作死結偵測與可視化儀表板（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：死結排除、可恢復
- 程式碼品質（30%）：同步清晰、無隱式共享
- 效能優化（20%）：恢復延遲可控
- 創新性（10%）：故障注入與可觀測性

---

## Case #3: 用 yield return 實作協程：以迭代器替代執行緒同步

### Problem Statement（問題陳述）
業務場景：多執行緒同步成本高、難除錯；希望在單執行緒中以協作式排程實現 Host/Player 回合。
技術挑戰：如何用 yield return 將回合邏輯拆分成可逐步執行的狀態機，並由簡易排程器交替執行？
影響範圍：降低並行複雜度、穩定回合行為、提升可測性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 使用多執行緒造成鎖與競態，難以驗證。
2. 回合序控制分散在多處，不易理清。
3. Unit Test 難以決定性重現。
深層原因：
- 架構層面：缺少單一事件迴圈式設計。
- 技術層面：未善用 yield 產生之狀態機能力。
- 流程層面：缺少可重播的測試排程。

### Solution Design（解決方案設計）
解決策略：將 Host 與 Player 各自實作 IEnumerable<Step> 或 IEnumerator，使用簡單 round-robin 調度器交替 MoveNext()；每個回合進行一步，避免鎖與 WaitHandle，讓邏輯完全決定性。

實施步驟：
1. 拆分回合為可 yield 的步驟
- 實作細節：Host()/Player() 各為 IEnumerator；每一步 yield 返回控制權。
- 所需資源：C# yield return
- 預估時間：2 小時
2. 實作簡單調度器
- 實作細節：Round-robin 呼叫 MoveNext()；完成即移除。
- 所需資源：基礎集合、迭代器
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
IEnumerable<string> Host() {
    while (true) {
        // 根據上一個猜測產生回饋
        yield return "host-step";
    }
}

IEnumerable<string> Player() {
    while (true) {
        // 產生下一個猜測
        yield return "player-step";
    }
}

void RunScheduler(params IEnumerable<string>[] coroutines) {
    var iters = new Queue<IEnumerator<string>>(coroutines.Select(c => c.GetEnumerator()));
    while (iters.Count > 0) {
        var it = iters.Dequeue();
        if (it.MoveNext()) {
            // 可在此分派事件、紀錄
            iters.Enqueue(it);
        }
    }
}
```

實際案例：用協程實作 Host/Player 回合交替
實作環境：C# 8+/ .NET 6+（不依賴 Thread/WaitHandle）
實測數據：
- 可量測指標：每回合延遲、上下文切換次數（理論 0）、測試穩定重現率
- 目標範圍：決定性 100% 可重現；回合步進 < 1ms

Learning Points（學習要點）
核心知識點：
- yield return 的協作式控制流
- 自訂調度器與狀態機思維
- 決定性測試的優勢
技能要求：
- 必備技能：yield/迭代器
- 進階技能：排程器設計、狀態機建模
延伸思考：
- 如何與 UI/IO 同步（需要事件轉接）？
- 是否可與 async/await 混合？
Practice Exercise（練習題）
- 基礎練習：寫一個兩協程交替的示例（30 分鐘）
- 進階練習：增加第三方協程（裁判/紀錄員）（2 小時）
- 專案練習：做一個可暫停/恢復/回放的協程引擎（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：交替正確
- 程式碼品質（30%）：結構清晰、可測
- 效能優化（20%）：低延遲、零鎖
- 創新性（10%）：可視化或回放功能

---

## Case #4: yield return 如何運作：從編譯器狀態機理解與重寫

### Problem Statement（問題陳述）
業務場景：學習 yield return 的底層行為，以便正確在高負載遊戲迴圈中使用。
技術挑戰：理解編譯器如何把 yield 方法轉換為狀態機，避免誤用。
影響範圍：避免記憶體滲漏、迭代器誤用造成的隱性 Bug。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 誤以為 yield 保證即時計算或快取行為。
2. 不理解 MoveNext/Current/State 的關係。
3. 在迭代器中做阻塞操作導致不可預期延遲。
深層原因：
- 架構層面：將迭代器誤作工作執行緒替代。
- 技術層面：不熟悉編譯器生成的狀態機程式碼。
- 流程層面：缺乏針對迭代器的單元測試。

### Solution Design（解決方案設計）
解決策略：以簡單範例理解 yield 生成的狀態機，並手寫等價 IEnumerator 版本，比對呼叫時序，建立正確使用準則。

實施步驟：
1. 編寫 yield 版本與手寫 IEnumerator 版本
- 實作細節：對照 MoveNext 的 state 過渡。
- 所需資源：C#、ILSpy（可選）
- 預估時間：1 小時
2. 加入測試驗證時序
- 實作細節：紀錄呼叫順序、Current 值。
- 所需資源：xUnit/NUnit
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// yield 版本
IEnumerable<int> Seq() {
    yield return 1;
    yield return 2;
    yield return 3;
}

// 等價手寫狀態機（簡化）
sealed class SeqEnum : IEnumerator<int> {
    int state = 0;
    public int Current { get; private set; }
    object IEnumerator.Current => Current;
    public bool MoveNext() {
        switch (state) {
            case 0: Current = 1; state = 1; return true;
            case 1: Current = 2; state = 2; return true;
            case 2: Current = 3; state = -1; return true;
            default: return false;
        }
    }
    public void Reset() => state = 0;
    public void Dispose() { }
}
```

實際案例：在 Host/Player 協程中避免阻塞性操作放入 yield 方法
實作環境：C# / .NET 6
實測數據：
- 可量測指標：MoveNext 平均耗時、GC 分配
- 目標範圍：每步近零分配；MoveNext < 200ns（視平台）

Learning Points（學習要點）
核心知識點：
- yield -> 狀態機
- MoveNext/Current/Dispose 契約
- 延遲序列與快取語意
技能要求：
- 必備技能：IEnumerable/IEnumerator
- 進階技能：剖析 IL/反編譯
延伸思考：
- 何時應該避免 yield？（需要同步/阻塞時）
Practice Exercise（練習題）
- 基礎練習：手寫一個三步狀態機（30 分鐘）
- 進階練習：帶條件分支的狀態機（2 小時）
- 專案練習：將小型 DSL 編譯為狀態機（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：狀態正確
- 程式碼品質（30%）：清楚、可維護
- 效能優化（20%）：低分配
- 創新性（10%）：工具化/可視化

---

## Case #5: GameHost 為主 vs Player 為主：用 Mediator 消除「誰呼叫誰」的結構糾結

### Problem Statement（問題陳述）
業務場景：Host 與 Player 相互呼叫彼此方法，容易形成循環依賴與耦合，難測試、難替換。
技術挑戰：釐清控制權與單向溝通路徑，避免雙向耦合。
影響範圍：架構脆弱、維護成本高、擴充困難。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 彼此持有對方參考，形成緊耦合。
2. 缺少明確訊息契約，呼叫語義混亂。
3. 單元測試需啟動整套依賴才可跑。
深層原因：
- 架構層面：未定義中介者（Mediator）/總線。
- 技術層面：介面設計不足、依賴反轉未落實。
- 流程層面：用例驅動不足，未抽象通用協議。

### Solution Design（解決方案設計）
解決策略：引入 Mediator，Host/Player 不直接互調；各自只對 Mediator 發訊與訂閱事件。控制權在 Host，Player 為純策略提供者。

實施步驟：
1. 定義訊息契約與介面
- 實作細節：IGameMediator、IPlayer、IGameHost
- 所需資源：C# 介面/事件
- 預估時間：1 小時
2. 實作 Mediator 並移除雙向引用
- 實作細節：透過 Mediator 路由猜測與回饋
- 所需資源：DI（可選）
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
public interface IPlayer { int NextGuess(GameState state); }
public interface IGameHost { Verdict Judge(int guess); }
public interface IGameMediator {
    Verdict SubmitGuess(IPlayer player, int guess);
}

public class GameMediator : IGameMediator {
    private readonly IGameHost _host;
    public GameMediator(IGameHost host) => _host = host;
    public Verdict SubmitGuess(IPlayer player, int guess) => _host.Judge(guess);
}
```

實際案例：猜數字：Player 只關注產生猜測；Host 控制回合並評分
實作環境：C# / .NET 6；可用 DI 容器（選用）
實測數據：
- 可量測指標：類之間耦合度、替換 Player 的時間、單元測試覆蓋率
- 目標範圍：Player 熱插拔 < 1 分鐘；測試無須啟動對方物件

Learning Points（學習要點）
核心知識點：
- Mediator/依賴反轉
- 合約驅動設計
- 可替換性與測試隔離
技能要求：
- 必備技能：介面抽象、事件
- 進階技能：DI、測試替身
延伸思考：
- 若有多 Player 競賽如何擴展？
Practice Exercise（練習題）
- 基礎練習：將雙向呼叫改為 Mediator（30 分鐘）
- 進階練習：加入記錄與重放（2 小時）
- 專案練習：支援多 Player 排程（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：無循環依賴
- 程式碼品質（30%）：低耦合、高聚合
- 效能優化（20%）：調用成本可忽略
- 創新性（10%）：可觀測性設計

---

## Case #6: 回合制請求-回應協議：用 BlockingCollection 明確化訊息流程

### Problem Statement（問題陳述）
業務場景：回合流程散落，資料傳遞沒有統一格式，造成錯誤與混亂。
技術挑戰：建立明確訊息契約與隊列，確保 Host/Player 流轉一目了然。
影響範圍：易出錯、難追蹤、難測試。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 使用共享變數傳遞資料，缺乏同步。
2. 沒有回合 ID 與關聯追蹤。
3. 異常處理與重試無標準。
深層原因：
- 架構層面：缺少消息導向的設計。
- 技術層面：未善用阻塞佇列與型別安全契約。
- 流程層面：無結構化紀錄。

### Solution Design（解決方案設計）
解決策略：用 BlockingCollection 作為單生產者/單消費者佇列，定義 Guess/Verdict 訊息，使用回合 ID 追蹤，集中協議處理與重試策略。

實施步驟：
1. 定義訊息模型與佇列
- 實作細節：record Guess、Verdict，加入 RoundId。
- 所需資源：BlockingCollection
- 預估時間：1 小時
2. 建立處理回圈
- 實作細節：Producer/Consumer 分離，集中例外處理。
- 所需資源：Task/Thread
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public record Guess(int RoundId, int Value);
public record Verdict(int RoundId, int Bulls, int Cows);

var guesses = new BlockingCollection<Guess>(new ConcurrentQueue<Guess>());
var verdicts = new BlockingCollection<Verdict>(new ConcurrentQueue<Verdict>());

// Player
Task.Run(() => {
    int round = 0;
    foreach (var g in GuessGenerator()) {
        guesses.Add(new Guess(round++, g));
    }
    guesses.CompleteAdding();
});

// Host
Task.Run(() => {
    foreach (var guess in guesses.GetConsumingEnumerable()) {
        var v = Judge(guess);
        verdicts.Add(v);
    }
    verdicts.CompleteAdding();
});
```

實際案例：統一 Host/Player 資料流，便於診斷與回放
實作環境：C# / .NET 6
實測數據：
- 可量測指標：丟訊率（0）、處理吞吐量、平均等待時間
- 目標範圍：零丟失；可支撐 >10k 回合/秒（視硬體）

Learning Points（學習要點）
核心知識點：
- Producer-Consumer 模式
- 型別安全訊息契約
- 回合關聯追蹤
技能要求：
- 必備技能：BlockingCollection
- 進階技能：回放與重試策略
延伸思考：
- 是否改用 Channel/TPL Dataflow？
Practice Exercise（練習題）
- 基礎練習：以 BlockingCollection 建立資料流（30 分鐘）
- 進階練習：加入重試與死信佇列（2 小時）
- 專案練習：可重放檔案輸出/輸入（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：資料流正確
- 程式碼品質（30%）：清楚解耦
- 效能優化（20%）：吞吐穩定
- 創新性（10%）：回放工具

---

## Case #7: 多執行緒安全的隨機數：ThreadLocal Random 與安全 RNG

### Problem Statement（問題陳述）
業務場景：多執行緒生成猜測時使用同一 Random，導致序列碰撞或低隨機性。
技術挑戰：提供高質量且執行緒安全的亂數來源。
影響範圍：猜測品質下降、結果偏頗、不公平。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多執行緒共用 Random 導致競態與重複序列。
2. 以時間種子初始化多個 Random，種子相近。
3. 缺乏可重現測試種子策略。
深層原因：
- 架構層面：未定義 RNG 策略與生命週期。
- 技術層面：不了解 Random 的執行緒安全性。
- 流程層面：無固定種子測試流程。

### Solution Design（解決方案設計）
解決策略：每執行緒一個 Random（ThreadLocal），或使用 RandomNumberGenerator 產生高品質亂數；提供固定種子選項以重現。

實施步驟：
1. 提供 ThreadLocal Random 工具
- 實作細節：使用 Guid 雜湊作為種子。
- 所需資源：ThreadLocal<T>
- 預估時間：0.5 小時
2. 安全 RNG 選項
- 實作細節：RandomNumberGenerator.Fill，用於高品質隨機。
- 所需資源：System.Security.Cryptography
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
static readonly ThreadLocal<Random> Rng = new(() => new Random(Guid.NewGuid().GetHashCode()));

int NextInt(int min, int max) => Rng.Value!.Next(min, max);

// 安全 RNG 範例
int NextSecureInt(int min, int max) {
    Span<byte> bytes = stackalloc byte[4];
    RandomNumberGenerator.Fill(bytes);
    uint v = BitConverter.ToUInt32(bytes);
    return (int)(v % (uint)(max - min)) + min;
}
```

實際案例：在多 Player 策略並行產生猜測時避免重複
實作環境：C# / .NET 6
實測數據：
- 可量測指標：重複率、分布均勻性
- 目標範圍：重複率顯著下降；可選固定種子重現

Learning Points（學習要點）
核心知識點：
- Random 執行緒安全與種子
- ThreadLocal 與 RNGCrypto
- 可重現性
技能要求：
- 必備技能：C# 基礎、RNG
- 進階技能：統計檢定（可選）
Practice Exercise（練習題）
- 基礎練習：ThreadLocal Random（30 分鐘）
- 進階練習：比較 Random vs RNGCrypto 分布（2 小時）
- 專案練習：加入固定種子與回放（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：無碰撞/低碰撞
- 程式碼品質（30%）：易用 API
- 效能優化（20%）：延遲可接受
- 創新性（10%）：統計報表

---

## Case #8: 超時與取消：避免無限等待與僵死回合

### Problem Statement（問題陳述）
業務場景：在等待對方訊號時可能無限阻塞，需要系統性超時與取消。
技術挑戰：一致性的超時策略與取消傳遞，確保優雅退出。
影響範圍：程式卡死、資源無法釋放。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未設定 Wait 超時。
2. 取消權杖未被傳遞或忽略。
3. 遇到例外時未清理資源與通知對方。
深層原因：
- 架構層面：取消路徑未標準化。
- 技術層面：對 WaitAny/Token 了解不足。
- 流程層面：無超時測試與注入。

### Solution Design（解決方案設計）
解決策略：所有等待都加超時；建立 CancellationTokenSource，將 Token 傳遞到所有回圈；用 WaitHandle.WaitAny 支援雙重條件（事件或取消）。

實施步驟：
1. 建立全域取消機制
- 實作細節：CancellationTokenSource 傳播。
- 所需資源：System.Threading
- 預估時間：0.5 小時
2. 封裝帶超時的 Wait
- 實作細節：WaitAny({turn, token.WaitHandle}, timeout)
- 所需資源：工具方法
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
bool WaitWithCancel(AutoResetEvent turn, CancellationToken token, TimeSpan timeout) {
    int idx = WaitHandle.WaitAny(new WaitHandle[] { turn, token.WaitHandle }, timeout);
    return idx == 0; // 0: turn signaled, 1: canceled, WaitHandle.WaitTimeout: -1
}
```

實際案例：Host/Player 皆能在對方異常時優雅停止
實作環境：C# / .NET 6
實測數據：
- 可量測指標：取消響應時間、資源釋放率
- 目標範圍：取消響應 < 50ms；無遺留 Thread

Learning Points（學習要點）
核心知識點：
- CancellationToken 傳播
- WaitAny 與多條件等待
- 優雅關閉
技能要求：
- 必備技能：Thread/Token API
- 進階技能：資源釋放與復原
Practice Exercise（練習題）
- 基礎練習：WaitWithCancel 包裝（30 分鐘）
- 進階練習：在壓測中注入取消（2 小時）
- 專案練習：完備的關閉序列（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可取消
- 程式碼品質（30%）：封裝良好
- 效能優化（20%）：低延遲
- 創新性（10%）：可觀測指標

---

## Case #9: 併發追蹤與診斷：序列化事件紀錄與回放

### Problem Statement（問題陳述）
業務場景：偶發同步問題難以重現，需要完整事件紀錄與回放重播。
技術挑戰：低成本記錄時序與關聯 ID，並支持回放。
影響範圍：降低除錯成本，提高穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無回合 ID 與時序戳記。
2. 記錄零碎難以關聯。
3. 無回放機制驗證修補效果。
深層原因：
- 架構層面：缺少統一事件模型。
- 技術層面：未建立非阻塞記錄管道。
- 流程層面：缺失「重現—修補—驗證」閉環。

### Solution Design（解決方案設計）
解決策略：以非阻塞隊列收集 LogEvent，序列化到檔案；提供回放器讀取事件驅動 Host/Player 模擬，支持決定性重現。

實施步驟：
1. 定義 LogEvent 與收集器
- 實作細節：RoundId、Timestamp、Actor、Action、Payload
- 所需資源：ConcurrentQueue/Channel
- 預估時間：1 小時
2. 回放器
- 實作細節：按時間順序觸發事件，驗證結果
- 所需資源：序列化/反序列化
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
public record LogEvent(int RoundId, string Actor, string Action, long Ticks, string Payload);

ConcurrentQueue<LogEvent> logQ = new();

void Log(int round, string actor, string action, string payload = "") =>
    logQ.Enqueue(new LogEvent(round, actor, action, Stopwatch.GetTimestamp(), payload));
```

實際案例：重現互等/超時問題並驗證修復
實作環境：C# / .NET 6
實測數據：
- 可量測指標：重現成功率、記錄開銷
- 目標範圍：重現率 100%；記錄延遲 < 1% 回合時間

Learning Points（學習要點）
核心知識點：
- 結構化日誌
- 回放測試
- 非阻塞記錄
技能要求：
- 必備技能：序列化、集合
- 進階技能：時間同步與回放策略
Practice Exercise（練習題）
- 基礎練習：記錄/回放簡易實作（30 分鐘）
- 進階練習：加上校驗（2 小時）
- 專案練習：視覺化時序瀑布圖（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可回放
- 程式碼品質（30%）：資料結構合理
- 效能優化（20%）：低開銷
- 創新性（10%）：可視化

---

## Case #10: 決定性單元測試：用協程/虛擬排程器重現回合

### Problem Statement（問題陳述）
業務場景：多執行緒測試不穩定；需要可控排程的決定性測試。
技術挑戰：建立步進式排程器，以固定順序執行 Host/Player 步驟。
影響範圍：提高測試穩定性與覆蓋率。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 測試依賴 Thread 與 timing。
2. Race condition 造成測試偶發失敗。
3. 無可控順序的排程器。
深層原因：
- 架構層面：未抽象執行模型。
- 技術層面：不熟悉協程式測試技巧。
- 流程層面：未推動決定性測試策略。

### Solution Design（解決方案設計）
解決策略：將邏輯封裝為協程（Case #3），在測試中以虛擬排程器逐步執行，注入固定種子 RNG 與固定 Host 目標，確保穩定重現。

實施步驟：
1. 重構為協程化
- 實作細節：Host/Player 以 IEnumerator 暴露步驟
- 所需資源：yield
- 預估時間：2 小時
2. 測試用排程器
- 實作細節：提供 Step() API，斷言每一步
- 所需資源：測試框架
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public sealed class TestScheduler {
    private readonly List<IEnumerator> _actors;
    public TestScheduler(params IEnumerator[] actors) => _actors = actors.ToList();
    public bool Step() {
        bool moved = false;
        foreach (var a in _actors.ToList()) {
            if (a.MoveNext()) { moved = true; }
        }
        return moved;
    }
}
```

實際案例：對單回合/多回合行為做逐步斷言
實作環境：C# / .NET 6、xUnit/NUnit
實測數據：
- 可量測指標：測試穩定性、重現率、執行時間
- 目標範圍：重現率 100%；單測 < 100ms

Learning Points（學習要點）
核心知識點：
- 決定性測試
- 協程步進
- 固定種子策略
技能要求：
- 必備技能：單元測試
- 進階技能：測試替身與虛擬時間
Practice Exercise（練習題）
- 基礎練習：寫 Step() 型測試（30 分鐘）
- 進階練習：注入固定 RNG 與 Host 目標（2 小時）
- 專案練習：回放檔案驅動測試（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：重現穩定
- 程式碼品質（30%）：測試維護佳
- 效能優化（20%）：快速
- 創新性（10%）：回放整合

---

## Case #11: 捨棄鎖改採單執行緒事件迴圈：降低上下文切換

### Problem Statement（問題陳述）
業務場景：鎖競爭嚴重、上下文切換多、效能不佳。
技術挑戰：轉為單執行緒事件迴圈，同時維持高吞吐與可擴充性。
影響範圍：效能瓶頸、延遲不穩定、除錯困難。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 過多鎖競爭造成延遲。
2. Thread 數過多導致切換開銷。
3. 資料共享導致 cache 不友善。
深層原因：
- 架構層面：共享狀態太多。
- 技術層面：不恰當的同步基元選擇。
- 流程層面：未量測切換開銷。

### Solution Design（解決方案設計）
解決策略：使用單執行緒事件迴圈＋工作佇列（Action Queue），所有邏輯在同一執行緒上執行，避免鎖；IO 事件以 Post 進佇列。

實施步驟：
1. 建立事件迴圈執行緒
- 實作細節：BlockingCollection<Action> + loop
- 所需資源：BlockingCollection
- 預估時間：1 小時
2. 封裝 Post/Send API
- 實作細節：由外部將工作提交
- 所需資源：小型抽象層
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var q = new BlockingCollection<Action>(new ConcurrentQueue<Action>());
var loop = new Thread(() => { foreach (var a in q.GetConsumingEnumerable()) a(); });
loop.Start();

void Post(Action a) => q.Add(a);
void Stop() => q.CompleteAdding();
```

實際案例：Host 與 Player 的互動均在事件迴圈中串行執行
實作環境：C# / .NET 6
實測數據：
- 可量測指標：上下文切換次數、平均延遲
- 目標範圍：上下文切換近零；延遲穩定

Learning Points（學習要點）
核心知識點：
- 事件迴圈模型
- 鎖避免策略
- 排隊理論
技能要求：
- 必備技能：集合與執行緒
- 進階技能：背壓與容量控制
Practice Exercise（練習題）
- 基礎練習：建立事件迴圈（30 分鐘）
- 進階練習：加入背壓控制（2 小時）
- 專案練習：將既有鎖重構為事件迴圈（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：功能等價
- 程式碼品質（30%）：清晰、無鎖
- 效能優化（20%）：延遲穩定
- 創新性（10%）：背壓機制

---

## Case #12: 策略插件化：以 Strategy 模式熱插拔多個 Player

### Problem Statement（問題陳述）
業務場景：需要比較多種猜測策略，並在不更動 Host 的前提下插拔。
技術挑戰：抽象共同介面、反射載入、生命週期管理。
影響範圍：擴充性與實驗效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Player 策略與 Host 耦合。
2. 缺乏統一介面與載入規約。
3. 無法動態切換策略。
深層原因：
- 架構層面：缺漏 Strategy 與插件化設計。
- 技術層面：反射與組件邊界不明。
- 流程層面：無 A/B 測試流程。

### Solution Design（解決方案設計）
解決策略：定義 IPlayerStrategy；以反射或 DI 容器載入；Host 只依賴介面。提供基準測試工具切換策略。

實施步驟：
1. 定義介面與 Host 注入
- 實作細節：IPlayerStrategy.NextGuess(GameState)
- 所需資源：DI/反射
- 預估時間：1 小時
2. 策略載入與切換
- 實作細節：Assembly.LoadFrom + Activator.CreateInstance
- 所需資源：檔案布局
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public interface IPlayerStrategy {
    int NextGuess(GameState state);
}

var asm = Assembly.LoadFrom("MyPlayerStrategy.dll");
var type = asm.GetTypes().First(t => typeof(IPlayerStrategy).IsAssignableFrom(t));
var strategy = (IPlayerStrategy)Activator.CreateInstance(type)!;
```

實際案例：快速比較「二分剪枝」與「啟發式」策略
實作環境：C# / .NET 6
實測數據：
- 可量測指標：回合數、耗時、成功率
- 目標範圍：支援 1 鍵切換策略、產出比較報表

Learning Points（學習要點）
核心知識點：
- Strategy 模式
- 反射載入
- 基準測試
技能要求：
- 必備技能：介面抽象、反射
- 進階技能：DI、模組化
Practice Exercise（練習題）
- 基礎練習：實作兩個策略並切換（30 分鐘）
- 進階練習：策略熱更新（2 小時）
- 專案練習：策略 A/B 測試看板（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可插拔
- 程式碼品質（30%）：低耦合
- 效能優化（20%）：比較工具
- 創新性（10%）：熱更新

---

## Case #13: 懶惰序列：用 yield 產生猜測組合，節省記憶體

### Problem Statement（問題陳述）
業務場景：一次性產生所有候選（例如 4 位不重複數字）會耗費大量記憶體與時間。
技術挑戰：以 lazy 方式逐步產生，邊用邊算。
影響範圍：降低初始化成本、提升吞吐。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預先展開全域域（例如 10P4 = 5040）造成成本。
2. 產生後未必都會用到。
3. GC 壓力增加。
深層原因：
- 架構層面：資料生產與消費未解耦。
- 技術層面：未使用 yield 的延遲特性。
- 流程層面：缺乏效能分析。

### Solution Design（解決方案設計）
解決策略：遞迴/迭代以 yield 逐步產生不重複排列，與評分流程串接，避免整批建立。

實施步驟：
1. 撰寫排列生成器
- 實作細節：避免重複數字；yield 回傳
- 所需資源：C#
- 預估時間：1 小時
2. 串接評分管線
- 實作細節：在 foreach 中即時評估
- 所需資源：BlockingCollection（可選）
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
IEnumerable<string> Gen(int length, string digits = "0123456789", string prefix = "") {
    if (prefix.Length == length) { yield return prefix; yield break; }
    foreach (var d in digits) {
        if (!prefix.Contains(d))
            foreach (var s in Gen(length, digits, prefix + d))
                yield return s;
    }
}
```

實際案例：逐步產生候選並與約束剪枝（Case #14）串接
實作環境：C# / .NET 6
實測數據：
- 可量測指標：初始化時間、峰值記憶體、GC 次數
- 目標範圍：峰值記憶體顯著下降、初始化幾乎為零

Learning Points（學習要點）
核心知識點：
- Lazy evaluation
- 產消解耦
- 記憶體友善
技能要求：
- 必備技能：yield
- 進階技能：性能剖析
Practice Exercise（練習題）
- 基礎練習：產生 4 位不重複數（30 分鐘）
- 進階練習：支援黑名單數字（2 小時）
- 專案練習：與剪枝器串接（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：正確性
- 程式碼品質（30%）：簡潔
- 效能優化（20%）：內存下降
- 創新性（10%）：動態約束

---

## Case #14: 約束剪枝（Bulls and Cows）：以回饋過濾候選集

### Problem Statement（問題陳述）
業務場景：每次猜測後可用回饋（幾 A 幾 B）大幅縮小候選空間。
技術挑戰：撰寫高效剪枝器並與產生器串接。
影響範圍：降低回合數、提升速度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未使用回饋過濾，重覆嘗試無效候選。
2. 比對演算法低效。
3. 產生器與剪枝器耦合差。
深層原因：
- 架構層面：缺乏管線化設計。
- 技術層面：比對邏輯不優。
- 流程層面：無效能驗證。

### Solution Design（解決方案設計）
解決策略：實作 Bulls/Cows 計算函式；每次回饋都將候選集過濾；配合 lazy 生成避免大量無效計算。

實施步驟：
1. 實作評分函式
- 實作細節：O(n) 比對
- 所需資源：C#
- 預估時間：0.5 小時
2. 串接剪枝
- 實作細節：Where 過濾或自訂 enumerator
- 所需資源：LINQ
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
(bool ok) Match(string guess, string target, int expA, int expB) {
    int A = 0, B = 0;
    for (int i = 0; i < guess.Length; i++) {
        if (guess[i] == target[i]) A++;
        else if (target.Contains(guess[i])) B++;
    }
    return (A == expA) && (B == expB);
}
```

實際案例：每次回饋後候選集指數下降，快速收斂
實作環境：C# / .NET 6
實測數據：
- 可量測指標：平均回合數、每回合過濾耗時
- 目標範圍：回合數顯著下降

Learning Points（學習要點）
核心知識點：
- 約束滿足/剪枝
- 演算法與資料結構
- 管線化
技能要求：
- 必備技能：C# 與字串處理
- 進階技能：演算法分析
Practice Exercise（練習題）
- 基礎練習：實作 Match 函式（30 分鐘）
- 進階練習：針對多位數最佳化（2 小時）
- 專案練習：完整解題器（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：正確剪枝
- 程式碼品質（30%）：可讀性
- 效能優化（20%）：比對效率
- 創新性（10%）：啟發式策略

---

## Case #15: 回合同步屏障：Barrier/Rendezvous 確保同一節奏開局

### Problem Statement（問題陳述）
業務場景：需要確保 Host 與 Player 在每回合開始前皆準備就緒。
技術挑戰：設計集中同步點，避免有人先跑。
影響範圍：避免時序錯亂、狀態不一致。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少共同起點訊號。
2. 多方準備時間不同步。
3. 初始化與回合開始混在一起。
深層原因：
- 架構層面：缺少回合生命週期定義。
- 技術層面：未使用 Barrier。
- 流程層面：未定義「Ready/Go」流程。

### Solution Design（解決方案設計）
解決策略：使用 Barrier(2) 作為回合開始屏障；所有參與者 SignalAndWait() 後同步起跑。

實施步驟：
1. 建立 Barrier
- 實作細節：參與者數量與後置動作（增加回合計數）
- 所需資源：System.Threading.Barrier
- 預估時間：0.5 小時
2. 嵌入回合流程
- 實作細節：回合內不可再次等待屏障
- 所需資源：流程調整
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
int round = 0;
var barrier = new Barrier(2, b => Interlocked.Increment(ref round));

void HostLoop() { while (true) { barrier.SignalAndWait(); /* host actions */ } }
void PlayerLoop() { while (true) { barrier.SignalAndWait(); /* player actions */ } }
```

實際案例：每回合開局一致，便於度量與重放
實作環境：C# / .NET 6
實測數據：
- 可量測指標：回合偏斜（start time 差）
- 目標範圍：偏斜 < 1ms（視平台）

Learning Points（學習要點）
核心知識點：
- Barrier 用法
- 同步語意
- 回合生命週期
技能要求：
- 必備技能：Thread 同步
- 進階技能：時序度量
Practice Exercise（練習題）
- 基礎練習：Barrier 範例（30 分鐘）
- 進階練習：加入第三參與者（2 小時）
- 專案練習：可配置參與者與報表（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：同步正確
- 程式碼品質（30%）：簡潔安全
- 效能優化（20%）：低延遲
- 創新性（10%）：監控指標

---

## Case #16: 跨執行緒 UI 更新安全：用 SynchronizationContext/Invoke

### Problem Statement（問題陳述）
業務場景：WinForms/WPF 介面顯示回合過程，但背景執行緒直接更新 UI 導致例外。
技術挑戰：在不阻塞 UI 的前提下，安全地跨執行緒更新。
影響範圍：程式崩潰、UI 凍結。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 背景執行緒直接存取 UI 元件。
2. 用同步呼叫阻塞 UI 執行緒。
3. 未捕捉 UI 更新例外。
深層原因：
- 架構層面：缺乏 UI 更新通道。
- 技術層面：未使用 SynchronizationContext/Dispatcher。
- 流程層面：未測試 UI 響應性。

### Solution Design（解決方案設計）
解決策略：取得 UI SynchronizationContext，使用 Post 非同步投遞更新；或在 WinForms 用 Control.BeginInvoke。

實施步驟：
1. 建立 UI 更新封裝
- 實作細節：UIThread.Post(Action)
- 所需資源：SynchronizationContext
- 預估時間：0.5 小時
2. 替換所有 UI 更新呼叫
- 實作細節：避免跨執行緒直呼
- 所需資源：全域搜尋替換
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var ui = SynchronizationContext.Current!;
void UiPost(Action a) => ui.Post(_ => a(), null);

// WinForms: this.BeginInvoke((Action)(() => label.Text = "OK"));
```

實際案例：即時顯示猜測與回饋進度
實作環境：C# / .NET 6、WinForms/WPF
實測數據：
- 可量測指標：UI thread block 次數、FPS
- 目標範圍：無跨執行緒例外；UI 流暢

Learning Points（學習要點）
核心知識點：
- UI 執行緒模型
- SynchronizationContext
- 非阻塞更新
技能要求：
- 必備技能：UI 框架基礎
- 進階技能：節流/防抖
Practice Exercise（練習題）
- 基礎練習：封裝 UiPost（30 分鐘）
- 進階練習：批次更新與節流（2 小時）
- 專案練習：實作進度看板（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：無崩潰
- 程式碼品質（30%）：封裝易用
- 效能優化（20%）：UI 流暢
- 創新性（10%）：節流策略

---

## Case #17: 生產者-消費者流水線：BlockingCollection/TPL Dataflow 分離關注點

### Problem Statement（問題陳述）
業務場景：猜測生成、評分與統計同時進行，彼此干擾效能。
技術挑戰：建立非同步流水線，分離階段，提升吞吐。
影響範圍：整體吞吐量與延遲。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 所有工作在同一執行緒串行。
2. 評分耗時阻塞生成。
3. 統計與紀錄與主流程混雜。
深層原因：
- 架構層面：缺乏管線化設計。
- 技術層面：未使用 BlockingCollection/Dataflow。
- 流程層面：無背壓控制。

### Solution Design（解決方案設計）
解決策略：建立多階段：Generator -> Evaluator -> Stats；用 BlockingCollection 或 TPL Dataflow Block 連接；設定容量與背壓。

實施步驟：
1. BlockingCollection 版管線
- 實作細節：三段佇列相連
- 所需資源：BlockingCollection
- 預估時間：1 小時
2. TPL Dataflow 優化（可選）
- 實作細節：Buffer/TransformBlock + BoundedCapacity
- 所需資源：System.Threading.Tasks.Dataflow
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var q1 = new BlockingCollection<int>(100);
var q2 = new BlockingCollection<Verdict>(100);

// Producer
Task.Run(() => { foreach (var g in GuessGenerator()) q1.Add(g); q1.CompleteAdding(); });

// Evaluator
Task.Run(() => {
    foreach (var g in q1.GetConsumingEnumerable()) q2.Add(Judge(g));
    q2.CompleteAdding();
});

// Stats
Task.Run(() => { foreach (var v in q2.GetConsumingEnumerable()) UpdateStats(v); });
```

實際案例：高吞吐的回合處理線
實作環境：C# / .NET 6；TPL Dataflow（可選）
實測數據：
- 可量測指標：吞吐量、平均延遲、佇列長度
- 目標範圍：吞吐穩定、佇列無長期堆積

Learning Points（學習要點）
核心知識點：
- Pipeline/背壓
- BlockingCollection 與 Dataflow
- 非同步佇列
技能要求：
- 必備技能：集合/Task
- 進階技能：平衡與調參
Practice Exercise（練習題）
- 基礎練習：三段管線（30 分鐘）
- 進階練習：加上容量與度量（2 小時）
- 專案練習：自動調參（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：管線工作
- 程式碼品質（30%）：解耦清晰
- 效能優化（20%）：吞吐提升
- 創新性（10%）：自動調參

---

## Case #18: 基準測試與驗收指標：建立可重現的效能評估流程

### Problem Statement（問題陳述）
業務場景：比賽追求「又快又好」，需要可重現的基準與驗收標準衡量改進。
技術挑戰：定義基準場景、指標、報告與比較流程。
影響範圍：客觀評估、持續優化。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無一致測試場景與資料。
2. 指標定義不清。
3. 無自動化報告。
深層原因：
- 架構層面：缺失基準測試模組。
- 技術層面：未使用 Stopwatch/Benchmark 工具。
- 流程層面：無 CI 整合。

### Solution Design（解決方案設計）
解決策略：建立 Benchmark 模組：固定種子與目標、固定回合數；記錄吞吐、延遲、回合數；輸出 JSON 報告；CI 內比較前後結果。

實施步驟：
1. 撰寫基準 Driver
- 實作細節：固定種子、迭代 N 次、記錄
- 所需資源：Stopwatch、JSON
- 預估時間：2 小時
2. 報告與比較
- 實作細節：生成報表、比較前後
- 所需資源：CI 腳本
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
var sw = Stopwatch.StartNew();
// 跑 N 次遊戲
sw.Stop();
var report = new {
    Rounds = rounds,
    ElapsedMs = sw.Elapsed.TotalMilliseconds,
    Throughput = rounds / sw.Elapsed.TotalSeconds
};
File.WriteAllText("bench.json", JsonSerializer.Serialize(report));
```

實際案例：對比多種同步/策略組合的效能
實作環境：C# / .NET 6
實測數據：
- 可量測指標：吞吐、延遲、回合數、GC 分配
- 目標範圍：提供通過門檻（如吞吐 > X）

Learning Points（學習要點）
核心知識點：
- 基準測試設計
- 指標與報告
- CI 驗收
技能要求：
- 必備技能：Stopwatch/序列化
- 進階技能：CI/CD 整合
Practice Exercise（練習題）
- 基礎練習：單場景報表（30 分鐘）
- 進階練習：多策略對比（2 小時）
- 專案練習：CI 自動化比較（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：完整報表
- 程式碼品質（30%）：結構清晰
- 效能優化（20%）：可量測
- 創新性（10%）：CI 報告

---

## 案例分類

1) 按難度分類
- 入門級（適合初學者）：#7, #13, #15, #16
- 中級（需要一定基礎）：#1, #2, #5, #6, #8, #12, #17, #18, #14
- 高級（需要深厚經驗）：#3, #4, #9, #10, #11

2) 按技術領域分類
- 架構設計類：#5, #11, #12, #18
- 效能優化類：#11, #13, #14, #17, #18
- 整合開發類：#6, #12, #17
- 除錯診斷類：#2, #8, #9, #10
- 安全防護類：#7（隨機性與公平性）

3) 按學習目標分類
- 概念理解型：#3, #4, #5
- 技能練習型：#1, #6, #7, #13, #15, #16
- 問題解決型：#2, #8, #9, #10, #11, #14
- 創新應用型：#12, #17, #18

## 案例關聯圖（學習路徑建議）
- 建議先學：#1（事件驅動同步）、#2（死結排除）、#4（yield 原理）
- 依賴關係與進階：
  - #3（協程同步）依賴 #4
  - #5（架構 Mediator）可與 #1/#2 並行，加深設計思維
  - #6（訊息契約）承接 #5，為 #9/#17 奠基
  - #7（RNG）獨立但建議早學，利於測試重現
  - #8（超時取消）依賴 #1/#2 的同步模型
  - #9（追蹤診斷）依賴 #6 的事件結構
  - #10（決定性測試）依賴 #3（協程化）
  - #11（事件迴圈）是 #1/#2 的架構級替代方案
  - #12（策略插件化）依賴 #5 的抽象
  - #13（lazy 生成）可直接套用，#14（剪枝）與之組合
  - #17（流水線）依賴 #6；可與 #13/#14 聯動
  - #18（基準測試）作為整體驗收，建議最後實施
- 完整學習路徑建議：
  1. 基礎同步與死結：#1 -> #2 -> #8
  2. yield 與協程：#4 -> #3 -> #10
  3. 架構抽象與訊息流：#5 -> #6 -> #9
  4. 策略與資料流：#12 -> #13 -> #14 -> #17
  5. 架構優化：#11（事件迴圈）
  6. 輔助與 UI：#7 -> #15 -> #16
  7. 基準驗收：#18

以上 18 個案例可對應文章提到的核心主題：Thread Sync 概念與實作、yield return 的理解與替代同步、以及 GameHost/Player 誰為主的架構抉擇，並延伸為完整可操作的教學與評估素材。