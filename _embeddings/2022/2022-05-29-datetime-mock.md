---
source_file: "_posts/2022/2022-05-29-datetime-mock.md"
generated_date: "2025-01-03 10:30:00 +0800"
version: "1.1"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# [架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用 - 生成內容

## Metadata

### 原始 Metadata

```yaml
layout: post
title: "[架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用"
categories:
- "系列文章: 架構師的修練"
tags: ["系列文章", "架構師的修練", "刻意練習", "UnitTest", "PoC"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2022-05-29-datetime-mock/2022-05-29-00-57-25.png
```

### 自動識別關鍵字
keywords:
  primary:
    - DateTime
    - Mock
    - PoC
    - 單元測試
    - 架構師修練
  secondary:
    - DateTimeUtil
    - 時間控制
    - 降維打擊
    - 微服務架構
    - 事件驅動

### 技術堆疊分析
tech_stack:
  languages:
    - C#
  frameworks:
    - .NET
    - ASP.NET Core
  tools:
    - Visual Studio
    - Microsoft Fakes
    - System.Timer
  platforms:
    - .NET Framework
    - Visual Studio Enterprise

### 參考資源
references:
  internal_links:
    - /2022/04/25/microservices16-api-implement/
    - /2022/03/25/microservices15-api-design/
    - /2016/10/10/microservice3/
    - /2018/03/25/interview01-transaction/
  external_links:
    - https://docs.microsoft.com/en-us/visualstudio/test/code-generation-compilation-and-naming-conventions-in-microsoft-fakes?view=vs-2022
    - https://methodpoet.com/unit-testing-datetime-now/
    - https://www.netsolutions.com/insights/proof-of-concept-PoC/
    - https://ani.gamer.com.tw/animeVideo.php?sn=29007
  mentioned_tools:
    - Microsoft Fakes
    - ShimsContext
    - System.Timer
    - Visual Studio Enterprise

### 內容特性
content_metrics:
  word_count: 4800
  reading_time: "24 分鐘"
  difficulty_level: "中級"
  content_type: "教學"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)

作者在本文中探討如何解決單元測試和概念驗證（PoC）中 DateTime.Now 難以控制的問題，並自行設計實作了 DateTimeUtil 工具類別。文章首先分析了 DateTime.Now 作為靜態屬性無法被正規手段替換的問題，接著評估了市面上常見的三種解決方案：自訂替代品、介面抽象化設計，以及 Microsoft Fakes 框架。作者最終選擇了 Ambient Context 方式，設計出能同時滿足單元測試固定時間需求和 PoC 時間流動需求的解決方案。這個 DateTimeUtil 不僅支援時間的快轉和跳躍，還提供跨日事件觸發機制，讓時間相關的業務邏輯能在測試和驗證過程中正確執行。作者進一步闡述了「降維打擊」的 PoC 概念，即透過降低問題複雜度的維度來專注於核心概念的驗證，這種方法在微服務架構設計中特別有效。

### 關鍵要點 (Key Points)

- DateTime.Now 靜態屬性無法透過正規手段替換，造成測試困難
- 市面上解決方案分為：自訂替代品、介面抽象化、Microsoft Fakes 三類
- DateTimeUtil 採用 Ambient Context 模式，支援時間控制和事件觸發
- PoC 應採用「降維打擊」策略，專注核心概念驗證
- 微服務架構設計可透過降維方式簡化複雜度

### DateTime.Now 的問題分析 (Section Summaries)

作者詳細說明了 DateTime.Now 作為靜態屬性所帶來的測試挑戰，指出由於其靜態連結特性，完全無法透過依賴注入、包裝器等正規手段進行替換。這個問題在需要精準控制時間的業務邏輯測試中特別明顯，例如系統需要在特定時間點執行排程任務時，測試就變得非常困難。作者進一步分析了 Google 搜尋結果中常見的三類解決方案，包括自訂替代品如 SystemTime.Now、透過 IDateTimeProvider 介面進行抽象化設計，以及使用 Microsoft Fakes 進行運行時攔截。每種方案都有其優缺點，但都無法完全滿足作者對於 PoC 場景的需求，特別是需要時間持續流動和事件觸發的情況。

