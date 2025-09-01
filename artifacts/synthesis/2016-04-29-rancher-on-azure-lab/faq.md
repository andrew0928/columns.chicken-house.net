# Rancher - 管理內部及外部 (Azure) Docker Cluster 的好工具

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Rancher？
- A簡: Rancher 是跨環境的容器管理與編排平台，提供主機註冊、服務部署、負載平衡、升級與監控等一站式能力。
- A詳: Rancher 是一套用來管理 Docker 環境的平臺，能同時管理多台主機與多個環境（Environments），支援 Stack/Service 的模型部署，並內建負載平衡與 In-Service Upgrade，協助零停機更新。Rancher 提供易用的 Web UI、資源監控（Host 與容器層級）、與多雲整合（含 Azure）。它同時支援多種編排技術（如內建 Cattle、亦可選 Swarm/Mesos），讓開發與營運可用一致的方式部署與維運容器化應用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q9, A-Q11, B-Q1

Q2: 什麼是 Docker Cluster？
- A簡: 由多台安裝 Docker 的主機組成的資源池，能彈性部署、擴縮容器並提供高可用與調度能力。
- A詳: Docker Cluster 是將多台 Docker 主機（Hosts/Nodes）集合成一個可統一管理的資源池，讓應用以服務為單位分散部署在不同主機上，達到高可用、彈性擴縮與資源最佳化。透過編排系統（如 Rancher 的 Cattle、Swarm、Kubernetes 等），開發者定義服務與相依關係，平台負責安置容器、處理故障、負載平衡、與滾動升級。Rancher 讓這些操作以圖形化方式執行，降低門檻。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q10, B-Q7

Q3: 什麼是 Rancher OS？
- A簡: 專為執行 Docker 設計的極簡 Linux，Docker 為 PID 1；系統功能多以容器形式提供。
- A詳: Rancher OS 是為容器化工作負載設計的精簡 Linux 發行版，系統啟動後即以 Docker 做為 PID 1，移除非必要元件以縮減映像大小與攻擊面，常見的系統服務（如 SSH、Cloud-init）以「系統容器」提供。它非常適合用來作為 Docker Host，能快速啟動並易於維護，亦可在其上直接以 docker run 啟動 Rancher Server，構建最小化且一致的運行環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q1, C-Q2

Q4: 為什麼選擇 Rancher 作為容器管理平台？
- A簡: 介面清楚、資源監控完善、支援 In-Service Upgrade 與內建 Load Balancer，且多雲整合方便。
- A詳: Rancher 的核心價值在於降低容器營運複雜度。其 UI 清楚呈現主機與每個容器的 CPU/RAM/Disk 使用，方便定位瓶頸；提供 In-Service Upgrade，能分批滾動替換實例、支持回滾；內建 HAProxy 為基礎的 Load Balancer，簡化對外發布；支援多環境隔離（如開發與正式），並能直接對接 Azure 等 IaaS 自動建機，讓部署、擴縮、升級與監控在同一平台完成。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q13, B-Q8, C-Q7

Q5: Rancher 與 Docker Cloud（Tutum）的差異？
- A簡: Docker Cloud 收費且監控較精簡；Rancher 自架免費、監控豐富，並提供就地升級與內建 LB。
- A詳: 文章經驗指出 Docker Cloud（Tutum）免費版僅支援1節點，增加節點需付費，且缺少細緻的資源統計儀表板；Rancher 作為自託管平台，部署在自有主機上即可使用，提供更完整的主機與容器資源監控、內建負載平衡與 In-Service Upgrade，適合需要多節點與跨環境的一站式管理且希望控制成本的團隊。但 Docker Cloud 的託管與省維護優勢仍具吸引力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q14, A-Q13

Q6: Rancher 與 Azure Container Service 的差異？
- A簡: ACS 快速建立編排叢集；Rancher 著重多環境與服務管理。文中時點 Rancher 尚無法匯入現有 Swarm。
- A詳: Azure Container Service（文中時點）可快速以幾步完成 Swarm/Mesos 叢集的自動化建置，解決「如何建叢集」；Rancher 著重「如何在多環境管理服務」，提供 Stack/Service 模型、LB、升級、監控與 UI。當時 Rancher 不支援匯入外部建立的 Swarm 叢集（官方表示努力中），因此兩者定位與流程不同：ACS 建好叢集，Rancher 提供跨環境的運維價值。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: B-Q17, C-Q4

Q7: 什麼是 Cattle（Rancher 的編排引擎）？
- A簡: Cattle 是 Rancher 內建編排平台，負責服務調度、健康檢查、升級與依賴管理。
- A詳: Cattle 為 Rancher Labs 開源的基礎編排層，管理容器服務的生命週期，如複本數（Scale）、部署順序、健康檢查、跨主機調度與 In-Service Upgrade。它與 Docker Compose 格式相容，讓使用者以熟悉的語法定義服務，Rancher UI 會解析並執行。除 Cattle 外，Rancher 也可選擇接入 Swarm/Mesos 作為替代編排引擎。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q11, A-Q8

