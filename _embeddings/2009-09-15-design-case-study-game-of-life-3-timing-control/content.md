原本的範例，其實有些盲點，不知各位有沒看到? 一樣的起始狀態，一樣的遊戲規則，你不一定會得到一樣的結果。為什麼? 因為這會跟你程式 SCAN 的順序有關。怎麼說? 因為到目前為只，整個遊戲就好像下棋一樣，是 "回合制"，我下完了換你... 一路一直輪下去。

這時先下後下就會影響結果了。現實世界的生命不是這樣的啊... 不知有沒有人玩過早期的太空戰士 (Final Fantasy) 系列遊戲? 當年 FF 有個很重要的突破，就是把 RPG 從傳統的 "回合制" 改成即時戰鬥... 每個人都有個倒數的碼錶，數到 0 你就可以發動下一次的攻擊... 這樣才接近現實世界啊。套用到我們的生命遊戲，這次我們想作的改變，就是把程式改成這種模式。

因此來調整一下規則，每個細胞每隔 1000ms 後會進到下一個狀態。不過生命總是沒有完全一樣的，因此每個細胞進到下一個狀態的時間差，都會有 10% 的誤差 (也就是 950ms ~ 1050ms 之間的時間都有可能)。其它規責則維持不變，來看看程式該怎麼改寫。

這種 "即時制"，是比較合乎現實的情況的，如果未來你想發展到像 facebook 上的那些小遊戲，或是其它線上遊戲一樣的話， "回合制" 是決對行不通的... 這時，我們可以想像，每個細胞都有自己的執行緒，每換過一次狀態後就 Sleep() 一段時間，醒來再換到下一次狀態... 一直到指定的世代 (generation) 到達為止。

來看一下改版過的程式。我們先不動原本的 Cell, 只追加一個 method: WholeLife( ), 呼叫後就會一直更新這個細胞的狀態，直到它結束為止 (不是死掉喔，是 generation 到達)。而整個世界的所有細胞，都是獨立的個體，都有個專屬的執行緒在運作...。這時 Game Host 就得換個方式來讓這些細胞過日子 (執行)，同時 Game Host 好像有個人造衛星一樣，不斷的在上空拍照來更新畫面，而完全不影響這些細胞的生命進行。

來看一下改寫過的 Cell 追加的 method:

```csharp
        public void WholeLife(object state)
        {
            int generation = (int)state;
            for (int index = 0; index < generation; index++)
            {
                this.OnNextStateChange();
                Thread.Sleep(_rnd.Next(950, 1050));
            }
        }
```

改變不大，只是多個簡單的迴圈，跟 sleep 來控制時間而已。再來看看 Game Host 要怎麼改:

```csharp
        static void Main(string[] args)
        {
            int worldSizeX = 30;
            int worldSizeY = 30;
            int maxGenerationCount = 100;

            World realworld = new World(worldSizeX, worldSizeY);

            // init threads for each cell
            List<Thread> threads = new List<Thread>();
            for (int positionX = 0; positionX < worldSizeX; positionX++)
            {
                for (int positionY = 0; positionY < worldSizeY; positionY++)
                {
                    Cell cell = realworld.GetCell(positionX, positionY);
                    Thread t = new Thread(cell.WholeLife);
                    threads.Add(t);
                    t.Start(maxGenerationCount);
                }
            }

            // reflesh maps
            do
            {
                realworld.ShowMaps("");
                Thread.Sleep(100);
            } while (IsAllThreadStopped(threads) == false);

            // wait all thread exit.
            foreach (Thread t in threads) t.Join();
        }

        private static bool IsAllThreadStopped(List<Thread> threads)
        {
            foreach (Thread t in threads)
            {
                if (t.ThreadState != ThreadState.Stopped) return false;
            }
            return true;
        }
```

 

其實這卅幾行 code, 大都花在控制執行緒上面，有興趣的讀者可以翻翻我之前寫的那系列文章，我就不多作說明了。調整之後，這個世界變的更不可測了，一樣的起始環境，連上帝 (在這模擬世界裡，我就是上帝 XD) 都無法預測下一秒會發生什麼事...

![image](/images/2009-09-15-design-case-study-game-of-life-3-timing-control/image.png)

 

感覺就好像看電視一樣。畫面不斷的在閃動，而畫面裡的細胞會不規責的跳動，不像上一版程式一樣，每刷一次就變一次那樣的枯燥無聊。如果畫面呈現的地方再多用點心思，就可以弄的像卡通一樣，每個細胞都各自用自己的步調在活著...

到這裡，如何? 應該沒有人把作業寫到這個樣子了吧 XD (就說別抄我的程式去交作業了)。不適當的利用執行緒，也做的到類似的結果。不過，你花費的代價會很大，因為你的程式得自己來做 context switch (這些是 OS + thread scheduler 會幫你解決掉的，只要你曉得要用 thread)。

接下來下一篇，我們再繼續調整這世界的遊戲規則，加入更多元素進去，看看程式會變怎樣? 多執行緒解決時間的問題了，再來我們要用繼承及多型，讓不同的生命可以在同一個世界下共同生活...  ((待續))

 
[Multi-Thread Source Code](/wp-content/be-files/WindowsLiveWriter/3/5579A0F9/BLOG_3.zip)