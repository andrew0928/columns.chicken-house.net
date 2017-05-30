---
layout: post
title: "ThreadPool 實作 #3. AutoResetEvent / ManualResetEvent"
categories:
- "系列文章: Thread Pool 實作"
tags: [".NET","作業系統","多執行緒","技術隨筆"]
published: true
comments: true
permalink: "/2007/12/17/threadpool-實作-3-autoresetevent-manualresetevent/"
redirect_from:
  - /columns/post/2007/12/17/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent-ManualResetEvent.aspx/
  - /post/2007/12/17/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent-ManualResetEvent.aspx/
  - /post/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent-ManualResetEvent.aspx/
  - /columns/2007/12/17/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent-ManualResetEvent.aspx/
  - /columns/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent-ManualResetEvent.aspx/
  - /columns/post/2007/12/17/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent--ManualResetEvent.aspx/
  - /post/2007/12/17/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent--ManualResetEvent.aspx/
  - /post/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent--ManualResetEvent.aspx/
  - /columns/2007/12/17/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent--ManualResetEvent.aspx/
  - /columns/ThreadPool-e5afa6e4bd9c-3-AutoResetEvent--ManualResetEvent.aspx/
  - /blogs/chicken/archive/2007/12/17/2894.aspx/
wordpress_postid: 128
---

續上篇, 從眾多閒置的 worker thread 挑選一個起來接工作有兩種策略作法. 一種作法是 Thread Pool 自己決定, 最基本的就是誰等最久就叫誰起來, 或是 Thread Pool 有自己的演算法挑一個最菜的 worker thread 來做工都可以... 另一種作法就是不管它, 每個 worker thread 都靠運氣, 交給上天 (OS) 決定, 看誰搶到下一個 job. 看起來第一種好像比較好, 事實上不見得. 每個 thread 之間的排程是個學問, OS 多工的效率好不好就看這個. 舉例來說, 如果每個 worker thread 的優先順序不同, 或是某些 thread 正好碰到 GC, 或是正好被移到 virtaual memory 等等, 硬去叫它起來工作反而要花更多的時間. 而這些資訊都在 OS 的排程器裡才有足夠的資訊可以判斷, 以寫 AP 的角度很難顧級到這個層面. 這時最好的辦法就是不管它, 用齊頭式的平等, 把選擇權交給 OS 決定.

又是一個說起來比 code 多的例子. 這兩種不同的策略, 寫成 code 其實只差一行... 就是選用 AutoResetEvent 跟 ManualResetEvent 的差別而以. .NET SDK 的 Class Reference 上這樣寫著:

> AutoResetEvent: Notifies **a** waiting thread that an event has occurred.
> ManualResetEvent: Notifies **one or more** waiting threads that an event has occurred.

真正寫成 Code 來測試一下... 

```csharp
static void Main(string[] args)
{
    for (int count = 0; count < 5; count++)
    {
        Thread t = new Thread(new ThreadStart(ThreadTest));
        t.Start();
    }
    Thread.Sleep(1000);
    wait.Set();
    Thread.Sleep(1000);
    wait.Set();
    Thread.Sleep(1000);
    wait.Set();
    Thread.Sleep(1000);
    wait.Set();
    Thread.Sleep(1000);
    wait.Set();
}
 
private static AutoResetEvent wait = new AutoResetEvent(false);

private static void ThreadTest()
{
    Console.WriteLine("Thread[{0}]: wait...", Thread.CurrentThread.ManagedThreadId);
    wait.WaitOne();
    Console.WriteLine("Thread[{0}]: wakeup...", Thread.CurrentThread.ManagedThreadId);
}
```




執行結果:

```text
Thread[ 3 ]: wait...
Thread[ 5 ]: wait...
Thread[ 4 ]: wait...
Thread[ 6 ]: wait...
Thread[ 7 ]: wait...
Thread[ 3 ]: wakeup...
Thread[ 4 ]: wakeup...
Thread[ 6 ]: wakeup...
Thread[ 5 ]: wakeup...
Thread[ 7 ]: wakeup... 
```




程式過程中我加了幾個 Sleep, 首先我用同一個 AutoResetEvent, 讓五個 thread 都去等待同一個 notify event 來叫醒它. 而 AutoResetEvent 一次只能叫醒一個被 WaitOne blocked 住的 thread. 就是第一種先到先贏的作法, 後面幾行 wakeup 的 message 每隔一秒會跳一行出來.


再來看一下 ManualResetEvent ...


```csharp
static void Main(string[] args)
{
    for (int count = 0; count < 5; count++)
    {
        Thread t = new Thread(new ThreadStart(ThreadTest));
        t.Start();
    }
 
    Thread.Sleep(1000);
    wait.Set();
}
 
private static ManualResetEvent wait = new ManualResetEvent(false);

private static void ThreadTest()
{
    Console.WriteLine("Thread[{0}]: wait...", Thread.CurrentThread.ManagedThreadId);
    wait.WaitOne();
    Console.WriteLine("Thread[{0}]: wakeup...", Thread.CurrentThread.ManagedThreadId);
}
```



執行結果:
```text
Thread[ 3 ]: wait...
Thread[ 4 ]: wait...
Thread[ 5 ]: wait...
Thread[ 6 ]: wait...
Thread[ 7 ]: wait...
Thread[ 5 ]: wakeup...
Thread[ 4 ]: wakeup...
Thread[ 6 ]: wakeup...
Thread[ 3 ]: wakeup...
Thread[ 7 ]: wakeup... 
```

