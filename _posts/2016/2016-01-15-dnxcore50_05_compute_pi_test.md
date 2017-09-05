---
layout: post
title: ".NET Core 跨平台 #5, 多工運算效能大考驗 – 計算圓周率測試"
categories:
- "系列文章: .NET Core 跨平台"
tags: [".Net Core","C#","Docker","專欄"]
published: true
comments: true
permalink: "/2016/01/15/dnxcore50_05_compute_pi_test/"
redirect_from:
wordpress_postid: 739
---
&nbsp;

<img src="http://26.media.tumblr.com/tumblr_lstbslOSFm1qd5bcwo1_500.gif" alt="external image tumblr_lstbslOSFm1qd5bcwo1_500.gif" />

前面幾篇，研究完記憶體管理的部分之後，接著就是來看看運算的效能了。這部分的測試方式，我想了很久，最後決定拿出老本行: 平行處理的部分來當作 .NET core 跨平台第二回合的主題!

如果單純只是要將各種平台的 .NET Core 比出個高下，那感覺有點像是拿 benchmark 在賽豬公而已，這樣的話找現成的 C# benchmark 應該比較快。因此，我把測試的目的定義清楚，我想藉由這些測試的進行，一方面了解不同平台的差異，我也想透過測試更熟悉這些環境，還有試圖從測試的結果挖出背後運作原理的不同。所以，上一個記憶體管理的主題，已經達到目的了，不這樣測試我還真的不曉得 Linux 預設會壓縮(?) 為初始化的記憶體... 算是值回票價。

<!--more-->

<hr />
<p style="padding-left: 30px;"><em>文長，分成幾篇張貼，Happy Reading! :D</em></p>
<p style="padding-left: 30px;"><em>#1. <a href="http://columns.chicken-house.net/2015/12/26/dnxcore50_01_should_i_run_dotnet_on_linux/">我真的需要在 Linux 上跑 .NET 嗎?</a></em>
<em> #2. <a href="http://columns.chicken-house.net/2015/12/27/dnxcore50_02_memfrag_test/">記憶體管理大考驗 – setup environment</a></em>
<em> #3. <a href="http://columns.chicken-house.net/2015/12/28/dnxcore50_03_windows_server_2016/">記憶體管理大考驗 – Windows Container (2016 TP)</a></em>
<em> #4. <a href="http://columns.chicken-house.net/2015/12/29/dnxcore50_04_linux_and_summary/">記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker</a></em>
<em> #5. 多工運算效能大考驗 – 計算圓周率測試</em></p>
<p style="padding-left: 30px;"><em>#source code (github): <a href="https://github.com/andrew0928/blog-netcore-cross-platform-test" target="_blank">https://github.com/andrew0928/blog-netcore-cross-platform-test</a></em></p>


<hr />

&nbsp;

第二回合既然要探討 CPU 運算效能，那就來考驗看看 .NET Core 在各種平台下的 CPU Bound 運算的優劣吧。首先我找了段 cpu bound 的代表: 計算指定位數的圓周率程式碼 (計算 10000 位數)。這計算會耗費大量的 CPU 資源，但是不會耗用大量 I/O 及 Memory。透過 <a href="https://msdn.microsoft.com/en-us/library/system.threading.tasks.task(v=vs.110).aspx">System.Threading.Tasks</a> 同時計算 1 / 2 / 4 / 8 / 16 / 32 / 64 次 10000 位的圓周率，並紀錄執行所花費的時間。同樣的測試，則會在不同的平台，在不同的硬體組態下，用 1 core / 2 core / 4 core / 8 core 的硬體配備，分別執行一次。
<p id="oHRhkpl"><img class="alignnone size-full wp-image-742 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_56967d2029838.png" alt="" /></p>
先用一張簡單的時序圖，解釋一下這次測試的指標。上圖的 X 軸代表時間，由左至右。丟了 5 個 task 給 .NET Core, 讓他自己去排程處理。排程有很多種策略，這邊我就不另外控制，完全按照 Task 預設的模式來排程。

看過我過去幾年文章的網友，大概都知道我花了很多時間在 "多執行緒" 這個主題上，不同的執行策略其實落差很大。我介紹過的包括 multi-threading, thread pool, 生產者/消費者模式, 生產線模式等等。這次我跳過這些控制機制，直接用 .NET 內建的 Task (可以把它想像成更好用的 thread pool)，他會視你的資源使用狀況，將你的 Task(s) 分配給可用的 thread 來執行。

為了能具體評估這次測試的結果，我採用了這幾個指標:

<strong>Total Execute Time</strong>:
如上圖，整個測試開始執行到全部結束的時間。這指標可以評估整體的執行效能，時間越短越好。

<strong>Average Execute Time</strong>:
每個 Task 個別完成時間的平均值。這個指標，可以用來評估個別 Task 的執行效率，時間越短代表個別 Task 的效能越好。

<strong>Efficiency Rate (%)</strong>:
平行處理帶來的效益提升率 (%)。計算方式是拿 1 cpu 只執行 1 task 的 total execute time 為基準 ( total execute time - base ), 沒有平行處理加持的狀態下，要把所有的 task 跑完，要花的時間是 {total execute time - base} x {total task count}，而實際的時間則是 {total execute time}, 因此 Efficiency Rate = {total execute time - base} x {total task count} / {total execute time} x 100%, 可用來評估該環境多工帶來的整體效率提升率。

指標要怎麼看? 我會從幾個角度來看實驗結果:

如果我想看單線 CODE 執行的速度，比如我想評估 JIT 的效能，或是 -native 參數編譯的差異，那我會看 Total Execute Time 來比較 (越小越好)。如果想排除掉多工排程的影響，那可以看 1 core 的硬體環境的測試結果。

如果我想看多工執行針對多 CPU 最佳化的效果，那我會看 Efficiency Rate。他代表透過平行處理機制，整體效能能提升的百分比(%)。這個指標也是我想做這次測試的原因，我想知道不同 OS 的執行緒管理機制是否有所不同? 因為上一次記憶體管理的測試，讓我有意料之外的結果，即使都是 .NET Core CLR, 記憶體管理的機制竟然會因為底層的 OS 有這麼大的差別... 多工 / 執行緒的管理，一樣是很依賴 OS 的機制，會不會也出現很大的落差?

測試方式先介紹到這裡，接下來就看看實際測試結果了。這次一樣用 VM 來控制執行環境的硬體資源，不同平台通通都用一樣的 PC，開一樣規格的 VM 來比較。測試平台一樣是:
<ol>
	<li>Windows 2012 R2 (server core)</li>
	<li>Windows 2016 TP4 nano server + windows container</li>
	<li>Ubuntu 15.10 + docker</li>
	<li>Boot2Docker 1.9 + docker</li>
	<li>(對照組) 我的 PC，用原生的環境 windows 10 enterprise</li>
</ol>
<ol>
	<li><strong>Boot2Docker</strong>, 使用 Docker Toolbox 提供的 boot2docker.iso, 版本 1.9.1</li>
	<li><strong>Ubuntu 15.10</strong>, 預設安裝 + SSH, 安裝 docker 1.9.1</li>
	<li><strong>Windows 2012R2 Server Core</strong> (直接在上面跑 .NET Core)</li>
	<li><strong>Windows 2016 Tech Preview 4 (Nano)</strong>, 在上面建立 windowsservercore container, 在裡面安裝 .NET Core 的 CoreCLR runtime</li>
	<li><strong>(對照組) 我的 PC, </strong>直接採用 windows 10 enterprise, 沒有經過虛擬化的機制, 執行 x64 版本的 coreclr</li>
</ol>
我自己 PC 的規格 (跟上次一樣):
<ul>
	<li><strong>CPU</strong>: Intel Core i7-2600K ( @ 3.40GHz )</li>
	<li><strong>RAM</strong>: 24GB (DDR3-1600, 4 + 4 + 8 + 8)</li>
	<li><strong>HDD</strong>: Intel SSD 730 (240GB) + Seagate Enterprise Capacity 5TB (ST5000NM0024), 7200 rpm 企業級硬碟</li>
	<li><strong>OS</strong>: Microsoft Windows 10 Enterprise</li>
