---
layout: synthesis
title: "Rancher - 管理內部及外部 (Azure) Docker Cluster 的好工具"
synthesis_type: solution
source_post: /2016/04/29/rancher-on-azure-lab/
redirect_from:
  - /2016/04/29/rancher-on-azure-lab/solution/
postid: 2016-04-29-rancher-on-azure-lab
---

## Case #1: 選型轉換—以 Rancher 取代 Docker Cloud 降本並補強監控

### Problem Statement（問題陳述）
業務場景：團隊需要以圖形化方式管理多台 Docker 節點，快速佈署、擴縮與升級，同時能看到主機與容器的 CPU/RAM/Disk 使用率。原先評估使用 Docker Cloud，但遇到成本與監控不足的困擾，影響導入決策與持續擴展。

技術挑戰：需同時滿足多叢集管理、可視化監控、內建 LB 與零中斷升級，且控制成本；避免多套工具分散管理。

影響範圍：工具成本遞增、資源可視性不足導致容量規劃與故障診斷困難、上線與維運效率受限。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Docker Cloud 價格結構：免費版僅支援 1 個節點，新增節點每月 USD$15，擴展成本上升。
2. 監控面板不足：缺少 CPU/RAM/DISK 資源使用的儀表板，需另建監控堆疊。
3. 多工具分裂：單一工具無法同時涵蓋 LB、升級與監控，導致維運流程斷裂。

深層原因：
- 架構層面：托管服務功能偏重管理與部署，未整合完整可觀測性。
- 技術層面：監控與事件流需額外代理與資料管線，平台未內建。
- 流程層面：選型未平衡功能深度與成本預算，未建立統一管理面板。

### Solution Design（解決方案設計）
解決策略：改採 Rancher 作為統一的容器管理平台，整合主機/容器監控、內建 LB、In-Service Upgrade 與多環境管理，透過自管模式避免節點授權費，滿足多叢集與可視化監控需求。

實施步驟：
1. 選型與評估
- 實作細節：對照需求清單（監控、LB、升級、成本），確認 Rancher 功能覆蓋。
- 所需資源：需求矩陣、評估報告
- 預估時間：4 小時

2. 建置 Rancher Server
- 實作細節：以 RancherOS 啟動 Docker，部署 rancher/server。
- 所需資源：RancherOS、Docker Host
- 預估時間：1 小時

3. 驗證功能與遷移 PoC
- 實作細節：建立 Stack、啟用 LB、測試升級，驗證監控面板與操作流。
- 所需資源：Docker Compose、測試服務
- 預估時間：4 小時

關鍵程式碼/設定：
```bash
# 啟動 Rancher Server（示意）
docker run -d --restart=unless-stopped -p 8080:8080 rancher/server:stable

# 節點成本對比（說明性）
# Docker Cloud: free 1 node; +USD$15/node/month thereafter
# Rancher: 自管節點，不收節點費（仍有雲端主機成本）
```

實際案例：作者由 Docker Cloud 過渡至 Rancher，理由為成本與監控能力，Rancher 內建主機與容器資源使用視覺化，並支援 LB 與就地升級。

實作環境：Rancher Server（Container）、RancherOS/Docker Engine、瀏覽器 UI

實測數據：
改善前：新增每節點 USD$15/月；缺少資源監控儀表板
改善後：自管節點 0 授權費；具主機與容器資源監控
改善幅度：節省授權費；監控能力由無到有

Learning Points（學習要點）
核心知識點：
- 容器平台選型權衡（功能/成本/維運）
- 自管平台與托管服務的取捨
- 監控能力對容量規劃與穩定性的影響

技能要求：
必備技能：Docker 基礎、容器管理面板操作
進階技能：平台遷移規劃、監控需求設計

延伸思考：
- 中大型團隊如何分層管理與權限控管？
- 自管平台的營運風險（升級、備援）如何控管？
- 若導入混合雲，如何統一監控與告警？

Practice Exercise（練習題）
基礎練習：列出你團隊對容器平台的功能需求清單（30 分鐘）
進階練習：設計從 Docker Cloud 遷移到 Rancher 的 PoC 計畫（2 小時）
專案練習：完成一套 Rancher 平台落地（Dev/Prod 多環境、LB、升級）並出報告（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：多環境、LB、升級與監控皆可用
程式碼品質（30%）：部署腳本清晰、版本標註明確
效能優化（20%）：監控指標可用於容量規劃
創新性（10%）：提出具體遷移與成本優化策略


## Case #2: 使用 RancherOS 快速承載 Rancher Server（解決雞生蛋蛋生雞）

### Problem Statement（問題陳述）
業務場景：需要先部署 Rancher Server 來管理叢集，但 Rancher 本身是容器化服務，若為此另建完整 Linux 冗重且費時。希望用最小系統快速啟動 Docker 與 Rancher Server，降低維運開銷。

技術挑戰：在無既有 Docker Host 的情況下，以最小代價啟動穩定的容器管理平面。

影響範圍：部署速度、主機資源消耗、平台運作穩定性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Rancher Server 需運行在 Docker 上，形成部署前置依賴。
2. 一般 Linux 發行版包含多餘服務，鏡像體積與攻擊面較大。
3. 團隊希望縮短從零到可用的時間。

深層原因：
- 架構層面：管理平面依賴容器執行環境。
- 技術層面：作業系統與 Docker 整合程度影響穩定度與啟動時間。
- 流程層面：若需安裝多套系統套件，流程繁瑣易錯。

### Solution Design（解決方案設計）
解決策略：採用專為 Docker 最小化優化的 RancherOS 作為宿主系統；系統啟動後直接由 Docker 作為 PID 1 啟動，快速以容器方式部署 Rancher Server。

實施步驟：
1. 安裝 RancherOS 至磁碟
- 實作細節：照官方指引安裝，設定開機網路與 Docker。
- 所需資源：RancherOS 映像、安裝手冊
- 預估時間：30 分鐘

2. 啟動 Rancher Server
- 實作細節：以 Docker 執行 rancher/server 並對外開 8080。
- 所需資源：Docker、網路連線
- 預估時間：15 分鐘

關鍵程式碼/設定：
```bash
# 安裝完成後啟動 Rancher Server
docker run -d --restart=unless-stopped -p 8080:8080 --name rancher rancher/server:stable
# 預設管理介面 http://<ip>:8080
```

實際案例：作者以 RancherOS 作為最小宿主，部署 Rancher Server 後約 1–2 分鐘完成啟動，提供 Web 管理 UI。

實作環境：RancherOS、Rancher Server 容器、單一 VM