除了把型別宣告從 AutoResetEvent 換成 ManualResetEvent 之外, 其它都沒變. 當然 line 10 一次就能叫醒所有的 thread, 所以後面四次 Set( ) 我就直接刪掉了. 程式 run 到 line 10, 後面五行 wakeup 的訊息就會一次全出現, 而出現的順序是隨機的, 每次都不大一樣.

這種作法的解釋, 是一次 Set( ), 卡在 WaitOne( ) 的五個 thread 就全被叫醒了. 而這個現象如果套用在 SimpleThreadPool 的實作上, 它的作用相當於第二種作法. 一瞬間把所有的 worker thread 從 blocked 狀態移到 waiting 狀態. 而到底是那一個 thread 有幸第一個被 OS 移到 running 狀態? 就是根據 OS 自己的排程策略而定. 第一個移到 running 狀態的 thread 通常就能搶到 job queue 裡的工作, 剩下的沒搶到, 則又會因為沒有工作好做, 再度進入閒置狀態, 等待下一次機會再一起來碰一次運氣...

就這一行, 花了最多篇幅來說明, 因為它最抽象. 說明這段的目的, 如果你的 ThreadPool 要更進階一點, 如果你想要改用先排隊先贏的策略, 把 WaitHandle 的型別改成 AutoResetEvent 就好. 如果你希望根據工作的特性來微調每個 thread 的 priority, 你就必需用 ManualResetEvent.

好, 沒想到一百行左右的 SimpleThreadPool 有這麼多東西可以寫, 完整的 code 我直接貼在底下, 歡迎引用. 好用的話記得給個回應. 要用在你的 project 也歡迎, 只要禮貌性的支會我一聲. 讓我知道我寫的 code 被用在什麼地方就好. 寫到這裡總算告一段落. 謝謝收看 [:D] 

--
完整的 SimpleThreadPool.cs 原始碼:


```csharp
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Diagnostics;
 
namespace ChickenHouse.Core.Threading
{
    public class SimpleThreadPool : IDisposable
    {
        private List<Thread> _workerThreads = new List<Thread>();
 
        private bool _stop_flag = false;
        private bool _cancel_flag = false;
 
        private TimeSpan _maxWorkerThreadTimeout = TimeSpan.FromMilliseconds(3000);
        private int _maxWorkerThreadCount = 0;
        private ThreadPriority _workerThreadPriority = ThreadPriority.Normal;
 
        private Queue<WorkItem> _workitems = new Queue<WorkItem>();
        private ManualResetEvent enqueueNotify = new ManualResetEvent(false);
 
        public SimpleThreadPool(int threads, ThreadPriority priority)
        {
            this._maxWorkerThreadCount = threads;
            this._workerThreadPriority = priority;
        }
 
        private void CreateWorkerThread()
        {
            Thread worker = new Thread(new ThreadStart(this.DoWorkerThread));
            worker.Priority = this._workerThreadPriority;
            this._workerThreads.Add(worker);
            worker.Start();
        }
 
        public bool QueueUserWorkItem(WaitCallback callback)
        {
            return this.QueueUserWorkItem(callback, null);
        }
 
        public bool QueueUserWorkItem(WaitCallback callback, object state)
        {
            if (this._stop_flag == true) return false;
 
            WorkItem wi = new WorkItem();
            wi.callback = callback;
            wi.state = state;
 
            if (this._workitems.Count > 0 && this._workerThreads.Count < this._maxWorkerThreadCount) CreateWorkerThread();
 
            this._workitems.Enqueue(wi);
            this.enqueueNotify.Set();
 
            return true;
        }
 
        public void EndPool()
        {
            this.EndPool(false);
        }
 
        public void CancelPool()
        {
            this.EndPool(true);
        }
 
        public void EndPool(bool cancelQueueItem)
        {
            if (this._workerThreads.Count == 0) return;
 
            this._stop_flag = true;
            this._cancel_flag = cancelQueueItem;
            this.enqueueNotify.Set();
 
            do
            {
                Thread worker = this._workerThreads[0];
                worker.Join();
                this._workerThreads.Remove(worker);
            } while (this._workerThreads.Count > 0);
        }
 
        private void DoWorkerThread()
        {
            while (true)
            {
                while (this._workitems.Count > 0)
                {
                    WorkItem item = null;
                    lock (this._workitems)
                    {
                        if (this._workitems.Count > 0) item = this._workitems.Dequeue();
                    }
                    if (item == null) continue;
 
                    try
                    {
                        item.Execute();
                    }
                    catch (Exception)
                    {
                        //
                        //  ToDo: exception handler
                        //
                    }
 
                    if (this._cancel_flag == true) break;
                }
 
                if (this._stop_flag == true || this._cancel_flag == true) break;
                if (this.enqueueNotify.WaitOne(this._maxWorkerThreadTimeout, true) == true) continue;
                break;
            }
 
            this._workerThreads.Remove(Thread.CurrentThread);
        }
 
        private class WorkItem
        {
            public WaitCallback callback;
            public object state;
 
            public void Execute()
            {
                this.callback(this.state);
            }
        }
 
        public void Dispose()
        {
            this.EndPool(false);
        }
    }
}
```