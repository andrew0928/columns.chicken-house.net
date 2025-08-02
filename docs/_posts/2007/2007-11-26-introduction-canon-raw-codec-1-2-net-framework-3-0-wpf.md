---
layout: post
title: "前言: Canon Raw Codec 1.2 + .NET Framework 3.0 (WPF)"
categories:
- "系列文章: Canon Raw Codec & WPF"

tags: [".NET","WPF","作品集","多執行緒","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2007/11/26/前言-canon-raw-codec-1-2-net-framework-3-0-wpf/
  - /columns/post/2007/11/26/e5898de8a880-Canon-Raw-Codec-12-2b-NET-Framework-30-(WPF).aspx/
  - /post/2007/11/26/e5898de8a880-Canon-Raw-Codec-12-2b-NET-Framework-30-(WPF).aspx/
  - /post/e5898de8a880-Canon-Raw-Codec-12-2b-NET-Framework-30-(WPF).aspx/
  - /columns/2007/11/26/e5898de8a880-Canon-Raw-Codec-12-2b-NET-Framework-30-(WPF).aspx/
  - /columns/e5898de8a880-Canon-Raw-Codec-12-2b-NET-Framework-30-(WPF).aspx/
  - /blogs/chicken/archive/2007/11/26/2833.aspx/
wordpress_postid: 134
---

[搞了好幾天](/post/Canon-G9-e585a5e6898b2c-e4b88de9818e.aspx), 終於理出點頭緒了. 自從 [Canon 推出 1.2 版的 codec](http://software.canon-europe.com/software/0026049.asp) 之後, G9 拍的 .CR2 支援問題總算是往前跨了一大步, 至少在 XP / Vista 下可以直接顯示 .CR2 了. 接下來就是如何讓它[自動化](/wp-content/be-files/archive/2006/12/23/cr2-supported.aspx)等等問題.

WPF寫起來很簡單, 效率的問題就先擺一邊了 (很理想的預期 canon 會在未來版本會改善... 咳...), 不過 EXIF 的問題還真是令我傷透腦筋... 前前後後碰到幾個問題, 加上官方文件很多細節沒有提供, 讓我碰了不少釘子... Orz. 先整理一下碰過的釘子有那些 (現在當然拔乾淨了才有心情打這篇.. 哈哈 [H]), 先列一下問題最大的 metadata:

1. Metadata抓不到, BitmapSource.Metadata 抓出來都是 null ..  
   (後來發現文件漏掉一行... Orz, 目前版本不提供 BitmapSource.Metadata, 只提供每個 Frame 自己的 Metadata ...)

2. 內建的 Metadata 只有十個不到的欄位 (ApplicationName, CameraModel, ...), 問題是 exif 有一堆啊..

3. WPF 改用 "Metadata Query Language", 類似 xpath 之於 xml document 一樣... 看起來就像 "/ifd/{ushort1000}" 這樣. 所有底層動作都是 GetQuery( ) / SetQuery( ). 不過沒有地方讓我列舉出所有已存在的 metadata query 啊...

4. 文件上說用 InPlaceMetadataWriter 可以修改 metadata, 不過到現在我還是試不出來 -_-

5. EXIF 上百個欄位, 對應的 query, 官方文件一個字都沒提到... 冏rz...

6. .CR2 解出來的 metadata 跟 .JPG 廣為接受的 EXIF, 對應的 query 完全不一樣...

另外其它跟 metadata 無關的問題也有幾個:

1. Canon Codec 的效能不怎麼樣, G9 的檔案 (4000x3000, 15mb 左右) 全幅解開, 接上 JpegEncoder 存同尺寸 100% quality 檔案, 在我的 Core2Duo E6300 (2GB ram, XP MCE2005 SP2) 足足要 80 sec ...

2. 多處理器佔不到便宜. 雙核CPU跑下去, 處理器只有約 50% ~ 60% 使用率. 改了改程式, 開兩個 thread 下去也一樣, 殘念... ( Microsoft 的就要誇一下, 內建的 codec 就運作的很好... 又快, thread pool 用下去也享受的到全速.. [Y])

3. 怪的很, Microsoft 提供的 viewer 直接看 G2 的 .CRW 一切正常, 不過透過 WPF 就會得到 Exception .. 還沒解.

這些鳥問題都在 MSDN 找不到直接的答案, 只好埋頭苦TRY了. 好消息是主要問題都解的差不多了. 先簡單列一下 solution, 後續的等我 [歸檔程式] 改版完成後再來專欄報導..

1. Metadata Query 列舉的問題原來隱藏在實作的 interface 裡.. [:@], 氣的是官方文件還沒有任何說明 & 範例. 原來 BitmapMetadata 實作了 IEnumerable<string>, 直接把 BitmapMetadata 丟到 foreach 裡就是了...

2. 修改 metadata 的動作, 暫時由 metadata.clone() 之後修改, 再加到 encoder 裡可以閃開碰到的問題, 就不理它了

3. EXIF 問題, 因為 (1) 有解了, 加上 google 找到其它 sample, 東拼西湊誤打誤撞也被我試出來... 哈哈

4. 效能問題一樣無解, 只能改程式儘量把不相干的 job 排在一起, 想辦法把空閒的 CPU 運算能力吃掉... 就看是我改的快還是 canon 改的快了 [H]..

前言大概就先打到這裡, 沒啥內容, 都只是預告片而以, 被它折磨了兩個禮拜, 當然要先貼一篇發洩一下. 剩下的工作就單純多了, code 改到一個段落我就會繼續寫後續幾篇. 這次會包括兩個 project, 一個是 Image Resizer, 另一個就是之前好幾篇都在講的歸檔工具. 敬請期待!

替舊文章打一下廣告... [H]

- [歸檔工具更新 - .CR2 Supported](/wp-content/be-files/archive/2006/12/23/cr2-supported.aspx)
- [Digital Camera Filer - Source Code (update)](/post/Digital-Camera-Filer---Source-Code-(update).aspx)
- [Canon Digital Camera 記憶卡歸檔工具 - Release Notes](/post/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---Release-Notes.aspx)
- [Canon Digital Camera 記憶卡歸檔工具 - RAW Support Update](/post/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---RAW-Support-Update.aspx)
- [Canon Digital Camera 相機獨享 - 記憶卡歸檔工具](/post/Canon-Digital-Camera-e79bb8e6a99fe78da8e4baab---e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7.aspx)
