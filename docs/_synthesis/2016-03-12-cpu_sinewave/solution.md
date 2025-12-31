---
layout: synthesis
title: "[樂CODE] Microsoft 面試考題: 用 CPU utilization 畫出正弦波"
synthesis_type: solution
source_post: /2016/03/12/cpu_sinewave/
redirect_from:
  - /2016/03/12/cpu_sinewave/solution/
postid: 2016-03-12-cpu_sinewave
---

以下為根據文章內容萃取並結構化的15個問題解決案例，涵蓋問題、根因、解法、實作與評估，並附上案例分類與學習路徑建議。

## Case #1: 以時間切片控制 CPU 利用率繪製正弦波（基線版）

### Problem Statement（問題陳述）
業務場景：以 CPU 利用率在系統監視器/工作管理員中畫出正弦波。需求是在指定的時間窗（例如 60 秒）內，讓 CPU 使用率依照 sin(time) 變化，並呈現可辨識的平滑波形，作為面試題目或系統層時間控制的實作練習。需能持續執行且不被一般程式雜訊干擾、波形明顯可辨識。

技術挑戰：如何將 sin(x) 的值映射為各時間切片的 CPU 繪制需求，並轉譯為 busy/idle 的時間比例控制。

影響範圍：波形是否可辨識、是否接近理想曲線、是否穩定；對呈現品質與教學示範影響大。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. sin(x) 取值為 -1~1，未做縮放與位移，無法直觀對應 CPU 使用率（0~100%）。
2. 未切片化，無法對每段時間內的使用率做明確控制。
3. 忙/閒區段的邊界未對齊，導致波形鋸齒與漂移。

深層原因：
- 架構層面：缺乏固定節拍與資料驅動（lookup）設計。
- 技術層面：時間控制未以高解析度計時器與切片規則統一管理。
- 流程層面：先做邏輯後推調整，未先定義周期、單位切片與對照表。

### Solution Design（解決方案設計）
解決策略：以固定單位時間（unit，如100ms）切片整個展示週期（period，如60秒），先將 f(x)=sin(x) 線性位移縮放為 (sin(x)+1)/2 ∈ [0,1] 後，將每片的目標使用率轉成 busy/idle 時長（例如 unit×70% busy、unit×30% idle），並用 Stopwatch 與迴圈精確控制兩段行為。

實施步驟：
1. 建立時間切片與對照表
- 實作細節：period/unit 得出 steps，對每步 s 計算 (sin+1)/2×unit。
- 所需資源：.NET、C#、Stopwatch。
- 預估時間：1 小時。

2. 實作 busy/idle 執行流程
- 實作細節：idleUntil=起始+v；busyUntil=起始+unit；先 idle 再 busy。
- 所需資源：SpinWait 或 Sleep、while 迴圈。
- 預估時間：1 小時。

3. 週期循環與視覺對齊
- 實作細節：以 (Elapsed/unit)%steps 推進步點；確保每片從切片邊界開始。
- 所需資源：Stopwatch。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
long unit = 100; // ms
long period = 60_000; // ms
long steps = period / unit;
long[] data = new long[steps];
for (int s = 0; s < steps; s++)
{
    data[s] = (long)((Math.Sin(Math.PI * s * 360 / steps / 180.0) / 2 + 0.5) * unit);
}

var timer = Stopwatch.StartNew();
while (true)
{
    long step = (timer.ElapsedMilliseconds / unit) % steps;
    long offset = timer.ElapsedMilliseconds % unit;
    long busy = data[step];
    long idleUntil = timer.ElapsedMilliseconds - offset + busy;
    long busyUntil = timer.ElapsedMilliseconds - offset + unit;

    // idle
    SpinWait.SpinUntil(() => timer.ElapsedMilliseconds > idleUntil);
    // busy
    while (timer.ElapsedMilliseconds < busyUntil) ;
}
```

實際案例：初版即能畫出可辨識 sin 波，但受雜訊與多核心影響，波形鋸齒與飄移明顯。

實作環境：Windows 10/Windows Server 2012 R2 Core、.NET Framework 4.6.1、Visual Studio 2015、4C/8T CPU。

實測數據：
改善前：未縮放/未切片，波形不可辨或嚴重鋸齒。
改善後：波形可辨識，與 sin 形狀一致。
改善幅度：可視化品質由不可辨提升至可辨識，作為基線達成度 100%。

Learning Points（學習要點）
核心知識點：
- sin(x) 區間縮放與位移映射。
- 時間切片化與對照表驅動。
- busy/idle 時長轉換的實務。

技能要求：
- 必備技能：C# 計時與迴圈控制、基本三角函數。
- 進階技能：對 Stopwatch/SpinWait 行為的理解與校準。

延伸思考：
- 可用其他波形（方波、三角波）？
- 單位切片過大/過小的影響？
- 如何在不同硬體/OS 上穩定重現？

Practice Exercise（練習題）
- 基礎練習：將正弦週期改為30秒並保持可辨識（30 分鐘）。
- 進階練習：支援動態調整 unit（50~200ms）並維持波形穩定（2 小時）。
- 專案練習：建立可切換各種波形的 CPU 畫圖器（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能持續畫出可辨正弦波。
- 程式碼品質（30%）：模組化、可維護。
- 效能優化（20%）：計時、切片與 busy/idle 切換低開銷。
- 創新性（10%）：支援不同波形/參數化設定。


## Case #2: 多核心導致單執行緒忙等僅佔整機低比例（12.5%）的問題

### Problem Statement（問題陳述）
業務場景：在 4C/8T 機器上以單執行緒 busy-wait 嘗試控制 CPU 利用率，發現總體 CPU（工作管理員顯示）最多只到 12.5%。造成目標波形的振幅無法上行，整體波形變形，視覺上難以辨識所需幅度變化，影響面試題的可展示性與可控性。

技術挑戰：如何讓總體 CPU（aggregate）達到需要的使用率，而非只在單一核心有效。

影響範圍：波形振幅不足、上緣壓縮、失真；教學演示失敗。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. busy waiting 只讓某一個核心達到 100%。
2. 工作管理員的 CPU% 是所有邏輯處理緒的總平均。
3. 多執行緒/多核心分佈未處理，造成集體指標低。

深層原因：
- 架構層面：缺乏核心/執行緒調度策略。
- 技術層面：未並行對多核心施加 busy。
- 流程層面：測試環境未與控制方法匹配（多核 vs 單線程）。

### Solution Design（解決方案設計）
解決策略：採兩路徑擇一或混用。方案A：在多核機器上依目標負載在多個執行緒上分配 busy 時間。方案B：在 1-core VM（或限制 CPU affinity）內執行，讓單執行緒控制即映射為整體 CPU%。

實施步驟：
1. 單核隔離法（推薦入門）
- 實作細節：啟 1-core VM、精簡 OS，於 VM 內跑繪圖程式。
- 所需資源：Hyper-V/VMware、Server Core。
- 預估時間：1~2 小時。

2. 多執行緒分配法（進階）
- 實作細節：依邏輯處理緒數目開對應 worker，按每片目標%分配各 worker 的 busy 比例。
- 所需資源：Thread/Task、ProcessorCount。
- 預估時間：2~4 小時。

關鍵程式碼/設定：
```csharp
// 方案A：限制至單核心（Windows 可設定 Processor Affinity 或在 VM 中以1vCPU執行）
Process.GetCurrentProcess().ProcessorAffinity = (IntPtr)0x1;

