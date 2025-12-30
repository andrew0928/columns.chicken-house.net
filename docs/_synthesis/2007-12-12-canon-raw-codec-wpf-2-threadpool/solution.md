---
layout: synthesis
title: "Canon Raw Codec + WPF #2, ThreadPool"
synthesis_type: solution
source_post: /2007/12/12/canon-raw-codec-wpf-2-threadpool/
redirect_from:
  - /2007/12/12/canon-raw-codec-wpf-2-threadpool/solution/
---

以下內容依據提供的文章，提取並結構化 15 個具教學價值的問題解決案例。每個案例均包含問題、根因、解法、實測效果、學習要點與練習評估，便於用於實戰教學、專案練習與能力評估。

## Case #1: 用 WPF 重建「批次縮圖」工具以替代 XP Powertoy

### Problem Statement（問題陳述）
業務場景：團隊在 Windows Vista 環境下已無法使用 XP 時代的 Resize Pictures Powertoy。需要一個可右鍵快速批次縮圖的小工具，涵蓋 JPG 與 CR2（Canon RAW）等格式，並維持良好的 UI 響應。
技術挑戰：要在 WPF/.NET 上重現簡單可靠的批次縮圖流程，支援 RAW 解碼、JPEG 編碼，以及背景運算與 UI 互動的平衡。
影響範圍：無法快速縮圖導致影像處理流程中斷，需改用大型影像軟體或手動處理，耗費大量時間與人力。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. XP Powertoy 與 Vista 不相容：GDI+ 與 WPF 圖像堆疊差異導致無法沿用。
2. 影像編解碼負載高：Canon RAW 解碼耗時，單純移植 UI 並不足以達到良好體驗。
3. UI 與背景工作相互干擾：內建 ThreadPool 無優先權管控，造成 UI 卡頓。

深層原因：
- 架構層面：缺乏面向不同工作類型（RAW/JPEG）的排程模型與資源隔離。
- 技術層面：ThreadPool 不支援多池/固定池大小/優先權設定。
- 流程層面：缺少標準化的測試集與量測流程以驗證效益。

### Solution Design（解決方案設計）
解決策略：以 WPF 建立簡潔 UI，底層整合 Canon RAW codec 與 JPEG 編碼，並引入自製 SimpleThreadPool，分離 RAW 與 JPEG 任務、設定優先權、固定執行緒數，確保 UI 響應並提升整體吞吐。

實施步驟：
1. 建立 WPF UI 與檔案挑選流程
- 實作細節：使用 OpenFileDialog/DragDrop，提供尺寸選單與進度列
- 所需資源：.NET 3.x WPF、XAML
- 預估時間：0.5 天

2. 整合編解碼與批次任務
- 實作細節：呼叫 RAW 解碼、JPEG 編碼；統一任務介面
- 所需資源：Canon RAW Codec、WIC/JPEG Encoder
- 預估時間：1 天

3. 導入 SimpleThreadPool 並分池
- 實作細節：RAW（1 執行緒，高優先權）、JPEG（4 執行緒，低優先權）
- 所需資源：自製 SimpleThreadPool
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 建立兩個工作池：RAW 優先、JPEG 次之
var rawPool  = new SimpleThreadPool(1, ThreadPriority.AboveNormal);
var jpgPool  = new SimpleThreadPool(4, ThreadPriority.BelowNormal);
rawPool.StartPool();
jpgPool.StartPool();

foreach (var job in jobs)
{
    if (job.Type == JobType.RawDecode)
        rawPool.QueueWorkItem(_ => ProcessRaw(job), null);
    else
        jpgPool.QueueWorkItem(_ => ProcessJpeg(job), null);
}

// 等待全部完成
rawPool.EndPool();
jpgPool.EndPool();
```

實際案例：
- 批次資料：125 JPG + 20 G9 CR2 + 2 G2 CR2
- 實作環境：Windows Vista, .NET 3.x WPF, Canon RAW Codec, Core2Duo E6300

實測數據：
改善前：無替代工具（須手動或大型軟體）
改善後：完整批次於 90 秒完成（見 Case #10 詳述）
改善幅度：可量化吞吐達成；替代不可用之 Powertoy

Learning Points（學習要點）
核心知識點：
- WPF 與影像編解碼整合的基本流程
- 背景工作與 UI 響應的分離
- 批次處理的任務建模

技能要求：
- 必備技能：WPF/XAML、基本多執行緒
- 進階技能：影像管線設計、資源隔離排程

延伸思考：
- 可否做成 Explorer shell extension？
- 需注意解碼器相容性與授權
- 可用 TPL/Dataflow（現代 .NET）重構

Practice Exercise（練習題）
- 基礎：做一個可選檔案與選尺寸的 WPF 對話框（30 分）
- 進階：實作批次轉檔與進度列（2 小時）
- 專案：加入 RAW/JPEG 分池與優先權控制（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可選檔、轉檔、輸出正確
- 程式碼品質（30%）：模組化、命名、例外處理
- 效能優化（20%）：多核利用、UI 流暢
- 創新性（10%）：介面易用性、可擴充性

---

## Case #2: CR2 全尺寸轉 JPG 過慢：改以解碼階段縮放

### Problem Statement（問題陳述）
業務場景：大量 CR2 檔需縮成小圖（例如 800x600）供快速預覽或分享。若先全尺寸解碼再縮放，速度緩慢，影響批次效率。
技術挑戰：如何在解碼階段就利用解碼器的縮放能力，避免全尺寸解碼的高成本。
影響範圍：單張 CR2 轉同尺寸 JPEG 要 60–80 秒，批次處理時間過長。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 全尺寸解碼工作量大：RAW 展開成本高。
2. 先全解再縮小：多做一步不必要的像素處理。
3. 未用到解碼器對「縮小輸出」的最佳化路徑。

深層原因：
- 架構層面：影像管線未抽象「目標尺寸」傳遞至解碼器。
- 技術層面：未活用 WIC/Codec 的解碼縮放能力。
- 流程層面：缺乏針對輸出需求（小圖）的策略切換。

### Solution Design（解決方案設計）
解決策略：直接在解碼階段指定目標尺寸（DecodePixelWidth/Height），讓解碼器走縮圖優化路徑，避免全尺寸解碼成本，顯著縮短處理時間。

實施步驟：
1. 目標尺寸前傳
- 實作細節：在開啟影像時指定 DecodePixelWidth/Height
- 所需資源：WPF BitmapImage/WIC
- 預估時間：0.5 天

2. 驗證輸出品質與速度
- 實作細節：抽樣比對畫質、量測時間
- 所需資源：測試資料集、碼表
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 以解碼階段縮放至 800 寬，避免全尺寸解碼
var bi = new BitmapImage();
bi.BeginInit();
bi.CacheOption = BitmapCacheOption.OnLoad;
bi.DecodePixelWidth = 800; // 或 DecodePixelHeight
bi.UriSource = new Uri(cr2Path);
bi.EndInit();

// 後續直接編碼成 JPEG 小圖
EncodeToJpeg(bi, outputPath, quality: 85);
```

