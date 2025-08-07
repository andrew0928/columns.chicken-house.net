# WMCmd.vbs 在 Windows Vista 因 DEP 導致 cscript.exe 異常的解決方案

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Windows Vista 執行 WMCmd.vbs 會導致 cscript.exe 因 DEP 而當機

**Problem**:  
在 Windows Vista 上，嘗試使用 Windows Media Encoder 9 所附的指令稿 WMCmd.vbs 進行影片批次轉檔時，cscript.exe 於執行過程中被 Data Execution Prevention (DEP) 阻擋並當機，導致整個轉檔流程中斷，無法完成編碼工作。

**Root Cause**:  
1. Windows Vista 針對 cscript.exe 強制啟用 DEP，禁止任何可能於資料區段執行的程式碼。  
2. Windows Media Encoder 9 及其指令稿 WMCmd.vbs 內部仍包含會觸發「於資料區段執行」的舊式函式呼叫或組件，因而被 DEP 認定為不安全並直接終止程序。  
3. 使用者無法在 Vista 中對 cscript.exe 關閉 DEP，因此僅靠系統設定無法規避此例外。

**Solution**:  
套用 Microsoft 官方發佈的 Hotfix (KB 929182) 以更新 Windows Media Encoder 9 相關元件。該 Hotfix 重新編譯問題 DLL/COM 物件或修補 WMCmd.vbs 內部呼叫，使其不再於資料區段執行，從根本上符合 DEP 規範。  
安裝步驟：  
1. 下載 Hotfix：  
   http://support.microsoft.com/kb/929182/en-us  
2. 依安裝指示完成修補並重新開機。  
3. 重新執行原本的批次轉檔指令，例如：  
   ```cmd
   cscript.exe WMCmd.vbs -input input.avi -output output.wmv -v_codec WMV9
   ```  
   執行過程將不再因 DEP 中斷。

**Cases 1**:  
• 背景：利用自製批次指令稿一次轉檔 60 GB DV AVI 影片至 WMV 前，升級至 Vista 後全數失敗。  
• 根本原因：如前所述，由於 DEP 強制開啟，WMCmd.vbs 執行期間觸發存取違例。  
• 解決方法：安裝 KB 929182 Hotfix。  
• 成效：  
  – 所有轉檔批次腳本恢復正常運作，轉檔速度與 XP/2003 時期相同。  
  – 減少 100% 由 DEP 造成的失敗率。  
  – 無需調整 OS DEP 設定或改寫現有指令稿，維護成本趨近零。

