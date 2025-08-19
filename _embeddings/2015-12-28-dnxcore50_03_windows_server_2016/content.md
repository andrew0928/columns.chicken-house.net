---
layout: post
title: ".NET Core 跨平台 #3, 記憶體管理大考驗 - Windows Container (2016 TP)"
categories:
- "系列文章: .NET Core 跨平台"
tags: [".NET",".Net Core","Docker","作業系統","專欄"]
published: true
comments: true
permalink: "/2015/12/28/dnxcore50_03_windows_server_2016/"
redirect_from:
wordpress_postid: 630
---
&nbsp;

<hr />

<img class="aligncenter" src="http://dirteam.com/sander/wp-content/uploads/sites/2/2015/11/tp4-1024x512.jpg" alt="" width="589" height="295" />這次 .NET Core 的實驗做完，我看相關的 How To 可以寫一堆了 @@，整個過程中都在挑戰過去很少做的事情，包括 Linux, .NET Core, Docker, 現在連 Windows Container 都出動了.. 不過試完之後一整個充實啊，最後能把預期的結果弄出來，幾個晚上睡不飽是值得的...

接續上篇文章，這篇就把 windows 的兩個平台測試給搞定吧! 先快速交代一下打算當作對照組的 Windows 2012 R2~

<!--more-->

<hr />

&nbsp;
<p style="padding-left: 30px;"><em>文長，分成幾篇張貼，Happy Reading! :D</em></p>
<p style="padding-left: 30px;"><em>#1. <a href="http://columns.chicken-house.net/2015/12/26/dnxcore50_01_should_i_run_dotnet_on_linux/">我真的需要在 Linux 上跑 .NET 嗎?</a></em>
<em> #2. <a href="http://columns.chicken-house.net/2015/12/27/dnxcore50_02_memfrag_test/">記憶體管理大考驗 – setup environment</a></em>
<em> #3. 記憶體管理大考驗 – Windows Container (2016 TP)</em>
<em> #4. <a href="http://columns.chicken-house.net/2015/12/29/dnxcore50_04_linux_and_summary/">記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker</a></em>
<em> #5. <a href="http://columns.chicken-house.net/?p=739&amp;preview=true">多工運算效能大考驗 – 計算圓周率測試</a></em></p>


<hr />

&nbsp;

&nbsp;
<h1>#1. Windows 2012R2 Server Core (對照組)</h1>
這一組應該不用多說了吧? 已經是很成熟的組合了，除了 .NET Core CLR 還是新的之外... 為了讓各組的組態都接近一點，2012R2 我特地選用最輕量的 Server Core, 沒有 GUI 介面可以用，所有動作都要靠下指令來完成。這個正合我意，多了 GUI 也會拖慢速度... 反正 Linux 那麼多指令都已經搞定了...

直接來看結果吧，裝完該裝的之後，主角上場。所有的測試，我都是拿 source code 直接到受測平台，就地編譯就地測試。測試步驟我一律是:
<ol>
	<li>VM 重新啟動</li>
	<li>下載相關的 package</li>
	<li>編譯</li>
	<li>連續執行兩次，以第二次的數據為準 (避免第一次啟動有額外的最佳化等等動作)</li>
</ol>
<p id="niLqAmO"><img class="alignnone size-full wp-image-633 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_568017243c37f.png" alt="" /></p>
執行的結果中規中矩，記憶體回收的效果不算特別突出。我沒有特別指定虛擬記憶體的大小，系統預設是給 4GB pagafile, 加上本身 1GB 的 RAM，看來程式能在第一階段要到 4416MB memory 是很合理的.. 經過故意讓記憶體碎片化的動作後，重新要記憶體來用，最後只能要到共 2888MB 的大小... 我就訂一個指標 (記憶體利用率 %) 吧，用 phase 1 可取得的大小當分母，phase 3 可取得的大小當分子，算出 2012R2 的結果是: 65.40%

