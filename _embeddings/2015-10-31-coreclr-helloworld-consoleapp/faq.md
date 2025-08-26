# 在 Docker 上面執行 .NET (CoreCLR) Console App

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 .NET Core CLR？
- A簡: 可跨平台的 .NET 執行時環境，含 JIT 與可裁剪 BCL，支援 Linux/Mac，能隨應用並存與佈署。
- A詳: CLR 是能執行 .NET IL 的執行時環境，含 JIT 與基底類別庫（BCL）。Core CLR 是為跨平台重構的版本，支援 Linux、macOS，並以模組化 NuGet 套件形式提供 BCL，可按需裁剪，減少體積。它支援應用層級的並存佈署，不依賴機器全域安裝，對容器化與持續交付特別友善。本文情境以 CoreCLR 為基礎在 Docker 內執行 Console App，展現其跨平台能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q6, B-Q11

A-Q2: .NET Framework 與 .NET Core CLR 有何差異？
- A簡: Framework 功能完整且偏向 Windows；Core CLR 輕量、可裁剪、跨平台，支援容器與並存佈署。
- A詳: .NET Framework 提供完整 BCL 與 Windows 整合，常用於傳統 Windows 伺服器環境。Core CLR 以跨平台為核心，將 BCL 套件化，按需引用，減少部署體積；支援應用並存版本與容器化場景。功能覆蓋度初期較精簡，但更易於在 Linux/macOS 與 Docker 等環境運行，對現代化架構與混搭部署更具彈性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q8, B-Q8

A-Q3: 什麼是 DNX（.NET Execution Environment）？
- A簡: DNX 是 ASP.NET 5/.NET 應用的執行環境與啟動器，類似 Java 的 java.exe。
- A詳: DNX 負責啟動並承載 .NET 應用，讀取專案設定（如 project.json），載入對應 Runtime 與相依套件，並執行指派的命令（如 run）。在本文的 Console App 案例中，透過 dnx 命令在容器內啟動程式。DNX 與 DNVM、DNU 搭配，形成安裝、相依管理與執行的基本工具鏈。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, A-Q6, B-Q2

A-Q4: 什麼是 DNVM（.NET Version Manager）？
- A簡: DNVM 是 DNX 版本管理工具，負責安裝、升級、切換不同 Runtime 與架構。
- A詳: DNVM 讓開發者在同一台機器或容器內共存多版本 DNX（如 coreclr/mono、x64/x86），並可快速切換使用。常用指令包含 dnvm list、dnvm install、dnvm upgrade、dnvm use。本文在容器內以 dnvm list 確認可用版本，再選用 coreclr x64，確保 Console App 以 CoreCLR 執行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, B-Q3

A-Q5: 什麼是 DNU（.NET Utilities）？
- A簡: DNU 是開發工具列，負責 restore 套件、build 與發佈相關操作。
- A詳: DNU 提供建置與相依套件管理功能。最常用的 dnu restore 會解析專案的相依關係，從 NuGet 擷取缺少的套件並快取。也可執行 dnu build 產生組件。本案例中，進入 dnxcore50 目錄後先 dnu restore，確保所有相依已就緒，最後才用 dnx 執行 Console App。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, B-Q4, C-Q8

A-Q6: DNX、DNVM、DNU 彼此的關係是什麼？
- A簡: DNVM 管理與切換 DNX；DNU 管理相依與建置；DNX 作為應用啟動器。
- A詳: 工具鏈分工清楚：DNVM 管理多版本 Runtime（安裝、升級、選用），DNU 處理相依套件與建置，DNX 依據專案設定啟動應用。工作流程通常是：用 DNVM 準備/選用 Runtime，用 DNU 下載相依，最後用 DNX 執行。本文即沿此路徑在 Docker 內完成 Console App 執行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, A-Q5, B-Q2

A-Q7: 為什麼要在 Linux 上執行 .NET 應用？
- A簡: 降低成本、擴大部署彈性、支援容器化與混搭架構，利於現代化雲端營運。
- A詳: 微軟將 .NET 開源與跨平台化，使 .NET 能在 Linux 上穩定運行。對系統架構師而言，這意味著可在多平台採用一致技術堆疊，根據成本、資源與擴展需求做彈性部署。搭配 Docker，可提升密度、交付速度與可移植性，讓 .NET 與 Linux 生態工具協作，擴大應用場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q15, B-Q14