實測數據：
改善前：需安裝完整 Linux + Docker，步驟繁多
改善後：RancherOS 鏡像僅約 28MB，安裝簡單
改善幅度：部署步驟與 OS 體積顯著下降；啟動約 1–2 分鐘可用

Learning Points（學習要點）
核心知識點：
- 最小化 OS 對容器平台的優勢
- 容器化管理平面部署模式
- 服務對外埠設定與持久化策略

技能要求：
必備技能：Linux/Docker 基礎、網路埠映射
進階技能：最小化系統硬化、主機生命週期管理

延伸思考：
- 用通用 Linux 發行版部署的利弊？
- 如何為管理平面做備援（多節點/快照）？
- 嚴重故障時的快速重建流程？

Practice Exercise（練習題）
基礎練習：在 VM 安裝 RancherOS 並啟動 Rancher Server（30 分鐘）
進階練習：為 Rancher Server 配置持久化存儲與 SSL Proxy（2 小時）
專案練習：自動化安裝腳本（Cloud-Init/Ansible）批量部署（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：Rancher UI 可用、埠對外正確
程式碼品質（30%）：啟動腳本穩定、參數清楚
效能優化（20%）：啟動時間與資源占用合理
創新性（10%）：最小化與備援策略設計


## Case #3: Rancher Server 啟動慢與資源規劃

### Problem Statement（問題陳述）
業務場景：部署 Rancher Server 後，容器啟動需等待 1–2 分鐘才完全可用，團隊初次導入容易誤判為部署失敗，反覆重啟導致時間浪費與風險增加。

技術挑戰：明確規劃管理平面的主機資源與啟動觀察，避免誤操作。

影響範圍：部署效率、平台可用性、誤判與重試造成的不穩定。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Rancher Server 內含多個以 Java 實作的元件，啟動較慢。
2. 預設 VM 記憶體不足易造成初始化延遲。
3. 缺乏啟動健康檢查與等待機制，導致人為重試。

深層原因：
- 架構層面：管理平面本身即是複合性服務。
- 技術層面：JVM 啟動與依賴載入時間無法忽略。
- 流程層面：未建立標準啟動時間與健康檢查 SOP。

### Solution Design（解決方案設計）
解決策略：按官方建議規劃至少 1GB、實務 2GB RAM 的 VM，建立啟動等待與健康檢查標準流程，避免無謂重啟。

實施步驟：
1. 規格調整
- 實作細節：將 Rancher Server VM RAM 設為 2GB，CPU 至少 1 vCPU。
- 所需資源：虛擬化平台
- 預估時間：15 分鐘

2. 啟動 SOP
- 實作細節：啟動後等待 1–2 分鐘，透過日誌或健康檢查 URL 確認可用。
- 所需資源：日誌檢視、瀏覽器
- 預估時間：15 分鐘

關鍵程式碼/設定：
```bash
# 觀察 Rancher Server 日誌直到服務就緒
docker logs -f rancher | sed -n '/Started.*Application/p'

# 健康檢查（示意）
curl -sSf http://<ip>:8080 | grep -i rancher
```

實際案例：作者調整 VM 至 2GB RAM 後，Rancher Server 啟動更穩定，1–2 分鐘可用。

實作環境：Rancher Server、單一 VM

實測數據：
改善前：1GB RAM 偶有延遲；易誤判反覆重啟
改善後：2GB RAM 啟動約 1–2 分鐘；穩定
改善幅度：誤操作下降；啟動時間可預期

Learning Points（學習要點）
核心知識點：
- 管理平面資源規劃
- 服務就緒檢查（logs/health）
- 穩定性與配置關係

技能要求：
必備技能：Docker 日誌、基本監控
進階技能：啟動探針與自動重試策略

延伸思考：
- 如何以 Liveness/Readiness Probe 自動化健康檢查？
- 是否需多實例高可用？
- 如何記錄標準啟動基準以利回歸？

Practice Exercise（練習題）
基礎練習：設定 2GB RAM 並測量啟動時間（30 分鐘）
進階練習：撰寫啟動檢查腳本並整合到 CI（2 小時）
專案練習：設計 HA 架構與自動故障切換（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：啟動 SOP 文件與腳本可用
程式碼品質（30%）：檢查腳本健全
效能優化（20%）：啟動延遲可控
創新性（10%）：自動化與可視化儀表設計


## Case #4: 啟用 Rancher Server 權限控管（預設無密碼的安全風險）

### Problem Statement（問題陳述）
業務場景：Rancher Server 預設可匿名存取，若直接曝露在內網或外網，恐有未授權操作風險；正式環境需落實存取控制與最小權限。

技術挑戰：以最小阻力導入存取控制，避免影響既有使用流。

影響範圍：平台安全、變更風險、審計追蹤。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設無密碼便於入門，但不適用正式環境。
2. 無權限隔離時，任何人可操作環境、刪除資源。
3. 未啟用審計與稽核，不利事後追蹤。

深層原因：
- 架構層面：平台預設偏開發體驗。
- 技術層面：未配置認證供應者（GitHub/AD 等）。
- 流程層面：未建立存取群組與角色權限。

### Solution Design（解決方案設計）
解決策略：啟用 Rancher 的 Access Control（如 GitHub/AD/OAuth 或本地帳號），配置團隊角色與環境隔離，限制對外曝露。

實施步驟：
1. 啟用 Access Control
- 實作細節：Admin > Access Control，選擇供應者，設定允許名單。
- 所需資源：身分供應者憑證
- 預估時間：30 分鐘

2. 權限與環境隔離
- 實作細節：建立使用者與角色，按 Environment 指派權限。
- 所需資源：使用者清單、角色矩陣
- 預估時間：1 小時

關鍵程式碼/設定：
```text
Admin -> Access Control -> Enable
- Provider: GitHub / Local Auth / AD
- Allow List: <org/team/users>
- Roles: Owner / Member / ReadOnly
```

實際案例：作者提醒正式環境勿跳過帳號權限設定，避免未授權操作風險。

實作環境：Rancher Server UI、身分供應者

實測數據：
改善前：匿名可操作所有環境與資源
改善後：需登入並基於角色授權
改善幅度：風險顯著降低，具稽核追蹤

Learning Points（學習要點）
核心知識點：
- 存取控制與最小權限原則
- 環境級隔離與角色授權
- 對外曝露面管理

技能要求：
必備技能：身分管理基礎、RBAC 概念
進階技能：審計/告警整合與密碼學基礎

延伸思考：
- 如何與企業 AD/SSO 整合？
- 對外介面是否需加上反向代理與 WAF？
- 秘密管理（API Key）如何流通與輪替？

