---
layout: post
title: "Azure Labs: Mixed-OS Docker Swarm"
categories:
tags: ["Docker", "Windows Container", "Swarm"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/07/maxresdefault.jpg
---

![](/wp-content/uploads/2017/07/maxresdefault.jpg)

接下來就玩大一點，前一篇都講到，既然將來 container 會是 software 統一的發行途徑了, 那麼只有 windows 怎麼夠用?
延續前面的 labs environment, 我們就接著把 linux 加進來吧~

其實，去年在寫這篇 [架構師觀點: .NET 開發人員該如何看待 Open Source Solutions?](/2016/05/05/archview-net-open-source/) 的文章時，我就有這個想法了。文內提到 stackoverflow.com 的架構, 採用個別 domain 最好的 solution, 而不是先被某個 os 或是 framework 限制住選擇。因此 stackoverflow.com 選擇了一個混搭 windows + linux 的架構。

![](/wp-content/uploads/2017/07/img_572b734171d80.png)

這類架構，在過去的開發環境內，真的是來折磨開發人員的。開發不外乎要建立測試環境，想想看你有辦法很容易地在你的 PC 建立一個同樣的
架構嗎? Sure.. 弄個 VM 當然沒問題，只是要讓每個人都能很快地架起來，他的門檻實在不低啊，再加上裡面的服務都要 update to date, 就更
吃團隊的開發流程與 CI/CD 是否確實了。如果你的環境都已經容器化, 那剩下的就是找個能同時丟 linux 及 windows container 進去執行的環境了。

這願景已經可以實現一半了 :D，較正式的部署 (例如開發團隊共用的 DEV environment, 或是 Production environment), 可以建立一個
Mixed-OS docker swarm, 也就是本篇 labs 要介紹的。另一個就是等 Microsoft 在今年 dockercon 2017 宣布的下一個年度更新 [Microsoft to allow Linux containers to run on Windows Server](https://siliconangle.com/blog/2017/04/19/microsoft-plans-use-hyper-v-run-linux-containers-windows-server/) 釋出之後，你就
可以在自己的開發機，用 docker-compose 一次就把整個開發環境建立起來，不論背後是跑 windows or linux。

不論如何，這一切都是以 container 為核心架構的，現在投資這技術永遠不嫌晚，看下去就對了!


<!--more-->

整個環境，延續上一篇 [Azure Labs: Windows Container Swarm](/2017/07/25/wc-swarm-labs/) 的環境。若想按照順序做，請從上一篇開始。我用簡單的一張意示圖來說明這次要建置的環境:

![](/wp-content/uploads/2017/07/2017-07-30-18-54-47.png)

其中 wcs1 ~ wcs3, 還有 ingress 都是上一篇建立起來的 docker swarm 環境。我們也透過 docker swarm 的管理機制，把 ASP.NET MVC 的 DEMO 放上去執行了。這次目的是要追加 Linux Node, 同時也把 Linux Apps (NGINX) 放上去執行。

# Add Linux Node

這個步驟，多虧 Microsoft 這次支援容器技術，沒有另外 create 一整套自己的 API 與 ECO system, 拜完全的 API 相容所賜, 在 Docker Swarm 內追加一個 Linux Node 的作法，完全跟追加 Windwos Node 一模一樣 (啊? 應該是 windows node 完全跟 linux node 一樣才對吧?)

程序是一樣的，我先在 Azure 上面，加了第四台 VM，命名為 lcs4, 使用 ubuntu server + docker .. 建置 VM 的過程我就略過了。
只要確保你建置的過程沒有手殘，弄到不同的 VLAN 下就好了。我曾經恍神，選到 classic 的 VM，結果是完全另一個 virtual network 啊 (IP 一樣 10.0.0.0/24)，結果怎樣都 ping 不到...

![](/wp-content/uploads/2017/07/2017-07-30-19-03-44.png)

在 swarm manager node (wcs1) 下這道指令，就能查閱要讓其他 docker node 加入的指令。最關鍵的就是 Token 的內容了。
要加入新的 worker node, 或是 manager node, 使用的 Token 是不一樣的。直接看指令跟執行的結果:


```text
C:\Users\andrew>docker swarm join-token
"docker swarm join-token" requires exactly 1 argument(s).
See 'docker swarm join-token --help'.

Usage:  docker swarm join-token [OPTIONS] (worker|manager)

Manage join tokens

C:\Users\andrew>docker swarm join-token worker
To add a worker to this swarm, run the following command:

    docker swarm join \
    --token SWMTKN-1-24jeip7lhisepualtg7mjbf7nqv9zv8grcxhwz9mvgrj53ow6b-6wkrvgnvz8zlhpi5nhv773hrw \
    10.0.0.4:2377


C:\Users\andrew>docker swarm join-token manager
To add a manager to this swarm, run the following command:

    docker swarm join \
    --token SWMTKN-1-24jeip7lhisepualtg7mjbf7nqv9zv8grcxhwz9mvgrj53ow6b-f2jmuiwkvhriitrqqyrrzm0oy \
    10.0.0.4:2377
```

把對等的指令，貼到 linux console 就可以了。成功的把 LCS4 加入 swarm 之後，我在 WCS1 (manager) 上面查詢所有節點:

```text
C:\Users\andrew>docker node ls
ID                           HOSTNAME  STATUS  AVAILABILITY  MANAGER STATUS
4hlsads3z14yoms1goqtejxc9    wcs2      Ready   Active
iwcsb37iox899qfhhch9rzr6m    lcs4      Ready   Active        Reachable
lnu2qjg2jxttxkn6wgx9t0a2l *  wcs1      Ready   Active        Leader
rvg17p5wwrauvduga9uivmiay    wcs3      Ready   Active
```

可以看到整個叢集已經有四個 node 了。到此為止，環境準備大功告成，可以繼續後面的步驟了 :D


# Add OS Label

接下來有些陷阱要注意了。整個 cluster 有了兩種類型的 OS，問題就開始變複雜了。我在 cluster 內追加一個 linux container 的 service,
docker swarm 並不會那麼聰明的替你辨識 OS 版本，manager 會把這個 task 按照規則分配給 nodes 去執行，如果 OS type 不對，只會收到
create container 失敗的回應。然而 cluster 會有修復機制，會嘗試替你重新啟動，於是你會浪費很多資源在這些無謂的 retry 上面...

以下就是個 **錯誤** 的示範: 下了指令，用 nginx (linux) 這個 container image 建立一個服務，沒有指定個數 (預設: 1), 於是 docker swarm manager 替我安排給 wcs2 (windows node) 執行這個 task...

然而 wcs2 是 windows 無法成功建立這個 container, 就看到不斷的 retry... 短短 10 秒內就在嘗試建立第三次:

```text
andrew@lcs4:~$ sudo docker service create --name nginx nginx
qhekwtv209sz84ytegzedmsel
Since --detach=false was not specified, tasks will be created in the background.
In a future release, --detach=false will become the default.
andrew@lcs4:~$ sudo docker service ps nginx
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE             ERROR                              PORTS
ka3nelzehyzs        nginx.1             nginx:latest        wcs2                Ready               Preparing 2 seconds ago             
l7lx9g3hnas7         \_ nginx.1         nginx:latest        wcs2                Shutdown            Rejected 3 seconds ago    "No such image: nginx@sha256:7…"
yjtqrndy04vm         \_ nginx.1         nginx:latest        wcs2                Shutdown            Rejected 7 seconds ago    "No such image: nginx@sha256:7…"
andrew@lcs4:~$
```

正確的方式，你可以事先替 nodes 下標籤 (label), 然後再 create service 時，下指令告訴 manager 該用什麼規則去分配 task 該在哪個 node 執行。意思是你必須明確的安排好這些細節才行。

這邊我舉[官方文件: Getting Started with Swarm Mode](https://docs.microsoft.com/en-us/virtualization/windowscontainers/manage-containers/swarm-mode#linuxwindows-mixed-os-clusters)的範例:
1. 先替每個 node 加上 os 這個 label, 分別標記 windows or linux 的內容
1. 建立 service 時，加上限制 (constraint), 只限於標記 os 為 linux 的節點才能執行

好，來看執行範例:

```text
andrew@lcs4:~$ sudo docker node ls
ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS
4hlsads3z14yoms1goqtejxc9     wcs2                Ready               Active
iwcsb37iox899qfhhch9rzr6m *   lcs4                Ready               Active              Reachable
lnu2qjg2jxttxkn6wgx9t0a2l     wcs1                Ready               Active              Leader
rvg17p5wwrauvduga9uivmiay     wcs3                Ready               Active

andrew@lcs4:~$ sudo docker node update --label-add os=windows wcs1
wcs1

andrew@lcs4:~$ sudo docker node update --label-add os=windows wcs2
wcs2

andrew@lcs4:~$ sudo docker node update --label-add os=windows wcs3
wcs3

andrew@lcs4:~$ sudo docker node update --label-add os=linux lcs4
lcs4
```

完成之後，每個 node 都會有個名為 "os" 的標籤 (label)，內容不是 "windows" 就是 "linux"。
接下來執行的時候你可以用這樣的方式 ```--constraint 'node.labels.os==linux'```，告訴 docker swarm 你的分配規則, 只有 node.labels.os 為 linux 才符合條件。請 docker swarm manager 在這條件之下分配 task 要在哪個 node 上面執行。


執行結果:

```text
andrew@lcs4:~$ sudo docker service create --name web --network ingress --replicas 3 -p 80:80 --constraint 'node.labels.os==linux' nginx

cp3xcsnpvq2m6ju85v08zn0mf
Since --detach=false was not specified, tasks will be created in the background.
In a future release, --detach=false will become the default.
andrew@lcs4:~$
andrew@lcs4:~$
andrew@lcs4:~$ sudo docker service ls
ID                  NAME                MODE                REPLICAS            IMAGE                                PORTS
cp3xcsnpvq2m        web                 replicated          3/3                 nginx:latest                         *:80->80/tcp
pzziyu0gp62w        mvcdemo             replicated          5/5                 wcshub.azurecr.io/vs20:latest
qfz35hd259w2        console             replicated          3/3                 microsoft/windowsservercore:latest
tspoz3pevo0l        ssh                 replicated          1/1                 busybox:latest
andrew@lcs4:~$ sudo docker service ps web
ID                  NAME                IMAGE               NODE                DESIRED STATE       CURRENT STATE            ERROR               PORTS
gkgjmy7jr5mk        web.1               nginx:latest        lcs4                Running             Running 10 seconds ago              
sezkbujza758        web.2               nginx:latest        lcs4                Running             Running 11 seconds ago              
9x3dbu3tx2xj        web.3               nginx:latest        lcs4                Running             Running 11 seconds ago              
```

可以看到，nginx 我要求要執行三個 instance, docker swarm 都很精確地把他安排在 linux node (lcs4) 上面執行。

我還沒準備 linux 版本的 demo, 暫時還看不到 3 個 nginx container 透過 routing mesh 切換的結果，不過我開瀏覽器連到 lcs4 的 public ip address, 可以正確的尋訪到 nginx 的服務內容:

![](/wp-content/uploads/2017/07/2017-07-30-19-34-50.png)

看來就真的等 windows container 也支援 routing mesh 的那天了啊... 希望那個 "coming soooooon" 真的很快會來臨 :D


# DNSRR 驗證

其實我補這段 Mixed-OS 的 Labs, 還有另一個目的，就是搞清楚上個 Labs 測不出來的 DNSRR 機制。我想知道到底是 windows container 支援不足? 還是我的使用方式不對?

同樣方式，我依樣畫葫蘆，我在 linux 開了 ssh 這個 service:

```text
sudo docker service create --name ssh --endpoint-mode dnsrr --network ingress --constraint 'node.labels.os==linux' busybox sleep 86400000
```

我選了 busybox 這個 container, 讓他睡個 86400 sec, 好讓我有時間 exec 進去測試..


先查詢 container id (要找 busybox 那個, id 是 c9b79f59fe):

```text
andrew@lcs4:~$ sudo docker ps -a
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS               NAMES
f095ab9a7a0f        nginx:latest        "nginx -g 'daemon ..."   8 minutes ago       Up 8 minutes        80/tcp              web.3.9x3dbu3tx2xjml3qudg6ndjhg
9e560dc238bc        nginx:latest        "nginx -g 'daemon ..."   8 minutes ago       Up 8 minutes        80/tcp              web.1.gkgjmy7jr5mksjeq6k9f7vifp
5bdb896016eb        nginx:latest        "nginx -g 'daemon ..."   8 minutes ago       Up 8 minutes        80/tcp              web.2.sezkbujza7588xwh260lemzha
c9b79f59fe6c        busybox:latest      "sleep 86400000"         2 hours ago         Up 2 hours                              ssh.1.boim4e8zcyfc2hkvyx9zf0g6b
```

測試 ping mvcdemo 其中一個 container (10.255.0.11), 看看是否在 network: ingress 同網段內:

```text
andrew@lcs4:~$ sudo docker exec -t -i c9b7 busybox ping 10.255.0.11
PING 10.255.0.11 (10.255.0.11): 56 data bytes
64 bytes from 10.255.0.11: seq=0 ttl=64 time=0.201 ms
64 bytes from 10.255.0.11: seq=1 ttl=64 time=0.087 ms
64 bytes from 10.255.0.11: seq=2 ttl=64 time=0.073 ms
64 bytes from 10.255.0.11: seq=3 ttl=64 time=0.069 ms
64 bytes from 10.255.0.11: seq=4 ttl=64 time=0.069 ms
^C
--- 10.255.0.11 ping statistics ---
5 packets transmitted, 5 packets received, 0% packet loss
round-trip min/avg/max = 0.069/0.099/0.201 ms
```


測試通過，可以 ping 的到。網路連接沒問題。接著測看看 DNS lookup。用內建的 Docker Native DNS (IP: 127.0.0.11)
分別查詢 windows container 的 service: mvcdemo | console:

```text
andrew@lcs4:~$ sudo docker exec -t -i c9b7 busybox nslookup mvcdemo
Server:    127.0.0.11
Address 1: 127.0.0.11

nslookup: can't resolve 'mvcdemo'

andrew@lcs4:~$ sudo docker exec -t -i c9b7 busybox nslookup console
Server:    127.0.0.11
Address 1: 127.0.0.11

nslookup: can't resolve 'console'
```

查不到 DNS 紀錄，看來 linux node 一樣查不到。接著再看看 linux node 本身的 service (ssh 跟 nginx 兩個 service):

```text
andrew@lcs4:~$ sudo docker exec -t -i c9b7 busybox nslookup nginx
Server:    127.0.0.11
Address 1: 127.0.0.11

nslookup: can't resolve 'nginx'


andrew@lcs4:~$ sudo docker exec -t -i c9b7 busybox nslookup ssh
Server:    127.0.0.11
Address 1: 127.0.0.11

nslookup: can't resolve 'ssh'
```

Orz, 看來情況也沒比較好啊 @@
不過這邊跟 windows container 相比，有一點點進步，至少按照規格，Docker Native DNS 位於 IP: 127.0.0.11 這件事，在 linux 上面
是存在的，至少 TCP/IP 有正確的設定 DNS IP, 同時這 IP 也有查詢結果回來，只是查不到紀錄而已。

但是在 windows container 的狀況下，ping 的到 127.0.0.11, 但是 nslookup 卻無法對她查詢，看來上面沒有正確 bind DNS 這個 service..

這個問題到目前為止，看來還是沒有頭緒。我是相信我自己應該漏掉了部分細節了才對。若有朋友們知道正確的方式，歡迎跟我聯絡~
不論是在[Facebook粉絲團](https://www.facebook.com/andrew.blog.0928/)留話給我，或是在這篇底下回覆，甚至是你願意的話可以直接提 Pull Request 給我 (我的部落格是直接放在 [GitHub](https://github.com/andrew0928/columns.chicken-house.net) 上的，修改 MD 檔案就可以立即更新文章內容)~



# MS 官方的 DEMO 怎麼做? (2017/07/31 補充)

上面提到的 [官方文件: Getting Started with Swarm Mode](https://docs.microsoft.com/en-us/virtualization/windowscontainers/manage-containers/swarm-mode#linuxwindows-mixed-os-clusters) 裡面，有擺了 Microsoft Container Network Team 的 Program Manager 作的三段 Demo Videos, 主題就剛好是我這兩篇探討的內容。

![](/wp-content/uploads/2017/07/2017-07-31-00-28-43.png)

第三段就是講透過 nginx 來做 web load balance, 枉我很認真地看完這三段在幹嘛... 結果當我看到這畫面時，我就... 就...
就崩潰了 XDD, 看看這段 nginx conf 的內容:

![](/wp-content/uploads/2017/07/2017-07-31-00-30-53.png)

影片 [位置](https://youtu.be/I9oDD78E_1E?t=430): 07:20 處

哪有人這樣弄得啦... 原來這 PM 是另外弄第四個 windows server (不再 docker swarm cluster 內), 單純只跑 nginx, 編輯 nginx.conf, 設定上面三個 web app instance 的動態 ports 去做 load balance, 這樣是會動沒錯拉，要是上線要這樣叫我搞，我應該會被砍吧! 只要增加一個 node, config 就要改一次... server 重開機, container restart 的話, ports 有變
nginx 也要重新 config 一次...

如果連 Microsoft 在做 windows container network 的 PM 都這樣 DEMO, 那我更相信這問題暫時是無解了 XDDD

看來我可以放心地等那個 "coming sooooon" 的 routing mesh... XD


# 總結

這兩篇 Labs 就先告一段落，有興趣嘗試看看地都可以直接在 Azure 上面體驗看看 :) 免費的 6300 元額度很夠用的，我這兩天包含測試跟寫文章
都開著，結算到目前為止也花了 600 而已... 免費額度的 1/10 不到。如果你還在觀望的話，真的不用再多想了，開始動手才是正途...

我的總結還是一樣，這篇是個 windows container 踩地雷的過程。雖然沒辦法有立即的效益，但是對於你了解背後的細節是絕對有幫助的。我一
直有個明確的目標，就是將來我的 Legacy .NET Application, 一定是要透過 container 的技術來部署的，因此目前碰到的困難，我都當成是將來
能夠協助我破除障礙的訓練，越早經歷過我就能比別人更有效率的解決這些架構問題 :D

也許將 .NET framework 轉移到 .NET core 也是一條路，但是我在業界的開發團隊待很久了，我很了解一件事，就是全面改寫 code 這件事
是很難實現的，你永遠有一堆現實的原因沒辦法讓你把整個 code 都翻過來。因此我比較奉行 microservice 的理念，就是容許異質系統互相
協同合作。即使 .NET core 是將來的方向，眼前的 5 ~ 10 年，一定還會繼續面對 Windows v.s. Linux 的課題 (話說，連 ASP 現在都還有
人在用不是嗎? XDD)，現在先做好準備，絕對是個值得的投資!

我一直期望軟體開發人員，都能夠用最好的工具，最好的架構，最好的環境去開發系統。在 container 之前，我們總是為了 language, framework, OS, IDE ... 等等問題纏住，兩年前開始把希望寄託在 .NET core + Docker, 一年前開始關注 Windows Container, 到今天做完
這個 Labs, 我真的開始覺得這一天就要來了。當這天來臨時，你是否已經準備好了嗎?

