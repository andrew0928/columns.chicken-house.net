# Canon Digital Camera 相機獨享 - 記憶卡歸檔工具

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這篇文章的工具主要想解決哪些數位相片管理上的痛點？
1. 照片與影片需要依拍攝日期及主題自動分目錄。  
2. 兩台以上相機可能造成檔名重複衝突。  
3. 直式拍攝的照片需要自動旋轉。  
4. 使用者希望透過命令列一次完成搬移、命名，而不必安裝龐大的圖形化軟體。

## Q: 市面上已有哪些現成軟體可以處理這些需求？作者為何仍自己動手寫？
現成方案例如 Google Picasa、Adobe Album、ACDSee 都能完成上述管理工作，但作者不想額外安裝「五四三」的 GUI 軟體，偏好在 Windows 內建 Image Viewer 配合簡單的命令列工具，於是決定自行撰寫。

## Q: 作者最初的批次檔 copypic.cmd 如何整理照片與影片？
1. 依「日期＋主題」建立資料夾，例如  
   c:\photos\2006-0101 [去公園]\IMG_9999.jpg  
2. 影片 *.avi 另外存放，命名格式為  
   c:\videos\2006-0101 [去公園 #MVI_9999].avi  
3. 只要在命令列輸入  
   copypic.cmd 主題（或 copypic.cmd 主題 日期）  
   即可完成搬移與重新命名。

## Q: 為什麼批次檔仍然不夠用，迫使作者改寫為 DigitalCameraFiler.exe？
批次檔存在下列限制：  
1. 只能用「複製當下」的系統日期，無法精確以 EXIF 真實拍攝日期歸檔。  
2. 一次複製多天的照片時無法分開存放。  
3. 無法依相機型號自動區分檔名。  
4. 做不到自動旋轉照片。  
因此作者以 .NET 2.0 重新開發 DigitalCameraFiler.exe 來補足這些功能。

## Q: 使用 DigitalCameraFiler.exe 前需要做哪些設定？
1. 電腦需先安裝 Microsoft .NET Framework 2.0。  
2. 編輯 DigitalCameraFiler.exe.config，設定  
   • default.title – 預設主題名稱  
   • video.targetPattern – *.avi 目標路徑命名規則  
   • general.targetPattern – *.crw 目標路徑命名規則  
   • photo.targetPattern – *.jpg 目標路徑命名規則  
   • arguments – 代入 {0}~{4} 的欄位順序（如 EXIF 時間、相機型號…）。

## Q: 實際執行 DigitalCameraFiler.exe 的指令與結果範例為何？
於 DOS Prompt 執行：  
DigitalCameraFiler.exe F:\ 公園外拍  
其中 F:\ 為記憶卡根目錄，「公園外拍」為主題。  
完成後 *.jpg 會被搬到例：  
c:\photos\2006-1102 [公園外拍]\Canon PowerShot G2 #IMG_1234.jpg

## Q: 如果我想直接下載這套工具，該到哪裡取得？
作者已提供壓縮檔下載：  
http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip