```markdown
# 專為 Windows 量身訂做的 Docker for Windows (Beta) !

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Windows 桌面／筆電上使用 Docker 體驗糟糕，與 Hyper-V 衝突

**Problem**:  
開發者想在 Windows 端直接跑 Docker 做日常開發，但過去只能依賴「Docker Toolbox＋VirtualBox」。  
1. VirtualBox 與 Windows 內建 Hyper-V 只能擇一，常需要來回切換或重開機。  
2. VM 與 Host 幾乎沒有整合，效能差、操作繁雜。  
3. 對不熟 Linux 的 .NET／Windows 工程師門檻極高。  

**Root Cause**:  
Toolbox 採用 VirtualBox 做 Hypervisor，與 Hyper-V 互斥；Boot2Docker ISO 又缺乏與 NTFS、網路、Credential 的整合，造成「必須自己管 VM + 自行 SSH」的體驗落差。  

**Solution**:  
Docker for Windows (Beta) 改以 Hyper-V 為唯一 Hypervisor，安裝時自動建一台「MobyLinuxVM (Alpine+BusyBox)」，並把 Docker CLI / Compose / Machine 以原生 MSI 裝到 Windows：  
• 消除 Hypervisor 衝突 → 不必再卸載 VirtualBox  
• VM 由 Docker Desktop Service 接管 → 開機即啟，整合托盤更新  
• Alpine 體積小、啟動快 → 開發迴圈縮短  

**Cases 1**:  
作者在 Win10 Enterprise Host 上安裝 Beta，無需安裝 VirtualBox 即能 `docker run hello-world`，啟動時間及 CPU/RAM 佔用均優於舊流程。  

**Cases 2**:  
同一台機器可並行執行 Hyper-V Android Emulator 與其他 VM，不再因 VirtualBox 衝突被迫重開機。  

---

## Problem: 想在「VM 裡」體驗 Docker for Windows，MobyLinuxVM 卻起不來

**Problem**:  
為避免在實體機安裝 Beta，團隊把 Win10 VM (稱 WIN10) 跑在 Hyper-V Host (稱 CHICKEN-PC) 裡測試 Docker Desktop。一安裝就收到「Cannot start MobyLinuxVM」錯誤，無法啟動 Docker。  

**Root Cause**:  
Docker Desktop 需在本地 Hyper-V 再開一層 Linux VM。VM 內要再開 VM，必須啟用「Nested Virtualization」。預設關閉，且須：  
• Intel VT-x；  
• 關閉 Dynamic Memory；  
• `Set-VMProcessor -ExposeVirtualizationExtensions $true`；  
• 至少 4 GB RAM。  
文件分散又是 Preview 功能，易漏設定。  

**Solution**:  
1. 在實體 Host 用 PowerShell 啟用 Nested：  

   ```powershell
   Set-VMProcessor -VMName WIN10 -ExposeVirtualizationExtensions $true
   ```  
2. 關閉 WIN10 VM 的 Dynamic Memory，固定 4 GB+ RAM。  
3. 重新開機 WIN10，安裝 Docker for Windows，即可順利建立 MobyLinuxVM。  

**Cases 1**:  
作者按上述設定完成 nested，WIN10 VM 成功 `docker run hello-world`，驗證「VM in VM」鏈路可行。  

**Cases 2**:  
Nested 後 WIN10 仍可跑 VS Android Emulator（亦用 Hyper-V），證實設定不影響其他工作負載。  

---

## Problem: Container 要存取 Host 檔案，只能繞 Samba／CIFS，效能差又難維護

**Problem**:  
開發時常需把本機原始碼或資料夾掛進 Container。以往作法：  
1. Windows 把資料夾設成 File Share，Linux VM 用 CIFS mount；或  
2. Linux VM 開 Samba，Windows 用網芳連。  
流程繁瑣、路徑易錯，且等於「在本機磁碟上走一圈 TCP/IP」，IO 效能差。  

**Root Cause**:  
早期 Boot2Docker 缺乏能直接存取 NTFS 的 Volume Driver，只能用網路檔案協定轉一手。  

**Solution**:  
Docker Desktop 新增「Shared Drives」設定：  
1. 在 Settings 勾選要共享的磁碟 (C:\ / D:\ …)。  
2. Docker Desktop 透過內建 Volume Driver 把該磁碟自動掛進 MobyLinuxVM。  
3. 容器內直接使用：  

   ```bash
   docker run -v C:\code:/data myimage
   ```  
無需再手動設定 Samba 或 CIFS。  

**Cases 1**:  
作者在 `C:\Users\chicken\Docker\apline-data` 放 `readme.txt`，勾選 C:\ 為 Shared Drive 後，容器內 `/data` 即可即時讀到該檔案；在容器裡新增 `aplinux-version.txt`，Windows File Explorer 也立刻看到。  

**Cases 2**:  
取消勾選 Shared Drive 後重建容器，掛載立即失效，驗證磁碟級權限控制可依需要開關。  

---

## Problem: Namespace 隔離仍共用核心，部份高安全場景需更強隔離

**Problem**:  
多租戶 SaaS 或需滿足嚴格安全／合規的工作負載，擔心單純 Process Namespace 隔離不足，仍可能因共用宿主 Kernel 被突破。  

**Root Cause**:  
傳統 Linux / Windows Server Containers 都與宿主共用 Kernel；Docker 原生缺乏 Kernel-level 隔離能力。  

**Solution**:  
Microsoft 與 Docker 合作，於 Windows 提供 `--isolation=hyperv`：  
• 為每個 Container 啟動極輕量 Hyper-V VM (Hyper-V Container)，提供 Kernel 隔離；  
• 與現有 Docker CLI / Image Workflow 完全相容；  
• 讓使用者可在 `process` 與 `hyperv` 隔離模式間彈性切換。  

**Cases 1** (官方文件範例):  

```bash
docker run -it --isolation=hyperv mcr.microsoft.com/windows/nanoserver:latest cmd
```  

開啟後 `docker inspect` 可看到獨立 VHDX，證實已啟用 Kernel 隔離，可用於多租戶高安全需求。

```