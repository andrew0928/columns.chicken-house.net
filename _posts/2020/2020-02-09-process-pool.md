---
layout: post
title: "架構面試題 - Process Pool"
categories:
tags: ["系列文章", "架構師", "C#"]
published: false
comments: true
redirect_from:
logo: 
---

會想解決這個議題: **Task Management**, 是剛好工作上面臨的技術架構需求。不過這篇我沒打算把主題擴的那麼大，我就專注在我要解決的問題上了。還記得我多年前寫的一系列多執行緒的文章嗎? 其中有一篇，我花了 100 行左右的 C# code, 實作出一個完整功能的 thread pool, 能動態調節適合的 threads 數量來處理工作負載。這次，我要把這同樣的機制，擴大成分散式版本的 process pool, 而其中相關的設計決策，我則搭配了我在過程中做的研究與 POC 來說明。

不過，這次我要面對的需求，其實遠遠比 Task Management 還要複雜啊! 過去在開發 Thread Pool, 主要面對的是效能問題, 要炸出極端的效能, 就必須面對生產者跟消費者的高度協調才能辦到，重點都在執行緒的控制。不過，這次搬上實際應用的場景，同時還是全部研發團隊 (100+ 人) 必須共同運作的通用平台，就多了非常多維運與可靠度上的考量。

我就針對我最在意的一點: 那麼多人寫的 code 都要丟在一起排程執行與管理, 一定會面臨執行環境隔離的議題, 也會面臨分散式的考量。這是一體兩面，要有適當的隔離，某段 code 失敗造成的影響才能被控制住不會影響其他任務；適度的隔離間接帶來的好處，就是更容易變成分散式的機制，達到橫向擴展 (scale out) 的要求。這些主題，其時我過去的文章都有個別談到了，這篇我就集中在探討 "isolation" 隔離這件事身上。

這篇文章，我分三個段落來說明最終 Process Pool 這個構想是怎麼誕生的:

1. 挑戰: Isolation 的機制研究:  
了解與比較各種執行環境隔離的技術 (InProcess / AppDomain / Process), 以及如何橫跨隔離環境進行有效率的通訊 (IPC)
1. 為何你需要隔離環境:  
交代我工作場合面臨的需求與挑戰，Container + Orchestration / Serverless 無法滿足的需求
1. 挑戰: Process Pool  
在技術與平台的選擇與平衡, 如何設計 Process Pool 

在這過程中，其時用了很多我過去文章個別提過的好幾種技巧，算是個終極的綜合應用篇吧! 最遠可以追溯到 10 年前那系列 Thread Pool 設計與實作的相關文章。只是這篇的應用，把 "Thread" Pool 的觀念，擴大到 "Process" Pool 了。現在的技術，Process 層級的隔離期時有更多的工具可以運用了，例如 Container 就是一例；所以過程中我也花了不少時間在拿捏，站在巨人的肩膀上 vs 重新發明輪子 的取捨；對這部分有興趣的讀者們，可以直接跳到第二段。


<!--more-->

葉配: 繼續寫下去前先補一些我自己的心得, 如果你也想挑戰這樣的工作內容, 請跟我聯絡 XD

> 最近花了點時間，重新讀了一次我自己寫的文章，自從我開始把主軸轉移到 container 及 microservices 之後, 我發現我越來越能針對特定主題深入探討了。其實這跟工作內容的改變也有直接的關聯。過去我的角色是一路從 Tech Lead 一路做到 CTO, 我需要替團隊做好技術決策與開發管理，寫出來的文章大都偏向實作會碰到的問題。近幾年開始轉型擔任架構師，開始對於架構設計的 "WHY" 有更深刻的體認了，我開始有機會能從 "WHY" 到 "HOW" 整個完整的過程來探討特定的技術主題，才會有這些內容的分享。台灣的軟體產業，很可惜的是很難有這樣的空間經歷這些過程，有的公司沒有發揮的舞台，有的公司老闆不重視，有的公司苦於找不到合適的人才來主導...



<!-- 


Thread pool, 主要是妥善的安排 threads 來處理 workload, 而須要把 thread 升級成 process, 不外乎是要有更好的隔離 (isolation) 層級。同機器的 process 之間有完全獨立的 memory space, 你就能有更大的彈性裝載不同的開發技術。若你都已經將 workload 抽象化到 process 的層級, 你要擴大到分散式就是很容易的一件事了。不過這篇我不會擴大到跨機器的實作，這部分我只會點到為止，留一些關鍵字讓讀者們自己去推敲。

