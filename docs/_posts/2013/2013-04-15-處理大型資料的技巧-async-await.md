---
layout: post
title: "處理大型資料的技巧 – Async / Await"
categories:

tags: [".NET","ASP.NET","AZURE","C#","MSDN","Tips","多執行緒","技術隨筆"]
published: true
comments: true
permalink: "/2013/04/14/處理大型資料的技巧-async-await/"
redirect_from:
  - /columns/post/2013/04/15/e89995e79086e5a4a7e59e8be8b387e69699e79a84e68a80e5b7a7-e28093-Async-Await.aspx/
  - /post/2013/04/15/e89995e79086e5a4a7e59e8be8b387e69699e79a84e68a80e5b7a7-e28093-Async-Await.aspx/
  - /post/e89995e79086e5a4a7e59e8be8b387e69699e79a84e68a80e5b7a7-e28093-Async-Await.aspx/
  - /columns/2013/04/15/e89995e79086e5a4a7e59e8be8b387e69699e79a84e68a80e5b7a7-e28093-Async-Await.aspx/
  - /columns/e89995e79086e5a4a7e59e8be8b387e69699e79a84e68a80e5b7a7-e28093-Async-Await.aspx/
wordpress_postid: 6
---


原本只是很單純的把大型檔案 (100mb 左右的 video) 放到 Azure Storage 的 BLOB 而已，結果效能一直不如預期般的理想。才又把過去的 thread 技巧搬出來用，結果又花了點時間改寫，用 async / await 的效果還更漂亮一點，於是就多了這篇文章 :D

其實這次要處理的問題很單純，就是 WEB 要從 Azure Storage Blob 讀取大型檔案，處理前端的認證授權之後，將檔案做編碼處理後直接從 Response 輸出。主要要解決的問題是效能過於糟糕... 透過層層的處理，效能 (3.5 Mbps) 跟直接從 Azure Storage 取得檔案 (7.3 Mbps) 相比只剩一半左右.. 過程中監控過 SERVER 的 CPU，頻寬等等，看來這些都不是效能的瓶頸。

![](/wp-content/be-files/image_16.png)



為了簡化問題，我另外寫了個簡單的 Sample Code, 來呈現這問題。最後找出來的原因是，程式碼就是單純的跑 while loop, 不斷的把檔案內容讀進 buffer 並處理後，將 buffer 輸出。結果因為程式完全是 single thread 的處理方式，也沒有使用任何非同步的處理技巧，導致程式在讀取及處理時，輸出就暫停了，而在輸出時，讀取及處理的部份就暫停了，讓輸入及輸出的 I/O, 還有 CPU 都沒有達到滿載... 於是效能就打對折了。用時間軸表達，過程就如下圖:

![](/wp-content/be-files/image_17.png)

這樣的設計方式，同一時間只能做一件事。若把上圖換成各種資源的使用率，會發現不論是 DISK、NETWORK、CPU等等資源，都沒有同時間保持忙碌。換句話說好像公司請了三個員工，可是同時間只有一個人在做事一樣，這樣的工作安排是很沒效率的。要改善的方法就是讓三個員工都保持忙碌，同時還能亂中有序，能彼此協調共同完成任務。

同樣的狀況應該很普遍吧? 不要說別人了，就連我自己都寫過很多這樣的 CODE ... 光是 COPY 大型檔案，大家一定都是這樣寫的: 用個 while loop, 把來源檔讀進 buffer, buffer 滿了寫到目地檔，然後不斷重複這動作，直到整個檔案複製完成為止。這不是一模一樣的情況嗎? 只是大部份的人不會去考量如何加速這樣的動作而已...

我先把目前的CODE簡化一下，拿掉一些不相關的部份，單純的用 ```Read()``` / ```Process()``` / ```Write()``` 三個空的 method 代表執行這三部份的工作，執行過程需要的時間，就用 Task.Delay( 100 ) 來取代。經簡過後的 Code 如下:


**經簡後的示意程式碼**:

```csharp
public class Program
{
    static Stopwatch read_timer = new Stopwatch();
    static Stopwatch proc_timer = new Stopwatch();
    static Stopwatch write_timer = new Stopwatch();
    static Stopwatch overall_timer = new Stopwatch();
    public static void Main(string[] args)
    {
        overall_timer.Start();
        for (int count = 0; count < 10; count++)
        {
            Read();
            Process();
            Write();
        }
        overall_timer.Stop();
        Console.WriteLine("Total Time (over all): {0} ms", overall_timer.ElapsedMilliseconds);
        Console.WriteLine("Total Read Time:       {0} ms", read_timer.ElapsedMilliseconds);
        Console.WriteLine("Total Process Time:    {0} ms", proc_timer.ElapsedMilliseconds);
        Console.WriteLine("Total Write Time:      {0} ms", write_timer.ElapsedMilliseconds);
    }
    public static void Read()
    {
        read_timer.Start();
        Task.Delay(200).Wait();
        read_timer.Stop();
    }
    public static void Process()
    {
        proc_timer.Start();
        Task.Delay(300).Wait();
        proc_timer.Stop();
    }
    public static void Write()
    {
        write_timer.Start();
        Task.Delay(500).Wait();
        write_timer.Stop();
    }
}
```


