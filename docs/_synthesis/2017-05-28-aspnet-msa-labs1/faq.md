---
layout: synthesis
title: "容器化的微服務開發 #1, IP查詢架構與開發範例"
synthesis_type: faq
source_post: /2017/05/28/aspnet-msa-labs1/
redirect_from:
  - /2017/05/28/aspnet-msa-labs1/faq/
postid: 2017-05-28-aspnet-msa-labs1
---
{% raw %}

# 容器化的微服務開發 #1：IP查詢架構與開發範例（FAQ）

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是容器驅動開發（Container Driven Development）？
- A簡: 以容器能力為設計起點，應用專注業務，環境交給容器，統一打包、啟停、網路、檔案與設定，提升一致性與可移植性。
- A詳: 容器驅動開發是從容器的能力與限制出發，規劃系統的模組化邊界與運維方式。應用程式僅專注業務邏輯；執行環境、啟停控制、端口、目錄掛載、設定注入與日誌，交由容器標準化處置。以 Dockerfile 固化環境、映像統一交付、registry 發佈、logs 走 stdout/stderr、volume 掛載共享、compose 佈署整體拓撲。本案例以 WebAPI、Worker、SDK 三模組，透過 volume 與反向代理，實現高可用、可擴展與自動更新。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q10, B-Q5

A-Q2: 什麼是微服務架構？
- A簡: 微服務以小而自治為核心，聚焦單一職責，獨立部署，透過 API 協作，利於快速迭代與彈性擴展。
- A詳: 微服務將系統拆分成多個小型、自治、可獨立部署的服務。每個服務聚焦單一業務職責，藉由輕量 API（如 REST）彼此協作。其優點包括技術異質性、部署粒度小、獨立擴展、故障隔離；代價是運維複雜度上升、跨服務資料一致性與觀測性需求提升。本案例的 IP 查詢即是單一職責的理想微服務：讀多寫少、狀態外置、可水平擴展。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q12, B-Q11

A-Q3: 為什麼 IP 所屬國家查詢適合做成微服務？
- A簡: 功能單一、狀態外置、讀多寫少、易水平擴展，且可獨立演進，符合微服務設計準則。
- A詳: IP→國家查詢屬於清晰單職責的功能。服務本身不持久化狀態，依賴外部資料檔（CSV）即可；查詢以讀為主、頻繁、延遲敏感，透過無狀態 WebAPI 易於水平擴展；資料更新可另由 Worker 週期處理，與查詢面分離，降低耦合。SDK 再以客端快取減少重複查詢與延遲，強化效能。整體結構貼合微服務的自治性與運維邊界。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q1, B-Q8

A-Q4: 容器化與傳統部署有什麼差異？
- A簡: 容器化將程式與環境打包為映像，統一啟停與配置；傳統部署需手動佈建環境，易漂移與不一致。
- A詳: 容器以映像固定執行環境與依賴，實現不可變基礎設施。啟動以 docker run 定義網路、volume 與環境變數；日誌走 stdout 供統一收集；更新以替換映像、滾動升級。傳統部署仰賴機器層安裝與設定，易受環境差異影響，部署與回滾成本高。容器化大幅簡化「在我機器可用」的落差，強化 CI/CD 與擴展能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q15, A-Q8

A-Q5: Windows Container 與 Linux Container 有何差異？
- A簡: 核心共用但基底不同，Windows 映像依賴 Windows 核心，適合 .NET Framework；Linux 適合 .NET Core 等。
- A詳: 兩者皆為 OS 層隔離的容器，但共用的核心不同。Windows 容器需 Windows 核心，常搭配 IIS、.NET Framework（如 microsoft/aspnet）；Linux 容器搭配 Linux 核心，常用 nginx、.NET Core（mcr/dotnet）。差異包含映像體積、網路堆疊（NAT）、檔案系統與路徑慣例、工具鏈。選擇取決於技術棧與部署平台。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q9

A-Q6: 什麼是 Docker 映像（Image）與容器（Container）？
- A簡: 映像是唯讀藍圖，容器是映像的執行實例。映像供分發，容器負責運行。
- A詳: 映像為多層唯讀快照，包含檔案與中介軟體，透過 Dockerfile 建置；容器則是映像的可執行實例，疊加可寫層並具備生命週期（start/stop/restart）。開發交付映像，運維以容器運行，二者分工明確。映像可推送到 registry，容器啟動時配置埠、volume 與環境參數。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q7

A-Q7: 什麼是 Dockerfile？
- A簡: 建置映像的宣告式藍圖，定義基底、檔案複製、埠、volume 與啟動命令。
- A詳: Dockerfile 以層層指令（如 FROM、WORKDIR、COPY、RUN、EXPOSE、VOLUME、ENTRYPOINT）描述映像內容與行為。重複建置可重現、差異化層便於快取。本案例 WebAPI Dockerfile 基於 microsoft/aspnet，複製網站到 IIS 根目錄、宣告 80 埠與 App_Data 為 volume；Worker Dockerfile 基於 dotnet-framework，設定工作目錄、volume 與 ENTRYPOINT 執行 console 程式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q7, C-Q1

