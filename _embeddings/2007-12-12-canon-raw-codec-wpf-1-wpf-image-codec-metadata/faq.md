# Canon Raw Codec + WPF #1, WPF Image Codec, Metadata

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者買了 Canon G9 之後，空閒時間都在研究 WPF 的 Image Codec？
作者原本就計畫撰寫一套自動化的相片歸檔程式流程，而 Canon 官方同時提供了支援 RAW 的 Windows Image Codec；WPF 又能直接利用該 Codec 進行影像處理。因此，買下支援 RAW 的 G9 正好補齊整個計畫最後一塊拼圖，作者才投入時間研究 WPF 的 Image Codec。

## Q: 作者認為相機必須支援 RAW 的主要理由是什麼？
因為 JPEG 已是舊規格，未來勢必出現取代者；若保留原始的 RAW 檔，只要相機品牌仍在，就能在未來轉成任何新通用格式，而且不必經過 JPEG 而造成額外資訊折損。

## Q: 與傳統 GDI/GDI+ 相比，WPF 在影像處理思維上有何差異？
GDI/GDI+ 典型應用偏向「小畫家」這類逐像素的靜態處理；WPF 則類似 Flash 或 Photoshop layer 的概念，把影像視為可套用多層 Transform 的物件，最後疊合後才呈現結果。

## Q: 如何在 WPF 中把 Canon RAW（.CR2）縮圖並轉成 JPEG？
可利用 BitmapDecoder 讀取 RAW，再用 JpegBitmapEncoder 輸出。例如：
```csharp
BitmapDecoder source = BitmapDecoder.Create(
    new Uri(@"C:\IMG_0001.CR2"),
    BitmapCreateOptions.DelayCreation,
    BitmapCacheOption.None);

JpegBitmapEncoder target = new JpegBitmapEncoder();
target.Frames.Add(BitmapFrame.Create(
    new TransformedBitmap(source.Frames[0], new ScaleTransform(0.3, 0.3)),
    source.Frames[0].Thumbnail,
    metadata,
    null));
target.QualityLevel = 80;
using (FileStream fs = File.OpenWrite(@"C:\IMG_0001.JPG"))
{
    target.Save(fs);
}
```
亦可呼叫封裝好的函式：
```csharp
ImageUtil.SaveToJPEG(
    @"c:\IMG_0001.CR2",
    @"c:\IMG_0001.JPG",
    800, 800, 75);
```

## Q: WPF 如何統一讀寫各種影像格式的 Metadata？
WPF 的 Image Codec 以「Metadata Query」字串（類似 XPath）抽象化所有格式的 metadata 存取。程式可用 `GetQuery()` 讀取或 `SetQuery()` 寫入，而不需關心底層是 EXIF、IFD、XMP 等哪一種規格。

## Q: Canon RAW 的 Metadata 為何無法直接對應到 JPEG EXIF？作者怎麼解決？
Canon RAW 與 JPEG EXIF 的 Query Path 不同，例如  
`/ifd/{ushort=256}` 需對應到 `/app1/ifd/exif/{ushort=256}`。  
作者以程式比對多張轉檔結果，整理出一份可用的對照表，存成 XML 嵌入於 Library，轉檔時先查表再寫入對應欄位，從而保留 EXIF 資訊。

## Q: 除了影像與 Metadata 轉檔，作者下一個待解決的最大問題是什麼？
效能（Performance）。在完成「正確轉檔並保留 EXIF」的基本功能後，作者發現處理速度仍不足，決定留待下一篇文章深入探討。