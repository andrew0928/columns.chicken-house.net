---
layout: synthesis
title: "[實戰] 十分鐘搞定! 在 Azure 上面佈署 Docker Container! - Docker Cloud 託管服務體驗"
synthesis_type: solution
source_post: /2016/02/29/labs_docker_cloud_with_azure/
redirect_from:
  - /2016/02/29/labs_docker_cloud_with_azure/solution/
postid: 2016-02-29-labs_docker_cloud_with_azure
---
{% raw %}

以下內容依據原文逐段抽取並結構化，彙整為 18 個可教可練的實戰解決方案案例。每一案均包含問題、根因、方案、步驟、範例、學習要點與評估建議，供教學、專案演練與能力評估使用。

## Case #1: 快速佈建多個 Docker Host（Azure 節點自動化）

### Problem Statement（問題陳述）
- 業務場景：團隊需在短時間內建立多台具 Docker Engine 的 Linux 主機，支撐多服務或 HA 部署。主機可能分佈於 Azure、公有雲或自有機房，手動建立 VM、安裝與設定 Docker 導致交付延誤。
- 技術挑戰：跨雲與跨環境的一致化佈建、標準化 VM 規格與磁碟、避免人為誤差、維持 5–10 分鐘內完成節點準備。
- 影響範圍：專案交期、擴容速度、後續服務部署與運維複雜度。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 手動建立 VM 與安裝 Docker 步驟繁瑣，易出錯。
  2. 各雲供應商介面與 API 不一致，造成腳本難以泛用。
  3. 缺乏集中式節點生命週期管理（建立、銷毀、替換）。
- 深層原因：
  - 架構層面：缺少統一的節點管理層來抽象化 Provider 差異。
  - 技術層面：僅依賴單機 docker 指令與手動流程，無 IaC 化。
  - 流程層面：節點佈建未納入標準作業流程與審核。

### Solution Design（解決方案設計）
- 解決策略：採用 Docker Cloud Nodes 直接在 Azure 自動建立節點。透過事前與 Azure 完成認證（管理憑證 + 訂閱 ID），於 Docker Cloud 選定區域、機型與磁碟容量後發起建立，5–10 分鐘內可得可用節點，後續 Stacks/Services 直接指派部署。

- 實施步驟：
  1. 建立 Azure 認證連結
     - 實作細節：於 Docker Cloud 下載管理憑證，至 Azure 舊版 Portal 上傳「管理憑證」，回填 Subscription ID。
     - 所需資源：Docker Cloud 帳號、Azure 訂閱。
     - 預估時間：5–10 分鐘。
  2. 建立 Nodes
     - 實作細節：Docker Cloud > Nodes > Launch node，選 Microsoft Azure、區域、VM 規格（如 Basic A1）、Disk 大小（如 60GB），提交後等待。
     - 所需資源：Azure 訂閱配額與區域可用度。
     - 預估時間：5–10 分鐘。
  3. 驗證節點可用
     - 實作細節：觀察 Docker Cloud 節點狀態與 Azure Portal 的 VM/雲端服務是否建立成功。
     - 所需資源：Azure Portal 存取權。
     - 預估時間：3–5 分鐘。

- 關鍵程式碼/設定：
```text
// 無需程式碼，重點在 Docker Cloud 介面與 Azure Portal 設定。
// 可補充：建立完成後以 SSH 驗證 docker 版本與 daemon 狀態。
```

- 實際案例：文中於 Azure 建立 Basic A1 VM + 60GB HDD，節點在 5–10 分鐘內可用。
- 實作環境：Docker Cloud（Tutum 前身）、Azure（Classic/傳統 VM）。
- 實測數據：
  - 改善前：手動建 VM + 裝 Docker + 開防火牆（數十步，易出錯）。
  - 改善後：5–10 分鐘完成節點自動化建立。
  - 改善幅度：建立時間與風險大幅下降（質性改善）。

Learning Points（學習要點）
- 核心知識點：
  - Nodes 概念與跨雲抽象。
  - Azure 認證（管理憑證）串接流程。
  - 規格化 VM 與磁碟設定的重要性。
- 技能要求：
  - 必備技能：雲端 VM 基本知識、Docker 基本操作。
  - 進階技能：IaC 與多雲供應商 API/配額規劃。
- 延伸思考：
  - 方案可擴展至 AWS/自有機房節點管理。
  - 風險：憑證外洩、資源誤開造成費用。
  - 優化：以標籤/命名規則管理資源生命週期。

Practice Exercise（練習題）
- 基礎練習：在測試訂閱建立 1 個 Azure Node，並以 SSH 驗證 docker 版本。
- 進階練習：建立位於兩個不同區域的 2 個節點，測試可用性。
- 專案練習：撰寫節點建立與銷毀 SOP，含費用檢查清單與回收流程。

Assessment Criteria（評估標準）
- 功能完整性（40%）：節點建立成功且可部署容器。
- 程式碼品質（30%）：N/A（著重設定流程紀錄與可重複性）。
- 效能優化（20%）：建立時間控制在 10 分鐘內。
- 創新性（10%）：多雲節點策略與命名規則設計。


## Case #2: 導入既有 Linux 伺服器至 Docker Cloud 的衝突與處置

### Problem Statement（問題陳述）
- 業務場景：已有 Ubuntu + Docker VM，想直接納入 Docker Cloud 管理，避免重建資源。
- 技術挑戰：Docker Cloud Agent 會自帶 CS 版本 Docker Engine，與既有 Docker 衝突；且需自行設防火牆與 Agent 安裝。
- 影響範圍：服務中斷風險、導入時間拉長、節點一致性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 既有 VM 上已有 Docker Engine，Agent 安裝會停用/移除原引擎。
  2. 防火牆與通訊埠未按需求放行，Agent 無法回報。
  3. 環境差異（OS 版本、套件）造成 Agent 安裝不穩。
- 深層原因：
  - 架構層面：缺乏標準化節點映像檔與基線。
  - 技術層面：Agent 與既有引擎版本/配置不相容。
  - 流程層面：缺少導入前檢核與回滾計畫。

### Solution Design（解決方案設計）
- 解決策略：優先使用 Docker Cloud 直接建立新節點。若必須導入既有主機，先卸載舊引擎、設定防火牆、再乾淨安裝 Agent，驗證後再遷移工作負載。

- 實施步驟：
  1. 風險評估與備援
     - 實作細節：備份資料卷與 Compose 檔，評估可容忍維護窗。
     - 所需資源：備份空間、維運窗口。
     - 預估時間：30–60 分鐘。
  2. 清理既有 Docker
     - 實作細節：停用容器、移除舊 Docker Engine 套件。
     - 所需資源：SSH 權限、套件管理工具。
     - 預估時間：15–30 分鐘。
  3. 安裝 Docker Cloud Agent 並放行防火牆
     - 實作細節：依官方腳本安裝，開放必要通訊（Outbound 至 Docker Cloud）。
     - 所需資源：網路與防火牆規則調整權限。
     - 預估時間：15–30 分鐘。

