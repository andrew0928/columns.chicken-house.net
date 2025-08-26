## Case #1: 以生產線（Pipeline）模式平行化「縮圖→壓縮」相依流程

### Problem Statement（問題陳述）
**業務場景**：批次處理大量 JPG 相片，需先將每張照片產生縮圖，再將所有縮圖統一壓縮成單一 ZIP 檔。兩步驟存在明確的先後相依，且每一步都相對耗 CPU，既要正確性又要在多核心環境下有效加速。
**技術挑戰**：步驟相依導致無法直接水平切分為獨立任務；ZIP 步驟必須等縮圖完成且本身不易切分並行。
**影響範圍**：若仍採單執行緒，CPU 閒置高、吞吐量低、總處理時間過長。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 任務階段存在先後相依，無法獨立併行。
2. 壓縮 ZIP 對輸出流的序列一致性有要求，不易多執行緒分割。
3. 單執行緒使多核心 CPU 資源無法被有效利用。

**深層原因**：
- 架構層面：未採用能讓相依步驟重疊執行的架構（Pipeline）。
- 技術層面：缺少階段間傳遞與同步機制（佇列/事件）。
- 流程層面：仍以同步序列流程思維處理 CPU 密集任務。

### Solution Design（解決方案設計）
**解決策略**：將整體流程拆為兩個連續階段（Stage1 縮圖、Stage2 壓縮），以兩條專屬執行緒與兩個佇列串接，並用事件同步，讓階段重疊執行，提升整體吞吐。

**實施步驟**：
1. 設計 PipeWorkItem（定義 Stage1/Stage2）
- 實作細節：每項工作封裝圖檔路徑，Stage1 產生縮圖中間檔，Stage2 寫入 Zip。
- 所需資源：.NET/C#、檔案 I/O、壓縮庫（ZipOutputStream）。
- 預估時間：1-2 小時

2. 建立 PipeWorkRunner（兩執行緒＋兩佇列＋事件）
- 實作細節：_stage1_queue → Stage1Runner → _stage2_queue → Stage2Runner；ManualResetEvent 通知。
- 所需資源：System.Threading、Queue<T>。
- 預估時間：1-2 小時

3. 驗證效能（與單執行緒對照）
- 實作細節：以 Stopwatch 記錄總時間，觀察 CPU 使用率。
- 所需資源：Stopwatch、工作負載。
- 預估時間：1 小時

**關鍵程式碼/設定**：
```csharp
public class MakeThumbPipeWorkItem : PipeWorkItem
{
    public ZipOutputStream zipos;
    public string SourceImageFile;
    private string temp;

    public override void Stage1()
    {
        temp = Path.ChangeExtension(SourceImageFile, ".temp");
        if (File.Exists(temp)) File.Delete(temp);
        MakeThumb(SourceImageFile, temp, 1600, 1600); // 縮圖輸出為中繼檔
    }

    public override void Stage2()
    {
        var ze = new ZipEntry(Path.GetFileName(Path.ChangeExtension(SourceImageFile, ".PNG")));
        zipos.PutNextEntry(ze);
        var buffer = File.ReadAllBytes(temp);
        zipos.Write(buffer, 0, buffer.Length);
        File.Delete(temp); temp = null;
    }
}
```

實際案例：將資料夾內多張 JPG 以 PipeWorkRunner 串接兩階段處理。
實作環境：Windows Vista x64、Intel Q9300（四核心）、.NET Framework、C#。
實測數據：
- 改善前：單執行緒 251.4 秒，CPU 約 27%
- 改善後：兩階段管線 163.7 秒，CPU 約 43%
- 改善幅度：時間縮短約 1.53 倍，CPU 使用率 +16 個百分點

Learning Points（學習要點）
核心知識點：
- Pipeline 架構可讓相依步驟重疊執行
- 以佇列為輸送帶，事件為同步手段
- CPU-bound 工作需以架構方案而非僅靠 ThreadPool

技能要求：
- 必備技能：C# 執行緒、基礎 I/O、佇列
- 進階技能：並行架構設計、吞吐/延遲思維

延伸思考：
- 此方案可用於影像處理、影音轉檔、ETL 流水線等。
- 限制：序列化資源（如單一輸出流）限制並行度。
- 優化：量測並平衡各階段產能（見 Case #4）。

Practice Exercise（練習題）
- 基礎練習：把單一縮圖流程改為 PipeWorkItem，跑 10 張圖。
- 進階練習：完成 PipeWorkRunner 兩階段併行，打印進度。
- 專案練習：封裝成 CLI 工具，支援輸入/輸出目錄、ZIP 名稱。

Assessment Criteria（評估標準）
- 功能完整性（40%）：兩階段皆正確、ZIP 可解壓
- 程式碼品質（30%）：抽象清晰、例外處理、資源釋放
- 效能優化（20%）：相對單執行緒有顯著縮時
- 創新性（10%）：參數化、擴展性設計（可插拔階段）


## Case #2: 以 Queue + ManualResetEvent 實作「輸送帶＋同步」的兩階段 Runner

### Problem Statement（問題陳述）
**業務場景**：需要讓縮圖與壓縮兩階段在多核心上重疊，但仍要確保資料依序且不丟失；需要一個簡單穩定的執行骨架。
**技術挑戰**：如何傳遞半成品、如何在無工作時讓消費者阻塞而非忙等、如何優雅結束。
**影響範圍**：若傳遞或同步設計不當，會造成高 CPU 空轉、資料遺失或無法終止。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺少兩階段間的安全交換區。
2. 消費者無法判定何時等待/醒來。
3. 結束條件不明確，可能永遠等待。

**深層原因**：
- 架構層面：尚未建立「生產者-消費者」的模式。
- 技術層面：未運用事件同步和佇列傳遞。
- 流程層面：缺少啟停與邊界條件處理。

### Solution Design（解決方案設計）
**解決策略**：為每階段建立 Queue 作為輸送帶；以 ManualResetEvent 通知下一階段有工作；以執行緒專責各階段，並在無工作時阻塞等待。

