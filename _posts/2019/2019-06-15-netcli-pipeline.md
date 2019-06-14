---
layout: post
title: "設計案例: 命令列工具開發技巧 - 串流處理 & PIPELINE"
categories:
tags: []
published: true
comments: true
redirect_from:
logo: 
---

最近工作上碰到個案子，其中需要開發 CLI (Command Line Interface) 的工具。其實這本來是件不起眼的小事，不過如果你平常不常用 shell script (其實我也不熟啊 @@), 或是其他 CLI tools 的話，要你決定 CLI 該怎麼被使用，應該一時間也不知道該怎麼辦吧! 這篇要來介紹一下 CLI 的設計技巧，如何透過 PIPELINE 串流(平行)處理大量資料。

我把主軸拉回 "串流資料" 的處理方式吧。會需要用到 CLI 不外乎幾個原因，例如:

1. 這個操作必須被自動化或是重複執行，寫成 CLI 才方便放在 shell script 執行。
1. 這個操作需要處理大量資料，或是需要長時間執行，不需要 GUI 介面的時候。
1. 需要跨語言開發，直接做成 CLI 方便跨異質開發環境呼叫。
1. 發展自己的 CLI toolset, 讓 shell script 能夠組合使用。

為了搞定這幾件事情，你的 CLI 可不是 "能動" 就好了。你提供的操作方式 (參數，輸入輸出的設計) 會直接影響你寫的 CLI 用起來順不順手。我這篇就特別針對 CLI 之間的資料交換，還有大量資料交換的串流處理方式介紹一下好了。我相信很多後端的工程師都碰過這種場景，只是過去你可能沒留意到就用別的方式處理掉了。看完這篇文章，可以仔細想想，重新來一次的話是否有更好的設計方式。

<!--more-->



# 概念: 串流處理的基本概念

我很愛找那種 code 寫起來沒幾行，但是背後很多觀念的文章。這篇要講的又是一樣的東西，我先在這個段落把幾個重要觀念先交代一下。

"串流處理" 這件事不算新觀念了，簡單的說，就是把一大串的資料，切成小塊，每次處理塊，就能輸出一小塊的結果。由於不用等到所有資料 (input) 都備齊就可以持續處理及輸出結果 (output)，因此也能拿來處理各種源源不絕的資料來源，只要機制啟動，資料不斷的產生，就有結果不斷的輸出。串流處理技術的進步，最典型的應用就是影音直播，或是資料分析很常用的 streaming analystics。

串流處理，最大的效益就是低延遲，尤其是資料量越大時越明顯。舉例來說，如果你有 N 筆資料要處理，每筆需要處理 M 秒，批次處理的話你需要花費 N x M 的時間，而你必須在這些時間結束之後才會一口氣拿到所有的結果。串流處理則不同，每隔 M 筆就會輸出一筆結果給你，持續 N x M 秒你才會拿到所有的輸出。整體效率並沒有很大的差異，但是你拿到第一筆處理結果的時間則是固定的 O(1)，不會受資料大小的影響 O(N)。

再來看進階一點的案例: 如果你的處理過程有好幾個步驟 (例如: P1, P2, P3)，每個階段各需要花費的時間不同 (例如: M1, M2, M3)，則:

1. 批次處理需要花費 N x (M1 + M2 + M3) 的時間，一口氣拿到所有的結果。
2. 串流處理需要花費一樣的時間，但是經過 (M1 + M2 + M3) 秒之後就能拿到第一筆資料的結果。

這邊開始有另一種可能性了，也就是這篇我運用的另一個技巧: PIPELINE (管線)。試想一下，如果我用平行處理的技巧，第一筆資料要處理 P1 + P2 + P3 三個階段；當 P1 處理完第一筆資料之後，換 P2 接手了，這時 P1 空閒了下來，能不能同時間繼續處理第二筆資料的 P1 ??

如果你的 code 能做到這點，那麼來看一下管線處理的話要花費的時間: 經過 M1 + M2 + M3 秒，就可以開始拿到第一筆資料；總處理時間會變成 N x Max(M1, M2, M3) ...

