---
layout: synthesis
title: "專為 Windows 量身訂做的 Docker for Windows (Beta) !"
synthesis_type: summary
source_post: /2016/06/11/docker-for-window-beta-evaluate/
redirect_from:
  - /2016/06/11/docker-for-window-beta-evaluate/summary/
postid: 2016-06-11-docker-for-window-beta-evaluate
---

# 專為 Windows 量身訂做的 Docker for Windows (Beta) !

## 摘要提示
- 原生整合: Docker for Windows Beta 改以 Hyper-V 管理 Linux VM，移除 VirtualBox，整合度與穩定性大幅提升。
- 操作體驗: 內建設定介面與自動更新，Docker CLI、Compose、Machine 一次到位，開發流程更順暢。
- 效能與可靠性: 新架構更快更穩，Volume 掛載速度與一致性明顯改善。
- Linux 基底替換: 從 Boot2Docker 改為 Alpine Linux + BusyBox，輕量與啟動速度更佳。
- 與 Toolbox 並存: 可與 Docker Toolbox 共存，暫不含 Kitematic，仍需 Toolbox 使用該 GUI。
- 多架構支援: 規劃支援 x86 與 ARM（Windows 版說明即將推出），擴大影像建置與執行範圍。
- Nested Hyper-V: 在 VM 內測試需啟用巢狀虛擬化，並遵守記憶體、快照、MAC 偽裝等限制。
- 本機卷掛載: 透過 Shared Drives 授權磁碟後，容器能直接讀寫 Windows 檔案系統。
- Windows 容器走向: Microsoft 與 Docker 深度合作，提供 process 和 hyper-v 兩級隔離。
- DevOps 版圖: 從本機開發到雲端部署的生態整合更完整，有助團隊導入與推廣。

## 全文重點
本文記錄作者取得 Docker for Windows Beta 的上手體驗與在 VM 內測試的實作筆記。新版以 Hyper-V 取代 VirtualBox，並在隱含的 Alpine Linux VM 上運行 Docker Engine，藉由原生應用與統一設定介面，改善過去在非 Linux 平台上操作 Docker 的痛點。相較 Docker Toolbox，本版提供更快更穩的體驗、簡化工具鏈安裝與更新，並對 Volume 掛載提供一致且可預期的行為。

在技術面，Docker 工具組改為原生整合，啟動時可自動安裝/啟用 Hyper-V，並由 Docker 服務統一管理對應 VM。卷掛載方面，Windows 端可在 Docker 設定中勾選 Shared Drives，實際上是以 SMB 分享的方式讓容器透過 Volume Driver 存取 Windows 檔案系統，實測證明唯有開啟對應磁碟分享，容器才看得到並能持久化到本機檔案。文章亦示範在 VM 內啟用 Nested Hyper-V 的完整路徑，包含作業系統版本需求、記憶體與檢查點限制、MAC spoofing、以及 Intel VT-x 必要條件等，並逐步完成在「VM 內再啟 VM」的環境準備。

作者指出，Docker 與 Microsoft 在容器隔離技術的協作正逐步落地。Windows 容器在 process 隔離之外，另提供以輕量級 VM 為基礎的 hyper-v 隔離，可透過 docker run --isolation=hyperv 指定。雖然目前多架構與 Windows 容器的完整體驗仍在推進中，但趨勢顯示從開發環境（Windows/Mac 桌面）到上線環境（Linux 原生 + Cluster）正被更緊密串接，Docker Hub 也已率先納入 Windows 相關生態。整體而言，Docker for Windows Beta 顯著降低在 Windows 開發機上的使用門檻，對 DevOps 前段的開發效率帶來實質助益；而隨 Windows Server 2016 與 Windows Container 成熟，團隊提前熟悉此生態系將是值得的投資。

