# 利用 WPF 讀取 CANON (.CR2) 的 EXIF 及縮圖 (C# 範例程式說明)

## 摘要提示
- WPF 與RAW處理: 使用 WPF 可讀取 Canon CR2 檔案的 Metadata 與產生縮圖，但需留意 CODEC 相容與效能差異。
- Metadata/EXIF 概念: WPF 以 Metadata 概念與 Metadata Query Language 取代傳統 EXIF 屬性名的雜亂。
- 讀取Metadata重點: 使用 BitmapDecoder 建立 Frames 後取得 BitmapMetadata，且檔案串流不可過早關閉。
- Query字串陣列: 以 ifd 與 ushort 標記定址 EXIF 標籤，列出 CR2 常用的查詢路徑以便批次抓取。
- CODEC差異問題: 微軟內建 CODEC 正常，但第三方 CODEC（如 Canon Raw Codec）在 WPF 範例上常踩雷。
- 縮圖流程: 以 TransformedBitmap 搭配 ScaleTransform 與 JpegBitmapEncoder 生成縮圖。
- 影像品質參數: JPEG QualityLevel 建議 75~90，縮圖通常 75 已足夠，檔案小且視覺差異不大。
- 效能觀察: 原尺寸轉檔約 60~65 秒，Canon DPP 約 20 多秒；縮圖 1/10 尺寸約 1.5 秒，差異顯著。
- ASP.NET應用建議: 伺服器端即時縮圖仍偏慢，需善用快取機制以承載多用戶併發。
- 範例與資源: 文末提供範例下載與示意 CR2 放置方式，方便直接測試。

## 全文重點
本文針對在 WPF 環境下處理 Canon CR2 RAW 檔案的兩大需求：讀取 Metadata（包括 EXIF）與快速產生縮圖，補充官方文件與一般範例未清楚說明的細節。作者先說明 WPF 對 EXIF 的抽象：以 Metadata 與 Metadata Query Language 統一讀取，避免傳統 EXIF 屬性名混亂；實作上以 BitmapDecoder 取得第一張 Frame 的 BitmapMetadata，再用 metadata.GetQuery(query) 擷取所需資料。關鍵陷阱是檔案串流不可過早關閉，否則 Metadata 讀取會失敗。為了便於通用擷取，作者列出一組對 CR2 可用的 query 字串陣列，涵蓋常見 EXIF/IFD 標籤（像 256、271、34665 下的子標籤等），雖未逐一解釋含意，但可直接實務套用。

在產生縮圖部分，作者指出 WPF 架構雖良好，但透過 Canon Raw Codec 處理原尺寸轉檔效能不佳：CR2 轉 JPG 不縮放時，WPF 需約 60 秒，而 Canon 自家 DPP 約 20 多秒。幸而 CODEC 對縮圖做過最佳化，只取用必要資料即可大幅提速。範例以 TransformedBitmap 搭配 ScaleTransform(0.1, 0.1) 建立 1/10 大小縮圖，並用 JpegBitmapEncoder 設定 QualityLevel（建議 75~90）後輸出；以 Canon G9 的 4000x3000 RAW 生成 400x300 JPEG，大約 1.5 秒，與原尺寸 60+ 秒對比顯著。如果不縮圖，則可直接將 source.Frames[0] 加入 encoder，但時間會回到約 65 秒。對於 ASP.NET 網站場景，縮圖 1.5 秒仍偏長，建議使用快取避免高併發下的效能瓶頸。文末提供完整範例下載與檔案放置說明，並點出此經驗來自實作 MediaFiler 時踩過的坑，特別是第三方 CODEC 在 WPF 的相容與效能細節。

## 段落重點
### 1. 讀取 Metadata
作者先釐清概念：EXIF 規格分歧，WPF 以統一的 Metadata 與 Query Language 來解讀影像資訊，避免事先定義大量屬性名。實作流程：以 FileStream 開檔，BitmapDecoder.Create 建立解碼器後，取得第一張 Frame 的 Metadata（轉為 BitmapMetadata），接著對預先準備的 queries 陣列逐一呼叫 GetQuery 取值。關鍵注意事項是 STREAM 不可過早關閉，否則後續讀取會失效。作者提供一組針對 CR2 的 Metadata Query 清單，使用 ifd 與 {ushort=...} 的路徑語法，涵蓋常見的基本標籤與 EXIF 子 IFD（例如 34665 下的快門、光圈、ISO、曝光補償、焦距、製造商特定資料等），可用於批量擷取與轉檔流程中同步複製 Metadata。雖未逐條解釋每一標籤的語意，但此清單能滿足大多數 CR2 讀取需求，解決官方文件不完整、第三方 CODEC 表現不一致造成的實務困擾。

### 2. 建立縮圖
針對效能，作者對比 Canon DPP 與 WPF + Canon Raw Codec：原尺寸 CR2→JPG，DPP 約 20 多秒，WPF 約 60 秒，顯示透過 WPF/外掛 CODEC 的全尺寸解碼開銷大。但 CODEC 對縮圖做過優化，可僅解析必要資料，因此縮圖速度快很多。範例以 TransformedBitmap 施作 ScaleTransform(0.1, 0.1)，再以 JpegBitmapEncoder 設定 QualityLevel（建議 75~90，縮圖用 75 視覺上足夠且檔案更小）輸出，Canon G9 4000x3000 轉 400x300 約 1.5 秒；若不縮放，直接加入原 Frame 輸出則約 65 秒。對網站應用而言，1.5 秒在高併發下仍偏慢，建議採用快取避免即時重算負載；或另行比較替代方案與後端批次預算。整體結論：在 WPF 中正確地使用 CODEC 與轉換流程，能有效讀取 CR2 Metadata 與快速產生縮圖；但全尺寸轉檔仍受限於 CODEC 與框架開銷，應依情境設計快取與預處理策略。文末提供範例下載連結，方便直接測試驗證。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C# 與 .NET（檔案/串流、例外處理）
   - WPF 影像 API（BitmapDecoder/Encoder、BitmapFrame、TransformedBitmap）
   - EXIF/Metadata 基礎（IFD、EXIF IFD、標籤/Tag 與查詢）
   - 影像編解碼器概念（CODEC；安裝與支援 RAW 格式）
