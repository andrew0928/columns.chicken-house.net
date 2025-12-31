---
layout: synthesis
title: "Running Jekyll on NAS - 高效率的新選擇
title: Deploy Windows Containers on Nano Server"
synthesis_type: faq
source_post: /2016/09/20/jekyll-on-nas/
redirect_from:
  - /2016/09/20/jekyll-on-nas/faq/
postid: 2016-09-20-jekyll-on-nas
---

# Running Jekyll on NAS - 高效率的新選擇

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Jekyll？
- A簡: Jekyll 是以 Markdown/模板生成靜態網站的開源工具，支援部落格結構與自動重建。
- A詳: Jekyll 是一套以 Ruby 開發的靜態網站產生器，將 Markdown、Liquid 模板與 Front Matter 組合，輸出純 HTML/CSS/JS。它特別適合部落格與文件網站，具備固定的目錄結構（如 _posts、_layouts）、支援標籤與分類，並能監控檔案變更自動重建。因輸出為靜態檔案，部署更簡單、安全、快速，亦可搭配 GitHub Pages 或自架伺服器使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1

A-Q2: 什麼是靜態網站產生器？
- A簡: 將原始內容與模板編譯為純靜態頁面的工具，部署簡單、速度快、安全性高。
- A詳: 靜態網站產生器（SSG）將 Markdown 等原始內容與佈局模板結合，預先產生可直接由 Web 伺服器提供的 HTML 檔。與動態 CMS 相比，不需資料庫與伺服端運算，降低攻擊面與運行成本，響應更快。典型用途包括部落格、文件、產品說明書與知識庫，Jekyll、Hugo 即是常見代表。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q6, A-Q7

A-Q3: 什麼是 GitHub Pages？與 Jekyll 的關係？
- A簡: GitHub Pages 提供原生 Jekyll 編譯與托管，push 即自動發布靜態網站。
- A詳: GitHub Pages 是 GitHub 提供的靜態網站託管服務，對指定分支/目錄支援內建 Jekyll 編譯。使用者只需將內容推送至儲存庫，GitHub 即自動建置並發布。它特別適合公開部落格與開源文件。然而若有私密性或自主管理考量，亦可改在 NAS 上自建 Jekyll 流程達成。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q15, B-Q12

A-Q4: 什麼是 NAS？為何拿來架網站？
- A簡: NAS 是網路儲存設備，常在線、低功耗，適合作為靜態網站的穩定主機。
- A詳: NAS（Network Attached Storage）提供集中式檔案儲存與分享，具備長時運行、低功耗、易備份等特性。對靜態網站而言，NAS 搭配輕量 Web 伺服器可提供穩定、高效、低維護成本的發布環境。若 NAS 支援 Docker，更能以容器快速部署 Jekyll 的建置與監控流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q5, C-Q1

A-Q5: 為什麼在 NAS 上跑 Jekyll？
- A簡: 兼顧效能、私密性與維運簡易，省資源又安全，適合內部文件與部落格。
- A詳: 在 NAS 上執行 Jekyll，可保留內容私密性（不公開到雲端）、享受靜態網站的高速與高安全性，並利用 NAS 的長時在線特性。以 Docker 部署 Jekyll 只在建置時消耗資源，平時由 NAS 的 Web Station/Nginx 直接服務靜態檔，可靠且維護成本低，適用於團隊文件、內網站點與個人站。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q15, B-Q2, C-Q4

A-Q6: 靜態網站與 WordPress 等動態網站差異？
- A簡: 靜態預生 HTML，無資料庫；動態即時運算，功能彈性高但負擔與風險較大。
- A詳: 靜態網站於建置階段產生 HTML，發布時僅提供檔案，速度快、資源占用低、安全性高。動態網站（如 WordPress）需伺服器即時計算與資料庫讀寫，功能強大但效能較受限、維護與安全風險較高。在 NAS 上，靜態網站更能充分發揮低功耗硬體的性能優勢。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q7, B-Q10

A-Q7: 使用靜態網站在 NAS 的核心價值是什麼？
- A簡: 快速、安全、穩定、易維護，以極少資源提供優質瀏覽體驗。
- A詳: 靜態網站在 NAS 上運作的價值包含：瀏覽極快（無動態運算）、攻擊面小（無資料庫/後端程式）、穩定（Jekyll 掛了仍能由 Web 伺服器服務舊版檔案）、維護簡（改文即重建）。對效能有限的 NAS，這種模式能以最低成本達成良好用戶體驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q5, B-Q10

