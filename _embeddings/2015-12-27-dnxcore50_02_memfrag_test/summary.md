# .NET Core 跨平台 #2, 記憶體管理大考驗 - setup environment

## 摘要提示
- 跨平台驗證: 透過 Windows、Linux 及 Windows Container 比較 .NET Core 在不同作業系統的記憶體行為。
- 記憶體碎片: 先製造 64 MB 區塊碎片，再嘗試配置 72 MB 以觀察 GC 與 Runtime 的應變。
- 測試步驟: 連續配置→釋放偶數區塊→再次較大配置，分別記錄次數與執行時間。
- 硬體環境: 使用 i7-2600K／24 GB RAM／SSD+企業級 HDD 的桌機，配合 Hyper-V 建立統一 VM。
- 虛擬環境: 建立 Boot2Docker、Ubuntu 15.10、Windows Server 2012 R2 及 Windows Server 2016 TP4 Nano。
- Container 實驗: Windows 2016 Nano 上啟用 Windows Container 以驗證 .NET Core 行為。
- 測試程式: C# 撰寫三段式配置/釋放/再配置流程並使用隨機資料填滿 buffer。
- Out-Of-Memory 保護: 比較 Runtime 在極端情境下對應用程式的保護能力。
- GC 效能: 觀察不同平台下垃圾收集器在碎片化後的回收與再配置效率。
- Azure 後續: 本地測試完成後，將再移至 Azure 進行雲端對照與性能綜合比較。

## 全文重點
作者欲驗證 .NET Core 在 Windows、Linux 及 Windows Container 等多種環境中的記憶體管理差異。方法是先於個人 PC 以 Hyper-V 建立規格一致的虛擬機，再於其上安裝各種作業系統與 Docker Host，最後在 Container 或 OS 內執行同一支 C# 測試程式。程式流程包含三步：1) 連續配置 64 MB 區塊直到觸發 OOM，記錄總數；2) 釋放偶數區塊並強制 GC，製造碎片；3) 嘗試配置 72 MB 區塊直到再次 OOM，以觀察碎片對大區塊配置的影響。程式中特地以亂數填滿每個 buffer，避免因頁面延遲分配而影響實測。

硬體基礎為 i7-2600K、24 GB RAM、SSD 與企業級 HDD，VM 統一配置 1 vCPU、1 GB RAM、4 GB Swap、32 GB VHDX 及 1366×768 解析度，以確保測試在可控環境下進行。驗證平台包含：Boot2Docker 1.9.1、Ubuntu 15.10 + Docker 1.9.1、Windows Server 2012 R2 Core 直接跑 .NET Core，以及 Windows Server 2016 TP4 Nano 內的 Windows Server Core Container。藉此比較不同核心、不同 GC 策略與記憶體配置機制對性能的影響，並評估 Runtime 在極端耗用下是否能妥善保護應用程式。此外，作者計畫於後續將相同測試搬至 Azure，整合雲端環境的數據再行對照。

## 段落重點
### 測試的方法
作者說明選擇記憶體管理做為觀察重點，因為它與底層平台關係最深，而開發者僅能透過分配、釋放與調整 GC 行為來介入。為驗證 .NET Core 在開源後跨平台的真實表現，他將舊有記憶體碎片測試搬到新環境重跑，並設定三步測試流程：大量連續配置 64 MB、交錯釋放並 GC、再嘗試配置 72 MB。測試以同規格 VM 執行，平台涵蓋 Windows、Linux 與 Windows Container，並預告之後會在 Azure 重現以觀察雲端差異。硬體環境與 VM 參數詳列，確保結果可重製。此段同時點出測試目的：檢視 GC 是否能在碎片化後有效整理，以及 Runtime 在記憶體吃緊時對應用程式的保護能力。

### #0. 準備測試程式
此段展示 C# 測試程式的完整原始碼。程式以三組 List 儲存 byte[]，依序執行三段流程並在每段結束輸出配置總量與花費時間。特別加入 InitBuffer 方法以亂數填充每個 buffer，避免作業系統僅分配頁表而未真正佔用實體記憶體，確保測試更貼近真實耗用。程式透過 try/catch 捕捉 OutOfMemoryException 來判定極限，並在釋放階段呼叫 GC.Collect 進行強制回收。作者指出此測試為「最沒有問題」的典型 .NET 執行環境示例，藉此做為後續跨平台比較的基準。