# [實戰] 十分鐘搞定! 在 Azure 上面佈署 Docker Container! - Docker Cloud 託管服務體驗

## 摘要提示
- 問題背景: 作者從單機 Docker 轉向雲端與大規模管理，尋找更有效率的佈署與營運方式
- 三大神器: Docker Machine、Docker Compose、Docker Swarm 分別處理主機佈署、服務編排、叢集與高可用
- 核心解法: 採用 Docker 官方託管服務 Docker Cloud 簡化跨雲管理與自動化
- Azure 整合: 透過證書授權讓 Docker Cloud 以你的身分在 Azure 建立與管理資源
- Nodes 佈署: 直接從 Docker Cloud 建立 Azure VM 作為 Docker Host，最省事且相容最佳
- Stacks 編排: 以 Stackfile（相容 Docker Compose）快速一鍵佈署多服務（如 WordPress + MySQL）
- Endpoints 與 DNS: Docker Cloud 自動給定可用 FQDN，亦可用自有網域 CNAME 友善接入
- 變更與重佈署: 修改 Stackfile 後以 Redeploy 無痛重建容器，結合多節點可做到不中斷更新
- 成本與方案: 免費帳號限 1 個 Node；多節點需額外月費，另須支付雲端（Azure）基礎設施費
- 實戰體會: 用一天內完成多服務上線，體驗相當於 IaaS/PaaS 等級的管理能力，適合個人與團隊導入

## 全文重點
本文記錄作者從單機 Docker 管理走向雲端與規模化實務的過程與心得，核心目的在於用最少時間與成本，實現在 Microsoft Azure 上快速佈署、管理與擴展 Docker 工作負載。傳統僅以 docker 指令操作單機容器，在面對多主機、多服務編排、版本更新與高可用需求時明顯不足，因此作者先梳理了三個重要工具：Docker Machine 用於在各雲端與虛擬化平台快速建立 Docker Host；Docker Compose 讓多容器服務以宣告式方式一次性佈署；Docker Swarm 則處理叢集、資源調度與高可用。不過要自行把這套體系完整打通仍有相當門檻，於是選擇導入 Docker 官方託管服務 Docker Cloud，將複雜的跨雲資源與容器管理，整合為單一介面與自動化流程。

實作流程分三步。第一步是連結服務帳號：在 Docker Cloud 下載管理憑證，至 Azure 舊版管理入口上傳為管理證書，最後回填 Subscription ID 完成授權。完成後 Docker Cloud 可代為在 Azure 建立 VM、磁碟與相關雲端服務，但相對也會產生 Azure 費用，需隨時關注資源使用。

第二步是在 Azure 建立 Docker Cloud Nodes（即 Docker Hosts）。雖然也能把自有 Linux Server 納入，但須自行設防火牆、安裝 Docker Cloud Agent，且 Agent 會自帶商業支援版 Docker Engine，若系統原已安裝 Docker 會被移除；為避免相容性與設定負擔，作者建議直接從 Docker Cloud 建立 Azure VM。建立過程中可選擇區域、機型（如 A1）、磁碟大小與數量；免費帳號僅支援 1 個 Node，多節點需額外付費。建立後在 Azure 後台可見到對應 VM 與雲端服務資源，等待 5–10 分鐘完成佈署即可。

第三步是以 Stacks 佈署應用。Docker Cloud 的 Stackfile 與 Docker Compose 相容，文中以 WordPress + MySQL 為例，定義兩個服務（web 與 db），指向公共映像（wordpress、mysql），設定連結、環境變數與連接埠映射，按下 Save and Deploy 後即自動拉取映像、建立容器與啟動服務。佈署完成後在 Endpoints 分頁可見自動產生的 FQDN，直接對外可用；若要用自有網域，可在 DNS 加入 CNAME 指向，省去自建 DDNS 與客戶端更新的繁瑣。此時已可完成 WordPress 初始化並登入後台，整個流程相當平順。

