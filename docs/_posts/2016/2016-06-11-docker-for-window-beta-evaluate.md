---
layout: post
title: "專為 Windows 量身訂做的 Docker for Windows (Beta) !"
categories:

tags: ["Docker","MSDN","作業系統","專欄","技術隨筆"]
published: true
comments: true
permalink: "/2016/06/11/docker-for-window-beta-evaluate/"
redirect_from:
wordpress_postid: 1238
logo: /wp-content/uploads/2016/06/icon-218x181.png
---

![Docker for Windows Beta](/images/2016-06-11-docker-for-window-beta-evaluate/CjNVIX9UgAA0Z8L.jpg)

總算輪到我了!! 排隊等 Docker Beta Program Token 等好久了~  4 月初登記，5 月中才排到名額... 前陣子忙，一直到現在才有空研究 @@。這版是 Docker 在三歲生日時一起公布的 beta test program, 為 Windows / Mac 開發的新板 Docker, 企圖改善在非 Linux 平台上的 Docker 使用體驗。既然到手了，當然要體驗看看 :D

<!--more-->

# Docker for Windows Beta, 操作體驗大躍進!

開始 step by step 之前，先講一下我對這版的感想。不想聽這段心得的話，可以直接跳到後面看如何在 VM 裡面體驗這次大改版的 Docker for Windows beta... 要在 VM 裡面跑這個有些小地雷要閃過，我就順手整理在後面了。

做這些基礎建設的公司，真的都要掌握自己的虛擬化技術才玩得起來，不然就是要密切的跟掌握這些技術的公司合作才行。這次 Docker for Windows 我想背後 Microsoft 應該幫了不少忙吧? 不但跟 Hyper-V 整合的天衣無縫，同時 Windows Container 的幾個關鍵 Feature 也開始看的到跡象了，背後雙方應該合作了很久，現在開始端出成果出來了。我就被之前 Virtual Box 搞到完全不想在 Windows 上面跑 Docker, 索性忘掉 Docker Toolbox for Windows, 直接自己開 Linux 的 VM，不然就是直接找獨立的機器裝 Linux + Docker Engine, 用 SSH 連進去玩。完全跟我自己的 Host OS (Windows 10 Ent) 沒有直接的關聯，自然也沒甚麼整合性可言。換句話說，你不會 Linux 就不用玩了...。

畢竟，現在的 Container 都還是以 Linux 為主，未來兩三年內年應該還是脫離不了得附掛 Linux VM 才能執行 Docker 的狀況。很尷尬的一點就是，Container 就是為了脫離 VM 才設計出來的輕量化架構，而現在 Windows 上要跑 Linux 的 Container 又非得使用 VM 不可，這些整合的問題就浮現出來了。Mac 雖然也是 Unix 系列的 OS，不過她畢竟也不是 Linux, 也有類似問題存在。如何在虛擬化技術及整合上做到完美，就是這次改版主要的訴求了。

