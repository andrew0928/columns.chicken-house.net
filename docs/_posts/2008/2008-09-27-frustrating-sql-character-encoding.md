---
layout: post
title: "令人火大的 SQL 字元編碼..."
categories:

tags: ["SQL","Tips","火大"]
published: true
comments: true
redirect_from:
  - /2008/09/27/令人火大的-sql-字元編碼/
  - /columns/post/2008/09/27/SQL-BUFFER-OVERFLOW.aspx/
  - /post/2008/09/27/SQL-BUFFER-OVERFLOW.aspx/
  - /post/SQL-BUFFER-OVERFLOW.aspx/
  - /columns/2008/09/27/SQL-BUFFER-OVERFLOW.aspx/
  - /columns/SQL-BUFFER-OVERFLOW.aspx/
wordpress_postid: 66
---
今天同事有個問題搞不定，就找我去處理，越弄越火... 嘖嘖，這裡就來還原一下現場，記錄一下這個鳥問題...。

最討厭處理這種問題了。現在客戶 IT 都委外，結果就變成 IT 本身不大管事，什麼事就交給外包商就好... 而這種 A 包商跟 B 包商之間的問題，往往就變成踢皮球... 除非有明確證據指出人就是他殺的，不然? 出問題的一方自己摸摸鼻子吧。幾年來吃了不少這種虧，這就是小廠的悲哀啊。

這次碰到的例子是客戶 A 系統建的資料，需要整理後匯到我們負責維護的 B 系統。而中間資料需要作些修正，所以建了一個中繼資料庫，透過 LINKED SERVER，從 A 系統的 DB 把整個 TABLE SELECT 一份到中繼資料庫，然後再進行一連串的修正...

![image](/wp-content/be-files/WindowsLiveWriter/SQL_11CC/image_7.png)

一開始問題很單純，就兩邊碰到中文字編碼不同，直接 SELECT 就碰到這樣的亂碼..

![image](/wp-content/be-files/WindowsLiveWriter/SQL_11CC/image_8.png)

看起來是個小問題，請對方 IT 確認了編碼的問題後，我在中繼資料庫作了點調整，convert 成 ntext 就搞定了。已經可以跑出正確的中文資料了。

正想把程式弄一弄就收工，然後很得意的回報問題搞定時，發現不大對勁，怎麼整個 BATCH 跑下來結果還是錯的? 還錯的不一樣? 真是奇了... 原本轉 UNICODE 問題，再怎麼樣也應該只是變亂碼，或是變 ? 而以，結果這次看到的是資料錯亂，跑出其它的字出來...

![image](/wp-content/be-files/WindowsLiveWriter/SQL_11CC/image_9.png)

這張圖是我把問題簡化後抓到的，原本是有上百行的 SQL SCRIPT ... @_@ 被我抽絲撥繭剩這段。第 33 筆資料是有問題的，不過出現的資料不是原本 "馥瑈" 啊，原本是第二個字變成 ? 而以... 現在竟然變成上一筆資料 (第32筆) 的內容，而第三個字 '榮' 則是由前面好幾筆的 "XX榮" 留下來，第四個字 "子" 就真的不曉得從那裡來了...

好怪的問題，如果是程式碰到這種 BUG，一看就像某個 BUFFER 沒清掉就一直重複被使用，後面的值直接蓋掉前面的值，字串長一點沒被蓋掉，就這樣留下來了。而到了第 33 這筆不知為什麼原因，整個 BUFFER 的內容就跑出來... 這段 SQL SCRIPT 跟本沒作什麼事，不過是前面的 SELECT 指令，改 SELECT INTO 到 TEMP TABLE，然後再撈出來而以。直接 SELECT 沒問題，沒道理 SELECT INTO 就掛掉啊! 不過還真的被我碰到了，see the ghost ..

我沒有直接拼下去 GOOGLE 或是試各種解法，而是想了一下問題是怎麼回事? SQL / DB 的東西我只算外行人，沒本事跟他硬碰硬，我也不知道有啥工具可以看 SQL NATIVE CLIENT 的 TRACE INFO 之類的，只能靠想像，猜一下問題會在那。一開始我就否定掉是不是什麼編碼或是定序的問題，因為我可以正確的 SELECT 出來啊，而且如果 SELECT INTO 是變成 ?? 的話我也許還會頭痛一點，不過竟然是上一筆的資料跑過來了? 這個問題很明顯的，跟本就是 overflow (緩衝區溢位) 之類的 BUG。八成是什麼地方應該填個 0x00 作字串結尾的 CODE 錯掉，結果 SQL 就抓過頭，抓到不該抓的舊資料才會這樣。

拿我寫了十幾年程式的經驗，跟它賭下去了!! 於是我就沒再去跟一堆編碼定序之類的設定搏鬥了，因為我認定這是 SQL SERVER 或是 SQL NATIVE CLIENT 的 BUG。我採的方案是找可以繞過去的方式，於是我把我想的到的 COPY TABLE 都用上了，最後試出來的是笨方法...

**_用... 用... 用 CURSOR 一筆一筆的跑... @_@_**

哈哈，各位看倌請笑小聲一點，我這貴州的驢子就只會這種把戲而以.... 果然這樣就正確了。CURSOR 的 FETCH 指令，把欄位的值抓到 nvarchar 的變數，就一切 OK，然後再把這變數的值 update 回我的暫存 TABLE，就什麼問題都沒了 -_-

真是它ㄨㄨㄨㄨ的，最後的 SOLUTION 細節我就不一一的貼出來了，反正只是換個方式 COPY TABLE 而以。既然我賭是 Microsoft 的問題，而換條路的方式 (完全沒改任何定序 OR 編碼) 也成功了，我就不跟它奮鬥下去了，客戶的 IT 既然懶的上 UPDATE / SERVICE PACK，我也只好避掉問題了事... 咳咳。特地貼出來記念一下，如果你們也碰到一樣的問題，切記切記，別跟它硬碰硬啊... :D
