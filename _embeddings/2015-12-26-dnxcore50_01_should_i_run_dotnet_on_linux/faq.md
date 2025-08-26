# .NET Core 跨平台 #1, 我真的需要在 Linux 上跑 .NET 嗎?

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 .NET Core？
- A簡: .NET Core 是跨平台、開源的 .NET 執行平台與程式庫集合，可在 Windows、Linux、macOS 上執行，支援現代化部署（容器）、模組化套件與自包含發行。
- A詳: .NET Core 是 Microsoft 推出的跨平台執行環境與基底類別庫（BCL），以開源方式發展，目標是讓 C#/.NET 生態能在 Windows 以外的系統（Linux、macOS）一致運作。它採用模組化套件（NuGet）與自包含部署模式，適合容器化與雲端場景。相較 .NET Framework，.NET Core 更輕量、可攜、更新節奏快，並以 ASP.NET Core、CLI、Kestrel 等元件組成完整開發體驗與生產架構。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, C-Q1

A-Q2: .NET Core 與 .NET Framework 的差異是什麼？
- A簡: .NET Core 跨平台、開源、模組化；.NET Framework 以 Windows 為主、完整成熟。短期移轉誘因小，長期投資價值高。
- A詳: .NET Framework 僅支援 Windows，生態成熟、元件齊備；.NET Core 則是跨平台、開源、可自包含發行，體積更小、更新更快。就現況（文章語境）而言，.NET Core 尚在起步期，功能與成熟度落後 Framework，但能利用社群力量、容器化與雲端場景整合更佳，並獲官方保證的 Linux 支援，長期可望擴大應用範疇。移轉時需評估 API 相容性與部署目標。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q18, C-Q7

A-Q3: 為什麼要在 Linux 上跑 .NET？
- A簡: 為融入 open source 生態、雲端以 Linux 為主、可與 Nginx/Apache 等方案緊密整合，拓展部署選項與成本彈性。
- A詳: 在 Linux 上運行 .NET 的價值在於：一、可與龐大的開源方案（如 Nginx、Apache）順暢搭配，形成主流部署拓撲；二、雲端市場以 Linux 為大宗，提供更具成本效益與擴展彈性的選擇；三、官方跨平台承諾降低非官方執行環境的風險。此舉也避免 Windows/Linux 生態割裂，讓架構師以系統全貌與維護成本作整體決策，而非被平台相容性所限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q19, C-Q2

A-Q4: .NET Core 開源的核心價值是什麼？
- A簡: 開源讓社群快速發現並修正問題、透明化設計、促進生態整合與採用，縮短修補周期，提高可靠度。
- A詳: 對工程師而言，原始碼可讀性勝過工具文件；開源使得錯誤能被社群快速回報與修正，縮短等待官方釋補的時間，並提升平台可信度。更重要的是，開源促進與其他專案的互操作（如 OWIN、Nginx），形成以雲端與容器為核心的新式部署習慣，讓 .NET 進入 Linux 主導的生態圈，同時提升 Microsoft 在開源社群的影響力，利於長期市佔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q8

A-Q5: 什麼是 BCL（Base Class Library）？
- A簡: BCL 是 .NET 的基底類別庫，提供集合、IO、網路、執行緒等常用 API，.NET Core 與 Framework 均依賴。
- A詳: BCL 為 .NET 應用最底層的共用程式庫，涵蓋字串、集合、檔案/網路 IO、序列化、執行緒與並行等基礎功能。對移轉者而言，現有 C# 程式碼若主要依賴 BCL 常見 API，通常可較順利移植到 .NET Core。差異部分可藉由 NuGet 擴充或替代方案調整。理解 BCL 範疇與差異，是評估相容性與重構成本的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q7

A-Q6: 什麼是 OWIN？為何重要？
- A簡: OWIN 定義 Web 伺服器與 .NET Web 應用的抽象介面，解耦應用與伺服器，促進跨平台與中介軟體生態。
- A詳: OWIN（Open Web Interface for .NET）規範 Web 伺服器（如 Kestrel）與應用之間的溝通契約，使 ASP.NET 類應用獨立於特定伺服器實作。這有利跨平台與部署彈性，也催生豐富的中介軟體（middleware）生態。對 Linux 場景，OWIN 讓 .NET 應用能與 Nginx/Apache 等前端伺服器以反向代理方式順暢協作，降低與 IIS 的耦合，提升移植性與可靠度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q8

