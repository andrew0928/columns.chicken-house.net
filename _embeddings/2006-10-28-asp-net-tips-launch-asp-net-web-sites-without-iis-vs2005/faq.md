# ASP.NET Tips: Launch ASP.NET Web Sites without IIS / VS2005

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 如果不想安裝 IIS 或開啟 Visual Studio 2005，還能如何快速啟動並瀏覽一個 ASP.NET 網站？
利用 .NET Framework 2.0 內建的 WebDev.WebServer.EXE。作者提供了一段批次檔 (見下) 來自動隨機指定埠號、啟動 Development Web Server，並立即開啟瀏覽器檢視網站。  
```batch
set DEVWEB_PORT=%random%
start /min /low c:\Windows\Microsoft.NET\Framework\v2.0.50727\WebDev.WebServer.EXE /path:%1 /port:%DEVWEB_PORT%
start http://localhost:%DEVWEB_PORT%/
@set DEVWEB_PORT=
```

## Q: 要讓這支批次檔隨處可用，應該把它放在哪裡？
將批次檔的「捷徑」放到  
c:\Documents and Settings\{your account name}\SendTo  
資料夾下。如此日後在檔案總管對任何網站目錄按右鍵時，就能透過「傳送到 → Dev ASP.NET Web」直接執行。

## Q: 實際操作步驟是什麼？
1. 下載並解開網站原始碼。  
2. 在檔案總管找到該網站資料夾。  
3. 右鍵點選資料夾 → 傳送到 → Dev ASP.NET Web。  
批次檔會自動啟動 Development Web Server 及瀏覽器，完成網站預覽。