**實施步驟**：
1. 建立兩個 Queue 與兩個 Runner 執行緒
- 實作細節：Stage1Runner 出隊→Stage1→入隊 Stage2；Stage2Runner 等待事件/出隊→Stage2。
- 所需資源：Queue<T>、Thread。
- 預估時間：1 小時

2. 加入 ManualResetEvent 同步
- 實作細節：Stage1 完成一次 Set 通知；Stage2 WaitOne 等待。
- 所需資源：ManualResetEvent。
- 預估時間：0.5 小時

3. 處理結束條件
- 實作細節：當 Stage1 執行緒完成且 Stage2 佇列清空時跳出。
- 所需資源：Thread.Join / IsAlive。
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
private Queue<PipeWorkItem> _stage1_queue = new();
private Queue<PipeWorkItem> _stage2_queue = new();
private ManualResetEvent _notify_stage2 = new(false);

private void Stage1Runner()
{
    while (_stage1_queue.Count > 0)
    {
        var pwi = _stage1_queue.Dequeue();
        pwi.Stage1();
        _stage2_queue.Enqueue(pwi);
        _notify_stage2.Set(); // 通知 Stage2 有新工作
    }
}

private void Stage2Runner()
{
    while (true)
    {
        while (_stage2_queue.Count > 0)
        {
            var pwi = _stage2_queue.Dequeue();
            pwi.Stage2();
        }
        if (_stage1_thread.IsAlive == false) break; // 優雅結束
        _notify_stage2.WaitOne(); // 無工作即阻塞
    }
}
```

實際案例：作為 Case #1 成效基礎骨架。
實作環境：同 Case #1。
實測數據：
- 改善前：單執行緒 251.4 秒
- 改善後：兩階段管線骨架 163.7 秒
- 改善幅度：1.53 倍（吞吐提升來自階段重疊）

Learning Points（學習要點）
核心知識點：
- 兩階段生產者-消費者模式
- ManualResetEvent 與阻塞等待
- 輸送帶（Queue）在流水線中的角色

技能要求：
- 必備技能：Thread/Queue/事件
- 進階技能：邏輯邊界與結束條件處理

延伸思考：
- 可替換為 BlockingCollection 實作（新版 .NET）
- 風險：事件誤用導致假喚醒/漏喚醒
- 優化：批量喚醒/合併訊號

Practice Exercise（練習題）
- 基礎：以 Queue + 事件做簡單兩階段字串處理。
- 進階：加入錯誤處理與重試策略。
- 專案：抽象多階段流水線框架，支援 N 階段。

Assessment Criteria（評估標準）
- 功能完整性：正確傳遞與終止
- 程式碼品質：同步點正確、無競態
- 效能優化：Wait/Set 行為不忙等
- 創新性：可重用骨架與配置化


## Case #3: 抽象單筆工作為 PipeWorkItem，清楚切出 Stage1/Stage2

### Problem Statement（問題陳述）
**業務場景**：每張照片需先縮圖再壓縮，若無清楚的抽象，階段難以替換、測試與維護；需求可能擴充新階段（如浮水印）。
**技術挑戰**：混雜實作讓重複利用性低，無法快速插拔或平衡階段。
**影響範圍**：維護成本高、擴展困難、效能調校受阻。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏明確的工作單位抽象。
2. 階段責任不清導致耦合。
3. 測試不易，難以分階段度量。

**深層原因**：
- 架構層面：沒有策略模式或模板方法支撐。
- 技術層面：缺乏可擴充的接口/基類。
- 流程層面：無法單元化測試各步。

### Solution Design（解決方案設計）
**解決策略**：以基類 PipeWorkItem 定義 Stage1/Stage2 虛擬方法，讓每種資料單元以類別實作，達到階段清楚、測試明確、替換容易。

**實施步驟**：
1. 建立 PipeWorkItem 抽象
- 實作細節：定義 Stage1/Stage2 方法。
- 所需資源：C# 繼承/多型。
- 預估時間：0.5 小時

2. 以具體類別實作縮圖/壓縮
- 實作細節：MakeThumb 與 ZipEntry。
- 所需資源：I/O、壓縮。
- 預估時間：1 小時

3. 撰寫單元測試
- 實作細節：分別測 Stage1/Stage2。
- 所需資源：測試框架。
- 預估時間：1 小時

**關鍵程式碼/設定**：
```csharp
public abstract class PipeWorkItem
{
    public abstract void Stage1(); // e.g., 產生縮圖中繼檔
    public abstract void Stage2(); // e.g., 寫入 ZipOutputStream
}
```

實際案例：MakeThumbPipeWorkItem 實作兩階段（見 Case #1 程式碼）。
實作環境：同 Case #1。
實測數據：
- 改善前：整體流程耦合，難以量測/優化（不可量化）
- 改善後：能清楚插拔、重用與量測；與管線化結合帶來 1.53 倍加速
- 改善幅度：可觀測性從 0 到可度量（支撐後續優化）

Learning Points（學習要點）
核心知識點：
- 模板方法/策略的實用抽象
- 單一責任原則
- 可測試性與可維護性對效能調校的價值

技能要求：
- 必備技能：OOP 基礎、抽象設計
- 進階技能：測試設計、接口演進

延伸思考：
- 可將 Stage 拓展為 N 階段
- 風險：抽象過度導致額外成本
- 優化：以 DI 注入資源（如 ZipOutputStream）

Practice Exercise（練習題）
- 基礎：為簡單文本處理定義兩階段 PipeWorkItem。
- 進階：新增第三階段（如額外轉檔）。
- 專案：建立通用 Pipeline SDK（支援插件式階段）。

Assessment Criteria（評估標準）
- 功能完整性：抽象可支撐需求
- 程式碼品質：低耦合、高內聚
- 效能優化：支援分階段量測
- 創新性：擴充性設計


## Case #4: 以 Stopwatch 量測 Stage2 閒置時間，定位產能瓶頸

### Problem Statement（問題陳述）
**業務場景**：導入管線後速度未如預期（未達 2 倍），需診斷哪個階段拖慢整體吞吐，避免盲目調整。
**技術挑戰**：缺少可觀測性，無法精確判斷閒置/忙碌分佈。
**影響範圍**：優化方向錯誤、時間浪費、可能造成反效果。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未記錄閒置時間。
2. 無法判定 Stage1/Stage2 何者為瓶頸。
3. 缺少數據支撐調整決策。

**深層原因**：
- 架構層面：管線缺乏度量點。
- 技術層面：未利用 Stopwatch/計時器。
- 流程層面：未建立效能觀測流程。

### Solution Design（解決方案設計）
**解決策略**：在 Stage2 WaitOne 前後用 Stopwatch 量測閒置時間，輸出 log 分析，據以判斷產能不均並制定平衡策略。

**實施步驟**：
1. 插入量測碼
- 實作細節：Reset/Start → WaitOne → Reset → Console.WriteLine。
- 所需資源：Stopwatch。
- 預估時間：0.5 小時

2. 蒐集樣本與計算平均/分佈
- 實作細節：彙整多筆 Idle msec。
- 所需資源：簡易統計。
- 預估時間：0.5 小時

3. 擬定調整策略（見 Case #5）
- 實作細節：決定增加 Stage1 工作者數。
- 所需資源：執行緒控制。
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
idle_timer.Reset();
idle_timer.Start();
_notify_stage2.WaitOne();
_notify_stage2.Reset(); // 為了量測下一次 idle
Console.WriteLine($"Stage 2: Idle {idle_timer.ElapsedMilliseconds} msec");
```

