---
layout: post
title: "Memory Management (III) - .NET CLR ?"
categories:
- "系列文章: Memory Management"
tags: [".NET","作業系統","技術隨筆"]
published: true
comments: true
permalink: "/2008/03/03/memory-management-iii-net-clr/"
redirect_from:
  - /columns/post/2008/03/03/Memory-Management-(III)-NET-CLR-.aspx/
  - /post/2008/03/03/Memory-Management-(III)-NET-CLR-.aspx/
  - /post/Memory-Management-(III)-NET-CLR-.aspx/
  - /columns/2008/03/03/Memory-Management-(III)-NET-CLR-.aspx/
  - /columns/Memory-Management-(III)-NET-CLR-.aspx/
  - /columns/post/2008/03/03/Memory-Management-(III)---NET-CLR-.aspx/
  - /post/2008/03/03/Memory-Management-(III)---NET-CLR-.aspx/
  - /post/Memory-Management-(III)---NET-CLR-.aspx/
  - /columns/2008/03/03/Memory-Management-(III)---NET-CLR-.aspx/
  - /columns/Memory-Management-(III)---NET-CLR-.aspx/
  - /blogs/chicken/archive/2008/03/03/3021.aspx/
wordpress_postid: 117
---

續 [上篇](/post/Memory-Management-(II)---Test-Result.aspx) & [上上篇](/post/Memory-Management---(I)-Fragment-.aspx) ，同樣的問題，我改用 .NET 開發是不是就搞定了? 其實這篇才是我要寫的重點，只不過引言寫太高興，就是兩篇文章了，咳咳... 有人在問，為什麼我老是寫些冷門的文章? 沒辦法... 大家都在寫的東西我就沒興趣寫了，文筆沒別人好，網站沒別人漂亮，連範例程式都沒別人炫，只好挑些沒人寫的內容...

大部份討論這主題的文章，講的都是 GC, GC 的 generation，IDisposable，還有 Heap 等等，不過這些知識都無法直接回答這次問題。底下的例子你會發現，預設的 GC 也無法解決 memory fragment 的問題，不過實際上是有解的，只是還要動用到秘技...


回題，先來看看之前的問題為什麼會是個問題? 萬惡之首都在: 指標 (POINTER)。

因為有 pointer，因此 C 絕對不能 *自動* 幫你調整記憶體位置，也就一定會有這種問題。看到為何我在上篇提到的程式碼要把 pointer 的值印出來? 因為這代表我可以輕易拿的到實際的位址，因此任何重新定址 (relocation) 的動作一定會影響到程式的執行。所以最根本的解決辦法就是把 pointer 這東西拿掉。

年紀較輕的程式語言，如我常提到的 Java 跟 C#，都完完全全的把 pointer 從語言內移掉了，只留下 reference 這類差不多的東西。除了拿不到絕對的 address 之外，其它功能一個都不缺。但是這樣帶來的好處是很明顯的，除了一般書上講到爛的理由: "更安全，更簡易" 之外，很重要的一點就是，像 CLR or JavaVM 這種環境，開始有機會去搬移記憶體配置的區塊，徹底的由系統層面解決這種問題了。

.NET / Java 回收記憶體的動作是自動的，就是常聽到的 Garbage Collection，而上面提到的 relocation，就是指在回收時順便把剩下已配置的空間排在一起，搬移記憶體區塊所需要的重新定址動作。這種類型的 GC 有個特別的名辭，叫作 compact collection。理論上，.NET 已經具備這樣的條件了，應該要有能力可以解決這樣的問題。

不過 "可以解決" 跟 "已經解決" 仍然有一段差距，那麼現在的 .NET CLR 到底行不行? 一樣的範例程式用 C# 改寫一下，同樣的試看看，不過這次懶的再放好幾種版本試試看了，除了最大可用記憶體可能有差別之外，其它應該都統一了。我只針對 .NET 2.0 (x86) 一種版本測試，一樣，鐵齒的讀者們，有興趣就抓回去試一試...。

整段程式碼跟之前 C 版本大同小異，就是照順序配置 64mb 的 byte[]，直到丟出 OutOfMemoryException，然後跳著釋放，接著再配置 72mb 的 byte[]，看看能不能配置成功? 直到再丟出 OutOfMemoryException 為止，能配置多少記憶體? 這邊為了方便，我直接在 vista x86 系統上測試:



測試的結果令我想殺人，竟然是 FAIL ? 放掉的空間拿不回來...

![](/images/2008-03-03-memory-management-iii-net-clr/image_3.png)


後來想到，程式移除 reference，不見得會立刻釋放記憶體，總得等垃圾車 (Garbage Collect) 來收拾一下... 手動呼叫了 GC，也強迫指定要回收所有的 Generation 了 (呼叫: GC.Collect(GC.MaxGeneraion) ) 再試一次:

![](/images/2008-03-03-memory-management-iii-net-clr/image_5.png)


