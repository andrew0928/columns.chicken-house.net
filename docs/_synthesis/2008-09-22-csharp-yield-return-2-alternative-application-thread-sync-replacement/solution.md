---
layout: synthesis
title: "[C# yield return] #2. 另類的應用 - Thread Sync 替代方案"
synthesis_type: solution
source_post: /2008/09/22/csharp-yield-return-2-alternative-application-thread-sync-replacement/
redirect_from:
  - /2008/09/22/csharp-yield-return-2-alternative-application-thread-sync-replacement/solution/
---

## Case #1: 用 yield return 取代 Thread Sync 的同步替代方案

### Problem Statement（問題陳述）
**業務場景**：在 xAxB 猜數字遊戲中，GameHost 與 Player 需要頻繁互動。原設計以兩個執行緒運作，透過 AutoResetEvent 與共用變數進行等待/喚醒與資料交換。題目需要進行上萬次互動測試，任何額外的同步成本都會被放大，導致整體執行時間大幅拉長。  
**技術挑戰**：如何在不破壞 Player 連續邏輯與狀態的前提下，消除跨執行緒等待/喚醒的高成本。  
**影響範圍**：單輪同步至少 10 ms 的等待時間，疊加十幾萬次會造成顯著效能下降，且同步邏輯讓程式更難維護。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 使用 AutoResetEvent 等待/喚醒，涉及 OS 層級切換，單次成本高。
2. 兩個執行緒互等導致 CPU 閒置與背景切換，提高延遲。
3. 邏輯切割在多個回呼之間，Player 狀態需被手動保存，增加複雜度。

**深層原因**：
- 架構層面：以多執行緒解問題，但本質是「協作式切換」，適合用協程/迭代器模型。
- 技術層面：不必要地引入多執行緒與同步原語。
- 流程層面：以「被動回呼」分段 Player 邏輯，非自然的控制流程。

### Solution Design（解決方案設計）
**解決策略**：以 C# yield return 將 Player 思考流程改為 Iterator。GameHost 成為「驅動者」，透過 MoveNext 推進 Player 的狀態機，每一次 yield 就是一個「同步點」。這樣「同步」退化為單執行緒內的控制權交還，避免 OS 同步成本，同時保留 Player 邏輯的連續性。

**實施步驟**：
1. 將 Player 規劃為 Iterator
- 實作細節：把 Think() 改為 IEnumerable<HintRecord>，用 yield return 送出問題。
- 所需資源：C# 2.0+ 語言特性（yield return）。
- 預估時間：1 小時。

2. 以 Enumerator Pump 取代 Wait/Signal
- 實作細節：GameHost 以 MoveNext 推進，並在 Current.Hint 回填答案。
- 所需資源：現有 GameHost 呼叫點。
- 預估時間：1 小時。

3. 移除 AutoResetEvent 與同步原語
- 實作細節：刪除等待/喚醒，改以 Current 資料交換。
- 所需資源：程式碼重構。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
// Player 端（YieldPlayer）
public abstract IEnumerable<HintRecord> Think();
private IEnumerator<HintRecord> _enum;

public override int[] StartGuess(int maxNum, int digits) {
    base.StartGuess(maxNum, digits);
    _enum = Think().GetEnumerator();
    _enum.MoveNext(); // 取得第一個問題
    return _enum.Current.Number;
}

public override int[] GuessNext(Hint lastHint) {
    _enum.Current.Hint = lastHint; // 回填上一題答案
    if (_enum.MoveNext()) return _enum.Current.Number;
    throw new InvalidOperationException("Player Stopped!");
}
```

實際案例：文章將原 ThreadSync 的 AsyncPlayer 改寫為基於 yield 的 YieldPlayer，保留邏輯連續性並消除同步成本。  
實作環境：C#（yield return 支援版本，2.0+），.NET Framework。  
實測數據：  
改善前：每次同步至少 10 ms，十幾萬次互動造成大量累積延遲。  
改善後：與直接手寫版本差異可忽略，與 DarkThread 版本相當。  
改善幅度：作者描述「差異小到可以不理它」。

Learning Points（學習要點）
核心知識點：
- yield return 編譯為狀態機，可自然保留流程狀態
- 單執行緒協作式切換可替代多執行緒同步
- Enumerator Pump 模式（由呼叫端推進協程）

技能要求：
- 必備技能：C# iterator、IEnumerable/IEnumerator
- 進階技能：狀態機拆解、併發替代設計

延伸思考：
- 適用廣泛的「回合式互動」或「管線處理」場景
- 風險：不能跨多執行緒共享 Enumerator；需小心 Current 的生命週期
- 可加入診斷計數器衡量每次互動耗時、GC 壓力

Practice Exercise（練習題）
- 基礎練習：把回呼式流程改為 yield iterator（30 分）
- 進階練習：為 iterator 加入超時與中斷控制（2 小時）
- 專案練習：把整個 GameHost/Player 同步版遷移至 yield 版並加上基準測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確完成所有互動輪次
- 程式碼品質（30%）：Iterator 清晰、無共享狀態污染
- 效能優化（20%）：同步開銷顯著下降
- 創新性（10%）：善用語言特性替代同步原語


## Case #2: 以 Iterator 保留 Player 連續邏輯避免「被迫切段」

### Problem Statement（問題陳述）
**業務場景**：GameHost 維持主控，需在多次呼叫之間向 Player 取得下一步猜測。原設計因回呼將 Player 思考拆成數段，使推理流程被迫分裂在多個方法中，狀態必須手動保存。  
**技術挑戰**：讓 Player 的推理能以自然連續的流程表達，不需在多個回呼之間顧及臨時狀態保存。  
**影響範圍**：可讀性與可維護性差，新增策略時成本高、容易出錯。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 回呼模型強迫把長流程切段。
2. 臨時狀態需在 class 欄位或參數間傳遞，污染介面。
3. 思考過程與「同步機制」耦合，邏輯難以聚焦。

**深層原因**：
- 架構層面：控制流程由外部主控，未提供連續式的表達模型。
- 技術層面：缺少語言級狀態機支援前的手工狀態管理。
- 流程層面：回呼固定節奏限制了算法組織方式。

### Solution Design（解決方案設計）
**解決策略**：把 Player 的邏輯寫在 Think() 迭代器中，遇到「要提問」的節點就 yield return 一個 HintRecord。編譯器把這段程式轉為狀態機，隱式保存所有局部變數與進度，讓程式碼保持線性可讀。

**實施步驟**：
1. 把思考流程移入 Think()
- 實作細節：透過 while/for 和 yield return 將每次提問自然切點化。
- 所需資源：C# yield。
- 預估時間：0.5 小時。

2. 用 Current 交換資料
- 實作細節：GameHost 回填 Current.Hint 即可，無須額外狀態欄位。
- 所需資源：HintRecord 結構。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
public override IEnumerable<HintRecord> Think() {
    // 以線性流程撰寫推理
    while (true) {
        // 在自然節點產生提問
        yield return this.GameHost_AskQuestion(this.randomGuess());
        // 可在此接續使用 GameHostAnswer 做推理
    }
}
```

