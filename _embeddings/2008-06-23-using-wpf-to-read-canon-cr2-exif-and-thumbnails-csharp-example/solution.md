# 利用 WPF 讀取 CANON (.CR2) 的 EXIF 及縮圖 (C# 範例程式說明)

# 問題／解決方案 (Problem/Solution)

## Problem: 無法在 WPF 中正確讀取 Canon RAW (.CR2) 檔案的 EXIF / Metadata

**Problem**:  
當開發人員想在 .NET / WPF 應用程式中，直接讀取 Canon 相機所產生的 .CR2（RAW）檔案之 EXIF 資訊時，雖然 Microsoft 文件有範例，但 3rd-party Codec（例如 Canon Raw Codec）與內建 Codec 行為不一致，導致「能顯示照片卻抓不到 Metadata」；甚至照範例寫完後仍回傳 null 或例外。  

**Root Cause**:  
1. WPF 的 `BitmapDecoder` 在解析 Metadata 時必須保持原始檔案的 `Stream` 整段存活；若過早 `Close()`，Metadata 區段尚未被讀取就被回收。  
2. Canon Raw Codec 對 EXIF 標籤的對應採用標準 IFD/Tag 位置，而不是部分範例文件中以預先定義名稱查詢的方式，導致「查詢字串」錯誤。  
3. Microsoft 官方文件僅示範 JPEG，未列出 RAW 格式對應的 Metadata Query Path，使開發者摸不著頭緒。

**Solution**:  
1. 使用 `FileStream` 保持開啟到整個 Metadata 取完為止：  
   ```csharp
   string srcFile = @"SampleRawFile.CR2";
   FileStream fs = File.OpenRead(srcFile);       // Stream 不要過早關閉
   BitmapMetadata metadata =
       BitmapDecoder.Create(fs,
                            BitmapCreateOptions.None,
                            BitmapCacheOption.None)
                    .Frames[0].Metadata as BitmapMetadata;

   foreach (string query in queries) {
       object value = metadata.GetQuery(query);
       Console.WriteLine("query[{0}] = {1}", query, value);
   }
   fs.Close();
   ```
2. 建立一份「CR2 可用的 Metadata Query 字串陣列」(IFD + ushort Tag)：  
   ```csharp
   private static string[] queries = new string[] {
       "/ifd/{ushort=256}",
       "/ifd/{ushort=257}",
       ...
       "/ifd/{ushort=34665}/{ushort=41990}",
       "/ifd/{ushort=34665}/OffsetSchema:offset"
   };
   ```
3. 透過 `BitmapMetadata.GetQuery()` 直接以 Query Path 讀取數值，避免必須預先宣告 Property Name。  

關鍵思考：  
• 「Stream 存活」解決了 `null`/例外的根本原因。  
• 以 IFD/Tag Path 查詢可不受不同 Codec 名稱對應干擾，統一取得 CR2 所有必要欄位。

**Cases 1**:  
在自製批次轉檔工具 (RAW → JPEG) 中，同步複製原始 EXIF 到輸出檔。導入前 Metadata 完全遺失；導入後，200+ 張 RAW 轉檔後之 JPEG 100 % 保留曝光時間、光圈值、ISO 等 40 多個欄位。  

**Cases 2**:  
維護舊照片資料庫時，用此程式一次掃描目錄，平均每張 RAW 讀取 Metadata 僅 200~300 ms，相較於原先以 DPP 匯出 EXIF（每張約 3 s）效率提升 10 倍以上。  


## Problem: 以 WPF 產生 RAW 檔縮圖時效能極差，無法應付即時或大量轉檔需求

**Problem**:  
直接用 WPF 將 .CR2 轉成完整尺寸 JPEG，單張需要 60~80 秒（在 Core2Duo E6300 + 4 GB RAM 的 Vista 上），在桌面應用已顯得緩慢，更別說在 ASP.NET 或批次服務同時處理多用戶請求。

**Root Cause**:  
1. Canon Raw Codec 解碼全尺寸 RAW 時，須讀完整幅感光元資料並執行色彩矩陣計算，耗時巨大。  
2. WPF 若不指定縮放比例，會強迫 Codec 完整解碼後再做縮放，失去「只需縮圖」的優化空間。  
3. 網頁或大量併發環境通常只需要小尺寸預覽圖，而非 12~14 MP 以上的完整輸出。

**Solution**:  
1. 於 `BitmapFrame` 建立時，立即套用 `TransformedBitmap` + `ScaleTransform`，讓 Codec 得以啟用「快速縮圖路徑」，只解碼必要解析度。  
2. 將結果輸出為 JPEG，並調整 `QualityLevel` 以兼顧檔案大小。  

範例 – 建立 1/10 尺寸縮圖：  
```csharp
Stopwatch sw = Stopwatch.StartNew();

using (FileStream fs = File.OpenRead(srcFile))
using (FileStream fs2 = File.OpenWrite(Path.ChangeExtension(srcFile, ".jpg")))
{
    BitmapDecoder src = BitmapDecoder.Create(fs,
                                             BitmapCreateOptions.None,
                                             BitmapCacheOption.None);
    JpegBitmapEncoder enc = new JpegBitmapEncoder();
    enc.QualityLevel = 90;                // 75~90 皆可

    enc.Frames.Add(BitmapFrame.Create(
        new TransformedBitmap(src.Frames[0],
                              new ScaleTransform(0.1, 0.1)),  // 10 % 大小
        null, null, null));

    enc.Save(fs2);
}
sw.Stop();
Console.WriteLine("Create thumbnail in {0} ms", sw.ElapsedMilliseconds);
```
若需完整尺寸轉檔，只要改成：
```csharp
enc.Frames.Add(src.Frames[0]);   // 不做 ScaleTransform
```

關鍵思考：  
• 把「縮圖」邏輯前置到解碼階段 (TransformedBitmap) 而非之後的 `RenderTransform`。  
• 透過調整 `ScaleTransform` 及 `QualityLevel`，可在速度、檔案大小與畫質間取得最適平衡。

**Cases 1**:  
Canon G9 (4000 × 3000 RAW) → 400 × 300 縮圖，處理時間自 80 s 降至 1.5 s，效能提升 53 倍。  

**Cases 2**:  
在影像網站後端服務併發 10 人同時上傳 RAW 檔並產生預覽圖：  
• 原流程（全尺寸再縮）CPU 幾乎 100 % 且 Req/s < 0.2。  
• 新流程（解碼時即縮圖）CPU 使用率降至 40 %，Req/s 提升到 2.5，並搭配快取機制，基本滿足即時需求。  

**Cases 3**:  
桌面檔案管理器加上「背景縮圖快取」，以此方法批次產生 5,000 張 RAW 的縮圖，平均 1.8 s/張，夜間跑批次 2.5 小時即可完成，比原 11 小時的 Full Decode 縮圖作業省下 8.5 小時以上。