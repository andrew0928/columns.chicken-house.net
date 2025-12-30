---
layout: synthesis
title: "CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)"
synthesis_type: solution
source_post: /2015/12/04/casestudy-nginx-as-reverseproxy/
redirect_from:
  - /2015/12/04/casestudy-nginx-as-reverseproxy/solution/
---

以下內容基於原文逐段抽取、拆解並重構，整理出 16 個具完整教學價值的問題解決案例。每個案例包含問題、根因、可操作的解法（含程式碼/設定）、實測觀察、學習要點與練習與評估標準。可用於課堂實戰、專案練習與能力評估。

## Case #1: NAS 效能瓶頸，遷移至 Ubuntu Server + Docker

### Problem Statement（問題陳述）
- 業務場景：個人部落格從 BlogEngine.NET 遷移至 WordPress，初期部署在 Synology NAS（內建 Docker），隨著容器數量增加（Web、DB、其他工具），頁面回應時間明顯變慢，影響日常瀏覽與管理。為確保穩定與可擴充性，決定遷移至專用 Ubuntu Server（舊 NB）並持續使用 Docker。
- 技術挑戰：在不中斷服務的前提下，將多容器服務從 NAS 平滑搬遷到 Ubuntu，並維持既有轉址與反向代理能力。
- 影響範圍：用戶體驗、SEO、維運穩定性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. NAS 硬體資源不足（Atom CPU + 2GB RAM）無法支撐多容器並行。
  2. NAS I/O 與網路堆疊對容器化負載不友善，增大延遲。
  3. 前端仍有 Apache 壓力（內建，佔用 80 port），降低整體效率。
- 深層原因：
  - 架構層面：單機所有服務疊在 NAS 上，缺乏資源隔離與擴充空間。
  - 技術層面：未充分利用高效的 NGINX；資料與服務耦合在宿主機。
  - 流程層面：缺乏容量規劃與搬遷計畫。

### Solution Design（解決方案設計）
- 解決策略：以舊 NB 建立 Ubuntu Server + Docker 的專用環境，前端改用 NGINX Reverse Proxy，後端以資料 Volume-Container 隔離持久化資料，依序完成服務轉移與驗證，確保老網址 301 正確。

- 實施步驟：
  1. 建立新環境（Ubuntu + Docker）
     - 實作細節：安裝 Docker、配置基本防火牆；建立 Docker network
     - 所需資源：Ubuntu Server、Docker Engine
     - 預估時間：0.5 天
  2. 佈署 NGINX 反向代理
     - 實作細節：設定 server block、proxy_pass；準備轉址規則（map）
     - 所需資源：nginx:stable 映像
     - 預估時間：0.5 天
  3. 資料外掛與容器遷移
     - 實作細節：建立 Volume-Container；WordPress、DB 使用 volumes-from
     - 所需資源：MySQL/MariaDB、WordPress 映像
     - 預估時間：1 天
  4. 切換與驗證
     - 實作細節：DNS/反代切換、301 測試（curl -I）
     - 所需資源：域名控制、測試腳本
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```bash
# 建立資料卷容器
docker create --name blogdata -v /var/lib/mysql -v /var/www/html busybox

# DB
docker run -d --name blogdb --volumes-from blogdata -e MYSQL_ROOT_PASSWORD=**** mariadb:10

# WordPress
docker run -d --name blogweb --link blogdb:db --volumes-from blogdata wordpress:php-fpm

# NGINX (反代)
docker run -d --name nginx -p 80:80 -v $PWD/nginx.conf:/etc/nginx/nginx.conf --link blogweb:web nginx:stable
```

- 實際案例：原文由 NAS（Synology 412+）遷移至 Ubuntu Server（舊 NB：Pentium P6100 + 4GB RAM），前端改用 NGINX。
- 實作環境：Ubuntu Server 15.10、Docker Engine、NGINX、WordPress、MariaDB
- 實測數據：
  - 改善前：NAS 多開兩個 container 明顯變慢（主觀觀察）
  - 改善後：Ubuntu 同等容器數無明顯延遲（主觀觀察）
  - 改善幅度：未量化，體感明顯改善

Learning Points（學習要點）
- 核心知識點：
  - 容器遷移策略與中斷最小化
  - 反向代理前置的流量匯聚
  - Volume-Container 資料持久化模式
- 技能要求：
  - 必備技能：Linux/Docker 基本操作、Nginx 基本設定
  - 進階技能：零停機切換、容量規劃
