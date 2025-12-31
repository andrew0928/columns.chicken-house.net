---
layout: synthesis
title: "[架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用"
synthesis_type: solution
source_post: /2022/05/29/datetime-mock/
redirect_from:
  - /2022/05/29/datetime-mock/solution/
postid: 2022-05-29-datetime-mock
---

以下為基於文章內容所提煉的 16 個結構化解決方案案例，涵蓋 DateTime 可控化、事件觸發、測試穩定性、PoC 降維打擊與多種替代策略。每個案例含完整問題、根因、方案、程式碼與實測/效益說明，便於教學、實作與評估。

## Case #1: 在測試與 PoC 中取得可控且會流動的現在時間（Ambient Context：DateTimeUtil）

### Problem Statement（問題陳述）
- 業務場景：系統需在接單後立即回覆，並於每月 15 日 02:00 產生月結報。開發者在 PoC 或單元測試中需要快速演示整體流程，不可能等待真實時間流動，也不應改動系統時鐘。
- 技術挑戰：標準的 DateTime.Now 是 static property，無法用 DI 或 wrapper 無縫替換；多數 mock 實作將時間凍結，不能自然流動。
- 影響範圍：時間相依的邏輯無法被穩定演示/測試，導致回饋迴圈極慢、測試脆弱。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. DateTime.Now 是 static property，呼叫點與 System.DateTime 緊耦合。
  2. 傳統 mock 時間的方法大多將時間固定，無法反映真實時間流動。
  3. 需要跨日/跨月事件觸發，凍結時間不利於流程驗證。
- 深層原因：
  - 架構層面：缺少可控時間的 Ambient Context；全域時間取用無抽象層。
  - 技術層面：無法攔截 static 呼叫；沒有具備 offset 與事件的時間控制器。
  - 流程層面：測試與 PoC 缺乏時間操控工具，迭代成本高。

### Solution Design（解決方案設計）
- 解決策略：實作 Ambient Context（全域唯一）的 DateTimeUtil，透過 Init 設定起點時間，內部以「offset = expected - DateTime.Now」計算，Now 隨真實時間流動。提供 TimePass 快轉，並在跨日時透過 RaiseDayPassEvent 觸發每日事件。

- 實施步驟：
  1. 建立 DateTimeUtil 核心
     - 實作細節：單例 Instance、Init/Reset、Now 計算 offset、TimePass 快轉、RaiseDayPassEvent
     - 所需資源：.NET 6+/C# 10、MSTest/NUnit
     - 預估時間：1-2 小時
  2. 將 PoC/測試程式改用 DateTimeUtil.Instance.Now
     - 實作細節：在 PoC/測試中以 DateTimeUtil.Now 取代 DateTime.Now；啟動點呼叫 Init
     - 所需資源：編輯器/IDE
     - 預估時間：0.5-1 小時
  3. 設計日界事件
     - 實作細節：Seek_LastEventCheckTime 檢查跨日並 RaiseDayPassEvent
     - 所需資源：同上
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```csharp
public class DateTimeUtil
{
    private static DateTimeUtil _instance = null;
    public static DateTimeUtil Instance => _instance;
    public static void Init(DateTime expectedTimeNow)
    {
        if (_instance != null) throw new InvalidOperationException("re-init? call Reset()");
        _instance = new DateTimeUtil(expectedTimeNow);
    }
    public static void Reset() => _instance = null;

    public event EventHandler<TimePassEventArgs> RaiseDayPassEvent;
    public class TimePassEventArgs : EventArgs { public DateTime OccurTime; }

    private TimeSpan _realtime_offset;
    private DateTime _last_check_event_time;

    private DateTimeUtil(DateTime expected)
    {
        _realtime_offset = expected - DateTime.Now;
        _last_check_event_time = expected;
    }

    public DateTime Now
    {
        get
        {
            var result = DateTime.Now + _realtime_offset;
            Seek_LastEventCheckTime(result);
            return result;
        }
    }

    private void Seek_LastEventCheckTime(DateTime checkTime)
    {
        while (_last_check_event_time < checkTime)
        {
            if (_last_check_event_time.Date < checkTime.Date)
            {
                _last_check_event_time = _last_check_event_time.Date.AddDays(1);
                RaiseDayPassEvent?.Invoke(this, new TimePassEventArgs { OccurTime = _last_check_event_time });
            }
            else { _last_check_event_time = checkTime; break; }
        }
    }

    public void TimePass(TimeSpan duration)
    {
        if (duration < TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(duration));
        _realtime_offset += duration;
        Seek_LastEventCheckTime(Now);
    }
}
```

- 實際案例：文中單元測試 TimePassTest/TimePassWithEventTest/RealtimeEventTest
- 實作環境：.NET 6+/C# 10、Visual Studio 2022、MSTest
- 實測數據：
  - 改善前：需等待真實跨日（24 小時）才能看見日界事件
  - 改善後：呼叫 TimePass(TimeSpan.FromDays(1)) 即時觸發
  - 改善幅度：> 86,400 倍（以日為單位）

Learning Points（學習要點）
- 核心知識點：
  - Ambient Context 模式與單例差異
  - 以 offset 取代凍結時間的思路
  - 事件補發與應觸發時間（OccurTime）的重要性
- 技能要求：
  - 必備技能：C# 委派/事件、時間處理、單元測試
  - 進階技能：架構抽象（Context/Provider）、事件驅動設計
- 延伸思考：
  - 可應用於報表排程、資料快照、到期檢核等
  - 風險：全域狀態誤用、忘記 Reset/Init 造成測試干擾
  - 優化：提供背景計時器（可選）降低事件延遲

Practice Exercise（練習題）
- 基礎練習：實作 DateTimeUtil.Init/Now/TimePass，並在測試中驗證 Now 會隨 Sleep 流動（30 分）
- 進階練習：完成 RaiseDayPassEvent 與跨日補發邏輯（2 小時）
- 專案練習：用 DateTimeUtil 實作「每月 15 日 02:00 報表產生」PoC（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：Init/Reset/Now/TimePass/事件齊備且正確
- 程式碼品質（30%）：可讀性、單一職責、測試覆蓋
- 效能優化（20%）：跨大量日數時事件補發效率
- 創新性（10%）：OccurTime 設計、可插拔背景計時器


## Case #2: 用 offset 取代凍結時間，讓 Now 隨真實時間流動

