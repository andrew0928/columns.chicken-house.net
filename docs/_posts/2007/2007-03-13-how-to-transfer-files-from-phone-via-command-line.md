---
layout: post
title: "如何透過命令列, 從手機搬檔案到電腦?"
categories:

tags: [".NET","Tips","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2007/03/12/how-to-transfer-files-from-phone-via-command-line/
  - /columns/post/2007/03/13/e5a682e4bd95e9808fe9818ee591bde4bba4e588972c-e5be9ee6898be6a99fe690ace6aa94e6a188e588b0e99bbbe885a6.aspx/
  - /post/2007/03/13/e5a682e4bd95e9808fe9818ee591bde4bba4e588972c-e5be9ee6898be6a99fe690ace6aa94e6a188e588b0e99bbbe885a6.aspx/
  - /post/e5a682e4bd95e9808fe9818ee591bde4bba4e588972c-e5be9ee6898be6a99fe690ace6aa94e6a188e588b0e99bbbe885a6.aspx/
  - /columns/2007/03/13/e5a682e4bd95e9808fe9818ee591bde4bba4e588972c-e5be9ee6898be6a99fe690ace6aa94e6a188e588b0e99bbbe885a6.aspx/
  - /columns/e5a682e4bd95e9808fe9818ee591bde4bba4e588972c-e5be9ee6898be6a99fe690ace6aa94e6a188e588b0e99bbbe885a6.aspx/
  - /blogs/chicken/archive/2007/03/13/2295.aspx/
wordpress_postid: 176
---

這年頭了, 還有誰需要這種東西? 要搬檔案, 不就 active sync 連好, 檔案總管一開就好了?

不過問題沒這麼簡單... 先列一下我的需求跟問題:

1. 要能自動化, 能寫在批次檔內
2. 要能搭配 DigitalCameraFiler 自動歸檔手機的相片

本來想的很簡單, 看看檔案總管的路逕, 寫在 xcopy 後面就好, 沒想到 ActiveSync 提供的 browse device 竟然只是個 shell extension, 只是讓你 "用起來" 像是 local 的檔案而以 [:'(]

看來不修改 DigitalCameraFiler 直接讀手機的相片是不可能了, 最快的方式是找到能用命令列工具, 把檔案搬出來, 再接著用 DigitalCameraFiler 接手... 順手 google 了一下, 找到了這兩種 solution:

1. [http://www.codeproject.com/ce/rcmd.asp](http://www.codeproject.com/ce/rcmd.asp)  
   透過 Microsoft 提供的 RAPI, 寫了一個 command line 的 tools 可以辦到
2. [http://www.microsoft.com/taiwan/msdn/library/2004/...](http://www.microsoft.com/taiwan/msdn/library/2004/...)  
   MSDN 的文章, 介紹如何用 .net 開發像 (1) 這樣的 tools ...

懶人我當然是先試 (1), 可以耶!! :D, 批次檔裡動點手腳, 先把手機裡的照片檔搬到暫存目錄, 再丟給 DigitalCameraFiler 處理就好, 批次檔只要這樣寫:

> 
> ```
> ' 用亂數取得暫存目錄名
> set RND=%RANDOM%
> 
> ' 建立暫存目錄
> md %TEMP%\%RND%
> 
> ' 照片 copy 到暫存目錄
> D:\WinAPP\MobileTools\rcmd.exe copy "\Storage Card\My Documents\My Pictures\*.jpg" %TEMP%\%RND%
> 
> ' 砍掉手機上的照片
> D:\WinAPP\MobileTools\rcmd.exe del "\Storage Card\My Documents\My Pictures\*.jpg"
> 
> ' 相片歸檔
> D:\WinAPP\Tools\DigitalCameraFiler\ChickenHouse.Tools.DigitalCameraFiler.exe %TEMP%\%RND% %1
> 
> ' 砍掉暫存目錄
> rd /s /q %TEMP%\%RND%
> 
> ' 清掉環境變數
> set RND=
> ```

不過即使如此, 還是花了點時間看了 MSDN 那篇文章, 原來 Microsoft 官方都沒有把 ActiveSync 提供的 Remote API 包成 .net 版的 class library, open source 的組織就已經做好了, 連 MSDN 官方文件都引用它來試範... 哈哈, 提供一下 link:

[OpenNETCF 網站](http://www.opennetcf.org/communication.asp)

這個 wrapper 包裝的 API, 功能一點都不少, 只要手機用 active sync 連線後, 除了搬檔案等動作之外, 還可以取得手機的詳細資訊, registry, 甚至遠端叫手機執行指定的程式等等...

看起來真不錯, 下次來寫看看... [:D]
