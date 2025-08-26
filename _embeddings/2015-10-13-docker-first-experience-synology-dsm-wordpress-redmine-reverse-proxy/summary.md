# Docker 初體驗 - Synology DSM 上面架設 WordPress / Redmine / Reverse Proxy

## 摘要提示
- 背景遷移: 作者從自架 PC/Server 轉換到 Synology NAS，尋找低維護成本的服務承載方式。
- DSM 與 Docker: DSM 5.2 引入 Docker，讓 NAS 能以輕量化容器快速部署多種服務。
- 容器選擇: 優先選官方或成熟映像；WordPress 改用 Nginx+PHP-FPM 映像以解決崩潰問題。
- 網站架構: 家中單一對外 80 埠被 DSM 內建 Apache 佔用，需以反向代理對外發布多個服務。
- Reverse Proxy 解法: 以 DSM 內建 Apache 啟用反向代理，將對外域名導向內部 WordPress 容器。
- 具體設定: 透過 Virtual Host 綁定網域，修改 httpd-vhost.conf-user 加入 ProxyPass/ProxyPassReverse。
- 網域與 DNS: 內外網分流設定（家用路由器內 DNS + 公網 DNS/DDNS）確保域名解析正確。
- 操作重點: 調整設定後需重啟 httpd；DSM 介面改動會覆寫設定檔，務必備份。
- Docker 優勢: 可多實例、可移植、管理一致、選擇多，優於 Synology 套件中心單一 WordPress。
- 實務成果: 成功以正常網址對外發布 WordPress，為後續擴充其他容器打下基礎。

## 全文重點
作者原先以自架 PC 兼作檔案與服務伺服器（含 BlogEngine、VisualSVN、Redmine 等），後因不穩定改用 Synology DS-412+。雖然 DSM 套件中心易用，但軟體選擇與更新速度受限，且作者偏好低維護、標準化的方法。DSM 5.2 引入 Docker 後，透過 Docker Hub 可取得大量現成映像，符合 NAS 資源有限、部署需輕量化的需求。實作上，作者計畫以容器化替換 WordPress、Redmine、MySQL、WebSVN 並配置 Reverse Proxy；本文聚焦 WordPress 與反向代理。

在安裝 WordPress 時，作者發現官方映像搭配 DSM Docker 終端機會導致容器崩潰，遂改用 Nginx+PHP-FPM 的 WordPress 映像與 MySQL 官方映像，問題隨即消失。部署完成後，面臨單一對外 80 埠被 DSM 內建 Apache 佔用，且多容器無法同時對映至 80 埠的限制。為提供對外友善網址（非帶埠號），作者採用 Reverse Proxy：由 DSM 內建 Apache 充當反向代理，對外服務 80 埠，並把特定網域的請求轉發至內部容器的對應埠。

步驟為：首先在 DSM Web Station 建立 Virtual Host，綁定域名（如 columns.chicken-house.net），並完成內外網 DNS（內網路由器 DNS 對 NAS 內部 IP，公網 DNS/DDNS 對外 IP）。接著 SSH 登入 NAS，編輯 /etc/httpd/httpd-vhost.conf-user，於對應 VirtualHost 中加入 ProxyPreserveHost、ProxyPass、ProxyPassReverse 與存取允許設定，讓根路徑請求轉至內部 WordPress 容器（如 http://nas:8012/）。儲存後以 httpd -k restart 使設定生效，即可透過正常網址瀏覽 WordPress。需注意 DSM 介面再次調整 Virtual Host 會覆寫設定檔，務必先備份。

最後，作者說明不選用 Synology 套件中心 WordPress 的理由：URL 會多一層路徑、不支援多實例、日後遷移不易、可選映像較少、資源與埠對映等管理彈性不足。以 Docker 可標準化管理儲存掛載、埠對映與資源限制，並便於未來將容器遷移至雲端（Azure/AWS 均支援）。本文提供在 DSM 上以 Docker 建站並透過 Apache 反向代理對外發布的實作經驗，可套用到其他服務，作為 Synology 用戶將 NAS 轉為個人伺服器的實用範例。

## 段落重點
### 前言與背景：從自架 Server 到 NAS 與服務遷移
作者原以自組 PC 負責檔案與多項服務（BlogEngine、VisualSVN、Redmine），後因不穩定改用 Synology NAS。DSM 套件雖易用，但受限於包裝與更新速度，且對慣用 Windows Server 的作者來說調整成本高。核心訴求是維持低維護、可擴充與標準化的服務部署方式，因此尋求更靈活的解決方案。

