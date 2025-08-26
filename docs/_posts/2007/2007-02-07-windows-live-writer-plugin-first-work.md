---
layout: post
title: "Windows Live Writer - Plugin 處女作..."
categories:
tags: [".NET","作品集","技術隨筆"]
published: true
comments: true
redirect_from:
  - "/2007/02/07/windows-live-writer-plugin-處女作/"
  - /columns/post/2007/02/07/Windows-Live-Writer-Plugin-e89995e5a5b3e4bd9c.aspx/
  - /post/2007/02/07/Windows-Live-Writer-Plugin-e89995e5a5b3e4bd9c.aspx/
  - /post/Windows-Live-Writer-Plugin-e89995e5a5b3e4bd9c.aspx/
  - /columns/2007/02/07/Windows-Live-Writer-Plugin-e89995e5a5b3e4bd9c.aspx/
  - /columns/Windows-Live-Writer-Plugin-e89995e5a5b3e4bd9c.aspx/
  - /columns/post/2007/02/07/Windows-Live-Writer---Plugin-e89995e5a5b3e4bd9c.aspx/
  - /post/2007/02/07/Windows-Live-Writer---Plugin-e89995e5a5b3e4bd9c.aspx/
  - /post/Windows-Live-Writer---Plugin-e89995e5a5b3e4bd9c.aspx/
  - /columns/2007/02/07/Windows-Live-Writer---Plugin-e89995e5a5b3e4bd9c.aspx/
  - /columns/Windows-Live-Writer---Plugin-e89995e5a5b3e4bd9c.aspx/
  - /blogs/chicken/archive/2007/02/07/2125.aspx/
wordpress_postid: 189
---

Windows Live Writer (以下簡稱 WLW) 用過的都說好, 老實說它做的真是不錯, 連家裡太座用了之後就再也不到網頁上寫 blog 了... 

不過有個缺點實在是很礙眼, 就是透過它上傳的圖檔, 不管 options 怎麼調, 透過 MetaBlogAPI 或是 FTP, 都會被重新存一次 JPEG 檔. 一來 JPEG 是破壞性壓縮, 越存會越糟糕, 二來它用的 quality 還不低, 我自己的圖檔丟上去大概都會肥一倍... 畫質變差, 檔案又有可能變肥, 真是人財兩失.. 到底差多少? 各位自己比較一下就知道了, 在圖檔上按右鍵選內容可以看的到 file size.. 底下左邊的圖是原檔, 右邊是 WLW 幫你加工過的, 不過我原圖是 JPEG 100% quality, 所以 WLW 雞婆完反而變小一點... 

![](/images/2007-02-07-windows-live-writer-plugin-first-work/10502.jpg)![](/images/2007-02-07-windows-live-writer-plugin-first-work/CRW_0465(Canon%20PowerShot%20G2)%5B4%5D.jpg)%5B4%5D.jpg)

試了半天沒得解, 每次都用 "Insert Picture From Web" 也不是辦法, 就把腦筋動到 Plugin 上了... 跟小熊子聊完後就開始手癢了, 去下載 WLW SDK 回來看... 可以用 .NET 寫, 就邊 K 邊寫起來... 做法跟 Insert Picture From Web 差不多, 只是先設定好 UNC 路逕跟網址的對應, 讓你挑完檔案先幫你 copy 好再塞入網址.. 懶人用. 

首先是 option settings, dll 丟到 Plugins 目錄後, 打開 WLW 的 Tools -> Preferences, Plugins 就會看到新加進去的外掛了.. 

![](/images/2007-02-07-windows-live-writer-plugin-first-work/23218.gif)

我有準備編輯設定的畫面... 因此有 [options] 的按鈕可以用.. 

![](/images/2007-02-07-windows-live-writer-plugin-first-work/35291.gif)

這個畫面就很簡單的只填 UNC (網路分享的路逕), 跟對應的 URL ... 設定完成後, 只要要插入圖檔時, 從選單選 Insert -> 插入圖片(從網路芳鄰), 就會跳出標準的 Open File DialogBox, 挑完就一切大功告成了 :D 

![](/images/2007-02-07-windows-live-writer-plugin-first-work/17535.gif)

本來是想從 MetaBlog API 下手, 因為這個管道也可以 upload image, 不過試了半天宣告放棄, 大概是 Microsoft 怕有人寫 Plugins 來偷密碼吧? 也可能是 Plugins 都被定位在 "edit blog" 的部份, 而不是 "publish" 的部份, 因此完全拿不到 WLW 的 Weblog Account 相關資訊... 這條路宣告放棄, 就算要作, 也得分開 config, 沒辦法... 

現在這個版本其實只是自己做爽的而以, 所以就不用跟我要 .dll 了, 不成氣候的作品... 因為不知 Microsoft 下一版會不會改掉這鳥問題? 有的話這外掛就變廢物了, 二來現在太陽春, 連個防呆都沒有... 哈哈... 只是花兩個小時邊 K 邊寫的本來就只能玩玩... 不過做過這個 plugin 後, 寫法跟能運用的範圍大概都有個底了, 下次來改寫的話, 我打算 option 那邊就改成 MetaBlogAPI 需要的設定, 如 Blog URL, account, password 等資訊, 不然放個網芳真的是沒啥用...