實際案例：記錄多次閒置 389–441 msec。
實作環境：同上。
實測數據：
- 改善前：不可觀測
- 改善後：Stage2 每次閒置約 389–441 ms（顯示 Stage1 較慢）
- 改善幅度：可觀測性 +100%，為後續調整提供依據

Learning Points（學習要點）
核心知識點：
- 效能優化先度量再調整
- Wait/Signal 與 idle 時間的關聯
- 數據驅動的平衡策略

技能要求：
- 必備技能：Stopwatch 使用
- 進階技能：簡單統計分析

延伸思考：
- 可量測各階段處理時間分佈
- 限制：僅觀測到 Stage2 idle，非全貌
- 優化：加入 Stage1 耗時統計

Practice Exercise（練習題）
- 基礎：在 WaitOne 周邊量測 idle。
- 進階：輸出 CSV 並畫出分佈。
- 專案：建立統一觀測模組（事件、耗時、佇列長度）。

Assessment Criteria（評估標準）
- 功能完整性：正確輸出 idle 統計
- 程式碼品質：低侵入、易移除
- 效能優化：能支撐正確決策
- 創新性：可擴充觀測點


## Case #5: 增加 Stage1 工作者數（從 1 → 2），平衡產能提升吞吐

### Problem Statement（問題陳述）
**業務場景**：量測顯示 Stage2 經常閒置約 400ms，代表 Stage1 供料不足；需要透過增加並行度加快 Stage1。
**技術挑戰**：增加執行緒後的同步與資料正確性，避免競態與死鎖。
**影響範圍**：若不平衡，Stage2 閒置或佇列爆量；總時間與 CPU 使用率受影響。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 單一 Stage1 執行緒產能不足。
2. Stage2 處理較快，導致 idle。
3. 未依 CPU 核數調整工作者數。

**深層原因**：
- 架構層面：固定 1:1 工作者配置。
- 技術層面：缺少安全的多生產者存取。
- 流程層面：未建立容量規劃與調參流程。

### Solution Design（解決方案設計）
**解決策略**：將 Stage1 工作者增加為 2 條執行緒；以 lock 保護 _stage1_queue 出隊；維持 Stage2 單工以確保 Zip 正確性。

**實施步驟**：
1. 建立第二條 Stage1Runner
- 實作細節：新增 Thread 指向同一 Runner。
- 所需資源：Thread API。
- 預估時間：0.5 小時

2. 加上 lock 確保佇列安全
- 實作細節：出隊前 lock(_stage1_queue)。
- 所需資源：lock 語法。
- 預估時間：0.5 小時

3. 驗證效能與 Stage2 閒置
- 實作細節：重跑 Case #4 量測。
- 所需資源：Stopwatch。
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
private Thread _stage1_thread1, _stage1_thread2, _stage2_thread;

private void Stage1Runner()
{
    while (true)
    {
        PipeWorkItem pwi = null;
        lock (_stage1_queue)
        {
            if (_stage1_queue.Count > 0) pwi = _stage1_queue.Dequeue();
        }
        if (pwi == null) break;

        pwi.Stage1();

        _stage2_queue.Enqueue(pwi); // 需保證單一消費者時安全
        _notify_stage2.Set();
    }
}
```

實際案例：將 Stage1 從 1 工作者提升為 2。
實作環境：同上。
實測數據：
- 改善前：163.7 秒，CPU 約 43%，Stage2 idle 約 400ms
- 改善後：98.8 秒，CPU 約 75–78%，Stage2 idle < 100ms
- 改善幅度：時間再縮短約 1.66 倍，CPU 使用率 +32–35 個百分點

Learning Points（學習要點）
核心知識點：
- 以 DoP（Degree of Parallelism）平衡階段
- 競態條件與臨界區保護
- 以量測數據驗證調整成效

技能要求：
- 必備技能：執行緒同步、lock
- 進階技能：容量規劃、瓶頸分析

延伸思考：
- 是否可改為動態調整工者數？
- 風險：過度並行導致 Stage2 無 CPU
- 優化：用工作佇列 + ThreadPool 限流（見 Case #12）

Practice Exercise（練習題）
- 基礎：將 Stage1 工作者數改為 2，確保正確。
- 進階：引入參數化工者數（讀取設定）。
- 專案：實作自動調參（依 idle 或佇列長度）。

Assessment Criteria（評估標準）
- 功能完整性：無資料遺失、ZIP 正確
- 程式碼品質：同步正確、無死鎖
- 效能優化：縮時與 CPU 提升明顯
- 創新性：動態調整策略


## Case #6: 使用 lock 確保多工者下佇列操作 Thread-Safe

### Problem Statement（問題陳述）
**業務場景**：Stage1 增至 2 條執行緒後同時存取 _stage1_queue；需確保不會取重、不會漏資料、無例外。
**技術挑戰**：Queue<T> 非 thread-safe；多執行緒 Dequeue 容易產生競態。
**影響範圍**：資料錯誤、壓縮檔遺漏、程式崩潰。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 使用非 thread-safe 容器。
2. 多執行緒同時出隊/入隊。
3. 無臨界區保護。

**深層原因**：
- 架構層面：缺少併發容器設計。
- 技術層面：忽略容器的 thread-safe 特性。
- 流程層面：未針對並行重構做風險評估。

### Solution Design（解決方案設計）
**解決策略**：以 lock 保護 _stage1_queue 出隊；單一 Stage2Runner 消費使 _stage2_queue 可不加鎖（或同樣以 lock 保守保護）。

**實施步驟**：
1. 將 Dequeue 包在 lock 中
- 實作細節：lock(_stage1_queue){ ... }
- 所需資源：C# lock。
- 預估時間：0.2 小時

2. 視需求保護 _stage2_queue
- 實作細節：單一消費者可放行，或加 lock 嚴謹保護。
- 所需資源：lock。
- 預估時間：0.2 小時

3. 壓力測試
- 實作細節：大量檔案、多次跑。
- 所需資源：測試資料。
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
lock (_stage1_queue)
{
    if (_stage1_queue.Count > 0) pwi = _stage1_queue.Dequeue();
}
// 產生者數多時，對 _stage2_queue.Enqueue(pwi) 視需求加 lock
```

