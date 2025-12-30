---
layout: synthesis
title: "Azure Labs: Windows Container Swarm"
synthesis_type: summary
source_post: /2017/07/25/wc-swarm-labs/
redirect_from:
  - /2017/07/25/wc-swarm-labs/summary/
---

# Azure Labs: Windows Container Swarm

## 摘要提示
- Azure 容器生態: Azure 在 Registry、Orchestration、Web App、ACI 等面向已趨完整，降低自行架設門檻。
- Windows Container 落差: 相較 Linux，Windows Container 支援較慢，仍有多處限制與踩雷點。
- 實作環境: 以 Azure 快速建立 3 台 Windows Server 2016 with Containers VM，組成 Swarm 叢集。
- 私有 Registry: 使用 Azure Container Registry，僅收儲存費用，適合團隊維護專屬映像檔。
- Swarm 啟用: 以 docker swarm init/join 建立 Manager/Worker，快速完成叢集設定。
- 部署服務: 以 docker service create 部署 ASP.NET MVC 範例，需處理私有 Registry 認證。
- 認證要點: 每個節點皆需 docker login，並在建立服務時加上 --with-registry-auth。
- 網路與發布: Windows 尚不支援 Routing Mesh，改用 --publish mode=host 映射主機埠。
- Overlay Network: 叢集會建立 ingress overlay，用於跨節點虛擬網路與服務互通。
- DNSRR 限制: 依文件應支援 DNS 服務發現，但實測無法依服務名解析多實例，建議以外部 LB 因應。

## 全文重點
本文記錄在 Azure 上以 Windows Container 搭配 Docker Swarm 進行叢集部署的實作經驗與踩雷重點。作者指出 Azure 的容器相關服務日益完善（ACR、ACS/AKS、Web App for Containers、ACI），但 Windows Container 支援仍相對滯後，特別是某些網路與服務發現能力尚未齊備。因有在內網與 Windows 環境導入的需求，作者以 Azure 快速建立三台「Windows Server 2016 Datacenter – with Containers」VM（wcs1、wcs2、wcs3），並以 docker swarm init 在 wcs1 啟動 Manager，再用 join 指令讓其他節點加入，迅速完成 Swarm 叢集。

在映像管理上，作者推薦使用 Azure Container Registry（ACR）作為私有 Registry，僅需支付儲存空間費用；建立後啟用 Admin User 並設定金鑰，透過 docker login 登入，再以 docker tag/push 將自有映像（例如 ASP.NET MVC 範例 vs20）推送到 ACR。部署服務時，因取用私有 Registry，必須在每個節點先行 docker login，且於 docker service create 時加入 --with-registry-auth，使 Manager 能將認證帶到各節點拉取映像。服務參數上，--name 指服務名、--mode 可選 global（每節點一份）或 replicas（由 Manager 排程），-p/--publish 負責對外埠口發布。

在網路層，Swarm 會自動建立 ingress overlay network，用於跨節點虛擬網路與服務內部通訊。理想狀況下，使用 Routing Mesh 可讓對任一節點的已發布埠進行負載分散到所有實例，但目前 Windows 主機尚未支援 Routing Mesh。為讓服務可從外部連通，作者改用 --publish mode=host,target=80,published=80，直接將容器埠綁定到各節點主機埠，實現一對一映射，雖能讓每個節點各自對外提供服務，但不具叢集層級的內建負載平衡。

作者再嘗試使用 Docker 原生 DNS Round Robin（DNSRR）與內建 DNS 進行服務發現與負載，但實測在同一 overlay 下，無法以服務名查得所有實例 IP（nslookup 僅回傳單一或無法解析），雖然已知其他容器 IP 時可互通，但欠缺自動化的服務發現使得以 NGINX 等外部 LB 進行動態後端更新變得困難。文件建議在 Windows 上暫以 DNSRR 搭配外部 LB 作為替代，但實務上仍存在限制。最後，作者總結：在 Windows 環境導入容器與 Swarm 仍需面對網路與服務發現的不完整；然而容器標準化鏡像與部署生態優勢明顯，學習與實作價值高，待 Windows 支援 Routing Mesh 與更完善的 DNS 服務發現後，體驗將更成熟。

## 段落重點
### 安裝與設定
本文以 Azure 作為實作場域，因其可快速建立具容器支援的 Windows VM 並簡化安裝設定。作者先提醒需有可用的 Azure 訂閱（新用戶有免費額度），接著將展示如何從零建立一個可用的 Windows Container + Docker Swarm 叢集，並補充因 Windows 支援落後而可能遇到的坑洞與解法。整體流程分為：建立三台 Windows 2016 with Containers 的 VM、建立 ACR 私有 Registry、設定 Swarm Cluster。選擇 Azure 的目的在於縮短環境建置時間，把重點放在 Swarm 的部署與操作上，也利於讀者快速複製實驗情境。

