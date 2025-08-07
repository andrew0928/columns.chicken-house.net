# x64 Programming #2：ASP.NET 讀取 CSV 於 IIS 6 x64 失敗的排除實錄  

# 問題／解決方案 (Problem/Solution)

## Problem: ASP.NET 網站在 IIS 6 (x64) 讀取 CSV 時當機

**Problem**:  
開發者於 Vista x64 + Visual Studio 2008 使用下列程式碼，透過 ODBC「Microsoft Text Driver」讀取 CSV 檔並繫結至 DataGrid，在內建開發伺服器 (DevWeb) 執行一切正常；當相同網站部署到 Windows 2003 x64 + IIS 6 時，網頁立即拋出例外，無法載入 ODBC Driver。  

```csharp
OdbcConnection conn =
    new OdbcConnection("Driver={Microsoft Text Driver (*.txt; *.csv)};DBQ=" 
                        + Server.MapPath("~/App_Data"));
OdbcDataAdapter adpt = new OdbcDataAdapter("select * from [database.txt]", conn);
adpt.Fill(ds);
```

**Root Cause**:  
1. IIS 6 預設以 64 位元模式執行 w3wp.exe。  
2. Microsoft Text Driver (ODBC) 只有 32 位元版本，無 64 位元版本。  
3. 64 位元 Process 內無法載入 32 位元 DLL；因此當 ASP.NET 應用程式 (64 位元) 嘗試建立 ODBC 連線時，OS 找不到相容 (64 位元) 的 Driver 而失敗。  
4. 管理工具誤導：控制台開啟的 *ODBC Data Source Administrator* 為 64 位元版 (`%SystemRoot%\System32\odbcad32.exe`)，看不到任何 32 位元 Driver，更讓問題難以判讀。  

**Solution**:  
將 IIS 6 切換為「32 位元工作模式」執行，使 ASP.NET 應用程式於 32 位元 Process 中執行，得以載入 32 位元之 Microsoft Text Driver。步驟：  

1. 以系統管理員身分開啟命令列：  
   ```cmd
   cscript %SYSTEMDRIVE%\inetpub\adminscripts\adsutil.vbs 
           SET W3SVC/AppPools/Enable32bitAppOnWin64 1
   ```  
2. 註冊 32 位元 ASP.NET 2.0：  
   ```cmd
   %SystemRoot%\Microsoft.NET\Framework\v2.0.50727\aspnet_regiis.exe -i
   ```  
3. 於 IIS 管理員中，將 *ASP.NET v2.0.50727 (32-bit)* 加入「Web Service Extensions」並設為 *Allowed*。  
4. 重新啟動 IIS (`iisreset`)。  

關鍵思考點：  
• 讓整個應用程式池以 32 位元執行，就不再需要 64 位元版 Driver，根本性地繞過「x64 Process 不能載入 x86 Driver」的限制。  

**Cases 1**:  
背景：內部系統需讓使用者上傳 Excel/CSV，伺服器為 Windows 2003 x64。  
問題：部署後拋出 ODBC 例外，ODBC 管理員看不到任何 Text Driver。  
解法：照上述步驟將 `Enable32bitAppOnWin64` 設為 1，重新註冊 32 位元 ASP.NET。  
效益：  
• 網站可順利匯入 CSV，終端使用者不再回報錯誤。  
• 避免改寫程式碼或另行購買 64 位元 Driver，0 元成本修復。  

**Cases 2**:  
背景：另一台 Windows 2008 x64 + IIS 7 測試機，同時需跑 32 位元舊版 COM 元件及 64 位元 WCF。  
處理：在 IIS 7 直接針對單一 Application Pool 勾選「Enable 32-bit Applications」，即可讓舊 COM 元件正常載入，同時保留其他站台以 64 位元模式執行。  
效益：  
• 同一台伺服器並行多版本元件，無需額外硬體；部署彈性大幅提升。  