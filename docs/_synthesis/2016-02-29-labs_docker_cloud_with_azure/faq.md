---
layout: synthesis
title: "[實戰] 十分鐘搞定! 在 Azure 上面佈署 Docker Container! - Docker Cloud 託管服務體驗"
synthesis_type: faq
source_post: /2016/02/29/labs_docker_cloud_with_azure/
redirect_from:
  - /2016/02/29/labs_docker_cloud_with_azure/faq/
postid: 2016-02-29-labs_docker_cloud_with_azure
---

# [實戰] 十分鐘搞定! 在 Azure 上面佈署 Docker Container! - Docker Cloud 託管服務體驗

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Docker Cloud 託管服務？
- A簡: Docker 官方提供的容器託管平台，幫你管理節點、服務與佈署；主機仍由你在 Azure/AWS/自建環境提供。
- A詳: Docker Cloud 是 Docker 旗下的容器「託管」服務，重點在提供跨雲端與自建環境的一致管理介面與流程。它不替你提供實體或虛擬主機，而是連結你在 Azure、AWS 或自有資料中心的資源，協助一鍵佈署 Docker 節點（Nodes）、定義應用堆疊（Stacks）、管理服務（Services）、建立端點（Endpoints）與 DNS 名稱（FQDN），並整合 Docker Hub 的映像檔。藉此，你能以最小的指令與設定成本完成從環境佈建到應用上線的全流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q7, B-Q1

A-Q2: 託管（管理）與主機代管（Hosting）有何差異？
- A簡: 託管管的是「管理」，Hosting 管的是「運算資源」。前者不供應 VM，後者供應主機運算。
- A詳: Docker Cloud 的託管，指提供佈署、監控、擴展、DNS 與生命週期等「管理能力」，但不提供主機運算資源；你需自備或向雲端供應商租用 VM。主機代管（Hosting）則包含運算、儲存與網路資源本身。本文案例中，Azure 提供 VM/Disk/網路，Docker Cloud 以你的授權代表你在 Azure 建立與管理資源，並提供上層的容器佈署與服務治理能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q14

A-Q3: 什麼是 Docker Machine？
- A簡: 一套用同一組指令在不同雲/虛擬化平台建立 Docker Host 的工具。
- A詳: Docker Machine 讓你用一致的 CLI 指令在多種 IaaS 或虛擬化平台（Azure、AWS、VMware、Hyper‑V 等）建立安裝好 Docker Engine 的主機（Docker Host）。它抽象化了供應商差異，適合大量快速佈建主機。相較只在單機上安裝 Docker Engine，Machine 面向「多主機佈署」，是大規模容器基礎建設的第一步。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q2

A-Q4: 什麼是 Docker Compose？
- A簡: 用 YAML 宣告多容器服務組合與相依，讓一指令佈署整組服務。
- A詳: Docker Compose 以 YAML 檔（docker-compose.yml）描述一組服務所需容器、映像、環境變數、網路、儲存、相依與連線方式。對多容器應用（如 WordPress+MySQL+Proxy），以單一設定檔完成建置、啟動、停止、更新與移除，避免人工下多條 docker run 指令的繁瑣與錯誤，適合可移植、可重現的佈署。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q15, B-Q4

A-Q5: 什麼是 Docker Swarm？
- A簡: 將多台 Docker Host 組成叢集，提供容器排程、擴展與高可用。
- A詳: Docker Swarm 將多個 Docker 主機整合為單一邏輯叢集，提供資源排程、服務擴展、滾動更新、故障切換與跨主機網路。當服務需要更高可用性或自動擴縮，Swarm 可將多副本容器分散到不同節點，並處理資源（CPU/RAM/DISK）與網路的協調，減少單點故障風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q8, B-Q9

A-Q6: Machine、Compose、Swarm 的差異與分工？
- A簡: Machine 建主機、Compose 編排服務、Swarm 叢集調度與 HA，各司其職互補。
- A詳: Machine 面向「主機層」佈建，負責在各平台快速建立 Docker Host；Compose 面向「應用層」編排，將多容器服務用 YAML 宣告化；Swarm 面向「叢集層」治理，負責跨主機的資源排程、擴展與高可用。三者串起來，即從基礎到應用、從單機到叢集的一條龍流程。Docker Cloud 則把這些能力整合成單一圖形介面與 API。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q4, A-Q5, B-Q2

