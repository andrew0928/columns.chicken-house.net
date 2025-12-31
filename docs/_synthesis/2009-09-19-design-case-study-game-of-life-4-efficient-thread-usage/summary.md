---
layout: synthesis
title: "[設計案例] 生命遊戲 #4, 有效率的使用執行緒"
synthesis_type: summary
source_post: /2009/09/19/design-case-study-game-of-life-4-efficient-thread-usage/
redirect_from:
  - /2009/09/19/design-case-study-game-of-life-4-efficient-thread-usage/summary/
postid: 2009-09-19-design-case-study-game-of-life-4-efficient-thread-usage
---

# [設計案例] 生命遊戲 #4, 有效率的使用執行緒

## 摘要提示
- 問題動機: 30x30 網格卻啟動約 903 條執行緒且 CPU 使用率不足 5%，顯示實作效率低落。
- 設計方向: 由被動 callback 改為主動 execute，以更貼近真實「主動」生物行為與 OOP 模擬世界精神。
- yield return 時序: 以 yield return TimeSpan 取代 Thread.Sleep，讓單一流程可被切段、排程與喚醒。
- GameHost 轉型: 由放任每個 Cell 自管時間，改為集中調度：「少量執行緒 + 時間表排程」。
- 執行緒集區: 改用 ThreadPool 管理任務，避免大量長期閒置的專屬執行緒。
- 簡易排程器: 建立 ToDo List（時間表），按醒來時間排序，逐一喚醒並取得下一次喚醒時間。
- 資料結構: 使用 SortedList 實作 thread-safe 的 CellToDoList，提供 Add/Check/Get 操作。
- 畫面更新隔離: 畫面刷新由獨立執行緒處理，運算與呈現分離。
- 實作成效: 執行效果與 #3 相同，但執行緒由 903 條降至 9 條，大幅改善資源占用。
- 後續規劃: 在高效 GameHost 基礎上，將引入 OOP 繼承與多型，擴充多樣生物行為。

## 全文重點
作者觀察到上一版生命遊戲（#3）以每個 Cell 一條專屬執行緒的方式運作，在 30x30 規模下產生約 903 條執行緒，CPU 使用率卻不到 5%，顯示大量執行緒多處於 Sleep 狀態，資源浪費嚴重，若搬到線上遊戲伺服器將不可行。為解決此問題，本文採用「流程切段 + 集中排程」策略：將每個 Cell 內原本 Thread.Sleep 控制節奏的作法，改成 yield return TimeSpan 來回報下一次可運行的時間間隔。這種寫法讓邏輯保留主動性（更接近真實生物與 OOP 的模擬精神），同時把「等待」從每個 Cell 的專屬執行緒抽離，交給 GameHost 統一管理。

GameHost 的角色因此徹底改變：不再為每個 Cell 維持一條執行緒，而是以極少數執行緒搭配一個簡單的排程器來服務所有 Cell。實作上，作者建立一個 ToDo List（CellToDoList）作為時間表，內部用 SortedList 依喚醒時間排序並保證 thread-safe。GameHost 流程為：初始化世界與所有 Cell，先呼叫一次 OnNextStateChangeEx() 取得下次喚醒時間並加入 ToDo List；另開一條獨立執行緒定期刷新畫面；主迴圈則不斷從 ToDo List 取出下一個到期的 Cell，若未到時間便 Sleep 到該時刻，時間到後將 Cell 的下一步運算委派給 ThreadPool（執行 OnNextStateChangeEx），並依回傳的下一次休眠時間再將其加入 ToDo List。

此設計的重點在於：
- 使用執行緒集區（ThreadPool）承接短工作，避免大量長時閒置的專屬 Thread。
- 以 yield return TimeSpan 將連續邏輯切段，使「等待」由排程器處理，不佔用執行緒。
- 以時間優先佇列（SortedList）作為簡易排程器，確保按時喚醒與公平處理。
- 將畫面更新與計算分離，各用適當的執行緒進行。

結果顯示，在相同的可見行為與規則下，整體效果與 #3 無異，但所需執行緒數從約 903 條降至 9 條，效能與資源使用顯著提升。作者強調，儘管這只是練習題，但良好的 GameHost 設計是多數遊戲（特別是線上遊戲、社交遊戲）的基礎。打好效能與調度架構後，下一步將導入 OOP 的繼承與多型，設計多樣生物共同在世界中運作，持續朝更真實且可擴充的模擬前進。