A-Q8: 什麼是 Docker？為何與 .NET Core 相輔相成？
- A簡: Docker 是應用層容器，打包執行環境與相依，啟動快、佔用少，適合 .NET Core 部署。
- A詳: Docker 藉由 OS 隔離與資源控制，將應用與其相依封裝為映像，執行為容器。容器啟動時間短、資源效率高、可移植性強，能將 .NET Core 的模組化與並存部署優勢發揮到極致。在本文中，作者使用官方 ASP.NET 5 CoreCLR 映像，省去手動安裝 Runtime 的成本，快速驗證 Console App。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q1, C-Q2

A-Q9: Docker 與虛擬機（VM）有何不同？
- A簡: VM 虛擬整個 OS；容器僅隔離應用與相依。容器更輕量、密度高、啟動快。
- A詳: VM 需為每個實例安裝完整 OS，管理成本與資源開銷較大（如多台 VM 同時掃毒拖垮主機）。容器共享宿主 OS 核心，僅打包應用所需檔案與設定，啟動秒級、資源效率更高。對中小規模服務，容器能保留合理的分層/分離，同時避免 VM 過度切分造成的效能與維運負擔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q1, D-Q10

A-Q10: 為什麼用容器部署可維持理想架構而不犧牲效能？
- A簡: 容器將服務拆分獨立執行，隔離清晰、開銷小，利於微型化與擴展。
- A詳: 傳統三層若硬切成多 VM，常帶來管理與資源浪費。容器化允許將服務按職責拆分為多個容器，透過網路與設定連結，保留架構正確性與可觀測，且在單機或小型叢集中仍具良好效能與密度。這讓理想設計不必為硬體成本或啟動時間折衷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q9, D-Q10

A-Q11: 什麼是「ASP.NET 5 Preview Docker Image」？
- A簡: 微軟預打包含 DNX/CoreCLR 的官方映像，能直接啟動，快速進入開發/測試。
- A詳: 在 beta8 時期，微軟於 Docker Hub 提供 microsoft/aspnet:1.0.0-beta8-coreclr 等映像，預裝 DNVM、DNX、DNU 與必要依賴，讓開發者免去在 Linux 手動配置 Runtime 的繁瑣步驟。本文即以此映像為基礎容器，透過 docker exec 進入後執行工具鏈與 Console App。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q2, C-Q3

A-Q12: 為何選用現成官方映像而非自行建包？
- A簡: 減少環境安裝風險與時間，專注在應用驗證；適合入門與快速試作。
- A詳: 對非 Linux 背景的開發者，採用官方映像能快速獲得可用環境，避免在 Runtime 安裝與設定上耗費心力。本文作者即以「不先包自有映像」為策略：用 docker exec 進入容器、放入程式、restore 相依後直接執行；待需求成熟再改以 Dockerfile 建制流水線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, C-Q6, C-Q10

A-Q13: 什麼是 Docker Toolbox 與 Boot2Docker？
- A簡: Windows 使用者的一鍵工具包，含 Docker 客戶端、VirtualBox 與精簡 Linux（Boot2Docker）。
- A詳: 在早期 Windows 上，Docker Toolbox 透過 VirtualBox 啟動 Boot2Docker（精簡 Linux），同時安裝 Docker 客戶端，協助沒有原生 Docker 的環境快速上手。本文建議若無 NAS 或 Linux 主機，可使用 Toolbox 快速準備容器執行環境進行實驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q14

A-Q14: POC 與實際營運環境練習的差異？
- A簡: POC 僅驗證能跑；實務需涵蓋備份、反向代理、升級與維運流程。
- A詳: 只做 POC 易忽略線上營運必要項，如 reverse proxy 的路由與埠管理、備份還原、監控、升級、災難復原等。本文作者以將部落格容器化、在 NAS 配置 reverse proxy 與備份為練習目標，來獲得完整經驗，避免只停留在「能跑」層級。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q10, D-Q6

