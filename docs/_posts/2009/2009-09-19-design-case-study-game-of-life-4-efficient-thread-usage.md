---
layout: post
title: "[設計案例] 生命遊戲 #4, 有效率的使用執行緒"
categories:
- "系列文章: 生命遊戲"
tags: [".NET","C#","作品集","多執行緒","技術隨筆","有的沒的","物件導向","系列文章: 生命遊戲"]
published: true
comments: true
redirect_from:
  - /2009/09/19/設計案例-生命遊戲-4-有效率的使用執行緒/
  - /columns/post/2009/09/19/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b2-4-e69c89e69588e78e87e79a84e4bdbfe794a8e59fb7e8a18ce7b792.aspx/
  - /post/2009/09/19/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b2-4-e69c89e69588e78e87e79a84e4bdbfe794a8e59fb7e8a18ce7b792.aspx/
  - /post/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b2-4-e69c89e69588e78e87e79a84e4bdbfe794a8e59fb7e8a18ce7b792.aspx/
  - /columns/2009/09/19/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b2-4-e69c89e69588e78e87e79a84e4bdbfe794a8e59fb7e8a18ce7b792.aspx/
  - /columns/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b2-4-e69c89e69588e78e87e79a84e4bdbfe794a8e59fb7e8a18ce7b792.aspx/
wordpress_postid: 30
---

