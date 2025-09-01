# x64 programming #2: ASP.NET + ODBC (讀取 CSV)

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 ODBC？它的用途是什麼？
- A簡: ODBC 是資料存取標準介面，透過驅動程式讓應用程式以一致方式連接多種資料來源。
- A詳: ODBC（Open Database Connectivity）是微軟提出的通用資料存取介面標準。應用程式只需面對 ODBC API，不必關心底層資料來源的差異（如 CSV、Excel、SQL Server、Oracle 等），由對應的 ODBC 驅動程式負責轉譯與連線。它的特點是標準化、可擴充、跨資料來源；常見應用於將異質資料（如文字檔或舊系統資料）統一接入到 .NET、Excel、BI 或報表系統。本文示例以 Microsoft Text Driver 透過 ODBC 將 CSV 當作表格讀取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q15, C-Q1, D-Q1

Q2: 什麼是 Microsoft Text Driver（*.txt; *.csv）？
- A簡: 一種 ODBC 驅動，將文字/CSV 檔視為資料表，支援 SQL 查詢與欄位推斷。
- A詳: Microsoft Text Driver 是 ODBC 驅動程式，讓應用程式以表格方式讀取文字檔（含 CSV）。它將目標資料夾視為資料庫，個別檔案視為資料表，透過簡化的 SQL（如 SELECT）查詢資料。特點是免安裝資料庫、即用即查；應用場景包括暫存資料、系統交換、快速匯入等。限制在於編碼、類型推斷與大型檔案效能，較正式資料庫弱；但對 CSV 快速顯示與簡易報表非常實用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, B-Q1, B-Q16, C-Q2

Q3: 在 ASP.NET 中用 ODBC 讀取 CSV 的基本流程是什麼？
- A簡: 建連線、查詢填入 DataSet、資料繫結至 DataGrid，於 Page_Load 執行。
- A詳: 基本步驟為：1) 以 OdbcConnection 建立連線字串，Driver 選 Text Driver，DBQ 指向 CSV 所在資料夾；2) 建立 OdbcDataAdapter 與 SELECT 語句（如 SELECT * FROM [database.txt]）；3) 以 DataAdapter.Fill 將結果填入 DataSet；4) 將 DataSet.Tables[0] 指派為 DataGrid 的 DataSource 並 DataBind。通常在 Page_Load（可搭配 !IsPostBack）執行。此流程無需額外資料庫，便能快速顯示 CSV。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q3, C-Q1, C-Q2

Q4: DataSet、DataAdapter、DataGrid 各自扮演什麼角色？
- A簡: DataAdapter 查詢並填充 DataSet；DataGrid 負責資料呈現與繫結。
- A詳: DataAdapter 是資料橋樑，負責執行查詢、將結果填入記憶體中的離線資料容器 DataSet（或 DataTable）。DataSet 以表格集合儲存資料，不連線狀態操作。DataGrid（WebForms 控制項）負責 UI 顯示與資料繫結，透過 DataSource 接收資料並渲染為表格。三者配合：Adapter→DataSet→Grid，分離資料存取與呈現，便於維護與測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q3, C-Q1, D-Q5

Q5: 什麼是 x64 與 x86？與程式執行有何關聯？
- A簡: x64 與 x86 分別指 64/32 位元架構，程式與驅動需與進程位元數相符。
- A詳: x86 指 32 位元、x64 指 64 位元 CPU/OS/程式架構。位元數影響可用記憶體、指令集與二進位相容性。關鍵原則：同一進程內不可混用不同位元數的元件（含 ODBC 驅動、COM、ActiveX、Codec）。在 64 位 Windows，若 IIS 以 64 位執行，則僅能載入 64 位驅動；若驅動只有 32 位，必須讓應用程式以 32 位執行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q4, B-Q5, D-Q2

Q6: 為什麼 64 與 32 位程式不能在同一進程中混用？
- A簡: 不同位元 ABI 與載入器規範不同，二進位無法互通，會載入失敗。
- A詳: 進程位元數決定其位址寬度、呼叫慣例、結構對齊與指令集。OS 載入器依進程位元數載入同位元的 DLL。32 位 DLL 與 64 位 DLL 在二進位層面不相容，彼此函式匯出、堆疊慣例不同，強行載入會失敗或崩潰。故同一進程（如 w3wp.exe）只能載入同位元元件，包含 ODBC 驅動、COM、ActiveX 與 Plug-in。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q4, D-Q2, D-Q4

Q7: ODBC Driver 與「硬體」Driver 有何異同？
- A簡: 皆屬驅動程式，提供標準介面；ODBC 驅動是軟體層的資料存取驅動。
- A詳: 驅動（Driver）廣義上是介於系統與資源之間的抽象層。硬體驅動介接 OS 與硬體裝置；ODBC 驅動介接應用程式與資料來源（CSV、Excel、DB）。相同點是都提供標準化介面與實作差異抽象；不同點在於服務對象與執行層級。對 x64 而言，兩者皆需與進程位元數相容，否則無法載入或使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q6, B-Q1, D-Q1

Q8: 什麼是 ODBC Data Source Administrator？
- A簡: 管理 ODBC 驅動與資料來源（DSN）的工具，建立/測試連線設定。
- A詳: ODBC Data Source Administrator 是 Windows 系統工具，用於查看安裝的 ODBC 驅動、建立使用者/系統 DSN、測試連線、設定參數。於 64 位 Windows 上有 32 與 64 位兩個版本，分別管理各自位元的驅動與 DSN。使用錯誤版本常導致「找不到驅動」或清單空白的誤判。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q25, C-Q4, D-Q3

Q9: 為什麼 64 位 Windows 會有兩個 ODBC 管理工具？
- A簡: 因為 32 與 64 位驅動與 DSN 分離，需各自管理與設定。
- A詳: 64 位 Windows 同時支援 32 與 64 位應用，對應需要 32 與 64 位 ODBC 驅動與 DSN。為避免混淆，系統提供兩套管理工具：64 位（管理 64 位驅動/DSN）與 32 位（管理 32 位）。常見路徑為 C:\Windows\System32\odbcad32.exe（64 位）與 C:\Windows\SysWOW64\...（32 位）。使用錯版本會看不到對應驅動或 DSN。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q4, B-Q25, D-Q3

