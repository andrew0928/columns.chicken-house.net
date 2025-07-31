---
layout: post
title: "Canon Digital Camera 記憶卡歸檔工具 - Release Notes"
categories:

tags: [".NET","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2006/11/17/canon-digital-camera-記憶卡歸檔工具-release-notes/
  - /columns/post/2006/11/17/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-Release-Notes.aspx/
  - /post/2006/11/17/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-Release-Notes.aspx/
  - /post/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-Release-Notes.aspx/
  - /columns/2006/11/17/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-Release-Notes.aspx/
  - /columns/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7-Release-Notes.aspx/
  - /columns/post/2006/11/17/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---Release-Notes.aspx/
  - /post/2006/11/17/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---Release-Notes.aspx/
  - /post/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---Release-Notes.aspx/
  - /columns/2006/11/17/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---Release-Notes.aspx/
  - /columns/Canon-Digital-Camera-e8a898e686b6e58da1e6adb8e6aa94e5b7a5e585b7---Release-Notes.aspx/
  - /blogs/chicken/archive/2006/11/17/1952.aspx/
wordpress_postid: 205
---

好戲不拖棚了, 這個小工具寫到現在, 大部份的問題都解決掉了, 接下來除非有碰到啥 Bug, 否則就不會再大改版了. 在這裡總結一下:

## Overview

DigitalCameraFiler 是專為數位相機記憶卡歸檔用的工具, 包括一般相片, raw file, 及 video clip, 可以依照拍照時的各種資訊 (exif, 包括拍照時間, 相機型號, 光圈值, 快門值... etc) 的組合當成檔名及目錄名稱自動歸檔. 這個工具沒有 windows 介面, 為 Console Application. 可以搭配批次等等工具一起使用.

## How it work

這工具運作的方式很簡單, 它會掃描指定的目錄 (記憶卡) 下的所有檔案, 碰到支援的檔案類型就會依照定義好的歸檔動作去處理它. 以下是這個工具支援的幾種類型, 及它的處理方式:

1. **JPEG file**: 最常見的類型, 碰到 *.jpg 檔會先依照 exif 裡的 Orientation 值決定要不要把照片轉正. 轉好後就把照片放到指定位置.

2. **RAW file**: 支援 Canon 的 *.crw 檔案. crw 會搭配對應的 .thm 檔, 會從這兩個檔案取得必要的 exif 資訊, 用來做歸檔的動作. 除了把 .crw 放到指定位置之外, 也會另外把 .crw 轉成 .jpg 放在同一個目錄下. 在轉換檔案格式的同時, 也會把對應的 .thm 檔的 exif 都複製一份到 .jpg 檔.

3. **VIDEO file**: 支援 Canon 拍攝的 MJPEG ( *.avi ) 檔. Canon 一樣會準備一份對應的 .thm 檔, 歸檔 .avi 時就會依照對應的 .thm 內的 exif 資訊為準.

## Configuration

這個工具主要的目的就是依照 exif 等資訊來安排歸檔的路逕, 因此設定的方式採取 .net framework 裡通用的 format string 格式為準. 細節可以直接參考 MSDN 網站, 設定的方式如下:

> **pattern**: 格式化字串. 大括號 { } 內的數字代表要用後面定的第幾個 exif 代碼替代.
>
> **exif list**: 你要取用的 exif variable list. 序號從 0 開始算.

舉例來說, 如果你指定的 pattern 為:

> `c:\photos\{0:yyyy-MM-dd}\{1}-{2}`

而指定的 exif variable list 為:

> `DateTime,Model,FileName`

則用我的 G2 在 2006/11/11 拍的照片 IMG_1234.jpg 則會被歸檔到這個位置:

> `c:\photos\2006-11-11\Canon PowerShot G2-IMG_1234.jpg`

pattern 可以依照這樣的原則任意指定, 不存在的目錄會自動建立, 而可用的 exif variable 到底有多少? 在命令列執行這個工具, 不帶任何參數的話就會列出所有的變數名. 這些設定寫在 DigitalCameraFiler.exe.config 檔案內, pattern 可以各別為 JPEG / RAW / VIDEO 分別指定, 而 EXIF List 則是共用的.

下回會把 source code 也一起 release 出來, 請有耐心點等待 :D

**安裝檔下載位置**: [http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip](http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip)
