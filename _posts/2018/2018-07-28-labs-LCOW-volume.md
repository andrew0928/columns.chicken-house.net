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

我決定改掉過去都會講一堆故事的習慣了，這次直接從結果開始看。我測試的標的，就用我自己的部落格，用 Jekyll 官方的 [docker image](https://hub.docker.com/r/jekyll/jekyll/):2.4.0。我把簡單的測試條件先列一下:

測試網站: 安德魯的部落格 (https://github.com/andrew0928/columns.chicken-house.net)
----
* repo 大小:   549mb, 4778 files
* source 大小: 278mb, 3604 files
* 文章大小:    308 篇 (.md 跟 .html), 共 3.12mb


測試環境 #1: LCOW
----
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

測試環境 #2: LCOW
----
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

測試環境 #3: LCOW
----
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



測試環境 #4: Docker for Windows
----
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




測試環境 #5: Docker for Windows
----
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





測試環境 #6: Docker for Windows
----
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




