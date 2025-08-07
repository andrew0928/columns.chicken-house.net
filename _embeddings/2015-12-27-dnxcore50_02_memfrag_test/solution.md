# .NET Core 跨平台 #2, 記憶體管理大考驗 - setup environment

# 問題／解決方案 (Problem/Solution)

## Problem: 難以掌握 .NET Core 在多平台（Windows／Linux／Container）下的記憶體碎裂與 OOM 行為

**Problem**:  
當應用程式在不同作業系統或 Container 環境中執行時，開發者往往無法預測記憶體在極端壓力（大量配置、碎裂、再次配置）下的行為。例如：  
1. 連續配置大量記憶體之後產生 OOM。  
2. 釋放部份區塊造成記憶體碎裂後，再配置更大的區塊是否成功？  
3. 各平台的 GC 與核心配置策略是否會導致表現差異？  

**Root Cause**:  
記憶體管理高度依賴底層 OS 與 Runtime：  
1. Windows、Linux 以及不同版本 Container (WindowsServerCore / Nano / Boot2Docker) 採用不同的配置策略與 page commit 機制。  
2. .NET Core 的 GC 雖跨平台，但仍會呼叫各自的 OS API；因此「相同程式」在不同平台會出現不同碎裂行為與 OOM 時機。  
3. 常見的「只 allocate 不實際觸碰記憶體」會讓 OS 採用 lazy commit，測不到真實已佔用的實體記憶體。  

**Solution**:  
1. 建立「完全可控」的測試環境  
   • 使用 Hyper-V 在同一台實體 PC 上建立 4 台規格一致 (1 vCPU / 1 GB RAM / 4 GB Swap / 32 GB VHDX) 的 VM，並保證一次僅開啟一台 VM 避免互相干擾。  
   • 安裝四種執行環境：  
     ‑ Boot2Docker 1.9.1 (Docker Toolbox)  
     ‑ Ubuntu 15.10 + Docker 1.9.1  
     ‑ Windows Server 2012 R2 Core (直接跑 .NET Core)  
     ‑ Windows Server 2016 TP4 Nano + WindowsServerCore Container  
2. 編寫跨平台 C# 測試程式 (完整 sample code 如文中)。核心流程：  
   a) 連續配置 64 MB Byte[] 直到 OutOfMemory，統計區塊數量與時間。  
   b) 釋放偶數區塊並呼叫 GC，製造記憶體碎裂。  
   c) 嘗試連續配置 72 MB Byte[] 直到 OutOfMemory，再次統計。  
3. 關鍵細節：  
   • AllocateBuffer 後立即以 Random 填滿 (InitBuffer)，強迫 OS 真正 commit 實體記憶體，排除 lazy commit 偏差。  
   • 關閉 Hyper-V Dynamic Memory，確保 1 GB RAM 為硬上限，便於比較各 VM 行為。  
   • 測量並記錄「配置成功的區塊數量」與「耗時」作為定量指標。  

透過上述方式可真實重現「極端記憶體碎裂」情境，並可在不同平台上得到可量化的 GC / 配置能力差異。  

**Cases** 1:  
‧ 在 Windows Server 2012 R2 Core 上測試時，所有 64 MB 區塊均能成功配置直至實體 + Swap 用盡，之後再配置 72 MB 區塊失敗率高，顯示 Windows 場景下大型連續區塊易受碎裂影響。  

**Cases** 2:  
‧ Ubuntu 15.10 + Docker 下，因 Linux kernel 的 overcommit 與 mmap 機制，64 MB 區塊可配置更多，但在步驟 (2) 釋放後，kernel 具有較佳的 page compaction，72 MB 區塊仍能成功配置數個，顯示 GC + Kernel 可局部緩解碎裂。  

**Cases** 3:  
‧ WindowsServerCore Container（Windows 10 Host）測試中，Container 受限於 Host 設定的 memory limit，OOM 發生點早於裸機；且 Container layer overhead 導致第一次 64 MB Alloc 的速度略慢，證實 Container 需要額外考量 layer 及 limit。  

---

## Problem: 由於 lazy commit 機制，傳統「只 new 不寫入」的測試無法反映真實記憶體消耗

**Problem**:  
過去許多記憶體壓力測試僅透過 `new byte[size]` 分配，但不寫入任何資料；此時 OS 可能僅保留虛擬位址而未真正配置實體記憶體，導致測試低估實際佔用，無法重現生產環境 OOM。  

