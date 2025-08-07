# 還是換回 XP 了...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者最後決定從 Windows Vista 換回 Windows XP？
主要因為三大問題尚無解決方案：  
1. 眾多內建工具與程式相容性差（XP PowerToys、Resource Kit Tools、Canon .CR​W codec 等無法使用）。  
2. 檔案系統權限機制怪異，搬移檔案常被拒絕但改成「複製＋刪除」卻可行。  
3. 整體操作速度偏慢，即使在 Core 2 Duo E6300＋2 GB RAM 的硬體上仍常卡頓。  
因此作者決定先回到較穩定的 XP，等待 Vista 問題被解決後再行升級。

## Q: Vista 的 Volume Shadow Copy（VSS）對作者造成了什麼困擾？
Vista 的 VSS 實作與 Windows Server 2003 不同，導致硬碟空間在不到兩週內就被快速吃掉近 100 GB，使 250 GB 的相片硬碟只剩約 150 GB，與作者理解的「copy-on-write」機制落差很大。

## Q: 作者在 Vista 上遇到哪些相容性或缺乏支援的工具問題？
‧ XP PowerToys（尤其是 Image Resizer、Raw Image Viewer）  
‧ Windows Resource Kit Tools（cdburn、dvdburn 等）  
‧ Canon 相機的 .CR​W 影像編碼器遲遲未推出  
這些常用工具在 Vista 下都無法正常運作。

## Q: Vista 的檔案系統安全機制有哪些「怪異」行為？
在 Vista 中直接「搬移」檔案常會出現沒有權限的錯誤訊息，但如果換成「複製檔案後再刪除原檔」卻又能成功，原因不明，作者懶得再追查。

## Q: 在 Core 2 Duo E6300＋2 GB RAM 的電腦上，Vista 的效能如何？
即使硬體規格不差，Vista 仍然常在操作途中出現短暫停頓，體感明顯比 XP 緩慢。

## Q: 作者原先以為 Vista MCE 的錄影功能有什麼問題？最後發現真正原因是什麼？
他以為 MCE 會自動多錄重播節目而感到困擾，後來才發現根本原因是節目表資料有誤，並非 Vista 本身的問題。

## Q: 作者在轉回 XP 的過程中遇到哪些技術障礙？
‧ Vista 建立的動態磁碟在 XP 中無法匯入。  
‧ Vista「Complete PC Backup」產生的映像檔無法還原到 XP。  
最後只好重灌一套 Vista，再手動把多顆硬碟的資料慢慢搬回去，導致停機兩三天。

## Q: 作者目前對 Vista 採取什麼策略？
將 Vista 暫時安裝在 VPC（Virtual PC）虛擬機器中，隨時觀察更新，等相關問題獲得解決後再考慮重新改用 Vista。

## Q: 作者大約使用了多久的 Vista 就決定放棄？
大約使用一到兩個月後就覺得時機未成熟而回到 XP。