實作環境：Windows Vista, .NET 3.x WPF, Canon RAW Codec
實測數據：
改善前：CR2(4000x3000) -> JPG(4000x3000) 約 60–80 秒/張
改善後：CR2 -> JPG(800x600) 約 5 秒/張
改善幅度：時間縮短約 92% 以上

Learning Points（學習要點）
核心知識點：
- 解碼階段縮放的效能優勢
- WIC 解碼參數與畫質取捨
- 針對需求選擇最短路徑

技能要求：
- 必備技能：WPF 影像 API
- 進階技能：畫質評估與壓縮參數調校

延伸思考：
- 可否因應不同輸出尺寸自動切換策略？
- 不同相機 RAW 解碼器差異？
- 大量網路檔案時的串流與快取策略

Practice Exercise（練習題）
- 基礎：用 DecodePixelWidth 讀一張 CR2 並輸出 800x600（30 分）
- 進階：加入畫質選項與時間量測（2 小時）
- 專案：做一個可選多尺寸的批次轉檔器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：尺寸正確、可批次
- 程式碼品質（30%）：結構清晰、錯誤處理
- 效能優化（20%）：時間相較全尺寸縮短顯著
- 創新性（10%）：自動尺寸策略或畫質優化

---

## Case #3: 多核心未吃滿：將 RAW 視為單執行緒瓶頸

### Problem Statement（問題陳述）
業務場景：雙核 CPU 執行 CR2 解碼時 CPU 使用率僅約 50–60%，即使丟多個 ThreadPool 工作也不見提升，導致吞吐不足。
技術挑戰：辨識 RAW 解碼的內部序列化或鎖定，避免盲目提高併發造成無效競爭。
影響範圍：CPU 無法吃滿，多任務同時反而拉長單張處理時間。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. RAW 解碼器內部鎖或序列化：多工無效。
2. ThreadPool 無法限制 RAW 任務數量。
3. 任務混雜搶占 CPU，引發上下文切換而無收益。

深層原因：
- 架構層面：未區分「不可並行」與「可並行」工作。
- 技術層面：缺少任務類型與池化策略。
- 流程層面：未先以基準測試驗證併發有效性。

### Solution Design（解決方案設計）
解決策略：將 RAW 解碼固定在單執行緒（1 條）高優先權池中執行，視為不可並行的瓶頸；並將其他可並行（JPEG）工作在另一池中平行處理，以吃滿剩餘 CPU。

實施步驟：
1. RAW 任務單執行緒化
- 實作細節：SimpleThreadPool(1, AboveNormal) 專責 RAW
- 所需資源：自製 ThreadPool
- 預估時間：0.5 天

2. 非 RAW 任務平行化
- 實作細節：SimpleThreadPool(4, BelowNormal) 處理 JPEG
- 所需資源：同上
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var rawPool  = new SimpleThreadPool(1, ThreadPriority.AboveNormal);
var jpgPool  = new SimpleThreadPool(4, ThreadPriority.BelowNormal);

