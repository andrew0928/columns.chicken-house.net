# .NET Core 跨平台 #4, 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在僅有 1 GB RAM 的 Ubuntu VM 內，測試程式卻顯示可以配置到 712 GB 記憶體？
這是因為 Linux Kernel 會針對「尚未初始化」的記憶體區塊採用類似 Sparse File 的機制（稱作 SPARSEMEM）。當程式向 OS 要求大量位元組陣列而尚未寫入實際內容時，核心並不真的分配實體頁面，所以看起來好像拿到了數百 GB 的 RAM。

## Q: 要如何避免因 SPARSEMEM 造成的「虛假記憶體」數字？
在配置完成後立即對整個位元組陣列做寫入（例如以亂數填滿），讓 Kernel 必須真正分配對應的實體/虛擬頁面，就可以得到正確的記憶體使用量統計。

## Q: 把記憶體陣列初始化後，Ubuntu Server 15.10 的實際測試結果為何？
在調整 Swapfile 至 4 GB 並重新執行測試後，Ubuntu Server 於第一階段成功配置 4 864 MB，碎片化後仍能重新配置 4 808 MB，回收率約 98.85%。

## Q: Boot2Docker 執行相同測試時得到的數據是什麼？
在成功完成一次測試的情況下，Boot2Docker 第一階段僅能配置 832 MB，第三階段可配置 736 MB，回收率約 88.46%；且經常因 swap 寫入錯誤而在第一階段就被 Kernel 強制終止。

## Q: 為什麼 Boot2Docker 的表現比 Ubuntu 差這麼多？
Boot2Docker 是為「快速測試」而設計的輕量級發行版：  
1. 完全從 RAM 開機、映像檔僅約 27 MB；  
2. 預設不使用實體硬碟，因此沒有預先建立 Swapfile；  
3. 系統資源配置保守，導致在高記憶體壓力下很快就觸發錯誤。  
因此不適合作為正式、高負載環境。

## Q: 測試得到的跨平台記憶體管理結論有哪些？
1. Ubuntu Server 在可配置記憶體量與碎片回收率皆為四個平台中最佳，但 Linux 版 CLR 有機會在極低記憶體下直接被 OS「Killed」，連例外都來不及丟出。  
2. Linux 平台的記憶體使用效率（碎片化後回收率）普遍高於 Windows 平台。  
3. Boot2Docker 僅適合本機快速測試，不建議用於正式環境。

## Q: 為何在 Linux 上會出現 CLR 直接被「Killed」而沒有丟出 OutOfMemoryException？
當系統記憶體與 Swap 耗盡時，Linux 的 OOM Killer 可能直接終止消耗資源最多的程序。若 CLR 被殺掉，應用程式層就無法捕捉到任何 .NET 例外，自然也看不到 OutOfMemoryException。

## Q: 文章最後列出了哪些尚待釐清的議題？
1. Linux 未初始化記憶體為何只佔用極小空間（SPARSEMEM 的實作細節）。  
2. Linux 版 CLR 在低記憶體情況下無法「全身而退」的根本原因。  
3. Windows Server 是否可透過 `gcServer` 等設定改善記憶體破碎化問題。

## Q: 如果要在生產環境部署 .NET Core，作者建議優先考慮哪個平台？
作者建議目前階段仍以 Windows Server 2012 R2 為首選，原因是 CLR 在該平台上最成熟、最少遇到被 OS 直接終止的情況；Ubuntu Server 15.10 的記憶體表現雖佳，但穩定性仍需進一步驗證。