---
layout: post
title: "關於我轉生成為 Linux 使用者的那件事"
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

結果竟然秒開.. 然後匯入資料的速度變正常了 (一秒可以跑 5 筆左右)，基本上就是卡在 embedding 的速度了。差了幾十倍的速度，這才正常的表現啊。經歷過這次，決定不撐了，趁著要升級 24H2 的契機，直接換掉我主要的工作環境，從 windows 為主變成 linux (wsl) 為主。


雖然工作環境很多，但是歸納一下其實也只有三種類型.. 我就各挑一個代表來展示就好:

1. 需要大量 IO 的 docker container - Qdrant
1. 需要整合環境 Visual Studio Code - 我的部落格撰寫環境 GitHub Pages
1. 需要 GPU 支援的 docker container - Ollama + OpenWeb-UI


# 2, 容器化的向量資料庫 - Qdrant

第一個就先來面對我最痛的 IO 效能問題 (因為根本慢到沒辦法跑啊..)。首先，到底有多慢? 我找個 Linux 下的 disk benchmark tools (我用無腦就能跑的 Bonnie++) 跑看看就知道了..

我測試的方式很簡單，就測兩組，一個是在 Linux 下測試原生的 ext4 file system ( 這是在虛擬化環境內，在 OS disk 下的 ext4.vhdx，理論上效能應該會略低於真正的 disk )。另一個則是測試 Linux 下，存取藉由 WSL2 掛進來的 windows ntfs file system ( drvfs, 掛載在 /mnt/c 這樣的路徑 )。

如果你在 windows 下執行 docker run, 然後還 -v 掛載了 c:\working-dir\ 的目錄，那就會踩到第二種情境了。通常你會高機率不知不覺地就踩到，因為大部分的範例都是這樣教你的 XDD

不囉嗦，直接來看 Bonnie 跑出來的結果..

## 2-1, WSL 磁碟效能 Benchmark

我用的設備是同一套，就我的桌機，規格跟組態如下:

```
CPU: AMD Ryzen9 3900X
RAM: DDR4 16GB x 4 = 64GB
SSD: Crucial T500 2TB PCIe Gen4 NVMe M.2 SSD
GPU: NVidia RTX 4060Ti - 16GB
OS: Microsoft Windows 11 Pro (24H2)
WSL Distro: Ubuntu 24.04 LTS
```

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

這組我不用看數字就知道有問題了，第一組大概跑個幾分鐘就結束了 (抱歉我沒有特別紀錄)，而第二組跑了兩個多小時... 這數字不大好判讀，全部貼到 ChatGPT o1 preview, 他幫我解讀如下:

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

實在無法想像，這些都是在同一台電腦，同一顆硬碟上面測出來的結果.. 只是換個存取路徑就有這種天差地遠的差別。知道這差異之後，我就知道該怎麼調整用法了...

## 2-2, 實際部署 Qdrant 測試資料庫

接下來，就拿我實際的測試案例出來吧。在之前聊 RAG 的文章: "______" 內，我用的是 Microsoft Kernel Memory 這個服務，封裝 file storage 以及 vector database, 整合幾種主流的 LLM 與 Embedding Model, 結合而成的 RAG 服務框架..

而這服務，背後的 vector database 是可以選擇的，我選用了最廣受好評的 Qdrant 這套。我自己一份測試資料，大約包含了 40000 筆資料，整個 DB 內涵的資料樣貌大致如下:

```

Dirs:	43782
Files:	282797
Bytes: 5.386GB

```

其實，還不需要動用到 benchmark, 光是看啟動時間就有差別了... 我直接拿 docker logs 來看，從第一筆啟動的 log timestamp, 直到看到 gRPC ready 的紀錄為止:

```
qdrant-1  | 2024-11-11T15:17:28.311248Z  INFO storage::content_manager::consensus::persistent: Loading raft state from ./storage/raft_state.json
qdrant-1  | 2024-11-11T15:17:28.399231Z  INFO storage::content_manager::toc: Loading collection: b2e-knowledge
qdrant-1  | 2024-11-11T15:17:34.362612Z  INFO collection::shards::local_shard: Recovering collection b2e-knowledge: 0/1 (0%)
qdrant-1  | 2024-11-11T15:17:34.597841Z  INFO collection::shards::local_shard: Recovered collection b2e-knowledge: 1/1 (100%)
qdrant-1  | 2024-11-11T15:17:34.601310Z  INFO storage::content_manager::toc: Loading collection: erp-shop-production
qdrant-1  | 2024-11-11T15:17:46.145280Z  INFO collection::shards::local_shard: Recovering collection erp-shop-production: 0/1 (0%)
qdrant-1  | 2024-11-11T15:17:46.318082Z  INFO collection::shards::local_shard: Recovered collection erp-shop-production: 1/1 (100%)
qdrant-1  | 2024-11-11T15:17:46.320745Z  INFO storage::content_manager::toc: Loading collection: erp-shop-qa
qdrant-1  | 2024-11-11T15:18:18.517880Z  INFO collection::shards::local_shard: Recovering collection erp-shop-qa: 0/1 (0%)
qdrant-1  | 2024-11-11T15:18:18.698370Z  INFO collection::shards::local_shard: Recovered collection erp-shop-qa: 1/1 (100%)
qdrant-1  | 2024-11-11T15:18:18.700815Z  INFO storage::content_manager::toc: Loading collection: pq-points-testcase
qdrant-1  | 2024-11-11T15:18:24.108431Z  INFO collection::shards::local_shard: Recovering collection pq-points-testcase: 0/1 (0%)
qdrant-1  | 2024-11-11T15:18:24.362571Z  INFO collection::shards::local_shard: Recovered collection pq-points-testcase: 1/1 (100%)
qdrant-1  | 2024-11-11T15:18:24.365352Z  INFO storage::content_manager::toc: Loading collection: pq-test-cases
qdrant-1  | 2024-11-11T15:18:30.282890Z  INFO collection::shards::local_shard: Recovering collection pq-test-cases: 0/1 (0%)
qdrant-1  | 2024-11-11T15:18:30.486071Z  INFO collection::shards::local_shard: Recovered collection pq-test-cases: 1/1 (100%)
qdrant-1  | 2024-11-11T15:18:30.488923Z  INFO storage::content_manager::toc: Loading collection: pq-testcase-documents
qdrant-1  | 2024-11-11T15:18:35.645220Z  INFO collection::shards::local_shard: Recovering collection pq-testcase-documents: 0/1 (0%)
qdrant-1  | 2024-11-11T15:18:35.929094Z  INFO collection::shards::local_shard: Recovered collection pq-testcase-documents: 1/1 (100%)
qdrant-1  | 2024-11-11T15:18:35.940218Z  INFO qdrant: Distributed mode disabled
qdrant-1  | 2024-11-11T15:18:35.941537Z  INFO qdrant: Telemetry reporting enabled, id: 26363849-cb35-46a3-a4d1-d822d5b036b2
qdrant-1  | 2024-11-11T15:18:35.951942Z  INFO qdrant::actix: TLS disabled for REST API
qdrant-1  | 2024-11-11T15:18:35.953860Z  INFO qdrant::actix: Qdrant HTTP listening on 6333
qdrant-1  | 2024-11-11T15:18:35.954027Z  INFO actix_server::builder: Starting 15 workers
qdrant-1  | 2024-11-11T15:18:35.954955Z  INFO actix_server::server: Actix runtime found; starting in Actix runtime
qdrant-1  | 2024-11-11T15:18:35.962011Z  INFO qdrant::tonic: Qdrant gRPC listening on 6334
qdrant-1  | 2024-11-11T15:18:35.962079Z  INFO qdrant::tonic: TLS disabled for gRPC API
```

第一組，是跑在 /mnt/c 底下的測試結果，啟動需要 67.563 sec .. (17:28.399 ~ 18:35.962)



