---
layout: post
title: "Canon Raw Codec + WPF #2, ThreadPool"
categories:
- "系列文章: Canon Raw Codec & WPF"
tags: [".NET","WPF","作品集","多執行緒"]
published: true
comments: true
redirect_from:
  - /2007/12/11/canon-raw-codec-wpf-2-threadpool/
  - /columns/post/2007/12/12/Canon-Raw-Codec-2b-WPF-22c-ThreadPool.aspx/
  - /post/2007/12/12/Canon-Raw-Codec-2b-WPF-22c-ThreadPool.aspx/
  - /post/Canon-Raw-Codec-2b-WPF-22c-ThreadPool.aspx/
  - /columns/2007/12/12/Canon-Raw-Codec-2b-WPF-22c-ThreadPool.aspx/
  - /columns/Canon-Raw-Codec-2b-WPF-22c-ThreadPool.aspx/
  - /blogs/chicken/archive/2007/12/12/2874.aspx/
wordpress_postid: 132
---

效能問題, 就跟我自己寫的小工具一起講好了. 話說之前 Microsoft 提供了一個很讚的小工具: [Resize Pictures Power Toys](http://download.microsoft.com/download/whistler/Install/2/WXP/EN-US/ImageResizerPowertoySetup.exe), 功能超簡單, 大概就是檔案總管把圖檔選一選, 按右鍵選 "Resize pictures" 就好了:

![image](/images/2007-12-12-canon-raw-codec-wpf-2-threadpool/image_3.png)

選了之後就有簡單的對話視窗:

![image](/images/2007-12-12-canon-raw-codec-wpf-2-threadpool/image_9.png)

很簡單吧, 我個人非常愛用, 而且轉出來的效果也不差, 看起來 JPEG quality 大約有 80% ~ 90% 吧... 無耐 windows xp 裡有幾個跟 image 相關的 power toys, 到了 vista 通通不能用. 看來應該都是碰到 GDI+ 要轉換到 WPF 的陣痛期吧, 這幾個小工具還真是讓我繼續撐在 XP 的主要理由之一...

扯遠了, 所以我的目標就是寫個類似的小工具, 讓我簡單的做批次縮圖就好. 有了上一篇的基礎, 要寫這種 tools 實在是沒什麼挑戰, 大概會寫 winform 的拉兩下就可以收工了...

不過, 大話說太早. 先貼一下成品的畫面, 後面說明比較清楚:

![image](/images/2007-12-12-canon-raw-codec-wpf-2-threadpool/image_12.png)

要做的東西很簡單. 選好一堆圖按右鍵選 resize pictures 後就跳這畫面, 按 Resize 就開始跑. 用的是前一篇弄好的 library. 結果碰到的障礙還不少. 雖然可以跑, 但是看了就很礙眼...

1. **效能有點糟.**  
   比較好的架構一定會有額外的效能折損, 我倒可接受. 內建的 JPEG codec 還好, 比不上像 Google Picasa 那樣快速. 但是 canon raw codec 就慘不忍睹... 如果把 raw 轉成同大小的 jpg (4000x3000 pixel), 足足要 60 ~ 80 sec ...

2. **沒針對多處理器最佳化**  
   簡單的說, 以我的雙核 CPU (Core2Duo E6300), 跑起來 CPU 利用率只有 5x% 而以.

3. **ThreadPool 也無法解決問題**  
   因為 (2), 就很直覺的聯想到, 我一次轉兩張, 同樣時間內可以完成兩張的轉檔, 單位時間的運算量還是有提升, 雖然每一張還是要花那麼久... 不過我錯了, 看來是 canon codec 的限制, 開 thread pool 跑下去, 一樣是卡在 60% cpu 使用率左右...

4. **UI thread 問題**  
   thread pool 也不完全沒有作用. jpeg encode / decode 的部份是可以充份利用到 thread pool 的好處的, 只是 canon raw decode 的部份用不到. 當部份時間是 canon raw decode + jpeg encode / decode 時, 剩餘的 CPU 運算能力還是吃的到. 但是 thread pool 無法控制 priority, pool 裡的 thread 就嚴重的影響到 UI thread 的作業. 常看到的現像就是進度列一直在跑, 不過預覽圖片的控制項卻一直跑不出來

(1) 的問題其實沒這麼嚴重. Microsoft HD Photo 有一個 feature, 就是大檔放在網路上, 你也能夠很快的透過網路看到小圖. 有點類似早期漸進式的 jpeg 那樣. 不過看起來 codec 的設計更好一點. 實驗的結果是, Full Size .CR2 (4000x3000) 存成同大小的 JPEG 檔需要 60sec, 而存成 800x600 只要 5 sec. 但是拿對照組 .JPG (4000x3000) -> .JPG (800x600), 差距又沒這麼大. 因此推測起來, 應該在 decode 階段就已經針對這樣的需求設計過了.

剩下的問題我試了好幾種方法, 目標都擺在如何安排這堆 thread 在合適的時間做合適的工作. canon codec 就不適合同時丟好幾個 thread 下去跑, 因為完全沒用, 反而拉長每個 .CR2 從開始到輸出的時間. jpeg 的部份就很適合, 因為時間短, 多核的好處也可以藉著多 thread 用的到. 另外 canon codec 因為限制較多, 我需要它以較高的 priority, 並且要在第一時間就開始跑, 才不會拖慢整個轉檔的處理時間... 理想的 task 安排狀況應該要像這樣:

![簡報1](/images/2007-12-12-canon-raw-codec-wpf-2-threadpool/1_3.png)

最後找到一個我比較滿意的解, 就是另外寫一個合用的 ThreadPool... @_@

其實我是很不想做重新發明輪子這件事, 不過除此之外實在沒什麼好方法. 所幸 .net 下要自己弄出個 thread pool 也不難. 這一切都要感謝當年在 yam, 當時研發部的一位主管, 交大的學長, 現在跑到 Microsoft 去了, 我們都叫他 "旺旺" .. 他技術能力只能用 "神" 來形容... 當時他在公司內開了門課, 真是印像深刻. 就用 java 示範了如何寫 ThreadPool ... 寫起來還真沒幾行... 扣掉一堆 import (相當於 c# 的 using) 等宣告之類的 code, 整個功能 "完整" 的 thread pool 大概只有一百行左右的code... 而且 thread 動態 create 跟回收等功能一樣不少... threads 之間同步問題也沒漏掉..

我歸納了一下我需要的 ThreadPool 到底要什麼功能, 而內建的到底缺什麼... 要怎麼做就很清楚了... 要解決上面的問題, 我大概需要這樣的 thread pool 來支援我的想法:

1. thread 的數量不需要是動態的, 固定的就夠了. 一次開太多 thread 效果不見得好.
2. thread 一定要能設定 priority. 因為轉圖檔是 cpu bound 的工作, priority 設低一點對整體的回應時間比較好.
3. 需要多組 thread pool. 我的想法是用一組專用的 thread pool 來處理 canon raw codec, 只要 1 thread 就夠 (以後 canon 真的改善的話再加大數量). 另外其它 (大部份都是 jpeg codec) 的工作就丟到有 4 threads 的 thread pool 去跑. 至少到四核的 cpu 都還能夠充份的利用到.
4. 需要簡單的作法, 能夠 wait thread pool 裡的工作全處理完. .net 內建的也可以, 不過必需透過比較麻煩的 WaitHandle 自己去 wait ...

這些剛好都是我需要, 但是 .NET 內建的 thread pool 做不到的需求. 因此自己寫了個簡單的 SimpleThreadPool .. 介面規格就儘量比照內建的 ThreadPool (因為 code 已經寫好不想改太多 [:P]). 用起來像這樣:

```csharp
private static void SimpleThreadPoolTest()
{
    SimpleThreadPool stp1 = new SimpleThreadPool(2, System.Threading.ThreadPriority.BelowNormal);
    SimpleThreadPool stp2 = new SimpleThreadPool(1, System.Threading.ThreadPriority.Lowest);

    stp1.StartPool();
    stp2.StartPool();

    for (int count = 0; count < 10; count++)
    {
        stp1.QueueWorkItem(
            new WaitCallback(ShowMessage),
            string.Format("STP1[{0}]", count));
        stp2.QueueWorkItem(
            new WaitCallback(ShowMessage),
            string.Format("STP2[{0}]", count));

        Thread.Sleep(13);
    }


    Console.WriteLine("wait stop");
    stp1.EndPool();
    stp2.EndPool();
}


private static void ShowMessage(object state)
{
    Console.WriteLine("ThreadID: {0}, state: {1}", Thread.CurrentThread.ManagedThreadId, state);
    Thread.Sleep((new Random()).Next(1000));
}
```

嗯, 功力跟旺旺比差了一點, 不過也是一百出頭行就搞定這個 ThreadPool ... [:D], 接下來就是火力展示了... 因為介面跟內建的 ThreadPool 幾乎一樣. 就簡單測一下 125 JPEG + 20 G9 RAW + 2 G2 RAW files 一起做轉檔時的 CPU 使用率記錄...

圖一. 用內建的 ThreadPool, 110 sec ( UI 回應正常, 進度列也會跑. 不過礙於 CPU loading 關係, ImageBox 的圖都沒出來)

![image](/images/2007-12-12-canon-raw-codec-wpf-2-threadpool/image_18.png)

圖二. 改用我自己寫的 SimpleThreadPool, 90 sec. 因為調整過 priority, 每張圖轉完 ImageBox 都會立即顯示出來.

![image](/images/2007-12-12-canon-raw-codec-wpf-2-threadpool/image_21.png)

第一張圖, 所有的 job 都依序執行, 簡單的 jpeg 都擠在前段, 那段 cpu 100% 就是這樣來的. 後面就都是 canon decoder 在跑, cpu 大約都維持在 50% 左右, 直到跑完為止.

而第二張圖, jpeg / canon 都強迫同時一起執行. 而 canon 的 priority 略高於 jpeg. 因此排程的策略是優先執行較慢的 canon decoder, 而剩餘的 cpu 運算能力就拿來處理 jpeg 的部份. 因為 cpu 使用率的統計圖下的面積 (積分) 就是總共需要的運算量. 看的出來維持在 100% 的部份越短, 則總體完成的時間就會拉長... 後面自定的 thread pool 的作法, 不論在 UI 回應, 跟整體處理的時間都比較好. 看來適度的調整 thread 數量, 跟 thread priority 還是很有用的. 不過題外話, thread 再怎麼用, 效果還是不如 lib or compiler level 做的平行處理效果來的好. ZD Net 上有一系列 [intel 提供的 video](http://www.zdnet.com.tw/white_board/intel/video-8.htm), 講的還不錯. [Microsoft 也替 .NET 開發了一套 Library](http://msdn.microsoft.com/msdnmag/issues/07/10/Futures/default.aspx?loc=zx) ([download](http://www.microsoft.com/downloads/details.aspx?FamilyID=e848dc1d-5be3-4941-8705-024bc7f180ba&DisplayLang=en)), 只要調整一點語法, 就可以把 loop 內的運算轉成平行運算, 這種效果遠比用 thread pool 來的聰明 & 有效. 不過還在 community preview 就暫時不考慮採用了.

總算, 搞定了 thread pool, 也搞定了 metadata, 幾個主要的障礙都排除了. 兩個要開發的工具也完成了一個 ( image resizer ), 剩下的歸檔程式就剩下納入 video encoder 的部份也就大功告成了. 有力氣的話會再寫一篇吧, 敬請期待 [:D]
