# 後端工程師必備: 平行任務處理的思考練習

# 問題／解決方案 (Problem/Solution)

## Problem: 工程師無法「精準」掌握程式執行與效能

**Problem**:  
在日常開發中，開發者大量倚賴框架與外部服務，往往只要功能能動就提交。當程式佈署到雲端且流量變大時，效能微幅下滑便直接反映在 VM 數量與月租費上。例如同一段程式若能再提升 1% 效能，整體雲端成本即可下降 1%，反之亦然。

**Root Cause**:  
1. 現代框架高度封裝，工程師漸漸忽略底層 Thread、Memory、排程等基礎能力。  
2. 缺少「可量化指標」與「理論極限」的概念，因此無法判斷自己的程式離目標還有多遠，導致盲目堆硬體或微調卻收效有限。  

**Solution**:  
設計一套「平行任務處理練習題」，讓參與者必須自行撰寫 `TaskRunner` 來完成 1000 個 `MyTask`。題目刻意加入下列限制，迫使開發者面對真實世界的資源分配問題：  
- 三段步驟 (Step1~3) 必須依序執行。  
- 每一步驟的併行量有限 (Step1:5、Step2:3、Step3:3)。  
- 每一步驟耗時 / Memory 不同，開始即配置，結束才釋放。  

同時內建四大品質指標：  
1. Max WIP (半成品數)  
2. Memory Peak  
3. TTFT (第一筆完成時間)  
4. TTLT (全部完成時間) + AVG_WAIT (平均交期)  

並以 Console Summary ＋ CSV (可匯入 Excel 畫圖) 方式輸出，讓開發者能「量化」自己的優化成果。  
範例 `AndrewPipelineTaskRunner1` 使用 Producer/Consumer + BlockingCollection + 專屬 Thread Pool，示範如何在 TTLT、AVG_WAIT 均逼近理論極限 0.03% 內：

```csharp
public class AndrewPipelineTaskRunner1 : TaskRunnerBase
{
    private BlockingCollection<MyTask>[] queues = {
        null,
        new BlockingCollection<MyTask>(),
        new BlockingCollection<MyTask>(),
        new BlockingCollection<MyTask>()
    };

    public override void Run(IEnumerable<MyTask> tasks)
    {
        int[] limits = {0,5,3,3};                   // 併行上限
        List<Thread> workers = new List<Thread>();

        // 依步驟建立對應執行緒
        for (int step=1; step<=3; step++)
            for (int i=0;i<limits[step];i++)
                workers.Add(new Thread(DoStep){ IsBackground=true })
                       .Last().Start(step);

        // 將任務導入 Step1
        foreach(var t in tasks) queues[1].Add(t);
        queues[1].CompleteAdding();

        // 等候全部 Thread 結束
        workers.ForEach(th=>th.Join());
    }

    private void DoStep(object s)
    {
        int step=(int)s;
        foreach(var task in queues[step].GetConsumingEnumerable())
        {
            task.DoStepN(step);
            if(step<3) queues[step+1].Add(task);
        }
        if(step<3) queues[step+1].CompleteAdding();
    }
}
```

**Cases 1**:  
公司內部 5 人小組以此練習為 1 週衝刺目標，最後版本使 TTLT 從 290 sec 改善到 176 sec，雲端 VM 使用量下降 18%，月費省下近兩成。

---

## Problem: 錯誤的平行化策略導致記憶體爆炸與瓶頸惡化

**Problem**:  
常見的「一股腦開 N 個 Thread / VM」解法，若忽視每一步驟的併行限制與不同記憶體需求，會出現：  
• Step1 受限 5 條 Thread，其餘 Thread 閒置 → CPU 浪費  
• 1000 筆 Task 全部同時進入，占用記憶體 ×1000 → OOM

**Root Cause**:  
1. 不理解 Producer/Consumer 流程，誤把「總 Thread 數」當成效能保證。  
2. 沒有 WIP 與 Memory Peak 觀念；無法在「吞吐」與「資源」之間找到平衡。  

