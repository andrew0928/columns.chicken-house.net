# Windows Container FAQ - 官網沒有說的事

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Windows Container？
- A簡: Windows 上的容器技術，使用 Windows Kernel，讓現有 Windows 應用在隔離環境中可攜運作。
- A詳: Windows Container 是微軟在 Windows Server 2016 首度提供的容器能力。它沿用 Docker 生態（API、Client、鏡像、Registry 等），但容器共用的是 Windows Kernel，因此能原生運行 Windows 應用（非 Linux）。其核心價值在於以影像化的方式封裝應用與相依，帶來一致部署、快速啟動、資源隔離與更好密度，特別適合既有的 Windows 應用與服務現代化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q7, B-Q1

A-Q2: 什麼是 Docker for Windows？
- A簡: 官方的 Windows 版 Docker 套件，透過 Hyper-V 啟動 Linux 虛擬機，運行 Linux 容器與工具。
- A詳: Docker for Windows 是 Docker 提供的安裝包，會在 Windows 背後啟動一台輕量 Linux VM（例如 Alpine Linux）並在該 VM 裡運行 Docker Engine。前端在 Windows 配好 Docker CLI 與整合，讓你可用 Windows 工具管理 VM 內的 Linux 容器。因此它能運行 Linux 應用，而非 Windows 應用，定位與 Windows Container 不同。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2, B-Q10

A-Q3: Windows Container 與 Docker for Windows 有何差異？
- A簡: 前者用 Windows Kernel 跑 Windows 應用；後者用 Hyper-V 跑 Linux VM 來跑 Linux 容器。
- A詳: Windows Container 是微軟在 Windows 平台上提供的原生容器能力，容器共用 Windows Kernel，只能跑 Windows 應用。Docker for Windows 則是 Docker 的發行包，透過 Hyper-V 啟動 Linux VM，容器實際上依附 Linux Kernel，故能運行 Linux 應用。兩者共用 Docker 生態，但服務對象、核心相依與相容性完全不同。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q4, A-Q5

A-Q4: 為什麼 Windows Container 不能執行 Linux 映像？
- A簡: 容器共用宿主核心；Windows 與 Linux 核心與系統呼叫不相容，無法交叉運行。
- A詳: 容器並非完整虛擬機，而是共享宿主 Kernel 並以命名空間等機制隔離。Linux 映像依賴 Linux 系統呼叫與檔案格式，Windows 映像依賴 Windows API 與子系統。由於核心不相容，Windows Container 無法運行 Linux 映像，必須使用為 Windows 構建的容器映像。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, A-Q10, B-Q1

A-Q5: 為什麼 Docker for Windows 能運行 Linux 應用？
- A簡: 它在 Hyper-V 啟動 Linux VM，容器依附該 Linux Kernel，因此可跑 Linux 應用。
- A詳: Docker for Windows 的核心是讓 Docker Engine 在 Linux 環境中執行。為此，它透過 Hyper-V 建立一台 Linux 虛擬機，並把 Windows 上的 Docker CLI 指向 VM 內的 Engine。容器仍然在 Linux Kernel 之上運作，維持 Linux 相容性，這就是能執行 Linux 應用的原因。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q10, A-Q3

A-Q6: 什麼是容器的隔離型態（Process 與 Hyper-V）？
- A簡: Process 以命名空間隔離；Hyper-V 以輕量 VM 加強隔離與相容，安全邊界更強。
- A詳: Windows Container 支援兩種隔離：Process 隔離透過命名空間與資源控制在同一 Kernel 分隔工作負載；Hyper-V 隔離則為每個容器建立最小化的隔離環境（輕量 VM），在安全與相容性（如用在 Windows 10）上更有保障。選擇取決於安全需求、OS 版本與相容性考量。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q7, A-Q8

A-Q7: Windows Container 與 Docker 生態相容哪些面向？
- A簡: 相容 Docker API、Client、Image、Registry、管理協定與叢集工具等生態系關鍵元件。
- A詳: 微軟設計 Windows Container 時刻意相容 Docker 生態：沿用 Docker API/協定、Docker CLI 客戶端、映像格式、Registry（如 Docker Hub），並可與現有管理與叢集工具對接。這使跨平台的流程與工具鏈（CI/CD、Registry、腳本）能夠重用，降低導入成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q5, B-Q15

A-Q8: 使用 Windows Container 需要哪些系統？
- A簡: Windows Server 2016 支援；Windows 10 Pro/Ent 可用 Hyper-V 隔離的 Windows 容器。
- A詳: 官方支援以 Windows Server 2016 為主（文章時點為 TP5 預覽版）。Windows 10 Pro/Enterprise 在 2016/08 更新後，支援以 Hyper-V 隔離方式運行 Windows 容器。啟用時需安裝容器與（在 Windows 10 上）Hyper-V 功能，再安裝 Docker 套件與基底映像。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, B-Q16

