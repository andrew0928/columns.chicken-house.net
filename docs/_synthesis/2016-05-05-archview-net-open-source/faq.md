---
layout: synthesis
title: "[架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?"
synthesis_type: faq
source_post: /2016/05/05/archview-net-open-source/
redirect_from:
  - /2016/05/05/archview-net-open-source/faq/
postid: 2016-05-05-archview-net-open-source
---

# [架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是混搭架構（Polyglot/混合平台架構）？
- A簡: 混搭架構指在同一系統中選用不同平台與開源元件，各取所長以達成最佳效能、彈性與成本效益。
- A詳: 混搭架構是在一個系統內部有意識地採用多種平台、語言與開源元件，例如以 .NET 開發 Web 與服務層，並搭配 Linux 上的 Elasticsearch、Redis 與 HAProxy。其核心價值在於用最合適的技術解決特定子問題（搜尋、快取、負載平衡），在效能、穩定性與成本間取得更佳均衡。代價是增加跨平台整合、維運、監控與團隊技能的複雜度，需以容器化與自動化基礎建設來降低門檻。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, B-Q8, B-Q10

Q2: 為何 Stack Overflow 採用 .NET 搭配 Linux 組件？
- A簡: 以 .NET 擅長的 Web/服務層結合 Linux 強項的搜尋、快取與負載平衡，取長補短，滿足高流量需求。
- A詳: Stack Overflow 的核心 Web 與 Service 採 C#/.NET 與 SQL Server，因其開發效率高、工具鏈成熟；同時選用 Linux 上的 Elasticsearch（全文檢索）、Redis（快取）與 HAProxy（負載平衡），因這些在開源社群成熟度高、效能顯著。此混搭提升整體吞吐與穩定性，但也引入跨平台維運複雜度；透過標準化部署（容器化）、自動化與良好的團隊分工，可將複雜度控制在可管理範圍內。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, B-Q8, B-Q10

Q3: .NET Core 是什麼？與 .NET Framework 有何差異？
- A簡: .NET Core 為跨平台、開源的 .NET 執行環境與庫，能在 Windows、Linux、macOS 執行，與傳統 Framework 相分離。
- A詳: .NET Core 是微軟開源的跨平台 .NET 執行環境，包含 runtime、編譯器與基礎類別庫（BCL），支援 Windows、Linux、macOS。其特色是模組化、輕量、側邊部署與多目標（netcoreapp），適合容器化與微服務。與 .NET Framework（僅 Windows、龐大單體）不同，.NET Core 聚焦雲端與跨平台場景。對 .NET 開發者而言，能保留語言與工具優勢，同時拓展部署選擇。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2, C-Q9

Q4: 為什麼 .NET 開發者需要關注 Open Source？
- A簡: 開源元件在搜尋、快取、編排等領域領先，可與 .NET 結合，取得更高效能與更廣維運選擇。
- A詳: 現代系統常需全文檢索、快取、服務網格、容器編排等能力，這些領域多由開源方案領先（如 Elasticsearch、Redis、HAProxy、Docker、Swarm）。.NET 開發者透過 .NET Core 跨平台與容器化，可無痛採用這些元件，獲得優秀效能與更豐富的部署選項（Windows/Linux/雲端）。同時，開源社群的創新速度與透明度，能加速團隊學習與問題解決。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q10, B-Q11

Q5: 容器化（Docker）是什麼？核心價值為何？
- A簡: 容器以輕量隔離包裝應用與相依，提供可重現、可擴縮、可移植的部署單位，簡化跨環境一致性。
- A詳: Docker 容器透過作業系統層的隔離（namespaces/cgroups）封裝應用程式與相依，不需完整虛擬機即可快速啟動與高密度運行。映像分層與不可變特性確保部署可重現；標準化界面（Dockerfile、Compose）促進自動化、擴縮與滾動更新。對混搭架構尤為重要，因可將不同技術棧元件以一致方式運維，降低跨平台安裝配置成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, B-Q5, C-Q2

Q6: 微軟策略由平台轉向應用與服務，意味著什麼？
- A簡: 微軟從綁定平台轉為擁抱跨平台工具與服務，重心放在抓住開發者與雲端工作負載。
- A詳: Satya 之下，微軟不再以 Windows 平台鎖定開發者，而是開放 .NET Core、VS Code，支援 Linux、Mac；Visual Studio 支援跨平台開發（Xamarin、Cordova、Linux C++）。在雲端，Azure 提供多種 Linux 與開源服務樣板，重點是成為承載應用與資料的首選雲。對團隊而言，未來選型更聚焦問題解決，而非意識形態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q14, B-Q12