**Solution**:  
導入生產者/消費者 Pipeline 模式，並使用下列工具精準控管：  
- BlockingCollection / Channel：作為步驟間 Queue，內含同步或非同步 Block 機制，自動喚醒或暫停生產者。  
- SemaphoreSlim：限制各步驟 Thread 進入數，確保不超出題目上限。  
- ThreadPool / Task.ContinueWith：在完成 StepN 時立即排程下一步，減少 Thread 空轉。  

示例 – 來自 PR8 `JWTaskRunnerV5`：  

```csharp
ThreadPool.SetMinThreads(14,14);   // 5+3+3 + buffer
Queue.Init();                      // 建立三個 BlockingCollection

// 建立三組 Worker
Task.Run(()=> new JobWorker(1,5));
Task.Run(()=> new JobWorker(2,3));
Task.Run(()=> new JobWorker(3,3, total, doneEvent));

// 將 1000 筆任務推入 Step1 Queue
foreach(var t in tasks) Queue.Produce(1,t);
doneEvent.WaitOne();               // 等待全部完成
```

該方案 TTLT 174 496 ms (理論 174 392 ms, 誤差 +0.06%)、Memory Peak 27 904 bytes，證明「精準併發」可在資源極小化下逼近極限吞吐。

**Cases 2**:  
• PR3 `EPTaskRunner` 採過度限縮 Thread (3 條) → WIP=7，TTLT 衰退至 290 307 ms (理論 166%)；調整為 Step 上限後，TTLT 立即降至 174 xxx ms。  
• PR6 `JulianTaskRunner` 改用 Channel + async/await + 單一 Queue → Memory 32 384 bytes, TTLT 174 467 ms，印證 Channel 能在非同步場景取得相同效益。

---

## Problem: 缺乏指標與理論基準，優化方向與投資報酬率難以判斷

**Problem**:  
很多團隊在「效能改善」議題上，只知道盲目重寫或加 Server，卻無法回答：  
• 「第一筆結果多久出來？」  
• 「全部跑完要多久？」  
• 「目前數值距離理論極限還有幾 %？」  

**Root Cause**:  
1. 沒有建立 TTFT / TTLT / AVG_WAIT / WIP 等客觀衡量指標。  
2. 不會先計算「理論極限」(Step1~3 官方耗時 ÷ 併行上限)；因此不知何時該停止微調，轉而尋找新架構。  

**Solution**:  
1. 題目內建 `Execution Summary` 與 `.csv` 細部資訊：  
   • Console 即時列出 Max WIP、Memory Peak、TTFT、TTLT、AVG_WAIT。  
   • CSV 詳錄 TS/MEM/WIP/THREADS/T1~T30，方便 Excel 繪圖或比對排程。  
2. 訓練工程師先「推算理論值」，再比對自己程式的百分比差距：  
   • 理論 TTFT = 867 + 132 + 430 = 1 429 ms  
   • 理論 TTLT = Step1 200 批 × 867 + 132 + 430 + 430 ≒ 174 392 ms  
   • 以此為基準，才知道調校是否已到天花板。  

**Cases 3**:  
• PR1 `LexTaskRunner` 初始只靠 Semaphore+Task，TTLT 174 479 ms (+0.05%)，顯示 .NET TPL 已能追到理論極限；開發者因此停止無謂優化，轉向功能開發。  
• 公司實際專案中，先用練習專案調出瓶頸指標，再把相同指標搬進批次報表服務，排查 3 小時批次縮短到 40 分鐘。  

---

# 小結

1. 沒指標 ➜ 不知問題在哪，也就談不上優化。  
2. 指標有了，但若不懂「極限值」 ➜ 容易在 0.5% 的邊際效益不斷燃燒工時。  
3. 真正的「精準」：  
   • 先用理論推算天花板  
   • 建立量化指標＋可視化工具  
   • 依據問題性質選擇策略：  
     - 需求模糊 ➜ 使用 PLINQ / TPL / ThreadPool 獲得 80 分通用解  
     - 資源或效能極限 ➜ 自建 Pipeline + Thread + BlockingCollection 作 95~99 分精調  
4. 實務效益：多個案例證明，只要在 TTFT、TTLT、WIP 上各省 1%，月雲端帳單亦同步下降 1%，且系統穩定度隨之提升。