Practice Exercise（練習題）
基礎練習：啟用本地帳號並配置兩種角色（30 分鐘）
進階練習：整合 GitHub 團隊授權（2 小時）
專案練習：制定平台安全作業手冊與審計流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：Access Control 正確啟用
程式碼品質（30%）：設定紀錄與備份清晰
效能優化（20%）：登入體驗與可用性
創新性（10%）：安全自動化與審計報表


## Case #5: 多環境（Dev/Prod）集中管理與快速切換

### Problem Statement（問題陳述）
業務場景：同時營運內部開發與雲上正式環境，需在單一控制台中切換管理，降低誤操作與環境交叉影響，支援獨立擴縮與升級流程。

技術挑戰：多叢集隔離、權限分離與快速切換。

影響範圍：部署風險、維運效率、權限治理。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 開發與正式需求不同，需資源與權限隔離。
2. 多平台（內部與 Azure）管理分散，切換成本高。
3. 缺乏集中監控與策略一致性。

深層原因：
- 架構層面：多叢集/多環境架構缺乏統一控制面。
- 技術層面：環境設定與命名空間治理不足。
- 流程層面：未建立環境切換與操作權限 SOP。

### Solution Design（解決方案設計）
解決策略：在 Rancher 建立多個 Environment（如 Local Dev、Azure Prod），在單一 UI 內各自納管 Hosts/Stacks，並以右上角切換器快速切換；環境間完全隔離。

實施步驟：
1. 建立 Environment
- 實作細節：Environment > Manage > Add，選 Orchestration（Cattle）。
- 所需資源：環境命名與用途定義
- 預估時間：30 分鐘

2. 各自加入 Hosts
- 實作細節：在不同環境中分別加入本地與 Azure 節點。
- 所需資源：主機或雲端帳號
- 預估時間：1–2 小時

關鍵程式碼/設定：
```text
Environment -> Manage Environments -> Add Environment
- Name: Local Dev / Azure Prod
- Orchestration: Cattle (default)
# 右上角 Environment 切換器快速切換視圖
```

實際案例：作者建立 Local 與 Azure 兩個環境，以單一 Rancher 管理，達成開發與正式分離。

實作環境：Rancher Server、內部 VM、Azure VM

實測數據：
改善前：多介面、多平台切換成本高
改善後：單一 UI 切換環境、隔離納管
改善幅度：操作一致性提升、誤操作風險降低

Learning Points（學習要點）
核心知識點：
- 多環境管理模式與隔離邊界
- Orchestration 選型與一致性
- 權限與操作邏輯分區

技能要求：
必備技能：Rancher UI、節點管理
進階技能：環境即程式碼（IaC）與命名規範

延伸思考：
- 如何為每個環境制定不同的擴縮與升級策略？
- 日誌與監控是否要跨環境集中？
- 多雲場景如何實作一致性治理？

Practice Exercise（練習題）
基礎練習：建立 Dev/Prod 兩個環境（30 分鐘）
進階練習：為兩環境分別加入 2 台主機（2 小時）
專案練習：在兩環境分別部署同一個 Stack 並比較差異（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：多環境可切換、主機納管成功
程式碼品質（30%）：命名與標籤規範
效能優化（20%）：切換與查找效率
創新性（10%）：環境治理與自動化策略


## Case #6: 以 Rancher Agent 將本地主機加入叢集

### Problem Statement（問題陳述）
業務場景：需將三台本地 VM（RancherOS）加入 Local 環境成為節點，讓平台統一部署與監控。手動逐台配置易錯且耗時。

技術挑戰：快速、安全地註冊主機並上報資源狀態。

影響範圍：叢集就緒時間、節點一致性與可觀測性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 節點加入需發佈 Agent 與 Token/URL 綁定。
2. 多台主機手工操作容易參數不一致。
3. 缺乏節點標籤與環境歸屬管理。

深層原因：
- 架構層面：主控端-代理端註冊模型。
- 技術層面：網路/憑證/Token 的正確配置。
- 流程層面：缺少註冊 SOP 與標籤策略。

### Solution Design（解決方案設計）
解決策略：使用 Rancher UI 的 Add Host（Custom）給出的註冊命令，在主機上執行一次；3–5 分鐘內 Agent 完成註冊並回報資源監控。

實施步驟：
1. 取得註冊命令
- 實作細節：Infrastructure > Hosts > Add Host（Custom）複製命令。
- 所需資源：Rancher UI、網路通
- 預估時間：5 分鐘

2. 主機執行註冊
- 實作細節：貼上命令，待 Agent 完成上線。
- 所需資源：Docker Engine、root 權限
- 預估時間：每台 3–5 分鐘

關鍵程式碼/設定：
```bash
# 於 Host 上執行（命令由 UI 生成，以下為示意）
sudo docker run -e CATTLE_AGENT_IP=<HOST_IP> \
  -e CATTLE_HOST_LABELS='env=dev' \
  --privileged -v /var/run/docker.sock:/var/run/docker.sock \
  -v /var/lib/rancher:/var/lib/rancher \
  rancher/agent:vX.Y.Z http://<RANCHER_SERVER>:8080/v1/scripts/<TOKEN>
```

實際案例：作者將三台本地 VM 以 Agent 註冊，UI 中可見主機與容器資源使用。

實作環境：RancherOS、Rancher Agent、Local Environment

實測數據：
改善前：手工整備節點、監控未接入
改善後：3–5 分鐘/台完成註冊，監控到位
改善幅度：節點納管效率顯著提升

Learning Points（學習要點）
核心知識點：
- 主控端/代理端註冊模型
- 節點標籤策略
- 節點監控資料上報

技能要求：
必備技能：Docker 操作、Linux 權限
進階技能：批次化節點註冊（Ansible/Shell）

延伸思考：
- 大量節點如何批量註冊與標籤一致性？
- 註冊 URL/Token 如何保密與輪替？
- 節點淘汰的清理流程？

Practice Exercise（練習題）
基礎練習：註冊 1 台本地節點（30 分鐘）
進階練習：以腳本註冊 3 台節點並加上標籤（2 小時）
專案練習：撰寫 Ansible Role 自動註冊與驗證（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：節點成功上線且監控可見
程式碼品質（30%）：註冊腳本穩定可重複
效能優化（20%）：批量註冊耗時
創新性（10%）：標籤與資源治理設計


## Case #7: 透過 Rancher 一鍵在 Azure 佈署多台 Host

### Problem Statement（問題陳述）
業務場景：正式環境需在 Azure 部署多台 Docker Host；若逐台建立 VM、安裝 Docker、註冊 Agent，流程冗長。希望在單一畫面完成多台主機建立與註冊。

技術挑戰：整合雲端供應者憑證、批量建立主機、同步註冊到對應環境。