// 方案B：多執行緒分攤
int workers = Environment.ProcessorCount;
Parallel.For(0, workers, i => {
    // 每 worker 以相同比例或加權比例 busy/idle
    // while-loop 與分片時間相同的控制
});
```

實際案例：作者改在 1-core VM、Server Core 最小化背景程序下執行，避免 8 线程平均化效應，波形更貼近目標。

實作環境：Windows Server 2012 R2 Core（1 vCPU）、.NET 4.6.1。

實測數據：
改善前：單執行緒在 4C/8T 上限 ≈12.5%。
改善後：1-core VM 可達 0~100% 全域控制。
改善幅度：可用控制範圍從 12.5% 擴大至 100%（+8 倍）。

Learning Points（學習要點）
核心知識點：
- 系統 CPU% 指標為全機平均。
- 單 vs 多核心對 busy-wait 的影響。
- VM/affinity 作為控制策略。

技能要求：
- 必備技能：基本執行緒、Process/環境 API。
- 進階技能：在多核下做負載分配與同步。

延伸思考：
- 多核下如何確保各 worker 同步切片起點？
- Hyper-Threading 對負載的觀測偏差？
- 實機 vs VM 下的差異如何量化？

Practice Exercise（練習題）
- 基礎練習：在 1-core VM 中重現正弦波（30 分）。
- 進階練習：在 4C/8T 上以4個 worker 分擔負載，維持形狀（2 小時）。
- 專案練習：建立可切換「單核隔離/多線程分擔」模式的控制器（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：兩種模式皆可用。
- 程式碼品質（30%）：抽象清晰，硬體相關設定分離。
- 效能優化（20%）：切片對齊，低漂移。
- 創新性（10%）：自動偵測最佳模式。


## Case #3: 背景程序雜訊干擾導致波形抖動

### Problem Statement（問題陳述）
業務場景：在一般桌機上執行 CPU 繪圖程式，背景服務、其他應用與 OS 任務排程造成不可控雜訊，導致波形抖動與變形，無法穩定重現。同樣程式在不同時間、不同負載下結果差異大。

技術挑戰：降低非受控負載對時間精度與 CPU% 的影響。

影響範圍：圖形穩定度、可重現性、評估可信度。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 背景執行緒（noise）占用時間片，干擾 idle/busy 時間分配。
2. OS 調度與中斷搶占造成時間漂移。
3. 圖形計算與控制穿插，增加額外負載。

深層原因：
- 架構層面：執行環境未隔離。
- 技術層面：時間關鍵段落未最小化工作量。
- 流程層面：未先量測環境噪音再設計閾值/策略。

### Solution Design（解決方案設計）
解決策略：在隔離且最小化的環境下執行（Server Core/1 vCPU），並將重運算移至初始化，時間關鍵路徑只做查表與忙/閒切換，最大化 idle 段時間，減少波形抖動。

實施步驟：
1. 環境隔離與精簡
- 實作細節：Server Core 安裝、關閉不必要服務。
- 所需資源：Windows Server Core、VM 管理。
- 預估時間：1~2 小時。

2. 預計算與查表
- 實作細節：sin/bitmap 轉對照表，執行時 O(1) 查表。
- 所需資源：C# 陣列/記憶體。
- 預估時間：1 小時。

3. 重排執行序
- 實作細節：先運算再 idle，再 busy，將計算成本歸入 busy 段。
- 所需資源：Stopwatch、SpinWait。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 初始化階段完成所有運算
long[] data = Precompute(period, unit); // sin 或 bitmap 來源
// 迴圈階段只查表＋idle＋busy
SpinWait.SpinUntil(() => timer.ElapsedMilliseconds > idleUntil);
while (timer.ElapsedMilliseconds < busyUntil) ;
```

實際案例：作者以 Server Core 最小化背景程序，並調整程式執行順序，波形明顯穩定與平滑。

實作環境：Windows Server 2012 R2 Core、.NET 4.6.1、1 vCPU VM。

實測數據：
改善前：波形抖動明顯、雜訊高。
改善後：波形平滑、抖動顯著降低。
改善幅度：肉眼可辨抖動下降，穩定性明顯提升（質化）。

Learning Points（學習要點）
核心知識點：
- 執行環境對時間敏感程式的影響。
- 預計算/查表降低即時負載。
- 重排工作以擴大 idle 余裕。

技能要求：
- 必備技能：Windows 服務管理、C# 效能意識。
- 進階技能：時間路徑的成本分析與重構。

延伸思考：
- 是否可以將計算搬到專屬核心？
- 背景雜訊可否量測並動態補償？
- 記憶體佔用與查表精度的取捨？

Practice Exercise（練習題）
- 基礎練習：在本機與 VM 比較波形穩定度（30 分）。
- 進階練習：建立預計算管線，支援不同 period/unit（2 小時）。
- 專案練習：加上噪音監測與自動告警（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：穩定畫出波形。
- 程式碼品質（30%）：初始化與執行分層清晰。
- 效能優化（20%）：噪音下降、抖動減少。
- 創新性（10%）：噪音量測與報告。


## Case #4: 將 sin(x) 從 [-1,1] 映射到 [0,1] 以對應 CPU%

### Problem Statement（問題陳述）
業務場景：需要將理想的正弦函數輸出對應到 CPU 利用率（0%~100%）。若未做映射，波形計算難以直觀控制，且易造成程式內的切片控制失準，導致 busy/idle 分配不合邏輯。

技術挑戰：建立穩健、易讀、可重用的映射方式，便於擴充到任意波形。

影響範圍：波形振幅、偏移、可讀性、擴展性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. sin(x) 自然值域 -1~1 不等於 CPU% 的 0~1。
2. 無振幅與偏移控制不便調整視覺效果。
3. 直用 sin 值造成負值無法對應 idle/busy 時間。

深層原因：
- 架構層面：缺少「波形 -> 時間配額」的標準化規約。
- 技術層面：未把數學模型與控制器解耦。
- 流程層面：先寫控制器後補數學，增加耦合。

### Solution Design（解決方案設計）
解決策略：定義標準化函式 f(x)=(sin(x)+1)/2，再乘以每片時間單位 unit 取得該片的 busy 時長，idle=unit-busy。此規則同時適用於其他波形，只需替換 f(x)。

