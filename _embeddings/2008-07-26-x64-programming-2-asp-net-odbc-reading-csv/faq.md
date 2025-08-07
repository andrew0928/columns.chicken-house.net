# x64 programming #2: ASP.NET + ODBC (讀取 CSV)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼範例程式在 Vista x64 的開發伺服器可以正常抓取 CSV，佈署到 Windows 2003 x64 IIS6 後卻收到「ERROR [IM002] [Microsoft][ODBC Driver Manager] Data source name not found and no default driver specified」？

IIS6 預設以 64 位元模式執行，而 Microsoft Text Driver（*.txt; *.csv）只有 32 位元版本。64 位元行程看不到 32 位元的 ODBC driver，因而導致驅動程式找不到並噴錯。

---

## Q: 在 Windows x64 系統裡要從哪裡開啟 32 位元版的「ODBC Data Source Administrator」？

執行  
c:\Windows\SysWOW64\odbccp32.cpl  
（或 c:\Windows\SysWOW64\odbcad32.exe）即可進入 32 位元 ODBC 管理工具並看到完整的 32 位元驅動程式清單。

---

## Q: 單一行程可以同時載入 x86 及 x64 的 DLL 或驅動程式嗎？

不行。同一個 process 只能載入一種位元架構的程式碼。所有 In-Process 元件（ODBC driver、OLE DB Provider、COM 元件、ActiveX、Codec…）都必須與行程位元數相同。

---

## Q: 要如何讓 IIS6 在 x64 作業系統上以 32 位元模式執行 ASP.NET 2.0，從而使用 32 位元的 ODBC driver？

1. 以系統管理員身分開啟命令提示字元。  
2. 啟用 32 位元應用程式池：  
   cscript %SYSTEMDRIVE%\inetpub\adminscripts\adsutil.vbs SET W3SVC/AppPools/Enable32bitAppOnWin64 1  
3. 重新註冊 32 位元版 ASP.NET 2.0：  
   %SYSTEMROOT%\Microsoft.NET\Framework\v2.0.40607\aspnet_regiis.exe -i  
4. 在 IIS 管理員的 Web Service Extensions 清單中，將「ASP.NET 2.0.40607 (32-bit)」設成 Allowed。  
完成後，IIS6 即會以 32 位元模式執行，程式可正常呼叫 32 位元 ODBC driver。

---

## Q: IIS6 能同時執行 32 位元與 64 位元應用程式嗎？

不能。IIS6 只能二擇一地在整個站台上啟用 32 位元或 64 位元模式。若需要同時並存兩種位元架構，可升級到 IIS7，它已支援在同一台伺服器上並行 x86 與 x64 應用程式。

---

## Q: 如果應用程式中有任何元件沒有 64 位元版本，最直接的解法是什麼？

將整個應用程式（或該應用程式池）切換到 32 位元模式執行，確保所有相依元件皆為 x86，便能避免位元數不符所造成的載入失敗。