A-Q15: 何謂「混搭」架構？為何重要？
- A簡: 不同平台與技術共存協作的部署設計，提升彈性與成本效率，影響長期生態。
- A詳: 混搭架構允許在 Windows 與 Linux 上以最適技術承載不同子系統，再以 API、消息或反向代理整合。隨 .NET 跨平台與容器化，.NET 與現有 Linux 工具鏈可協作，讓系統在性能、成本、團隊技能與雲端策略上取得平衡。對架構師，這是部署與擴展決策的核心。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, B-Q15

### Q&A 類別 B: 技術原理類

B-Q1: Docker 容器如何達成隔離並啟動應用？
- A簡: 以命名空間與 cgroups 實現進程/檔案/網路隔離，映像分層，容器快速啟動。
- A詳: Docker 利用 Linux namespaces 隔離 PID、網路、檔案系統與使用者空間，並用 cgroups 控制資源（CPU、記憶體）。映像以分層檔案系統構成，容器在最上層提供可寫層。啟動流程為從映像建立容器，執行指定 entrypoint 或命令。本文以官方映像為基礎，啟動後再 docker exec 進入容器，於隔離環境內操作 DNX 工具鏈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q9, B-Q6

B-Q2: DNX 的運作流程是什麼？
- A簡: 讀取專案設定與相依，載入選定 Runtime，初始化應用，執行對應命令。
- A詳: DNX 啟動時會定位專案（含 project.json），解析 commands 與 target frameworks，並從本機快取讀取套件。依據 DNVM 選定的 Runtime（如 coreclr/x64）載入執行引擎與 BCL，將應用組件與相依組態注入，最後執行既定命令（如 dnx run）。若相依缺漏，應先以 dnu restore 補齊。Console App 流程同理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q6, C-Q9

B-Q3: DNVM 如何管理多版本 DNX？
- A簡: 透過本機快取與別名切換，支援安裝、升級、列出與選用不同 Runtime。
- A詳: DNVM 維護多版本 DNX 的安裝位置與設定，常見於使用者家目錄下的 .dnx 路徑。指令 dnvm list 顯示可用版本，dnvm install 下載新版本，dnvm upgrade 升級至最新版，dnvm use 切換當前會話使用版本。也可設定別名便於切換。本文在容器中先確認 coreclr x64 版本，再進行還原與執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q7, D-Q4

B-Q4: DNU restore/build 的機制為何？
- A簡: 解析 project.json 相依，從 NuGet 抓取套件並快取；build 編譯產出組件。
- A詳: dnu restore 會讀取 project.json 的 dependencies 與 frameworks，解析版本範圍，向 NuGet feed 下載缺少套件，存入本機快取（減少重複下載）。網路與來源設定影響速度與成功率。dnu build 則據此編譯專案生成組件。本文重點在 restore，確保容器內能離線重用快取並順利由 dnx 啟動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q8, D-Q1

B-Q5: microsoft/aspnet:1.0.0-beta8-coreclr 映像包含哪些？
- A簡: 預裝 DNVM/DNX/DNU 與 CoreCLR 相關相依，提供可直接啟動的執行環境。
- A詳: 該官方映像於 beta8 時期為開發者預打包好 CoreCLR 相關工具鏈與必要系統元件，省去在 Linux 中安裝設定 DNX 的流程。啟動容器後，即可使用 dnvm、dnu、dnx 指令。本文即採此映像，進入容器放入專案，再 restore 與執行，快速驗證 Console App 在 Linux 的可行性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q2, C-Q4

B-Q6: docker run、ps、exec 分別做什麼？
- A簡: run 啟動容器，ps 列出容器狀態，exec 進入既有容器執行指令或互動。
- A詳: docker run 基於映像建立並啟動容器，可加 -d 背景執行、--restart always 設定重啟策略。docker ps -a 檢視所有容器及其 ID/狀態。docker exec -it <id> /bin/bash 會在既有容器內啟動互動式 bash，方便檢視與操作。本文以這三步完成容器管理與進入環境的流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q4, D-Q2

B-Q7: 為何可在容器內開第二個 shell 互動？
- A簡: 容器本質是隔離的進程集合，可同時執行多進程；exec 會新增一個進程。
- A詳: 容器啟動時通常有一個主進程（PID 1），但可以再透過 docker exec 啟動其他進程，例如 bash，以便除錯或維運。雖常建議一容器一進程，但在開發/排錯階段，附加互動 shell 可提升效率。本文即以 exec -it 進入，像 SSH 到一台輕量主機般操控 DNX 工具。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q9, D-Q2