rawPool.StartPool(); jpgPool.StartPool();
// RAW 工作只進 rawPool
rawPool.QueueWorkItem(_ => DecodeRaw(cr2Path), null);
// JPEG 工作只進 jpgPool
jpgPool.QueueWorkItem(_ => EncodeJpeg(src, outPath), null);
```

實作環境：Vista, .NET 3.x, Core2Duo E6300, Canon RAW Codec
實測數據：
改善前：RAW 併發 >1 時 CPU 仍 ~60%，且整體時間拉長
改善後：RAW 單執行緒 + JPEG 多執行緒，整體時間縮短（見 Case #10）
改善幅度：整體批次由 110 秒降至 90 秒的一部分貢獻

Learning Points（學習要點）
核心知識點：
- 辨識不可並行瓶頸
- 任務分池與資源隔離
- CPU 使用率與吞吐的關聯

技能要求：
- 必備技能：效能測試與觀察
- 進階技能：系統瓶頸分析與任務分級

延伸思考：
- 若 RAW 解碼器未來支援並行，如何調整？
- 自動檢測最佳 RAW 併發度
- 與 I/O 任務混合調度的策略

Practice Exercise（練習題）
- 基礎：測量單/雙 RAW 併發的 CPU 與時間（30 分）
- 進階：寫一個偵測最佳 RAW 併發度的小工具（2 小時）
- 專案：做一個可自適應調整池大小的排程器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可調整 RAW 併發並量測
- 程式碼品質（30%）：抽象清晰、易測試
- 效能優化（20%）：能避免無效併發
- 創新性（10%）：自動探索最適參數

---

## Case #4: 內建 ThreadPool 不足：自製 SimpleThreadPool 以控優先權與多池

### Problem Statement（問題陳述）
業務場景：需要同時處理 RAW 與 JPEG 任務，並保護 UI 響應。內建 ThreadPool 無優先權控制、不可多池分工，導致 UI 卡頓與資源無法精準分配。
技術挑戰：在 .NET 下實作輕量可控的 ThreadPool（固定大小、可設定優先權、多池、WaitAll）。
影響範圍：內建 ThreadPool 導致整體處理時間偏長、UI 頓挫。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無法控制工作執行緒優先權。
2. 無法為不同工作類型建立獨立池。
3. 等待全部完成需手動 WaitHandle，繁瑣易錯。

深層原因：
- 架構層面：缺乏可配置的排程層。
- 技術層面：ThreadPool API 適用一般場景，不符高控性需求。
- 流程層面：缺少基於任務型態的資源管理策略。

### Solution Design（解決方案設計）
解決策略：設計 SimpleThreadPool，提供固定池大小、優先權設定、QueueWorkItem 與 EndPool；以最小代碼成本滿足任務分池與控制需求。

實施步驟：
1. Worker 與 Queue 設計
- 實作細節：阻塞佇列 + 背景工作執行緒
- 所需資源：Monitor/AutoResetEvent
- 預估時間：0.5 天

2. API 與優先權
- 實作細節：StartPool/QueueWorkItem/EndPool，Thread.Priority
- 所需資源：.NET Thread API
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
private void WorkerLoop()
{
    while (_running)
    {
        Action job = null;
        lock (_lock)
        {
            while (_running && _queue.Count == 0) Monitor.Wait(_lock);
            if (!_running) break;
            job = _queue.Dequeue();
        }
        try { job?.Invoke(); }
        catch (Exception ex) { Log(ex); }
    }
}

public void EndPool()
{
    lock (_lock) { _running = false; Monitor.PulseAll(_lock); }
    foreach (var t in _workers) t.Join();
}
```

實作環境：.NET 3.x，C#
實測數據：
改善前：僅用內建 ThreadPool，批次 110 秒
改善後：用 SimpleThreadPool，批次 90 秒（見 Case #10）
改善幅度：約 18% 總時間縮短

Learning Points（學習要點）
核心知識點：
- 自製 ThreadPool 的關鍵設計點
- 優先權與多池的效能意義
- 可靠停止/等待機制

技能要求：
- 必備技能：C# 多執行緒基礎
- 進階技能：同步原語與佇列設計

延伸思考：
- 新版 .NET 可用自訂 TaskScheduler 取代
- 加入工作取消/逾時/權重排程
- 觀測指標（queue 長度、等待時間）

Practice Exercise（練習題）
- 基礎：寫一個固定大小工作池（30 分）
- 進階：加入 EndPool 與優先權（2 小時）
- 專案：支援多池、不同優先權、簡單權重排程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：Queue/Wait/Stop 可用
- 程式碼品質（30%）：同步正確、無死鎖
- 效能優化（20%）：低額外開銷
- 創新性（10%）：擴充性設計

---

## Case #5: UI 被 CPU 任務拖慢：以優先權與回到 UI 執行緒保護體驗

### Problem Statement（問題陳述）
業務場景：批次轉檔時進度列會動，但預覽圖出不來或延遲很久，使用者體驗不佳。
技術挑戰：CPU bound 工作占用過高且無優先權控制，導致 UI Thread Starvation。
影響範圍：UI 互動變慢或「看起來卡住」。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 背景工作與 UI 同優先權競爭。
2. 內建 ThreadPool 無法設低優先權。
3. 更新 UI 未使用 Dispatcher 導致跨執行緒問題。

深層原因：
- 架構層面：無 UI/工作隔離策略。
- 技術層面：未正確返回 UI 執行緒更新控制項。
- 流程層面：缺乏 UI 響應性驗證指標。

### Solution Design（解決方案設計）
解決策略：將 JPEG 等大量 CPU 工作設為 BelowNormal/Lowest，RAW 稍高；所有 UI 更新以 Dispatcher.Post 回到 UI 執行緒執行，確保 Preview/Progress 及時。

實施步驟：
1. 低優先權背景池
- 實作細節：SimpleThreadPool(..., ThreadPriority.BelowNormal/Lowest)
- 所需資源：自製 ThreadPool
- 預估時間：0.5 天