- 延伸思考：
  - 可否以 docker-compose 或 k8s 簡化？
  - 硬體故障風險如何備援？
  - 如何量化性能（如 wrk/ab 基準）？
- Practice Exercise
  - 基礎練習：在本機起一組 NGINX+WordPress+DB 並以 volumes-from 管理資料（30 分鐘）
  - 進階練習：撰寫切換腳本，一鍵將反代指向新環境（2 小時）
  - 專案練習：完成 NAS→Ubuntu 的遷移演練與回滾方案（8 小時）
- Assessment Criteria
  - 功能完整性（40%）：遷移後功能無中斷、轉址正確
  - 程式碼品質（30%）：Docker/NGINX 配置清晰
  - 效能優化（20%）：延遲可觀察性與優化證據
  - 創新性（10%）：自動化與回滾設計

---

## Case #2: 多容器共享單一 IP:80 的反向代理設計

### Problem Statement（問題陳述）
- 業務場景：後端有多個 Docker container（Blog、Redmine、管理工具）需用同一個公共 IP 與 80 port 對外，避免暴露多個 port 與複雜 URL 結構。
- 技術挑戰：以前端 Reverse Proxy 匯聚請求，基於 Host/Path 路由到正確容器，並保持舊網址的 301 導向。
- 影響範圍：用戶入口一致性、維運與擴充便利性、資訊安全。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 多服務需共用單一 80 port。
  2. 容器內部位址與 port 不宜直接暴露。
  3. 舊連結需要在入口層處理轉址。
- 深層原因：
  - 架構層面：缺少前置網關/反代層。
  - 技術層面：未使用 Host/Path 路由與健康檢查。
  - 流程層面：缺乏統一入口與路由規範。

### Solution Design（解決方案設計）
- 解決策略：以 NGINX 為前端反代，採用 server_name 與 location 路由至對應容器，並將轉址（map/return 301）放在入口層統一處理。

- 實施步驟：
  1. 設計路由規格
     - 實作細節：以網域或路徑切分服務
     - 所需資源：域名/DNS、設計文件
     - 預估時間：0.5 天
  2. 配置 NGINX server block
     - 實作細節：proxy_set_header、超時參數、健康檢查
     - 所需資源：nginx 映像/套件
     - 預估時間：0.5 天
  3. 轉址規則接入
     - 實作細節：map + return 301；測試 301/302
     - 所需資源：slug map 檔
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```nginx
http {
  map $slug $slugwpid { include maps/slugmap.txt; * 0; }

  upstream blog { server blogweb:9000; } # e.g., PHP-FPM via fastcgi_pass

  server {
    listen 80;
    server_name example.com;

    # 舊 BlogEngine 到 WP
    if ($uri ~* "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*)\.aspx$") {
        set $slug $5;
        return 301 /?p=$slugwpid;
    }

    location / {
      proxy_pass http://blog;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }
}
```

- 實際案例：原文以 NGINX 前置反代集中發布後端多個容器，並處理老網址轉址。
- 實作環境：NGINX + Docker 網路（bridge）
- 實測數據：
  - 改善前：各容器需暴露 port 或透過 NAS 內建 Apache，維運複雜
  - 改善後：單一入口統一路由，轉址在入口層完成
  - 改善幅度：維運複雜度與風險明顯降低（定性）

Learning Points
- 核心知識點：反向代理路由、Header 透傳、入口層轉址
- 技能要求：NGINX 基本配置、HTTP 路由
- 延伸思考：是否引入 API Gateway / Service Mesh？
- Practice Exercise：以不同 Host/Path 路由到兩個容器（30 分鐘）；加入健康檢查與熔斷（2 小時）；做成可重用模板（8 小時）
- Assessment：路由正確性、配置可維護性、可擴充性、自動化程度

---

## Case #3: Apache Reverse Proxy → NGINX 的架構替換

### Problem Statement（問題陳述）
- 業務場景：早期使用 NAS 內建 Apache 做反代（80 port 被佔），遷移到 Ubuntu 後可自由選擇，目標改為 NGINX 以獲得更佳性能與精簡轉址。
- 技術挑戰：在不影響舊鏈接與 SEO 的前提下，重寫反代與轉址規則。
- 影響範圍：入口層穩定性、性能、轉址正確性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. NAS 限制導致只能用 Apache。
  2. Apache RewriteMap 與 NGINX map 語法差異。
  3. 需要維持 2400 組舊網址轉新網址。
