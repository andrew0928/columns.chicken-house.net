# 處理大型資料的技巧 – Async / Await

## 摘要提示
- Azure Blob: 以 ASP.NET 從 Azure Storage Blob 讀取 100 MB 影片時遭遇效能腰斬問題。  
- I/O 重疊: 問題源於單執行緒 Read/Process/Write 只能序列化執行，導致網路、磁碟、CPU 交互等待。  
- 範例程式碼: 透過 `Task.Delay` 模擬 Read(200 ms) / Process(300 ms) / Write(500 ms)，展示同步迴圈需 10 秒。  
- Async/Await: 將 Write 改成 `async Task`，並在下一輪迴圈前 `await` 前一次 Write，立即回傳以擠壓空檔。  
- 效能提升: 重構後總時間縮短為 5 秒，效能約提升 2 倍。  
- 資源利用: I/O 與 CPU 可同時忙碌，解決「三個員工、但一次只動一人」的低效率。  
- 頻寬分析: 在 80 Mbps 區段改善幅度最佳；頻寬越低，Write 時間變長，提速效果遞減。  
- 多執行緒回顧: 生產線模式、Producer/Consumer 亦可解，同理皆在重疊工作時段。  
- 適用情境: 若程式大量等待外部 I/O 而硬體利用率低，Async/Await 較 Thread 簡潔且代價小。  
- 結論建議: 大規模並行選 Thread；需求是「片段非同步＋精準等待」則用 Async/Await 最合拍。  

## 全文重點
作者在 ASP.NET 上傳／下載約 100 MB 的影片檔到 Azure Blob 時，發現經過授權與轉碼之後，實際輸送率僅剩原 Blob 直接下載的一半。經監控 CPU、磁碟與網路皆未飽和，判斷瓶頸是程式流程：同步迴圈先讀取，再處理，最後寫出，三個階段彼此阻塞，造成任何一項工作時其餘資源皆閒置。  
為了證明此點，作者寫出 Read(200 ms)／Process(300 ms)／Write(500 ms) 的示範程式，十回合需 10 秒。接著回顧過去利用 Thread、Pipeline、Producer/Consumer 等多執行緒技巧重疊工作的方法，但決定改用 .NET 4.5 之後提供的 Async/Await。  
重構方式很單純：把 Write 改為非同步，主流程儲存上一輪的 Task，並於下一輪開始前 `await`；如此 Read+Process 可與前一筆 Write 並行，縮短總時間到約 5 秒，僅首筆 Read+Process 與尾筆 Write 不重疊，因此多出約 0.66 秒誤差。  
實際案例中 Read 受限 VM↔Storage 200 Mbps，Process 受限 CPU，Write 取決於 Client↔VM 頻寬。依不同頻寬測試可知，當 Write 時間落在 Read+Process 時間附近（約 80 Mbps）提速最明顯，隨頻寬降低而 Write 變長，改善幅度趨於 0。  
結論指出：凡是「程式經常等待 I/O」而硬體整體利用率又低時，重疊等待即可獲得效果；若要大規模平行運算仍以 Thread 為宜，單純消除等待則 Async/Await 兼具可讀性與維護性。  

## 段落重點
### 問題背景：大型檔案讀寫效能不足
作者在 Azure Blob 讀取並即時轉碼影片後輸出，由於程式採單執行緒序列式 Read→Process→Write，結果整體輸送率僅 3.5 Mbps，不到直接下載的一半。監控顯示 CPU、頻寬皆未滿，證明瓶頸在流程而非硬體。

### 同步迴圈模型的限制
示範程式以 `Task.Delay` 模擬 I/O 與運算，十次循環總耗時 10 秒，恰為各階段時間 2 s+3 s+5 s 相加。資源利用如時間軸所示，任何時刻僅有單一資源工作，形同公司雇三人卻一次只讓一人上班。

### 多執行緒/生產線模式的回顧
作者回顧早年以 Thread、Stream Pipeline、Producer/Consumer 等模式解決類似問題的文章與雜誌稿，說明核心思想皆為「重疊作業」。然而傳統多執行緒需額外管理同步、排程與例外，程式結構易被切割而難以維護。

### C# Async/Await 語法與重構
自 .NET 4.5 起，C#5 提供 Async/Await syntax sugar，可將 method 返回型別提升為 `Task`，呼叫端立即返回並於需要時 `await` 結果。作者僅將 Write 改成 `async Task`，主流程記錄上一輪 Task，呼叫前 `await`，即可達到 Read+Process 與前一筆 Write 並行的 pipeline 效果。

### 實測結果與頻寬敏感度分析
改寫後程式總耗時約 5 秒，恰為 Write 500 ms 與 Read+Process 500 ms 重疊帶來的一倍提速。真實環境下以 2 Mbps–200 Mbps 客戶端頻寬測試，當 Write 時間 ≒ Read+Process 時間(80 Mbps) 時改善率 181%；頻寬降低導致 Write 偏長，提速比降至 102%。顯示 Async 僅能消除「等待」，無法提高單項 I/O 上限。

### 總結：何時選擇 Async/Await
若應用流程包含大量 I/O 等待而硬體利用率低，利用 Async/Await 重疊工作可用最少改動換取可觀提速，且程式碼保留同步式可讀性；若需求為 CPU 密集或需同時計算多任務，仍應使用 Thread 或 Parallel。簡言之，「排隊改串行」用 Async，「真平行運算」用 Thread。