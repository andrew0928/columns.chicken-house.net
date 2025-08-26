# Rancher - 管理內部及外部 (Azure) Docker Cluster 的好工具

## 摘要提示
- 容器管理平台：Rancher 同時是 Docker Engine 管理工具與叢集管理平台，支援多環境與多種編排。
- 以使用者為中心的 UI：提供清楚的資源監控與容器級別的使用率儀表板，介面友善。
- 多雲支援：可在自架環境與公有雲（含 Azure）建立與管理 Hosts，支援以認證自動化佈署。
- 編排彈性：原生 Cattle，並支援 Docker Swarm、Mesos 等；未來可匯入外部 Swarm（官方規劃中）。
- 開發到生產多環境：可切分多個 Environment（如 Local 與 Azure）獨立管理與佈署。
- 內建負載平衡：以 HAProxy 為基礎，支援以 Service 為目標的路由與進階規則。
- 水平擴展簡單：以 Scale 控制容器數量，自動分散至不同 Hosts 提升可用性。
- 就地升級（In-Service Upgrade）：透過批次、間隔、啟停順序參數，實現不中斷服務升級與可回滾。
- 與 Azure 的對照：Azure Cloud Service 早有成熟升級/切換機制；Rancher接近但缺少正式/預備環境一鍵切換。
- 實作範例：以 Rancher OS + Rancher Server 建置管理面；示範 Hello World/WordPress 的部署、LB、擴展與升級流程。

## 全文重點
作者從使用 Docker 的指令行管理起步，尋找能兼顧易用性與可視化監控的 GUI 管理工具。在嘗試多款單機與叢集方案後，決定深入評估 Rancher。Rancher 不僅提供完整的 Docker Engine 管理與叢集功能，更支援多環境隔離（Environment）、多種編排（Cattle、Swarm、Mesos）、以及對多家雲服務（含 Azure）的原生整合；同時具備深入的資源監控視圖、內建 HAProxy 負載平衡、與最受作者青睞的 In-Service Upgrade（不中斷服務的就地更新）。

文章以實作為主線：首先以 Rancher OS 快速建起第一台 Docker 主機並部署 Rancher Server 作為控制中樞。接著建立兩個獨立環境：Local（內網開發）與 Azure（公有雲生產），分別將多台 Hosts 加入管理。對 Azure，Rancher 能直接透過雲端認證自動開設與註冊多台 VM 作為 Hosts；作者亦示範 Azure Container Service 以幾步點選便能建立 Swarm 叢集，惟當時 Rancher 尚未支援匯入既有 Swarm，僅能由 Rancher 端建立（官方明確表示正與 Docker 團隊合作改善）。

在部署環節，作者先以 tutum/hello-world 作為暖身，展示 Stack/Service/Container（Node）的分層概念與 Rancher UI 的部署體驗。之後示範如何水平擴展（Scale Out）服務，Rancher 會自動把容器分散至不同 Hosts，提高可靠度。隨後配置內建 Load Balancer，將流量導向多個 Service 實例，並以重新整理顯示不同容器 ID 的頁面驗證負載分流生效。LB 基於 HAProxy，可套用進階語法規則以滿足複雜場景。

最重要的一節是 In-Service Upgrade。Rancher 透過新版 compose 設定，先啟動新容器，再按策略批次替換舊容器，整個過程不中斷服務，並支援 Rollback 與 Finish Upgrade 後回收舊資源。升級流程的三個關鍵參數包括：Batch Size（每批替換數量，需小於服務實例數以保可用性）、Batch Interval（批次間隔，視初始化時間調整）、Start Before Stopping（先啟動新服務或先停舊服務）。相比 Azure Cloud Service/ Web App 早已成熟的 Production/Staging 切換與零停機回切，Rancher 雖已能穩定達成就地升級，但尚缺少正式/預備一鍵切換的完備體驗，屬於小小的遺憾。

總結而言，Rancher 憑藉易用 UI、強大監控、內建 LB、多環境管理，以及關鍵的 In-Service Upgrade，成功複刻作者在 2009 年初識 Azure Cloud Service 的感動，並將這些能力帶到自建與多雲環境中。對想要跨內外網、跨公有雲管理 Docker 叢集、同時追求簡單而可靠的部署與升級流程的團隊而言，Rancher 是值得投入的解決方案。