## 段落重點
### 問題與動機：從「主動生物」到「效率瓶頸」
作者指出前一版（#3）雖把生物行為改為主動執行，理念上符合 OOP 模擬精神，但實務上出現大量執行緒閒置造成資源浪費。以 30x30 世界為例，近千條執行緒僅換來不到 5% 的 CPU 使用率。此模式難以擴充到真實遊戲伺服器場景，需在保持主動行為與即時回應的前提下，重新思考執行緒使用策略與效能。

### 流程切段：以 yield return 取代 Thread.Sleep
調整 Cell 的 WholeLife 實作，將 Thread.Sleep(ts) 改為 yield return TimeSpan，讓每個 Cell 在完成當前一步後告知「下次應該何時再喚醒」。這使得邏輯可被切段與排程。改寫後，GameHost 需主動詢問每個 Cell 下一次等待時間並負責喚醒，從「各自睡覺」轉為「集中叫醒」，為共用執行緒與集中排程鋪路。

### 目標與策略：以少量執行緒達到同等效果
明確的目標是維持 #2/ #3 的可見行為與效果，但用更高效率方式實現。策略包括：改用執行緒集區承接計算任務，避免大量閒置；建立簡易排程器，維護一個按喚醒時間排序的時間表；GameHost 依時序喚醒各 Cell，取得新一輪等待時間，重複此流程；畫面更新交由獨立執行緒，將呈現與計算分離。

### 時間表設計：CellToDoList 的介面與資料結構
為實作排程器，設計 CellToDoList，提供 AddCell、GetNextCell、CheckNextCell 與 Count 屬性。內部採 SortedList 依喚醒時間排序，雖具佇列語意但非 FIFO，而是時間優先。搭配基本的 lock 確保 thread-safe。此結構讓 GameHost 只需「丟工作進去、按順序取出來」，即能完成簡單而有效的時間排程。

### 實作流程：GameHost 主迴圈與 ThreadPool
GameHost 初始化世界，先讓每個 Cell 執行一次 OnNextStateChangeEx 以取得下一次喚醒時間並加入 ToDo List；另開一條執行緒每 500ms 刷新畫面；主迴圈持續從 ToDo List 取出最接近的 Cell，若未到時間則 Sleep 至該時刻，到時後將計算任務丟給 ThreadPool 執行，並依回傳的 TimeSpan 再次加入 ToDo List。如此以少量執行緒配合集區與時間表完成整體調度。

### 成效與展望：從效能基礎到 OOP 擴充
實驗結果顯示，畫面行為與規則與 #3 相同，但執行緒數由約 903 降至 9，效能與資源占用大幅改善。作者強調，這樣的 GameHost 架構是多數遊戲（含線上與社交遊戲）的基礎。接下來將在此高效基礎上導入 OOP 的繼承與多型，設計更多樣的生物共存於世界，逐步建構更接近真實的模擬環境。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C#/.NET 基礎語法與物件導向（類別、方法、繼承與多型的概念）
   - 基本多執行緒觀念（Thread、ThreadPool、Thread.Sleep）
   - 迭代器與 yield return（IEnumerable、協作式流程切割）
   - 時間與排程概念（DateTime、TimeSpan）
   - 基本資料結構與同步化（Queue/SortedList、lock 保障 thread-safe）

2. 核心概念：
   - 單位行為的主動驅動：由每個 Cell 主動回報「下一次要醒來的時間」（yield return TimeSpan）
   - 中央排程器（GameHost）：以少量執行緒統一管理所有 Cell 的醒來與執行
   - 工作切碎與共用執行緒：用 ThreadPool 取代「每 Cell 一條專屬 Thread」
   - 時間表/ToDo List（優先佇列）：按 NextWakeUpTime 管理下一個待處理 Cell
   - 顯示與模擬解耦：獨立渲染執行緒定期更新畫面
   彼此關係：Cell 用 yield 切割長流程→回報下一次喚醒時間→GameHost 依 ToDo List 排程→用 ThreadPool 執行下一步→再度入列；渲染與模擬分離並行。

