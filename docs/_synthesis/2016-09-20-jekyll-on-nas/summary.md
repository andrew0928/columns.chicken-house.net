---
layout: synthesis
title: "Running Jekyll on NAS - 高效率的新選擇
title: Deploy Windows Containers on Nano Server"
synthesis_type: summary
source_post: /2016/09/20/jekyll-on-nas/
redirect_from:
  - /2016/09/20/jekyll-on-nas/summary/
---

# Running Jekyll on NAS - 高效率的新選擇

## 摘要提示
- 靜態網站與NAS: 在NAS上用Jekyll生成並發布靜態網站，兼顧效能與安全性
- Blogging as Code: 以程式化方式管理文件與內容，與版本控制緊密整合
- Docker部署: 以官方 jekyll/jekyll 容器監控目錄，變更即自動重建
- 文件工作流程: 程式碼註解生成API文件＋Markdown撰寫其他文件的雙軌並行
- MSDN實例: 微軟文件採Jekyll＋GitHub協作，Issues/PR直接驅動內容更新
- Synology環境: DSM內Docker＋Web Station（Nginx）對應 _site 目錄發布
- Volume對應: 將 /docker/jekyll 對映容器 /srv/jekyll，簡化檔案存取
- Git與備份: 可選擇Git管理或NAS檔案系統備份，需求高者建議搭配版本控制
- 本機測試: 可用Jekyll內建伺服器（port 4000映射）與Web Station雙路驗證
- 效能評估: i7 PC 30秒、Atom NAS 42秒建置完成，差距小、體感大幅加速

## 全文重點
作者從GitHub Pages接觸到Jekyll，體認到靜態網站在效能與安全上對NAS環境極為合適，相較於在硬體資源有限的NAS上跑WordPress這類動態網站，靜態HTML能提供更快的回應與更低的維運風險。延續「Blogging as Code」的理念，文章示範如何在Synology NAS上以Docker快速部署Jekyll，讓內容檔案一有變動即自動重建網站，並由NAS的Web Station（採Nginx）對外提供服務。

在文件工作流上，作者主張將可自動生成的API文檔（由程式碼註解編譯而成）與需人工維護的文件（如安裝手冊、規格書）同時納入版本控制，後者以Markdown撰寫並與程式碼共存於repo中。部署上可用GitHub Pages全自動釋出；若有隱私或內部專案需求，也能改在NAS自行架設。MSDN Windows Containers文檔案例印證了此法的可行與高效：讀者可在GitHub上透過Issue/PR協作，Jekyll則自動接力發布更新。

實作方面，作者在Synology DSM內安裝Docker，從Registry拉取官方映像 jekyll/jekyll:latest，將NAS的 /docker/jekyll 對應容器內 /srv/jekyll，並把網站樣板與內容複製到該目錄（文章放 _posts，產出會於 _site）。Web Station再將虛擬主機指到 /docker/jekyll/_site，以Nginx服務對外。初次啟動需等待Jekyll安裝gems與生成站點，從容器日誌可確認進度；同時可用容器映射的4000埠進行Jekyll內建伺服器測試，或直接用Web Station對外網址驗證。

作者也討論了儲存與版本控制：單純檔案系統僅有變更層級的還原，缺乏分支、追蹤等能力，因此建議有協作或審核需求時仍搭配Git使用，另可利用NAS內建備份或先進檔案系統（Btrfs/ZFS）增強保護。效能測試顯示，雖NAS硬體（Atom D2701／2GB RAM）遠不如桌機（i7-2600K／24GB RAM），但Jekyll建置時間僅約30秒對42秒的差距；而在瀏覽體感上，靜態網站幾乎即點即開，遠勝過以往在NAS上跑的動態網站。結論是，若不願將內容放到GitHub或需要內部部署，利用NAS＋Docker＋Jekyll是一個穩定、高效、易維護的方案。

## 段落重點
### 用 Jekyll 當作開發文件管理系統
作者延續「Blogging as Code」理念，主張把程式碼與文件並置於版本控制系統中，形成一致的開發與文件流程。文件來源分兩類：其一是由程式碼註解自動產生的API/函式庫文件；其二是需人工維護的文件，如安裝手冊、規格書等。過去作者讓（1）在每日建置時自動生成，並以網站讓團隊下載（2）的Word檔，但體驗不佳。改用Markdown撰寫（2）並交給GitHub Pages發布後，達成「Push即部署」的簡化流程，極大提升便利性。若因隱私與合規不適合放上GitHub，則在NAS內自行部署Jekyll，仍能複製相同的自動化與版本化優勢，既保內部掌控，也保留靜態網站的高效能、高安全性與低維運成本。