### Problem Statement（問題陳述）
- 業務場景：在 PoC/Demo 時希望「啟動時間固定」但「之後自然流動」，例如啟動在 2002/10/26 12:00:00，跑 30 秒後讀 Now 即為 12:00:30。
- 技術挑戰：一般凍結時間 mock 無法反映「自然流動」。
- 影響範圍：日誌/排程/事件時間欄位失真，Demo 說服力下降。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 凍結時間的 mock 僅回傳固定值。
  2. 測試啟動點與 Now 讀取點存在不可預測延遲。
  3. UI/報表需顯示「流動」時間才貼近真實情境。
- 深層原因：
  - 架構層面：缺少可表示「真實時間差」的抽象。
  - 技術層面：未將「自然流動」納入時間策略。
  - 流程層面：Demo/PoC 未提供動態時間能力。

### Solution Design（解決方案設計）
- 解決策略：儲存 expected - DateTime.Now 的 TimeSpan offset。每次讀取 Now 時，用 DateTime.Now + offset 動態計算，達到啟動點固定、其後自然流動。

- 實施步驟：
  1. 設計 offset 的計算與保存
     - 實作細節：Init 時 offset = expectedNow - DateTime.Now
     - 所需資源：.NET/C#
     - 預估時間：30 分
  2. 於 Now getter 動態計算
     - 實作細節：return DateTime.Now + offset
     - 所需資源：同上
     - 預估時間：30 分

- 關鍵程式碼/設定：
```csharp
private TimeSpan _realtime_offset;
public static void Init(DateTime expectedNow)
{
    _instance = new DateTimeUtil(expectedNow);
}
private DateTimeUtil(DateTime expectedNow)
{
    _realtime_offset = expectedNow - DateTime.Now;
}
public DateTime Now => DateTime.Now + _realtime_offset;
```

- 實際案例：TimePassTest 以 Sleep(5s) 後 Now 約為 +5 秒
- 實作環境：.NET 6+/C# 10
- 實測數據：
  - 改善前：無法自然流動；只能固定時間
  - 改善後：Sleep 5 秒後 Now ≈ +5 秒，誤差 < 1 秒（測試容忍值）
  - 改善幅度：可用性質變（從靜止到動態）

Learning Points
- 核心知識點：offset 模式優勢、避免凍結造成資料失真
- 技能要求：時間運算、測試誤差處理
- 延伸思考：offset 可擴展到時區/夏令時間模擬

Practice Exercise
- 基礎練習：以 offset 計算 Now，寫測試驗證 Sleep 後時間變化（30 分）
- 進階練習：在高頻讀取下驗證誤差界線（2 小時）
- 專案練習：在 PoC 中顯示「系統 Now」並持續更新（8 小時）

Assessment Criteria
- 功能完整性（40%）：Now 能隨時流動
- 程式碼品質（30%）：簡潔、可讀
- 效能優化（20%）：頻繁存取時的負擔低
- 創新性（10%）：對其他時間語意（時區）延伸


## Case #3: 跨日快轉時逐日補發事件，保證每日任務不漏

### Problem Statement（問題陳述）
- 業務場景：一次快轉 35 天 15 小時，所有跨過的日界均需觸發排程事件（如產月報的每日前置邏輯）。
- 技術挑戰：單次時間跳轉會略過多個日界，若未補發會遺漏事件。
- 影響範圍：批次/排程作業缺漏、資料不一致。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 一次性時間跳轉未檢查中間日界。
  2. 少見將「應觸發時間」與「實際觸發時間」分離。
  3. 事件觸發點未定義（讀 Now/TimePass 皆可能是觸發點）。
- 深層原因：
  - 架構層面：缺乏補發（catch-up）策略。
  - 技術層面：缺少跨日循環檢查。
  - 流程層面：測試未覆蓋大跨度時間跳轉。

### Solution Design（解決方案設計）
- 解決策略：在 Seek_LastEventCheckTime 內以 while 迴圈逐日檢查，當 last_check.Date < checkTime.Date 時，逐日推進並 RaiseDayPassEvent，並以 OccurTime 標定該日。

- 實施步驟：
  1. 定義最後檢查點與補發邏輯
     - 實作細節：_last_check_event_time；while 逐日 RaiseDayPassEvent
     - 所需資源：.NET/C#
     - 預估時間：1 小時
  2. 在 Now getter 與 TimePass 後皆呼叫補發檢查
     - 實作細節：Seek_LastEventCheckTime(now)
     - 所需資源：同上
     - 預估時間：30 分

- 關鍵程式碼/設定：
```csharp
private DateTime _last_check_event_time;
private void Seek_LastEventCheckTime(DateTime checkTime)
{
    while (_last_check_event_time < checkTime)
    {
        if (_last_check_event_time.Date < checkTime.Date)
        {
            _last_check_event_time = _last_check_event_time.Date.AddDays(1);
            RaiseDayPassEvent?.Invoke(this, new TimePassEventArgs { OccurTime = _last_check_event_time });
        }
        else { _last_check_event_time = checkTime; break; }
    }
}
```

- 實際案例：TimePassWithEventTest 快轉 35 天 15 小時，事件計數 36
- 實作環境：.NET 6+/C# 10、MSTest
- 實測數據：
  - 改善前：可能 0 次或少發事件
  - 改善後：補發正確，計數 36（含跨過 36 個換日點）
  - 改善幅度：漏發率由不確定降為 0

Learning Points
- 核心知識點：補發策略、應觸發時間與實際觸發時間的分離
- 技能要求：事件模型設計、邊界條件測試
- 延伸思考：可延伸至每小時/每分鐘事件（粒度可配置）

Practice Exercise
- 基礎練習：實作 while 逐日補發（30 分）
- 進階練習：將補發粒度改為每小時並測試（2 小時）
- 專案練習：以補發策略驅動每日對帳流程 PoC（8 小時）

Assessment Criteria
- 功能完整性（40%）：跨大跨度時間不漏發
- 程式碼品質（30%）：邏輯清晰、易維護
- 效能優化（20%）：大量日數補發效率
- 創新性（10%）：可配置粒度/策略


## Case #4: 無背景執行緒的事件偵測策略與延遲界定

