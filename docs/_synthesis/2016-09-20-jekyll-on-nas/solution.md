---
layout: synthesis
title: "Running Jekyll on NAS - 高效率的新選擇
title: Deploy Windows Containers on Nano Server"
synthesis_type: solution
source_post: /2016/09/20/jekyll-on-nas/
redirect_from:
  - /2016/09/20/jekyll-on-nas/solution/
postid: 2016-09-20-jekyll-on-nas
---

## Case #1: 用 Jekyll 靜態化取代 NAS 上的 WordPress

### Problem Statement（問題陳述）
**業務場景**：小型團隊在 S 牌 NAS 上以 WordPress 部署內網部落格與文件站，NAS 為省電配置，CPU 與記憶體均偏弱，遇到讀者高峰或備份時，網站回應卡頓且時常需要更新修補安全性問題。團隊希望換成更快、更簡單且更安全的方案，同時保留在 NAS 內部自管的優勢，避免放到公有雲或 GitHub 造成內容外洩風險。  
**技術挑戰**：WordPress（PHP + DB）在低規 NAS 上效能不足，且動態系統的維護安全成本高。  
**影響範圍**：使用者體驗、維運成本、資安風險、內網可用性。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. WordPress 為動態架構（PHP/DB）對 CPU/RAM 敏感，硬體瓶頸導致延遲。  
2. 外掛/主題繁多，更新頻繁，安全面與維護負擔大。  
3. NAS 預設省電配置，對即時計算型工作不友善。  

**深層原因**：
- 架構層面：以動態渲染頁面，無法充分利用靜態快取優勢。  
- 技術層面：選用不適合低規硬體的技術棧。  
- 流程層面：頻繁更新與修補，增加維運流程複雜度與風險。

### Solution Design（解決方案設計）
**解決策略**：以 Jekyll 產生靜態 HTML，改用 NAS 的 Web Station（Nginx）提供靜態檔案，將渲染計算移至建置時，使用 Docker 容器化 Jekyll，使部署與升級簡化、效能與安全同步提升。

**實施步驟**：
1. 建置 Jekyll 容器
- 實作細節：自 Registry 拉 jekyll/jekyll:latest，建立容器並將 NAS:/docker/jekyll 掛載到 /srv/jekyll。  
- 所需資源：Synology Docker、jekyll/jekyll:latest。  
- 預估時間：20 分鐘。  

2. Web Station 發佈靜態檔
- 實作細節：在 Web Station 設定 Virtual Host，根目錄指向 /docker/jekyll/_site，選用 Nginx。  
- 所需資源：Web Station、Nginx。  
- 預估時間：15 分鐘。

**關鍵程式碼/設定**：
```bash
# 取得 Jekyll 映像
docker pull jekyll/jekyll:latest

# 以目錄對應與預覽啟動（本機 4000 對應容器 4000）
docker run --name jekyll-nas --rm -it \
  -p 4000:4000 \
  -v /docker/jekyll:/srv/jekyll \
  jekyll/jekyll:latest jekyll serve --watch

# Web Station (Nginx) 對應 /docker/jekyll/_site
# 若需 Nginx 手動設定示意：
# /etc/nginx/sites-enabled/jekyll.conf
server {
  listen 80;
  server_name columns-jekyll.chicken-house.net;
  root /docker/jekyll/_site;
  index index.html;
  location / { try_files $uri $uri/ =404; }
}
```

實際案例：文中將 Jekyll 產出（_site）交由 NAS Web Station（Nginx）提供，取代 WordPress 動態網站。  
實作環境：Synology DS-412+、Docker、jekyll/jekyll:latest、Web Station（Nginx）。  
實測數據：  
改善前：WordPress 於低規 NAS 體感延遲、需持續更新（敘述性）。  
改善後：靜態網站點擊即出現，維護負擔顯著下降（敘述性）。  
改善幅度：以「體感速度顯著提升、維護頻率降低」衡量（未量測百分比）。

Learning Points（學習要點）  
核心知識點：  
- 靜態化帶來的效能與安全性提升  
- 容器化工具鏈減少部署摩擦  
- 分離建置與服務的架構穩定性  

技能要求：  
必備技能：Docker 基礎、NAS 基礎管理、Jekyll 基本操作  
進階技能：Nginx 配置、站點優化與自動化

延伸思考：  
- 可復用於內網知識庫、產品文件站。  
- 風險：靜態生成延遲，更新不是即時。  
- 優化：啟用增量建置、前端資源壓縮與 CDN 快取。

Practice Exercise（練習題）  
基礎練習：在 NAS 上以 Docker 跑起 Jekyll 並顯示首頁（30 分鐘）。  
進階練習：設定 Web Station 虛擬主機並導向 _site（2 小時）。  
專案練習：將原 WordPress 內容遷移至 Jekyll 架構並驗證路由（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：能以 Nginx 正確提供 _site 內容  
程式碼品質（30%）：容器與 Nginx 設定清晰可重現  
效能優化（20%）：明顯改善載入速度與 NAS 負載  
創新性（10%）：提供自動化建置或額外優化策略


## Case #2: 在 NAS 上私有化部署 Jekyll，避免公開 GitHub 暴露

### Problem Statement（問題陳述）
**業務場景**：部分團隊不願將內部文件、專案筆記與敏感規格公開在 GitHub Pages。希望保有 GitHub/Jekyll 的開發便利與文件生產力，同時將最終成品僅發佈於內網，確保資料不外流。  
**技術挑戰**：保留 Jekyll 的產出效率，並在 NAS 內部網路下以最少步驟完成部署。  
**影響範圍**：合規、資安、資料主權、協作流程。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. GitHub Pages 為公開發佈，無法滿足私有化需求。  
2. 文件仍希望使用 Markdown 與自動化建置。  
3. 需要簡單易維護的內網發布流程。  

