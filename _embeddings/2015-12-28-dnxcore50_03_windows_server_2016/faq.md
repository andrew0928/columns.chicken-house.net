# .NET Core 跨平台 #3, 記憶體管理大考驗 - Windows Container (2016 TP)

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是「記憶體管理大考驗」測試？
- A簡: 以多平台實測 .NET Core 記憶體配置、碎片化與再分配，建立可比較的「記憶體利用率」指標。
- A詳: 本測試在不同 Windows 平台（2012 R2 Server Core、2016 TP Windows Container）上，就地編譯並執行相同的 .NET Core（DNX）程式，分三階段：先大量配置（Phase 1），再刻意造成碎片化，最後重新配置（Phase 3）。以 Phase3/Phase1 做為「記憶體利用率%」衡量碎片化後可有效取得的連續記憶體比例，對照不同平台下的差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q14, B-Q1

A-Q2: 什麼是 .NET Core（DNX 版）？
- A簡: DNX 是早期 .NET Core 的執行環境，負責載入、編譯與執行應用程式。
- A詳: DNX（.NET Execution Environment）是 .NET Core 早期（pre-1.0）生態的一部分，提供跨平台的執行主機與工具鏈（dnx、dnu、dnvm），允許在 Windows/Linux 上還原套件、即時編譯並執行應用。文中 dnx.exe 即為執行主體，用以觀察不同平台上的記憶體行為與資源使用狀態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q1, C-Q2

A-Q3: 什麼是 Windows Server 2012 R2 Server Core？
- A簡: 一種無 GUI 的精簡安裝選項，減少元件與資源耗用，利於伺服器化部署。
- A詳: Server Core 是 Windows Server 的精簡化安裝模式，移除傳統 GUI，以命令列與 PowerShell 操作為主，具有較小攻擊面、較少更新、較低資源占用。文中將其作為對照組，以避免 GUI 造成額外干擾，讓記憶體測試更純粹地反映執行階段行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, C-Q9

A-Q4: 什麼是 Windows Container？
- A簡: 以宿主相同 Kernel 提供行程、檔案與網路隔離的 Windows 容器技術。
- A詳: Windows Container 在 Windows Server 2016 引入，採用與宿主相同的 NT Kernel，透過命名空間、檔案系統層與網路隔離達成「像 VM 的體驗」，但無額外 Hypervisor 成本。它兼容 Docker 工具鏈與 PowerShell 管理，適合快速部署、資源效率高、啟動迅速的應用情境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q19, B-Q4

A-Q5: 為何 Windows Container 不能使用 Linux 映像？
- A簡: 因為容器共用宿主 Kernel，Windows 與 Linux 系統呼叫與 ABI 不相容。
- A詳: 容器並非完整模擬硬體，而是與宿主共享 Kernel。因此映像必須與宿主作業系統核相容。Linux 映像依賴 Linux Kernel 的系統呼叫與 ABI，無法在 Windows NT Kernel 上執行；相同地，Windows 容器映像也不能在 Linux 宿主上直接運行。這也是文中以 windowsservercore 作為基底映像的原因。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q5, D-Q1

A-Q6: 什麼是 Hyper-V Container？
- A簡: 為了 Kernel 隔離，容器自動包裹在輕量 VM（Hyper-V）中的模式。
- A詳: Hyper-V Container 是 Windows 2016 引入的選項。當需要 Kernel 級隔離時，系統會用預製映像啟動輕量 VM，並在其中啟動容器，達到與 VM 類似的隔離安全。同時保留容器管理體驗與映像生命週期優勢，適合多租戶或高安全需求場景。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q7, B-Q22

A-Q7: Windows Container 與 Hyper-V Container 差異？
- A簡: 前者共用宿主 Kernel、效能近原生；後者隔離於輕量 VM，安全更強。
- A詳: Windows Container 直接共用宿主 Kernel，啟動快、資源開銷小，效能接近原生；Hyper-V Container 以每容器一個輕量 VM 包裹，提供 Kernel 隔離、映像一致性與強安全性，但啟動成本與資源占用較高。選擇取決於安全、合規與租戶隔離需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, A-Q8, D-Q9

A-Q8: Windows Container 與傳統 VM 有何差異？
- A簡: 容器共用宿主 Kernel，啟動快、耗用少；VM 模擬硬體，隔離最強。
- A詳: VM 透過 Hypervisor 提供完整硬體虛擬化，客體 OS 與宿主完全隔離；容器只隔離行程、檔案與網路，與宿主共享 Kernel，因此資源效率高、啟動時間短，部署更敏捷。文中也以 Task Manager 觀察到容器內程序能在宿主上看見，反映其 Kernel 共享特性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q11

