# 如何在 VM 裡面使用 Docker Toolbox ?

# 問題／解決方案 (Problem/Solution)

## Problem: 在既有的 Windows VM 內無法使用 Docker Toolbox

**Problem**:  
在公司筆電或雲端已經架好的 Windows VM 內，想直接安裝 Docker Toolbox 進行容器實驗；然而一執行 `Docker Quickstart Terminal` 就失敗，VirtualBox 提示「VT-x/AMD-V 不可用」。

**Root Cause**:  
1. Docker Toolbox 會透過 Oracle VirtualBox 再建立一層 Linux VM（boot2docker）作為 Docker Host。  
2. 一般 VM 的 vCPU 不會再向下暴露硬體虛擬化指令集（VT-x/AMD-V），導致「VM 裡再開 VM」失敗。

**Solution**:  
1. 改用 Windows 10 / Windows Server 2016 提供的 Nested Virtualization。  
2. 在實體機 (Level-0) 上：  
   - 確認 OS 版本 ≥ Build 10565，CPU 支援 Intel VT-x，並預留 ≥4 GB RAM。  
   - 下載並執行官方 PowerShell 腳本 `Enable-NestedVm.ps1 -VmName "<你的 VM 名稱>"`，為目標 VM 打開 Nested Virtualization。  
3. 重新開機後，VM 內即可偵測到 VT-x，VirtualBox 能順利完成 boot2docker 初始化。  

**Cases 1**:  
在 Intel i7-2600K / 24 GB RAM 的桌機上為名為 “WIN10” 的 Lab VM 啟用 Nested Virtualization，Docker Toolbox 初始化不再出現 “VT-x 不可用” 的錯誤，成功建立 boot2docker VM，驗證 VM in VM 的可行性。

---

## Problem: 開啟 Nested Virtualization 後，VirtualBox 仍無法啟動內層 Linux VM

**Problem**:  
Nested Virtualization 成功啟用後，Docker Toolbox 仍在「啟動 boot2docker」階段卡死，VirtualBox GUI 直接報錯，無法點選「啟動」。

**Root Cause**:  
Nested Virtualization 仍屬 Preview，Hyper-V 與 VirtualBox 低層 Hypervisor 互相衝突；二者同時載入時，VirtualBox 對硬體虛擬化指令的呼叫仍會失敗。

**Solution**:  
1. 捨棄 VirtualBox，改用 Hyper-V 當內層 Hypervisor。  
2. 步驟：  
   a. 在 VM 內解除安裝 VirtualBox，啟用 Hyper-V 功能並重開。  
   b. 於 Hyper-V Manager 新增外部 Virtual Switch，供內層 Docker Host 使用。  
   c. 打開 CMD/Powershell：  
      ```bash
      docker-machine create -d hyperv boot2docker
      docker-machine env boot2docker | Invoke-Expression   # 設定環境變數
      ```  
   d. 測試 `docker run hello-world`，確認 CLI 能連到新建的 boot2docker Host。  
3. 關鍵思路：Docker Machine 提供多種 driver；只要把 `-d virtualbox` 換成 `-d hyperv`，就能避開 VirtualBox 與 Hyper-V 的衝突。

**Cases 1**:  
改用 `docker-machine -d hyperv` 後，2 分鐘內完成 boot2docker VM 佈署；`docker run hello-world` 成功抓取映像並輸出訊息，證實容器可在「第二層」Hyper-V VM 中執行。

---

## Problem: 移除 VirtualBox 後，Docker GUI 工具 Kitematic 無法使用

**Problem**:  
為了相容性移除 VirtualBox 之後，Kitematic 一開啟就尋找 VirtualBox，導致 GUI 失效，無法用圖形介面下載／啟動容器。

**Root Cause**:  
Kitematic Windows 版在程式碼中硬性呼叫 `docker-machine create -d virtualbox`，未提供 Hyper-V 選項，當 VirtualBox 不存在時即閃退。

**Solution**:  
1. 參考社群文章《Modifying Kitematic to run on Windows 10 with Hyper-V》：  
   - fork Kitematic 或直接修改 `%AppData%\Kitematic\engine\docker-machine.js`，把預設 driver 改為 `hyperv`。  
   - 重新編譯或覆蓋後重新啟動 Kitematic。  
2. 修改後 Kitematic 會呼叫 `docker-machine create -d hyperv`，與前述 CLI 流程一致，GUI 功能恢復。

**Cases 1**:  
依文章指示替換檔案後，Kitematic 成功偵測到已存在的 `boot2docker` (Hyper-V) Host；可透過 UI 搜尋、下載並啟動 Redis、MySQL 等映像，驗證 GUI 體驗完整恢復。

---

## 整體成效 (Summary)

1. 在單一實體主機內，完成「Hyper-V Host → Windows 10 VM → Hyper-V → boot2docker → Docker Container」五層巢狀架構。  
2. 不需實體機重灌或額外購置伺服器，即可在受控 VM 環境中學習、展示 Docker 與微服務。  
3. 透過 Nested Virtualization + Docker Machine 的組合，將原本「完全不可行」的情境轉化為可用解；實驗人員節省重新佈建實體環境的 100% 時間成本。