Q8: Docker Swarm、Mesos、Kubernetes 的差異？
- A簡: Swarm 原生 Docker 編排；Mesos 通用資源管理；Kubernetes 提供完整容器編排生態與控制面。
- A詳: Swarm 是 Docker 官方編排，重視與 Docker API 相容；Mesos 是更通用的資源管理系統，可承載多種框架（含容器）；Kubernetes 提供豐富物件模型（Deployment/Service/Ingress）與健康檢查、滾動更新、服務發現。Rancher 可整合不同編排，讓使用者依需求與既有經驗選擇。文中將 Cattle/Swarm/Mesos列為可用選項，Kubernetes 亦為常見替代方案。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q16, B-Q17

Q9: Rancher 的 Environment 是什麼？
- A簡: Environment 是資源與服務的隔離邏輯邊界，可獨立管理主機、Stack 與權限。
- A詳: 在 Rancher 中，Environment（後稱 Project）是切分資源的單位。每個 Environment 有各自的主機清單、Stack/Service 與設定，可用來區隔 Dev/Prod 等環境或不同業務線，避免互相影響。UI 右上角可快速切換 Environment，部署與擴縮等操作僅作用於當前環境，讓多租戶與多團隊協作更清晰。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q3, C-Q4

Q10: Stack、Service、Container、Host（Node）分別是什麼？
- A簡: Host 為節點；Container 為運行單元；Service 為容器組；Stack 則為一組應用服務集合。
- A詳: Host/Node 指承載容器的實體或虛擬機。Container 是映像運行出的單一實例。Service 是具備相同角色的一組容器（可水平擴展），例如 Web 前端。Stack 是應用層級的打包，包含多個 Service（如 Web、DB、LB）與其關聯。這層次化模型讓部署、擴縮與升級能針對不同粒度執行，並於 UI 清楚呈現依賴關係。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q5, C-Q5

Q11: 什麼是 In-Service Upgrade？
- A簡: 以分批替換服務實例的方式就地升級，保持服務連續性，並支援回滾。
- A詳: In-Service Upgrade 是 Rancher 對既有 Service 進行不中斷升級的能力。透過調整 Compose 設定（映像版本、環境變數、Port、Volume 等），平台按 Batch Size 與間隔拉起新容器，通過健康檢查後再停舊容器，直到全部替換完成。若驗證失敗可一鍵 Rollback，還原升級前狀態，降低改版風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q8, C-Q9, A-Q24

Q12: 為什麼需要 Load Balancer 在容器架構中？
- A簡: LB 聚合多實例服務，提供流量分配、故障切換與對外單一入口，提高可用性與擴展性。
- A詳: 容器服務常以多個複本提供高可用與彈性伸縮，需藉由 LB 將外部流量分發至後端實例，並在節點異常時自動移除故障目標，避免單點失效。Rancher 內建基於 HAProxy 的 LB，可直接選取目標 Service、設定 Port/協議與多 Stack 路由，讓服務發布與擴容更簡單。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q7, A-Q13

Q13: Rancher 內建 Load Balancer 與 HAProxy 的關係？
- A簡: 內建 LB 以 HAProxy 為核心，支援其語法與進階設定，並透過 UI 簡化配置。
- A詳: Rancher 的 LB 服務封裝了 HAProxy，使用者在 UI 勾選目標 Service、設定前端/後端規則即可完成常見配置；若需要進階行為（如 Header/URL 規則、權重、健康檢查），可注入 HAProxy 兼容的設定片段。這使得初學者能快速上手，高階用戶亦可使用成熟的 HAProxy 能力實現複雜路由。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q16, C-Q7

Q14: Rancher 提供哪些資源監控與儀表板？
- A簡: 提供 Host 與容器層級的 CPU、RAM、磁碟、網路等即時與歷史使用狀況。
- A詳: Rancher 於每台 Host 卡片與容器詳情頁呈現關鍵資源使用度，包括 CPU/記憶體/儲存/網路，協助快速定位資源瓶頸與異常容器。這些數據來自 Agent 與內部度量機制彙整後，以 UI 視覺化展示，與部署、升級、擴縮操作整合在同一介面，提升日常維運效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, D-Q9

Q15: Rancher 支援哪些 IaaS/雲端供應商？
- A簡: 支援多家 IaaS（含 Microsoft Azure），可透過憑證自動建立並註冊主機。
- A詳: Rancher 對接主流 IaaS，包含 Azure 等，能在單一畫面填入認證、選規格/數量，即自動建立 VM、安裝 Agent 並加入指定 Environment。這降低手動建機與註冊 Host 的操作成本，讓跨公有雲與自架環境的一致化管理更容易落地。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, B-Q9, D-Q8

Q16: 什麼是 Scale Out？在 Rancher 中的意義？
- A簡: 增加服務實例數量以提高吞吐與可用性；Rancher 會自動分散容器到不同主機。
- A詳: Scale Out 指將同一服務的容器實例數從 N 提升至 N+K，以橫向擴展達成承載提升與冗餘。Rancher UI 可直接調整 Service 的 Scale 值，平台會拉起新實例並盡量分散於不同 Hosts，配合 LB 將流量分配至新增實例，實現快速擴容。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q6, A-Q12

