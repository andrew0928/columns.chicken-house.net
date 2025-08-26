![](/images/2017-07-25-wc-swarm-labs/Docker-Swarm-Orchestration-1024x265.png)

Azure 上面的 container 相關服務越來越完整了, 完整到我都快找不到理由自己架設了 @@, 從 registry 有 Azure Container Registry 可以，Orchestration 有 Azure Container Service 可用之外 (支援 swarm, dc/os, kubernetes), WebAPP 也開始支援直接部署 container,加上前兩天 preview 的 [Azure Container Instance](https://azure.microsoft.com/en-us/blog/announcing-azure-container-instances/) (把 container 當作超高效率的 vm 看待會比較好懂, 你自己準備 image 就可以丟上去跑)... 

不過 windows container 的支援總是慢半拍啊.. (敲碗), 加上我有些 Scenario 不得不再 intranet 架設這些環境, 因此還是硬著頭皮花了點時間研究 windows container + swarm mode.. 大部分的文章都是跟你講 linux container, 針對 windows container 的沒幾篇，中文的就更不用講了，我只好野人獻曝的貢獻這篇..

這篇交代兩個部分: 一是 windows container + swarm mode 的部署經驗。為了強調重點在於 swarm mode 的運用, 我選擇在 Azure 上面建置，
可以省去很多 OS 安裝設定的問題。另一部分就是 windows container 總是慢半拍, 先期導入的人 (對，就是我) 總是有些地雷要踩，後半部就是
分享一些目前還有陷阱的地方，讓現在就需要使用 windows container 的朋友們可以少走一點冤枉路。

其實這些服務，花個兩分鐘填一下資料，ACS (Azure Container Services) 就通通幫你搞定了啊，不過 ACS 對 windows container 的支援還在
preview, 我只好自己來土炮了。不過得力於 Azure 實在太方便，其實自己土炮一個 Windows Container Swarm Mode 的 Cluster 也只是五分鐘的事情啊! 要等下一篇文章出來再寫，大概又是一個月過去了，於是我就順手先把這篇紀錄一下，想在 Azure 上面體驗 Windows Container Cluster 的可以先參考這篇~



<!--more-->

# 安裝與設定

設定步驟其實很簡單，你只要先準備好一個有足夠餘額的 Azure Subscription, 沒有的話去[註冊](https://azure.microsoft.com/zh-tw/free/)一個就好。初次註冊 Microsoft 會給你免費的額度 (記得是 NTD 6300 ?)，要做這次的 Labs 其實很夠用了...

訂閱帳號搞定後，就開始吧!

## 建立 Windows 2016 VM (with containers) x 3

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-00-37-37.png)

這步驟其實還蠻無腦的，因為 Microsoft 早就幫你準備好了。建立 VM 時直接挑選  "Windows Server 2016 Datacenter - with Containers" 這個 VM image 即可。同樣的 VM 我們需要三台，分別命名為 wcs1, wcs2, wcs3。我這邊就用 wcs1 當作示範:

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-00-40-49.png)

其中 1, 2, 3 的步驟都只是選擇規格而已，我直接跳到第四個步驟 Summary 就好了。我這邊選用的是 Basics 系列的 VM, 全部的 VM 我都放在wcsdemo 這個 Resource group, VM 規格是 Standard DS2 v2, SSD, 除了 VM Size 之外其他都是用預設值就可以了。同樣規格 VM 開三台，訂購的按鈕用力按下去就好了。只要後面使用時的手腳快一點，其實花不了多少錢的 XDD

開好 VM 之後就先放著吧 (反正等他跑起來也要幾分鐘)... 趁這空檔先進行下個步驟。


## 建立 Azure Container Registry

既然都要用 Docker 了，能在同樣的環境下準備一個自己專用的 Registry 是一定要的。這邊要大推一下 Azure Container Registry 服務，真是
佛心啊，你只要支付 Storage 的費用就夠了，你 push 多少 images 在上面，付多少錢就可以了。Azure Container Registry 服務本身是不用錢的。如果一開始你都還沒 push 甚麼東西進去的話，那等於是 0 成本就可以有自己的 Registry 可以用了。於是我想都沒想就弄了一個... 

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-00-48-36.png)

