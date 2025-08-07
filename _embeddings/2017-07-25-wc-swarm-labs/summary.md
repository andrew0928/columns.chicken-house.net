# Azure Labs: Windows Container Swarm

## 摘要提示
- Azure 容器生態系: ACR、ACS、ACI 等服務已趨完整，但 Windows Container 功能仍落後。
- 架設目標: 在 Azure 以三台 Windows Server 2016 VM 手動佈署 Docker Swarm Cluster。
- 私有映像庫: 透過 Azure Container Registry 建立零月租、按使用付費的私人 Registry。
- Swarm 建置: 使用 `docker swarm init/join` 將 wcs1 設為 Manager，其餘兩台加入為 Worker。
- 映像推送: 先 `docker login` ACR，再 `docker pull‧tag‧push` 將 ASP.NET MVC 範例上傳。
- 服務部署: 以 `docker service create --with-registry-auth` 全域模式發布並修正 Port Mapping。
- 網路機制: 解析 Overlay Network、Routing-Mesh 與 Publish-Port 的差異及限制。
- 功能缺口: Windows 版 Swarm 尚不支援 Routing-Mesh，DNSRR 亦未如文件宣稱可用。
- 疑難排解: 必須逐節點登入 Registry、以 Host 模式發布埠才能順利對外服務。
- 展望: Container 技術將成為跨平台封裝與佈署標準，Hyper-V Container 日後可原生執行 LinuxKit。

## 全文重點
本文示範如何在 Azure 環境手動建立三台 Windows Server 2016 Datacenter – with Containers 的虛擬機，並組成 Docker Swarm Mode 叢集，彌補目前 ACS 尚未正式支援 Windows Container 的缺口。步驟包含：(1) 建立 VM 與設定虛擬網路；(2) 以 Azure Container Registry 架設私人映像庫，只需負擔儲存費即可使用；(3) 在 Manager 節點執行 `docker swarm init`，記下產生的 Join Token，再於其他節點以 `docker swarm join` 加入叢集；(4) 先 `docker login` ACR，將本地或 Docker Hub 上的 ASP.NET MVC 範例映像重新標記並 Push 至 ACR；(5) 以 `docker service create --name mvcdemo --with-registry-auth --mode global --publish mode=host,target=80,published=80` 在每一節點各部署一份服務。  
過程中作者踩到數個 Windows 特有地雷：Swarm 的 Routing-Mesh 尚未支援 Windows，因此單純的 `-p 80:80` 無法讓瀏覽器連線，必須改用 Host Publish 模式；另外 Docker 原生 DNS Round-Robin（DNSRR）在 Windows 亦無法查詢到其他容器 IP，導致 Service Discovery 與內部負載平衡功能受限，需依賴外部負載平衡器如 NGINX。最後，作者提醒 Container 與 Orchestration 已是必備技能，未來 Windows Hyper-V Container 將能直接執行 Linux 映像，真正落實「Package once, Run everywhere」。

## 段落重點
### 前言與動機
說明 Azure 容器服務日益完備，唯獨 Windows Container 支援相對落後；因某些場景必須在企業內網自行布建，作者決定以 Azure 快速搭建 Windows Swarm Cluster，同時分享踩雷經驗，讓有需求者少走冤枉路。

### 安裝與設定
本節分三步：1) 於 Azure 建立三台 “Windows Server 2016 Datacenter – with Containers” VM，命名 wcs1~3；2) 透過入口網站建立 Azure Container Registry（範例名 wcshub），並啟用 Admin 帳號供後續登入；3) 以 wcs1 為 Manager 執行 `docker swarm init --advertise-addr 10.0.0.4`，再在 wcs2、wcs3 執行 `docker swarm join …` 加入叢集，完成基本環境。

### 建立 Azure Container Registry
解釋 ACR 僅按儲存量計價、服務本身免費，非常適合作為專屬 Registry。示範如何在入口網站填寫名稱、區域後即快速完成，並於 Access Keys 中啟用 Admin 使用者與密碼，以便 Docker 客戶端認證。

### 設定 Swarm Cluster
詳細列出在 Manager 與 Worker 節點執行的指令及輸出，說明 Swarm 架構需至少一台 Manager；完成後即擁有可用的三台節點叢集，後續即可部署服務。

### Push Image to Registry
示範先 `docker login -u <acrName>` 登入 ACR，再將 Docker Hub 上的 `andrew0928/vs20:latest` 拉回、重新標記為 `wcshub.azurecr.io/vs20:latest` 並 Push。強調私有 Registry 可提升拉取速度與安全性，尤其在多節點 Swarm 情境下更顯重要。

### Create Service
用 ASP.NET MVC 範例映像作為示範。首次嘗試僅以 `-p 80:80` 推出服務，但因 Windows 缺少 Routing-Mesh 導致瀏覽器無法連線。經排查後改用 `--publish mode=host,target=80,published=80` 與 `--with-registry-auth`，並在每節點事先 `docker login`，最終成功讓三個節點各自對外提供服務。介紹 `docker service ls‧ps` 指令與 `--mode global/replicas` 差異。

### Overlay Network
說明 Swarm 會自動建立 ingress Overlay Network，用來跨主機讓容器互聯並支援 Routing-Mesh；Linux 上可直接達成負載平衡，而 Windows 目前尚未支援，官方文件僅承諾 “coming soon”，因此無法使用預期的透明負載均衡功能。

### DNSRR (Docker Native DNS Round Robin)
作者嘗試改用 `--endpoint-mode dnsrr` 實驗內建 DNS Round-Robin，並在同一網段建立 console 容器測試，但 Windows 版 Docker DNS 依然查不到其他服務 IP，只能透過手動取得 IP 來互 Ping，顯示該機制尚未落實，若需負載平衡仍得仰賴外部 LB。

### 後記
總結 Container 與 Orchestration 的重要性，並展望 Hyper-V Container 未來可直接執行 LinuxKit 映像，真正實現「Package once, Run everywhere」。鼓勵讀者把握時機學習 Docker，越早投入越能在日後跨平台雲端部署浪潮中佔得先機。