B-Q8: .NET Core 的 BCL 可裁剪性原理是什麼？
- A簡: 以 NuGet 套件拆分 BCL，按需引用、減少體積，支援跨平台差異。
- A詳: CoreCLR 將傳統單體式 BCL 切為多個 System.* 套件，根據目標框架與平台選擇最小相依。這讓不同應用只帶入需要的 API，改善容器映像大小與冷啟動時間。也能針對平台差異提供對應實作，提升可攜性與彈性。本文場景即受惠於此特性，快速在 Linux 容器啟動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q2, B-Q11

B-Q9: 容器可同時跑多進程有何影響？
- A簡: 可靈活除錯與側工具，但要確保主進程生命週期與監控正確。
- A詳: 雖可同時執行多進程，但容器的存活取決於主進程（PID 1）。若主進程結束，容器即終止。附加的 bash 或工具進程適合除錯，但不宜成為常態依賴。建議以監控/日誌方案外掛，並正確設計 entrypoint 與重啟策略，避免行為不確定。本文用 exec 僅作臨時互動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q4, D-Q6

B-Q10: docker cp 的工作原理是什麼？
- A簡: 在宿主與容器檔案系統間複製檔案，無需 SSH/網路服務，直接對本地引擎操作。
- A詳: docker cp 透過 Docker 引擎直接讀寫容器層檔案系統，支援單檔或目錄複製，語法如 docker cp src <container>:/dest。權限與目標路徑需正確，容器可在執行中或停止狀態。本文以此將 VS 編譯產物拷入 /home/ConsoleApp1 供容器內執行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, D-Q5

B-Q11: dnxcore50 與其他目標框架的關係？
- A簡: dnxcore50 代表在 CoreCLR 上的 .NET 平台；dnx451 等則對應完整 .NET Framework。
- A詳: 專案可多目標框架（TFM）。dnxcore50 針對 CoreCLR，適合跨平台與容器；dnx451 等針對完整 Framework，功能較全但偏向 Windows。選錯 TFM 會導致相依解析與執行失敗。本文刻意以 dnxcore50 執行 Console App，以驗證在 Linux 容器上的跨平台能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, C-Q8, D-Q8

B-Q12: 為什麼 dnu restore 需要網路？其快取如何運作？
- A簡: 相依套件需自 NuGet 下載；成功後快取本機，供後續還原/編譯重用。
- A詳: dnu restore 解析相依後，連線至設定的 NuGet 源抓取套件，首次較慢。完成後套件存於本機快取，後續相同版本無需再下載，提升速度；也可離線重用。若網路或 DNS 異常，restore 會失敗。本文場景依賴此快取機制在容器中提升迭代效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, D-Q1, D-Q9

B-Q13: Visual Studio 在此流程中的角色？
- A簡: 負責開發與編譯產物；容器僅作運行時。藉 docker cp 將產物放入容器再執行。
- A詳: 本文採「本機開發、容器運行」模式：在 VS2015 建立 Console App，產出二進位與 project.json，然後用 docker cp 放入容器。容器中以 dnvm/dnu/dnx 確認相依與執行。此分離讓開發工具保持熟悉，而運行環境靠官方映像保證一致性與可移植。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q6, C-Q9

B-Q14: NAS 上的 Docker 與自架 Linux 有何差異？
- A簡: NAS 多提供易用 GUI 與整合儲存/備份；自架 Linux 彈性高但需自行維護。
- A詳: NAS（如 Synology/QNAP）內建 Docker 管理介面，簡化容器生命週期與映像管理，並整合儲存、備份。自架 Linux 需以 CLI 或自行選用 Web UI 管理，學習曲線較陡，但彈性更高。本文先在 NAS 練習，再自架 Ubuntu 熟悉底層，利於未來實戰部署。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q12, C-Q1