Q10: 32 位與 64 位 ODBC DSN 有何差異？
- A簡: 兩者分別供同位元應用使用，互不相通，需在正確工具中建立。
- A詳: DSN（Data Source Name）是 ODBC 連線設定的命名集合，包含驅動、路徑、參數。64 位 DSN 僅供 64 位應用程式存取；32 位 DSN 僅供 32 位應用程式存取。它們分別由不同登錄檔範圍維護，彼此不可見。因此建立與測試時務必使用正確位元的 ODBC 管理工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q9, C-Q4, D-Q3

Q11: 為何在 IIS6 x64 上無法同時執行 x86 與 x64 Web 應用？
- A簡: IIS6 的 32 位模式是全伺服器層級開關，無法同機混合兩種模式。
- A詳: IIS6 在 64 位 Windows 上支援 32/64 位模式，但 Enable32bitAppOnWin64 是全域設定，切到 32 位後整個 w3svc 都以 32 位運作，無法同時執行 64 位應用。若系統有僅支援 64 位的網站，將受影響。IIS7 起改為每個應用程式集區可獨立設定，解決同機共存問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q4, C-Q5

Q12: ASP.NET 1.1 與 2.0 在 x64 上的支援差異是什麼？
- A簡: ASP.NET 1.1 僅支援 32 位；ASP.NET 2.0 可 32 或 64 位執行。
- A詳: 依微軟文件，ASP.NET 1.1 僅能在 32 位模式下運作；ASP.NET 2.0 則能在 32 或 64 位模式執行。若 IIS6 上同時需要 ASP.NET 1.1 與 2.0，必須將伺服器切至 32 位模式運作，並重新註冊 ASP.NET 2.0（32 位）對應的 ISAPI 指令碼對應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q3, D-Q4, A-Q11

Q13: 為什麼在 Visual Studio 開發伺服器可運作，部署 IIS 後卻失敗？
- A簡: 開發伺服器常為 32 位執行，IIS 可能以 64 位運作，驅動不相容。
- A詳: VS 內建的開發伺服器（DevWeb）通常以 32 位進程運作，能載入 32 位 ODBC 文字驅動，故程式可跑。部署到 IIS6 x64 時，若 AppPool 為 64 位，將嘗試載入 64 位驅動；系統未安裝對應驅動或僅有 32 位版本時，連線即失敗。根因是進程位元數與驅動位元數不匹配。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q6, D-Q2, D-Q9

Q14: 為什麼讀取 CSV 可改用純文字解析而不靠 ODBC？
- A簡: CSV 結構簡單，可用 .NET 檔案讀寫與分割解析避免驅動依賴。
- A詳: CSV 是逗號分隔的純文字格式。若需求僅為讀取展示，可用 File.ReadAllLines、Split、或現成解析器處理，避免 ODBC 驅動位元相依問題。優點是部署簡化、跨平台，缺點是型別、編碼、轉義、效能需自行處理，且缺乏 SQL 查詢便利。適用於簡化需求或臨時報表。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, C-Q7, D-Q6, D-Q5

Q15: 為什麼讀取 Excel 檔較難以純文字解析取代？
- A簡: Excel 格式複雜含型別/公式，需專用驅動或程式庫才能準確解析。
- A詳: Excel 檔（.xls/.xlsx）不僅是分隔文字，包含工作表結構、格式、資料型別、公式、日期與本機化等。純文字解析難以準確處理格式與相依，且歷史版本格式不一。因此常需依賴 ODBC/OleDb 或專用程式庫。若缺乏對應位元的驅動，需調整應用執行位元或改用其他解析方案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q8, D-Q9, A-Q14

Q16: IIS6 與 IIS7 在位元數支援的差異是什麼？
- A簡: IIS6 只有全域切換；IIS7 可每個應用程式集區分別設定 32/64 位。
- A詳: 在 IIS6，Enable32bitAppOnWin64 是 w3svc 全域設定，切換影響整機所有網站。IIS7 引入應用程式集區隔離，允許個別集區設定 Enable 32-Bit Applications（True/False），達到同機混用 32/64 位應用的目標，降低相依衝突，便於逐步遷移。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5, D-Q10, A-Q11

Q17: 什麼是 WOW64？與 32 位相容有何關聯？
- A簡: WOW64 是 64 位 Windows 上的 32 位相容層，隔離並執行 x86 程式。
- A詳: WOW64（Windows-On-Windows 64-bit）是 64 位 Windows 的相容層，可在 x64 上執行 32 位應用。它提供檔案與登錄檔重新導向（如 SysWOW64 資料夾）與位元隔離。雖允許 32 位程式運作，但不允許 64 位進程載入 32 位 DLL，仍須同位元原則。ODBC 管理工具亦因此分為兩個版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q25, D-Q3, A-Q9

Q18: 為什麼要關注 in-process 元件（COM、ActiveX、Codec）位元數？
- A簡: 因同進程載入需位元相容，否則無法載入或造成崩潰。
- A詳: In-Process 元件會以 DLL 形式載入至應用程式進程，受同位元相容性限制。包含 ODBC 驅動、OleDb Provider、COM/ActiveX、瀏覽器外掛、媒體 Codec 等。若任一必要元件沒有對應位元版本，整體功能將失效。部署前需盤點並確認所有相依具備相容版本，或調整應用的執行位元。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q4, C-Q8, A-Q6

Q19: 切換 IIS6 至 32 位模式的核心價值是什麼？
- A簡: 讓網站以 32 位執行，得以載入僅有 32 位版的驅動與元件。
- A詳: 當必要元件（如 ODBC Text Driver、Excel Provider）僅有 32 位版本時，IIS6 切換至 32 位模式可即時恢復功能，無需等待 64 位驅動。此法風險在於影響同機所有網站的位元環境，可能與 64 位相依衝突。權衡方式是獨立伺服器或升級至 IIS7 以集區隔離。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q4, A-Q11, A-Q16

