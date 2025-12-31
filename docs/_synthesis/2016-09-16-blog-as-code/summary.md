---
layout: synthesis
title: "Blogging as code !!"
synthesis_type: summary
source_post: /2016/09/16/blog-as-code/
redirect_from:
  - /2016/09/16/blog-as-code/summary/
postid: 2016-09-16-blog-as-code
---

# Blogging as code !!

## 摘要提示
- 靜態網站取向: 放棄傳統部落格系統，改以純靜態網站減少維護與資源消耗。
- GitHub Pages: 以 GitHub Pages 作為主機服務，自動以 Jekyll 產生網站。
- Markdown 編寫: 以 Markdown 搭配 Git 版本控制，取代後台與所見即所得編輯器。
- Developer 工作流: 以「blogging as code」的觀念，讓文章、樣板、設定全部進版控。
- VS Code 工具鏈: 使用 Visual Studio Code 作為編輯、預覽與 Git 操作的一站式工具。
- Jekyll 本機預覽: Windows 環境評估三法：Linux原生、Windows安裝、Docker 容器。
- Docker 實作取捨: Docker 方便但 watch/polling 開銷大，建議改為手動重啟容器。
- Windows 安裝眉角: Ruby 版本相容、IIS 與大小寫、.aspx 模組等相容性問題需處理。
- WordPress 移轉: 透過工具與插件匯出，解決中文網址、分類/標籤、留言與轉址。
- 風險與授權: 開源帶來複製風險，但以 CC 授權與開放分享換取便利與擴散。

## 全文重點
作者回顧多年使用多套部落格系統的經驗後，選擇回歸簡單，以純靜態網站加上 GitHub Pages 的方式經營部落格，並提出「blogging as code」的理念：將寫作流程全面開發化，讓文章、樣板、設定檔都像程式碼一樣被版本控制、審查、佈署。動機包括：不再承擔系統維運與升級成本、獲得更成熟的版本控制、以 Markdown 取代笨重編輯器、用第三方服務處理互動需求。技術上採用 Jekyll 作為靜態站生器，GitHub Pages 自動建置發佈，作者在本機以 VS Code 撰寫、預覽與 Git 操作。

在本機預覽方面，作者比較了三種做法：Linux 原生（最佳相容但環境不符使用習慣）、Windows 直接安裝（效能佳但相容性坑多）、Docker for Windows（建置最省心，但因 volume 事件通知問題需 --force_polling，導致 I/O/CPU 開銷提高與延遲）。實務建議是在 Docker 模式避免 --watch，改用手動重啟容器；或採 Windows 安裝 Jekyll，以較佳的 rebuild 時間支援日常撰寫。Windows 方案需注意 Ruby 版本（選 2.2）、Jekyll 內建 web server 對中文檔名限制、IIS 與 GitHub Pages 檔名大小寫差異、以及 .aspx 被 IIS 模組攔截的相容性議題。作者以並行啟動 jekyll serve（監控與編譯）與 iisexpress（本機預覽）繞過限制，並利用 --drafts 測試未發佈文章。

在遷移 WordPress 上，作者綜整多篇參考並實測指出共通難點：中文網址被轉成大量編碼、分類與標籤支援不一致、不包含留言、普遍改用 Disqus。作者的處方包括：先從 WordPress 匯出 XML 層處理中文網址，使留言與文章 URL 能一致對應；選用支援 categories/tags cloud 的主題；導入 jekyll-redirect-from 以相容舊站多種連結格式（含 .aspx 與查詢參數），並以自製 C# 工具輔助批次處理與補欄位。此外，嵌入 Google Analytics、AdSense、Facebook Open Graph 與 Like/Share 也簡化為在模板中插入對應 HTML 與 Liquid 變數。

結論指出，這套方案雖需跨越環境與相容性的小坑，但總體是巨大進步：以 Git 控制不僅是單篇文章，而是整站內容、屬性與設定；以分支開發版面與功能後再合併上線；流程與軟體開發一致，極大化透明度與可維護性。至於開源後被複製的風險，作者以 CC 授權與開放心態面對，視之為推廣與分享的一部分，並正式以新站上線作結。

## 段落重點
### TL;DR
作者從自架 asp.net 1.1 到 .Text、Community Server、BlogEngine、WordPress，一路更換系統與升級，深感維運成本與繁複功能不符自身需求。針對權限、後台、版本控制、編輯器、互動等問題，作者提出用最簡化的靜態站路線解決：內容以 Markdown 撰寫、版本控制交給 Git、託管改為 GitHub Pages、互動以第三方服務嵌入。核心思維是「是否真的需要 runtime？」若網站內容可事先產生，則以靜態化滿足需求；動態元素如留言與分享交給外部服務嵌入即可。於是提出「blogging as code」，將整個部落格開源上 GitHub，以開發者視角與工具鏈運作寫作與佈署。