## 段落重點
### 前言與背景
作者回顧容器技術在短短三年間的飛速發展，特別是從半年前入門 Docker 到如今管理工具百花齊放的變化。其核心需求是以圖形化界面取代繁瑣指令，並能從單機管理進化到多 Docker Engine 的叢集管理。在評估 Synology Docker Station、Docker UI、Shipyard 等單機工具後，因規模與需求成長，開始尋找能一次管理多套 Docker Engine 的平台。在編排方面，作者列舉 Swarm、Rancher Cattle、Mesos、Kubernetes、Docker Cloud 等多項選擇；管理工具則聚焦 Rancher、Tutum（Docker Cloud）、Azure Container Service 等。考量成本與功能，作者指出 Docker Cloud 收費與缺少資源監控是痛點，轉而選擇 Rancher，因其擁有優質 UI 與完整資源監控、In-Service Upgrade、內建 Load Balancer、安裝簡便與 Rancher OS、支援多編排與雲廠商、多環境管理等優勢。本文以 Azure 作為公有雲場景，重現當年在 Azure Cloud Service 上的管理與升級體驗，並以具體操作流程與心得為主軸。

### STEP #0, Planning
規劃建立兩個獨立環境（Environment）與叢集：Local（開發/內網）與 Azure（正式/公有雲），但統一由單一 Rancher Server 管控與部署。示範情境為：部署一套 WordPress，將 Web 與 DB 拆為服務，Web 透過負載平衡達到高可用；隨後執行 Scale Out（Web 由 2 節點擴至 3 節點）；最後進行不中斷升級（In-Service Upgrade）。此規劃反映企業常見的多環境隔離與生產級操作要求，並能展示 Rancher 在跨環境部署、水平擴展與灰度升級的實戰能力。作者強調，這些能力曾在 Azure Cloud Service 時代就已成熟，如今透過容器與 Rancher，在地端與多雲也能達到相近等級的部署管理體驗。

### STEP #1, 架設 Rancher Server
Rancher Server 本身以容器形式提供，需要先有 Docker 主機。為簡化宿主建置，作者選擇 Rancher OS——專為執行 Docker 的極簡 Linux，系統啟動即以 Docker 為 PID 1，其它傳統服務透過容器外掛，映像極小（約 28MB）。流程為：先安裝 Rancher OS，啟用 Docker，然後以 docker run 啟動 rancher/server（預設服務埠 8080）。作者提醒 Rancher Server 啟動較慢（大量 Java 元件），建議至少 1GB RAM，實務給 2GB 更穩妥；此 VM 僅作為管理平面，不加入叢集跑業務容器。完成後即可存取 UI 與進行環境與 Hosts 建置。此步驟的關鍵在於將控制平面獨立、規格適當，確保後續操作穩定與順暢。

### STEP #2, 架設 Local Environment
在 Rancher Server 建立 Local Environment（預設 Cattle 編排），接著於內網準備三台以 Rancher OS 建置的 VM 作為 Hosts。透過 Infrastructure > Hosts > Add Host（Custom），在每台 Host 上執行 Rancher 提供的一鍵註冊指令，等待 Agent 啟動並向 Server 註冊回報。加入完成後，Rancher UI 可即時呈現每台 Host 的容器清單與 CPU/RAM/DISK 等資源使用狀態。此流程展示了 Rancher 在內網環境導入的便捷性與可視化優勢，為後續部署 Stack/Service 奠定基礎。作者指出 Rancher 對資源監控的呈現是其選用主因之一，有助於日常營運與容量觀測。

### STEP #3, 架設 Azure Environment
針對生產環境，作者以 Azure 資源建立 Hosts。Rancher 原生支援多家 IaaS，能在 UI 內一次完成多台 VM 的建立與註冊，只要提供 Azure 認證、設定 VM 規格與數量，即可自動化部署 Hosts，流程大幅簡化。作者並分享 Azure Container Service（ACS）以點選方式快速建立 Swarm 叢集的體驗，但當時 Rancher 尚無法直接匯入既有 Swarm，只能由 Rancher 端建立（官方表示正與 Docker 合作以支援外部叢集自動匯入）。此段凸顯 Rancher 與 Azure 的互補性：Rancher 管控層具多雲/多環境一致性與視覺化優勢；Azure 在叢集速建上成熟高效。對實務團隊而言，兩者結合能降低上雲門檻並加速生產環境落地。