實際上程式其他的 overhead 其實不大，跟測試結果差不多。雖然 server core 沒有 GUI，不過平常常在下指令，有些 tips 還是派得上用場的，在 dos pormpt 下輸入 taskmgr.exe 可以叫出工作管理員 XD，趁機看一下:
<p id="FaLHjkU"><img class="alignnone size-full wp-image-635 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_568018e727ab4.png" alt="" /></p>
看來執行 .NET Core 的 runtime dnx.exe 本身吃掉 4548MB, 而實際的 RAM 1G 被吃掉了 800MB，其實在意料之中，沒有太大的落差。工作管理員切換到效能頁看看:
<p id="oZKqemr"><img class="alignnone size-full wp-image-636 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_568019519b820.png" alt="" /></p>
右半突然飆高的那段，就是程式剛開始啟動的時候，看來實體記憶體一開始就用光了，剩下後面都在用虛擬記憶體，從記憶體使用率來看也是一樣的結果。

&nbsp;
<h1>#2. Windows Server 2016 Nano (Tech Preview 4)</h1>
雖然這也是 windows, 不過有很大的不同喔，這是 Microsoft 第一個支援 container 容器技術的 OS。Microsoft 跟 Docker 密切的合作，計畫在 2016 這個版本正式推出 windows container. 體驗了之後感覺好奇妙，提供了完全相容 docker 的管理工具 (也有提供 powershell 版本)，讓你可以在 windows server 裡面建立屬於 windows 的 container .. 當然，能跟 docker 共用的是架構，管理工具這些東西，然而 container 是必須依賴 host 的 kernel 啊，所以不可能用到那堆 linux 的 container image ... 這邊就只能辛苦一點，直接拿 windows server core 的 image 當起點，自己一步一步把環境建立起來 T_T

也許是還在 Preview 階段的關係，操作上回應速度有點慢，尤其是我用 interactive mode 把終端機接到 container 內更明顯... 到時等到更接近 release 的版本再來看看吧，Microsoft 的效能調教很強的，之前 windows 10 insider 體驗時有見識到了 :D...  這邊的建置過程我就先跳過了，有朋友有興趣可以在私下問我。直接貼一下測試結果:
<p id="lprJDRa"><img class="alignnone wp-image-697 size-full" src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56840f8bb211b-e1451495326913.png" alt="" width="520" height="325" /></p>
第一階段最多可以要到 4032MB 記憶體空間，第三階段則可以用到 2696MB，整體的利用率達到: 66.87%

第一次體驗 windows container, 其實還蠻奇妙的，用起來就像是個 VM，只是他限定 Guest OS 跟 Host OS 必須是同一個的感覺... 我試著去工作管理員找證據，也證明了他真的是用 container 技術在執行。如下圖，我開的是 Host OS 本身的工作管理員，可以看的到在 Container 內執行的指令。證明它們適用同一個 kernel, 而不是像 VM 依樣是完全隔離的兩套系統，可想見的，這種模式下對於資源的應用一定是更有效率，可以看的到在效能上跟原生的其實沒有太大的差別。
<p id="EiyrAVE"><img class="alignnone size-full wp-image-638 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56801dd7cd650.png" alt="" /></p>
不過，如果你只把他想成 windows 版的 docker,  那又太小看 Microsoft 了，在 Host OS 與 container 之間，Microsoft 又增加了一層隔離，讓 user 能夠對 OS kernel 有選擇性的決定要步要隔離它? 這個技術在 TP4 首次現身，它就叫做 Hyper-V Container. 簡單的說，若你需要 Kernel 層級的隔離支援，底層的 Hyper-V 會自動替你用預先做好的 image 來建立 VM，然後在把你的 container 見在這個 VM 裡面。讓你在必要時有 VM 層級的隔離與保護，同時又能享有 container 技術的優點。

這次我是沒機會體驗到這個部分，先留個筆記，下次有機會再回頭研究。有興趣的朋友可以參考這篇: <a href="http://windowsitpro.com/windows-server-2016/differences-between-windows-containers-and-hyper-v-containers-windows-server-201" target="_blank">The differences between Windows Containers and Hyper-V Containers in Windows Server 2016</a>

<img class="alignnone" src="http://windowsitpro.com/site-files/windowsitpro.com/files/uploads/2015/08/container2.jpg" alt="" width="800" height="398" />

&nbsp;

&nbsp;

#4. <a href="http://columns.chicken-house.net/2015/12/29/dnxcore50_04_linux_and_summary/">記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker</a>