### 建立 Windows 2016 VM (with containers) x 3
在 Azure 建立三台 VM，直接選用「Windows Server 2016 Datacenter - with Containers」映像，命名 wcs1、wcs2、wcs3。作者使用 Standard DS2 v2（SSD）並將資源置於同一 Resource Group（wcsdemo），除 VM 規格外多採預設值。此步驟可視為「無腦」流程，因為容器功能已預先安裝好，省去繁瑣的 OS 設定。三台 VM 部署完成後即可進入後續 Registry 與 Swarm 設定，充分利用 Azure 的自動化與快速就緒特性。

### 建立 Azure Container Registry
為了在叢集化情境下快速取得私有映像、減少拉取延遲並控管版本，作者建立 Azure Container Registry（ACR），並強調 ACR 本身不收費、僅計算儲存成本，對初期實驗幾乎是零門檻。建立時僅需命名與選擇區域，本例命名為 wcshub；完成後務必啟用 Admin User 並設定密碼，後續推送/拉取映像會用到。私有 Registry 的價值在於：多節點同時拉取映像時速度更可控、權限更安全，也利於團隊內部版本治理與部署一致性。

### 設定 Swarm Cluster
以 RDP 登入各 VM，選定 wcs1 為 Manager，在其上執行 docker swarm init --advertise-addr <wcs1-ip> --listen-addr <wcs1-ip>:2377，取得加入 Token。接著於 wcs2、wcs3 執行 docker swarm join ... 成為 Worker。完成後叢集可用，幾乎不比 ACS/AKS 慢多少。這個步驟凸顯 Swarm 的低門檻與內建性：原生命令即可快速組成叢集，無需額外安裝協調器元件，是 Windows 容器初探叢集時的捷徑。

### Deploy Service On Docker Swarm
本節改以實際部署示範 ASP.NET MVC 範例（會回報伺服器 IP 以便觀察分佈狀況），對比單機 docker run 與叢集 docker service create 的差異。重點說明 service 的概念、模式（global/replicas）、埠口發布，以及使用私有 Registry 的認證處理。最終將展示如何在每個節點看到對應的容器實例與網頁回應，並說明在 Windows 上需要調整發布策略以避免 Routing Mesh 未支援的限制。

### Push Image to Registry
先 docker login 到 ACR（使用 wcshub.azurecr.io 與 Admin User），再透過 docker pull 取得既有映像、docker tag 重新命名到私有 Registry 命名空間、最後 docker push 推送上 ACR。作者展示完整命令與輸出，並強調在 Swarm 多節點拉取時使用近端私有 Registry 的效益：降低外網依賴、加快多節點同步速度、提升可控性與安全性。此步驟亦為後續部署建立統一來源。

### Create Service
以 docker service create 建立服務：--name 指定服務名、--mode global 讓每節點各跑一份、-p 或 --publish 設定對外埠口；因映像位於私有 Registry，需在每個節點先 docker login，並於建立服務時加入 --with-registry-auth 讓 Manager 代傳認證。作者示範在 Windows 上若僅用 -p 80:80 會遇到無法從外部連入的問題，改用 --publish mode=host,target=80,published=80 後即可分別以各節點公網 IP:80 連線成功，但這種做法是一對一映射，不具叢集負載平衡效果。

### Overlay Network
說明 Swarm 的 overlay network（ingress）如何在不同主機間建立虛擬私網，以支援跨節點容器互通。理想狀態可搭配 Routing Mesh：對任一節點已發布的埠都能導向所有服務實例並負載分散。然而目前 Windows 主機尚未支援 Routing Mesh，因此單純 -p 80:80 的直覺做法在 Windows 上不可行。此限制導致需改用 host 模式發布，或引入外部負載平衡器才能取得類似體驗。

### DNSRR (Docker Native DNS Round Robin)
依官方文件，Windows 可暫以 --endpoint-mode dnsrr 配合 Docker 內建 DNS 做服務發現與流量分散，並搭外部 LB（如 NGINX）實現負載平衡。作者實測：在同一 overlay 下建立多副本服務與 console 容器後，透過容器內 nslookup 無法解析出該服務的多個實例 IP；雖可直連已知 IP 互通，但缺少可用的服務發現使自動化負載與擴縮難以落地。結論是目前 DNSRR 在 Windows 上仍不如預期，需以外部 LB 和手動或額外機制維護後端目標清單。

### 後記
本文著重實作細節與踩雷筆記，期望補足中文圈 Windows Container + Swarm 的實戰經驗。作者看好容器在封裝執行環境與標準化部署生態（映像/Registry）方面的價值，認為「package once, run everywhere」在 OS 支援下更可落實。展望未來，當 Windows Hyper-V Container 與 Linux 容器互通更完善、Routing Mesh 與服務發現補齊後，體驗將更成熟。對學習時機的建議是：愈早愈好，現在切入仍極具價值，對開發與維運皆是必備技能。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 Docker 與容器概念（image、container、registry、port publishing）
   - Windows Server 2016 with Containers 基本操作、RDP 使用
   - Azure 基礎：訂閱、建立 VM、Resource Group、網路安全性與防火牆
   - 基本網路觀念：NAT、Load Balancer、DNS、Overlay Network

