---
layout: synthesis
title: "用 WSL + VSCode 重新打造 Linux 開發環境"
synthesis_type: faq
source_post: /2024/11/11/working-with-wsl/
redirect_from:
  - /2024/11/11/working-with-wsl/faq/
postid: 2024-11-11-working-with-wsl
---

# 用 WSL + VSCode 重新打造 Linux 開發環境

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 WSL（Windows Subsystem for Linux）？
- A簡: WSL 是在 Windows 上提供 Linux 環境的相容層與輕量虛擬化，讓你直接執行 Linux 工具與應用。
- A詳: WSL 是 Microsoft 在 Windows 上提供的 Linux 執行環境。WSL1 以系統呼叫轉譯方式提供相容性，WSL2 起改用輕量級虛擬化（Hyper-V）與完整 Linux kernel。你可以用 WSL 在 Windows 原生執行 bash、包管理、Docker（於 WSL2）、GPU 工作負載，以及與 Windows 工具互通（檔案、網路、VS Code 等），大幅降低跨系統開發摩擦。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q10, B-Q1

Q2: WSL1 與 WSL2 的差異是什麼？
- A簡: WSL1 是系統呼叫轉譯，WSL2 是完整 Linux kernel 的輕量虛擬機，支援度與效能更好。
- A詳: WSL1 透過轉譯 Linux 系統呼叫到 Windows 內核 API，啟動快、IO 對 NTFS 友好，但相容性有限。WSL2 使用 Hyper-V 啟動輕量 VM 搭載 Linux kernel，對容器、網路、檔案系統、GPU 等支援完整，整體相容性與效能更佳。代價是多一道虛擬化層，跨系統檔案 IO 需注意。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q3, A-Q10

Q3: 什麼是 DrvFS？
- A簡: DrvFS 是 WSL 存取 Windows NTFS 檔案系統的橋接檔案系統，位於 /mnt/c 等掛載點。
- A詳: DrvFS 由 Microsoft 開發，讓 WSL 以 Linux 風格路徑（如 /mnt/c）存取 Windows NTFS。它將 Linux VFS 要求透過 9P 等機制定向到 Windows 檔案系統。雖然便利，但在大量隨機小 IO 下延遲高、吞吐低，且部分 NTFS 特性（ACL、Stream）與 Linux 權限模型不完全對應。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q14, A-Q15

Q4: 什麼是 9P 協定（9p protocol）？
- A簡: 9P 是一種檔案系統通訊協定，WSL 用它在 Windows 與 Linux 之間轉送檔案操作。
- A詳: 9P（Plan 9 Filesystem Protocol）是輕量檔案協定，讓不同系統以訊息交換方式操作檔案。WSL 用 9P 在 Windows 與 Linux 核心間傳遞開檔、讀寫、列舉等請求。跨 kernel 必經此轉換，加入延遲與額外複雜度，是跨系統 IO 性能顯著降低的主因之一。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q16, A-Q3

Q5: WSL 的 ext4.vhdx 是什麼？
- A簡: ext4.vhdx 是 WSL2 的 Linux 根檔案系統，儲存在 Windows 檔案系統上的虛擬硬碟檔。
- A詳: WSL2 採用 Hyper-V 輕量 VM，Linux 檔案系統存於 ext4.vhdx 虛擬磁碟（預設於使用者 LocalState）。WSL 內的根檔系（如 /home）實際寫入此 vhdx。此層虛擬化帶來些許開銷，但避免跨 kernel 存取時能獲得顯著效能優勢，適合放置 IO 密集的資料（如資料庫、容器卷）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q8, D-Q8

Q6: 為什麼要在 Windows 上建立 Linux 原生開發環境？
- A簡: 因為越來越多工具與部署目標在 Linux，開發、測試與部署一致可減少摩擦。
- A詳: 多數雲端、容器、AI/資料科學堆疊皆以 Linux 為一級公民。於 Windows 以 WSL 建 Linux 原生環境，可直接使用 Linux 工具鏈、容器、GPU 工作負載，並透過 VS Code Remote 保留 Windows 使用體驗。這讓開發、測試與生產行為一致，降低「在我機器可運行」的落差。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q9, C-Q4

Q7: 為什麼拋開 Docker Desktop for Windows？
- A簡: 為避授權與額外負擔，改在 WSL 原生 Docker，功能足夠且更單純高效。
- A詳: 對多數開發者，Docker Desktop 提供的是便利整合，但也帶來授權限制、資源開銷與跨系統 IO 瓶頸。直接在 WSL 內跑 Docker Engine，可少轉換層，卷（volume）放在 Linux 檔系，效能與相容性更好，也便於 GPU/AI 堆疊使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, C-Q3, D-Q1

Q8: 為什麼 Docker 掛載 volume 在 Windows 很慢？
- A簡: 因為容器透過 DrvFS/9P 跨 kernel 存取 NTFS，隨機小 IO 延遲大，效能極差。
- A詳: 在 Windows 啟動的容器若將宿主 NTFS 目錄映射進 Linux 容器，將經 DrvFS→9P→Windows NTFS 多層轉譯。此路徑對 4K 隨機讀寫、深 iodepth、並行工作負載特別不利，常見效能僅剩原生的幾％。Qdrant、Jekyll 這類大量小檔或隨機 IO 的服務表現會非常糟。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q1, C-Q3

