# Canon Digital Camera 記憶卡歸檔工具 - Release Notes

## 摘要提示
- 工具定位: 專為數位相機記憶卡的相片、RAW、影片自動歸檔的 Console 工具
- 支援格式: JPEG、Canon RAW(.crw/.thm)、Canon MJPEG 影片(.avi/.thm)
- EXIF 驅動: 以 EXIF 資訊（時間、相機型號、光圈、快門等）組合檔名與目錄
- 自動轉正: JPEG 依 EXIF Orientation 自動旋轉後再歸檔
- RAW 處理: Canon .crw 搭配 .thm 取 EXIF，並自動轉出對應 .jpg 並複製 EXIF
- 影片對應: 影片以 .thm 檔的 EXIF 作為歸檔依據
- 彈性設定: 以 .NET format string 定義 pattern，支持目錄自動建立
- 參數化: 以 exif list 對應 pattern 中的索引，跨 JPEG/RAW/VIDEO 共用
- 命令列友善: 不帶參數可列出所有可用 EXIF 變數名
- 版本狀態: 主要問題已解決，除非有 Bug 不再大改版；稍後釋出原始碼

## 全文重點
本文介紹「DigitalCameraFiler」這款專為數位相機記憶卡歸檔的工具，設計目標是在無圖形介面的情況下，透過命令列與批次流程，自動將照片、RAW 檔與影片依 EXIF 資訊命名並分類到指定目錄。工具支援 JPEG、Canon RAW(.crw) 與 Canon MJPEG 影片(.avi)，針對不同格式採用相應策略：JPEG 會先依 EXIF Orientation 自動轉正再存放；Canon RAW 會結合對應的 .thm 取 EXIF，除歸檔 .crw 外，並自動轉出同名 .jpg 並複製 EXIF；影片則以配對的 .thm 取得時間與機型等資料進行歸檔。

工具的設定採 .NET 常用的格式化字串（format string）機制，使用 pattern 與 exif list 搭配：pattern 中以 {索引:格式} 指向 exif list 中的變數，支援時間格式化（如 yyyy-MM-dd）與多變數組合。使用者可為 JPEG、RAW、VIDEO 各自指定不同的 pattern，exif list 則共用；若目標目錄不存在，工具會自動建立。命令列不帶參數即可列出所有可用 EXIF 變數名稱，方便查詢與配置。文章以範例說明：設定 pattern 為 c:\photos\{0:yyyy-MM-dd}\{1}-{2}，exif list 為 DateTime,Model,FileName 時，G2 於 2006/11/11 拍攝之 IMG_1234.jpg 會被歸檔為 c:\photos\2006-11-11\Canon PowerShot G2-IMG_1234.jpg。作者表示目前功能穩定，除非發現 Bug 不會再大改版，後續將釋出原始碼，並提供安裝檔下載連結供使用者試用或部署於自動化流程。

## 段落重點
### Overview
DigitalCameraFiler 是一款命令列（Console）工具，目標是將記憶卡中的各類相機檔案（相片、RAW、影片）自動依據 EXIF 資訊進行命名與歸檔。支援以拍攝時間、相機型號、光圈值、快門值等欄位組合出檔案與目錄結構。因為無 GUI，特別適合與批次檔、排程或其他自動化工具串接，建置個人的影像歸檔流程。作者表示工具已趨於穩定，未來除非遇到 Bug，原則上不再進行大改版。

### How it work
工具會掃描指定來源（如記憶卡）下所有檔案，遇到支援的類型即依規則處理：
- JPEG：先讀取 EXIF 的 Orientation 判斷是否需旋轉，轉正後再放入目標位置。
- RAW：支援 Canon .crw，搭配對應 .thm 取得必要 EXIF；除將 .crw 歸檔外，會轉出 .jpg 並將 .thm 的 EXIF 複製到該 .jpg，確保縮圖或後續流程能沿用拍攝資訊。
- VIDEO：支援 Canon MJPEG .avi，並以對應 .thm 中的 EXIF 為歸檔依據，解決影片本體缺乏完整 EXIF 的問題。
整體流程簡潔，著重一致與可重複的自動化處理。

### Configuration
設定依 .NET 的格式化字串機制進行：以 pattern 定義目錄與檔名格式，並以 exif list 提供可替換的變數來源。pattern 中的 {索引:格式} 會對應 exif list 的項目（從 0 起算），例如 pattern 為 c:\photos\{0:yyyy-MM-dd}\{1}-{2}，exif list 為 DateTime,Model,FileName，則可產生 c:\photos\2006-11-11\Canon PowerShot G2-IMG_1234.jpg。目錄若不存在會自動建立。可分別為 JPEG/RAW/VIDEO 指定不同 pattern，以符合不同媒體的命名需求；exif list 則共用。執行程式不帶參數可列出所有可用 EXIF 變數，便於查表設置。設定存於 DigitalCameraFiler.exe.config。作者並提供安裝檔下載，且預告將釋出原始碼，方便社群使用與擴充。