A-Q9: Windows Container 的核心價值是什麼？
- A簡: 讓既有 Windows 應用容器化，獲得一致部署、快速交付與更佳隔離管理。
- A詳: 對大量現存的 Windows 應用而言，Windows Container 提供影像化封裝與可復現的部署環境，降低環境差異導致的問題；啟動快、回收快、密度高，有利提升資源使用率；結合 Docker 生態，能融入既有 Registry 與自動化流程，促進微服務與持續交付實踐。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q7, A-Q12

A-Q10: Windows 與 Linux 容器映像有何差異？
- A簡: 前者以 Windows 基底映像，後者以 Linux 基底映像，因核心不同而互不相容。
- A詳: 容器映像是分層檔案系統與中繼資料的組合。Windows 映像以 windowsservercore 或 nanoserver 等為基底；Linux 映像以各發行版為基底。由於容器依賴宿主 Kernel，跨 OS 的映像不能互換，拉錯平台的映像將無法運行或拉取失敗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, A-Q11, C-Q4

A-Q11: 什麼是 windowsservercore 與 nanoserver？
- A簡: 微軟提供兩種基底映像：較完整的 Windows Server Core 與更精簡的 Nano Server。
- A詳: windowsservercore 提供較高相容性與豐富 API，適合需要完整 Win32/.NET Framework 能力的應用；nanoserver 更精簡、體積更小、啟動更快，適合較現代化、相依較少的服務。兩者常作為建置 Windows 容器映像的基礎層，後續再疊加應用與配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, B-Q8, A-Q20

A-Q12: 如何從 Docker Hub 取得 Windows 映像？
- A簡: 與 Linux 相同，使用 docker pull 拉取如 microsoft/windowsservercore、nanoserver、iis。
- A詳: Windows 容器映像可從 Docker Hub 取得。常見起點包括 microsoft/windowsservercore、microsoft/nanoserver 與 microsoft/iis 等。可直接 docker pull，或在 Dockerfile 以 FROM 指定基底。也能推送自建映像到私有或公有 Registry，沿用既有流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, C-Q5, B-Q7

A-Q13: 為什麼在 Docker Hub 難以分辨 Linux 與 Windows 映像？
- A簡: 當時缺乏明確標註，需讀明細或 Dockerfile，避免跨平台拉取或運行失敗。
- A詳: 文章時點，Hub 上沒有直觀標示映像的 OS 平台。實務上可檢視描述、標籤（nanoserver、windowsservercore）、Dockerfile 的 FROM，或查詢官方帳號（microsoft）。若在 Linux 上拉 Windows 映像或反之，常見為 manifest 不匹配或架構不支援錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, C-Q9, B-Q7

A-Q14: 為何在 TP5 上部署微服務較具挑戰？
- A簡: 多個關鍵網路能力未支援，如連結、名稱解析與 overlay，增加服務組網難度。
- A詳: Docker 為微服務提供容器連結、內建 DNS 與 overlay 等，使多容器能以名稱互相尋址並跨主機通訊。TP5 時期的 Windows 容器尚未支援這些功能，導致需改以主機端口映射、固定位址或應用層發現等方式繞過，設計與運維成本提高。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q13, D-Q2

A-Q15: 哪些 Docker 網路功能在當時 Windows 不支援？
- A簡: 不支援 --link、名稱解析、預設 overlay，及多數 DNS/網路相關 CLI 參數。
- A詳: 文章列出未支援項目：容器連結（--link）、以名稱/服務為本的 IP 解析、預設 overlay driver。亦未支援參數包括 --add-host、--dns、--dns-opt、--dns-search、--hostname、--net-alias、--aux-address、--internal、--ip-range。需以替代方案設計通訊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, B-Q6, B-Q17

A-Q16: 在 TP5 階段是否值得開始評估 Windows Container？
- A簡: 值得。除網路限制與零星錯誤外，多數情境可正常運作，足以進行 PoC。
- A詳: 作者實測多數功能運作良好。雖有網路功能限制與偶發錯誤，但就封裝、啟動、基本網路與映像流程而言，成熟度已可支援可行性評估。建議先從官方基底與樣例入手，聚焦應用封裝與部署流程驗證，網路部分採權宜設計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q20, C-Q5

A-Q17: Docker Client 能否管理 Windows 容器？
- A簡: 可以；甚至能用 Linux 版 Client 連線管理 Windows 上的 Docker Engine。
- A詳: 由於沿用 Docker API/協定，Docker CLI 可跨平台連線對應的 Docker Engine。只要設定正確的 DOCKER_HOST 與憑證（若啟用 TLS），即可在 Linux、macOS 或 Windows 上使用 CLI 管理 Windows 容器主機，執行 pull/run/build 等操作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, B-Q10, D-Q4