Q9: WSL→Windows 與 Windows→WSL 的存取差異是什麼？
- A簡: 前者經 DrvFS，後者經 9P+虛擬化；兩者皆慢，但 Windows→WSL 常更慢。
- A詳: WSL 應用存取 Windows 檔案走 DrvFS（實際也經 9P），Windows 存取 WSL 檔案走 9P 並觸及 vhdx 虛擬層。實測顯示原生（Win→NTFS）最快，WSL→WSL 次之，跨系統雙向都顯著變慢，其中 Windows→WSL 常為最差路徑，不適合高 IO 場景。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q4, B-Q5

Q10: 為什麼把資料移到 WSL rootfs（EXT4）會加速？
- A簡: 因避免跨 kernel/DrvFS/9P，僅留虛擬磁碟開銷，IO 路徑最短。
- A詳: 將容器卷與資料直接放在 WSL 的 EXT4 rootfs 或直掛 EXT4 實體分割，可避開跨系統橋接，IO 僅經 Hyper-V 虛擬磁碟，延遲低、吞吐可觀。實測資料庫啟動時間可縮至原本 1/25，Jekyll 建置至約 1/18，整體體感顯著改善。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q7, C-Q8

Q11: 為什麼 VS Code Remote Development 能解決跨系統協作？
- A簡: 它在遠端（WSL）跑 Server，前端在 Windows，只傳遞互動，避免跨 OS IO。
- A詳: VS Code Remote 架構採前後端分離：UI 在 Windows，本體在 WSL 的 VS Code Server 執行，負責檔案存取、終端、除錯、擴充。這使你使用 Windows 的鍵鼠與視窗體驗，同時交由 WSL 原生檔案系統處理重 IO 與工具鏈，兼顧效能與便利。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q4

Q12: 什麼是 VS Code Server？
- A簡: VS Code Server 是遠端端元件，在 WSL/容器/SSH 遠端執行，供本地 VS Code 使用。
- A詳: VS Code Server 是支撐 Remote Development 的服務端，部署於 WSL、容器或遠端機，處理檔案、命令、擴充與除錯等，透過通道與本地 VS Code UI 溝通。它讓你的原始碼與執行環境留在遠端，卻仍享有本地體驗與全功能 IntelliSense 與調試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q4

Q13: 什麼是 binfmt_misc 與 WSLInterop？
- A簡: binfmt_misc 讓 Linux 認得非 ELF 可執行格式；WSLInterop 用它啟動 Windows 可執行檔。
- A詳: Linux 的 binfmt_misc 可登記「非常規格式」的啟動方式。WSL 將 PE（Windows .exe）簽頭註冊到 binfmt_misc，透過 WSLInterop 將執行導向 /init 的代理，最終觸發 Windows 主機執行實體 .exe。故你可在 bash 直接執行 cmd.exe、explorer.exe 等。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q18, C-Q4

Q14: FileSystemWatcher 與 inotify 有何差異？
- A簡: 前者為 Windows NTFS 事件，後者為 Linux 檔案事件；跨 DrvFS 時對應不完全。
- A詳: FileSystemWatcher 是 .NET/Windows 對 NTFS 的檔案變更事件；inotify 為 Linux 核心事件機制。DrvFS 是跨系統橋接，無法完整雙向映射所有事件，導致容器掛 NTFS 時常需輪詢而非事件觸發，熱重載/增量建置失靈或延遲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, B-Q5, C-Q5

Q15: 什麼是 NTFS Streams（附加資料串流）？
- A簡: NTFS 支援一檔多串流，除主要內容外可有額外資料串流，Linux 不支援此特性。
- A詳: NTFS 可在同一檔案中儲存多個資料流（如 filename:streamname），用於儲存附加屬性或附檔。Linux 不支援該模型，透過 WSL 看 NTFS 可能看到「怪異檔案」樣態或完全無法映射。跨系統時應避免依賴此特性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, D-Q9

Q16: 什麼是 WSLg？
- A簡: WSLg 讓 WSL 直接執行 Linux GUI 應用，並無縫顯示於 Windows 桌面。
- A詳: WSLg 整合 Wayland/X11 顯示堆疊、音訊與輸入裝置，讓你在 WSL 啟動圖形應用（如 gedit、Firefox），視窗出現在 Windows 桌面，可與 Windows 應用 Alt-Tab 切換、開始選單啟動、剪貼簿互通。適合需要 Linux GUI 工具的情境。
- 難度: 初級
- 學習階段: 進階
- 關聯概念: B-Q22

Q17: WSL 的 GPU 虛擬化是什麼？
- A簡: 透過 WDDM 與 Hyper-V 將實體 GPU 虛擬化給 WSL，暴露 /dev/dxg 供圖算使用。
- A詳: Windows 端以 WDDM 2.9+ 驅動與 Hyper-V 將 GPU 能力虛擬化至 WSL，Linux 端暴露 /dev/dxg 裝置。Microsoft 提供對應驅動與對接層，使 DirectX、DirectML 以及經轉接的 CUDA/OpenCL 可在 WSL 使用，容器亦能派用 GPU 計算。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q13, C-Q9

