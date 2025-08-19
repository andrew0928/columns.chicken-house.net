---
layout: post
title: "困難重重的 x64"
categories:

tags: ["技術隨筆","有的沒的","水電工"]
published: true
comments: true
redirect_from:
  - /2008/02/26/困難重重的-x64/
  - /columns/post/2008/02/26/e59bb0e99ba3e9878de9878de79a84-x64.aspx/
  - /post/2008/02/26/e59bb0e99ba3e9878de9878de79a84-x64.aspx/
  - /post/e59bb0e99ba3e9878de9878de79a84-x64.aspx/
  - /columns/2008/02/26/e59bb0e99ba3e9878de9878de79a84-x64.aspx/
  - /columns/e59bb0e99ba3e9878de9878de79a84-x64.aspx/
  - /blogs/chicken/archive/2008/02/26/3005.aspx/
wordpress_postid: 121
---

即使是做足了功課，還是敗下陣來... Orz 

之前 Vista x64 用的都還不錯，直到加上 4GB 之後，才是惡夢的開始... 之前貼了一篇 6GB 很爽的 POST，之前插上去只偵測到4.8GB，想說小事情，一定是 BIOS Remap沒打開的關係，果然一開就是 6GB，一切正常，就貼了 POST .. 

不過隔一兩天，想開個 MCE 來看電視，怎麼沒訊號? 查了半天確定線路都正常，才想到之前剛裝好不是都 OK 嗎? MCE 還列為重點測試項目之一，driver早都打聽好了，怎麼還會這樣? 就一個一個設定 rollback 試看看... 

搞半天，問題出在想都沒想到的地方... 我的 TV 卡，在Vista x64開了Memory Remap後就會出問題了。Device Manager沒有任何異狀，但是MCE就一直說訊號微弱... 跟本沒辦法看. Memory Remap 關掉就正常了。寫Mail去圓剛跟華碩的客服反應，果然再怎樣還是要買大廠的... 

ASUS 有回，不過沒用... 

圓剛? 沒人鳥我... 

雖然切回 4.8GB 還是戡用，不過多買的 4GB 只能當 2.8GB 不到，感覺有點鳥... 加上裝了 X64 有一半以上的軟體都是 X86 ... 看起來實在有點礙眼... 其實現階段用 X64 也是有些缺點的，第一就是很多軟體及 DLL 都要分兩套， x64 + x86，很佔空間。第二，一樣的程式 x64 吃的 memory 比較多，為何? 每個 Pointer 都多兩倍空間... 多少都會有影響... 第三，幾乎用到 COM 元件的都得靠 WOW，效能有點下滑... 所以暫時還是換回 x86 版了. 

換回 x86 vista 後第一件事就是試試電視卡，在 x86 mode 下開不開 REMAP 就都正常，看來 Driver 要負一點責任，不過工作忙，暫時就不理它了，下次擇日再挑戰一次 x64. Ram 裝太多果然還是有一堆問題，新問題是我的主機板 (ASUS P5B-E Plus) 如果開了 BIOS Remap，進 Vista 後只能看到 2048MB Ram @_@，關掉反而還有 2.8GB... 搞什麼飛機... 

又是搞了半天，確定無解，網路上很多人跟我一樣... 本想就讓它 2.8GB 吧，不過又讓我發現了個評價不錯的 Ram Disk 軟體: "Gavotte Ramdisk" 

評價不外呼是免費，沒有容量限制，很穩定等等，不過它有個特異功能倒是 RAM 插太多的人要試試... 它可以把像我這樣失去的 RAM 挖回來用!! 

真的蠻神奇的，只要 Vista 起用 PAE (Physical Address Extension)，這套 RAM DISK 就能自動把 OS 不會抓來用的 RAM 當成 RAMDISK. 不過不開 BIOS Remap 就沒輒... 因此當場我的組態變成: RAM: 2GB, RamDisk: 4GB ... 

真的是 Orz，我要那麼大的 RamDisk 幹嘛? 像網路一堆人把 Page File 放到 RamDisk 上的作法又覺的有點蠢，雖然很多時後非得要 Page File 不可，不過把 RAM 不夠時某些 RAM 的資料搬到 DISK，而這 DISK 又是 RAM 模擬的，感覺就像是做了一堆白工... 算了，拔掉 2GB 吧，剩下 2GB 就當 TEMP 用，可以塞 TEMP 的就塞過去.. 

看起來 x64 還是小問題多多，沒那個人生跟他耗的話，還是過一陣子再試試吧，反正照這情勢，RAM很快就會漲到不得不換 X64 的地步了，往好的方面想，這應該會加速廠商移到 x64 的腳步吧? [H]