A-Q8: 什麼是 Blogging as Code？
- A簡: 以程式碼思維管理部落格，用版本控制與自動化部署文件。
- A詳: Blogging as Code 強調用開發流程管理內容：Markdown 撰寫、前置欄位定義中繼資料、Git 版控追蹤變更、建置系統自動產出網站。在 NAS 上以 Docker 跑 Jekyll，配合 Git 或檔案系統備份，能將文章與文件視為程式碼般維運，確保可追溯、可協作與可自動部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q11, B-Q12, C-Q8

A-Q9: 為何用 Markdown 撰寫文件？
- A簡: 語法簡潔、可讀可寫、利於版控，與 Jekyll 無縫整合成網頁。
- A詳: Markdown 以簡潔標記撰寫段落、標題、清單與程式碼，易讀易寫，學習成本低。文本純文字特性非常適合 Git 版控，比二進位的 Word 文件更易追蹤差異。Jekyll 可直接將 Markdown 轉成 HTML，輔以模板與樣式形成一致的文件網站。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q1, C-Q3

A-Q10: 什麼是 Jekyll Front Matter？
- A簡: 檔頭以 YAML 定義標題、作者、日期等中繼資料，驅動模板與功能。
- A詳: Front Matter 是每篇內容檔案頂端以 --- 包裹的 YAML 區段，用於描述標題、描述、作者、日期、分類、標籤等。Jekyll 依此決定路由、模板套用與清單呈現。MSDN 文件亦使用相似欄位，顯示業界將中繼資料與內容分離的實務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, A-Q11, C-Q3

A-Q11: Jekyll 作為開發文件管理系統的優勢？
- A簡: 與程式碼共版控、可自動部署、結構一致，利於協作與審核。
- A詳: 開發文件來源常見兩種：由程式註解產生的 API 文件，以及需手寫的規格/操作文件。將後者以 Markdown 撰寫，與程式碼同 repo 管理，透過 Jekyll 產生網站並自動發布，可維持版本一致、審核制度與回溯能力。大型文件網站（如 MSDN 某些頁面）亦採相同思路。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q12, B-Q12

A-Q12: API 註解文件與手工文件有何不同？
- A簡: 前者由註解工具生成；後者以 Markdown 手寫，適用規格與指南。
- A詳: API 文件可由程式語言註解（如 C# 的 ///）透過工具自動產生，適合類別庫/介面說明。安裝指南、規格、操作手冊等需人工維護，適合以 Markdown 撰寫，由 Jekyll 統一呈現。兩者可並行：自動生成 API，手工撰寫其他文件，共存於同網站。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q9, B-Q1

A-Q13: Docker 在此架構中扮演什麼角色？
- A簡: 提供可攜的 Jekyll 執行環境，透過 Volume 將 NAS 目錄掛載建置。
- A詳: 使用官方 jekyll/jekyll 映像在 NAS 上以容器運行，免去本機安裝 Ruby 與套件。將 NAS 的 /docker/jekyll 映射到容器內 /srv/jekyll，容器監控該路徑內容變化並重建輸出至 _site。容器化帶來環境一致性、部署簡化與維護便利。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, C-Q1, C-Q2

A-Q14: 為何選用 NAS 內建 Web Station 而非 Jekyll 內建伺服器？
- A簡: 專業 Web 伺服器效能更佳、更穩定，Jekyll 只負責建置即可。
- A詳: Jekyll 內建伺服器適合本機測試；正式服務建議交由 NAS 內建的 Web Station（如 Nginx）處理，具較高性能與可靠性。即便 Jekyll 未運行，已建置的靜態頁仍由 Web 伺服器穩定提供，減少單點故障風險，強化整體可用性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q4, C-Q10

A-Q15: 在 NAS 上自架與放 GitHub 上的考量差異？
- A簡: 自架重私密與掌控；GitHub Pages 重公開、零維運與社群協作。
- A詳: 將站點放 GitHub Pages 享受自動建置與全球 CDN，但內容為公開或付費私有庫。自架在 NAS 可完整掌控訪問權限與部署節奏，適合內網文件或不公開的專案。依需求權衡私密性、維運成本、可用性與協作模式來選擇。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q5, C-Q8