- 深層原因：
  - 架構層面：對入口層選型綁定於裝置預設。
  - 技術層面：未抽象出轉址規則，遷移成本高。
  - 流程層面：缺乏跨伺服器的配置可移植性設計。

### Solution Design（解決方案設計）
- 解決策略：以 NGINX 作為統一反代；將 Apache RewriteMap 轉為 NGINX map（外部 include 檔）；藉由 regex + map 實現 slug 查表與 301。

- 實施步驟：
  1. 彙整現有 Apache 轉址規則
     - 實作細節：提取 RewriteMap 與 RewriteRule
     - 所需資源：原 Apache conf
     - 預估時間：0.5 天
  2. 語法轉換與測試
     - 實作細節：改用 map/include；以 NGINX for Win32 先測
     - 所需資源：nginx-win32、測試 URL 清單
     - 預估時間：0.5 天
  3. 上線切換
     - 實作細節：灰度/分段路由；監看 301 命中
     - 所需資源：監控與日誌
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```nginx
map $slug $slugwpid { include maps/slugmap.txt; * 0; }

server {
  if ($uri ~* "^/post(/\d+)?(/\d+)?(/\d+)?/(.*)\.aspx$") {
      set $slug $4; # 視實際群組順序調整
      return 301 /?p=$slugwpid;
  }
}
```

- 實際案例：原文由 Apache → NGINX 完成入口層替換。
- 實作環境：Ubuntu + NGINX + Docker
- 實測數據：
  - 改善前：受限 NAS；規則分散
  - 改善後：NGINX 規則更精簡、效能更佳（定性）
  - 改善幅度：作者測試無明顯不良影響

Learning Points：入口層替換步驟、語法差異、灰度發布
- 練習：撰寫 Apache→NGINX 的轉換清單（30 分）；建立語法對照與自動轉換腳本（2 小時）；完成入口替換專案演練（8 小時）
- 評估：轉換正確性、回滾策略、日誌與監控完備

---

## Case #4: 將 Apache RewriteMap 遷移為 NGINX map

### Problem Statement（問題陳述）
- 業務場景：需維護約 400 篇文章 × 6 種歷史格式的對照，Apache RewriteMap 已在用，改用 NGINX 後需等效能力。
- 技術挑戰：語法與行為差異，需確保查表效率與維護性。
- 影響範圍：轉址正確性、SEO、維護成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. NGINX 與 Apache Rewrite 語法不同。
  2. 查表文件需外部化、可注釋、易維護。
  3. 性能顧慮（NGINX map 是否等效 hash）。
- 深層原因：
  - 架構層面：轉址規則未模組化。
  - 技術層面：對 NGINX map 行為掌握不足。
  - 流程層面：轉換/驗證流程不完善。

### Solution Design
- 解決策略：採用 NGINX map + include 外部檔維護 key/value；沿用原 TXT 的一行一對應並支援註解；小規模表測試效能可接受。

- 實施步驟：
  1. 轉換 RewriteMap TXT → slugmap.txt
     - 實作細節：空白分隔、分號結尾、# 註解
     - 所需資源：文字編輯器/腳本
     - 預估時間：0.5 天
  2. NGINX map 宣告與接線
     - 實作細節：map $slug $slugwpid; include; 預設 *
     - 所需資源：nginx conf
     - 預估時間：0.5 天
  3. 覆蓋測試與回歸
     - 實作細節：針對 2400 組合抽測
     - 所需資源：測試清單
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```nginx
map $slug $slugwpid {
  include maps/slugmap.txt;
  * 0;  # 預設查無對應時的值
}
# slugmap.txt 每行：<oldSlug> <wpId>;
```

- 實際案例：原文示例貼出 slug 對應檔，證明易維護。
- 實作環境：NGINX
- 實測數據：
  - 改善前：Apache 寫法可用但受限於 NAS
  - 改善後：NGINX map 精簡、維護成本低
  - 改善幅度：作者測試性能無明顯影響

Learning Points：map/include 語法、外部化配置
- 練習：撰寫 10 筆 slug 對照並測 301（30 分）；把轉換自動化（2 小時）；引入版本管理與審核流程（8 小時）
- 評估：對照正確率、可維護性、部署流程可追溯

---

## Case #5: 用 NGINX 正規表示法擷取 slug 並 301 導向

### Problem Statement
- 業務場景：舊系統 BlogEngine.NET 的網址包含 .aspx 與可變的年月日/slug 片段，新系統 WordPress 需以 ?p=<id> 接收。
- 技術挑戰：在入口層以 regex 擷取 slug（或其變形），查表換成 WordPress ID，回應 301。
- 影響範圍：SEO、用戶書籤、對外連結。
- 複雜度：中

