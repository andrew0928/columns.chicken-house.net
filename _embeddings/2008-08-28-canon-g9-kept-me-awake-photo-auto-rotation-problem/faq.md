# Canon G9 害我沒睡好... 相片自動轉正的問題

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼同樣直拿相機拍的照片，有些會自動旋轉 90° 顯示正確，有些卻不會？
造成差異的主因有二：
1. Canon 相機只會在偵測到「左轉 90°」或「右轉 90°」時，才把結果寫進 EXIF 的 ORIENTATION 欄位（值 6 或 8）。若相機被倒轉 180° 拍攝，就不會留下可判斷的標記，因此任何軟體都無法自動把它轉回。
2. Canon RAW (.CR2) 檔案在經過 Canon RAW Codec 解碼時，Codec 會依 ORIENTATION 值自動替你旋轉；而直接拍出的 JPEG 檔則沒有這層貼心處理，必須在程式裡自己讀取 ORIENTATION 後手動做 RotateTransform。

## Q: Canon G9 / IXUS55 拍照時在 EXIF 的 ORIENTATION 欄位到底會寫哪些值？
實測四種拍攝方向得到的值依序為：
‧ 0x01 – 正常方向  
‧ 0x08 – 需旋轉 270°  
‧ 0x01 –（再次）正常方向  
‧ 0x06 – 需旋轉 90°  
理論上 180° 應該要寫 0x03，但實際上 Canon 並未寫入，導致 180° 的照片無法被自動轉正。

## Q: Canon 相機能偵測 180° 反轉拍攝嗎？
不行。G9、IXUS55 只偵測得到 90° 左右轉，對 180° 倒轉完全無反應，所以倒著拍的照片在任何軟體裡都只會維持倒立狀態。

## Q: 什麼情境下使用者會把相機倒轉 180° 拍照？
1. 右手拿相機自拍時，按不到快門，只好把相機倒過來用大拇指按。  
2. 小孩隨手亂拍。  
3. 其它特殊需求或創意拍攝。

## Q: 如果想在 .NET/WPF 中讓 JPEG 自動依 EXIF 方向縮圖，該怎麼做？
可利用 BitmapMetadata 讀取 ORIENTATION，轉成 Rotation 列舉後，再用 TransformGroup 同時套用 ScaleTransform 與 RotateTransform。範例程式碼：

```csharp
BitmapMetadata metadata = (BitmapMetadata)sourceFrame.Metadata;
Rotation rotate = Rotation.Rotate0;
ushort value = (ushort)metadata.GetQuery("/app1/{ushort=0}/{ushort=274}");
switch (value)
{
    case 6: rotate = Rotation.Rotate90;  break;
    case 8: rotate = Rotation.Rotate270; break;
    case 3: rotate = Rotation.Rotate180; break;
}

TransformGroup tfs = new TransformGroup();
tfs.Children.Add(new ScaleTransform(0.1, 0.1));  // 縮圖
tfs.Children.Add(new RotateTransform((int)rotate));

JpegBitmapEncoder encoder = new JpegBitmapEncoder();
encoder.Frames.Add(BitmapFrame.Create(new TransformedBitmap(sourceFrame, tfs)));
encoder.QualityLevel = 90;
using (var fs = File.Create(trgFile)) encoder.Save(fs);
```

上述程式即可在縮圖的同時，自動完成正確的旋轉。