- 關鍵程式碼/設定：
```bash
# 停用容器並移除既有 Docker（範例，以 Debian/Ubuntu 為例）
sudo systemctl stop docker || true
sudo apt-get remove -y docker docker-engine docker.io || true

# UFW 放行常見必要通訊（示意）
sudo ufw allow 22/tcp
sudo ufw allow 2375/tcp
sudo ufw allow 2376/tcp
sudo ufw reload

# 安裝 Docker Cloud Agent（依官方文件版本為準，示意）
curl -Ls https://get.cloud.docker.com/agent.sh | sudo bash
```

- 實際案例：作者嘗試導入既有 VM，遇到 Agent/Engine 衝突，最終建議改由 Docker Cloud 建立新節點。
- 實作環境：Ubuntu（Azure 預建映像）、Docker Cloud Agent。
- 實測數據：
  - 改善前：導入既有主機流程繁瑣、風險高。
  - 改善後：改用 Docker Cloud 建節點，流程簡化且一致。
  - 改善幅度：導入時間與風險顯著降低（質性）。

Learning Points（學習要點）
- 核心知識點：Agent 與 Engine 相容性、節點基線管理。
- 技能要求：Linux 套件管理、防火牆設定、服務切換。
- 延伸思考：以 Golden Image/模板保證一致；導入自建機房需 NAT/防火牆策略。

Practice Exercise（練習題）
- 基礎練習：模擬在 VM 上移除舊 Engine 並安裝 Agent（測試環境）。
- 進階練習：撰寫導入檢核清單與回滾流程。
- 專案練習：設計既有主機轉換為受管節點的「無痛切換」方案。

Assessment Criteria（評估標準）
- 功能完整性（40%）：節點成功受管。
- 程式碼品質（30%）：腳本有防呆與日誌。
- 效能優化（20%）：切換時間控制在維護窗內。
- 創新性（10%）：導入零停機策略設計。


## Case #3: Docker Cloud 與 Azure 的認證打通（管理憑證 + 訂閱 ID）

### Problem Statement（問題陳述）
- 業務場景：需要讓 Docker Cloud 代表團隊在 Azure 建立 VM/Disk 等資源，以自動化節點建立與服務部署。
- 技術挑戰：無法在 Azure 進行代操作，節點建立卡關。
- 影響範圍：所有後續自動化流程（Nodes/Stacks/Services）無法啟動。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未建立 Docker Cloud 與 Azure 的信任關係。
  2. 未上傳管理憑證至 Azure 舊版 Portal。
  3. 未在 Docker Cloud 回填 Subscription ID。
- 深層原因：
  - 架構層面：需使用 Azure Classic（ASM）管理憑證模式。
  - 技術層面：認證材料與 Portal 位置不清楚。
  - 流程層面：未制定雲端憑證管理流程。

### Solution Design（解決方案設計）
- 解決策略：依流程在 Docker Cloud 下載管理憑證，於 Azure 舊版 Portal 上傳至「管理憑證」，回填 Subscription ID。完成後由 Docker Cloud 代為建立 Azure 資源。

- 實施步驟：
  1. 下載並上傳管理憑證
     - 實作細節：Docker Cloud > Azure > Add credentials > 下載 .cer；Azure 舊版 Portal > 設定 > 管理憑證 > 上傳。
     - 所需資源：Docker Cloud 帳號、Azure 舊版 Portal 存取。
     - 預估時間：5 分鐘。
  2. 回填 Subscription ID 並測試
     - 實作細節：將訂閱 ID 貼回 Docker Cloud 視窗，驗證看到綠色勾勾成功。
     - 所需資源：Azure 訂閱資訊。
     - 預估時間：2 分鐘。

- 關鍵程式碼/設定：
```text
// 主要透過 Portal 操作。
// 補充：在 Azure 入口網站「訂閱」頁可查 Subscription ID；或以 CLI 檢視（ARM）：
az account show --query "{name:name, id:id}"
```

- 實際案例：文中完成上傳後看到綠色勾勾，隨後得以自動建立 VM。
- 實作環境：Docker Cloud、Azure Classic（管理憑證）。
- 實測數據：
  - 改善前：Docker Cloud 無法下達建立資源操作。
  - 改善後：成功建立節點與 VM。
  - 改善幅度：流程開通（關鍵路徑打通）。

Learning Points（學習要點）
- 核心知識點：Azure Classic 管理憑證、訂閱 ID、第三方代操作。
- 技能要求：Portal 導航與權限設定。
- 延伸思考：現代化可改用 Service Principal；憑證輪替與最小權限。

Practice Exercise（練習題）
- 基礎練習：於沙箱訂閱完成憑證上傳與驗證。
- 進階練習：撰寫憑證管理標準作業規範（建立、輪替、撤銷）。
- 專案練習：將認證步驟整合入佈署管線（含審核）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：完成 Docker Cloud–Azure 認證。
- 程式碼品質（30%）：N/A（著重文件與腳本化取值）。
- 效能優化（20%）：流程完成時間 < 10 分鐘。
- 創新性（10%）：權限最小化與稽核設計。


## Case #4: 自動化資源建立的費用治理與風險控管

### Problem Statement（問題陳述）
- 業務場景：Docker Cloud 代表使用者在 Azure 建立 VM/Disk 等，若缺乏監控與預算控管，可能產生非預期費用。
- 技術挑戰：資源快速增長、跨團隊操作透明度不足、成本預測困難。
- 影響範圍：雲費用、預算控管、財務風險。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 自動化建立資源未同步審核。
  2. 缺少成本監控與預算警示。
  3. 資源未命名與標籤化，難以歸因。
- 深層原因：
  - 架構層面：缺成本/標籤治理設計。
  - 技術層面：未啟用費用 API/報表與警示。
  - 流程層面：未納入費用檢查與回收 SOP。

### Solution Design（解決方案設計）
- 解決策略：建立「操作即檢查」機制，於 Azure 入口網站即時檢視新增資源；啟用預算與警示；為資源加上命名規範與標籤，建立週期性回收流程。

- 實施步驟：
  1. 操作即時檢查
     - 實作細節：每次透過 Docker Cloud 建立節點/服務後，立刻回到 Azure Portal 檢視新增的 VM/Disk。
     - 所需資源：Azure Portal。
     - 預估時間：5 分鐘。
  2. 設定預算與警示
     - 實作細節：Azure Cost Management + Billing 設預算與警示門檻。
     - 所需資源：訂閱擁有者權限。
     - 預估時間：15 分鐘。
  3. 命名與標籤規範
     - 實作細節：以專案/環境（prod/stage/dev）/擁有者標籤標記。
     - 所需資源：治理標準。
     - 預估時間：30 分鐘。