### Problem Statement（問題陳述）
- 業務場景：不啟用背景 Thread 的前提下，仍需在跨日時觸發事件。
- 技術挑戰：真實時間跨日發生在「程式閒置」期間可能遲到觸發。
- 影響範圍：事件延遲觸發；但在 PoC 設定下學習成本與穩定性更重要。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未使用背景監控，無法精準到時即發。
  2. 事件觸發點被限定在 Now/TimePass 的呼叫時機。
  3. PoC 設定對延遲容忍度高。
- 深層原因：
  - 架構層面：刻意不引入複雜度（背景執行緒、timer）
  - 技術層面：以呼叫點替代背景監控
  - 流程層面：以 PoC 為導向，換取快速驗證

### Solution Design（解決方案設計）
- 解決策略：明文規範事件觸發點（Now/TimePass），接受輕微延遲；若需更準時，提供可插拔背景 Timer 作為選配。

- 實施步驟：
  1. 文件化觸發時機
     - 實作細節：在 XML doc 註記 Now/TimePass 觸發
     - 所需資源：無
     - 預估時間：15 分
  2. 可選：背景 Timer 增強
     - 實作細節：以 System.Threading.Timer 每秒觸發 Seek_LastEventCheckTime
     - 所需資源：.NET/C#
     - 預估時間：1-2 小時

- 關鍵程式碼/設定（可選增強）：
```csharp
private Timer _timer;
private void StartTimer()
{
    _timer = new Timer(_ =>
    {
        Seek_LastEventCheckTime(Now);
    }, null, TimeSpan.Zero, TimeSpan.FromSeconds(1));
}
```

- 實際案例：RealtimeEventTest 展示「先 Sleep 不觸發，呼叫 Now 時補發」
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：需背景 thread 以準時觸發，複雜
  - 改善後：無背景 thread，延遲可接受（直到下一次 Now/TimePass）
  - 改善幅度：PoC 可靠性提升，複雜度降低

Learning Points
- 核心知識點：PoC 下的延遲容忍與設計權衡
- 技能要求：Timer/Threading 基礎（可選）、事件驅動觀念
- 延伸思考：生產系統可替換為 Quartz/HostedService

Practice Exercise
- 基礎練習：撰寫文件說明事件觸發點（30 分）
- 進階練習：加入 Timer 並量測延遲（2 小時）
- 專案練習：將 Timer 實作成可插拔策略（8 小時）

Assessment Criteria
- 功能完整性（40%）：明確觸發點；可選 Timer
- 程式碼品質（30%）：可讀、可關閉/釋放資源
- 效能優化（20%）：Timer 負載控制
- 創新性（10%）：策略化實作


## Case #5: 防止時間倒流，保護資料一致性

### Problem Statement（問題陳述）
- 業務場景：某些邏輯（如對帳、累計）對時間順序敏感；時間倒流會破壞一致性。
- 技術挑戰：提供 TimePass 的同時需禁止負值跳轉；若需重來，應明確 Reset/Init。
- 影響範圍：資料污染、事件重觸發、不可逆狀態扭曲。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未限制 TimePass 接受負值。
  2. 未清楚標示 Reset 與時光倒流差異。
- 深層原因：
  - 架構層面：全域狀態管理缺規範
  - 技術層面：未加參數驗證
  - 流程層面：缺少重置流程與資料清理策略

### Solution Design（解決方案設計）
- 解決策略：TimePass 僅允許非負 TimeSpan；需要倒退時，透過 Reset()+Init() 重建 Context 並準備資料清理。

- 實施步驟：
  1. 參數防衛
     - 實作細節：TimePass(duration < 0) throw
     - 所需資源：.NET/C#
     - 預估時間：10 分
  2. 文件化 Reset/Init 使用
     - 實作細節：註記 Reset 代表重建 Context 而非倒流
     - 所需資源：無
     - 預估時間：10 分

- 關鍵程式碼/設定：
```csharp
public void TimePass(TimeSpan duration)
{
    if (duration < TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(duration));
    _realtime_offset += duration;
    Seek_LastEventCheckTime(Now);
}
public static void Reset() => _instance = null; // 明確重置
```

- 實際案例：文中明確定義不得倒流，需 Reset/Init 重來
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：可能會接受負值導致狀態不一致
  - 改善後：倒流被阻止；重置流程清晰
  - 改善幅度：一致性風險趨近 0

Learning Points
- 核心知識點：防衛式程式設計、全域狀態治理
- 技能要求：例外設計、測試邊界值
- 延伸思考：可提供「試算」模式模擬回滾而不改動狀態

Practice Exercise
- 基礎練習：加入負值防衛與測試（30 分）
- 進階練習：設計 Reset/Init 流程測試（2 小時）
- 專案練習：在業務上實作「回放」而非倒流（8 小時）

Assessment Criteria
- 功能完整性（40%）：嚴格禁止倒流、Reset 安全
- 程式碼品質（30%）：錯誤訊息、測試覆蓋
- 效能優化（20%）：重置後資源釋放
- 創新性（10%）：回放/影子狀態設計


## Case #6: 快速驗證「每月 15 日 02:00」月結報行為

### Problem Statement（問題陳述）
- 業務場景：接單後立即回覆，並在每月 15 日 02:00 產生月結報；PoC/測試需快速重現整個流程。
- 技術挑戰：無法等待真實時間到達；需模擬跨日跨月且不漏觸發。
- 影響範圍：需求驗證時程、團隊溝通效率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 實時間等待成本高
  2. 靜態 Now 無法控制
  3. 跨日跳轉需補發事件
- 深層原因：
  - 架構層面：缺可控時間與事件
  - 技術層面：缺乏「下一個 15 日 02:00」計算
  - 流程層面：PoC 缺少快速演示機制

### Solution Design（解決方案設計）
- 解決策略：用 DateTimeUtil.Init 把起始時間固定；用 TimePass 直接跳至下一個 15 日 01:59，再 +1 分鐘觀察觸發；或直接跳過整月，檢查每日事件計數是否正確。

- 實施步驟：
  1. 計算下一個 15 日 02:00
     - 實作細節：若當前日期已過 15 日 02:00，下一個月；否則本月
     - 所需資源：.NET/C#
     - 預估時間：30 分
  2. 快轉並驗證
     - 實作細節：TimePass 到目標前 1 分，觀察事件/任務觸發
     - 所需資源：同上
     - 預估時間：30 分

