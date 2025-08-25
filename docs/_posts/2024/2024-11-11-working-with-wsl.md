---
layout: post
title: "用 WSL + VSCode 重新打造 Linux 開發環境"
categories:
- "技術隨筆"
tags: ["技術隨筆", "VSCode", "Jekyll", "Docker", "WSL"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /images/2024-11-11-working-with-wsl/logo.jpg
---

![](/images/2024-11-11-working-with-wsl/logo.jpg)
> 圖: DALL-E, 趕流行, 我讓 ChatGPT 搜尋我自己然後畫出來的形象圖..

TL;DR; 這篇只是心得文而已，記錄我把主要工作環境翻新成 WSL + VS code 的過程，跟背後追問題學到的冷知識..

--

因為越來越多東西需要在原生的 linux 環境下執行, 趁著更新 [24H2](https://learn.microsoft.com/en-us/windows/whats-new/whats-new-windows-11-version-24h2?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155)，重灌 windows 的機會, 就一起認真的重整我的開發環境了。在 windows 下要以 linux 為主要的工作環境，用 [WSL](https://learn.microsoft.com/en-us/windows/wsl/setup/environment?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) (windows subsystem for linux) 是首選，不過畢竟是跨 OS 的使用，也有不少障礙要排除。趁這次花了點時間研究作法，同時也惡補了一下 wsl 的相關背景知識，這才發現 Microsoft 對 WSL 下了不少功夫啊，背後藏了很多不錯的巧思。

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

我想起我多年前踩過的地雷 ( 2018 的文章: [使用 LCOW 掛載 Volume 的效能陷阱](/2018/07/28/labs-lcow-volume/) )，也碰過類似的狀況，這次我趁著有乾淨環境的狀況下，好好的測試一次，也重新調整過磁碟的使用方式，算是徹底解決掉了，這是第一個成果，我只要些微的改變磁碟目錄的安置方式，問題就搞定了。啟動 [Qdrant](https://qdrant.tech/) 的時間只需要原本的 1/25, 部落格文章預覽需要的建置時間只要原本的 1/18 ...

這麼戲劇化的改善，一定是原本的架構有問題 XDD，不然你要花多少錢才買的到 25 倍快的 SSD?

細節後面會交代，我把我這過程碰到的案例，整理歸納成三種類型.. 每種題型我就各挑一個代表來展示就好。後面段落我就來說明這三個情境背後的關鍵原因，跟我解套的方式:

1. 需要大量 IO 的 docker container - 示範案例: [Qdrant](https://qdrant.tech/)
1. 需要整合環境 Visual Studio Code - 示範案例: 我的部落格撰寫環境 [GitHub Pages](https://pages.github.com/)
1. 需要 GPU 支援的 docker container - 示範案例: AI 模型推論的基本環境, [Ollama](https://ollama.com/) + [Open-WebUI](https://github.com/open-webui/open-webui)

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

![](/images/2024-11-11-working-with-wsl/image.png)
> 來源: [Introduction to WSL 2](https://www.polarsparc.com/xhtml/IntroToWSL2.html)


基本上存取路徑大致可以這樣分，應用程式都是在黃色的 user space 執行的 ( 有 windows / wsl 兩個 )，而 file system 也都是跟著 kernel 的 ( 一樣有 windows: NTFS, 也有 wsl: ext4 ), 而我用預設的 wsl, disk 多一層虛擬化。

WSL 磁碟對應到 NTFS 上的檔案: ext4.vhdx, 預設路徑在這裡: 

```
c:\Users\%USERNAME%\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu_79rhkp1fndgsc\LocalState\ext4.vhdx
```

因此，我列出所有的 4 種組合情境:

1. **由 windows app 存取 windows file system**:  
NTFS, ```c:\benchmark_temp```, 最直接的存取路徑, 沒有額外消耗的理想情境, 大部分單純的 windows 應用都是這類。  

1. **由 wsl application 存取 wsl file system**:  
EXT4, ```~/benchmark_temp```, 在 linux kernel 內基本上軟體也是直接的路徑。但是 wsl 畢竟是個 windows 下運作的 Lightweight VM，他的磁碟是虛擬化而來的，多了一層 .vhdx 的轉換。   

1. **由 windows app 存取 wsl file system**:  
EXT4, ```\\wsl$\ubuntu\home\andrew\benchmark_temp```, 中間跨越 9p protocol 進到 linux kernel 就能存取到檔案。不過同上, 虛擬硬碟終究多了一層 .vhdx 轉換。  

1. **由 wsl application 存取 windows file system**:  
NTFS, ```/mnt/c/benchmark_temp```, 中間經過一層 drvfs 檔案系統的處理 (這是由 Microsoft 開發並且開源的 linux file system, 會負責將檔案系統的存取經由 9p protocol 轉接到 windows file system) 的轉換..


舉例來說，如果你在 windows 下執行 docker, 下了這個指令:

```
docker run ......  -v c:\working-dir\:/mydir .....
```

Docker 會啟動一個 container, 並且把 windows 下的 ```c:\working-dir\``` 掛載到 container 內的 ```/mydir``` 路徑。這時 container 存取檔案的時候，就會走 (4) 的路徑了，磁碟效能會被扒一層皮 ( DrvFS )。你會發現效能掉的很離譜，就是這種狀況。

這時，除了損失效能之外，DrvFS 對應兩種截然不同的 file system, 也會失去部分 NTFS 的特性。例如 NTFS 的檔案異動通知 [FileSystemWatcher](https://learn.microsoft.com/zh-tw/dotnet/api/system.io.filesystemwatcher?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) 就無法對應到 Linux 的檔案異動通知 [inotify](https://zh.wikipedia.org/zh-tw/Inotify)，因此 container 如果掛載了 windows 下的檔案目錄，這些功能就失效了。

這影響有多大? 我後面會提及的例子: GitHub Pages 的應用就很頭痛。我在 windows 編輯的檔案，GitHub Pages 的 container 內無法靠檔案系統的機制偵測到異動，因此只能用很蠢的輪巡 (polling) 機制來檢查，效能跟反應速度就掉了一大截，慘不忍睹 (有一段時間我都直接放棄這機制，改採手動，我自己有更動檔案，自己重啟一次 container, 結果還比較快)。偏偏很多教學文件，都教你這樣用 .... ，連我都踩雷了一陣子才發現，過去都在浪費時間...
。

<a id="chapter2_1" />

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

測試工具，我選擇同時有 windows / linux 版本的 [fio](https://fio.readthedocs.io/en/latest/fio_doc.html), 跨平台支援我可以用一樣的測試來比較結果。我測試的參數統一如下 (除了不同環境，會換掉 path, 也會換掉 io engine 之外, 其餘都相同)，測試的都是同一顆硬碟:

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

測試檔案大小 16GB, 隨機讀寫, 4k block, 8 jobs, disable cache, 連續測試 300 sec。為了驗證高附載的表現，io-depth 我調到 64.. 這參數的意義我貼一下[官方文件](https://fio.readthedocs.io/en/latest/fio_doc.html#i-o-depth)的說明:

**iodepth=int**

Number of I/O units to keep in flight against the file. Note that increasing iodepth beyond 1 will not affect synchronous ioengines (except for small degrees when verify_async is in use). Even async engines may impose OS restrictions causing the desired depth not to be achieved. This may happen on Linux when using libaio and not setting direct=1, since buffered I/O is not async on that OS. Keep an eye on the I/O depth distribution in the fio output to verify that the achieved depth is as expected. Default: 1.


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

![alt text](/images/2024-11-11-working-with-wsl/image-2.png)
> 來源: [第2版視窗子系統Linux　二刀流無縫順暢運行](https://www.netadmin.com.tw/netadmin/zh-tw/technology/EDC6D4560B184F0D9E7A750862D3C9E4)

每多一層轉換，IO 的效率就會 **很有感** 的下降一級... 按照這圖的說明，我把前面測試的四種案例經過的轉換，都整理成列表，並且做成表格:

1. **windows -> windows**:  
最短路徑, 當作理想毫無損耗的對照組
1. **windows -> wsl2**:  
經過 **9P protocol** 到 linux kernel, 再經過 **hpyervisor** 處理硬碟的虛擬化 (實體是 ext4.vhdx)
1. **wsl2 -> wsl2**:  
只有經過 **hypervisor** 虛擬化硬碟, 其餘都沒有經過額外的轉換
1. **wsl2 -> windows**:  
只有經過 **DrvFS** 轉譯 ( 背後也是有經過 **9P protocol**, 不過我就把它當作同一件事了) 來傳送檔案存取的要求

每層轉換，我都用黑體標示了。我把上面那張表格內容換一下，對照看就知道影響多大了:

|編號| 測試環境        | 檔案系統  | READ (MiB/s) | 轉換層 | 效能表現 |
|-----|---------------|------------|---------------|---------|----------|
|(1)| Windows      | Windows  | 576               | --         | 100% (對照組)     |
|(2)| WSL              | WSL         | 209               | Hyper-V | 36.28% |
|(3)| Windows     | WSL          | 16.5              | 9P protocol + Hyper-V | 2.86% |
|(4)| WSL            | Windows   | 37.5              | DrvFS | 6.51% |


從 (2) 大約可以推估經過 **Hpyer-V** 會只剩 36.28% 的效能；從 (4) 推估經過 **9P protocol** 剩 6.51% 的效能，那麼兩個都過一次就是 36.28% x 6.51% = 2.34%, 其實已經很接近 (3) 的測試結果了, 大致上可以驗證架構圖上的路徑。

而 WSL 層層轉譯的效能研究，也有網友做了比我還詳盡的測試: [Windows Subsystem for Linuxガイド 第5回 wsl$ファイルシステムとWSLファイルベンチマーク編](https://news.mynavi.jp/article/20220318-2296803/) (雖然是日文的，但是找了好幾篇就這篇最清楚)   

其實，如果你認真要用 WSL，(2) 的情境是有機會調整到跟 (1) 差不多的，那就是直接掛實體硬碟 (disk) 或是分割區 (partition) 讓 WSL 專用，就可以免去 **Hyper-V** 處理 .vhdx 的效能折損 (只剩 36.28%)。Microsoft 官方文件就有說明作法: [Mount a Linux disk in WSL2](https://learn.microsoft.com/en-us/windows/wsl/wsl2-mount-disk?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155)。雖然設置麻煩了一點，不過你可以得到最好的效能表現。等到哪天我 WSL 越用越兇，願意投資一顆專屬的 SSD 給 WSL 用的話，再來補這個測試..

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

第一組，是跑在 ```/mnt/c``` 底下的測試結果，也就是 wsl -> windows 的組態，啟動已有四萬筆資料的 qdrant container, 需要 38.376 sec ..

仔細看看 docker logs, 你會發現, 時間都花費在載入 collection，例如光這行就花掉 6 sec, 才看的到下一行:

```
qdrant-1  | 2024-11-11T15:17:28.399231Z  INFO storage::content_manager::toc: Loading collection: b2e-knowledge
```

第二組，換了個位置，Log 都長的一樣我就不貼了, 條件完全都一樣，只是檔案搬到 wsl rootfs 內，直接存在 VM 的 vhdx 內。這對應到的是 wsl -> wsl 的組態，這次啟動 qdrant 只需要 1.499 sec ..

同樣的，那麼明顯的差距 ( 啟動時間差了 25x, 從 38.376 s 降至 1.499 s ) ，我就懶得再拿 benchmark 來測試 DB 效能了。基本上我自己在測試的時候，打 API 要 insert 一筆資料庫，就需要花掉 5 sec 的時間... 這段的重點在確認問題來源，跟怎麼重新改變我的工作環境，不是在測試與調教 qdrant 的效能 ...


## 2-4, 在 windows 下掛載 wsl 的資料夾

知道問題原因在 volume 沒有擺對地方後，解決方法就換個目錄就搞定了。我把檔案擺在對的地方，也就是執行效率最好的地方 ( wsl 內的 ```/opt/docker``` )，然後想辦法用 symbolic link 的技巧，維持我習慣的存取方式，問題就解決了。我只要在 windows 下做同一件事，把 wsl 下的 ```/opt/docker``` 掛到 windows 下的 ```c:\codes\docker``` 就好了。

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

檔案總管下，也看的到類似的資訊:
![alt text](/images/2024-11-11-working-with-wsl/file-explorer-mklink.png)



這麼一來，你不論用檔案總管，或是 vscode，只要照原本的習慣操作就好了。唯一需要留意的是記得備份。因為它終究是個連結，實際檔案是存在 ext4.vhdx 虛擬硬碟內的。這 vhdx 檔案結構損毀的話，你的檔案就消失了.. 

另一個要留意的是，換個地方擺 volume, 雖然直接避開了 qdrant 執行時大量跨 kernel 的 IO 效能問題 (走 case 2, wsl -> wsl, 36.28%), 但是問題仍然在... 如果你從另一端 (windows) 來存取檔案 (case 3, windows -> wsl, 2.86%)，則是效能最糟糕的安排。如果你有需求從 windows 端對這目錄做大量 IO 操作的話，仍然會碰到這個問題..

這問題在後面的互通性再繼續聊，現在先跳過，用 mklink 重新掛載 WSL 的資料夾，這倒不失為一個好方法，既維持了我原本工作的習慣與方便性，也解決了硬碟效能問題 (你要買多高級的 SSD 才能有 25x 的效能提升? )





## 2-5, 其他 file system 議題


最後，補充兩項我在研究這議題踩到的資訊，但是我這篇決定不特別討論的議題:

1. windows / linux 對於檔案系統的權限管理機制不同
1. windows NTFS 額外支援的特殊功能: NTFS stream

科普一下，Windows 的權限設計是基於 RBAC ( Role Based Access Control )，支援用 ACL ( Access Control List ) 的方式來管控檔案權限。而 Linux 則單純的多，是按照當前的執行者身分跟群組，以及檔案的屬性 (chmod) 來決定能否授予存取權限。這兩者管控的模式完全不同，DrvFS 是無法直接對應轉換的，因此這些設定，在跨系統存取的時候都會失效。

另一個 NTFS 的特異功能也是，就是 NTFS stream... 我想應該沒幾個人聽過 & 用過這東西吧? 基本上一般認知的檔案，就是一個唯一的檔名，對應到一組串流資料 ( stream )。而 NTFS，允許你一個檔案，有主要的串流資料之外，還可以有多個附掛的 stream.. 

這些機制，Linux 同樣不支援。因此，有些檔案你在 wsl 下來看，會多出一些莫名其妙的檔案名稱出來，就是這些 NTFS stream 在作怪。看到的時候請無視它就好。

想了解 NTFS stream, 保哥這篇介紹的蠻清楚的: [介紹好用工具：Streams 讓你瞭解神秘的 NTFS 檔案系統](
https://blog.miniasp.com/post/2008/07/23/Useful-tools-Streams-let-you-know-the-uncovered-secret-in-NTFS)


<a id="chapter2_6" />

## 2-6, WSL 掛載額外的 Disk

> 2024/12/06 追加測試:  
> 在寫這篇文章的過程中，也發現了 WSL2 在某個版本後也支援 mount 額外的磁碟機了。能掛上的選項, 包含 .vhdx 虛擬磁碟機, 或是實體磁碟機都可以。如果你認真要拿 WSL 處理一些任務，配置專屬的磁碟機這絕對是必要的啊! 於是, 我寫完原本要分享的內容後，追加了測試，也把結果補在這段了。

這段落，我想弄清楚，我如果投資專用的 SSD 給 WSL 使用，來改善 IO 效率是否值得? 不同的掛載方式表現如何?

先說結果吧，結論是 "絕對值得"! 改善效果很明顯。如果 WSL 是你主要的工作場域，投資專用的 SSD 並且正確的配置是值得的。某些場景下，你甚至會得到比 windows + ntfs 還要好的存取效能。為了這個測試，我把古董 SSD 也挖出來了，連同原本的系統碟，我的 PC 上目前總共裝了這四顆 SSD, 為了讓大家有基本認識，括號我放了這些 SSD 上市的年份，還有基本效能規格:

1. 系統碟 - Crucial T500 Gen4 SSD, 2TB TLC ( [2023](https://www.crucial.tw/ssd/t500/CT4000T500SSD3), R: 7000mb/s, W: 6900mb/s  )
1. 工作碟 - Samsung 970Pro Gen3 SSD, 512GB MLC ( [2018](https://semiconductor.samsung.com/consumer-storage/internal-ssd/970pro/), R: 3500mb/s, 2700mb/s )
1. 參考用 - Kingston NV1 Gen3 SSD, 500GB, QLC ( [2021](https://www.kingston.com/datasheets/SNVS_tw.pdf), R: 2100mb/s, W: 1700mb/s )
1. 參考用 - Intel 730SSD, 240GB, SATA 6GB, MLC ( [2014](https://www.intel.com/content/dam/www/public/us/en/documents/product-specifications/ssd-730-series-spec.pdf), R: 550mb/s, W:470mb/s )

前面的測試，都是在 (1) 的狀況, 只有一顆 SSD 測的。假如有專屬的 SSD 要給 WSL 用，有三種方式可以配置 (如下)，我加上直接在 windows 下使用 SSD 當作對照組，共有這四種:

1. (對照組) 實體磁碟用 NTFS, 直接在 windows 下存取 ( x:\test )
1. (實驗組) 實體磁碟用 NTFS, wsl 直接透過 DrvFS 的方式使用 ( /mnt/x )
1. (實驗組) 實體磁碟用 EXT4, 將實體磁碟機直接掛上 wsl 使用 ( /dev/sdc1 )
1. (實驗組) 虛擬磁碟用 EXT4, (在實體磁碟, NTFS 上面建立虛擬磁碟 .vhdx ) 掛上 wsl 存取使用 ( /dev/sdc1 )

我在我所有可以動用的硬碟，每顆都測試了這四種配置方式。有些測試項目跟前面的測試有重複，我用前面的表格，跟這段落的測試方式做個對比:

這是前面 [#2-1, WSL 磁碟效能 Benchmark](#chapter2_1) 的測試整理

|編號| 測試環境        | 檔案系統  | READ (MiB/s) | 轉換層 | 效能表現 |
|-----|---------------|------------|---------------|---------|----------|
|(1)| Windows      | Windows  | 576               | --         | 100% (對照組)     |
|(2)| WSL              | WSL         | 209               | Hyper-V | 36.28% |
|(3)| Windows     | WSL          | 16.5              | 9P protocol + Hyper-V | 2.86% |
|(4)| WSL            | Windows   | 37.5              | DrvFS | 6.51% |


這邊我既然都要準備 WSL 專用的 SSD 了，上述測試就有點多餘。我拿 (1) 當作對照組，畢竟大部分 windows 的使用者都是 (1) 的方式在使用 SSD, 能代表合理的性能表現。其餘我只測試 WSL 為主的環境，就是 (2) 跟 (4) 兩項。專用 SSD 要用的場景其實是 (2), 但是 WSL 預設的作法不是用虛擬硬碟 ( .vhdx ), 而且 windows / linux 兩個層面都跟作業系統本身共用硬碟，最後對比 (1) 只有 36% 的效能，實在看不過去，難道我用了 WSL 就只能忍受這樣的效能嗎?

所以我用了兩種配置方式來擴充 (2) 的應用，從磁碟分割開始，我就直接將整顆 SSD 交給 WSL 使用, 實體磁碟機直接對應到 /dev/sdc, 不過我也保留 .vhdx 的做法，做了相同的測試，我想了解只有多了虛擬化會有多大的影響。

所以前後兩段的測試數據，你如果要一起看，大概就是這樣:

|編號| 測試環境        | 檔案系統  |  (這次的測試項目) |
|-----|---------------|------------|---------------|
|(1)| Windows      | Windows  | (對照組) 實體磁碟用 NTFS, 直接在 windows 下存取 |
|(2)| WSL              | WSL         | (實驗組)虛擬磁碟用 EXT4, 掛上 wsl 存取使用 |
|(*2)| WSL              | WSL         | *(實驗組) 實體磁碟用 EXT4, 將實體磁碟機直接掛上 wsl 使用, **這是新的測試** |
|(3)| Windows     | WSL          | 略, 不做這項測試了 |
|(4)| WSL            | Windows   | (實驗組) 實體磁碟用 NTFS, wsl 直接透過 DrvFS 的方式使用 |


測試工具我同樣用 fio 的 windows / linux 兩種版本, 用相同的參數測試, 我同樣用高負載的參數 ( jobs = 8, io-depth = 64 ) 來看評比。這測試方式比較吃 SSD 本身顆粒的讀寫性能，反而跟介面的規格關連不大，某些場合，我那顆 10 年前的 SSD 還能跑贏這兩年的 QLC SSD ... (真心建議 QLC 別拿來工作用)。

每顆硬碟，我就都跑這四種組態來測試看看吧! 我的系統碟 ( Cruicial T500 ) 因為 windows 安裝在上面，基本上沒辦法用實體磁碟的方式掛上 wsl 了，因此 (3) 的數據從缺。

直接來看結果:

**1. 系統碟 - Crucial T500 Gen4 SSD, 2TB TLC ( 2023 )**

|測試|配置方式|測試環境|測試分數 (mb/s) |
|-----|-------------------|-----------|----------|
|1.     | 實體磁碟用 NTFS| windows | 609 (~~576~~)  |
|2.     | 實體磁碟用 NTFS| wsl          | 37.5 |
|3.     | 實體磁碟用 EXT4| wsl          | --  |
|4.     | 虛擬磁碟用 EXT4| wsl          | 620 (~~497~~, ~~209~~)  |

這棵 SSD，是 "帳面上" 規格最好最新的磁碟機了，除了 TLC 比 MLC 差之外。系統碟上面的干擾多，測試起來誤差也大。同樣測試，我大約一個月前跑的數字是 576 (前面 [#2-1, WSL 磁碟效能 Benchmark](#chapter2_1) 的數據)，不過我自己多次測試，有幾次是跑出 609 mb/s 左右的成績，稍微好了一點 ( +7% )，不過為了維持這段落能互相參照，在這邊我選擇用後面的測試數據為主。

第二個要注意的地方是 (4), 先前的測試跑出 209 mb/s 的分數，但是那是跟兩套作業系統共用的結果 (我無法排除到底有多少干擾)，我關掉所有我能關的 WSL 背景服務重跑一次，可以跑到 497mb/s... 不過這點是挺怪的, 這些背景服務理論上也會影響所有成績, 包括 windows - ntfs 在內, 但是數據上倒是虛擬硬碟影響最大。當我進一步隔離虛擬磁碟，我在同一顆硬碟下 ( windows c:\ ) 額外建立一個 WSL.vhdx, 拿這個虛擬磁碟掛到 WSL 來測試，跑出第二個分數 620 mb/s, 即使物理上都是同一顆 SSD，但是配置方式看來影響頗大，同樣的我就取第二個測試數據 620 mb/s 了，原本的數據我列在後面。




**2. 工作碟 - Samsung 970Pro Gen3 SSD, 512GB MLC ( 2018 )**

這顆則是我六年前買的 SSD，當時組裝這台工作機時買的，帳面上規格差了些，傳輸介面是 Gen3, 理論頻寬只有 Gen4 的一半, 容量也小, 年代也久遠。不過 MLC 跟 TLC 先天的差距，在這種高負載測試情境下，都跑不到介面的理想速度，這五年技術的差距仍然沒有追回來啊.. 意外的發現舊款的SSD 跑出來還比新的 SSD 強...

少了虛擬化的轉換，wsl + ext4 的效率竟然還強過 windows + ntfs ...，是原本的 120% .. 這組測試結果，完全可以這樣使用啊，有點意外的是跑出來的成績竟然比直接在 windows 下使用還強。我猜可能性只有 NTFS 多做了很多我們看不到的事情 (例如 security)，相對的 EXT4 精簡的多，就反映在速度與效能上了。

而在 windows + ntfs 上面建立的虛擬硬碟，格式化成 ext4 掛上 wsl, 跑出來的成績跟 windows + ntfs 一樣 ( 那 0.6% 的差距我就當誤差了)，很明顯的瓶頸是掉在 ntfs 身上...



|測試|配置方式|測試環境|測試分數 (mb/s) |
|-----|-------------------|-----------|----------|
|1.     | 實體磁碟用 NTFS| windows | 646  |
|2.     | 實體磁碟用 NTFS| wsl          | 36.9 |
|3.     | 實體磁碟用 EXT4| wsl          | 780  |
|4.     | 虛擬磁碟用 EXT4| wsl          | 650  |



**3. 參考用 - Kingston NV1 SSD, 500GB, QLC ( 2021 )**

這棵 QLC 的 SSD 其實不是買的，是家人買電腦的 "贈品"，之前我連裝都懶的裝起來用，它躺在我的抽屜裡兩年多了，這次為了測試，特地買了張 PCIE 轉接卡，把它裝起來試試看了...。不裝還好，跑起來果然如預期的差... Orz, 這分數甚至比 10 年前的高階機種還糟糕，跑出來的分數最差只有一半左右... 。

2014 的 MLC, 跟 2021 的 QLC 差距就是這麼大。如果你是工作用的設備，就別考慮 QLC 了，什麼廠牌都差不多慘...

|測試|配置方式|測試環境|測試分數 (mb/s) |
|-----|-------------------|-----------|----------|
|1.     | 實體磁碟用 NTFS| windows | 74.1  |
|2.     | 實體磁碟用 NTFS| wsl          | 31.4  |
|3.     | 實體磁碟用 EXT4| wsl          | 49.6 |
|4.     | 虛擬磁碟用 EXT4| wsl          | 46.3 |





**4. 參考用 - Intel 730SSD, 240GB, SATA, MLC ( 2014 )**

我挖出骨董硬碟，當年也是一時之選，Intel 將企業級 SSD 的技術下放到消費性產品的 SSD, 雖然是十一年前發表的產品了，不過跑出來的成績沒有到很差啊，除了 (2) 明顯是架構問題，DrvFS 的折損太大，不管什麼組態跑出來都落在 35 上下，應該就是 DrvFS 的限制了吧。其他三項成績都在 100, 看起來這就是 SSD 本身的極限了。

不過，看到這骨董 SATA 介面的 SSD，表現還能輾壓 NVME 介面的 QLC SSD .. 想想還是留著好了。像這樣有 LAB 需要測試時，看起來骨董硬碟還比較好用一點 XDD



|測試|配置方式|測試環境|測試分數 (mb/s) |
|-----|-------------------|-----------|----------|
|1.     | 實體磁碟用 NTFS| windows | 100  |
|2.     | 實體磁碟用 NTFS| wsl          | 34.8 |
|3.     | 實體磁碟用 EXT4| wsl          | 99  |
|4.     | 虛擬磁碟用 EXT4| wsl          | 101  |


沒有太多設備可以交叉測試，也難以控制變因，搞到最後 SSD 的介面有 SATA/Gen3/Gen4 都有, SSD 顆粒也涵蓋不同世代的 MLC/TLC/QLC, 設備的年份也從 2013 ~ 2023 橫跨了 10 年... 這數據就純當作參考吧，沒那麼客觀的測試比較方式，得到的結論也只是推測，大家看看就好。有不同想法也歡迎留言給我。



**我簡單總結一下我的觀察**:

歸納一些我認為的影響因素，跟實驗的結果對比推測。我的測試樣本不夠，各位請把這些當作 "觀察" 就好，還不是 100% 肯定的影響...

1. **跟 os 共用 disk 的影響很大**:  
跟前面案例對比, 同樣虛擬磁碟 (.vhdx) 的測試, 完全一樣的環境, 只是拆成獨立的 .vhdx 就有明顯的提升了 ( 209 mb/s -> 620 mb/s )
1. **顆粒的特性影響很大** #1 ( 可惜我手上沒有 SLC 可以驗證.. T_T ),  
一個影響是絕對的效能表現, 看的到在高負載隨機讀寫的情況下 (我模擬 DB 的應用)。現階段效能前段班的 TLC 打不贏 6 年前的 MLC.. 同樣的現階段 QLC ( 抱歉我只有中階的可以測試 ) 也一樣拚不贏更古老 10 年前 SATA MLC .. 如果你有選擇, 顆粒類型優先
1. **顆粒的特性影響很大** #2,  
這次談的是相對的效能表現。就是 SSD 在原生的 windows 環境下的表現，跟原生硬碟掛載在 wsl 下的表現落差，這點我其實是想不通的.. XDD, MLC 可以到 120%, 即使多包一層用 .vhdx 虛擬硬碟, 也有追平 100% 的表現, 兩顆 MLC, 跟現役前段班 TLC 新舊世代的代表都如此。而 QLC 慢歸慢, 但是相對效率竟然掉到只有 60% 左右我就不能理解了, 只能把原因歸類到 windows 可能特別對這類 SSD 作了什麼最佳化，而 WSL 沒做吧?
1. **虛擬化有額外 CPU 資源消耗, 但是效能影響不大可以考慮**:  
只要你的主機性能能追得上 (跑測試時這項的 CPU 使用率偏高)，這影響其實不大，可以接受的。拿測試項目中最後兩項來對比，差別只差在虛擬硬碟，差距都不大，看來只有在 SSD 本身效能夠強的時候會有感 ( 970Pro )，其他主機運算效能夠好，大概都能追平這中間的效率落差。實際應用如果這落差對你無感，用虛擬硬碟方便很多，其實是可以考慮的，不用糾結最高效能。
1. **請把 DrvFS 視為網路磁碟機，別當作本機磁碟使用**:  
這組就真的只是拿來對照用了，別拿它來當作工作環境。不管哪種組態，很明顯都卡在 35 mb/s 上下。唯獨 QLC 這顆 SSD，看來有額外的影響，掉得更低，只到 31.4 mb/s 。基本上 DrvFS 就方便操作就好，別透過他來跑 IO 負載重的服務，自找麻煩而已.. 別為了圖方便而踩到這個地雷..

合併這四顆 SSD 的測試數據，並且以 (1) windows 的數字當作理想數據，標示每種配置方式的對比效率:

|測試|  配置方式             |測試環境  | Crucial<br/>T500(TLC) | Samsung<br/>970Pro(MLC)| Kingston<br/>NV1(QLC)| Intel<br/>SSD730(MLC)|
|-----|-------------------|-----------|---------------|--------------------|----------------|-----------------|
|1.     | 實體磁碟用 NTFS| windows | 609<br/>(100%)   | 646<br/>(100%)           | 74.1<br/>(100%)   | 100<br/>(100%) |
|2.     | 實體磁碟用 NTFS| wsl          | 37.5<br/>(6.16%) |36.9<br/>(5.71%)         | 31.4<br/>(42.38%)  | 34.8<br/>(34.8%) |
|3.     | 實體磁碟用 EXT4| wsl          | --                  |**780<br/>(120.74%)**     | 49.6<br/>(66.94%)   | **99<br/>(99%)**  |
|4.     | 虛擬磁碟用 EXT4| wsl          | **620<br/>(101.81%)** | **650<br/>(100.62%)**    | 46.3<br/>(62.48%)  | **101<br/>(101%)**  |

越接近 100%, 就代表越接近原生的效率 (所以我拿在 windows 下的表現當基準)。我覺得在 WSL 這種虛擬化環境下，有 80% 以上的表現其實都算合格了，達標的我都標一下黑體，有興趣的可以參考。看起來 (可能是巧合吧) ，只有 QLC 很戲劇化的... 沒有跟上，其他都能達到理想的使用效能。

如果真的要給配置的結論，我會建議:

1. **最理想的組態**:  
你就買顆等級好一點的 SSD 直接給 WSL 用吧，顆粒的選擇比介面的選擇重要。TLC 輸給 5 年前的 MLC，QLC 輸給 10 年前的 MLC .. 在 SSD 的世界裡不要迷信新的一定比較好...
1. **避開低階產品**:  
虛擬磁碟看來會高度依賴顆粒本身的選擇，控制器與 SSD 本身的架構可能也會有顯著的差異。工作用的設備，請避開太過低階的選項 ( QLC + DRAMless 看來是大地雷)
1. **請直接採用 EXT4**:  
在 WSL 的世界就別考慮 NTFS 了，你要用 NTFS 的話就乖乖留在 windows ... WSL + NTFS 占不到便宜的
1. **把 DrvFS 當作網路磁碟機來使用**:  
最後，跨系統的 disk mount ( 透過 DevFS 或是 9P protocol ), 一樣就當作方便的檔案搬運管道就好, 基本上你要把它當作網路磁碟看待，而不是本機磁碟。


操作方式我就附上官方的說明了，其實很多小細節要留意，需要的人自己研究: [Mount a Linux disk in WSL 2](https://learn.microsoft.com/en-us/windows/wsl/wsl2-mount-disk?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155)





# 3, GitHub Pages with Visual Studio Code

前面的案例: Qdrant 把檔案移到 wsl rootfs 下，來避開效能問題時有提到，優化了 linux app 的 IO 效能，就代表 windows app 存取同一份資料的效能就會掉下來，因為終究有一方要面對跨 os-kernel 的問題，你只能權衡看哪邊比較重要而以，在 Qdrant 這案例，我選擇了顧好 linux 端 container 的效能，而 windows 存取的效能就是堪用就好。

但是在開發的應用，這兩件事就沒辦法靠邊站了。開發時主要是靠 IDE, 通常需要在 windows 環境下不斷的做 git 的操作 ( git clone, pull, push, commit, ... ), 或是 code build 的操作 ( dotnet build, docker build, ... ), 而測試，除錯，執行等等則是另一個面向，需要在執行環境 (linux) 執行開發階段的產出 ( build output, run container .. ), 而為了讓程式順利執行, 也許也會有相依的東西要一起執行 (例如 database, 就會踩到前面 Qdrant 的案例)。

這種情況就沒有選邊站的空間了。我把腦筋動到工具的身上，如果我可以連工具都搬到 linux 上面執行呢? 如果我連 IDE 都可以在 linux 上執行呢? 這就回到這段的主題: 跨系統 (跨 OS Kernel) 操作的互通性了。

不得不誇一下 Microsoft, WSL 在這部份真的是做得沒話講，先說結論，Visual Studio Code 的 [Remote Development](https://code.visualstudio.com/docs/remote/remote-overview) 模式，已經可以完美的解決這問題了。Microsoft 同時在 WSL 的底層，Linux Executable 格式的支援，檔案系統的互通，硬體虛擬化的互通，以及軟體層的抽象化設計 ( vscode 支援 [code-server](https://code.visualstudio.com/docs/remote/vscode-server) ) 都要配合，才做得到的成就。這連我都覺得是外星黑科技了。就算是我也花了點功夫，才搞清楚 Microsoft 在背後做了哪些事情... 這段就來聊聊這部分神奇的機制

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

看起來頂多只是像 ssh 那樣的感覺，好像沒有那麼了不起... 我再示範另一個 case, 直接在 wsl 下叫出檔案總管 (請注意，在 WSL 下不能省掉 .exe)，並且開到目前 (wsl) 的工作目錄:

```
andrew@113N000081:~$ explorer.exe .
```

開出來的檔案總管 (注意看檔案總管的資料夾開在這位置 ```\\wsl.localhost\Ubuntu\home\andrew``` ):

![alt text](/images/2024-11-11-working-with-wsl/wsl-launch-explorer.png)




這個就神奇了，開起來就是個貨真價實的 windows 版檔案總管 ( file explorer ), UI 也是 windows 原生的, Process 也是 windows 的。這黑科技怎麼做到的其實很有趣，Microsoft 動了點手腳，讓 linux 認得 PE 格式的擋頭，然後重新導向這個啟動的動作.. 細節我就不多說，有興趣可以看這篇文章: [Working across Windows and Linux file systems](https://learn.microsoft.com/en-us/windows/wsl/filesystems?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155), 其中最後一段 Interoperability between windows and linux commands, 說明了不少這機制的使用方式。

運作原理嘛，簡單的說 wsl 把 windows 執行檔的結構 PE format, 預先註冊到 Linux binfmt_misc 了，因此碰到這種格式 (就是 windows .exe file ), 就會啟動註冊的 handler, 背後一連串的安排, 就能啟動 host os 實際的 .exe 了。

爬文爬到一些資訊，我就留個線索，有興趣的追看看吧:

```
andrew@ANDREW-PC:~$ cat /proc/sys/fs/binfmt_misc/WSLInterop

enabled
interpreter /init
flags: PF
offset 0
magic 4d5a
```



## 3-2, Visual Studio Code: Remote Development

回到 vscode, 在 wsl 就算能啟動 vscode, 它仍然是在 windows user mode 環境下執行的 application, 存取 wsl file system 的效能瓶頸沒有解決。理想的作法是: vscode 本身要有前後端分離的結構，分別處理 UI 操作 (這部分留在 windows)，跟實際處理檔案、編譯等等背景作業 (這部分留在 linux)，如果做得到，這些問題就算完美解決了。

結果查了一下，還真的有這東西，而且支援的遠端的模式遠超出我預期: [VS Core Remote Development](https://code.visualstudio.com/docs/remote/remote-overview) 這官方的說明講得很詳細，我直接貼簡介:

**Visual Studio Code Remote Development** allows you to use a container, remote machine, or the [Windows Subsystem for Linux](https://learn.microsoft.com/windows/wsl?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) (WSL) as a full-featured development environment. You can:

- Develop on the **same operating system** you deploy to or use **larger or more specialized** hardware.
- **Separate** your development environment to avoid impacting your local **machine configuration**.
- Make it easy for new contributors to **get started** and keep everyone on a **consistent environment**.
- Use tools or runtimes **not available** on your local OS or manage **multiple versions** of them.
- Develop your Linux-deployed applications using the **Windows Subsystem for Linux**.
- Access an **existing** development environment from **multiple machines or locations**.
- Debug an **application running somewhere else** such as a customer site or in the cloud.

**No source code** needs to be on your local machine to get these benefits. Each extension in the [Remote Development extension pack](https://aka.ms/vscode-remote/download/extension) can run commands and other extensions directly inside a container, in WSL, or on a remote machine so that everything feels like it does when you run locally.

![alt text](/images/2024-11-11-working-with-wsl/image-3.png)

Remote Development 支援好幾種環境 ( SSH, WSL, DevContainer, Tunnel )，我只針對 WSL 環境的使用來介紹就好了。官方的說明我貼兩個，一個是 vscode server 的架構說明，另一個是 WSL 的部署方式。

先看第一個 - [Visual Studio Code Server](https://code.visualstudio.com/docs/remote/vscode-server):

**What is the VS Code Server?**

In VS Code, we want users to seamlessly leverage the environments that make them the most productive. The VS Code Remote Development extensions allow you to work in the Windows Subsystem for Linux (WSL), remote machines via SSH, and dev containers directly from VS Code. These extensions install a server on the remote environment, allowing local VS Code to smoothly interact with remote source code and runtimes.

We now provide a standalone "VS Code Server," which is a service built off the same underlying server used by the remote extensions, plus some additional functionality, like an interactive CLI and facilitating secure connections to vscode.dev.

從架構圖來看, vscode 就是負責 ui 操作, 而 source code 的存取 ( file system ), terminal, run / debug application 等等都是在 vscode server 這端進行的, 中間只透過 vscod remote - tunnel extension 來溝通

![alt text](/images/2024-11-11-working-with-wsl/image-4.png)



因此，各種不同的 remote development 模式, 其實就是不同的部署方式與不同的 protocol 而已。我採用的 WSL 實際部署方式，參考這篇: [Developing in WSL](https://code.visualstudio.com/docs/remote/wsl)

**Developing in WSL**

The Visual Studio Code WSL extension lets you use the Windows Subsystem for Linux (WSL) as your full-time development environment right from VS Code. You can develop in a Linux-based environment, use Linux-specific toolchains and utilities, and run and debug your Linux-based applications all from the comfort of Windows.

The extension runs commands and other extensions directly in WSL so you can edit files located in WSL or the mounted Windows filesystem (for example /mnt/c) without worrying about pathing issues, binary compatibility, or other cross-OS challenges.

![alt text](/images/2024-11-11-working-with-wsl/image-1.png)

This lets VS Code provide a local-quality development experience — including full IntelliSense (completions), code navigation, and debugging — regardless of where your code is hosted.


--

我選擇 WSL 的整合的原因，因為它緊密到你幾乎可以把它當作單機版使用。一來無網路環境也可以正常執行，甚至你也能在 WSL 工作目錄下直接下指令叫出 vscode, 就像我可以在 powershell 下直接叫出 Notepad 來編輯文字檔一樣。這用起來真的很外星科技，我示範一下:


操作 1: git clone / git pull 後, 叫出 vscode

```
andrew@113N000081:/opt/docker/columns.chicken-house.net$ git pull
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Total 5 (delta 4), reused 5 (delta 4), pack-reused 0 (from 0)
Unpacking objects: 100% (5/5), 2.91 KiB | 496.00 KiB/s, done.
From https://github.com/andrew0928/columns.chicken-house.net
   b907c21..eaf0edc  draft      -> origin/draft
Updating b907c21..eaf0edc
Fast-forward
 _posts/2024/2024-11-11-working-with-wsl.md | 91 ++++++++++++++++++++++++++++++++++++-------------------------------------------
 1 file changed, 41 insertions(+), 50 deletions(-)
andrew@113N000081:/opt/docker/columns.chicken-house.net$ code .
andrew@113N000081:/opt/docker/columns.chicken-house.net$
```

我下了 ``` code . ``` 指令, 就可以開啟 vs code, 並且將目前的工作目錄載入 workspace。這背後其實是幾個分解動作..

首先，我本來一直以為 code 跟前面的 explorer.exe 一樣, 就是啟動 windows 執行檔而已，其實 code 只是個 linux 的 shell script... 這 script 的位置在 ```/mnt/c/Program Files/Microsoft VS Code/bin/code``` , 內容就不貼了, 最重要的目的，就是在你下指令的同時，一起把 vscode-server 安裝 / 更新 / 啟動 都先處理好，, 再啟動 windows 端的 vscode ( 本尊是 code.exe 才對) 而已。

如果你是第一次使用 (或是有更新 vscode), 你應該會自這瞬間看到一段文字說明，說他在更新 vscode-server 的字樣 (我錯過這機會，沒截到圖)。成功啟動 vs code 後，左下角看的到 ```WSL - Ubuntu``` 的字樣，代表你現在的 vscode 已經是 remote development 狀態, 連線的工作環境就是 ```wsl - ubuntu```.

簡單幾個動作測試一下，證明 vscode 是 remote development mode..


1. 試試看 CTRL-O 開啟檔案, 你會發現能選的檔案，都是 linux 環境下的檔案:  
![alt text](/images/2024-11-11-working-with-wsl/vscode-open-file-dialog.png)  

1. 用 CTRL-` 開啟 vscode 內建的 terminal, 開出來的是 linux 下的 bash, 工作目錄就是 git repo 的目錄:  
![alt text](/images/2024-11-11-working-with-wsl/vscode-terminal.png)  

1. 在 terminal 啟動 docker compose, 會直接起一個 GitHub Pages 的 container, 跑 Jekyll 來建置靜態網站:  
![alt text](/images/2024-11-11-working-with-wsl/image-6.png)  

1. (bonus) 可以偵測這個 session 是否有轉發 ports, 可以列出來並且開瀏覽器預覽內容:  
![alt text](/images/2024-11-11-working-with-wsl/image-7.png)
  
1. 如果你喜歡，可以在 vscode 預覽:  
![alt text](/images/2024-11-11-working-with-wsl/image-9.png)  


>
> 補一段跟主題無關，單純推薦的用法: VSCode 從 [May 2023 (version 1.79)](https://code.visualstudio.com/updates/v1_79) 開始支援 markdown 編輯時，可以從剪貼簿直接貼上 image，會自動在指定目錄存圖檔，並且插入對應的 markdown image 標記。
> 
> 在這之前，我都是安裝額外的 extension 來做類似功能的，不過先前試過各種 "remote" 的方案，包括自己蓋了一個 [code-server](https://github.com/coder/code-server)( Run VS Code on any machine anywhere and access it in the browser )，但是都卡在這類功能無法啟用，一直跟我說 server side 缺乏 xclip 套件之類的，明明我裝了也沒有解決...
> 
> 現在改用 WSL remote, 加上 vscode 也內建這功能, 遠端編輯無法直接貼上圖檔的問題順便被解決掉了, 開始覺得這樣的編輯環境，已經遠遠的把各種 online editor ( 我當年用過 word press, 更早以前還用過 windows live writer, 有年輕人用過嗎 XDDD ) 甩在一旁了。現在有各種線上文件編輯需求，我一率推薦 Git + VSCode + [Static Site Builder](https://www.cloudflare.com/learning/performance/static-site-generator/) 這種組合。  
>


寫到這邊，我沒有遺憾了 XDD
所有開發環境的問題都解決了，整合度高，執行效率好，IO效率也好，都能用 linux 原生環境，容器化，一行指令就跑起來，不用裝一大堆套件 (就搞定 vscode + docker 就夠了)




# 4, GPU (CUDA) Application

終於來到最後一個，跑 LLM 需要用到 GPU , 需要相依 Python 套件, 也要相依很難搞的 CUDA ... ( CUDA 版本相容性很難纏，裝錯版本可能就跑不起來了 )


結果，這個問題真的是我庸人自擾，想太多了。Microsoft 早就幫我解決掉了... 在搞清楚黑科技怎麼做的之前，先來體驗一下效果。我直接看 ollama 的 docker hub 上的說明，他把步驟整理的很精簡:


## 4-1, Ollama Docker 的設定步驟

https://hub.docker.com/r/ollama/ollama

摘要步驟，大致是這樣:

1. windows 上面要裝 NVIDIA GPU driver (版本夠新就可以，沒有特別的軟體要安裝或設定)
2. wsl 安裝 NVIDIA container toolkit, 注意 wsl 不需要再裝 linux 環境的 GPU driver 了..
3. wsl 設定 docker runtime 要正確使用 ```nvidia-ctk``` (NVIDIA container toolkit)

其實, 第一步做完, wsl 本身就已經支援 GPU 了，後面的動作都是為了 docker 內可以使用 GPU 而準備的。沒想到這個需求意外的簡單，按照步驟做完一次就成功了

你可以在 wsl 下這指令: ```nvidia-smi``` 就看的到顯卡的資訊了:

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

之後就可以快樂的讓你的 container 能直接使用到 GPU 運算資源了。你只需要在 docker run 啟動 container 時追加這參數 ```--gpus=all```，指派可用的 GPU 給他就可以了。

例如:

```
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```


試跑了一下 ```llama3.2```, 問了幾個問題, 回應速度還挺快的, 底下這堆訊息大概一秒鐘就回應完成了, 比正常人說話的速度快多了:

![alt text](/images/2024-11-11-working-with-wsl/image-8.png)


對應 windows 的 task manager, 果然看的到 GPU 有 loading... 多問了兩句，感覺對於 RTX4060Ti-16GB 來說不痛不癢的:
![alt text](/images/2024-11-11-working-with-wsl/image-10.png)


大功告成! 看來我也可以無痛的在 wsl 下面執行需要 CUDA 的應用程式了，最後我弄了個 ollama + open-webui 的 ```docker-compose.yaml``` (可以參考黑大的範本: [傻瓜 LLM 架設 - Ollama + Open WebUI 之 Docker Compose 懶人包](https://blog.darkthread.net/blog/ollam-open-webui/))，無痛就起了一個私人的類 ChatGPT UI...

![alt text](/images/2024-11-11-working-with-wsl/image-11.png)


這條路打通，開始很多需要靠 GPU 的應用就都隨手可得了。拿個 ```docker-compose.yaml```，執行 ```docker compose up -d``` , 就能啟動完整的服務, 要跑 ollama, vllm, stable diffusion 以及各種好用的 UI 都不是問題了。



## 4-2, WSL + GPU 的冷知識

為了研究這些，其實我還翻了不少技術文件，我就不一一解釋了，這跟工作環境無關，但是搞清楚背後的原理其實還蠻有趣的，我就當作冷知識貼在下方，沒興趣的可以直接跳過這一段 XDD


想了解全貌的，我推薦這篇: [DirectX is coming to the Windows Subsystem for Linux](https://devblogs.microsoft.com/directx/directx-heart-linux/), Microsoft 官方文件, //Build/2020 公開的內容，這麼大範圍的整合，如果不是在一家公司內應該很難做得到吧.. 從 windows driver, hyper-v, guest os ( linux driver ), runtime ( open cl, direct x , cuda ), container, application 等等都要顧到.. 還好在 windows 的世界, Microsoft 做到這一點了..

雖說沒什麼人期待 Linux 上面能跑 DirectX (咦?)... 不過整個架構推動策略的脈絡很清楚，DirectX for Linux 只是剛剛好而已.. 我看完文章後我覺得脈絡式這樣:

**GPU Virtualization**:  
核心重點仍然是虛擬化, GPU Virtualization 是首要任務。要做到這件事，最重要的就是 Host OS ( windows ) 端的 driver 支援, WDDM 2.9+ 的 GPU driver 是必要條件。  

**VM 內的 GPU: /dev/dxg**:  
Guest OS 會有對應的虛擬化的硬體, 在 Linux 下就是 ```/dev/dxg``` (我猜 dxg 是指: DirectX Graphics, 因為 Microsoft 在多個地方都用到這名詞，例如 [DXGI](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) - DirectX Graphics Infrastructure, [DXGKNL](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/directx-graphics-kernel-subsystem?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155) - DirectX Graphics Kernel Subsystem) 這個 device, Microsoft 直接為了這個虛擬 GPU 寫了 driver, 然後這路線就打通了

![alt text](/images/2024-11-11-working-with-wsl/image-12.png)


**GPU 對應的涵式庫**:

GPU 虛擬化打通之後，Microsoft 第一件事是拿 Direct X 的 source 在 linux 下重新編譯, 宣稱能在 Linux 下提供了 100% 相容的 DxCore / D3D12 API... 我猜沒有多少人有興趣在 Linux 下面用 D3D 啦... 不過除了宣示意味之外，我覺得跟 .NET 跨平台後，很多應用沒辦法跨平台的窘境會因為這些涵式庫一個一個打破，例如 WPF 這類應用。

在 AI 的領域，DirectML 就是一例，上半年看到的 [Windows Copilot Runtime](https://learn.microsoft.com/en-us/windows/ai/overview?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155), 提到了 OnnxRuntime 能在 DirectML 上面執行，對應的模型都能輕易的在 .NET 應用程式內啟動了。我當時看到這新聞，第一件事就是:

> 那這樣的 .NET 程式還能在 container 執行嗎? 

看來，四年前的 //Build 就給我答案了，Direct ML 也能被移植到 WSL.. 我相信這範圍的應用會比 D3D 來的吸引人。

![alt text](/images/2024-11-11-working-with-wsl/image-13.png)


除了 DirectX 系列的移植，其他 AI 運算涵式庫，最大宗的就是 CUDA 了，其他還有 OpenGL, OpenCL 等等, 也都循同樣路徑, 從 DxCore 開始來轉換提供相容性。從架構圖來看, 轉換的架構略有不同，不過結果很簡單，就是 WSL 也能用到 GPU 資源了。看完這個架構，我才理解，為何我在處理 WSL 下跑 CUDA 應用的時候，好幾份文件都強調:

> 要安裝正確的 GPU **windows** driver, 不要在 WSL 內安裝任何的 linux graphic driver ...

原來就是這個原因，因為關鍵都在啟動 GPU 虛擬化.. 這關打通後，後面的其實都一樣，WSL 直接內建了。真正要裝在 WSL 內的應該是 Microsoft 替 ```/dev/dxg``` 寫的 driver, 而不是 GPU 原廠寫的 driver 啊

最後捕兩張圖: OpenGL, OpenCL 等套件, 是透過 mesa library 來實作的:
![alt text](/images/2024-11-11-working-with-wsl/image-14.png)

而 CUDA 的堆疊路徑有點差別, 直接從 DxCore 對應而來:
![alt text](/images/2024-11-11-working-with-wsl/image-15.png)


**GUI 應用程式**:

最後一個，直接在 WSL 上面執行有 GUI 的應用程式... 這件事 Microsoft 也打通了，只是我這次沒用到，不過為了主題完整，我依樣把我研究過相關的題目列一下吧，有興趣的自己在往下挖。這關卡打通了後，你可以直接在 WSL 內執行有 GUI 的相關應用程式，而 GUI 的部分，則會無縫的直接在 windows 下顯示出來。當年我還在念書的年代，用的是 x11, 你可以指定 x11-display, 決定你開啟的 x-windows 要顯示在哪個終端機 (那個終端機會看到畫面，也可以用那台終端機的鍵盤滑鼠)。基本上 WSLg 也是把這件事跟 windows 整合完成了。

之前看這相關主題時，關鍵字都是 WSLg, 現在好像沒特別再提 WSLg 這關鍵字了。直接看這篇: [Run Linux GUI apps on the Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps?source=docs&WT.mc_id=email&sharingId=AZ-MVP-5002155)


Windows Subsystem for Linux (WSL) now supports running Linux GUI applications (X11 and Wayland) on Windows in a fully integrated desktop experience.

WSL 2 enables Linux GUI applications to feel native and natural to use on Windows.

- Launch Linux apps from the Windows Start menu
- Pin Linux apps to the Windows task bar
- Use alt-tab to switch between Linux and Windows apps
- Cut + Paste across Windows and Linux apps

You can now integrate both Windows and Linux applications into your workflow for a seamless desktop experience.

![alt text](/images/2024-11-11-working-with-wsl/image-16.png)


# 5, 心得

從 2014 Satya Nadella 接任 Microsoft CEO, 開始喊 "Microsoft Love Linux" 開始, 到現在 10 年了, 真心佩服他有辦法把 windows 生態系改造成現在這個樣子, windows 終究不是 linux, 但是兩個異質的作業系統, Microsoft 能 (願意) 整合到這種程度也是挺了不起的..

![alt text](/images/2024-11-11-working-with-wsl/image-17.png)
> 果然 Microsoft 要有愛才能做到這程度啊

當年寫的這篇: [[架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?](/2016/05/05/archview-net-open-source/)，看起來預測的每件事情都逐步實現了。Visual Studio 已經可以直接編譯 & 測試 Linux APP 了，.NET 真的也擴展到 Linux 及 IoT 等領域, VS Code 已經是各平台的 IDE 首選了。而這篇講的工作環境整合，則是說明 windows 已經可以成為 linux 的開發環境了。

雖然還不及 MacOS 那樣的體驗，但是整合度夠高，效能跟體驗夠好，足以變成我日常的工作環境，這樣就夠了。