Q20: 何時應安裝 64 位驅動，何時改用 32 位執行環境？
- A簡: 優先裝 64 位驅動；若缺少則將應用改為 32 位以確保相容。
- A詳: 若主機以 64 位模式運行且驅動有 64 位版本，應優先安裝以獲得更大記憶體與一致環境。若驅動僅有 32 位版本或第三方元件尚未支援 64 位，將應用設定為 32 位執行（如 IIS6 切換或 IIS7 集區 32 位）能快速解決。長期策略仍是逐步淘汰無 64 位支援的相依。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q26, C-Q5, D-Q10, A-Q19

Q21: 什麼是 ASP.NET WebForms 的 DataGrid？
- A簡: WebForms 的資料繫結表格控制項，支援排序、分頁與樣板。
- A詳: DataGrid 是 ASP.NET WebForms 早期常用的資料呈現控制項，可繫結任何 IEnumerable 或 DataSet/DataTable，並提供基本的排序、分頁、欄位格式化與模板自訂。其使用簡單，適合快速展示資料來源，如本文從 CSV 讀出資料後直接綁定顯示。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q1, D-Q5, A-Q4

Q22: 為什麼連線字串使用 DBQ 指向資料夾而非檔案？
- A簡: Text Driver 將資料夾視為資料庫，每個檔案是表格。
- A詳: Microsoft Text Driver 的設計是資料夾=資料庫、檔案=資料表。因此連線字串的 DBQ 參數要指定資料夾路徑；查詢語句用 [檔名] 指定表格，如 SELECT * FROM [database.txt]。此設計讓同一資料夾下多檔案可被同時查詢與聯結（受限）。部署時請確保路徑使用 Server.MapPath 轉實體路徑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q15, C-Q2, D-Q5

Q23: CSV 欄位如何對映為資料表欄位？
- A簡: 預設第一列為欄名，其餘列為資料；以逗號分隔欄位。
- A詳: Text Driver 會將第一行視為欄位名稱（若無則自動命名 F1…），每行資料以分隔符號（預設逗號）切分，推斷欄位型別並建立資料表結構。為避免解析誤差，確保第一行為正確標頭，資料遵循一致格式，必要時另建 schema 設定或採用手動解析。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q16, C-Q2, D-Q5

Q24: 為何部署前需檢查目標機器的 ODBC 驅動？
- A簡: 驅動是否存在與位元數相容決定程式能否正常連線與執行。
- A詳: 部署成功與否取決於目標環境是否具備所需驅動與相容位元。若目標只有 64 位而缺少 64 位 Text Driver，且 IIS 以 64 位運行，連線會失敗。應預先在正確位元 ODBC 管理工具檢查驅動清單、建立測試 DSN、以現成工具驗證，降低「到站才發現不相容」的風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q4, D-Q1, D-Q3

---

### Q&A 類別 B: 技術原理類

Q1: ODBC Text Driver 讀取 CSV 的運作原理是什麼？
- A簡: 將資料夾視為資料庫，檔案當表格，透過 SQL 與驅動解析資料。
- A詳: 技術原理說明：Text Driver 把 DBQ 指向的資料夾當成資料庫，每個 .txt/.csv 檔視為表，第一行視為欄名，解析分隔符。關鍵步驟或流程：1) OdbcConnection 以 Driver=Microsoft Text Driver 連線；2) OdbcCommand 發送 SELECT 語句；3) 驅動讀取檔案並解析欄位與資料；4) 返回結果集予 DataAdapter。核心組件介紹：OdbcConnection、OdbcCommand、OdbcDataAdapter、Text Driver 解析器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q22, C-Q2, D-Q5

Q2: OdbcDataAdapter.Fill 如何將 CSV 結果放入 DataSet？
- A簡: DataAdapter 執行查詢，將結果集轉為 DataTable，置入 DataSet。
- A詳: 技術原理說明：Fill 會根據 SelectCommand 執行查詢，建立 DataTable 結構並逐行載入。關鍵步驟或流程：1) 建立 OdbcDataAdapter(Select, Connection)；2) 呼叫 Fill(DataSet)；3) 內部以 DataReader 讀取；4) 在 DataSet 內建立/合併 DataTable。核心組件介紹：OdbcDataAdapter、OdbcDataReader、DataTable、DataSet。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q1, D-Q5, B-Q3

Q3: ASP.NET 請求到 DataGrid 綁定的執行流程是什麼？
- A簡: Page_Load 取資料→設定 DataSource→DataBind→輸出 HTML。
- A詳: 技術原理說明：WebForms 生命週期在 Page_Load 取得資料並繫結控制項，於 Render 階段輸出 HTML。關鍵步驟或流程：1) Page_Load 判斷 !IsPostBack（可選）；2) 取數據（ODBC→DataSet）；3) DataGrid.DataSource=DataTable；4) DataBind；5) Page Render。核心組件介紹：Page、DataGrid、DataBinding、HttpHandler/HttpPipeline。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q21, C-Q1, D-Q5

Q4: 64 位 Windows 上 ODBC 子系統如何區分 32/64 位？
- A簡: 透過 WOW64 隔離兩套驅動、DSN 與管理工具，互不交錯。
- A詳: 技術原理說明：x64 上同時提供 32/64 位 ODBC 子系統，檔案與登錄採重新導向。關鍵步驟或流程：1) 32 位程式載入 32 位 ODBC 驅動；2) 64 位程式載入 64 位驅動；3) 各用對應的 ODBC 管理工具維護 DSN。核心組件介紹：WOW64 相容層、odbc32.dll（不同位元）、ODBC 管理工具（System32/SysWOW64）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q10, B-Q25, D-Q3

Q5: 為何 64 位進程無法載入 32 位 ODBC 驅動？
- A簡: 受 OS 載入器與 ABI 限制，DLL 位元數必須與進程一致。
- A詳: 技術原理說明：Windows Loader 依進程 PE 標頭（32/64）解析匯入表與記憶體對映，位址寬度與呼叫慣例須一致。關鍵步驟或流程：1) 進程啟動載入核心 DLL；2) 解析依賴的 ODBC 驅動；3) 若位元不同則載入失敗。核心組件介紹：PE 檔頭、Windows Loader、w3wp.exe、ODBC 驅動 DLL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q2, D-Q9, B-Q4

