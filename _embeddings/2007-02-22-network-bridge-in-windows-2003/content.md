又在沒事找事做了... 這次是搬硬碟, 外加把部份網路從 100Mbps --> GBE, 不過這次沒有要添購新配備... 

我很迷信大廠的硬體, 自己有在開發軟體最清楚, 只有大廠才有那個本錢把軟體的 bug 都抓乾淨, driver 更是明顯... driver 寫不好鳥問題一堆, 到這種年紀已經沒力氣跟那堆 driver 慢慢奮鬥了, 只要穩定可以用不要出問題就好... 

因此之前買了一批 Intel 82559 的網路卡 (不是只有 chip 是 82559, 而是整張卡都是貼 intel mark), 有 Intel PRO/100 S 跟 PRO/100 Management+, 當時一次買了十幾張, 因為 yahoo 賣家要一次賣掉... 所以當然就全家的網卡全部換成這批. 就算主機板有內建 GBE, 還是把它給關了用 Intel 82559... 換了果然有差, driver 比那堆 d-xxxx, rxxxxt 的好多了, 也從來沒碰過傳一堆大檔傳到一半, 網路會停掉的問題, 而且經過便宜的 hub, 網路傳輸速率隨便也有 8x% ... 

不過再怎樣, 100Mbps 終究抵不過 1000Mbps, 試過幾次從 server 拉 iso 到 desktop pc 燒 dvd 就受不了了, 一定得先把 iso copy 到 desktop pc 再燒, copy 得等上十分鐘, 燒完又是十來分鐘, 還要再 verify 又是十來分鐘... Orz 

忍了一陣子, 決定趁過年調整一下, 剛好 desktop pc / server 的主機版都內建 Marvell GBE 網卡, 就把它們的封印拿掉直接對連, hub 也省了, 反正只有兩台有 GBE. 改這個很簡單, BIOS 把 LAN 打開, 網路線拔過去插上去就收工了. 

麻煩的是網路設定的地方... 原本的架構是這樣, 有點小複雜, 除了基本的 NAT 之外, server 上的 RRAS 也設定了 demand-dial, 會自動連到公司的 VPN, 同時也是 VPN server, 接受我在外面撥到家裡的區域網路, 其它 DNS, DHCP, IIS, Net Share 等等的就不畫了.. 

![](/images/2007-02-22-network-bridge-in-windows-2003/58684.gif)

最初的想法是, 直接多增加一個網段, 專門放 GBE 的 node. 不過家裡也才幾台電腦, 這樣弄好像太小題大作了, 加上這麼一來設定就越來越複雜了, DHCP 要調, static routing 要改... [:'(], 後來放棄, 直接用最不用大腦的 solution ... software networking bridge! 架構如下: 

![](/images/2007-02-22-network-bridge-in-windows-2003/37191.gif)

還好 windows 2003 有內建 bridge, 正好把 LAN 的兩張網卡串起來, 邏輯上只有一張 network interface, 只是實體接的線路有兩條 (100mbps / 1000mbps), 啥軟體設定都不用改... 

試了一下效果, 不錯, 直接 copy 檔案就有 30% 的使用率... 跟以前 100mbps 的 90% 來比, 隨便也有三倍多的提升. 不過 30% 的瓶頸似乎是掉在 disk i/o 上面, 同時從不同 disk 拉檔案就可以飆到 60% .. 

之前對 Marvell 的 chip 很感冒, 公司的 virtual server 2005 就是內建這個 chip, 流量很大, 開個一兩個禮拜網路就不通了, 但是怎麼看都正常, 就是網路不通, 得把 LAN 停用再啟用才會正常, 如果剛好人不在公司就完了, 得等隔天拔 monitor 直接到主機上面去點... 後來加了張 Intel 的網卡, 這張就一點事都沒有... 家裡流量應該不會這麼大吧? 哈哈, 就加減用一下就好..