3. 技術依賴：
   - Cell.WholeLife 由 Sleep 模式改為 IEnumerable<TimeSpan>（yield return）
   - GameHost 依賴 ToDo List（內部 SortedList + lock）維持最接近的下一個喚醒點
   - 使用 ThreadPool.QueueUserWorkItem 執行 Cell 的下一狀態轉移（OnNextStateChangeEx）
   - 以 Thread 啟動獨立 RefreshScreen 渲染循環
   - DateTime.Now 與 TimeSpan 控制喚醒時機

4. 應用場景：
   - 多代理人模擬（生命遊戲、群體行為、AI agent）
   - 遊戲伺服器（大量 NPC/玩家行為的有效率排程）
   - 互動式平台遊戲（例如社群/小遊戲）需兼顧效能與即時性
   - 任何需要大量輕量任務週期性執行的系統（IoT 模擬、事件驅動模擬）

### 學習路徑建議
1. 入門者路徑：
   - 了解 Thread vs ThreadPool、Sleep 的基本行為與成本
   - 學習 C# 的 IEnumerable/Iterator 與 yield return 的語義
   - 練習以簡單範例將長流程改寫為 yield 分段（如計數器每次 yield 一個延遲）
   - 熟悉 TimeSpan/DateTime 的基本使用

2. 進階者路徑：
   - 實作 thread-safe 的 ToDo List（以 SortedList 或最小堆為核心，配合 lock）
   - 設計 GameHost 事件迴圈：CheckNextCell/GetNextCell、睡眠至下一事件、喚醒後入列
   - 使用 ThreadPool 執行工作並處理回傳（下一次喚醒時間）
   - 分離渲染執行緒與模擬執行緒，確保互不阻塞

3. 實戰路徑：
   - 將既有 per-thread 的 agent 模型改為 yield + 中央排程器
   - 加入停止條件、動態加入/移除 Cell/Agent 的能力
   - 度量與監控：觀察執行緒數、CPU 使用率、延遲抖動
   - 擴展至 OOP 多型：不同生物/行為以繼承與多型提供不同的狀態轉移與節奏

### 關鍵要點清單
- 將 Thread.Sleep 改為 yield return TimeSpan（協作式切割）: 用編譯器將連續流程切段，利於共享執行緒與中央排程 (優先級: 高)
- 中央排程器 GameHost: 以單一事件迴圈統籌所有 Cell 的喚醒與執行，避免每 Cell 一執行緒 (優先級: 高)
- ToDo List 作為時間表: 以下一次喚醒時間排序的佇列（優先佇列）決定處理順序 (優先級: 高)
- ThreadPool 使用: 用執行緒集區承接短小任務，降低過量 Thread 帶來的成本 (優先級: 高)
- 渲染與模擬解耦: 獨立渲染執行緒定期刷新，避免阻塞模擬排程 (優先級: 中)
- thread-safe 資料結構: ToDo List 需以 lock 或等效手段保證併發正確性 (優先級: 高)
- 時間控制策略: 以 DateTime.Now + TimeSpan 控制睡眠至下一事件點，減少忙等 (優先級: 中)
- OnNextStateChangeEx 設計: 回傳下一次喚醒的 TimeSpan?，為排程器提供決策資訊 (優先級: 高)
- 減少執行緒數的效益: 從 ~903 降至 ~9 條，顯著降低上下文切換與資源耗用 (優先級: 中)
- 工作切碎基本法則: 想要共享執行緒，必須將長任務拆成可快速完成的小步驟 (優先級: 高)
- 結構可擴充性: 以 OOP 多型擴展不同生物行為，排程層不需感知具體行為 (優先級: 中)
- 定時 vs 事件驅動: 從固定週期 callback 轉為每個 agent 自主節奏的事件式驅動 (優先級: 中)
- 資料結構選擇: SortedList 可行，但最小堆（priority queue）在大量元素時更有效率 (優先級: 低)
- 停止條件與資源回收: 實務需要加上終止條件、取消與清理機制 (優先級: 中)
- 效能監控與調校: 度量 CPU/執行緒/延遲，調整睡眠精度、批次喚醒策略等 (優先級: 低)