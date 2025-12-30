---
layout: synthesis
title: "微服務基礎建設: Process Pool 的設計與應用"
synthesis_type: solution
source_post: /2020/02/09/process-pool/
redirect_from:
  - /2020/02/09/process-pool/solution/
---

以下為基於文章內容萃取與結構化的 18 個教學型實戰案例，涵蓋問題、根因、解法（含關鍵程式碼/流程）、實測數據與學習與評估設計。所有案例皆來自文中場景與測試數據，便於在專案練習與能力評估中落地應用。

------------------------------------------------------------

## Case #1: 多團隊非同步任務的安全隔離與高吞吐

### Problem Statement（問題陳述）
- 業務場景：公司內超過百人的研發團隊，透過 Message Queue 派送大量類 serverless 的非同步任務至後端 Worker。各團隊的程式碼需共用同一套任務管理平台，必須同時滿足隔離失敗風險與高吞吐處理的需求。
- 技術挑戰：在確保隔離（避免記憶體/CPU/靜態狀態污染/未捕捉例外）的同時，維持極高的任務處理吞吐，並兼顧跨 .NET Fx/Core 的相容性。
- 影響範圍：一旦缺乏隔離，單一任務失敗可能拖垮整個進程；吞吐不足將導致 MQ 堆積、SLA 失效。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 不同團隊任務共用執行環境，靜態變數與例外可互相污染或終止進程。
  2. Process 啟動成本高，若每任務重啟將造成巨大延遲。
  3. .NET Core 已取消 AppDomain，傳統隔離手段受限。
- 深層原因：
  - 架構層面：以 Thread/In-Process 為單位的執行模式不具防護網，且難以水平擴展。
  - 技術層面：IPC、跨執行環境序列化與 I/O 成本未被設計消彌。
  - 流程層面：缺乏以 Pool 為核心的資源調度與自動回收策略。

### Solution Design（解決方案設計）
- 解決策略：以 Process 作為基本隔離單位，並建置 Process Pool 調度，將昂貴的 Process 啟動成本攤銷在多筆任務上。跨進程通訊採 STDIO（或 Pipe）+ Base64（BLOB）傳遞，抽象出 Worker 介面以兼容 .NET Fx/Core。以 Benchmark 驅動選型，最終選擇「Host/Worker 均 .NET Core + Process Pool」。

**實施步驟**：
1. 隔離層級選型與基準測試
   - 實作細節：對 InProcess/Thread/AppDomain/Process 以空 Main 與 HelloTask（SHA512）做啟動與吞吐測試。
   - 所需資源：.NET Fx 4.7.2、.NET Core 3.1、Stopwatch。
   - 預估時間：0.5 天
2. IPC 通道與資料格式決策
   - 實作細節：STDIN/STDOUT 重導向，VALUE/BASE64 兩種模式；HelloTask 對應 BLOB。
   - 所需資源：ProcessStartInfo（RedirectStandardInput/Output）。
   - 預估時間：0.5 天
3. 建置 Worker 抽象層
   - 實作細節：定義 HelloWorkerBase/HelloTaskResult（ManualResetEventSlim），封裝 Queue/Wait。
   - 所需資源：BlockingCollection、ManualResetEventSlim。
   - 預估時間：0.5 天
4. Process Pool 編排
   - 實作細節：Min/Max/Idle Timeout、TryIncrease/ShouldDecrease、Keep-Alive 與回收。
   - 所需資源：自訂 ProcessPoolWorker。
   - 預估時間：1 天

**關鍵程式碼/設定**：
```csharp
// 啟動 Process 並重導向 STDIO
var p = Process.Start(new ProcessStartInfo {
  FileName = "Worker.exe",
  RedirectStandardInput = true,
  RedirectStandardOutput = true,
  UseShellExecute = false
});
var reader = p.StandardOutput;
var writer = p.StandardInput;

// 傳遞參數（BASE64）並取回結果
writer.WriteLine(Convert.ToBase64String(buffer));
string result = reader.ReadLine();
```

實際案例：
- 實作環境：Windows 10、.NET Framework 4.7.2、.NET Core 3.1、Console App
- 實測數據：
  - 啟動速度（.NET Core Host）：Process 23.2558 run/sec；（.NET Fx Host）Process 11.7647~12.6582 run/sec
  - 任務吞吐（無負載，Process Core + BLOB）：37037 tasks/sec
  - 任務吞吐（有負載 1KB，Process Core + BLOB）：25575 tasks/sec
  - 以 Process Pool（.NET Core + 1MB）達 183.898 tasks/sec，相較單 Process 55.13 提升約 233%

Learning Points（學習要點）
- 核心知識點：
  - 隔離層級（Thread/AppDomain/Process）特性與取捨
  - IPC 模型與資料序列化策略（VALUE vs BLOB）
  - Pool 編排（Min/Max/Idle）與自動回收
- 技能要求：
  - 必備技能：C#、Process/IPC、基準測試、同步原語
  - 進階技能：系統調度思維（Backpressure、Keep-Alive）、效能分析
- 延伸思考：
  - 能否以 Container/Pod 取代？（頻率極低任務 + Windows/DB 連線池不利）
  - 風險：跨語言序列化成本、Process 泄漏
  - 優化：Named Pipe/Memory-Mapped File、零拷貝、非同步管線

Practice Exercise（練習題）
- 基礎練習：複製文中 Process + STDIO 範例，完成 VALUE/BASE64 兩模式（30 分）
- 進階練習：加上 Benchmark，比較 .NET Fx 與 .NET Core 的吞吐（2 小時）
- 專案練習：實作 Process Pool（Min/Max/Idle + 日誌），接上簡單 MQ 模擬（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能穩定跨進程傳參回傳、Pool 自動伸縮
- 程式碼品質（30%）：抽象良好，無共享狀態污染
- 效能優化（20%）：吞吐達到或優於參考數據 ±15%
- 創新性（10%）：提出管道或序列化優化（如 Span、Pipe、Binary）

------------------------------------------------------------

## Case #2: AppDomain 停用後的隔離替代方案遷移

### Problem Statement（問題陳述）
- 業務場景：原系統以 AppDomain 作為隔離單位以容納多團隊任務，計畫遷移至 .NET Core 以提升效能與跨平台維運，但 .NET Core 已移除 AppDomain。
- 技術挑戰：維持與 AppDomain 類似的安全隔離，避免靜態狀態污染與未捕捉例外影響，且要兼顧效能。
- 影響範圍：遷移風險導致平台不穩定；若僅 InProcess/Thread 替代，將失去隔離。
- 複雜度評級：中高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. .NET Core 官方移除 AppDomain（建議改用 Process/Container）。
  2. 原以 AppDomain 隔離靜態狀態的做法不再可用。
  3. 不同任務共用相同進程將產生污染與耦合。