A-Q7: Docker Cloud 的 Node、Service、Stack 分別是什麼？
- A簡: Node 是主機、Service 是邏輯服務、Stack 是一組服務的整體（類 Compose）。
- A詳: Node 代表可被管理的 Docker Host（實體/虛擬機）。Service 是邏輯服務定義，可由一個或多個容器組成（如 web 服務兩副本）。Stack 是應用堆疊，對應一份（擴充的）Compose 檔，內含多個 Service 的組合與相依。透過 Stack 管 Service，再將 Service 調度到 Nodes 上執行，形成完整的佈署拓樸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q15, B-Q4

A-Q8: 什麼是 Endpoint 與 FQDN？為何重要？
- A簡: Endpoint 是對外服務入口，Docker Cloud 會給每服務一個可存取的 FQDN。
- A詳: 佈署完成後，對外存取需有固定入口。Docker Cloud 會為映射出來的服務埠建立 Endpoint，並整合 DNS 指派對應的 FQDN（完整網域名稱）。你可直接用該 FQDN 使用服務，或在自家 DNS 新增 CNAME 指向此 FQDN，讓自訂網域對外提供服務，省去自行架 DDNS 與動態 IP 更新的繁瑣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, C-Q5, B-Q6

A-Q9: 為什麼大規模管理不能只靠 docker engine 指令？
- A簡: 多主機、多服務、相依與擴展繁雜，單機指令無法高效一致地管理。
- A詳: 單用 docker run/stop 等指令，難以處理多容器相依、多主機佈署、滾動更新、DNS 與端點管理與故障切換等複雜場景。Compose 將設定宣告化、可重現；Swarm 提供叢集調度與 HA；Docker Cloud 以圖形化/自動化整合整套流程並接上雲供應商 API，顯著降低操作複雜度與風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, B-Q4

A-Q10: 為什麼要把 Docker Cloud 與 Azure 連結？會產生什麼費用？
- A簡: 讓 Docker Cloud 代你在 Azure 建/管 VM 等資源；Azure 會照用量計費。
- A詳: 連結後，Docker Cloud 以你的授權在 Azure 建立 VM、磁碟與相關網路資源，完成節點佈建與服務部署。好處是免去手動開 VM 與安裝 Agent/Engine。注意連結後的所有資源會依 Azure 計費（包含 VM、Disk、頻寬等），且 Docker Cloud 託管本身超過免費節點也會收費，需定期在 Azure 入口檢查與控管成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q14, D-Q7

A-Q11: 什麼是高可用性（HA）？文中的 WordPress 如何達成？
- A簡: HA 確保服務不中斷；以多節點多副本容器、負載分散與故障切換實現。
- A詳: HA 旨在面對節點故障或維護時維持服務連續。文中方法是讓 web 容器有多副本，分散在不同 Nodes；前端以 Reverse Proxy/負載平衡分流，當一台節點維護或失效，另一台接手。同時搭配滾動式重新佈署，逐台替換容器，避免整體停機。儲存面需確保資料持久化（DB/Volume）以防資料遺失。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q8, B-Q9, D-Q9

A-Q12: 什麼是 Reverse Proxy？在案例中扮演什麼角色？
- A簡: 位於前端轉發請求，處理轉址、Cache、負載平衡與多服務共用 80 埠。
- A詳: Reverse Proxy（如 NGINX）位於客戶端與後端服務之間，負責請求轉發、TLS 終結、快取、負載平衡與路由分派。文中 WordPress 與其他服務共用 80 埠，因此將 Proxy 獨立成一個服務，對外只開 80/443，再依路徑或主機名導向不同後端容器（含動態埠）。此設計也便於水平擴展與零停機更新。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q7, D-Q4

A-Q13: 什麼是資料 Volume/資料容器（DATA）？
- A簡: 將資料持久化到獨立 Volume/容器，與應用容器解耦，便於更新與備援。
- A詳: 容器本身是短暫的，重新佈署會重建檔層。將資料放在 Volume 或專責資料容器（DATA）可確保持久性，應用容器更新或替換不影響資料。文中 WordPress+MySQL 架構建議以 Volume/資料容器保存 DB 與上傳檔案，避免 redeploy 或擴展造成資料遺失，並利於備份與搬遷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q5, C-Q3

A-Q14: Service 與 Container 有何差異？
- A簡: Service 是邏輯服務定義，可含多個容器；Container 是實際執行單元。
- A詳: 在 Docker Cloud/Compose，Service 是服務的意圖與設定（映像、環境、網路、擴展數等），可對應 1 個或多個實體容器（副本）。Container 則是某一時刻的實際執行實例。管理上多以 Service 維度進行擴容、更新與滾動升級，而非逐一手動管理單一容器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q4

