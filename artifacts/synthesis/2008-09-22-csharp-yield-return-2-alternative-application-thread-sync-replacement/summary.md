# [C# yield return] #2. 另類的應用 - Thread Sync 替代方案

## 摘要提示
- 問題背景: 作者在多執行緒同步的猜數字遊戲中遭遇效能瓶頸，尋找更佳解法。
- ThreadSync 瓶頸: 以 AutoResetEvent 等機制互相等待/喚醒，單次同步約耗時 10ms，累積代價高。
- 發想來源: 注意到雙方輪流接續邏輯的需求，與 yield return 的迭代模型相似。
- 思路轉換: 將 GameHost 與 Player 的互動轉化為「Player 以 yield return 逐次送出問題」。
- 資料回傳: 問題以 yield return 丟出，答案透過共用變數回填並在下一次 MoveNext() 取得。
- 實作重點: Player.Think() 回傳 IEnumerable<HintRecord>，GameHost 透過 IEnumerator 控制流程。
- 範例程式: DummyYieldPlayer 展示以 yield return 不斷提出隨機猜測。
- 語言限制: yield return 受限於方法簽章，無法簡化成一般 function call 封裝返回值。
- 效能成果: 單執行緒迭代避免昂貴同步，表現與原版幾乎無差，接近最佳化。
- 結論反思: 善用 C# 編譯器自動產生狀態機，降低複雜度並避開 ThreadSync 開銷。

## 全文重點
本文延續上篇對 C# yield return 的編譯行為與 IEnumerator 自動生成機制的解析，提出一個「迭代器替代執行緒同步」的實務應用。作者先回顧在黑暗盃「xAxB 猜數字」遊戲中，為了讓 GameHost 與 Player 能獨立思考且不割裂邏輯，曾以 ThreadSync（AutoResetEvent 等）讓兩個執行緒互相等待/喚醒。雖然邏輯清晰，但同步本身昂貴，單次至少約 10ms，當互動次數達數十萬次時，累積開銷龐大，促使作者尋求更有效率的方案。

靈感來自對兩張時序圖的對比：傳統呼叫模型中，主流程在 GameHost 與被動的 Player 之間穿梭，玩家邏輯被切割；ThreadSync 雖讓雙方各自保有連貫邏輯，卻付出等待/喚醒成本。作者注意到兩者共同點在於「斷點續執行」與「交替推進」，這恰與 yield return 迭代器的運作吻合。因此改造互動模型：把「Player 提問、GameHost 回答」視為一個迭代序列，Player 透過 Think() 方法逐次 yield return 問題，GameHost 以 IEnumerator 逐步 MoveNext() 推進流程，於每一步之間把答案填回共用欄位，再喚起下一次迭代。

具體實作上，Player 抽象出 Think() 回傳 IEnumerable<HintRecord>。StartGuess() 初始化 enumerator 並先 MoveNext() 取得首個猜測；GuessNext() 接收上一輪提示（Hint）後寫回當前項，再 MoveNext() 取得下一個猜測；Stop() 則以特定 Hint 結束。透過 GameHost_AskQuestion() 產生 HintRecord 並暫存，GameHostAnswer 屬性提供回讀答案的管道。示例 DummyYieldPlayer 在 Think() 中無限迭代：生成隨機答案，yield return 丟出問題，GameHost 取走後計算提示再回填。

此法的關鍵在於以單執行緒、狀態機驅動的方式，維持 Player 的連續思考流程，同時消除跨執行緒同步的昂貴成本。限制在於 C# 的 yield return 必須位於回傳 IEnumerable<T> 的方法中，難以用一般 function 封裝返回值；若要突破只能自行實作 IEnumerator 狀態機，失去語法糖優勢。實測顯示，改用 yield return 後的 DummyYieldPlayer 效能與 Darkthread 的版本幾乎一致，足可忽略差距，且開發複雜度顯著降低。作者總結，這是善用 C# 編譯器產生狀態機、以迭代驅動流程來取代 ThreadSync 的一次成功嘗試，兼具邏輯連貫與效能。