### STEP #4, Deploy "Hello World" Service
作者先用 tutum/hello-world 作為暖身，展示 Rancher 的 Stack/Service/Container 概念與部署體驗。Stack 對應一個應用組合（如未來的 WordPress），Service 對應角色（如 Web/DB），Service 可能包含多個容器實例（Nodes）。在 Applications > Stacks > Add Stack 中，可直接貼上 docker-compose.yml 完成部署，Rancher 會依關聯自動拉起容器。部署完成後，透過對應 IP/PORT 測試服務，並可從輸出顯示容器 ID 以驗證後續負載平衡。此段重點在於 Rancher 與 Compose 的無縫銜接，以及 UI 層對多容器服務的清晰表達，讓部署對開發與運維人員都更直覺。

### STEP #5, Scale Out Your Service
為達可用性與容量要求，作者示範直接在 Service 頁面調整 Scale 值，Rancher 便會自動擴增容器實例，並盡量分散到不同 Hosts。擴展完成前未配置 LB 時，可分別以各 Host 的 IP 連線至對應容器驗證。接著在同一 Stack 內新增 Load Balancer 服務，將目標設定為對應的 Service，Rancher 以 HAProxy 為核心實現流量分發。透過多次重新整理，可看到返回頁面輪流顯示不同容器 ID，驗證 LB 生效。Rancher LB 支援跨 Stack 指定目標服務，也能套用 HAProxy 進階語法以處理更複雜路由/權重/健康檢查等需求。此段展現了從水平擴展到對外服務的全鏈路配置在 Rancher 中極為順暢，降低了運維與故障轉移的複雜度。

### STEP #6, In-Service Upgrade
此段是全文核心。Rancher 的 In-Service Upgrade 讓服務在不中斷或最小中斷下完成升級。操作上，透過 Upgrade 入口進入 Service 設定，調整映像版本、環境變數、Port、Volume 等，即可開始升級流程。Rancher 會先依新設定啟動新容器（可能暫時超過原先 Scale 數），待新容器健康啟動後，逐批停用舊容器，整體服務持續可用。完成替換後狀態為 Upgraded，使用者可選擇 Finish Upgrade（回收舊容器）或 Rollback（停新啟舊）。三個關鍵參數決定升級節奏與安全性：Batch Size（每批替換數，應小於實例總數以確保流量承載）、Batch Interval（批次間隔時間，取決於初始化時長）、Start Before Stopping（選擇先啟動新容器或先停舊容器）。作者高度肯定此功能對日常維運價值，但也指出與 Azure Cloud Service/Web App 的 Production/Staging 一鍵切換相比，Rancher 尚缺少預備環境直接切換的完整體驗，屬可期待的改進方向。文末附上官方升級文件，建議讀者參考命令列版說明以理解更多參數細節。

### Summary
作者以實作帶出 Rancher 的長處：易用的 UI 與監控、跨環境/多雲一致的 Host/Stack 管理、內建 HAProxy LB、簡單的水平擴展，以及最關鍵的 In-Service Upgrade 帶來的連續服務升級能力。Rancher 成功把過去 Azure Cloud Service 上的高水準部署/升級體驗帶到自建與多雲世界，讓團隊能以更低門檻達成生產級容器營運。雖然在正式/預備環境切換的完善度上尚與 Azure 有差距，但整體而言，Rancher 已足以成為兼顧開發效率與營運穩定性的實用解決方案。作者期望本文能幫助讀者快速理解並落地使用，並邀請讀者回饋支持。

## 資訊整理

### 知識架構圖
1. 前置知識
   - Docker 基礎：容器/映像檔、Docker Engine、Registry、Docker CLI/Compose
   - Linux 與虛擬化：VM 基本操作、SSH、公私鑰
   - 網路與服務：Port/映射、Load Balancer 基本概念、HAProxy 概念
   - 雲端 IaaS 基礎：Azure 訂用帳戶、認證與金鑰、VM 規格與費用
   - 基本持續交付概念：版本升級、回滾、零停機

2. 核心概念
   - Rancher 元件與角色：Rancher Server（控制面/GUI）、Rancher Agent（節點代理）、RancherOS（極簡為 Docker 而生的 OS）
   - 基本資源模型：Environment（環境/邏輯隔離）→ Hosts（節點/VM）→ Stacks（應用組）→ Services（服務角色）→ Containers（實例/Nodes）
   - Orchestration 選項：Cattle（Rancher 內建）、Docker Swarm、Mesos、Kubernetes（本文示範以 Cattle 為主）
   - 運維能力：部署（Compose 驅動）、Scale Out、Load Balancer（HAProxy）、In-Service Upgrade（不中斷升級、Rollback/Finish）
   - 混合雲管理：同一套 Rancher 統一管理內部與 Azure 上的叢集與服務

