# 同場加映: 用 Synology NAS 的 Docker 環境，執行 .NET Core CLR Console App

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Synology NAS 的 Docker 環境？
- A簡: Synology 在 DSM 提供的 Docker 套件與圖形介面，用於管理映像與容器的輕量化執行環境。
- A詳: Synology 在其 DiskStation Manager(DSM) 系統中提供 Docker 套件，整合了映像管理、Registry 搜尋、容器建立、資源限制與終端機存取等功能。使用者不需手動安裝 Linux 與 Docker，即可透過圖形介面完成映像拉取、容器啟動與目錄掛載。對想快速驗證技術、部署測試服務或運行 .NET Core 應用的人而言，這是一條低摩擦的入門路徑，特別適合不追求極致效能但重視便利與穩定的場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, B-Q1

A-Q2: 什麼是 .NET Core CLR Console App？
- A簡: 以 .NET Core 執行時為基礎的跨平台主控台應用程式，採用精簡相依與命令列執行。
- A詳: .NET Core CLR Console App 是建立於 .NET Core 執行時上的主控台程式，具備跨平台、模組化套件相依、精簡部署的特性。文章示範使用 Visual Studio 2015 與 DNX Core 5.0 建立「Hello World」範例，再封裝至容器執行。此類應用適合服務工具、批次處理、任務排程與教學驗證。相較傳統 .NET Framework，.NET Core 更強調可攜性與雲端/容器場景的輕量化需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q5, B-Q21

A-Q3: DNX Core 5.0 是什麼？
- A簡: 早期 .NET Core 的執行與工具模型，使用 dnx/dnu 啟動與還原套件。
- A詳: DNX(DotNet eXecution) Core 5.0 是 .NET Core 早期(預覽)的執行與工具鏈，透過 dnx 啟動應用、dnu restore 還原相依套件。文章所用映像 microsoft/aspnet:1.0.0-beta8-coreclr 內含 DNX 工具與 CoreCLR，支援執行 Console 與 ASP.NET 5(beta) 應用。雖然 DNX 後續已被 .NET CLI(dotnet) 取代，但理解 DNX 架構有助於看懂舊版映像與專案的行為與輸出結構。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q5, C-Q8

A-Q4: 為什麼在 NAS 上用 Docker 跑 .NET Core？
- A簡: 免自行架設 Linux 與工具鏈，快速取得可重複、輕量、隔離的執行環境。
- A詳: 在 NAS 上使用 Docker 可避開從零安裝 Linux、設定相依與權限等繁雜步驟。透過 Synology 的 Docker 介面，幾步驟就能拉取映像、掛載目錄並在容器內執行 .NET Core 程式。這對驗證想法、教學展示、內網自動化或小型工具非常合適；容器具備一致性與可移植性，使開發機與運行環境差異縮小，降低「在我機器可行」的風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q5, B-Q15

A-Q5: Docker 映像與容器的差異是什麼？
- A簡: 映像是只讀模板；容器是映像的執行實例，具可寫層與生命週期。
- A詳: 映像(Image)是打包了檔案系統與中介軟體的只讀模板，例如 microsoft/aspnet:1.0.0-beta8-coreclr。容器(Container)是基於映像創建的執行實體，啟動後有自己的可寫層、資源限制與進程。DSM 的「Launch」即對應 docker run，會以選定映像創建並啟動容器。理解兩者的差異，才能正確管理版本、更新、資料持久化與部署策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, B-Q16, C-Q5

A-Q6: 什麼是 microsoft/aspnet:1.0.0-beta8-coreclr 映像？
- A簡: 微軟提供的 ASP.NET 5 與 CoreCLR 預覽映像，內含 DNX 與執行時環境。
- A詳: 該映像是早期 ASP.NET 5/.NET Core 開發的基底，包含 CoreCLR、DNX 工具(dnx/dnu)與必要依賴，體積約 350MB。文章以它作為執行 .NET Core Console App 的容器基底，省去手動安裝框架。雖屬舊版標籤，但概念示範了利用官方映像快速建立跨平台執行環境的做法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q4, D-Q10

A-Q7: 為何要在 VS 勾選「Produce outputs on build」？
- A簡: 產生完整可部署輸出，方便將檔案複製到 NAS 供容器使用。
- A詳: 預設開發流程可能只於本機執行，缺少整合輸出的發佈檔。勾選「Produce outputs on build」會在 artifacts/bin 生成可部署輸出(含依賴)，便於離線複製到 NAS 的掛載目錄。這能避免容器內找不到執行目標或相依項，提升部署成功率與可重複性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q6, D-Q5

A-Q8: artifacts 目錄有什麼作用？
- A簡: 儲存編譯後的標準輸出結構，便於發佈、複製與容器掛載。
- A詳: VS 2015 在勾選產出後，會將組件、相依與目標框架分層放在 solution/artifacts/bin 下。這種標準化的輸出結構，讓部署動作更可預測，容器側只需掛載該資料夾即可找到目標 DLL 與相依套件。對版本控管、CI/CD 與多環境重複部署而言，artifacts 是重要的產物目錄。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q7, D-Q5