- 關鍵程式碼/設定：
```csharp
DateTime Start = new DateTime(2022, 05, 01, 0, 0, 0);
DateTimeUtil.Init(Start);

DateTime NextExec(DateTime dt)
{
    var candidate = new DateTime(dt.Year, dt.Month, 15, 2, 0, 0);
    return (dt <= candidate) ? candidate : new DateTime(dt.Year, dt.Month, 1, 2, 0, 0).AddMonths(1).AddDays(14);
}

var next = NextExec(DateTimeUtil.Instance.Now);
// 跳到前 1 分鐘
DateTimeUtil.Instance.TimePass(next - DateTimeUtil.Instance.Now - TimeSpan.FromMinutes(1));
// 模擬 1 分鐘後
DateTimeUtil.Instance.TimePass(TimeSpan.FromMinutes(1));
// 驗證：此時已到 15 日 02:00，對應任務應觸發
```

- 實際案例：文中月結報舉例
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：需等待數日至月級時間
  - 改善後：秒級完成；事件/任務如期觸發
  - 改善幅度：數千至數萬倍縮短等待

Learning Points
- 核心知識點：目標時間計算、快轉與事件驗證
- 技能要求：日期運算、單元測試斷言
- 延伸思考：時區/夏令時間影響

Practice Exercise
- 基礎練習：實作 NextExec 計算（30 分）
- 進階練習：加入時區調整（2 小時）
- 專案練習：完整月結流程 PoC（8 小時）

Assessment Criteria
- 功能完整性（40%）：正確計算與觸發
- 程式碼品質（30%）：邏輯清晰
- 效能優化（20%）：大跨度快轉效率
- 創新性（10%）：容錯/重試機制


## Case #7: 在 PoC 介面提供「時間快轉」與「現在時間」顯示的操作

### Problem Statement（問題陳述）
- 業務場景：對利害關係人展示流程（接單→月結報），需直觀操作快轉時間。
- 技術挑戰：需要 UI 層快速集成 DateTimeUtil 並同步顯示「系統認為的 Now」。
- 影響範圍：PoC 溝通效率、需求確認速度。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺少可視化時間控制
  2. Demo 互動性不足
- 深層原因：
  - 架構層面：PoC 缺少便利工具
  - 技術層面：UI 與時間工具耦合未建立
  - 流程層面：演示效率低

### Solution Design（解決方案設計）
- 解決策略：在 UI 加上 Label 顯示 DateTimeUtil.Now，以及按鈕觸發 GoNextDays/GoNextHours/TimePass，讓時間跳轉一目了然。

- 實施步驟：
  1. 注入時間控制
     - 實作細節：表單載入時 Init；計時器或按下刷新按鈕顯示 Now
     - 所需資源：WPF/WinForms/Blazor 其一
     - 預估時間：1 小時
  2. 快轉按鈕
     - 實作細節：按鈕事件中呼叫 TimePass/GoNextDays
     - 所需資源：同上
     - 預估時間：1 小時

- 關鍵程式碼/設定（WinForms 範例）：
```csharp
public partial class DemoForm : Form
{
    public DemoForm()
    {
        InitializeComponent();
        DateTimeUtil.Init(new DateTime(2022, 5, 1, 0, 0, 0));
        var timer = new System.Windows.Forms.Timer { Interval = 500 };
        timer.Tick += (_, __) => lblNow.Text = DateTimeUtil.Instance.Now.ToString("yyyy/MM/dd HH:mm:ss");
        timer.Start();
    }

    private void btnNextDay_Click(object sender, EventArgs e)
    {
        DateTimeUtil.Instance.TimePass(TimeSpan.FromDays(1));
    }
    private void btnNextHour_Click(object sender, EventArgs e)
    {
        DateTimeUtil.Instance.TimePass(TimeSpan.FromHours(1));
    }
}
```

- 實際案例：文末提及在 UI 上提供 Now 與快轉按鈕
- 實作環境：.NET WinForms/WPF
- 實測數據：
  - 改善前：口述流程、難以理解
  - 改善後：即時可視化，會議決策效率提升
  - 改善幅度：溝通成本大幅下降（質化）

Learning Points
- 核心知識點：PoC 的 UX 助攻
- 技能要求：UI 事件處理、時間格式化
- 延伸思考：將時間控制抽象成開發運維工具

Practice Exercise
- 基礎練習：在 UI 顯示 Now（30 分）
- 進階練習：加入多種快轉按鈕（2 小時）
- 專案練習：整合排程結果視覺化（8 小時）

Assessment Criteria
- 功能完整性（40%）：Now 顯示與快轉可用
- 程式碼品質（30%）：UI 與邏輯分離
- 效能優化（20%）：更新頻率
- 創新性（10%）：PoC 專用控件


## Case #8: 降低時間類測試的脆弱性：以「容忍誤差」取代嚴格相等

### Problem Statement（問題陳述）
- 業務場景：Now 受真實時間影響（ms），若用嚴格相等，測試易因不穩定而失敗。
- 技術挑戰：需要穩健的斷言策略以避免 flakiness。
- 影響範圍：CI 可靠性、開發者信心。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Now 讀取點與 Sleep 等操作有不可預期延遲
  2. Debug 單步會增加差距
- 深層原因：
  - 架構層面：時間測試需容忍 ms~s 的漂移
  - 技術層面：比較策略欠佳
  - 流程層面：CI 中執行環境多變

### Solution Design（解決方案設計）
- 解決策略：使用 TimeSpan 容忍區間（如 1 秒）判定兩時間相差小於容忍值即算通過。

- 實施步驟：
  1. 撰寫容忍函式
     - 實作細節：Assert.IsTrue(Math.Abs((a-b).TotalSeconds) < 1)
     - 所需資源：MSTest/xUnit/NUnit
     - 預估時間：15 分
  2. 替換嚴格相等斷言
     - 實作細節：重構測試
     - 所需資源：同上
     - 預估時間：30 分

- 關鍵程式碼/設定：
```csharp
TimeSpan tolerance = TimeSpan.FromSeconds(1);
Assert.IsTrue(
    (DateTimeUtil.Instance.Now - new DateTime(2002,10,26,12,0,0)) < tolerance
);
```

- 實際案例：TimePassTest 中使用 1 秒容忍值
- 實作環境：.NET/MSTest
- 實測數據：
  - 改善前：間歇性失敗（特別是 Debug/慢機器）
  - 改善後：相同案例穩定通過
  - 改善幅度：Flaky 測試比例接近 0