實際案例：DummyYieldPlayer 的 Think() 僅以 while(true) + yield return 寫出連續流程。  
實作環境：C#/.NET。  
實測數據：非效能向，重在可讀性；作者回饋可維護性明顯提升。

Learning Points（學習要點）
- yield 將流程自動狀態化，保持線性敘事
- Current 作為當前交互上下文
- 去除回呼帶來的樣板與狀態污染

技能要求：
- 必備：IEnumerable/IEnumerator 使用
- 進階：把業務流程切點化的能力

延伸思考：
- 其他可用場景：工作流、對話機器人、回合制 AI
- 限制：不適用需要真正並行的重 CPU 任務
- 優化：將推理步驟模組化為可測迭代片段

Practice Exercise（練習題）
- 基礎：把兩段式回呼改為單一 Think() + yield（30 分）
- 進階：在每次 yield 後讀取上一 Hint 並調整策略（2 小時）
- 專案：設計一套可插拔的猜數策略，均以 iterator 實作（8 小時）

Assessment Criteria
- 功能完整性（40%）：策略能正確完整運作
- 程式碼品質（30%）：流程連續、清楚
- 效能優化（20%）：無不必要暫存/複製
- 創新性（10%）：策略模組化程度


## Case #3: 以 HintRecord 共享物件解決迭代器單向資料流

### Problem Statement（問題陳述）
**業務場景**：迭代器天然是「單向輸出」（Player 丟問題）。但 GameHost 需把答案回傳給 Player，形成雙向資料流。  
**技術挑戰**：如何在 IEnumerable 模型中實現雙向溝通，不破壞迭代器語義。  
**影響範圍**：若無法回填答案，Player 無法根據上一輪提示做推理。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. yield return 只能由迭代器方法往外丟資料。
2. IEnumerator.Current 為唯讀屬性，但可承載可變物件參考。
3. 缺少「把答案帶回去」的自然機制。

**深層原因**：
- 架構層面：Iterator 設計偏向單向流式處理。
- 技術層面：需要共用可變物件作為交換容器。
- 流程層面：需對每輪建立提問/回答的握手協議。

### Solution Design（解決方案設計）
**解決策略**：定義 HintRecord 作為提問容器，包含 Number 與 Hint。Player yield return HintRecord；GameHost 在 Current.Hint 回填答案；Player 於下一次繼續點讀取 GameHostAnswer（指向最後一個 HintRecord）。

**實施步驟**：
1. 建立 HintRecord 作為資料容器
- 實作細節：持有 Number（問題）與 Hint（回答）。
- 所需資源：POCO 類別。
- 預估時間：0.5 小時。

2. 在 GameHost 回填答案
- 實作細節：在 GuessNext 先 _enum.Current.Hint = lastHint 再 MoveNext。
- 所需資源：現有 API。
- 預估時間：0.5 小時。

3. Player 讀取 GameHostAnswer
- 實作細節：Think() yield return 之後即能讀取 last_record。
- 所需資源：GameHostAnswer 屬性。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
protected virtual HintRecord GameHost_AskQuestion(int[] number) {
    this.last_record = new HintRecord((int[])number.Clone(), new Hint());
    return this.last_record; // 由 GameHost 回填 last_record.Hint
}

protected HintRecord GameHostAnswer => this.last_record;
```

實際案例：文章以 last_record 屬性共享回合資料，解決雙向溝通。  
實作環境：C#/.NET。  
實測數據：設計層面改善；效能等同直接引用；避免額外拷貝開銷外只 clone number 以防變異。

Learning Points（學習要點）
- 以可變物件承載雙向溝通
- Current 可攜帶可寫資料結構
- clone 防止參考別名帶來的非預期變異

技能要求：
- 必備：.NET 參考型別/值型別語意
- 進階：資料握手協議設計

延伸思考：
- Alternative：使用 Channel/Buffer 封裝，但會退回同步模型
- 風險：多執行緒下需加鎖；本方案假設單執行緒
- 優化：限制 HintRecord 可變區，避免過多共享狀態

Practice Exercise（練習題）
- 基礎：增添 HintRecord 欄位（回合序號）並讓 Host/Player 共用（30 分）
- 進階：引入驗證程式，確保 Host 必回填 Hint（2 小時）
- 專案：實作可序列化的問答紀錄並保存至檔案（8 小時）

Assessment Criteria
- 功能完整性（40%）：雙向資料流可用
- 程式碼品質（30%）：資料不可變界面設計清晰
- 效能優化（20%）：避免不必要拷貝
- 創新性（10%）：握手協議的健全性


## Case #4: Enumerator Pump 設計：StartGuess/GuessNext 控制權交還

### Problem Statement（問題陳述）
**業務場景**：GameHost 需先取得 Player 的第一個猜測，之後每次拿到上輪提示再索取下一猜。  
**技術挑戰**：如何以 IEnumerator 正確實現「首回合初始化」與「回合推進」的呼叫序。  
**影響範圍**：若呼叫順序錯誤將導致 Current 無效或 MoveNext 狀態錯亂。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. IEnumerator 初始時未定位在第一個元素，需先 MoveNext。
2. 必須先回填上一輪 Hint 再推進才有正確的下一猜。
3. 未妥善處理終止，會異常或死循環。

**深層原因**：
- 架構層面：缺少「主動驅動」的明確契約。
- 技術層面：Enumerator 狀態管理不直觀。
- 流程層面：首次呼叫與後續推進需要不同邏輯。

### Solution Design（解決方案設計）
**解決策略**：定義 StartGuess 做 enumerator 初始化與第一個 MoveNext；GuessNext 先回填 Hint 再 MoveNext，並在結束時丟出清楚的訊息，確保呼叫方知道流程終止。

**實施步驟**：
1. 正確初始化 enumerator
- 實作細節：Think().GetEnumerator() + MoveNext()。
- 所需資源：YieldPlayer 基底類。
- 預估時間：0.5 小時。

2. 安全推進與回填
- 實作細節：先 _enum.Current.Hint = lastHint 再 MoveNext。
- 所需資源：GuessNext 介面。
- 預估時間：0.5 小時。

3. 終止處理
- 實作細節：MoveNext false 時丟 InvalidOperationException。
- 所需資源：例外處理。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
public override int[] StartGuess(int maxNum, int digits) {
    base.StartGuess(maxNum, digits);
    _enum = Think().GetEnumerator();
    _enum.MoveNext();
    return _enum.Current.Number;
}

public override int[] GuessNext(Hint lastHint) {
    _enum.Current.Hint = lastHint;
    if (_enum.MoveNext()) return _enum.Current.Number;
    throw new InvalidOperationException("Player Stopped!");
}
```

