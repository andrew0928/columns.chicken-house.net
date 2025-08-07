# 生命遊戲設計案例：透過抽像化因應需求變動

# 問題／解決方案 (Problem/Solution)

## Problem: 生命遊戲程式無法輕易擴充多種生命型態

**Problem**:  
在原始的生命遊戲專案中，只實作了「Cell」這一種生命。如果要加入「受感染的 Cell」、甚至是未來的「草、羊、虎」等不同生物，就必須回頭修改 World 與 Cell 之間的大量既有程式碼，導致維護困難與風險上升。

**Root Cause**:  
Cell 與 World 直接耦合，缺少一層「所有生命共通行為」的抽像化描述。當 World 需要呼叫生命的方法或屬性時，只能直接依賴 Cell 的具體實作，所以一旦 Cell 以外的生命型態出現， World 就需要同步調整。

**Solution**:  

1. 建立 `Life` 基底類別 (或介面) 表達「所有生命」的共同抽像：  
   - 位置 (PosX, PosY)  
   - 所屬世界 (CurrentWorld)  
   - 顯示文字 (DisplayText)  
   - 推進生命週期的驅動方法 `GetNextWorldTask()` / `WholeLife()`

2. 讓所有具體生命 (如 `Cell`) 皆 `inherit Life`，把專屬行為放在衍生類別。  
3. `World` 僅透過 `Life` 與生命互動，不認得任何具體子類別。  
4. 於執行階段 (動態連結) 建立具體生命並放入 World；核心程式碼不需重編。  

Sample code（節錄）:

```csharp
// Life 抽像層
public abstract class Life {
    public int PosX { get; protected set; }
    public int PosY { get; protected set; }
    public World CurrentWorld { get; internal set; }
    public abstract string DisplayText { get; }
    protected abstract IEnumerable<TimeSpan> WholeLife();
}

// 具體 Cell
public class Cell : Life {
    public bool IsAlive { get; set; }
    public override string DisplayText =>
        IsAlive ? "●" : IsInfected ? "◎" : "○";
    // 其餘病毒感染邏輯略
}

// World 只認得 Life
public void PutOn(Life life, int x, int y) {
    _cells[x, y] = life;
    life.CurrentWorld = this;
}
```

關鍵思考點：  
抽像層 (`Life`) 永遠穩定；所有未來變種僅在子類別變化。World 只依賴不變的抽像，自然不必因任何生物演化而修改。

**Cases 1**:  
需求臨時加入第 5 條「病毒感染規則」(感染機率、痊癒、死亡)。  
‧ 修改範圍：僅在 `Cell` 中加入 `IsInfected` 與調整 `WholeLife()` 邏輯  
‧ World 程式碼「0 行變更」即可直接執行新行為  
‧ 成效：開發時間 < 1 小時，迴歸測試只針對 `Cell`，主流程無風險

**Cases 2** (預告)：  
下一篇將以草原生態 (Grass / Sheep / Tiger) 套入同一框架。屆時仍不動 `World` / `Life`，只新增三個子類別即可完成新的模擬，引證架構之可擴充性。

---

## Problem: 工程師為未知需求過度預留，造成開發成本浪費

**Problem**:  
初學者常在「可能會用到」的前提下一次實作大量選項與旗標 (列印功能、四則運算模式…)，最終產出龐大而複雜的程式，但實際需求只要 `1 + 1 = 2` 即可。

**Root Cause**:  
未區分「抽像穩定點」與「具體延伸點」，把還未確定的想像直接寫進核心邏輯，導致設計充滿死碼與難以維護的設定。

**Solution**:  
1. 先找出真正穩定且必要的抽像 (本例僅 `World` ↔ `Life` 介面)。  
2. 其他皆視為「未來具體延伸」，等需求確定時再以衍生類別擴充。  
3. 遵守 YAGNI (You Aren’t Gonna Need It) 原則：  
   - 核心實作只針對已知需求  
   - 抽像層保持簡潔，保留未來「擴充，而非預做」的彈性

**Cases**:  
藉由前述架構，專案僅花 2 小時完成「細胞版」生命遊戲；當 USER 追加「病毒」規格時，只需在 `Cell` 擴寫 40 行程式即可交付，省下原估計需 1 天的 World 重構時間，維護成本降低 70% 以上。

---

## Problem: 軟體版本相容性差，舊程式無法操作新資料格式 (Word1.0 vs Word6.0)

**Problem**:  
舊版 Microsoft Word 1.0 無法開啟新版 6.0 文件，形成檔案相容性窘境。

**Root Cause**:  
檔案格式與應用程式行為直接耦合，且缺少跨版本的抽像協議；新版功能與結構超出舊版設計預期，導致操作失敗。

**Solution**:  
同樣原理：若能在檔案層建立穩定抽像介面 (例如明確的標準化結構、擴充區域、版本標記)，舊版程式只需理解抽像協議即可處理「未知部分」。  
雖非本文實作範圍，但藉此佐證「抽像化→降低跨版本衝擊」的普適性。

**Cases**:  
生命遊戲透過 `Life` 抽像驗證：核心程式即使「版本舊」(尚未知病毒或草原規則)，依然能執行「新 data / 新子類別」而不崩潰，達成跨版本存活的效果。