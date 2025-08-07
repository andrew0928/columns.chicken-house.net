# 如何在 VM 裡面使用 Docker Toolbox ?

## 摘要提示
- VM 內再開 VM: VirtualBox 無法在第二層 VM 取得 VT-x，導致 Docker Toolbox 建立失敗。  
- Nested Virtualization: Windows 10／Server 2016 新增巢狀虛擬化，可讓 Guest OS 再跑 Hyper-V。  
- 系統需求: Intel VT-x、4GB RAM 以上、Windows Build 10565+，且僅供測試環境使用。  
- 啟用方式: 以 PowerShell 執行 Enable-NestedVm.ps1，對指定 VM 開巢狀功能。  
- VirtualBox 失敗: 即使巢狀啟用，VirtualBox 仍因相容性問題無法開機。  
- Docker Machine 出場: 改用 docker-machine 的 Hyper-V driver，在 Guest 內直接建立 boot2docker VM。  
- 網路設定: 須先於 Hyper-V 建立 Virtual Switch，確保 Docker Host 可對外。  
- 操作流程: docker-machine create -d hyperv boot2docker → docker-machine env 設定環境變數。  
- 成功驗證: 執行 docker run hello-world 下載並跑起 Container，證明可行。  
- Kitematic 調整: GUI 預設綁 VirtualBox，需手動修改才能配合 Hyper-V。

## 全文重點
本文原為解答「如何在 Hyper-V 虛擬機裡使用 Docker Toolbox」的臨時筆記。Docker Toolbox 內建 VirtualBox，用來在 Windows 上建立一台跑 Docker 的 Linux VM；然而一旦 Toolbox 安裝在 Hyper-V 的客體作業系統中，就會因為第二層 VirtualBox 取不到 VT-x 而失敗。解決之道是利用 Windows 10／Server 2016 開始提供的 Nested Virtualization，讓第一層 Hyper-V 能把硬體虛擬化指令向下透通給第二層。  
啟用巢狀功能前必須確認主機具備 Intel VT-x、4GB 以上記憶體，且 OS 版本高於 10565。完成後在 Host 執行官方 PowerShell 腳本 Enable-NestedVm.ps1，針對目標 VM 開啟 nested，並依指示調整記憶體、MAC Spoofing 等設定。  
啟用後雖可在 Guest 中順利安裝 Docker Toolbox，但實測顯示 VirtualBox 仍因相容性缺陷無法開機。因此作者改走另一條路：保留 Toolbox 其他元件，只捨棄 VirtualBox，改用 docker-machine 的 Hyper-V Driver。步驟為：  
1. 解除安裝 VirtualBox，啟用 Guest 內的 Hyper-V。  
2. 於 Hyper-V 建立外部 Virtual Switch。  
3. 在命令列執行 `docker-machine create -d hyperv boot2docker`，數分鐘後即生成一台裝有 boot2docker 的 Linux VM。  
4. 使用 `docker-machine env boot2docker` 匯入環境變數，讓 Windows 端的 Docker Client 指向新 VM。  
5. 以 `docker run hello-world` 驗證，可見映像拉取並成功執行。  
若仍想使用圖形化的 Kitematic，需依網路文章修改其預設的 VirtualBox 呼叫邏輯，改指向 Hyper-V。整體而言，透過 Hyper-V 巢狀虛擬化與 docker-machine 的彈性 Driver，便能在任何支援 Hyper-V 的 VM 內部順利體驗 Docker 全套工具。

## 段落重點
### 關鍵問題：無法在 VM 裡面建立 VM
Docker Toolbox 仰賴 VirtualBox 先啟動一台 Linux，才能跑 Container；但在已經被虛擬化的環境中，第二層 VirtualBox 取不到硬體層 VT-x/AMD-V，導致安裝流程卡關，形成「VM 中開 VM」的技術瓶頸。

### Nested Virtualization Support
Windows 10 / Server 2016 提供 Nested Virtualization，Hyper-V 會把虛擬化指令集暴露給來賓 OS，讓其內部再啟一層 Hypervisor。雖仍屬 Preview，效能與相容性未知，卻是突破上述瓶頸的關鍵。

### 替 VM 啟用 Nested Virtualization 的支援
官方腳本 Enable-NestedVm.ps1 可一次檢查並設定需求：記憶體須 ≥4 GB、啟用 MAC Spoofing、關閉 Dynamic Memory 與 Checkpoints，最後為指定 VM 打開 nested，前提是 Host 與 Guest 系統皆為 Build 10565 以上且使用 Intel CPU。

### 安裝 Docker Toolbox、準備 Docker Host VM
在開啟 nested 的 Guest OS 內安裝 Docker Toolbox，初步初始化可通過，但真正啟動 VirtualBox VM 時仍報錯，顯示 VirtualBox 與 Hyper-V 巢狀環境不相容。多次重試仍告失敗，決定放棄 VirtualBox 改用 Hyper-V。

### Docker Machine
Docker Machine 提供多種 Driver，可在不同平台自動建置 boot2docker VM。先移除 VirtualBox、啟用 Hyper-V、設定 Virtual Switch，再執行 `docker-machine create -d hyperv boot2docker`。建置完成後用 `docker-machine env` 匯入環境變數，Docker Client 即能遠端操控該 VM。hello-world 容器測試成功，證明方案可行；若要使用 Kitematic，需手動改寫其呼叫機制以支援 Hyper-V。