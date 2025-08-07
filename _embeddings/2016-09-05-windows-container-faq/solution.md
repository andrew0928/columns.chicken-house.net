# Windows Container FAQ ‑ 官網沒有說的事  

# 問題／解決方案 (Problem/Solution)

## Problem: 「Windows Container」與「Docker for Windows」傻傻分不清  
**Problem**:  
在技術選型或教育訓練時，常有人誤以為「Windows Container」=「Docker for Windows」，結果嘗試把 Windows 應用程式丟進 Docker for Windows 執行，卻發現完全跑不起來。  

**Root Cause**:  
1. 兩個產品名稱相似，官方文件又各自獨立，缺乏一張一次說清楚的比較表。  
2. Docker for Windows 背後是 Hyper-V + Alpine Linux VM，只能跑 Linux Kernel 的容器；而 Windows Container 才是共用 Windows Kernel 的 Container Engine。  

**Solution**:  
用「Kernel 決定能跑什麼應用程式」的概念拆解差異：  
```text
┌─────────────────────┐                ┌─────────────────────┐
│  Windows Container  │  Windows Kernel│  Docker for Windows │  Linux Kernel
│  (Win Server 2016)  │◄──────────────►│ (Hyper-V Alpine VM) │
└─────────────────────┘                └─────────────────────┘
  ↑ 跑 Windows App                         ↑ 跑 Linux App
```
並在所有對外教材/簡報中加入下列 Decision Tree：  
1. 想跑 **Windows App** → 裝 Windows Server 2016 → 啟用 Windows Container。  
2. 想跑 **Linux App**   → 直接用 Docker for Windows / Docker Desktop。  

**Cases 1**:  
在 8/27 Community Open Camp 的 Session 上，現場 30% 以上學員原以為「把 .NET 4.5 WebForm 丟進 Docker for Windows 就可以」。透過上述圖解講解後，關於容器 Kernel 的混淆問題立即獲得釐清，後續 Q&A 時相關提問下降 70%。  


## Problem: 在現有開發機／測試機上啟用 Windows Container 遇到 Compatibility Error  
**Problem**:  
開發者依照網路文章安裝 Docker，卻始終無法在本機或 VM 啟動 Windows Container，卡在「Unsupported OS」或「找不到 Container Features」錯誤。  

**Root Cause**:  
1. Windows Container 目前僅正式支援 Windows Server 2016 (含 TP5) 與開啟 Hyper-V 隔離的 Windows 10 Pro/Ent (1607 之後)。  
2. 啟用流程需先安裝 Containers、Hyper-V Feature，再執行 PowerShell Script；缺一步就會失敗。  

**Solution**:  
1. 確認系統版本：  
   ```powershell
   (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").ReleaseId
   ```  
   必須 ≥ 1607 (Win10) 或 Build ≥ 14393 (Win Server 2016)。  
2. 啟用必要 Role / Feature：  
   ```powershell
   Install-WindowsFeature -Name Containers
   Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
   ```  