A-Q15: Stack 與 Docker Compose 檔有何關係與差異？
- A簡: Stack 相容 Compose，又加入 Docker Cloud 擴充標記與管理語意。
- A詳: Stackfile 基本相容 Compose 的 YAML 格式，描述多服務編排；在 Docker Cloud 可增添延伸標記（如調度與雲端整合屬性）。因此你能重用既有 Compose 檔快速導入，並運用 Cloud 的部署、DNS、節點選擇與視覺化管理能力，將單機編排提升到跨主機與跨雲的操作體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q7, B-Q4

A-Q16: Docker Cloud 的 Public 與 Private Repository 有何不同？
- A簡: Public 取用公開映像；Private 提供私有映像倉庫（免費帳號含一個）。
- A詳: Public repository（如 Docker Hub 公開映像）可直接搜尋與拉取常見映像（WordPress、MySQL 等）。Private repository 則用於存放自製或企業專用映像，控管存取權限，便於安全發布與自動化佈署。Docker Cloud 與 Repository 整合，讓你從映像直接建立 Service，串接版本標籤與部署流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q8

---

### Q&A 類別 B: 技術原理類

B-Q1: Docker Cloud 與 Azure 的授權連結如何運作？
- A簡: 以管理憑證與訂閱 ID 授權，讓 Docker Cloud 代你呼叫 Azure API 建立資源。
- A詳: 連結流程為：於 Docker Cloud 下載管理憑證（證書），到 Azure 舊版入口上傳至「管理憑證」，並回填 Subscription ID。完成後 Docker Cloud 即能以該憑證身分呼叫 Azure 管理 API，建立 VM、雲端服務與磁碟等資源。此為基於證書的授權模式，確保操作可審計，亦意味任何後續建置都會計入你的 Azure 帳單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q1, D-Q1

B-Q2: 在 Azure 啟動一個 Node 背後做了哪些事？
- A簡: 建 VM/雲端服務/磁碟，安裝 Docker Cloud Agent 與 Docker Engine，開放必要埠。
- A詳: Docker Cloud 呼叫 Azure API 在指定區域與規格建立 VM，附加資料磁碟（依你設定大小），並建立相應的雲端服務/網路設定。VM 啟動後自動安裝 Docker Cloud Agent 與商業支援版 Docker Engine（CS）。完成後節點註冊回管理平面，呈現為可用的 Node，約 5–10 分鐘可就緒。全程將依 Azure 計價。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q7, C-Q2

B-Q3: Docker Cloud Agent 與 Docker Engine（CS）各自扮演什麼角色？
- A簡: Agent 負責與雲/控制面溝通與生命週期；Engine 負責容器執行。
- A詳: Agent 於 Node 上與 Docker Cloud 控制平面通訊，執行佈署、更新、監控、擴展與端點設定等動作；Docker Engine（CS 版）提供容器運行時與 API 介面。若原主機已裝社群版 Engine，導入時 Agent 可能替換為 CS 版並停除原服務，確保一致性與支援度，需先行評估影響與備份。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, B-Q2

B-Q4: 由 Stackfile 觸發的佈署流程是什麼？
- A簡: 解析 YAML→建立 Services→拉映像→建立/連結容器→設定端點→健康檢查。
- A詳: Docker Cloud 讀取 Stackfile，依序建立每個 Service 的設定（映像、環境、links、ports、重啟策略等），從公/私有倉庫拉取映像，分配到選定 Nodes 上建立容器，配置連線（links/networks）與端點（Endpoints/FQDN），並在服務轉為健康（Running）後標記佈署成功。錯誤時顯示事件與時間線供排錯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q7, C-Q3

B-Q5: 服務之間的 links 與環境變數如何實現互聯？
- A簡: links 指定相依與別名，注入環境變數與主機名解析，讓容器可直連。
- A詳: 在 Stack/Compose，links: ['db:mysql'] 代表 web 服務以 mysql 別名連向 db 容器。系統會設定主機名解析與相關環境變數（如 DB 主機、埠等），讓應用在啟動時可透過別名尋址後端。此機制簡化跨容器連線設定，搭配環境變數可將密碼等參數化，降低硬編碼風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q3

B-Q6: Port 映射與 Endpoint/FQDN 的指派機制是什麼？
- A簡: 將主機埠映射到容器埠，Docker Cloud 依映射建立對外 Endpoint 與 FQDN。
- A詳: 在 Stackfile 宣告 ports（如 "80:80"），系統於 Node 開放對應主機埠並轉送至容器埠；Docker Cloud 為此建立 Endpoint，綁定該 Node 的對外位址，並配置一個可直接存取的 FQDN。使用者可直接用此 FQDN 或以 CNAME 將自有網域指向該 FQDN，完成對外發布。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q4, C-Q5