這次我需要設計一個通用的 task 管理機制, 讓各個開發團隊能將自己開發的 task 掛上這機制來運行。因為這樣可能有跨越多個團隊程式碼彼此衝突的風險存在，因此是否能有效做好隔離就是成功的關鍵之一。另一個關鍵則是在隔離的前題下，是否還能有效的兼顧效能? 這兩者之間能取得的最佳平衡點，就是我這篇文章要探討的目標。

大概交代一下問題背景，就可以直接開始了。我會探討 C# 各種隔離的技術 (thread, app domain, process) 開始, 一步一步推進到我最終的版本: process pool, 想看最後的程式碼可以直接跳到最後一段就好，想知道我如何無中生有的進行設計與決策過程，那請按照順序往下看。第一步分我會先搞清楚，C# 能用的各種 isolation 機制的特性及優缺點，若你有研究過 cloud native 的設計思維, 12 factors app 就把 process 當作其中一個關鍵的設計因素；第二部分則是來探討這些 isolation 的機制該如何搭配編排 (orchestration) 的做法，來達到整體產出 (throughput) 最大化的目的。

其實這兩個目的 (isolation / orchestration), 乍看之下也都跟使用 container 的目的相符合, 最後結論的地方我也會說明一下適用的時機, 當你的需求規模大到某個程度後, 你更應該考量用成熟的機制 (例如: container + k8s), 當規模化的機制無法 100% 滿足你的前題下, 你才應該局部的用自行開發的方式, 補足你需要的那個環節即可。 -->




# 挑戰: Isolation 的機制研究

雖然我有跨平台的需求 (需要跨越 windows / linux 這些作業系統, 同時開發技術也需要跨越 .net frameowkr / .net core / node js), 不過主力還是 C#, 因此我還是以目前最大宗的 C# / .net framework 為起點好了。

根據隔離的層級不同，我大概區分這幾種可行的做法:


1. In-Process (Direct Call):  
完全正常的呼叫方式，不多做說明。  

1. Thread:  
執行緒之間除了執行的順序各自獨立之外, 幾乎沒有任何隔離的措施了。這個就當作完全沒有隔離機制的對照組。  

1. GenericHost:  
從 .net core 2.0 開始被引入的機制。嚴格的來說這不算強制的隔離機制，但是在 DI (dependency injection) 的技術越用越廣泛的今日, 一個 generic host 代表的就是一個獨立的 DI container, 所有相依注入的註冊資訊都會被隔離開來。這是個有潛力的技術, 不過現階段還沒辦法解決我的需求 T_T, 因此僅止於介紹, 這次不參與評估。  

1. AppDomain:  
從 .NET Framework 時代就開始支援的技術，直接由 .NET runtime 提供，相較於 process 來說更為輕量化的隔離技術。AppDomain 是 .NET CLR 提供的機制, 他同樣提供了兩個不想被互相影響的程式 (assembly) 有互相獨立不被干擾的 space, 透過 .NET API 的保證, .NET 的物件是無法跨越 AppDomain 的邊界的。不過這些優點是有代價的，由於是 .NET runtime (CLR) 提供的技術, 只有支援該 runtime 的程式 (assembly) 才能被使用載入執行。  

1. Process:  
直接由作業系統 (OS: operation system) 提供的機制。OS 在載入任何程式支前, 都會先在 OS 內建立一個新的處理程序 (process), 有獨立的啟動點，也有完全隔離的 memory space, 隨後才在這個 process 內載入及執行你指定的程式 (executable)。由於這是由 OS 提供的機制，因此只要被該 OS 支援的程式都可以支援，不限定開發技術或是開發語言。雖然使用的方式有點不同，但是基本上 container 也是屬於這個層級。不過這次探討的主要是以開發為主，我就不特別再介紹 container 的做法了。  

1. Hypervisor:
由硬體虛擬化提供的機制。一套支援虛擬化的硬體設備，搭配 hypervisor 的抽象層，可以在這基礎之上模擬成獨立的多個硬體設備，分別在這上面載入 OS ，進一步執行程式。這比起 Process 來說有更安全的隔離層級。不過通常再開發的階段，我都把 Hypervisor 隔離的環境直接當作 VM (virtual machine) 看待了。對於大部分的開發者來說，實體機器跟虛擬機器在開發上沒有太多的不同，這技術一樣我也不特別討論了，我直接歸類在分散式的環境下討論。


