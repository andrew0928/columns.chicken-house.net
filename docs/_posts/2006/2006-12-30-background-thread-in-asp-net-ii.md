---
layout: post
title: "Background Thread in ASP.NET (II)"
categories:
- "系列文章: 多執行緒的處理技巧"
tags: [".NET"]
published: true
comments: true
redirect_from:
  - /2006/12/29/background-thread-in-asp-net-ii/
  - /columns/post/2006/12/30/Background-Thread-in-ASPNET-(II).aspx/
  - /post/2006/12/30/Background-Thread-in-ASPNET-(II).aspx/
  - /post/Background-Thread-in-ASPNET-(II).aspx/
  - /columns/2006/12/30/Background-Thread-in-ASPNET-(II).aspx/
  - /columns/Background-Thread-in-ASPNET-(II).aspx/
  - /blogs/chicken/archive/2006/12/30/2028.aspx/
wordpress_postid: 195
---

為了讓 ASP.NET 的 worker thread 能多做點事, 還真是吃盡了苦頭... 最近試到差不多了, 晚上睡覺就放著讓 worker thread 跑看看...

果然, 放著去看個電視回來就不跑了, log 檔剛剛好寫了 20 min 就停了... 看了一下, 原來是 COM+ App Pool 設定在搞鬼, 20 min 內 iis 沒有新的 request 過來, 就自動停掉把 resource 放出來, worker thread 就跟著 application unload 就不見去了

![COM+ App Pool Settings](/images/2006-12-30-background-thread-in-asp-net-ii/2003-AppPool.jpg)

改個設定再跑一次, 不錯, 跑了幾個小時, 不過這次因為別的問題, IIS w3wp.exe 又停了... 至少往前跨一大步... 接下來就是看怎樣做 exception handling 比較妥當的問題了 :D
