# Azure Labs: Mixed-OS Docker Swarm

# 問題／解決方案 (Problem/Solution)

## Problem: 在開發／部署流程中，難以快速重建「Windows + Linux」混合環境

**Problem**:  
團隊希望在本機或雲端快速重現與​ Production 相同的 Windows + Linux 混合架構 (例如 StackOverflow​ 的做法)，但傳統做法需手動建立多台 VM、維護 OS 相依服務版本，門檻高且更新流程繁瑣，導致 CI/CD 效率低落。

**Root Cause**:  
1. Windows 與 Linux 長期在不同管理模式下維運，缺乏單一 API 可同時操作兩種 OS。  
2. 各開發人員本機硬體／網段差異大，VM 影像一旦過時即需重新發佈。  
3. 缺乏「一次定義、到處執行」的標準化封裝方式。  

**Solution**:  
採用 Docker 容器 + Azure VM + Swarm mode。  
1. 於 Azure 建立三台 Windows Server (wcs1~wcs3) 與一台 Ubuntu Server (lcs4)；所有 VM 位於同一 Virtual Network。  
2. 在 wcs1 初始化 `docker swarm init` 作為 manager，lcs4 透過 `docker swarm join --token …` 加入同一叢集。  
3. 之後任何 Windows／Linux 應用皆以容器映像檔發佈，只需 `docker stack deploy` 或 `docker service create` 即可還原整套環境。  

該方案能統一 API、簡化 VM 管理，並讓開發者以 `docker-compose` 一鍵拉起完整混合環境。

**Cases 1**:  
• 成功在 4 台 VM 上形成單一 Swarm；新進人員僅需安裝 Docker CLI、複製 `docker-compose.yml` 便可 10 分鐘內重建環境。  
• 實際使用 Azure 免費額度下，兩日實驗僅花費約 NT$600 (≈USD 20)，成本 < 免費額度 1/10。

---

## Problem: Swarm 在 Mixed-OS 叢集中「把 Linux 映像排到 Windows 節點」造成服務不停重啟

**Problem**:  
建立 NGINX (Linux) 服務時，Swarm manager 將 task 調度到 Windows 節點 (wcs2)。Windows 無法啟動 Linux 映像，導致 container 連續失敗、產生大量 retry 及資源浪費。

**Root Cause**:  
Swarm 的排程器預設只考量資源量，並不檢查「映像所需 OS 與 Node OS 是否一致」，因此在 Mixed-OS 叢集容易產生 OS 不相容的排程結果。

**Solution**:  
1. 先為每個 Node 加上明確 `os` 標籤  
   ```
   docker node update --label-add os=windows wcs1
   docker node update --label-add os=windows wcs2
   docker node update --label-add os=windows wcs3
   docker node update --label-add os=linux   lcs4
   ```  
2. 建立服務時加上 Constraint，強制排程至相符 OS  
   ```
   docker service create \
     --name web \
     --replicas 3 \
     --network ingress \
     --constraint 'node.labels.os==linux' \
     nginx
   ```  
3. Swarm 依 Constraint 僅將 NGINX 任務派送到 lcs4 (Ubuntu)。

此方法透過 Label + Constraint 讓／避免跨 OS 調度，根本解決因 OS 不相容產生的無限重試。

**Cases 1**:  
• 修正後 NGINX 3 個 Replica 全部運行於 lcs4，`docker service ps web` 顯示 3/3 Running，重試次數由數十次降為 0。  
• 叢集 CPU 抖動與網路雜訊顯著降低；排程成功率提升到 100%。

---

## Problem: Windows Container 缺乏完整 DNSRR / Routing-Mesh，服務之間無法以 Service Name 互相解析

**Problem**:  
在 Mixed-OS 叢集中測試 DNS Round-Robin (`--endpoint-mode dnsrr`) 時，Linux 容器 (busybox) 使用 `nslookup mvcdemo`、`nslookup console` 均無 DNS 紀錄；Windows 容器更無法查詢 127.0.0.11。導致應用無法依 Service Name 相互通訊與自動負載平衡。

**Root Cause**:  
1. 當前 Windows Container Networking 尚未完整實作 Docker Native DNS/Routing-Mesh，無法註冊 Service A/AAA 記錄。  
2. 官方文件與 Demo 亦以「在叢集外部再架一台 NGINX 並手動寫死動態 Port」作為 workaround，證明功能尚未 GA。  

**Solution**:  
短期暫行方案  
a) 於叢集外 (或 Linux Node 上) 部署 NGINX／HAProxy，手動維護 Upstream 名單。  
b) Windows 服務間以 Container 内 IP 或 Docker Publish Port 直接通訊。  
長期方案  
等待 Microsoft 釋出支援 Linux Container on Windows Server 與 Routing-Mesh 更新後，再改回原生 Service Discovery。  

**Cases 1**:  
• 官方 PM Demo (影片 7:20) 亦在獨立 Windows Server 手動編輯 `nginx.conf` 指向三個動態 Port，驗證當前僅能用外部 LB 變通。  
• 對現場系統影響：每增加 / 重啟一個 Windows 容器須重新產生 NGINX 設定，運維成本高。待未來 Windows Networking 更新可望一次消除此人工步驟。

---

