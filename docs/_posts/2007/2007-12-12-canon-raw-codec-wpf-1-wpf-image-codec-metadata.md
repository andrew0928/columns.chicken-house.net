---
layout: post
title: "Canon Raw Codec + WPF #1, WPF Image Codec, Metadata"
categories:
- "系列文章: Canon Raw Codec & WPF"
tags: [".NET","WPF","作品集","多執行緒","技術隨筆","當年勇"]
published: true
comments: true
redirect_from:
  - /2007/12/11/canon-raw-codec-wpf-1-wpf-image-codec-metadata/
  - /columns/post/2007/12/12/Canon-Raw-Codec-2b-WPF-12c-WPF-Image-Codec2c-Metadata.aspx/
  - /post/2007/12/12/Canon-Raw-Codec-2b-WPF-12c-WPF-Image-Codec2c-Metadata.aspx/
  - /post/Canon-Raw-Codec-2b-WPF-12c-WPF-Image-Codec2c-Metadata.aspx/
  - /columns/2007/12/12/Canon-Raw-Codec-2b-WPF-12c-WPF-Image-Codec2c-Metadata.aspx/
  - /columns/Canon-Raw-Codec-2b-WPF-12c-WPF-Image-Codec2c-Metadata.aspx/
  - /blogs/chicken/archive/2007/12/12/2873.aspx/
wordpress_postid: 133
---

託 Canon G9 的福, 這一個月來的空閒時間都在研究 Windows Presentation Foundation 裡的 Image Codec 相關事項. 幹嘛買個相機還這麼辛苦? 因為原本算計好的計劃, 就差這一環啊... 雖然老早就有換機的計劃, 為什麼龜了那麼久 G9 一出來就跑去買? 除了之前講了一堆相機本身的考量之外, 剩下的關鍵因素是 RAW support. 因為:

1. Canon G9 "又" 開始支援 RAW file
2. Canon 正好搭配 WPF (windows presentation foundation), 發表了它專屬的 RAW file codec.
3. WPF 裡提供了許多 JPEG 無法帶來的好處, 我打的如易算盤是: 不管未來是什麼東西取代了 JPEG, 留著 RAW 一定沒錯, 因此支援 RAW 就大大加了不少分.

RAW support 在我看來是必要的. 照片可不能等十年後再搭時光機回來照, 而現有的 JPEG 又已經是老古董的規格了, 未來是一定會有取而代之的新規格. 會是什麼我不曉得, 不過留著 RAW 準沒錯. 只要 Canon 沒倒, 未來一定有辦法把 RAW 轉成新的通用格式, 而不用經過 JPEG 的折損...

未來看起來很美好, 不過當 G9 入手後, 事情沒有想像的順利, 有了 WPF + Codec, 我自己必需寫些小程式來簡化未來例行的相片歸檔動作. Codec 只要去 Canon 下載就有, WPF 則是新東西, 得自己先研究一番... 搭配 WPF, Microsoft 也推出了新的圖型檔格式: HD Photo. 它的一堆好處我就不多說了, Microsoft 網站多的是. 我在意的是, HD Photo 提供的新功能, 包括廣大的色域等, 也會對應的在 image codec 裡提供. 因此如果 RAW file 本身就包含這些資訊的話, 透過 codec 讀出來就不會有資訊的折損, 存成 JPEG 就沒有這些好處了.

實作第一步, 當然是先研究 WPF 關於 Image 物件的基本處理. 嗯, 果然是跟之前的 GDI / GDI+ 不一樣. 感覺起來 GDI 典型 application 就是像 "小畫家" 這類的 AP, 而 WPF 典型的 application 就是像 flash 這類的, 裡面的物件已經變成圖型來源, 套用各種 transform, 層層處理套上去後得到的結果才是你看到的東西, 大概就類似 photoshop 的 layer 那樣的東西.

講了那麼多, 其實我也只是要用到 codec 來讀取 canon raw file, 把圖檔縮成我要的像素, 存成指定的 jpeg 檔而以... 我就以這個例子貼一段 sample code

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

FileStream trgs = File.OpenWrite(@"C:\IMG_0001.JPG");
target.Save(trgs);
trgs.Close(); 

```

而過去也寫過 GDI+ 版本的, 那個我就不貼了. 老實說 code 也不會太多, 不過寫起來就覺的是兩種不同層次的思考邏輯. 也隨著這次機會花了點心思研究 System.Windows.Media.Imaging 裡的東西, 就開始想把舊的程式都翻一翻.. 包括了之前的歸檔程式, 及另一個批次縮圖的工具. 後面有機會再貼.

圖檔基本內容處理掉之後, 接下來就是 exif. 我很在意這些圖檔隱藏的資訊, 也不知道為什麼, 哈哈. 上面的 code 轉完是沒有半點 EXIF 的, 沒轉過來感覺就像少了什麼... 無奈在處理 metadata 時又碰到了一些小 trouble ...

花了一些時間搞定了 metadata, 不過又碰到不同檔案格式之間的 metadata 轉換問題. WPF 的 Image Codec 已經把 metadata 的讀寫方式給 "抽像化" 了, 所有圖檔的 metadata 都用一樣的方式讀寫. 它採用的是類似 xpath 的 metadata query 來指明目標是那個 metadata, 然後再用 GetQuery( ) 來讀值, 或是用 SetQuery( ) 把值寫進去. 現在碰到的問題是 Canon Raw 的 query 跟 JPEG exif 用的對應不起來. 我也不知道怎麼解, google 找幾個 sample 對照著比一比, 摸黑試了幾種對應方式, 竟然看起來還好像猜中了, 就不管先用下去. 我簡單的把整理的對照表貼一下...

```

/ifd/{ushort=256} --> /app1/ifd/exif/{ushort=256}
/ifd/{ushort=257} --> /app1/ifd/exif/{ushort=257}

```



請不要問我這是啥意思, 我真的也搞不懂, 看了 w3c 一些 spec, 真是天書... 大概只知道 metadata 有幾種規範, exif, xmp, ifd 等等. 而 ushort=256 大概就是指整個 block 裡, 第 256 bytes 位置的 ushort 的值就是這筆資料存放的地方等等. 我是拿幾張照片轉換後對照著看, 看起來對就將就著用了. 最後是用程式跑了一份看起來可用的對照表, 存成 xml 檔, 丟在自己寫的 library project 裡, 當作 embedded resource. 供未來轉檔的動作時拿出來用. library 包裝好之後用起來像這樣:

```csharp
ImageUtil.SaveToJPEG(
    @"c:\IMG_0001.CR2",
    @"c:\IMG_0001.JPG",
    800,
    800,
    75);
```

弄到現在, 總算把最基本的動作: 轉檔 (含 exif) 給搞定了. 總算有足夠的資訊把 library 給弄好. 不過馬上就碰到第二個大問題... "效能". 這部份就留著下一篇吧.