Q18: /dev/dxg 代表什麼？
- A簡: /dev/dxg 是 WSL 中虛擬化 GPU 的裝置節點，對應 DirectX Graphics 的介面。
- A詳: 為將 Windows GPU 能力共享到 WSL，Microsoft 在 Linux 端提供 /dev/dxg 裝置與驅動，作為圖形與通用計算的入口。上層可經由 DirectX/DxCore 對接，或由 CUDA/OpenCL/DirectML 經轉接層使用。nvidia-smi 在 WSL 能看到裝置即得益此機制。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q13, C-Q9

Q19: 什麼是 DirectML？與 WSL 的關係？
- A簡: DirectML 是 Windows 上基於 DX 的機器學習 API，WSL 亦可對接使用。
- A詳: DirectML 以 DirectX/D3D12 為基礎提供 ML 加速，ONNX Runtime 可對接 DirectML。透過 WSL 的 GPU 虛擬化，Microsoft 對應層讓 DirectML 亦能在 WSL 堆疊使用，為 .NET、容器化 ML 工作負載在混合 Windows/WSL 場景移植鋪路。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q9

Q20: 為何建議給 WSL 專用 SSD 並使用 EXT4？
- A簡: 專用 SSD、原生 EXT4 可繞過 NTFS/DrvFS/9P，獲得接近或超越原生效能。
- A詳: 專用 SSD 以 EXT4 格式直掛 WSL，可避免系統共用干擾與 NTFS 橋接，隨機 IO 表現顯著提升。實測 MLC 顆粒 SSD 可達至或超越 Windows 下 NTFS 原生表現；虛擬磁碟（vhdx）也可接近原生。建議將資料庫卷、構建快取放於此類掛載。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, C-Q7, C-Q8

Q21: SSD 顆粒（MLC/TLC/QLC）對 WSL 效能影響？
- A簡: 高負載隨機 IO 下，MLC 常優於 TLC，QLC 最弱；顆粒勝過介面規格。
- A詳: 在 4K 隨機、多工作併發的資料庫型負載，顆粒寫入耐受與內部佇列管控影響很大。實測顯示 MLC 老旗艦仍可勝過新款 TLC，甚至壓過 QLC。若工作以隨機 IO 為主，顆粒選擇比介面（Gen3/4）更關鍵，QLC+DRAMless 不建議用於工作卷。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q17, C-Q7

Q22: 為何把 DrvFS 視為「網路磁碟」？
- A簡: 因其經橋接協定與跨 kernel 轉送，特性類似遠端檔案分享，延遲高吞吐低。
- A詳: DrvFS 需將 Linux VFS 請求轉譯為 9P/Windows 調用，行為更像 SMB/NFS 類遠端存取。適合輕量操作、檔案搬運、簡易整合，不適合高頻小 IO 或低延遲需求。設計工作流程時，將其當網路磁碟能設定合理期望與架構。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q16, D-Q7

---

### Q&A 類別 B: 技術原理類

Q1: WSL 的四種檔案存取路徑如何運作？
- A簡: 四路徑為 Win→NTFS、WSL→EXT4、Win→WSL(9P+虛擬)、WSL→Win(DrvFS)。
- A詳: 技術原理說明：路徑含(a)Windows 應用→NTFS（原生最快）、(b)WSL 應用→EXT4（虛擬磁碟）、(c)Windows → WSL（9P+vhdx 虛擬層）、(d)WSL → Windows（DrvFS）。關鍵步驟或流程：每跳跨 kernel/協定皆引入延遲。核心組件：Hyper-V、9P、DrvFS、ext4.vhdx。理解此路徑可指導你把資料放在最短路徑處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q4, A-Q5

Q2: Windows→Windows（NTFS 原生）流程與代表意義？
- A簡: 直接落在 NTFS，無跨 kernel 與協定轉換，作為性能對照組。
- A詳: 技術原理說明：Windows 應用直存 NTFS，走最短路徑。關鍵步驟：系統快取、I/O 排程、控制器直通。核心組件：Windows I/O stack、NTFS 驅動。此情境提供硬體與 OS 原生上限參考，用以評估其他路徑折損比例與最佳化空間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q3

Q3: WSL→WSL（EXT4.vhdx）流程與 Hyper-V 影響？
- A簡: 走 Linux 原生 EXT4，但在 vhdx 虛擬磁碟，僅有虛擬化開銷。
- A詳: 技術原理說明：I/O 由 Linux kernel 進 EXT4，映射至 vhdx，經 Hyper-V 虛擬層寫入宿主儲存。關鍵步驟：虛擬磁碟元資料、I/O 合併。核心組件：EXT4、Hyper-V、vhdx。比跨系統快得多，適合放重 IO 卷，如 DB、建置快取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q3, C-Q8

Q4: Windows→WSL（9P+虛擬）背後機制？
- A簡: Windows 透過 9P 存取 WSL EXT4，再經 vhdx 虛擬層，延遲累計最高。
- A詳: 技術原理說明：在 Windows 發起檔案操作，透過 9P 傳遞至 WSL，再進 EXT4/vhdx。關鍵步驟：協定協商、訊息封包、虛擬磁碟轉譯。核心組件：9P server/client、EXT4、Hyper-V。此路徑在隨機小 IO 最差，應避免作為容器卷或 DB 資料位置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q9, D-Q1