A-Q16: 在 NAS 上跑 Jekyll 的效能是否足夠？
- A簡: 實測低階 CPU 亦可於數十秒完成建置，瀏覽端幾乎即時響應。
- A詳: 文中比較桌機 i7 與 NAS Atom，建置時間分別約 30 秒與 42 秒，差異可接受；而瀏覽端因為是純靜態檔，載入體感「飛快」。對部落格與文件站而言，NAS 規格通常足以應付日常編輯與發布需求。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q13, D-Q6

---

### Q&A 類別 B: 技術原理類

B-Q1: Jekyll 的運作流程如何？
- A簡: 讀取內容與配置，套用模板輸出至 _site，監控變更自動重建。
- A詳: 原理是從專案根目錄讀取 _config.yml、_posts、頁面與資產，解析 Front Matter 與 Markdown，透過 Liquid 模板渲染，最後輸出靜態檔至 _site。啟用監控後，檔案變更會觸發增量或完整重建。核心組件含解析器、模板引擎、檔案觀察器與輸出器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q10, B-Q8

B-Q2: 官方 jekyll/jekyll Docker 映像如何工作？
- A簡: 內建 Jekyll 與工具，掛載工作目錄，執行 serve/build 與監控。
- A詳: 影像預裝 Ruby、Jekyll 與必要工具。將 NAS 目錄映射為 /srv/jekyll 後，容器內以 jekyll serve/watch 監控該路徑，內容變更觸發建置至 _site。容器抽象出環境差異，確保各 NAS 機型可用同一流程建置與測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q2, D-Q7

B-Q3: Volume 映射 /docker/jekyll ↔ /srv/jekyll 的原理？
- A簡: 透過 Docker bind mount 將 NAS 目錄映射進容器工作路徑。
- A詳: 建立容器時設定 Volume，將主機路径 /docker/jekyll 綁定為容器內 /srv/jekyll。容器內對 /srv/jekyll 的讀寫即反映到 NAS 檔案系統，達到持久化與即時共享。關鍵是確保正確路徑與權限，以便建置輸出與 Web Station 讀取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q4, D-Q9

B-Q4: Auto-regeneration 機制如何偵測異動？
- A簡: 以檔案監聽偵測內容變更，觸發增量或完整重建。
- A詳: Jekyll 啟動監控後使用檔案系統監聽器觀察 /srv/jekyll 底下的檔案/目錄變更。當 Markdown、模板或設定調整時，觸發重建流程，重算受影響頁面並輸出至 _site。日誌會顯示 Generating... done，表示完成建置與刷新。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q6, D-Q4

B-Q5: Web Station 與 Nginx 如何服務靜態檔？
- A簡: Nginx 直接讀取 _site 目錄檔案，零後端運算，並處理快取與壓縮。
- A詳: Web Station 配置虛擬主機的文件根目錄指向 /docker/jekyll/_site。Nginx 接收請求後，直接回傳對應的靜態檔，並可啟用 gzip、快取、索引等功能。此模式避免 JIT 運算與資料庫查詢，提供穩定且高速的回應。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q4, C-Q10

B-Q6: 容器 4000 埠與主機埠對應機制？
- A簡: 透過 Port Mapping 將容器 4000 對應到主機任一可用埠供區網測試。
- A詳: jekyll serve 預設監聽容器內 4000 埠。建立容器時設定主機埠映射，例：host:4000→container:4000。Synology 會顯示實際對應埠，讓你以 http://NAS_IP:host_port 測試。正式發布仍建議用 Web Station。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q2, A-Q14

B-Q7: 首次啟動為何需要安裝 Ruby gems？
- A簡: 初次執行需拉取相依套件，完成後才可完整建置站點。
- A詳: Jekyll 與主題/外掛依賴多個 Ruby gems。首次啟動容器會安裝或更新必要套件，日誌會顯示進度。此過程受網路與套件快取影響，可能需數分鐘。完成後後續建置會快許多。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q6, D-Q5