實施步驟：
1. 設計映射函式
- 實作細節：f(x)=(sin(x)+1)/2，必要時再做振幅與直流偏移。
- 所需資源：Math.Sin。
- 預估時間：0.5 小時。

2. 封裝為可替換策略
- 實作細節：介面 IWaveGenerator，回傳 steps 長度陣列。
- 所需資源：C# 介面/抽象。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
double norm = (Math.Sin(theta) + 1) / 2.0; // 0..1
long busy = (long)(norm * unit);
long idle = unit - busy;
```

實際案例：作者將 sin 映射後，以查表法驅動繪製，波形明確可控。

實作環境：.NET 4.6.1、C#。

實測數據：
改善前：負值無法對應、波形亂。
改善後：0..1 映射清晰，CPU% 可控。
改善幅度：控制正確性顯著提升（質化）。

Learning Points（學習要點）
核心知識點：
- 函數值域映射。
- 振幅與偏移控制。
- 策略模式支援多波形。

技能要求：
- 必備技能：C# 數學函式。
- 進階技能：可插拔波形生成器設計。

延伸思考：
- 是否加入增益與限幅保護？
- 不同波形（鋸齒、脈衝）如何實作？
- 映射是否要量化以配合 unit 粒度？

Practice Exercise（練習題）
- 基礎練習：加入幅度與偏移參數（30 分）。
- 進階練習：支援三角波/方波策略（2 小時）。
- 專案練習：建立波形插件系統（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：映射正確、可替換。
- 程式碼品質（30%）：介面設計良好。
- 效能優化（20%）：映射計算輕量。
- 創新性（10%）：擴展到自定義波形。


## Case #5: Idle 精準度不足（Sleep vs SpinWait）的選型與驗證

### Problem Statement（問題陳述）
業務場景：在每個切片中，需精確控制 idle 時長以達到目標 CPU%。若 idle 精準度差，會造成每片的誤差累積，讓波形飄移與失真，尤其面對背景雜訊與 OS 排程。

技術挑戰：在 10ms 等級的時間尺度上比較 Thread.Sleep 與 SpinWait/SpinUntil 的準確度與穩定性，選擇更好的方法。

影響範圍：切片內誤差、波形漂移、穩定性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Thread.Sleep 受 OS/主板 timer 影響，精確度/抖動大。
2. SpinUntil 以 delegate 判斷，存在執行成本與 timeout 超時偏移。
3. 背景噪音造成調度不確定性。

深層原因：
- 架構層面：時間控制手段未抽象、未實證。
- 技術層面：忽略 Sleep/Spin 的硬體依賴與執行語義。
- 流程層面：缺少量測比較流程與決策依據。

### Solution Design（解決方案設計）
解決策略：實作測試工具，對比在無雜訊/有雜訊（10 threads）下，Sleep(10ms) 與 SpinUntil(10ms) 的耗時分佈；選用在抖動小、平均誤差可接受的方法，並進一步優化（見 Case #7）。

實施步驟：
1. 實作度量工具
- 實作細節：Stopwatch + 多次重複；noise threads 可配置。
- 所需資源：C#、Thread。
- 預估時間：1 小時。

2. 收集與比較
- 實作細節：記錄每次耗時、計算範圍與標準差。
- 所需資源：Console/CSV。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// noise
for (int i = 0; i < 10; i++) new Thread(() => { while(!stop); }).Start();
// measure
timer.Restart(); Thread.Sleep(10); Console.WriteLine(timer.ElapsedMilliseconds);
timer.Restart(); SpinWait.SpinUntil(() => false, TimeSpan.FromMilliseconds(10));
Console.WriteLine(timer.ElapsedMilliseconds);
```

實際案例：文章實測顯示在噪音下，Sleep(10ms) 落在 10~31ms，SpinUntil(10ms) 落在 23~26ms，後者較穩定但偏移較大。

實作環境：.NET 4.6.1、Windows、4C/8T。

實測數據：
改善前（Sleep）：10~31ms，飄移大。
改善後（SpinUntil）：23~26ms，範圍更窄。
改善幅度：峰-峰抖動由 21ms 降至 3ms（約 86% 降低）。

Learning Points（學習要點）
核心知識點：
- 精確度（accuracy）vs 精密度（precision）。
- Sleep/Spin 的硬體與OS依賴。
- 實證量測的重要性。

技能要求：
- 必備技能：Stopwatch、執行緒控制。
- 進階技能：統計指標（平均/標準差）分析。

延伸思考：
- 為何 SpinUntil 平均延遲更大？
- 可否混合法降低兩者缺點？
- 如何對不同硬體自動選型？

Practice Exercise（練習題）
- 基礎練習：重現10ms測試並記錄50次（30 分）。
- 進階練習：加上 0~16 noise threads 比較（2 小時）。
- 專案練習：做一個 IdleStrategy 基準測試小工具（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可比較多策略。
- 程式碼品質（30%）：可重用與可配置。
- 效能優化（20%）：量測開銷低。
- 創新性（10%）：報表/視覺化。


## Case #6: 以 Thread.Sleep(0) 實作 Advanced Sleep（低開銷 busy-wait）

### Problem Statement（問題陳述）
業務場景：Thread.Sleep(timeout) 漂移大但平均誤差小；SpinUntil 漂移小但平均偏大。可否以 Sleep(0) 搭配 while 檢查方式折衷，既降低 context switch 不確定性，又避免長 timeout 的過度延遲？

技術挑戰：設計一個低成本、低漂移、可控的 idle 等待策略。

影響範圍：切片精確度、穩定性、整體波形品質。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Sleep(timeout) 容易被 OS 延長喚醒時間。
2. 純 Spin 會佔用核心且產熱/耗電。
3. 需要一種輕量讓出時間片但持續檢查的機制。

深層原因：
- 架構層面：時間等待未抽象成策略。
- 技術層面：忽略 Sleep(0) 讓出時間片語義。
- 流程層面：缺少對不同策略的系統性測試。

### Solution Design（解決方案設計）
解決策略：以 while(timer.Elapsed<idle) Thread.Sleep(0) 方式輪詢時間達成等待，避免長時間休眠，同時把計時主導權掌握在應用端。

實施步驟：
1. 建立 AdvancedSleep 方法
- 實作細節：Stopwatch 檢查、Sleep(0) 釋放時間片。
- 所需資源：C# Thread API。
- 預估時間：0.5 小時。

