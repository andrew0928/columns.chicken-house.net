## Case #1: 用 Docker 補齊 DSM 套件缺口與更新時滯

### Problem Statement（問題陳述）
業務場景：家庭/個人 NAS（Synology DS-412+）需同時承載多個網站與協作服務（Blog、Redmine、WebSVN 等）。DSM 套件中心可裝的應用有限且更新慢，很多想要的服務沒有官方套件或維護落後，且作者長期使用 Windows Server，對 Linux 手工改造不熟悉，想用「標準方式」快速落地服務。
技術挑戰：在 DSM 上取得足夠的應用選擇與更快的更新節奏，避免手工編譯與不易維護的改機。
影響範圍：上線速度慢、維運風險高、服務版本落後與安全風險、難以擴充新服務。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. DSM 套件中心供應數量有限且更新頻率低，常落後上游社群與官方。
2. 非套件化應用需自行編譯或繁雜設定，對不熟 Linux 的管理者門檻高。
3. 以 NAS 硬體資源運行 VM 成本高，不適合大量部署。
深層原因：
- 架構層面：單一平台單一套件來源，生態系與可用性受限。
- 技術層面：傳統 VM 虛擬化開銷大，不適合 NAS 的 CPU/RAM。
- 流程層面：升級與維護依賴套件打包流程，與上游脫節。

### Solution Design（解決方案設計）
解決策略：在 DSM 5.2 安裝 Docker，改以容器化交付應用；盡量選擇 Docker Hub 官方/權威映像；以容器為單位進行版本升級與回滾，避開 DSM 套件的更新時滯與可用性限制。

實施步驟：
1. 安裝 Docker 並驗證
- 實作細節：在 DSM 套件中心安裝 Docker 套件後，以 ssh 登入驗證 docker info
- 所需資源：DSM 5.2、Docker 套件、SSH
- 預估時間：0.5 小時
2. 以官方映像部署常用服務
- 實作細節：優先選官方/verified publisher 映像；建立本地 volumes 保存資料
- 所需資源：Docker Hub、儲存空間
- 預估時間：1 小時

關鍵程式碼/設定：
```sh
# 驗證 Docker 安裝
docker version
docker info

# 範例：拉取官方 MySQL 映像
docker pull mysql:8.0
```

實際案例：在 DS-412+ 安裝 Docker，從 Hub 拉取 MySQL、WordPress 容器替代 DSM 套件。
實作環境：Synology DS-412+、DSM 5.2、Docker 套件
實測數據：
改善前：可用應用少、版本落後；新服務導入需手工。
改善後：Docker Hub 可用服務數大幅增加；映像啟動約 2-3 秒。
改善幅度：上線速度顯著縮短；可用應用種類數量級提升（質性指標）。

Learning Points（學習要點）
核心知識點：
- 容器與套件/VM 的差異
- Docker Hub 生態與映像選型
- 容器化帶來的升級與回滾優勢
技能要求：
必備技能：DSM 操作、SSH、基本 Docker CLI
進階技能：映像安全審視、版本策略、資料卷管理
延伸思考：
- 可套用於任何 DSM 不提供或更新慢的應用
- 需關注映像安全與可信來源
- 引入 Compose 以編排多容器

Practice Exercise（練習題）
基礎練習：安裝 Docker 並拉取 hello-world 映像
進階練習：拉取官方 Nginx 映像，掛載靜態頁面 Volume
專案練習：以 Docker 取代一個現有 DSM 套件（如 Git、Wiki）

Assessment Criteria（評估標準）
功能完整性（40%）：能在 DSM 上成功部署容器並啟動
程式碼品質（30%）：命令與配置可重現、可讀
效能優化（20%）：合理使用 volume、資源限制
創新性（10%）：映像選型與版本策略合理


## Case #2: 官方 WordPress 映像在 DSM 開終端機即崩潰，改用 Nginx+PHP-FPM 映像

### Problem Statement（問題陳述）
業務場景：欲在 NAS 上以 Docker 佈署 WordPress + MySQL。使用官方 WordPress 映像時，只要從 DSM Docker 管理員打開該容器的終端機就會導致容器整個崩潰，影響使用與管理。
技術挑戰：容器在 DSM 的終端機操作引發不穩定，需快速找到穩定替代映像。
影響範圍：WordPress 容器可用性、維運操作（終端機）受限。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 官方 WP 映像與 DSM Docker 終端機交互不相容，觸發容器崩潰。
2. WordPress 映像內部進程控制或 TTY 配置與 DSM 不兼容。
3. DSM Docker 管理員的終端功能可能與該映像預設入口點衝突。
深層原因：
- 架構層面：不同容器基底與 init/entrypoint 管理方式差異。
- 技術層面：TTY、PID 1、信號轉發處理差異導致不穩定。
- 流程層面：映像選型未考量 DSM UI 終端機兼容性。

### Solution Design（解決方案設計）
解決策略：改用 Nginx + PHP-FPM 的 WordPress 映像（amontaigu/wordpress），避開 DSM 終端機兼容性問題，並獲得更輕量與高效能的佈署。

實施步驟：
1. 拉取替代映像並測試
- 實作細節：拉取 amontaigu/wordpress 映像，啟動測試容器並嘗試打開終端機觀察穩定度
- 所需資源：Docker Hub
- 預估時間：0.5 小時
2. 切換到新映像上線
- 實作細節：導入既有 WP 資料卷，切換端口與反向代理指向新容器
- 所需資源：原 WP 資料備份/卷、Apache 反向代理
- 預估時間：1 小時

關鍵程式碼/設定：
```sh
# 拉取 Nginx+PHP-FPM 版 WordPress 映像
docker pull amontaigu/wordpress:latest

# 啟動測試
docker run -d --name wp-nginx -p 8012:80 amontaigu/wordpress

# 測試 DSM Docker 終端機是否穩定
```

實際案例：切換至 Nginx 版映像後，先前的「開終端即崩潰」問題消失。
實作環境：DSM 5.2、Docker、amontaigu/wordpress
實測數據：
改善前：開啟終端機導致容器 crash
改善後：終端機可正常使用、容器穩定運行
改善幅度：可用性由易崩潰提升為穩定（質性）