### DateTimeUtil 介面設計 (Section Summaries)

作者採用 Ambient Context 方式設計了 DateTimeUtil 類別，提供單例模式的時間控制功能。設計包含靜態方法 Init() 用於初始化時間偏移量、Reset() 用於重置狀態，以及 Instance 屬性提供全域存取點。核心功能包括 Now 屬性用於取得當前控制時間、TimePass() 方法用於時間快轉，以及 RaiseDayPassEvent 事件用於跨日觸發。這個設計的關鍵特色是時間會隨著實際時間流動而變化，而非僅回傳固定時間，同時支援手動時間跳躍功能。事件機制確保在時間跨越日期分界線時能正確觸發相關業務邏輯，解決了排程任務在測試和驗證過程中的執行問題。作者特別強調不支援時間倒流，以避免資料一致性問題。

### 實作程式碼檢視 (Section Summaries)

作者展示了 DateTimeUtil 的完整實作，內部使用 _realtime_offset 記錄時間差異，以及 _last_check_event_time 追蹤事件觸發時間點。Now 屬性透過 DateTime.Now 加上偏移量計算當前時間，並在每次存取時檢查是否需要觸發跨日事件。TimePass() 方法調整時間偏移量並觸發相應事件，Seek_LastEventCheckTime() 負責檢查和觸發所有跨越的日期變更事件。作者提供了三個測試案例：TimePassTest 驗證基本時間控制功能，TimePassWithEventTest 測試事件觸發機制，RealtimeEventTest 驗證實際時間流動的事件觸發。實作中考慮了執行時間誤差問題，採用容忍範圍內的斷言判定，確保測試的穩定性。這個解決方案既滿足了單元測試的需求，也支援了 PoC 中時間相關的驗證場景。

### PoC 降維打擊策略 (Section Summaries)

作者闡述了「降維打擊」的 PoC 概念，即透過降低問題複雜度的維度來專注於核心概念驗證。在微服務架構設計中，這種方法特別有效，例如將分散式系統降維至多執行緒、將遠端程序呼叫降維至本地程序呼叫、將資料庫操作降維至記憶體集合操作。作者強調這種降維的前提是必須清楚理解真實維度與 PoC 維度之間的對應關係，並具備足夠的技術掌握能力。透過 C# 語言的 interface、LINQ、事件機制等特性，可以有效模擬複雜的分散式系統行為。作者分享了多篇過往文章作為 PoC 應用案例，涵蓋 API 設計、微服務基礎建設、架構面試題等主題。這種方法讓設計者能夠空出思考空間，專注於解決核心問題，避免被技術實作細節分散注意力，是架構師在面對複雜系統設計時的重要思考工具。

## 問答集 (Q&A Pairs)

### Q1. 為什麼 DateTime.Now 在單元測試中難以控制？

Q: DateTime.Now 在單元測試和 PoC 中會遇到什麼問題？為什麼難以控制？
A: DateTime.Now 是靜態屬性，具有靜態連結特性，完全無法透過依賴注入、包裝器等正規手段進行替換。由於它會傳回系統目前的時間，這很難預測執行時間，導致依賴 DateTime.Now 的程式碼難以進行精準測試。例如在測試排程邏輯時，我們無法控制測試執行的確切時間點，使得斷言變得困難或不可靠。

### Q2. 市面上有哪些解決 DateTime.Now Mock 的方案？

Q: 目前常見的 DateTime.Now Mock 解決方案有哪些？各有什麼特點？
A: 主要有三類解決方案：1) 自訂替代品，如 SystemTime.Now，單純提供可控制的替代品；2) 介面抽象化設計，如 IDateTimeProvider，透過依賴注入實現可抽換性；3) Microsoft Fakes 框架，透過運行時重新編寫技術攔截原始呼叫。Microsoft Fakes 看似最理想但需要 Visual Studio Enterprise 版本，且會影響效能，主要適用於單元測試場景。

### Q3. DateTimeUtil 的設計理念是什麼？