原本這篇不講執行緒，要直接跳到 OOP 多型的應用... 不過看一看 [#3](/post/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b23-e69982e5ba8fe79a84e68ea7e588b6.aspx) 自己寫的程式，實在有點看不下去... 30x30 的大小，程式跑起來就看到 903 條執行緒在那邊跑... 而看一下 CPU usage, 只有 5% 不到... 這實在不是很好看的實作範例，如果這是線上遊戲的 SERVER 程式，裡面的每個人，每個怪物等等都用一條專用的執行緒在控制他的行為的話，我看這遊戲不用太多人玩，SERVER 就掛掉了吧! 因此要繼續更貼近實際的生命模擬遊戲前，我們先來解決效能的問題，所以多安插了這篇進來 :D

前一篇 ([#3](/post/e8a8ade8a888e6a188e4be8b-e7949fe591bde9818ae688b23-e69982e5ba8fe79a84e68ea7e588b6.aspx)) 的主題是把生命的進行，從被動的在固定時間被喚醒 (callback) 的作法，改成主動的在指定時間執行 (execute)。 想也知道，現實世界的生物都是 "主動" 的，後面的作法比較符合 OOP 的 "[模擬世界，加以處理](/post/e4b896e7b580e69cabe8bb9fe9ab94e99da9e591bde5bea9e588bbe78988.aspx)" 的精神。但是，一個小程式就吃掉 900 條執行緒，是有點過頭了。不知道還有沒有人[記得](/post/Thread-Sync-2-e5afa6e4bd9ce7af87-e4ba92e79bb8e7ad89e5be85e79a84e585a9e5808be59fb7e8a18ce7b792.aspx)，我騙到獎品的這個程式... 很另類的用 yield return 來解決類似問題的作法... 藉著 compiler 很雞婆的把單一流程翻成數段可以切開執行的邏輯...，正好拿來利用一下，替我們把一連串連續的邏輯切段，以便利用多執行緒來處理。我的想法是這樣，原程式是用個迴圈，作完該作的事，就休息 (sleep) 一段時間。而新的寫法，我打算用 yield return new TimeSpan(…) 來取代 Thread.Sleep(…)。每個 Cell內部的程式結構修改不大，不過對於 GameHost 就是個挑戰了... 來看看修改前及修改後的程式碼:

```csharp
        // 修改前
        // 使用 Thread.Sleep( ) 來控制時間
        public void WholeLife(object state)
        {
            int generation = (int)state;
            for (int index = 0; index < generation; index++)
            {
                this.OnNextStateChange();
                Thread.Sleep(_rnd.Next(950, 1050));
            }
        }
        //
        //
        //
        // 修改後
        // 使用 yield return new TimeSpan( ) 來控制時間
        public IEnumerable<TimeSpan> WholeLife(object state)
        {
            int generation = (int)state;
            for (int index = 0; index < generation; index++)
            {
                this.OnNextStateChange();
                yield return TimeSpan.FromMilliseconds(_rnd.Next(950, 1050));
            }
            yield break;
        }
```

別想的太美，只改這樣，程式是不會動的... 修改過之後，麻煩的地方會在 GameHost. 因為整個 GameHost 的邏輯都反過來了。原本是 GameHost 只要放著那九百條執行緒自生自滅，它只要不斷的刷新畫面就好了。現在它則得用 foreach(…) 去詢問:

> *"大爺，這次您要休息多久?"*

接到 yield return 傳回的 TimeSpan 物件 (代表它要休息多久後，繼續下一個動作) 後，經過這段時間，GameHost 就要再去叫醒 cell, 然後再詢問一次:

> *"大爺，這次您要休息多久?"*

關鍵就在於 GameHost 如何能透過少量的 thread 來伺後這些大爺，而不是像 #3 的程式一樣，每個大爺都用一條專屬的 thread… 要共用執行緒，就要先想辦法把工作切碎，這是基本法則。如果你希望你的生命遊戲程式不只是作業的話，那麼效能跟即時回應的問題是必需要考慮的。在動手改寫 GameHost 程式之前，先來分析一下改寫的目標有那些:

> ***目標是要達到像 #2 範例一樣的效果，但是要用更有效率的方式。***

目標很清楚，再來就看看有什麼手段可以用了。第一個是過量的執行緒，應該要想辦法改用執行緒集區。因為 #2 用了高達 900 條執行緒，不過整體 CPU USAGE 不到 5%，大部份的執行緒都在閒置狀態。如果能想辦法把這些運算丟到執行緒集區，由集區動態管理會有效率的多。

第二，就是把原本的 Thread.Sleep(ts) 改成 yield return ts 後，原本每個 thread 自己睡覺的機制，就要改成 cell 各自回報 game host 它想要睡多久，然後由 game host 統一在時間到時叫醒它。由於一次有多個 cell 同時在運作，因此我們需要一個簡單的排程器，作法像這樣:

1. 建立一個時間表，依照時間順序，把每個 cell 預計要被叫醒的時間標上去。
2. 時間到了之後，就去呼叫該 cell 的 OnNextStateChangeEx()，同時取得該 cell 下次要喚醒的時間，再標到時間表上
3. GameHost就不斷的替每個 cell 重複 (1) (2) 的動作..
4. 同時另外用一條獨立的執行緒，作畫面更新的動作。

嗯，要處理的方式越來越清楚了。剩下的是 "時間表" 要用什麼型式來表現? 我的選擇是，我希望它是個 ToDo List, 會幫我排好時間，我只要把工作標上時間，丟進 ToDo List, 然後 ToDo List 只要能忠實的回報給我還有沒有排定的工作? 如果有，下一個要處理的工作是那一個? 什麼時後處理?

它的用法只有丟工作進去，跟拿工作出來，因此我設計它的公開介面長這個樣子:

```csharp
        public class CellToDoList
        {
            public void AddCell(Cell cell) {...}
            public Cell GetNextCell() {...}
            public Cell CheckNextCell() {...}
            public int Count {get;}
        }
```

裡面的實作，我就不多說了。我是把它當成 QUEUE 在設計，唯一的差別是，放進 QUEUE 的東西會先經過排序，因此不見得是 "First In First Out" 這種典型的貯列，而是會以 Cell 上標示的時間為準，依序 Out …。實作起來很簡單，用現成的 SortedList 當內部的儲存方式，加上基本的 lock 機制來確保它是 thread safe 的就夠了。

好，這些雞絲都準備好之後，就可以來打造我們的新版 GameHost 了。來看看 Code:

```csharp
        static CellToDoList _cq;
        static void _YieldReturnGameHost(string[] args)
        {
            int worldSizeX = 30;
            int worldSizeY = 30;

            World realworld = new World(worldSizeX, worldSizeY);

            _cq = new CellToDoList();
            // init threads for each cell
            for (int positionX = 0; positionX < worldSizeX; positionX++)
            {
                for (int positionY = 0; positionY < worldSizeY; positionY++)
                {
                    Cell cell = realworld.GetCell(positionX, positionY);
                    cell.OnNextStateChangeEx();
                    _cq.AddCell(cell);
                }
            }

            // 啟動定期更新畫面的執行緒
            Thread t = new Thread(RefreshScreen);
            t.Start(realworld);

            while (_cq.Count > 0)
            {
                Cell item = _cq.GetNextCell();
                if (item.NextWakeUpTime > DateTime.Now)
                {
                    // 時間還沒到，發呆一下等到時間到為止
                    Thread.Sleep(item.NextWakeUpTime - DateTime.Now);
                }
                
                ThreadPool.QueueUserWorkItem(RunCellNextStateChange, item);
            }
        }

        private static void RunCellNextStateChange(object state)
        {
            Cell item = state as Cell;
            TimeSpan? ts = item.OnNextStateChangeEx();
            if (ts != null) _cq.AddCell(item);
        }


        private static void RefreshScreen(object state)
        {
            while (true)
            {
                Thread.Sleep(500);
                (state as World).ShowMaps("");
            }
        }
```

 

GameHost 的工作很明確，一開始 (line 18 ~ 20) 就把更新畫面的動作完全交給另一個執行緒，之後就專心處理 ToDoList 內的工作了。

接著後面的 while loop (line 21 ~ 30) 則是很單純的從 ToDoList 裡取出下一個要要動作的 Cell, 如果時間還沒到就 Sleep 等一下它。執行完後會再詢問下一次是什麼時后，同時再把他加到 ToDoList 內等待下一次輪到他時繼續。

這次的程式我沒有設定停止的條件，因此你會看到程式會不斷的執行下去。程式執行起來，結果跟 #3 沒什麼不同，畫面上的每個細胞會照著題目的規則生長或死亡，不同的是 #3 的 Game Host 需要用到 903 條執行緒，而這版的 Game Host 只要 9 條執行緒...

![image](/images/2009-09-19-design-case-study-game-of-life-4-efficient-thread-usage/image.png)

 

其實，以這樣的範例題，我大可以不用顧慮到效能的問題，不過就是示範程式怎麼寫嘛。不過，我的目標如果只是訂在怎麼寫這練習題，大可以 GOOGLE 一下就有一堆作業解答了 :D。我的目標是要展示一下，該如何開發這樣的 GameHost ? 這樣的程式，是大部份的遊戲的基礎，尤其是像線上遊戲或是 facebook 這類互動遊戲的基礎。有了像樣的 Game Host 之後，接下來就把目標放在如何建立多樣的生物，一起放在這世界裡面生活了。接下來就會大量運用到 OOP 的特點 (對，就是上一篇預告的...) 繼承及多型。

有沒有人覺的，這種程式越寫越像 Matrix (就是駭客任務裡的 "母體") 了? 裡面活著的東西其實都在我的掌控之下... =_= 哈哈... 未完待續，請期待續集 :D。

--

範例程式:

[BLOG #4.zip](/wp-content/be-files/WindowsLiveWriter/4/7DFFC8B9/BLOG_4.zip)