2. UI Dispatcher 更新
- 實作細節：Dispatcher.BeginInvoke 更新 Image/Progress
- 所需資源：WPF Dispatcher
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 背景完成一張後，回 UI 更新預覽
Application.Current.Dispatcher.BeginInvoke(new Action(() =>
{
    previewImage.Source = resultBitmap;
    progressBar.Value = percent;
}));
```

實作環境：WPF/.NET 3.x
實測數據：
改善前：進度列動但預覽不出現，主觀體驗不佳
改善後：每張完成即顯示預覽（文章述及）
改善幅度：UI 響應性大幅改善（質性指標）

Learning Points（學習要點）
核心知識點：
- UI 執行緒模型與 Dispatcher
- 背景工作優先權對互動性的影響
- 使用者感知進度的重要性

技能要求：
- 必備技能：WPF UI 執行緒
- 進階技能：優先權調整與量測

延伸思考：
- 可加入節流（Throttle）避免 UI 更新過頻
- 以 FPS 或主緒排程延遲為客觀指標
- 背景任務分塊與切片化

Practice Exercise（練習題）
- 基礎：背景執行計算，UI 顯示進度（30 分）
- 進階：加入優先權與節流更新（2 小時）
- 專案：圖庫瀏覽器，邊載入邊預覽（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：UI 穩定更新
- 程式碼品質（30%）：執行緒安全
- 效能優化（20%）：UI 無明顯卡頓
- 創新性（10%）：進度與預覽體驗佳

---

## Case #6: 兩池分工：RAW 單執行緒 + JPEG 多執行緒

### Problem Statement（問題陳述）
業務場景：混合 CR2 與 JPG 的批次轉檔需同時兼顧吞吐與 UI 響應。
技術挑戰：如何同時執行 RAW 與 JPEG，使 CPU 維持高利用率，避免 RAW 長尾拖慢整體。
影響範圍：單池執行導致序列化，或 JPEG 全吃在前面造成後段長尾 50% CPU。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. RAW 與 JPEG 工作特性不同（長任務 vs 短任務）。
2. 單池會讓短任務擠在前段，後段只剩 RAW 長尾。
3. 無法針對不同工作型態精細排程。

深層原因：
- 架構層面：混雜工作型態未分池。
- 技術層面：無優先權差異與資源隔離。
- 流程層面：缺少混合負載的策略。

### Solution Design（解決方案設計）
解決策略：建立兩個池：RAW（1 條，優先），JPEG（4 條，次優先），強迫同時執行兩類工作，讓 RAW 先跑、JPEG 切吃剩餘 CPU，以縮短長尾。

實施步驟：
1. 建立兩池與工作路由
- 實作細節：依檔案型態派送到不同池
- 所需資源：SimpleThreadPool
- 預估時間：0.5 天

2. 排程策略驗證
- 實作細節：觀測 CPU 曲線、總時間
- 所需資源：PerfMon 或內建監視器
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 路由：RAW -> rawPool, JPEG -> jpgPool
foreach (var f in files)
{
    if (IsRaw(f)) rawPool.QueueWorkItem(_ => ProcessRawToTarget(f), null);
    else          jpgPool.QueueWorkItem(_ => ProcessJpegResize(f), null);
}
```

實測數據（同資料集）：
改善前：內建 ThreadPool：110 秒、CPU 後段 ~50%
改善後：雙池策略：90 秒、持續有 JPEG 吃滿空檔
改善幅度：時間縮短約 18%，UI 響應改善

Learning Points（學習要點）
核心知識點：
- 雙池策略的優勢
- 長短任務併行減少長尾
- CPU 面積（積分）觀念

技能要求：
- 必備技能：基礎排程概念
- 進階技能：效能監測與策略調整

延伸思考：
- 三池策略（I/O、CPU、GPU）？
- 動態調整 JPEG 池大小
- 根據負載回饋自動調參

Practice Exercise（練習題）
- 基礎：將任務依型態分派至不同池（30 分）
- 進階：加入負載監控與自動調整（2 小時）
- 專案：可視化 CPU/Queue 長度與策略切換（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：雙池分工正確
- 程式碼品質（30%）：模組清晰
- 效能優化（20%）：長尾縮短明顯
- 創新性（10%）：自動調參或視覺化

---

## Case #7: 限制執行緒數量避免反而變慢

### Problem Statement（問題陳述）
業務場景：直覺會「開更多執行緒更快」，實際上 RAW 多開反而變慢，JPEG 適度多開才有效。
技術挑戰：決定不同任務的最佳執行緒數，避免上下文切換與同步成本。
影響範圍：過度併發導致總時間拉長、UI 卡頓。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. RAW 解碼器內部鎖，併發無效。
2. JPEG 任務短小，可平行但受限核心數。
3. Context switch 增加、快取失誤。

深層原因：
- 架構層面：無「每類任務最佳併發度」參數化。
- 技術層面：對 CPU bound 任務的錯誤直覺。
- 流程層面：未做系統化壓力測試。

### Solution Design（解決方案設計）
解決策略：RAW 固定 1；JPEG 設為接近核心數（雙核 2–4，四核 4），以測試驗證最佳值，再固定為配置。

實施步驟：
1. 參數探索
- 實作細節：嘗試 JPEG=1..N 測試總時間
- 所需資源：自動化測試腳本
- 預估時間：0.5 天