A-Q7: ASP.NET 5/ASP.NET Core 的定位與變化？
- A簡: ASP.NET Core（文中稱 ASP.NET 5）重寫為跨平台、模組化、雲端優先的 Web 架構，搭配 Kestrel 與中介軟體。
- A詳: ASP.NET Core 是 ASP.NET 的現代化重構，去除對 System.Web 舊有沉重依賴，採用輕量的 Kestrel 為內建伺服器與中介軟體管線，支援跨平台部署。它與 OWIN 精神一致，能透過 Nginx/Apache 作反向代理，適合容器化、DevOps 與微服務。此改造使 .NET Web 在 Linux 上具可行性與競爭力，並連結開源社群的運作模式與工具鏈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q1

A-Q8: 什麼是反向代理（Reverse Proxy）？為何常搭配 Nginx？
- A簡: 反向代理位於客戶端與後端應用之間，轉發請求、終結 TLS、負載平衡；Nginx 以效能佳、穩定而常用。
- A詳: 反向代理將外部請求轉發至後端應用，並可處理 TLS 終結、壓縮、路由、健康檢查與快取。Nginx 具事件驅動模型、低資源占用與高吞吐，成為 Linux 場景最常見的前端。對 ASP.NET Core/Kestrel 而言，讓 Nginx 面向網路，Kestrel 專注應用邏輯，是最佳實踐；亦能平滑整合多語言、多服務的微服務拓撲。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q2

A-Q9: 為何 open source 生態對 .NET 重要？
- A簡: 可快速獲得修補、相容與整合，直接閱讀原始碼縮短排錯週期，並擴大與主流開源元件的協同效益。
- A詳: 開源社群透過議題追蹤、PR 與評審機制，加速平台演進；工程師可用原始碼直接定位問題與修補，縮短等待時間。更重要的是，.NET 與 Linux 主流元件（Nginx、Docker）無縫整合，讓架構選型由目標服務與維運成本主導，而非被封閉平台限制。長期而言，開源能穩定 .NET 在雲端市場的能見度與採用率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, A-Q4

A-Q10: Mono 與 .NET Core 有何不同？
- A簡: Mono 為社群實作的跨平台 .NET，.NET Core 為官方開源、跨平台的正式方案；後者獲官方支援與保證。
- A詳: Mono 早於 .NET Core 出現，旨在複製 .NET 功能以跨平台運行，覆蓋面廣但與官方框架有差異；.NET Core 則為 Microsoft 正式推出的開源、跨平台平台，具有官方相容與維護承諾。對生產系統與雲端整合而言，.NET Core 與 Azure、容器映像、工具鏈整合更緊密；Mono 在特定場景仍適用，但主流服務建議優先 .NET Core。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q1

A-Q11: 什麼是 Kestrel？與 IIS 的關係？
- A簡: Kestrel 是 ASP.NET Core 內建跨平台 Web 伺服器，常置於 Nginx/IIS 後方，由前端代理面向網路。
- A詳: Kestrel 基於 libuv/.NET 實作的跨平台高效伺服器，隨 ASP.NET Core 提供。生產建議以前端伺服器（Nginx/Linux、IIS/Windows）反向代理至 Kestrel：前端處理 TLS、靜態檔、負載平衡與安全性，Kestrel 專注應用層。此模式將 Windows/Linux 生產架構對齊，便於跨平台部署與一致的監控策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2

A-Q12: 為何雲端以 Linux 為大宗？
- A簡: Linux 具授權成本低、可客製、資源占用低與社群龐大等優勢，雲商供應與生態配套成熟。
- A詳: 雲環境強調彈性、擴展與成本，Linux 在授權、效能、客製化與映像供應上具有明顯優勢，並與容器、微服務及開源工具鏈（Kubernetes、Nginx）緊密結合。雲商因此提供大量 Linux 方案，帶動生態正回饋。對 .NET 而言，擁抱 Linux 可擴大部署面、降低成本，並獲得與主流基礎建設的最佳整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q13, B-Q9

A-Q13: Azure 與 .NET Core on Linux 的關係與策略？
- A簡: Azure 同時支援 Linux/Windows，.NET Core 開源跨平台有助 Azure 留住開發者並提供更好整合服務。
- A詳: 作為雲平台，Azure 必須支援 Linux 工作負載以符合市場現實。透過 .NET Core 開源與跨平台，Microsoft 能提供在 Azure 上更緊密的整合（映像、監控、DevOps），留住 .NET 開發者並吸引跨語言用戶。在 Azure 上以 Linux 佈署 .NET Core，可同享平台服務（負載平衡、儲存、監控）與開源生態優勢，形成雙贏。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q9, C-Q9

A-Q14: 為何 Visual Studio 對 .NET 開發者重要？
- A簡: VS 提供卓越 IDE、偵錯、重構與整合體驗，搭配 C# 語言優勢，提高生產力與可維護性。
- A詳: Visual Studio 長期以來在偵錯、重構、效能剖析、測試與專案管理上領先同儕，與 C# 的語言設計（由 Anders 主導）相輔相成，提供高生產力與工程品質。雖然過去授權成本較高，但隨 .NET Core 與跨平台策略推進，VS Code 等輕量工具崛起，整體開發體驗更具普及性與彈性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, C-Q7