2. 與其他策略比較
- 實作細節：同 Case #5 度量框架。
- 所需資源：統計紀錄。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
var timer = Stopwatch.StartNew();
while (timer.Elapsed < idleDuration)
{
    Thread.Sleep(0); // 讓出時間片，降低佔用
}
```

實際案例：作者以 Advanced Sleep 測試，準確度排序位居第二（Adv_Spin > Adv_Sleep > Spin > Sleep）。

實作環境：.NET 4.6.1。

實測數據：
改善前：Sleep 漂移 10~31ms。
改善後：Advanced Sleep 準確度與穩定度較 Sleep 明顯改善。
改善幅度：排序提升，漂移顯著下降（質化）。

Learning Points（學習要點）
核心知識點：
- Sleep(0) 語義與排程器互動。
- 輪詢 + 讓出時間片的折衷策略。
- 與 SpinUntil 的互補性。

技能要求：
- 必備技能：Thread API、Stopwatch。
- 進階技能：策略比較與基準測試。

延伸思考：
- 是否可隨負載動態調整 Sleep(0) 與純 Spin 的比例？
- 高負載下 Sleep(0) 表現是否退化？
- 與 CPU affinity 搭配的影響？

Practice Exercise（練習題）
- 基礎練習：實作 AdvancedSleep 並比較 10ms 等待（30 分）。
- 進階練習：加入自動超時保護與記錄（2 小時）。
- 專案練習：封裝策略並支援熱切換（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：策略工作正常。
- 程式碼品質（30%）：封裝與介面清晰。
- 效能優化（20%）：低開銷、低漂移。
- 創新性（10%）：自動調參。


## Case #7: SpinUntil timeout 超時偏移的根因與 Advanced SpinUntil 修正

### Problem Statement（問題陳述）
業務場景：SpinUntil(timeout) 在 10ms 的設定下，實測耗時常為 23~26ms；雖然穩定，但平均偏移過大，導致 idle 段延長，進而影響 busy 段與波形準確度。

技術挑戰：理解 SpinUntil(timeout) 內部行為造成的延遲，並設計避免超時偏移的替代方案。

影響範圍：切片準確度、平均誤差、波形貼合度。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. SpinUntil 反覆執行委派判斷式，帶來額外執行成本。
2. timeout 僅為上限，實際跳出取決於內部迴圈與委派頻率。
3. 背景負載會使委派呼叫更緩慢。

深層原因：
- 架構層面：超時控制與條件判斷耦合。
- 技術層面：delegate 呼叫成本未量化。
- 流程層面：未用外部計時器主導離開條件。

### Solution Design（解決方案設計）
解決策略：改用 Advanced Spin：SpinWait.SpinUntil(()=> timer.Elapsed>idle)，以外部 Stopwatch 主導條件，而非用 timeout 參數。此法減少委派重複觸發造成的偏移。

實施步驟：
1. 改寫 idle 等待為 Advanced Spin
- 實作細節：SpinUntil(() => timer.Elapsed > idleUntil)。
- 所需資源：Stopwatch、SpinWait。
- 預估時間：0.5 小時。

2. 量測比較（與 Sleep/Spin/AdvSleep）
- 實作細節：重跑噪音情境，收集 mean/std。
- 所需資源：度量框架。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
var timer = Stopwatch.StartNew();
SpinWait.SpinUntil(() => timer.Elapsed > idleDuration);
```

實際案例：作者綜合比較，在 8 noise threads 情境下，準確度與精密度最佳為 Adv_Spin，其次 Adv_Sleep、Spin、Sleep。

實作環境：.NET 4.6.1。

實測數據：
改善前：SpinUntil(timeout=10ms) 實際 23~26ms。
改善後：Adv_Spin 精確度、精密度最佳（排序第一）。
改善幅度：平均偏移顯著下降、抖動小（質化）。

Learning Points（學習要點）
核心知識點：
- 委派成本與超時語義的差別。
- 外部計時器主導的好處。
- 準確度/精密度雙指標評估。

技能要求：
- 必備技能：SpinWait、Stopwatch。
- 進階技能：策略調優與量測。

延伸思考：
- 是否可適配不同 unit 與負載？
- 對 ARM/非 x86 平台的影響？
- 加入退避與讓出時間片的混合設計？

Practice Exercise（練習題）
- 基礎練習：改寫為 Adv_Spin 並比較結果（30 分）。
- 進階練習：在 0~10 噪音執行緒下建立比較圖（2 小時）。
- 專案練習：做策略選擇器自動挑選最佳 idle 策略（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：策略可替換與比較。
- 程式碼品質（30%）：結構清楚、重用性高。
- 效能優化（20%）：平均偏移與抖動下降。
- 創新性（10%）：自動選型與報告。


## Case #8: 預計算查表法降低即時路徑運算負擔

### Problem Statement（問題陳述）
業務場景：在時間切片內即時計算 sin、索引映射等，會增加 CPU 負載，影響 idle 段可用時間，使得波形穩定性下降，尤其在噪音或高負載下更明顯。

技術挑戰：減少即時運算，讓時間關鍵路徑最短，確保 idle 時間能充分執行。

影響範圍：抖動、穩定性、可擴充性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 每片 sin 計算與索引換算耗時。
2. 計算放在 idle 前，擠壓 idle 時間。
3. 迴圈中多次分配與轉型增加成本。

深層原因：
- 架構層面：時間關鍵路徑未最小化。
- 技術層面：未使用查表。
- 流程層面：初始化階段未善用。

### Solution Design（解決方案設計）
解決策略：將 sin/bitmap 對應的 busy 時長在初始化期一次性計算好（steps 大小陣列），執行期僅查表、Idle、Busy，並把所有邏輯重排以最大化 idle 窗。

實施步驟：
1. 實作 GetDataFromSineWave / GetDataFromBitmap
- 實作細節：輸入 period/unit，輸出 long[]。
- 所需資源：C# 陣列。
- 預估時間：0.5 小時。

