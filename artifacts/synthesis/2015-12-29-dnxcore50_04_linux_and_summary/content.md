&nbsp;

<hr />

<img class="alignleft" src="http://images.boomsbeat.com/data/images/full/1046/23-jpg.jpg" alt="" />

測試完 windows 家族的 .NET Core CLR 之後，接下來就是 Linux 家族了。我挑了兩個環境，一個是標準安裝的 Ubuntu 15.10 server。另一個則是採用大家常用的 Boot2Docker, 它是附在 Docker Toolbox 內的一個元件，有人預先準備好的精簡型 Linux, 預先安裝了 Docker 在裡面。

為什麼要把 Linux 的部分獨立成一篇來說明? 因為 Linux 的環境是這整個測試中，意外狀況最多的一個環境了.. 有興趣的朋友請繼續看下去..<!--more-->

<hr />

&nbsp;
<p style="padding-left: 30px;"><em>文長，分成幾篇張貼，Happy Reading! :D</em></p>
<p style="padding-left: 30px;"><em>#1. <a href="http://columns.chicken-house.net/2015/12/26/dnxcore50_01_should_i_run_dotnet_on_linux/">我真的需要在 Linux 上跑 .NET 嗎?</a></em>
<em> #2. <a href="http://columns.chicken-house.net/2015/12/27/dnxcore50_02_memfrag_test/">記憶體管理大考驗 – setup environment</a></em>
<em> #3. <a href="http://columns.chicken-house.net/2015/12/28/dnxcore50_03_windows_server_2016/">記憶體管理大考驗 – Windows Container (2016 TP)</a></em>
<em> #4. 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker</em>
<em> #5. <a href="http://columns.chicken-house.net/?p=739&amp;preview=true">多工運算效能大考驗 – 計算圓周率測試</a></em></p>


<hr />

&nbsp;
<h1></h1>
<h1>#3. Ubuntu Server 15.10 + Microsoft .NET Core CLI Container</h1>
Ubuntu Server 的部分，就是標準的安裝而已。所有選用套件，我只裝了 SSH 方便我用終端機操作，另外就是必要的 Docker Engine 而已，其他就是抓 Microsoft 準備好的 dotnet cli 這個 image 回來用.. 操作過程前幾篇都介紹過了，直接跳到測試結果:

<img class="alignnone size-full wp-image-641 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56815077450fc.png" alt="" />

第一次測試我還真的有點傻眼，有沒有搞錯? 小小一個 1GB RAM 的 Linux, 可以 allocate 到 712GB RAM ? 掛上去的 32GB HDD 都給她當作 swap 也沒這麼大啊.. 這想都不用想，一定有陷阱在裡面..

突然慶幸當年在交大除了電機的本科之外，有跑去修資工系的課，而且還挑那種特別硬的學分來修.. 包含作業系統 (Operating Systems 恐龍版), 系統程式 (System Programming 海螺版)，其他記得還有演算法跟編譯器.. 學這些基礎，這時就派上用場了。記得在講 file system 時教授提過一個關鍵字 "<a href="https://en.wikipedia.org/wiki/Sparse_file" target="_blank">SPARSE FILE</a>"，意思就是當你 allocate 一個很大的檔案時 (比如 1GB)，但是內容都還沒 initialize, 這時檔案的內容對你是完全沒有意義的，因此 OS 實際上可以把這些空間給省下來，等你真正有寫入需求時，才真正去配置硬碟空間給你用。

現在測到的情況，不就跟 sparse file 一模一樣嗎? 只不過發生的對象是 memory, 因此找了一下，才發現 linux kernel 還真的支援一種叫 SPARSEMEM 的模式，還查不大道詳細的說明，但是大致上 google 看了一下，我猜是指記憶體管理的策略有多種模式的樣子，其中一種就是 SPARSEMEM。不過我沒花時間真的去驗證是不是這個機制搞鬼，但是要避開它很簡單，我只要真的去 initialization 我取得的記憶體就可以了.. 為了確認這個問題，我改了測試的 source code, 每個平台都重新跑了一次... 改的 code 只有一小段:
<pre class="lang:c# decode:true">        static byte[] AllocateBuffer(int size)
        {
            byte[] buffer = new byte[size];
            //InitBuffer(buffer);
            return buffer;
        }
 
        static void InitBuffer(byte[] buffer)
        {
            rnd.NextBytes(buffer);
        }
</pre>
就是被我註解掉的那行 InitBuffer( ), 我原本想全部填 0x00，不過想說該不會又被我碰上啥記憶體壓縮等等最佳化的技巧，我就改填亂數了。沒想到這樣 code 寫起來還更精簡，一行就搞定了 (雖然沒有比較快)。