- 深層原因：
  - 架構層面：以 CLR 內部機制（AppDomain）耦合隔離，與未來 Runtime 發展相悖。
  - 技術層面：動態載入、Assembly 隔離需改以 AssemblyLoadContext + Process。
  - 流程層面：缺少遷移時的基準比較與回歸驗證。

### Solution Design（解決方案設計）
- 解決策略：以 Process 作為隔離單位，並以 AssemblyLoadContext 處理必要動態載入。建置簡單 IPC（STDIO + Base64），利用 Process Pool 彌補啟動成本。以實測證明「Process(.NET Core) ≥ AppDomain(.NET Fx)」。

**實施步驟**：
1. 等價行為驗證
   - 實作細節：以 AppDomain 展示 static field 隔離（543 vs 0）與 Process 等效。
   - 所需資源：.NET Fx 範例程式。
   - 預估時間：1 小時
2. 效能基準對比
   - 實作細節：比較 AppDomain(.NET Fx) 與 Process(.NET Core) 任務吞吐。
   - 所需資源：HelloTask（SHA512）、Stopwatch。
   - 預估時間：2 小時
3. 遷移與替代
   - 實作細節：以 Process 包裝任務執行，建立 Worker 抽象層。
   - 所需資源：ProcessStartInfo、STDIO。
   - 預估時間：1 天

**關鍵程式碼/設定**：
```csharp
// AppDomain 靜態狀態隔離示範
AppDomainProgram.InitCount = 543;
AppDomainProgram.Main(null);
var iso = AppDomain.CreateDomain("demo");
iso.ExecuteAssemblyByName(typeof(AppDomainProgram).Assembly.FullName);
// 輸出示例：543（原域）、0（新域）
```

實際案例：
- 實作環境：.NET Fx 4.7.2、.NET Core 3.1
- 實測數據（有負載 1KB / BLOB）：
  - AppDomain（.NET Fx）：10822 tasks/sec
  - Process（.NET Core）：21322 tasks/sec
  - 提升幅度：約 +97%

Learning Points
- 核心知識點：AppDomain 與 Process 隔離等價性、官方遷移建議（AssemblyLoadContext）
- 技能要求：熟悉 .NET 兩代差異與替代 API
- 延伸思考：以 Container/Pod 作為更強隔離是否必要？（視維運成本而定）

Practice Exercise
- 基礎練習：完成 AppDomain 隔離示範（30 分）
- 進階練習：以 Process 重製相同隔離行為並比較吞吐（2 小時）
- 專案練習：將一個現有 AppDomain 任務改為 Process 外掛（8 小時）

Assessment Criteria
- 功能完整性（40%）：隔離行為等效
- 程式碼品質（30%）：清晰抽象，低耦合
- 效能優化（20%）：吞吐≥AppDomain 版本 ±10%
- 創新性（10%）：動態載入策略優化

------------------------------------------------------------

## Case #3: 啟動成本量化：隔離環境啟動速率基準測試

### Problem Statement（問題陳述）
- 業務場景：平台需調度大量短任務，若每次執行都新建隔離環境，啟動延遲將累積成瓶頸。
- 技術挑戰：量化 InProcess/Thread/AppDomain/Process 啟動成本，作為 Pool 設計與選型依據。
- 影響範圍：錯估啟動成本將導致架構設計錯誤（如不必要的動態啟動、過度服務化）。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Process 建立昂貴（OS 層級），AppDomain 其次。
  2. 不同 Runtime（.NET Fx/Core）有顯著差異。
  3. 啟動成本常被忽略（只看執行速度）。
- 深層原因：
  - 架構層面：未以測試數據做決策。
  - 技術層面：未了解 CLR/OS 啟動流程差異。
  - 流程層面：缺乏標準化 Benchmark 工具鏈。

### Solution Design
- 解決策略：實作空 Main()，以 for 100 次建立/卸載環境（AppDomain/Process）測每秒啟動次數，分別在 .NET Fx 與 .NET Core 驗證。

**實施步驟**：
1. 測試程式準備
   - 實作細節：空 Main()、for 100 次、Stopwatch 計算 run/sec。
   - 資源：.NET Fx/Core 專案各一。
   - 時間：1 小時
2. 多模式測試
   - 實作細節：InProcess、Thread、AppDomain、Process（Fx/Core）。
   - 資源：ProcessStartInfo。
   - 時間：1 小時
3. 結果解讀
   - 實作細節：圖表化，輸出結論（Process Pool 必要性）。
   - 時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
for (int i=0; i<100; i++) {
  var p = Process.Start(new ProcessStartInfo {
    FileName = "Host.exe", UseShellExecute=false
  });
  p.WaitForExit();
}
```

實際案例（每秒啟動次數 run/sec）：
- .NET Fx Host：
  - AppDomain：333.33
  - Process (.NET Fx)：11.76
  - Process (.NET Core)：12.66
- .NET Core Host：
  - Process (.NET Fx)：31.25
  - Process (.NET Core)：23.26

Learning Points
- 核心知識點：啟動成本 >> 任務成本 ⇒ 必須 Pool 化
- 技能要求：基準測試、誤差控制
- 延伸思考：Lazy Warm-up、預熱池、冷啟動策略

Practice Exercise
- 基礎：重現 run/sec 測試（30 分）
- 進階：加入 GC 設定、單/多核心對比（2 小時）
- 專案：撰寫自動化基準框架（8 小時）

Assessment Criteria
- 功能（40%）：測到穩定結果
- 品質（30%）：結果可重現有統計說明
- 效能（20%）：提出池化策略建議
- 創新（10%）：自動化分析/圖表

------------------------------------------------------------

## Case #4: 跨隔離的任務吞吐比較與傳參策略

### Problem Statement（問題陳述）
- 業務場景：HelloTask（SHA512 計算）需在不同隔離機制下執行，評估跨邊界傳參（VALUE vs BLOB）對吞吐的影響。
- 技術挑戰：Marshal/序列化/I/O 成本對吞吐影響顯著，需以數據決策。
- 影響範圍：資料傳輸策略錯誤將拖累整體吞吐。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. AppDomain 需要 MarshalByRefObject，Process 需要 I/O 序列化。
  2. VALUE 與 BLOB 序列化開銷不同。
  3. .NET Core 密碼學/記憶體優化顯著影響計算效能。
- 深層原因：
  - 架構層面：未抽象出 Worker 封裝與測試框架。
  - 技術層面：對跨邊界資料流缺乏基準。
  - 流程層面：缺少模式化測試（有負載/空轉）。

### Solution Design
- 解決策略：以抽象 Worker + HelloTask（1KB/1MB），在 InProcess/AppDomain/Process 下測 VALUE/BLOB 模式，分析不同 Runtime 效能。

**實施步驟**：
1. 任務與抽象層
   - 實作細節：HelloTask + HelloWorkerBase/HelloTaskResult。
   - 資源：SHA512、BlockingCollection。
   - 時間：2 小時
2. 不同模式實測
   - 實作細節：VALUE/BLOB（BASE64）兩模式，1KB 與 1MB。
   - 資源：Stopwatch。
   - 時間：2 小時
3. 分析與建議
   - 實作細節：建議 BLOB 為預設（簡化與通用性）。
   - 時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
public class HelloTask : MarshalByRefObject {
  static Random _rnd = new Random();
  static HashAlgorithm _ha = HashAlgorithm.Create("SHA512");
  public string DoTask(byte[] buffer) {
    _rnd.NextBytes(buffer);
    return Convert.ToBase64String(_ha.ComputeHash(buffer));
  }
}
```