Learning Points（學習要點）
核心知識點：
- 容器 entrypoint/TTY 相容性
- Nginx+PHP-FPM 與 Apache 架構差異
- 替代映像選型思路
技能要求：
必備技能：Docker 映像操作、容器日誌診斷
進階技能：容器內進程管理、健康檢查
延伸思考：
- 其他服務也可用替代映像解決相容性
- 注意映像維護度與社群活躍度
- 評估長期維運的升級策略

Practice Exercise（練習題）
基礎練習：啟動官方 WP 與替代映像各一個，觀察行為差異
進階練習：將資料捲掛載至兩個映像，切換不中斷
專案練習：撰寫一份映像選型報告（相容性/維護度/效能）

Assessment Criteria（評估標準）
功能完整性（40%）：替代映像能穩定運行
程式碼品質（30%）：啟動腳本/指令清晰可重現
效能優化（20%）：容器資源配置合理
創新性（10%）：選型依據完整


## Case #3: 在 DSM 以 Docker 建立 WordPress + MySQL 堆疊

### Problem Statement（問題陳述）
業務場景：自架部落格需 WordPress + MySQL。希望在 NAS 上以容器形式建置，避免安裝繁複套件，並保留數據持久化。
技術挑戰：容器間網路、資料卷與環境變數設定；確保資料持久化與可遷移。
影響範圍：服務穩定性、資料安全、後續遷移便利性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WordPress 依賴 MySQL，需正確配置連線與密碼。
2. 容器預設無持久化，需建立資料卷。
3. DSM 預設網路需明確規劃容器互通。
深層原因：
- 架構層面：多容器依賴需編排與隔離
- 技術層面：環境變數、Volume 與網路別名治理
- 流程層面：備份/還原流程需標準化

### Solution Design（解決方案設計）
解決策略：使用官方 MySQL 映像與 WP 映像（或穩定替代映像），建立自定網路與資料卷；以環境變數參數化設定，實現可重現與可遷移。

實施步驟：
1. 建立網路與資料卷
- 實作細節：docker network create、建立 /volume1/docker 的持久化路徑
- 所需資源：NAS 儲存空間
- 預估時間：0.5 小時
2. 啟動 MySQL 與 WordPress
- 實作細節：設定 MYSQL_ROOT_PASSWORD、MYSQL_DATABASE 等；WP 設定 DB Host 指向 mysql 容器別名
- 所需資源：Docker Hub 映像
- 預估時間：1 小時

關鍵程式碼/設定：
```sh
# 建立網路
docker network create wpnet

# 啟動 MySQL（官方映像）
docker run -d --name mysql \
  --network wpnet \
  -v /volume1/docker/mysql:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=strongpass \
  -e MYSQL_DATABASE=wordpress \
  -e MYSQL_USER=wpuser \
  -e MYSQL_PASSWORD=wppass \
  mysql:8.0

# 啟動 WordPress（以官方為例，或替代映像自行對應環境變數）
docker run -d --name wp \
  --network wpnet \
  -p 8012:80 \
  -e WORDPRESS_DB_HOST=mysql:3306 \
  -e WORDPRESS_DB_USER=wpuser \
  -e WORDPRESS_DB_PASSWORD=wppass \
  -e WORDPRESS_DB_NAME=wordpress \
  wordpress:latest
```

實際案例：作者使用 MySQL 官方映像搭配 Nginx 版 WP 映像，端口 8012 對內服務，由反向代理對外發布。
實作環境：DSM 5.2、Docker、MySQL 官方映像、amontaigu/wordpress
實測數據：
改善前：未建置
改善後：容器啟動 2-3 秒可用，資料持久化落地 /volume1/docker
改善幅度：部署時間縮短為分鐘等級

Learning Points（學習要點）
核心知識點：
- 容器網路與別名
- Volume 的資料持久化
- WordPress 與 MySQL 連線參數
技能要求：
必備技能：Docker CLI、基本網路/檔案系統
進階技能：Compose 編排、備份策略
延伸思考：
- 用 docker-compose 管理整組服務
- 數據備份/還原與升級流程
- 引入健康檢查與自動重啟策略

Practice Exercise（練習題）
基礎練習：啟動 MySQL + WordPress 兩容器並成功安裝 WP
進階練習：將資料捲遷移到新 NAS
專案練習：以 Compose 定義整組堆疊並一鍵部署

Assessment Criteria（評估標準）
功能完整性（40%）：WP 能連上 DB 且持久化
程式碼品質（30%）：指令/Compose 清晰、可重現
效能優化（20%）：資源限制與健康檢查
創新性（10%）：備份與遷移設計


## Case #4: DSM 80 埠被內建 Apache 佔用，導入反向代理解決對外服務

### Problem Statement（問題陳述）
業務場景：DSM 內建 Apache 佔用 80 埠，Docker 內多個網站服務無法同時映射到 80；也無法在 DSM 介面釋放 80 埠。
技術挑戰：需要單一 80 埠對外承載多站點且分發至不同容器。
影響範圍：外部訪客只能以非標準埠存取或無法存取，體驗與 SEO 受損。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 80 埠被 DSM 內建 Apache 綁定。
2. 多容器無法共享相同宿主機埠。
3. DSM 介面無直接釋放 80 埠的設定。
深層原因：
- 架構層面：單一入口需求（80/443）與多後端服務佈署
- 技術層面：端口映射限制
- 流程層面：缺少前端入口控制層

### Solution Design（解決方案設計）
解決策略：使用 DSM 內建 Apache 虛擬主機開啟 mod_proxy，配置 Reverse Proxy 將 80 埠流量按 Host/Path 導向不同容器服務。

實施步驟：
1. 建立 Virtual Host
- 實作細節：透過 DSM Web Station 建立 columns.chicken-house.net 的 VH
- 所需資源：DSM Web Station
- 預估時間：0.5 小時
2. 編輯反向代理設定並重啟 Apache
- 實作細節：編輯 /etc/httpd/httpd-vhost.conf-user，加入 ProxyPass/ProxyPassReverse
- 所需資源：SSH、Apache mod_proxy
- 預估時間：0.5 小時

關鍵程式碼/設定：
```apache
# /etc/httpd/httpd-vhost.conf-user
<VirtualHost *:80>
  ServerName columns.chicken-house.net
  DocumentRoot "/var/services/web/columns"
  ProxyPreserveHost On
  ProxyRequests Off
  <Location />
    ProxyPass http://nas:8012/
    ProxyPassReverse http://columns.chicken-house.net/
    Order allow,deny
    Allow from all
  </Location>
</VirtualHost>

# 套用設定
httpd -k restart
```