Q17: 什麼是零停機升級？如何在 Rancher 達成？
- A簡: 升級過程不中斷對外服務；透過 start-before-stopping、分批與健康檢查達成。
- A詳: 零停機升級是在更新服務時維持連續對外提供。Rancher 的 In-Service Upgrade 允許先啟新實例（Start Before Stopping）、通過健康檢查再停舊實例，並以 Batch Size/Interval 控制節奏。配合 LB 與回滾機制，即可在異常時快速恢復，降低風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q13, C-Q8, C-Q9

Q18: 為何要同時使用 Local 與 Azure 兩個 Environment？
- A簡: 用於隔離開發與正式環境，既保安全又能以同一平台統一部署與維運。
- A詳: 文中示範以 Local Environment 供內部開發測試、Azure Environment 提供對外正式服務。兩者完全隔離、由同一 Rancher 管控，保有一致的部署體驗。這種分層讓測試不影響生產，且能演練升級與擴縮流程，降低上線風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q4, A-Q9

Q19: Rancher Server 的建議資源規格與特性？
- A簡: 至少 1GB RAM，實務建議 2GB；啟動較慢，因使用多個 Java 元件。
- A詳: 文中實測 Rancher Server 作為單一容器運行時，1GB 可啟動但餘裕有限，2GB 較合適。因後端採用多個 Java 元件，容器啟動後需 1–2 分鐘完成初始化。建議將 Rancher Server 與工作負載分離，獨立 VM 承載，避免與業務容器爭資源影響管理面穩定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q1

Q20: Rancher 的安全性預設與建議做法？
- A簡: 預設無登入保護；正式環境務必啟用認證、限制網路存取並升級 TLS。
- A詳: 新裝 Rancher Server 預設 8080 無需密碼即可進入管理介面。實務上應立即啟用身份驗證（整合 LDAP/OAuth 等）、限制管理面來源 IP、置於私網並透過反向代理與 TLS 對外、定期更新版本，避免未授權存取與中間人攻擊。單機測試可暫時開放，生產務必加固。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q10, C-Q2

Q21: Rancher OS 與一般 Linux 發行版的差異？
- A簡: 極簡、以 Docker 為核心；傳統服務多以容器提供，映像小、啟動快。
- A詳: 一般 Linux 內建完整套件庫與系統服務；Rancher OS 精簡至核心與必需元件，系統服務（如 SSH）以容器運行。優點是體積小、攻擊面少、一致性高；代價是需轉換思維，以容器化方式補齊工具鏈，適合純容器主機，不適合作為通用工作站。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, B-Q2

Q22: Rancher 與 Azure Cloud Service 的升級機制比較？
- A簡: Azure 早期即有 Prod/Staging 切換；Rancher 以就地分批替換，缺少內建預熱槽位。
- A詳: 文中回顧 Azure Cloud Service 提供 Production/Staging 雙槽切換，上線前可在 Staging 驗證，且支援瞬間切換與快速回退；Rancher 以 In-Service Upgrade 就地替換容器，能達成零停機但少了內建「預備槽」概念，驗證需在同一服務內進行。若需相似體驗，可用兩個 Stack 模擬藍綠切換。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, B-Q13, C-Q8

### Q&A 類別 B: 技術原理類

Q1: Rancher Server 如何運作？架構與角色
- A簡: Rancher Server 以容器運行，提供 UI/API；Host 透過 Agent 與之通訊，完成部署與監控。
- A詳: 原理說明：Rancher Server 是控制平面，提供 REST API 與 Web UI，負責 Environment、Stack/Service 定義與狀態管理。關鍵流程：1) 啟動 server 容器；2) 在每台 Host 透過「Add Host」註冊，部署 Agent；3) Agent 心跳回報資源與事件，接收調度指令；4) Server 協調部署、升級、LB 與監控。核心組件：Server 容器、Agent 容器、資料存儲（隨版本可內建或外部 DB）、UI/API 層。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q3, C-Q2

Q2: Rancher OS 如何運作？PID 1 與系統容器
- A簡: 以 Docker 作為 PID 1，系統服務以容器形式運行，維持最小化與一致性。
- A詳: 原理說明：Rancher OS 開機後直接啟動 Docker 守護程序為 PID 1，其餘服務（如 SSH）作為系統容器運行。流程：1) 開機載入 kernel；2) 啟動 Docker；3) 拉起 system-docker 容器提供基礎服務；4) 使用者工作負載由 user-docker 管理。核心元件：kernel、system-docker、user-docker、Cloud-init（配置）。此設計讓主機管理與工作負載完全容器化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q1

