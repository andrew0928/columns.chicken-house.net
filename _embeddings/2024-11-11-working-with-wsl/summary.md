# 用 WSL + VSCode 重新打造 Linux 開發環境

## 摘要提示
- WSL2架構: 微軟以輕量 VM + 9P/DrvFS 技術，實現 Windows / Linux 檔案與行程互通。
- Docker IO效能: Volume 掛在 NTFS 會掉到原生 1/35；改存 WSL ext4 可回到 1/3 以上。
- 磁碟最佳化: 直掛實體 SSD 或獨立 .vhdx，可把效能提升至與 Windows 原生持平甚至超越。
- VSCode Remote: 透過 vscode-server 與 binfmt_misc，UI 在 Windows、編輯/編譯在 Linux，實現零縫切換。
- GPU 虛擬化: 依賴新版 WDDM 驅動與 /dev/dxg，WSL 可直接使用 CUDA、DirectML。
- Ollama 範例: 三步驟安裝 nvidia-ctk，即能在容器中跑 Llama3 並調用 RTX4060Ti。
- 開發迴路: Git 操作、Jekyll build、Qdrant 測試全移入 WSL，Windows 端只負責 UI。
- 黑科技細節: Windows 可在 Bash 直接執行 .exe，WSLg 亦支援 Linux GUI 顯示於桌面。
- SSD選擇: 顆粒與獨立掛載比介面更影響效能；MLC Gen3 竟能勝過 TLC Gen4。
- 結論反思: “Microsoft Love Linux” 十年後，Windows 已可成為高效率 Linux 開發主機。

## 全文重點
作者因需在本機執行 AI 與容器化工作，決定把 Windows 桌機全面轉向「WSL2 + VSCode Remote」的 Linux 開發模式。首先利用 fio 對四種磁碟路徑（Win→Win、WSL→WSL、Win→WSL、WSL→Win）做隨機 4K 測試，證實跨核心的 9P/DrvFS 使效能掉到 3%‒6%，而放在 WSL ext4 僅損 1/3。將 Qdrant volume 由 /mnt/c 改到 /opt/docker 後，啟動時間從 38 秒降至 1.5 秒。進一步實測四種 SSD（TLC Gen4、MLC Gen3、QLC Gen3、MLC SATA）並比較「原生 NTFS」「DrvFS」「實體 EXT4」「vhdx EXT4」，發現實體 EXT4 或獨立 vhdx 均可達原生 100% 以上，唯 QLC 效率顯著較差。

在工具整合上，VSCode 透過 Remote-WSL 模式，將 vscode-server 部署於 Linux；使用者於 Windows 按 `code .` 即可開 IDE、開 Bash、跑 docker compose，同時保有 Windows Explorer、Notepad 等 .exe 可在 Bash 直接呼叫的便利。GUI 程式亦能借 WSLg 顯示於桌面。

GPU 部分，安裝新版 NVIDIA Windows 驅動後，WSL 內建 /dev/dxg 便能被 nvidia-container-toolkit 偵測，`docker run --gpus=all` 即可在容器內使用 CUDA。作者以 Ollama+Open-WebUI 測試 Llama3 推論，RTX4060Ti 顯示正常負載。透過這些調整，他成功打造出「Linux 為核心、Windows 為介面」的長效開發環境，並體會到微軟十年來對開源與跨平台生態的深度投入。

## 段落重點
### 1. 替換工作環境的動機
作者因 Docker Desktop 授權、NTFS Volume 慢、GPU 難用等痛點，決定重灌 Windows 11 24H2、改用 WSL2，並將 VSCode、git、dotnet 等整合進 Linux，以獲得單一平台的一致體驗與高效能。

### 2. 案例：容器化的向量資料庫 Qdrant
以 Qdrant 4 萬筆資料為例，啟動容器需大量隨機 IO。若 volume 掛在 /mnt/c（WSL→Win），啟動 38 秒；改至 WSL ext4 僅 1.5 秒，證實 IO 瓶頸在 DrvFS/9P。作者並用 fio 測得 Win→Win 576 MB/s、WSL→WSL 209 MB/s、跨核心僅 16.5 MB/s。解法是在 Windows 以 mklink 把 \\wsl$ 目錄映到 C:\Path，維持操作便利又保效能。

### 2-1 WSL 磁碟效能 Benchmark
詳細解釋四種路徑對應的轉換層：Hyper-V、9P、DrvFS。每多一層效能驟降，理想是 WSL→WSL 或實體 disk 直掛。引用日文測試與自測數據推估各轉換約耗 60%‒90% 帶寬。

### 2-6 WSL 掛載額外 Disk
在四顆 SSD 上比較 NTFS/DrvFS/實體 EXT4/vhdx EXT4。結果顆粒與獨立掛載決定上限：MLC Gen3 實體 EXT4 可達 780 MB/s，甚至超原生；QLC 表現最差。建議為 WSL 配專用 SSD、採 EXT4，DrvFS 僅作檔案交換。

### 3. GitHub Pages 與 VSCode
開發場景需雙向高效 IO。VSCode Remote-WSL 讓 UI 仍在 Windows，但編輯/編譯/執行都在 Linux，避免跨核心開銷。`code .` 會自動部署 vscode-server；terminal 直出 bash；開檔、啟容器、預覽網站皆流暢。Markdown 圖片貼上、Port 轉發等功能也完整支援。

### 3-1 在 WSL 執行 Windows 程式
WSL 透過 binfmt_misc 註冊 PE magic，將 .exe 呼叫轉交 /init 實體啟動。因而可在 bash 直接執行 cmd.exe、explorer.exe，達到雙向互操作。

### 3-2 VSCode Remote 內部原理
VSCode 分為前端 UI 與後端 server。Remote-WSL 於 Linux 啟動 vscode-server，透過隧道傳 JSON-RPC，同步檔案、執行 debug、container 等，全程不需本機存原始碼。

### 4. GPU（CUDA）Application
WSL 2 內建 GPU 虛擬化 /dev/dxg，只需 Windows 端安裝新版 NVIDIA Driver，並在 WSL 裝 nvidia-container-toolkit。Ollama Docker 例子顯示 `nvidia-smi` 正常，`docker run --gpus=all` 即可調用 GPU 推理。架構上 DirectX/DxCore 為基礎，CUDA、OpenCL、OpenGL 皆經該層轉譯，WSLg 亦支援 GUI 顯示。

### 4-2 GPU 虛擬化冷知識
微軟於 Build 2020 公布 DirectX for Linux；關鍵在 host WDDM 2.9+ 與 guest dxgkrnl。CUDA 等運算庫透過 DxCore 達成相容。Linux 驅動僅需微軟提供的 dxg driver，不再安裝原廠驅動。

### 5. 心得
十年來微軟由 “Love Linux” 口號落實到 WSL、VSCode、.NET 跨平台。作者認為 Windows 已可成為優秀 Linux 開發主機；憑數據與實戰證明，只要擺對磁碟、善用 Remote-WSL 與 GPU 虛擬化，就能兼顧效率與體驗。