2. 核心概念：
   - WPF Metadata 讀取：透過 BitmapDecoder 與 BitmapMetadata.GetQuery 以 Metadata Query Language 查詢 EXIF/IFD 標籤
   - CODEC 依賴：能否讀 CR2 取決於系統已安裝的 Canon Raw Codec（或其他支援 .CR2 的解碼器）
   - 縮圖產生流程：Decoder 讀取 → TransformedBitmap(ScaleTransform) 縮放 → JpegBitmapEncoder 輸出
   - 效能對比與最佳化：原圖轉檔極慢、縮圖由 CODEC 最佳化大幅加速；串流壽命與快取策略是關鍵
   - Metadata Query 列表：以 /ifd/{ushort=...} 與 /ifd/{ushort=34665}/... 等路徑存取 EXIF 標籤
3. 技術依賴：
   - BitmapDecoder 依賴系統已註冊之影像 CODEC（CR2 需 Canon Raw Codec 或等效）
   - BitmapMetadata 依賴 Decoder 解析結果；GetQuery 需正確的 Query Path
   - TransformedBitmap 依賴來源 BitmapSource 與 ScaleTransform
   - JpegBitmapEncoder 依賴 Frames 與 QualityLevel 設定
   - 檔案串流需在整個解碼/編碼過程中維持開啟，避免提早關閉
4. 應用場景：
   - 桌面相片管理/瀏覽工具：讀取 EXIF、顯示快照、產生縮圖
   - 影像轉檔器：CR2 轉 JPG 與 Metadata 複製
   - 伺服器端縮圖服務（需搭配快取，控制併發）
   - 攝影工作流工具：批次擷取 EXIF（光圈、快門、ISO 等）並建檔

### 學習路徑建議
1. 入門者路徑：
   - 安裝並確認系統有支援 CR2 的 CODEC（如 Canon Raw Codec）
   - 用 BitmapDecoder 讀取檔案，取得 Frames[0].Metadata 並以 GetQuery 讀幾個基礎標籤
   - 練習用 JpegBitmapEncoder 將一張圖片另存為 JPG
2. 進階者路徑：
   - 熟悉 Metadata Query Language 路徑格式（/ifd/{ushort=...} 與 EXIF 子 IFD）
   - 建立 Query 清單並驗證各標籤值，加入型別判斷與錯誤處理（null、不可用標籤）
   - 透過 TransformedBitmap + ScaleTransform 產生固定長邊或固定尺寸縮圖（含比例計算）
   - 比較不同 QualityLevel 的檔案大小與視覺品質
3. 實戰路徑：
   - 實作 CR2 → JPG 的縮圖服務/工具：輸入路徑、輸出路徑、品質、目標尺寸
   - 加入快取策略（磁碟快取/記憶體快取、檢查檔案時間戳以避免重算）
   - 批次處理與管線化：IO 與 CPU 解耦、控制併發數避免壓垮 CODEC
   - 遇不到支援的 CODEC 時之降級策略（回報、跳過、或改用外部工具）

### 關鍵要點清單
- WPF BitmapDecoder 與 Frames: 用 Decoder.Create 取得 Frames[0] 作為後續讀取與轉換的來源 (優先級: 高)
- BitmapMetadata 與 GetQuery: 以 Metadata Query Language 讀 EXIF/IFD 標籤，避免硬編碼名稱 (優先級: 高)
- 串流壽命管理: 解碼與讀取 Metadata 時，來源 FileStream 不可過早關閉 (優先級: 高)
- CODEC 依賴性: 能否讀 CR2 取決於系統是否安裝對應 RAW CODEC (優先級: 高)
- Metadata Query 路徑語法: /ifd/{ushort=...} 與 /ifd/{ushort=34665}/... 表示 EXIF 子 IFD 標籤 (優先級: 中)
- 常見 EXIF 標籤: 例如 271(廠牌)、272(機型)、33434(曝光時間)、33437(光圈)、34855(ISO) 等 (優先級: 中)
- 縮圖流程: TransformedBitmap(ScaleTransform) → BitmapFrame.Create → JpegBitmapEncoder.Save (優先級: 高)
- 縮放比例計算: 以目標尺寸/原圖尺寸計算 ScaleTransform 比例，固定長邊需動態計算 (優先級: 中)
- JPEG 品質設定: QualityLevel 75–90 為常用區間；品質與檔案大小折衷 (優先級: 中)
- 效能觀察: 原圖轉檔（CR2→JPG）極慢；縮圖由 CODEC 最佳化顯著加速 (優先級: 高)
- 非縮圖直接轉檔: 可直接將 source.Frames[0] 加入 Encoder，但耗時較長 (優先級: 低)
- 錯誤與相容性處理: 第三方 CODEC 行為差異，需對 null/不支援標籤設計保護 (優先級: 中)
- 批次與伺服器情境: 需加上快取與併發控制，避免多用戶時延遲累積 (優先級: 高)
- Metadata 複製: 轉檔時如需保留 EXIF，需讀取並寫回對應 Encoder 的 Metadata（不同格式支援度不同） (優先級: 中)
- 記憶體與資源釋放: Encoder.Save 後正確關閉輸出串流，避免檔案鎖定與資源洩漏 (優先級: 中)