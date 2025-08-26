# Azure Labs: Windows Container Swarm

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Docker Swarm？
- A簡: Docker 原生的容器編排系統，透過 Manager/Worker 節點管理服務與任務，支援擴縮容、滾動更新與高可用。
- A詳: Docker Swarm 是 Docker 內建的容器編排解決方案。它把多台主機組成叢集（Swarm），由 Manager 節點負責排程與狀態維護，Worker 節點執行實際容器任務。開發者以 Service 定義期望狀態，如副本數、網路與連接埠，Swarm 負責分散部署、故障重試與縮放。特點是與 Docker CLI/Engine 一致、上手快、維運簡單；適合中小型叢集、快速 PoC 及與現有 Docker 工作流程整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q8, B-Q1

A-Q2: 什麼是 Windows Container？
- A簡: 在 Windows Server 核心上運行的容器格式，封裝應用與依賴，與 Linux 容器共享類似生態但功能推出較慢。
- A詳: Windows Container 是建立在 Windows Server 內核上的容器技術，將應用程式及其依賴封裝於 image，透過 Docker 指令運行。其優勢是對 .NET Framework、IIS 等 Windows 生態支援良好，並可沿用 Docker 工作流程與 Registry。文章指出 Windows 容器功能推出節奏相對 Linux 慢，如當時未支援 Routing Mesh；適用於需要 Windows 執行環境、企業內部系統遷移或混合叢集場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q13, B-Q3

A-Q3: 為什麼在 Azure 上建置 Swarm？
- A簡: Azure 提供現成映像、快速佈建與託管服務，可省去 OS 安裝設定，加速體驗與驗證。
- A詳: 選擇 Azure 的原因在於佈建效率與服務整合：可直接使用「Windows Server 2016 Datacenter - with Containers」映像省去安裝與設定，3 台 VM 幾分鐘可就緒；同時 Azure 提供私有 Registry（ACR）、Web App for Containers 與 ACI 等服務，便於打造從映像管理到運行的完整流程。對於只需短時間做實驗、PoC 或內網場景，也能以最低成本快速搭環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q1, C-Q6

A-Q4: 什麼是 Azure Container Registry（ACR）？
- A簡: Azure 託管的 Docker 私有映像倉庫，按儲存用量計費，支援推送/拉取與存取控制，便於企業私有化管理。
- A詳: ACR 是 Azure 提供的 Docker 相容私有 Registry。文章強調其「服務不額外收費、按 Storage 用量付費」的優勢，對剛起步的團隊幾乎零門檻。ACR 支援標準 Docker 指令推送/拉取、存取金鑰與 Admin User 驗證，適用於私有映像集中管理、權限控管與叢集多節點快速拉取，特別是在 Swarm 中每個節點需各自拉取映像時更顯價值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, D-Q5

A-Q5: 什麼是 Azure Container Service（ACS）？
- A簡: Azure 的容器編排服務（當時），支援 Swarm/DC/OS/Kubernetes，Windows 容器支援仍屬預覽。
- A詳: 文章撰寫時，ACS 是 Azure 上的容器編排服務門面，支援多種編排器（Swarm、DC/OS、Kubernetes），可一鍵佈建。但作者指出 ACS 對 Windows Container 的支援仍在 Preview，因此選擇自行在 VM 上搭建 Swarm。對想快速體驗編排又不願自行安裝設定者，ACS 提供便捷選項；若遇到平台對 Windows 容器支援限制，自行部署仍是可行方案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, C-Q1

A-Q6: 什麼是 Azure Container Instances（ACI）？
- A簡: 將容器視為輕量 VM 的即用即付運算服務，提供免管理主機、快速啟動的單容器運行環境。
- A詳: ACI 是 Azure 的「容器即服務」，使用者準備好映像即可直接啟動容器，無需管理 VM 或叢集。文章建議把 ACI 想成「超高效率 VM」更好理解：單容器或少量容器、短作業、事件驅動工作負載等皆適合。雖不屬於編排器，但能與 ACR 等周邊服務形成輕量級部署方案，搭配 Swarm/K8s 則可作為輔助運算資源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q3

A-Q7: Swarm 的 Manager 與 Worker 有何差異？
- A簡: Manager 負責排程、狀態與資源分配；Worker 接受指派執行任務。Manager 亦可執行任務。
- A詳: 在 Swarm 中，Manager 節點維護叢集期望狀態、進行排程與協調，並持有加入 Token；Worker 節點專注執行任務（Tasks）。初次建立叢集時第一台為 Manager，之後可加入更多 Workers。服務模式為 global 時，每節點（含 Manager）各跑一個實例；replicated 則由 Manager 依副本數與資源情況分配到部分節點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q10, C-Q4