A-Q9: 為什麼要做資料夾掛載（/docker/netcore → /home）？
- A簡: 讓容器可直接存取 NAS 上的程式與資料，簡化檔案傳遞。
- A詳: 透過 DSM 的 Advanced Settings 進行 volume 掛載，可把 NAS 的 /docker/netcore 綁定到容器的 /home。如此無需在容器內額外下載或複製程式，更新檔案只要在 NAS 側同步即可。取消唯讀(ReadOnly)可允許容器內寫入暫存或還原套件，有助於 dnu restore 等步驟順利進行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q13, C-Q6

A-Q10: Synology Docker「Registry」是什麼？
- A簡: 內建的映像搜尋與拉取介面，對應至遠端 Docker Registry。
- A詳: DSM 的 Registry 面板提供搜尋關鍵字、選擇標籤(tag)並拉取映像的功能，對應 CLI 的 docker search/pull。使用者可輸入 microsoft/aspnet 並挑選 1.0.0-beta8-coreclr 標籤，DSM 會顯示下載進度與完成通知。這降低了入門門檻，讓無 CLI 經驗者也能順利獲取所需映像。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q4, D-Q1

A-Q11: DSM 的「Launch」與 docker run 有何關係？
- A簡: Launch 精靈將圖形設定轉為 docker run 參數，建立並啟動容器。
- A詳: 使用者在 Launch 精靈中填入容器名稱、資源限制、卷掛載等設定，DSM 會生成等效的 docker run 命令並執行。這將容器建立(create)與啟動(start)合併成一鍵操作，簡化部署流程。理解其對應有助於日後改用 CLI 自動化或故障排除。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q5, C-Q10

A-Q12: 為什麼要執行 dnu restore？
- A簡: 還原專案相依的 NuGet 套件，確保執行時可找到所有依賴。
- A詳: dnu restore 會解析 project.json 中的相依套件與版本範圍，從 NuGet 原始碼庫下載尚未存在的套件到本地快取。首次換機或換容器執行時通常需要這一步，以解決缺少依賴導致的啟動失敗。容器內網路需可訪問 NuGet，或事先在掛載目錄放入已還原的套件。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q8, D-Q3

A-Q13: dnx 如何啟動 .NET Core Console？
- A簡: dnx 載入指定框架環境與相依，執行目標 DLL 的 Main 進入點。
- A詳: dnx 會根據目標框架(dnxcore50)與 runtime 設定，解析載入路徑與依賴，建立 CLR 環境後呼叫程式入口點。對 Console App 而言，dnx HelloCoreCLR.dll 可直接啟動主程式並輸出到容器的標準輸出，DSM logs/terminal 即可看到結果。這流程仰賴事前還原完成與正確的路徑對應。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q9, D-Q4

A-Q14: 為何容器記憶體使用量看起來很省？
- A簡: 容器共用主機核心與映像層，啟動僅增加少量程序與快取。
- A詳: Docker 容器不是完整 VM，啟動時只建立進程與必要檔系統層，重用大量映像層與主機資源。文章觀察到執行 .NET Core Console 的容器僅約 6MB 記憶體，顯示輕量化優勢。但實際使用會因應用大小、JIT/快取、還原套件與 GC 狀態而變動，需以 cgroups/DSM 監控作準。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q7

A-Q15: 哪些 Synology 機種支援 Docker？
- A簡: 多為採用 Intel 架構的型號，官方頁面列出具備 Docker 支援清單。
- A詳: Synology 僅部分機種支援 Docker 套件，主要是較高階、採 Intel CPU 的系列。文章附上官方清單連結與歷年型號範例(如 DS1515+、RS2416+ 等)。採購前應先核對支援性，以免因處理器架構(如 ARM) 或機型限制而無法安裝 Docker。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q9, B-Q14

A-Q16: NAS 上 Docker 與在 Linux 主機上 Docker 有何差異？
- A簡: 功能相近，但 NAS 提供圖形化管理與整合，降低安裝維運成本。
- A詳: 核心 Docker 功能一致；差異在於操作介面與維運責任。NAS 以 DSM 圖形化包裝映像拉取、容器管理、終端機存取與資源監控，免去自行配置 OS、儲存與安全更新。Linux 主機則具最高自由度與效能微調空間，適合進階部署與自動化場景。依需求選擇即可。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q10

A-Q17: 什麼是「Console Application (Package)」專案類型？
- A簡: VS 2015 中支援 DNX/CoreCLR 的主控台專案範本，輸出可被 dnx 執行。
- A詳: 在 VS 2015 的 Visual C#/Web 節點下可找到 Console Application (Package) 範本，屬 DNX/ASP.NET 5 時期的專案系統。其 project.json 描述相依與目標框架(dnxcore50)，配合 dnx/dnu 工具鏈執行與還原。此專案產出的 artifacts 結構便於容器部署，示範跨平台 console 的最小可行實作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q6

A-Q18: 為何文章建議「買現成 NAS 比較輕鬆」？
- A簡: 可快速取得可用 Docker 環境，避免從零安裝 Linux 與相依。
- A詳: 自建 Linux 雖彈性高，但耗時在硬體相容、網路、套件相依與安全更新。NAS 把硬體、儲存、網路與 Docker 套件整合起來，一鍵安裝即可用，特別適合想驗證 .NET Core 容器化而不追求極致效能者。對個人/小團隊，總成本與維運壓力更可控。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q3