新增服務的地方，搜尋一下，就會看到 "Azure Container Registry" ... 選這個就對了。

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-00-49-32.png)

除了取名字還有選機房地點之外，其實沒什麼要煩惱的，我都採用預設值就好了。以後有進階的需求再回來研究這些設定是幹嘛的..
這邊我取名為 wcshub, 請記好這名字，後面會用到。

"Create" 按下去，設定步驟就完成了。這時前面的三台 VM 應該都跑完了，我們可以繼續進行下一個步驟了。

![](/images/2017-07-25-wc-swarm-labs/2017-07-29-15-03-06.png)

另外，Access Keys 的設定項目哩，記得要 Enable Admin User, 還有設定一下存取的密碼... 後面要 push images 時需要用到。

## 設定 Swarm Cluster

> 以下這個部分 "設定 swarm cluster" 的動作，將來若是 Azure Container Service 正式支援 windows container 之後，就通通可以省略了，在那之前，我就提供這些說明給大家參考...

接下來，就用 RDP 逐一連到剛才建立的三台 VM (wcs1, wcs2, wcs3)。Windows Container 微軟已經預先安裝好了，我們只需要設定 Docker Swarm Cluster 即可。

我這邊會把 wcs1 當作 master node. 先 RDP 到 wcs1, 開個 DOS command prompt 出來:

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-00-54-57.png)

Docker Swarm 的架構是，Cluster 內至少需要挑一台出來做 Manager, 負責分派資源。初次建立 Swarm Cluster 時，第一台就會是 Manager.
在 wcs1 下這道指令:

```shell
docker swarm init --advertise-addr 10.0.0.4 --listen-addr 10.0.0.4:2377
```

其中 10.0.0.4 是 wcs1 這台 VM 的 ip address, 成功之後就會看到如下的畫面，也會列出其他 node 要如何加入 cluster 的指令。
```SWMTKN-xxxxx``` 那串 ID 就是要加入 swarm cluster 必要的 TOKEN，這段指令可以先保留下來... 後面加入其他節點時會用的到。


第一台 (wcs1) 搞定後，把另外兩台加進來就好。同樣的 RDP 到 wcs2 及 wcs3, 開 DOS command prompt 下這道指令 (其實就剛才那指令
複製貼上而已):

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-01-00-25.png)

看到 ```This node joined a swarm as a worker.``` 就代表成功了。

這兩台都做完這道程序之後，就.... 就全部完成了。老實說沒有 ACS 整個包一包，好像也沒有差多少... 哈哈!
設定步驟現在已經全部完成，接下來就可以真的 deploy service 到你專屬的 docker swarm cluster 了。





# Deploy Service On Docker Swarm

接下來就是真的把 container 丟上去跑看看了。原本我打算拿 hello-world, 不過這個例子實在顯示不出 docker swarm 的威力啊，
於是我就把之前 Visual Studio Everywhere - 20th 週年紀念的研討會，講 Windows Container 場子用的範例拿出來獻醜了.. :D


## Push Image to Registry

首先，我們既然都有 private registry 可以用了，就不用再大老遠跑到 hub.docker.com 下載 images 了。第一件事先把我們自己的 container image push 到 private registry 內。以我這次要用的 Visual Studio Everywhere - 20th Demo 為例:


先登入 private registry:

```
C:\>docker login --help

Usage:  docker login [OPTIONS] [SERVER]

Log in to a Docker registry

Options:
      --help              Print usage
  -p, --password string   Password
  -u, --username string   Username

C:\>docker login -u wcshub -p ******** wcshub.azurecr.io
Login Succeeded

C:\>
```