A-Q8: 什麼是 Swarm 的 Service？
- A簡: Service 是期望狀態的抽象，定義映像、網路、連接埠與副本數，由 Swarm 轉為實際容器任務。
- A詳: Service 是 Swarm 的核心抽象，描述要運行的映像與對應設定（環境變數、網路、發布連接埠、模式與副本數）。Manager 依 Service 期望狀態建立 Tasks，在各節點啟動容器並維持健康。這與單機 Docker 的「docker run 一次啟動一容器」不同，Service 支援自動恢復、擴縮與跨節點分散，更適合生產與多機部署。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q10, C-Q6

A-Q9: docker run 與 docker service create 有何差異？
- A簡: docker run 建單機容器；service create 建叢集服務，交由 Swarm 排程與維持期望狀態。
- A詳: docker run 直接在單一 Docker 主機啟動一個容器，參數如 -p、-e、--name 作用於該主機。docker service create 則宣告服務形態，Swarm Manager 會在叢集內安排任務、維護副本、處理重啟與擴縮。連接埠發布語意也不同：service 的 -p 牽涉到叢集網路（如 ingress 與 routing mesh 或 host 模式），需理解平台支援差異。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q4, A-Q16

A-Q10: global 與 replicated 模式的差異？
- A簡: global 為每節點一實例；replicated 依指定副本數分散到部分節點，由 Manager 排程。
- A詳: global 模式適合節點常駐代理、監控探針等需求，每新增節點即自動跑一份。replicated 模式則指定副本數（--replicas N），Manager 按資源與健康情況分配至部分節點。兩者影響網路發布與負載策略：global 常與 host 發布做一對一映射；replicated 通常期待由 Mesh/LB 聚合。Windows 當時尚未支援 Mesh，需調整策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, A-Q16

A-Q11: 什麼是 Overlay Network 與 ingress？
- A簡: Overlay 是跨主機虛擬網路；ingress 是 Swarm 初始化時的共用 overlay，用於服務對外與跨節點通訊。
- A詳: 單機 Docker 常用 NAT，不跨主機。Swarm 需跨主機通訊，故建立 Overlay Network 疊加於實體網路，提供跨節點容器互通。Swarm init 會自動建立 ingress Overlay，作為預設服務通道與對外發布基礎。此網路讓服務實例能互聯並配合內建 DNS 與（在支援平台）Routing Mesh 實現彈性流量分配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q9, A-Q17

A-Q12: 什麼是 Routing Mesh？
- A簡: 將已發布連接埠統一入口，透過內建負載均衡把流量分配至各實例；當時 Windows 尚未支援。
- A詳: Routing Mesh 是 Swarm 的對外入口機制，所有節點在指定連接埠接收流量，並由內部負載均衡轉送至任一服務實例，達成單一對外位址與彈性擴縮。文章引述官方說明：Windows 主機當時尚未支援 Mesh，僅支援 DNSRR 策略；因此預設 -p 在 Windows 上無法達到 Mesh 行為，需改為 host 模式或外部 LB。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q9, A-Q16

A-Q13: 什麼是 DNS Round Robin（DNSRR）？
- A簡: 透過 Docker 內建 DNS 回應多個實例 IP，客戶端以輪詢方式連線；Windows 當時僅支援此策略。
- A詳: DNSRR 是 Swarm 的一種服務端點分配策略，解析服務名稱時回傳多個容器 IP，客戶端輪詢達成簡單負載分散。官方文件指出 Windows 主機僅支援 DNSRR，不支援 Mesh。作者依文件測試仍無法在容器內以服務名解析出多 IP，顯示當時實作仍有落差，實務上可先採外部負載均衡替代。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q4, A-Q12

A-Q14: 為何要使用私有 Registry（ACR）而非 Docker Hub？
- A簡: 控管權限、靠近叢集節點提升拉取速度，適合團隊維運與多節點部署。
- A詳: 在 Swarm 中，每個節點都需獨立拉取映像。使用 ACR 可帶來更穩定的頻寬與接近性，減少多節點同時拉取的延遲；同時可集中管理私有映像與權限，避免公開倉庫風險。文章也提到 ACR 僅依儲存用量計費，成本友善，非常適合自研映像與企業內部部署。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, D-Q9

