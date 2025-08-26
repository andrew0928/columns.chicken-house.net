![Ubuntu Server Setup](/images/2015-10-24-finally-got-ubuntu-server-15-10-working/img_5635a1568329d.jpeg)

原本只是想在 NAS 上簡單玩玩 Docker, 為了接下來的 ASP.NET 5 做準備.. 不過實在太好用，還沒開始做正事 (ASP.NET 5), 就先把原本的 BLOG 從 GoDaddy 的 hosting 搬回來放 NAS 了，順手也架了 reverse proxy ... 現在 NAS Docker 有正式用途了, 而 NAS 的運算能力又很有限 (我的是 DS-412+, CPU 只是 atom d2700, 雙核而已, 1GB RAM), 裝沒幾個就跑開始擔心了，於是就開始想另外搞一個可以隨便玩得 docker engine 環境..

其實 PC 上弄個 VM 是很容易啦，windows 10 內建的 hyper-v 根本就不用花甚麼功夫, 不過我想弄個像 NAS 這樣省電不大需要去管它, 24hr 開著隨時都可以用.. 就把腦筋動到古董要丟掉的筆電.. 我老姊正好有台筆電要丟掉，找我幫他先把硬碟資料清掉她才敢丟...一切都來的太巧了! 於是這台就被我拿來大整修一番...

**這台的規格是 Acer Aspire 5742Z:**

- 15.6" LCD (已經裂開沒辦法顯示了)
- 320GB HDD
- 4G RAM
- Intel Pentium P6200

看來正和我需要 :D，螢幕我也不需要，直接拆掉可以放桌上當鍵盤，還不用擔心螢幕翻起來遮到我真正的螢幕... 用舊 NB 當 SERVER 好處還蠻多的，一來省電，二來快報廢的電池其實當成內建的 UPS 也不錯，夠撐幾分鐘關機就好了。

不過開始安裝 Ubuntu, 就是噩夢的開始... 平常我連使用 windows 都常常開 dos command prompt 下指令，命令列對我來說不是甚麼問題，不過 linux 從研究所畢業之後就很少在碰了，這次光安裝就踢到鐵板..

從一開始，抓錯 USB 開機工具，做出來的開機 USB 好像只支援 net install, 硬要我設定網路才能繼續... 無奈網路卡又抓不到, 查了一堆說明又說這步驟可以跳過, 後來才發現另一套 USB 開機工具就沒這問題..

再來，不知碰到啥問題，我抓了 12.04 LTS, 14.04 LTS, CentOS 都試過了，裝到一半跟我講 CDROM 內容不對，不過我重下載了幾次，也比對過 MD5 hash 都無誤.. 想說換 desktop 板好了，desktop 版應該會比較親民吧? 結果開到桌面就又不動了 @@

最後把 wireless lan 卡直接拔掉，換 15.10 版，終於裝起來 =_=

果然隔行如隔山，裝好後光是要設定 SSH server, 要改固定 IP, 設定 samba 開網路分享... 都花了一些時間, 這部分就還好, 只是花點時間查指令，照著打進去就搞定...

現在終於把基本環境搞定了，特此留念 :D
過程解決的問題對於熟 linux 的人來說應該都是小兒科吧? 我就不貼了，自己記載我私人的 onenote 就好.. 貼幾張照片作紀念:

![雙螢幕安裝畫面](/images/2015-10-24-finally-got-ubuntu-server-15-10-working/IMG_8271-Canon-PowerShot-S110-Medium-e1445685690586.jpg)

我用雙螢幕，旁邊的螢幕是轉成直的，方便看文件。因為有現成的 D-SUB，想說裝一裝就可以改用 SSH ，就懶得把他轉正了，結果搞了半天 =_=

[![筆電螢幕已拆除](/images/2015-10-24-finally-got-ubuntu-server-15-10-working/IMG_8272-Canon-PowerShot-S110-Medium.jpg)](/images/2015-10-24-finally-got-ubuntu-server-15-10-working/IMG_8272-Canon-PowerShot-S110-Medium.jpg)

這張照片可以看到，螢幕已經被我用暴力拆掉了 XD。
這次用 Microsoft 的隨身碟來裝 Linux ... 裝起來的 Linux 又要跑 Microsoft 的 ASP.NET 5 ... 你搞得我好亂啊..

至於 ASP.NET 5 ... 哈哈，再過幾個禮拜再說 XD