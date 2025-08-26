---
layout: post
title: "難搞的 Entity Framework - 跨越 Context 的查詢"
categories:

tags: [".NET","C#", "Entity Framework"]
published: true
comments: true
redirect_from:
  - /2009/01/20/難搞的-entity-framework-跨越-context-的查詢/
  - /columns/post/2009/01/20/e99ba3e6909ee79a84-Entity-Framework-e8b7a8e8b68a-Context-e79a84e69fa5e8a9a2.aspx/
  - /post/2009/01/20/e99ba3e6909ee79a84-Entity-Framework-e8b7a8e8b68a-Context-e79a84e69fa5e8a9a2.aspx/
  - /post/e99ba3e6909ee79a84-Entity-Framework-e8b7a8e8b68a-Context-e79a84e69fa5e8a9a2.aspx/
  - /columns/2009/01/20/e99ba3e6909ee79a84-Entity-Framework-e8b7a8e8b68a-Context-e79a84e69fa5e8a9a2.aspx/
  - /columns/e99ba3e6909ee79a84-Entity-Framework-e8b7a8e8b68a-Context-e79a84e69fa5e8a9a2.aspx/
wordpress_postid: 45
---

咳，沒錯... 兩個月都沒寫什麼東西出來，就是都在研究 Entity Framework 跟 Enterprise Library... Enterprise Library 倒還好，看看範例，看看 Key Scenario 大概就能入門了，不過 Entity Framework 就沒這麼簡單...

Microsoft 對 Entity Framework 的 Roadmap 規劃的很大，不過再怎麼樣附在 .NET 3.5 SP1 的也還只是第一版而已。背負著龐大的架構，而現在卻還不一定能拼過其它成熟的 ORM solution, 這就是辛苦的地方。

先抱怨一下它的設計工具... 好用是蠻好用的 (跟直接寫 XML 檔相比)，不過小問題還不少。像是 TABLE 拉進去，刪掉再拉進去，就有機會 build 失敗... VIEW 拉進去沒辦法明確的指定 KEY 是那個欄位，不是結果不對就是 build 失敗，最後忍不住還是得去手動改 .edmx .. 這些事件老實說這兩個月也碰了不少 @_@

不過撇開工具的問題，Entity Framework 的設計還真是不錯。其它的心得就改天再講，先講困擾我最久的，也是大部份 ORM 的通病 - 大型 database 的問題。

這裡指的 "大型" 不是指資料筆數很多，是指 schema 很複雜的情況。大型的 AP 用到上百個 table + view 是很常見的，尤其是隨著改版，舊 table 沒刪掉，新的 table 又一直加，那還真是恐佈。所有的 ORM 都需要某種型態的 O / R Mapping, 不是寫設定檔，就是有視覺化的設計工具。不過... 你能想像一張有 500 個 table 的 ER-MODEL 嗎? 

要避免過大的單一 OR Mapping 設定，就只有做適度的切割了。在 Entity Framework / Visual Studio 2008 ，這點很容易做到，分成多個 .edmx 檔就可以了。不過問題會在後面，分開多個 .edmx 有幾個缺點:

1. 會有多個 ObjectContext 產生，每邊都有物件要更新時，每個 ObjectContext 都得呼叫 SaveChange..
2. 不論是 LINQ to Entities 或是 eSQL, 想要 join 橫跨在多個 .edmx 的資料時，會得到無情的錯誤... 不支援跨 context 的操作
3. AssoicationSet 無法跨越 context 的範圍，意思是跨 .edmx 的 Entity, 不能靠 Navigation Property 來處理。

解決的方式當然也有，也查了 ADO.NET Team Blog，這兩篇是所有 GOOGLE 到的相關文章裡，講這問題講的最深入的..

- [Working With Large Models In Entity Framework – Part 1](http://blogs.msdn.com/adonet/archive/2008/11/24/working-with-large-models-in-entity-framework-part-1.aspx)
- [Working With Large Models In Entity Framework – Part 2](http://blogs.msdn.com/adonet/archive/2008/11/25/working-with-large-models-in-entity-framework-part-2.aspx)

有碰到這問題的，這兩篇一定要看一看。其實文章內探討的問題已經超過我的需求了，我只是要解決我面臨到的問題:

1. 因應模組化需求，我需要把 .edmx 跟其相關的邏輯封裝在各別的 assembly 
2. 不同的模組間定義的 EntitySet 能夠用 eSQL 做 JOIN 的查詢
3. 最基本的 LINQ 也不能少
4. 新增新的模組時，其它模組不需要重新編譯

老實說這兩篇沒解決到我的問題，只不過瞄到了 Part 2 有這麼一段話:

> 9. At runtime, you could create either one Context that works with both the schema sets or two different contexts. To create a single context with both the schema sets, you would use the ObjectContext constructor that takes in an EntityConnectionString. In the Metadata parameter of the connection string, specify the paths to both sets of files.

哈哈，運氣不錯，關鍵的一段話沒有漏掉... 就這段話解決了我一個多月以來的困擾。Entity Connection 用的連接字串又臭又長，包括了你的 .csdl, .ssdl, .msl 三份定義檔在那裡，還有底層用的 database connection string. 湊起來一大串，像這樣:

```
medadata=res://*/Model1.csdl|res://*/Model1.ssdl|res://*/Model1.msl;............
```

而從這兩篇文章，除了各種 split / reuse 這堆設定檔的方法及優缺點之外，就是學到原來 entity connect string 可以併入多組對應檔啊 :D，像這樣:

```
medadata=res://*/Model1.csdl|res://*/Model1.ssdl|res://*/Model1.msl|res://*/Model2.csdl|res://*/Model2.ssdl|res://*/Model2.msl;............
```

沒錯!! 說穿了不值錢，就是把 entity connection string 這樣改一改就好了，eSQL 就可以透過單一 object context 就能存取兩份 .edmx 內定義的內容， Linq 則要自己用 CreateQuery< >() 方式來產生 EntitySet.. 其它就沒有什麼太大不同了。

總算搞定這個大問題!! 收工! 其它的應用就改天有空再慢慢貼了 :D 感謝各位在這兩個月枯水期還沒取消訂閱我的 BLOG ... :D
