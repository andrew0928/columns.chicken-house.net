# 用 WSL + VSCode 重新打造 Linux 開發環境

## 摘要提示
- 動機與目標: 以 WSL 取代 Docker Desktop，建立以 Linux 為主、與 Windows 無縫整合的長期開發環境，並支援 GPU/CUDA。
- IO 效能關鍵: 跨 OS 檔案系統（DrvFS/9P/Hyper-V）會造成嚴重效能損耗，是 Docker volume 慢的重要原因。
- 基準測試發現: Windows→Windows 576MB/s 對比 Windows↔WSL 最低僅 16.5MB/s，跨層轉譯造成最高可達 35x 落差。
- 實戰成效: 將 volumes 移至 WSL ext4 後，Qdrant 啟動時間從 38.4s 降至 1.5s（25x）；Jekyll 預覽 18x 加速。
- 目錄佈局策略: 在 WSL 中使用 /opt/docker 存放資料，Windows 端以 mklink 掛載，維持工作流程與體感。
- 專用磁碟最佳化: 配置 WSL 專用 SSD 並採 EXT4，效能可達或超越 Windows+NTFS；避免以 DrvFS 當本機盤使用。
- VSCode 整合: 以 Remote WSL/VS Code Server 實現前後端分離，UI 在 Windows、開發/編譯/檔案在 Linux，近乎原生體驗。
- GPU 支援: 僅需安裝 Windows NVIDIA 驅動；WSL 內裝 NVIDIA Container Toolkit，Docker 加 --gpus=all 即可使用 CUDA。
- 架構冷知識: WSL 透過 binfmt_misc 互通 .exe；檔案跨系統用 9P/DrvFS；GPU 虛擬化以 /dev/dxg 與 DxCore 打通。
- 實務建議: 以 EXT4 儲存熱 IO，將 DrvFS 視為「網路磁碟」；SSD 顆粒優先於介面（MLC>TLC>QLC），專用磁碟最理想。

## 全文重點
作者因需在本機穩定執行 Linux 為主的容器與 AI 工作負載（含 CUDA/GPU），決定捨棄 Docker Desktop，全面切換至 WSL + VSCode 的開發環境。重建過程中，釐清 WSL 在檔案系統與虛擬化上的本質：應用程式在不同 kernel（Windows/WSL2）間跨界存取時，會經過 DrvFS、9P 協定與 Hyper-V 虛擬磁碟（ext4.vhdx）等轉譯層，這些層次將導致極可觀的 IO 損耗，成為 Docker volume 掛載於 Windows 路徑時效能低落的主因。

以 fio 在相同硬體進行 4K 隨機讀寫基準測試，Windows→Windows 達 576MB/s；WSL→WSL（ext4.vhdx）約 209MB/s；WSL→Windows（DrvFS）約 37.5MB/s；Windows→WSL（9P+Hyper-V）僅 16.5MB/s。跨 OS 存取的兩種情境最慢，與理想對照組相比落至 6.5% 與 2.86%。對應到實務案例，將 Qdrant 的資料與 Jekyll 的專案搬到 WSL rootfs（ext4）後，Qdrant 啟動從 38.4 秒降至 1.5 秒、Jekyll 預覽建置時間也大幅縮短，顯示只要把熱 IO 的資料避開跨 kernel，就能獲得戲劇性改善。

為兼顧 Windows 使用體驗與 WSL 效能，作者在 WSL 以 /opt/docker 作為資料主目錄，Windows 以 mklink 將其掛到慣用路徑，維持操作便利；同時提醒需定期備份 ext4.vhdx。進一步，WSL 現已支援掛載實體或虛擬磁碟：將獨立 SSD 直接格式化為 EXT4 並交由 WSL 掛載，可避開 Hyper-V 虛擬硬碟開銷，效能可達甚至超越 Windows+NTFS。測試多顆 SSD 顯示：顆粒與是否共用系統盤影響甚大，MLC 在高負載隨機 IO 下常優於新款 TLC/QLC；DrvFS 應當作網路磁碟看待，不宜承載重 IO。

在工具整合層面，VSCode 的 Remote Development（WSL）成為關鍵：透過 VS Code Server，UI 留在 Windows 而所有檔案、編譯、除錯、Terminal 都在 WSL 執行，避免跨 OS 路徑與二進位相容性問題，體驗接近本機原生。於 WSL 中執行 code . 時，script 會布署/啟動 VS Code Server 並連回 Windows 客戶端，最終在 VSCode 內直接以 Linux 路徑開檔、在 bash 內啟動 Docker、轉發埠並預覽網站，達到「Windows 外觀、Linux 實核」的日常開發流程。