接著我們就可以把本機的 images push 到 private registry 了。你可以自己在本機 build images, 或是從外面 pull 回來都可以。只是 container image 本身的 name 就已經包含 registry 的 location 了，因此我們要 push 到 private registry 的話，image name 格式必須是 {registry name}/{image name}:{tags}

來看個例子，我先把我放在 hub.docker.com 的 andrew0928/vs20:latest 這個 image 拉回來，給他個新名字 wcshub.azurecr.io/vs20:latest, 然後再把它 push 到我們自己建立的 private registry:

```
docker pull andrew0928/vs20:latest
docker tag andrew0928/vs20:latest wcshub.azurecr.io/vs20:latest
docker push wcshub.azurecr.io/vs20:latest
```

以下是完整的 logs (包含 output message):

```
C:\>docker images
REPOSITORY                    TAG                 IMAGE ID            CREATED             SIZE
microsoft/windowsservercore   <none>              2c42a1b4dea8        2 weeks ago         10.2 GB
microsoft/windowsservercore   latest              015cd665fbdd        6 weeks ago         10.2 GB
microsoft/nanoserver          latest              4a8212a9c691        6 weeks ago         1.04 GB

C:\>docker pull andrew0928/vs20:latest
latest: Pulling from andrew0928/vs20                                                                                    3889bb8d808b: Already exists
3430754e4d17: Pull complete
7aee39cd34f9: Pull complete
5b8e6b632025: Pull complete
e067d71858d2: Pull complete
b631fefd9523: Pull complete
511d8c25970e: Pull complete
5d202c6e7498: Pull complete
60cb3c596b19: Pull complete
Digest: sha256:f6809287ab6fbfcf51e39531f43fed08dbbcb4479e377682caddfb276a1f1a92
Status: Downloaded newer image for andrew0928/vs20:latest

C:\>docker tag andrew0928/vs20:latest wcshub.azurecr.io/vs20:latest

C:\>docker images
REPOSITORY                    TAG                 IMAGE ID            CREATED             SIZE
microsoft/windowsservercore   <none>              2c42a1b4dea8        2 weeks ago         10.2 GB
microsoft/windowsservercore   latest              015cd665fbdd        6 weeks ago         10.2 GB
microsoft/nanoserver          latest              4a8212a9c691        6 weeks ago         1.04 GB
wcshub.azurecr.io/vs20        latest              4688e759642f        4 months ago        10.1 GB
andrew0928/vs20               latest              4688e759642f        4 months ago        10.1 GB

C:\>docker push wcshub.azurecr.io/vs20:latest
The push refers to a repository [wcshub.azurecr.io/vs20]
d7a84b067064: Pushed
21656e4ec85b: Pushed
d8d98fa867ec: Pushed
1fd8bf94df89: Pushed
5b4aace84103: Pushed
1f2f3eb32edc: Pushed
0451551dda21: Pushed
c28d44287ce5: Skipped foreign layer
f358be10862c: Skipped foreign layer
latest: digest: sha256:f6809287ab6fbfcf51e39531f43fed08dbbcb4479e377682caddfb276a1f1a92 size: 2414

C:\>
```

到這邊，你的 images 就都已經放在 private registry 裡面了。其實就算不經過這步驟，直接從 hub.docker.com 拉回來也可以。
只是我會強烈建議，如果是你自己開發維護的 images, 那還是放 private registry 比較好，尤其是妳搭配 docker swarm 的時候。
因為到時每個 swarm node 都必須直接到 registry 拉一份 image 回來，如果你的 nodes 越多，越會感受到速度的差別。


## Create Service

這個 container image 早已放在 hub.docker.com 上面, source code 則已經放上 github.com 了。他就是個標準的 ASP.NET MVC
範例而已，只是在這個 web app 的 about 頁面，會標記 server ip address, 方便我們驗證 cluster 的效果。

正常情況下，我要執行這個 container, 會用這道指令啟動它:

```shell
docker run -d --name mvcdemo -p 80:80 wcshub.azurecr.io/vs20:latest
```

現在改成部署到 docker swarm cluster, 我們可以在 manager node 用這道指令來部署並啟動:

```shell
docker service create --name mvcdemo --mode global -p 80:80 wcshub.azurecr.io/vs20:latest
```

**Note**: 正常的狀況下，這道指令就可以直接執行了。不過現在我們用的是 private registry, 需要經過認證 (login) 才能存取，因此步驟複雜一點。上述這道指令應該會看到錯誤訊息: 

```
C:\>docker service create --name mvcdemo --mode global -p 80:80 wcshub.azurecr.io/vs20:latest
unable to pin image wcshub.azurecr.io/vs20:latest to digest: Head https://wcshub.azurecr.io/v2/vs20/manifests/latest: no basic auth credentials
```

最後找出來的解決方式是: 每一個 node (此例包含 wcs1, wcs2, wcs3) 都先執行過前面提到的 docker login 指令，除此之外讓 docker swarm
在 create service 時，送出 auth/z header..
修正後的指令，要加上這段: ```--with-registry-auth```

```
C:\>docker service create --name mvcdemo --with-registry-auth --mode global -p 80:80 wcshub.azurecr.io/vs20:latest
```

唯一美中不足的是，docker login 的動作目前看來還只能每台一個一個先去做一次，還沒找到能一次在 cluster 端就一勞永逸的解決方式。


在一般的 docker run 指令裡面, 邏輯上是把一個 image 透過 "run" 的指令，同時建立 container 並且啟動 (start) 他。
這觀念搬到 docker swarm, 則改成把一個 image 透過 "create service" 的指令，在 cluster 內建立這個 "service" 。
因此這邊的幾個參數，意義就跟 docker run 的情境下有些不同:

* --name: service name, not container name
* --mode: 服務的模式。global 代表在這個 cluster 內的每個 node (包含 manager) 都要部署一份 container, 若 mode 是 replica (預設值), 則代表由 manager 替你分配要在哪幾個 node 啟動你的 container (會按照後面指定的啟動份數 --replicas nnn 決定)。
* -p: publish port settings, 這個就沒什麼不同了，不過發布 ports 的規則在 cluster 環境下就有點複雜，後敘
* <image>: 最後面依樣是 container image name + tags, 後面也可以加自訂的 command + arguments, 這部分跟 docker run 一樣，都是啟動 container 的參數


接下來，要查詢所有的 service 有哪些, 跟執行的狀態，就不再是 ```docker ps``` 了，改成這兩個:

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-01-39-05.png)

啟動的過程中，wcs3 不知碰到啥問題，看來第一次啟動是失敗的，所以有個 container 後來被 shutdown 了，第二次啟動才成功。因此 wcs3 有兩筆 container 的 PS 紀錄。

總結一下指令用途，若要查詢 cluster 到底有多少 service，可用這指令:

```
docker service ls
```

查詢某個 service 的 container 執行狀況:

```
docker service ps {service name}
```

最後，服務都正常啟動了，我們就直接來開瀏覽器確認看看 (記得打開 Azure VM 的防火牆)

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-01-42-16.png)


結果，我沒辦法透過瀏覽器看到 vs20 這個 container 執行的結果啊... 之前在這裡卡關卡了一陣子... 先講解法:

原本建立服務 (service create) 的指令，把 publish port 的部分改成這樣:

```
docker service create --name mvcdemo --with-registry-auth --mode global --publish mode=host,target=80,published=80 wcshub.azurecr.io/vs20:latest
```

![](/images/2017-07-25-wc-swarm-labs/2017-07-29-22-15-31.png)

這次的 PS 結果，就看的到 port mapping 了。這時用瀏覽器，分別連到三個 node 的 public ip address, 可以看到三個 container 都正常的執行:

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-01-47-02.png)
從 wcs1 的 IP 連線

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-01-47-24.png)
從 wcs2 的 IP 連線

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-01-47-33.png)
從 wcs3 的 IP 連線

可以看到三個 instance 的 ip address 都不大一樣。這個沒有 load balance 的效果，三個 container 跟三個 node 是一對一的，
你重新整理後還是會看到一樣的 server side ip address, 不會亂跳。





