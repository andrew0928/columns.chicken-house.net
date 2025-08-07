# Docker 初體驗 ─ 在 Synology DSM 上架設 WordPress、Redmine 與 Reverse Proxy

## 摘要提示
- Synology-Docker：DSM 5.2 內建 Docker，為 NAS 帶來輕量虛擬化能力。
- 舊伺服器汰換：作者將家用 PC 伺服器工作量遷入 DS-412+。
- WordPress 搬家：以 Docker 容器取代 GoDaddy 上的 BlogEngine。
- Nginx 取代 Apache：改用 nginx + php-fpm 型 WordPress image 解決 container 當機。
- Port 80 衝突：DSM 的內建 Apache 佔用 80 port，需另尋對外發布方案。
- Reverse Proxy：利用 Apache proxy 模組把外部流量導向內部 8012 埠的 WordPress。
- 實作步驟：建立 Virtual Host、修改 /etc/httpd/httpd-vhost.conf-user、重啟 Apache。
- 注意事項：DSM GUI 重新套用設定會覆寫手動修改，須先行備份。
- Docker 優勢：多版本併存、匯出容易、image 選擇多、資源耗用低。
- 個人伺服器升級：NAS 透過 Docker 搭配 Reverse Proxy，成功取代傳統主機。

## 全文重點
作者原以自組 PC 充當檔案與網站伺服器，因硬體不穩而改購 Synology DS-412+。然而 NAS 上軟體包有限，更新也不及官方版，直到 DSM 5.2 將 Docker 納入，才真正解決部署彈性不足的問題。Docker 不同於傳統 VM，省去 OS 層，啟動迅速且資源佔用低；Docker Hub 上現成 image 更遠勝 Synology Package Center，成為作者將多項服務（WordPress、Redmine、MySQL、WebSVN 等）搬回 NAS 的契機。  
以 WordPress 為例，作者先取官方 MySQL image，再選用 nginx + php-fpm 的 WordPress image 以避開 Synology Docker 介面開終端機導致 container crash 的怪現象。網站本身順利執行後，面臨的新問題是 DSM 內建 Apache 已占用 80 port，容器只能對外開 8012，不便公眾存取。業界慣用解法是架設 Reverse Proxy，讓外部使用者仍以標準 80/443 連線。  
作者遂在 DSM 的 Web Station 先行建立 Virtual Host，綁定自有網域 columns.chicken-house.net，再透過 SSH 修改 /etc/httpd/httpd-vhost.conf-user，於該主機區段插入 ProxyPass、ProxyPassReverse 等設定，將所有 / 路徑請求轉送至 http://nas:8012。重啟 Apache 後，內外網皆可用乾淨網址瀏覽新站。  
此方案還支援多容器、多網域映射，亦可延伸至 HTTPS、快取或負載平衡。作者提醒修改完成後務必備份設定，因為日後只要在 DSM GUI 重新套用 Virtual Host，就會覆寫手動增添的 proxy 區段。  
最後作者比較 Docker 與 Synology 套件中心：Docker 可同時跑多個獨立 WordPress、網址不受 /wordpress 子目錄限制、日後可直接匯出容器搬至雲端，且 Docker Hub 生態系更豐富；加上 DSM 仍保有統一的容器資源管理介面，整體管理與擴充性遠勝原生套件。透過此流程，NAS 已從單純儲存設備升級為具備完整 Web 服務能力的個人伺服器。

## 段落重點
### 1. 前言：從自組 Server 遷移到 NAS
作者原在家中以 Windows Server 與多顆硬碟自建檔案與網站伺服器，後因硬體老舊常當機而改買 Synology NAS。搬遷後雖享受 DSM 套件安裝便利，但因套件數量與更新速度有限，長期仍受侷限，尤其對習慣微軟生態的人更感不便。

### 2. DSM 5.2 整合 Docker 的意義
Synology 在 DSM 5.2 正式支援 Docker，成為輕量級虛擬化解決方案。相較 QNAP 導入完整 VM，Docker 無須額外 OS，啟動只需數秒，幾乎不增額外 CPU/RAM 負荷，特別適合資源有限的家用 NAS。Docker Hub 上包山包海的 image 也補足了 Synology Package 缺口。

### 3. 計畫與 Image 選擇：WordPress、MySQL、Nginx
作者規劃將 WordPress、Redmine、MySQL 等服務全部容器化。安裝 WordPress 時遭遇官方 image 在 DSM Docker 終端機操作會 Crash 的 bug，轉而採用社群版 nginx + php-fpm image；資料庫則使用官方 MySQL image。此改變同時享受 Nginx 輕量與高效特性。

### 4. Port 衝突與 Reverse Proxy 概念
NAS 內建 Apache 佔用 80 port，WordPress 容器只能對外暴露 8012；若直接供訪客使用不僅 URL 醜陋也不利 SEO。解法是部署 Reverse Proxy：由外部連 80，再由代理伺服器轉請求至內網容器，機制與一般 Proxy 相同但方向相反，可附帶負載平衡、快取、SSL 等延伸功能。

### 5. 實作流程：Virtual Host 與 ProxyPass
首先在 DSM Web Station 建立 Virtual Host 綁定網域 columns.chicken-house.net。接著 SSH 連入修改 /etc/httpd/httpd-vhost.conf-user，於指定主機區塊加入 ProxyPreserveHost、ProxyPass、ProxyPassReverse 等指令，把所有 / 請求導向 http://nas:8012。重啟 Apache（httpd -k restart）後，內外網皆可透過標準網址瀏覽 WordPress。需注意 GUI 再次儲存設定會覆寫手動變更，故必須備份。

### 6. Docker 方案優勢與結語
相較 Synology 套件中心版 WordPress，Docker 具備：1) URL 不含多餘子目錄；2) 可同時部署多站點；3) 容器可匯出遷移至雲端；4) Docker Hub 選擇遠多於官方套件；5) 統一資源管理與限制更彈性。作者成功把 NAS 轉型為全功能個人伺服器，下一步僅考慮升級記憶體以容納更多容器。