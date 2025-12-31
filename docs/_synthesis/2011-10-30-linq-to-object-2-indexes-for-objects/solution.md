---
layout: synthesis
title: "LINQ to Object #2, Indexes for Objects"
synthesis_type: solution
source_post: /2011/10/30/linq-to-object-2-indexes-for-objects/
redirect_from:
  - /2011/10/30/linq-to-object-2-indexes-for-objects/solution/
postid: 2011-10-30-linq-to-object-2-indexes-for-objects
---

以下內容基於你提供的文章，聚焦 LINQ to Objects 在大型集合上的等值查詢與索引化的實戰，萃取並擴充成具教學價值的 16 個案例。每個案例均包含問題、根因、方案、關鍵程式碼、實測指標描述、學習要點、練習與評估標準，方便課堂實作、專案演練與能力評估。

----------------------------------------

## Case #1: 百萬筆非索引 List 的 LINQ 等值查詢過慢

### Problem Statement（問題陳述）
- 業務場景：批次任務或報表系統將 1,000,000 筆 Foo 資料（含 Text 與 Number 欄位）載入記憶體，開發者以 LINQ to Objects 即時查詢單一鍵值（例如 Text == "888365"）並投影 select x.Text。此需求在系統啟動後會被頻繁觸發。
- 技術挑戰：對 List<Foo> 使用 where x.Text == "888365" 需要逐筆比對，隨資料量成長延遲顯著增加。
- 影響範圍：查詢延遲上升、CPU 消耗高、服務端吞吐降低，造成使用者體感卡頓。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. List<T> 無索引：LINQ to Objects 的 Where 針對 IEnumerable<T> 為逐筆掃描，時間複雜度 O(n)。
  2. 高資料量：1,000,000 筆資料使得單次掃描成本高。
  3. 熱點查詢：相同條件多次查詢重複支付掃描成本。
- 深層原因：
  - 架構層面：未將「查詢模式」納入記憶體資料結構設計（缺索引）。
  - 技術層面：只用 List<T> 與標準 Enumerable.Where，未引入適配 in-memory 索引的工具。
  - 流程層面：性能基準與資料量放大測試不足。

### Solution Design（解決方案設計）
- 解決策略：導入物件索引化資料結構，將等值查詢從 O(n) 降為 O(1)～O(log n)。可採用 i4o（IndexableCollection + CreateIndexFor）或自訂字典索引。本文先以 i4o 最小侵入導入，保留現有 LINQ 語法。

- 實施步驟：
  1. 建立可索引集合
     - 實作細節：將 List<Foo> 轉為 IndexableCollection，建立 Text 欄位索引。
     - 所需資源：i4o 函式庫、.NET、C#。
     - 預估時間：0.5 小時。
  2. 使用相同 LINQ 查詢
     - 實作細節：維持 from/where/select 語法不變。
     - 所需資源：Stopwatch 量測，驗證快慢差異。
     - 預估時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
// 建資料
List<Foo> list1 = new List<Foo>();
list1.AddRange(RndFooSeq(8072, 1_000_000));

// 轉為可索引集合並建立 Text 索引
var list3 = list1.ToIndexableCollection<Foo>();
list3.CreateIndexFor(i => i.Text);

// 查詢
var result = (from x in list3 where x.Text == "888365" select x.Text).ToList();
```

- 實際案例：文章以 list1（無索引）、list2（自訂字典索引）、list3（i4o）三組對照，使用 Stopwatch 輸出 Build Index time 與 Query time。
- 實作環境：.NET/C#、LINQ to Objects、i4o library。
- 實測數據：
  - 改善前：非索引查詢需掃描 1,000,000 筆（O(n)）。
  - 改善後：索引查詢為雜湊/樹結構查找（O(1)～O(log n)）。
  - 改善幅度：理論上數十倍級；原文示範透過 Stopwatch 顯示明顯下降（未提供具體毫秒值）。

- Learning Points（學習要點）
  - 核心知識點：
    - LINQ to Objects 在 IEnumerable<T> 上的時間複雜度。
    - 索引化資料結構對等值查詢的顯著效益。
    - 最小侵入導入 i4o 保留 LINQ 語法。
  - 技能要求：
    - 必備技能：C#、LINQ 基礎、Stopwatch 基準量測。
    - 進階技能：記憶體結構選型、Big-O 分析。
  - 延伸思考：
    - 適用於高頻的精確等值查詢。
    - 風險：索引建置成本與記憶體佔用。
    - 優化：只為熱點欄位建立索引、啟動期預建索引。

- Practice Exercise（練習題）
  - 基礎練習：以 100 萬筆資料比較非索引 vs i4o 索引查詢時間。
  - 進階練習：重複查詢同條件 100 次，觀察時間差異與穩定性。
  - 專案練習：包裝一個「開關式索引」工具類，支援動態啟用/停用索引。

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：能正確執行非索引與索引版查詢並輸出結果。
  - 程式碼品質（30%）：程式結構清晰，命名與註解完善。
  - 效能優化（20%）：展示明顯查詢時間改善與建置成本解釋。
  - 創新性（10%）：提供通用化的小型索引封裝與切換策略。

----------------------------------------

## Case #2: 自訂 IndexedList 以字典為基礎加速等值查詢

### Problem Statement（問題陳述）
- 業務場景：團隊希望不引入外部套件，先以快速原型方式驗證「索引是否真的能加速」；針對 Foo.Text 與 Foo.Number 做等值查詢最佳化。
- 技術挑戰：要在維持 LINQ 語法的同時，讓等值查詢改走索引，不走全表掃描；且需支援鍵值重複。
- 影響範圍：影響查詢延遲、CPU 使用率、與後續是否採用第三方庫的決策。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 非索引 List 逐筆掃描 O(n)。
  2. 熱點條件反覆查詢造成重複成本。
  3. 一對多鍵值（多筆 Foo.Text 相同）需妥善設計索引容器。
- 深層原因：
  - 架構層面：集合未內建索引層。
  - 技術層面：未有 Expression 分析以辨識可索引條件。
  - 流程層面：缺乏索引建立/重建的生命週期約定。

### Solution Design（解決方案設計）
- 解決策略：實作 IndexedList，內含 Dictionary<key, List<Foo>> 索引與 ReIndex 方法；針對「==」條件使用索引，其他條件回退 Enumerable.Where。

- 實施步驟：
  1. 建索引結構
     - 細節：_byText 與 _byNumber 使用 GroupBy 建置；支援重複值。
     - 資源：C#、LINQ。
     - 時間：1 小時。
  2. 解析條件與回退策略
     - 細節：提供 Where(Expression<Func<Foo,bool>>) 版本，辨識 BinaryExpression.Equal 並抽取成常值。
     - 資源：System.Linq.Expressions。
     - 時間：1.5 小時。

- 關鍵程式碼/設定：
```csharp
public sealed class IndexedList : IEnumerable<Foo>
{
    private readonly List<Foo> _data = new();
    private Dictionary<string, List<Foo>> _byText = new();
    private Dictionary<int, List<Foo>> _byNumber = new();

