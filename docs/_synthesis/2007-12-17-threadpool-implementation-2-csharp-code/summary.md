---
layout: synthesis
title: "ThreadPool 實作 #2. 程式碼 (C#)"
synthesis_type: summary
source_post: /2007/12/17/threadpool-implementation-2-csharp-code/
redirect_from:
  - /2007/12/17/threadpool-implementation-2-csharp-code/summary/
postid: 2007-12-17-threadpool-implementation-2-csharp-code
---

# ThreadPool 實作 #2. 程式碼 (C#)

## 摘要提示
- 目標能力: 可設定執行緒數、優先權、Idle Timeout、佇列安全範圍並具動態擴縮與回收。
- API 介面: 提供 QueueUserWorkItem、EndPool、CancelPool、Dispose 等簡潔用法。
- 使用範例: 以 SimpleThreadPool 建立固定上限並批次排入 25 個工作示範。
- 核心機制: 每個 worker thread 以無窮迴圈從佇列取出工作執行。
- 同步策略: 以 ManualResetEvent 結合 WaitOne/Set 實作喚醒與 Idle Timeout。
- 動態擴充: 佇列堆積且執行緒未達上限時自動建立新 worker。
- 資源回收: Idle Timeout 或停止旗標觸發 worker 結束並自列表移除。
- 終止流程: EndPool 等待清空佇列，CancelPool 中止佇列未執行項目。
- 競爭控制: 多個執行緒爭奪同一工作時交由作業系統排程決定。
- 錯誤處理: 工作執行例外以 try/catch 包覆，細節待後續補強。

## 全文重點
本文在前一篇的偽碼基礎上，實作一個具備基本彈性與控制力的 C# 簡易 Thread Pool。作者先界定目標：可由使用者設定 worker thread 上限、優先權、Idle Timeout 及 job queue 的安全範圍；在佇列壅塞時能動態增加 worker；在空閒超時時能回收 worker；提供簡易同步機制以等待全部工作完成；並把工作競爭交由作業系統排程決定。接著給出 SimpleThreadPool 的介面草稿與理想使用方式，說明如何以 QueueUserWorkItem 排入工作，並在結尾以 EndPool 等待收攤或以 CancelPool 放棄未執行的佇列工作。

實作的關鍵在 DoWorkerThread：每個 worker 啟動後進入無窮迴圈，先嘗試從佇列取出工作執行，佇列清空或收到取消指令即跳出內層迴圈；之後透過 WaitHandle.WaitOne(timeout) 進入睡眠，若被 Set 喚醒代表有新工作，則繼續取件；若逾時醒來，表示長時間無新工作，則結束該 worker 並自集合移除。此處同時支援 End/Cancel 的旗標控制，保證在停止或取消時優雅退出。

在排入工作時，QueueUserWorkItem 會建立 WorkItem 並 enqueue；若發現佇列已有積壓而 worker 數尚未達上限，則動態建立新 worker 以加速消化；最後以 ManualResetEvent.Set() 喚醒可能在 WaitOne 中阻塞的 worker。作者選用 ManualResetEvent 作為同步原語，配合超時機制達成喚醒與回收；至於多 worker 爭搶工作則交由 OS 調度，不在 Pool 端強行指定。文末點出例外處理尚簡略，以及為何選擇 ManualResetEvent 的更深入討論將留待下一篇。

整體設計強調：以簡單明確的 API 操作工作佇列；以事件喚醒與逾時回收控制 worker 生命週期；在負載上升時自動擴充，在閒置時自動收斂；提供等待收攤或立即取消的二種終止策略；將工作爭奪交給系統層級排程，避免過度自訂競爭邏輯。這些構件組合出一個精簡但可用的 Thread Pool 骨架，適合作為理解 .NET ThreadPool 原理與自行延伸的基礎。