## 段落重點
### 問題背景與前情
作者延續上篇討論 yield return 的編譯結果與 IEnumerator 自動生成，回到黑暗盃猜數字遊戲的場景。原先為了讓 GameHost 與 Player 的邏輯都能「獨立思考」且不中斷，曾撰寫兩篇 ThreadSync 文章介紹以雙執行緒互相等待/喚醒的作法（AsyncPlayer），以便配合 GameHost 的呼叫模式，降低程式邏輯被切割的負擔。

### 執行緒同步的效能瓶頸
ThreadSync 的代價在於每一步互動都要等待對方與發出喚醒，單次約需 10ms。若遊戲需反覆上萬次互動，總時間會被同步成本拖垮。作者因此反思：是否有能維持流程連貫、又能省下同步成本的替代方案？

### 從時序圖到 yield return 的發想
對比單執行緒穿梭呼叫與雙執行緒互等喚醒的時序圖，作者察覺兩者皆屬「交替推進、斷點續執行」。這與迭代器在每次 MoveNext() 從上次中斷點繼續的行為極為相似，遂提出以 yield return 來驅動 Player 的「提問序列」，由 GameHost 逐步消費，達成邏輯連續而不需跨執行緒同步。

### 設計與實作重點（AsyncPlayer 以 yield 改寫）
核心改寫包括：
- 將 Player.Think() 定義為 IEnumerable<HintRecord>，以 yield return 逐次丟出問題。
- StartGuess() 建立 enumerator 並先 MoveNext() 取得第一個猜測。
- GuessNext() 接收上一輪 Hint，寫入當前項，MoveNext() 推進並取得下一猜測。
- Stop() 以特定 Hint 結束迭代。
- GameHost_AskQuestion() 建立並暫存 HintRecord，GameHostAnswer 提供答案回讀。
GameHost 在每輪之間計算提示並回填到共用變數，下一次 MoveNext() 時，Think() 從上次 yield return 處續跑。

### DummyYieldPlayer 範例
示例中，DummyYieldPlayer 以隨機不重複數字產生猜測，Think() 內以無窮迭代 while(true) 不斷 yield return GameHost_AskQuestion(randomGuess())。若需要讀回提示，應在 yield return 與下一輪之間透過 GameHostAnswer 取得。不需額外同步，流程清晰。

### 語言限制與權衡
yield return 受限於方法回傳型別必須是 IEnumerable<T>，無法將其隨意包裝到一般函式再 return 結果；若硬要抽象，需要自行手寫 IEnumerator 狀態機與狀態轉移，反而失去 C# 語法糖的簡潔。實務上以兩行輔助呼叫配合共用欄位即可達成。

### 效能觀察與結語
以 DummyYieldPlayer 實測，效能接近手寫最佳化版本，與原提供的版本幾乎無差，且避開 ThreadSync 的巨大開銷。此法讓邏輯保持連續、可讀性高，又能仰賴編譯器自動產生狀態機處理難寫的部分。作者滿意並以此版本參賽，也鼓勵讀者分享更多以 yield return 解決非典型問題的經驗。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C# 基礎語法與物件導向概念
   - 迭代器與集合：IEnumerable/IEnumerator、yield return 的基本機制
   - 多執行緒與同步：Thread、AutoResetEvent、等待/喚醒的成本與風險
   - 狀態機思維：以狀態保存來分段執行邏輯

2. 核心概念：
   - 使用 yield return 取代執行緒同步：以迭代器分段執行，避免跨執行緒等待/喚醒的高成本
   - GameHost/Player 的協作式流程：Host 驅動 enumerator.MoveNext()，Player 以 yield return 提出問題
   - 共享狀態傳遞答案：問題透過 yield return 丟出，答案以共享欄位（GameHostAnswer/HintRecord）回填
   - 編譯器生成狀態機：C# 將 iterator block 轉為實作 IEnumerator 的狀態機，降低手寫難度
   - 限制與邊界：yield return 需在回傳 IEnumerable<T> 的方法內，無法任意包在一般 function call 內返回值