    public void AddRange(IEnumerable<Foo> items) => _data.AddRange(items);

    public void ReIndex()
    {
        _byText = _data.GroupBy(f => f.Text)
                       .ToDictionary(g => g.Key, g => g.ToList());
        _byNumber = _data.GroupBy(f => f.Number)
                         .ToDictionary(g => g.Key, g => g.ToList());
    }

    // 僅示意：辨識 x.Text == "val" / x.Number == val
    public IEnumerable<Foo> Where(Expression<Func<Foo, bool>> predicate)
    {
        if (TryResolveEqualityOnText(predicate, out var text))
            return _byText.TryGetValue(text, out var list) ? list : Enumerable.Empty<Foo>();
        if (TryResolveEqualityOnNumber(predicate, out var num))
            return _byNumber.TryGetValue(num, out var list) ? list : Enumerable.Empty<Foo>();
        // 回退：一般列舉
        return _data.AsEnumerable().Where(predicate.Compile());
    }

    public IEnumerator<Foo> GetEnumerator() => _data.GetEnumerator();
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();

    // TryResolveEqualityOnText/Number 解析 Expression 的工具略
}
```

- 實際案例：文章 list2 使用 IndexedList，僅支援等值運算元（==），並在 ReIndex 後做查詢量測。
- 實作環境：.NET/C#、自訂集合型別。
- 實測數據：
  - 改善前：List 掃描 O(n)。
  - 改善後：字典查找 O(1)（找到群組後再列舉）。
  - 改善幅度：理論顯著，依鍵值分布而定；文章以 Stopwatch 呈現差距（未列具體毫秒）。

- Learning Points（學習要點）
  - 核心知識點：字典索引結構、一對多鍵值映射、Expression 分析。
  - 技能要求：泛型/集合、LINQ GroupBy、Expression Tree 基礎。
  - 延伸思考：支援更多運算子時的折衷；回退策略的可預期性與可測性。

- Practice Exercise（練習題）
  - 基礎：實作 ReIndex 並驗證 Text/Number 的查詢正確性。
  - 進階：加入簡單的 StartsWith 回退策略，並與等值索引比較時間。
  - 專案：實作一個可插拔的 IndexProvider 介面，支援多欄位註冊与回退。

- Assessment Criteria（評估標準）
  - 功能完整性：等值條件走索引、其他條件回退正常。
  - 程式碼品質：清晰封裝、單元測試覆蓋 ReIndex 與查詢。
  - 效能優化：等值查詢明顯加速。
  - 創新性：可擴充的索引提供者設計。

----------------------------------------

## Case #3: 使用 i4o 建立索引並保留 LINQ 語法體驗

### Problem Statement（問題陳述）
- 業務場景：既有系統有大量 LINQ 查詢語法，團隊希望以最小改動導入索引讓查詢加速，避免重寫查詢邏輯。
- 技術挑戰：既有查詢是 LINQ to Objects 語法，需要索引庫在不破壞語法的情況下接管查詢。
- 影響範圍：重構成本、風險控制、交付速度。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 標準 IEnumerable<T> Where 為逐筆掃描。
  2. 缺乏可將 Where 映射至索引查找的機制。
  3. 不希望修改大量查詢碼。
- 深層原因：
  - 架構層面：缺乏中介層抽象（Indexable + Provider）。
  - 技術層面：沒有 Expression 攔截與重寫。
  - 流程層面：重構風險與測試覆蓋不足。

### Solution Design（解決方案設計）
- 解決策略：採用 i4o 的 IndexableCollection 與 CreateIndexFor，透過擴充與 Provider 攔截 Where，使等值條件走索引，同時保留原有查詢語法。

- 實施步驟：
  1. 轉換集合並建立索引
     - 細節：list1.ToIndexableCollection<Foo>().CreateIndexFor(i => i.Text)。
     - 資源：i4o 套件。
     - 時間：0.5 小時。
  2. 驗證查詢一致性
     - 細節：對比 list1（非索引）與 list3（i4o）查詢結果。
     - 資源：單元測試。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
var list3 = list1.ToIndexableCollection<Foo>();
list3.CreateIndexFor(i => i.Text);
var q = (from x in list3 where x.Text == "888365" select x.Text).ToList();
```

- 實際案例：文章 list3 使用 i4o 建立索引後量測，顯示 Query time 明顯較非索引快。
- 實作環境：.NET/C#、i4o。
- 實測數據：
  - 改善前：O(n)。
  - 改善後：O(1)～O(log n)。
  - 改善幅度：顯著；文章以 Stopwatch 呈現（未列具體毫秒）。