2. 重排主迴圈
- 實作細節：先計算當前 step 與時間邊界，再 idle，再 busy。
- 所需資源：Stopwatch。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public static long[] GetDataFromSineWave(long period, long unit)
{
    long steps = period / unit; var data = new long[steps];
    for (int s = 0; s < steps; s++)
        data[s] = (long)((Math.Sin(Math.PI * s * 360 / steps / 180.0) / 2 + 0.5) * unit);
    return data;
}
```

實際案例：作者導入查表後，波形顯著平滑，雜訊干擾下降。

實作環境：.NET 4.6.1。

實測數據：
改善前：迴圈中計算造成 idle 受壓縮，波形抖動。
改善後：查表 + 重排，波形穩定。
改善幅度：波形品質顯著提升（質化）。

Learning Points（學習要點）
核心知識點：
- 即時路徑最小化思維。
- 查表法（O(1)）應用。
- 先計算後控制的流程設計。

技能要求：
- 必備技能：陣列與索引操作。
- 進階技能：時間敏感程式的微型架構。

延伸思考：
- 是否可用 SIMD/Span 進一步提速？
- steps 增加的記憶體取捨？
- 熱切換波形時，如何無縫更新表？

Practice Exercise（練習題）
- 基礎練習：把 sin 實時計算改為查表（30 分）。
- 進階練習：支援動態重建表且不中斷（2 小時）。
- 專案練習：建立波形表快取與版本管理（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：查表正確與可用。
- 程式碼品質（30%）：清楚分離 init/loop。
- 效能優化（20%）：迴圈負載降低。
- 創新性（10%）：無縫更新策略。


## Case #9: 切片與周期對齊（unit/period 校準）以匹配監視器時間尺

### Problem Statement（問題陳述）
業務場景：要讓工作管理員/監視器視窗呈現完整的波形，需與其時間軸對齊。若 unit 與 period 未合理設定，形狀會被壓縮/拉伸或邊界斷裂，影響視覺辨識。

技術挑戰：選擇適合的 unit（如 100ms）與 period（如 60s）使波形完整穩定。

影響範圍：視覺品質、展示效果、比較一致性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. steps 選擇不匹配視窗寬度/更新節奏。
2. unit 過小導致管理員更新頻率不及。
3. period 與裝置顯示視窗不同步。

深層原因：
- 架構層面：未做外部觀測系統的標定。
- 技術層面：忽略 UI 更新節奏。
- 流程層面：缺乏校準步驟。

### Solution Design（解決方案設計）
解決策略：設定 period=60秒、unit=100ms，得 steps=600；對應常見 CPU 圖的 60 秒寬度。此設計容易在大多數 Windows 版本上取得一致視覺效果。

實施步驟：
1. 目標視窗辨識
- 實作細節：確認 CPU 圖顯示 60秒。
- 所需資源：系統工具。
- 預估時間：10 分。

2. 參數設定與驗證
- 實作細節：調整 unit 為 100ms、重繪檢視。
- 所需資源：程式參數化。
- 預估時間：20 分。

關鍵程式碼/設定：
```csharp
long unit = 100;      // 100ms
long period = 60_000; // 60s window
```

實際案例：作者使用 100ms/60s 組合，獲得完整清晰的 1 週期顯示。

實作環境：Windows、.NET 4.6.1。

實測數據：
改善前：unit 不匹配，曲線斷裂/變形。
改善後：完整 1 週期視覺穩定。
改善幅度：展示品質提升（質化）。

Learning Points（學習要點）
核心知識點：
- 外部觀測同步的重要性。
- unit/period 關係與步數。
- 視覺呈現對技術參數的約束。

技能要求：
- 必備技能：參數化與驗證。
- 進階技能：對外部系統行為建模。

延伸思考：
- 不同 OS/工具的窗口長度差異？
- 自動偵測並調整 unit/period？
- 動態縮放多週期拼接？

Practice Exercise（練習題）
- 基礎練習：把 period 改為 30s 並保持美觀（30 分）。
- 進階練習：加入自動 period 偵測（2 小時）。
- 專案練習：建立 GUI 讓使用者調參並即時預覽（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可對齊外部視窗。
- 程式碼品質（30%）：參數化與持久化。
- 效能優化（20%）：切片開銷穩定。
- 創新性（10%）：自動校準。


## Case #10: 先 idle 後 busy 的執行順序重排以降低干擾

### Problem Statement（問題陳述）
業務場景：若先做運算/busy 再 idle，會出現 idle 剩餘時間不足的情形，造成切片漂移與波形抖動。需要調整流程以最大化 idle 段準確性。

技術挑戰：如何將所有計算歸入 busy 段，留給 idle 最乾淨的窗口。

影響範圍：時間精確度、漂移與穩定性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 計算插入 idle 前，壓縮 idle。
2. busy/idle 邊界與切片起點未對齊。
3. while 迴圈的忙等無法補償前段運算。

深層原因：
- 架構層面：執行階段工作順序未設計。
- 技術層面：缺乏邊界對齊。
- 經驗流程：未考慮最壞情境。

### Solution Design（解決方案設計）
解決策略：在每片開始，立即計算 step、offset、idleUntil、busyUntil，然後先 idle（用 Adv_Spin），最後 busy（純 while）。此序避免 idle 前的運算成本擠壓 idle。

實施步驟：
1. 邊界計算
- 實作細節：以 (Elapsed/unit)%steps 與 offset 取得本片邊界。
- 所需資源：Stopwatch。
- 預估時間：0.5 小時。

2. 流程重排
- 實作細節：先 idle 再 busy。
- 所需資源：SpinWait、while。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
long step = (timer.ElapsedMilliseconds / unit) % (period / unit);
long offset = timer.ElapsedMilliseconds % unit;
long idleUntil = timer.ElapsedMilliseconds - offset + v;
long busyUntil = timer.ElapsedMilliseconds - offset + unit;
SpinWait.SpinUntil(() => timer.ElapsedMilliseconds > idleUntil);
while (timer.ElapsedMilliseconds < busyUntil) ;
```

實際案例：重排後波形更平滑，雜訊顯著降低。

實作環境：.NET 4.6.1。

實測數據：
改善前：idle 被擠壓，漂移大。
改善後：idle 窗口最大化，漂移小。
改善幅度：穩定度可視化提升（質化）。

Learning Points（學習要點）
核心知識點：
- 邊界對齊與 offset 校正。
- 執行順序對時間準確性的影響。
- idle 窗窗口設計。

技能要求：
- 必備技能：時間計算。
- 進階技能：流程重構。

延伸思考：
- busy 段是否允許自動截短防止溢出？
- offset 校正是否需積分補償？
- 高負載下的保護策略？

Practice Exercise（練習題）
- 基礎練習：加入 offset 計算並重排流程（30 分）。
- 進階練習：記錄每片 drift 並統計（2 小時）。
- 專案練習：實作 drift 補償控制環（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：重排後運作穩定。
- 程式碼品質（30%）：邏輯清晰。
- 效能優化（20%）：drift 降低。
- 創新性（10%）：補償機制。


## Case #11: 比較四種等待策略的準確度與精密度並選型

### Problem Statement（問題陳述）
業務場景：待選策略含 Sleep、SpinUntil、Advanced Sleep、Advanced SpinUntil。需在不同噪音程度下比較「準確度（平均接近程度）」與「精密度（標準差）」以選出最佳方案。

技術挑戰：建立可重現的測試並做出客觀選型。

影響範圍：整體波形品質與可重現性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不同策略的行為差異大。
2. 噪音下誤差與漂移變化明顯。
3. 無比較就難以決策。

深層原因：
- 架構層面：缺乏策略比較框架。
- 技術層面：缺少統計指標。
- 流程層面：未制訂選型標準。

### Solution Design（解決方案設計）
解決策略：在 0~10 noise threads 下各執行50次，收集均值與標準差。依據準確度（均值接近理想）與精密度（標準差最小）綜合評分。選擇 Advanced SpinUntil。

實施步驟：
1. 度量框架
- 實作細節：統一介面、可配置 noise 與重複次數。
- 所需資源：C#、統計。
- 預估時間：2 小時。

