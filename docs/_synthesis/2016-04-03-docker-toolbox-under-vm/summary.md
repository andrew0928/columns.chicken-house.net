---
layout: synthesis
title: "如何在 VM 裡面使用 Docker Toolbox ?"
synthesis_type: summary
source_post: /2016/04/03/docker-toolbox-under-vm/
redirect_from:
  - /2016/04/03/docker-toolbox-under-vm/summary/
postid: 2016-04-03-docker-toolbox-under-vm
---

# 如何在 VM 裡面使用 Docker Toolbox ?

## 摘要提示
- 問題起點: 在 Hyper-V 下的 VM 內無法再建立 VM，導致 Docker Toolbox（依賴 VirtualBox）無法運行
- 虛擬化限制: 第一層 VM 的 vCPU 通常不支援 VT-x/AMD-V，無法再啟動第二層虛擬機
- Nested Virtualization: Windows 10/Server 2016 預覽版支援巢狀虛擬化，可把硬體虛擬化功能暴露給 VM
- 系統需求: 需 Windows Build 10565+、Intel VT-x、至少 4GB RAM，且不建議用於生產環境
- 啟用方式: 透過 Microsoft 提供的 PowerShell 腳本替指定 VM 開啟巢狀虛擬化
- VirtualBox 相容問題: 在巢狀虛擬化下 VirtualBox 仍不穩定，常見無法啟動 VM 的錯誤
- 解法關鍵: 改用 Docker Machine 的 Hyper-V driver 建立 boot2docker 主機
- 網路設置: 需於 Hyper-V 建立虛擬交換器，確保 Docker Host VM 具備網路
- 使用流程: docker-machine create -d hyperv 建立主機並設定環境變數後即可使用 Docker
- Kitematic 調整: 預設綁 VirtualBox，需額外修改才能在 Hyper-V 上運作

## 全文重點
本文探討如何在虛擬機內使用 Docker Toolbox 的實務解法。問題根源在於 Docker Toolbox 預設依賴 Oracle VirtualBox 建立 Linux VM；但一旦在 Hyper-V 上再開一層 VM，通常無法提供 VT-x/AMD-V，導致第二層 VM 無法啟動。微軟在 Windows 10/Server 2016 預覽中推出 Nested Virtualization，可將硬體虛擬化功能向下暴露到客體 VM，使其能再跑自己的 Hypervisor。然而此功能仍在預覽期，且有硬體（Intel VT-x）與版本（Build 10565+）、記憶體（至少 4GB）等限制，並不支援動態記憶體與快照等功能。

作者先以 PowerShell 腳本為特定 VM 啟用巢狀虛擬化，成功越過 VT-x 檢查，但實測發現 VirtualBox 在此情境仍不穩定，出現 VM 無法啟動、初始化失敗等錯誤。因而改變路線：捨棄 VirtualBox，改用 Docker Machine 與 Hyper-V driver 建置 Docker Host。步驟為移除 VirtualBox、啟用 Hyper-V、設定虛擬交換器，接著以 docker-machine create -d hyperv 建立 boot2docker 主機，透過 docker-machine env 設定環境變數後，即可在 VM 內使用 Docker 指令順利拉取與執行容器（例如 hello-world）。

最後提到 Docker Toolbox 中的 GUI 工具 Kitematic 預設仍綁定 VirtualBox，若要在 Hyper-V 方案下使用需參考社群文章進行修改。整體而言，核心解法是：在支援的 Windows 版本上啟用巢狀虛擬化，並使用 Hyper-V 而非 VirtualBox 來提供 Docker Host，藉 Docker Machine 以一致介面管理 VM，繞開 VirtualBox 與巢狀虛擬化的不相容問題。

## 段落重點
### 關鍵問題: 無法在 VM 裡面建立 VM!
Docker 在 Windows 上運行需透過 Linux VM 作為 Docker Host，Docker Toolbox 預設使用 VirtualBox 來建立此 VM。然而當使用者已在 Hyper-V 上跑一層 Windows VM 時，該 VM 的 vCPU 多半不具備 VT-x/AMD-V，使得第二層虛擬化失敗，VirtualBox 無法啟動 Linux VM。核心難題因此變成「如何在 VM 裡再建立 VM」。這是安裝架構上的先天限制：Docker 本體需要 Linux Kernel；Windows 上要跑容器勢必先有一台 Linux VM，但二階虛擬化常因缺乏硬體輔助而失敗。

