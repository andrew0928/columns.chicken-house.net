---
layout: post
title: "Bot Checker 回來了!"
categories:

tags: [".NET","ASP.NET","BlogEngine.NET","作品集","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/06/25/bot-checker-回來了/
  - /columns/post/2008/06/25/BotChecker.aspx/
  - /post/2008/06/25/BotChecker.aspx/
  - /post/BotChecker.aspx/
  - /columns/2008/06/25/BotChecker.aspx/
  - /columns/BotChecker.aspx/
wordpress_postid: 92
---
哈哈，終於加回來了 :D

為什麼原本在 CS 上很簡單就加上去的 Bot Checker, 在 BE 上弄到現在才好? 原因只有一個，就是 BE 在張貼回應時用了不少 AJAX 的機制，變的要插一段 CODE 進去要追半天 @_@...

很諷刺的是，AJAX 其實是 Community Server 用的比較兇，到處都要來一下... 反而 BlogEngine.NET 就中規中舉多了，很多地方就都乖乖的用 PostBack.. 唯讀回應的地方很突兀，感覺好像是特別要現一下回應的那個 TEXT EDITOR 還有 BBCODE 預覽的樣子... 那邊的 CODE 弄的實在是有點亂...

也是之前幾次都沒認真追啦... 追到一半覺的煩就去逛網站了，哈哈... 今天狠下心把它解決掉了。只不過卡著 AJAX，又不想跟它奮鬥，所以有些地方就偷懶混過去了。什麼意思? 意思就是攤開 HTML 原始碼，這個 Bot Checker 也是防不了 Bot 啦，不過我就賭我的站還有我的 Bot Checker 沒大到有人願意寫 Bot 來攻擊我.. 哈哈.. 來看看效果:

![image](/images/2008-06-25-bot-checker-is-back/image_3.png)

當然，張貼出去的回應也會帶著 Bot Checker 的問題。只不過礙於 AJAX，一堆東西被迫要移到 CLIENT SIDE 來處理，這邊就偷懶，題目產生完就先填到 [評論] 欄了，各位在填回應時，不爽附上 "芭樂雞萬歲" 的話，還是可以把它刪掉...

![image](/images/2008-06-25-bot-checker-is-back/image_6.png)

--
題外話，在追 BE 的程式碼的過程中，發現 BE 也有 CAPTCHA ? 不過還真的找不到怎麼把它打開... 有興趣用 BlogEngine.NET 又想用正統的 CAPTCHA 驗證的人可以試看看