Q6: Visual Studio 開發伺服器與 IIS 的執行架構差異？
- A簡: 開發伺服器常為 32 位獨立進程；IIS 用 w3wp 集區，位元可不同。
- A詳: 技術原理說明：VS 開發伺服器（或 Cassini/IIS Express）以使用者模式獨立進程執行，多為 32 位；IIS 以應用程式集區（w3wp）承載，位元數由集區或全域設定決定。關鍵步驟或流程：1) 開發時本機 32 位執行；2) 部署到伺服器由 AppPool 承載；3) 若位元不符導致驅動問題。核心組件介紹：Dev Server、IIS AppPool、w3wp。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q7, C-Q3, D-Q2

Q7: IIS6 切換 32 位模式的機制與步驟為何？
- A簡: 透過 adsutil 設 Enable32bitAppOnWin64=1，並註冊 32 位 ASP.NET。
- A詳: 技術原理說明：IIS6 以全域旗標控制 w3svc 進程位元數。關鍵步驟或流程：1) cscript ...adsutil.vbs SET W3SVC/AppPools/Enable32bitAppOnWin64 1；2) 以 %windir%\Microsoft.NET\Framework\...aspnet_regiis.exe -i 註冊 32 位 ASP.NET 2.0；3) 在 IIS 管理中允許對應 Web Service Extension。核心組件介紹：adsutil.vbs、aspnet_regiis、w3svc。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q4, A-Q12, A-Q19

Q8: IIS7 如何同機支援 32 與 64 位應用？
- A簡: 以應用程式集區隔離，針對每個集區獨立設定 32 位開關。
- A詳: 技術原理說明：IIS7 引入更細緻的集區層級設定，每個 AppPool 皆有 Enable 32-Bit Applications 屬性。關鍵步驟或流程：1) 建立兩個集區（32/64 位）；2) 各網站/應用指派對應集區；3) 驅動與元件依集區位元載入。核心組件介紹：AppPool、w3wp、appcmd/applicationHost.config 設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q10, A-Q16, A-Q20

Q9: ODBC DSN 在系統中的儲存與分流機制是什麼？
- A簡: 32/64 位 DSN 分別儲存於各自登錄分支，互不可見。
- A詳: 技術原理說明：ODBC DSN 設定寫入登錄檔，64 位在 HKLM\Software\ODBC；32 位在 HKLM\Software\WOW6432Node\ODBC。關鍵步驟或流程：1) 透過對應 ODBC 管理工具建立 DSN；2) 儲存到對應登錄分支；3) 相同名稱在兩側互不影響。核心組件介紹：登錄檔、ODBC 管理工具、WOW6432Node。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q10, B-Q25, D-Q3, C-Q4

Q10: 如何驗證伺服器是否具備所需 ODBC 驅動？
- A簡: 用正確位元 ODBC 管理工具檢查驅動清單並以測試程式驗證。
- A詳: 技術原理說明：以對應位元工具檢查驅動是否存在，並用同位元程式測試。關鍵步驟或流程：1) 啟動 32/64 位 ODBC 管理工具；2) 檢視 Drivers 分頁；3) 建立 DSN 並測試；4) 用簡單範例應用或 Excel 驗證。核心組件介紹：ODBC 管理工具、測試應用（如 ODBCTest/Excel）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, C-Q4, D-Q1, D-Q3

Q11: ASP.NET 與 COM/ActiveX 的相容性機制為何？
- A簡: In-process 載入需位元相容；若不相容需改為 32 位執行或替代。
- A詳: 技術原理說明：ASP.NET 應用（w3wp）在同進程載入 COM/ActiveX DLL，位元須一致。關鍵步驟或流程：1) 確認 COM 位元；2) 設定 AppPool 位元或註冊相同位元版本；3) 測試載入。核心組件介紹：w3wp、COM Runtime、Regsvr32（不同位元）、AppPool 位元設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q4, C-Q8, B-Q5

Q12: Excel 與 ODBC 的互動原理，為何 Excel 能用而網站不行？
- A簡: Excel 多為 32 位程式，能載入 32 位驅動；網站若在 64 位則不相容。
- A詳: 技術原理說明：Excel（常見為 32 位）藉由 ODBC 連到 CSV/資料庫，載入 32 位驅動。關鍵步驟或流程：1) Excel 建立 ODBC 連線；2) 載入 32 位驅動顯示資料；3) 網站若為 64 位，則找不到 64 位對應驅動。核心組件介紹：Excel ODBC、ODBC 驅動、應用進程位元。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, D-Q9, B-Q10, A-Q20

Q13: 以 ODBC 讀 CSV 與純文字解析的技術比較？
- A簡: ODBC 快速方便有 SQL；純解析部署簡單無依賴，各有取捨。
- A詳: 技術原理說明：ODBC 倚賴驅動解析與查詢；純解析以程式碼自行剖析。關鍵步驟或流程：ODBC：連線→查詢→繫結；純解析：讀檔→解析→建表。核心組件介紹：ODBC 驅動、DataAdapter vs File IO、字串/正則解析。權衡：ODBC 上手快、查詢力道強；純解析可避相依、跨平台，可控性高。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q7, D-Q6, A-Q22

Q14: 安全性：使用 App_Data 與 ODBC Text Driver 有何影響？
- A簡: App_Data 預設不可被直接下載，較安全；ODBC 讀取需權限。
- A詳: 技術原理說明：ASP.NET 會阻擋對 App_Data 的直接 HTTP 存取，保護資料檔。關鍵步驟或流程：1) 將 CSV 放在 App_Data；2) 以 Server.MapPath 指向 DBQ；3) 確保 AppPool 帳號具檔案讀取權。核心組件介紹：ASP.NET 要求篩選、檔案系統 ACL、AppPool 身份。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, D-Q7, B-Q21

