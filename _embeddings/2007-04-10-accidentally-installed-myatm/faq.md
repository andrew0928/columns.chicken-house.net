# 手癢亂裝 MyATM...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 移除 MyATM 時，新增/移除程式出現「權限不足」訊息，其實是什麼原因？
在登錄檔的 UninstallString 路徑多了一個多餘的反斜線 ( \ )，導致解除安裝程式無法正確呼叫，才誤報「權限不足」。

## Q: 要如何成功解除安裝 MyATM？
1. 開啟登錄編輯器，找到  
   HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{F25E1429-F70A-4843-8885-84CE5E18C352}\UninstallString  
2. 將其中  
   C:\Program Files\\InstallShield Installation Information\{F25E1429-F70A-4843-8885-84CE5E18C352}\setup.exe "-removeonly"  
   多出的那個反斜線刪除，變成  
   C:\Program Files\InstallShield Installation Information\{F25E1429-F70A-4843-8885-84CE5E18C352}\setup.exe "-removeonly"  
3. 再次執行「新增/移除程式」中的移除動作即可順利卸載。

## Q: 為什麼作者想要移除 MyATM？
MyATM 只是個藏在系統右下角、插入 ATM 卡就跳出網頁的 Applet，既沒解決 Vista 下台新 WebATM 當掉的問題，還顯得惹人厭，因此作者決定將它移除。