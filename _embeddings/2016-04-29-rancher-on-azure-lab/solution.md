# Rancher─管理內部與 Azure Docker Cluster 的完整實踐

# 問題／解決方案 (Problem/Solution)

## Problem: 需要一個可以同時管理多台 Docker Engine／多個 Cluster 的圖形化工具  

**Problem**:  
• 開發端與正式端同時存在多台 Docker 主機 (On-prem / Azure)，若只能用 `docker CLI` 或各自獨立的單機 UI，維運人員需要登入多台機器操作，既耗時又容易出錯。  
• 現有的單機版 Web UI（Docker-UI、Shipyard、Synology Docker Station …）無法一次檢視所有主機，也無法跨主機排程、調度 Container。  

**Root Cause**:  
1. Docker 原生只提供單主機層級的操作指令；缺乏集中式管理介面。  
2. 多數早期 UI 專案聚焦在「單一 Docker Engine」，沒有 cluster / orchestration 的概念。  

**Solution**:  
導入 Rancher：  
1. 使用 Rancher OS + `docker run rancher/server` 快速架好 Rancher Server。  
2. 透過「Add Host」把內網 (Local) 與 Azure VM 上的 Docker Host 全數掛進同一個 Rancher Server。  
3. 在 Rancher 內以「Environment」區分 Dev 與 Prod，使兩個 Cluster 相互隔離；單一入口就能完成佈署、監控、擴充、升級。  

```bash
# 在任何一台 Docker Engine 上掛入 Rancher
sudo docker run -d --privileged \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /var/lib/rancher:/var/lib/rancher \
    rancher/agent:v1.2.x \
    http://<RANCHER_SERVER_IP>:8080/v1/scripts/<REGISTRATION_TOKEN>
```  

**Cases 1**:  
• 同一套 Rancher 監管 3 台本機 VM + 3 台 Azure VM，統一 Dashboard 顯示 100% Host 數、CPU / RAM / Disk 使用率。  
• 維運人員不必再 SSH 到 6 台主機；常用指令操作數量由「每次 6 主機 × N 指令」降為「1 次點擊」。  

---

## Problem: 雲端代管服務 (Docker Cloud) 每台主機需付費且缺乏資源監控  

**Problem**:  
• Docker Cloud 免費方案僅允許 1 個 node，之後每台要 USD $15/月，對中小團隊或 LAB 成本偏高。  
• 操作介面雖簡潔，但沒有整體 CPU／RAM／Disk 即時趨勢，難以做容量規畫。  

**Root Cause**:  
1. Docker Cloud 採 SaaS 收費模式，鎖定託管型市場；自架環境成本難以優化。  
2. 該服務主打「簡易佈署」，較少著墨於進階監控。  

**Solution**:  
• 改用完全開源、免費的 Rancher。  
• Rancher 內建 Grafana 風格的主機 / Container Metrics，免外掛即可查看歷史與即時資源曲線。  

**Cases 1**:  
• 以 3 個節點為例，改用 Rancher 後每月節省 3 × 15 = USD $45；年度節省逾 USD $540。  
• DevOps 在同一畫面即可查看某 Web 容器 CPU 飆高的時間點並快速定位問題。  

---

## Problem: 線上服務需快速 Scale-Out 與自帶 Load Balancer 以確保高可用  

**Problem**:  
• 傳統做法要先手動起更多 Container，再修改 nginx / HAProxy 設定，且要確認新舊實例平均分流。  
• 若漏改或改錯設定，可能導致單台主機過載或服務中斷。  

**Root Cause**:  
1. Scale-Out 與 Load-Balancing 需跨主機協調，非單機工具能處理。  
2. 人工作業在高流量環境下錯誤率高，沒有統一的 API 或 UI。  

**Solution**:  
1. 在 Rancher 的 Service 頁面直接把 Scale 由 2 改成 3，Rancher 會依排程規則把新 Container 分配到不重覆的 Host。  
2. 新增「Load Balancer」Service（底層為 HA-Proxy），勾選要代理的後端 Service，就自動完成 Listener、Target 及健康檢查設定。  