A-Q15: 為什麼部署到叢集需要 --with-registry-auth？
- A簡: 用於把 Registry 認證一併傳遞給排程任務，讓各節點能授權拉取私有映像。
- A詳: 將 Service 部署到 Swarm 時，實際拉取映像的是各節點。若映像位於私有 Registry（如 ACR），節點端需具備授權。--with-registry-auth 會將當前 CLI 的授權隨 Service 建立一併傳遞，使節點能順利拉取，避免「no basic auth credentials」錯誤。搭配事先於每節點 docker login 可提高成功率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, C-Q6, C-Q3

A-Q16: 發布連接埠的 mode=host 與預設差異？
- A簡: 預設期望 Mesh；host 模式改為各節點本機映射，無跨節點負載均衡。
- A詳: service create 的 --publish 預設語意會借助 Mesh 做統一入口。但因 Windows 當時不支援 Mesh，需明確指定 mode=host，使各節點直接將已發布連接埠映射到本機上的該容器。此作法一對一、無負載均衡，瀏覽節點 IP 會固定命中本節點實例。若需 LB，須外接如 NGINX/雲端 LB。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q12, D-Q2

A-Q17: NAT 與 Overlay 網路有何差別？
- A簡: NAT 僅限單機容器互通；Overlay 橫跨多主機，提供叢集內容器彼此通訊能力。
- A詳: 單機 Docker 預設使用 NAT，容器彼此以私網互通，對外需 -p 映射。Swarm 跨多主機時，NAT 無法跨機連通，因此需 Overlay Network 疊加於實體網路之上，讓叢集中容器跨節點溝通。Swarm 會建立 ingress overlay 支援服務發布、服務間通訊與（在支援平台）名稱解析策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, C-Q8

A-Q18: 為何容器編排是必要技能？
- A簡: 當部署主機超過一台，需排程、擴縮、復原與網路治理，編排可系統化處理並提升穩定性。
- A詳: 當應用需橫向擴展或多機部署，單機 Docker 已不足以處理節點選擇、故障恢復、滾動更新與跨機網路等需求。Swarm 等編排工具將期望狀態化、擴縮自動化、故障自我修復並統一服務入口。即便將來採其他編排器（如 Kubernetes），Swarm 的概念與操作對建立整體心智模型仍非常有幫助。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q8, B-Q5


### Q&A 類別 B: 技術原理類

B-Q1: Swarm 初始化（init）與加入（join）如何運作？
- A簡: init 建立叢集與 Manager，產生 Token；join 以 Token 與地址加入為 Worker 或 Manager。
- A詳: docker swarm init 在第一台主機建立叢集、指定 --advertise-addr（廣播本機私 IP）與 --listen-addr:2377（管理通訊埠），產生 SWMTKN Token。其他節點以 docker swarm join 搭配 Manager 位址與 Token 加入，多數情況加入為 Worker。核心組件含：Manager（排程/狀態）、Worker（執行任務）、Raft 狀態儲存（僅概念）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q5, A-Q7

B-Q2: ACR 驗證在 Swarm 中如何運作？
- A簡: 節點需授權拉取映像。先在各節點 docker login，再以 --with-registry-auth 傳遞憑證。
- A詳: 映像拉取發生在執行任務的節點，因此節點端必須能對 ACR 驗證。常見流程：於每個節點 docker login {registry}，建立憑證快取；建立 Service 時加上 --with-registry-auth，將 CLI 認證一併傳遞給排程工作，使節點能成功拉取私有映像。若缺認證，將報「no basic auth credentials」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, C-Q3, C-Q6

B-Q3: Windows 上為何預設 -p 無法對外？
- A簡: 預設 -p 期望 Mesh 行為；Windows 當時未支援 Routing Mesh，導致無對外效果。
- A詳: service create -p 在支援 Mesh 的平台會於所有節點打開該埠並以內建 LB 分流至任務實例。文章指出 Windows 主機尚未支援 Mesh，僅支援 DNSRR，故預設 -p 無法達到預期的對外連通。需改用 --publish mode=host, target=..., published=... 直接將節點本機埠映射到容器埠。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q16, D-Q2

B-Q4: Swarm 的連接埠發布流程為何？
- A簡: 預設以叢集入口發布；Windows 需改 host 模式，由各節點本地埠直連本地容器。
- A詳: 在支援 Mesh 的平台，發布埠會在所有節點開啟，再由內建代理轉送到任務所在節點。Windows 不支援 Mesh 時，指定 mode=host 後，每節點只向本地映射，形成「節點 IP + 埠」直達該節點的實例。核心組件：Service、Tasks、ingress/自建 overlay 及（可用時）內建代理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q12, D-Q2