```
qdrant-1  | 2024-11-11T15:15:41.384524Z  INFO storage::content_manager::toc: Loading collection: b2e-knowledge
qdrant-1  | 2024-11-11T15:15:41.659300Z  INFO collection::shards::local_shard: Recovering collection b2e-knowledge: 0/1 (0%)
qdrant-1  | 2024-11-11T15:15:41.753061Z  INFO collection::shards::local_shard: Recovered collection b2e-knowledge: 1/1 (100%)
qdrant-1  | 2024-11-11T15:15:41.755562Z  INFO storage::content_manager::toc: Loading collection: pq-points-testcase
qdrant-1  | 2024-11-11T15:15:41.954480Z  INFO collection::shards::local_shard: Recovering collection pq-points-testcase: 0/1 (0%)
qdrant-1  | 2024-11-11T15:15:42.039353Z  INFO collection::shards::local_shard: Recovered collection pq-points-testcase: 1/1 (100%)
qdrant-1  | 2024-11-11T15:15:42.040599Z  INFO storage::content_manager::toc: Loading collection: erp-shop-qa
qdrant-1  | 2024-11-11T15:15:42.762995Z  INFO collection::shards::local_shard: Recovering collection erp-shop-qa: 0/1 (0%)
qdrant-1  | 2024-11-11T15:15:42.834588Z  INFO collection::shards::local_shard: Recovered collection erp-shop-qa: 1/1 (100%)
qdrant-1  | 2024-11-11T15:15:42.835558Z  INFO storage::content_manager::toc: Loading collection: pq-testcase-documents
qdrant-1  | 2024-11-11T15:15:43.111973Z  INFO collection::shards::local_shard: Recovering collection pq-testcase-documents: 0/1 (0%)
qdrant-1  | 2024-11-11T15:15:43.199262Z  INFO collection::shards::local_shard: Recovered collection pq-testcase-documents: 1/1 (100%)
qdrant-1  | 2024-11-11T15:15:43.200216Z  INFO storage::content_manager::toc: Loading collection: pq-test-cases
qdrant-1  | 2024-11-11T15:15:43.406815Z  INFO collection::shards::local_shard: Recovering collection pq-test-cases: 0/1 (0%)
qdrant-1  | 2024-11-11T15:15:43.485705Z  INFO collection::shards::local_shard: Recovered collection pq-test-cases: 1/1 (100%)
qdrant-1  | 2024-11-11T15:15:43.487100Z  INFO storage::content_manager::toc: Loading collection: erp-shop-production
qdrant-1  | 2024-11-11T15:15:44.716729Z  INFO collection::shards::local_shard: Recovering collection erp-shop-production: 0/1 (0%)
qdrant-1  | 2024-11-11T15:15:44.793619Z  INFO collection::shards::local_shard: Recovered collection erp-shop-production: 1/1 (100%)
qdrant-1  | 2024-11-11T15:15:44.795503Z  INFO qdrant: Distributed mode disabled
qdrant-1  | 2024-11-11T15:15:44.795852Z  INFO qdrant: Telemetry reporting enabled, id: 744ae5dd-7970-4431-bdd0-b7a958f7c25d
qdrant-1  | 2024-11-11T15:15:44.799686Z  INFO qdrant::actix: TLS disabled for REST API
qdrant-1  | 2024-11-11T15:15:44.800206Z  INFO qdrant::actix: Qdrant HTTP listening on 6333
qdrant-1  | 2024-11-11T15:15:44.800226Z  INFO actix_server::builder: Starting 15 workers
qdrant-1  | 2024-11-11T15:15:44.800233Z  INFO actix_server::server: Actix runtime found; starting in Actix runtime
qdrant-1  | 2024-11-11T15:15:44.801323Z  INFO qdrant::tonic: Qdrant gRPC listening on 6334
qdrant-1  | 2024-11-11T15:15:44.801357Z  INFO qdrant::tonic: TLS disabled for gRPC API
```

第二組，換了個位置，我直在 vhdx 內 /opt/docker/ 下面測試，啟動只需要 3.417 sec .. (41.384 ~ 44.801)

同樣的，那麼明顯的差距 ( 啟動時間差了 20x, 差了 64 sec ) ，我就懶得再拿 benchmark 來測試 DB 效能了。基本上我自己在測試的時候，打 API 要 insert 一筆資料庫，就需要花掉 5 sec 的時間... 這段的重點在怎麼重新改變我的工作環境，不是在 tune performance ..

## 2-3, 在 windows 下掛載 wsl 的資料夾

解決方法其實也很簡單，換個目錄就搞定了。但是會踩這麼多次地雷，就是因為這樣用太方便了啊 (終究我是個以 windows desktop 為主要工作環境的使用者...)，打開檔案總管，能直接看到我的檔案是最方便的啊...