2. 核心概念：
   - Windows 容器與 Docker Swarm Mode：建立 Manager/Worker、service 部署與調度
   - 私有鏡像庫 Azure Container Registry（ACR）：鏡像推送、授權存取
   - Swarm 服務模型：global 與 replicated 模式、publish port、service 與 container 的對應
   - Overlay/Ingress 網路與路由：routing mesh（當時不支援 Windows）、DNSRR 的服務發現
   - 實務限制與繞道方案：每節點登入 registry、host publish 模式、外部負載平衡器（NGINX）替代

3. 技術依賴：
   - Swarm 叢集依賴：每台節點需安裝 Docker Engine（Windows Server 2016 with Containers 映像已內建）
   - Registry 依賴：ACR 啟用 Admin user、節點需 docker login，service create 時需 --with-registry-auth
   - 網路依賴：Swarm 自動建立 ingress overlay；Windows 當時不支援 routing mesh，需使用 publish mode=host 或外部 LB
   - 平台依賴：Azure VM/NSG/防火牆需開放對應埠

4. 應用場景：
   - 在 Azure 快速體驗或建立 Windows 容器 Swarm 叢集（實驗/PoC）
   - 企業內網自建 Windows 容器叢集且需私有鏡像庫
   - 部署多實例的 ASP.NET/Windows 型 Web 應用，並以外部 LB 實作流量分散
   - 在 ACS/AKS 尚未完整支援或需要自控環境時的過渡方案

### 學習路徑建議
1. 入門者路徑：
   - 申請 Azure 訂閱並建立 3 台 Windows Server 2016 Datacenter – with Containers VM
   - 建立 ACR、啟用 Admin user、設定密碼
   - 基礎 Docker 操作：pull/tag/push、run/-p、login
   - 以單機方式啟動簡單 Web 容器並從瀏覽器驗證

2. 進階者路徑：
   - 初始化 Swarm（docker swarm init）與加入節點（join token）
   - 理解 service 與 container 關係、global vs replicated、replicas
   - 學會使用 docker service ls/ps、滾動更新、故障觀察
   - 研究 overlay/ingress 網路、publish 模式與 Windows 限制

3. 實戰路徑：
   - 將自建鏡像推送至 ACR；在每個節點 docker login，部署 service 並加上 --with-registry-auth
   - 因 Windows 當時不支援 routing mesh，改用 --publish mode=host 或建置外部 LB（如 NGINX）
   - 配置 Azure NSG/VM 防火牆開放對外埠；以多節點對外驗證
   - 建立監控與日誌蒐集，並撰寫部署腳本（PowerShell）自動化 login、service 建立與驗證

### 關鍵要點清單
- Azure Container Registry（ACR）建立與授權：啟用 Admin user、設定密碼，供叢集節點拉取私有鏡像使用 (優先級: 高)
- 鏡像推送流程：docker pull → tag 為 {registry}/{image}:{tag} → docker push (優先級: 高)
- Swarm 初始化與節點加入：docker swarm init --advertise-addr / --listen-addr；以 join token 新增 worker (優先級: 高)
- Manager/Worker 角色：至少一台 Manager 負責調度，其餘為 Worker 執行工作負載 (優先級: 中)
- 以 service 部署應用：docker service create（非 docker run），--name、--mode、--replicas、--publish 等參數 (優先級: 高)
- Registry 驗證在 Swarm 的處理：每節點 docker login，service create 時加 --with-registry-auth (優先級: 高)
- 服務模式差異：--mode global（每節點一份） vs replicated（指定 --replicas N，由 Manager 分配） (優先級: 中)
- Windows 上的 publish 策略：因 routing mesh 當時不支援，需使用 --publish mode=host,target=80,published=80 (優先級: 高)
- Overlay/Ingress 網路概念：跨機器的虛擬網路，支撐服務互聯與（未來）負載分散能力 (優先級: 中)
- Routing mesh 限制（Windows）：當時不支援，需要外部 LB 或 host publish 作替代 (優先級: 高)
- DNSRR 與服務發現：理論上以 --endpoint-mode dnsrr 進行 DNS 輪詢，但 Windows 實作與行為有限制 (優先級: 中)
- Swarm 常用觀察指令：docker service ls、docker service ps <service>、docker exec 進入容器診斷 (優先級: 中)
- Azure 網路與防火牆：開放 VM/NSG 對外埠，否則無法從外部瀏覽器存取服務 (優先級: 高)
- 成本與規格：用 DS2 v2 等基本規格快速建置 3 節點實驗叢集，控制使用時間以降低成本 (優先級: 低)
- 疑難排解重點：無法拉取鏡像多為認證問題；無法對外連線多為 publish 模式或防火牆設定 (優先級: 高)