B-Q5: global 模式的排程機制是什麼？
- A簡: Manager 確保每節點恆有一個任務實例，新節點加入自動部署一份。
- A詳: global 服務會在叢集中每個節點（含 Manager）各分配一個任務。當節點加入或離開時，Manager 自動調整，確保期望狀態。此模式適合節點本地代理、日誌收集與監控探針，也與 host 發布模式相性良好，形成一對一映射。若實例失敗，Manager 會在該節點重建任務。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q6, D-Q3

B-Q6: replicated 模式的排程流程是什麼？
- A簡: 依 --replicas 指定數量，Manager 分散到若干節點並維持數量，支持擴縮。
- A詳: replicated 模式下，Manager 根據副本數、節點資源與健康狀態，挑選節點放置任務。擴縮即改變副本數，Manager 即時調整。若配合 Mesh 或外部 LB，可將對外連線聚合。Windows 因無 Mesh，常需外接負載平衡並搭配 publish-port 模式。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q12, B-Q17

B-Q7: ingress Overlay 的角色與機制？
- A簡: Swarm 自動建立的跨節點虛擬網路，承載服務間通訊與對外發布的基礎。
- A詳: 初始化 Swarm 時建立的 ingress overlay 提供跨節點 L3 連通，使服務實例互相可達。它也作為服務對外發布的骨幹（在支援平台承載 Mesh）。關鍵組件包含節點上的虛擬網路裝置、控制平面分配的網段與內建 DNS。Windows 當時 Mesh 不可用，但 overlay 仍提供跨機容器互通。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q9, C-Q8

B-Q8: Docker 內建 DNS 與 DNSRR 如何工作？
- A簡: 內建 DNS 解析服務名至實例 IP；DNSRR 回傳多筆 IP 供輪詢。作者實測 Windows 尚不穩。
- A詳: 內建 DNS 讓容器以服務名尋址對方，DNSRR 策略會回多筆 A 記錄供客戶端輪詢，達成基本分流。官方稱 Windows 僅支援 DNSRR，但作者實驗在 console 容器 nslookup 服務名無法得到多 IP，顯示當時支援仍有限。實務上可先以外部 LB 搭配 host 發布因應。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, D-Q4, C-Q8

B-Q9: Routing Mesh 的原理是什麼？
- A簡: 於所有節點開入口埠，內建代理把連線導至任意健康實例，統一入口與彈性擴縮。
- A詳: Mesh 讓「任何節點的已發布埠」都能存取服務，內部以代理/負載演算法選擇目標實例，簡化客戶端設定與擴縮策略。在 Linux 已成熟；Windows 當時未支援。因此若企圖使用預設 -p 實現 Mesh，在 Windows 將無效，必須改用 host 發布或外部 LB。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q4, D-Q2

B-Q10: 服務、任務、容器三者關係是？
- A簡: 服務定義期望狀態；任務是排程單元；容器是任務在節點上實際運行的實體。
- A詳: 在 Swarm 中，Service 是宣告式定義；Manager 將其拆成 Tasks，並排程到節點；每個 Task 在節點上對應為一個容器。當容器失敗，Manager 會以 Task 為單位重建。理解此關係有助於解讀 docker service ps 的輸出與故障排除。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q5, D-Q3

B-Q11: Swarm 管理通訊如何設計？
- A簡: 以 --listen-addr 指定管理通道（預設 2377/TCP），--advertise-addr 宣告可被其他節點連線的位址。
- A詳: init 指令中的 --listen-addr 綁定管理通訊埠，其他節點透過該埠加入；--advertise-addr 告知集群其他節點用此私網位址連回 Manager。若設錯會導致 join 失敗或不穩。務必確保私網可達、NSG/防火牆允許通訊。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q4, D-Q6, D-Q8

B-Q12: 使用 --publish mode=host 後流量如何路由？
- A簡: 用戶連到節點公開埠，直接命中該節點本地容器；無跨節點代理或負載均衡。
- A詳: mode=host 會在各節點建立本機埠到容器埠的映射。這使得「節點 IP + 已發布埠」固定連到該節點上的服務實例。多實例時用戶需自行選擇節點地址，或透過外部負載均衡器彙總多個節點位址。優點是簡單、可預期；缺點是缺乏內建分流。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q2, B-Q4

