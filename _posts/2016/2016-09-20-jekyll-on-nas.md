---
layout: post
title: "Running Jekyll on NAS - 高效率的新選擇"
categories:
- "Tips"
tags: ["Jekyll", "NAS", "Docker", "Tips"]
published: true
comments: true
logo: /wp-content/uploads/2016/09/run-jekyll-on-nas-logo.png
---

自從發現了 GitHub Pages 這好用的服務，原來是源自 Jekyll 這 open source project 後，想說靜態網站產生器這麼好的東西，
怎麼沒人拿來用在 NAS 上? 與其在 NAS 貧弱的硬體上面，安裝 wordpress, 還不如在上面放靜態的 HTML 來的快速且安全。不過順手
Google 了一下，還真的沒什麼人這樣用，於是一時手癢，就...

<!--more-->

這篇算小品文章吧，延續[上一篇的長篇大論](/2016/09/16/blog-as-code/)，闡述 Blogging as Code 的理念，這邊只是補上在 NAS 上實作的步驟。老實說比我想像的簡單啊，
根本沒五分鐘就完成了，寫這篇只是留個紀錄...

# 用 Jekyll 當作開發文件管理系統

如果你還不知道這篇要幹嘛用的，可以先參考上一篇 [Blogging as code!](/2016/09/16/blog-as-code/), 上篇講到為何我想換成靜態網站的原因。這篇只是同樣的
東西，在 NAS 上架設而已。畢竟有些人可能不想東西都擺上 GitHub 被看光光... 有這種考量的話，在 NAS 上架設不失為一個好方法。

不過，反過來想，這東西拿來做專案開發的文件發布，其實蠻方便實用的，GitHub 本來就是讓你放 code 用的啊，code 跟 document 一起
放進版本控制系統管理，這真是天衣無縫的搭配啊。對開發人員來說，文件就兩種來源:

1. from code comments  
在程式碼的註解裡面 (EX: C# 的 /// 型態註解就是一例)，事後透過工具 compile 出對應的文件。
這種適合拿來做 API / Class library documentation

2. 其他需要人工維護的文件:  
如安裝手冊，規格說明等等，這類文件用 markdown 來寫，隨著 codes 一起放版本控制系統管理。

在過去，我都是用 (1), 在 daily build 時順便重建 API documentation, 至於 (2) 當年就都用 WORD，check-in 後就自動 deploy 到
小組用的網站，要看的人自己下載。不過用起來並不是很方便，現在把 (2) 用 markdown 一起放在 GitHub, 而 deploy 的部分則被 GitHub Pages
取代。基本上很無腦的，Code + Docs Push 上去之後，WEB 版的文件就自動更新好了，方便的很。


# 應用範例: MSDN - Windows Container Document

原本以為這是我自己的用法，沒想到 Microsoft 也這樣用啊! 無意間看到這些文件: 

[MSDN - Windows Containers Document](https://msdn.microsoft.com/en-US/virtualization/windowscontainers/deployment/deployment_nano?f=255&MSPPError=-2147217396)  

![](/wp-content/uploads/2016/09/run-jekyll-on-nas-msdn.png)

右上角的 "contribute" 點進去後，就會連到 GitHub.com 對應的 markdown 檔案。很有意思的是，你要投稿或是建議，直接 po issues, 或是
直接 pull request, 把你的修正丟上去，Microsoft 負責的人自然會替你 merge 上去，Jekyll 就自動接手發布內容的動作了。

為何我會這麼確定它 (MSDN) 也是用 Jekyll ? 因為每份文件前面都有一樣的 post header，太好認了，就像這樣:

```markdown
---
title: Deploy Windows Containers on Nano Server
description: Deploy Windows Containers on Nano Server
keywords: docker, containers
author: neilpeterson
manager: timlt
ms.date: 09/28/2016
ms.topic: article
ms.prod: windows-containers
ms.service: windows-containers
ms.assetid: b82acdf9-042d-4b5c-8b67-1a8013fa1435
---
```

這是我覺得最棒的應用案例了，我幾乎每天看的東西，我竟然現在才發現它也是用 Jekyll ... Orz... 案例看完，接著就直接來看
怎麼在家裡自己用 NAS 架設這樣的網站 :D


# 環境準備

我自己的 NAS 是 S 牌，後面就都用 S 牌當作案例了。不論你的 NAS 是白牌、S 牌還是 Q 牌，請[確認你的 NAS 支援 Docker](https://www.synology.com/zh-tw/dsm/app_packages/Docker) 就好了.. 我這邊
的架構很簡單，用 Docker 安裝 Jekyll, 監控 NAS 上的指定目錄，只要有任何檔案異動，就自動重新 Build 靜態的 website。

為了方便後面的描述，安裝的路徑我就定在 /docker/jekyll, 你編好的 website template 就放在這邊，你自己寫的文章，就放在 /docker/jekyll/_post 目錄下。
編譯好的網站目錄，預設會放在 /docker/jekyll/_site ，對應的網址，我用 http://columns-jekyll.chicken-house.net/ 。

Build 的 website 我也不需要再透過 Jekyll 發佈了，直接採用 NAS 內建的 Web Station 來發佈。畢竟專用的 web server 效率比 ruby 版
來的好的多，也可靠的多.. 如果 Jekyll 沒有執行，你的網站也不會掛掉，只要你的 NAS 還活著大概就沒事了。


# STEP 1. 架設 Jekyll (使用 docker)

![docker pull jekyll/jekyll:latest](/wp-content/uploads/2016/09/run-jekyll-on-nas-docker-pull.png)  
打開 S 牌的 DSM，打開 Docker 套件，先到 Registry 搜尋 Jekyll 官方的 container image: jekyll/jekyll:latest  

![docker volume setting](/wp-content/uploads/2016/09/run-jekyll-on-nas-volume-mapping.png)
下載完成後就可以用它建立 container 了，只要設定 volume 對應，把 NAS 的 /docker/jekyll 對應到 container 內的 /srv/jekyll 就可以了。
其他 network ports 都用預設值即可


# STEP 2. 把你的網站樣板 (含內容檔案) 複製到 NAS:/docker/jekyll

![jekyll template files](/wp-content/uploads/2016/09/run-jekyll-on-nas-files.png)
這步驟蠻無腦的，就是把檔案 COPY 過來 NAS 的目錄而已。
這邊的實作沒有像 GitHub Pages 一樣，搭配 Git Repository 當作 storage, 就是用一搬的 file system 而已。
當然你需要的話，還是可以把它放在 Git ，或是其他版本控制系統。或是你要用 NAS 內建的 backup 來保護它，甚至適用 Brtfs / ZFS
之類的檔案系統也行。總之顧好它就對了 XD

只是 file system 層級，頂多給你所有檔案的異動紀錄而已，讓你弄錯檔案還有機會還原回來。但是 file system 的版本控制能力
則遠遠不及 Git 這類的系統，你沒辦法追蹤，或是用分支等等的方式來控制。有這類需要，你還是要另外搭配版本控制系統來用會比較好。

當然，你自己的撰寫工具，還是可以用上一篇介紹的 visual studio code, 實在好用, 大推!

# STEP 3. 設定 NAS web station (對應目錄: /docker/jekyll/_site)

![web station](/wp-content/uploads/2016/09/run-jekyll-on-nas-webstation.png)
啟動 web station, 看你是要指定 domain name or port, 在 web station 建立你的 virtual host。
網站目錄請對應到 /docker/jekyll/**_site**, web server 我用 Nginx (個人喜好, 速度快)


# 測試結果

其實網站架設到現在就 OK 了... 這大概是我寫過最短的 Tips 文了... 如果是第一次使用，應該要等個一兩分鐘等 Jekyll 更新完
必要的 ruby gem 套件。不確定跑到哪裡了的話，可以開終端機確認，或是看看 docker container log 確定執行狀況。如果看到這段，那
就代表你網站檔案更新已經完成:

```text
Configuration file: /srv/jekyll/_config.yml
            Source: /srv/jekyll
       Destination: /srv/jekyll/_site
 Incremental build: disabled. Enable with --incremental
      Generating... 
                    done in 41.995 seconds.
 Auto-regeneration: enabled for '/srv/jekyll'
Configuration file: /srv/jekyll/_config.yml
    Server address: http://0.0.0.0:4000/
  Server running... press ctrl-c to stop.
```

有看到 Generating... done in xxxxx seconds. 字樣，就代表已經完成了。這時，如果你想在區網內用 Jekyll 自帶的 web server
驗證結果，可以看看 container 的 4000 port 被對應到 host 的哪個 port:
![ports](/wp-content/uploads/2016/09/run-jekyll-on-nas-ports-mapping.png)

用 Jekyll 自帶的 web server 測試，請用 http://{nas ip}:{host-map-port}
若你想用 web station 來測試，請用 http://{your domain name}
![result](/wp-content/uploads/2016/09/run-jekyll-on-nas-result.png)

結果你會發現，過去 NAS 為了省電，總是只給剛剛好夠用的 CPU / RAM (尤其 S 牌)，跑起 wordpress 之類的應用程式，是跑得動，但是
就是沒有 **飛快** 的感覺，現在這個是單純靜態的 HTML 網站，我想應該沒有比他更快的了吧? 所有內容都是點一下就出現... (Y)

那麼，build web site 的時間是否會很慢? 這點倒是也大出我意料之外.. 看來我之前用的 jekyll on docker for windows 的效能那麼糟糕，
應該有其他原因... 我拿 PC 上的 Jekyll for Win32 當對比:

**My PC**:  
- CPU: Intel i7-2600k  
- RAM: DDR3 24GB  
- DISK: Seagate Enterprise HDD 5TB / 7200RPM  
- Build Time: **30 seconds**  
  
**My NAS**:  
- Model: Synology DS-412+  
- CPU: Intel Atom D2701  
- RAM: DDR3 2GB  
- DISK: Seagate Enterprise HDD 5TB / 7200RPM  
- Build Time: **42 seconds**  
  
  
沒想到 CPU 差了這麼多檔次，結果效能也沒有差很多嘛，這對我來說其實已經可以接受了。真的有需要用 Jekyll, 不想放在 GitHub 上，想要自己
Hosting 在 NAS 的朋友可以試試喔。Blog 改用靜態網站，嫌以前用 wordpress 跑太慢的話，換這個你一定會滿意的 :D 