對於 GPU/CUDA，WSL 的虛擬化堆疊已成熟：只需在 Windows 安裝 NVIDIA Driver，WSL 內安裝 NVIDIA Container Toolkit 並設定 Docker runtime，容器以 --gpus=all 啟動即可。nvidia-smi 可在 WSL 直接查看 GPU 狀態。其底層由 /dev/dxg 與 DxCore/D3D12 以及 DirectML/mesa 之類堆疊打通，CUDA 亦透過相容層實現於 WSL；因此不要在 WSL 裝 Linux 顯卡驅動，重點在 Windows 端的 WDDM 與對應堆疊。最後，WSL 也支援 Linux GUI 應用程式（WSLg）與 Windows 桌面整合，但本文主焦在 CLI/容器/開發流程。

綜合建議：將資料與容器 volumes 儘量放在 WSL EXT4；避免以 DrvFS 作為重 IO 路徑；必要時提供 WSL 專用 SSD，顆粒優先於介面（MLC/TLC>QLC）；以 VSCode Remote WSL 作為主要 IDE 模式；GPU 以 Windows Driver + NVIDIA Container Toolkit 啟用即可。整體而言，WSL2 生態已足以支撐 Windows 作為 Linux 開發主力環境，效能、整合與體驗兼具。

## 段落重點
### 1. 替換工作環境的動機
作者因需在本機執行 AI/LLM 與容器化服務，包含 CUDA/GPU 與 Docker-based 的工作流程，決定拋棄 Docker Desktop，全面將開發環境轉向 WSL + VSCode。核心動機包含：避開 Docker Desktop 授權與冗餘、解決 Docker 在 Windows volume 掛載的 IO 瓶頸、使容器可直接使用 GPU、建立可長期維護的 Linux 為主工作環境並與 Windows 無縫整合。過往在本機用 Qdrant、Jekyll 等場景遭遇嚴重效能瓶頸（啟動/建置耗時），促成此次徹底翻修；最終升級到 Win11 24H2、Ubuntu 24.04、增添 RTX4060Ti 與更高速 SSD，並將 VSCode 操作、git、dotnet 等日常工具完整融入 WSL 生態。

### 2, 案例: 容器化的向量資料庫 - Qdrant
以 Qdrant 為例，揭露 Docker volume 慢的本質：在 Windows 執行容器並掛載 Windows 路徑，容器內的 IO 其實走 WSL DrvFS/9P 等跨層轉譯，造成極大延遲與吞吐下降。作者整理 WSL 檔案系統路徑的四種組合（Win→Win、WSL→WSL、Win→WSL、WSL→Win），指出只要跨 OS/kernal，就會經過 DrvFS 或 9P 或 Hyper-V 虛擬磁碟層，導致倍數耗損。實際從 Qdrant logs 對比可見：資料放在 /mnt/c 下（WSL→Windows）啟動要 38.4s；改放於 WSL rootfs（WSL→WSL）則 1.5s。策略是：將熱 IO 移至 WSL EXT4，Windows 端以 mklink 掛載維持操作習慣；提醒備份 vhdx 與跨端重 IO 仍會慢。另補充 Windows/Linux 權限模型與 NTFS stream 與 Linux 不對應的知識點，提醒跨系統時會遇到特性流失與怪異現象。

### 2-1, WSL 磁碟效能 Benchmark
使用 fio（一致參數、4K 隨機讀寫、高負載）對四種情境測試：Win→Win 約 576MB/s；WSL→WSL 約 209MB/s；Win→WSL 約 16.5MB/s；WSL→Win 約 37.5MB/s。結論：原生檔案系統讀寫最佳；WSL 虛擬化（Hyper-V vhdx）有損耗；跨 OS 的 9P/DrvFS 開銷極大，不適合高性能場景。據此明確指示：熱路徑應避免跨層。

