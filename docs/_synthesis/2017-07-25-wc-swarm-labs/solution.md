---
layout: synthesis
title: "Azure Labs: Windows Container Swarm"
synthesis_type: solution
source_post: /2017/07/25/wc-swarm-labs/
redirect_from:
  - /2017/07/25/wc-swarm-labs/solution/
---

以下為基於原文整理出的 15 個可教學、可實作的結構化問題解決案例。每個案例均包含問題、根因、解方、步驟、關鍵指令/程式碼、學習要點與練習評估，便於實戰教學與專案演練。

## Case #1: 在 Azure 上手動建置 Windows Container Swarm 叢集

### Problem Statement（問題陳述）
業務場景：團隊需要在公司內網或 Azure 上快速搭建 Windows 容器的 Swarm 叢集以做為 Proof-of-Concept 與測試環境。由於當時 Azure Container Service 對 Windows Container 尚在預覽，且內網場景需要自行管理環境，必須在短時間內完成最小可用叢集。
技術挑戰：如何以最少步驟建立 3 台節點（1 管理 + 2 工作）並完成 Swarm 初始化與節點加入。
影響範圍：若叢集無法正確建立，後續的映像部署、服務發布、網路測試均無法進行。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 受限於當時 ACS 對 Windows Container 的支援仍為 preview，無法一鍵完成。
2. 內網與自管環境需要可控的 VM 與網路配置。
3. Windows Container 資訊與文件相較 Linux 容器較少，容易踩雷。
深層原因：
- 架構層面：缺乏托管式 Windows 容器編排方案，只能自行搭建。
- 技術層面：Windows 上 Docker 與 Swarm 模式的相依與網路選項需手動設置。
- 流程層面：缺乏標準化建置腳本，需手動 RDP 逐台設定。

### Solution Design（解決方案設計）
解決策略：使用 Azure 市場影像 Windows Server 2016 Datacenter – with Containers 建三台 VM，指定一台為 Manager，透過 docker swarm init 與 join token 完成叢集建立。

實施步驟：
1. 建立 VM 節點
- 實作細節：在 Azure 建立 3 台 VM（wcs1、wcs2、wcs3），選用 Standard DS2 v2，Windows Server 2016 Datacenter – with Containers。
- 所需資源：Azure 訂閱、對應資源群組與 VNet。
- 預估時間：15 分鐘

2. 初始化 Swarm（wcs1）
- 實作細節：在 wcs1 以私網 IP 作為 advertise 與 listen。
- 所需資源：RDP、Docker CLI
- 預估時間：5 分鐘

3. 加入工作節點（wcs2、wcs3）
- 實作細節：在 wcs2、wcs3 使用 join token 加入。
- 所需資源：RDP、Docker CLI
- 預估時間：5 分鐘

關鍵程式碼/設定：
```shell
# Manager 初始化（wcs1，假設私網 IP 10.0.0.4）
docker swarm init --advertise-addr 10.0.0.4 --listen-addr 10.0.0.4:2377

# 取得 worker join 指令（含 SWMTKN token）後，在 wcs2 / wcs3 執行
docker swarm join --token SWMTKN-xxxx 10.0.0.4:2377

# 驗證節點
docker node ls
```

實際案例：wcs1 為 manager，wcs2、wcs3 為 worker，成功加入後可見 docker node ls 列出 3 節點。
實作環境：Azure Windows Server 2016 Datacenter with Containers（3 台），同一 VNet。
實測數據：
改善前：無叢集，不可部署服務
改善後：3 節點 Swarm 可運行服務
改善幅度：未提供（功能達成）

Learning Points（學習要點）
核心知識點：
- Swarm Manager/Worker 節點角色
- advertise-addr 與 listen-addr 的用途
- 叢集初始化與節點加入流程
技能要求：
- 必備技能：Azure VM 建置、基本 Docker CLI
- 進階技能：VNet 與私網位址規劃
延伸思考：
- 如何以 IaC（ARM/Bicep/Terraform）自動化建置？
- Swarm Manager 高可用如何規劃？
- 叢集節點擴縮的標準作業流程？

Practice Exercise（練習題）
基礎練習：新增第 4 台 worker 並成功加入（30 分鐘）
進階練習：新增第 2 台 manager，測試 manager 失效時叢集行為（2 小時）
專案練習：以腳本實現 3 節點自動化建置與初始化（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可見 3 節點、正確角色、可用
程式碼品質（30%）：初始化指令與紀錄清楚
效能優化（20%）：初始化時間與重試策略
創新性（10%）：加入 IaC 或自動化腳本


## Case #2: 建立 Azure Container Registry 與啟用 Admin User 以便節點認證