A-Q18: 什麼是容器 Registry？在 Windows 容器中的角色？
- A簡: 儲存與分發映像的伺服器；Windows 映像同樣透過 Registry 進行拉取與推送。
- A詳: Registry 扮演映像倉庫角色，客戶端透過身份驗證與 API 傳輸分層。Windows 容器完全沿用該機制：開發者可從 Docker Hub 取得官方基底映像，或將自建 Windows 映像推送到私有/公有 Registry，融入版本控管與交付管線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q4, C-Q6

A-Q19: 什麼是 Tech Preview 5（TP5）？有何意義？
- A簡: Windows Server 2016 的預覽版，功能未完整，特別是網路面仍在完善中。
- A詳: TP5 是 Windows Server 2016 的技術預覽，讓社群先行測試與回饋。此時期功能與相容性尚未最終定版，網路能力有缺口（如連結、DNS、overlay），且偶有錯誤。仍適合用於學習、PoC 與回饋，正式生產建議等待正式釋出與修補。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, A-Q16, B-Q6

A-Q20: 何時應選擇 windowsservercore 或 nanoserver 作為基底？
- A簡: 需高相容選 servercore；重視體積與啟動選 nanoserver，視應用相依決定。
- A詳: 若應用需完整 Win32/.NET Framework API 或較多系統元件，選 windowsservercore 可減少相容性風險；若應用精簡、依賴較少（如原生服務、工具），nanoserver 能帶來更小影像與更快啟動。可先以 servercore 驗證，再逐步瘦身到 nanoserver。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q6, B-Q8

### Q&A 類別 B: 技術原理類

B-Q1: Windows Container 的架構如何運作？
- A簡: 共用 Windows Kernel，以 Docker Engine/CLI 管理映像與容器，沿用 Docker 生態。
- A詳: 技術原理說明：容器是一組以命名空間與資源限制隔離的進程，與宿主共用 Windows Kernel。關鍵步驟或流程：1) 以映像分層建立容器檔案系統；2) 啟動進程並套用隔離/限制；3) 透過 NAT 暴露端口。核心組件：Docker Engine（Windows）、Docker CLI、映像/Registry、網路與儲存驅動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q7, B-Q6

B-Q2: Docker for Windows 的運作流程是什麼？
- A簡: 於 Hyper-V 啟動 Linux VM，CLI 透過 Docker API 控制 VM 內 Engine 運作 Linux 容器。
- A詳: 技術原理說明：把 Linux 容器運行環境搬到 Hyper-V VM 中。流程：1) 安裝 Docker for Windows；2) 建立 Linux VM 與 Engine；3) Windows CLI 連線 VM 的 Engine；4) 拉取與啟動 Linux 映像。核心組件：Hyper-V、Linux VM、Docker Engine、Docker CLI 與 API。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, A-Q3

B-Q3: Process 與 Hyper-V 隔離背後機制差異？
- A簡: Process 共享宿主 Kernel；Hyper-V 提供輕量 VM 邊界，提升相容性與安全隔離。
- A詳: 技術原理說明：Process 隔離依賴命名空間/控制群組等概念；Hyper-V 隔離為容器配置獨立最小環境。流程：建立容器時選擇 --isolation；Engine 依模式配置執行環境。核心組件：Windows Kernel（命名空間）、Hyper-V 隔離環境、Engine 調度與網路。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q7, D-Q3

B-Q4: 為何 Windows 容器無法執行 Linux 映像（機制層面）？
- A簡: 容器需匹配宿主 Kernel 與系統呼叫；Windows 與 Linux 在 ABI 與檔案格式上不相容。
- A詳: 技術原理說明：容器並不虛擬化 Kernel，應用直接呼叫宿主提供的系統介面。Linux 映像期望 Linux 系統呼叫與 ELF 格式，Windows 映像期望 Win32/PE 與 Windows API。關鍵步驟：拉取後會比對平台/架構；不匹配則拒絕或失敗。核心組件：Kernel、映像中繼資料（平台/架構）、Engine 相容性檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q10, D-Q1

B-Q5: Docker API 在 Windows 上如何運作？
- A簡: 沿用 REST API 與協定，Windows Engine 以相同端點提供容器與映像管理。
- A詳: 技術原理說明：Docker Engine 對外暴露標準 REST 端點，CLI 與 SDK 透過該 API 操作。流程：1) 建立連線（本機命名管道或 TCP）；2) 發送 API 請求（如 pull/run）；3) Engine 執行並回報狀態。核心組件：Docker Engine（Windows）、REST API、CLI/SDK 客戶端。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q17, C-Q3

