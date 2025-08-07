# 後端工程師必備: 平行任務處理的思考練習 (0916補完)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這個「平行任務處理」練習的核心目的與重點是什麼？
本練習旨在訓練後端工程師對「精準掌控程式執行」的能力。透過處理 1,000 個 `MyTask` 物件並滿足一系列併發與資源限制，讓參與者思考如何在效能、記憶體與等待時間之間取得最適平衡，並以量化指標驗證結果。

## Q: `MyTask` 物件在執行時有哪些強制規則？
1. 每個 `MyTask` 必須依序執行 `DoStep1() → DoStep2() → DoStep3()`。  
2. 各 Step 同時併發的數量有限：Step1 最多 5、Step2 最多 3、Step3 最多 3。  
3. 三個 Step 執行時間不同（867 ms、132 ms、430 ms）。  
4. 每個 Step 會先配置、結束時才釋放記憶體，因此無限制併發會導致記憶體爆量。

## Q: 評分／觀察 TaskRunner 品質的四個指標是哪些？
1. Max WIP：任何時刻處於「已開始但未全部完成」的 `MyTask` 數量最大值  
2. Memory Peak：執行期間佔用記憶體的最高點  
3. TTFT（Time To First Task）：第一個 `MyTask` 完成所花時間  
4. TTLT（Time To Last Task）：所有 `MyTask` 全數完成所花時間

## Q: 在題目既定參數下，理論最佳 (極限) 效能大約是多少？
• TTFT ≈ 1,429 ms（867 + 132 + 430）  
• TTLT ≈ 174,392 ms（Step1 200 批 × 867 ms + Step2/3 收尾）  
• AVG_WAIT ≈ 87,867 ms（1,000 筆任務等待時間平均值，依瓶頸 Step1 推算）

## Q: 為什麼先估算「理論極限」對優化工作至關重要？
掌握理論上能達到的最好成績，可判斷目前程式與目標的差距。若已逼近極限，再投入大量時間只能換得極小收益；若仍差距巨大，才值得繼續尋找瓶頸與改良方向，避免盲目最佳化。

## Q: 在所提供的多種解法中，主要可分為哪三大類？
1. 多執行緒／多 Task：直接使用 Thread、ThreadPool、TPL、PLINQ 等並行機制。  
2. 生產者－消費者 Pipeline：以 BlockingCollection、Channel 等做階段緩衝與背壓控制。  
3. 其他／實驗性作法：如示範用迴圈依序執行，或刻意失衡的極端版本。

## Q: 本次 Benchmark 中，哪個參賽者在 AVG_WAIT 指標拿到最佳成績？
由 JW 的 `JW.JWTaskRunnerV5` 拿下最低的 AVG_WAIT（約 85,855 ms），被視為 100 % 基準。

## Q: 題目中指出最主要的效能瓶頸在哪一個 Step？為什麼？
瓶頸在 Step #1。因為它的執行時間最長（867 ms）且併發上限僅 5，整體吞吐量受其限制，其餘 Step 2、3 只是等待 Step 1 的產出。

## Q: 使用 BlockingCollection 或 Channel 做為步驟之間緩衝有何優點？
兩者皆能：  
1. 自動處理生產者／消費者同步與排程 (blocking 或 async)。  
2. 內建容量控制，能對上游施加背壓，防止記憶體或 WIP 爆量。  
3. 簡化通知機制，避免以忙輪詢 (polling) 消耗 CPU。

## Q: 若只想用最少程式碼就達到接近理想的總執行時間，有哪些簡易策略？
1. 直接用 PLINQ / TPL 的 `.AsParallel().ForAll()`，並以 `.WithDegreeOfParallelism()` 控制最大併發。  
2. 讓三個 Step 依序以 `.ContinueWith()` 串接，保住執行順序。  
3. 依據各 Step 併發上限粗略設定 ThreadPool 的 Min/Max Threads，即可取得 1% 內的效能表現，又保有高度可讀性與維護性。