Q3: Rancher 如何把 Host 加入管理？註冊流程
- A簡: 透過 UI 產生註冊指令，在 Host 上啟動 Agent 容器，與 Server 建立心跳與指令通道。
- A詳: 原理說明：Add Host 會產生含註冊 Token 的 docker run 指令。關鍵步驟：1) 在 Host 執行指令啟動 Agent；2) Agent 連回 Server 註冊並綁定 Environment；3) 上報 Host 資源與容器事件；4) 接收調度任務並拉起服務。核心組件：Agent 容器、註冊 Token、心跳/事件通道。完成後 Host 立即出現在 UI，可見資源與容器資訊。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q4, D-Q2

Q4: Environment 的隔離機制如何設計？
- A簡: 以邏輯命名空間隔離資源與權限，Host/Stack/Service 與憑證綁定至各自 Environment。
- A詳: 原理說明：Environment（Project）是控制平面的命名空間，Server 將 Host 與服務的元資料、認證、憑證分別綁定於對應 Environment。流程：1) 建立 Environment；2) 在該 Environment 下註冊 Host/部署服務；3) UI 切換時僅顯示該命名空間資源。核心組件：元資料存儲、權限策略、UI 篩選。這確保不同團隊/階段互不干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q3

Q5: Stack/Service 是如何映射為容器與網路的？
- A簡: Stack 定義應用組合，Service 定義可擴縮單元；解析 Compose 後拉起對應容器與連結。
- A詳: 原理說明：Rancher 解析 Docker Compose（或 UI 表單）為 Stack/Service 模型。流程：1) 讀取映像、環境變數、port、volumes、links；2) 為每個 Service 建立指定數量的容器；3) 建立網路連結與服務發現（基於別名/內部 DNS）；4) 對外暴露端口或透過 LB 發布。核心組件：Compose 解析器、調度器、網路/服務發現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q11, C-Q5

Q6: In-Service Upgrade 的執行流程與機制？
- A簡: 依批次策略啟新容器、檢查健康、移除舊容器；可手動完成或回滾。
- A詳: 原理說明：升級基於新 Compose 設定，Server 生成升級計畫。流程：1) 按 Batch Size 啟新容器；2) 等待啟動/健康通過；3) 停對應舊容器；4) 迭代至完成；5) 狀態為 Upgraded，使用者選擇 Finish（清理舊容器）或 Rollback。核心組件：升級控制器、健康檢查、狀態機、回收器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q17, C-Q8, C-Q9

Q7: Scale 與排程：Rancher 如何把容器分散至不同 Host？
- A簡: 預設採分散策略，於可用主機中均衡放置容器，並考量資源與親和/反親和規則。
- A詳: 原理說明：當調整 Service 的 Scale 值，調度器評估可用 Host 的資源（CPU/Mem）、已佈署分佈與策略，盡量分散實例至不同節點，降低同時故障風險。流程：1) 計算目標實例數；2) 選主機並拉起容器；3) 同步狀態與 LB 目標。核心組件：調度器、資源評估、約束規則（親和/反親和）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q6, D-Q3

Q8: 內建 Load Balancer 如何分流？背後機制
- A簡: 以 HAProxy 接收前端連線，依規則將請求轉發到後端服務實例，並健康檢查。
- A詳: 原理說明：LB 啟動一個 HAProxy 容器，建立前端端口與後端目標（Service）。流程：1) 監聽指定 Port；2) 定時健康檢查後端；3) 依演算法（如輪詢）分發；4) 異常下線移除目標。核心組件：HAProxy、配置生成器、健康檢查。支援跨 Stack 目標、URL/Host 路由與進階 HAProxy 設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q13, C-Q7, D-Q4

Q9: Rancher 與 Azure 整合如何自動建立主機？
- A簡: 透過 Azure 認證建立 VM，安裝 Agent 後自動加入 Environment，實現一鍵擴容。
- A詳: 原理說明：Rancher 內建 IaaS 供應商驅動。流程：1) 在 UI 輸入 Azure 憑證/設定 VM 規格；2) Server 調用 Azure API 建立 VM；3) 佈署 Agent 並註冊；4) Host 出現在環境中。核心組件：雲端驅動器、認證管理、Agent 自動佈署。相比手動建機，能縮短佈署時間並提升一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q4, D-Q8

Q10: Rancher 的資源監控數據如何收集與呈現？
- A簡: Agent 收集 Host/容器統計並傳回 Server，統一彙整後以 UI 圖表呈現。
- A詳: 原理說明：安裝於 Host 的 Agent 讀取容器與宿主機度量（cgroups、/proc 等），定期上報 Server。流程：1) 採集指標；2) 傳輸至 Server；3) 彙整與存儲；4) UI 可視化。核心組件：Agent、指標蒐集器、UI 儀表板。當 Agent 斷線或權限不夠，度量可能為 0 或缺失。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q9

Q11: Rancher Compose 與 Docker Compose 的關係？
- A簡: 相容於 Docker Compose 語法，Rancher 解析後提供升級、擴縮、LB 等進階動作。
- A詳: 原理說明：Rancher 可直接匯入 docker-compose.yml，將服務定義轉為 Stack/Service。流程：1) 解析 YAML；2) 建立服務與相依；3) 支援擴縮與升級；4) 可搭配 Rancher Compose CLI 進行腳本化升級（含 Batch 參數）。核心組件：YAML 解析器、部署控制器、CLI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q8