A-Q8: 什麼是不可變伺服器（Immutable Server）？
- A簡: 不修改在位實例，升級以替換映像重建容器，確保一致性與可回滾性。
- A詳: 不可變伺服器主張運行實例不做就地修改；任何變更透過新版映像與重新部署實現。優點是環境一致、回滾迅速、漂移風險低，便於自動化與擴展。搭配 registry、compose 或編排器可實現滾動更新與藍綠部署。本案例 WebAPI、Worker 改版即重建映像，避免手動改機器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q9

A-Q9: 什麼是反向代理（Reverse Proxy），在此扮演什麼角色？
- A簡: 代理客戶端請求至後端多實例，做流量分配、路由與保護，支撐高可用與擴展。
- A詳: 反向代理位於用戶與服務之間，接收請求後將其分發到後端服務實例，常兼具 TLS 終結、路由、快取與限流。於本案例，反向代理將外部流量平均分配至多個 IP2C.WebAPI 容器，提升可用性與擴展能力，也可整合 API 路徑與版本治理。可選用 IIS ARR、nginx、Traefik 等。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q11, B-Q13

A-Q10: 案例中有哪些核心組件（服務與專案）？
- A簡: 三大專案：IP2C.WebAPI 查詢、IP2C.Worker 更新資料、IP2C.SDK 封裝呼叫與客端快取。
- A詳: 整體由三部分構成：WebAPI 以 ASP.NET WebAPI2 提供 /api/ip2c/{int} 查詢，讀取 App_Data/ipdb.csv；Worker 為 console 背景服務，定時下載官方 GZip 檔、解壓驗證後熱替換 CSV；SDK 提供友善呼叫界面並內建客端快取，降低延遲與重複查詢。容器化後透過 volume 共享資料，反向代理分流查詢流量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4, C-Q4

A-Q11: 為什麼要提供 SDK 並內建客端快取？
- A簡: 降低整體延遲與重複查詢，統一介面，改善 DX，並緩解後端負載，提升穩定性。
- A詳: SDK 可隱蔽呼叫細節（序列化、重試、錯誤處理），提升開發者體驗（DX）。加入客端快取後，對同一 IP 的短期重複查詢可命中本地，降低網路延遲與後端壓力；若搭配 TTL 與逐出策略，可在準確度與效能間取得平衡。SDK 亦可內建備援邏輯（多端點、降級），提升整體可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q10

A-Q12: 為什麼需要高可用（HA）與可擴展（Scalability）？
- A簡: 查詢量不穩定且對延遲敏感，需容錯與水平擴展，確保不中斷與穩定回應。
- A詳: 公共查詢服務的流量具有峰谷，且每次請求延遲敏感。HA 透過多實例與反向代理避免單點失效；Scalability 可依流量水平擴展 WebAPI 實例。資料更新由 Worker 分離處理，不影響查詢；volume 共享與檔案監聽支持熱更新，縮短停機。容器化配合編排器可快速擴縮。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q13

A-Q13: Docker Volume 與傳統共享資料夾有何差異？
- A簡: Volume 以掛載方式注入，免去網路分享與 ACL 複雜性，便於跨容器共享檔案。
- A詳: Volume 讓宿主檔案（或命名 volume）被容器掛載使用，對容器如符號連結。相較傳統 SMB 分享與網路磁碟，省去權限與網路拓撲的繁複設定；單一宿主目錄可同時掛載多容器，共享一致資料。本案例 Worker 與 WebAPI 共用 CSV 即以 -v 掛載同一路徑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q4

A-Q14: Docker 的三大配置通道是什麼？
- A簡: 網路（-p）、檔案（-v volume）、環境變數（-e），啟動時注入容器行為與設定。
- A詳: 容器啟動可透過三類通道調整行為：網路以 -p 做宿主與容器埠對應；檔案以 -v 掛載宿主目錄或 volume；設定以 -e 注入環境變數。這三者涵蓋對外溝通、狀態與配置注入需求，讓同一映像在不同環境以不同設定運作，達到 12-factor 精神。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, B-Q9

A-Q15: 為何選擇 Console App + 容器取代 Windows 服務？
- A簡: 容器本身可守護運行與啟停管理，Console 更輕量，少樣板與安裝步驟。
- A詳: 在容器內，背景服務只需以 Console 形式運作，由 docker 管理生命週期與重啟，ENTRYPOINT 啟動程序即可。相較 Windows Service，免去安裝註冊、服務管理與安裝程式維護，樣板代碼大幅減少。日志以 Console.WriteLine 輸出，由 docker logs 統一查看。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q3

