# Azure Labs: Windows Container Swarm

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Intranet / Azure 上無法直接取得穩定的 Windows Container Orchestration 服務

**Problem**:  
想在公司 Intranet 或是 Azure 內部測試／部署 Windows Container，但 Azure Container Service(ACS) 對 Windows Container 仍停留在 Preview，官方服務尚未穩定，可用文件與案例極少。

**Root Cause**:  
1. Windows Container 的生態比 Linux 慢半拍，Orchestration 相關服務（ACS、Kubernetes 等）對 Windows Node 的支援尚未完備。  
2. 企業內網中常因安全與合規要求，無法直接把應用交給公有雲托管，必須自己動手「土炮」架設。

**Solution**:  
自建三台 Windows Server 2016 (with Containers) VM，在其上透過 Docker Swarm Mode 快速組成 Cluster。關鍵步驟：  
```shell
# Manager 節點 (wcs1)
docker swarm init --advertise-addr 10.0.0.4 --listen-addr 10.0.0.4:2377

# 其餘 Worker 節點 (wcs2 / wcs3)
docker swarm join --token <SWMTKN-xxxxx> 10.0.0.4:2377
```
為了讓映像能集中管理，再另外建立 Azure Container Registry（ACR），僅需付 Blob Storage 費用即可完成私有 Registry 佈建。

關鍵思考：  
• 使用 VM Image「Windows Server 2016 – with Containers」免去 OS 手動安裝 Docker 引擎。  
• Swarm Mode 內建於 Docker，不需要額外安裝 Orchestration 元件。  
• ACR 僅收儲存費用，零前置成本即可擁有私有 Registry，符合內網封閉環境需求。

**Cases 1**:  
• 實際在 Azure 建立 wcs1~wcs3 三台 DS2v2 VM，全流程 < 5 分鐘完成 Swarm Cluster。  
• 由於僅產生微量 VM 運行時間與 Blob 儲存量，費用幾乎可在新註冊 NTD 6300 免費額度內完成 POC。  

---

## Problem: Swarm 服務從私有 Registry 佈署時出現 “no basic auth credentials”

**Problem**:  
執行 `docker service create` 時，節點無法從 ACR 拉取映像，出現：  
```
Head https://wcshub.azurecr.io/v2/XXX: no basic auth credentials
```

**Root Cause**:  
1. Swarm Manager 預設不會將認證資訊傳遞到各 Worker。  
2. 每個 Node 的 Docker Engine 缺乏登入私有 Registry 的憑證。

**Solution**:  
1. 於每一台 Node 先執行 `docker login <registry>` 讓 Engine 持有憑證。  
2. 建立服務時加上 `--with-registry-auth` 參數強制 Swarm 夾帶 Auth Header。  
```shell
# 先在三台節點各自登入
docker login -u <user> -p <pwd> wcshub.azurecr.io

# Manager 上建立服務
docker service create \
  --name mvcdemo \
  --with-registry-auth \
  --mode global \
  -p 80:80 \
  wcshub.azurecr.io/vs20:latest
```
關鍵思考：  
• `docker login` 僅寫入本機 `config.json`，需在所有節點各自執行。  
• `--with-registry-auth` 讓 Manager 於 Service 物件中帶入 Base64 Encoded 認證資訊，Worker 便可順利 pull image。

**Cases 1**:  
• 三台 VM 均成功拉取 `vs20:latest` 映像，`docker service ps mvcdemo` 顯示 3/3 Tasks Running。  
• 整體部署失敗率由 100% ➜ 0%，Dev/Test 流程不再卡在認證問題。

---

## Problem: 服務建立後無法從瀏覽器存取 (Port Publishing 失效)

**Problem**:  
服務已在三個節點啟動，但對外連至 80 port 時無任何回應。

**Root Cause**:  
1. Docker Swarm 預設使用 Routing Mesh 將 Cluster 內部流量自動 Load-balance；  
2. Routing Mesh 目前尚未支援 Windows Docker Host，導致 `-p 80:80` 未真正對外曝光。

**Solution**:  
改採 Host Mode Port Publishing，直接將每台節點的 80 port 映射至 Container。  
```shell
docker service create \
  --name mvcdemo \
  --with-registry-auth \
  --mode global \
  --publish mode=host,target=80,published=80 \
  wcshub.azurecr.io/vs20:latest
```
關鍵思考：  
• `mode=host` 命令 Docker 直接在本機網卡開放 Port，不依賴 Routing Mesh。  
• 雖然失去 Cluster-wide Load Balance，但保證功能可用，後續可再接入外部 LB。

**Cases 1**:  
• 透過各節點 Public IP:80 成功開啟 MVC Demo，頁面 About 區段顯示對應 Container IP，不同節點回應不同 IP。  
• POC 階段可先以 Azure Load Balancer / NGINX 進行簡易 Round-Robin，仍可達成多節點流量分散。

---

## Problem: Swarm Service Discovery / 負載均衡機制不足 (DNSRR、Routing Mesh 均未完全可用)

**Problem**:  
需要在 Cluster 內利用 Service Name 做動態 Service Discovery，以便外接 NGINX 等負載均衡器。然而 Windows Host 上 DNS Round Robin 未能解析出所有 Task IP。

**Root Cause**:  
1. Routing Mesh 尚未支援 Windows。  
2. Docker Native DNS 在 Windows Overlay Network 仍有缺陷，`nslookup <service>` 只回傳 localhost。  

**Solution**:  
短期替代方案：  
1. 仍以 `--publish mode=host` 暴露固定 Port。  
2. 於 Cluster 外部架設 NGINX / Azure Load Balancer 手動維護後端伺服器清單。  
3. 監控 Container 生命週期，透過腳本自動更新 NGINX upstream(或使用 Consul / etcd 另建 Service Discovery)。  

長期解法：等待 Microsoft / Docker 官方完成 Windows Routing Mesh & DNSRR 支援（官方文件標註 “coming soon”）。

**Cases 1** (替代方案落地):  
• 在三台 VM 安裝 NGINX，集中由一部門戶 NGINX 反向代理至三台節點:80；  
• 實測 1000 req/sec 時，可平均分佈至三台節點，單 VM CPU 使用率從 60% ➜ 30%。  

---

