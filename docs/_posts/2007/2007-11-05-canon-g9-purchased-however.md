---
layout: post
title: "Canon G9 入手, 不過..."
categories:

tags: ["技術隨筆","敗家","有的沒的"]
published: true
comments: true
redirect_from:
  - /2007/11/05/canon-g9-入手-不過/
  - /columns/post/2007/11/05/Canon-G9-e585a5e6898b2c-e4b88de9818e.aspx/
  - /post/2007/11/05/Canon-G9-e585a5e6898b2c-e4b88de9818e.aspx/
  - /post/Canon-G9-e585a5e6898b2c-e4b88de9818e.aspx/
  - /columns/2007/11/05/Canon-G9-e585a5e6898b2c-e4b88de9818e.aspx/
  - /columns/Canon-G9-e585a5e6898b2c-e4b88de9818e.aspx/
  - /blogs/chicken/archive/2007/11/05/2788.aspx/
wordpress_postid: 136
---

想了很久的 Canon PowerShot G9 終於狠下心的敗下去了, 買了英日機的水貨, 約比公司貨便宜三千塊... 其實已經買了兩個禮拜, 但是碰到一堆小障礙, 所以拖到現在才寫 BLOG...

打從 G6 就開始物色新機, G6 因為跟 G2 都採用 DIGIC chip, 功能效能都沒啥大長進, 連 video 也都是很兩光, 不考慮... S2 IS, S3 IS 沒有熱靴不考慮, S5 IS 撐了很久, 最後還是決定留在 G 系列. G7 換了 DIGIC II 則是大改版, 光圈變小, 翻轉 LCD 沒了, 連 RAW 都沒了... 不考慮. G9 跟 G7 差不多, 就是把 RAW 加回來, 換 DIGIC III ... 覺的還在可接受範圍內, 就敗了 [:D], 那 G8 呢? 很抱歉... Canon 沒出 G8 .. Orz.

事前雖然功課作足了, 不過買回來後還是碰到了些小障礙:

1. 畫質普普, 大部份情況跟 G2 半斤八兩, 不過有些時後 G2 還略勝一籌... 這是意料之中, 沒有很意外, 那麼小的 CCD 擠這麼多像素進去, 這是必然的. 只不過還是有點失望, 怎麼沒有奇跡出現..

2. 像素 12M, 拍下來的 raw file 足足有 12 ~ 15mb, jpeg 也有 3 ~ 4 mb, 如果用 RAW+JPEG 模式, 最多 18mb 就去了... 附的 32mb SD 真的是只能塞牙縫... 為了這個只好去買 SDHC 的記憶卡, 連帶的讀卡機都得換掉...

3. RAW file 解不開... 這點最頭痛. Photoshop 元件更新後認不得 G9 拍的 .CR2, Canon 自己附的 Raw Image Converter 也不吃, DPP 3.0 也不吃, Raw Codec for Vista 1.0 也不吃, Microsoft Raw Image Viewer 也不吃, Google Picasa 可以讀, 不過顏色不正常... 試了一堆支援 .CR2 的軟體, 除了隨機光碟附的 ZoomBrowserEx 之外, 沒一個能用的 [:'(]

4. 因為 (3) 的關係, 連帶的我自己寫的歸檔程式也不能動了...

不過還好, 除了這些缺點之外, 其它一切如預期, 老實說電子元件本身的改變, 跟鏡頭加上 IS 真的很不錯, 整體還是值得的... 這兩個禮拜就都在搞這些小問題... 因為 (3) 的關係, 只好改一下原本的歸檔程式, 同時改變習慣一定要用 RAW+JPEG 模式, 在歸檔的動作裡跳過 RAW --> JPEG 這步驟的動作.. 勉強可用. 反正 8GB SD 卡暫時也拍不滿..

感謝老天, 就在前天, Canon 終於發怖了 Canon Raw Codec 1.2, 支援 G9 拍的 Raw File 了. 連帶的 G2 的 Raw 也在支援範圍內, 就改起程式來試看看... 不過情況也不怎麼樂觀. 細節就不講了, 以後另外再寫一篇, 我先寫初步得到的資訊:

1. Codec 可以搭配 Microsoft .NET Framework 3.0 的 WPF ( Windows Presentation Foundation ) 使用. 雖然官方說 for Vista 32bits only, 不過我自己在 XP SP2 下也是可以用.

2. 15mb 的 .CR2, decode 速度... 有... 夠... 慢... [:@], Core2Duo 6300 竟然要解到快一分鐘... CPU 使用率約只有 50%, 改了改程式, 用 thread pool 一次解兩個 raw file, 一樣... CPU 使用率只有 5x%... 看來這個 codec 是 Single Thread Apartment 模式跑的... 雙核 CPU 派不上用場

3. 慢就算了, 不知是 codec 的問題, 還是 .net runtime callable wrapper 的關係, 透過 WPF 抓不到任何的 metadata (exif), 傳回的 BitmapMetadata 物件就是 null ...

天那, 這個 codec 對我等於完全沒用了 [:'(], 歸檔程式就是靠一堆 exif 才能達到自動歸檔, 改檔名, 照片轉正... 現在不旦讀不到 exif, 同時一張解開就要花 60 sec...

看來用 RAW + JPEG 拍照的模式得撐上好一陣子了, 要改版就得等 canon raw codec 再改善一點了..
