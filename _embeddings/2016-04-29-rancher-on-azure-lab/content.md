---
layout: post
title: "Rancher - 管理內部及外部 (Azure) Docker Cluster 的好工具"
categories:

tags: ["AZURE","Docker","專欄","技術隨筆"]
published: true
comments: true
permalink: "/2016/04/29/rancher-on-azure-lab/"
redirect_from:
wordpress_postid: 1159
---

過去快20年的經驗裡，很少看到有哪個技術在短短的三年就可以發展成這個樣子的... 半年前剛開始研究 Docker 時，就想找個好用的 WEB / GUI 管理工具，結果都沒滿意的，沒想到現在就一堆選擇了...

這次要介紹的 [Rancher](http://rancher.com/), 除了是套完整的 Docker Engine 管理工具之外，也是個 Docker Cluster 管理工具及平台，讓你在佈署 Containers 的時候，不用去傷腦筋你要怎麼分配資源等等瑣碎的事情，你只管把你的 Container 組態設定好，丟上去就行了。這感覺跟當年 (2009) 初次接觸到 Winows Azure 的 Cloud Service 一樣令人感動。當年只要把你的 Application 打包成 Cloud Service Package，開發階段設定好組態，佈署階段可直接手動或自動的設定 Scale，具備 Production / Staging Environment 切換上線，可以不中斷服務的升級系統...，整個就是靠 Visual Studio Deploy 就足以取代過去要 OP team 搞半天的升級程序。

只可惜 Azure Cloud Service 的種種優異的管理及佈署能力，至今都還只限於 Azure Only，沒有下放到地面版本的 Platform ... 真的是 "此物只應天上有" 啊... 但是站在地上的凡人沒機會用啊...  現在看到 Docker Cluster + Management Tools 的發展，這種威力已經變成隨手可得了... 為了紀念一下當年 Microsoft 早在 Azure 就達成的成就 (而且早已商業化)，這次的實作案例就拿 Azure 示範位於公有雲的 Production Environment，如何做到服務的管理及升級程序吧!

<!--more-->

過去開始用 Docker 時，其實我就一直在找合用的 Web UI，來取代每次都要打一堆指令的管理方式。過去都還停在單機版的時代，按照我使用的順序，我嘗試過這幾套:

1. [Synology Docker Station](https://www.synology.com/en-us/dsm/app_packages/Docker) (內建在 NAS 內的 Docker 套件)
2. Docker UI (實在有點陽春... 已放棄)
3. [Shipyard](https://shipyard-project.com/) (一樣用不順手，連安裝都沒完全搞定就放棄了)

其他連裝都沒裝起來用的就不列了.. 接下來只管理一台 Docker Engine 的 Solution, 漸漸的滿足不了我了，於是我開始尋找能一次管理多套 Docker Engine 的工具... 一找下去，不得了... 選擇一堆... @@:

處理 Docker Cluster 的平台 (orchestration) 就有好幾種平台可以選擇，這邊也是多到沒力氣一個一個研究 @@:

1. [Docker Swarm](https://docs.docker.com/swarm/) (Docker 官方內建的 solution)
2. [Cattle](https://github.com/rancher/cattle) (Rancher 內建的 infrastruction orchestration platform)
3. [Apache Mesos](http://mesos.apache.org/documentation/latest/docker-containerizer/)
4. [Kubernetes](http://kubernetes.io/) (Google 的方案)
5. [Docker Cloud](http://cloud.docker.com) (前身: Tutum, 被 docker 併購的線上託管服務)

能使用的管理工具也不少 (Docker Swarm 我就略過了):

1. [Rancher](http://rancher.com/)
2. [Tutum](https://www.tutum.co/), 被 docker 收購後變成 [docker cloud](http://cloud.docker.com)
3. [Azure Container Service](https://azure.microsoft.com/zh-tw/services/container-service/) (using Mesos or Swarm)
4. ...

這些都是這兩個月才 Release 的服務啊... 這個領域真是競爭，一個多月出來這麼多項重量級服務... 選擇多是件好事，不過我只想無腦的跟著主流用一套就好 XD，實在沒力氣每一套都去研究啊... 畢竟我的目的是用它來解決我的問題，而不是以搞懂這麼多 solution 為樂啊.. 所以之前才選用了 Docker Cloud (前面的心得文)。老實說用了很滿意，介面的複雜度恰到好處，我想要的東西都改的到，又不會過於複雜難懂。不過唯獨缺了兩點:

1. 要錢! 免費版本只提供管理 1 node，每多一個 node 每個月就要 USD $15..
2. 缺少資源使用的統計或是 dashboard，想知道 CPU / RAM / DISK 的使用狀況，得另外想辦法

挑選評估爬文等等的過程就不說了，最後我看上了 Rancher 這套，就決定花點時間來研究看看。看上這套主要有幾個原因:

1. (大推) UI 介面合我的胃口.. 更重要的是提供詳細的硬體資源使用狀況，也提供每個 Container 的資源使用狀況
2. (大推) 支援 In-Service Upgrade
3. (大推) 內建 Load Balancer
4. 安裝容易，同時也提供了專為執行 Docker 而發行的專用 Linux: Rancher OS
5. 支援多種 Orchestration Platform, 包括 Docker Swarm / Mesos
6. 支援 Windows Azure 及其他 Cloud 服務商
7. 支援多個環境 (Environment) 的管理，可以切割幾個完全獨立的 Cluster 個別負責不同的任務，或是隔離測試環境等

其他評論挪到後面再說，介紹先到這裡告一段落。接著就來看看我實作的過程，然後再來講心得...

# STEP #0, Planning

![Planning Diagram](/wp-content/uploads/2016/04/img_5720ee43d57b5.png)

我這次 LAB 想架設的環境，就用典型的切割開發跟正式環境吧。我希望有兩組 Docker Cluster, 分別做為開發及正式使用。開發環境理所當然的要架設在 Intranet 內，這次案例我就用我自己的 PC 開 VM 來模擬。而正式環境就在 Azure 上面架設。然而這兩組環境，統一由一套 Rancher 來管理及佈署。

環境準備好之後，我會在上面模擬這個情境:

1. 佈署 WordPress 服務，區分 WEB 及 DB 兩個 container, WEB 需要透過 Load Balance 達到 HA 的要求
2. Scale Out, 將 Web Nodes 從 2 個升級到 3 個
3. 進行升級，在升級 WEB 的過程中必須持續提供服務 (In-Service Upgrade)

其實這些都是過去我在 Azure Cloud Service 上用的很高興的管理功能，多年後容器技術的發展，我終於也有能力自己架設同樣等級的環境了 :D

接下來請看實際操作步驟~

# STEP #1, 架設 Rancher Server

這邊開始前，先說明一下 Rancher 的基本觀念 (可參考[這篇](https://blog.hellosanta.com.tw/%E7%B6%B2%E7%AB%99%E8%A8%AD%E8%A8%88/%E4%BC%BA%E6%9C%8D%E5%99%A8/%E8%A6%96%E8%A6%BA%E5%8C%96%E7%AE%A1%E7%90%86%E7%9C%BE%E5%A4%9A-docker-%E5%AE%B9%E5%99%A8%E8%88%87%E9%83%A8%E7%BD%B2%E7%9A%84%E5%A5%BD%E5%B7%A5%E5%85%B7%EF%BC%9Arancher))。Rancher Server 本身是套 Docker Cluster 的管理介面，但是他本身也被包裝成 Container, 所以你為了執行它，你也是得找個 Docker Engine 來安置它。雞生蛋蛋生雞的問題來了，所以我還是得架設一台 Linux + Docker 嗎? Rancher Labs 提供了另一個好選擇，就是 Rancher OS。

簡單的說，Rancher OS 是個特別為了執行 Docker 所發行的 Linux, 它拿掉所有不必要的服務，也因此整個 image 非常小，只有 28mb. Docker Engine 在 Rancher OS 的地位很高，系統啟動後第一個執行的就是 Docker (PID : 1) .. 當然你可能需要些其他標準 Linux OS 有的功能，這些通通都可用 Container 的方式外掛上去，維持 OS 本身的簡潔...

因此，這次我的動作就是先用 Rancher OS 搞定我第一個 Docker Engine, 並且在上面跑 Rancher Server。這部分我就不多說，很多前輩 & 官網都寫得比我還清楚，我直接貼參考連結就好 :D

- 如何將 Rancher OS 安裝到 HDD ?
  > [Installing RancherOS to Disk](http://docs.rancher.com/os/running-rancheros/server/install-to-disk/)
- 如何安裝 Rancher Server ?
  > [視覺化管理眾多 Docker 容器與部署的好工具：Rancher](https://blog.hellosanta.com.tw/%E7%B6%B2%E7%AB%99%E8%A8%AD%E8%A8%88/%E4%BC%BA%E6%9C%8D%E5%99%A8/%E8%A6%96%E8%A6%BA%E5%8C%96%E7%AE%A1%E7%90%86%E7%9C%BE%E5%A4%9A-docker-%E5%AE%B9%E5%99%A8%E8%88%87%E9%83%A8%E7%BD%B2%E7%9A%84%E5%A5%BD%E5%B7%A5%E5%85%B7%EF%BC%9Arancher)

過程很簡單，就是 Docker Engine 搞定後，docker run rancher/server 回來執行就完成了。裝好後預設的 PORT 是 8080，輸入 http://{your ip}:8080/ 就可以看到 Rancher Server 的管理介面了。預設不用密碼，我自己單機使用我就懶得去設定帳號權限，正式使用時請勿跳過這段!

![Rancher Server 預設安裝的畫面](/wp-content/uploads/2016/04/img_57221f673affc.png)
*圖: Rancher Server 預設安裝的畫面*

Rancher Server 跑起來不算輕快，Container Started 之後要等一兩分鐘才能完全啟動，請有耐心點等待，別以為你裝壞了。Rancher Server 用了不少 Java 開發的套件，啟動慢是正常的 @@，請別用太糟糕的規格給 Rancher Server, 官方建議是至少 1GB+ RAM, 我自己觀察，最後給了 2GB RAM 比較剛好，這個 VM 就只執行 Rancher OS + Rancher Server 這個 Container 而已，本身我並沒有讓他加入 Cluster，往後要佈署的服務也不會被放到這台 VM 上，單純當 Master 來使用。

這步驟完成之後，就可以開始建立你的 Docker Cluster 了，請繼續看下去!

# STEP #2, 架設 Local Environment

這邊有些準備動作要先做，我想建立一組 Docker Engine Cluster, 專供內部的 Development Team 使用，步驟是先準備好 Docker Engine 環境，然後按照 Rancher Server 的指示，執行 "Add Host" 的步驟，把這個 Docker Engine 納入 Cluster 的管控。這邊我比照前面的步驟，用 Rancher OS 建了三台 VM，分別是 Rancher Host #1 ~ #3。

![Rancher Hosts](/wp-content/uploads/2016/04/img_57222434871bf.png)

接著，進入 Rancher Server, 先建立 "Local Environment"

Environment > Manage Environments > Add Environment, Container Orchestration 選預設的 Cattle:

![Add Environment](/wp-content/uploads/2016/04/img_572224eb7eda3.png)

右上角切換到 Local Environment, 從 Infrastructure > Hosts > Add Host, 把建立好的三台 VM 都加進去: (手動增加 Host, 請選 Custom )

![Add Host](/wp-content/uploads/2016/04/img_5722253db5c6e.png)

複製 (5) 的指令，到 Host 上面執行，稍等 3 ~ 5 分鐘，Rancher Agent 啟動執行完畢，就可以在 Rancher Server 上面看到這個 Host 了 !

![Host Added](/wp-content/uploads/2016/04/img_572225fa8eeb3.png)

介面設計的很不錯，上面跑了那些 container, 還有目前整個 host 的資源使用狀況，或是每個 container 的使用狀況都一清二楚:

![Host Management](/wp-content/uploads/2016/04/img_5722269a33cb6.png)

# STEP #3, 架設 Azure Environment

接下來要準備正式上線的環境了。正式環境當然不是自己在家亂搞一通就 OK。這部分我選擇把他配置在 Azure 的 Data Center 內，卻保有良好的服務品質。這部分的執行方式，其實跟 STEP #2 沒甚麼不同，只是 VM 環境改成 Azure 而已。

比較特別的是，Rancher 直接支援各大 IaaS 的環境，Microsoft Azure 也在支援之內。支援的意思是你不在需要自己手工從 VM 建立到加入 HOST 都一步一步慢慢來，可以在一個畫面內一次搞定所有的配置需求。在 Azure 上面佈署多台 HOST 的動作，整個過程都已經自動化，我只要把我的 certification 貼進去，告訴它我需要幾台 VM (之後等著付錢) 就搞定了!

一樣，先準備 Azure Environment，切換過去後，從 Infrastructure > Hosts > Add Host ，輸入你 Azure 上的資訊，還有你要開設的 VM 規格及數量後:

![Azure Configuration](/wp-content/uploads/2016/04/img_57222755ed594.png)

按下 [CREATE] ，等個幾分鐘就一切大功告成! 你下單的 Host 就都排排站在那邊等你差遣了 XD

*"At your service! Sir!"*

這邊穿插一下，其實 Rancher Server 直接原生的支援 Docker Swarm, 只是目前版本還沒辦法 "匯入" 已經建立好的 Swarm Cluster. 也就是你必須透過 Ranhcer Server, 從頭建立 Host(s). 官網說正在努力這件事啦，完成後就可以匯入現有的 Docker Swarm Cluster. 為什麼我要補充這個? 因為同樣這個月才 GA (General Available) 的 Azure Container Service, 可以讓你 Click 幾下就把整個 Docker Swarm Cluster 搞定...  Orz, 怎麼四月份這麼熱鬧? @@

步驟一樣很簡單... 就跟在 PCHome 上面買東西一樣... 從 Marketplace 挑選: Containers > Azure Container Service..

![Azure Container Service](/wp-content/uploads/2016/04/img_572227ef0fa06.png)

填一下基本設定，登入帳號，還有 SSH 要用的 public key，挑選你要用的機房...

![Azure Setup 1](/wp-content/uploads/2016/04/img_5722283f5022e.png)

選擇你要用的 Orchestrator configuration, 這邊我就用最標準的 Swarm ...

![Azure Setup 2](/wp-content/uploads/2016/04/img_5722285abac2c.png)

選擇訂購數量，看看你要什麼規格的 VM 要幾台...

![Azure Setup 3](/wp-content/uploads/2016/04/img_5722286ce0af1.png)

最後，付款前最終確認...

![Azure Setup 4](/wp-content/uploads/2016/04/img_5722287ce9238.png)

完成，接下來你只要等就可以了...

![Azure Deployment](/wp-content/uploads/2016/04/img_57222899d6dc6.png)

Orz, 真的是 OOXX ... 之前研究了半天，結果按幾下就可以用了... 這個速成的時代，你要會的 "操作" 跟 "基礎知識" 的落差實在是越來越大了。很難想像再晚十年才進入這行的年輕人，到時他們接受的資訊量，腦袋還能負荷嗎? 未來懂得操作又能理解背後的基礎知識的人，會不會越來越少?

雖然 Azure Container Services 很好用，不過這還不是這篇要介紹的重點啊啊啊啊，寫這篇的時候本來還以為 Create 好的 Swarm Cluster 可以直接掛上 Rancher 使用，後來才發現原來還不支援... 看來只好等後續版本再來測試...

官方這篇文章有說明:

http://rancher.com/rancher-support-for-docker-swarm-and-machine/

截錄一段:

> *we are working with the Docker team to extend Swarm so that a cluster can be created outside of Rancher and automatically imported into Rancher for management.*

OK，官方都這樣說了... 只好等了~

# STEP #4, Deploy "Hello World" Service

其實，到這個步驟為止，環境就建立好了，接下來就可以真正的體驗一下，如何把你的 Application Deploy 上去。稍後我會用了大家用到爛的 WordPress 當範例，來示範整個過程。但是現在我想先展示內建的 Load Balance 功能，為了方便觀察，我先用 Tutum 提供的 Hello World 來熱身一下!

前面 STEP #2 #3 個別建立了 Local 及 Azure 兩個 Environment，這要做甚麼用? 兩個 Environment 各自獨立的兩組 infrastructure, 接下來的佈署動作你可以任意指定其中一個 environment 來執行。也就是本篇文章後面的操作你都可以任選一個地方來執行。

怎麼切換? 很簡單，右上角的 Environment 選單選完就好了...

![Environment Switch](/wp-content/uploads/2016/04/img_57225073588ee.png)

這邊補充一下 Rancher 的用語。以我的例子，我佈署的是整套 WordPress 服務。這整組服務就稱作 Stack, 而每個角色 (如 WEB，DB) 則稱作 Service，每個 Service 可能是由一個或多個 Container 組合起來的，那這就叫 Node。因此，你可以從管理介面上看到這些服務組成的關係，跟細節的相關資訊。

![Stack Configuration](/wp-content/uploads/2016/04/img_57222bf24eb00.png)

Applications > Stacks > Add Stack, 輸入你要建立的服務組態。這邊要是你用過 Docker Compose 的話，那麼這個介面一看就懂了，其實你就是把 docker-compose.yml 的內容傳上去或是直接貼上去就搞定了，你需要幾個 conainer, 彼此之間怎麼連結, 通通都是貼上後按 CREATE 就 OK~

這邊選用 tutum/hello-world 的用意是，它最簡單，而且會印出 container id, 稍後可以驗證 load balance 是否正常運作~

等 Rancher 佈署完成，連上對應的 IP / PORT 就可以使用了!

![Hello World Deployment](/wp-content/uploads/2016/04/img_57222ce1d6a74.png)

![Hello World Result](/wp-content/uploads/2016/04/img_57222dbf32386.png)

# STEP #5, Scale Out Your Service

如果你的服務要正式上線，通常 Scale Out, 設定 Load Balancer 提高服務能力，及提高可靠度都是必要的動作。到這個 Service 的頁面，Scale 的數值設定成你要的值，然後就靜靜地等 Rancher 幫你擴充 container 的數量就完成了 :D

![Scale Out](/wp-content/uploads/2016/04/img_57222d3b27ac3.png)

老實說這動作有點無腦... 不過要留意的是， Rancher 會替你把 container 分散在不同的 host 上面。如果你想挑選... 我還找不到很明確的方法來做這件事 XD

等它跑完後，當然可以執行。Rancher 會替你把每個 container 分配在不同的 host。由於還沒有啟用 Load Balancer, 因此要個別用不同的 IP 連到這三個 instance:

![Multiple Instances 1](/wp-content/uploads/2016/04/img_57222dbf32386.png)
![Multiple Instances 2](/wp-content/uploads/2016/04/img_57222da8cce29.png)
![Multiple Instances 3](/wp-content/uploads/2016/04/img_57222dd6387ea.png)

仔細看，這三個分別是 Host #1, #2, #3 的 IP address, 連到這三個不同的 container 也得到不一樣的 hostname ..

來試看看 Rancher 內建的 Load Balancer 怎麼用吧~ 回到 Stack, 在這組 Application 內新增 [Load Balancer] 這個服務:

![Add Load Balancer](/wp-content/uploads/2016/04/img_57222e40753c8.png)

![Load Balancer Config](/wp-content/uploads/2016/04/img_57222e6614ecf.png)

Load Balancer 的設定，你可以直接綁訂它要處理的 Target Services. 這邊可以跨越 Stack 連結 Services, 意思是你可以替好幾個不同的應用 (Stacks), 透過同一個 Load Balancer 服務來發佈它。設定完成後，改用 Load Balancer 的網址重新來看看這個 Tutum 的 Hello-World:

![Load Balancer Test 1](/wp-content/uploads/2016/04/img_57222efa89b05.png)
![Load Balancer Test 2](/wp-content/uploads/2016/04/img_57222f0e3fe62.png)
![Load Balancer Test 3](/wp-content/uploads/2016/04/img_57222f1f04992.png)

我可是重新整理按了好幾次，才湊滿這三張畫面的... 這證明了 Load Balancer 發揮作用了! 看它的官方文件，得知 Rancher Load Balancer 服務其實用的就是 HA-Proxy, 因此很多進階的設定檔也都可以直接使用 HA Proxy 的語法來進行。這邊就不多做說明，各位有需要研究可以參考官方網站的說明:  [Adding Load Balancers](http://docs.rancher.com/rancher/rancher-ui/applications/stacks/adding-balancers)

# STEP #6, In-Service Upgrade

服務上線之後，升級開始是個頭痛的問題了。這些線上服務，大概都沒辦法等你停個幾個小時升級後重新上線... 因此升級系統的程序也是件很頭痛的問題。Rancher 在這邊提供了一個不錯的功能: In-Service Upgrade (不知怎麼翻譯? 就地更新?)。

先來看看怎麼做吧，回頭再來說背後的原理... 這邊假定你的服務都是透過 Stack 的方式佈署，也就是背後都會有對應的 docker compose 設定檔。所以如何指派你的更新內容? 當然就是異動你的 docker compose 設定了。透過新的 docker compose 設定，Rancher 會替你把更新的 container 拉回來，替代你現在正在運作的服務。

![Upgrade Option](/wp-content/uploads/2016/04/img_572245251ccec.png)

首先，Rancher 很貼心的直接把 Upgrade 獨立成一個選項...

![Upgrade Configuration](/wp-content/uploads/2016/04/img_5722456271099.png)

之後就可以看到整個 Service 的設定畫面了，包含你的 container image 來源，container 環境設定，包含 port mapping, start up 參數，volumes .... 等等設定都可以在這邊調整。

不過重點不在有多少設定可以更改，重點在最上面那行... Batch Size, Batch Interval, 還有 Start Behavior... 這三個參數的作用各位先記著，後面再說明..

![Upgrade Process 1](/wp-content/uploads/2016/04/img_57224612a9f8f.png)

線上服務的升級，優先以不中斷服務為主要目的，因此前面不論你改了甚麼設定，Rancher 不會去更動任何 "既有" 的 containers. 畫面上可以看到 Rancher 開始用新的設定值，替你按照需求，建立新的 container。圖中 TutumHelloWorld 這個 Service 的 Scale 設定為 3，不過 Rancher 卻幫你建立第四個了... 這就是將要替代舊服務的 container.

![Upgrade Process 2](/wp-content/uploads/2016/04/img_572246be623eb.png)

再繼續等下去，會發現三個 containers 都已經被建立好，同時也自動啟動了 (畫面中還有一個的狀態是 Starting 啟動中)。

![Upgrade Process 3](/wp-content/uploads/2016/04/img_572247110c81d.png)

要替換的服務都準備好，也成功啟動後... 原有的 containers 就可以退役了，於是 Rancher 就自動替你停掉他們... 畫面中可以看到原有的 containers 開始一個一個進到 Stopping 狀態...

![Upgrade Process 4](/wp-content/uploads/2016/04/img_57224769ae0e1.png)

隔了一會兒，舊的 containers 都成功的停掉了，這時看看右上角的服務狀態，已經從之前的 "Upgrading" 變為 "Upgraded"。這時你可以實際測試看看，是否新的服務都正常運行?

接下來你有兩個選擇:

1. **Finish Upgrade**
   如果升級過後，你的服務一切正常，你就可以選擇 "Finish Upgrade"，告訴 Rancher 服務升級成功。它會替你回收舊的資源，也就是前面步驟被停掉的 containers.

2. **Rollback**
   當然升級也有可能失敗，一旦失敗的話，你可以選擇 Rollback，Rancher 會立刻幫你還原成升級前的樣子 (簡單的說，就是把新的 containers 停掉並且刪除，把原有的 containers 啟動)

這邊我就不抓 Rollback 的畫面了，給各位看一下 Finish Upgrade 之後會有什麼事情發生:

![Finish Upgrade 1](/wp-content/uploads/2016/04/img_572248b74e84a.png)

右上角的服務狀態，變成 "Finishing Upgrade"，而經過 user 的確認之後，原有的 containers 就變成 Removing 的狀態，Rancher 開始替你刪除回收這些資源...

![Finish Upgrade 2](/wp-content/uploads/2016/04/img_5722490655b73.png)

一切都完成後，服務狀態又回到正常的 "Active"，原有的 container 也已被移除，如果你畫面還沒刷新，那它會標示 "Removed"，如果你重新整理畫面，就會發現原有的 containers 完全消失了。

![Upgrade Complete](/wp-content/uploads/2016/04/img_57224961c4cab.png)

整個 Upgrade 程序，到這裡告一段落。這是我覺得最有用的部分，因為它大大解決了日常維運最常碰到的困擾啊... 其實整個流程並不難理解，但是過去同樣的動作，我都得自己下一堆指令... 下指令不是什麼難事，難就難在只要是人就醫訂有機會犯錯... 尤其在線上運作時，這些錯誤更難以接受... 這個功能就真的幫上大忙了!

回到前面說到 upgrade 的三個重要參數，就是告訴 Rancher 該用甚麼樣的 process 來替你執行升級的過程。看過這整個程序，在回過頭來看這三個參數，大概就不難理解它的意義了吧?

1. **Batch Size**:
   批次執行的數量。以上例來說，Batch Size = 1 代表一次只處理一個 container, 整個服務 scale 設為 3，代表你有 3 個 container 要處理，一次處理一個，完成了再進行下一個...。這部分要留意，如果你很在意線上服務不能中斷的話，切記這個數值不能太大，必須小於你的 scale 數值。否則升級的過程中可能某個關鍵服務的 containers 全部被你停掉了，或是留下可運作的 containers 數量太小，無法乘載升級期間的用量..

2. **Batch Interval (sec)**:
   顧名思義，批次處理過程中要間隔多久? 視你的服務需要多少時間 init 而定。

3. **Start Before Stopping**:
   新的 container 要先啟動? 還是原有的 container 要先停用? 有些服務你不希望新舊同時運作，有些服務你希望能不間斷的接軌... 是你需要而定。

整個 Rancher 管理介面，就這個功能最得我心... 當年一頭跳入 Azure 就是因為 Azure 的 Cloud Service 的升級程序做的實在太讚了。跟 Azure 的升級機制比起來，Rancher 小輸了一點... 就是:

> *Upgrade 版本上線前，沒有地方讓我先測試啊...*

這點用過 Azure 的就知道我在講什麼，只能讚嘆 Microsoft Azure 的 architect 實在太厲害，在六七年前 Azure 就能推出這樣等級的服務，當年 Azure Cloud Service 就已經有 Production / Staging Environment 的設計, 不用正式上線你就可以先行測試。測試滿意後只要 switch，一瞬間就切換上線了。不滿意再 switch 就 rollback ，這動作可以不斷的重複。進化到現在，Azure WebAPP 甚至可以讓你建立多組環境，不限於 Production / Staging 這兩套... 這點對服務中斷的程度，做的比 Rancher 還要徹底... Rancher 沒做到這個地步，算是有點小遺憾... 這是美中不足的地方。

最後，補一下 Rancher 官方的[說明文件](http://docs.rancher.com/rancher/rancher-compose/upgrading/) ([Upgrading Services with Rancher Compose](http://docs.rancher.com/rancher/rancher-compose/upgrading/))。雖然是搭配命令列操作的說明 (不是 GUI)，不過很多參數跟觀念說明的很清楚，有興趣可以參考。

# Summary

又是一篇不小心就寫太長的文章。這篇沒講到甚麼大道理，就是介紹我體驗 Rancher 的心得。為了想重現當年初次使用 Azure 的感動，特地用一樣的案例演練一次。重點在 Rancher 能替我解決那些問題，是否值得繼續使用?

希望這篇能幫助到有需要的人，要是你覺得這篇文章有幫到你的話，那就替我的粉絲專頁按個讚吧 :D

安德魯的部落格
[https://www.facebook.com/andrew.blog.0928](https://www.facebook.com/andrew.blog.0928)