2. 報表與決策
- 實作細節：輸出圖表/排序。
- 所需資源：簡易繪圖或 CSV。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 以委派傳入等待策略，迭代測量均值/標準差
Func<TimeSpan, TimeSpan> idleStrategy = AdvSpin; // or Sleep/Spin/AdvSleep
```

實際案例：排序結果在 8 noise threads 下為：準確度 Adv_Spin > Adv_Sleep > Spin > Sleep；精密度 Adv_Spin > Spin > Adv_Sleep > Sleep。

實作環境：.NET 4.6.1。

實測數據：
改善前：無選型依據。
改善後：有客觀排序與最佳策略（Adv_Spin）。
改善幅度：決策品質提升（質化）。

Learning Points（學習要點）
核心知識點：
- 準確度 vs 精密度。
- 策略基準測試。
- 噪音情境測試設計。

技能要求：
- 必備技能：C# 委派/介面。
- 進階技能：統計與報表。

延伸思考：
- 可否根據結果自動調參？
- 不同硬體上是否需重訓基準？
- 長時間運轉的漂移如何監控？

Practice Exercise（練習題）
- 基礎練習：建立策略比較骨架（30 分）。
- 進階練習：輸出 CSV 並用 Excel 畫圖（2 小時）。
- 專案練習：實作策略選型器（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能比較並產出排序。
- 程式碼品質（30%）：架構清晰、易擴充。
- 效能優化（20%）：量測負擔低。
- 創新性（10%）：自動決策。


## Case #12: 利用 ASCII Art 生成對照表，畫出任意圖形（Batman Logo 範例）

### Problem Statement（問題陳述）
業務場景：在完成正弦波後，將輸出一般化至任意圖形。輸入為字元畫（ASCII Art），輸出為每片的 busy 時長表，達成「用 CPU% 畫圖」的創意應用。

技術挑戰：設計從字元矩陣到時間切片的映射流程。

影響範圍：功能擴展性、教學趣味性、展示效果。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 需要從二維圖映射到一維時間序列。
2. X 軸取樣與 Y 軸高度需轉為時間占比。
3. 字元矩陣解析與取樣邊界處理。

深層原因：
- 架構層面：對照表生成器需支持多來源。
- 技術層面：取樣與比例換算。
- 流程層面：資料準備與驗證。

### Solution Design（解決方案設計）
解決策略：解析字串陣列 bitmap，對 steps 內每一步 s 依比例映射至 X 座標，從上往下掃描遇到 'X' 的第一列作為高度，轉為 busy 時長比例，即可得到 data[]；主程式不變。

實施步驟：
1. 設計 Bitmap 解析器
- 實作細節：max_x/ max_y、X 比例映射、首個 'X' 為高度。
- 所需資源：C# 字串處理。
- 預估時間：1 小時。

2. 整合與展示
- 實作細節：與 DrawBitmap 流程共用。
- 所需資源：現有主迴圈。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
int max_x = bitmap[0].Length, max_y = bitmap.Length;
for (int s = 0; s < steps; s++)
{
    int x = (int)(s * max_x / steps);
    int value = 0;
    for (int y = 0; y < max_y; y++) { value = y; if (bitmap[y][x] == 'X') break; }
    data[s] = value * unit / max_y; // busy 時長
}
```

實際案例：Batman Logo 成功用 CPU 圖繪出，與原圖對比相似度高。

實作環境：.NET 4.6.1。

實測數據：
改善前：僅能畫正弦波。
改善後：能畫任意圖形（ASCII Art）。
改善幅度：功能增強，應用場景擴展（質化）。

Learning Points（學習要點）
核心知識點：
- 二維到一維映射。
- 比例換算與取樣。
- 資料驅動繪製。

技能要求：
- 必備技能：字串處理、陣列。
- 進階技能：資料映射與抽象。

延伸思考：
- 是否可支持圖片灰階到多層 busy 百分比？
- 動態圖（多幀）如何播放？
- 解析度與 unit 的關係？

Practice Exercise（練習題）
- 基礎練習：用 ASCII 畫出簡單圖形並繪製（30 分）。
- 進階練習：支援讀取文字檔/圖片轉字元（2 小時）。
- 專案練習：做一個「CPU 繪圖秀」工具（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可從 ASCII 成功繪出。
- 程式碼品質（30%）：清楚解耦來源與渲染。
- 效能優化（20%）：解析與渲染順暢。
- 創新性（10%）：多圖/動畫。


## Case #13: 建立噪音執行緒（noise）以壓力測試與驗證穩定性

### Problem Statement（問題陳述）
業務場景：為了逼近實際環境，需要在背景加入可控噪音（例如 10 個 while(true) 執行緒），用以驗證等待策略與繪圖流程在高負載下的穩定性與漂移狀況。

技術挑戰：如何設計可控、可重現、可調整的噪音產生器。

影響範圍：測試可信度、穩健性、策略選型。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 實務環境不可能零噪音。
2. 缺乏噪音會高估策略表現。
3. 噪音強度需可調。

深層原因：
- 架構層面：測試環境不完整。
- 技術層面：缺少噪音模組。
- 流程層面：未建立壓力測試流程。

### Solution Design（解決方案設計）
解決策略：在測試程式中加入 noise thread 啟動段，可設定數量，使用 while(!stop) 忙等。測試結束時以旗標停止並回收。

實施步驟：
1. 噪音模組化
- 實作細節：StartNoise(n)、StopNoise()。
- 所需資源：Thread API。
- 預估時間：0.5 小時。