實測數據（節錄）：
- 有負載 1KB（.NET Core Host + Process + BLOB）：25575 tasks/sec
- 有負載 1KB（.NET Core Host + Process + VALUE）：29240 tasks/sec（VALUE 稍優）
- 無負載（.NET Core Host + Process + VALUE）：52631 vs BLOB：37037（VALUE 優 29.5%）
- 結論：在多數實務下偏好 BLOB（通用、與既有儲存系統解耦）；計算量大時差異更小。

Learning Points
- 核心知識點：傳參策略與吞吐關聯、.NET Core 密集計算效能
- 技能要求：可重現的吞吐測試
- 延伸思考：以 Shared Storage 只傳 PK 的混合策略

Practice Exercise
- 基礎：實作 VALUE/BLOB 兩模式（30 分）
- 進階：加入 1MB 測試與比較（2 小時）
- 專案：以 Redis/DB 只傳 PK 的混合管線（8 小時）

Assessment Criteria
- 功能（40%）：兩模式皆可運作
- 品質（30%）：測試框架清晰
- 效能（20%）：數據解讀合理
- 創新（10%）：提出混合策略

------------------------------------------------------------

## Case #5: Worker 抽象與同步模型（不依賴 async/await）

### Problem Statement（問題陳述）
- 業務場景：平台需提供統一的 Queue/Result API，讓任務像本地函式般易用，並可精準控制執行緒。
- 技術挑戰：不依賴 Task-based async/await，仍要提供阻塞/通知與結果傳回。
- 影響範圍：抽象不當導致耦合與測試困難。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 需要外部可等待（WaitHandle）以控制完成時機。
  2. 不同隔離實作需同一抽象介面。
  3. 任務結果需安全回傳（避免 race）。
- 深層原因：
  - 架構層面：需要 Producer-Consumer 標準化模型。
  - 技術層面：同步原語使用（ManualResetEventSlim）。
  - 流程層面：測試/比較不同 Worker 得一致方法。

### Solution Design
- 解決策略：定義 HelloWorkerBase 抽象類與 HelloTaskResult（內含 ManualResetEventSlim），實作 InProcess/AppDomain/Process/ProcessPool 多個 Worker。

**實施步驟**：
1. 抽象與結果模型
   - 實作細節：QueueTask(int|byte[]) → HelloTaskResult（Wait/ReturnValue）。
   - 資源：ManualResetEventSlim。
   - 時間：1 小時
2. 範例使用
   - 實作細節：Queue→Wait.Wait()→讀取 ReturnValue。
   - 資源：Console App。
   - 時間：0.5 小時
3. 多實作套件化
   - 實作細節：InProcessWorker、SingleAppDomainWorker、SingleProcessWorker、ProcessPoolWorker。
   - 時間：1 天

**關鍵程式碼/設定**：
```csharp
public abstract class HelloWorkerBase {
  public class HelloTaskResult {
    public string ReturnValue;
    public readonly ManualResetEventSlim Wait = new ManualResetEventSlim(false);
  }
  public abstract HelloTaskResult QueueTask(byte[] buffer);
}
```

實測數據（空轉 InProcess 破表、作為對照組）：InProcessWorker：∞ tasks/sec（顯示抽象開銷極低）

Learning Points
- 核心知識點：自建同步模型、避免過早依賴 Task/async 隱藏行為
- 技能要求：同步原語正確使用
- 延伸思考：可再包裝成 Task/async/await

Practice Exercise
- 基礎：以手工 Wait/Set 完成一輪任務（30 分）
- 進階：將結果包裝成 Task（2 小時）
- 專案：在抽象層上替換不同 Worker 實作（8 小時）

Assessment Criteria
- 功能（40%）：阻塞/通知可用
- 品質（30%）：Race-free、線程安全
- 效能（20%）：低額外延遲
- 創新（10%）：異步封裝品質

------------------------------------------------------------

## Case #6: 單一 Process Worker（VALUE 模式）IPC 實作

### Problem Statement（問題陳述）
- 業務場景：需最小代價打通跨進程通道，傳遞小型參數（int/小字串），以便快速落地跨進程任務。
- 技術挑戰：無共享記憶體，必須透過 I/O 管道。
- 影響範圍：通道不穩將導致整體不可用。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Process 間記憶體隔離，需用 STDIO/Pipe/Socket。
  2. VALUE 模式最易落地，但仍需處理阻塞與錯誤。
  3. 需確保結果準確回傳與錯誤傳播。
- 深層原因：
  - 架構層面：先以 MVP 驗證跨進程基本通訊。
  - 技術層面：STDIO 阻塞/行緩衝/關閉協定。
  - 流程層面：雙端協定約定。

### Solution Design
- 解決策略：重導向 STDIN/STDOUT，VALUE 模式單行協定（輸入 size、輸出結果字串），以 Reader/Writer 同步 I/O。

**實施步驟**：
1. 啟動與重導向
   - 實作細節：ProcessStartInfo、UseShellExecute=false、Redirect IO。
   - 時間：0.5 小時
2. 協定定義
   - 實作細節：寫入一行數字→讀一行 Base64 哈希。
   - 時間：0.5 小時
3. 關閉協定
   - 實作細節：關閉 STDIN 代表不再有任務，Worker 結束。
   - 時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