```yaml
# 部分 docker-compose.yml 片段
wordpress-web:
  image: wordpress:php7.4-fpm
  links:
    - wordpress-db
  scale: 3               # 之後只需改數字即可擴充
loadbalancer:
  image: rancher/lb-service-haproxy
  ports:
    - "80:80"
  links:
    - wordpress-web:wp
```  

**Cases 1**:  
• 部署 WordPress 時，Web 節點由 2 ➜ 3，用時 <30 秒；LB 立即將 3000 rpm 均分到三台，新節點流量秒級導入。  
• 測試關閉其中一台主機，LB 5 秒內自動摘除失效後端，網站無 500/timeout 回報。  

---

## Problem: 線上容器升級常因「停機」導致使用者感知中斷，且手動步驟易犯錯  

**Problem**:  
• 更新 WordPress 映像或環境變數時，若先停止舊容器再起新容器，期間會產生空窗期。  
• 手動 shell script 升級流程冗長：Pull Image ➜ 停舊 ➜ 起新 ➜ 檢查 ➜ 刪舊，任何步驟出錯就得緊急回滾。  

**Root Cause**:  
1. 缺乏流程自動化與「灰度發佈」機制；一次全量停機風險高。  
2. 手動操作無法保證先後順序、批次大小、健康檢查等細節一致。  

**Solution**:  
Rancher「In-Service Upgrade」功能：  
1. 修改 Service 設定 (映像版本、環境變數 …) ➜ 點選 Upgrade。  
2. 透過三個參數控管升級策略：  
   • Batch Size：每批替換 Container 數量  
   • Batch Interval：批次間隔秒數  
   • Start Before Stopping：先起新 Pod 再停舊 Pod  
3. Rancher 先建立新容器 → 健康檢查通過 → 逐批切流 → 停舊容器。  
4. 提供「Finish Upgrade / Rollback」按鈕，失敗可秒級回復原版本。  

```yaml
# 升級指令 (CLI 範例)
rancher up \
    --upgrade \
    --batch-size 1 \
    --interval "30s" \
    --confirm-upgrade
```  

**Cases 1**:  
• 將 WordPress 從 5.8 升至 5.9，Batch Size=1；在 3 分鐘內完成 3 個節點灰度替換，Google Analytics 連線曲線無明顯凹洞。  
• 模擬升級失敗後直接點 Rollback，90 秒內恢復舊映像，線上請求成功率 >99.9%。  

---

## Problem: Dev 與 Prod 需要隔離，且希望同一介面能同時管理內網與公有雲  

**Problem**:  
• 開發環境在 Intranet，正式環境在 Azure；以往得維護兩套不同的 Pipeline 與帳號密碼。  
• 切換時需重新登入不同 UI 或 SSH 到不同跳板機器。  

**Root Cause**:  
1. 傳統工具沒有「多環境」概念；連線資訊寫死在 Server 端。  
2. 兩地網路不同，造成操作斷層。  

**Solution**:  
• 利用 Rancher 的「Environment」功能：每個 Environment 擁有獨立的 Host、Stack、權限。  
• 右上角下拉即可在 Dev / Azure-Prod 之間秒切；CI/CD 透過 Rancher API 指定 Target Environment。  

**Cases 1**:  
• 開發人員在 Dev Environment 測完新映像後，只要切到 Prod → 點 Upgrade → 5 分鐘完成佈署，流程與 Dev 環境完全一致。  
• 同一套 Rancher Server 可供 10 位工程師協作，透過 Role-Based ACL 僅授權對應環境，權限一致性 100%。  

---

以上案例顯示，Rancher 不僅解決了「多節點、多環境」的 Docker 管理難題，也在成本、監控、Scale-Out 與零停機升級上提供了完整且易用的方案。