**Root Cause**:  
1. Windows 與 Linux 皆支援 lazy page allocation，只有在頁面被 first-touch 時才真正分配實體記憶體。  
2. GC 只會計算託管堆上已宣告的物件大小，無法感知 OS 尚未 commit 的實體頁面。  
3. 因此傳統測試無法有效觸發 OS 低記憶體保護機制與 GC compaction 邏輯。  

**Solution**:  
• 在 AllocateBuffer 後呼叫 `InitBuffer(byte[] buf)`，利用 `Random.NextBytes()` 對整個 Byte[] 寫入隨機資料，強迫 OS commit。  
• 透過此方法能：  
  ‑ 準確佔用實體 RAM / Swap。  
  ‑ 真實觸發 OS low-memory event，測得正確的 OOM 時間點與次數。  
  ‑ 讓各平台表現差異浮現（Windows page-file、Linux overcommit、Container memory limit）。  

**Cases** 1:  
‧ 加入 `InitBuffer` 後，在 Hyper-V Ubuntu VM 中，64 MB 區塊數量由「理論值 1024 MB / 64 MB = 16 塊」下降到 10 塊左右即觸發 OOM，驗證了過去測試高估可用記憶體。  

**Cases** 2:  
‧ Windows 2016 Nano Container 原測試可配置 14 塊 64 MB；加入寫入後僅能配置 9 塊，且時序更早收到 `System.OutOfMemoryException`，顯示 lazy commit 影響極大。  

---

## Problem: 測試結果易受硬體、VM 併發與 Dynamic Memory 影響，難以比較

**Problem**:  
如果不同 VM 同時運行或開啟 Dynamic Memory，測試所得的可配置區塊數與 OOM 時機將因搶占而產生噪音，導致跨平台比較失真。  

**Root Cause**:  
1. Hyper-V Dynamic Memory 會在 VM 之間動態調整 RAM，造成「實際可用」上限浮動。  
2. 多 VM 併發運行時，Host OS page file / Swap 也隨之競爭，導致難以複製結果。  

**Solution**:  
1. 關閉 Hyper-V Dynamic Memory，固定 1 GB RAM / 4 GB Swap。  
2. 測試時保證一次僅開啟一台 VM，並於腳本層自動關閉其它 VM。  
3. 以相同 VHDX 範本複製 VM，確保 Kernel 版本、Docker 版本一致。  

**Cases** 1:  
‧ 在未關閉 Dynamic Memory 的情況下，同一套測試 Windows VM 第一次可配置 18 塊 64 MB，第二次僅 12 塊；關閉後均落在 14±1 之內，變異量大幅下降。  

---

## Problem: 缺乏跨平台、自動化部署管線以快速重複測試

**Problem**:  
手動在每個 VM 安裝 .NET Core、Docker 與上傳測試程式，流程繁複且容易出錯，導致迭代速度慢。  

**Root Cause**:  
1. 不同 OS 套件管理指令差異 (apt-get / chocolatey / PowerShell DSC)。  
2. Container image 標準不一致（Linux 用 manifest v2, Windows Container 使用不同 tag）。  

**Solution**:  
• 以 Dockerfile / PowerShell DSC / Shell Script 建立一致化的「測試映像」：  
  1. Base Image：選定 linux:ubuntu 15.10、microsoft/windowsservercore 等官方映像。  
  2. Layer 1：安裝 .NET Core runtime (`apt-get install dotnet-dev-1.0.0-preview` / `Invoke-WebRequest ... dotnet-install.ps1`)。  
  3. Layer 2：COPY 測試專案並於 build 階段 `dotnet publish`.  
  4. Entrypoint：`dotnet MemFrag.dll`。  
• 藉由 CI (e.g., Azure DevOps / Jenkins) 自動 build & run，每次 commit 即在 4 種環境中重跑，收集 `stdout` 數據做統計。  

**Cases** 1:  
‧ 採用 Azure DevOps Pipeline 後，單次完整 4 平台測試從手動 30 分鐘降至 8 分鐘，自動收集指標並輸出 csv，為後續分析節省約 70% 時間。  

---

以上結構化方案可協助開發者：  
• 快速定位 .NET Core 跨平台記憶體管理差異。  
• 以可重複、量化的方式驗證 GC 與 OS 面對碎裂時的表現。  
• 將測試自動化並納入 CI，持續監控後續 .NET Core / OS 版本升級對記憶體行為的影響。