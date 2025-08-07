# Canon Digital Camera 記憶卡歸檔工具 - Release Notes

# 問答集 (FAQ, frequently asked questions and answers)

## Q: DigitalCameraFiler 是什麼？能解決什麼問題？
DigitalCameraFiler 是一套專為「數位相機記憶卡歸檔」而寫的 Console 應用程式。它會依照相片／影片的 EXIF 資訊（拍攝時間、相機型號、光圈、快門等）自動重新命名檔案並建立對應目錄，讓使用者能快速、有條理地把 JPEG、RAW、Video Clip 等檔案從記憶卡歸檔到電腦中。

## Q: 這個工具有圖形化介面嗎？
沒有。DigitalCameraFiler 只有命令列（Console）介面，方便搭配批次檔或其他自動化工具一起使用。

## Q: DigitalCameraFiler 支援哪些檔案類型？各自會怎麼被處理？
1. JPEG (*.jpg)：先透過 EXIF 的 Orientation 欄位判斷是否需要自動旋轉，旋轉完後再移動到指定位置。  
2. RAW (*.crw)：支援 Canon CRW 檔及其對應的 .thm 檔。除了歸檔 .crw，還會額外轉出一份 .jpg，並把 .thm 裡的 EXIF 全數複製到該 .jpg。  
3. Video (*.avi)：支援 Canon 的 MJPEG 檔案，同樣讀取對應 .thm 裡的 EXIF 來決定歸檔路徑與檔名。

## Q: 我可以為不同檔案類型設定不同的歸檔路徑格式 (pattern) 嗎？
可以。JPEG / RAW / VIDEO 的 pattern 可以分別設定；EXIF 變數清單 (exif list) 則共用。所有設定都寫在 DigitalCameraFiler.exe.config 裡。

## Q: pattern 與 exif list 的語法是什麼？有範例嗎？
pattern 採用 .NET 標準的 format string 語法，`{index:format}` 代表用 exif list 中對應索引的變數並用指定格式輸出。  
範例：  
  pattern：`c:\photos\{0:yyyy-MM-dd}\{1}-{2}`  
  exif list：`DateTime,Model,FileName`  
假設檔名為 IMG_1234.jpg、拍攝日期 2006/11/11、相機型號 Canon PowerShot G2，歸檔結果為  
`c:\photos\2006-11-11\Canon PowerShot G2-IMG_1234.jpg`。  
不存在的目錄會自動建立。

## Q: 可以使用的 EXIF 變數有哪些？要怎麼查？
在命令列執行 DigitalCameraFiler.exe 並且「不帶任何參數」，程式就會列出目前支援的全部 EXIF 變數名稱。

## Q: 下載安裝檔的位置在哪裡？
Binary 安裝檔可從以下網址下載：  
http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip

## Q: 之後會公開原始碼嗎？
會。作者表示下次發佈時會連同 source code 一併釋出，請耐心等待。