# Overlay Network

前面的 network 設定是怎麼回事? 老實說這個指令的背後藏了很多東西啊，我也是花了些時間才搞懂。這也是 docker swarm 的精隨，值得
花些時間了解 & 掌握他的用法。

首先，先來談談什麼是 "overlay network" 吧。在單機版的 docker engine, 我們最常用的就是 nat, 每個 container 都可以拿到一個
內部的 ip address, 如果你需要的話, 再透過 -p 的指令，在 NAT 上面開個 port, 轉接到 container 內部的 port.

同樣的架構，換成 docker swarm 就行不通了, 因為你的 node 不只一個, nat network 的 lan 是無法跨機器的。這個部分沒打通的話，
在 cluster 內的多個 container 就無法無障礙的互相溝通了。為了解決這個問題，docker swarm 在 init 時，就會自動建立一個名為
"ingress" 的 overlay network:

![](/images/2017-07-25-wc-swarm-labs/2017-07-27-01-54-33.png)

顧名思義，他是 "overlay" 在實體網路上，建立的虛擬私有網路, scope 是在整個 swarm 內都可以看的到，意思是整個 swarm cluster
都可以共用這個 overlay network。

所以，我們第一次使用的指令，只是單純地用 -p 80:80 代表甚麼? 就是我前面提到的 "routing mesh", 意思是每個 node 的 public port 80,
都會對應到這個 service 的每個 instance 的 port 80...

有點抽象? 看這張圖就懂了:

![](/images/2017-07-25-wc-swarm-labs/ingress-routing-mesh.png)