- Learning Points
  - 知識點：以 Provider 層接管 LINQ 查詢；擴充方法最小侵入導入。
  - 技能：NuGet/套件導入、API 閱讀、回歸測試。
  - 延伸：Provider 的限制條件辨識（等值、可翻譯條件）。

- Practice Exercise
  - 基礎：將現有 List 查詢改為 i4o 版本，確保結果一致。
  - 進階：測試不同鍵值選擇度對查詢時間的影響。
  - 專案：撰寫索引啟用/停用的實作與效能儀表板。

- Assessment Criteria
  - 功能完整性：結果一致性與查詢正確。
  - 程式碼品質：最小改動且可回退。
  - 效能優化：明顯查詢加速。
  - 創新性：索引開關與監控。

----------------------------------------

## Case #4: 同時為 Text 與 Number 建立多欄位索引

### Problem Statement（問題陳述）
- 業務場景：不同情境會用 Text 或 Number 查詢 Foo；為避免不同欄位查詢時性能不穩定，需要為多欄位建立索引。
- 技術挑戰：多索引的建置與維護成本、查詢時的索引選擇、與記憶體佔用。
- 影響範圍：查詢體驗一致性、記憶體壓力、啟動時間。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單欄位索引無法覆蓋其他欄位的查詢。
  2. 未索引欄位仍是 O(n)。
  3. 多索引會增加建置與維護成本。
- 深層原因：
  - 架構層面：索引策略未與使用者查詢行為對齊。
  - 技術層面：索引選擇與落地資料結構需規劃。
  - 流程層面：缺少「熱點欄位」的量測與決策機制。

### Solution Design（解決方案設計）
- 解決策略：以 i4o 建立多個索引 CreateIndexFor(i=>i.Text).CreateIndexFor(i=>i.Number)，確保常見查詢都有對應索引。

- 實施步驟：
  1. 觀測與選欄位
     - 細節：收集查詢行為，選定 Text 與 Number。
     - 資源：記錄器/效能日誌。
     - 時間：0.5 小時。
  2. 建立多索引
     - 細節：連鎖呼叫 CreateIndexFor。
     - 資源：i4o。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
var list3 = list1.ToIndexableCollection<Foo>();
list3.CreateIndexFor(i => i.Text)
     .CreateIndexFor(i => i.Number);
```

- 實際案例：文章示範同時建立 Text、Number 索引。
- 實作環境：.NET/C#、i4o。
- 實測數據：
  - 改善前：未索引欄位查詢 O(n)。
  - 改善後：兩欄位等值查詢皆為 O(1)～O(log n)。
  - 改善幅度：顯著（視查詢條件而定）。

- Learning Points
  - 知識點：多索引策略與取捨、查詢分佈的重要性。
  - 技能：指標收集、索引規劃。
  - 延伸：對低選擇度欄位索引效益有限。

- Practice Exercise
  - 基礎：為 Number 建索引並量測查詢時間。
  - 進階：比較建立單索引 vs 多索引的建置時間與記憶體。
  - 專案：做一份欄位選擇度與命中率報告，驅動索引策略。

- Assessment Criteria
  - 功能完整性：兩欄位等值皆具加速。
  - 程式碼品質：清楚的索引宣告與註解。
  - 效能優化：建置成本與查詢收益分析。
  - 創新性：索引選擇的資料驅動方法。

----------------------------------------

## Case #5: 索引建立時間成本與查詢頻度的折衷

### Problem Statement（問題陳述）
- 業務場景：系統啟動時要快速提供查詢；索引建置需時間，如何平衡「啟動延遲」與「查詢延遲」？
- 技術挑戰：Build Index time 不為零；是否應在啟動期預建或延後/懶建？
- 影響範圍：啟動體驗、首次查詢延遲、整體吞吐。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 建索引為 O(n)。
  2. 啟動時一次建完易造成冷啟動延遲。
  3. 懶建又可能將成本轉嫁到首次查詢。
- 深層原因：
  - 架構層面：缺乏索引生命週期策略。
  - 技術層面：沒有背景建置或漸進式策略。
  - 流程層面：缺乏基準量測做決策。

### Solution Design（解決方案設計）
- 解決策略：量測 Build Index time 與查詢頻度，選擇預建/懶建/背景建置策略。多次查詢同條件情境建議預建或在啟動後背景建置再切換。

- 實施步驟：
  1. 量測建置與查詢成本
     - 細節：Stopwatch 記錄 Build Index time 與 Query time。
     - 資源：Stopwatch。
     - 時間：0.5 小時。
  2. 策略落地
     - 細節：啟動預建或背景 Task 建置，建置完成後切換指標。
     - 資源：Task/Threading。
     - 時間：1 小時。

- 關鍵程式碼/設定：
```csharp
var timer = Stopwatch.StartNew();
list3.CreateIndexFor(i => i.Text).CreateIndexFor(i => i.Number);
Console.WriteLine($"Build Index time: {timer.Elapsed.TotalMilliseconds:0.00} ms");
```

- 實際案例：文章分別列出 Build Index time 與 Query time。
- 實作環境：.NET/C#、i4o。
- 實測數據：
  - 改善前：無索引查詢每次 O(n)。
  - 改善後：一次性 O(n) 建置換取後續 O(1)～O(log n)。
  - 改善幅度：取決於查詢次數；多次查詢越划算。

- Learning Points
  - 知識點：建置成本攤提、首次查詢效應。
  - 技能：基準測試與曲線分析。
  - 延伸：背景建置與漸進式索引。

- Practice Exercise
  - 基礎：量測 1M 筆建索引時間。
  - 進階：模擬不同查詢頻率下的總成本比較。
  - 專案：實作背景建置與完成事件，切換至索引版查詢。

- Assessment Criteria
  - 功能完整性：能輸出建置與查詢時間。
  - 程式碼品質：測試與量測程式清晰。
  - 效能優化：給出策略選擇的數據佐證。
  - 創新性：自動策略切換。

----------------------------------------

## Case #6: 大量 AddRange 後的 ReIndex 流程設計

### Problem Statement（問題陳述）
- 業務場景：資料來源批量更新（AddRange）；自訂 IndexedList 的索引已過期，必須重建才有效。
- 技術挑戰：如何在批次載入後一致性地重建索引，避免不一致與錯誤命中。
- 影響範圍：查詢正確性與效能。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 批次新增沒有同步更新索引。
  2. 索引過期造成查詢錯誤或回退掃描。
  3. 未定義重建時點。
- 深層原因：
  - 架構層面：索引更新策略缺失。
  - 技術層面：缺少 Bulk Load 與 ReIndex 配套。
  - 流程層面：無明確資料載入完成訊號。

### Solution Design（解決方案設計）
- 解決策略：在 AddRange 完成後統一呼叫 ReIndex；或提供「批次模式」暫停增量更新，最後一次性建索引。

- 實施步驟：
  1. 批次加入
     - 細節：AddRange(list1)。
     - 資源：IndexedList。
     - 時間：0.1 小時。
  2. 重建索引
     - 細節：list2.ReIndex()。
     - 資源：GroupBy/ToDictionary。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
IndexedList list2 = new IndexedList();
list2.AddRange(list1);
list2.ReIndex(); // 建立/重建索引
```