A-Q15: 跨平台常見差異有哪些？為何要注意？
- A簡: 檔案系統大小寫、路徑分隔、換行符、權限與網路堆疊差異，會造成行為不一致與錯誤。
- A詳: Windows 與 Linux 在檔名大小寫敏感性、路徑字元（\ vs /）、換行（CRLF vs LF）、檔案權限與 socket 行為上皆不同。未處理會導致部署後出錯（檔案找不到、無權限、解析失敗）。跨平台開發應採用抽象 API、正規化路徑、CI 上同時測兩環境，並將配置外部化降低耦合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q6, B-Q7

A-Q16: 什麼是記憶體碎裂？與虛擬記憶體有何關聯？
- A簡: 記憶體碎裂為可用空間被切割成小區塊，導致大區塊配置失敗；虛擬位址空間管理方式會影響其表現。
- A詳: 記憶體碎裂指雖然總可用記憶體足夠，但因分散與不連續，無法配置大區塊。虛擬記憶體與位址空間映射策略、架構（x86/x64）與執行平台（Windows/Linux）、GC 行為都會影響碎裂機率與表現。實測常見不同平台與 GC 模式呈現差異，需藉壓力測試驗證實際行為，作容量規劃與調整配置策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q6, D-Q4

A-Q17: 什麼是垃圾回收（GC）？在 .NET 中扮演什麼角色？
- A簡: GC 自動管理記憶體配置與回收，減少記憶體洩漏風險；不同模式影響延遲與碎裂表現。
- A詳: .NET 的 GC 為分代、壓縮與併行等策略的組合，自動回收無用物件。不同模式（Workstation/Server、並行與否）在延遲、吞吐與碎裂方面各有取捨。跨平台時，OS 配合、位址空間與執行時差異會放大這些行為的差別，需借助量測（記憶體壓力、配置模式）與設定（GCServer、容器限制）調優。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q4

A-Q18: 為何短期不必急著遷移到 .NET Core+Linux？
- A簡: 現階段（文章語境）.NET Core 尚未完全成熟，生態與相容性不足，立即轉移誘因有限。
- A詳: 文章撰寫時 .NET Core 尚在 RC，與 .NET Framework 4.6 的生態完整度差距大；許多企業內既有元件、工具鏈、運維流程仍以 Windows/IIS 為主，短期全面切換代價高。更務實的作法是持續評估、挑選合適子系統試點，累積跨平台經驗與工具，為中長期轉型打基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q19

A-Q19: 為何長期來看值得投資 .NET Core+Linux？
- A簡: 可擴大部署選擇、融入主流開源生態、雲端整合更佳，長期提升競爭力與可持續性。
- A詳: 長期趨勢上，雲端與容器驅動的基礎設施以 Linux 為核心；開源讓 .NET 與主流堆疊緊密協作，並透過社群加速修補與改進。官方跨平台保證降低風險，持續投入能累積團隊跨平台實力，未來在架構選型、成本控制與服務韌性上都更具優勢。這是面向下個十年的布局與投資。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4

A-Q20: Docker 在 .NET Core 跨平台中的角色是什麼？
- A簡: Docker 提供一致的執行環境與可攜封裝，便於在 Linux/Windows 間部署 .NET Core，支援微服務與 CI/CD。
- A詳: Docker 以映像封裝應用與相依，確保在不同主機上有一致行為。對 .NET Core 而言，容器化能快速建立 Linux 與 Windows 的可比較環境，利於效能評測與部署自動化。搭配 Nginx 反向代理與 Kestrel，可組裝出穩健的生產拓撲，並運用雲端平台的編排與監控能力，落實現代化交付。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, C-Q5


### Q&A 類別 B: 技術原理類

B-Q1: .NET Core 跨平台如何運作（Runtime/BCL/Host）？
- A簡: 透過跨平台 Runtime、統一 BCL 與可攜部署模型，結合 CLI 與宿主（Kestrel）實現一致行為。
- A詳: 原理說明：.NET Core 提供跨平台 CLR、通用 BCL 與 NuGet 套件，讓同一套程式碼於多 OS 運行。關鍵流程：編譯→還原套件→部署（框架相依或自包含）→在目標 OS 以 dotnet/宿主啟動。核心組件：dotnet CLI、CoreCLR、CoreFX、Kestrel。這種設計將 OS 差異封裝於 Runtime 與原生互操作層，確保 API 行為一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q2, C-Q1