A-Q19: Docker 的「資源限制」是什麼？
- A簡: 對容器配置 CPU、記憶體等上限，避免資源爭用影響主機。
- A詳: 透過 DSM 或 docker run 參數，可為容器設定記憶體上限、CPU 配額/權重、I/O 限制等，背後由 cgroups 強制執行。文章示例略過此步，但在多服務共存或保護 NAS 穩定性時很重要。建議根據應用負載與機器規格設置，並觀察實際執行指標再調整。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, D-Q7

A-Q20: 為什麼在容器中切到 /home/dnxcore50？
- A簡: 該目錄包含目標框架 dnxcore50 的輸出與執行入口，便於 dnx 執行。
- A詳: 專案輸出會按目標框架分類，dnxcore50 對應 .NET Core 的 DNX 執行環境。切換到該路徑可直接找到 HelloCoreCLR.dll 與相依。實務上應依實際 artifacts 結構與掛載目錄調整路徑，確保 dnu restore 與 dnx 的工作資料夾一致。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q20, C-Q8, C-Q9

A-Q21: Registry 中選擇標籤(tag)的重要性？
- A簡: 決定映像版本與內含工具，影響相容性與執行成功率。
- A詳: 不同 tag 對應不同版本的 runtime/工具與基底 OS。文章選用 1.0.0-beta8-coreclr，內含 DNX 與 CoreCLR 預覽。若 tag 過舊或無法取得，可改選相容的替代版本。正確的 tag 能避免「找不到命令」或相依不符的錯誤，是部署前的關鍵選項。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q10

A-Q22: 映像大小約 350MB 的意義？
- A簡: 代表已包含必要執行時與工具，換取快速上手與較小部署成本。
- A詳: 350MB 對比自建環境所需的多套件安裝，已屬精簡。此大小多來自基底 OS、CoreCLR、DNX 與工具鏈。雖非最小，但能確保開箱可用、減少相依錯誤。後續如需更輕量，可改用更精簡基底或自行建置多階段映像。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, C-Q4


### Q&A 類別 B: 技術原理類

B-Q1: Synology Docker 套件在 DSM 中如何運作？
- A簡: DSM 以 GUI 驅動 Docker 服務，封裝映像、容器與資源管理。
- A詳: 技術原理說明: DSM 後端運行 Docker 引擎，前端以套件中心與 Docker App 提供 GUI。關鍵步驟: 1) 透過 Registry 檢索與拉取映像；2) Launch 精靈填寫參數；3) DSM 轉為 docker run；4) 監控容器狀態與資源。核心組件: Docker daemon、DSM Docker GUI、映像與容器管理模組、終端機 Web 控制台。此封裝降低 CLI 門檻，仍保留容器核心能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q11, C-Q5

B-Q2: DSM 的 Volume 掛載機制如何運作？
- A簡: 以 bind mount 將 NAS 檔案系統目錄映射至容器內路徑。
- A詳: 技術原理說明: DSM 將使用者選定的 NAS 目錄，以 bind mount 方式映射到容器檔案系統。關鍵步驟: 1) 在 Advanced Settings 指定主機與容器路徑；2) 選擇唯讀/可寫；3) 啟動容器時 Docker 建立掛載。核心組件: Docker volume/bind mount、DSM 設定轉換器。此機制讓容器直接讀寫 NAS 上的程式、資料與快取，簡化部署與更新。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q6, D-Q2

B-Q3: microsoft/aspnet:1.0.0-beta8-coreclr 映像內含什麼？
- A簡: 內含 CoreCLR、DNX 工具與基底 OS，支援執行 .NET Core/DNX 應用。
- A詳: 技術原理說明: 該映像提供可執行 DNX 應用的完整環境。關鍵步驟或流程: 1) 拉取映像層；2) 以該映像建立容器；3) 於容器中呼叫 dnu/dnx。核心組件介紹: CoreCLR 執行時、DNX/dnu 工具、基底 Linux 映像、NuGet 原始端點設定。這讓使用者免去手動安裝框架與工具。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q21, D-Q10

B-Q4: dnu restore 背後機制是什麼？
- A簡: 根據 project.json 解析相依，從 NuGet 下載套件到本地快取。
- A詳: 技術原理說明: dnu 解析 project.json 的 dependencies 與 frameworks，計算版本並查詢 NuGet 源。關鍵步驟: 1) 讀取 project.json；2) 解析語意版本；3) 從源取得 nupkg；4) 解壓至本地快取；5) 更新 lock 檔。核心組件: NuGet 客戶端、語意化版本解析、快取/本地資源。此步驟確保運行時可解析所有參考。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q8, D-Q3

B-Q5: dnx 執行流程與元件組成？
- A簡: dnx 建立 CoreCLR，載入相依組件，呼叫應用入口點執行。
- A詳: 技術原理說明: dnx 作為 host，配置 CLR 與 AssemblyLoader，解析相依。關鍵步驟: 1) 讀取目標框架/路徑；2) 初始化 CoreCLR；3) 根據相依圖載入組件；4) 執行 Main。核心組件: CoreCLR、dnx host、Assembly Loader、配置與 probing path。此機制讓 Console 與 Web 應用得以在容器中一致啟動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q9, D-Q4

B-Q6: VS 2015 artifacts/bin 輸出結構如何設計？
- A簡: 依組態與目標框架分層，包含 DLL、相依與執行用檔案。
- A詳: 技術原理說明: 專案系統輸出包含多框架資料夾(dnxcore50 等)。關鍵步驟: 1) Build 產生中繼；2) Copy 相依至對應框架資料夾；3) 生成 artifacts/bin 層級。核心組件: 專案系統、MSBuild/命令列工具、相依解析。此結構利於部署至容器，讓 dnx 可精確找到對應目標框架的輸出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, C-Q2

