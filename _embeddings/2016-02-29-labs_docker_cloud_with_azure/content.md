![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d40b3783dce.png)

之前一直預告要在 Azure 上面快速佈署 Docker Engine / Container, 現在終於做到這一個步驟了。由於之前一直都是 Linux 的門外漢，所以講了一口好架構，但是真的要實作驗證時，總是碰到不少難關，現在一一克服了，就把這些過程整理一下~

<!--more-->

前面幾篇跟 Docker 相關的文章，都著重在單機的佈署跟管理上面。為了加速對基礎架構的了解，我都選擇自己動手下 docker 的指令來完成。不過實際上大規模管理時，應該要有更有效率的方式。有效率不代表不用指令，而是只靠單機的 docker engine 指令是不夠的。相關的幾套工具可以大幅簡化這個挑戰:

### Docker Machine

大規模的佈署，第一個挑戰就是你要快速的建立好幾個 Docker Host, 也就是建立已經安裝好 Docker Engine 的 Linux Server (實體 / 虛擬機器)。你要佈建 Docker Host 的地方，可能是你自己的 Data Center, 或是其他 Public Cloud Provider 都有可能。Docker Machine 的目的就是解決這個需求產生出來的管理工具，同時他的架構下也支援外掛各種不同的 Cloud Provider，因此你可以用一樣的指令，在 Azure、Amazon Web Service、Hyper-V、VMWare 等等 IaaS 或是虛擬化環境內，快速幫你建立大量 Docker Host 的管理工具。有興趣的讀者可以參考官方網站的說明: [Docker Machine Overview](https://docs.docker.com/machine/overview/)

### Docker Compose

如果你在意的是你的 Service 如何快速佈署在既有的基礎上，你需要的是 Docker Compose。已我自己的例子來說，最基本的 WordPress, 我會選擇分成四個 Container 來佈署我的服務:

1. **Reverse Proxy** - 用 NGINX 當作前端，用來處理新舊系統的轉址、網站發佈、Cache、Load Balance 等等任務
2. **Web** - 實際執行 WordPress 的 container
3. **DB** - 實際執行 MYSQL 的 container
4. **DATA** - 單純簡化管理 volumes 的 container, 選用的架構。實際上不需要啟動 (RUN)

單一一個服務就要建立四個 container, 還要指定彼此之間的連結，單靠 docker engine 的指令來做實在太辛苦了。Docker Compose 就是解決這類問題的好工具。你只要先把上述的架構寫成一個設定檔，接著一道指令下下去，就幫你把整組服務建立好了。

詳細的介紹，可以參考官方網站的說明: [Docker Compose Overview](https://docs.docker.com/compose/overview/)

### Docker Swarm

如果我佈署了好幾台 Docker Machine, 我也把我的服務都用 Docker Compose 規畫好了，下個問題就是 High Availability 了。舉例來說，我想提高 WordPress 的可用性，想把 WordPress 的 container 分別佈署在兩台 Docker Machine 上執行，一台掛掉或維護，另一台可以接手? 或是自動擴充，尖峰時刻兩台跑不動時，自動擴充第三台來分散流量?

這些問題，牽扯到 Docker Hosts 之間的溝通，也牽捨道 Container 的佈署調度，細節甚至包含多個 Docker Hosts 之間的資源調度 (RAM、CPU、DISK)，以及多個 Docker Hosts 間的網路通訊，這就是 Docker Swarm 想要解決的問題。一樣，詳細的介紹可以參考官網: [Docker Swarm Overview](https://docs.docker.com/swarm/overview/)

看起來架構是很漂亮沒錯，不過... 全部要自己實作實在是有難度啊，於是這幾個月我一直在嘗試各種能解決我這些困擾的工具 & 服務，過程我就略過不提了，最終我採用的是 Docker 官方的 Docker Cloud!

### Docker (官方) 的託管服務: Docker Cloud

![](http://static4.ithome.com.tw/sites/default/files/styles/picture_size_large/public/field/image/docker_cloud.jpg?itok=4E_uQGFh)

[Docker Cloud](http://cloud.docker.com) 是 Docker 旗下的服務之一，跟 Docker Hub 這公開的 Repository 都共用同一組帳號。Docker Cloud 前身是 Tutum，專注在提供良好的 Docker 託管服務。所謂的 "託管"，就是只幫你做管理而已，而 Hosting 這件事則是你自己處理，你可以用 Azure, Aws, 甚至自己準備機器都行，Docker Cloud 則提供了很好的整合介面及服務，幫你把這堆複雜的問題簡化成單一介面。

這邊我就不做太多介紹，我直接用這個案例，直接從頭到尾做一次，就知道有多簡單好用了。我挑的例子，就用前面說的 WordPress 好了，我想在 Azure 上面從無到有快速搭建我的 BLOG，那到底該怎麼做?

### #1, 事前準備 - 連結服務帳號

第一步，當然事先註冊帳號。如果你已經有 Docker Hub 帳號那可以直接沿用，沒有就註冊一個，過程我就跳過了。註冊成功後登入畫面會有介紹跟教學~

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3ec187fa12.png)

連結你其他雲端 IaaS 服務的帳號。Docker Cloud 支援這幾種，今天要示範的是 Windows Azure:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3ec9c9a41f.png)

點選 "Microsoft Azure" 這項的 "Add credentials", 會跳出設定視窗:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3ecf8a9fc9.png)

這邊要設定 Docker Cloud 跟 Microsoft Azure 兩者間的授權連結。你要先從 Docker Cloud 下載管理憑證，然後稍後把這個憑證上傳到 Microsoft Azure, 最後回填 Microsoft Azure 的 Subscription ID, 就完成整個授權的動作。完成之後 Docker Cloud 就能代表你去 Microsoft Azure 建立 VM 等等細節。

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3ede830a79.png)

在就版的 Microsoft Azure Management Portal 內，左方的 [設定]，切到 [管理憑證] 頁籤，上傳前一個步驟從 Docker Cloud 下載的憑證。完成後把你的 Subscription ID 填到 Docker Cloud 的畫面就大功告成!

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3eecb7485b.png)