### Problem Statement（問題陳述）
業務場景：團隊需將自有映像集中管理並供叢集節點快速拉取，避免從 Docker Hub 跨網拉取造成速度與穩定性問題。
技術挑戰：如何在 Azure 建立 ACR、啟用 Admin User、設定密碼，並於節點使用 docker login 寫入認證。
影響範圍：未有私庫或無法認證時，服務建立與拉取會失敗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無私有 Registry，節點需跨網從 Hub 拉取大型 Windows 映像。
2. ACR 預設未啟用 Admin User，無法直接以帳密登入。
3. 未設定密碼或未下發到節點，導致認證失敗。
深層原因：
- 架構層面：缺少企業級映像治理與近端倉庫。
- 技術層面：Swarm 節點需具備拉取權限。
- 流程層面：未建立統一的節點認證下發流程。

### Solution Design（解決方案設計）
解決策略：在 Azure 入口建立 ACR（同區域），啟用 Admin User 與密碼，於各節點使用 docker login 寫入認證。

實施步驟：
1. 建立 ACR 並啟用 Admin User
- 實作細節：Portal 建立 ACR，Access Keys -> Enable Admin User -> 設定密碼
- 所需資源：Azure Portal/CLI
- 預估時間：5-10 分鐘

2. 節點登入 ACR
- 實作細節：於 wcs1、wcs2、wcs3 分別 docker login
- 所需資源：Docker CLI
- 預估時間：5 分鐘

關鍵程式碼/設定：
```shell
# 各節點登入（以 wcshub.azurecr.io 為例）
docker login -u <acr-username> -p <acr-password> wcshub.azurecr.io
# Login Succeeded
```

實際案例：ACR 名稱 wcshub，啟用 Admin User，三節點成功登入。
實作環境：Azure ACR + Windows 節點
實測數據：
改善前：節點匿名拉取受限、速度慢
改善後：節點本地已儲存認證，可快速拉取
改善幅度：未提供

Learning Points（學習要點）
核心知識點：
- ACR 建置與費用模式（僅存儲計費）
- Admin User 與 docker login 流程
- 私有 Registry 在叢集中的角色
技能要求：
- 必備技能：Azure Portal 操作、Docker 基本命令
- 進階技能：使用服務主體與最低權限（延伸思考）
延伸思考：
- 生產環境避免 Admin User，改用 SPN/Managed Identity？
- 同區域部署與網路對映的最佳化？
- ACR Webhook 與 CI/CD 整合？

Practice Exercise（練習題）
基礎練習：啟用 Admin User 並完成 1 節點 docker login（30 分鐘）
進階練習：完成 3 節點 docker login 並驗證 pull（2 小時）
專案練習：撰寫腳本自動化 ACR 建立與節點認證（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：ACR 可用，節點可登入
程式碼品質（30%）：命令清楚、無硬編碼敏感資訊
效能優化（20%）：近區部署、拉取時間改善
創新性（10%）：自動化與安全最佳實踐


## Case #3: 將映像重標籤並推送到 ACR（Tag + Push 流程）

### Problem Statement（問題陳述）
業務場景：團隊需將公開映像或自建映像統一納入 ACR 管理與分發。
技術挑戰：Docker push 需包含 registry endpoint，未正確標籤會導致推送失敗。
影響範圍：鏡像分發不穩、節點拉取延誤。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未以 {registry}/{image}:{tag} 命名，push 目標不正確。
2. 未先 pull/本地無映像，導致 tag 無對象。
3. 未登入 ACR，推送 401。
深層原因：
- 架構層面：映像命名規範未制定。
- 技術層面：Tag 與完整名稱對推送行為的影響。
- 流程層面：未建立「pull → tag → push → 驗證」標準流程。

### Solution Design（解決方案設計）
解決策略：嚴格遵循完整映像命名，先 pull 後 tag，再 push 到 ACR。

實施步驟：
1. 拉取來源映像
- 實作細節：docker pull 來源（例如 Docker Hub）
- 預估時間：依映像大小

2. 重標籤至 ACR
- 實作細節：docker tag <src> <acr>/<repo>:<tag>
- 預估時間：1 分鐘

3. 推送到 ACR
- 實作細節：docker push <acr>/<repo>:<tag>
- 預估時間：依映像大小

關鍵程式碼/設定：
```shell
docker pull andrew0928/vs20:latest
docker tag andrew0928/vs20:latest wcshub.azurecr.io/vs20:latest
docker push wcshub.azurecr.io/vs20:latest
```

實際案例：vs20:latest 重標籤後推送至 wcshub.azurecr.io/vs20:latest。
實作環境：本機/節點 Docker + ACR
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- 完整映像名稱規範
- tag 與 push 的關係
- ACR 名稱在映像 URI 中的角色
技能要求：
- 必備技能：Docker pull/tag/push
- 進階技能：ACR 存取權限控管
延伸思考：
- 多架構（amd64/arm64）映像流程？
- Tag 與版本策略如何制定？
- 自動化 pipeline 中的 tag 管理？

Practice Exercise（練習題）
基礎練習：將任一公共映像重標籤並推送至 ACR（30 分鐘）
進階練習：以多 tag（latest、v1）推送並測 pull（2 小時）
專案練習：撰寫 CI 腳本自動完成 tag/push（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：映像可被正確拉取
程式碼品質（30%）：命令與命名一致
效能優化（20%）：合理分層與大小
創新性（10%）：版本與標籤策略


