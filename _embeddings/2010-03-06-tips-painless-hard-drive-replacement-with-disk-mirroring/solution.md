# 用「磁碟鏡像 + 延伸磁區」無痛更換硬碟

# 問題／解決方案 (Problem/Solution)

## Problem: 伺服器硬碟升級必須「不中斷服務」完成

**Problem**:  
在 Windows Server 上有多項線上服務 (IIS 網站、SQL Server、檔案分享、Page File) 均存放於同一組 RAID1 磁碟 (兩顆 750 GB)。當硬碟容量不足、欲升級為兩顆 1.5 TB 硬碟時，若採取傳統方式 (停機複製檔案或使用第三方 Clone 工具)，勢必長時間關閉服務、搬移資料，流程繁雜且風險高。

**Root Cause**:  
1. 傳統「關機 ‑> 複製檔案 ‑> 重建服務」流程需要：  
   • 長時間停機 (數百 GB 複製時間)  
   • 重新設定分享、IIS、SQL 目錄…等，錯誤點多  
2. Disk Clone 工具雖可複製，但：  
   • 依賴離線作業，仍需停機  
   • 新碟為 Advanced Format，Clone 後效能須再校正 (alignment)，流程更複雜  

**Solution**:  
利用 Windows Server 內建「動態磁碟 Mirror (RAID-1) + Extend Volume」機制，讓資料在「線上」自動同步到新硬碟，再延伸磁區即可完成。  
Workflow：  
1. 關機，裝入新硬碟 (容量更大)。  
2. 開機後，將舊碟 (Disk 1) 與新碟 (Disk 2) 在 Disk Management 轉成 Dynamic Disk，建立 Mirror。系統立即開始 Resync。  
3. Resync 完成 → 資料已完整複製到新碟，且所有服務全程在線。  
4. 中斷 Mirror (Break Mirror)，保留新碟。  
5. 針對留下的新碟磁區做 Extend Volume，將剩餘未配置空間一次吃進來 (Windows 2008 以上支援)。  
6. 移除舊碟 (若需再鏡像，可用另一顆新碟重建)。  

為何可解決 Root Cause：  
• Mirror 過程允許磁區保持線上；Resync 期間所有 I/O 仍可持續。  
• 不需第三方 Clone → 免去 Advanced Format 對齊議題。  
• 服務目錄、權限、分享設定完全不變，降低人為錯誤。  

**Cases 1**:  
背景：作者實際將兩顆 750 GB RAID1 升級為兩顆 1.5 TB。  
成效：  
• 實際停機時間僅「關機插拔硬碟」數分鐘。  
• 750 GB → 1.5 TB 擴充全程 IIS、SQL、File Share 無中斷。  
• 管理者操作僅「幾次滑鼠點擊」，省去重新設定服務的人力成本。  

---

## Problem: 鏡像到較大硬碟後，原磁區容量未自動擴充

**Problem**:  
Mirror 會按照「較小那顆」硬碟的容量建立，換上 1.5 TB 後，鏡像完成仍顯示原 750 GB，剩餘空間無法使用。

**Root Cause**:  
• 軟體 Mirror 的邏輯是「位元對位元」複寫，不會自動將磁區擴充至整顆硬碟。  
• 在動態磁碟中，磁區大小與硬碟實體容量脫鉤，必須手動調整。

**Solution**:  
1. Break Mirror → 解除 Disk 1 / Disk 2 的鏡像關係。  
2. 對新碟 (原 Disk 2) 的目標磁區使用「Extend Volume」，將後方未配置空間一次併入。  
3. 系統即時把 D: 從 750 GB 擴充到 1.5 TB，資料完整且線上。  

**Cases 1**:  
• Extend Volume 操作不到 1 分鐘完成，容量立即翻倍。  
• D: 磁碟機代號不變，IIS 與 SQL Server 資料庫路徑皆無須重新設定。  

---

## Problem: 動態磁碟與部分 OS / 工具不相容

**Problem**:  
使用 Windows 動態磁碟後，若該硬碟需接到其它作業系統 (Linux, Windows Client SKU) 或第三方工具，可能無法辨識。

**Root Cause**:  
• Dynamic Disk metadata 與 MBR/GPT 格式不同，非 Windows Server 的 OS 與部分磁碟工具缺少對應 driver。  
• Desktop 版 Windows (XP / 7) 僅支援讀取部分 Dynamic Volume 類型，且不支援建立 Mirror。

**Solution**:  
替代方案與避免方式：  
1. 若日後需跨 OS 使用，改採「硬體 RAID 控制卡」或「軟體換回 Basic Disk + Clone」。  
2. 若只在 Windows Server 環境內運行，維持 Dynamic Disk 不成問題。  

**Cases 1**:  
• 作者轉成 Dynamic Disk 後持續在 Windows Server 2008 R2 使用，穩定運作超過半年；並未再接到其它 OS，因此無不相容困擾。  

**Cases 2**:  
• 另一專案需要將硬碟掛到 Linux 進行 forensic，因 Dynamic Disk 無法被讀取，改以硬體 RAID 1 解決。  

---