B-Q7: 為何修改設定需「重新佈署（Redeploy）」？機制是什麼？
- A簡: 部分容器參數不可熱改，需砍舊建新；Redeploy 自動重建套用新設定。
- A詳: 容器建立後，像 ports、volumes 等屬性無法直接修改。Redeploy 會停止並移除舊容器，再以新設定重建。Docker Cloud 會比對 Stackfile 與現況，標記需更新的 Services，支援對整個 Stack 或單一 Service/容器進行重新佈署，確保設定變更一致落地。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q9

B-Q8: 多節點擴展與調度在 Docker Cloud 如何運作？
- A簡: 以服務副本數與排程策略，將容器分配到不同 Nodes，提升可用性。
- A詳: 當同一 Service 設定多副本時，系統會依排程策略分散到多個 Nodes，避免單點故障並更好利用資源。若主機資源不足或埠衝突，會提示無法安置。搭配反向代理與動態埠，可在前端彈性匯聚多後端實例，形成可水平擴展的拓樸。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q7, D-Q4

B-Q9: 如何達成零停機的滾動更新（Rolling Update）？
- A簡: 多副本分批 Redeploy：先替換一個，健康後再替換下一個，前端持續分流。
- A詳: 先將 Service 擴展到至少兩個副本，前端用 Proxy 負載分流。更新時對單一容器執行 Redeploy，待其健康並接流量後，再逐一替換其他實例。整體期間仍有健康實例提供服務，從而達成不中斷升級。資料需持久化至 Volume/外部 DB 以避免資料層中斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q6, D-Q9

B-Q10: 動態 Port 映射搭配反向代理如何工作？
- A簡: 後端容器隨機映射主機埠，Proxy 轉發到實際埠，避免固定埠衝突。
- A詳: 若服務多副本都綁死 80:80 會衝突；改用動態映射（如 "80"→容器 80，主機埠由系統指派），每個實例獲得不同主機埠。前端 Proxy 透過設定（或服務發現）知道各實例的主機埠，將外部的 80/443 請求轉發至正確後端，實現同節點多實例並行，並能彈性擴縮。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q7, D-Q4

B-Q11: Docker Cloud 與 Docker Hub 的整合如何建立 Service？
- A簡: 以關鍵字搜尋映像，選定標籤與參數（環境、埠、Volume），一鍵建立。
- A詳: 在 Services 建立流程中輸入關鍵字（如 wordpress），Docker Cloud 會列出可用的公開映像。選取後設定必要參數（環境變數、Ports、Volumes 等），保存即觸發拉取映像與建立容器。此流程也支援私有倉庫影像，便於落實從映像到服務的快速交付。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, C-Q8

B-Q12: 監控與操作歷程（Timeline）如何提升可觀測性？
- A簡: 顯示節點/服務狀態、事件與操作歷程，輔助故障診斷與稽核。
- A詳: Docker Cloud 提供節點與服務視角的狀態與事件流，記錄建立、啟動、失敗、重試、重新佈署與擴容等操作，並能觀察端點、容器清單與健康狀況。這些資訊有助快速定位問題來源（映像拉取、排程、網路、儲存），並提供變更追溯以強化營運控管。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q2, D-Q3

B-Q13: 安全模型：Docker Cloud 可做什麼？有何風險？
- A簡: 取得對你雲端資源的管理權限，可建/改/刪資源並產生費用，需嚴格控管。
- A詳: 完成授權後，Docker Cloud 能代表你呼叫雲 API 建立/修改/刪除 VM、磁碟與網路設定，佈署與運行容器。這帶來自動化便利，也意味誤操作會產生費用或中斷服務。建議使用專用訂閱/資源群組、最小化權限、定期稽核與監看帳單，並為資料層規劃備份。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, D-Q7