## Case #4: 使用私有 Registry 建立 Swarm Service 出現 no basic auth credentials

### Problem Statement（問題陳述）
業務場景：在 Swarm 以 service create 從 ACR 拉取私有映像部署服務。
技術挑戰：create service 時回報 Head ... no basic auth credentials。
影響範圍：服務無法建立，阻礙部署。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 節點未 docker login ACR，無本地認證。
2. service create 預設不會將 client 的認證傳給排程節點。
3. 採用私有 repo 未傳遞 auth header。
深層原因：
- 架構層面：Swarm 認證傳遞機制需顯式啟用。
- 技術層面：Windows 節點各自保存認證。
- 流程層面：缺乏建立服務前的「全節點登入」步驟。

### Solution Design（解決方案設計）
解決策略：先在所有節點 docker login ACR，並於 service create 時加入 --with-registry-auth 將認證一併傳遞。

實施步驟：
1. 各節點預先登入 ACR
- 實作細節：wcs1、wcs2、wcs3 分別 docker login
- 預估時間：5 分鐘

2. 建立服務並傳遞認證
- 實作細節：於 manager 節點 create service 時加 --with-registry-auth
- 預估時間：5 分鐘

關鍵程式碼/設定：
```shell
# 節點登入
docker login -u <acr-user> -p <acr-pass> wcshub.azurecr.io

# 錯誤示例（將會失敗）
docker service create --name mvcdemo -p 80:80 wcshub.azurecr.io/vs20:latest

# 正確示例（傳遞認證）
docker service create --name mvcdemo --with-registry-auth -p 80:80 wcshub.azurecr.io/vs20:latest
```

實際案例：原文錯誤訊息與修正指令如上。
實作環境：Windows Swarm + ACR
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- --with-registry-auth 的用途
- 節點本地認證存放與作用
- 私有倉庫在 Swarm 建立服務時的行為
技能要求：
- 必備技能：Docker 認證管理
- 進階技能：腳本自動下發認證（見 Case #12）
延伸思考：
- 使用 Docker Secrets/ Credential Spec 管理認證？
- 多 Registry 情境如何管理？
- 認證輪換的 SOP？

Practice Exercise（練習題）
基礎練習：重現錯誤並修正（30 分鐘）
進階練習：在 3 節點驗證可成功拉取（2 小時）
專案練習：寫腳本驗證每節點認證狀態並建立服務（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：服務成功建立
程式碼品質（30%）：命令與錯誤處理清楚
效能優化（20%）：減少重試與等待
創新性（10%）：自動化認證分發


## Case #5: Routing Mesh 不支援導致無法透過 -p 80:80 存取，改用 Host 模式發布連接埠

### Problem Statement（問題陳述）
業務場景：部署 ASP.NET MVC 容器服務並期望以 -p 80:80 直接對外存取。
技術挑戰：Windows Swarm 當時不支援 routing mesh，預設 -p 對應 ingress mesh 無效，瀏覽器無法連線服務。
影響範圍：服務雖運行，卻對外不可達。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Windows Docker 主機尚不支援 Routing Mesh（當時）。
2. 預設 -p 對 ingress mesh 發佈，不會落地到 host。
3. 缺乏外部負載平衡與 host port 綁定。
深層原因：
- 架構層面：叢集網路功能在 Windows 平台落後。
- 技術層面：--publish 須選擇 mode。
- 流程層面：未事先驗證平臺差異。

### Solution Design（解決方案設計）
解決策略：改用 host 模式發布連接埠（--publish mode=host,target=80,published=80），每節點各自對外提供 80 埠。

實施步驟：
1. 移除舊服務（若有）
- 實作細節：docker service rm mvcdemo
- 預估時間：1 分鐘

2. Host 模式建立服務
- 實作細節：指定 --publish mode=host
- 預估時間：3 分鐘

3. 逐節點測試
- 實作細節：以各節點 Public IP:80 驗證
- 預估時間：5 分鐘

關鍵程式碼/設定：
```shell
docker service create --name mvcdemo \
  --with-registry-auth \
  --mode global \
  --publish mode=host,target=80,published=80 \
  wcshub.azurecr.io/vs20:latest
```

實際案例：wcs1~wcs3 分別以各自 IP 顯示不同 Server IP 標示頁。
實作環境：Windows Swarm
實測數據：
改善前：無法對外存取
改善後：可透過各節點 IP 存取
改善幅度：功能恢復（未提供量化）

Learning Points（學習要點）
核心知識點：
- --publish 的 mode（ingress vs host）
- Windows 平台與 Linux 的差異
- 叢集對外暴露策略
技能要求：
- 必備技能：Swarm service 參數
- 進階技能：規劃外部 LB（見 Case #10）
延伸思考：
- 如何以 Azure Load Balancer 匯聚多節點？
- Service Mesh/Ingress Controller 的替代？
- 未來 Routing Mesh 支援到位的切換策略？