實際案例：如文中所示，StartGuess/GuessNext 封裝了正確的 pump 節奏。  
實作環境：C#/.NET。  
實測數據：流程正確性提升；錯誤用法快速失敗（例外），便於除錯。

Learning Points（學習要點）
- IEnumerator 初始定位規則
- Pump 節奏：回填→推進→讀取
- 明確的終止訊號與例外

技能要求：
- 必備：迭代器生命週期理解
- 進階：錯誤路徑設計

延伸思考：
- 可將 pump 模式封裝為通用協程驅動器
- 風險：呼叫者若漏回填資料，會造成邏輯錯亂
- 優化：以狀態機 Enum 強化呼叫順序驗證

Practice Exercise（練習題）
- 基礎：寫一個安全的 Pump，檢查必填欄位（30 分）
- 進階：加入回合序號校驗（2 小時）
- 專案：抽象成 CoroutinesRunner 支援多種 iterator（8 小時）

Assessment Criteria
- 功能完整性（40%）：正確推進所有回合
- 程式碼品質（30%）：Pump 介面清楚
- 效能優化（20%）：無多餘呼叫
- 創新性（10%）：可重用性


## Case #5: 移除 AutoResetEvent 等待/喚醒的效能負擔

### Problem Statement（問題陳述）
**業務場景**：原 ThreadSync 作法每回合都需等待/喚醒一次，頻繁到造成整體測試不堪負荷。  
**技術挑戰**：如何在不犧牲控制權交還的前提下，徹底移除等待/喚醒。  
**影響範圍**：每回合至少 10 ms，總體延遲級數上升。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. WaitHandle 等待涉及系統呼叫。
2. 兩執行緒互等導致上下文切換。
3. 喚醒/脈衝時機錯置易出現競態。

**深層原因**：
- 架構層面：用「同步」解決「順序」問題。
- 技術層面：忽略單執行緒可達成的協作式切換。
- 流程層面：等待/喚醒成為回合必要步驟。

### Solution Design（解決方案設計）
**解決策略**：以 yield 迭代替代同步，消除等待/喚醒；回合切換僅為 MoveNext 呼叫與屬性存取，成本極低。

**實施步驟**：
1. 刪除所有 WaitHandle 與事件
- 實作細節：用 Current.Hint 交還資料。
- 所需資源：重構 PR。
- 預估時間：1 小時。

2. 針對熱路徑檢查分支
- 實作細節：確保 Pump 僅包含必要邏輯。
- 所需資源：效能分析工具。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
// 同步移除前：Wait/Set
// After：單純屬性賦值 + MoveNext
_enum.Current.Hint = lastHint;
_enum.MoveNext();
```

實際案例：文章轉為 yield 後達成與手寫版本接近的效能。  
實作環境：C#/.NET。  
實測數據：作者敘述「差異小到可以不理它」，相較同步版大幅降低額外開銷。

Learning Points（學習要點）
- 用控制流替代同步原語
- 熱路徑最小化
- 避免 OS 邊界呼叫

技能要求：
- 必備：性能敏感路徑辨識
- 進階：替代設計的成本/效益評估

延伸思考：
- 需要真正並行時仍需執行緒或 Task
- 注意：Iterator 仍可能造成 GC 壓力（短命物件）
- 可用結構體 enumerator 進一步減壓（C# 7.3+）

Practice Exercise（練習題）
- 基礎：刪除等待/喚醒，替換為 yield（30 分）
- 進階：量測每回合耗時並繪圖（2 小時）
- 專案：基準測試三種實作（同步/執行緒/yield）（8 小時）

Assessment Criteria
- 功能完整性（40%）：行為等價
- 程式碼品質（30%）：熱路徑精簡
- 效能優化（20%）：延遲顯著下降
- 創新性（10%）：方案對比深入


## Case #6: 以訊號 Hint 終止迭代器，實作可控停止

### Problem Statement（問題陳述）
**業務場景**：測試框架需在任意時刻終止 Player。若 Iterator 為 while(true) 將無限產出資料，可能造成資源無法釋放。  
**技術挑戰**：如何在 Iterator 模型下安全終止，避免死循環。  
**影響範圍**：無法停止、造成測試掛死或資源外洩。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. while(true) 的 Iterator 若無停止條件會無限產出。
2. Stop() 僅 MoveNext 但 Think() 不檢查終止，無效。
3. 需明確的「結束訊號」供 Think() 觀察。

**深層原因**：
- 架構層面：終止協議未被寫入迭代邏輯。
- 技術層面：Stop 與 Think 缺乏共同約定。
- 流程層面：測試框架未統一結束事件。

### Solution Design（解決方案設計）
**解決策略**：約定 Hint(A == digits) 或特定旗標為終止訊號。Stop() 設定該訊號並再推進一次；Think() 在 yield 後檢查 GameHostAnswer.Hint，若為終止條件則 yield break。

**實施步驟**：
1. 定義終止條件
- 實作細節：以 A == digits 或 Hint.IsStop。
- 所需資源：模型擴充。
- 預估時間：0.5 小時。

2. 實作 Stop 推進
- 實作細節：Stop 設定 Hint + MoveNext；Try/Catch 只記錄。
- 所需資源：既有 Stop。
- 預估時間：0.5 小時。

3. 在 Think 檢查停止
- 實作細節：每次 yield 後立即檢查是否停止。
- 所需資源：GameHostAnswer。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
public override void Stop() {
    base.Stop();
    _enum.Current.Hint = new Hint(this._digits, 0); // A==digits 作為完成訊號
    try { _enum.MoveNext(); } catch { /* 正常結束或忽略 */ }
}

public override IEnumerable<HintRecord> Think() {
    while (true) {
        yield return GameHost_AskQuestion(randomGuess());
        if (GameHostAnswer.Hint.A == this._digits) yield break; // 終止
    }
}
```

