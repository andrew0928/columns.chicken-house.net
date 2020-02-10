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

Thread pool, 主要是妥善的安排 threads 來處理 workload, 而須要把 thread 升級成 process, 不外乎是要有更好的隔離 (isolation) 層級。同機器的 process 之間有完全獨立的 memory space, 你就能有更大的彈性裝載不同的開發技術。若你都已經將 workload 抽象化到 process 的層級, 你要擴大到分散式就是很容易的一件事了。不過這篇我不會擴大到跨機器的實作，這部分我只會點到為止，留一些關鍵字讓讀者們自己去推敲。

這次我需要設計一個通用的 task 管理機制, 讓各個開發團隊能將自己開發的 task 掛上這機制來運行。因為這樣可能有跨越多個團隊程式碼彼此衝突的風險存在，因此是否能有效做好隔離就是成功的關鍵之一。另一個關鍵則是在隔離的前題下，是否還能有效的兼顧效能? 這兩者之間能取得的最佳平衡點，就是我這篇文章要探討的目標。

大概交代一下問題背景，就可以直接開始了。我會探討 C# 各種隔離的技術 (thread, app domain, process) 開始, 一步一步推進到我最終的版本: process pool, 想看最後的程式碼可以直接跳到最後一段就好，想知道我如何無中生有的進行設計與決策過程，那請按照順序往下看。第一步分我會先搞清楚，C# 能用的各種 isolation 機制的特性及優缺點，若你有研究過 cloud native 的設計思維, 12 factors app 就把 process 當作其中一個關鍵的設計因素；第二部分則是來探討這些 isolation 的機制該如何搭配編排 (orchestration) 的做法，來達到整體產出 (throughput) 最大化的目的。

其實這兩個目的 (isolation / orchestration), 乍看之下也都跟使用 container 的目的相符合, 最後結論的地方我也會說明一下適用的時機, 當你的需求規模大到某個程度後, 你更應該考量用成熟的機制 (例如: container + k8s), 當規模化的機制無法 100% 滿足你的前題下, 你才應該局部的用自行開發的方式, 補足你需要的那個環節即可。


<!--more-->


# 挑戰: Isolation

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

跑出來的結果，由於跑的太快，C# 直接給我顯示無限大 XDDD, 其實真的去追究差異倍數意義也不大，我就不去追了。大家只要知道這個版本跑很快就好...


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

這個版本跑出來的結果: `6250 run/sec`


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

這版本跑出來的結果: `423.7288 run/sec`


### Process

這個版本，我直接把 Main() 編譯成獨立的 .exe, 然後透過 Process 物件來啟動獨立的程序，測試執行 .exe 的速度。這邊的結果頗令我意外，因為我用模一樣的 code, 甚至用一樣的 .NET Standard 編譯出來的 binary code 來寫關鍵部分, 只是最後用兩個不同的專案來編譯而已。結果編譯成 .NET Framework 跟 .NET Core 跑出來的結果有很大的落差。先來看 code (都一樣的 code, 只有執行檔的路徑不一樣):


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

.NET Fx 4.7.2 測試結果: `11.8807 run/sec`
.NET Core 3.1 測試結果: `0.8990 run/sec`

我說這也差距太大了... 不過沒關係，這只是環境的啟動速度比較。實際執行狀況還有很多變數...

### 小結

把結果列在一起看一下吧! 主程式是用 .NET Framework 開發的，因為不用 .NET Fx 我就無法使用 AppDomain 了:

|Freq\Mode    |InProcess|Thread|AppDomain|Process(.NET Fx)|Process(.NET Core)|
|-------------|---------|------|---------|----------------|------------------|
|單位: run/sec|∞|6250|423.7288|11.8807|0.8990|



(圖表)




看起來落差很大啊! 不過我不急著解讀這個測試結果。先把數據留著，後面再一起看吧! 不過看到同樣的 code, 用 .NET Fx / Core 的差距竟然這麼明顯，我就交叉測試了一下，把主程式也用 .NET Core 測了一遍。不過 .NET Core 不支援 AppDomain, 因此測試項目 AppDomain 會從缺。我直接把兩份測試結果列在同一個表格:

|Freq\Mode    |InProcess|Thread|AppDomain|Process(.NET Fx)|Process(.NET Core)|
|-------------|---------|------|---------|----------------|------------------|
|主程式: .NET Fx|∞|6250|423.7288|11.8807|0.8990|
|主程式: .NET Core|∞|8333.3333|無法測試|36.8596|0.9434|



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

這段 code 唯一的目的，就是造成一些合理的負載而已。我先配置了 16MB 的 buffer, 打算用這方式對 Heap 造成一些壓力；用亂數填入這 16MB 的記憶體空間，然後用 SHA512 的演算法計算 hash .. 這些動作打算對 CPU 造成一些壓力；往後所有的效能測試，都會以計算一秒能夠執行這個 task 幾次為參考依據。留意一下，這段 code 雖然 source code 一致, 不過有可能會在不同的 runtime 下執行；我在過程中就不小心踩到這個地雷 (後面會說明)，害我一直以為我的實驗數據不對勁...

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

|Freq\Mode        |InProcess|Thread     |AppDomain|Process(.NET Fx)|Process(.NET Core)|
|-----------------|---------|-----------|---------|----------------|------------------|
|主程式: .NET Fx  |0.011593  |0.011588   |0.011591 |0.013087        |0.06129           |
|主程式: .NET Core|0.03821   |0.03848    |--       |0.01309         |0.06144           |

看起來，這段 code 本身光是編譯成 .NET Fx / Core, 執行速度就有差距了，不過不同情況下的差距也不一樣。同樣的這些測試結果先不做評論，最後再來一起探討。




## Benchmark: 不同環境的 Task 參數傳遞效率

接下來開始的 code 就要認真面對了，前面都是簡單測完 code 我就砍了 (啥? XDD)。接下來，我要開始模擬真正的執行狀況，我希望 Task 能夠如同本地端的 lib 一樣容易的呼叫，需要傳遞參數過去，也需要傳遞結果回來。我期望主控端建立好環境後，可以傳遞 task 需要的參數過去，然後等待執行結果回來。除了參數根結果的傳遞之外，我需要 task 所有執行過程都被限制在安全的隔離環境內。

測試模式跟剛才差不多，不過因應這個測試需求，我改了一些 code ... 






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

