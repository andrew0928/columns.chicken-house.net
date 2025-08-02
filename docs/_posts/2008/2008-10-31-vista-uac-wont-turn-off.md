---
layout: post
title: "關不掉的 Vista UAC !?"
categories:

tags: ["Tips"]
published: true
comments: true
redirect_from:
  - /2008/10/31/關不掉的-vista-uac/
  - /columns/post/2008/10/31/e9979ce4b88de68e89e79a84-Vista-UAC-!.aspx/
  - /post/2008/10/31/e9979ce4b88de68e89e79a84-Vista-UAC-!.aspx/
  - /post/e9979ce4b88de68e89e79a84-Vista-UAC-!.aspx/
  - /columns/2008/10/31/e9979ce4b88de68e89e79a84-Vista-UAC-!.aspx/
  - /columns/e9979ce4b88de68e89e79a84-Vista-UAC-!.aspx/
wordpress_postid: 55
---
不知道是更新了啥 PATCH，還是那次沒正常關機，我公司 VISTA 的 UAC 突然莫名奇妙的被打開了。怪的是控制台裡看到的還是關掉的，不管怎麼改狀態也不會改變 (一直都是關的) ...。

直覺告訴我一定是控制台的 AP 那邊出問題，設定值寫不進去造成的...，於是我就開使找其它可以修改 UAC 設定的方法...，最後找到這個，還真的成功了 :D，看來沒機會動用 ProcessMonitor 追追看問題了..

找到的方法是: msconfig.exe

在開始 --> 執行裡輸入 msconfig.exe 後，可以看到這一項:

![image](/wp-content/be-files/WindowsLiveWriter/VistaUAC_1E70/image_3.png)

看來是直接修改 registry, 果然有效，直接執行後 REBOOT 就一切正常了 -_-, 如果有人也碰過一樣的問題可以試看看!