**深層原因**：
- 架構層面：缺少私有化的發佈節點。  
- 技術層面：Jekyll 發佈點綁定 GitHub Pages 的迷思。  
- 流程層面：未定義內網的部署與存取策略。

### Solution Design（解決方案設計）
**解決策略**：保留 Jekyll 原工作流（Markdown + 模板），在 NAS 以 Docker 建置，最後用 Web Station（Nginx）發佈至僅內網可達的 Virtual Host，完全不經公有雲。

**實施步驟**：
1. 準備內容與模板
- 實作細節：將網站樣板與內容複製至 NAS:/docker/jekyll。  
- 所需資源：File Station/rsync/SMB。  
- 預估時間：20 分鐘。  

2. 內網 Virtual Host
- 實作細節：Web Station 新增虛擬主機，僅解析內網 DNS，根目錄 /docker/jekyll/_site。  
- 所需資源：Web Station、內網 DNS。  
- 預估時間：30 分鐘。

**關鍵程式碼/設定**：
```bash
# 複製內容至 NAS
rsync -av ./my-jekyll-site/ nas:/docker/jekyll/

# 僅內網可解析的 DNS 設定（概念示意）
# DNS A 記錄：docs.internal.local -> 192.168.1.X (NAS IP)
```

實際案例：文中採用 NAS 上的 Web Station 直接提供 _site，達成「不走 GitHub、僅內網可見」。  
實作環境：Synology DS-412+、Docker、Nginx、內網 DNS。  
實測數據：  
改善前：文件須公開發佈（不符合保密要求）。  
改善後：文件僅內網可見，資料主權掌握在內（敘述性）。  
改善幅度：合規與保密需求滿足（非數值指標）。

Learning Points（學習要點）  
核心知識點：  
- 私有化文件平台設計  
- 內網 DNS 與虛擬主機策略  
- 與 GitHub Pages 的能力對照  

技能要求：  
必備技能：NAS 基礎、DNS/虛擬主機設定  
進階技能：網段隔離、權限控管

延伸思考：  
- 可延伸至多租戶、多專案文件站。  
- 風險：內網單點故障。  
- 優化：鏡像備援或多 NAS 互備。

Practice Exercise（練習題）  
基礎練習：建立僅內網可達的虛擬主機（30 分鐘）。  
進階練習：加上基本認證限制（2 小時）。  
專案練習：將部門文件全面私有化上 NAS（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：私有站點可用、內容完整  
程式碼品質（30%）：設定與文件清楚、可重現  
效能優化（20%）：內網回應時間穩定  
創新性（10%）：內網權限與審計創新


## Case #3: 文件與程式碼共版控的 Blogging-as-Code 工作流

### Problem Statement（問題陳述）
**業務場景**：團隊希望將 API 文件與安裝手冊等非程式文件與程式碼一起管理，避免 Word 檔案散落、版控難追蹤的局面，並能在提交後自動更新 Web 文件供團隊查閱。  
**技術挑戰**：API 文件多由註解產生，其他文檔需手動維護，如何整合成一致的網站並自動發布。  
**影響範圍**：文件一致性、更新即時性、協作效率。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Word 檔案版控不友善，難以做差異與分支。  
2. 多種文件來源（註解產出與手寫 Markdown）難整合。  
3. 手動部署增加出錯率與延遲。  

**深層原因**：
- 架構層面：缺少將多源文件整合為單一網站的靜態生成流程。  
- 技術層面：未善用 Jekyll + Markdown 的靜態化能力。  
- 流程層面：缺少提交即更新的自動化。

### Solution Design（解決方案設計）
**解決策略**：將 Markdown 文檔與程式碼同庫管理；API 由註解工具生成 Markdown/HTML，再由 Jekyll 統一產生站點；提交至 NAS 工作目錄後由容器自動偵測變更並重建，Web Station 自動呈現。

**實施步驟**：
1. 文檔結構落地
- 實作細節：將手寫文檔置於 /docker/jekyll/_posts 與 pages；API 文件生成到 docs/ 再被 Jekyll 包含。  
- 所需資源：Jekyll、文件生成工具。  
- 預估時間：1 小時。  

2. 自動化建置
- 實作細節：以 jekyll serve --watch 在容器內偵測變更；完成後輸出至 _site。  
- 所需資源：Docker、Jekyll 容器。  
- 預估時間：30 分鐘。

**關鍵程式碼/設定**：
```yaml
# _config.yml（示意：整合 docs/ 與 posts/）
title: "Team Docs"
markdown: kramdown
collections:
  docs:
    output: true
include:
  - docs
```

實際案例：文中指出將 Markdown 與程式碼一起版控，Jekyll 自動發布 Web 版文件。  
實作環境：Jekyll on Docker、NAS Web Station。  
實測數據：  
改善前：手動部署、下載查看不便（敘述性）。  
改善後：提交即觸發重建，自動更新 Web 文件（敘述性）。  
改善幅度：部署人工步驟趨近 0（流程指標）。

Learning Points（學習要點）  
核心知識點：  
- Blogging-as-Code 概念  
- 多來源文檔整合  
- 自動化重建與發佈

技能要求：  
必備技能：Git、Markdown、Jekyll  
進階技能：CI/自動化腳本

延伸思考：  
- 可接 CI/CD 進行測試後才發布。  
- 風險：文檔結構失序。  
- 優化：建立文檔模板與 PR 模版。

Practice Exercise（練習題）  
基礎練習：新增一篇 Markdown 並在站點顯示（30 分鐘）。  
進階練習：整合自動生成的 API docs 到站點（2 小時）。  
專案練習：建立完整「代碼+文檔」單一站（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：文檔與 API 一站式呈現  
程式碼品質（30%）：結構清楚、可維護  
效能優化（20%）：重建耗時可接受  
創新性（10%）：流程自動化程度


