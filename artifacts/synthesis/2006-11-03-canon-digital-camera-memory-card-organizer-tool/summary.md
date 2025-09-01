# Canon Digital Camera 相機獨享 - 記憶卡歸檔工具

## 摘要提示
- 使用痛點: 相片與影片歸檔繁瑣，含日期整理、檔名衝突、直拍旋轉與多機混用問題
- 現有工具: Picasa、Adobe Album、ACDSee 可解，但作者偏好免 GUI、命令列自動化
- 批次檔方案: 以 Windows 批次檔自動移動 JPG/CRW/AVI，依日期與主題命名並清除 THM
- 批次檔命名規則: 照片至 c:\photos\日期 [主題]，影片至 c:\videos\日期 [主題 #檔名]
- 批次檔不足: 日期依複製時間不精確、跨日混檔、相機名稱無法入檔名、無法自動轉正
- 工具轉進: 自製 .NET 2.0 命令列工具 DigitalCameraFiler，讀 EXIF 改善精確性
- 設定檔機制: 以 appSettings 配置 targetPattern 與 arguments，彈性定義輸出路徑與檔名樣式
- 多格式支援: 針對 JPG/CRW/AVI 各自對應 general/photo/video 目標路徑與命名
- 命令列用法: DigitalCameraFiler.exe <記憶卡路徑> <主題>，一鍵完成歸檔
- 輸出示例: c:\photos\yyyy-MMdd [主題]\相機型號 #原始檔名.jpg，含相機資訊與正確日期

## 全文重點
作者以數位相機日常管理為出發，點出大量拍攝後歸檔的常見困擾：以日期與主題分門別類的繁瑣、影片與相片混放、直拍照片需旋轉、以及家中多台 Canon 相機導致檔名衝突。雖然市面上如 Picasa、Adobe Album、ACDSee 等工具能解決，但作者偏好輕量、無 GUI 的命令列流程，因此先以 Windows 批次檔構建自動化：從記憶卡 DCIM 扫描 JPG/CRW/AVI，移動到依日期與主題命名的目錄，影片則另行分流並刪除 THM 縮圖。此方案已能快速整理，並提供簡易的使用方式（copypic.cmd 主題 [日期]）。

然而批次檔的限制明顯：日期只能用複製當下時間而非拍攝時間，跨日歸檔不準確；多天照片易混在一起；無法在命名中帶入相機型號以避免重名；直拍自動旋轉也不易。考量需讀取 EXIF 等進階資訊，作者改以 .NET 2.0 開發命令列工具 DigitalCameraFiler，完全取代批次檔。工具透過設定檔 appSettings 定義輸出規則：以 video.general.photo 三組 targetPattern 指定 AVI/CRW/JPG 的目錄與檔名模式，並以 arguments 決定占位符對應的檔案屬性（如 LastWriteTime、Title、Model、Name、FileNameWithoutExtension）。執行方式為 DigitalCameraFiler.exe <來源路徑> <主題>，若未給主題則以 default.title 代替。示例輸出包含日期、主題、相機型號與原始檔名，實現準確日期歸檔、按機型區分與規模化整理。最後提供下載連結，供偏好命令列的使用者直接導入工作流程。

## 段落重點
### 背景與問題描述
作者指出數位攝影的普及帶來管理難題：拍攝成本低導致照片暴增，單靠手動整理既費時又容易出錯。常見痛點包含：以拍攝日期為目錄命名的麻煩、相機錄製的影片歸檔斷裂、直拍照片需逐張旋轉、以及多台相機檔名（如 IMG_XXXX）重複造成衝突。雖然 Google Picasa、Adobe Album、ACDSee 等軟體提供完整管理功能，但作者不想安裝沉重且具圖形介面的軟體，更偏好在 Windows XP 內建檢視器基礎上，用簡單、可腳本化的命令列工具把記憶卡內容自動搬至規範化的目的地結構，追求可重複、低干擾、可批次執行的最小化解決方案。

### 批次檔自動化方案與成效
第一版解決方案為 Windows 批次檔。設計重點：以當天日期與手動輸入的主題組合成目錄名稱；遞迴掃描記憶卡 F:\DCIM，將 JPG、CRW 依序移動至 c:\photos\yyyy-MMdd [主題]\，AVI 影片則移動到 c:\videos\input [dc-avi]\yyyy-MMdd [主題 #原始檔名].avi，並清除 THM 縮圖以避免冗餘。使用上只需執行 copypic.cmd 主題 或 copypic.cmd 主題 指定日期，即可完成一鍵歸檔。此流程已快速解決多數日常整理需求，將相片與影片分流，並以統一的路徑規則維持一致性與可搜尋性，顯著降低手動搬移與命名錯誤的風險。

### 批次檔限制與改進需求
在長期使用中，批次檔的侷限浮現：一是日期不精確，因缺乏讀取 EXIF 能力，只能用複製時間，導致晚間跨日操作時日期錯置；二是多日拍攝內容無法依拍攝實際日期自動拆分，累積後更難分離；三是無法將相機型號加入檔名或路徑，因此多機拍攝時容易檔名撞車；四是自動旋轉直拍照片（依 EXIF Orientation）在批次層面難以實現。綜合以上，作者認為要徹底解決需讀取檔案的中繼資料（EXIF、檔案屬性），批次語言難以勝任，因而決定開發一個小型、無 GUI 的 .NET 工具，保留命令列使用體驗，同時取得更精確與可客製的歸檔能力。

### .NET 工具 DigitalCameraFiler 的設計與設定
作者以 .NET Framework 2.0 開發 DigitalCameraFiler.exe，透過設定檔 appSettings 提供高度可配置性：default.title 為未提供主題時的預設值；video.targetPattern、general.targetPattern、photo.targetPattern 分別定義 AVI、CRW、JPG 的輸出路徑與檔名模式，並使用 {0}、{1}… 的占位符。arguments 指定各占位符所對應的屬性順序，例如 LastWriteTime、Title、Model、Name、FileNameWithoutExtension，使日期、主題、相機型號、完整檔名或去副檔名等皆可彈性拼組。藉由讀取 EXIF 與檔案屬性，能以拍攝時間精準歸檔、把相機型號納入命名、區分不同格式至對應資料夾，全面解決批次檔的痛點，並保有簡潔的命令列工作流。

### 使用方式與輸出實例
使用者先安裝 .NET Framework 2.0，編輯 DigitalCameraFiler.exe.config 以符合自身路徑命名偏好。執行時於命令列輸入 DigitalCameraFiler.exe <來源路徑> <主題>，例如 DigitalCameraFiler.exe F:\ 公園外拍。工具會依設定自動掃描記憶卡資料夾，將 JPG 依 photo.targetPattern、CRW 依 general.targetPattern、AVI 依 video.targetPattern 產出目標檔案。示例輸出為 c:\photos\2006-1102 [公園外拍]\Canon PowerShot G2 #IMG_1234.jpg，體現以拍攝日期、主題、相機型號、原始檔名構成的規範化命名。此設計強化可讀性、可搜尋性與跨設備一致性，並為後續備份、後製、分享提供穩定基礎。文末提供下載連結，方便偏好命令列的使用者直接導入日常歸檔流程。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - Windows 檔案系統與路徑操作基礎
   - 命令列與批次檔（.cmd/.bat）基本語法
   - 數位相機檔案結構（如 DCIM 目錄）
   - EXIF/檔案時間等中繼資料概念
   - .NET Framework 2.0 安裝與 app.config 設定

2. 核心概念：
   - 照片歸檔自動化：依日期、主題、機型與檔名模式自動移動與命名檔案
   - 模式化命名（pattern-based naming）：以占位符 {0}…{n} 搭配可配置 arguments 動態產生目標路徑/檔名
   - EXIF/檔案屬性取用：用拍攝時間（或最後寫入時間）、相機型號等資訊決定歸檔位置與名稱
   - 媒體類型分流：照片（jpg）、原始檔（crw）、影片（avi）分別輸出到不同目的地
   - 輕量命令列流程：無需 GUI 應用，透過一行指令完成卡片歸檔

3. 技術依賴：
   - 批次檔方案依賴：Windows CMD、基本檔案操作指令（move、del、for /R）
   - 進階工具方案依賴：Microsoft .NET Framework 2.0、可讀 EXIF/檔案屬性之程式庫（文中隱含於工具內）
   - 設定驅動：app.config 中的 appSettings 決定各類檔案的 targetPattern 與 arguments 對應

4. 應用場景：
   - 需快速、重複地將記憶卡內容依日期/主題/機型整理歸檔
   - 多台相機混用，避免檔名（如 IMG_9999）衝突
   - 想將影片與照片分開管理，並清理相機產生的副檔（如 .thm）
   - 不想安裝重量級相片管理軟體（Picasa、Adobe Album、ACDSee），偏好命令列與可客製化命名

### 學習路徑建議
1. 入門者路徑：
   - 理解 DCIM 結構與常見副檔名（jpg/crw/avi/thm）
   - 直接使用現成批次檔範例，學會修改來源（記憶卡槽）與目標路徑
   - 安裝 .NET Framework 2.0，下載並執行 DigitalCameraFiler.exe，嘗試預設 config 進行一次歸檔

2. 進階者路徑：
   - 讀懂並調整 app.config 的 targetPattern 與 arguments（熟悉 {index} 對應與時間格式字串）
   - 新增或改寫不同副檔名的處理規則（如增加 RAW 格式、副檔案清理）
   - 以 EXIF/檔案時間分日/分段歸檔，驗證跨天拍攝的歸檔正確性
   - 建立主題命名慣例，將主題參數納入日常工作流

3. 實戰路徑：
   - 以 .NET 撰寫/擴充自己的歸檔工具：讀取 EXIF、建立模式化命名、處理衝突與錯誤
   - 寫額外腳本自動偵測記憶卡插入後執行歸檔（排程或事件觸發）
   - 整合備份流程（例如：歸檔後同步到 NAS/雲端、產生校驗碼/日誌）
   - 增加後處理步驟（如縮圖、影片轉碼、報表輸出）

### 關鍵要點清單
- 問題痛點盤點: 歸檔麻煩、跨天日期不準、影片/相片混放、檔名衝突 (優先級: 高)
- 批次檔基礎解法: 用 for/move/del 自動搬運與清理，快速可用 (優先級: 中)
- 批次檔限制: 無法精準用 EXIF 拍攝時間、難以多日區分與機型命名 (優先級: 高)
- 進階工具思路: 以 .NET 製作命令列工具，補足 EXIF 與模式化命名 (優先級: 高)
- 媒體分流策略: 照片、RAW、影片分別輸出至不同根目錄 (優先級: 中)
- 模式化命名 targetPattern: 使用 {index} 占位與日期格式化控制路徑/檔名 (優先級: 高)
- arguments 映射: LastWriteTime、Title、Model、Name、FileNameWithoutExtension 的對位關係 (優先級: 高)
- 主題參數設計: 執行時帶入主題，搭配 default.title 作為備援 (優先級: 中)
- EXIF/時間來源: 優先以拍攝或檔案時間作歸檔依據，解決跨日誤差 (優先級: 高)
- 命名避免衝突: 將相機型號或原檔名併入檔名，減少多機重名 (優先級: 高)
- 附檔管理: 刪除 .thm 等副檔，避免目錄污染 (優先級: 低)
- 依需求客製: 為 jpg/crw/avi 設不同 targetPattern（如含「#{原檔名}」） (優先級: 中)
- 執行範例與流程: DigitalCameraFiler.exe <來源路徑> <主題> 一次完成 (優先級: 中)
- 環境相依: 需安裝 .NET Framework 2.0，並具存取記憶卡路徑權限 (優先級: 中)
- 擴充與自動化: 可再結合排程/事件、備份、縮圖/轉碼等後續流程 (優先級: 低)