在營運維護面，修改 Stackfile 後，Docker Cloud 會標示需重佈署的服務，可選擇整體或單一服務 Redeploy。Redeploy 本質為以新設定重建容器，若事先規劃有多節點與前端反向代理，便能透過滾動方式達到不中斷更新。要橫向擴展 web 容器數量，需注意連接埠衝突（固定綁 80 會導致同一 Node 無法啟多實例）；可改用動態連接埠對映，並以前端 Reverse Proxy 負責路由與負載分散。文中亦展示作者在自有 Mini-PC 上，以 Docker Cloud 管理多個 Stacks（部落格、反向代理、Redmine、GitLab 等），跨服務共享 80 埠由 Proxy 統一入口，強化了整體管理性與擴展性。

此外，Docker Cloud 與映像倉庫（Docker Hub）整合流暢，除每帳號提供 1 個 Private Repository 外，也能直接搜尋 Public Repository 建立服務，填好設定立即佈署上線。相較於一般 NAS 的 Docker 管理界面，此整合度與自動化能力更佳，作者甚至建議 NAS 廠商可考慮與 Docker Cloud 整合，讓家用或中小企業也享有更高階的雲端營運能力。

總結來說，Docker Cloud 將 Docker Machine、Compose、Swarm 等能力整合並圖形化，讓跨雲、跨主機的容器佈署與維運變得簡單可靠；在免費方案下對個人已相當夠用，若進一步導入多節點付費方案，搭配 Azure 等雲端資源，即可在有限成本下獲得接近 IaaS/PaaS 的專業級佈署與高可用能力。對剛入門 Linux 與容器編排的實作者而言，是極具投資報酬的選擇。

## 段落重點
### 前言與單機到規模化的轉折
作者長期想在 Azure 快速佈署 Docker Engine/Container，從 Linux 門外漢一路克服實作障礙。先前文章聚焦單機佈署與指令操作，適合學習但不利於規模化。為提升效率與可用性，需導入能處理多主機、多服務與高可用的工具鏈。本文即分享最終實作選擇：以 Docker Cloud 為核心，結合 Azure，達成從零到可用的快速上線。

### Docker Machine
Docker Machine 用來大規模建立 Docker Host（安裝好 Docker Engine 的 Linux 主機），並支援多種雲與虛擬化平台（Azure、AWS、Hyper-V、VMware 等）。好處是以一致指令集快速鋪設多台 Host，為後續容器佈署鋪路。

### Docker Compose
Compose 著重多容器服務的宣告式編排與一次佈署。以 WordPress 為例，通常會拆成 Reverse Proxy、Web、DB、DATA（Volume 管理）等容器。若手動以 docker 指令建立與連結，成本高且易錯；改用 Compose 以設定檔描述，單一指令即可建立整組服務，亦便於重複與版本管理。

### Docker Swarm
當有多台 Docker Host 與既定服務編排後，接著需處理高可用與彈性擴縮。Swarm 涵蓋跨 Host 的資源排程（CPU/RAM/Disk）、容器分配與跨節點網路通訊等，使容器能在多主機間協作、故障接手與自動擴容。雖然架構美好，但全靠自行整合仍有技術門檻。

### Docker（官方）託管服務：Docker Cloud
Docker Cloud（前身 Tutum）是 Docker 官方的託管管理平台，與 Docker Hub 共用帳號。它不提供主機代管，而是以單一介面整合你在 Azure、AWS 或自建機器上的 Docker 環境，簡化建立節點、佈署服務、擴縮與域名接入等繁瑣流程。本文將以在 Azure 佈署 WordPress 為例，展示端到端體驗。

### #1 事前準備—連結 Azure 帳號
在 Docker Cloud 建立與 Azure 的授權：下載 Docker Cloud 管理憑證、到 Azure 舊版入口上傳為管理證書、回填 Subscription ID。成功後 Docker Cloud 可代為在 Azure 建立 VM、磁碟等資源。需留意後續所有由平台代操作的資源都會產生 Azure 費用，應在 Azure 後台監控。

### #2 開始佈署—在 Azure 建立 Docker Cloud Nodes
雖可連結自有 Linux 主機，但需自設防火牆與安裝 Docker Cloud Agent，且 Agent 會安裝商業支援版 Docker Engine，可能與既有安裝衝突。建議直接從 Docker Cloud 建立 Azure VM 作為 Node，最簡單與相容最佳。建立時可選區域、機型與磁碟大小，等待數分鐘即可於 Azure 後台看到 VM 與關聯雲端服務。免費帳號僅支援 1 個 Node，多節點需付費（月費約 USD 15/節點），且基礎設施費用由 Azure 另計。