### Root Cause Analysis
- 直接原因：
  1. 舊新格式差異大，需要正確擷取 slug。
  2. 需與 map 查表連動。
  3. 需用 301 永久轉址。
- 深層原因：
  - 架構：轉址責任未在入口層標準化。
  - 技術：regex 群組與變數傳遞認知不足。
  - 流程：測試用例不足。

### Solution Design
- 策略：在 server 區塊內以 if + ~* regex 判斷並 set $slug，map 自動將 $slug 映射為 $slugwpid，最後 return 301 /?p=$slugwpid。

- 實施步驟：
  1. 編寫正規表示法
     - 細節：捕獲第 N 個群組為 slug
     - 資源：regex101、Nginx 文件
     - 時間：0.5 天
  2. 接 map 串接
     - 細節：set $slug 後 map 自動填 $slugwpid
     - 資源：map 設定
     - 時間：0.5 天
  3. 驗證 301 與 SEO
     - 細節：curl -I、瀏覽器 DevTools
     - 資源：測試列表
     - 時間：0.5 天

- 關鍵程式碼：
```nginx
if ($uri ~* "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*)\.aspx$") {
    set $slug $5;         # 第五個群組為 slug/title
    return 301 /?p=$slugwpid;  # 映射到 WordPress ID
}
```

- 實際案例：原文提供此核心片段。
- 環境：NGINX
- 實測數據：
  - 前：存在 6 種舊網址組合，需人工維護
  - 後：自動擷取 + 查表 + 301
  - 幅度：404 風險降低（定性）

Learning Points：Nginx regex 群組、變數傳遞、301 永久轉址
- 練習：為不同日期深度寫三條規則（30 分）；引入多種 slug 格式（2 小時）；建立完整回歸腳本（8 小時）
- 評估：擷取準確率、301 正確率、配置可讀性

---

## Case #6: 外部化 400+ 映射檔並以 include 管理

### Problem Statement
- 業務場景：400+ 文章、2400 組轉址組合不宜硬寫在 conf，需獨立成檔案以便維護與註解。
- 技術挑戰：格式簡潔、能註解、可版本控制。
- 影響範圍：維護性、風險管理。
- 複雜度：低

### Root Cause Analysis
- 直接原因：
  1. 大量 key/value 對應。
  2. NGINX conf 適合邏輯，不適合大量資料。
  3. 需在不重啟情況下安全 reload。
- 深層原因：
  - 架構：資料/邏輯混雜。
  - 技術：對 include 機制掌握不足。
  - 流程：缺少版本管理與審核。

### Solution Design
- 策略：將對照表置於 maps/slugmap.txt，採用「key 空格 value;」格式，# 註解，並由 map include 載入。

- 實施步驟：
  1. 定義檔案格式
     - 細節：一行一筆，分號結尾
     - 資源：文字編輯器
     - 時間：0.5 天
  2. include 串接
     - 細節：測試 nginx -t、reload
     - 資源：nginx
     - 時間：0.5 天
  3. 加入版本控管
     - 細節：git 管理、PR 審查
     - 資源：Git
     - 時間：0.5 天

- 關鍵設定：
```nginx
map $slug $slugwpid {
  include maps/slugmap.txt;
  * 0;
}
# slugmap.txt 範例
# GoodProgrammer1 65; # 2008/09/27, 該如何學好 "寫程式" ??
```

- 實測數據：作者回報維護容易、性能無明顯影響

Learning Points：外部化資料、配置熱載
- 練習：建立 20 筆映射 + reload（30 分）；加入 GitFlow（2 小時）；導入自動化檢查（8 小時）
- 評估：檔案格式正確率、版本管理、回滾能力

---

## Case #7: 支援 6 種舊網址格式的模式匹配

### Problem Statement
- 業務場景：同一篇文章在舊系統存在多種 URL 變體（含/不含 /columns、可變日期段、大小寫等），需統一導向到 WP。
- 技術挑戰：以最少規則覆蓋最多變體，避免規則衝突。
- 影響範圍：404 率、SEO、維護性。
- 複雜度：中

### Root Cause Analysis
- 直接原因：
  1. 歷史演進產生多格式。
  2. 大小寫與可選片段複雜。
  3. 規則過多易互相干擾。
- 深層原因：
  - 架構：URL 規格未標準化。
  - 技術：regex 設計欠缺覆蓋性。
  - 流程：無回歸測試集。

