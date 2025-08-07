# [設計案例] 清除Cache物件 #1. 問題與作法

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 要如何手動將某個物件從 .NET HttpRuntime 的 Cache 移除?
使用 Remove 方法即可，一行程式就能完成：  
```csharp
HttpRuntime.Cache.Remove("cache-key");
```

## Q: 如果想知道目前 Cache 內所有的 key，該怎麼取得?
Cache 物件沒有提供 Keys 屬性，需要透過 GetEnumerator 迭代：  
```csharp
foreach (string key in HttpRuntime.Cache) {  
    // ...  
}
```

## Q: 直接記錄 key 或逐一列舉 key 來批次清除 Cache，有哪些實務上的困難?
1. 必須額外維護所有 key，資料量大時程式碼易混亂。  
2. 列舉大量 cache 物件效能不佳，而且在列舉過程中項目可能已被移除。  
3. 整體程式可讀性與維護性都會下降，不符合高效又優雅的設計需求。

## Q: 在「瀏覽器快取」情境下，如果想只刪除某網站、某 content-type 或某 protocol 的快取，用傳統做法會遇到什麼缺點?
1. 需要自行維護所有已下載 URL 的清單並比對，等同重做一套 cache。  
2. 或是每次從 Cache 取出所有 key，再用正規表示式篩選，效率低且程式碼冗長。  
3. 兩種做法都無法保證列舉到的項目仍存在，邏輯複雜且效能差。

## Q: 作者提出了哪種「聰明又愚蠢」的方法來批次清除相關的 Cache 物件?
先依需求將 cache item 分群，讓每一群都關聯到同一個檔案 (以 CacheDependency 建立依賴)。  
當需要清除該群物件時，只要 touch 一下這個檔案，整組 cache 物件就會被自動移除。

## Q: 這個方法為什麼被說是既聰明又愚蠢?
• 聰明：能優雅地一次清掉整群相關 cache 物件，不必逐一記錄和移除 key。  
• 愚蠢：為了純程式內可解決的事，額外引入檔案 I/O，速度較慢且多了外部依賴。

## Q: Cache 物件與一般 Dictionary 有何差異，為什麼不能直接用 Keys 屬性?
Cache 類型雖是典型的 Key-Value 容器，但未實作 IDictionary 介面，因此沒有 Keys 屬性；必須透過 GetEnumerator 來巡覽其中的 key。