Q5: WSL→Windows（DrvFS）流程與限制？
- A簡: WSL 以 DrvFS 橋接 NTFS，特性難與 Linux 權限/事件完全對應。
- A詳: 技術原理說明：WSL 中的開檔/寫入由 DrvFS 轉成 9P/Win I/O。關鍵步驟：權限映射、事件轉換。核心組件：DrvFS、9P、NTFS。對熱更新、檔案監聽常需輪詢；延遲較高，建議視為「網路盤」只做輕量操作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q14, D-Q2

Q6: fio 測試參數如何設計？為何重點在 iodepth/numjobs/bs？
- A簡: 以 4K 隨機、8 jobs、iodepth 64、direct=1 模擬資料庫型負載。
- A詳: 技術原理說明：資料庫常為小區塊隨機 I/O。關鍵步驟：bs=4k、rw=randrw、numjobs=8、iodepth=64、direct=1（繞過快取）。核心組件：fio 引擎（linuxaio、windowsaio）。此設計暴露延遲與併發瓶頸，最能看出跨 kernel/協定的效能差距。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q10

Q7: 為何跨 OS kernel 會造成大幅 I/O 延遲？
- A簡: 因需協定轉譯、權限/事件映射、上下文切換與同步成本。
- A詳: 技術原理說明：跨 kernel 操作涉及多層封包、路徑管理與抽象轉譯。關鍵步驟：9P 來回、DrvFS 映射、vhdx 虛擬化、記憶體屏障。核心組件：9P 堆疊、DrvFS、Hyper-V。延遲累積使小 IO 成本高，建立策略將重 IO 留在單一 kernel。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q4, B-Q5

Q8: mklink 如何兼顧習慣路徑與 WSL 效能？
- A簡: 用 Windows 符號連結指向 WSL 目錄，工具照舊用 C: 路徑，資料實際在 WSL。
- A詳: 技術原理說明：建立 Windows 端符號連結，掛到 \\wsl$ 目標。關鍵步驟：mklink /d \\wsl$\distro\path C:\path。核心組件：Windows 連結點、WSL 檔案分享。這保留你的工具使用 C:\codes 工作流，但 IO 實際在 EXT4，需留意備份與跨端大 IO。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, D-Q7

Q9: VS Code Remote 架構如何設計？
- A簡: 前端本地 VS Code，後端 VS Code Server 在 WSL；通道傳指令與結果。
- A詳: 技術原理說明：VS Code 啟動遠端伺服（WSL/容器/SSH），UI 僅處理互動。關鍵步驟：安裝/更新 server、建立隧道、同步擴充。核心組件：VS Code Server、隧道擴充、LSP/Debug Adapter。能保留 Windows 體驗、以 WSL 原生 IO/工具鏈工作。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, C-Q4

Q10: code 指令在 WSL 啟動 VS Code Server 的流程？
- A簡: code 是 shell 腳本，安裝/更新/啟動 server，然後開啟本地 VS Code。
- A詳: 技術原理說明：/mnt/c/Program Files/.../code 腳本檢查/部署 vscode-server。關鍵步驟：檢測版本、安裝 server、建立連線、啟動 code.exe。核心組件：vscode-server、腳本橋接、通訊通道。首次啟動會看到 server 安裝訊息，完成即進 Remote WSL。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q4

Q11: 為什麼 WSL 不需安裝 Linux GPU 驅動？
- A簡: 因 GPU 虛擬化由 Windows 驅動實作，WSL 使用 /dev/dxg 與對接層即可。
- A詳: 技術原理說明：Windows 端 WDDM 驅動+Hyper-V 提供虛擬 GPU；WSL 僅需對應 dxg 驅動層。關鍵步驟：安裝最新 NVIDIA Windows Driver；WSL 透過 dxg 與對接層使用。核心組件：WDDM、dxg 驅動、DxCore。故只需在 WSL 安裝容器工具鏈，不安裝 Linux GPU 驅動。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q17, A-Q18, C-Q9

Q12: NVIDIA Container Toolkit 與 Docker runtime 如何協作？
- A簡: nvidia-ctk 設定 Docker runtime，容器得以存取 GPU 裝置與函式庫。
- A詳: 技術原理說明：nvidia-container-runtime 將 GPU 裝置與必要庫掛入容器。關鍵步驟：安裝 toolkit、設定 default-runtime 或 --gpus 參數。核心組件：nvidia-ctk、容器 runtime、libnvidia-*. 適當配置後，docker run --gpus=all 容器可用 GPU。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q5

Q13: CUDA 在 WSL 的運作堆疊是怎樣的？
- A簡: 以 DxCore/對接層映射至 /dev/dxg，讓 CUDA 呼叫可交由 Windows 驅動執行。
- A詳: 技術原理說明：CUDA API 透過 Microsoft 對接層與 DxCore 導向虛擬 GPU。關鍵步驟：應用→CUDA Runtime/Driver→對接層→dxg→WDDM。核心組件：CUDA、DxCore、dxg、WDDM。因而 nvidia-smi 於 WSL 可用，容器化 CUDA 工作負載亦可行。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, A-Q18, C-Q9

