---
layout: synthesis
title: "Canon G9 害我沒睡好... 相片自動轉正的問題"
synthesis_type: summary
source_post: /2008/08/28/canon-g9-kept-me-awake-photo-auto-rotation-problem/
redirect_from:
  - /2008/08/28/canon-g9-kept-me-awake-photo-auto-rotation-problem/summary/
---

# Canon G9 害我沒睡好... 相片自動轉正的問題

## 摘要提示
- 問題起因: 直拍照片有的會自動轉正、有的卻不會，導致觀看體驗不一致
- 方向偵測機制: Canon 相機透過感測器將拍攝方向寫入 EXIF 的 Orientation 欄位
- 機型差異: G9 拍的照片「有機會」自動轉正，IXUS55 拍的 JPG 大多不會自動轉
- 檔案格式影響: G9 的 .CR2 經 RAW Codec 轉 JPG 會自動旋轉；原生 JPG 則不會
- EXIF 讀取路徑: .CR2 與 .JPG 需使用不同的 Metadata Query 路徑才能取得 Orientation
- 值的判讀: Orientation 常見值 6=右轉90、8=左轉90、3=180，0x01 表示不旋轉
- 問題根因: Canon 僅偵測左右 90 度，對於 180 度旋轉場景不處理
- 實務情境: 自拍按不到快門、小孩亂拍等情境常出現 180 度照片
- 程式解法: 以 WPF 讀取 EXIF、決定旋轉角度，並用 TransformGroup 同步縮放與旋轉
- 維護建議: 對 JPG 流程補上 Orientation 判讀與旋轉，避免依賴解碼器自動行為

## 全文重點
作者觀察到使用 Canon 相機拍攝的直向照片，顯示時有的會自動旋轉為正確方向，有的卻不會，甚至存在應該 180 度轉正卻未被處理的案例。基於印象中 Canon 應有方向偵測，作者推測問題與 EXIF 的 Orientation 欄位和處理流程有關，遂展開排查。

首先比較機型與檔案格式：G9 的 .CR2 檔透過 RAW Codec 轉 JPG 時會自動旋轉；但 G9 與 IXUS55 直接拍的 JPG 卻未自動轉正。作者進一步以程式讀取 EXIF，發現 .CR2 與 .JPG 的 Orientation 欄位需透過不同 Metadata Query 路徑存取（.CR2 用 /ifd/{ushort=274}；.JPG 用 /app1/{ushort=0}/{ushort=274}），取得的值在四個測試角度下分別為 0x01、0x08、0x01、0x06。參照定義，0x06=向右 90 度、0x08=向左 90 度、0x03=180 度、0x01=不旋轉。實測中唯獨 180 度案例的值異常，導致自動旋轉流程無法正確處理。

作者進一步比對所有 EXIF 欄位與 BLOB，仍無發現能補強判斷的旗標。最後在相機上直接檢視時才確認：Canon 相機本身對 180 度旋轉場景不做偵測或處理，只支援左右 90 度。在某些實際情境（例如右手自拍為了按快門將相機倒轉、小孩亂拍）確實常會產生 180 度的照片，因此形成「機身與解碼器都不處理、應用程式未補救」的缺口。

為解決問題，作者在 WPF 歸檔程式中補上 Orientation 判讀與旋轉：讀取 EXIF Orientation 值（JPG 走 /app1/{ushort=0}/{ushort=274}），將 6 對應 Rotate90、8 對應 Rotate270、3 對應 Rotate180，並以 TransformGroup 同步套用 ScaleTransform 與 RotateTransform，一次完成縮放與旋轉後再輸出 JPG。對於 RAW 檔案，因 Canon Codec 在解碼階段會幫忙做旋轉，流程相對單純；但對於原生 JPG，必須自行補齊旋轉步驟，才能確保所有方向都能正確顯示。

總結來說，問題的根因是機身偵測策略與後續處理的不一致：Canon 僅針對 90 度旋轉提供可靠的偵測與自動處理，180 度場景則缺乏支援。應用端若不主動解析 EXIF 並補上旋轉，便容易出現顯示方向錯誤。最佳實務是在影像歸檔／縮圖流程中一律讀取 EXIF Orientation，統一做旋轉處理，以避免不同機型、不同檔案格式、不同解碼器行為差異造成的顯示不一致，並對 180 度情境特別加以覆蓋。

## 段落重點
### 問題描述：自動轉正不一致
作者發現直向照片顯示時有的自動轉正、有的沒有，甚至有應轉 180 度卻未處理的案例。回想 Canon 應有方向偵測並寫入 EXIF Orientation，於是懷疑流程中有環節未生效。初步比較後，G9 的 .CR2 經 RAW Codec 轉 JPG 會被自動旋轉；而 G9 與 IXUS55 的原生 JPG 大多不會，顯示出機型與格式差異。

### 調查過程：EXIF 驗證與值對照
作者分別以四種持機角度拍攝，使用 Debugger 檢視 EXIF Orientation，並注意到 .CR2 與 .JPG 的查詢路徑不同（前者 /ifd/{ushort=274}、後者 /app1/{ushort=0}/{ushort=274}）。取得的值為 0x01、0x08、0x01、0x06，其中 0x06 對應右轉 90、0x08 對應左轉 90、0x03 應為 180，但實測 180 度案例卻未得到 0x03，導致流程無法判定該旋轉。大量比對 EXIF 欄位與 BLOB 後仍無新線索。

### 根因釐清：Canon 未支援 180 度偵測
在相機端按下 Display 交叉檢視後確定，Canon 相機本身只偵測左右 90 度，對倒轉 180 度的拍攝並不處理。這解釋了為何 .CR2 透過 Codec 有時能正確（依賴解碼器行為），而原生 JPG 不會；也說明了自拍與小孩拍攝等情境常見的 180 度照片為何顯示錯向。

