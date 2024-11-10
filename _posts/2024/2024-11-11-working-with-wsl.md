---
layout: post
title: "關於我轉升成為 Linux 用户的那件事"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---

![](/wp-content/images/2024-11-11-working-with-wsl/logo.jpg)
> 圖: DALL-E, 我讓 ChatGPT 搜尋我自己然後畫出來的形象圖..


最近認真的重新整理我桌機的開發環境了。以前都是 90% 以 windows 為主的工作環境 ( visual studio, powershell, docker desktop, NTFS ... )，我主要都用 .NET，反正主要的工具都有 windows 版，沒用原生的 Linux 環境好像也沒那麼重要，必要時用 Hyper-V 或是 Docker 擋一下，日子也是過得去...

不過，最近有幾個情境，首選都是 Linux，讓我認真考慮要跨出純 windows 環境的舒適圈了... 也因為這樣，最近認真了研究一下 WSL ( Windows Subsystems for Linux )，才發現 Microsoft 在整合兩大作業系統上花了不少功夫，老實說挺厲害的，這應該是其他第三方工具到達不了的境界。

這篇，就當作我個人轉移工作環境的心得文好了。其實我要講的都不是新聞了，有認真在這環境下工作的人大概也都熟悉了，我就當作野人獻曝，講一下我的作法，跟我理解背後 WSL 比單純的 VM 還多做了什麼整合。


<!--more-->

我要解決的情境有這幾個:

1. docker 效率問題，docker desktop for windows 很多餘，docker container 的 IO 效率很糟糕..
2. 能在 docker 下順利的運行 AI / LLM 的應用，要能高效率的使用我本機的運算資源 ( GPU, CPU, RAM, Disk ...)
3. 需要桌面應用的操作 (例如 editor, IDE, browser 等等 ) 仍然保留 windows 的介面

過去就無腦的在 windows 下開專案，然後在 PowerShell 下啟動 docker 跑 container，基本上 WSL 我只把它當作執行 container 的 host 而已，沒有太多機會直接開 shell 進去下指令，直到我決定調整我工作環境..


# 1. 換工作環境的動機

起因是最近在研究 AI 的相關應用開發，免不了都會碰到向量資料庫的建置...。我用的是 Microsoft Kernel-Memory 這個服務，他做的是封裝 RAG 必要的幾個元件，包含 LLM, Embedding, VectorDB, 以及 File Storage ...

我選擇了 Qdrant 當作 VectorDB, 而當我想倒入約 40000 萬筆資料的時候 (這數量以資料庫來說不算很多吧?)，竟然發現建立一筆資料要花掉 5sec, 而且不論我怎麼優化都沒有用, 看了 CPU / Memory / Disk 也都正常..

接著重啟服務 (我用 docker compose), 結果服務竟然要花一分多鐘才能啟動完成, 我心裡想這是什麼狀況? 我的桌機雖然是五年前的設備，但是也沒這麼不堪吧? 我列一下我的配備:

CPU: AMD Ryzen9 3900X
RAM: DDR4 16GB x 4 ( 64GB )
SSD: Samsung 970Pro 512GB, PCIE 3.0, NVME
OS: Microsoft Windows 11 Pro ( 當時跑的是 23H2 )

最後，我想起我多年前踩過的地雷，而且還踩過好幾次... 姑且確認看看吧，我把整個 docker compose 的目錄，包含 docker volumes 都搬到 WSL 內的 ~/mskm 目錄下，這次直接在 WSL 下啟動 docker ...

結果竟然秒開.. 然後匯入資料的速度變正常了 (一秒可以跑 5 筆左右)，基本上就是卡在 embedding 的速度了。差了幾十倍的速度，這才正常的表現啊，經歷過這次，我知道以後只會越碰越多，於是就決定翻掉整個工作環境了。


# 2. 確認 Disk IO 的差異

首先，我好奇 Disk IO 的效率到底有差多大，花了點時間了解一下...