B-Q13: ACR 成本與儲存模型的意涵？
- A簡: 以儲存用量計費，映像層可重複利用；初期未上傳內容幾近零成本。
- A詳: ACR 按映像層（Layers）占用的儲存空間計費，層可被多映像共享，能有效節省空間與費用。文章提到服務本身不額外收費，對起步與實驗非常友善。這也鼓勵團隊將自研映像集中到 ACR，提升多節點拉取效能與權限控管。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q3, D-Q9

B-Q14: 為何每個節點都需自行拉取映像？
- A簡: 任務在不同節點執行，映像需存在該節點本地，否則無法啟動容器。
- A詳: Swarm 的任務調度是分散的，任務可能被排到任一節點。Docker 會在該節點檢查映像是否存在，不存在則從 Registry 拉取。故使用高速、近端的 Registry（如 ACR）可縮短拉取時間，並確保副本快速擴縮。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q3, D-Q9

B-Q15: 如何解讀 docker service ls/ps 的輸出？
- A簡: ls 概覽服務；ps 顯示任務狀態（Running/Shutdown/Restarting）與所在節點、埠映射等。
- A詳: docker service ls 顯示服務名稱、模式、副本數與映像。docker service ps {service} 可見每個任務的節點、當前/期望狀態與原因碼。文章示例顯示某節點首次啟動失敗後重試成功，ps 中留有歷史紀錄，利於診斷不穩定與重啟行為。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q3, A-Q10

B-Q16: 在容器內測試網路連線的流程？
- A簡: 以 docker exec 進入容器，使用 ping/nslookup 測試 IP 或服務名解析與互通性。
- A詳: 建立一個 console 類服務（如 windowsservercore 持續 ping），以 docker exec -it 進入 cmd。可用 ping 測試跨節點 IP 可達性、nslookup 測試 Docker 內建 DNS 的服務名解析。文章中 IP 互通正常，但服務名解析多 IP 未成功，提示 Windows 當時 DNSRR 實作限制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q4, B-Q8

B-Q17: 外部負載均衡如何與 Swarm 結合？
- A簡: 將各節點 host 模式公開的埠後端，交由外部 LB（如 NGINX）彙總做分流。
- A詳: 因 Windows 不支援 Mesh，可將服務以 host 模式發布（各節點固定公開埠），再把這些「節點 IP:埠」配置到外部 LB 的後端池，上游以單一虛擬位址對外，達成分流與健檢。Docker 文件建議此法作為當前替代策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, A-Q16, D-Q4


### Q&A 類別 C: 實作應用類

C-Q1: 如何在 Azure 建立三台 Windows 2016（with Containers）VM？
- A簡: 於 Azure Portal 選用 Windows Server 2016 Datacenter - with Containers 映像，建立 wcs1~wcs3 三台 VM。
- A詳: 步驟：1) 登入 Azure，建立 Resource Group（如 wcsdemo）。2) 新增 VM，映像選「Windows Server 2016 Datacenter - with Containers」，尺寸選 Standard DS2 v2。3) 命名 wcs1、wcs2、wcs3，其他採預設。4) 佈建完成以 RDP 連線。注意：控制成本、確保內網可互通，日後記得開放 HTTP 80（Windows 防火牆/NSG）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q6, D-Q7

C-Q2: 如何建立 ACR 並啟用 Admin User？
- A簡: 新增 Azure Container Registry，完成後在 Access Keys 啟用 Admin User 並設定密碼。
- A詳: 步驟：1) 在 Azure Portal 新增服務搜尋「Azure Container Registry」。2) 命名（如 wcshub）、選區域與 RG，建立。3) 進入 ACR「Access Keys」，啟用 Admin User，設定密碼。注意：記下登入伺服器（wcshub.azurecr.io）與帳密，後續 docker login 使用；權限管理可依需求再細化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q3, D-Q5

C-Q3: 如何將 Docker Hub 映像推送至 ACR？
- A簡: docker login 至 ACR，pull 原映像、tag 為 {acr}/{repo}:{tag}，再 docker push。
- A詳: 範例命令：1) docker login -u {acrName} -p {pwd} {acrName}.azurecr.io。2) docker pull andrew0928/vs20:latest。3) docker tag andrew0928/vs20:latest {acr}.azurecr.io/vs20:latest。4) docker push {acr}.azurecr.io/vs20:latest。注意：tag 必須包含 ACR 登入伺服器前綴；確保本地與網路頻寬充足。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13, D-Q5