<del>調整過的 code 就正常多了，第一階段總共要到了 1792MB memory, 釋放之後重新配置記憶體，第三階段則要到了 1760MB. 配置後回收使用的效率高達 98.21%</del>

<del>不過 windows 都能配置到 4GB 以上的記憶體，Ubuntu 才 2GB 不到... 不知是 OS 的因素? 還是 Microsoft 在 Linux 上面實作 CLR 用了不同的做法? 還是是 Docker Container 的限制，這就不確定了，先記錄下這現象，之後再查證原因...</del>
<p id="OGCzlmO">(環境設定錯誤，測試結果請看下方修訂內容)</p>
不過，意外的部分還不只這一個。有十多是幾次，會隨機發生這種狀況:
<p id="XfYtXKf"><img class="alignnone size-full wp-image-644 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_5681597f933de.png" alt="" /></p>
第三階段時，莫名其妙就被 OS 給終結了，畫面上直接顯示 Killed, 連 OOM (Out Of Memory Exception ) 都沒有丟出來就結束了。這種情況，看來是連 Exception 都來不及丟出來，整個 CLR 就被 OS 強制終止的結果。以這點來看，Windows 版本的實作就成熟的多，我用了那麼多年都還沒碰到這種 CLR 無法搞定的狀況，再怎麼樣都還拿的到 CLR 丟給我的 Exception..

&nbsp;

------------------------------------------------------------------------

2015/12/29 01:23 修訂:

我太豬頭了，忽略掉一個關鍵的因素，就是 ubuntu 的 swapfile 設定 @@，之前都用預設值按的太高興，沒留意到不同 OS 對於虛擬記憶體預設值的不同... windows server 預設會配置 4GB c:\pagefile.sys 檔案，而 ubuntu 安裝程式預設只替我準備 1GB /swapfile ...

想到之後去求證一下，果然:
<p id="jZCNmok"><img class="alignnone size-full wp-image-661 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_568170a978f0b.png" alt="" /></p>
立馬調整成一樣的配置，一樣給 4GB swapfile，然後重新執行一次測試:
<p id="vudnSJP"><img class="alignnone size-full wp-image-662 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_568170eb4fb85.png" alt="" /></p>
讚，Ubuntu Server 版回一城，測試結果是 4864MB / 4808MB, 98.85%

&nbsp;
<h1>#4. Boot2Docker + Microsoft .NET Core CLI Container</h1>
這是準備起來最輕鬆的環境了! boot2docker 它是以光碟 .iso 的映象檔方式發布，<a href="https://github.com/boot2docker/boot2docker" target="_blank">官方的 github 網址在這裡</a>，需要的可以自行下載。使用很簡單，只要開個 VM，掛上這個 .iso 開機就可以了。不過為了讓他有足夠的空間 pull docker image, 我還是按照一樣的規格，掛了個 32GB VHD 上去給 Docker Engine 支配使用。
<p id="diKreyb"><img class="alignnone size-full wp-image-645 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56815ac57b4d8.png" alt="" /></p>
這個環境算是最快就搞定的，VM + .iso 根本不花費什麼功夫就開機成功了，加上連 docker engine 都早就預先安裝好，如上圖，光碟開機後馬上就可以開始 docker pull ... 把環境準備好，實在是很無腦 :D。原本預期結果差不多，貼個圖就可以收工了，沒想到... 也是有意外狀況發生:
<p id="OmkBaAj"><img class="alignnone size-full wp-image-646 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56815b172e548.png" alt="" /></p>
boot2docker 一樣，也會有 SPARSEMEM 的狀況，沒有 init 的記憶體實際上部會占太多空間，於是就出現這種很誇張的數據: 配置 330GB memory ... 當然改 code 配置後 init 就解決了。不過即使都是 linux, 看來也是存在差異，Ubuntu server 可以配置到 700G，boot2docker 只有 330GB ...

改用會正確 INIT 的版本後，再 run 一次:
<p id="LMznFMQ"><img class="alignnone size-full wp-image-647 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56815bf493500.png" alt="" /></p>
這次比 Ubuntu 的狀況更慘，第一階段沒跑完就掛了... 這時旁邊沒關掉的 virtual console 1 跳了一堆錯誤訊息出來:
<p id="wPsgdhC"><img class="alignnone size-full wp-image-648 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56815c3522859.png" alt="" /></p>
不是很確定實際的原因是什麼，不過很明顯的這是寫入 swap memory 時的錯誤訊息.. 很頭痛的，這狀況也是隨機的，我多跑了幾次，各種狀況都有 @@，總算抓到一次成功結束的畫面:
<p id="xfuHlRa"><img class="alignnone size-full wp-image-649 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56815d5d03a5d.png" alt="" /></p>
看來 boot2docker 的配置保守的多，我相信是很多資源沒被充分利用拉，Linux Kernel 沒有這麼不耐.. 應該是 boot2docker 設計本來就是方便測試為主，才會有這些差異。這個測試的結果，第一階段可以配置到 832 mb, 第三階段則可配置到 736 mb, 88.46%