整個截圖塗得很難看 =_=，各位將就一點 XD。看到這個畫面有認證成功的綠色小勾勾，就代表大功告成! 可以繼續往下一步邁進了!

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3ef3149f4f.png)

做到這邊要小心喔，之後 Docker Cloud 會代表你的身分，按照你的操作，替你在 Azure 上面建立需要的資源，像是 VM 或是 DISK 等等。這些都會產生額外的 Azure 費用。如果你不確定你做的動作會有甚麼影響，切記要隨時回到 Azure 的管理介面查看!

### #2, 開始佈署 - 在 Azure 上面建立 Docker Cloud Nodes

兩個服務的連結完成之後，接著就要開始準備 VM 了。雖然 Docker Cloud 支援連結你自己既有的 Linux Server, 不過我親自試過了，過程有點小麻煩，不但要自己設定防火牆，安裝 Docker Cloud Agent，同時 Docker Cloud Agent 還會自帶 Docker Engine ([商業化版本的 Docker Engine Commercially Supported](https://docs.docker.com/docker-trusted-registry/cse-release-notes/)), ，如果你的 Server 已經裝了 Docker, 則服務會被停掉並且移除。Microsoft 在 Azure 上預先為你準備的 Ubuntu + Docker VM, 在這邊派不上用場。我建議就全部從 Docker Cloud 上面，直接由她替你新增 VM，這是最簡單的步驟。以下我就這樣示範:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f08476c87.png)

先說明一下 Docker Cloud 管理的架構，後面都會用的到。整個管理介面分幾個部分:

**Welcome**:
資訊首頁，有教學、相關資訊等內容。

**Stacks:**
定義你的應用程式堆疊。你可以把她想像成管理 Docker Compose 設定的地方。每一項 Stack 都是由好幾個 Service 組成的。

**Service:**
定義你的服務，你可以把她想像成管理 Docker Container 的地方。這邊的 Service 是邏輯上的服務，實際上可以是由一個或多個 Container 組成。舉前面 WEB 的例子，WEB 是個 Service，但是為了做到 HA，可能由兩個 Container 組成。

**Nodes:**
就是 Docker Host, 實際連結能管理的 Docker Host 列表。你可以把這邊當成對等 Docker Machine 的功能。設定好的 Nodes, 將來你可以手動或自動的決定那些 Service or Container 要放在那些 Nodes 上。

OK，因此我們現在要建立第一個 Node，從 Docker Cloud 的 Nodes > Launch your first node，可以看到下列畫面:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f2084c3f1.png)

這邊你可以選擇你要在哪個供應商的服務上面建立 Node。這邊當然是選 Microsoft Azure, 你可以同時指定 Azure 的機房地點、VM 的規格、你要一次建立幾台、還有你的 Disk size 要配置多大。完成後按下確定，接下來等幾分鐘等她佈署完成就可以了。這邊我選擇的是 Basic A1 等級的 VM (1 CPU, 1.75GB RAM) + 額外的 60GB HDD

這邊提醒一下，很多進階的應用都需要一個以上的 Nodes, 不過 Docker Cloud 免費帳號只支援一個 Node, 因此這邊我就不做進階的示範了。多一個節點一個月要 USD $15 的費用，相當於每小時 USD $0.02 (對應到台幣 0.6 元/小時，或是 450元/月)。這只是託管的費用喔，VM 本身的費用 Azure 會另外跟你收... 需要多少就看個人需求了。

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f378625ea.png)

