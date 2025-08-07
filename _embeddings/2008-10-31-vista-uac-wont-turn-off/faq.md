# 關不掉的 Vista UAC !?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Vista 的 UAC 在控制台裡明明顯示為「關閉」，卻還是一直跳出提示，要怎麼真正把 UAC 關掉？
透過「開始 → 執行」輸入 `msconfig.exe`，在開啟的「系統設定」視窗中找到「關閉 UAC」(Disable UAC) 的項目並執行，完成後重新開機即可確實關閉 UAC。

## Q: 為什麼在控制台切換 UAC 開關後，狀態完全沒有改變？
作者推測是控制台的小程式 (applet) 出了問題，設定值沒有成功寫進登錄檔 (registry)；造成原因可能與最近套用的某個 Windows 更新或一次異常關機有關。

## Q: 使用 msconfig.exe 關閉 UAC 的原理是什麼？
msconfig.exe 的「關閉 UAC」工具會直接修改 Windows 登錄檔中的相關鍵值，因而能繞過控制台介面，讓變更立即生效並在重新開機後反映出正確的 UAC 狀態。