2. 度量集成
- 實作細節：支援 0~N 不同級別測試。
- 所需資源：測試控制台。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
volatile bool stop = false;
List<Thread> noises = new();
void StartNoise(int n) {
    for (int i=0;i<n;i++){ var t=new Thread(()=>{ while(!stop) ;}); t.Start(); noises.Add(t); }
}
void StopNoise(){ stop=true; foreach(var t in noises) t.Join(); }
```

實際案例：作者使用 10 noise threads 測出 Sleep 與 SpinUntil 行為差異，支撐選型。

實作環境：.NET 4.6.1。

實測數據：
改善前：無法評估高負載情境。
改善後：可量測 0~10 noise 下策略差異。
改善幅度：測試覆蓋度提升（質化）。

Learning Points（學習要點）
核心知識點：
- 壓力測試的重要性。
- 可調噪音設計。
- 與度量框架整合。

技能要求：
- 必備技能：執行緒操作。
- 進階技能：測試設計與報告。

延伸思考：
- 加入 I/O 或記憶體型噪音？
- 噪音與核心數比例的影響？
- 自動化壓力測試管線？

Practice Exercise（練習題）
- 基礎練習：加入 5/10 個 noise 並比較（30 分）。
- 進階練習：噪音型別可切換（busy/睡眠/IO）（2 小時）。
- 專案練習：壓測控制台＋報表匯出（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：噪音可控。
- 程式碼品質（30%）：模組化與清晰。
- 效能優化（20%）：測試穩定、無資源洩漏。
- 創新性（10%）：多型噪音。


## Case #14: 理解與善用 SpinWait（HLT/讓位）以降低 idle 段對 CPU% 的干擾

### Problem Statement（問題陳述）
業務場景：需要 idle 段不顯著抬高 CPU%，又要避免 Sleep 的長延遲與漂移。SpinWait 在單處理器上會選擇 yield 而非純 busy，在超執行緒硬體上也能避免飢餓，有助於控制 idle 段的「輕量忙等」。

技術挑戰：適當使用 SpinWait 調節忙等與讓出，降低 idle 對 CPU% 的干擾。

影響範圍：idle 段的 CPU 佔用、穩定性、耗電與散熱。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 純 while(true) 忙等會拉高 idle 段 CPU%。
2. Sleep 長延遲造成切片漂移。
3. SpinWait 可透過內部策略（如 HLT/Yield）達到折衷。

深層原因：
- 架構層面：未善用 runtime 提供的同步原語。
- 技術層面：對 SpinWait 語義與實作不了解。
- 流程層面：未實證比較其效果。

### Solution Design（解決方案設計）
解決策略：在 idle 段使用 SpinWait.SpinUntil（Adv 版本），以較低的 CPU 佔用實現精細等待；busy 段才使用純 while 忙等，以達到預期使用率。

實施步驟：
1. Idle 使用 Adv_Spin
- 實作細節：SpinUntil(() => timer > idleUntil)。
- 所需資源：SpinWait、Stopwatch。
- 預估時間：0.5 小時。

2. Busy 使用 while
- 實作細節：while(timer < busyUntil) ;。
- 所需資源：Stopwatch。
- 預估時間：0.2 小時。

關鍵程式碼/設定：
```csharp
SpinWait.SpinUntil(() => timer.ElapsedMilliseconds > idleUntil);
while (timer.ElapsedMilliseconds < busyUntil) ;
```

實際案例：Idle 段 CPU% 佔用低，波形穩定且漂移可控。

實作環境：.NET 4.6.1。

實測數據：
改善前：純忙等 idle 影響總體 CPU%。
改善後：SpinWait 降低 idle 佔用與抖動。
改善幅度：穩定性與能效提升（質化）。

Learning Points（學習要點）
核心知識點：
- SpinWait 語義與平台差異。
- 忙等與讓位策略的取捨。
- Idle vs Busy 的不同實作。

技能要求：
- 必備技能：SpinWait。
- 進階技能：對硬體/OS 行為的理解。

延伸思考：
- 不同 CPU 節能策略對行為的影響？
- 混合 Sleep(0) 與 SpinWait 是否更佳？
- 建立能效與穩定性的平衡指標？

Practice Exercise（練習題）
- 基礎練習：以 SpinWait 實作 idle 段（30 分）。
- 進階練習：比較 idle 段 CPU% 佔用（2 小時）。
- 專案練習：能效/穩定性雙目標優化（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：idle 段表現良好。
- 程式碼品質（30%）：清楚區分 idle/busy。
- 效能優化（20%）：CPU% 與漂移下降。
- 創新性（10%）：混合策略。


## Case #15: 以 VM/Server Core 最小化背景服務，提升波形可重現性

### Problem Statement（問題陳述）
業務場景：在一般桌機上背景服務眾多，結果不穩。將程式移至 Windows Server 2012 R2 Server Core，採最精簡安裝，並在 1 vCPU VM 執行以最小化干擾，提升結果可重現性與可比性。

技術挑戰：建立可控、可複製的測試/展示環境。

影響範圍：可靠度、跨團隊共享、教學演示。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 背景程序不可控。
2. 多核平均稀釋。
3. OS 版本與設定差異。

深層原因：
- 架構層面：缺固定參考環境。
- 技術層面：硬體/OS 變項多。
- 流程層面：環境準備未標準化。

### Solution Design（解決方案設計）
解決策略：以 VM 模板提供固定環境（Server Core＋1 vCPU），安裝必要工具，關閉非必要服務，搭配簡單腳本一鍵部署，確保測試/展示一致性。

實施步驟：
1. VM 模板建立
- 實作細節：1 vCPU、Server Core、關閉服務。
- 所需資源：Hyper-V/VMware。
- 預估時間：1~2 小時。

2. 部署腳本與指引
- 實作細節：PowerShell 啟停服務、設定優先度/親和性。
- 所需資源：PowerShell。
- 預估時間：1 小時。

關鍵程式碼/設定：
```powershell
# 範例：停用不必要服務（依實測調整）
Stop-Service -Name "DiagTrack" -ErrorAction SilentlyContinue
# 設定處理序優先度/親和性可另行加入
```

實際案例：作者在 Server Core 1 vCPU 中執行，得到更穩的正弦波形。

實作環境：Windows Server 2012 R2 Core、Hyper-V/VMware、.NET 4.6.1。

實測數據：
改善前：雜訊高、結果每次不同。
改善後：穩定可重現。
改善幅度：可重現性顯著提升（質化）。

Learning Points（學習要點）
核心知識點：
- 測試環境標準化。
- VM/OS 精簡化的好處。
- 參數固定化的重要性。

技能要求：
- 必備技能：基礎 VM 操作。
- 進階技能：PowerShell 自動化。

延伸思考：
- Docker/容器是否可用於此類型？
- 以 CI 自動跑測試與截圖？
- 跨硬體平台的一致性？

Practice Exercise（練習題）
- 基礎練習：在 VM 中重現波形（30 分）。
- 進階練習：建立停用服務腳本（2 小時）。
- 專案練習：打造一鍵部署與自動測試（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：環境可用。
- 程式碼品質（30%）：腳本清晰。
- 效能優化（20%）：雜訊低。
- 創新性（10%）：自動化程度。


## Case #16: 用 Stopwatch 作為高解析度時鐘，避免系統時鐘不準

### Problem Statement（問題陳述）
業務場景：需要高精度計時來界定 idle_until 與 busy_until。若使用 DateTime.Now 等低解析度時鐘，易造成時間判定誤差，對每片內的等待造成偏差。

技術挑戰：使用高解析度計時（Stopwatch）並確保重置/讀取位置正確。

影響範圍：片內時間判準、漂移、抖動。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 系統時鐘解析度不足。
2. 不當重置或多次新建計時物件造成開銷與誤差。
3. 讀取位置不當導致 offset 計算錯誤。

深層原因：
- 架構層面：計時器使用未標準化。
- 技術層面：忽略 Stopwatch 的解析度優勢。
- 流程層面：未統一計時器生命週期。

### Solution Design（解決方案設計）
解決策略：全程使用單一 Stopwatch 實例，啟動後不重建；在每片起點讀取 elapsed 並計算 offset；以該基準推算 idle/busy 邊界。

實施步驟：
1. 統一計時器
- 實作細節：var timer=Stopwatch.StartNew(); 全域使用。
- 所需資源：System.Diagnostics。
- 預估時間：10 分。

2. 讀取與計算規約
- 實作細節：固定在片起點讀取 elapsed，避免中途變更。
- 所需資源：程式碼規範。
- 預估時間：20 分。

關鍵程式碼/設定：
```csharp
var timer = Stopwatch.StartNew();
// 每片使用 timer.ElapsedMilliseconds 作為單一來源
```

實際案例：作者所有量測與等待皆以 Stopwatch 主導，避免時鐘不準問題。

實作環境：.NET 4.6.1。

實測數據：
改善前：以系統時鐘可能造成毫秒級誤差。
改善後：Stopwatch 穩定，漂移降低。
改善幅度：精度提升（質化）。

Learning Points（學習要點）
核心知識點：
- Stopwatch 解析度與可靠性。
- 計時器生命週期設計。
- 讀取時機對準確性影響。

技能要求：
- 必備技能：Stopwatch 使用。
- 進階技能：量測框架設計。

延伸思考：
- 在 .NET Core 與不同平台解析度差異？
- 是否需要校準 Stopwatch 與牆鐘？
- 長期運作的計時漂移？

Practice Exercise（練習題）
- 基礎練習：改用 Stopwatch 並驗證（30 分）。
- 進階練習：長時運行漂移觀測（2 小時）。
- 專案練習：計時抽象介面＋可換實作（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：計時正確穩定。
- 程式碼品質（30%）：一致使用單一來源。
- 效能優化（20%）：低開銷。
- 創新性（10%）：跨平台支持。


## Case #17: Busy 段內扣除額外運算時間，確保目標占比落地

### Problem Statement（問題陳述）
業務場景：若在 busy 段內還執行其他非忙等的運算（如索引/輸出），會導致實際忙等時間不足，CPU% 低於目標，長期累積造成波形下緣鋸齒或偏移。

技術挑戰：如何精確扣除運算時間，讓純忙等段補足至 busy_until。

影響範圍：占比準確性、波形平滑度。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 忙等時間被其他運算侵蝕。
2. 未以 busy_until 作為嚴格邊界。
3. 片內開銷未統計。

深層原因：
- 架構層面：未將開銷歸入 busy。
- 技術層面：邊界未實作硬限制。
- 流程層面：缺乏片內成本度量。

### Solution Design（解決方案設計）
解決策略：建立 busy_until 為嚴格邊界，將片內所有非 idle 的運算視為 busy 開銷，最後以 while(timer<busy_until) 純忙等補足，確保目標占比。

實施步驟：
1. 定義邊界
- 實作細節：busy_until = 起始切片基準 + unit。
- 所需資源：Stopwatch。
- 預估時間：0.2 小時。

2. 歸屬與補足
- 實作細節：計算/輸出等皆放 busy 段起始，最後補足忙等。
- 所需資源：流程重排。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
// busy 邊界固定
long busyUntil = baseTime + unit;
// 做完必要運算後，補足忙等
while (timer.ElapsedMilliseconds < busyUntil) ;
```