</ul>
VM 的規格跟上次一樣 (如下)， 不過核心數則會分別用 1 / 2 / 4 / 8 core 分別執行一次測試:
<ul>
	<li><strong>CPU</strong>: 1 / 2 / 4 / 8 core</li>
	<li><strong>RAM</strong>: 1024 MB (dynamic memory was disabled)</li>
	<li><strong>SWAP</strong>: 4096 MB</li>
	<li><strong>HDD</strong>: 32GB (VHDX, attached on IDE controller 0, HDD #1)</li>
	<li><strong>DISPLAY</strong>: 1366 x 768</li>
</ul>
每個平台測試完，會產出一份這樣的數據結果出來 (時間的單位是 ms):
<p id="WhqSVjO"><img class="alignnone size-full wp-image-744 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_56968d3f83288.png" alt="" /></p>
測試的程式碼如下，我把這次跟上次的 <a href="https://github.com/andrew0928/blog-netcore-cross-platform-test" target="_blank">source code</a> 都放上 github 了，有興趣的朋友可以自己拉一份下來玩玩.. 主程式如下:
<pre class="lang:c# decode:true" title="計算圓周率 測試程式 (CalcPI)" data-url="https://raw.githubusercontent.com/andrew0928/blog-netcore-cross-platform-test/master/CalcPI/Program.cs">// please find the source code at:
// https://github.com/andrew0928/blog-netcore-cross-platform-test/blob/master/CalcPI/Program.cs</pre>
&nbsp;

OK，該說明的都說明完了，來看測試結果:

&nbsp;

&nbsp;
<h1>#1 Windows Server 2012R2 (server core)</h1>
<p id="cmZUGGC"><img class="alignnone size-full wp-image-747 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_56968ead5dbc6.png" alt="" /></p>
密密麻麻的數字，應該沒啥人想看吧 XD，我直接貼圖表好了。不過圖表好幾個，有些沒代表性的我用 2012R2 當代表貼一次就好。第一張圖是看看平行處理在多核心的狀況下有沒有發揮效果?

&nbsp;
<p id="nPUdsdm"><img class="alignnone size-full wp-image-757 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697bf0537be2.png" alt="" /></p>
這圖表的 Y 軸代表執行時間，X 軸分為四區，分別代表 1 2 4 8 個核心的執行狀況。而每區的每種顏色，則代表執行 1 2 4 8 次計算。我先掠過 16 32 64 次的數據，這樣關係看得比較清楚。可以看到 1 core 的狀況下，計算次數加倍，時間就會加倍，但是隨著 core 數量的增加，total execute time 在 core 數還沒用盡時的測試結果，幾乎是一樣的..。

&nbsp;
<p id="XyTOYQS"><img class="alignnone size-full wp-image-760 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c15611c7e.png" alt="" /></p>
這圖代表 average execute time 的變化關係。跟 total execute time 的關係類似，隨著 core 數量的增加，average execute time 的增加幅度就趨緩了，代表 thread pool 其實是有效的在控制 threads 總數，沒有讓過多的 threads 在系統內執行，避免沒有提升整體效能，還造成額外的負擔的狀況。
<p id="qXMpkom"><img class="alignnone size-full wp-image-758 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c01884e41.png" alt="" /></p>
接著看看 efficiency-rate, 一樣如預期，隨著 core 數量的增加，效率提升大體上也跟 core 數量呈正比。我的設備是 i7-2600k, 是個 4core / 8 thread 架構的 CPU，可以看到在 4 core 時的效率提升還成比例，但是增加到 8 core 時的進步就沒有那麼明顯了，可見 cpu core 跟 cpu thread 的作用還是有差別的。intel 的 <a href="http://www.intel.com/content/www/us/en/architecture-and-technology/hyper-threading/hyper-threading-technology.html" target="_blank">hyper-threading 技術</a>，有興趣的就看官方說明吧.. 這邊跳過。

每個平台的這幾張圖表，模式都類似，我就貼數據就好，圖表略過。最後綜合比較時再拿出來交叉比對..

&nbsp;

&nbsp;
<h1>#2 Windows Server 2016 Tech Preview 4 (nano server)</h1>
<p id="iVNSJze"><img class="alignnone size-full wp-image-748 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_56968eee469c0.png" alt="" /></p>
&nbsp;

&nbsp;
<h1>#3 Ubuntu Server 15.10 + Docker (image: microsoft/dotnet)</h1>
<p id="bhkLZQJ"><img class="alignnone size-full wp-image-753 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_56969885d1767.png" alt="" /></p>
&nbsp;

&nbsp;
<h1>#4 Boot2Docker 1.9 + Docker (image: microsoft/dotnet)</h1>
<p id="JNKbdDF"><img class="alignnone size-full wp-image-750 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_56968f4a5c0ba.png" alt="" /></p>
&nbsp;

&nbsp;
<h1>#5 (對照組, 純參考用) 我的PC, Windows 10 Enterprise</h1>
<p id="MGSUyNl"><img class="alignnone size-full wp-image-751 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_56968fad5bee3.png" alt="" /></p>
附帶一提，單純當作對照組。因為是實體機器，我沒辦法關掉其中幾個 core XD, 因此這組數據只有 8 core 這區 (嚴格的來說是 4 core 8 thread .. XD)

&nbsp;

&nbsp;
<h1>綜合比較 - Total Execute Time</h1>
我本來還期望不同平台，除了看到效能差距之外，會看到有不同的 patterns 出現，看來這邊沒有意外發生 XD，不過效能的差距還是有的，這次我把四個平台數據擺在一起看。
<p id="bvKjqEa"><img class="alignnone size-full wp-image-762 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c39e4b005.png" alt="" /></p>
數據繁多，我就挑關鍵的部分來看了。我針對 64 次計算的數據，把每個平台跟核心的組合列在一起看:
<p id="hXmxmCQ"><img class="alignnone size-full wp-image-763 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c3e869f9c.png" alt="" /></p>
有點意思的結果，跟之前 memory test 的結果有點出入，.NET core 在 windows 平台上的最佳化果然還是有優勢的，除了 1 core 環境下，最輕量的 boot2docker 速度最快之外，其他環境下都是 windows 家族領先。

原本我最不看好的 windows server 2016 tech preview 4, 想說他還在 TP 而已，應該都還沒最佳化... 結果沒想到 1 / 2 core 時效能還排最後，但是到 4 / 8 core 時，效能馬上竄到第一名... 看來 Microsoft 不知在甚麼細節上的最佳化下了功夫，表現亮眼，正式版值得期待~ 想要跑得快的話，挑 windows server 2016 是比較好的選擇!

&nbsp;

&nbsp;
<h1>綜合比較 - Average Execute Time</h1>
<p id="XLNjfbo"><img class="alignnone size-full wp-image-764 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c57aa738a.png" alt="" /></p>
<p id="LYuwtbE"><img class="alignnone size-full wp-image-765 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c596917c0.png" alt="" /></p>
接著是 average execute time 的比較，一樣，圖表我只留下 64 次計算的結果。結果跟 total execute time 類似，運算速度還是 windows server 家族維持領先。很意外的是，Ubuntu 在這部分的表現敬陪末座，原本想說 linux 極度輕量化的環境，跑起來應該會比 windows server 輕快許多，結果不是如此。一方面 .NET core 在自家的 windows server 最佳化做的最好之外，我想 2016 nano server 極度的輕量化之後，在這邊也看到效果了，不但拚過 ubuntu 預設安裝，連 boot2docker 這種 boot cd 只有 20mb 的 linux 都拚贏了，真是不簡單 (Y)

&nbsp;

&nbsp;
<h1>綜合比較 - Efficiency Rate</h1>
<p id="IXbzUsL"><img class="alignnone size-full wp-image-766 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c755b02c8.png" alt="" /></p>
<p id="XJWAcwe"><img class="alignnone size-full wp-image-767 " src="http://columns.chicken-house.net/wp-content/uploads/2016/01/img_5697c76a62687.png" alt="" /></p>
最後一張，其實也沒什麼好比的了 XD，一樣是 windows 2016 獲勝。531% 的效率改善，遙遙領先第二名的 windows 2012 470% ! 不過，我想這個除了最佳化做的好之外，跟 windows 2016 在 1 core 環境下的表現最糟，一增一減下來，進步的比例就放大了，應該也有關係吧!

&nbsp;

&nbsp;
<h1>結論</h1>
既然評比的結果一面倒，那也沒啥好講了。如果你很講究運算的效能，又很愛用 C# 開發程式的話，那挑選 windows server 家族準沒錯。由實驗結果看來，.NET core 還是在 windows 平台上表現較佳。我想這是 microsoft 對 windows binary 掌握程度遠高於 linux 的關係吧? 畢竟這測試完全取決於 JIT / native compiler 的效果。而對 threads 的管理，我相信也同樣的 windows 會戰有更大的優勢，這些都可以從 execute time, 還有 efficiency rate 的數據得到證明

不過雖說如此，平台的決定不是只看效能一件事，其他管理跟維護的成本也別忽略了，畢竟表現最好的 2016 跟 ubuntu 的差距，也只有 10.4% 而已，說大不大，一班情況下的差異也不容易感覺得出來.. 其他工具、系統相容性、以及系統維護成本才是主要考量的地方。

&nbsp;

兩類我想做的測試，都完成了。下一篇就最後一篇了，我會整理一下這次研究過程中，其他瑣碎的心得~ 其實這次這樣研究下來很累人的，要不是測試要控制環境，我一定是選擇在 Azure 上面部屬這些環境，省事多了... 下一篇產出的速度，看看 1/16 開票的結果吧! 要是心情好的話，這週就會生出下一篇了 XD