## Case #4: 以 Docker Volume 對應實現自動重建與資料持久化

### Problem Statement（問題陳述）
**業務場景**：希望編輯 NAS 上的檔案即可觸發 Jekyll 重建，並保證內容與輸出結果在容器重建後仍可持續存在，以利長期運作與備份。  
**技術挑戰**：容器檔案系統為易失性，需將來源與輸出掛載至 NAS。  
**影響範圍**：資料安全、開發效率、部署穩定性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器內修改不會保留在主機。  
2. 不掛載目錄無法被 NAS 備份或版本控制。  
3. 未啟用 watch 無法自動重建。  

**深層原因**：
- 架構層面：未分離來源與輸出路徑。  
- 技術層面：未正確設定 Volume。  
- 流程層面：缺少自動重建策略。

### Solution Design（解決方案設計）
**解決策略**：將 NAS:/docker/jekyll 掛載到容器 /srv/jekyll；以 jekyll serve --watch 啟動，容器檔案變更偵測自動重建；_site 由 Web Station 提供。

**實施步驟**：
1. Volume 對應
- 實作細節：-v /docker/jekyll:/srv/jekyll。  
- 所需資源：Docker。  
- 預估時間：10 分鐘。  

2. 啟用 watch
- 實作細節：jekyll serve --watch，確認日誌出現 Auto-regeneration。  
- 所需資源：Jekyll 容器。  
- 預估時間：10 分鐘。

**關鍵程式碼/設定**：
```bash
docker run --name jekyll-watch --rm -it \
  -p 4000:4000 \
  -v /docker/jekyll:/srv/jekyll \
  jekyll/jekyll:latest jekyll serve --watch
```

實際案例：文中 Volume 映射 /docker/jekyll -> /srv/jekyll，日誌顯示 Auto-regeneration。  
實作環境：Synology Docker + jekyll/jekyll:latest。  
實測數據：  
改善前：容器刪除即資料遺失、需手動重建。  
改善後：資料持久化，檔案變更即自動重建（敘述性）。  
改善幅度：維運與手動重建成本大幅降低（流程指標）。

Learning Points（學習要點）  
核心知識點：  
- Docker Volume 掛載  
- Jekyll 自動重建  
- 來源與輸出分離策略

技能要求：  
必備技能：Docker CLI  
進階技能：監控與備份整合

延伸思考：  
- 可加上檔案監控告警。  
- 風險：權限錯誤導致重建失敗。  
- 優化：以 docker compose 描述環境。

Practice Exercise（練習題）  
基礎練習：掛載目錄並看到變更觸發重建（30 分鐘）。  
進階練習：加入 docker-compose.yaml 管理（2 小時）。  
專案練習：整合 NAS 備份與版本控制（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：自動重建穩定  
程式碼品質（30%）：配置清晰  
效能優化（20%）：重建耗時合理  
創新性（10%）：工具鏈整合


## Case #5: 分離建置與服務：Jekyll 負責建置、Web Station（Nginx）負責服務

### Problem Statement（問題陳述）
**業務場景**：希望就算 Jekyll 沒在跑，網站也不會掛，並讓 Web Server 用最省資源的方式服務靜態內容，以提高穩定度與效能。  
**技術挑戰**：Jekyll 自帶 server 僅適合開發預覽，不適合生產；需由 Nginx 接管對外服務。  
**影響範圍**：可用性、穩定性、效能。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 以 Jekyll 伺服器提供生產服務不穩定。  
2. 靜態內容由 Nginx 服務效率更高。  
3. 建置程序與服務綁在一起會形成單點。  

**深層原因**：
- 架構層面：缺乏職責分離。  
- 技術層面：未選用最佳靜態伺服器。  
- 流程層面：建置與服務耦合。

### Solution Design（解決方案設計）
**解決策略**：Jekyll 容器僅負責生成 _site，Web Station 使用 Nginx 提供靜態頁面，確保即使建置流程暫停，網站依舊可用。

**實施步驟**：
1. 設定 Web Station
- 實作細節：虛擬主機指向 /docker/jekyll/_site，選用 Nginx。  
- 所需資源：Synology Web Station。  
- 預估時間：15 分鐘。  

2. 關閉對外的 Jekyll server
- 實作細節：保留 jekyll build/serve 僅用於內部預覽。  
- 所需資源：Docker。  
- 預估時間：10 分鐘。

**關鍵程式碼/設定**：
```nginx
server {
  listen 80;
  server_name docs.local;
  root /docker/jekyll/_site;
  index index.html;
  location / { try_files $uri $uri/ =404; }
}
```

實際案例：文中指出「Jekyll 沒有執行，網站也不會掛掉，只要 NAS 還活著大概就沒事。」  
實作環境：Synology Web Station（Nginx）、Jekyll on Docker。  
實測數據：  
改善前：以 Jekyll 伺服服務存在風險。  
改善後：Nginx 生產服務穩定，Jekyll 僅建置（敘述性）。  
改善幅度：網站可用性顯著提升（非數值）。

Learning Points（學習要點）  
核心知識點：  
- 職責分離的架構設計  
- 靜態網站最佳化服務  
- 生產預覽環境分離

技能要求：  
必備技能：Nginx/虛擬主機設定  
進階技能：健康檢查與監控

延伸思考：  
- 可加入 CDN 或反向代理。  
- 風險：_site 與源碼不同步。  
- 優化：自動化同步與通知。

Practice Exercise（練習題）  
基礎練習：以 Nginx 提供 _site（30 分鐘）。  
進階練習：關閉 Jekyll 對外端口僅保留內網預覽（2 小時）。  
專案練習：在 Nginx 加入快取與壓縮（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：Nginx 正常服務  
程式碼品質（30%）：設定清楚可維護  
效能優化（20%）：回應速度提升  
創新性（10%）：穩定性設計


