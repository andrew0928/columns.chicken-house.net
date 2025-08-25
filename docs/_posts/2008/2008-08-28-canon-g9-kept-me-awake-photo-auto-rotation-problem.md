---
layout: post
title: "Canon G9 害我沒睡好... 相片自動轉正的問題"
categories:

tags: [".NET","Tips","WPF","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/08/28/canon-g9-害我沒睡好-相片自動轉正的問題/
  - /columns/post/2008/08/28/Canon-G9-e5aeb3e68891e6b292e79da1e5a5bd.aspx/
  - /post/2008/08/28/Canon-G9-e5aeb3e68891e6b292e79da1e5a5bd.aspx/
  - /post/Canon-G9-e5aeb3e68891e6b292e79da1e5a5bd.aspx/
  - /columns/2008/08/28/Canon-G9-e5aeb3e68891e6b292e79da1e5a5bd.aspx/
  - /columns/Canon-G9-e5aeb3e68891e6b292e79da1e5a5bd.aspx/
wordpress_postid: 75
---

抱怨一下，因為在看照片時發現，有些直的拍的照片看起來是正確的 (會自己轉 90 度)，有些卻不是... 得歪著頭看，所以就很好奇到底是怎麼回事...。

![Correct orientation photos](/images/2008-08-28-canon-g9-kept-me-awake-photo-auto-rotation-problem/image_12.png)

這幾張是正確的 (右上 & 左下，會自動轉 90 度)

![Incorrect orientation photos](/images/2008-08-28-canon-g9-kept-me-awake-photo-auto-rotation-problem/image_11.png)

這幾張是錯的 (應該自動轉 90 度才對)

![Wrong rotation](/images/2008-08-28-canon-g9-kept-me-awake-photo-auto-rotation-problem/image_10.png)

第二張是錯的 (應該要轉 180 度才對)

越想越不對，我記得除了我那台古董 CANON G2 之外，後來 CANON 的相機都有加上偵測轉向的機制啊? 不外乎是[水銀開關](http://zh.wikipedia.org/w/index.php?title=%E6%B0%B4%E9%8A%80%E9%96%8B%E9%97%9C&variant=zh-tw)或是類似的東西，總之相機能夠得知目前是不是轉直的拍，同時能把這資訊寫到 EXIF 內的 ORIENTATION 欄位去...

但是為什麼拍出來的相片有的可以自動轉，有的不行? 花了點時間歸納一下，發現 G9 拍出來的 "有機會" 是正常的，而家裡大人的 IXUS55 則都不會自動轉，真是怪了... 在相機上看都會自動轉正啊...

因為我的照片都是自己用 WPF 寫程式縮圖處理的，我開始懷疑是不是我的歸檔程式的問題。G9 拍的 .CR2 檔，透過 RAW CODEC 轉成 JPEG 會自動轉正，G9 / IXUS55 拍的 JPG 檔則不會...

![EXIF orientation values](/images/2008-08-28-canon-g9-kept-me-awake-photo-auto-rotation-problem/image_9.png)

嗯，開始無聊了，拿起相機拍了四種角度，然後用 DEBUGGER 去看 EXIF 的 ORIENTATION 值為啥... .CR2 要用 "/ifd/{ushort=274}" 來查，會得到一個 UInt16 的值，如果是 .JPG 則要改成 "/app1/{ushort=0}/{ushort=274}" ...

得到的值還真怪。.CR2 / .JPG 都一樣。依照上圖的順序，得到的值分別是 0x01, 0x08, 0x01, 0x06。查了查文件，除了轉 180 度那個的值不大對之外，另外三個都正常。不過 Canon Codec 在 decode 時會自動幫我做 RotateTransform，我得在處理 .JPG 時自己補上這個動作。除了轉 180" 之外其它都正常了。

就是那張 180 度的不正確，害我氣的牙癢癢的... 決定跟它拼了... 改了改程式，把所有 EXIF 都印出來，用肉眼一個一個比... 本來想說是不是有別的 FLAG 可以判定出來正反? 結果看到眼睛脫窗了也沒找到，我連 EXIF 裡的 BLOB (Binary data) 都一個一個印出來看 @_@，GOOGLE 也找不到啥有用的資訊...

最後氣到，拿起相機重拍一次，這次直接在相機上看，按下 DISPLAY 看看有無其它資訊... COW，終於發現... 相機自己也認不出轉 180 度的狀況? 嘖嘖... 搞了半天 CANON 只有偵測左轉及右轉 90 度的情況，轉 180 度就不理它了.. 哈哈!

不過有誰會轉 180 度拍照? 當然有...

1. 用右手拿相機自拍，按不到快門... 只好轉 180 度，用底下的姆指來按
2. 小孩拿著自己亂拍
3. 想不出來了...

總算水落石出，犧牲了幾個小時的睡覺時間，咳咳... 不過既然本版都是討論 .NET 程式設計的，最後就貼點 CODE 充個數... 也算沒偏離主題了 :D 不過我想應該沒人像我一樣無聊在搞這些吧?

**取得 ORIENTATION 的值，並且判定要往那個方向旋轉**

```csharp
BitmapMetadata metadata = null;
Rotation rotate = Rotation.Rotate0;
// ...  
ushort value = (ushort)metadata.GetQuery("/app1/{ushort=0}/{ushort=274}");
if (value == 6)
{
    rotate = Rotation.Rotate90;
}
else if (value == 8)
{
    rotate = Rotation.Rotate270;
}
else if (value == 3)
{
    rotate = Rotation.Rotate180;
}
```

**利用 TransformGroup, 一次套用 ScaleTransform (縮放) + RotateTransform (旋轉) 兩種轉換特效**

```csharp
JpegBitmapEncoder target = new JpegBitmapEncoder();
TransformGroup tfs = new TransformGroup();
tfs.Children.Add(new ScaleTransform(0.1, 0.1));
switch (rotate)
{
    case Rotation.Rotate90:
        tfs.Children.Add(new RotateTransform(90));
        break;
    case Rotation.Rotate180:
        tfs.Children.Add(new RotateTransform(180));
        break;
    case Rotation.Rotate270:
        tfs.Children.Add(new RotateTransform(270));
        break;
}
target.Frames.Add(BitmapFrame.Create(
        new TransformedBitmap(sourceFrame, tfs),
        null,
        null,
        null));
target.QualityLevel = quality;
//
// save to temp file
//
string temp = Path.Combine(Path.GetDirectoryName(trgFile), string.Format("{0:N}.tmp", Guid.NewGuid()));
FileStream trgs = File.OpenWrite(temp);
target.Save(trgs);
trgs.Close();
```
