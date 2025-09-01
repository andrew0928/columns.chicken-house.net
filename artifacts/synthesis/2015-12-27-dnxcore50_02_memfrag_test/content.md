![](/images/2015-12-27-dnxcore50_02_memfrag_test/img_567f9c9e811a9.png)


記憶體管理，是跟底層平台高度相關的議題。對於 developer 來說，能掌控的部分很有限，developer 能做的動作，不外乎是 allocate / free memory, 頂多對於 GC (garbage collection) 的機制更明確的掌握而已。超出這個範圍以外的部分，就真的只剩下好好處理 exception 的份了...

這次 .NET Core 開源 + 支援 Linux / MacOS, 正好開創了一個新的平台支援，實際測測看，是掌握差異最快的方式。我挖出了當年的老文章探討的記憶體管理問題，在新的平台上驗證。不同平台的差異，遠比我想像的精彩，就順手把它寫成文章整理起來，給需要的人參考。


<!--more-->

{% include series-2016-dnxcore.md %}



# 測試的方法

驗證的方式很簡單，就是測試 .NET 的記憶體管理能力。測試方式會分三個步驟:

1. 連續配置 64mb 區塊的記憶體，直到 OOM (Out Of Memory) 為止，記錄能配置的區塊數量。
1. 按順序，保留奇數的區塊，把偶數的區塊 free 掉。理論上這樣會讓記憶體空間碎片化，剩餘的空間不會有超過連續 64mb 以上的可用空間。
1. 接著試著配置 72mb 區塊的記憶體，直到 OOM 為止，記錄能配置的區塊數量。


