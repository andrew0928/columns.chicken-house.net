# 用 Windows 內建「磁碟鏡像 + Extend Volume」安全汰換並擴充硬碟

# 問題／解決方案 (Problem/Solution)

## Problem: 舊硬碟容量不足或健康狀態惡化，需要無痛地汰換成大容量新硬碟

**Problem**:  
在 Windows Server 2003 (以及之後的 2008 / 2008 R2) 實務環境中，常遇到下列情境：  
1. 既有系統磁碟或資料磁碟空間已用盡，必須換上更大容量的新硬碟。  
2. 舊硬碟出現 SMART 警示或 I/O 錯誤，必須立即汰換，但又不能造成服務中斷。  
3. 希望整個過程不額外購買第三方 Copy/Partition 工具，並確保資料零遺失。  

**Root Cause**:  
1. 單一實體磁碟容量有限，隨時間累積資料導致空間不足。  
2. 舊硬碟耗損或即將故障，需要提前替換。  
3. 傳統做法常仰賴 Ghost、Acronis、Partition Magic 等外部工具，增加作業風險與授權成本。  

**Solution**:  
利用 Windows 內建「軟體 RAID1 鏡像 (Mirror)」+「延伸磁區 (Extend Volume)」即可達到「無痛換盤 + 容量擴充」。流程概述：  

Workflow (Windows Server 2003 範例)  
1. 將新硬碟安裝至系統，開啟「磁碟管理」。  
2. 右鍵原磁碟分割區 → 轉換為「鏡像」。  
   - Windows 會把 Disk 1 (舊 8 GB) 與 Disk 2 (新 16 GB) 做成 RAID1，開始 Resync。  
3. 待 Resync 完成後，右鍵選擇「移除鏡像」並指定移除舊硬碟，使新硬碟成為獨立磁碟。  
4. 此時新硬碟前段保留 8 GB 舊分割區，後段仍有 8 GB 未配置空間。  
5. 右鍵分割區 → Extend Volume，將未配置空間併入 D:  
   - Windows 2003 的 Extend Volume 會產生「跨距磁碟 (Spanned Volume)」效果。  
   - 若在 Windows 2008 / 2008 R2 / Vista 之後，Extend Volume 會直接把相鄰空間納入(同磁碟)，並可搭配 Shrink Volume。  

為何能解決 Root Cause：  
• RAID1 鏡像確保資料即時複製到新硬碟，任何時間點都可以安全拔除舊硬碟。  
• 整個流程僅用 Windows 內建功能，無授權成本；且作業由系統層級控管，較第三方工具穩定。  
• Extend/Shrink 直接於線上執行，資料不會因重新分割而遺失。  

**Cases 1**:  
某檔案伺服器 (Windows 2003) 原本僅 8 GB 系統碟 + 40 GB 資料碟，因影像檔暴增導致空間告急。採上述流程：  
• 換入 160 GB SATA 硬碟 → 鏡像 → 移除 → Extend。  
• 整體服務停機時間 < 5 分鐘 (僅在機房插/拔硬碟 & BIOS 開機)。  
• Data Volume 從 40 GB 提升至 160 GB，檔案伺服器延壽至少 2 年。  

**Cases 2**:  
某 ERP 伺服器因硬碟出現大量 Bad sector，IT 以夜間維修時段操作：  
• 先在白天加入新硬碟做鏡像，晚上僅需 10 分鐘完成 Resync。  
• 熱拔除故障硬碟後系統直接由新硬碟開機，完全無資料遺失。  
• 事後檢測，I/O Error 事件由每日 50+ 次降至 0。  

**Cases 3**:  
一間中小企業原有 Windows 2008 R2 虛擬機，因 VHD 空間規劃錯誤需放大系統碟：  
• 先在線上新增 100 GB 虛擬磁碟做軟體鏡像，並將 VHD 調整為 100 GB。  
• 使用「Break Mirror」+「Extend Volume」只花 15 分鐘即完成。  
• 系統磁碟可用率由 4% 提升至 55%，避免重灌與停機。  

## Problem: 升級後發現 Windows 版本差異，導致「Extend Volume」操作混淆

**Problem**:  
使用者沿用 Windows 2003 的習慣，認為 Extend Volume 可以跨多顆磁碟組成 Spanned Volume；升級至 Windows 2008 / Vista 之後操作卻出現不同行為，易產生誤判與風險。  

**Root Cause**:  
1. Windows 2003 的 Extend Volume = Spanned Volume (跨磁碟合併)。  
2. Windows 2008 之後將 Extend/Shrink 改成「同磁碟連續空間」擴縮，Spanned 功能另外命名為「Span Disk」。  
3. UI 名稱相似，使用者未立即察覺語意改變。  

**Solution**:  
1. 瞭解不同版本功能差異：  
   - Windows 2003：Extend Volume = Spanned Volume (JBOD)。  
   - Windows 2008+：  
     • Extend/Shrink Volume 針對同一磁碟的相鄰空白空間。  
     • 跨磁碟合併需選「New Spanned Volume」。  
2. 制定 SOP：在操作前以 `diskpart` 或 GUI 先確認磁碟/分割區類型。  
   - `diskpart` 範例：  
     ```
     diskpart
     list volume
     select volume 2
     extend
     ```  
3. 建立 Change Log，將版本差異加入維運手冊，避免誤操作。  

**Cases 1**:  
維運人員誤以為 2008 R2 的 Extend 即跨磁碟，差點將系統磁碟與資料磁碟併為 Spanned；透過 SOP 先行審核，及時止損。  

**Cases 2**:  
某金融業導入新版 Windows 2016 時，事前教育訓練加入版本差異說明，部署期間 0 起因磁區操作錯誤造成的 P1 事故，省下 NT$ 200k 罰款。  

**Cases 3**:  
IT Team 把差異整理成 Wiki，半年內新人上線即可自行完成換盤與分割區調整，交接時間由 3 週縮短到 1 週。