### 應用範例: MSDN - Windows Container Document
作者發現MSDN的Windows Containers文件也使用Jekyll與GitHub協作：每篇文件開頭有典型Jekyll前置欄位（Front Matter），頁面上的Contribute連結指向對應的GitHub Markdown檔。讀者可直接開Issue或發PR，由維護者審閱合併後，Jekyll自動重新發布網站。此案例顯示，企業級文件同樣適合採用以Markdown＋Jekyll為核心的流程：撰寫標準化、審核透明化、釋出自動化，在持續變動的技術內容中尤其有效。作者強調這種「程式碼與文件共治」的模式每天都看得到、用得到，證實其不是實驗品，而是成熟、可複製的最佳實務，值得在團隊與組織內推廣。

### 環境準備
以Synology NAS為例，前提是NAS需支援Docker（S/Q/白牌皆可，只要有Docker即可）。架構為：透過Docker跑Jekyll容器，監控NAS上的指定目錄，檔案一有變更即自動重建靜態網站；成品輸出到 _site，由NAS內建的Web Station直接對外提供服務。作者將根目錄定為 /docker/jekyll，網站模板與內容置於此，文章放在 _posts，Jekyll編譯後輸出至 /docker/jekyll/_site，對應網址則由Web Station虛擬主機設定。選擇Web Station（Nginx）作最終對外服務，讓網站即便Jekyll沒在跑也不會掛，提升可靠度與效能，同時分離「建置」與「服務」兩個角色，便於維運與擴展。

### STEP 1. 架設 Jekyll (使用 docker)
打開DSM的Docker套件，於Registry搜尋並拉取官方映像 jekyll/jekyll:latest。建立容器時，將NAS的 /docker/jekyll 掛載到容器內 /srv/jekyll，其他網路與埠設定採預設即可。此Volume對應是關鍵：它讓Jekyll能直接監控並讀寫NAS實體目錄，包含讀入模板與內容，以及輸出編譯結果至 _site。由於容器內會安裝所需的Ruby gems並執行Jekyll伺服與Auto-regeneration，初次啟動需稍候依賴安裝與初次建置完成。這種容器化方式隔離了環境差異，減少在NAS上手動安裝Ruby與套件的成本與風險。

### STEP 2. 把你的網站樣板 (含內容檔案) 複製到 NAS:/docker/jekyll
將既有的Jekyll站台樣板與內容直接Copy到 /docker/jekyll（文章在 _posts）。此作法未強制綁定Git倉庫，單純用檔案系統即可運作；若有需要，仍可自行接上Git或其他版本控制工具，或仰賴NAS備份、Btrfs/ZFS等快照功能保護資料。不過作者提醒：檔案系統層級的歷史僅限回溯與復原，缺乏分支與細緻追蹤等協作能力；若團隊協作或審核要求較高，建議採用Git來管理內容。撰寫工具方面，作者推薦使用Visual Studio Code進行Markdown編輯與預覽，搭配版控與擴充套件，能提升撰寫與維護效率。

### STEP 3. 設定 NAS web station (對應目錄: /docker/jekyll/_site)
啟用Web Station，建立對應的Virtual Host，域名或埠號按需求配置，網站根目錄指向 /docker/jekyll/_site。Web伺服器選Nginx（速度快、資源占用低），讓Jekyll只負責建置（Generate），由Nginx專職對外服務靜態檔案。這種分工可提升整體效能與穩定性：即使Jekyll容器暫停或重啟，已生成的靜態網站仍能被Nginx穩定提供。對外測試時，使用Virtual Host對應的域名即可；內部驗證也可同時透過Jekyll的內建伺服器（容器對外映射的4000埠）來檢視生成狀態與版面。

### 測試結果
完成上述配置後，初次啟動須等待Jekyll安裝gems與生成站點。可透過容器終端或日誌檢視進度，看到“Generating... done in xx seconds.”即表示建置完成；日誌亦會顯示Auto-regeneration啟用與服務埠等資訊。測試方式有二：1）Jekyll內建伺服器，使用 http://{NAS-IP}:{映射埠}；2）Web Station對外服務，使用 http://{你的網域或埠}。實測體感上，靜態網站在NAS上呈現「即點即開」，顯著優於以往在資源節省導向的NAS上跑WordPress。建置效能方面，桌機（i7-2600K/24GB RAM）約30秒，NAS（Atom D2701/2GB RAM）約42秒，差距有限且在可接受範圍；瀏覽端的加速體感更為明顯。作者結論：若不願將內容上雲或需內部部署，NAS＋Docker＋Jekyll是高效率、低維運且安全的理想選項。

## 資訊整理

### 知識架構圖
1. 前置知識：
- 靜態網站與動態網站的差異
- 基本的 Markdown、Git 版本控制概念
- NAS 基本管理（Synology/QNAP/白牌）、Docker 基本操作（鏡像、容器、Volume 對應、Port 映射）
- Jekyll 基本結構與工作流程（_config.yml、_posts、_site）

