# 如何透過命令列, 從手機搬檔案到電腦?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼不能直接用 xcopy 或檔案總管路徑把手機檔案搬到電腦?
因為 ActiveSync 的「Browse Device」只是一個 shell extension，並沒有真正對外暴露檔案系統路徑，命令列工具 (如 xcopy) 無法識別，無法放進批次檔做自動化。

## Q: 作者想解決的兩項核心需求是什麼?
1. 整個流程必須能自動化並寫進批次檔。  
2. 要能和 DigitalCameraFiler 搭配，將手機相片自動歸檔。

## Q: 作者最後採用哪種方式來滿足需求?  
作者下載並使用 CodeProject 上的 rcmd.exe (以 RAPI 為基礎的命令列工具)，在批次檔中先把手機上的照片複製到電腦暫存目錄，再交給 DigitalCameraFiler 進行歸檔。

## Q: 批次檔的大致流程是什麼?
1. 以亂數建立一個暫存資料夾。  
2. 用 `rcmd.exe copy` 把手機 `\Storage Card\My Documents\My Pictures\*.jpg` 複製到該暫存夾。  
3. 用 `rcmd.exe del` 刪掉手機上已複製的照片。  
4. 呼叫 DigitalCameraFiler 對暫存夾進行相片歸檔。  
5. 刪除暫存資料夾並清理環境變數。

## Q: 如果不想直接用 rcmd.exe，還有其他做法嗎?
可以參考 MSDN 的文章，照範例自己用 .NET 撰寫基於 RAPI 的工具，功能與 rcmd.exe 類似。

## Q: Microsoft 有沒有提供官方的 .NET 版 RAPI 封裝?
沒有。Microsoft 只提供原生 RAPI。若要在 .NET 中使用，通常會採用 OpenNETCF 提供的 RAPI wrapper；連 MSDN 範例文章也引用該開源專案。

## Q: OpenNETCF 的 RAPI wrapper 除了搬檔案，還能做什麼?
在手機透過 ActiveSync 連線後，該 wrapper 可取得裝置詳細資訊、讀寫 Registry，甚至遠端呼叫手機上指定的程式，功能相當完整。