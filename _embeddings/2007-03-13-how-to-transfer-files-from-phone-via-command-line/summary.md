# 如何透過命令列，從手機搬檔案到電腦？

## 摘要提示
- 自動化需求: 作者希望把「手機→電腦→相片歸檔」流程寫進批次檔，全程無人工介入。  
- ActiveSync 限制: ActiveSync 的「裝置瀏覽」只是 Shell Extension，無法用傳統檔案路徑搭配 xcopy 存取。  
- RAPI 原理: ActiveSync 其實提供 Remote API（RAPI），能讓 PC 對手機執行檔案與系統操作。  
- rcmd 工具: CodeProject 上現成的 rcmd.exe 封裝 RAPI，可於命令列下 copy、del。  
- 批次檔範例: 建暫存資料夾→複製手機照片→刪除手機端檔案→呼叫 DigitalCameraFiler 歸檔→清理暫存。  
- .NET 自製可能: MSDN 教學示範如何用 .NET 封裝 RAPI 編寫同類工具。  
- OpenNETCF 封裝: 開源 OpenNETCF 通訊元件已把 RAPI 做成 .NET Class Library，功能包含檔案、Registry、遠端啟動程式。  
- 延伸應用: 一旦能在 PC 端自由呼叫 RAPI，可開發更多自動化工具，例如批次備份、裝置資訊收集等。

## 全文重點
作者起初以為把手機相片搬到電腦只要用 ActiveSync 後透過檔案總管拖曳即可，然而真正需求是「完全自動化」。他需要一支能在批次檔執行的命令列工具，把手機上的照片先複製到電腦暫存目錄，再交由 DigitalCameraFiler 依時間、機型自動歸檔，最後刪除暫存及手機原檔。嘗試直接用 xcopy 時才發現 ActiveSync 提供的「Mobile Device」路徑只是 Windows Shell Extension，並非檔案系統實體路徑，因此無法在命令列存取。  
解決之道是使用 ActiveSync 本來就附帶的 Remote API（RAPI）。作者 Google 後找到兩條路：一是 CodeProject 上的 rcmd.exe，已把 RAPI 打包成命令列工具；二是 MSDN 的文章，教人用 .NET 自行撰寫 RAPI 包裝。作者先試 rcmd.exe，成功用 copy、del 指令對手機檔案系統操作，於是以批次檔串連「產生亂數命名暫存目錄→複製 *.jpg→刪除手機端→呼叫 DigitalCameraFiler→清除暫存」整個流程。  
雖然 rcmd 已能解決眼前問題，作者仍閱讀 MSDN 文件，發現 Microsoft 並未推出官方 .NET 版 RAPI Wrapper，但開源組織 OpenNETCF 早已完成，且被 MSDN 文章引用示範。該封裝除了檔案搬移，還能讀取裝置資訊、操作 Registry、在手機遠端啟動程式等，功能完備、程式碼開源，適合日後擴充。最後，作者表示下次想自己動手用 OpenNETCF 開發更彈性的自動化工具。

## 段落重點
### 為何還要研究命令列搬檔案？
作者一開始質疑「現代誰還需要命令列搬檔案」，因為 ActiveSync 搭配檔案總管即可拖曳；但當需求改成「每天自動把手機照片歸檔」時，純 UI 操作就不敷使用，必須改用可自動執行且可嵌入批次檔的命令列方式。

### 自動化需求與問題點
核心需求有兩項：1) 能用批次檔全自動執行；2) 能和 DigitalCameraFiler 結合自動歸檔照片。實測後發現 ActiveSync 在檔案總管中的「裝置」其實是 Shell Extension，並非真實路徑，所以 xcopy/move 等指令無法辨識，導致傳統批次檔操作行不通。

### 搜尋並比較兩種解決方案
作者搜尋到兩個方案：1) CodeProject 的 rcmd.exe 直接把 RAPI 封裝成 CLI 工具，可即刻使用；2) MSDN 文章示範以 .NET 撰寫 RAPI Wrapper，自行打造工具。權衡後先採用現成 rcmd 以求快速落地，但仍對第二方案保持興趣。

### 實作範例 – 批次檔流程
利用 rcmd.exe，作者寫出批次檔：產生亂數暫存資料夾、將手機 \Storage Card\My Pictures\*.jpg 複製到暫存、刪除手機原檔、呼叫 DigitalCameraFiler 進行時間與資料夾規則歸檔，再刪掉暫存夾並清空變數。整個流程可每日排程，自動完成備份與分類。

### OpenNETCF RAPI 封裝與延伸應用
進一步閱讀資料後，作者發現 OpenNETCF 已把 RAPI 做成完整 .NET Class Library，不僅能搬檔案，還支援讀取裝置序號、IMEI、操作 Registry，甚至可以遠端在手機執行程式。由於程式碼開源，日後可自行擴充，包括批次備份、裝置健康檢查、遠端部署等自動化腳本，都能因這個封裝而大幅簡化開發工作。