## 資訊整理

### 知識架構圖
1. 前置知識：
- 基本檔案系統與目錄結構觀念
- EXIF 基礎（常見欄位如 DateTime、Model、Orientation 等）
- .NET 應用程式設定檔（App.config）與格式化字串（format string）
- 相機檔案類型差異：JPEG、RAW（Canon .crw + .thm）、VIDEO（MJPEG .avi + .thm）

2. 核心概念：
- EXIF 驅動的自動歸檔：以 EXIF 欄位組合生成目錄/檔名
- 檔案型別處理流程：JPEG 轉正、RAW 轉 JPG 並複製 EXIF、VIDEO 依 THM 歸檔
- 格式化規則：pattern + exif variable list 的對應與佔位使用
- 無介面批次化：Console app 可納入批次/自動化流程
- 設定集中化：不同檔類型各自 pattern，共用 EXIF 變數表

3. 技術依賴：
- .NET Framework（Console Application、格式化字串、App.config）
- EXIF 解析與存取（包含從 .thm 讀取）
- 影像處理：自動旋轉（依 Orientation）、RAW 轉 JPG、EXIF 複製
- 檔案系統操作：掃描、分類、目錄自動建立

4. 應用場景：
- 數位相機記憶卡批次歸檔（旅行、活動後一次整理）
- 攝影工作流程前置整理（按日期/機身/檔名歸檔）
- 無人值守的自動備份與檔名正規化
- 舊相簿整理（依拍攝時間重建時間軸）

### 學習路徑建議
1. 入門者路徑：
- 了解 EXIF 欄位與常見用途（DateTime、Model、Orientation、FileName）
- 安裝並執行工具：先不帶參數列出可用 EXIF 變數
- 在 DigitalCameraFiler.exe.config 設定簡單 pattern，例如按日期/機型/檔名
- 先用小量測試資料驗證目錄與命名是否符合預期

2. 進階者路徑：
- 為 JPEG/RAW/VIDEO 分別設定不同 pattern；測試各類型案例
- 熟悉 RAW（.crw）與 .thm 關係，驗證 EXIF 複製與轉 JPG 的結果
- 整合批次檔或排程（Windows Task Scheduler）實現自動化
- 增加錯誤處理與日誌收集（觀察非支援格式與 EXIF 缺漏情境）

3. 實戰路徑：
- 針對多機身與多記憶卡來源制定統一檔名規範
- 在導入正式流程前，於備份副本上演練一次完整跑批
- 與後續影像處理軟體（如 Lightroom）之匯入規則對齊（避免重複改名）
- 導入版本控管與設定檔備份，確保 pattern 變更可追溯

### 關鍵要點清單
- 支援檔案型別範圍: 支援 JPEG、Canon RAW (.crw + .thm)、Canon MJPEG (.avi + .thm) 的自動歸檔 (優先級: 高)
- EXIF 驅動歸檔: 以 EXIF 欄位組合生成目錄與檔名，實現一致化與可追溯 (優先級: 高)
- 格式化字串 pattern: 使用 {索引:格式} 方式，對應 EXIF 變數清單順序替換 (優先級: 高)
- EXIF 變數清單: exif list 以序號從 0 起計，提供給 pattern 各佔位使用 (優先級: 高)
- 以 Orientation 自動轉正: JPEG 依 EXIF Orientation 旋轉後再歸檔，避免後續顯示方向錯誤 (優先級: 中)
- RAW/.thm 雙檔處理: .crw 需搭配 .thm 取得 EXIF；同時輸出 .crw 與轉檔後 .jpg (優先級: 高)
- EXIF 複製到 JPG: 轉換 RAW 為 JPG 時，將 .thm 的 EXIF 複製到新 JPG 檔 (優先級: 中)
- VIDEO 依 .thm 歸檔: Canon MJPEG .avi 以對應 .thm 的 EXIF 作為歸檔依據 (優先級: 中)
- 目錄自動建立: pattern 所指路徑若不存在會自動建立，降低人工前置作業 (優先級: 中)
- 分類設定獨立: JPEG/RAW/VIDEO 各自可定義 pattern；EXIF 變數表共用 (優先級: 中)
- Console 應用特性: 無 GUI、易於批次與自動化整合（排程、批次檔） (優先級: 中)
- 列出可用變數: 不帶參數執行可輸出所有支援 EXIF 變數名稱 (優先級: 中)
- 相容性限制: 目前聚焦 Canon 格式（.crw、含 .thm 的 .avi），他牌/他格式需評估 (優先級: 中)
- 設定檔位置: DigitalCameraFiler.exe.config 為主要配置入口，便於版本控管 (優先級: 中)
- 下載與部署: 以提供的安裝包下載與解壓即可使用，適合隨身碟/臨時環境 (優先級: 低)