Q: DateTimeUtil 採用什麼設計模式？主要解決什麼問題？
A: DateTimeUtil 採用 Ambient Context 模式結合單例模式設計，提供全域存取的時間控制功能。主要解決兩個問題：1) 單元測試需要固定時間點進行斷言；2) PoC 需要時間能夠流動並支援時間快轉。設計特色包括時間會隨實際時間流動、支援手動時間跳躍、提供跨日事件觸發機制，讓時間相關的業務邏輯在測試和驗證過程中能正確執行。

### Q4. DateTimeUtil 如何處理事件觸發機制？

Q: DateTimeUtil 的 RaiseDayPassEvent 事件是如何運作的？什麼時候會被觸發？
A: RaiseDayPassEvent 事件會在時間跨越日期分界線時觸發，用於處理需要定期執行的業務邏輯。觸發時機有兩個：1) 呼叫 TimePass() 進行時間跳躍時；2) 透過 DateTimeUtil.Instance.Now 存取目前時間時。系統會追蹤 _last_check_event_time，檢查從上次到現在是否跨越了日期邊界，若有則觸發相應的事件。這個機制確保在 PoC 過程中，時間跳躍不會遺漏應該執行的定期任務。

### Q5. 什麼是 PoC 的「降維打擊」策略？

Q: 作者提到的「降維打擊」PoC 策略是什麼意思？如何應用？
A: 「降維打擊」是指將複雜問題的維度降低一個層級來解決的策略。例如：將分散式系統降維至多執行緒、將遠端程序呼叫降維至本地程序呼叫、將資料庫操作降維至記憶體集合操作、將訊息佇列降維至 C# 事件機制。這種方法讓開發者能專注於核心概念驗證，省略大量技術實作細節。前提是必須清楚理解真實維度與 PoC 維度的對應關係，並具備足夠的技術掌握能力。

### Q6. TimePass() 方法的設計考量是什麼？

Q: DateTimeUtil 的 TimePass() 方法為什麼不支援時間倒流？有什麼替代方案？
A: TimePass() 不支援時間倒流是為了避免資料一致性問題，如已觸發的事件是否需要回復、資料狀態是否需要還原等複雜情況。如果需要「倒流」效果，唯一方式是透過 Reset() 重新初始化整個系統，然後用 Init() 設定新的起始時間。這種設計明確告知使用者這是「重新開始」而非「時光倒流」，使用者需要有清除或還原環境的配套準備。

### Q7. DateTimeUtil 在實際專案中如何應用？

Q: DateTimeUtil 除了單元測試外，在實際專案中還有什麼應用場景？
A: 作者在實際專案的原型設計中直接整合了 DateTimeUtil 的 UI 控制功能，在後台右上角加入顯示目前系統時間的標籤，以及 TimePass()、GoNextHours()、GoNextDays() 等操作按鈕。這讓展示過程能夠即時快轉時間，驗證時間相關的業務邏輯流程。特別適用於需要展示長時間跨度的系統行為，如月結報表生成、定期任務執行等場景，讓複雜的時間邏輯能夠「眼見為憑」地展示給利害關係人。

## 解決方案 (Solutions)

### P1. DateTime.Now 靜態屬性測試困難

Problem: DateTime.Now 作為靜態屬性無法在單元測試中被 Mock 或替換，導致時間相關的業務邏輯測試變得困難或不可靠。

Root Cause: DateTime.Now 採用靜態連結設計，編譯時就確定了呼叫目標，無法透過依賴注入、包裝器等設計模式進行抽換。靜態屬性的設計初衷是提供全域存取的便利性，但這也犧牲了可測試性。

Solution: 設計 DateTimeUtil 工具類別，採用 Ambient Context 模式提供可控制的時間來源。使用單例模式確保全域一致性，透過 Init() 方法設定時間偏移量，讓測試能夠控制時間起點。

Example: 
```csharp
[TestInitialize]
public void Init()
{
    DateTimeUtil.Init(new DateTime(2022, 05, 01, 00, 00, 00));
    // 原本的測試邏輯，改用 DateTimeUtil.Instance.Now 取代 DateTime.Now
}
```

### P2. PoC 場景需要時間流動和快轉功能

Problem: 傳統的 DateTime Mock 方案只提供固定時間，無法滿足 PoC 場景中需要時間持續流動和支援時間快轉的需求。