B-Q15: Reverse Proxy 在容器化架構中的角色是？
- A簡: 統一對外端點與路由，隱藏內部容器埠/URL，便於多服務協作與維運。
- A詳: 在多容器場景，Reverse Proxy（如 Nginx）負責接收外部流量，依路徑/主機名/埠代理到對應容器，解決埠衝突與多服務共存問題，並可加上 TLS、壓縮與快取策略。本文作者在實作 WordPress 時透過 RP 歸位對外 URL/Port，確保門面與維運一致性。此觀念同樣適用 .NET 服務。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q10, D-Q6

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何快速準備 Docker 執行環境（NAS 或 Docker Toolbox）？
- A簡: NAS 直接安裝 Docker 套件；無 NAS 可在 Windows 裝 Docker Toolbox（含 VirtualBox/Boot2Docker）。
- A詳: 具體步驟：1) 若有 Synology/QNAP，於套件中心安裝 Docker，啟用後即可透過 GUI 管理。2) Windows 無原生 Docker 時，安裝 Docker Toolbox，完成後會有 Docker 客戶端與以 VirtualBox 啟動的 Boot2Docker 虛機。3) 驗證：執行 docker version、docker info 確認可用。注意：Toolbox 適合入門與舊環境，確保 BIOS 啟用虛擬化並分配足夠 RAM/CPU。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q14

C-Q2: 如何拉取 microsoft/aspnet:1.0.0-beta8-coreclr 映像？
- A簡: 使用 docker pull 從 Docker Hub 下載官方 CoreCLR 預裝映像。
- A詳: 在 Docker 主機執行： 
  指令：
  ```
  sudo docker pull microsoft/aspnet:1.0.0-beta8-coreclr
  ```
  完成後以 docker images 檢視映像是否到位。此映像預裝 DNVM/DNX/DNU，省去在 Linux 安裝 .NET Runtime。注意：連線需可達 Docker Hub；企業環境可預先同步私有 Registry。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q5

C-Q3: 如何啟動容器並設定常駐重啟？
- A簡: 使用 docker run -d 與 --restart always 背景啟動容器，自動重啟維持常駐。
- A詳: 指令：
  ```
  sudo docker run -d --restart always microsoft/aspnet:1.0.0-beta8-coreclr
  ```
  說明：-d 背景執行；--restart always 在 Docker 服務啟動或容器異常時自動重啟。可用 --name 命名容器便於管理。啟動後以 docker ps 驗證狀態。注意：未指定 entrypoint 時以映像預設進程啟動；確保主進程正常運作，否則容器會退出。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q6

C-Q4: 如何查詢容器 ID 並進入互動式 Bash？
- A簡: 先 docker ps -a 取得 ID，再以 docker exec -it <ID> /bin/bash 進入容器。
- A詳: 步驟：1) 查詢容器：
  ```
  sudo docker ps -a
  ```
  2) 進入互動式 bash：
  ```
  sudo docker exec -it <CONTAINER_ID> /bin/bash
  ```
  成功後提示符會變為 root@<容器ID>:/#。注意：-i/-t 提供互動與終端；容器需在執行中。無法進入時檢查容器狀態與 shell 是否存在（/bin/bash 或 /bin/sh）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q7, D-Q2

C-Q5: 如何在 Visual Studio 2015 建立 .NET Core Console App（Hello World）？
- A簡: 建立 Console 專案，撰寫主程式輸出文字，產生 project.json 與編譯產物。
- A詳: 步驟：1) 在 VS2015 建立 ASP.NET 5 Console App（或對應範本）；2) 確認 project.json 目標框架含 "dnxcore50"；3) 編寫程式：
  程式碼：
  ```
  using System;
  public class Program {
      public static void Main(string[] args) {
          Console.WriteLine("Hello .NET Core!");
      }
  }
  ```
  4) 建置專案產生輸出。注意：確保產物與 project.json 一併準備，供容器內 dnu restore 與 dnx 執行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, B-Q11

C-Q6: 如何把編譯結果拷入容器（docker cp）？
- A簡: 使用 docker cp 將本機專案或輸出目錄複製到容器指定路徑。
- A詳: 指令示例：
  ```
  sudo docker cp ./ConsoleApp1 <CONTAINER_ID>:/home/ConsoleApp1
  ```
  或複製單檔：
  ```
  sudo docker cp ./project.json <CONTAINER_ID>:/home/ConsoleApp1/
  ```
  進容器檢查：
  ```
  ls -la /home/ConsoleApp1
  ```
  注意：目標目錄需存在或可由 cp 建立；留意大小寫與權限。路徑建議簡潔（如 /home/ConsoleApp1）便於定位。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, D-Q5

