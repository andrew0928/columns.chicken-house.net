---
layout: post
title: "[樂CODE] Microsoft 面試考題: 用 CPU utilization 畫出正弦波"
categories:

tags: [".NET","C#","作業系統","多執行緒","專欄","技術隨筆"]
published: true
comments: true
permalink: "/2016/03/12/cpu_sinewave/"
redirect_from:
wordpress_postid: 973
logo: /wp-content/images/2016-03-12-cpu_sinewave/logo.png
---

![](/wp-content/images/2016-03-12-cpu_sinewave/logo.png)

故事的開頭很簡單，起因就只是某個上了年紀的大叔，逛到別人的面試題目，發現答不出來就一頭鑽進去，輸不起的故事而已 XD

<!--more-->

每次看到 **"這是XXX(大公司)的面試題目"** 這種聳動的標題，我都覺得那只是噱頭而已...  直到某日亂逛靠北工程師，看到這則留言:


![](/wp-content/uploads/2016/03/img_56dee24543173.png)




# 什麼!!! Microsoft 面試考這個?


長年都抱著 Microsoft Solution 在研究的我，怎麼能錯過這個考驗? 想想這題目還蠻有趣的，於是一時手癢，就開了 Visual Studio 2015 動起手來... 中間的過程就省略了，其實程式沒幾行，控制 CPU 使用率的原理，還有三角函數搞得清楚就沒問題了。結果不到十分鐘，第一版就出來了，直接看結果:


![](/wp-content/uploads/2016/03/img_56dee4e3127bd.png)

這是 sin wave? @@, 用點想像力的話，結果是沒有錯啦，不過這也太難看了一點 T_T

好像做失敗的蛋糕，外在內在都沒有 @@，形狀勉強算是 sin 的波形啦，不過那個雜訊干擾也太多了吧.. 實在太糟糕，這版 source code 我就不貼出來了...



稍做一點改變，原本程式是在本機執行，為了避免其他背景程式的影響，也先暫時避開 8 core 不大好控制的因素，改開 1 core 的 VM 在裡面執行。OS 安裝 Windows 2012R2 server core, 用最精簡的安裝，最少的背景程序，將影響 CPU utilization 的因素降到最低。

改善過後的波形...:  

![](/wp-content/images/2016-03-12-cpu_sinewave/12512448_10204274956434167_8308402654463171370_n.jpg)


Orz, 這什麼鬼? 勉強比上一個好一些，還看的出來是個 sine wave 啦 =_=


於是仔細想下去，才發現... 這題目雖然不難，但是你要做得漂亮也不是那麼簡單... 好像當年在念訊號處理一樣，最難搞的就是類比訊號。要處理訊號並不難，難的是類比訊號要有完美的波形可不是件容易的事! 就跟這個題目一模一樣，寫得出來不稀奇，你的波形要漂亮才叫了不起。不服輸的脾氣來了，就一鼓作氣的改下去...




繼續下去前，先來說明一下基本的運作原理。其實程式的運作方式很簡單，就像微積分一樣，把圖形切成很系的不同時段，我只要控制在那個時段內的 CPU 使用率，在我想要的數值內就夠了。剩下只要隨著時間的變化，讓 CPU 的使用率隨著 sin(time) 來變化就夠了。先把正弦波調整一下，調整一下震幅大小，同時也把波形位移一下...，如下圖:

![](/wp-content/uploads/2016/03/img_56e2e918afcd9.png)


Orz, 好久沒算數學了, 不過這種題目就是要計算啊...```sin(x)``` 的值是從 1 ~ -1 之間變化，所以我做了位移 + 縮放，最後我真正要的函數是 ```f(x) = (sin x + 1) / 2```。我只要把時間按照指定的單位切割成小段 (我用的是 100ms), 然後把每一段的時間當作 x 帶入計算，就可以知道這段時間內我要把 CPU 使用率控制在多少 % ...