文字描述很難想像，簡單畫成時間軸來比較就知道了。我把 批次(Batch)、串流(Stream)、管線(Pipeline) 三種處理方式我都畫成圖:


![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-03-12-36.png)
> 批次處理

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-03-13-05.png)
> 串流處理

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-03-13-20.png)
> 管線處理

其中，藍色的箭頭，代表第一筆資料完成的時間，橘色的箭頭代表最後一筆資料完成的時間。整個橘色的框框則是處理的邊界，框框結束才能拿到裡面的資料。

看得出差異了嗎? 你如果有能力精準的用 pipeline 的方式處理資料，加上不同階段之間的資源不會互相占用 (例如 CPU, DISK ... etc) 的話，你就能得到戲劇性的效能增長。

其實這類的探討，我以前寫過很多篇了。從當年投稿 RUN!PC，寫了十來篇探討平行處理的文章，就有講到生產線的處理模式，就是在講這個。另外在探討 C# async 處理的技巧，也有談到類似的問題。這邊我就不另外再重打一次，十年前的老文章了，有興趣的朋友們可以翻回去看:


1. [處理大型資料的技巧 – Async / Await](/2013/04/14/處理大型資料的技巧-async-await/), (2009/04/14)
1. [RUN!PC 精選文章 - 生產線模式的多執行緒應用](/2009/01/16/runpc-精選文章-生產線模式的多執行緒應用/), (2009/01/16)
1. [生產線模式的多執行緒應用](/2008/11/04/run-pc-2008-十一月號/), ([RUN! PC] 2008 十一月號, 2008/11/04)
1. [生產者 vs 消費者 - BlockQueue 實作](/2008/10/18/生產者-vs-消費者-blockqueue-實作/), (2008/10/18)
1. [MSDN Magazine 閱讀心得: Stream Pipeline](/2008/01/19/msdn-magazine-閱讀心得-stream-pipeline/), (2008/01/19)



# 在同一個 Console 內的處理技巧 (C# yield return, async / await)

別急著馬上就要開始寫 CLI ... 先掌握好幾個基本技巧再說吧! 我就用上面的例子，把他變成程式碼，先來 POC 看看你有沒有能力達到想像中的效果。我們先在單一一個 .NET Console App 內完成這整件事，稍後再來把它換成 CLI。

先來準備一下，模擬資料 (```DataModel```) 以及處理資料的程序 (```DataModelHelper```) 的 code:

```csharp

public class DataModel
{
    public string ID { get; set; }

    public int SerialNO { get; set; }

    public DataModelStageEnum Stage { get; set; } = DataModelStageEnum.INIT;

    public byte[] Buffer = null;
}

public enum DataModelStageEnum : int
{
    INIT,
    PHASE1_COMPLETE,
    PHASE2_COMPLETE,
    PHASE3_COMPLETE
}

```

我簡單用 ```class DataModel { ... }``` 來代表資料，其中的 ```Stage``` 代表狀態，分為 ```INIT```, ```PHASE1_COMPLETE```, ```PHASE2_COMPLETE```, ```PHASE3_COMPLETE``` 來代表處理狀態。

接著看一下 Phase 1 ~ 3 的處理程式碼:

```csharp

public static class DataModelHelper
{
    public static bool ProcessPhase1(DataModel data)
    {
        if (data == null || data.Stage != DataModelStageEnum.INIT) return false;

        Console.Error.WriteLine($"[P1][{DateTime.Now}] data({data.SerialNO}) start...");
        Thread.Sleep(1000);
        data.Stage = DataModelStageEnum.PHASE1_COMPLETE;
        Console.Error.WriteLine($"[P1][{DateTime.Now}] data({data.SerialNO}) end...");

        return true;
    }
    public static bool ProcessPhase2(DataModel data)
    {
        if (data == null || data.Stage != DataModelStageEnum.PHASE1_COMPLETE) return false;

        Console.Error.WriteLine($"[P2][{DateTime.Now}] data({data.SerialNO}) start...");
        Thread.Sleep(1500);
        data.Stage = DataModelStageEnum.PHASE2_COMPLETE;
        Console.Error.WriteLine($"[P2][{DateTime.Now}] data({data.SerialNO}) end...");

        return true;
    }
    public static bool ProcessPhase3(DataModel data)
    {
        if (data == null || data.Stage != DataModelStageEnum.PHASE2_COMPLETE) return false;

        Console.Error.WriteLine($"[P3][{DateTime.Now}] data({data.SerialNO}) start...");
        Thread.Sleep(2000);
        data.Stage = DataModelStageEnum.PHASE3_COMPLETE;
        Console.Error.WriteLine($"[P3][{DateTime.Now}] data({data.SerialNO}) end...");

        return true;
    }
}


```