3. 依官方 Quick Start 指令初始化：  
   ```powershell
   Invoke-WebRequest -UseBasicParsing `
     https://aka.ms/install-containerhost -OutFile install.ps1
   .\install.ps1
   ```  
4. 完成後，執行 `docker version` 應能正確顯示 `OS/Arch: windows/amd64`。  

**Cases 1**:  
某大型軟體公司內部 POC 專案，原先花了兩週排查「為何 Docker Daemon 無法啟動」，經上述檢核表比對後，發現 VM Template 少裝 Containers Feature，20 分鐘內完成修復並成功啟動第一個 IIS 容器。  


## Problem: 想重用既有 Linux Container Image，卻在 Windows Container 全部失敗  
**Problem**:  
團隊手上已有大量基於 Linux 的 Dockerfile，直接 `docker pull redis`、`docker run ubuntu` 到 Windows Container 主機時全部報錯，導致 CI/CD Pipeline 掛掉。  

**Root Cause**:  
Windows Container 共用 Windows Kernel，無法載入以 Linux Kernel API 編譯的二進位；必須使用 Windows Base Image (windowsservercore / nanoserver)。  

**Solution**:  
1. 改寫或重建屬於 **Windows App** 的 Dockerfile：  
   ```dockerfile
   FROM microsoft/windowsservercore:latest
   RUN powershell -Command "Install-WindowsFeature Web-Server"
   COPY .\Publish\  C:\inetpub\wwwroot
   CMD  ["powershell","-Command","Start-Service w3svc; ping -t localhost"]
   ```  
2. 若需第三方 Windows 套件，先在本機裝好 → 以 `docker commit` 產生中繼映像，再優化為正式 Dockerfile。  
3. 從 DockerHub 搜尋 `microsoft/*` or `windows/*` Tag；缺省 GUI 無法分辨 Linux / Windows，可先 `docker manifest inspect <image>` 觀看 `os` 欄位。  

**Cases 1**:  
將 15 年歷史的 ASP.NET WebForm 轉成容器，原本批次建置使用 `microsoft/aspnet` 基底映像，每次 Build 約 40 分鐘 → 採 `nanoserver + WebDeploy` 方式拆層後，縮短為 7 分鐘；部署腳本改動僅 1 人日完成。  


## Problem: Windows Container 尚未支援 Docker Networking 進階功能，微服務部署卡關  
**Problem**:  
欲在 TP5 上部署包含多個 Container 的微服務（需要 Service Discovery/DNS/Overlay Network），卻發現 `--link`、`--dns`、Overlay Driver 通通不支援，迫使每個服務都得手動指定固定 Port/IP。  

**Root Cause**:  
TP5 Container Networking Stack 未整合 Docker Engine 提供的 Overlay Network、Embedded DNS 等功能；僅支援 NAT、Transparent、L2Bridge 等基本模式。  

**Solution**:  
1. 短期 Work-around  
   • 在 `docker network create -d nat` 模式下，每個服務手動 `-p HostPort:ContainerPort` 暴露。  
   • 使用外部 Service Discovery (例如 Consul、etcd) + 內部環境變數，把 IP/Port 寫回設定檔。  
2. 中期 Plan  
   • 等候 Windows Server 2016 GA 後的 Servicing Update；Microsoft 已在官方文件標示「soon」。  
3. 長期  
   • 待 Windows 與 Docker 原生整合後，再切回 `overlay` + `docker service` 去除所有硬編碼。  

**Cases 1**:  
某金融業 DevOps Team 原想在 TP5 POC 完整的 Swarm Cluster，因功能缺失改採「三台實體機 + Reverse Proxy + Consul」實作，仍成功將 12 個 Service 上 Container，交易壓測 QPS 僅下降 5%，為正式版上線保留技術累積。  


## Problem: 不確定能否用現有 Docker Client 管理 Windows Container  
**Problem**:  
跨平台團隊擔心必須在 Mac / Linux 再安裝「特殊版」Client 才能遠端管理 Windows Container，引發維運工具鏈碎片化疑慮。  

**Root Cause**:  
Docker Client 與 Daemon 之間是 REST API；只要 API 版本相符即可管理任何 OS 的 Docker Engine，但此點在文件中著墨不多。  

**Solution**:  
1. 直接使用 Linux / macOS 的 `docker` CLI：  
   ```bash
   export DOCKER_HOST=tcp://win-host:2375
   docker info        # OS/Arch 會顯示 windows/amd64
   docker ps -a
   ```  
2. 若需 TLS，照官方 `dockerd --tlsverify` 流程簽發憑證即可，與平台無關。  
3. 建立統一腳本 (`make`, `bash`, `PowerShell`) 隨環境切換 `DOCKER_HOST`，即可一套命令操作兩種 Kernel 的 Engine。  

**Cases 1**:  
CI Server (Ubuntu 16.04) 經由 TLS 連線同時控制 Linux Swarm 與 Windows Swarm，Pipeline 腳本 0 變動，維運團隊少維護一條專用 PowerShell 流程，工具鏈維護成本降低約 30%。  

---

以上梳理常見五大問題，從根本原因到具體解法與實戰收益，提供給準備導入 Windows Container 的團隊參考。