### #3 開始佈署你的應用程式（Stacks）
Stacks 以 Stackfile（相容 Docker Compose）描述服務。文中用 WordPress 範例：定義 db（mysql:latest）與 web（wordpress 映像）、設定環境變數、連結與對外埠（80:80），按下 Save and Deploy 後自動拉取映像與啟動。完成後在 Endpoints 可見自動生成的 FQDN，可直接訪問或以自有網域 CNAME 指向，免去自建 DDNS 的麻煩。實際點開即進入 WordPress 初始化流程，證明佈署已完成。

### 調整服務架構—重新佈署
容器建立後多數參數（如 Port、Volume）無法直接修改，需重建。以 Stackfile 為單一事實來源，修改後 Docker Cloud 會標記需 Redeploy 的服務，可選整體或局部重佈署。若要提升高可用，可增加 web 容器數量；需避免固定綁定同一對外埠導致的衝突，可改用動態埠並以前端 Reverse Proxy 做流量分配。多節點情境下可採滾動重佈署，實現不中斷更新。

### 其他介紹補充（實戰案例與倉庫整合）
作者實際在自有 Mini-PC 上以 Docker Cloud 管理多個 Stacks（部落格、Proxy、Redmine、GitLab 等），透過獨立 Proxy 共用 80 埠，整體只花不到一天完成遷移與上線。Docker Cloud 與 Docker Hub 整合良好，可直接搜尋公共映像建立服務，亦提供每帳號 1 個私有倉庫。相較 NAS 介面，Docker Cloud 的搜尋、設定與一鍵佈署體驗更優。作者甚至建議 NAS 廠商可考慮內建與 Docker Cloud 的結合，進一步提升家用與中小企業的雲端化能力。

### 後記
從單雲（過往 Azure Cloud Service）到跨雲與自建環境，今天已能以 Docker Cloud 這類託管平台獲得近似 IaaS/PaaS 的管理體驗，且門檻更低、彈性更高。對 Linux 新手與小型團隊來說，Docker Cloud 是把容器技術從實驗帶入生產的加速器；若有實際商業需求，付費取得多節點與高可用，也遠比自建團隊與工具鏈來得划算。本文除自我記錄，也提供給有意導入者作為實作參考。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本 Linux 操作與網路概念（SSH、Port、Firewall）
- Docker 基礎（Image、Container、Volume、Network）
- Docker Compose 語法與服務間連結
- 公有雲 IaaS 基本概念（Azure VM/區域/訂閱/費用）
- 基本 DNS 與反向代理（NGINX/Reverse Proxy）

2. 核心概念：本文的 3-5 個核心概念及其關係
- Docker Cloud（託管控制面）：集中管理 Nodes、Stacks、Services、Endpoints，與雲端供應商整合
- Docker Machine/Compose/Swarm 的對應：Machine 建 Host、Compose 配置多容器服務、Swarm/HA 調度 → Docker Cloud 在單一介面整合並簡化
- Azure 整合與授權：以管理憑證授權 Docker Cloud 代表你建立/管理 VM 與資源
- Stack 驅動式部署：以 Stackfile（Compose 語法擴充）定義多服務架構，一鍵部署/重佈署
- 擴展與高可用：透過多 Node、多容器、副本數、動態 Port 與前端 Reverse Proxy 實現 HA/擴容

3. 技術依賴：相關技術之間的依賴關係
- Docker Cloud 依賴：Cloud Provider（Azure）帳號授權 + Docker Cloud Agent 安裝於 Nodes
- Stack/Service 依賴：Public/Private Docker Registry 的 Images、Compose 連結（links/env/ports）
- HA 與可用性：多 Nodes 基礎 + 動態 Ports + 前端反向代理/負載平衡
- 網路與存儲：容器間網路連結、Host-Container Port 映射、資料持久化（Volumes/DATA 容器）

