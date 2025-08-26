繼[上篇](/post/C-yield-return-1-How-It-Work-.aspx)，講了一些 yield return 編譯後產生的 Code, 說明了 C# compiler 如何用簡單的語法替你實作了 IEnumerator 介面，而完全不會增加程式的複雜度，這是我認為 C# 提供最讚的 Syntax Sugar ...。

不過無意間我想到了 yield return 還有另一種應用方式。靈感來自之前 [Darkthread](http://blog.darkthread.net/) 舉辦的 [[黑暗盃程式魔人賽](http://blog.darkthread.net/blogs/darkthreadtw/archive/2008/09/02/coding-for-fun-contest-start.aspx)]。因為參賽題目 [xAxB猜數字遊戲] 原本就是考驗演算法，邏輯就不大簡單了，加上要配合 GameHost 的呼叫方式，難度更提高不少。因此之前貼了兩篇文章 [ThreadSync [#1. 概念篇 - 如何化被動為主動?](/post/Thread-Sync-1-e6a682e5bfb5e7af87-e5a682e4bd95e58c96e8a2abe58b95e782bae4b8bbe58b95.aspx), [#2. 實作篇 - 互相等待的兩個執行緒](/post/Thread-Sync-2-e5afa6e4bd9ce7af87-e4ba92e79bb8e7ad89e5be85e79a84e585a9e5808be59fb7e8a18ce7b792.aspx)]，介紹了我改寫的 AsyncPlayer，讓程式可以分別以獨立的執行緒執行 GameHost 及 Player 的程式碼。藉著這方式讓兩者都可以 "獨立思考"，邏輯不會中斷，讓程式能夠簡單一些。

不過執行緒同步機制是很花時間的，因為兩方都要等來等去...。多了 Sync 的動作，就要至少 10 ms 的時間來完成這動作。跑個十幾萬次下來，額外花費的時間太多了，因此我貼了那兩篇文章後，就一直在思考這樣的作法有沒有其它效能較佳的方式?

有的，最後我找到的答案就是 yield return，不過大家看了一定很納悶...

**_"yield return (Iteration) 跟執行緒同步機制有什麼關聯?"_**

不多說，先看看之前畫的兩張時序圖:

![image](/images/2008-09-22-csharp-yield-return-2-alternative-application-thread-sync-replacement/image_6.png)

先看之前 ThreadSync #1 裡提到的圖，我這次加上紅線當 "輔助線"，紅線代表執行 GameHost 的主程式，這個執行序必需反反覆覆的在 GameHost / Player 兩份類別的程式碼跑來跑去，主程式是 GameHost 發起的，當然被強迫切成好幾段的就只有 Player 了。

![image](/images/2008-09-22-csharp-yield-return-2-alternative-application-thread-sync-replacement/image_5.png)

這是修改過後的版本，GameHost / Player 有各自的執行緒，紅色是 GameHost，藍色是 Player。當執行緒跑到中間時代表它在等待了，等另一方也跑到中間把執行結果放到共用變數，同時叫醒對方之後才交換過來。兩方都各自照著自己的邏輯跑，不過這種等待 & 喚醒的動作，相較於一般的 function call / return 而言，實在是太慢了...。我就是從這張圖得來的靈感，這個解決方式不就跟 yield return 很像嘛? 都是為了避免多次呼叫之間，被呼叫的另一方的邏輯被破切斷的問題... 因此我就開始思考 AsyncPlayer 是不是有機會用 yield return 寫出另一個版本...。

原本的結構很直覺，透過共用變數來傳遞資訊，用 AutoResetEvent 來通知另一個等待中的執行緒可以醒來拿資料去用。而 yield return 則要換個角度來想這件事。yield return 是實作 Iterator 的一種方式，目的是讓你的程式自己決定如何把 collection 裡的 element 照什麼方式丟出去，原本的問題就要想成:

"GameHost 要跟 Player 拿所有 Player 會問的問題，而 Player 會透過 yield return 一次一次的把問題丟出去。"

看起來好像可行，不過方向只有單向，就是 Player 丟問題給 GameHost，還缺了 GameHost 把問題答案交給 Player 這段。不過這部份好解決，一樣用共用變數就搞定。細節我就不講太多，直接來看程式碼:

**用 yield return 改寫過的 AsyncPlayer**
```csharp
        public abstract IEnumerable<HintRecord> Think();

        private HintRecord last_record = null;

        public override int[] StartGuess(int maxNum, int digits)
        {
            base.StartGuess(maxNum, digits);
            this._enum = this.Think().GetEnumerator();
            this._enum.MoveNext();
            return this._enum.Current.Number;
        }

        public override int[] GuessNext(Hint lastHint)
        {
            this._enum.Current.Hint = lastHint;
            if (this._enum.MoveNext() == true) return this._enum.Current.Number;
            throw new InvalidOperationException("Player Stopped!");
        }

        public override void Stop()
        {
            base.Stop();
            this._enum.Current.Hint = new Hint(this._digits, 0);
            try { this._enum.MoveNext(); }
            catch {
                Console.WriteLine("!!!!");
            }
        }

        protected virtual HintRecord GameHost_AskQuestion(int[] number)
        {
            this.last_record = new HintRecord(
                (int[])number.Clone(),
                new Hint());
            return this.last_record;
        }

        protected HintRecord GameHostAnswer
        {
            get
            {
                return this.last_record;
            }
        }
```

程式碼一如往常，又是只有一點點 (謎之音: 你到底有沒有寫過長一點的程式碼? -_-) ...。 原本的 Think 改成會傳回 IEnumerable<HintRecord> 的型別，因此內部就可以透過一連串的 yield return xxxx; 指令來把問題交給 GameHost。而 GameHost 拿到題目就會開始計算答案，然後再呼叫 Player.GuessNext( ) 把上次的答案傳回去。透過 Player 的實作，GuessNext 會呼叫 _enum.MoveNext( ), 控制權會再交到 Think( ) 上次呼叫 yield return 的地方，直到又執行到下一個 yield return 為止。這時 GameHost 又取得下一個問題，不斷重複這樣的動作直到結束。

同樣的，我們用 DummyPlayer 改寫，看看用 yield return 的版本寫起來是怎麼樣?

**DummyYieldPlayer 的程式碼**
```csharp
    public class DummyYieldPlayer : YieldPlayer
    {
        private Random _rnd = new Random();
        private int[] randomGuess()
        {
            int[] _currAnswer = new int[this._digits];
            List<int> lst = new List<int>();
            for (int i = 0; i < _digits; i++)
            {
                int r = _rnd.Next(_maxNum);
                while (lst.Contains(r))
                    r = _rnd.Next(_maxNum);
                lst.Add(r);
                _currAnswer[i] = r;
            }
            return _currAnswer;
        }

        public override IEnumerable<HintRecord> Think()
        {
            while (true)
            {
                yield return this.GameHost_AskQuestion(this.randomGuess());
            }
        }
    }
```

跟上次的 DummyAsyncPlayer (用 ThreadSync 的版本) 一樣，超簡單，實在沒什麼需要說明的了。唯一要特別記得的是，如果你需要取得 GameHost 傳回的答案，應該在 22 ~ 23 行之間，使用 this.GameHostAnswer( ) 來取得答案。有人問我為什麼不把它包成 function call ? 在 function 內接到參數後呼叫 yield return, 而把答案 return 回來不是很好嗎?

很無奈，除非 C# 支援像 C/C++ 那樣的 MACRO 語法，不然這個東西是不可能單靠 yield return 就做出來。你使用 yield return 的條件就是 function return type 一定要是 IEnumerable<T>，這是配對的，代表你不能任易的把 yield return 移到其它 function call 內。除非你不靠 C# yield return 來自動產生對應的 IEnumerator，一切自己來就可以。不過這樣不就又回到原點了? 咳咳... 就乖乖的寫兩行吧。

這樣的寫法執行效率就好的多，我用 DummyYieldPlayer 來測試，跟 DarkThread 提供的版本不相上下，意思是差異小到可以不理它的地步了 :D 這樣的方式不會有太大的效能損失，因為最後要執行的程式碼，跟直接手寫是差不多的，只是中間難寫的那段 code 是 C# compiler 幫我們解決掉，而不是像上回 AsyncPlayer 是用兩個執行緒來解決的。

效果很滿意，當然最後參賽的版本就改這寫法了 :D。不過寫的太晚，來不及幫到其它參賽者 :P，想到這方法算是我佔了 C# compiler 一點便宜，有幸找到方法坳 C# compiler 幫我把最難的部份寫好了，我自己則樂的輕鬆，專心研究怎樣才能少猜幾次... 這裡把我另類應用 yield return 的方法貼給各位參考一下，也算作個筆記 :D，各位高手如果還有發現 yield return 解決過你什麼樣的怪問題，也歡迎到我這留個言 :D