實際案例：將 columns.chicken-house.net 綁定至內部 WP 容器（:8012）。
實作環境：DSM 5.2、Apache（DSM 內建）、Docker
實測數據：
改善前：僅能以 http://host:8012 存取
改善後：以 http://columns.chicken-house.net 直接存取
改善幅度：URL 標準化、對外可達性與體驗顯著提升

Learning Points（學習要點）
核心知識點：
- 反向代理與虛擬主機
- ProxyPass / ProxyPassReverse
- 入口層架構
技能要求：
必備技能：基本 Apache 配置、SSH
進階技能：多站點路由策略、SSL 終結
延伸思考：
- 亦可用 Nginx/Traefik 作為入口
- 加入 HTTPS 與 HSTS 提升安全
- Path 與 Host 雙維度路由

Practice Exercise（練習題）
基礎練習：建立一個虛擬主機代理到單一容器
進階練習：新增第二個站點與 Host-based 路由
專案練習：為多容器站點建立完整入口（80/443）

Assessment Criteria（評估標準）
功能完整性（40%）：80 埠代理可用
程式碼品質（30%）：配置清晰、可維護
效能優化（20%）：代理延遲與連線管理
創新性（10%）：路由策略設計


## Case #5: 用反向代理提供乾淨網址（去除 /wordpress 與非標準埠）

### Problem Statement（問題陳述）
業務場景：使用 DSM 套件版 WordPress 時，網址通常帶有 /wordpress 子路徑或需非標準埠，造成使用者體驗差且搜索引擎連結可能失效。
技術挑戰：要讓對外訪客以根網域（不含子路徑與特殊埠）訪問容器內的 WP。
影響範圍：SEO、外部引用連結、品牌形象。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. DSM 套件版 WP 預設安裝於子路徑。
2. 多容器共用 80 埠導致需改用非標準埠。
3. 直接映射容器埠難以對外以 80 埠曝光多站點。
深層原因：
- 架構層面：缺少前置路由層
- 技術層面：URL 組成與反向代理重寫
- 流程層面：部署選型偏向「就近安裝」忽略對外體驗

### Solution Design（解決方案設計）
解決策略：以 Apache 虛擬主機對應 Host，根路徑 Location / 全量代理至 WP 容器，前端公開為標準 80 埠與乾淨根路徑。

實施步驟：
1. 建立 Host-based VH
- 實作細節：ServerName 綁定目標網域
- 所需資源：DSM Web Station
- 預估時間：0.5 小時
2. 設置 ProxyPass 根路徑
- 實作細節：Location / 代理至 http://nas:8012/，確保 ProxyPassReverse
- 所需資源：Apache mod_proxy
- 預估時間：0.5 小時

關鍵程式碼/設定：
```apache
<VirtualHost *:80>
  ServerName columns.chicken-house.net
  ProxyPreserveHost On
  <Location />
    ProxyPass http://nas:8012/
    ProxyPassReverse http://columns.chicken-house.net/
  </Location>
</VirtualHost>
```

實際案例：columns.chicken-house.net 以根路徑對外，實際服務由 :8012 容器提供。
實作環境：DSM 5.2、Apache、Docker
實測數據：
改善前：http://domain:8012 或 http://domain/wordpress
改善後：http://domain/
改善幅度：URL 清潔度 100% 提升；避免外部連結斷鏈

Learning Points（學習要點）
核心知識點：
- Host-based 反向代理
- URL 重寫與反向代理返寫
- SEO 與 URL 策略
技能要求：
必備技能：Apache 配置
進階技能：Rewrite 規則與 HSTS/HTTPS
延伸思考：
- 將管理後台 /wp-admin 做額外保護
- 將靜態檔案前置快取
- 導入 HTTPS

Practice Exercise（練習題）
基礎練習：將子路徑站點代理到根路徑
進階練習：保留/重寫特定路徑（如 /admin）
專案練習：對同一域配置 HTTP→HTTPS 全站強制

Assessment Criteria（評估標準）
功能完整性（40%）：乾淨根路徑可用
程式碼品質（30%）：代理與返寫正確
效能優化（20%）：最小代理開銷
創新性（10%）：URL 策略設計


## Case #6: 內外 DNS 分流（Split-horizon DNS）避免內網繞外

### Problem Statement（問題陳述）
業務場景：內部使用者訪問自家站點若經過外部 DNS/路由，會「繞出國再回來」，增加延遲與不穩定。希望內部解析到 NAS 內網 IP，外部解析到路由器對外 IP。
技術挑戰：同一網域需在內/外兩套 DNS 上給出不同解析結果。
影響範圍：效能、可用性、疑難雜症（NAT 迴流）。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一公共 DNS 設定導致內部訪問也走外線。
2. 多數家用路由 NAT 迴流支援不佳。
3. 內部缺少權威或靜態 DNS 規則。
深層原因：
- 架構層面：缺乏內外分離的名稱解析策略
- 技術層面：DNS 區域與記錄管理
- 流程層面：網域與 DDNS 調和方案缺失

### Solution Design（解決方案設計）
解決策略：在家用路由/內部 DNS 加入網域靜態紀錄指向 NAS 內網 IP；對外 DNS 指向路由器對外 IP（固定 IP 用 A 記錄；動態 IP 以 CNAME 指向 DDNS）。

實施步驟：
1. 設定內部 DNS
- 實作細節：在路由器內建 DNS 加入 columns.chicken-house.net → 內網 NAS IP
- 所需資源：路由/DNS 管理權限
- 預估時間：0.5 小時
2. 設定外部 DNS
- 實作細節：固定 IP → A 記錄；動態 IP → CNAME 指向 DDNS 名稱
- 所需資源：網域註冊商/代管 DNS
- 預估時間：0.5 小時

關鍵程式碼/設定：
```txt
# 外部 DNS（固定 IP 範例）
A  columns.chicken-house.net 203.0.113.10

# 外部 DNS（動態 IP 範例）
CNAME columns.chicken-house.net myddns.example.com

# 內部 DNS（路由器靜態記錄）
A columns.chicken-house.net 192.168.1.10   # NAS 內網 IP
```

實際案例：內部解析直達 NAS，外部解析至路由器對外位址；使用手機 4G 測試對外可達。
實作環境：家用路由器（含簡易 DNS）、外部 DNS 供應商
實測數據：
改善前：內部訪問繞外，延遲高且偶有失敗
改善後：內部直連低延遲；外部流量正常入站
改善幅度：內部延遲顯著降低（質性）

