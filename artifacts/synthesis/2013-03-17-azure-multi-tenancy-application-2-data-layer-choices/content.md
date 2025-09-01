其實上一篇設計概念還沒寫完，只不過很晚了想睡覺就先貼了，本篇繼續..

之前介紹 MSDN 的那篇[文章](http://msdn.microsoft.com/en-us/library/aa479086.aspx)，作者很精確的分析了資料層面的三種設計方式。不過仔細研究之後，真正能搬上台面的，也只有最後一種 "Shared Schema" 而已。我從系統實際運作的角度，來分別考量這三種方式的可行性，各位就知道我為何這樣說了..。上篇介紹了各種可行的方案，這篇則會說明我認為的最佳方案。

我的看法很簡單，除非你的 Multi-Tenancy 的 "Tenancy" 規模只有幾十個的數量，否則 Separated DB / Separated Schema 都不適用，因為這兩種方式都是依賴把資料放在不同的 DB 或是 TABLE，來達到隔離的目的。並不是說這樣不好，而是這些都是 "過渡" 的作法，讓傳統的 application 不需要大符修改就能化身變為 Multi-Tenancy 的應用系統。而且 database / table 的數量都是有限制的，無法無限制的擴張。同時，以系統設計的角度來看，在系統執行的過程中，動態去建立 DB 或是建立 TABLE 也不是個很好的作法，在我眼裡都會覺的這是禁忌 XD。

當你辛辛苦苦建立了 SaaS 服務，總不可能只服務兩三隻小貓吧? 因此下列的分析會用使用量及 DB 各種功能的理論上限來做簡單的評估。Multi-Tenancy 的用戶數量，就抓個 50000 好了，至於每個用戶的 profile 我也依過去的經驗大致預估看看。依這些假設，就可以來評估各種資料層的處理方式，會有啥問題。

以下是一般的應用，每個用戶需要的資料規模 (假設):

| | 平均數量 |
|---|---|
| 資料表 (table) | 500 |
| 物件 (Sql obj, 如 table, view, trigger, function… etc) | 5000 |
| 資料筆數 (rows per table) | 100000 |
| 總容量 (data size) | 5GB |

# 1. 能容納的用戶量限制

以 SalesForce.com 為例，它會為每個 "公司" 開設一個專區，接著看該公司買了多少帳號，就開幾個 User Account。這裡的 "公司" 就是一個用戶，也就是 Multi-Tenancy 裡指的 "Tenancy"。這用戶的數量合理的數量應該是多少? 而系統的理論上限又是多少?

實際運作當然還有軟硬體搭配跟效能問題，這理就先就 "理論上限" 來探討。理論上限值，應該要在任何情況都足夠使用才合理。我特地去挖了 Microsoft SQL Server 的各種物件的數量上限，下表是從[官方資料](http://msdn.microsoft.com/en-us/library/ms143432.aspx) 整理出來的，以目前最新的 SQL 2012 為準，單一一套 SQL SERVER 可以:

| **數值名稱** | **最大上限** |
|---|---|
| Database size | 524272 TB |
| Databases per instance | **32767** |
| Instance per computer | 50 |
| Tables per database | 2147483647 (所有database objects總數上限) |
| User connections | **32767** |

看起來，最需要注意的就是 database 數量了。一套 SQL SERVER 最多只能開設3萬個database, 如果你採用 Separated DB 的作法，不論使用量為何，連同試用用戶，或是測試用戶在內，只能給三萬個用戶使用... 雖然不見得每個系統都會有這麼多用戶，不過一定會有不少熱門的應用會超出這樣的限制。

那第二種切割作法 (Separated Schema) 情況如何? SQL server 是以 database objects 的總數來計算的，包含 table, view, function, trigger 等等都算是 database object. 一個資料庫能容納 2G (20億) 個 database objects, 相當於能容納 400K (40萬) 個用戶。這數值比 Separated DB 的 3 萬好上一些... 在台灣，以公司為單位的服務，應該還沒有問題。若是以部門、團隊、或是家庭、社團設計的 application, 這樣的容量上限就需要耽心了。

Share Schema 則完全沒這些問題，只要儲存空間足夠，系統的效能能夠負耽，就沒有這種物理的上限限制了。

# 2. 效能擴充 (scale out) 的限制

如果考量到大型一點的規模，其實這三種方式都有困難。Separated DB 本身就已經是獨立DB，SQL server 本身執行的負擔就大很多，對於數量很多的用戶，但是每個用戶的人數都不多時，會浪費太多系統資源在執行這堆 DB 上面。不過相對的，這種架構很容易做 Scale Out 的擴充。

另一個要考量的是，雖然稱做 Multi-Tenancy, 但是總有些資料是要讓全部的用互共用吧? 這時這類資料就會變的很難處理，一個不小心就會動用到橫跨上千個 database 的 sql query ..

另一個極端的 Share Schema 做法就完全相反，沒有執行多個 DB 的負擔，執行起來效能是最好的。但是因為所有資料都塞在一起，很容易就面臨到單一 table 的資料筆數過大的問題。以這次的例子，一個用戶有10萬筆資料的話，隨便 1000 個用戶就有 1 億筆資料了... insert / delete / update 資料時，更新 index 的成本會變的很高。一般的查詢就會很吃力了，若是碰到沒寫好的 table join 會更想哭... 換句話說，這樣的架構規劃下，資料庫的最佳化非常的重要。因為你面臨到的就是大型資料庫效能調校問題..

再者，資料庫相對於 WEB 來說，是很不容易 Scale Out 的... 比較合適的作法是對資料庫做 Partition. 不過，這也不是件容易的事，已超出我的理解範圍了 XD，我只能說，要是老闆決定這樣做，那 $$ 決對是省不了的...

# 3. RDBMS 之外的選擇: Azure Table Store

前面講的，其實都是幾年前我在傷腦筋的問題。傳統的資料庫是為了資料的正確性及一致性而打造的儲存技術，過多的限制 (schema, constraint, relation…) 也限制了它無法有效 scale / partition 的特性。要徹底解決這些問題，不砍掉重練的話就只能花大錢及人力，來追上雲端服務的使用量了...。

不論是 Google, 或是 Microsoft Azure, 或是依據 Google 提出 MapReduce 而發展出來的 Hadoop, 都有處理巨量資料的能力。我就挑我最熟的 Azure 來說明。近幾年資料庫相關的技術，開始有了不一樣的變化。開始出現 "[NO SQL](http://en.wikipedia.org/wiki/NoSQL)" 的資料儲存方式。這種儲存方式有著跟 RDBMS 完全不一樣的特性，它比較簡單，主要是以 Key-Value 的型式來存取。因為 NO SQL 的結構比 RDBMS 簡單，因此能夠很容易的做到 scale out, 將單一資料庫，擴充到上千台 server 的規模。而 Azure 提供的 Table Storage, 則是將這種 NO SQL 的資料，跟 RDBMS 表格式的資料，做了一個很好的串接。

想瞭解 Azure 的細節，這輪不到我來說，市面上有幾本書很不錯，像是 MVC 小朱的[新書](http://books.gotop.com.tw/a_ACL036700)，或是大師 Lee Ruddy 的大作都很值得參考，若不介意看英文書，那選擇就更多了~，我就不在這多說太多了。但是 Azure Table Storage 有兩個很重要的特色，一定要講一下:

**1. PartitionKey / RowKey:**

老實說，這對 Multi-Tenancy 來說，是最完美的設計了。[這篇文章](http://robbincremers.me/2012/03/01/everything-you-need-to-know-about-windows-azure-table-storage-to-use-a-scalable-non-relational-structured-data-store/)講的很精闢，你要用 Azure Table Storage 的話一定要好好的研究 PartitionKey / RowKey, 因為我看過太多可笑的用法，實在糟蹋了這樣好的設計...。這篇文章前面講的都是howto, 最後一章是 "Why using Windows Azure Table Storage", 我截錄一段:

> *The storage system **achieves good scalability by distributing the partitions** across many storage nodes.*
> 
> *The system monitors the usage patterns of the partitions, and **automatically balances these partitions across all the storage nodes**. This allows the system and your application to **scale to meet the traffic needs** of your table. That is, if there is a lot of traffic to some of your partitions, the system will automatically spread them out to many storage nodes, so that the traffic load will be spread across many servers. However, a partition i.e. all entities with same partition key, will be served by a single node. Even so, the amount of data stored within a partition is not limited by the storage capacity of one storage node.*
> 
> *The entities within the same partition are stored together. This allows efficient querying within a partition. Furthermore, your application can benefit from efficient caching and other performance optimizations that are provided by data locality within a partition. **Choosing a partition key is important** for an application to be able to scale well. There is a tradeoff here between trying to benefit from entity locality, where you get efficient queries over entities in the same partition, and the scalability of your table, where the more partitions your table has the easier it is for Windows Azure Table to spread the load out over many servers.*

翻成白話，意思就是，開發人員只要慎選 partition key, 則 Azure 就會把同一個 partition 的資料放在同一個 node (不限於同一個 table 的 entities)。因此查詢會受惠於各種 cache 及 optimiaztion 機制，得到最佳效能。同時 Azure 也會自動依照 partition key 來分散到多個 node, 達到最佳的 scalability。

**2. Scalability Issues, and Query optimization issues**

另外，MSDN magazine 也有一篇值得一讀的[文章](http://msdn.microsoft.com/en-gb/magazine/ff796231.aspx)... "Windows Azure Table Storage – Not Your Father's Database" (中譯: 不是令北的資料庫… Orz), 一樣切重點出來:

> #### *PartitionKeys and RowKeys Drive Performance and Scalability*
> 
> *Many developers are used to a system of primary keys, foreign keys and constraints between the two. With Windows Azure Table storage, you have to let go of these concepts or you'll have difficulty grasping its system of keys.*
> 
> *In Windows Azure Tables, the string PartitionKey and RowKey properties work together as an index for your table, so when defining them, you must consider how your data is queried. Together, the properties also provide for uniqueness, acting as a primary key for the row. Each entity in a table must have a unique PartitionKey/RowKey combination.*

這篇就實際一點了，講到很多 Azure Table Storage 的特性，也帶出了設計時必需考慮的要點。因為設計理念不同，連帶的查詢時的限制 & 表現，跟傳統的 RDBMS 完全不同... 有沒有仔細規劃 partition key / row key, 決定了你的 query 效能的好壞。

除了內定的 partition key / row key 之外，其它 "欄位" 完全沒有任何的索引機制。這就是最需要顧慮的地方。實際上，Azure Table Storage 跟本就沒有 Schema 的設計，當然也沒有像 RDBMS 那樣的表格，反而是個典型的 Key-Value Pair 的 storage 而已。至於這些看起來像欄位的東西，完全是用 Code (TableEntity) 跟實際儲存的 Data (應該是 XML，或是類似的結構化 data) 變出來的東西。也因此，Query 完全需要良好的規劃才能有好的表現。

若各位對 Azure Table Storage 的 Query 技巧有興趣，這段 [VIDEO](http://www.microsoftpdc.com/2009/svc09) 很值得一看。這是 2009 PDC 的一個場次: "Windows Azure Tables and Queues Deep Dive", 講到很多 Query 的技巧..

再回到[前面那篇參考文章](http://robbincremers.me/2012/03/01/everything-you-need-to-know-about-windows-azure-table-storage-to-use-a-scalable-non-relational-structured-data-store/)，最後作者也列了一些缺點及建議，強烈建議各位在決定採用 Azure Table Storage 前要認真閱讀:

> *Windows Azure table storage is designed for high scalability, but there are some **drawbacks** to it though:*
> 
> - *There is no possibility to sort the data through your query. The data is being sorted by default by the partition and row key and that's the only order you can retrieve the information from the table storage. This can often be a painful issue when using table storage. Sorting is apparently an expensive operation, so for scalability this is not supported.*
> - *Each entity will have a primary key based on the partition key and row key*
> - *The only clustered index is on the PartitionKey and the RowKey. That means if you need to build a query that searches on another property then these, performance will go down. If you need to query for data that doesn't search on the partition key, performance will go down drastically. With the relational database we are used to make filters on about any column when needed. With table storage this is not a good idea or you might end up with slow data retrieval.*
> - *Joining related data is not possible by default. You need to read from seperate tables and doing the stitching yourself*
> - *There is no possibility to execute a count on your table, except for looping over all your entities, which is a very expensive query*
> - *Paging with table storage can be of more of a challenge then it was with the relational database*
> - *Generating reports from table storage is nearly impossible as it's non-relational*
> 
> *If you can not manage with these restrictions, then Windows Azure table storage might not be the ideal storage solution. **The use of Windows Azure table storage is depending on the needs and priorities of your application**. But if you have a look at how large companies like Twitter, Facebook, Bing, Google and so forth work with data, you'll see they are moving away from the traditional relational data model. **It's trading some features like filtering, sorting and joining for scalability and performance**. The larger your data volume is growing, the more the latter will be impacted.*

看起來蠻恐佈的，由於架構的不同，Azure Table Storage 無法題供像 RDBMS 那樣多樣化的查詢能力，除了 partition key / row key 之外，甚至連 RDBMS 最基本的 index 都沒有，這也導至這篇的作者連這點也列入缺點 "*Generating reports from table storage is nearly impossible as it's non-relational*" ...

不過，實際的狀況其實沒這麼嚴重。Azure Table Storage 極為強大的 scalability 可以彌補查詢上的不足，平行的查詢，及針對巨量資料的設計，都是你在處理巨量資料的武器，而這些是 RDBMS 所無法提供的。

寫到這裡，我簡單下個結論。Azure Table Storage, 是個很棒的 "storage", 有絕佳的延申及擴充能力。能夠輕易的儲存及處理巨量資料，不論是資料大小或是資料筆數都一樣。不過它畢竟不是 "R"DBMS，而是 NO SQL這一類的 storage, 因此在執行覆雜的 QUERY 上不是 RDBMS 的對手。一些統計方面的功能 (如 SUM, COUNT, AVERAGE …. 等等) 就更不用說了。這部份得靠 ORM、Linq 及你的程式來補足。

而 Azure Table Storage 的規劃就將 partition 的機制放進去了，拿來做 Multi-Tenancy 的資料切割機制真是絕配! 跟本就是為了這樣的應用而設計的... 下一篇我會示範實際的程式碼，用 Azure Table Storage 來實作 Multi-Tenancy Applicaion 的 Data Layer ..