B-Q6: Windows 容器網路堆疊現況與機制是什麼？
- A簡: 預設使用 NAT 暴露埠；TP5 未支援連結、內建名稱解析與預設 overlay。
- A詳: 技術原理說明：預設建立 NAT 網路，透過端口轉發連通外部。流程：1) 建立容器附加至預設網路；2) 以 -p 將宿主埠映射到容器；3) Engine 註冊規則。核心組件：NAT 網路、端口轉發規則、Engine 網路管理。受限功能：--link、內建 DNS、overlay driver 等暫不支援。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q8, D-Q2

B-Q7: 從 Registry 拉取 Windows 映像的流程？
- A簡: 認證後依 manifest 拉取分層，快取於本機，據此建立容器檔案系統。
- A詳: 技術原理說明：映像由多個唯讀層組成。流程：1) 客戶端請求 manifest；2) 逐層拉取 blob；3) 校驗與快取；4) 建立本地映像；5) run 時疊加可寫層。核心組件：Registry、manifest、layer blob、內容可尋址儲存與本地快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q18, D-Q1

B-Q8: Windows base image 的分層與相依原理？
- A簡: 應用映像疊加於 windowsservercore 或 nanoserver 層，版本需匹配宿主。
- A詳: 技術原理說明：映像以基底層提供 OS 元件，上層加入應用檔案與設定。流程：1) FROM 指定基底；2) RUN/COPY 新增層；3) build 產生最終映像。核心組件：基底映像（servercore/nanoserver）、映像層、相容性（版本匹配）與標籤管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q6, D-Q5

B-Q9: Dockerfile 在 Windows 的機制與常用指令？
- A簡: 解析 Dockerfile 生成分層，常以 PowerShell 執行 RUN，並用 COPY/ADD 複製檔案。
- A詳: 技術原理說明：每條指令產生新層。流程：1) FROM 指定基底；2) RUN 執行 PowerShell/命令；3) COPY/ADD 注入檔案；4) EXPOSE/ENTRYPOINT 定義埠與啟動命令。核心組件：Build 引擎、分層快取、Windows 命令/PowerShell 執行環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, A-Q20, B-Q7

B-Q10: Docker Client 如何跨平台管理 Windows Engine？
- A簡: 透過 TCP 或本機通道連到 Engine，使用相同指令與 API 操作不同平台。
- A詳: 技術原理說明：CLI 是 API 客戶端，不依賴目標平台。流程：1) 設定 DOCKER_HOST 指向 Windows 主機；2) （可選）設定 TLS；3) 發送命令；4) Engine 執行回應。核心組件：Docker CLI、REST API、傳輸通道（命名管道/TCP）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, C-Q3, D-Q4

B-Q11: 內建 DNS 名稱解析未支援的影響與替代方案？
- A簡: 容器無法以名稱互相尋址；可用主機端口映射、固定位址或外部服務發現。
- A詳: 技術原理說明：缺少內建 DNS 使容器名稱不自動解析。流程替代：1) 以 -p 暴露服務到宿主固定埠；2) 在客戶端配置連線到宿主 IP:Port；3) 導入外部服務發現。核心組件：NAT 映射、應用設定、外部註冊中心（若採用）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q8, D-Q8

B-Q12: 容器端口映射在 Windows 的運作原理？
- A簡: 透過 NAT 將宿主埠轉發至容器；Engine 建立與維護轉發規則與狀態。
- A詳: 技術原理說明：Engine 在宿主網路層安裝對應轉發規則。流程：1) docker run -p 指定映射；2) Engine 檢查衝突並建立規則；3) 封包由宿主埠導向容器內埠。核心組件：NAT 驅動、端口轉發表、Engine 網路管理模組。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q6, B-Q6

B-Q13: 微服務與 overlay 網路的關係是什麼？
- A簡: overlay 提供跨主機虛擬網路與名稱解析，簡化服務間通訊；TP5 尚未支援。
- A詳: 技術原理說明：overlay 將不同主機上的容器接入同一虛擬網路，並結合服務發現。流程：1) 建網路；2) 將容器連接；3) 服務以名稱互通。核心組件：overlay driver、分散式 KV、內建 DNS。Windows TP5 缺此能力，需以其他手段連通。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q15, D-Q2

B-Q14: 如何透過 CLI 指定隔離模式，其背後機制？
- A簡: 使用 --isolation=process|hyperv，Engine 依模式建立對應的隔離環境。
- A詳: 技術原理說明：CLI 將隔離選項傳給 Engine。流程：1) docker run --isolation=hyperv ...；2) Engine 檢查平台支援；3) 啟動對應環境。核心組件：Docker CLI、Engine 執行器、Process/Hyper-V 隔離層。注意：Windows 10 通常需 Hyper-V 隔離。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, B-Q3, D-Q3