## Case #6: 首次執行 Ruby Gem 更新導致等待，透過容器日誌判斷狀態

### Problem Statement（問題陳述）
**業務場景**：第一次在 NAS 上啟動 Jekyll 容器時，等待時間超過預期，不確定是否卡住，亟需具體方法判斷是否正常執行與何時完成。  
**技術挑戰**：缺乏對容器日誌與 Jekyll 輸出訊息的認識。  
**影響範圍**：部署信心、問題排查效率。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 首次更新必要 Gems 需 1-2 分鐘。  
2. 未檢視容器日誌導致不確定狀態。  
3. 不熟悉 Jekyll 完成訊息。  

**深層原因**：
- 架構層面：部署可觀測性不足。  
- 技術層面：不知道如何查看 docker logs。  
- 流程層面：缺少標準檢查步驟。

### Solution Design（解決方案設計）
**解決策略**：使用 docker logs -f 追蹤 Jekyll 輸出，辨識「Generating... done in X seconds」與「Server running...」字樣來確認完成與端口狀態。

**實施步驟**：
1. 追蹤容器日誌
- 實作細節：docker logs -f <container>，觀察生成訊息。  
- 所需資源：Docker CLI。  
- 預估時間：5 分鐘。  

2. 確認端口與訪問
- 實作細節：docker port <container> 或 docker ps，並以 http://{NAS}:{host-port} 驗證。  
- 所需資源：瀏覽器。  
- 預估時間：5 分鐘。

**關鍵程式碼/設定**：
```bash
docker logs -f jekyll-nas

# 典型輸出
# Generating... 
#           done in 41.995 seconds.
# Server address: http://0.0.0.0:4000/
# Server running... press ctrl-c to stop.

docker port jekyll-nas
```

實際案例：文中附 Jekyll 日誌片段，首次需 1-2 分鐘更新 Gems。  
實作環境：Jekyll on Docker。  
實測數據：  
改善前：不確定是否卡住。  
改善後：清楚判斷完成訊息與端口狀態（敘述性）。  
改善幅度：排查時間縮短（流程指標）。

Learning Points（學習要點）  
核心知識點：  
- 容器日誌閱讀  
- Jekyll 完成訊息判讀  
- 端口對應檢查

技能要求：  
必備技能：Docker CLI  
進階技能：日誌收集與告警

延伸思考：  
- 可導入集中式日誌平台。  
- 風險：忽略警告訊息。  
- 優化：建立 SOP 與常見訊息對照。

Practice Exercise（練習題）  
基礎練習：透過 docker logs 確認首次建置完成（30 分鐘）。  
進階練習：撰寫 Shell 腳本監控日誌完成關鍵字（2 小時）。  
專案練習：把日誌送到 ELK/Graylog（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：能可靠判斷建置完成  
程式碼品質（30%）：監控腳本清楚  
效能優化（20%）：排查時間縮短  
創新性（10%）：告警自動化設計


## Case #7: 以 4000 端口本機預覽與 NAS 實機測試並行

### Problem Statement（問題陳述）
**業務場景**：開發者需要在不影響生產環境的情況下，快速預覽變更；同時也要驗證 NAS 上的實際端口映射與網段可達性。  
**技術挑戰**：搞清楚容器內端口與主機端口映射，並同時使用內網域名測試 Nginx 發佈。  
**影響範圍**：驗證效率、風險控制。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不熟悉容器端口映射指令。  
2. 未區分預覽（Jekyll）與生產（Nginx）。  
3. 測試路徑混亂導致誤判。  

**深層原因**：
- 架構層面：缺乏明確預覽/生產分流。  
- 技術層面：端口映射知識薄弱。  
- 流程層面：測試 SOP 不完整。

### Solution Design（解決方案設計）
**解決策略**：以 docker run -p 4000:4000 啟動預覽；同時用內網域名走 Web Station 驗證生產輸出，建立雙路測試法。

**實施步驟**：
1. 啟動預覽端口
- 實作細節：docker run -p 4000:4000 ... jekyll serve。  
- 所需資源：Docker、瀏覽器。  
- 預估時間：10 分鐘。  

2. 驗證生產域名
- 實作細節：以 http://{domain} 測試 Nginx；預覽用 http://{NAS}:{port}。  
- 所需資源：DNS/瀏覽器。  
- 預估時間：10 分鐘。

**關鍵程式碼/設定**：
```bash
docker run --rm -it -p 4000:4000 \
  -v /docker/jekyll:/srv/jekyll \
  jekyll/jekyll:latest jekyll serve --watch

# 預覽：http://{NAS_IP}:4000
# 生產（Web Station）：http://{your-domain}
```

實際案例：文中使用 4000 端口預覽與 Web Station 兩種路徑驗證。  
實作環境：Jekyll on Docker、Web Station。  
實測數據：  
改善前：預覽與生產混用導致誤判。  
改善後：雙路測試清晰、風險降低（敘述性）。  
改善幅度：驗證效率提升（流程指標）。

Learning Points（學習要點）  
核心知識點：  
- 容器端口映射  
- 預覽/生產環境分離測試  
- DNS 與內網訪問

技能要求：  
必備技能：Docker、基礎網路  
進階技能：測試自動化

延伸思考：  
- 可加入整合測試。  
- 風險：誤把預覽對外暴露。  
- 優化：限制預覽端口僅內網可達。

Practice Exercise（練習題）  
基礎練習：同時跑預覽與生產測試（30 分鐘）。  
進階練習：寫腳本自動開關預覽環境（2 小時）。  
專案練習：建立藍綠發佈流程（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：兩路測試可用  
程式碼品質（30%）：腳本清晰  
效能優化（20%）：測試時間縮短  
創新性（10%）：風險控制設計