Q14: WSL 掛載實體/虛擬磁碟原理為何？
- A簡: 以 wsl --mount 掛實體分割，或以 vhdx 作為虛擬磁碟並格式化 EXT4。
- A詳: 技術原理說明：WSL 支援直接掛 /dev/sdX 分割與 vhdx 檔為區塊裝置。關鍵步驟：建立/格式化 EXT4、掛載到目錄、設定 fstab。核心組件：wsl.exe、內核驅動、EXT4 工具。直掛 EXT4 可最佳化性能；vhdx 方便管理/備份且效能接近。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q7, C-Q8, D-Q8

Q15: 為何 EXT4 直掛 WSL 能逼近/超越 NTFS 原生？
- A簡: 少協定轉換、無 NTFS 其他負擔，EXT4 更貼近 Linux I/O 模型。
- A詳: 技術原理說明：EXT4 直掛省去 DrvFS/9P，同時少了 NTFS ACL/security 特殊流程。關鍵步驟：就緒的 block I/O 直由 Linux 排程。核心組件：EXT4、I/O 排程、journaling。實測 MLC SSD 下，EXT4 直掛可達 100%+ 相對表現，適合重 IO 場景。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q20, B-Q14, C-Q7

Q16: 為何 DrvFS 效能近似「網路磁碟」？
- A簡: 因操作被包裝成跨層通訊，需編解碼、同步、切換，與遠端檔案類似。
- A詳: 技術原理說明：DrvFS 透過協定橋接送往 Windows，類似 SMB/NFS 概念。關鍵步驟：封包傳輸、權限映射、事件轉譯。核心組件：DrvFS、9P、Windows I/O。延遲固定成本使小 IO 非線性放大，故建議僅用於檔案搬運與輕量讀寫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, D-Q7

Q17: 為何 SSD 顆粒會影響 WSL EXT4/NTFS 相對表現？
- A簡: 隨機寫入耐性、控制器策略不同，小 IO 併發下影響更明顯。
- A詳: 技術原理說明：顆粒 P/E 壽命與寫入放大量、SLC Cache 與 DRAM 缺失會在小 IO 暴露。關鍵步驟：測試以 iodepth/numjobs 模擬高併發。核心組件：NAND 顆粒、控制器、韌體策略。MLC 長期穩定性較佳，QLC/DRAMless 在此場景劣勢明顯。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21, C-Q7

Q18: WSL 執行 Windows .exe 的機制？
- A簡: 以 binfmt_misc 註冊 PE 簽頭，WSLInterop 導向 /init，再呼叫 Windows 執行。
- A詳: 技術原理說明：在 Linux 偵測到 PE magic（4d5a），觸發已註冊的處理器。關鍵步驟：binfmt_misc→/init→Host 端執行對應 .exe。核心組件：binfmt_misc、WSLInterop、/init。因而可在 bash 執行 explorer.exe、cmd.exe 等，與檔案總管整合。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, C-Q4

Q19: VS Code 的連接埠轉發如何工作？
- A簡: 由 VS Code Server 偵測遠端服務埠，透過隧道映射到本地，並輔以 UI 列示。
- A詳: 技術原理說明：Server 監視 listen 埠，通知客戶端建立轉發。關鍵步驟：辨識服務、建立本地→遠端通道、在 UI 顯示並可開瀏覽器。核心組件：VS Code Server、tunnel、端口轉發模組。適合容器/WSL 服務的本地預覽與除錯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q10

Q20: GitHub Pages/Jekyll 在 WSL 的運作重點？
- A簡: 優先放原始碼與建置在 WSL EXT4，避免 DrvFS，才能享受快速熱重載。
- A詳: 技術原理說明：Jekyll 會大量小檔存取與監控變更。關鍵步驟：原始碼置於 WSL、由 VS Code Remote 編輯、容器於 WSL 進行建置。核心組件：inotify、Jekyll、Docker。避開 DrvFS 可大幅縮短預覽延遲，提高開發迭代效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q5, D-Q2

Q21: Qdrant 容器啟動 IO 行為與瓶頸？
- A簡: 啟動需載入 collections 與索引，小檔隨機讀寫密集，對跨系統路徑敏感。
- A詳: 技術原理說明：Qdrant 啟動掃描/恢復集合資料，屬隨機小 IO 型態。關鍵步驟：讀元資料→恢復分片→載入索引→開服務。核心組件：RocksDB/檔案結構、Docker 卷。放在 WSL EXT4 啟動可由數十秒降至 1–2 秒，顯著改善體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q6

Q22: WSLg 圖形堆疊如何整合 Windows？
- A簡: 以 Wayland/X11 合作，視窗輸出到 Windows，支援剪貼簿與輸入整合。
- A詳: 技術原理說明：WSLg 提供合成器與轉譯層，將 Linux GUI 轉發至 Windows 顯示。關鍵步驟：啟動 GUI 應用→經 WSLg 顯示管線→Windows 視窗。核心組件：Wayland/X11、PulseAudio、RDP/顯示橋接。讓 Linux GUI 應用無縫融入 Windows 桌面。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16

---

### Q&A 類別 C: 實作應用類

Q1: 如何安裝與初始化 WSL（Ubuntu 24.04 LTS）？
- A簡: 以啟用 WSL 功能、安裝 Ubuntu 24.04、更新套件並設定使用者環境。
- A詳: 具體步驟：1) 以系統管理員啟用 WSL與虛擬化（wsl --install 或 Windows 功能）；2) Microsoft Store 安裝 Ubuntu 24.04；3) 初次啟動設定使用者；4) 更新 sudo apt update && apt upgrade；5) 安裝常用工具（git、curl、build-essential）。注意事項：BIOS 開啟虛擬化；磁碟空間足夠；定期備份。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q3