B-Q8: 目錄結構 _posts、_site、_config.yml 各自用途？
- A簡: _posts 放文章；_site 為輸出；_config.yml 管理全域設定。
- A詳: _posts 用於部落格文章（含日期命名與 Front Matter）；_site 是 Jekyll 輸出目的地，供 Web 伺服器直接讀取；_config.yml 包含站點名稱、路徑、外掛、排除清單等設定。正確安排結構能讓 Jekyll 正確路由與渲染。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q10, C-Q3

B-Q9: 在 NAS 上部署的安全性為何較單純？
- A簡: 靜態檔無後端邏輯與資料庫，攻擊面小，配置更直觀。
- A詳: 靜態網站不執行伺服端腳本，不需 DB 連線，避免 SQL 注入、程式漏洞等動態攻擊向量。Nginx 僅提供檔案，安全控管重心在檔案權限、HTTPS 與存取控制，相較動態 CMS 明顯簡化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, D-Q10

B-Q10: 為何靜態網站在低規硬體也能很快？
- A簡: 回應僅為檔案傳送，CPU 幾乎不計算，I/O 成主要瓶頸。
- A詳: 靜態回應省去模板渲染、框架啟動與 DB 查詢。伺服器只需讀取並傳送檔案，受益於檔案系統快取與網路優化，即使在低階 CPU 和少量 RAM 的 NAS 上仍有極佳體感。建置階段較耗時，但不影響瀏覽。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q13, D-Q8

B-Q11: Git 版控與檔案系統快照有何差異？
- A簡: Git 可追蹤變更與分支；快照偏備援還原，難細粒度協作。
- A詳: Git 提供提交歷史、分支、合併與差異比對，利於協作與審核；而 Btrfs/ZFS 快照偏向時間點還原與災備，對於細微內容變更追蹤較弱。文件編輯建議以 Git 管版，另搭配 NAS 快照作最後一道備援。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, C-Q8, D-Q1

B-Q12: 建置流程如何對應 CI/CD？
- A簡: 編輯→提交→建置→發布，與程式交付流程同構，易自動化。
- A詳: 雖在 NAS 上未必使用雲端 CI，但概念上相同：內容變更即觸發 Jekyll 建置並發布至 _site。也可將 Git 提交當事件，透過 hooks 觸發 NAS pull + build。這使文件發布可預測、可回溯且可審核。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, A-Q11, C-Q8

B-Q13: 建置時間的瓶頸通常在哪？
- A簡: 受檔案數量、I/O 與外掛影響；CPU 次之，首次安裝最久。
- A詳: 大量文章與複雜模板會增加渲染時間；磁碟 I/O 與目錄掃描亦佔比高。CPU 差異會影響總時間，但靜態渲染多半非完全 CPU 密集。首次安裝 gems 會是最久的一次，之後建置會顯著縮短。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q7, D-Q6

B-Q14: 多虛擬主機與目錄對應如何運作？
- A簡: Web Station 映射不同網域/埠至不同根目錄，如 _site。
- A詳: 在 NAS 的 Web Station 可建立多個虛擬主機，為每個網域或埠設定對應的網站根目錄。此案將某網域對應 /docker/jekyll/_site，使不同專案或環境各自獨立，利於隔離與維運。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q3, A-Q14

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Synology 上安裝 jekyll/jekyll 映像？
- A簡: 打開 Docker→Registry 搜尋 jekyll/jekyll:latest，下載並準備建立容器。
- A詳: 步驟：1) 在 DSM 開啟 Docker；2) 進入 Registry，搜尋 jekyll/jekyll，選擇 jekyll/jekyll:latest 下載；3) 下載完成後於 Image 建立容器。命令版可用：docker pull jekyll/jekyll:latest。注意保持 NAS 有足夠儲存、網路暢通，首次拉取需等待。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q7, D-Q5

C-Q2: 如何建立 Container 並設定 Volume 映射？
- A簡: 建立容器時將 /docker/jekyll 綁定到 /srv/jekyll，其餘採預設。
- A詳: 步驟：1) Docker→Image 選 jekyll/jekyll→Launch；2) 設定 Volume：Host 路徑 /docker/jekyll 綁至 Container 路徑 /srv/jekyll；3) Port Mapping 可保留預設或指定 Host:4000→Container:4000；4) 啟動。CLI 範例：docker run -p 4000:4000 -v /docker/jekyll:/srv/jekyll jekyll/jekyll jekyll serve。注意：先建立 /docker/jekyll 目錄並賦予讀寫權限。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q6, D-Q9