C-Q7: 如何在容器內用 dnvm list 選擇 coreclr x64？
- A簡: 使用 dnvm list 檢視版本；如需切換用 dnvm use（或先 dnvm install）選擇 coreclr x64。
- A詳: 在容器 bash：
  ```
  dnvm list
  dnvm install 1.0.0-beta8 -r coreclr -arch x64   # 如需
  dnvm use 1.0.0-beta8 -r coreclr -arch x64
  ```
  驗證目前版本顯示為 coreclr/x64。注意：不同映像可能已預裝多版本；切換後僅對當前 shell 有效（可設定別名或寫入啟動腳本以持久化）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q4

C-Q8: 如何在 dnxcore50 目錄執行 dnu restore？
- A簡: 切換到包含 project.json 的 dnxcore50 專案路徑，執行 dnu restore 下載相依。
- A詳: 操作：
  ```
  cd /home/ConsoleApp1/dnxcore50
  dnu restore
  ```
  成功時會顯示已還原的套件清單。注意：需有有效的網路與 NuGet 源；失敗時檢查 DNS/Proxy 或改用國內鏡像。恢復完成後相依會快取，後續執行更快。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q12, D-Q1

C-Q9: 如何用 dnx 執行 Console App 並驗證環境？
- A簡: 在專案目錄執行 dnx run，顯示 Hello 訊息；可附加系統資訊確認運行於 Linux。
- A詳: 操作：
  ```
  cd /home/ConsoleApp1/dnxcore50
  dnx run
  ```
  輸出應含 "Hello .NET Core!"。為避免混淆可同時輸出 OS 資訊或在提示符觀察 root@<容器ID>。注意：若找不到命令或相依，先確認 dnvm use 與 dnu restore 已正確完成。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q3

C-Q10: 如何將流程封裝為腳本或 Dockerfile 以便重現？
- A簡: 可撰寫 bash 腳本自動化 cp/restore/run；或用 Dockerfile FROM 官方映像封裝應用。
- A詳: 兩種方式：1) 腳本（適合開發期）：
  ```
  docker cp ./ConsoleApp1 <ID>:/home/ConsoleApp1
  docker exec -it <ID> bash -lc "cd /home/ConsoleApp1/dnxcore50 && dnu restore && dnx run"
  ```
  2) Dockerfile（適合部署）：
  ```
  FROM microsoft/aspnet:1.0.0-beta8-coreclr
  COPY ./ConsoleApp1 /app
  WORKDIR /app/dnxcore50
  RUN dnu restore
  CMD ["dnx", "run"]
  ```
  注意：本文策略先不建包以加速驗證；正式化時再以 Dockerfile 固化流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q5, A-Q14

### Q&A 類別 D: 問題解決類（10題）

D-Q1: dnu restore 失敗或下載很慢怎麼辦？
- A簡: 檢查網路/DNS/Proxy，改用近端 NuGet 源或預熱快取，必要時重試與清理。
- A詳: 症狀：restore 超時、404、名稱解析失敗。可能原因：無法連到 NuGet、DNS 緩慢、代理限制。解法：1) 設定近端/鏡像來源；2) 確認 DNS（/etc/resolv.conf）與 Proxy；3) 重試或清理快取；4) 離線部署時先在可連線環境預熱快取再打包。預防：固定 NuGet 源、納入 CI 快取流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8

D-Q2: docker exec -it 無法進入 Bash 怎麼辦？
- A簡: 確認容器在執行、ID 正確、bash 存在；必要時改用 /bin/sh 或重新啟動容器。
- A詳: 症狀：exec 連線即斷、找不到 /bin/bash。原因：容器已退出、映像無 bash、權限不足。解法：1) docker ps 檢查狀態；2) 用 /bin/sh 嘗試；3) 以 docker logs 觀察主進程錯誤；4) 重新以 --name 管理並啟動；5) 確認 Docker 版本。預防：選用含 bash 的映像或在 Dockerfile 安裝必要 shell。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q4

D-Q3: dnx 執行時找不到相依套件如何處理？
- A簡: 回到專案目錄執行 dnu restore，確認正確目標框架與 runtime 已選用。
- A詳: 症狀：Missing assembly/package、無法解析依賴。原因：未 restore、目標框架不符、NuGet 源缺失。解法：1) 確保在含 project.json 的目錄 dnu restore；2) 使用 dnvm use 選擇 coreclr x64；3) 檢查 project.json 的 frameworks 與 dependencies；4) 清快取後重試。預防：建立一致的還原腳本與 CI 流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q11, C-Q8