### Solution Design
- 策略：設計一條包含可選群組的 regex 規則，涵蓋日期段/columns 前綴/slug，搭配 map 查表一次到位。

- 實施步驟：
  1. 採樣分析舊網址
     - 細節：整理 6 類樣本
     - 資源：存量資料
     - 時間：0.5 天
  2. 設計通用 regex
     - 細節：用可選群組 (/\d+)? 與 ~* 忽略大小寫
     - 資源：regex 工具
     - 時間：0.5 天
  3. 撰寫覆蓋測試
     - 細節：針對每一變體測 301
     - 資源：自動化腳本
     - 時間：0.5 天

- 關鍵設定：
```nginx
if ($uri ~* "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*)\.aspx$") {
    set $slug $5;
    return 301 /?p=$slugwpid;
}
```

- 實測數據：作者自測覆蓋多種變體，無明顯漏網情況（定性）

Learning Points：高覆蓋 regex 設計、衝突排查
- 練習：將 6 類 URL 全部列出並驗證（30 分）；加入更多歷史變體擴展測試（2 小時）；建立自動回歸（8 小時）
- 評估：覆蓋率、規則衝突、維護性

---

## Case #8: 將轉址責任自 WordPress 下移至 Proxy

### Problem Statement
- 業務場景：不希望把 2400 組轉址複雜度加諸 WordPress（外掛/程式載入成本高），改以反代層處理。
- 技術挑戰：確保應用層零變更仍能完成正確轉址。
- 影響範圍：應用性能、維護成本。
- 複雜度：低

### Root Cause Analysis
- 直接原因：
  1. WordPress 插件處理轉址會增加負擔。
  2. 應用層修改風險較大。
  3. 入口層更適合做連結治理。
- 深層原因：
  - 架構：責任分層不清。
  - 技術：應用與運維耦合。
  - 流程：變更審核與回歸成本高。

### Solution Design
- 策略：所有舊鏈接辨識與轉址統一在 NGINX；WordPress 專注內容與呈現，降低耦合。

- 實施步驟：
  1. 清點應用側改動需求 → 歸零
  2. 反代側實作 map + 301
  3. 監控 301 命中率與 404 數

- 關鍵設定：
```nginx
# 應用層不做轉址
location / { proxy_pass http://blog; }
# 舊網址一律在入口層 return 301
```

- 實測數據：入口統一治理後，應用層負擔降低；作者測試無明顯負面影響

Learning Points：責任分層、入口層治理
- 練習：將轉址從應用搬到 NGINX（30 分）；對比兩方案延遲（2 小時）；建立轉址治理準則（8 小時）
- 評估：職責清晰度、性能觀察、維護性

---

## Case #9: 使用 NGINX for Win32 快速驗證設定

### Problem Statement
- 業務場景：作者較熟 Windows，為加速 NGINX 設定試錯，採用 NGINX for Win32 做本機快速驗證。
- 技術挑戰：在 Windows 環境快速模擬 Linux 上的 NGINX 行為。
- 影響範圍：開發效率、迭代速度。
- 複雜度：低

### Root Cause Analysis
- 直接原因：
  1. Linux 操作不熟，迭代成本高。
  2. 設定試錯頻繁。
  3. 需快速啟停與檢查。
- 深層原因：
  - 架構：缺少安全沙箱環境。
  - 技術：跨平台差異認知不足。
  - 流程：缺快速驗證與回饋。

### Solution Design
- 策略：在 Windows 安裝 NGINX for Win32，本機測試 regex/map/return；用 curl -I 驗證 301；穩定後再上 Linux。

- 實施步驟：
  1. 安裝與啟動
  2. 放置 conf 與 slugmap.txt
  3. 測試（nginx -t / -s reload）

- 關鍵指令：
```bash
nginx -t        # 測試設定
nginx -s reload # 熱載設定
curl -I "http://localhost/columns/post/2008/09/27/GoodProgrammer1.aspx"
```

- 實測數據：本機快速試錯明顯縮短迭代周期（定性）

Learning Points：本機沙箱、配置驗證
- 練習：在 Windows 模擬一條 301 規則（30 分）；建立測試腳本（2 小時）；形成驗證清單（8 小時）
- 評估：迭代速度、測試覆蓋率、跨平台一致性

---

## Case #10: 採用 Docker Volume-Container 管理資料持久化