B-Q7: DSM 的終端機功能與容器 TTY 的關係？
- A簡: DSM 透過 Web 終端連線到容器的交互式 shell/TTY。
- A詳: 技術原理說明: DSM 呼叫 Docker API 開啟 exec -it，將 TTY 對應至瀏覽器。關鍵步驟: 1) 建立 exec session；2) 附加輸入輸出；3) 在容器內啟動 shell。核心組件: Docker exec、TTY、WebSocket 橋接。此機制讓使用者可直接在瀏覽器操作容器，執行 dnu/ dnX 等命令。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, C-Q9, D-Q8

B-Q8: 容器記憶體使用量是如何計算與限制的？
- A簡: 借助 cgroups 追蹤與限制，計入程序與快取，不含共享核心。
- A詳: 技術原理說明: Docker 使用 Linux cgroups 計數/限制記憶體。關鍵步驟: 1) 為容器建立 cgroup；2) 追蹤 RSS、cache、swap；3) 可設定上限與 OOM 行為。核心組件: cgroups、Docker runtime、DSM 監控。文章觀察的 6MB 為一時點讀數，實際依負載、GC 與套件還原而變化。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, A-Q19, D-Q7

B-Q9: 拉取映像與標籤解析的流程？
- A簡: 向 Registry 解析標籤指向的 digest，拉取對應映像層。
- A詳: 技術原理說明: docker pull 解析倉庫與 tag，獲得 manifest 與各層 digest。關鍵步驟: 1) 認證/匿名訪問；2) 取得 manifest；3) 分層拉取與快取；4) 驗證完整性。核心組件: Docker client/daemon、Registry API、內容可尋址儲存。DSM 的 Registry 介面封裝上述動作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q21, D-Q1

B-Q10: DSM Launch 如何轉為 docker run？
- A簡: 將 GUI 設定序列化為參數，呼叫 Docker API 建立與啟動容器。
- A詳: 技術原理說明: DSM 蒐集使用者輸入(名稱、掛載、限制等)轉為 HostConfig。關鍵步驟: 1) 組合 HostConfig/ContainerConfig；2) Docker create；3) Docker start。核心組件: Docker Engine API、DSM 轉換層。這確保 GUI 與 CLI 行為一致，便於後續改用腳本自動化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q5, C-Q10

B-Q11: 資源限制在底層如何生效？
- A簡: 透過 cgroups 設定記憶體、CPU 配額/權重，I/O 限速等。
- A詳: 技術原理說明: Docker 將限制寫入對應 cgroup 控制檔。關鍵步驟: 1) 設定 memory.limit、cpu.cfs_quota；2) 執行容器進程附屬至 cgroup；3) 核心執行限制。核心組件: cgroups、Docker HostConfig、內核排程器。設定合理配額可避免容器互搶資源，提升 NAS 穩定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q19, D-Q7

B-Q12: 為什麼要取消 ReadOnly 掛載選項？
- A簡: 允許容器在掛載目錄寫入暫存/套件，利於還原與輸出。
- A詳: 技術原理說明: ReadOnly 限制寫入會阻擋 dnu restore 等動作。關鍵步驟: 1) 在 Advanced Settings 取消唯讀；2) 確認 UID/權限足夠；3) 執行還原與運行。核心組件: Bind mount 權限、Linux 檔案權限/擁有者。允許寫入也利於將執行產生的檔案保留在 NAS 上。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, D-Q2, D-Q3

B-Q13: NAS 檔案系統與容器檔案視圖怎麼整合？
- A簡: 透過 bind mount 將主機目錄併入容器層，與映像層疊加呈現。
- A詳: 技術原理說明: 容器檔案系統由映像層 + 可寫層 + 掛載點組成。關鍵步驟: 1) 啟動容器建可寫層；2) 建立 bind mount；3) 檔案解析按優先順序呈現。核心組件: OverlayFS/aufs、bind mount、VFS。這讓容器既能重用映像內容，又能直接讀寫 NAS 上的專案輸出。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q2, A-Q9

B-Q14: 不同 CPU 架構對映像相容性的影響？
- A簡: x86_64 映像無法在 ARM 主機原生執行，需相符架構與支援。
- A詳: 技術原理說明: 映像包含針對特定架構編譯的二進位與庫。關鍵步驟: 1) 主機架構檢查；2) 拉取相容映像；3) 如需跨架構，需仰賴模擬/轉譯。核心組件: CPU ISA、Docker 平台支援、QEMU(如用模擬)。Synology 多數支援 Docker 的機型為 Intel 架構，確保映像可直接執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q9

B-Q15: 從開發到部署的端到端流程如何設計？
- A簡: 本機建置輸出 → 複製至 NAS 掛載 → 容器還原相依 → dnx 執行。
- A詳: 技術原理說明: 將建置產物與執行環境解耦。關鍵步驟: 1) VS 產生 artifacts；2) 複製到 /docker/netcore；3) DSM 建容器掛載 /home；4) 容器內 dnu restore；5) dnx 執行 DLL。核心組件: VS 專案系統、NAS 檔案共享、Docker Volume、DNX。此流程確保可重複、快速且易於故障排除。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q6, C-Q9

