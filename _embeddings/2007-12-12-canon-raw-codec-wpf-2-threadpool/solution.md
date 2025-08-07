# Canon Raw Codec + WPF：用自訂 ThreadPool 解決批次縮圖的效能與 UI 回應問題

# 問題／解決方案 (Problem/Solution)

## Problem: 批次轉檔耗時，CPU 利用率偏低  

**Problem**:  
在開發「類似 Windows XP Resize Pictures Power Toys」的批次縮圖工具時，當同時處理 Canon .CR2（4000×3000）與一般 JPEG 檔案時，總處理時間動輒 >110 秒，而且雙核心 CPU（Core2Duo E6300）僅有 50–60 % 的使用率，無法充分發揮多核心效能。

**Root Cause**:  
1. Canon RAW Codec 的解碼演算法本身就比 JPEG 慢得多（同尺寸 RAW → JPEG 約需 60–80 秒）。  
2. Canon RAW Codec 幾乎無法併行執行；一次啟動多條執行緒反而會彼此卡住。  
3. .NET 內建 ThreadPool 為單一資源池，無法針對不同工作類型（RAW / JPEG）指定執行緒數量與優先權，導致排程次序不理想，CPU 閒置。  

**Solution**:  
1. 重新設計排程策略—「慢的 RAW 解碼」與「快的 JPEG 縮圖」分別交錯執行。  
2. 自行實作 SimpleThreadPool，特色如下：  
   • 建構時即可固定執行緒數量，避免過度建立執行緒。  
   • 可指定每一池的 ThreadPriority。  
   • 支援同時建立多個 ThreadPool；本案例建立  
     – stp2：1 條執行緒（Highest / AboveNormal），專跑 RAW 解碼  
     – stp1：4 條執行緒（BelowNormal），專跑 JPEG 縮圖  
   • 提供 StartPool / QueueWorkItem / EndPool 介面，並可簡易 wait all 完成。  

   Sample Code（節錄）  
   ```csharp
   SimpleThreadPool stp1 = new SimpleThreadPool(4, ThreadPriority.BelowNormal); // JPEG
   SimpleThreadPool stp2 = new SimpleThreadPool(1, ThreadPriority.AboveNormal); // RAW
   stp1.StartPool();   stp2.StartPool();

   foreach(var job in jpegJobs)
       stp1.QueueWorkItem(DoJpegResize, job);
   foreach(var job in rawJobs)
       stp2.QueueWorkItem(DoRawDecode, job);

   stp1.EndPool();     stp2.EndPool();
   ```

   關鍵思考：  
   • 讓「瓶頸工作」(RAW) 先行佔用一條高優先權執行緒，確保始終有 RAW 在跑；  
   • 將剩餘 CPU 時間交給多條低優先權執行緒處理 JPEG，填滿空檔，提高積分面積 ≒ 降低總耗時。  

**Cases 1**:  
條件：125 張 JPEG + 22 張 RAW （G9 ×20 + G2 ×2）  
‒ 內建 ThreadPool：CPU 先 100 % 後 50 %，總耗時 110 秒  
‒ SimpleThreadPool：CPU 80–100 % 持續、RAW/JPEG 交錯，總耗時 90 秒（≈ 18 % 改善）  

## Problem: 使用內建 ThreadPool 時，UI 執行緒被餓死，介面卡頓  

**Problem**:  
轉檔過程中雖然進度列持續更新，但預覽 ImageBox 及其它 UI 控制項經常空白或停止重繪，造成「程式當掉」錯覺。

**Root Cause**:  
.NET ThreadPool 產生的工作執行緒預設 Priority = Normal，和 UI Thread（WPF Dispatcher）同級，CPU 滿載時缺乏系統層級排程優勢，導致 UI message loop 得不到時間片。  

**Solution**:  
使用 SimpleThreadPool 時將所有背景工作執行緒 Priority 調至 BelowNormal / Lowest；同時保留 UI Thread 為 Normal 或更高。這樣即使 CPU 100 %，排程器仍優先把時間片給 UI，確保介面可即時重繪。  

**Cases 1**:  
‒ 內建 ThreadPool：ImageBox 幾乎不顯示縮圖，使用者看到長時間空白；  
‒ SimpleThreadPool：每張圖轉完即刻顯示預覽，整體操作回應度大幅提升（Subjective UX 指標，使用者不再誤判程式當機）。  

## Problem: 等待所有背景工作完成的 API 使用繁瑣  

**Problem**:  
若持續沿用 .NET ThreadPool，必須自行建立 WaitHandle、呼叫 WaitAll/WaitAny 來判斷所有轉檔是否結束，程式碼冗長且易錯。

**Root Cause**:  
內建 ThreadPool 沒有「Pool 級別」的 Start/End 控制介面，也無跨工作簡易 wait 方法。  

**Solution**:  
SimpleThreadPool 直接提供 StartPool()/EndPool()，呼叫 EndPool() 時內部 Join 所有 worker，即可阻塞直到目前隊列排空且執行緒終止，呼叫端無須管理 WaitHandle。  

**Cases 1**:  
Main Form 在按「Resize」後呼叫  
```csharp
stp1.EndPool();
stp2.EndPool();
```  
即可保證所有檔案處理完成再關閉視窗，程式碼由數十行 WaitHandle 簡化為二行。