_writer.WriteLine(size.ToString());
string result = _reader.ReadLine();
// 子進程 while ((line=Console.ReadLine())!=null) { ... Console.WriteLine(hash); }
```

實測數據：
- 空轉（VALUE）：SingleProcessWorker 高達約 41493.78 tasks/sec（示例）
- 有負載（1KB，.NET Core Host）：約 29,240 tasks/sec（VALUE）

Learning Points
- 核心知識點：STDIO IPC、阻塞 I/O 協定
- 技能要求：錯誤處理與關閉協定
- 延伸思考：非同步 I/O、批次封包

Practice Exercise
- 基礎：完成 VALUE 模式 IPC（30 分）
- 進階：加入簡單錯誤回傳（2 小時）
- 專案：價值型任務批次處理（8 小時）

Assessment Criteria
- 功能（40%）：雙向通訊穩定
- 品質（30%）：關閉/錯誤處理妥善
- 效能（20%）：吞吐接近參考值
- 創新（10%）：批次/管道優化

------------------------------------------------------------

## Case #7: 單一 Process Worker（BLOB 模式）大物件傳輸

### Problem Statement（問題陳述）
- 業務場景：需跨進程傳遞較大資料（如 1KB~1MB buffer），利於自包含運算任務。
- 技術挑戰：二進位資料需轉文本通道，序列化與編碼成本與可靠性需平衡。
- 影響範圍：資料錯誤/截斷將造成任務失敗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. STDIO 通常以行文本傳輸，需 Base64 編碼。
  2. 大物件序列化成本不可忽略。
  3. 子進程需解碼再計算。
- 深層原因：
  - 架構層面：資料傳遞 vs 只傳鍵值的取捨。
  - 技術層面：Base64 編解碼效能。
  - 流程層面：協定版本與相容性。

### Solution Design
- 解決策略：子進程以 BASE64 模式運作：讀字串→Base64 解碼→計算→回寫字串。主進程將 byte[] 轉 Base64 並寫入。

**實施步驟**：
1. 協定擴充
   - 實作細節：Process 參數指定 "BASE64"；子進程 switch 模式。
   - 時間：0.5 小時
2. 編碼解碼
   - 實作細節：Convert.To/FromBase64String。
   - 時間：0.5 小時
3. 吞吐測試
   - 實作細節：1KB/1MB 對比 VALUE。
   - 時間：1 小時

**關鍵程式碼/設定**：
```csharp
// 子進程 BASE64 模式
while ((line = Console.ReadLine()) != null) {
  byte[] buffer = Convert.FromBase64String(line);
  Console.WriteLine((new HelloTask()).DoTask(buffer));
}
```

實測數據：
- 有負載（1KB，.NET Core Host + Process + BLOB）：25575 tasks/sec
- 無負載（.NET Core Host + Process + BLOB）：37037 tasks/sec

Learning Points
- 核心知識點：大物件傳輸的協定化處理
- 技能要求：可靠的編碼與錯誤處理
- 延伸思考：壓縮、分塊、二進位管道

Practice Exercise
- 基礎：完成 BASE64 模式 IPC（30 分）
- 進階：比較 1KB/1MB 吞吐差異（2 小時）
- 專案：以 BLOB 模式串接影像/檔案任務（8 小時）

Assessment Criteria
- 功能（40%）：大物件傳遞正確
- 品質（30%）：錯誤/超時保護
- 效能（20%）：可達參考值
- 創新（10%）：管道/壓縮優化

------------------------------------------------------------

## Case #8: Process Pool 編排（Min/Max/Idle Timeout + 自動擴縮）

### Problem Statement（問題陳述）
- 業務場景：Process 啟動昂貴（每秒僅 ~23 次），任務執行吞吐極高（每秒 ~37037），需要以 Pool 攤銷啟動成本並自動擴縮。
- 技術挑戰：如何在任務到達時即時擴容、閒置時回收，並避免震盪與爭用。
- 影響範圍：影響整體吞吐與資源成本。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 啟動成本與任務成本差距高達 ~1600 倍。
  2. Process 常駐占用記憶體。
  3. 任務到達不均勻，需快速調節。
- 深層原因：
  - 架構層面：缺乏 Pool 編排策略（Min/Max/Idle）。
  - 技術層面：並發與隊列控制、避免競態。
  - 流程層面：缺乏擴縮可觀測性。

### Solution Design
- 解決策略：以 BlockingCollection 作為任務隊列；每個 Process 對應一個管理 Thread；實作 TryIncrease/ShouldDecrease 與 Keep-Alive；Stop() 等待所有任務完成。

**實施步驟**：
1. Pool 參數定義
   - 實作細節：_min/_max/_idleTimeout/queue size。
   - 時間：0.5 小時
2. ProcessHandler
   - 實作細節：循環 TryTake(timeout)、空轉→Keep-Alive/回收決策。
   - 時間：1 小時
3. 併發保護
   - 實作細節：_syncroot 鎖、狀態計數。
   - 時間：1 小時
4. Stop 等候收斂
   - 實作細節：CompleteAdding + AutoResetEvent。
   - 時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
private bool TryIncreaseProcess() {
  lock (_syncroot) {
    if (_total_created_process_count >= _max_pool_size) return false;
    if (_total_created_process_count > _total_working_process_count) return false;
    if (_queue.Count == 0 || _queue.IsCompleted) return false;
  }
  new Thread(ProcessHandler).Start();
  return true;
}

private bool ShouldDecreaseProcess() {
  lock (_syncroot) {
    if (_queue.Count > 0) return false;
    if (_total_created_process_count <= _min_pool_size) return false;
  }
  return true;
}
```

實測數據：
- 1KB 有負載（.NET Core）：
  - 單 Process：26385 tasks/sec → Process Pool：58823（+123%）
- 1MB 有負載（.NET Core）：
  - 單 Process：55.13 → Process Pool：183.90（+233%）
- 1MB 有負載（.NET Fx）：
  - 單 Process：40.98 → Process Pool：168.88（+312%）

Learning Points
- 核心知識點：Pool 編排模式、Keep-Alive 與回收策略
- 技能要求：並發控制、阻塞佇列
- 延伸思考：可否以 PID 健康檢查與熔斷機制增穩

Practice Exercise
- 基礎：實作 Min/Max/Idle 的 ProcessPoolWorker（30 分）
- 進階：對比 1KB/1MB 吞吐（2 小時）
- 專案：整合簡易監控與自動化擴縮日誌（8 小時）

Assessment Criteria
- 功能（40%）：可自動擴縮/回收
- 品質（30%）：無死鎖/競態
- 效能（20%）：提升達 2x 以上
- 創新（10%）：加入健康檢測/熔斷

------------------------------------------------------------

## Case #9: Idle 回收與記憶體/雲成本優化

### Problem Statement（問題陳述）
- 業務場景：大量 Process 長時間閒置造成 RAM 壓力與雲端成本上升，需要在流量低谷自動回收，保留最小存活數量。
- 技術挑戰：在保持可用性的同時回收閒置進程，避免冷啟動延遲。
- 影響範圍：硬體資源浪費、VM 數量過高。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 常駐 Process 內存開銷高。
  2. 任務到達呈現突發/間歇性。
  3. 未設定 Idle Timeout 與 Min Pool。