實際案例：搭配 Case #5 調整產能。
實作環境：同上。
實測數據：
- 改善前：存在競態風險（不可量化）
- 改善後：穩定完成，總時間 98.8 秒（與 Case #5 一致）
- 改善幅度：正確性與穩定性提升（無異常）

Learning Points（學習要點）
核心知識點：
- 非 thread-safe 容器在多工者下的風險
- 最小鎖範圍與效能平衡
- 消費者單執行緒的設計折衷

技能要求：
- 必備技能：lock/臨界區
- 進階技能：併發容器替代（BlockingCollection）

延伸思考：
- 改用 ConcurrentQueue？
- 風險：過度上鎖造成瓶頸
- 優化：縮小鎖範圍或用 lock-free 容器

Practice Exercise（練習題）
- 基礎：為 Dequeue 加鎖並驗證正確。
- 進階：引入 ConcurrentQueue 重構。
- 專案：做 10 萬筆壓力測試與錯誤率統計。

Assessment Criteria（評估標準）
- 功能完整性：零重複/零遺失
- 程式碼品質：鎖範圍合理
- 效能優化：避免鎖競爭過高
- 創新性：容器替代方案


## Case #7: 正確啟停：IsAlive 與 Join 防止 Stage2 無限等待

### Problem Statement（問題陳述）
**業務場景**：當全部工作處理完後，Stage2 可能仍在等待事件而無限阻塞，需正確結束整體流程並收攏資源。
**技術挑戰**：判斷何時沒有後續工作且可安全退出；避免假喚醒或提前中止。
**影響範圍**：程式不退出、資源未釋放、ZIP 不完整。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Stage2 單靠 WaitOne 不知何時真正結束。
2. 無明確結束訊號或檢查。
3. 主執行緒可能過早結束未 Join。

**深層原因**：
- 架構層面：缺乏終止協議。
- 技術層面：未使用 IsAlive/Join。
- 流程層面：不足的收尾流程。

### Solution Design（解決方案設計）
**解決策略**：Stage2 在佇列空時檢查 Stage1 執行緒 IsAlive，若已結束則跳出回圈；主執行緒呼叫 Join 等待兩執行緒完成。

**實施步驟**：
1. Stage2Runner 中加入 IsAlive 檢查
- 實作細節：佇列空、Stage1 不在生存 → break。
- 預估時間：0.2 小時

2. 主執行緒 Join
- 實作細節：Start 後 Join 等待。
- 預估時間：0.2 小時

3. 收尾釋放 Zip 流
- 實作細節：Flush/Close。
- 預估時間：0.2 小時

**關鍵程式碼/設定**：
```csharp
if (_stage1_thread.IsAlive == false) break; // Stage2 優雅退出
// 主執行緒
_stage1_thread.Join();
_stage2_thread.Join();
```

實際案例：穩定產生完整 ZIP。
實作環境：同上。
實測數據：
- 改善前：可能卡住或提前結束（不可量化）
- 改善後：穩定在 98.8 秒內完成並正確退出
- 改善幅度：健壯性顯著提升

Learning Points（學習要點）
核心知識點：
- 終止協議與條件判斷
- Join 的重要性
- 事件同步與結束條件互動

技能要求：
- 必備技能：Thread 狀態與 Join
- 進階技能：通用終止訊號（Poison Pill）

延伸思考：
- 可改以哨兵物件（Poison Pill）通知結束
- 風險：錯誤判定導致提前退出
- 優化：雙重條件（Stage1 停止且 Stage2 空列）

Practice Exercise（練習題）
- 基礎：加入 IsAlive 檢查並驗證退出。
- 進階：改用 Poison Pill 實作終止。
- 專案：往 N 階段推廣終止協議。

Assessment Criteria（評估標準）
- 功能完整性：不阻塞、不提早退出
- 程式碼品質：條件清晰
- 效能優化：無多餘等待
- 創新性：普適性終止設計


## Case #8: 事件喚醒取代忙等，降低空轉與無效 CPU 消耗

### Problem Statement（問題陳述）
**業務場景**：消費者階段（Stage2）在無工作時，若採輪詢會造成高 CPU 空轉；需在有工作時才喚醒。
**技術挑戰**：正確使用事件避免漏喚醒與假喚醒；避免以 sleep 輪詢。
**影響範圍**：CPU 使用率偏高、能源浪費、效能不穩。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 輪詢/睡眠策略造成 CPU 不必要消耗。
2. 無法即時對工作到來做出反應。
3. 喚醒時機掌握不佳。

**深層原因**：
- 架構層面：缺少阻塞式等待。
- 技術層面：未運用 ManualResetEvent。
- 流程層面：缺少事件驅動思維。

