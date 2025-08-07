# WMCmd.vbs 在 VISTA 下執行會導致 cscript.exe 發生錯誤…

## 摘要提示
- WMCmd.vbs: Windows Media Encoder 9 內附的 WMCmd.vbs 在 Vista 執行時會觸發錯誤。  
- DEP 防護: 錯誤原因為 Vista 強制的資料執行防護（DEP）攔截 cscript.exe。  
- cscript.exe 限制: Vista 對 cscript.exe 強制開啟 DEP，使用者無法透過排除清單關閉。  
- Google/MS Support: 作者先以搜尋及官方支援管道尋找解法。  
- KB929182: 微軟發佈修補程式「FIX: You may experience issues when you use Windows Media Encoder 9 Series on a computer that is running Windows Vista」。  
- 安裝修補: 安裝後 WMCmd.vbs 與批次轉檔腳本恢復正常運作。  
- 影像工作流程: 批次轉檔腳本可繼續將 DV AVI 檔轉為 WMV 使用。  
- 未竟事項: 作者尚待 Canon 更新 .CRW RAW 影像的編解碼器。  

## 全文重點
作者在 Windows Vista 進行影音轉檔時，發現原本在 Windows XP 時期使用的冷門工具——Windows Media Encoder 9 隨附的指令稿 WMCmd.vbs——一執行就讓 cscript.exe 因 DEP（Data Execution Prevention）觸發而被迫終止。DEP 會在偵測到程式試圖在資料區段執行程式碼時立即封鎖，以減少惡意程式入侵風險；但這同時也暴露出微軟舊版程式在記憶體使用上的潛在問題。作者原想將 WMCmd.vbs 加入 DEP 排除名單，卻發現 Vista 對 cscript.exe 採用「一律啟用 DEP」的策略，無法手動停用，只得改以搜尋與官方技術支援尋求解法。

幸運的是，微軟已針對此特定相容性問題釋出修補程式 KB929182（標題：You may experience issues when you use Windows Media Encoder 9 Series on a computer that is running Windows Vista）。安裝之後，WMCmd.vbs 能在保持 DEP 啟用的前提下正常執行，作者撰寫的批次轉檔腳本亦恢復運作，得以持續將大量 DV AVI 檔案批次轉換成 WMV 格式。整體來說，此事件揭示了 Vista 新增安全機制與舊軟體之間的衝突，也說明透過官方修補可迅速排除問題；目前作者僅剩等待 Canon 釋出 .CRW RAW 格式的 Vista 編解碼器，即可完成整個影音與影像工作流程的升級。

## 段落重點
### 問題現象
作者在 Vista 執行 WMCmd.vbs 時，cscript.exe 因 DEP 觸發而被終止，顯示 Microsoft 舊程式碼仍可能在資料區段執行指令，與 Vista 的安全強化機制衝突。

### 排除過程
嘗試將程式加入 DEP 排除名單失敗，因為 Vista 對 cscript.exe 強制開啟 DEP；作者只得透過 Google 與 Microsoft Support 尋找官方解法。

### 解決方案與後續
發現並安裝 KB929182 修補程式後，問題完全排除，批次轉檔腳本恢復正常。作者下一步僅待 Canon 補上 .CRW 編解碼器，即可在 Vista 上完成全部多媒體工作流程。