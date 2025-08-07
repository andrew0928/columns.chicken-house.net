# Canon Digital Camera 記憶卡歸檔工具 - Release Notes

## 摘要提示
- Console工具: 無視窗介面的純 Console Application，可與批次檔等自動化工具整合。
- Exif歸檔: 依照拍攝日期、相機型號、光圈值等 Exif 資訊自動產生目錄與檔名。
- JPEG旋轉: 解析 Orientation 欄位，先將相片自動轉正再存入目的地。
- RAW支援: 處理 Canon *.crw + *.thm，並同步轉出對應 JPEG，完整複製 Exif。
- 影片歸檔: 支援 Canon MJPEG *.avi，透過 .thm 檔取得拍攝資訊後歸檔。
- 可自訂格式: 以 .NET Format String 描述路徑與檔名，不存在的目錄會自動建立。
- Exif清單查詢: 執行程式不帶參數即可列出所有可用的 Exif 變數名稱。
- 輕量部署: ZIP 下載後即可執行，後續僅維護 Bug，不再大幅改版。
- 原始碼預告: 下一階段將公開完整 Source Code 供社群參考與改進。

## 全文重點
作者針對 Canon 數位相機記憶卡整理需求撰寫了「DigitalCameraFiler」這支工具。它是一個無 GUI、純 Console 的小程式，可掃描記憶卡或任意目錄，依照拍攝當下記錄在 Exif 中的各種參數，自動決定檔案最終的存放資料夾與檔名。  
工具主要支援三大檔案類型：  
1. JPEG：讀取 Orientation 資訊，自動旋轉後歸檔。  
2. RAW (*.crw)+*.thm：擷取 Exif 後將 RAW 移至指定位置，同時轉出一份 JPEG 並複製所有 Exif。  
3. MJPEG 影片 (*.avi)+*.thm：同樣根據 .thm 內的 Exif 決定歸檔路徑。  

使用者可在設定檔 (DigitalCameraFiler.exe.config) 內，以 .NET 標準 Format String 定義各檔案類型專屬的 pattern，再列出欲使用的 Exif 欄位順序。例如 pattern 為 `c:\photos\{0:yyyy-MM-dd}\{1}-{2}`，Exif List 設 `DateTime,Model,FileName`，則會產生 `c:\photos\2006-11-11\Canon PowerShot G2-IMG_1234.jpg`。執行程式時若不帶參數，會列出所有可填入的 Exif 變數名稱，方便制定路徑格式。  
作者表示目前已排除大部分問題，後續除非有 Bug 不再大改版；並預告將釋出原始碼供研究。安裝方式僅需下載並解壓官方提供的 ZIP 即可開始使用，適合與批次腳本及其他工具鏈結成完整的備份／整理流程。

## 段落重點
### Overview
DigitalCameraFiler 專為整理數位相機記憶卡內容而生，可同時處理照片、RAW 與影片檔。透過分析 Exif 產生目錄與檔名，協助使用者快速、有系統地歸檔素材。程式採 Console 形式，方便在自動化流程中呼叫。

### How it work
程式會掃描指定資料夾並依檔案類型套用不同動作：  
• JPEG：讀 Orientation 做自動旋轉後存檔。  
• RAW：讀取 .crw 與 .thm，搬移 RAW 並轉出對應 JPEG，保留完整 Exif。  
• VIDEO：針對 Canon MJPEG .avi，使用相同 .thm 取得日期與機型後歸檔。  
如遇未存在的目錄系統會自動建立，確保檔案結構完整。

### Configuration
所有路徑、檔名規則均寫在 DigitalCameraFiler.exe.config 內。使用者以 .NET Format String 指定 pattern，並列出 Exif 欄位順序；JPEG、RAW、VIDEO 可各設一組 pattern，Exif List 則共用。若想查詢可用的 Exif 欄位，只需在命令列執行程式且不帶任何參數即可。作者提供 ZIP 安裝檔，並預告將於下一版釋出完整 Source Code。