## 段落重點
### Docker for Windows Beta, 操作體驗大躍進!
作者首先回顧過去在 Windows 上以 VirtualBox + Docker Toolbox 的不佳體驗，常為相容性與整合性所苦，甚至改以手動架設 Linux VM 或獨立 Linux 主機來使用 Docker。本次 Beta 改以 Hyper-V 管理 Alpine Linux VM，並由原生應用接管安裝、設定與自動更新，免除外部工具依賴。官方亮點包括速度更快、穩定性更高、工具整合完整、可與 Toolbox 並存、多架構支援等；同時更換基底至 Alpine + BusyBox、統一以 Docker 服務管理 VM 啟動，整體整合度提升。作者認為此舉能大幅降低 Windows/Mac 開發者導入門檻，有助串連從本機開發到雲端部署的 DevOps 流程。Docker 近年併購與整合（Docker Hub、Docker Cloud、Unikernel Systems）顯示其在生態建構上的企圖與前瞻，令人期待未來在系統結構與隔離技術上的更多突破。

### Tips: 如何在 VM 裡面體驗 Docker for Windows?
本節說明在「VM 內再跑 Docker for Windows（其背後仍啟 Linux VM）」的巢狀虛擬化實作。因 Docker Engine 仍依賴 Linux，Windows 版會自動建立名為 MobyLinuxVM 的 Alpine VM；若欲在 VM 內測試，必須啟用 Nested Hyper-V。作者提供架構圖與命名：實體機（CHICKEN-PC）上啟一台 Windows 10 VM（WIN10），其中 Docker 會建立 MobyLinuxVM 執行 Engine。重點在於層次清楚，避免「夢中夢」混淆；並提醒若 Nested 設置不正確，MobyLinuxVM 將無法啟動。實務上，先在外層主機建立可支援巢狀虛擬化的 VM，後續才在該 VM 內安裝並啟用 Docker for Windows，最後驗證容器能順利啟動與掛載卷，即可安全在受控環境中體驗 Beta 功能。

### STEP #1, 準備好支援 Nested Hyper-V 的 VM
此步聚焦巢狀虛擬化需求與限制。主機與來賓 OS 需為 Windows 10 Pro/Enterprise 或 Windows Server 2016（Build 10565 以上）；Windows 10 Home 不支援 Hyper-V。必須以 PowerShell 啟用 Nested Virtualization，且受多項限制：須關閉動態記憶體、不可在執行中套用檢查點、無法 Live Migration、Save/Restore 受限；必須啟用 MAC spoofing；禁用 Device Guard/VBS；僅支援 Intel VT-x；記憶體需求偏高。作者示範於 CHICKEN-PC（Win10 Ent 10586）上建立名為 WIN10 的 VM，分配至少 4GB RAM、停用動態記憶體，並依官方文件啟用巢狀虛擬化。完成後再於該 VM 內進行 Docker for Windows 的安裝。若設定得當，後續才能在此 VM 內再啟動 Docker 內部的 Linux VM。

### STEP #2, 在 VM 內安裝設定 Docker for Windows Beta
在 WIN10 VM 內以 MSI 安裝 Docker for Windows。若事先未啟用 Hyper-V，Docker 首次啟動會提示自動安裝並重開機。完成後輸入 Beta Token 進入。若 MobyLinuxVM 啟動失敗，多半源自外層未正確啟用 Nested Hyper-V，應回到 Hyper-V 管理員或手動建立測試 VM 驗證是否能在來賓內再開 VM；勿急於重裝 Docker。當右下角托盤顯示 Docker 圖示且提示啟動完成，代表內部 Alpine VM 已就緒。Docker Settings 提供統一管理介面，可調整 VM CPU/記憶體、設定更新與共用磁碟等。此時即完成在 VM 內部署 Docker for Windows 的環境準備，可著手拉取映像並執行容器。

### STEP #3, 執行 Docker Container: Hello-World
在 WIN10 VM 的 PowerShell 或命令提示字元直接執行 docker run --rm hello-world，即可測試到從 Windows CLI 透過 Docker for Windows 控制內部 Engine 的完整路徑。成功輸出代表網路與映像拉取、MobyLinuxVM、Engine、CLI 到容器執行鏈路皆正常。相較過去需 SSH 進 Linux VM 執行 Docker 指令，新版可在 Windows 原生腳本與工具鏈中直接使用 Docker CLI，更利於與既有批次流程、自動化腳本和 CI 工具結合。此步驟確認核心執行環境健康，是進一步測試卷掛載與開發工作流前的最低門檻驗證。