Practice Exercise（練習題）
基礎練習：以 host 模式重建服務並逐節點測試（30 分鐘）
進階練習：改為 replicas 模式測多副本（2 小時）
專案練習：配合外部 LB 完成 L4/L7 對外服務（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可對外連線
程式碼品質（30%）：參數正確、可重現
效能優化（20%）：合理副本與資源
創新性（10%）：結合 LB 的方案設計


## Case #6: 無法從外網存取服務：開啟 Windows 防火牆與 Azure NSG 入站規則

### Problem Statement（問題陳述）
業務場景：服務已以 host 模式發布 80 埠，但仍無法由外網瀏覽。
技術挑戰：Windows 防火牆或 Azure NSG 未允許 80/TCP 入站。
影響範圍：服務不可達，影響驗證與測試。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. VM Windows 防火牆未放行 80/TCP。
2. NSG 未加開 80/TCP 入站。
3. 企業代理/網段控管阻擋。
深層原因：
- 架構層面：多層網安管控。
- 技術層面：主機與雲端防火牆雙層。
- 流程層面：缺少標準開孔清單。

### Solution Design（解決方案設計）
解決策略：同時檢查並放行 VM 防火牆與 NSG 入站規則的 80 埠。

實施步驟：
1. 開啟 VM Windows 防火牆 80/TCP
- 實作細節：以 PowerShell 新增規則
- 預估時間：5 分鐘

2. 設定 NSG 入站規則
- 實作細節：Azure 入口或 CLI 新增 80/TCP Allow
- 預估時間：5 分鐘

關鍵程式碼/設定：
```powershell
# VM 內執行
New-NetFirewallRule -DisplayName "HTTP 80" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow
```

實際案例：作者提醒「記得打開 Azure VM 的防火牆」。
實作環境：Azure VM + NSG
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- 主機防火牆 vs NSG
- 網路連通性排查順序
- 叢集服務對外暴露最佳實務
技能要求：
- 必備技能：Windows 防火牆與 Azure NSG
- 進階技能：以測試工具（tcpping/curl）排查
延伸思考：
- 自動化網路健康檢查？
- 管控變更審核流程？
- 最小開孔原則與安全基線？

Practice Exercise（練習題）
基礎練習：放行 80/TCP 並驗證（30 分鐘）
進階練習：加入 443/TCP 並測試 HTTPS（2 小時）
專案練習：以 IaC 定義 NSG 規則（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可自外網連線
程式碼品質（30%）：規則清楚、無過度開放
效能優化（20%）：最小必要開孔
創新性（10%）：自動化與審核流程


## Case #7: 跨節點通訊失敗：使用 Overlay Network（ingress）

### Problem Statement（問題陳述）
業務場景：多節點容器之間需互通與服務探索，單機 NAT 無法跨主機。
技術挑戰：如何透過 overlay network 讓服務跨節點互通。
影響範圍：服務拆分與多容器協作受阻。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Docker NAT 僅限單機，跨主機不通。
2. 未加入 overlay network。
3. 未了解 ingress 與自訂 overlay 的差異。
深層原因：
- 架構層面：跨主機網路抽象需 overlay。
- 技術層面：Swarm 自動建立 ingress（routing mesh），但 Windows 當時不支援 mesh。
- 流程層面：service 未正確附掛網路。

### Solution Design（解決方案設計）
解決策略：使用 Swarm 內建 ingress overlay 作為跨節點網路，並在 service create 時指定 --network。

實施步驟：
1. 檢查網路清單
- 實作細節：docker network ls，確認有 ingress
- 預估時間：1 分鐘

2. 指定網路建立服務
- 實作細節：--network ingress
- 預估時間：3 分鐘

關鍵程式碼/設定：
```shell
docker network ls
docker service create --name mvcdemo \
  --with-registry-auth \
  --network ingress \
  --replicas 3 \
  wcshub.azurecr.io/vs20:latest
```

實際案例：作者解釋 ingress overlay 的角色與限制。
實作環境：Windows Swarm
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- NAT vs Overlay
- ingress overlay 概念
- 服務附掛網路的重要性
技能要求：
- 必備技能：Docker 網路基本操作
- 進階技能：自訂 overlay 與多網路綁定
延伸思考：
- 何時需要自訂 overlay？
- 多網段/多租戶隔離？
- 後續 Mesh 功能到位時如何切換？

Practice Exercise（練習題）
基礎練習：建立附 ingress 的 replicated 服務（30 分鐘）
進階練習：建立第二個服務並進行跨服務通訊測試（2 小時）
專案練習：設計多 overlay 網路拓撲（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：跨節點通訊可行
程式碼品質（30%）：網路參數正確
效能優化（20%）：合理副本與連線
創新性（10%）：網路拓撲設計


## Case #8: 觀測與除錯 service 啟動失敗：使用 docker service ls/ps

### Problem Statement（問題陳述）
業務場景：服務在部分節點啟動失敗（例如 wcs3 首次啟動失敗後重啟）。
技術挑戰：如何快速定位失敗節點與任務狀態。
影響範圍：降低可用性，影響驗證與用戶體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 任務拉取/啟動過程 transient 錯誤。
2. 資源不足或暫時性網路問題。
3. 未即時觀察任務狀態。
深層原因：
- 架構層面：分散式系統中的節點差異。
- 技術層面：需要工具查看任務生命周期。
- 流程層面：缺乏標準健康檢查流程。