Learning Points（學習要點）
核心知識點：
- Split-horizon DNS 概念
- A/CNAME 與 DDNS 策略
- NAT 迴流問題定位
技能要求：
必備技能：DNS 基礎、路由器管理
進階技能：區域轉發、條件轉發、DNS 快取
延伸思考：
- 自建輕量 DNS（dnsmasq）
- 多站點/子域的分流策略
- 加入健康檢查與自動切換

Practice Exercise（練習題）
基礎練習：為單一域設內外不同記錄
進階練習：為多子域配置不同路徑
專案練習：撰寫 DNS 變更與驗證 SOP

Assessment Criteria（評估標準）
功能完整性（40%）：內外可正確解析
程式碼品質（30%）：DNS 設定清晰可驗證
效能優化（20%）：內網延遲降低
創新性（10%）：動態 IP 方案設計


## Case #7: DSM UI 覆寫 Apache vhost 設定，建立備份與自動回填

### Problem Statement（問題陳述）
業務場景：透過 SSH 修改 /etc/httpd/httpd-vhost.conf-user 加入反向代理設定後，日後若再透過 DSM UI 調整 Web Station，原設定會被覆寫遺失，需重做。
技術挑戰：避免手工設定被 UI 覆蓋，降低重工與風險。
影響範圍：服務中斷、維運時間增加、出錯風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. DSM UI 重建 vhost 檔，覆寫手工修改。
2. 無變更管控與外部持久化配置。
3. 缺少回填自動化機制。
深層原因：
- 架構層面：UI 與手動變更未整合
- 技術層面：配置檔來源單一且易被覆蓋
- 流程層面：缺乏備份與回填 SOP

### Solution Design（解決方案設計）
解決策略：建立配置備份並撰寫回填腳本；在每次 DSM 變更後或開機自動回填；並保留版本控制。

實施步驟：
1. 建立備份與版本控制
- 實作細節：將 vhost 檔備份至 /volume1/config/httpd，並納入 Git
- 所需資源：NAS 儲存、Git（可選）
- 預估時間：0.5 小時
2. 建立回填腳本與排程
- 實作細節：以 sh 腳本比對關鍵段落，不存在則追加；排程或手動執行
- 所需資源：DSM 工作排程器、SSH
- 預估時間：1 小時

關鍵程式碼/設定：
```sh
# 備份
cp /etc/httpd/httpd-vhost.conf-user /volume1/config/httpd/httpd-vhost.conf-user.bak

# 回填（示意：若未包含 Proxy 段就插入）
if ! grep -q "ProxyPreserveHost On" /etc/httpd/httpd-vhost.conf-user; then
  cat /volume1/config/httpd/proxy-snippet.conf >> /etc/httpd/httpd-vhost.conf-user
  httpd -k restart
fi
```

實際案例：作者經歷一次被覆寫後重做，建議務必備份；此處補強自動回填以避免重工。
實作環境：DSM 5.2、Apache
實測數據：
改善前：UI 變更後設定消失、需手工重建
改善後：自動回填、服務快速恢復
改善幅度：重工時間近乎歸零（質性）

Learning Points（學習要點）
核心知識點：
- 配置持久化與版本化
- 自動化回填策略
- 服務重啟與驗證
技能要求：
必備技能：Shell、grep/sed、排程
進階技能：配置碎片化 Include（若支援）
延伸思考：
- 以 Ansible/配置管理落地
- 以容器化入口替代系統 Apache
- 建立異動告警

Practice Exercise（練習題）
基礎練習：寫一個備份腳本
進階練習：寫比對關鍵段落的回填腳本
專案練習：導入 Git 管控 vhost 配置與回填流程

Assessment Criteria（評估標準）
功能完整性（40%）：可自動回填與重啟
程式碼品質（30%）：腳本健壯、可讀
效能優化（20%）：最小停機
創新性（10%）：版本化與告警設計


## Case #8: Synology 套件只能裝一份 WordPress，Docker + 反向代理啟動多站點

### Problem Statement（問題陳述）
業務場景：需要多個 WordPress 實例（多部落格/測試站）。DSM 套件版 WP 限制一次僅一份，不利隔離與管理。
技術挑戰：在單台 NAS 同時運行多個獨立 WP 實例並各自對外發布。
影響範圍：產品迭代、A/B 測試、多品牌運營。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. DSM 套件版 WP 架構設計為單實例。
2. 套件安裝路徑與設定不易複製多份。
3. 網域/端口映射受限。
深層原因：
- 架構層面：單實例設計
- 技術層面：入口層缺失
- 流程層面：缺乏標準化多實例佈署

### Solution Design（解決方案設計）
解決策略：以 Docker 啟動多個 WP 容器（各自端口/卷/DB），透過 Apache 虛擬主機以 Hostname 路由至不同實例。

實施步驟：
1. 啟動多個 WP/DB 實例
- 實作細節：wp-a:8012、wp-b:8013 等，使用獨立 DB 與卷
- 所需資源：Docker、儲存空間
- 預估時間：1.5 小時
2. 配置多個 VH
- 實作細節：ServerName a.example.com → :8012、b.example.com → :8013
- 所需資源：Apache vhost
- 預估時間：0.5 小時

關鍵程式碼/設定：
```apache
<VirtualHost *:80>
  ServerName blog-a.example.com
  ProxyPreserveHost On
  <Location />
    ProxyPass http://nas:8012/
    ProxyPassReverse http://blog-a.example.com/
  </Location>
</VirtualHost>

<VirtualHost *:80>
  ServerName blog-b.example.com
  ProxyPreserveHost On
  <Location />
    ProxyPass http://nas:8013/
    ProxyPassReverse http://blog-b.example.com/
  </Location>
</VirtualHost>
```

實際案例：作者指出 Docker 可輕易跑多份 WP，反向代理映射到不同 Host。
實作環境：DSM 5.2、Docker、Apache
實測數據：
改善前：僅能 1 份 WP
改善後：多份 WP 並存、各自獨立管理
改善幅度：多實例能力從 1 → N（關鍵容量提升）

Learning Points（學習要點）
核心知識點：
- 多實例隔離
- Host-based 路由
- Volume 與 DB 隔離
技能要求：
必備技能：Docker、多容器規劃
進階技能：自動化生成 vhost、Compose
延伸思考：
- 引入 Traefik/NGINX 入口動態路由
- 集中化日誌收集
- 自動簽 SSL

