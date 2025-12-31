---
layout: synthesis
title: "三個好用的 ASP.NET HttpHandler"
synthesis_type: summary
source_post: /2004/12/15/three-useful-asp-net-httphandlers/
redirect_from:
  - /2004/12/15/three-useful-asp-net-httphandlers/summary/
postid: 2004-12-15-three-useful-asp-net-httphandlers
---

# 三個好用的 ASP.NET HttpHandler

## 摘要提示
- 動機：作者因為維運網站「懶」而寫了三個實用的 ASP.NET HttpHandler 來自動化繁雜工作
- MediaServiceHttpHandler：將網頁中的大型影音檔自動轉接到 Windows Media Services，節省頻寬
- 使用門檻：只要使用者端 Media Player 版本在 7.0 以上，即可自動播放
- RssMonitorHttpHandler：監控目錄檔案變化並輸出 RSS，讓靜態網站也能「訂閱更新」
- 靜態網站加值：不需改動原有 *.html 靜態頁面，即可提供 RSS 訂閱通知
- ZipVirtualFolderHttpHandler：把 ZIP 壓縮檔虛擬成網站目錄，直接瀏覽或連結 ZIP 內檔案
- 節省維運成本：避免同內容同時維護「網頁檔」與「下載包」的重工問題
- 範例路徑示範：支援直接下載、瀏覽 ZIP 清單、與直連 ZIP 內特定檔案
- 目的與風格：三個處理常見「小站維運痛點」的懶人工具，強調實用與自動化
- 取得方式：提供 ChickenHouse.Web 的範例程式碼下載

## 全文重點
本文介紹作者為解決個人網站日常維運痛點而撰寫的三個 ASP.NET HttpHandler，主軸是以最少維護成本換取更高的自動化與可用性。首先，MediaServiceHttpHandler 解決影音檔直接放網頁導致的頻寬負擔問題：對於頻寬有限（例如 ADSL 架站）的站台，傳統上需要手動分辨何時使用 http 與 mms 協定，既麻煩也容易出錯。此 Handler 可自動將在網站中的影音資源轉導至 Windows Media Services，只要用戶端 Media Player 版本在 7.0 以上，即可透明播放，大幅降低站台的頻寬消耗與教學成本。

其次，RssMonitorHttpHandler 針對「想知道某目錄新增了哪些檔案，卻常忘記上次看到哪裡」的情境，提供以 RSS 訂閱目錄變動的方式來解決。此 Handler 將指定目錄下的所有檔案視為可被訂閱的「文章」，當有新檔案加入，RSS Reader 就會顯示更新通知。對於大量以 *.html 組成的純靜態網站，這能在不改動原有頁面的前提下，快速賦予「RSS 訂閱」功能，對內容更新頻繁但缺乏動態後端的站點特別方便。

第三，ZipVirtualFolderHttpHandler 針對「相同內容同時要提供線上瀏覽與打包下載」的維護痛點，提供將 ZIP 檔視為虛擬目錄的能力。常見情境如相簿網頁：不論是用 ACDSee 或 Windows XP 的 Slide Show Power Toys 產生的靜態相簿，往往除了上線給人瀏覽，還要另外放一份 ZIP 方便一次下載。這會造成重工與維護難度。透過此 Handler，網站能把 *.zip 檔當成一個目錄來瀏覽：相同路徑可選擇直接下載 ZIP、列出壓縮包內容，或直接連到 ZIP 內部的檔案（例如 default.htm）。如此一來，只需上傳一份 ZIP，就同時滿足瀏覽和下載兩種需求，簡化部署與整理流程。

整體而言，三個 HttpHandler 聚焦於小站常見的實務問題：頻寬受限的影音發佈、靜態內容的更新追蹤與通知、以及壓縮檔與網站內容的同步維護。它們以最小侵入、低學習曲線的方式提升維運效率，尤其適合個人或小型網站。文末提供範例程式碼下載，方便讀者實作與套用。

