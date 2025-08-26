---
layout: post
title: "HVRemote (Hyper-V Remote Management Configuration Utility)"
categories:

tags: ["MSDN","Tips","有的沒的"]
published: true
comments: true
permalink: "/2009/08/16/hvremote-hyper-v-remote-management-configuration-utility/"
redirect_from:
  - /columns/post/2009/08/16/HVRemote-(Hyper-V-Remote-Management-Configuration-Utility).aspx/
  - /post/2009/08/16/HVRemote-(Hyper-V-Remote-Management-Configuration-Utility).aspx/
  - /post/HVRemote-(Hyper-V-Remote-Management-Configuration-Utility).aspx/
  - /columns/2009/08/16/HVRemote-(Hyper-V-Remote-Management-Configuration-Utility).aspx/
  - /columns/HVRemote-(Hyper-V-Remote-Management-Configuration-Utility).aspx/
wordpress_postid: 35
---

被這東西搞了半天，過了幾個月後發現有善心人事寫了個工具，今天看到了特地來記一篇... 免的以後又忘了 @@

話說 Microsoft 從幾年前開始被一堆 security 的問題苦惱後，決定所有產品都把安全視為第一優先... 這是件好事啦，不過為了 security 問題，真的會把 MIS 及 DEV 的相關工作難度加上好幾倍... 今天這個就是一例: 在沒有 AD 環境下，如何遠端的管理 Hyper-V server ?

之前把家裡的 SERVER 升級到 Windows Server 2008 + Hyper-V, PC 升級為 Vista 後，當然很高興的抓了 Hyper-V 的遠端管理工具回來裝。想說大概跟以往的 MMC 一樣，輸入 SERVER 的資訊，帳號密碼打一打，就可以用了...

事情當然沒這麼簡單，不然就沒這篇了... 直接使用的結果當然只是丟個沒權限之類的訊息。GOOGLE 找了一下解決方式... 找到這文章 (有五篇，別以為很辛苦的把它照作就結束了，還有 part 2 ~ part 5 @@):

http://blogs.technet.com/jhoward/archive/2008/03/28/part-1-hyper-v-remote-management-you-do-not-have-the-requested-permission-to-complete-this-task-contact-the-administrator-of-the-authorization-policy-for-the-computer-computername.aspx

細節就不講了，要調整的步驟還真它X的多... 先在 CLIENT / SERVER 都建好帳號，防火牆要允許 WMI，DCOM... 再設定 WMI 相關的權限給指定的帳號，還有後續一堆安全相關的設定要開... 最後搞了半天，真的成功了，不過... 最近趕流行，把 Vista 換成 Windows 7... 真糟糕，這堆步驟又要來一次 @@

這次又找了一下解決方式，還是一樣有這堆設定要改，不過跟幾個月前找到的同一個 BLOG，版主真是個好人，他把他整理出來的步驟寫成了個工具: HVRemote.wsf … 沒錯，就只是個 script 而已，不過它可不簡單。先看一下它的網站:

http://blogs.technet.com/jhoward/archive/2008/11/14/configure-hyper-v-remote-management-in-seconds.aspx

http://code.msdn.microsoft.com/HVRemote

http://technet.microsoft.com/en-us/library/ee256062(WS.10).aspx

作者把上面那一大串的步驟都寫成 script 了，你只要把這 script 抓下來，放到 client / server 都執行一次，就搞定了 :D 真專業，還有一份很完整的操作說明 PDF 檔... 一定要推一下這個工具 (Y)

附帶提一下，Hyper-V 遠端管理工具是透過 MMC 來執行的，但是我喜歡像 Remote Desktop 那種簡單的作法，只要開個連線工具，驗證過之後就可以遠端桌面這樣... Hyper-V 也有提供這樣的工具。只要裝好管理工具，你的電腦就會有這檔案:

C:\Program Files\Hyper-V\vmconnect.exe

![image](/images/2009-08-16-hvremote-hyper-v-remote-management-configuration-utility/image.png)

搞什麼，連登入視窗都弄的跟 Remote Desktop Client 一模一樣，有時不小心還真會弄錯 =_=

開起來後就是大家熟悉的 Hyper-V 遠端管理的畫面了。這工具只是讓你省掉從 MMC 去 connect VM 這些步驟而以，像 RDP 一樣開了就能用:

![image](/images/2009-08-16-hvremote-hyper-v-remote-management-configuration-utility/image.png)

當然透過這工具，上面那堆設定步驟也要照做才會通啦，只是順帶提一下這個 tips 而已。有了 HVRemote 這工具，要設定遠端管理 Hyper-V VM 就更輕鬆了，有需要的人就參考看看吧!