B-Q2: ASP.NET Core 在 Linux 上的架構（Nginx+Kestrel+OWIN）是怎麼設計的？
- A簡: 以前端 Nginx 反代至 Kestrel，應用透過中介軟體管線（OWIN 精神）處理請求，實現安全與高效。
- A詳: 技術原理：Nginx 面向網際網路，負責 TLS、靜態檔與轉發；Kestrel 為應用伺服器；中介軟體形成處理管線。流程：Client→Nginx→Kestrel→Middleware→App→回應。核心組件：Nginx、Kestrel、ASP.NET Core Middleware、Systemd（服務）。此分層提高可維護性與效能，並統一 Linux/Windows 架構語言（IIS 扮演前端時亦同）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q11, C-Q2

B-Q3: Reverse Proxy 的請求流程與關鍵點是什麼？
- A簡: 代理接收請求、終結 TLS、設置轉發標頭，再轉至後端；需保留 Host/IP/Proto 與健康檢查。
- A詳: 原理：反代位於邊界，負責連線管理與協定轉換。流程：Client→Proxy（TLS/路由/節流）→後端（HTTP/Unix Socket）→回應→快取/壓縮→Client。關鍵：proxy_set_header Host/X-Forwarded-*；逾時/重試策略；健康檢查與熔斷。核心：Nginx/Apache、Upstream 池、Kestrel 端點。正確標頭與逾時設定避免 502/504 與位址解析錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2

B-Q4: 記憶體管理與碎裂在不同 OS/架構/GC 下如何演變？
- A簡: 位址空間、配置器與 GC 模式差異會改變碎裂表現；x64、壓縮與伺服器 GC 通常較穩定。
- A詳: 原理：碎裂受虛擬位址空間、配置策略（Large Object Heap/Small Object Heap）、GC 模式影響。流程：配置→存活→回收/壓縮→再配置；若大物件分散且無壓縮，易碎裂。核心：CoreCLR GC、LOH、SOH、OS 記憶體配置器。跨 OS 與 x86/x64 差異會改變最大可配置區塊與回收效率，需以壓力測試驗證假設。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q16, A-Q17, C-Q6, D-Q4

B-Q5: 多執行緒計算效能比較的原理與衡量方式？
- A簡: 以相同負載與演算法，衡量吞吐、延遲與 CPU 利用率；控制變因、觀察 OS 調度差異。
- A詳: 原理：使用等價演算法（如 PI 計算）與固定負載，透過多執行緒/Task 平行化。流程：設定執行緒數→量測執行時間→監控 CPU/記憶體→多平台比對。核心：TPL/Parallel.For、定時器、效能計數器/Perf 工具。需控制 VM 規格、容器限制、JIT/Runtime 版本，才能客觀比較 Linux/Windows 的調度與系統呼叫差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q4, D-Q9

B-Q6: Docker 容器在 Linux/Windows 的隔離與差異機制？
- A簡: Linux 用命名空間/cgroups；Windows 用 Job Objects、伺服器核心容器層；映像與底層不相容。
- A詳: 原理：Linux 以 namespace（pid/net/mnt）與 cgroups 做資源隔離；Windows 以 Host/Hyper-V 隔離模式運作。流程：映像→容器建立→網路/儲存掛載→啟動進程→限制資源。核心：containerd、runc/win 容器執行期、映像基底（Linux vs Windows）。跨 OS 容器不可互換，需對應基底映像與編排設定調整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q3, C-Q5, D-Q5

B-Q7: Windows 與 Linux 檔案系統差異對 .NET 的影響機制？
- A簡: 大小寫敏感、路徑/換行/權限差異影響 IO 與部署；需使用抽象 API 與正規化策略。
- A詳: 原理：NTFS（預設不敏感）vs ext4（敏感），路徑分隔符差異，權限模型不同。流程：跨平台 IO→Path/Env API 正規化→部署時調整權限→測試驗證。核心：System.IO、Path、FilePermission、行尾轉換。若硬編碼路徑或忽視大小寫，將在 Linux 出錯；最佳實踐是使用框架 API 與相容測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q6

B-Q8: 開源社群修 Bug 的流程與效益機制是什麼？
- A簡: 透過 issue、PR、Code Review 與 CI 驗證快速迭代，縮短修補週期並提升品質與透明度。
- A詳: 原理：公開議題追蹤、以 PR 提交修補，經維護者審查與自動化測試驗證。流程：提報→討論/重現→PR→Review/CI→合併→釋出。核心：GitHub、CI/CD、語義化版本。效益：縮短等待官方修補時間、促進知識共享、降低黑箱風險。對平台錯誤（如編碼問題）能快速定位並回饋至主分支。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q9