C-Q3: 如何把現有 Jekyll 樣板與內容搬到 NAS？
- A簡: 將站點模板與 Markdown 檔複製至 /docker/jekyll，文章放 _posts。
- A詳: 步驟：1) 於本機準備好 Jekyll 專案或主題；2) 透過 SMB/SFTP 或 File Station 將所有檔案複製到 NAS:/docker/jekyll；3) 確認 _posts、_config.yml、_layouts 等目錄存在；4) 新文章以 Markdown 與 Front Matter 編寫，放入 _posts。注意：避免將 _site 複製進來，讓容器自行生成。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q9, D-Q4

C-Q4: 如何設定 Web Station 虛擬主機指向 _site？
- A簡: Web Station 建立虛擬主機，根目錄設定為 /docker/jekyll/_site，選 Nginx。
- A詳: 步驟：1) 開啟 Web Station→虛擬主機→建立；2) 選擇主機類型（網域或埠）；3) 文件根目錄指向 /docker/jekyll/_site；4) Web 伺服器選 Nginx；5) 套用。最佳實踐：針對產出目錄唯讀、啟用 gzip、設定正確的索引檔。完成後以 http://你的網域 測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q5, D-Q3

C-Q5: 如何用容器內建 Jekyll 伺服器在區網測試？
- A簡: 查詢容器 4000 埠對應的主機埠，瀏覽 http://NAS_IP:主機埠。
- A詳: 步驟：1) 在 Docker→Container 檢視埠映射；2) 若為 4000:4000，瀏覽 http://NAS_IP:4000；3) 內容變更後觀察即時重建與刷新。注意：此伺服器僅用於測試，正式發布仍以 Web Station 對外服務，避免單點風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q2, A-Q14

C-Q6: 如何觀察容器日誌確認已完成建置？
- A簡: 檢視 Docker 日誌有 Generating... done 與 Server running 訊息。
- A詳: 步驟：1) Docker→Container→選擇容器→Logs；2) 看到 Configuration file...、Generating... done in X seconds、Auto-regeneration enabled、Server running... 表示完成；3) 若長時間無進度，檢查網路或套件安裝。最佳實踐：首次啟動耐心等待，之後建置會更快。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q7, D-Q5

C-Q7: 如何啟用增量建置加速重建？
- A簡: 在啟動命令加入 --incremental，僅重建變動頁面縮短時間。
- A詳: 作法：修改容器啟動命令為 jekyll serve --incremental（UI 可於 Command 欄設定）。CLI 範例：docker run ... jekyll/jekyll jekyll serve --incremental。注意：增量模式有時需完整重建以清除舊輸出，定期停/啟容器或手動 jekyll build 保持乾淨輸出。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q4, B-Q13, D-Q6

C-Q8: 如何結合 Git 版控管理 Markdown 文件？
- A簡: 將 /docker/jekyll 作為 Git 工作目錄，提交變更即可觸發重建。
- A詳: 步驟：1) 在本機 clone 專案，編輯 Markdown 與配置；2) push 到遠端；3) NAS 可透過 Git pull 同步至 /docker/jekyll；4) 容器監測到變更即重建。也可將 /docker/jekyll 初始化為 repo。最佳實踐：使用分支與 PR 審核，搭配 NAS 備份快照做雙重保護。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q12, A-Q8

C-Q9: 如何規劃資料夾結構與權限以利維運？
- A簡: 分離原始與輸出，賦予容器與 Web 伺服器適當讀寫權限。
- A詳: 建議：/docker/jekyll 存原始內容，_site 為輸出；將寫入權限授予容器進程，Web Station 讀取 _site 可為唯讀。避免在 _site 手動修改，所有變更由原始內容產出。最佳實踐：定期備份 /docker/jekyll，排除 _site 避免重複備份。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q5, D-Q9

