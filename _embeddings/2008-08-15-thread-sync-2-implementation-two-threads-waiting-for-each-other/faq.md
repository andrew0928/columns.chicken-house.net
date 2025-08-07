# Thread Sync #2. 實作篇 - 互相等待的兩個執行緒

# 問答集 (FAQ, frequently asked questions and answers)

## Q: DummyPlayer 與 AsyncDummyPlayer 的最大差異是什麼？
DummyPlayer 採被動模式，完全依賴 GameHost 逐次呼叫 `StartGuess()` 與 `GuessNext()`；玩家邏輯被切散在不同方法中。  
AsyncDummyPlayer 則在 `StartGuess()` 內自建執行緒，於 `Think()` 迴圈中主動思考、隨時透過 `GameHost_AskQuestion()` 與 GameHost 溝通，使整體邏輯可連續撰寫、更貼近人類思考流程。

## Q: AsyncPlayer 是如何把「被動呼叫」轉換成「主動思考」的？
AsyncPlayer 在 `StartGuess()` 先 new 一條 thread 執行 `ThinkCaller()`，裡面依序呼叫 `Init()` 與 `Think()`。  
雙執行緒間利用三個 AutoResetEvent  
1. `_host_call`  
2. `_host_return`  
3. `_host_end`  
以及暫存區 `_temp_number`、`_temp_hint` 互相等待／喚醒，完成「玩家送出猜測 → 主機回傳提示」的同步流程。

## Q: GameHost_AskQuestion(int[] number) 的角色是什麼？
這支方法由「玩家執行緒」呼叫，流程是  
1. 將最新猜測寫入 `_temp_number`  
2. `Set()` `_host_return` 通知 GameHost「題目來了」  
3. `WaitOne()` `_host_call` 等待主機填好 `_temp_hint`  
4. 取回提示後回傳給 `Think()`  
藉此達成雙向資料交換。

## Q: 這種非同步寫法使用了哪些同步原語？
程式中用到的是 .NET 的 AutoResetEvent 物件：`_host_call`、`_host_return`、`_host_end`。它們負責在線程間「等待／喚醒」彼此，以確保資料讀寫的時序正確。

## Q: 把玩家邏輯拆在 StartGuess 與 GuessNext 中有哪些閱讀上的缺點？
邏輯被迫分散，閱讀者必須在腦中「拼圖」才能弄懂流程，還得靠 instance variables 保存跨呼叫的狀態；若改成單一 `Think()` 迴圈即可保持區域變數與流程的連續性，易讀許多。

## Q: 使用 AsyncDummyPlayer 會帶來什麼代價？
雖然可讀性大幅提升，但因多了一條 thread 及事件同步，效能反而比 DummyPlayer 慢約 4–5 倍；這是以可維護性換取效能的典型折衷。

## Q: 作者從這個範例得到的結論是什麼？
Thread 雖然無法保證效能提升，卻能改變呼叫模式、簡化複雜問題；善用同步機制就能把「被動回呼」轉成「主動流程」，讓程式撰寫更直覺。