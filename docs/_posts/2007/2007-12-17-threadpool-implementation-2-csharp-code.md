---
layout: post
title: "ThreadPool 實作 #2. 程式碼 (C#)"
categories:
- "系列文章: Thread Pool 實作"
tags: [".NET","作業系統","多執行緒","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2007/12/17/threadpool-實作-2-程式碼-c/
  - /columns/post/2007/12/17/ThreadPool-e5afa6e4bd9c-2-e7a88be5bc8fe7a2bc-(C).aspx/
  - /post/2007/12/17/ThreadPool-e5afa6e4bd9c-2-e7a88be5bc8fe7a2bc-(C).aspx/
  - /post/ThreadPool-e5afa6e4bd9c-2-e7a88be5bc8fe7a2bc-(C).aspx/
  - /columns/2007/12/17/ThreadPool-e5afa6e4bd9c-2-e7a88be5bc8fe7a2bc-(C).aspx/
  - /columns/ThreadPool-e5afa6e4bd9c-2-e7a88be5bc8fe7a2bc-(C).aspx/
  - /blogs/chicken/archive/2007/12/17/2893.aspx/
wordpress_postid: 129
---

既然上一篇都把 pseudo code 寫出來了, 現在就可以開始來寫真正的 Thread Pool 了. 開始之前, 我先把目標定一下. 這次寫的 Thread Pool 必需俱備這些能力:

1. 要能由使用者控制 thread pool 的組態:
- worker thread 數量上限
- worker thread 優先權
- thread idle timeout 時間 (超過 idle timeout, 代表 thread 是宂員, 可以下台了)
- job queue 安全範圍 (超過代表需要找幫手 - 建立新的 worker thread)
1. thread pool 在 job queue 超過安全範圍時, 要能動態建立新的 thread 來消化 queue 裡的工作
1. worker thread 在 idle 時間超過 idle timeout 時, 則這個 worker thread 就要被回收
1. 簡單的同步機制, 要能等待 thread pool 處理完所有的 job.
1. 如果有多個 worker thread 要搶同一個 job 來執行, 要由 OS 決定, 不要由 thread pool 自己決定

每次在寫這些描述, 都會覺的怎麼寫起來比 code 還多... @_@, 沒錯, code 短到我可以直接貼上來, 不需要附檔案.. 我會把完整的 code 貼在最下方. 其它說明的部份只會貼片段.

首先, 先來決定 SimpleThreadPool 的 class define 為何. 依照需求及我希望它用起來的樣子, 為:




```csharp
public class SimpleThreadPool : IDisposable
{
	public SimpleThreadPool(int threads, ThreadPriority priority)
	{
	}

	public bool QueueUserWorkItem(WaitCallback callback)
	{
	}

	public bool QueueUserWorkItem(WaitCallback callback, object state)
	{
	}

	public void EndPool()
	{
	}

	public void CancelPool()
	{
	}

	public void EndPool(bool cancelQueueItem)
	{
	}

	private void DoWorkerThread()
	{
	}

	public void Dispose()
	{
		this.EndPool(false);
	}

	// 略...

```




這個 ThreadPool 我希望它用起來像這樣, 貼一段理想中的用法 sample code:


```csharp
SimpleThreadPool stp = new SimpleThreadPool(2, System.Threading.ThreadPriority.BelowNormal);

for (int count = 0; count < 25; count++)
{
    stp.QueueUserWorkItem(
        new WaitCallback(ShowMessage),
        string.Format("STP1[{0}]", count));
    Thread.Sleep(new Random().Next(500));
}
Console.WriteLine("wait stop");
stp.EndPool();
```  




把 ```ThreadPool``` 想像成一個服務櫃台, 很多人排隊等著處理. 因此整個實作會像是個工作的佇列 (job queue), 只要把你的工作放到 queue 裡 (排隊), 而服務人員 (worker thread) 就會一個一個的處理. 最後你可以決定要把所有工作做完才收攤 (呼叫 ```EndPool()```, 會 blocked 直到工作清光), 或是決定掛牌 "明日請早" (呼叫 ```CancelPool()```), 只把作到一半的工作處理掉, 剩下還在排隊的改天再來. 


整個實作的關鍵部份是在 ```private void DoWorkerThread()```, 裡面寫的 code 就是每一個 worker thread 要執行的所有內容. 補上實作的 code:




```csharp
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
```


每個 worker thread 就只作很簡單的一件事, 就是進入無窮迴圈, 只要開始上班就不段的接工作來處理, 一直到下班為止. 整個最外層的 while loop 就是指這部份. 離開 loop 後就代表這個 worker thread 該下班了.

迴圈內也很簡單, 上工的第一件事就是看 job queue 裡有沒有工作要做? 有就 dequeue 一個來處理, 一直重複到 job queue 空了為止, 或是直到老闆下令關店 (```_cancel_flag``` 為 true).

無論是要關店或是工作做完了, 流程會跳離 line 6 ~ 27 這個 while loop. 後序的關鍵在 line 30:

```csharp
if (this.enqueueNotify.WaitOne(this._maxWorkerThreadTimeout, true) == true) continue;
```


呼叫 ```WaitHandle``` 的 ```WaitOne( )``` method, 會讓 worker thread 進入 blocked 狀態. 直到被叫醒為止 (叫醒它的 code 寫在 add queue 裡), 或是 idle timeout 時間到了. .NET API ```WaitHandle.WaitOne( )``` 提供 option 指定 timeout 時間, 至於是被叫醒的 or 時間到了自己醒來, 就靠 return value 來判定. 以這段 code 來看, 被叫醒 (return true) 代表有新工作進來, 就執行 continue 指令, 繼續到 job queue 拿新的工作繼續努力, 如果是睡太飽自己醒的, 就執行 break, 準被收拾東西下班去...

整個 worker thread 的生命周期就是靠這段 code 來運作. 接下來看一下如何把 job 加進來:

```csharp
private List<Thread> _workerThreads = new List<Thread>();
private Queue<WorkItem> _workitems = new Queue<WorkItem>();
private ManualResetEvent enqueueNotify = new ManualResetEvent(false);
 
public bool QueueUserWorkItem(WaitCallback callback, object state)
{
    if (this._stop_flag == true) return false;
 
    WorkItem wi = new WorkItem();
    wi.callback = callback;
    wi.state = state;
 
    if (this._workitems.Count > 0 && this._workerThreads.Count < this._maxWorkerThreadCount) this.CreateWorkerThread();
 
    this._workitems.Enqueue(wi);
    this.enqueueNotify.Set();
 
    return true;
}
```




扣掉一大半準備 WorkItem 的 code 之外, 剩下的就是把 workitem 加到 queue 裡了. 兩個關鍵的地方是:

```csharp
if (this._workitems.Count > 0 && this._workerThreads.Count < this._maxWorkerThreadCount) this.CreateWorkerThread();
```



如果 job queue 堆的工作超過 0 個, 而總共的 worker thread 數量還沒超過上限, 就呼叫 ```CreateWorkerThread( )``` 再叫一個 worker thread 來幫忙.


line 14 把 work item 加到 queue 之後, line 15 就緊接著呼叫 ```WaitHandle.Set( )```, 通知所有正卡在 ```WaitOne( )``` 睡覺中的 worker thread 該醒來工作了. 其實到這裡, thread pool 主要結構都說明完了, 剩下的都是細部實作, 比如如何封裝 job 的物件, 如何得知共有幾個 worker thread 等等, 這些直接看 code 比較快我就不多說明了. 搭配前一篇, 提到有各種 synchrinization 機制可以使用, 這裡我用的是 ```ManualResetEvent```, 為什麼要挑這個? 先弄清楚觀念上的問題: 假設有五個 worker thread 都睡著等待新的工作進來, 這時只有一個新的工作進來, 到底是誰該醒來作事? 是由誰決定?



說明起來又是一大篇了... 改寫第三篇再繼續吧!
