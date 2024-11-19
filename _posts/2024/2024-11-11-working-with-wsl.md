---
layout: post
title: "關於我轉生成為 Linux  開發者的那件事"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: /wp-content/images/2024-11-11-working-with-wsl/logo.jpg
---

![](/wp-content/images/2024-11-11-working-with-wsl/logo.jpg)
> 圖: DALL-E, 我讓 ChatGPT 搜尋我自己然後畫出來的形象圖..

因為越來越多東西需要在原生的 linux 環境下執行, 趁著要更新 24H2 要重灌系統的機會, 就一起認真的重整我的開發環境了。在 windows 下要以 linux 為主要的工作環境，用 wsl (windows subsystem for linux) 是首選。也因為這次改便環境，研究作法的同時也惡補了一下 wsl 的相關背景知識，這才發現 Microsoft 對 WSL 下了不少功夫啊，背後藏了很多不錯的巧思，正好用這篇整理一下心得。

後面我會交代我的作法，以及我理解的背後架構與限制。不管原理，其實我最想解決的問題 (也是我的動機) 是這幾個:

1. 拋開 docker desktop for windows, 改成直接在 linux 下執行 docker 就好了
1. 在 windows 下執行 docker, 掛載 volumes 的 IO 效能很糟糕 (糟到用不下去)
1. 我想在 docker 下執行 CUDA 相關的 AI 應用
1. 我想建立一個 linux 為主, 能長期使用的通用工作環境，並且能無縫的跟我慣用的 windows 環境整合在一起。常用的工具就那些，包含 visual studio code, git, dotnet 等


總算，灌好 windows 11 pro 24h2 的這個禮拜，我總算把我的工作環境打造好了。過程中也發現不少 WSL 的冷知識，也挖出了不少 Microsoft 藏在裡面的黑科技。經過這次下定決心要重新轉移工作環境，而這幾年相關的整合也都成熟了 (其實不是新東西，可能用的兇的人早就在用了，我其實是慢半拍)，我就野人獻曝，分享一下我的整理心得。

<!--more-->





# 1. 換工作環境的動機

動機前面帶過了，不過更具體地來說，推動我決定這樣做的最後一根稻草，是 AI 相關的應用。年中的時候，為了跑本地端的 LLM (我當時只有 CPU: AMD 3900X 跟 GPU: AMD RX570 而已)，算力完全不夠啊，買了張 NVIDIA RTX4060Ti 16GB，結果發現要搞定 CUDA 那堆環境還真惱人...

查了一下，難道就不能像 docker 那樣一堆相依的環境都裝在 docker 裡面就好嗎? 還真的有，而且大部分科學運算的應用也都是以 Linux 為主，在 Windows 下要搞定 CUDA，還要搞定 Python，還真是件煩死人的任務。

於是，一路就從 docker, 從 GPU, 連帶的解決 docker / wsl 存取 windows file system 很離譜的 IO 效能問題, 到整個 visual studio code 的環境完全搬移到 linux ( 對，連你開出 vscode terminal, 都直接是 bash, 不是 powershell ..., 檔案的路徑都是 rootfs, 不是 windows ntfs..)

而 IO 問題，我有兩個案例，一個是跑向量資料庫 Qdrant, 才塞了四萬筆資料，結果整個 container 啟動竟然需要一分鐘? (換了 Gen4 SSD 後有改善，"只要" 不到 40 sec ... )，另外我自己的部落格，要用 Jekyll 的 container 預覽，竟然也要跑 110 sec ... 這實在不是個能接受的工作環境..

我心裡想這是什麼狀況? 我的桌機雖然是五年前的設備，但是也沒這麼不堪吧? 我列一下我的配備:

```
CPU: AMD Ryzen9 3900X (12 cores, 24 threads)
RAM: DDR4 16GB x 4 ( 64GB )
SSD: Samsung 970Pro 512GB (MLC), PCIE 3.0, NVME
OS: Microsoft Windows 11 Pro ( 當時跑的是 23H2 )
```

