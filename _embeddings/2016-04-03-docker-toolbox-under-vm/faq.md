# 如何在 VM 裡面使用 Docker Toolbox ?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 VM 中安裝 Docker Toolbox 時，VirtualBox 會顯示「VT-x / AMD-V 不支援」而無法啟動 Docker VM？
Docker Toolbox 內建的 VirtualBox 需要 CPU 暴露出 VT-x / AMD-V 的硬體虛擬化指令，才能在 Windows 裡再開一層 Linux VM 來跑 Docker。當作業系統本身已經是一台虛擬機（VM）時，預設並不會把這些指令「再向下一層」轉出，因此在 VM 裡啟動 VirtualBox 會失敗，造成 Docker Toolbox 初始化卡關。

## Q: 要在 Hyper-V 的虛擬機裡成功使用 Docker Toolbox，第一步應該做什麼？
必須先為該虛擬機開啟「Nested Virtualization」。具體條件與做法如下：
1. Host 與 Guest 皆需是 Windows 10/Windows Server 2016 Build 10565 以上版本。
2. 處理器必須支援 Intel VT-x，且建議配置 4 GB 以上 RAM。
3. 以系統管理員身份執行 PowerShell，下載並執行官方指令碼：
   ```
   Invoke-WebRequest https://raw.githubusercontent.com/Microsoft/Virtualization-Documentation/master/hyperv-tools/Nested/Enable-NestedVm.ps1 -OutFile ~/Enable-NestedVm.ps1
   ~/Enable-NestedVm.ps1 -VmName "<你的 VM 名稱>"
   ```
   這段指令會自動完成記憶體、MAC Spoofing 等必要設定，並啟用 Nested Virtualization 功能。

## Q: 若 VirtualBox 仍無法在 Nested Virtualization 中啟動，有沒有替代方案能在同一台 Windows VM 裡使用 Docker？
可以捨棄 VirtualBox，改用 Hyper-V 做為 Docker Machine 的驅動程式：
1. 解除安裝 VirtualBox，並在 Windows 功能中啟用 Hyper-V。
2. 於 Hyper-V 管理員中先建立好「Virtual Switch」，確保 Docker Host 能連網。
3. 使用 Docker Machine 建立 Docker Host：
   ```
   docker-machine create -d hyperv boot2docker
   ```
4. 執行
   ```
   docker-machine env boot2docker
   ```
   並依提示設定環境變數後，就能在 VM 內直接執行 `docker run hello-world` 等 Docker 指令，驗證 Docker 已運作無誤。