Practice Exercise（練習題）
基礎練習：啟動兩個 WP 實例
進階練習：為兩實例配置兩個網域
專案練習：以 Compose 一次部署多站點與入口

Assessment Criteria（評估標準）
功能完整性（40%）：多站點可用
程式碼品質（30%）：配置清晰不衝突
效能優化（20%）：資源隔離合理
創新性（10%）：自動化/動態路由


## Case #9: 反向代理後 Host/Redirect 錯誤，利用 ProxyPreserveHost/ProxyPassReverse 修正

### Problem Statement（問題陳述）
業務場景：將 WP 置於反向代理後，若不正確處理 Host Header 與回應中的 Location，會導致後台導向錯誤或資源路徑出錯。
技術挑戰：保持前端 Host 一致性與修正後端回應中的 URL。
影響範圍：登入、後台操作、靜態資源載入。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 反向代理未保留原 Host，WP 產生錯誤 URL。
2. 未對回應 Location/Set-Cookie 進行返寫。
3. 前/後端 URL 不一致。
深層原因：
- 架構層面：入口層與後端 URL 協同
- 技術層面：HTTP Header、Location 返寫
- 流程層面：缺乏代理前後一致性驗證

### Solution Design（解決方案設計）
解決策略：在 Apache vhost 啟用 ProxyPreserveHost On，並設定 ProxyPassReverse 指回前端網域，確保導向與資源路徑正確。

實施步驟：
1. 開啟 Host 保留
- 實作細節：ProxyPreserveHost On
- 所需資源：Apache mod_proxy
- 預估時間：15 分鐘
2. 設置返寫
- 實作細節：ProxyPassReverse 指向前端 Host
- 所需資源：Apache vhost
- 預估時間：15 分鐘

關鍵程式碼/設定：
```apache
ProxyPreserveHost On
<Location />
  ProxyPass http://nas:8012/
  ProxyPassReverse http://columns.chicken-house.net/
</Location>
```

實際案例：作者 vhost 片段中已正確加入兩項設定，站點能以乾淨 URL 正常運作。
實作環境：DSM 5.2、Apache
實測數據：
改善前：登入導向錯誤/資源失連（潛在）
改善後：導向與資源路徑正常
改善幅度：功能完整度顯著提升（質性）

Learning Points（學習要點）
核心知識點：
- Host Header 與反代一致性
- ProxyPassReverse 原理
- WP/後端對 URL 的敏感性
技能要求：
必備技能：Apache 代理配置
進階技能：更複雜返寫（正則/多 upstream）
延伸思考：
- Path-based 代理下的返寫策略
- Cookies Domain/Path 影響
- 以 Nginx/Traefik 對應的等價配置

Practice Exercise（練習題）
基礎練習：測試有/無 ProxyPreserveHost 的差異
進階練習：模擬 Location 返寫案例
專案練習：加入一段複雜返寫規則（含子路徑）

Assessment Criteria（評估標準）
功能完整性（40%）：後台與資源可用
程式碼品質（30%）：代理/返寫配置正確
效能優化（20%）：代理不產生多餘轉換
創新性（10%）：對異常案例處理


## Case #10: 對外可達性驗證：使用手機 4G 測試與命令列檢查

### Problem Statement（問題陳述）
業務場景：內部 DNS 已分流，需確認外部用戶是否能以標準網域正常存取站點，避免被內部快取或 NAT 迴流誤導。
技術挑戰：區分內外部解析結果與路由行為，進行確證。
影響範圍：上線驗收、對外可用性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 僅在內網測試易被內部 DNS 誤導。
2. 瀏覽器快取/憑證快取影響判斷。
3. 未進行外網網路環境測試。
深層原因：
- 架構層面：內外網路路徑差異
- 技術層面：DNS 解析與 HTTP 回應檢視
- 流程層面：缺少對外驗收步驟

### Solution Design（解決方案設計）
解決策略：以手機 4G 關閉 Wi-Fi 直接測試；輔以 nslookup/dig、curl -I 檢查 DNS 與 HTTP 狀態碼與 Host 一致性。

實施步驟：
1. 外網實機測試
- 實作細節：手機 4G 訪問域名，瀏覽頁面與登入流程
- 所需資源：手機、行動網路
- 預估時間：10 分鐘
2. 命令列驗證
- 實作細節：dig/nslookup 查詢 DNS；curl -I 查看 HTTP 頭與 200/301
- 所需資源：任一外網機器
- 預估時間：10 分鐘

關鍵程式碼/設定：
```sh
# DNS 檢查
dig +short columns.chicken-house.net

# HTTP 檢查
curl -I http://columns.chicken-house.net
```

實際案例：作者於手機關 Wi-Fi 用 4G 測試，確認外部可達。
實作環境：行動網路、外部 DNS
實測數據：
改善前：未知
改善後：確認對外可用（200 OK/頁面可見）
改善幅度：可用性驗收完成

Learning Points（學習要點）
核心知識點：
- 外部驗收重要性
- DNS 與 HTTP 狀態碼解讀
- 快取與測試隔離
技能要求：
必備技能：dig/curl
進階技能：traceroute/ssl 憑證檢查
延伸思考：
- 自動化合規性檢查
- 多地監控
- SLA/性能監測

Practice Exercise（練習題）
基礎練習：curl -I 檢查站點狀態碼
進階練習：對內外 IP 解析做差異化檢查
專案練習：建立一個可用性檢查腳本（DNS+HTTP）

Assessment Criteria（評估標準）
功能完整性（40%）：外部可正常訪問
程式碼品質（30%）：檢查腳本可讀
效能優化（20%）：檢測耗時低
創新性（10%）：增設告警


## Case #11: 以 Docker 取代 VM，在 NAS 上降低資源開銷

### Problem Statement（問題陳述）
業務場景：NAS 資源有限（CPU/RAM），過往以 VM 方式運行服務會造成啟動慢、資源吃重。需要輕量、快速、近原生效能的部署方式。
技術挑戰：在性能有限的 NAS 上同時運行多個服務。
影響範圍：服務數量、響應速度、能源成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. VM 虛擬化需額外 OS 層，開銷大。
2. 啟動慢，無法快速擴縮。
3. NAS 硬體規格有限。
深層原因：
- 架構層面：虛擬機 vs 容器的隔離方式差異
- 技術層面：系統呼叫與資源共享
- 流程層面：Dev/Prod 一致性需求