A-Q16: 什麼是 CI/CD？本案例如何設計？
- A簡: 持續整合與交付，提交即編譯測試，產出映像/套件，選定版本自動部署。
- A詳: CI 在每次提交後自動編譯並執行測試，CD 將合格產物（映像、套件）自動發佈。本案例流程：push 觸發 CI→建置與單元測試→生成 WebAPI/Worker 映像並推送 registry→SDK 打包 nuget 並 push→決定上版時以 docker-compose 從 registry 拉取並部署。可用 GitLab CI Runner 執行 build script。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, B-Q15, C-Q9

A-Q17: 什麼是 NAT loopback 限制（Windows Container）？
- A簡: Windows NAT 不支援本機回環訪問映射埠，自機測試需用容器 IP 或外機連線。
- A詳: 在 Windows 預設 NAT 網路，宿主無法以自身的 NAT 對應埠 loopback 訪問容器服務（localhost:port 失效）。解法包括：以 docker inspect 取得容器 IP 直接用 80 埠、從同網段另一台機器訪問宿主對外埠、或改用透明網路模式。文章示範以容器 IP 訪問。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q1

A-Q18: 什麼是 IP2C.NET 函式庫？
- A簡: 以 C# 實作的高效 IP→國家查詢庫，讀取官方 CSV，支援快速查詢。
- A詳: 由社群提供的 C# 函式庫，載入官方 IP 資料庫 CSV，提供輸入 IPv4（字串或數值）查詢國碼與國名的 API。本案例 WebAPI 與 Worker 皆以此為核心查詢與驗證工具，簡化資料處理並確保效能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4


### Q&A 類別 B: 技術原理類

B-Q1: IP2C.WebAPI 的查詢流程如何運作？
- A簡: 轉換整數為 IPv4，載入快取中的資料庫，查國碼與名稱，回傳 JSON 結果。
- A詳: 技術原理說明：控制器接收整數型 id，透過位移轉為 IPv4 字串；呼叫 LoadIPDB 取得 IPCountryFinder 實例，該實例放在 MemoryCache，並以 HostFileChangeMonitor 監看 CSV 變更。核心步驟：1) 轉換 IP 2) 從快取/檔案載入資料庫 3) GetCountryCode 取得國碼 4) 對應國名 5) 回傳匿名物件序列化為 JSON。核心組件：ASP.NET WebAPI2、IPCountryFinder、MemoryCache、HostFileChangeMonitor。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q3, C-Q7

B-Q2: 將整數轉為 IPv4 的機制是什麼？
- A簡: 以位移與遮罩取出四個位元組，組合成 x.x.x.x 字串表示。
- A詳: 技術原理說明：IPv4 以 32 位元表示，最高位元組為第一段。將整數右移 24/16/8/0 位，並以 0xFF 遮罩各段，得到四個 0-255 的數值。關鍵步驟：1) 右移 2) AND 遮罩 3) 格式化為字串。核心組件：位元運算、C# 格式化。此轉換確保與 Worker 測試資料的一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, A-Q3

B-Q3: MemoryCache 與 HostFileChangeMonitor 如何實現資料熱更新？
- A簡: 將 Finder 快取於記憶體，監看 CSV 檔變更，自動失效並重建實例。
- A詳: 技術原理說明：MemoryCache 保存 IPCountryFinder 實例，CacheItemPolicy 綁定 HostFileChangeMonitor 監看 CSV 檔。當檔案時間戳改變或替換，新實例會在下次查詢時重建。關鍵步驟：1) 讀檔並建立 Finder 2) 建立監看器 3) 加入快取 4) 失效後重建。核心組件：MemoryCache、CacheItemPolicy、HostFileChangeMonitor、FileSystemWatcher。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, A-Q13

B-Q4: IP2C.Worker 的自動更新機制如何設計？
- A簡: 週期等待→下載 GZip→解壓→驗證→備份→原子替換→下一輪，循環執行。
- A詳: 技術原理說明：Worker 啟動後以 while 迴圈與 Task.Delay 計時，週期性觸發更新。關鍵步驟：1) 計算等待時間 2) 下載官方 GZip（HttpClient）3) GZipStream 解壓至 .temp 4) 用 IPCountryFinder 驗證一組測試 IP 5) 刪除舊 .bak 6) 將現有 .csv 改名 .bak 7) 將 .temp 改名 .csv（原子替換）8) 記錄 stdout 日誌。核心組件：HttpClient、GZipStream、檔案 I/O、IPCountryFinder。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, A-Q15, D-Q2