Q7: Windows 與 Linux 在伺服器端的典型分工差異？
- A簡: Windows 長於 .NET、生態整合；Linux 生態在搜尋、快取、代理與容器工具鏈資源豐富且成熟。
- A詳: Windows 擅長承載 .NET 應用、Active Directory、IIS 等企業整合，工具與 IDE（VS）一流；Linux 在開源資料基礎設施（Elasticsearch、Redis、Nginx/HAProxy）與容器工具（Docker、生態）成熟度高，資源與社群廣。混搭時可依強項分工，例如 Web/Service 在 .NET，搜尋/快取/負載平衡在 Linux，以達效能與運維最優化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, B-Q8

Q8: 什麼是反向代理與負載平衡（HAProxy/Nginx）？
- A簡: 反向代理位於前端接受請求並轉發，負載平衡將流量分散到多台服務，提升可用性與延展性。
- A詳: 反向代理（如 Nginx、HAProxy）位於客戶與後端服務間，負責 TLS 終結、路由、壓縮、快取與安全控制。負載平衡策略（輪詢、最少連線、健康檢查）將請求分散至多個實例，避免單點瓶頸並支援擴縮。對 .NET Core/Kestrel，常以反向代理承接外部流量，強化安全與效能，並作為流量治理入口。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q4, D-Q5

Q9: 為何選用 Redis 與 Elasticsearch 作為外掛式能力？
- A簡: 它們提供高效快取與全文檢索這兩類通用能力，成熟穩定，能與任意語言服務解耦整合。
- A詳: Redis 以記憶體資料結構提供極低延遲快取、佇列與分散式鎖；Elasticsearch 以倒排索引提供彈性全文檢索與聚合。兩者均為語言無關、標準協定的網路服務，可被 .NET、Java、Node 等整合。將搜尋與快取外部化，有助於微服務化、提升效能與可維護性，避免自行造輪子維護高成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, B-Q10, C-Q3

Q10: Visual Studio 與 VS Code 各自的角色與差異？
- A簡: VS 是全功能 IDE，適合大型 .NET 專案；VS Code 輕量跨平台編輯器，延伸性強，適合多語言與容器場景。
- A詳: Visual Studio 提供完整 .NET 工具鏈、設計器、偵錯、測試、分析，並整合 Xamarin、容器工具，適合企業級開發。VS Code 輕量、跨平台，透過擴充支援 C#、Docker、K8s、前端框架，啟動快、客製化強，適合容器化與混合語言開發。兩者互補，視團隊規模與平台選擇採用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q2, C-Q5

Q11: Windows 容器、Linux 容器與 Hyper-V 容器差異？
- A簡: Windows/ Linux 容器依 OS 內核相容，彼此不可互跑；Hyper-V 容器以輕量 VM 提供更強隔離。
- A詳: 容器共用主機 OS 內核，故 Windows 容器僅跑 Windows 映像，Linux 容器僅跑 Linux 映像；兩者不可互通用。Hyper-V 容器在 Windows 以輕量 VM 提供每容器隔離內核，能承載 Linux 容器工作負載（透過 LinuxKit），隔離強度更高但成本略增。選型取決於安全隔離、相容性與資源效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q7, D-Q3

Q12: WSL 與 Hyper-V 容器在混合環境中的定位？
- A簡: WSL 提供開發者本機 Linux 使用體驗；Hyper-V 容器則用於在 Windows 主機安全跑容器工作負載。
- A詳: WSL（Windows Subsystem for Linux）讓開發者在 Windows 上原生使用 Linux 使用者空間與工具鏈，適合開發、測試與腳本；其非完整內核隔離，不用於生產容器承載。Hyper-V 容器以輕量 VM 提供內核級隔離，能在 Windows 上安全執行 Linux 或 Windows 容器，適合生產工作負載。兩者場景不同但互補。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q5, D-Q8

Q13: Docker Swarm、Mesos、DC/OS 是什麼？差異為何？
- A簡: 三者皆為叢集編排平台；Swarm 輕量易用，Mesos/DC/OS 適合大規模與多工作負載調度。
- A詳: Docker Swarm 提供原生 Docker API 的叢集編排、服務與排程，學習曲線低；Mesos 是分散式資源管理核心，配 Marathon 等支援多框架（含容器與批次），擴展性強；DC/OS 為 Mesos 發行版，整合包管理與運維工具。小中型團隊首選 Swarm 或 Kubernetes，超大規模或多框架可考慮 Mesos/DC/OS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q11, C-Q8

Q14: Azure 在跨平台與開源生態中的定位是什麼？
- A簡: Azure 提供 Windows 與 Linux 等多樣基礎設施與開源服務樣板，成為應用託管的中立平台。
- A詳: Azure 已從僅支援 .NET 的雲，轉型為可建立 Linux VM、部署開源服務（如 Elastic、Redis）與容器工作負載的雲平台。目標是「任何語言、任何框架、任何平台」皆可在 Azure 上運行，並提供 DevOps、監控與安全服務。對混搭架構團隊，Azure 能作為一站式承載與治理平台。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q10, D-Q10

