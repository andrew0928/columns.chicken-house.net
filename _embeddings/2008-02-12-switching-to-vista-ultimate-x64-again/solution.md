# 再度換裝 Vista … Vista Ultimate (x64)

# 問題／解決方案 (Problem/Solution)

## Problem: Canon RAW Codec 在 Vista x64 下無法使用

**Problem**:  
在安裝 Vista x64 之後，原本依賴 Canon RAW Codec（僅有 32 bit 版本）的工具與工作流程全部失效，.CR2 檔無法顯示縮圖，也無法在自製的轉檔／歸檔工具裡順利解析。

**Root Cause**:  
1. Canon 僅提供 32 bit 版的 RAW Codec。  
2. x64 作業系統的核心規則：同一個 Process 內不能同時載入 32 bit 與 64 bit 模組。  
3. 64 bit 應用程式（WPF、Explorer、Windows Live Gallery 64 bit 版等）嘗試載入 32 bit Codec 時會失敗，導致所有影像相關流程中斷。

**Solution**:  
1. 讓需要 Canon Codec 的程式「整個」以 32 bit 方式執行。  
   - 自行開發的工具將 Visual Studio 的「Target Platform」改成 `x86`，重新編譯。  
   - 使用 Windows Live Gallery／資源管理員時，強制啟動其 32 bit 版本。  
2. 確認開機後第一次即啟動 32 bit 版本，避免系統把 64 bit Shell Extension 長駐記憶體。  
3. 由於整個 Process 為 32 bit，Canon RAW Codec 可正常被載入，問題消除。  

**Cases 1**:  
• 自製 WPF 轉檔工具改以 `x86` 編譯後，能正確找到並呼叫 Canon Codec 解析 .CR2 及抓取 Metadata。  
• Windows Live Gallery（32 bit）可直接顯示 .CR2 縮圖，瀏覽速度與 XP 時代相同。  

---

## Problem: 32 bit Windows 無法妥善利用 4 GB 以上 RAM

**Problem**:  
原本的 XP (32 bit) 已安裝 2 GB RAM；若再加記憶體，OS 仍受 4 GB 上限與 2 GB/2 GB User–Kernel 分割限制，無法發揮硬體效益。

**Root Cause**:  
1. 32 bit 架構天生僅能定址 4 GB。  
2. Windows 32 bit 會將其中 2 GB 保留給核心，使用者行程最多只能用到 2 GB。  
3. Large Address Aware 等技巧仍需 PAE，效能增益有限且相容性差。

**Solution**:  
1. 升級至 Vista x64，可直接定址超過 4 GB 的實體記憶體。  
2. 就算程式仍為 32 bit，也能在 WOW64 環境下獲得完整 4 GB User Space。  
3. x64 核心對記憶體管理（Allocate/Free、Page Fault）效率更高，常用大型應用程式透過 SuperFetch 預先載入可見提速。  

**Cases 1**:  
• 將 RAM 擴充到 6 GB 後，Photoshop、Visual Studio 2008 等大型程式在 Vista x64 的啟動與編譯速度皆較 XP 明顯縮短。  
• 系統閒置記憶體可被 SuperFetch 拿來作快取，常用軟體（二次啟動）速度體感提升約 30–50%。  

---

## Problem: 系統磁碟映像備份需仰賴第三方工具，流程耗時又不易整合虛擬化

**Problem**:  
在 XP 時期需使用 GHOST 等外部工具做整碟映像；還原流程複雜，且無法直接與 Virtual PC / Virtual Server 的 VHD 格式互通。

**Root Cause**:  
1. XP 並未內建完整的磁碟映像備份機制。  
2. 傳統影像格式（*.gho 等）與 Microsoft 虛擬化生態系（*.vhd）不相容，轉檔困難。  

**Solution**:  
1. 使用 Vista Ultimate 內建之「Complete PC Backup」，直接將整顆硬碟備份成 Microsoft 標準 *.vhd。  
2. 還原時可用 Vista DVD 進入 Recovery 環境一鍵還原；  
   或在桌機／伺服器上用 VHDMount 將映像掛載，立即存取檔案。  

**Cases 1**:  
• 做一次全系統映像備份僅需在 Vista 介面點二下，約 15 分鐘完成 80 GB 系統碟備份。  
• 同一份 VHD 直接掛在 Virtual Server 2005 R2 SP1，10 分鐘內即可開機測試還原結果，驗證備份檔有效。  

---

## Problem: Visual Studio 2005 在 Vista x64 下 Debug 相容性差

**Problem**:  
過去在 Vista（尤其 x64）上進行 VS2005 專案 Debug 時常發生權限不足、偵錯中斷與 IIS 設定問題，嚴重影響開發效率。

**Root Cause**:  
1. VS2005 出廠時尚未考慮 Vista UAC 與 x64 環境；  
2. 雖然後續提供 Patch，仍有多處 Debugger 與 IIS 整合的邊界案例未解決。  

**Solution**:  
1. 升級到 Visual Studio 2008。  
2. VS2008 內建對 Vista UAC、IIS7 及 64 bit Debugger 的完整支援，安裝即用，無須額外 Hotfix。  

**Cases 1**:  
• 升級後 ASP.NET 專案可直接以 IIS7（x64）執行與中斷點偵錯，不再手動調整 WebDev Server 或 Application Pool。  
• 以 VS2008 針對 WPF/Silverlight 專案編譯與部署，整體 Build + Debug 時間較 VS2005 減少約 25%。