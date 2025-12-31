---
layout: synthesis
title: "x64 programming #2: ASP.NET + ODBC (讀取 CSV)"
synthesis_type: summary
source_post: /2008/07/26/x64-programming-2-asp-net-odbc-reading-csv/
redirect_from:
  - /2008/07/26/x64-programming-2-asp-net-odbc-reading-csv/summary/
postid: 2008-07-26-x64-programming-2-asp-net-odbc-reading-csv
---

# x64 programming #2: ASP.NET + ODBC (讀取 CSV)

## 摘要提示
- CSV 讀取：以 ODBC Microsoft Text Driver 讀取 CSV/TXT，資料繫結至 ASP.NET DataGrid。
- 開發環境正常：在 Vista x64 上用 Visual Studio 2008 的開發伺服器執行一切正常。
- 佈署失敗：佈署到 Windows Server 2003 x64、IIS6 後執行發生錯誤。
- 驅動差異：64 位元 ODBC 管理工具看不到 32 位元 ODBC 驅動，導致連線失敗。
- 32/64 位元面板：需啟用 32 位元 ODBC 管理工具 c:\Windows\SysWOW64\odbccp32.cpl 才看得到文字驅動。
- 模式不可混用：單一 Process 內不能同時載入 x86 與 x64 元件，ODBC/OleDB/COM/ActiveX/Codec 皆受限。
- IIS6 限制：IIS6 在 x64 上只能二選一，以 32 或 64 位元模式執行（無法同時）。
- 切換作法：以 adsutil.vbs 啟用 IIS 32 位元模式，再以 32 位元 aspnet_regiis 安裝 ASP.NET 2.0。
- IIS7 改善：IIS7 可同機同時跑 32/64 位元應用程式（不同應用程式集區）。
- 經驗教訓：佈署前盤點所有相依元件的 x64 版，否則需退回 32 位元模式。

## 全文重點
作者示範一個極簡的 ASP.NET 範例，利用 ODBC 的 Microsoft Text Driver 從 App_Data 下的 database.txt（CSV 格式）讀取資料，透過 OdbcConnection 與 OdbcDataAdapter 填入 DataSet，最後繫結到 DataGrid 顯示。在開發環境（Vista x64 + VS2008，使用內建開發伺服器）運行正常，但佈署至 Windows Server 2003 x64、IIS6 後卻發生錯誤，初看難以判斷原因。

為釐清問題，作者先檢查系統 ODBC 設定，驚訝地發現 64 位元的 ODBC 管理工具裡看不到預期的文字檔驅動程式。靈機一動轉向 32 位元脈絡調查，嘗試從 Excel 使用 ODBC 成功後，意識到可能是 x64 與 x86 的差異。進一步在 c:\Windows\SysWOW64\ 內啟動 32 位元版 ODBC Data Source Administrator（odbccp32.cpl），果然看見需要的 32 位元 ODBC Driver，確認問題源自 32/64 位元模式與驅動不匹配。

作者進而說明 x64 的關鍵限制：同一個進程中不能混用 x86 與 x64 程式碼。這不只指硬體裝置驅動，廣義上包含 ODBC Driver、OleDB Provider、COM 元件（In-Process）、ActiveX 控制項、Media Player 的 Codec 等等，一律必須與執行程序的位元數一致。當應用程式或其相依元件缺少對應的 x64 版本時，若仍以 64 位元模式執行，便會在載入驅動或元件時失敗。

解法是讓 ASP.NET 應用在 IIS6 上改以 32 位元模式執行，便能使用 32 位元的 ODBC Driver。文章引用微軟知識庫（KB894435）並列出操作步驟：以 adsutil.vbs 將 IIS 啟用 32 位元模式，接著用 32 位元 aspnet_regiis.exe 安裝 ASP.NET 2.0（32 位元）並在 IIS 中允許該版本。切換後同一個範例在 IIS6 上即可正常讀取 CSV 並顯示。

作者總結，IIS6 在 x64 上只能二選一（整機以 32 或 64 位元模式跑應用程式），而 IIS7 則可在不同應用程式集區分別以 32/64 位元執行，解決無法並存的限制。轉向 x64 的實務挑戰在於相依性繁多，任何一個元件沒有 x64 版都會成為瓶頸；若無法全面升級，只能退回以 32 位元模式執行。作者預告將在後續篇章分享更多在 x64 上踩到的坑，協助讀者避免重蹈覆轍。

