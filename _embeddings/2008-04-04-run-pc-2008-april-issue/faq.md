# [RUN! PC] 2008 四月號

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這篇文章發表在哪一期的 RUN! PC 雜誌？
文章刊登於 2008 年四月號的 RUN! PC。

## Q: 想要下載或線上試跑文章中的 ASP.NET 執行緒範例程式，該到哪裡取得？
可至 http://demo.chicken-house.net/runpc/2008-04/2008-04.zip 下載範例程式；若僅想線上試跑，可直接瀏覽 http://demo.chicken-house.net/runpc/2008-04/。

## Q: 在執行範例程式前需要注意 Internet Explorer 的什麼預設限制？
IE 預設對同一網站僅建立 2 條 HTTP 連線，可能導致測試結果與文章描述不同。

## Q: 如果要提高 IE 的同站連線數上限，該怎麼做？
可透過修改登錄檔（或匯入提供的 IE.reg）來調整：
[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings]  
"MaxConnectionsPerServer"=dword:00000008  
"MaxConnectionsPer1_0Server"=dword:00000008

## Q: 文中提供的 IE 連線上限調整檔在哪裡下載？
可於 http://demo.chicken-house.net/runpc/2008-04/ie.reg 下載並匯入，以快速設定 IE 的同站連線數上限。