Learning Points
- 核心知識點：時間測試的可預期性與容忍策略
- 技能要求：測試設計
- 延伸思考：引入重試與超時策略

Practice Exercise
- 基礎練習：寫出容忍時間差的斷言（30 分）
- 進階練習：不同容忍值對比（2 小時）
- 專案練習：時間相關測試回顧與重構（8 小時）

Assessment Criteria
- 功能完整性（40%）：斷言正確
- 程式碼品質（30%）：可重用
- 效能優化（20%）：測試穩定
- 創新性（10%）：抽象成測試工具


## Case #9: 讓 JWT 到期測試可持續：固定啟動時間並快轉

### Problem Statement（問題陳述）
- 業務場景：既有測試內嵌 JWT（exp 固定 3 年）；時間一到，測試必 fail。
- 技術挑戰：測試壽命綁死在實際日期；長期維護成本高。
- 影響範圍：CI 鎖死、回歸阻斷。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 使用固定 exp JWT 字串
  2. 測試依賴真實時間
- 深層原因：
  - 架構層面：缺少測試時間 Context
  - 技術層面：未抽象時間來源
  - 流程層面：未規劃長壽命測試策略

### Solution Design（解決方案設計）
- 解決策略：DateTimeUtil.Init 固定啟動時間（2022/05/01），再用 TimePass 快轉 5 年觸發 JWT 過期，確保測試隨時可跑。

- 實施步驟：
  1. 測試啟動時間固定
     - 實作細節：TestInitialize 中 Init
     - 所需資源：MSTest
     - 預估時間：15 分
  2. 快轉並驗證過期
     - 實作細節：TimePass(TimeSpan.FromYears(5))，Assert token 驗證失敗
     - 所需資源：同上
     - 預估時間：15 分

- 關鍵程式碼/設定：
```csharp
[TestInitialize]
public void Init()
{
    DateTimeUtil.Init(new DateTime(2022, 05, 01, 0, 0, 0));
    // ... init service with token ...
    DateTimeUtil.Instance.TimePass(TimeSpan.FromYears(5));
    // 斷言：token 應過期
}
```

- 實際案例：文中 MemberService 測試示例
- 實作環境：.NET/MSTest
- 實測數據：
  - 改善前：2025/04/04 後全部失敗
  - 改善後：任何時間執行皆可重現過期情境
  - 改善幅度：測試壽命由 3 年→無限期

Learning Points
- 核心知識點：測試資料與時間脫鉤
- 技能要求：安全機制測試、token 時效
- 延伸思考：動態簽發測試 token（非硬編碼）

Practice Exercise
- 基礎練習：加入 Init 與快轉（30 分）
- 進階練習：測試不同 exp 的行為（2 小時）
- 專案練習：設計 Token 測試工廠（8 小時）

Assessment Criteria
- 功能完整性（40%）：過期斷言可靠
- 程式碼品質（30%）：可維護
- 效能優化（20%）：測試速度
- 創新性（10%）：測試資料工廠


## Case #10: 用 Microsoft Fakes（Shims）攔截 DateTime.Now（不改業務碼）

### Problem Statement（問題陳述）
- 業務場景：不願改動既有業務 code，但希望在單元測試中固定 Now。
- 技術挑戰：DateTime.Now 為 static，難以 DI；需測試層攔截。
- 影響範圍：測試能否快速接手遺留系統。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Now 為 static property
  2. 業務碼不可動（或成本過高）
- 深層原因：
  - 架構層面：未設計時間抽象
  - 技術層面：需要 runtime 攔截（Shims）
  - 流程層面：測試依賴特定工具

### Solution Design（解決方案設計）
- 解決策略：在 ShimsContext 範圍內，替換 System.DateTime.Now 的 getter，回傳固定時間。適合單元測試，需 Visual Studio Enterprise。

- 實施步驟：
  1. 建立 Fakes 組件
     - 實作細節：參考 System 程式集，產生 Fakes
     - 所需資源：VS Enterprise
     - 預估時間：30 分
  2. 在測試裡使用 ShimsContext
     - 實作細節：ShimDateTime.NowGet = () => 固定值
     - 所需資源：同上
     - 預估時間：15 分

- 關鍵程式碼/設定：
```csharp
using (ShimsContext.Create())
{
    System.Fakes.ShimDateTime.NowGet = () => new DateTime(2000, 1, 1);
    var componentUnderTest = new MyComponent();
    int year = componentUnderTest.GetTheCurrentYear();
    Assert.AreEqual(2000, year);
}
```

- 實際案例：文中範例
- 實作環境：VS Enterprise、.NET
- 實測數據：
  - 改善前：需修改業務碼或無法測
  - 改善後：無需改碼即可測
  - 改善幅度：導入成本低，但執行期有性能/工具限制（僅測試環境）

Learning Points
- 核心知識點：Shims 攔截原理與適用範圍
- 技能要求：測試框架整合
- 延伸思考：性能與授權成本權衡

Practice Exercise
- 基礎練習：設定 ShimDateTime.NowGet（30 分）
- 進階練習：只針對特定測試範圍啟用（2 小時）
- 專案練習：遺留系統導入 Fakes 測試套件（8 小時）

Assessment Criteria
- 功能完整性（40%）：成功攔截
- 程式碼品質（30%）：測試邏輯清晰
- 效能優化（20%）：限制影響範圍
- 創新性（10%）：結合多策略使用


## Case #11: 以介面注入 IDateTimeProvider 進行時間抽象

### Problem Statement（問題陳述）
- 業務場景：希望乾淨可測且可替換時間來源；生產用實際時間、測試用假的提供者。
- 技術挑戰：需要改動呼叫點以注入 provider。
- 影響範圍：可測性、擴充性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 依賴 static Now 造成耦合
  2. 無 DI 的介面抽象
- 深層原因：
  - 架構層面：缺少時間 provider
  - 技術層面：需設計與注入
  - 流程層面：需重構呼叫方

### Solution Design（解決方案設計）
- 解決策略：定義 IDateTimeProvider，提供 RealTimeProvider 與 FakeTimeProvider；在測試中注入 fake，生產使用 real。