- 實際案例：文章 list2 在查詢前呼叫 ReIndex。
- 實作環境：.NET/C#。
- 實測數據：
  - 改善前：索引過期/無索引，回退 O(n)。
  - 改善後：索引一致，等值查詢 O(1)。
  - 改善幅度：明顯。

- Learning Points
  - 知識點：批次模式下的索引維護。
  - 技能：資料載入流程設計。
  - 延伸：增量更新 vs 全量重建比較。

- Practice Exercise
  - 基礎：完成 AddRange 後重建索引並驗證查詢。
  - 進階：量測增量更新與重建的時間差。
  - 專案：設計批次模式 API，支援 BeginBulk/EndBulk。

- Assessment Criteria
  - 功能完整性：重建後查詢正確。
  - 程式碼品質：API 明確、錯誤處理完善。
  - 效能優化：合適的更新策略。
  - 創新性：批次模式設計。

----------------------------------------

## Case #7: 當集合資料異動時的索引一致性維護

### Problem Statement（問題陳述）
- 業務場景：資料在運行期連續 Add/Remove 或修改 Foo.Text；索引需同步更新避免查詢錯誤。
- 技術挑戰：如何在新增、刪除、欄位變更時維持索引正確性且成本可控。
- 影響範圍：查詢正確性、效能與記憶體。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 變更未反映至索引。
  2. 欄位變更需同時從舊鍵移除、加至新鍵。
  3. 並發情境下需要同步機制。
- 深層原因：
  - 架構層面：缺少事件/觀察者模型。
  - 技術層面：未實作增量索引更新。
  - 流程層面：無一致的資料變更 API。

### Solution Design（解決方案設計）
- 解決策略：在自訂 IndexedList 中集中資料異動 API（Add/Remove/Update），在其中同步更新字典索引；必要時以 ReaderWriterLockSlim 保護。

- 實施步驟：
  1. 集中異動入口
     - 細節：禁止外部直接操作內部 List，改用方法封裝。
     - 資源：封裝、介面設計。
     - 時間：1 小時。
  2. 增量更新索引
     - 細節：Add 時加入索引；Update 時從舊鍵移除再加入新鍵。
     - 資源：字典操作/鎖。
     - 時間：2 小時。

- 關鍵程式碼/設定：
```csharp
public void Add(Foo item) {
    _data.Add(item);
    _byText.GetOrCreate(item.Text).Add(item);
    _byNumber.GetOrCreate(item.Number).Add(item);
}

public void UpdateText(Foo item, string newText) {
    if (_byText.TryGetValue(item.Text, out var bucket)) bucket.Remove(item);
    item.Text = newText;
    _byText.GetOrCreate(item.Text).Add(item);
}
```

- 實際案例：文章指明自訂 IndexedList 僅示範，需自行維護；此案例補足「運行期異動」實作。
- 實作環境：.NET/C#。
- 實測數據：
  - 改善前：索引與資料不一致會導致錯誤或回退。
  - 改善後：一致性維護，查詢正確且快。
  - 改善幅度：功能正確性與穩定性提升。

- Learning Points
  - 知識點：增量索引維護、觀察者/事件模型。
  - 技能：執行緒安全、封裝 API 設計。
  - 延伸：INotifyPropertyChanged 自動追蹤。

- Practice Exercise
  - 基礎：完成 Add/Remove 更新索引。
  - 進階：實作 Text 變更的 Update API。
  - 專案：支援 INotifyPropertyChanged 自動更新索引。

- Assessment Criteria
  - 功能完整性：各種異動後查詢正確。
  - 程式碼品質：同步與封裝合理。
  - 效能優化：增量更新開銷可控。
  - 創新性：自動化追蹤機制。

----------------------------------------

## Case #8: 鍵值重複情境下的索引桶設計

### Problem Statement（問題陳述）
- 業務場景：Foo.Text 可能出現大量重複值，索引需高效返回多筆結果，且保持可預期的列舉順序。
- 技術挑戰：字典索引需要一對多映射；如何選擇容器型態（List/HashSet）與初始容量。
- 影響範圍：查詢速度、記憶體佔用、順序穩定性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 重複鍵需存多元素。
  2. 若使用單一 Foo 值會覆蓋資料。
  3. 需兼顧列舉效率。
