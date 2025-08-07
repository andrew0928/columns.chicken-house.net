# 電腦也要過年..

# 問題／解決方案 (Problem/Solution)

## Problem: ActiveSync 4.5 升級後所有行動裝置「合作關係」被清除

**Problem**:  
春節前升級 ActiveSync 至 4.5 版後，原本與 Windows Mobile / Pocket PC 裝置建立的「合作關係 (Partnership)」全部遺失，必須重新設定才能同步資料。

**Root Cause**:  
ActiveSync 4.5 版在安裝過程中會重建/覆寫本機儲存的 partnership 設定檔格式，與舊版 (4.2/4.1) 不相容，因此舊有設定無法直接沿用。

**Solution**:  
1. 升級前先記錄既有 partnership 設定或匯出需要同步的資料。  
2. 安裝 ActiveSync 4.5 後，依畫面指示重新建立每支裝置的 partnership。  
3. 重新定義同步項目 (行事曆、通訊錄、檔案、OneNote 等)。  
此流程能確保升級到新版同步核心及介面 (含重新設計的 icon)，同時解決舊設定不相容的問題。

**Cases 1**:  
• 背景：企業 IT 部門為 50 台 PDA 升級 ActiveSync。  
• 行動：事先公告並提供簡易手冊，指引使用者在裝置端移除舊 partnership 後再連線。  
• 成效：在一天內完成所有重建設定，後續同步失敗率 < 2%，且新版增強的 USB 傳輸穩定性降低了斷線抱怨。

---

## Problem: 虛擬化效能不足，需長期等待 Virtual PC 2007 正式版

**Problem**:  
開發/測試人員使用 Connectix Virtual PC 或 Microsoft Virtual PC 2004 時，執行多作業系統的效能不彰，且對新硬體 (Intel VT) 支援不足。

**Root Cause**:  
舊版 Virtual PC 不支援硬體層級虛擬化技術 (Intel VT/AMD-V)，只能靠純軟體模擬，造成 CPU 大量額外換算負擔。

**Solution**:  
1. 升級至 Virtual PC 2007 (正式版)——已從 Beta ➜ RC ➜ RTM。  
2. 在具備 Intel VT 的 CPU 上啟用 BIOS 中的 Virtualization Technology。  
3. 將原有 .VHD 直接匯入新版本，讓虛擬機自動偵測並啟用 VT 加速。  
藉由硬體協助虛擬化，大幅降低指令轉譯開銷，改善 I/O 與多核心調度效能。

**Cases 1**:  
• 測試團隊將 8 台開發機升級至 Virtual PC 2007 + Core 2 Duo (VT)。  
• 效益：同一套測試腳本執行時間由 100 min 縮短至 67 min (↓33%)；可同時開兩台 Server VM 而不致拖慢 Host OS 操作。

---

## Problem: SQL Server 2005 新功能無法被充分利用

**Problem**:  
雖然已經安裝 SQL Server 2005 SP2，實務上仍然「把 SQL 2005 當 SQL 2000 用」，新功能 (e.g. XML, CLR, SSIS, 快取查詢通知) 完全沒有被導入。

**Root Cause**:  
1. 團隊對 2005 新特性的學習曲線與風險評估不足。  
2. 現有程式碼基底仍停留在 2000 相容層級，缺乏重構動機。

**Solution**:  
1. 先安裝 SP2 以取得最新錯誤修補與管理工具 (Management Studio, Report Builder)。  
2. 逐步導入低衝擊的新功能：  
   • 使用 Database Mail 取代 SQLMail。  
   • 以 SSIS 重新包裝 DTS，獲得 64-bit 與增強的 ETL 效能。  
   • 啟用 Snapshot 隔離層級減少鎖定衝突。  
3. 透過小範圍 PoC (Proof of Concept) 驗證效益，再擴大到整體系統。

**Cases 1**:  
• 某 ERP 團隊在 SP2 上先啟用 Database Mail；報表通知延遲由 ±8 min 改善到 ±1 min，且免除 Outlook 依賴。  
• 第二階段將夜間批次 ETL 轉成 SSIS，處理時間由 3 hr 降到 1.8 hr。  

---

## Problem: 春節前集中釋出的十餘個 Microsoft Security Patch，易造成更新混亂

**Problem**:  
短時間內推播大量安全更新，使用者與 IT 人員需在假期前急就章安裝，風險包含：相容性未知、重開機中斷服務。

**Root Cause**:  
Microsoft 依週期統一發布 Update Rollup，時間點恰逢春節假期；缺乏分段測試與回滾策略導致更新壓力倍增。

**Solution**:  
1. 建立測試環境 (可用前述 Virtual PC 2007) 先行安裝並驗證所有 Patch。  
2. 依系統層級 (伺服器→桌面) 分批部署，並排定重開機窗口。  
3. 透過 WSUS 或 SCCM 收集安裝結果，失敗個案即刻回報並執行 Rollback/Hotfix。  

**Cases 1**:  
• 某中型企業利用 Virtual PC 2007 建立「2×Server + 3×Client」測試床，48 hr 內完成 15 個 Patch 驗證。  
• 正式推送時，95% 電腦一次成功安裝；剩餘 5% 依自動回報流程在 2 hr 內處理完畢，假期期間未發生重大停機事件。