- 實施步驟：
  1. 設計介面與實作
     - 實作細節：Now 屬性；Fake 可設定 Now
     - 所需資源：.NET/DI
     - 預估時間：1 小時
  2. 注入至業務服務
     - 實作細節：建構子注入 provider
     - 所需資源：同上
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```csharp
public interface IDateTimeProvider { DateTime Now { get; } }
public class RealTimeProvider : IDateTimeProvider { public DateTime Now => DateTime.Now; }
public class FakeTimeProvider : IDateTimeProvider
{
    private DateTime _now;
    public FakeTimeProvider(DateTime now) => _now = now;
    public DateTime Now => _now;
    public void Advance(TimeSpan delta) => _now = _now.Add(delta);
}
// 使用
public class ReportService
{
    private readonly IDateTimeProvider _clock;
    public ReportService(IDateTimeProvider clock) { _clock = clock; }
}
```

- 實際案例：文章提及策略 #1（interface）
- 實作環境：.NET/DI
- 實測數據：
  - 改善前：不可替換
  - 改善後：可注入、可測
  - 改善幅度：測試覆蓋與可維護性提升

Learning Points
- 核心知識點：依賴反轉（DIP）與時間抽象
- 技能要求：DI 容器、測試注入
- 延伸思考：可加入時區/文化資訊

Practice Exercise
- 基礎練習：建立 provider 與測試（30 分）
- 進階練習：支援 Advance/Freeze（2 小時）
- 專案練習：全域替換時間來源（8 小時）

Assessment Criteria
- 功能完整性（40%）：可注入與替換
- 程式碼品質（30%）：介面設計合理
- 效能優化（20%）：無過度開銷
- 創新性（10%）：時區支持


## Case #12: 用 SystemTime 靜態包裝器集中控制 Now

### Problem Statement（問題陳述）
- 業務場景：希望 minimal 變更，集中改用 SystemTime.Now，而非大量 DI。
- 技術挑戰：仍是全域靜態狀態，需小心使用。
- 影響範圍：替換成本小、風險可控。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 不想大改架構
  2. 需要可控 Now
- 深層原因：
  - 架構層面：選擇集中點替換
  - 技術層面：提供 Hook 設定
  - 流程層面：漸進重構策略

### Solution Design（解決方案設計）
- 解決策略：建立 SystemTime 靜態類，預設回傳 DateTime.Now；在測試中覆寫 Delegate，以固定或快轉時間。

- 實施步驟：
  1. 建立 SystemTime
     - 實作細節：Func<DateTime> NowProvider；Reset 還原
     - 所需資源：.NET/C#
     - 預估時間：30 分
  2. 漸進替換呼叫點
     - 實作細節：將 DateTime.Now 替換為 SystemTime.Now
     - 所需資源：IDE/Find&Replace
     - 預估時間：1-2 小時（視規模）

- 關鍵程式碼/設定：
```csharp
public static class SystemTime
{
    public static Func<DateTime> NowProvider = () => DateTime.Now;
    public static DateTime Now => NowProvider();
    public static void Reset() => NowProvider = () => DateTime.Now;
}
// 測試時
SystemTime.NowProvider = () => new DateTime(2000, 1, 1);
```

- 實際案例：文章提及策略 #2（SystemTime static class）
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：無法控制 Now
  - 改善後：集中可控，改動小
  - 改善幅度：導入成本低

Learning Points
- 核心知識點：靜態包裝器與全域狀態風險
- 技能要求：代碼重構
- 延伸思考：結合 Ambient Context/DI 的組合拳

Practice Exercise
- 基礎練習：建置 SystemTime（30 分）
- 進階練習：導入大專案（2 小時）
- 專案練習：搭配事件實作（8 小時）

Assessment Criteria
- 功能完整性（40%）：集中控制成功
- 程式碼品質（30%）：替換一致性
- 效能優化（20%）：無額外負擔
- 創新性（10%）：結合策略模式


## Case #13: 用 OccurTime 標記「應觸發時間」，處理補發與延遲

### Problem Statement（問題陳述）
- 業務場景：快轉或補發事件時，需要清楚知道「這是屬於哪一天的事件」。
- 技術挑戰：實際觸發時間可能晚於應觸發時間。
- 影響範圍：審計/追蹤正確性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未攜帶應觸發時間
  2. 僅能依賴觸發時刻，易造成混淆
- 深層原因：
  - 架構層面：事件定義不完整
  - 技術層面：EventArgs 欠缺上下文
  - 流程層面：審計需求未被考慮

### Solution Design（解決方案設計）
- 解決策略：在 EventArgs 帶入 OccurTime，明示這是「應觸發」的時間點；消費者以 OccurTime 判定歸屬。

- 實施步驟：
  1. 擴充 EventArgs
     - 實作細節：TimePassEventArgs.OccurTime
     - 所需資源：.NET/C#
     - 預估時間：10 分
  2. 調整消費者邏輯
     - 實作細節：以 OccurTime 作為業務判定時間
     - 所需資源：同上
     - 預估時間：30 分

- 關鍵程式碼/設定：
```csharp
public class TimePassEventArgs : EventArgs
{
    public DateTime OccurTime; // 應觸發時間
}
```

- 實際案例：DateTimeUtil 內已有設計
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：追蹤混亂
  - 改善後：審計清楚
  - 改善幅度：錯判率接近 0

Learning Points
- 核心知識點：事件語意設計
- 技能要求：EventArgs 設計
- 延伸思考：加入 CorrelationId/批次號

Practice Exercise
- 基礎練習：在事件中使用 OccurTime（30 分）
- 進階練習：記錄日誌含 OccurTime（2 小時）
- 專案練習：審計報表 PoC（8 小時）

Assessment Criteria
- 功能完整性（40%）：OccurTime 正確傳遞
- 程式碼品質（30%）：語意清晰
- 效能優化（20%）：事件數量大時仍有效
- 創新性（10%）：追蹤擴展設計


## Case #14: 大跨度快轉的誤差控制與（可選）細粒度拆分策略

### Problem Statement（問題陳述）
- 業務場景：一次快轉數月或數年；希望事件 OccurTime 與 Now 差距可控。
- 技術挑戰：單次快轉會導致事件實際觸發時間與 OccurTime 差距較大。
- 影響範圍：審計、監控呈現。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單一大跳產生的時間落差
  2. 未拆分為多次小跳
- 深層原因：
  - 架構層面：未提供拆分快轉選項
  - 技術層面：補發策略僅逐日，不逐步同步 Now
  - 流程層面：PoC 對精度容忍度不同

