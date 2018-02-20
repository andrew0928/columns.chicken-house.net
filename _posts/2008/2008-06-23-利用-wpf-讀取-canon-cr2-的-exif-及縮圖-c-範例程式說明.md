---
layout: post
title: "利用 WPF 讀取 CANON (.CR2) 的 EXIF 及縮圖 (C# 範例程式說明)"
categories:

tags: [".NET","WPF","技術隨筆","有的沒的"]
published: true
comments: true
permalink: "/2008/06/23/利用-wpf-讀取-canon-cr2-的-exif-及縮圖-c-範例程式說明/"
redirect_from:
  - /columns/post/2008/06/23/e588a9e794a8-WPF-e8ae80e58f96-EXIF-e58f8ae7b8aee59c96.aspx/
  - /post/2008/06/23/e588a9e794a8-WPF-e8ae80e58f96-EXIF-e58f8ae7b8aee59c96.aspx/
  - /post/e588a9e794a8-WPF-e8ae80e58f96-EXIF-e58f8ae7b8aee59c96.aspx/
  - /columns/2008/06/23/e588a9e794a8-WPF-e8ae80e58f96-EXIF-e58f8ae7b8aee59c96.aspx/
  - /columns/e588a9e794a8-WPF-e8ae80e58f96-EXIF-e58f8ae7b8aee59c96.aspx/
wordpress_postid: 93
---

因為有人 [留話](/post/Canon-Raw-Codec-for-Vista--XP-x64-.aspx) 在詢問怎麼利用 WPF 處理這些動作，而這些又都是 Microsoft 文件及範例沒有寫的很清楚的部份... 有些範例有提到，但是 Microsoft 內建的 CODEC 正常，3RD PARTY 的 CODEC (像我碰到的 Canon Raw Codec) 就搞半天也搞不出來...。因為之前寫 [MediaFiler](/post/Canon-Digital-Camera-e79bb8e6a99fe78da8e4baab---e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7.aspx) 正好都碰過這些釘子，就順手寫起來以免以後又忘掉.. :P


# 1. 讀取 Metadata

講 METADATA 也許會有些人一頭霧水，講 EXIF 搞不好還比較多人知道... EXIF 的規格有點混亂，就像 RSS 一樣，有好幾個派係，Microsoft 乾脆在 WPF 裡跳出來直接稱它做 METADATA，也搭配了 METADATA QUERY LANGUAGE 來避開像 EXIF 一堆必需事先定義好 PROPERTY NAME 的麻煩事...

所以所有的動作都集中在兩件事上面，一個是怎麼操作 METADATA ? 另一個是我要的資料到底藏在那? (你得知道什麼樣的 QUERY 才抓的到你要的資料?)

先看簡單的，貼段 SAMPLE CODE 就搞定了..

SAMPLE 1. 如何讀取 METADATA ?
```csharp

string srcFile = @"SampleRawFile.CR2";

//
//  sample 1. read metadata
//                FileStream fs = File.OpenRead(srcFile);                
BitmapMetadata metadata = BitmapDecoder.Create(
  fs,
  BitmapCreateOptions.None,
  BitmapCacheOption.None).Frames[0].Metadata as BitmapMetadata;

foreach (string query in queries)
{
  object result = metadata.GetQuery(query);
  Console.WriteLine("query[{0}]: {1}", query, result);
}
fs.Close();

```                




扣掉 COMMENTS 只有12行... 哈哈，看起來好像也沒什麼好講的，關鍵就只有一個，STREAM別太早關掉...。以前我就吃過虧，試了好久才知道原來是我太雞婆，在第10行之前就把 fs 給關了，後面通通讀不出來...

不過關鍵的 queries (型別是 ```string[]``` )，內容到底是啥? 老實說我也不是很清楚 :P 先貼一下建立這字串陣列的 CODE:


建立 CR2 支援的 METADATA QUERY

```csharp
private static string[] queries = new string[] {
  "/ifd/{ushort=256}",
  "/ifd/{ushort=257}",
  "/ifd/{ushort=258}",
  "/ifd/{ushort=259}",
  "/ifd/{ushort=262}",
  "/ifd/{ushort=270}",
  "/ifd/{ushort=271}",
  "/ifd/{ushort=272}",
  "/ifd/{ushort=273}",
  "/ifd/{ushort=274}",
  "/ifd/{ushort=277}",
  "/ifd/{ushort=278}",
  "/ifd/{ushort=279}",
  "/ifd/{ushort=282}",
  "/ifd/{ushort=283}",
  "/ifd/{ushort=284}",
  "/ifd/{ushort=296}",
  "/ifd/{ushort=306}",
  "/ifd/{ushort=315}",
  "/ifd/{ushort=34665}/{ushort=33434}",
  "/ifd/{ushort=34665}/{ushort=33437}",
  "/ifd/{ushort=34665}/{ushort=34855}",
  "/ifd/{ushort=34665}/{ushort=36864}",
  "/ifd/{ushort=34665}/{ushort=36868}",
  "/ifd/{ushort=34665}/{ushort=37377}",
  "/ifd/{ushort=34665}/{ushort=37378}",
  "/ifd/{ushort=34665}/{ushort=37380}",
  "/ifd/{ushort=34665}/{ushort=37386}",
  "/ifd/{ushort=34665}/{ushort=37500}",
  "/ifd/{ushort=34665}/{ushort=37510}",
  "/ifd/{ushort=34665}/{ushort=40960}",
  "/ifd/{ushort=34665}/{ushort=40961}",
  "/ifd/{ushort=34665}/{ushort=41486}",
  "/ifd/{ushort=34665}/{ushort=41487}",
  "/ifd/{ushort=34665}/{ushort=41488}",
  "/ifd/{ushort=34665}/{ushort=41728}",
  "/ifd/{ushort=34665}/{ushort=41985}",
  "/ifd/{ushort=34665}/{ushort=41986}",
  "/ifd/{ushort=34665}/{ushort=41987}",
  "/ifd/{ushort=34665}/{ushort=41988}",
  "/ifd/{ushort=34665}/{ushort=41990}",
  "/ifd/{ushort=34665}/OffsetSchema:offset"
};
```