Q15: 連線字串的構成（Driver、DBQ）如何解析？
- A簡: Driver 指驅動名稱；DBQ 指資料夾路徑；SQL 指檔案表名。
- A詳: 技術原理說明：ODBC 連線字串包含 Driver={Microsoft Text Driver (*.txt; *.csv)} 與 DBQ=實體資料夾。關鍵步驟或流程：1) 以 Server.MapPath 取得實體路徑；2) 驗證路徑存在；3) 在 SQL 用 [filename] 指定表。核心組件介紹：OdbcConnectionStringBuilder、Server.MapPath、Text Driver 引擎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, B-Q1, C-Q2, D-Q5

Q16: SQL 查詢語法對 CSV 有哪些注意事項？
- A簡: 表名用中括號含副檔名；欄名以標頭；子集語法有限制。
- A詳: 技術原理說明：Text Driver 支援基本 SELECT、WHERE 等，但不支援完整 SQL。關鍵步驟或流程：1) SELECT * FROM [file.txt]；2) 欄位名取自首列；3) 需配合簡單條件；4) 特殊字元以中括號轉義。核心組件介紹：OdbcCommand、SQL Parser（Text Driver）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q2, D-Q5, A-Q23

Q17: OdbcConnection/OdbcDataAdapter 的例外處理與資源釋放原理？
- A簡: 用 using 自動釋放，try/catch 捕捉連線與查詢錯誤。
- A詳: 技術原理說明：IDisposable 模式確保連線釋放，例外需捕捉處理。關鍵步驟或流程：1) using(OdbcConnection) 開啟連線；2) using(OdbcDataAdapter) 執行 Fill；3) try/catch 記錄 OdbcException；4) finally 清理資源。核心組件介紹：IDisposable、OdbcException、Logging（EventLog/Trace）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, D-Q1, D-Q5, B-Q2

Q18: 資料繫結生命週期與避免重複繫結的原理？
- A簡: 使用 !IsPostBack 避免每次回傳重綁，維持狀態與效能。
- A詳: 技術原理說明：WebForms 於 PostBack 會重跑 Page_Load，若每次都 DataBind 會覆蓋使用者狀態。關鍵步驟或流程：1) Page_Load 判斷 !IsPostBack 才載入與繫結初始資料；2) 事件中再依需要更新；3) 減少不必要的資料存取。核心組件介紹：Page.IsPostBack、ViewState、DataBinding。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, D-Q5, B-Q3, A-Q21

Q19: 如何偵測 64 位驅動缺失並找替代方案？
- A簡: 檢查驅動清單與錯誤，選擇安裝 64 位版或改 32 位執行。
- A詳: 技術原理說明：從例外訊息與 ODBC 管理工具判斷驅動是否存在。關鍵步驟或流程：1) 讀錯誤與事件檢視器；2) 用 64 位 ODBC 工具看 Text Driver 是否存在；3) 若無，改用 32 位 AppPool 或純解析；4) 長期安裝或更換驅動。核心組件介紹：ODBC 工具、IIS 位元設定、替代解析器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2, A-Q20, C-Q7

Q20: 建置組態（AnyCPU/x86/x64）與主機位元的互動原理？
- A簡: AnyCPU 隨主機；x86 強制 32 位；x64 強制 64 位，須與宿主一致。
- A詳: 技術原理說明：.NET 組件標記 PlatformTarget 影響 JIT 與載入機制。關鍵步驟或流程：1) WebForms 由 w3wp 位元決定；2) Library 設為 AnyCPU 通用；3) 若需載入 32 位元件，Web 主機須為 32 位。核心組件介紹：PlatformTarget、w3wp 位元、JIT Compiler。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q5, D-Q4, B-Q6

Q21: Server.MapPath 在連線 DBQ 中扮演什麼角色？
- A簡: 將虛擬路徑轉成實體檔案系統路徑，供驅動讀取。
- A詳: 技術原理說明：MapPath 解析相對/虛擬路徑為伺服器實體路徑。關鍵步驟或流程：1) Server.MapPath("~/App_Data")；2) 將結果拼入 DBQ；3) 驅動存取檔案系統。核心組件介紹：HttpServerUtility(MapPath)、ODBC 連線字串、檔案系統 ACL。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q7, A-Q22, B-Q14

Q22: 如何盤點相依元件與位元數，避免部署踩雷？
- A簡: 列舉驅動與 COM 清單，確認位元版本，規劃執行環境。
- A詳: 技術原理說明：相依盤點透過工具與文件確認元件位元與版本。關鍵步驟或流程：1) 列出用到的 ODBC/OleDb/COM；2) 檢查 32/64 位可用性；3) 在目標機測試；4) 擬定切換或替代方案。核心組件介紹：ODBC 管理工具、依賴掃描工具、部署清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q4, C-Q8, B-Q19

Q23: ODBC Text Driver 的效能與限制考量？
- A簡: 適合小中型檔案與簡易查詢；大型資料與複雜語法受限。
- A詳: 技術原理說明：驅動逐行解析文字，缺少索引與強型別優化。關鍵步驟或流程：1) 控制檔案大小與欄位複雜度；2) 只取所需欄位；3) 可用快取減少重複解析。核心組件介紹：Text Parser、OdbcDataAdapter、應用層快取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q5, A-Q14, B-Q16

Q24: 如何記錄 ODBC 連線錯誤以利診斷？
- A簡: 捕捉 OdbcException，記錄 SQLState/Message/Stack 與環境資訊。
- A詳: 技術原理說明：OdbcException 提供 SQLState 與錯誤訊息。關鍵步驟或流程：1) try/catch(OdbcException ex)；2) 記錄 ex.Errors 詳細內容；3) 併記錄進程位元（Environment.Is64BitProcess）與連線字串要點；4) 送交事件檢視器或日誌系統。核心組件介紹：OdbcException、Logging、EventLog。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q1, D-Q2, B-Q17

Q25: 如何正確啟動 32 位 ODBC 管理工具？
- A簡: 於 SysWOW64 啟動 32 位版本，檢視與建立 32 位 DSN/驅動。
- A詳: 技術原理說明：SysWOW64 存放 32 位系統工具。關鍵步驟或流程：1) 執行 C:\Windows\SysWOW64\odbcad32.exe（或相應控制台項）；2) 檢視 Drivers/DSN；3) 建立並測試；4) 與 64 位版本分開使用。核心組件介紹：odbcad32.exe（32/64 位）、WOW64 檔案重導向。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, A-Q10, C-Q4, D-Q3

