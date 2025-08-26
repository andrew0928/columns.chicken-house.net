![IMG_3972](/images/2010-07-09-run-pc-2010-july-combining-file-and-database-transaction-processing/IMG_3972_1.jpg)

再次感謝編輯大人 :D，Transactional NTFS #2 也刊出來了!

這篇是延續[上一篇](/post/2010/05/05/RUNPC-2010-05.aspx)，進一步的介紹 TxF 如何與 TransactionScope 互動，讓你可以結合檔案系統及資料庫的異動，變成單一交易的技巧。

由於TxF還沒有正式在.NET Framework裡支援，所以這篇最後也介紹了 AlphaFS，可以簡化應用時的障礙。AlphaFS 是一套想要取代 System.IO.* 的類別庫，它支援了許多 NTFS 的進階功能 (像是 VSS、HardLink 等) 的功能，而 TxF 也在範圍內，透過它就不用再像 [上一篇](/post/2010/05/05/RUNPC-2010-05.aspx) 一樣，辛苦的用 P/Invoke 了。

這篇提到的範例程式可以在[這裡](/wp-content/be-files/RunPC-201007.zip)下載。有任何意見也歡迎在這裡留話給我 :D