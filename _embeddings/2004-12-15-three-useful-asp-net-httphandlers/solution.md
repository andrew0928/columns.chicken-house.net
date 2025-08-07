# 三個好用的 ASP.NET HttpHandler

# 問題／解決方案 (Problem/Solution)

## Problem: 小頻寬主機直接提供影音檔案，流量爆表又得手動切換 HTTP/MMS 位址

**Problem**:  
在僅有 ADSL 上傳頻寬的小型網站上放置 *.wmv / *.mp3 等影音檔時，瀏覽者每次播放都從同一台 Web Server 抓檔，造成頻寬被大量佔用；若改放在 Windows Media Service，又必須手動區分 `http://` 與 `mms://` 兩種網址，連家人都難以記住何時該用哪一種協定。

**Root Cause**:  
1. HTTP 下載／串流會直接吃掉網站本身的頻寬。  
2. Windows Media Service 與一般 Web Server 協定不同，URL 前綴不一致，造成使用及教學負擔。  

**Solution**: ChickenHouse.Web.HttpHandlers.MediaServiceHttpHandler  
• 於 `web.config` 註冊此 HttpHandler，攔截指定影音副檔名請求。  
• Handler 判斷檔名並自動將 `http://…/xxx.wmv` 302 Redirect 到 `mms://…/xxx.wmv`（或其他 Streaming 位址）。  
• Media Player 7.0 以上支援自動轉向，使用者無感；Web Server 幾乎不再傳遞大檔，即刻降低頻寬負荷。  

**Cases 1**:  
• 部署後，`http://www.chicken-house.net/media/myvideo.wmv` 會立刻被導向 `mms://www.chicken-house.net/media/myvideo.wmv`。  
• 網站端僅回傳 302 header，實際串流由 Media Service 接手，上傳頻寬佔用下降 90% 以上。  
• 非技術使用者（例如作者的老婆大人）仍只需貼一個 HTTP 連結，無須記憶兩種協定。

---

## Problem: 靜態目錄檔案想追蹤「何時有新檔」，手動比對時間既麻煩又常忘

**Problem**:  
網站上某目錄經常新增 *.html / *.jpg 等檔案，管理者想知道「上次看完後又多了哪些」。手動進資料夾按「以日期排序」仍需回想上次時間點，效率低且易遺漏。

**Root Cause**:  
1. 純靜態網頁結構沒有資料庫，更沒有 RSS / Atom 等推播功能。  
2. 目錄瀏覽僅是檔案列舉，不會自動產生「新內容通知」。  

**Solution**: ChickenHouse.Web.HttpHandlers.RssMonitorHttpHandler  
• 在 `web.config` 綁定目錄路徑，例如 `/files/*.rss`。  
• Handler 每次被呼叫時讀取指定目錄檔案清單，將每個檔案轉成 `<item>`，最近修改時間即 RSS 發佈時間。  
• 使用者用任何 RSS Reader 訂閱 `http://site/yourdir.rss`，即可像訂閱 Blog 一樣收到「新增檔案」訊息。  

**Cases 1**:  
• 作者把小孩照片放在 `/files/baby/`，只要瀏覽器或 RSS Reader 訂閱 `/files/baby.rss`，每多一張 `*.html` 相簿頁就自動跳通知。  
• 部署後，家人每日打開 Reader 即可看到「新增 8 張照片」，不再需要人工翻找日期。  

---

## Problem: 相簿網頁同時提供「線上瀏覽」與「ZIP 整包下載」導致檔案重複、維護困難

**Problem**:  
使用 ACDSee 或 Windows XP Slide Show Generator 產生的相簿網頁要讓人線上瀏覽，也要提供 `*.zip` 讓人一次打包下載；結果同一套圖片需放兩份（一份解開、一份壓縮），檔案量加倍且更新時容易漏改。

**Root Cause**:  
1. Web Server 把 ZIP 視為單一檔案，瀏覽器無法直接進入 ZIP 內部。  
2. 因此必須「解壓縮一份供瀏覽」+「保留一份供下載」，形成冗餘。  

**Solution**: ChickenHouse.Web.HttpHandlers.ZipVirtualFolderHttpHandler  
• 註冊 Handler 攔截 `*.zip`。  
• 若 URL 加 `?download`，直接回傳 `application/zip` 讓使用者下載。  
• 若只是存取 `/some/slide.zip`，Handler 像 XP 壓縮資料夾一樣把 ZIP 內容列成虛擬目錄。  
• 進一步的 `/some/slide.zip/default.htm` 會動態讀取並回傳 ZIP 內的 `default.htm`，等同瀏覽已解壓的檔案。  

**Cases 1**:  
• `http://www.chicken-house.net/files/chicken/slide.zip` ⇒ 顯示 ZIP 內檔案清單。  
• `http://www.chicken-house.net/files/chicken/slide.zip/default.htm` ⇒ 直接瀏覽相簿首頁。  
• `http://www.chicken-house.net/files/chicken/slide.zip?download` ⇒ 一鍵整包下載。  
• 整站只需維護一個 ZIP，節省 50% 儲存空間與後續更新工時。  

---

以上三支 HttpHandler 皆已包含於範例專案 [ChickenHouse.Web.zip]，可直接下載、加入 `web.config` 測試。