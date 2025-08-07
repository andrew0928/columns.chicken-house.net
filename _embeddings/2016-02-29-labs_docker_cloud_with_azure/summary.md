# [實戰] 十分鐘搞定! 在 Azure 上面佈署 Docker Container! - Docker Cloud 託管服務體驗

## 摘要提示
- 快速佈署: 透過 Docker Cloud + Azure，十分鐘即可完成從 VM 建立到 WordPress 上線的全流程。
- 核心工具: Docker Machine、Compose、Swarm 分別解決 Host 佈署、服務組合與高可用調度。
- 託管服務: Docker Cloud 以「託管而不代管」模式，集中管理多雲或自建節點。
- Azure 整合: 透過憑證與 Subscription ID 授權，Docker Cloud 可自動建立、銷毀 Azure 資源。
- 一鍵部署: Stackfile 兼容 Docker Compose 語法，Save & Deploy 後自動拉取 image、建立 Service。
- DNS/Endpoint: Docker Cloud 自動生成 FQDN，亦可自行加 CNAME 轉址。
- 高可用擴充: 可透過增加 Node/Container 與動態 Port Mapping，實現無縫 Redeploy 與負載分散。
- 成本考量: Docker Cloud 免費方案僅含一個 Node，額外 Node 每月 15 美元，另需加上雲端 VM 費用。
- 實務經驗: 作者已將個人部落格及多項服務遷至自家 Mini-PC + Docker Cloud 管理。
- 未來展望: 公私有雲、NAS 若能深度整合 Docker Cloud，將進一步降低維運門檻。

## 全文重點
本文示範如何利用 Docker 官方的託管平台 Docker Cloud，結合 Microsoft Azure 的 IaaS，於十分鐘內完成 WordPress 部落格的佈署。作者先說明三大核心工具：Docker Machine 用於批量建立安裝好 Docker Engine 的主機；Docker Compose 用檔案描述多 Container 的服務拓撲；Docker Swarm 則處理多 Host 間的排程與高可用。由於自行建構整套環境門檻不低，作者改採 Docker Cloud，其可連結多家公有雲或自有機房，集中提供節點管理、服務部署、DNS、Endpoint 與版本控管等功能，但實際的運算資源仍由使用者的雲端帳戶負擔。

操作流程分三步：一、事前準備，在 Docker Cloud 介面新增 Microsoft Azure 憑證並填入 Subscription ID，讓系統得以代表使用者呼叫 Azure API。二、建立 Node，於介面選擇 Azure、機房區域及 VM 規格後，Docker Cloud 會自動在 Azure 建立對應的虛擬機、磁碟與雲端服務並安裝 Agent；免費帳號僅可建一台 Node，多出來的每月 15 美元。三、部署應用，透過 Stackfile（Compose 格式）描述 db 與 web 兩個 Service，點選 Save & Deploy 即可自動拉取 mysql 與 wordpress image、建立 Container、設定 Link 與 Port。完成後在 Endpoints 頁籤即可取得系統產生的 FQDN，瀏覽器開啟即見 WordPress 首次設定畫面。

後續如需修改服務配置，只要在 Stackfile 編輯後按 Redeploy，Docker Cloud 會自動銷毀並重建關聯 Container；若採多節點且動態 Port，可輪流重佈署達到零停機。作者實測除部落格外，還以相同方式部署 GitLab、Redmine 等服務，並以自家 Mini-PC 作為單一 Node，Docker Cloud 提供的圖形介面、操作歷程與整合 Repository 功能大幅降低維運負擔。文章最後感嘆雲端與容器技術進步神速，現在個人亦能享有昔日僅大型 PaaS 才具備的跨雲佈署與集中管理能力。

## 段落重點
### Docker Machine
說明批量建立 Docker Host 的需求與挑戰，Docker Machine 透過支援多雲外掛，讓使用者以一致指令在 Azure、AWS、VMware 等環境自動開 VM、安裝 Docker Engine，解決「Host 生成」的第一關。

### Docker Compose
聚焦於多 Container 服務的描述與一次性佈署；作者以 WordPress 為例，需要 Reverse Proxy、Web、DB、Data 四個容器，單靠 docker run 太繁瑣，因此透過 Compose 設定檔把架構、連結與環境變數寫好，一行指令即可整組啟動。

### Docker Swarm
探討跨 Host 的高可用與自動擴充需求，例如 WordPress 佈署在兩台 Host 上以防單點故障，或尖峰時自動加入第三台。Swarm 負責資源排程、網路、服務調度，然而自行實作複雜，催生作者尋找託管解決方案。

### Docker Cloud 託管服務
介紹 Docker Cloud（前身 Tutum）的定位：僅負責管理與整合，真正運算仍在使用者選定的公有雲或自建伺服器。帳號與 Docker Hub 共通，可直接存取公私有 Image。作者決定用它簡化前述 Machine、Compose、Swarm 的繁雜細節。

### #1 事前準備－連結 Azure 帳號
詳細步驟：在 Docker Cloud 下載管理憑證→登入舊版 Azure Portal 上傳憑證→複製 Subscription ID 回貼，完成後 Docker Cloud 即可代表使用者建立、管理 Azure 資源；提醒須注意雲端成本。

### #2 建立 Docker Cloud Nodes
於 Nodes→Launch node 選擇 Azure、區域、VM 規格與磁碟大小，點擊後約 5–10 分鐘完成 VM 佈署與 Agent 安裝。作者示範 Basic A1 規格並於 Azure Portal 觀察自動產生的 VM、雲端服務、磁碟等資源；免費帳號限定單一 Node。

### #3 佈署應用程式（Stacks）
在 Stacks→Create stack 輸入 Stack name 與 Stackfile（Compose 語法）後 Save & Deploy；例中定義 db 與 web Service，自動拉取 mysql:latest 與 amontaigu/wordpress:latest。完成後切換 Endpoints 取得系統產生的 URL，即可開啟 WordPress 初始設定頁。

### 調整服務架構與 Redeploy
修改 Stackfile（如增加 Container 數量、變更 Port）後 Save，介面會標記需 Redeploy。可選擇整個 Stack 或單一 Service 重佈署；在多 Node、動態 Port 情境下，可輪流佈署達成零中斷升級，並藉此實現 HA 與自動擴充。

### 其他介紹補充
作者展示實際生產環境：一台自購 Mini-PC 作為 Node，透過多個 Stack 同時運行 Blog、GitLab、Redmine 等，Docker Cloud 提供圖形化監控、Endpoint、操作 timeline 及與 Docker Hub/Private Repo 整合，讓個人亦能享有企業級佈署體驗。

### 後記
作者反思從早期 Azure Cloud Service 的驚豔到今日多雲整合的成熟，Docker Cloud 結合容器技術讓跨雲、跨平台的佈署與維運門檻大幅降低；期望未來 NAS 等硬體亦能原生整合此服務，讓更多使用者受惠。