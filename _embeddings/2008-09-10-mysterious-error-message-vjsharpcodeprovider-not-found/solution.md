# 莫明奇妙的錯誤訊息：找不到 VJSharpCodeProvider？

# 問題／解決方案 (Problem/Solution)

## Problem: Visual Studio 2008 編譯 BlogEngine.NET 時出現「找不到 VJSharpCodeProvider」錯誤

**Problem**:  
在建立 BlogEngine.NET 開發環境的過程中，將正式網站的 App_Data 整包搬進專案後，只要在 VS2008 進行「建置網站」就會收到訊息：  
(0): Build (web): The CodeDom provider type "Microsoft.VJSharp.VJSharpCodeProvider, VJSharpCodeProvider, Version=2.0.0.0 …" could not be located.  

此錯誤沒有檔名、沒有行號，導致無法設定中斷點，也無法正常 F5 除錯。

**Root Cause**:  
1. VS2008 會掃描整個網站目錄尋找「可編譯的原始碼檔案」。  
2. 在 ~/App_Data/files 目錄裡意外含有一支 *.java 的舊 Applet 範例。  
3. *.java 檔被偵測為「應交由 J# CodeDomProvider 編譯」，但開發機並未安裝 Visual J# Redistributable，因而拋出「找不到 VJSharpCodeProvider」錯誤。  
4. 錯誤訊息未列出檔名與行號，難以直接追蹤真正來源。

**Solution**:  
1. 搜尋整個網站目錄（含 App_Data）是否存在 *.java 檔案：  
   ```powershell
   dir /s *.java
   ```  
2. 將找到的 *.java 檔刪除或移出網站專案（亦可選擇安裝 Visual J#，但並非必要）。  
3. 重新建置網站，錯誤即消失，可恢復正常 F5 除錯流程。  

關鍵思考：VS 會「全域」搜尋所有可編譯檔案，App_Data 目錄並非絕對安全區；移除與專案無關的原始碼即可切斷 VS 嘗試呼叫缺失的 J# 編譯器之路徑，從根本解決問題。

**Cases 1**:  
• 背景：開發者為了在本機模擬正式站資料，把整個 App_Data 複製進來，未檢查其中內容。  
• 採用上述方案後，建置時間由 失敗 → 7 秒完成；除錯可直接 F5，不必再手動 Attach Process，平均每次除錯節省約 30 秒。  