### 2-2, 測試數據的解讀, 與 WSL 架構
對照 WSL 架構（9P、DrvFS、Hyper-V），將四情境映射至實際轉譯層，並藉由相對比值估算各層耗損（Hyper-V 約剩 36%、9P 約剩 6.5%，疊加接近 2.34%）驗證模型合理。指出可透過直接掛載實體磁碟/分割區給 WSL（避免 vhdx）以恢復效能，官方文檔亦有教學。理解結構後，即可因地制宜避開性能陷阱。

### 2-3, 實際部署 Qdrant 測試資料庫
展示 Qdrant 搭配 Microsoft Kernel Memory 的 RAG 堆疊，使用約 4 萬筆資料集實測：當資料位於 /mnt/c（WSL→Windows）啟動耗時 38.4s，花時間在 collection 載入；改為 WSL rootfs（WSL→WSL）僅 1.5s，效能提升 25 倍。由此不再花力氣測 DB 調優，因瓶頸在檔案路徑而非 Qdrant 本身。

### 2-4, 在 windows 下掛載 wsl 的資料夾
以 mklink 將 WSL 中 /opt/docker 掛到 Windows 路徑（如 C:\CodeWork\docker），兼顧操作體驗與效能。提醒：實體檔在 ext4.vhdx，需備份；同目錄若從 Windows 端做大量 IO，仍會遭遇跨層效能瓶頸（Win→WSL 最慢），需衡量使用情境。此法適合「Linux 熱路徑、Windows 偶爾存取」的日常工作流。

### 2-5, 其他 file system 議題
補充 Windows 與 Linux 權限與屬性的根本差異（ACL/RBAC vs. owner/group/chmod），DrvFS 難以等價轉譯；另外 NTFS Alternate Data Streams（多串流）在 Linux 不支援，跨系統時可能看到怪檔名。建議理解差異並忽略不必要雜訊。

### 2-6, WSL 掛載額外的 Disk
新增測試顯示：給 WSL 專用 SSD 並採 EXT4，可大幅提升效能；某些場景甚至優於 Windows+NTFS。比較四配置：Windows 原生 NTFS、WSL 透過 DrvFS 讀 NTFS、WSL 直接掛實體 EXT4、WSL 掛 vhdx 的 EXT4。結果：DrvFS 仍慢（約 35MB/s 級別）；WSL 實體 EXT4 常可達甚至超越 Windows NTFS；WSL vhdx EXT4 視顆粒/負載也能接近或追平。顆粒影響甚於介面，MLC 在高負載隨機 IO 下普遍優於 TLC/QLC；共用系統盤干擾大。建議：熱 IO 優先 WSL 專用 SSD + EXT4；DrvFS 當「網路磁碟」使用；避免低階 QLC/DRAMless 作為工作盤。

### 3, GitHub Pages with Visual Studio Code
開發情境需同時兼顧 Windows 工具鏈（git/IDE）與 Linux 執行/測試環境，單純移動資料夾不足以解決「雙端都要快」的需求。解法是將 IDE 本體前後端分離：UI 留在 Windows、編譯/檔案/執行留在 Linux。VSCode Remote Development（WSL）正好精準滿足此模式，達到無縫體驗與原生效能，並解決檔案監聽（inotify vs FileSystemWatcher）失效與跨路徑相容性等問題。

### 3-1, 在 WSL 下執行 Windows CLI / Application
WSL 支援在 Linux 直接呼叫 Windows 可執行檔（需 .exe），如 explorer.exe 打開 WSL 目錄、cmd.exe 執行命令。原理為在 Linux 的 binfmt_misc 註冊 Windows PE handler（WSLInterop），遇到 PE 格式即交由 /init 啟動 host Windows 的對應程式。此互通性讓工具鏈更彈性，但效能敏感工作仍應留在對的側（Linux/EXT4）。

### 3-2, Visual Studio Code: Remote Development
VS Code Server 在 WSL 端負責檔案、terminal、執行與除錯，Windows 端 VSCode 僅為 UI。於 WSL 執行 code . 時，script 會自動安裝/更新/啟動 VS Code Server，並將工作目錄以 WSL 路徑載入。實務上可在 VSCode 內直接用 Linux 路徑開檔、在 bash 下 docker compose up、埠轉發、瀏覽預覽。此模式同時滿足「Linux 原生效能」與「Windows 介面整合」。另提及 VSCode 內建貼圖到 Markdown 的便利，WSL Remote 下體驗完整。