Q15: 遷移到 .NET Core 的戰略價值與潛在風險？
- A簡: 戰略上擴大跨平台與容器化能力；風險在相依差異、第三方支援度與升級成本。
- A詳: 遷移至 .NET Core 可獲跨平台部署、輕量化與容器友善優勢，讓團隊能採用最佳開源元件與混搭架構，並保持語言與工具鏈優勢。風險包括 API 差異、老舊相依套件不支援、部署與監控方式轉變、團隊技能需要更新。需以分段遷移、測試覆蓋、相依審核與藍綠部署降低風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, B-Q2, D-Q6


### Q&A 類別 B: 技術原理類

Q1: Stack Overflow（2016）混搭架構如何運作？
- A簡: .NET 服務與 SQL Server 為核心，外接 Linux 上的 Elasticsearch、Redis 與 HAProxy，前端負載與快取搜尋分離。
- A詳: 技術原理說明：Web 與 Service 層以 C#/.NET 提供主要業務能力，資料持久化於 SQL Server。關鍵步驟或流程：前端 HAProxy 進行 TLS 與負載，流量導向多台 Web；應用讀寫常用資料進 Redis 快取，複雜檢索委派 Elasticsearch；背景服務透過佇列或排程同步資料庫與索引。核心組件：.NET/IIS 或 Kestrel、SQL Server、Redis、Elasticsearch、HAProxy、AD（管理）。此切分達成可擴展與高可用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q8, B-Q10

Q2: .NET Core 跨平台運作的原理是什麼？
- A簡: 以開源 runtime、編譯器與 BCL 實現跨平台，結合 RyuJIT 與自託管伺服器 Kestrel，支援多 OS。
- A詳: 技術原理說明：.NET Core 提供跨平台 runtime（CoreCLR）、JIT（RyuJIT）、通用 BCL 與 SDK，統一語言功能。關鍵步驟：開發目標 netcoreapp TFM，編譯成 IL，於不同 OS 由對應 runtime 執行；Web 由 Kestrel 接管 HTTP，再由反代承接外部流量。核心組件：CoreCLR、RyuJIT、BCL、Kestrel、CLI（dotnet）。透過側邊部署與 RID targeting，實現可移植與自含發行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q2, C-Q9

Q3: 容器與虛擬機的隔離機制有何不同？
- A簡: 容器共享主機內核以 namespaces/cgroups 隔離；VM 透過虛擬化提供完整客體 OS 與更強隔離。
- A詳: 技術原理說明：容器使用 OS 層隔離，進程級封裝，啟動快、資源效率高；VM 則以 Hypervisor 提供虛擬硬體與客體內核。關鍵步驟：容器以映像分層組合 RootFS，啟動一個或多個行程；VM 啟動完整作業系統。核心組件：Docker Engine、containerd、Hyper-V/VMware/KVM。容器適合微服務與高密度，VM 適合強隔離與異質內核需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q11, D-Q3

Q4: Docker 映像建置與分層檔系統如何運作？
- A簡: 以 Dockerfile 指令逐層建置映像，每層快取與不可變，容器運行時疊加寫入層以保持輕量。
- A詳: 技術原理說明：映像由多層唯讀層（如 FROM、RUN、COPY）構成，使用疊層檔系統（Overlay2），容器運行時新增可寫層。關鍵步驟：Dockerfile 定義步驟，build 產生映像，push 到 Registry；run 時從映像建立容器。核心組件：Dockerfile、BuildKit、Registry、OverlayFS。分層與快取便於重用與快速建置，但需最佳化層順序與清理中繼檔以減少體積。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q3, D-Q7

B5: Docker Compose 如何定義與啟動多服務拓樸？
- A簡: 以 YAML 描述服務、網路、卷與相依，單一命令即可啟動多容器應用並管理其生命週期。
- A詳: 技術原理說明：Compose 使用 docker-compose.yml 定義多服務（image/build、ports、env、depends_on）、網路與卷。關鍵步驟：撰寫 YAML；docker-compose up 建置與啟動；scale 或 replicas 控制擴縮；down 清理資源。核心組件：Compose CLI、Docker Engine、Bridge/Overlay 網路。適合本機與小型叢集協調，讓應用一致可重現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q2, D-Q7

Q6: Docker Swarm 的排程與服務擴縮如何實現？
- A簡: Swarm 以 Raft 管理狀態，根據資源與限制在節點間排程任務，支援滾動更新與服務副本。
- A詳: 技術原理說明：Swarm Mode 將節點編成管理與工作節點，群集狀態以 Raft 複寫。關鍵步驟：docker service create 定義副本數與限制；排程器依節點資源、標籤與放置限制分配；支援 rolling update、healthcheck 與自我修復。核心組件：SwarmKit、Raft、Overlay Network、Service/Task。提供簡易而實用的原生編排能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q8, D-Q9

