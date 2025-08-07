# MSDN Magazine 閱讀心得: Stream Pipeline  

# 問題／解決方案 (Problem/Solution)

## Problem: 單執行緒串流鏈結無法善用多核心

**Problem**:  
在 .NET 中若要同時對資料做「壓縮 (GZipStream) + 加密 (CryptoStream)」，最直覺的寫法是把兩個 Stream 直接串起來，再用單一 Thread 讀寫資料：

```
[INPUT] → GZipStream → CryptoStream → [OUTPUT]
```

然而這會導致：
1. 壓縮與加密兩個 CPU-bound 工作完全在同一條執行緒上順序執行。  
2. 即便機器有 2 顆或 4 顆核心，也只能吃到 1 顆核心的效能。  

**Root Cause**:  
.NET Stream 預設是同步 (blocking) 寫入；串接多個 Stream 時，資料必須在「同一條呼叫鏈」上一路往下寫。只要最外層呼叫端是在單一 Thread，所有底層 Stream 便被限制在同一 Thread，導致無法平行運算。

**Solution**:  
改採「Pipeline」模型，將每一道 Stream 工作配置在不同 Thread 上，以 BlockingStream 做為 Stage 之間的緩衝區；Stephen Toub 於 MSDN Magazine 提出的範型如下：

```
[INPUT]
      ┌──(Thread 1)──┐
      │  GZipStream  │
      └──────────────┘
            │
        BlockingStream
            │
      ┌──(Thread 2)──┐
      │ CryptoStream │
      └──────────────┘
[OUTPUT]
```

關鍵做法  
1. BlockingStream 同時實作 Stream 介面 + 具備 Blocking Queue 行為，確保「生產者(壓縮) / 消費者(加密)」在記憶體壓力可控的情況下平行運作。  
2. 兩個 Thread 可同時佔用不同 CPU 核心；壓縮完成一塊就立即交由加密執行，形成類似工廠生產線 (Pipeline) 的流動。  
3. 程式碼僅需把原本串接的兩個 Stream 中間插入 BlockingStream，再用 Thread 啟動各自的 Stream 寫入即可；其餘 API 介面保持不變。

```csharp
var outputFs = new FileStream("out.dat", FileMode.Create);
var blocking = new BlockingStream(capacity: 64 * 1024);   // 64 KB buffer

// Stage 1 – Thread 1
new Thread(() =>
{
    using var gz = new GZipStream(blocking, CompressionLevel.Optimal, leaveOpen:true);
    CopyLargeInputTo(gz);        // 將輸入資料寫進 gz (→ blocking)
    blocking.CompleteWriting();  // 通知下游結束
}).Start();

// Stage 2 – Thread 2 (本執行緒)
using var crypto = new CryptoStream(outputFs, CreateEncryptor(), CryptoStreamMode.Write);
blocking.CopyTo(crypto);         // 從 blocking 讀資料→加密→寫檔
crypto.FlushFinalBlock();
```

**Cases 1**:  
• 硬體：雙核心 CPU  
• 測試檔案：500 MB 未壓縮純文字  
• 傳統單執行緒版本：完成時間 100 秒  
• Pipeline 版本：完成時間 80 秒 (≈ 20 % 效能提升)  
原因：壓縮耗時較長，加密較短，Stage 不對稱仍可帶來加速，但上限受最慢 Stage 牽制。

---

## Problem: 單工人「多工」造成換手成本高、又無法保持順序

**Problem**:  
某些工作流程 (如「裝信封→貼郵票→投遞」) 必須保持項目順序，且每個步驟需要不同工具/資源。若讓同一個 Worker 在 ThreadPool 中同時負責所有步驟，會因為頻繁切換工具 (context switch) 而浪費時間。

**Root Cause**:  
ThreadPool 做的是「任務切段 → 多人分攤」，假設每個任務相互獨立。但「裝信封」與「貼郵票」屬同一封信之不同階段，需要先後順序，又會因工具切換產生 Overhead。ThreadPool 難以在「必須保序」及「各階段耗時不均」兩條件下高效運作。

**Solution**:  
把流程切割成多個固定 Stage，採用 Pipeline：  
1. 每位工人 (Thread) 專注於單一動作 (Stage)，避免工具切換浪費。  
2. 透過同步佇列 (BlockingQueue / BlockingStream) 傳遞中間產物，天然保序。  
3. Stage 數 = Thread 數，固定且可預估，不會因 ThreadPool 動態增減而增加 Thread 產生/銷毀成本。  

Pseudo-workflow：

```
Thread A  ─►  Thread B  ─►  Thread C
 折信封        貼郵票         投遞
```

**Cases 1**: 郵件處理線  
• 單人全手續：每封 10 秒 (折 6 秒 + 貼 4 秒)  
• Pipeline 雙人：第一人折 6 秒/封、第二人貼 4 秒/封，除首尾空檔外平均 ≈ 6 秒/封 → 約 1.6× 效率提升。  

---

## Problem: 需要保序處理，但傳統 ThreadPool「人海戰術」難以保證正確輸出順序

**Problem**:  
影像處理、影音轉碼或任何「輸入必須依序輸出」的長序列資料，若直接把 N 個片段分派給 ThreadPool Worker，再將結果寫回串流，易出現順序錯亂或需要昂貴的重新排序 Buffer。

**Root Cause**:  
ThreadPool 睡醒順序 & 執行時間不可預期，除非額外排序邏輯，否則無法保證「先處理的片段」一定「先輸出」。為避免資料亂序，開發者常被迫回到單執行緒模式。

**Solution**:  
• 將整體工作拆成連續的 Pipeline Stage，而不是拆成多個獨立 Task。  
• 每個 Stage 內部可再用 ThreadPool 平行化，但 Stage-to-Stage 之間序列化 (即使 Buffer 到 BlockingStream)，仍能天然維持順序。  
• 若 Stage 分配得宜，可同時兼得平行度與資料輸出順序正確性。

**Cases 1**: 直播影像 → H.264 壓縮 → 加密 → 推流  
採三段式 Pipeline 減少乱序重排 Buffer，端到端延遲由 2.0 s 降到 1.4 s，CPU 使用率均衡分佈於三核。  

---