&nbsp;
<h1>#5. 綜合比較 &amp; 結論</h1>
來看圖說故事了。我隱藏一些不必要的數據，只列出四個測試平台中，三個階段配置的記憶體總數，以及經過破碎化之後，還能重新配置的記憶體比例 (%) 表:
<p id="sEqlawz"><img class="alignnone size-full wp-image-663 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_56817158e722c.png" alt="" /></p>
 這年頭應該沒人想看一堆密密麻麻的字了吧? XD  畫成圖表看看點閱率會不會高一點:
<p id="jMhEetP"><img class="alignnone size-full wp-image-664 " src="http://columns.chicken-house.net/wp-content/uploads/2015/12/img_568171618a821.png" alt="" /></p>
灰色部分是第一階段可配置的記憶體數量，深藍色則是碎片化之後的配置量，淺藍色的曲線，則是可回收重新配置的比率 (%)。

&nbsp;

結論很有趣，我歸納成幾個結論給大家參考:
<ol>
	<li>Ubuntu Server, 是記憶體管理表現最好的平台。無論是可配置的記憶體，以及記憶體破碎後的表現，都幾乎到完美的表現了。不過 Linux 上的 CLR 在測試過程中碰到好幾次 Killed 的狀況，階段要使用仍然是以 Windows Server 2012R2 為最佳選擇。</li>
	<li><del>Windows Server 家族的表現明顯較好，都能配置到 4GB 以上。相較於 Linux 不知為何，無法配置到這麼多記憶體。</del> (後來證實為烏龍一場，請略過這條結論)</li>
	<li>Linux 的記憶體使用效率 (%) 明顯優於 Windows, 還不確定是 CLR 的實作差異所致，還是是 OS 本身的差異造成的。Linux 大都能達到 90% 以上的使用率，較不受記憶體破碎的狀況所影響。</li>
	<li>boot2docker 的表現... 就... 就拿它來測試就好了。它的特性級組態，不適合用於正式環境。</li>
</ol>
補充一下 boot2docker, 可千萬別誤會了，它是個好物，只是它的組態就是為了方便使用而設計，而不是為了高負載的前題設計的，看它包裝的方式就知道了。30mb 不到的檔案大小、採用 .iso 的方式，而不是要讓你安裝到 HDD、可以完全不依靠 HDD 就能執行 (所以自然也不會有任何 swapfile 的配置)，一切都只依靠 RAM 來運作... 因此會有這樣的測試結果，是理所當然的。這篇<a href="http://www.henning.ms/2015/05/11/running-docker-on-hyper-v/" target="_blank">教學</a>裡面有一小段，對於 boot2docker 的定位寫的蠻貼切的:
<p style="padding-left: 30px;"><em>boot2docker is a lightweight Linux distribution based on Tiny Core Linux made specifically to run Docker containers. It runs completely from RAM, weighs ~27MB and boots in ~5s (YMMV)</em></p>
另外文章內提到幾個還沒解開的懸案，我就整理在下方了。Linux 跟 Docker 我實在是新手，也許背後只是很簡單的因素造成的也說不定，有網友知道原因請笑小聲一點，你願意留言分享的話我會很感謝的 :D

&nbsp;

待確認問題:
<ol>
	<li>(?) Linux 配置為初始化的記憶體 (疑似會採用 SPARSEMEM 模式?)只占用很小的記憶體空間。</li>
	<li>(?) 記憶體不足的狀況下，Linux 版本的 CLR 可能無法全身而退，有時連 Exception 都還來不及丟出來，就被砍掉了</li>
	<li>Windows Server GC 表現不佳的問題，其實<a href="http://columns.chicken-house.net/2008/03/03/memory-management-iii-net-clr/" target="_blank">在過去的文章</a>有探討，在過去 .NET Framework 有個參數: gcServer, 可以啟動 compact collection, 能進一步解決破碎的記憶體問題。不過這次我都採用預設值，後續有機會再繼續研究看看這參數是否有影響。</li>
</ol>
&nbsp;

下一篇:
#5. <a href="http://columns.chicken-house.net/?p=739&amp;preview=true">多工運算效能大考驗 – 計算圓周率測試</a>