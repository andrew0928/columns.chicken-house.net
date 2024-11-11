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

結果竟然秒開.. 然後匯入資料的速度變正常了 (一秒可以跑 5 筆左右)，基本上就是卡在 embedding 的速度了。差了幾十倍的速度，這才正常的表現啊。經歷過這次，決定不撐了，趁著要升級 24H2 的契機，直接換掉我主要的工作環境，從 windows 為主變成 linux (wsl) 為主。


雖然工作環境很多，但是歸納一下其實也只有三種類型.. 我就各挑一個代表來展示就好:

1. 需要大量 IO 的 docker container - Microsoft Kernel Memory
1. 需要 GPU 支援的 docker container - Ollama + OpenWeb-UI
1. 需要整合環境 Visual Studio Code - 我的部落格撰寫環境 GitHub Pages


# 2, Microsoft Kernel Memory

第一個就先來面對我最痛的 IO 效能問題 (因為根本慢到沒辦法跑啊..)。首先，到底有多慢? 我找個 Linux 下的 disk benchmark tools (我用無腦就能跑的 Bonnie++) 跑看看就知道了..

我測試的方式很簡單，就測兩組，一個是在 Linux 下測試原生的 ext4 file system ( 這是在虛擬化環境內，在 OS disk 下的 ext4.vhdx，理論上效能應該會略低於真正的 disk )。另一個則是測試 Linux 下，存取藉由 WSL2 掛進來的 windows ntfs file system ( drvfs, 掛載在 /mnt/c 這樣的路徑 )。

如果你在 windows 下執行 docker run, 然後還 -v 掛載了 c:\working-dir\ 的目錄，那就會踩到第二種情境了。通常你會高機率不知不覺地就踩到，因為大部分的範例都是這樣教你的 XDD

不囉嗦，直接來看 Bonnie 跑出來的結果..

## 2-1, WSL 磁碟效能測試

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

## 2-2, 實際部署 Kernel Memory Service 測試

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

解決方法其實也很簡單，換個目錄就搞定了。但是會踩這麼多次地雷，就是因為這樣用太方便了啊 (終究我是個以 windows desktop 為主要工作環境的使用者...)，打開檔案總管，能直接看到我的檔案是最方便的啊...

山不轉路轉，我就把檔案擺在對的地方，然後想辦法繼續照我習慣的方式 ( 在 windows 下，可以用正常的磁碟路徑存取他，也能用我習慣的工具去讀取檔案 ) 來存取檔案，問題就解決了。相對於 WSL 自動把 windows 下的 c:\ 掛載到 wsl 下的 /mnt/c 這樣的做法，我能不能反過來做一樣的事情，把 wsl 下的 /opt/docker 掛到 windows 下的 c:\codes\docker 呢?

其實還真的有，而且也不是新東西了。大概在 windows 2000 那個年代的 ntfs 就開始支援的 reparse points 機制。中間還冒出很多讓人搞不清楚分別的東西 (例如 junction points)，使用的指令也是，有 mklink, 也有 mountvol ...

我用的是 mklink, wsl 的檔案系統可以透過 \\wsl$\ubuntu\.... 來存取 ( ubuntu 是 distro name )，所以你只需要把 \\wsl$\ubuntu\opt\docker -> c:\codes\docker 就好了

指令很簡單: 

```
mklink /d \\wsl$\ubuntu\opt\docker c:\codes\docker
```

這麼一來，你不論用檔案總管，或是 vscode，只要照原本的習慣操作就好了。唯一需要留意的是記得備份。因為它終究是個連結，實際檔案是存在 ext4.vhdx 虛擬硬碟內的。這 vhdx 檔案結構損毀的話，你的檔案就消失了.. 

不過，撇開這些不談，這倒不失為一個好方法，既維持了我原本工作的習慣與方便性，也解決了硬碟效能問題 (你要買多高級的 SSD 才能有 20x 的效能提升? )




# 3, GitHub Pages with Visual Studio Code

透過 mklink, 在 windows 掛載 wsl 的工作環境，雖然解決了使用習慣問題，但是終究是把效能問題換邊放而已啊，跨越 OS 的存取效能終究不好。我只是把效能好的部分保留給 linux 端 ( wsl ) 而已。如果我在 windows 端有別的工具要處理檔案，還是會踩到效能糟的那個環節。

最常碰到的是 IDE，例如 Visual Studio, 或是 VS code, 以及常用的 dotnet build, 或是 git 等等，都是需要大量操作檔案的工具。這時兩邊不能兼顧也是很麻煩...

同時，跨 OS，跨 File System，使用上除了效能之外，很多細微的地方也是有差別的，像是 file change event 會失效, 部分 file system 的特色也會因為轉換而遺失，例如沒多少人聽過的 NTFS stream... 

因此，我開始想是否有辦法連 CLI / GUI 的工具都在 Linux 端執行，只有操作跟顯示保留在 Windows 端? 本來我想的方式原始了點，想說 wslg 已經支援 linux 的 gui 整合了，可以把 x-window 的 display 設到 windows 來，結果我想太多了，原來 Microsoft 早就替我搞定了...

有兩個關鍵的技術:

1. wsl 支援在 linux 環境下執行 windows pe 格式的執行檔 (所以我可以在 linux 下叫出 vscode)
1. vscode 支援 remote shell, 我可以在 windows 下操作 vscode, 但是 vscode 背後會連結 vscode-server, 在 linux 下用原生的工具 ( dotnet, git, shell ) 來做事..

有點玄? 直接看這番操作, 你會覺得好像在變魔術一樣，一時之間不知道背後發生了什麼事情... (我也是看半天價構說明才搞懂的)




# 4, Ollama with CUDA support

接著下一個問題: 我在 windows 下面跑 AI 的應用，光是處理 Python 環境，搞定 CUDA 的套件跟環境，就已經快抓狂了... 工作環境問題，我希望能用 docker 這樣虛擬化的方式幫我搞定，我不需要在我真正工作環境夏裝那麼多相依性的套件，只要 docker pull 正確的 image 回來就能用..

軟體安裝倒是簡單，docker 已經很成熟了。問題在於 GPU 的支援。不過，我後來才發現，這點我白擔心了...，Microsoft 早在幾年前就搞定了，WSL 原生支援 GPU support ...

我查了我主要的應用: ollama, 發現 ollama 官網的安裝說明直接教你怎麼搞定 wsl 的 nvidia gpu support 了...

https://hub.docker.com/r/ollama/ollama

沒想到這是最容易的，基本上照做就完成了。懶得看指令的，我總結一下好處:

1. windows 環境什麼都不用裝，只要安裝夠新的 nvidia gpu driver 就夠了
1. wsl 不需要裝 gpu driver, 只要裝 nvidia container toolkit 就好了
1. 其他只要正確的使用 docker image, 在啟動 container 時 docker run 記得加上  --gpus=all 這參數就夠了，docker 會把所有的 GPU 都分配給 container 使用..

你可以用 nvidia-smi 這指令查看 GPU 的狀況:


我就真的跑個 LLM 吧，來試試 llama3.2:






回答的速度挺快的，一秒大概 10+ tokens, 比正常講話速度還快。看了一下 windows task manager, 果然 loading 是在 GPU 身上無誤
















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


