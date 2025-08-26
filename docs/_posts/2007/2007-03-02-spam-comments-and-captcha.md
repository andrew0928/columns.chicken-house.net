---
layout: post
title: "Spam Comments And CAPTCHA..."
categories:

tags: [".NET","作品集","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2007/03/01/spam-comments-and-captcha/
  - /columns/post/2007/03/02/Spam-Comments-And-CAPTCHA.aspx/
  - /post/2007/03/02/Spam-Comments-And-CAPTCHA.aspx/
  - /post/Spam-Comments-And-CAPTCHA.aspx/
  - /columns/2007/03/02/Spam-Comments-And-CAPTCHA.aspx/
  - /columns/Spam-Comments-And-CAPTCHA.aspx/
  - /blogs/chicken/archive/2007/03/02/2285.aspx/
wordpress_postid: 177
---

也許該值得高興吧, 本站都用 robots.txt 擋掉 google 等 search engine, 只因為目標只是放在給認識的人看的 blog, 不想太公開, 所以一直以來都相安無事. 一直到最近, 大概看的人變多了, 也被外面一堆不知名的 bot 盯上, 開始一直有一堆廣告的 comments 貼到 blog 上... [:@] 

試了 community server 內建的 spam rule, 是檔掉了一些, 不過仍然有一堆漏網之魚... 想想還是跟各大網站一樣, 找個 CAPTCHA 的元件來用用. 在 community server 官方網站提供了一套, 在 msn 問了 [darkthread](http://www.darkthread.net) 前輩, 他也提供了兩個網址, 也研究了一下... 

- [Clearscreen SharpHIP HIP-CAPTCHA Control for ASP.NET](http://blogs.clearscreen.com/migs/archive/2005/02/01/905.aspx)
- [http://blog.darkthread.net/forums/thread/575.aspx](http://blog.darkthread.net/forums/thread/575.aspx)

每次看到這種怪名字 (CAPTCHA), 就很想查一下它到底是啥字的縮寫, 查了 [wiki](http://en.wikipedia.org/wiki/Captcha), 原來是 "**<span style="color:red">C</span>**ompletely **<span style="color:red">A</span>**utomated **<span style="color:red">P</span>**ublic **<span style="color:red">T</span>**uring test to tell **<span style="color:red">C</span>**omputers and **<span style="color:red">H</span>**umans **<span style="color:red">A</span>**part" ... 比較有趣的是 turing test, 唸資工的大概都記得啥是 turing machine, 而 turing test 也是 Alan Turing 提出來的, 大意是在探討機器怎樣才算是有 "智慧" 的程度? 如果讓一個人 (測試者) 跟另一個真人及機器對話, 而測試者如果沒有辦法從對話內容中猜出誰是真人, 誰是機器, 就代表這個機器已經通過 turing test, 就算是具有某種程度的 "智慧", 而不只是會運算的計算機了... 

即使到現在, 連 IBM 深藍都打敗棋王了, 不過終究也只是運用高速的運算加上龐大的儲存空間, 超越人類對邏輯深度及廣度的挑戰而以. 這種比賽人類遲早會輸的... 像我打牌幾回合以前出過的牌都忘光光了... 哈哈... 不過這種還算不上是 "智慧". Microsoft 有兩個 msn bot 還蠻有趣的, 雖然一看就知道是 robot, 不過還能跟你聊上一兩句... 問問題也只要直接用白話打進去就好. 要跟它聊天很簡單, 只要把這兩個 account 加到你 msn messanger 的聯絡人... 

1. Encarta 百科全書: [encarta@botmetro.net](mailto:encarta@botmetro.net) 
2. 會講中文的 "聰明小孩" (只會簡體 :@): [smarterchinesechild@hotmail.com](mailto:smarterchinesechild@hotmail.com)

近來網站很流行讓你看一張圖, 然後要你把裡面的字 key 進表格內, 目的就是要判定填資料的是 "真人", 而不是 "機器"... 不過這樣就要套上 CAPTCHA, 就有點過頭了, 現在 CAPTCHA 已經變成這種作法的代名詞了, 這個字也被註冊過, 不能亂用... 不過人跟機器的辨識, 真的只靠這種圖片就可以解決了嗎? spammer 開使採用 OCR 的技術來反擊, 辨識率約有 80%, 但是剩下的 20%, 不知道有多少比例是連真人都認不出來的圖? 

辯別人跟機器的戰爭, 不應該只靠肉眼跟OCR做區隔, 人腦對資訊的 "理解" 能力是另一個關鍵... 如果有些問題是目前的 bot 回答不出來的, 那麼這就是個有效的辯別方式... 扯遠了, 我只不過是要講一下 CAPTCHA 的由來而以 [:P]... 不過老實說, 我還真不喜歡網站加這些東西, 毫無意義的文字, 有些已扭曲到我真的看不懂 [:|] 連 I 跟 1, 0 跟 O 也都分不出來, 還要試好幾次才過, 嘖嘖... 為了防 spammer 苦了人... 但是為了保障我自己家的 blog 不受 spammer 侵襲, 還是得試一試. 上面提到的那幾套, 都很盡責的能正常的運作, 不過看了就是不大爽... 

"<span style="color:green">如果有些問題是目前的 bot 回答不出來的, 那麼這就是個有效的辯別方式... </span>" 

想想也沒幾行 code, 就自己寫了一個簡單的. 反正暫時還不會有 spammer 針對我的 blog 寫破解的程式吧 [H], 我採用的方式是隨機產生一些問題, 要 user 輸入正確的答案, 答對才判定你不是 robot ... 當然這些問題都不難... 目前做的問題有三大類: 

1. 簡單的數學問題, 就兩個個位數字的運算. 
2. Echo. 題目只是很簡單要你跟著打一段字而以... 
3. 靜態的題庫, 另外在 xml 檔裡先建好題目 & 答案的配對, 隨機挑一題出來...

Code 本身倒是很簡單, 完全沒有什麼特別的, 我就不講了. 為了 deployment 方便, 我連 code 都藏到 .ascx 裡了... 沒有其它的 .cs 跟 .dll 要安裝, 純脆以方便為原則. 

這方法只是簡單的題庫測驗的簡化版而以. 它跟真正的 turing test 仍然有好大一段差距. 因為 tester 也是機器, 不是人, 而且要簡化到單一問題的回答, 不是一連串的對話. 要由機器來判定對方是不是真人, 真的不是簡單的課題.... 我只能實際一點, 做到夠用就好.. 

效果如何? 大家捲到[底下試看看](#comments)就知道了, 網頁 refresh 一下就可以隨機換一題..., 靜態題目我目前都放腦筋急轉彎類的, 當然我都有附解答, 免的大家答不出來, 掛在那邊不能留言... Echo 型態則只是要大家無腦一點, 跟著打一些口號而以, 像 "叭樂雞萬歲" 之類的 [H] ..... 

果然這樣看起來爽多了, 也比較有趣一點, 反正目的達到就好 [:D], 如果大家有啥有趣的腦筋急轉彎也提供一下, 看看這樣 page view 跟 comment 數會不會衝高一點 [H] 