### Solution Design（解決方案設計）
解決策略：使用 docker service ls 概覽與 docker service ps <service> 檢視每個任務的歷史、Failed/Shutdown/Running。

實施步驟：
1. 檢視服務清單與狀態
- 實作細節：docker service ls
- 預估時間：1 分鐘

2. 檢視特定服務的任務
- 實作細節：docker service ps mvcdemo
- 預估時間：1 分鐘

3. 進一步調查
- 實作細節：docker inspect、docker logs（視容器支援）
- 預估時間：15-30 分鐘

關鍵程式碼/設定：
```shell
docker service ls
docker service ps mvcdemo
# 進一步
docker ps -a
docker logs <container-id>
docker inspect <task-or-service>
```

實際案例：作者顯示 wcs3 有一次失敗後再成功的紀錄。
實作環境：Windows Swarm
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- service 與 task 的關係
- service ls / ps 的訊息解讀
- 常見失敗模式
技能要求：
- 必備技能：Docker 觀測指令
- 進階技能：事件追蹤與日誌蒐集
延伸思考：
- 建置集中式日誌與度量系統？
- 健康探測與自動修復？
- 異常自動告警？

Practice Exercise（練習題）
基礎練習：故意指定不存在映像，觀察失敗（30 分鐘）
進階練習：限縮資源造成失敗並排查（2 小時）
專案練習：串接 ELK/EFK 收集 service 事件（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能準確定位任務狀態
程式碼品質（30%）：指令組合合理
效能優化（20%）：縮短定位時間
創新性（10%）：告警與可觀測性整合


## Case #9: 保證每節點一份：使用 Global 服務模式

### Problem Statement（問題陳述）
業務場景：希望在叢集中每個節點都跑一份容器（如代理、監控 agent 或本例的示範網站）。
技術挑戰：預設 replicated 模式僅控副本數，不能保證每節點都有。
影響範圍：節點覆蓋不完整，影響一致性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用預設 replicated 模式。
2. 未理解 --mode global 的語意。
3. 未基於需求選擇正確模式。
深層原因：
- 架構層面：服務部署策略差異。
- 技術層面：Global vs Replicated 設定。
- 流程層面：需求分析不足。

### Solution Design（解決方案設計）
解決策略：使用 --mode global 讓每個節點各自部署一份，便於測試與示範。

實施步驟：
1. 建立 Global 服務
- 實作細節：--mode global
- 預估時間：3 分鐘

2. 驗證每節點有一份
- 實作細節：docker service ps mvcdemo 檢視分配
- 預估時間：5 分鐘

關鍵程式碼/設定：
```shell
docker service create --name mvcdemo \
  --with-registry-auth \
  --mode global \
  --publish mode=host,target=80,published=80 \
  wcshub.azurecr.io/vs20:latest
```

實際案例：作者以 global 模式在 3 節點各一份，瀏覽各節點 IP 顯示不同 Server IP。
實作環境：Windows Swarm
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- global 與 replicated 模式差異
- 節點覆蓋與服務用途
- 與資源規劃的關係
技能要求：
- 必備技能：service 參數
- 進階技能：placement constraints
延伸思考：
- 如何排除特定節點（標籤/污點）？
- Global 與 DaemonSet（K8s）的對照？
- 混合模式的案例？

Practice Exercise（練習題）
基礎練習：建立 global 服務並驗證（30 分鐘）
進階練習：改用 replicated=5 並比對差異（2 小時）
專案練習：設計 agent 類服務布署（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：每節點各一份
程式碼品質（30%）：參數正確
效能優化（20%）：節點與資源均衡
創新性（10%）：placement 規劃


## Case #10: DNSRR 服務探索未如預期的權宜：外部負載平衡器

### Problem Statement（問題陳述）
業務場景：欲使用 Docker 原生 DNSRR 完成服務探索與負載平衡。
技術挑戰：在 Windows Swarm 上作者實測無法以 nslookup 解析出服務的多 IP，DNSRR 未生效。
影響範圍：無法自動發現副本，難以用 NGINX 等動態 upstream。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. Windows Swarm 當時不支援 routing mesh，且 DNSRR 行為異常。
2. 服務端點未透過 Docker DNS 返回多 A 記錄。
3. 測試在 ingress 上執行仍不可得。
深層原因：
- 架構層面：Windows 叢集網路功能尚未齊備。
- 技術層面：Docker 原生 DNS 在 Windows 行為差異/限制。
- 流程層面：需規劃替代方案（外部 LB）。

### Solution Design（解決方案設計）
解決策略：退而求其次，使用外部負載平衡器（如 NGINX for Windows），對各節點的 host-published 80 埠做 Round Robin。

實施步驟：
1. 建置外部 NGINX
- 實作細節：安裝 NGINX for Windows 或使用獨立 VM
- 預估時間：30-60 分鐘