### Solution Design（解決方案設計）
- 解決策略：提供「分段快轉」選項，例如一次跳一天，逐步觸發事件，每段更新 Now，降低 OccurTime 與 Now 的落差。

- 實施步驟：
  1. 設計分段快轉 API
     - 實作細節：TimePassSegmented(TimeSpan, TimeSpan step)
     - 所需資源：.NET/C#
     - 預估時間：1 小時
  2. 比較兩策略
     - 實作細節：量測 OccurTime-Now 差距
     - 所需資源：同上
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```csharp
public void TimePassSegmented(TimeSpan total, TimeSpan step)
{
    if (total < TimeSpan.Zero || step <= TimeSpan.Zero) throw new ArgumentOutOfRangeException();
    var passed = TimeSpan.Zero;
    while (passed < total)
    {
        var delta = (total - passed) > step ? step : (total - passed);
        TimePass(delta);
        passed += delta;
    }
}
```

- 實際案例：文章中說明了此為可選優化
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：OccurTime 與 Now 可能相差多日
  - 改善後：分段後差距可控（例如控制在 1 天內）
  - 改善幅度：可根據 step 顯著降低

Learning Points
- 核心知識點：精度與成本的權衡
- 技能要求：API 設計
- 延伸思考：在生產替換為排程/訊息總線

Practice Exercise
- 基礎練習：實作分段快轉（30 分）
- 進階練習：量測不同 step 的差距（2 小時）
- 專案練習：加入配置以動態決策 step（8 小時）

Assessment Criteria
- 功能完整性（40%）：可分段快轉
- 程式碼品質（30%）：穩定、可測
- 效能優化（20%）：大量分段仍順暢
- 創新性（10%）：自動 step 調整


## Case #15: 用 C# 事件取代訊息總線的事件驅動 PoC（降維打擊）

### Problem Statement（問題陳述）
- 業務場景：想驗證事件驅動流程（producer/consumer），但不想先搭建 Message Bus。
- 技術挑戰：複雜基礎建設導入成本高，PoC 迭代慢。
- 影響範圍：設計思考被實作成本拖累。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 引入 MQ/Kafka/Rabbit 需大量工作
  2. PoC 重點在流程，不是 infra
- 深層原因：
  - 架構層面：可用語言層事件替代
  - 技術層面：需要嚴謹的對應關係
  - 流程層面：先驗證概念再擴充

### Solution Design（解決方案設計）
- 解決策略：用 C# event 模擬事件發佈/訂閱。以 RaiseDayPassEvent 代表每日訊息，消費者訂閱並執行對應邏輯，完成事件驅動 PoC。

- 實施步驟：
  1. 定義事件介面
     - 實作細節：EventArgs/事件發佈點
     - 所需資源：.NET/C#
     - 預估時間：30 分
  2. 編寫消費者
     - 實作細節：+= 事件處理，寫入結果
     - 所需資源：同上
     - 預估時間：30 分

- 關鍵程式碼/設定：
```csharp
DateTimeUtil.Instance.RaiseDayPassEvent += (sender, args) =>
{
    // 模擬消費者：執行每日任務
    Console.WriteLine($"Do daily job for {args.OccurTime:yyyy/MM/dd}");
};
```

- 實際案例：文章多次強調用 event 驅動 PoC 的思路
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：需要搭建 MQ
  - 改善後：用 event 即可驗證流程
  - 改善幅度：PoC 時程大幅縮短

Learning Points
- 核心知識點：事件驅動設計模型、語言層 vs Infra 層
- 技能要求：事件訂閱、委派
- 延伸思考：映射到實際訊息總線後的語意一致性

Practice Exercise
- 基礎練習：以事件觸發實作每日任務（30 分）
- 進階練習：多消費者並行（2 小時）
- 專案練習：將事件序列化/持久化（8 小時）

Assessment Criteria
- 功能完整性（40%）：事件正確觸發/消化
- 程式碼品質（30%）：解耦良好
- 效能優化（20%）：多消費者表現
- 創新性（10%）：與真實總線對應策略


## Case #16: 以 C# 介面設計先行，後映射到 HTTP API（降維打擊）

### Problem Statement（問題陳述）
- 業務場景：微服務 API 設計複雜，若先做完整 Client/Server/Infra，驗證週期過長。
- 技術挑戰：設計容易卡在傳輸細節，忽略核心概念。
- 影響範圍：設計品質、產出時效。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 同步處理太多維度（infra/security/reliability）
  2. 無法專注於介面抽象
- 深層原因：
  - 架構層面：缺乏降維策略
  - 技術層面：接口到 HTTP 的對應未分離
  - 流程層面：PoC 不純粹

### Solution Design（解決方案設計）
- 解決策略：先以 C# Interface 定義服務邊界、模型、錯誤；以 in-memory 實作驗證行為；待通過後再對應到 HTTP 層。

- 實施步驟：
  1. 設計介面與模型
     - 實作細節：IOrderService.PlaceOrder(...), IReportService.GenerateMonthlyReport(...)
     - 所需資源：.NET/C#
     - 預估時間：1-2 小時
  2. In-memory 實作與測試
     - 實作細節：集合/字典存放資料，LINQ 查詢
     - 所需資源：同上
     - 預估時間：2-4 小時
  3. 對應到 HTTP（後續）
     - 實作細節：ASP.NET Controller 實作介面
     - 所需資源：ASP.NET Core
     - 預估時間：2-4 小時

- 關鍵程式碼/設定：
```csharp
public interface IOrderService
{
    Task<OrderResult> PlaceOrder(OrderRequest request, DateTime now);
}
public class InMemoryOrderService : IOrderService
{
    private readonly List<Order> _orders = new();
    public Task<OrderResult> PlaceOrder(OrderRequest request, DateTime now)
    {
        _orders.Add(new Order { Id = Guid.NewGuid(), CreatedAt = now });
        return Task.FromResult(new OrderResult { Success = true });
    }
}
// PoC 中用 DateTimeUtil.Instance.Now 傳入 now，後續再映射至 Controller 中的 clock
```

- 實際案例：文章「降維打擊」段落
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：需同時處理 infra/security/scale
  - 改善後：先驗證概念，縮短週期
  - 改善幅度：設計迭代速度顯著提升（質化）