B-Q15: 與叢集/管理工具的相容性為何？
- A簡: 相容 Docker 管理協定，可沿用 Registry、CLI、CI/CD 與部分叢集工具鏈。
- A詳: 技術原理說明：Windows Engine 遵循 Docker API，因此上層工具可無縫接入。流程：1) 工具透過 API 操作；2) Engine 按平台執行；3) 狀態回報一致。核心組件：API/協定、Registry、CLI、現有自動化系統。注意：特定網路特性若依賴 overlay 可能受限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q16, B-Q6

B-Q16: Windows 10 上 Hyper-V 隔離的設計目的？
- A簡: 以 Hyper-V 為容器提供更強隔離與相容性，解決核心版本與安全邊界需求。
- A詳: 技術原理說明：Windows 10 非伺服器 SKU，透過 Hyper-V 隔離可確保容器與宿主間的邊界。流程：1) 啟用 Hyper-V 與容器功能；2) 使用 --isolation=hyperv；3) 每容器以輕量環境執行。核心組件：Hyper-V、Engine、輕量客體環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q3, C-Q2

B-Q17: 為何 CLI 的若干網路參數未支援？
- A簡: 因平台網路堆疊尚未實作對應功能，傳入參數會被拒絕或忽略。
- A詳: 技術原理說明：功能對應的 driver/服務尚未提供，Engine 無法套用設定。流程：1) 使用不支援參數；2) CLI/Engine 報錯或忽略；3) 需改以支援的方式配置。核心組件：網路 driver、DNS 解析組件、Engine 參數解析。建議改用端口映射與外部服務發現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q2, C-Q8

B-Q18: 容器與宿主共享檔案在 Windows 的機制？
- A簡: 透過 Volume 掛載資料夾，Engine 以檔案共享橋接容器與宿主檔案系統。
- A詳: 技術原理說明：Volume 提供獨立於容器生命週期的儲存。流程：1) 建立或指定 volume；2) docker run -v 宿主:容器；3) 透過共享機制讀寫。核心組件：Volume 管理、檔案系統橋接、權限控制。可用於持久化資料與設定檔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q7, B-Q9

B-Q19: 更新基底映像對應用映像與容器的影響？
- A簡: 基底變更會改變分層指紋，需重建應用映像並重新部署容器。
- A詳: 技術原理說明：映像透過內容可尋址分層管理，任何層變動都使上層快取失效。流程：1) 拉取新版基底；2) 重新 build（利用快取）；3) 部署新容器。核心組件：映像層、快取、標籤與部署流程。注意控管標籤與相容性，避免執行時期不一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q5, A-Q18

B-Q20: 為何評估期建議先用官方延伸映像（如 microsoft/iis）？
- A簡: 官方映像已封裝常見角色，降低建置與相容風險，加速 PoC 與學習。
- A詳: 技術原理說明：延伸映像在基底上預安裝與配置常用元件（如 IIS）。流程：1) 直接 pull 官方映像；2) 以最少設定啟動服務；3) 疊加應用層驗證部署。核心組件：基底映像、角色/功能封裝、最小化配置。有助專注於應用封裝與流程，而非 OS 細節。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, A-Q16, A-Q12

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Windows Server 2016 啟用 Windows Container？
- A簡: 安裝 Containers 功能與 Docker，重啟後拉取基底映像並測試執行。
- A詳: 具體實作步驟：1) 以系統管理員開 PowerShell；2) 安裝容器功能與重啟；3) 安裝 Docker；4) 拉取映像測試。關鍵程式碼片段或設定:
  - Install-WindowsFeature -Name Containers
  - Restart-Computer
  - 安裝 Docker 與啟動服務
  - docker pull microsoft/windowsservercore
  - docker run -it --rm microsoft/windowsservercore cmd
  注意事項與最佳實踐：使用官方映像、更新至相容版本、預留磁碟空間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q4, D-Q5

C-Q2: Windows 10 如何啟用 Hyper-V 隔離容器？
- A簡: 啟用 Hyper-V 與容器功能，安裝 Docker，使用 --isolation=hyperv 執行。
- A詳: 具體實作步驟：1) 以系統管理員 PowerShell 啟用功能；2) 安裝 Docker；3) 指定 Hyper-V 隔離啟動容器。關鍵程式碼:
  - Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
  - Enable-WindowsOptionalFeature -Online -FeatureName Containers -All
  - docker run --isolation=hyperv -it --rm microsoft/nanoserver cmd
  注意事項：需 Windows 10 Pro/Ent；確保 BIOS 啟用虛擬化；優先選擇輕量映像。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q16, C-Q7

C-Q3: 如何使用 Linux 上的 Docker Client 管理 Windows 容器主機？
- A簡: 設定 DOCKER_HOST 指向 Windows Engine，開放連線並使用標準 CLI 操作。
- A詳: 具體步驟：1) 在 Windows 主機啟用 Docker 遠端（TCP）存取；2) 開防火牆；3) 在 Linux 設定 DOCKER_HOST；4) 測試 docker ps。關鍵設定/指令:
  - 在 Windows 設定 Docker 服務啟動參數以開啟 TCP（或使用預設設定）
  - 防火牆允許連線
  - export DOCKER_HOST=tcp://WIN_HOST:2375
  注意事項：評估安全性（內網或 TLS），版本匹配，網路可達性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q10, D-Q4