- 深層原因：
  - 架構層面：索引桶策略未定義。
  - 技術層面：容器選擇影響效能/記憶體。
  - 流程層面：缺乏鍵值分佈分析。

### Solution Design（解決方案設計）
- 解決策略：使用 Dictionary<TKey, List<Foo>>；如需去重且不在意順序可改 HashSet<Foo>；對熱點鍵預估容量。

- 實施步驟：
  1. 選容器
     - 細節：List 維持插入順序、容量擴充策略。
     - 資源：.NET 集合。
     - 時間：0.5 小時。
  2. 建桶
     - 細節：GroupBy 建立；或逐筆 GetOrCreate。
     - 資源：擴充方法。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
public static class DictExt {
    public static List<TV> GetOrCreate<TK, TV>(this Dictionary<TK, List<TV>> d, TK key)
        => d.TryGetValue(key, out var list) ? list : (d[key] = new List<TV>(capacity: 4));
}
```

- 實際案例：文章自訂索引語意上需支援重複值。
- 實作環境：.NET/C#。
- 實測數據：
  - 改善前：覆蓋或錯誤回傳。
  - 改善後：正確返回所有命中項。
  - 改善幅度：功能正確性提升。

- Learning Points
  - 知識點：一對多索引桶設計。
  - 技能：容量預估、順序需求判斷。
  - 延伸：熱點鍵的空間優化。

- Practice Exercise
  - 基礎：完成 GetOrCreate 並測試。
  - 進階：比較 List vs HashSet 記憶體與速度。
  - 專案：針對熱點鍵做容量探勘與預配置。

- Assessment Criteria
  - 功能完整性：正確支持重複鍵。
  - 程式碼品質：擴充方法設計清楚。
  - 效能優化：減少擴容與分配。
  - 創新性：分佈感知優化策略。

----------------------------------------

## Case #9: 不支援等值以外條件時的回退策略

### Problem Statement（問題陳述）
- 業務場景：開發者寫了 x.Text.StartsWith("888") 或 x.Number > 100；自訂 IndexedList 僅支援 ==。
- 技術挑戰：如何在不支援的條件下安全回退到列舉，且維持一致的結果。
- 影響範圍：功能正確性、使用者預期、效能。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 索引僅支援等值運算符。
  2. 其他運算子難以索引化。
  3. 若強行解析可能錯誤。
- 深層原因：
  - 架構層面：索引能力邊界未清楚揭示。
  - 技術層面：Expression 解析與安全回退未實作。
  - 流程層面：缺乏使用者指引與日誌。

### Solution Design（解決方案設計）
- 解決策略：在 Where(Expression<...>) 中辨識可索引條件；不可索引則回退到 _data.Where(predicate.Compile())，並可選擇記錄一次性警告。

- 實施步驟：
  1. 條件分類
     - 細節：BinaryExpression.Equal → 索引；其他 → 回退。
     - 資源：Expression Tree。
     - 時間：1 小時。
  2. 日誌/文件
     - 細節：提示等值查詢最佳化能力與限制。
     - 資源：Logger/README。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
if (IsEqualityOnSupportedField(predicate, out var key)) {
    return LookupByIndex(key);
} else {
    // 回退
    return _data.Where(predicate.Compile());
}
```

- 實際案例：文章註明「Query 只支援 == 運算元」。
- 實作環境：.NET/C#。
- 實測數據：
  - 改善前：所有條件皆掃描。
  - 改善後：等值→索引；其他→掃描但結果正確。
  - 改善幅度：在可索引條件下顯著加速。

- Learning Points
  - 知識點：能力邊界設計與回退。
  - 技能：Expression 安全分析。
  - 延伸：可考慮為範圍查詢另建排序索引。

- Practice Exercise
  - 基礎：為 StartsWith 建測試，驗證回退正確。
  - 進階：在回退情況記錄一次性警告。
  - 專案：加入 SortedDictionary 為 Number 提供簡單範圍查詢。

- Assessment Criteria
  - 功能完整性：回退結果正確。
  - 程式碼品質：清晰的能力判斷。
  - 效能優化：等值條件確實走索引。
  - 創新性：範圍查詢雛型。

----------------------------------------

## Case #10: 記憶體佔用與索引選擇的取捨

### Problem Statement（問題陳述）
- 業務場景：在 1,000,000 筆資料上同時建立多個索引造成記憶體壓力；需決定只索引哪些欄位。
- 技術挑戰：在效能與資源間取得平衡；避免過度索引。
- 影響範圍：機器成本、GC 壓力、服務穩定性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 多索引帶來額外字典與桶的記憶體。
  2. 熱點欄位與冷門欄位混雜。
  3. 未衡量選擇度帶來的收益。
- 深層原因：
  - 架構層面：缺乏容量與壓力預估。
  - 技術層面：索引策略未根據查詢數據驅動。
  - 流程層面：缺乏監控與定期調整。

### Solution Design（解決方案設計）
- 解決策略：只為高頻且高選擇度欄位建索引；提供可配置的索引白名單；定期審視。

- 實施步驟：
  1. 蒐集資料
     - 細節：記錄查詢次數與命中選擇度。
     - 資源：Metrics/Logging。
     - 時間：1 小時。
  2. 配置索引
     - 細節：基於閾值建立/移除索引。
     - 資源：設定檔/Feature flag。
     - 時間：1 小時。

- 關鍵程式碼/設定：
```csharp
// 只為熱點欄位建立索引
var cfg = new IndexConfig { EnableText = true, EnableNumber = false };
var ix = list1.ToIndexableCollection<Foo>();
if (cfg.EnableText) ix.CreateIndexFor(i => i.Text);
if (cfg.EnableNumber) ix.CreateIndexFor(i => i.Number);
```