B-Q16: 映像/容器生命週期管理為何重要？
- A簡: 規劃拉取、建立、啟動、更新與清理，避免資源浪費與版本混亂。
- A詳: 技術原理說明: 容器是短生命體，映像則可重用。關鍵步驟: 1) 拉取/標籤管理；2) 建立與命名規則；3) 觀察執行；4) 停止與清理；5) 定期更新。核心組件: docker images/ps/rm/prune、DSM Docker 管理。良好生命週期管理提升穩定與安全，避免磁碟被舊層佔滿。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q5, D-Q1

B-Q17: .NET Core 與 .NET Framework 的執行時差異？
- A簡: .NET Core 跨平台、模組化；.NET Framework 依賴 Windows。
- A詳: 技術原理說明: CoreCLR 可在 Linux/容器運行，採包式相依；Framework 綁定 Windows 與 GAC。關鍵步驟: 1) Core 使用 NuGet 套件；2) Framework 需安裝完整 .NET。核心組件: CoreCLR、BCL 子集、NuGet、DNX/CLI。容器場景偏好 .NET Core，部署更輕量與可攜。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, C-Q9

B-Q18: 映像層疊與容量節省如何達成？
- A簡: 多映像共享相同層，僅新增差異層，減少重複儲存。
- A詳: 技術原理說明: Docker 採用分層檔案系統，每層唯讀。關鍵步驟: 1) 基底 OS 層；2) Runtime 層；3) 應用層；4) 共享未變更層。核心組件: OverlayFS/aufs、內容可尋址儲存。因共享機制，拉取多個相近映像不會倍增容量，350MB 也包含可重用部分。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, B-Q13

B-Q19: DSM 映像下載完成的通知如何來的？
- A簡: DSM 監聽 Docker pull 完成事件，顯示系統通知提示。
- A詳: 技術原理說明: DSM 與 Docker daemon 溝通，接收 pull 進度。關鍵步驟: 1) 啟動下載；2) 收集進度/完成狀態；3) 發出通知。核心組件: Docker 事件 API、DSM 通知中心。此機制讓使用者可在背景下載時處理其他事，完成後立即進入部署。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, C-Q4

B-Q20: dnxcore50 目標框架資料夾的作用？
- A簡: 對應 .NET Core 的 DNX 目標，存放該框架的輸出與相依。
- A詳: 技術原理說明: 多目標輸出按框架分目錄。關鍵步驟: 1) 編譯產出不同目標；2) 容器選用 dnxcore50；3) dnx 於該資料夾探測相依。核心組件: 目標框架定義(TFM)、組件解析。正確選定資料夾能避免版本衝突與缺件。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q9

B-Q21: 應用輸出與 runtime 版本如何匹配？
- A簡: 目標框架、工具鏈與映像內 runtime 需對齊，確保相容執行。
- A詳: 技術原理說明: 輸出 TFM、DNX 版本與映像內工具需一致。關鍵步驟: 1) 檢查 project.json frameworks；2) 選擇對應映像；3) 若不符，調整目標或換映像。核心組件: DNX 版本、CoreCLR、NuGet 相依。版本對齊可避免執行階段找不到 API 或工具。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q3, A-Q21, D-Q5

B-Q22: 容器 logs 與 .NET Console 輸出的對應？
- A簡: 應用標準輸出/錯誤流會被容器捕捉，DSM/CLI 均可檢視。
- A詳: 技術原理說明: Docker 將 stdout/stderr 收集為容器 logs。關鍵步驟: 1) 應用 Console.WriteLine；2) 日誌驅動收集；3) DSM 顯示或 docker logs 查閱。核心組件: 日誌驅動(json-file 等)、DSM 介面。這使除錯與監控更便利，無需額外記錄器亦可看到輸出。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q8

B-Q23: 容器網路在此案例如何處理？
- A簡: Console App 無對外服務，使用預設橋接網路即可。
- A詳: 技術原理說明: Docker 預設建立 bridge 網路，容器可對外連線。關鍵步驟: 1) 容器取得虛擬 IP；2) 對外訪問 NuGet；3) 無需對外映射埠。核心組件: docker0 橋接、NAT、DNS 解析。若應用需對外服務，則再行設定埠映射；此案例僅需下載套件與輸出文字。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q3

B-Q24: 在 NAS 上的安全性考量有哪些？
- A簡: 控制權限、更新映像、限制資源與最小化暴露面，防止濫用。
- A詳: 技術原理說明: 將原則落實於權限與隔離。關鍵步驟: 1) 最小權限掛載；2) 維持映像更新；3) 設定資源限制；4) 僅開必要埠；5) 使用獨立帳號存取共享。核心組件: Docker 安全最佳實務、DSM 存取控制與更新機制。雖然本案例不對外，但良好習慣可避免潛在風險。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q19, D-Q1


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 VS 2015 建立 Core CLR「Hello World」專案？
- A簡: 選用 Console Application (Package)，設定 DNX Core 5.0，編寫簡單輸出。
- A詳: 具體實作步驟: 1) VS 2015 新增專案→Visual C#/Web→Console Application (Package)；2) 專案名稱 HelloCoreCLR；3) 於 Program.cs 加入 Console.WriteLine("Hello World"); 4) 於工具列選 DNX Core 5.0。關鍵程式碼片段: Console.WriteLine("Hello World"); 注意事項與最佳實踐: 使用最新相容的工具集；確認目標框架為 dnxcore50；後續勾選「Produce outputs on build」以便部署。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q17, C-Q2