C-Q4: 如何拉取 windowsservercore 並執行簡單容器？
- A簡: 使用 docker pull 與 docker run 啟動互動式 cmd 測試環境。
- A詳: 具體步驟：1) docker pull microsoft/windowsservercore；2) docker run -it --rm microsoft/windowsservercore cmd；3) 在容器內執行命令驗證。關鍵指令:
  - docker pull microsoft/windowsservercore
  - docker run -it --rm microsoft/windowsservercore cmd
  注意事項：確保磁碟空間充足；首次拉取時間較久；留意映像標籤版本相容。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q7, D-Q5

C-Q5: 如何快速起一個 IIS Windows 容器並對外服務？
- A簡: 拉取 microsoft/iis，使用 -p 映射埠啟動，於瀏覽器測試回應。
- A詳: 具體步驟：1) docker pull microsoft/iis；2) docker run -d -p 8080:80 --name web microsoft/iis；3) 瀏覽 http://HOST:8080。關鍵指令:
  - docker pull microsoft/iis
  - docker run -d -p 8080:80 --name web microsoft/iis
  注意事項：確認 Windows 防火牆放行；避免埠衝突；用 -d 背景運行與 docker logs 排錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, D-Q6, A-Q20

C-Q6: 如何撰寫 Windows Dockerfile 打包 .NET 應用？
- A簡: 以 windowsservercore 或 nanoserver 為基底，COPY 應用並以 ENTRYPOINT 啟動。
- A詳: 具體步驟：1) 新增 Dockerfile；2) 指定基底；3) COPY 應用；4) RUN 進行必要註冊/設定；5) 設定 ENTRYPOINT。關鍵程式碼:
  - FROM microsoft/windowsservercore
  - WORKDIR C:\app
  - COPY . C:\app
  - RUN powershell -Command "Write-Host 'Build steps...'"
  - ENTRYPOINT ["C:\\app\\yourapp.exe"]
  注意事項：用 PowerShell 作為 RUN；控制層數；善用 .dockerignore。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q11, B-Q8

C-Q7: 如何指定容器使用 Hyper-V 或 Process 隔離？
- A簡: 在 docker run 時加 --isolation 旗標，或設定預設隔離模式。
- A詳: 具體步驟：1) 以容器建立時指定；2) 依平台選擇（Windows 10 常用 hyperv）；3) 驗證模式。關鍵指令:
  - docker run --isolation=hyperv -it --rm microsoft/nanoserver cmd
  - docker run --isolation=process -it --rm microsoft/windowsservercore cmd
  注意事項：模式需平台支援；Hyper-V 隔離開銷較高；在同一主機上可混用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q14, D-Q3

C-Q8: 網路功能受限下如何讓兩個容器互通？
- A簡: 以宿主端口映射並讓客戶端指向宿主 IP:Port，避免依賴名稱解析。
- A詳: 具體步驟：1) 將服務容器以 -p 暴露固定埠；2) 於客戶端容器設定目標為宿主 IP 與該埠；3) 驗證連線。關鍵設定:
  - docker run -d -p 5000:5000 --name svc yourimage
  - 在客戶端以 http://HOST_IP:5000 呼叫
  注意事項：預留埠規劃；防火牆放行；以設定檔注入位址，避免重建映像。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q11, D-Q2

