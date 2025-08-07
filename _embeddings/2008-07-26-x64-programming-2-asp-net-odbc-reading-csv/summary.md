# x64 programming #2: ASP.NET + ODBC (讀取 CSV)

## 摘要提示
- 範例程式: 以 ASP.NET 2.0 透過 Microsoft Text Driver 讀取 CSV 並以 DataGrid 顯示。
- 開發環境: 在 Vista x64 + VS2008 的內建 DevWeb Server 上正常執行。
- 部署失敗: 移轉到 Windows 2003 x64 + IIS6 後發生 ODBC 相關錯誤訊息。
- ODBC 驅動: 64 位元系統預設只列出 64 位元驅動，找不到 32 位元 Text Driver。
- 驗證方法: 執行 SysWOW64 目錄下的 32 位元 ODBC 管理員可看到所需驅動。
- 問題本質: 64 位元行程無法載入 32 位元驅動，導致連線失敗。
- IIS6 限制: 同一部機器只能擇一使用 32 或 64 位元模式執行工作行程。
- 解決步驟: 透過 adsutil.vbs 啟用 Enable32bitAppOnWin64，再重新註冊 32 位元 ASP.NET。
- 成功驗證: 切換後重新部署，CSV 資料順利顯示於網頁。
- 延伸思考: x64 環境需檢視所有 COM/OleDB/Plug-in 是否有 64 位元版本，否則得回退 32 位元模式。

## 全文重點
本文以一段極簡的 ASP.NET 範例程式為引子，示範如何利用 ODBC 的 Microsoft Text Driver 讀取位於 App_Data 資料夾中的 CSV 檔並以 DataGrid 呈現。在 Vista x64 的開發機上以 Visual Studio 內建伺服器測試一切正常，然而當專案部署到 Windows Server 2003 x64 的 IIS6 上時卻立即噴錯，顯示無法載入對應的 ODBC 驅動。作者先在系統的 ODBC Data Source Administrator 檢查，意外發現 64 位元控制台完全沒有列出 Text Driver；進一步啟動 SysWOW64\odbccp32.cpl 的 32 位元版本後才看到熟悉的驅動，因而確定問題出在執行階段嘗試以 64 位元行程載入僅有 32 位元的驅動。  

由於 IIS6 每一個應用程式集區只能在單一位元模式執行，若要使用 32 位元驅動，唯有將整個 Application Pool 切換到 32 位元。文章引用 Microsoft KB894435，說明透過命令
cscript … adsutil.vbs SET W3SVC/AppPools/Enable32bitAppOnWin64 1  
以及執行 %SystemRoot%\Microsoft.NET\Framework\v2.0.xxxxx\aspnet_regiis.exe -i
即可讓 IIS 重新以 32 位元模式承載 ASP.NET 2.0。完成設定、重啟 IIS 之後，網頁成功抓到 CSV 資料顯示，問題迎刃而解。作者最後提醒，x64 移植的真正難處在於外部元件：凡屬 In-Process 的 ODBC Driver、OLE DB Provider、COM 元件、ActiveX、Codec… 等都必須有 64 位元版本才能在 64 位元行程中使用；只要其中一塊缺席，就只能整體退回 32 位元模式執行，並預告後續將整理更多實務碰壁經驗。

## 段落重點
### 1. 範例程式與環境說明
作者提供 Default.aspx 及其後置程式碼，透過 OdbcConnection 連線到 Microsoft Text Driver，將 ~/App_Data/database.txt 讀入 DataSet 再繫結至 DataGrid；開發環境為 Vista x64 + VS2008 的 DevWeb Server，範例在本機執行可正確顯示姓名與 e-mail 資料。

### 2. 部署至 IIS6 後的錯誤現象
相同程式部署到 Windows Server 2003 x64 IIS6，立刻出現 OdbcException，訊息指出找不到資料來源及驅動，讓人一開始無從判斷是程式、系統還是安裝缺失所致。

### 3. 追查 ODBC 驅動版本差異
進入控制台的 ODBC Data Source Administrator 檢查，發現 64 位元介面完全沒有顯示 Microsoft Text Driver；啟動 SysWOW64\odbccp32.cpl 的 32 位元 ODBC 管理員後才確認驅動存在，由此推斷 IIS 以 64 位元行程執行，無法載入 32 位元驅動造成失敗。

### 4. IIS6 切換至 32 位元模式的實作
參考 KB894435，透過 adsutil.vbs 將 Enable32bitAppOnWin64 設為 1，並使用 aspnet_regiis.exe 重新註冊 32 位元 ASP.NET 2.0，再於 IIS Manager 將對應 Web Service Extension 設為 Allowed；切換後同一網站即可使用 32 位元 ODBC Driver 成功讀取 CSV。

### 5. x64 移植的普遍挑戰與結語
作者體會到在 x64 平台開發常受制於外部元件是否具備 64 位元版本，包含 ODBC/OleDB、COM、ActiveX、Codec 等都屬同一問題範疇；IIS6 只能擇一執行位元模式且應用程式無法混和，雖 IIS7 之後已可並存，但在舊平台上仍需權衡；文章最後預告將在後續分享更多碰壁案例供讀者參考。