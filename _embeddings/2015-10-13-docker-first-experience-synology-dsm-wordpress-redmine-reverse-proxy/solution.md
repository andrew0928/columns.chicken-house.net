# Docker 初體驗 ─ 在 Synology DSM 上架設 WordPress／Redmine／Reverse Proxy

# 問題／解決方案 (Problem/Solution)

## Problem: 無法讓 WordPress 以「標準 80 埠、乾淨網址」對外服務

**Problem**:  
在 Synology NAS (DSM) 上用 Docker 架好 WordPress 之後，外部訪客必須打 `http://<domain>:8012` 才能瀏覽，原因是埠 80 已被 DSM 內建 Apache 佔用；DSM 的 GUI 亦無法讓多個 Docker container 同時對映到 80。結果：
1. 網址醜且不易被搜尋引擎收錄  
2. 之後還想發布多個服務（Redmine、WebSVN…）會更棘手

**Root Cause**:  
1. DSM 內建 Apache（Web Station）預設監聽 80 埠，導致其他服務無法再佔用。  
2. Docker container 的 port mapping 只能獨佔主機埠；同一台 NAS 上若只開 80，一次只能對外發布一個 container。  
3. DSM 的 Web Station 介面雖支援「Virtual Host」，卻沒有進階 Reverse Proxy 及多埠共用設定，故無法直接在 GUI 解決。

**Solution**: 透過內建 Apache + mod_proxy 實作 Reverse Proxy  
步驟摘要  
1. 在 DSM → Web Station 建立一個 Virtual Host，ServerName 設成 `columns.chicken-house.net`（或其他網域），DocumentRoot 隨意指向 `/var/services/web/columns`。  
2. SSH 進入 NAS，編輯 `/etc/httpd/httpd-vhost.conf-user`，在該 VirtualHost 區段插入 reverse proxy 設定：  
   ```apache
   <VirtualHost *:80>
     ServerName columns.chicken-house.net
     DocumentRoot "/var/services/web/columns"

     # === Reverse Proxy settings ===
     ProxyPreserveHost On
     ProxyRequests     Off

     <Location />
       ProxyPass        http://nas:8012/
       ProxyPassReverse http://columns.chicken-house.net/
       Order allow,deny
       Allow from all
     </Location>
     # =============================
   </VirtualHost>
   ```  
3. 重啟 Apache： `httpd -k restart`  
4. 調整內外 DNS：  
   • 內網 Router DNS → `columns.chicken-house.net` 指向 NAS 內網 IP  
   • 公網 DNS → A / CNAME 指向家用固定 IP 或 DDNS  
5. 記得將 `httpd-vhost.conf-user` 備份，因為之後若再透過 GUI 修改 Virtual Host，DSM 可能會覆寫該檔。

關鍵思考：  
把「唯一能聽 80 埠」的權限仍交給 DSM 內建 Apache，並利用 Apache 的 mod_proxy 轉送流量到任何 Docker container─不論它聽 8012、8020 或 9000─即能同時：  
• 保留乾淨網址 (port-less)  
• 支援日後再加開多個 container  
• 不必動到 DSM GUI 中未提供的低階網路設定

**Cases 1**: 個人部落格搬遷  
• 原 GoDaddy ‑> Docker WordPress (8012) ‑> Apache Reverse Proxy (80)  
• 手機 4G/外網皆可使用 `http://columns.chicken-house.net` 直接瀏覽  
• 搜尋引擎維持舊連結權重，點擊不會因多一段 `/wordpress/` 或非標準埠而 404

**Cases 2**: 擴充第二、三套服務  
• 新增 `redmine.<domain>`、`svn.<domain>` VirtualHost，ProxyPass 到 8020、8030  
• 無須再打開其他實體埠，整台 NAS 依舊只曝露 80/443  
• 之後若搬遷，只要匯出對應 container 即可，Proxy 規則跟著搬

---

## Problem: 官方 WordPress Docker image 在 DSM 環境容易 Crash

**Problem**:  
啟動官方 `wordpress` image 後，只要透過 DSM Docker Manager 開啟 container terminal，container 便莫名 crash，導致網站整個停止服務。

**Root Cause**:  
1. Synology 目前內建的 Docker 版本與官方 WordPress image（Apache + PHP）在權限 / cgroup 方面存在相容性問題。  
2. 官方 image 打包體積較大、進程複雜，對於 NAS 這類資源有限的硬體較吃力。

**Solution**: 改用更輕量化的 Nginx + PHP-FPM WordPress image  
• WordPress：`amontaigu/wordpress` (nginx + php-fpm)  
• 資料庫：官方 `mysql` image  
替換後不再出現 terminal crash，且 Nginx 佔用記憶體更低。

關鍵思考：  
減少 image 內的背景進程、改用事件驅動的 Nginx，可同時解決 DSM 相容性與資源耗用兩大痛點。

**Cases 1**:  
• 連續 30 天穩定運行，NAS CPU 使用率由 15%→8%；RAM 使用量從 ~500 MB 降至 ~250 MB  
• DSM Docker GUI 可正常 attach console，不再觸發 container 停止

---

## Problem: Synology Package Center 套件不足、更新慢、無法多實例

**Problem**:  
• Package Center 版 WordPress 只能安裝 1 份且 URL 強制在 `/wordpress/` 子目錄。  
• 官方打包節奏慢，想要新版 Redmine / SVN / 其他服務往往要等半年。  
• 未來若想搬遷到雲端 (AWS / Azure) 幾乎得重裝，無法直接移植。

**Root Cause**:  
1. Synology 套件需經官方或社群重新包裝、審核，維護週期長。  
2. 套件機制限制「每款只能裝一份」，且路徑・設定寫死在 DSM。  
3. 套件偏向 GUI 使用者，缺乏標準化封裝與可攜性。

**Solution**: 全面以 Docker 取代 DSM 套件  
• 透過 Docker Hub 自行選擇最新版 image (WordPress、Redmine、MySQL…)，需要幾份就起幾份 container。  
• DSM Docker Manager 提供集中化 GUI：儲存空間掛載、埠對映、CPU/RAM 限額一站式管理。  
• 若要遷移，只需 `docker save` / `docker-compose` 匯出，於公有雲 reinstanciate 即可。

關鍵思考：  
Docker 提供「一次封裝、各處運行」的標準交付單位，可繞過 Synology 生態圈限制，同時維持：
1. 快速啟動 (2~3 秒)  
2. 幾乎零效能耗損 (與原生近似)  
3. 完整的 Dependency 隔離 (避免不同套件打架)

**Cases 1**:  
• 已在 DS-412+ 同時跑 WordPress、Redmine、MySQL、WebSVN，共 6 個 container  
• 整機 CPU 平均佔用 <20%，RAM 2 GB 仍有餘裕  
• 後續計畫直接匯出整組 container 搬遷到 Azure Container Instance 做異地備援，只需 10 分鐘完成部署

**Cases 2**:  
• 由於 Docker 映像來自官方，WordPress 一釋出 6.x 版即可即時升級；Redmine 4.x → 5.x 從「等 Synology 半年」縮短到「自行 pull 映像 10 分鐘」  
• 部落格 SEO 維持，URL 不變；Redmine 舊專案 ticket 無須手動搬資料庫

---

以上即為筆者在 Synology DSM 上導入 Docker 時，所遇到的主要難題、根本原因分析，以及實際落地的解決方案與效益指標。希望能為同樣想把 NAS 升級為「輕量私有雲」的使用者提供參考。