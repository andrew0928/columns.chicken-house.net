# Tips: 踢掉遠端桌面連線的使用者

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 當 RDP 連線人數已滿、又無法碰到實體主機時，該怎麼遠端踢掉其他使用者？
先在遠端桌面用「/console」參數連入伺服器的 console session，開啟工作管理員 (Task Manager) 的最後一頁「使用者 (Users)」，選取要中斷的帳號並登出即可釋放名額。

## Q: 如果連 console session 也被占用，還有什麼辦法可強制中斷其他人的遠端桌面連線？
可以使用內建指令 TSDISCON.exe。做法是：
1. 以系統管理者權限先連入伺服器  
   `NET USE \\MYSERVER /user:MYACCOUNT *`
2. 執行  
   `TSDISCON 1 /SERVER:MYSERVER`  
   (其中 1 為欲中斷的 Session ID)  
成功後指定的連線會被強制中斷。

## Q: TSDISCON 命令中的 Session ID 0 表示什麼？
Session ID 0 代表伺服器的 console session，而 1、2… 等則是額外的 RDP 連線。

## Q: 在沒有另外購買授權的情況下，Windows 伺服器預設最多允許多少個同時的 RDP 連線？
作業系統內建的授權只允許 2 個同時的遠端桌面連線。

## Q: 執行 TSDISCON 前需要滿足哪些條件？
使用者必須擁有遠端伺服器的系統管理者權限，且防火牆不能封鎖 NetBIOS，才能成功透過 TSDISCON 中斷其他人的 Session。