實際案例：文章展示 Stop 設 Hint 並 MoveNext 的做法，建議在 Think 端補上終止檢查。  
實作環境：C#/.NET。  
實測數據：正確性向；避免無限迴圈。

Learning Points（學習要點）
- 終止協議必須雙端一致
- yield break 作為自然結束
- Stop 需要再推進一次讓迭代器觀察訊號

技能要求：
- 必備：yield break 語意
- 進階：跨方法的協議設計

延伸思考：
- 若需「立即」終止，可引入 CancellationToken 風格設計
- 風險：誤判條件導致提前結束
- 優化：以 enum 狀態取代魔術數

Practice Exercise（練習題）
- 基礎：加入 A==digits 即停止（30 分）
- 進階：用旗標 IsStop 取代魔術數（2 小時）
- 專案：統一終止協議，涵蓋多策略 Player（8 小時）

Assessment Criteria
- 功能完整性（40%）：可可靠終止
- 程式碼品質（30%）：無魔術數
- 效能優化（20%）：停止無額外開銷
- 創新性（10%）：協議清晰可擴充


## Case #7: 語言限制下的 yield return 結構化：避免包進子函式

### Problem Statement（問題陳述）
**業務場景**：希望把 yield return 封裝成像 function call 一樣使用，提問後直接得到答案再 return。  
**技術挑戰**：C# 規定 yield 語句必須在 iterator 方法體內，不可任意包進另一個普通方法中。  
**影響範圍**：抽象程度受限，重用性下降，看起來不像一般同步呼叫。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. C# 限制：yield 只能存在於回傳 IEnumerable/IEnumerator 的方法。
2. 無法在普通方法內「暫停並回到呼叫點」。
3. 封裝成函式會破壞 iterator 簽章。

**深層原因**：
- 架構層面：欲以同步抽象表達協程語意。
- 技術層面：語言不支援通用協程關鍵字（C# 目前為 iterator 限定）。
- 流程層面：封裝與語言機制耦合。

### Solution Design（解決方案設計）
**解決策略**：保留 yield 於 Think() 內，改以輕量包裝方法返回容器（如 GameHost_AskQuestion 返回 HintRecord），避免把 yield 移入子函式；或以組合方式將常用片段抽成產生器（generator pattern）。

**實施步驟**：
1. 把 yield 留在 Think()
- 實作細節：以 GameHost_AskQuestion 產物包裝資料。
- 所需資源：現有方法。
- 預估時間：0.5 小時。

2. 將片段抽象為產生器
- 實作細節：建立私有 iterator 方法並 foreach 轉拋 yield return。
- 所需資源：編排邏輯。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
// 錯誤做法：在普通方法內 yield return => 不允許
// 正確：把 yield 放在 Think() 中
public override IEnumerable<HintRecord> Think() {
    foreach (var r in StepGenerator()) yield return r;
}
private IEnumerable<HintRecord> StepGenerator() {
    yield return GameHost_AskQuestion(randomGuess());
}
```

實際案例：文中說明無法把 yield 包成 function call，只能在 iterator 內使用。  
實作環境：C#。  
實測數據：設計限制性質，無量測。

Learning Points（學習要點）
- C# 的 iterator 限定
- 以生成器組合重用片段
- 抽象與語言機制的邊界

技能要求：
- 必備：yield 使用規範
- 進階：產生器組合設計

延伸思考：
- C# 無通用 coroutine 關鍵字；可用 async/await 處理非同步，但語意不同
- 風險：過度抽象反而複雜
- 優化：以命名清晰的方法劃分邏輯區塊

Practice Exercise（練習題）
- 基礎：把 Think 拆成多個產生器（30 分）
- 進階：重用產生器於不同策略（2 小時）
- 專案：建立產生器庫（常見問答片段）（8 小時）

Assessment Criteria
- 功能完整性（40%）：片段可重用
- 程式碼品質（30%）：iterator 結構清楚
- 效能優化（20%）：無多餘產物
- 創新性（10%）：抽象恰當


## Case #8: 用 yield return 建模「協作式時序」取代雙執行緒

### Problem Statement（問題陳述）
**業務場景**：GameHost 與 Player 需輪流執行，原以兩執行緒搭配等待/喚醒達到協作。  
**技術挑戰**：如何讓兩邏輯「各自思考」但仍在單執行緒上正確交替。  
**影響範圍**：多執行緒除效能負擔，亦帶來除錯難度。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 雙執行緒實現協作本質上是在模擬協程。
2. 設計與排程耦合，不利推理。
3. 同步流程噪音掩蓋業務邏輯。

**深層原因**：
- 架構層面：未利用語言提供的協作式模型。
- 技術層面：誤用並行解同步序問題。
- 流程層面：邏輯與同步交織。

### Solution Design（解決方案設計）
**解決策略**：把 Player 寫成 iterator，GameHost 以 pump 推進；兩者交替成為「yield 點」的自然切面。保持「各自思考」且無需真並行。

**實施步驟**：
1. 將切換點對齊 yield
- 實作細節：每個互動節點以 yield 表示。
- 所需資源：Think()。
- 預估時間：1 小時。

2. 移除排程耦合
- 實作細節：刪除執行緒啟動/Join/同步碼。
- 所需資源：重構。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
// 切換點 = yield return
yield return GameHost_AskQuestion(this.randomGuess());
// 交還控制權給 GameHost，再由 MoveNext 回來
```

實際案例：文章用紅藍兩執行緒時序對照 yield 模式，抽掉等待/喚醒仍保留交替。  
實作環境：C#。  
實測數據：除錯簡化、可讀性提升；效能優於雙執行緒等候模式。

Learning Points（學習要點）
- 協程/迭代器與並行的差異
- 切換點設計即流程設計
- 單執行緒也能達成「雙方各自思考」

技能要求：
- 必備：時序圖→程式切點映射
- 進階：協作式架構設計

延伸思考：
- 真並行需要時仍用 Task/Thread
- 風險：長計算阻塞整體
- 優化：切出可中斷的小步驟

Practice Exercise（練習題）
- 基礎：畫出 yield 時序圖（30 分）
- 進階：將一段雙執行緒協作改写為 iterator（2 小時）
- 專案：把一個複雜對話流程以 iterator 建模（8 小時）

Assessment Criteria
- 功能完整性（40%）：交替正確
- 程式碼品質（30%）：切點清晰
- 效能優化（20%）：無同步成本
- 創新性（10%）：時序到程式的映射能力


