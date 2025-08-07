# [設計案例] 清除Cache物件 #2. Create Custom CacheDependency

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 .NET 中，要一次失效一整組快取 (cache) 資料，而不必逐一以 key 移除，有沒有更簡單的作法？
可以自訂一個 CacheDependency 類別，如文中的 TaggingCacheDependency，把相關快取物件透過「tag」分組；之後只要呼叫 TaggingCacheDependency.DependencyDispose(tag) 即可一次讓同一 tag 底下的所有 cache item 同步失效。

## Q: TaggingCacheDependency 在內部用什麼資料結構來對應 tag 與 CacheDependency 物件？
它使用  
Dictionary<string, List<TaggingCacheDependency>>  
這個靜態集合來維護「tag → 依賴物件清單」的對應關係。

## Q: 實際要把物件放進快取、並指定可被 tag 控制的依賴關係，程式碼該怎麼寫？
在呼叫 HttpRuntime.Cache.Add 時，把 TaggingCacheDependency 當作第三個參數傳入即可，例如：  
```csharp
HttpRuntime.Cache.Add(
    sourceURL.ToString(),          // cache key
    buffer,                        // 實際要快取的資料
    new TaggingCacheDependency(    // 依賴物件 (標上 tag)
        sourceURL.Host,            // 例：以 Host 當 tag
        sourceURL.Scheme),         // 例：再以 Scheme 當另一個 tag
    Cache.NoAbsoluteExpiration,
    TimeSpan.FromSeconds(600),
    CacheItemPriority.NotRemovable,
    Info);                         // 被移除時的 callback
```
如此一來，後續只要呼叫  
```csharp
TaggingCacheDependency.DependencyDispose("funp.com");
```  
便能一次移除所有 host 為 funp.com 的快取資料。