結果好不到那裡去，難到我沒用市政府的垃圾袋嘛? [:@] 查了一下 MSDN，常見的 generation 問題也試過，沒有用。90% 講 CLR GC 的問題都在探討 generation 的問題...  查到某 Java 名人的 [文章](http://www.microsoft.com/taiwan/msdn/columns/DoNet/garbage_collection.htm)，提到了 compact collection 比較接近，不過沒有講怎麼明確的啟動這樣的 GC 啊... 後來去翻 .NET runtime 裡關於 garbage collection 的設定，發現還有這玩意... gcConcurrent / gcServer:

gcConcurrent: Specifies whether the common language runtime runs garbage collection on a separate thread.

gcServer: Specifies whether the common language runtime runs server garbage collection.

講的很清楚，不過對我沒啥用。gcConcurrent可能的影響是，也許呼叫後系統還在GC，我的程式就先跑下去了? 因此這東西關掉也許有幫助，再來試一次:


![](/images/2008-03-03-memory-management-iii-net-clr/image_7.png)


真慘，一點幫助都沒有... 放掉的 768MB，只撈回 72MB，再來看一下最後一個 gcServer，看它的 HELP 看不大出來什麼是 "server garbage collection" ? 算了，試一下比較快:

![](/images/2008-03-03-memory-management-iii-net-clr/image_9.png)


Bingo，看來這個參數下下去才是我預期的結果，放掉了 576MB，後面撈了 648MB 回來。這樣的作法，已經完全不會受到 memory fragment 問題的影響，証實了 compact collection 是有發恢它的效用的，只不過這個參數實際的作用，翻遍了 Google / MSDN，得到的都是很模菱兩可的答案，不外乎是你的程式如果是 blah blah blah 的話就要用 gcServer，這樣會比較好之類的，不過實際的差別則看不大出來。沒有任何一篇文件明確提到 server gc 會做 compact collection (如果這篇不算的話，哈哈)，而 workstation gc 不會，也許前面的方式也會觸發 compact collection也說不定，只是時機不成熟...

抱著不可能的希望，用 Reflector追看看，果然不出所料，Reflector也看不到細節，因為全都呼叫 native code 去了。不過這次的測試，至少確定了，在啟用 gcServer option 之後，CLR 的 GC 是會進行 compact collection 的。

寫到這裡，本系列文章結束，只是為了在新的平台驗證古早的問題而以，果然時代在進步，以前耽心的問題現在都不再是問題了。這一連串試下來，學到了一課，原來 gcServer 有這個差別，算是值回票價了。最後把我的測試程式碼貼一下，一樣，歡迎拿去各種平台試一下，有不一樣的結果也記得通知我一聲!


[Program.cs]

```csharp

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
namespace ClrMemMgmt
{
    class Program
    {
        static void Main(string[] args) {
            List<byte[]> buffer1 = new List<byte[]>();
            List<byte[]> buffer2 = new List<byte[]>();
            List<byte[]> buffer3 = new List<byte[]>();
            
            //            
            //    allocate             
            //            
            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine("1. Allocate 64mb block(s) as more as possible...");
            try
            {
                while (true)
                {
                    buffer1.Add(new byte[64 * 1024 * 1024]);
                    Console.Write("#");
                    buffer2.Add(new byte[64 * 1024 * 1024]);
                    Console.Write("#");
                }
            }
            catch (OutOfMemoryException)
            {
            }
            Console.WriteLine();
            Console.WriteLine("   Total {0} blocks were allocated ( {1} MB).", (buffer1.Count + buffer2.Count), (buffer1.Count + buffer2.Count) * 64);
            
            //        
            //    free  
            //        
            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine("2. Free Blocks...");
            buffer2.Clear();
            Console.WriteLine("   Total: {0} blocks ({1} MB)", buffer1.Count, buffer1.Count * 64);

            //        
            //  GC  
            //            
            GC.Collect(GC.MaxGeneration);  
                 
            //           
            //    allocate  
            //          
            Console.WriteLine();
            Console.WriteLine();
            Console.WriteLine("3. Allocate 72mb block(s) as more as possible...");
            try
            {
                while (true)
                {
                    buffer3.Add(new byte[72 * 1024 * 1024]);
                    Console.Write("#");
                }
            }
            catch (OutOfMemoryException)
            {
            }
            Console.WriteLine();
            Console.WriteLine("   Total: 64mb x {0}, 72mb x {1} blocks allocated( {2} MB).\n", buffer1.Count, buffer3.Count, buffer1.Count * 64 + buffer3.Count * 72);
            Console.ReadLine();
        }
    }
}
```

[configuration file]
```xml
<?xml version="1.0" encoding="utf-8" ?>
<configuration>  
  <runtime>    
    <!--<gcConcurrent enabled="false" />-->    
    <!--<gcServer enabled="true" />-->  
  </runtime>
</configuration>
```