影響範圍：雲端成本、佈署時間、錯誤率。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手動建立 VM 流程繁複且易錯。
2. 缺乏與雲供應者 API 直接整合的自動化流程。
3. 節點建立與平台註冊步驟分離。

深層原因：
- 架構層面：缺少 IaaS API 與平台的直通整合。
- 技術層面：認證、網路與機型規格組態需要自動化。
- 流程層面：無單一入口完成「建立＋註冊」。

### Solution Design（解決方案設計）
解決策略：用 Rancher 的雲供應商整合，於 Infrastructure > Hosts > Add Host 選 Azure，輸入憑證、規格與台數，一次自動建立並註冊主機。

實施步驟：
1. 設定 Azure 憑證
- 實作細節：於 Rancher 填入 Subscription/Cert 等憑證資訊。
- 所需資源：Azure 帳號與憑證
- 預估時間：30 分鐘

2. 選擇規格與建立
- 實作細節：設定 VM 規格、數量與區域，按 Create 自動建立。
- 所需資源：Azure 資源群組/網路
- 預估時間：10–20 分鐘（取決於台數）

關鍵程式碼/設定：
```text
Infrastructure -> Hosts -> Add Host -> Microsoft Azure
- Subscription/Credential
- Region/VM Size/Count/SSH Key
- Create
# 幾分鐘後節點自動出現在環境中
```

實際案例：作者在 Rancher UI 中配置 Azure 後，一鍵建立多台 Host，幾分鐘完成並出現在平台中。

實作環境：Rancher Server、Azure 訂閱

實測數據：
改善前：逐台建立、安裝、註冊
改善後：一鍵建立多台並自動註冊
改善幅度：佈署時間由數小時縮短至數分鐘等級（依台數）

Learning Points（學習要點）
核心知識點：
- 雲供應者 API 整合
- 憑證與金鑰管理
- 批量資源佈署模式

技能要求：
必備技能：Azure 基礎、網路概念
進階技能：資源模板化與成本控管

延伸思考：
- 如何與企業網路（VPN/ExpressRoute）整合？
- 批量建立是否需加上標籤以利成本歸屬？
- 銷毀與縮容策略？

Practice Exercise（練習題）
基礎練習：以 UI 佈署 1 台 Azure Host（30 分鐘）
進階練習：佈署 3 台並以標籤區分用途（2 小時）
專案練習：以 IaC（Bicep/Terraform）搭配 Rancher 完成端到端（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：主機可自動建立並註冊
程式碼品質（30%）：憑證與設定安全妥當
效能優化（20%）：佈署與回收時間
創新性（10%）：成本與標籤治理


## Case #8: Swarm 叢集無法匯入 Rancher 的限制與替代方案

### Problem Statement（問題陳述）
業務場景：Azure Container Service 可快速建立 Swarm Cluster，但 Rancher 當時版本無法「匯入」既有 Swarm 叢集，導致無法在單一平台管理。

技術挑戰：要在現有雲上 Swarm 與 Rancher 平台間建立管理一致性。

影響範圍：平台一致性、操作體驗、維運成本。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Rancher 當時版本不支援匯入既有 Swarm Cluster。
2. ACS 可一鍵建立 Swarm，但管理面與 Rancher 分離。
3. 兩者整合路線仍在研發中。

深層原因：
- 架構層面：異平台 Orchestrator 整合尚未完成。
- 技術層面：API/狀態同步與權限模型差異。
- 流程層面：平台選型與建立途徑不一致。

### Solution Design（解決方案設計）
解決策略：短期在 Rancher 內建立與註冊節點管理叢集（避免分裂）；關注官方匯入功能進展，或以單一平台維持一致性。

實施步驟：
1. 暫定以 Rancher 建立節點
- 實作細節：避免使用無法被匯入的外部 Swarm 作為主環境。
- 所需資源：Rancher/雲端主機
- 預估時間：依節點數

2. 規劃未來匯入路線
- 實作細節：留意官方公告，避免雙平台並行導致治理困難。
- 所需資源：產品路線追蹤
- 預估時間：持續

關鍵程式碼/設定：
```text
# 官方說明摘要（引述）
"we are working with the Docker team ... a cluster can be created outside of Rancher and automatically imported ..."
# 暫行策略：於 Rancher 內建立與納管叢集，避免平行管理
```

實際案例：作者測試 ACS 建置 Swarm，因 Rancher 尚不支援匯入，暫不採用該路線。

實作環境：Azure Container Service、Rancher

實測數據：
改善前：Swarm 與 Rancher 分離管理
改善後：改以 Rancher 建立與納管
改善幅度：管理一致性提升、避免工具分裂

Learning Points（學習要點）
核心知識點：
- 異平台整合限制辨識
- 短中期替代架構策略
- 選型風險控管

技能要求：
必備技能：基礎 Orchestrator 知識
進階技能：平台路線風險評估

延伸思考：
- 若未來支援匯入，怎麼做平滑遷移？
- 雙平台並行帶來哪些治理成本？
- 是否需事先制定抽象層（如 GitOps）避免綁死？

Practice Exercise（練習題）
基礎練習：整理 Rancher 與 ACS 特性差異（30 分鐘）
進階練習：設計單平台治理藍圖（2 小時）
專案練習：撰寫遷移/匯入的風險清單與回退方案（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：替代方案可落地
程式碼品質（30%）：規劃文件清晰
效能優化（20%）：治理與操作效率
創新性（10%）：遷移策略與風險緩解


## Case #9: 以 Stack + Docker Compose 佈署 Hello-World 服務

### Problem Statement（問題陳述）
業務場景：在新平台驗證部署鏈路，先以最簡服務（tutum/hello-world）建立 Stack，快速確認容器啟動、連線與觀測性，後續再導入業務服務。

技術挑戰：以 Compose 定義服務、透過 UI/CLI 佈署並驗證。

影響範圍：部署鏈路可信度、教學與示範效率。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 新平台需以簡單範例驗證。
2. 需測試對外埠、容器識別與輸出內容。
3. 需為後續 LB 與擴縮鋪路。

深層原因：
- 架構層面：Stack/Service/Container 關係建立。
- 技術層面：Compose 定義與 UI/CLI 映射。
- 流程層面：先易後難、逐步驗證。

### Solution Design（解決方案設計）
解決策略：建立 Stack，貼上（或上傳）Compose 設定，一鍵部署 hello-world，透過輸出顯示容器 ID 驗證多實例與 LB。

實施步驟：
1. 建立 Stack 與 Service
- 實作細節：Applications > Stacks > Add Stack > Add Service。
- 所需資源：Compose 檔
- 預估時間：15 分鐘

