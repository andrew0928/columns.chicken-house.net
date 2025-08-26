# LCOW Labs: Linux Container On Windows

## 摘要提示
- LCOW 定義: 以 Hyper-V Container 搭配 LinuxKit/Ubuntu 取代容器內的 OS，讓 Windows 原生執行 Linux Container。
- 與 WSL 的關係: 秋季更新後 LCOW 將取代 WSL，提供更精簡、相容性更佳的 Linux 執行途徑。
- 測試平台: 使用 Windows 10 Pro Insider Preview 1709、Docker for Windows Edge 17.09.0-ce 與額外 LCOW 支援的 daemon。
- 操作方式: 維持一般 Docker CLI 流程，但需以 -H 指向 LCOW 專用的 docker daemon 管道。
- LAB1 成果: BusyBox 與 hello-world 成功啟動，體驗到 Hyper-V Container + LinuxKit 的快速啟動（約 5 秒）。
- LAB2 限制: 嘗試在 LCOW daemon 上跑 Windows Container 失敗，出現 windowsfilter 與 LCOW 模式衝突的 panic。
- LAB3 網路: 不同 daemon 啟動的 Windows/Linux 容器可互 ping，同步發現無法跨 daemon 使用 link/DNS。
- 基礎映像改進: Nano Server、Server Core 體積大幅縮減（Nano 約降至 80MB），.NET Core/PowerShell 提供預覽映像。
- Volume 與生態: 新增 SMB volume 掛載、Named pipe 映射、Kubernetes/Swarm 網路強化與 orchestrator 基礎建設。
- 實務展望: 混合 OS 架構在單機開發與生產可行性提升，待正式版整合同一 daemon 後體驗將更完整。

## 全文重點
本文以實驗角度介紹 LCOW（Linux Containers on Windows）：在 Windows 容器架構下，將 Hyper-V Container 的來賓 OS 從 Nano Server 改為 LinuxKit（或 Ubuntu），使 Windows 能以近乎原生的方式執行 Linux 容器。相較過去 WSL 透過轉譯系統呼叫的方式來跑 Linux 應用，LCOW 以更精簡、相容性更好的方法同時擴及 Linux Container 支援，並預計在秋季更新後取代 WSL 成為主要路徑。

作者使用 Windows 10 Pro Insider Preview 1709，搭配 Docker for Windows Edge 17.09.0-ce 作為預設 daemon，另從 GitHub 取得支援 LCOW 的 docker daemon（master-dockerproject-2017-10-03）。因目前測試版尚不支援同一 daemon 同時跑 Windows 與 LCOW，需以 -H 指向 LCOW daemon 來操作。環境就緒後以 LCOW daemon 成功運行 BusyBox 和 hello-world，並以影片展示 Hyper-V Container + LinuxKit 的啟動速度，於非頂級硬體上仍能在約五秒內完成啟動與結束，顯示體驗順暢。

為驗證混合 OS 並存與開發便利性，作者嘗試用同一 LCOW daemon 直接運行 Windows Container（Nano Server）。結果下載映像後出現「windowsfilter graphdriver 不應在 LCOW 模式使用」的 panic，daemon 也因此中止，顯示此時期版本不支援該情境，若要繼續測試需重啟 LCOW daemon。接著作者測試跨 daemon 網路：在預設 daemon 跑 Windows Container，在 LCOW daemon 跑 Linux BusyBox，兩者各分配到不同子網但可互 ping；然而因屬不同 daemon，docker ps 無法互見，也無法使用 --link 或內建 DNS 解析彼此名稱，需以 IP 溝通或另行規劃跨 daemon 名稱解析。

最後整理 2017/10 更新中與 Windows 容器相關的改進：Nano Server 與 Server Core 基礎映像大幅縮小，.NET Core 2.0 與 PowerShell 6.0 預覽映像釋出；新增 SMB volume 掛載、Named pipe 映射；持續強化對 orchestrators 的基礎（含 Kubernetes 網路增強）。這些變更對推進 Windows Container 進入生產環境相當關鍵。作者原計畫以 docker-compose 進行 Linux NGINX + Windows ASP.NET MVC 的混合範例，但因尚未在同一 daemon 維持混合容器，暫緩至正式版釋出後再驗證。整體而言，LCOW 明顯縮短了 Windows 與 Linux 的距離，為混合 OS 的單機開發與未來上線鋪路。

