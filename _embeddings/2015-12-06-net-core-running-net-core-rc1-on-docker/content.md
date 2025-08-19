---
layout: post
title: "[.NET Core] Running .NET Core RC1 on Docker - DOTNET CLI"
categories:


tags: [".Net Core","C#","Docker"]
published: true
comments: true
permalink: "/2015/12/06/net-core-running-net-core-rc1-on-docker/"
redirect_from:
wordpress_postid: 560
---

[![Microsoft Connect 2015](/wp-content/uploads/2015/12/connect14-300x170.jpg)](/wp-content/uploads/2015/12/connect14-e1449308872383.jpg)

在半個月前，Microsoft Connect 2015 大會上正式宣布 .NET Core / ASP.NET 5 正式推出 RC1. RC 代表開發已經到了準備 release 的階段 (RC: release candidate), 功能都已完備 (FF: feature freeze), 品質也到一定的階段，RC 推出後若沒碰到重大問題，那接下來應該就是 RTM 了。

若你擔心 Beta 跟最終的版本落差太大，而不願意太早投入了解 .NET Core 的話，那現在是個適合的時間點了! 這次除了版本進展到 RC1 之外，Microsoft 除了在 Docker Hub 釋出了新版的 image 之外，也推出了另一個新的命令列工具集: DOTNET CLI, 同樣也提供 Docker Container 的 Image 可以使用。

原本開始研究 Docker, 目的是為了有個簡易上手的 .NET Core / ASP.NET 5 在 Linux 上面執行的環境而已，我真正的目標是了解 .NET Core 跨平台的轉移過程，以及跨平台帶來的效益 (單純的在 Linux 上執行並不是重點，而是在 Linux 上面執行後可以帶來其他的資源跟優勢，以及對企業大型佈署可以獲得的效益) ...  不過這陣子越玩越大，研究 & 體驗的範圍也擴大到正式佈署上會用到的幾個重要服務 (apache, nginx, docker, mysql ... etc)，加上拿了我自己的部落格當白老鼠實際體驗，弄到現在才回到正題 =_=，正好趁那些偏離主題的研究告一段落，現在正好回頭來試試! 接著下去之前，先看看官方發布的消息:

# *[Announcing .NET Core and ASP.NET 5 RC1](http://blogs.msdn.com/b/dotnet/archive/2015/11/18/announcing-net-core-and-asp-net-5-rc.aspx)*