3. 技術依賴
   - Rancher Server 以容器方式執行，需先有 Docker Host（可用 RancherOS 或一般 Linux）
   - Hosts 需安裝 Rancher Agent 與 Docker；由 Server 發出註冊指令加入叢集
   - Stack/Service 由 docker-compose 設定驅動；Cattle 執行排程與生命週期管理
   - Load Balancer 基於 HAProxy；可用其進階語法做細部路由/健康檢查
   - Azure 整合需提供憑證與配置，Rancher 可自動在 Azure 建立/託管 Hosts

4. 應用場景
   - 內外部混合雲容器叢集的一站式管理（地端開發環境 + Azure 正式環境）
   - 可水平擴展的 Web 應用（如 WordPress 前後端分離，Web 多實例 + DB 容器）
   - 線上不中斷升級（藉由 In-Service Upgrade 批次滾動替換）
   - 資源監控與可視化運維（主機/容器 CPU、RAM、Disk 使用狀況儀表板）
   - 依環境隔離的多租/多團隊管理（Environment 分割）

### 學習路徑建議
1. 入門者路徑
   - 安裝 Docker 與 Docker Compose，熟悉基本指令與 yml 結構
   - 用 RancherOS 建一台 VM，啟動 Rancher Server（docker run rancher/server）
   - 在 GUI 透過 Add Host 註冊 1-3 台本機或 VM 為 Hosts
   - 用官方 Hello-World 或簡單 Nginx 建立第一個 Stack/Service

2. 進階者路徑
   - 在 Azure 以 Rancher 自動佈署 Hosts，練習混合雲環境切換與管理
   - 設定 Rancher Load Balancer，串多個 Services/跨 Stack 服務
   - 練習 Scale Out/Scale In 策略與排程（理解分散到不同 Hosts）
   - 探索 Orchestration 選項與差異（Cattle vs Swarm/Mesos/K8s），並測試標籤/親和性排程
   - 啟用使用者/權限與安全性配置

3. 實戰路徑
   - 建立 dev/prod 兩個 Environments；在 dev 先行部署 WordPress（Web/DB 分離）後再推到 prod
   - 實作 In-Service Upgrade：調整鏡像版本/環境變數，設定 Batch Size/Interval/Start-before-stop，驗證零停機
   - 建置監控告警與日誌收集；設計 Rollback 流程與演練
   - 與 CI/CD 整合（rancher-compose 或 pipeline）實現自動化部署
   - 成本與容量規劃：Azure VM 規格、節點數、網路與儲存費用評估

### 關鍵要點清單
- Rancher Server/Agent 機制: 控制面以容器運行，節點以 Agent 註冊加入叢集 (優先級: 高)
- RancherOS 角色: 為 Docker 精簡化的 Linux，啟動即以 Docker 為 PID 1 (優先級: 中)
- Environment/Host/Stack/Service/Container 術語: 從邏輯環境到具體容器的資源模型 (優先級: 高)
- Cattle 與其他編排: Cattle 為預設編排，亦支援 Swarm/Mesos/K8s（匯入既有 Swarm 當時尚未支援） (優先級: 中)
- Azure 主機佈署整合: 以憑證自動在 Azure 建立多台 Hosts，簡化 IaaS 配置 (優先級: 高)
- Docker Compose 驅動部署: 以 docker-compose.yml 定義 Stack/Service 及關聯 (優先級: 高)
- 內建 Load Balancer: 基於 HAProxy，支援多服務/跨 Stack 綁定與進階設定 (優先級: 高)
- Scale Out 策略: 以 Scale 數值擴容，Rancher 會把容器分散到不同 Hosts (優先級: 高)
- In-Service Upgrade 流程: 以新設定啟動新容器、健康後替換舊容器，支援 Finish/Retry/Rollback (優先級: 高)
- 升級三參數: Batch Size、Batch Interval、Start Before Stopping 決定滾動升級行為 (優先級: 高)
- 資源監控儀表板: 主機與容器層級 CPU/RAM/Disk 可視化，有助容量與故障檢測 (優先級: 中)
- 安全與權限: 預設無密碼僅適合單機測試，正式環境需啟用帳號/權限管理 (優先級: 高)
- 與 Azure Cloud Service 對比: Rancher 升級便利但缺少類似 Azure 的 staging slot 即時切換 (優先級: 中)
- 成本考量: 相較 Docker Cloud 計價（每節點月費），Rancher 自架可控成本但需自管基礎設施 (優先級: 中)
- 主機規格建議: Rancher Server 建議 ≥1GB RAM，實務給 2GB 較穩定；避免與業務工作負載共用 (優先級: 中)