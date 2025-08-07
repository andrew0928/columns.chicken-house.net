# 困難重重的 x64

# 問題／解決方案 (Problem/Solution)

## Problem: Vista x64 + 6 GB RAM 時，MCE 無法收看電視

**Problem**  
情境：在 Vista x64 上將實體記憶體由 2 GB 擴充到 6 GB，BIOS 開啟 Memory Remap 後雖然可正常偵測到 6 GB，但只要執行 Media Center (MCE) 便出現「訊號微弱」而無法觀看電視，Device Manager 卻顯示 TV 卡一切正常。  

**Root Cause**  
TV  卡的 64 bit 驅動程式與「BIOS Memory Remap + Vista x64」組合存在相容性缺陷。  
Memory Remap 開啟後，PCI/PCI-e 裝置的 MMIO 位址被重新配置到 >4 GB 區段；TV 卡的舊版驅動無法在此位址範圍正確讀寫，導致影音資料無法傳遞給 MCE。  

**Solution**  
1. 關閉 BIOS Memory Remap，讓所有裝置被映射到 <4 GB 區段。  
2. 退回可運作之 4.8 GB 組態；短期內改用 Vista x86。  

關鍵思考：  
• 先確保裝置驅動於 <4 GB 位址可正常運作，再行評估升級驅動或等候廠商出新版。  
• 捨棄部分可用記憶體，換取核心功能 (收視) 的穩定性。  

**Cases 1**  
‒ 重新開機、關閉 Memory Remap 後，MCE 立即可正常收看；但 OS 僅剩 4.8 GB 可用。  
‒ 與華碩、圓剛客服聯繫無即時解決方案，確認為裝置驅動問題。  



## Problem: Vista x86 下 BIOS 開啟 Memory Remap 只認得 2 GB，關閉則剩 2.8 GB

**Problem**  
情境：改裝 Vista x86 後測試記憶體，開啟 Memory Remap 僅能看到 2 GB；關閉 Remap 雖回到 2.8 GB，仍損失近一半實體記憶體。  

**Root Cause**  
1. 32 bit Windows 核心僅能直接定址 4 GB 空間；  
2. 當 Memory Remap 開啟時，部分實體 RAM 被移到 >4 GB 位址；Vista x86 因未啟用 PAE 無法存取該區段；  
3. 關閉 Remap 雖保留較多 RAM，但高位址仍被 MMIO/BIOS 影射區吃掉。  

**Solution**  
1. 於 Vista x86 啟用 PAE 開關 (`bcdedit /set pae ForceEnable`)；  
2. 安裝免費 RamDisk 軟體「Gavotte Ramdisk」，它能把 OS 無法定址、位於 4 GB 以上的 RAM 挖出並建立為 RAMDisk；  
3. 關閉 BIOS Memory Remap，確保多餘 RAM 仍掛在 4 GB 內（但被遮蔽），由 Gavotte 自動掛載；  
4. 將 TEMP 目錄或高速暫存資料放到 RAMDisk。  

關鍵思考：  
• 借助 PAE + 第三方驅動，把「OS 無法直接使用」的位址空間轉為 I/O 快取或暫存區，以提高整體 I/O 效率而不浪費記憶體。  

**Cases 1**  
‒ 組態：可用系統 RAM 2 GB + RamDisk 4 GB。  
‒ 將瀏覽器 Cache、解壓縮暫存檔移至 RamDisk，磁碟 I/O 明顯加速，系統體感變快。  

**Cases 2**  
‒ 為避免「RAM→PageFile→RAMDisk」來回搬運造成浪費，停用 PageFile 或僅保留最小值，改將大量臨時檔導向 RamDisk。  



## Problem: 現階段 x64 軟體生態不成熟，維運成本升高

**Problem**  
情境：即便硬體已支援 64 bit，實務開發與日常使用仍大量依賴 x86 軟體與元件，導致在 Vista x64 上需同時安裝 x86 與 x64 兩套 DLL/COM 元件，造成空間、維護與效能負擔。  

**Root Cause**  
1. 多數商用／開源軟體尚未完全移植到 x64；  
2. 指標寬度由 32 → 64 bit，導致 x64 應用記憶體佔用成長；  
3. 需透過 WOW64 執行 x86 COM，系統呼叫額外轉譯，效能下降。  

**Solution**  
短期策略：  
• 生產環境先行回退至穩定的 Vista x86；等待驅動、第三方函式庫與 COM 元件全面支援 64 bit 再升級。  

中期準備：  
• 持續追蹤廠商 x64 版發布，規劃漸進式替換；  
• 實驗機維持 x64 以測試新驅動，提早發現相容性問題。  

關鍵思考：  
用「可控風險 + 最小維運成本」為優先，分階段導入新架構。  

**Cases 1**  
‒ 回到 x86 後，系統維護流程簡化：備份腳本、安裝套件與自動化工具均沿用舊版，省下 1/3 的部署時間。  