C-Q2: 如何設定「Produce outputs on build」並找到產出？
- A簡: 在專案屬性勾選產出，Build 後於 solution/artifacts/bin 查看。
- A詳: 具體實作步驟: 1) 右鍵專案→屬性→勾選 Produce outputs on build；2) 儲存後執行 Build；3) 到 solution/artifacts/bin 確認輸出。關鍵設定: 勾選產出選項。注意事項與最佳實踐: 確保組態(Debug/Release)一致；檢查輸出包含 dnxcore50 目錄；將此資料夾備份或同步至 NAS 以利部署。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q6, C-Q7

C-Q3: 如何在 Synology 安裝 Docker 套件？
- A簡: 於套件中心搜尋 Docker，安裝官方套件並啟動 Docker 應用。
- A詳: 具體實作步驟: 1) 登入 DSM→套件中心；2) 搜尋「Docker」；3) 點擊安裝；4) 完成後從主選單開啟 Docker。關鍵設定: 確認 NAS 機型支援 Docker。注意事項與最佳實踐: 若找不到套件，核對機型清單；更新 DSM 至支援版本；保留充足儲存空間以容納映像層。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q15, D-Q9

C-Q4: 如何在 Registry 下載 microsoft/aspnet:1.0.0-beta8-coreclr？
- A簡: 開啟 Docker→Registry，搜尋 microsoft/aspnet，選擇對應標籤拉取。
- A詳: 具體實作步驟: 1) Docker→Registry；2) 搜尋 microsoft/aspnet；3) 選擇 tag: 1.0.0-beta8-coreclr；4) 點擊下載，待通知完成。關鍵設定: 正確選取標籤(tag)。注意事項與最佳實踐: 網路需暢通；若標籤過時，選擇相容替代版；留意映像大小(約350MB) 與磁碟空間。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q21, D-Q1

C-Q5: 如何用 DSM Launch 建立名為 NetCoreCLR 的容器？
- A簡: 在映像頁選取映像→Launch→命名 NetCoreCLR→完成精靈設定。
- A詳: 具體實作步驟: 1) Docker→映像→選取 microsoft/aspnet:...→Launch；2) Step1 填 Container Name: NetCoreCLR；3) Step2 資源限制可先跳過；4) 進入 Advanced Settings 設定掛載。關鍵設定: 容器名稱、資源限制、掛載。注意事項與最佳實踐: 命名有辨識性；後續可在需要時補上資源上限以保護 NAS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q10, C-Q6

C-Q6: 如何在 Advanced Settings 掛載 /docker/netcore 到 /home？
- A簡: 在 Volume 加入資料夾，主機路徑 /docker/netcore，容器路徑 /home。
- A詳: 具體實作步驟: 1) Launch 精靈→Advanced Settings→Volume；2) Add Folder 選擇 /docker/netcore；3) Mount path 輸入 /home；4) 取消 ReadOnly。關鍵設定: bind mount 路徑與權限。注意事項與最佳實踐: 確保 /docker/netcore 已存在；權限允許 Docker 讀寫；保持清晰的目錄結構便於維護。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q2, B-Q12

C-Q7: 如何將編譯產出複製到 NAS 指定目錄？
- A簡: 將 artifacts/bin 下的輸出複製到 NAS 的 /docker/netcore 目錄。
- A詳: 具體實作步驟: 1) 在開發機找到 solution/artifacts/bin；2) 複製 dnxcore50 相關輸出；3) 經由 SMB/AFP/SFTP 上傳至 NAS 的 /docker/netcore。關鍵設定: 保持目錄結構完整。注意事項與最佳實踐: 檢查檔案大小與完整性；避免覆寫不相容版本；可用版本號分資料夾以便回溯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2, D-Q5

C-Q8: 如何在 DSM 開啟容器終端機並執行 dnu restore？
- A簡: Docker→容器→Details→Terminal→切到 /home/dnxcore50 執行 dnu restore。
- A詳: 具體實作步驟: 1) 啟動容器；2) 選取容器→Details→Terminal→新增終端；3) cd /home/dnxcore50；4) 執行 dnu restore。關鍵命令: cd /home/dnxcore50 && dnu restore。注意事項與最佳實踐: 確認網路可連 NuGet；如為唯讀掛載將導致失敗；必要時預先在開發機還原並隨產物帶入。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q7, D-Q3

C-Q9: 如何在容器中以 dnx 執行 HelloCoreCLR.dll？
- A簡: 進入輸出目錄，使用 dnx HelloCoreCLR.dll 啟動主控台應用。
- A詳: 具體實作步驟: 1) Terminal 中 cd 至 /home/dnxcore50；2) 確認 DLL 存在；3) 執行 dnx HelloCoreCLR.dll；4) 觀察輸出「Hello World」。關鍵命令: dnx HelloCoreCLR.dll。注意事項與最佳實踐: 先完成 dnu restore；版本需對齊 dnxcore50；如找不到命令，檢查映像 tag 與 PATH 設定。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q5, D-Q4