- 深層原因：
  - 架構層面：沒有資源生命週期策略。
  - 技術層面：缺乏 Keep-Alive/回收判斷。
  - 流程層面：缺少觀測與驗證。

### Solution Design
- 解決策略：設定 Min=2、Max=5、Idle=3s；在 10s 空閒期觀察自動回收與保留；恢復工作再擴容。

**實施步驟**：
1. Pool 參數設定
   - 實作細節：new ProcessPoolWorker(file, 2, 5, 3000)。
   - 時間：10 分
2. 測試流程
   - 實作細節：先投 100 任務→休眠 10s→再投 100 任務→Stop。
   - 時間：30 分
3. 行為觀測
   - 實作細節：加上 Started/KeepAlive/Stopped 日誌。
   - 時間：20 分

**關鍵程式碼/設定**：
```csharp
var worker = new ProcessPoolWorker(path, 2, 5, 3000);
// queue 100 tasks → delay 10s → queue another 100 → Stop()
```

實測數據（節錄）：
- 04:37:59 啟動 5 個 Process
- 04:38:04 閒置 5s 後，自動停止 3 個；2 個 KeepAlive
- 04:38:11 新任務到達，再啟動 3 個補齊
- 效益：低谷時釋放 RAM、峰值時快速恢復，CPU 使用率更集中於執行中 Process，減少 VM 需求（質化）

Learning Points
- 核心知識點：資源生命週期編排、可觀測性
- 技能要求：日誌化與行為驗證
- 延伸思考：Idle 多段策略（短/中/長）與分層回收

Practice Exercise
- 基礎：重現 KeepAlive/Stop 行為（30 分）
- 進階：繪製 Process 數量隨時間曲線（2 小時）
- 專案：加入 RAM 上限保護與自動退避（8 小時）

Assessment Criteria
- 功能（40%）：回收與保留行為正確
- 品質（30%）：日誌/觀測清楚
- 效能（20%）：低谷 RAM 下降、峰值吞吐穩定
- 創新（10%）：回收策略優化

------------------------------------------------------------

## Case #10: CPU Affinity 與 Process 優先權調校

### Problem Statement（問題陳述）
- 業務場景：Process Pool 擴張後 CPU 飽和，影響主控程序/其他服務相應性，需要用 OS 級調度維持系統可用。
- 技術挑戰：在充分吃滿 CPU 的前提下，確保高優任務先得到 CPU。
- 影響範圍：整機延遲、用戶體驗下降。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Pool 以等優先權競爭 CPU。
  2. 所有核心被背景任務佔滿。
  3. 未配置 Affinity 與 PriorityClass。
- 深層原因：
  - 架構層面：缺乏資源隔離策略（CPU）。
  - 技術層面：OS 調度器使用知識不足。
  - 流程層面：未建立「背景任務降級」規範。

### Solution Design
- 解決策略：設定 Process PriorityClass=BelowNormal，僅使用部分核心（ProcessorAffinity 指定位元）；讓其他服務以較高優先權與核心資源獲得即時性。

**實施步驟**：
1. 優先權設定
   - 實作細節：PriorityClass = BelowNormal。
   - 時間：10 分
2. Affinity 配置
   - 實作細節：ProcessorAffinity = new IntPtr(0b1110) → 綁定第 1,2,3 核。
   - 時間：10 分
3. 效果觀察
   - 實作細節：監看 CPU 圖（24 Process 只擠在 3 核），主程式流暢度回升。
   - 時間：20 分

**關鍵程式碼/設定**：
```csharp
_process.PriorityClass = ProcessPriorityClass.BelowNormal;
// 僅用第 1~3 核
_process.ProcessorAffinity = new IntPtr(0b1110);
```

實測數據（質化）：
- Pool 開到 24 個進程，觀察 CPU 僅 3 核滿載，其他核心留給主程式與系統，整體響應性改善。

Learning Points
- 核心知識點：OS 調度、優先權與核心關聯
- 技能要求：性能觀察與回饋調整
- 延伸思考：以 cgroups/Job Object 做資源硬限制

Practice Exercise
- 基礎：設定優先權與 Affinity（30 分）
- 進階：比較有/無設定的反應時間（2 小時）
- 專案：加入自動化調整策略（8 小時）

Assessment Criteria
- 功能（40%）：設定生效、行為可見
- 品質（30%）：無誤配置（如與超執行緒衝突）
- 效能（20%）：主程式響應改善
- 創新（10%）：自動化調優

------------------------------------------------------------

## Case #11: 傳參策略選型：VALUE vs BLOB 的數據化決策

### Problem Statement（問題陳述）
- 業務場景：部分任務僅需小型參數，部分則需傳遞大資料；需在開發簡易性與效能間取捨。
- 技術挑戰：VALUE/BLOB 差異取決於資料量與序列化成本。
- 影響範圍：錯誤選型導致吞吐下降或實現複雜。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. VALUE 不需 Base64，BLOB 需。
  2. 計算型任務差異較小，空轉型差異較大。
  3. .NET Core I/O/記憶體優化讓差異縮小。
- 深層原因：
  - 架構層面：多場景共存。
  - 技術層面：序列化成本對吞吐的非線性影響。
  - 流程層面：缺乏一體化測試/選型準則。

### Solution Design
- 解決策略：以數據導向：若資料小且頻繁，VALUE 略優；但為通用性與簡化整體實作，預設採 BLOB，特殊場景才切 VALUE。

**實施步驟**：
1. 兩模式實作
   - 實作細節：同一 IPC 管線支援 VALUE/BASE64。
   - 時間：1 小時
2. 吞吐測試
   - 實作細節：空轉/1KB/1MB 對比。
   - 時間：1 小時
3. 準則固化
   - 實作細節：BLOB 為預設、VALUE 為優化選配。
   - 時間：0.5 小時

**關鍵程式碼/設定**：
```csharp
// Host 側（兩模式）
if (mode=="VALUE") writer.WriteLine(size);
if (mode=="BASE64") writer.WriteLine(Convert.ToBase64String(buffer));
```

實測數據（.NET Core Host）：
- 無負載：VALUE 52631 > BLOB 37037（+29.5%）
- 有負載 1KB：VALUE 29240 > BLOB 25575（+12.5%）
- 結論：計算非空轉時差異縮小；通用情境優先 BLOB。

Learning Points
- 核心知識點：傳參策略與工作性質的對應
- 技能要求：效能測試與判讀
- 延伸思考：以外部儲存只傳 PK 的第三選項

Practice Exercise
- 基礎：兩模式切換測試（30 分）
- 進階：以 10 種大小測繪曲線（2 小時）
- 專案：引入策略選擇器（8 小時）

Assessment Criteria
- 功能（40%）：兩模式穩定
- 品質（30%）：策略可配置
- 效能（20%）：數據支撐結論
- 創新（10%）：自動化選擇

