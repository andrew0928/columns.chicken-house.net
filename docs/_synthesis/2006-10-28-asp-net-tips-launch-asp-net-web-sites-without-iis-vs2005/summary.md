---
layout: synthesis
title: "ASP.NET Tips: Launch ASP.NET Web Sites without IIS / VS2005"
synthesis_type: summary
source_post: /2006/10/28/asp-net-tips-launch-asp-net-web-sites-without-iis-vs2005/
redirect_from:
  - /2006/10/28/asp-net-tips-launch-asp-net-web-sites-without-iis-vs2005/summary/
postid: 2006-10-28-asp-net-tips-launch-asp-net-web-sites-without-iis-vs2005
---

# ASP.NET Tips: Launch ASP.NET Web Sites without IIS / VS2005

## 摘要提示
- 無需 IIS: 透過 .NET 內建的 WebDev.WebServer.EXE 即可啟動 ASP.NET 網站，免安裝 IIS。
- 免開 VS2005: 不必啟動 Visual Studio 2005，快速預覽與測試網站。
- 批次檔自動化: 使用簡單批次檔自動啟動開發伺服器與瀏覽器。
- 隨機埠號: 以 %random% 產生隨機埠，避免埠號衝突。
- 右鍵傳送到: 將捷徑放入 SendTo，檔案總管右鍵即可啟動網站。
- 輕量快速: 適合筆電或臨時測試情境，省下啟動大型 IDE 的時間。
- 適用範例程式: 下載的 sample code 解壓後可立即以站台方式啟動瀏覽。
- 低資源消耗: 啟動參數設為最小化與低優先序，減少系統負擔。
- 通用性高: 任何 ASP.NET Web Site 目錄皆可套用相同流程。
- 開發體驗提升: 降低進入門檻，提升試跑與除錯的靈活度。

## 全文重點
文章分享一個輕量級技巧：不需要安裝 IIS，也不必開啟 Visual Studio 2005，即可快速啟動 ASP.NET 網站進行瀏覽與測試。作者指出，VS2005 雖內建開發用的 Web 伺服器（ASP.NET Development Server），但在實務上若只是想快速跑個 sample 或檢查頁面效果，打開 VS2005 仍嫌繁瑣且耗時，尤其在筆電上更明顯。因此作者以「懶人」需求為出發點，提供一個批次檔與「傳送到」捷徑的做法，將啟動流程簡化為檔案總管中的幾次點擊。

具體作法是編寫一個批次檔，核心使用 .NET Framework 2.0 的 WebDev.WebServer.EXE（即 VS2005 隨附的開發用 Web 伺服器）來啟動指定目錄為網站根目錄，並用 %random% 產生隨機埠號，避免與現有服務衝突。批次檔以最小化與低優先序啟動伺服器，接著自動開啟瀏覽器導向 http://localhost:隨機埠，以立即預覽網站。為了讓操作更直覺，作者將該批次檔的捷徑放入 Windows 的「SendTo」資料夾，於是使用者只需在檔案總管中對著網站根目錄按右鍵，選擇「傳送到」對應項目，即可完成啟動。

文章也以實例說明：例如下載 NUnitLite 在 Web Application 的 sample code，解壓縮後直接在資料夾上用「傳送到」啟動，就能立刻在瀏覽器中查看。這種方式不僅省去在 IIS 中建立站台或在 VS 裡建立/開啟 Web Site 的程序，也避免大軟體啟動的等待時間，對於想快速驗證樣本、重現問題、或短暫測試頁面的情境非常合適。總結來說，此技巧以最小成本提供足夠的開發體驗，大幅提高了 ASP.NET 網站快速試跑的效率與便利性。

## 段落重點
### 背景與動機
作者指出在沒有此技巧前，常見的兩種啟動做法是：在 IIS 上設定站台，或用 VS2005 的內建開發伺服器執行。然而這兩者流程都偏重、啟動成本高，特別是在筆電上開 VS2005 常需等待，降低了快速測試 sample code 的意願。因此萌生以更輕便的方式來啟動 ASP.NET 網站的需求，目標是「免 IIS、免開 VS，直接跑」。

### 批次檔內容與原理
核心是呼叫 c:\Windows\Microsoft.NET\Framework\v2.0.50727\WebDev.WebServer.EXE，透過參數 /path 指定網站目錄（由 %1 接收），/port 指定動態埠號（以 %random% 產生，降低衝突風險）。以 start /min /low 啟動可讓伺服器以最小化與低優先序執行，減少對系統資源的影響。伺服器啟動後，批次檔再以 start 開啟瀏覽器，直達 http://localhost:埠號/，完成一鍵啟動與預覽。最後清理環境變數，避免殘留。此流程本質上等同 VS 的開發伺服器行為，但去除了啟動 VS 的負擔。

### 快速啟動的使用步驟
為了讓操作更順手，作者將該批次檔的捷徑放到 C:\Documents and Settings\{使用者}\SendTo。之後只要：
1) 解壓下載的網站或範例程式碼；
2) 在檔案總管找到其根目錄；
3) 右鍵該資料夾，選「傳送到」→ 事先建立的捷徑（如「Dev ASP.NET Web」）。
系統即會自動以開發伺服器啟動該目錄為網站根目錄，同時開啟瀏覽器顯示首頁，達到與 VS F5 類似的即時體驗，卻更輕量快速。