C-Q10: 如何用 docker CLI 完成相同步驟？
- A簡: docker pull → docker run -v /docker/netcore:/home → docker exec 進容器執行。
- A詳: 具體實作步驟: 1) ssh 到 NAS；2) docker pull microsoft/aspnet:1.0.0-beta8-coreclr；3) docker run --name NetCoreCLR -d -v /docker/netcore:/home microsoft/aspnet:1.0.0-beta8-coreclr tail -f /dev/null；4) docker exec -it NetCoreCLR bash；5) cd /home/dnxcore50 && dnu restore && dnx HelloCoreCLR.dll。關鍵指令: run、exec、-v 掛載。注意事項與最佳實踐: 使用 -d 與保活命令；妥善命名；權限與網路需可用。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, B-Q10, C-Q8


### Q&A 類別 D: 問題解決類（10題）

D-Q1: Registry 找不到或拉取 microsoft/aspnet 失敗怎麼辦？
- A簡: 檢查網路/權限與標籤正確性，改用 CLI 或替代映像重試。
- A詳: 問題症狀描述: Registry 搜尋不到、拉取卡住或報錯。可能原因分析: 標籤過時、網路防火牆、Registry 變動或未登入。解決步驟: 1) 確認關鍵字與 tag；2) 測試網路連線；3) 嘗試 docker pull CLI；4) 改用相容 tag；5) 稍後重試。預防措施: 保持 DSM 與 Docker 更新；記錄可用映像版本；為 NAS 設置可用 DNS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q9, A-Q21

D-Q2: 容器內看不到 /home 檔案或顯示唯讀？
- A簡: 檢查掛載路徑、唯讀選項與 NAS 目錄權限是否正確。
- A詳: 問題症狀描述: /home 空白或寫入 Permission denied。可能原因分析: 未正確掛載、ReadOnly 未取消、NAS 檔案權限不足。解決步驟: 1) 檢查 Advanced Settings/Volume 設定；2) 取消 ReadOnly；3) 確認 /docker/netcore 存在與權限；4) 重建或重啟容器。預防措施: 建立前先準備好目錄；使用一致路徑與命名規則。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q2, B-Q12

D-Q3: dnu restore 失敗如何處理？
- A簡: 檢查網路與 NuGet 來源，改為可寫掛載或離線帶入套件。
- A詳: 問題症狀描述: 還原報錯、逾時或找不到來源。可能原因分析: 無網路、來源被擋、唯讀掛載、版本不符。解決步驟: 1) 測試 ping/nameserver；2) 確認掛載可寫；3) 指定替代 NuGet 源；4) 在開發機先還原後複製快取。預防措施: 容器鏡像網路；設定企業鏡像源；固定相依版本避免飄移。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q4, C-Q8

D-Q4: 出現「dnx: command not found」該怎麼辦？
- A簡: 確認映像內含 DNX、環境變數與 PATH，或改用相容標籤。
- A詳: 問題症狀描述: 終端機執行 dnx 無此命令。可能原因分析: 映像不含 DNX、PATH 未載入、使用非預期 tag。解決步驟: 1) 檢查映像版本；2) 嘗試 /opt/dnx 路徑；3) source 對應 profile；4) 改用含 DNX 的映像。預防措施: 事先確認 tag；於容器入口腳本設定環境變數；記錄可用映像清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q5, A-Q21

D-Q5: HelloCoreCLR.dll 找不到或版本不符如何解決？
- A簡: 檢查 artifacts 路徑、目標框架與複製完整性，對齊 dnxcore50。
- A詳: 問題症狀描述: 容器內找不到 DLL，或執行報 API 缺失。可能原因分析: 未勾選產出、複製不完整、框架不符、相依缺件。解決步驟: 1) 重建並確認 artifacts/bin/dnxcore50；2) 重新複製；3) dnu restore；4) 確認目標框架與映像相容。預防措施: 建立發佈腳本；為不同版本分資料夾；部署前做檔案校驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q6, B-Q21

D-Q6: Console 中文輸出亂碼如何處理？
- A簡: 設定 Console 編碼或使用 UTF-8，確保終端機與字元集一致。
- A詳: 問題症狀描述: 終端機顯示中文為亂碼/問號。可能原因分析: 容器環境區域設定、終端機編碼與應用輸出不一致。解決步驟: 1) 設定環境變數 LANG=C.UTF-8；2) 在程式中 Console.OutputEncoding=UTF8；3) 確認 DSM 終端支援 UTF-8。預防措施: 一律使用 UTF-8；在映像或啟動腳本中預設語系設定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q22

D-Q7: 容器記憶體使用異常升高怎麼診斷？
- A簡: 查看資源監控、設定記憶體上限、檢查 GC 與相依快取。
- A詳: 問題症狀描述: 記憶體飆高、NAS 變慢。可能原因分析: 應用記憶體外洩、套件還原快取、無限制分配。解決步驟: 1) DSM 監控容器資源；2) 設定記憶體上限；3) 觀察 GC 與釋放；4) 清理快取；5) 使用更輕量映像。預防措施: 合理資源限制；壓力測試；定期更新映像與套件。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, A-Q19, B-Q11

D-Q8: DSM 無法開啟容器終端機怎麼辦？
- A簡: 檢查容器狀態與權限，改用 docker exec -it 直接連線。
- A詳: 問題症狀描述: 點擊 Terminal 無回應或錯誤提示。可能原因分析: 容器未啟動、瀏覽器限制、DSM 權限不足。解決步驟: 1) 確認容器已運行；2) 更換瀏覽器；3) 用 SSH 執行 docker exec -it 容器 bash；4) 檢查 DSM 用戶權限。預防措施: 保持 DSM 更新；建立管理員帳號操作 Docker。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q10

