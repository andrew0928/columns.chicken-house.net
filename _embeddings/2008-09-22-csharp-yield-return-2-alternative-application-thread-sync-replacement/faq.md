# [C# yield return] #2. 另類的應用 - Thread Sync 替代方案

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者會想到用 yield return 取代傳統的執行緒同步 (Thread Sync) 機制？
作者在測試 Thread Sync 版本時發現，兩個執行緒之間的等待／喚醒 (AutoResetEvent 等) 每次至少要耗掉約 10 ms，在需要反覆同步十幾萬次的情況下額外耗時驚人。反觀 yield return 的迭代器模型本質上就是「把流程暫停，再於下一次呼叫時從斷點繼續」，概念上與 Thread Sync 的「邏輯不中斷」目標一致，但完全不必切換執行緒，因此可能大幅降低同步成本。這讓作者靈機一動，嘗試用 yield return 來重寫原本靠 Thread Sync 溝通的程式。

## Q: 在 xAxB 猜數字遊戲中，yield return 是怎麼替代 Thread Sync 來完成資料交換的？
1. Player 把原本的 Think() 改寫成 `IEnumerable<HintRecord>`，在其中用 `yield return` 把每一次猜測 (問題) 傳給 GameHost。  
2. GameHost 取得迭代器後，呼叫 `MoveNext()` 取得 `Current`，計算答案 (Hint)，並把結果塞回共用欄位。  
3. GameHost 接著呼叫 `Player.GuessNext()`；此方法會先把上一回合的 Hint 寫入 `enum.Current.Hint`，再呼叫 `MoveNext()`，控制權因而回到 Think() 函式被暫停的下一行。  
4. Player 可透過 `this.GameHostAnswer` 在兩次 `yield return` 之間讀取上一回合的 Hint。  
透過上述流程，資料能雙向流動，但整個過程只用一條執行緒，不需任何 AutoResetEvent 或 lock。

## Q: 使用 yield return 重寫後與 Thread Sync 版的效能差異如何？
實測顯示，用 yield return 重寫的 DummyYieldPlayer 執行效率和 DarkThread 提供的「無同步」基準版本幾乎相同，也就是說與 Thread Sync 版相比，額外耗時可忽略不計，達到「省去同步延遲又保留連續邏輯」的效果。

## Q: 為什麼不能把 yield return 包成一個內部函式並用 return 傳回結果？
C# 規定只要方法裡出現 `yield return`，該方法的回傳型別就必須是 `IEnumerable<T>` 或 `IEnumerator<T>`；若將 `yield return` 移到別的方法裡，就得手動實作整個 `IEnumerator`，等同放棄編譯器提供的語法糖。由於 C# 目前沒有像 C/C++ 巨集那樣的語法，作者選擇直接在 Think() 裡寫 `yield return`，維持簡潔。

## Q: 在 Player 端若想取得 GameHost 回傳的 Hint，該在哪裡存取？
應在每一次 `yield return` 與下一次 `yield return` 之間呼叫 `this.GameHostAnswer` (文中對應到 `last_record`) 取得。這是 GameHost 在上回合計算完後，透過共用變數回填的最新 Hint。