下一個問題就是 CPU 使用率控制的問題了。我的假設是 [busy waiting](https://zh.wikipedia.org/wiki/%E5%BF%99%E7%A2%8C%E7%AD%89%E5%BE%85) 的程式碼，會造成 CPU utilization 達到 100%, 剩下我只要控制 CPU utilization 達到 100% 的時間要維持多久就行了。舉例來說，若我讓 busy waiting loop 每 100ms 執行 50ms，那麼當下我就會得到 CPU utilization 為 50% 的圖形.. 如上圖，如果我控制每一區段時間長度是 100 ms, 那麼 ```(sin x + 1) / 2``` 若等於 70%, 那麼代表 busy 的部分需要執行 100ms x 70% = 70ms, 而剩下的 100ms x 30% = 30ms 則是進入 idle 的狀態。



這樣其實是沒錯啦，不過問題開始出現了:

1. busy waiting 只對1 cpu core 起作用，我的 PC 有 4core / 8threads..., busy waiting 只能到達 12.5% 的負載
1. 讓 CPU 忙碌的部份解決了，但是怎麼讓 CPU "很精確的" 空閒? 空閒的部分做任何事情，也都會影響到 CPU utilization..


突然發現，這些技巧其實都是過去研究 [多執行緒](/category/thread/)，還有 [作業系統](/category/os/) 碰到的問題啊，哈哈哈... 還好過去累積了不少這些知識，現在可以拿來現寶了 XD，第一個很簡單，我只要用 multi-threading 或是開個只配置 1 core 的 VM 就搞定了，跳過!


第二個問題就有趣了，事實上我有一堆方法讓 "程式" 休息一段時間。然而過去的知識告訴我，```Thread.Sleep()``` 精確度低，而且呼叫他會讓目前的執行緒進入 IDLE 狀態，等到下次 OS 喚醒他，對於時間有精確控制的需求時是不適用的。相對的應該用 SpinWait 這類別，他會搭配 HLT 的指令，進行忙碌等待 (busy waiting)，同時又能讓 CPU 的使用率保持很低的狀態...。怎麼看都應該選用 ```SpinWait``` 啊...

不過我還是爬了文，也做了點實驗，發現很多東西都有變化了 XD，首先，爬到 darkthread 的這篇: [KB-測試Thread.Sleep的精確度](http://blog.darkthread.net/blogs/darkthreadtw/archive/2007/03/24/657.aspx)，提到 ```Sleep()``` 的精確度很糟糕，糟到連 15ms 的精確度都達不到...

但是真的寫一段 CODE 來確認，反倒讓我跌破眼鏡... ```Sleep()``` 的精確度已經不是吳下阿蒙了，也許我的主機板比較威一點... 看來是很精確的。但是 ```Sleep()``` 的結果的卻是飄移的比較厲害，容易受到 OS 的影響而有變化。反觀 ```SpinWait.SpinUntil()```, 飄移的幅度較小，但是精確度也沒好到哪裡去，就是省掉 context switch 的不確定性而已... 附上執行結果及測試用的程式:


![](/wp-content/uploads/2016/03/img_56e385cf5a90e.png)


沒有背景的干擾情況下，分別用 ```Sleep()``` 及 ```SpinUntil()``` 分別 IDLE 10 ms 的結果:


![](/wp-content/uploads/2016/03/img_56e2ecf83bddb.png)

開了 10 threads 當作背景的干擾，分別用 ```Sleep()``` 及 ```SpinUntil()``` 分別 IDLE 10 ms 的結果


# 測試精確度用的程式碼:

```csharp
class Program
{
    static bool stop = false;

    static void Main(string[] args)
    {
        // noise: background threads
        {
            for (int i = 0; i < 10; i++)
            {
                Thread t = new Thread(Foo);
                t.Start();
            }
        }

        Stopwatch timer = new Stopwatch();
        TimeSpan idle = TimeSpan.FromMilliseconds(10);

        // test Thread.Sleep()
        for(int i = 0; i < 10; i++)
        {
            timer.Restart();
            Thread.Sleep(idle);
            Console.WriteLine("Sleep(10): take {0} ms", timer.ElapsedMilliseconds);
        }

        // test SpinWait.SpinUntil()
        for(int i = 0; i<10; i++)
        {
            timer.Restart();
            SpinWait.SpinUntil(() => { return false; }, idle);
            Console.WriteLine("SpinUntil(10): take {0} ms", timer.ElapsedMilliseconds);
        }

        stop = true;
    }

    static Random _rnd = new Random();
    static void Foo()
    {
        while (stop == false) ;
    }
}
```

從結果來看，在有背景程式 (noise) 的干擾下，在 10ms 這樣的 scale 下，兩者的精確度都沒有好到哪裡去。雖然 ```Sleep()``` 的誤差比較小，但是飄移的範圍較大，從 10ms ~ 31ms 都有。相較之下 ```SpinUntil()``` 就穩定的多，少掉 context switch 的不確定性，表現平均的多，大致落在 23ms ~ 26ms 之間。不過誤差比較大，我指定的時間是 10 ms 啊...

只能這樣推測了，不過還想不到什麼方法證實... ```SpinUntil()``` 主要是用 ```delegate``` 讓使用者傳入判斷式，.NET framework 不斷的執行這個 ```delegate```, 來判定是否要跳出? 而 time out 的設定只是這 "Busy Waiting" 機制的執行上限而已。簡單算了一下，10ms timeout 時間的設定下，delegate 其實已經被執行了 130 ~ 150 次不等。這應該是延遲的主因吧? 相較之下 ```Sleep()``` 應該單純的多，只要 OS 跟主機板的 timer 精確一點就能提高精確度了。



測到這邊，我只能說... 理論跟實際還是有差距的啊啊啊... 我不確定 .net framework 的內部實作有甚麼特別的考量，不過實驗出來的結果的卻跟我預期有點出入。我花了點時間，查了 Spin 的機制是怎麼設計的:



**Spin Wait**:

> 多執行續的控制手段中，常常會拿 SpinWait 來實作 busy waiting 的技巧。SpinWait 能夠達到 Busy waiting 的要求，同時又不會讓 CPU utilization 飆高。


先來看看系統底層怎麼實作 SpinWait( ) 吧.. 關鍵在於 infinite loop 內插入一段 HLT 指令。看一下 wikipedia 的說明:

> HLT (https://en.wikipedia.org/wiki/HLT)  
> Almost every reasonably modern processor [instruction set](https://en.wikipedia.org/wiki/Instruction_set) includes an instruction or sleep mode which halts the processor until more work needs to be done. In interrupt-driven processors, this instruction halts the CPU until an external interrupt is received. On most architectures, executing such an instruction allows the processor to significantly reduce its power usage and heat output, which is why it is commonly used instead of [busy waiting](https://en.wikipedia.org/wiki/Busy_waiting) for sleeping and idling.


不過，搞到插入組語也太累了吧，.NET Framework 已經幫我們包裝好這個需求了，只要直接用 SpinWait 這個 class 就夠了:  

[SpinWait Structure](https://msdn.microsoft.com/query/dev14.query?appId=Dev14IDEF1&l=EN-US&k=k(System.Threading.SpinWait);k(TargetFrameworkMoniker-.NETFramework,Version%3Dv4.6.1);k(DevLang-csharp)&rd=true)  


> **SpinWait** encapsulates common spinning logic. On single-processor machines, yields are always used instead of busy waits, and on computers with Intel processors employing Hyper-Threading technology, it helps to prevent hardware thread starvation. SpinWait encapsulates a good mixture of spinning and true yielding.


研究到這裡，我決定做個規模大一點的實驗... 除了基本的 Sleep( ) 及 SpinUntil( ) 兩種做法之外，我另外弄了兩種改良的作法，嘗試修正原作法的弱點:

Advanced Sleep( ): 改用 busy waiting 的做法，用 while( !isTimeout ) Thread.Sleep(0); 的做法折衷處理。


```csharp
// test advanced Thread.Sleep()
stat.Reset();
for (int i = 0; i < testrun_count; i++)
{
    timer.Restart();
    while (timer.Elapsed < idle) Thread.Sleep(0);
    temp = timer.Elapsed;
    Console.WriteLine("- Advanced Sleep(): take {0} ms", temp.TotalMilliseconds);
}
```

Advanced SpinUntil( ): 不用原本內建的 Timeout 機制，改用 callback 的機制同時控制 Timeout: SpinWait.SpinUntil(()=>{return isTimeout;}) 替代。


```csharp
// test advanced SpinWait.SpinUntil()
stat.Reset();
for (int i = 0; i < testrun_count; i++)
{
    timer.Restart();
    SpinWait.SpinUntil(() => { return timer.Elapsed > idle; });
    temp = timer.Elapsed;
    Console.WriteLine("- Advanced SpinUntil(): take {0} ms", temp.TotalMilliseconds);
}
```



完整程式碼就不多貼了，文章最底下有附上 GitHub 連結，請自行採用。我直接跑了 noise thread 0 ~ 10 的結果出來。我分別針對不同方法的 "精密度" 及 "準確度" 來探討。這兩者有啥不同? 可以參考 Wiki 的 [說明](https://zh.wikipedia.org/wiki/%E6%BA%96%E7%A2%BA%E8%88%87%E7%B2%BE%E5%AF%86)。

![](/wp-content/uploads/2016/03/img_56e82e4177266.png)


先來看準確度吧! 我拿平均值跟理想值來比較，用這個來當作準確度的指標。下圖的 X 軸代表背景的干擾，就是我測試程式內 noise thread 的數量。Y軸代表每種方法各執行 50 次，測到的平均值。圖中Y軸 100 的那條虛線，就是我預期的結果，也是完美方法應該得到的曲線位置。越接近虛線代表越完美。

![](/wp-content/uploads/2016/03/img_56e39ce8bab6d.png)

我的 CPU 是 4 core / 8 threads, 所以可以看到 thread 在 7 的時候，準確度就明顯的開始受影響了。系統預設的 SpinUntil( ) 明顯的有誤差，但是在後面高負載的情況下反而表現最好，看來理論的基礎還是有用的，只不過在我需要的範圍內不見得是最佳的選擇...

我的情況下就是到 8 threads, 在這前提下我修正過的 Adv_SpinUntil 方法看來最理想，比起其他做法來說，有最佳的準確度表現。其他方法誤差太大，準確度的問題會影響最後跑出來的正弦波漂不漂亮... 這四種方法，在 8 noise threads 的情況下，表現依序是:

1. Adv_Spin
1. Adv_Sleep
1. Spin
1. Sleep

另外一個 "精密度" 又要怎麼看? 我拿 50 次測試結果的標準差，來當作 "精密度" 的指標，越低代表結果越穩定可靠，不會有暴衝的問題。直接來看圖:

![](/wp-content/uploads/2016/03/img_56e39f73d83e3.png)

這張圖的結果也類似，在我期望的範圍內，也是 Advanced SpinUntil( ) 的表現最好，依序是:

1. Adv_Spin
1. Spin
1. Adv_Sleep
1. Sleep

經過綜合考慮之後，最終我還是選用 Advanced SpinUntil 的機制來控制時間。一來行為表現比較可靠可預測，飄移的狀況較低。二來就架構上他是較合適的，有理論基礎。加上看到 [Darkthread 的文章](http://blog.darkthread.net/blogs/darkthreadtw/archive/2007/03/24/657.aspx) ，Sleep( ) 的精確度會跟硬體有高度相關，很依賴硬體(主機板) 的設計，因此我還是選用架構上較可靠的方案優先，後續的程式碼都改用 Spin 的機制來設計。



最後，就是盡可能的降低程式本身的誤差造成的干擾，因此我必須盡可能的排除這些因素。這些考量都是一班寫 CODE 時不會留意到的...。CPU 除了 IDLE 之外，其他任何動作都會造成 LOADING，你的程式做了越多額外的動作，越有可能影響 CPU utiization，這就是這個題目考驗的重點之一。感覺好像以前物理學的 [測不準原理](http://wiki.mbalib.com/zh-tw/%E6%B5%B7%E6%A3%AE%E5%A0%A1%E4%B8%8D%E7%A1%AE%E5%AE%9A%E6%80%A7%E5%8E%9F%E7%90%86) 一樣 XD，你沒有辦法在不影響粒子的位置前提下，精確測量到粒子的速度，反之亦然。因此你沒辦法同時精準的測到速度與位置這兩個資訊... 現在也是依樣啊，我為了產生正弦波寫了越多部必要的 CODE，波形受到的干擾就越多...

為了盡一切可能的排除所有來自自身程式碼的干擾，因此我要先確保 IDLE 的部分能執行足夠的時間。所以我調整了程式的執行順序，以求達到最高的精確度:

1. 盡可能地把所有的運算，在初始化的階段就處理掉。複雜的數學運算 (如 sin), 我先抽出來在 init 階段先算好，後面只要用速度最快的查表法 (time complexity: O(1))
1. 確保 IDLE 的部分能空出足夠的時間，其餘任何額外的運算，都把它歸在 BUSY 的那部分
1. BUSY 的部分扣除其他的運算用掉的時間，剩餘部分繼續用 Busy Waiting ( while(true); ) 來填滿。


OK，講了這麼多廢話，開始來看看修正過的結果吧。果然努力是看的到結果的，這次的波形就漂亮多了:

![](/wp-content/uploads/2016/03/img_56dee7228dd76.png)


來看看經過多次調教後的 source code:

```csharp
/// <summary>
/// 產生對照表，每個時段對應的附載數值。
/// </summary>
/// <param name="period">週期，圖形多久循環一次 (ms)?</param>
/// <param name="unit">每個時段的單位長度 (ms)</param>
/// <returns></returns>
public static long[] GetDataFromSineWave(long period, long unit)
{
    long steps = period / unit;
    long[] data = new long[steps];

    for (int s = 0; s < steps; s++)
    {
        //long degree = s * 360 / steps
        data[s] = (long)(unit - (Math.Sin(Math.PI * s * 360 / steps / 180.0) / 2 + 0.5) * unit);
    }

    return data;
}

/// <summary>
/// 按照對照表的數據，將圖形用 CPU utilization 繪製出來
/// </summary>
public static void DrawBitmap()
{
    long unit = 100; // ms
    long period = 60 * 1000; // msec, full image time period

    // get drawing data
    long[] data = GetDataFromBitmap(period, unit);
    //long[] data = GetDataFromSineWave(period, unit);

    Stopwatch timer = new Stopwatch();
    timer.Restart();
    while (true)
    {
        long step = (timer.ElapsedMilliseconds / unit) % (period / unit);
        long offset = (long)(timer.ElapsedMilliseconds % unit);
        long v = data[step];
        long idle_until = timer.ElapsedMilliseconds - offset + v;
        long busy_until = timer.ElapsedMilliseconds - offset + unit;

        // idle part
        SpinWait.SpinUntil(() => { return (timer.ElapsedMilliseconds > idle_until); });

        // busy part
        while (timer.ElapsedMilliseconds < busy_until) ;
    }
}
```

其實這個程式改過好幾版了，原本是沒有用查表法來加速 sin x 的計算的... 既然花了一番功夫，改成查表法之後，那代表... 我只要改變對照表的內容，就可以畫出任意圖形了不是嗎? 果然人是不會滿足的，基本需求完成後就開始想搞怪了...

程式改一改，產生對照表的來源不再是三角函數，改成由 ascii art 產生的 char map 當作來源。我用字串的陣列，在 source code 裡畫了一些設計圖，想不到啥好點子，就拿快要上映的 batman + superman 當例子吧，來個 batman:


```csharp
public static string[] bitmap = new string[]
{
    @"              XXXX          X      X          XXXX              ",
    @"             X   X          XX    XX          X   X             ",
    @"            X    X         X  XXXX  X         X    X            ",
    @"           X      XXXX     X        X     XXXX      X           ",
    @"          X           XXXXX          XXXXX           X          ",
    @"         X                                            X         ",
    @"        X                                              X        ",
    @"       X                                                X       ",
    @"      X                                                  X      ",
    @"     X                                                    X     "
};

public static long[] GetDataFromBitmap(long period, long unit)
{
    int max_x = bitmap[0].Length;
    int max_y = bitmap.Length;
    long steps = period / unit;

    long[] data = new long[steps];

    for (int s = 0; s < steps; s++)
    {
        int x = (int)(s * max_x / steps);
        int value = 0;
        for (int y = 0; y < bitmap.Length; y++)
        {
            value = y;
            if (bitmap[y][x] == 'X') break;
        }
        data[s] = value * unit / max_y;
    }

    return data;
}
```

除了用字串陣列，在程式碼裡面畫圖之外，另外也改寫產生對照表的 method, 用同樣的規格傳回對照表，丟到一樣的主程式，執行後的效果變成這樣:

![](/wp-content/images/2016-03-12-cpu_sinewave/12705619_10204279832556067_6262664502740275173_n.jpg)

來跟正規的 Batman Logo 對比一下...

![](http://www.clipartbest.com/cliparts/LiK/zRp/LiKzRpaia.jpeg)

哈哈哈，還挺有 Fu 的...

好，夠了，我知道我很宅，一大篇寫到這裡，為了個面試題目我竟然還可以搞到一整篇 =_= ....

最後，我只想問...

*"我這樣算通過 Microsoft 面試了嗎? XDDDD"*


相關 source code, 有需要的可以到我的 GitHub clone 回去玩玩~

GitHub Project: [Andrew.CPUDraw](https://github.com/andrew0928/Andrew.CPUDraw)