2. 驗證對外訪問
- 實作細節：以 Host IP/Port 存取，觀察輸出容器 ID。
- 所需資源：瀏覽器/curl
- 預估時間：10 分鐘

關鍵程式碼/設定：
```yaml
# docker-compose.yml（簡化示意）
version: '2'
services:
  hello:
    image: tutum/hello-world
    ports:
      - "80:80"   # 或由平臺指派動態埠
```

實際案例：作者以 hello-world 快速部署並驗證輸出，為後續 LB 測試準備。

實作環境：Rancher Stack、Compose

實測數據：
改善前：無法快速驗證平台部署路徑
改善後：幾分鐘內完成部署與驗證
改善幅度：部署鏈路驗證門檻大幅降低

Learning Points（學習要點）
核心知識點：
- Stack/Service/Container 概念
- Compose 與平台 UI 的對應
- 最小化驗證方法

技能要求：
必備技能：Compose 基礎
進階技能：多環境參數化

延伸思考：
- 如何把這個流程納入 CI（自動部署）？
- 多節點下的埠管理策略？
- 服務健康檢查的設計？

Practice Exercise（練習題）
基礎練習：部署 hello-world 並對外開放（30 分鐘）
進階練習：以 Compose 加入健康檢查與環境變數（2 小時）
專案練習：寫一條 Git 推送觸發部署的管線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：服務可對外、輸出正常
程式碼品質（30%）：Compose 清楚可維護
效能優化（20%）：啟動時間與資源占用合理
創新性（10%）：自動化與參數化設計


## Case #10: 服務水平擴展—實例數由 2 擴至 3

### Problem Statement（問題陳述）
業務場景：線上服務需調整承載，將 Web 服務由 2 個實例擴展至 3 個，提升容量與容錯。希望由平台自動分散至不同 Host。

技術挑戰：在不中斷情況下調整副本數並確保跨主機分散。

影響範圍：服務容量、可靠度、成本。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 用量上升需增加實例數。
2. 需確保新實例跨主機分布以提升可用性。
3. 手動擴展易錯且耗時。

深層原因：
- 架構層面：橫向擴展需要排程與分散策略。
- 技術層面：副本數與健康檢查關聯。
- 流程層面：擴展需可回退與觀測。

### Solution Design（解決方案設計）
解決策略：於服務頁面調整 Scale 數值至 3，Rancher 自動建立實例並分佈在不同 Host，透過 UI 驗證分散情況。

實施步驟：
1. 調整 Scale
- 實作細節：至 Service 頁面把 Scale 改 3。
- 所需資源：Rancher UI
- 預估時間：5 分鐘

2. 驗證分佈
- 實作細節：檢查實例所在主機、對外訪問結果。
- 所需資源：瀏覽器/curl
- 預估時間：10 分鐘

關鍵程式碼/設定：
```yaml
# rancher-compose.yml（示意）
version: '2'
services:
  hello:
    scale: 3
```

實際案例：作者把服務從 2 擴至 3，三個實例被分配到不同 Host 上。

實作環境：Rancher Stack、多主機

實測數據：
改善前：2 個實例、容量較低
改善後：3 個實例、跨主機分佈
改善幅度：容量與容錯提升（+1 實例）

Learning Points（學習要點）
核心知識點：
- 水平擴展與排程分散
- 副本數與可用性
- 擴展與監控聯動

技能要求：
必備技能：平台操作、服務觀測
進階技能：自動擴縮策略設計

延伸思考：
- 如何根據監控指標自動擴縮？
- 擴展對資料層（DB/Cache）的影響？
- 成本與容量平衡？

Practice Exercise（練習題）
基礎練習：把 hello 擴展到 3（30 分鐘）
進階練習：寫腳本自動調整 scale（2 小時）
專案練習：依 CPU 使用率自動擴縮 PoC（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：實例數正確且可訪問
程式碼品質（30%）：配置明確可重現
效能優化（20%）：擴展過程平順
創新性（10%）：自動擴縮構想


## Case #11: 啟用內建 Load Balancer（HAProxy）進行輪詢分流

### Problem Statement（問題陳述）
業務場景：服務已擴展為多實例，需要單一入口並在多容器間做負載分流，並可跨 Stack 綁定目標。

技術挑戰：快速建置 LB、綁定目標服務並驗證輪詢。

影響範圍：高可用與擴展性、入口治理。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多實例需對外單一入口。
2. 要求簡易配置與可視化管理。
3. 希望支援跨 Stack 綁定。

深層原因：
- 架構層面：服務網關/入口的設計。
- 技術層面：HAProxy 規則與健康檢查。
- 流程層面：LB 與服務版本的耦合。

### Solution Design（解決方案設計）
解決策略：在 Stack 內新增 Load Balancer 服務，指派對外埠，綁定目標 Service；刷新頁面觀察容器 ID 變化以驗證輪詢。

實施步驟：
1. 新增 LB
- 實作細節：Add Service -> Load Balancer，設定 Port 與 Targets。
- 所需資源：Rancher UI
- 預估時間：15 分鐘

2. 驗證輪詢
- 實作細節：持續刷新 LB URL，觀察回應差異。
- 所需資源：瀏覽器/curl
- 預估時間：10 分鐘

關鍵程式碼/設定：
```yaml
# docker-compose.yml（示意：lb + app）
version: '2'
services:
  hello:
    image: tutum/hello-world
  lb:
    image: rancher/lb-service-haproxy
    ports:
      - "80:80"
    links:
      - hello:hello
```

實際案例：作者連續刷新三次，回應對應不同容器 ID，證明輪詢分流生效。

實作環境：Rancher LB（HAProxy）、多實例服務

實測數據：
改善前：需逐一連線不同實例
改善後：單一入口自動分流
改善幅度：操作與擴展性提升

Learning Points（學習要點）
核心知識點：
- LB 基本概念與輪詢策略
- 目標綁定與健康檢查
- 跨 Stack 目標綁定

技能要求：
必備技能：LB 基礎、網路埠
進階技能：HAProxy 高級規則

延伸思考：
- SSL/TLS 終結與憑證管理？
- 權重與 Session 親和性如何配置？
- 與 API Gateway 的分工？

Practice Exercise（練習題）
基礎練習：為 hello 建置 LB 並驗證輪詢（30 分鐘）
進階練習：加入健康檢查與權重（2 小時）
專案練習：為兩個服務共用一個 LB 並設置路徑分流（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：LB 可用與正確分流
程式碼品質（30%）：配置清晰可維護
效能優化（20%）：延遲與錯誤率
創新性（10%）：規則與安全加值


## Case #12: 跨 Stack 將多個服務綁定到同一個 Load Balancer