山不轉路轉，我就把檔案擺在對的地方，然後想辦法繼續照我習慣的方式 ( 在 windows 下，可以用正常的磁碟路徑存取他，也能用我習慣的工具去讀取檔案 ) 來存取檔案，問題就解決了。相對於 WSL 自動把 windows 下的 c:\ 掛載到 wsl 下的 /mnt/c 這樣的做法，我能不能反過來做一樣的事情，把 wsl 下的 /opt/docker 掛到 windows 下的 c:\codes\docker 呢?

其實還真的有，而且也不是新東西了。大概在 windows 2000 那個年代的 ntfs 就開始支援的 reparse points 機制。中間還冒出很多讓人搞不清楚分別的東西 (例如 junction points)，使用的指令也是，有 mklink, 也有 mountvol ...

https://learn.microsoft.com/zh-tw/windows-server/administration/windows-commands/mklink


我用的是 mklink, wsl 的檔案系統可以透過 \\wsl$\ubuntu\.... 來存取 ( ubuntu 是 distro name )，所以你只需要把 \\wsl$\ubuntu\opt\docker -> c:\codes\docker 就好了

指令很簡單: 

```
mklink /d \\wsl$\ubuntu\opt\docker c:\codes\docker
```

這麼一來，你不論用檔案總管，或是 vscode，只要照原本的習慣操作就好了。唯一需要留意的是記得備份。因為它終究是個連結，實際檔案是存在 ext4.vhdx 虛擬硬碟內的。這 vhdx 檔案結構損毀的話，你的檔案就消失了.. 

不過，撇開這些不談，這倒不失為一個好方法，既維持了我原本工作的習慣與方便性，也解決了硬碟效能問題 (你要買多高級的 SSD 才能有 20x 的效能提升? )




# 3, GitHub Pages with Visual Studio Code

透過 mklink, 在 windows 掛載 wsl 的工作環境，雖然解決了使用習慣問題，但是終究是把效能問題換邊放而已啊，跨越 OS 的存取效能終究不好。我只是把效能好的部分保留給 linux 端 ( wsl ) 而已。如果我在 windows 端有別的工具要處理檔案，還是會踩到效能糟的那個環節。


前面的案例是 container 跑 database, 大量的 io 都是發生在 runtime, 因此把檔案丟到 wsl 為主的環境很正常，在 windows 端的操作大概就編輯 dockerfile, docker-compose.yaml 這類操作而已，慢一點不會有感。

但是如果情境是 IDE, 我要面對的是 source code 編輯, 有大量的 css / html / 圖檔等等，IDE 運作會高頻次的存取這些檔案，而 code 在 build 或是 git pull / push / commit 也都會有大量小檔案的存取操作，這時狀況就反過來了。更糟的情況是: 開發編譯需要大量 I/O, 執行也需要大量 I/O, 那你該怎麼辦?

這問題就更硬了，只是把檔案挑地方放已經不夠了，你的 IDE, git, build tool, runtime, container 等等都應該在同一個體系內才能解決... 這就回到這段的主題: 跨系統 (跨 OS Kernel) 的互通性了。

不得不誇一下 Microsoft, WSL 在這部份真的是做得沒話講，整合的程度我都覺得是外星黑科技了。就算是我也花了點功夫，才搞清楚 Microsoft 在背後做了哪些事情...

首先, 前面提到 Microsoft 在 WSL 已經把 file system 打通了。windows -> wsl 有 drvfs, 可以在 wsl 內 mount windows file system, 而 wsl -> windows 也支援 9p protocol, windows 內可以用 \\wsl$\ubuntu\ 來存取

接下來是 UI, 某一版 windows 開始支援 WSLg, 意思是你可以把 Linux 的 UI 顯示到 Windows 上，就是 Xwindows 那套機制，可以運用到 GPU 資源。這背後其實打通了 device 這層 (後面會再度聊到 GPU，我這邊先點到為止)，UI 操作面也打通了。 (不過最終這個我覺得不大實用，我用不到)

第三個是 command 的整合。這個真的是黑科技，我示範幾個情境:

在 wsl 下 ( bash )，我可以啟動 dos prompt:

```
andrew@113N000081:~$ cmd.exe /c dir a*
'\\wsl.localhost\Ubuntu\home\andrew'
CMD.EXE was started with the above path as the current directory.
UNC paths are not supported.  Defaulting to Windows directory.
 Volume in drive C is Windows
 Volume Serial Number is 6A76-E5CC

 Directory of C:\Windows

10/07/2024  02:05 PM    <DIR>          appcompat
10/30/2024  12:00 PM    <DIR>          apppatch
11/07/2024  11:20 AM    <DIR>          AppReadiness
10/08/2024  10:26 AM    <DIR>          assembly
               0 File(s)              0 bytes
               4 Dir(s)  262,307,336,192 bytes free
andrew@113N000081:~$
```

看起來頂多只是像 ssh 那樣的感覺，好像沒有那麼了不起... 我再示範另一個 case, 直接在 wsl 下叫出檔案總管，並且開到目前 (wsl) 的工作目錄:

```
andrew@113N000081:~$ explorer.exe .
```

開出來的檔案總管，作用中的路徑是這個

```
\\wsl.localhost\Ubuntu\home\andrew
```

這個就神奇了，開起來就是個貨真價實的 windows 版檔案總管 ( file explorer ), UI 也是 windows 原生的, Process 也是 windows 的。這黑科技怎麼做到的其實很有趣，Microsoft 動了點手腳，讓 linux 認得 PE 格式的擋頭，然後重新導向這個啟動的動作.. 細節我就不多說，有興趣可以看這篇文章:

// linux + windows pe

如果這樣就嚇到你，那我再加碼一個:  這次我在 wsl 叫出 vscode, 然後這個 vscode 除了 UI 看起來都是 windows 原生地之外，其他看起來都像是 linux 的... 在這個 vscode 開啟檔案, 是 wsl 的 file system 結構；執行檔案 ( run / debug ) 都是跑 linux 版本的程式碼... 開起來的 terminal, 是 linux 的 shell ... 執行的 vscode extension, 都是 linux 下的 extension ( 這不是全部 ) ...

沒錯，這已經不是 file system 整合，或是遠端呼叫那麼簡單了。這有兩個層級:

1. 透過 wsl 啟動 windows 的 process (並且傳遞 environment 相關資訊)
1. Visual Studio Code 其實有特別的設計: Remote Shell, 拆成 UI 跟 Code Server .. UI 在 windows 端執行，Code Server 在 Linux 端執行，中間靠 ssh 通訊..
1. Visual Studio Code 準備了一組 shell script, 試圖欺騙你.. 其實你執行的 code 是 shell script, 背後做了一連串準備動作，最後才會去呼叫 code.exe 才是真正的啟用 windows 版本的 vscode ..

// 貼 vscode remote shell 架構圖
https://code.visualstudio.com/docs/remote/ssh

到這裡，這真的是我認為的終極解法了。UI 完全就是 windows 的影子，但是骨子裡完全就是 linux 的東西... 彷彿就是 windows 的 kernel 完全替換成 linux 一樣...


這真的解掉我一個大難題，就是我的部落格撰寫環境。

還記得我 X 年前寫的這篇嗎? Blog as Code!, 我老早就用 vscode 在寫部落格了。我的標準環境就是 GitHub Pages, 我整個部落格就放在 GitHub 上..

1. 要寫部落格, 就把 git repo 拉下來就可以開始編輯了
1. 要發布內容, 就 git commit / git push 推回 github, 內建的 ci / cd 機制就會把我的部落格 build 成靜態檔案發佈出去了 ( github pages, jekyll )

我在本機，需要處理部落格上萬個檔案, 因此 vscode 要開起來不是件輕鬆的事情 (左側的 tree 要載入的項目不少)。不過本機環境，這樣的 loading 對我的電腦還不成問題

不過預覽是很痛苦的一件事啊。我如果 push 上 github 要等三分鐘才看的到結果 (就算只改一個字也一樣)..

於是我嘗試過，裝 windows 版本的 jekyll, 相依 ruby, 我直接放棄...

接著我跑 docker 版本的 jekyll, 碰到 file system 的問題。windows 的 file system 掛載到 docker volume, 檔案異動的 event 過不去，只能用 pooling，效能已經夠糟了還雪上加霜... 改一個字要花 80 sec 才能 build 完...