### STEP #4, 掛載 Windows Folder, 給 Container 使用
重點展示本機卷掛載。於 Docker Settings 的 Shared Drives 勾選要授權的磁碟（實作上是建立對應 SMB Share），之後以 -v c:\path:/data 方式將 Windows 路徑掛入容器。作者實測：未勾選 C: 時，容器雖可啟動且 /data 存在，但看不到本機檔，且在容器內建立的檔案不會出現在 Windows 檔案總管（代表未連至本機實體路徑，而是掛到 Engine 預設卷位置）。當啟用 C: 的 Shared Drive 後，再以相同指令啟動 Alpine，容器內對 /data 的讀寫會即時反映於 Windows 對應目錄，且刪除並重建容器後檔案仍在，驗證了正確的本機持久化。此機制雖仍透過網路分享實作，但流程被 Docker 封裝簡化，顯著改善開發時的檔案同步與效能一致性。

### 後記: Container Isolation Technonlgy
作者關注多架構與隔離技術走向。官方宣稱將支援 Linux x86 與 ARM（Windows 相關文件即將推出），而 Windows 容器部分，Microsoft 將隔離分成 process（命名空間）與 hyper-v（以輕量 VM 提供核心級隔離）兩種。Docker CLI 已可見 --isolation 參數，於 Windows 平台可選 default、process、hyperv，其中 hyperv 能提供更高等級隔離。MSDN 文件示範以 docker run -it --isolation=hyperv nanoserver cmd 建立 Hyper-V 容器。可見 Docker 與 Microsoft 在工具與 API 層面逐步對齊，為未來在 Windows 環境下安全與彈性並重的容器落地鋪路，亦為混合工作負載與更嚴格合規場景提供選項。

### 總結
Docker for Windows Beta 以 Hyper-V 為核心，結合原生應用與輕量 Alpine VM，實質降低 Windows 開發機使用 Docker 的門檻，並修補 Toolbox 時代在相容、效能與體驗上的斷裂。作者透過在 VM 內啟用 Nested Hyper-V 的實作，證實可安全在隔離環境測試 Beta 功能；同時以 Shared Drives 驗證本機卷掛載的可用性與持久化。更重要的是，Docker 與 Microsoft 的緊密合作，使 Windows Container 的隔離技術、工具鏈與生態（含 Docker Hub）逐步一致。儘管 Windows Server 2016 尚在演進，開發團隊若及早熟悉此整合生態，未來從開發到部署將能沿用一致流程與資源，投資報酬可期。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本容器觀念：Docker Engine、Image、Container、Volume 概念
   - 虛擬化基礎：Hypervisor、Hyper‑V 基礎設定與限制、Nested Virtualization
   - Windows 平台操作：Windows 10 Pro/Enterprise 版別與功能啟用、PowerShell
   - 檔案共享與網路：SMB/Share、Volume Mount 原理與常見問題
2. 核心概念：
   - Docker for Windows（Beta）原生整合：以 Hyper‑V 取代 VirtualBox，內建管理介面與自動更新
   - 背後架構：在 Windows 上以 Hyper‑V 啟動 Alpine Linux（MobyLinuxVM）承載 Docker Engine
   - Nested Hyper‑V：在 VM 內再開 VM 的先決條件、限制與實作
   - Volume 掛載（Shared Drives）：以共享磁碟方式將 Windows 路徑映射進容器
   - Windows Container 隔離模式：process 與 hyperv 兩種 isolation 及其使用情境
3. 技術依賴：
   - Docker for Windows → 依賴 Hyper‑V → 在其上啟動 MobyLinuxVM（Alpine Linux）→ Docker Engine
   - Volume 掛載 → 依賴 Windows Shared Drives（SMB）→ Docker Volume Driver → 容器內路徑
   - Nested Virtualization → 依賴最新版本 Hyper‑V 與 CPU VT‑x（Intel）→ 關閉動態記憶體等限制
   - Windows 容器隔離 → 依賴 Windows 10/Server 2016 的容器執行環境與 Docker CLI 的 --isolation 參數
