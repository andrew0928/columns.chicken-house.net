# Running Jekyll on NAS ‑ 高效率的新選擇

## 摘要提示
- 靜態網站優勢: 在硬體能力有限的 NAS 上，以 Jekyll 產生靜態 HTML 可取代 WordPress，速度更快且維護更安全。  
- 文件即程式碼: 把 Markdown 文件與程式碼一起納入 Git 版本控制，配合 Jekyll 自動產生網站，形成「Blogging as Code」工作流。  
- 微軟實例: MSDN Windows Containers 文件採用 Jekyll 與 GitHub 流程，示範大型文件協作的最佳典範。  
- Docker 部署: NAS 只要支援 Docker，就能透過 jekyll/jekyll 官方映像快速建立環境。  
- 目錄規畫: 專案根目錄 /docker/jekyll，文章放 _posts，成品輸出至 _site 再由 Web Station 發佈。  
- 三步驟安裝: 1. 拉取映像並掛載 Volume；2. 複製網站樣板；3. 在 Web Station 建立 Virtual Host 指向 _site。  
- 自動重建: Container 內啟用 auto-regen，任何檔案異動都會觸發重新 Build，確保網站內容即時更新。  
- 效能實測: Atom D2701 NAS 編譯全站僅 42 秒，與桌機 i7 不相上下，顯示靜態產生器對硬體要求低。  
- 備份建議: 檔案層可搭配 Btrfs/ZFS 快照或 Git 儲存庫，保留歷史版本與分支管理能力。  
- 應用場景: 個人私有部落格、團隊技術文件、內部 API 說明書皆適用，降低佈署與維運成本。  

## 全文重點
作者因為體驗到 GitHub Pages 的便利，而發現背後的核心—靜態網站產生器 Jekyll—若能移植到家用 NAS，便可利用 NAS 低耗能、長時間開機且具備檔案伺服器優勢的特性，打造一套快速、安全又幾乎零維護的私有網站或文件平台。文章先回顧「Blogging as Code」概念，強調把程式碼與文件一起放入版本控制系統的好處，接著以 Microsoft 將 MSDN 文件遷移到 Jekyll 作為成功範例，證明大型企業也採用相同做法。

實作部分僅需 NAS 能安裝 Docker。作者將 /docker/jekyll 對應至 Container 內的 /srv/jekyll，使版型、文章與輸出目錄彼此分離，再利用 Synology Web Station（或任一 Web Server）直接發佈 _site 中的靜態檔案；如此即使 Jekyll 停止，網站依舊可被存取。步驟分成三階段：拉映像・設定 Volume、複製網站樣板、設定 Virtual Host。完成後 Container 會自動監聽檔案變動並重新編譯，開發者可透過 Container 暴露的 4000 埠本地預覽，或透過網域名稱瀏覽正式站。

效能測試顯示，在 i7-2600K 桌機需 30 秒的 Build，移到 Atom D2701 NAS 只多花 12 秒，證明 Jekyll 編譯不依賴強大 CPU。與 WordPress 等動態系統相比，靜態網站的存取速度與資源消耗皆大幅優化，同時降低資安風險。最後作者鼓勵讀者結合 Git、NAS 快照及自動備份，打造兼顧速度、彈性與可靠性的文件／部落格平台。

## 段落重點
### 用 Jekyll 當作開發文件管理系統
說明「Blogging as Code」理念：將程式碼註解自動產生 API 文件，其他手動維護的安裝說明、規格文件則以 Markdown 撰寫並與程式碼共存於 Git。Jekyll 能在每次 Push 後自動編譯並部署，替代過去 Word 檔＋檔案伺服器的低效率流程，讓開發者在同一工作流內完成程式與文件維護。

### 應用範例: MSDN – Windows Container Document
微軟將 Windows Containers 文件移轉至 GitHub，以 Jekyll 驅動 MSDN 靜態頁面。讀者點選「Contribute」即可開 Issues 或送 Pull Request，文件前的 YAML Front-Matter 明示 Jekyll 架構。此案例驗證 Jekyll 能支援大型、多作者的企業級文件協作，也展示開放貢獻與自動佈署的優點。

### 環境準備
以 Synology 為例，重點在確保 NAS 支援 Docker。架構設計為：Docker Container 內跑 Jekyll 負責 Build 與監控，輸出的 _site 靜態檔交由 NAS 內建 Web Station（Nginx/Apache 均可）服務。檔案路徑統一置於 /docker/jekyll，方便備份、快照與權限管理。

### STEP 1. 架設 Jekyll（使用 Docker）
透過 DSM Docker 套件搜尋並拉取 jekyll/jekyll:latest 映像，建立 Container 時將 NAS 端 /docker/jekyll 掛載到容器 /srv/jekyll。網路與埠設定保持預設即可；容器內 Jekyll 啟動後會開 4000 埠供即時預覽，也會持續監聽檔案異動自動重建。

### STEP 2. 複製網站樣板至 /docker/jekyll
將既有的 Jekyll 專案（含 _config.yml、佈景與 _posts 文章）整份複製到指定目錄。儲存層可以只是檔案系統，也可搭配 Git 或 NAS 內建快照備份，以取得完整版本控制、分支與回溯能力。編輯器推薦 Visual Studio Code，其 Markdown 與 Git 整合度高。

### STEP 3. 設定 NAS Web Station
開啟 Web Station，建立新的 Virtual Host，網域或埠可視需求設定，根目錄指向 /docker/jekyll/_site。選用 Nginx 作為 Web Server 可獲得較佳效能，也確保即便 Jekyll 服務停止，靜態網站仍能正常對外服務。

### 測試結果
首次啟動容器時，Jekyll 會安裝必要 Gem 並完成編譯，終端機 Log 出現 “Generating… done” 即代表成功。局域網預覽可以 NAS_IP:HOST_PORT 存取，正式站則透過 Virtual Host 網域。效能測試顯示，Atom D2701 NAS 全站 Build 僅 42 秒，與 i7 桌機相差有限，而靜態 HTML 的瀏覽速度遠勝過在同一台 NAS 上執行 WordPress。結論指出 Jekyll on NAS 是低成本、高效率且安全的私人部落格與文件平台方案。