Q12: Rollback 機制背後的動作是什麼？
- A簡: 停掉新實例、刪除其資源，並重新啟動升級前的舊實例，恢復原狀。
- A詳: 原理說明：升級失敗時，Rollback 會回到升級前快照。流程：1) 標記新實例為待移除；2) 停止與刪除新容器；3) 重啟舊容器（保留的設定/卷）；4) 將 LB 與服務狀態恢復。核心組件：狀態機、資源回收器、服務路由恢復。確保快速復原降低停機風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q9, D-Q7

Q13: Start-before-stopping 對服務可用性的影響？
- A簡: 先啟新、後停舊可降低中斷風險；相反順序則適合不允許雙版本並存的場景。
- A詳: 原理說明：此選項決定升級順序。流程：1) Start-before-stopping：先起新容器，健康通過後停舊；2) 反之則先停舊再起新。核心考量：零停機、狀態遷移、相容性。建議：多數 Web/無狀態服務選用先起後停；對於需唯一性或不允許雙寫的服務，謹慎評估。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q8, D-Q5

Q14: 多 Environment 切換與部署視圖如何協作？
- A簡: UI 依當前 Environment 過濾資源，部署操作僅影響該環境，避免交叉干擾。
- A詳: 原理說明：Environment 作為命名空間，Server 與 UI 在查詢與操作時附帶環境上下文。流程：1) 右上角切換環境；2) 列表與儀表板過濾；3) Add Host/Stack 只對當前環境生效。核心組件：環境上下文、UI 篩選、API 作用域。確保 Dev/Prod 操作清晰分離。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q3

Q15: 容器資源統計（CPU/RAM/Disk/Net）的核心元件？
- A簡: 由 Host Agent 讀取 cgroups、/proc 與 Docker API，彙整後回傳 Server 顯示。
- A詳: 原理說明：Linux cgroups 與 /proc 暴露資源使用；Docker API 提供容器層級統計。流程：1) Agent 定期讀取；2) 轉換為統一格式；3) 送往 Server；4) 儀表板圖表化。核心組件：Agent、度量收集器、API。若 Agent 權限不足或版本不匹配可能導致統計異常。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q9

Q16: HAProxy 進階設定如何注入到 LB？
- A簡: 透過 Rancher 的 LB 設定項加入 HAProxy 兼容片段，擴展路由與健康檢查行為。
- A詳: 原理說明：LB 容器會根據 UI 設定產生 HAProxy 配置；可於進階欄位加入自定 directives。流程：1) 設定目標服務；2) 在進階區填寫額外 HAProxy 配置（如 acl、backend 參數）；3) 套用並滾動重載。核心組件：配置生成器、HAProxy、熱重載機制。能滿足複雜場景如基於路徑/標頭的流量分配與細緻健康檢查。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, C-Q7

Q17: Azure Container Service 建置 Swarm 的流程與限制
- A簡: 透過 Azure 市集向導輸入基本資料與金鑰，數分鐘自動建成 Swarm；當時無法匯入 Rancher。
- A詳: 原理說明：ACS 以模板自動建立含管理/工作節點的 Swarm 叢集。流程：1) 市集選 ACS；2) 填訂閱/資源群組/地區/SSH key；3) 選 Orchestrator 與節點規格/數量；4) 部署完成可用。限制：文中時點 Rancher 不能匯入既有 Swarm，導致兩系統流程分開。適合快速上雲建叢集。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q4

Q18: Rancher 的服務連結與服務發現如何運作？
- A簡: 透過 Compose links/別名與內部解析，服務間可用名稱互相訪問，簡化相依配置。
- A詳: 原理說明：在 Compose 或 UI 定義服務關聯，Rancher 建立內部 DNS/別名與網路連結。流程：1) 解析 links/depends_on；2) 建立服務別名；3) 容器內以服務名存取對端。核心組件：服務發現、內部 DNS、網路。這讓 Web 服務以「db:3306」存取資料庫，避免硬編碼 IP。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q10

### Q&A 類別 C: 實作應用類

Q1: 如何安裝 Rancher OS 到硬碟？
- A簡: 下載映像啟動後，以 ros install 安裝至磁碟，重開機即載入極簡容器主機環境。
- A詳: 具體實作步驟：1) 下載 Rancher OS 映像並以 USB/ISO 啟動；2) 取得網路後執行 `sudo ros install -d /dev/sda`（依實際磁碟調整）；3) 設定雲端初始化或 SSH；4) 重啟即完成。關鍵設定：網路、SSH 金鑰。注意事項：確認磁碟代號與資料清除、使用穩定電源、設定時區。最佳實踐：安裝完成後更新至相容版本，並鎖定給 Rancher Server/Agent 的資源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2

