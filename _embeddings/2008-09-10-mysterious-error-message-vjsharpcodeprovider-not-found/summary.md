# 莫明奇妙的錯誤訊息: 找不到 VJSharpCodeProvider ?

## 摘要提示
- BlogEngine.NET 升級: 作者為了升級與開發外掛而建立本機開發環境。  
- VS2008 編譯正常: 原始碼解壓、移植後初期編譯皆無問題。  
- 加入 sample data 出錯: 搬移 ~/App_Data 內資料檔後開始出現編譯失敗。  
- 無頭緒訊息: Visual Studio 只回報找不到 VJSharpCodeProvider，卻無檔名與行號。  
- 懷疑 J#: 作者並未安裝 J#，也未在專案或 web.config 指定 J#。  
- 搜尋檔案: 在 App_Data 找到一支多年前留下的 .java 檔案。  
- 刪除 .java 後復原: 清除該檔後編譯立刻通過，證實問題原因。  
- VS 掃描範圍過大: Visual Studio 連 App_Data 的檔案都列入編譯，導致誤觸。  
- 除錯痛點: 沒有完整訊息使得排錯困難，只能「死馬當活馬醫」嘗試。  
- 教訓: App_Data 並非免死金牌，無關程式檔案也需謹慎放置。  

## 全文重點
作者在為 BlogEngine.NET 進行升級與外掛開發時，於本機以 Visual Studio 2008 建立專案並順利編譯。然而當他為了測試功能而將線上站台的 ~/App_Data 資料檔搬回本機後，編譯忽然失敗，僅出現一行「無檔名、無行號」的錯誤訊息：「The CodeDom provider type "Microsoft.VJSharp.VJSharpCodeProvider… could not be located."」。由於作者並未安裝 Visual J#，也未在任何設定檔指向該 CodeProvider，訊息顯得莫名其妙。  
經過檢查 web.config 與專案屬性皆一無所獲後，只能透過搜尋方式全盤掃瞄，終於在 ~/App_Data/files 找到一支研究所時期遺留的 .java Applet 原始檔。Visual Studio 會將專案目錄下所有可能的「程式碼檔」納入 Build，因而企圖以 J# 編譯該 .java 檔；然而本機並未安裝 J#，遂丟出找不到 VJSharpCodeProvider 的錯誤。刪除該檔後隨即恢復正常。  
此事件說明：  
1. VS 的自動偵測機制可能把 App_Data 內檔案也視為需要編譯的源碼。  
2. 當缺乏對應的語言提供者時，錯誤訊息將十分簡略，不利除錯。  
3. 為避免類似問題，開發者應避免在網站專案—尤其是 App_Data—中存放無關程式或未知副檔名的檔案。作者最後提醒，別再以為 App_Data 是「什麼都能塞」的保險箱。  

## 段落重點
### 問題背景與情境
作者為升級 BlogEngine.NET 至 1.4.5 以及撰寫 SecurePost、PostViewCounter 等外掛，在本機下載官方原始碼並於 VS2008 編譯，一開始全數順利通過。為方便測試，他將生產環境的資料檔（除 App_Data 之外的程式碼已先移入）搬到本機，準備透過模擬正式資料來驗證功能。

### 錯誤訊息與初步觀察
搬移資料後第一次編譯即失敗，唯獨出現「找不到 Microsoft.VJSharp.VJSharpCodeProvider」的訊息，且不附檔名、行號。作者認為 J# 從未在專案中被引用，web.config 與 VS 專案屬性也無任何關聯設定，顯得相當離奇。編譯雖失敗，但網站仍能啟動，只是無法在 IDE 內設定中斷點，對除錯形成阻礙。

### 排除過程與嘗試
作者首先檢查 CodeDom 與各種參考設定，皆無所獲。意識到「無頭無尾」的訊息難以定位，他開始全面搜尋專案目錄，嘗試找出可能觸發 J# 編譯的檔案類型或設定。此時「死馬當活馬醫」的心態促使他鎖定副檔名為 .java 的檔案，因 J# 能編譯 Java 語法。

### 真正原因與解法
搜尋結果在 ~/App_Data/files 發現一支大學時期遺留的 Java Applet 原始檔。Visual Studio 自動將其視為需要編譯的程式碼，因本機未安裝 J#，便拋出找不到 VJSharpCodeProvider 的錯誤。刪除該 .java 檔後，專案立即恢復正常編譯，證實問題根因就是 VS 的自動掃描機制與異質檔案衝突。

### 心得與建議
事件暴露了 VS 網站專案的兩個盲點：一是掃描範圍過廣，連 App_Data 都列入 Build；二是當缺少對應語言提供者時，錯誤訊息過度簡化，增加排錯成本。作者提醒開發者不要過度信賴 App_Data 的「資料專用」形象，任何非必要或非 .NET 語言檔案都應盡量避免置於專案資料夾，以免重蹈覆轍。