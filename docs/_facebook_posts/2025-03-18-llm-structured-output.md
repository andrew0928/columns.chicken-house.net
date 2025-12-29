---
date: 2025-03-18
datetime: 2025-03-18T20:22:31+08:00
timestamp_utc: 1742300551
title: ", LLM - Structured Output"
---

#1, LLM - Structured Output

這是我在 .NET Conf 2024 的其中一張簡報, 今天想聊一下這題..

>
> Developer 應該怎樣善用 AI?
>

別誤會了，我沒有要聊 GitHub Copilot / Cursor 寫 code 有多厲害, 那個大家講到爛了, 我來講並沒有比較厲害, 反正用 AI 輔助 coding 早就不可逆了, 用就對了。我要談的是, 如果把 LLM 當作你的可用套件或是服務之一, 你會怎樣應用在你的 Application? 當 LLM 在各位開發人員手上, 各位你知道你手上的武器有多大的威力嗎?

這頁簡報，談的是先進的 LLM ( 我拿 GPT4o-mini 當分界 )，開始正式支援 Json Schema. 圖中的例子是要從一段對話, 擷取出對話中提及的那家 tea shop 正確的 address .. 如果這是別人問我的問題，我第一時間的反射動作一定是:

>
> ChatGPT, 告訴我下列對話提及的地址...
> (貼上對話內容)
>

如果我還有其他雜七雜八的要求，我一定一起丟給 ChatGPT 幫我處理，例如找出附近的景點，或是多告訴我那個地點的相關資訊等等。但是 ( 就是這個 BUT )，如果這功能是要埋在你某個 application 內呢? 如果你有幾百萬組這樣的對話，你都要抽出地址資訊呢?

反射式回答: 那就 call chat-completion api 就好了啊...

不過，你是 Developer, 你其實可以想得更多一點。我試著多列幾個思考題:

1. 你要 LLM 用什麼格式回答你?
2. 如果有 1% 的機率 LLM 回答不出來，你程式能怎麼判斷?
3. 你還該讓 LLM 處理雜七雜八的要求嗎? 通通寫在 prompt 讓 AI 一氣呵成比較好? 還是取得地址後自己打 google map api 處理比較好?

開發應用程式就是這樣，依靠開發團隊的經驗，把處理過程寫成應用程式，使用者就能站在你的肩膀上不用再踩一次地雷。如果你的服務使用量夠大，你的一念之間的決定可能影響著巨大的效率提升..

這才是身為 Developer 的職責，也是身為 Developer 的優勢。這世界有更多這種新的服務需要開發，要讓 AI 來開發 AI 的應用程式，現階段也還沒那麼容易，這會是 Developer 大顯身手的地方。回到這題來看，你會發現你平常在 ChatGPT 下的 prompt, 都不見得適合直接拿到程式內使用。

那麼怎麼弄才是 Developer 的作法?
上面的問題，我的答案是:

1. 用 Json output
最好還能定義 Json Schema, 拿到結果後立刻 deserialize 成 C# object, 以利後續讓非 AI 的程式碼能無縫的接手處理。

2. 直接在 output 就 "明確" 標明執行結果成功或失敗 
(就像 HTTP status code 一樣)，不要用猜的，對你好，對 LLM 也好。明確的讓 AI 輸出能否判定答案 (輸出地址)，比起你自己 parsing 後再丟出 exception 優雅的多。LLM 的幻覺跟不確定性已經夠多了，不需要多妳一個..

3. 單一職責，只讓 LLM 處理非他不可的任務就好。
其餘任務，只要用 json 傳出必要資訊，用程式碼來處理就夠了。講直白一點，搜尋，格式轉換，數值計算等等，這些都是 code 來處理遠遠強過 LLM 的領域。你不需要為了少打那幾行 code (都可以 AI coding 了)，結果原本幾百個 CPU instructions 能處理完畢的事情，變成每次都花費幾百個 tokens 才能處理... 你知道一個 Azure Function Call 的費用，跟一個 ChatCompletion API Call 的費用差多少嗎? 別忘了妳的決定會被放大 100 萬倍....

所以，回到這張簡報，你知道為何你該了解 LLM 的 Json Mode 了嗎? 實際的 code 我就不貼了，這是我在 03/25 直播的前半段會提及的 AI APPs 開發基本技巧的內容 XDD，因為我必須交代完他，我才能讓大家充分體驗我要談的主角: Microsoft Kernel Memory 啊 ...

當天，這個案例 (還包含接下來我每天會貼一則案例)，我會用 OpenAI 的 ChatCompletion API 當基礎，我會分享:

- 用 Http Client 示範
- 用 OpenAI .NET SDK 示範
- 用 Microsoft Semantic Kernel 示範

用不同方式寫這段 code... 其實有很大的差別。SDK 相依姓的取捨，跟帶來的便利，你要懂得之間的差別。別以為只是 call API 就結束，如果你看到你 call api 要自己寫 json schema, 而用 semantic kernel 的時候只需要給 C# type, 你的想法就會改變了...

好，胃口就吊到這邊，有興趣的記得參加 03/25 我跟保哥合辦的直播，相關連結我放在第一則留言😀

![](/images/facebook-posts/facebook-posts-attachment-2025-03-18-002-001.png)