Q2: 如何啟動 Rancher Server 容器並登入？
- A簡: 在 Docker 主機上執行 `docker run -p 8080:8080 rancher/server`，稍候以瀏覽器連入。
- A詳: 具體步驟：1) 準備一台 Docker 主機（建議獨立跑 Server）；2) 執行 `docker run -d --restart=unless-stopped -p 8080:8080 rancher/server`；3) 等候 1–2 分鐘初始化；4) 以瀏覽器開 `http://{IP}:8080`。注意：預設無密碼，正式環境請立即啟用認證、置於私網與 TLS 代理。最佳實踐：分配≥2GB RAM，避免與工作負載混用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, D-Q1

Q3: 如何建立 Local Environment 並新增三台 Host？
- A簡: 新增 Environment 後，於 Hosts 選單 Add Host，複製註冊指令到三台主機執行即可。
- A詳: 步驟：1) UI: Environment > Manage > Add，新建 Local（編排選 Cattle）；2) 切換至 Local；3) Infrastructure > Hosts > Add（Custom）；4) 複製註冊指令（含 Token）到三台 Rancher OS/Docker 主機執行；5) 稍候即可在 UI 見到三台 Host。注意：Host 與 Server 需可互通（防火牆/安控），時間同步。最佳實踐：分散主機區域與規格確保容錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q9

Q4: 如何在 Azure 以 Rancher 自動建立 Hosts？
- A簡: 在 Hosts > Add 選 Azure，填入憑證與 VM 規格數量，按 Create 自動建機並註冊。
- A詳: 步驟：1) 切至目標 Environment；2) Hosts > Add > Azure；3) 輸入訂閱憑證/認證、區域、VM 規格與數量、SSH key；4) 按 Create 等候部署；5) Host 自動加入並可用。關鍵設定：訂閱憑證、網路/安全群組。注意：計費與配額、清理未用資源。最佳實踐：標記資源標籤、以多可用性區域部署提升可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q8

Q5: 如何建立 Stack 並部署 tutum/hello-world？
- A簡: 新建 Stack，貼上 Docker Compose 定義或以 UI 設定映像與 Port，按 Create 部署。
- A詳: 步驟：1) Applications > Stacks > Add；2) 以 UI 或貼上 compose：`image: tutum/hello-world`、`ports: ["80:80"]`；3) Create 等待部署完成；4) 以 Host IP:Port 驗證。關鍵片段：`image: tutum/hello-world`。注意：避免與其他服務 port 衝突。最佳實踐：用此服務驗證 LB 與調度是否正常（會顯示容器 id）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q11

Q6: 如何為服務 Scale Out 至 3 個實例？
- A簡: 進入 Service 頁面，將 Scale 設為 3，Rancher 將自動啟動新容器並分散於不同 Host。
- A詳: 步驟：1) 開啟目標 Service；2) 調整 Scale=3；3) 觀察三個實例在不同 Host 啟動；4) 測試可用性。注意：確保資源足夠與配額允許；擔心單點時確認已跨主機分散。最佳實踐：搭配 LB 暴露統一入口、觀測延遲與 CPU 使用，必要時再加節點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q7

Q7: 如何建立並設定 Rancher 內建 Load Balancer？
- A簡: 在 Stack 內新增 Load Balancer，指定前端 Port 與目標 Service，即可對外分流。
- A詳: 步驟：1) 回到 Stack > Add Service > Load Balancer；2) 設定 Listen Port（如 80）與 Target Services（選 hello-world）；3) 建立後以 LB 的 IP:Port 測試多次刷新，應輪流顯示不同容器 id；4) 需要進階行為時加入 HAProxy 設定片段。注意：開放安全群組/防火牆。最佳實踐：設定健康檢查與限流，提升穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q8

Q8: 如何對服務執行 In-Service Upgrade？
- A簡: 在 Service 選 Upgrade，調整映像或設定，配置批次大小/間隔與啟停順序，執行升級。
- A詳: 步驟：1) 開啟 Service > Upgrade；2) 調整 `image` 版本或環境/port/volumes；3) 設定 Batch Size、Batch Interval、Start before stopping；4) 執行並觀測新實例啟動、舊實例停止；5) 驗證後按 Finish。注意：Batch 需小於副本數以保可用；先啟後停較安全。最佳實踐：升級前備份資料卷與配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q6, B-Q13

Q9: 如何執行升級 Rollback 並恢復服務？
- A簡: 升級有誤時按 Rollback，Rancher 會停掉新容器、刪除資源並重啟舊容器。
- A詳: 步驟：1) 升級失敗或驗證不通過時點擊 Rollback；2) 觀察新實例被停止/移除；3) 舊實例回到 Running；4) 再次驗證服務；5) 修正組態後再試一次升級。注意：確保舊版本映像仍可拉取、資料卷未破壞。最佳實踐：在非高峰時操作，設監控告警與審核流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q7