## Case #8: 以 Git 取代單純檔案系統的版本控制限制

### Problem Statement（問題陳述）
**業務場景**：目前僅依賴 NAS 檔案系統的歷史版本或備份，無法支援分支、差異比對與細緻追蹤，影響協作與回溯。  
**技術挑戰**：在不改變 NAS 部署方式下，導入 Git 以強化版本控制能力。  
**影響範圍**：協作效率、回溯能力、審計可追溯性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 檔案系統版本控制能力有限。  
2. 缺少分支與差異工具。  
3. 難以審計變更責任。  

**深層原因**：
- 架構層面：未引入 VCS。  
- 技術層面：只用檔案備份。  
- 流程層面：缺少提交與審核機制。

### Solution Design（解決方案設計）
**解決策略**：在 /docker/jekyll 初始化 Git，採用分支/PR 流程，仍由 Web Station 發佈 _site；進一步可鏡像到私有 Git 伺服器。

**實施步驟**：
1. 初始化與提交
- 實作細節：git init、.gitignore 設定忽略 _site。  
- 所需資源：Git。  
- 預估時間：20 分鐘。  

2. 建立分支策略
- 實作細節：main 為穩定、feature/* 為開發；合併再觸發重建。  
- 所需資源：Git、團隊規範。  
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```bash
cd /docker/jekyll
git init
echo "_site" >> .gitignore
git add .
git commit -m "init jekyll content repo"
```

實際案例：文中提醒檔案系統的版本控制遠不及 Git。  
實作環境：NAS 檔案系統 + Git。  
實測數據：  
改善前：只能還原檔案版本，無分支與差異。  
改善後：具備完整 VCS 能力（敘述性）。  
改善幅度：可追溯性顯著提升（非數值）。

Learning Points（學習要點）  
核心知識點：  
- VCS 與 FS 版本的差異  
- 分支與 PR 流程  
- 部署與版控解耦

技能要求：  
必備技能：Git 基礎  
進階技能：Git Workflow 設計

延伸思考：  
- 可導入私有 Git 服務。  
- 風險：合併衝突。  
- 優化：PR 模板與檢查清單。

Practice Exercise（練習題）  
基礎練習：初始化 Git 並提交（30 分鐘）。  
進階練習：建立分支與合併流程（2 小時）。  
專案練習：私有 Git 伺服器鏡像與備援（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：版控功能完善  
程式碼品質（30%）：提交訊息規範  
效能優化（20%）：協作效率提升  
創新性（10%）：流程改良


## Case #9: 以 YAML Front Matter 標準化文件中繼資料（MSDN 範例）

### Problem Statement（問題陳述）
**業務場景**：文件分散、缺乏統一中繼資料導致搜尋、分類與佈局不一致，影響使用與維護。  
**技術挑戰**：建立可機器讀取的標頭規範，讓 Jekyll 能一致處理。  
**影響範圍**：資訊架構、一致性、可維護性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏統一的 Front Matter。  
2. 模板無法根據屬性正確呈現。  
3. 搜尋與分類混亂。  

**深層原因**：
- 架構層面：未定義資料模型。  
- 技術層面：未使用 YAML 前置標頭。  
- 流程層面：缺少編寫規範。

### Solution Design（解決方案設計）
**解決策略**：採用 YAML Front Matter 規範（參照 MSDN 範例），確保每篇文檔帶有標題、描述、關鍵字、作者等欄位，支援自動化呈現與分類。

**實施步驟**：
1. 制定模板
- 實作細節：在模板中強制要求字段。  
- 所需資源：Jekyll 佈局。  
- 預估時間：30 分鐘。  

2. 落實檢查
- 實作細節：PR 檢查 Front Matter 是否齊全。  
- 所需資源：Code Review 流程。  
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```markdown
---
title: Deploy Windows Containers on Nano Server
description: Deploy Windows Containers on Nano Server
keywords: docker, containers
author: neilpeterson
manager: timlt
ms.date: 09/28/2016
ms.topic: article
ms.prod: windows-containers
ms.service: windows-containers
ms.assetid: b82acdf9-042d-4b5c-8b67-1a8013fa1435
---
```

實際案例：文中引用 MSDN 文件使用一致的 Front Matter。  
實作環境：Jekyll 模板。  
實測數據：  
改善前：中繼資料缺失，呈現不一致。  
改善後：分類與佈局一致（敘述性）。  
改善幅度：維護成本降低（非數值）。

Learning Points（學習要點）  
核心知識點：  
- Front Matter 資料模型  
- 模板與屬性驅動渲染  
- 文件規範制定

技能要求：  
必備技能：YAML、Jekyll 佈局  
進階技能：Lint/檢查工具

延伸思考：  
- 能套用到 SEO 與站內搜尋。  
- 風險：欄位變更造成破壞性更新。  
- 優化：自動填補預設值。

Practice Exercise（練習題）  
基礎練習：新增一篇含完整 Front Matter 的文章（30 分鐘）。  
進階練習：修改模板根據屬性動態顯示（2 小時）。  
專案練習：建立 Front Matter Lint 流程（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：中繼資料完整  
程式碼品質（30%）：模板結構清楚  
效能優化（20%）：渲染穩定  
創新性（10%）：規範與自動化工具


## Case #10: 以 PR/Issue 開放式協作文件流程（參考 MSDN）

### Problem Statement（問題陳述）
**業務場景**：希望降低文件貢獻門檻，讓內外部貢獻者能直接透過 PR/Issue 提案與修正，提升內容品質與更新速度。  
**技術挑戰**：將 Markdown 文檔流程與審核機制結合。  
**影響範圍**：社群參與、內容品質、維運效率。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 傳統文件提交流程繁瑣。  
2. 缺乏透明的審核與合併機制。  
3. 知識沉澱速度慢。  

**深層原因**：
- 架構層面：未以 Git 為核心的協作流程。  
- 技術層面：Markdown 與 PR 深度整合缺失。  
- 流程層面：未定義審核責任。

### Solution Design（解決方案設計）
**解決策略**：借鑑 MSDN 作法，對每篇文件建立對應的 Markdown 檔與 Front Matter；以 PR/Issue 進行提案與審核，合併後由 Jekyll 自動建置並發布至 NAS。

**實施步驟**：
1. 倉庫與分支策略
- 實作細節：repo 對應文檔，定義 reviewer，PR 合併即觸發建置。  
- 所需資源：Git 平台。  
- 預估時間：2 小時。  

2. 貢獻導引
- 實作細節：README/CONTRIBUTING 說明提交流程與 Front Matter 規範。  
- 所需資源：文件模板。  
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```markdown
# CONTRIBUTING.md 片段（示意）
1. Fork 專案，建立 feature 分支
2. 編修 Markdown，補齊 Front Matter
3. 提交 PR，等待 Reviewer 審核
4. 合併即自動建置發布
```

實際案例：文中「MSDN 右上角 contribute 連到 GitHub，PR 合併後由 Jekyll 自動發布」。  
實作環境：Git 平台 + NAS 發布端。  
實測數據：  
改善前：閉鎖式流程，更新慢。  
改善後：社群/團隊可 PR，更新加速（敘述性）。  
改善幅度：貢獻門檻顯著降低（非數值）。

Learning Points（學習要點）  
核心知識點：  
- 文檔協作流程設計  
- PR/Issue 與發布串接  
- Reviewer 責任制

技能要求：  
必備技能：Git、Markdown  
進階技能：審核流程、合規檢查

延伸思考：  
- 可結合自動測試語法/連結完整性。  
- 風險：PR 雜訊。  
- 優化：模板與自動檢查工作流。

Practice Exercise（練習題）  
基礎練習：提交並合併一個小修正 PR（30 分鐘）。  
進階練習：建立 PR 自動檢查（2 小時）。  
專案練習：搭建完整貢獻手冊與審核機制（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：PR 流程可運作  
程式碼品質（30%）：模板與檢查清晰  
效能優化（20%）：合併到發布鏈順暢  
創新性（10%）：協作創新


## Case #11: 在低規 NAS 上驗證 Jekyll 建置可行性與性能

### Problem Statement（問題陳述）
**業務場景**：擔心低規 NAS（Atom + 2GB RAM）無法承受 Jekyll 建置，影響使用體驗與更新效率，需要基於實測決策。  
**技術挑戰**：比較 PC 與 NAS 建置耗時，評估是否可接受。  
**影響範圍**：硬體選型、體驗、成本。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. CPU 等級差距大引發疑慮。  
2. Docker on Windows 與 NAS 觀感差異。  
3. 缺少客觀數據比較。  

**深層原因**：
- 架構層面：未建立性能基準。  
- 技術層面：不同平台 I/O 與容器層差異。  
- 流程層面：未做建置時間量測。

### Solution Design（解決方案設計）
**解決策略**：以相同專案在 PC 與 NAS 分別執行 jekyll build/serve，記錄日誌中的 done in X seconds，據此評估可接受性。

**實施步驟**：
1. 量測 PC 與 NAS
- 實作細節：分別執行建置，記錄時間。  
- 所需資源：同一專案內容。  
- 預估時間：30 分鐘。  

2. 結論與決策
- 實作細節：若差距可接受（如 30s vs 42s），NAS 方案可行。  
- 所需資源：測試報告。  
- 預估時間：30 分鐘。

**關鍵程式碼/設定**：
```bash
# 觀察日誌輸出時間
# Generating...
#           done in 41.995 seconds.
```

實際案例：文中 PC 約 30s、NAS 約 42s，差距不大、可接受。  
實作環境：PC（i7-2600K/24GB）、NAS（DS-412+/Atom/2GB）。  
實測數據：  
改善前：未知效能是否可用。  
改善後：在低規 NAS 上 ~42s 可完成建置（定量）。  
改善幅度：可接受的落差（30s → 42s）。

Learning Points（學習要點）  
核心知識點：  
- 建置時間量測  
- 跨平台性能比較  
- 以數據決策

技能要求：  
必備技能：讀取日誌、基本測試  
進階技能：基準測試與報告

延伸思考：  
- 可比較增量建置。  
- 風險：資料集規模不同導致偏差。  
- 優化：I/O 與快取優化。

Practice Exercise（練習題）  
基礎練習：量測建置時間（30 分鐘）。  
進階練習：不同資料集對比（2 小時）。  
專案練習：撰寫性能評估報告（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：量測方法正確  
程式碼品質（30%）：記錄完整  
效能優化（20%）：提出改善建議  
創新性（10%）：測試設計


## Case #12: 啟用 Jekyll 增量建置以縮短重建時間

### Problem Statement（問題陳述）
**業務場景**：專案規模擴大後，全量重建時間漸長，影響迭代效率，需要縮短每次變更的建置時間。  
**技術挑戰**：預設 Incremental build 未啟用。  
**影響範圍**：開發者迭代速度、CI 時間。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 日誌顯示 Incremental build: disabled。  
2. 每次變更皆全量建置。  
3. 未使用 --incremental 參數。  

**深層原因**：
- 架構層面：沒有增量策略。  
- 技術層面：未啟用 Jekyll 增量建置。  
- 流程層面：缺少針對熱變更的優化。

### Solution Design（解決方案設計）
**解決策略**：在開發/預覽環境啟用 --incremental；在 CI 或生產建置視需求選擇全量或增量，平衡速度與一致性。

**實施步驟**：
1. 啟用增量
- 實作細節：jekyll serve --watch --incremental。  
- 所需資源：Jekyll 容器。  
- 預估時間：5 分鐘。  

2. 驗證效果
- 實作細節：修改單檔觀察重建時間縮短。  
- 所需資源：日誌觀察。  
- 預估時間：20 分鐘。

**關鍵程式碼/設定**：
```bash
docker run --rm -it -p 4000:4000 \
  -v /docker/jekyll:/srv/jekyll \
  jekyll/jekyll:latest jekyll serve --watch --incremental
```

實際案例：文中日誌提示可啟用 --incremental。  
實作環境：Jekyll on Docker。  
實測數據：  
改善前：全量重建 ~42s（示例）。  
改善後：單檔改動重建時間顯著降低（未量測具體值）。  
改善幅度：依內容變更而定（流程指標）。

Learning Points（學習要點）  
核心知識點：  
- 增量建置原理  
- 開發/生產模式權衡  
- 日誌驅動優化

技能要求：  
必備技能：Jekyll CLI  
進階技能：CI 策略分流

延伸思考：  
- 生產仍建議全量以確保一致性。  
- 風險：增量狀態不一致。  
- 優化：定期全量與快取策略。

Practice Exercise（練習題）  
基礎練習：開啟增量、修改單檔觀察（30 分鐘）。  
進階練習：撰寫腳本依分支決定增量或全量（2 小時）。  
專案練習：CI 中落地增量策略（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：增量建置可運作  
程式碼品質（30%）：腳本清楚  
效能優化（20%）：重建時間縮短  
創新性（10%）：策略權衡


## Case #13: 以靜態 HTML 降低攻擊面積、提升安全性

### Problem Statement（問題陳述）
**業務場景**：內網站過去使用 WordPress，長期面臨外掛漏洞與更新壓力，希望降低攻擊面與維護負擔。  
**技術挑戰**：用靜態化取代動態執行環境。  
**影響範圍**：資安、維運。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 動態程式與外掛帶來漏洞風險。  
2. 更新不及時易受攻擊。  
3. 低規 NAS 不利安全加固。  

**深層原因**：
- 架構層面：動態渲染 + DB。  
- 技術層面：PHP/外掛生態風險。  
- 流程層面：更新流程繁瑣。

### Solution Design（解決方案設計）
**解決策略**：改為 Jekyll 生成靜態檔，由 Nginx 提供，移除動態執行環境，僅維護內容與模板，降低攻擊面與更新頻率。

**實施步驟**：
1. 靜態化部署
- 實作細節：導入 Jekyll + Nginx 發佈。  
- 所需資源：Docker、Web Station。  
- 預估時間：1 小時。  

2. 安全維護
- 實作細節：定期更新容器映像與模板依賴。  
- 所需資源：維運流程。  
- 預估時間：持續。

**關鍵程式碼/設定**：
```bash
# 以靜態檔服務，不啟用 PHP/DB
# Nginx 僅提供 /docker/jekyll/_site
```

實際案例：文中指出靜態網站「快速且安全」。  
實作環境：Jekyll + Nginx。  
實測數據：  
改善前：WordPress 需頻繁安全更新。  
改善後：靜態站點攻擊面大幅降低（敘述性）。  
改善幅度：維護頻率降低（非數值）。

Learning Points（學習要點）  
核心知識點：  
- 攻擊面最小化  
- 靜態站安全維運  
- 依賴管理

技能要求：  
必備技能：Nginx 基礎  
進階技能：安全基線與稽核

延伸思考：  
- 可加入 WAF/反代。  
- 風險：內容更新延遲。  
- 優化：自動化建置縮短延遲。

Practice Exercise（練習題）  
基礎練習：關閉 PHP 只服務 _site（30 分鐘）。  
進階練習：容器映像更新流程（2 小時）。  
專案練習：安全基線文件與巡檢（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：僅靜態檔服務  
程式碼品質（30%）：設定明確  
效能優化（20%）：減少資源消耗  
創新性（10%）：安全流程設計


## Case #14: 以 NAS 備份與快照（Btrfs/ZFS）保護 Jekyll 內容與輸出

### Problem Statement（問題陳述）
**業務場景**：內容誤刪或模板錯誤導致輸出網站損壞，需要快速回復機制。  
**技術挑戰**：僅以檔案系統歷史不足以支援細緻回復與分支策略。  
**影響範圍**：RTO/RPO、內容安全。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未結合版本控制與快照。  
2. 快照策略未規劃。  
3. 還原流程無演練。  

**深層原因**：
- 架構層面：缺少多層保護。  
- 技術層面：未用 Btrfs/ZFS 與 NAS 備份。  
- 流程層面：未制定還原 SOP。

### Solution Design（解決方案設計）
**解決策略**：對 /docker/jekyll 啟用 NAS 快照/備份；同時以 Git 管內容；出問題先用 Git 還原，再以快照復舊完整目錄。

**實施步驟**：
1. 快照與排程
- 實作細節：每日快照與每週備份，保留 N 份。  
- 所需資源：NAS 快照/備份套件。  
- 預估時間：1 小時。  

2. 還原演練
- 實作細節：模擬誤刪，演練 Git 與快照復原。  
- 所需資源：測試環境。  
- 預估時間：2 小時。

**關鍵程式碼/設定**：
```bash
# Git 還原示意
git checkout -- path/to/file.md
# NAS 端：於快照管理介面選取時間點還原 /docker/jekyll
```

實際案例：文中提及可用 NAS 內建備份與 Btrfs/ZFS 保護。  
實作環境：Synology（支援 Btrfs）/ZFS NAS。  
實測數據：  
改善前：誤刪難快速回復。  
改善後：版本控制 + 快照雙保護（敘述性）。  
改善幅度：RTO/RPO 顯著降低（非數值）。

Learning Points（學習要點）  
核心知識點：  
- 檔案層與版本層雙保護  
- 快照策略  
- 還原演練重要性

技能要求：  
必備技能：NAS 備份/快照  
進階技能：災難復原流程

延伸思考：  
- 可加遠端備援。  
- 風險：錯誤覆寫。  
- 優化：變更前自動快照。

Practice Exercise（練習題）  
基礎練習：設定每日快照（30 分鐘）。  
進階練習：模擬誤刪並還原（2 小時）。  
專案練習：制定 DR 計畫（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：快照/備份可用  
程式碼品質（30%）：還原步驟文件化  
效能優化（20%）：RTO/RPO 改善  
創新性（10%）：保護策略設計


## Case #15: 導入網站模板與內容目錄結構，快速上線

### Problem Statement（問題陳述）
**業務場景**：從零開始整站搭建成本高，需快速導入既有模板與內容，縮短上線時間並建立一致的目錄結構，降低後續維護成本。  
**技術挑戰**：將本地模板與內容移至 NAS 指定路徑，確保 Jekyll 能正確識別與輸出。  
**影響範圍**：上線速度、可維護性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 模板與內容不在正確目錄。  
2. 缺少既有模板範本。  
3. 未遵循 _posts 與 _site 結構。  

**深層原因**：
- 架構層面：目錄結構未標準化。  
- 技術層面：未熟悉 Jekyll 規範。  
- 流程層面：移轉步驟不明確。

### Solution Design（解決方案設計）
**解決策略**：遵循文中路徑規範，將模板與內容複製至 /docker/jekyll，文章放在 _posts，輸出對應 _site，再由 Web Station 直接提供。

**實施步驟**：
1. 檔案導入
- 實作細節：COPY/rsync 到 /docker/jekyll，文章進 _posts。  
- 所需資源：File Station/rsync。  
- 預估時間：30 分鐘。  

2. 驗證與調整
- 實作細節：預覽並修正連結、佈局。  
- 所需資源：瀏覽器、編輯器。  
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```bash
rsync -av ./theme/* nas:/docker/jekyll/
rsync -av ./content/_posts/ nas:/docker/jekyll/_posts/
```

實際案例：文中「把你的網站樣板（含內容）複製到 NAS:/docker/jekyll」。  
實作環境：Jekyll on Docker、Web Station。  
實測數據：  
改善前：從零搭建耗時。  
改善後：幾分鐘完成導入、快速上線（敘述性）。  
改善幅度：上線時間顯著縮短（非數值）。

Learning Points（學習要點）  
核心知識點：  
- Jekyll 目錄約定  
- 模板移轉  
- 快速上線技巧

技能要求：  
必備技能：檔案操作、Jekyll 基礎  
進階技能：模板客製化

延伸思考：  
- 可建立多站共用模板。  
- 風險：連結與資產路徑錯誤。  
- 優化：相對路徑與資產管線。

Practice Exercise（練習題）  
基礎練習：導入模板並顯示首頁（30 分鐘）。  
進階練習：客製佈局與導航（2 小時）。  
專案練習：從舊站批次移轉內容（8 小時）。

Assessment Criteria（評估標準）  
功能完整性（40%）：模板與內容正確呈現  
程式碼品質（30%）：結構清晰  
效能優化（20%）：資產載入順暢  
創新性（10%）：模板改造



--------------------------------
案例分類
--------------------------------

1) 按難度分類  
- 入門級（適合初學者）：#2, #4, #6, #7, #8, #9, #15  
- 中級（需要一定基礎）：#1, #3, #5, #10, #12, #13, #14  
- 高級（需要深厚經驗）：#11（性能評估可視為中高），#12（策略化應用，可歸中高）

2) 按技術領域分類  
- 架構設計類：#1, #5, #12, #13  
- 效能優化類：#11, #12  
- 整合開發類：#2, #3, #4, #7, #15  
- 除錯診斷類：#6, #7, #11  
- 安全防護類：#1, #13, #14

3) 按學習目標分類  
- 概念理解型：#1, #3, #5, #13  
- 技能練習型：#2, #4, #6, #7, #15  
- 問題解決型：#8, #9, #11, #12, #14  
- 創新應用型：#10（開放協作流程）

--------------------------------
案例學習路徑建議
--------------------------------
- 建議先學順序：  
1) 基礎搭建與預覽：#2（私有部署）、#4（Volume/自動重建）、#6（日志判讀）、#7（端口與雙路測試）  
2) 模板與內容：#15（模板導入）、#9（Front Matter 規範）  
3) 工作流整合：#3（Blogging-as-Code）、#8（Git 版控）  
4) 生產化與架構：#5（建置/服務分離）、#1（靜態化取代動態）、#13（安全）  
5) 效能與可行性：#11（效能驗證）、#12（增量建置）  
6) 維運與協作：#14（備份快照 DR）、#10（PR/Issue 協作）

- 依賴關係：  
#4 依賴 #2（需容器與目錄）  
#5 依賴 #2、#4（需有 _site 輸出）  
#3 依賴 #8、#9（版控與規範）  
#12 依賴 #4/#6（能看懂日誌並啟動 serve）  
#14 依賴 #8（版控）與 NAS 管理  
#10 依賴 #3/#8（文檔與版控）

- 完整學習路徑建議：  
先完成私有化 Jekyll 基礎環境（#2、#4、#6、#7），再導入模板與規範（#15、#9）；然後建立文件與程式碼共治流程（#3、#8）；進一步完成生產化佈署與安全強化（#5、#1、#13）；接著以數據驗證可行性並優化建置效率（#11、#12）；最後建立備援/快照與開放協作體系（#14、#10），形成一條從搭建、規範、部署、優化到治理的閉環。