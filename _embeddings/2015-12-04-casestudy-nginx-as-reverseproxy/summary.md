# CaseStudy: 網站重構─NGINX Reverse Proxy 與文章連結轉址 (Map)

## 摘要提示
- 轉換動機: 從 BlogEngine 移轉到 WordPress，順勢練功 Linux 與 Docker。
- Docker 價值: 透過 Container 免除繁複安裝與設定，快速複製環境。
- 硬體更新: NAS 效能不足，改以舊 NB + Ubuntu Server 取代。
- 架構升級: 前端改用 NGINX Reverse Proxy，後端多個 Container 共用 80 埠。
- URL 轉址: 400 篇 × 6 種格式＝2400 筆舊連結，需一次性 301 對應。
- NGINX Map: 以 map 指令及外部對照檔取代 Apache RewriteMap。
- Volume-Container: 依官方建議將資料獨立至專用 Container，方便備份與搬遷。
- 效能考量: NGINX 本身輕量，配合新硬體後較 Apache+NAS 明顯提升。
- 實作心得: Map 語法精簡但不易懂，需掌握「變數對應」的隱性機制。
- 跨界反思: 從 .NET → Linux 的過程，重點在「架構思維」而非工具本身。

## 全文重點
作者原以 BlogEngine.NET 經營部落格，搬遷至 WordPress 並部署於 Synology NAS 上的 Docker 容器。隨著文章量上升與 Docker 容器增多，Atom-級 NAS 效能成為瓶頸，因此決定改用舊筆電裝 Ubuntu Server，繼續以 Docker 容器方式營運；筆電內建電池順勢充當 UPS，耗電亦低，硬體成本幾乎為零。

新架構延續「反向代理＋多容器」模式，但把前端由 Apache 換成 NGINX。原因一是 Ubuntu Server 不再被 NAS 內建的 httpd 侷限；原因二是 NGINX 在併發與記憶體占用上較優。主要技術挑戰是「舊網址轉新網址」：BlogEngine 產生的 URL 與 WordPress 相異，400 多篇文章又衍生出 6 種路徑樣式，共 2400 種組合，必須確保 SEO 及使用者書籤不失效。先前在 Apache 透過 RewriteMap（靜態 key/value 對照檔）已驗證可行，如今需以 NGINX 重寫。

NIGNX 的 map 機制用兩個變數定義 key 與 value，於行為發生時自動查表並把結果指派給新變數。作者示範先以正則式抽取 slug 置入 $slug，map 區段負責將 $slug 轉為對應的 WordPress 文章 ID 再填入 $slugwpid，最後以 return 301 /?p=$slugwpid 完成永久轉址。對照表放在獨立檔 slugmap.txt，格式為「舊 slug 空格 新 ID;」並可加註解。雖然 NGINX map 還支援萬用字元與正則式，作者以靜態表即可滿足需求；配合硬體升級與 NGINX 的高效能，並未觀察到延遲問題。

資料層方面，採用官方推薦的 Volume-Container，把 MySQL 資料及 WordPress 上傳檔分開管理，未來搬遷或備份更單純。作者亦分享心得：Docker 讓系統部署真正落實 UML Deployment Diagram 的理念，工程師能「按照設計圖」組裝服務，而不再被繁瑣的 OS 安裝與設定拖累。

結語強調跨陣營學習的重要性：微軟新任 CEO Satya Nadella 坦言「Linux is best for Cloud」，.NET Core 也將多平台化；身為長期使用 Microsoft 技術的開發者，投入 Linux、生態系是必經之路。透過本次實作，作者累積了 NGINX、Docker、Volume-Container 與 URL 重寫的經驗，並鼓勵同樣想從 Windows 轉向開放原始碼世界的讀者，從小型且具體的專案切入，邊做邊學效果最佳。

## 段落重點
### 前言：從 Windows 到 Linux 的必要之路
作者自嘲「學另一個陣營是一條不歸路」，指出大型雲端部署離不開 Linux 與開源方案；隨著 .NET Core 跨平台，他開始以自家部落格作為實驗場，學習 Linux、Docker 與 WordPress。安裝設定雖繁瑣，但 Docker 的出現大幅降低門檻，使他能專注在系統架構而非細節。Satya Nadella「Linux is Best for Cloud」的言論，更強化了他跨界的決心。

### 架構演進：從 NAS + Docker 到 Ubuntu Server
原先部落格部署於 Synology NAS（Atom CPU＋2 GB RAM）。因硬體孱弱，多開兩個容器即明顯卡頓；作者遂把舊筆電改裝成 Ubuntu Server，CPU、記憶體雖不頂尖卻已優於 NAS，再加上電池可兼 UPS，成為省錢又實用的私有伺服器。新的 Deployment Diagram 仍採「前端反向代理＋後端多容器」概念，但硬體、OS 與服務皆獨立控制，彈性更高。

### 技術重點一：NGINX 取代 Apache 作 Reverse Proxy
在 NAS 時期，80 埠已被內建 Apache 佔用，故沿用 httpd 作反向代理；改用 Ubuntu 後不再受限，作者選擇 NGINX。理由包含：記憶體輕量、併發能力佳、設定檔 C-like 易讀等。透過 Docker Hub 取得官方 NGINX 映像，僅需少量設定即能攔截外部請求，依 Host 或 URI 轉發到對應的 WordPress、Redmine 等容器。

### 技術重點二：大量舊網址轉址的 Map 實作
最大的挑戰是 BlogEngine 舊網址（.aspx＋slug）要 301 到 WordPress 新網址（/?p=ID）。共 400 篇文章 × 6 種路徑格式＝2400 筆需一次對應，既要 SEO 友善又要維護簡易。Apache 時期以 RewriteMap 搭配純文字對照表已驗證可行，如今在 NGINX 透過 map 指令重寫；流程為：正則式擷取 slug → 指派給 $slug → map 區段自動查表 → 產生 $slugwpid → return 301。對照檔可置於外部並支援註解，維護成本低。

### Volume-Container 與其他效能考量
按照 Docker 官方建議，作者新增 Volume-Container 專責資料與上傳檔，使資料與應用解耦，後續備份、搬家只需搬 Volume 即可。雖然 NGINX map 支援萬用字與 regex，可能無法像 Apache 將表編譯成二進位 Hash，但在 400 筆×查詢量下並無明顯延遲；加上新硬體與 NGINX 的高效能，整體回應速度優於 NAS 時代。

### 結語：跨界學習的架構思維
透過本次遷移，作者不僅掌握了 NGINX Map 與 Volume-Container，也體會到 Docker 讓 UML 部署圖終於落地——架構師的構想能被工程師迅速實踐。而從 Microsoft 陣營跨向 Linux 的核心價值，在於理解架構與流程，工具只是手段；期盼分享能為同樣從 Windows 轉至開源世界的讀者提供實務指引與信心。