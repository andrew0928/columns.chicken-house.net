![](/images/2015-12-26-dnxcore50_01_should_i_run_dotnet_on_linux/img_567e9b3cb3f8f.png)

最近這幾篇 .NET Core / Docker 相關的文章貼出來之後，最常聽到有人問我的問題就是:

"**要跑 .NET 就在 windows 上面跑就好了，要在 Linux 上跑 .NET 有甚麼意義嗎?**"

其實還蠻有意義的 XD，這兩個月每天下班花一點時間研究之後的心得，.NET Core 的確還在起步的階段 (現在才第一版 RC)，跟已經進展到 4.6 的 .NET Framework 完整成熟的生態來說真的差太遠，現階段來看還完全沒有什麼誘因值得立刻轉移到 .NET Core + Linux 上面執行。不過眼光放長遠一點，這我認為到是個蠻值得的投資。怎麼說? 以下是我的觀點，跟大家分享:

<!--more-->

{% include series-2016-dnxcore.md %}



# 投資在 .NET Core + Linux 眼前的好處:

1. 可以沿用所有的 .NET 開發資源 (.NET BCL, Visual Studio, 其他既有 C# source code 的程式碼)
1. .NET Core 可以充分利用 open source 的社群資源
1. .NET Core 可以在 windows 以外的平台執行的官方支援與保證

這些優點都是非常顯而易見的，以 (2) 來說，光是有 Bug 被找到時，有 source code 的話就會有很多魔人直接修正了。這讓我想到[當年我找到 .NET Framework 裡面的一個 SMTP 編碼的 BUG](/?p=169)，我當時很辛苦的只能用反組譯的方式來追問題，找到問題回報後，等到官方解決 & 釋出修正檔，已經是半年多以後的事了。我相信有這種經驗的人一定不只我一個... ，對於 software engineer 來說，給他再好的工具或是文件，都比不上直接看 code 來的有用，而 open source 就是最大的幫助!

再來看 (3), 換個角度想，.NET Core 支援 Linux 之後，以後 .NET 程式終於可以名正言順，有官方支持的方式，大大方方的在 Linux 上面執行了。最大的效益在於，可以跟很多其他 open source project 更緊密的配合。很多情況下，最終服務要佈署的方式，就已經決定你的開發平台了。有的狀況是特定 solution 只支援 Linux, 這時架構師為了簡化系統的維護，可能會因為這樣遷就統一整體的環境都用 Linux，另外常見的例子是非營利單位，大型佈署時其實沒甚麼選擇，也是用 0 授權成本的 Linux，這些情境在過去都是會對 .NET 造成排擠效應的族群。

另外再舉個例子，我碰過很多 open source 的套件，雖然有 windows 版本，不過由於 windows / linux 很多地方先天上就有差異，這些套件就算 porting 到 win32 用起來就是水土不服，最後這樣的組合，只有在不得不用的情況下會被端出來，正常的狀況或是新案子根本不可能挑選這樣的組合。我就曾經碰過只是個小型專案，但是最後竟然得在一台 Windows Server 上同時跑 IIS + Apache 的窘境... 這些都是造成 Windows / Linux 兩大陣營格格不入的原因，為了長遠考量，往往都只能做出 2 選 1 的決定。

融入 open source 的生態，不只有表面上的效益，除了讓你摸的到 source code 之外，更深層的意義是你的解決方案也要符合這個社群的使用習慣。舉例來說，Linux 上面可不會有 IIS，就算 Microsoft 願意把 IIS 也 open source, 我想在 Linux 的世界裡，不會有人想用 IIS 吧 XD... 所以，Microsoft 除了把 .NET Core 開源之外，架構上也得替 ASP.NET 5 做一些調整，讓他能夠在 Apache 或是 Nginx 上面跑才有意義... 所以就催生了 OWIN (參考 [darkthread: 開發筆記: OWIN](http://blog.darkthread.net/post-2013-12-01-about-owin.aspx) ) 這東西出來。OWIN 的優點我就不多說了，Google 可以找到很多。我舉個反例，有在寫 ASP.NET 的人應該都知道，Microsoft 光是要執行你的 web project  就有好幾種環境可以使用，包括: 各個版本的 IIS、IIS express、Visual Studio 內建的 Dev Web Server、還有社群版本的 [Cassini](https://cassinidev.codeplex.com/) .. 令人想哭的是，除了 IIS / IIS express 之外，其他每個環境之間的差異都不小，常常在 A 是正常，但是拿到 B 就掛掉的狀況... 到最後整個開發團隊只好退回都用最終的環境 (IIS) 來測試，直到 IIS express 出現後才有所改善..

這些改變，也讓 .NET Core 相關 solution 能在架構上可以更直接地跟其他 open source solutions 搭配，像我最近在弄得 .NET Core + NGINX + Reverse Proxy 等等混搭的做法就很容易實現，這是好處。如果是在過去，首先要用 .NET 就是得用 Windows，OS 沒有其他選擇 (先別提非官方的 Mono)。接著我得先想半天，WEB 到底要用 IIS 還是用 Apache / Nginx ?  Reverse Proxy 到底是要設在 Apache / Nginx 裡，還是在 IIS 上面安裝 [ARR](http://www.iis.net/downloads/microsoft/application-request-routing) (Application Request Routing) ?





# 投資在 .NET Core + Linux 長遠的好處:

再來看長遠一點的趨勢變化，Microsoft 這麼做的目的，我認為合理的有:

1. .NET 在 open source 社群的地位  
cloud 都是以 linux 為大宗，open source 可以讓 .NET 族群維持一定的市佔率，可以留住這些 .NET 的生態圈 (include me)。最接近的對手，大概就是 Java 了吧，.NET / C# 想要擠下 Java 的地位的話是一定要 open source 的，只是現在做還來不來的及的問題而已 XD

1. Azure  
Azure 是 Microsoft 的雲端平台，Linux 在 Cloud Solution 裡是大宗，客戶有需要 Linux, Microsoft 沒道理不提供。有人在用 Azure 的服務，Microsoft 就會有營收，即使你用的是 Linux 而不是 Windows。不過這樣長遠來看實在是很尷尬，既然你用了 Linux, 那 Microsoft 就必須有更強烈的誘因來留住客戶。直接對這個生態有大量的貢獻，在這個生態內提供比對手更好整合更緊密的服務是必要的。以這角度來看，.NET open source 就是不可或缺的第一步，而 Microsoft 已經跨出去了。



目前 .NET 仍然有很大的優勢，那就是 C# 語言的優越，跟大幅領先全世界其他開發工具的 Visual Studio。 C# 對於程式碼很講究的我來說，是我的首選。我很喜歡 [Anders](https://www.microsoft.com/about/technicalrecognition/anders-hejlsberg.aspx) 大神 (Delphi, C#, TypeScript 的創造者) 的風格.. 搭配沒有對手的 Visual Studio 之後，這組合是在是太無敵了，只可惜過去這是要錢的，不管是開發工具，或是要佈署的環境都是。很多非營利單位沒辦法大規模採用。這現象也許在 .NET Core open source 之後會有改善，不過要造成影響，恐怕還要等上幾年才會成氣候吧..

雖然這些趨勢，短期內都對我還沒有影響，公司還是照樣用 Windows Server / IIS / SQL server, 還是照樣用 C#, 用 Visual Studio 開發系統，但是身為十幾年的 Microsoft 陣營的 developer, 我是還蠻看好這樣的改變的，所以最近才認真研究起 .NET Core / Docker 這樣的組合。Microsoft 新任 CEO 果然還是比較抓得住 developer 心裡在想甚麼，過去 Bill Gates 在位時，這部分都做得不錯，中間換了 Steve Ballmer, 對 developer 的感官就差了點 (我自己的感受)，就是少了點 fu, 直到 Satya Nadella 上任，這感覺又回來了 XD


# 回到主題，了解 .NET Core 在不同平台上的表現

因為有上述這些考量，這也才是我想要深入研究 .NET Core / Docker / Linux 的動機。為的不是接下來一兩年，而是為了下個 10 年做準備...

跨平台最討厭的就是各種平台上的細節行為的差異，尤其是 OS 掌管的資源 (CPU, Memory ... etc) 更是如此。想要快速的掌握這些差異，最快的方法就是親手做一次，因此我把以前的 Code 挖了出來，打算寫兩篇探討:

1. 記憶體管理的差異 (use: memory fragment test)
1. 運算速度及效能的差異 (use: multi-thread + compute PI )

記憶體管理這個主題，這個我把之前的舊文探討的主題拿出來用。當年學生時代，在 BBS 上看到個很有意思的論點 (應該有 20 年了吧)，就是 virtual memory 的管理機制下，virtual address space 還會不會有 fragment 的問題? 當年也為了這個主題寫了三篇文章 (如下)，結果在不同的 OS，不同的架構 (x86 / x64), 甚至是不同的 GC 方式 (garbage collection) 下都有不同的行為表現。當時這結果大出我意料之外，也令我印象深刻，因此這次 .NET Core 對我而言，我是把它當作新的平台來看待，因此這測試也被我重新拿出來用了。


1.	[Memory Management - I, Fragment](/2008/02/26/memory-management-i-fragment/) ?
1.	[Memory Management II - Test Result](/2008/03/03/memory-management-ii-test-result/) ?
1.	[Memory Management III - .NET CLR](/2008/03/03/memory-management-iii-net-clr/) ?


另一個運算速度的測試，就比較單純了，我只是想知道同樣 .NET Core 的 Code, 在不同平台執行起來的效能到底有沒有差別? 大家普遍認為 Linux 省資源，跑得快，但是 .NET 在 Windows 卻又比 Linux 上來的成熟，誰勝誰負還很難講，目前也還 Google 不到太多相關資訊，我就找了段計算小數點以下50000位數圓周率的 CODE 來當作基礎，搭配我的老本行 multi-thread 來測看看。我用了同樣規格的 Hyper-V VM, 分別在 Linux + Docker, Windows 2016 + Windows Container, Windows 2012R2 (這個沒 container 可以用，只好讓他作弊直接在 host os 上跑了) 來比較。

這篇評論就當作引言，充當第一篇吧 XD，接下來兩篇就是這兩個比較了，請待下期分曉~