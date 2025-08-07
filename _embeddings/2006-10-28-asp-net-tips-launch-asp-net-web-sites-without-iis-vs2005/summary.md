# ASP.NET Tips: Launch ASP.NET Web Sites without IIS / VS2005

## 摘要提示
- IIS 依賴: 過去開發 ASP.NET 網站必須先安裝並設定 IIS，流程繁複。  
- VS2005 內建伺服器: Visual Studio 2005 提供 Development Web Server，可免 IIS 執行網站。  
- 啟動成本: 像 Notebook 等效能有限的環境，開啟 VS2005 測試小範例非常耗時。  
- 懶人需求: 作者為了「下載範例 → 立即執行」的便利性，自行撰寫批次檔降低門檻。  
- 批次檔機制: 透過隨機 Port 啟動 WebDev.WebServer.EXE，再自動開啟瀏覽器。  
- SendTo 整合: 將批次檔捷徑放入 Windows 「傳送到」目錄，右鍵即可執行。  
- 操作流程: 解壓範例→檔案總管右鍵資料夾→傳送到 Dev ASP.NET Web→瀏覽器自動啟動。  
- 測試情境: 搭配 NUnitLite 等單元測試範例，可快速驗證 Web 應用。  
- 效率提升: 不需要開啟 VS 或設定 IIS，大幅縮短測試與示範準備時間。  
- 精神總結: 小巧批次檔體現「因懶而生」的開發效率提升技巧。  

## 全文重點
作者指出，傳統 ASP.NET 網站開發與範例測試往往依賴 IIS 或直接在 Visual Studio 2005 中執行，但這兩種方式對機器性能與設定皆有不便，特別是在 Notebook 等較慢的環境下。為了快速檢視像 NUnitLite 之類的 Web 應用範例，他利用 VS2005 內建的 Development Web Server（WebDev.WebServer.EXE），撰寫一支簡單的批次檔。   
批次檔邏輯為：先以 %random% 產生隨機 Port，接著以 /min /low 參數在背景啟動 WebDev.WebServer.EXE，並指定 /path 為使用者所點選的資料夾；待伺服器啟動後，再以 start 指令自動開啟 http://localhost:Port/，最後清除環境變數。   
為了讓此流程更加直覺，他將批次檔的捷徑放入 Windows 使用者目錄下的 SendTo 目錄，命名為「Dev ASP.NET Web」。如此一來，當開發者下載並解壓任何 ASP.NET 範例，只需在檔案總管中右鍵該資料夾、選擇「傳送到 → Dev ASP.NET Web」，系統便會自動啟動內建伺服器與瀏覽器，無須進入 VS、亦不必預先設定 IIS。   
此技巧充分利用了 VS2005 既有功能，配合 Windows 介面小整合，即可達成「零設定、即點即跑」的需求，對於需要頻繁檢視或示範各種 ASP.NET 範例的開發者而言，能顯著節省時間並降低操作門檻。作者最後以「enjoy it :D」收尾，強調這項由「懶」激發出的輕量化開發流程。  

## 段落重點
### 1. 背景與問題
過去開發 ASP.NET 網站若非要安裝並設定 IIS，便得拉開 Visual Studio 2005 執行內建伺服器；對 Notebook 等效能有限的裝置而言，光是啟動 VS2005 就得等待許久，讓人懶得開啟程式來測試一些不甚吸引的小範例。作者以試用 NUnitLite Web 應用範例為例，說明傳統流程的繁瑣與時間成本。

### 2. 解決方案概述
VS2005 已附帶 WebDev.WebServer.EXE，可獨立於 IDE 執行，作者遂萌生「用批次檔一鍵啟動網站」的想法：自動呼叫內建伺服器、使用隨機 Port 避免衝突，再順手開啟瀏覽器，如此即可免去 IIS 設定與 VS 載入時間，實現迅速測試。

### 3. 批次檔內容解析
批次檔程式碼僅數行：設定 DEVWEB_PORT 取 %random%，以 start /min /low 啟動 c:\Windows\Microsoft.NET\Framework\v2.0.50727\WebDev.WebServer.EXE，指定 /path 為 %1 的資料夾路徑，/port 為隨機 Port；接著使用 start 指令打開 http://localhost:%DEVWEB_PORT%/，最後清掉環境變數。整個過程靈活、無副作用且能在背景低優先序執行。

### 4. SendTo 整合與操作流程
為了讓批次檔更易用，作者把它的捷徑放進「C:\Documents and Settings\{使用者}\SendTo」資料夾，命名為「Dev ASP.NET Web」。日後只要：① 解壓下載的範例；② 在檔案總管選中資料夾；③ 右鍵「傳送到→Dev ASP.NET Web」，系統便會背景啟動 Development Web Server，同步開啟瀏覽器至該網站首頁，實現「一鍵即跑」。

### 5. 效益與收尾
此懶人批次檔讓測試 ASP.NET 範例或進行簡易開發不再依賴 IIS，也省去開啟龐大 VS2005 的等待時間，特別適合隨手驗證程式片段、示範單元測試成果，或在受限環境中快速部署。作者以輕鬆口吻鼓勵讀者試用並享受這項小技巧，彰顯「因懶而生」卻能顯著提升效率的開發哲學。