B-Q14: 帳務與配額：免費帳號與付費有何不同？
- A簡: 免費僅支援一個 Node；超出需付月費；雲端資源費用另計由供應商收取。
- A詳: 文中示例：免費帳號只允許 1 個 Node；新增節點需付託管費（文中示價每節點每月 USD$15，僅供參考），屬管理平台的服務費。Azure/TCO 則另外依 VM 規格、磁碟容量與網路用量計費。規劃時需同時考慮託管費與底層 IaaS 成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, D-Q7

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何將 Docker Cloud 連結 Azure 帳號？
- A簡: 下載憑證→上傳至 Azure 管理憑證→回填訂閱 ID→測試連線成功。
- A詳: 
  - 具體實作步驟:
    1) 登入 Docker Cloud，選擇 Microsoft Azure，點 Add credentials 並下載管理憑證。2) 登入 Azure 舊版入口，設定→管理憑證→上傳剛下載憑證。3) 取得 Subscription ID 回填 Docker Cloud。4) 等待驗證成功（綠色勾）。
  - 關鍵設定: Azure 訂閱 ID、管理憑證。
  - 注意事項與最佳實踐: 僅授權必要訂閱；用專用訂閱隔離；完成後立刻在 Azure 監看資源與費用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, D-Q1

C-Q2: 如何在 Azure 啟動第一個 Node 並選擇規格/磁碟/區域？
- A簡: Nodes→Launch→選 Azure、區域、VM 規格、台數與磁碟大小，送出等待就緒。
- A詳:
  - 具體實作步驟: 在 Docker Cloud 的 Nodes 頁面點 Launch your first node；選擇 Microsoft Azure；選區域（Region）、VM 規格（例：Basic A1）、建立台數與磁碟大小（例：60GB）；送出後等待 5–10 分鐘。
  - 關鍵設定: VM 規格、磁碟、數量、區域。
  - 注意事項與最佳實踐: 從小規格開始驗證；同區域部署相關資源；建立後於 Azure 入口確認 VM/雲端服務/磁碟均已建立並運行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q2

C-Q3: 如何撰寫 WordPress+MySQL 的 Stackfile 並佈署？
- A簡: 定義 db/web 兩服務、環境變數與埠映射，保存並 Deploy。
- A詳:
  - 具體實作步驟: Stacks→Create→命名（如 My Blog）→貼上 Stackfile→Save and Deploy。示例:
    ```yaml
    db:
      image: mysql:latest
      environment:
        - MYSQL_ROOT_PASSWORD=YES
      restart: always
    web:
      image: amontaigu/wordpress:latest
      links:
        - db:mysql
      ports:
        - "80:80"
      restart: always
    ```
  - 關鍵設定: MySQL root 密碼、web→db 連結、80:80 埠。
  - 注意事項與最佳實踐: 生產環境請用強密碼與持久化 Volume；視需要加入反向代理與 SSL。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, D-Q3

C-Q4: 如何查看並使用 Stack 的 Endpoint 存取網站？
- A簡: 於 Stack 的 Endpoints 分頁取得自動產生的 FQDN，點擊即可開站。
- A詳:
  - 具體實作步驟: Stacks→選你的 Stack→切到 Endpoints 分頁；找到對外 80/443 對應的 FQDN；點擊檢視。
  - 關鍵設定: 服務已映射 ports（例 80:80）。
  - 注意事項與最佳實踐: 若無法開啟，檢查容器狀態、port 映射、Azure 防火牆/端點；生產建議用自有網域 CNAME 指向此 FQDN 並配置 HTTPS。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q6, D-Q3

C-Q5: 如何把自有網域透過 CNAME 指到 Docker Cloud Endpoint？
- A簡: 在你的 DNS 設定 CNAME，主機名指向 Docker Cloud 提供的 FQDN。
- A詳:
  - 具體實作步驟: 以 blog.example.com 為例，在 DNS 管理新增記錄：
    ```
    類型: CNAME
    名稱: blog
    值: <your-endpoint>.dockercloud.com.
    ```
  - 關鍵設定: CNAME 需指向 FQDN（非 IP）；尾碼點號視 DNS 供應商而定。
  - 注意事項與最佳實踐: 等待 DNS 傳播（TTL）；避免對根網域用 CNAME；若需 HTTPS，配置憑證於前端 Proxy。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q8

C-Q6: 如何修改 Stack 設定並安全地重新佈署？
- A簡: 編輯 Stackfile→保存→對有變更的 Service 執行 Redeploy，逐一替換。
- A詳:
  - 具體實作步驟: Stacks→選擇 Stack→Edit→修改 YAML→Save；系統標示需 Redeploy 的 Service；先選單一 Service 執行 Redeploy；驗證健康再處理下一個。
  - 關鍵設定: 不可熱改屬性（ports/volumes）需重建容器。
  - 注意事項與最佳實踐: 資料放 Volume；多副本滾動更新；先在測試環境驗證；維持回滾方案（保留舊標籤）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q9, D-Q9

