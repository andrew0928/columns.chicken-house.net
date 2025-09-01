gt3b-JPEG-e9809fe5baa6e58aa0e5808d-e8a9b2e68f9b-Core2-Quad-e4ba86e5989b.aspx/
  - /post/2008/04/10/Canon-CR2---gt3b-JPEG-e9809fe5baa6e58aa0e5808d-e8a9b2e68f9b-Core2-Quad-e4ba86e5989b.aspx/
  - /post/Canon-CR2---gt3b-JPEG-e9809fe5baa6e58aa0e5808d-e8a9b2e68f9b-Core2-Quad-e4ba86e5989b.aspx/
  - /columns/2008/04/10/Canon-CR2---gt3b-JPEG-e9809fe5baa6e58aa0e5808d-e8a9b2e68f9b-Core2-Quad-e4ba86e5989b.aspx/
  - /columns/Canon-CR2---gt3b-JPEG-e9809fe5baa6e58aa0e5808d-e8a9b2e68f9b-Core2-Quad-e4ba86e5989b.aspx/
  - /blogs/chicken/archive/2008/04/10/3159.aspx/
wordpress_postid: 110
---

看來是換四核心CPU的時機到了 [H]

之前弄了半天的歸檔程式，效能都卡在 .CR2 -> .JPG 這段。雖然祭出了 ThreadPool，也想盡辦法把獨立的工作湊在一起，盡量提升 CPU 的利用率，不過得到的效果有限，因為最後都是剩下 .CR2 的檔案轉不完啊，其它拿來填空檔的工作早就做完了，實在不成比例... 整體效能還是卡在最慢的 Canon Codec 身上...

這次無意間想到，單一 process 內，Canon Codec 有過多不能重複進入的問題 (不能同時利用到兩顆CPU)，那麼拆成兩個獨立的 process 是否就解決了?

想一想還蠻可行的，通常為了安全，都只需要做到 process 內的 LOCK 就夠了，不需要做到全域的 LOCK，除非要 LOCK 的資源是跨 process 會用的到的才需要這樣做... 在真正改程式下去之前，當然要先驗證一下...

用之前的 LIB 簡單寫了個執行檔，就單純的把 .CR2 轉 .JPG 而以。寫好後同時 RUN 兩份，讚! CPU 利用率飆到 80% (雖然離理想的 100% 還有段距離) ... 不過在我的 E6300 CPU，同時跑兩份，執行速度倒沒有下降，差不多..

確定這方式有效之後，花了點時間改我的歸檔程式，把轉檔部份抽成 .exe 然後由歸檔程式來啟動，一樣維持同時有兩個 .CR2 轉檔程序進行。耶! 情況不錯，轉一個檔案一樣要 70 秒，但是 70 秒過後可以轉完兩個檔案... 平均起來等於速度加倍了...

之前一直不想用這個方法，因為一來 IPC (inter-process communication) 是件麻煩事，不想去碰，二來啟動另一個 process，參數的傳遞也是個麻煩事，大概就只能靠檔案或是 arguments ... 或多或少都要處理到一些 parsing 的問題... 三來執行的回傳值也是一樣，總之都碰到 IPC 的問題就不想去碰他了

不過這次評估了一下，這些動作麻煩歸麻煩，至少不是花運算資源的動作，跟一張照片轉 70 秒，一次動則上百張的量比起來，怎麼算都划算...

真糟糕，這樣下去是不是代表該換 Q9450 了? 咳咳...