Q10: 如何用 Rancher 佈署 WordPress（Web+DB+LB）？
- A簡: 建立 Stack，定義 web 與 db 兩個 Service，web 連 db；再建立 LB 指向 web 實例。
- A詳: 步驟：1) 新建 Stack；2) Compose 片段：`web: image: wordpress; ports: ["80:80"]; environment: WORDPRESS_DB_HOST=db; db: image: mysql:5.7; environment: MYSQL_ROOT_PASSWORD=...; volumes: ["db-data:/var/lib/mysql"]`；3) 先起 DB 再起 Web；4) 新增 LB 指向 web；5) 視需要 Scale web。注意：持久化 DB、設定強密碼與備份。最佳實踐：用 LB 對外，web 可多副本，db 單副本並妥善存儲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q8, A-Q12

### Q&A 類別 D: 問題解決類

Q1: 連不到 http://{ip}:8080，Rancher Server 啟不來怎麼辦？
- A簡: 等待初始化、確認容器狀態與主機資源，檢查防火牆與映射 Port 是否正確。
- A詳: 症狀：8080 無響應或連線被拒。可能原因：Server 容器尚在初始化（需 1–2 分鐘）、主機 RAM 不足、Docker Daemon 異常、未映射 8080、被防火牆阻擋。解決：`docker ps`/`logs` 檢查狀態；提高 RAM 至≥2GB；確認 `-p 8080:8080`；開放安全群組；重啟容器/主機。預防：專用主機承載、開機自啟、監控健康。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, A-Q19

Q2: Add Host 後長時間顯示 Waiting/Disconnected？
- A簡: 檢查 Agent 指令與 Token、Server/Host 網路互通、時間同步與防火牆設定。
- A詳: 症狀：Host 卡在 Waiting 或斷線。原因：註冊 Token 過期/錯誤、Server 無法回連 Host、DNS/時間偏差、公司防火牆阻擋。解決：重複產生註冊指令、確認 Host 可解析/連線至 Server、同步 NTP、開放必要端口。預防：固定 Server DNS、記錄指令、設計可達網路路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q3

Q3: 容器沒有被分散，全部落在同一台 Host？
- A簡: 檢查主機資源是否足夠、調度約束設定與親和/反親和規則，必要時擴增主機。
- A詳: 症狀：Scale Out 後新實例仍在同主機。原因：其他 Host 資源不足、調度策略/約束導致、Host 被標記不可調度。解決：釋放/增加資源、檢視服務約束規則、校正 Host 標籤與可調度狀態。預防：部署前規劃容量、設定反親和避免同主機共置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q6

Q4: 負載平衡看起來未分流或回應 503？
- A簡: 核對目標服務健康、LB 規則/Port、健康檢查與安全群組，必要時檢視 HAProxy 日誌。
- A詳: 症狀：總打到同實例或 503。原因：後端健康檢查失敗、LB 指向錯誤服務/Port、HAProxy 規則不符、Port 未開放。解決：確認後端實例健康、檢查 LB 目標與端口、打開安全群組、複查進階設定、查看 HAProxy logs。預防：設定健康檢查、版本控管 LB 配置、灰度驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q7

Q5: In-Service Upgrade 時出現短暫中斷？
- A簡: 調小 Batch、增加間隔、啟用先起後停，並用 LB 與健康檢查保護切換。
- A詳: 症狀：升級瞬間部分請求失敗。原因：Batch 太大、先停後起、健康檢查未啟。解決：設定 Start-before-stopping、Batch < 副本數、增加 Batch Interval、啟用健康檢查、確保 LB 正確移除不健康目標。預防：於低峰升級、預熱新版本、建立演練流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q13, C-Q8

Q6: 升級後卡在 Upgraded 無法 Finish？
- A簡: 驗證功能正常後點 Finish；若清理卡住，檢查舊容器/卷占用與權限。
- A詳: 症狀：狀態長期停在 Upgraded。原因：尚未按 Finish、或清理舊容器/資源失敗。解決：完成驗證後按 Finish Upgrade；若清理失敗，檢查舊容器依賴（卷/鎖）、手動移除阻塞；查看日誌。預防：設計升級核對清單、避免在升級中做非相關變更。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, B-Q12

Q7: Rollback 後舊容器啟動失敗？
- A簡: 檢查舊映像仍可用、配置與卷未破壞，修正後再觸發啟動或重建舊版本。
- A詳: 症狀：回滾後舊容器起不來。原因：舊映像被刪、環境變數/卷結構變更不相容、Port 衝突。解決：重新拉取舊映像、還原配置、修正卷相容性；必要時以舊 Compose 重建；釐清 Port 使用。預防：升級前保留舊映像與配置快照、資料結構遷移可回退。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q9

Q8: Azure 建立 Hosts 失敗或顯示認證錯誤？
- A簡: 檢查訂閱憑證/權限、資源配額、網路/位置設定與 SSH key 格式是否正確。
- A詳: 症狀：一鍵建機失敗、報認證/配額錯。原因：憑證錯誤或權限不足、區域配額用盡、VNet/子網不合法、SSH key 格式不符。解決：更新認證、調整區域或申請配額、修正網路設定、用正確 OpenSSH 公鑰。預防：事先驗證 API 權限與配額、用資源標籤管理成本與清理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q4