### Nested Virtualization Support
微軟在 Windows 10/Server 2016 預覽加入 Nested Virtualization，讓 Hyper-V 能將硬體虛擬化延伸至客體 VM，使其可安裝 Hypervisor 並再開子 VM。雖仍處於 preview 且未揭露效能細節（例如是否轉送至 L0 處理、雙層虛擬化的成本），但已可作為實驗與教學用途。此能力對研究微服務與容器相當實用，因為能在單機或受限環境下模擬更接近實務的拓樸，無須直接佔用或風險性操作實體主機。

### 替 VM 啟用 Nested Virtualization 的支援
要使用巢狀虛擬化需滿足條件：Windows Build 10565 以上、Intel 平台（VT-x）、至少 4GB RAM，且不建議用於生產。以 PowerShell 執行微軟提供的 Enable-NestedVm.ps1，對指定 VM 名稱進行檢查與設定，逐一開啟所需選項（例如 MAC 位址偽裝），並提示不支援動態記憶體與檢查點等限制。流程是先正常建立 VM，再套用腳本開巢狀。作者實測在 Windows 10 (10586) 上符合需求，並成功對目標 VM 啟用此功能，完成 Host 端準備。

### 安裝 Docker Toolbox, 準備 Docker Host VM
在已啟用巢狀虛擬化的客體 Windows VM 內安裝 Docker Toolbox，過程採預設值。初期初始化顯示已通過 VT-x 檢測，但隨後 VirtualBox 在 VM 內仍出現啟動失敗等不穩定現象，多次嘗試後仍無法修復。推測為預覽期兼容性問題：雖然 Hyper-V 已能把虛擬化能力暴露給客體 VM，但 VirtualBox 在此情境下依然不完全支援，導致 Docker Toolbox 預設路徑行不通。因此作者決定放棄 VirtualBox，轉向微軟自家 Hyper-V 以提高成功率與穩定性。

### Docker Machine
Docker Machine 提供一致化建立 Docker Host 的介面，支援多種 driver（AWS、Azure、Hyper-V、VirtualBox、vSphere 等）。解法為：移除 VirtualBox、啟用 Hyper-V，並先於 Hyper-V 建立虛擬交換器，確保新建 Docker Host VM 具備網路。接著以 docker-machine create -d hyperv boot2docker 建立主機；流程會自動準備 boot2docker.iso、設定 SSH 憑證與 Docker 守護行程。最後以 docker-machine env boot2docker 匯入環境變數，便能直接在 VM 內執行 docker 指令。作者以 hello-world 驗證成功，證明改用 Hyper-V driver 能在巢狀環境順利運作。

### MODIFYING KITEMATIC TO RUN ON WINDOWS 10 WITH HYPER-V
Kitematic 是 Docker Toolbox 同捆的圖形化工具，能以 App Store 式體驗快速瀏覽與啟動容器映像。然而其預設綁定 VirtualBox，於 Hyper-V 方案下無法直接運作。作者提供一篇社群文章作參考，示範如何修改 Kitematic 的底層呼叫，將其從 VirtualBox 切換到 docker-machine 的 Hyper-V driver。整體來說，CLI 端以 Docker Machine + Hyper-V 已可解決大部分需求；若需 GUI 體驗，則可能需投入額外調整，使工具鏈自洽於 Hyper-V 生態。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本虛擬化概念（Hypervisor、VT-x/AMD-V、Nested Virtualization）
   - Docker 基礎（Docker Client/Daemon、Image/Container）
   - Windows 平台虛擬化工具（Hyper-V、VirtualBox）基本操作
   - PowerShell 基本使用

2. 核心概念：
   - Docker Toolbox 與其組件：包含 Docker Machine、VirtualBox、Kitematic，用於在 Windows 上快速建置 Docker 環境
   - Nested Virtualization：在 VM 內再運行 Hypervisor/VM 的能力，是在 VM 內跑 Docker 的關鍵
   - Docker Machine Driver：以一致化介面在不同 Hypervisor/雲端建立 Docker Host（boot2docker）
   - Hyper-V 替代 VirtualBox：在 Nested 環境中 VirtualBox 可能失敗，改用 Hyper-V 驅動更可靠
   - 網路與環境變數設定：Hyper-V Virtual Switch、docker-machine env 對接 Docker Host