- 關鍵程式碼/設定：
```bash
# 列出傳統（Classic）或 ARM 資源輔助檢查（ARM 示意）
az vm list -o table
az disk list -o table
az resource list --tag project=myblog -o table
```

- 實際案例：作者提醒「後續操作都可能產生 Azure 費用，務必回到 Azure 檢視」。
- 實作環境：Docker Cloud + Azure。
- 實測數據：N/A（質性），建立費用治理流程後，非預期資源留存風險下降。

Learning Points（學習要點）
- 核心知識點：雲費用治理、標籤策略、預算警示。
- 技能要求：Azure 成本管理、資源盤點。
- 延伸思考：自動化每日盤點報表、資源到期回收策略。

Practice Exercise（練習題）
- 基礎練習：為新建 VM 加上標籤並在 Portal 檢視。
- 進階練習：設定預算與超標警示（Email/Teams）。
- 專案練習：建立月度成本稽核 SOP 與報表。

Assessment Criteria（評估標準）
- 功能完整性（40%）：預算與警示生效。
- 程式碼品質（30%）：成本盤點腳本可重用。
- 效能優化（20%）：盤點腳本執行時間/覆蓋度。
- 創新性（10%）：自動回收機制設計。


## Case #5: 以 Docker Compose/Stack 一鍵部署 WordPress（Web + DB）

### Problem Statement（問題陳述）
- 業務場景：需快速在既有節點上部署 WordPress 與 MySQL，手動建立與連結容器耗時。
- 技術挑戰：多容器組合、連線設定、開放對外端口、重啟策略。
- 影響範圍：上線時間、維運一致性、可移植性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單機 docker 指令難以描述多容器拓撲。
  2. 連結/環境變數/端口配置缺乏中心化描述。
  3. 缺乏重啟與故障復原策略。
- 深層原因：
  - 架構層面：未以宣告式方式描述服務組合。
  - 技術層面：未引入 Compose/Stack。
  - 流程層面：缺少版本化 Stackfile 與審核。

### Solution Design（解決方案設計）
- 解決策略：以 Stackfile（Compose YAML）宣告 Web 與 DB；使用公有 Image；設定環境變數與端口映射；在 Docker Cloud 以「Save and Deploy」自動建置服務。

- 實施步驟：
  1. 撰寫 Stackfile
     - 實作細節：定義 mysql 與 wordpress 容器、鏈結、重啟策略。
     - 所需資源：Docker Hub 公開映像。
     - 預估時間：10–15 分鐘。
  2. 於 Docker Cloud 建立 Stack
     - 實作細節：Stacks > Create > 貼上 YAML > Save and Deploy。
     - 所需資源：可用節點。
     - 預估時間：3–5 分鐘（拉取映像視網速）。

- 關鍵程式碼/設定：
```yaml
# Stackfile（Compose v1 語法，對應文中）
db:
  image: mysql:latest
  environment:
    - MYSQL_ROOT_PASSWORD=YES   # 範例：請於實務改為安全強密碼
  restart: always

web:
  image: amontaigu/wordpress:latest
  links:
    - db:mysql
  ports:
    - "80:80"
  restart: always
```

- 實際案例：作者 Save and Deploy 後，3–5 分鐘內兩個服務轉為 Running。
- 實作環境：Docker Cloud、Azure Node。
- 實測數據：
  - 改善前：手動建立/連結容器耗時且易誤。
  - 改善後：3–5 分鐘完成部署，立即可見 WP 初始化畫面。
  - 改善幅度：部署效率大幅提升（質性）。

Learning Points（學習要點）
- 核心知識點：Compose 基本語法、links、ports、restart。
- 技能要求：Compose/Stack 基礎、Docker Hub 搜尋/選型。
- 延伸思考：改用 networks/depends_on、環境密碼安全管理、健康檢查。

Practice Exercise（練習題）
- 基礎練習：改寫 Stackfile 為固定版號映像。
- 進階練習：加入健康檢查與環境變數管理（.env）。
- 專案練習：將 Stackfile 納入版本控制與審核流程。

Assessment Criteria（評估標準）
- 功能完整性（40%）：WordPress 成功對外提供服務。
- 程式碼品質（30%）：YAML 結構清晰、參數注釋完整。
- 效能優化（20%）：映像拉取與啟動時間。
- 創新性（10%）：安全性強化（密碼、網段、健康檢查）。


## Case #6: Endpoint 與 DNS 整合：部署後的對外存取

### Problem Statement（問題陳述）
- 業務場景：服務部署成功但不知如何對外存取，且希望綁定自有網域而非臨時 IP。
- 技術挑戰：端點探索、DNS 綁定與簡化 DDNS 作業。
- 影響範圍：用戶可用性、上線速度、域名管理。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未知容器對外公開端點與 DNS 名稱。
  2. 舊有做法需自建 DDNS 與更新客戶端。
  3. 缺乏一站式端點清單。
- 深層原因：
  - 架構層面：端點管理未被視為部署的一部分。
  - 技術層面：DNS 綁定與 CNAME 未自動化。
  - 流程層面：未制定域名綁定 SOP。

### Solution Design（解決方案設計）
- 解決策略：使用 Docker Cloud Endpoints 取得服務 FQDN，立即可用；若需自有網域，在 DNS 設定 CNAME 指向該 FQDN，免維護 DDNS Client。

- 實施步驟：
  1. 查詢 Endpoints
     - 實作細節：Stacks > Endpoints 頁籤取得 FQDN。
     - 所需資源：Docker Cloud 介面。
     - 預估時間：1 分鐘。
  2. DNS 綁定（可選）
     - 實作細節：在自家 DNS 設 CNAME 指向 Docker Cloud FQDN。
     - 所需資源：DNS 管理權限。
     - 預估時間：5–10 分鐘（視生效時間）。

- 關鍵程式碼/設定：
```text
; DNS Zone（BIND 範例）
blog     CNAME   myblog-web.stackhash.dockercloud.com.
```

- 實際案例：作者透過 Endpoints 直接打開 URL，出現 WP 初始化畫面；表示 DNS/FQDN 工作即時生效。
- 実作環境：Docker Cloud、公共 DNS。
- 實測數據：N/A；綁定流程顯著簡化（免 DDNS 客戶端）。

Learning Points（學習要點）
- 核心知識點：服務端點、CNAME 綁定、FQDN 使用。
- 技能要求：DNS 基礎設定。
- 延伸思考：HTTPS/憑證、自動化 DNS（API/ExternalDNS）。

