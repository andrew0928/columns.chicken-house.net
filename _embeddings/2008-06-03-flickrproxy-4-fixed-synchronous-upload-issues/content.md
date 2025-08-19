---
layout: post
title: "FlickrProxy #4 - 修正同步上傳的問題"
categories:
- "作品集: FlickrProxy"
tags: [".NET","ASP.NET","作品集"]
published: true
comments: true
redirect_from:
  - /2008/06/03/flickrproxy-4-修正同步上傳的問題/
  - /columns/post/2008/06/03/FlickrProxy-4-e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /post/2008/06/03/FlickrProxy-4-e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /post/FlickrProxy-4-e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /columns/2008/06/03/FlickrProxy-4-e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /columns/FlickrProxy-4-e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /columns/post/2008/06/03/FlickrProxy-4---e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /post/2008/06/03/FlickrProxy-4---e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /post/FlickrProxy-4---e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /columns/2008/06/03/FlickrProxy-4---e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /columns/FlickrProxy-4---e4bfaee6ada3e5908ce6ada5e4b88ae582b3e79a84e5958fe9a18c.aspx/
  - /blogs/chicken/archive/2008/06/03/3261.aspx/
wordpress_postid: 103
---

寫到這，越寫越拖抬了... 這次沒有加上任何 "新功能"，有的只是修正使用上的一些問題而以...