4. 應用場景：
   - 開發環境在 Windows 桌機/筆電上直接使用 Docker（更快、更穩、更易更新）
   - 在不影響工作機的前提下，於 Hyper‑V VM 中體驗 Docker for Windows（隔離風險）
   - 需要將本機程式碼/資料直接映射給容器進行熱重載或資料持久化
   - 研究與測試 Windows Container 的隔離等級（process vs hyperv）
   - 多架構鏡像（x86/ARM）建置與測試的前置探索

### 學習路徑建議
1. 入門者路徑：
   - 了解容器基礎（Image/Container/Volume/Registry）
   - 安裝 Docker for Windows（啟用 Hyper‑V），以 hello-world 驗證
   - 使用 PowerShell/命令列執行 docker run、docker images、docker ps 基本指令
   - 設定 Shared Drives，完成本機資料夾到容器的 Volume 掛載
2. 進階者路徑：
   - 於 VM 中部署 Docker for Windows，實作 Nested Hyper‑V（含限制與疑難排解）
   - 深入 Volume 機制與 SMB 共享行為、效能與一致性
   - 實測多架構鏡像建置與運行（x86 為主，了解 ARM 方向）
   - 研究 Docker Desktop 設定、資源配額、更新與診斷
3. 實戰路徑：
   - 在 Windows 開發機上以 Compose 組合多容器開發環境，掛載本機程式碼
   - 規劃團隊標準化開發環境（同一版 Docker、同一組設定）
   - 導入 CI/CD：本機與遠端環境一致化，對接 Registry（Docker Hub）
   - 探索 Windows Container 與 --isolation=hyperv 的測試矩陣，為未來上線做準備

### 關鍵要點清單
- Docker for Windows 原生整合: 以 Hyper‑V 取代 VirtualBox，提供更穩定與自動更新體驗 (優先級: 高)
- MobyLinuxVM 架構: 在 Hyper‑V 上運行 Alpine Linux 作為 Docker Engine 宿主 (優先級: 高)
- Nested Virtualization 前提: 僅支援最新 Hyper‑V、需 Intel VT‑x，且有多項功能限制 (優先級: 高)
- 動態記憶體限制: 啟用 Nested 後需關閉 Dynamic Memory，並配置足夠 RAM（≥4GB） (優先級: 高)
- Hyper‑V 其他限制: 不能套用執行中檢查點、Save/Restore、Live Migration 等 (優先級: 中)
- 安裝需求: Windows 10 Pro/Enterprise（1511/10586+），先啟用 Hyper‑V 再安裝 Docker (優先級: 高)
- CLI 本機直用: 於 Windows 直接用 PowerShell/命令列操作 Docker，免 SSH 進 Linux VM (優先級: 高)
- Volume 掛載原理: 透過 Shared Drives（SMB 共享）把 Windows 路徑映射至容器 (優先級: 高)
- Shared Drives 設定: 未勾選磁碟時映射將退化為容器內部 Volume，無法對應到本機 (優先級: 高)
- Hello‑World 驗證: 安裝後以 hello-world 快速驗證整體鏈路可用性 (優先級: 中)
- 效能與穩定性: 捨棄 VirtualBox 帶來更佳效能與較少相容性問題 (優先級: 中)
- 多架構鏡像支持: 可建置/運行 Linux x86 與 ARM（Windows 端細節仍在演進） (優先級: 中)
- Windows Container 隔離: 透過 --isolation 指定 process 或 hyperv，視隔離需求選擇 (優先級: 高)
- 生態與整合: 與 Docker Hub、Docker Cloud、DevOps 流程的端到端串接 (優先級: 中)
- 風險隔離實務: 在上層 VM 中測試 Beta 版 Docker，避免動到工作機基礎設施 (優先級: 中)