Practice Exercise（練習題）
- 基礎練習：為服務新增 CNAME 並驗證。
- 進階練習：為自有網域配置 Let’s Encrypt 憑證。
- 專案練習：以自動化工具更新 DNS（如 Terraform/CLI）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：FQDN 與自有域名皆可存取。
- 程式碼品質（30%）：DNS 設定文件與驗證步驟清楚。
- 效能優化（20%）：DNS 生效時間與快取策略。
- 創新性（10%）：自動化 DNS 與憑證布建。


## Case #7: 重新佈署（Redeploy）以套用不可變更參數變動

### Problem Statement（問題陳述）
- 業務場景：容器建立後，需修改 ports/volumes 等不可熱改參數；手動重建易遺漏。
- 技術挑戰：追蹤應變更之服務、避免整體中斷、保持資料安全。
- 影響範圍：服務可用性、部署正確性、資料完整性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 容器的部分參數不可在運行中修改。
  2. 缺少變更追蹤與顯示。
  3. 手動重建步驟繁雜。
- 深層原因：
  - 架構層面：未將 Redeploy 納入標準流程。
  - 技術層面：忽略 Compose/Stack 的宣告式驅動。
  - 流程層面：無分段/部分重佈署策略。

### Solution Design（解決方案設計）
- 解決策略：以 Stackfile 作為單一事實來源；變更後由 Docker Cloud 自動偵測需 Redeploy 的服務（顯示驚嘆號），使用「Redeploy」按鍵僅針對影響服務重建，確保有計畫地中斷或零停機滾動。

- 實施步驟：
  1. 編輯 Stackfile
     - 實作細節：Stacks > Edit > 修改參數 > Save。
     - 所需資源：Stack 管理權限。
     - 預估時間：5–10 分鐘。
  2. 選擇 Redeploy 範圍
     - 實作細節：可對整個 Stack 或特定 Service 執行。
     - 所需資源：變更影響評估。
     - 預估時間：3–5 分鐘。

- 關鍵程式碼/設定：
```yaml
# 範例：新增 Volume 後需 Redeploy
db:
  image: mysql:8.0
  environment:
    - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
  volumes:
    - dbdata:/var/lib/mysql
  restart: always

volumes:
  dbdata: {}
```

- 實際案例：作者修改 Stackfile 後，UI 顯示驚嘆號提示需 Redeploy。
- 實作環境：Docker Cloud Stack。
- 實測數據：N/A；正確性與一致性提升。

Learning Points（學習要點）
- 核心知識點：不可變參數、宣告式變更、部分重佈署。
- 技能要求：Compose/Stack 管理、影響評估。
- 延伸思考：結合 HA 進行滾動更新，降低停機。

Practice Exercise（練習題）
- 基礎練習：新增 Volume 並對單一服務 Redeploy。
- 進階練習：設計雙節點下的滾動 Redeploy。
- 專案練習：建立變更審核與自動 Redeploy 流程。

Assessment Criteria（評估標準）
- 功能完整性（40%）：變更成功且服務恢復。
- 程式碼品質（30%）：YAML 與變更紀錄清晰。
- 效能優化（20%）：Redeploy 時間與影響降至最低。
- 創新性（10%）：零停機策略。


## Case #8: 擴充副本數與固定 Port 衝突

### Problem Statement（問題陳述）
- 業務場景：想將 Web 服務擴充至多個容器以提高可用性，但每個容器都要求 Host 的 80 port，導致同節點無法並存。
- 技術挑戰：端口資源競爭、單節點限制、擴容失敗。
- 影響範圍：高可用性、擴容能力、服務穩定性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. ports 採用固定映射 "80:80"。
  2. 僅有一個節點，無法在不同 Host 分散。
  3. 無前端代理協調流量。
- 深層原因：
  - 架構層面：未設計前端反向代理/負載平衡。
  - 技術層面：未採用動態 Host Port 或多節點。
  - 流程層面：擴容策略與網路設計未同步。

### Solution Design（解決方案設計）
- 解決策略：改用動態 Port 映射（隨機 Host Port），或先擴增第二個 Node；在前方新增 Reverse Proxy/Nginx，集中接收 80/443 並反向轉發至各副本，解決衝突與完成負載分散。

- 實施步驟：
  1. 改用動態 Port 映射
     - 實作細節：將 "80:80" 改為 "80" 讓 Host 動態分配；或於 Docker Cloud UI 啟用動態。
     - 所需資源：Compose 修改權限。
     - 預估時間：5 分鐘。
  2. 新增 Reverse Proxy
     - 實作細節：部署 Nginx/Traefik 接聽 80/443，使用服務發現/靜態 upstream。
     - 所需資源：額外容器與設定。
     - 預估時間：30–60 分鐘。
  3. 擴增 Node
     - 實作細節：新增第二個 Node，將副本分散至不同 Host。
     - 所需資源：雲資源與費用。
     - 預估時間：10 分鐘。

- 關鍵程式碼/設定：
```yaml
# 動態 Port 映射（Compose v1）
web:
  image: amontaigu/wordpress:latest
  links:
    - db:mysql
  ports:
    - "80"  # 隨機 Host Port
  restart: always
```

- 實際案例：作者嘗試擴副本時遇固定 80 port 限制，系統提示需第二個 Node 或改動態映射。
- 實作環境：Docker Cloud。
- 實測數據：N/A；擴容策略從單節點受限轉為可多副本運作。

Learning Points（學習要點）
- 核心知識點：端口映射模型、動態 Port、前端代理。
- 技能要求：Compose ports、Nginx/Traefik 基礎。
- 延伸思考：Service Mesh、L4/L7 負載均衡。

Practice Exercise（練習題）
- 基礎練習：將固定 Port 改為動態，驗證 Endpoints。
- 進階練習：導入 Nginx 並反向到多個動態後端。
- 專案練習：雙節點部署，實現多副本與滾動更新。

Assessment Criteria（評估標準）
- 功能完整性（40%）：多副本可服務。
- 程式碼品質（30%）：Compose 與 Nginx 配置清晰。
- 效能優化（20%）：連線分散與延遲。
- 創新性（10%）：自動服務發現整合。


## Case #9: Reverse Proxy 模式整合多服務（Nginx）

### Problem Statement（問題陳述）
- 業務場景：多個服務都需對外以 80/443 提供存取（Blog、GitLab、Redmine 等），需同時共存並易於路由與快取。
- 技術挑戰：單一 Port 資源共享、舊新系統轉址、快取與靜態發佈。
- 影響範圍：用戶體驗、架構彈性、可維護性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 多服務都需要 80/443。
  2. 無集中入口與路由規則。
  3. 無快取與靜態資源優化。
- 深層原因：
  - 架構層面：缺少邊界層（Reverse Proxy）。
  - 技術層面：未實作路由/快取/SSL 終結。
  - 流程層面：缺少統一網域與子路徑規劃。

