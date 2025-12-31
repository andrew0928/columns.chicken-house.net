---
layout: synthesis
title: "後端工程師必備: 平行任務處理的思考練習 (0916補完)"
synthesis_type: summary
source_post: /2019/07/06/pipeline-practices/
redirect_from:
  - /2019/07/06/pipeline-practices/summary/
postid: 2019-07-06-pipeline-practices
---

# 後端工程師必備: 平行任務處理的思考練習 (0916補完)

## 摘要提示
- 練習目標: 透過 C# 基礎與 BCL，訓練「精準」掌控多步驟大量任務的平行處理與資源使用。
- 題目設定: 處理 1000 個 MyTask，需依序完成 Step1→Step2→Step3，且每步有並行上限與不同耗時/記憶體配置。
- 評量指標: 主要正確性外，觀察 Max WIP、峰值記憶體、TTFT、TTLT、平均等待時間等。
- 觀測工具: Console 摘要與 CSV 事件軌跡，量化 WIP/Threads/MEM、各步驟 Enter/Exit 與 Thread 任務分布。
- 設計思路: 把問題視為生產者-消費者與流水線（Pipeline）；精準控制比盲目加 Thread 更關鍵。
- 理論極限: 由各步耗時/併發上限推估瓶頸（Step1），TTFT≈1429ms，TTLT≈174392ms，AVG_WAIT 以推導值作比較基準。
- 解法譜系: 以 Task/ThreadPool/TPL 的「多工排程」派，與 BlockingCollection/Channel 的「Pipeline 管理」派為主。
- 觀察結論: 泛用排程易達中上水準；精準管控（專屬工作執行緒+有界緩衝+通知）可逼近理論極限。
- 常見盲點: 忽略每步併發上限與執行順序、過度依 CPU 核數、在 Task 內部才用 Semaphore 限流導致時機太晚。
- 實戰建議: 先算理論極限→定義指標→用 CSV 佐證→再選結構（TPL/PLINQ 或 BlockingCollection/Channel）做精準優化。

## 全文重點
作者以可執行的 C# 練習題，訓練後端工程師在平行任務處理上的「精準」控制：在只用語言基本功與 BCL 的前提下，完成 1000 個必須依序執行三步驟的 MyTask。每步驟有不同耗時、不同記憶體配置，且步內並行數量受限；因此無法單靠無腦增加 Threads 或機器數量，反而需要在吞吐、延遲與資源（特別是記憶體/WIP）中取得平衡。評量除正確性外，包含 Max WIP、峰值記憶體、Time To First Task（TTFT）、Time To Last Task（TTLT）與平均等待時間（AVG_WAIT）。為了讓表現可量化、可診斷，程式輸出 Console 摘要與 CSV 記錄，CSV 追蹤時間戳、記憶體、各步驟在製數、各執行緒的任務分布，有助於以圖表視覺化與檢查排程是否落在預期。

題目本質是生產者-消費者與流水線問題。從步驟耗時與併發上限可知瓶頸在 Step1（867ms/5），理想 TTFT≈1429ms；以 Step1 吞吐粗估處理 1000 筆的下限約 173.4 秒，進一步考量尾段收斂與分批交接，理想 TTLT≈174.392 秒。AVG_WAIT 可依每批進入流水線的時間推導近似值，作為評比基準。了解理論極限可避免花大量時間在已接近極限的微幅收益上，並能判斷是否該轉換策略。

作者彙整 18 組實作進行 Benchmark。解法大致分兩派：（1）多工排程派，如 Task/ThreadPool/TPL/PLINQ，優點是簡潔、維護成本低，在不了解任務細節時也有不錯表現；（2）Pipeline 管理派，如 BlockingCollection/Channel/Queue，於步驟之間設置有界緩衝，配合 Semaphore 或 Channel 的 backpressure 與通知，精準控制交接時機與並行數，能逼近極限。結果顯示若忽略步內限流或在 Task 啟動後才限流，容易拉高 TTFT 或失去吞吐；反之，將每步配置專屬 worker threads，結合 BlockingCollection 有界隊列，能同時兼顧 TTFT、TTLT 與平均等待時間。