4. 應用場景：適用於哪些實際場景？
- 在 Azure 快速從無到有部署部落格/網站（WordPress+MySQL）
- 小團隊以最小人力成本獲得接近 PaaS 的部署/維運體驗
- 自建機房或家用設備（Mini-PC/NAS）與公有雲混合管理
- 多服務協作（Web/DB/Proxy/GitLab/Redmine）的一致性部署與滾動升級
- 教學/實驗環境的一鍵佈署與快速重置

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 Docker 基本概念與常用指令（run/pull/ps/logs）
- 學會撰寫最小 Compose 檔（單 Web + 單 DB）
- 註冊 Docker Hub/Cloud 帳號，熟悉 Docker Cloud 介面
- 在 Azure 開啟訂閱並認識基本費用項目
- 以範例 Stackfile 部署 WordPress + MySQL 至單一 Node

2. 進階者路徑：已有基礎如何深化？
- 掌握 Stackfile 參數（環境變數、重啟策略、Port 映射、資源限制）
- 導入 Reverse Proxy（NGINX）與多服務協作
- 練習 Redeploy 與零停機更新（分批重新部署容器）
- 導入 Private Repository、版本標籤策略與映像自動更新
- 觀察/調整 Azure VM 規格、磁碟、區域以優化成本/效能

3. 實戰路徑：如何應用到實際專案？
- 設計多環境 Stack（dev/stage/prod）與配置差異（env/密鑰）
- 建立多 Node 拓撲，啟用動態 Ports + 前端負載平衡（或雲端 LB）
- 規劃資料持久化與備援（資料卷/分離 DATA 容器/雲端磁碟）
- 監控與事件追蹤（Endpoints、Timeline、健康檢查）
- 成本治理：託管授權費用（節點數）+ Azure VM/存儲/流量預估與告警

### 關鍵要點清單
- Docker Cloud 託管定位: 提供控制面與整合介面，資源實際運行在你選擇的雲或自建環境上（非主機代管） (優先級: 高)
- 與 Azure 授權整合: 下載憑證、上傳至 Azure 管理入口、回填 Subscription ID，使 Docker Cloud 可代表你建立/管理 VM (優先級: 高)
- Nodes 概念: Nodes 等同 Docker Hosts，是部署容器與服務的實體/虛擬主機單位 (優先級: 高)
- Stack/Service 模型: 以 Stackfile（Compose 兼容）定義多服務架構，Service 是邏輯服務可對應多容器 (優先級: 高)
- WordPress 範例架構: Web + DB 基礎，進一步可加上 Reverse Proxy 與 DATA 容器做持久化 (優先級: 中)
- 一鍵部署與端點管理: Save and Deploy 觸發拉取映像/建容器，內建 Endpoints 與 FQDN 簡化 DNS 問題 (優先級: 高)
- 重新佈署機制: 修改 Stackfile 後以 Redeploy 滾動更新，解決容器不可變更配置（ports/volumes）問題 (優先級: 高)
- 擴容與 HA 策略: 調整容器副本數、跨多 Nodes 部署、分批 redeploy 達到不停機升級 (優先級: 高)
- Ports 衝突與動態映射: 固定對外 Port 會限制同機多副本；改用動態 Port 並在前端以反向代理/負載平衡彙整 (優先級: 中)
- 成本與配額: Docker Cloud 免費帳號僅 1 Node；額外節點約 $15/月，Azure 資源費用另計 (優先級: 高)
- 自建環境接入: 可連接自備 Linux 主機，但需設防火牆與安裝 Cloud Agent，且 Agent 會管理 Docker Engine (優先級: 中)
- Registry 整合: 支援 Public/Private Repository，介面可搜尋映像並快速生成 Service (優先級: 中)
- 監控與可觀測性: 介面提供容器/端點狀態、時間軸操作記錄，便於問題追蹤 (優先級: 中)
- 網路與存儲實務: 服務間連結（links/env）、資料持久化（Volumes/DATA 容器）是生產穩定度關鍵 (優先級: 高)
- 多雲與可攜性: 相同 Stack 定義可跨 Azure/AWS/自建環境復用，降低雲供應商綁定 (優先級: 中)