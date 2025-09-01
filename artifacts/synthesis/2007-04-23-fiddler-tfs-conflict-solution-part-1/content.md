I.aspx/
  - /post/2007/04/23/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---I.aspx/
  - /post/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---I.aspx/
  - /columns/2007/04/23/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---I.aspx/
  - /columns/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---I.aspx/
  - /blogs/chicken/archive/2007/04/23/2350.aspx/
wordpress_postid: 166
---

[Fiddler](http://www.fiddler2.com/), 應該不用我多介紹了, 一套很好用的 Http Debugging Tool. 它的原理是把自己當成 Proxy, 讓所有的 Http 流量都經過它再轉出去, 讓你能看到你的程式到底跟網站講了那些話, 尤其是新興的 AJAX 更需要這種 Tools, 因為一堆東西是你按右鍵 + view source 所看不到的...

不過以上不是重點, 重點是我常常搭配 visual studio 2005 一起使用, 每當 Fiddler 開啟, 我再使用 vs2005 的 TFS 相關功能時, vs2005 跟 TFS 中間的 http connection 就被欄下來不動了.

![TFS connection blocked](/images/2007-04-23-fiddler-tfs-conflict-solution-part-1/image07.png)

Fiddler Log:

![Fiddler HTTP 401 error](/images/2007-04-23-fiddler-tfs-conflict-solution-part-1/image012.png)

HTTP 401, 看起來就像是 vs2005 傳出去的身份驗證機制沒有成功的通過 Fiddler 傳到 server, 導至 server 回應 401 回報沒有權限... vs2005 回的 ERROR MESSAGE 則是看起來跟這件事一點關聯都沒有...

正規的解法應該是想辦法讓 vs2005 的驗證能過 Fiddler Proxy ... 不過太懶了, 我發現只要開 Fiddler 等它自動改完 IE Proxy Settings 後再把 TFS 網址加到 bypass host list 後就一切正常了, 所以腦筋就動到怎麼讓 Fidder 自動調整的 Proxy Settings 能自動把 TFS 網址加到忽略清單內. 我打算的流程是這樣:

1. Fiddler 存下目前的 Proxy Config 
2. Fiddler 把 WinINET 的 Proxy 改為 127.0.0.1:8888 
3. 在 OnAttach 裡加上自定的 Script, 就抄 (2) 的 CODE 改一改再把我要的值加上去

想的很好, 就開始動工了, 不過開始動工才發現, 原來一路上困難重重... -_-

<< 下期待續 >>