這個畫面大概會停個 5 ~ 10 分鐘左右。等待的過程中，我同時連到 Azure 的管理介面，看看他幫我採購了什麼資源?

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f3e2ab525.png)

果然，對應規格的 VM 被建立起來了...

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f41c2ef84.png)

對應的雲端服務 (管理需要，沒有額外費用) 也被建立起來了

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f471ce466.png)

如果你用的是新板的管理介面，那要在 "虛擬機器(傳統)" 這邊才看的到..

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f4da11d1b.png)

整個 VM 的運作狀況，都可以在這邊觀察的到

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f501f1a68.png)

其實什麼都不用作，只要等就可以了。等到完成後，你就可以開始佈署你的服務了! 到這邊這個階段也大功告成!

### #3, 開始佈署你的應用程式 (Stacks)

接下來就是跟你的服務相關的配置了。我先假定你知道 Docker Compose 是幹嘛用的，這邊就是用 Docker Compose 的觀念來設定你的服務。Docker Cloud 把它稱作 Stacks, 基本上是跟 Compose 相容的服務，但是有它額外延伸擴充的標記。這邊我就不額外說明，有興趣可以看它上方的 Docs ，會連結到他的官網，有詳細的說明。

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f5d4b39b5.png)

從 Stacks > Create your first stack, 就可以建立你第一個應用了。點選後會出現下列畫面:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f61ec1c0e.png)

這邊只有兩個設定，一個是你的 Stack name, 放的是整個服務的名字，我這邊填 "My Blog" 。Stackfile 則是放你的組態檔，你可以點下方 "try ours" 他會幫你填個範本進來.. 我這邊自己寫了一組:

```ini
db:
  image: 'mysql:latest'
  environment:
    - MYSQL_ROOT_PASSWORD=YES
  restart: always

web:
  image: 'amontaigu/wordpress:latest'
  links:
    - 'db:mysql'
  ports:
    - "80:80"
  restart: always
```

看的懂 Docker Compose 的設定檔的人大概就不用我多做解釋了。基本上就是標是我需要建立兩個服務: web / db. 標記每個服務用的 image file, 預設會到 http://hub.docker.com 去取得。啟用 container 的必要參數也都列在上面了，web 會連結到 db 這個容器，web 也宣告了要將 host 的 80 port 對應到 container 的 80 port...

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f76672a62.png)

按下 "Save and Deploy" 後，Docker Cloud 就會接著替你把後續的動作搞定了。從 Stacks 畫面可以看到，按照設定，兩個對應的服務 (db & web) 就按順序被建立起來了。一樣等 3 ~ 5 分鐘就好了。

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f7e2a6ca2.png)

服務都已經佈署完成，也都變成 Running 狀態了。其實到現在就已經全部完成了。但是... 我該怎麼連到我的部落格?

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f82f4f94a.png)

把 Stacks 的頁籤，從 Services 切到 Endpoints, 就可以看到這些服務所用到的 Endpoints 列表。Docker Cloud 替你整合了 DNS，直接幫你只定了你專屬服務的 FQDN，你可以省去自己搞 DDNS 的麻煩。如果不介意網址醜一點，其實這樣就可以用了。如果你想改成你自己的網址、在你自己的 DNS 加上一筆別名 (CNAME) 就可以了，比起過去我自己搞了 DDNS 等等，還裝 DDNS Client 定期自動更新 IP address 一堆東西弄半天，真是簡單太多 @@。

接著點選看看 URL:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d40dede7117.png)

果然，看到了 WordPress 第一次啟動的設定畫面...

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f915456de.png)

資料填完了，果然就可以登入管理畫面，開始寫 BLOG ..

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3f93be6559.png)

當然首頁也看的到了。到此為止，整個任務全部結束，你已經有一個穩定可靠的服務，在 Microsoft Azure 上面成功的運作，而且你也可以用 Docker Cloud 的管理介面輕鬆的維護他們。很簡單吧?

### 調整服務架構 - 重新佈署

接下來補充一些前面沒提到的細節。用過 Docker 的大概都知道，Docker Container 一旦建立之後，很多參數是沒辦法修改的，例如 Ports / Volumns 的對應，想修改只有砍掉重建一途。重建其實很簡單，但是如果當初建立的指令沒有留下來，要重打一次是很惱人的.. 有管理介面的好處就是讓你可以省掉這些功夫...

舉例來說，所有設定的源頭都是在 Stackfile.. 如果我調整了 stackfile 的內容:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3faf11839a.png)