## 段落重點
### 目標與能力定義
作者列出 Thread Pool 必備能力：可由使用者設定 worker 上限、優先權、Idle Timeout 與佇列安全範圍；當佇列超過安全範圍要能自動增加 worker；worker 若長時間閒置需被回收；提供等待全部工作完成的同步機制；在多 worker 爭搶同一工作時，決策交由 OS 排程。這些目標奠定了設計的伸縮性與可控性：前者對應彈性調參與動態擴縮，後者確保資源不被閒置浪費。此外，設計中明確區分「正常收攤」與「取消未執行工作」兩種關店策略，以對應不同場景需求（確保全部任務完成 vs. 優先快速結束）。

### API 與類別輪廓
SimpleThreadPool 的介面包括建構子（設定 thread 數和優先權）、兩種 QueueUserWorkItem（可帶 state）、EndPool/CancelPool/EndPool(bool) 終止控制，以及 Dispose 對應 EndPool(false)。這些方法提供了基本但足夠的操作面：排程工作、等待完成或快速取消、釋放資源。作者強調程式碼其實不長，並將完整內容集中在 DoWorkerThread 與 QueueUserWorkItem 的核心流程，其餘為細節封裝（如 WorkItem 結構、worker 集合管理等）。

### 使用情境與收攤策略
示例建立一個 BelowNormal 優先權、最多 2 個 worker 的池，循環排入 25 個工作並隨機 Sleep，最後呼叫 EndPool 等待所有工作完成。作者以服務櫃台比喻：工作入佇列排隊，工作人員逐一處理；EndPool 會阻塞直到清空佇列，CancelPool 則僅讓已在處理的收尾，放棄尚未開始的工作。此對比凸顯不同終止策略對任務完整性和關閉時間的取捨，亦反映在內部旗標控制上。

### DoWorkerThread 的生命週期
每個 worker 進入外層無窮迴圈：內層迴圈中，只要佇列有任務即嘗試以鎖取出並執行，例外以 try/catch 包住（細節待補）；若接獲取消旗標則跳出。內層結束後，若停止或取消旗標被設置則整體結束；否則呼叫 enqueueNotify.WaitOne(maxTimeout, true) 進入阻塞等待新工作或逾時。被 Set 喚醒代表新工作可處理，continue 回內層；若逾時醒來代表空閒過久，break 離開並在尾端自 worker 集合移除，完成回收。此設計自然涵蓋了動態生死：忙時活躍，閒時回收。

### QueueUserWorkItem 與動態擴充
QueueUserWorkItem 會在停止旗標未開啟時，將 callback/state 封裝成 WorkItem 丟入佇列；若發現佇列已有積壓且目前 worker 數未達上限，立即 CreateWorkerThread 擴充處理能力；接著呼叫 enqueueNotify.Set() 喚醒所有可能在 WaitOne 的 worker，讓其競爭新工作。這裡的喚醒採用 ManualResetEvent，能一次喚醒多個等待者；而實際哪個執行緒先取得工作，由 OS 排程與鎖競爭決定，符合「不在人為層決定搶占者」的原則。作者最後指出，關於為何選擇 ManualResetEvent 的深入理由與更完整的同步策略，將留待下一篇詳述。

## 資訊整理

### 知識架構圖
1. 前置知識：
- C#/.NET 基礎語法與類別使用
- 多執行緒基本概念（Thread、工作分派、競態條件）
- 同步原語（lock、Monitor、WaitHandle、ManualResetEvent）
- 佇列與集合（Queue、List）的基本操作與執行緒安全
- 例外處理與 IDisposable 模式

2. 核心概念：
- Thread Pool 基本結構：工作佇列（job queue）+ 工作者執行緒（worker threads）
- 動態伸縮：根據佇列壓力啟動新執行緒、Idle Timeout 回收閒置執行緒
- 同步與喚醒：使用 ManualResetEvent 與 WaitHandle.WaitOne/Set 做阻塞與喚醒
- 關閉策略：EndPool（等工作清空）與 CancelPool（取消尚未執行的工作）
- 調度責任分工：由 OS 決定搶到工作之執行緒，ThreadPool 不介入搶占策略