2. 設定 upstream 與反向代理
- 實作細節：上游指向各節點 IP:80
- 預估時間：15 分鐘

3. 驗證負載分配
- 實作細節：反覆刷新觀察 Server IP 變化
- 預估時間：15 分鐘

關鍵程式碼/設定：
```nginx
# nginx.conf 片段
http {
  upstream mvcdemo_upstream {
    server 10.0.0.4:80;
    server 10.0.0.5:80;
    server 10.0.0.6:80;
  }
  server {
    listen 80;
    location / {
      proxy_pass http://mvcdemo_upstream;
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-For $remote_addr;
    }
  }
}
```

實際案例：作者說明 DNSRR 未成功，建議外部 LB 作為替代策略。
實作環境：Windows Swarm + NGINX for Windows
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- Docker DNSRR 與其限制
- 以外部 LB 實現 RR
- host-publish 與 LB 搭配
技能要求：
- 必備技能：NGINX 基本設定
- 進階技能：健康檢查、權重、熔斷
延伸思考：
- 改用 Azure Load Balancer/Application Gateway？
- DNSRR 後續可用時的切換？
- 以服務註冊中心替代 DNSRR？

Practice Exercise（練習題）
基礎練習：以 NGINX 做基本 RR（30 分鐘）
進階練習：加入健康檢查與超時設定（2 小時）
專案練習：以 IaC 建置前端 LB + 後端節點（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可分流至三節點
程式碼品質（30%）：nginx.conf 清晰
效能優化（20%）：健康檢查、超時設定
創新性（10%）：結合雲端 LB 或自動化


## Case #11: 大型 Windows 映像拉取過慢：就近使用 ACR 提升效率

### Problem Statement（問題陳述）
業務場景：Windows Server Core 基底映像達 10GB 級別，多節點同時拉取耗時且占頻寬。
技術挑戰：跨區拉取與頻寬瓶頸，使部署延遲。
影響範圍：部署時間拉長、成本上升。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 來源倉庫（Docker Hub）與叢集不在同區。
2. 映像巨大（servercore ~10GB）。
3. 多節點重複下載。
深層原因：
- 架構層面：倉庫就近策略缺失。
- 技術層面：Windows 基底映像偏大。
- 流程層面：缺乏映像快取與分發策略。

### Solution Design（解決方案設計）
解決策略：在與叢集相同區域建立 ACR，將映像推送至 ACR，節點由近端拉取。

實施步驟：
1. 確認叢集區域
- 實作細節：將 ACR 建在相同 Region
- 預估時間：5 分鐘

2. 將映像推送 ACR
- 實作細節：pull → tag → push（見 Case #3）
- 預估時間：視映像大小

3. 節點自 ACR 拉取
- 實作細節：docker pull wcshub.azurecr.io/...
- 預估時間：視映像大小

關鍵程式碼/設定：
```shell
docker pull wcshub.azurecr.io/vs20:latest
docker service create --name mvcdemo --with-registry-auth wcshub.azurecr.io/vs20:latest
```

實際案例：作者指出 ACR 僅收存儲費、近端拉取更快。
實作環境：ACR + Windows 節點
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- 同區部署的重要性
- Windows 基底映像大小差異
- 多節點拉取行為
技能要求：
- 必備技能：ACR 操作
- 進階技能：映像瘦身（見 Case #15/17）
延伸思考：
- 以 Cache/Registry Mirror 降低外部流量？
- P2P 分發（如 BitTorrent）方案？
- 階段性預熱映像策略？

Practice Exercise（練習題）
基礎練習：從 ACR 拉取並記錄耗時（30 分鐘）
進階練習：比較 Hub 與 ACR 拉取時間（2 小時）
專案練習：設計映像預熱流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可從 ACR 拉取
程式碼品質（30%）：流程清楚
效能優化（20%）：拉取時間下降
創新性（10%）：預熱與快取策略


## Case #12: 一次對所有節點完成 docker login（PowerShell 遠端）

### Problem Statement（問題陳述）
業務場景：叢集內多節點需登入 ACR，手動逐台效率低。
技術挑戰：Windows 節點需要集中化發送 docker login。
影響範圍：容易遺漏節點，導致部署失敗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Swarm 不會自動分發 Registry 認證。
2. 人工逐台耗時。
3. 易因密碼錯誤或未更新失敗。
深層原因：
- 架構層面：認證以主機為單位存放。
- 技術層面：需使用 WinRM/PowerShell Remoting。
- 流程層面：缺乏自動化腳本。

### Solution Design（解決方案設計）
解決策略：使用 PowerShell 遠端在節點上執行 docker login，集中化管理。

實施步驟：
1. 準備節點名單與認證
- 實作細節：安全保存 ACR 帳密
- 預估時間：10 分鐘

2. 使用 Invoke-Command 遠端下發
- 實作細節：在管理機器跑腳本
- 預估時間：10 分鐘

關鍵程式碼/設定：
```powershell
$nodes = @("wcs1","wcs2","wcs3")
$acr = "wcshub.azurecr.io"
$user = "<acr-user>"
$pass = "<acr-pass>"

Invoke-Command -ComputerName $nodes -ScriptBlock {
  param($acr,$user,$pass)
  docker login -u $user -p $pass $acr
} -ArgumentList $acr,$user,$pass
```