[![image_3](/wp-content/uploads/2015/12/image_3.png)](http://blogs.msdn.com/b/dotnet/archive/2015/11/18/announcing-net-core-and-asp-net-5-rc.aspx)

*Today, we are announcing .NET Core and ASP.NET 5 Release Candidate, supported on Windows, OS X and Linux. This release is "Go Live", meaning you can deploy apps into production and call Microsoft Support if you need help. Please check out the [Announcing ASP.NET 5 RC blog post](http://blogs.msdn.com/b/webdev/archive/2015/11/18/announcing-asp-net-5-release-candidate-1.aspx) to learn more about the updates to ASP.NET 5.*

這篇我分幾個角度來探討 .NET Core. 如果你是想看 Step by step 的教學，或是想看看新版本有甚麼功能，或是哪裡下載等等，那請直接 Google 新聞或是官網就可以了。我的重點會擺在我的研究過程發現的心得，一些官方文件上沒寫的資訊，以及我研究過程得到的結論跟想法等等。接下來這系列我會談到這幾個主題，一篇寫不完的話就請各位等待續集了~ Progrmming / Coding 相關的探討，我本來就會定期分享，因此這系列文章我會著重在跨平台以及 .NET Core 本身的改進，還有原本就用 Microsoft Solution 的企業，導入 .NET Core + Linux 後帶來的效益。主題包括:

1. DOTNET CLI, 跟 BETA 時期的 DNX / DNVM / DNU 的關係
2. DOTNET CLI 搭配 Docker 的使用技巧
3. CODING 實際上機: Hello World (Console)
4. (下回分曉) Inside .NET Core Runtime, Windows / Linux 的差異 #1, Compute PI (performance)
5. (下回分曉) Inside .NET Core Runtime, Windows / Linux 的差異 #2, Memory Fragment Test (memory management)
6. (下回分曉) (還在想...)

這次不碎碎念了，直接從第一個主題開始!

# 新玩意: DOTNET CLI, 整合 DNVM / DNX / DNU 的命令列工具

隨著這次的 RC1 Announcing, 原本 Beta 時代的那些命令列工具, 也開始有新版本了。原本的工具分別負責 RUNTIME 的管理 (DNVM)，執行 (DNX)，維護 (DNU).. 現在被集中在同一個指令 dotnet 底下了，也就是這次新發布的 DOTNET CLI。

不過這個 CLI (Command Line Interface) 版本還很前期，看她的編號才 0.01 alpha , 離正式版本還很久，因此這次是分成兩個 container image 發行:

- [microsoft/aspnet](https://hub.docker.com/r/microsoft/aspnet/): 這個 image 還是跟[上次介紹文章](/2015/12/06/net-core-running-net-core-rc1-on-docker/?p=384)寫的一樣，用的是 DNVM / DNX / DNU 這組指令，指示相關的版本已經升級到 RC1，使用方式跟前幾篇文章介紹的都一樣，這次就略過，後面應用測試時有需要再拿他出來..
- [microsoft/dotnet](https://hub.docker.com/r/microsoft/dotnet/): 這個則是另一個新的 image, 裡面放的就是 .NET Core 新版的命令列工具 (v0.0.1-alpha preview). 功能差不多，不過比之前有組織的多。DNVM / DNX / DNU 這些指令第一次看到還真的會搞混，從名字完全看不出是幹嘛用的，新版工具的命名就清楚的多，同時也追加了一些新功能，像是編譯成 Nativa Code 等等，這些是之前 Beta 版時期還沒有的機制

# DOTNET CLI Container 的使用技巧

開始介紹我的使用方式錢，先把幾個關鍵的參考資訊貼一下... 現在的參考資料還不是很多，除了官方少少的幾份資料之外，碰到問題根本還 Google 不到甚麼東西，只能自己憑經驗摸索 @@

1. 來自 Microsoft GitHub 的 Readme: [.NET CLI Preview Docker Image](https://github.com/dotnet/dotnet-docker)
2. 來自 Microsoft GitHub 的 Quick-Start 說明: [It is very easy to get started with .NET Core on your platform of choice.](https://dotnet.github.io/getting-started/)

其他我參考過的相關資料還有這幾篇:

1. [ASP.NET 5 and .NET Core RC1 in context (Plus all the Connect 2015 News)](http://www.hanselman.com/blog/ASPNET5AndNETCoreRC1InContextPlusAllTheConnect2015News.aspx)
2. [.NET Blog / Announcing .NET Core and ASP.NET 5 RC](http://blogs.msdn.com/b/dotnet/archive/2015/11/18/announcing-net-core-and-asp-net-5-rc.aspx)
3. [.NET Web Dev and Tools Blog / Announcing ASP.NET 5 Release Candidate 1](http://blogs.msdn.com/b/webdev/archive/2015/11/18/announcing-asp-net-5-release-candidate-1.aspx)
4. [ScottGu's Blog](http://weblogs.asp.net/scottgu/) / [Introducing ASP.NET 5](http://weblogs.asp.net/scottgu/introducing-asp-net-5)
5. [Scott Hanselman](http://www.hanselman.com/blog/) / [Visual Studio 2015 Released plus ASP.NET 5 Roadmap](http://www.hanselman.com/blog/VisualStudio2015ReleasedPlusASPNET5Roadmap.aspx)

OK, 參考資訊交代完，來看 Hands-On Lab 吧. 在過去幾篇文章哩，我都只把 Container 當成像 VM 一樣使用，把 SERVER 裝在裡面開起來用。然而 Container 實際上可以不用像 VM 隔離的這麼遠，他是能退化成單一應用程式來使用的.. DOTNET CLI 在 GitHub 的 README 也教你這樣用:

## *[Compile your app inside the Docker container](https://github.com/dotnet/dotnet-docker)*

*There may be occasions where it is not appropriate to run your app inside a container. To compile, but not run your app inside the Docker instance, you can write something like:*

```bash
$ docker run --rm -v "$PWD":/myapp -w /myapp microsoft/dotnet:0.0.1-alpha dotnet compile
```

*This will add your current directory as a volume to the container, set the working directory to the volume, and run the command `dotnet compile` which will tell dotnet to compile the project in the working directory.*

其實關鍵就在中間 Docker 用的指令: "--rm" 會在這個 Container 執行完畢之後立即刪除它的狀態，等於你這個 Container 變成可拋棄式的 Container 了，以這個範例來說，用 Docker Run 啟動 Container, 透過 -v 掛載目錄，用 Container 內的編譯工具編譯你的 APP，結束之後就直接把這個 Container 狀態給刪掉，就跟 docker rm 一樣的作用..

這招挺好用的，不過我在開發測試階段，要不斷的執行，老是進進出出 Container 也是不方便，因此我用的指令稍微修改一下，啟動的不是編譯器，而是啟動 shell, 結束這個 shell 之後才是刪除整個 Container.

以下來看看我的步驟，我打算從無到有，寫一段 Hello World 的 C#, 並且執行它，在畫面上印出 "Hello World!"，過程中要經過 create project (init), download dependency packages (restore), build (compile) 以及 launch (run) 幾個步驟.. 直接來看做法:

首先，先準備好 Docker 環境，取得 Microsoft 釋出的 .NET Core CLI image:

```bash
chicken@localhost:~$ sudo docker pull microsoft/dotnet
```

![](/wp-content/uploads/2015/12/img_5663dc4cc3f35.png)

完成後，用下列指令啟動 Container 內的 shell, 並且進入這個 shell:

```bash
chicken@localhost:~$ sudo docker run --name dotnet --rm -t -i microsoft/dotnet /bin/bash
root@6b021f6be610:/#
```

第一行的 prompt 提示訊息還是 Linux Host OS, 執行成功之後，第二行的 prompt 就換成 Container 內的 shell ，代表執行成功!

如果你有現成的 code 想丟進去 Container 編輯使用，可以用 -v 加掛 volume 進去，不過我這邊的範例還不需要，我就略過了。接下來就進入這套新的 CLI: dotnet. 先來看看 dotnet cli 到底支援幾種命令?

```bash
root@6b021f6be610:/# dotnet -h
```

![](/wp-content/uploads/2015/12/img_5663dc8742088.png)

就 compile , publish , run 三個，不過查了 Microsoft 的官方文件及範例，才發現原來還有好幾個指令列出來 @@, 第一個就是 dotnet init, 它可以幫你 init project, 有點類似 Visual Studio 在你 Create New Project 的時候做的事情一樣，指不過這個比較陽春。直接來試試:

```bash
root@6b021f6be610:/tmp/HelloWorld# dotnet init
```

![](/wp-content/uploads/2015/12/img_5663dcdf06f93.png)

![](/wp-content/uploads/2015/12/img_5663dd38b9c82.png)

執行過 dotnet init 後，就會在目前目錄下建立 Program.cs 及 project.json 兩個檔案。預設的內容我就直接列給大家看了。若你另外有搭配開發工具，例如 visual studio 2015 等等，其實這個步驟就可以省掉了，整個資料夾直接搬過來就好。

這次我 create project 後，先不改任何 code, 直接進行下一步。下一步是把這個 project 所有需要的相關套件，從 NuGet 下載下來，作用就跟之前的 DNU restore 一樣，只是現在改了個名字重新包裝，變成 dotnet restore。第一次執行可能會下載一堆 depency packages, 放著讓他跑完就 OK 了:

```bash
root@6b021f6be610:/tmp/HelloWorld# dotnet restore
```

![](/wp-content/uploads/2015/12/img_5663dd60820d4.png)

中間還一堆... 我就不貼了，直接跳到最後面:

![](/wp-content/uploads/2015/12/img_5663dd8af0c94.png)

沒想到一個 Hello World 就這麼多相依的套件要處理... 完成後就可以進行下一步，編譯你的程式! 我特地把 --help 顯示出來，其實看的到這個版本開始支援 compiles source to native machine code 了。看看後面的文章有沒有機會寫到這部分 :D

```bash
root@6b021f6be610:/tmp/HelloWorld# dotnet compile -h
```

![](/wp-content/uploads/2015/12/img_5663ddd168151.png)

直接開始編譯，碰上兩個警告訊息，應該是相依的 assemblies 版本衝突，這問題暫時略過，下次再回頭探討:

```bash
root@6b021f6be610:/tmp/HelloWorld# dotnet compile
```

![](/wp-content/uploads/2015/12/img_5663de26333f3.png)

編譯完成之後不執行它的話，不然要幹嘛? 接下來可以用 dotnet run 來啟動:

```bash
root@6b021f6be610:/tmp/HelloWorld# dotnet run
```

![](/wp-content/uploads/2015/12/img_5663de78d60d9.png)

走到這邊，總算大功告成! 各位的 .net code 若想 porting 到 linux 上面，就這麼簡單.. 當然這邊指的是操作程序的部分而已，我想 porting 最大的門檻應該是在那些只有 windows 版的 .net framework 才支援的 BCL (basic class library) 以及尚未支援 .net core 而無法在 linux 上執行的 3rd party 套件吧，那部分的 code 改寫才是最痛苦的.. 這種問題好像隔幾年就會來一次，當年轉移到 win32 api, 轉移到 x64, COM 轉移到 .NET, ... etc..

其實我在嘗試的過程中，也碰到不少其他困難，懊惱的是 google 也還查不到太多前輩的經驗可供參考... 我覺得主要問題應該是 beta / rc 之間的差異造成的.. 我原本在 windows 10 上面用 visual studio 2015 (asp.net 5 beta 8) 開出來的 .net core project, 直接搬過來 microsoft/dotnet 這個 container 執行時卻困難重重，包含 runtime 不支援 (預設跑到 .net frmework 4.6.1)，相關的 assemblies 找不到，或是 nuget 無法找到正確版本等等，甚至也有編譯等等都成功，執行也成功，但是 console output 卻沒有顯示出來等等怪異問題。

這些問題的排除，等我先把我的環境全面升級到 RC1 之後再來驗證一次，我相信現在開始接觸 .net core 的朋友們應該也會碰到類似問題吧，我的經驗給大家參考~