### Solution Design（解決方案設計）
**解決策略**：Stage1 完成一次就 Set 事件；Stage2 無工作時 WaitOne 阻塞，有工作時被喚醒立即處理，避免忙等。

**實施步驟**：
1. Stage1 Set 事件
- 實作細節：入隊後呼叫 _notify_stage2.Set()。
- 預估時間：0.2 小時

2. Stage2 WaitOne
- 實作細節：佇列空時等待事件。
- 預估時間：0.2 小時

3. 測試喚醒準確性
- 實作細節：壓力與邊界測試。
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
// Stage1: 完成一筆入隊後
_stage2_queue.Enqueue(pwi);
_notify_stage2.Set();

// Stage2: 無工作時
if (_stage2_queue.Count == 0) _notify_stage2.WaitOne();
```

實際案例：結合 Case #2/#5 的骨架。
實作環境：同上。
實測數據：
- 改善前：理論上輪詢會推高 CPU（未實作）
- 改善後：整體 CPU 使用率於兩階段/平衡後為 43% → 75–78%（反映有效工作佔比提升）
- 改善幅度：避免空轉，CPU 有效工作佔比增加

Learning Points（學習要點）
核心知識點：
- Wait/Set 的正確使用
- 事件與阻塞式等待對效能的影響
- ManualResetEvent vs AutoResetEvent 選擇

技能要求：
- 必備技能：事件同步
- 進階技能：多事件/條件變數

延伸思考：
- 單事件對 burst 的適用性
- 風險：錯誤 Reset 造成長期阻塞
- 優化：AutoResetEvent/信號量/條件變數替代

Practice Exercise（練習題）
- 基礎：從 sleep 輪詢改為事件等待。
- 進階：比較兩者 CPU 使用率差異。
- 專案：事件驅動的多階段管線 Demo。

Assessment Criteria（評估標準）
- 功能完整性：不漏喚醒、不忙等
- 程式碼品質：事件生命週期清晰
- 效能優化：有效降低空轉
- 創新性：事件策略設計


## Case #9: 保持 ZipOutputStream 單執行緒，確保壓縮序與正確性

### Problem Statement（問題陳述）
**業務場景**：ZIP 壓縮階段需串流寫入，並維持 entry 順序與完整性；多執行緒寫入會破壞壓縮檔。
**技術挑戰**：如何在不破壞壓縮正確性的前提下提升整體效能。
**影響範圍**：壓縮檔損毀、資料遺失、不可解壓。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. ZipOutputStream 非 thread-safe。
2. ZIP 檔案格式對 entry/central directory 有嚴格要求。
3. 並行寫入會競爭同一輸出流。

**深層原因**：
- 架構層面：序列化資源造成全域瓶頸。
- 技術層面：對壓縮格式限制認知不足。
- 流程層面：一味增加執行緒易出錯。

### Solution Design（解決方案設計）
**解決策略**：維持 Stage2 單執行緒負責 ZipOutputStream 寫入；將並行優化重點放在 Stage1，透過產能平衡來提升整體吞吐。

**實施步驟**：
1. 確認壓縮 API 限制
- 實作細節：檢視 ZipOutputStream 文件。
- 預估時間：0.2 小時

2. 固定 Stage2 單工
- 實作細節：Stage2Runner 單一執行緒。
- 預估時間：0.2 小時

3. 調高 Stage1 產能（見 Case #5）
- 實作細節：增加 Stage1 工作者數。
- 預估時間：依 Case #5

**關鍵程式碼/設定**：
```csharp
// 單一 Stage2Runner 負責序列化寫 Zip
var ze = new ZipEntry(Path.GetFileName(Path.ChangeExtension(SourceImageFile, ".PNG")));
zipos.PutNextEntry(ze);
zipos.Write(buffer, 0, buffer.Length);
```

實際案例：最終版本維持 Stage2 單工。
實作環境：同上。
實測數據：
- 改善前：若嘗試並行寫入，風險高（未測）
- 改善後：以 Stage1 並行拉滿 CPU 至 75–78%，總時間 98.8 秒，且 ZIP 正確
- 改善幅度：在正確性的前提下達成最大吞吐

Learning Points（學習要點）
核心知識點：
- 序列化共享資源的並行設計
- 將並行度配置在可伸縮的階段
- 正確性優先的效能思維

技能要求：
- 必備技能：I/O 串流、壓縮格式
- 進階技能：架構取捨與風險控管

延伸思考：
- 可否先行分檔平行壓縮、最後合併？（不同需求）
- 風險：合併策略複雜
- 優化：分批寫入、壓縮等級調整

Practice Exercise（練習題）
- 基礎：將 Stage2 維持單工並驗證 ZIP 正確。
- 進階：調整 Stage1 工者數觀察吞吐。
- 專案：比較單 ZIP 與多分片 ZIP 的策略。

Assessment Criteria（評估標準）
- 功能完整性：ZIP 可正確解壓
- 程式碼品質：串流管理正確
- 效能優化：在限制下達最大吞吐
- 創新性：策略比較能力


## Case #10: 生產線步驟切割與啟停成本評估

### Problem Statement（問題陳述）
**業務場景**：盲目增加階段數可能提高啟動/結束成本（前段等待供料、後段無事可做），需評估步驟切割粒度。
**技術挑戰**：決定階段數量與單階段工作量，平衡吞吐與成本。
**影響範圍**：過多階段造成效益遞減，甚至反向影響效能。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 啟動期後段閒置、結束期前段閒置。
2. 過多執行緒導致排程與切換成本。
3. CPU 已滿載時新增階段無效。

**深層原因**：
- 架構層面：錯誤的粒度選擇。
- 技術層面：忽略排程/快取/同步成本。
- 流程層面：未評估工作量與產品數關係。

### Solution Design（解決方案設計）
**解決策略**：先以兩階段建立明顯收益，再依量測（閒置、吞吐、CPU）調整；避免過度細分階段，確保有足夠產品數攤平啟停成本。

**實施步驟**：
1. 建立基線兩階段（見 Case #1）
2. 量測閒置/吞吐（見 Case #4）
3. 規劃 DoP 與階段數（見 Case #5）

**關鍵程式碼/設定**：
```csharp
// 留意不要無限制拆階段與加線程；以量測結果決定 DoP
// 建議：先 2 階段，平衡產能再談升階
```

實際案例：兩階段即帶來 1.53 倍提升；升級 DoP 再到 98.8 秒。
實作環境：同上。
實測數據：
- 改善前：單執行緒 251.4 秒
- 改善後：兩階段 163.7 秒 → 平衡後 98.8 秒
- 改善幅度：兩次優化疊加達約 2.54 倍

Learning Points（學習要點）
核心知識點：
- Pipeline 填充/清空成本
- 粒度選擇與排程成本
- 以數據驅動的階段設計

技能要求：
- 必備技能：效能分析
- 進階技能：容量規劃、Amdahl 定律思維

延伸思考：
- 多階段是否引入佇列放大（背壓）？
- 風險：過細粒度導致同步成本壓過收益
- 優化：設定最小批量尺寸

Practice Exercise（練習題）
- 基礎：比較 2 階段 vs 3 階段（虛擬分拆）時間。
- 進階：繪出填充/清空時間區塊圖。
- 專案：做階段粒度/DoP 掃描自動化實驗。

Assessment Criteria（評估標準）
- 功能完整性：能完成比較
- 程式碼品質：量測方法正確
- 效能優化：提出數據支撐決策
- 創新性：可視化與自動化


## Case #11: 以 Reset/WaitOne 取得準確 idle 量測並驗證優化成效

### Problem Statement（問題陳述）
**業務場景**：需要客觀比較優化前後的 Stage2 閒置時間變化，以確認是否有效消除瓶頸。
**技術挑戰**：避免重複計入喚醒期間，確保 idle 計時區間準確。
**影響範圍**：若量測不準，優化決策失真。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 事件狀態未重置導致下次 WaitOne 立即回復。
2. 計時區間未正確包覆等待段。
3. 樣本數不足。

**深層原因**：
- 架構層面：缺少標準量測介面。
- 技術層面：事件/計時配合錯誤。
- 流程層面：缺少前後對照。

### Solution Design（解決方案設計）
**解決策略**：WaitOne 後立即 Reset 事件供下次量測；收集多筆樣本，比較 DoP 調整前後閒置分佈。

**實施步驟**：
1. 插入 Reset
2. 收集 N 筆樣本
3. 比較優化前後（DoP=1 vs DoP=2）

**關鍵程式碼/設定**：
```csharp
idle_timer.Reset();
idle_timer.Start();
_notify_stage2.WaitOne();
_notify_stage2.Reset(); // 確保下次真的等待
Console.WriteLine($"Idle {idle_timer.ElapsedMilliseconds} ms");
```

實際案例：DoP=1 時 389–441 ms；DoP=2 後 <100 ms。
實作環境：同上。
實測數據：
- 改善前：Idle 約 389–441 ms/次
- 改善後：Idle < 100 ms/次
- 改善幅度：閒置縮短 ~74% 以上（粗估）

Learning Points（學習要點）
核心知識點：
- 事件與計時器配合
- 成效驗證需前後對照
- 以 idle 指標輔助 DoP 選擇

技能要求：
- 必備技能：Stopwatch/事件
- 進階技能：統計分析

延伸思考：
- 擴展量測至 Stage1/佇列長度
- 風險：樣本偏誤
- 優化：長期監控與異常偵測

Practice Exercise（練習題）
- 基礎：加入 Reset 增進量測準確度。
- 進階：繪 idle CDF 並比較前後。
- 專案：建立效能儀錶板模組。

Assessment Criteria（評估標準）
- 功能完整性：量測合理
- 程式碼品質：非侵入可拔除
- 效能優化：支撐 DoP 決策
- 創新性：可視化分析


## Case #12: 避免過度平行化（ThreadPool）造成產能不均與搶占

### Problem Statement（問題陳述）
**業務場景**：直覺用 ThreadPool 將 Stage1 開很多工者，但可能搶占 Stage2 CPU，導致整體吞吐下降或不穩。
**技術挑戰**：控制 Stage1 佔用的 CPU 比例，避免壓制序列化瓶頸階段。
**影響範圍**：Stage2 得不到 CPU、佇列淤積、延遲上升。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 超過 CPU 核數的工者數。
2. ThreadPool 自動擴張不可控。
3. 未限制最大並行度。

**深層原因**：
- 架構層面：缺少整體資源分配策略。
- 技術層面：對 ThreadPool 行為認知不足。
- 流程層面：未以量測作為調參依據。

### Solution Design（解決方案設計）
**解決策略**：若採 ThreadPool，需搭配並行度上限（如 SemaphoreSlim）；或維持固定數目手動執行緒。依 Idle/CPU/時間數據調整。

**實施步驟**：
1. 設定最大並行度（建議 ≤ 核心數-1）
2. 觀測 Stage2 idle 與總時間（見 Case #4/#11）
3. 調整至 CPU 約 70–80% 且 Stage2 idle 接近 0

**關鍵程式碼/設定**：
```csharp
// 範例：以 SemaphoreSlim 限制 ThreadPool 工作數
SemaphoreSlim limiter = new(Environment.ProcessorCount - 1);
await limiter.WaitAsync();
try { /* queue Stage1 work */ }
finally { limiter.Release(); }
```

實際案例：最終以固定 2 工者達到 98.8 秒、CPU 75–78%。
實作環境：同上。
實測數據：
- 改善前：可能 oversubscription（未測）
- 改善後：受控並行度 → 98.8 秒、CPU 75–78%
- 改善幅度：穩定性與吞吐最佳化

Learning Points（學習要點）
核心知識點：
- Oversubscription 的危害
- 受控並行度的重要性
- 以數據閉環調參

技能要求：
- 必備技能：ThreadPool 行為
- 進階技能：限流/背壓設計

延伸思考：
- 動態調整並行度的控制回路
- 風險：下降太多導致 CPU 閒置
- 優化：基於 idle 的自調平衡

Practice Exercise（練習題）
- 基礎：新增簡單並行度限制。
- 進階：建立自動調參（基於 idle）。
- 專案：ThreadPool 版 Pipeline 實作與調參工具。

Assessment Criteria（評估標準）
- 功能完整性：限制生效
- 程式碼品質：無資源外漏
- 效能優化：達到穩定最佳點
- 創新性：自動調參策略


## Case #13: 使用臨時檔作為中繼成果，解耦 I/O 與壓縮階段

### Problem Statement（問題陳述）
**業務場景**：縮圖結果需傳遞給壓縮階段；直接以記憶體傳遞可能造成高記憶體壓力，檔案亦需正確清理。
**技術挑戰**：設計中繼格式、命名與清除策略，避免殘留。
**影響範圍**：記憶體峰值過高、磁碟垃圾檔、壓縮錯誤。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 大檔案以記憶體傳遞風險高。
2. 臨時檔未清理可能污染結果。
3. 命名不一致導致壓縮 entry 錯亂。

**深層原因**：
- 架構層面：缺少明確中繼協議。
- 技術層面：臨時檔生命週期管理不足。
- 流程層面：缺少清理步驟。

### Solution Design（解決方案設計）
**解決策略**：Stage1 將縮圖輸出至 .temp 檔，Stage2 讀取後寫入 Zip 並刪除 temp；以 Path.ChangeExtension 與 GetFileName 保持一致命名。

**實施步驟**：
1. 臨時檔命名與覆蓋策略
2. Stage2 讀取後刪除
3. 例外時的清理（finally）

**關鍵程式碼/設定**：
```csharp
temp = Path.ChangeExtension(SourceImageFile, ".temp");
if (File.Exists(temp)) File.Delete(temp); // 避免殘留
MakeThumb(SourceImageFile, temp, 1600, 1600);
var ze = new ZipEntry(Path.GetFileName(Path.ChangeExtension(SourceImageFile, ".PNG")));
```

實際案例：穩定產生 ZIP，無 temp 殘留。
實作環境：同上。
實測數據：
- 改善前：可能殘留/不一致（不可量化）
- 改善後：穩定完成，總時間達 98.8 秒（不影響吞吐）
- 改善幅度：穩定性提高

Learning Points（學習要點）
核心知識點：
- 中繼層解耦
- 檔案命名與資源清理
- 功能正確性優先

技能要求：
- 必備技能：I/O 操作
- 進階技能：例外處理與恢復

延伸思考：
- 可改為記憶體串流＋池化
- 風險：池化實作複雜
- 優化：使用 using/try-finally 清理

Practice Exercise（練習題）
- 基礎：以 temp 中繼並正確清理。
- 進階：加入錯誤注入測試清理路徑。
- 專案：替換為 MemoryStream ＋緩衝池。

Assessment Criteria（評估標準）
- 功能完整性：無殘留、ZIP 正確
- 程式碼品質：清理可靠
- 效能優化：控制記憶體峰值
- 創新性：資源管理策略


## Case #14: 以檔名與副檔名規範確保壓縮內條目清晰一致

### Problem Statement（問題陳述）
**業務場景**：ZIP 內需以 PNG 命名條目，防止重名或副檔名錯誤導致使用端混淆。
**技術挑戰**：在不同來源檔名下統一條目命名，並確保只包含檔名不含目錄。
**影響範圍**：ZIP 可用性與可讀性、後續處理正確性。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 來源 JPG 與輸出 PNG 副檔名不同。
2. 若寫入全路徑，ZIP 條目結構混亂。
3. 重名檔風險。

**深層原因**：
- 架構層面：命名規範缺失。
- 技術層面：未使用 Path API 正確切割。
- 流程層面：缺乏檔名正規化。

### Solution Design（解決方案設計）
**解決策略**：使用 Path.ChangeExtension 和 Path.GetFileName，確保條目為檔名＋.PNG，避免路徑滲入。

**實施步驟**：
1. 轉換副檔名為 .PNG
2. 僅取檔名部分
3. 確保唯一性（必要時加序號）

**關鍵程式碼/設定**：
```csharp
var entryName = Path.GetFileName(Path.ChangeExtension(SourceImageFile, ".PNG"));
zipos.putNextEntry(new ZipEntry(entryName));
```

實際案例：ZIP 條目命名一致。
實作環境：同上。
實測數據：
- 改善前：命名不一致風險（不可量化）
- 改善後：ZIP 條目清晰，總時間 98.8 秒
- 改善幅度：可用性提升

Learning Points（學習要點）
核心知識點：
- 檔名處理 API 的正確使用
- 條目命名對下游流程的影響

技能要求：
- 必備技能：Path API
- 進階技能：唯一性處理

延伸思考：
- 條目加入中繼資料（EXIF）？
- 風險：命名衝突處理
- 優化：規範化命名策略文件

Practice Exercise（練習題）
- 基礎：正確命名條目。
- 進階：處理同名檔。
- 專案：設計命名規範與檢核工具。

Assessment Criteria（評估標準）
- 功能完整性：命名一致
- 程式碼品質：處理周全
- 效能優化：無額外負擔
- 創新性：規範化工具


## Case #15: 匯總指標管理：總時間、CPU 使用率、閒置時間的閉環優化

### Problem Statement（問題陳述）
**業務場景**：需要用一致的指標來管理與驗證優化：總時間、CPU 使用率、Stage2 閒置時間，形成可持續改進閉環。
**技術挑戰**：建立可重現的量測流程與對照組，避免偶然性。
**影響範圍**：沒有一致指標將導致優化方向不明、投資回報模糊。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 指標零散或缺失。
2. 量測過程不一致。
3. 缺少對照組。

**深層原因**：
- 架構層面：缺乏觀測性設計。
- 技術層面：未集中輸出統計。
- 流程層面：未建立驗證流程。

### Solution Design（解決方案設計）
**解決策略**：建立三類指標與對照組：總時間（Stopwatch）、CPU 使用率（系統監視）、Stage2 閒置（Case #4 方法）；逐案對照單執行緒、兩階段、平衡後三組。

**實施步驟**：
1. 定義量測腳本/流程
2. 執行三組對照
3. 彙整表格與結論

**關鍵程式碼/設定**：
```csharp
// 總時間
var sw = Stopwatch.StartNew();
// ... run workload ...
sw.Stop();
Console.WriteLine($"Total: {sw.Elapsed.TotalSeconds} s");
// Stage2 idle 量測見 Case #4
```

實際案例：本文三階段結果。
實作環境：同上。
實測數據：
- 單執行緒：251.4 秒，CPU 約 27%
- 兩階段：163.7 秒，CPU 約 43%，Stage2 idle ~400ms
- 平衡後：98.8 秒，CPU 約 75–78%，Stage2 idle < 100ms
- 改善幅度：最終相對基線約 2.54 倍

Learning Points（學習要點）
核心知識點：
- 指標閉環驅動優化
- 多指標權衡（時間/CPU/idle）
- 對照實驗的重要性

技能要求：
- 必備技能：量測、統計
- 進階技能：結果詮釋與決策

延伸思考：
- 加入記憶體與 I/O 指標
- 風險：指標誤導（如只看 CPU）
- 優化：自動報表與回歸測試

Practice Exercise（練習題）
- 基礎：輸出三項指標。
- 進階：建立 CSV 報告。
- 專案：打造效能回歸 CI 任務。

Assessment Criteria（評估標準）
- 功能完整性：三指標齊備
- 程式碼品質：量測穩定
- 效能優化：能支撐決策
- 創新性：自動化程度


## Case #16: 流程正確性與效能的權衡：為序列化瓶頸建模與分配資源

### Problem Statement（問題陳述）
**業務場景**：在存在序列化瓶頸的任務（ZIP）中，如何最大化效能又確保正確性？需建模各階段可伸縮性，集中資源於可擴展段。
**技術挑戰**：識別可擴展與不可擴展步驟；合理分配 CPU。
**影響範圍**：不當分配導致錯誤或效能下降。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未區分序列化（Zip）與可並行（縮圖）步驟。
2. 平均分配資源導致總體不佳。
3. 缺乏模型與量測。

**深層原因**：
- 架構層面：無並行度模型
- 技術層面：未建立「可伸縮/不可伸縮」清單
- 流程層面：未以瓶頸驅動設計

### Solution Design（解決方案設計）
**解決策略**：將 Zip 步驟建模為序列化瓶頸，固定單執行緒；將並行度集中於縮圖（Stage1），以 idle 與 CPU 指標驗證資源分配是否最佳。

**實施步驟**：
1. 標註每階段伸縮性
2. 資源優先分配於可伸縮段
3. 持續量測與校正（Case #15）

**關鍵程式碼/設定**：
```csharp
// 配置：ZipStage.MaxDOP = 1; ThumbStage.MaxDOP = N (依 CPU 調整)
```

實際案例：N=2 達最佳（本環境）→ 98.8 秒、CPU 75–78%。
實作環境：同上。
實測數據：
- 改善前：無模型（不可量化）
- 改善後：以模型分配資源 → 指標最佳（98.8 秒）
- 改善幅度：建立可重用調參方法論

Learning Points（學習要點）
核心知識點：
- 序列化瓶頸建模
- 資源分配與伸縮性
- 以量測閉環驗證

技能要求：
- 必備技能：瓶頸分析
- 進階技能：資源規劃與調度

延伸思考：
- 擴展至更多階段的資源分配
- 風險：環境變動需重校
- 優化：自動建議 DoP

Practice Exercise（練習題）
- 基礎：列出每階段伸縮性。
- 進階：寫簡單配置檔控制 DoP。
- 專案：建立資源分配建議器（依指標給建議）。

Assessment Criteria（評估標準）
- 功能完整性：配置可控
- 程式碼品質：清楚的模型表示
- 效能優化：貼近最佳點
- 創新性：自動建議能力


--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）：Case #3, #6, #7, #8, #13, #14
- 中級（需要一定基礎）：Case #1, #2, #4, #5, #15
- 高級（需要深厚經驗）：Case #10, #11, #12, #16, #9

2. 按技術領域分類
- 架構設計類：Case #1, #2, #3, #10, #16
- 效能優化類：Case #4, #5, #11, #12, #15
- 整合開發類：Case #9, #13, #14
- 除錯診斷類：Case #4, #11, #15
- 安全防護類（正確性/穩定性）：Case #6, #7, #9, #13, #14

3. 按學習目標分類
- 概念理解型：Case #1, #2, #10, #16
- 技能練習型：Case #3, #6, #7, #8, #13, #14
- 問題解決型：Case #4, #5, #11, #12
- 創新應用型：Case #15（指標閉環）、#16（資源分配模型）

--------------------------------
案例關聯圖（學習路徑建議）
- 建議先學：Case #1（整體動機與目標）、#2（Runner 骨架）、#3（PipeWorkItem 抽象）
- 之後學：Case #4（度量 idle，定位瓶頸）→ Case #5（平衡 DoP 提升吞吐）→ Case #6（lock 確保安全）
- 並行補強：Case #7（正確啟停）、#8（事件喚醒避免忙等）、#9（ZIP 正確性）
- 進一步：Case #11（準確量測驗證）、#12（避免過度平行化）、#13（中繼檔解耦）、#14（命名規範）
- 收斂與方法論：Case #10（步驟切割評估）、Case #15（指標閉環）、Case #16（資源分配模型）

依賴關係：
- Case #5 依賴 Case #4 的瓶頸診斷
- Case #6 依賴 Case #5 的多工者設計
- Case #11 依賴 Case #4 的量測基礎
- Case #12 依賴 Case #5（DoP 調整）與 Case #11（指標）
- Case #16 依賴 Case #1/#2（架構）＋ Case #4/#11/#15（數據）

完整學習路徑：
1) #1 → #2 → #3（建構管線基礎）
2) #4 → #5 → #6（診斷與平衡、確保安全）
3) #7 → #8 → #9（正確啟停與序列化資源處理）
4) #11 → #12 → #10（量測、避免過度並行、步驟粒度）
5) #13 → #14 → #15 → #16（工程化整合、指標閉環、模型化資源分配）

完成後，學習者能從零搭起一個可量測、可調參、可擴充且在多核 CPU 上具備實際吞吐提升的生產線式多執行緒系統。