程式執行結果：

![](/wp-content/be-files/image_18.png)

程式總共要花掉 10 秒鐘才執行完畢，由於完全沒有任何並行的處理，因此就是很簡單的 Read 花掉 2 秒，Process 花掉 3 秒，Write 則花掉 5 秒，加起來剛好就是總執行時間 10 秒。


回顧一下，過去寫過幾篇如何善用多執行緒來解決各種效能問題的文章，其中兩篇跟這次的案例有關:

1. [MSDN Magazine 閱讀心得: Stream Pipeline](/post/MSDN-Magazine-e996b1e8ae80e5bf83e5be97-Stream-Pipeline.aspx), (2008/01/19)
1. [生產者 vs 消費者 - BlockQueue 實作](/post/e7949fe794a2e88085-vs-e6b688e8b2bbe88085-BlockQueue-e5afa6e4bd9c.aspx), (2008/10/18)
1. [生產線模式的多執行緒應用](/post/RUNPC-2008-11.aspx), ([RUN! PC] 2008 十一月號, 2008/11/04)
1. [RUN!PC 精選文章 - 生產線模式的多執行緒應用](/post/RUN!PC-e7b2bee981b8e69687e7aba0-e7949fe794a2e7b79ae6a8a1e5bc8fe79a84e5a49ae59fb7e8a18ce7b792e68789e794a8.aspx), (2009/01/16)


其實這些方法的目的都一樣，都是透過各種執行緒的操作技巧，讓一件大型工作的不同部份，能夠重疊在一起。這樣的話，整體完成的時間就能縮短。不過，隨著 .NET Framework 一直發展，C# 5.0 提供的 Syntax Sugar 也越來越精彩，到了 .NET Framework 4.5 開始提供了 Async / Await 的語法，能夠大幅簡化非同步模式的設計工作。

非同步的程式設計，其實也是 multi-threading 的一種運用。簡單的說，它就是把要非同步執行的任務丟到另一條執行緒去執行，等到它執行結束後再回過頭來找它拿結果。只是為了這樣的一個動作，往往得寫上數十行程式碼，加上原本程式的結構被迫切的亂七八糟，過去往往非絕對必要，否則不會用這樣的模式。

這次我的目的，其實用前面那幾篇的技巧就能解決了。不過這次實作我想換個方法，都已經 2013 了，有 Async / Await 為何要丟著不用? 這次就用新方法來試看看。先用上面的時間軸那張圖，來看看改進後的程式執行狀況，應該是什麼樣子:

![](/wp-content/be-files/image_19.png)

解釋一下這張圖: 橘色的部份代表是用非同步的方式呼叫的，呼叫後不會 BLOCK 原呼叫者，而是會立即 RETURN，兩邊同時進行。而圖中有個箭頭 + ```await```, 則代表第二個非同步呼叫 ```Write()``` 的動作，會等待前一個 ```Write()``` 完成後才會繼續。

```Write()``` 跟下一次的 ```Read()``` 其實並無相依性，因此在開始 ```Write()``` 時，其實可以同時開始下一回的 ```Read()```, 因此時間軸上標計的執行順序就可以被壓縮，調整一下執行的順序，馬上得到大幅的效能改進。這次要改善的，就是把 ```Read() + Process()``` 跟 ```Write()``` 重疊在一起，預期會有一倍的效能提升。

想要瞭解 C# 的 async / await 該怎麼用，網路上的資源有很多，我習慣看官方的文件，有需要參考的可以看這幾篇:

1. [async (C# Reference)](http://msdn.microsoft.com/en-us/library/vstudio/hh156513.aspx)
1. [Asynchronous Programming with Async and Await (C# and Visual Basic)](http://msdn.microsoft.com/en-us/library/vstudio/hh191443.aspx)

Async / Await 的細節我就不多說了，簡單的說在 method 宣告加上 async 的話，代表它的傳回值會被改成 ```Task<>```, 而呼叫這個 method 會變成非同步的，一旦呼叫就會立刻 Return, 若需要這個 method 的執行結果，可用 await 等待，直到 method 已經執行完畢才會繼續...

廢話不多說，過程就沒啥好說的了，直接來看改好的程式碼跟執行結果:


**改寫為非同步模式的 CODE:**

```csharp
public class Program
{
    static Stopwatch read_timer = new Stopwatch();
    static Stopwatch proc_timer = new Stopwatch();
    static Stopwatch write_timer = new Stopwatch();
    static Stopwatch overall_timer = new Stopwatch();
    public static void Main(string[] args)
    {
        overall_timer.Start();
        DoWork().Wait();
        overall_timer.Stop();
        Console.WriteLine("Total Time (over all): {0} ms", overall_timer.ElapsedMilliseconds);
        Console.WriteLine("Total Read Time:       {0} ms", read_timer.ElapsedMilliseconds);
        Console.WriteLine("Total Process Time:    {0} ms", proc_timer.ElapsedMilliseconds);
        Console.WriteLine("Total Write Time:      {0} ms", write_timer.ElapsedMilliseconds);
    }
    public static void Read()
    {
        read_timer.Start();
        Task.Delay(200).Wait();
        read_timer.Stop();
    }
    public static void Process()
    {
        proc_timer.Start();
        Task.Delay(300).Wait();
        proc_timer.Stop();
    }
    public static async Task Write()
    {
        write_timer.Start();
        await Task.Delay(500);
        write_timer.Stop();
    }
    private static async Task DoWork()
    {
        Task write_result = null;
        for (int count = 0; count < 10; count++)
        {
            Read();
            Process();
            if (write_result != null) await write_result;
            write_result = Write();
        }
        await write_result;
    }   
}
```


程式碼幾乎都沒有動，不過就是把 ```Write()``` 改寫為 Async 版本，同時在主程式 ```DoWork()``` 用 Task 形別，把 ```Write()``` 傳回的 ```Task``` 物件，保留到下一次呼叫 ```Write()``` 前，用 await 來確保上一個 ```Write()``` 已經完成。

改寫過的版本，程式碼很簡單易懂，90% 以上的程式碼結構，都跟原本同步的版本是一樣的，大幅維持了程式碼的可讀性，完全不像過去用了多執行緒或是非同步的版本，整個結構都被切的亂七八糟。看看程式的執行結果，果然跟預期的一樣，整體執行時間大約為 5 秒。多出來的 660 ms, 就是第一次的 ```Read() + Process()```, 跟最後一次的 ```Write()``` 是沒有重疊的，因此會多出 500 ms, 再加上一些執行的誤差及額外負擔，就是這 660ms 的來源了。

![](/wp-content/be-files/image_thumb_2.png)


最後，來看一下效能的改善。在我實際的案例裡，Read 是受限於 VM 與 Storage 之間的頻寬，固定為 200Mbps, 而 Process 是受限於 VM 的 CPU 效能，也是固定可控制的, 最後 Write 則是受限於 client 到 VM 之間的頻寬，可能從 2Mbps ~ 20Mbps 不等，這會直接影響到到 Write 需要的時間。

不管是用 thread 或是 async ，都不是萬靈丹，主要還是看你的狀況適不適合用這方法解決。這次我的案例是用 async 的方式，將 Read / Write 閒置的時間重疊在一起，節省的時間就反應在整個工作完成的時間縮短了。因此兩者花費的時間差距如果過大，則就沒有效果了。

我簡單列了一張表，來表達這個關係。分別針對 client 端的頻寬，從 2Mbps ~ 200Mbps, 列出使用 async 改善前後的花費時間，及效能改善的幅度:




||*200M|100M|80M|50M|20M|10M|5M|2M|
|---|---|---|---|---|---|---|---|---|
|原花費時間(ms)|7000|9000|10000|13000|25000|45000|85000|205000|
|ASYNC花費時間(ms)|5500|5500|5500|8500|20500|40500|80500|200500|
|效能改善%|127.27%|163.64%|181.82%|152.94%|121.95%|111.11%|105.59%|102.24%|

![](/wp-content/be-files/image_21.png)

以執行時間來看，頻寬低於 80M 之後，改善的程度就固定下來了，隨著頻寬越來越低，WRITE 需要花費的時間越來越長，改善的幅度就越來越不明顯。同樣這些數據，換成改善的百分比，換成下一張圖:

![](/wp-content/be-files/image_22.png)

改善幅度最好的地方，發生在 80Mbps, 這時正好是 ```Read() + Process()``` 的時間，正好跟 ```Write()``` 花費的時間一樣的地方。頻寬高於或低於這個地方，效果就開始打折扣了。通常改善幅度若低於 10%, 那就屬於 "無感" 的改善了。

簡單的下個結論，其實任何效能問題都很類似，能用 async 改善的效能問題，一定有這種模式存在: 整個程式執行過程中，有太多等待的狀況發生。不論是 IO 等待 CPU，或是 DISK IO 等待 NETWORK IO 等等，都屬此類。從外界能觀察到的狀況，就是幾個主要的硬體資源，如 Network, CPU, DISK, Memory 等等，都沒有明顯的負載過重，但是整體效能就是無法提升，大概就屬於這種模式了。找出流程能夠重新安排的地方後，剩下的就是如何善用這些技巧 (async)，把它實作出來就結束了。

而 async / await, 處理這類問題，遠比 thread 來的有效率。就我看來，若需要大規模的平行處理，還是 thread 合適。但是像這次的案例，只是希望將片段的任務以非同步的模式進行，重點在精確的切割任務，同時要在特定的 timing 等待先前的任務完成，這時 async / await 會合適的多。