D-Q4: 容器內沒有 dnvm/dnx/dnu 指令怎麼辦？
- A簡: 確認使用正確官方映像；或在容器內安裝 DNX 工具，載入對應環境設定。
- A詳: 症狀：command not found。原因：使用錯映像、PATH 未載入、工具未安裝。解法：1) 改用 microsoft/aspnet:1.0.0-beta8-coreclr；2) 檢查環境變數是否正確載入；3) 參考官方指引於 Linux 安裝 DNX；4) 用 which dnx 驗證路徑。預防：固定基底映像並版本控管。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q2, C-Q7

D-Q5: docker cp 報路徑錯誤或權限不足如何排查？
- A簡: 驗證源/目標路徑存在與大小寫；切換到具權限目錄，必要時調整目錄權限。
- A詳: 症狀：no such file or directory、permission denied。原因：路徑大小寫錯、目標不可寫、目錄不存在。解法：1) 檢查本機與容器路徑正確性；2) 先在容器建立目錄（mkdir -p）；3) 確保以 root 或具寫入權限用戶執行；4) 盡量避免特殊字元與空白路徑。預防：規範專案目錄結構與名稱。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q6

D-Q6: 容器意外停止或重啟，如何維持狀態與可用性？
- A簡: 設定 --restart 策略，將資料外掛卷，使用反向代理與健康檢查監控。
- A詳: 症狀：容器頻繁退出、服務中斷。原因：主進程錯誤、資源不足、未設重啟策略。解法：1) --restart always；2) 資料放 Volume，避免容器刪除丟失；3) 加入 reverse proxy 做流量承接；4) 使用監控與自動重啟機制。預防：健康檢查、資源限制、日誌觀測與自動化部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q15, C-Q3

D-Q7: Console App 在 Linux 不執行或異常（路徑/大小寫/換行）？
- A簡: 檢查檔名大小寫、路徑分隔符與換行格式，確保檔案權限與執行目錄正確。
- A詳: 症狀：找不到檔案、執行路徑錯誤、文字檔解析異常。原因：Windows/Linux 大小寫與換行差異、路徑分隔符不同。解法：1) 調整為一致大小寫與使用 / 分隔符；2) 以 dos2unix 轉換換行；3) 確認在包含 project.json 的目錄執行；4) 檢查檔案權限。預防：跨平台開發遵循約定，CI 上做格式檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, C-Q8, C-Q9

D-Q8: 選錯目標框架（dnx451 vs dnxcore50）怎麼處理？
- A簡: 修改 project.json 指向 dnxcore50，調整相依套件，重新 restore 與執行。
- A詳: 症狀：Linux 執行失敗或相依解析錯。原因：專案目標為完整 Framework（dnx451）而非 CoreCLR。解法：1) 編輯 project.json frameworks 為 "dnxcore50"；2) 替換不相容 API；3) 重新 dnu restore；4) 驗證 dnx run。預防：建立跨平台模板與守門檢查，避免誤用 TFM。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q5, C-Q8

D-Q9: 宿主機網路或 DNS 導致 NuGet 解析失敗怎排查？
- A簡: 測試 DNS/路由，指定穩定 DNS，配置 NuGet 源鏡像或離線快取。
- A詳: 症狀：restore 报 DNS 错误或名称解析超时。解法：1) 宿主與容器內分別 ping/ nslookup 測試；2) 調整 /etc/resolv.conf 使用穩定 DNS；3) 在 NuGet.Config 指定鏡像；4) 如有代理，設定環境變數；5) 緩存相依套件供離線使用。預防：在 CI/CD 中預熱快取，固定可用源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8

