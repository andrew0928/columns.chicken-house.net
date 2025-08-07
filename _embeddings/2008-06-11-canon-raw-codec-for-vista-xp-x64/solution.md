# Canon RAW 檔在 Vista / XP x64 無法預覽的解決方案整理

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Windows Vista / XP x64 系統上無法直接預覽 Canon 相機的 RAW (CR2) 檔

**Problem**:  
當使用 Canon 相機拍攝 RAW 檔 (副檔名 *.CR2) 後，若在 Windows Vista x64 或 Windows XP x64 作業系統上開啟檔案總管，系統無法顯示縮圖、預覽或讀取檔案中關鍵的 EXIF/Metadata。對以 64-bit 系統為主要作業環境的攝影玩家或影像工作者而言，這會造成快速檢閱與挑片流程的斷點。

**Root Cause**:  
1. Canon 官方僅提供 32-bit 版 RAW Codec，尚未釋出支援 x64 的版本。  
2. Windows x64 Shell Extension (用來產生縮圖與預覽) 只能載入 64-bit DLL，導致 32-bit Codec 無法被系統直接呼叫。  
3. 雖可透過 WOW64 子系統執行 32-bit 應用程式，但與 Explorer Shell 的整合能力受限，仍無法在 64-bit Explorer 中生效。

**Solution**:  
1. 採用第三方開發者 ArdFry Imaging 提供的 “ArdFry CR2 Codec” (售價 USD 29.95，預購價 USD 19.95)，該套件直接提供 x64 原生 DLL，安裝後即可於 Explorer 及任何呼叫 Windows Imaging Component (WIC) 的程式內預覽、顯示縮圖與讀取 Metadata。  
   - 為何可解決？因為它補足了「缺少 x64 原生 WIC Codec」這個結構性缺口，使系統得以正確載入與編解碼 CR2 檔案。  
2. 暫時性替代方案：在 Vista x64 以「32-bit Explorer (WOW64)」開啟檔案總管，再載入 Canon 32-bit RAW Codec。  
   - 此法僅能在 32-bit Explorer 視窗中生效，且需額外手動切換，工作體驗不佳，但可作為 Canon 官方尚未推出 x64 Codec 前的權宜措施。  

**Cases 1**:  
背景：攝影師 A 使用 Vista x64 + Lightroom 工作流程，需要在 OS 層先篩片。  
處理：安裝 ArdFry CR2 Codec (x64) → Explorer 即時顯示縮圖 → 利用檔案總管即可快速淘汰 30% 不合格照片。  
效益：  
• 篩選時間由 20 分鐘降至 8 分鐘 (≈60% 時間節省)。  
• 檔案總管縮圖載入時間平均 <1 秒/張，提升使用者體驗。  

**Cases 2**:  
背景：部門內僅允許使用免費/現有工具，無預算購買第三方 Codec。  
處理：改用 32-bit Explorer (C:\Windows\SysWOW64\explorer.exe) 啟動 + 安裝 Canon 32-bit RAW Codec。  
效益：  
• 可在限定視窗內瀏覽縮圖，避免完全看不到的困擾。  
• 缺點是需手動啟動，且效能較差；作為過渡期權宜之計。