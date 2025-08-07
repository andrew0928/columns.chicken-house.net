# Vista 初體驗 - (DISK篇)...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Vista 內建了哪些讓作者驚喜的磁碟／備份相關功能？
Vista 在桌面版上首次內建了三大與磁碟相關的功能：  
1. Volume Shadow Copy (VSS) – 提供檔案的時間點還原保護。  
2. Windows Complete PC – 內建的磁碟映像備份工具（Ultimate 版限定）。  
3. Microsoft iSCSI Initiator – 讓用戶端可直接連接 iSCSI 儲存裝置。

## Q: Volume Shadow Copy 的加入對作者有什麼意義？
作者原本在檔案伺服器上依賴 VSS 保護珍貴相片不被誤刪。切換到桌面環境後，Vista 終於把 VSS 納入，讓桌面電腦也能有相同的檔案還原保障，令作者大感安心。

## Q: 什麼是 Windows Complete PC？它產生的映像檔格式為何？
Windows Complete PC 是 Vista Ultimate 版內建的磁碟映像備份工具，功能類似 Ghost。它所產生的映像檔格式是 VHD（Virtual Hard Disk）。

## Q: 為何 Vista 的映像檔採用 VHD 格式被作者視為「可怕」且具策略意義？
因為 VHD 同時是 Virtual PC／Virtual Server 使用的虛擬硬碟格式。  
－ 使用者做完 Vista 的 Complete PC 映像後，可直接在虛擬機器中掛載並開機，遷移流程大幅簡化。  
－ Microsoft 透過統一格式，讓備份、虛擬化與未來雲端儲存解決方案相互連結，進一步鞏固生態系，也使傳統的 Ghost 類工具更難競爭。

## Q: Vista 為何會內建 Microsoft iSCSI Initiator？作者推測背後可能帶來哪些發展？
內建 iSCSI Initiator 表示 Vista 已準備好成為 iSCSI 用戶端。作者推測：  
1. 未來 Windows Server 可能內建 iSCSI Target，直接提供 .vhd 格式的網路磁碟。  
2. Virtual PC／Virtual Server 便有機會直接從該 iSCSI Target 掛載 VHD 開機，形成完整的網路虛擬化解決方案。

## Q: 作者對於 RAID-1 的內建支援有何疑問與擔憂？
作者質疑「Microsoft 什麼時候才要把 RAID-1 加進來？」目前只能依賴主機板內建 RAID，他認為這種做法在可靠性上令人擔心，期待作業系統層級的軟體 RAID-1 支援。

## Q: 作者如何總結 Microsoft 一貫制勝的策略？
作者認為 Microsoft 擅長「軟體重複利用」：  
－ 先打造核心元件（如 IE、Office、.NET、VHD）。  
－ 再廣泛把這些元件整合到各種產品與平台，讓使用者即使改用其他方案仍難以脫離 Microsoft 生態系。  
這種策略使 Microsoft 在多次市場戰役中立於不敗之地。