2. 核心概念：
- Jekyll 靜態網站生成：從 Markdown/模版生成純 HTML，部署簡單、速度快與安全性高
- Docker 容器化：用 jekyll/jekyll:latest 隔離執行環境，透過 Volume 監控檔案變動自動重建
- NAS 作為私有部署平台：避免把內容公開到 GitHub，利於內部文件或私有站台
- Web 伺服器分工：Jekyll 負責編譯輸出至 _site，NAS Web Station/Nginx 負責高效靜態檔案服務
- 文件即程式碼（Docs as Code）：與程式共版本控，支援 PR/Issue 協作（以 MSDN/Windows Containers 為範例）

3. 技術依賴：
- Jekyll 依賴 Ruby/Gems，但以 Docker 封裝免本機安裝 → 需要 NAS 支援 Docker
- 檔案存放於 NAS 檔案系統（可再搭配 Git、Btrfs/ZFS Snapshot、NAS 備份）
- 生成輸出到 /docker/jekyll/_site → 由 NAS Web Station（Nginx/Apache）對外提供服務
- 監控與重建：容器內自動偵測 /srv/jekyll 檔案變動 → 重新 build

4. 應用場景：
- 企業/團隊內部開發文件、安裝手冊、規格書的私有發布
- 想要擺脫 WordPress 等動態系統、追求速度與低維運風險的部落格/官網
- 不願將內容公開至 GitHub Pages 的私有/內網站台
- API/Class Library 文件：由程式註解產生，再與手寫 Markdown 文件整合

### 學習路徑建議
1. 入門者路徑：
- 了解靜態網站與 Jekyll 基本概念與目錄結構
- 在 NAS 套件中心安裝 Docker，拉取 jekyll/jekyll:latest
- 設定 Volume 對應：NAS /docker/jekyll → 容器 /srv/jekyll
- 將範例 Jekyll 專案複製至 /docker/jekyll，啟動容器確認自動重建
- 在 Web Station 建立 Virtual Host，指向 /docker/jekyll/_site，用 Nginx 提供服務

2. 進階者路徑：
- 導入 Git 版本控制，設定分支/PR 流程與備份策略（NAS Snapshot + Git Remote）
- 自訂主題、版型、Front Matter；最佳化 _config.yml
- 啟用增量建置、Gem 快取、容器建置效能調校
- 使用反向代理、HTTPS 憑證、存取控制（內網/帳密保護）

3. 實戰路徑：
- 建立團隊文件庫：定義資料夾規範與貢獻流程（Issues/PR 模板）
- 以 Docker Compose 定義 jekyll + nginx（或直接用 NAS Web Station）
- 針對不同專案建立多個 Virtual Hosts，對應不同的 _site 目錄
- 加入自動化：Git push 觸發 NAS pull + 重建（Webhooks/CI on NAS）
- 監控與記錄：查看容器 logs、建置時間、錯誤通知

### 關鍵要點清單
- 靜態網站優勢: 靜態 HTML 速度快、安全性高、維運簡單，特別適合 NAS (優先級: 高)
- Jekyll 基礎結構: 透過 _posts、_layouts、_config.yml 生成 _site (優先級: 高)
- Docker 封裝 Jekyll: 使用 jekyll/jekyll:latest 免安裝 Ruby/Gems (優先級: 高)
- Volume 對應: NAS /docker/jekyll 對應容器 /srv/jekyll 以實現檔案熱重建 (優先級: 高)
- Web Station/Nginx 服務: 用 NAS 內建 Web 伺服器提供 _site 靜態檔 (優先級: 高)
- 內外網測試方式: 以容器 4000 埠檢視 Jekyll 內建 server，或用 Virtual Host 網域測試 (優先級: 中)
- 日誌與狀態判讀: Generating... done in X seconds 表示建置完成 (優先級: 中)
- 效能觀察: Synology 入門硬體建置時間可接受（PC 30s vs NAS 42s）(優先級: 中)
- Docs as Code 流程: 以 Git 管理 Markdown，配合 Issues/PR 協作 (優先級: 高)
- 私有部署動機: 不想公開到 GitHub Pages、需內部存取控制 (優先級: 高)
- 檔案系統 vs Git: 檔案系統僅提供異動復原；版本追蹤/分支需 Git (優先級: 高)
- 安全與可靠性: Jekyll 停止不影響服務，Nginx 照常提供既有 _site (優先級: 中)
- 主題與版型客製: 透過 Front Matter 與模版調整版面與中繼資料 (優先級: 中)
- 備份與快照: 善用 NAS 備份、Btrfs/ZFS 快照確保文件安全 (優先級: 中)
- 擴充部署: 未來可加上反向代理、HTTPS、認證與 CI/Webhook 自動重建 (優先級: 低)