Root Cause: 單元測試著重於固定時間點的精準斷言，但 PoC 需要模擬真實的時間流動來驗證系統行為，特別是時間相關的業務邏輯如排程任務、到期處理等。

Solution: 在 DateTimeUtil 中使用時間偏移量而非固定時間值，讓時間能隨實際時間流動。提供 TimePass() 方法支援時間快轉，並整合事件觸發機制處理跨日邏輯。

Example:
```csharp
DateTimeUtil.Init(new DateTime(2002, 10, 26, 12, 0, 0));
DateTimeUtil.Instance.TimePass(TimeSpan.FromDays(30)); // 快轉30天
var currentTime = DateTimeUtil.Instance.Now; // 取得快轉後的時間
```

### P3. 時間跳躍時遺漏定期任務執行

Problem: 在 PoC 測試中進行大幅度時間跳躍時，可能遺漏應該在跳躍期間執行的定期任務或排程邏輯。

Root Cause: 傳統的時間模擬只關注終點時間，忽略了跳躍過程中應該觸發的事件。在真實系統中，這些定期任務會在特定時間點自動執行，但在模擬環境中容易被忽略。

Solution: 設計 RaiseDayPassEvent 事件機制，在 TimePass() 執行過程中自動檢查跨越的日期，並為每個跨越的日期觸發事件。透過 Seek_LastEventCheckTime() 方法確保不遺漏任何應該觸發的事件。

Example:
```csharp
DateTimeUtil.Instance.RaiseDayPassEvent += (sender, args) => {
    // 處理每日應執行的業務邏輯
    Console.WriteLine($"執行日期: {args.OccurTime}");
};
DateTimeUtil.Instance.TimePass(TimeSpan.FromDays(35)); // 會觸發35次事件
```

### P4. 複雜系統架構的概念驗證困難

Problem: 微服務等複雜架構的概念驗證需要涉及多個技術領域，導致 PoC 成本過高且難以專注於核心概念。

Root Cause: 真實的分散式系統涉及網路通訊、基礎設施、DevOps、安全性等多個面向，要完整實現所有細節需要大量時間和專業知識，容易偏離核心設計概念的驗證目標。

Solution: 採用「降維打擊」策略，將複雜的分散式問題降維到較簡單的層級進行驗證。例如用多執行緒模擬分散式節點、用本地函式呼叫模擬遠端 API、用記憶體集合模擬資料庫操作。

Example:
```csharp
// 將分散式服務呼叫降維為介面呼叫
interface IOrderService { Task<OrderResult> ProcessOrder(OrderRequest request); }
interface IPaymentService { Task<PaymentResult> ProcessPayment(PaymentRequest request); }

// 用多執行緒模擬分散式並行處理
var tasks = new List<Task>();
for(int i = 0; i < 10; i++) {
    tasks.Add(Task.Run(() => orderService.ProcessOrder(request)));
}
await Task.WhenAll(tasks);
```

### P5. 測試環境時間相關斷言的穩定性問題

Problem: 在測試環境中，由於執行時間的不確定性，時間相關的斷言容易因為微小的時間差異而失敗。

Root Cause: 程式執行會消耗時間，且在不同的硬體環境或系統負載下執行時間會有差異，導致基於精確時間的斷言變得不穩定。在除錯模式下單步執行更會放大這個問題。

Solution: 在斷言中引入容忍範圍概念，允許合理的時間誤差。設定適當的容忍時間範圍（如1秒），讓測試更穩定可靠。同時在設計上避免對精確時間的依賴。

Example:
```csharp
TimeSpan tolerance = TimeSpan.FromSeconds(1);
var expectedTime = new DateTime(2002, 10, 26, 12, 0, 0);
var actualTime = DateTimeUtil.Instance.Now;
Assert.IsTrue(Math.Abs((actualTime - expectedTime).TotalSeconds) < tolerance.TotalSeconds);
```

## 版本異動紀錄

### v1.1 (2025-01-03)
- 修正摘要格式，改用第三人稱敘述，加入生成工具資訊
- 完善技術堆疊分析和參考資源連結
- 調整問答集內容，使其更貼近實際應用場景

### v1.0 (2025-01-03)
- 初始版本
