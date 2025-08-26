![from: blog.docker.com](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634e81ed3baf.png)

*from: blog.docker.com*

Microsoft 官方宣布能在 Linux 上面運行 .NET (v5) 應用程式.. 其實這已經不是什麼新聞了，去年 Microsoft TechEd 2014 North America 就正式的發布這個消息了，不過因為種種原因，去年看到這新聞的時候，只停留在 "看看" 的階段而已，直到現在時機成熟了才開始動手研究。一來是因為官方的開發工具 Visual Studio 2015 已經 RTM 了 (這麼大的軟體，實在不大想安裝 preview 版本).. 二來 Docker 用的很高興，NAS / Ubuntu Server 也都已經準備好，執行環境我也上手了.. 萬事俱備只欠東風，於是今天就趁周末，把 .NET Core 版的 "Hello World" 丟到 Docker 裡面執行的任務給搞定了 :D

Microsoft 自從新任 CEO Satya Nadella 上任後，宣布了一連串改變，我覺得對未來影響最大的就是 .NET Open Source + Support Linux 這件事了。我認為這決策帶來的影響，遠遠大於 ASP.NET5 本身開發技術及架構上的改變 (例如 MVC6.. 動態編譯.. Dependency Injection 等等)。因為前者影響的是整個 .NET 生態的改變，可能會影響到將來大型應用部屬的架構決策，而後者影響的只是開發團隊，完全是不同層級的問題..。如果你的職責是 system architect, 那千萬別忽略這個改變.. 以後 "混搭" 風格的架構一定會越來越盛行，不管是在 windows server 上面，或是在 Linux server 上都是。

在這兩年內，另一個很快竄起的技術: Docker, 也是另一個關鍵。Docker 這才出來兩年就紅翻天的 Container 技術，這種東西實在太對 architect 的胃口了。過去 VM 的技術沒甚麼不好，不過最大的問題就是: 充分虛擬化之後，帶來的副作用是多一堆 "虛擬" 的機器要管理... 每個 VM 裡面都要裝一套 OS，不論是 Linux or Windows，都要花力氣去維護，要執行這些 OS 也要花費運算資源... 舉個慘痛的經歷，我就碰過在同一台實體機器上，上面的 10 台 VM 都開始掃毒，那狀況真的只能用 Orz 來形容... 上面的 APP 都還沒認真在跑，系統就被 OS + AntiVirus 給拖垮了...

Docker 只虛擬化 Application 的執行環境，巧妙的避開了 VM 過度使用帶來的副作用... 舉例來說，如果你的應用規模不大，只要一台最低規格的 VM 就跑得動的話，你會為了架構考量把他分裝在三台 VM，實作三層式架構嗎? 應該沒人會這麼幹吧? 除非你要展示應用架構，或是可預見的將來會需要 scale out, 不然這樣搞只是自找麻煩而已。 但是現在用了 Docker 你就可以盡可能的採用你認為最理想的架構，分成幾個獨立的 container 可以維持架構上的正確性，同時也不必擔心架構帶來效能的折損。