C-Q4: 如何初始化 Swarm Manager？
- A簡: 在第一台 VM 執行 docker swarm init，指定 --advertise-addr 與 --listen-addr:2377。
- A詳: 於 wcs1 執行：docker swarm init --advertise-addr <wcs1私IP> --listen-addr <wcs1私IP>:2377。成功後會輸出 join 指令與 SWMTKN。確保私網可達、NSG/防火牆允許 2377/TCP。保存 join 指令供其他節點使用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, D-Q8, C-Q5

C-Q5: 如何讓節點加入 Swarm？
- A簡: 在 wcs2、wcs3 執行 Manager 輸出的 docker swarm join 指令，帶上 Token 與 Manager 位址。
- A詳: 於 wcs2/wcs3 執行類似：docker swarm join --token <SWMTKN...> <managerIP>:2377。終端顯示「This node joined a swarm as a worker.」即成功。若遺失 Token，可於 Manager 查詢 join-token。確保私網連通與位址正確。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, D-Q6, D-Q8

C-Q6: 如何在 Windows Swarm 部署能對外的 Web 服務？
- A簡: 先於各節點 docker login ACR，再以 --with-registry-auth 與 --publish mode=host 建立服務。
- A詳: 指令：docker service create --name mvcdemo --with-registry-auth --mode global --publish mode=host,target=80,published=80 {acr}.azurecr.io/vs20:latest。注意：1) 先在 wcs1~wcs3 分別 docker login。2) 使用 host 發布避免 Windows Mesh 限制。3) 開放 80 入站（VM 防火牆/NSG）。4) 以各節點公網 IP:80 測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q12, D-Q2

C-Q7: 如何查驗服務與任務狀態？
- A簡: 用 docker service ls 檢查服務清單，docker service ps {svc} 觀察任務節點與狀態。
- A詳: 常用：1) docker service ls；2) docker service ps mvcdemo；3) docker ps -a（節點本地容器）。若任務失敗會顯示 Shutdown 並重試新任務。也可 docker service inspect 或 logs（容器層級）輔助診斷。對外測試以瀏覽器連各節點公開埠驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q15, D-Q3, C-Q6

C-Q8: 如何用 DNSRR 模式部署多副本服務？
- A簡: 指定 --endpoint-mode dnsrr 與 --replicas N，在同一 overlay 下嘗試以服務名解析多 IP。
- A詳: 範例：docker service create --name mvcdemo --with-registry-auth --network ingress --endpoint-mode dnsrr --replicas 5 {image}。驗證：以 console 容器 docker exec 進入，用 nslookup/ping 服務名測試。注意：作者實測當時 Windows 容器解析多 IP 不穩，可能需改用外部 LB。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, D-Q4, B-Q7

C-Q9: 如何建立 Console 服務並在容器內測試連線？
- A簡: 建立簡單長駐服務，docker exec 進入容器以 ping/nslookup 測試對其他實例連通。
- A詳: 建立：docker service create --name console --network ingress --endpoint-mode dnsrr --replicas 3 microsoft/windowsservercore ping -t localhost。進入：docker exec -it <containerId> cmd。測試：ping <對方容器IP>、nslookup mvcdemo。注意：先查任務 IP，再測服務名解析；用於驗證 overlay 可達與 DNS 行為。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q16, B-Q7, C-Q8

C-Q10: 如何清理服務與環境以節省費用？
- A簡: 刪除服務、離開/關閉叢集並移除 Azure 資源，避免持續計費。
- A詳: 服務清理：docker service rm mvcdemo console。節點離開（Workers）：docker swarm leave；Manager：docker swarm leave --force。最後刪除 Azure VMs 與 ACR/Resource Group。注意：先備份必要映像與資料，再清理；避免遺留公開埠與存儲資源造成費用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q10, C-Q1, C-Q2


### Q&A 類別 D: 問題解決類

D-Q1: 建立服務時出現「no basic auth credentials」怎麼辦？
- A簡: 各節點先 docker login ACR，建立服務時加 --with-registry-auth 傳遞憑證。
- A詳: 症狀：service create 報「no basic auth credentials」。原因：節點無法存取私有 ACR。解法：1) 在 wcs1~wcs3 逐一 docker login {acr}.azurecr.io。2) 建立服務加 --with-registry-auth。3) 確認映像名稱含完整 ACR 前綴。預防：啟用 ACR Admin User，統一管理憑證與命名規則。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q3, C-Q6