2. 配置固定化
- 實作細節：寫入設定檔，啟動載入
- 所需資源：app.config/JSON
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 讀配置決定池大小
int jpgWorkers = Math.Min(Environment.ProcessorCount, 4);
var jpgPool = new SimpleThreadPool(jpgWorkers, ThreadPriority.BelowNormal);
```

實測數據：
改善前：猜測性多開執行緒，波動大、總時間偏長
改善後：RAW=1、JPEG≈核心數，穩定達到 90 秒結果
改善幅度：穩定性與吞吐提升（相對內建 ThreadPool）

Learning Points（學習要點）
核心知識點：
- 執行緒數 ≠ 越多越好
- 核心數與任務特性關聯
- 設定可調與驗證

技能要求：
- 必備技能：CPU/執行緒知識
- 進階技能：基準測試設計

延伸思考：
- 不同硬體自動調整
- 任務時間分佈估測（短任務/長任務）
- NUMA/快取親和性

Practice Exercise（練習題）
- 基礎：測試 JPEG 併發度對時間影響（30 分）
- 進階：自動探索最佳執行緒數（2 小時）
- 專案：併發度 vs 成本建模（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：參數可調
- 程式碼品質（30%）：設定管理
- 效能優化（20%）：找到最佳區間
- 創新性（10%）：自動化探索

---

## Case #8: 等待全部處理完成：EndPool 取代繁瑣 WaitHandle

### Problem Statement（問題陳述）
業務場景：批次轉檔完成後需進行收尾（例如 UI 更新、資源釋放），用 WaitHandle 管控多個工作繁瑣。
技術挑戰：提供簡單 API 等待池內任務全部完成。
影響範圍：WaitHandle 容易誤用/遺漏，增加維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 內建 ThreadPool 無「WaitAll」型 API。
2. 多個 Handle 管理複雜。
3. 停止流程與回收難以一致化。

深層原因：
- 架構層面：缺少標準化關閉流程。
- 技術層面：同步原語使用成本高。
- 流程層面：收尾程序未模板化。

### Solution Design（解決方案設計）
解決策略：SimpleThreadPool 提供 EndPool：停止接單、等待佇列清空、Join 所有 worker；將收尾變成單一呼叫。

實施步驟：
1. 設計停止旗標
- 實作細節：_running=false + PulseAll
- 所需資源：Monitor
- 預估時間：0.25 天

2. Join Workers
- 實作細節：逐一 Join 確保退出
- 所需資源：Thread.Join
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
Console.WriteLine("wait stop");
rawPool.EndPool();
jpgPool.EndPool();
// 此處做最終 UI 更新/資源釋放
```

實測數據：
改善前：需手動管理多個 WaitHandle
改善後：單呼叫 EndPool 完成等待與釋放
改善幅度：開發與維護複雜度顯著降低（質性）

Learning Points（學習要點）
核心知識點：
- 工作池關閉設計
- 正確使用 Join 與同步
- 收尾流程一致化

技能要求：
- 必備技能：同步/Join
- 進階技能：中止/取消設計

延伸思考：
- 支援取消中的安全停止
- 逾時與降級策略
- 統計最終成果（成功/失敗）

Practice Exercise（練習題）
- 基礎：為工作池加入 EndPool（30 分）
- 進階：EndPool 回報統計數據（2 小時）
- 專案：含取消、逾時的關閉流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：關閉可控
- 程式碼品質（30%）：無死鎖/資源洩漏
- 效能優化（20%）：最小化等待成本
- 創新性（10%）：友善 API 與回報

---

## Case #9: 排程優化避免「100% 峰值 + 50% 長尾」

### Problem Statement（問題陳述）
業務場景：使用內建 ThreadPool 時，前段全是 JPEG（CPU 100%），後段剩 RAW（CPU ~50%）形成長尾，總時間變長。
技術挑戰：將 RAW 與 JPEG 交錯執行，讓 CPU 曲線更平滑，縮短總完成時間。
影響範圍：整體批次時間偏長。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 先到先服務導致短任務（JPEG）集中前段。
2. RAW 任務滯後形成長尾。
3. 無優先權與分池造成排程偏差。

深層原因：
- 架構層面：缺少公平策略或權重
- 技術層面：單池無法約束任務混排
- 流程層面：未以 CPU 面積（積分）觀念評估

### Solution Design（解決方案設計）
解決策略：RAW 高優先權先跑、JPEG 低優先權補滿剩餘 CPU，強迫交錯執行，縮短長尾、縮短總時間。

實施步驟：
1. 優先權與兩池
- 實作細節：rawPool(↑)、jpgPool(↓)
- 所需資源：SimpleThreadPool
- 預估時間：0.5 天

