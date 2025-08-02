---
layout: post
title: "LINQ to Object #2, Indexes for Objects"
categories:

tags: [".NET","C#","Tips","物件導向"]
published: true
comments: true
permalink: "/2011/10/30/linq-to-object-2-indexes-for-objects/"
redirect_from:
  - /columns/post/2011/10/30/LINQ-to-Object-2-Indexes-for-Objects.aspx/
  - /post/2011/10/30/LINQ-to-Object-2-Indexes-for-Objects.aspx/
  - /post/LINQ-to-Object-2-Indexes-for-Objects.aspx/
  - /columns/2011/10/30/LINQ-to-Object-2-Indexes-for-Objects.aspx/
  - /columns/LINQ-to-Object-2-Indexes-for-Objects.aspx/
wordpress_postid: 10
---


上一篇自己寫了很不成熟的範例，示範怎麼同時使用 LINQ to Object 的方式查詢物件，同時又能用到索引的機制。不過示範歸示範，總是要有上的了檯面的作法... 這就是本篇的目的: i4o (indexes for objects) 這套函式庫的應用!

開始囉唆前，先來看看怎麼用吧! 接續上一篇的範例，我做了點調整，一方面把查詢的對像，從原本的 string 換成 Foo，另一方面也加上了第三種對照組: 使用 i4o 來建立索引。程式碼及執行結果如下:

**對三種不同的 collection 進行 Linq 查詢**


```csharp
Stopwatch timer = new Stopwatch();

// 建立資料集合 list1: 使用 List<Foo>, 沒有索引
List<Foo> list1 = new List<Foo>();
list1.AddRange(RndFooSeq(8072, 1000000));

// 建立資料集合 list2: 使用 IndexedList, 自訂型別，針對 Foo.Text 及 Foo.Number 建立索引，Query 只支援 == 運算元
IndexedList list2 = new IndexedList();
list2.AddRange(list1);

// 建立資料集合 list3: 使用 i4o library
IndexableCollection<Foo> list3 = list1.ToIndexableCollection<Foo>();

// 對 list1 進行 query
Console.WriteLine("\n\n\nQuery Test (non-indexed):");
timer.Restart();
(from x in list1 where x.Text == "888365" select x.Text).ToList<string>();
Console.WriteLine("Query time: {0:0.00} msec", timer.Elapsed.TotalMilliseconds);

// 對 list2 建立索引，進行 query
Console.WriteLine("\n\n\nQuery Test (indexed, dic):");
timer.Restart();
list2.ReIndex();
Console.WriteLine("Build Index time: {0:0.00} msec", timer.Elapsed.TotalMilliseconds);
timer.Restart();
(from x in list2 where x.Text == "888365" select x.Text).ToList<string>();
Console.WriteLine("Query time: {0:0.00} msec", timer.Elapsed.TotalMilliseconds);

// 對 list3 建立索引，進行 query
Console.WriteLine("\n\n\nQuery Test (indexed, i4o):");
timer.Restart();
list3.CreateIndexFor(i => i.Text).CreateIndexFor(i=>i.Number);
Console.WriteLine("Build Index time: {0:0.00} msec", timer.Elapsed.TotalMilliseconds);
timer.Restart();
(from x in list3 where x.Text == "888365" select x.Text).ToList<string>();
Console.WriteLine("Query time: {0:0.00} msec", timer.Elapsed.TotalMilliseconds);
```



![](/wp-content/be-files/image_14.png)