Q26: 為何 IIS6 的 32 位切換有副作用？如何權衡？
- A簡: 全域切換影響所有網站相依；可分流、升級 IIS7 或獨立機器。
- A詳: 技術原理說明：IIS6 以全域旗標控制 w3wp 位元，所有網站共用。關鍵步驟或流程：1) 需求評估（哪些網站需 64 位）；2) 若切 32 位，測試影響；3) 規劃分流或升級 IIS7，以 AppPool 隔離；4) 長期導入 64 位元件。核心組件介紹：Enable32bitAppOnWin64、AppPool、部署拓撲。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, A-Q20, C-Q5, D-Q4

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何建立一個以 ODBC 讀取 CSV 並顯示於 DataGrid 的 WebForms 頁面？
- A簡: 新增 WebForms，於 Page_Load 連 ODBC Text Driver 取數據並 DataBind。
- A詳: 具體實作步驟：1) 建立 WebForms 專案與 Default.aspx；2) 放置 <asp:DataGrid ID="DataGrid1" runat="server" />；3) Page_Load 中連線並綁定。關鍵程式碼片段或設定：
  using (var conn=new OdbcConnection("Driver={Microsoft Text Driver (*.txt; *.csv)};DBQ=" + Server.MapPath("~/App_Data")))
  using (var ad=new OdbcDataAdapter("select * from [database.txt]", conn)){
    var ds=new DataSet(); ad.Fill(ds);
    DataGrid1.DataSource=ds.Tables[0]; DataGrid1.DataBind();
  }
注意事項與最佳實踐：加上 !IsPostBack；確保 App_Data 權限與檔名正確。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2, B-Q3, D-Q5

Q2: 如何撰寫正確的 ODBC Text Driver 連線字串與查詢？
- A簡: Driver 指 Text Driver；DBQ 指資料夾；SQL 用 [檔名] 作表名。
- A詳: 具體實作步驟：1) var path=Server.MapPath("~/App_Data"); 2) 建字串："Driver={Microsoft Text Driver (*.txt; *.csv)};DBQ="+path; 3) SQL："SELECT * FROM [database.txt]"; 關鍵程式碼片段或設定：使用 OdbcConnection/OdbcDataAdapter。注意事項與最佳實踐：確認 DBQ 路徑存在；檔名含副檔名；特殊路徑避免引號錯誤；必要時檢查檔案編碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, B-Q1, B-Q15, D-Q5

Q3: 在 IIS6 上如何切換至 32 位模式以使用 32 位 ODBC 驅動？
- A簡: 用 adsutil 設 Enable32bitAppOnWin64=1，並註冊 32 位 ASP.NET。
- A詳: 具體實作步驟：1) 以系統管理員開 cmd；2) 執行：cscript %SYSTEMDRIVE%\inetpub\adminscripts\adsutil.vbs SET W3SVC/AppPools/Enable32bitAppOnWin64 1；3) 註冊 32 位 ASP.NET：%SYSTEMROOT%\Microsoft.NET\Framework\v2.0.40607\aspnet_regiis.exe -i；4) IIS 管理將對應 Web Service Extension 設 Allowed。注意事項與最佳實踐：切換為全域影響；先盤點其他 64 位網站。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, B-Q7, D-Q4

Q4: 如何使用 32 位 ODBC 管理工具建立與測試 DSN？
- A簡: 從 SysWOW64 啟動 32 位工具，建立 DSN 並測試讀取 CSV 路徑。
- A詳: 具體實作步驟：1) 執行 C:\Windows\SysWOW64\odbcad32.exe；2) 至 Drivers 確認 Microsoft Text Driver 存在；3) 新增系統 DSN，選 Text Driver；4) 指定資料夾路徑與檔案；5) 測試連線。關鍵設定：路徑需為實體路徑。注意事項與最佳實踐：勿用 64 位工具建立 32 位 DSN；名稱清楚標示位元數。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q10, B-Q25, D-Q3

Q5: 在 IIS7 如何設定特定應用程式集區為 32 位？
- A簡: 建立或編輯 AppPool，啟用 Enable 32-Bit Applications=True。
- A詳: 具體實作步驟：1) IIS 管理器→應用程式集區；2) 新建集區或選擇目標；3) 進階設定→Enable 32-Bit Applications=True；4) 將網站/應用指派到該集區；5) 回收集區。關鍵設定：確保對應驅動存在。注意事項與最佳實踐：僅對需 32 位相依的應用使用，其他維持 64 位以確保資源利用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q8, D-Q10, A-Q20

Q6: 如何為 ODBC 操作加入健全的錯誤處理與日誌？
- A簡: 使用 using/try-catch，捕捉 OdbcException，記錄詳細資訊。
- A詳: 具體實作步驟：1) using 包裝 Connection/Adapter；2) try/catch(OdbcException ex)；3) 記錄 ex.Message、SQLState、Stack、Environment.Is64BitProcess；4) 顯示友善訊息。關鍵程式碼片段或設定：使用 ILogger 或 EventLog。注意事項與最佳實踐：勿回傳內部細節給前端；保留足夠診斷資訊。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q17, B-Q24, D-Q1, D-Q2

Q7: 如何改寫為不用 ODBC 的純 .NET CSV 解析？
- A簡: 以 File.ReadLines 讀檔，Split 解析欄位，組 DataTable 繫結。
- A詳: 具體實作步驟：1) 讀取檔案：var lines=File.ReadLines(Server.MapPath("~/App_Data/database.txt")); 2) 第一行作欄名；3) 逐行 Split(',') 建 DataTable Rows；4) 綁定 DataGrid。關鍵程式碼片段或設定：注意逗號轉義/引號，必要時採用成熟解析器。注意事項與最佳實踐：處理編碼與例外；大型檔案分批讀取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13, D-Q6, B-Q23