## 段落重點
### 準備測試環境
作者以 Windows 10 Pro Insider Preview 1709（Build 16299.0）作為測試平台，安裝 Docker for Windows Edge 17.09.0-ce 作為預設 daemon，同時從 GitHub 取得支援 LCOW 的 docker daemon（master-dockerproject-2017-10-03）。由於當前預覽版不支援同一 daemon 同時啟用 LCOW 與 Windows Container，需透過 -H 指定到名為 npipe:////./pipe//docker_lcow 的管道來連線 LCOW daemon。兩個 daemon 各自維護獨立容器清單，操作上需留意切換端點。本文也對 LCOW 的原理進行說明：利用 Hyper-V Container 將容器的基底 OS 替換為 LinuxKit/Ubuntu，以達在 Windows 環境原生執行 Linux 容器之目的，並指出 LCOW 將在秋季更新後取代 WSL，提供更精簡而相容性更佳的 Linux 支援。

### LAB1, Run BusyBox / Hello-World
在 LCOW daemon 上運行 busybox sh 與 hello-world，二者皆能順利啟動，證實 LCOW 能以熟悉的 Docker 用法在 Windows 啟動 Linux 應用。作者以影片展示其啟動速度：透過 Docker -> Hyper-V Container -> LinuxKit 的鏈結，在非高階硬體（i7-4785T、16GB RAM、老款 2.5 吋 7200rpm HDD）上，約 5 秒內完成 hello-world 的啟動與結束。此結果突顯 LCOW 在體驗層面與效率上的優勢，讓在 Windows 上快速試跑 Linux 應用變得實用且輕量，對開發者尤具吸引力。

### LAB 2, Run Windows Container with LCOW
作者嘗試利用同一支援 LCOW 的 docker daemon 直接運行 Windows 容器（microsoft/nanoserver:latest + cmd.exe），於拉取映像後遭遇錯誤並觸發 panic，訊息指示「windowsfilter graphdriver 不應在 LCOW 模式使用」。此結果顯示該預覽階段不支援在 LCOW 模式下執行 Windows Container，亦即暫時無法達成單一 LCOW daemon 同時運行 Windows 與 Linux 容器的目標。此外，一旦出現此錯誤，LCOW daemon 會中止運行，要繼續測試必須重新啟動 daemon。這段經驗提醒使用者在預覽期需分別以不同 daemon 執行不同 OS 的容器，並避免跨用途混用以致不穩定。

### LAB 3, Networking
作者分別在預設 daemon 啟動 Windows Container（windowsservercore + cmd.exe），另一邊在 LCOW daemon 啟動 BusyBox。兩者雖位於不同 daemon、各自網段，但均獲得 172.28.x.x 的位址並可互相 ping 通，證明在 Hyper-V 虛擬網路下跨 daemon 的容器仍可能互通。然而由於兩者不屬同一 daemon，互查 docker ps 無法看到對方容器，亦無法使用 --link 或內建 DNS 對等名稱解析，只能以 IP 直連或另行設計服務發現機制。作者以影片示範整體流程，指出雖然基本網通可行，但若要建立以名稱解析為基礎的跨容器協作，仍需等待單一 daemon 混合支援或採用額外網路/服務發現方案。

### 小結
作者原欲以 docker-compose 實作混合 OS 架構（Linux 上跑 NGINX，Windows 上跑 ASP.NET MVC），但因尚未能在同一 daemon 同時運行兩種容器而暫緩。文末整理 2017/10 的 Windows 容器改進：Nano Server 與 Server Core 映像大幅縮減（Nano 約 80MB）、提供 .NET Core 2.0 與 PowerShell 6.0 預覽映像、支援 SMB volume 掛載與 Named pipe 映射，以及強化 orchestrators（含 Kubernetes）網路功能。這些更新有助於推進 Windows Container 走向生產環境。作者對 LCOW 的前景持樂觀態度，預期正式版釋出後可進一步驗證在單一開發機無縫運行混合 OS 架構的可行性，並承諾後續分享更多實測心得。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 Docker 概念（Client/Daemon、Image、Container、Registry）
   - Windows 容器基礎（Windows Containers、Hyper-V Containers、Windows 网络/虚拟交换机）
   - 虚拟化與 Hyper-V 基本概念
   - 基本 Linux 指令與容器操作（busybox、hello-world）
   - Windows 10/Server Insider/17.09 時期的 Docker for Windows 安裝與切換（Linux/Windows container）

2. 核心概念：
   - LCOW（Linux Containers on Windows）：在 Windows 上透過 Hyper-V Container 啟動一個極簡 Linux（LinuxKit/Ubuntu）以原生執行 Linux Containers
   - 多 Docker Daemon 並存：預設 Docker for Windows 的 daemon 與額外啟動的 LCOW 專用 daemon（需以 -H 指定連線）
   - Hyper-V Container 與 LinuxKit：每個容器對應極簡 VM + 極簡 OS，快速啟動與隔離
   - Mixed-OS 開發體驗：同一台 Windows 開發機同時操作 Windows 與 Linux 容器（雖然當時同一 daemon 尚未同時支援）
   - Windows 容器生態改進：更小的基底映像、SMB volume、命名管道映射、對編排器與網路的增強