其實也沒啥，就是檢查傳進來的物件狀態對不對，印出開始結束時間，同時 P1 ~ P3 分別延遲 1000ms, 1500ms, 2000ms, 代表不同的處理時間。


最後，是產生測試資料，我循序產生五筆測試資料:

```csharp

static IEnumerable<DataModel> GetModels()
{
    Random rnd = new Random();
    byte[] allocate(int size) 
    {
        byte[] buf = new byte[size];
        rnd.NextBytes(buf);
        return buf;
    };

    for (int seed = 1; seed <= 5; seed++)
    {
        yield return new DataModel()
        {
            ID = $"DATA-{Guid.NewGuid():N}",
            SerialNO = seed,
            Buffer = allocate(1024)
        };
    }
}


```


接下來就開始看各種不同的處理方式 DEMO 了。

## DEMO 1, 批次處理

不囉嗦，直接看 code, 應該不用解釋了:

```csharp

static void Demo1()
{
    DataModel[] models = GetModels().ToArray();

    foreach (var model in models)
    {
        DataModelHelper.ProcessPhase1(model);
    }

    foreach (var model in models)
    {
        DataModelHelper.ProcessPhase2(model);
    }

    foreach (var model in models)
    {
        DataModelHelper.ProcessPhase3(model);
    }
}

```

看一下輸出:

```text

[P1][2019/6/15 上午 04:07:21] data(1) start...
[P1][2019/6/15 上午 04:07:22] data(1) end...
[P1][2019/6/15 上午 04:07:22] data(2) start...
[P1][2019/6/15 上午 04:07:23] data(2) end...
[P1][2019/6/15 上午 04:07:23] data(3) start...
[P1][2019/6/15 上午 04:07:24] data(3) end...
[P1][2019/6/15 上午 04:07:24] data(4) start...
[P1][2019/6/15 上午 04:07:25] data(4) end...
[P1][2019/6/15 上午 04:07:25] data(5) start...
[P1][2019/6/15 上午 04:07:26] data(5) end...
[P2][2019/6/15 上午 04:07:26] data(1) start...
[P2][2019/6/15 上午 04:07:27] data(1) end...
[P2][2019/6/15 上午 04:07:27] data(2) start...
[P2][2019/6/15 上午 04:07:29] data(2) end...
[P2][2019/6/15 上午 04:07:29] data(3) start...
[P2][2019/6/15 上午 04:07:30] data(3) end...
[P2][2019/6/15 上午 04:07:30] data(4) start...
[P2][2019/6/15 上午 04:07:32] data(4) end...
[P2][2019/6/15 上午 04:07:32] data(5) start...
[P2][2019/6/15 上午 04:07:33] data(5) end...
[P3][2019/6/15 上午 04:07:33] data(1) start...
[P3][2019/6/15 上午 04:07:35] data(1) end...
[P3][2019/6/15 上午 04:07:35] data(2) start...
[P3][2019/6/15 上午 04:07:37] data(2) end...
[P3][2019/6/15 上午 04:07:37] data(3) start...
[P3][2019/6/15 上午 04:07:39] data(3) end...
[P3][2019/6/15 上午 04:07:39] data(4) start...
[P3][2019/6/15 上午 04:07:41] data(4) end...
[P3][2019/6/15 上午 04:07:41] data(5) start...
[P3][2019/6/15 上午 04:07:43] data(5) end...

C:\Program Files\dotnet\dotnet.exe (process 15828) exited with code 0.
Press any key to close this window . . .


```