- 實際案例：文章同時建兩個索引，顯示建置時間可量測；本案例聚焦取捨。
- 實作環境：.NET/C#、i4o。
- 實測數據：
  - 改善前：所有欄位建索引，記憶體高。
  - 改善後：只建必要索引，記憶體壓力下降。
  - 改善幅度：依欄位數與分布而定。

- Learning Points
  - 知識點：選擇度與索引收益。
  - 技能：監控與配置化。
  - 延伸：動態索引開關。

- Practice Exercise
  - 基礎：為單一欄位建索引，觀察記憶體。
  - 進階：建立兩個索引，對比差異。
  - 專案：做一個簡易索引策略管理介面。

- Assessment Criteria
  - 功能完整性：索引開關可用。
  - 程式碼品質：配置清晰。
  - 效能優化：內存與時間權衡合理。
  - 創新性：策略自動化。

----------------------------------------

## Case #11: 基準測試方法學：JIT/GC/暖機的影響

### Problem Statement（問題陳述）
- 業務場景：以 Stopwatch 比較不同集合查詢時間，但第一次執行常受 JIT、GC 影響導致數據不穩。
- 技術挑戰：如何建立可重現的量測流程，公平比較非索引、字典索引、i4o。
- 影響範圍：決策正確性、可信度。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 首次 JIT 編譯。
  2. GC 干擾。
  3. 測量區段不一致。
- 深層原因：
  - 架構層面：無統一量測框架。
  - 技術層面：對 .NET 執行模型理解不足。
  - 演練流程：欠缺暖機與多次重複。

### Solution Design（解決方案設計）
- 解決策略：預熱、強制 GC、重複 N 次取中位數；隔離建索引與查詢測段，分別計時。

- 實施步驟：
  1. 暖機與 GC
     - 細節：先跑一次查詢；GC.Collect/WaitForPendingFinalizers。
     - 資源：System.GC。
     - 時間：0.5 小時。
  2. 重複取樣
     - 細節：迴圈執行 30 次取中位數。
     - 資源：Stopwatch/統計。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
// 暖機
_ = list1.Where(x => x.Text == "888365").ToList();
// GC 清理
GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();

// 重複測量
double MedianTime(Func<double> measure) => Enumerable.Range(0,30).Select(_ => measure()).OrderBy(x=>x).ElementAt(15);
```

- 實際案例：文章展示 Build/Query time；本案例補足方法學。
- 實作環境：.NET/C#。
- 實測數據：可重現性提升、波動降低。

- Learning Points
  - 知識點：量測原則、變異來源。
  - 技能：GC 控制、統計中位數。
  - 延伸：BenchmarkDotNet 導入。

- Practice Exercise
  - 基礎：加上暖機與 GC 後重測。
  - 進階：寫自動化量測工具。
  - 專案：導入 BenchmarkDotNet 比對三種集合。

- Assessment Criteria
  - 功能完整性：量測腳本完善。
  - 程式碼品質：結構與輸出格式清晰。
  - 效能優化：降低量測誤差。
  - 創新性：自動報表。

----------------------------------------

## Case #12: 將既有 List 查詢最小侵入地遷移到 i4o

### Problem Statement（問題陳述）
- 業務場景：既有代碼大量使用 List<Foo> 與 LINQ；希望在不大量重寫的前提下導入索引。
- 技術挑戰：最大限度沿用既有查詢與測試，降低改動風險。
- 影響範圍：工期、風險與回歸測試範圍。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 大量查詢散佈在各處。
  2. 重寫成本高。
  3. 缺少轉接層。
- 深層原因：
  - 架構層面：集合型別耦合緊。
  - 技術層面：缺乏封裝點。
  - 流程層面：回歸測試成本高。

### Solution Design（解決方案設計）
- 解決策略：在查詢入口處以 ToIndexableCollection 包覆，建立必要索引後，維持原查詢語法。

- 實施步驟：
  1. 封裝入口
     - 細節：提供方法 GetIndexableFoos() 回傳索引化集合。
     - 資源：i4o。
     - 時間：0.5 小時。
  2. 漸進替換
     - 細節：逐個模組替換查詢來源。
     - 資源：單元/整合測試。
     - 時間：1～2 小時。

- 關鍵程式碼/設定：
```csharp
IndexableCollection<Foo> GetIndexableFoos(List<Foo> src)
    => src.ToIndexableCollection<Foo>()
          .CreateIndexFor(i => i.Text)
          .CreateIndexFor(i => i.Number);
```

- 實際案例：文章用 list1 → list3 轉換並建立索引。
- 實作環境：.NET/C#、i4o。
- 實測數據：導入後等值查詢獲得顯著加速（見 Stopwatch）。

- Learning Points
  - 知識點：遷移策略、包裝與抽象。
  - 技能：API 設計與重構。
  - 延伸：Feature flag 控制開關。

- Practice Exercise
  - 基礎：將一個模組改成用 i4o。
  - 進階：提供回退到 List 的開關。
  - 專案：批次導入與回歸測試自動化。

- Assessment Criteria
  - 功能完整性：結果一致。
  - 程式碼品質：封裝清楚。
  - 效能優化：明顯加速。
  - 創新性：灰度/開關策略。

----------------------------------------

## Case #13: 與投影 Select 搭配減少資料搬運

### Problem Statement（問題陳述）
- 業務場景：查詢只需 Text 欄位，若回傳整個 Foo 會增加記憶體與序列化負擔。
- 技術挑戰：在索引查詢後，只投影必要欄位，避免額外負荷。
- 影響範圍：延遲、記憶體、帶寬。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 回傳整個物件不必要。
  2. 投影缺失導致額外負擔。
  3. 與索引相乘造成浪費。
- 深層原因：
  - 架構層面：缺乏「最小資料」原則。
  - 技術層面：忽略 Select 對效能影響。
  - 流程層面：缺測量。

### Solution Design（解決方案設計）
- 解決策略：延續文章寫法，查詢後以 select x.Text 投影，將結果轉為 List<string>。

- 實施步驟：
  1. 依需求投影
     - 細節：只取 Text。
     - 資源：LINQ。
     - 時間：0.1 小時。
  2. 序列化優化
     - 細節：前端只收必要資料。
     - 資源：序列化設定。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
var texts = (from x in list3 where x.Text == "888365" select x.Text).ToList();
```