Q7: 在 Windows 上以 Hyper-V 隔離執行 Linux 容器的機制？
- A簡: 透過 Hyper-V 容器以輕量 VM 載入 LinuxKit 內核，為每容器提供獨立內核與更強隔離。
- A詳: 技術原理說明：Windows 上無法原生載入 Linux 內核，故以 Hyper-V 啟動精簡 VM（LinuxKit）承載 Linux 容器。關鍵步驟：Docker Desktop 啟用 Hyper-V/WSL2 後，建立隔離環境；每容器或節點級別提供內核隔離。核心組件：Hyper-V、LinuxKit、Docker Engine、gVisor/WSL2（視模式）。權衡隔離強度與啟動/資源成本。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q11, A-Q12, D-Q3

Q8: 反向代理/負載平衡（HAProxy）背後機制為何？
- A簡: 依據 L4/L7 規則分配請求，透過健康檢查、連線池與重試確保高可用與穩定吞吐。
- A詳: 技術原理說明：HAProxy 支援 L4（TCP）與 L7（HTTP）代理，基於路由規則選擇後端；維護連線池與 keep-alive。關鍵步驟：定義 frontend/backend、健康檢查、平衡策略（roundrobin、leastconn）、超時與重試；啟用 TLS 終結與 sticky sessions。核心組件：配置檔、stats、ACL、MAP。配合 Kestrel/ASP.NET 可提升安全與效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q4, D-Q5

Q9: Redis 快取的核心原理與常見使用模式？
- A簡: 以記憶體資料結構提供極低延遲存取，支援過期、發佈訂閱、鎖與副本，常用於快取與序列化。
- A詳: 技術原理說明：Redis 將鍵值與多種資料結構（String、Hash、List、Set、ZSet、HyperLogLog、Stream）存於記憶體，持久化以 AOF/RDB。關鍵步驟：設計快取鍵、TTL、淘汰策略；用作分散式鎖、排行榜、去重、訊息流。核心組件：主從、Sentinel、Cluster、Client Library（StackExchange.Redis）。與 .NET 易整合，顯著降低 DB 壓力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q3, D-Q2

Q10: Elasticsearch 索引與查詢的原理是什麼？
- A簡: 以倒排索引儲存詞項到文件映射，透過分片與副本分散資料，支援全文檢索與聚合。
- A詳: 技術原理說明：Elasticsearch 建立倒排索引，將文本分詞為詞項映射至文件，查詢時以布林/TF-IDF/BM25 計分。關鍵步驟：索引建立 Mapping、寫入文件、背景合併段；查詢解析、過濾、計分、聚合。核心組件：索引/型別（deprecated 概念）、分片/副本、Analyzer、Query DSL。適合內容搜尋與分析，與 .NET 透過 NEST 客戶端整合。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q9, C-Q3, D-Q2

Q11: Rancher 如何簡化容器編排與管理？
- A簡: Rancher 整合叢集管理、服務部署、網路與負載平衡，提供 UI/API 讓小團隊快速上手。
- A詳: 技術原理說明：Rancher 透過 Agent 管理節點，提供疊代的 orchestrator 支援（早期 Cattle、或整合 Swarm/K8s），內建 LB 與服務目錄。關鍵步驟：註冊節點、建立環境、部署 Stack/Service、設定升級策略。核心組件：Rancher Server、Agent、LB、Catalog。對入門團隊可大幅降低學習曲線與操作複雜度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q8, D-Q9

Q12: 在雲端（Azure）上管理容器服務的模式？
- A簡: 透過雲端提供的 VM、網路與托管編排服務快速建立叢集，整合監控、儲存與安全。
- A詳: 技術原理說明：使用 Azure 建立 VM/Scale Set 與虛擬網路，或採用托管容器服務（歷史 ACS、現代 AKS）。關鍵步驟：佈建運算資源、安裝 Docker/代理、配置編排（Swarm/AKS）、接入 Registry 與 Logs/Metrics。核心組件：VM、VNet、Load Balancer、Registry、Monitor/Sentinel。將基礎設施與治理功能外包給雲，縮短落地時間。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q10, D-Q10

Q13: .NET Core 容器化專案的 CI/CD 流程長怎樣？
- A簡: 程式碼提交觸發建置與測試，產生版本化映像推送登錄，再經藍綠/滾動策略部署到叢集。
- A詳: 技術原理說明：以 CI 工具（Azure DevOps、GitHub Actions）拉取程式碼，執行單元/整合測試與安全掃描；產生 Docker 映像並標記版本。關鍵步驟：build、test、scan、push、deploy；部署採藍綠或滾動更新並監控回饋。核心組件：CI/CD Pipeline、Dockerfile、Compose/Swarm/K8s、Registry。確保可重現與快速回滾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q3, D-Q10

