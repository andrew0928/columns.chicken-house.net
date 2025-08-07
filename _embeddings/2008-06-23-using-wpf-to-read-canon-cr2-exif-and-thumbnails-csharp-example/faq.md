# 利用 WPF 讀取 CANON (.CR2) 的 EXIF 及縮圖（C# 範例程式說明）

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 WPF 中要如何讀取 Canon CR2 檔案的 Metadata / EXIF？
使用 `BitmapDecoder.Create()` 先取得第一張 Frame，再轉成 `BitmapMetadata` 後以 `GetQuery()` 讀取所需欄位。範例重點如下：  
```csharp
FileStream fs = File.OpenRead(@"SampleRawFile.CR2");
BitmapMetadata metadata = BitmapDecoder.Create(
        fs,
        BitmapCreateOptions.None,
        BitmapCacheOption.None)
    .Frames[0].Metadata as BitmapMetadata;

object result = metadata.GetQuery("/ifd/{ushort=272}"); // 例如機型
fs.Close();
```  
注意：串流 (`FileStream`) 不能在讀取完 Frame 之前關閉，否則 Metadata 會全部讀不到。

## Q: 讀取 Metadata 時常見的「全部都是 null」問題通常是什麼原因？
最常見的原因是檔案串流過早被關閉。只要在 `BitmapDecoder` 與 `BitmapMetadata.GetQuery()` 皆完成前保持 `FileStream` 開啟，就能正常取得資料。

## Q: 需要查詢哪些 Metadata 欄位？有沒有現成的 Query 字串陣列？
文章列出了作者實務上用於 CR2 檔的 Query 陣列，例如  
```
"/ifd/{ushort=256}",
"/ifd/{ushort=272}",
"/ifd/{ushort=34665}/{ushort=33434}",
⋯
```  
把這些字串放進 `string[] queries`，即可迴圈呼叫 `metadata.GetQuery()` 取得大部分 CR2 支援的 EXIF 欄位。

## Q: 如何用 WPF 把 CR2 原檔快速轉出 1/10 大小的 JPEG 縮圖？
重點做法是把原 Frame 包進 `TransformedBitmap` 並指定 `ScaleTransform(0.1,0.1)`，再交給 `JpegBitmapEncoder`：  
```csharp
BitmapDecoder src = BitmapDecoder.Create(fs, BitmapCreateOptions.None, BitmapCacheOption.None);
JpegBitmapEncoder enc = new JpegBitmapEncoder();
enc.Frames.Add(BitmapFrame.Create(
        new TransformedBitmap(src.Frames[0], new ScaleTransform(0.1, 0.1)),
        null, null, null));
enc.QualityLevel = 90;   // JPEG 壓縮品質
enc.Save(fs2);
```  
在 Core2Duo E6300 + 4 GB RAM 的測試機上，4000×3000 的 RAW 轉 400×300 JPEG 約 1.5 秒即可完成。

## Q: 不做縮放、直接把 CR2 轉成同尺寸 JPEG 時速度如何？
若把程式改成  
```csharp
enc.Frames.Add(src.Frames[0]);   // 不做 ScaleTransform
```  
則完整解析度的轉檔約需 60–65 秒，遠比 1.5 秒的縮圖慢許多。

## Q: Canon 自家 DPP 與 WPF + Canon Raw Codec 的轉檔效能差多少？
在同一台機器上，Canon DPP 直接輸出 JPEG 約 20 多秒；改用 WPF 搭配 Canon Raw Codec 轉檔則約 60 秒，顯示 WPF Pipeline 的額外負擔不容忽視。

## Q: 如果要在 ASP.NET 網站上動態產生縮圖，1.5 秒仍嫌太慢怎麼辦？
建議將縮圖結果快取 (Cache) 起來，避免每次請求都重新解碼 CR2。若流量更大，可考慮預先批次產生縮圖或使用專門的影像服務。