B-Q5: WebAPI 的 Dockerfile 架構與作用是什麼？
- A簡: 以 ASP.NET 基底，複製站台，開放 80 埠，宣告 App_Data 為可掛載資料卷。
- A詳: 技術原理說明：FROM microsoft/aspnet 提供 IIS 與 ASP.NET 執行時；WORKDIR 指向站台根目錄；COPY 將編譯輸出放入容器；EXPOSE 80 宣告服務埠；VOLUME App_Data 允許外部掛載。關鍵步驟：建置→複製→開放→持久化。核心組件：IIS、ASP.NET Runtime、Dockerfile 指令。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, A-Q7

B-Q6: Worker 的 Dockerfile 與 ENTRYPOINT 有何作用？
- A簡: 指定 dotnet-framework 基底，複製檔案，宣告資料卷，ENTRYPOINT 啟動主程序。
- A詳: 技術原理說明：FROM microsoft/dotnet-framework 提供執行時；WORKDIR 設定工作路徑；COPY 放入可執行檔；VOLUME 宣告 data 目錄供掛載；ENTRYPOINT 指定 IP2C.Worker.exe，容器啟動即開始監控更新。關鍵步驟：環境→檔案→卷→啟動。核心組件：Dockerfile、ENTRYPOINT。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, A-Q15

B-Q7: 為何以 volume 實現 Worker→WebAPI 的資料流？
- A簡: 共享同一路徑，Worker 更新 CSV 即時可見，配合檔案監看達成熱切換。
- A詳: 技術原理說明：二者皆將容器內資料路徑對應至同一宿主目錄，Worker 完成原子替換後，WebAPI 監看檔案變更使記憶體快取失效並重建 Finder。關鍵步驟：一致掛載點→原子替換→快取失效→新資料生效。核心組件：-v 掛載、HostFileChangeMonitor、檔案改名。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q3, C-Q4

B-Q8: docker run -p 的埠對應原理是什麼？
- A簡: 將宿主埠映射至容器內服務埠，外部流量藉宿主埠進入容器。
- A詳: 技術原理說明：-p host:container 建立 NAT 規則，宿主指定埠接受連線並轉發至容器目標埠（例：8000:80）。關鍵步驟：選定對外埠→宣告映射→透過宿主埠訪問。核心組件：Docker NAT、端口轉發。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q2

B-Q9: docker run -v 在 Windows 上如何掛載路徑？
- A簡: 以 -v 宿主路徑:容器路徑 掛載；注意磁碟代號與路徑格式一致性。
- A詳: 技術原理說明：Windows 使用 -v d:\data:c:\path 格式；容器中可見為符號連結至 ContainerMappedDirectories。關鍵步驟：建立宿主目錄→以相同路徑掛載至兩容器→確認權限。核心組件：Volume 驅動、Windows 路徑慣例。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q4, D-Q5

B-Q10: 容器日誌如何收集與查看？
- A簡: 將訊息輸出至 stdout/stderr，使用 docker logs 集中查看與追蹤。
- A詳: 技術原理說明：應用以 Console.WriteLine 輸出，Docker 以 logging driver 收集。關鍵步驟：標準輸出→docker logs <container-id> 查看→必要時導出集中化。核心組件：stdout/stderr、docker logs、logging driver。此法避免複雜檔案寫入與權限問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, D-Q7

B-Q11: 反向代理與負載分配的基本機制是什麼？
- A簡: 以健康檢查與演算法（RR 等）將請求分配至多實例，提升可用與吞吐。
- A詳: 技術原理說明：反向代理接收外部請求，根據路由與負載演算法（輪詢、最少連線等）轉發至後端實例，並監控健康狀態以避開失效節點。關鍵步驟：前端接入→路由與分配→健康檢測→回應聚合。核心組件：反向代理（IIS ARR/nginx/Traefik）、健康檢查、路由規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q12

B-Q12: 如何在容器環境達成高可用與水平擴展？
- A簡: 多實例部署，前置反向代理；以 compose/編排器進行擴縮與滾動更新。
- A詳: 技術原理說明：同映像跑多容器實例，反向代理分流，藉 compose 或編排器（Swarm/K8s）擴縮；映像更新以滾動方式逐步替換。關鍵步驟：打包→多實例→分流→擴縮→更新。核心組件：Docker Compose/Swarm、反向代理、健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q9

B-Q13: 本案例的 CI/CD 流程技術架構如何設計？
- A簡: Git push 觸發 Runner 建置測試，產出映像與 NuGet，推送 registry/server。
- A詳: 技術原理說明：CI 由 Runner 執行 build script，完成解決方案編譯、測試；WebAPI/Worker 以 docker build 建映像，tag 並 push registry；SDK 以 pack/push 發佈到 NuGet。CD 以 compose 檔描述服務，拉取指定 tag 部署。核心組件：GitLab Runner、docker CLI、nuget CLI、registry。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q15, C-Q9