## 段落重點
### 範例概述與程式碼
作者提供一個最簡示範：在 Default.aspx.cs 以 OdbcConnection 指向 App_Data 路徑，用 Microsoft Text Driver (*.txt; *.csv) 執行「select * from [database.txt]」讀入 DataSet，再繫結給 DataGrid 顯示。Default.aspx 僅包含一個 DataGrid 控制項，資料檔 database.txt 是標準 CSV 格式（name,email 與多筆資料）。在 VS2008 開發伺服器執行可順利顯示列表。

### 佈署到 IIS x64 後的錯誤
同一程式佈署到 Windows Server 2003 x64、IIS6 後發生錯誤。初期無明確線索，作者先假設可能為環境或驅動問題，打算用現成工具驗證 ODBC 是否可用，並在系統 ODBC 管理工具中尋找文字驅動，結果卻發現清單裡沒有該驅動，與預期不符。

### 追查：ODBC 驅動與管理工具的 32/64 位元差異
作者嘗試以 Excel 開啟 ODBC 成功，進一步聯想到 32/64 位元之別。於是從 SysWOW64 啟動 32 位元版 ODBC Data Source Administrator（c:\Windows\SysWOW64\odbccp32.cpl），果真出現 Microsoft Text Driver 與相關 32 位元驅動。由此確立：64 位元 ODBC 管理工具看不到 32 位元驅動，導致在 64 位元視角下無法設定/使用該 Driver。

### 原因解析：x64 與 x86 模式不可混用
問題核心在於單一 Process 內不得混用 x86 與 x64 元件。除硬體驅動外，ODBC Driver、OleDB Provider、各式 In-Process COM、Plug-in、ActiveX、媒體 Codec 皆屬「驅動/元件」範疇，必須與宿主程序位元數一致。當網站在 64 位元 IIS 工作進程上執行，而需要的 ODBC Driver 只有 32 位元版本時，就會在載入連線提供者時失敗。

### 解法：IIS6 切換為 32 位元執行 ASP.NET 2.0
依 KB894435，在 IIS6 上可將整體執行模式切到 32 位元：先用 adsutil.vbs 將 Enable32bitAppOnWin64 設為 1，再用 Framework 32 位元路徑下的 aspnet_regiis.exe -i 安裝 ASP.NET 2.0（32 位元），並在 IIS 的 Web Service Extensions 允許該版本。切換完成後，應用程式即可使用 32 位元 ODBC Driver，範例成功運行，CSV 內容如預期顯示於 DataGrid。

### 延伸與結語：IIS7 的改善與實務建議
IIS6 在 x64 僅能二選一，無法同機同時跑 32/64 位元應用；IIS7 起可於不同應用程式集區分別選擇位元數並存。實務上遷移到 x64 的難點在於相依元件眾多，需逐一確認是否有 x64 版本；若有任一缺漏，往往只能改以 32 位元模式執行應用。作者最後提醒，佈署前務必盤點 ODBC/OleDB/COM/ActiveX 等依賴，避免在正式環境踩坑，並預告後續將分享更多 x64 相容性案例。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - ASP.NET Web Forms 基本結構（.aspx/.cs、Page_Load、資料繫結）
   - ADO.NET 與 ODBC 基本用法（Connection、DataAdapter、DataSet）
   - Windows x64 與 x86 架構差異（同一個進程不可混用不同位元的元件）
   - IIS 6/7 基本管理（應用程式集區、位元模式切換）
   - ODBC Data Source Administrator（32 位與 64 位的管理工具差異）

2. 核心概念：
   - ODBC Text Driver 讀取 CSV：以 OdbcConnection + OdbcDataAdapter 查詢 CSV（Text Driver）
   - 位元相容性：進程位元（x86/x64）必須與驅動/提供者/COM 元件位元一致
   - IIS 位元模式：IIS6 整站二選一（32 或 64 位）；IIS7 可在不同應用程式集區並存
   - 管理工具對應：32 位 ODBC 管理工具需從 SysWOW64 啟動，才能看到 32 位驅動
   - 部署差異：開發伺服器可跑，部署 IIS x64 出現驅動缺失或位元不相容