過去對這個議題詳細的探討，可以參考這三篇 ([#1](/?p=120), [#2](/?p=118), [#3](/?p=117))。





為了完全控制測試環境，我用我自己的 PC 開了幾個相同規格的 VM，分別用不同的平台 (windows, windows container, linux container) 來驗證，一次只開一個 VM，確保不會互相干擾。雲端版本的測試，我也會在 Windows Auzre 上進行一次，Azure 的部分會等下一篇計算圓周率的測試也做完之後，一起搬上 Azure 再來綜合比較。有忍不住想偷跑的網友，這邊([www.apertus.com.tw](http://www.apertus.com.tw/), coding in cloud) 有很多相關的文章，可以到上面看看~

為什麼要做這樣的測試? 主要是先製造 memory fragment 的情況，然後看看 garbage collection 的機制能否應付這種狀況? 同時也看看底層的 .net core runtime 在記憶體不足的狀況下，能否有效的保護好上面的應用程式? 處理的效能及效果是否理想等等議題。測試的過程中，老實說發現了好幾個我意料之外的狀況，因此答案也不是 YES 或 NO 那麼簡單... 想知道測試的過程及結果，請繼續看下去~

這次的測試，由於扯到很多環境設定的步驟，我想親自體驗.. 因此沒有在第一時間就採用 Azure .. 而是自己從無到有建立起來，後面的整體評比再改到 Azure 上面進行。我自己的 PC 規格及環境如下:

* **CPU**: Intel Core i7-2600K ( @ 3.40GHz )
* **RAM**: 24GB (DDR3-1600, 4 + 4 + 8 + 8)
* **HDD**: Intel SSD 730 (240GB) + Seagate Enterprise Capacity 5TB (ST5000NM0024), 7200 rpm 企業級硬碟
* **OS**:  Microsoft Windows 10 Enterprise


為了這次測試，我直接用了 windows 10 內建的 Hyper-V 當作虛擬化的環境，情況允許的話我會建立 Docker Host 的作業環境，在 Container 內執行 .NET Core 的程式。VM 的規格統一如下:

* **CPU**:  1 Processor
* **RAM**:  1024 MB (dynamic memory was disabled)
* **SWAP**: 4096 MB
* **HDD**:  32GB (VHDX, attached on IDE controller 0, HDD #1)
* **VGA**:  1366 x 768



執行的環境，我準備了這四套 (如下)，比較特別的是 windows server 2016 也支援了 windows container, 當然要拿出來用用看 XD，不過現在還在 tech preview, 結果僅供參考，等到正式 release 後再來補測試結果:

1. **Boot2Docker**, 使用 Docker Toolbox 提供的 boot2docker.iso, 版本 1.9.1
1. **Ubuntu 15.10**, 預設安裝 + SSH, 安裝 docker 1.9.1
1. **Windows 2012R2 Server Core**,  (直接在上面跑 .NET Core)
1. **Windows 2016 Tech Preview 4 (Nano)**, 在上面建立 windowsservercore container, 在裡面安裝 .NET Core 的 CoreCLR runtime


OK，準備動作大功告成，開始測試~




# #0. 準備測試程式

我特地挑選了一個最沒有問題的平台當作對照組。這組其實沒什麼好講的，這是最典型的 .NET application 執行環境啊，從最早的 .NET 1.0 開始算，已經有十幾年了.. 就趁這個段落來看一下測試用的 CODE:



```csharp
using System;
using System.Collections.Generic;

namespace dotnetcore.MemFrag
{
    class Program
    {
        static Random rnd = new Random();

        static byte[] AllocateBuffer(int size)
        {
            byte[] buffer = new byte[size];
            //InitBuffer(buffer);
            return buffer;
        }

        static void InitBuffer(byte[] buffer)
        {
            rnd.NextBytes(buffer);
        }

        static void Main(string[] args)
        {
            DateTime start;

            List&lt;byte[]&gt; buffer1 = new List&lt;byte[]&gt;();
            List&lt;byte[]&gt; buffer2 = new List&lt;byte[]&gt;();
            List&lt;byte[]&gt; buffer3 = new List&lt;byte[]&gt;();

            //            
            //    allocate             
            //            
            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine("1. Allocate 64mb block(s) as more as possible...");
            start = DateTime.Now;
            try
            {
                while (true)
                {
                    buffer1.Add(AllocateBuffer(64 * 1024 * 1024));
                    Console.Write("#");
                    buffer2.Add(AllocateBuffer(64 * 1024 * 1024));
                    Console.Write("#");
                }
            }
            catch (OutOfMemoryException)
            {
            }
            Console.WriteLine();
            Console.WriteLine("   Complete.");
            Console.WriteLine("   - total {0} x 64mb blocks = {1} MB were allocated.", (buffer1.Count + buffer2.Count), (buffer1.Count + buffer2.Count) * 64);
            Console.WriteLine("   - total execute time: {0} sec", (DateTime.Now - start).TotalSeconds);

            //        
            //    free  
            //        
            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine("2. Free Blocks...");
            start = DateTime.Now;
            {
                //        
                //  de-reference and GC  
                //            
                buffer2.Clear();
                GC.Collect(GC.MaxGeneration);
            }
            Console.WriteLine("   Complete.");
            Console.WriteLine("   - total {0} x 64mb blocks = {1} MB were allocated.", buffer1.Count, buffer1.Count * 64);
            Console.WriteLine("   - total execute time: {0} sec", (DateTime.Now - start).TotalSeconds);


            //           
            //    allocate  
            //          
            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine("3. Allocate 72mb block(s) as more as possible...");
            start = DateTime.Now;
            try
            {
                while (true)
                {
                    buffer3.Add(AllocateBuffer(72 * 1024 * 1024));
                    Console.Write("#");
                }
            }
            catch (OutOfMemoryException)
            {
            }
            Console.WriteLine();
            Console.WriteLine("   Complete.");
            Console.WriteLine("   - total: 64mb x {0} + 72mb x {1} = {2} MB were allocated.", buffer1.Count, buffer3.Count, buffer1.Count * 64 + buffer3.Count * 72);
            Console.WriteLine("   - total execute time: {0} sec", (DateTime.Now - start).TotalSeconds);


            Console.WriteLine("[Enter] to exit...");
            Console.ReadLine();
        }
    }
}
```


程式很簡單，主要就分三大部分，以 64mb 為單位連續配置，然後跳著釋放空間 + 呼叫 GC，最後試著連續配置 72mb 空間。每個步驟結束後統計 64 / 72 mb 的配置數量，以及計算花費的時間。

唯一特別要注意的是 static void InitBuffer(byte[] buf) 這個 method, 這個動作在之前的文章沒有出現，是這次特地加上去的。它的功能很單純，就是 buffer 配置好了之後，用亂數填滿這整個 buffer 的空間。為何要做這動作? 後面測試時再說明...

(未完待續)