## Case #9: 產生不重複亂數解的猜測器（DummyYieldPlayer）

### Problem Statement（問題陳述）
**業務場景**：Player 需隨機產生一組不重複的數字作為猜測，符合 xAxB 規則與上限。  
**技術挑戰**：避免重複數字與超出範圍，且需快速生成。  
**影響範圍**：生成錯誤會導致不合法猜測，測試無效。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 直接使用 Random 可能產生重複數字。
2. 沒有額外檢查導致無效結果。
3. 缺少快速去重邏輯。

**深層原因**：
- 架構層面：生成策略與驗證耦合不足。
- 技術層面：未利用集合避免重複。
- 流程層面：缺乏生成-驗證一體化。

### Solution Design（解決方案設計）
**解決策略**：以 List/HashSet 暫存已用數字，循環抽取新數字，若重複則重試；封裝為 randomGuess 方法供 Think() 使用。

**實施步驟**：
1. 去重容器
- 實作細節：使用 List/HashSet 檢查 Contains。
- 所需資源：System.Collections.Generic。
- 預估時間：0.5 小時。

2. 封裝生成函式
- 實作細節：回傳 int[]，由 Think 使用。
- 所需資源：Player 類。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
private int[] randomGuess() {
    int[] ans = new int[this._digits];
    var used = new List<int>();
    for (int i = 0; i < _digits; i++) {
        int r = _rnd.Next(_maxNum);
        while (used.Contains(r)) r = _rnd.Next(_maxNum);
        used.Add(r);
        ans[i] = r;
    }
    return ans;
}
```

實際案例：文章中的 DummyYieldPlayer 採用此生成法。  
實作環境：C#。  
實測數據：足夠應付測試；如需更高效率可用 Fisher-Yates 洗牌。

Learning Points（學習要點）
- 亂數與去重策略
- 效率 vs 簡潔的折衷
- 封裝生成與驗證

技能要求：
- 必備：隨機數與集合操作
- 進階：洗牌演算法

延伸思考：
- 大範圍/高 digits 狀況改用洗牌更快
- 風險：Contains 在 List 上為 O(n)
- 優化：改用 HashSet 降低到 O(1)

Practice Exercise（練習題）
- 基礎：改用 HashSet 去重（30 分）
- 進階：實作 Fisher-Yates（2 小時）
- 專案：可配置策略（隨機/啟發式）（8 小時）

Assessment Criteria
- 功能完整性（40%）：產生合法猜測
- 程式碼品質（30%）：封裝與命名清楚
- 效能優化（20%）：生成時間/空間合理
- 創新性（10%）：策略可插拔


## Case #10: MoveNext 結束時的例外與錯誤路徑設計

### Problem Statement（問題陳述）
**業務場景**：當 Player 無法再提供猜測時，GameHost 仍可能呼叫 GuessNext，需明確錯誤訊息。  
**技術挑戰**：如何在 iterator 結束時提供清晰的錯誤與恢復策略。  
**影響範圍**：錯誤難以診斷，可能造成崩潰或靜默失敗。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. MoveNext 返回 false 代表結束。
2. 呼叫者若未檢查可能誤用。
3. 需要明確例外提示。

**深層原因**：
- 架構層面：未定義終止後行為。
- 技術層面：缺乏錯誤訊號標準。
- 流程層面：呼叫方錯誤流程未實作。

### Solution Design（解決方案設計）
**解決策略**：在 MoveNext 返回 false 時丟出 InvalidOperationException("Player Stopped!")，呼叫端以 try/catch 或流程判斷處理。

**實施步驟**：
1. 擲出語義清楚例外
- 實作細節：GuessNext 當 MoveNext false 時拋例外。
- 所需資源：標準例外。
- 預估時間：0.5 小時。

2. 呼叫端處理
- 實作細節：終止循環或切換策略。
- 所需資源：錯誤處理邏輯。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
if (_enum.MoveNext()) return _enum.Current.Number;
throw new InvalidOperationException("Player Stopped!");
```

實際案例：文章原碼如此實作。  
實作環境：C#。  
實測數據：提高可診斷性；錯誤定位容易。

Learning Points（學習要點）
- iterator 結束語意
- 清晰例外訊息設計
- 呼叫端錯誤流程

技能要求：
- 必備：例外處理
- 進階：可恢復錯誤策略

延伸思考：
- 可自定義 PlayerStoppedException
- 風險：過度使用例外影響效能（非熱路徑無虞）
- 優化：以 Result<T> 回傳亦可

Practice Exercise（練習題）
- 基礎：為 Player 停止新增自訂例外（30 分）
- 進階：在 Host 記錄最後一筆有效猜測（2 小時）
- 專案：設計錯誤碼與統一錯誤處理（8 小時）

Assessment Criteria
- 功能完整性（40%）：停止時行為一致
- 程式碼品質（30%）：錯誤訊息清楚
- 效能優化（20%）：非熱路徑無負擔
- 創新性（10%）：錯誤處理策略


## Case #11: 單執行緒假設與共享狀態安全（last_record）

### Problem Statement（問題陳述）
**業務場景**：使用 last_record 作為問答容器，Host 與 Player 需共用該參考。  
**技術挑戰**：避免出現競態與資料撕裂，確保單執行緒假設成立。  
**影響範圍**：若被跨執行緒存取，可能出現未定義行為。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. last_record 是可變參考型別。
2. Enumerator 與 Host 若在不同執行緒存取需同步。
3. 目前設計假設同一執行緒。

**深層原因**：
- 架構層面：用共享物件傳遞資料。
- 技術層面：缺乏並行安全保護。
- 流程層面：未限制呼叫執行緒模型。

### Solution Design（解決方案設計）
**解決策略**：強制單執行緒模型；必要時加鎖或複製資料。記錄在介面契約中，禁止跨執行緒存取 Enumerator；對數組採用 Clone 防止後續變異。

**實施步蓆**：
1. 明確文件化單執行緒
- 實作細節：XML doc/註解說明。
- 所需資源：文件。
- 預估時間：0.5 小時。

2. 防變異處理
- 實作細節：number.Clone()。
- 所需資源：原碼已實作。
- 預估時間：0.5 小時。

