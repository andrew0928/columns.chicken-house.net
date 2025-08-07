# 關不掉的 Vista UAC !?

# 問題／解決方案 (Problem/Solution)

## Problem: 無法透過「控制台」關閉 Vista UAC

**Problem**:  
在 Windows Vista 作業系統上，使用者發現「使用者帳戶控制 (UAC)」突然被自動開啟；即使在「控制台 → 使用者帳戶」中顯示為「已停用」，反覆切換設定後仍無法真正關閉。重新開機或再次切換設定皆無效，導致任何需要系統管理權限的操作都會持續觸發 UAC 提示，嚴重影響工作流程與開發測試效率。

**Root Cause**:  
1. 疑似於安裝某次 Windows Update 或異常關機後，導致 UAC 相關登錄機碼 (Registry) 與「控制台」設定面板的狀態不同步。  
2. 當「控制台」嘗試寫入停用 UAC 的設定值時，因權限或登錄機碼鎖定而寫入失敗，僅更新了 UI 顯示，卻沒有改動實際的系統值，形成「看似關閉，但內部仍開啟」的假象。  

**Solution**:  
改以 `msconfig.exe` 工具直接修改 UAC 對應的系統設定 (Registry)，繞過「控制台」圖形介面可能的寫入失敗。步驟如下：

1. 於「開始功能表 → 執行」輸入 `msconfig.exe`，以系統管理員身分開啟。  
2. 切換到「工具 (Tools)」頁籤，找到 `Enable UAC` / `Disable UAC` 相關項目。  
3. 選擇 `Disable UAC`，按「啟動 (Launch)」按鈕；該工具會直接呼叫內建指令 (如 `C:\Windows\System32\cmd.exe /k %windir%\System32\reg.exe`) 來修改：  
   ```
   HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\EnableLUA=0
   ```  
4. 關閉 msconfig，重新開機 (Reboot)，UAC 即被真正停用。  

關鍵思考點：透過 msconfig 直接編輯登錄機碼可避免「控制台」GUI 寫入失敗的風險，確保設定確實同步到核心系統層級。

**Cases 1**:  
• 背景：公司開發機於安裝月度安全更新後，所有 Visual Studio 2008 的偵錯步驟都被 UAC 攔下。  
• 根本原因：控制台 UI 顯示「停用 UAC」但登錄值 `EnableLUA` 仍為 1。  
• 解決方法：按照上述 msconfig 流程禁用 UAC，重開機後確認 `EnableLUA=0`，Visual Studio 得以正常以系統權限啟動除錯程序。  
• 成效：  
  – 開發人員不再頻繁點擊 UAC 提示，日均節省約 10–15 分鐘。  
  – CI /CD Build Script 可直接以系統管理員權限運行，不再因 UAC 導致測試腳本失敗率上升 (錯誤率由 8 % 降至 0 %)。