首先，還是要感謝愛用者 [小熊子](http://michadel.chicken-house.net/blogs/michadel/default.aspx) 的回報，照片初次被下載時會觸發上傳到 Flickr 的動作，上傳完成才重新引導 Request 到 Flickr 存取照片。如果在這一連串動作尚未完成前，就有第二個 Request 跑來的話，那這張照片就會被傳到 Flickr 兩次...。Orz，枉費我還[投搞](/wp-content/be-files/archive/tags/RUNPC/default.aspx)這些並行處理的文章，怎麼可以犯這種錯...

就跟很多 BUG 一樣，難在沒想到，難在沒發現，難在不知道原因...，不然修正 BUG 倒是很簡單的事，感謝回報這個 BUG 的[恩公](http://michadel.chicken-house.net/blogs/michadel/default.aspx)... 找到問題後剩下的 ISSUE 就迎刃而解了，要做的就是把關鍵的程式碼包裝在臨界區 ([CRITICAL SECTION](http://en.wikipedia.org/wiki/Critical_section)) 內，以防這段 CODE 同時間執行多次。這段 CODE 不能太大，鎖定範圍太大會影響效能 (好不容易換了[四核CPU](/post/Next-Ten-Years.aspx)，鎖太大就糟踏這顆 CPU 了...)，最後找出關鍵應該是 [判定是否需要上傳到 FLICKR] 及 [建立 FLICKR 副本檔] 這兩個動作，一定要包括在內，拆開的話就不能保證結果正確了。

**修正過的程式，加上 LOCK 鎖定部份程式碼**

```csharp
string flickrURL = null;
lock (this.GetType())
{
    if (File.Exists(this.CacheInfoFile) == false)
    {
        //
        //  CACHE INFO 不存在，重新建立
        //
        this.BuildCacheInfoFile(context);
        context.Response.AddHeader("X-FlickrProxy", "Upload");
    }
}
```

寫好後，這段 CODE 越看越不順眼，雖然我的網站流量沒那麼大啦 [H]，不過怎麼可以這麼短視... 這段 CODE 的問題還是一樣，鎖定的範圍 "太大了" !! 會嚴重影響效能.. (如果流量真的很大的話)

怎麼說? 不過才兩行，那到底是要縮到多小? 不不，問題其實不在於 LOCK 的區段到底有多少 CODE，而是該 LOCK 的只有對同一張照片的 Http Request 才該被阻檔下來，同時間有多個 Http Request 來下載不同張照片，以現在的點閱率來說我應該要高興吧... 幹嘛還去 LOCK 它? 不過上面的 CODE 就是在做這件事，不分青紅皂白只要是有上傳到 FLICKR 的動作就一率 LOCK。更糟的是如果有一張照片正在上傳中，其它照片的 Http Request 也都會被迫停下來等它傳完...

該要有個改進的版本了。LOCK過度也是初次碰到 Multi-threading Programming 的人很容易犯的錯誤，接下來看看第二個版本:

**修正過的版本，只會LOCK同一個檔案的REQUEST:**

```csharp
lock (this.LockHandle)
{
    if (File.Exists(this.CacheInfoFile) == false)
    {
        //
        //  CACHE INFO 不存在，重新建立
        //
        this.BuildCacheInfoFile(context);
        context.Response.AddHeader("X-FlickrProxy", "Upload");
    }
}
```

看起來只有第一行 LOCK STATEMENT 裡指定的物件不一樣而以。沒錯，這裡跟第一段 CODE 的差別只在於 LOCK 的標的物不一樣。同一個物件只能被 LOCK 一次，當物件被 LOCK 還沒放開時，第二個人想要 LOCK 同一個物件，很抱歉... 得先等第一個人願意放掉它才可以。LOCK不同物件就各不相干了。沒錯，這就是我要的邏輯。所以這個問題的關鍵在於，我如何讓每張照片有專屬的 "物件" 來 LOCK ?

檔名的字串物件? 不適合... 可能有多個字串值相同，但是是不同物件... FileInfo? 也不行，因為找不到文件會保證同一個檔案拿到的 FileInfo 物件會是同一個... 沒辦法，只好自己弄一個。來看一下 LockHandle 的實作:

**LockHandle Property 實作的程式碼**

```csharp
private object LockHandle
{
    get
    {
        string hash = this.GetFileHash();
        lock (_locks)
        {
            if (_locks.ContainsKey(hash) == false)
            {
                _locks.Add(hash, new object());
            }
        }
        return _locks[hash];
    }
}
private static Dictionary<string, object> _locks = new Dictionary<string, object>();
```

其實以值來說，拿檔名就足夠拿來示別了，只不過有大小寫的問題要處理。拿檔案的內容做 MD5 實在有點殺雞用牛刀，不過因為處理照片本來就需要算檔案的 MD5 了，現成的就拿來用一下...。這裡我簡單的做了個 Dictionary，就放沒什麼用的 OBJECT，我只要這個 PROCESS 在有生之年，同一個檔案都會拿到同一個 OBJECT 就足夠了...

都寫到這還有什麼不滿意的? 還是有... 哈哈。因為我在測試時有過一個頁面，同一頁會放一堆圖檔...。試想一下當我瀏覽這頁面會發生什麼事?

"同時間 IE 發出了數個 HttpRequest 來跟我的程式要圖檔，如果正巧都是第一次，嗯，有限的頻寬要一次上傳多張圖檔到 Flickr，不就更慢了?"

就算我的頻寬沒問題，同一瞬間這麼多 UPLOAD 的動作，引起 Flickr 的 "關切" 就不好了... 我是不是應該要限制一下同時上傳的數量才對? 就像 FlashGet 可以限制同時下載的數量一樣...

哈，不就是之前寫過的文章，用 SEMAPHORE ? 沒錯... 怎麼老覺的這篇像在替我其它文章打廣告用的... 事實上不見得要動用到 SEMAPHORE，如果你要限制的是一次只能一個 UPLOAD 動作，直接用各種的 LOCK 機制就夠了。如果你要限制並行的 UPLOAD 動作是兩個以上，甚至更動態隨著 LOADING 變化等等，才需要動用到 SEMAPHORE ...

既然要 DEMO，就 DEMO 實際一點的 CODE 吧。假設我要限制並行 UPLOAD 的數量不超過 2 個，則需要把 CODE 改成這樣。首先要先準備好 SEMAPHORE 物件:

**準備 SEMAPHORE，事先插好兩根旗子**

```csharp
public static Semaphore FlickrUploaderSemaphore = new Semaphore(2, 2);
```

真正執行上傳動作的部份要加上 SEMAPHORE 的管控:

**用 SEMAPHORE 控制同步執行的數量**

```csharp
FlickrUploaderSemaphore.WaitOne();
photoID = flickr.UploadPicture(this.FileLocation);
FlickrUploaderSemaphore.Release();
```

嗯，真是小題大作，不過這種機會不拿來練習練習，真正碰到怎麼寫的出來? 如果各位對於在 ASP.NET 上怎麼使用 LOCK 及 SEMAPHORE 不大熟的，可以參考一下我[投稿](/wp-content/be-files/archive/tags/RUNPC/default.aspx)的文章... 萬分感謝 [:D]