Q2: 如何用 mklink 將 WSL 目錄掛到 Windows 路徑？
- A簡: 在 Windows 建符號連結指向 \\wsl$，保留 C: 路徑工作流但資料留在 WSL。
- A詳: 步驟：1) 於 WSL 建 /opt/docker 等目錄；2) Windows 以系統管理員：mklink /d \\wsl$\ubuntu\opt\docker C:\CodeWork\docker；3) 在檔案總管/VS Code 使用 C:\CodeWork\docker。關鍵指令：mklink /d 來源 目標。注意：實體資料在 vhdx，請備份；跨端大量 IO 仍慢。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q7

Q3: 如何在 WSL 下以最佳 IO 方式部署 Qdrant？
- A簡: 將資料卷放 WSL EXT4 路徑，避免 DrvFS；以 docker compose 管理。
- A詳: 步驟：1) 在 WSL 建資料目錄：/opt/data/qdrant；2) docker run -v /opt/data/qdrant:/qdrant/storage -p 6333:6333 qdrant/qdrant；或使用 docker-compose；3) 觀察 logs，啟動載入 collections 應顯著變快。關鍵設定：卷在 WSL EXT4。注意：備份策略、監控磁碟空間。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, D-Q6

Q4: 如何設定 VS Code Remote WSL 工作區？
- A簡: 在 WSL 路徑執行 code .，自動安裝 VS Code Server 並進入 Remote 模式。
- A詳: 步驟：1) WSL 進入專案：cd /opt/projects/myrepo；2) 執行 code .；3) 首次會安裝/更新 VS Code Server；4) 左下角顯示 WSL-Ubuntu；5) 打開內建 Terminal 即為 bash。注意：擴充需安裝至「WSL：Ubuntu」；保證專案存在 WSL EXT4 以獲最佳 IO。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10

Q5: 如何在 WSL 下執行 GitHub Pages/Jekyll 預覽？
- A簡: 將站點放 WSL，使用容器或 bundler 執行 Jekyll，並用 VS Code 端口轉發預覽。
- A詳: 步驟（容器法）：1) 專案置於 /opt/docker/site；2) docker compose up -d 啟動 Jekyll；3) VS Code 看到埠轉發，點開瀏覽器。步驟（原生法）：1) 安裝 Ruby/bundler；2) bundle exec jekyll serve。注意：避免 DrvFS；若熱更新遲鈍，確認 inotify 生效與檔案在 WSL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q20, D-Q2

Q6: 如何在 WSL 安裝 fio 並進行一致的效能測試？
- A簡: apt 安裝 fio，使用固定參數測試 4K 隨機多併發，對比不同路徑。
- A詳: 步驟：1) sudo apt install fio；2) 建測試目錄（WSL/DrvFS/Windows）；3) fio --name=bench --size=16G --rw=randrw --bs=4k --numjobs=8 --iodepth=64 --ioengine=libaio --direct=1 --time_based --runtime=300；4) 記錄 MiB/s。注意：確保空間、避免其他負載干擾；對比路徑解讀差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q10

Q7: 如何在 WSL 掛載專用 SSD（實體 EXT4）？
- A簡: 用 wsl --mount 掛入實體磁碟，格式化 EXT4，掛到目錄供資料/卷使用。
- A詳: 步驟：1) 在 Windows 以 diskpart 找出磁碟；2) wsl --mount \\.\PHYSICALDRIVEn --partition X；3) 於 WSL：sudo mkfs.ext4 /dev/sdXN；4) sudo mkdir -p /mnt/data；5) sudo mount /dev/sdXN /mnt/data；6) 寫入 /etc/fstab 持久化。注意：資料將專供 WSL；小心誤格式化。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q14, A-Q20

Q8: 如何建立 vhdx 並以 EXT4 掛載至 WSL？
- A簡: 在 Windows 建立 vhdx，附加後於 WSL 格式化 EXT4，掛載並使用。
- A詳: 步驟：1) 用磁碟管理或 diskpart 建立固定大小 vhdx；2) 附加磁碟；3) WSL 內查得 /dev/sdX；4) sudo mkfs.ext4 /dev/sdX；5) sudo mount 至 /mnt/vhdx；6) 加入 /etc/fstab。注意：vhdx 易備份搬移；避免與系統繁忙磁碟共用以減少干擾。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q5, B-Q14

Q9: 如何安裝 NVIDIA Container Toolkit 並讓 Docker 使用 GPU？
- A簡: 僅需安裝新版 Windows NVIDIA 驅動，WSL 裝 toolkit，docker --gpus=all 即可。
- A詳: 步驟：1) Windows 安裝最新 NVIDIA Driver；2) WSL 依官方指引安裝 nvidia-container-toolkit；3) 設定 /etc/docker/daemon.json default-runtime 或於 run 用 --gpus=all；4) 以 nvidia-smi 驗證。注意：不在 WSL 裝 Linux GPU 驅動；Docker 重啟後設定生效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q13, D-Q5

