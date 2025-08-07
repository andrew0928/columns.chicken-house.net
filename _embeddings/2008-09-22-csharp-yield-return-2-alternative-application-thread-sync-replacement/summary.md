# [C# yield return] #2. 另類的應用 - Thread Sync 替代方案

## 摘要提示
- yield return: 利用迭代器語法把「等待╱喚醒」轉成連續執行流程，取代傳統同步原語。  
- ThreadSync: 原本以 AutoResetEvent 讓 GameHost 與 Player 互相等待，但 10 ms 級開銷累積後顯著拖慢演算法。  
- xAxB猜數字: 黑暗盃比賽題目促使作者尋找更優雅的同步方式，最終找到迭代器解法。  
- IEnumerator: 交由 C# 編譯器自動產生狀態機，使 Player 能「分段執行」卻保有完整邏輯。  
- AsyncPlayer: 先前用雙執行緒分別執行 GameHost/Player，程式雖直覺卻為同步性能付出代價。  
- YieldPlayer: 將 Think() 改回傳 IEnumerable<HintRecord>，靠 yield return 把問題逐筆送出，再以共用變數接收答案。  
- 效能評估: 實測 DummyYieldPlayer 與純同步版本幾乎無差，證明迭代器方案可忽略額外負擔。  
- 設計思維: 將「雙向溝通」重構為「單向產生＋共用回寫」，簡化心智模型。  
- 語法限制: yield return 只能存在於回傳 IEnumerable<T> 的方法，無法包成巨集隨處使用。  
- 經驗分享: 巧用 Compiler Syntactic Sugar 能省去最難撰寫的狀態管理程式碼，專注於演算法本身。

## 全文重點
作者延續上一篇 yield return 內部運作分析，進一步探討該語法在「執行緒同步」領域的另類應用。黑暗盃 xAxB 猜數字比賽需要 GameHost 與 Player 在極短時間內反覆交換「猜測」與「提示」。傳統做法以兩支執行緒配合 AutoResetEvent 互相等待／喚醒，但每一次同步至少耗費十毫秒，對需十多萬次迴圈的演算法來說代價龐大。  
受到時序圖啟發，作者意識到兩方其實只是交替執行一段「不中斷的邏輯」，與迭代器模式極為相似；於是將 Player 的 Think() 改為傳回 IEnumerable<HintRecord>，在其中藉由一連串 yield return 把猜測逐筆送給 GameHost。GameHost 取得猜測後照舊計算 Hint，再呼叫 Player.GuessNext() 把結果回寫共用欄位；迭代器的 MoveNext() 讓控制權回到 Think() 上次停下的位置，玩家邏輯得以「一路想下去」而無須真正切執行緒。  
實作上僅需少量程式碼：保留一個 HintRecord 共用變數負責結果傳遞；Think() 透過 this.GameHost_AskQuestion() 封裝每次 yield return；GuessNext() 則設定 Hint 後再呼叫 MoveNext()。DummyYieldPlayer 範例顯示，迴圈中只要隨機產生猜測再 yield return 即可，結構比 ThreadSync 版更簡潔。  
測試結果證實，YieldPlayer 在效能上與手寫單執行緒版本不相上下，成功消除同步額外成本，同時保留直覺的「雙方獨立思考」程式架構。作者總結：善用 C# 編譯器提供的 Syntactic Sugar，可將複雜的狀態管理與同步邏輯委託給編譯器，開發者得以專注在演算法與邏輯優化；也鼓勵讀者探索 yield return 在其他非典型場景的潛力。

## 段落重點
### 緒論：yield return 與 IEnumerator
作者回顧前篇介紹過的 yield return 編譯流程，指出該語法能自動產生 IEnumerator 狀態機，讓開發者以簡潔語法撰寫具有「分段執行」特質的邏輯，而不必手動維護複雜狀態；這點是 C# 最具代表性的 Syntactic Sugar 之一。

### 問題緣起：xAxB猜數字與 ThreadSync
黑暗盃程式賽題目「xAxB 猜數字」要求 GameHost 與 Player 高頻率互動。原本直接呼叫使 Player 被切成多段邏輯，難以維護；作者於是改用 ThreadSync 讓兩者各跑一條執行緒，各自「獨立思考」，卻因頻繁同步大幅拖慢整體執行速度。

### 傳統 ThreadSync 方法的效能瓶頸
時序圖顯示，兩條執行緒必須重複「等待對方」「寫入共用變數」「喚醒對方」三步驟；每回合約耗 10 ms。當猜數字需演算數十萬次時，僅同步成本就難以接受，促使作者尋求可維持連續邏輯又能避免執行緒切換的替代方案。

### 用 yield return 重新思考同步—設計理念
作者發現兩方交互實質上是單向「提出問題」再獲得「答案」。若 Player 以 IEnumerable<HintRecord> 暴露「問題串」，GameHost 可批次取用，每次 MoveNext() 都會讓 Player 從上次停下的位置繼續，達到「不中斷思考」效果；答案則透過共用變數回填即可，簡化為單向資料流＋共享回寫。

### YieldPlayer／AsyncPlayer 程式碼解析
核心改動在 Player：StartGuess() 先取 enumerator；GuessNext() 把 Hint 寫回給當前節點再 MoveNext()；Stop() 以特殊 Hint 結束迭代。Think() 方法則以 yield return 送出 Question。DummyYieldPlayer 示範每回合隨機產生猜測，程式只有二十餘行，相比 ThreadSync 版省去大量同步與例外處理碼。

### 效能評估與實務心得
實測顯示 DummyYieldPlayer 與最佳化後的單執行緒程式無明顯差距，成功移除 AutoResetEvent 帶來的時間成本。同時迭代器程式碼更接近直覺流程式寫法，降低維護與除錯難度。缺點是 yield return 受制於方法簽章，無法像巨集般隨處插用，但換得的簡潔與效率足以抵銷此限制。

### 結語與讀者啟發
以 yield return 替代 ThreadSync 展現「轉換思維」的重要：將雙向同步問題拆解為單向迭代＋共享資料，便能把複雜度交給編譯器處理。作者鼓勵讀者發掘語言特性在非典型場景中的應用，讓程式更簡單、快速且易於維護，也歡迎社群分享其他 yield return 的創意用法。