因為這個原因，了解這種跨界的應用，對我來說遠比了解 ASP.NET5 本身 coding 帶來的改變還重要的多。裝了 Visual Studio 2015 之後，第一件事不是先寫看看 MVC6，而是先弄了個 Hello World, 試看看該怎樣丟到 Linux 上面跑.. 為了這件事，前置作業就花了快一個月... 有在 follow 我的 facebook 或是訂閱 blog 的就知道，之前我都在研究 Docker ，包括在 NAS 上用我理想的架構，來架設我自己的 blog.. 也[弄了台差點要被扔掉的舊筆電，架了台研究用的 Ubuntu Server](http://columns.chicken-house.net/2015/10/24/%e7%b5%82%e6%96%bc%e6%90%9e%e5%ae%9a-ubuntu-server-15-10/) .. 接下來主角要上場了，就是 .NET CoreCLR !

## 進入主題: .NET Core CLR 體驗

終於進入主題了 =_= ，要是各位跟我一樣長期使用 Microsoft Solution 的話，應該會踢到很多塊鐵板吧? 分享一下我如何讓自己跨進來的步驟，既然目標都很清楚了 (以 docker 為主要的執行環境)，所以我自己計畫的步驟是:

1. **先用最快的時間了解 Docker 是什麼? 可以怎麼應用? 如何實作?**  
我挑了最無腦的作法，從 NAS 上的 Docker 套件.. 我自己有台 Synology DS-412+ , 正好支援 Docker, 於是我自己挑了個實作的目標，就是把我原本的 Blog 搬回家，打算用 Docker 架設 WordPress。部落格再怎麼少人看，至少也是我的門面吧 XD，因此有些事情是省不掉的。例如我上一篇文章就提到 reverse proxy 把對外的 port / url 歸位這件事，還有整個 application 的維護及備份等等，都是不能忽略的部分。如果你不拿一個實際的應用來練習，那你做的只會是 POC (Prove Of Concept) 層級的事情，很容易就淪為 "啊! 成功了，會跑了" 之後就告一段落，很多實繼運作要顧慮的部分就不見了。想參考這段過程的，可以看[我這篇文章](/2015/10/13/docker-%e5%88%9d%e9%ab%94%e9%a9%97-synology-dsm-%e4%b8%8a%e9%9d%a2%e6%9e%b6%e8%a8%ad-wordpress-redmine-reverse-proxy/)。順利搬完部落格，至少讓我親身體驗 Docker 的應用方式。過去我是真的養了台 PC 架 windows server, 在裝個 VM 跑 windows server 來架站的，現在可以在 NAS 裡用同樣等級的架構作一樣的事，而運算資源只有以前的 1/4 不到 (NAS: atom 2cores, 1GB ram.. PC server Q9400 4cores, 8GB ram).. 我想優勢很明顯了.. 體驗過這一段，以後要如何把 Docker 應用在整體的系統架構內，心裡就有個譜了。

2. **親手架設實際的運作環境**  
NAS 的 Docker 使用實在太無腦了，害我以為裝實體 server 也是滑鼠按兩下就結束，結果真的是動手就吃鱉了 @@，過程我也不多說了，[上一篇文章](http://columns.chicken-house.net/2015/10/24/%e7%b5%82%e6%96%bc%e6%90%9e%e5%ae%9a-ubuntu-server-15-10/)有紀載 :D自己動手架設的好處是，你會親自走過安裝過程的所有細節，將來要 upgrade 或是 change configuration 就不會不知如何下手了。做到這步我才發現，NAS 廠商其實還蠻強的 XD，我自己用指令來管理 Docker 就已經一個頭兩個大了，找了一些 Docker Web UI 來用 (docker-ui), 發現也很難用 @@，但是 Synology / Qnap 自己的 Docker 管理介面就做得不錯...實際走過這段 setup ubuntu, configuration docker environment 之後，以後實際佈署時會碰到什麼問題，一樣心裡大概就有個譜了。

3. **進入主題，熟悉 .NET CoreCLR 的運用 (DNVM, DNU, DNX) 方式**  
這是這次的目的，我想先解決我最不熟悉的部分，往後的 Coding 我反而不擔心，好歹我有 2x 年的 coding 經驗，這應該難不倒我的... 所以我直接跳過 Coding, 拿了最基本的 Console Application, 寫了 Hello World, 以成功在 Docker 環境內執行為主要目標。這步驟搞定的話，後面的路就順了，就可以正式進入研究 ASP.NET5 的階段了這段就沒有連結可以看了 XD，對，沒錯，就是這篇文章。請繼續看下去!

## .NET Core CLR 的名詞定義

開始之前，先惡補一下，這次 .NET CoreCLR 的底層改變幅度很大, 如果只打算裝起來玩一玩按一按就搞懂的話，應該沒那麼簡單。幾個一定要知道的 keyword 我先筆記一下。推薦兩篇寫得不錯的介紹:

[![DNVM, DNX, and DNU - Understanding the ASP.NET 5 Runtime Options](http://typecastexception.com/image.axd?picture=give-my-regards-to-mr-escher-240.jpg)](http://www.codeproject.com/Articles/1005145/DNVM-DNX-and-DNU-Understanding-the-ASP-NET-Runtime)

**[DNVM, DNX, and DNU - Understanding the ASP.NET 5 Runtime Options](http://www.codeproject.com/Articles/1005145/DNVM-DNX-and-DNU-Understanding-the-ASP-NET-Runtime)**

Understanding the relationship between the .NET Version Manager (DNVM), the .NET Execution Environment (DNX) and .NET Development Utilities (DNU) is fundamental to developing with ASP.NET 5. In this post we will look at installing and using DNVM, DNX, and DNU on to work with ASP.NET from the command

[![What are DNX, DNVM, DNU and other ASP.NET 5 components?](http://www.dnnsoftware.com/portals/0/Images/DNN/communityDLSeal.png)](http://www.dnnsoftware.com/community-blog/cid/155264/what-are-dnx-dnvm-dnu-and-other-aspnet-5-components)

DNN: **[What are DNX, DNVM, DNU and other ASP.NET 5 components?](http://www.dnnsoftware.com/community-blog/cid/155264/what-are-dnx-dnvm-dnu-and-other-aspnet-5-components)**


In a previous post on the upcoming ASP.NET 'vNext' release, I covered all of the terminology around 'Project K' – which is what it was known as in early betas. Things have moved along a lot since then, and with that has come a change in terminology as the release gets closer. The trend of calling everything 'K' is no more – sadly in my opinion as I liked the quirkiness of it.

This post will cover the new terminology, relate it back to the Project K era terminology and relate that back to existing ASP.NET (1-4) concepts where possible. Again, this is intended as a primer for the existing ASP.NET developer to learn what is coming next and get themselves familiar with the changes.

底下就我自己整理的內容了。幾個名詞還是要先定義一下，否則看來看去腦袋會打結:

**Core CLR ( .NET Core Common Language Runtime )**

CLR 就是 Common Language Runtime, 套用 Java 的說法其實就是 VM，也就是能執行 .NET IL 的環境。包含 VM，JIT，還有 BCL (Base Class Library) 都算在內。而過去常講的 .NET Framework 就是所謂的 CLR，在 windows 平台上有完整的功能。Core CLR 則是重新包裝的可跨平台版本，包括 Linux / MacOS. Core CLR 有其他特性，向是 CLR 可以個別佈署，同時裡面的 BCL 都只需要佈署你用的到的部分即可。

**DNX ( .NET Execution Environment )**

.NET 的執行環境，可以執行及啟動 .NET app / ASP.NET 的命令列指令。一樣套用 Java 的說法，就像是對應到 java.exe 的東西，

![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634cc50c552f.png)

**DNVM ( .NET Version Manager )**

.NET 的版本維護工具，類似 APT-GET 這樣的命令列指令，用來維護及更新 DNX. DNX 各種版本的維護工具就叫做 DNVM，可別看到 VM 就以為是 Virtual Machine, 他是各種 DNX 的 Version Manager.

![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634cc306b7c5.png)

**DNU ( .NET Utilities )**

.NET 開發人員維護工具，有點像是 Java 的 Javac.exe, 可以進行 build, 下載或是更新相依的 NuGet 套件。

![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634cc6325694.png)

這幾個指令的關係搞清楚之後，今天的主角終於... 終於可以上場了。

## 將 .NET Core APP 放進 Docker 執行

[![Docker Toolbox](https://www.docker.com/sites/default/files/products/tbox.jpg)](https://www.docker.com/docker-toolbox)

第一步，首先你要有個 Docker 執行環境可以用.. 其實這是小事，你有 NAS 的話，規格別太差又剛好有支援 Docker 那你就賺到了，直接用就好。不然可以像我一樣自己裝一台 Linux, 或是用 VM 都可以。如果你甚麼都沒有，可以考慮看看用 Docker Toolbox (windows 版), 他包含了 windows 上的 docker client, 也包含了 VirtualBox 虛擬環境，還有一個包裝好的 Boot2Docker, 專為執行 Docker 而生的 Linux 開機 image.

我畢竟不是用 Linux 長大的那群人，對我而言能越簡單解決環境問題越好。因此我並不打算直接在 Linux 上安裝 DNX .. 我只想搞定 Docker 後，找 Microsoft 官方提供的 Container Image 來用。我用的是這個: [ASP.NET 5 Preview Docker Image](https://hub.docker.com/r/microsoft/aspnet/) ，抓下來後就有現成的執行環境.. 其他動作通通都省了，真的是適合我用的懶人包 XD

不過看了幾篇怎麼使用這 container image 的文章 (官方: [Running ASP.NET 5 Applications in Linux Containers with Docker](http://blogs.msdn.com/b/webdev/archive/2015/01/14/running-asp-net-5-applications-in-linux-containers-with-docker.aspx))，發現跟我要的不大一樣。官方都是教你要寫 DockerFile, 把自己的 application 包裝成一個新的 image, 然後丟進去 docker 執行.. 這樣是沒錯啦，不過我只想把我的 app 丟進某個現成的環境來測試，還不想搞到自己包 image ..

於是，花了點時間，總算找到切入點。多虧這個念頭，讓我沒有一步一步照著官方文件來走，也意外地讓我多了解了 Docker 的運作機制。Docker 提供一個跟外界隔離的應用程式的執行環境，但是裡面能執行的不一定只有我的 application 啊，也不一定只能執行一個。我可以多執行一個 shell, 對我來說就好像開了一個 VM 然後 ssh 連進去一樣，這就是我現階段想要的，將來有正式的佈署需求再來照官方文件進行就好。

環境搞定後，確定可以正確操作 DNVM, DNU, DNX 等指令後, 就幾乎達成我的目標了。方向想通了，剩下的舊是查察指令文件，找出正確的操作步驟就可以了。我最後整理下來的執行步驟是:

在 Docker Host:

1. 下載官方 image
   ```
   sudo docker pull microsoft/aspnet:1.0.0-beta8-coreclr
   ```

2. 啟動 container (daemon mode, 加上 -d)
   ```
   sudo docker run -d --restart always microsoft/aspnet
   ```

3. 查詢 container id:
   ```
   sudo docker ps -a
   ```
   ![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634db571dd81.png)

4. 在 container 內執行 bash, 同時進入互動模式直到 bash 結束為止:
   ```
   sudo docker exec -t -i 93462d92e941 /bin/bash
   ```
   ![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634dbc969491.png)
   這時 command prompt 已經變了，由原本的 chicken@localhost:~$ 變成 root@93462d92e941:/# , 代表 shell 已經啟動成功，且順利進去 conainer 內了，接下來我就可以把它當作 VM 開始大玩特玩..

5. 打開 visual studio 2015, 開 console app project, 寫一段不入流的 code, 印出 "Hello! .Net Core! " ..
   ![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634dcb340830.png)

6. 完成後，想辦法把檔案丟到 container 裡面... docker 提供 cp 這個指令，可以跨過 docker host / container 的界線 copy 檔案。細節我就跳過，總之 (5) 編譯出來的檔案，我放在 container 內的 /home/ConsoleApp1/ 目錄下:
   ![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634dd872b08f.png)

7. 接下來就是主要步驟了，先用 dnvm list 確認你能用的 dnx 版本，有需要可以用 dnvm install 來安裝，或是用 dnvm upgrade 來升級.. 我這次要用的是 coreclr x64 的版本:
   ![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634dde846dc0.png)

8. 進入 dnxcore50 的目錄，用 dnu restore 指令，確認所有相依的 package 都已存在 (若沒有的話會自動到 NuGet 去抓回來)
   ![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634de4cad27c.png)

9. 噹噹! 萬事俱備，最後就是執行了! 用 dnx 來跑我的 console application:
   為了避免有人誤會，我是用 windows command prompt 充數，順手把 OS information 印出來以資證明..
   ![](/images/2015-10-31-coreclr-helloworld-consoleapp/img_5634ded3b054b.png)

哇哈哈，終於成功了。看到我寫的 C# code 的控制範圍能擴大到 Ubuntu Server 上，那個成就感實在是不可言喻 :D 這次碰到最大的困難，是查到的指令都是講 ASP.NET 如何在 docker 上執行，可是我只是要 run console app 啊，沒找到文章把這整傳邏輯跟做法整理再一起，只好自己摸索...。好在當年學生時代有好好的學 unix (當年用 solaris ... 自己有用過一陣子的 linux.. ), 基本觀念跟 shell script 都還有，硬是闖出一條路。

就為了這行 "Hello .Net Core!", 花了我一個上午... 不過至少達到我的目標，把最基本的命令列執行成功了! 能夠親手在 Linux 上操作 dnvm, dnu, dnx 這幾個核心指令把程式跑起來，也算值回票價了 :D 這些步驟整理起來就當作我的筆記。應該有不少人跟我一樣，不熟 Linux 又想跨入這個領域的吧? 有需要的盡管取用，也歡迎分享這篇文章~