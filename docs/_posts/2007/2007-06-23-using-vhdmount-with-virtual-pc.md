---
layout: post
title: "Using VHDMount with Virtual PC"
categories:
tags: ["Tips","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2007/06/23/using-vhdmount-with-virtual-pc/
  - /columns/post/2007/06/23/Using-VHDMount-with-Virtual-PC.aspx/
  - /post/2007/06/23/Using-VHDMount-with-Virtual-PC.aspx/
  - /post/Using-VHDMount-with-Virtual-PC.aspx/
  - /columns/2007/06/23/Using-VHDMount-with-Virtual-PC.aspx/
  - /columns/Using-VHDMount-with-Virtual-PC.aspx/
  - /blogs/chicken/archive/2007/06/23/2462.aspx/
wordpress_postid: 157
---

Microsoft Virtual Server 2005 R2 SP1 (好長的名字...) 在兩個禮拜前出來了. 這版本總算支援了 Hardware Assisted Virtualization, 也支援了直接在 Host OS 掛上 VHD 用的工具: VHDMount...

這年頭應該不少人用過各種的 virtual cd-rom 軟體, 可以把 .iso 檔當成光碟片, "塞" 進 virtual cd-rom 來使用. VHDMount 也是一樣, 只不過它的對相是 vpc 用的硬碟映象檔 *.vhd, 而不是光碟的映象檔 *.iso ...

vmware 則是提供這種工具好久了, Microsoft 終於也支援了, 而且在 mount vhd 時會啟用 undo disk 的機制, dismount 時可以選則要不要 commit 這些 change, 真是不錯 [Y], 以後不用為了改 vhd 的內容, 還得大費周張的 boot guest os...

因為 VPC 跟 VS2005 R2 SP1 用的 vhd 格式是互通的, 因此你可以放心的在你的 XP 上面裝 Virtual Server 2005 R2 SP1, 其它項目都不要選, 只要安裝 VHDMount 這個工具就好了, 這麼一來即使你只是用 VPC, 也可以享受到 VHDMount 帶來的好處...

提外話抱怨一下, 這年頭什麼都虛擬化了, 為什麼都沒有虛擬的燒錄器? 沒有可以模擬燒錄器的 virtual cd-rom, 連 virtual machine 也沒有支援假的燒錄器... :<