3. 技術依賴：
   - Think(): IEnumerable<HintRecord> 定義 → C# 編譯器產生對應的狀態機類別（IEnumerator）
   - GameHost 端透過 GetEnumerator()/MoveNext()/Current 驅動 Player 的 Think()
   - 共享變數 HintRecord/last_record 作為答案回填通道（GameHost_AskQuestion 建立記錄、GameHostAnswer 讀取）
   - StartGuess/GuessNext/Stop 驅動流程：初始化 → 設定上一輪 Hint → 推進到下一個 yield return → 結束處理

4. 應用場景：
   - 需要雙向互動但不追求真正平行的邏輯（協作式流程/協程風格）
   - 在高頻交互場景中，替代昂貴的執行緒同步（避免每次10ms級的等待/喚醒）
   - 遊戲主機-玩家、模擬器-代理、管線處理中「一步一問」的回合式互動
   - 以可讀性高的分段邏輯取代複雜的手寫狀態機或多執行緒

### 學習路徑建議
1. 入門者路徑：
   - 了解 IEnumerable/IEnumerator 與 foreach 的關係
   - 練習基本 yield return：從集合遍歷到自訂序列生成
   - 寫一個最小化的 Think(): IEnumerable<T>，用 MoveNext()/Current 手動驅動

2. 進階者路徑：
   - 研究 C# 如何將 iterator block 編譯為狀態機（查看 IL 或概念圖）
   - 將原本用 AutoResetEvent/lock 的雙向互動改寫為 yield return 流程
   - 加入停止/取消、例外處理（Stop()、Try/Finally 與 iterator 的互動）

3. 實戰路徑：
   - 實作 GameHost/Player：Host 控制節拍、Player 以 yield return 提問、Host 以共享欄位回覆
   - 基準測試：比較 Thread Sync 版與 yield 版的迭代次數、延遲、CPU 使用率
   - 整合守護邏輯：處理結束條件、超時、空回覆與資源釋放

### 關鍵要點清單
- 使用 yield return 取代同步 (優先級: 高)
  - 以迭代器分段執行邏輯，避免跨執行緒等待/喚醒帶來的高延遲與複雜度。

- Host 驅動 Player 的 enumerator (優先級: 高)
  - GameHost 透過 MoveNext()/Current 一步步推進 Player 的 Think()。

- 單向問題、共享回覆 (優先級: 高)
  - 問題由 yield return 丟出，答案以共享欄位（GameHostAnswer/HintRecord）回填。

- Think() 必須回傳 IEnumerable<T> (優先級: 高)
  - 使用 yield return 的方法簽名受限，無法任意包裝到一般函式再 return 值。

- 狀態機由編譯器生成 (優先級: 高)
  - C# 將 iterator block 轉為實作 IEnumerator 的狀態機，降低實作成本。

- StartGuess/GuessNext/Stop 流程控制 (優先級: 中)
  - 初始化 enumerator、以 Hint 回填上一輪結果、推進到下一個 yield 點、結束時送終止信號。

- 性能優勢與邊際 (優先級: 高)
  - 避免每次同步約10ms的成本，高頻互動下總體差異巨大。

- 非真正平行、屬協作式 (優先級: 中)
  - 此法是單執行緒的協作流程，不提供多核並行能力。

- DummyYieldPlayer 範例 (優先級: 中)
  - 以隨機猜測示範最小可行寫法，yield return GameHost_AskQuestion(...)

- 回覆讀取時機 (優先級: 中)
  - 在 yield return 與下一輪前，透過 GameHostAnswer 取得上一輪的答案。

- 例外與終止處理 (優先級: 中)
  - Stop() 設定結束提示並嘗試推進一次，以完成清理與退出狀態機。

- 適用與不適用情境 (優先級: 高)
  - 適合回合式、順序協作；不適合需要真正並行或阻塞 I/O 的情境。

- 可讀性與維護性提升 (優先級: 中)
  - 以線性流程撰寫跨呼叫的邏輯，避免手寫狀態機或複雜同步。

- 無法以函式封裝 yield return (優先級: 中)
  - 若要抽取通用邏輯，需以可 yield 的方法或組合模式設計，不能期待一般方法 return 值。

- 對既有 Thread Sync 的替代策略 (優先級: 中)
  - 評估互動頻率、延遲敏感性，將「互相等待」改為「主動驅動的迭代器」。