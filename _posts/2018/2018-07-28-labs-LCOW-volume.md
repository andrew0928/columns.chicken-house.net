---
layout: post
title: "有雷! 使用 LCOW 掛載 Volume 的效能陷阱"
categories:
tags: []
published: false
comments: true
redirect_from:
logo: 
---

有時候，無知就是福啊... 沒想到我也默默忍受了這個地雷一年多了都沒發現。Container 透過 volume 掛載儲存空間到容器內部，會有一定的效能折損是一定的。然而 container 本身透過 [AUFS](https://philipzheng.gitbooks.io/docker_practice/content/underly/ufs.html) 也有一定的效能折損啊。原本很天真的想: 我都在本機使用，想想應該不會差到哪裡去，直到膝蓋中了一箭... 

事情要回顧到兩年前，我[開始把 Blog 搬到 GitHub Pages 上面](/2016/09/16/blog-as-code/)來開始說起... 當時為了避開 Ruby for Windows 地獄，我一直用 Docker for Windows 跑 Jekyll 在我自己 PC build website 測試，直到前一陣子突然想用 LCOW 來替代，才意外發現 volume 跟 container 內部的 I/O 效能有天跟地的差別...

# LAB1, 測試不同環境下 jekyll 建置時間

我決定改掉過去都會講一堆故事的習慣了，這次直接從結果開始看。我測試的標的，就用我自己的部落格，用 Jekyll 官方的 [docker image](https://hub.docker.com/r/jekyll/jekyll/):2.4.0。測試的紀錄跟數據有點囉嗦，我列在這段的最後面，有興趣的讀者們再去看就好。我直接先來解讀 LAB1 的測試結果。

測試的方式很簡單，同樣的 Jekyll 官方版本 docker image, 我分別用 docker for windows 與 LCOW (linux container on windows) 兩種環境，並且把 source 與 destination 分別放在 volume 與 container 內部測試。我測試了這三種組態:
1. source 擺在 volume, destination 擺在 volume
1. source 擺在 volume, destination 擺在 container
1. source 擺在 container, destination 擺在 container

這樣安排的目的，就是先前踩了一堆雷之後，我想觀察不同的 container engine 對於不同的 storage 處理方式，對 Jekyll build website 的效能差異到底有多大?

測試結果我列成這張表:

|   |volume -> volume|volume -> container|container -> container|
|:--|----------------:|-------------------:|----------------------:|
|LCOW| (#1), 無法測試 |(#2),135.493s|(#3),12.86s|
|Docker|(#4),120.368s|(#5),35.763s|(#6),12.11s|


其中比較特別的，是測試環境 #1, LCOW (volume -> volume) 這個測試。同一個 docker image, 理論上執行環境應該都是一樣的才對，但是在 LCOW 上面卻跑到一半就有錯誤訊息，試了不下數十次，每次都停在不同的檔案無法寫入的問題上。同時 volume -> container 的這組測試，兩種 container engine 表現出來的效能差異也頗大，令我訝異。看來兩種 engine 對於跨越 windows host -> linux host 之間的 volume 處理方式差異很大，不但對效能有影響，而且看來也對大量 I/O 下的某些行為 (我猜是 file lock release 時機之類的差異?) 也有不同，導致這些落差。

不過這些落差，影響我每次改完 code 要等多久才能預覽結果啊! 12sec 的落差我可以接受，135sec 這種就完全不行啊! 可是 LCOW 對我而言方便一些，因為我主要都是用 windows container 居多，能用 LCOW 的話我就不用一直切換了，我可以同時使用 windows 跟 linux 的 container。

因此，我決定繼續挖下去。我大概還沒什麼本事挖出真正的原因，不過我至少可以透過實驗，更精準的掌握差異點吧? 所以我就繼續進行了 LAB2, 直接用 disk benchmark 的工具下手，試著比較一下不同的執行環境，對於 container I/O 效能的差距。



# LAB2, 不同組態下 container 的 I/O 效率

前面 LAB1 是用實際的 scenario (Jekyll Build WebSite) 來當作評估的方式，但是如果單純想了解 I/O 上面的差異，比較好的方式是直接針對 I/O 進行測試。LAB2 就是要側這個東西，我找了 linux 內建的 dd 指令，也找了對應的 windows 版本 dd.exe 來當對照組，直接測試從 /dev/urandom 讀取 1M 的資料 1024 次，並寫入 container or volume 所要花費的時間。我分別用這幾種組態來測試:

1. windows container (isolation: process)
1. windows container (isolation: hyper-v)
1. linux container (isolation: hyper-v)
1. linux container (docker for windows, hyper-v)

這邊問題複雜了點，Microsoft 在 container 的架構設計上，支援了 --isolation 的選項，你可以選擇用預設的 process 隔離層級，可以得到最棒的效能；你也可以選擇 hyperv 的隔離層級，windows 會為你的 container 啟動專屬的 VM, 跑最精簡版的 OS (應該是 nanoserver 吧)。但是 windows 10 只支援 hyper-v 隔離層級的 container, 因此這實驗一定得在支援 hyper-v 的 windows server 上面才能測試。

類似的狀況也發生在 docker for windwos, docker for windows 也是靠建立一個 VM 來支援 linux container, 差別是 docker for windows 沒有整合在 OS 裡面，不是內建的而已。將來能夠繼續最佳化的空間也有限。老實說已一個 3rd party 的廠商來說，做到現在的程度已經很了不起了...。但是，依樣，拿 docker for windows 當對照組也是有點頭痛，只有 windows 10 能支援。我要在 windows server 1803 上面測 docker for windows 就很頭大了。

第三個則是財力問題，不是技術問題... 哈哈哈... 理論上我要是能準備多台硬體規格相同的 server, 或是我願意重灌 OS 來測試，上面的問題就不是問題了。不過我很懶啊... 於是把腦筋動到 Azure 上了。BUT !!! Azure 上面都是 VM, VM 還要再開啟 hyper-v ... 就有很多限制了，比如 VM 一定得用 D 系列，再來就是 VM 裡面在跑 hyper-v, 真的只是為了實驗或是相容性而已，實驗的結果證明這樣跑完全沒有經濟效益....



## 測試方式

由於硬體環境上的限制，沒辦法湊到所有環境都能用一樣的硬體來進行。因此我用一樣的 container, 一樣的測試工具, 一樣的參數來進行測試；測試結果我分成三組，每一組內的測試環境規格都是一模一樣的，因此同一組的數據可以讓你比較效能差異，不同組之間的比較的只能當作參考。

測試方式很簡單，我找了 linux 內建的指令: dd, 同時也找到對應的 dd for windows 版本，拿來當跨平台評估使用。我用這樣的指令來測試:

dd if=/dev/urandom of=./largefile bs=1M count=1024

簡單說明一下這行指令在幹嘛:
- if: input file, 指定 /dev/unrandom 讀取亂數的內容當作 source
- of: output file, 從 if 讀出的資料，會寫到 of 指定的目的地
- bs: block size, 讀取與寫入過程中用的 block size
- count: 重複執行次數

白話的說，這段指令會從 if 讀取 bs 大小的資料，寫到 of, 重複 count 次，依據花費時間就能評估寫入速度。這些參數都固定，因此底下的測試我都只標示執行時間。接下來，就是在各種環境下，分別啟動 windows container 與 linux container，記錄下執行上述測試的時間 5 次取平均值。

platform: 執行測試工具的 OS。可能的值有 windows | linux
isolation: 執行測試工具 OS 的隔離層級 (none 代表在本機上執行)。可能的值有: none | process | hyperv
of=container: 寫入 container 內的空間。
of=volume: 寫入由 host local disk 掛載進 container 使用的 volume


## 架構差異

真不知道該對 windows container 支援 hyperv isolation 同時還支援 linux (LCOW) 是褒還是貶? 雖然很方便，一台 windows server 可以通吃所有的需求；但是也讓問題變複雜了。光是這次要做這實驗，我就想了很久。技術架構上，我要面對幾種不同的組合:

1. 




# LAB2-1, Windows Server 1803 (實體PC)

硬體規格:


測試結果:

|platform|isolation|to container|to volume|
|--------|---------|------------|---------|
|windows|none|--|1.5673|
|windows|process|1.5724|1.6365|
|windows|hyperv|5.9010|2.2083|
|linux|hyperv|4.8470|21.3261|


# LAB2-2, Windows 10, 1803 (實體PC)
硬體規格:


測試結果:
|platform|isolation|to container|to volume|
|--------|---------|------------|---------|
|windows|none|--|3.11617|
|windows|hyperv|4.5774|5.6002|
|linux|hyperv(LCOW)|6.3755|41.1397|
|linux|hyperv|6.2241|9.1047|

# LAB2-3, Azure D4S (Linux VM, Windows Server 1803 VM)
硬體規格:


測試結果:

|platform|isolation|to container|to volume|
|--------|---------|------------|---------|
|windows|none|--|2.1890|
|windows|process|2.0567|2.1264|
|windows|hyperv|66.8226|3.3977|
|linux|hyperv|52.5351|59.9209|
|||||
|linux|none|--|6.3952|
|linux|process|6.5074|6.5207|







# 結論





# 附錄: LAB1 實驗結果


## 測試網站: 安德魯的部落格
* repo:        https://github.com/andrew0928/columns.chicken-house.net
* repo 大小:   549mb, 4778 files
* source 大小: 278mb, 3604 files
* 文章大小:    308 篇 (.md 跟 .html), 共 3.12mb

## 測試環境 #1: LCOW (volume -> volume)

* Image:  Jekyll 2.4.0
* Source: volume
* Destnation: volume
* Build Time:  68.52 sec (測試中斷) (碼表)

Logs:
```log
ruby 2.5.1p57 (2018-03-29 revision 63029) [x86_64-linux-musl]
Configuration file: /srv/jekyll/_config.yml
Configuration file: /srv/jekyll/_config.yml
            Source: /srv/jekyll
       Destination: /srv/jekyll/_site
 Incremental build: enabled
      Generating...
jekyll 3.4.3 | Error:  Operation not permitted @ apply2files - /srv/jekyll/_site/assets/js/jquery-ui.js
```

每次中斷的時間跟位置都有點不同，我做了幾次實驗，看來是隨機的:

```
jekyll 3.4.3 | Error:  Operation not permitted @ apply2files - /srv/jekyll/_site/assets/js/jquery.toc.js
jekyll 3.4.3 | Error:  Operation not permitted @ apply2files - /srv/jekyll/_site/assets/js/jquery-ui.js
jekyll 3.4.3 | Error:  Operation not permitted @ apply2files - /srv/jekyll/_site/assets/images/qrcode.jpg
jekyll 3.4.3 | Error:  Operation not permitted @ apply2files - /srv/jekyll/_site/assets/images/octocat-spinner-32-EAF2F5.gif
jekyll 3.4.3 | Error:  Operation not permitted @ apply2files - /srv/jekyll/_site/assets/images/octocat-spinner-16px.gif
...
```


## 測試環境 #2: LCOW (volume -> container)

* Image:  Jekyll 2.4.0
* Source: volume
* Destnation: container
* Build Time:  135.493 sec

Logs:
```log
ruby 2.5.1p57 (2018-03-29 revision 63029) [x86_64-linux-musl]
Configuration file: /srv/jekyll/_config.yml
Configuration file: /srv/jekyll/_config.yml
       Deprecation: You appear to have pagination turned on, but you haven't included the `jekyll-paginate` gem. Ensure you have `gems: [jekyll-paginate]` in your configuration file.
            Source: /srv/jekyll
       Destination: /tmp
 Incremental build: enabled
      Generating...
                    done in 135.493 seconds.
 Auto-regeneration: enabled for '/srv/jekyll'
Configuration file: /srv/jekyll/_config.yml
    Server address: http://0.0.0.0:4000/
  Server running... press ctrl-c to stop.
```


## 測試環境 #3: LCOW (container -> container)

* Image:  Jekyll 2.4.0
* Source: container
* Destnation: container
* Build Time:  12.86 sec (碼表)

Logs:
```log
/srv # jekyll s --watch --drafts --source /tmp/source --destination /tmp/site --unpublished
Configuration file: /tmp/source/_config.yml
            Source: /tmp/source
       Destination: /tmp/site
      Generating...
                    done.
 Auto-regeneration: enabled for '/tmp/source'
Configuration file: /tmp/source/_config.yml
    Server address: http://0.0.0.0:4000
  Server running... press ctrl-c to stop.
```



## 測試環境 #4: Docker for Windows

* Image:  Jekyll 2.4.0
* Source: volume
* Destnation: volume
* Build Time: 120.368 sec

Logs:
```log
Configuration file: /srv/jekyll/_config.yml
Configuration file: /srv/jekyll/_config.yml
            Source: /srv/jekyll
       Destination: /srv/jekyll/_site
 Incremental build: enabled
      Generating...
                    done in 120.368 seconds.
 Auto-regeneration: enabled for '/srv/jekyll'
Configuration file: /srv/jekyll/_config.yml
    Server address: http://0.0.0.0:4000/
  Server running... press ctrl-c to stop.
```




## 測試環境 #5: Docker for Windows

* Image:  Jekyll 2.4.0
* Source: volume
* Destnation: container
* Build Time: 35.763 sec

Logs:
```log
Configuration file: /srv/jekyll/_config.yml
Configuration file: /srv/jekyll/_config.yml
            Source: /srv/jekyll
       Destination: /tmp
 Incremental build: enabled
      Generating...
                    done in 35.763 seconds.
 Auto-regeneration: enabled for '/srv/jekyll'
Configuration file: /srv/jekyll/_config.yml
    Server address: http://0.0.0.0:4000/
  Server running... press ctrl-c to stop.
```





## 測試環境 #6: Docker for Windows

* Image:  Jekyll 2.4.0
* Source: container
* Destnation: container
* Build Time: 12.11 sec  (碼表)

Logs:
```log
/srv/jekyll # jekyll serve --watch -s /tmp/src -d /tmp/dst
Configuration file: /tmp/src/_config.yml
            Source: /tmp/src
       Destination: /tmp/dst
      Generating...
                    done.
 Auto-regeneration: enabled for '/tmp/src'
Configuration file: /tmp/src/_config.yml
    Server address: http://0.0.0.0:4000
  Server running... press ctrl-c to stop.
```