實際案例：作者指出目前需逐台 login，此為改進方案。
實作環境：Windows 節點 + WinRM
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- Docker 認證分發的局限
- PowerShell 遠端操作
- 機密管理
技能要求：
- 必備技能：PowerShell
- 進階技能：安全憑證/機密庫整合
延伸思考：
- 使用 DSC/Ansible for Windows？
- 憑證輪換自動化？
- 以 Secrets 管理替代帳密？

Practice Exercise（練習題）
基礎練習：用 PS 遠端對 3 節點 login（30 分鐘）
進階練習：加入錯誤重試與回報（2 小時）
專案練習：整合企業憑證庫自動下發（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：全節點登入成功
程式碼品質（30%）：錯誤處理、機密不外洩
效能優化（20%）：相比手動效率提升
創新性（10%）：與憑證庫/CI 整合


## Case #13: 避免參數誤用：docker run -p 與 docker service create --publish 的差異

### Problem Statement（問題陳述）
業務場景：開發者習慣在單機用 run -p，搬到 Swarm 後沿用同參數導致預期落差。
技術挑戰：Swarm 的 --publish 默認針對 ingress mesh；Windows 不支援 routing mesh。
影響範圍：服務不可達或行為差異。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. run -p 與 service --publish 行為不同。
2. 預設 ingress 模式不適用 Windows。
3. 未指定 host 模式。
深層原因：
- 架構層面：單機與叢集語義差異。
- 技術層面：Swarm 網路模式選項。
- 流程層面：缺乏遷移注意清單。

### Solution Design（解決方案設計）
解決策略：明確教會差異與遷移做法：單機 run -p；叢集則多用 --publish mode=host（在 Windows）。

實施步驟：
1. 對照範例比較
- 實作細節：run -p vs service --publish
- 預估時間：10 分鐘

2. 建立正確的 service
- 實作細節：加 --publish mode=host
- 預估時間：5 分鐘

關鍵程式碼/設定：
```shell
# 單機
docker run -d --name mvcdemo -p 80:80 wcshub.azurecr.io/vs20:latest

# 叢集（Windows）
docker service create --name mvcdemo \
  --with-registry-auth \
  --publish mode=host,target=80,published=80 \
  wcshub.azurecr.io/vs20:latest
```

實際案例：作者明確對照 run 與 service create 的語意差異。
實作環境：Windows Swarm
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- run vs service 的概念轉換
- --mode global / --replicas 與端口發布
- ingress vs host 發布
技能要求：
- 必備技能：Docker 基本操作
- 進階技能：叢集網路設計
延伸思考：
- Linux 與 Windows 行為比較？
- 未來 mesh 支援後的策略？
- 如何以文件/模板降低誤用？

Practice Exercise（練習題）
基礎練習：在單機與叢集各運行一次，體會差異（30 分鐘）
進階練習：設計一張 run→service 參數對照表（2 小時）
專案練習：撰寫 scaffolding 腳本自動輸出正確指令（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：成功運作於兩環境
程式碼品質（30%）：對照明確
效能優化（20%）：正確端口與副本策略
創新性（10%）：模板/工具


## Case #14: 在 Azure 多網卡環境中指定 advertise-addr 確保節點互聯

### Problem Statement（問題陳述）
業務場景：Azure VM 可能有多重介面或位址，Swarm 需綁定正確的內部通訊位址。
技術挑戰：未指定 advertise-addr 可能導致節點互聯異常。
影響範圍：節點加入失敗或管理通道不穩。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 預設選錯 NIC/IP。
2. listen-addr 未綁定正確私網 IP。
3. Azure 網路特性（多 IP/多 NIC）。
深層原因：
- 架構層面：控制面通訊需要明確入口。
- 技術層面：init/join 參數需匹配。
- 流程層面：缺乏初始化準則。

### Solution Design（解決方案設計）
解決策略：在 swarm init 指定 --advertise-addr 與 --listen-addr 綁定私網 IP:2377。

實施步驟：
1. 確認私網 IP
- 實作細節：ipconfig / Azure Portal
- 預估時間：5 分鐘

2. 正確初始化
- 實作細節：指定兩個參數
- 預估時間：5 分鐘

關鍵程式碼/設定：
```shell
docker swarm init --advertise-addr 10.0.0.4 --listen-addr 10.0.0.4:2377
```

實際案例：作者於 init 明確指定 10.0.0.4 與 2377。
實作環境：Azure VM（同 VNet）
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- advertise vs listen
- 管理平面端口（2377）
- Azure 私網位址規劃
技能要求：
- 必備技能：網路基礎
- 進階技能：NSG/子網管理
延伸思考：
- 若更換 IP 如何重設？
- 多 Subnet/跨區的限制？
- 端口安全與 ACL？