圖片來源: docker docs / [Use swarm mode routing mesh](https://docs.docker.com/engine/swarm/ingress/#publish-a-port-for-a-service)

docker swarm 會替你把這個 service 發佈到每個 node 的 port 80, 同時用內建的 load balancer, 替你把負載分散到所有的 service instance. 這種模式之下，你可以指定任意個數的 service instances, 這個例子之中，我們有 3 個 nodes, 你可以部署 1 個 instance, 也
可以一次部署 10 個 instance。對外不論你連到哪一個 node 的 80 port, routing mesh 的機制都會替你搞定他，讓你可以正確地連到指定的服務。

聽起來很棒，唯一美中不足的是....

參考資料: microsoft docs / [Getting Started with Swarm Mode](https://docs.microsoft.com/en-us/virtualization/windowscontainers/manage-containers/swarm-mode)

> **Note:** The second argument to this command, `--endpoint-mode dnsrr`, is required to specify to the Docker engine that the DNS Round Robin policy will be used to balance network traffic across service container endpoints. Currently, DNS Round-Robin is the only load balancing strategy supported on Windows.[Routing mesh](https://docs.docker.com/engine/swarm/ingress/) for Windows docker hosts is not yet supported, but will be coming soon. Users seeking an alternative load balancing strategy today can setup an external load balancer (e.g. NGINX) and use Swarm’s [publish-port mode](https://docs.docker.com/engine/reference/commandline/service_create/#/publish-service-ports-externally-to-the-swarm--p---publish) to expose container host ports over which to load balance.


實在是很 OOXX 啊... 研究到這邊，正很興奮地要使用他的時候，才看到這段... *"Routing mesh for Windows docker hosts is not yet supported, but will be coming soon."* 這時只能很忠誠的相信 Microsoft 說的 "coming soon" 了... 官網這篇文章是 2017/02/09, 現在是 2017/07/26, 就看看還要多久...



# DNSRR (Docker Native DNS Round Robin)

好，既然這樣只能退而求其次。Microsoft 看來還是給了另一條出路啊，透過 Docker 內建的 DNS，可以用 DNSRR (DNS Round Robin) 搭配
你自己建立的 load balancer (例如我之前用的 NGINX for windows) 一樣可以做到類似的效果。不過按照文件，我應該可以用 Docker 內建的
Native DNS Server 取得其他 container instances 的相關資訊才對，不過這邊我卻怎麼試也試不出來 @@

這邊就分享一下我的研究過程吧，有專家的話，幫忙看看我是漏了哪個環節...


先把前面所有的 service 清掉，重新建立 docker swarm services, 指定 dnsrr, 在這 3 個 nodes 中啟動 5 個 instance:

```shell
docker service create --name mvcdemo --with-registry-auth --network ingress --endpoint-mode dnsrr --replicas 5 wcshub.azurecr.io/vs20:latest
```

啟動完成後，看看執行狀況:

```shell
docker service ps mvcdemo
```

![](/images/2017-07-25-wc-swarm-labs/2017-07-28-00-59-28.png)

這些 instance 被分配到 wcs1 ~ wcs3 個別執行中。另外再開個 console service:

```shell
docker service create --name console --with-registry-auth --network ingress --endpoint-mode dnsrr --replicas 3 microsoft/windowsservercore ping -t localhost
```

挑一台 console 的 instance, 開個 cmd 連進去 (xxxxxx 是 container id, 每次都不一樣，我就不列了):

```shell
docker exec -t -i xxxxxx cmd.exe
```

結果進去 query dns, 找不到所有的 mvcdemo instances 的 ip address 啊 @@

![](/images/2017-07-25-wc-swarm-labs/2017-07-28-01-16-29.png)


不過，如果先查好其他 container 的 ip address, 連進 console 用 ping 的就可以 ping 的到啊...

![](/images/2017-07-25-wc-swarm-labs/2017-07-28-01-18-16.png)

看來除了 Docker Native DNS 不會動之外 (當然也用不到 DNSRR)，其他一切正常.... 可是少了 DNS, 最關鍵的 service discovery 就沒辦法用了啊，如果我要用 nginx 當作 reverse proxy + load balancer, 我總不能每次 containers 啟動後都要手動去更新 upstream ip address 吧 @@

好吧，按照規格跟文件的話，上述的測試，應該可以在其他同個 docker network 內, 可以透過 dns (round robin) 的方式, 用 service name
找到其他 container instances 才對。這時其他服務就能正確地找的到對方。你也可以視需要，直接動態調整每個 service instances 數量，
對於大型服務的部署來說是非常方便的。

可惜這功能目前僅存在於文件及規格中，我還試不出來 T_T，我看我還是等等那個 "coming soon" 的 routing mesh 吧...


# 後記

這篇不像之前一樣，會講一堆架構面還有規畫面的目的等等，單純的說明設定及操作的細節而已，因為目前專門說明 windows container 的文章終究是少數啊，因此想說有餘力就可以貢獻一些經驗。Container 是個好東西，我相信將來一定是所有開發團隊及維運團隊都會需要的技能。只要你部署的環境的機器數量不只一台，container orchestration 就是必要的觀念跟技能了。這時 docker swarm 絕對是個你必須熟悉的技能 (因為它是內建的)。即使你選擇的是其他 orchestration 系統，如 Kubernetes 等等，我相信這些操作的方式跟觀念也是有幫助的。

過去很多開發技術，如 Java 等等，想要強調 write once, run everywhere 的理念，最後都沒落實。因為 Java 雖然能達到 binary code 跨平台執行，但是終究沒辦法統一執行環境與部署問題啊。Docker 走了另一條不一樣的路，把 app 執行環境的封裝格式 (image) 跟整個部署機制的生態系 (registry) 都標準化了。兩大陣營的 OS (linux + windows) 都共用同樣的 ECO system, 在 OS 支援的前提下, 真正實現了 package once, run everywhere。

接下來，值得期待的是 windows hyper-v container 開始內建支援 linuxkit 與直接支援 linux container, 到時不論是 windows container 或是 linux container, 通通都可以直接 docker run 就能執行，等到那個時候, container 就真正變成通用的執行封裝標準了。如果你問我甚麼時候適合學習 docker ? 最適合的時間就是四年前或是現在! :D