C-Q7: 如何水平擴展 Web 服務並以 NGINX 反向代理匯聚？
- A簡: 將 web 多副本且用動態埠，前端 NGINX 匯聚並負載分流。
- A詳:
  - 具體實作步驟: 將 web Service 改用動態 ports（僅宣告容器埠 "80"），增加副本數；另建 proxy 服務，設定 upstream 指向各 web 實例主機埠，範例：
    ```nginx
    upstream blog_upstream {
      server <node-ip>:<web1-host-port>;
      server <node-ip>:<web2-host-port>;
    }
    server {
      listen 80;
      location / { proxy_pass http://blog_upstream; }
    }
    ```
  - 關鍵設定: 動態 host port 與 NGINX upstream。
  - 注意事項與最佳實踐: 自動化更新 upstream（腳本/服務發現）；健康檢查；啟用 Keepalive 與 gzip。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q10, D-Q4

C-Q8: 如何從公用 Docker Hub 快速建立新 Service？
- A簡: Services→Create→搜尋映像→選標籤→設定環境/埠→Save 立即佈署。
- A詳:
  - 具體實作步驟: 進入 Services→Create service；搜尋關鍵字（例 wordpress）；選擇映像與標籤；設定環境變數、ports 與 volumes；Save。
  - 關鍵設定: 正確的環境變數（如 DB 連線）、持久化 Volume。
  - 注意事項與最佳實踐: 先檢閱映像說明；固定版本標籤避免 latest 帶來不可預期變更；在測試環境驗證後再上線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, A-Q16

C-Q9: 如何把服務從 Azure Node 搬遷到自建機（Mini‑PC）？
- A簡: 將自建機加入為 Node，複製 Stack 設定與資料 Volume，重新佈署。
- A詳:
  - 具體實作步驟: 準備自建 Linux 主機，依指引將其加入 Docker Cloud 為 Node；在新 Node 上建立相同的 Volumes/資料路徑並還原資料；將 Stack 調度到新 Node 佈署與驗證；再關閉 Azure 上的對應服務。
  - 關鍵設定: 資料一致性（DB/上傳檔）、端點與 DNS 切換。
  - 注意事項與最佳實踐: 維持雙活短期驗證；設定備援與監控；完工後清理 Azure 資源避免額外費用。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q7, D-Q2

C-Q10: 如何在 Azure 監看成本並清理不需要的資源？
- A簡: 於 Azure 入口查看計費/資源，刪除閒置 VM/磁碟/端點，關閉不必要服務。
- A詳:
  - 具體實作步驟: Azure 入口→成本管理/計費→監看資源消耗；資源群組/傳統資源→檢視 VM、磁碟、雲端服務；停止或刪除不再使用的資源。
  - 關鍵設定: 傳統（Classic）與新式資源位置；磁碟是否有附掛。
  - 注意事項與最佳實踐: 刪除前先備份資料；定期巡檢孤兒磁碟與 IP；將測試與生產分開訂閱或資源群組。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, D-Q7

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 連結 Azure 憑證失敗怎麼辦？
- A簡: 確認用舊版入口上傳管理憑證、訂閱 ID 正確、等待生效並重試。
- A詳:
  - 問題症狀描述: Docker Cloud 無法驗證 Azure，缺少綠色勾勾或報錯。
  - 可能原因分析: 憑證未於「管理憑證」上傳；訂閱 ID 錯誤；權限不足；傳播延遲。
  - 解決步驟: 至 Azure 舊版入口上傳憑證；核對訂閱 ID；稍等數分鐘；於 Docker Cloud 重新驗證。
  - 預防措施: 使用專用訂閱；記錄憑證來源；定期稽核授權。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q1

D-Q2: Node 佈署久未完成或失敗怎麼辦？
- A簡: 檢查 Azure 配額/區域/規格、網路/雲端服務、Agent 安裝與日誌。
- A詳:
  - 問題症狀描述: Node 卡在 Provisioning/Initializing 多於 10 分鐘或失敗。
  - 可能原因分析: VM 規格/區域不可用；配額不足；網路/端點建立失敗；Agent 無法回報。
  - 解決步驟: 在 Azure 入口查看 VM/雲端服務狀態與事件；更換區域或規格；刪除重建；於 VM 檢查 Agent/網路。
  - 預防措施: 事先確認配額；選常用區域；小規格試跑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q12

