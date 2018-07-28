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




