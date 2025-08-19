---
layout: post
title: "[設計案例] 生命遊戲#1, 前言"
categories:
- "系列文章: 生命遊戲"
tags: [".NET","C#","多執行緒","技術隨筆","物件導向","系列文章: 生命遊戲"]
published: true
comments: true
redirect_from:
  - /2009/09/12/設計案例-生命遊戲1-前言/
  - /columns/post/2009/09/12/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b21-e5898de8a880.aspx/
  - /post/2009/09/12/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b21-e5898de8a880.aspx/
  - /post/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b21-e5898de8a880.aspx/
  - /columns/2009/09/12/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b21-e5898de8a880.aspx/
  - /columns/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b21-e5898de8a880.aspx/
wordpress_postid: 34
---

[前言]

好久沒寫點自己覺的有內容的東西了... 最近 code 寫的少，實在沒有什麼了不起的新技術可以分享，而 thread 那種 "古典" 計算機科學的東西也寫的差不多了.. 就懶了起來。

雖然沒新技術好寫，不過老狗玩的把戲還是能榨出點渣的... 很多人都熟新技術，可以寫出很炫的程式，不過也常看到程式的結構真的是亂搞一通的... 所以我打算寫些 [設計案例] 的文章，舉一些我實作過的案例，說明什麼樣的問題可以用什麼方式或技術來解決。其實我想寫的就是像 design patterns 那類的東西，只不過我程度還差的遠，只能稱作 "案例" ... Orz

----------------------------------------------------------------------------------

最近 facebook 上有一些小遊戲，不知道在紅什麼... 突然間大家都在玩，就都是些模擬遊戲，像是開心農場、My FishBowl … 之類的，你要在裡面種東西或養魚，條件充足就會長大，收成等等... 然後透過 Facebook API 可以跟別人互動的遊戲。看到這類的 GAME，不禁想起過去在唸書時，幾個經典的作業題目，其中一個 [生命遊戲] (Game of Life) 就是這種 GAME 的始祖...

在 Wiki 找的到這段介紹:

> [http://zh.wikipedia.org/zh-hk/%E7%94%9F%E5%91%BD%E6%B8%B8%E6%88%8F](http://zh.wikipedia.org/zh-hk/%E7%94%9F%E5%91%BD%E6%B8%B8%E6%88%8F)
> 
> **生命遊戲**（Game of Life），又稱**生命棋**，是[英國](http://zh.wikipedia.org/zh-hk/%E8%8B%B1%E5%9B%BD)[數學家](http://zh.wikipedia.org/zh-hk/%E6%95%B0%E5%AD%A6%E5%AE%B6)[約翰·何頓·康威](http://zh.wikipedia.org/zh-hk/%E8%A9%B9%C2%B7%E4%BD%95%E9%A0%93%C2%B7%E5%BA%B7%E5%A8%81)（John Horton Conway）在[1970年](http://zh.wikipedia.org/zh-hk/1970%E5%B9%B4)發明的[細胞自動機](http://zh.wikipedia.org/zh-hk/%E7%B4%B0%E8%83%9E%E8%87%AA%E5%8B%95%E6%A9%9F)（cellular automaton，也翻譯成「格狀自動機」）。
> 
> 它最初於[1970年](http://zh.wikipedia.org/zh-hk/1970%E5%B9%B4)[10月](http://zh.wikipedia.org/zh-hk/10%E6%9C%88)在《[科學美國人](http://zh.wikipedia.org/zh-hk/%E7%A7%91%E5%AD%B8%E7%BE%8E%E5%9C%8B%E4%BA%BA)》（Scientific American）雜誌中[馬丁·葛登能](http://zh.wikipedia.org/w/index.php?title=%E9%A6%AC%E4%B8%81%C2%B7%E8%91%9B%E7%99%BB%E8%83%BD&action=edit&redlink=1)（Martin Gardner）的「數學遊戲」專欄出現。

1970… 我還沒出生... Orz, 不過, 這麼一個古老經典的問題，找的到一大堆範例程式，或是作業解答。清一色是用 C 這類配的上它的年紀的程式語言寫的，就算有 JAVA 版，大概也是換湯不換藥... 這四十年程式語言及軟體技術的進步，寫這種程式總該有點改變吧?

這篇我想寫的，就是這樣的問題，配合現在的 .NET / C#，能怎麼寫它? 這年代的軟體開發技術，對這種古典的程式能發揮什麼效益? 

(警告: 剛好要交作業的人，可千萬別用我的方法交出去啊... 你的助教看不懂可能會給你零分...)

先找個範例來看看... 為了不讓過多的畫面處理程式碼，干擾到主程式的架構，我特地找了兩個 console based 的範例:

Java 版:  
[http://tw.myblog.yahoo.com/dust512/article?mid=25&prev=28&next=-1](http://tw.myblog.yahoo.com/dust512/article?mid=25&prev=28&next=-1)

多語言版 (C, Java, Python, Scala):  
[http://caterpillar.onlyfun.net/Gossip/AlgorithmGossip/LifeGame.htm](http://caterpillar.onlyfun.net/Gossip/AlgorithmGossip/LifeGame.htm)

這... 這就是典型的 "Java 版 C 程式碼" 的範例... 用 Java 來寫只寫這樣，有點用牛刀的感覺... 新的開發環境強調這幾項:

1. 物件導向 (封裝，多型，動態連結... etc)
2. 多執行緒
3. 其它語言特色 (這次會講到的是 yield return)

這些技術怎麼套進這程式? 先來看看這遊戲有幾個障礙要克服吧。遊戲的規則簡單明瞭，借轉貼上面第二個範例的說明:

> 生命遊戲（game of life）為1970年由英國數學家J. H. Conway所提出，某一細胞的鄰居包括上、下、左、右、左上、左下、右上與右下相鄰之細胞，遊戲規則如下:
> 
> 1. 孤單死亡：如果細胞的鄰居小於一個，則該細胞在下一次狀態將死亡。
> 2. 擁擠死亡：如果細胞的鄰居在四個以上，則該細胞在下一次狀態將死亡。
> 3. 穩定：如果細胞的鄰居為二個或三個，則下一次狀態為穩定存活。
> 4. 復活：如果某位置原無細胞存活，而該位置的鄰居為三個，則該位置將復活一細胞。

以前我最討厭寫這種程式了，這種程式寫起來就跟 Regexp 一樣，是 "write only" 的 code… 怎麼說? 程式寫好後，可能自己都看不懂了，因為邏輯被切的亂七八糟... GAME 裡可能同時有好幾個細胞，每個都有獨立的規則，不過程式卻是一個主迴圈，每次執行每個細胞的一小段邏輯... 程式的流程就這樣被切碎了... 我打算用C#的 yield return, 解決這邏輯破碎的問題。

第二個障礙，就是這類程式，某種程度都是隨著時間的進行而跑的，比如上面的條件都是 "下一次狀態" … 把每次狀態改變定義一個時間 (比如一秒)，這就是個 realtime 的模擬程式了。如果有的細胞是一秒改變一次狀態，有的是兩秒，有的是五秒... 那就傷腦筋了... 你的程式會被切的更破碎... 這些每種細胞特殊的部份，我打算用 OOP 的多型來解決。

最後，這種很明顯是 "並行" 的問題，照道理來說，用多執行緒是最適合的了。不過隨便也有成千上萬個 "細胞" 在成長，每個都來一個 thread 養它，再高級的 server 都撐不住吧? 這邊會來探討一下，怎麼用執行緒相關的技巧，來解決這問題。

--------------------------------------------------------------------------------------

寫到這裡，突然覺的這題目好大... Orz, 搞不好這幾篇要撐幾個月才寫的完... 至少有個題材好寫，等到我生出第一個 sample code, 就會有下一篇了... 如果有同好也想試試看的，也歡迎分享看看你的 code… 只不過我沒像 darkthread 有本錢提供[獎品](http://blog.darkthread.net/blogs/darkthreadtw/archive/2008/07/21/win-a-vsts-2008.aspx)... 哈哈 :D