3. 技術依賴：
   - ASP.NET 應用程式 → .NET Framework 執行階段 → IIS 應用程式集區位元 → ODBC/OLE DB/COM 驅動（相同位元）
   - CSV 讀取 → Microsoft Text Driver（ODBC）→ ODBC DSN/驅動安裝狀態
   - 管理與診斷 → 正確版本的 ODBC Admin 工具（SysWOW64）→ 驗證驅動存在與可用性

4. 應用場景：
   - 在 ASP.NET 站台中快速讀取 CSV 或文字資料表
   - 將本機可跑的 WebForms 專案部署至 x64 的 IIS 環境
   - 需要使用 ODBC/OLE DB/COM 元件（如讀取 Excel）且只提供 32 位驅動的情境
   - 針對「部署到 IIS 後驅動找不到/無法載入」的問題排除

### 學習路徑建議
1. 入門者路徑：
   - 建立簡單的 WebForms 頁面與 DataGrid
   - 使用 OdbcConnection 與 OdbcDataAdapter 讀取 App_Data 下的 CSV（Text Driver）
   - 在本機開發伺服器（DevWeb/Cassini）驗證資料繫結與顯示

2. 進階者路徑：
   - 理解 x86/x64 在 IIS 中的執行模式與限制
   - 學會使用 32 位 ODBC 管理工具（SysWOW64）檢視/設定驅動與 DSN
   - 熟悉在 IIS6 切換 32 位模式與安裝 32 位 ASP.NET 的步驟；了解 IIS7 可並存模式的配置思路

3. 實戰路徑：
   - 將站台部署到 Windows Server x64 + IIS6，遇錯誤時以 ODBC Admin 驗證驅動
   - 如需 32 位驅動，切換 IIS6 為 32 位模式並重新註冊 32 位 ASP.NET；於 IIS7 以 32 位應用程式集區承載
   - 建立檢核清單：所有相依元件（ODBC/OLE DB/COM/Plug-in/Codec）是否有目標位元版本，否則制定降階執行策略

### 關鍵要點清單
- ODBC Text Driver 讀取 CSV：使用 Driver={Microsoft Text Driver (*.txt; *.csv)} 搭配 DBQ 指向資料夾 (優先級: 高)
- 查詢語法與檔名：以 select * from [database.txt] 查詢目標檔案（含副檔名） (優先級: 中)
- 資料繫結：使用 DataSet + DataGrid/資料繫結控制項顯示結果 (優先級: 低)
- 位元不可混用：同一個進程不得同時載入 x86 與 x64 的驅動/元件 (優先級: 高)
- 驅動廣義定義：ODBC、OleDB Provider、COM、ActiveX、各式 Plug-in/Codec 皆屬需對位元相容的驅動/元件 (優先級: 中)
- 本機可跑、IIS 掛掉的常因：IIS 進程位元與驅動位元不相容或缺少對應驅動 (優先級: 高)
- 32 位 ODBC 管理工具入口：於 c:\Windows\SysWOW64 啟動 32 位 ODBC 管理（文中例：odbccp32.cpl；常見亦為 odbcad32.exe）(優先級: 高)
- IIS6 位元模式限制：IIS6 只能選擇整體以 32 位或 64 位其中一種模式執行 (優先級: 高)
- IIS6 切換 32 位模式指令：cscript %SYSTEMDRIVE%\inetpub\adminscripts\adsutil.vbs SET W3SVC/AppPools/Enable32bitAppOnWin64 1 (優先級: 高)
- 註冊 32 位 ASP.NET：%SYSTEMROOT%\Microsoft.NET\Framework\v2.0.40607\aspnet_regiis.exe -i 並在 Web Service Extensions 設為 Allowed (優先級: 中)
- IIS7 改善：可同時存在 32/64 位應用程式（以不同應用程式集區） (優先級: 中)
- 驗證方法：先用已知可行的程式/工具（如 Excel）測試 ODBC 是否可用，協助判斷是程式或系統問題 (優先級: 中)
- 部署心法：若任何相依元件無 x64 版，需以 32 位模式承載整個應用或該應用程式集區 (優先級: 高)
- CSV/Excel 差異：CSV 可改用文字解析替代；Excel 常需 ODBC/OLE DB/Interop，位元相容性更關鍵 (優先級: 中)
- 路徑與權限：DBQ 指向的資料夾需正確（如 Server.MapPath("~/App_Data")）且 IIS 帳號具讀取權限 (優先級: 中)