### Solution Design（解決方案設計）
解決策略：將服務改以容器運行，減少 OS 層；利用容器啟動快與資源限制，提升密度與效率。

實施步驟：
1. 容器化現有服務
- 實作細節：將 Redmine、WP 等從 VM/套件改為容器
- 所需資源：Docker Hub
- 預估時間：1-2 小時/服務
2. 設資源限制與監控
- 實作細節：docker update 設定 --memory/--cpus，使用 docker stats
- 所需資源：Docker CLI
- 預估時間：0.5 小時

關鍵程式碼/設定：
```sh
# 設定容器資源上限
docker update --cpus 1 --memory 512m wp

# 觀察資源
docker stats
```

實際案例：作者指出 Docker 啟動 2-3 秒，與原生相近，資源利用率佳。
實作環境：DSM 5.2、Docker
實測數據：
改善前：VM 啟動慢、佔用高
改善後：容器啟動 2-3 秒，CPU/RAM 開銷小
改善幅度：啟動時間量級縮短

Learning Points（學習要點）
核心知識點：
- VM vs Container
- 資源限制與監控
- 容器密度
技能要求：
必備技能：Docker 基礎
進階技能：資源治理策略
延伸思考：
- 結合 cgroup 與 QoS
- 峰值時排程策略
- 熱升級/滾動更新

Practice Exercise（練習題）
基礎練習：為容器設 CPU/RAM 限制
進階練習：對比 VM 與容器的啟動耗時
專案練習：計劃一份容器資源治理準則

Assessment Criteria（評估標準）
功能完整性（40%）：平穩容器化運行
程式碼品質（30%）：限制與監控清楚
效能優化（20%）：資源利用提升
創新性（10%）：治理策略


## Case #12: Docker Hub 映像選型：官方優先與風險控管

### Problem Statement（問題陳述）
業務場景：Docker Hub 同一服務有多個封裝版本，品質參差。不當選型會導致相容性、更新、維護風險。
技術挑戰：制定映像選用準則並落實到實務。
影響範圍：穩定性、安全性、升級維護。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Hub 上映像來源多，品質不一。
2. 某些映像缺乏維護或安全更新。
3. 文檔不足導致誤用。
深層原因：
- 架構層面：社群驅動與官方維護差異
- 技術層面：基底映像與打包方式不同
- 流程層面：缺乏選型標準

### Solution Design（解決方案設計）
解決策略：優先選擇官方/Verified Publisher；檢視更新頻率、Stars、Issues 活躍度；審閱 Dockerfile 與 README。

實施步驟：
1. 制定選型準則
- 實作細節：建立 checklist（官方標記、更新日期、issue/PR 狀況）
- 所需資源：團隊規範
- 預估時間：0.5 小時
2. 實際篩選
- 實作細節：比對候選映像，選定官方版或維護積極者
- 所需資源：Docker Hub
- 預估時間：0.5 小時

關鍵程式碼/設定：
```sh
# 檢查映像資訊
docker pull wordpress:latest
docker inspect wordpress:latest | jq '.[0].Config.Labels'
```

實際案例：作者表示「有官方版就盡量挑官方」，減少社群差異帶來風險。
實作環境：Docker Hub
實測數據：
改善前：映像品質不確定
改善後：相容性與更新可靠度提升
改善幅度：風險顯著下降（質性）

Learning Points（學習要點）
核心知識點：
- 官方/Verified 標識
- 維護活躍度指標
- 映像透明度（Dockerfile）
技能要求：
必備技能：Hub 查詢、inspect
進階技能：安全掃描
延伸思考：
- 私有倉庫鏡像治理
- 內部白名單/黑名單
- SBOM 與合規

Practice Exercise（練習題）
基礎練習：對比兩個映像維護度
進階練習：審閱 Dockerfile 與版本策略
專案練習：建立映像選型 SOP 文檔

Assessment Criteria（評估標準）
功能完整性（40%）：能依準則選型
程式碼品質（30%）：檢視流程可重現
效能優化（20%）：版本策略清楚
創新性（10%）：安全與合規考量


## Case #13: 多容器共享 80 的埠策略：高埠映射與內綁定

### Problem Statement（問題陳述）
業務場景：多個容器後端皆提供 HTTP，無法全部對外映射為 80；且不希望高埠直接對外曝露。
技術挑戰：避免外部直接訪問後端高埠，統一由 80 入口代理。
影響範圍：安全、治理、運維簡化。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 宿主 80 埠不可共享給多容器。
2. 直接映射高埠到 0.0.0.0 有安全風險。
3. 缺乏統一入口。
深層原因：
- 架構層面：入口層與後端解耦
- 技術層面：端口綁定與本地限制
- 流程層面：零信任/最小曝露原則

### Solution Design（解決方案設計）
解決策略：各容器映射至不同高埠且僅綁定到 NAS 本機/內網介面；所有對外流量統一經由 Apache 反向代理。

實施步驟：
1. 內綁定容器埠
- 實作細節：-p 127.0.0.1:8012:80 或 -p 192.168.1.10:8012:80
- 所需資源：Docker CLI
- 預估時間：15 分鐘
2. 入口代理
- 實作細節：Apache vhost 指向內部高埠
- 所需資源：Apache
- 預估時間：15 分鐘

關鍵程式碼/設定：
```sh
# 僅綁定到本機回環或內網 IP
docker run -d --name wp-a -p 127.0.0.1:8012:80 amontaigu/wordpress
docker run -d --name wp-b -p 127.0.0.1:8013:80 amontaigu/wordpress
```

實際案例：作者以 8012 作為內部端點，外界透過 80 代理存取。
實作環境：DSM、Docker、Apache
實測數據：
改善前：高埠可能對外曝露
改善後：高埠僅內部可達，對外統一 80
改善幅度：攻面縮小（質性）

Learning Points（學習要點）
核心知識點：
- 端口綁定與安全
- 入口層分離
- 反向代理治理
技能要求：
必備技能：Docker 埠映射
進階技能：網路 ACL、防火牆
延伸思考：
- 以 docker network 增強隔離
- 僅暴露入口容器
- 加入 WAF/速率限制

Practice Exercise（練習題）
基礎練習：綁定高埠到 127.0.0.1
進階練習：入口代理兩個服務
專案練習：加入防火牆規則限制外部高埠

