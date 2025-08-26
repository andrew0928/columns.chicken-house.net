先講在前面, 我是很不喜歡這種無聊的網站... 擋右鍵幹嘛? 也許站長真的覺的他的內容很了不起大家都想偷... 不過右鍵按下去一堆功能, 又不是每個人點右鍵都是要偷內容... 被當小偷看待的感覺真的挺不爽.. 真的要看, fillder 開下去什麼都看的到..

好, 牢騷發完了 (H), 今天不是要講這個.. 因為工作的關係, 開發的系統是處理企業內部的 web content, 免不了有這種檔右鍵的需求, 這種 code 大家或多或少都寫過, 不過都寫的很煩吧...

"什麼!!! 每一頁都要檔?"

"每一頁都加 code 要加到什麼時後..."

接到這種需求大概都想扁人吧, 咳咳... 我就是因為懶所以想到一招省事的... 先來看一下這個網頁, 看看大家追不追的到右鍵是怎麼擋的...

[test html page](http://www.chicken-house.net/files/chicken/htc-sample.zip/index.html) ([full source](http://www.chicken-house.net/files/chicken/htc-sample.zip))

看出來為什麼右鍵被停用了嗎? 沒有 script tag, 也沒有 include 啥鬼東西, 開這個 page 的 link 也沒動啥手腳... 開 page 時 ie 也沒要求下載啥奇怪的軟體...

不過, 右鍵的確是被 disable 了, 秘密就在這段 css ..

`body { behavior:url('context-menu-blocker.htc'); }`

這是 Microsoft 在 IE5 之後就引進的 DHTML Behaviors. CSS 是為了樣式而設計出來的, 目的就是希望一組網頁只要有共通的樣式, 就不用每一頁去調字型顏色等等... 只要透過 CSS 就可以把整個網站的每一頁, 在特定 tag 套用特定的樣式...

"只能套用外觀嗎? 如果程式也可以這樣撒出去就好了"

沒錯, behavior 就是這個目的, 把你想怎樣 "改造" 這個 tag 的 script 寫在 .htc 裡, 再用 css 把它綁到 tag 上, 一切就完成了.

這個例子的 htc 只有去攔捷 oncontextmenu 事件, 攔下來後只有做取消事件的動作而以. 藉著 css 就可以把這功能套用到 page 上了... 當然, 你的網站有 css 的話, 這個功能馬上就套用到你所有的網頁了.

這些技巧果然說穿了就不值錢... 咳咳, 不過 HTC 還有很多其它更讚的應用, 因為它很精巧的把 code 跟 tag binding 處理的很好, 很可惜這技術好像不大登的上抬面, 用過的人似乎不多, IE5.0 推出後, IE5.5 對 htc 有些改進, 之後就沒有啥新的進展了..

不知道 IE7 對 htc 有啥改進? 有空再來試試了 :D