### Solution Design（解決方案設計）
- 解決策略：獨立部署 Nginx Reverse Proxy 於專屬 Stack 作為前端入口，實施路由（Host/Path Based）、快取與 SSL 終結；後端服務可採動態 Port 與多副本。

- 實施步驟：
  1. 部署 Reverse Proxy Stack
     - 實作細節：Nginx 掛載自定義配置與憑證。
     - 所需資源：Nginx 映像、憑證（選）。
     - 預估時間：30–60 分鐘。
  2. 路由規則與後端清單
     - 實作細節：以 server_name/Location 對應各服務。
     - 所需資源：各服務 Endpoints。
     - 預估時間：30 分鐘。

- 關鍵程式碼/設定：
```nginx
# /etc/nginx/conf.d/apps.conf（示意）
server {
  listen 80;
  server_name blog.example.com;
  location / {
    proxy_pass http://blog_upstream;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
  }
}

upstream blog_upstream {
  server web1:8080;
  server web2:8081;
}
```

- 實際案例：作者將 proxy 獨立為第二個 Stack，其他應用共用 80 port。
- 實作環境：Docker Cloud + Nginx。
- 實測數據：N/A；成功整合多服務入口。

Learning Points（學習要點）
- 核心知識點：反向代理、Host/Path 路由、上游池化。
- 技能要求：Nginx 配置、容器網路與 DNS。
- 延伸思考：Let's Encrypt 自動憑證、HTTP/2、Traefik/Ingress Controller。

Practice Exercise（練習題）
- 基礎練習：為 Blog 配置反向代理並通過。
- 進階練習：加入第二服務並以子路徑路由。
- 專案練習：導入 HTTPS 與自動憑證更新。

Assessment Criteria（評估標準）
- 功能完整性（40%）：多服務路由正常。
- 程式碼品質（30%）：Nginx 配置結構化與註解。
- 效能優化（20%）：快取命中與延遲。
- 創新性（10%）：自動化憑證與動態後端發現。


## Case #10: 高可用與滾動更新（多節點 + 多副本）

### Problem Statement（問題陳述）
- 業務場景：希望在維護/故障時不中斷服務，並能於尖峰擴容。
- 技術挑戰：多節點調度、副本分散、滾動替換策略。
- 影響範圍：SLA、用戶體驗、營運風險。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單副本/單節點無容錯。
  2. 無滾動更新程序，Redeploy 可能中斷。
  3. 無跨節點資源調度。
- 深層原因：
  - 架構層面：缺少叢集與調度（Swarm/Orchestrator）。
  - 技術層面：未實作副本、健康檢查、反向代理。
  - 流程層面：未建立維護窗口與滾動策略。

### Solution Design（解決方案設計）
- 解決策略：建立 2 個以上節點；Web 服務至少 2 副本分散節點；前端代理做負載分散；Redeploy 採一台一台替換，達成零停機更新與節點故障容忍。

- 實施步驟：
  1. 擴節點與副本
     - 實作細節：Nodes >= 2；Web 副本數 >= 2 並分散。
     - 所需資源：雲資源。
     - 預估時間：15–30 分鐘。
  2. 加入健康檢查
     - 實作細節：設定 healthcheck 與存活探針，代理僅轉送健康後端。
     - 所需資源：Compose/代理配置。
     - 預估時間：30 分鐘。
  3. 滾動更新
     - 實作細節：Redeploy 時逐一替換副本。
     - 所需資源：操作 SOP。
     - 預估時間：依映像拉取時間。

- 關鍵程式碼/設定：
```yaml
# Compose v2+（示意，可在 Swarm 或具備調度功能的環境）
services:
  web:
    image: amontaigu/wordpress:5.9
    deploy:
      replicas: 2
      update_config:
        order: start-first
        parallelism: 1
```

- 實際案例：作者建議「一次 Redeploy 一個副本」，確保不中斷。
- 實作環境：Docker Cloud 多節點。
- 實測數據：N/A；中斷時間可降至 0（策略達成）。

Learning Points（學習要點）
- 核心知識點：HA、滾動更新、副本調度。
- 技能要求：副本/節點規劃、代理健康檢查。
- 延伸思考：自動擴縮容（HPA）、跨區域容錯。

Practice Exercise（練習題）
- 基礎練習：將副本數調為 2，測試單副本維護不中斷。
- 進階練習：新增健康檢查與代理後端剔除。
- 專案練習：完整 HA 部署與滾動更新 Runbook。

Assessment Criteria（評估標準）
- 功能完整性（40%）：單節點失效服務不斷。
- 程式碼品質（30%）：部署文件與配置清楚。
- 效能優化（20%）：更新期間延遲與錯誤率。
- 創新性（10%）：自動擴縮策略。


## Case #11: 資料持久化策略（DATA 容器/Volume）

### Problem Statement（問題陳述）
- 業務場景：WordPress 與 MySQL 若未做資料持久化，Redeploy/重建可能導致資料遺失。
- 技術挑戰：容器無狀態與有狀態分離、資料卷管理、備份與復原。
- 影響範圍：資料完整性、RPO/RTO、營運風險。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未配置 Volume/資料容器。
  2. Redeploy 會重建容器，資料丟失。
  3. 缺備份策略。
- 深層原因：
  - 架構層面：未規劃狀態層。
  - 技術層面：未落實 Volume 與備份工具。
  - 流程層面：無週期備份與演練。

### Solution Design（解決方案設計）
- 解決策略：採 DATA 容器/命名 Volume 承載 MySQL 與 WP 上傳目錄；將應用容器視為無狀態；建立定期備份工作與復原演練。

- 實施步驟：
  1. 定義 Volume
     - 實作細節：將 /var/lib/mysql、/var/www/html/wp-content 掛載至命名 Volume。
     - 所需資源：Compose 修改權限、備份空間。
     - 預估時間：15–30 分鐘。
  2. 備份/還原
     - 實作細節：mysqldump、檔案備份、排程與驗證還原。
     - 所需資源：備份工具與存放。
     - 預估時間：持續性作業。

- 關鍵程式碼/設定：
```yaml
version: "2"
services:
  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
    volumes:
      - dbdata:/var/lib/mysql
  web:
    image: wordpress:php8.1-apache
    depends_on: [db]
    volumes:
      - wpdata:/var/www/html/wp-content
volumes:
  dbdata: {}
  wpdata: {}
```

- 實際案例：作者曾提出 DATA 容器概念作為管理 Volumes（文章示例的 WP Stack 未配置，為改進點）。
- 實作環境：Docker Cloud + Compose。
- 實測數據：N/A；資料持久化風險大幅降低。

Learning Points（學習要點）
- 核心知識點：Volumes 與無狀態設計。
- 技能要求：備份/還原演練。
- 延伸思考：外接儲存（NFS/雲硬碟）、快照。