3. 技術依賴：
   - Docker 於 Windows 上需依賴 Linux Kernel（透過 VM，例如 boot2docker）
   - Docker Toolbox 預設依賴 VirtualBox；在 Nested 情境下可能不相容 → 改用 Hyper-V Driver
   - Nested Virtualization 依賴硬體 VT-x（Intel）與 OS 版本（Windows 10/Server 2016 Insider/10565+）
   - Docker Machine 依賴對應 Driver（hyperv、virtualbox、azure、aws 等）管理 VM 生命週期
   - Kitematic 預設綁 VirtualBox；若改用 Hyper-V 需額外修改流程

4. 應用場景：
   - 在公司受限環境或教學/實驗室中，於現有 VM 內體驗與練習 Docker
   - 微服務架構實驗、PoC 在非實體機上快速搭環境
   - 雲端/本地混合開發：同一套 docker-machine 流程切換 Hyper-V、AWS、Azure 等目標

### 學習路徑建議
1. 入門者路徑：
   - 認識 Docker 基本概念與指令（run、pull、images、ps）
   - 安裝 Docker Toolbox，理解其組件（Docker Machine、Kitematic、VirtualBox）
   - 在非 Nested 環境先跑一個 hello-world，熟悉 docker-machine env 設定

2. 進階者路徑：
   - 理解 Nested Virtualization 原理與限制（VT-x、RAM、OS 版本、功能限制如不支援 Dynamic Memory/Checkpoint）
   - 於 Hyper-V 啟用 Nested Virtualization（PowerShell 腳本 Enable-NestedVm.ps1）
   - 掌握 Docker Machine 多種 Driver（hyperv/virtualbox/aws/azure）與常見參數

3. 實戰路徑：
   - 在 Hyper-V Host 上對目標 VM 啟用 Nested Virtualization
   - 在該 VM 內卸載 VirtualBox、安裝/啟用 Hyper-V，建立 Virtual Switch
   - 使用 docker-machine create -d hyperv 建立 boot2docker，透過 docker-machine env 對接並執行容器
   - 需要 GUI 時，參考社群做法調整 Kitematic 以支援 Hyper-V 或改用 CLI/Portainer 等替代

### 關鍵要點清單
- Nested Virtualization 基礎：在 VM 內再次啟用 Hypervisor 能力，允許建立次級 VM（優先級: 高）
- 硬體與 OS 要求：Intel VT-x、至少 4GB RAM、Windows Build 10565+（優先級: 高）
- 預覽版限制：不建議用於生產；不支援 Dynamic Memory、Checkpoints、需啟用 MAC Spoofing（優先級: 中）
- Enable-NestedVm.ps1 腳本：以 PowerShell 在 Hyper-V Host 對特定 VM 啟用 Nested（優先級: 高）
- Docker Toolbox 組件：包含 Docker Machine、VirtualBox、Kitematic；是 Windows 用戶的一站式工具（優先級: 中）
- VirtualBox 相容性問題：在 Nested 環境下可能無法啟動 VM（優先級: 高）
- 改用 Hyper-V Driver：以 docker-machine -d hyperv 取代 VirtualBox 建立 Docker Host（優先級: 高）
- Hyper-V 網路設定：需建立 External Virtual Switch 以確保 Docker Host VM 有網路（優先級: 高）
- boot2docker：針對 Docker Host 的精簡 Linux，docker-machine 會自動下載與配置（優先級: 中）
- docker-machine env：設定環境變數讓 Docker Client 連線到對應 Docker Host（優先級: 高）
- hello-world 測試：驗證 Client→Host→Docker Hub→容器執行的端到端流程（優先級: 中）
- Kitematic 限制與替代：預設綁 VirtualBox，改用 Hyper-V 需改造或改用 CLI/其他 GUI（優先級: 低）
- 多雲/多目標驅動：Docker Machine 可切換至 AWS/Azure/vSphere 等，流程一致（優先級: 中）
- 效能考量：Nested 層疊會有開銷，適合學習/PoC，不建議生產（優先級: 中）
- 疑難排解要點：確認 VT-x 開啟、RAM 配額、MAC Spoofing、OS 版本與 Driver 是否正確（優先級: 高）