A-Q9: 為何要「就地編譯、就地測試」？
- A簡: 排除跨平台二進位差異與載入成本，讓指標更貼近實際環境。
- A詳: 不同平台的編譯器、JIT 與相依套件版本可能帶來性能與記憶體行為差異。就地編譯可避開跨平台 binary 帶來的偏差，且能讓 JIT 與程式資料在該平台最佳化，便於比較 Phase1 與 Phase3 的相對結果，使衡量更一致可比。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q2

A-Q10: 測試中的 Phase 1 與 Phase 3 是什麼？
- A簡: Phase1 大量配置；Phase3 在碎片化後再次嘗試取得可用記憶體。
- A詳: Phase1 是在乾淨狀態下最大化記憶體配置量，量測可獲得的峰值。之後透過特定模式釋放/重配，刻意造成碎片化。Phase3 再次申請記憶體，觀察在碎片化後可實際取得的連續記憶體。兩者比值用於衡量碎片對可用度的影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q14

A-Q11: 為什麼要連續執行兩次，以第二次為準？
- A簡: 避免第一次啟動的還原、JIT、快取等一次性開銷干擾測值。
- A詳: 首次執行常包含套件下載/還原、JIT 預熱、檔案與 OS 快取建立等一次性成本，會影響時間與記憶體曲線。第二次執行後，環境較為穩定，能更準確反映程式執行期的常態行為，提升跨平台比較的一致性與信度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q8

A-Q12: 什麼是記憶體碎片化？
- A簡: 記憶體被拆成多個小片段，難以取得足夠的連續大區塊使用。
- A詳: 由於反覆配置/釋放不同大小的區塊，堆積空間會出現零散間隙，雖總量未耗盡，卻因缺乏足夠大的連續區塊而導致分配失敗或下降。測試透過特定分配/釋放序列放大此現象，量化其對可用記憶體的實質影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q20

A-Q13: 什麼是頁面檔（pagefile）與虛擬記憶體？
- A簡: Pagefile 是磁碟上的擴充空間，輔助 RAM 形成較大的虛擬記憶體。
- A詳: Windows 以虛擬記憶體提供每行程的線性位址空間。當實體 RAM 不足時，會把不常用頁面換出至 pagefile（磁碟上的交換檔），以換取更大可用空間。代價是 I/O 延遲與隨機存取效能降低。文中 1GB RAM + 4GB pagefile 是測試的重要背景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, A-Q25

A-Q14: 什麼是本測試的「記憶體利用率%」？
- A簡: 指標=Phase3/Phase1，代表碎片化後仍能取得的可用比例。
- A詳: 以 Phase1 最大配置量為分母、Phase3 碎片化後可再獲得的量為分子，指標值愈高，表示面對碎片化時仍能維持較大可用連續空間。此相對化指標可減少平台間總量差異，凸顯資源回收與配置策略的效能差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q8

A-Q15: Windows Server 2012 R2 測試結論是什麼？
- A簡: Phase1 4416MB、Phase3 2888MB，記憶體利用率約 65.40%。
- A詳: 在 1GB RAM、預設約 4GB pagefile 的條件下，2012 R2 Server Core 執行 DNX 測得第一階段可配置約 4416MB。造成碎片化後重試，第三階段約 2888MB，可用比例 65.40%。顯示碎片化對連續配置能力有明顯影響，但整體行為穩定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q13

A-Q16: Windows Server 2016 容器測試結論是什麼？
- A簡: Phase1 4032MB、Phase3 2696MB，記憶體利用率約 66.87%。
- A詳: 在 Windows Server 2016 TP4 的 Windows Container 中，以 windowsservercore 映像建立環境，執行相同測試。第一階段可配置約 4032MB，第三階段約 2696MB，利用率 66.87%。結果與原生 2012 R2 相近，顯示容器共享 Kernel 的效能開銷很低。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q21

A-Q17: 為何 Windows Container 效能接近原生？
- A簡: 因共用宿主 Kernel，省去 Hypervisor 與完整客體 OS 開銷。
- A詳: 容器不模擬硬體，也無需啟動完整客體 OS；行程直接呼叫宿主 Kernel，省去 VM 層的轉譯與上下文切換開銷。文中實證其記憶體利用率與原生差距小，支持容器在 CPU/記憶體壓力下的效率優勢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, A-Q8

A-Q18: 為什麼需要 Windows Container？
- A簡: 提供可重現、隔離與高效率的部署單元，加速交付與運維。
- A詳: 容器將應用與相依封裝於映像，啟動快速、資源占用低，適合微服務、CI/CD 與彈性伸縮。對 .NET Core 而言，能確保跨環境一致性並快速驗證效能與資源行為。Windows Container 讓既有 .NET 生態能延續至 Windows 平台。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q5

