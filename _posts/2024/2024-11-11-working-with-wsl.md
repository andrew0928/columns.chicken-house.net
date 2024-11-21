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

<!--

果然決定丟掉 docker desktop for windows 後就一路順暢... 雖然 disk i/o 效能糟其實是 WSL2 的鍋, 不過過度依賴 docker for windows 會讓人不想直接碰 WSL2, 就衍生了一堆問題..

docker 還是繼續用，只是改成直接進 wsl 安裝 docker 來用, 也順便避開難搞的授權問題 (爽)。決定正式面對 wsl 內的 linux 工作環境之後, disk i/o 問題解掉了, docker 內跑 CUDA 問題也解掉了, 同時也體驗了 vscode remote sh 的威力, 操作介面完全是 windows 的體驗, 但是整個工作環境全都在 linux, 完全就是理想的後端開發環境啊..

我算後知後覺，這些好東西出來了兩三年才發現，還沒用過的歡迎參考我的心得.. :D

-->


![](/wp-content/images/2024-11-11-working-with-wsl/logo.jpg)
> 圖: DALL-E, 我讓 ChatGPT 搜尋我自己然後畫出來的形象圖..

因為越來越多東西需要在原生的 linux 環境下執行, 趁著更新 24H2，重灌 windows 的機會, 就一起認真的重整我的開發環境了。在 windows 下要以 linux 為主要的工作環境，用 wsl (windows subsystem for linux) 是首選，不過畢竟是跨 OS 的使用，也有不少障礙要排除。趁這次花了點時間研究作法，同時也惡補了一下 wsl 的相關背景知識，這才發現 Microsoft 對 WSL 下了不少功夫啊，背後藏了很多不錯的巧思。

在這篇，我會交代我的作法，同時我也會整理一下我找到的參考資訊，以及背後架構與限制。我最想解決的問題 (也是我的動機) 是這幾個:

1. **我想拋開 docker desktop for windows**:  
太多我不必要的東西了, 授權的限制也是原因之一。其實我用的功能不多，改成直接在 linux 下執行 docker 還更單純，少了一堆束縛，跑起來也更輕鬆愉快
1. **我想避開 docker 掛載 volume 的 IO 效能低落問題**:  
目前用法，在 windows 下執行 docker, 掛載 volumes 的 IO 效能很糟糕 (糟到用不下去)
1. **我想在 docker 使用 GPU / CUDA 應用**:  
目前在 windows 下跑 CUDA 困難重重，我只是想爽快地跑 ollama 啊... 我想要把 AI 應用都搬到 docker 環境下去執行, 支援 GPU 的 docker / linux 環境是必要條件
1. **我想建立一個 linux 為主, 能長期使用的通用工作環境**:  
並且能無縫的跟我慣用的 windows 環境整合在一起。常用的工具就那些，包含 visual studio code, git, dotnet 等，能高度整合 windows, 不需要花太多心思在兩套系統間的協作，認知負荷越低越好

花了一個禮拜的下班時間，我總算把我的工作環境打造好了。過程中也發現不少 Microsoft 藏在 WSL 裡面的黑科技。自 WSL2 推出以來，這幾年相關的整合也都成熟了，我就野人獻曝，分享一下我的整理心得。

<!--more-->





# 1. 替換工作環境的動機

動機前面帶過了，不過我決定這樣做的最後一根稻草，是我需要在 docker 上面跑 AI 相關的應用。2024/06 的時候，為了跑本地端的 LLM (我當時只有 CPU: AMD 3900X 跟 GPU: AMD RX570 而已)，算力完全不夠啊，買了張 NVIDIA RTX4060Ti 16GB，結果發現要搞定 CUDA 那堆相依性的套件與設定還真惱人...

難道就不能像 docker 那樣，相依的環境都裝在 image 裡面，拉下來啟動就好嗎? 還真的有，而且大部分科學運算的應用也都是以 Linux 為主，在 Windows 下要搞定 CUDA，還要搞定 Python 執行環境，真的是件煩死人的任務。

於是，我就一路從 docker 環境簡化 (我放棄掉 docker desktop), 搞清楚 GPU 虛擬化, 成功的在 wsl / docker 內能使用 GPU 資源，連帶的解決 docker / wsl 存取 windows file system 的 IO 效能問題, 到整個 visual studio code 的環境完全搬移到 linux ( 對，連你開出 vscode terminal, 都直接是 bash, 不是 powershell ..., 檔案的路徑都是 rootfs, 不是 windows ntfs..)

其中 IO 問題，影響最大。其中的效能差異可以到幾十倍之譜。我有兩個案例，一個是跑向量資料庫 Qdrant, 才塞了四萬筆資料，結果整個 container 啟動竟然需要一分鐘? 另外一個是我自己的部落格，用 Jekyll (Ruby, GitHub Pages 用這套) 來 Build 靜態網站，竟然也要花掉 110 sec ... 我改了一行字要等兩分鐘才看的到結果，這實在不是個能接受的工作環境..

我的桌機雖然是五年前的設備，但是也沒這麼不堪吧? 我列一下我的配備:

```
CPU: AMD Ryzen9 3900X (12 cores, 24 threads)
RAM: DDR4 16GB x 4 ( 64GB )
SSD: Samsung 970Pro 512GB (MLC), PCIE 3.0, NVME
OS: Microsoft Windows 11 Pro ( 當時跑的是 23H2 )
```

我想起我多年前踩過的地雷 ( 2018 的文章: [使用 LCOW 掛載 Volume 的效能陷阱](/2018/07/28/labs-lcow-volume/) )，也碰過類似的狀況，這次我趁著有乾淨環境的狀況下，好好的測試一次，也重新調整過磁碟的使用方式，算是徹底解決掉了，這是第一個成果，我只要些微的改變磁碟目錄的安置方式，問題就搞定了。啟動 Qdrant 的時間只需要原本的 1/25, 部落格文章預覽需要的建置時間只要原本的 1/18 ...

這麼戲劇化的改善，一定是原本的架構有問題 XDD，不然你要花多少錢才買的到 25 倍快的 SSD?

細節後面會交代，我把我這過程碰到的案例，整理歸納成三種類型.. 每種題型我就各挑一個代表來展示就好。後面段落我就來說明這三個情境背後的關鍵原因，跟我解套的方式:

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

第一個就先來面對我最痛的 Docker IO 效能問題，以前我認為這無解，就乾脆不在本機跑這些服務了 (我直接丟到 NAS / Cloud 用原生的 Linux 來跑，眼不見為淨)。


在這邊先科普一下 WSL 的 file system 架構... 看底下這張圖:

![](/wp-content/images/2024-11-11-working-with-wsl/image.png)
> https://www.polarsparc.com/xhtml/IntroToWSL2.html


基本上存取路徑大致可以這樣分，應用程式都是在黃色的 user space 執行的 ( 有 windows / wsl 兩個 )，而 file system 也都是跟著 kernel 的 ( 一樣有 windows: NTFS, 也有 wsl: ext4 ), 而我用預設的 wsl, disk 多一層虛擬化 (對應到 NTFS 上的檔案: ext4.vhdx )

因此，我列出所有的 4 種組合情境:

1. 由 windows app 存取 windows file system:  
NTFS, c:\benchmark_temp, 最直接的存取路徑, 沒有額外消耗的理想情境, 大部分單純的 windows 應用都是這類。  

1. 由 wsl application 存取 wsl file system:  
EXT4, ~/benchmark_temp, 在 linux kernel 內基本上軟體也是直接的路徑, 不過同上, 虛擬硬碟終究多了一層 .vhdx 轉換。  

1. 由 windows app 存取 wsl file system:  
EXT4, \\wsl$\ubuntu\home\andrew\benchmark_temp, 中間跨越 9p protocol 進到 linux kernel 就能存取到檔案。但是 wsl 畢竟是個 windows 下運作的 lightweight VM，他的磁碟是虛擬化而來的，多了一層 .vhdx 的轉換。   

1. 由 wsl application 存取 windows file system:  
NTFS, /mnt/c/benchmark_temp, 中間經過一層 drvfs 檔案系統的處理 (這是由 Microsoft 開發並且開源的 linux file system, 會負責將檔案系統的存取經由 9p protocol 轉接到 windows file system) 的轉換..


舉例來說，如果你在 windows 下執行 docker, 下了這個指令:

```
docker run ......  -v c:\working-dir\:/mydir .....
```

Docker 會啟動一個 container, 並且把 windows 下的 c:\working-dir\ 掛載到 container 內的 /mydir 路徑。這時 container 存取檔案的時候，就會走 (4) 的路徑了，磁碟效能會被扒一層皮 ( drvfs )。你會發現效能掉的很離譜，就是這種狀況。

這時，除了損失效能之外，DrvFS 對應兩種截然不同的 file system, 也會失去部分 NTFS 的特性。例如 NTFS 的檔案異動通知 [FileSystemWatcher](https://learn.microsoft.com/zh-tw/dotnet/api/system.io.filesystemwatcher?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) 就無法對應到 Linux 的檔案異動通知 [inotify](https://zh.wikipedia.org/zh-tw/Inotify)，因此 container 如果掛載了 windows 下的檔案目錄，這些功能就失效了。

這影響有多大? 我後面會提及的例子: GitHub Pages 的應用就很頭痛。我在 windows 編輯的檔案，GitHub Pages 的 container 內無法靠檔案系統的機制偵測到異動，因此只能用很蠢的輪巡 (polling) 機制來檢查，效能跟反應速度就掉了一大截，慘不忍睹 (有一段時間我都直接放棄這機制，改採手動，我自己有更動檔案，自己重啟一次 container, 結果還比較快)。偏偏很多教學文件，都教你這樣用 .... ，連我都踩雷了一陣子才發現，過去都在浪費時間...
。



## 2-1, WSL 磁碟效能 Benchmark


這次我不忍了，先來跑分量化一下效能到底差距有多大.. ，再來研究怎麼解決。前面提到的四種組合我都跑一次 disk benchmark 來比較看看差異...。 我用同一套設備，就我的桌機，測試當下我已經小幅度升級軟硬體了，升級後的規格跟組態如下:

```
CPU: AMD Ryzen9 3900X
RAM: DDR4 16GB x 4 = 64GB
WSL Distro: Ubuntu 24.04 LTS

(以下有升級過了)
SSD: Crucial T500 2TB PCIe Gen4 NVMe M.2 SSD
GPU: NVidia RTX 4060Ti - 16GB
OS: Microsoft Windows 11 Pro (24H2)
```

測試工具，我選擇同時有 windows / linux 版本的 [fio](https://fio.readthedocs.io/en/latest/fio_doc.html), 跨平台支援我可以用一樣的測試來比較結果。Fio 的安裝也很容易, 在 wsl 下只要一行指令就能安裝:

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

測試檔案大小 16GB, 隨機讀寫, 4k block, 8 jobs, disable cache, 連續測試 300 sec

這四組測試的結果，我直接都貼給 ChatGPT 幫我彙整了，我就不另外整理數據了，請看 AI 幫我整理的分析報告:

---

### 數據表格 (via ChatGPT)

|編號| 測試環境        | 檔案系統  | READ (MiB/s) | READ IO (GiB) | WRITE (MiB/s) | WRITE IO (GiB) | 測試時長 (秒) |
|----|----------------|---------------|-------------------|------------------|--------------------|-------------------|---------------|
|(1)| Windows    | Windows       | 576               | 169              | 576                | 169               | 300           |
|(2)| WSL            | WSL           | 209               | 61.2             | 209                | 61.2              | 300           |
|(3)| Windows    | WSL           | 16.5              | 4.951            | 16.5               | 4.958             | 300           |
|(4)| WSL            | Windows       | 37.5              | 11.0             | 37.6               | 11.0              | 300           |

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




其他情境差距更大，我只關注我最在意的 database access 使用情境，因此我挑 4k random 讀寫, 並且有多 process 平行處理的情況, 最好跟最差就有 576MB/s 跟 16.5 MB/s 的差別，足足 35x 的差距... (我用 HDD 跟 SSD 也沒差這麼多啊)。實在無法想像，還好我有做過這測試才知道差距這麼大... 既然知道狀況了，我就知道該怎麼解決 (或是避開) 這問題了。


## 2-2, 測試數據的解讀, 與 WSL 架構

雖說對這結果 (分數) 有點意外，但是對照架構圖來看，其實都能找到合理的解釋。還記得前面我描述四種路徑的檔案存取，個別經過甚麼轉換嗎?

我找了張仔細一點的架構圖:

![alt text](/wp-content/images/2024-11-11-working-with-wsl/image-2.png)
> 來源: [第2版視窗子系統Linux　二刀流無縫順暢運行](https://www.netadmin.com.tw/netadmin/zh-tw/technology/EDC6D4560B184F0D9E7A750862D3C9E4)

每多一層轉換，IO 的效率就會 **很有感** 的下降一級... 按照這圖的說明，我把前面測試的四種案例經過的轉換，都整理成列表，並且做成表格:

1. **windows -> windows**:  
最短路徑, 當作理想毫無損耗的對照組
1. **windows -> wsl2**:  
經過 **9P protocol** 到 linux kernel, 再經過 **hpyervisor** 處理硬碟的虛擬化 (實體是 ext4.vhdx)
1. **wsl2 -> wsl2**:  
只有經過 **hypervisor** 虛擬化硬碟, 其餘都沒有經過額外的轉換
1. **wsl2 -> windows**:  
只有經過 **DrvFS** 轉譯 ( 背後也是有經過 9P protocol, 不過我就把它當作同一件事了) 來傳送檔案存取的要求

每層轉換，我都用黑體標示了。我把上面那張表格內容換一下，對照看就知道影響多大了:

|編號| 測試環境        | 檔案系統  | READ (MiB/s) | 轉換層 | 效能表現 |
|-----|---------------|------------|---------------|---------|----------|
|(1)| Windows      | Windows  | 576               | --         | 100% (對照組)     |
|(2)| WSL              | WSL         | 209               | Hyper-V | 36.28% |
|(3)| Windows     | WSL          | 16.5              | 9P protocol + Hyper-V | 2.86% |
|(4)| WSL            | Windows   | 37.5              | DrvFS | 6.51% |


從 (2) 大約可以推估經過 Hpyer-V 會只剩 36.28% 的效能；從 (4) 推估經過 9P protocol 剩 6.51% 的效能，那麼兩個都過一次就是 36.28% x 6.51% = 2.34%, 其實已經很接近 (3) 的測試結果了, 大致上可以驗證架構圖上的路徑。

而 WSL 層層轉譯的效能研究，也有網友做了比我還詳盡的測試: [Windows Subsystem for Linuxガイド 第5回 wsl$ファイルシステムとWSLファイルベンチマーク編](https://news.mynavi.jp/article/20220318-2296803/) (雖然是日文的，但是找了好幾篇就這篇最清楚)   

其實，如果你認真要用 WSL，(2) 的情境是有機會調整到跟 (1) 差不多的，那就是直接掛實體硬碟 (disk) 或是分割區 (partition) 讓 WSL 專用，就可以免去 Hyper-V 處理 .vhdx 的效能折損 (只剩 36.28%)。Microsoft 官方文件就有說明作法: [Mount a Linux disk in WSL2](https://learn.microsoft.com/en-us/windows/wsl/wsl2-mount-disk?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155)。雖然設置麻煩了一點，不過你可以得到最好的效能表現。等到哪天我 WSL 越用越兇，願意投資一顆專屬的 SSD 給 WSL 用的話，再來補這個測試..

看到這邊，大概心理的疑慮都有答案了。雖然數字不好看，但是知道原因，知道表現，我至少有能力閃開他，挑選我最適合的用法了。接下來繼續往下，看看我實際的配套措施。

## 2-3, 實際部署 Qdrant 測試資料庫

接下來，就拿我實際的測試案例出來吧。在之前聊 RAG 的文章: [替你的應用程式加上智慧! 談 RAG 的檢索與應用](/2024/03/15/archview-int-blog/) 內，我用的是 [Microsoft Kernel Memory](https://github.com/microsoft/kernel-memory) 這個服務，封裝 file storage 以及 vector database, 整合幾種主流的 LLM 與 Embedding Model, 結合而成的 RAG 服務框架..

而這服務，背後的 vector database 是可以選擇的，我選用了最廣受好評的 [Qdrant](https://qdrant.tech/) 。我自己一份測試資料，大約包含了 40000 筆資料，整個 DB 內涵的資料樣貌大致如下:

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

仔細看看 docker logs, 你會發現, 時間都花費在載入 collection，例如光這行就花掉 6 sec, 才看的到下一行:

```
qdrant-1  | 2024-11-11T15:17:28.399231Z  INFO storage::content_manager::toc: Loading collection: b2e-knowledge
```

第二組，換了個位置，Log 都長的一樣我就不貼了, 條件完全都一樣，只是檔案搬到 wsl rootfs 內，直接存在 VM 的 vhdx 內。這對應到的是 wsl -> wsl 的組態，這次啟動 qdrant 只需要 1.499 sec ..

同樣的，那麼明顯的差距 ( 啟動時間差了 25x, 從 38.376 s 降至 1.499 s ) ，我就懶得再拿 benchmark 來測試 DB 效能了。基本上我自己在測試的時候，打 API 要 insert 一筆資料庫，就需要花掉 5 sec 的時間... 這段的重點在確認問題來源，跟怎麼重新改變我的工作環境，不是在測試與調教 qdrant 的效能 ...


## 2-4, 在 windows 下掛載 wsl 的資料夾

知道問題原因在 volume 沒有擺對地方後，解決方法就換個目錄就搞定了。我把檔案擺在對的地方，也就是執行效率最好的地方 ( wsl 內的 /opt/docker )，然後想辦法用 symbolic link 的技巧，維持我習慣的存取方式，問題就解決了。我只要在 windows 下做同一件事，把 wsl 下的 /opt/docker 掛到 windows 下的 c:\codes\docker 就好了。

在 windows 下有個指令: [mklink.exe](https://learn.microsoft.com/zh-tw/windows-server/administration/windows-commands/mklink?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) 就是做這件事，你可以用下面的指令把這 symbolic link 建立起來:

```
mklink /d \\wsl$\ubuntu\opt\docker c:\codes\docker
```

我貼一下我實際的工作環境, 在 windows terminal 下 dir 可以看到:

```

C:\CodeWork>dir
 Volume in drive C is Windows
 Volume Serial Number is 6A76-E5CC

 Directory of C:\CodeWork

10/14/2024  12:11 PM    <SYMLINKD>     docker [\\wsl$\ubuntu\opt\docker]

# 以下略

```

這麼一來，你不論用檔案總管，或是 vscode，只要照原本的習慣操作就好了。唯一需要留意的是記得備份。因為它終究是個連結，實際檔案是存在 ext4.vhdx 虛擬硬碟內的。這 vhdx 檔案結構損毀的話，你的檔案就消失了.. 

另一個要留意的是，換個地方擺 volume, 雖然直接避開了 qdrant 執行時大量跨 kernel 的 IO 效能問題 (走 case 2, wsl -> wsl, 36.28%), 但是問題仍然在... 如果你從另一端 (windows) 來存取檔案 (case 3, windows -> wsl, 2.86%)，則是效能最糟糕的安排。如果你有需求從 windows 端對這目錄做大量 IO 操作的話，仍然會碰到這個問題..

這問題在後面的互通性再繼續聊，現在先跳過，用 mklink 重新掛載 WSL 的資料夾，這倒不失為一個好方法，既維持了我原本工作的習慣與方便性，也解決了硬碟效能問題 (你要買多高級的 SSD 才能有 20x 的效能提升? )





## 2-5, 其他 file system 議題


最後，補充兩項我在研究這議題翻到的資訊，但是我這篇決定不特別深談的議題

1. windows / linux 對於檔案系統的權限管理機制不同
1. windows NTFS 額外支援的特殊功能: NTFS stream

科普一下，Windows 的權限設計是基於 RBAC ( Role Based Access Control )，支援用 ACL ( Access Control List ) 的方式來管控檔案權限。而 Linux 則單純的多，是按照當前的執行者身分跟群組，以及檔案的屬性 (chmod) 來決定能否授予存取權限。這兩者管控的模式完全不同，DrvFS 是無法直接對應轉換的，因此這些設定，在跨系統存取的時候都會失效。

另一個 NTFS 的特異功能也是，就是 NTFS stream... 我想應該沒幾個人聽過 & 用過這東西吧? 基本上一般認知的檔案，就是一個唯一的檔名，對應到一組串流資料 ( stream )。而 NTFS，允許你一個檔案，有主要的串流資料之外，還可以有多個附掛的 stream.. 

這些機制，Linux 同樣不支援。因此，有些檔案你在 wsl 下來看，會多出一些莫名其妙的檔案名稱出來，就是這些 NTFS stream 在作怪。看到的時候請無視它就好。

想了解 NTFS stream, 保哥這篇介紹的蠻清楚的: [介紹好用工具：Streams 讓你瞭解神秘的 NTFS 檔案系統](
https://blog.miniasp.com/post/2008/07/23/Useful-tools-Streams-let-you-know-the-uncovered-secret-in-NTFS)





# 3, GitHub Pages with Visual Studio Code

前面的案例: Qdrant 把檔案移到 wsl rootfs 下，來避開效能問題時有提到，優化了 linux app 的 IO 效能，就代表 windows app 存取同一份資料的效能就會掉下來，因為終究有一方要面對跨 kernel 的問題，你只能權衡看哪邊比較重要而以，在 Qdrant 這案例，我選擇了顧好 container 的效能，而 windows 存取的效能就是堪用就好。

但是在開發的應用，這兩件事就沒辦法靠邊站了。開發時主要是靠 IDE, 通常需要在 windows 環境下不斷的做 git 的操作 ( git clone, pull, push, commit, ... ), 或是 code build 的操作 ( dotnet build, docker build, ... ), 而測試，除錯，執行等等則是另一個面向，需要在執行環境 (linux) 執行開發階段的產出 ( build output, run container .. ), 而為了讓程式順利執行, 也許也會有相依的東西要一起執行 (例如 database, 就會踩到前面 Qdrant 的案例)。

這種情況就沒有選邊站的空間了。我就把腦筋動到工具的身上，如果我連工具都搬到 linux 上面執行呢? 如果我連 IDE 都可以在 linux 上執行呢? 這就回到這段的主題: 跨系統 (跨 OS Kernel) 操作的互通性了。

不得不誇一下 Microsoft, WSL 在這部份真的是做得沒話講，先說結論，Visual Studio Code 的 Remote Shell 模式，已經可以完美的解決這問題了。Microsoft 同時在 WSL 的底層，Linux Executable 格式的支援，檔案系統的互通，硬體虛擬化的互通，以及軟體層的抽象化設計 ( vscode 支援 code-server ) 都要配合，才做得到的成就。這連我都覺得是外星黑科技了。就算是我也花了點功夫，才搞清楚 Microsoft 在背後做了哪些事情... 這段就來聊聊這部分神奇的機制

接下來，我就分兩個主題來聊聊這整合環境怎麼做到的，第一個先來看 WSL 怎麼執行 Windows 的執行檔 (沒錯，你可以在 Linux 跑 .exe )，第二個來看 Visual Studio Code 的 Remote Shell ..



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




## 3-2, Visual Studio Code 的 Remote Shell 

即使你已經能在 wsl 啟動 windows application, 終究還是 windows application 啊，嚴格的來說並沒有解決前面碰到的 IO 限制問題。

理想的作法是，把 vscode 拆成兩半，前後端分離；一半處理 UI (留在 windows)，一半處理後端 (留在 linux)，前後端分離，中間有統一的傳輸通道 ( ssh ) 連結起來。

結果還真的有這東西，其實 Microsoft 想得比我快好幾步，這些東西早就在那邊了，而且遠端的模式遠超出我預期: [VS Core Remote Development](https://code.visualstudio.com/docs/remote/remote-overview) 這官方的說明講得很詳細，你可以在你熟悉的 desktop environment 使用 vscode (windows, mac ..), 而工作環境則可以透過 remote development 的機制，連結到你的後端工作環境。支援的連接方式很完整，可以 SSH 或是建立 Tunnel 來連到你既有的 VM，也可以直接用 Container 啟動一個全新的獨立環境，或是直接連到本機的 WSL..

我貼一段官網的簡介，所有的特色都在這裡了:

**Visual Studio Code Remote Development** allows you to use a container, remote machine, or the [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl) (WSL) as a full-featured development environment. You can:

- Develop on the **same operating system** you deploy to or use **larger or more specialized** hardware.
- **Separate** your development environment to avoid impacting your local **machine configuration**.
- Make it easy for new contributors to **get started** and keep everyone on a **consistent environment**.
- Use tools or runtimes **not available** on your local OS or manage **multiple versions** of them.
- Develop your Linux-deployed applications using the **Windows Subsystem for Linux**.
- Access an **existing** development environment from **multiple machines or locations**.
- Debug an **application running somewhere else** such as a customer site or in the cloud.

**No source code** needs to be on your local machine to get these benefits. Each extension in the [Remote Development extension pack](https://aka.ms/vscode-remote/download/extension) can run commands and other extensions directly inside a container, in WSL, or on a remote machine so that everything feels like it does when you run locally.

![alt text](/wp-content/images/2024-11-11-working-with-wsl/image-3.png)


不過，雖然功能這麼多，我只針對 WSL 環境的使用來介紹就好了。我前面多介紹 WSL 可以跑 windows .exe 這段，是因為這是最後一段串連我使用方式的關卡，我可以完全照我平常的習慣，在 terminal 啟動 vscode, 直接開啟工作目錄:

// wsl -> code
// init code server
// launch code.exe
// connect remote to wsl


到這裡，這真的是我認為的理想解決方案了。UI 完全就是 windows 的影子，但是骨子裡完全就是 linux 的東西... 彷彿就是 windows 的 kernel 完全替換成 linux 一樣...

這真的解掉我一個大難題，就是我的部落格撰寫環境。從現在開始，我想要在我本機環境寫部落格，只要這樣做:

1. WSL: git clone
1. WSL: launch vscode
1. VSCODE: git pull, switch branch
1. VSCODE: terminal, docker compose up
1. Open preview page: http://localhost:4000 in browser or in vscode
1. VSCODE: git commit & git push

最後我的改變，只是在我部落格的 git repo 底下，加了一個 docker-compose.yaml ，設定了怎麼啟動 GitHub Pages 的預覽環境。這個 container 跑起來之後，只要我改完檔案存檔，5 sec 左右就可以預覽了。如果你不記得網址，VSCODE 也會提醒你 remote port ..

寫到這邊，我沒有遺憾了 XDD
所有開發環境的問題都解決了，整合度高，執行效率好，IO效率也好，都能用 linux 原生環境，容器化，一行指令就跑起來，不用裝一大堆套件 (就搞定 vscode + docker 就夠了)




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

