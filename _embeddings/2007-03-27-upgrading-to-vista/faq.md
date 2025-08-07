# 升級 Vista ...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者決定把家中的 Windows Server 2003 x64 換成 Vista？
原本的機器長期只用了不到 5% 的負載，做為純伺服器實在太浪費；作者希望同時當成桌機使用，加上 Vista Ultimate 有優惠價且內建 Media Center 功能，因此決定升級。

## Q: 升級後這台電腦必須同時執行哪些工作？
1. Network service：RRAS、IIS、Media Service、SQL Express、DNS、DHCP、SMTP  
2. File Server：Windows 內建 RAID-1 與 Volume Shadow Copy 來保護檔案  
3. MCE：看電視、錄影、節目表等  
4. Batch Job：每週備份、影片轉檔等  
5. 一般桌機用途：上網、玩遊戲

## Q: 為什麼「Network service」(1) 與 MCE (3) 無法安裝在同一套作業系統裡？
Media Center 版本與伺服器元件（例如 RRAS）在同一作業系統中會互相衝突，兩者幾乎沒有機會同時存在於同一 OS 環境，因此被視為互斥。

## Q: 作者最後如何解決兩者互斥的問題？
作者採取折衷方案：把 (1) 的 Network service 全部搬到 Virtual PC 的 guest OS，其他 (2) (3) (4) (5) 則留在主機的 Vista Ultimate 上。

## Q: Virtual PC guest OS 的硬體資源配置為何？效能如何？
最初僅分配 256 MB RAM（Virtual PC 不支援 SMP，只能用單核心），之後調整為 512 MB。作者詢問多位使用者後，大家都感覺不到明顯變慢，證實此配置足以應付原本的服務。

## Q: Host OS 為何選擇 Vista Ultimate？
Vista Ultimate 同時附帶 Media Center、完整桌面功能與伺服器元件授權，且購買時有優惠價，能滿足作者同時「伺服器＋桌機」的需求。

## Q: 作者下一步打算如何部署 32/64 位元版本的 Vista？
盒裝 Vista 內含 32 與 64 位元版本；正式換裝前，作者計畫先在 Virtual PC 中試裝、評估，再決定最終在主機安裝哪一個版本。