Q14: 容器化的安全重點有哪些？
- A簡: 控制映像來源與漏洞、管理密鑰與權限、加固網路隔離與最小權限原則。
- A詳: 技術原理說明：供應鏈安全確保映像可信（簽章/掃描）；執行時限制權限與檔案系統；網路隔離與流量控管。關鍵步驟：使用官方/內部 Registry、漏洞掃描、Secrets 管理、非 root 執行、只讀檔案系統、安全組態（seccomp、capabilities）。核心組件：Registry/Notary、Scanner、Secrets、Network Policy。以預設安全態勢降低風險。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q10, C-Q2, B-Q4

Q15: 容器化 .NET 的觀測性該怎麼設計？
- A簡: 透過結構化日誌、度量與分散式追蹤三合一，串接集中化平台以支援定位與容量規劃。
- A詳: 技術原理說明：應用輸出結構化日誌（stdout），收集至集中系統；暴露 Prometheus/StatsD 指標；嵌入 OpenTelemetry 做追蹤。關鍵步驟：標準化日誌格式、關聯 request-id；建立儀表板與告警；壓測與基線。核心組件：ELK/EFK、Prometheus/Grafana、OpenTelemetry/Jaeger。讓跨服務的瓶頸與故障可觀測可追蹤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q6, D-Q9


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 Linux 上安裝 .NET Core 並執行範例？
- A簡: 使用套件管理安裝 SDK，執行 dotnet new/build/run 建立與啟動 ASP.NET Core 範例專案。
- A詳: 具體實作步驟：1) 安裝 SDK（以 Ubuntu 為例）sudo apt-get update; 安裝 Microsoft 套件來源後 sudo apt-get install dotnet-sdk-<版本>。2) 建立專案：dotnet new webapi -n Demo。3) 邏輯驗證：dotnet build；本機啟動：dotnet run。關鍵程式碼片段或設定：Program.cs 使用 Kestrel；appsettings.json 控制設定。注意事項與最佳實踐：版本釘住；使用 LTS；以非 root 執行；確認防火牆與開放埠。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2, A-Q3

Q2: 如何撰寫 ASP.NET Core 的 Dockerfile 並建置映像？
- A簡: 以多階段建置還原與發行，建立小體積 Runtime 映像，搭配環境變數與健康檢查。
- A詳: 具體實作步驟：撰寫 Dockerfile（多階段）。關鍵程式碼片段或設定： 
  - FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build 
  - WORKDIR /src; COPY . .; RUN dotnet restore; RUN dotnet publish -c Release -o /out 
  - FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS run 
  - WORKDIR /app; COPY --from=build /out . 
  - ENV ASPNETCORE_URLS=http://+:8080 
  - EXPOSE 8080 
  - HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1 
  - ENTRYPOINT ["dotnet","Demo.dll"]。注意：避免 COPY . . 帶入多餘檔案；使用 .dockerignore；釘住基底映像標籤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q14, D-Q7

Q3: 如何用 docker-compose 建立 Web + Redis 拓樸？
- A簡: 在 compose 檔定義兩服務與網路、環境變數與相依性，啟動後以服務名稱互連存取快取。
- A詳: 具體實作步驟：建立 docker-compose.yml。關鍵程式碼片段或設定： 
  - services: web: build: .; ports: - "8080:8080"; environment: REDIS__HOST=redis; depends_on: - redis 
  - redis: image: redis:6-alpine; command: redis-server --appendonly yes 
  - networks: default: driver: bridge。應用中使用連線字串 host=redis,port=6379。注意事項與最佳實踐：使用健康檢查；設定 restart: unless-stopped；資料持久化掛載卷；避免使用 latest 標籤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q9, D-Q2

Q4: 如何以 HAProxy 作為前端負載平衡 .NET 服務？
- A簡: 以 haproxy.cfg 定義前後端、TLS 與健康檢查，容器化後與後端服務同網路運行。
- A詳: 具體實作步驟：撰寫 haproxy.cfg；以官方映像運行。關鍵設定片段： 
  - global/maxconn 4096；defaults timeout connect 5s, client/server 50s 
  - frontend fe_http bind *:80; default_backend be_app 
  - backend be_app balance leastconn; option httpchk GET /health; server app1 web:8080 check。Docker 啟動：docker run -v ./haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg:ro --net <compose_net> -p 80:80 haproxy:alpine。注意：Kestrel 背後運行；啟用健康檢查；妥善處理 X-Forwarded-* 標頭。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q5, A-Q8

Q5: 如何在 Windows 使用 WSL 打造跨平台開發環境？
- A簡: 啟用 WSL 並安裝 Linux 發行版，在其中安裝 .NET SDK、Docker CLI 與工具鏈進行本機開發。
- A詳: 具體實作步驟：1) 啟用 WSL 與虛擬機平台，安裝 Ubuntu。2) 在 WSL 安裝 .NET SDK、Node、Git；3) 以 VS Code Remote WSL 連線開發。關鍵設定：wsl.exe --install；在 VS Code 安裝 Remote - WSL；設定行尾與路徑一致性。注意事項與最佳實踐：專案放於 WSL 檔系統；避免跨邊界大量 I/O；與 Docker Desktop 整合時留意 context 與網路。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q8, C-Q2

