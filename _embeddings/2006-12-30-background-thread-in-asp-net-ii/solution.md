# Background Thread in ASP.NET (II)

# 問題／解決方案 (Problem/Solution)

## Problem: ASP.NET 背景工作緒在執行 20 分鐘後自動消失  

**Problem**:  
在 ASP.NET 應用程式中啟動一支長時間執行的背景工作緒（worker thread），希望它能持續執行批次處理／排程任務。但實際執行時，只要瀏覽器沒有新請求進來，大約 20 分鐘後背景工作緒就自動終止，Log 檔也停止寫入。

**Root Cause**:  
IIS 的 Application Pool（AppPool）預設 Idle Time-out 設為 20 分鐘。當在這段期間內沒有任何 HTTP Request，IIS 會將整個 AppDomain 卸載以釋放資源，導致在該 AppDomain 內執行的背景工作緒也跟著被回收。

**Solution**:  
1. 進入 IIS 管理員 → Application Pools → 選擇對應的 AppPool → Advanced Settings  
2. 將 Process Model → Idle Time-out (minutes) 由預設 20 改為 0（代表停用）或調高到足以覆蓋預期的背景工作時間。  
3. 重新啟動 AppPool／IIS 使設定生效。  

此設定可避免因「應用程式閒置」而被自動回收，進而確保背景工作緒可持續執行。  

**Cases 1**:  
• 原先背景工作緒在 20 分鐘時終止 → Idle Time-out 設為 0 後，觀察數小時均未再中斷。  
• Log 檔由原本僅 20 分鐘長，拉長至數小時連續輸出，證實工作緒持續運作。  



## Problem: 背景工作緒仍因 w3wp.exe 異常結束而中斷  

**Problem**:  
即便 Idle Time-out 已解除，但在長時間執行過程中，整個 IIS 工作行程 (w3wp.exe) 停掉，背景工作緒隨之中斷。

**Root Cause**:  
AppPool 可能因未攔截的例外（Unhandled Exception）或記憶體耗盡 (Crash Protection) 觸發自動回收／閤起，導致 w3wp.exe 結束。

**Solution**:  
1. 在背景工作緒主迴圈加入 try…catch，並捕捉所有例外 (Exception) 做紀錄。  
   ```csharp
   Task.Run(() =>
   {
       while (true)
       {
           try
           {
               DoWork();              // 實際商業邏輯
           }
           catch (Exception ex)
           {
               LogError(ex);          // 寫入自訂 Log 或 Windows EventLog
           }
           Thread.Sleep(1000);        // 視需求加上休眠
       }
   });
   ```  
2. 將嚴重錯誤寫入 EventLog，並設定 AppPool 的「Rapid-Fail Protection」參數，避免因連續 Crash 而被停用。  
3. 對記憶體密集或 I/O 操作加入資源釋放 (Dispose / using) 與失敗重試機制，降低例外發生機率。  

**Cases 1**:  
• 透過全域 exception handling，原本 2 小時左右就 Crash 的 w3wp.exe，可穩定執行超過 24 小時；  
• EventLog 中未再出現 Unhandled Exception 紀錄。