### Solution: GitHub Pages Service + Visual Studio Code
GitHub Pages 在指定分支異動時自動以 Jekyll 產出靜態網站，流程幾乎全自動：先建模板與設定，之後以 Markdown 寫文並 push 即完成發佈。作者列舉多篇比較 Jekyll 與 WordPress 的文章，說明轉換的利弊，也指出有人轉回 WordPress 的案例，顯示取捨因人而異。在工具層，作者鎖定 VS Code：內建 Git 操作、強力語法高亮、IntelliSense、Markdown 預覽小而快，與 GitHub Pages 構成面向開發者的黃金組合。整體以最少系統、最熟悉的版控與編輯體驗，達成輕量、穩定、易維護的寫作與發佈流程。

### Workflow: How to create a new post ?
作者以 Windows 為主力環境，設計本機撰寫—預覽—發佈的迴圈。流程圖示為在 VS Code 編輯、Jekyll 本機建置預覽、Git push 觸發 GitHub Pages。關鍵在本機 Jekyll 的部署方式：1) Linux 原生最佳但不符日常環境；2) Windows 安裝效能最佳但相容性坑多，對 Ruby 不熟者成本高；3) Docker for Windows 建置最輕鬆，受限於檔案通知需改用 polling，導致 rebuild 延遲與資源耗用。作者實測後建議：若走 Docker，避免 --watch，改手動重啟容器或以腳本監測檔案變化；若追求日常效率，傾向用 Windows 原生 Jekyll。

### Running Jekyll on docker-for-windows
實作上以 docker run 映射本機目錄到 /srv/jekyll，開 4000 埠並啟動 jekyll s。因 Windows 到容器的 volume 無法傳遞檔案變更事件，需加入 --force_polling 解決，但會導致高 I/O 與 CPU 負擔，偵測延遲明顯。作者以約 400 篇文章的庫測得初次 build 約 70 秒，偵測異動後的 rebuild 因 polling 成本甚至可能拖長至數十秒甚至更久，CPU 使用率也偏高。實務建議：不要使用 --watch，改以手動或腳本在檔案變更時重啟容器，以換取穩定與效率；或改採其他本機執行選項。

### Running Jekyll on windows
Windows 原生安裝 Jekyll 實測初次 build 約 40 秒、rebuild 約 30 秒，日用體感優於 Docker polling 模式。需注意幾點：1) Ruby 版本相容性，建議 2.2；2) Jekyll 內建 server 在 Windows 對中文檔名不友善，作者以 jekyll --watch 搭配 iisexpress 作雙服務預覽；3) 檔名大小寫在 IIS 與 GitHub Pages 行為不同，大小寫不一致會導致圖檔遺失且 Git 可能不偵測變更；4) .aspx 路徑在 IIS 會被 ASP.NET 模組攔截，靜態頁 404，需改以 Jekyll 預覽或調整設定。日常流程為啟動 VS Code、啟動 jekyll s --draft -w、啟動 iisexpress 指向 _site 目錄，以 --drafts 方便測試未發布文章。

### Wordpress to GitHub Pages Migration
作者彙整官方與社群工具，指出普遍痛點：中文網址被轉成大量編碼字元、分類或標籤支援不一、留言未處理且多建議用 Disqus。作者方案為：先在 WordPress 匯出 XML 層處理中文 URL，確保日後留言對應；選擇支援 categories/tags cloud 的主題以降低模板調整成本；用 jekyll-redirect-from 在 Front Matter 列出舊站多種 URL（含 .aspx 與不同層級路徑），確保相容；對於含查詢參數的舊連結以前端 JS 補救。分析工具方面，將 GA、AdSense、Facebook OG 與讚/分享按鈕以 HTML 片段與 Liquid 變數嵌入模板即可。作者並提供自製 C# 匯入工具，解決中文檔名、分類標籤、轉址與留言對應等細節。

### Conclusion
以「blogging as code」重塑寫作與佈署，帶來版本控制的一致性與可回溯性，不只針對單篇，而是全站內容、設定與樣板皆可在分支上協作與測試，最後合併上線，流程與開發無縫對齊。雖然在 Windows 與 Docker 上需處理相容性與效能取捨，但整體成本仍遠低於傳統動態系統的維運與升級。把網站開源確實讓「複製」更容易，但在 CC 授權與分享心態下反成優勢，利於傳播與貢獻。作者最終以新站上線作結，實證此架構在可維護性、效率與透明度上的整體優勢。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 Git 與 GitHub 操作（clone/commit/push/branch/merge）
   - Markdown 語法與基本 HTML/CSS 概念
   - 靜態網站與動態網站的差異
   - 基本終端機/命令列操作（Windows/ Linux 或 Docker）
   - 基本網站部署與 DNS 概念（可選）

