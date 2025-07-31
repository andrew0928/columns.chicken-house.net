---
layout: post
title: "IE6 縮放網頁: using css + htc"
categories:

tags: ["HTML/CSS","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2006/11/11/ie6-縮放網頁-using-css-htc/
  - /columns/post/2006/11/12/IE6-e7b8aee694bee7b6b2e9a081-using-css-2b-htc.aspx/
  - /post/2006/11/12/IE6-e7b8aee694bee7b6b2e9a081-using-css-2b-htc.aspx/
  - /post/IE6-e7b8aee694bee7b6b2e9a081-using-css-2b-htc.aspx/
  - /columns/2006/11/12/IE6-e7b8aee694bee7b6b2e9a081-using-css-2b-htc.aspx/
  - /columns/IE6-e7b8aee694bee7b6b2e9a081-using-css-2b-htc.aspx/
  - /blogs/chicken/archive/2006/11/12/1936.aspx/
wordpress_postid: 208
---

之前在小熊子朋友 DarkThread 的網頁看到[一篇](http://feeds.feedburner.com/~r/Darkthread/~3/45804519/kb-ie6.html), 可以不用裝 IE7 / Firefox 等就可以有縮放網頁的功能.. 不過有個限制是要在網頁加上一段 html code, 逛的網頁不是自己能改的就頭痛了...

之前這篇講到用 css 可以把所有的網頁縮放大小, 不過縮放比例是寫死在 css 裡的... 看到 DarkThread 的那篇, 就手癢了起來, 試試用 htc + css 的方式, 看看能不能藉著這個技巧把縮放網頁的功能散佈到所有的網站上...

htc (Html Component) 是從 IE5.0 開始的 "新技術", 基本上它的目的就像 asp.net 的 server control, 你可以透過它創造自己的 html tag, 只不過 htc 是 client side 的技術, 而 server control 是 server side 的技術, 用法很像, 技巧完全不一樣...

htc 在 IE5.0 只是很基本的 support, 它是從 css 裡的 behavior 延伸出來的, 因為它是靠 css 的 behavior 把 html element 跟 htc 綁在一起, 因此可以透過 css 直接把功能散佈到整個網站, 就變成它最擅長的地方了, 下次貼一篇把整個網站的右鍵選單停用的例子, 超簡單...

原理大概是這樣, 因為 IE 提供了 user 自訂 css 的功能, 你可以把你自訂的 css 檔套用在所有你的 ie 開啟的網頁, 加上 htc (html component) 可以藉著 css 套用到網頁上, 這次就來試試這兩者的組合...

1. 在 c:\ 放了三個檔案: zoom.htc / zoom.css / zoom.html (點[這裡下載](http://www.chicken-house.net/files/chicken/zoom.zip))

2. 打開 IE, 工具 -> 網際網路 -> 存取設定 -> 樣式表 -> 指定 c:\zoom.css

3. 開網頁, c:\zoom.html

4. 按住 ALT, 同時點一下滑鼠左鍵, 不錯, 底下跳出 select 來了, 選百分比就可以直接改變網頁放大率...

![IE6 Zoom Interface](http://community.chicken-house.net/blogs/images/49b1d4940d01_14B92/23.jpg)

看起來好像很不錯, html 裡完全跟我自訂的 css / htc 沒關係, 但是效果卻出來了 (y). 不過在早期的 IE 這樣就大功告成了, 現在的 IE 可沒那麼簡單... :'(

接著再打開 google 首頁看看...

![Google Homepage Security Issue](http://community.chicken-house.net/blogs/images/49b1d4940d01_14B92/17.jpg)

Orz, 因為 c:\zoom.htc 跟 http://www.google.com.tw 在兩個不同的 security zone, 而且 domain 也不同, 兩者的 cross talk 被 IE 給檔了下來... ouch... 看來就差這個該死的安全機制... 不然一切就太完美了... 這個限制還沒有找到很簡單的解法, 有點子的人就提供一下吧... :'(