### DSM 5.2 與 Docker：輕量化虛擬化的契機
DSM 5.2 正式內建 Docker，對資源有限的 NAS 是關鍵優勢。Docker 不需完整 OS，啟動快、資源耗用低，接近原生效能。Docker Hub 生態系豐富，幾乎所有熱門應用皆有現成映像，選擇多於套件中心，有助快速替換與擴充。作者因此規劃以容器化部署 WordPress、Redmine、MySQL、WebSVN 並透過反向代理對外發布。

### 安裝 WordPress 與 MySQL：改用 Nginx 解決不穩定
部署 WordPress+MySQL 屬常規操作，但在 DSM 上開啟官方 WordPress 映像的終端機易導致容器崩潰。作者改用 Nginx+PHP-FPM 的 WordPress 映像（amontaigu/wordpress）及 MySQL 官方映像，成功避開問題。Nginx 以輕量高效著稱，編譯式模組設計更符合 NAS 的資源條件，成為穩定替代方案。

### 需求與瓶頸：單一 80 埠與多服務對外發布
家中網路架構下，對外 80 埠被 DSM 內建 Apache 佔用，容器無法各自對映至 80 埠。若以非常規埠（如 8012）對外，網址不友善且不利 SEO/分享。為同時支援多站點與友善網址，需由單一前端處理 80 埠並分流至內部不同容器，標準作法即為 Reverse Proxy。

### 解法設計：以 DSM 內建 Apache 做 Reverse Proxy
Reverse Proxy 將外部用戶請求轉發至內部服務，可延伸為負載平衡、快取、TLS 終結等。作者沿用 DSM 內建 Apache，啟用 proxy 能力而無須額外安裝。前端 Virtual Host 綁定對外域名，後端則是容器服務埠。此設計保留 DSM 接管 80 埠的優點，同時彈性發布多個站點。

### 實作步驟：Virtual Host、DNS 與 Proxy 設定
先在 DSM Web Station 建立 Virtual Host 並綁定域名（columns.chicken-house.net），完成內外網 DNS（內網路由器 DNS 指向 NAS 內部 IP；公網 DNS/DDNS 指向對外 IP），確認預設 404 頁面可見。再以 SSH 編輯 /etc/httpd/httpd-vhost.conf-user，於對應 VirtualHost 區塊加入 ProxyPreserveHost On、ProxyRequests Off、Location / 中的 ProxyPass 與 ProxyPassReverse（指向 http://nas:8012/ 與對外網域），允許存取，最後 httpd -k restart 套用設定。測試手機 4G 與桌面瀏覽器皆能以正常網址看到 WordPress。

### 注意事項：設定檔備份與被覆寫風險
DSM 介面若再次調整 Web Station 或 Virtual Host，可能覆寫 httpd-vhost.conf-user 內手動加入的反向代理設定，導致服務中斷。實務上需先備份該檔，或以外部檔案包含/自動化腳本維護設定，以降低操作風險並加速恢復。

### 為何不用套件中心 WordPress：限制與擴充性比較
套件中心版 WordPress 會在網址多一層路徑，不利 SEO 與外部連結；且僅能安裝一份，不便多站點管理。相較之下 Docker 可輕鬆多實例、標準化資源與埠對映管理、映像選擇多、且易於日後遷移至雲端（Azure/AWS 皆支援容器執行）。對需要彈性與可移植性的使用者，Docker 方案更具優勢。

### 結語：以 Docker 讓 NAS 成為可擴充的個人伺服器
透過 Docker 與 Apache 反向代理，作者以友善網址成功對外發布 WordPress，並建立可複製到其他服務的模式。此作法在資源有限的 NAS 上兼顧低維護、擴充性與可移植性，為將 NAS 打造成個人伺服器提供實用藍本，後續再新增容器依樣畫葫蘆即可擴展整體服務。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基礎網路概念：IP、Port、NAT、DNS、Virtual Host
   - Linux/UNIX 觀念與 SSH 操作
   - Docker 基礎：image、container、port mapping、volume
   - Web 伺服器與反向代理基本概念：Apache/Nginx、Reverse Proxy、Host header
   - Synology DSM 基本操作：Web Station、套件中心、權限

2. 核心概念：
   - Docker 輕量化虛擬化：以 container 方式快速部署應用（WordPress/MySQL）
   - 服務發布的端口衝突：DSM 佔用 80 導致多站點對外發布困難
   - Reverse Proxy 解決方案：用 DSM 內建 Apache 的 proxy 模組轉發至內部服務
   - Virtual Host 與 DNS 配合：以域名將外部請求導向正確站點
   - 可攜性與可維護性：使用官方/成熟的 Docker image、備份配置、防止 DSM 覆寫

