---
source_file: "_posts/2024/2024-11-11-working-with-wsl.md"
generated_date: "2025-01-03 20:00:00 +0800"
version: "1.0"
tools: github_copilot
model: claude_sonnet_3_5
---

# 用 WSL + VSCode 重新打造 Linux 開發環境 - 生成內容

## Metadata

### 原始 Metadata

layout: post
title: "用 WSL + VSCode 重新打造 Linux 開發環境"
categories:
- "技術隨筆"
tags: ["技術隨筆", "VSCode", "Jekyll", "Docker", "WSL"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-11-11-working-with-wsl/logo.jpg

### 自動識別關鍵字

keywords:
  primary:
    - WSL
    - VSCode
    - Docker
    - Linux 開發環境
    - GPU 虛擬化
    - 檔案系統效能
    - 跨平台開發
  secondary:
    - NTFS
    - EXT4
    - DrvFS
    - 9P protocol
    - Hyper-V
    - CUDA
    - GitHub Pages
    - Jekyll
    - Qdrant
    - AI 應用
    - 向量資料庫
    - LLM
    - Ollama

### 技術堆疊分析

tech_stack:
  languages:
    - Bash
    - PowerShell
  frameworks:
    - WSL2
    - Docker
    - Jekyll
  tools:
    - Visual Studio Code
    - Git
    - Docker Compose
    - WSL
    - fio
    - nvidia-smi
  platforms:
    - Windows 11
    - Ubuntu 24.04 LTS
    - Docker Desktop
    - WSL2
  concepts:
    - File System Performance
    - GPU Virtualization
    - Remote Development
    - Cross-platform Development
    - Container Technology
    - AI/ML Infrastructure

### 參考資源

references:
  internal_links:
    - /2018/07/28/labs-lcow-volume/
    - /2024/03/15/archview-int-blog/
    - /2016/05/05/archview-net-open-source/
  external_links:
    - https://learn.microsoft.com/en-us/windows/wsl/setup/environment
    - https://code.visualstudio.com/docs/remote/remote-overview
    - https://qdrant.tech/
    - https://ollama.com/
    - https://pages.github.com/
    - https://devblogs.microsoft.com/directx/directx-heart-linux/
    - https://www.polarsparc.com/xhtml/IntroToWSL2.html
    - https://news.mynavi.jp/article/20220318-2296803/
    - https://blog.darkthread.net/blog/ollam-open-webui/
  mentioned_tools:
    - WSL2
    - Visual Studio Code
    - Docker
    - Qdrant
    - Ollama
    - Open-WebUI
    - Jekyll
    - GitHub Pages
    - fio
    - nvidia-smi
    - CUDA
    - DirectX
    - GPU drivers

### 內容特性

content_metrics:
  word_count: 15000
  reading_time: "45 分鐘"
  difficulty_level: "進階"
  content_type: "技術教學"

## 摘要

### 文章摘要

作者詳細記錄了將主要開發環境從傳統 Windows 轉移到 WSL + VSCode 的完整過程與心得。文章起因於作者希望解決四個核心問題：拋開 Docker Desktop for Windows 的束縛、改善 Docker 掛載 volume 的 IO 效能問題、在 Docker 中使用 GPU/CUDA 應用、以及建立一個以 Linux 為主且能與 Windows 無縫整合的長期工作環境。作者透過詳細的效能測試發現，不同的檔案系統組合會造成高達 35 倍的效能差距，最終透過將檔案存放在 WSL 原生檔案系統、使用 VSCode Remote Development 模式、以及正確配置 GPU 虛擬化，成功建立了一套高效的跨平台開發環境。文章不僅提供實用的配置方法，更深入解析了 WSL 架構、檔案系統互通機制、以及 Microsoft 在底層實現的各種黑科技，為想要在 Windows 平台建立 Linux 開發環境的開發者提供了完整的參考指南。

### 關鍵要點

- WSL + VSCode 的整合可以提供接近原生 Linux 的開發體驗
- 檔案系統的存放位置對效能有巨大影響，跨系統存取會造成嚴重效能損失
- 透過正確配置，可以在 Windows 下無痛使用 Docker 和 GPU 加速的 AI 應用
- Microsoft 在 WSL 中實現了許多底層整合技術，包括 GPU 虛擬化和檔案系統互通
- VSCode Remote Development 模式可以完美解決跨系統開發的各種問題
- 投資專用的 SSD 給 WSL 使用可以獲得最佳的效能表現
- GPU 虛擬化技術讓 WSL 能夠直接使用 Windows 的 GPU 驅動和 CUDA 功能

### 替換工作環境的動機

作者決定重新打造開發環境的主要動機是為了在 Docker 上運行 AI 相關應用。當購買了 NVIDIA RTX4060Ti 16GB 後，發現要在 Windows 下搞定 CUDA 相依性套件與設定非常麻煩，而大部分科學運算應用都以 Linux 為主。除此之外，作者也面臨 Docker Desktop for Windows 的授權限制、Docker 掛載 volume 的 IO 效能問題（效能差距可達數十倍）、以及希望建立一個認知負荷低且能長期使用的整合工作環境。透過實際測試發現，Qdrant 向量資料庫的啟動時間從原本的一分鐘縮短到幾秒鐘，Jekyll 建置時間從 110 秒降到 6 秒，這些戲劇性的改善證明了原本架構確實存在嚴重問題。

### WSL 磁碟效能分析與檔案系統架構

作者透過詳細的 benchmark 測試，量化了四種不同檔案系統組合的效能表現。測試結果顯示，Windows 原生 NTFS 存取可達 576 MiB/s，WSL 內部 EXT4 存取為 209 MiB/s（36.28%），而跨系統存取的效能則大幅下降：Windows 存取 WSL 檔案系統僅有 16.5 MiB/s（2.86%），WSL 存取 Windows 檔案系統為 37.5 MiB/s（6.51%）。這些效能差異的根本原因在於 WSL 的檔案系統架構，包括 Hyper-V 虛擬化層、9P protocol、以及 DrvFS 檔案系統轉換等多層轉換機制。作者建議將重要的應用程式檔案存放在 WSL 原生檔案系統中，並透過 Windows 的 mklink 指令建立 symbolic link 來維持存取的便利性。

### Visual Studio Code Remote Development 整合

作者詳細介紹了 VSCode Remote Development 的運作機制，這是解決跨系統開發問題的關鍵技術。VSCode Remote Development 採用前後端分離的架構，UI 操作在 Windows 端處理，而檔案存取、編譯、執行等背景作業則在 Linux 端進行。這種設計完美解決了效能問題，因為所有重度 IO 操作都在同一個作業系統內完成。作者展示了如何在 WSL 中直接使用 `code .` 指令啟動 VSCode，以及如何在 VSCode 中直接存取 Linux 檔案系統、啟動 Linux terminal、運行 Docker 容器、並透過 port forwarding 預覽網頁應用。整個過程的整合度極高，幾乎可以將其視為單機版使用，即使在無網路環境下也能正常運作。

### GPU 虛擬化與 AI 應用支援

作者成功配置了 WSL 的 GPU 虛擬化功能，讓 Docker 容器能夠直接使用 NVIDIA GPU 進行 CUDA 運算。配置過程出乎意料地簡單：只需在 Windows 安裝正確版本的 NVIDIA GPU 驅動、在 WSL 安裝 NVIDIA container toolkit、以及正確配置 Docker runtime。配置完成後，可以透過 `nvidia-smi` 指令在 WSL 中查看 GPU 狀態，並在啟動 Docker 容器時使用 `--gpus=all` 參數來啟用 GPU 支援。作者成功運行了 Ollama + Open-WebUI 的組合，建立了私人的類 ChatGPT 介面，證明整套環境能夠順利支援需要 GPU 加速的 AI 應用。Microsoft 在底層實現了完整的 GPU 虛擬化架構，包括 DirectX、CUDA、OpenGL、OpenCL 等各種 GPU 運算框架的支援。

## 問答集

### Q1: 為什麼需要重新打造 Linux 開發環境？
Q: 在 Windows 下開發有什麼問題需要透過 WSL 來解決？
A: 主要問題包括：Docker Desktop for Windows 的授權限制和額外負擔、Docker 掛載 Windows volume 時的嚴重 IO 效能問題（可能差距數十倍）、Windows 下配置 CUDA 環境的複雜性、以及缺乏一個能夠無縫整合 Windows 和 Linux 工具的統一開發環境。這些問題在處理 AI 應用或需要大量 IO 的容器化服務時特別明顯。

### Q2: WSL 的檔案系統效能差異有多大？
Q: 不同的檔案系統組合對效能有什麼影響？
A: 根據 benchmark 測試，效能差異極大：Windows 原生 NTFS 存取為基準（576 MiB/s），WSL 內部 EXT4 存取約為 36%，而跨系統存取效能則大幅下降，Windows 存取 WSL 檔案僅有 3%，WSL 存取 Windows 檔案約有 7%。這是因為跨系統存取需要經過多層轉換，包括 9P protocol 和 DrvFS 檔案系統轉換。

### Q3: 如何正確配置 WSL 的檔案存放策略？
Q: 要如何安排檔案存放位置才能獲得最佳效能？
A: 建議將需要大量 IO 的應用程式檔案（如 Docker volumes、資料庫檔案）存放在 WSL 原生檔案系統中（如 `/opt/docker`），然後透過 Windows 的 `mklink /d` 指令建立 symbolic link 到習慣的 Windows 路徑（如 `c:\codes\docker`）。這樣既能獲得最佳的 IO 效能，又能維持操作的便利性。

### Q4: VSCode Remote Development 如何解決跨系統開發問題？
Q: VSCode Remote Development 的運作原理是什麼？
A: VSCode Remote Development 採用前後端分離架構，UI 在 Windows 端處理，而檔案操作、編譯、執行等重度 IO 作業在 Linux 端進行。透過 vscode-server 機制，可以在 WSL 中直接使用 `code .` 指令啟動完整的開發環境，所有操作都像在本機一樣流暢，但實際的檔案處理都在同一個作業系統內完成，避免了跨系統的效能損失。

### Q5: 如何在 WSL 中使用 GPU 進行 AI 運算？
Q: WSL 支援 GPU 虛擬化嗎？如何配置？
A: WSL2 完全支援 GPU 虛擬化。配置步驟包括：在 Windows 安裝最新的 NVIDIA GPU 驅動、在 WSL 安裝 NVIDIA container toolkit（注意不需要安裝 Linux GPU 驅動）、配置 Docker runtime 使用 nvidia-ctk。配置完成後可以在 WSL 中使用 `nvidia-smi` 查看 GPU 狀態，Docker 容器啟動時加上 `--gpus=all` 參數即可使用 GPU 資源。

### Q6: 投資專用 SSD 給 WSL 使用是否值得？
Q: 為 WSL 配置專用硬碟能帶來多大改善？
A: 絕對值得。測試顯示，將實體磁碟直接掛載給 WSL 使用（EXT4 格式）可以獲得接近甚至超越 Windows 原生效能的表現。某些情況下，優質的 MLC SSD 在 WSL 環境下的表現甚至比在 Windows 下還要好（達到 120% 效能）。但要注意避免低階的 QLC SSD，因為虛擬化環境會放大其效能缺陷。

## 解決方案

### Docker 容器 IO 效能優化
Problem: Docker 容器掛載 Windows volume 時效能極差，影響資料庫和建置工具的運行速度
Root Cause: 跨作業系統的檔案存取需要經過 DrvFS 和 9P protocol 多層轉換，造成嚴重的效能瓶頸
Solution:
- 將 Docker volumes 遷移到 WSL 原生檔案系統（如 `/opt/docker`）
- 使用 Windows mklink 建立 symbolic link 維持存取便利性
- 確保容器和資料都在同一個作業系統內運行
- 避免在 Docker 啟動時掛載跨系統的目錄

Example:
```bash
# 在 WSL 中建立 Docker 工作目錄
sudo mkdir -p /opt/docker

# 在 Windows 中建立 symbolic link
mklink /d c:\codes\docker \\wsl$\ubuntu\opt\docker

# Docker Compose 使用相對路徑或 WSL 內路徑
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

### VSCode 跨系統開發環境建置
Problem: 需要在 Windows 和 Linux 之間頻繁切換，缺乏統一的開發體驗
Root Cause: 傳統開發方式需要分別在兩個系統中配置工具，無法充分利用各自的優勢
Solution:
- 安裝 VSCode Remote Development extension pack
- 在 WSL 中直接使用 `code .` 啟動遠端開發模式
- 利用 vscode-server 實現前後端分離的開發架構
- 透過 port forwarding 功能預覽和調試應用程式

Example:
```bash
# 在 WSL 中切換到專案目錄
cd /opt/docker/my-project

# 直接啟動 VSCode Remote Development
code .

# 在 VSCode 內建 terminal 執行 Docker
docker-compose up -d

# 使用 port forwarding 預覽應用
# VSCode 會自動偵測並提供瀏覽器預覽選項
```

### GPU 虛擬化配置與 AI 應用部署
Problem: 在 Windows 下配置 CUDA 環境複雜，AI 應用部署困難
Root Cause: Windows 下的 CUDA 相依性管理複雜，版本相容性問題多
Solution:
- 在 Windows 安裝最新 NVIDIA GPU 驅動
- 在 WSL 安裝 NVIDIA Container Toolkit
- 配置 Docker 使用 nvidia-ctk runtime
- 使用容器化方式部署 AI 應用，避免直接管理相依性

Example:
```bash
# 檢查 GPU 是否正確識別
nvidia-smi

# 安裝 NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 運行支援 GPU 的容器
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 檔案系統效能優化策略
Problem: 需要在不同檔案系統間找到效能和便利性的平衡點
Root Cause: WSL 架構的多層虛擬化導致跨系統存取效能差異巨大
Solution:
- 根據應用類型選擇合適的檔案系統配置
- 投資專用 SSD 並正確配置掛載方式
- 避免在效能敏感的應用中使用 DrvFS
- 使用 symbolic link 和 mount 技術優化存取路徑

Example:
```bash
# 為 WSL 掛載專用磁碟（需要 Windows 管理員權限）
# 1. 在 Windows 中準備磁碟
wsl --mount \\.\PHYSICALDRIVE2 --type ext4

# 2. 在 WSL 中掛載到指定位置
sudo mkdir -p /mnt/wsl-disk
sudo mount /dev/sdc1 /mnt/wsl-disk

# 3. 配置自動掛載
echo '/dev/sdc1 /mnt/wsl-disk ext4 defaults 0 0' | sudo tee -a /etc/fstab

# 4. 建立工作目錄並設定權限
sudo mkdir -p /mnt/wsl-disk/docker
sudo chown -R $USER:$USER /mnt/wsl-disk/docker
```

## 版本異動紀錄

### v1.0 (2025-01-03)
- 初始版本生成
- 基於原始文章完整內容建立結構化摘要、問答對和解決方案