3. 技術依賴：
   - LCOW 依賴 Hyper-V 支援 + LinuxKit 影像
   - LCOW 專用 docker daemon（支援 API 1.34）與 Docker Client（可同時連不同 daemon）
   - Windows 版本（Insider/1709 以上）與 Docker for Windows Edge 版本
   - 容器網路互通依賴主機虛擬網路設定；不同 daemon 間無共享控制面（無法直接使用 --link/DNS）

4. 應用場景：
   - Windows 開發機原生運行 Linux 容器（無需獨立 Linux 主機）
   - Mixed-OS 架構開發與測試（如 NGINX on Linux + ASP.NET on Windows）
   - 快速驗證/教學示範（hello-world、busybox）
   - 企業內部以 SMB 分享目錄掛載至容器（資料/設定/日誌共享）
   - 向生產編排（Swarm/Kubernetes）過渡的先期試驗與網路測試

### 學習路徑建議
1. 入門者路徑：
   - 安裝 Docker for Windows（啟用 Hyper-V）
   - 熟悉 docker 基本指令（pull/run/ps/logs/images）
   - 使用預設 daemon 跑 hello-world（Linux 或 Windows 模式）
   - 了解如何切換/指定 daemon：docker -H "npipe:////./pipe//docker_lcow"
   - 以 LCOW daemon 运行 busybox/hello-world，體驗啟動速度

2. 進階者路徑：
   - 同機管理多個 daemon 與環境變數/contexts（或以 -H 明確指定）
   - 分析 daemon logs，理解 graphdriver、API 版本相容性
   - 測試容器網路（跨 daemon 互 ping、理解為何 DNS/--link 不可用）
   - 探索 Windows 容器基底映像（Nano Server/Server Core）與映像大小差異
   - 實作 SMB volume 掛載、命名管道映射，驗證 I/O 與權限

3. 實戰路徑：
   - 建立 Mixed-OS 範例：Linux NGINX 反向代理 + Windows ASP.NET App（以兩個 daemon 或等待單一 daemon 支援）
   - 撰寫 docker-compose（先分環境運行，或以多 context/多 daemon 規劃）
   - 加入 CI/CD：針對 Windows/Linux 映像分開建置與推送
   - 模擬編排器部署前的網路與存儲策略（SMB 卷、虛擬網段）
   - 監控與效能：記錄啟動時間、資源占用，驗證 Hyper-V 隔離對效能的影響

### 關鍵要點清單
- LCOW 基本原理: 以 Hyper-V Container 啟動極簡 Linux 環境，在 Windows 上原生執行 Linux 容器 (優先級: 高)
- 多 daemon 管理: 預設 Docker for Windows daemon 與 LCOW daemon 並存，需以 -H 指定目標 (優先級: 高)
- API/版本相容性: LCOW daemon 使用較新 API（例如 1.34），Client 與 Server 版本需匹配 (優先級: 高)
- LinuxKit 角色: 作為容器執行所需的最小 Linux OS，提供快速啟動與隔離 (優先級: 中)
- Hyper-V 依賴: LCOW 需啟用 Hyper-V，容器本質為輕量 VM 隔離 (優先級: 高)
- 同一 daemon 的限制: 當時 LCOW 測試版無法在同一 daemon 同時支援 Windows 與 Linux 容器 (優先級: 高)
- 跨 daemon 網路: 不同 daemon 建立的容器可互 ping，但無共享控制面，無法用 --link/DNS 解析 (優先級: 中)
- 故障排查: 嘗試用 LCOW daemon 跑 Windows 映像會觸發 graphdriver 錯誤（windowsfilter 不應在 LCOW 模式使用） (優先級: 高)
- 啟動效能: 透過 Hyper-V + LinuxKit 的 Linux 容器啟動可達數秒級，體驗接近原生 (優先級: 中)
- 基底映像優化: Nano Server/Server Core 顯著縮小（Nano 約 80MB），加快拉取與佈署 (優先級: 中)
- SMB 卷掛載: Windows 容器開始支援直接掛載 SMB 共享，改善資料與設定管理 (優先級: 高)
- 命名管道映射: 增進 Windows 容器與主機/服務之間的整合能力 (優先級: 中)
- 編排支援: 對 Swarm/Kubernetes 的網路與基礎能力持續增強，利於生產落地 (優先級: 中)
- WSL 與 LCOW 取代趨勢: LCOW 以更簡潔架構與更佳相容性取代早期 WSL 使用情境（歷史背景） (優先級: 低)
- 實戰建議: 規劃 Mixed-OS 開發流程、使用多 context/多 daemon、結合 CI/CD 與存儲/網路策略 (優先級: 高)