------------------------------------------------------------

## Case #12: 選擇 .NET Core 作為 Worker（負載端）以提升計算效能

### Problem Statement（問題陳述）
- 業務場景：SHA512 計算在 .NET Fx 與 .NET Core 表現差異巨大，影響整體吞吐。
- 技術挑戰：同源程式碼在不同 Runtime 的效能差，需以 .NET Core 提升計算密集任務效能。
- 影響範圍：任務處理時間、吞吐、成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. .NET Core 在記憶體/I/O/加密庫有顯著優化（Span 等）。
  2. .NET Fx 基礎類庫多年未大改。
- 深層原因：
  - 架構層面：遷移阻力使部分任務停留在 Fx。
  - 技術層面：Runtime 差異未被量化。
  - 流程層面：缺少雙 Runtime 並行編譯（.NET Standard）。

### Solution Design
- 解決策略：將計算端（Worker）優先遷移 .NET Core；共用 .NET Standard 程式庫，以條件編譯過渡。

**實施步驟**：
1. 程式庫抽離
   - 實作細節：HelloTask → .NET Standard 2.0。
   - 時間：1 小時
2. 雙目標編譯
   - 實作細節：Worker 編 .NET Core，Host 可 Fx/Core。
   - 時間：1 小時
3. 效能驗證
   - 實作細節：1KB/1MB 測試比較 Fx/Core Worker。
   - 時間：1 小時

**關鍵程式碼/設定**：
```xml
<!-- csproj 中加入 netstandard2.0 -->
<TargetFrameworks>netstandard2.0</TargetFrameworks>
```

實測數據（.NET Fx Host + 有負載 1KB / BLOB）：
- Process（.NET Fx）：9285 tasks/sec
- Process（.NET Core）：21322 tasks/sec
- 提升：約 +130%（文中敘述「差了 230%」的量級差異）

Learning Points
- 核心知識點：Runtime 對計算效能的影響
- 技能要求：多目標編譯與相容性
- 延伸思考：向 .NET 7/8 遷移的進一步收益

Practice Exercise
- 基礎：將任務程式庫抽到 .NET Standard（30 分）
- 進階：雙 Runtime Worker 對比（2 小時）
- 專案：完成 Worker 全面遷移 .NET Core（8 小時）

Assessment Criteria
- 功能（40%）：兩端相容
- 品質（30%）：清晰目標設定與條件編譯
- 效能（20%）：Core 端顯著優於 Fx
- 創新（10%）：剖析瓶頸

------------------------------------------------------------

## Case #13: 選擇 .NET Core 作為 Host（管控端）以提升啟動與 I/O 表現

### Problem Statement（問題陳述）
- 業務場景：Host 端使用 .NET Core 時，Process 啟動速率與 I/O 表現均有提升，影響整體調度效率。
- 技術挑戰：在不變更 Worker 的前提下，Host 遷移帶來可觀收益。
- 影響範圍：冷/熱啟動、I/O 阻塞、調度延遲。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. .NET Core 對 I/O/流程控制優化（IAsyncEnumerable/Async Streams）。
  2. Process 啟動與管線操作在 Core 下更快。
- 深層原因：
  - 架構層面：Host 常被忽略，實則影響全局。
  - 技術層面：Runtime 對 Process API 的最佳化。
  - 流程層面：Host 遷移風險低、收益高。

### Solution Design
- 解決策略：優先將 Host 遷移 .NET Core，評估對現有 Worker 的兼容（Fx/Core 均可），測試啟動速率與吞吐提升。

**實施步驟**：
1. Host 遷移
   - 實作細節：將 Host 專案目標設為 netcoreapp3.1。
   - 時間：1 小時
2. 啟動速率測試
   - 實作細節：run/sec 比較 Fx Host vs Core Host。
   - 時間：1 小時
3. 吞吐對比
   - 實作細節：相同 Worker 下觀測差異。
   - 時間：1 小時

**關鍵程式碼/設定**：
```xml
<TargetFramework>netcoreapp3.1</TargetFramework>
```

實測數據：
- 啟動 run/sec（Host 換 Core）：
  - Process(.NET Fx) 提升至 31.25 run/sec（相較 Fx Host 約 +165%）
  - Process(.NET Core) 23.26 run/sec（相較 Fx Host +~84%）
- 吞吐（文中示例）：Process(.NET Core) 在 Core Host 下較 Fx Host 提升約 +19.95%

Learning Points
- 核心知識點：Host 層 runtime 對流程的影響
- 技能要求：遷移驗證與風險控制
- 延伸思考：Host 端非同步化與通道抽象

Practice Exercise
- 基礎：Host 端轉 Core（30 分）
- 進階：run/sec 對比與分析（2 小時）
- 專案：Host 管線改非同步化（8 小時）

Assessment Criteria
- 功能（40%）：Host 遷移成功
- 品質（30%）：相容性良好
- 效能（20%）：run/sec/吞吐有顯著提升
- 創新（10%）：IO 管線優化

------------------------------------------------------------

## Case #14: Process Pool 效益隨負載增加而提升（1KB vs 1MB）

### Problem Statement（問題陳述）
- 業務場景：當任務負載（資料量/計算量）增大，Pool 化帶來的效益明顯提升。
- 技術挑戰：量化不同負載下 Pool 相對於單 Process 的收益。
- 影響範圍：決定是否啟用/擴大 Pool 的關鍵依據。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 任務越重，啟動成本佔比越小。
  2. 多 Process 可更充分利用多核。
- 深層原因：
  - 架構層面：CPU-bound 任務利於橫向併行。
  - 技術層面：I/O/序列化成本被計算掩蓋。
  - 流程層面：需以曲線評估最佳 Pool 大小。

### Solution Design
- 解決策略：對比 1KB 與 1MB 情境下單 Process vs Process Pool，定量化收益曲線，作為擴容策略依據。

**實施步驟**：
1. 雙負載測試
   - 實作細節：1KB 與 1MB，BLOB 模式。
   - 時間：1 小時
2. 效益計算
   - 實作細節：計算提升倍數與最佳 Pool Size 區間。
   - 時間：1 小時
3. 策略產出
   - 實作細節：CPU-bound 場景預設啟用 Pool。
   - 時間：0.5 小時

**關鍵程式碼/設定**：
（同 Case #8 測試管線）

實測數據：
- 1KB（.NET Core）：26385 → 58823（+123%）
- 1MB（.NET Core）：55.13 → 183.90（+233%）
- 1MB（.NET Fx）：40.98 → 168.88（+312%）
- 結論：負載越重，Pool 化收益越高。

Learning Points
- 核心知識點：負載特性與併行收益
- 技能要求：基於數據的容量規劃
- 延伸思考：自動根據負載調整 Pool Size