D-Q3: 無法開啟 WordPress 首頁怎麼辦？
- A簡: 檢查容器運行、port 映射、Endpoint/FQDN、Azure 防火牆與服務日誌。
- A詳:
  - 問題症狀描述: 點擊 Endpoint 404/超時或連不上。
  - 可能原因分析: 容器未 Running；未映射 80:80；Endpoint 未建立；Azure 端口未開；web→db 連線失敗。
  - 解決步驟: 檢查 Service/容器狀態；確認 ports 設定；重佈署；在 Azure 入口查看端點；檢閱容器日誌修正環境變數。
  - 預防措施: 以範例 Stackfile 佈署；健康檢查；自動重啟策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q4, B-Q6

D-Q4: 擴展服務時提示埠衝突如何處理？
- A簡: 改用動態映射或新增 Node，前端以 Proxy 匯聚流量。
- A詳:
  - 問題症狀描述: 增加 web 容器副本出現「80 已被占用」。
  - 可能原因分析: 多副本都要求 80:80 固定映射；同 Node 無法重複占用主機 80。
  - 解決步驟: 改 ports 為動態主機埠；或增加 Node 把副本分散；在前端 Reverse Proxy 匯聚。
  - 預防措施: 設計時即規劃 Proxy 與動態埠；以滾動更新避免停機。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q7

D-Q5: 重新佈署後資料遺失如何避免與補救？
- A簡: 使用 Volume/資料容器持久化；事前備份；還原資料並調整 Stack。
- A詳:
  - 問題症狀描述: Redeploy 後 DB/上傳檔不見。
  - 可能原因分析: 資料存於容器可寫層，重建即遺失。
  - 解決步驟: 將資料改存 Volume；還原備份；重新佈署；驗證持久性。
  - 預防措施: 一開始即使用 Volume/外部儲存；定期備份；在測試環境先演練更新。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q3

D-Q6: 導入既有 Linux 主機為 Node 後 Docker 被替換怎麼辦？
- A簡: Docker Cloud 會安裝 CS 版並移除原 Engine；需事前評估與備份。
- A詳:
  - 問題症狀描述: 原主機 Docker 服務被停用/替換。
  - 可能原因分析: Agent 安裝流程會部署 CS 版以確保一致性。
  - 解決步驟: 於測試環境先驗證；備份原容器與資料；規劃停機窗；必要時改用由 Docker Cloud 直接新建 VM。
  - 預防措施: 生產與測試隔離；文件化既有環境；避免在未評估的主機上直接接入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q9

D-Q7: 帳單暴增或預算超支如何處理？
- A簡: 盤點資源、縮規/關閉閒置、清理孤兒磁碟，監看成本與警示。
- A詳:
  - 問題症狀描述: Azure 帳單超出預期；Docker Cloud 託管費增加。
  - 可能原因分析: 多餘節點/大規格 VM、閒置資源未刪、跨區頻寬。
  - 解決步驟: 檢視計費報表；關閉不必要 VM；刪除未掛載磁碟/IP；縮規至合適等級；降低節點數。
  - 預防措施: 設成本警示；專用測試訂閱； IaC 管理資源生命週期。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q14, C-Q10

D-Q8: Endpoint FQDN 無法解析或自訂網域無效怎麼辦？
- A簡: 檢查 CNAME 設定、TTL、拼字與傳播時間；避免根域 CNAME。
- A詳:
  - 問題症狀描述: FQDN 打不開或自訂網域無法指向服務。
  - 可能原因分析: CNAME 指錯、TTL 未生效、使用根網域 CNAME、遺漏結尾點號（供應商差異）。
  - 解決步驟: 用 dig/nslookup 驗證；改用子網域 CNAME；等待 TTL；修正拼字。
  - 預防措施: 變更前降低 TTL；文件化 DNS 設定；在低流量時段切換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, B-Q6

D-Q9: Redeploy 造成短暫停機如何改善？
- A簡: 以多副本與滾動更新，逐一替換；前端 Proxy 保持服務。
- A詳:
  - 問題症狀描述: Redeploy 時全站短暫不可用。
  - 可能原因分析: 單副本服務被同時移除重建；無前端負載平衡。
  - 解決步驟: 擴展至至少兩副本；配置 Proxy；按序 Redeploy 單一實例；確認健康再替換下一個。
  - 預防措施: 預先設計 HA 與健康檢查；資料持久化；演練更新流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q6

