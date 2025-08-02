---
layout: post
title: "JPEG XR (就是 Microsoft HD Photo 啦) 已經是 ISO 正式標準了..."
categories:

tags: [".NET","WPF","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2009/08/05/jpeg-xr-就是-microsoft-hd-photo-啦-已經是-iso-正式標準了/
  - /columns/post/2009/08/05/JPEG-XR-(e5b0b1e698af-Microsoft-HD-Photo-e595a6)-e5b7b2e7b693e698af-ISO-e6ada3e5bc8fe6a899e6ba96e4ba86.aspx/
  - /post/2009/08/05/JPEG-XR-(e5b0b1e698af-Microsoft-HD-Photo-e595a6)-e5b7b2e7b693e698af-ISO-e6ada3e5bc8fe6a899e6ba96e4ba86.aspx/
  - /post/JPEG-XR-(e5b0b1e698af-Microsoft-HD-Photo-e595a6)-e5b7b2e7b693e698af-ISO-e6ada3e5bc8fe6a899e6ba96e4ba86.aspx/
  - /columns/2009/08/05/JPEG-XR-(e5b0b1e698af-Microsoft-HD-Photo-e595a6)-e5b7b2e7b693e698af-ISO-e6ada3e5bc8fe6a899e6ba96e4ba86.aspx/
  - /columns/JPEG-XR-(e5b0b1e698af-Microsoft-HD-Photo-e595a6)-e5b7b2e7b693e698af-ISO-e6ada3e5bc8fe6a899e6ba96e4ba86.aspx/
wordpress_postid: 36
---

先寫在前面，這篇不是什麼技術的探討或是評論，純脆是我個人看到這消息的想法而已。很久沒貼些軟體相關的文章了，最近比較少在動手寫 Code, 自然就沒什麼新題材好寫 @@，不過這兩天倒是看到一個蠻令人興奮的新聞，就是:

**JPEG XR 已經正式通過 ISO 標準了!!**

http://jpeg.org/newsrel26.html  
http://blogs.msdn.com/billcrow/archive/2009/07/29/jpeg-xr-is-now-an-international-standard.aspx

JPEG 應該已經無人不知，無人不曉了吧? 不過當年還是有朋友鬧過笑話... 曾有人正經八百的來問我

"什麼是 [結合照片專業群組] 啊???" 就是 JPEG 啦 (無聊的話看一下底下的題外話)

> 我還丈二金剛摸不著頭腦，把他在看的整篇文章拿過來看，才晃然大悟他到底在問啥 =_= ... 原來是 "JPEG: Joint Photographic Experts Group"的縮寫... 當然類似的 MPEG (Moving Picture Experts Group) 也碰過類似的笑話... 無聊 GOOGLE 一下，竟然還查的到一篇範例...

> http://support.microsoft.com/default.aspx/kb/235928/zh-tw

> My God… 這翻譯真是比之前碰到了 "[註冊傑克](/post/e6b0b4e99bbbe5b7a5e697a5e8aa8c-4-e9858de68ea5e99bbbe8a9b1e7b79a-amp3b-e7b6b2e8b7afe7b79a.aspx)" 還絕 XD...

之前其實沒特別注意這些標準，曾經有印像的就是用 wavelet 壓縮方式的 JPEG2000... 嘗試取代 JPEG，也取得 ISO 的標準化，不過一直沒達成它的目的，只在特定領域還有應用空間。兩年前 Microsoft 隨著 Vista / WPF 推出 Windows Media Photo 的格式，後來為了讓它成為標準，換了個叫沒有 MS 色彩的名字: HD Photo, 最後變成現在的 JPEG XR ..

我是在兩年前，隨著 .NET 3.0 推出 WPF，剛好自己用的 CANON 相機的 RAW FILE 又被 WPF 支援，所以開始[研究](/category/WPF.aspx)相關的 API 及 support .. 在關於 HD Photo 眾多報導中，有個觀點是我相當認同的。找不到較具代表性的消息來源，我就憑記憶寫一下，大意是:

隨著技術進步，未來影像設備 (如印表機，掃描器，顯示器等等) 的色彩表現能力及色域會遠超過 JPEG 格式的範圍 (現在就是了)，因此儲存格式支援的動態範圍 (dynamic range) 越高，對於影像的長期保存越重要。

這就是處女座的龜毛個性啊... 衝著這個看法，我從 Canon PowerShot G2 時代開始，我就試著盡量用 .CRW 格式 (CANON RAW) 來保存相片，而不是用 JPEG。後來換了 Canon PowerShot G9，正好 WPF 出來，我就開始改用保存 .CR2 檔，而另外轉一份 JPEG 檔來作一般用途 (畢竟 JPEG 還是方便的多)。不過一張照片花掉 15 ~ 20mb, 保存起來壓力還真不小 =_=

現在看到 JPEG XR 的標準化，正好是我要的東西啊 :D 我需要的正是個能妥善保存這些影像資料細節的方式，同時能讓我輕鬆愉快的使用，不用耽心工具支不支援，或是其它五四三等問題困擾...。這些問題對阿宅來說，一點都不困難，有一缸子的工具辦的到，不過... 如果隨變看個照片，或是要 COPY 給家人朋友看，還要動用一堆雞絲，那也太辛苦了一點... 能有個通用的標準格式及大廠背書，那是再好也不過了 :D

所以，接下來要做什麼? 我突然慶興我一直都有留著這幾年拍下來的 RAW file (.CRW / .CR2) 檔案... 該是替我的歸檔程式翻新的時後了，下一步是開始嘗試用 .WDP 來取代現在放兩份 RAW + JPEG 的方式... 