實際案例：作者重排後波形貼合度高，抖動降低。

實作環境：.NET 4.6.1。

實測數據：
改善前：忙等不足造成占比偏低。
改善後：占比吻合，波形平滑。
改善幅度：準確性提升（質化）。

Learning Points（學習要點）
核心知識點：
- 邊界控制與嚴格補足。
- 成本歸屬原則。
- 占比達成的實務。

技能要求：
- 必備技能：時間計算。
- 進階技能：微觀性能分析。

延伸思考：
- 是否需對忙等前的運算限時？
- 多線程下如何一致扣除？
- 引入統計以量化片內成本？

Practice Exercise（練習題）
- 基礎練習：以 busy_until 補足忙等（30 分）。
- 進階練習：統計片內運算時間（2 小時）。
- 專案練習：自動調整 busy 目標以補償系統性偏差（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：占比一致。
- 程式碼品質（30%）：邏輯清晰。
- 效能優化（20%）：抖動降低。
- 創新性（10%）：動態補償。


--------------------------------
案例分類
--------------------------------
1. 按難度分類
- 入門級（適合初學者）
  - Case #1, #2, #4, #8, #9, #16
- 中級（需要一定基礎）
  - Case #3, #5, #6, #7, #10, #11, #14, #15, #17
- 高級（需要深厚經驗）
  - （無；本文案例以系統/時間控制中級為主，可延伸為高級：多核負載分配與自動補償控制）

2. 按技術領域分類
- 架構設計類
  - Case #1, #8, #9, #10, #11, #15
- 效能優化類
  - Case #3, #5, #6, #7, #14, #16, #17
- 整合開發類
  - Case #2, #12, #13, #15
- 除錯診斷類
  - Case #5, #11, #13, #16
- 安全防護類
  - （不適用，本文無安全面向案例）

3. 按學習目標分類
- 概念理解型
  - Case #1, #4, #9, #14, #16
- 技能練習型
  - Case #2, #6, #8, #10, #12, #13, #15
- 問題解決型
  - Case #3, #5, #7, #11, #17
- 創新應用型
  - Case #12（ASCII Art）、#11（自動選型延伸）

--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 建議先學：
  - Case #1（基線設計：切片與映射）
  - Case #4（sin 值域映射到 CPU%）
  - Case #9（unit/period 校準）
  - Case #16（Stopwatch 高解析度計時）

- 依賴關係與進階：
  - Case #1 → Case #8（查表優化）→ Case #10（先 idle 後 busy 重排）→ Case #17（忙等補足與占比精準）
  - Case #5（Sleep vs SpinWait 比較）→ Case #6（Advanced Sleep）與 Case #7（Advanced SpinUntil）→ Case #11（策略選型）
  - Case #2（多核/單核控制）與 Case #15（VM/Server Core 環境）→ Case #3（雜訊抑制）
  - Case #13（噪音壓測）支援 Case #5/#6/#7/#11 的比較驗證
  - Case #12（ASCII Art 擴展）依賴 Case #1/#8 的資料驅動框架

- 完整學習路徑建議：
  1) Case #1 → #4 → #9 → #16（建立正確基礎）
  2) Case #8 → #10 → #17（時間關鍵路徑優化與占比精準）
  3) Case #5 → #6 → #7 → #11（等待策略的實證與選型）
  4) Case #2 → #15 → #3（環境與多核影響的控制）
  5) Case #13（建立壓測方法論）
  6) Case #12（功能創新擴展：任意圖形）
  
  依此路徑學習，可從基礎概念、時間控制實作、策略選型、環境工程，到創意應用完整掌握，並具備在異質硬體/雜訊環境下穩定重現的能力。