### Problem Statement
- 業務場景：原本以宿主目錄掛載資料，遷移後採用官方建議的 Volume-Container，隔離資料與服務。
- 技術挑戰：安全遷移資料、確保服務不中斷。
- 影響範圍：資料安全、備份、升級。
- 複雜度：中

### Root Cause Analysis
- 直接原因：
  1. 服務容器與資料耦合。
  2. 升級替換容器不便。
  3. 備份策略不清。
- 深層原因：
  - 架構：資料層未抽象。
  - 技術：未採用 volumes-from 模式。
  - 流程：備份/還原演練缺失。

### Solution Design
- 策略：建立專用 data container，Web/DB 容器透過 --volumes-from 掛載，簡化升級與備份。

- 實施步驟：
  1. 創建資料卷容器
  2. DB/WEB 掛載使用
  3. 備份與還原演練

- 關鍵指令：
```bash
docker create --name blogdata -v /var/lib/mysql -v /var/www/html busybox
docker run -d --name blogdb --volumes-from blogdata mariadb:10
docker run -d --name blogweb --volumes-from blogdata wordpress:php-fpm
```

- 實測數據：資料與服務分離後，升級與替換容器更順暢（定性）

Learning Points：資料持久化模式、升級與備份
- 練習：資料卷容器備份/還原（30 分）；容器替換演練（2 小時）；自動化備份流程（8 小時）
- 評估：資料可靠性、演練完整性、自動化程度

---

## Case #11: NAS 內建 Apache 佔用 80 port 的衝突處理

### Problem Statement
- 業務場景：Synology NAS 內建 Apache 佔用 80 port，導致無法在 NAS 上改用 NGINX 作入口。
- 技術挑戰：在受限條件下仍需提供多容器入口與轉址。
- 影響範圍：選型彈性、性能。
- 複雜度：低

### Root Cause Analysis
- 直接原因：
  1. 80 port 已被內建 Apache 佔用。
  2. 無法修改系統服務。
  3. 容器需透過 Apache 反代。
- 深層原因：
  - 架構：裝置預設與需求衝突。
  - 技術：缺乏靈活 port 管理策略。
  - 流程：缺少設備層面的規劃。

### Solution Design
- 策略：在 NAS 仍用 Apache 反代；遷移至 Ubuntu 後改用 NGINX，解除限制。

- 實施步驟：
  1. NAS 階段沿用 Apache
  2. 遷移規劃到 Ubuntu
  3. 切換入口至 NGINX

- 可能的暫解設定（非原文實作）：
```apache
# Apache 反向代理（NAS）
ProxyPass "/" "http://blogweb:8080/"
ProxyPassReverse "/" "http://blogweb:8080/"
```

- 實測數據：限制解除後可採 NGINX，性能與靈活性提升（定性）

Learning Points：設備限制下的替代方案與最終解
- 練習：在 8080 暫掛反代（30 分）；遷移後切 NGINX（2 小時）；形成設備選型原則（8 小時）
- 評估：可行性、切換風險、最終達成度

---

## Case #12: NGINX map 的性能顧慮與驗證

### Problem Statement
- 業務場景：擔心 NGINX map 不像 Apache dbm 一樣為二進位 hash，查表性能是否足夠？
- 技術挑戰：量化/定性評估，確保對 400 筆不構成瓶頸。
- 影響範圍：延遲、吞吐。
- 複雜度：低

### Root Cause Analysis
- 直接原因：
  1. map 支援萬用字元與 regex，可能難以編譯為純 hash。
  2. 查表頻繁。
  3. 性能未知。
- 深層原因：
  - 架構：入口層負載評估缺失。
  - 技術：map 實作認知不足。
  - 流程：未做壓測。

### Solution Design
- 策略：以實測為準；在 400 筆規模下觀察無明顯影響；保留後續升級（如 lua/hash）。

- 實施步驟：
  1. 建立測試樣本
  2. 以 wrk/ab 對照測試 map on/off
  3. 觀察 CPU/延遲

- 關鍵設定（示意）：
```nginx
map $slug $slugwpid { include maps/slugmap.txt; * 0; }
# 使用 curl -w 或 wrk 驗證延遲
```

- 實測數據：作者主觀測試無明顯影響；規模固定（400）可接受

Learning Points：以實證替代過度擔憂、保留升級路徑
- 練習：自建 map 壓測（30 分）；與 openresty/lua 比較（2 小時）；設計性能門檻與告警（8 小時）
- 評估：測試設計、觀察指標、報告品質

---

## Case #13: 舊 NB 自建 Ubuntu Server 的性價比實踐

