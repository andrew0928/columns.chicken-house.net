# [C# yield return] 另類的應用 ‑ Thread Sync 替代方案

# 問題／解決方案 (Problem/Solution)

## Problem: 在 GameHost 與 Player 之間維持「獨立思考」卻又要高速互動

**Problem**:  
在「xAxB 猜數字」比賽中，為了讓 `GameHost` 與 `Player` 彼此「獨立思考」，作者一開始採用兩條獨立執行緒 (Thread) 搭配 `AutoResetEvent` 做同步。  
情境：  
1. `GameHost` 啟動後等待 `Player` 提問。  
2. `Player` 計算完問題後，透過事件喚醒 `GameHost`。  
3. `GameHost` 回答後再喚醒 `Player`。  
4. 上述動作在一次遊戲內要反覆執行數十萬次。  
結果：每一次同步（Wait / Set）平均耗時約 10 ms，累積下來導致整體執行時間大幅增加。

**Root Cause**:  
1. OS 執行緒的「等待→喚醒」牽涉到排程與 context switch，本身就昂貴。  
2. 問題本質只是「把控制權來回交給對方並交換資料」，卻動用完整的執行緒同步機制，成本完全不成比例。  
3. 為了避免函式呼叫打斷邏輯，才選擇 Thread，但「保持邏輯連續」並不一定非得用 Thread。

**Solution**: 以 `yield return` 取代 Thread Sync  
1. 把 `Player` 的核心邏輯改寫成 iterator：  
   ```csharp
   public abstract IEnumerable<HintRecord> Think();
   ```  
   ‑ 透過 `yield return`，一次丟出一個 `HintRecord` (題目)。  
2. `GameHost` 取得 enumerator 後，只需不斷呼叫 `MoveNext()` / 讀取 `Current`：  
   ```csharp
   this._enum = this.Think().GetEnumerator();
   this._enum.MoveNext();                 // 取第一題
   var num = this._enum.Current.Number;   // 問題
   ```  
3. `GameHost` 算完答案，再把結果填回共用欄位 (`Hint`) 後呼叫 `MoveNext()`，控制權自然回到 `Think()` 當前 `yield return` 之後，邏輯不中斷。  
4. 底層完全不需 Thread；`yield return` 由 C# 編譯器幫忙產生 `IEnumerator` 狀態機，切換成本極低。  

核心關鍵：  
- `yield return` 內建的狀態機天生就是「暫停→回到呼叫端→再繼續執行」的模式，剛好符合雙向溝通需求，卻不必付出 Thread 同步成本。

**Cases 1**: DummyAsyncPlayer (Thread 版) vs. DummyYieldPlayer  
• 測試條件：同樣執行數十萬次猜題。  
• 指標：總執行時間。  
• 結果：採用 `yield return` 的 `DummyYieldPlayer` 與單執行緒直寫版相當，遠快於 Thread Sync 版；Thread 造成的 10 ms * 10^5 次 ≈ 1000 s 延遲完全消失。  

**Cases 2**: 參賽最終提交  
• 將原本的 `AsyncPlayer` 全面換成 `YieldPlayer` 後，效能提升到「與 DarkThread 範例相同級距」，即差異可忽略，成功避免線程同步開銷。  

**Cases 3**: 可維持「獨立思考」的程式結構  
• 透過 iterator，`GameHost` / `Player` 的邏輯區塊皆保持在自己函式中，無須被強迫切割成多段 callback。可讀性與維護性大幅改善。