在「Solution & Review」中，作者逐一評論 PR：如以 CPU 核數作為限流依據並不契題；只用少量 Threads 導致低 WIP 也會拖慢整體；善用 BlockingCollection/Channel 能自然達到精準交接與同步通知；RX 結合 Semaphore 的寫法亦可達高效能。多例中，ThreadPool 的泛用排程常有「第一筆非最先完成」與 threads 空檔無法完全填滿的隱性延遲，但整體仍在 1% 內；而作者親寫的 AndrewPipelineTaskRunner1 採固定專屬 threads + BlockingCollection 的流水線架構，三項指標幾乎逼近理論極限，顯示「精準」控制的上限。總結建議：先用指標和理論極限建立「正確的目標」，再選擇適當結構與工具，善用 CSV/圖表驗證排程是否真的如預期執行；實務上若非核心熱點，TPL/PLINQ 簡潔方案常已足夠，核心熱點則以專屬 worker + 有界緩衝與嚴格時機控制追求極致。

## 段落重點
### 解題規則說明
本練習在 ParallelProcessPractice.Core 提供 MyTask 類別，須依序呼叫 DoStep1/2/3 完成，總數 1000 筆。每步有並行上限與不同耗時；每步開始配置記憶體，結束釋放，故 WIP 過高會拉高峰值記憶體。參與者需自行繼承 TaskRunnerBase 實作 Run，透過 ExecuteTasks(100) 觸發。Console 輸出包含 Max WIP、峰值記憶體、TTFT、TTLT、平均等待時間等；另輸出 CSV，欄位涵蓋 TS、MEM、WIP、THREADS_COUNT、各步 Enter/Exit 與 T1~T30 執行緒的當前任務，便於用圖表檢視記憶體曲線、在製數、並行執行緒數與任務在各 thread 的分配，協助驗證設計是否「照想像在跑」。

### 解題規則說明 / 1, 建立並執行你的 TaskRunner
以 Console App 建專案，繼承 TaskRunnerBase，覆寫 Run(IEnumerable<MyTask> tasks) 進行任務處理。示範程式 AndrewDemo 僅用 for 迴圈逐步呼叫三步驟，無平行與最佳化，作為最低基準。Main 中建立 Runner 並呼叫 ExecuteTasks(100) 即可執行、產出 Console 與 CSV。

### 解題規則說明 / 2, 檢查 console output
Console 摘要顯示是否 PASS（步驟順序正確與成功數），並列出 Max WIP（總與各步）、資源使用（峰值記憶體、Context Switch）、等待時間（TTFT、TTLT、Total/Average Waiting），以及執行計數（成功/失敗/各步完成）。可快速比較不同方案的整體表現與資源消耗。

### 解題規則說明 / 3, 進階監控資訊 (csv) 說明
CSV 以固定頻率記錄 TS、MEM、WIP_ALL/1/2/3、THREADS_COUNT、ENTER/EXIT 統計、各 thread 當前任務（T1~T30）。可用 Excel 視覺化記憶體曲線、WIP 波動、並行 threads 數；以表格觀察在每個時間點各 thread 執行哪個 Task/Step，辨識空轉、等待與錯配，據以調整排程或緩衝策略。

### 品質指標的挑選
評比不只看正確性，更看能否用最少資源、最短等待達成。Max WIP 對應在製品，直接影響記憶體與其他稀缺資源；TTFT關乎使用者第一個結果的體感；TTLT代表整體吞吐的極限；AVG_WAIT平衡兩端極端，能防堵只追前或只追尾的「KPI 作弊」。作者強調以使用者體感與整體效率並重，並透過 CSV 佐證是否達成設計初衷。

### 品質指標的挑選 / 指標: 最大處理中任務數 (Max WIP)
WIP 是所有已開始 Step1 但未完成 Step3 的任務數，代表暫佔資源的「在製品」；WIP 高可提升吞吐但會推高記憶體與風險，WIP 低省資源但可能餓死後段。題目會統計全程 max(WIP)，要求在效能與資源間取得合理平衡。

### 品質指標的挑選 / 指標: 第一個任務完成時間 (TTFT)
TTFT是 Runner 啟動至第一個任務完成的時間，類似網頁的 TTFB。它直接影響使用者首次回應體驗，亦能讓後續 Pipeline 更早啟動。相較只看執行時間，Lead Time 更能反映排程策略與等待成本，題目更重視 TTFT 的意義。

### 品質指標的挑選 / 指標: 所有任務完成時間 (TTLT)
TTLT是最後一個任務的交付時間，衡量整體處理效率與吞吐。在批次場景往往較重要，與 TTFT 的取捨要視業務定義。針對本題的流水線，TTFT較有助前段啟動，但 TTLT仍是評估極限的核心參考。

### 品質指標的挑選 / 指標: 平均完成時間 (Average Lead Time)
AVG_WAIT 是每個任務從啟動到完成的平均等待時間，介於 TTFT 與 TTLT 之間，避免指標偏誤。它能抑制只優化首筆或尾筆的策略，使整體體感更均衡。