2. 交錯入列策略
- 實作細節：每批入列含 RAW 與 JPEG
- 所需資源：Queue 策略
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 確保 RAW 先入列，同時維持 JPEG 積壓量
EnqueueNextRawBatch(rawFiles.Take(1));
EnqueueNextJpegBatch(jpegFiles.Take(4)); // 適度保留待處理
```

實測數據：
改善前：110 秒（前段 100%，後段 ~50%）
改善後：90 秒（交錯執行）
改善幅度：約 18%

Learning Points（學習要點）
核心知識點：
- CPU 面積（積分）與總時間關係
- 長短任務混合排程
- 入列策略影響大於想像

技能要求：
- 必備技能：排程基礎
- 進階技能：實驗設計與可視化

延伸思考：
- 權重式入列（Weighted Fair）
- 基於 SLA 的任務優先權
- 在線負載變化的自適應

Practice Exercise（練習題）
- 基礎：設計交錯入列策略（30 分）
- 進階：視覺化 CPU 曲線與 Queue 長度（2 小時）
- 專案：可配置權重的排程器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：交錯生效
- 程式碼品質（30%）：結構清晰
- 效能優化（20%）：長尾明顯縮短
- 創新性（10%）：可視化與自適應

---

## Case #10: 實測基準：內建 ThreadPool 110 秒 → SimpleThreadPool 90 秒

### Problem Statement（問題陳述）
業務場景：需以量化數據驗證新排程策略（雙池 + 優先權）的效益。
技術挑戰：同資料集、同環境、公正量測 CPU 與總時間。
影響範圍：無數據將難以推動改變與收斂設計。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 內建 ThreadPool 對混合工作不友善。
2. 無優先權導致長尾。
3. RAW 併發無效造成 CPU 閒置。

深層原因：
- 架構層面：缺乏數據導向決策
- 技術層面：未對比替代方案
- 流程層面：缺少固定測試集

### Solution Design（解決方案設計）
解決策略：以固定資料集（125 JPG + 20 G9 RAW + 2 G2 RAW），對比兩種排程策略，量測總時間與 CPU 使用曲線，據以決策。

實施步驟：
1. 設定基準測試
- 實作細節：同一批檔案、同程式版本
- 所需資源：碼表/日誌
- 預估時間：0.25 天

2. 收集與對比
- 實作細節：輸出時間、CPU 曲線截圖
- 所需資源：Perfmon 或第三方工具
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
var sw = Stopwatch.StartNew();
// 執行整批轉檔...
sw.Stop();
Log.Info($"Total: {sw.Elapsed.TotalSeconds:F1} sec");
```

實測數據：
改善前：內建 ThreadPool＝110 秒（UI 回應差）
改善後：SimpleThreadPool＝90 秒（每張完成即顯示）
改善幅度：縮短約 18%，體感大幅提升

Learning Points（學習要點）
核心知識點：
- 基準測試的重要性
- 同資料集、同環境原則
- 量化與質化指標並重

技能要求：
- 必備技能：量測與紀錄
- 進階技能：效能剖析與呈現

延伸思考：
- 自動跑批 + 報告
- 不同硬體環境對比
- 加入誤差與信賴區間

Practice Exercise（練習題）
- 基礎：加入總時間量測（30 分）
- 進階：輸出 CPU 曲線與對比報告（2 小時）
- 專案：打造基準測試儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：量測可重現
- 程式碼品質（30%）：紀錄清晰
- 效能優化（20%）：以數據驅動
- 創新性（10%）：報表自動化

---

## Case #11: ThreadPool 併發對 RAW 無效：診斷與對策

### Problem Statement（問題陳述）
業務場景：對 RAW 任務使用 ThreadPool 併發，CPU 仍 60% 左右，無吞吐提升。
技術挑戰：證實 RAW 任務間存在內部互斥/序列化，並調整策略。
影響範圍：誤以為多執行緒等於快，反而拖慢整體。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. RAW 解碼器內部鎖。
2. 任務間共享資源（codec/IO）。
3. ThreadPool 只會增加搶占與切換。

深層原因：
- 架構層面：未辨識硬限制
- 技術層面：缺測試驗證
- 流程層面：先做再測的反向流程

### Solution Design（解決方案設計）
解決策略：對 RAW 任務改單執行緒高優先權處理；只對 JPEG 用併發；用基準測試證實策略優於盲目併發。

實施步驟：
1. 行為驗證
- 實作細節：RAW=1 vs RAW>1 對比
- 所需資源：計時、CPU 監視
- 預估時間：0.5 天

2. 策略落地
- 實作細節：兩池與優先權
- 所需資源：SimpleThreadPool
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 錯誤示例（避免）：ThreadPool 多開 RAW
ThreadPool.QueueUserWorkItem(_ => DecodeRaw(cr2_1));
ThreadPool.QueueUserWorkItem(_ => DecodeRaw(cr2_2));
// 修正：RAW 僅單執行緒池
rawPool.QueueWorkItem(_ => DecodeRaw(cr2_1), null);
rawPool.QueueWorkItem(_ => DecodeRaw(cr2_2), null);
```

實測數據：
改善前：RAW 多併發無提升，甚至更慢
改善後：RAW 單執行緒 + JPEG 併發＝總時間 90 秒
改善幅度：整體吞吐提升、UI 體驗改善

Learning Points（學習要點）
核心知識點：
- 併發不等於並行
- 共享資源與鎖的影響
- 針對限制制定策略

技能要求：
- 必備技能：併發基礎
- 進階技能：剖析第三方元件行為

延伸思考：
- 動態偵測 RAW 是否可並行
- 以 TryParallel → Fallback 序列化模式
- 記錄策略決策過程以便回溯

Practice Exercise（練習題）
- 基礎：比較 RAW=1/2/3 的效果（30 分）
- 進階：自動 Fallback 機制（2 小時）
- 專案：與不同相機 RAW codec 對比（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：策略可切換
- 程式碼品質（30%）：記錄/報告
- 效能優化（20%）：避免無效併發
- 創新性（10%）：自動偵測

---

## Case #12: JPEG 任務短小：用低優先權多執行緒最大化利用

### Problem Statement（問題陳述）
業務場景：JPEG 解碼/編碼時間短，適合平行。但必須讓出資源給 RAW 與 UI。
技術挑戰：決定 JPEG 的併發度與優先權，達成「吃滿剩餘 CPU」且不干擾 UI。
影響範圍：若優先權過高會搶 UI、過低又浪費 CPU。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. JPEG 任務短小、CPU bound。
2. UI 需優先保護。
3. 與 RAW 需資源共存。

深層原因：
- 架構層面：共存策略未定義
- 技術層面：欠缺優先權配置
- 流程層面：未做併發/體驗平衡測試

### Solution Design（解決方案設計）
解決策略：JPEG 使用 2–4 執行緒，優先權 BelowNormal/Lowest；RAW 設更高優先權；以視覺化監控調整。

實施步驟：
1. JPEG 池配置
- 實作細節：workers=2..4, priority=BelowNormal
- 所需資源：SimpleThreadPool
- 預估時間：0.25 天

2. 體驗與吞吐平衡
- 實作細節：觀察 UI/CPU，迭代調整
- 所需資源：PerfMon
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var jpgPool = new SimpleThreadPool(
    workers: Math.Min(4, Environment.ProcessorCount),
    priority: ThreadPriority.BelowNormal);
```