基本上，問題來自跨 OS 的 file system 互通這層。Windows Kernel / NTFS 算是 Windows 原生的系統，我就不用管他了。效率自然是沒問題。而 WSL2 開始，Microsoft 的做法基本上是內含一個 Hyper-V 的 VM 來跑 Linux Kernel，然後外掛各種機制來讓你覺得 Windows / WSL 是無縫銜接的，而這中間的效率問題就是元兇...

簡單的區隔一下，使用 WSL 時，磁碟空間大致可以分兩大區域:

1. 來自 windows 原生的 disk, 基本上你在 disk manager 看的到的 ( c:\ , d:\ , e:\ 等等 ) 都屬於這類
1. 來自 WSL 虛擬硬碟 ( wsl.vhdx ) 的, 例如 ~/ 都屬於這類

從使用情境來看，大致也是兩種狀況:
1. 在 WSL 下，執行 linux application, 可以透過 /mnt/c 這種路徑來存取 windows c:\ 的檔案，這些檔案是透過 drvfs mount 掛上去的，這就是跨系統的檔案存取。
1. 另一種是在 windows 下，執行 windows application，藉由 \\wsl$\ubuntu\... 這種路徑來存取 WSL 下 /... 的檔案，這種也是跨系統的檔案存取，靠的是 9P protocol ..

參考虛擬化領域的專家 MVP 的說明:

![](https://www.netadmin.com.tw/netadmin/upload/pic/2023-03/202303301530430456147917.jpg)
> 來源: 網管人 [第2版視窗子系統Linux - 二刀流無縫順暢運行](https://www.netadmin.com.tw/netadmin/zh-tw/technology/EDC6D4560B184F0D9E7A750862D3C9E4)


通常，像我這種 windows 為主的人，使用 docker / wsl 的情境，大都是把檔案擺在 windows 管理範圍內，用熟悉的 windows 管理工具來編輯或是整理檔案 ( vscode, 檔案總管 等等 )，碰到的是 (1) 這種狀況。過去我只知道 (1) 這種狀況的 IO 效能是 "有感" 的慢，到底慢多少我還真沒認真測過.. 這次我剛好升級了設備，就來試試看:

我用的設備是同一套，就我的桌機，規格跟組態如下:

CPU: AMD Ryzen9 3900X
RAM: DDR4 16GB x 4 = 64GB
SSD: Crucial T500 2TB PCIe Gen4 NVMe M.2 SSD
GPU: NVidia RTX 4060Ti - 16GB
OS: Microsoft Windows 11 Pro (24H2)
WSL Distro: Ubuntu 24.04 LTS


我在 WSL 下跑 Linux 的磁碟效能測試工具: Bonnie++, 第一組 測試存取 ~/temp 目錄的讀寫效能

```
Version 2.00a       ------Sequential Output------ --Sequential Input- --Random-
                    -Per Chr- --Block-- -Rewrite- -Per Chr- --Block-- --Seeks--
Name:Size etc        /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP
ANDREW-PC       63G  540k  99  728m 100  958m  91 2205k  99  1.1g  58 +++++ +++
Latency             16366us    5650us   12027us    4465us    1806us     478us
Version 2.00a       ------Sequential Create------ --------Random Create--------
ANDREW-PC           -Create-- --Read--- -Delete-- -Create-- --Read--- -Delete--
              files  /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP
                 16 +++++ +++ +++++ +++ +++++ +++ +++++ +++ +++++ +++ +++++ +++
Latency               586us     404us    3818us    3324us     837us    3156us
1.98,2.00a,ANDREW-PC,1,1731168315,63G,,8192,5,540,99,745124,100,980550,91,2205,99,1203968,58,+++++,+++,16,,,,,+++++,+++,+++++,+++,+++++,+++,+++++,+++,+++++,+++,+++++,+++,16366us,5650us,12027us,4465us,1806us,478us,586us,404us,3818us,3324us,837us,3156us
```

第二組, 一樣 WSL 下，只是測試的目錄是 /mnt/c/temp 的讀寫效能

```
Version 2.00a       ------Sequential Output------ --Sequential Input- --Random-
                    -Per Chr- --Block-- -Rewrite- -Per Chr- --Block-- --Seeks--
Name:Size etc        /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP
ANDREW-PC       63G    6k   6 50.6m   6 22.2m   6    6k   7 39.4m   4  8475 109
Latency              1445ms   17524us    9356us    1284ms    5950us     408ms
Version 2.00a       ------Sequential Create------ --------Random Create--------
ANDREW-PC           -Create-- --Read--- -Delete-- -Create-- --Read--- -Delete--
              files  /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP  /sec %CP
                 16     0   6     0   7     0   7     0   6     0   8     0   6
Latency             15088us   15053us   18784us   11317us    3377us   12653us
1.98,2.00a,ANDREW-PC,1,1731170067,63G,,8192,5,6,6,51776,6,22717,6,6,7,40308,4,8475,109,16,,,,,793,6,1765,7,1574,7,827,6,1945,8,1416,6,1445ms,17524us,9356us,1284ms,5950us,408ms,15088us,15053us,18784us,11317us,3377us,12653us
```

這組我不用看數字就知道有問題了，第一組大概跑個幾分鐘就結束了 (抱歉我沒有特別紀錄)，而第二組跑了兩個多小時...

這數字不大好判讀，全部貼到 ChatGPT o1 preview, 他幫我解讀如下:

--

您提供了兩份來自 Bonnie++ 的基準測試結果，以下我將對這兩份結果進行比較和分析，幫助您理解它們之間的差異以及可能的原因。

**概述**:
主機名稱：兩份結果均來自 ANDREW-PC
測試文件大小：都是 63GB

**第一份測試結果**
- 順序輸出 - 單字元：6 KB/s，CPU 使用率 6%
- 順序輸出 - 區塊：50.6 MB/s，CPU 使用率 6%
- 順序輸出 - 重寫：22.2 MB/s，CPU 使用率 6%
- 順序輸入 - 單字元：6 KB/s，CPU 使用率 7%
- 順序輸入 - 區塊：39.4 MB/s，CPU 使用率 4%
- 隨機搜尋：8,475 次/秒，CPU 使用率 109%

**第二份測試結果**
- 順序輸出 - 單字元：540 KB/s，CPU 使用率 99%
- 順序輸出 - 區塊：728 MB/s，CPU 使用率 100%
- 順序輸出 - 重寫：958 MB/s，CPU 使用率 91%
- 順序輸入 - 單字元：2,205 KB/s，CPU 使用率 99%
- 順序輸入 - 區塊：1.1 GB/s，CPU 使用率 58%
- 隨機搜尋：顯示為 “+++++”，表示性能極高

**比較分析**
1. 整體性能差異  
第一份結果顯示出相對較低的 I/O 性能，尤其是在單字元 I/O 操作中，速度極低。  
第二份結果顯示出異常高的 I/O 性能，傳輸速率達到數百 MB/s，甚至超過 1 GB/s。  

2. CPU 使用率  
第一份結果的 CPU 使用率普遍較低，除隨機搜尋外，大多在 4-7% 之間。  
第二份結果的 CPU 使用率極高，單字元和區塊操作中達到 91-100%。  

3. 單字元 I/O 性能  
第一份結果：6 KB/s，非常低，表示存在性能瓶頸或配置問題。  
第二份結果：540 KB/s（輸出）和 2,205 KB/s（輸入），有明顯提升，但 CPU 使用率也大幅增加。  

4. 區塊 I/O 性能  
第一份結果：輸出約 50.6 MB/s，輸入約 39.4 MB/s，屬於機械硬碟的正常範圍。  
第二份結果：輸出達到 728 MB/s，輸入達到 1.1 GB/s，遠超一般硬碟的性能。  

5. 隨機搜尋性能  
第一份結果：8,475 次/秒，CPU 使用率 109%。  
第二份結果：顯示為 “+++++”，表示性能極高或測試結果異常。  

6. 文件創建與刪除操作  
第一份結果：每秒操作數為 0，操作未成功。  
第二份結果：每秒操作數顯示為 “+++++”，表示操作速度極高。  

--


後面還有可能原因分析跟建議作法，我就不貼了，有興趣看整份完整的 report 解讀:
https://chatgpt.com/share/6730c417-e928-800d-8f5c-e00295bbe0a1

知道了架構上的差異，也知道了實際數字上的差異，怎麼配置就很清楚了。基本上看你最在意效能的環節是哪個，檔案放置的地方就配合它吧，方不方便使用的問題，再由其他工具層級的設定來解決就好。這後面再聊我的案例



# 3. 確認 WSL 能否存取 GPU 的運算能力

前陣子我為了在本機跑 LLM (我用 ollama)，專程去買了張有 16GB RAM, 規格最入門的 RTX 4060Ti ... 這張沒啥 CP 值，就是老黃專門切給我們這種只是要 "有" GPU 可以用來跑 AI 的人用的產品... 









---



1. AI 相關
	為了跑 ollama ( 雖然有 windows 版，但是相關資源少很多，往往都得自己除錯。很多錯誤都是低級錯誤，例如檔案路徑 / 跟 \ 的差別，shell script 跟 powershell 的差別，檔案系統特性的差別等等 )。為了跑 LLM 我換了張 4600Ti-16GB 的顯卡，在 windows 上面要裝 CUDA，裝 Python 等等環境，加上相容性問題等等，真是災難...

1. Docker with Heavy IO 相關
	於是我把念頭動到 docker 身上。上面那些問題如果能用 docker 不是就萬事太平了嗎? docker 是 linux 為基礎的機制，雖然有 windows container，不過連我是 MVP 我都在 2020 年左右棄用它了，改用純 linux docker .. 跑 AI 應用程式開發，當然免不了向量資料庫。在 docker 跑資料庫是一件很 xxxx 的事情，因為這樣我重新踩到 windows 環境 docker 的 IO 問題

1. Windows Desktop 的整合
	其實我都知道，現在 Server Side 都是以 Linux 為主流了，但是我主要工作環境是 Windows Desktop OS，我不響各種小事都要 ssh 到 linux 才能用啊，本機我還是希望能搞定大部分的事情，而且要簡單，不要做個小事也要啟動 VM blah blah ..., 光是一個 IDE, 我用 visual studio code, 以前嘗試過 code server, 用 browser 來當作工作環境，但是 ...

最後我決定用 WSL 為基礎，重新打造我的工作環境了。Microsoft 提供了一個高度整合 windows / linux 的環境: WSL ( Windows Subsystem for Linux ), 比起你直接跑一個 Linux VM 強太多了，

幾個主要要解決的問題:

- WSL: Ubuntu + Docker ( 不再用 Docker Desktop for Windows )
	- WSL
	- Ubuntu + Docker
- 解決跨 Linux / Windows 的 IO 問題
	- 在 WSL 內放 docker files / volumes 以提升效能

- 解決 Linux / Windows 的交互操作問題
	- NTFS 掛上 WSL 的資料夾
	- VSCODE remote ssh
	- 其他指令: WSL 啟動 vscode ( code . )
	- 其他指令: Windows 執行 Linux 指令 ( wsl ls -la )
	- 其他指令: WSL 執行 Windows ( explorer.exe . )


應用案例: 我的部落格 + GitHub Pages
- docker
- vscode remote shell exec


應用案例: Microsoft Kernel Memory ( using Qdrant )
- docker volume
- dotnet develop







後端的環境, Linux 早就是標準了, 不過我在 .com 年代就開始在用 windows server, 說實在話很多環境我還是對 windows 掌握比較熟悉一點。不熟的部分，靠著虛擬化，靠著 docker 的幫助，好像不用真的變成 "原生" linux 的使用者，繼續以 windows 當作 desktop 作業環境，日子也可以很開心的過下去...

不過，最近認真重新整理我的工作環境，也順勢換上了 Windows 11 24H2，迎來了 kernel 用 rust 改寫，以及第一版 copilot+ pc 的支援，我決定重新安裝 OS，而非用升級的方式 (我上一次重新安裝我的桌機，應該是六年前換電腦時的事了)