Practice Exercise（練習題）
- 基礎練習：為 MySQL 加入 Volume，重建驗證資料仍在。
- 進階練習：加入 WP 上傳目錄 Volume 與備份腳本。
- 專案練習：制定完整備份/還原/演練 SOP。

Assessment Criteria（評估標準）
- 功能完整性（40%）：重建後資料仍在。
- 程式碼品質（30%）：Volume 與備份腳本清楚。
- 效能優化（20%）：備份耗時與還原時間。
- 創新性（10%）：快照/增量備份設計。


## Case #12: 以職責劃分 Stack（Proxy 與 App 拆分）

### Problem Statement（問題陳述）
- 業務場景：多應用共用 80/443，將 Proxy 與 App 同置一 Stack 使變更牽連過大且不易維護。
- 技術挑戰：部署邊界、變更影響控制、共用資源治理。
- 影響範圍：維運效率、風險隔離、重用性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Proxy 與 App 綁在單一 Stack，耦合度高。
  2. 共用端口資源調配不靈活。
  3. 變更影響範圍大。
- 深層原因：
  - 架構層面：缺少職責邊界切分。
  - 技術層面：Stack 規劃不足。
  - 流程層面：變更管理未分層。

### Solution Design（解決方案設計）
- 解決策略：以 Proxy 為獨立 Stack，App 各自為 Stack。Proxy 專注接入、安全、緩存、路由；App Stack 專注業務本身，彼此獨立部署、擴縮容與 Redeploy。

- 實施步驟：
  1. 拆分 Stack
     - 實作細節：建立 proxy-stack 與 app-stack*。
     - 預估時間：30–60 分鐘。
  2. 明確依賴與接點
     - 實作細節：以 DNS/環境變數/服務名稱連接。
     - 預估時間：30 分鐘。

- 關鍵程式碼/設定：
```yaml
# proxy-stack.yml（示意）
services:
  proxy:
    image: nginx:alpine
    ports: ["80:80","443:443"]
    volumes: ["./nginx:/etc/nginx/conf.d"]
```

- 實際案例：作者實際運營中將 proxy 獨立成第二個 Stack（blog/gitlab/redmine 共用）。
- 實作環境：Docker Cloud。
- 實測數據：N/A；維運邊界清晰、改動風險降低。

Learning Points（學習要點）
- 核心知識點：職責分離、邊界設計。
- 技能要求：Stack 規劃、路由配置。
- 延伸思考：跨 Stack 的健康監控與告警。

Practice Exercise（練習題）
- 基礎練習：將現有單一 Stack 拆分為 Proxy 與 App。
- 進階練習：多 App 共享 Proxy 並測試隔離。
- 專案練習：建立跨 Stack 版本/變更管理流程。

Assessment Criteria（評估標準）
- 功能完整性（40%）：拆分後服務正常。
- 程式碼品質（30%）：配置與文件清晰。
- 效能優化（20%）：變更影響與回滾時間。
- 創新性（10%）：拆分策略通用性。


## Case #13: 以公有 Registry 快速選型與建立服務

### Problem Statement（問題陳述）
- 業務場景：想快速找到合適的容器映像（如 WordPress），並以最小設定上線。
- 技術挑戰：映像選型、版本管理、基本參數輸入。
- 影響範圍：開發上線速度、映像品質。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 不熟悉映像來源與品質。
  2. 手動查找映像與文件耗時。
  3. 缺少一站式建立流程。
- 深層原因：
  - 架構層面：映像治理不足（來源、信任）。
  - 技術層面：缺少 Catalog 與搜尋整合。
  - 流程層面：映像選用標準未建立。

### Solution Design（解決方案設計）
- 解決策略：使用 Docker Cloud Services > Create service，輸入關鍵字（例如 wordpress）搜尋 Docker Hub 映像，點選後僅補齊必要參數即可部署。

- 實施步驟：
  1. 搜尋映像
     - 實作細節：輸入關鍵字、評估官方/社群映像。
     - 預估時間：5–10 分鐘。
  2. 補充設定
     - 實作細節：環境變數、端口、持久化等。
     - 預估時間：10–15 分鐘。

- 關鍵程式碼/設定：
```text
// 以 UI 建立為主。補充：選用官方映像（library/wordpress、mysql）更可靠。
```

- 實際案例：作者以關鍵字搜尋列出可用映像，快速建立服務。
- 實作環境：Docker Cloud + Docker Hub。
- 實測數據：N/A；建立時間由手動查找降至數分鐘。

Learning Points（學習要點）
- 核心知識點：映像選型、信任來源、最小可行配置。
- 技能要求：Docker Hub 使用。
- 延伸思考：私有 Registry 與掃描策略。

Practice Exercise（練習題）
- 基礎練習：以 UI 搜尋並部署一個示例服務。
- 進階練習：比較兩個映像的差異（大小、標籤、維護）。
- 專案練習：建立團隊映像選型準則文件。

Assessment Criteria（評估標準）
- 功能完整性（40%）：服務可運行。
- 程式碼品質（30%）：配置文件與紀錄。
- 效能優化（20%）：映像拉取速度與精簡。
- 創新性（10%）：映像信任與掃描策略。


## Case #14: 可觀測性與稽核：Nodes/Containers/Endpoints/Timeline

### Problem Statement（問題陳述）
- 業務場景：需清楚知道有哪些容器在跑、對外端點是什麼、歷史操作紀錄如何，以利除錯與稽核。
- 技術挑戰：資源分散、缺乏單一視圖、操作追蹤困難。
- 影響範圍：問題診斷、責任歸屬、合規稽核。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 無集中清單顯示當前運行資源。
  2. 缺少端點匯總頁。
  3. 缺乏操作時間線。
- 深層原因：
  - 架構層面：監控/稽核設計不足。
  - 技術層面：未啟用平台內建觀測功能。
  - 流程層面：缺少定期檢視流程。

### Solution Design（解決方案設計）
- 解決策略：使用 Docker Cloud 的 Nodes 檢視容器清單、Endpoints 統一端點、Timeline 頁檢視歷史操作；將該流程納入例行維運檢查。

- 實施步驟：
  1. 定期盤點
     - 實作細節：每週檢視 Nodes/Services/Endpoints。
  2. 稽核操作
     - 實作細節：Timeline 查異常/變更來源，配合變更管理。

- 關鍵程式碼/設定：
```text
// 以 UI 為主。可補充整合外部日誌/告警系統。
```

- 實際案例：作者展示 Nodes 上的容器總表、Endpoints、Timeline。
- 實作環境：Docker Cloud。
- 實測數據：N/A；除錯耗時降低（質性）。