### 下一步: 提交你的 TaskRunner !
作者在公司內外推動此練習，鼓勵以 PR 交流，藉由可量化的指標討論不同解法的優缺點與適用情境。也可依實際專案調整題目的 PracticeSettings，對映真實瓶頸，透過「先問對問題、定義對指標」的方法，讓優化更有效。

### PART II, Solution & Review (2019/09/16)
作者彙整 18 組 Runner 進行 Benchmark 與 Code Review。先以題目參數推導理論極限：步耗時（867/132/430ms）、步內併發（5/3/3），瓶頸在 Step1；理想 TTFT≈1429ms，理想 TTLT≈174392ms，AVG_WAIT 以最佳實測值為 100%。解法分「多工排程」與「Pipeline 管理」兩派，並逐案檢討常見誤區（如以 CPU 核數限流、在 Task 啟動後才限流、缺少步間緩衝或通知），說明如何用 CSV 查證問題根因，如 Step1 未並行導致整體慢 5 倍，或初期交接延遲拉高 TTFT/AVG。

### 理論極限在哪邊?
將三步視為三站生產線：以步耗時/併發推導各站吞吐，Step1 最慢（867/5≈173.4ms/件），決定全線下限；首件 TTFT 為三步總和（≈1429ms）。尾段收斂需考量 Step2→Step3 的分批交付與兩輪處理，理想 TTLT≈173400+132+430+430=174392ms。AVG_WAIT 以分批累計近似推導。掌握極限可避免投入在邊際收益極小的微優化，幫助判斷何時改架構更划算。

### Benchmark Result
以 1000 筆任務評比，各 Runner 的 TTFT/TTLT/AVG 與理論值差距小於 1% 標綠；AVG 以最佳實測作 100%。結果顯示：TPL/PLINQ/ThreadPool 等泛用排程，整體多能達良好水平，但 TTFT 常受初期交接/排程選擇影響；Pipeline+有界緩衝+精準通知者，最能逼近極限。若忽略步內上限或只開少量 threads，會大幅拉長 TTLT/AVG。

### Solution & Code Review
- 多工排程派（Task/ThreadPool/TPL/PLINQ）：簡潔、泛用，對任務未知性高時實用；但步內限流與步間時機控制不精準，TTFT/AVG 易失分。
- Pipeline 管理派（BlockingCollection/Channel/RX）：精準移交、限流與 backpressure，易逼近極限；代價是結構設計與通知同步較複雜。
- 代表案例：有以 CPU 核數做限流（不契題目瓶頸）、在 Task 內才 Semaphore（時機偏晚）、或 Step1 未並行導致吞吐重挫；也有 RX+Semaphore/BlockingCollection/Channel 的寫法，整體逼近理論值。最佳 AVG 來自 ThreadPool+BlockingCollection 精準調度。

### 範例與總結 / 首選: AndrewPipelineTaskRunner1
作者示範以每步專屬固定 threads（依步內上限配置）+ BlockingCollection 作有界緩衝，步間以 Add/CompleteAdding 與 GetConsumingEnumerable 做自然交接；避免把排程交給泛用機制，改以專屬 worker 精準掌控順序與時機。此解法 TTFT/TTLT/AVG 均≈100.03%~100.21%，幾近極限。若兩步效率差距大，可調整緩衝容量平衡 WIP 與吞吐。另提供以 PLINQ 或 Channel 改寫的版本作對照。

### 範例與總結 / 其他類型: 使用多工排程的技巧
若非核心熱點或任務未知性高，可選 TPL/PLINQ 的簡潔寫法：AsParallel().WithDegreeOfParallelism().ForAll 搭配 ContinueWith 串接三步，給足排程依序提示；維護成本低、效能水準穩定。當指標要求極致或資源極敏感時，再回到專屬 worker + 有界緩衝的精準架構追求上限。

### 參考資料
文末彙整 RX/.NET 平行程式設計與 Channel/BlockingCollection/Dataflow 比較等參考資源。建議讀者以此練習做 Hands-On：先算極限、定義指標，再用 Console/CSV 驗證與迭代。透過可量化的討論，培養面向本質的效能思維與架構取捨能力。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C# 與 .NET BCL 基礎（IEnumerable、Task、Thread、ThreadPool、SemaphoreSlim）
   - 非同步與多執行緒觀念（CPU/IO bound、同步/非同步、鎖與同步原語）
   - 生產者/消費者與 Pipeline 模式（緩衝區、背壓、通知/阻塞）
   - OS 排程與效能指標基礎（Lead Time、平均等待時間、瓶頸分析）
   - 監控與資料可視化（CSV/Excel 基本圖表）

