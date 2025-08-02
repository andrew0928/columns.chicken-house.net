---
layout: post
title: "[設計案例] 清除Cache物件 #2. Create Custom CacheDependency"
categories:
- "設計案例: 清除 Cache 物件"
tags: [".NET","C#","MSDN","Tips","技術隨筆","有的沒的","物件導向"]
published: true
comments: true
redirect_from:
  - /2009/12/19/設計案例-清除cache物件-2-create-custom-cachedependency/
  - /columns/post/2009/12/19/e8a8ade8a888e6a188e4be8b-e6b885e999a4Cachee789a9e4bbb6-2-Create-Custom-CacheDependency.aspx/
  - /post/2009/12/19/e8a8ade8a888e6a188e4be8b-e6b885e999a4Cachee789a9e4bbb6-2-Create-Custom-CacheDependency.aspx/
  - /post/e8a8ade8a888e6a188e4be8b-e6b885e999a4Cachee789a9e4bbb6-2-Create-Custom-CacheDependency.aspx/
  - /columns/2009/12/19/e8a8ade8a888e6a188e4be8b-e6b885e999a4Cachee789a9e4bbb6-2-Create-Custom-CacheDependency.aspx/
  - /columns/e8a8ade8a888e6a188e4be8b-e6b885e999a4Cachee789a9e4bbb6-2-Create-Custom-CacheDependency.aspx/
wordpress_postid: 22
---

上一篇廢話了這麼多，其實重點只有一個，我這次打算利用 CacheDependency 的機制，只要一聲令下，我想移除的 cache item 就會因為 CacheDependency 的關係自動失效，而不用很辛苦的拿著 cache key 一個一個移除。

我的想法是用 tags 的概念，建立起一套靠某個 tag 就能對應到一組 cache item，然後將它移除。開始之前先來想像一下 code 寫好長什麼樣子:

**透過 tags 來控制 cache items 的範例程式**

```csharp
static void Main(string[] args)
{
    string[] urls = new string[] {
        "http://columns.chicken-house.net/",
        // 共 50 組網址... 略
    };

    foreach (string url in urls)
    {
        DownloadData(new Uri(url));
    }

    Console.ReadLine();
    TaggingCacheDependency.DependencyDispose("funp.com");
    Console.ReadLine();
}

private static void Info(string key, object value, CacheItemRemovedReason reason)
{
        Console.WriteLine("Remove: {0}", key);
}

private static byte[] DownloadData(Uri sourceURL)
{
    byte[] buffer = (byte[])HttpRuntime.Cache[sourceURL.ToString()];

    if (buffer == null)
    {
        // 直接到指定網址下載。略...
        buffer = null;

        HttpRuntime.Cache.Add(
            sourceURL.ToString(),
            buffer,
            new TaggingCacheDependency(sourceURL.Host, sourceURL.Scheme),
            Cache.NoAbsoluteExpiration,
            TimeSpan.FromSeconds(600),
            CacheItemPriority.NotRemovable,
            Info);
    }

    return buffer;
}
}
```

 

這段 sample code 做的事很簡單，程式準備了 50 個網址清單，用 for-loop 一個一個下載。下載的 method: DownloadData(Uri sourceURL) 會先檢查 cache 是否已經有資料，沒有才真正下載 (不過下載的細節不是本篇要講的，所以就直接略過了...)。

而主程式的最後一行，則是想要把指定網站 ( funp.com ) 下載的所有資料，都從 cache 移除。為了方便觀看程式結果，我特地加上了 callback method, 當 cache item 被移除時, 會在畫面顯示資訊:

![image](/wp-content/be-files/WindowsLiveWriter/Cache2.CreateCustomCacheDependency/624B07FE/image.png)

由執行結果來看，果然被移出 cache 的都是來在 funp.com 的網址... 接著來看看程式碼中出現的 TaggingCacheDependecny 是怎麼實作的。相關的 code 如下:

**TaggingCacheDependency 的實作**

```csharp
public class TaggingCacheDependency : CacheDependency
{
    private static Dictionary<string, List<TaggingCacheDependency>> _lists = new Dictionary<string, List<TaggingCacheDependency>>();

    public TaggingCacheDependency(params string[] tags)
    {
        foreach (string tag in tags)
        {
            if (_lists.ContainsKey(tag) == false)
            {
                _lists.Add(tag, new List<TaggingCacheDependency>());
            }
            _lists[tag].Add(this);
        }
        this.SetUtcLastModified(DateTime.MinValue);
        this.FinishInit();
    }

    public static void DependencyDispose(string tag)
    {
        if (_lists.ContainsKey(tag) == true)
        {
            foreach (TaggingCacheDependency tcd in _lists[tag])
            {
                tcd.NotifyDependencyChanged(null, EventArgs.Empty);
            }
            _lists[tag].Clear();
            _lists.Remove(tag);
        }
    }
}
```

 

30 行不到... 其實程式很簡單，TaggingCacheDependency 繼承自 CacheDependency, 額外宣告一個靜態的 Dictionary<string, List<TaggingCacheDependency>> 來處理各個標簽及 TaggingCacheDependency 的關係，剩下的就沒什麼了。呼叫 DependencyDispose( ) 就可以通知 .NET Cache 機制，將相關的 cache item 移除。

用法很簡單，當你要把任何物件放進 cache 時，只要用 TaggingCacheDependency 物件來標示它的 tag:

**把物件加進 Cache, 配上 TaggingCacheDependency ...**

```csharp
HttpRuntime.Cache.Add(
    sourceURL.ToString(),
    buffer,
    new TaggingCacheDependency(sourceURL.Host, sourceURL.Scheme),
    Cache.NoAbsoluteExpiration,
    TimeSpan.FromSeconds(600),
    CacheItemPriority.NotRemovable,
    Info);
```

在這個例子裡 (line 4), 直接在 TaggingCacheDependency 物件的 constructor 上直接標上 tags, 在此例是直接把網址的 hostname, scheme 兩個部份當作 tag, 未來就可以依照這兩種資訊直接讓 cache 裡的相關物件失效。

而要下令讓 Cache 內有標上某個 tag 的 cache item 失效，只要這行:

**將標為 "funp.com" 的 cache item 設為失效的 cache item**

```csharp
TaggingCacheDependency.DependencyDispose("funp.com");
```

 

結果就會如同上面的程式範例一樣，還留在 cache 的該網址下載資料，在這一瞬間通通都會被清掉...

 

用這種方式，是不是比拿到 key 再去呼叫 Cache.Remove( key ) 的方式簡單多了呢? 同時也能夠更快速的處理複雜的移除機制。其實運用 tagging 的方式只是一例，需要的話你也可以設計合適的 CacheDependency 類別。

以下是本篇文章的兩個附加參考檔案:

Download File - [URL清單](/wp-content/be-files/WindowsLiveWriter/Cache2.CreateCustomCacheDependency/192B4E9C/tmp22EC.zip)

Download File - [Visual Studio 2008 Project](/wp-content/be-files/WindowsLiveWriter/Cache2.CreateCustomCacheDependency/32271EE1/tmpB405.zip)
