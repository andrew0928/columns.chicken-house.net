---
layout: post
title: "EF#3. Entity & Inheritance"
categories:
- "系列文章: Entity Framework 與 物件導向設計"
tags: [".NET","C#","SQL","技術隨筆","物件導向", "Entity Framework"]
published: true
comments: true
permalink: "/2009/03/03/ef3-entity-inheritance/"
redirect_from:
  - /columns/post/2009/03/03/EF3-Entity-Inheritance.aspx/
  - /post/2009/03/03/EF3-Entity-Inheritance.aspx/
  - /post/EF3-Entity-Inheritance.aspx/
  - /columns/2009/03/03/EF3-Entity-Inheritance.aspx/
  - /columns/EF3-Entity-Inheritance.aspx/
wordpress_postid: 42
---

繼承 (inheritance) 是物件技術的核心，就是這個特性提供了 OOP 絕大部份的特色。這東西被拿掉的話，OOP就沒這麼迷人了。繼然談到了 ORM，就不能不來看看 R(關聯式資料庫) 怎麼被對應到 O(物件)，同時還能處理好繼承關係。

RDBMS 連基本的物件 (Object Base) 都不支援了，更別說物件導向 (Object Oriented) 了。因此要搞懂 ORM 及繼承的關係，就得先瞭解基本的 OO 是怎麼實作 "繼承" 這個動作。這些知識是古早以前學 C++ 時唸到的，現在的 CLR 不知道有沒有新的作法? 不過應該大同小異吧! C++ 主要是靠 [virtual table](http://en.wikipedia.org/wiki/Virtual_table) 來實作繼承關係，當子類別繼承父類別時，父類別定義的 data member 跟 method 就全都遺傳到子類別身上了，這動作就是靠 virtual table 作到的。細節我就不多說了，有興趣的讀者們請先上網找找相關資訊看一看。

ORM 的運氣好多了，只要處理資料的部份。因此前一段提到的 virtual table 如果要拿來應用也會簡單的多。virtual table 可以很直覺的想像成是 DBMS 裡 table schema 的定義，而一個物件 (instance) 的 virtual table 資料，正好就對應到該 table (DBMS) 的一筆資料。這正好是 ORM 基本的動作。大部份 OO 的書都會說，繼承就是 " Is A " 的關係。在資料上則是子類別擁有父類別所有的欄位定義。這很容易對應到資料庫的正規化，該如何切割資料表的規責。你可以切開靠 PK / FK 再併回來，或是直接反正規化讓它重複定義在多個 TABLE... 事實上，兩大 ORM (EF & NH) 都歸納出三種作法，後面來探討一下彼此的差異...

再來看看繼承關係，假設父類別 class A 對應到 table A, 那麼衍生出的子類別 class B 對應的 table B, 則應該要包含所有 table A 定義的欄位才對。從這點出發，就帶出了第一種作法: 就是把 table A 所有的欄位都建一份到 table B (註: table per concrete type)。

不過這樣看起來有點蠢，DBMS 熟悉的人也許會採另一種作法: 沒錯... table B 只要留個 foreign Key, 指向 table A 的 primary Key，需要時再 join 起來就好了，這是第二種作法 (註: table per type)。

唸過 DBMS 的人都還記得 "正規化" ([normalization](http://en.wikipedia.org/wiki/Database_normalization#Normal_forms)) 跟 "反正規化" 吧? 切割過頭也是很麻煩的，因此有第三種作法逆其道而行，就是建一個 table 給所有的子子孫孫類別共用。因此 table 需要的欄位，就是所有的子類別的所有欄位集大成，通通都建進來... 不用的話就空在那裡，這是第三種作法 (註: table per hierarchy)。

這三種作法，在 Entity Framework (以下簡稱 EF) 或是 NHibernate (以下簡稱 NH) 都有對應的作法，只不過名字不大一樣... [這篇](http://blogs.msdn.com/adonet/archive/2007/03/15/inheritance-in-the-entity-framework.aspx) ADO.NET team blog 借紹的還不錯，可以參考看看。這三種方式，在 EF 裡的說法分別是 (括號裡是 NH 的說法，參考這篇: [Inheritance Mapping](http://www.hibernate.org/hib_docs/reference/en/html/inheritance.html)):

- Table per Hierarchy (NH: Table per class hierarchy)
- Table per Type (NH: Table per subclass)
- Table per Concrete Type (NH: Table per concrete class)

事時上，處理方式大同小異，不外乎用三種不同的對應方式，來處理物件繼承關係。這些不同類別的物件彼此有繼承關係，對應到 TABLE 的方法不同，各有各的優缺點。其實 ADO.NET team blog 講的都很清楚，我就不再多說，簡單列張比較表:

|                        | 適用於                                                                     | 不適用於                                                           |
|------------------------|----------------------------------------------------------------------------|-------------------------------------------------------------------|
| Table Per Hierarchy    | 1. 最簡單的實作方式<br>2. 所有同系類別的實體 (instance) 數量不會很多時<br>3. 需要用單一 QUERY 查出所有的子類別物件時<br>4. 繼承階層較簡單的情況<br>5. 類別的欄位要調整很容易 | 1. instance數量太多，會嚴重影響效能<br>2. 無法在table schema上做太多嚴格的檢查 |
| Table Per Type         | 1. 繼承關係清楚的對應到 TABLE<br>2. 需要用單一QUERY查出所有子類別的物件<br>3. 不同於 TPH，可以針對每種類別，設定嚴僅的 table constraint<br>4. 每個類別要變動或調整都很容易 | 1. 繼承階層較多時，要取得單一 instance data 需要透過多層 join<br>2. table 數量會隨著類別的數量快速增長 |
| Table Per Concrete Type | 1. 綜合 TPH / TPT 的優點 (也綜合了兩者的缺點)<br>2. 可以針對每種類別設定 table constraint<br>3. ORM mapping 很簡單 | 1. 要用單一QUERY查出所有子類別的物件並不容易 (需要把所有的 TABLE JOIN 起來)<br>2. 父類別的欄位調整很麻煩，所有的 TABLE 都需要配合調整 |

[未完待續] to be continue…