### Problem Statement（問題陳述）
業務場景：多個應用（不同 Stack）需共用同一組對外入口，透過 LB 規則路由至對應服務，便於域名/埠集中管理。

技術挑戰：跨 Stack 綁定與規則管理。

影響範圍：入口治理、維運便捷性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多 Stack 服務對外入口過多難管理。
2. 希望集中化管理對外端口與域名。
3. LB 規則需支援目標服務跨 Stack。

深層原因：
- 架構層面：入口層集中化設計。
- 技術層面：LB 規則與目標引用。
- 流程層面：變更與版本協調。

### Solution Design（解決方案設計）
解決策略：於 LB 服務的 Target Services 中，選擇跨 Stack 的目標服務，配置路徑/主機名規則，統一入口。

實施步驟：
1. 設置跨 Stack Targets
- 實作細節：在 LB 設定畫面選擇其他 Stack 的服務為目標。
- 所需資源：Rancher UI
- 預估時間：20 分鐘

2. 規則設計
- 實作細節：以 host/path 規則路由。
- 所需資源：域名/路徑規劃
- 預估時間：40 分鐘

關鍵程式碼/設定：
```text
LB -> Add Target
- Select Service: <StackA/serviceA>, <StackB/serviceB>
- Rules: 
  host: appA.example.com -> serviceA
  host: appB.example.com -> serviceB
```

實際案例：作者指出 LB 可跨 Stack 綁定目標服務，統一對外發佈。

實作環境：Rancher LB、兩個以上 Stack

實測數據：
改善前：多入口分散管理
改善後：單一 LB 統一入口
改善幅度：入口治理簡化

Learning Points（學習要點）
核心知識點：
- 跨 Stack 目標綁定
- Host/Path 路由
- 入口統一設計

技能要求：
必備技能：LB 規則配置
進階技能：域名與證書自動化

延伸思考：
- 如何與 DNS/證書自動簽發（ACME）整合？
- 多租戶隔離下的入口治理？
- 入口層的容量規劃？

Practice Exercise（練習題）
基礎練習：同一 LB 綁定兩個服務（30 分鐘）
進階練習：依 Host/Path 分流（2 小時）
專案練習：多環境共用 LB 的規則與風險設計（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：路由正確
程式碼品質（30%）：規則清晰可維護
效能優化（20%）：延遲與錯誤控制
創新性（10%）：自動化與域名治理


## Case #13: In-Service Upgrade 零中斷升級與參數調校

### Problem Statement（問題陳述）
業務場景：線上服務需升級但不可中斷，需就地替換容器，控制批次大小與間隔，並選擇先啟動新容器再停止舊容器的策略。

技術挑戰：配置升級策略參數（Batch Size、Interval、Start Before Stopping），確保流量不中斷。

影響範圍：可用性、升級風險、使用者體驗。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 線上服務無法接受停機。
2. 升級需細緻控制批次與先後順序。
3. 需在舊容器完全退役前驗證新容器健康。

深層原因：
- 架構層面：無狀態服務易於藍綠/滾動升級。
- 技術層面：健康檢查與 LB 流量切換。
- 流程層面：升級/回退 SOP 與觀測性。

### Solution Design（解決方案設計）
解決策略：使用 Rancher 的 In-Service Upgrade，設定 Batch Size=1、適當 Interval，啟用 Start Before Stopping；先起新容器並通過健康檢查，再停舊容器。

實施步驟：
1. 觸發 Upgrade
- 實作細節：Service -> Upgrade，調整 Image/Env/Ports。
- 所需資源：新版本鏡像
- 預估時間：10 分鐘

2. 設定策略參數
- 實作細節：Batch Size、Interval、Start Before Stopping
- 所需資源：服務初始化時間基準
- 預估時間：10 分鐘

3. 監看過程
- 實作細節：確認新容器 Running，舊容器停止。
- 所需資源：UI/日誌
- 預估時間：視規模而定

關鍵程式碼/設定：
```yaml
# 版本升級示意（Compose 片段）
services:
  web:
    image: myapp/web:2.0.0   # 從 1.x 升至 2.0.0
# 升級策略（在 UI 選項中設定）
# - Batch Size: 1
# - Batch Interval: 10s（依應用初始化時間）
# - Start Before Stopping: true
```

實際案例：作者展示升級過程，新舊容器並行，待新容器就緒後舊容器才停止，UI 狀態從 Upgrading -> Upgraded。

實作環境：Rancher Stack、內建 LB

實測數據：
改善前：升級需停機或手動切換，易出錯
改善後：就地滾動升級、不中斷
改善幅度：可用性大幅提升

Learning Points（學習要點）
核心知識點：
- 滾動升級策略
- 批次大小與間隔的權衡
- 先啟動再停止的零中斷思維

技能要求：
必備技能：鏡像版本管理、健康檢查
進階技能：灰度發布/流量切換

延伸思考：
- 有狀態服務如何升級？
- 與資料庫 schema 演進協作？
- 自動化升級 + 失敗回退策略？

Practice Exercise（練習題）
基礎練習：把 hello-world 改版升級（30 分鐘）
進階練習：調整 Batch/Interval 找到最佳值（2 小時）
專案練習：設計零中斷升級流水線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：升級過程不中斷
程式碼品質（30%）：版本與配置管理清晰
效能優化（20%）：升級時延抖動控制
創新性（10%）：灰度與驗證策略


## Case #14: 升級失敗的快速復原—Rollback 策略

### Problem Statement（問題陳述）
業務場景：升級可能因配置或相依問題失敗，需要一鍵回退至升級前狀態，將風險與中斷時間降到最低。

技術挑戰：快速、安全且可重複的回退機制。

影響範圍：可用性、事故影響面、信任度。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 新版本存在未預期錯誤。
2. 升級過程未通過健康檢查。
3. 人工回退步驟繁瑣易錯。

深層原因：
- 架構層面：版本與配置不可變原則。
- 技術層面：舊容器仍在平台內可快速復活。
- 流程層面：回退 SOP 未標準化。

### Solution Design（解決方案設計）
解決策略：使用 Rancher 的 Rollback 按鈕快速回復升級前狀態（停新起舊），將服務恢復到穩定版本。

實施步驟：
1. 觸發 Rollback
- 實作細節：Service -> Rollback，平台自動停止新容器、啟動舊容器。
- 所需資源：UI
- 預估時間：數分鐘

2. 事後檢討
- 實作細節：收集日誌與指標，修正後再升級。
- 所需資源：觀測與日誌
- 預估時間：依問題

關鍵程式碼/設定：
```text
UI: Service -> Rollback
# 平台動作：
# - Stop/Remove 新容器
# - Start 舊容器（回復到升級前快照）
```