簡單算一下執行的結果:
* 第一筆資料完成時間: 12 sec (04:07:21 ~ 04:07:33)
* 全部的資料完成時間: 22 sec (04:07:21 ~ 04:07:43)

這就當作對照組吧，沒啥好解釋的 code ... XDD


## DEMO 2, 串流處理

串流處理的版本，開始有點不一樣了。前面鋪的梗可以開始拿出來講了... 一樣先看 code 跟執行結果:

```csharp

static void Demo2()
{
    foreach(var model in GetModels())
    {
        DataModelHelper.ProcessPhase1(model);
        DataModelHelper.ProcessPhase2(model);
        DataModelHelper.ProcessPhase3(model);
    }
}

```

執行結果

```text

[P1][2019/6/15 上午 04:13:04] data(1) start...
[P1][2019/6/15 上午 04:13:05] data(1) end...
[P2][2019/6/15 上午 04:13:05] data(1) start...
[P2][2019/6/15 上午 04:13:07] data(1) end...
[P3][2019/6/15 上午 04:13:07] data(1) start...
[P3][2019/6/15 上午 04:13:09] data(1) end...
[P1][2019/6/15 上午 04:13:09] data(2) start...
[P1][2019/6/15 上午 04:13:10] data(2) end...
[P2][2019/6/15 上午 04:13:10] data(2) start...
[P2][2019/6/15 上午 04:13:11] data(2) end...
[P3][2019/6/15 上午 04:13:11] data(2) start...
[P3][2019/6/15 上午 04:13:13] data(2) end...
[P1][2019/6/15 上午 04:13:13] data(3) start...
[P1][2019/6/15 上午 04:13:14] data(3) end...
[P2][2019/6/15 上午 04:13:14] data(3) start...
[P2][2019/6/15 上午 04:13:16] data(3) end...
[P3][2019/6/15 上午 04:13:16] data(3) start...
[P3][2019/6/15 上午 04:13:18] data(3) end...
[P1][2019/6/15 上午 04:13:18] data(4) start...
[P1][2019/6/15 上午 04:13:19] data(4) end...
[P2][2019/6/15 上午 04:13:19] data(4) start...
[P2][2019/6/15 上午 04:13:20] data(4) end...
[P3][2019/6/15 上午 04:13:20] data(4) start...
[P3][2019/6/15 上午 04:13:22] data(4) end...
[P1][2019/6/15 上午 04:13:22] data(5) start...
[P1][2019/6/15 上午 04:13:23] data(5) end...
[P2][2019/6/15 上午 04:13:23] data(5) start...
[P2][2019/6/15 上午 04:13:25] data(5) end...
[P3][2019/6/15 上午 04:13:25] data(5) start...
[P3][2019/6/15 上午 04:13:27] data(5) end...

C:\Program Files\dotnet\dotnet.exe (process 1780) exited with code 0.
Press any key to close this window . . .

```

執行的結果:
* 第一筆資料完成時間: 5 sec (04:13:04 ~ 04:13:09)
* 全部的資料完成時間: 23 sec (04:13:04 ~ 04:13:27)

結果如預期，相信也不需要太多解釋了。不過這邊開始回頭看一下，這兩種做法，除了時間之外，其實還有隱藏的差異...。由於串流處理一次會把一筆資料的所有步驟從頭到尾處理完畢，因此不論你總共有幾筆資料要處理，任何瞬間的半成品一定只有一個。這個案例我的資料是擺在記憶體內，因此串流處理的做法我只需要花費固定 (一筆) 的記憶體空間而已。

這段 sample code 我只替每個 data 準備 1024 bytes 的 buffer 而已，如果我把它改成 2GB 會發生甚麼事?

我把產生測試資料的這段，把 allocate 的 size 從 1024 (1KB) 換成 1024 x 1024 x 1024 (1GB):