- 實際案例：文章查詢以 select x.Text 投影。
- 實作環境：.NET/C#、i4o。
- 實測數據：投影減少資料搬運；在大量命中時差異更明顯。

- Learning Points
  - 知識點：投影與效能。
  - 技能：LINQ 投影、型別轉換。
  - 延伸：匿名型別、DTO。

- Practice Exercise
  - 基礎：改寫查詢只回傳必要欄位。
  - 進階：比較回傳 Foo vs string 的時間/記憶體。
  - 專案：為 API 加上「欄位選擇」參數。

- Assessment Criteria
  - 功能完整性：投影正確。
  - 程式碼品質：清晰簡潔。
  - 效能優化：搬運成本下降。
  - 創新性：欄位選擇 API。

----------------------------------------

## Case #14: 能力邊界提示與使用者引導（僅支援 ==）

### Problem Statement（問題陳述）
- 業務場景：團隊新成員不清楚自訂 IndexedList 只支援 ==；誤以為所有運算子皆優化。
- 技術挑戰：提供明確 API 訊號與運行期警告，避免誤用。
- 影響範圍：缺陷報告、維護成本與信任度。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 能力邊界未明示。
  2. 錯誤預期導致誤用。
  3. 回退行為不透明。
- 深層原因：
  - 架構層面：缺文檔與警示。
  - 技術層面：API 缺乏可發現性。
  - 流程層面：缺入門指引。

### Solution Design（解決方案設計）
- 解決策略：在類別與方法摘要標示僅支援 ==；運行期遇不支援條件時，記錄一次性警告或拋出可選例外。

- 實施步驟：
  1. 文件與註解
     - 細節：XML docs、README。
     - 資源：說明文件。
     - 時間：0.5 小時。
  2. 監控警示
     - 細節：Logger 一次性警告。
     - 資源：Logging。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
/// <summary>Only equality (==) on Text/Number is indexed; others fallback.</summary>
public IEnumerable<Foo> Where(Expression<Func<Foo,bool>> predicate) {
    if (!IsSupported(predicate)) {
        _logger.Warn("IndexedList: non-indexable predicate, fallback to scan.");
        return _data.Where(predicate.Compile());
    }
    return Lookup(predicate);
}
```

- 實際案例：文章：「Query 只支援 == 運算元」。
- 實作環境：.NET/C#。
- 實測數據：誤用降低，問題定位更快。

- Learning Points
  - 知識點：設計可發現性與可觀測性。
  - 技能：API 文件化、日誌策略。
  - 延伸：特性標註與分析工具。

- Practice Exercise
  - 基礎：撰寫 XML docs。
  - 進階：加入一次性警告機制。
  - 專案：產出使用指南與常見問題。

- Assessment Criteria
  - 功能完整性：訊息可見且準確。
  - 程式碼品質：文件與註解完整。
  - 效能優化：無不必要開銷。
  - 創新性：友善的開發者體驗。

----------------------------------------

## Case #15: 為 Number 欄位導入索引以加速數值鍵查詢

### Problem Statement（問題陳述）
- 業務場景：系統也常以 Number（int）查找 Foo；未建立 Number 索引時查詢變慢。
- 技術挑戰：與 Text 相同導入索引，確保兩種查詢一致表現。
- 影響範圍：查詢延遲一致性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未為 Number 建索引。
  2. 整數等值查詢仍為 O(n)。
  3. 熱點鍵多次查詢。
- 深層原因：
  - 架構層面：索引策略不完整。
  - 技術層面：忽略數值欄位。
  - 流程層面：需求變更後未更新索引策略。

### Solution Design（解決方案設計）
- 解決策略：以 i4o CreateIndexFor(i=>i.Number) 或自訂 _byNumber 索引，確保等值查詢加速。

- 實施步驟：
  1. 建索引
     - 細節：與 Text 同步建立。
     - 資源：i4o 或自訂。
     - 時間：0.5 小時。
  2. 驗證
     - 細節：對比查詢結果與時間。
     - 資源：測試。
     - 時間：0.5 小時。

- 關鍵程式碼/設定：
```csharp
list3.CreateIndexFor(i => i.Number);
var r = list3.Where(x => x.Number == 123456).ToList();
```

- 實際案例：文章同時建立 Text、Number 索引。
- 實作環境：.NET/C#、i4o。
- 實測數據：等值查詢由 O(n) 降為 O(1)～O(log n)。

- Learning Points
  - 知識點：多欄位均衡。
  - 技能：索引覆蓋率分析。
  - 延伸：跨欄位複合索引（需自訂實作）。

- Practice Exercise
  - 基礎：新增 Number 索引並查詢。
  - 進階：比較 Text vs Number 查詢時間。
  - 專案：嘗試以 Tuple 建複合索引（Number+Text）。

- Assessment Criteria
  - 功能完整性：數值鍵查詢加速。
  - 程式碼品質：一致的索引管理。
  - 效能優化：時間顯著下降。
  - 創新性：複合鍵探索。

----------------------------------------

## Case #16: 三種集合查詢一致性與回歸測試

### Problem Statement（問題陳述）
- 業務場景：系統同時存在非索引 List、自訂 IndexedList 與 i4o；需確保三種集合在相同查詢下結果一致。
- 技術挑戰：避免索引錯漏或回退分支導致結果差異。
- 影響範圍：正確性、可靠性、維護成本。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 表達式解析錯誤可能漏命中。
  2. 索引桶不完整或未更新。
  3. i4o 與自訂策略不同。
- 深層原因：
  - 架構層面：多實作並存缺少統一驗證。
  - 技術層面：單元測試不足。
  - 流程層面：回歸測試流程未建立。

### Solution Design（解決方案設計）
- 解決策略：建立對照測試：以 list1 為權威（全掃描），比對 list2、list3 的結果集合；納入 CI。

- 實施步驟：
  1. 權威結果
     - 細節：list1 上的 Where/Select 作為 expected。
     - 資源：LINQ。
     - 時間：0.5 小時。
  2. 比對與報告
     - 細節：Set 相等比較、差異報告。
     - 資源：單元測試框架。
     - 時間：1 小時。

- 關鍵程式碼/設定：
```csharp
var expected = list1.Where(x => x.Text == "888365").Select(x => x.Text).ToHashSet();
var got2 = list2.Where(x => x.Text == "888365").Select(x => x.Text).ToHashSet();
var got3 = list3.Where(x => x.Text == "888365").Select(x => x.Text).ToHashSet();
Assert.True(expected.SetEquals(got2));
Assert.True(expected.SetEquals(got3));
```

- 實際案例：文章三組集合對照；本案例補充測試方法。
- 實作環境：.NET/C#、xUnit/NUnit。
- 實測數據：一致性保證。

- Learning Points
  - 知識點：基於權威實作的對照測試。
  - 技能：集合比較、測試自動化。
  - 延伸：隨機資料種子（如 8072）確保可重現。

- Practice Exercise
  - 基礎：寫三集合一致性測試。
  - 進階：覆蓋 Number 查詢。
  - 專案：加入隨機測試與種子控制。

- Assessment Criteria
  - 功能完整性：測試覆蓋主要條件。
  - 程式碼品質：測試結構清晰。
  - 效能優化：測試效率合理。
  - 創新性：差異報表工具。

----------------------------------------

案例中共用的型別示意（可在各案例中重用）：
```csharp
public sealed class Foo
{
    public string Text { get; set; }
    public int Number { get; set; }
}