Learning Points
- 核心知識點：介面先行、分離 concerns
- 技能要求：抽象建模、TDD/PoC
- 延伸思考：契約測試、OpenAPI 對應

Practice Exercise
- 基礎練習：定義/實作 IOrderService（30 分）
- 進階練習：以 LINQ 完成查詢 PoC（2 小時）
- 專案練習：對應到 ASP.NET Controller（8 小時）

Assessment Criteria
- 功能完整性（40%）：介面與行為正確
- 程式碼品質（30%）：抽象清晰
- 效能優化（20%）：in-memory 效率
- 創新性（10%）：映射策略


-----------------------
案例補充：對應文章中的三段測試可成為獨立教學實戰

## Case #17: 單元測試：TimePassTest（時間快轉與自然流動）

### Problem Statement
- 業務場景：驗證 Init/TimePass/Sleep 行為是否影響 Now 如預期。
- 技術挑戰：需考慮誤差容忍。
- 影響範圍：基礎行為正確性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：Now 受實時計時影響
- 深層原因：測試需容忍小誤差

### Solution Design
- 解決策略：設定 tolerance，以誤差 < 1 秒判定。

- 實施步驟：
  1. Init 固定起點
  2. 逐步 TimePass/GoNext 並斷言

- 關鍵程式碼/設定：
```csharp
DateTimeUtil.Init(new DateTime(2002,10,26,12,0,0));
TimeSpan tolerance = TimeSpan.FromSeconds(1);
Assert.IsTrue(DateTimeUtil.Instance.Now - new DateTime(2002,10,26,12,0,0) < tolerance);
DateTimeUtil.Instance.TimePass(TimeSpan.FromMinutes(15));
```

- 實測數據：
  - 前：測試難以穩定重現
  - 後：可穩定驗證
  - 幅度：可靠性提升

Learning Points：offset、容忍誤差
Practice：完成整段測試（30 分）
Assessment：測試穩定通過


## Case #18: 單元測試：TimePassWithEventTest（跨日補發計數）

### Problem Statement
- 業務場景：一次快轉多日，應觸發跨日事件 N 次。
- 技術挑戰：逐日補發計數須正確。
- 影響範圍：排程可靠性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：單跳多天需補發
- 深層原因：未設補發機制

### Solution Design
- 解決策略：迴圈補發、計數器斷言

- 實施步驟：
  1. 註冊事件計數
  2. 快轉 35 天 15 小時，斷言 36

- 關鍵程式碼/設定：
```csharp
int count = 0;
DateTimeUtil.Instance.RaiseDayPassEvent += (_, __) => count++;
DateTimeUtil.Instance.GoNextHours(15).GoNextDays(35);
Assert.AreEqual(36, count);
```

- 實測數據：計數符合預期（36）
- Learning Points：補發策略
- Practice：不同跨度組合（30 分）
- Assessment：邊界情境完整


## Case #19: 單元測試：RealtimeEventTest（跨日延遲補發）

### Problem Statement
- 業務場景：程式閒置跨日，呼叫 Now 後應補發事件。
- 技術挑戰：非即時觸發但語意正確。
- 影響範圍：使用說明需清楚。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：無背景 Thread
- 深層原因：PoC 設計權衡

### Solution Design
- 解決策略：Sleep 後呼叫 Now，驗證補發觸發

- 實施步驟：
  1. Init 在跨日前 2 秒
  2. Sleep 5 秒
  3. 呼叫 Now 使事件補發

- 關鍵程式碼/設定：
```csharp
DateTimeUtil.Init(new DateTime(2002,10,25,23,59,58));
int count = 0;
DateTimeUtil.Instance.RaiseDayPassEvent += (_, __) => count++;
Thread.Sleep(5000);
Assert.AreEqual(0, count);
var now = DateTimeUtil.Instance.Now;
Assert.AreEqual(1, count);
```

- 實測數據：補發如預期
- Learning Points：事件延遲語意
- Practice：多次 Sleep 與 Now 序列（30 分）
- Assessment：斷言邏輯清晰


-----------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 2, 5, 7, 8, 11, 12, 17, 18, 19
- 中級（需要一定基礎）
  - Case 1, 3, 4, 6, 9, 10, 14, 15, 16
- 高級（需要深厚經驗）
  - 無（本文重心為 PoC 與測試設計，刻意避免過度複雜）

2) 按技術領域分類
- 架構設計類
  - Case 1, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16
- 效能優化類
  - Case 3, 14
- 整合開發類
  - Case 6, 7, 9, 16
- 除錯診斷類
  - Case 8, 17, 18, 19
- 安全防護類
  - Case 9（JWT 測試）

3) 按學習目標分類
- 概念理解型
  - Case 1, 2, 4, 13, 15, 16
- 技能練習型
  - Case 7, 8, 11, 12, 17, 18, 19
- 問題解決型
  - Case 3, 5, 6, 9, 10, 14
- 創新應用型
  - Case 14, 15, 16


案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 2（offset 思維）、Case 8（誤差容忍）
  - 再看 Case 1（DateTimeUtil 全貌）
- 依賴關係：
  - Case 3（跨日補發）依賴 Case 1/2
  - Case 5（禁止倒流）、Case 13（OccurTime）依賴 Case 1
  - Case 6（每月 15 日 02:00）依賴 Case 1/3
  - Case 7（UI 快轉）依賴 Case 1
  - 測試三兄弟 Case 17/18/19 依賴 Case 1/2/3/4/8
  - 替代策略：Case 10（Fakes）、Case 11（介面）、Case 12（SystemTime）與 Case 1 為平行替代選項
  - 進階優化：Case 14（分段快轉）依賴 Case 3
  - 降維打擊：Case 15（事件驅動）、Case 16（介面先行）可搭配 Case 1/3 應用
- 完整學習路徑建議：
  1) 基礎概念與穩定測試：Case 2 → Case 8 → Case 1
  2) 事件與補發：Case 3 → Case 13 → Case 5 →（可選）Case 4 → Case 14
  3) 實戰應用：Case 6 → Case 7 → Case 9
  4) 測試演練：Case 17 → Case 18 → Case 19
  5) 策略比較與架構思維：Case 12 → Case 11 → Case 10 → Case 15 → Case 16

此套路徑先建立可控時間與穩定測試的基本功，再前進到事件補發與 PoC 實戰，最後以策略比較與降維打擊強化架構視野與遷移能力。