基本觀念介紹完一輪後，後面的 POC 我就只針對 threads , application domain, process 三者來比較就好了，請繼續看下去...




## Benchmark: 隔離環境的啟動速率

真正開始測試執行速率前，我先準備了一個啥事都不做的 Main(), 呼叫了立馬 return 的 code:

```csharp

class Program
{
    static void Main(string[] args)
    {
    }
}

```

接著，我用 .NET Framework 4.7.2 起了一個 Console App 的 project, 分別用了這五種方式，建立執行環境 (如果需要的話)，然後呼叫這個 Main() 一次，離開。如此重複 100 次，計算每秒可以跑幾次。第一次先來看看每個測試的 code。

### InProcess Mode

直接呼叫, 沒有任何隔離層級的設計:

```csharp

Stopwatch timer = new Stopwatch();
int total_domain_cycle_count = 100;

timer.Restart();
for (int i = 0; i < total_domain_cycle_count; i++)
{
    HelloWorldTask.Program.Main(null);
}
Console.WriteLine($"Benchmark (InProcess Mode):           { total_domain_cycle_count * 1000.0 / timer.ElapsedMilliseconds } run / sec");

```

跑出來的結果: 

```
Benchmark (InProcess Mode):           ∞ run / sec
```

由於跑的太快，C# 直接給我顯示無限大 XDDD, 其實真的去追究差異倍數意義也不大，我就不去追了。大家只要知道這個版本跑很快就好...


### Thread Mode

這次每個 Main() 的呼叫，都用一個執行緒來包裝他。前後幾行 init Stopwatch 跟計算結果的 code 我就直接略過了:


```csharp

for (int i = 0; i < total_domain_cycle_count; i++)
{
    Thread t = new Thread(() =>
    {
        HelloWorldTask.Program.Main(null);
    });
    t.Start();
    t.Join();
}

```

這個版本跑出來的結果: 

```
Benchmark (Thread Mode):              ∞ run / sec
```

一樣是無限大，比較就沒什麼意義了，一樣略過。


### AppDomain Mode

這版本特別一點，我直接用 .NET Framework 的特殊機制 Application Domain 來實作。先看 code:

```csharp

for (int i = 0; i < total_domain_cycle_count; i++)
{
    var d = AppDomain.CreateDomain("demo");
    var r = d.ExecuteAssemblyByName(typeof(HelloWorld).Assembly.FullName);
    AppDomain.Unload(d);
}

```

這版本跑出來的結果: 

```
Benchmark (AppDomain Mode):           333.333333333333 run / sec
```


### Process

這個版本，我直接把 Main() 編譯成獨立的 .exe, 然後透過 Process 物件來啟動獨立的程序，測試執行 .exe 的速度。這邊的結果頗令我意外，因為我用模一樣的 code, 甚至用一樣的 .NET Standard 編譯出來的 binary code 來寫關鍵部分, 只是最後用兩個不同的專案來編譯而已。結果編譯成 .NET Framework 跟 .NET Core 跑出來的結果有很大的落差。多跑幾次或是重新開機都會有些變化，受環境影響的因素不少。我跑了好幾次挑有代表性的貼結果就好。先來看 code (都一樣的 code, 只有執行檔的路徑不一樣):


```csharp

for (int i = 0; i < total_domain_cycle_count; i++)
{
    var p = Process.Start(new ProcessStartInfo()
    {
        FileName = @"C:\CodeWork\github.com\Andrew.ProcessPoolDemo\ProcessHostFx\bin\Debug\ProcessHostFx.exe",              // .net fx 4.7.2
        WindowStyle = ProcessWindowStyle.Hidden,
    });
    p.WaitForExit();
}
 
```

再來看看跑出來的結果:

```
Benchmark (.NET Fx Process Mode):     11.7647058823529 run / sec
Benchmark (.NET Core Process Mode):   12.6582278481013 run / sec
```

附註說明一下， .NET Fx 我使用的版本是 4.7.2, .NET Core 則是用 3.1


### 小結

把結果列在一起看一下吧! 主程式是用 .NET Framework 開發的，因為不用 .NET Fx 我就無法使用 AppDomain 了:

|Freq\Mode    |InProcess|Thread|AppDomain|Process(.NET Fx)|Process(.NET Core)|
|-------------|---------|------|---------|----------------|------------------|
|單位: run/sec|∞|∞|333.3333|11.7647|12.6582|



(圖表)




看起來落差很大啊! 不過我不急著解讀這個測試結果。先把數據留著，後面再一起看吧! 不過看到同樣的 code, 用 .NET Fx / Core 的差距竟然這麼明顯，我就交叉測試了一下，把主程式也用 .NET Core 測了一遍。不過 .NET Core 不支援 AppDomain, 因此測試項目 AppDomain 會從缺。我直接把兩份測試結果列在同一個表格:

.NET Fx:

```
Benchmark (InProcess Mode):           ∞ run / sec
Benchmark (Thread Mode):              ∞ run / sec
Benchmark (AppDomain Mode):           333.333333333333 run / sec
Benchmark (.NET Fx Process Mode):     11.7647058823529 run / sec
Benchmark (.NET Core Process Mode):   12.6582278481013 run / sec
```

.NET Core:

```
Benchmark (InProcess Mode):           ∞ run / sec
Benchmark (Thread Mode):              ∞ run / sec
Benchmark (.NET Fx Process Mode):     31.25 run / sec
Benchmark (.NET Core Process Mode):   23.25581395348837 run / sec
```

|Freq\Mode    |InProcess|Thread|AppDomain|Process(.NET Fx)|Process(.NET Core)|
|-------------|---------|------|---------|----------------|------------------|
|主程式: .NET Fx|∞|∞|333.3333|11.7647|12.6582|
|主程式: .NET Core|∞|∞|無法測試|31.2500|23.2558|



(圖表)



## Benchmark: 不同環境的 Task 執行效率

開始之前，我先寫了一個很簡單的 code, 來做為比較的標準依據:

```csharp

public class HelloWorld
{
    public string DoTask()
    {
        Random rnd = new Random();
        byte[] buffer = new byte[1 * 1024 * 1024]; // 1mb
        rnd.NextBytes(buffer);

        var ha = HashAlgorithm.Create("SHA512");
        var hash = ha.ComputeHash(buffer);

        return Convert.ToBase64String(hash);
    }
}

```    

這段 code 唯一的目的，就是造成一些合理的負載而已。我先配置了 1MB 的 buffer, 打算用這方式對 Heap 造成一些壓力；用亂數填入這 1MB 的記憶體空間，然後用 SHA512 的演算法計算 hash .. 這些動作打算對 CPU 造成一些壓力；往後所有的效能測試，都會以計算一秒能夠執行這個 task 幾次為參考依據。留意一下，這段 code 雖然 source code 一致, 不過有可能會在不同的 runtime 下執行；我在過程中就不小心踩到這個地雷 (後面會說明)，害我一直以為我的實驗數據不對勁...

這段 code 我直接用 .NET standard 2.0 的規範開發與編譯, 其他專案不論是 .NET framework 或是 .NET code, 都會共用同一個 binary code 來執行。接著，我也把 Main() 的部分做了點調整。原本是立馬 return 的 code, 改成呼叫 100 次 HelloWorld:

```csharp

public static int Main(string[] args)
{
    for (int i = 1; i < 100; i++)
    {
        new HelloWorld().DoTask();
    }
    System.Threading.Thread.Sleep(10 * 1000);
    return 0;
}

```        

然後，測試的主程式就不再跑 100 次重新建立環境的 code 了，這次我只執行一次。我的目的是想觀察，這 HelloWorld 在不同環境下的執行速率有沒有影響。其他 code 都完全一樣，我就不逐一說明跟測試了，直接看測試結果:

.NET Fx 測試結果:

```
Benchmark (InProcess Mode):           21.1237853823405 run / sec
Benchmark (Thread Mode):              21.0482003788676 run / sec
Benchmark (AppDomain Mode):           21.1327134404057 run / sec
Benchmark (.NET Fx Process Mode):     20.6100577081616 run / sec
Benchmark (.NET Core Process Mode):   88.5739592559787 run / sec
```

.NET Core 測試結果:

```
Benchmark (InProcess Mode):           94.5179584120983 run / sec
Benchmark (Thread Mode):              93.63295880149813 run / sec
Benchmark (.NET Fx Process Mode):     20.955574182732608 run / sec
Benchmark (.NET Core Process Mode):   93.63295880149813 run / sec
```


比較表:

|Freq\Mode        |InProcess|Thread     |AppDomain|Process(.NET Fx)|Process(.NET Core)|
|-----------------|---------|-----------|---------|----------------|------------------|
|主程式: .NET Fx  |21.1238   |21.0482    |21.1327  |20.6101         |88.5740           |
|主程式: .NET Core|94.5180   |93.6330    |--       |20.9556         |93.6330           |

看起來，這段 code 本身光是編譯成 .NET Fx / Core, 執行速度就有差距了，不過看的出來 .NET Core 原生的效能大勝啊... 這邊先不深入探討原因，先記錄實驗結果就好，後面一起看結果。




## Benchmark: 不同環境的 Task 參數傳遞效率

接下來開始的 code 就要認真面對了，前面都是簡單測完 code 我就砍了 (啥? XDD)。接下來，我要開始模擬真正的執行狀況，我希望 Task 能夠如同本地端的 lib 一樣容易的呼叫，需要傳遞參數過去，也需要傳遞結果回來。我期望主控端建立好環境後，可以傳遞 task 需要的參數過去，然後等待執行結果回來。除了參數根結果的傳遞之外，我需要 task 所有執行過程都被限制在安全的隔離環境內。

不同的隔離方式，有不同的通訊技巧。我這邊把通訊的需求簡化成傳遞呼叫參數，跟傳回執行結果就好。基本上 InProcess / Thread 都在同一個 memory space 下，直接傳遞物件的 reference 就夠了。AppDomain 嚴格的說也是在同個 memory space (相同 process 的多個 AppDomain, 是共用 managed heap 的), 只是 heap 內的物件存取會被 AppDomain 管控。跨越 AppDomain 存取物件，必須透過 Marshal 的機制處理。至於 memory space 完全獨立的 process, 只能透過 OS 層級的機制了, 例如 pipe, network, share file / memory map file 等等都是可行的做法, 後面的 code 我就直接拿 standard I/O + pipe 來示範..

測試模式跟剛才差不多，不過因應這個測試需求，我改了一些 code ..., 為了鋪梗後面的延伸範例, 我先把 POC 架構一次到位。我用以前寫過的 ThreadPool 當作範本，過去自己手動搞定 ManualResetEvent 的部分，我這邊直接用 BlockingCollection 簡化了。所有的 POC 都從 WorkerBase 衍生出來:

```csharp

public abstract class HelloWorkerBase
{
    public HelloWorkerBase()
    {
    }

    public abstract HelloTaskResult QueueTask(int size);

    public abstract void Stop();

    
    public class HelloTaskResult
    {
        public string ReturnValue;
        public ManualResetEventSlim Wait = new ManualResetEventSlim(false);
    }

}

```

我抽象化了各種 Worker 的實作；Worker 只限定處理 HelloTask, 但是我希望這些 HelloTask 將來能在各種不同隔離層級的要求下，有效率的處理 HelloTask...。因此 POC 公開的介面就是 QueueTask(), 我只傳遞執行 Task 必要的參數 (int size) 就夠了。為了精確控制 thread, 我選擇跳過 .NET 內建的 async / await 機制, 用簡單的 TaskWrap 來封裝執行結果。

如果資深一點的 developer, 應該會記得當年還沒有 async / await 時, .NET 怎麼處理這類問題的方法吧? IAsyncResult .. 我這邊就是做了一個簡化的版本: HelloTaskResult, 來當作 QueueTask() 的傳回值。這設計允許你先拿到 Result, 然後在需要的時候再呼叫 HelloTaskResult.Wait.Wait() 來等待結果。整個 Worker 設計上應該要允許平行處理，直到 Worker.Stop() 被呼叫為止。呼叫 Stop() 會停止接受新的 QueueTask() 需求，同時 Stop() 會等待 (blocking) 到所有 Task 都完成為止才會 return 。


先從單純一點的測試開始吧。我先不去處理平行執行的部分，參數也先以最單純的 value 為主就好。我來測試看看，不重覆建立隔離環境的前提下，加上傳遞參數的效能測試。我暫時把 HelloTask.DoTask() 的內容清空，我想先測試一下空轉時這個機制的效能極限:

```csharp

public class HelloTask : MarshalByRefObject
{
    public string DoTask(int size) => null;
}

```

不論你用哪一種 Worker 的實作來執行 HelloTask, 我都用這段程式碼來測試效能:

```csharp

static void Main(string[] args)
{
    var worker =
        //new InProcessWorker();
        //new ThreadWorker();
        //new SingleAppDomainWorker();
        new SingleProcessWorker();

    Stopwatch _timer = new Stopwatch();
    int count = 10000;

    _timer.Restart();
    for (int i = 0;i<count; i++)
    {
        var task = worker.QueueTask(1);
        // task.Wait.Wait();
        // Console.WriteLine(task.ReturnValue);
    }
    worker.Stop();

    Console.WriteLine($"{worker.GetType().Name}: {count * 1000.0 / _timer.ElapsedMilliseconds} tasks/sec");
}

```


### 基本參數傳遞測試

接著先來看對照組 InProcessWorker: 完全沒有做任何隔離環境，直接執行 HelloTask ...

```csharp

public class InProcessWorker : HelloWorkerBase
{
    public override HelloTaskResult QueueTask(int size)
    {
        return new HelloWorkerBase.HelloTaskResult(true)
        {
            ReturnValue = (new HelloTask()).DoTask(size)
        };
    }

    public override void Stop()
    {
        return;
    }
}

```    

測試空轉 10000 次 HelloTask 呼叫的結果: `InProcessWorker: ∞ tasks/sec`
一如預期，一樣跑到破表...


接下來來看看 AppDomain 的部分。基本上時作的方式跟 InProcessWorker 雷同，主要的差異在於，跨越 AppDomain 的物件傳遞，必須透過 .NET Marshal 的機制來處理才行。所幸 Microsoft 幫我們把大部分的細節都處理掉了，我只需要讓 HelloTask 繼承 MarshalByRefObject, 基本上就搞定了:

```csharp

public class HelloTask : MarshalByRefObject
{
    public string DoTask(int size) => null;
}

```

接著來看看 SingleAppDomainWorker 的實作:

```csharp
    public class SingleAppDomainWorker : HelloWorkerBase
    {
        private AppDomain _domain = null;

        public SingleAppDomainWorker()
        {
            this._domain = AppDomain.CreateDomain("demo");
        }

        public override HelloTaskResult QueueTask(int size)
        {
            HelloTask ht = this._domain.CreateInstanceAndUnwrap(typeof(HelloTask).Assembly.FullName, typeof(HelloTask).FullName) as HelloTask;

            return new HelloWorkerBase.HelloTaskResult(true)
            {
                ReturnValue = ht.DoTask(1),
            };
        }

        public override void Stop()
        {
            AppDomain.Unload(this._domain);
            this._domain = null;
            return;
        }
    }
```

關鍵在於這段: CreateInstanceAndUnwrap(...), 透過 AppDomain 的這個方法，你告訴指定的 AppDomain 要替你建立指定的物件，然後 Unwrap (背後需要經過 ObjectHandle 處理), 經過一連串的步驟把遠在另一個 AppDomain 的物件穿越回你現在的 AppDomain... 拿到 Unwrap 後的物件你就能直接呼叫他了。除此之外，這段 code 其時跟 InProcessWorker 沒有什麼不同。

來看看執行結果: `SingleAppDomainWorker: 26666.6666666667 tasks/sec`
數字已經不如 InProcess 那樣破表的表現了...



最後來看一下 Process 隔離層級的做法。前面提到，跨越 Process 能使用的通訊方式，大部分都是繞到 I/O 的機制去處理了。不論是 pipe, stdio redir, network, share file 等等都算是 I/O 的領域。我這邊就用前面介紹過的 standard i/o redir 的機制來實作:

```csharp

    public class SingleProcessWorker : HelloWorkerBase
    {
        private Process _process = null;
        private TextReader _reader = null;
        private TextWriter _writer = null;

        public SingleProcessWorker()
        {
            this._process = Process.Start(new ProcessStartInfo()
            {
                FileName = @"D:\CodeWork\github.com\Andrew.ProcessPoolDemo\NetFxProcess\bin\Debug\NetFxProcess.exe",
                Arguments = "",
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                UseShellExecute = false
            });

            this._reader = this._process.StandardOutput;
            this._writer = this._process.StandardInput;
        }

        public override HelloTaskResult QueueTask(int size)
        {
            this._writer.WriteLine(size);
            return new HelloTaskResult(true)
            {
                ReturnValue = this._reader.ReadLine()
            };
        }

        public override void Stop()
        {
            this._writer.Close();
            this._process.WaitForExit();
        }
    }
```

