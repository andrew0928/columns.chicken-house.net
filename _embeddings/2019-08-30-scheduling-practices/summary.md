# 後端工程師必備: 排程任務的處理機制練習 (12/01 補完)

## 摘要提示
- 排程痛點: Web 以 Request/Response 為核心，天生不擅長「指定時間執行」的工作。  
- 輪詢瓶頸: 由「分」縮短到「秒」會使 DB 查詢量放大 60 倍，效能與精度陷入兩難。  
- 必要條件: 低負載、低延遲、分散式高可用、絕不重覆執行同一 Job。  
- 評分機制: 成本分數 Cost 與精確度分數 Efficient，量化每種實作的優劣。  
- 測試流程: 10 分鐘不斷產生任務、五個 instance 同時跑，並混入隨機中斷驗證 HA。  
- JobsRepo API: GetReadyJobs / AcquireJobLock / ProcessLockedJob 為存取與鎖定的唯一通道。  
- 範例解法: 先鎖後排、BlockingCollection/Channel、Random 漂移避撞等技巧。  
- PR 評比: 7 份解答交手，比較 Cost 與 Efficient，並逐一 Code Review 優缺點。  
- 最佳策略: 提前鎖定但控制時間、錯開執行瞬間、同時顧及停機收斂。  
- 結論建議: 能自己造輪子才有整合與調校空間，透過量化指標反覆優化最具學習價值。

## 全文重點
本文以「如何在只能輪詢資料庫的前提下，實作高效、精準、可擴充的排程服務」為主軸，先闡述 Web 系統對「預約執行」的先天劣勢，進而提出練習題：  
1. 資料庫僅被動提供 Job 清單，無任何事件通知。  
2. 服務必須輪詢，卻要兼顧低負載、高精度、分散式、一次僅執行一次。  

作者訂下固定的準備/延遲門檻（MinPrepareTime=10s, MaxDelayTime=30s）與兩組量化指標：  
‧ 成本＝查詢清單×100＋鎖定失敗×10＋單筆查詢×1；  
‧ 精度＝所有 Job 延遲平均＋延遲標準差。  

測試程式會在 10 分鐘內不斷產生各種節奏的排程資料，並啟動五個實例、隨機殺掉三個，再以指標驗證可靠度及計算得分。  
開發者只能透過 JobsRepo 操作資料庫，避免外部捷徑；範例碼用 .NET Generic Host＋BackgroundService 示範最基本解法。  

下半部彙整七位參賽者的 Pull Request，逐一跑 1~10 個 instance、量化 Cost/Efficient、再檢視程式結構。常見優化招式包括：  
‧ 先 GetJob 再 Decide 是否 Lock 以降低成本；  
‧ 提前 N 毫秒鎖定、並以亂數漂移避免多實例同時碰撞；  
‧ 使用 BlockingCollection 或 Channel 實作生產者/消費者，拆分 Fetch 與 Execute；  
‧ 充分平行化 ProcessLockedJob，處理瞬間大量 Job；  
‧ 優雅停機：CancellationToken、WaitHandle、CompleteAdding 等確保已鎖 Job 不遺失。  

最終作者示範方案以「預先 300~1700ms 隨機鎖定＋10 條 Worker Thread」取得最低 Efficient 分，並兼顧 Cost 與 1 秒內可收斂關機。文章最後強調：即使有眾多現成服務，理解核心機制、能量化評估並在必要時自行打造，才是架構師真正的價值。

## 段落重點
### 問題定義
Web 系統缺乏主動執行能力，排程任務只剩「輪詢 DB」一途；直接每秒查詢雖可達秒級精度，卻把 DB 壓垮，需尋求折衷。

### 需求定義
1) 最小化資料庫負載；2) 啟動延遲小且穩定；3) 支援多實例、高可用；4) 嚴禁重覆執行。前提：Job 至少提前 10 秒寫入，最遲 30 秒內一定要執行。

### 評量指標
以三種查詢對 DB 的次數計算 Cost Score；以延遲平均與標準差計算 Efficient Score，分數越低代表方案越佳。

### 測試方式
自動產生多型態 Job，啟動 5 個排程實例並隨機中斷，先驗證所有 Job 是否準時且僅執行一次，再依兩指標排名。

### 開發方式
提供 SQL Schema 與 JobsRepo；開發者須撰寫 BackgroundService，僅能透過 JobsRepo 操作；文中範例以單純輪詢＋ThreadPool 示範最低標實作。

### Solution & Review
收錄 7 份 PR，逐一跑 11 組測試並 Code Review：  
- HankDemo 與 JolinDemo 架構正統但缺乏進一步優化；  
- JWDemo 透過隨機延遲降低碰撞，Cost 分最低；  
- LeviDemo 因偷跑 Bug 失敗；  
- BorisDemo、JulianDemo、AndyDemo 各自權衡先鎖策略與平行度，在 Cost 與 Efficient 取得平衡。

### 示範專案
作者方案：10 條 Worker＋BlockingCollection；提前 0.3~1.7 秒鎖定，並加入亂數漂移；確保任何時候 1 秒內可優雅停機；最終拿下全場最低 Efficient 分並保持 Cost 在前段。

### 結論
現成服務雖多，自行理解並量化設計仍必須；透過可重現的 POC 與指標化比對，工程師才能真正掌握效能瓶頸、在實務中做出最適合的整合或自建決策。