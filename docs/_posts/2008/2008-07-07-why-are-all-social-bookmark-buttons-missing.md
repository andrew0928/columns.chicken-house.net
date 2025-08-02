---
layout: post
title: "為什麼一堆推文的按鈕都不見了?"
categories:

tags: [".NET","BlogEngine.NET"]
published: true
comments: true
redirect_from:
  - /2008/07/07/為什麼一堆推文的按鈕都不見了/
  - /columns/post/2008/07/07/e782bae4bb80e9babce4b880e5a086e68ea8e69687e79a84e68c89e98895e983bde4b88de8a68be4ba86.aspx/
  - /post/2008/07/07/e782bae4bb80e9babce4b880e5a086e68ea8e69687e79a84e68c89e98895e983bde4b88de8a68be4ba86.aspx/
  - /post/e782bae4bb80e9babce4b880e5a086e68ea8e69687e79a84e68c89e98895e983bde4b88de8a68be4ba86.aspx/
  - /columns/2008/07/07/e782bae4bb80e9babce4b880e5a086e68ea8e69687e79a84e68c89e98895e983bde4b88de8a68be4ba86.aspx/
  - /columns/e782bae4bb80e9babce4b880e5a086e68ea8e69687e79a84e68c89e98895e983bde4b88de8a68be4ba86.aspx/
wordpress_postid: 87
---

![image](/wp-content/be-files/WindowsLiveWriter/8dc7a0549a69_196F/image_12.png)

前兩天突然發現，怎麼一堆文章原本有推文數字的，怎麼都不見了?

![image](/wp-content/be-files/WindowsLiveWriter/8dc7a0549a69_196F/image_14.png)

網站有問題怎麼可以不追查個水落石出? 連到推推王找一下當時的推文... 耶? 還在啊，旁邊還有推文記錄...。

![image](/wp-content/be-files/WindowsLiveWriter/8dc7a0549a69_196F/image_13.png)

怪的是從推推王點回來看我的文章，Oops!

越看越不對，把網址印出來比對一下才發現，我這邊的網址已經不一樣了!!

[http://columns.chicken-house.net/post/FlickrProxy-1---Overview.aspx](http://columns.chicken-house.net/post/FlickrProxy-1---Overview.aspx) (推推王那邊的網址)

[http://columns.chicken-house.net/post/FlickrProxy-1-Overview.aspx](http://columns.chicken-house.net/post/FlickrProxy-1-Overview.aspx) (我這邊實際的網址)

真妖獸，馬上聯想到前幾天升級 BE1.4 可能會有影響，就搬出 VSS 來比對一下，果然 1.3 跟 1.4 在自動產生 SLUG (SLUG 就是指 POST 網址後面那一串) 的規責有調整過:

![image](/wp-content/be-files/WindowsLiveWriter/8dc7a0549a69_196F/image_3.png)

嗯，肉眼看的出的調整，包括逗號被移掉，連續多個 -- 也會被替換成 - ，這個案例就是原網址的 "---" 換成 "-" 後就連不到了 :@

本來想寫個程式修一下，後來想想跟本沒幾篇，就直接到推推王改掉了事，哈哈... 結案!
