繼上次颱風天介紹的 [Mixed-OS Docker Swarm](/2017/07/25/wc-swarm-labs2/) 之後，適逢中秋節，那就再來一篇吧!

![](/images/2017-10-04-lcow/2017-10-04-22-47-00.jpg)

Microsoft 的 LCOW (Linux Container On Windows, 以下簡稱 LCOW) 推出後，Windows + Linux 的整合程度就更進一步了。Microsoft 願意這樣破釜沉舟的整合 Linux + Windows, 看來是下了很大的決心啊! 又進一步的讓 Windows 跟 Linux 的界線越來越模糊了。這是是在 Windows Container 的架構下，用原本就支援的 Hyper-V Container (簡單的說，為特定的 Container 準備一個獨立的 VM + 一套精簡的 OS，只為了執行 Container 使用的 OS 環境，來運行 Container), 進一步把裡面的 OS 從 NanoServer 換成 Linux Kit (或是 Ubuntu 也行), 讓 Windows Container 得到原生執行 Linux Container 的能力。

<!--more-->

聽起來很威，不過這也代表 Microsoft 已經下定決心了，秋季版的更新推出後，LCOW 會進一步取代掉 WSL (Windows Subsystem for Linux, 以下簡稱 WSL)，以前 WSL 是在 Windows Kernel 裡面動手腳，把 System Call 轉成對應的 Linux System Call, 得到原生執行 Linux Application 的能力，這次改版會用精簡一點的架構，改用 LCOW 替代了。相容性更好，架構更精簡，也更容易維護，同時也擴大了支援範圍，連同 Linux Container 也一併支援了。


# 準備測試環境