Learning Points（學習要點）
- 核心知識點：資源盤點、端點治理、操作稽核。
- 技能要求：平台觀測功能運用。
- 延伸思考：集中化日誌、監控與告警整合。

Practice Exercise（練習題）
- 基礎練習：導出當前容器與端點清單。
- 進階練習：建立每週稽核報告模板。
- 專案練習：串接外部告警（Email/ChatOps）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能提供完整清單與時間線。
- 程式碼品質（30%）：報告模板與指標定義。
- 效能優化（20%）：除錯時間縮短。
- 創新性（10%）：觀測與告警自動化。


## Case #15: Azure 傳統/新入口混淆下的資源定位

### Problem Statement（問題陳述）
- 業務場景：建立的 VM 無法在新入口（ARM）找到，導致誤判資源遺失或建立失敗。
- 技術挑戰：Azure Classic（ASM）與 ARM 資源視圖差異。
- 影響範圍：資產可見性、除錯時間、運維決策。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 以管理憑證建立資源屬於 Classic 模式。
  2. 在新入口查詢不到「虛擬機器（傳統）」。
  3. 不熟悉兩種資源模型差異。
- 深層原因：
  - 架構層面：雙模型並存過渡期。
  - 技術層面：Portal 視圖與 API 差異。
  - 流程層面：缺少資源模型識別與指引。

### Solution Design（解決方案設計）
- 解決策略：於 Azure 新入口切換至「虛擬機器（傳統）」視圖，或改以 ARM/Service Principal 重建；建立資源標識與查找指引。

- 實施步驟：
  1. 確認資源模型
     - 實作細節：Docker Cloud + 管理憑證 => Classic VM。
  2. 建立查找指引
     - 實作細節：文件化 Classic/ARM 的查詢位置與差異。

- 關鍵程式碼/設定：
```text
// 以 Portal 操作為主。CLI 可輔助：az vm list（ARM），Classic 需相應工具或 Portal。
```

- 實際案例：作者於「虛擬機器（傳統）」找到所建 VM。
- 實作環境：Azure。
- 實測數據：N/A；定位時間縮短。

Learning Points（學習要點）
- 核心知識點：ASM vs ARM 模型。
- 技能要求：入口導航。
- 延伸思考：資源遷移策略到 ARM。

Practice Exercise（練習題）
- 基礎練習：在新入口找到傳統 VM 視圖。
- 進階練習：撰寫 Classic/ARM 對照表。
- 專案練習：規劃 Classic 到 ARM 遷移路線。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確定位資源。
- 程式碼品質（30%）：文件清楚。
- 效能優化（20%）：定位時間縮短。
- 創新性（10%）：遷移方案。


## Case #16: 異質環境的一致化：Machine/Compose/Swarm 與 Docker Cloud

### Problem Statement（問題陳述）
- 業務場景：同一套服務需在 Azure、AWS、VMware、On-Prem 部署；異質環境增加複雜度。
- 技術挑戰：工具鏈碎片化、操作不一致、學習成本高。
- 影響範圍：交付速度、可移植性、運維標準化。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 各 Provider API 與操作不同。
  2. 單用 docker CLI 難以應對大規模。
  3. 缺乏集中編排能力。
- 深層原因：
  - 架構層面：缺少抽象統一層。
  - 技術層面：未善用 Machine/Compose/Swarm 或託管平臺。
  - 流程層面：未建立跨環境 SOP。

### Solution Design（解決方案設計）
- 解決策略：以 Compose 描述應用拓撲，以 Machine/Swarm 提供節點建立與編排；或直接使用 Docker Cloud 做為託管管理層，跨供應商以一致流程部署。

- 實施步驟：
  1. 標準化 Compose
  2. 選擇編排與管理層（Swarm 或 Docker Cloud）
  3. 驗證跨環境部署流程

- 關鍵程式碼/設定：
```yaml
# 一份 Compose 跨環境複用
version: "2"
services:
  web:
    image: wordpress:latest
    environment: [...]
    ports: ["80:80"]
  db:
    image: mysql:8.0
    environment: [...]
```

- 實際案例：作者介紹 Machine/Compose/Swarm 的角色，並最終採 Docker Cloud 簡化管理。
- 實作環境：多雲/混合。
- 實測數據：N/A；操作一致性提升，學習成本下降。

Learning Points（學習要點）
- 核心知識點：Machine/Compose/Swarm 分工與替代方案。
- 技能要求：工具鏈整合。
- 延伸思考：抽象層選型（K8s/Swarm/託管）。

Practice Exercise（練習題）
- 基礎練習：以同一 Compose 在兩環境啟用。
- 進階練習：對比 Swarm 與 Docker Cloud 操作差異。
- 專案練習：制定跨環境 SOP 與工具清單。

Assessment Criteria（評估標準）
- 功能完整性（40%）：同一 Compose 跨環境可運行。
- 程式碼品質（30%）：配置一致性。
- 效能優化（20%）：部署時間。
- 創新性（10%）：抽象層最佳化。


## Case #17: 混合雲管理：將部落格遷移至自家 Mini-PC

### Problem Statement（問題陳述）
- 業務場景：將運行中的部落格從雲端遷至自家 Mini-PC，仍希望保有雲端等級的管理能力與 UI。
- 技術挑戰：On-Prem 節點納管、單節點限制（免費帳戶）、端點曝光。
- 影響範圍：成本、可用性、營運彈性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. On-Prem 網路/NAT 下的連線與曝光。
  2. 免費帳戶僅 1 節點限制。
  3. 多服務共享 80 需 Proxy。
- 深層原因：
  - 架構層面：混合雲架構設計。
  - 技術層面：Agent/端點/DNS 設定。
  - 流程層面：遷移計畫與風險控管。

### Solution Design（解決方案設計）
- 解決策略：將 Mini-PC 加入 Docker Cloud 作為 Node（或以免費單節點使用）；以既有 Stack 部署 Blog/DB/Proxy；用 Endpoints 或自有 DNS 暴露服務，快速完成遷移。

- 實施步驟：
  1. 納管 Mini-PC 節點
  2. 部署既有 Stack
  3. 設定 Proxy 與 DNS/Endpoints

- 關鍵程式碼/設定：
```text
// 重用既有 Stackfile。視 On-Prem 網路條件設定對外路由或端口轉發。
```

- 實際案例：作者一日內完成從研究到建立與遷移，並以免費單節點運轉多服務。
- 實作環境：Docker Cloud + 自有 Mini-PC。
- 實測數據：
  - 改善後：一天內完成導入與部署（文中描述）。
  - 成本：託管免費（1 節點），硬體自備。

Learning Points（學習要點）
- 核心知識點：混合雲場景、On-Prem 節點納管。
- 技能要求：網路/NAT/防火牆、DNS。
- 延伸思考：在家頻寬/電力/備援風險。