修改的功能: Stacks > MyBlog > Edit, 修改內容後 Save

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3fb1e773ca.png)

Docker Cloud 會自動偵測有哪些服務需要重新佈署。在 Running 的狀態旁邊會有明顯的 ! 警告，你必須重新佈署 (Redeploy) 才會生效。你可以按上方的 Redeploy 按鈕，重新佈署整個 stack, 或是針對特定的 service / container, 只重新佈署特定的部分即可。重新佈署就是剛才提到，砍掉 container 重新建立一次而已，有是先做好規劃的話資料跟服務都不會中斷。

前面提到的 HA (High Availability)，在這邊就派上用場了。你可以點進去，把提供 web 服務的 containers 數量增加:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3fc58e48b4.png)

不過，因為我已經指名要對應 80 port, 你必須有第二個 node 才能佈署第二個 container, 因此跳出這個警告... 要避開這個限制，你可以指定動態的 Ports mapping。這麼一來，每個 container 不會占用同一個 port, 就不會有這個問題。不過這麼一來，你就必須再前端多架設一個 reverse proxy, 替 user 做 port 的轉址。各位可以自行想像一下.. 如果你成功的用兩個以上的 container 提供你的 service, 那麼在重新 redeploy 時，你只要一次 redeploy 一個，完成後再 redeploy 第二個，你的服務就完全不會中斷。

### 其他介紹補充

這篇是我另外準備的 demo, 實際上各位看到的 BLOG，我已經用同樣的方法，搬移到上個月敗家的 Mini-PC 上了，讓我快速搬移完成的，靠的就是之前準備好的 Docker Container, 以及 Docker Cloud 服務。給各位參考一下實際的案例:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d3feb916696.png)

這是我的 SERVER 上提供的所有服務 (stacks)，columns 就是這個部落格服務，裡面有 web / db, 而我還有其他服務都要共用 80 port, 因此我把 proxy 獨立成第二個 stack. 其他 issues 是 redmine, git 是 gitlab-ce 的服務，都是用一樣的方式建立的。會很麻煩嗎? 其實不會，從開始研究 Docker Cloud 開始，到建立完成，才花了一天不到的時間...

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d400b6d128b.png)

換個管理的角度，看看我的 node 上總共跑了那些 container? 當然也可以看所有的 endpoints, 或是用流水帳 (timeline) 顯示過去的操作歷程.. 我個人用的情況，機器是我自己的 (就是[上次的敗家文，對岸淘寶買的 MINI-PC](http://columns.chicken-house.net/2016/02/07/buy_minipc_server/))，加上只有一個 node, 因此 Docker Cloud 上的服務也是免費的。完全免費的情況下，能得到過去要用雲端大廠才擁有的 IaaS / PaaS 才有的服務，真的是太划算了。強烈推薦各位，有需要的話絕對值得試一試~ 如果實際工作上有需要，我想花一點費用來託管，省下一個專職的管理人力，也是很划算的。

補充一下前面都沒機會提到，就是 Docker Cloud 跟 Repository 的整合。Docker Cloud 提供每個免費帳號一個 Private Repository, 這個下次有機會再探討。今天先探討跟 Public Repository 整合的部分。你要單獨新增一個 Service 是很簡單的:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d40770622c5.png)

只要到 Services > Create service, 就可以跳到這畫面。我打了 keyword: wordpress, 就列出所有我可以用的 images:

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d407bda230e.png)

接著下一步，就是補上你的設定，按下 SAVE 就完成設定與佈署... 你的服務就可以上線了

![](/images/2016-02-29-labs_docker_cloud_with_azure/img_56d407ffa638c.png)

這樣的整合，遠遠比 NAS 廠商提供的介面更加優秀好用。反正只用一套都是免費，NAS 買了也就包含硬體部分的費用了。NAS 廠商以後是否有考慮內建跟 Docker Cloud 整合? 比如 NAS 保固期間，把 NAS 加入 Docker Cloud Nodes 則免費之類的 XD，這樣的話我會捧場!

### 後記

操作到這邊，是不是很簡單? 原本我只是想找個像 Synology Docker 一樣的管理介面來用，後來發現 Docker Cloud 已經遠遠超過我的想像了! 做這些 Hands On Labs, 總讓我有個感想，當年透過 Azure Cloud Service, 很簡單就得到這樣佈署管理的能力，讓我感動了很久。沒想到發展到現在，同樣層級的管理能力已經可以做到跨越不同的雲端服務了，甚至是我這種 Linux 新手自己自建的服務都可以做到這種層級的服務水準... 時代的進步果然是快到無法想像..

這篇就我自己留個紀錄，同時也提供給有需要參考的讀者們使用~