Overview.aspx/
  - /post/2008/05/16/FlickrProxy-1---Overview.aspx/
  - /post/FlickrProxy-1---Overview.aspx/
  - /columns/2008/05/16/FlickrProxy-1---Overview.aspx/
  - /columns/FlickrProxy-1---Overview.aspx/
  - /blogs/chicken/archive/2008/05/16/3238.aspx/
wordpress_postid: 106
---

久久沒動手寫 code，手又開始癢了... 前陣子跟[小熊子](http://michadel.chicken-house.net/blogs/)聊的時後想到一個新的 IDEA，就順手記下來。像我們這種自己用ADSL架的小型網站，瓶頸都是卡在頻寬。愛拍照的[小熊子](http://michadel.chicken-house.net/blogs/)最在意的當然就是網站擺照片所需要的頻寬... 解決方式其實有一堆，像是 Live Writer 就有個很有名的 [PLUGIN](http://www.flickr4writer.com)，可以直接插入你放在 Flickr 的照片...

其實這類的 solution 很多，但是用起來就覺的不大喜歡，怎麼說? 倒不是說軟體不好用，而是它的作法。這類 plug-ins 都是幫你一次把事情作好，幫你上傳到 [flickr](http://www.flickr.com/)，幫你查出 link，幫你產生HTML片段，貼到 WLW... 這種作法的問題在於你張貼文章時，這些資訊就得確定下來。你沒辦法裝了這個外掛，就把你八百年前貼的照片一起轉到 flickr，你也被這個外掛還有你的 flickr 帳號綁死了，未來換帳號的話，或是你沒有 WLW 可以用時，這些功能都沒有了。

我比較喜歡的是 server side 的 solution，如果是透明的 (像 PROXY) 更好，如果隨時可以不要或是改設定最好，這樣我不但不用綁死在我的某個 flickr 帳號上，甚至不用綁在 flickr 這樣的服務...

過去 (沒想到已經快四年了 -_- ) 其實我作過幾個類似的 [HttpHandler](/post/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx)，都是用一樣的理念去開發的。這次想的是利用 Flickr 提供的 API，來做一樣的事。

簡單的說，如果我能夠寫個程式，能夠在 Run Time 動態去檢查網站上某張圖檔有沒有傳到 flickr 上? 如果沒有且判定不需要，則像一般網站一樣直接在 Http Response 傳回圖檔的內容。如果需要則自動上傳到 flickr，最後把這個 Http Request 重新導向到 flickr 上的照片網址。

這樣作法最後的結果跟 WLW 搭配 flickr plugins 差不多，差別在一個是靠 client 端，在你張貼文章時幫你處理掉一連串的動作，我的作法是統一在 server 端，在觀看文章內容時才做這件事。效能一定不如 WLW + Flickr plugin 好，不過就是多了彈性。我可以隨時關掉這個功能，隨時換相片服務，另一個更重要的是我自己保有一份完整的網站跟檔案資料。如果我的 BLOG 資料散在各地各個服務，我要備份或是還原等等也都很辛苦...

講了一堆都是廢話，其實這篇主題只有一個，就是想到好點子又要開始動手寫 code 了 [:D] ，有點成果之後會陸續在貼幾篇相關的文章。在之前作了 [POC](http://demo.chicken-house.net/MediaProxy/storage/GoogleNews.htm "PS: Google News 存下來的 HTML，所有的圖檔都用這樣的作法轉到另一個目錄，有興趣的可以開 Fiddler 看看就知道") ( Prove Of Concept )，證明這個技巧是可行的，剩下的就是真正動手寫了。另外也有一個目的，就是想把[之前寫的另外兩個 HttpHandler](/post/e4b889e5808be5a5bde794a8e79a84-ASPNET-HttpHandler.aspx)整合起來，弄成統一的 provider 架構來實作。

想的很美，照片就轉到 Flickr，影片就轉到 [YouTube](http://www.youtube.com/) ... 不過影片那邊的難度就高的多了，現在的實作只是從 HTTP 自動轉到 RTSP 而以.. ZIP 檔現在是虛擬化成一個資料夾，未來看看能不能自動轉到 [Microsoft SkyDrive](http://skydrive.live.com/) 之類的服務....

好，先寫到這裡，敬請期待下集 [:D]