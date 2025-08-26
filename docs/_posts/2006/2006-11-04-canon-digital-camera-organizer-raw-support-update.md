---
layout: post
title: "Canon Digital Camera 記憶卡歸檔工具 - RAW Support Update"
categories:

tags: [".NET","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2006/11/04/canon-digital-camera-記憶卡歸檔工具-raw-support-update/
  - /columns/post/2006/11/04/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-RAW-Support-Update.aspx/
  - /post/2006/11/04/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-RAW-Support-Update.aspx/
  - /post/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-RAW-Support-Update.aspx/
  - /columns/2006/11/04/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-RAW-Support-Update.aspx/
  - /columns/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-RAW-Support-Update.aspx/
  - /columns/post/2006/11/04/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---RAW-Support-Update.aspx/
  - /post/2006/11/04/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---RAW-Support-Update.aspx/
  - /post/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---RAW-Support-Update.aspx/
  - /columns/2006/11/04/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---RAW-Support-Update.aspx/
  - /columns/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---RAW-Support-Update.aspx/
  - /blogs/chicken/archive/2006/11/04/1918.aspx/
wordpress_postid: 212
---

每次貼新東西, 小熊子都會來支持一下... 這次寫的記憶卡歸檔工具, 既然他抱怨了一下不支援 RAW file, 那當然要來找一下 solution.. 哈哈..

順手找了一下, 發現資源真少, 追到最後只有一些 open source 的 project 提供 Canon 的 Raw File Access, 另外 Canon 也有自己的一套 Digital Camera SDK ( free, C++ only ), 要寫信去要, 不過不用收費就是.. 其它都是不成熟的 project, 看起來都不是很可靠 :S

咳, c++ 已經好幾年沒碰了, 拿來唬唬還可以, 真的要動手就算了... 結果剛好讓我找到一條線索... Microsoft 提供一個簡單的 viewer, 可以直接看各家的 RAW file, 名字落落長: [Microsoft RAW Image Thumbnailer and Viewer for Windows XP](http://www.microsoft.com/downloads/details.aspx?FamilyId=D48E808E-B10D-4CE4-A141-5866FD4A3286&displaylang=en&Hash=AKaUVvxBh5XTO8fSXj6oUQmxLZAIkGTh8NzlZpwqSoCKqxdFKhVexFexOz1oLkXYi7C3rLi1dzbWfrUGColAfA==) ...

印相中這個工具可以看 canon crw, 而且安裝的系統需求是要裝 .net framework..

> "該不會有現成的 .net assembly 可以讀 canon raw file 的內部資訊吧?"

試了一下, 隨便找個看的順眼的 dll 反組譯一下, 老天真是照顧我啊, 中獎!! 哇哈哈... 原本 DigitalCameraFiler.exe 的程式架構其實早就想好要怎麼改了, 只是之前一直找不到適當的 lib..

找到的 assembly 用法很簡單, 只要先裝好 Microsoft RAW Image Thumbnailer and Viewer for Windows XP, 就可以在安裝目錄找到這個 assembly dll: RawManager.Interop.dll

使用的方式也很簡單 (感謝 Microsoft 工程師的 coding style 都很一致... ), 隨便試一下就試出來了:

```csharp
   22     CRawViewerClass raw = new CRawViewerClass();
   23     raw.Load(@"c:\CRW_1234.crw");
   24     Console.WriteLine("Camera Model: {0}", raw.CameraModel);
```

這 Interop assembly 寫的還真不錯... 看起來真正做事的仍然是 Canon Digital Camera SDK... 不過現在我也可以用 C# 很簡單的叫來用, 哈哈, 感覺真爽...

不過還沒挖到可以 edit raw 的 API, 感覺遜了一點, 但是小熊子都說了...

> chicken: 不過抓的東西很有限 :S, 也還沒辦法自動轉正  
> Michael (小熊子): raw 不需要轉正說  
> Michael (小熊子): raw 只要知道啥米時間拍的應該就 OK

所以這部份就再說了 [H]... 哈哈...

更新過的檔案下載: [DigitalCameraFilerSetup.msi](http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip)  
使用前請先安裝: [Microsoft RAW Image Thumbnailer and Viewer for Windows XP](http://www.microsoft.com/downloads/details.aspx?FamilyId=D48E808E-B10D-4CE4-A141-5866FD4A3286&displaylang=en&Hash=AKaUVvxBh5XTO8fSXj6oUQmxLZAIkGTh8NzlZpwqSoCKqxdFKhVexFexOz1oLkXYi7C3rLi1dzbWfrUGColAfA==)