### 效果與結語
此方法非常適合臨時檢視與測試 ASP.NET 專案或範例，省去 IIS 配置與 VS 啟動時間，特別對筆電使用者與快速試跑場景更有感。透過隨機埠避免衝突、最小化與低優先序降低資源占用，整體體驗流暢。雖然只是小技巧，卻有效提升開發效率與靈活度，讓開發者能更專注於驗證與問題重現。作者以「enjoy it」作結，鼓勵讀者實際套用這個簡便流程。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本的 ASP.NET Web Site 概念（檔案夾即網站、以檔案系統為根目錄）
   - Windows 批次檔與命令列基礎（環境變數、start 指令）
   - .NET Framework 2.0 與內建 ASP.NET Development Server（WebDev.WebServer.EXE）
   - Windows 檔案總管 SendTo 功能與捷徑操作

2. 雙心概念：
   - 使用 ASP.NET Development Server（WebDev.WebServer.EXE）取代 IIS/VS2005 直接啟動網站
   - 以批次檔自動化：動態指定隨機連接埠、最小化啟動伺服器並自動開啟瀏覽器
   - SendTo 整合：在資料夾上右鍵「傳送到」快速啟動網站
   - 輕量開發/測試流程：無需啟動 VS 或設定 IIS，即可快速預覽範例或小型網站

3. 技術依賴：
   - WebDev.WebServer.EXE（路徑：c:\Windows\Microsoft.NET\Framework\v2.0.50727\）
   - .NET Framework 2.0（提供開發伺服器）
   - Windows 命令解譯器（批次檔、環境變數 %random%）
   - 預設瀏覽器（以 http://localhost:<port>/ 開啟）

4. 應用場景：
   - 下載的 ASP.NET 範例專案快速試跑
   - 在筆電/環境受限時不安裝或設定 IIS
   - 不啟動 Visual Studio 的輕量測試與預覽
   - 臨時展示或檢查小型 WebSite 型專案

### 學習路徑建議
1. 入門者路徑：
   - 確認已安裝 .NET Framework 2.0
   - 找到 WebDev.WebServer.EXE 的實際路徑
   - 複製文章批次檔內容為 .bat 檔並以實際路徑調整
   - 將批次檔捷徑放入 C:\Documents and Settings\{帳號}\SendTo
   - 在任意 ASP.NET WebSite 根目錄上右鍵「傳送到」→ 選擇該捷徑啟動

2. 進階者路徑：
   - 自訂固定連接埠、網站虛擬目錄、錯誤頁面與日誌輸出
   - 在批次檔加入參數檢查、錯誤處理（例如檢查目錄是否存在）
   - 建立多個 SendTo 快捷以支援不同 .NET 版本/不同啟動模式
   - 了解與 IIS 行為差異（管線、模組、權限）

3. 實戰路徑：
   - 將此啟動器納入團隊共享工具，快速驗收下載的範例或 Issue 附檔
   - 結合原始碼管控（如在 repo 提供 run.bat）降低新成員上手成本
   - 為特定專案編寫針對性啟動腳本（指定起始頁、靜態檔快取關閉等）

### 關鍵要點清單
- WebDev.WebServer.EXE 路徑：ASP.NET 開發伺服器可在 .NET Framework v2.0.50727 目錄下找到 (優先級: 高)
- /path 參數：指定要啟動為網站根目錄的檔案夾 (優先級: 高)
- /port 參數：指定伺服器監聽連接埠，避免衝突可用隨機值 (優先級: 高)
- %random% 使用：以環境變數快速生成隨機連接埠（簡便但不保證不衝突） (優先級: 中)
- start 指令：啟動程式或 URL，支援同時開啟瀏覽器 (優先級: 中)
- start /min /low：最小化且低優先序啟動，降低打擾與資源占用 (優先級: 低)
- SendTo 整合：將批次檔捷徑放入 SendTo，右鍵資料夾即可一鍵啟動網站 (優先級: 高)
- 批次檔變數清理：啟動後清空臨時環境變數，保持整潔 (優先級: 低)
- 無需 IIS/VS：對於快速測試與範例驗證更輕量省時 (優先級: 高)
- 環境需求：需安裝 .NET Framework 2.0，且目錄權限允許執行 (優先級: 中)
- 瀏覽器自動開啟：以 http://localhost:<port>/ 立即預覽 (優先級: 中)
- 檔案系統為根：WebSite 型專案可直接以資料夾作為網站根目錄 (優先級: 中)
- 行為差異提醒：與 IIS 在管線、權限、部署特性上有所不同 (優先級: 中)
- 範例操作流程：解壓→檔案總管定位→右鍵傳送到→自動啟動與預覽 (優先級: 高)
- 輕量開發體驗：特別適合筆電或短暫檢視不值得開 VS 的情境 (優先級: 中)