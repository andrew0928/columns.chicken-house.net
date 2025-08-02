---
layout: post
title: "Hash 的妙用"
categories:

tags: ["技術隨筆"]
published: true
comments: true
redirect_from:
  - /2005/06/08/hash-的妙用/
  - /columns/post/2005/06/08/Hash-e79a84e5a699e794a8.aspx/
  - /post/2005/06/08/Hash-e79a84e5a699e794a8.aspx/
  - /post/Hash-e79a84e5a699e794a8.aspx/
  - /columns/2005/06/08/Hash-e79a84e5a699e794a8.aspx/
  - /columns/Hash-e79a84e5a699e794a8.aspx/
  - /blogs/chicken/archive/2005/06/08/643.aspx/
wordpress_postid: 255
---

最近替公司的系統開發了一些工具, 深深覺的有個良好的 Hash 演算法, 用處實在太多了 ![emotion-21](/Emoticons/emotion-21.gif)  
唯一的限制, 真的就只在於你的想像力而以...

Hash algorithm (中譯: 雜湊演算法), 其實沒有什麼, 不過就是一個數學函數, Hash(X) = ......... 這樣而以. 不同的資料代進去計算, 可以得到不一樣的值. 這些值越亂越好, 越沒有規則越好, 輸出的值越難預測越好, 而且不能從輸出的值反推回原本輸入的資料.

<!--more-->

看來很複雜, 其實很簡單, 身份證字號最後一碼, 就是跟據前面的字母加上八個數字依某個原則算出來的, 勉強也可以當成一個簡單的 Hash function. 它能幹嘛? 透過最後一碼當檢查碼, 可以確認這個身份證字號是不是亂寫的.

當然實際上應用的 hash algorithm 不像身份證號碼這麼簡單. 常用的就如 MD5 (Message Digest 5), SHA (Secure Hash Algorithm), SHA256, SHA512 ... etc. 這些演算法的輸入, 可以是一連串的 binary data, 像是一整個檔案. 而輸出的則是故定長度的 bytes, 能用的地方很多, 比如:

1. 儲存密碼的 Hash, 代替儲存明文的密碼
2. 檔案的 Hash 能夠快速的比對兩份檔案是否相同, 或是從一堆檔案中, 快速找出內容相同的檔案
3. 數位簽章, 確保資料沒有被修改過
4. 保護曝露在外的資訊不被竄改, 像 cookie 或是 URL 附加的 query string

這些都是我實際上在公司開發的系統上應用的地方, 不過, 打到這裡, 發現想講的才講了 1/10 不到, 但是已經覺的手痠了, 哈哈... 就當在閒聊吧, 下回再說 ![emotion-15](/Emoticons/emotion-15.gif)