主要的通訊機制，就是在 Worker 內啟動 NetFxProcess.exe, 同時重新導向這個 process 的 STDIN / STDOUT, 我寫入一行數字就代表傳遞參數過去，讀取一行字串就代表傳回執行結果。中間的等待與協調，就靠 I/O 的 blocking 來達成。

同時來看看 Process 另一端的 code :

```csharp

    class Program
    {
        static void Main(string[] args)
        {
            string line = null;

            while((line = Console.ReadLine()) != null)
            {
                int size = int.Parse(line);
                var result = (new HelloTask()).DoTask(size);
                Console.WriteLine(result);
            }

        }
    }

```

基本上就是把上面對於 STDIO 的傳輸定義，反過來寫而已。這邊就是讀取一行 STDIN 當作參數來呼叫 HelloTask, 然後把執行結果寫到 STDOUT 就結束了。不斷循環，直到 STDIN 被關閉為止。

這次來看看 Process 的版本執行效率: `SingleProcessWorker: 41493.77593361 tasks/sec`

結果有點令人意外，資料量不大的情況下，process 隔離層級的做法效能竟然還贏過 AppDomain ... 當然這並不是絕對的結果，不過也證明其中的落差不如我們想像的巨大。這次測試傳遞的都是很簡單的資料 (int, string)，接下來我們測試一下大型的物件看看...


### BLOB 參數傳遞

為了測試傳遞 BLOB，我擴充了 HelloTask:

```csharp

public class HelloTask : MarshalByRefObject
    {
        public string DoTask(int size) => null;
        public byte[] DoTask(byte[] buffer) => new byte[512];
    }

```

同樣的先讓他空轉，但是我把原本 DoTask 的參數改成 byte[] 了。我統一用傳入 1MB 資料，傳回 512Byte 資料為範本來測試。稍微改了一下測試程式 (這我就不列了)，值接看看測試結果:

```
FX Worker:
InProcessWorker: 40000 tasks/sec
SingleAppDomainWorker: 1949.31773879142 tasks/sec
SingleProcessWorker(FX): 36.6703337000367 tasks/sec
SingleProcessWorker(CORE): 69.2712662787476 tasks/sec

Core Worker:
InProcessWorker: 55555.555555555555 tasks/sec
SingleProcessWorker(FX): 38.74767513949163 tasks/sec
SingleProcessWorker(CORE): 118.73664212776063 tasks/sec
```

Process 透過 STDIO 傳輸，我刻意沒有直接用最有效率的 binary 格式，而是改用 base64, 因為實際狀況下我一定會碰到序列化的需求, 甚至是有需要透過 json 等等標準格式。我不想要在 POC 過度美化效能，要看出實際的差異才是我的目的啊，因此我選擇了這樣的實作方式。

傳輸資料的 size 被放大後，不同隔離層級造成的效能差距開始看的出來了。本來效能無敵到算不出來的 InProcess, 現在也掉到 51813 t/s, 這是對照組, 你可以把他想成執行測試基本的開銷。即使是同個 memory space 下的 AppDomain, 光是 Marshal 也讓效能從 51813 掉到 1512, 透過 Process 不斷的做 Base64 轉換, 效能更是掉到 37 ...

不過, 請先記下這個結果就好, 別急著下決定，因為這些方法其實各有優缺點。後面這段我要來談一下我為何要做這些 POC 背後的原因。




# 回到主題: 為何你需要隔離環境?






# 挑戰: Orchestration















<!--more-->


# 問題背景, 可靠度 與 效能的挑戰

## 隔離行為不良的程式碼

## 重設執行環境

## 容許不同版本的 assembly

## 容許不同版本的 runtime / tech stack



# 解決方案比較, In-Process, AppDomain 與 Process


## Benchmark - Activate

## Benchmark - Task Execution

## Solution Consideration


# 通訊方式

## Named / Anonymous Pipe

## STDIO redir


# Next: Thread Pool 的進化, Process Pool

## 設計概念

## 實作

## Benchmark


# 結論