3. 技術依賴：
   - DSM 5.2+ 提供 Docker 套件 → 拉取並運行容器（WordPress with Nginx/PHP-FPM、MySQL official）
   - WordPress 容器依賴 MySQL 容器（網路或連線設定）
   - DSM Web Station 建立 Virtual Host（80）→ Apache httpd 啟用 proxy 把 / 轉發到內部容器端點（如 http://nas:8012）
   - DNS/路由設定：內外網域名均指向正確 IP（內部走內網 IP、外部走對外 IP/DDNS）
   - Apache 設定檔 /etc/httpd/httpd-vhost.conf-user → ProxyPreserveHost/ProxyPass/ProxyPassReverse → httpd -k restart

4. 應用場景：
   - 在 Synology 上同時部署多個網站（WordPress、Redmine 等）並透過單一 80 埠對外
   - 以友善 URL 發布容器服務，避免非標準埠（如 :8012）
   - 後續擴充：SSL 終端、快取、負載平衡皆可由 Reverse Proxy 延伸
   - 容器可攜：未來將服務遷移至雲端（Azure/AWS）或其他主機更容易
   - 避免被動等待 Synology 套件更新，直接使用官方/社群最新版 image

### 學習路徑建議
1. 入門者路徑：
   - 了解 Docker 基礎與 DSM 套件安裝流程
   - 在 DSM 上安裝 Docker，從 Docker Hub 拉取 MySQL official 與 WordPress（Nginx/PHP-FPM）image
   - 使用 DSM Docker 介面完成 port mapping、volume 掛載與環境變數設定（WordPress 對接 MySQL）
   - 基礎 DNS 設定（內網 hosts 或家用路由器 DNS）與瀏覽器連線測試

2. 進階者路徑：
   - DSM Web Station 建立 Virtual Host（指向域名與 80 埠）
   - SSH 連線 DSM，編輯 /etc/httpd/httpd-vhost.conf-user，加入 ProxyPreserveHost、ProxyPass、ProxyPassReverse
   - 重啟 httpd 並測試主機頭轉發與站點正確性（含手機 4G 測試）
   - 瞭解 DSM 可能覆寫自訂設定，建立備份與變更紀錄流程

3. 實戰路徑：
   - 導入多站點：不同域名/子域各對應一個容器端口，由 Apache 反代至對應容器
   - 加上 HTTPS：在 Reverse Proxy 層安裝憑證（可考慮 Let’s Encrypt 套件或手動憑證）
   - 擴充應用：加入 Redmine、WebSVN 等容器，複用同一反代架構
   - 維運：以 DSM Docker 管理資源（CPU/RAM/存儲）、定期備份容器資料卷與 Apache 配置

### 關鍵要點清單
- Docker 輕量化虛擬化：以容器快速部署應用，啟動快、資源占用低（優先級: 高）
- 選擇合適 image：盡量選官方或成熟社群 image（如 MySQL official、Nginx+PHP-FPM 的 WordPress）（優先級: 高）
- Port 80 被占用的解法：用 Reverse Proxy 聚合多服務到單一 80 埠（優先級: 高）
- DSM Web Station + Virtual Host：以域名區分站點，與反代設定配合（優先級: 高）
- Apache 反向代理設定：ProxyPreserveHost、ProxyPass、ProxyPassReverse 的正確用法（優先級: 高）
- 設定檔位置與維護：/etc/httpd/httpd-vhost.conf-user 編輯與備份，防止 DSM 覆寫（優先級: 高）
- 服務端點規劃：容器內部服務使用非標準埠（如 8012），對外僅開放 80（優先級: 中）
- DNS 與路由配置：內外網域名解析一致性（內部走內網、外部走對外 IP/DDNS）（優先級: 中）
- Nginx + PHP-FPM 組合：相較 Apache 更輕量快速，適合 NAS 資源限制（優先級: 中）
- 容器間連線：WordPress 與 MySQL 的連線設定、網路與憑證（優先級: 中）
- DSM Docker 管理：port mapping、volume 掛載、資源限制與監控（優先級: 中）
- HTTPS 延伸：在反代層終止 TLS，集中管理憑證與安全（優先級: 中）
- 可攜性與遷移：容器化讓日後遷移至雲端或他機更容易（優先級: 中）
- 測試與驗證：以不同網路（如手機 4G）測外網可用性與主機頭處理（優先級: 低）
- 套件中心 vs Docker：URL 乾淨度、多實例能力、更新速度與管理彈性比較（優先級: 低）