A-Q19: 為何宿主 Task Manager 看得到容器內程序？
- A簡: 因共用同一 Kernel，容器行程屬於宿主的行程樹一部分。
- A詳: 容器以命名空間隔離視圖，但底層仍由宿主 Kernel 調度。因此宿主可見容器內行程（如 dnx.exe），並可在效能頁觀察記憶體與 CPU 曲線。這與 VM 完全隔離（看不到客體行程）不同。文中以此佐證容器架構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, A-Q8

A-Q20: 什麼是 dnx.exe？
- A簡: .NET Execution Environment 的執行程序，承載應用程式。
- A詳: dnx.exe 是 DNX 時期的執行主體，負責載入還原後的相依、JIT 編譯與啟動應用。文中以 Task Manager 觀察 dnx.exe 佔用約 4.5GB，反映測試程式大量配置與虛擬記憶體使用狀態，有助分析平臺差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q2

A-Q21: Server Core 與 Nano Server 差異？
- A簡: Nano 更精簡、無本機登入與 32 位支援；Server Core 較通用。
- A詳: Nano Server 是更激進的精簡選項，取消本機互動、僅遠端管理、移除大量元件與 32 位相容性，映像極小；Server Core 保留本機命令列、相容性較好。文中以 2016 TP4 之 Nano/Container 體驗對比 2012 R2 Server Core。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q5

A-Q22: 為何 Server Core 適合作為對照組？
- A簡: 元件少、干擾低，能更純粹地觀察執行期行為與資源。
- A詳: GUI 與額外服務會引入不可控開銷與噪音。Server Core 以最小化安裝減少背景程序與更新影響，使記憶體曲線與分配行為更可重現。作為 baseline 能凸顯容器層對行為的相對影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q15

A-Q23: 為何互動模式（-it）在 TP4 會較慢？
- A簡: 預覽版網路/主控端代理成熟度不足，交握與 I/O 延遲偏高。
- A詳: TP4 時期容器堆疊尚在演進，包含 Console attach、PTY 模擬、網路虛擬層與記錄管線可能未最佳化，互動模式下 I/O path 較長、封包轉譯成本高，體感延遲較明顯。隨版本前進通常會改善。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, D-Q2

A-Q24: Docker 工具如何在 Windows 上相容？
- A簡: 提供與 Docker 類似的命令與 API，同時也有 PowerShell 管理。
- A詳: Windows 容器支援 Docker Daemon 與 CLI 的相容操作（pull/run/exec/logs），並提供 Containers PowerShell 模組以原生方式管理生命週期。兩者共同指向 Windows 映像（如 windowsservercore），維持工具鏈一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q5, C-Q7

A-Q25: 測試中 RAM 與 pagefile 的關係為何？
- A簡: RAM 先用滿，超出部分換出到 pagefile，提升總可配置量。
- A詳: 在 1GB RAM 下，Phase1 初期 RAM 迅速用盡，隨即轉向虛擬記憶體，系統將冷頁換出至 pagefile（約 4GB），使進程位址空間仍可擴張至 4GB 量級。代價是存取延遲上升，但能完整觀察碎片化帶來的效應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, A-Q13

A-Q26: 本實驗的核心價值是什麼？
- A簡: 用一致流程量化跨平臺記憶體表現，檢核容器開銷與實務可行性。
- A詳: 透過統一的編譯/執行/觀測方法，以相對指標比較 Windows 原生與容器環境的記憶體行為，驗證容器效能接近原生，並揭示碎片化對可用度的影響。可作為平台選型與部署策略的實證依據。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, A-Q16, B-Q24

---

### Q&A 類別 B: 技術原理類

B-Q1: 測試程式如何模擬記憶體碎片化？
- A簡: 以不同大小的配置/釋放序列，打散連續空間製造間隙。
- A詳: 原理是先大量配置形成高水位，再以交錯釋放與重新配置的模式，特別是穿插大小不一的區塊，破壞原本連續的可用區。關鍵步驟：1) 連續配置至峰值；2) 以模式化序列釋放；3) 混合大小重配；4) 量測再配置可及上限。核心組件：堆積管理、配置器、GC/堆壓力回收。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q12

B-Q2: Task Manager 的記憶體曲線代表什麼？
- A簡: 反映實體記憶體用量、分頁活動與行程工作集變化。
- A詳: 工作管理員效能圖顯示 RAM 使用與分頁/快取波動；行程頁的工作集/提交大小對應進程實際駐留與已保留的虛擬空間。關鍵觀察：啟動尖峰=RAM 迅速填滿；之後主要依賴 pagefile 提升提交大小。核心組件：MM、分頁器、快取管理器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q25, B-Q9

B-Q3: 為何採用「重開機→還原→編譯→跑兩次」流程？
- A簡: 排除背景干擾與一次性成本，取得穩定可比的度量。
- A詳: 重開機減少殘留快取與外在負載；套件還原/編譯固定相依版本；跑兩次取第二次避免首次 JIT/IO 開銷。步驟：1) Reboot；2) 套件還原；3) 編譯；4) 連跑兩次；5) 取第二次。核心組件：nuget/dnu、JIT、檔案快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q2