實際案例：作者說明升級失敗可以 Rollback，一鍵恢復。

實作環境：Rancher

實測數據：
改善前：人工回退時間長、風險高
改善後：一鍵回退、數分鐘內恢復
改善幅度：MTTR 降低

Learning Points（學習要點）
核心知識點：
- 回退機制與不可變部署
- 事故回復流程
- 版本管理

技能要求：
必備技能：平台操作、觀測分析
進階技能：變更審核與回退自動化

延伸思考：
- 如何在升級前建立自動回退保護閘？
- 回退後資料一致性問題？
- 與變更凍結政策的搭配？

Practice Exercise（練習題）
基礎練習：模擬升級失敗並回退（30 分鐘）
進階練習：設計回退觸發條件（2 小時）
專案練習：回退演練手冊與演練報告（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可快速回復服務
程式碼品質（30%）：文件與步驟清晰
效能優化（20%）：回復時間短
創新性（10%）：自動化保護與驗證


## Case #15: 升級成功後的資源回收—Finish Upgrade

### Problem Statement（問題陳述）
業務場景：升級完成後，舊容器仍佔用資源；需明確標記升級完成並回收舊資源，保持環境整潔與成本可控。

技術挑戰：升級後狀態管理與資源清理。

影響範圍：資源利用率、成本、可觀測性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 升級完成，但舊容器仍停放於平台。
2. 未清理影響資源與畫面清晰度。
3. 手動清理易漏。

深層原因：
- 架構層面：升級狀態機設計。
- 技術層面：容器與資源回收策略。
- 流程層面：缺乏完成升級的明確手續。

### Solution Design（解決方案設計）
解決策略：點擊 Finish Upgrade，讓平台自動移除舊容器與關聯資源，狀態回復為 Active。

實施步驟：
1. 完成確認
- 實作細節：測試通過後點擊 Finish Upgrade。
- 所需資源：UI
- 預估時間：5 分鐘

2. 驗證清理
- 實作細節：確認舊容器變為 Removed（或消失）。
- 所需資源：UI
- 預估時間：5 分鐘

關鍵程式碼/設定：
```text
UI: Service -> Finish Upgrade
# 平台動作：Remove 舊容器與相關資源，狀態 Active
```

實際案例：作者示範狀態由 Upgraded -> Finishing Upgrade -> Active，舊容器變 Removed。

實作環境：Rancher

實測數據：
改善前：舊資源佔用、畫面混亂
改善後：自動清理、狀態清晰
改善幅度：資源回收明顯、可視性提升

Learning Points（學習要點）
核心知識點：
- 升級狀態機
- 資源回收策略
- 環境整潔度

技能要求：
必備技能：平台操作
進階技能：資源監控與成本分析

延伸思考：
- 是否保留部分舊版本以快速回退？
- 清理策略與保留策略的取捨？
- 自動化驗收與 Finish 流程？

Practice Exercise（練習題）
基礎練習：完成一次升級並 Finish（30 分鐘）
進階練習：設計清理前的驗收清單（2 小時）
專案練習：自動化 Finish 與清理報告（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：舊容器正確清理
程式碼品質（30%）：操作與文件清晰
效能優化（20%）：資源釋放
創新性（10%）：自動化驗收機制


## Case #16: 主機與容器資源監控導入（CPU/RAM/DISK 可視化）

### Problem Statement（問題陳述）
業務場景：需要即時掌握主機與容器資源使用，作為擴縮與除錯依據；先前工具缺乏儀表板，難以決策。

技術挑戰：在不額外部署監控堆疊的前提下，快速取得基本可觀測性。

影響範圍：容量規劃、故障診斷、成本。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏 CPU/RAM/DISK 可視化面板。
2. 擴縮決策無數據支撐。
3. 故障診斷耗時。

深層原因：
- 架構層面：平台未提供觀測性則需另建堆疊。
- 技術層面：節點代理與統計上報。
- 流程層面：監控與維運脫節。

### Solution Design（解決方案設計）
解決策略：使用 Rancher 內建主機/容器監控視圖，於 Hosts 與 Containers 頁面直接查看，作為第一層觀測；必要時再擴充專業監控。

實施步驟：
1. 註冊節點
- 實作細節：確保 Agent 正常上報。
- 所需資源：Case #6 流程
- 預估時間：依節點數

2. 觀測與基準
- 實作細節：建立容量基準與告警門檻。
- 所需資源：監控策略文檔
- 預估時間：2 小時

關鍵程式碼/設定：
```text
UI 路徑：
- Infrastructure -> Hosts -> <Host> -> Stats
- Stacks -> <Service> -> <Container> -> Stats
# 作為第一層監控視圖
```

實際案例：作者指出 Rancher 提供主機與容器資源使用情形，一目了然。

實作環境：Rancher UI、已註冊節點

實測數據：
改善前：無內建監控面板
改善後：可見主機與容器資源使用
改善幅度：觀測性由無到有

Learning Points（學習要點）
核心知識點：
- 內建監控視圖用途與限制
- 容量基線與告警
- 觀測驅動擴縮

技能要求：
必備技能：平台操作
進階技能：監控策略設計

延伸思考：
- 何時需要導入完整監控堆疊（Prometheus/Grafana）？
- 如何結合日誌/追蹤形成可觀測性三支柱？
- 告警疲勞如何避免？

Practice Exercise（練習題）
基礎練習：查看主機與容器 Stats 並截圖（30 分鐘）
進階練習：定義三個容量告警門檻（2 小時）
專案練習：基於監控制定擴縮策略草案（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能取得基本監控數據
程式碼品質（30%）：監控策略文件完整
效能優化（20%）：依據監控做決策
創新性（10%）：監控整合構想


## Case #17: 預設分散佈署帶來的高可用—主機選擇的實務

### Problem Statement（問題陳述）
業務場景：擴展服務後，希望實例分散至不同 Host 提升可用性，但手動指定主機較繁；需理解並運用平台預設分散策略。

技術挑戰：確保副本分散而不需逐一指定主機。

影響範圍：可用性、擴展效率。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用者不確定如何手動挑主機。
2. 需要快捷達成跨主機分散。
3. 減少人為干預。

深層原因：
- 架構層面：平台預設排程為分散可用性。
- 技術層面：副本與主機可用度模型。
- 流程層面：避免過度指定造成耦合。

### Solution Design（解決方案設計）
解決策略：依賴 Rancher 預設的分散排程（spread），確保相同服務的副本盡可能分布於不同主機；先確保叢集擁有足夠主機數。

實施步驟：
1. 檢查主機數
- 實作細節：保證多於 1 台主機可用。
- 所需資源：節點
- 預估時間：10 分鐘