### 程式實作：WPF 中的 Orientation 處理
作者在自製的縮圖歸檔程式中加入 EXIF Orientation 判讀邏輯：從 JPG 的 /app1/{ushort=0}/{ushort=274} 取值，將 6、8、3 分別對應 Rotate90、Rotate270、Rotate180，並以 TransformGroup 結合 ScaleTransform 與 RotateTransform，一次完成縮放與旋轉後再輸出。對 RAW 依賴 Canon Codec 的自動旋轉；對 JPG 則強制補上旋轉。此作法可跨機型、跨格式地統一顯示方向，彌補機身偵測與解碼器行為的不足。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 數位影像基本概念（像素、旋轉、縮放）
   - EXIF 基礎與常見欄位（特別是 Orientation, Tag 274）
   - C#/.NET 與 WPF 影像處理類別（BitmapMetadata, BitmapFrame, TransformedBitmap, JpegBitmapEncoder）
   - 相機方向偵測原理（傾斜/方向感測器的限制）

2. 核心概念：
   - EXIF Orientation 標記：用於描述相片拍攝時的方向資訊
   - RAW vs JPEG 解碼差異：Codec 是否自動依 Orientation 旋轉
   - 方向值對應與旋轉邏輯：6/8/3 對應 90/270/180 的實作
   - WPF 影像轉換管線：TransformGroup 組合 ScaleTransform + RotateTransform
   - 相機偵測限制：部分相機（文中 Canon 機型）不處理 180 度旋轉

   關係說明：相機在拍攝時（可能）寫入 EXIF Orientation；RAW 檔在 Windows/Codec 解碼時可能自動依 EXIF 旋轉，JPEG 通常需在應用層讀取 EXIF 並自行旋轉；WPF 以 Transform 實作縮放與旋轉；若相機沒正確寫入 180 度，應用端需有補救策略。

3. 技術依賴：
   - 硬體：相機方向偵測器（多為僅能偵測 90° 左右轉）
   - 檔案格式與編碼：CR2（RAW）需對應 Canon RAW Codec；JPEG 以 APP1/EXIF 區塊存取
   - .NET/WPF 影像 API：BitmapMetadata.GetQuery 路徑依檔案格式不同
   - 轉換與輸出：TransformedBitmap、JpegBitmapEncoder（含 Quality 設定）

4. 應用場景：
   - 相片瀏覽器/相簿自動轉正
   - 縮圖批次產生與歸檔流程
   - 影像匯入管線（自動修正方向再儲存）
   - 舊機型或未寫入 180 度方向的補救處理

### 學習路徑建議
1. 入門者路徑：
   - 了解 EXIF 與 Orientation 標記的意義與常見值
   - 練習用 .NET 讀取 JPEG 的 EXIF（GetQuery 路徑與型別）
   - 用 WPF TransformedBitmap 實作基本旋轉與縮放並輸出 JPEG

2. 進階者路徑：
   - 區分 RAW 與 JPEG 的差異，測試不同相機/Codec 的自動旋轉行為
   - 實作健壯的錯誤處理：缺失/異常的 Orientation 值、無 EXIF 的檔案
   - 研究保留或編輯 EXIF 中的 Orientation（像素旋轉 vs 僅改標記）

3. 實戰路徑：
   - 建立批次處理工具：讀檔→判向→變換（Scale+Rotate）→輸出（品質、暫存檔）
   - 增加 180 度偵測缺口的補救策略（人工覆寫、啟發式偵測、UI 快速修正）
   - 加入測試影像組合（四方向樣本、不同機型/格式）自動驗證流程

### 關鍵要點清單
- EXIF Orientation（Tag 274）: 描述影像應如何顯示的方向資訊，是自動轉正的依據 (優先級: 高)
- Orientation 值對應: 常見值 1=不旋轉、6=順時針 90、8=順時針 270、3=180 (優先級: 高)
- JPEG 取值路徑: 使用 /app1/{ushort=0}/{ushort=274} 讀取 Orientation (優先級: 高)
- CR2 取值路徑: 使用 /ifd/{ushort=274} 讀取 Orientation (優先級: 中)
- RAW Codec 自動旋轉: 某些 Canon RAW Codec 解碼時會自動套用旋轉，而 JPEG 不會 (優先級: 高)
- 180 度偵測限制: 文中 Canon 機型不寫入/不識別 180 度，導致無法自動轉正 (優先級: 高)
- 應用端補救: 對 JPEG 必須在程式中依 Orientation 值自行旋轉像素 (優先級: 高)
- WPF 變換管線: 使用 TransformGroup 結合 ScaleTransform 與 RotateTransform 一次完成多重變換 (優先級: 中)
- TransformedBitmap 與編碼: 利用 TransformedBitmap + JpegBitmapEncoder 輸出處理後影像 (優先級: 中)
- 輸出品質與暫存檔: JpegBitmapEncoder.QualityLevel 可控，先存暫存檔再覆寫更安全 (優先級: 低)
- 例外與缺值處理: 缺少 Orientation 或值異常時的 fallback 策略（例如視為不旋轉或提供 UI 修正）(優先級: 高)
- 測試策略: 以四種拍攝角度樣張驗證讀值與旋轉邏輯是否一致 (優先級: 中)
- EXIF vs 像素旋轉: 僅改 EXIF 標記與實際旋轉像素的差異與相容性取捨 (優先級: 中)
- 裝置差異: 不同相機/手機對 Orientation 的寫入行為可能不同，需實測 (優先級: 中)
- 效能與批次處理: 大量縮圖/旋轉時關注記憶體與 I/O，適當串流與釋放資源 (優先級: 低)