## 段落重點
### 前言：寫 Handler 的初衷
作者花了幾個晚上開發三個 ASP.NET HttpHandler，核心動機是「懶」：希望用自動化手段減少教學、維護、與重工。以個人小站的限制為背景（例如 ADSL 頻寬有限、內容多為靜態頁），作者將常見痛點抽象為可重複使用的處理元件，以簡單部署方式快速提升網站可用性。

### MediaServiceHttpHandler：自動轉接影音到 Media Services
此 Handler 解決影音檔直接由網站提供時的高頻寬消耗問題。原本需要區分 http 與 mms 連結的繁瑣流程，交由 Handler 透明處理：當訪問網頁下的影音資源時，自動轉接到 Windows Media Services 進行串流播放。條件是使用者端 Media Player 版本需在 7.0 以上，即可無痛播放。對頻寬有限的小站而言，能顯著降低流量負載，也免去教育非技術使用者（例如站務人員或家人）切換連結協定的困擾。

### RssMonitorHttpHandler：讓目錄變成可訂閱的 RSS 來源
針對「想知道某個目錄新增了什麼檔案」的需求，此 Handler 將目錄內的檔案當成 RSS 項目，當有新檔案加入時，RSS Reader 會推送更新提醒。這對全靜態網站特別實用：無需改動既有 *.html，便可立即擁有「RSS 訂閱更新」的能力，符合現代使用者對內容通知的期待。作者並以「小皮的網頁」為例，提供 RSS 示範，顯示其能快速賦能既有站台，而不引入複雜的後端系統。

### ZipVirtualFolderHttpHandler：ZIP 即是虛擬目錄
面對相簿網站等常見情境，維護者常同時提供線上相簿與一份 ZIP 下載包，導致重複維護。此 Handler 讓 ZIP 檔在網站中被視為一個可瀏覽的目錄：使用者可選擇直接下載 ZIP、查看壓縮包中的檔案清單，或直接存取 ZIP 內部的檔案（像是 default.htm）。作者提供了三種 URL 範例：加上 ?download 參數進行下載、不帶參數瀏覽內容、或帶內部路徑直連檔案。此設計讓網站只需上傳一份 ZIP 檔，就能同時滿足瀏覽與打包下載需求，簡化資料整理與後續維護。

### 結語與下載
作者以輕鬆口吻強調「純現寶」，但三個 Handler 針對小站的實務痛點提供了有效解法：降低頻寬壓力、為靜態站加上 RSS 通知、以及以 ZIP 虛擬目錄減輕重工。文末提供 Sample Code 下載（ChickenHouse.Web.zip），方便讀者快速上手與擴充應用。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - ASP.NET 網站架構與 IIS 管線、HttpHandler/IHttpHandler 基礎
   - web.config 中的 handler/映射設定
   - 靜態資源服務與 Content-Type/下載回應處理
   - RSS 基本結構與讀取工具（RSS Reader）
   - 檔案系統操作（目錄列舉、ZIP 檔讀取）
   - 媒體串流基礎（HTTP vs MMS/串流伺服器、Windows Media Services）

2. 核心概念（3-5 個）及其關係：
   - HttpHandler 擴充點：以自訂邏輯接手特定 URL 請求 → 為靜態檔案/目錄提供動態行為
   - URL 轉換/代理：依請求特徵轉向適合的後端（例：HTTP → MMS 串流）
   - 將檔案系統虛擬化為服務：將目錄或壓縮包呈現為可瀏覽/訂閱的資源（RSS、虛擬資料夾）
   - 帶寬與維運優化：以串流、省去重複部署（只放 ZIP）、RSS 推播降低人工巡覽
   - 相容與用戶體驗：依用戶端能力（Media Player 版本）與參數（?download）提供正確體驗