D-Q9: NAS 型號不支援 Docker 如何因應？
- A簡: 先核對支援清單，必要時更換支援機型或改用其他主機。
- A詳: 問題症狀描述: 套件中心找不到 Docker 或提示不支援。可能原因分析: 機型/CPU 架構不符、DSM 版本過舊。解決步驟: 1) 查官方支援清單；2) 更新 DSM；3) 若仍不支援，改用支援 Docker 的 NAS/主機；4) 以開發機或迷你主機承擔容器。預防措施: 採購前確認規格與清單，優先選 Intel 架構機種。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q14, C-Q3

D-Q10: 遇到映像標籤過時或不存在該怎麼辦？
- A簡: 改選相容新標籤，或以可用映像重新對齊專案目標。
- A詳: 問題症狀描述: 指定 tag 404/拉取失敗。可能原因分析: 映像下架、 Registry 重組、版本淘汰。解決步驟: 1) 查詢可用 tag；2) 選擇含 DNX/CoreCLR 相容版；3) 如需，調整專案目標框架；4) 測試 dnu/dnx 可用性。預防措施: 維護映像白名單；定期驗證環境；在教學/生產分別鎖定版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, B-Q3, B-Q21


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Synology NAS 的 Docker 環境？
    - A-Q2: 什麼是 .NET Core CLR Console App？
    - A-Q4: 為什麼在 NAS 上用 Docker 跑 .NET Core？
    - A-Q5: Docker 映像與容器的差異是什麼？
    - A-Q6: 什麼是 microsoft/aspnet:1.0.0-beta8-coreclr 映像？
    - A-Q7: 為何要在 VS 勾選「Produce outputs on build」？
    - A-Q8: artifacts 目錄有什麼作用？
    - A-Q9: 為什麼要做資料夾掛載（/docker/netcore → /home）？
    - A-Q10: Synology Docker「Registry」是什麼？
    - A-Q11: DSM 的「Launch」與 docker run 有何關係？
    - C-Q1: 如何在 VS 2015 建立 Core CLR「Hello World」專案？
    - C-Q2: 如何設定「Produce outputs on build」並找到產出？
    - C-Q3: 如何在 Synology 安裝 Docker 套件？
    - C-Q4: 如何在 Registry 下載 microsoft/aspnet:1.0.0-beta8-coreclr？
    - C-Q5: 如何用 DSM Launch 建立名為 NetCoreCLR 的容器？

- 中級者：建議學習哪 20 題
    - A-Q3: DNX Core 5.0 是什麼？
    - A-Q12: 為什麼要執行 dnu restore？
    - A-Q13: dnx 如何啟動 .NET Core Console？
    - A-Q14: 為何容器記憶體使用量看起來很省？
    - A-Q16: NAS 上 Docker 與在 Linux 主機上 Docker 有何差異？
    - A-Q19: Docker 的「資源限制」是什麼？
    - B-Q1: Synology Docker 套件在 DSM 中如何運作？
    - B-Q2: DSM 的 Volume 掛載機制如何運作？
    - B-Q4: dnu restore 背後機制是什麼？
    - B-Q5: dnx 執行流程與元件組成？
    - B-Q6: VS 2015 artifacts/bin 輸出結構如何設計？
    - B-Q7: DSM 的終端機功能與容器 TTY 的關係？
    - B-Q9: 拉取映像與標籤解析的流程？
    - B-Q10: DSM Launch 如何轉為 docker run？
    - C-Q6: 如何在 Advanced Settings 掛載 /docker/netcore 到 /home？
    - C-Q7: 如何將編譯產出複製到 NAS 指定目錄？
    - C-Q8: 如何在 DSM 開啟容器終端機並執行 dnu restore？
    - C-Q9: 如何在容器中以 dnx 執行 HelloCoreCLR.dll？
    - D-Q1: Registry 找不到或拉取 microsoft/aspnet 失敗怎麼辦？
    - D-Q2: 容器內看不到 /home 檔案或顯示唯讀？

- 高級者：建議關注哪 15 題
    - B-Q8: 容器記憶體使用量是如何計算與限制的？
    - B-Q11: 資源限制在底層如何生效？
    - B-Q13: NAS 檔案系統與容器檔案視圖怎麼整合？
    - B-Q14: 不同 CPU 架構對映像相容性的影響？
    - B-Q15: 從開發到部署的端到端流程如何設計？
    - B-Q16: 映像/容器生命週期管理為何重要？
    - B-Q18: 映像層疊與容量節省如何達成？
    - B-Q21: 應用輸出與 runtime 版本如何匹配？
    - B-Q22: 容器 logs 與 .NET Console 輸出的對應？
    - B-Q24: 在 NAS 上的安全性考量有哪些？
    - C-Q10: 如何用 docker CLI 完成相同步驟？
    - D-Q3: dnu restore 失敗如何處理？
    - D-Q4: 出現「dnx: command not found」該怎麼辦？
    - D-Q7: 容器記憶體使用異常升高怎麼診斷？
    - D-Q10: 遇到映像標籤過時或不存在該怎麼辦？