B-Q14: NuGet 在 SDK 發佈中扮演什麼角色？
- A簡: 作為封裝與分發通道，統一版本管理，便於開發者引用與更新。
- A詳: 技術原理說明：SDK 以 NuGet 包含 API、相依與版本資訊；打包後 push 至 NuGet Server，使用者以 package manager 引用。關鍵步驟：定義 metadata→pack→push→消費端安裝更新。核心組件：.nuspec/.csproj pack、nuget.org 或私服、語意化版本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q10

B-Q15: Docker Registry 的角色是什麼？
- A簡: 儲存與分發映像，CI push、CD pull，支撐不可變交付與回滾。
- A詳: 技術原理說明：Registry 保存映像版本（tag），CI 推送、部署端拉取。支援權限控管與快取，並作為回滾依據。關鍵步驟：打包→tag→push→pull→部署。核心組件：Docker Hub/私有 Registry、tag 策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q9

B-Q16: Docker Compose 在多容器部署中的設計概念？
- A簡: 以 YAML 宣告服務、網路、卷與相依，命令式一鍵啟停整套系統。
- A詳: 技術原理說明：Compose 將多服務的映像、環境、卷、端口、相依與副本數以 YAML 描述。docker-compose up 依序啟動整體，down 清理資源。關鍵步驟：撰寫 compose.yml→定義服務關係→一鍵啟動。核心組件：docker-compose CLI、YAML 模型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, B-Q12

B-Q17: SDK 的客戶端快取原理與設計重點？
- A簡: 以鍵為 IP 與 TTL 保存，命中即回傳，過期重取，兼顧準確與效能。
- A詳: 技術原理說明：SDK 以字典（或 MemoryCache）快取 IP→國家結果，搭配 TTL 與上限容量；查詢先檢查命中，否則呼叫 WebAPI 並寫回快取。關鍵步驟：查→命中→直回；未命中→呼叫→寫入。核心組件：快取容器、TTL、逐出策略（LRU）。注意錯誤與降級處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q10

B-Q18: Windows NAT 網路與容器 IP 取得機制？
- A簡: 預設為 NAT 網路，容器私有 IP；以 docker inspect 取得 IP，供本機測試用。
- A詳: 技術原理說明：Windows 預設建立 nat 網路，容器獲得內部 IP，宿主以端口映射橋接；因不支援 loopback，本機需直接用容器 IP:80 測試。關鍵步驟：docker ps→docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" <id>→瀏覽器連線。核心組件：NAT、inspect、vEthernet (nat)。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q2, D-Q1


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何建置 IP2C.WebAPI 的 Docker 映像？
- A簡: 先建置專案輸出，再在輸出目錄 docker build，使用 ASP.NET 基底映像。
- A詳: 具體實作步驟：1) MSBuild 以 Release/DeployOnBuild 輸出網站 2) 進入 PackageTmp 目錄 3) docker build -t ip2c/webapi:latest . 4) 驗證映像。核心程式碼片段或設定：
  - MSBuild: "C:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe" /p:Configuration=Release /p:DeployOnBuild=true
  - Dockerfile: FROM microsoft/aspnet / WORKDIR c:/inetpub/wwwroot/ / COPY . . / EXPOSE 80 / VOLUME ["c:/inetpub/wwwroot/App_Data"]
  注意事項：確保輸出目錄正確；映像體積可透過多階段/裁剪資源優化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, A-Q7

C-Q2: 如何執行 WebAPI 容器並對外開放埠？
- A簡: 以 docker run -p 8000:80 啟動，外部經宿主 8000 訪問容器之 80 埠。
- A詳: 具體實作步驟：1) docker run -d -p 8000:80 ip2c/webapi 2) 取得容器狀態 docker ps 3) Windows 本機測試採容器 IP:80（NAT 限制）。關鍵設定：-p 8000:80。注意事項：埠需可用；防火牆放行；Windows NAT 不支援 loopback，改用 inspect 取 IP 測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, A-Q17

C-Q3: 如何建置並執行 IP2C.Worker 容器？
- A簡: docker build 產生映像，docker run 執行 ENTRYPOINT，Console 背景定時更新。
- A詳: 具體實作步驟：1) 在專案根目錄 docker build -t ip2c/worker . 2) 互動測試：docker run ip2c/worker 3) 背景模式：docker run -d ip2c/worker。關鍵設定：Dockerfile ENTRYPOINT IP2C.Worker.exe。注意事項：以 stdout 輸出；日誌用 docker logs；請掛載資料卷至 data 目錄以持久化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q10

C-Q4: 如何用 volume 讓 WebAPI 與 Worker 共用 CSV？
- A簡: 將宿主同一路徑分別掛載至兩容器的資料路徑，達成檔案共用。
- A詳: 具體實作步驟：1) 建立宿主資料夾 d:\data 2) 啟動 WebAPI：docker run -d -p 8000:80 -v d:\data:c:/inetpub/wwwroot/App_Data ip2c/webapi 3) 啟動 Worker：docker run -d -v d:\data:c:/IP2C.Worker/data ip2c/worker。關鍵設定：兩容器掛載到相同宿主目錄。注意事項：路徑需存在且具存取權；Windows 路徑需含磁碟代號。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q9