3. 技術依賴：
   - ASP.NET + IIS → 提供 HttpHandler 執行環境與 URL 映射
   - Windows Media Services/播放器（Media Player 7+）→ 媒體串流相容性
   - 檔案系統 API/ZIP 讀寫函式庫 → 目錄掃描、ZIP 列表與解壓取檔流
   - RSS XML 產生 → Syndication 格式輸出與 Reader 相容
   - HTTP 回應控制 → 狀態碼、Header（Content-Type、Content-Disposition）、快取

4. 應用場景：
   - 小型站點節省頻寬：將大檔影音自動轉向串流服務
   - 靜態網站加入訂閱：對純 HTML 網站提供「新檔即新文章」的 RSS
   - 相簿/檔案發佈：僅上傳 ZIP 即可同時支援線上瀏覽與整包下載
   - 檔案更新監控：透過 RSS 追蹤指定目錄的新增內容

### 學習路徑建議
1. 入門者路徑：
   - 了解 IHttpHandler 介面與在 web.config 註冊自訂 handler
   - 寫一個最小可行的 Hello World handler，回傳純文字/JSON
   - 練習設定 Content-Type、Content-Disposition，體會下載與瀏覽差異
   - 嘗試將特定副檔名映射至 handler（例如 .zip、.rss）

2. 進階者路徑：
   - 實作 MediaServiceHttpHandler：依請求檔案類型產生轉向（HTTP 302 或回傳播放清單）
   - 實作 RssMonitorHttpHandler：列舉目錄檔案、產出 RSS XML、處理 If-Modified-Since/ETag
   - 實作 ZipVirtualFolderHttpHandler：用 ZIP 函式庫列出內容、串流單檔、支援 ?download
   - 加入快取與安全性（白名單目錄、路徑穿越防護、大小限制、權限控管）

3. 實戰路徑：
   - 在測試站布署三個 handler，設計對應 URL 規則與 MIME 對應
   - 以實際影音檔測試轉向播放，在 RSS Reader 中訂閱目錄 RSS，驗證 ZIP 虛擬瀏覽/下載
   - 監控效能（日誌、吞吐、快取命中），調整回應標頭與檔案讀取策略
   - 撰寫文件與自動化部署腳本，將 handler 套用到團隊專案

### 關鍵要點清單
- HttpHandler 基礎：IHttpHandler.ProcessRequest 接手請求並回應內容或轉向 (優先級: 高)
- web.config 映射：將副檔名/路徑綁定到自訂 handler 以攔截請求 (優先級: 高)
- 媒體轉向策略：依影音副檔名改用 MMS/串流端點，降低 HTTP 帶寬壓力 (優先級: 高)
- 用戶端相容性：Media Player 7+ 等播放相容性檢核與替代方案 (優先級: 中)
- RSS 產生：以檔案清單輸出 RSS（標題、連結、日期），便於訂閱更新 (優先級: 高)
- 目錄列舉與排序：依檔案建立/修改時間排序，對應 RSS 發佈時間 (優先級: 中)
- ZIP 虛擬資料夾：將 .zip 視為可瀏覽目錄，允許直接連入內部檔案 URL (優先級: 高)
- 下載與線上瀏覽切換：以查詢參數 ?download 控制 Content-Disposition (優先級: 中)
- 檔案串流與記憶體使用：以串流回應避免整檔載入，處理大檔效能 (優先級: 高)
- 安全性與路徑防護：防止路徑穿越、限制可存取目錄/副檔名 (優先級: 高)
- MIME 與標頭設定：正確回應 Content-Type、快取控制、範圍請求 (優先級: 中)
- 快取與條件式請求：支援 ETag/Last-Modified，減少頻寬與 CPU (優先級: 中)
- 例外處理與回應碼：對缺檔/格式錯誤回傳 404/400/415 等適當碼 (優先級: 中)
- 記錄與監控：為 handler 加入存取日誌與度量，便於調校 (優先級: 中)
- 部署與測試：區分開發/正式環境設定、以自動化腳本與整合測試保障品質 (優先級: 中)