3. 若需跨執行緒則加鎖
- 實作細節：lock(last_record) 或不可變物件替代。
- 所需資源：同步原語。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
// 防止呼叫端改動 number，先 clone
this.last_record = new HintRecord((int[])number.Clone(), new Hint());
```

實際案例：文章中已 clone 陣列，避免外部變異污染狀態。  
實作環境：C#/.NET。  
實測數據：正確性設計；無量測。

Learning Points（學習要點）
- 參考別名與不可變設計
- 單執行緒假設的契約化
- 在必要處 clone 以隔離副作用

技能要求：
- 必備：CLR 記憶體模型基本觀念
- 進階：不可變資料結構

延伸思考：
- 以 record/readonly struct 承載資料
- 風險：過度 clone 造成 GC 壓力
- 優化：在熱路徑上重用緩衝

Practice Exercise（練習題）
- 基礎：為數據容器加上 readonly 屬性（30 分）
- 進階：用不可變型別重寫 HintRecord（2 小時）
- 專案：實作跨執行緒安全版本（8 小時）

Assessment Criteria
- 功能完整性（40%）：資料一致
- 程式碼品質（30%）：契約清晰
- 效能優化（20%）：clone 次數可控
- 創新性（10%）：不可變化應用


## Case #12: 主動回填與觀察順序的契約化（回填→推進→讀取）

### Problem Statement（問題陳述）
**業務場景**：每回合需先把上一輪 Hint 回填，再取下一猜。順序錯誤會造成邏輯錯亂。  
**技術挑戰**：統一定義呼叫順序，避免使用者誤用。  
**影響範圍**：可能導致使用未初始化的 Hint 或取到錯誤的 Number。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Current 的內容在 MoveNext 前後語意不同。
2. 回填順序不可顛倒。
3. 缺少統一說明。

**深層原因**：
- 架構層面：Pump 節奏未正式化。
- 技術層面：Enumerator 容易被誤用。
- 流程層面：強制順序未檢查。

### Solution Design（解決方案設計）
**解決策略**：把「回填→推進→讀取」封裝在 API（GuessNext/StartGuess）中，禁止外部直接操作 Enumerator；提供開發說明。

**實施步驟**：
1. API 封裝
- 實作細節：外界只能透過 GuessNext。
- 所需資源：介面限制。
- 預估時間：0.5 小時。

2. 文件與斷言
- 實作細節：加 Debug.Assert 確保序列。
- 所需資源：診斷。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
public override int[] GuessNext(Hint lastHint) {
    _enum.Current.Hint = lastHint;   // 回填
    if (_enum.MoveNext())            // 推進
        return _enum.Current.Number; // 讀取
    throw new InvalidOperationException("Player Stopped!");
}
```

實際案例：文章已將這個順序固定在 GuessNext。  
實作環境：C#。  
實測數據：正確性設計；無量測。

Learning Points（學習要點）
- 對迭代場景定義呼叫節奏
- 封裝保護正確用法
- 以斷言輔助開發期檢查

技能要求：
- 必備：API 設計
- 進階：契約式設計（Design by Contract）

延伸思考：
- 在 Release 移除斷言避免成本
- 風險：外部仍可反射呼叫內部方法（非一般場景）
- 優化：以狀態列舉機制檢查合法轉移

Practice Exercise（練習題）
- 基礎：寫出 Guard/斷言確保順序（30 分）
- 進階：加入狀態機轉移檢查（2 小時）
- 專案：設計一套 Pump 驗證框架（8 小時）

Assessment Criteria
- 功能完整性（40%）：順序受保護
- 程式碼品質（30%）：API 清楚
- 效能優化（20%）：無額外熱路徑開銷
- 創新性（10%）：契約化實作


## Case #13: 以 Hint(A==digits) 做為完成條件的終局協議

### Problem Statement（問題陳述）
**業務場景**：當 Player 猜中答案，需結束回合。需一個通用的「完成」協議，以避免邏輯分散。  
**技術挑戰**：將終局條件統一為資料層面的訊號，避免流程分支太多。  
**影響範圍**：結束邏輯不一致導致難以維護。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 多處檢查可能造成邏輯重複。
2. 缺少單一終止點。
3. Stop 與完成條件混淆。

**深層原因**：
- 架構層面：未定義結束協議。
- 技術層面：條件分散。
- 流程層面：回合管理鬆散。

### Solution Design（解決方案設計）
**解決策略**：統一使用 Hint.A == digits 為「猜中」訊號；Think 在 yield 後立即檢查，達成則 yield break；Stop 也可產生該訊號迫使終止。

**實施步驟**：
1. 定義完成條件
- 實作細節：介面文件與常數定義。
- 所需資源：模型修訂。
- 預估時間：0.5 小時。

