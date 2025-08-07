# Vista 初體驗－DISK篇

## 摘要提示
- Volume Shadow Copy: Vista 將伺服器等級的 VSS 納入桌面版，使用者終於可以在本機享有快照與檔案復原的安全感。  
- Windows Complete PC: Ultimate 版內建磁碟映像備份功能，且備份檔直接採用 VHD 格式，等同免費內建「類 Ghost」工具。  
- VHD 統一戰略: 映像備份與 Virtual PC/Server 共用 VHD，讓實體─虛擬的轉移變得簡單，鞏固微軟虛擬化版圖。  
- iSCSI Initiator: Vista 出廠即內建 iSCSI 用戶端，暗示未來 Windows Server 可能內建 iSCSI Target 並支援 VHD。  
- 軟體再利用: 微軟一貫以「把寫好的程式重複用到每個角落」為核心，從 Office、IE 到虛擬化皆以此制勝。  
- 技術佈局: 透過公開規格與 SDK，微軟將自家技術變成生態系標準，競爭者即使存在也難以被完全取代。  
- 使用者觀感: 作者在短短兩天試用 Vista 就連續發現上述三大驚喜，對微軟的整體策略感到「可怕」且佩服。  

## 全文重點
作者在將檔案伺服器職責移回桌面後，嘗試了兩天 Windows Vista，意外發現許多先前僅存在於伺服器或第三方工具的功能已被正式整合。首先，Vista 桌面版終於內建 Volume Shadow Copy，解決他在 Windows XP 時期無法對重要照片進行快照保護的焦慮，也讓家庭使用者多了一道對抗誤刪的防線。其次，Ultimate 版所附的 Windows Complete PC 磁碟映像工具不僅免除額外購買 Ghost 之類軟體的負擔，更直接使用與 Virtual PC／Virtual Server 相同的 VHD 格式，意味著未來可以「備份即虛擬機」，大幅降低 P2V（Physical to Virtual）或災難復原門檻。第三項驚喜是 Vista 原生包含 Microsoft iSCSI Initiator，象徵微軟在用戶端已為網路儲存做好準備；若下一版 Windows Server 真的內建 iSCSI Target，虛擬化平台即可直接以 VHD 透過 iSCSI 開機，完成端到端的整合。作者進而回顧微軟歷年戰術：從 Office 介面整合、IE 技術全面滲透，到 .NET 與虛擬化版圖，核心都在於「技術重用」與「生態系封鎖」。透過把一次開發的元件向外全面釋放，微軟使得使用者即便改用其他瀏覽器或工具，也離不開其底層技術。這一連串發現令作者既震撼又佩服，並期待於 Vista 中挖掘更多尚未曝光的巧思。

## 段落重點
### 1. 初試 Vista 的驚喜
作者僅花兩天試用 Vista，便感受到微軟在細節中埋入的多項重大改變；因此決定聚焦分享對自己最有感的三個「磁碟／儲存」功能，而非零碎小變動。

### 2. Volume Shadow Copy：桌面級快照終於到位
過去作者仰賴 Windows Server 的 VSS 與 RAID-1 來保護照片；移至 XP 後缺乏快照機制讓他十分不安。Vista 把 VSS 下放到桌面，不僅讓誤刪檔案可即時復原，也為家庭用戶帶來伺服器等級的資料安全。作者雖仍盼官方能內建軟體 RAID-1，但 VSS 已令他「感動」。

### 3. Windows Complete PC：VHD 格式的影像備份
Ultimate 版新增的磁碟映像工具原本被視為內建 Ghost 替代品；實測後發現備份檔其實就是標準 VHD。由於微軟早在前一年公開 VHD 規格並計畫提供 Mount 工具，此舉讓從實體機轉成虛擬機（或災難復原）只需「備份→掛載→開機」即可完成，讓競爭對手難以匹敵。

### 4. Microsoft iSCSI Initiator：網路儲存整合伏筆
發現 Vista 預載 iSCSI Initiator 雖不足為奇（此前已可免費下載），但作者認為這意味微軟正鋪路：若 Server 端日後內建 iSCSI Target，且以 VHD 作為預設檔案格式，虛擬機將能直接從網路磁碟開機，過去必須東拼西湊的解決方案可望成為原生功能。

### 5. 微軟的技術重用與生態策略
作者藉此感嘆微軟「軟體要重複利用才有價值」的哲學：當年 IE 並非僅與 Netscape 正面對決，而是被深植於 HTML Help、檔案總管、桌面與各式應用程式，令使用者即使改用其他瀏覽器也難脫 IE 影響。類似手法如今在虛擬化、.NET 乃至 Vista 的新功能上再度上演。

### 6. 結語：更多祕寶待發掘
短短兩天的體驗已帶來連環驚喜，作者推測 Vista 內仍潛藏更多值得研究的整合點；未來他將持續挖掘，並對微軟「可怕」卻高效的產品佈局保持高度興趣。