Mac 版的我沒有研究，有很多前輩分享過這部份了，我就不班門弄斧了，我就針對 for windows 版本的來研究。這次在架構上，官網講到有[幾項主要的改進](https://beta.docker.com/docs/features-overview/)，對我而言有感的改變有這幾個 (紅字):

*Docker for Mac and Docker for Windows are faster, more reliable alternatives to Docker Toolbox for running Docker on these platforms. Here are some highlights of the new products.*

- ***Faster and more reliable** - **No more VirtualBox!** On Mac, the Docker Engine runs in an [xhyve](https://github.com/mist64/xhyve/) Virtual Machine (VM) on top of an Alpine Linux distribution. The VM is managed by the native Docker application. On Windows, the Docker Engine is running in a [Hyper-V](http://www.microsoft.com/en-us/server-cloud/solutions/virtualization.aspx) VM. You do not need Docker Machine (`docker-machine`) to run Docker for Mac and Docker for Windows.*
- ***Native apps for better tools integration** - **Docker for Mac and Docker for Windows are native applications, including native user interfaces and the ability to stay updated automatically**. The Docker tools are bundled with these apps, including the Docker command line interface (CLI), Docker Compose, and Docker Machine.*
- ***Use with Docker Toolbox and Docker Machine** - Docker for Mac and Docker for Windows can be used at the same time as Docker Toolbox on the same machine. Docker for Mac and Docker for Windows do not include Kitematic yet. So, for now, the only reason you would still need both Toolbox and Docker for Mac or Windows is to run Kitematic. (See [Docker for Mac vs. Docker Toolbox](https://beta.docker.com/docs/mac/docker-toolbox/) in the Mac documentation. A Windows-specific version is coming soon.)*
- ***Volume mounting for your code and data** - Volume data access is fast and works correctly.*
- ***Support for multiple architectures out-of-the-box** - Docker for Mac and Windows lets you build and run Docker images for Linux x86 and ARM. (See [Leveraging Multi-Architecture Support](https://beta.docker.com/docs/mac/multi-arch/) in the Mac documentation. **A Windows-specific version is coming soon**.)*

補充一下這些改善，對我而言最有感的，就是終於拿掉 Oracle Virtual Box, 而改用 Microsoft 自家的 Hyper-V。Hypervisor 的應用是獨佔的，我沒辦法同時在一台機器上用 Hyper-V 又同時用 Virtual Box, 過去往往我都得自己手工改造，把 Virtual Box 換成 Hyper-V，現在已經變成內建預設的支援模式了 :D

另外，還有些官網沒提到的小改變，也是很有感... 值得提出來，例如 Docker 也換掉了原本搭配的 Boot2Docker ISO, 改用 [Apline Linux](http://www.alpinelinux.org/about/) + [Busybox](https://www.busybox.net/about.html)。Docker 也開始提供原生的管理介面，設定或更新都更簡單了，同時 Docker Engine + 配合的 VM，也統一由 Docker Service 管理，開機會自動運行，大大提高整合度。

不得不說 Docker 這次做的真不錯，把在 Mac / Windows 上面使用 Docker 的障礙降到最低了。實際上線時，應該不會有人在 Mac / Windows 上面跑 Linux VM 來執行 Docker，應該會直接用原生的 Linux Docker Engine 搭配 Docker Cluster 管理工具來運行，但是開發環境就不一樣了，Windows / Mac 這類 Desktop OS 是主流。因此這段能做好的話對於 Docker 的推廣絕對是一大助力。

Docker 在併購及整合技術的挑選上，都很有眼光。精準的建構整個 Docker 生態系，是他成功的主要原因。從 Docker Engine 容器技術本身，到 Docker Hub 統一的 Registry，併購了 TumTum (Docker Cloud 前身)，加上這次跟 Mac / Windows 徹底整合，把整段從開發到上線的 DevOps 開發流程都串起來了。不知 [Docker 併購的 UniKernel](https://www.docker.com/docker-news-and-press/docker-acquires-unikernel-systems-extend-breadth-docker-platform)，將來又會有甚麼樣的改革? 真是令人期待 :D

# Tips: 如何在 VM 裡面體驗 Docker for Windows?

感想先寫到這邊，接下來我就把我在 VM 裡面測試 Docker for Windows beta 的過程簡單紀錄一下。這邊有些技巧要留意，這是官網沒有講的。因為 Docker Engine 還是得依靠 Linux, 因此背後藏一台 Linux VM 仍然是必要的作法。既然我要在 VM 裡測試 Docker for Windows beta, 那麼 VM 裡面要再開 VM 就是閃不了的議題了。還好之前這篇已經先演練過 Nested Hyper-V 了，架構上的問題 Microsoft 已經解決了，剩下就是規劃跟實作。這次我要示範的架構圖如下:

![架構圖](/images/2016-06-11-docker-for-window-beta-evaluate/img_575af1cebe972.png)

由於太多層 VM 了，不先講清楚架構的話，會像 Inception 一樣搞不清楚你做了幾層夢境? 最後醒不過來就糟糕了 XD。這次的演練案例，只有最外層是我的實體 PC (CHICKEN-PC), 我在裡面開了台 VM (WIN10) 來跑 Docker for Windows beta, Docker 要求我啟用 Hyper-V feature 後，會自動建立一台 Linux VM (MobyLinuxVM), 在裡面跑 Apline Linux, 並且執行 Docker Engine。

## STEP #1, 準備好支援 Nested Hyper-V 的 VM

這部分可以參考之前的文章 ([如何在 VM 裡使用 Docker ToolBox ?](http://columns.chicken-house.net/2016/04/03/docker-toolbox-under-vm/))，或是直接參考 Microsoft 的[官方說明](https://blogs.technet.microsoft.com/virtualization/2015/10/13/windows-insider-preview-nested-virtualization/)即可。這部分難在 Hyper-V Nested Support 還只是 preview 階段，可能你連想都沒想到能這樣解決，或是根本還不知道有這功能...。另外，Preview 階段的東西文件也不足，也還沒有 GUI 可以用，只能透過 PowerShell Script 來啟用他。同時啟用 Nested Hyper-V 的 VM，也有一些規格限制要留意。這些細節突破後就過關了。以下是操作步驟:

第一件事，按照上圖施工，當然是在 Host PC 上 (CHICKEN-PC) 先準備好你要執行 Docker for Windows beta 的 VM (WIN10)。CHICKEN-PC 必須符合 Nested Virtualization 的需求，按照 Microsoft 的說法，OS 必須是 Windows 10 Pro or Enterprise / Windows Server 2016 Build 10565 以上的版本。Windows 10 Home 因為不支援 Hyper-V, 直接淘汰出局...。

至於 WIN10 VM 跑的 OS 要能夠執行這版 Docker for Windows beta 的系統需求，又有點不同，[官網](https://www.docker.com/docker-news-and-press/docker-released-native-mac-and-windows-apps-optimize-developer-experience)寫的是:

> *System Requirements for Docker for Windows*
> *Windows 10 Pro (1511 November update, Build 10586) and above, with [Hyper-V package installed.](https://msdn.microsoft.com/en-us/virtualization/hyperv_on_windows/quick_start/walkthrough_install)*

不過，我實際上用 Windows 10 Enterprise 也是 OK 的，Windows Server 2016 沒在列表上，我沒試過... 總之，我在 CHICKEN-PC 跟 WIN10 這兩個 Host 用的都是 Windows 10 Enterprise 10586 這版本，這組合是可以正確無誤的執行的。

同時，用到 Nested Virtualization 技術的 VM，會有這些限制，[官方列了十幾條](https://blogs.technet.microsoft.com/virtualization/2015/10/13/windows-insider-preview-nested-virtualization/)，這邊特別要留意的我標紅字:

- **Both hypervisors need to be the latest versions of Hyper-V.** Other hypervisors will not work. Windows Server 2012R2, or even builds prior to 10565 will not work.
- Once nested virtualization is enabled in a VM, the following features are no longer compatible with that VM. These actions will either fail, or cause the virtual machine not to start if it is hosting other virtual machines:

- **Dynamic memory must be OFF**. This will prevent the VM from booting.
- Runtime memory resize will fail.
- **Applying checkpoints to a running VM will fail**.
- Live migration will fail — in other words, a VM which hosts other VMs cannot be live migrated.
- **Save/restore will fail**. **Note:** these features still work in the "innermost" guest VM. The restrictions only apply to the first layer VM.

- Once nested virtualization is enabled in a VM, MAC spoofing must be enabled for networking to work in its guests.
- Hosts with Device Guard enabled cannot expose virtualization extensions to guests. You must first disable VBS in order to preview nested virtualization.
- Hosts with Virtualization Based Security (VBS) enabled cannot expose virtualization extensions to guests. You must first disable VBS in order to preview nested virtualization.
- **This feature is currently Intel-only**. Intel VT-x is required.
- Beware: nested virtualization requires a good amount of memory. I managed to **run a VM in a VM with 4 GB of host RAM**, but things were tight.

順序是你先用 Hyper-V 建立好要安裝 Docker 的 VM (我取的名字是 WIN10)，然後再用 PowerShell Script 啟用 Nested Virtualization。畫面如下:

![PowerShell Script](/images/2016-06-11-docker-for-window-beta-evaluate/img_575ac7c6e166c.png)

詳細步驟可以參考[官方說明](https://blogs.technet.microsoft.com/virtualization/2015/10/13/windows-insider-preview-nested-virtualization/)的這個段落: How to enable nested virtualization

接著就是建立 WIN10 這台 VM，同時安裝 Windows 10 Enterprise, 這個我就不多說，要留意 VM 的規格，必須停用 Dynamic Memory, 同時至少配置 4GB 以上的 RAM 就可以了。其他隨意... 以下是我自己測試環境的配置，給大家參考。用紅筆畫起來的地方請留意上述的限制:

![VM 設定](/images/2016-06-11-docker-for-window-beta-evaluate/img_575bac318bc22.png)

## STEP #2, 在 VM 內安裝設定 Docker for Windows Beta

接下來的動作，通通都轉移到 VM: WIN10 裡面進行了。如果你有申請 Beta Program, 你應該會收到下載網址，以及測試用的 Token.. 這段過程很無腦，下載安裝包 (MSI package), 下一步下一步按完就 OK 了:

![Docker 安裝](/images/2016-06-11-docker-for-window-beta-evaluate/img_575af80225e5d.png)

不過，如果你沒事先在 WIN10 裡面啟用 Hyper-V 的話，第一次執行 Docker for Windows 的話會出現這警告，按下 [Install & Restart] 後會自動幫你補安裝 + 重新開機:

![Hyper-V 安裝提示](/images/2016-06-11-docker-for-window-beta-evaluate/img_575af8c46977b.png)

重新啟動後，如果看到要你輸入 Token 的話，那就對了:

![Token 輸入](/images/2016-06-11-docker-for-window-beta-evaluate/img_575af908356cf.png)

這邊要留意一下，如果你 STEP #1 的部分沒做，或是動作不正確的話，接下來會看到 Docker 的警告訊息，說 MobyLinuxVM 無法啟動... 那個訊息閃太快我來不及抓到畫面。不過我自己手動到 Hyper-V 管理員去啟動 VM 也會看到一樣的訊息:

![VM 啟動錯誤](/images/2016-06-11-docker-for-window-beta-evaluate/img_575af99d5c5ec.png)

Nested Virtualization 沒正確設定好，就會造成 WIN10 這台 VM 裡面沒辦法再往下開一層 Linux VM .. 這時不要傻傻的重新安裝 Docker for Windows, 檢查上層的 CHICKEN-PC 是否正確設定比較重要。最簡單的驗證方法，就是在 WIN10 裡面另外手動建立第二台 VM，看看能否啟動就知道了。

![Docker 啟動成功](/images/2016-06-11-docker-for-window-beta-evaluate/img_575afea2eb1ff.png)

如果一切順利的話，開機後過一兩分鐘後，待 Docker VM 啟動完成之後，會看到這個訊息。同時右下角的 Tray Icon 也會有個 Docker 的 Icon 在那邊。

![Docker Settings](/images/2016-06-11-docker-for-window-beta-evaluate/img_575aff4482e69.png)

Docker Settings 也有統一的介面了。Dashboard 的部分這版還沒提供，不過調整設定的部分已經好了，VM 的規格可以在這邊調整，其實他只是代替你去調整 Hyper-V 配置給 VM 的 CPU 跟 MEMORY 資源而已。其他細節就各位自己摸索，總知道這個步驟，Docker for Windows 的安裝設定動作就告一段落。可以進行到下一步，開始 Pull Image 回來執行了。

## STEP #3, 執行 Docker Container: Hello-World

這邊測試我就簡單扼要的進行就好。我會測試兩個 container, 一個就是 hello-world, 證明這樣的架構是可運作的，第二個就是直接開 shell, 來驗證 mount local volume 的機制是否會運作。

若你順利的進行完前述 STEP #1 及 #2 的步驟的話，這步驟就再簡單不過了，唯一的差別是，過去需要自己 SSH 連到 Linux VM 內執行 Docker CLI, 現在可以直接在 Windows 下，透過 DOS Command Prompt / PowerShell 來執行 Docker CLI 指令，省了一層轉換，好處是你可以更密切的跟原生的 Windows 批次檔做整合，去運用及操控這些 Docker 的資源。

延續前述的環境，在 WIN10 VM 環境下，開啟 DOS 命令提示字元，執行 docker run 指令:

```bash
docker run --rm hello-world
```

![Hello World](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b089b8c29b.png)

完全不意外的執行結果，當然是有顯示出 hello-world 這個 container 的輸出。別小看這些訊息，他的背後可是累積了多少資源才能執行成功的 @@

這個步驟完成的話，恭喜你，你已經能順利的開始用 VM 來體驗 Docker for Windows 帶來的好處了，不用再擔心你在工作機上面安裝 Beta 版的工具 (尤其是這種會影響 infrastructure 的東西) 是否會搞壞你的工作環境了 :D

## STEP #4, 掛載 Windows Folder, 給 Container 使用

接下來的案例，是這篇的最後一個 DEMO，也是本篇的重頭戲: 要展示 Local Volume Mount 的機制。過去要嘛就是直接掛載 Linux VM 內的 volume, 需要溝通的話就開 SAMBA ，讓 Windows 透過網芳來存取。或是反過來 Windows 開分享，讓 Linux VM 用 CIFS mount 起來用。不管是哪一個方法，明明都在本機的 DISK，還要透過網路繞一圈 (雖然沒有真正繞出去啦) 實在是很蠢...

Docker for Windows 開始有專屬的設定方式可以解決這個問題了，在 Settings 畫面中，[Share Drivers] 就可以讓你勾選那些 DISK 能夠允許 Docker Engine 來使用，這應該是透過 [Docker Volume Driver](https://docs.docker.com/engine/extend/plugins_volume/) 來實現的。設定很簡單，Local Disk 有勾起來的，將來就能用在 Docker Volume 上面。

不過，前面的 "蠢" 方法講太快... Docker for Windows 一樣是透過網路繞了一圈，只是他把動作做到最精簡而已。我做了個小實驗，我的 WIN10 VM 有兩顆硬碟，分別是 C:\ 跟 D:\:

只勾選 C，結果 windows 就多了 C 這個分享目錄:

![共享設定 C](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b0bc5070d2.png)

是不是只是個巧合? 那我再把 D 勾起來看看:

![共享設定 D](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b0b396d834.png)

結果真的多了 D 這個 share .. 沒關係，瑕不掩瑜，至少它解決了過去棘手的大麻煩。這次我換成 apline linux 的 image, 直接掛載一個 volume 來驗證看看效果。

首先，我在 C:\Users\chicken\Docker\apline-data 目錄下，放置了 readme.txt 這個檔案，之後我移除所有的 Share Drives 設定，沒有勾選任何 DISK 的情況下，執行這個指令，將 C:\Users\chicken\Docker\apline-data 目錄掛到 Container 內的 /data ，啟動 apline linux, 並且進入 shell:

```bash
docker run -it --rm -v C:\Users\chicken\Docker\apline-data:/data apline /bin/ash
```

![Volume 測試 1](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b0e501d7a1.png)

沒有啟動 C:\ shared drivers 的情況下，並不會出錯，不過 container 內的確也看不到我預先放的 readme.txt 檔...

反過來測試看看，我在 apline linux 的 shell 下執行這段指令:

```bash
cp /proc/version /data/aplinux-version.txt
```

![Volume 測試 2](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b0f6f7001d.png)

很遺憾，左邊 Windows 檔案總管果然看不到這新增的檔案，但是在 Linux shell 內 cat 的到內容...

OK，離開這個 container, 刪除 image 後重新再 create 新的 container, 發現剛才的檔案還在，代表 volume 只是沒被正確的掛在 Local DISK，但是 Docker Engine 仍然有找個地方準備 Volume 讓 Container 掛起來用...

![Volume 測試 3](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b105bea9e7.png)

同樣的實驗再做一次，唯一的差別，在於第二次我事先打開 C:\ 的 Shared Drives 設定:

![共享設定啟用](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b10ad9bf2c.png)

同樣用這道指令，進入 Apline Linux shell:

```bash
docker run -it --rm -v c:\Users\chicken\Docker\apline-data:/data apline /bin/ash
```

![Volume 測試 4](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b11002573f.png)

這次果然順利 mount 到我只定的 Local DISK 了。同樣的，我在 Linux shell 內產生一個檔案:

```bash
cp /proc/version /data/aplinux-version.txt

cat /data/aplinux-version.txt
```

![Volume 測試 5](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b114157a49.png)

回到檔案總管看看，果然檔案有寫進來:

![Volume 測試 6](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b11959e3c8.png)

同樣的，離開 & 刪除 container 後，重建一次，前面對檔案的異動都有保留下來:

![Volume 測試 7](/images/2016-06-11-docker-for-window-beta-evaluate/img_575b11cc48af7.png)

大功告成! 實驗順利結束 :D

# 後記: Container Isolation Technonlgy

最後一個還沒機會測試的功能，也是我很感興趣的:

> ***Support for multiple architectures out-of-the-box** - Docker for Mac and Windows lets you build and run Docker images for Linux x86 and ARM. (See [Leveraging Multi-Architecture Support](https://beta.docker.com/docs/mac/multi-arch/) in the Mac documentation. **A Windows-specific version is coming soon**.)*

Linux x86 這次就已經能執行了，ARM 我手邊則還沒有東西可以測試...。我比較有機會用到的是 Windows Container, 看來也在將來的支援範圍內。這只能從文件跟這次的 release 找出一些蛛絲馬跡了。

舉個例子，Microsoft 在 MSDN 曾經提到，Windows Container 的架構為了 Docker 的弱項 "isolation" 做了加強，除了常看到用 namespace 做隔離之外 (process isolation)，Microsoft 也提供了更高隔離層級的 hyper-v container (kernel isolation)。簡介可以參考[這篇 MSDN BLOG](https://blogs.msdn.microsoft.com/jcorioland/2016/05/31/create-and-run-hyper-v-containers-using-docker-on-windows-10-desktop/):

> *There are two different kind of containers on Windows : Windows Container and Hyper-V Container. They work in the same way, instead of that Hyper-V containers are more isolated than Windows Container because they are running in a very lightweight virtual machine that provides kernel isolation and not just process isolation.*
> 
> *For more information about Hyper-V containers, check the official documentation on MSDN: [https://msdn.microsoft.com/en-us/virtualization/windowscontainers/management/hyperv_container](https://msdn.microsoft.com/en-us/virtualization/windowscontainers/management/hyperv_container)*

看來 Microsoft 跟 Docker 的合作很密切啊，這版的 Docker CLI 就已經看的到這 options:

```bash
docker run --help
```

![Docker CLI Options](/images/2016-06-11-docker-for-window-beta-evaluate/img_575bb0070b9c4.png)

查了一下，這是 Windows Container 專用的參數啊 (就算你用 Docker for Windows 也沒用喔，是要 Windows Container)。找到正式說明這參數的文件，有兩份:

### Docker Command Line Reference: [run / --isolation](https://docs.docker.com/engine/reference/commandline/run/#specify-isolation-technology-for-container-isolation)

#### *Specify isolation technology for container (--isolation)*

> *This option is useful in situations where you are running Docker containers on Microsoft Windows. The `--isolation <value>` option sets a container's isolation technology. On Linux, the only supported is the `default` option which uses Linux namespaces. These two commands are equivalent on Linux:*

```bash
$ docker run -d busybox top
$ docker run -d --isolation default busybox top
```

> *On Microsoft Windows, can take any of these values:*

| *Value* | *Description* |
|---------|---------------|
| *`default`* | *Use the value specified by the Docker daemon's `--exec-opt`. If the `daemon` does not specify an isolation technology, Microsoft Windows uses `process` as its default value.* |
| *`process`* | *Namespace isolation only.* |
| *`hyperv`* | *Hyper-V hypervisor partition-based isolation.* |

另外一份，則是 Microsoft 在 MSDN [說明 Hyper-V Containers 的官方文件](https://msdn.microsoft.com/en-us/virtualization/windowscontainers/management/hyperv_container):

### Hyper-V container

#### *Create container*

> *Managing Hyper-V containers with Docker is almost identical to managing Windows Server containers. When creating a Hyper-V container with Docker, the `--isolation=hyperv` parameter is used.*

```bash
docker run -it --isolation=hyperv nanoserver cmd
```

# 總結

寫到這邊，總算把我這幾天研究成果寫完，可以告一段落了。落落長的寫了一堆，實際操作的細節，可能在將來 release 推出時都還會異動，各位其實不大需要去記這些細節。

不過更重要的，是透過 beta 搶先了解有那些問題會在將來的版本被解決掉? 還有官方的發展趨勢是什麼? 像這次就看到 Docker 跟兩大主流 Desktop OS 的無縫整合越做越好了，目的我想就是要改善 DevOps 流程的前段 (Development)。

另一個主軸就是 Docker 跟 Microsoft 的合作越來越密切了，這其實是件好事，對我而言這代表:

1. Microsoft 的 Windows Container 將會跟 Docker 有很好的相容性，不論是在架構上，工具上，甚至 API 都是。
2. Windows Container 除了 OS 的不同之外，Docker 在架構及流程上的好處都可以繼續沿用。
3. Docker Hub 官方公開的 Registration 也率先支援了 Windows Container, 更確保將來 Deployment 的機制是一致且可以共用的。

所以，雖然 Windows Server 2016 到現在還在 Tech **Preview**，等到正式出來不知道等到啥時，不過他帶來的效益，是可以預期的。開發團隊盡早熟悉這個生態，絕對是件值得的投資~