2. Think 檢查
- 實作細節：每輪 yield 後 check。
- 所需資源：GameHostAnswer。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
if (GameHostAnswer.Hint.A == this._digits) {
    yield break; // 完成
}
```

實際案例：Stop 以新 Hint(digits, 0) 傳遞訊號，Think 端應加檢查以完成迭代。  
實作環境：C#。  
實測數據：邏輯一致性提升。

Learning Points（學習要點）
- 以資料訊號驅動流程
- 單一終局條件
- yield break 的應用

技能要求：
- 必備：資料模型設計
- 進階：協議統一與版本化

延伸思考：
- 可考慮加入 IsSolved 屬性避免魔術數
- 風險：不同策略對「完成」定義需對齊
- 優化：引入 Result 型別承載終局資訊

Practice Exercise（練習題）
- 基礎：在 Think 中加入完成檢查（30 分）
- 進階：抽象為 IEndCondition（2 小時）
- 專案：多策略共用終局協議（8 小時）

Assessment Criteria
- 功能完整性（40%）：完成即停止
- 程式碼品質（30%）：無重複條件判斷
- 效能優化（20%）：最小成本檢查
- 創新性（10%）：協議抽象


## Case #14: 從 ThreadSync 遷移到 YieldPlayer 的重構步驟

### Problem Statement（問題陳述）
**業務場景**：既有專案使用雙執行緒 ThreadSync，欲在不改動既有 GameHost 介面的前提下改成 yield 模式。  
**技術挑戰**：控制風險、逐步替換，確保行為等價與效能提升。  
**影響範圍**：涉及 Player 實作、同步碼移除與測試。  
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 同步碼散落各處。
2. Player 以回呼/事件驅動，難一次替換。
3. 測試依賴時序。

**深層原因**：
- 架構層面：耦合同步原語。
- 技術層面：狀態分散。
- 流程層面：缺少回歸測試。

### Solution Design（解決方案設計）
**解決策略**：先在新分支引入 YieldPlayer 實作，並提供相同介面；以特性旗標切換；逐步刪除同步碼；以行為測試與基準測試驗證等價與效能。

**實施步驟**：
1. 建立 YieldPlayer 平行實作
- 實作細節：Think/StartGuess/GuessNext 完整。
- 所需資源：新類別。
- 預估時間：2 小時。

2. 以 Feature Flag 切換
- 實作細節：可環境變數或設定。
- 所需資源：設定檔。
- 預估時間：1 小時。

3. 移除同步碼與重構
- 實作細節：刪 Wait/Signal，保留介面。
- 所需資源：重構支援。
- 預估時間：2-4 小時。

4. 加入測試與基準
- 實作細節：用 DummyPlayer 與 DarkThread 版本對比。
- 所需資源：測試框架。
- 預估時間：2 小時。

**關鍵程式碼/設定**：
```csharp
// 介面不變，實作切換
IPlayer player = useYield ? new DummyYieldPlayer() : new DummyAsyncPlayer();
```

實際案例：文章作者在參賽版採用 yield 實作，與原版效能相當或更好。  
實作環境：C#/.NET。  
實測數據：作者敘述差異可忽略，達成目標。

Learning Points（學習要點）
- 風險控制：雙實作與旗標切換
- 行為等價測試
- 基準測試方法

技能要求：
- 必備：重構技巧、單元測試
- 進階：效能基準

延伸思考：
- 可逐步封存 ThreadSync 版
- 風險：兩套維護期短暫增加成本
- 優化：用介面/工廠管理實作切換

Practice Exercise（練習題）
- 基礎：為 Player 加入雙實作切換（30 分）
- 進階：寫出行為等價測試（2 小時）
- 專案：建立完整遷移計畫與回滾策略（8 小時）

Assessment Criteria
- 功能完整性（40%）：等價行為
- 程式碼品質（30%）：切換清晰
- 效能優化（20%）：基準達標
- 創新性（10%）：風險管控


## Case #15: 以實測驗證：yield 版與基準版效能差異可忽略

### Problem Statement（問題陳述）
**業務場景**：新架構需以實測證明不劣於既有最佳實作（DarkThread 版本）。  
**技術挑戰**：在相同條件下公正比較，排除雜訊。  
**影響範圍**：架構選型與投產決策。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 原 ThreadSync 版過慢，需替代。
2. yield 版需與基準比較可信。
3. 測試次數大、時間敏感。

**深層原因**：
- 架構層面：選型需數據支撐。
- 技術層面：基準設計與執行重要。
- 流程層面：CI 中需重複測試。

### Solution Design（解決方案設計）
**解決策略**：使用 DummyYieldPlayer 在同台機器、同設定下連跑多次，去除極端值，與 DarkThread 版本比較；以「差異可忽略」作為門檻。

**實施步驟**：
1. 基準腳本
- 實作細節：固定隨機種子與輪次。
- 所需資源：測試腳本。
- 預估時間：1 小時。

2. 多次重跑取中位數
- 實作細節：M 次執行取中位。
- 所需資源：測試框架。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
// 偽碼
for (int i=0; i<N; i++) RunAndRecord(playerVariant);
var median = CalcMedian(times);
```

實際案例：作者實測「與 DarkThread 版本差異小到可以不理」。  
實作環境：C#/.NET，同機測試。  
實測數據：差異可忽略（描述性結論）。

Learning Points（學習要點）
- 基準測試設計
- 去除雜訊的方法（多次取中位）
- 門檻定義與決策

技能要求：
- 必備：測試與統計基礎
- 進階：基準自動化

延伸思考：
- 加入 GC/分配統計
- 風險：測試環境不一致
- 優化：固定 CPU 頻率/隔離背景程序

Practice Exercise（練習題）
- 基礎：寫一個簡單基準器（30 分）
- 進階：統計中位/90 百分位（2 小時）
- 專案：CI 中跑標竿回歸（8 小時）

Assessment Criteria
- 功能完整性（40%）：測試可重現
- 程式碼品質（30%）：腳本清晰
- 效能優化（20%）：數據可信
- 創新性（10%）：報表化


## Case #16: 以 GameHost_AskQuestion 封裝提問與資料保留

### Problem Statement（問題陳述）
**業務場景**：每次產生問題都需建立 HintRecord 並確保數據不被後續修改。  
**技術挑戰**：封裝提問行為並避免資料別名問題。  
**影響範圍**：若數據被意外修改，後續推理錯誤。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. int[] 為可變參考。
2. 後續程式可能誤改原陣列。
3. 資料一致性需保護。

**深層原因**：
- 架構層面：提問與狀態保留未封裝好。
- 技術層面：需 clone 保護。
- 流程層面：資料生命週期未界定。

### Solution Design（解決方案設計）
**解決策略**：用 GameHost_AskQuestion 建立 HintRecord，對 Number 做 Clone，保留最後一筆至 last_record，提供 GameHostAnswer 快取存取。

**實施步驟**：
1. 提問封裝
- 實作細節：建立 HintRecord 並保存。
- 所需資源：輔助方法。
- 預估時間：0.5 小時。

2. Clone 防護
- 實作細節：避免原陣列被改動。
- 所需資源：陣列複製。
- 預估時間：0.5 小時。

**關鍵程式碼/設定**：
```csharp
protected virtual HintRecord GameHost_AskQuestion(int[] number) {
    this.last_record = new HintRecord((int[])number.Clone(), new Hint());
    return this.last_record;
}
protected HintRecord GameHostAnswer => this.last_record;
```

實際案例：文章完整展示此封裝。  
實作環境：C#。  
實測數據：正確性與可維護性提升。

Learning Points（學習要點）
- 封裝行為與資料一致性
- clone 的必要性與成本
- 快取最近回合資料

技能要求：
- 必備：API 設計
- 進階：不可變封裝

延伸思考：
- 將 Number 換成不可變型別
- 風險：過度 clone 成本
- 優化：重用陣列池（ArrayPool<T>）

Practice Exercise（練習題）
- 基礎：實作陣列 clone 與測試（30 分）
- 進階：改為不可變包裝（2 小時）
- 專案：以 ArrayPool<T> 最小化分配（8 小時）

Assessment Criteria
- 功能完整性（40%）：資料安全
- 程式碼品質（30%）：封裝良好
- 效能優化（20%）：分配合理
- 創新性（10%）：池化應用


## Case #17: 用 Iterator 抽離「同步噪音」，聚焦演算法

### Problem Statement（問題陳述）
**業務場景**：參賽題著重演算法本身，但同步樣板與排程讓開發者分心。  
**技術挑戰**：清除與演算法無關的樣板碼，讓心力放在「少猜幾次」。  
**影響範圍**：可維護性與可讀性下降，開發效率差。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 同步程式碼大量佔據思考空間。
2. 回呼/事件造成樣板增生。
3. 排程細節與演算法耦合。

