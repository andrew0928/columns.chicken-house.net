---
layout: post
title: "偷偷升級到 CS2007 .."
categories:

tags: [".NET","Community Server","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2007/05/05/偷偷升級到-cs2007/
  - /columns/post/2007/05/05/e581b7e581b7e58d87e7b49ae588b0-CS2007-.aspx/
  - /post/2007/05/05/e581b7e581b7e58d87e7b49ae588b0-CS2007-.aspx/
  - /post/e581b7e581b7e58d87e7b49ae588b0-CS2007-.aspx/
  - /columns/2007/05/05/e581b7e581b7e58d87e7b49ae588b0-CS2007-.aspx/
  - /columns/e581b7e581b7e58d87e7b49ae588b0-CS2007-.aspx/
  - /blogs/chicken/archive/2007/05/05/2378.aspx/
wordpress_postid: 164
---

好像沒啥人發現的樣子, 哈哈, 本站兩個禮拜前升級到 CS2007 了, 升級完面版馬上就調成舊的, 外觀看起來一模一樣...

功能當然有差, 不過我就不提了, 請直接到官方網站看就好. 升級很簡單, DB upgrade + File upgrade 就好了. 比較麻煩的是我自己客製過的 theme 跟 control ..

CS2007 的樣版系統, 從當年的 1.0 到 2.x 都一樣, 用了一堆動態載入 UserControl 的方式, 把版面配置的部份留在 User Control 的 TAG, 而後端的 data / logic 則是寫在 code. 因此要改它的樣版, 得花一番功夫瞭解它的作法.. 到了 CS2007, 總算改用 ASP.NET 2.0 標準作法了, 每套樣版就是一個 master page + config 而以 (theme.master, theme.config), 以 BLOG 來說, 每個頁面就很單純是一個 .aspx, 改起來方便多了, 不需要花什麼大腦就找的到要改那裡...

另一個 User Control, 舊的 API 有些都不能用了, 趁著這次改版我就直接把這幾個 User Control 改寫一次了. 以前都要寫 DLL 也是很麻煩, 這次一起改成 .ascx + .cs 就丟著了, deployment 方便嘛...

至於 CS2007 的新功能, 還沒很仔細的研究, 至少現在平台 ready 了 :D
