# WMCmd.vbs 在 VISTA 下執行會導致 cscript.exe 發生錯誤…

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 Windows Vista 執行 WMCmd.vbs 會讓 cscript.exe 因 DEP 而被終止？
當 WMCmd.vbs（隨 Windows Media Encoder 9 附帶）在 Vista 上執行時，腳本中的某段程式碼會從資料區段被執行，觸發 Data Execution Prevention (DEP) 的保護機制，系統便會強制關閉 cscript.exe。

## Q: 能不能直接把 DEP 關掉來解決這個問題？
不行。在 Windows Vista 中，cscript.exe 被系統規定必須啟用 DEP，無法透過關閉 DEP 來繞過這個錯誤。

## Q: 是否有官方修補程式可解決 WMCmd.vbs 與 DEP 的衝突？
有。Microsoft 已釋出 KB929182 Hotfix，標題為「FIX: You may experience issues when you use Windows Media Encoder 9 Series on a computer that is running Windows Vista」。安裝此修補程式後，WMCmd.vbs 即可正常執行而不再觸發 DEP。

## Q: 安裝 KB929182 後實際效果如何？
安裝 Hotfix 後問題立即消失，原本用來批次轉檔的腳本可繼續運作。作者只剩等待 Canon 補上 .CRW 格式的編解碼器。