---
layout: post
title: "ThreadPool 實作 #1. 基本概念"
categories:
- ".NET"
- "多執行緒"
- "技術隨筆"
tags: [".NET","多執行緒","技術隨筆"]
published: true
comments: true
permalink: "/2007/12/14/threadpool-實作-1-基本概念/"
redirect_from:
  - /columns/post/2007/12/14/ThreadPool-e5afa6e4bd9c-1-e59fbae69cace6a682e5bfb5.aspx/
  - /post/2007/12/14/ThreadPool-e5afa6e4bd9c-1-e59fbae69cace6a682e5bfb5.aspx/
  - /post/ThreadPool-e5afa6e4bd9c-1-e59fbae69cace6a682e5bfb5.aspx/
  - /columns/2007/12/14/ThreadPool-e5afa6e4bd9c-1-e59fbae69cace6a682e5bfb5.aspx/
  - /columns/ThreadPool-e5afa6e4bd9c-1-e59fbae69cace6a682e5bfb5.aspx/
  - /blogs/chicken/archive/2007/12/14/2880.aspx/
wordpress_postid: 130
---

既然都花了力氣回憶起過去學的 ThreadPool Implementation, 而且都用 C# 寫好了, 不如就整理一下好了. 其實寫起來 code 真的都不難, 難的是人腦天生就不適合思考這種 multithreading 的東西, 想多了腦筋真的會打結. 另外一個障礙是有些東西要唸過 Operation System 才會懂, 沒這基礎的話, 光看 API 說明會一個頭兩個大...

這篇還不會貼完整的 code, 先把必要的基礎及認知說明一下. ThreadPool 的概念其實很簡單, 這 design pattern 目的是把過去的 multi-threading programming model 簡化, 把複雜的 threads control 拆到 thread pool implementation 裡封裝起來, 使用它的人只要把你的 job 封裝成一個 job object, 丟到 pool 裡面代為執行就可以了. 然後裡面就套用 "生產者 / 消費者" 的模式, User 不斷的生出 job 給 thread pool, 而 thread pool 不斷的消化掉 (執行 job) 它. 實作這些東西要面臨到的課題, 有這幾項:

1. 基本的 thread sync 機制
1. thread pool 內部的 thread 管理, thread 動態建立 / 回收機制
1. 封裝 job, job queue

先從最抽像的 (1) 來說好了. 這是過去作業系統 (OS) 這門課, 特地花了一整章來說明的課題. 當年第一次碰到用 java 實作 thread pool 時, 我還特地把課本挖出來再看一次... @_@, 不過搬了兩次家, 課本也不曉得塞到那去了, 哈... 印像中記得裡面有 OS 管理下的 process 生命周期 state machine:

圖片來源: [http://en.wikipedia.org/wiki/Process_states](http://en.wikipedia.org/wiki/Process_states)

![](http://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Process_states.svg/600px-Process_states.svg.png)



中間三個狀態是主要的部份, running 當然就是指執行中, 而要等待別人喚醒則是進入 blocked 狀態, block 狀態時是不會被 OS 分配到任何 cpu time slice 的. 等到被喚醒後, 並不是直接跳到 running, 而是跳至 waiting, 等待 OS 把下一段 cpu time slice 分給這個 thread 時, 它就會再度進到 running 狀態.

所謂的 synchronization, 就是指在 multi-threading 環境下, 每個 thread 各跑各的, 完全不管其它 thread 在作什麼. 但是在某些特殊情況下, 是要 threads 之間互相調整腳步的. 舉例來說, FlashGet 大家都用過吧? 它一次開好幾個 thread 下載同個檔案的不同部份. 那些情況需要 synchrinization ? 舉個 use case:

> 下載到一半想停掉, UI thread 接受了 user 的指令 (按按鈕), 每個 thread 必需適當的中止目前的動作及存檔. UI thread 必需 "等待" 每個
> thread 完成後才能回報 user 停止的指令已經完成.

在 Multi-threading 的環境下, 千萬不要再去用老掉牙的同步方式 (啥? 就是用 global variable, 然後用 loop 一直去檢查), 正規的用法就是用 OS 提供的 synchronization 機制, 一邊 wait, 另一邊去叫醒它. 對照上面的圖來說, 也就是讓 thread 進到 blocked 狀態. 在 Java 裡就是 Thread 的 Notify 相關 method, 在 .NET 則是包裝成 WaitHandle 物件. 以這種最基本的 wait / notify, 在 .NET 可以用 ManualResetEvent 來達成. 簡單的寫兩段 code, 用起來像這樣:

```csharp
// thread 1: 等著被喚醒
wait_handle.WaitOne( );
 
// thread 2: 喚醒 thread 1
wait_handle.Set( );
```


更複雜的例子, 可以用其它不同型態的 WaitHandle 來達成. 在 .NET 是把所有這種用於同步機制的物件都抽像化成 System.Threading.WaitHandle, 它是 abstract class, 你要找一個合適的衍生類別來用. 這些機制原則上一定要靠 OS 的 API 才能提供, 請別異想天開自己搞一個...  列幾個常用的:

1.	AutoResetEvent: 叫醒單一個 wait thread
1.	ManualResetEvent: 叫醒多個 wait thread(s)
1.	Semaphore (旗標): 只允許有限數量的 thread 執行某段程式. 再舉 FlashGet 的例子, 如果某個網站只限最多 3 threads download, 就可以用 Sempahore.

其它還有一些, Mutex, Monitor, SpinLock... 就不一一說明了, 直接去翻 OS 課本.. [H]

為什麼花這麼多篇幅講這個? 因為這短短一兩行的 code, 可是控制 thread pool 運作的重要關鍵. Thread Pool 需要一個 Queue 來存放待處理的工作. ThreadPool 同時也要 "養" 數個 threads 來處理掉 Queue 裡面的工作. 正常情況下每個 thread 忙完後就到 Queue 再拿一個工作出來, 如果 Queue 空了, thread 就可以休息 (blocked). 如果 Queue 有新工作進來, 這些睡著 (blocked) 的 thread 就應該要醒來繼續處理堆在 queue 裡的工作.

這是 Thread Pool 的基本型, 通常會用 thread pool 有幾個理由:

	1. 要處理的工作數量很多. 不可能用最古董的作法: 每個工作建一個 thread, 做完就丟掉...  (因為 thread create / delete, OS 是要花成本的, 同時 thread 太多也會造成效能及回應時間下降)
	1. 工作是不斷的持續的產生, 需要有 thread 事先在那邊等著接工作來做, 降低回應時間.
	1. 工作的性質適合以有限的 thread 來處理時


最典型的例子就是 ASP.NET. ASP.NET Hosting 會養一堆 thread, 來服務前方 IIS 送來的一堆 request. 即使 CPU 只有一顆, 多個 thread 也可以有降低回應時間的好處. 記得照 MSDN 的建議, 一個 CPU 建議值是開 25 threads 的樣子... 因此會有一些變型, 以求效能更好一點. 通常 thread 的建立 / 回收, 很花時間. 養一堆 thread 也很花資源. 因此考量的重點都放在怎樣才不會重複建立/回收 thread, 怎樣才不會養太多不工作的 thread ... 歸納一下:

	1. 現有 threads 不夠 (或未達上限), 而還有工作還卡在 Queue 裡沒人處理, 就建立新的 thread 加進來幫忙.
	1. 如果工作都做完了, 多餘的 thread 就可以讓它發呆. 發呆太久的 "宂員" 就可以把它 fired 了... 判定的依據一般都用 idle timeout. 當然也有不同的策略, 那就不管了.

看起來很囉唆, 其實想通之後, 就像 recursive 一樣, 寫起來很簡潔, 多寫兩行都會覺的累贅... 我把流程用假的 code 整理一下:

每個 thread 運作的 body 就像這樣:

```csharp
  while (true)
  {
      //
      //  從 queue 裡找 job 來做, 直到做完為止.
      //
   
      //
      //  idle.
      //
      if (超過IDLE時間 == true) break;
  }
```


另外, 就是把 Job 加到 Queue 裡的動作要像這樣:



```csharp
  //
  //  把 Job 加到 Queue
  //
   
  if (Job太多)
  {
      //
      //  多建立一些 thread 來幫忙
      //
  }
   
  if (有Idle的thread)
  {
      //
      //  叫醒 thread 來工作
      //
  }
```


上面兩段 code 關鍵就在如何讓 thread idle ? 如何判定 idle 超過某段時間? 另外就是如何叫醒 idle 的 thread? 答案其實就是用上面講的 synchronization 的機制來做. 這些 code 搞定後, 包裝在一起, thread pool 其實就完成了. 很簡單吧? 哈哈... 實際的 code 等下篇再說... 正好寫第二篇的時間, 就讓大家想一想到底該怎麼寫... [H], 敬請期待下集!