B-Q4: Windows 容器與 Docker 工具鏈如何協作？
- A簡: 以 Docker Daemon/CLI 操控 Windows 映像，或用 PowerShell 管理。
- A詳: Windows 提供與 Docker 相容的 API/CLI，支援 pull/run/exec/logs 等指令，映像來源為 Windows 基底（windowsservercore、nanoserver）。PowerShell Containers 模組提供本地化管理。關鍵步驟：啟用容器功能→啟動 Docker/守護程序→操作映像/容器。核心組件：Docker Engine、Windows 容器執行層。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, C-Q5

B-Q5: 容器如何實作行程、檔案與網路隔離？
- A簡: 透過命名空間、檔案系統層與虛擬網路，隔離環境視圖。
- A詳: Windows 容器使用命名空間樣式機制隔離 PID/IPC/網路，檔案系統以分層唯讀+可寫層實作；網路以 vSwitch/NAT 虛擬化提供獨立網段。核心組件：Job Object、命名空間、Filter Driver、HNS（Host Network Service）。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q4, B-Q11

B-Q6: 為何 Linux 映像不可在 Windows 容器執行（技術面）？
- A簡: 系統呼叫介面與 Kernel ABI 完全不同，無法直接相容。
- A詳: 應用透過 libc/系統呼叫與 Kernel 溝通，Linux 與 Windows 在系統呼叫表、驅動模型、檔案/權限語意上大幅不同。容器共享宿主 Kernel，無法跨 Kernel 邊界轉譯。除非以 VM（如 Hyper-V、WSL2）承載 Linux Kernel，否則無法執行 Linux 容器映像。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, D-Q1

B-Q7: Hyper-V Container 的啟動流程與組成？
- A簡: 先起輕量 VM，再於其內啟動容器，對外仍以容器呈現。
- A詳: 管理層接收建立請求後，透過 Hyper-V 啟動精簡客體映像（與宿主版本相符），於其內載入容器執行層與映像，最後將端口/檔案映射回宿主。步驟：Create VM→Boot Guest→Start Container。組件：Hyper-V、Guest OS、容器執行層、管理代理。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, B-Q22, D-Q9

B-Q8: 「Phase3/Phase1」指標合理性何在？
- A簡: 把總量差異消除，專注衡量碎片化後的可用比例。
- A詳: 不同平台的總可配置量受 RAM/pagefile/配置策略影響。以比值方式，可部份抵消總量差異，聚焦於碎片化與回收機制效率，提升跨平台比較的公平性與可解釋性。限制：仍受配置模式與記憶體分頁策略左右。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q24

B-Q9: Pagefile 與實體 RAM 在測試中的角色？
- A簡: RAM 供熱路徑；Pagefile 擴大提交空間但增加延遲。
- A詳: RAM 速度快，承擔活躍工作集；當提交大小超過 RAM，系統以 pagefile 換出冷頁維持更大位址空間。測試高峰主要由提交大小推動，觀察到 RAM 滿載後，曲線續增代表分頁活躍。核心：分頁器、LRU、工作集修剪。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, A-Q25

B-Q10: 為何 dnx.exe 顯示高記憶體占用？
- A簡: 大量托管堆配置、JIT/中繼資料載入與提交空間膨脹。
- A詳: DNX 承載應用，配置大量物件與緩衝；JIT 編譯、組件中繼資料與各種緩存提升提交大小。碎片化後，堆空間更難緊縮，提交空間維持高位。觀測重點：工作集 vs 提交大小、GC 週期、LOH 行為（概念上）。核心：CLR 記憶體管理、JIT、Loader。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, D-Q3

B-Q11: 宿主與容器的資源視圖如何映射？
- A簡: 容器行程由宿主排程；隔離視圖由命名空間提供。
- A詳: 宿主 Kernel 管理所有實體資源；容器只改變可見範圍與命名空間。Task Manager 能見行程與總體記憶體曲線，容器內工具則看到受限的命名空間。網路/檔案映射透過虛擬層實現。核心：命名空間、Job Objects、HNS。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, B-Q5

B-Q12: 為什麼第二次執行較穩定？
- A簡: JIT/檔案快取/套件還原已完成，減少一次性抖動。
- A詳: 首次執行會觸發 nuget 還原、磁碟讀寫、JIT 編譯；OS 快取與 CLR 內部緩存建立後，第二次執行少了這些開銷，記憶體曲線與時間表現更平滑。步驟：觀測兩次→取第二次。核心：檔案系統快取、JIT、程式啟動路徑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q8