2. 驗證分散
- 實作細節：擴到多副本後確認分布情形。
- 所需資源：UI
- 預估時間：10 分鐘

關鍵程式碼/設定：
```text
# 無需額外配置；平台預設嘗試分散副本至不同主機
# 驗證路徑：Service -> Containers -> 查看每個實例所在 Host
```

實際案例：作者擴展服務後，實例自動分布至不同主機，提高容錯。

實作環境：Rancher、多主機

實測數據：
改善前：副本可能集中單一主機（風險）
改善後：預設分散至不同主機
改善幅度：可用性提高

Learning Points（學習要點）
核心知識點：
- 預設分散排程的作用
- 主機數量與可用性關係
- 避免過度手動指定

技能要求：
必備技能：平台觀測與驗證
進階技能：排程策略理解

延伸思考：
- 何時需要自訂排程規則（如親和/反親和）？
- 區域/機架容錯如何設計？
- 與 LB 結合的影響？

Practice Exercise（練習題）
基礎練習：擴展服務並確認跨主機分布（30 分鐘）
進階練習：嘗試在單主機情境觀察風險（2 小時）
專案練習：撰寫分散策略與驗證清單（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：副本分散達成
程式碼品質（30%）：驗證步驟清晰
效能優化（20%）：分散帶來的可用性提升
創新性（10%）：容錯設計


## Case #18: 沒有內建 Staging Slot 的替代方案—多 Environment/Stack + LB 切換

### Problem Statement（問題陳述）
業務場景：Azure Cloud Service 有 Production/Staging Slot 可先測再切換；Rancher 沒有同等內建 Slot，需自行設計可先測後切換的流程，避免直上造成風險。

技術挑戰：在無 Slot 機制下實作近似藍綠切換。

影響範圍：部署風險、可用性、驗收流程。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Rancher 無內建 Slot 切換。
2. 升級前缺少可驗證的「影子」環境。
3. 無快速切換機制增加風險。

深層原因：
- 架構層面：平台定位不同。
- 技術層面：需以多環境/多 Stack 與 LB 規則模擬。
- 流程層面：驗收與切換 SOP 需自訂。

### Solution Design（解決方案設計）
解決策略：用多 Environment（或同環境內兩個 Stack：blue/green）各自部署版本；以 LB 調整目標或 DNS 切換達成零中斷切換；不滿意再切回。

實施步驟：
1. 建立 blue/green
- 實作細節：部署兩套相同 Stack（不同版本）。
- 所需資源：節點資源
- 預估時間：1–2 小時

2. LB 切換
- 實作細節：LB Target 改指向 green；驗收通過後移除 blue。
- 所需資源：LB 設定
- 預估時間：30 分鐘

關鍵程式碼/設定：
```yaml
# 兩個 Stack：app-blue / app-green（示意）
# LB Target 初始指向 app-blue，驗收後切到 app-green
# UI：LB -> Targets -> 切換目標服務
```

實際案例：作者指出 Rancher 沒有內建 Staging Slot，提出可用多 Environment/Stack + LB 方式替代。

實作環境：Rancher、多 Stack、LB

實測數據：
改善前：無法先驗收再切換
改善後：可在平行環境中驗收並快速切換
改善幅度：部署風險降低

Learning Points（學習要點）
核心知識點：
- 藍綠部署與切換
- 多環境/多 Stack 運用
- LB 目標切換策略

技能要求：
必備技能：LB 與 Stack 操作
進階技能：DNS/流量分配與回退

延伸思考：
- 如何自動化驗收與切換按鈕？
- 資料層如何共同存取與遷移？
- 複雜依賴的切換順序？

Practice Exercise（練習題）
基礎練習：建立 blue/green 兩個 Stack（30 分鐘）
進階練習：以 LB 切換並驗證（2 小時）
專案練習：撰寫藍綠切換 SOP 與自動化腳本（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可切換且不中斷
程式碼品質（30%）：配置與腳本清晰
效能優化（20%）：切換延遲與錯誤控制
創新性（10%）：自動化與驗收設計


--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #2, #3, #4, #6, #9, #10, #16, #17
- 中級（需要一定基礎）
  - Case #1, #5, #7, #11, #12, #15, #18
- 高級（需要深厚經驗）
  - Case #8, #13, #14

2. 按技術領域分類
- 架構設計類
  - Case #1, #5, #8, #18
- 效能優化類
  - Case #3, #10, #16, #17
- 整合開發類
  - Case #2, #6, #7, #9, #11, #12, #15
- 除錯診斷類
  - Case #3, #13, #14, #16
- 安全防護類
  - Case #4, #7（憑證）、#11（入口治理）

3. 按學習目標分類
- 概念理解型
  - Case #1, #5, #8, #16
- 技能練習型
  - Case #2, #6, #9, #10, #11, #12, #15, #17
- 問題解決型
  - Case #3, #4, #7, #13, #14, #18
- 創新應用型
  - Case #11, #12, #18

--------------------------------
案例關聯圖（學習路徑建議）

- 建議先學：
  - Case #2（RancherOS + Server 安裝）→ Case #4（安全基線）→ Case #5（多環境）→ Case #6（本地節點納管）
  - 同步進行 Case #3（資源與啟動 SOP）建立穩定基礎

- 之間的依賴關係：
  - Case #7（Azure 節點）依賴 Case #5（多環境）與 Case #4（安全）
  - Case #9（部署）依賴 Case #6（節點可用）
  - Case #10（擴展）與 Case #11（LB）依賴 Case #9（已部署）
  - Case #12（跨 Stack LB）依賴 Case #11（LB 基礎）
  - Case #13（升級）依賴 Case #9/10/11（服務已上線且有入口）
  - Case #14（回退）與 Case #15（清理）依賴 Case #13（升級流程）
  - Case #16（監控）貫穿所有案例，建議早期導入
  - Case #17（分散佈署）依賴 Case #10（多副本）
  - Case #18（藍綠切換）依賴 Case #5（多環境/Stack）與 Case #11（LB）

- 完整學習路徑建議：
  1) Case #2 → #4 → #5 → #6 →（可並行 #3/#16）
  2) #7（雲節點）→ #9（部署）→ #10（擴展）→ #11（LB）→ #12（跨 Stack）
  3) #17（分散驗證）→ #13（升級策略）→ #14（回退）→ #15（清理）
  4) 進階：#18（藍綠/替代 Slot）→ #8（異平台整合風險與策略）

此路徑由基礎平台搭建與安全治理開始，逐步進入部署、擴展、入口管理、升級/回退，再到藍綠與多雲整合的高階議題，完整覆蓋實戰所需能力。