B-Q9: Azure 如何同時支援 Linux 與 Windows 工作負載？
- A簡: 透過多樣計算資源、映像與服務抽象，讓應用以一致方式被部署、監控與擴展。
- A詳: 原理：Azure 提供 VM/容器/函數等多型態計算，並以負載平衡、儲存、網路、安全作通用層。流程：選擇 OS 與映像→部署→掛載服務→監控與調整。核心：Azure VM、Container Apps/AKS、Monitor、Load Balancer。這使 .NET Core on Linux 與 Windows 皆可用一致的管控面，降低異質環境運維負擔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q13, C-Q9

B-Q10: .NET Core 的套件管理與部署機制（NuGet/自包含）？
- A簡: 以 NuGet 管套件，相依於主機框架或自包含發行；後者攜帶 Runtime，提升可攜性。
- A詳: 原理：專案宣告目標框架與套件，相依還原後編譯。部署可選框架相依（較小）或自包含（攜 runtime）。流程：dotnet restore→build/publish→（framework-dependent/self-contained）→部署與啟動。核心：NuGet、Runtime Identifier（RID）、PublishTrimmed。自包含有利跨平台落地與減少目標機器前置要求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, C-Q1, C-Q7


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Linux 安裝 .NET Core 並執行 ASP.NET Core 範例？
- A簡: 安裝 SDK→dotnet new web→dotnet run→以瀏覽器測試；建議建立 systemd 服務供生產。
- A詳: 
  - 實作步驟: 
    1) 安裝 SDK: sudo apt-get install dotnet-sdk; 
    2) 建案: dotnet new web -o MyApp; 
    3) 執行: dotnet run; 
    4) 瀏覽 http://localhost:5000。 
  - 程式碼: Program.cs 使用 WebApplication.CreateBuilder(); MapGet("/"). 
  - 注意: 生產改用 publish（dotnet publish -c Release），並以 systemd 管理服務與環境變數，開防火牆僅暴露給前端代理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, B-Q2