Practice Exercise
- 基礎：重現 1KB/1MB 曲線（30 分）
- 進階：探索最佳 Pool Size（2 小時）
- 專案：根據實時負載自動調整 Pool 參數（8 小時）

Assessment Criteria
- 功能（40%）：曲線可重現
- 品質（30%）：策略清晰
- 效能（20%）：收益明顯
- 創新（10%）：自動化調參

------------------------------------------------------------

## Case #15: AppDomain vs Process 的性能反轉案例（驚喜觀察）

### Problem Statement（問題陳述）
- 業務場景：普遍直覺認為 AppDomain 比 Process 輕量，但在實測中多次出現 Process 反超 AppDomain 的情況。
- 技術挑戰：釐清何種組合下 Process 勝出，避免錯誤依賴過時技術。
- 影響範圍：錯誤認知影響選型與遷移時機。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. .NET Core 計算效能顯著提升，Process(.NET Core) 優勢大。
  2. AppDomain 僅在 .NET Fx 可用，無法享用 Core 優化。
- 深層原因：
  - 架構層面：平台策略變動（Core 為主）。
  - 技術層面：AppDomain Marshal/邊界開銷。
  - 流程層面：經驗主義 vs 實測數據。

### Solution Design
- 解決策略：以同任務/同參數，對比 AppDomain(.NET Fx) 與 Process(.NET Core) 在「無負載/有負載」雙情境下的吞吐。

**實施步驟**：
1. 準備與測試
   - 實作細節：HelloTask + 1KB + BLOB。
   - 時間：1 小時
2. 結果整理
   - 實作細節：表格化對比。
   - 時間：0.5 小時
3. 結論固化
   - 實作細節：以 Process 為主，AppDomain 僅保留概念。
   - 時間：0.5 小時

**關鍵程式碼/設定**：
（同 Case #4 的測試框架）

實測數據（.NET Fx Host, 有負載 1KB）：
- AppDomain：10822 tasks/sec
- Process (.NET Core)：21322 tasks/sec
- Process 勝出近 +97%

Learning Points
- 核心知識點：實測 > 直覺；平台演進帶來反直覺結果
- 技能要求：正確對比條件設計
- 延伸思考：何時 AppDomain 還有價值？（Fx 遺留場景）

Practice Exercise
- 基礎：完成對比（30 分）
- 進階：加入不同資料量測試（2 小時）
- 專案：撰寫選型報告（8 小時）

Assessment Criteria
- 功能（40%）：測試完整
- 品質（30%）：對比公平
- 效能（20%）：數據可信
- 創新（10%）：決策建議

------------------------------------------------------------

## Case #16: 以 BlockingCollection 建構生產者-消費者的穩定佇列

### Problem Statement（問題陳述）
- 業務場景：需要穩定的隊列緩衝與反壓（Backpressure），避免任務暴增時記憶體爆量或過度啟動。
- 技術挑戰：隊列需可阻塞、可完成（CompleteAdding），支援 Stop 時優雅收斂。
- 影響範圍：穩定性與關閉行為。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無上限隊列導致記憶體風險。
  2. 無阻塞機制，生產端無法退避。
  3. 無完成通知，消費端無法有序結束。
- 深層原因：
  - 架構層面：缺反壓設計。
  - 技術層面：同步原語使用不足。
  - 流程層面：關閉程序未設計。

### Solution Design
- 解決策略：以 BlockingCollection<(buffer, result)>(capacity) 作為核心隊列；Queue 滿則阻塞，Stop() 時 CompleteAdding，消費端迴圈檢查 IsCompleted 有序退出。

**實施步驟**：
1. 隊列建立
   - 實作細節：new BlockingCollection<...>(10)。
   - 時間：10 分
2. 反壓與關閉
   - 實作細節：Add/TryTake(timeout)、CompleteAdding/IsCompleted。
   - 時間：30 分
3. 驗證
   - 實作細節：壓力測試觀察阻塞與退出序。
   - 時間：1 小時

**關鍵程式碼/設定**：
```csharp
BlockingCollection<(byte[] buf, HelloTaskResult res)> _queue = new(10);
_queue.Add((buffer, result)); // 滿則阻塞
_queue.CompleteAdding();      // 通知不再新增
while (!_queue.IsCompleted) { _queue.TryTake(out var item, timeout); /*處理*/ }
```

實測數據：
- 在 Process Pool 基準測試中，穩定支撐 1KB/1MB 的高吞吐曲線，並保證 Stop 時有序收斂（參照 Case #8/9 的數據與日誌）

Learning Points
- 核心知識點：反壓、優雅關閉
- 技能要求：佇列與同步 API 熟悉
- 延伸思考：替換為 Channels 或 TPL Dataflow

Practice Exercise
- 基礎：建一個 10 容量阻塞隊列（30 分）
- 進階：加入 TryTake 超時與退避（2 小時）
- 專案：替換為 System.Threading.Channels（8 小時）

Assessment Criteria
- 功能（40%）：阻塞與完成正確
- 品質（30%）：無 Race
- 效能（20%）：高負載穩定
- 創新（10%）：替代方案比較

------------------------------------------------------------

## Case #17: 以日誌驗證 Process 生命週期與擴縮決策

### Problem Statement（問題陳述）
- 業務場景：需可視化 Process 的啟動/保活/回收，驗證擴縮決策是否如預期。
- 技術挑戰：缺少可觀測性導致排錯困難。
- 影響範圍：維運可用性、可信度。
- 複雜度評級：低中

### Root Cause Analysis
- 直接原因：
  1. 沒有生命週期日誌，行為黑盒。
  2. 擴縮決策缺佐證。
- 深層原因：
  - 架構層面：可觀測性不足。
  - 技術層面：缺關鍵點日誌。
  - 流程層面：無驗證流程。

### Solution Design
- 解決策略：在 ProcessHandler 的 Start/KeepAlive/Stop 皆打印時間戳與 PID，並以時間序分析決策正確性。

**實施步驟**：
1. 日誌點植入
   - 實作細節：Started/KeepAlive/Stopped。
   - 時間：20 分
2. 場景測試
   - 實作細節：加入 idle 期與再負載。
   - 時間：30 分
3. 分析報告
   - 實作細節：按時間序對應決策。
   - 時間：30 分

**關鍵程式碼/設定**：
```csharp
Console.WriteLine($"* {DateTime.Now} - Process [PID: {_process.Id}] Started.");
Console.WriteLine($"* {DateTime.Now} - Process [PID: {_process.Id}] Keep alive for this process.");
Console.WriteLine($"* {DateTime.Now} - Process [PID: {_process.Id}] Stopped.");
```

實測數據（節錄，見 Case #9）：
- 閒置 5 秒後按 Min Pool 保留 2，其他回收；新流量來時快速補齊

