```markdown
# 從 CommunityServer 2007 到 BlogEngine.NET

## 摘要提示
- BlogML 匯入：透過 BlogML 匯出／匯入工具完成兩套系統之間的資料轉移。
- 時間戳錯誤：CommunityServer 輸出的修改時間被解析成 0000-01-01，導致 BlogEngine.NET 丟出例外。
- VS2008 修補：多數問題最終都得靠開啟原始碼、修改程式才能排除。
- 連結搬運：圖片、站內文章、站外文章的 URL 全面重寫，避免 404 與 SEO 損失。
- 兩段式轉檔：先匯入取得新 PostID，再以第二輪批次搜尋取代修正文章內容。
- 檢視次數：BlogEngine.NET 原生欠缺 View Count，需安裝／改寫 Extension 並匯入舊資料。
- 客製版面：利用 Master Page 與 CSS 調整，順利納入 Google Ads 及自訂控制項。
- 舊址轉新址：撰寫轉址模組，保留舊 CS URL，並以提示頁告知使用者。
- 程式碼品質：BlogEngine.NET 架構精實易懂，修改難度僅約 CommunityServer 的三分之一。
- 經驗分享：全文記錄從規畫、碰壁到完成的心路歷程，供後續搬遷者參考。

## 全文重點
作者原先使用功能成熟但龐大的 CommunityServer 2007 架設部落格，思考多時後決定遷移至輕量、開放原始碼且以 ASP.NET 為基礎的 BlogEngine.NET。遷移的關鍵工具是 BlogML：CommunityServer 以官方外掛匯出 BlogML，BlogEngine.NET 以 ClickOnce 下載的匯入程式透過 Web Service 讀入。不料匯入過程因日期欄位被帶成 0000/01/01 而發生時區計算錯誤，只好立刻打開 Visual Studio 2008 修改程式碼，刪除自動時區換算後才得以繼續。  
測試期很快暴露八大痛點：圖檔絕對路徑、Article 未被匯入、站內／站外 URL 失效、缺乏瀏覽次數、舊瀏覽次數遺失、版面客製、以及過去自行加入的多項功能。解方幾乎都離不開動手寫碼：以批次字串替換修復圖片路徑；自行撰寫雙階段轉檔腳本，先取得 BlogEngine.NET 生成的新 PostID，再回頭逐篇替換舊文的站內連結；安裝他人撰寫的 View Count Extension 並額外寫程式批次匯入舊統計值；利用 Master／UserControl 架構重製版面並嵌入 Google Ads 與原有控制項；最後再實作一個 HTTP 模組，將 CommunityServer 時代的複雜 URL 規則對應至新站，同時於轉址前顯示提示頁，既告知使用者又利於除錯。  
整個搬遷過程讓作者深入檢視 BlogEngine.NET 的程式碼，發現其架構清晰、程式量不大、易於擴充，相比 CommunityServer 製作者在 .NET 1.1 時代自行實作的複雜框架，維護與客製難度僅約後者的三分之一。文章最後展示了成功整合 Google Ads 的新版面、正確跳轉的新舊連結、以及站內外皆可正常瀏覽的結果，將完整經驗與心法留給有志從 CommunityServer 搬家到 BlogEngine.NET 的開發者參考。

## 段落重點
### 引言：一次意外卻必然的搬家
作者坦言「搬家」的念頭醞釀已久，但真正決定從 CommunityServer 2007 遷移到 BlogEngine.NET 卻只花了數天。BlogEngine.NET 年輕輕量、原始碼開放且 ASP.NET 架構熟悉，是主要吸引力；然而也因年輕，許多機制仍待磨合，作者提前預期會遇到不少小麻煩，於是決定以本文詳細記錄整個遷移過程與所學。

### BlogML 匯入測試與第一個障礙
遷移首要任務是資料轉移。藉由 CommunityServer 提供的 BlogML 匯出工具，再配合 BlogEngine.NET 官方 ClickOnce 匯入程式，理應能一次搞定；實測時卻因日期欄位誤讀為 0000-01-01，Web 服務在修正時區時發生負值例外。作者立即以 VS2008 編輯匯入程式，刪除時區運算程式碼後重編，總算順利導入全站文章並搭建起測試環境，也正式揭開後續一連串問題的序幕。

### 八大搬家痛點清單
測試網站運行後，作者列出八項亟待解決的問題：1) 圖檔絕對網址連回舊站；2) Article 未被匯入；3) 站內文章間互連失效；4) 外部網站仍指向舊 URL，導致 404；5) BlogEngine.NET 缺乏 View Count；6) 舊站累積的瀏覽次數遺失；7) 版面與廣告尚未整合；8) 過去自行加掛的控制項與驗證機制必須重寫。這份清單成為後續開發的工作藍圖，也讓作者意識到「搬家」遠非單純匯入資料即可。

### Visual Studio 上場：逐項解決問題
面對八大痛點，作者幾乎都得打開 Visual Studio 手動寫碼。圖片與 CSS 以批次字串替換修正；Article 部分改寫匯入程式使其不被忽略；View Count 透過社群開源的 Extension 並二次開發匯入舊數據；版面則利用 BlogEngine.NET 的 Master Page 與 UserControl 架構重新佈局，插入 Google Ads 與自製控制項。過程中作者深刻感受 BlogEngine.NET 程式碼精實、架構清楚的優點，修改體驗遠勝於 CommunityServer。

### 連結與網址的雙階段修補策略
站內連結因匯入後的網址格式與 PostID 全數改變，原本想用單純批次檔處理，但無法在匯入前得知新網址，遂改採「兩段式」策略：第一階段先正常匯入並紀錄新文章對應的 PostID 與新 URL；第二階段再掃描原始 BlogML 檔，將舊網址替換成新網址後回寫資料庫。對外則撰寫 HTTP 模組攔截舊 CommunityServer URL，解析並導向對應的新文章，並於跳轉前顯示提示頁，既維護使用者體驗，也方便除錯與搜尋引擎更新索引。

### 完成後的成果展示與總結
所有問題修畢後，新站成功呈現：版面素雅，Google Ads 與內容自然融合；站內外連結皆可正確導向；檢視次數正常累加；舊網址 301 轉址運作無礙。作者在結尾以多張截圖示範成果，並再次強調：只要肯動手，從 CommunityServer 搬遷到 BlogEngine.NET 並不困難，且可藉機重構版面與功能。文章亦鼓勵仍在觀望的友人不要再猶豫，勇敢邁出第一步。
```
