---
layout: post
title: "換到 BlogEngine.Net 了!"
categories:

tags: [".NET","BlogEngine.NET","Community Server","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2008/06/17/換到-blogengine-net-了/
  - /columns/post/2008/06/17/e68f9be588b0-BlogEngineNet-e4ba86!.aspx/
  - /post/2008/06/17/e68f9be588b0-BlogEngineNet-e4ba86!.aspx/
  - /post/e68f9be588b0-BlogEngineNet-e4ba86!.aspx/
  - /columns/2008/06/17/e68f9be588b0-BlogEngineNet-e4ba86!.aspx/
  - /columns/e68f9be588b0-BlogEngineNet-e4ba86!.aspx/
wordpress_postid: 99
---

也許有人只是覺的換版面而以... 原本是打算升級到 [CommunityServer 2008](http://communityserver.org) 的，不過自從 Community Server 商業化之後，個人版限制越來越多，整套系統也越來越大，常常出了一些問題都沒辦法自己解決 (連 Error Message 都藏的很隱密 -_-)...

其實上面這些也不算缺點，不然我也不會一路從 .Text 時代就用到現在，一用就用了四年多... 上禮拜無意間聽同時講到 [BlogEngine.Net](http://www.codeplex.com/blogengine)，一時好奇抓下來看看，馬上就被它的簡易安裝嚇到了.. 有多簡單? 步驟如下:

1. 下載
2. 解開
3. 設定 IIS 虛擬目錄 / 用 DEV WEB 執行它
4. 完成了

我已經很努力的把它寫複雜一點了... 它安裝就是這麼簡單，因為它可以不需要 DB (用一堆 XML 檔取代)，因此一行 web.config 都不用改就可以用了... 驚喜之餘，也吸引我更深入的多試了幾個功能...

基本功能試過一次之後，發現它比 CS 還符合我的須要，怎麼說?

1. **很簡單**  
   不只是設定簡單，它的功能也很專一，就是一套BLOG而以。沒有複雜的會員機制，也沒有帳號申請，也沒有多套BLOG管理 (不過它支援多個作者)，除了 BLOG 也沒有其它功能... 不多不少，正好我要的都有!

2. **Open Source**  
   雖然 CS 也有 Source Code 可以看，不過它的原始碼越來越難找了... 每次逛它的網站都要找半天才找的到 SDK 在那裡下載...

3. **不需要 DB**  
   雖然我自己 HOSTING 我的網站，DB並不是什麼大問題。不過不需要 DB 對我也是個大利多。一方面網站備份更容易，另一方面除錯及改程式也更容易... 更好用的是，未來我可以把整個網站目錄燒到 DVD 上 (不過兩百多篇文章，不到100MB，燒什麼 DVD...)，只要再搭配 .NET 附的 DevWebServer，做個 AutoRun ... 想到可以幹嘛了嗎? 我的 BLOG 馬上就變成一份可以放在 CD，需要時就可以就地用 BROWSER 來看內容了!

4. **CODE 精簡，程式碼架構佳**  
   這點又免不了跟 CS 拿來比較一下... CS 的作者也是高手，CODE寫的很漂亮，不過跟 BE 最大的差別是，CS實在太肥了。肥到什麼功能都要繞個兩三圈... 要修改雖然不難，但是都要花點時間...

5. **免費! 免費!**  
   心理作用，其實賣錢的 CS 送的免費版本，功能比完整的 BlogEngine.NET 還多... 不過商業化之後難免會有些功能得付費才能使用... Orz

6. **小巧，易用，速度快**  
   CS 即使是在 LOCAL 執行，速度都沒辦法讓人覺的 "飛快"，但是換了 BlogEngine.Net 就有這種感覺... 我目前的文章只有兩百多篇，不靠 DB 的速度都還很快。我試過灌了1000篇文章，速度依然很快... 我想這樣就夠了，我要寫到破千篇，不知道還要多久?

光是這幾個優點，就讓我決定試用只有一天的 BlogEngine.NET 換掉用了四年的 CS ... 剩下的問題只有 "怎麼轉" ? 各位看到現在都成功搬過來，那一定是搞定了... 哈哈... 沒錯，周末花了兩個晚上研究 + 寫匯入程式，今天就重新開張了 :D

轉檔的過程，改天再寫另一篇，有興趣的朋友請耐心等待續集...