D-Q2: 瀏覽器連不到服務的 80 埠怎麼辦？
- A簡: Windows 未支援 Mesh，改用 --publish mode=host；同時開放 VM/NSG 的 80 入站。
- A詳: 症狀：已建立服務但無法透過節點 IP:80 存取。原因：預設 -p 期待 Mesh（Windows 不支援），或防火牆/NSG 阻擋。解法：重建服務：--publish mode=host,target=80,published=80；同時開放 Windows 防火牆與 Azure NSG 的 80/TCP。預防：事先選定發布策略並檢查安全規則。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q3, C-Q6

D-Q3: 服務任務反覆重啟或出現兩筆紀錄怎麼辦？
- A簡: 透過 docker service ps 與容器 logs 檢查失敗原因，修正映像/設定後重試。
- A詳: 症狀：service ps 顯示某節點有 Shutdown 紀錄後又重新啟動。原因：映像啟動失敗、設定錯誤或資源不足。解法：1) docker service ps mvcdemo 查節點與任務；2) 到該節點 docker logs <container>；3) 修正映像環境變數/連接埠；4) 重建服務。預防：部署前本機驗證映像、縮小變更步幅。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q7, C-Q6

D-Q4: 在容器內無法用服務名稱解析其他實例怎麼辦？
- A簡: 確認同一 overlay 網路與 --endpoint-mode dnsrr；Windows 當時支援有限，可改外部 LB。
- A詳: 症狀：nslookup 服務名無多 IP 或不可解析。原因：未在同一 overlay、未使用 dnsrr、Windows 內建 DNS 實作限制。解法：1) 建立服務加 --network 同一 overlay 與 --endpoint-mode dnsrr；2) 以 IP 驗證可達；3) 如仍失敗，採外部 LB。預防：設計時預留外部 LB 方案，減少對內建 DNS 的依賴。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, C-Q8, B-Q16

D-Q5: 無法推送映像至 ACR 怎麼辦？
- A簡: 啟用 ACR Admin User，正確 docker login，並以含 ACR 前綴的 tag 再 push。
- A詳: 症狀：push 遭拒或找不到倉庫。原因：未啟用 Admin User、登入伺服器錯誤、tag 未含 {acr}.azurecr.io 前綴。解法：1) ACR 啟用 Admin User 並設密碼；2) docker login {acr}.azurecr.io；3) docker tag 原映像為 {acr}.azurecr.io/{repo}:{tag}；4) docker push。預防：建立一致的命名規範與推送流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, B-Q13

D-Q6: 節點加入 Swarm 失敗怎麼辦？
- A簡: 檢查 Token、Manager 位址與 2377/TCP 連通；必要時重新取得 join-token。
- A詳: 症狀：join 報錯或卡住。原因：Token 過期/錯誤、--advertise-addr 設錯、2377/TCP 被阻擋。解法：1) 在 Manager 重新取得 join 指令；2) 確認使用私網 IP；3) 檢查防火牆/NSG；4) 必要時重跑 init。預防：紀錄 join 指令、固定私網位址、在同一虛擬網路內部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q4, C-Q5

D-Q7: 防火牆阻擋導致服務不可達怎麼辦？
- A簡: 同時開放 Windows 防火牆與 Azure NSG 的公開埠（如 80/TCP）與管理埠。
- A詳: 症狀：節點埠對外不可連。原因：VM 作業系統防火牆或 Azure NSG 未允許入站。解法：1) 在 VM 開啟 80/TCP 入站；2) 在網卡/子網路的 NSG 新增允許規則；3) 驗證 2377/TCP 僅用於內網管理。預防：佈建時即套用正確安全群組與基線規則。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q6, B-Q11

D-Q8: 管理埠 2377 被阻擋導致叢集不穩怎麼辦？
- A簡: 確保節點間私網可達，放行 2377/TCP；避免暴露於公網。
- A詳: 症狀：節點離線、任務不排程。原因：Manager 與 Worker 間管理通道被防火牆/NSG 阻擋。解法：1) 放行私網 2377/TCP；2) 確認 --advertise-addr 為可達私 IP；3) 避免公網暴露管理埠。預防：在同一虛擬網路/子網部署，套用最小必要開放策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q4, C-Q5

