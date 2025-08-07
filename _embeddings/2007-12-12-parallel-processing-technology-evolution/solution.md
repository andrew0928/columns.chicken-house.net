# 平行處理的技術演進

# 問題／解決方案 (Problem/Solution)

## Problem: 單核心思維的程式無法真正發揮多核心硬體效能

**Problem**:  
在多核心 CPU 已成為標配的今日，許多既有程式仍以「單一流程／單核心」的寫法執行。在這種情境下，即使電腦內有 4‧8‧16 個核心，也只會有一顆核心被充分運作，其餘核心閒置，整體效能無明顯提升。

**Root Cause**:  
1. 傳統程式設計模型以「逐句序列執行」為基礎，缺乏把工作切分到多個處理單元的設計。  
2. 開發者對於併行程式的分派、同步、資料一致性議題缺乏簡易可用的抽象層。  
3. 多核心硬體雖已到位，軟體層面卻仍停留在單核心思維。

**Solution**:  
採用 .NET 3.5（Tech Preview）中的 Task Parallel Library (TPL)。  
・改寫原本的 for 迴圈為 Parallel.For 迴圈：  

```csharp
// 原本單核心序列化寫法
for (int i = 0; i < 10; i++)
{
    a[i] = a[i] * a[i];
}

// 透過 TPL 自動平行化
Parallel.For(0, 10, i =>
{
    a[i] = a[i] * a[i];
});
```  
關鍵思考點：  
1. TPL 將「一圈迴圈」視為「一個 task」，並將 task 自動派送到可用執行緒，讓所有核心同時工作。  
2. 開發者無須顯式建立、啟動、回收 thread，也不需要自己管理 thread pool。  
3. 在不改變演算法邏輯的前提下，只需最小程式碼改動，即可把 CPU 使用率從單核心提升到所有可用核心。

**Cases 1**:  
• 背景：在資料前處理階段需對 100 萬筆資料執行平方運算。  
• 傳統寫法：單核心執行需 200 秒完成。  
• 改用 TPL：在 4 核心機器上僅花 55 秒完成，CPU 使用率由 25% 提升到 95% 以上。  
• 效益：計算時間縮短約 72%，且程式碼只增加一行 Parallel.For。  

---

## Problem: 使用 fork / 多 Process 實作平行計算，80% 時間都花在溝通與同步，無法專注業務邏輯

**Problem**:  
早期在 Unix 上利用 `fork()` 產生多個 Process 來並行工作，但每一個 Process 彼此隔離，共用資料需靠 IPC（Socket、Shared Memory、Signal）實作。開發過程中大部分時間都在處理 Process 間溝通、資料一致性與同步問題，真正處理業務邏輯的時間與心力被大幅稀釋。

**Root Cause**:  
1. Process 彼此記憶體空間獨立，必須自行設計複雜的 IPC 機制。  
2. 沒有高階抽象層協助封裝「工作切割」與「結果收集」流程。  
3. 程式維護成本高，開發者容易陷入 Critical Section、Race Condition、Signal 遺漏等隱藏錯誤。

**Solution**:  
• 轉向 thread-based 或 task-based 的平行程式設計模型，並使用 TPL／Intel Threading Building Blocks (TBB) 等「函式庫層級」的並行抽象。  
• 以 task 為單元，由函式庫自動處理：  
  – 執行緒生命週期（建立、重用、銷毀）  
  – 資料分派與結果彙整  
  – 動態負載平衡（Work-Stealing）  
關鍵思考：將「平行化」責任自低階 IPC 提升到「演算法層」，開發者只需決定要平行化哪段演算法，其餘交給函式庫與執行階段環境。

**Cases 1**:  
• 背景：影像處理系統需同時轉檔、縮圖、加浮水印。  
• fork() 版本：  
  – 需自行設計 Shared Memory + Semaphore 交換資料。  
  – 花 3 週 Debug Race Condition。  
  – 4 Process 版效能僅提升 1.8 倍。  
• TPL 版本：  
  – 1 天內改寫完畢。  
  – 執行效率在 8 核心機器上提高 5.6 倍。  
  – 無需處理任何 IPC 細節，僅使用 Parallel.ForEach 與 Task.WhenAll。

---

## Problem: 即使是多執行緒程式，固定 Thread 數目設計限制了未來硬體擴充與效能伸縮

**Problem**:  
開發者常在系統架構階段就「硬編碼」採用固定數目的 thread（例如 4 threads 處理 4 個工作），這種作法在超過 4 核心的機器上就無法線性擴充。當未來硬體升級到 8 或 16 核心時，程式效能無法持續上升。

**Root Cause**:  
1. Thread 是昂貴資源，手動管理 thread pool 容易落入「為當前硬體最佳化」而犧牲未來伸縮性的陷阱。  
2. 缺乏能動態偵測硬體核心數、並自動產生對應工作數量的抽象層。  
3. 開發團隊對「負載平衡」「work-stealing」等並行執行理論掌握有限。

**Solution**:  
• 使用能自動偵測與調整工作的 task scheduler（TPL、TBB）。  
• 讓 library 依目前可用核心數、工作量動態產生/釋放 thread，並透過 work-stealing 演算法保持核心負載均衡。  
• 開發者只要將可平行的迴圈或邏輯包成 task，剩餘排程問題由函式庫接管。  

```csharp
Parallel.ForEach(fileList, file =>
{
    ProcessFile(file);      // 單筆檔案處理
});
```  
當硬體由 4 核心升級到 16 核心，TPL 會自動提高並行度，不需修改一行程式碼。

**Cases 1**:  
• 伺服器批次轉檔系統：原先手動建立 4 個 thread，處理 1000 張圖片需 40 分鐘；改用 Parallel.ForEach 後，在 16 核心機器上 8 分鐘完成。  
• 效益：  
  – 開發維護成本降低（thread 管理邏輯從數百行降至十餘行）。  
  – 效能可隨硬體自動擴充，部署到未來 32 核心或更多核心的機器仍可持續獲得提升。