Learning Points
- 核心知識點：可觀測性是擴縮正確的保障
- 技能要求：日誌布局與時序分析
- 延伸思考：接入指標系統（Prometheus/Grafana）

Practice Exercise
- 基礎：加入 3 個日誌點（30 分）
- 進階：將日誌輸出為結構化 JSON（2 小時）
- 專案：繪製擴縮時序圖（8 小時）

Assessment Criteria
- 功能（40%）：日誌可讀
- 品質（30%）：結構化、可檢索
- 效能（20%）：低侵入
- 創新（10%）：指標化

------------------------------------------------------------

## Case #18: 以 Message Queue + Process Pool 替代 Serverless/Container 於特定限制場景

### Problem Statement（問題陳述）
- 業務場景：Serverless（冷啟動/DB 連線池）與 Container Orchestration（Windows 支援/低頻任務 Pod 浪費）不符現況，需要內建於 VM 的任務編排機制。
- 技術挑戰：在應用層實作細粒度 Job 調度，並保留 VM 級的彈性擴展。
- 影響範圍：穩定性、成本、人力維運分工。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. Serverless 冷啟動與 DB 連線池復用差。
  2. Windows Container 支援度/彈性有限。
  3. 任務顆粒度為 Job 而非 Service。
- 深層原因：
  - 架構層面：Infra 無法 100% 滿足需求。
  - 技術層面：需要應用層 Orchestration。
  - 流程層面：SRE/Dev 區分界線與協作。

### Solution Design
- 解決策略：以 MQ 投遞任務到單機 Process Pool，將「單機內 Pool 編排」與「以 VM 為單位的水平擴展（k8s/Auto Scaling）」分層處理，最大化彈性與成本效益。

**實施步驟**：
1. 應用層 Orchestration
   - 實作細節：Process Pool 對接 MQ、以 Job 為單位調度。
   - 時間：2 天
2. 基礎設施層擴展
   - 實作細節：以 VM/Pod 為單位做 Auto Scaling。
   - 時間：1 天
3. 成本觀測
   - 實作細節：觀察 RAM/CPU/VM 數量變化。
   - 時間：1 天

**關鍵程式碼/設定**：
（同 Case #8 的 Pool + MQ 取件邏輯即可）

實測數據（質化與量化綜合）：
- Pool 化後 CPU 使用率提高、記憶體不再成瓶頸（Case #9）
- 1MB 計算下 Process Pool 提升 233%~312%，可用更少 VM 達成目標吞吐

Learning Points
- 核心知識點：應用 vs 基礎設施的責任邊界
- 技能要求：分層設計、成本導向決策
- 延伸思考：長期可逐步 Containerize

Practice Exercise
- 基礎：以假 MQ 驗證取件與調度（30 分）
- 進階：加入 Auto Scaling 觸發條件模擬（2 小時）
- 專案：整合雲監控與擴容規則（8 小時）

Assessment Criteria
- 功能（40%）：調度穩定、可擴展
- 品質（30%）：清晰分層與責任界定
- 效能（20%）：吞吐/成本改善有據
- 創新（10%）：可演進路線

------------------------------------------------------------

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #5（Worker 抽象與同步）
  - Case #6（VALUE IPC）
  - Case #7（BLOB IPC）
  - Case #16（BlockingCollection 佇列）
  - Case #17（日誌可觀測性）
- 中級（需要一定基礎）
  - Case #3（啟動速率基準）
  - Case #4（吞吐與傳參）
  - Case #11（VALUE vs BLOB 選型）
  - Case #12（Worker 遷移 Core）
  - Case #13（Host 遷移 Core）
  - Case #15（AppDomain vs Process 反轉）
  - Case #14（負載與 Pool 效益曲線）
- 高級（需要深厚經驗）
  - Case #1（整體隔離與吞吐）
  - Case #2（AppDomain 替代遷移）
  - Case #8（Process Pool 編排）
  - Case #9（Idle 回收與成本）
  - Case #10（CPU 調校）
  - Case #18（應用層 Orchestration 與雲擴展）

2) 按技術領域分類
- 架構設計類
  - Case #1, #2, #14, #18
- 效能優化類
  - Case #3, #4, #8, #9, #10, #11, #12, #13, #15
- 整合開發類
  - Case #5, #6, #7, #16
- 除錯診斷類
  - Case #17
- 安全防護類
  - Case #1, #2（隔離即安全邊界的一部分）

3) 按學習目標分類
- 概念理解型
  - Case #1, #2, #15, #18
- 技能練習型
  - Case #5, #6, #7, #16, #17
- 問題解決型
  - Case #3, #4, #8, #9, #10, #11, #12, #13, #14
- 創新應用型
  - Case #8, #10, #18

案例關聯圖（學習路徑建議）
- 入門順序（基礎與通道）
  1) Case #5（抽象與同步）→
  2) Case #6（VALUE IPC）→
  3) Case #7（BLOB IPC）→
  4) Case #16（阻塞佇列）
- 基準與選型（數據導向）
  5) Case #3（啟動速率）→
  6) Case #4（吞吐與傳參）→
  7) Case #11（VALUE vs BLOB 準則）→
  8) Case #15（AppDomain vs Process 反轉）
- 遷移與效能（Runtime 策略）
  9) Case #12（Worker 用 Core）→
  10) Case #13（Host 用 Core）
- 編排與擴縮（核心能力）
  11) Case #8（Process Pool 編排）→
  12) Case #9（Idle 回收）→
  13) Case #10（CPU 調校）→
  14) Case #17（可觀測性）
- 架構落地與雲整合（全局）
  15) Case #1（整體隔離/吞吐）→
  16) Case #2（AppDomain 替代）→
  17) Case #14（負載 vs 效益）→
  18) Case #18（應用層 Orchestration + 雲擴展）

依賴關係摘要
- IPC 與抽象（Case #5-7, #16）為 Process Pool（Case #8）的前置。
- 基準測試（Case #3-4, #11, #15）是選型與調參的依據。
- Runtime 遷移（Case #12-13）對 Pool 效能有根本影響。
- 可觀測性（Case #17）是擴縮與成本優化（Case #9-10, #18）的保障。

完整學習路徑建議
- 先掌握 Worker 抽象與 IPC 基礎（Case #5-7, #16）
- 再以基準數據建立選型與傳參準則（Case #3-4, #11, #15）
- 完成 .NET Core 遷移的效能地基（Case #12-13）
- 進入 Process Pool 核心編排與擴縮（Case #8-10, #17）
- 最後落地到整體架構與雲擴展（Case #1-2, #14, #18）

以上 18 個案例均源自文章中的真實情境、程式碼與數據，可直接作為教學模組、實作演練與考核規準。