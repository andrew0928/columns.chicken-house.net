---
layout: post
title: "Volume Shadow Copy Service ..."
categories:

tags: ["技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2006/12/06/volume-shadow-copy-service/
  - /columns/post/2006/12/06/Volume-Shadow-Copy-Service-.aspx/
  - /post/2006/12/06/Volume-Shadow-Copy-Service-.aspx/
  - /post/Volume-Shadow-Copy-Service-.aspx/
  - /columns/2006/12/06/Volume-Shadow-Copy-Service-.aspx/
  - /columns/Volume-Shadow-Copy-Service-.aspx/
  - /blogs/chicken/archive/2006/12/06/1991.aspx/
wordpress_postid: 202
---

windows 2003 提供的 "新" 功能... 其實也不算新了, 都已經要邁入第四年了, 不過卻是個很實用的東西..

簡單的說, vss 是建立在 file system 以下的服務, 它可以替你的 storage 做 snapshot, 跟一般的備份不一樣, 它是用 "copy on write" 的方式. 意思就是, 當我要求現在替我的硬碟做一次 snapshot, 只要這份 snapshot 不刪除, 我都隨時可以找到這時的檔案內容.

聽起來就是一般的備份嘛, 不過它的作法完全不同. snapshot 很快就可以作好, 是快到 0.x sec 這種程度, 它只是在目前的資料上做個記號, 只要檔案沒更新, 完全沒有資料需要被備份. 而已經作了 snapshot 的資料要被更新時, 它才立即做了一份 copy, 實際上的更新動作是 copy 一份出來才 update. 這就是 "copy on write" 的作法.

講那麼多幹嘛? 因為當年研究所考試台大有考 "copy on write" ... 當時年紀輕什麼都不懂, 想破頭也寫不出來, 後來考完出來翻書才恍然大悟, 只怪書翻的太晚... :~ 所以印相就特別清楚.. 哈哈

win2003 提供的 vss 其實不只如此, 它還提供了 provider 的架構, 意思是做 snapshot 的機制, 有可能換成其它軟體來處理, 或是其它硬體, 像是 Microsoft 自己的 SQL2005, Exchange2007, Data Protection 2006, 還有其它備份軟體... 等等工具都會受惠. 這些軟體可以基於 vss 再開發出更進階的功能, 像 SQL2005 也在 db 上提供了 snapshot, Exchange2007 也靠 vss 做出更完整的檔案備份及複寫功能...

不過這些對大部份自己用的電腦都沒啥用, 大家不都是現成電腦買來, windows 灌好就開始用了... 最近花了些時間研究一下, 發現還挺好用的:

1. 在 disk properties 上可以看到 shadow copy 的畫面, 你可以定期做 snapshot
2. 做好 snapshot 後, 透過網路芳鄰來看這個 share folder 就會有額外的 options
3. 按下 view 就可以把過去的備份叫出來, 也可以還原到某個時間的檔案內容

很棒的功能, 不過跟我的需求有點差距... 我希望用 snapshot 解決我碰到的一些問題:

1. 我必需要更可靠的備份作業, 我要把資料 "真正" 的 copy 出來, 而不是只留著 snapshot.
2. copy 的動作要花一些時間, 但是 copy 時有可能資料也正在被修改 or 鎖定..
3. 我需要隨時做這些動作, 而不是像 2003 內建的, 只能排排程定期做.. 最好是可以寫成批次檔 (老人家的壞習慣... Orz)

最後找到的方式, 很陽春, 不過已經足夠解決我的問題了 (H), 就順手貼出來, 邏輯上的步驟, 是:

1. 要開始備份前, 先做一次 snapshot
2. 之後備份作業從 snapshot copy 出來, 而不是從 current state copy 出來, 就不會有 lock or update 的問題
3. 動作完成後, snapshot 就可以砍了, 當然要留著也無所謂...

要做成批次檔, 一次完成的話, 則有這兩項關鍵:

1. 命令列執行建立及刪除 snapshot 的方式: 用 vssadmin.exe
2. 讓其它工具 (我用 RAR.exe) 直接讀取 snapshot 的方式, vss 是以 UNC 的路逕提供:  
   \\localhost\d$\@GMT-2006.11.28-23.00.01

其中 \\nest\Home 是一般的 UNC 路逕, 後面加的 @GMT-...... 則是做 snapshot 的 timestamp, 以我來說, 要備份這目錄只要這樣下：

RAR.exe a -r c:\backup.rar \\nest\Home\@GMT-2006.11.28-23.00.01

說穿了沒啥特別的, 只不過找到了最後兩項關鍵, 命令列指令, 跟存取 snapshot 的路逕, 解決掉了我多年來的困擾, 每次要備份檔案一下這個 lock 一下那個 lock, 不然就是得先關一堆程式才能 copy 的困擾. 不過 windows xp 的 vss 好像就沒這麼完整, 這些作法目前只有 windows 2003 能夠用, 殘念... 不知道 vista 有沒有類似的東西可以用? :D
