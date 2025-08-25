---
layout: post
title: "Tips: 遠端桌面連線的小技巧"
categories:

tags: ["Tips","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2008/03/05/tips-遠端桌面連線的小技巧/
  - /columns/post/2008/03/06/Tips-e981a0e7abafe6a18ce99da2e980a3e7b79ae79a84e5b08fe68a80e5b7a7.aspx/
  - /post/2008/03/06/Tips-e981a0e7abafe6a18ce99da2e980a3e7b79ae79a84e5b08fe68a80e5b7a7.aspx/
  - /post/Tips-e981a0e7abafe6a18ce99da2e980a3e7b79ae79a84e5b08fe68a80e5b7a7.aspx/
  - /columns/2008/03/06/Tips-e981a0e7abafe6a18ce99da2e980a3e7b79ae79a84e5b08fe68a80e5b7a7.aspx/
  - /columns/Tips-e981a0e7abafe6a18ce99da2e980a3e7b79ae79a84e5b08fe68a80e5b7a7.aspx/
  - /blogs/chicken/archive/2008/03/06/3035.aspx/
wordpress_postid: 116
---

查了文件, 才發現可以這樣用... 平常連到 server 用的遠端桌面連現, 常碰到幾個問題: 

1. 每次都要打 IP, 能不能拉捷逕出來, 我常連的那台只要點兩下就自動登入? 
2. 只有那幾種解析度可以選, 沒有我要的... 
3. 遠端桌面連進去的畫面, 跟本機的不一樣. 看不到某些在本機才看的到的訊息... 

原來這些都有解啊... (1) 最簡單, 把設定存檔就好, 就附圖的資訊, 底下有 [Save As], 以後直接點兩下存好的檔案就好了. 

![image](/images/2008-03-06-tips-remote-desktop-connection-tricks/image_3.png)

再來, (2) 跟 (3) 其實也有解, 只要先打開 DOS Prompt, 輸入 MSTSC /? 就會出現這個說明畫面: 

![image](/images/2008-03-06-tips-remote-desktop-connection-tricks/image_6.png)

答案就在影片中... 加上 /w:1440 /h:900 參數, 就可以用寬螢幕的解析度 1440 x 900 來搖控遠端的 server 了. 想要看 console (本機) 的畫面嘛? 比如有時 service 的 error message 只會秀在 console.. 這時只要加上 /console 參數就好. 整段指令如下: 

[![image](/images/2008-03-06-tips-remote-desktop-connection-tricks/image_thumb_2.png)](/wp-content/be-files/WindowsLiveWriter/Tips_1082C/image_8.png)

開出來的視窗: 

![image](/images/2008-03-06-tips-remote-desktop-connection-tricks/image_11.png)

嗯, 看寬螢幕的果然比較爽, 當然這樣也就有機會用雙螢幕了. 小技巧, 需要的人可以參考看看!
