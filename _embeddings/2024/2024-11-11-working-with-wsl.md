---
- source_file: /docs/_posts/2024/2024-11-11-working-with-wsl.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# 用 WSL + VSCode 重新打造 Linux 開發環境

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "用 WSL + VSCode 重新打造 Linux 開發環境"
categories: ["技術隨筆"]
tags: ["技術隨筆","VSCode","Jekyll","Docker","WSL"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-11-11-working-with-wsl/logo.jpg

# 自動識別關鍵字
primary-keywords:
  - WSL2
  - VS Code Remote Development
  - Docker IO Performance
  - GPU Virtualization / CUDA
  - Qdrant
  - GitHub Pages
secondary-keywords:
  - NTFS vs EXT4
  - DrvFS / 9P Protocol
  - Hyper-V
  - fio Benchmark
  - Ollama & Open-WebUI
  - NVIDIA Container Toolkit
  - DirectX / DirectML on Linux
  - SSD 顆粒 TLC・MLC・QLC
  - Dev Container / Remote-SSH
  - Windows 11 24H2

# 技術堆疊分析
tech_stack:
  languages:
    - Bash
    - PowerShell
    - YAML / Markdown
  frameworks:
    - Jekyll
    - .NET Core (build 環節)
  tools:
    - WSL2
    - Visual Studio Code & VS Code Server
    - Docker / Docker Compose
    - Qdrant
    - fio
    - Git
    - NVIDIA Container Toolkit
    - Ollama
    - Open-WebUI
  platforms:
    - Windows 11 24H2
    - Ubuntu 24.04 LTS (WSL)
  concepts:
    - File-system Virtualization
    - Remote Development
    - GPU Passthrough / vGPU
    - Benchmarking
    - Vector Database
    - RAG Pipeline

# 參考資源
references:
  internal_links:
    - /2018/07/28/labs-lcow-volume/
    - /2024/03/15/archview-int-blog/
  external_links:
    - https://learn.microsoft.com/windows/wsl/
    - https://fio.readthedocs.io/
    - https://qdrant.tech/
    - https://code.visualstudio.com/docs/remote/remote-overview
    - https://hub.docker.com/r/ollama/ollama
    - https://learn.microsoft.com/windows/wsl/tutorials/gui-apps
    - https://devblogs.microsoft.com/directx/directx-heart-linux/
  mentioned_tools:
    - Docker Desktop
    - Hyper-V
    - VS Code Server
    - DirectML
    - mesa

# 內容特性
content_metrics:
  word_count: 18000
  reading_time: "60 分鐘"
  difficulty_level: "進階"
  content_type: "實戰心得 / 系統調校"
```

## 文章摘要
作者把日常開發機從「Windows + Docker Desktop」全面升級為「Windows 11 24H2 + WSL2 + VS Code Remote」。動機來自四大痛點：Docker Desktop 授權與臃腫、Volume IO 慢到不可用、CUDA 在 Windows 難以部署、以及希望長期維運 Linux 為主的工作流。  
文中先用 fio 為四種檔案路徑（Win→Win、WSL→WSL、Win→WSL、WSL→Win）跑隨機 4K 測試，量化出 576 MiB/s 到 16 MiB/s 的 35× 差異，並歸因於 Hyper-V、DrvFS、9P 等轉譯層。接著以向量資料庫 Qdrant、Jekyll 部落格與 Ollama LLM 為三個案例示範：只要把資料放進 WSL EXT4，效能立刻從 38 秒縮到 1.5 秒；再配合 mklink 把目錄映回 Windows，即可兼顧 DX 與 UX。  
開發端則透過 VS Code Remote 在 WSL 啟動 VS Code Server，讓 Git、Build、Debug 全走 Linux 原生 FS，UI 仍留在 Windows；Ctrl-` 彈出的就是 Bash，Hot-Reload 不再卡頓。  
最後作者驗證 NVIDIA Container Toolkit：僅需安裝 Windows 驅動與 `nvidia-ctk`，WSL 便能以 `/dev/dxg` 直通 GPU，`docker run --gpus all ollama/ollama` 即可跑 Llama 3，用 Task Manager 可見 GPU 佔用。  
整體結論：WSL 生態已成熟，投資一顆專用 SSD、善用 VS Code Remote、避免 DrvFS，把重 IO 與 CUDA 任務全部搬進 Linux，Windows 依舊保留桌面體驗，兩邊優勢一次到手。

---

## 段落摘要

### 1 替換工作環境的動機  
作者因 AI/LLM 需要 GPU 與高 IO，決定趁重灌 24H2 一口氣換掉 Docker Desktop，轉向 WSL2。主要期望：改善 Volume IO、解鎖 GPU in Docker、減少授權束縛並維持 Windows 生態工具。

### 2 案例：向量資料庫 Qdrant  
以 4 萬筆資料的 Qdrant 容器為例，比較不同 Volume 路徑。掛 NTFS 時啟動 38 秒；改放 WSL EXT4 僅 1.5 秒。fio 基準證實 Hyper-V 與 DrvFS/9P 轉譯是瓶頸；解法是把磁碟放進 Linux，Windows 端用 `mklink` 映射存取。

### 2-1 WSL 磁碟效能 Benchmark  
詳細列出四種組合的 4K randrw 分數：Win→Win 576 MiB/s；WSL→WSL 209；WSL→Win 37；Win→WSL 16。並對照架構圖說明各層折損來源。

### 2-6 掛載專屬 SSD  
追加測試四顆 SSD (TLC/MLC/QLC/SATA)，發現「實體 EXT4」或「獨立 vhdx」皆可達原生 100% IO，唯 QLC 效能相對低。結論：買顆好 SSD 給 WSL，DrvFS 只當網路盤。

### 3 GitHub Pages with VS Code  
展示 VS Code Remote：`code .` 會自動布署 VS Code Server，UI 留在 Windows，Terminal 跑 Linux。Git pull->Jekyll build->Hot reload 全在 WSL，檔案更動立即生效，解決 NTFS 缺乏 inotify 的問題。

### 3-1 WSL 執行 Windows App  
透過 binfmt_misc 與 `WSLInterop`，WSL 可直接呼叫 `explorer.exe`、`cmd.exe`，並將目前目錄掛到 `\\wsl$`；證明跨 Kernel 呼叫的高整合度。

### 4 GPU (CUDA) Application  
按官方指南安裝 Windows GPU Driver + WSL NVIDIA CTK，`nvidia-smi` 即顯示 GPU。啟動 `docker run --gpus=all ollama/ollama`，Llama 3 問答可在 1 秒內回應，Task Manager 可見 GPU Loading。也解釋 `/dev/dxg`、DxCore 與 DirectML 在 WSL 的角色。

### 5 心得  
回顧 Satya Nadella 十年「Microsoft ♥ Linux」路線：WSL、VS Code、.NET OSS 及 GPU Pass-through 讓 Windows 成為合格的 Linux Dev Box。只要避開 DrvFS、活用 Remote Dev，Windows 11 已能同時提供桌面體驗與 Linux 原生效能。

---

## 問答集

### Q1 為什麼作者要捨棄 Docker Desktop？  
A: Docker Desktop 體積大、商用授權限制多，而且 Volume 掛載 NTFS 造成嚴重 IO 瓶頸；在 WSL2 直接跑 Linux Docker 不但免費也更單純，Volume 可放 EXT4，效能大幅提升。

### Q2 Win→WSL IO 為何特別慢？  
A: 因為經過 9P Protocol 將 NTFS 操作轉成 EXT4，再疊 Hyper-V vhdx，兩層轉譯讓 4K 隨機 IO 只剩原生約 3% 效能。

### Q3 mklink 能完全解決跨系統路徑問題嗎？  
A: 能大幅簡化路徑記憶與 IDE 操作，但 Windows 端大量 IO 仍走 DrvFS，速度遠低於原生；mklink 只是 UX 改善，不是效能解藥。

### Q4 VS Code Remote 與 SSH/Container 有何差別？  
A: 其核心是 VS Code Server，WSL 模式用本機通道，不依賴網路；SSH 與 DevContainer 則走 TCP/STDIO。WSL 模式整合度最高，無網路亦可用。

### Q5 如何判斷 VS Code 已連上 WSL？  
A: 左下角 Status Bar 顯示「WSL - Ubuntu」，開檔對話框只列 `/home` 路徑，內建 Terminal 是 Bash 而非 PowerShell。

### Q6 在 WSL 要另外安裝 Linux GPU Driver 嗎？  
A: 不需要。只安裝 Windows WDDM 2.9+ 驅動，WSL 透過 `/dev/dxg` 與 Hyper-V vGPU 即可共享硬體。

### Q7 fio 測試為何選 4K randrw、iodepth 64？  
A: 模擬資料庫高併發隨機讀寫情境；大 iodepth 能放大 queue 深度，凸顯轉譯層延遲對 IOPS 的影響。

### Q8 把 SSD 格式化成 EXT4 直接掛 WSL 有風險嗎？  
A: Windows 無法直接存取該分割區，需透過 WSL；備份與磁碟管理需在 Linux 端操作，惟可換得接近原生的效能。

### Q9 QLC SSD 在 WSL 為何表現特別差？  
A: QLC 天然寫入放大與低耐久，在高併發隨機寫環境下易掉速；再疊加 NTFS 或 vhdx 轉譯，效能進一步被稀釋。

### Q10 要跑 LLM 一定得用 NVIDIA 卡嗎？  
A: 目前 WSL CUDA Pass-through 只支援 NVIDIA；AMD/RDNA 仍需等待 ROCm for WSL。若無 GPU 也可用 CPU 但速度與能耗劣勢明顯。

### Q11 DrvFS 完全不能用嗎？  
A: 可作檔案搬運或輕量編輯；任何需要 inotify、低延遲或高 IOPS 的服務（資料庫、熱編譯）都應避免。

### Q12 WSLg 可以拿來跑 Linux GUI IDE 嗎？  
A: 可以，WSLg 會自動轉譯 X11/Wayland 視窗至 Windows，但作者實測 VS Code Remote 提供更流暢且資源佔用更低的體驗。

---

## 問題與解決方案整理

### Problem 1 Docker Volume IO 極慢
Root Cause:
1. DrvFS/9P 跨 Kernel 轉譯  
2. vhdx 再經 Hyper-V 虛擬化  
3. NTFS 與 inotify 不相容  
Solutions:
- 將資料搬進 `~/data` 或獨立 EXT4/vhdx  
- 以 `mklink` 把路徑映回 Windows  
- 重度服務（DB、Vector Store）全部走 WSL → WSL  
Example:
```bash
docker run -v ~/docker/qdrant:/qdrant/storage qdrant/qdrant
```

### Problem 2 開發時需要雙邊高效 IO
Root Cause: IDE 在 Windows，程式跑在 Linux，頻繁跨 FS。  
Solutions:
- 使用 VS Code Remote - WSL  
- Git、Build、Debug 全在 Linux  
- Windows 僅負責前端 UI  
Example:
```bash
# WSL
code .

# Windows VSCode status:
#  --> WSL - Ubuntu
```

### Problem 3 CUDA 在容器環境難部署
Root Cause: Windows 與 Linux Driver 不相容，容器內缺 GPU Runtime。  
Solutions:
1. 安裝 Windows WDDM 2.9+ Driver  
2. `sudo apt install nvidia-container-toolkit && sudo nvidia-ctk runtime configure`  
3. `docker run --gpus=all …`  
Example:
```yaml
services:
  ollama:
    image: ollama/ollama
    runtime: nvidia
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    volumes:
      - ollama:/root/.ollama
```

### Problem 4 不同 SSD 顆粒效能差異大
Root Cause: QLC/DRAM-less 在高併發隨機寫易降速；虛擬化再疊加延遲。  
Solutions:
- 工作碟選 TLC/MLC，甚至獨立 SATA MLC 亦優於 QLC NVMe  
- 專用實體 EXT4 分割給 WSL  
- 若用 vhdx，避免與系統碟共用 IO  

---

## 版本異動
- 1.0.0 (2025-08-06)  首次生成：含 Metadata、摘要、5 段段落摘要、12 組 Q&A、4 組 Problem/Solution。