因為我之前處理的目標，是在做轉檔的動作，同時要忠實的把 METADATA 也複製過去，因此得到這列表對我來說很重要，但是搞懂每個項目的意義是啥我就不管了，先列出來再說... 需要的人請自行判斷....



# 2. 建立縮圖

WPF 架構滿分，但是效能多少會打折扣。JPEG實在看不大出來，拿CANON的CODEC來看就很清楚了。如果是以 .CR2 -&gt; .JPG，不作大小的縮放，CANON 自家的 DPP 大概要廿幾秒，CANON自家寫給 WPF 用的 CODEC 搭配 .NET 的 WPF 程式，則要 60 秒左右，測試的機器就我這台 Vista + 4GB RAM, CPU 是 Core2Duo E6300...

速度實在是不快，也不是用 .NET 寫效能太糟的原因，因為 VISTA 內建的秀圖程式也是靠同一個 CODEC，效能也差不多... 不過 CODEC 的架構設計的很好，如果我要的只是縮圖，那就不一樣了... 來看第二個範例:

SAMPLE 2. 建立原圖 (.CR2) 1/10 大小的 JPEG 縮圖

```csharp
Stopwatch timer = new Stopwatch();

timer.Start();
FileStream fs = File.OpenRead(srcFile);
FileStream fs2 = File.OpenWrite(Path.ChangeExtension(srcFile, ".jpg"));
BitmapDecoder source = BitmapDecoder.Create(fs, BitmapCreateOptions.None, BitmapCacheOption.None);
JpegBitmapEncoder target = new JpegBitmapEncoder();

target.Frames.Add(BitmapFrame.Create(
  new TransformedBitmap(source.Frames[0], new ScaleTransform(0.1, 0.1)), 
  null, 
  null, 
  null));

target.QualityLevel = 90;
target.Save(fs2);
fs.Close();
fs2.Close();
timer.Stop();

Console.WriteLine("Create 0.1x thumbnail: {0} ms.", timer.ElapsedMilliseconds);
```



範例程式也很簡單，扣掉計時的程式碼只有 16 行... 裡面兩個關鍵的參數，分別為第 11 行， 0.1 代表 Scale Transform 用的縮放比例，0.1 就是只要 1/10 的大小。如果你想要固定尺寸的縮圖，得先自行計算出這個 SCALE 的值。要單純的轉檔，就填 1.0 就好。

另一個參數是第15行的 90，它是指存成 JPEG 時要使用的 QUALITY，100 最好，越低失真越嚴重，但是相對的檔案大小也會大幅下降。一般用的 QUALITY 大約都在 75% ~ 90%，其實縮圖 75% 就夠了，反正看不大出來 (H)

我用 CANON G9 拍出來的 RAW (4000 X 3000)，存成 400x300 JPEG，約要花費 1.5 秒，比原圖尺寸的 80 秒差太多了，可見 CODEC 一定針對這種需求作過最佳化，會有效避開縮圖時不必讀取的部份資料... 以加快速度。

同樣程式改成不縮圖看看，如果不縮圖的話，ScaleTransform也可以省了，直接把 Frame 加進去就好，原程式的 line 10 ~ line 14，換成這段:



不縮圖的替代程式碼

```csharp
target.Frames.Add(source.Frames[0]);
```



嘖，只有一行也在貼... 沒錯，就是這樣而以。跑出來的時間約為 65 秒...

這部份我就沒仔細的拿 DPP 比較過了。不過當你縮圖的尺寸降低時，的確是能有效的加快速度。不過如果對於 ASP.NET WEB 應用程式來看，1.5 秒還是太慢了 @_@，十個人連上來就會想哭了，怎麼辦? 只好善用 CACHE，不然就 [買本六月號 RUN PC 看看我投的那篇文章](/post/RUNPC-2008-06.aspx) ... 哈哈...


----

PS: 這篇是寫給對岸的那位愛賞鳥的網友看的，希望有解決到你的問題。完成後也記得給我欣賞一下你們的攝影作品 :D

PS2: 範例程式放在這裡，請自行 [下載](http://www.chicken-house.net/files/chicken/WPF_Samples.zip)。圖檔請放同目錄的 SampleRawFile.CR2
PS3: 家裡大人不准我買 PS3 ...