### Problem Statement
- 業務場景：以舊 NB（Pentium P6100、4GB）自建 Ubuntu Server，達成省電、足夠資源、NB 電池即 UPS。
- 技術挑戰：在有限硬體上穩定承載部落格。
- 影響範圍：成本、可用性。
- 複雜度：低

### Root Cause Analysis
- 直接原因：
  1. NAS 資源不足。
  2. 舊 NB 閒置。
  3. 電池可當 UPS。
- 深層原因：
  - 架構：家用級硬體的最佳化使用。
  - 技術：Linux 輕量化配置。
  - 流程：維運與自動化不足。

### Solution Design
- 策略：裝 Ubuntu Server + Docker，精簡服務，確保足夠資源與續航。

- 實施步驟：
  1. 安裝 Ubuntu、Docker
  2. 佈署 NGINX + WP + DB
  3. 基本監控與自動更新

- 參考指令：
```bash
sudo apt-get update && sudo apt-get install -y docker.io nginx
```

- 實測數據：比 NAS 明顯順暢；電池 UPS 功能降低停電風險（定性）

Learning Points：低成本環境建置
- 練習：NB 裝 Ubuntu、起容器（30 分）；加入監控（2 小時）；備援流程（8 小時）
- 評估：穩定性、可用性、成本效益

---

## Case #14: 用容器化把「部署圖」落地

### Problem Statement
- 業務場景：作者提到以往 UML 部署圖與實作落差大；容器化後可直觀地將元件照圖放置與連接。
- 技術挑戰：把架構設計落實為一致的容器、網路與卷。
- 影響範圍：對齊架構與實作、溝通效率。
- 複雜度：中

### Root Cause Analysis
- 直接原因：
  1. 傳統部署流程碎片化。
  2. 配置細節淹沒工程師。
  3. 缺乏標準化單元（容器）。
- 深層原因：
  - 架構：描述與執行缺乏映射。
  - 技術：缺少基礎設施即程式（IaC）。
  - 流程：手動步驟多。

### Solution Design
- 策略：以容器為最小單元，使用命名網路與卷，將部署圖轉換為 docker run/docker-compose 配置。

- 實施步驟：
  1. 定義元件與關係
  2. 建立網路與卷
  3. 以 Compose 表達並版本化

- 關鍵指令：
```bash
docker network create blognet
docker run -d --name blogdb --network blognet mariadb:10
docker run -d --name blogweb --network blognet wordpress:php-fpm
```

- 實測數據：部署與圖一致，認知負擔降低（定性）

Learning Points：架構可執行化、IaC 初探
- 練習：畫部署圖→Compose 文件（30 分）；加入健康檢查（2 小時）；端到端自動化（8 小時）
- 評估：一致性、可讀性、自動化程度

---

## Case #15: RewriteMap TXT → NGINX map 檔的批次轉換

### Problem Statement
- 業務場景：已有 Apache RewriteMap TXT，需要快速改寫為 NGINX 格式（key value; 並支援 # 註解）。
- 技術挑戰：批次轉換與人工校對成本。
- 影響範圍：上線效率、錯誤率。
- 複雜度：低

### Root Cause Analysis
- 直接原因：
  1. 格式差異。
  2. 條目多。
  3. 註解保留需求。
- 深層原因：
  - 架構：未標準化資料格式。
  - 技術：缺少轉換工具。
  - 流程：校對流程缺失。

### Solution Design
- 策略：用文字編輯器或簡單腳本進行格式替換；建立對照抽樣校對。

- 實施步驟：
  1. 樣式分析與替換規則制定
  2. 腳本執行與抽查
  3. 整體回歸測試

- 轉換示意（假設原行無分號）：
```bash
# 將 "KEY VALUE" 轉成 "KEY VALUE;"
sed -E 's/^([^#\s]+\s+[^#\s]+)(\s*#.*)?$/\1; \2/' rewritemap_apache.txt > slugmap.txt
```

- 實測數據：作者以文字編輯器簡單替換即完成；效率高（定性）

Learning Points：格式轉換、質量保證
- 練習：寫一支轉換腳本（30 分）；加入驗證（2 小時）；建立轉換與回歸管線（8 小時）
- 評估：轉換正確率、工具健壯性、回歸覆蓋

---

## Case #16: 大量 301 導向保全 SEO 與舊連結

### Problem Statement
- 業務場景：400+ 文章、6 種舊格式需全部 301 到新站，避免 404 與權重流失。
- 技術挑戰：正確映射、永久轉址、性能可接受。
- 影響範圍：SEO、外部連結、用戶體驗。
- 複雜度：中