public static IEnumerable<Foo> RndFooSeq(int seed, int count)
{
    var rnd = new Random(seed);
    for (int i = 0; i < count; i++)
        yield return new Foo { Text = rnd.Next(100000, 999999).ToString(), Number = rnd.Next() };
}
```

----------------------------------------
案例分類
----------------------------------------

1) 按難度分類
- 入門級（適合初學者）
  - Case #1 百萬筆非索引等值查詢過慢
  - Case #3 使用 i4o 並保留 LINQ 語法
  - Case #12 最小侵入遷移到 i4o
  - Case #13 與投影 Select 搭配
  - Case #15 為 Number 欄位導入索引
- 中級（需要一定基礎）
  - Case #2 自訂 IndexedList 字典索引
  - Case #4 多欄位索引
  - Case #5 建索引時間與查詢頻度取捨
  - Case #6 批次 AddRange 後 ReIndex
  - Case #8 鍵值重複的索引桶設計
  - Case #9 不支援條件回退策略
  - Case #10 記憶體佔用取捨
  - Case #11 基準測試方法學
  - Case #16 查詢一致性與回歸測試
- 高級（需要深厚經驗）
  - Case #7 異動時的索引一致性維護
  - Case #14 能力邊界提示與使用者引導

2) 按技術領域分類
- 架構設計類
  - Case #5, #7, #10, #12, #14, #16
- 效能優化類
  - Case #1, #2, #3, #4, #5, #6, #8, #9, #11, #13, #15
- 整合開發類
  - Case #3, #12, #14
- 除錯診斷類
  - Case #11, #16, #9
- 安全防護類
  -（本系列案例不涉及安全主題）

3) 按學習目標分類
- 概念理解型
  - Case #1, #4, #5, #10, #11
- 技能練習型
  - Case #2, #6, #8, #13, #15
- 問題解決型
  - Case #3, #7, #9, #12, #16
- 創新應用型
  - Case #5, #10, #14

----------------------------------------
案例關聯圖（學習路徑建議）
----------------------------------------
- 建議先學：
  - Case #1（理解非索引查詢瓶頸）
  - Case #3（最小侵入導入 i4o 的方法）
  - Case #12（遷移策略與封裝）
- 依賴關係與進階：
  - Case #4 依賴 #3（先會建單欄位索引，再擴展到多欄位）。
  - Case #2 依賴 #1（先理解瓶頸，再動手做自訂索引）。
  - Case #6 依賴 #2（自訂索引後學會重建索引流程）。
  - Case #7 依賴 #2（先有索引，才談一致性維護）。
  - Case #9 依賴 #2（在自訂 Where 中做回退策略）。
  - Case #11 橫切所有效能類案例（提供方法學）。
  - Case #16 依賴 #1/#2/#3（完成一致性回歸測試）。
- 完整學習路徑建議：
  1) Case #1 → 2) Case #3 → 3) Case #12 → 4) Case #4 → 5) Case #5 → 6) Case #2 → 7) Case #6 → 8) Case #9 → 9) Case #10 → 10) Case #11 → 11) Case #7 → 12) Case #8 → 13) Case #13 → 14) Case #15 → 15) Case #14 → 16) Case #16

此路徑從概念與最小侵入導入開始，逐步擴展到多欄位與策略取捨，再進入自訂實作、回退與一致性維護，最後以方法學與回歸測試收尾，形成一條完整的從理解到落地、從性能到可靠性的學習曲線。