這篇其實我再等半個月，應該就有正式版可以用了，不過... 為了趕在 [.NET Conf](http://study4.tw/Activity/Details/9) 10/14 前完成，我就拿 Insider Preview 來試試吧。這次我測試的環境是:

*Windows 10 Pro + Insider Preview, Slow Ring Build 1709 (OS Build: 16299.0)*

上面安裝的 Docker for Windows 是 Edge 版本, 17.09.0-ce
不過 Docker Engine 則是另外從 GitHub 抓下來的版本: master-dockerproject-2017-10-03

安裝步驟我就省掉了，我是參考這篇:

* [Running Docker Linux Containers on Windows with LinuxKit](https://blog.docker.com/2017/09/preview-linux-containers-on-windows/)

簡單講，他的步驟只是從 GitHub 抓了新版支援 LCOW 的 docker daemon, 也另外先準備了 Linux Kit 的 Image, 然後用一般的 Docker Client, 連到這個另外安裝的 docker daemon 就可以啟用 LCOW 支援了。不過這次測試版，還無法同時支援 LCOW 跟 Windows Container, 需要的話你必須連到預設的 docker daemon 才行...

安裝好之後，我用預設的 docker daemon (來自 Docker for Windows Edge), 版本資訊如下:

```
C:\>docker version
Client:
 Version:      17.09.0-ce
 API version:  1.32
 Go version:   go1.8.3
 Git commit:   afdb6d4
 Built:        Tue Sep 26 22:40:09 2017
 OS/Arch:      windows/amd64

Server:
 Version:      17.09.0-ce
 API version:  1.32 (minimum version 1.24)
 Go version:   go1.8.3
 Git commit:   afdb6d4
 Built:        Tue Sep 26 22:50:27 2017
 OS/Arch:      windows/amd64
 Experimental: true

C:\>
```

支援 LCOW 的 docker daemon, 版本資訊如下:

```
C:\>docker -H "npipe:////./pipe//docker_lcow" version

Client:
 Version:      17.09.0-ce
 API version:  1.32
 Go version:   go1.8.3
 Git commit:   afdb6d4
 Built:        Tue Sep 26 22:40:09 2017
 OS/Arch:      windows/amd64

Server:
 Version:      master-dockerproject-2017-10-03
 API version:  1.34 (minimum version 1.24)
 Go version:   go1.8.3
 Git commit:   d65ab86
 Built:        Tue Oct  3 23:51:47 2017
 OS/Arch:      windows/amd64
 Experimental: true

C:\>
```

環境準備好之後，就可以開始體驗了! 使用方式跟過去一模一樣，唯獨要注意的是，這時 Windows 同時存在三套 Docker Engine ... 我有安裝 Docker for Windows, 因此就有預設的 Linux Container (Docker for Windows 自己用 VM 搞出來的) 及 Windows Container, 這個二選一，要從 Docker for Windows 切換。

另一套就是安裝過程中，額外啟動的 docker daemon, 跟前面的 Docker for Windows 是獨立的，你必須在 CLI 額外的指定 Host 才能連到它，例如:

```
docker -H "npipe:////./pipe//docker_lcow" version
```

# LAB1, Run BusyBox / Hello-World

其實我 Linux 指令不大熟，學校畢業後就沒怎麼在用 Unix 系列的 OS 了，真的進去 BusyBox 我也不曉得要幹嘛 XD

不過總是要試一下，前面環境準備好之後，這樣就可以開始了:

```
docker -H "npipe:////./pipe//docker_lcow" run -ti busybox sh
```

![](/images/2017-10-04-lcow/2017-10-04-22-00-37.png)

意思一下就好，證明真的可以跑起來就行了...。能用這樣無縫的方式直接在 Windows 執行 Linux Application, 真是特別的體驗啊! 

接著換一下以前裝好都要測試看看的 hello-world:

```
docker -H "npipe:////./pipe//docker_lcow" run hello-world
```

![](/images/2017-10-04-lcow/2017-10-04-22-04-05.png)


不過，為了讓大家體會，即使都是透過 VM 技術來執行 Linux App, 透過 Docker -> Hyper-V Container -> Linux Kit 的啟動速度到底有多快，我錄一段沒有剪接的 video 給大家體驗一下, 大概只要五秒鐘就執行完畢了:

<!-- <video 
    src="/wp-content/uploads/2017/10/2017-10-04-01-LaunchContainer-HelloWorld.mp4"
    style="max-width:100%;width:640;height:480;"
    controls>
</video> -->
<iframe width="560" height="315" src="https://www.youtube.com/embed/NjETSvAC8gY" frameborder="0" allowfullscreen></iframe>
因為跟效能有關，我這邊就交代一下我執行的硬體設備:

```
CPU: Intel i7-4785T
RAM: DDR3L-1600 8GB x 2 (16GB)
HDD: HGST 2.5" HDD (7200rpm, 340GB, 約六七年前的舊硬碟)
```

不算是很頂級的配備，就能跑出這樣的成果，其實算很棒的了...



# LAB 2, Run Windows Container with LCOW

這有啥好測試的? 不就是 Windows Container 嗎? XD
其實我這串研究跟評估，背後的目的都是將來在面臨 Mixed-OS 的系統架構時，能不能很簡單的在單一開發機上面就能跑起來啊! 因此驗證一下 Linux / Windows Container 能否並存，也是很合理的。

於是，我用同樣支援 LCOW mode 的 docker daemon, 跑看看 Windows Container... 開個 NanoServer 的命令列模式來試看看:

```
C:\>docker -H "npipe:////./pipe//docker_lcow" run -t -i microsoft/nanoserver cmd.exe

Unable to find image 'microsoft/nanoserver:latest' locally
latest: Pulling from microsoft/nanoserver
bce2fbc256ea: Download complete
5cd49617cf50: Download complete
docker: unexpected EOF.
See 'docker run --help'.

C:\>
```

哈哈，真是糟糕，nanoserver 跑不起來... 看了一下 docker daemon 的 logs, 發現這段訊息:

```
DEBU[2017-10-04T22:21:51.392861200+08:00] Calling GET /v1.32/info
DEBU[2017-10-04T22:21:51.562311500+08:00] Calling POST /v1.32/images/create?fromImage=microsoft%2Fnanoserver&tag=latest
DEBU[2017-10-04T22:21:51.562311500+08:00] Trying to pull microsoft/nanoserver from https://registry-1.docker.io v2
DEBU[2017-10-04T22:21:54.321365100+08:00] Pulling ref from V2 registry: microsoft/nanoserver:latest
DEBU[2017-10-04T22:21:57.377094800+08:00] pulling blob "sha256:5cd49617cf500abea7b9f47d82b70455d816ae6b497cabc1fc86a9522d19a828"
DEBU[2017-10-04T22:21:57.377094800+08:00] pulling blob "sha256:bce2fbc256ea437a87dadac2f69aabd25bed4f56255549090056c1131fad0277"
DEBU[2017-10-04T22:21:58.262107500+08:00] Pulling sha256:5cd49617cf500abea7b9f47d82b70455d816ae6b497cabc1fc86a9522d19a828 from foreign URL https://go.microsoft.com/fwlink/?linkid=857905
DEBU[2017-10-04T22:21:58.370240000+08:00] Pulling sha256:bce2fbc256ea437a87dadac2f69aabd25bed4f56255549090056c1131fad0277 from foreign URL https://go.microsoft.com/fwlink/?linkid=837858
DEBU[2017-10-04T22:22:23.402032800+08:00] Downloaded 5cd49617cf50 to tempfile C:\Users\chick\AppData\Local\Temp\GetImageBlob464734931
DEBU[2017-10-04T22:22:33.644205700+08:00] Downloaded bce2fbc256ea to tempfile C:\Users\chick\AppData\Local\Temp\GetImageBlob494712342
panic: inconsistency - windowsfilter graphdriver should not be used when in LCOW mode

goroutine 155 [running]:
github.com/docker/docker/daemon/graphdriver/windows.panicIfUsedByLcow()
        /go/src/github.com/docker/docker/daemon/graphdriver/windows/windows.go:163 +0x80
github.com/docker/docker/daemon/graphdriver/windows.(*Driver).Create(0xc0423fdf50, 0xc042a85940, 0x40, 0x0, 0x0, 0x0, 0x22a74c0, 0x18e59e0)
        /go/src/github.com/docker/docker/daemon/graphdriver/windows/windows.go:193 +0x2d
github.com/docker/docker/layer.(*layerStore).registerWithDescriptor(0xc0423e1aa0, 0x4724060, 0xc04306a660, 0x0, 0x0, 0xc042a76f88, 0x7, 0xc042251f80, 0x39, 0xf0fc23a, ...)
        /go/src/github.com/docker/docker/layer/layer_store.go:312 +0x28a
github.com/docker/docker/layer.(*layerStore).RegisterWithDescriptor(0xc0423e1aa0, 0x4724060, 0xc04306a660, 0x0, 0x0, 0xc042a76f88, 0x7, 0xc042251f80, 0x39, 0xf0fc23a, ...)
        /go/src/github.com/docker/docker/layer/layer_store_windows.go:10 +0xb5
github.com/docker/docker/distribution/xfer.(*LayerDownloadManager).makeDownloadFunc.func1.1(0xc042825da0, 0xc042825ce0, 0x22988a0, 0xc042437c20, 0x0, 0xc042453340, 0xc0420ee900, 0xc042825d40, 0xc042a77010, 0xc042a76f88, ...)
        /go/src/github.com/docker/docker/distribution/xfer/download.go:344 +0xd18
created by github.com/docker/docker/distribution/xfer.(*LayerDownloadManager).makeDownloadFunc.func1
        /go/src/github.com/docker/docker/distribution/xfer/download.go:372 +0x1dd
```

其中藏了這麼一段:

```
panic: inconsistency - windowsfilter graphdriver should not be used when in LCOW mode
```

看起來暫時是不支援了，等正式版出來再看看吧! 不過如果有跟我做一樣測試的朋友們請留意，跑出這 error message 時，docker daemon 就停掉了，如果你還要繼續玩 LCOW，那得再次啟動一次 docker daemon 才行。


# LAB 3, Networking

手癢的時候就是想亂玩一些有的沒有的，於是我繼續 ~~惡搞~~ 研究，看看混用不同 OS 的 container 的網路環境是否能互通。這次我在預設的 docker daemon 啟動一個 Windows Container: (microsoft/windowsservercore:latest + cmd.exe), 外加一個 BusyBox + sh:

![](/images/2017-10-04-lcow/2017-10-04-22-35-31.png)


這時，CMD.exe 拿到的 IP 是: 172.28.47.196, BusyBox 拿到的則是: 172.28.44.106, 兩邊互相 ping 會通。不過由於是透過兩個不同的 docker daemon 啟動的，每個 docker daemon 個別查詢 docker ps , 只能列出自己的 container. 所以也無法用 --link 或是 DNS 找到對方。這問題我想 IP 都通了，應該好解決吧? 依樣我把這段操作錄成 video 供各位參考:

<!-- <video 
    src="/wp-content/uploads/2017/10/2017-10-04-02-Networking.mp4"
    style="max-width:100%;width:640;height:480;"
    controls>
</video> -->

<iframe width="560" height="315" src="https://www.youtube.com/embed/2cgym3XzZjo" frameborder="0" allowfullscreen></iframe>

# 小結

本來打算弄個 docker-compose, 看看我之前那個例子 ([IP查詢服務](/2017/05/28/aspnet-msa-labs1/)) 能否實現 NGINX 用 Linux, 而 ASP.NET MVC 用 Windows 來跑的情境，看來目前暫時還因為無法在同個 docker daemon 一起執行，最後一步還無法跨出去... 不過沒關係，看來馬上就要 release 了，到時候再來測試一次 :D

這次 2017/10 的更新，除了 LCOW 之外，其實還有很多 windows container 相關的改進，這篇文章沒辦法每個都 LAB，我就整理一下遺漏的部分。資料來源是 windows blog 這篇文章:

[Announcing Windows Server Insider Preview Build 16278](https://blogs.windows.com/windowsexperience/2017/09/05/announcing-windows-server-insider-preview-build-16278/#SOIdfeTtZblSWuGp.97)

截錄其中一段:

*Developers and Containers*:

* New base container images (available on Windows Insider Docker Hub repo)
* Optimized Nano Server base image (over 70% smaller)
* The .NET team is providing a preview image based on Nano Server with .NET Core 2.0
* The PowerShell team is providing a preview image based on PowerShell 6.0
* Optimized Server Core base image (over 20% smaller)
* Support for SMB volume mounting
* Infrastructure for Orchestrators
* Networking enhancements for ongoing Kubernetes work
* Named pipe mapping support
* Bug fixes, performance enhancements

比較有感的有: nanoserver / windowsservercore 這兩個最常用的 OS based image 大幅縮減它的大小了。nano server 從原本的 330mb, 降低到 80mb, 有再用的舊感受的到差異了。

另外，container 支援的 volume driver, 也開始支援 SMB 了。意思是這版開始，你可以把 SMB 的分享目錄，直接掛上 container volume. 這不是啥大功能，但是實際使用上是個很重要的功能啊，不然每次我只能 mount local folder 實在很尷尬.. 能 demo 的 scenario 很有限。

再來就是對各種 orchestrators 的支援更完整了。我之前兩篇文章就有提到 docker swarm 的 network 支援還有些沒到位，這次看來也追上了，不只 docker swarm, 看來 kubernetes 也在改善支援程度的名單內。

這些改善對於有心想要把 windows container 推上 production environment 的朋友們都是很重要的更新啊! 再等兩個禮拜就可以體驗了! 到時有心得再跟各位分享。感謝各位看到這裡，祝大家中秋節快樂 :D