### Root Cause Analysis
- 直接原因：
  1. 新舊系統 URL 結構不同。
  2. 大量歷史連結存在外部。
  3. 需用 301 而非 302。
- 深層原因：
  - 架構：缺乏轉址策略。
  - 技術：map + regex 實作經驗不足。
  - 流程：測試與監控不完善。

### Solution Design
- 策略：入口層以 regex 擷取 slug → map 查表 → return 301 /?p=<id>；透過日誌觀察命中與 404。

- 實施步驟：
  1. 建立/維護 slugmap.txt
  2. 編寫 regex+return 301
  3. 監控與調整

- 關鍵設定：
```nginx
if ($uri ~* "/post/.*/(.*)\.aspx$") { set $slug $1; return 301 /?p=$slugwpid; }
```

- 實測數據：
  - 前：存在大量歷史連結需要兼容
  - 後：作者測試轉址無明顯問題；性能無明顯影響（定性）
  - 幅度：404 風險顯著降低（定性）

Learning Points：301 vs 302、SEO 影響
- 練習：用 curl -I 驗證 301（30 分）；建立 404/301 指標看板（2 小時）；SEO 觀察報表（8 小時）
- 評估：轉址正確率、監控指標、SEO 連續性

---

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #6 外部化映射檔
  - Case #8 轉址責任下移至 Proxy
  - Case #9 NGINX for Win32 驗證
  - Case #11 80 port 衝突處理
  - Case #13 舊 NB 自建 Server
  - Case #15 TXT → map 批次轉換
- 中級（需要一定基礎）
  - Case #1 NAS → Ubuntu 遷移
  - Case #2 多容器反代設計
  - Case #3 Apache → NGINX 替換
  - Case #4 RewriteMap → map 遷移
  - Case #5 regex 擷取 slug + 301
  - Case #7 覆蓋 6 種舊網址格式
  - Case #10 Volume-Container
  - Case #16 大量 301 與 SEO
- 高級（需要深厚經驗）
  - Case #12 map 性能顧慮與驗證
  - Case #14 容器化落地部署圖

2) 按技術領域分類
- 架構設計類
  - Case #1, #2, #3, #14
- 效能優化類
  - Case #1, #12
- 整合開發類
  - Case #4, #5, #6, #7, #10, #15, #16
- 除錯診斷類
  - Case #9, #11, #12
- 安全防護類
  - Case #2（入口統一、內網隔離）

3) 按學習目標分類
- 概念理解型
  - Case #2, #8, #14
- 技能練習型
  - Case #4, #5, #6, #9, #10, #15
- 問題解決型
  - Case #1, #3, #7, #11, #12, #16
- 創新應用型
  - Case #13, #14

案例關聯圖（學習路徑建議）
- 先學基礎與概念
  1) Case #8（責任分層：為何轉址放入口層）
  2) Case #2（反向代理與路由概念）
  3) Case #14（容器化部署圖思維）
- 進入配置與實作
  4) Case #9（本機快速驗證方法）
  5) Case #6（映射檔外部化）
  6) Case #5（regex 擷取 + 301）
  7) Case #4（RewriteMap → map 遷移）
  8) Case #7（多格式覆蓋）
- 完成架構替換與遷移
  9) Case #3（Apache → NGINX）
  10) Case #10（Volume-Container）
  11) Case #1（NAS → Ubuntu 遷移）
- 強化效能與穩定
  12) Case #12（map 性能驗證）
  13) Case #11（port 衝突處理策略）
  14) Case #16（301 與 SEO 實戰）
- 延展與最佳化
  15) Case #15（批次轉換工具化）
  16) Case #13（低成本硬體最佳實踐）

依賴關係提示：
- Case #5 依賴 #6、#4 的映射檔與 map 概念。
- Case #3 依賴 #2（反代設計）與 #5（轉址規則）。
- Case #1 遷移需先具備 #10（資料持久化）與 #3（入口替換）。
- Case #12 的性能評估依賴 #5/#6 的轉址已落地。
- Case #16 的 SEO 成效取決於 #5/#7 的正確性。

完整學習路徑：
- 概念（#8 → #2 → #14）→ 工具/配置（#9 → #6 → #5 → #4 → #7）→ 架構替換與資料（#3 → #10 → #1）→ 性能與穩定（#12 → #11 → #16）→ 自動化與運營（#15 → #13）。