D-Q10: 容器效能不佳的常見原因與優化？
- A簡: 資源競爭、映像膨脹、I/O 瓶頸；優化資源限制、裁剪映像、監控與調參。
- A詳: 症狀：高延遲/吞吐下降。原因：CPU/記憶體爭用、過多容器並行、映像過大、磁碟/網路 I/O 慢。解法：1) 設置 CPU/Memory 限制與親和性；2) 裁剪映像與相依；3) 使用更快的存儲或調整 I/O 配置；4) 監控指標定位瓶頸；5) 合理分層服務避免過度切割。預防：容量規劃、壓測與持續觀測。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q9, A-Q10, B-Q1

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 .NET Core CLR？
    - A-Q2: .NET Framework 與 .NET Core CLR 有何差異？
    - A-Q3: 什麼是 DNX（.NET Execution Environment）？
    - A-Q4: 什麼是 DNVM（.NET Version Manager）？
    - A-Q5: 什麼是 DNU（.NET Utilities）？
    - A-Q6: DNX、DNVM、DNU 彼此的關係是什麼？
    - A-Q7: 為什麼要在 Linux 上執行 .NET 應用？
    - A-Q8: 什麼是 Docker？為何與 .NET Core 相輔相成？
    - A-Q9: Docker 與虛擬機（VM）有何不同？
    - B-Q5: microsoft/aspnet:1.0.0-beta8-coreclr 映像包含哪些？
    - B-Q6: docker run、ps、exec 分別做什麼？
    - C-Q2: 如何拉取 microsoft/aspnet:1.0.0-beta8-coreclr 映像？
    - C-Q3: 如何啟動容器並設定常駐重啟？
    - C-Q4: 如何查詢容器 ID 並進入互動式 Bash？
    - C-Q9: 如何用 dnx 執行 Console App 並驗證環境？

- 中級者：建議學習哪 20 題
    - B-Q1: Docker 容器如何達成隔離並啟動應用？
    - B-Q2: DNX 的運作流程是什麼？
    - B-Q3: DNVM 如何管理多版本 DNX？
    - B-Q4: DNU restore/build 的機制為何？
    - B-Q7: 為何可在容器內開第二個 shell 互動？
    - B-Q8: .NET Core 的 BCL 可裁剪性原理是什麼？
    - B-Q9: 容器可同時跑多進程有何影響？
    - B-Q10: docker cp 的工作原理是什麼？
    - B-Q11: dnxcore50 與其他目標框架的關係？
    - B-Q12: 為什麼 dnu restore 需要網路？其快取如何運作？
    - B-Q13: Visual Studio 在此流程中的角色？
    - C-Q5: 如何在 Visual Studio 2015 建立 .NET Core Console App（Hello World）？
    - C-Q6: 如何把編譯結果拷入容器（docker cp）？
    - C-Q7: 如何在容器內用 dnvm list 選擇 coreclr x64？
    - C-Q8: 如何在 dnxcore50 目錄執行 dnu restore？
    - C-Q10: 如何將流程封裝為腳本或 Dockerfile 以便重現？
    - D-Q1: dnu restore 失敗或下載很慢怎麼辦？
    - D-Q2: docker exec -it 無法進入 Bash 怎麼辦？
    - D-Q3: dnx 執行時找不到相依套件如何處理？
    - D-Q8: 選錯目標框架（dnx451 vs dnxcore50）怎麼處理？

- 高級者：建議關注哪 15 題
    - A-Q10: 為什麼用容器部署可維持理想架構而不犧牲效能？
    - A-Q14: POC 與實際營運環境練習的差異？
    - A-Q15: 何謂「混搭」架構？為何重要？
    - B-Q1: Docker 容器如何達成隔離並啟動應用？
    - B-Q8: .NET Core 的 BCL 可裁剪性原理是什麼？
    - B-Q9: 容器可同時跑多進程有何影響？
    - B-Q14: NAS 上的 Docker 與自架 Linux 有何差異？
    - B-Q15: Reverse Proxy 在容器化架構中的角色是？
    - C-Q10: 如何將流程封裝為腳本或 Dockerfile 以便重現？
    - D-Q4: 容器內沒有 dnvm/dnx/dnu 指令怎麼辦？
    - D-Q5: docker cp 報路徑錯誤或權限不足如何排查？
    - D-Q6: 容器意外停止或重啟，如何維持狀態與可用性？
    - D-Q7: Console App 在 Linux 不執行或異常（路徑/大小寫/換行）？
    - D-Q9: 宿主機網路或 DNS 導致 NuGet 解析失敗怎排查？
    - D-Q10: 容器效能不佳的常見原因與優化？