實測數據：
改善前：JPEG 與 UI 互搶資源
改善後：UI 流暢，JPEG 吃滿剩餘 CPU；整體 90 秒內完成（整體策略貢獻）
改善幅度：體驗穩定、吞吐最佳化

Learning Points（學習要點）
核心知識點：
- 低優先權長期執行的好處
- UI/CPU-bound 共存
- 併發度 vs 優先權

技能要求：
- 必備技能：Thread.Priority
- 進階技能：負載監控與調參

延伸思考：
- 根據使用者互動動態降載
- 前台/背景模式切換
- 限制每秒任務完成率

Practice Exercise（練習題）
- 基礎：調整 JPEG 池優先權（30 分）
- 進階：加上前台/背景模式（2 小時）
- 專案：負載自動調整器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可調可用
- 程式碼品質（30%）：配置清晰
- 效能優化（20%）：UI 穩定
- 創新性（10%）：動態調整

---

## Case #13: 即時預覽更新：每張完成即顯示，優化感知進度

### Problem Statement（問題陳述）
業務場景：使用者需要看到縮圖預覽持續出現，以確認系統正在工作並獲得信心。
技術挑戰：在重 CPU 背景下，仍能每張完成即回 UI 顯示。
影響範圍：若預覽不出現，使用者誤判系統卡住。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 背景優先權過高，UI 無空檔。
2. 未切回 UI 執行緒更新控制項。
3. 預覽載入與編碼未分離。

深層原因：
- 架構層面：缺少「完成即回報」事件流
- 技術層面：Dispatcher 與資料繫結使用不足
- 流程層面：未定義 UX 指標

### Solution Design（解決方案設計）
解決策略：每張轉完即 Raise 完成事件，回 UI 執行緒更新 Image/進度；JPEG 以低優先權執行，保證 UI 可運行。

實施步驟：
1. 完成事件
- 實作細節：ISubmission 完成後觸發 OnItemDone
- 所需資源：事件/委派
- 預估時間：0.25 天

2. UI 更新
- 實作細節：Dispatcher.BeginInvoke 更新圖與列
- 所需資源：WPF
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
void OnItemDone(BitmapSource bmp)
{
    Application.Current.Dispatcher.BeginInvoke(new Action(() =>
    {
        imageBox.Source = bmp; // 立即顯示
        progress.Value++;
    }));
}
```

實測數據：
改善前：預覽長時間不變
改善後：每張完成即顯示（文章描述）
改善幅度：使用者體感顯著提升

Learning Points（學習要點）
核心知識點：
- 完成即回報的 UX 價值
- Dispatcher 與資料繫結
- 背景優先權設計

技能要求：
- 必備技能：WPF 資料繫結與事件
- 進階技能：非同步 UI 模式

延伸思考：
- 批次大時的虛擬化顯示
- 小圖快取策略
- 減少 UI 更新成本

Practice Exercise（練習題）
- 基礎：完成即更新一張圖（30 分）
- 進階：加上完成音效/通知列（2 小時）
- 專案：圖牆視圖 + 虛擬化（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：完成即顯示
- 程式碼品質（30%）：UI 執行緒安全
- 效能優化（20%）：不卡頓
- 創新性（10%）：UX 細節

---

## Case #14: 預覽版平行程式庫風險：先用自製可控方案

### Problem Statement（問題陳述）
業務場景：微軟提供的 parallel library 當時仍為 Community Preview，是否採用有風險。
技術挑戰：在需求急迫與穩定性間取捨。
影響範圍：採用預覽版可能導致發佈後問題與維護負擔。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預覽版 API 可能變動/缺陷。
2. 文件與社群支援不足。
3. 部署與相容性不確定。

深層原因：
- 架構層面：依賴不穩定基礎
- 技術層面：替代方案足以達標
- 流程層面：風險控管不足

### Solution Design（解決方案設計）
解決策略：短期用自製 SimpleThreadPool 達成需求；等 parallel library 穩定後再評估重構，以降低風險、保障交付。

實施步驟：
1. 風險評估
- 實作細節：列風險/影響/對策
- 所需資源：團隊評審
- 預估時間：0.25 天

2. 暫不採用並留重構點
- 實作細節：抽象排程層，日後可替換
- 所需資源：介面抽象
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 以 IJobScheduler 抽象，日後可換成 TPL
public interface IJobScheduler
{
    void Enqueue(Action job);
    void WaitAll();
}
```

實測數據：
改善前：不確定且可能延誤交付
改善後：用自製方案達標（90 秒），後續保留重構彈性
改善幅度：交付風險降低

Learning Points（學習要點）
核心知識點：
- 技術選型與風險管理
- 抽象層的價值
- 漸進式演進策略

