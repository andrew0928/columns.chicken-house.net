# Volume Shadow Copy Service …

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Windows Server 2003 的 Volume Shadow Copy Service (VSS)？
VSS 是建置在檔案系統之下的服務，可為儲存裝置建立即時快照（snapshot）。透過「copy-on-write」機制，它能在極短時間內（0.x 秒等級）完成快照，並讓使用者在日後隨時取回建立快照當下的檔案內容。

## Q: VSS 與傳統備份有何不同？
傳統備份會把整份資料複製到備份媒體；VSS 則只在建立快照時做標記，不複製資料。當檔案稍後被修改時，系統才把原始區塊複製一份後再寫入新內容（copy-on-write）。因此建立快照既快速又省空間，且可在系統線上執行。

## Q: 什麼是「copy-on-write」？
建立快照時不立即複製任何資料，只在磁碟上做標記；當標記區塊要被改寫時，系統先把舊資料複製到快照存放區，再把新資料寫回原位置，藉此保留修改前的內容。

## Q: VSS 為何需要「Provider」架構？
Provider 允許第三方軟硬體取代預設機制來生出快照。例如 SQL Server 2005、Exchange 2007、Data Protection Manager 2006 及其他備份工具都能在 VSS 架構上提供更進階的備份與複寫功能。

## Q: 在 Windows Server 2003 上如何以命令列建立或刪除快照？
使用 vssadmin.exe：
‧ 建立快照：vssadmin create shadow /for=d:  
‧ 刪除快照：vssadmin delete shadows /for=d: /oldest

## Q: 建立快照後，要如何在批次檔裡存取它？
VSS 會以 UNC 路徑公開快照，例如  
\\localhost\d$\@GMT-2006.11.28-23.00.01  
在批次檔中可直接把這條路徑當來源，例如：  
RAR.exe a -r c:\backup.rar \\localhost\d$\@GMT-2006.11.28-23.00.01

## Q: 作者利用 VSS 解決了哪些備份痛點？
1. 透過快照避免檔案鎖定或檔案正被修改時無法複製的問題。  
2. 可把「建立快照→從快照複製→刪除快照」寫成批次檔，隨時手動執行，不必受限於系統排程。  
3. 真正把資料「複製」出去，而不只倚賴系統保留的快照。

## Q: 這種做法在 Windows XP 或更新版系統上適用嗎？
作者實測發現 Windows XP 的 VSS 功能不夠完整，無法像 Windows Server 2003 一樣使用 vssadmin 與 UNC 路徑方式；至於 Windows Vista 是否具備相同能力，文章中並未得到確定答案，仍待驗證。