D-Q9: 每個節點下載映像很慢怎麼辦？
- A簡: 使用近端 ACR、預熱常用映像、保持層共用；減少多節點併發瓶頸。
- A詳: 症狀：服務首次部署耗時長。原因：多節點從遠端公用 Registry 拉取大型映像。解法：1) 改用 ACR（區域相近）；2) 提前 pull 預熱；3) 瘦身映像、共用層；4) 避免不必要重複 tag。預防：建置管線將 push 到 ACR 作為標準步驟。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q14, C-Q3

D-Q10: 成本超支如何避免？
- A簡: 做完實驗即刪除服務與資源，或停止/移除 VM 與 ACR，避免持續計費。
- A詳: 症狀：測試後持續產生費用。原因：VM/存儲/公開資源未清理。解法：1) docker service rm；2) docker swarm leave；3) 刪除 VM/磁碟/ACR 或整個 Resource Group。預防：事先規劃 RG 一鍵清理、使用標籤管理資源、設定成本警示。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q10, C-Q1, C-Q2


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Docker Swarm？
    - A-Q2: 什麼是 Windows Container？
    - A-Q3: 為什麼在 Azure 上建置 Swarm？
    - A-Q4: 什麼是 Azure Container Registry（ACR）？
    - A-Q6: 什麼是 Azure Container Instances（ACI）？
    - A-Q7: Swarm 的 Manager 與 Worker 有何差異？
    - A-Q8: 什麼是 Swarm 的 Service？
    - A-Q9: docker run 與 docker service create 有何差異？
    - A-Q10: global 與 replicated 模式的差異？
    - A-Q11: 什麼是 Overlay Network 與 ingress？
    - C-Q1: 如何在 Azure 建立三台 Windows 2016（with Containers）VM？
    - C-Q2: 如何建立 ACR 並啟用 Admin User？
    - C-Q3: 如何將 Docker Hub 映像推送至 ACR？
    - C-Q4: 如何初始化 Swarm Manager？
    - C-Q5: 如何讓節點加入 Swarm？

- 中級者：建議學習哪 20 題
    - B-Q1: Swarm 初始化（init）與加入（join）如何運作？
    - B-Q2: ACR 驗證在 Swarm 中如何運作？
    - B-Q3: Windows 上為何預設 -p 無法對外？
    - B-Q4: Swarm 的連接埠發布流程為何？
    - B-Q5: global 模式的排程機制是什麼？
    - B-Q6: replicated 模式的排程流程是什麼？
    - B-Q7: ingress Overlay 的角色與機制？
    - B-Q10: 服務、任務、容器三者關係是？
    - C-Q6: 如何在 Windows Swarm 部署能對外的 Web 服務？
    - C-Q7: 如何查驗服務與任務狀態？
    - D-Q1: 建立服務時出現「no basic auth credentials」怎麼辦？
    - D-Q2: 瀏覽器連不到服務的 80 埠怎麼辦？
    - D-Q3: 服務任務反覆重啟或出現兩筆紀錄怎麼辦？
    - D-Q5: 無法推送映像至 ACR 怎麼辦？
    - D-Q6: 節點加入 Swarm 失敗怎麼辦？
    - D-Q7: 防火牆阻擋導致服務不可達怎麼辦？
    - A-Q14: 為何要使用私有 Registry（ACR）而非 Docker Hub？
    - A-Q15: 為什麼部署到叢集需要 --with-registry-auth？
    - A-Q16: 發布連接埠的 mode=host 與預設差異？
    - C-Q10: 如何清理服務與環境以節省費用？

- 高級者：建議關注哪 15 題
    - A-Q12: 什麼是 Routing Mesh？
    - A-Q13: 什麼是 DNS Round Robin（DNSRR）？
    - A-Q17: NAT 與 Overlay 網路有何差別？
    - B-Q8: Docker 內建 DNS 與 DNSRR 如何工作？
    - B-Q9: Routing Mesh 的原理是什麼？
    - B-Q11: Swarm 管理通訊如何設計？
    - B-Q12: 使用 --publish mode=host 後流量如何路由？
    - B-Q13: ACR 成本與儲存模型的意涵？
    - B-Q14: 為何每個節點都需自行拉取映像？
    - B-Q15: 如何解讀 docker service ls/ps 的輸出？
    - B-Q16: 在容器內測試網路連線的流程？
    - B-Q17: 外部負載均衡如何與 Swarm 結合？
    - C-Q8: 如何用 DNSRR 模式部署多副本服務？
    - C-Q9: 如何建立 Console 服務並在容器內測試連線？
    - D-Q4: 在容器內無法用服務名稱解析其他實例怎麼辦？