C-Q5: 如何在本機測試 API（以 8.8.8.8 為例）？
- A簡: 將 IPv4 轉為整數 134744072，呼叫 /api/ip2c/134744072 取得國家資訊。
- A詳: 具體實作步驟：1) 8.8.8.8 十六進位 0x08080808→十進位 134744072 2) 確認容器 IP（inspect）或對外埠 8000 3) 發出 GET http://<host:port>/api/ip2c/134744072。關鍵程式碼片段（轉換）：(ipv4>>24)&0xFF ... 組合為字串。注意事項：Windows NAT 本機測試用容器 IP:80；檔案需先由 Worker 更新完成。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q17

C-Q6: 如何查看容器日誌與診斷更新流程？
- A簡: 用 docker ps 找容器，docker logs <id> 查看 stdout，必要時 docker exec 進入檢查檔案。
- A詳: 具體實作步驟：1) docker ps -a 2) docker logs <container-id> 觀察 wait/update 訊息 3) docker exec -it <id> cmd 進入容器 4) dir data 或 App_Data 驗證檔案更新。注意事項：若無輸出，確認程式是否寫 stdout；容器是否存活；必要時改 -it 互動模式重現問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, D-Q7

C-Q7: 如何撰寫 WebAPI Controller 以支援檔案熱更新？
- A簡: 用 MemoryCache 快取 Finder，綁定 HostFileChangeMonitor，檔案變更即失效重建。
- A詳: 具體實作步驟：1) 建立 LoadIPDB：讀取 ~/App_Data/ipdb.csv 2) 建立 CacheItemPolicy，加入 HostFileChangeMonitor 指向檔案 3) 快取 IPCountryFinder 4) 查詢流程取用快取實例。程式碼片段：
  - var cip=new CacheItemPolicy(); cip.ChangeMonitors.Add(new HostFileChangeMonitor(new List<string>{filepath}));
  - MemoryCache.Default.Add("storage:ip2c", new IPCountryFinder(filepath), cip);
  注意事項：確保 volume 掛載正確；檔案替換採改名，確保監看觸發。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q4

C-Q8: 如何撰寫 Worker 的下載、解壓與驗證程式碼？
- A簡: HttpClient 下載 GZipStream 解壓至 .temp，IPCountryFinder 驗證後原子替換。
- A詳: 具體實作步驟：1) 以 HttpClient 取得 ResponseStream 2) GZipStream 解壓寫入 temp 3) 用 IPCountryFinder(file) 測試固定 IP（如 168.95.1.1→TW）4) 刪除 .bak、將 .csv 改名 .bak 5) 將 .temp 改名 .csv。程式碼片段：GZipStream gzs=new GZipStream(source,CompressionMode.Decompress); while((count=gzs.Read(...))>0){fs.Write(...)}; 驗證：finder.GetCountryCode("168.95.1.1")=="TW"。注意事項：加入錯誤處理與重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q2

C-Q9: 如何推送映像至 Registry 並用 Compose 部署？
- A簡: 映像打 tag 並 push，Compose 定義服務、卷與埠，docker-compose up 啟動。
- A詳: 具體實作步驟：1) docker tag ip2c/webapi:latest myreg/webapi:1.0 2) docker push myreg/webapi:1.0（Worker 同步）3) 撰寫 docker-compose.yml：
  - services: reverse-proxy, webapi (image: myreg/webapi:1.0, ports: "80"), worker (image: myreg/worker:1.0); volumes: data:/shared/path
  - reverse-proxy 對外開放，路由至 webapi
  4) docker-compose pull && docker-compose up -d。注意事項：版本標籤清晰、機密不入映像、卷權限正確。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q16, B-Q15

C-Q10: 如何包裝並發佈 .NET SDK 至 NuGet？
- A簡: 於 csproj 設定 Package 資訊，dotnet/nuget pack 產生 nupkg，nuget push 發佈。
- A詳: 具體實作步驟：1) 在 .csproj 加入 <PackageId>、<Version>、<Authors>、<Description> 等 2) 執行 dotnet pack 或 nuget pack 3) 於 nuget.config 設定來源 4) nuget push <.nupkg> -Source <server>。注意事項：採語意化版本；含必要相依；發佈前測試；可於 CI 自動化進行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, A-Q11


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 本機無法用 localhost 存取容器埠怎麼辦（Windows NAT）？
- A簡: Windows NAT 不支援 loopback；以容器 IP:80 測試，或改用外機/透明網路。
- A詳: 症狀描述：docker run -p 8000:80 後，localhost:8000 不通。可能原因：Windows NAT 不支援回環。解決步驟：1) docker inspect 取容器 IP 2) 以 http://<容器IP>:80 測試 3) 或改在他機訪問宿主 8000 4) 進階：改用 transparent network。預防措施：開發文件明載限制與測試方式，或提供 compose 設定替代。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q18