D-Q10: 在新式 Azure 入口找不到 VM/雲端服務怎麼辦？
- A簡: 這些為傳統（Classic）資源；在「虛擬機器(傳統)」檢視或用舊入口。
- A詳:
  - 問題症狀描述: 新入口看不到剛建立的 VM/雲端服務。
  - 可能原因分析: Docker Cloud 以 Classic 模式建立資源，顯示分類不同。
  - 解決步驟: 在新式入口切換至「傳統資源」檢視；或改用舊版管理入口；亦可用 Azure CLI 查詢。
  - 預防措施: 文件化資源類型；逐步導入 ARM；規劃一致的資源模型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q10

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Docker Cloud 託管服務？
    - A-Q2: 託管（管理）與主機代管（Hosting）有何差異？
    - A-Q3: 什麼是 Docker Machine？
    - A-Q4: 什麼是 Docker Compose？
    - A-Q7: Docker Cloud 的 Node、Service、Stack 分別是什麼？
    - A-Q8: 什麼是 Endpoint 與 FQDN？為何重要？
    - A-Q9: 為什麼大規模管理不能只靠 docker engine 指令？
    - A-Q10: 為什麼要把 Docker Cloud 與 Azure 連結？會產生什麼費用？
    - A-Q13: 什麼是資料 Volume/資料容器（DATA）？
    - A-Q14: Service 與 Container 有何差異？
    - B-Q6: Port 映射與 Endpoint/FQDN 的指派機制是什麼？
    - C-Q1: 如何將 Docker Cloud 連結 Azure 帳號？
    - C-Q2: 如何在 Azure 啟動第一個 Node 並選擇規格/磁碟/區域？
    - C-Q3: 如何撰寫 WordPress+MySQL 的 Stackfile 並佈署？
    - C-Q4: 如何查看並使用 Stack 的 Endpoint 存取網站？

- 中級者：建議學習哪 20 題
    - A-Q5: 什麼是 Docker Swarm？
    - A-Q6: Machine、Compose、Swarm 的差異與分工？
    - A-Q11: 什麼是高可用性（HA）？文中的 WordPress 如何達成？
    - A-Q12: 什麼是 Reverse Proxy？在案例中扮演什麼角色？
    - A-Q15: Stack 與 Docker Compose 檔有何關係與差異？
    - B-Q1: Docker Cloud 與 Azure 的授權連結如何運作？
    - B-Q2: 在 Azure 啟動一個 Node 背後做了哪些事？
    - B-Q3: Docker Cloud Agent 與 Docker Engine（CS）各自扮演什麼角色？
    - B-Q4: 由 Stackfile 觸發的佈署流程是什麼？
    - B-Q5: 服務之間的 links 與環境變數如何實現互聯？
    - B-Q7: 為何修改設定需「重新佈署」？機制是什麼？
    - B-Q10: 動態 Port 映射搭配反向代理如何工作？
    - B-Q11: Docker Cloud 與 Docker Hub 的整合如何建立 Service？
    - B-Q12: 監控與操作歷程如何提升可觀測性？
    - C-Q5: 如何把自有網域透過 CNAME 指到 Docker Cloud Endpoint？
    - C-Q6: 如何修改 Stack 設定並安全地重新佈署？
    - C-Q7: 如何水平擴展 Web 服務並以 NGINX 反向代理匯聚？
    - C-Q8: 如何從公用 Docker Hub 快速建立新 Service？
    - D-Q3: 無法開啟 WordPress 首頁怎麼辦？
    - D-Q4: 擴展服務時提示埠衝突如何處理？

- 高級者：建議關注哪 15 題
    - B-Q8: 多節點擴展與調度在 Docker Cloud 如何運作？
    - B-Q9: 如何達成零停機的滾動更新？
    - B-Q13: 安全模型：Docker Cloud 可做什麼？有何風險？
    - B-Q14: 帳務與配額：免費帳號與付費有何不同？
    - C-Q7: 如何水平擴展 Web 服務並以 NGINX 反向代理匯聚？
    - C-Q9: 如何把服務從 Azure Node 搬遷到自建機（Mini‑PC）？
    - C-Q10: 如何在 Azure 監看成本並清理不需要的資源？
    - D-Q1: 連結 Azure 憑證失敗怎麼辦？
    - D-Q2: Node 佈署久未完成或失敗怎麼辦？
    - D-Q5: 重新佈署後資料遺失如何避免與補救？
    - D-Q6: 導入既有 Linux 主機為 Node 後 Docker 被替換怎麼辦？
    - D-Q7: 帳單暴增或預算超支如何處理？
    - D-Q8: Endpoint FQDN 無法解析或自訂網域無效怎麼辦？
    - D-Q9: Redeploy 造成短暫停機如何改善？
    - D-Q10: 在新式 Azure 入口找不到 VM/雲端服務怎麼辦？