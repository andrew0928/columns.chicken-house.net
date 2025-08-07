# Canon Digital Camera 記憶卡歸檔工具 – Release Notes

# 問題／解決方案 (Problem/Solution)

## Problem: 無法快速且一致地整理數位相機記憶卡中的照片、RAW 與影片檔案  

**Problem**:  
攝影完畢後要將記憶卡中的 JPEG、RAW 及影片檔搬到電腦硬碟，若手動操作必須：  
1. 逐一檢視檔名 (IMG_XXXX.JPG、CRW_XXXX.CRW …) 並重新命名  
2. 依日期或拍攝資訊自行建立多層資料夾  
3. 確認檔案轉向、RAW 轉 JPG、EXIF 保留等額外工序  
流程繁雜、容易出錯，也不利於後續搜尋與長期備份。

**Root Cause**:  
• 相機預設檔名與目錄結構不具備語意 (僅流水號)。  
• EXIF 雖儲存了日期、機型、光圈、快門等資訊，Windows 檔案系統卻不會自動利用。  
• 使用者缺乏一個能「一次性批次處理 + 彈性命名規則」的工具。  

**Solution**:  
開發 DigitalCameraFiler (純 Console App)，提供：  
1. 指定來源目錄後自動遞迴掃描所有檔案。  
2. 以 .NET Format String 設定 `pattern` 結合 EXIF 欄位命名目錄/檔名：  
   ```xml
   <!-- DigitalCameraFiler.exe.config -->
   <appSettings>
     <!-- {0}=DateTime {1}=Model {2}=FileName -->
     <add key="Pattern.JPEG"  value="c:\photos\{0:yyyy-MM-dd}\{1}-{2}" />
     <add key="Pattern.RAW"   value="c:\photos\RAW\{0:yyyy-MM-dd}\{1}-{2}" />
     <add key="Pattern.VIDEO" value="c:\videos\{0:yyyy-MM-dd}\{1}-{2}" />
     <add key="ExifList"      value="DateTime,Model,FileName" />
   </appSettings>
   ```
3. 不存在的路徑自動建立，可與任何批次檔或排程工具整合。  
4. 執行不帶參數時顯示所有可用 EXIF 變數 (便於自訂格式)。  

**Cases 1**:  
• 使用者將 2006/11/11 由 Canon G2 拍攝之 `IMG_1234.JPG` 匯出。  
• pattern 套用後，自動建立 `c:\photos\2006-11-11\Canon PowerShot G2-IMG_1234.jpg`。  
• 全程零手動操作，檔名具備日期與機型語意，便於搜尋。  

---

## Problem: JPEG 相片在電腦上顯示經常橫放或倒置  

**Problem**:  
大量照片匯入電腦後，常見部份畫面旋轉方向不正確，瀏覽時需逐張手動旋轉。

**Root Cause**:  
相機僅在 EXIF `Orientation` 標籤寫入旋轉資訊，而非真正去旋轉像素。許多檔案管理器或影像瀏覽器不讀取該標籤，導致顯示方向錯誤。

**Solution**:  
DigitalCameraFiler 在處理 `*.jpg` 時：  
1. 讀取 EXIF `Orientation`。  
2. 於歸檔前以程式邏輯 (GDI+/WIC) 真正旋轉影像像素，並重寫 EXIF 為「正常」。  

**Cases**:  
• 1000 張照片批次處理後，所有縮圖與投影片播放皆為正向；省去手動旋轉約 30 分鐘工作量。  

---

## Problem: Canon RAW (.crw) 讀取不便且轉檔易遺失 EXIF  

**Problem**:  
攝影師需同時保留 .CRW 原檔與 .JPG 參考檔，但傳統流程需先手動轉檔，再補植 EXIF、搬動檔案，冗長且容易造成 RAW/JPG 檔案分離。

**Root Cause**:  
• Canon RAW 檔的 EXIF 多存放於對應的 `.thm` 副檔名檔案。  
• 多數轉檔器未自動抓取 .THM 內容，造成轉檔後 Metadata 遺失。  

**Solution**:  
1. 掃描到 `.crw` 時，同步尋找同名 `.thm`。  
2. 將 `.crw` 直接依 pattern 歸檔。  
3. 以內建轉檔函式轉出 `.jpg`，並把 `.thm` 中所有 EXIF 全量複製到新圖檔。  
4. RAW 與轉檔 JPG 置於同一目錄，名稱一致，方便 Lightroom/Bridge 對應。  

**Cases**:  
• 500 張 RAW 一鍵匯入後立即獲得對應 `*.jpg`，且保留原始光圈/快門值；後製軟體可直接讀取，省去人工補 EXIF 的 100% 時間。  

---

## Problem: Canon MJPEG 影片檔 (.avi) 缺乏拍攝日期等檔案層級資訊  

**Problem**:  
`.avi` 本身不含拍攝日期與機型資訊，長期歸檔時僅靠流水號檔名難以追溯拍攝時間點。

**Root Cause**:  
與 RAW 相同，Canon 會為每支影片產生 `.thm` 檔存放 EXIF；若手動搬移時只關注 `.avi`，Metadata 即遺失。

**Solution**:  
歸檔時自動：  
1. 先找出 `.avi` 對應 `.thm`。  
2. 解析 `.thm` 取得 `DateTime`, `Model` 等欄位。  
3. 依使用者指定 pattern 建立目錄與重新命名 `.avi`。  

**Cases**:  
• 年底整理 200 支 `.avi` 檔，只花 1 分鐘完成自動歸檔；每支影片檔名即含拍攝日期與機型，搜尋效率提升 >90%。  

---

以上四大問題透過 DigitalCameraFiler 皆可一次解決，將原需數小時的人工歸檔流程縮短為單指令批次執行，並確保所有元資料完整保留。