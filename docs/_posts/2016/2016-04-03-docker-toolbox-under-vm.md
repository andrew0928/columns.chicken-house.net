---
layout: post
title: "如何在 VM 裡面使用 Docker Toolbox ?"
categories:

tags: ["Docker","Tips","作業系統","技術隨筆"]
published: true
comments: true
permalink: "/2016/04/03/docker-toolbox-under-vm/"
redirect_from:
wordpress_postid: 1015
---
這篇一樣是意料之外的文章，不在原本的寫作計畫內 XD

上個禮拜是 Docker 三周年的生日，很難想像一個才剛滿三歲的技術，就已經在整個資訊業界掀起一陣風潮了.. 這次剛好無意間在 FB 的 Docker 社團，看到[保哥問了個問題](https://www.facebook.com/groups/docker.taipei/permalink/1739265086308847/) (借保哥的圖用一下):

---

> *請問有人知道如何在 Hyper-V 下執行 Docker Toolbox 嗎？*

![](/images/2016-04-03-docker-toolbox-under-vm/12898285_10209340119290278_6988112908761034670_o.jpg)

一時手又癢了起來，於是就多了這篇意料之外的文章 XD

<!--more-->

### 關鍵問題: 無法在 VM 裡面建立 VM!

這次不碎唸了，直接開始正題。Docker Toolbox 是個 Docker 的常用工具箱，讓你可以一次解決在 Windows 下使用 Docker 的所有必要套件。裡面包含 Oracle VirtualBox, 幫你準備好執行 Docker 用的 Linux VM。

其實這次的問題的根源很簡單。由於已經是被模擬出來的 Virtual Machine 了，模擬出來的 CPU 就不再支援[ VT-X / AMD-V 這些硬體輔助的虛擬化能力了](https://en.wikipedia.org/wiki/X86_virtualization)。然而 Docker 是需要 Linux 的 Kernel 來運行的，在 Windows 環境下至少要先準備個 Linux VM (Docker Toolbox 預設使用 Virtual Box), 才有能力執行任一個 Docker Container..

因此，想在 VM 裡使用 Docker Toolbox, 第一個問題就是: 如何在 VM 裡再建立一個 VM ?

### Nested Virtualization Support

"養兵千日，用在一時"，就是這道理... 要不是之前曾經研究過 windows container，曾經花了些時間看一下 windows server 2016 有啥突破的話，這次也不會馬上就聯想到解決問題的方向。Windows Server 2016 其中一個新功能，就是支援 [nested virtualization](https://msdn.microsoft.com/en-us/virtualization/hyperv_on_windows/user_guide/nesting) 的技術。

其實當時看到這功能，心裡覺得不大實用，感覺有點脫褲子放屁... VM 是很花費資源的技術，一層一層的 VM 包裝下去，只是慢上加慢而已，有人會這樣用嗎? 不過這次還真的碰到了!! Docker 帶來一股微服務架構 ([MicroServices](https://en.wikipedia.org/wiki/Microservices)) 的風潮，老實說以系統架構的角度來看是個很實用的技術。不過要研究這些技術，如果不能在 VM 裡先玩看看，直接用到實體機總不是那麼方便...

終於找到 nested virtualization 技術應用的地方了，於是就動手開始研究如何解決這問題。我先參考了 Microsoft 放在 MSDN 的官方文件，節錄裡面的重點:

> *Nested Virtualization ([https://msdn.microsoft.com/en-us/virtualization/hyperv_on_windows/user_guide/nesting](https://msdn.microsoft.com/en-us/virtualization/hyperv_on_windows/user_guide/nesting))*

> ![](/wp-content/images/2016-04-03-docker-toolbox-under-vm/hvnesting.png)

> *In this case, Hyper-V exposes the hardware virtualization extensions to its virtual machines. With nesting enabled, a guest virtual machine can install its own hypervisor and run its own guest VMs.*

主要的改變，就是 Microsoft 調整了 Hyper-V Hypervisor 的實作方式，讓模擬出來的 vCPU 也具備 Hypervisor 的能力。至於這樣層層疊上去的做法是完全用模擬的? 還是只是把這指令 redir 到 Level 0 的實體 CPU 來處理? 這樣兩層的模擬會有多少效能折損? 這些細節文章就沒提到了。現在討論效能也還太早，其實這技術也還在 preview 階段而已...

### 替 VM 啟用 Nested Virtualization 的支援

看懂了原理，接下來就是實際操作。現階段要使用 Nested Virtualization 的功能，有幾個先決條件要符合:

> *Before enabling nested virtualization, be aware this is a preview. Do not use nesting in production environments.*

> *Requirements:*

- *4 GB RAM available minimum. Nested virtualization requires a good amount of memory.*
- *Both hypervisors need to be the latest Windows Insider build (10565 or greater). Other hypervisors will not work.*
- *This feature is currently Intel-only. Intel VT-x is required.*

軟體的限制是你必須使用 Windows Build 10565 以上的版本，原來我現在用的 Windows 10 (10586) Enterprise 也在支援範圍內啊!! 我本來還一直以為我得裝 Windows Server 2016 才能玩這東西，沒想到得來全不費工夫...

硬體限制很明確，目前只支援 Intel 的 VT-X, 同時至少要有 4GB 以上的 RAM... 正好我的 Intel i7-2600k / 24GB RAM 全都符合.. 通過軟硬體需求。接下來就是啟用這個功能。

詳細的步驟可參考 [MSDN 這篇文章](https://msdn.microsoft.com/en-us/virtualization/hyperv_on_windows/user_guide/nesting)，我只摘要關鍵的部分:

> *Run [this script](https://github.com/Microsoft/Virtualization-Documentation/blob/master/hyperv-tools/Nested/Enable-NestedVm.ps1) as administrator on the Hyper-V host.*

> *In this early preview, nesting comes with a few configuration requirements. To make things easier, [this PowerShell script](https://github.com/Microsoft/Virtualization-Documentation/blob/master/hyperv-tools/Nested/Enable-NestedVm.ps1)script will check your configuration, change anything which is incorrect, and enable nested virtualization for the specified virtual machine.*

要執行的 script 在這裡，請開啟 powershell 來執行:

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/Microsoft/Virtualization-Documentation/master/hyperv-tools/Nested/Enable-NestedVm.ps1 -OutFile ~/Enable-NestedVm.ps1
~/Enable-NestedVm.ps1 -VmName "DemoVM"
```

他的邏輯是這樣，Nested Virtualization 是針對個別的 VM 開啟的，因此你先照正常的程序建立跟設定你要的 VM，然後執行這段 Powershell Script 替這個 VM 啟用 Nested Virtualization 的功能。其中 "DemoVM" 就是指定 VM 的名字...

在我的範例裡面，我的 VM name 是: WIN10, 附上我的執行結果:

![](/images/2016-04-03-docker-toolbox-under-vm/img_57000bc9912e2.png)

Nested virtualization 有些地方要注意，VM memory 至少要 4GB, Mac Address Spoofing 必須啟用，還有一些 blah blah 的警告... 像是不支援 dynamic memory, 也不支援 checkpoints 等等。

### 安裝 Docker Toolbox, 準備 Docker Host VM

Script 執行完畢後，Host OS 這段的任務就結束了，接下來替這個 VM "開機"，在裡面開始安裝 Docker Toolbox:

![](/images/2016-04-03-docker-toolbox-under-vm/img_57000cba58b2c.png)

安裝過程就不多說了，全部都照預設值安裝... (後面會說明要注意的地方)，一路下一步跑完就結束了。安裝好之後，直到我按下 Docker Quickstart Terminal 才發現不對勁...

前面的 initialization 還算順利，啟用 nested virtualization 後，建立 VM 不再像之前保哥碰到的狀況，無法支援 VT-x .. 看起來都順利的 init:

![](/images/2016-04-03-docker-toolbox-under-vm/img_5700124ea57ca.png)

不過跑到後面，看來 Virtual Box 還是不買帳，重新測試幾次後 (該不會被我玩壞了吧?) 連建立都有問題了 @@

在 VM 內就是無法成功的用 Virtual Box 啟用已建立 VM ...

![](/images/2016-04-03-docker-toolbox-under-vm/img_57000f4120a6a.png)

直接開 Virtual Box 來看，也是碰到一樣的問題:

![](/images/2016-04-03-docker-toolbox-under-vm/img_57000f651308d.png)

我就把他當作 Nested Virtualizalization 的 Known Issues 吧，preview 階段的技術，跟對手的技術不相容應該也算正常... 跟自家的 Hyper-V 總不會有問題了吧?

由於還是 preview 的技術，我決定不繼續跟他耗下去，先改用比較可靠的方案，用 Microsoft Hyper-V 代替 Oracle Virtual Box!

### Docker Machine

這邊就必須先介紹一下 [Docker Machine](https://docs.docker.com/machine/overview/) 這東西了。這是包含在 Docker Toolbox 工具箱內的一個關鍵元件。Docker Container 再強，你終究還是需要台 "Machine" 來跑 Linux + Docker Host 啊... 不論你用的是實體機器還是虛擬機器... 然而建立虛擬機器的方法千百種，於是 Docker 就提供了 Docker Machine 這個好東西，讓你用一致的介面，在不同環境下建立你要的 VM (用 [boot2docker](http://boot2docker.io/))。

其中，Docker Machine 支援了十幾種 [Docker Machine Driver](https://docs.docker.com/machine/drivers/)，可以在這些主流的虛擬化環境下幫你建立 VM，包括:

- 雲端服務廠商: Amazon Web Services, Microsoft Azure ... etc
- 虛擬化軟體: Microsoft Hyper-V, Oracle VirtualBox, VMWare vSphere ... etc

既然 Docker Toolbox 預設支援的 Virtual Box 碰到釘子了，我跳過 Quickstart Terminal, 手動下指令，改用 Hyper-V 試看看...

我的準備步驟簡單紀錄一下，我就不一一詳細說明了 (sorry 我很懶 XD，原諒我只挑關鍵的部分說明)

1. 移除 Oracle VirtualBox, 安裝 Microsoft Hyper-V
2. Reboot 後，去 Hyper-V 設定 Network Virtual Switch (不做這項的話，Docker Host VM 就沒網路用了)

接下來，直接開個 DOS Prompt, 用 Docker Machine 建立 VM 試看看。我用的指令:

```
docker-machine create -d hyperv boot2docker
```

其中 -d hyperv 的意思，就是改用 hyper-v 的 driver 來執行 VM 準備動作。如果你不想在本機建立VM，換掉這個 options, 就可以改成在 Azure / AWS 上面玩了。讀者們有興趣可以自己試一試。

這次建立過程就很順利，等了一兩分鐘就完成了。

![](/images/2016-04-03-docker-toolbox-under-vm/img_570012eaeeb95.png)

看來除了建立 VM，連 VM 必要的設定也都準備好了。VM準備好後，直接用 boot2docker.iso 這光碟映像檔開機。Boot2Docker.iso 是個針對 Docker Host 設計的 Linux 開機光碟，目的是 Diskless 的環境下，只要用 CD BOOT 就可以使用 DOCKER 環境的特化版 Linux. 這邊可以看到，VM 開好 BOOT LINUX 後，連 SSH 憑證等等都幫你設定好了...

接下來，Docker Client 設定一下，你就可以直接用 Docker 指令來操作了。設定的方式最後一行有寫，照著做就可以:

```
run: docker-machine env boot2docker
```

![](/images/2016-04-03-docker-toolbox-under-vm/img_570014665a7e3.png)

設定好這幾個環境變數，我就可以直接在這台 windows vm 上面使用 docker 了。

拿 [hello-world](https://hub.docker.com/_/hello-world/) 這個 docker container 測試看看:

```
docker run hello-world
```

![](/images/2016-04-03-docker-toolbox-under-vm/img_570014b3b1c69.png)

用過 Docker 的人看了就懂了，我就不用多說... Docker Client 直接跟 Docker Host 溝通，去 Docker Hub Pull 這個 container image 回來執行... 印出來的那堆 message 就是執行的結果，代表你已經成功的執行這個 container

剩下美中不足的，是 Docker Toolbox 還有另一個好用的 Docker GUI, 讓你使用豐富的 Docker Container Image, 就好像用手機逛 App Store 下載 APP 回來用一樣容易的工具: Kitematic

雖然我們把背後的 VirtualBox 換成 Hyper-V 就可以用了，但是當你打開 Kitematic 時，他還是去用 VirtualBox 啊... 想把它改成 Hyper-V 的話，可以參考這篇文章:

---

### [MODIFYING KITEMATIC TO RUN ON WINDOWS 10 WITH HYPER-V](http://agup.tech/2015/08/14/hacking-at-kitematic-with-hyper-v-on-windows-10/)

*Kitematic is a new player in the Docker arsenal, and fully featured with Docker's release of the new Toolbox. Kitematic has two basic principles*

1. *Give everyone a streamlined process to spin up and try Docker on their local machine*
2. *Bring a delightful UI experience to the the container world*

*As most enthusiasts, when I saw this announcements I rushed onto the release page and began my Windows download. After I ran the installer I was shot into a Virtual Box installer and was up and running in seconds - Awesome. Now when I updated to Windows 10, I started with a clean slate, and Kitematic was unfortunately lost in the fire.*

*When I installed Kitematic again on Windows 10, I and many other users found that Virtual Box did not work on Windows 10. Forced to fend for myself I turned to my holy hypervisor savior Hyper-V. I love Hyper-V; for one it's installed on my machine by default, all my friends run Hyper-V, even my mom runs Hyper-V.*

*Anyways, I found that docker-machine had a pleasant experience with Windows 10 Hyper-V, and that if Kitematic used that same logic for docker-machine on Virtual Box I could simply switch the underlying docker-machine command. This blog is about the foolish endeavor to turn the streamlined process of running Kitematic, into a process full of long and complicated twists and turns.*

---

OK，到這邊就大功告成! 順利解決在 VM 裡使用 Docker Toolbox 的問題。感謝大家收看!

若你喜歡我分享的內容，也請支持我的粉絲團: [安德魯的部落格](https://www.facebook.com/andrew.blog.0928/) XD
