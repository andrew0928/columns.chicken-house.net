最近真是, 裝什麼, 什麼就出問題...

因為信用卡繳費期限要到了, 換了 Vista 用 WebATM 又有點怪怪的, 其它銀行的都可以, 唯讀台新的 ATM 一連就當, 看到它有 MyATM 這個小工具可以安裝, 就裝起來看看...

沒想到它只是個很惹人厭的 Applet, 躲在右下角, 等你 ATM 卡片塞進去就跳網頁出來... (這樣的話我幹麻裝... [:@])

沒想到要移除後, 新增移除工具竟然跟我講權限不足? 搞什麼, Administrators 還沒權限是要怎樣才有權限? 不過這年頭 Error Message 都亂寫一通, 一堆不知道啥怪問題的就說是權限... 讓我想起我追過的一堆 Bug, 都是 try { ... } catch 攔到不知明的 Exception, 就一概顯示 "權限不足, 請聯絡系統管理員" ...

最好系統管理員真的這麼了不起, 咳咳, 沒事開了 Registry Editor 出來找看看, search "台新銀行", 找到這筆:

電腦\HKEY_LOCAL\MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{F25E1429-F70A-4843-8885-84CE5E18C352}\UninstallString

C:\Program Files\\InstallShield Installation Information\{F25E1429-F70A-4843-8885-84CE5E18C352}\setup.exe "-removeonly"

發現它的路逕怎麼多了一個反斜線? 拿掉之後再移除一次就 OK 了

真是它ㄨㄨㄨ的... 還好我無聊, 不然安裝程式清單老卡一個不想要的軟體, 看了還真礙眼... 哈哈, 弄完了, 收工!

![MyATM uninstall registry fix](/images/2007-04-10-accidentally-installed-myatm/image03.png)