Assessment Criteria（評估標準）
功能完整性（40%）：入口代理可用
程式碼品質（30%）：映射與綁定正確
效能優化（20%）：最小暴露
創新性（10%）：安全策略


## Case #14: 容器可攜性：匯出/搬遷至雲端（Azure/AWS）

### Problem Statement（問題陳述）
業務場景：未來可能將服務搬遷至雲端（Azure/AWS 提供 Docker 執行環境），希望容器與資料能平滑遷移。
技術挑戰：如何匯出容器/映像與資料卷，並在新環境復原。
影響範圍：擴展性、災備、雲遷移。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. DSM 套件難以直接搬遷。
2. 容器需同時考慮映像與資料卷。
3. 環境差異導致啟動參數需重建。
深層原因：
- 架構層面：不可變映像 + 可變資料
- 技術層面：映像打包/載入與卷備份
- 流程層面：遷移步驟與驗證

### Solution Design（解決方案設計）
解決策略：以 docker save/load 匯出/載入映像；資料卷以 tar 備份；在新環境重建網路與啟動命令。

實施步驟：
1. 匯出映像與資料
- 實作細節：docker commit（必要時）、docker save、tar 資料卷
- 所需資源：外接儲存
- 預估時間：1 小時
2. 新環境導入
- 實作細節：docker load、還原卷、依參數啟動
- 所需資源：雲端 VM/容器服務
- 預估時間：1 小時

關鍵程式碼/設定：
```sh
# 匯出映像
docker save amontaigu/wordpress:latest | gzip > wp-img.tar.gz

# 備份資料卷（例：/volume1/docker/wp）
tar czf wp-vol.tar.gz -C /volume1/docker/wp .

# 新環境載入
gunzip -c wp-img.tar.gz | docker load
mkdir -p /data/wp && tar xzf wp-vol.tar.gz -C /data/wp
```

實際案例：作者指出 Docker 匯出/搬遷容易，較 Synology 套件有利。
實作環境：DSM、任一雲 VM/容器主機
實測數據：
改善前：套件遷移困難
改善後：映像/資料可攜、快速上線
改善幅度：遷移成本大幅降低（質性）

Learning Points（學習要點）
核心知識點：
- 映像 vs 容器 vs 卷
- save/load 與資料備份
- 參數再現性
技能要求：
必備技能：Docker CLI、檔案打包
進階技能：Compose/Registry 遷移
延伸思考：
- 建立私有 Registry
- IaC（Terraform/Ansible）自動化
- 多環境一致性驗證

Practice Exercise（練習題）
基礎練習：save/load 一個映像
進階練習：備份/還原資料卷
專案練習：在新 VM 復原完整 WP 站

Assessment Criteria（評估標準）
功能完整性（40%）：站點在新環境可用
程式碼品質（30%）：備份/還原流程清晰
效能優化（20%）：遷移耗時/體積控制
創新性（10%）：自動化與校驗


## Case #15: 集中管理：DSM Docker 管理員的 Volume/Port/資源治理

### Problem Statement（問題陳述）
業務場景：多容器部署需要集中管理掛載、端口映射與 CPU/RAM 限制。DSM 套件中心缺乏這些統一治理能力。
技術挑戰：在 GUI/CLI 下高效管理多容器資源與配置。
影響範圍：穩定性、資源分配、公平性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 套件中心管理能量有限。
2. 多容器需要一致管理介面。
3. 缺乏資源限制易造成互相影響。
深層原因：
- 架構層面：多租戶/多服務共平台
- 技術層面：Volume/Port/Resource 策略
- 流程層面：治理與巡檢缺失

### Solution Design（解決方案設計）
解決策略：使用 DSM Docker 管理員或 CLI 管理 Volume/Port/Resource；建立命名約定與標籤，定期巡檢。

實施步驟：
1. 規範化命名與標籤
- 實作細節：容器/卷命名規則，標籤註記用途
- 所需資源：團隊約定
- 預估時間：0.5 小時
2. 設置資源限制與巡檢
- 實作細節：—memory/—cpus；使用 docker ps/stats/inspect 報表
- 所需資源：Docker CLI/DSM GUI
- 預估時間：0.5 小時

關鍵程式碼/設定：
```sh
docker run -d --name wp \
  -v /volume1/docker/wp:/var/www/html \
  -p 127.0.0.1:8012:80 \
  --cpus 1 --memory 512m \
  --label app=wordpress --label env=prod \
  amontaigu/wordpress
```

實際案例：作者展示 DSM Docker 管理員可視化管理（圖示），相較套件中心更彈性。
實作環境：DSM、Docker
實測數據：
改善前：資源治理與配置分散
改善後：統一管理、可視化與限制能力
改善幅度：治理效率顯著提升（質性）

Learning Points（學習要點）
核心知識點：
- Volume/Port/Resource 基本功
- 命名與標籤治理
- 巡檢與報表
技能要求：
必備技能：DSM GUI、Docker 基礎
進階技能：事件告警、監控
延伸思考：
- 導入 Prometheus/Grafana
- 自定巡檢腳本
- 基於標籤的自動化

Practice Exercise（練習題）
基礎練習：用 DSM GUI 配置一個容器（含卷/埠/資源）
進階練習：以標籤產生巡檢清單
專案練習：編寫資源使用報表

Assessment Criteria（評估標準）
功能完整性（40%）：配置正確可用
程式碼品質（30%）：命名/標籤一致
效能優化（20%）：資源限制合理
創新性（10%）：巡檢可用性


## Case #16: Nginx + PHP-FPM 在 NAS 上的效能/資源優勢

### Problem Statement（問題陳述）
業務場景：NAS 硬體有限，希望網站伺服器更省資源又快速。Nginx 的事件驅動模型與 PHP-FPM 模式較適合低資源環境。
技術挑戰：在 WordPress 場景下取得更好效能與穩定度。
影響範圍：CPU/RAM、吞吐、延遲。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Apache 模組模式在低資源下較吃記憶體。
2. Nginx + FPM 輕量、啟動快。
3. 映像實作差異造成穩定性不同。
深層原因：
- 架構層面：事件驅動 vs 多進程/執行緒
- 技術層面：FPM 池化管理
- 流程層面：映像實作/最佳化差異

### Solution Design（解決方案設計）
解決策略：採用 Nginx + PHP-FPM 的 WP 映像，利用其輕量與高併發特性；結合反向代理入口達到穩定與效能。

