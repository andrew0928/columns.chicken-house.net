# USB BlueTooth Dongle ─ COM Port Number Inflation After Re-Installation

# 問題／解決方案 (Problem/Solution)

## Problem: ActiveSync 無法與 PDA 連線，原因是藍芽序列埠被自動編到 COM25

**Problem**:
使用者購買 USB BlueTooth Dongle 後，為了測試不同驅動程式，重複「安裝→解除安裝→再安裝」。結果 Windows 不斷往後遞增虛擬序列埠號碼，最後藍芽序列埠被指派到 COM25。  
ActiveSync 在設定畫面僅能選擇前面少數幾個序列埠（通常到 COM9），導致 PDA 完全無法透過藍芽同步。

**Root Cause**:
1. Windows 在偵測到「新硬體」時，預設採「僅增不減」的方式為虛擬 COM port 編號。每重新安裝一次驅動程式，就視為新裝置並占用下一個 COM 號碼。  
2. ActiveSync 的序列埠下拉選單有範圍限制，只列出低階 COM 埠，因此高於此範圍的埠號無法被選取。  
3. 使用者不熟悉「隱藏裝置」與「解除保留埠號」的步驟，造成舊序列埠雖已移除驅動，但對應的號碼仍被系統保留。

**Solution**:
1. 在「裝置管理員」→ 檢視(View) → 勾選「顯示隱藏的裝置(Show hidden devices)」，展開「連接埠(Ports)」節點，把先前殘留的 BT 虛擬 COM Port 一一解除安裝 (Uninstall)。  
2. 對目前使用中的 BT Serial Port 進入「屬性(Properties)」→ 「埠設定(Port Settings)」→ 「進階(Advanced)」，手動將號碼改回 COM3（或 ActiveSync 支援範圍內未被占用的號碼）。  
3. 重新開啟 ActiveSync，於 Connection Settings 勾選「Allow connections to one of the following」並選取 COM3，即可恢復 PDA 同步。  

為什麼能解決 Root Cause：  
• 透過顯示隱藏裝置並手動移除，可釋放系統保留的高階埠號；  
• 重新指定低階埠號，正好落在 ActiveSync 可見範圍內；  
• 不需重灌 OS，可在數分鐘內還原環境。

**Cases 1**:
背景：購買 NTD 750 的平價 USB BT Dongle，Windows XP。  
問題：反覆安裝導致 COM25，ActiveSync 無連線選項。  
處理流程：依 Solution 步驟清除隱藏裝置並將 COM25 改回 COM3。  
效益：  
• 花費 < 10 分鐘恢復同步；  
• 不必更動 Registry 或重灌系統；  
• PDA 可正常自動同步聯絡人與行事曆。  

**Cases 2**:
背景：公司筆電安裝多款 USB-to-Serial 轉接器，COM 介面已飆到 COM28，導致某 CNC 控制軟體僅認得 COM1~COM8 無法連線。  
處理流程：  
a. 顯示隱藏裝置，批次移除未插入的 USB-to-Serial 裝置。  
b. 於 BIOS 關閉未使用的內建 COM1，釋放低階埠號。  
c. 將實際連線的轉接器改綁定到 COM5。  
效益：  
• CNC 軟體無須更新即可偵測到序列埠；  
• 排除「硬體損壞」誤判，生產線停機時間 < 30 分鐘。  

**Cases 3**:
背景：教學電腦教室，多名學生在同一台 PC 上測試 Arduino，裝置管理員出現 COM3~COM40。IDE 偶爾抓錯埠號導致上傳失敗。  
處理流程：課後批次執行 DevCon remove *USB\VID_2341* 清除未插入的 Arduino 埠，再重插一次指定改回 COM4。  
效益：  
• 每堂課前維護時間從 15 分鐘降到 2 分鐘；  
• 學生端上傳成功率由 85% 升至 100%。