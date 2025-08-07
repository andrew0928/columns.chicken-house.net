# 再度換裝 Vista ... Vista Ultimate (x64)

## 摘要提示
- Vista x64 升級: 為了突破 4 GB 記憶體限制與整合 Media Center、Tablet PC 功能，作者決定全面改用 Vista Ultimate x64。  
- 硬體更新: 新增 750 GB 硬碟與增設記憶體，提供安裝 64 位元作業系統的硬體條件。  
- Canon RAW Codec: 透過強迫程式以 x86 模式編譯並執行，成功在 x64 系統使用原不支援的 Canon RAW Codec。  
- Vista Complete PC Backup: 內建 VHD 影像備份功能取代 GHOST，可直接掛載於 Virtual PC/Server。  
- WOW64 相容機制: 說明 32/64 位元程式不可混載，並討論 32 位元程式在 x64 下的效能與記憶體優勢。  
- 開發環境更新: Visual Studio 2008 釋出後，多數在 VS2005 及 x64 上的 Debug 問題已獲解決。  
- IIS 7 研究: 以桌面版 Vista 先行體驗 IIS7，以便日後過渡到 Windows Server 2008。  
- SuperFetch 與快取: 作者欣賞 Vista 透過剩餘記憶體提升常用大型程式的啟動速度。  
- SP1 與時機成熟: Vista SP1 即將登場，加上正版授權已購買，升級意願大增。  
- 升級結論: 透過相容性技巧與硬體升級，Vista x64 已可滿足工作與多媒體需求，不必再回頭 XP。  

## 全文重點
作者先前因相容性與效能問題從 Vista 退回 XP，經過一年觀察與硬體更新後，再次嘗試安裝 Vista Ultimate x64。主要動機包含新硬碟與記憶體擴充、Media Center 與 Tablet PC 功能整合、研究 IIS7、以及 Visual Studio 2008 解決了舊版開發工具在 Vista x64 的 Debug 障礙。最棘手的 Canon RAW Codec 雖官方宣稱不支援 x64，但作者實驗發現只要將自寫轉檔工具與 Windows Live Gallery 以純 32 位元模式執行，即可透過 WOW64 讀取 32 位元 Codec 並正常顯示與轉檔 RAW 檔。Vista 內建的 Complete PC Backup 亦提供 VHD 影像備份，省去第三方 Ghost 類工具，並可直接掛載於 Virtual PC/Server 進行檢視。文章進一步解析 32/64 位元程式混用限制、32 位元應用在 x64 OS 的效能與記憶體分配優勢，指出只要完整切換為 32 位元進程即可避開 DLL 與驅動混載問題。結論為 Vista x64 在硬體與軟體生態漸趨成熟後已可日常使用，加上 SP1 臨近與正版授權在手，此次升級應該不會再降級回 XP。  

## 段落重點
### 升級契機與背景
作者回顧先前升級 Vista 後又退回 XP 的歷程，距離上次嘗試已近一年。隨著硬碟空間不足及記憶體需求增加，加上身邊使用者對 Vista 的正面經驗，決定再度安裝 Vista Ultimate x64 以解決硬體瓶頸並嘗試新功能。  

### 主要換裝原因總覽
列出十三項升級理由：1) 750 GB 新硬碟避免破壞舊系統；2) 64 位元才能有效利用 4 GB 以上 RAM；3) XP MCE 沒有 x64 版本；4) Canon RAW Codec 已有解決方案；5) 想研究 IIS7；6) 家人使用經驗良好；7) Vista 內建多媒體與 DVD 編輯；8) 小幅改良累積成顯著升級；9) Tablet PC 功能與數位板整合；10) SuperFetch 提升應用程式啟動速度；11) VS2008 修復開發問題；12) SP1 將出爐；13) 已購買正版不想閒置。  

### Vista Complete PC Backup 與 VHD 整合
發現 Vista 內建的 Complete PC Backup 能將整顆硬碟做成 VHD 影像，無須第三方工具即可備份與還原。該影像格式與 Virtual PC/Server 相容，可直接掛載檢視或還原，對開發與測試環境十分便利。  

### Canon RAW Codec 在 x64 的相容性難題
網路上一致認定 Canon RAW Codec 不支援 Vista x64，作者在虛擬機嘗試安裝後證實無法運作；自製轉檔工具與 Explorer、Windows Live Gallery 均無法顯示 .CR2 縮圖，成為升級最大障礙。  

### WOW64 機制與 32/64 混載限制
闡述 WOW64 的核心原則：同一 Process 內不得混用 32 與 64 位元程式碼。硬體與軟體驅動、各式 DLL、ActiveX、Codec 等若未提供 64 位元版本即會失效；然而完整以 32 位元執行即可避開問題，並獲得記憶體空間擴大與管理速度提升的附加效益。  

### 解決 Canon Codec 與升級後心得
將自寫工具重新編譯為 x86，並使用 Windows Live Gallery 32 位元版本，成功載入 Canon RAW Codec 顯示與轉檔 RAW 檔，證明相容性問題可解。提醒 Gallery 常駐機制可能造成版本混用，需在開機後先啟動正確版本。解決關鍵障礙後，作者認為 Vista x64 已可穩定工作，多項內建功能帶來實質便利，升級決策終於塵埃落定。