Q6: 如何在 Windows Server 2016 部署 Windows 容器？
- A簡: 啟用容器與 Hyper-V 功能，安裝 Docker，拉取 Windows 映像並以 NAT 網路方式曝光服務。
- A詳: 具體實作步驟：1) Install-WindowsFeature containers, Hyper-V；2) 依官方指引安裝 Docker；3) docker pull mcr.microsoft.com/dotnet/aspnet；4) docker run -p 8080:80。關鍵設定：選擇 process 或 Hyper-V 隔離；設定防火牆與 DNS；使用固定標籤。注意事項與最佳實踐：Windows 與 Linux 映像不可混用；更新累積更新以修補；監控儲存層增長。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, D-Q3

Q7: 如何讓容器化 Web 連線 SQL Server on Linux？
- A簡: 確認網路可達與連線字串，開啟埠 1433，設定 SA 密碼與資料持久化，使用受支援的驅動程式。
- A詳: 具體實作步驟：1) 啟動 SQL Server：docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=強密碼" -p 1433:1433 -v mssqldata:/var/opt/mssql mcr.microsoft.com/mssql/server:2019-latest；2) Web 連線字串：Server=sqlhost,1433;User ID=sa;Password=...;TrustServerCertificate=true;3) 驗證可達與登入。注意事項：設定時區與排序；限制權限；使用連線集區；在同一網路使用服務名稱解析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q2, D-Q4

Q8: 如何用 Rancher/Portainer 管理小型 Docker 叢集？
- A簡: 部署管理伺服器並安裝節點代理，透過 UI 建立堆疊與服務，設定升級策略與健康檢查。
- A詳: 具體實作步驟：1) docker run 啟動 Rancher/Portainer 伺服器；2) 於 UI 註冊節點（安裝 Agent）；3) 以 UI/Compose 建立服務與 LB；4) 設定副本與升級策略。關鍵設定：節點標籤、網路、卷；整合 Registry 與憑證。注意事項：限制面板存取；備份管理資料；版本相容性；小規模優先簡化為單管理節點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q6, D-Q9

Q9: 如何將現有 .NET Framework 專案遷移到 .NET Core？
- A簡: 盤點相依與 API 差異，先轉移類庫再轉 Web，採分段遷移與測試覆蓋，最終容器化部署。
- A詳: 具體實作步驟：1) 相依審核與可移植性分析（.NET Portability Analyzer）；2) 先轉移無 UI 類庫至 .NET Standard；3) 新建 ASP.NET Core 專案逐步搬遷邏輯；4) 建立自動化測試；5) 撰寫 Dockerfile 與 Compose；6) 漸進式切流。關鍵程式碼/設定：TFM 目標、NuGet 相依替換、設定檔轉換。注意：避免大爆改；保持可回滾；逐步替換第三方套件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q2, D-Q6

Q10: 如何將服務部署到 Azure（IaaS VM + Docker）？
- A簡: 佈建 Linux/Windows VM，安裝 Docker，拉取映像並以 Compose 啟動，配置 LB 與監控告警。
- A詳: 具體實作步驟：1) 建立 VM 與 VNet；2) 安裝 Docker 與登入 Registry；3) 複製 docker-compose.yml；4) docker compose up -d；5) 綁定公網 LB 與健康探測；6) 配置 Azure Monitor/Log Analytics 收集日誌。關鍵設定：Managed Identity 或安全憑證；持久卷對應 Azure Disk/File；NSG 規則。注意：以基礎建設作為程式碼；釘住映像版本；設置備援與備份。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q13, D-Q10


### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到「Cannot connect to the Docker daemon」怎麼辦？
- A簡: 確認 Docker 服務運行與權限、Socket/Context 設定，於 Windows 檢查 WSL/Hyper-V 狀態。
- A詳: 問題症狀：docker ps 報錯無法連線。可能原因：Docker 服務未啟動、權限不足（需加使用者到 docker 群組）、Docker context 指向錯誤、Windows 的 WSL/Hyper-V 未啟用。解決步驟：1) systemctl status docker；2) sudo usermod -aG docker $USER 並重新登入；3) docker context ls/ use 切換；4) Windows 啟用 WSL/Hyper-V 與 Docker Desktop 重啟。預防措施：開機自動啟動服務、文件化安裝流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q5, B-Q3

Q2: 容器間無法互通（Redis/DB 連不到）如何診斷？
- A簡: 檢查服務名稱解析、網路/埠對應、健康檢查與安全政策，逐層用工具驗證可達性。
- A詳: 問題症狀：應用連線逾時或拒絕。可能原因：不同網路、服務名/主機名錯誤、埠未開、容器未啟動或健康失敗、ACL/防火牆阻擋。解決步驟：1) docker network inspect；2) 在容器內用 ping/nc/curl 測試；3) 檢查 compose depends_on 與 healthcheck；4) 檢視 Redis/DB 日誌；5) 檢查密碼與 SSL。預防：使用服務名；定義健康檢查；以 IaC 固化網路與安全設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q5, B-Q9