### 4, GPU (CUDA) Application
在 WSL 使用 GPU 其實極為簡單：Windows 安裝 NVIDIA Driver 即具備 GPU 虛擬化基礎；WSL 內安裝 NVIDIA Container Toolkit 並設定 Docker runtime；啟動容器時加 --gpus=all 即可。nvidia-smi 可於 WSL 查看 GPU 狀態。作者以 Ollama 測試，Llama3.2 回應流暢，Task Manager 可見 GPU 負載；再以 docker-compose 快速整合 Open WebUI，輕鬆搭建本地 LLM 介面。

### 4-1, Ollama Docker 的設定步驟
步驟摘要：在 Windows 裝對版本的 NVIDIA Driver；WSL 端安裝 NVIDIA Container Toolkit（不需裝 Linux 顯卡驅動）；Docker 設定使用 nvidia runtime；以 --gpus=all 啟動容器。實測一鍵即用，體驗順暢。

### 4-2, WSL + GPU 的冷知識
WSL GPU 的關鍵在虛擬化：Windows 端 WDDM 2.9+ 驅動啟用 GPU virtualization，WSL 內以 /dev/dxg 對應；Microsoft 提供 DxCore/D3D12 在 Linux 的相容層，DirectML/mesa/OpenGL/OpenCL/CUDA 透過對應堆疊打通。故應「只」在 Windows 安裝 GPU 驅動，WSL 端不需裝 Linux 驅動。WSLg 亦使 Linux GUI app 無縫整合至 Windows 桌面，雖本文未深用，但代表生態整體成熟。

### 5, 心得
過去十年間，Microsoft 從「Microsoft loves Linux」到今日 WSL/VSCode/容器/GPU 虛擬化的深度落地，已讓 Windows 得以成為可用、好用、效能足夠的 Linux 開發主機。雖體驗未必等同 macOS，但以 WSL2 + VSCode Remote + 正確的檔案/磁碟布局與 GPU 堆疊配置，已能滿足作者長期日常開發與 AI 應用需求，並兼顧效率、穩定與整合度。

## 資訊整理

### 知識架構圖
1. 前置知識
- 作業系統與檔案系統基礎：Windows/NTFS、Linux/EXT4、虛擬硬碟 VHDX
- 虛擬化與 WSL2 架構：Hyper-V、9P/DrvFS、WSLg 基本概念
- Docker 與容器基本功：volumes、bind mount、GPU runtime（NVIDIA Container Toolkit）
- VS Code Remote 觀念：VS Code Server、遠端編輯/除錯、code 命令
- 基本硬體知識：SSD 顆粒（MLC/TLC/QLC）、PCIe 介面世代、GPU 驅動

2. 核心概念
- WSL2 檔案路徑的四種 IO 路徑與效能梯度：Windows→Windows（最佳）、WSL→WSL（中）、WSL↔Windows（差，經 9P/DrvFS）
- Volume 擺放位置決定效能：將資料放在 WSL EXT4 rootfs 或專用磁碟，避開 DrvFS/9P
- VS Code Remote in WSL：UI 在 Windows、編輯/編譯/除錯在 Linux（vscode-server）
- Windows↔WSL 可執行檔互通：binfmt_misc + /init 轉譯 PE（magic 4d5a）
- GPU 虛擬化於 WSL：/dev/dxg、安裝 Windows 驅動＋WSL 端 NVIDIA Container Toolkit，容器以 --gpus=all 使用

3. 技術依賴
- WSL2 基礎：Hyper-V 虛擬化、EXT4.vhdx、9P/DrvFS 檔案橋接
- VS Code Remote：vscode-server、Remote WSL 擴充、code 啟動腳本
- Docker + GPU：Windows NVIDIA Driver（WDDM 2.9+）、WSL 端 NVIDIA Container Toolkit（nvidia-ctk）、Docker runtime
- 檔案系統優化：EXT4（rootfs、實體掛載、VHDX）、mklink 便利存取
- GPU API 映射：DxCore/D3D12/DirectML 於 WSL、CUDA on WSL（透過 dxg 路徑）

4. 應用場景
- 本機向量資料庫/Qdrant、資料密集型容器：需要高 IO 的 volume
- 部落格/SSG（Jekyll, GitHub Pages）本地預覽：需要檔案監看與快速 rebuild
- LLM/Stable Diffusion 等 GPU 容器：Ollama、vLLM、Open-WebUI
- 跨 OS 開發：Windows 下 VS Code、Linux 端 build/測試/除錯一體化
- GUI Linux App on Windows：日常工具與展示（WSLg）