```csharp

static IEnumerable<DataModel> GetModels()
{
    Random rnd = new Random();
    byte[] allocate(int size) 
    {
        byte[] buf = new byte[size];
        rnd.NextBytes(buf);
        return buf;
    };

    for (int seed = 1; seed <= 5; seed++)
    {
        yield return new DataModel()
        {
            ID = $"DATA-{Guid.NewGuid():N}",
            SerialNO = seed,
            Buffer = allocate(1024 * 1024 * 1024)
        };
    }
}


```

改完後重新執行這兩個案例。這次我們不看 output, 我們開啟 performance profiler 來看看記憶體使用量:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-04-40-18.png)


為了避免以前踩過的地雷 (沒有填資料進去的記憶體，OS / CLR 可能會幫我最佳化延遲 allocale, 造成這測試根本沒作用 XDD)，因此配置出來的記憶體我都填亂數進去，執行速度比較慢。先來看看 Demo1 的數據:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-04-37-55.png)


可以看到記憶體一直飆上去，前面 45 sec 都在準備物件，配置了 5GB 記憶體，大約 45 sec 後才開始在執行程式。結束之後 5GB 記憶體都釋放出來了。過程中我就算按了 force GC 也沒有用，就是會吃這麼多記憶體。

留意一下，這裡測試資料才 5 筆... 如果是 5000 筆，你的 server 有 5000GB 的 RAM 可以用嗎? 應該馬上就 OOM (OutOfMemoryException) 了吧...




接著來看 Demo2:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-04-43-35.png)


過程可以看到記憶體仍然會往上飆，但是我再跑一次，這次我看到往上飆我就順手按一下 [Force GC] 看看:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-04-45-12.png)

上面有紅色的標記，就是 GC completed 的 mark, 可以看到 GC 是有效的，代表你的程式已經釋放物件了，只是 CLR 沒那麼勤勞沒有立刻回收而已。記憶體使用量大致上都維持再 1 ~ 2GB, 意思是過程中只需要處理中的物件被保留在記憶體內就好了，測試資料不論改成多少筆，測試結果都差不多。


"處理過程中需要占用的資源是固定的" 這是另一個串流處理的特色，如果你是 backend engineer 你必須要更了解這點。留意一下 Demo2 我特地用 foreach 直接取用測試資料，而 GetModels() 我也直接用 yield return 傳回，整個從資料產生到處理完畢的過程，通通都用串流模式，就能有這樣的效果。反觀 Demo1, 我故意 GetModels().ToArray() 轉成陣列一次傳回來，就變成了批次模式。

C# Yield Return 的使用技巧，我當年也寫過幾篇... (怎麼每次拿出來的文章都超過十年以上了? Orz)