C-Q2: 如何用 Nginx 設定反向代理到 Kestrel？
- A簡: 將 Nginx server 區段 proxy_pass 至 Kestrel，設 X-Forwarded-* 標頭與逾時；Kestrel 綁本機埠。
- A詳: 
  - 步驟: 安裝 Nginx→建立站台→啟動 Kestrel（:5000）→設定反代→重載。 
  - 設定: 
    server { location / { proxy_pass http://127.0.0.1:5000; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto $scheme; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; proxy_read_timeout 60s; } }
  - 注意: TLS 終結於 Nginx、健康檢查、限制直接對外開放 Kestrel，調整緩衝與逾時避免 502/504。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q11, B-Q2

C-Q3: 如何用 Docker 建立 .NET Core 應用的容器映像？
- A簡: 使用官方基底映像，COPY 發行檔至 /app，設定 ENTRYPOINT；建置與執行容器並映射埠。
- A詳: 
  - 步驟: dotnet publish -c Release -o publish→撰寫 Dockerfile→docker build→docker run -p。 
  - Dockerfile: 
    FROM mcr.microsoft.com/dotnet/aspnet:8.0 
    WORKDIR /app 
    COPY ./publish . 
    ENTRYPOINT ["dotnet","MyApp.dll"]
  - 注意: 依目標 OS 選 Linux/Windows 映像；善用多階段建置，設定健康檢查與唯讀檔系統，記得以非 root 角色執行提升安全。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q6

C-Q4: 如何比較 .NET Core 在 Linux/Windows 的執行效能？
- A簡: 控制變因（相同硬體/VM/容器限制），以相同程式負載量測時間與資源占用，重複多次取中位數。
- A詳: 
  - 步驟: 準備相同規格 VM/容器→部署相同二進位→設定相同環境變數與限制→執行測試程式→收集指標。 
  - 程式碼: 使用 Parallel.For 執行計算（如 PI）與 Stopwatch 記錄時間。 
  - 注意: 關閉除錯符號、固定執行緒數、預熱 JIT、避免 IO 影響；記錄 CPU/記憶體/GC 計數，分析調度與容器限制差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q3

C-Q5: 如何在 Windows Server 2016 上運行 Windows Container 與 .NET？
- A簡: 啟用容器功能→安裝 Docker for Windows Server→拉取 .NET 映像→執行容器並映射埠。
- A詳: 
  - 步驟: Install-WindowsFeature containers; 安裝 Docker；docker pull mcr.microsoft.com/dotnet/aspnet；docker run -d -p 8080:80 映像。 
  - 設定: 使用 --isolation=process 或 hyperv 視需求。 
  - 注意: Windows 容器僅支援 Windows 映像；版本需匹配主機；網路與儲存掛載策略調整，避免與主機政策衝突。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q6

C-Q6: 如何執行記憶體碎裂測試於 .NET Core？
- A簡: 寫配置/釋放模式製造壓力，量測最大可配置區塊與失敗情況；跨 OS/架構/GC 比較。
- A詳: 
  - 步驟: 以不同大小與壽命的物件反覆配置→保留/釋放→嘗試大區塊配置→記錄失敗。 
  - 程式碼: List<byte[]> 保留小塊；嘗試 new byte[large]; 觀察 GC 計數與例外。 
  - 注意: 測 x86/x64、Server/Workstation GC、容器記憶體限額；避免 OOM 影響主機，分批增加壓力並記錄行為差異。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q4

C-Q7: 如何將既有 .NET Framework 程式碼遷移到 .NET Core？
- A簡: 盤點相依→對應 BCL/API 替代→多目標建置→逐步替換與測試→調整部署模式。
- A詳: 
  - 步驟: 用 API 分析器盤點→移除 System.Web 相依→引入跨平台套件→設定 TargetFramework（netstandard/netX）→dotnet publish。 
  - 程式碼: 替換路徑/IO 為 System.IO.Abstractions；改用 HttpClient。 
  - 注意: 外部元件相容性、平台差異（檔案/權限）、CI 同時跑 Win/Linux 測試；必要時採自包含發行降低環境相依。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q10

C-Q8: 如何在 ASP.NET Core 使用 OWIN 兼容中介軟體？
- A簡: 透過中介軟體模式實作請求處理鏈，或使用 OWIN 相容橋接；重點在解耦伺服器與應用。
- A詳: 
  - 步驟: 在 Program.cs 加入 app.Use(...) 自訂中介；必要時引用 OWIN 相容套件。 
  - 程式碼: app.Use(async (ctx,next)=>{ /*前置*/ await next(); /*後置*/ }); 
  - 注意: 中介順序決定行為；避免阻塞；將跨平台差異（如路徑正規化）封裝於中介統一處理，提高可移植性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2

C-Q9: 如何在 Azure Linux VM 佈署 .NET Core + Nginx 服務？
- A簡: 建立 VM→安裝 .NET/Nginx→部署發行檔→systemd 設服務→Nginx 反代→開啟 80/443。
- A詳: 
  - 步驟: 建 VM（Ubuntu）→安裝 dotnet-runtime、nginx→dotnet publish 上傳→systemd 服務：ExecStart=/usr/bin/dotnet /app/MyApp.dll→Nginx proxy_pass→Azure NSG 開通。 
  - 設定: Environment=ASPNETCORE_URLS=http://127.0.0.1:5000。 
  - 注意: 使用 Managed Identity/Key Vault 管密鑰；啟用診斷與自動更新，滾動更新降低中斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q9

C-Q10: 如何選擇 IIS、Nginx、Apache 作為 Web 前端？
- A簡: Windows 生態/IIS；Linux 生態/Nginx 常見；Apache 擴充模組多。依團隊技術棧與運維優勢決策。
- A詳: 
  - 步驟: 盤點 OS、團隊技能、現有監控與自動化→評估 TLS/HTTP/2、反代、負載、模組相容→做 PoC。 
  - 設定: ASP.NET Core 生產建議「前端代理+Kestrel」；IIS（Windows）或 Nginx（Linux）皆可。 
  - 注意: 一致化跨平台拓撲、確保標頭與逾時設定一致；避免一台伺服器同時承載多種 Web 伺服器造成維運複雜。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q3


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 在 Linux 正常、Windows 失敗（或反之）如何診斷？
- A簡: 重現症狀→收集日誌/環境→檢查路徑/大小寫/權限→最小化範例→建立雙平台 CI 驗證。
- A詳: 
  - 症狀: 同程式跨平台行為不一致。 
  - 原因: 路徑/大小寫、權限、行尾、區域設定、編碼、依賴 OS 特性。 
  - 解法: 啟用詳細日誌；用 Path/Environment API 正規化；修正權限與大小寫；建立最小重現並比對。 
  - 預防: 制定跨平台檢查清單、CI 同步測、避免硬編碼與平台特有 API。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q7

D-Q2: Nginx 反向代理出現 502/504 錯誤怎麼辦？
- A簡: 檢查後端存活與埠、逾時與緩衝設定、X-Forwarded-* 標頭；查看 Nginx/error 與應用日誌。
- A詳: 
  - 症狀: 502 Bad Gateway/504 Gateway Timeout。 
  - 原因: 後端未啟動/埠錯、逾時過短、DNS 解析、標頭缺失、資源耗盡。 
  - 解法: 確認 Kestrel 運行與 listen；調整 proxy_read_timeout；設 proxy_set_header；檢查 upstream 健檢。 
  - 預防: 加入健康檢查、熔斷與重試；監控延遲與資源；滾動更新避免全斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2

D-Q3: Kestrel 啟動失敗或埠被占用如何處理？
- A簡: 檢查 ASPNETCORE_URLS、lsof/netstat 確認埠、修改綁定或釋放占用；查看權限與防火牆。
- A詳: 
  - 症狀: 應用啟動錯誤、無法綁定埠。 
  - 原因: 埠被占用、權限不足、URL 綁定錯誤、SELinux/AppArmor 限制。 
  - 解法: 改綁 127.0.0.1:5000；釋放占用進程；以 systemd 設環境變數；放行防火牆。 
  - 預防: 固定使用本機埠由前端代理轉發；在部署腳本中檢查埠狀態，避免直接對外開放 Kestrel。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q2

D-Q4: .NET Core 應用記憶體偏高、疑似碎裂怎麼診斷？
- A簡: 觀察 GC 計數與 LOH、做壓力重現、嘗試不同 GC 模式與 x64，檢視配置模式並減少大物件。
- A詳: 
  - 症狀: 記憶體飆升或配置大區塊失敗。 
  - 原因: LOH 碎裂、大物件生命週期長、容器限額太緊。 
  - 解法: dotnet-counters/trace 分析 GC；減少/分塊大物件；改 x64、Server GC；調整容器記憶體；程式碼排查保留集合。 
  - 預防: 避免頻繁大配置；池化緩衝；壓測驗證各 OS/GC 模式行為。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q4, C-Q6

D-Q5: 容器中 CPU/記憶體受限導致效能差如何排查？
- A簡: 檢查 cgroups 限制、容器參數（--cpus/-m）、觀測 Throttling；調整限額與 GC 模式。
- A詳: 
  - 症狀: 高延遲、CPU 無法跑滿、GC 頻繁。 
  - 原因: cgroups 限制、超賣、GC 未感知限額。 
  - 解法: docker stats/Top 觀察；設定 DOTNET_GCHeapHardLimit；調整 --cpus/--memory；壓測比對前後。 
  - 預防: 以壓測訂定合理限額；資源隔離與併發策略協同設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, C-Q5

D-Q6: 檔案路徑與大小寫差異造成錯誤如何修正？
- A簡: 改用 Path/Env API、正規化路徑、避免硬編碼；統一命名大小寫並在 CI 驗證。
- A詳: 
  - 症狀: 找不到檔案、存取拒絕、路徑解析錯。 
  - 原因: Linux 大小寫敏感、路徑分隔差、權限/行尾不同。 
  - 解法: 使用 Path.Combine/Directory API；正規化大小寫；檔案權限調整（chmod/chown）；轉換行尾。 
  - 預防: 在 Linux/Windows 雙測；建立命名規範；避免把路徑寫死於程式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q7

D-Q7: Docker 容器內部 DNS/網路連線異常的解法？
- A簡: 檢查容器網路模式、DNS 設定、主機防火牆與代理；使用 curl/nslookup 診斷並調整。
- A詳: 
  - 症狀: 容器無法解析/連線外部服務。 
  - 原因: DNS 設定缺失、公司代理、防火牆或 bridge 網路異常。 
  - 解法: docker run --dns、修正 resolv.conf；設定 NO_PROXY；檢查 iptables/Windows 防火牆；改用 host 網路作確認。 
  - 預防: 標準化網路配置；寫入健康檢查；文件化代理/白名單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, C-Q5

D-Q8: 不同 Runtime 版本不相容如何處理？
- A簡: 明確目標框架與 RID，自包含發行或鎖定版本；在 CI 驗證多環境，避免隱性升級。
- A詳: 
  - 症狀: 在新環境啟動失敗或行為改變。 
  - 原因: Runtime/套件版本差異、API 變更。 
  - 解法: global.json 鎖定 SDK；自包含發行攜帶 Runtime；NuGet 鎖版；發佈清單檢視。 
  - 預防: 版本治理流程；多目標測試；升級前先在預備環境驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q1, C-Q7

D-Q9: 多執行緒計算效能不如預期的原因與改善？
- A簡: 受限於 CPU 數、容器限額、同步鎖或 GC；調整平行度、演算法與資源配置。
- A詳: 
  - 症狀: 增加執行緒未改善或變慢。 
  - 原因: 上下文切換、共享資源鎖、NUMA、容器 CPU 限制、GC 壓力。 
  - 解法: 控制平行度（Environment.ProcessorCount）、降低共享、向量化、Pinned 物件減少、調整 GC；壓測驗證。 
  - 預防: 以實測選平行度；避免過度執行緒化；資源與演算法聯動設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q4

D-Q10: SMTP/編碼等平台差異導致字元亂碼如何避免？
- A簡: 統一編碼（UTF-8）、明確指定 Content-Type/Charset，並用跨平台函式庫與測試驗證。
- A詳: 
  - 症狀: 郵件或輸出在不同平台顯示亂碼。 
  - 原因: 預設編碼不同、MIME 標頭缺失、平台 API 行為差。 
  - 解法: 明確設定 UTF-8；檢查 Content-Transfer-Encoding；以相容套件寄發；驗證各客戶端。 
  - 預防: 寫入自動化測試涵蓋編碼；避免依賴平台預設；發現問題即回饋上游（開源專案）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, A-Q15


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 .NET Core？
    - A-Q2: .NET Core 與 .NET Framework 的差異是什麼？
    - A-Q3: 為什麼要在 Linux 上跑 .NET？
    - A-Q4: .NET Core 開源的核心價值是什麼？
    - A-Q5: 什麼是 BCL（Base Class Library）？
    - A-Q8: 什麼是反向代理（Reverse Proxy）？為何常搭配 Nginx？
    - A-Q11: 什麼是 Kestrel？與 IIS 的關係？
    - A-Q12: 為何雲端以 Linux 為大宗？
    - A-Q14: 為何 Visual Studio 對 .NET 開發者重要？
    - A-Q15: 跨平台常見差異有哪些？為何要注意？
    - A-Q18: 為何短期不必急著遷移到 .NET Core+Linux？
    - A-Q19: 為何長期來看值得投資 .NET Core+Linux？
    - C-Q1: 如何在 Linux 安裝 .NET Core 並執行 ASP.NET Core 範例？
    - C-Q2: 如何用 Nginx 設定反向代理到 Kestrel？
    - D-Q3: Kestrel 啟動失敗或埠被占用如何處理？

- 中級者：建議學習哪 20 題
    - B-Q1: .NET Core 跨平台如何運作（Runtime/BCL/Host）？
    - B-Q2: ASP.NET Core 在 Linux 上的架構（Nginx+Kestrel+OWIN）是怎麼設計的？
    - B-Q3: Reverse Proxy 的請求流程與關鍵點是什麼？
    - B-Q7: Windows 與 Linux 檔案系統差異對 .NET 的影響機制？
    - B-Q10: .NET Core 的套件管理與部署機制（NuGet/自包含）？
    - C-Q3: 如何用 Docker 建立 .NET Core 應用的容器映像？
    - C-Q4: 如何比較 .NET Core 在 Linux/Windows 的執行效能？
    - C-Q5: 如何在 Windows Server 2016 上運行 Windows Container 與 .NET？
    - C-Q7: 如何將既有 .NET Framework 程式碼遷移到 .NET Core？
    - C-Q8: 如何在 ASP.NET Core 使用 OWIN 兼容中介軟體？
    - C-Q9: 如何在 Azure Linux VM 佈署 .NET Core + Nginx 服務？
    - C-Q10: 如何選擇 IIS、Nginx、Apache 作為 Web 前端？
    - D-Q1: 在 Linux 正常、Windows 失敗（或反之）如何診斷？
    - D-Q2: Nginx 反向代理出現 502/504 錯誤怎麼辦？
    - D-Q4: .NET Core 應用記憶體偏高、疑似碎裂怎麼診斷？
    - D-Q5: 容器中 CPU/記憶體受限導致效能差如何排查？
    - A-Q6: 什麼是 OWIN？為何重要？
    - A-Q7: ASP.NET 5/ASP.NET Core 的定位與變化？
    - A-Q20: Docker 在 .NET Core 跨平台中的角色是什麼？
    - B-Q9: Azure 如何同時支援 Linux 與 Windows 工作負載？

- 高級者：建議關注哪 15 題
    - B-Q4: 記憶體管理與碎裂在不同 OS/架構/GC 下如何演變？
    - C-Q6: 如何執行記憶體碎裂測試於 .NET Core？
    - D-Q4: .NET Core 應用記憶體偏高、疑似碎裂怎麼診斷？
    - B-Q5: 多執行緒計算效能比較的原理與衡量方式？
    - C-Q4: 如何比較 .NET Core 在 Linux/Windows 的執行效能？
    - D-Q9: 多執行緒計算效能不如預期的原因與改善？
    - B-Q6: Docker 容器在 Linux/Windows 的隔離與差異機制？
    - C-Q3: 如何用 Docker 建立 .NET Core 應用的容器映像？
    - C-Q5: 如何在 Windows Server 2016 上運行 Windows Container 與 .NET？
    - D-Q5: 容器中 CPU/記憶體受限導致效能差如何排查？
    - B-Q3: Reverse Proxy 的請求流程與關鍵點是什麼？
    - C-Q2: 如何用 Nginx 設定反向代理到 Kestrel？
    - D-Q2: Nginx 反向代理出現 502/504 錯誤怎麼辦？
    - B-Q10: .NET Core 的套件管理與部署機制（NuGet/自包含）？
    - D-Q8: 不同 Runtime 版本不相容如何處理？