B-Q13: 2012 R2 與 2016 容器的差異如何影響指標？
- A簡: 共享 Kernel 的容器開銷小，利用率與原生相近。
- A詳: 2016 容器在相近 RAM/pagefile 下，Phase3/Phase1 與 2012 R2 差距很小（~1.5pt）。顯示容器層（命名空間、分層檔系統）對本測指標影響有限。主要受堆配置策略與 OS 記憶體管理主導。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q16

B-Q14: 互動模式為何影響操作體感？
- A簡: 終端附掛需經由多層代理/轉譯，I/O 路徑較長。
- A詳: docker -it 會經由守護行程、Named Pipe/REST、PTY 模擬與網路虛擬層傳遞標準輸入輸出。預覽版最佳化不足，使輸入回顯與輸出體感延遲。可改以非互動執行與檔案方式收集結果緩解。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, D-Q2

B-Q15: Server Core 與 Nano 的技術差異？
- A簡: Nano 去除本機互動與大量元件，偏遠端與容器場景。
- A詳: Nano 移除 GUI、WoW64、MSI 等，僅支援部分 Server 角色；Server Core 保有本機 Shell 與較佳相容。Nano 容器映像更小、啟動更快。取捨：相容性 vs 體積/攻擊面。核心：組件化、遠端管理、映像分層。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q5

B-Q16: 容器隔離的層次有哪些？
- A簡: 行程/命名空間、檔案分層、網路虛擬化與資源配額。
- A詳: 進程與 IPC 隔離避免跨容器干擾；檔案分層保證每容器可寫層；虛擬網路提供獨立命名空間；資源控制（如 Job Object、配額）限制使用量。核心：命名空間、Filter Driver、HNS、Job Object/計量。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q11

B-Q17: 用 Server Core 映像建 .NET Core 需哪些元件？
- A簡: 基底映像、DNX/CLI、NuGet 相依與必要系統元件。
- A詳: 以 windowsservercore 映像為基底，安裝 DNX（或新版 .NET SDK）、NuGet 來源與相依原生組件（vc++ runtime 等）。步驟：更新包管理→裝 DNX/SDK→還原→編譯→執行。組件：CLR/CoreCLR、JIT、nuget/源、證書信任根。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q1

B-Q18: 容器中開發環境如何保持可重現？
- A簡: 以 Dockerfile 分層宣告安裝步驟，確保映像一致。
- A詳: 透過分層映像記錄安裝命令與版本，重建時重放相同步驟，確保環境可重現。關鍵步驟：鎖定套件版本、使用內部鏡像、驗證雜湊。核心：分層檔系統、內容可位址、快取重用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q10

B-Q19: 測試資料的可靠性可能受哪些變因影響？
- A簡: 背景負載、IO/網路、版本差異與配置策略。
- A詳: 背景行程、磁碟/網路擁塞、DNX/OS 版本差異、pagefile 大小/策略都會影響曲線與峰值。控制方法：重啟隔離、釘版本、鎖定配置、跑多次取中位。核心：實驗設計、統計穩健性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q4

B-Q20: 為何碎片化會降低可用連續記憶體？
- A簡: 空間雖總量足夠，但被切碎成小塊，難以滿足大配額。
- A詳: 配置器需要連續區塊來滿足請求；碎片化使空洞分散與對齊困難，導致大配置失敗或降為較小配置。GC/壓縮策略若受限於釘選物件或大物件堆（LOH），更難合併空間。核心：堆管理、碎片合併、釘選與 LOH。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q1

B-Q21: 為何容器效能與原生差距小？
- A簡: 少虛擬化層、系統呼叫直通 Kernel，減少上下文成本。
- A詳: 系統呼叫不經 Hypervisor 翻譯，I/O 資源由宿主直接管理；檔案/網路僅加一層虛擬視圖與過濾。故 CPU/記憶體密集工作接近原生。文中記憶體利用率相近即為佐證。核心：系統呼叫路徑、調度、資源管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, A-Q16

B-Q22: Hyper-V Container 的性能代價與安全性取捨？
- A簡: 多一層客體 OS 成本，換來 Kernel 隔離與版本一致性。
- A詳: 每容器一 VM 帶來啟動時間與記憶體足跡增加，但能隔離 Kernel、避免命名空間逃逸，允許多租戶與版本差異共存。選擇策略：高安全/合規→Hyper-V；追求極致效率→Windows Container。核心：Hyper-V、隔離邊界、供應合規。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q7, D-Q9

B-Q23: 將容器視為「像 VM」的侷限？
- A簡: 錯把 Kernel 共享忽略，產生錯誤的隔離與可攜性期待。
- A詳: 容器並非全系統虛擬化；映像需與宿主 Kernel 匹配，系統層功能受限於宿主能力。錯誤假設會導致跨 OS 遷移失敗與安全邊界誤用。核心：Kernel 相容性、隔離層界線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q6