* [C#: yield return, How It Work ?](/2008/09/18/c-yield-return-1-how-it-work/), (2008/09/18)




## DEMO 3, 管線處理

回頭看一下 Demo1 / Demo2 的程式碼結構... 很典型的，Demo1 以 PHASE 處理的結構為主，Demo2 則是以 DataModel 為主。兩種各有利弊，沒有好壞之分。想看看，如果 Demo1 的範例內，foreach loop 內的邏輯很複雜的話，哪一種比較好維護? Demo1 or Demo2?

這時，以單一職責原則來看，Demo1 的方式分工比較明確 (先不管記憶體問題)，程式碼結構比較利於處理複雜的 PHASE 內邏輯，是比較好維護的。我們有辦法同時兼顧兩種做法嗎?

有的，這就是 PIPELINE 的雛型了。我們來看看 DEMO 3:

```csharp

static void Demo3()
{

    foreach(var m in StreamProcessPhase3(StreamProcessPhase2(StreamProcessPhase1(GetModels()))));

}

public static IEnumerable<DataModel> StreamProcessPhase1(IEnumerable<DataModel> models)
{
    foreach (var model in models)
    {
        DataModelHelper.ProcessPhase1(model);
        yield return model;
    }
}
public static IEnumerable<DataModel> StreamProcessPhase2(IEnumerable<DataModel> models)
{
    foreach (var model in models)
    {
        DataModelHelper.ProcessPhase2(model);
        yield return model;
    }
}
public static IEnumerable<DataModel> StreamProcessPhase3(IEnumerable<DataModel> models)
{
    foreach (var model in models)
    {
        DataModelHelper.ProcessPhase3(model);
        yield return model;
    }
}

```

```text

[P1][2019/6/15 上午 05:31:35] data(1) start...
[P1][2019/6/15 上午 05:31:36] data(1) end...
[P2][2019/6/15 上午 05:31:36] data(1) start...
[P2][2019/6/15 上午 05:31:37] data(1) end...
[P3][2019/6/15 上午 05:31:37] data(1) start...
[P3][2019/6/15 上午 05:31:39] data(1) end...
[P1][2019/6/15 上午 05:31:39] data(2) start...
[P1][2019/6/15 上午 05:31:40] data(2) end...
[P2][2019/6/15 上午 05:31:40] data(2) start...
[P2][2019/6/15 上午 05:31:42] data(2) end...
[P3][2019/6/15 上午 05:31:42] data(2) start...
[P3][2019/6/15 上午 05:31:44] data(2) end...
[P1][2019/6/15 上午 05:31:44] data(3) start...
[P1][2019/6/15 上午 05:31:45] data(3) end...
[P2][2019/6/15 上午 05:31:45] data(3) start...
[P2][2019/6/15 上午 05:31:46] data(3) end...
[P3][2019/6/15 上午 05:31:46] data(3) start...
[P3][2019/6/15 上午 05:31:48] data(3) end...
[P1][2019/6/15 上午 05:31:48] data(4) start...
[P1][2019/6/15 上午 05:31:49] data(4) end...
[P2][2019/6/15 上午 05:31:49] data(4) start...
[P2][2019/6/15 上午 05:31:51] data(4) end...
[P3][2019/6/15 上午 05:31:51] data(4) start...
[P3][2019/6/15 上午 05:31:53] data(4) end...
[P1][2019/6/15 上午 05:31:53] data(5) start...
[P1][2019/6/15 上午 05:31:54] data(5) end...
[P2][2019/6/15 上午 05:31:54] data(5) start...
[P2][2019/6/15 上午 05:31:55] data(5) end...
[P3][2019/6/15 上午 05:31:55] data(5) start...
[P3][2019/6/15 上午 05:31:57] data(5) end...

C:\Program Files\dotnet\dotnet.exe (process 15672) exited with code 0.
Press any key to close this window . . .

```


執行的結果:
* 第一筆資料完成時間: 4 sec (05:31:35 ~ 05:31:39)
* 全部的資料完成時間: 22 sec (05:31:35 ~ 05:31:57)


我善用了 yield return 的結構，把三個 PHASE 的處理動作都隔開了，隔離在個別的 StreamProcessPhaseX(...) 內，這個 method 的 input / output 都是 IEnumerable<DataModel>, 然後就像接力賽一樣，一棒一棒交下去。串完之後，最外圍的主程式，單純用個不做事的 foreach loop 驅動整個引擎運轉，就跑出跟 Demo2 一樣的結果了 (如上)。

為了公平比較效能，這段測試一樣是以 buffer size = 1024 bytes 為主下去測試的。我們一樣補一個 1GB buffer 的測試，看看 memory usage:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-05-39-56.png)

有趣的來了。我一樣在測試過程中不斷的點 Force GC (可以從上面的 GC completed mark 看到我點了幾下)。這個版本跑出來的邏輯跟 Demo2 一樣，記憶體使用也維持平穩固定，但是固定的記憶體使用量卻比 demo2 多... 

主要的差異在於，我們包了三層的 IEnumerable<DataModel> , 同一瞬間不同的 IEnumerable<DataModel> 至少會保留 2 ~ 3 個物件，因此我按 GC 的時候，有些物件會晚一點才能被放掉，但是整體長期來看，仍然會維持固定的量，不會像 Demo1 隨總資料筆數增加而增加。

但是，這版本只是程式碼結構改善了而已啊，執行的時間沒有像最前面講概念的部分一樣，看的到執行效能大幅縮短的效果。因為除了流程改變之外，我們還缺了另一個很重要的因素: 非同步 (async)。我們接著看 Demo4...




## DEMO 4, 管線平行處理