C-Q10: 如何切換或比較 Nginx 與 Jekyll 伺服器？
- A簡: 測試用 Jekyll，正式用 Nginx；前者易預覽，後者性能穩定。
- A詳: Jekyll 伺服器：啟動快、適合本地/區網預覽；Nginx：生產等級、可加壓縮/快取與多站管理。切換作法：保留兩者並行，Jekyll 用於內部測試埠，正式網域由 Web Station 指向 _site。注意：避免對外暴露測試埠，並以 Nginx 為主。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q5, B-Q6

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 無法在 Synology 找到 Docker 套件怎麼辦？
- A簡: 確認機型/DSM 版本是否支援；不支援可改用外部建置後同步。
- A詳: 症狀：套件中心無 Docker。可能原因：機型或 DSM 版本不支援。解法：1) 檢查官方支援清單；2) 可於可用電腦上建置 _site，再以 NAS 只當靜態檔伺服；3) 或改用其他容器方案。預防：選購前確認支援，規劃機型升級路線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q11, C-Q4

D-Q2: 連不到測試埠 4000/對應主機埠？
- A簡: 檢查埠映射、容器狀態與防火牆；確認訪問 http://NAS_IP:主機埠。
- A詳: 症狀：瀏覽器無法載入測試頁。原因：未映射埠、容器未啟動、網路阻擋。解法：1) 查看容器 Port Mapping；2) 重啟容器；3) 關閉防火牆或開放埠；4) 確認用主機映射埠而非 4000 原生埠。預防：建立容器時明確指定埠映射。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q5, C-Q2

D-Q3: Web Station 出現 403/404 或空白頁？
- A簡: 多為根目錄設定錯誤或未生成輸出，修正至 /docker/jekyll/_site。
- A詳: 症狀：403 禁止或 404 找不到。原因：虛擬主機根目錄設錯、_site 未生成、權限不足。解法：1) 確認根目錄指向 /docker/jekyll/_site；2) 查看容器日誌是否完成建置；3) 檢查權限。預防：建立嚴謹的資料夾結構與啟動檢查清單。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q6, D-Q9

D-Q4: 內容有更新但網站沒變？
- A簡: 可能未觸發重建或指向舊輸出；檢查監控與日誌。
- A詳: 症狀：修改 Markdown 後前端未更新。原因：監控未啟動、容器已停止、瀏覽器快取、Web Station 指到舊目錄。解法：1) 查看容器狀態與日誌 Generating... done；2) 清除快取；3) 確認 _site 新時間戳；4) 重啟容器。預防：固定啟動方式與監控參數。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q6, C-Q4

D-Q5: 初次啟動很久或卡住？
- A簡: 多在安裝 gems，需等待或檢查網路；完成後會快很多。
- A詳: 症狀：容器啟動久無回應。原因：首次下載/安裝 gems、網路慢。解法：1) 查看日誌進度；2) 確認 DNS/網路通暢；3) 重新啟動嘗試；4) 改用離峰時段。預防：提前拉映像與快取套件，確保 NAS 穩定供電與網路。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q1, C-Q6

D-Q6: 建置時間過長如何改善？
- A簡: 啟用增量建置、精簡外掛與檔案、優化 I/O 與權限。
- A詳: 症狀：每次變更建置很慢。原因：檔案多、模板複雜、I/O 慢。解法：1) 啟用 --incremental；2) 排除不必要目錄（_config.yml exclude）；3) 確保 NAS 磁碟健康；4) 降低外掛數量。預防：良好內容結構與定期健康檢查。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q7, A-Q16

D-Q7: 容器啟動就退出或持續重啟？
- A簡: 多為命令/路徑錯誤或資料夾不存在，修正啟動參數與目錄。
- A詳: 症狀：容器無法持續運行。原因：啟動命令缺失、目錄未映射、權限不足。解法：1) 檢查 Volume 映射 /docker/jekyll→/srv/jekyll；2) 確認啟動命令含 jekyll serve；3) 建立目錄並賦權限；4) 查看日誌錯誤訊息。預防：以模板建立標準化設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q3, B-Q2

D-Q8: 網站快慢不一或突然很慢？
- A簡: 與 NAS I/O、網路或併發負載相關；檢查硬碟與網路狀態。
- A詳: 症狀：回應時快時慢。原因：磁碟負載、同步任務佔用 I/O、網路擁塞。解法：1) 檢視 NAS 資源監控；2) 避開繁忙排程時段；3) 啟用 Nginx 壓縮快取；4) 使用有線網路。預防：規劃備份/同步時程，分流靜態資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q4, B-Q5

