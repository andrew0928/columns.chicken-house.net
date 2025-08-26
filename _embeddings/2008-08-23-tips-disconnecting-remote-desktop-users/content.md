近日同事連不進 SERVER，因為連線人數已滿，又摸不到本機，正在那邊苦惱...。原來大家都知道怎麼連，但是都不知道怎麼砍人... 。從 windows 2000 開始就有 RDP 可以用了，當時學到的一個指令一直到現在都可以用，就藉這個機會貼一下。

什麼秘技都一樣，說穿了就不值錢。半年前貼了一篇 [[遠端桌面連線的小技巧](/post/Tips-e981a0e7abafe6a18ce99da2e980a3e7b79ae79a84e5b08fe68a80e5b7a7.aspx)]，裡面講到加上 /console 這參數就能連到 console session，不會跟其它人去搶那兩個連線，就可以把不順眼的 USER 砍了。連進去後要砍人很簡單，工作管理員叫出來，最後一頁 [USER] 就會列出有多少人掛在上面...

![Remote Desktop Task Manager](/images/2008-08-23-tips-disconnecting-remote-desktop-users/image_5.png)

通常這樣就能解決 90% 的問題了。如果連這個秘密連線都被用掉了，那只剩另一招: TSDISCON.exe

![TSDISCON Command Help](/images/2008-08-23-tips-disconnecting-remote-desktop-users/image_6.png)

TSDISCON: Disconnects a terminal session. 讚! 就是要這種東西... 用法很簡單，如果你有遠端 SERVER 的管理者權限，防火牆又沒把 NETBIOS 關掉，那麼可以這樣用:

1. 先登入遠端 server  
   NET USE \\MYSERVER /user:MYACCOUNT *
2. 踢掉其它人  
   TSDISCON 1 /SERVER:MYSERVER

BINGO，其中要注意一下就是 SESSION ID，也就是上面工作管理員 ID 那一欄。0 代表 console，其它就是額外的連線。不過除非你有另外買 LICENCE，否則 OS 內建的授權只有兩個連線，意思就是亂猜一通，1 跟 2 隨便挑一個砍了就好...

指令成功的話，被你挑中的連線就會中斷了。趁對方還沒重新連上去之前，快點連進去佔名額吧 :D