Q3: Windows 無法啟動 Linux 容器的常見原因？
- A簡: 未啟用必要虛擬化（Hyper-V/WSL2）、後端切換錯誤，或 CPU 虛擬化支援關閉。
- A詳: 問題症狀：啟動 Linux 容器報錯無法建立 VM。可能原因：未啟用 Hyper-V/虛擬機平台或 WSL2、BIOS 未開啟虛擬化、Docker Desktop 後端設錯（Windows 容器模式）。解決步驟：1) 啟用功能並重啟；2) BIOS 開啟 VT-x/AMD-V；3) Docker Desktop 切換至 WSL2 或 Hyper-V；4) 重新安裝核心元件。預防：依需求選定後端；保存設定與版本相容清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, C-Q6

Q4: SQL Server on Linux 連線逾時如何排查？
- A簡: 驗證服務運行與埠開放、認證正確與加密設定；從容器內外多點測試網路可達。
- A詳: 問題症狀：應用或 sqlcmd 連線逾時。可能原因：mssql 未啟動、SA 密碼策略不符、1433 未開、容器網路隔離、TLS/憑證問題。解決步驟：1) systemctl status mssql-server 或容器日誌；2) netstat/ss 檢查埠；3) 防火牆與 NSG 規則；4) 用 sqlcmd -S host,1433 測試；5) TrustServerCertificate 設定。預防：健康檢查、強密碼策略、憑證管理與安全掃描。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, C-Q10, B-Q12

Q5: HAProxy 後端健康檢查失敗怎麼辦？
- A簡: 檢查探測路徑/狀態碼、超時與 ACL 規則，對齊 Kestrel 綁定位址與反向代理標頭。
- A詳: 問題症狀：後端被標記為 DOWN。可能原因：健康檢查 URL 錯、Kestrel 只綁 localhost、超時過短、TLS/證書錯誤、X-Forwarded 標頭處理不當。解決步驟：1) 驗證健康端點回傳 200；2) Kestrel 設定 Urls=http://0.0.0.0:8080；3) 調整 timeout/interval；4) 日誌檢視與 stats 頁面；5) 檢查路由與防火牆。預防：提供專用健康端點；基準測試合理超時值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, B-Q8, B-Q2

Q6: .NET Core 容器 CPU/記憶體高的常見原因？
- A簡: 無限並行/ThreadPool 配置不當、快取失效或 GC 模式不適合，亦可能為資源限制缺失。
- A詳: 問題症狀：容器資源飆高且響應緩慢。可能原因：過度並行、阻塞 I/O、Cache 未命中、序列化開銷、Server GC 與容器 CPU 設定不一致。解決步驟：1) 加入效能計數與 Profiling；2) 調整 ThreadPool、限制並行；3) 導入 Redis 快取；4) 切換 GC 模式；5) 設置容器資源限制與 autoscaling。預防：持續壓測、A/B 實驗與資源監控告警。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, A-Q9, C-Q3

Q7: docker-compose up 報「port is already allocated」？
- A簡: 該埠已被佔用或殘留容器映射，釋放埠、調整映射或清理舊資源即可。
- A詳: 問題症狀：啟動失敗，提示埠占用。可能原因：本機進程佔用、舊容器未清理、Compose 映射重複。解決步驟：1) lsof -i :<port>/netstat 找出佔用進程；2) docker ps 與 docker rm -f 清理；3) 調整 ports 或使用動態映射；4) 使用 docker compose down -v 清資源。預防：避免硬編碼埠；以反代統一入口。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q3, C-Q4

Q8: WSL 檔案 I/O 緩慢與路徑問題如何優化？
- A簡: 優先使用 WSL 原生檔系統與工具，避免跨系統大量 I/O；設定一致行尾與大小寫敏感。
- A詳: 問題症狀：編譯或 npm install 很慢。可能原因：跨邊界（/mnt/c）I/O 開銷大；行尾或大小寫差異導致重建。解決步驟：1) 專案存於 WSL 家目錄；2) 使用 VS Code Remote WSL；3) 設定 git autocrlf 與 .gitattributes；4) 檢查路徑大小寫與符號連結。預防：文件化規範；避免混用多環境生成器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, A-Q12, D-Q1

Q9: Swarm 服務無法擴展/排程失敗怎麼排除？
- A簡: 檢查節點健康與資源、放置限制與節點標籤，並查看事件與日誌找出排程原因。
- A詳: 問題症狀：副本維持在低數量或 Pending。可能原因：資源不足、放置條件不符、節點離線、映像拉取失敗、網路建立失敗。解決步驟：1) docker node ls/inspect；2) 檢查 service constraints 與 node labels；3) 查看 service ps 與 events；4) 驗證 Registry 權限；5) 確認 Overlay 網路容量。預防：容量規劃；健康檢查；版本與映像釘住。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q8, B-Q14