D-Q2: Worker 下載或解壓失敗怎麼辦？
- A簡: 檢查網路與來源，加入重試與超時，驗證 GZip 正確性與磁碟權限。
- A詳: 症狀：更新迴圈顯示失敗或無 CSV 變更。原因分析：網路中斷、URL 改變、HTTP 非 200、GZip 壞檔、磁碟權限不足。解決步驟：1) 手動下載驗證 2) 設定 HttpClient 超時與重試 3) 檢查解壓流程與檔案大小 4) 確認 volume 可寫 5) 加入回退至 .bak。預防措施：健康檢查與告警、來源鏡像、指紋驗證與重試退避。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q8

D-Q3: WebAPI 沒讀到最新 CSV，如何排查？
- A簡: 檢查 volume 掛載一致、檔名原子替換、檔案監看是否生效與快取失效。
- A詳: 症狀：Worker 更新成功，WebAPI 查詢仍舊值。原因：不同掛載點、檔案未替換、監看未觸發或快取未失效。步驟：1) docker inspect 驗證兩容器掛載到同宿主路徑 2) 進容器比對檔案時間與大小 3) 確認以改名替換（非覆寫） 4) 檢視 WebAPI 程式快取與監看設定。預防：固定掛載點相同、原子替換策略、監看器單元測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q7

D-Q4: 啟動容器提示埠已被占用，如何處理？
- A簡: 更換宿主埠或釋放占用服務，避免與其他進程衝突。
- A詳: 症狀：docker run 報綁定失敗。原因：宿主埠已被其他服務使用。步驟：1) netstat -ano 找到占用 PID 2) 終止或變更該服務埠 3) 改用其他宿主埠，如 -p 8080:80 4) 更新反向代理設定。預防：規劃埠表與健康檢查，CI/CD 中埠衝突檢測。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q2

D-Q5: Volume 路徑錯誤導致容器啟動異常怎麼辦？
- A簡: 確認宿主目錄存在、路徑格式與權限正確，修正 -v 參數。
- A詳: 症狀：容器啟動報錯或應用找不到檔案。原因：Windows 路徑語法錯、目錄不存在、權限不足。步驟：1) 建立 d:\data 2) 確認使用 -v d:\data:c:\path 3) 檢查容器內符號連結目錄是否存在 4) 檢查 ACL。預防：啟動前建立目錄、用腳本檢查路徑、統一掛載規範。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q4

D-Q6: API 回傳 null 或國碼為空，怎麼排查？
- A簡: 檢查 IP 轉換、CSV 格式與內容、Finder 載入與錯誤處理。
- A詳: 症狀：CountryCode 為空或例外。原因：整數轉 IPv4 錯誤、CSV 格式變更、資料未載入或路徑錯誤。步驟：1) 單元測試轉換方法 2) 手查 CSV 是否含該段範圍 3) 檢視 LoadIPDB 檔案路徑與例外 4) 增加錯誤處理與預設回應。預防：強化輸入驗證、加測試案例、監控錯誤率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2, C-Q7

D-Q7: docker logs 沒輸出，如何診斷？
- A簡: 確認程式輸出至 stdout、容器正在運行、ENTRYPOINT 正確。
- A詳: 症狀：logs 空白。原因：程式寫檔案非 stdout、容器已退出、ENTRYPOINT/CMD 錯誤。步驟：1) 查看 docker ps 狀態 2) 以 -it 互動測試 3) 檢查程式是否用 Console.WriteLine 4) 檢視 Dockerfile 的 ENTRYPOINT 5) 容器退出碼判斷異常。預防：統一標準輸出、增加啟動日誌、健康檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q6

D-Q8: WebAPI 效能不佳的可能原因與優化？
- A簡: 檔案 I/O、快取使用不當、單實例瓶頸；可用快取、擴容與反向代理。
- A詳: 症狀：高延遲或吞吐不足。原因：反覆讀檔、Finder 未重用、單實例無擴展、反向代理無快取。步驟：1) 確保 IPCountryFinder 置於記憶體 2) 擴增 WebAPI 副本 3) SDK 客端快取 4) 反向代理微快取 5) 監控與壓測。預防：設計期即無狀態、預備擴展，加入觀測指標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q12, A-Q11

D-Q9: 容器無法連網的常見原因與解法？
- A簡: NAT 或 DNS 問題、代理限制；檢查網路設定、DNS、代理與防火牆。
- A詳: 症狀：Worker 無法下載。原因：NAT 失效、DNS 配置錯、需經 Proxy、企業防火牆阻擋。步驟：1) docker network inspect nat 2) 設定 DNS（--dns） 3) 設定 HTTP(S)_PROXY 環境變數 4) 確認防火牆放行 5) 宿主可否直接訪問。預防：建置前網路健檢、紀錄依賴端點與 Proxy 設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q3

