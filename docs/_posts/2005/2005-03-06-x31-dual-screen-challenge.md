---
layout: post
title: "X31 + 雙螢幕的挑戰 @_@"
categories:

tags: ["技術隨筆","敗家","有的沒的","水電工"]
published: true
comments: true
redirect_from:
  - /2005/03/06/x31-雙螢幕的挑戰-_/
  - /columns/post/2005/03/06/X31-2b-e99b99e89ea2e5b995e79a84e68c91e688b0-_.aspx/
  - /post/2005/03/06/X31-2b-e99b99e89ea2e5b995e79a84e68c91e688b0-_.aspx/
  - /post/X31-2b-e99b99e89ea2e5b995e79a84e68c91e688b0-_.aspx/
  - /columns/2005/03/06/X31-2b-e99b99e89ea2e5b995e79a84e68c91e688b0-_.aspx/
  - /columns/X31-2b-e99b99e89ea2e5b995e79a84e68c91e688b0-_.aspx/
  - /blogs/chicken/archive/2005/03/06/336.aspx/
wordpress_postid: 273
---

![Dual Screen Setup](/images/2005-03-06-x31-dual-screen-challenge/dualview.jpg)

買了 ThinkPad X31 後, 我在公司就一直很奢侈的用兩個螢幕來工作 (真過癮啊), 本來家裡也有古董 19"CRT 可以這樣用的, 但是 CRT 終究逃不過老化的命運, 就這樣掛掉了 :~ 所以才動了買台 17"LCD 的念頭..

其實我的要求很簡單, 反正接 notebook 用的, 不玩 game, 反應時間? 隨便啦.. 解析度? 也隨便啦, 1280x1024 就夠了. DVI ? 暫時也沒機會用... 比較重要的反倒是能不能轉 90 度, 上下的視角 (轉成直的用, 上下視角就很重要) 還有外觀 and 價格之類的...

我的 X31 有搭配 Dock 一起用, 上面有 DVI 的接頭, 無奈 X31 本身不支援 DVI output, 這個接頭也只能當成裝飾品... 看來暫時無緣用 DVI 了. 所以解析度... 別想太多, 1280x1024 大概是極限了...

<!--more-->

最後挑出來的機種是 Sxxxxxx 720T, 除了滿足上面要求之外, 就是它附了 Pivot Pro 這套軟體... 是一套跟你用啥顯示卡無關, 可以把你畫面轉成 90 度的工具, 為何買 monitor 還要看軟體? 看下去就知道... 有附這套軟體是讓我挑這營幕主要原因之一...

之前為了這個功能吃盡了苦頭, 首先 IBM?內建的 vga driver 並沒有把輸出畫面轉 90 度的功能, 好不容易查到這個 hack:

> 修改機碼: [HKEY_LOCAL_MACHINE\SOFTWARE\ATI Technologies\Desktop\{xxx-xxx-xxx-xxx-xxx}]  
> {}只有一個所以不用擔心找錯，  
> 修改其中的 Rotation  
> 將原本 00 00 00 00  
> 修改成 01 00 00 00

![ATI Rotation Registry](/images/2005-03-06-x31-dual-screen-challenge/ati-rotation.jpg) ![ATI Menu](/images/2005-03-06-x31-dual-screen-challenge/ati-menu.jpg)

真是神奇, 顯示卡的設定裡就多了 "旋轉"的功能了, ATI 的 TaskIcon 也多了快速選單可以轉... ![](/images/2005-03-06-x31-dual-screen-challenge/teeth_smile.gif)

事情還沒結束, 外接 monitor 調成 1280x1024 才發現, ATI driver 在這個模式下 ( 1024x768x32bits + 1280x1024x16bits ) 不支援旋轉的功能.. ![](/images/2005-03-06-x31-dual-screen-challenge/angry_smile.gif)

![Pivot Pro](/images/2005-03-06-x31-dual-screen-challenge/pivot.jpg)

到最後還是得靠 Pivot Pro 來解決... 至於解析度為何要 1280x1024x**16bits** ? 沒想到 32MB Video RAM 竟然撐不住 1024x768x32bits + 1280x1024x32bits ... 只能把其中一個降到 Hicolor ... ![](/images/2005-03-06-x31-dual-screen-challenge/cry_smile.gif) 這個就沒解了, 只能以後有機會換機器的話再說...

為了讓 X31 搭配直立式 17"LCD 雙螢幕工作, 沒想到困難這麼多... 幸好現在可以順利使用了, 總算沒有白買 monitor ![](/images/2005-03-06-x31-dual-screen-challenge/shades_smile.gif)
