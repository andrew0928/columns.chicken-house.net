---
layout: post
title: "架構面試題: 非同步任務的處理機制 - Process Pool"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
- "系列文章: 架構面試題"
tags: ["microservice", "系列文章", "架構師", "POC", "ASYNC"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2020-02-09-process-pool/logo.png
---

![](/wp-content/images/2020-02-09-process-pool/logo.png)

好久沒寫微服務系列的文章了，這篇算是 Message Queue 的進階版本，如果你有越來越多的任務需要 Message Queue 後端的 Worker 來處理，後端 Worker 的架構其實是個很有意思的架構思考練習題。會想解決這個議題: Task Management, 需求有點類似 serverless, 我希望有個 pool 能很快的消化掉我丟進去的 task ...。其實我需要的架構就類似 message queue + serverless 就能符合了，但是有些因素, 我得認真評估自行建置最關鍵的那一塊該怎麼做。不過這篇我沒打算把主題擴的那麼大，我就專注在 Process Pool 上面了。

本來打算先講我打算如何解決問題，再來講實作的，不過架構題的決策，往往就是需求、架構跟實作的平衡啊，不先交代一下基本的實作技術，有點講不下去 XDD，我決定先花點篇幅說明程式碼隔離機制 (Isolation) 的架構選擇，再來講應用考量，最後說明 Process Pool 的實作。我分三個段落來說明最終 Process Pool 這個構想是怎麼誕生的:

1. **挑戰: Isolation 的機制研究**:  
了解與比較各種執行環境隔離的技術 (InProcess / AppDomain / Process), 以及如何橫跨隔離環境進行有效率的通訊 ([IPC](https://zh.wikipedia.org/wiki/%E8%A1%8C%E7%A8%8B%E9%96%93%E9%80%9A%E8%A8%8A))  
  
1. **為何需要建立隔離環境**:  
交代我工作場合面臨的需求與挑戰，Container + Orchestration / Serverless 無法滿足的需求  
  
1. **挑戰: Process Pool 的設計與開發**  
在技術與平台的選擇與平衡, 如何設計與開發 Process Pool  

在這過程中，其時用了很多我過去文章個別提過的好幾種技巧，算是個終極的綜合應用篇吧! 最遠可以追溯到 10 年前那系列 [Thread Pool 設計與實作](/categories/#%E7%B3%BB%E5%88%97%E6%96%87%E7%AB%A0:%20Thread%20Pool%20%E5%AF%A6%E4%BD%9C)的相關文章。只是這篇的應用，把 "Thread" Pool 的觀念，擴大到 "Process" Pool 了。現在的技術，Process 層級的隔離期時有更多的工具可以運用了，例如 Container 就是一例；所以過程中我也花了不少時間在拿捏，站在巨人的肩膀上 vs 重新發明輪子 的取捨；對這部分有興趣的讀者們，可以直接跳到第二段。


<!--more-->




<!-- 

葉配: 繼續寫下去前先補一些我自己的心得, 如果你也想挑戰這樣的工作內容, 請跟我聯絡 XD

> 最近花了點時間，重新讀了一次我自己寫的文章，自從我開始把主軸轉移到 container 及 microservices 之後, 我發現我越來越能針對特定主題深入探討了。其實這跟工作內容的改變也有直接的關聯。過去我的角色是一路從 Tech Lead 一路做到 CTO, 我需要替團隊做好技術決策與開發管理，寫出來的文章大都偏向實作會碰到的問題。近幾年開始轉型擔任架構師，開始對於架構設計的 "WHY" 有更深刻的體認了，我開始有機會能從 "WHY" 到 "HOW" 整個完整的過程來探討特定的技術主題，才會有這些內容的分享。台灣的軟體產業，很可惜的是很難有這樣的空間經歷這些過程，有的公司沒有發揮的舞台，有的公司老闆不重視，有的公司苦於找不到合適的人才來主導...


還記得我多年前寫的一系列多執行緒的文章嗎? 其中有一篇，我花了 100 行左右的 C# code, 實作出一個完整功能的 thread pool, 能動態調節適合的 threads 數量來處理工作負載。這次，我要把這同樣的機制，擴大成分散式版本的 process pool, 而其中相關的設計決策，我則搭配了我在過程中做的研究與 POC 來說明。不過，這次我要面對的需求，其實遠遠比 Task Management 還要複雜啊! 過去在開發 Thread Pool, 主要面對的是效能問題, 要炸出極端的效能, 就必須面對生產者跟消費者的高度協調才能辦到，重點都在執行緒的控制。不過，這次搬上實際應用的場景要面對分散式架構的考量，使用 (開發 task) 對象還是全部研發團隊 (100+ 人) 必須共同運作的通用平台，就多了非常多維運與可靠度上的考量。

我就針對我最在意的一點: 那麼多人寫的 code 都要丟在一起排程執行與管理, 一定會面臨執行環境隔離的議題, 也會面臨分散式的考量。這是一體兩面，要有適當的隔離，某段 code 失敗造成的影響才能被控制住不會影響其他任務；適度的隔離間接帶來的好處，就是更容易變成分散式的機制，達到橫向擴展 (scale out) 的要求。這些主題，其時我過去的文章都有個別談到了，這篇我就集中在探討 "isolation" 隔離這件事身上。


Thread pool, 主要是妥善的安排 threads 來處理 workload, 而須要把 thread 升級成 process, 不外乎是要有更好的隔離 (isolation) 層級。同機器的 process 之間有完全獨立的 memory space, 你就能有更大的彈性裝載不同的開發技術。若你都已經將 workload 抽象化到 process 的層級, 你要擴大到分散式就是很容易的一件事了。不過這篇我不會擴大到跨機器的實作，這部分我只會點到為止，留一些關鍵字讓讀者們自己去推敲。

這次我需要設計一個通用的 task 管理機制, 讓各個開發團隊能將自己開發的 task 掛上這機制來運行。因為這樣可能有跨越多個團隊程式碼彼此衝突的風險存在，因此是否能有效做好隔離就是成功的關鍵之一。另一個關鍵則是在隔離的前題下，是否還能有效的兼顧效能? 這兩者之間能取得的最佳平衡點，就是我這篇文章要探討的目標。

大概交代一下問題背景，就可以直接開始了。我會探討 C# 各種隔離的技術 (thread, app domain, process) 開始, 一步一步推進到我最終的版本: process pool, 想看最後的程式碼可以直接跳到最後一段就好，想知道我如何無中生有的進行設計與決策過程，那請按照順序往下看。第一步分我會先搞清楚，C# 能用的各種 isolation 機制的特性及優缺點，若你有研究過 cloud native 的設計思維, 12 factors app 就把 process 當作其中一個關鍵的設計因素；第二部分則是來探討這些 isolation 的機制該如何搭配編排 (orchestration) 的做法，來達到整體產出 (throughput) 最大化的目的。

其實這兩個目的 (isolation / orchestration), 乍看之下也都跟使用 container 的目的相符合, 最後結論的地方我也會說明一下適用的時機, 當你的需求規模大到某個程度後, 你更應該考量用成熟的機制 (例如: container + k8s), 當規模化的機制無法 100% 滿足你的前題下, 你才應該局部的用自行開發的方式, 補足你需要的那個環節即可。 -->

{% include series-2016-microservice.md %}



# 挑戰: Isolation 的機制研究

進入應用之前，要先對一些基礎的隔離方式做些了解，就先來牛刀小試一下好了。有點手感 & 先了解每種技術的表現在哪個數量級，你才會知道後面要如何取捨以及設計。我有跨平台的需求 (需要跨越 windows / linux 這些作業系統, 同時開發技術也需要跨越 .net frameowkr / .net core / node js), 而且主力是 C#, 因此我還是以目前最大宗的 C# / .net framework 為起點好了，後面的選擇也至少要能兼顧這需求為前提。

根據隔離的層級不同，我大概區分這幾種可行的做法:


1. **In-Process** (Direct Call):  
完全正常的呼叫方式，就只有語言層級的隔離機制而已 (例如: public / private, local variable ... etc) 不多做說明。  

1. **Thread**:  
執行緒之間除了執行的順序各自獨立之外, 幾乎沒有任何隔離的措施了。從系統的角度來說，多個執行緒之間只有 call stack 是閣獨立的, 意思是只有 [PC](https://zh.wikipedia.org/wiki/%E7%A8%8B%E5%BC%8F%E8%A8%88%E6%95%B8%E5%99%A8) (program counter, 組語裡面指向目前執行位置的指標)、local variable 這類資料是被隔離的；但是除了平行處理之外，這個可當作完全沒有隔離機制的對照組。  

1. **[GenericHost](https://docs.microsoft.com/en-us/aspnet/core/fundamentals/host/generic-host?view=aspnetcore-3.1)**:  
從 .net core 2.0 開始被引入的機制。每個 Host 控制背後的 BackgroundService 的生命週期, 每個 Host 也擁有自己獨立的 [IoC](https://zh.wikipedia.org/wiki/%E6%8E%A7%E5%88%B6%E5%8F%8D%E8%BD%AC) container (Inversion of Control, 控制反轉)。在 .net core 的世界, Microsoft 大量運用 [DI](https://docs.microsoft.com/en-us/archive/msdn-magazine/2016/june/essential-net-dependency-injection-with-net-core) (Dependency Injection) 的技術, 因此 Host 你可以把他想像成有完全獨立的 DI 機制。不同 Host 之間注入的 Singleton 物件是彼此獨立的。  
嚴格的來說這不算強制的隔離機制，但是在 DI 的技術越用越廣泛的今日, 這是個有潛力的技術。不過沒有透過 DI 處理的部分，隔離層級就跟 InProcess / Thread 沒兩樣了。不過現階段這技術還沒辦法解決我的需求 T_T, 因此僅止於介紹, 這次不參與評估。  

1. **[AppDomain](https://docs.microsoft.com/en-us/dotnet/api/system.appdomain?view=netframework-4.8)**:  
從 .NET Framework 時代就開始支援的技術，直接由 .NET CLR (Common Language Runtime) 提供，相較於 process 來說更為輕量化的隔離技術。AppDomain 提供了互相獨立不被干擾的 space, 透過 .NET API 的保證, .NET 的物件是無法跨越 AppDomain 的邊界的。只要是 "managed" 的部分都在管控的範圍內。除非你用了 unsafe 或是 unmanaged code, 否則所有你用 C# 寫的 code 都可以被 AppDomain 所保護。不過這些優點是有代價的，只支援 .NET CLR, 只有 .NET Framework 的程式才被支援，這項技術在 .NET core 的時代也正式被廢掉了。官方的替代技術嘛... 很抱歉沒有了, 官方文件直接說明未來用 Process 跟 Container (這邊指的是 Docker 這種容器化技術, 不是前面提到的 IoC container) 取代，可以做到同樣的需求。因此這篇主要就是要看看 Process 的能耐...。

1. **[Process](https://en.wikipedia.org/wiki/Process_(computing))**:  
直接由作業系統 (OS: operation system) 提供的機制。OS 在載入任何程式支前, 都會先在 OS 內建立一個新的處理程序 (process), 有獨立的啟動點，也有完全隔離的 memory space, 隨後才在這個 process 內載入及執行你指定的程式 (executable)。由於這是由 OS 提供的機制，因此只要被該 OS 支援的程式都可以支援，不限定開發技術或是開發語言。雖然使用的方式有點不同，但是基本上 container 也是屬於這個層級。不過這次探討的主要是以開發為主，我就不特別再介紹 container 的做法了。實作上有需要的朋友，你可以把 Docker Container 擺在這層級來考量即可。  

1. **[Hypervisor](https://en.wikipedia.org/wiki/Hypervisor)**:  
由硬體虛擬化提供的機制。一套支援虛擬化的硬體設備，搭配 hypervisor 的抽象層，可以在這基礎之上模擬成獨立的多個硬體設備，分別在這上面載入 OS ，進一步執行程式。這比起 Process 來說有更安全的隔離層級。不過通常再開發的階段，我都把 Hypervisor 隔離的環境直接當作 VM (virtual machine) 看待了。對於大部分的開發者來說，實體機器跟虛擬機器在開發上沒有太多的不同，這技術一樣我也不特別討論了，我直接歸類在分散式的環境下討論。真的有需要這技術的朋友門，把你的 application 包裝成 container, 在 infrastructure 的選擇下，已經有特定平台，可以替你為每個 container 準備專屬的 hypervisor 虛擬化的環境了。Windows container 內建 Hypervisor Container (只要加上 --isolation hyperv 參數)，Linux 也有對應的 (抱歉我記不得名字了) 可以使用。


基本觀念介紹完一輪後，後面的 POC 我就只針對 inprocess / threads , application domain, process 三者來比較就好了，可以透過 infrastructure 解決的架構我暫時略過，因為面對的對象是 developer, 不是 SRE, 因此我專注在 coding 上需要了解對應做法的技術為主。我會特別評比 coding 的做法與限制，測試則是物理效能的 benchmark 為主；請繼續看下去...




## Benchmark: 隔離環境的啟動速率

真正開始測試執行速率前，我先準備了一個啥事都不做的 ```Main()```, 來代表整個隔離環境對應到 code 的完整 life cycle. 這個 ```Main()``` 只要呼叫了就立馬 return, 用他來測試隔離環境 "空轉" 的效能 (這測試結果也代表該架構的效能天花板):

```csharp

class Program
{
    static void Main(string[] args)
    {
    }
}

```

接著，我用 .NET Framework 4.7.2 起了一個 Console App 的 project, 分別用了這五種方式，建立執行環境 (如果需要的話)，然後呼叫這個 ```Main()``` 一次，離開。如此重複 100 次，計算每秒可以跑幾次。第一次先來看看每個測試的 code。

### InProcess Mode

直接呼叫, 沒有任何隔離層級的設計；當作對照組來看待:


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

這次每個 ```Main()``` 的呼叫，都用一個執行緒來包裝他。這麼做有些用意，後面再解釋，我先測試再說:


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

這版本特別一點，我直接用 .NET Framework 的特殊機制 AppDomain 來實作。先看 code:

```csharp

for (int i = 0; i < total_domain_cycle_count; i++)
{
    var d = AppDomain.CreateDomain("demo");
    var r = d.ExecuteAssemblyByName(typeof(HelloWorld).Assembly.FullName);
    AppDomain.Unload(d);
}

```

補充說明一下，你如果寫過 Console App 應該都知道, .NET 編譯器需要你指定進入點 (就是上面講的 ```Main(...)``` )。專案範本都會幫你產生一個 ```Program.cs``` 就是這用意:

```csharp
class Program
{
    static void Main(string[] args)
    {
        // ... 略
    }
}
```

這進入點的資訊，其實會記載在 assembly 的 metadata 內，AppDomain 啟動時就會去找這資訊，因此在上述的 code 你沒有看到直接呼叫 ```HelloWorldTask.Program.Main(null);``` 的原因就在這邊。如果你有多個 ```Main()``` 的話就必須自己動點手腳了。

這版本跑出來的結果: 

```
Benchmark (AppDomain Mode):           333.333333333333 run / sec
```



### Process

這個版本，我直接把 ```Main()``` 編譯成獨立的 .exe (Console App), 然後透過 Process 物件來啟動獨立的程序，測試執行 .exe 的速度。這邊的結果頗令我意外，因為我用模一樣的 code, 甚至用一樣的 .NET Standard 編譯出來的 binary code 來寫關鍵部分, 只是最後用兩個不同的專案來編譯而已。結果編譯成 .NET Framework 跟 .NET Core 跑出來的結果有很大的落差。多跑幾次或是重新開機都會有些變化，受環境影響的因素不少。我跑了好幾次挑有代表性的貼結果就好。先來看 code (都一樣的 code, 只有執行檔的路徑不一樣):


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

把結果列在一起看一下吧! 上面測試的主程式是用 .NET Framework 開發的，因為不用 .NET Fx 我就無法使用 AppDomain 了。為了對比同樣的 code (主程式) 用 .NET Fx / Core 的差異，同樣的測試我也另外用 .NET Core 測了一次，測試結果我列在底下的表格:

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
Benchmark (AppDomain Mode):           (Bypass)
Benchmark (.NET Fx Process Mode):     31.25 run / sec
Benchmark (.NET Core Process Mode):   23.25581395348837 run / sec
```

|Freq\Mode        |InProcess|Thread|AppDomain|Process (.NET Fx)|Process (.NET Core)|
|-----------------|---------|------|---------|----------------|------------------|
|主程式: .NET Fx  |∞        |∞      |333.3333 |11.7647         |12.6582|
|主程式: .NET Core|∞        |∞      |無法測試  |31.2500         |23.2558|






## Benchmark: 不同環境的 Task 執行效率

前面第一個 Part 我測試了整個 "環境" 啟動的效率。接下來要測一下在這環境下，執行 task 的效率 (也包括 code 寫法的說明) 差異。我寫了一個很簡單的 ```HelloTask```, 來做為比較的標準依據:

```csharp

public class HelloTask : MarshalByRefObject
{
    public static bool state_must_be_true = true;

#if NULL_LOAD
    public string DoTask(int size) => null;
    public string DoTask(byte[] buffer) => "";
#else

    private static Random _rnd = new Random();
    private static HashAlgorithm _ha = HashAlgorithm.Create("SHA512");

    public string DoTask(int bufferSize)
    {
        byte[] buffer = new byte[bufferSize];
        return this.DoTask(buffer);
    }

    public string DoTask(byte[] buffer)
    {
        if (state_must_be_true == false) throw new InvalidProgramException();

        _rnd.NextBytes(buffer);
        return Convert.ToBase64String(_ha.ComputeHash(buffer));
    }
#endif
}

```    

這段 code 唯一的目的，就是造成一些合理的負載而以，我挑了會占用 RAM 跟 CPU 的案例: 計算 SHA512 hash 來當作案例。用法很簡單，就是呼叫 ```DoTask()```, 然後把 buffer 傳進去，計算完 hash 後用 base64 字串傳回來。我設計了兩套參數，一個是只傳 ```int bufferSize```, 另一個是由 host 端直接準備好記憶體區塊內容，用 ```byte[] buffer``` 傳遞過來。兩者之間主要差異在傳遞參數的大小 ( 4 bytes vs 1M bytes )。因為，在跨越隔離環境下要呼叫另一端的 code, 通常參數的傳遞都是要花力氣處理的。

同樣的，為了觀察傳遞參數的影響，我用了條件式編譯，來切換空轉的版本。如果 compiler 定義了 ```#define NULL_LOAD``` 的話，就會啟動空轉的版本，所有 ```DoTask()``` 呼叫都是立刻 return, 可以觀察這些機制的效能天花板。這段 code 我直接用 .NET standard 2.0 的規範開發與編譯, 其他專案不論是 .NET framework 或是 .NET code, 都會共用同一個 binary code 來執行。接著，我也把``` Main()``` 的部分做了點調整。原本是立馬 return 的 code, 改成呼叫 100 次 ```HelloTask```:

```csharp

public static int Main(string[] args)
{
    for (int i = 1; i < 100; i++)
    {
        new HelloWorld().DoTask();
    }
    return 0;
}

```


然後，測試的主程式就不再跑 100 次重新建立環境的 code 了，這次我只執行一次隔離環境的建立。我的目的是想觀察，這 ```HelloTask``` 在不同環境下的執行速率有沒有影響。為了這個目的，我把主程式調整了一下:

```csharp

public static void WorkerMain(string mode, HelloWorkerBase[] workers)
{
    Stopwatch _timer = new Stopwatch();
    int count = 10000;
    int buffer_size = 1 * 1024; // 1kb

    Console.WriteLine($"Worker: {System.Reflection.Assembly.GetEntryAssembly().GetName().Name}, Mode: {mode}");
    foreach (var worker in workers)
    {
        _timer.Restart();
        for (int i = 0; i < count; i++)
        {
            HelloWorkerBase.HelloTaskResult result = null;

            if (mode == "VALUE")  result = worker.QueueTask(buffer_size);
            if (mode == "BASE64") result = worker.QueueTask(new byte[buffer_size]);
        }
        worker.Stop();
        Console.WriteLine($"{worker.GetType().Name.PadRight(30)}: {count * 1000.0 / _timer.ElapsedMilliseconds} tasks/sec");
    }
}

```

簡單的用個架構圖來表示，我想做的就是這樣的機制:

![](/wp-content/images/2020-02-09-process-pool/2020-02-16-21-57-06.png)

我需要有個隔離環境，來讓 ```HelloTask``` 安心的被執行，而主控端能夠適當的分配任務 (data) 給隔離環境下的 ```HelloTask``` 執行，並且傳回結果。

每種不同的隔離環境，都會有各自的 Worker 來實作。我定義了抽象類別來規範這個 Worker 的實作方式來方便測試。 ```HelloWorkerBase``` 以及每種隔離環境的實作方式，我在下個 Part 再各自說明。接下來開始的 code 就要認真面對了，我要開始模擬真正的執行狀況，我希望 Task 能夠如同本地端的 lib 一樣容易的呼叫，需要傳遞參數過去，也需要傳遞結果回來。我期望主控端建立好環境後，可以傳遞 task 需要的參數過去，然後等待執行結果回來。除了參數根結果的傳遞之外，我需要 task 所有執行過程都被限制在安全的隔離環境內。

不同的隔離方式，有不同的通訊技巧。我這邊把通訊的需求簡化成傳遞呼叫參數，跟傳回執行結果就好。基本上 InProcess / Thread 都在同一個 memory space 下，直接傳遞物件的 reference 就夠了。AppDomain 嚴格的說也是在同個 memory space (相同 process 的多個 AppDomain, 是共用 managed heap 的), 只是 heap 內的物件存取會被 AppDomain 管控。跨越 AppDomain 存取物件，必須透過 Marshal 的機制處理。至於 memory space 完全獨立的 process, 只能透過 OS 層級的機制了, 例如 pipe, network, share file / memory map file 等等都是可行的做法, 後面的 code 我就直接拿 standard I/O + pipe 來示範..

測試模式跟剛才差不多，不過因應這個測試需求，我改了一些 code ..., 為了鋪梗後面的延伸範例, 我先把 POC 架構一次到位。我用以前寫過的 [ThreadPool](/2007/12/17/threadpool-%E5%AF%A6%E4%BD%9C-3-autoresetevent-manualresetevent/) 當作範本，過去自己手動搞定 [ManualResetEvent](https://docs.microsoft.com/zh-tw/dotnet/api/system.threading.manualresetevent?view=netframework-4.8) 的部分，我這邊直接用 [BlockingCollection](https://docs.microsoft.com/zh-tw/dotnet/api/system.collections.concurrent.blockingcollection-1?view=netframework-4.8) 簡化了。所有的 POC 都從 ```HelloWorkerBase``` 衍生出來:

```csharp

public abstract class HelloWorkerBase
{
    public HelloWorkerBase()
    {
    }

    public abstract HelloTaskResult QueueTask(int size);
    public abstract HelloTaskResult QueueTask(byte[] buffer);

    public abstract void Stop();
    
    public class HelloTaskResult
    {
        public HelloTaskResult(bool waitState = false)
        {
            this.Wait = new ManualResetEventSlim(waitState);
        }
        public string ReturnValue;
        public readonly ManualResetEventSlim Wait;
    }

}

```


與前面提到的 Thread Pool 相比，我抽象化了各種 Worker 的實作，也簡化了他的泛用度，因此這邊的 Worker 只限定處理 ```HelloTask```, 但是我希望這些 HelloTask 將來能在各種不同隔離層級的要求下，有效率的處理 ```HelloTask```...。因此 POC 公開的介面就是 ```QueueTask()```, 我只傳遞執行 Task 必要的參數 (int size / byte[] buffer 二選一) 就夠了。為了精確控制 thread, 我選擇跳過 .NET 內建的 async / await 機制, 用簡單的 ```HelloTaskResult``` 來封裝執行結果。

如果資深一點的 developer, 應該會記得當年還沒有 async / await 時, .NET 怎麼處理這類問題的方法吧? [IAsyncResult](https://docs.microsoft.com/zh-tw/dotnet/standard/asynchronous-programming-patterns/calling-asynchronous-methods-using-iasyncresult) .. 我這邊就是做了一個簡化的版本: ```HelloTaskResult```, 來當作 ```QueueTask()``` 的傳回值。這設計允許你先拿到 Result, 然後在需要的時候再呼叫 ```HelloTaskResult.Wait.Wait()``` 來等待結果。整個 Worker 設計上應該要允許平行處理，直到 ```Worker.Stop()``` 被呼叫為止。呼叫 Stop() 會停止接受新的 ```QueueTask()``` 需求，同時 ```Stop()``` 會等待 (blocking) 到所有 Task 都完成為止才會 return 。

舉例來說，如果你要呼叫三個 ```HelloTask```, 並取得結果，正確的寫法應該是這樣:

```csharp

var worker = new MyDemoWorker();
for (int i = 0; i < 3; i++)
{
    var task = worker.QueueTask(1);
    task.Wait.Wait();
    Console.WriteLine(task.ReturnValue);
}
worker.Stop();

```


先從單純一點的測試開始吧。我先不去處理平行執行的部分，參數也先以最單純的 value 為主就好。我來測試看看，不重覆建立隔離環境的前提下，加上傳遞參數的效能測試。我啟用 ```NULL_LOAD``` 定義，把 ```HelloTask.DoTask()``` 的內容清空，我想先測試一下空轉時這個機制的效能極限:

不論你用哪一種 Worker 的實作來執行 ```HelloTask```, 我都用前面提到改寫後的 ```WorkerMan()``` 來測試效能。我會測試四種組合，一個維度是空轉 / 實際負載，另一個維度是基本參數傳遞 (int) 及大型資料傳遞 (byte[]: ~ 1MB)。切換測試方式會有微小的 code 調整，這些我也略過, 我只說明一次主程式結構就好，其他直接看測試數據。接下來就逐一來看各種隔離層級的程式碼，以及測試結果:



### InProcessWorker

接著先來看對照組 ```InProcessWorker```: 完全沒有做任何隔離環境，直接執行 ```HelloTask``` ...

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

測試空轉 10000 次 ```HelloTask``` 呼叫的結果: `InProcessWorker: ∞ tasks/sec`
一如預期，一樣跑到破表...



### SingleAppDomainWorker

接下來來看看 AppDomain 的部分。作法跟 ```InProcessWorker``` 雷同，主要的差異在於，跨越 AppDomain 的物件傳遞，必須透過 .NET Marshal 的機制來處理才行。所幸 Microsoft 幫我們把大部分的細節都處理掉了，我只需要讓 ```HelloTask``` 繼承 ```MarshalByRefObject```, 基本上就搞定了:

```csharp

public class HelloTask : MarshalByRefObject
{
    // 略 ...
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

關鍵在於這段: ```CreateInstanceAndUnwrap(...)```, 透過 AppDomain 的這個方法，你要求指定的 AppDomain 替你建立物件，然後 Unwrap (背後需要經過 ```ObjectHandle``` 處理), 經過一連串的步驟把遠在另一個 AppDomain 的物件穿越回你現在的 AppDomain... 拿到 Unwrap 後的物件你就能直接呼叫他了，其他背後的細節，.NET 會通通替你處理掉...，除此之外，這段 code 其時跟 ```InProcessWorker``` 沒有什麼不同。有時這麼方便背後的代價是很可怕的啊，短短一行 code 背後包含這麼多系統面的知識, 搞不清楚狀況的工程師可能誤用了多年都還不知道自己錯過了什麼... 

來看看執行結果: `SingleAppDomainWorker: 26666.6666666667 tasks/sec`
數字已經不如 InProcess 那樣破表的表現了...



### SingleProcessWorker

最後來看一下 Process 隔離層級的做法。由於作業系統 (OS: Operating System) 對 Process 有先天的隔離與限制，因此跨越 Process 能使用的通訊方式，大部分都是繞到全系統通用的 I/O 的機制去處理了。不論是 pipe, stdio redir, network, share file 等等都算是 I/O 的領域。我這邊就用前面介紹過的 standard i/o redir 的機制來實作:

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

主要的通訊機制，就是在 Worker 內啟動 ```NetFxProcess.exe```, 同時重新導向這個 process 的 STDIN / STDOUT, 我寫入一行數字到 STDIN 就代表傳遞參數過去；我從 STDOUT 讀取一行字串就代表傳回執行結果；我 close STDIN 就代表我不再需要這個 process 了，close STDIN 可以通知該 process 不會再有後面的參數了。中間的等待與協調，就靠 I/O 的 blocking 來達成。

同時來看看被啟動的 Process 另一端的 code :

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

基本上就是把上面對於 STDIO 的傳輸定義，反過來寫而已。這邊就是讀取一行 STDIN 當作參數來呼叫 ```HelloTask```, 然後把執行結果寫到 STDOUT 就結束了。不斷循環，直到 STDIN 被關閉為止。不過這是基本參數傳遞的版本，另外大量參數傳遞的版本大同小異，只是多用了序列化 / 轉換成 Base64 的方式處理參數傳遞而以，完整的版本:


```csharp

public static void ProcessMain(string[] args)
{
    string line = null;
    string mode = "VALUE";

    if (args != null & args.Length > 0) mode = args[0];      // transfer mode: VALUE | BASE64

    switch (mode)
    {
        case "VALUE":
            while ((line = Console.ReadLine()) != null)
            {
                int size = int.Parse(line);
                Console.WriteLine((new HelloTask()).DoTask(size));
            }
            break;

        //case "BINARY":
        //    break;

        case "BASE64":
            while ((line = Console.ReadLine()) != null)
            {
                byte[] buffer = Convert.FromBase64String(line);
                Console.WriteLine((new HelloTask()).DoTask(buffer));
            }
            break;
    }
}

```

這次來看看 Process 的版本執行效率: `SingleProcessWorker: 41493.77593361 tasks/sec`

結果有點令人意外，資料量不大的情況下，process 隔離層級的做法效能竟然還贏過 AppDomain ... 當然這並不是絕對的結果，不過也證明其中的落差不如我們想像的巨大。這次測試傳遞的都是很簡單的資料 (int, string)，接下來我們測試一下大型的物件看看...



## Isolation 測試結果總評


接下來就是有點煩人的綜合測式了。程式碼跟做法前面都交代過，我就直接看結果。我測試了兩個維度，各兩種做法的組合。測試結果如下:


執行平台: .NET Framework
參數模式: VALUE (基本數值)
執行內容: 正常負載

```text
Worker: NetFxWorker, Mode: VALUE
InProcessWorker               : 19011.4068441065 tasks/sec
SingleAppDomainWorker         : 10593.2203389831 tasks/sec
SingleProcessWorker           : 13440.8602150538 tasks/sec
SingleProcessWorker           : 27173.9130434783 tasks/sec
```


執行平台: .NET Core
參數模式: VALUE (基本數值)
執行內容: 正常負載

```text
Worker: NetCoreWorker, Mode: VALUE
InProcessWorker               : 84745.7627118644 tasks/sec
SingleProcessWorker           : 12919.896640826873 tasks/sec
SingleProcessWorker           : 29239.766081871345 tasks/sec
```


執行平台: .NET Framework
參數模式: BASE (大量資料)
執行內容: 正常負載

```text
Worker: NetFxWorker, Mode: BLOB
InProcessWorker               : 19120.4588910134 tasks/sec
SingleAppDomainWorker         : 10822.5108225108 tasks/sec
SingleProcessWorker           : 9285.05106778087 tasks/sec
SingleProcessWorker           : 21321.9616204691 tasks/sec
```

執行平台: .NET Core
參數模式: BASE (大量資料)
執行內容: 正常負載

```text
Worker: NetCoreWorker, Mode: BLOB
InProcessWorker               : 85470.08547008547 tasks/sec
SingleProcessWorker           : 9861.932938856016 tasks/sec
SingleProcessWorker           : 25575.447570332482 tasks/sec
```



執行平台: .NET Framework
參數模式: VALUE (基本數值)
執行內容: 無負載

```text
Worker: NetFxWorker, Mode: VALUE
InProcessWorker               : ∞ tasks/sec
SingleAppDomainWorker         : 26881.7204301075 tasks/sec
SingleProcessWorker           : 51546.3917525773 tasks/sec
SingleProcessWorker           : 57471.2643678161 tasks/sec
```

執行平台: .NET Core
參數模式: VALUE (基本數值)
執行內容: 無負載

```text
Worker: NetCoreWorker, Mode: VALUE
InProcessWorker               : 10000000 tasks/sec
SingleProcessWorker           : 43668.12227074236 tasks/sec
SingleProcessWorker           : 52631.57894736842 tasks/sec
```


執行平台: .NET Framework
參數模式: BASE (大量資料)
執行內容: 無負載

```text
Worker: NetFxWorker, Mode: BLOB
InProcessWorker               : 5000000 tasks/sec
SingleAppDomainWorker         : 23419.2037470726 tasks/sec
SingleProcessWorker           : 19193.8579654511 tasks/sec
SingleProcessWorker           : 32051.2820512821 tasks/sec
```


執行平台: .NET Core
參數模式: BASE (大量資料)
執行內容: 無負載

```text
Worker: NetCoreWorker, Mode: BLOB
InProcessWorker               : 2500000 tasks/sec
SingleProcessWorker           : 21739.130434782608 tasks/sec
SingleProcessWorker           : 37037.03703703704 tasks/sec
```

這樣不大好看，我整理成表格；我把有無負載分成兩個獨立的表格來看:



無負載:

|主程式 + 參數模式 \ 隔離方式        |InProcess |AppDomain  |Process (.NET Fx)   |Process .NET Core) |
|----------------------------------|----------|-----------|-------------------|-------------------|
|.NET Fx   + VALUE                 |∞         |26881.7204 |51546.3918         |57471.2644         |
|.NET Core + VALUE                 |10000000  |無法測試    |43668.1223         |52631.5789         |
|.NET Fx   + BLOB                  |5000000   |23419.2037 |19193.8580         |32051.2821         |
|.NET Core + BLOB                  |2500000   |無法測試    |21739.1304         |37037.0370         |



有負載 (buffer: 1KB):

|主程式 + 參數模式 \ 隔離方式        |InProcess     |AppDomain  |Process (.NET Fx)   |Process (.NET Core) |
|----------------------------------|--------------|-----------|-------------------|-------------------|
|.NET Fx   + VALUE                 |19011.4068    |10593.2203 |13440.8602         |27173.9130         |
|.NET Core + VALUE                 |84745.7627    |無法測試    |12919.8966         |29239.7661         |
|.NET Fx   + BLOB                  |19120.4589    |10822.5108 |9285.0511          |21321.9616         |
|.NET Core + BLOB                  |85470.0855    |無法測試    |9861.9329          |25575.4476         |


這表格應該要這麼解讀，基本上無負載的部分，InProcess 的數據可以直接忽略了，你只要知道他很快就夠了。因為測式的精確度不夠高，測式的數量也不高 (太高我的電腦要跑完所有測式要等很久啊)。這是拿來當對照組的，我實際上不可能去用他，讓大家大約知道數量級上的差距即可。

這些測式有點難歸納結論啊，要考慮的變因 (維度) 太多，我試著從我想知道的幾個結論回頭說明我觀察的測試結果:



### 主程式 (管控端) 開發平台的選擇: 推薦 .NET Core

測試做完，老實說最令我跌破眼鏡的就是這組數據。我把上面的 32 項測試結果都匯到 Excel, 過濾出 .NET Fx 主程式；有負載；BASE64 傳輸模式的測試結果。令我傻眼的是: 透過 Process 層級隔離的，理論上應該是最慢的啊... 怎麼反過頭來超車，比 InProcess 還要快? 這其中一定有甚麼誤會...。

![](/wp-content/images/2020-02-09-process-pool/2020-02-16-18-29-55.png)

我還花了不少時間看我的 code 有沒有弄錯，最後真相大白，原因是:

```
 .NET Core 的 SHA512 計算效能遠高於 .NET Fx 的版本... 
```

我忽略了 Microsoft 的 .NET Fx BCL / Runtime 已經有好幾年沒有大幅改版了, 近幾年來的資源都投注在 .NET Core 身上。光是記憶體存取的優化 [Span](https://docs.microsoft.com/zh-tw/archive/msdn-magazine/2018/january/csharp-all-about-span-exploring-a-new-net-mainstay) ，應該就有巨幅的影響了 (例如 .NET Core 3.1 的 Json [效能](https://michaelscodingspot.com/the-battle-of-c-to-json-serializers-in-net-core-3/) 就突飛猛進)。不相信? 從上圖的 Process(.NET Fx) 跟 Process(.NET Core) 兩條數據來對比就知道了，差了 230% 啊...

再來做個比較，通通一樣的條件，只是主程式換成 .NET Core, 來看看圖表:

![](/wp-content/images/2020-02-09-process-pool/2020-02-16-18-39-08.png)

數字果然會說話，這次純粹通通都是 .NET Core 來較勁，數據就合理了。InProcess 的效能遙遙領先 Process(.NET Core) 達 330% .. 神奇的是，一模一樣的 Process (.NET Fx / Core ), 只是透過不同的主程式來啟動，竟然效能也有差異... Process(.NET Fx) 的版本因為主程式換成 .NET Core, 效能就提升了 6.2% ...  而 Process(.NET Core) 表現更搶眼，提升了 19.95% ...

這些我沒有再深入挖掘，不過根據經驗推論，主要改善應該來自 .NET Core 本身跟 OS 的最佳化做得更好吧，尤其在 I/O 層面 (例如新的 [Async Stream](https://www.infoq.com/articles/Async-Streams/), [IAsyncEnumerable](https://dotnetcoretutorials.com/2019/01/09/iasyncenumerable-in-c-8/))..

記憶體的效率，加上 I/O 效率的改善，這次測試是我完全意料之外的結果。你還在猶豫要不要用 .NET Core 的話, 基本上可以不用考慮了。我現在終於可以理解，Microsoft 為何在 .NET Core 直接放棄 AppDomain 這樣的技術了。從數字上來看，"感覺" 架構上比較理想的 AppDomain, 完全被 Process + .NET Core 打趴在地上啊...


### 負載 (工作端) 開發平台的選擇: 推薦 .NET Core

基本上這也沒什麼好選擇了，做完這次測試，你現在開發的 code, 毫無懸念直接轉往 .NET Core 吧! 如果你跟我一樣，還有些離不開 .NET Fx 的原因的話，至少把你的 code 改成 .NET Standard .. (這次範例 HelloTask 就是 .NET Standard 2.0), 如果再不行, 就做好準備轉移吧! 一個好方法是善用條件式編譯, 讓你能用 **同一份** source code, 編譯出完整功能的 .NET Fx 版本, 同時也能編譯出只支援部分功能的 .NET Standard / Core 版本。有了這樣的規劃，剩下的交給 CI / CD, 你就開始有個基礎能夠逐步的升級轉移。

同樣這些資料，我再用不同角度來評斷一下:

![](/wp-content/images/2020-02-09-process-pool/2020-02-16-19-04-12.png)

我列出所有無負載；BASE64 傳輸的數據出來看，我想知道空轉的情況下，到底整體的架構帶來的影響有多大。

同樣是 .NET Fx , 比起 Process, AppDomain 的效能好上 22.02 %, 不過這代價是你必須綁死在 .NET Fx 身上，因為他在 .NET Core 已經沒有替代品了。這代價不小，你同時得綁定主程式端跟工作端。丟掉 AppDomain, 你的選擇就更寬廣了，如同前一個評論一樣，當你有選擇機會時，優先挑選 .NET Core。如果你期望有最大的彈性，第一時間先把你的工作端 code 從 AppDomain 改成 Process 吧! 也許這樣你暫時會損失 22% 的效能，但是你開始有能力獨立改版主控端了。如果你轉移完成，主控端用 Core, 工作端用 Fx, 跟原本都用 Fx + AppDomain 相比, 效能一來一往, 只掉了 7.73 %, 但是你換來更好的架構，還有更寬闊的升級空間。拋開 AppDomain 你也開始有能力承擔更龐大的規模，Scalability 的上限也直接往上衝 (這個後半段再來討論)。

### 參數傳遞方式的選擇: 推薦 BLOB

這又是另一個有趣的題目，先來看看數據，這次我過濾了 無負載；只看 Process(.NET Core) 隔離方式:

![](/wp-content/images/2020-02-09-process-pool/2020-02-16-19-15-09.png)

工作端基本上不用選了，我只看 Process(.NET Core) 這項就好。有 OS 的隔離，基本上我就把他當作同一回事了，我專注在前面一層主程式管控端的選擇。我唯一搞不清楚的是，最佳組合竟然是出現在 .NET Fx -> (VALUE) -> .NET Core, 比起 .NET Core -> (VALUE) -> .NET Core 好上 15.56 %... 我只能把他當作也許 .NET Fx 有些局部的最佳化做得比較好吧!

不過即使如此，整體考量我仍然會優先選擇 .NET Core 主控端 + BLOB .. 因為這次實測的參數我沒有弄得很大，才 1KB 而已，如果我傳輸的是 URL，有些較長的網址早就超過了... 這組合占優勢的地方，對我並不是那麼的關鍵。

具體來說，這兩種傳輸方式的差異可能會是什麼? 很多任務通常會搭配 DB，我做這測試的目的是想看看，透過 I/O 傳輸參數，跟透過早已存在的高效率 storage 來比的差異有多大。也許我的系統早就有備妥要傳遞的資訊了，也許存在 database, 也許存在 NoSQL 或是 Redis ... 這時我也許有機會選擇只傳遞 Primary Key, 來取代傳輸完整的資料。

不過空轉的情況下，落差也沒有很大，即使落差最大的組合，差距也只有 79.31% 而已。負載再加上去差距就更小了。這時工作管理傳遞參數的選擇，我會選擇直接傳遞，即使需要序列化較大型的物件。



## 下一步: Process Pool

這邊我就先把這一段 Isolation 的研究告一段落。看了這麼多種組合 (.NET Fx / Core)，傳遞參數的策略 (Value / BLOB), 隔離技術的選擇 (AppDomain / Process) 都做了一番測是，大體上都搞清楚每種組合的特性了。看起來最適合的隔離機制是 Process, 而主控端與工作端按照需求，盡可能的挑選效能最好的 .NET Core。中間跨越 Process 的通訊可以採用常見的 I/O (例如 STDIO, pipe 等)。

Process 跟 Thread 一樣，建立都是有很高昂的成本的，維護一個 Process 要比維護一個 Thread 代價還要更高，要花費更多的記憶體，啟動也需要花費更多時間。因此，下一步是我打算用 Process 來隔離主控端跟工作端，同時打造一個像 Thread Pool 這樣的機制，拿來管理跨越 Process 邊界執行 Task 用的 Process Pool。





# 回到主題: 為何你需要隔離環境?

(未完成，敬請期待)


* [Porting to .NET Core](https://devblogs.microsoft.com/dotnet/porting-to-net-core/)

> App Domains
> Why was it discontinued? AppDomains require runtime support and are generally quite expensive. While still implemented by CoreCLR, it’s not available in .NET Native and we don’t plan on adding this capability there.
> 
> What should I use instead? AppDomains were used for different purposes. For code isolation, we recommend processes and/or containers. For dynamic loading of assemblies, we recommend the new AssemblyLoadContext class.


# 挑戰: Orchestration

(未完成，敬請期待)












<!-- 


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
 -->