我想起我多年前踩過的地雷 ( 2018 的文章: [使用 LCOW 掛載 Volume 的效能陷阱](/2018/07/28/labs-lcow-volume/) )，也碰過類似的狀況，這次我趁著有乾淨環境的狀況下，好好的測試一次，也重新調整過磁碟的使用方式，算是徹底解決掉了，這是第一個成果，我只要些微的改變磁碟目錄的安置方式，問題就搞定了。啟動 Qdrant 的時間只需要原本的 1/25, 部落格文章預覽需要的建置時間只要原本的 1/18 ...

這麼戲劇化的改善，一定是原本的架構有問題 XDD，不然你要花多少錢才買的到 25 倍快的 SSD?

細節後面會交代，我整理了一下，我把我所有問題歸納成這三種類型.. 每種題型我就各挑一個代表來展示就好:

1. 需要大量 IO 的 docker container - 示範案例: Qdrant
1. 需要整合環境 Visual Studio Code - 示範案例: 我的部落格撰寫環境 GitHub Pages
1. 需要 GPU 支援的 docker container - 示範案例: AI 模型推論的基本環境, Ollama + OpenWeb-UI

最後，也因為這些調整跟研究，我也更清楚知道我未來的工作環境需要什麼了，就趁這次機會做個小幅的升級，小規模的敗家，升級了部分配備，現在，我的桌機的配備是:

```
CPU: AMD Ryzen9 3900X (沒變)
RAM: DDR4 16GB x 4 = 64GB (沒變)
WSL Distro: Ubuntu 24.04 LTS (重新建立)

SSD: Crucial T500 2TB PCIe Gen4 NVMe M.2 SSD (升級了容量跟速度)
GPU: NVidia RTX 4060Ti - 16GB (添購了 GPU)
OS: Microsoft Windows 11 Pro (24H2, 趁機重灌, 重建環境)
```


# 2, 案例: 容器化的向量資料庫 - Qdrant

