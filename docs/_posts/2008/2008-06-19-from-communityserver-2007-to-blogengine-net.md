---
layout: post
title: "從 CommunityServer 2007 到 BlogEngine.NET"
categories:

tags: [".NET","BlogEngine.NET","Community Server","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/06/19/從-communityserver-2007-到-blogengine-net/
  - /columns/post/2008/06/19/e696b0e5b185e890bde68890-e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /post/2008/06/19/e696b0e5b185e890bde68890-e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /post/e696b0e5b185e890bde68890-e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /columns/2008/06/19/e696b0e5b185e890bde68890-e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /columns/e696b0e5b185e890bde68890-e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /columns/post/2008/06/19/e696b0e5b185e890bde68890---e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /post/2008/06/19/e696b0e5b185e890bde68890---e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /post/e696b0e5b185e890bde68890---e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /columns/2008/06/19/e696b0e5b185e890bde68890---e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /columns/e696b0e5b185e890bde68890---e690ace5aeb6e9818ee7a88be79a84e4ba94e59b9be4b889.aspx/
  - /2008/06/19/從-communityserver-2007-到-blogengine-net/
wordpress_postid: 96
---

哈，不是我要搬家了，是網站搬家... 搬家是想了很久沒錯，只是決定搬到 BlogEngine.Net 倒是沒花幾天的時間，所以準備動作也是有點 LiLiLaLa .. 從 CommunityServer 這種成熟的系統搬到還很年輕的 BlogEngine.Net，其實碰到不少小麻煩，在這裡記錄一下給需要的人參考，也算功德一件! 

要搬 BLOG，最直覺的就是用 [BlogML](http://blogml.org/) 了，不錯，我用的 CommunityServer2007 [有工具](http://www.codeplex.com/BlogML/Release/ProjectReleases.aspx?ReleaseId=171)可以匯出 BlogML，而 BlogEngine.Net 也有工具可以匯入 BlogML，想想真是太好了... 就先用 DevWeb 架了 BlogEngine.Net 起來試搬看看.. 

![image](/images/2008-06-19-from-communityserver-2007-to-blogengine-net/image_8.png)

BlogEngine.Net 匯入的方式，是用 ClickOnce，直接從它的官方網站下載的 WinForm App 配合 BlogEngine.Net 本身提供的 Web Service 來進行匯入 BlogML 的動作，除了 BLOGML 之外也支援 RSS? 不過 RSS 怎麼試都試不出來，放棄... 直接用 BlogML ... 

![image](/images/2008-06-19-from-communityserver-2007-to-blogengine-net/image_7.png)

畫面很乾淨，它也很忠實的完成了它的工作... CommunityServer2007 的 BLOGML 匯入時出了點問題，文章的修改時間不知為何，BlogEngine.Net 都一直抓到 0000/01/01 00:00:00.000 ，而BlogEngine.Net 還會幫你修正時區的問題 (台灣時區，要 -8 小時才是標準時間)，結果一扣就變成負的，就送我一個 Exception ... Orz 

匯入的第一步就得動用到 Visual Studio 2008，真不是好兆頭... 所性拿掉那行程式，就一切沒問題了，順利匯入! 架了台測試網站，研究了一兩天，實在是有點不滿意... 

1. **LINK 不對**  
   Windows Live Writer 很好心的幫你把上傳的圖檔都用絕對網址來表示，因此所有的圖都連回原本的網站，正常顯示沒有問題。不過搬家那有這樣搬的... 改!!!
2. **只搬了BLOG，文章沒有搬**  
   只怪當時年輕，無聊去用 article 的功能，造成部份是 BLOG 文章，部份是 ARTICLE。CommunityServer2007是都有忠實的匯到 BLOGML，不過 BlogEngine.Net 的匯入工具略過它了... 改!!!
3. **站內 LINK 不對**  
   圖檔 LINK 還好修，字串換一換就搞定，不過站内的文章戶連才是個問題... 改!!!
4. **站外 LINK 不對**  
   其實這一點是搬完家才發現的，剛搬好 PAGE VIEW 低的可憐... 看一看 LOG 都是 404 Page Not Found ... 改!!!
5. **沒有 COUNTER**  
   BlogEngine.Net 說實在話，以BLOG來說功能一點都不缺，不過很怪，竟然沒有最基本的 VIEW COUNT ? 所幸 BlogEngine.Net 有定好 Extension 的架構，要寫它的擴充程式很簡單，有個高手寫了 BlogEngine.Net 的 [View Count Extension](http://mosesofegypt.net/?tag=/blogengine.net+extensions)... 畫面不怎麼樣，不過很實用... 裝!!!
6. **原有的 VIEW COUNT 沒匯入**  
   廢話，BlogEngine.Net 本來就沒內建 VIEW COUNT，那是我自己裝了擴充程式才有... 資料要匯，當然也只能自己想辦法 :~~ 改!!!
7. **版面問題**  
   標準的版面我很喜歡，就是我要的那種素素的 STYLE，很標準的 ASP.NET Master / UserControl 架構，太棒了... 我要求的也不多，就放放廣告 (看廣告收益很有意思耶，好像電動裡打怪會賺錢或是經驗值那樣... 真的賺多少其實也不重要 :D)，還有幾個我自己寫的 CONTROL ... 改!!!
8. **我在CommunityServer加的功能**  
   沒辦法，自作孽，改了一堆只能自己搬... 有好幾個: 
   - Google Ads (可以用)
   - FunP 推推王 (沒在用了)
   - ~~Recent Comments~~ (已經有內建，可以扔了)
   - ~~皮哥芸妹年齡~~ (跟太座的網站分家了，我這邊就不需要了)
   - Bot Check (還沒搞定要怎麼改 :~)
   - Code Formatter 在 BLOG SERVER 要配合的部份

上面這幾點，都是搬家時或多或少會碰到的小問題，不過很想哭的是，這六個最後都是搬出 Visual Studio 2008 出來才搞定的 @_@，什麼意思? 就是自己寫 CODE 來修啦... 真不知道該誇還是該罵，也因為這樣有機會 Trace 幾次它的 Code，忍不住想再誇它一次，要建起開發環境實在太容易了 :D 哈哈...  它的 CODE 很精實，CODE 不多，架構很好，規規舉舉的很容易懂，這種 CODE 改起來真舒服.. (為什麼公司的 CODE 都沒有像這種的...)，修改的難度大概只有 CommunityServer 的 1/3 .. (CommunityServer的作者很猛，把 Microsoft 在 2.0 才推出的那套架構在 1.1 時代就都實做了一套 :Y) 

現在還有空在這裡慢慢打，當然是這些問題都解決完了，先看看成果吧，細節有空再補 HOWTO 文章。那些 LINK 不對的問題，各位翻翻舊文章，如果都看的到圖點的到東西，就是沒問題了。有問題的請再留話給我，我來修看看。 

![image](/images/2008-06-19-from-communityserver-2007-to-blogengine-net/image_23.png)

來看看加上 Google Ads 的版面，老實說這個版跟 Google Ads 還真搭... 看起來就像同一套的.. 我只調了 CSS ，跟 MASTER PAGE.. 

![image](/images/2008-06-19-from-communityserver-2007-to-blogengine-net/image_22.png)

再來是站內文章互連的 LINK。這邊讓我傷了幾秒鐘的腦筋... 就放棄原本只想寫寫批次檔代換的念頭了。轉檔前跟本不知道轉檔後的新 LINK 是長什麼樣子，轉檔後就錯失先改好 BLOGML 再匯入的機會了... 想了一下，無解，一定要動用到 2 PASS 才行... 就乖乖的改轉檔程式了。第一輪就是基本的匯入，然後在原本的 BLOGML 附記新的 LINK 及 BlogEngine.Net 的 PostID，然後 PASS 2 再把舊文章逐一翻出來 SEARCH & REPLACE ... 上圖可以看到，內文 [四核 CPU] 的 LINK (在底下) 就已經是修正過的了，各位可以去試看看... 

再來是站外的 LINK，站內我自己的可以改，站外可沒辦法... 拿最捧我場的 [Darkthread](http://blog.darkthread.net/) 網站為例，[搜尋一下](http://blog.darkthread.net/blogs/darkthreadtw/search.aspx?q=chicken)就有七八篇是連到我這邊，怎麼可以辜負大人的好意... 動搖國本也要改! 現在我的 BlogEngine.Net 已經可以接受舊系統的網址了，而且會正確的轉到同一篇文章的新網址。不過為了不讓大家 "不知不覺" 就轉過來，我特地加了一頁提示，因為書上教的，不要把錯誤隱藏起來 :D，你可以用防禦性的方式寫 CODE，但是務必加上 ASSERT 及 TRACE 提醒自己這裡要注意... (出自一本古董書: Writing Solid Code... 太古董了實在找不到 LINK ... ) 

![image](/images/2008-06-19-from-communityserver-2007-to-blogengine-net/image_21.png)

就挑這篇來示範吧，黑暗大哥的文章裡有個 LINK，存的是舊的 CommunityServer 格式 URL，點下去之後會跳到我的網站... 

![image](/images/2008-06-19-from-communityserver-2007-to-blogengine-net/image_20.png)

倒數完或是你沒耐性直接按下去的話，就會跳到這篇文章... BINGO，原本的內容出現了! 

![image](/images/2008-06-19-from-communityserver-2007-to-blogengine-net/image_19.png)

嗯，總算修正回來了。其實修正網址是搬家最頭痛的問題了，這個搞定其它都好說 :D  留給有興趣想從 CommunityServer 搬家到 BlogEngine.Net 的人參考... 

(小熊子別再撐了... 還有那個誰也是一樣...) 