Practice Exercise（練習題）
基礎練習：以正確私網 IP 初始化（30 分鐘）
進階練習：模擬錯誤 IP 並排查（2 小時）
專案練習：編寫健檢腳本驗證端口/位址（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：節點穩定互聯
程式碼品質（30%）：指令與記錄完整
效能優化（20%）：快速排障
創新性（10%）：健檢與告警


## Case #15: 建立 Console Service 進行網路診斷（nslookup/ping/exec）

### Problem Statement（問題陳述）
業務場景：需在容器內檢驗服務解析與連通性，排查 DNSRR/網路問題。
技術挑戰：需快速在叢集內啟動可交互測試的容器並進入 shell。
影響範圍：若無法定位問題，難以修復服務探索故障。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏診斷容器。
2. 未在相同網路內測試。
3. 未使用 exec 進入容器。
深層原因：
- 架構層面：叢集需內部自檢機制。
- 技術層面：service/exec 使用技巧。
- 流程層面：標準診斷流程缺失。

### Solution Design（解決方案設計）
解決策略：建立簡單 console service（如 windowsservercore ping），以 docker exec 進入，使用 nslookup/ping 檢查。

實施步驟：
1. 建立 console 服務
- 實作細節：--endpoint-mode dnsrr --network ingress
- 預估時間：5 分鐘

2. 進入容器並測試
- 實作細節：docker exec -ti <id> cmd，nslookup/ping
- 預估時間：15 分鐘

關鍵程式碼/設定：
```shell
# 建立 console service
docker service create --name console \
  --with-registry-auth \
  --network ingress \
  --endpoint-mode dnsrr \
  --replicas 3 \
  microsoft/windowsservercore ping -t localhost

# 進入容器
docker ps
docker exec -t -i <container-id> cmd.exe

# 測試
nslookup mvcdemo
ping <mvcdemo-instance-ip>
```

實際案例：作者以 console 測試 nslookup/ping，觀察 DNSRR 未生效。
實作環境：Windows Swarm
實測數據：未提供

Learning Points（學習要點）
核心知識點：
- service 內的診斷方式
- docker exec 與基本網路工具
- 在相同 overlay 測試的重要性
技能要求：
- 必備技能：Docker 操作、Windows 命令列
- 進階技能：容器化診斷工具鏡像
延伸思考：
- 建立標準診斷映像（含 curl/nslookup/tcping）？
- 自動化健康檢查？
- 與觀測平臺整合？

Practice Exercise（練習題）
基礎練習：建立 console 並進行 nslookup（30 分鐘）
進階練習：撰寫一鍵診斷腳本（2 小時）
專案練習：打造團隊通用診斷映像（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能復現/觀察解析行為
程式碼品質（30%）：指令與流程明確
效能優化（20%）：快速定位問題
創新性（10%）：通用診斷工具鏡像


--------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 2, 3, 6, 8, 9, 13, 15
- 中級（需要一定基礎）
  - Case 1, 4, 5, 7, 11, 14
- 高級（需要深厚經驗）
  - Case 10, 12

2) 按技術領域分類
- 架構設計類：Case 1, 7, 9, 10, 14
- 效能優化類：Case 11
- 整合開發類：Case 2, 3, 4, 5, 6, 12, 13
- 除錯診斷類：Case 8, 15, 10
- 安全防護類：Case 2, 4, 12（認證/憑證管理）

3) 按學習目標分類
- 概念理解型：Case 7, 9, 13, 14
- 技能練習型：Case 2, 3, 5, 6, 8, 11, 15
- 問題解決型：Case 1, 4, 10, 12
- 創新應用型：Case 10, 12

--------------------------------
案例關聯圖（學習路徑建議）

- 建議先學：
  1) Case 1（叢集建置）→ 建立基礎環境
  2) Case 2 & 3（ACR 與推送）→ 完成鏡像治理
  3) Case 13（run vs service）→ 建立叢集語意正確心智模型

- 依賴關係：
  - Case 4 依賴 Case 2（ACR 登入）與 Case 3（映像可用）
  - Case 5 依賴 Case 4（能建服務）與 Case 6（網路開放）
  - Case 7 與 Case 5 並行（網路概念與實務）
  - Case 10 依賴 Case 5/7（host 發布、了解 overlay）
  - Case 12 依賴 Case 2（需可用 ACR 認證）
  - Case 11 可搭配 Case 3（推送到 ACR）最佳化拉取
  - Case 8、15 積木式支援所有部署與網路案例
  - Case 14 在 Case 1 初始化時即應掌握

- 完整學習路徑建議：
  - 階段 A（基礎設施）：Case 1 → Case 14 → Case 6
  - 階段 B（映像與私庫）：Case 2 → Case 3 → Case 11
  - 階段 C（服務部署語意）：Case 13 → Case 4 → Case 5 → Case 9 → Case 7
  - 階段 D（診斷能力）：Case 8 → Case 15
  - 階段 E（高級網路與分流）：Case 10
  - 階段 F（自動化與治理）：Case 12

以上案例與路徑，忠實對應原文中的問題、成因、解法與指令操作，並補齊教學化的練習與評估項目，適合用於實戰教學、專案演練與能力評估。