第一個就先來面對我最痛的 Docker IO 效能問題，當時我心裡想，這題要是無解，我就直接放棄了 XDD。以前我認為這無解，就乾脆不在本機跑這些服務了 (我直接丟到 NAS / Cloud 用原生的 Linux 來跑，眼不見為淨)。首先，為了弄清楚在 Windows 上面跑 Docker 的 IO 到底有多慢? 我找了同時有 windows / linux 版本的 disk benchmark 工具: [fio](https://fio.readthedocs.io/en/latest/fio_doc.html) 來測試。


我測試的方式很簡單，有兩組要被測試的資料夾，分別在 windows 下的 NTFS, 以及在 wsl (linux) 下的 ext4 ... 以這兩個磁碟空間為測試標的，個別測試從 windows 以及從 wsl 去存取這資料夾，看看這四種組合跑出來的 disk i/o benchmark 分數..

在這邊先科普一下 WSL 的 file system 架構... 看底下這張圖:

![](/wp-content/images/2024-11-11-working-with-wsl/image.png)
> https://www.polarsparc.com/xhtml/IntroToWSL2.html


基本上存取路徑大致可以這樣分，應用程式都是在黃色的 user space 執行的 ( 有 windows / wsl 兩個 )，而 file system 也都是跟著 kernel 的 ( 一樣有 windows: NTFS, 也有 wsl: ext4 ), 而我用預設的 wsl, disk 多一層虛擬化 (對應到 NTFS 上的檔案: ext4.vhdx )

因此，我列出所有的 4 種組合情境:

1. 由 windows app 存取 windows file system:  
NTFS, c:\benchmark_temp, 最直接的存取路徑, 完全沒有額外消耗的理想情境, 大部分單純的 windows 應用都是這類。
1. 由 windows app 存取 wsl file system:  
EXT4, \\wsl$\ubuntu\home\andrew\benchmark_temp, 中間跨越 9p protocol 進到 linux kernel, 而 linux 要存取 disk 還得經過一層 hyper-v 虛擬化的機制 (存取放在 NTFS 上的 .vhdx, 多一層虛擬化轉換)
1. 由 wsl application 存取 wsl file system:  
EXT4, ~/benchmark_temp, 基本上軟體也是直接的路徑, 只是 wsl 終究是 VM, 終究需要透過 hyper-v 虛擬化機制存取 .vhdx
1. 由 wsl application 存取 windows file system:  
NTFS, /mnt/c/benchmark_temp, 中間經過一層 drvfs (檔案系統對應，同時包含 9p protocol) 的轉換..


如果你在 windows 下執行 docker, 然後在 docker run ......  -v 掛載了 c:\working-dir\ 的目錄，那就會踩到第四種情境了，磁碟效能會被扒一層皮 ( drvfs )。WSL 的前生 LCOW ，就我前面提到，2018 那篇文章，也是踩到第四種情境。你會發現效能掉的很離譜，就是這種狀況。

在 Linux 環境下的 container 必須透過 drvfs 掛載 c:\working-dir 才能讓 container 存取，這層轉換損失了效能，也遺失了部分 file system 的特性 (例如 file change event)。你如果只是照各種範例教學，就在 windows 下使用 docker 的話，高機率就踩到這情境 (而且通常是不知不覺)... 實測之後，我才發現較能差距有這麼大，以前真的白花了很多冤枉時間在電腦前面發呆...  

不囉嗦，直接來看跑分的結果.. 這四種組合我都跑一次 disk benchmark 來比較看看差異...。



## 2-1, WSL 磁碟效能 Benchmark

我用的設備是同一套，就我的桌機，不過測試的當下，我已經小幅度升級軟硬體了，升級後的規格跟組態如下:

```
CPU: AMD Ryzen9 3900X
RAM: DDR4 16GB x 4 = 64GB
WSL Distro: Ubuntu 24.04 LTS

(以下有升級過了)
SSD: Crucial T500 2TB PCIe Gen4 NVMe M.2 SSD
GPU: NVidia RTX 4060Ti - 16GB
OS: Microsoft Windows 11 Pro (24H2)
```

我用的 disk benchmark 測試工具是 fio, 安裝很容易, 在 wsl 下只要一行指令就能安裝:

```
sudo apt-get install fio
```

在 windows 下也差不多:

```
winget install --id fio.fio
```


我測試的參數統一如下 (除了不同環境，會換掉 path, 也會換掉 io engine 之外, 其餘都相同)，測試的都是同一顆硬碟:

```
fio  --name=benchmark \
      --directory=//wsl$/ubuntu/home/andrew/benchmark_temp \
      --size=16G \
      --rw=randrw \
      --bs=4k \
      --numjobs=8 \
      --iodepth=64 \
      --ioengine=windowsaio \
      --direct=1 \
      --time_based \
      --runtime=300
```


測試檔案大小 16GB, 隨機讀寫, 4k block, 8 concurrent processes, disable cache, 測試 300 sec


四組測試的結果，我直接都貼給 ChatGPT 幫我彙整了，我就不另外整理數據了，請看分析報告:

以下是最終版本的數據表格以及測試數據的解讀：


---

### 數據表格 (via ChatGPT)

| 測試環境        | 檔案系統  | READ (MiB/s) | READ IO (GiB) | WRITE (MiB/s) | WRITE IO (GiB) | 測試時長 (秒) |
|----------------|---------------|-------------------|------------------|--------------------|-------------------|---------------|
| Windows    | Windows       | 576               | 169              | 576                | 169               | 300           |
| WSL            | WSL           | 209               | 61.2             | 209                | 61.2              | 300           |
| Windows    | WSL           | 16.5              | 4.951            | 16.5               | 4.958             | 300           |
| WSL            | Windows       | 37.5              | 11.0             | 37.6               | 11.0              | 300           |

---

### 測試數據的解讀 (via ChatGPT)

**1. Windows → Windows（測試編號 1）**
- **結果：高性能**  
  - 帶寬達到 576 MiB/s，總 IO 169 GiB。
  - 此結果完全符合 PCIe 4.0 NVMe SSD 的隨機 4K 性能範疇，表現正常。
- **解讀：**  
  - Windows 原生檔案系統（NTFS）的優化和直接 I/O 訪問使性能接近硬體極限。
  - 測試中的多工作線程和高 I/O 深度設置沒有明顯的瓶頸。

**2. WSL → WSL（測試編號 2）**
- **結果：中等性能**  
  - 帶寬 209 MiB/s，總 IO 61.2 GiB。
  - 性能約為 Windows → Windows 的 36%，存在虛擬化損耗。
- **解讀：**  
  - WSL2 虛擬環境中的 EXT4 模擬檔案系統性能相較於 Windows 原生檔案系統略有降低。
  - 虛擬化層和多線程高併發的開銷影響了性能。

**3. Windows → WSL（測試編號 3）**
- **結果：低性能**  
  - 帶寬僅 16.5 MiB/s，總 IO 約 4.951 GiB。
  - 性能明顯低於預期。
- **解讀：**  
  - Windows 透過 9P 協定存取 WSL 的 EXT4 檔案系統，導致高延遲。
  - NTFS 和 EXT4 之間的檔案格式轉換以及協定處理的低效率是主要瓶頸。
  - 此測試結果在跨系統操作中屬於合理範圍，但對於高性能應用場景不具代表性。

**4. WSL → Windows（測試編號 4）**
- **結果：低性能**  
  - 帶寬 37.5 MiB/s，總 IO 11 GiB。
  - 性能略優於 Windows → WSL，但仍顯著低於其他情境。
- **解讀：**  
  - 類似於測試編號 3，WSL 存取 Windows 的 NTFS 檔案系統同樣依賴 9P 協定。
  - 虛擬化層、協定延遲以及 I/O 格式轉換造成了性能瓶頸。

---

### 數據的關鍵洞察 (via ChatGPT)

1. **Windows 原生操作系統表現最佳**  
   - Windows 原生存取 Windows 檔案系統（NTFS）能發揮 SSD 性能的最大潛力。

2. **WSL 中的虛擬化開銷明顯**  
   - WSL → WSL 性能較佳，但仍有顯著虛擬化損耗。
   - EXT4 模擬和虛擬化層影響性能，但結果在合理範圍內。

3. **跨系統檔案系統操作存在嚴重性能損耗**  
   - Windows ↔ WSL 的存取受制於 9P 檔案系統協定，導致性能顯著下降。
   - 此類操作不適合高性能需求場景，應避免頻繁使用。

4. **測試設置合理，數據整體可信**  
   - 測試參數（隨機讀寫、4K 區塊、多工作線程）模擬了真實的高負載場景。
   - 結果反映了不同檔案系統與操作環境的性能差異。


---




別的不看，光是看 4k random access 存取同一顆 SSD, 最好跟最差就有 576MB/s 跟 16.5 MB/s 的差別，足足 35x 的差距... (我用 HDD 跟 SSD 也沒差這麼多啊)。實在無法想像，這些都是在同一台電腦，同一顆硬碟上面測出來的結果.. 。還好我有做過這測試，知道這差異之後，我就知道該怎麼調整用法了...


## 2-2, 測試數據的解讀, 與 WSL 架構

繼續往下看怎麼調整環境前，我先把 benchmark 這段作個結尾吧。雖說對這結果 (分數) 有點意外，因為落差實在太大，但是對照架構圖來看，其實都解釋的通。我就用架構圖來說明這測試背後發生什麼事，結束這段落吧。

首先，我特地引用了張我平常根本不會看的網站資訊 XDDD

![](/wp-content/images/2024-11-11-working-with-wsl/image-1.png)
> https://ascii.jp/elem/000/004/026/4026714/

我在 Microsoft 官網找了半天，都沒有找到合適的架構圖來講我講說的主題，結果意外的翻到這張圖，講得最到位；看了一下內容，也完全是我要講的題目啊啊啊 (難怪圖那麼搭)。我就破例用這篇日文的技術文章來說明吧

首先，WSL2 就是用 VM 來執行完整的 Linux Kernel, 外加 Microsoft 替 WSL 做的各種整合，來讓 Windows / Linux 兩組 Kernel 能夠盡量無縫的整合再一起的架構，其中第一個就是 file system 的整合。

圖的左側 (橘色)，就是正常的 win32 環境, 直接透過 windows driver 存取 disk, 通常都是用 NTFS 來格式化, 這是正常的部分。而 WSL2 主體的 Linux, 是在 VM 內執行的一套 Linux, 主要的 rootfs 來自 c:\users 下某目錄的 ext4.vhdx 虛擬硬碟，如圖左下所示。這 vhdx 對應到 WSL 內的 /dev/sda (Linux 設備內的第一顆硬碟)

而原生 windows 的 disk, 則透過內建在 WSL2 內的 DrvFS 驅動程式掛載進來的, 預設會按照 windows 的磁碟機代號, 按照 /mnt/c, /mnt/d ... 照順序一個一個 mount, 因此你可以在 WSL2 內用這樣的路徑存取 windows 的檔案。

而反過來，windows 也可以透過 \\wsl$\ubuntu\ 來存取 wsl2 的 rootfs, 其中 ubuntu 應該替換成你安裝的 distro 名稱 (如果你不是選 ubuntu 的話)，這是透過 9p protocol 來存取的 (這看 Microsoft 官方的圖就比較清楚了)

![alt text](/wp-content/images/2024-11-11-working-with-wsl/image-2.png)
> https://www.netadmin.com.tw/netadmin/zh-tw/technology/EDC6D4560B184F0D9E7A750862D3C9E4

每多一層轉換，IO 的效率就會 **很有感** 的下降一級... 我把前面測試的四種案例，都在圖上標示:

1. windows -> windows: 最短路徑, 當作理想毫無損耗的對照組
1. windows -> wsl2, 經過 **9P protocol** 到 linux kernel, 再經過 **hpyervisor** 處理硬碟的虛擬化 (實體是 ext4.vhdx)
1. wsl2 -> wsl2, 只有經過 **hypervisor** 虛擬化硬碟, 其餘都沒有經過額外的轉換
1. wsl2 -> windows, 只有經過 **DrvFS** 轉譯 ( 背後也是有經過 9P protocol, 不過我就把它當作同一件事了) 來傳送檔案存取的要求

每層轉換，我都用黑體標示了。我把上面那張表格內容換一下，對照看就知道影響多大了:

| 測試環境        | 檔案系統  | READ (MiB/s) | 轉換層 | 效能表現 |
|---------------|------------|---------------|---------|----------|
| Windows      | Windows  | 576               | --         | 100% (對照組)     |
| WSL              | WSL         | 209               | Hyper-V | 36.28% |
| Windows     | WSL          | 16.5              | 9P protocol + Hyper-V | 2.86% |
| WSL            | Windows   | 37.5              | DrvFS | 6.51% |

我用很不精準的估算，其實還算合理。如果單純經過 Hpyer-V 大概只剩 36.28% 的效能；只經過 9P 大概剩 6.51% 的效能，兩個都過一次就是 36.28% x 6.51% = 2.34%, 其實跟第三項測試結果接近 (2.86%), 大致上可以驗證架構圖上的路徑。

而我說這篇文章 (日文這篇) 很有意思，後面的內容就是介紹 WSL2 如何額外掛載獨立的 Disk, Hyper-V 允許你直接掛上原生的硬碟, 效率會好得多。

而 WSL 層層轉譯的效能研究，這一篇也講得不錯，它把我的情境做了更多詳細的測試跟圖表 (怎麼又是日文的... Orz)
https://news.mynavi.jp/article/20220318-2296803/

其實還有一個組合，我這次沒拿出來用，就是 WSL - WSL 的組態，受限於預設的 WSL 配置，Windows 會在 c:\ 配置一個 vhdx 檔案給 wsl 當作 disk 使用，導致無可避免地多了一層 Hyper-V 的轉換。其實如果你願意的話，是可以直接掛載實體的 disk 或是 partation 給 WSL 用的 (其實就是這篇日文文章的後半段在講的作法，或是 Microsoft 官方文件也有說明: [Mount a Linux disk in WSL2](https://learn.microsoft.com/en-us/windows/wsl/wsl2-mount-disk?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155))。你可以原生就格式化成 ext4 .. 這會最大化 WSL 的磁碟效能，應該跟原生的磁碟表現同等級的吧。目前硬體設備不足，等到哪天我 WSL 越用越兇，願意投資一顆專屬的 SSD 給 WSL 用的話，再來補這個測試..

看到這邊，大概心理的疑慮都有答案了。雖然數字不好看，但是知道原因，知道表現，我至少有能力閃開他，挑選我最適合的用法了。接下來繼續往下，看看我實際的配套措施。



## 2-3, 實際部署 Qdrant 測試資料庫

接下來，就拿我實際的測試案例出來吧。在之前聊 RAG 的文章: "______" 內，我用的是 Microsoft Kernel Memory 這個服務，封裝 file storage 以及 vector database, 整合幾種主流的 LLM 與 Embedding Model, 結合而成的 RAG 服務框架..

而這服務，背後的 vector database 是可以選擇的，我選用了最廣受好評的 Qdrant。我自己一份測試資料，大約包含了 40000 筆資料，整個 DB 內涵的資料樣貌大致如下:

```

Dirs:	43782
Files:	282797
Bytes: 5.386GB

```

其實，還不需要動用到 benchmark, 光是看啟動時間就有差別了... 我直接拿 docker logs 來看，從第一筆啟動的 log timestamp, 直到看到 gRPC ready 的紀錄為止:

```
Attaching to qdrant-1
qdrant-1  |            _                 _
qdrant-1  |   __ _  __| |_ __ __ _ _ __ | |_
qdrant-1  |  / _` |/ _` | '__/ _` | '_ \| __|
qdrant-1  | | (_| | (_| | | | (_| | | | | |_
qdrant-1  |  \__, |\__,_|_|  \__,_|_| |_|\__|
qdrant-1  |     |_|
qdrant-1  |
qdrant-1  | Version: 1.12.4, build: 5b578c4f
qdrant-1  | Access web UI at http://localhost:6333/dashboard
qdrant-1  |
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

第一組，是跑在 /mnt/c 底下的測試結果，也就是 wsl -> windows 的組態，啟動已有四萬筆資料的 qdrant container, 需要 38.376 sec ..

仔細看看 docker logs, 你會發現, 時間都花費在載入 collection，例如這行就花掉 6 sec, 才看的到下一行:

```
qdrant-1  | 2024-11-11T15:17:28.399231Z  INFO storage::content_manager::toc: Loading collection: b2e-knowledge
```

第二組，換了個位置，Log 都長的一樣我就不貼了, 條件完全都一樣，只是檔案搬到 wsl rootfs 內，直接存在 VM 的 vhdx 內。這對應到的是 wsl -> wsl 的組態，這次啟動 qdrant 只需要 1.499 sec ..

同樣的，那麼明顯的差距 ( 啟動時間差了 25x, 從 38.376 s 降至 1.499 s ) ，我就懶得再拿 benchmark 來測試 DB 效能了。基本上我自己在測試的時候，打 API 要 insert 一筆資料庫，就需要花掉 5 sec 的時間... 這段的重點在確認問題來源，跟怎麼重新改變我的工作環境，不是在測試與調教 qdrant 的效能 ...


## 2-4, 在 windows 下掛載 wsl 的資料夾

知道問題原因在 volume 沒有擺對地方後，解決方法就換個目錄就搞定了。我把檔案擺在對的地方，也就是執行效率最好的地方 ( wsl 的 /opt/docker )，然後想辦法用 mount 的技巧，維持我習慣的存取方式，問題就解決了。Linux 下有 mount 跟 ln 可以自由的掛載目錄結構，我只要在 windows 下做同一件事，把 wsl 下的 /opt/docker 掛到 windows 下的 c:\codes\docker 就好了。

有的, windows 也能這樣玩。大概在 windows 2000 那個年代的 ntfs 就開始支援的 reparse points 機制。對應的 windows command 是 [mklink.exe](https://learn.microsoft.com/zh-tw/windows-server/administration/windows-commands/mklink?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) 就可以做類似的操作。

WSL 的檔案系統，在 windows 下可以透過 \\wsl$\ubuntu\.... 來存取 ( ubuntu 是 distro name )，所以你只需要用 mklink 指令，把 \\wsl$\ubuntu\opt\docker 掛在 c:\codes\docker 就好了。指令很簡單: 

```
mklink /d \\wsl$\ubuntu\opt\docker c:\codes\docker
```

這麼一來，你不論用檔案總管，或是 vscode，只要照原本的習慣操作就好了。唯一需要留意的是記得備份。因為它終究是個連結，實際檔案是存在 ext4.vhdx 虛擬硬碟內的。這 vhdx 檔案結構損毀的話，你的檔案就消失了.. 

另一個要留意的是，換個地方擺 volume, 雖然直接避開了 qdrant 執行時大量跨 kernel 的 IO 效能問題, 但是問題仍然在... 只要你有跨系統存取同一份資料夾的話，終究會有一邊的效能較差的 (此例就是 windows 端存取會變慢)。如果你有需求從 windows 端對這目錄做大量 IO 操作的話，仍然會碰到這個問題..

這問題在後面的互通性再繼續聊，現在先跳過不談，用 mklink 重新掛載 WSL 的資料夾，這倒不失為一個好方法，既維持了我原本工作的習慣與方便性，也解決了硬碟效能問題 (你要買多高級的 SSD 才能有 20x 的效能提升? )


## 2-5, 其他 file system 議題


最後，補充兩項我在研究這議題翻到的資訊，但是我這篇決定不特別深談的議題

1. windows / linux 對於檔案系統的權限管理機制不同
1. windows NTFS 額外支援的特殊功能: NTFS stream

科普一下，Windows 的權限設計較複雜，NTFS 導入了完整的 RBAC ( Role Based Access Control )，支援用 ACL ( Access Control List ) 的方式來管控檔案權限。而 Linux 則單純的多，只是按照當前的執行者身分跟群組，以及檔案的屬性 (chmod) 來決定能否存取。兩者管控的模式完全不同，DrvFS 是無法直接對應轉換的，因此這些設定，在跨系統存取的時候都會失效。

另一個 NTFS 的特異功能也是，就是 NTFS stream... 我想應該沒幾個人聽過 & 用過這東西吧? 基本上一般認知的檔案，就是一個唯一的檔名，對應到一組串流資料 ( stream )。而 NTFS，允許你一個檔案，有主要的串流資料之外，還可以有多個附掛的 stream.. 

這些機制，Linux 同樣不支援。因此，有些檔案你在 wsl 下來看，會多出一些莫名其妙的檔案名稱出來，就是這些 NTFS stream 在作怪。看到的時候請無視它就好。

https://blog.miniasp.com/post/2008/07/23/Useful-tools-Streams-let-you-know-the-uncovered-secret-in-NTFS


# 3, GitHub Pages with Visual Studio Code

透過 mklink, 在 windows 掛載 wsl 的工作環境，雖然解決了使用習慣問題，但是終究是把效能問題換邊放而已啊，跨越 OS kernel 的存取效能終究不好。我只是把效能好的部分保留給 linux 端 ( wsl ) 而已。如果我在 windows 端有別的工具要處理檔案，還是會踩到效能糟的那個環節。

舉例來說，前面的案例是 container 跑 database, 大量的 io 都是發生在 runtime, 因此把檔案丟到 wsl 為主的環境很正常，在 windows 端的操作大概就編輯 dockerfile, docker-compose.yaml 這類操作而已，慢一點不會有感。

不過複雜一點的情境，同一份檔案我可能 "同時" 需要透過 windows / linux application 存取，同時都對檔案的存取效能很敏感。例如 IDE, 我要面對的是 source code 編輯, 有大量的 css / html / 圖檔等等，IDE 運作會高頻次的存取這些檔案，而 code 在 build 或是 git pull / push / commit 也都會有大量小檔案的存取操作，如果同時又有需要在 container 下存取這些檔案，上面的作法就無法兼顧了。這時，所有的軟體，包含 IDE, git, build tool, runtime, container 等等都應該在同一個體系內 (白話: 這些工具通通都改用 linux 版，因為很多東西在 windows 上不堪用，或是沒有選擇) 才能解決... 這就回到這段的主題: 跨系統 (跨 OS Kernel) 操作的互通性了。

不得不誇一下 Microsoft, WSL 在這部份真的是做得沒話講，先天上 Microsoft 居於劣勢 (無法拋棄 windows nt kernel)，但是跨兩個 os-kernel，居然能做到這般整合的程度，連我都覺得是外星黑科技了。就算是我也花了點功夫，才搞清楚 Microsoft 在背後做了哪些事情... 這段就來聊聊這部分神奇的機制

(1) 跨 OS 的 file system 整合:  
首先, 前面提到 Microsoft 在 WSL 已經把 file system 打通了。windows -> wsl 有 drvfs, 可以在 wsl 內 mount windows file system, 而 wsl -> windows 也支援 9p protocol, windows 內可以用 \\wsl$\ubuntu\ 來存取

(2) 跨 OS 的 GUI 整合:  
接下來是 UI, 某一版 windows 開始支援 WSLg, 意思是你可以把 Linux 的 UI 顯示到 Windows 上，就是 Xwindows 那套機制，可以運用到 GPU 資源。這背後其實打通了 device 這層 (後面會再度聊到 GPU，我這邊先點到為止)，UI 操作面也打通了。 (不過最終這個我覺得不大實用，我用不到)

(3) 跨 OS 的 CLI / Executable File 整合:  
第三個是 command 的整合。這個真的是黑科技，我可以在 linux 下啟動 windows application, 反過來也可以 ( ssh 很普及, windows 下 linux 指令反倒沒甚麼 ) 

其中 (1) 前面介紹過了，(2) 其實我這次用不到，單純介紹就好。(3) 我覺得是關鍵的黑科技，花點篇幅聊一下..


## 3-1, 在 WSL 下執行 Windows CLI / Application

我先示範幾個情境，各位猜看看，你猜不猜的到背後 Microsoft 是怎麼做的?

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
andrew@ANDREW-PC:/opt/docker$ nvidia-smi
Wed Nov 20 01:30:26 2024
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 565.51.01              Driver Version: 565.90         CUDA Version: 12.7     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4060 Ti     On  |   00000000:0A:00.0  On |                  N/A |
|  0%   51C    P8             15W /  165W |    1582MiB /  16380MiB |      1%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    0   N/A  N/A        35      G   /Xwayland                                   N/A      |
+-----------------------------------------------------------------------------------------+
andrew@ANDREW-PC:/opt/docker$

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

