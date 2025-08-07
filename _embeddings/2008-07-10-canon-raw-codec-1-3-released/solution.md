# Canon RAW Codec 1.3 – 相容性陷阱與回退策略

# 問題／解決方案 (Problem/Solution)

## Problem: 安裝 Canon RAW Codec 1.3 後，既有的 .NET/WPF 應用程式 (包含自家歸檔工具與 Microsoft Pro Photo Tools) 無法正常執行

**Problem**:  
在 Windows Vista SP1 (32 bit) 環境中，當使用者將 Canon RAW Codec 從 1.2 升級到 1.3 版後，  
1. 自行開發的歸檔程式啟動即當掉  
2. Microsoft Pro Photo Tools 也被官方明確標示為「不相容」  
導致所有依賴 .NET 3.0 + WPF 影像處理的工作流程中斷。

**Root Cause**:  
Canon RAW Codec 1.3 內部對 WIC (Windows Imaging Component) 的呼叫方式與 1.2 版不同，與 .NET 3.0/WPF 影像管線發生衝突；造成  
• 以 .NET 3.0 + WPF 為 UI 的應用程式載入 RAW 解碼器時掛掉  
• Microsoft Pro Photo Tools 依賴的介面無法正確初始化  
此相容性議題在 Canon 官方更新說明中僅一句「與 Microsoft Pro Photo Tools 不相容」帶過，未明示技術細節。

**Solution**:  
1. 立即回退至 Canon RAW Codec 1.2，且需使用「RC120UPD_7L.EXE」這個最早釋出的 1.2 安裝檔 (新版「CRC120UPD_7L.EXE」亦有相容性問題)。  
2. 如果已經安裝 1.3，步驟如下：  
   ```txt
   A) 控制台 → 程式和功能 → 卸載 Canon RAW Codec 1.3  
   B) 重新開機 (確保 WIC 快取清空)  
   C) 執行 RC120UPD_7L.EXE 重新安裝 1.2 版  
   D) 重新開機並驗證 .NET/WPF 程式可正常啟動
   ```  
3. 暫緩升級：所有依賴 .NET 3.0 + WPF 或需使用 Microsoft Pro Photo Tools 的工作站，暫停布署 1.3，直到 Canon 或 Microsoft 公布修補方案。  

為何此 Solution 能解決問題：  
• 回退至 1.2 版可恢復與 WIC、.NET 3.0 + WPF 的既有相容性；  
• 選擇最早的 RC120UPD_7L.EXE 確保使用經驗證可用的 build，避免同版本不同 build 再次踩雷；  
• 透過完整卸載 / 重開機流程，確保舊 DLL 與快取被正確取代。

**Cases 1**:  
背景：作者的歸檔程式 (使用 .NET 3.0 + WPF) 在安裝 1.3 後無法啟動。  
處置：依上述步驟回退至 1.2 (RC120UPD_7L.EXE) 後立即恢復正常。  
效益：  
• 生產中斷時間 < 30 分鐘  
• 歸檔流程 100% 恢復

**Cases 2**:  
背景：Microsoft Pro Photo Tools 官方文件標示與 1.3 不相容；多位攝影師論壇用戶回報升級後無法啟動 PPT。  
處置：拒絕升級或回退至 1.2。  
效益：  
• 避免批次加 GPS/EXIF 標註流程被迫改用其他工具  
• 減少 IT 支援工時 (估計每台機器節省 0.5~1 小時除錯時間)

## Problem: Canon 官方提供多個同版號 (1.2) 安裝檔，導致維運端無法快速辨識「可靠版本」

**Problem**:  
Canon 同時發佈兩個檔名相似的 1.2 安裝檔：  
• RC120UPD_7L.EXE (舊)  
• CRC120UPD_7L.EXE (新)  
僅前者與 .NET/WPF 應用程式相容；後者與 1.3 一樣會造成軟體當掉，運維人員難以分辨正確檔案。

**Root Cause**:  
版本控管/命名策略混亂：  
• Canon 未改版號就重新打包 DLL  
• 檔名僅差一個字元，無官方 changelog 說明差異  
• 使用者依「版本號」而非「檔名」進行軟體盤點，易誤裝錯檔

**Solution**:  
1. 於內部文件、安裝腳本或軟體倉庫明確標註「1.2 – RC120UPD_7L.EXE 為唯一可用版本」。  
2. 設置安裝檔 Hash 檢核：  
   ```powershell
   Get-FileHash RC120UPD_7L.EXE | Out-File .\CanonCodec12.hash
   ```  
   部署時比對 Hash，確保拉錯檔即終止安裝。  
3. 將「CRC120UPD_7L.EXE」與「RC130UPD_7L.EXE」封鎖於組織的套件管理系統或軟體中心，避免誤裝。

**Cases 1**:  
背景：公司影像部門有 20 台工作站；IT 透過 SCCM 佈署 RAW Codec。  
措施：只允許雜湊符合 RC120UPD_7L.EXE 的檔案通過。  
效益：  
• 安裝錯誤率從 30 % → 0 %  
• IT 省下平均每月 3 小時「誤裝→回退」的維運時間

**Cases 2**:  
背景：自由攝影師同步三台筆電環境，原用雲端同步資料夾存放安裝檔，因檔名過近誤用 CRC120UPD_7L.EXE。  
措施：修改檔名為「CanonRAWCodec12_OK.exe」並附帶 SHA1。  
效益：  
• 手動重裝次數歸零  
• 減少在外景時軟體失效的風險