C-Q9: 如何在 Docker Hub 辨識 Windows 映像以避免拉錯？
- A簡: 檢視描述與 Dockerfile 的 FROM，偏向 microsoft/* 並注意 nanoserver/servercore 標籤。
- A詳: 具體步驟：1) 開啟映像頁面閱讀說明；2) 查看 Dockerfile 的基底（是否 windowsservercore/nanoserver）；3) 優先選官方帳號（microsoft）；4) 必要時先以 Windows 主機測試拉取。注意事項：Hub 上當時無明顯標註；跨平台拉取常出現 manifest 不匹配錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, D-Q1, B-Q7

C-Q10: 如何取得微軟提供的 Windows Container 範例並練習？
- A簡: 從 GitHub 複製官方樣例倉庫，依指引 build 與 run 驗證流程。
- A詳: 具體步驟：1) 造訪官方樣例倉庫；2) git clone 至本機；3) 進入目錄依 README 執行 docker build/run；4) 根據樣例延伸自有應用。關鍵指令:
  - git clone https://github.com/Microsoft/Virtualization-Documentation.git
  - cd windows-container-samples/windowsservercore
  - docker build -t myapp .
  - docker run -it --rm myapp
  注意事項：選擇對應基底；按樣例版本匹配；先跑通再客製化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q20, C-Q6

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 拉取映像出現「no matching manifest」怎麼辦？
- A簡: 你可能在 Windows 拉取 Linux 映像（或相反），改用對應平台的 Windows 映像。
- A詳: 問題症狀描述：docker pull 報 manifest 不匹配或平台不支援。可能原因分析：映像為另一作業系統平台；標籤錯誤。解決步驟：1) 確認映像來源與 Dockerfile 基底；2) 改用 microsoft/windowsservercore 或 nanoserver 等 Windows 映像；3) 在目標平台測試拉取。預防措施：養成檢視說明/標籤習慣，建立白名單清單。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q13, C-Q9

D-Q2: 無法使用 --link 或容器名稱解析時怎麼辦？
- A簡: 這些功能於當時未支援；改用宿主端口映射與外部配置/服務發現。
- A詳: 問題症狀描述：使用 --link/名稱呼叫失敗。可能原因：Windows 容器（TP5）未支援連結、內建 DNS。解決步驟：1) 以 -p 暴露固定埠；2) 用宿主 IP:Port 設定客戶端；3) 考慮外部服務發現。預防措施：設計時避免硬依賴內建 DNS/overlay，明確規劃埠與設定注入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q11, C-Q8

D-Q3: 在 Windows 10 使用 Process 隔離失敗怎麼辦？
- A簡: Windows 10 通常需 Hyper-V 隔離；改用 --isolation=hyperv 或改用 Server。
- A詳: 問題症狀描述：run 報平台不支援或系統不匹配。可能原因分析：Windows 10 不支援或不建議使用 process 隔離。解決步驟：1) 改以 --isolation=hyperv；2) 啟用 Hyper-V；3) 若需 process 隔離，改用 Windows Server 2016。預防措施：依平台預設隔離模式建置腳本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q2, C-Q7

D-Q4: Docker Client 無法連線到 Windows Engine？
- A簡: 檢查 DOCKER_HOST 設定、網路可達、防火牆與版本相容性後重試。
- A詳: 問題症狀描述：docker ps 超時或拒絕連線。可能原因：DOCKER_HOST 設錯、端口未開、TLS/權限問題。解決步驟：1) 確認 Engine 運行；2) 檢查 DOCKER_HOST=tcp://host:port；3) 開放防火牆；4) 比對版本。預防措施：固定連線設定與文件化；以內網或 TLS 保護遠端 API。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q10, A-Q17

D-Q5: 拉取或啟動 microsoft/nanoserver 失敗的原因？
- A簡: 可能是基底版本不匹配或資源不足；檢查標籤、更新系統與磁碟空間。
- A詳: 問題症狀：pull 超時/失敗，run 報不相容。可能原因：映像標籤與宿主版本不匹配、網路中斷、磁碟不足。解決步驟：1) 指定正確標籤；2) 更新宿主；3) 清理舊映像釋放空間；4) 重試。預防：規劃儲存空間，建立映像版本與宿主對照表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q4, D-Q7

D-Q6: IIS 容器啟動後無法對外服務怎麼辦？
- A簡: 確認 -p 埠映射與防火牆放行，檢查容器內服務是否正常啟動。
- A詳: 症狀：瀏覽器連線逾時。原因：未映射埠、埠衝突、防火牆阻擋、IIS 未啟動。解決：1) 使用 -p 8080:80 重新啟動；2) 變更未衝突埠；3) 放行防火牆；4) docker logs 與容器內檢查 IIS。預防：以啟動腳本自檢，標準化埠配置。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, B-Q12, A-Q15

D-Q7: 影像過大導致磁碟不足如何處理？
- A簡: 使用較小基底、清理未用映像/容器，合併層與善用 .dockerignore。
- A詳: 症狀：拉取或 build 失敗報磁碟不足。原因：servercore 體積大、累積無用層。解決：1) 優先選 nanoserver（可行時）；2) 清理未用映像/容器；3) 精簡 Dockerfile 層與檔案。預防：定期清理、規劃儲存、建立瘦身指引。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q6, B-Q8

D-Q8: 容器彼此無法以名稱解析互通怎麼辦？
- A簡: 以宿主 IP:Port 溝通，或導入外部服務發現；暫勿依賴內建 DNS。
- A詳: 症狀：用容器名稱連線失敗。原因：TP5 未支援內建 DNS 名稱解析。解決：1) 對外暴露固定埠；2) 在客戶端配置宿主位址；3) 引入外部服務目錄。預防：在架構設計中明確約定端點，將可配置位址外部化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8, A-Q14

D-Q9: 防火牆導致容器或遠端管理連線異常怎麼辦？
- A簡: 放行應用映射埠與 Docker 遠端埠，驗證連通性並更新規則。
- A詳: 症狀：無法連到容器服務或 Docker Engine。原因：Windows 防火牆未放行對應埠。解決：1) 確認使用 -p 的宿主埠；2) 放行該埠；3) 對遠端管理放行目標埠；4) 測試連線。預防：在部署腳本中自動加規則，避免手動遺漏。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q3, B-Q12

D-Q10: 面對 TP5 的零星錯誤與不穩定該如何處置？
- A簡: 先重試與更新，縮小範圍定位問題，必要時改用官方映像與簡化場景。
- A詳: 症狀：偶發 build/run 錯誤或卡住。原因：預覽版穩定度與相容性不足。解決：1) 更新至最新 TP 與修補；2) 使用官方基底與樣例重現；3) 逐步增加複雜度定位；4) 收集日誌回報。預防：PoC 階段控管變因，建立最小可重現範本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q20, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Windows Container？
    - A-Q2: 什麼是 Docker for Windows？
    - A-Q3: Windows Container 與 Docker for Windows 有何差異？
    - A-Q4: 為什麼 Windows Container 不能執行 Linux 映像？
    - A-Q5: 為什麼 Docker for Windows 能運行 Linux 應用？
    - A-Q8: 使用 Windows Container 需要哪些系統？
    - A-Q12: 如何從 Docker Hub 取得 Windows 映像？
    - A-Q13: 為什麼在 Docker Hub 難以分辨 Linux 與 Windows 映像？
    - C-Q1: 如何在 Windows Server 2016 啟用 Windows Container？
    - C-Q2: Windows 10 如何啟用 Hyper-V 隔離容器？
    - C-Q4: 如何拉取 windowsservercore 並執行簡單容器？
    - C-Q5: 如何快速起一個 IIS Windows 容器並對外服務？
    - D-Q1: 拉取映像出現「no matching manifest」怎麼辦？
    - D-Q6: IIS 容器啟動後無法對外服務怎麼辦？
    - D-Q9: 防火牆導致容器或遠端管理連線異常怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是容器的隔離型態（Process 與 Hyper-V）？
    - A-Q7: Windows Container 與 Docker 生態相容哪些面向？
    - A-Q9: Windows Container 的核心價值是什麼？
    - A-Q10: Windows 與 Linux 容器映像有何差異？
    - A-Q11: 什麼是 windowsservercore 與 nanoserver？
    - A-Q14: 為何在 TP5 上部署微服務較具挑戰？
    - A-Q15: 哪些 Docker 網路功能在當時 Windows 不支援？
    - B-Q1: Windows Container 的架構如何運作？
    - B-Q3: Process 與 Hyper-V 隔離背後機制差異？
    - B-Q6: Windows 容器網路堆疊現況與機制是什麼？
    - B-Q7: 從 Registry 拉取 Windows 映像的流程？
    - B-Q9: Dockerfile 在 Windows 的機制與常用指令？
    - B-Q12: 容器端口映射在 Windows 的運作原理？
    - B-Q13: 微服務與 overlay 網路的關係是什麼？
    - B-Q15: 與叢集/管理工具的相容性為何？
    - C-Q6: 如何撰寫 Windows Dockerfile 打包 .NET 應用？
    - C-Q7: 如何指定容器使用 Hyper-V 或 Process 隔離？
    - C-Q8: 網路功能受限下如何讓兩個容器互通？
    - D-Q2: 無法使用 --link 或容器名稱解析時怎麼辦？
    - D-Q5: 拉取或啟動 microsoft/nanoserver 失敗的原因？

- 高級者：建議關注哪 15 題
    - B-Q2: Docker for Windows 的運作流程是什麼？
    - B-Q4: 為何 Windows 容器無法執行 Linux 映像（機制層面）？
    - B-Q5: Docker API 在 Windows 上如何運作？
    - B-Q8: Windows base image 的分層與相依原理？
    - B-Q11: 內建 DNS 名稱解析未支援的影響與替代方案？
    - B-Q14: 如何透過 CLI 指定隔離模式，其背後機制？
    - B-Q16: Windows 10 上 Hyper-V 隔離的設計目的？
    - B-Q17: 為何 CLI 的若干網路參數未支援？
    - B-Q18: 容器與宿主共享檔案在 Windows 的機制？
    - B-Q19: 更新基底映像對應用映像與容器的影響？
    - B-Q20: 為何評估期建議先用官方延伸映像（如 microsoft/iis）？
    - C-Q3: 如何使用 Linux 上的 Docker Client 管理 Windows 容器主機？
    - C-Q9: 如何在 Docker Hub 辨識 Windows 映像以避免拉錯？
    - D-Q3: 在 Windows 10 使用 Process 隔離失敗怎麼辦？
    - D-Q10: 面對 TP5 的零星錯誤與不穩定該如何處置？