Practice Exercise（練習題）
- 基礎練習：將家用機加入為 Node（測試）。
- 進階練習：以 Proxy 整合多服務並公開。
- 專案練習：撰寫完整遷移 Runbook 與回退計畫。

Assessment Criteria（評估標準）
- 功能完整性（40%）：服務可於 On-Prem 穩定運行。
- 程式碼品質（30%）：部署文件與網路設計。
- 效能優化（20%）：端點可用性與延遲。
- 創新性（10%）：混合雲成本/可用性平衡。


## Case #18: 憑證與代理代操的安全治理

### Problem Statement（問題陳述）
- 業務場景：Docker Cloud 獲得代表使用者在 Azure 建立資源的權限，若憑證或 Agent 設定不當，存在安全與風險。
- 技術挑戰：憑證保護、最小權限、外部系統代操稽核。
- 影響範圍：資安、合規、雲資源濫用。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 憑證一旦外洩即可代為建立資源。
  2. 未設最小權限/網段限制。
  3. Agent 與對外端口未妥善限制。
- 深層原因：
  - 架構層面：缺少 Zero Trust 與權限切分。
  - 技術層面：未建立憑證輪替/加密存放。
  - 流程層面：缺乏存取稽核與通報流程。

### Solution Design（解決方案設計）
- 解決策略：建立憑證治理（最小權限、輪替、撤銷）、限制 Agent 通訊、啟用操作稽核；異常行為通報；成本與資安雙警示。

- 實施步驟：
  1. 憑證治理
     - 實作細節：安全存放、定期輪替、撤銷程序。
  2. 網路限制
     - 實作細節：限制出入站規則、只開必要端口。
  3. 稽核與告警
     - 實作細節：審視 Timeline，啟用告警與成本警示。

- 關鍵程式碼/設定：
```bash
# 範例：UFW 僅開必要端口與特定來源（示意）
sudo ufw default deny incoming
sudo ufw allow from <trusted-ip> to any port 22
sudo ufw allow 80,443/tcp
sudo ufw enable
```

- 實際案例：作者提醒 Docker Cloud 會代表你建立資源並產生費用，務必留意。
- 實作環境：Docker Cloud + Azure。
- 實測數據：N/A；風險顯著降低（治理建立）。

Learning Points（學習要點）
- 核心知識點：憑證治理、最小權限、稽核。
- 技能要求：網路安全與作業流程。
- 延伸思考：改用短期憑證、Just-in-time 權限。

Practice Exercise（練習題）
- 基礎練習：為節點設定最小入站規則。
- 進階練習：建立憑證輪替計畫與演練。
- 專案練習：將資安與成本告警整合至 ChatOps。

Assessment Criteria（評估標準）
- 功能完整性（40%）：安全策略落地。
- 程式碼品質（30%）：規則/文件完備。
- 效能優化（20%）：誤報/漏報控制。
- 創新性（10%）：JIT 權限/短期憑證。


--------------------------------
案例分類

1) 按難度分類
- 入門級：
  - Case #3（認證打通）
  - Case #5（Compose 部署 WP）
  - Case #6（Endpoints/DNS）
  - Case #12（Stack 拆分）
  - Case #13（Registry 選型）
  - Case #15（Azure 傳統/新入口）
- 中級：
  - Case #1（節點自動化）
  - Case #2（導入既有 Linux）
  - Case #4（費用治理）
  - Case #7（Redeploy 管理）
  - Case #8（端口衝突與擴容）
  - Case #11（資料持久化）
  - Case #14（可觀測性/稽核）
  - Case #17（混合雲遷移）
  - Case #18（安全治理）
- 高級：
  - Case #9（Reverse Proxy 整合）
  - Case #10（HA 與滾動更新）
  - Case #16（跨供應商一致化）

2) 按技術領域分類
- 架構設計類：
  - Case #9, #10, #11, #12, #16, #17
- 效能優化類：
  - Case #8, #10（間接）
- 整合開發類：
  - Case #1, #3, #5, #6, #13, #15
- 除錯診斷類：
  - Case #14, #15
- 安全防護類：
  - Case #4, #18

3) 按學習目標分類
- 概念理解型：
  - Case #5, #6, #12, #13, #15, #16
- 技能練習型：
  - Case #1, #3, #7, #8, #9, #11, #14
- 問題解決型：
  - Case #2, #4, #10, #18
- 創新應用型：
  - Case #9, #10, #16, #17

--------------------------------
案例關聯圖（學習路徑建議）

- 建議先學：
  1) Case #5（Compose/Stack 基礎，掌握多容器部署）
  2) Case #3（Docker Cloud 與 Azure 認證）
  3) Case #1（建立節點，具備部署基礎設施）
  4) Case #6（端點與 DNS 綁定，完成對外服務）

- 之後學（功能深化）：
  5) Case #7（Redeploy 與宣告式變更）
  6) Case #11（資料持久化）
  7) Case #12（Stack 職責拆分）
  8) Case #13（Registry 選型與快速建置）

- 進一步（可用性/擴展）：
  9) Case #8（端口衝突與動態映射）
  10) Case #9（Reverse Proxy 整合多服務）
  11) Case #10（HA 與滾動更新）

- 橫向治理（安全/成本/觀測）：
  12) Case #4（費用治理）
  13) Case #14（可觀測性與稽核）
  14) Case #18（安全治理）

- 異質與混合雲能力：
  15) Case #15（Classic vs ARM 定位）
  16) Case #16（跨供應商一致化）
  17) Case #2（導入既有 Linux 主機）
  18) Case #17（混合雲遷移至 On-Prem）

- 依賴關係摘要：
  - Case #5 依賴 Case #1/#3（需節點與認證）。
  - Case #7 依賴 Case #5（有 Stackfile）。
  - Case #8/#9/#10 依賴 Case #5/#7（有可運行服務再談擴容/HA）。
  - Case #11 依賴 Case #5（在服務中加入持久化）。
  - Case #12 依賴 Case #9（Proxy 能力）與 Case #5（App）。
  - Case #16 建立在 #1/#5 基礎上，向多雲抽象延伸。
  - Case #17 依賴 #2/#6/#9（On-Prem 納管、端點、代理）。

- 完整學習路徑建議：
  - 基礎建置（#3 → #1 → #5 → #6）
  - 變更與資料（#7 → #11 → #12 → #13）
  - 可用性與擴展（#8 → #9 → #10）
  - 治理與安全（#4 → #14 → #18）
  - 異質與混合（#15 → #16 → #2 → #17）

以上 18 個案例涵蓋從節點建立、堆疊部署、端點與 DNS、變更與持久化、擴容與 HA、成本與安全治理到混合雲遷移的完整實戰鏈條，可直接用於課程、專案實作與評核。
{% endraw %}