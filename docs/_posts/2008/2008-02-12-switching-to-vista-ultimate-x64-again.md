---
layout: post
title: "再度換裝 Vista ... Vista Ultimate (x64)"
categories:

tags: ["技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/02/12/再度換裝-vista-vista-ultimate-x64/
  - /columns/post/2008/02/12/e5868de5baa6e68f9be8a39d-Vista-Vista-Ultimate-(x64).aspx/
  - /post/2008/02/12/e5868de5baa6e68f9be8a39d-Vista-Vista-Ultimate-(x64).aspx/
  - /post/e5868de5baa6e68f9be8a39d-Vista-Vista-Ultimate-(x64).aspx/
  - /columns/2008/02/12/e5868de5baa6e68f9be8a39d-Vista-Vista-Ultimate-(x64).aspx/
  - /columns/e5868de5baa6e68f9be8a39d-Vista-Vista-Ultimate-(x64).aspx/
  - /columns/post/2008/02/12/e5868de5baa6e68f9be8a39d-Vista--Vista-Ultimate-(x64).aspx/
  - /post/2008/02/12/e5868de5baa6e68f9be8a39d-Vista--Vista-Ultimate-(x64).aspx/
  - /post/e5868de5baa6e68f9be8a39d-Vista--Vista-Ultimate-(x64).aspx/
  - /columns/2008/02/12/e5868de5baa6e68f9be8a39d-Vista--Vista-Ultimate-(x64).aspx/
  - /columns/e5868de5baa6e68f9be8a39d-Vista--Vista-Ultimate-(x64).aspx/
  - /blogs/chicken/archive/2008/02/12/2976.aspx/
wordpress_postid: 124
---

暨之前[升級到 VISTA](/wp-content/be-files/archive/2007/03/27/vista.aspx) 的經驗, 到最後不適用又換回 XP 到現在, 差一個月就一年了 (真久), 這陣子因為陸陸續續解決掉一些問題, 加上一些誘因, 不得不換到 VISTA, 於是又再度換了一次...

這次會想換, 主要有幾個原因:

1. 因為硬碟滿了, 過年前買了顆 750G 的新硬碟, 可以有辦法裝新 OS 而不影響到舊系統
2. 想加 RAM, 不過原本已經是 2GB 了, 32 位元的系統 (XP) 再加上去效益不大, 想直接換到 64 位元, 個人用我也不大想換 server 版的 OS, 不大好用. 可用的 memory 雖然能突破 4GB, 但是它終究是 32 位元的系統, 對於記憶體的使用仍有一堆限制, 換成 x64 才是正途.
3. 原本用的是 XP MCE2005, 如果要保有 MCE 的功能, 又要64位元, 那只剩 Vista x64
4. Canon Raw Codec 已推出, 常用的轉檔作業都已經用 .NET Framework 3.0 改寫完成, 加上先前在 VM 試過, 可以初步解決 Canon Raw Codec 不支援 x64 的問題. 過去的障礙已經排除
5. 想開始研究一下 IIS7, Win2008 還太遙遠, 直接用現成的 vista 比較快
6. 家裡大人已經用 vista 好一段時間了, 看她用也沒啥問題...
7. 內建的東西夠多, 我是只要內建的堪用就會用的人... 內建 DVD codec, 基本的 Video DVD 編輯程式對我還蠻有用的
8. 雖然 Vista 沒啥重要的大改進, 但是每個小地方的改良加起來也不少
9. Tablet PC 功能. 前陣子弄了塊陽春的數位板, 可以直接用現成的 for Tablet PC 軟體. 又是跟 MCE 一樣的例子, 過去是有特定版本的 XP, 沒辦法同時保有 Tablet PC / Media Center / x64 等好處, 只有換 Vista 一途...
10. 雖然 Vista 預先載入你常用 AP 的功能常被罵到臭頭, 但是我倒是不介意多餘的 RAM 先拿去當 Cache 使用. 幾個常用的大型軟體, 在 Vista 下載入的速度還真的快很多, 雖然是錯覺, 但是至少也是有用到...
11. 過去 Visual Studio 2005 在 Vista 上有些小問題 (要加裝 patch), 在 x64 下問題更多... 尤其是 debugging 時. 現在 Visual Studio 2008 出來, 這類問題都解決的差不多了
12. Vista SP1 快出了, 時機應該成熟了, 預先準備一下...
13. 最重要的原因: 都買了正版 Vista 了, 放著不用是怎樣... [H]

補充個事後才發現的好處, Vista Complete PC 是內建的磁碟備份工具, 類似 GHOST 那樣, 是把你整顆硬碟做成映像檔. Microsoft 當然用它推廣的格式 *.vhd, 正好跟我常用的 Virtual PC / Virtual Server 的格式一致. 多好用? 簡單在 Vista 內點兩下就可以做 Disk Image, 以後需要的話可以直接用 Vista DVD 還原, 就像 GHOST 一樣. 或是直接用 Virtual Server 2005 R2 SP1 附的工具: [VHDMOUNT](/post/Using-VHDMount-with-Virtual-PC.aspx), 直接掛起來用 [Y]

另外一點也要特別提一下. 原本搜遍了 GOOGLE, 得到的答案清一色都是 Canon Raw Codec 不支援 Vista X64. 官方說法跟使用者討論都是這樣. 我是硬著頭皮先在 VM 裡試了一下, 耶? 至少還可以安裝上去. 不過果然不行. 我自己寫的[轉檔工具](/post/Canon-Raw-Codec-2b-WPF-12c-WPF-Image-Codec2c-Metadata.aspx)不能用, 如預期的找不到對應的 Codec. 在 Windows Live Gallery 及檔案總管下也不能直接看到 .CR2 的縮圖...

不過想到過去跟 X64 + WOW (是 Windows On Windows, 不是魔獸世界) 奮戰的經驗, 其實 Microsoft 做的 32 位元回朔相容作的還不錯. 只是有一個大前題: 32 / 64 兩種 CODE 不能混在一起執行. 同一個處理程序 (Process) 內必需都是 32 或是 64 位元的 code. 第一個碰到這種問題的就是各式軟應體的 driver. 硬體的就不說了, 軟體的像一堆 "虛擬" 裝置, virtual cdrom, virtual disk, virtual network adapter ... 等等. 第二個碰到的就是各式的 DLL, 它本來就是讓你載入到你的 Process 內使用的, 像一堆 ODBC driver, COM 元件, ActiveX Control, Video Codec, 加上 WPF 使用的 Image Codec, 都在此列. 這種才是真正的問題, 就像 Microsoft 可以把 IE 重新用 64 位元改寫, 但是它無法替所有的 ActiveX Control 改寫為 64 位元, 因此未來的五年內, 光是 IE 這東西, 你大概還是甩不掉 32 位元版本...

這類相容問題通常都是整套用 32 位元版本就可以解決, 就像 IE 你只要開啟 32 位元版本的話, 即使你是在 x64 OS, 也不會有太大問題. 32 位元的程式在 64 位元 OS 下執行, 還附帶了一些額外的好處. 記憶體管理就佔了不少便宜. 光是記憶體各種管理的動作就快很多 (以前看過相關文章, 不過找不到了 [:P], 下次寫 code 來測看看), 加上 32 位元的基本限制: 4GB memory size, 因為 OS 已經是 64 位元了, 4GB 可用的定址空間不用再切 2GB 給 OS 使用... 因此你的程式可用的定址空間也從 2GB 擴張到 4GB, 不無小補.

想到這些案例, 我就試了一下... 我自己寫的歸檔工具不能跑, 如果我把它切到 32 位元模式呢? 改了改 compile option, target platform 從原本的 "Any CPU" 改為 "x86", 耶! 可以了耶... 程式能正確的抓到 Canon Codec, 並且正確的解碼跟抓到 metadata.

再試一下 Windows Live Gallery, Microsoft 還算有良心, 裝好後就有兩種 32/64 版本. 我開了 32 位元版, .CR2 的照片也都可以正確顯示.. 哇哈哈... 讚 [Y]

不過 Windows Live Gallery 有些地方要注意, 它似忽載入後會留著, 類似古早的 OLE server 一樣的技術, 跑起來後就會留在系統內, 待下次有人要執行時繼續使用. 因此如果沒有在 BOOT 後第一次就開正確的版本, 以後就有可能你開 32 位元版, 它還是跑 64 位元的給你看...

這個問題可以解決, 算是讓我願意換 Vista x64 最主要的原因, 不然我大概會傻傻的等到 Canon 好心的推出 64 位元版的 codec 才換吧 [H], 這次升級 Vista 應該不會再像上次一樣, 用一用就換回去了... 想換 x64 的人就不用再撐了, 上吧!!!