D-Q10: 以 Compose 多容器部署後出現 403/404，怎麼排查？
- A簡: 檢查反向代理路由、服務名稱與埠、卷掛載與 YAML 縮排。
- A詳: 症狀：外部可達代理，但後端返回 4xx。原因：代理路由錯、端口不符、服務名稱誤、卷無資料。步驟：1) 檢查 compose.yml 路由與目標 2) 確認 webapi service 暴露 80 並健康 3) 日誌比對代理與後端 4) 檢查卷是否掛載同一路徑。預防：以範本與驗證工具檢查 YAML，加入健康檢查與啟動順序。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q16, C-Q9


### 學習路徑索引

- 初學者：建議先學習 15 題
    - A-Q1: 什麼是容器驅動開發（Container Driven Development）？
    - A-Q2: 什麼是微服務架構？
    - A-Q3: 為什麼 IP 所屬國家查詢適合做成微服務？
    - A-Q4: 容器化與傳統部署有什麼差異？
    - A-Q6: 什麼是 Docker 映像（Image）與容器（Container）？
    - A-Q7: 什麼是 Dockerfile？
    - A-Q10: 案例中有哪些核心組件（服務與專案）？
    - A-Q12: 為什麼需要高可用（HA）與可擴展（Scalability）？
    - A-Q13: Docker Volume 與傳統共享資料夾有何差異？
    - B-Q1: IP2C.WebAPI 的查詢流程如何運作？
    - B-Q5: WebAPI 的 Dockerfile 架構與作用是什麼？
    - C-Q1: 如何建置 IP2C.WebAPI 的 Docker 映像？
    - C-Q2: 如何執行 WebAPI 容器並對外開放埠？
    - C-Q5: 如何在本機測試 API（以 8.8.8.8 為例）？
    - C-Q6: 如何查看容器日誌與診斷更新流程？

- 中級者：建議學習 20 題
    - A-Q5: Windows Container 與 Linux Container 有何差異？
    - A-Q8: 什麼是不可變伺服器（Immutable Server）？
    - A-Q11: 為什麼要提供 SDK 並內建客端快取？
    - A-Q14: Docker 的三大配置通道是什麼？
    - A-Q15: 為何選擇 Console App + 容器取代 Windows 服務？
    - A-Q16: 什麼是 CI/CD？本案例如何設計？
    - A-Q17: 什麼是 NAT loopback 限制（Windows Container）？
    - B-Q2: 將整數轉為 IPv4 的機制是什麼？
    - B-Q3: MemoryCache 與 HostFileChangeMonitor 如何實現資料熱更新？
    - B-Q4: IP2C.Worker 的自動更新機制如何設計？
    - B-Q7: 為何以 volume 實現 Worker→WebAPI 的資料流？
    - B-Q8: docker run -p 的埠對應原理是什麼？
    - B-Q9: docker run -v 在 Windows 上如何掛載路徑？
    - B-Q10: 容器日誌如何收集與查看？
    - B-Q14: NuGet 在 SDK 發佈中扮演什麼角色？
    - B-Q16: Docker Compose 在多容器部署中的設計概念？
    - C-Q3: 如何建置並執行 IP2C.Worker 容器？
    - C-Q4: 如何用 volume 讓 WebAPI 與 Worker 共用 CSV？
    - C-Q7: 如何撰寫 WebAPI Controller 以支援檔案熱更新？
    - C-Q8: 如何撰寫 Worker 的下載、解壓與驗證程式碼？

- 高級者：建議關注 15 題
    - B-Q11: 反向代理與負載分配的基本機制是什麼？
    - B-Q12: 如何在容器環境達成高可用與水平擴展？
    - B-Q13: 本案例的 CI/CD 流程技術架構如何設計？
    - B-Q15: Docker Registry 的角色是什麼？
    - B-Q17: SDK 的客戶端快取原理與設計重點？
    - B-Q18: Windows NAT 網路與容器 IP 取得機制？
    - C-Q9: 如何推送映像至 Registry 並用 Compose 部署？
    - C-Q10: 如何包裝並發佈 .NET SDK 至 NuGet？
    - D-Q1: 本機無法用 localhost 存取容器埠怎麼辦（Windows NAT）？
    - D-Q2: Worker 下載或解壓失敗怎麼辦？
    - D-Q3: WebAPI 沒讀到最新 CSV，如何排查？
    - D-Q8: WebAPI 效能不佳的可能原因與優化？
    - D-Q9: 容器無法連網的常見原因與解法？
    - D-Q10: 以 Compose 多容器部署後出現 403/404，怎麼排查？
    - A-Q8: 什麼是不可變伺服器（Immutable Server）？
{% endraw %}