Q8: 如何上傳 Excel 並於 32 位模式讀取其內容？
- A簡: 啟用 32 位 AppPool，使用對應 Provider，讀取後轉為 DataTable。
- A詳: 具體實作步驟：1) 建檔案上傳；2) 將 AppPool 設 32 位；3) 以 32 位 Provider（如對應版本）建立連線字串；4) SELECT 讀取工作表；5) 繫結顯示。關鍵程式碼片段或設定：Provider/Extended Properties 正確；注意權限。注意事項與最佳實踐：留意驅動授權與安裝；檔案放 App_Data；清理暫存檔。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q11, D-Q9, A-Q20

Q9: 如何在程式中自動偵測執行位元並提示相依問題？
- A簡: 用 Environment.Is64BitProcess 判斷，提示需 32/64 位驅動。
- A詳: 具體實作步驟：1) bool is64=Environment.Is64BitProcess；2) 若需 32 位驅動而 is64 為真，提示切換 AppPool 或安裝 64 位驅動；3) 記錄診斷資訊。關鍵程式碼片段或設定：條件檢查於啟動或連線前。注意事項與最佳實踐：勿阻斷流程，提供指引連結與運維資訊。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q20, D-Q2, D-Q4

Q10: 如何在 web.config 啟用診斷以輔助 ODBC 問題排查？
- A簡: 暫時關閉自訂錯誤，顯示詳細錯誤，搭配日誌記錄。
- A詳: 具體實作步驟：1) web.config 設 <customErrors mode="Off" />（僅限內部或暫時）；2) 啟用 tracing 或 EL；3) 於程式捕捉 OdbcException 與環境資訊。關鍵設定：IIS 自訂錯誤、Failed Request Tracing。注意事項與最佳實踐：生產環境勿長期關閉；敏感資訊遮蔽。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q24, C-Q6, D-Q1, D-Q2

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 在 x64 IIS 上 CSV 讀取失敗，疑似找不到 ODBC 驅動怎麼辦？
- A簡: 確認使用正確位元 ODBC 工具檢查驅動，必要時切 32 位或裝 64 位。
- A詳: 問題症狀描述：網站拋出 ODBC 連線/驅動錯誤，無法讀取 CSV。可能原因分析：伺服器以 64 位執行但缺少 64 位 Text Driver；或誤用 64 位 ODBC 工具檢查 32 位驅動。解決步驟：1) 以 SysWOW64\odbc 工具檢查 32 位驅動；2) 決定安裝 64 位驅動或切 IIS 至 32 位；3) 測試簡單程式驗證。預防措施：部署前盤點驅動與位元，建立測試 DSN。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q3, C-Q4, A-Q24

Q2: 在 VS 可跑、IIS 失敗的位元不相容問題如何診斷與解決？
- A簡: 比對進程位元與驅動位元，改 AppPool 位元或更換驅動。
- A詳: 問題症狀描述：本機開發正常，部署 IIS 後報連線/驅動錯誤。可能原因分析：Dev 伺服器多為 32 位，IIS 為 64 位，導致載入錯誤。解決步驟：1) 確認 Environment.Is64BitProcess；2) 查 ODBC 驅動清單；3) 切 IIS6 至 32 位或 IIS7 設 32 位集區；4) 測試。預防措施：建立與生產一致的測試環境；CI 驗證位元相依。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q6, C-Q3, C-Q5

Q3: ODBC 管理工具中看不到預期的驅動或 DSN，如何處理？
- A簡: 確認啟動正確位元版本的 ODBC 工具，於對應版本建立/檢查。
- A詳: 問題症狀描述：Drivers 清單很少或 DSN 消失。可能原因分析：啟動了錯誤位元的 ODBC 管理工具。解決步驟：1) 執行 SysWOW64\odbcad32.exe 以檢視 32 位；2) 使用 System32 版本看 64 位；3) 在對應版本建立 DSN；4) 測試連線。預防措施：建立捷徑並標註位元，避免混淆。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q25, C-Q4, B-Q9

Q4: 切換 IIS6 至 32 位後其他網站出問題，怎麼辦？
- A簡: 用獨立伺服器或升級 IIS7 以集區隔離，或還原 64 位並重構。
- A詳: 問題症狀描述：切 32 位後部分網站功能失效（需 64 位）。可能原因分析：IIS6 全域切換影響所有應用。解決步驟：1) 還原 64 位設定；2) 規劃分流/獨立機器；3) 升級 IIS7 並分配 32/64 位集區；4) 逐步替換 64 位相依。預防措施：切換前完成相依盤點與整機測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, B-Q7, B-Q26, C-Q5

Q5: DataGrid 不顯示資料或拋例外，如何診斷？
- A簡: 檢查 DBQ 路徑、檔名中括號、欄名/首列與權限與例外訊息。
- A詳: 問題症狀描述：頁面空白、錯誤或欄位對不到。可能原因分析：DBQ 錯路徑、檔名未加副檔名、非首列標頭、無讀取權限。解決步驟：1) 記錄例外內容；2) 確認 Server.MapPath 與檔案存在；3) SELECT * FROM [file.txt]；4) 檢視首列欄名；5) 設定 App_Data 權限。預防措施：加單元測試與啟動檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q16, C-Q1, C-Q2

Q6: CSV 出現亂碼或分隔解析錯誤，如何處理？
- A簡: 確認檔案編碼與分隔規則；必要時改用自訂解析。
- A詳: 問題症狀描述：中文亂碼、欄位錯位。可能原因分析：Text Driver 對編碼/引號/分隔支援有限。解決步驟：1) 轉檔為合適編碼（如 UTF-8 with BOM/ANSI）試驗；2) 確保一致的分隔與引用；3) 若仍不穩定，改用純 .NET 解析。預防措施：規範資料交換格式並訂定測試用例。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13, C-Q7, B-Q23

Q7: 權限不足導致無法讀取 App_Data 檔案怎麼辦？
- A簡: 調整應用程式集區身分對目錄授權讀取，確認路徑正確。
- A詳: 問題症狀描述：IO/存取被拒，或 ODBC 無法打開檔。可能原因分析：AppPool 帳號無資料夾讀取權限；路徑錯誤。解決步驟：1) 確認 AppPool Identity；2) 賦予 App_Data 讀取權；3) 檢查 Server.MapPath；4) 重新測試。預防措施：部署腳本附帶 ACL 設定，最小權限原則。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q1, C-Q2, A-Q24