2. 核心概念：
   - 精準控制：讓程式行為與預期一致，能量化與驗證
   - Pipeline 與併發限制：每步驟並行上限、順序 constraint、資源控制
   - 關鍵效能指標：TTFT、TTLT、AVG_WAIT、Max WIP、記憶體峰值
   - 生產者/消費者協調：緩衝（BlockingCollection/Channel）、通知（blocking/async）
   - 理論極限與瓶頸：以最慢步驟決定整體吞吐，先估上限再優化

3. 技術依賴：
   - 任務模型：MyTask.DoStepN(1..3) 並需依序執行
   - 併發工具：Thread/ThreadPool/Task/TPL/PLINQ、SemaphoreSlim、ManualResetEvent
   - 緩衝與通道：BlockingCollection<T>（同步阻塞）、Channel<T>（原生 async）
   - 反應式與延續：ContinueWith、Reactive Extensions（RX）
   - 監控輸出：Console 指標與 CSV 明細（TS、MEM、WIPx、THREADS_COUNT、Tx thread 活動）

4. 應用場景：
   - 後端批次與高併發任務處理（大量任務、分步驟處理）
   - 雲端成本最佳化（降低 WIP/記憶體峰值→降成本）
   - 互動式系統改善回應（優化 TTFT）
   - 整體吞吐最佳化（優化 TTLT/AVG_WAIT，適用夜間批次）
   - 效能回歸與 A/B 解法評測（以統計與可視化驗證）

### 學習路徑建議
1. 入門者路徑：
   - 熟悉 C# Task/Thread/ThreadPool 與基本同步原語（SemaphoreSlim）
   - 理解生產者/消費者與 Pipeline 概念，動手寫單步驟並行
   - 學會讀取與繪製 CSV（MEM、WIP、THREADS_COUNT）圖表

2. 進階者路徑：
   - 用 BlockingCollection 與 Channel 實作三段式 Pipeline，控制每步驟併發上限
   - 導入 ContinueWith/async 管線化，觀察 TTFT/TTLT/AVG_WAIT 變化
   - 練習估算理論極限與瓶頸（以最慢步驟/並發上限推估吞吐）

3. 實戰路徑：
   - 建立可切換的 Runner 策略（ThreadPool vs 專屬 threads vs PLINQ vs Channel）
   - 指標驅動優化：先定 KPI（TTFT/TTLT/AVG_WAIT/WIP/MEM），再迭代調參
   - 以真實參數（步驟耗時/限制）回放專案流量，做容量規劃與成本估算

### 關鍵要點清單
- 精準控制思維: 先定預期行為與可量測指標，再驗證執行是否吻合 (優先級: 高)
- 任務順序約束: 每個 MyTask 必須嚴格依序執行 Step1→2→3 (優先級: 高)
- 步驟併發上限: 不同步驟各自有最大並行數，必須分別控制 (優先級: 高)
- 核心指標-TTFT: 第一個任務完成時間，影響使用者體感 (優先級: 高)
- 核心指標-TTLT: 最後一個任務完成時間，代表整體吞吐 (優先級: 高)
- 核心指標-AVG_WAIT: 平均交期/等待時間，平衡 TTFT 與 TTLT (優先級: 高)
- WIP 與資源: WIP 直接影響記憶體與成本，需抑制過度膨脹 (優先級: 高)
- 生產者/消費者管控: 使用緩衝與通知機制平衡上下游（BlockingCollection/Channel） (優先級: 高)
- 瓶頸與理論極限: 以最慢步驟吞吐估算上限，避免無效優化 (優先級: 高)
- 通用排程 vs 精準排程: 交給 ThreadPool/TPL 易用但可能失精準，專屬 threads 更可控 (優先級: 中)
- ContinueWith/管線化: 以延續任務精準銜接步驟，降低空轉 (優先級: 中)
- PLINQ/TPL 實用性: 少量代碼即可達到可用表現，適合實戰折衷 (優先級: 中)
- Channel（async 倉庫）: 原生非同步背壓，常優於 BlockingCollection 在特定情境 (優先級: 中)
- CSV 監控與可視化: 以 MEM/WIP/THREADS_COUNT/Tx 邏輯檢視真實執行 (優先級: 中)
- 以指標導向 Code Review: 透過指標比較不同 Runner，量化優缺點 (優先級: 中)