後來我用了折衷方案, 就前面 file system 的互通作法，改善了 github pages 的效能，就得犧牲 vscode 的效能，無法兼顧。有一段時間我是真的放兩份檔案，要預覽的時候就用 robocopy.exe 同步 ( windows 下類似 rsync 的工具)。同步大約花 30s, build website 大約花 10s, 雖不滿意但是已經好很多了...

最後，我用了 vscode + remote shell ... 完全不需要同步, jekyll watch 也運作正常。我只要 vscode 按下儲存, jekyll 馬上自動 build website, 5s 完成..., 而且這一切都在 vscode 內完成 ( 我直接開一個 vscode terminal 跑 github pages 的 docker container ...)

多追加一個，因為 code server 也能監控網路，所以我跑的 docker container 發佈了那些 tcp port 他也知道了，vscode 還會直接提是我要不要開 localhost:4000 來預覽我的網站?

我選擇了直接在 vscode 內預覽，畫面就是你看到的這個樣子:

// 貼圖, vscode 寫 blog + preview

看到這邊，我沒有遺憾了 XDD
所有開發環境的問題都解決了，整合度高，效率好，都能用 linux 原生環境，容器化，一行指令就跑起來，不用裝一大堆套件 (就搞定 vscode + docker 就夠了)

所以，我在部落格 root 擺了一個 docker-compose.yaml, 以後只要 git clone, code ., 開 terminal 跑 docker compose up, 開 http://localhost:4000 就可以開始寫部落格了..


我的案例剛好沒示範到 build code, 如果你不是寫部落格而是寫 code, 在 terminal 下直接跑 dotnet run 就可以在 wsl 跑你的 c# code 了，用法完全一樣，你不需要在 windows 測試完，在打包成 docker image 丟到 linux 再測一次。你可以很容易地從一開始開發，測試就通通都再以後要執行的 linux 環境下運行。



# 4, Ollama with CUDA support

終於來到最後一個，跑 LLM 需要用到 GPU , 需要相依 Python 套件, 也要相依很難搞的 CUDA ... ( CUDA 版本相容性很糟，裝錯版本可能就跑不起來了 )


結果，這個問題真的是我庸人自擾，想太多了。Microsoft 早就幫我解決掉了... 在搞清楚黑科技怎麼做的之前，先來體驗一下效果。我直接看 ollama 的 docker hub 上的說明，他把步驟整理的很精簡:

https://hub.docker.com/r/ollama/ollama

摘要步驟，大致是這樣:

1. windows 上面要裝 NVIDIA GPU driver (版本夠新就可以，沒有特別的軟體要安裝或設定)
2. wsl 安裝 NVIDIA container toolkit, 注意 wsl 不需要再裝 GPU driver 了..
3. wsl 設定 docker runtime 要正確使用 nvidia-ctk

其實, 第一步做完, wsl 本身就已經支援 GPU 了，後面的動作都是為了 docker 內可以使用 GPU 而準備的。

你可以下這指令: nvidia-smi 就看的到顯卡的資訊了:

```
qauser1@TPE-AI-PC:~$ nvidia-smi
Tue Nov 12 17:37:25 2024
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 550.40.06              Driver Version: 551.31         CUDA Version: 12.4     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4080 ...    On  |   00000000:01:00.0  On |                  N/A |
|  0%   30C    P8             11W /  320W |     726MiB /  16376MiB |      3%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A        33      G   /Xwayland                                   N/A      |
+-----------------------------------------------------------------------------------------+
```


之後就可以快樂的讓你的 container 能直接使用到 GPU 運算資源了。你只需要在 docker run 啟動 container 時追加這參數 --gpus=all，指派可用的 GPU 給他就可以了。

例如:

docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

試跑了一下 llama3.2, 問了幾個問題, 回應速度還挺快的, 比正常人說話的速度快多了:





對應 windows 的 task manager, 果然看的到 GPU 有 loading :




執行過程中，再次看一下 nvidia-smi 也一樣看的到有成試在使用 GPU:



大功告成! 看來我也可以無痛的在 wsl 下面執行需要 CUDA 的應用程式了


# 5, 心得





因為工作環境重整之後，實在太好用，我決定把主要工作環境都轉移到 wsl 上了，用的就是上面示範的幾種應用方式。

也因為這樣，投資了 GPU ( RTX 4060TI-16G ), 也添購了顆 2TB Gen4 SSD ..
