(DISKe7af87).aspx/
  - /post/2007/03/28/Vista-e5889de9ab94e9a997---(DISKe7af87).aspx/
  - /post/Vista-e5889de9ab94e9a997---(DISKe7af87).aspx/
  - /columns/2007/03/28/Vista-e5889de9ab94e9a997---(DISKe7af87).aspx/
  - /columns/Vista-e5889de9ab94e9a997---(DISKe7af87).aspx/
  - /blogs/chicken/archive/2007/03/28/2312.aspx/
wordpress_postid: 174
---

Vista 試了兩天, 果然是有隱藏很多驚喜在裡頭. Microsoft 真是家不簡單的公司... 小地方我就不寫了, 我只寫對我比較特別的部份:

**<span style="color:red">[Volume Shadow Copy]</span>**

因為我是把原本 file server 的工作都移到 desktop 上, 因此 vista 終於把 vss 納入, 真是福音一件啊 [:D], 原本我的 server 放照片的那區, 有雙重保護 ( RAID-1 + Volume Shadow Copy ), 換到 XP 時心裡很不安, 保護都沒有了. RAID 可以用主機版上面的取代, 不過可以預防不小心被吳小皮 or 老婆大人砍掉照片的 VSS 就沒有了. 昨天發現 Vista 有提供 VSS 真是感動啊... ( Microsoft 你什麼時後才要把 RAID-1 加進來...? 用主機板內建的 RAID 很可怕啊... )

**<span style="color:red">[Windows Complete PC]</span>**

另一個驚喜, 是老早就知道的, 就是 vista 開始內建 disk image 的工具 ( windows complete pc, ultima 版限定, 像 ghost 那樣的東西 ), 這沒什麼特別的, 不過試用一下的發現才發現, 做出來的檔案格式, 就是 VHD ( virtual hard disk ).

頓時覺的, Microsoft 真是間可怕的公司, 難怪他老是立於不敗之地. VHD 是 Microsoft 在 virtual machine 上面推廣的 virtuah hard disk 格式. Virtual PC / Virtual Server 都是以這個格式為 vm 的 disk. 一年多前才公開了 vhd 的 spec, 廣邀各方拿去使用, Virtual Server 2005 R2 SP1 也將會提供 VHD mount 的工具. 這樣佈局下來, ghost 早已不是對手了, 我還沒試過, 不過未來 vista pc 要移到 virtual machine 內應該就更簡單了, 只要做好 disk image, 再用 vm 掛起來, 搞定收工. 這麼讚的事一定要找時間來試一試.

**<span style="color:red">[Microsoft iSCSI Initiator]</span>**

另一個驚喜, 是 vista 竟然已經內建 Microsoft iSCSI initiator... 這個倒沒什麼特別的, Microsoft 老早就 free download 了. 不過我覺的它背後的意義, 是不是代表 client 已經做好 iSCSI client 的準備, 未來 windows server 就會內建 iSCSI target ? 會的話, 格式就會直接用 .vhd ? Virtual PC / Virtual Server 就有進一步的機會直接從 iSCSI target mount disk 來 boot vm ? 哇哈哈, 之前我找半天才湊起來的 solution, 看來以後有望內建了 [Y]

Microsoft 真是個不簡單的公司, 它總是很能利用 software 要 reuse 才有價值的理念, 打贏過去的每一場仗. 從當年的 office, 到 netscape, 到現在的 visualization solution, 還有 .net technology 都是... Microsoft 要跟 netscape 對打, 不是做出更好的 IE 內建而以. 它既然花了心力去打造 IE 這瀏覽器, Microsoft 一定會有 SDK, 讓到處都可以用的到 IE. 從 HTML Help, 檔案總管, windows 桌面, 到每一個小軟體都可以開網頁 (像 msn messenger 裡玩 game 就是), 還有一堆 Microsoft 的管理工具都看的到 IE 的影子, 除非你不用 Microsoft 的軟體了, 不然就算你用 FireFox, 你還是甩不掉 IE...

其實這樣的例子很多, Microsoft 每一場重要的戰爭都是這樣贏的吧, 不知道 vista 裡還有什麼驚奇, 我再來研究看看... [:D]