Q10: 如何用 docker-compose 一鍵啟動 Ollama + Open WebUI？
- A簡: 撰寫 compose 檔定義 ollama 與 open-webui，映射 GPU、卷與埠位後啟動。
- A詳: 步驟：1) 建 docker-compose.yaml，services: ollama（--gpus=all, vol: ollama:/root/.ollama, 11434:11434）、open-webui（depends_on、環境變數指向 ollama）；2) docker compose up -d；3) 確認網頁可用。注意：卷與 compose 放 WSL EXT4；GPU 需要 toolkit 與 --gpus 參數。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, B-Q19

---

### Q&A 類別 D: 問題解決類

Q1: Docker volume IO 很慢怎麼辦？
- A簡: 將卷與資料移至 WSL EXT4（/opt/...），避免 DrvFS/9P；或掛載專用 EXT4 磁碟。
- A詳: 症狀：容器啟動/建置/資料庫操作極慢。可能原因：跨 kernel 路徑、DrvFS/9P 延遲。解決步驟：1) 把卷放 /opt/data（WSL）；2) 以 mklink 保留工作流；3) 進階：wsl --mount 掛 EXT4 實體或 vhdx。預防：重 IO 一律置於 WSL EXT4；DrvFS 僅作輕量存取。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q4, B-Q5

Q2: Jekyll/Pages 熱更新不起作用或很慢？
- A簡: 檔案在 DrvFS 時 inotify 無法映射，改放 WSL EXT4 並以容器或原生執行。
- A詳: 症狀：修改檔案無即時重建，或延遲大。原因：FileSystemWatcher↔inotify 無法映射。解決：1) 專案移至 /opt/site；2) 在 WSL 內執行 jekyll 或容器；3) VS Code Remote 編輯；4) 必要時改事件為輪詢參數。預防：避免 NTFS 作為開發時的站點目錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q20, A-Q14, C-Q5

Q3: VS Code 無法連接 WSL 或 code . 失敗？
- A簡: 檢查 VS Code Server 安裝、WSL 版本、路徑與權限，重啟 WSL/VS Code。
- A詳: 症狀：code . 無反應或錯誤。原因：server 版本不符、WSL 未啟動、網路政策。步驟：1) 重啟 WSL：wsl --shutdown；2) 重啟 VS Code；3) 檢查 Remote-WSL 擴充；4) VS Code 底部狀態列檢查；5) 清除 server 緩存重裝。預防：保持 VS Code/擴充同步更新。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q4

Q4: 在 WSL 執行 nvidia-smi 找不到裝置？
- A簡: 確認 Windows NVIDIA 驅動版本、WSL GPU 支援開啟、重啟 WSL/系統。
- A詳: 症狀：nvidia-smi 無法列出 GPU。原因：Windows 驅動過舊或未安裝、WSL 尚未偵測到 /dev/dxg。步驟：1) 更新至最新 Windows Driver；2) wsl --shutdown；3) 重啟 Windows；4) 再測試 nvidia-smi。預防：定期維護驅動；避免在 WSL 安裝 Linux GPU 驅動。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q9

Q5: docker --gpus=all 看不到 GPU？
- A簡: 安裝 NVIDIA Container Toolkit，設定 runtime，並以正確參數啟動容器。
- A詳: 症狀：容器內 nvidia-smi 無結果。原因：缺 toolkit 或 runtime 未設。步驟：1) 在 WSL 安裝 nvidia-container-toolkit；2) 設定 /etc/docker/daemon.json 的 default-runtime；3) 重啟 Docker；4) docker run --gpus=all 測試。預防：文件化安裝步驟；升級後重驗設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q9

Q6: Qdrant 啟動卡在 Loading collection 很久？
- A簡: 把資料卷移至 WSL EXT4，降低隨機 IO 延遲，啟動時間可大幅縮短。
- A詳: 症狀：容器日誌停在 Recovering/Loading collection。原因：卷在 NTFS/DrvFS，隨機 IO 處理慢。步驟：1) 將 /qdrant/storage 映射至 /opt/data/qdrant（WSL）；2) 重建容器；3) 觀察時間差。預防：資料庫/向量庫一律放 WSL 卷。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q21

Q7: DrvFS 存取導致高 CPU 與延遲如何處理？
- A簡: 減少跨端頻繁小 IO，改以 WSL 卷執行；DrvFS 僅作搬運與偶爾存取。
- A詳: 症狀：編譯/建置或容器運作時 CPU 飆高、延遲長。原因：DrvFS/9P 協定開銷疊加。步驟：1) 移動熱路徑至 WSL；2) 用 mklink 維持路徑一致；3) 以檔案同步取代即時跨端存取。預防：架構設計時將 DrvFS 定位為「網路磁碟」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, C-Q2

Q8: ext4.vhdx 損毀或資料遺失怎麼辦？
- A簡: 以備份策略與獨立 vhdx 降風險，必要時嘗試掛載救援或重建發行版。
- A詳: 症狀：WSL 無法啟動或目錄空白。原因：vhdx 損毀、磁碟異常。步驟：1) 事前：用獨立 vhdx 存關鍵資料並定期備份；2) 事後：嘗試以 Windows 掛載 vhdx、用 Linux 工具檢查/修復；3) 無法修復則重建 WSL。預防：版本管控（git）、離線備份與快照。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q5, C-Q8

