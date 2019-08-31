---
layout: post
title: "後端工程師必備: 排程任務的處理機制練習"
categories:
tags: ["系列文章", "架構師", "Practices"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2019-08-30-scheduling-practices/2019-08-31-14-19-43.png
---

這篇也是個練習題，這次換個實際一點的主題，"排程任務" 的處理機制。

![](/wp-content/images/2019-08-30-scheduling-practices/2019-08-31-14-19-43.png)


後端服務做久了，一定有碰過這類需求: 使用者想要預約網站在某個指定的時間點執行預先排定的工作。不過，Web Application 先天的框架，就都是 Request / Response 的被動處理模式，有 Request, 才有 Response... 這模式先天就不擅長處理預先排定時間執行的任務。因此這類需求，通常都必須另外處理。雖然有不少現成的套件或是服務可以解決，不過我還蠻期待工程師都能思考看看，如果我找不到合適的套件，必須自己處理時，我知道該怎麼做嗎?

別誤會我不是要大家丟掉現成的服務，全部都自己造輪子...，但是現實狀況的確不是每個情境都完全適用的，這個練習就是讓你先做好準備，有必要時就有能力自己打造。當你能理解背後的設計時，你也同時有能力更精準的評估現有方案的好壞。擁有這能力，你也開始有機會做到更好的整合性。當你必須在既有的系統限制下實做這功能，又不想增加太多不必要的相依姓，或是更動既有的系統架構，都是運用的好時機。

如果不考慮 "預約" 這因素，其實這問題很簡單啊，用 message queue 搭配 worker(s) 就解決了，但是 message queue 都是一瞬間的事情, 預約一小時後才要執行的任務，丟到 queue 然後再讓它佔個位子等一小時才消化，實在不是個好主意。於是我就把這主題簡化一下:

> 在資料庫內維護排定工作的時程表, 你的解決方案只能用 pooling 輪詢的方式, 在指定的時間啟動工作。需要同時解決高可用，以及降低輪詢對於 DB 的效能負擔。

這練習題是我在公司，拿來給架構團隊的 team member 練習思考用的題目，同時也準備實際應用在要上線的專案身上。我想既然都做了準備了，因此也在這邊開放給大家練習看看。規則跟 [上一篇] 一樣，有興趣的請自行到我 GitHub 取用，願意的話，也歡迎將你的 solution PR 放上來，我會在後半段文章用我的角度幫你 code review 。

<!--more-->




# 問題定義

開始解題之前，先對問題做一些了解吧! 主要要解決的問題，是資料庫內有排定的任務清單資料。資料庫隨時會異動，除了定期輪詢之外無法有其它的通知機制告知排程改變。資料庫只能很單純的提供 "被動" 的查詢，意思是不支援像是 [SQL notification service](https://en.wikipedia.org/wiki/SQL_Server_Notification_Services) 這類主動通知異動的機制；資料庫的表格大致像這樣:

| ID | CreateAt | RunAt | ExecuteAt | State |
|----|----------|-------|-----------|-------|
|1|10:00|10:30|*NULL*|0|
|2|10:00|12:00|*NULL*|0|
|3|10:00|08:15|*NULL*|0|

其中，```CreateAt``` 代表這筆資料建立的時間，```RunAt``` 欄位代表 "預定" 要執行的時間， ```ExecuteAt``` 代表實際上被執行的時間，```State``` 則是這筆 Job 的狀態 (0:未執行, 1:執行中, 2:已完成)。

這類問題，如果只管能不能做出來，其實很容易解決啊。只要每分鐘都查一次是否有該執行卻未執行的 jobs, 若有就撈出來處理掉:

```sql

select * from jobs where state = 0 and runat < getdate() order by runat asc

```

不過，這方法常常令工程師陷入兩難...

> "什麼? 精確度只能到分鐘? 能不能精準到秒??"

於是，原本每分鐘查詢一次的動作，就被調快成每秒查一次....

> "為什麼 DB 沒事做也這麼忙? 到底在幹嘛??"

於是，改成每秒查一次的動作又被調慢成每分鐘... 這問題最終會變成死結，因為對於精準的需求會一直提高 (至少到秒級)，而資料量也會一直增加，但是資料庫的效能終究是有極限的...





## 需求定義

由於 DB 的效能是很昂貴且有限的運算資源，因此這樣輪詢的機制，往往要在效能(成本)與精確度之間做取捨...。光是從 "分" 提升到 "秒"，執行的成本就增加了 60 倍... 所以，這次練習主要的目的，就是試著找出，在只能用輪詢的前提下，如何達到下列幾個要求?

1. 對於 DB 額外的負擔，越小越好
1. 對於每個任務的啟動時間精確度，越高越好 (延遲越低越好，延遲的變動幅度越低越好)
1. 需要支援分散式 / 高可用。排程服務要能執行多套互相備援
1. 一個 Job 在任何情況下都不能執行兩次

當然，這些要求的同時也有一些附帶的條件限制，例如:

1. 所有排進 DB 的預約任務，至少都有預留 1 分鐘以上的反應時間。
1. 每個排定的任務，最大允許的延遲啟動時間不能超過 1 分鐘。

講白話一點，意思就是排定 10:30 要執行的任務，一定會在 10:29 之前就寫入資料庫；同時這筆任務最慢在 10:31 之前一定要開始執行。每一筆都只能執行一次，不多不少。否則，你的成績再好看都是假的。




## 評量指標

你能夠滿足基本需求後，接下來就是比較怎樣做會比較 "好" 了。為了方便量化每種不同作法的改善幅度，我直接定義一些指標，將來只要監控這些數據，我們就能量化處理方式的優劣。
假設在一定的時間內 (ex: 10 min)，我有工具按照上述的約束，不斷的產生任務資料排入 DB；額定的時間超過之後 (ex: 10 + 1 min), 應該要滿足下列所有條件才有評比的資格。

對於是否合格的通過條件指標:

1. 所有資料的狀態 (state) 都必須是 2 (已完成)
1. 每一筆紀錄的前置準備時間 (```RunAt - CreateAt```) 都應該大於要求 (ex: 10 sec)
1. 每一筆紀錄的延遲時間 (```ExecuteAt - RunAt```) 都應該小於要求 (ex: 30 sec)


對於排程機制對 DB 額外產生的負擔，我看這些指標最後算出來的分數:

1. 所有查詢待執行任務清單的次數 (權重: 100)
1. 所有嘗試鎖定任務的次數 (權重: 10)
1. 所有查詢指定任務狀態的次數 (權重: 1)

花費成本評分(cost score): (1) x 100 + (2) x 10 + (3)


對於任務實際執行的精確度，我用這些指標最後算出來的分數:

1. 所有任務的平均延遲時間,  ```Avg(ExecuteAt - RunAt)```
1. 所有任務的延遲時間標準差, ```Stdev(ExecuteAt - RunAt)```

精確度評分(efficient score): ```(1) + (2)```


用圖示化的方式說明一下這過程吧。由左到右是時間軸，空心三角形代表預定執行的 Job:

![](/wp-content/images/2019-08-30-scheduling-practices/2019-08-31-17-18-53.png)


如果我定期 (垂直虛線) 掃描一次該執行的 Job ...

![](/wp-content/images/2019-08-30-scheduling-practices/2019-08-31-17-20-58.png)

啟動掃描到的 Job (實心三角形):

![](/wp-content/images/2019-08-30-scheduling-practices/2019-08-31-17-21-39.png)

不斷重複同樣的動作:

![](/wp-content/images/2019-08-30-scheduling-practices/2019-08-31-17-22-02.png)

我們分別標出每個 job 的延遲時間 (Delay #1 ~ #5)

![](/wp-content/images/2019-08-30-scheduling-practices/2019-08-31-17-22-22.png)

這五筆延遲時間的平均值，以及標準差，就是我們精確度評分的項目。



## 測試方式

指標都定義結束了，剩下的問題就簡單了。最後是測試方式。不論你用何方式來開發你的解決方案，我最終會這樣驗證與計算你的程式得分:


首先，先測試可靠度是否達標:

1. 啟用測試程式，會清除資料庫，重建資料。
1. 同時啟用你的排程程式，一次跑 5 instances
1. 隨機次序與時間，再測試程式還未結束前，按下 CTRL-C 中斷 3 個 instance
1. 測試結束後，驗證通過指標


接下來就來測測評分了:

1. 啟用測試程式，會清除資料庫，重建資料。
1. 同時啟用你的排程程式，一次跑 5 instances
1. 測試結束後，驗證評分結果


如果兩個以上的解決方案都不分上下，那可以再做個延伸測試: 重複執行數次上述測驗，找出一次跑多少個 instances 能得到最佳的評分?





# 開發方式

接下來就要開始看 code 了。有興趣的朋友們，請到我的 GitHub: [https://github.com/andrew0928/SchedulingPractice](https://github.com/andrew0928/SchedulingPractice)


**準備資料庫**:

首先，在開始寫任何一行 code 之前，請先準備這次測試需要的資料庫。資料庫的需求很低，只要是 Microsoft SQL Server 即可，版本不要太舊應該都沒問題。我只是用 localdb 就可以搞定了。這次的測試對 DB 的效能要求很低，請不用擔心 SQL 會影響你的測試成績...

為了省麻煩，我的 code (後面說明) 預設就用這組 connection string, 如果你不介意的話，請用 LocalDB, 名字取名為 JobsDB 可以省掉一些麻煩。當然你要另外自己建立也無訪，記得改 code 即可。

預設連線字串: ```Data Source=(localdb)\MSSQLLocalDB;Initial Catalog=JobsDB;Integrated Security=True;Pooling=False```

建立 SQL 用的 [script](https://github.com/andrew0928/SchedulingPractice/blob/master/database.txt):

```sql

CREATE TABLE [dbo].[Jobs] (
    [Id]        INT      IDENTITY (1, 1) NOT NULL,
    [RunAt]     DATETIME NOT NULL,
    [CreateAt]  DATETIME DEFAULT (getdate()) NOT NULL,
    [ExecuteAt] DATETIME NULL,
    [State]     INT      DEFAULT ((0)) NOT NULL,
    PRIMARY KEY CLUSTERED ([Id] ASC)
);


GO
CREATE NONCLUSTERED INDEX [IX_Table_Column]
    ON [dbo].[Jobs]([RunAt] ASC, [State] ASC);



CREATE TABLE [dbo].[WorkerLogs] (
    [Sn]       INT           IDENTITY (1, 1) NOT NULL,
    [JobId]   INT           NULL,
    [LogDate]  DATETIME      DEFAULT (getdate()) NOT NULL,
    [Action]   NVARCHAR (50) NOT NULL,
    [ClientId] NVARCHAR (50) NULL,
    [Results] INT NULL, 
    PRIMARY KEY CLUSTERED ([Sn] ASC)
);

```


**測試程式導覽**:

前面段落提到，測試過程會有個測試程式，啟動後的 10 min 內會不斷的產生測試資料，就是現在要說明的。請看這個 project: ```SchedulingPractice.PubWorker```

程式我就不一一說明了。我說明一下這段 code 執行的流程。最前面幾行，是整段程式的設定，如果你嫌 10 min 跑太久可以改掉:

```csharp

TimeSpan duration = TimeSpan.FromMinutes(10);
DateTime since = DateTime.Now.AddSeconds(10);

```            

另外，我藏了部分整個機制運作的設定，放在 ```SchedulingPractice.Core```:

```csharp

public static class JobSettings
{
    /// <summary>
    /// 最低準備時間 (資料建立 ~ 預計執行時間)
    /// </summary>
    public static TimeSpan MinPrepareTime = TimeSpan.FromSeconds(10);

    /// <summary>
    /// 容許最高延遲執行時間 (預計執行 ~ 實際執行時間)
    /// </summary>
    public static TimeSpan MaxDelayTime = TimeSpan.FromSeconds(30);
}

```



其中, ```since``` 是代表測試開始的時間, ```duration``` 則代表要測多久。這邊分別指定的是 10 sec 後開始，測 10 min ..
在測試開始前的這 10 sec 內, 會 ASAP 的預約接下來 10 min 應該執行的 jobs 資料。包括:

1. 清除 database 的內容
1. 測試期間每隔 3 sec, 就預約 1 筆 job
1. 測試期間每隔 13 sec, 就預約 20 筆 job (測試瞬間多筆 job 的消化能力)
1. 測試期間每隔 1 ~ 3 sec (隨機), 就預約 1 筆 job

接下來 10 sec 應該就過去了，在 ```duration``` 這段期間, 測試程式還是不斷的在進行。這期間測試程式還是不斷的在產生測試資料。這時產生的是:

1. 測試期間，會隨機 sleep 1 ~ 3 sec, 醒來後立刻預約 10 sec 後執行的 job, 一次預約 1 筆

等到 10 min 都過去之後, 測試程式會再多 sleep 30 sec, 等待所有 jobs 應該都被處理完畢後，開始查詢統計資訊。統計的細節我們後面看...。





**撰寫排程服務**

這邊我先說明一下, 我提供了這個 project: ```SchedulingPractice.Core```, 裡面包含了 ```JobsRepo```, 當作存取資料庫的唯一管道。我信任大家不會在 code 裡面動手腳亂搞資料庫，就不做特別防範了。**請不要在你的解題內用任何 JobsRepo 以外的方式存取資料庫!!**

我直接說明一下 ```JobsRepo``` 的結構就好，我內部是用 ```Dapper``` 開發的，有興趣可以挖 code 看看我到底寫了那些 SQL；我列出你在寫解決方案過程中，你可能會用到的 method:


```csharp

    public class JobsRepo : IDisposable
    {
        public IEnumerable<JobInfo> GetReadyJobs() {...}
        public IEnumerable<JobInfo> GetReadyJobs(TimeSpan duration) {...}
        public JobInfo GetJob(int jobid) {...}
        public bool AcquireJobLock(int jobId) {...}
        public bool ProcessLockedJob(int jobId) {...}
    }


```    

1. **查詢(清單)**:  
你可以用 ```GetReadyJobs()``` 取得已經到預約時間，該執行的所有 Jobs 清單。如果你要預先抓未來 10 sec 要被執行的清單，可以加上 ```duration``` 的參數。
1. **查詢(單筆)**:  
如果你需要判讀個別單一一筆 job 的狀態的話，你也可以用 ```GetJob(jobid)``` 來完成這件事。
1. **鎖定**:  
你要先鎖定這個 job, 鎖定成功後才能處理這個 job。如果有多個 worker 同時想要搶奪同一個 job 的執行權，呼叫 ```AcquireJobLock()``` 只會有一個 worker 得到 true 的傳回值 (代表鎖定成功), 其他都會是 false.
1. **執行**:  
當你成功鎖定 job 之後，就可以呼叫 ```ProcessLockedJob()``` 來執行他。

以上的動作都有做防呆，例如你沒鎖定就執行，會得到 exception. 每個動作都有做對應的 log, 最後的評分就是靠這些被後埋的 log 計算出來的。

我提供了一個無腦的解題版本，一樣這是墊底用的低標 solution, 你可以參考這 project 的作法, 但是我預期每個人的 solution 應該都要比他強才對。
接著就來看看這個 demo project: ```SubWorker.AndrewDemo```, 主程式很短，我就全部都貼上來了:


```csharp

namespace SubWorker.AndrewDemo
{
    class Program
    {
        static void Main(string[] args)
        {
            var host = new HostBuilder()
                .ConfigureServices((context, services) =>
                {
                    services.AddHostedService<AndrewSubWorkerBackgroundService>();
                })
                .Build();

            using (host)
            {
                host.Start();
                host.WaitForShutdown();
            }
        }
    }

    public class AndrewSubWorkerBackgroundService : BackgroundService
    {
        protected async override Task ExecuteAsync(CancellationToken stoppingToken)
        {
            await Task.Delay(1);

            using (JobsRepo repo = new JobsRepo())
            {
                while(stoppingToken.IsCancellationRequested == false)
                {
                    bool empty = true;
                    foreach(var job in repo.GetReadyJobs())
                    {
                        if (stoppingToken.IsCancellationRequested == true) goto shutdown;

                        if (repo.AcquireJobLock(job.Id))
                        {
                            repo.ProcessLockedJob(job.Id);
                            Console.Write("O");
                        }
                        else
                        {
                            Console.Write("X");
                        }
                        empty = false;
                    }
                    if (empty == false) continue;

                    try
                    {
                        await Task.Delay(JobSettings.MinPrepareTime, stoppingToken);
                        Console.Write("_");
                    }
                    catch (TaskCanceledException) { break; }
                }
            }

            shutdown:
            Console.WriteLine($"- shutdown event detected, stop worker service...");
        }
    }
}


```

為了解決 HA (High Availability) 的問題，我用了 .NET core 支援的 generic host 的機制來處理 graceful shutdown 的問題。透過新的 generic host, 你可以輕易開發出適用在 container (long running), windows service (windows), systemd (linux) 這些[管理機制](https://www.hanselman.com/blog/dotnetNewWorkerWindowsServicesOrLinuxSystemdServicesInNETCore.aspx) 上的服務。撇開這些設計，剩下的就是單純的排程處理了。

我這段 code 示範的就是最常見的作法，只要你沒有按 CTRL-C 中斷執行，那麼解題程式就會不斷重複這動作:

> 查詢該執行而未執行的 jobs, 如果有的話就試著 lock, 成功就 process。處理完就再查詢一次看看是否還有新的 job 被排入資料庫? 沒有的話就休息 10 sec 再重複。過程中如果按下了 CTRL-C, 則會在處理目前這筆 job 後才會退出，不會發生 lock 卻未 process 的狀況。



**處理結果**:

按照前面我說的測試方式，跑 10 min 後可以看到這樣的 console output:

```

Init test database...
- now:   8/31/2019 2:21:32 AM
- since: 8/31/2019 2:21:42 AM
- until: 8/31/2019 2:31:42 AM

Step 0: reset database...

Step 1: add job per 3 sec
........................................................................................................................................................................................................
- complete(200).

Step 2: add 20 jobs per 13 sec
............................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................
- complete(940).

Step 3: random add job per 1 ~ 3 sec
.........................................................................................................................................................................................................................................................................................................
- complete(297).

Step 4: realtime: add a job scheduled after 10 sec, and random waiting 1 ~ 3 sec.
.................................................................................................................................................................................................................................................................................................
- complete(289).

Database initialization complete.
- total jobs: 1726
- now:   8/31/2019 2:31:33 AM
- since: 8/31/2019 2:21:42 AM
- until: 8/31/2019 2:31:42 AM

Jobs Scheduling Metrics:

--(action count)----------------------------------------------
- CREATE:             1726
- ACQUIRE_SUCCESS:    1726
- ACQUIRE_FAILURE:    4916
- COMPLETE:           1726
- QUERYJOB:           0
- QUERYLIST:          702

--(state count)----------------------------------------------
- COUNT(CREATE):      0
- COUNT(LOCK):        0
- COUNT(COMPLETE):    1726

--(statistics)----------------------------------------------
- DELAY(Average):     4343
- DELAY(Stdev):       2858.51700217987

--(test result)----------------------------------------------
- Complete Job:       True, 1726 / 1726
- Delay Too Long:     46
- Fail Job:           True, 0

--(benchmark score)----------------------------------------------
- Exec Cost Score:      119360 (querylist x 100 + acquire-failure x 10 + queryjob x 1)
- Efficient Score:      7201.52 (average + stdev)

C:\Program Files\dotnet\dotnet.exe (process 10880) exited with code 0.
Press any key to close this window . . .


```

測試的結果不算好看，總共 1726 筆 job 預約紀錄中, 平均延遲竟然到了 4343 msec, 標準差也到了 2858 ..
Jobs 全部都成功執行完畢，但是有 46 筆沒辦法在指定時間內完成...

最後的 cost score / efficient score 分別是 119360 分 / 7201.52 分。




## 寫在最後

這次的題目，算是比較務實的問題解決，考驗的是你解決實際問題的技巧。平時專案進行過程中，應該沒太多機會練習或是討論這類議題吧! 如果缺乏明確的指標，有時你可能也無從得知不同作法到底有沒有差異。這次會有機會，在公司內部進行這樣的練習與評估，主要原因是專案需要，同時我也希望團隊成員除了交付專案的需求之外，也能自我要求，在能力所及的範圍內做到最好。為了讓團隊能夠明確的比較各種方式的優劣，我才會自己先花時間準備了這個練習題，同時也花了些時間準備評估的方式。

有興趣的話，趁這次機會，用簡化過的 POC 環境來練習看看吧! POC 的好處是你可以專注在問題本身，盡可能地排除其他環境或是框架帶來的干擾，讓你專心地思考問題本身該怎麼解決。也只有 POC (尤其是我提供的練習環境)，你才能有機會觀察到實際測試的統計數據與評分，讓你比較與改善的過程可以更加科學。

最後還是要來工商一下，你對這樣的挑戰與工作方式感興趣的話，歡迎在 FB 留言找我聊聊 :D




# Code Review (敬請期待)