技能要求：
- 必備技能：架構抽象
- 進階技能：風險分析

延伸思考：
- 何時切換到 TPL/TaskScheduler？
- 版本/相容性策略
- 拆分與回退機制

Practice Exercise（練習題）
- 基礎：為排程加入抽象介面（30 分）
- 進階：做一個 TPL 版實作（2 小時）
- 專案：可熱插拔的排程層（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：抽象可替換
- 程式碼品質（30%）：介面清晰
- 效能優化（20%）：不退步
- 創新性（10%）：演進策略

---

## Case #15: 小而全的 SimpleThreadPool：百餘行即可落地

### Problem Statement（問題陳述）
業務場景：不想重新發明輪子，但內建 ThreadPool 不符需求；需一套低成本、可維護的自製 ThreadPool。
技術挑戰：在約百餘行代碼內實作固定池、多池、優先權、等待。
影響範圍：若過度複雜將難以維護與導入。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 需求與內建差距（優先權、多池、WaitAll）。
2. 工期有限、不宜引入大型框架。
3. 需快速驗證與上線。

深層原因：
- 架構層面：KISS 原則
- 技術層面：掌握必要而充分的功能
- 流程層面：迭代式完善

### Solution Design（解決方案設計）
解決策略：以最小功能集實作 SimpleThreadPool（固定大小、優先權、Queue、EndPool），介面盡量對齊內建 ThreadPool 以降低代碼改動。

實施步驟：
1. MVP 版（Queue/Worker/End）
- 實作細節：阻塞佇列、優先權、Join
- 所需資源：.NET Thread
- 預估時間：0.5 天

2. 強韌性
- 實作細節：例外捕捉、可重入 End
- 所需資源：日誌
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public class SimpleThreadPool
{
    readonly Queue<Action> _queue = new();
    readonly List<Thread> _workers = new();
    readonly object _lock = new();
    volatile bool _running;

    public SimpleThreadPool(int size, ThreadPriority prio)
    {
        for (int i = 0; i < size; i++)
        {
            var t = new Thread(WorkerLoop) { IsBackground = true, Priority = prio };
            _workers.Add(t);
        }
    }
    public void StartPool(){ _running = true; _workers.ForEach(t => t.Start()); }
    public void QueueWorkItem(WaitCallback cb, object state)
    {
        lock(_lock){ _queue.Enqueue(() => cb(state)); Monitor.Pulse(_lock); }
    }
    // WorkerLoop 與 EndPool 如 Case #4
}
```

實測數據：
改善前：內建 ThreadPool＝110 秒
改善後：SimpleThreadPool＝90 秒；UI 響應顯著提升
改善幅度：18% 總時間縮短

Learning Points（學習要點）
核心知識點：
- 最小可用實作（MVP）
- 對齊既有 API 減少侵入
- 可維護性的取捨

技能要求：
- 必備技能：多執行緒基礎
- 進階技能：API 設計

延伸思考：
- 加入取消/逾時/優先佇列
- 指標蒐集（等待/執行時間）
- 轉換為 TaskScheduler

Practice Exercise（練習題）
- 基礎：完成 MVP 版 SimpleThreadPool（30 分）
- 進階：例外處理與日誌（2 小時）
- 專案：加優先佇列與統計（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：Queue/Start/End
- 程式碼品質（30%）：簡潔穩健
- 效能優化（20%）：低額外開銷
- 創新性（10%）：擴充介面

---

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 8, 10, 12, 13, 14
- 中級（需要一定基礎）
  - Case 1, 2, 3, 5, 6, 7, 9, 11, 15
- 高級（需要深厚經驗）
  - Case 4

2) 按技術領域分類
- 架構設計類
  - Case 1, 4, 6, 7, 9, 14, 15
- 效能優化類
  - Case 2, 3, 6, 7, 9, 10, 11, 12
- 整合開發類
  - Case 1, 2, 5, 6, 13
- 除錯診斷類
  - Case 3, 9, 10, 11
- 安全防護類
  -（本篇無直接涉略）

3) 按學習目標分類
- 概念理解型
  - Case 9, 10, 14
- 技能練習型
  - Case 2, 5, 8, 12, 13, 15
- 問題解決型
  - Case 1, 3, 4, 6, 7, 11
- 創新應用型
  - Case 6, 9, 14, 15

案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 10（以數據理解問題全貌）
  - Case 2（解碼階段縮放核心觀念）
  - Case 12、13（確保 UX 與 CPU 共存）
- 依賴關係：
  - Case 4（自製 ThreadPool）是 Case 5–9、11–12、15 的基礎
  - Case 6（雙池分工）依賴 Case 3（RAW 單執行緒）與 Case 4
  - Case 9（排程優化）依賴 Case 6 與 Case 7（執行緒數最佳化）
- 完整學習路徑建議：
  1) Case 10 → 2 → 12 → 13（建立效能與 UX 直覺）
  2) Case 11 → 3（辨識 RAW 併發限制與對策）
  3) Case 4 → 8 → 7（打造可控排程與正確關閉、最佳執行緒數）
  4) Case 6 → 9（雙池分工與排程優化）
  5) Case 1 → 5（將能力落地為產品級工具與 UI 體驗）
  6) Case 14 → 15（技術選型與小而全的實作取捨）

以上案例均源自文章所述的實際問題、根因、解法與成效，並補充可操作的程式碼與練習，便於教學與實作演練。