D-Q9: 權限問題導致 _site 無法寫入？
- A簡: 調整 /docker/jekyll 權限給容器用戶，確保可寫入輸出目錄。
- A詳: 症狀：日誌顯示寫入失敗或 _site 未更新。原因：目錄權限不足。解法：1) 在 NAS 設定該共享資料夾為可讀寫；2) 調整擁有者與群組；3) 測試手動寫入。預防：建立專用帳號與群組，最小權限原則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q9, D-Q3

D-Q10: 需要私密發布，避免被外網看到？
- A簡: 僅內網 DNS/埠開放，或設存取控制；GitHub 改自架更可控。
- A詳: 症狀：希望限定內部瀏覽。解法：1) 僅在內網解析網域；2) 不開放外網埠；3) Nginx 加上基本驗證；4) 使用 NAS 存取控制與防火牆。預防：規劃網段隔離與權限模型，自架 NAS 相較公開 GitHub Pages 更易控管私密性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q15, B-Q9

---

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Jekyll？
    - A-Q2: 什麼是靜態網站產生器？
    - A-Q3: 什麼是 GitHub Pages？與 Jekyll 的關係？
    - A-Q4: 什麼是 NAS？為何拿來架網站？
    - A-Q5: 為什麼在 NAS 上跑 Jekyll？
    - A-Q6: 靜態網站與 WordPress 等動態網站差異？
    - A-Q7: 使用靜態網站在 NAS 的核心價值是什麼？
    - A-Q9: 為何用 Markdown 撰寫文件？
    - A-Q10: 什麼是 Jekyll Front Matter？
    - B-Q5: Web Station 與 Nginx 如何服務靜態檔？
    - B-Q6: 容器 4000 埠與主機埠對應機制？
    - C-Q1: 如何在 Synology 上安裝 jekyll/jekyll 映像？
    - C-Q2: 如何建立 Container 並設定 Volume 映射？
    - C-Q4: 如何設定 Web Station 虛擬主機指向 _site？
    - C-Q6: 如何觀察容器日誌確認已完成建置？

- 中級者：建議學習哪 20 題
    - A-Q8: 什麼是 Blogging as Code？
    - A-Q11: Jekyll 作為開發文件管理系統的優勢？
    - A-Q12: API 註解文件與手工文件有何不同？
    - A-Q14: 為何選用 Web Station 而非 Jekyll 伺服器？
    - A-Q15: 在 NAS 上自架與 GitHub 的考量差異？
    - A-Q16: 在 NAS 上跑 Jekyll 的效能是否足夠？
    - B-Q1: Jekyll 的運作流程如何？
    - B-Q2: 官方 jekyll/jekyll Docker 映像如何工作？
    - B-Q3: Volume 映射的原理？
    - B-Q4: Auto-regeneration 機制如何偵測異動？
    - B-Q7: 首次啟動為何需要安裝 Ruby gems？
    - B-Q8: 目錄結構用途？
    - B-Q9: 在 NAS 上部署的安全性為何較單純？
    - B-Q10: 為何靜態網站在低規硬體也能很快？
    - C-Q3: 如何搬移樣板與內容？
    - C-Q5: 如何用容器內建伺服器測試？
    - C-Q8: 如何結合 Git 版控？
    - D-Q2: 連不到測試埠怎麼辦？
    - D-Q3: Web Station 403/404 或空白頁？
    - D-Q4: 內容更新網站沒變如何排查？

- 高級者：建議關注哪 15 題
    - B-Q11: Git 版控與檔案系統快照差異？
    - B-Q12: 建置流程如何對應 CI/CD？
    - B-Q13: 建置時間的瓶頸在哪？
    - B-Q14: 多虛擬主機與目錄對應原理？
    - C-Q7: 如何啟用增量建置加速？
    - C-Q9: 資料夾結構與權限規劃？
    - C-Q10: 切換或比較 Nginx 與 Jekyll 伺服器？
    - D-Q1: NAS 無 Docker 的替代方案？
    - D-Q5: 初次啟動很久或卡住？
    - D-Q6: 建置時間過長的改善策略？
    - D-Q7: 容器啟動就退出或重啟？
    - D-Q8: 網站快慢不一的排查？
    - D-Q9: 權限問題導致 _site 無法寫入？
    - D-Q10: 私密發布的做法？
    - A-Q13: Docker 在此架構中的角色？