實施步驟：
1. 部署 Nginx 版 WP
- 實作細節：以替代映像運行，確保連線穩定
- 所需資源：Docker
- 預估時間：0.5 小時
2. 調整 FPM 池（可選）
- 實作細節：依 NAS 資源調整 pm.max_children 等
- 所需資源：容器配置檔
- 預估時間：0.5 小時

關鍵程式碼/設定：
```sh
# 啟動 Nginx+FPM 版 WP
docker run -d --name wp -p 8012:80 amontaigu/wordpress

# （可選）調整 FPM 參數：/usr/local/etc/php-fpm.d/www.conf
# pm.max_children = 5
```

實際案例：作者切換 Nginx 版映像後解決崩潰，且更省 RAM、啟動快。
實作環境：DSM、Docker、Nginx+FPM
實測數據：
改善前：不穩定、可能較耗資源
改善後：穩定、啟動 2-3 秒、資源佔用低（質性）
改善幅度：穩定性與效率提升

Learning Points（學習要點）
核心知識點：
- Nginx 事件驅動特性
- PHP-FPM 池設定
- 容器內最佳化
技能要求：
必備技能：容器檔案與設定修改
進階技能：壓測與參數優化
延伸思考：
- FastCGI 緩存策略
- 靜態資源由 Nginx 直接服務
- 前端快取（CDN）

Practice Exercise（練習題）
基礎練習：部署 Nginx+FPM 版 WP
進階練習：調整 FPM 參數並壓測前後
專案練習：加入 Nginx 靜態快取

Assessment Criteria（評估標準）
功能完整性（40%）：站點穩定運行
程式碼品質（30%）：配置變更可追溯
效能優化（20%）：壓測數據改善
創新性（10%）：快取策略


## Case #17: 變更 Apache 設定並安全重啟服務

### Problem Statement（問題陳述）
業務場景：修改 vhost 與反向代理設定後，需要安全重啟 Apache 使配置生效，避免中斷時間過長。
技術挑戰：正確套用設定、避免語法錯誤導致啟動失敗。
影響範圍：服務可用性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 配置修改未套用
2. 語法錯誤導致重啟失敗
3. 無檢查與回退
深層原因：
- 架構層面：入口單點
- 技術層面：配置語法驗證
- 流程層面：變更與回退缺失

### Solution Design（解決方案設計）
解決策略：在重啟前做語法檢查（若可用）；重啟後健康檢查；保留備份以便回退。

實施步驟：
1. 語法檢查與備份
- 實作細節：httpd -t（若可用）、備份配置檔
- 所需資源：Apache CLI
- 預估時間：10 分鐘
2. 重啟與驗證
- 實作細節：httpd -k restart、curl 健檢、觀察 error_log
- 所需資源：SSH
- 預估時間：10 分鐘

關鍵程式碼/設定：
```sh
# 語法檢查（若支援）
httpd -t || { echo "Syntax error"; exit 1; }

# 重啟
httpd -k restart

# 健康檢查
curl -I http://columns.chicken-house.net
```

實際案例：作者修改配置後以 httpd -k restart 套用，網站即時可達。
實作環境：DSM 內建 Apache
實測數據：
改善前：配置未生效
改善後：變更即時生效且站點可用
改善幅度：變更效率與可靠性提升

Learning Points（學習要點）
核心知識點：
- Apache 重啟與健檢
- 設定語法檢查
- 回退策略
技能要求：
必備技能：SSH/CLI
進階技能：自動化部署與回滾
延伸思考：
- 熱重載/平滑重啟策略
- 監控與告警整合
- 災備演練

Practice Exercise（練習題）
基礎練習：修改配置並重啟
進階練習：加入語法檢查與回退
專案練習：撰寫一鍵部署與驗證腳本

Assessment Criteria（評估標準）
功能完整性（40%）：變更可生效
程式碼品質（30%）：檢查與回退流程清晰
效能優化（20%）：最小中斷
創新性（10%）：自動化水準



--------------------------------
案例分類
--------------------------------

1. 按難度分類
- 入門級（適合初學者）：#4, #5, #10, #11, #12, #15, #17
- 中級（需要一定基礎）：#1, #2, #3, #6, #7, #8, #9, #13, #14, #16
- 高級（需要深厚經驗）：（本篇案例以實務入門/中級為主，無純高級案例）

2. 按技術領域分類
- 架構設計類：#1, #4, #8, #11, #13, #14, #15, #16
- 效能優化類：#11, #16
- 整合開發類：#3, #4, #5, #8, #9, #13, #15
- 除錯診斷類：#2, #7, #9, #10, #17
- 安全防護類：#6, #13, #15（治理）、#9（Host/Redirect 正確性避免洩露）

3. 按學習目標分類
- 概念理解型：#1, #11, #12, #16
- 技能練習型：#3, #4, #5, #10, #15, #17
- 問題解決型：#2, #6, #7, #8, #9, #13, #14
- 創新應用型：#8, #13, #14, #16


--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 起步（概念與基礎）：先學 #1（為何用 Docker）、#11（容器 vs VM）、#12（映像選型）
- 基礎實作：#3（WP+MySQL 堆疊）、#15（DSM Docker 管理）、#17（Apache 變更與重啟）
- 對外發布：#4（反向代理解決 80 埠）、#5（乾淨網址）、#9（Host/Redirect 修正）
- 網路與 DNS：#6（內外分流）、#10（對外驗證）、#13（埠策略與安全綁定）
- 進階穩定與性能：#2（映像相容性切換）、#16（Nginx+FPM 效能）、#7（配置持久化與回填）
- 擴展與遷移：#8（多站點佈署）、#14（容器搬遷到雲）

依賴關係示例：
- #3 依賴 #1/#12 的映像選型認知
- #4/#5 依賴 #17 的 Apache 操作
- #8 依賴 #3/#4/#5 的基礎
- #14 依賴 #3/#15 的資料卷與配置治理

完整學習路徑建議：
1) #1 → #11 → #12（建立容器與選型概念）
2) #3 → #15 → #17（能部署並治理單服務）
3) #4 → #5 → #9（對外發布與代理細節）
4) #6 → #10 → #13（DNS 與網路安全發布）
5) #2 → #16 → #7（穩定與效能、配置長治久安）
6) #8 → #14（多站點與可攜遷移，收束於可擴展架構）