Q9: 跨系統檔案權限/屬性錯亂如何處理？
- A簡: 認知 NTFS ACL 與 Linux 權限不同，跨端時以最小集屬性與工具處理。
- A詳: 症狀：權限異常、不可執行或監控失效。原因：ACL 與 chmod 模型差異、Streams 等特性。步驟：1) 在 WSL 卷內維護權限；2) 避免用 NTFS Streams；3) 需要跨端時以壓縮包/工具遷移。預防：對權限敏感專案避免放 NTFS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q15

Q10: fio 測試結果波動大如何校驗？
- A簡: 關閉背景負載、固定參數、重複多次、分別測試多路徑對比平均。
- A詳: 症狀：同參數結果差異大。原因：系統背景 I/O、快取與熱度、共用磁碟干擾。步驟：1) wsl --shutdown 後重啟；2) 避免與系統磁碟共用；3) 固定測參；4) 多輪測試取中位數。預防：專用 SSD、分離 vhdx、獨立分割。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q6

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 WSL（Windows Subsystem for Linux）？
    - A-Q2: WSL1 與 WSL2 的差異是什麼？
    - A-Q6: 為什麼要在 Windows 上建立 Linux 原生開發環境？
    - A-Q7: 為什麼拋開 Docker Desktop for Windows？
    - A-Q10: 為什麼把資料移到 WSL rootfs（EXT4）會加速？
    - A-Q11: 為什麼 VS Code Remote Development 能解決跨系統協作？
    - A-Q12: 什麼是 VS Code Server？
    - A-Q22: 為何把 DrvFS 視為「網路磁碟」？
    - B-Q1: WSL 的四種檔案存取路徑如何運作？
    - B-Q2: Windows→Windows（NTFS 原生）流程與代表意義？
    - B-Q5: WSL→Windows（DrvFS）流程與限制？
    - C-Q1: 如何安裝與初始化 WSL（Ubuntu 24.04 LTS）？
    - C-Q4: 如何設定 VS Code Remote WSL 工作區？
    - D-Q1: Docker volume IO 很慢怎麼辦？
    - D-Q3: VS Code 無法連接 WSL 或 code . 失敗？

- 中級者：建議學習哪 20 題
    - A-Q3: 什麼是 DrvFS？
    - A-Q4: 什麼是 9P 協定（9p protocol）？
    - A-Q14: FileSystemWatcher 與 inotify 有何差異？
    - B-Q3: WSL→WSL（EXT4.vhdx）流程與 Hyper-V 影響？
    - B-Q4: Windows→WSL（9P+虛擬）背後機制？
    - B-Q6: fio 測試參數如何設計？為何重點在 iodepth/numjobs/bs？
    - B-Q7: 為何跨 OS kernel 會造成大幅 I/O 延遲？
    - B-Q8: mklink 如何兼顧習慣路徑與 WSL 效能？
    - B-Q9: VS Code Remote 架構如何設計？
    - B-Q10: code 指令在 WSL 啟動 VS Code Server 的流程？
    - B-Q20: GitHub Pages/Jekyll 在 WSL 的運作重點？
    - B-Q21: Qdrant 容器啟動 IO 行為與瓶頸？
    - C-Q2: 如何用 mklink 將 WSL 目錄掛到 Windows 路徑？
    - C-Q3: 如何在 WSL 下以最佳 IO 方式部署 Qdrant？
    - C-Q5: 如何在 WSL 下執行 GitHub Pages/Jekyll 預覽？
    - C-Q6: 如何在 WSL 安裝 fio 並進行一致的效能測試？
    - D-Q2: Jekyll/Pages 熱更新不起作用或很慢？
    - D-Q6: Qdrant 啟動卡在 Loading collection 很久？
    - D-Q7: DrvFS 存取導致高 CPU 與延遲如何處理？
    - D-Q10: fio 測試結果波動大如何校驗？

- 高級者：建議關注哪 15 題
    - A-Q13: 什麼是 binfmt_misc 與 WSLInterop？
    - A-Q17: WSL 的 GPU 虛擬化是什麼？
    - A-Q18: /dev/dxg 代表什麼？
    - A-Q19: 什麼是 DirectML？與 WSL 的關係？
    - A-Q20: 為何建議給 WSL 專用 SSD 並使用 EXT4？
    - A-Q21: SSD 顆粒（MLC/TLC/QLC）對 WSL 效能影響？
    - B-Q11: 為什麼 WSL 不需安裝 Linux GPU 驅動？
    - B-Q12: NVIDIA Container Toolkit 與 Docker runtime 如何協作？
    - B-Q13: CUDA 在 WSL 的運作堆疊是怎樣的？
    - B-Q14: WSL 掛載實體/虛擬磁碟原理為何？
    - B-Q15: 為何 EXT4 直掛 WSL 能逼近/超越 NTFS 原生？
    - C-Q7: 如何在 WSL 掛載專用 SSD（實體 EXT4）？
    - C-Q8: 如何建立 vhdx 並以 EXT4 掛載至 WSL？
    - C-Q9: 如何安裝 NVIDIA Container Toolkit 並讓 Docker 使用 GPU？
    - C-Q10: 如何用 docker-compose 一鍵啟動 Ollama + Open WebUI？
