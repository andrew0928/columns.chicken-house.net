原本只是想找找有沒有 BlogEngine.NET Extension 存放自訂設定值的說明，無意間找到這個令人 Orz 的東西，BlogEngine.NET 專用的 Widgets ...

Widgets 這名字到處都有人用，指的不外乎是能留在桌面或是網頁的 "小工具"。拜物件技術所賜，這種東西越來越好作了。當年還在用 ET 的時代，一篇報告要插張圖，就有一堆技巧得拿出來用... 先下好控制碼把位子空出來，列印... 然後再印張圖，貼上去..

中間年代有些工具可以直接插圖的就不管了，真正有革命性的改變，是 WIN3.1 時代的 OLE (Object Linkage and Embedded) ，其實這也不是 Microsoft 先發展出來的，較早是 APPLE 的 OpenDoc ... 這些物件的技術開始可以讓兩種獨立的 AP，在同一份文件或是畫面上共同處理一樣的資料...。

幹嘛扯這些? 因為我碩士論文就是弄這些五四三的物件導向技術，哈哈...。沒什麼，只是看到 BlogEngine Widget 這麼好寫，沒幾行 CODE 就搞定，那當年我的研究論文跟本是寫好玩的.. @_@

 

[http://rtur.net/blog/post/2008/03/24/BlogEngine-Widgets-Tutorial.aspx](http://rtur.net/blog/post/2008/03/24/BlogEngine-Widgets-Tutorial.aspx)

原本要找 Extension, 後來逛到這位強者的網站，它擺了一段很簡單的 CODE，就是之前研究過一陣子的 FlickrNet。它寫了一個簡單的 USER CONTROL，透過 FlickrNet 抓幾張圖回來，顯示在 User Control 的範圍內。

另外他寫了另一個 User Control，用來編輯第一個 User Control 可能會用到的設定值，畫面上幾個 Text Box 也搞定了。

然後，放到 BlogEngine.NET 的 ~/Widgets/ 目錄下就好了? 簡單到想打人...

 

現在回頭來看看，這樣做出來的 widget 能幹嘛? 我現在用的版面，右側有一堆 "BOX"，有 Google 的廣告，有 "安德魯是誰?"，有最新回應...，沒錯，在 BlogEngine 1.4 之後，這些就變成真正的元件了。大概就像 Microsoft 的 Web Parts 一樣。網頁的主人可以很簡單的在畫面上拉一塊新的 "widget" 出來，直接用拖拉的方式放到喜歡的位子，按下 [EDIT]，畫面就會切到編輯用的 User Control，OK就存檔...

要做到這堆事，你只要會寫 USER CONTROL，照 BE 的規舉，繼承指定的 CLASS，把檔案放到指定的目錄就好了... Orz

 

有時後東西弄的太簡單也很令人洩氣，尤其是 BLOG 剛搬完家，差不多要完工時 @_@，才發現 BlogEngine 在 2008/06/30 推出 1.4 版，主要就是加上 widget 的功能... 哈哈，那個[小熊子](http://www.michadel.net/)應該比我更想哭吧 (H)

 

不過事情倒還很順利，之前有作好準備，花了一兩個小時試一下就動工了，動啥工? 看看底下的版本... 已經搬到 1.4 版了 :D，唯一美中不足的是，過去花太多工夫在這個樣板上面，所以只好連樣板一起搬過來... 而這個樣版並不支援 Widget 的功能。看來又有得忙了...