### 學習路徑建議
1. 入門者路徑
- 安裝 WSL2 與 Ubuntu 發行版；更新至 Windows 11 24H2
- 裝好 VS Code 與 Remote WSL 擴充；在 WSL 中用 code . 開啟專案
- 在 WSL 安裝 Docker；練習 docker run/compose 與基本 volume 掛載
- 熟悉四種檔案路徑差異：/mnt/c、\\wsl$、~、rootfs 位置
- 以 mklink 建立常用目錄映射，維持原工作習慣

2. 進階者路徑
- 用 fio 跑簡單磁碟 benchmark，量化不同放置位置效能
- 調整 volume 佈局：將資料搬至 WSL rootfs（如 /opt/docker）或專用 EXT4 磁碟/VHDX
- 熟悉 VS Code Remote 端的 terminal、ports 轉發、擴充套件在 WSL 的安裝
- 研究 Windows↔WSL 可執行檔互通（binfmt_misc），靈活混用工具
- 處理跨 OS 權限/檔案監看問題（inotify vs FileSystemWatcher）

3. 實戰路徑
- 以 Qdrant 為例：將資料目錄放在 WSL EXT4，驗證啟動/查詢效能差異
- 建立 Jekyll/GitHub Pages 的 dev 容器流程：變更即時預覽、port 轉發
- 打通 GPU：裝 Windows NVIDIA 驅動、WSL 端 NVIDIA Container Toolkit、docker --gpus=all 跑 Ollama + Open-WebUI
- 若長期重度使用：在獨立 SSD 上建立 EXT4 分割或獨立 VHDX 掛載 WSL
- 制定備份策略：ext4.vhdx 與專用磁碟之檔案備援

### 關鍵要點清單
- WSL 四種 IO 路徑與效能梯度: Windows→Windows最佳、WSL→WSL次佳、跨 OS（9P/DrvFS）最差，決定體感性能 (優先級: 高)
- 9P/DrvFS 成本: 跨 OS 檔案存取經 9P/DrvFS 有高延遲，對 DB/大量小檔案極不友善 (優先級: 高)
- Volume 擺放策略: 將容器資料放在 WSL EXT4（如 /opt/docker）可避開跨層轉譯，常見可達數十倍改善 (優先級: 高)
- mklink 便利性佈局: 用 mklink 讓 Windows 工作流程維持原路徑，實體檔放在 WSL rootfs (優先級: 中)
- WSL 獨立磁碟/分割/VHDX: 將 EXT4 置於專用磁碟或獨立 VHDX，可顯著接近/優於原生效能 (優先級: 高)
- SSD 顆粒選型: MLC>高階TLC>>QLC，重 IO 場景中新不一定比舊快，顆粒影響大於介面 (優先級: 中)
- 把 DrvFS 當網路磁碟: DrvFS 僅適合搬檔與輕量操作，不適合高 IO 工作負載 (優先級: 高)
- 檔案監看差異: NTFS FileSystemWatcher 與 Linux inotify 不等價，跨 OS 掛載常導致監看失效或退化為 polling (優先級: 中)
- NTFS 權限/Streams 差異: ACL/RBAC 與 chmod 模型不同、NTFS streams 對 Linux 非原生，跨系統需忽略或特別處理 (優先級: 低)
- VS Code Remote 架構: 本機 UI + 遠端 vscode-server 處理編輯/編譯/除錯，獲得近本機體驗 (優先級: 高)
- code 啟動流程: WSL 下的 code 腳本會自動安裝/啟動 vscode-server 並橋接到本機 VS Code (優先級: 中)
- Windows↔WSL 可執行互通: 透過 binfmt_misc 註冊（magic 4d5a）與 /init handler 在 WSL 執行 .exe (優先級: 低)
- WSL GPU 打通原則: 僅需安裝 Windows NVIDIA 驅動；WSL 端安裝 NVIDIA Container Toolkit，容器用 --gpus=all (優先級: 高)
- CUDA on WSL 概念: 透過 /dev/dxg 與 DxCore 堆疊映射，不需安裝 Linux 原生 GPU driver (優先級: 中)
- 典型實戰組合: Qdrant（高 IO）、Jekyll（快速預覽）、Ollama+Open-WebUI（GPU）在 WSL + VS Code 下高效整合 (優先級: 高)