變態燒腦的程式碼出現了... 要寫這種文章，精神不好的時候還真寫不下去... 先看 code 跟結果再說:


```csharp


        static void Demo4()
        {

            foreach (var m in StreamAsyncProcessPhase3(StreamAsyncProcessPhase2(StreamAsyncProcessPhase1(GetModels())))) ;

        }

        public static IEnumerable<DataModel> StreamAsyncProcessPhase1(IEnumerable<DataModel> models)
        {
            Task<DataModel> previous_result = null;
            foreach (var model in models)
            {
                if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
                previous_result = Task.Run<DataModel>(() => { DataModelHelper.ProcessPhase1(model); return model; });
            }
            if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
        }

        public static IEnumerable<DataModel> StreamAsyncProcessPhase2(IEnumerable<DataModel> models)
        {
            Task<DataModel> previous_result = null;
            foreach (var model in models)
            {
                if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
                previous_result = Task.Run<DataModel>(() => { DataModelHelper.ProcessPhase2(model); return model; });
            }
            if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
        }
        public static IEnumerable<DataModel> StreamAsyncProcessPhase3(IEnumerable<DataModel> models)
        {
            Task<DataModel> previous_result = null;
            foreach (var model in models)
            {
                if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
                previous_result = Task.Run<DataModel>(() => { DataModelHelper.ProcessPhase3(model); return model; });
            }
            if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
        }

```

執行結果:

```text
[P1][2019/6/15 上午 05:51:40] data(1) start...
[P1][2019/6/15 上午 05:51:41] data(1) end...
[P1][2019/6/15 上午 05:51:41] data(2) start...
[P2][2019/6/15 上午 05:51:41] data(1) start...
[P1][2019/6/15 上午 05:51:42] data(2) end...
[P2][2019/6/15 上午 05:51:43] data(1) end...
[P1][2019/6/15 上午 05:51:43] data(3) start...
[P2][2019/6/15 上午 05:51:43] data(2) start...
[P3][2019/6/15 上午 05:51:43] data(1) start...
[P1][2019/6/15 上午 05:51:44] data(3) end...
[P2][2019/6/15 上午 05:51:44] data(2) end...
[P3][2019/6/15 上午 05:51:45] data(1) end...
[P3][2019/6/15 上午 05:51:45] data(2) start...
[P2][2019/6/15 上午 05:51:45] data(3) start...
[P1][2019/6/15 上午 05:51:45] data(4) start...
[P1][2019/6/15 上午 05:51:46] data(4) end...
[P2][2019/6/15 上午 05:51:46] data(3) end...
[P3][2019/6/15 上午 05:51:47] data(2) end...
[P3][2019/6/15 上午 05:51:47] data(3) start...
[P2][2019/6/15 上午 05:51:47] data(4) start...
[P1][2019/6/15 上午 05:51:47] data(5) start...
[P1][2019/6/15 上午 05:51:48] data(5) end...
[P2][2019/6/15 上午 05:51:48] data(4) end...
[P3][2019/6/15 上午 05:51:49] data(3) end...
[P3][2019/6/15 上午 05:51:49] data(4) start...
[P2][2019/6/15 上午 05:51:49] data(5) start...
[P2][2019/6/15 上午 05:51:50] data(5) end...
[P3][2019/6/15 上午 05:51:51] data(4) end...
[P3][2019/6/15 上午 05:51:51] data(5) start...
[P3][2019/6/15 上午 05:51:53] data(5) end...

C:\Program Files\dotnet\dotnet.exe (process 20236) exited with code 0.
Press any key to close this window . . .

```

執行的結果:
* 第一筆資料完成時間: 5 sec (05:51:40 ~ 05:51:45)
* 全部的資料完成時間: 13 sec (05:51:40 ~ 05:51:53)



看到了嗎? 有兩個重要的差異，請留意看執行結果...

1. 全部完成的時間大幅縮短，前面幾個案例大約都在 22 sec 上下，現在變成 13 sec ...
1. 執行的順序開始有交錯的狀況發生了。每個 phase 的範圍內都是按照順序進行的，但是每個 phase 之間則是平行處理的。
1. 執行的順序開始有交錯的狀況發生了。每個 data 的處理順序一定是對的 (P1, P2, P3)，但是每個 data 之間則是平行處理的。


