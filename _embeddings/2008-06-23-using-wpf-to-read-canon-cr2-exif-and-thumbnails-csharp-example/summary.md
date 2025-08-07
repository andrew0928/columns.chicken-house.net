# 利用 WPF 讀取 CANON (.CR2) 的 EXIF 及縮圖 (C# 範例程式說明)

## 摘要提示
- WPF 與 RAW：WPF 可透過內建影像 API 搭配第三方 Canon Raw Codec 直接處理 .CR2 檔案。
- Metadata 讀取：使用 `BitmapDecoder` 取得 `BitmapMetadata` 後即可透過 `GetQuery()` 擷取 EXIF/METADATA。
- 流程關鍵：讀取 Metadata 時 Stream 務必保持開啟，否則 `GetQuery()` 失效。
- Query 語法：以 Metadata Query Language 透過 `/ifd/{ushort=...}` 對應 TIFF/EXIF Tag，避免繁瑣的常數定義。
- 批次 Tag 清單：作者列出一組常用 CR2 Query 陣列，方便一次擷取多種屬性。
- 縮圖原理：藉由 `TransformedBitmap` + `ScaleTransform` 可在解碼時直接將大圖縮成指定倍率。
- 效能觀察：原尺寸解碼需 60~80 秒，1/10 縮圖僅約 1.5 秒，顯示 Codec 對縮圖流程有最佳化。
- JPEG 參數：`JpegBitmapEncoder.QualityLevel` 可調整 75~90% 之間，兼顧檔案大小與畫質。
- Web 應用：縮圖仍耗時，實務上需搭配快取與背景製圖避免佔用伺服器執行緒。
- 範例資源：完整 C# 範例及測試 RAW 影像可至作者提供的連結下載。

## 全文重點
本文說明如何在 .NET WPF 環境下，以 C# 程式碼讀取 Canon RAW 檔（副檔名 .CR2）的 EXIF/METADATA，並快速產生 JPEG 縮圖。作者指出官方文件雖有範例，但對於第三方 Codec（例如 Canon Raw Codec）的支援細節並不完善，導致開發人員常卡在「抓不到資料與縮圖」的問題。文章分成兩大主題：

1. 讀取 Metadata  
   透過 `FileStream` 讀入 RAW，呼叫 `BitmapDecoder.Create()` 產生 `BitmapMetadata` 物件後，便能使用 `GetQuery()` 依 Metadata Query Language 提取任意欄位。關鍵在於讀取過程中不能提早關掉 Stream；若 Stream 關閉，後續所有 `GetQuery()` 皆失敗。作者並分享一組對 CR2 有效的 Query 陣列（約 40 條 `/ifd/{ushort=...}`），適合需要完整複製 EXIF 的場景。

2. 建立縮圖  
   WPF 解析 RAW 原圖轉 JPEG 效能不佳（約 60 秒），但若改以 `TransformedBitmap` 搭配 `ScaleTransform` 在解碼端就將影像縮放，可把同張 4000×3000 RAW 縮成 400×300 JPEG，時間降到 1.5 秒。示範程式僅十餘行：先建 `BitmapDecoder` 取得 Frame，再用 `ScaleTransform(0.1,0.1)` 創建縮圖 Frame，最後以 `JpegBitmapEncoder` 設定 90% 品質輸出。若不縮圖，僅需將原 Frame 直接加入 Encoder，但耗時回到 60 多秒。作者建議 Web 端需配合快取或離線處理，否則高並發時效能不足。

文末附上完整範例下載鏈結並向讀者致意，期望解決開發者在 WPF 操作 RAW 檔時常見的疑難雜症。

## 段落重點
### 前言
作者因應讀者提問，整理先前開發 MediaFiler 時累積的經驗，將 WPF 處理 RAW 檔的「Metadata 擷取」與「縮圖生成」兩大技巧彙整成簡易範例。背景指出：雖然 Vista 內建 Codec 能讀 RAW，但官方說明不足，連第三方 Canon Raw Codec 也常遇到資訊讀不到、效能不彰等問題，因此才撰文留存。

### 1. 讀取 Metadata
WPF 將 EXIF 等資訊統稱 Metadata，並以 Metadata Query Language 取代傳統 Tag 常數。實作流程：  
1. 透過 `FileStream` 開檔。  
2. 呼叫 `BitmapDecoder.Create()` 解析影像。  
3. 取出 `BitmapMetadata`，以 `GetQuery()` 依 Query 字串抓值。  
重點：Stream 不可提早 Close。作者分享大約 40 條 CR2 常用 Query，對批次轉檔並保留全部 EXIF 極為便利；至於各 Tag 意義則留給開發者視需求自行解譯。

### 2. 建立縮圖
原圖解碼→JPEG 在 WPF 上需 60~80 秒，原因在於 RAW 轉檔資料量龐大。若目的僅縮圖，可在解碼階段加入 `ScaleTransform`，例如倍率 0.1 即產生 1/10 大小 Frame，再以 `JpegBitmapEncoder` 輸出；此法 Canon G9 RAW 檔可於 1.5 秒完成。`QualityLevel` 建議 75~90；小圖 75 已足夠。若直接輸出原尺寸，只需將 Frame 加入 Encoder 無需 Transform，但時間回升。對 Web 應用應結合快取或背景批次產生，以免多用戶同時請求造成瓶頸。

### 後記與資源
作者向詢問的賞鳥攝影師致意，並提供完整 C# 範例與測試 .CR2 檔下載連結；另以幽默附註「家裡大人不准買 PS3」。文章旨在協助開發者快速掌握 WPF 處理 RAW 影像的實務技巧與效能考量。