Q8: 找不到 32 位 ODBC 管理工具路徑時怎麼辦？
- A簡: 至 C:\Windows\SysWOW64 尋找 odbcad32.exe，建立捷徑備用。
- A詳: 問題症狀描述：控制台無法開到正確 ODBC 工具。可能原因分析：混淆 System32 與 SysWOW64；捷徑指錯。解決步驟：1) 直接執行 C:\Windows\SysWOW64\odbcad32.exe；2) 建立明確名為「ODBC 32 位」捷徑；3) 記錄 SOP。預防措施：文件化環境操作，避免人員流失造成知識斷層。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q25, C-Q4, B-Q4

Q9: Excel 能連 ODBC，網站卻不行，該如何解？
- A簡: 比對兩者進程位元，網站改 32 位或安裝 64 位驅動。
- A詳: 問題症狀描述：Excel 成功查詢 CSV，網站報錯。可能原因分析：Excel 為 32 位，網站在 64 位 AppPool 上，驅動不相容。解決步驟：1) 確認 Excel 與 w3wp 位元；2) 檢查驅動清單；3) 將網站集區改 32 位或安裝 64 位驅動；4) 測試。預防措施：制定跨系統驅動與位元一致性策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q12, C-Q5, C-Q3

Q10: 部署到 IIS7 仍有位元衝突，如何排除？
- A簡: 為應用程式設定 32 位集區，驗證驅動版本並隔離其他網站。
- A詳: 問題症狀描述：IIS7 上 ODBC 仍報驅動不相容。可能原因分析：AppPool 仍為 64 位或驅動缺失。解決步驟：1) 啟用 Enable 32-Bit Applications；2) 確認 32 位驅動存在；3) 影響範圍僅限該集區；4) 測試與監控。預防措施：標準化部署腳本與檢查清單，確保集區與驅動正確。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q8, C-Q5, A-Q20

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 ODBC？它的用途是什麼？
    - A-Q2: 什麼是 Microsoft Text Driver（*.txt; *.csv）？
    - A-Q3: 在 ASP.NET 中用 ODBC 讀取 CSV 的基本流程是什麼？
    - A-Q4: DataSet、DataAdapter、DataGrid 各自扮演什麼角色？
    - A-Q5: 什麼是 x64 與 x86？與程式執行有何關聯？
    - A-Q8: 什麼是 ODBC Data Source Administrator？
    - A-Q9: 為什麼 64 位 Windows 會有兩個 ODBC 管理工具？
    - A-Q10: 32 位與 64 位 ODBC DSN 有何差異？
    - A-Q21: 什麼是 ASP.NET WebForms 的 DataGrid？
    - A-Q22: 為什麼連線字串使用 DBQ 指向資料夾而非檔案？
    - B-Q1: ODBC Text Driver 讀取 CSV 的運作原理是什麼？
    - B-Q2: OdbcDataAdapter.Fill 如何將 CSV 結果放入 DataSet？
    - C-Q1: 如何建立以 ODBC 讀取 CSV 的 WebForms 頁面？
    - C-Q2: 如何撰寫正確的 ODBC Text Driver 連線字串與查詢？
    - D-Q5: DataGrid 不顯示資料或拋例外，如何診斷？

- 中級者：建議學習哪 20 題
    - A-Q6: 為什麼 64 與 32 位程式不能在同一進程中混用？
    - A-Q11: 為何在 IIS6 x64 上無法同時執行 x86 與 x64 Web 應用？
    - A-Q12: ASP.NET 1.1 與 2.0 在 x64 上的支援差異是什麼？
    - A-Q13: 為什麼 VS 可運作、IIS 失敗？
    - A-Q14: 為什麼讀取 CSV 可改用純文字解析？
    - A-Q16: IIS6 與 IIS7 在位元數支援的差異是什麼？
    - B-Q3: ASP.NET 請求到 DataGrid 綁定的執行流程是什麼？
    - B-Q4: 64 位 Windows 上 ODBC 子系統如何區分 32/64 位？
    - B-Q5: 為何 64 位進程無法載入 32 位 ODBC 驅動？
    - B-Q6: 開發伺服器與 IIS 的執行架構差異？
    - B-Q7: IIS6 切換 32 位模式機制與步驟
    - B-Q8: IIS7 如何同機支援 32 與 64 位應用？
    - B-Q15: 連線字串的構成解析
    - B-Q16: SQL 查詢語法對 CSV 的注意事項
    - B-Q17: Odbc 例外處理與資源釋放原理
    - C-Q3: 在 IIS6 上如何切換至 32 位模式？
    - C-Q4: 如何使用 32 位 ODBC 管理工具建立與測試 DSN？
    - C-Q6: 如何加入錯誤處理與日誌？
    - D-Q1: x64 IIS 上 CSV 讀取失敗怎麼辦？
    - D-Q2: VS 可跑、IIS 失敗的位元不相容如何解？

- 高級者：建議關注哪 15 題
    - A-Q18: 為什麼要關注 in-process 元件位元數？
    - A-Q19: 切換 IIS6 至 32 位模式的核心價值是什麼？
    - A-Q20: 何時裝 64 位驅動，何時改 32 位執行？
    - A-Q23: CSV 欄位如何對映為資料表欄位？
    - B-Q9: ODBC DSN 的儲存與分流機制
    - B-Q19: 偵測 64 位驅動缺失與替代方案
    - B-Q20: 建置組態與主機位元互動
    - B-Q22: 相依元件盤點方法
    - B-Q23: ODBC Text Driver 效能與限制
    - B-Q24: 如何記錄 ODBC 錯誤以利診斷
    - B-Q26: 為何 IIS6 的 32 位切換有副作用？如何權衡？
    - C-Q5: 在 IIS7 設定 32 位集區
    - C-Q7: 改為不用 ODBC 的純 .NET CSV 解析
    - C-Q8: 上傳 Excel 並於 32 位模式讀取
    - D-Q4: 切到 32 位後其他網站出問題怎解？