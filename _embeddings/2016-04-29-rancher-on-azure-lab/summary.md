# Rancher - 管理內部及外部 (Azure) Docker Cluster 的好工具

## 摘要提示
- Rancher: 一站式 Docker Cluster GUI 管理與多環境佈署平台，支援多種 Orchestration。
- Rancher OS: 28 MB 的極簡 Linux，開機即啟 Docker，可作為 Rancher Server／Host 基底。
- 多環境管理: 透過 Environment 分離 Intranet 開發與 Azure 正式機房，集中在同一 UI 操作。
- Azure 整合: 內建支援 Azure API，一鍵建立並加入多台雲端 Host。
- Load Balancer: 內建 HAProxy，可直接在 UI 內綁定多個 Service 及 Stack。
- Scale Out: 調整 Scale 欄位即可自動在不同 Host 產生／分散 Container。
- In-Service Upgrade: 以 Batch Size／Interval／Start Before Stopping 控制不中斷滾動升級並支援 Rollback。
- 資源監控: 介面即時呈現 Host 與 Container CPU、RAM、Disk 使用率。
- 成本考量: 相較 Docker Cloud 每節點收費，Rancher 免費且功能更完整。
- 實作流程: 文章逐步示範從規劃、安裝、佈署 WordPress 到升級的完整操作。

## 全文重點
作者以自身多年雲端與容器經驗，評估多款 Docker GUI 與 Orchestration 後，選定 Rancher 作為同時管理內部 VM 與 Azure 公有雲的工具。Rancher 不僅提供 Cattle、Swarm、Mesos 等多種排程平台，也內建資源監控、Load Balancer、In-Service Upgrade 等功能，彌補了 Docker Cloud 需付費與缺乏監控的缺點。作者首先說明以 Rancher OS 建立最小化 Docker Host，並在其中啟動 Rancher Server。接著分別建構 Local Environment 與 Azure Environment，展示如何透過 UI 新增 Host 或直接藉由 Azure API 一鍵開出多台 VM 並納入 Cluster。

完成環境後，作者以 Tutum/hello-world 及 WordPress 堆疊示範部署流程：經由 Stacks 畫面貼上 docker-compose.yml 即可自動建立 Web 與 DB 服務；透過 Scale 欄位輕鬆水平擴充 Container 數量，同時利用內建 HAProxy 設定 Load Balancer 以檢驗流量分流效果。文章重點放在 In-Service Upgrade 機制：Rancher 先依 Batch Size 啟動新版 Container，待健康後再逐批關閉舊版，確保線上服務零中斷；若驗證失敗可立即 Rollback。作者比較了 Azure Cloud Service 在 2009 年即具備的分層佈署與升級機制，指出 Rancher 雖已強大但仍缺少可在 Production/Staging 間即時切換的功能。

整體而言，Rancher 透過簡潔的 GUI、跨雲支援與完整維運機制，把過去僅雲端大廠能提供的能力帶到一般 DevOps 手中。文章最後提醒正式環境需設定帳密並善用監控，亦對未來能匯入既有 Swarm Cluster 功能寄予期待。

## 段落重點
### 導言：Docker 管理工具的演進
作者回顧三年間 Docker 生態爆炸成長，從找不到合用 GUI 到選項繁多；列舉 Synology Docker Station、Shipyard、Docker Cloud 等工具的優缺點，點出 Docker Cloud 收費與監控不足而轉向 Rancher 的動機。

### STEP #0 Planning – 架構設計
規劃兩組獨立 Cluster：Local (開發) 與 Azure (正式)，均由同一 Rancher Server 集中管理；示範欲部署 WordPress 並進行 Scale-Out 與無縫升級的目標。

### STEP #1 架設 Rancher Server
說明以 Rancher OS 安裝至硬碟並啟動 Docker，透過 `docker run rancher/server` 起服務；建議配置 1–2 GB RAM，並提醒首次啟動需數分鐘。Server 僅作 Master，不參與實際負載。

### STEP #2 建立 Local Environment
於個人 PC 開三台 Rancher OS VM，透過「Add Host (Custom)」指令把主機註冊進 Rancher。展示 UI 內即時顯示 Host 與 Container 資源使用的監控畫面。

### STEP #3 建立 Azure Environment
利用 Rancher 內建 Azure Driver 填入訂閱與金鑰，一鍵建立多台雲端 VM 並自動安裝 Agent；同場加映 Azure Container Service 亦能快速部署 Swarm，但目前無法直接匯入 Rancher。

### STEP #4 Deploy “Hello World” Service
在任一 Environment 中新增 Stack，貼上 docker-compose.yml 佈署 tutum/hello-world；透過瀏覽器驗證容器回傳不同 hostname，以利後續 LB 測試。

### STEP #5 Scale Out 與 Load Balancer
將 Service Scale 從 2 提升至 3，Rancher 會自動分散至不同 Host；新增內建 Load Balancer 服務，選取目標 Service 即可導流，經多次刷新可觀察到流量輪詢至各容器。

### STEP #6 In-Service Upgrade
解釋 Upgrade 流程：Rancher 先依 Batch Size 增建新版容器，健康檢查後再逐批關閉舊版；可選擇 Finish Upgrade 或 Rollback，並深入說明 Batch Size、Batch Interval、Start Before Stopping 三參數對零停機升級的重要性。

### Summary – 心得與展望
Rancher 以免費、功能完整的 GUI 平台，重現當年 Azure Cloud Service 帶給作者的驚艷；雖尚欠缺 Production/Staging 快速切換與匯入外部 Swarm 的能力，但已大幅簡化日常 DevOps。作者鼓勵讀者嘗試並關注後續更新。