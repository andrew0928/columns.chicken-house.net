# .NET Core 跨平台 #2, 記憶體管理大考驗 - setup environment

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼要做這樣的記憶體管理測試？
主要是先刻意製造記憶體碎片（memory fragment）的情況，再觀察 .NET Core 的 Garbage Collection 機制是否能妥善因應；同時也評估在記憶體不足 (Out Of Memory) 時，底層 .NET Core runtime 保護應用程式的能力與效能表現。

## Q: 這次記憶體測試的三個步驟是什麼？
1. 連續配置 64 MB 區塊直到 OOM，並記錄可配置的區塊數量。  
2. 釋放偶數編號的區塊，只保留奇數編號區塊，以造成記憶體碎片，再執行一次 GC。  
3. 再連續配置 72 MB 區塊直到 OOM，並記錄可配置的區塊數量。  

## Q: 測試會在那些作業環境／平台上執行？
1. Boot2Docker（Docker Toolbox 1.9.1 所附的 boot2docker.iso）  
2. Ubuntu 15.10（預設安裝 + SSH，Docker 1.9.1）  
3. Windows Server 2012 R2 Server Core（直接執行 .NET Core）  
4. Windows Server 2016 Tech Preview 4 (Nano) + windowsservercore container（Container 內執行 .NET Core）  

## Q: 進行測試的實體主機硬體規格為何？
• CPU：Intel Core i7-2600K @ 3.40 GHz  
• RAM：24 GB DDR3-1600  
• 磁碟：Intel SSD 730 (240 GB) + Seagate Enterprise Capacity 5 TB (7200 rpm)  
• OS：Microsoft Windows 10 Enterprise  

## Q: 測試用虛擬機 (VM) 的統一規格設定是什麼？
• CPU：1 處理器  
• RAM：1 GB（關閉動態記憶體）  
• SWAP：4 GB  
• HDD：32 GB VHDX（掛載於 IDE 0）  
• 解析度：1366 × 768  

## Q: 在測試程式中 `InitBuffer(byte[] buffer)` 方法的用途是什麼？
`InitBuffer` 會在每次配置完記憶體後，用亂數資料填滿整個 buffer，確保該區塊的記憶體真的被「實際使用」而非只保留為保留頁面 (reserved memory)；這是本次測試特意加入的步驟，以獲得更貼近真實使用情境的量測結果。

## Q: 對開發人員而言，面對記憶體管理能掌控的範圍有哪些？
開發者大致只能做到：
1. 適當地配置與釋放記憶體 (allocate / free)。  
2. 盡可能了解並配合 .NET 的垃圾回收 (GC) 機制。  
超出這些範圍時，通常就只能透過良好的例外處理 (exception handling) 來應對。