**深層原因**：
- 架構層面：未將橫切關注（同步）與核心關注（算法）分離。
- 技術層面：無適當抽象層。
- 流程層面：開發流程未先清空噪音。

### Solution Design（解決方案設計）
**解決策略**：用 iterator 讓每步推理以自然流程呈現，同步噪音完全隱去；GameHost Pump 成為通用基礎設施，演算法專注在 Think()。

**實施步驟**：
1. 抽離 Pump
- 實作細節：Pump 通用化。
- 所需資源：共用基底類。
- 預估時間：1 小時。

2. 策略迭代化
- 實作細節：Think 只描述推理。
- 所需資源：Player 策略。
- 預估時間：1-2 小時。

**關鍵程式碼/設定**：
```csharp
public override IEnumerable<HintRecord> Think() {
    // 專注在策略，不含同步碼
    while (true) {
        yield return GameHost_AskQuestion(NextGuess());
        // 使用 GameHostAnswer 調整策略
    }
}
```

實際案例：作者表示採用 yield 後能「專心研究怎樣才能少猜幾次」。  
實作環境：C#。  
實測數據：開發效率與可讀性提升（質化）。

Learning Points（學習要點）
- 橫切關注分離
- 語言特性降低樣板
- 專注核心價值

技能要求：
- 必備：抽象能力
- 進階：基礎設施化思維

延伸思考：
- 可把紀錄/日誌/度量也抽成橫切
- 風險：過度抽象不易理解
- 優化：以模板方法/策略模式組合

Practice Exercise（練習題）
- 基礎：重寫策略僅保留推理（30 分）
- 進階：將 Pump 提取為基底類（2 小時）
- 專案：新增兩個不同策略並 A/B 測試（8 小時）

Assessment Criteria
- 功能完整性（40%）：策略可運行
- 程式碼品質（30%）：關注點分離
- 效能優化（20%）：無額外成本
- 創新性（10%）：策略多樣性


## Case #18: 以 DummyYieldPlayer 作為對照用的最小可行產品（MVP）

### Problem Statement（問題陳述）
**業務場景**：需要一個行為簡單、可重複驗證的 Player 作為測試基準，便於對比不同架構與策略。  
**技術挑戰**：在最少程式碼下提供穩定、可預測的互動流程。  
**影響範圍**：缺少基準使效能與正確性比較失焦。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 策略複雜會干擾基準。
2. 無共同比較基準。
3. 測試環境可變。

**深層原因**：
- 架構層面：缺少參考實作。
- 技術層面：基準的重要性被忽略。
- 流程層面：測試設計缺基石。

### Solution Design（解決方案設計）
**解決策略**：實作 DummyYieldPlayer 僅以隨機猜測與 yield 提問；藉此檢驗 Pump、問答協議、終止行為與效能。

**實施步驟**：
1. 建立 DummyYieldPlayer
- 實作細節：randomGuess + while(true) yield。
- 所需資源：Player 基底。
- 預估時間：0.5 小時。

2. 對照測試
- 實作細節：與 ThreadSync 版/基準版對比。
- 所需資源：測試腳本。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
public class DummyYieldPlayer : YieldPlayer {
    public override IEnumerable<HintRecord> Think() {
        while (true) {
            yield return this.GameHost_AskQuestion(this.randomGuess());
        }
    }
}
```

實際案例：文章提供 DummyYieldPlayer 以示範與測試。  
實作環境：C#。  
實測數據：作為基準用，行為穩定；效能與手寫版相當。

Learning Points（學習要點）
- 基準角色的價值
- 從最簡開始驗證協議
- 分離策略與架構

技能要求：
- 必備：簡化設計能力
- 進階：基準設計

延伸思考：
- 在 Dummy 上附加度量鉤子
- 風險：過於簡單可能掩蓋真實瓶頸
- 優化：加入可控隨機種子

Practice Exercise（練習題）
- 基礎：加上固定種子以可重現（30 分）
- 進階：度量每回合耗時（2 小時）
- 專案：建立自動化對比報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：可穩定運行
- 程式碼品質（30%）：精簡清楚
- 效能優化（20%）：可量測
- 創新性（10%）：基準可擴充


==============================
案例分類

1. 按難度分類
- 入門級（適合初學者）：#2, #7, #9, #10, #12, #13, #16, #18
- 中級（需要一定基礎）：#1, #3, #4, #5, #8, #11, #15, #17
- 高級（需要深厚經驗）：#6, #14

2. 按技術領域分類
- 架構設計類：#1, #2, #4, #8, #14, #17
- 效能優化類：#1, #5, #15, #16
- 整合開發類：#3, #4, #6, #12, #13, #18
- 除錯診斷類：#10, #11, #15
- 安全防護類（狀態/資料一致性視為安全）：#11, #16

3. 按學習目標分類
- 概念理解型：#2, #7, #8, #13, #17
- 技能練習型：#4, #9, #12, #16, #18
- 問題解決型：#1, #3, #5, #6, #10, #11, #14
- 創新應用型：#1, #8, #15, #17

==============================
案例關聯圖（學習路徑建議）

- 建議起點（概念與最小示例）：
  1) 先學 #18（DummyYieldPlayer 作為基準）→ 2) #2（保持連續邏輯的 iterator 思維）→ 3) #7（yield 語言限制）
- 控制流與資料流（必備基礎）：
  4) #4（Enumerator Pump 節奏）→ 5) #12（回填→推進→讀取契約）→ 6) #3（雙向資料流：HintRecord）
- 終止與協議：
  7) #13（完成條件協議）→ 8) #6（可控停止）
- 效能與設計優化：
  9) #1（用 yield 取代同步）→ 10) #5（移除等待/喚醒成本）→ 11) #16（封裝與 clone 防護）→ 12) #11（共享狀態安全）
- 實作與驗證：
  13) #9（隨機猜測生成）→ 14) #10（錯誤路徑設計）
- 遷移與基準：
  15) #14（從 ThreadSync 遷移）→ 16) #15（基準驗證）
- 完整路徑總結：
  #18 → #2 → #7 → #4 → #12 → #3 → #13 → #6 → #1 → #5 → #16 → #11 → #9 → #10 → #14 → #15 → #17  
  其中：#4 依賴 #2/#7；#6 依賴 #13；#1/#5 依賴 #4/#3；#14 依賴 #1/#5/#4；#15 依賴 #18 與 #14。