Q9: 監控儀表板沒有顯示 CPU/RAM 數據？
- A簡: 檢查 Agent 是否運行、版本相容、權限與時間同步，並確認瀏覽器/網路無阻擋。
- A詳: 症狀：Host/容器指標為 0 或空白。原因：Agent 未啟動/斷線、版本不相容、主機權限不足、時間漂移大。解決：重啟 Agent、校正版本、提升權限、同步 NTP；檢查網路與瀏覽器。預防：監控 Agent 健康、標準化鏡像與版本、落實時間同步。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, B-Q15

Q10: 預設無密碼導致安全風險，如何防範？
- A簡: 立即啟用身份驗證、封鎖公網直連、使用 TLS/反向代理與最小權限原則。
- A詳: 症狀：任何人可開啟 UI 操作。風險：未授權變更、資料外洩。解決：啟用內建認證（整合 LDAP/OAuth）、限制來源 IP、以反向代理（TLS）對外、僅開放必要端口、隔離管理面。預防：強密碼/MFA、定期更新、審計日誌、最小權限與網段隔離策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, C-Q2

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Rancher？
    - A-Q2: 什麼是 Docker Cluster？
    - A-Q3: 什麼是 Rancher OS？
    - A-Q9: Rancher 的 Environment 是什麼？
    - A-Q10: Stack、Service、Container、Host（Node）分別是什麼？
    - A-Q12: 為什麼需要 Load Balancer 在容器架構中？
    - A-Q14: Rancher 提供哪些資源監控與儀表板？
    - A-Q16: 什麼是 Scale Out？在 Rancher 中的意義？
    - A-Q19: Rancher Server 的建議資源規格與特性？
    - A-Q20: Rancher 的安全性預設與建議做法？
    - C-Q2: 如何啟動 Rancher Server 容器並登入？
    - C-Q3: 如何建立 Local Environment 並新增三台 Host？
    - C-Q5: 如何建立 Stack 並部署 tutum/hello-world？
    - C-Q6: 如何為服務 Scale Out 至 3 個實例？
    - D-Q1: 連不到 http://{ip}:8080，Rancher Server 啟不來怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q4: 為什麼選擇 Rancher 作為容器管理平台？
    - A-Q7: 什麼是 Cattle（Rancher 的編排引擎）？
    - A-Q8: Docker Swarm、Mesos、Kubernetes 的差異？
    - A-Q11: 什麼是 In-Service Upgrade？
    - A-Q13: Rancher 內建 Load Balancer 與 HAProxy 的關係？
    - A-Q17: 什麼是零停機升級？如何在 Rancher 達成？
    - A-Q18: 為何要同時使用 Local 與 Azure 兩個 Environment？
    - B-Q1: Rancher Server 如何運作？架構與角色
    - B-Q3: Rancher 如何把 Host 加入管理？註冊流程
    - B-Q5: Stack/Service 是如何映射為容器與網路的？
    - B-Q6: In-Service Upgrade 的執行流程與機制？
    - B-Q7: Scale 與排程：Rancher 如何把容器分散至不同 Host？
    - B-Q8: 內建 Load Balancer 如何分流？背後機制
    - B-Q11: Rancher Compose 與 Docker Compose 的關係？
    - C-Q7: 如何建立並設定 Rancher 內建 Load Balancer？
    - C-Q8: 如何對服務執行 In-Service Upgrade？
    - C-Q9: 如何執行升級 Rollback 並恢復服務？
    - D-Q2: Add Host 後長時間顯示 Waiting/Disconnected？
    - D-Q4: 負載平衡看起來未分流或回應 503？
    - D-Q5: In-Service Upgrade 時出現短暫中斷？

- 高級者：建議關注哪 15 題
    - A-Q22: Rancher 與 Azure Cloud Service 的升級機制比較？
    - B-Q2: Rancher OS 如何運作？PID 1 與系統容器
    - B-Q4: Environment 的隔離機制如何設計？
    - B-Q9: Rancher 與 Azure 整合如何自動建立主機？
    - B-Q10: Rancher 的資源監控數據如何收集與呈現？
    - B-Q13: Start-before-stopping 對服務可用性的影響？
    - B-Q15: 容器資源統計（CPU/RAM/Disk/Net）的核心元件？
    - B-Q16: HAProxy 進階設定如何注入到 LB？
    - B-Q17: Azure Container Service 建置 Swarm 的流程與限制
    - B-Q18: Rancher 的服務連結與服務發現如何運作？
    - C-Q4: 如何在 Azure 以 Rancher 自動建立 Hosts？
    - C-Q10: 如何用 Rancher 佈署 WordPress（Web+DB+LB）？
    - D-Q7: Rollback 後舊容器啟動失敗？
    - D-Q8: Azure 建立 Hosts 失敗或顯示認證錯誤？
    - D-Q10: 預設無密碼導致安全風險，如何防範？