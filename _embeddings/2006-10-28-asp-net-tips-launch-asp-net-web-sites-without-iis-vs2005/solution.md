# ASP.NET Tips: Launch ASP.NET Web Sites without IIS / VS2005  

# 問題／解決方案 (Problem/Solution)

## Problem: 想快速試跑 ASP.NET 範例專案，卻必須安裝 IIS 或啟動笨重的 Visual Studio

**Problem**:  
• 情境：開發者收到一個 ASP.NET 範例（例如 NUnitLite 在 Web Application 上的示範），  
• 需求：只想確認程式能否順利執行、稍作測試。  
• 困難：  
  1. 若走「IIS 部署」路徑，需要先在本機安裝/設定 IIS，手動建立虛擬目錄、設定埠號，非常耗時。  
  2. 若走「Visual Studio 2005」路徑，VS 啟動時間長，對於筆電或資源有限的機器尤為惱人，常因「懶得開 VS」而放棄嘗試範例。  

**Root Cause**:  
• ASP.NET 專案傳統上仰賴 IIS 或 VS 所內建的 Dev Web Server 才能啟動。  
• 使用者對「一鍵啟動」的需求與「現有工具啟動耗時、設定繁瑣」之間存在落差。  
• 缺乏一種「與專案目錄鬆耦合」「不需 GUI、不需預先設定」的輕量啟動機制。  

**Solution**:  
1. 利用 .NET 2.0 隨附的 `WebDev.WebServer.EXE`（VS2005 同捆的 Development Web Server）直接啟動站台。  
2. 撰寫下列批次檔，並將其捷徑放入 `C:\Documents and Settings\<UserName>\SendTo\`，即可在檔案總管→右鍵→傳送到，一鍵啟動。  

```batch
:: DevAspNetWeb.bat
set DEVWEB_PORT=%random%
start /min /low "DevWebServer" ^
  "C:\Windows\Microsoft.NET\Framework\v2.0.50727\WebDev.WebServer.EXE" ^
  /path:%1 /port:%DEVWEB_PORT%
start "" "http://localhost:%DEVWEB_PORT%/"
set DEVWEB_PORT=
```

關鍵思考點：  
• `WebDev.WebServer.EXE` 本質上就是 VS2005 背後呼叫的內建伺服器，直接使用可省下啟動 VS 的額外開銷。  
• 以 `%random%` 產生動態埠，避免與系統既有服務衝突。  
• 透過「SendTo→目錄」的 UX，無需任何 IIS 設定或 VS 方案檔即可啟動 Web 站台。  

**Cases 1**: Notebook 上跑 NUnitLite Web 範例  
• 背景：作者在筆電示範 NUnitLite Web 介面。  
• 以往：啟動 VS >30 秒，或手動設定 IIS 3~5 分鐘。  
• 採用批次檔後：  
  - 右鍵→傳送到→Dev ASP.NET Web，3 秒內完成伺服器啟動＋瀏覽器開啟。  
  - 減少至少90% 等待時間，試範例「懶得開 VS」的心理門檻消失。  

**Cases 2**: 提供 Sample Code 給同事／客戶  
• 背景：分享 ASP.NET Demo Zip 檔。  
• 過去：附加一張 README 說明「先安裝 IIS 或用 VS 開啟」。  
• 現在：只需附上 `DevAspNetWeb.bat`＋一句話：「解壓後右鍵資料夾→SendTo→Dev ASP.NET Web」。  
• 結果：  
  - 收到程式的同事不需要任何預先環境設定就能立即打開瀏覽器觀看效果。  
  - 減少「環境建置問題」回報，讓焦點回歸於程式本身。  

**Cases 3**: 教學／演講現場 Demo  
• 背景：講者在陌生電腦做 ASP.NET 示範，現場時間寶貴、無權限安裝 IIS。  
• 作法：USB 帶著批次檔，一解壓就能直接啟動範例站台。  
• 成效：  
  - 避免因網路或權限問題導致的 IIS 安裝失敗。  
  - Live Demo 準備時間由數分鐘縮短至數秒，提升教學流暢度。