2. 核心概念：
   - Blogging as code：用「文字檔＋版本控制」經營部落格
   - 靜態網站生成：以 Jekyll 將 Markdown/模板轉為 HTML
   - GitHub Pages：以 repo branch 觸發自動建置與託管
   - Template/資料分離：以 Liquid 模板與 Front Matter 組構內容
   - 外掛式動態能力：以第三方服務（留言/社群/統計/廣告）補齊動態需求
   彼此關係：內容以 Markdown 編寫 → 交由 Jekyll＋Liquid 生成 → 推至 GitHub Pages 自動部署 → 以第三方插件補動態 → 由 Git 進行版本控管與協作。

3. 技術依賴：
   - GitHub Pages 依賴 Jekyll（或內建的 pages build），由指定 branch（main/docs/gh-pages）觸發建置
   - Jekyll 依賴 Ruby 與 gems 環境；Windows 相容性較弱，Linux/Docker 較穩定
   - 本地預覽可直接 jekyll serve 或以 Docker 容器執行；Windows 另可搭配 IIS Express 作檔案伺服
   - 網站互動與追蹤依賴第三方：Disqus/Facebook Comments、Google Analytics、Facebook 社群外掛、Google AdSense
   - 轉址依賴 jekyll-redirect-from gem；網址兼容依賴嚴格大小寫一致與正確 permalink

4. 應用場景：
   - 個人/團隊技術部落格、產品文件站、專案說明頁
   - 不需後端流程與會員權限的內容網站
   - 追求版本可追溯、分支開發、開源協作的內容管理
   - 從 WordPress、BlogEngine 等系統遷移至靜態化的網站

### 學習路徑建議
1. 入門者路徑：
   - 建立 GitHub 帳號與熟悉 Git 基本操作
   - Fork 一個現成的 Jekyll 主題，嘗試新增一篇 Markdown 文章並推送至 GitHub Pages
   - 認識 Front Matter（title/tags/categories/permalink）與 Liquid 基本語法
   - 啟用 Google Analytics、Facebook/Open Graph 基本標籤

2. 進階者路徑：
   - 本地安裝 Jekyll（或用 Docker）進行即時預覽與除錯
   - 客製化主題：調整佈局、導覽、分類/標籤頁、Tag/Category Cloud
   - 導入 jekyll-redirect-from、處理大小寫/中文路徑、規劃 permalink 策略
   - 撰寫 Draft 流程、分支測試（feature branch）與 Pull Request 審稿

3. 實戰路徑：
   - 規劃從 WordPress 匯出：處理中文網址與檔名、category/tags 對應
   - 導入留言（Disqus 或 Facebook Comments）與舊文對應
   - 撰寫轉址規則，驗證舊連結（含 aspx 舊制與 query string 特例）
   - 以 VS Code＋擴充套件優化 Markdown/預覽/拼字/連結檢查
   - 建立自動化腳本（PowerShell/Makefile）啟動本地預覽、快取清理、資產壓縮

### 關鍵要點清單
- Blogging as code：以文字檔＋版本控制管理部落格全生命周期（文章、設定、模板、發布）(優先級: 高)
- 靜態化思維：無「即時決策」需求的內容可預先生成，減少維運負擔與資安面 (優先級: 高)
- GitHub Pages 流程：指定分支觸發 Jekyll 建置，自動發布至公網 (優先級: 高)
- Markdown＋Liquid：以易讀格式寫作，透過模板引擎組版，提高生產力 (優先級: 高)
- 第三方動態插件：以 Disqus/FB Comments、Analytics、OG/Like/Share 等嵌入擴充動態 (優先級: 中)
- 本地預覽策略：Windows 原生 Jekyll 相容性與效能 vs Docker 的易裝但需 polling 的權衡 (優先級: 中)
- Docker volume 通知限制：--watch 遇到通知丟失需 --force_polling，效能成本高 (優先級: 中)
- Windows 特性地雷：IIS 對 .aspx 的處理、大小寫不敏感導致與 GitHub Pages 行為不一致 (優先級: 高)
- Ruby 版本相容：Jekyll gems 對特定 Ruby 版本（如 2.2）相容性較佳，需鎖定版本 (優先級: 中)
- 轉址與舊鏈結維護：用 jekyll-redirect-from 與嚴謹 permalink 策略保存 SEO 與外鏈 (優先級: 高)
- WordPress 遷移重點：處理中文網址/檔名編碼、category/tags 對應、comments 搬遷 (優先級: 高)
- 工具鏈選擇：VS Code 提供 Git 整合、Markdown 預覽、語法高亮，提升編修效率 (優先級: 中)
- Draft 與發布流程：利用 --drafts 與 Front Matter 控制發佈狀態，降低誤發風險 (優先級: 中)
- 效能觀測與優化：關注初次 build/增量 rebuild 時間，依需要調整容器資源或改用原生環境 (優先級: 低)
- 授權與開源：將整站開源有助傳播與協作，但需清楚標示 CC 授權與出處 (優先級: 低)