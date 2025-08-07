# [架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用  

# 問題／解決方案 (Problem/Solution)

## Problem: 在單元測試中無法精確控制 `DateTime.Now`

**Problem**:  
‒ 在撰寫 C# 單元測試時，程式碼若直接呼叫 `DateTime.Now`，測試結果會隨「執行當下」而變動，導致測試無法重複、難以驗證 Y2K、閏年或 Token 到期等情境。

**Root Cause**:  
‒ `DateTime.Now` 是 `System.DateTime` 的 static property，編譯期就已靜態繫結；  
‒ 由於 static 呼叫無法用 DI / Wrapper 置換，測試框架很難「注入」可預期的時間值。

**Solution**:  
‒ 採 Ambient Context 策略自製 `DateTimeUtil` (Singleton)。  
‒ 介面設計：  

```csharp
public class DateTimeUtil
{
    public static DateTimeUtil Instance => _instance;
    public static void Init(DateTime expectedTimeNow); // 設定基準點
    public static void Reset();                        // 清除重來

    public DateTime Now { get; }                       // 取代 DateTime.Now
    public void TimePass(TimeSpan span);               // 時間快轉
    public DateTimeUtil GoNextDays(int days=1);        // sugar
    public DateTimeUtil GoNextHours(int hours);        // sugar
    public event EventHandler<TimePassEventArgs> RaiseDayPassEvent; // 跨日事件
}
```

‒ 核心做法：  
  1. 在 `Init()` 時計算「期望時間 – 真實時間」的 `_realtime_offset`。  
  2. 每次呼叫 `Now` 時回傳 `DateTime.Now + _realtime_offset`。  
  3. 透過 `TimePass()` 調整 `_realtime_offset` 實現「時光快轉」。  
‒ 不需改動既有程式，只要把 `DateTime.Now` 換成 `DateTimeUtil.Instance.Now`。  

**Cases 1** – JWT Token 測試過期問題  
‒ 過去測試硬寫死 3 年期限，3 年後測試會失敗。  
‒ 解法：在 `[TestInitialize]` 中先  
```csharp
DateTimeUtil.Init(new DateTime(2022,05,01));
DateTimeUtil.Instance.TimePass(TimeSpan.FromYears(5));   // 快轉 5 年
```  
‒ 測試永遠可重製，不受真實日期影響。  

**Cases 2** – `TimePassTest`  
‒ 透過 `GoNextHours()`、`TimePass()`、`Thread.Sleep()` 驗證 `Now` 皆與預期誤差 <1s。  

**Cases 3** – `TimePassWithEventTest`  
‒ 快轉 35 天 15 Hr，`RaiseDayPassEvent` 應觸發 36 次；單元測試確認計數器=36。  


## Problem: PoC / Demo 需要快速推進時間並觸發排程事件

**Problem**:  
‒ 例如「每月 15 日 02:00 產出月結報」的流程，如果要 Demo 就得等真實時間或調整系統時鐘，效率低且難呈現 UI 互動。

**Root Cause**:  
‒ 真實時鐘速度固定；  
‒ `System.Timer`、排程 Job 皆依賴系統時間，無法在數秒內重現多日、多月行為。

**Solution**:  
‒ 同樣利用 `DateTimeUtil`：  
  1. `TimePass()`、`GoNextDays()`、`GoNextHours()` 快速推進邏輯時鐘；  
  2. 內建 `RaiseDayPassEvent`，當 `Now` 跨過 00:00:00 自動觸發，供報表或批次任務訂閱；  
  3. Demo 時可在 UI 加「+1 Day」、「+1 Hour」按鈕，即時跳轉。  

**Cases 1** – 月結報表 Demo  
‒ Demo 過程：使用者下單 → 按「+15 Days」→ 系統即刻觸發 `RaiseDayPassEvent`，產生報表並於 UI 顯示，整個流程無須等待真實 15 天。  

**Cases 2** – `RealtimeEventTest`  
‒ 起始 `2002/10/25 23:59:58`， sleep 5 秒後透過 `Now` 取值才觸發隔日事件；驗證「真實時間推進＋人工取值」亦能補發事件。  


## Problem: Microsoft Fakes 方案過重，無法覆蓋 PoC 與 Runtime 場景

**Problem**:  
‒ 市面現成的解法如 Microsoft Fakes 雖能 Shim `DateTime.Now`，但需 VS Enterprise、Runtime 重寫 IL、效能下降，且只適合純 Unit Test，無法在 PoC / Demo / 產品原型裡長時間跑。

**Root Cause**:  
‒ Shims 需在執行期攔截所有呼叫並改寫代理，屬「葉克膜式」重裝；  
‒ 授權(CAL)與效能限制阻礙跨團隊、跨環境 (Dev / CI / Demo Server)。  

**Solution**:  
‒ 捨棄 Fakes，改用輕量 `DateTimeUtil`：  
  • 無額外 IDE / 授權要求；  
  • 無 Runtime Injection，效能近乎零額外成本；  
  • 不只能跑 Unit Test，也可直接嵌入 PoC、長時間 Prototype。  

**Cases 1** – 專案組 Prototype  
‒ 團隊將 `DateTimeUtil` 直接放進原型專案，相容 VS Community / Rider；  
‒ Demo 部署到 Linux 容器亦無相依性問題；  
‒ 減少 1/3 準備環境時間，免除授權成本。  

**Cases 2** – CI/CD Pipeline  
‒ 過去 Fakes 僅能在 Windows Build Agent；導入 `DateTimeUtil` 後，Pipeline 可切到 Linux runner，Build 時間下降 20%，費用降低。  