Q10: 映像版本漂移導致行為不一致如何防範？
- A簡: 釘住版本、啟用映像簽章與漏洞掃描，於 CI/CD 落實建置產物不可變與可回滾部署。
- A詳: 問題症狀：相同部署偶發行為差異。可能原因：使用 latest 標籤、外部相依更新、基底映像變動。解決步驟：1) 映像與依賴釘住語義化版本；2) 啟用簽章/驗證；3) 在 CI 以 digest 部署；4) 制定變更凍結窗口；5) 撰寫回滾手冊。預防：供應鏈治理、內部鏡像倉庫、變更審核與自動化測試閘道。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, B-Q13, C-Q2


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是混搭架構（Polyglot/混合平台架構）？
    - A-Q2: 為何 Stack Overflow 採用 .NET 搭配 Linux 組件？
    - A-Q3: .NET Core 是什麼？與 .NET Framework 有何差異？
    - A-Q4: 為什麼 .NET 開發者需要關注 Open Source？
    - A-Q5: 容器化（Docker）是什麼？核心價值為何？
    - A-Q7: Windows 與 Linux 在伺服器端的典型分工差異？
    - A-Q8: 什麼是反向代理與負載平衡（HAProxy/Nginx）？
    - A-Q9: 為何選用 Redis 與 Elasticsearch 作為外掛式能力？
    - A-Q10: Visual Studio 與 VS Code 各自的角色與差異？
    - B-Q1: Stack Overflow（2016）混搭架構如何運作？
    - B-Q3: 容器與虛擬機的隔離機制有何不同？
    - B-Q5: Docker Compose 如何定義與啟動多服務拓樸？
    - C-Q1: 如何在 Linux 上安裝 .NET Core 並執行範例？
    - C-Q3: 如何用 docker-compose 建立 Web + Redis 拓樸？
    - D-Q1: 遇到「Cannot connect to the Docker daemon」怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: 微軟策略由平台轉向應用與服務，意味著什麼？
    - A-Q11: Windows 容器、Linux 容器與 Hyper-V 容器差異？
    - A-Q12: WSL 與 Hyper-V 容器在混合環境中的定位？
    - A-Q13: Docker Swarm、Mesos、DC/OS 是什麼？差異為何？
    - A-Q14: Azure 在跨平台與開源生態中的定位是什麼？
    - A-Q15: 遷移到 .NET Core 的戰略價值與潛在風險？
    - B-Q2: .NET Core 跨平台運作的原理是什麼？
    - B-Q4: Docker 映像建置與分層檔系統如何運作？
    - B-Q6: Docker Swarm 的排程與服務擴縮如何實現？
    - B-Q8: 反向代理/負載平衡（HAProxy）背後機制為何？
    - B-Q9: Redis 快取的核心原理與常見使用模式？
    - B-Q10: Elasticsearch 索引與查詢的原理是什麼？
    - B-Q11: Rancher 如何簡化容器編排與管理？
    - B-Q12: 在雲端（Azure）上管理容器服務的模式？
    - B-Q13: .NET Core 容器化專案的 CI/CD 流程長怎樣？
    - C-Q2: 如何撰寫 ASP.NET Core 的 Dockerfile 並建置映像？
    - C-Q4: 如何以 HAProxy 作為前端負載平衡 .NET 服務？
    - C-Q5: 如何在 Windows 使用 WSL 打造跨平台開發環境？
    - C-Q7: 如何讓容器化 Web 連線 SQL Server on Linux？
    - D-Q2: 容器間無法互通（Redis/DB 連不到）如何診斷？

- 高級者：建議關注哪 15 題
    - B-Q7: 在 Windows 上以 Hyper-V 隔離執行 Linux 容器的機制？
    - B-Q14: 容器化的安全重點有哪些？
    - B-Q15: 容器化 .NET 的觀測性該怎麼設計？
    - C-Q6: 如何在 Windows Server 2016 部署 Windows 容器？
    - C-Q8: 如何用 Rancher/Portainer 管理小型 Docker 叢集？
    - C-Q9: 如何將現有 .NET Framework 專案遷移到 .NET Core？
    - C-Q10: 如何將服務部署到 Azure（IaaS VM + Docker）？
    - D-Q3: Windows 無法啟動 Linux 容器的常見原因？
    - D-Q4: SQL Server on Linux 連線逾時如何排查？
    - D-Q5: HAProxy 後端健康檢查失敗怎麼辦？
    - D-Q6: .NET Core 容器 CPU/記憶體高的常見原因？
    - D-Q7: docker-compose up 報「port is already allocated」？
    - D-Q8: WSL 檔案 I/O 緩慢與路徑問題如何優化？
    - D-Q9: Swarm 服務無法擴展/排程失敗怎麼排除？
    - D-Q10: 映像版本漂移導致行為不一致如何防範？