人的腦袋天生不適合思考平行處理的流程... 這邊要燒點腦... 來看看我們在 StreamAsyncProcessPhaseX() 裡面做了啥:

```csharp
        public static IEnumerable<DataModel> StreamAsyncProcessPhase1(IEnumerable<DataModel> models)
        {
            Task<DataModel> previous_result = null;
            foreach (var model in models)
            {
                if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
                previous_result = Task.Run<DataModel>(() => { DataModelHelper.ProcessPhase1(model); return model; });
            }
            if (previous_result != null) yield return previous_result.GetAwaiter().GetResult();
        }
```

結構跟前面的 DEMO3 一樣，但是差別在於真正呼叫 DataModelHelper.ProcessPhase1() 的時候，我改用 Task 包裝起來，用 Async 模式去執行。執行後我不管結果，把 task 放在 previous_result 等著待會 await，就先結束目前這圈 foreach loop, 讓 foreach 繼續拉下一筆資料進來。

但是，管線處理有個假設，就是同一個 PHASE，一次只能處理一筆啊，否則我就需要多倍的計算資源了... 因此 foreach 拉了下一筆之後，要等前一筆結束才能再交給 DataModelHelper.ProcessPhase1() 處理。因此多插了一段 previous_result.GetAwaiter().GetResult()。

因為我在每個階段都動了一樣的手腳，因此整個處理的流程，就再允許的限制下，部分的被平行化處理了。我一時手癢，把上面的 log 自己換成 excel, 用視覺化的方式來呈現:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-06-23-30.png)

左邊是 Log 的時間，上面的 P1 ~ P3 就是 Log 上的 P1 ~ P3, 每一筆資料都有開始結束，我用 1S / 1E 代表第一筆資料的每個階段啟始結束時間，把他標在正確的格子上。最後加點美工，把他框起來上色 (同樣顏色代表同一筆 data)，就變成這張圖了。

仔細看一下，你會發現這跟前面介紹 pipeline 我畫的示意圖是一樣的結果，代表這樣的程式碼真的在時序的處理上有如我們的預期。
這邊很容易想到腦袋打結 (Orz, 我也沒辦法)... 其實想不通也沒關係，可以直接放棄 XDD, 因為後面有簡單的替代方案...

再繼續之前，我一樣補一下記憶體使用的狀況:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-05-59-01.png)
(記憶體, 5)

因為這方式的平行化程度更高了，代表要保留的半成品也更多，因此記憶體使用量也變多了。由於我們才測五筆看不大出來記憶體使用量是否平穩，我改成 20 筆再測一次:

![](/wp-content/images/2019-06-15-netcli-pipeline/2019-06-15-06-01-31.png)
(記憶體, 50)

看來結果一樣維持平穩，只是平行處理的前提下，必須保留在記憶體內的資料比前面的 demo 更多而已。





# 分成不同的 CLI 處理技巧

我應該辦個投票嗎? 請告訴我你是否理解上面最後一個 DEMO4 ... (我自己都想到頭快炸了)。要寫出這樣的 code 要求有點高，我有沒有簡便一點的方式? 有的。接下來要介紹的就是用 CLI 來解。

不同的 CLI，先天就是不同的 process, 很多時候分成 **完全** 獨立的兩個 program, 平行處理的問題就可以交給 OS 跟 shell 去傷腦筋就好，這就是我這段要講的重點。我想藉著 shell 本身提供的 STDIO 轉向 (就是 PIPELINE)，搭配簡單的處理技巧，直接把 P1 ~ P3 從三個 method 拆成三個 console app, 然後再 shell script 裡面利用 PIPELINE 把三個 CLI 串起來，達成一樣的目的...

看到這裡黑人問號了嗎? 哈哈... 沒關係，一樣一步一步來 demo. 只是這次我的目標是把 P1 ~ P3 拆成 CLI_P1 ~ CLI_P3。




# 結論