B-Q24: 以 Phase1/Phase3 衡量跨平台的侷限？
- A簡: 受配置模式、GC/分頁策略影響，僅反映相對趨勢。
- A詳: 比值可減少總量差異，但仍受應用分配型態、GC 行為、OS 分頁策略影響，對 CPU/IO 等其他維度無法涵蓋。建議搭配多次取樣與其他指標（延遲、吞吐）共同解讀。核心：實驗外部效度、統計方法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q19

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Windows Server 2012 R2 Server Core 安裝 DNX？
- A簡: 以 PowerShell 安裝 Chocolatey→dnvm→dnx，再設定環境與路徑。
- A詳: 步驟
  - 以管理員 PowerShell 啟用 TLS 並裝 choco: Set-ExecutionPolicy Bypass; iex (New-Object Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')
  - 安裝 dnvm: choco install dnvm -y
  - 安裝 CoreCLR 64 位 DNX: dnvm install latest -r coreclr -arch x64
  - 使用預設: dnvm use default
  注意: Server Core 無 GUI，請確保代理/憑證設定良好；優先選用離線套件源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q17

C-Q2: 如何編譯並執行記憶體測試（DNX）？
- A簡: 還原套件→編譯→連續執行兩次，取第二次數據。
- A詳: 步驟
  - 進入專案資料夾，還原: dnu restore
  - 編譯: dnu build（或直接 dnx run）
  - 執行兩次：dnx run；dnx run
  - 記錄 Phase1/3 數據，計算利用率=Phase3/Phase1
  注意: 使用 Release 組態；固定相依版本；記錄同一環境下的測值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q11

C-Q3: 如何設定 pagefile 大小以配合測試？
- A簡: 於系統進階設定將虛擬記憶體改為固定大小（如 4GB）。
- A詳: 步驟（Server Core 可用 PowerShell）：
  - 關閉自動管理: wmic computersystem where name="%computername%" set AutomaticManagedPagefile=False
  - 設定 C: 固定大小 4096MB: wmic pagefileset where name="C:\\pagefile.sys" set InitialSize=4096,MaximumSize=4096
  - 重開機生效
  注意: 磁碟剩餘空間需足夠；避免與其他服務共用導致干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, A-Q25

C-Q4: 如何在宿主觀察容器內程序與記憶體？
- A簡: 用宿主 Task Manager/PowerShell 檢視 dnx.exe 工作集與提交大小。
- A詳: 步驟
  - 宿主開啟 Task Manager（Server Core 可輸入 taskmgr.exe）
  - 於 Details 檢視容器內進程（如 dnx.exe）
  - 以 PowerShell: Get-Process dnx | Select Name,WS,PM,VM
  注意: 需系統管理員權限；Hyper-V 容器因在客體 OS，宿主不直接可見客體進程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q11

C-Q5: 如何建立 Windows 2016 容器並安裝 DNX？
- A簡: 啟用容器功能→拉取 windowsservercore→互動安裝 DNX。
- A詳: 步驟
  - 啟用容器: Enable-WindowsOptionalFeature -Online -FeatureName containers -All
  - 安裝 Docker（官方指南）並啟動服務
  - 拉取映像: docker pull mcr.microsoft.com/windows/servercore
  - 啟容器: docker run -it --name memtest mcr.microsoft.com/windows/servercore powershell
  - 內部安裝 choco/dnvm/dnx（同 C-Q1）
  注意: 選擇與宿主版本匹配映像；代理/憑證設定影響下載。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, B-Q4

C-Q6: 如何以互動模式在容器中執行測試？
- A簡: docker run -it 進入容器，還原、編譯並連續執行兩次。
- A詳: 步驟
  - 啟動容器並附掛：docker run -it <image> powershell
  - 下載/掛載程式碼（Volume 或 Invoke-WebRequest）
  - dnu restore → dnu build → dnx run x2
  - 將結果輸出至檔案：dnx run > C:\out\log.txt
  注意: 互動模式延遲較大；建議以 docker exec 非互動與檔案收集。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q23, B-Q14

C-Q7: 如何用 PowerShell 管理 Windows 容器？
- A簡: 透過 Containers 模組執行新建、啟動、列出與移除操作。
- A詳: 步驟（TP4/2016）
  - 匯入模組：Import-Module Containers
  - 建立：New-Container -Name memtest -ContainerImageName windowsservercore
  - 啟動：Start-Container memtest；附加：Enter-PSSession -ContainerId ...
  - 停止/刪除：Stop-Container；Remove-Container
  注意: cmdlet 名稱依版本可能不同；建議優先參照對應文件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, B-Q4

C-Q8: 如何記錄兩次執行並計算「記憶體利用率%」？
- A簡: 解析輸出取得 Phase1/3 數字，計算比值取小數點兩位。
- A詳: 步驟
  - 執行兩次：dnx run；dnx run
  - 以簡單腳本擷取 Phase1/3 值（例如 Select-String）
  - 計算：利用率=Phase3/Phase1×100；四捨五入至 0.01
  - 輸出 CSV 便於對比
  注意: 格式需一致；以第二次數據為準；保留原始日誌供稽核。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q3

C-Q9: 在 Server Core 如何啟動 Task Manager？
- A簡: 於命令列輸入 taskmgr.exe，亦可用 perfmon/Get-Counter。
- A詳: 步驟
  - Cmd 輸入：taskmgr.exe 可開啟工作管理員
  - 或以 PowerShell 監控：Get-Process；Get-Counter '\Memory\*'
  - 可用 typeperf 匯出 CSV 供後續分析
  注意: 若最小化安裝無組件，改用 PowerShell 計數器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q4

C-Q10: 用現代 .NET CLI 重現該測試要怎麼做？
- A簡: 安裝 .NET SDK→dotnet restore/build/run→邏輯同前。
- A詳: 步驟
  - 安裝 .NET SDK（Windows 容器可用 nanoserver/servercore 對應映像）
  - 還原：dotnet restore；編譯：dotnet build -c Release
  - 執行兩次：dotnet run -c Release；再執行一次
  - 解析輸出計算 Phase3/1
  注意: CLI 與 DNX 指令不同；鎖定 SDK 版本（global.json/使用 roll-forward 設定）以確保可重現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, C-Q8

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 容器內無法使用 Linux 映像怎麼辦？
- A簡: 選用 Windows 基底映像（servercore/nanoserver），勿混用跨 OS 映像。
- A詳: 症狀: pull Linux 映像後 run 失敗或提示不相容。原因: 容器共享宿主 Kernel，不支援跨 Kernel 映像。解法: 改用 mcr.microsoft.com/windows/* 系列，並確保版本相容。預防: 宿主/映像 OS Build 對齊，於 CI 鎖定映像標籤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q6

D-Q2: 互動模式（-it）極慢或卡頓怎麼辦？
- A簡: 改用非互動執行、記錄輸出，升級版本並優化網路資源。
- A詳: 症狀: 輸入延遲、輸出卡頓。原因: 預覽版 Console/PTY 管線未優化、網路虛擬層延遲。解法: 用 docker exec 非互動、將輸出重導至檔案；調高 CPU/RAM；升級至較新版本。預防: 只在必要時使用 -it，平時以腳本批次。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q23, B-Q14

D-Q3: dnx.exe 記憶體異常升高如何診斷？
- A簡: 比對工作集/提交大小、檢查配置模式與 GC 日誌，調整建置。
- A詳: 症狀: 提交大小飆升、回收不明顯。原因: 大量配置、LOH 碎片、Debug 組建符號。解法: 切 Release、減少大物件、分批配置；以 PerfView/ETW 觀察 GC。預防: 監控配置型態、限制峰值、壓力測試前預熱。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q20

D-Q4: 第二次執行仍波動很大怎麼辦？
- A簡: 檢查還原/快取、背景負載與 I/O 瓶頸，多跑取中位數。
- A詳: 症狀: 第二次仍抖動。原因: 背景更新、磁碟擁塞、網卡/代理不穩。解法: 斷網路還原、關閉更新、固定資源；跑多次取中位。預防: 建立隔離測試節點、鎖版本、預備離線快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, C-Q8

D-Q5: dnu restore/編譯失敗怎麼辦？
- A簡: 檢查網路/代理與來源，改離線快取或鎖定套件版本。
- A詳: 症狀: 還原逾時、相依衝突。原因: 代理阻擋、源不穩或版本不相容。解法: 設定 nuget.config 私有源；鎖定版本；離線快取；重試策略。預防: 企業鏡像伺服器、版本凍結與簽章驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q3

D-Q6: Server Core 無 GUI 如何觀察資源？
- A簡: 使用 taskmgr.exe、Get-Process、Get-Counter、typeperf 匯出。
- A詳: 症狀: 無圖形介面。解法: 命令列啟動 taskmgr.exe；PowerShell 查詢 Get-Process/Measure-Object；Get-Counter 或 typeperf 監控計數器、匯出 CSV。預防: 建立常用監控腳本；使用遠端管理（PerfMon/RSAT）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, C-Q4

D-Q7: Pagefile 設定不當導致數據失真？
- A簡: 固定大小並確保磁碟空間，避免自動調整引起波動。
- A詳: 症狀: 峰值不穩、曲線劇烈跳動。原因: 自動管理動態擴張/收縮造成碎片與 IO 抖動。解法: 固定大小；預留空間；重開機生效。預防: 測前檢查配置，保持磁碟健康與穩定吞吐。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, A-Q25

D-Q8: 宿主 Task Manager 看不到容器內程序？
- A簡: 可能是 Hyper-V 容器或權限不足，改用客體內工具觀察。
- A詳: 症狀: 宿主無法見容器進程。原因: 若為 Hyper-V Container，程序存在於客體 OS；或宿主權限不足。解法: 於容器/客體內觀察；或以 Docker/PowerShell 查詢。預防: 確認容器模式；使用系統管理權限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q11

D-Q9: Hyper-V Container 無法啟動怎麼辦？
- A簡: 檢查 Hyper-V 角色、硬體虛擬化與映像版本匹配。
- A詳: 症狀: 建立/啟動失敗。原因: Hyper-V 未啟用、CPU 不支援 VT-x/SLAT、映像/宿主版本不一致。解法: 啟用 Hyper-V；更新 BIOS；匹配映像版本。預防: 以基準模板部署；版本控管與健檢腳本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q7

D-Q10: 宿主與映像版本不匹配導致容器無法運行？
- A簡: 使用與宿主相容的映像標籤，避免跨 Build 組合。
- A詳: 症狀: 啟動錯誤、API 不相容。原因: Windows 容器需與宿主 Kernel/OS build 對齊。解法: 選用相同版號映像（如 ltsc2019/windowsservercore）；升級宿主或降版映像。預防: 版本策略與 CI 驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, B-Q23

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是「記憶體管理大考驗」測試？
    - A-Q2: 什麼是 .NET Core（DNX 版）？
    - A-Q3: 什麼是 Windows Server 2012 R2 Server Core？
    - A-Q4: 什麼是 Windows Container？
    - A-Q5: 為何 Windows Container 不能使用 Linux 映像？
    - A-Q8: Windows Container 與傳統 VM 有何差異？
    - A-Q10: 測試中的 Phase 1 與 Phase 3 是什麼？
    - A-Q11: 為什麼要連續執行兩次，以第二次為準？
    - A-Q12: 什麼是記憶體碎片化？
    - A-Q13: 什麼是頁面檔（pagefile）與虛擬記憶體？
    - A-Q14: 什麼是本測試的「記憶體利用率%」？
    - A-Q15: Windows Server 2012 R2 測試結論是什麼？
    - A-Q16: Windows Server 2016 容器測試結論是什麼？
    - C-Q2: 如何編譯並執行記憶體測試（DNX）？
    - C-Q9: 在 Server Core 如何啟動 Task Manager？

- 中級者：建議學習哪 20 題
    - A-Q17: 為何 Windows Container 效能接近原生？
    - A-Q18: 為什麼需要 Windows Container？
    - A-Q19: 為何宿主 Task Manager 看得到容器內程序？
    - A-Q21: Server Core 與 Nano Server 差異？
    - A-Q22: 為何 Server Core 適合作為對照組？
    - A-Q23: 為何互動模式（-it）在 TP4 會較慢？
    - A-Q24: Docker 工具如何在 Windows 上相容？
    - B-Q3: 為何採用「重開機→還原→編譯→跑兩次」流程？
    - B-Q4: Windows 容器與 Docker 工具鏈如何協作？
    - B-Q8: 「Phase3/Phase1」指標合理性何在？
    - B-Q9: Pagefile 與實體 RAM 在測試中的角色？
    - B-Q12: 為什麼第二次執行較穩定？
    - B-Q13: 2012 R2 與 2016 容器差異如何影響指標？
    - C-Q1: 如何在 Server Core 安裝 DNX？
    - C-Q3: 如何設定 pagefile 大小以配合測試？
    - C-Q4: 如何在宿主觀察容器內程序與記憶體？
    - C-Q5: 如何建立 Windows 2016 容器並安裝 DNX？
    - C-Q6: 如何以互動模式在容器中執行測試？
    - C-Q8: 如何記錄兩次執行並計算「記憶體利用率%」？
    - D-Q2: 互動模式（-it）極慢或卡頓怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q6: 什麼是 Hyper-V Container？
    - A-Q7: Windows Container 與 Hyper-V Container 差異？
    - B-Q1: 測試程式如何模擬記憶體碎片化？
    - B-Q5: 容器如何實作行程、檔案與網路隔離？
    - B-Q6: 為何 Linux 映像不可在 Windows 容器執行（技術面）？
    - B-Q7: Hyper-V Container 的啟動流程與組成？
    - B-Q10: 為何 dnx.exe 顯示高記憶體占用？
    - B-Q11: 宿主與容器的資源視圖如何映射？
    - B-Q15: Server Core 與 Nano 的技術差異？
    - B-Q16: 容器隔離的層次有哪些？
    - B-Q20: 為何碎片化會降低可用連續記憶體？
    - B-Q21: 為何容器效能與原生差距小？
    - B-Q22: Hyper-V Container 的性能代價與安全性取捨？
    - D-Q8: 宿主 Task Manager 看不到容器內程序？
    - D-Q9: Hyper-V Container 無法啟動怎麼辦？