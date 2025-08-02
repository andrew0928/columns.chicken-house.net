---
layout: post
title: "NGenerics - DataStructure / Algorithm Library"
categories:

tags: [".NET","C#","MSDN","Tips","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/10/14/ngenerics-datastructure-algorithm-library/
  - /columns/post/2008/10/14/NGenerics-DataStructure-Algorithm-Library.aspx/
  - /post/2008/10/14/NGenerics-DataStructure-Algorithm-Library.aspx/
  - /post/NGenerics-DataStructure-Algorithm-Library.aspx/
  - /columns/2008/10/14/NGenerics-DataStructure-Algorithm-Library.aspx/
  - /columns/NGenerics-DataStructure-Algorithm-Library.aspx/
wordpress_postid: 58
---
其實本來沒打算寫這篇的，不過之前在寫第二篇: [[該如何學好 "寫程式" #2. 為什麼 programmer 該學資料結構 ??](/post/e8a9b2e5a682e4bd95e5adb8e5a5bd-e5afabe7a88be5bc8f-2-e782bae4bb80e9babc-programmer-e8a9b2e5adb8e8b387e69699e7b590e6a78b-.aspx)] 時，寫的太高興，忘了查 System.Collections.Generics.SortedList 的 KEY 能不能重複... 結果貼出來後同事才提醒我，SortedList 的 KEY 一樣得是唯一的... Orz

實在是不想自己再去寫這種資料結構的作業... 一來我寫不會比較好，二來自己寫的沒支援那堆 ICollection, IEnumerable 等 interface 的話，用起來也是很難用... 就到 [www.codeplex.com](http://www.codeplex.com) 找了找，沒想到還真的找到一個: [NGenerics](http://www.codeplex.com/NGenerics) :D 找到之後才發現挖到寶了，裡面實作的資料結構還真完整，Heap, BinaryTree, CircularQueue, PriorityQueue... 啥的一應俱全，好像看到資料結構課本的解答本一樣 @_@，有興趣研究的人可以抓它的 Source Code 來看..

這套 LIB 的實作範圍很廣，除了我前兩篇介紹很基本的那幾個之外，其它連一些數學的跟圖型，甚至是各種排序法的實作都包含在內。要看介紹就到它的官方網站看吧! 很可惜的是它的文件不像 MSDN 一般，有明確的標示時間複雜度... 不過它有附 Source Code, 拼一點的話還是可以自己看程式... 哈哈 :D

我就拿 NGenerics 來改寫之前我提供的範例程式吧，那個查通訊錄的程式就不用再改寫了，看不大出來效果差在那。我們來改寫複雜一點的，也就是高速公路的例子。

先來看看有什麼東西可以用? NGenerics.DataStructures.General 這個 Namespace 下竟然有現成的 Graph 類別!! 而 NGenerics.Algorithms 下也有現成的 GraphAlgorithm 這演算法的實作... Orz, 裡面提供了三種演算法，光看名字還真搞不懂它是啥... 分別查了一下，是這三個... 找到的都是教授或是考古題之類的網站 ... 咳咳...

1. Dijkstras Algorithm ([代克思托演算法](http://nthucad.cs.nthu.edu.tw/~yyliu/personal/nou/04ds/dijkstra.html)): ... 這種名字難怪我記不住 @_@，這演算法就是我在第三篇提過比較好的演算法，由起點一路擴散出去的作法。
2. [Kruskals Algorithm](http://203.64.42.21/course/2007/Algorithms/poko/Kruskal.htm): 這名字大概太難翻了，沒人把它翻成中文的.. 哈哈，這演算法是找出 minimal spanning tree (最小生成樹)，這篇不講教條了，跳過跳過，有興趣自己看 :D
3. Prims Algorithm ([普林演算法](http://nthucad.cs.nthu.edu.tw/~yyliu/personal/nou/04ds/prim.html)): 這名字好記多了... 一樣是找~~最短路逕~~ minimal spanning tree 的演算法

來看看原本我寫了上百行的程式 (請參考上一篇)，用這個 LIB 改寫有多簡單吧! 先來看看建地圖的部份。Graph<T> 的 T 是指圖的節點型別。暫時不管收費站的問題，因為 GRAPH 的模型裡，只有路逕是有成本的，點本身沒有。直接用 string 來識別點 (vertex)，兩個點跟它的距離就當作路段 (edge)。建資料還真有點囉唆，打了不少字:

**利用 NGeneric 的 Graph 來建立高速公路的模型**

```csharp
Graph<string> highway = new Graph<string>(false);
highway.AddVertex("基金");
highway.AddVertex("七堵收費站");
highway.AddVertex("汐止系統");
// 以下略
highway.AddEdge(
    highway.GetVertex("基金"), 
    highway.GetVertex("七堵收費站"),
    4.9 - 0);
highway.AddEdge(
    highway.GetVertex("七堵收費站"), 
    highway.GetVertex("汐止系統"), 
    10.9 - 4.9);
// 以下略
```

都是我一行一行慢慢打的 @_@... 地圖建完後，怎麼找出兩點之間的最短路逕? 只要這段...

**找出 [機場端] 到 [基金] 的最短路逕**

```csharp
Graph<string> result = GraphAlgorithms.DijkstrasAlgorithm<string>(
    highway,
    highway.GetVertex("機場端"));
Console.WriteLine(result.GetVertex("基金").Weight);
```

因為每個路段的 weight 我是填上油錢 (一公里兩塊錢)，所以印出來的就是兩端要花的油錢。那麼被我們忽略掉的收費站怎麼算? 因為圖型的 MODEL 裡，點是沒有 weight 的，因此我們必需把路段改成有方向的，也就是南下及北上分別算不同的路段 (edge), 同時把過路費加到 weight 裡。

這個演算法的實作有個小缺點，它只傳回結果，沒把過程傳回來...，所以我們只能算出要花多少錢，沒有很簡單的方法拿到該怎麼走。不過好在它有附原始碼，需要的人就拿來改一下吧 :D，多傳個 delegate 或是用它定義的 IVisitor 讓它走完所有的點，你就可以取得沿路的資訊了。

這篇主要是介紹這個意外發現的LIB，就不深入的挖這些細節了，有興趣的讀者們可以自己試看看，不難的。見識到這類演算法函式庫的威力了嗎? 用起來一點都不難，不過要知道怎麼用還真的要好好研究一下...。整套 NGenerics 都是這類的東西，有興趣的讀者好好研究吧 :D
