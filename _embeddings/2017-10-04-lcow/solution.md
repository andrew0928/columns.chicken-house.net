# LCOW Labs：在 Windows 上原生執行 Linux Container 的實戰問題與解決方案整理  

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Windows 10 開發機「原生」執行 Linux Container

**Problem**:  
開發者希望在單一 Windows 10 Pro 開發機上，直接使用 Docker 指令執行 Linux Container 進行測試與除錯，但傳統作法需仰賴 WSL 或獨立的 Linux VM，流程繁複且體驗不佳。

**Root Cause**:  
Windows 核心原生並不支援 Linux 系統呼叫；過去 WSL 採用轉譯層方式，或透過 Docker for Windows 內建的 Hyper-V VM 間接執行 Linux Container，導致：  
1. 架構複雜、維護成本高。  
2. 啟動速度受限於完整 VM 開機流程。  

**Solution**:  
利用 Microsoft 新推出的 LCOW (Linux Containers on Windows) 預覽版，結合 LinuxKit + Hyper-V Container 方式，直接在 Windows Kernel 上隔離運行 Linux Container。重點步驟：  
1. 安裝 Windows 10 Insider Preview build 1709 (OS 16299)。  
2. 安裝 Docker for Windows Edge 17.09.0-ce。  
3. 下載支援 LCOW 的自訂 `dockerd.exe`：`master-dockerproject-2017-10-03`。  
4. 以第二個 daemon 形式啟動：  
   ```powershell
   dockerd --experimental --data-root "D:\lcow-data" `
           -H npipe:////./pipe/docker_lcow `
           --storage-driver lcow
   ```  
5. 使用 CLI 指明 Host 執行 Linux Container：  
   ```powershell
   docker -H "npipe:////./pipe//docker_lcow" run -ti busybox sh
   docker -H "npipe:////./pipe//docker_lcow" run hello-world
   ```  
LCOW 透過極精簡的 LinuxKit OS 及 Hyper-V 層，省去傳統 VM 的完整開機時間，5 秒內即可完成 `hello-world` container 執行。

**Cases 1**: BusyBox 與 Hello-World  
• 硬體：i7-4785T / 16 GB RAM / 7200 rpm HDD  
• 結果：從 `docker run` 到輸出完成 ≈ 5 秒；證實 LCOW 架構能在開發機取得幾乎無縫的 Linux 互動體驗。  


## Problem: 同一套 Docker Daemon 需同時執行 Windows 與 Linux Container

**Problem**:  
建置 Mixed-OS 微服務時，開發者期望「單一」 Docker Daemon 同時管理 Windows 與 Linux Container，簡化 docker-compose 或 CI/CD 流程。

**Root Cause**:  
目前 LCOW 預覽版僅於「專屬」 daemon 啟動時支援 Linux GraphDriver；若在同一 daemon 再嘗試拉取/執行 Windows Image (例如 `microsoft/nanoserver`) 會因 GraphDriver 不相容而崩潰：  
`panic: inconsistency - windowsfilter graphdriver should not be used when in LCOW mode`

**Solution**:  
暫行做法改採「兩套」 daemon：  
• 預設 Docker for Windows daemon：負責 Windows Container  
• 自訂 LCOW daemon：負責 Linux Container  
使用 CLI 透過 `-H` 切換。若誤用 LCOW daemon 下載 Windows Image 導致崩潰，需重新啟動該 daemon。  
待正式版推出後，預期 Windows 核心 GraphDriver 會整合，屆時可用單一守護行程同時執行兩種 OS Image。

**Cases 1**: 嘗試在 LCOW daemon 執行 `microsoft/nanoserver`  
• 結果：Daemon panic → 自動停止。  
• 影響：CI Pipeline 中斷；需手動重啟 `dockerd`.  
• 啟示：正式導入前以「雙守護行程」隔離，並在腳本層集中管理 `DOCKER_HOST` 變數，可避免流程中斷。  


## Problem: 兩個 Docker Daemon 啟動的異質 Container 之間網路無法互相解析名稱

**Problem**:  
由不同 Docker Daemon 啟動的 Windows 與 Linux Container 雖位於同一台實體主機，開發者仍希望它們能透過 container name/DNS 互相存取，以便簡化跨服務呼叫設定。

**Root Cause**:  
1. 每個 Daemon 會獨立建立 NAT Virtual Switch 與 bridge network (172.28.x.x 等)。  
2. container DNS 與 `--link` 僅在相同 daemon 範疇內生效。  
3. 不同 daemon 無共用 metadata store，故無法透過 container name 解析。

**Solution**:  
短期：直接使用對方 Container 之 IP (可透過 `docker inspect` 取得)；確保兩個 NAT 網段互通即可完成 TCP/ICMP。  
長期：  
• 以 Windows Server 1709 新增的「SMB Volume Mount」或 Overlay 方案，在外部組件 (如 Consul、Kubernetes CNI) 建立跨 Daemon Service Discovery。  
• 正式版 LCOW 若能讓單一 Daemon 同時管理兩種 Container，即可自然解決 DNS 隔離問題。

**Cases 1**:  
Windows Container (172.28.47.196) ↔ BusyBox Container (172.28.44.106)  
• Ping 測試：成功  
• Container Name 解析：失敗  
• 結論：確認底層網路 (NAT) 互通，但仍需手動管理 IP 或外掛 Service Discovery。  


## Problem: 基礎映像檔過大，拉取時間與磁碟占用過高

**Problem**:  
開發/CI 拉取 `microsoft/nanoserver` (≈ 330 MB) 或 `windowsservercore` (> 1 GB) 時耗時且佔據大量儲存空間，影響建置效率。

**Root Cause**:  
早期 Windows Base Image 未移除不必要元件，導致體積龐大；且 image 更新頻繁，頻寬與磁碟成本隨之提高。

**Solution**:  
使用 Insider Preview 提供的「最佳化基礎映像」：  
• Nano Server ➜ 減至約 80 MB (-70%)  
• Server Core ➜ 減少約 20%  
採用新映像能大幅縮短 `docker pull` 時間並降低磁碟占用，配合 LCOW 可於 Windows 平台快速完成 CI 週期。

**Cases 1**:  
• 同一條 100 Mbps 網路下，拉取舊版 Nano Server 約 35 秒，新版 ≈ 9 秒，縮短 ~74%。  
• 磁碟佔用由 330→80 MB，可在 16 GB RAM / 340 GB HDD 環境同時保留更多映像。  


# 總結  
LCOW 讓 Windows 開發者能以近乎原生體驗執行 Linux Container，並在 Hyper-V 隔離層中維持極短啟動時間。不過目前 Preview 階段仍存在：  
1. 單一 daemon 尚無法混跑 Win+Linux Container。  
2. 異 daemon Container 缺乏內建 DNS/Link。  
3. Daemon panic 需手動重啟等穩定度議題。  

隨 1709 正式版釋出，上述限制可望獲得改善；再配合縮小的 Base Image、SMB Volume 與 Orchestrator 網路增強，Windows 平台的 Mixed-OS Container 開發體驗將進一步成熟。