3. 技術依賴：
- System.Threading.Thread（建立/管理 worker thread）
- ThreadPriority（設定優先權）
- WaitHandle.WaitOne(timeout) + ManualResetEvent.Set/Reset（阻塞/喚醒與超時）
- Queue<WorkItem>（FIFO 工作佇列）
- lock 關鍵區塊（對佇列與共享狀態之保護）
- IDisposable（釋放 ThreadPool 資源，封裝 EndPool 流程）

4. 應用場景：
- 後台批次工作處理（檔案處理、資料轉換）
- 伺服器端請求分派與節流
- GUI 應用程式的背景排程避免主緒塞住
- 自訂執行緒策略（優先權、最大數量、超時）無法直接用 .NET 內建 ThreadPool 時
- 教學/研究用自製簡化 ThreadPool 原理

### 學習路徑建議
1. 入門者路徑：
- 了解 Thread 與 ThreadPriority 的基本用法
- 練習 Queue 與 lock，確保對共享資源的基本同步
- 認識 WaitHandle、ManualResetEvent 的 WaitOne/Set 與 timeout
- 寫一個最小可行版本：單一 worker 從 queue 取 WorkItem 執行

2. 進階者路徑：
- 加入多個 worker thread 與安全的佇列存取（lock 範圍、判斷條件）
- 實作 Idle Timeout：WaitOne 帶 timeout、超時即結束 worker
- 動態擴張：當 queue 超過安全範圍/有壓力時創建新 worker（上限內）
- 關閉策略：EndPool 等待清空與 CancelPool 中斷尚未執行的工作
- 設計可設定的參數（最大工作執行緒、優先權、timeout、queue 安全範圍）

3. 實戰路徑：
- 封裝 SimpleThreadPool 類別（IDisposable），提供 QueueUserWorkItem API
- 加入例外處理策略與監控（計數器、日誌）
- 在實際專案替換或輔助 .NET ThreadPool，驗證效能與穩定性
- 加入測試：壓力測試（大量短任務、長任務混合）、關閉流程測試、競態測試
- 針對不同場景微調參數（max threads、timeout）並量測

### 關鍵要點清單
- ThreadPool 結構設計: 以工作佇列 + 多個 worker thread 模式處理並行任務 (優先級: 高)
- 動態擴張策略: 當佇列有壓力且未達上限時動態建立新 worker thread (優先級: 高)
- Idle Timeout 回收: worker 在 WaitOne 超時即結束，避免資源閒置 (優先級: 高)
- ManualResetEvent 使用: 以 Set 喚醒所有等待中的 worker，WaitOne 支援 timeout (優先級: 高)
- 佇列操作的執行緒安全: 使用 lock 保護 Dequeue/Enqueue 與共享狀態 (優先級: 高)
- 關閉策略 EndPool: 等待佇列清空（阻塞呼叫端），再關閉 thread pool (優先級: 高)
- 取消策略 CancelPool: 中止尚未執行的工作，只讓進行中的完成即結束 (優先級: 中)
- OS 決定搶占: 不在程式中「指定」哪個 worker 執行，而交由 OS 排程 (優先級: 中)
- 例外處理: 在 WorkItem.Execute 中捕捉例外，避免崩潰並可擴充處理 (優先級: 中)
- ThreadPriority 調整: 依情境設定 worker 優先權，影響 OS 排程行為 (優先級: 低)
- 組態參數化: 最大 worker 數量、queue 安全範圍、idle timeout 可由使用者設定 (優先級: 中)
- Wait/Notify 模式: WaitOne 阻塞 + Set 喚醒的典型同步模型 (優先級: 高)
- 資源釋放與 IDisposable: 實作 Dispose 以自動呼叫 EndPool 與清理 (優先級: 中)
- 測試與監控: 壓測、計數器、日誌觀察擴縮與關閉行為 (優先級: 中)
- 效能與公平性取捨: ManualResetEvent 喚醒多工者，實際由 OS 決定執行，簡化但可能有「驚群」代價 (優先級: 低)