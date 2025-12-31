---
layout: synthesis
title: "該如何學好 \"寫程式\" #2. 為什麼 programmer 該學資料結構 ??"
synthesis_type: solution
source_post: /2008/10/01/how-to-learn-programming-well-2-why-programmers-should-learn-data-structures/
redirect_from:
  - /2008/10/01/how-to-learn-programming-well-2-why-programmers-should-learn-data-structures/solution/
postid: 2008-10-01-how-to-learn-programming-well-2-why-programmers-should-learn-data-structures
---

以下內容基於原文抽取並重構，形成可教、可練、可評的問題解決案例集合。每個案例皆包含問題、根因、解法（含重點程式碼/流程）、並盡量給出文中可得的實測或推算指標。

## Case #1: 以 List<T> 線性搜尋 100 萬筆通訊錄的效能瓶頸

### Problem Statement（問題陳述）
業務場景：內部工具需載入約 100 萬筆通訊錄，支援依姓名精確查詢與依電話號碼前綴過濾（如 0928-1234*）。初版以 List<ContactData> 儲存資料，使用 List<T>.Find 和 FindAll，完成度高、程式簡潔，可快速上線內部 MVP 驗證。

技術挑戰：單純使用 List<T> 的搜尋為 O(n)，每次查詢都必須走訪整個清單；FindAll + StartsWith 針對前綴過濾同樣屬於線性掃描。

影響範圍：當資料規模擴大到千萬、億級時，查詢時間線性暴增，UI 卡頓、查詢逾時、服務資源放大成本高。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 List<T>.Find / FindAll 本質為線性搜尋，時間複雜度 O(n)。
2. 沒有索引結構，無法做到對鍵的直接定位。
3. 前綴過濾靠 StartsWith 並掃描全集，缺乏可界定範圍的排序結構。

深層原因：
- 架構層面：資料存取層未設計索引，資料結構選擇未考慮查詢模式。
- 技術層面：忽略集合類別的時間複雜度特性。
- 流程層面：先實作功能、缺少性能基準與擴展性評估環節。

### Solution Design（解決方案設計）
解決策略：建立性能基準（baseline），量測目前 List<T> 在 100 萬筆上的建置、記憶體與查詢延遲，據以決策後續索引化（Dictionary/SortedList）與多索引架構。以實測＋複雜度分析判斷最佳資料結構。

實施步驟：
1. 建立基準程式
- 實作細節：使用 Stopwatch 計時，Environment.WorkingSet 取記憶體。
- 所需資源：.NET、C#、Stopwatch。
- 預估時間：0.5 小時。

2. 撰寫兩類查詢
- 實作細節：Find（精確）、FindAll+StartsWith（前綴）。
- 所需資源：List<T>。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
// 建立 100 萬筆資料 + 基準查詢（List 基線）
var contacts = new List<ContactData>();
for (int i = 999_999; i >= 0; i--)
{
    contacts.Add(new ContactData {
        Name = $"A{i:D6}",
        EmailAddress = $"{i:D6}@chicken-house.net",
        PhoneNumber = $"0928-{i:D6}"
    });
}

// 精確查詢
var sw = Stopwatch.StartNew();
var hit = contacts.Find(x => x.Name == "A123456");
Console.WriteLine($"Find(Name) {sw.ElapsedMilliseconds} ms");

// 前綴過濾
sw.Restart();
var batch = contacts.FindAll(x => x.PhoneNumber.StartsWith("0928-1234"));
// foreach (var p in batch) p.OutputData(Console.Out);
Console.WriteLine($"FindAll(Phone prefix) {sw.ElapsedMilliseconds} ms");
```

實際案例：原文 Sample1

實作環境：.NET（泛型集合）、C#、Stopwatch

實測數據：
- 改善前：Find(Name) ≈ 60 ms；FindAll(電話前綴) ≈ 240 ms；建資料 ≈ 5151 ms；記憶體 ≈ 288 MB
- 改善後：此案例為基準，改善在後續案例呈現
- 改善幅度：N/A

Learning Points（學習要點）
核心知識點：
- 線性搜尋 O(n) 的可擴展性風險
- 基準測試對比的重要性
- Find vs FindAll 的行為差異

技能要求：
- 必備技能：C# 集合、Stopwatch 使用
- 進階技能：性能基準設計、數據記錄與解讀

延伸思考：
- 若升級到 1 億筆會如何？
- 資料載入順序是否也影響後續效能？
- 是否需引入索引或改變資料結構？

Practice Exercise（練習題）
- 基礎練習：寫出基準程式，量測 10 萬/100 萬筆（30 分鐘）
- 進階練習：新增不同查詢條件並記錄耗時（2 小時）
- 專案練習：封裝成可重複執行的效能基準工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可生成測試資料、執行兩類查詢、輸出數據
- 程式碼品質（30%）：結構清晰、可配置資料量、具錯誤處理
- 效能優化（20%）：可重複測量且數據穩定
- 創新性（10%）：加入數據可視化或報表

---

## Case #2: 以 Dictionary 建姓名索引，將精確查詢降到近 O(1)

### Problem Statement（問題陳述）
業務場景：通訊錄常見需求為「輸入全名即時顯示該人資料」。目前 List<T> 精確查詢耗時明顯且會隨資料量擴大而線性惡化，影響查詢體驗。

技術挑戰：需要對 Name 欄位提供近 O(1) 的存取，以穩定響應時間，同時盡量保持現有程式結構。

影響範圍：查詢延遲由數十毫秒降至接近即時，改善整體互動感；但會增加記憶體占用與建索引時間。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 List 線性掃描造成 O(n)。
2. 未以鍵值映射（hash）直接定址。
3. 缺少針對精確查詢的專用索引。

深層原因：
- 架構層面：單一資料結構難同時滿足不同查詢模式。
- 技術層面：未活用 Dictionary 的 hash table 特性。
- 流程層面：缺乏對精確 vs 範圍查詢的區分設計。

### Solution Design（解決方案設計）
解決策略：新增 Dictionary<string, ContactData> 作為 Name→ContactData 的唯一索引，維持 List 作為主要儲存，最小代價提升精確查詢性能。

實施步驟：
1. 建立姓名索引
- 實作細節：載入時同步填充 Dictionary。
- 所需資源：Dictionary<TKey, TValue>
- 預估時間：0.5 小時

2. 切換查詢路徑
- 實作細節：Name 精確查詢改用 nameIndex[key]。
- 所需資源：N/A
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
var nameIndex = new Dictionary<string, ContactData>();
var contacts = new List<ContactData>();
for (int i = 999_999; i >= 0; i--)
{
    var cd = new ContactData {
        Name = $"A{i:D6}",
        EmailAddress = $"{i:D6}@chicken-house.net",
        PhoneNumber = $"0928-{i:D6}"
    };
    nameIndex.Add(cd.Name, cd);
    contacts.Add(cd);
}

// O(1) 精確查詢
var sw = Stopwatch.StartNew();
var hit = nameIndex["A123456"];
Console.WriteLine($"Find by Dictionary {sw.ElapsedMilliseconds} ms");
```

實際案例：原文 Sample2

實作環境：.NET、C#、Dictionary（雜湊表）

實測數據：
- 改善前：Find(Name) ≈ 60 ms；建資料 ≈ 5151 ms；記憶體 ≈ 288 MB
- 改善後：Find(Name) ≈ 0 ms（破表）；建資料 ≈ 5843 ms；記憶體 ≈ 340 MB
- 改善幅度：精確查詢接近無延遲；代價為建置 +692 ms、+52 MB

Learning Points（學習要點）
核心知識點：
- HashTable 的近 O(1) 查詢特性
- 以空間換時間的典型手法
- 建索引時間/記憶體權衡

技能要求：
- 必備技能：Dictionary API、異常處理（Key 不存在）
- 進階技能：大資料載入時的初始化策略（預先容量）

延伸思考：
- 若 Name 不唯一怎麼辦？
- 如何避免 Dictionary 擴容帶來的尖峰？
- 如何與其它索引共存？

Practice Exercise（練習題）
- 基礎練習：為 Email 新增 Dictionary 索引（30 分鐘）
- 進階練習：處理 Key 不存在與 TryGetValue（2 小時）
- 專案練習：封裝索引管理器，支援多欄位索引（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確索引與查詢
- 程式碼品質（30%）：錯誤處理、可維護性
- 效能優化（20%）：初始化容量、測試數據
- 創新性（10%）：統一索引介面設計

---

## Case #3: Dictionary 不支援前綴/排序查詢，改用 SortedList + 範圍索引

### Problem Statement（問題陳述）
業務場景：需支援電話號碼「輸入前綴即過濾」（0928-1234*），同時也常用姓名/電話排序輸出。Dictionary 可解精確查詢，但不支援範圍與排序。

技術挑戰：要在維持快速查詢的同時，支援可預先排序的結構，並能透過鍵比較作上下界定位。

影響範圍：前綴查詢由全表掃描 O(n) 降為 O(log n + k)；排序列印可直接順序輸出。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Hash 結構不維持順序，無法作範圍查詢。
2. List<T> 雖可排序，但每次排序 O(n log n) 代價高。
3. 缺乏按鍵排序且可二分定位的索引。

深層原因：
- 架構層面：未針對「範圍與排序」設獨立索引。
- 技術層面：忽略 Sorted 系列集合的特性。
- 流程層面：需求分析未拆解精確 vs 範圍/排序。

### Solution Design（解決方案設計）
解決策略：為 Phone 和 Name 分別維護 SortedList<string, ContactData>，以鍵排序存放；使用二分搜尋求得 [lowerBound, upperBound) 以取回前綴結果。

實施步驟：
1. 建立兩個 SortedList 索引
- 實作細節：載入即插入，確保排序。
- 所需資源：SortedList<TKey, TValue>
- 預估時間：1 小時

2. 實作二分搜尋界限
- 實作細節：lowerBound(prefixStart) 與 lowerBound(prefixEnd)
- 所需資源：Comparer<string>
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var nameIndex  = new SortedList<string, ContactData>();
var phoneIndex = new SortedList<string, ContactData>();

for (int i = 0; i < 1_000_000; i++)
{
    var cd = new ContactData {
        Name = $"A{i:D6}",
        EmailAddress = $"{i:D6}@chicken-house.net",
        PhoneNumber = $"0928-{i:D6}"
    };
    nameIndex.Add(cd.Name, cd);
    phoneIndex.Add(cd.PhoneNumber, cd);
}

// 取前綴範圍 [0928-1234, 0928-1235)
int start = BinarySearch(phoneIndex, "0928-1234");
int end   = BinarySearch(phoneIndex, "0928-1235");
for (int pos = start; pos < end; pos++)
{
    // phoneIndex.Values[pos].OutputData(Console.Out);
}
```

實際案例：原文 Sample3

實作環境：.NET、C#、SortedList

實測數據：
- 改善前（List 前綴）：O(n)，≈ 240 ms/百萬筆
- 改善後（SortedList 範圍）：O(log n + k)；Name 搜尋於 100 萬筆為 39,294 ticks（相對 List 3,131,861 ticks，快約 80 倍）
- 改善幅度：大幅下降（依 k 大小而定）

Learning Points（學習要點）
核心知識點：
- Hash vs Sorted 結構差異
- 二分搜尋取得範圍邊界
- 以空間換取排序與查詢便利性

技能要求：
- 必備技能：SortedList API、Comparer
- 進階技能：二分搜尋邊界條件處理

延伸思考：
- 插入成本對批次載入的影響？
- 非整齊前綴（一般字串）如何求上界？
- 大量更新是否改選 SortedDictionary？

Practice Exercise（練習題）
- 基礎練習：以 SortedList 完成任一欄位排序輸出（30 分鐘）
- 進階練習：實作通用 PrefixRange 查詢（2 小時）
- 專案練習：整合姓名、電話雙索引與 UI 搜尋（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可正確回傳前綴結果
- 程式碼品質（30%）：邊界處理、泛型化
- 效能優化（20%）：O(log n + k) 實作
- 創新性（10%）：支援多欄位複合前綴

---

## Case #4: 為 SortedList 撰寫通用二分搜尋（BinarySearch）輔助

### Problem Statement（問題陳述）
業務場景：在 SortedList 上要取得某 prefix 的範圍，需要可重用的 lowerBound/upperBound 搜尋。內建不提供 BinarySearch，需自建泛型方法。

技術挑戰：實作正確的遞迴/迭代二分搜尋，處理起訖邊界與比較器，避免越界與死循環。

影響範圍：前綴查詢穩定性與可維護性；影響所有需要以鍵界定範圍的功能。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. SortedList<TKey, TValue> 未提供 BinarySearch。
2. prefix 查詢需兩次界定：下界、上界。
3. 不同鍵型別需共用泛型比較器。

深層原因：
- 架構層面：共用查詢基礎設施不足。
- 技術層面：邊界條件與遞迴終止未完整考慮。
- 流程層面：缺少單元測試覆蓋極端情境。

### Solution Design（解決方案設計）
解決策略：撰寫泛型 BinarySearch<TKey, TValue>(SortedList<TKey, TValue>, TKey, start, end)，回傳插入/定位位置；配合第二次查詢取得上界。

實施步驟：
1. 撰寫泛型方法
- 實作細節：使用 index.Comparer.Compare 比較鍵，處理 ==、>、< 分支。
- 所需資源：C# 泛型、Comparer
- 預估時間：1 小時

2. 加入單元測試
- 實作細節：空集合、單元素、完全匹配、不存在、全範圍
- 所需資源：xUnit/NUnit
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
private static int BinarySearch<TKey, TValue>(SortedList<TKey, TValue> index, TKey key)
    => BinarySearch(index, key, 0, index.Count - 1);

private static int BinarySearch<TKey, TValue>(SortedList<TKey, TValue> index, TKey key, int start, int end)
{
    if (index.Count == 0) return 0;
    if (start >= end) return start;
    int mid = (start + end) / 2;
    int cmp = index.Comparer.Compare(key, index.Keys[mid]);
    if (cmp == 0) return mid;
    if (cmp > 0) return BinarySearch(index, key, mid + 1, end);
    return BinarySearch(index, key, start, mid - 1);
}
```

實際案例：原文 Sample3 附帶方法

實作環境：.NET、C#、SortedList

實測數據：
- 改善前：無可重用方法，重複程式碼、易錯
- 改善後：二分搜尋 QPS 提升、錯誤率下降
- 改善幅度：時間複雜度由 O(n) 改為 O(log n)（單次搜尋）

Learning Points（學習要點）
核心知識點：
- lower/upper bound 的概念
- 比較器在泛型搜尋的重要性
- 邊界處理與單測覆蓋

技能要求：
- 必備技能：泛型、Comparer、遞迴/迭代
- 進階技能：API 設計與可測性

延伸思考：
- 迭代版本是否更節省堆疊？
- 需否改為回傳（found, index）雙結果？
- 如何泛化出 Range(prefix) API？

Practice Exercise（練習題）
- 基礎練習：將遞迴改寫為迭代（30 分鐘）
- 進階練習：回傳 lower/upper bound 的雙函式（2 小時）
- 專案練習：封裝為 PrefixRange 查詢模組（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可正確回傳定位
- 程式碼品質（30%）：泛型化、邊界清晰
- 效能優化（20%）：對大型鍵集穩定
- 創新性（10%）：易用 API 設計

---

## Case #5: 多索引架構（Name、Phone）滿足排序與多樣查詢

### Problem Statement（問題陳述）
業務場景：通訊錄需同時支援姓名精確查詢、電話前綴過濾，以及依不同欄位排序的輸出。單一結構難以兼顧。

技術挑戰：在可接受的記憶體成本下，設計能對不同欄位提供最佳查詢複雜度的組合索引。

影響範圍：查詢延遲、排序輸出效率、記憶體占用、資料載入時間。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不同查詢模式對資料結構有不同最佳解。
2. 單一清單無法同時滿足精確/範圍/排序。
3. 查詢頻率與型態需要分流到合適索引。

深層原因：
- 架構層面：缺少索引管理層。
- 技術層面：未將操作映射到複雜度矩陣。
- 流程層面：未對查詢熱點進行分析分級。

### Solution Design（解決方案設計）
解決策略：同時維護 Dictionary（Name 精確）、SortedList（Phone 前綴、排序輸出），必要時保留原始 List 作為全量遍歷容器。

實施步驟：
1. 設計索引管理器
- 實作細節：封裝 Add/Remove，確保多索引一致性。
- 所需資源：C# 類別封裝
- 預估時間：2 小時

2. 路由查詢
- 實作細節：依查詢型別選擇 Dictionary/SortedList。
- 所需資源：策略模式/簡易路由
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
class ContactIndex
{
    public Dictionary<string, ContactData> NameIndex { get; } = new();
    public SortedList<string, ContactData> PhoneIndex { get; } = new();

    public void Add(ContactData cd)
    {
        NameIndex[cd.Name] = cd;
        PhoneIndex.Add(cd.PhoneNumber, cd);
    }

    public ContactData FindByName(string name) => NameIndex.TryGetValue(name, out var v) ? v : null;
    // Range 查詢同 Case #3
}
```

實際案例：原文將 Name 與 Phone 建為 SortedList 索引；Name 亦可用 Dictionary

實作環境：.NET、C# 集合

實測數據：
- 改善前：單一 List，查詢 O(n)
- 改善後：精確 O(1)，前綴 O(log n + k)，排序輸出 O(1) 迭代
- 改善幅度：綜合查詢延遲大幅下降，記憶體增加（例如 +52 MB）

Learning Points（學習要點）
核心知識點：
- 多索引並存與查詢路由
- 一致性維護（新增/刪除）
- 複雜度矩陣映射

技能要求：
- 必備技能：集合操作與封裝
- 進階技能：查詢策略、索引一致性

延伸思考：
- 寫入頻繁時如何維護多索引效率？
- 可否延遲建索引（Lazy）？
- 索引持久化與載入恢復？

Practice Exercise（練習題）
- 基礎練習：實作 Add/Remove 同步多索引（30 分鐘）
- 進階練習：實作查詢路由器（2 小時）
- 專案練習：做一個可配置欄位索引的管理元件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：多索引同步、查詢正確
- 程式碼品質（30%）：封裝清晰、測試齊備
- 效能優化（20%）：熱路徑定位最佳索引
- 創新性（10%）：可擴充的索引註冊機制

---

## Case #6: 以時間複雜度預估擴展至 1 億筆的可行性

### Problem Statement（問題陳述）
業務場景：產品經理詢問資料量從 100 萬擴至 1 億時的表現。需提供以複雜度推估的量化報告，以支援技術選型與硬體配置。

技術挑戰：在現有實測基礎上，使用 O(n) 與 O(log n) 做合理外插，產出可決策的數字級差。

影響範圍：產品路線、成本評估、SLA 承諾。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. List 搜尋為 O(n)，資料擴大 100 倍 → 時間 x100。
2. SortedList 二分搜尋 O(log n)，成長平緩。
3. 缺乏前置的量化模型。

深層原因：
- 架構層面：無規模敏感性分析機制。
- 技術層面：忽略大 O 外插價值。
- 流程層面：缺可量化的技術報告模板。

### Solution Design（解決方案設計）
解決策略：以原文實測 ticks 作基準，套用 O(n)/O(log n) 外插，生成 100 倍資料下的預估值，對比差距。

實施步驟：
1. 數據蒐集
- 實作細節：記錄 List 與 SortedList 在 100 萬筆的 ticks
- 所需資源：Stopwatch
- 預估時間：0.5 小時

2. 外插模型
- 實作細節：O(n)：x100；O(log n)：乘以 log(新)/log(舊)
- 所需資源：C# Math.Log
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
long listTicksAt1M   = 3_131_861;
long sortedTicksAt1M = 39_294;

long listTicksAt100M   = listTicksAt1M * 100; // O(n)
long sortedTicksAt100M = (long)(sortedTicksAt1M * Math.Log(100_000_000) / Math.Log(1_000_000));

Console.WriteLine($"List @100M: {listTicksAt100M} ticks");
Console.WriteLine($"SortedList @100M: {sortedTicksAt100M} ticks");
```

實際案例：原文提供 100 萬筆時 List vs SortedList ticks；外插到 1 億筆

實作環境：.NET、C#

實測數據：
- 改善前（List @1M）：3,131,861 ticks；@100M ≈ 313,186,100 ticks
- 改善後（SortedList @1M）：39,294 ticks；@100M ≈ 52,392 ticks
- 改善幅度：在 1 億筆時約 5,978 倍差距

Learning Points（學習要點）
核心知識點：
- 大 O 與外插預估
- 指數 vs 對數成長的實務差距
- 用基準數據支撐決策

技能要求：
- 必備技能：數據處理、Log 計算
- 進階技能：效能報告撰寫

延伸思考：
- 記憶體/IO 是否成為新瓶頸？
- 寫入/更新模式如何影響？
- 何時要改為分散式索引/儲存？

Practice Exercise（練習題）
- 基礎練習：完成外插程式（30 分鐘）
- 進階練習：加入不同硬體時脈/核數估算（2 小時）
- 專案練習：做一份完整的效能預估報告（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確外插計算
- 程式碼品質（30%）：可配置、可重複
- 效能優化（20%）：呈現多種情境
- 創新性（10%）：圖表化呈現

---

## Case #7: 批次載入時利用鍵遞增，降低 SortedList 插入成本

### Problem Statement（問題陳述）
業務場景：載入 100 萬筆資料到 SortedList 時，若鍵分布隨機，插入成本 O(n)。若能順序插入末端，可趨近 O(log n)，縮短建索引時間。

技術挑戰：資料鍵是否可重排？如何在不改語意下讓插入順序符合鍵排序？

影響範圍：批次載入時間、建索引尖峰、上線效率。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. SortedList.Add 在非末端插入為 O(n)。
2. 若插入鍵恰為末端且不觸發 resize，可達 O(log n)。
3. 原基準中 List 遞減生成（999999→0）不利於末端插入。

深層原因：
- 架構層面：載入流程未與資料結構成本對齊。
- 技術層面：忽略插入順序對效能的影響。
- 流程層面：缺少可控制的資料供應順序。

### Solution Design（解決方案設計）
解決策略：批次載入時以鍵遞增的順序產生記錄（如 0→999999），讓 Add 大多落在末端，縮小移位成本。

實施步驟：
1. 重排生成順序
- 實作細節：for (int i=0; i<...; i++) 插入
- 所需資源：資料生成器
- 預估時間：0.5 小時

2. 驗證建置時間
- 實作細節：Stopwatch 比對前後差異
- 所需資源：Stopwatch
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
var phoneIndex = new SortedList<string, ContactData>();
for (int i = 0; i < 1_000_000; i++)
{
    var key = $"0928-{i:D6}"; // 遞增鍵
    phoneIndex.Add(key, new ContactData { PhoneNumber = key, Name = $"A{i:D6}" });
}
```

實際案例：原文說明 SortedList.Add 複雜度，順序插入可優化

實作環境：.NET、C#、SortedList

實測數據：
- 改善前：亂序插入 → 平均 O(n)，建置較慢
- 改善後：順序插入 → 趨近 O(log n)，建置縮短
- 改善幅度：依鍵分布、大幅縮短（以 Stopwatch 量測）

Learning Points（學習要點）
核心知識點：
- 資料載入順序與插入複雜度
- Resize 導致 O(n) 尖峰
- 以流程最佳化輔助資料結構效能

技能要求：
- 必備技能：資料生成控制
- 進階技能：載入管線設計

延伸思考：
- 無法重排時，改用 SortedDictionary 是否更佳？
- 預估容量能否降低 resize 次數？
- 批次 vs 實時插入混合場景？

Practice Exercise（練習題）
- 基礎練習：比較升序/降序/隨機插入時間（30 分鐘）
- 進階練習：加入預估容量對建置的影響（2 小時）
- 專案練習：設計可配置載入策略的索引建置器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：完成三種順序測試
- 程式碼品質（30%）：測試可重現、抽象良好
- 效能優化（20%）：合理分析原因
- 創新性（10%）：提出混合策略

---

## Case #8: 預先設定容量降低 List/Dictionary 擴容成本

### Problem Statement（問題陳述）
業務場景：載入百萬筆資料時，List/Dictionary 擴容會造成 O(n) 的搬移與 rehash。若能預估容量，可降低建置時間尖峰。

技術挑戰：在不影響功能下，以容量規劃換取穩定載入時間。

影響範圍：建索引時間、CPU 尖峰、併發環境穩定度。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. MSDN 說明 Count < Capacity → Add 為 O(1)，否則 O(n)。
2. Dictionary 擴容 rehash 成本高。
3. 未預估容量導致多次擴容。

深層原因：
- 架構層面：缺乏容量規劃機制。
- 技術層面：忽略集合擴容行為。
- 流程層面：測試環境未模擬大量資料。

### Solution Design（解決方案設計）
解決策略：在已知資料量級（如 1,000,000）時，初始化集合容量，將 Add 維持在 O(1) 區間。

實施步驟：
1. 預估容量
- 實作細節：設定 List、Dictionary 初始容量
- 所需資源：需求估算
- 預估時間：0.5 小時

2. 驗證建置時間
- 實作細節：Stopwatch 比較前後差異
- 所需資源：Stopwatch
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
var contacts  = new List<ContactData>(1_000_000);
var nameIndex = new Dictionary<string, ContactData>(1_000_000);
// SortedList<TKey, TValue> 無容量設定 API
```

實際案例：原文引用 MSDN 複雜度說明

實作環境：.NET、C#

實測數據：
- 改善前：多次擴容 → 建置時間波動
- 改善後：擴容次數下降 → 建置時間可預期
- 改善幅度：依原擴容次數不同而異

Learning Points（學習要點）
核心知識點：
- 集合 Capacity 與複雜度關係
- 建置時間尖峰的來源
- 以容量工程優化性能

技能要求：
- 必備技能：集合初始化
- 進階技能：容量估算

延伸思考：
- 估太大是否造成記憶體浪費？
- 是否要分區分桶（shard）載入？
- 與 GC 行為的互動？

Practice Exercise（練習題）
- 基礎練習：比較有/無容量設定的建置時間（30 分鐘）
- 進階練習：在不同資料量下作回歸分析（2 小時）
- 專案練習：撰寫容量估算器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可設定不同容量並量測
- 程式碼品質（30%）：介面清晰、可配置
- 效能優化（20%）：結果穩定可解讀
- 創新性（10%）：自動估算容量

---

## Case #9: 用 MSDN 複雜度文件選型，避免「用錯集合」

### Problem Statement（問題陳述）
業務場景：團隊常以直覺挑選集合類別，導致查詢/插入性能不佳。需建立「查詢模式 → 複雜度 → 集合」的選型流程。

技術挑戰：將需求語句轉譯為操作集合（精確、前綴、排序、範圍、插入模式），對照 MSDN 複雜度選擇。

影響範圍：降低錯選風險、節省重構成本、性能穩定。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未查閱集合複雜度文件。
2. 缺乏需求到操作的映射。
3. 未做可擴展性評估。

深層原因：
- 架構層面：欠缺設計準則。
- 技術層面：對資料結構認知薄弱。
- 流程層面：開發前缺少選型審核。

### Solution Design（解決方案設計）
解決策略：制定「查詢需求表」，將常見操作映射到 List/Dictionary/SortedList/SortedDictionary 的讀寫複雜度表，再基於資料分布/更新模式選擇。

實施步驟：
1. 建立操作清單
- 實作細節：精確查詢/前綴範圍/排序輸出/插入模式
- 所需資源：需求訪談
- 預估時間：1 小時

2. 建立映射表
- 實作細節：摘錄 MSDN 複雜度到表
- 所需資源：MSDN 文件
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 以程式內文件化方式保留複雜度備忘
// List.Find: O(n), Dictionary[key]: ~O(1), SortedList search: O(log n), insertion: O(n)
```

實際案例：原文以 MSDN 複雜度做選型，從 List → Dictionary/SortedList

實作環境：團隊流程 + .NET

實測數據：
- 改善前：List 搜尋 3,131,861 ticks
- 改善後：SortedList 39,294 ticks；Dictionary 精確 0 ms
- 改善幅度：80x～6000x（依場景）

Learning Points（學習要點）
核心知識點：
- 複雜度驅動選型
- 需求→操作→資料結構的映射
- 文檔閱讀力

技能要求：
- 必備技能：MSDN 檢索、對照表建立
- 進階技能：技術決策報告

延伸思考：
- 如何引入自動化 lint（選型檢查）？
- 何時需自實作資料結構？
- 如何納入記憶體成本？

Practice Exercise（練習題）
- 基礎練習：列出 5 類操作的最佳集合（30 分鐘）
- 進階練習：做一張選型海報（2 小時）
- 專案練習：建立選型審核流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：映射表完整
- 程式碼品質（30%）：文件化與維護
- 效能優化（20%）：能支援決策
- 創新性（10%）：自動化工具提案

---

## Case #10: 量化記憶體成本：多索引下 WorkingSet 的變化

### Problem Statement（問題陳述）
業務場景：新增索引提升查詢速度，但記憶體增加。需量化評估（如由 288MB 增至 340MB），確保佈署機器足以承載。

技術挑戰：如何在功能/性能與資源成本間權衡，並以數據說話。

影響範圍：佈署成本、資源配額、穩定性（避免 OOM）。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 兩份資料結構（List + Dictionary / SortedList）重複持有引用。
2. Dictionary/SortedList 的內部結構有額外 overhead。
3. 無量測即難以決策。

深層原因：
- 架構層面：未納入資源預算。
- 技術層面：忽略每筆/每結構的額外記憶體。
- 流程層面：缺乏資源監測流程。

### Solution Design（解決方案設計）
解決策略：在效能基準中加入記憶體量測，對比新增索引前後 WorkingSet（或 GC.GetTotalMemory），給出吞吐/延遲/記憶體的三維圖。

實施步驟：
1. 計量記憶體
- 實作細節：Environment.WorkingSet 或 GC.GetTotalMemory(true)
- 所需資源：.NET APIs
- 預估時間：0.5 小時

2. 報告對比
- 實作細節：呈現前後差異
- 所需資源：基準數據
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
Console.WriteLine($"WorkingSet: {Environment.WorkingSet / 1_000_000} MB");
```

實際案例：原文從 288MB → 340MB（新增 Dictionary 索引）

實作環境：.NET、Windows

實測數據：
- 改善前：≈ 288 MB
- 改善後：≈ 340 MB
- 改善幅度：+52 MB（約 +18%）

Learning Points（學習要點）
核心知識點：
- 多索引帶來的記憶體放大
- 量測方法與侷限（WorkingSet vs 堆）
- 成本/效益權衡

技能要求：
- 必備技能：記憶體量測 API
- 進階技能：壓測與資源曲線分析

延伸思考：
- 是否需壓縮資料或結構共享？
- 索引可否延遲建或部分建？
- 以磁碟索引替換部分記憶體索引？

Practice Exercise（練習題）
- 基礎練習：輸出建置後記憶體（30 分鐘）
- 進階練習：比對多種索引組合（2 小時）
- 專案練習：建立資源評估報告模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可比較兩版本記憶體
- 程式碼品質（30%）：可重複量測
- 效能優化（20%）：數據可支持決策
- 創新性（10%）：視覺化呈現

---

## Case #11: 名稱非唯一時的精確查詢：Dictionary<string, List<ContactData>>

### Problem Statement（問題陳述）
業務場景：真實世界姓名可能重複，使用 Dictionary<string, ContactData> 只能保留最後一筆。需支援同名多筆的精確查詢結果。

技術挑戰：在保留 O(1) 近似查詢的同時，回傳多筆結果並保持易用 API。

影響範圍：查詢正確性、資料完整性、API 介面。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Dictionary key 不可重複，覆蓋舊值。
2. 單值映射不適用多筆結果。
3. 資料建模未考慮非唯一情形。

深層原因：
- 架構層面：缺乏一對多建模。
- 技術層面：索引值型別選擇不當。
- 流程層面：需求分析忽略資料實態。

### Solution Design（解決方案設計）
解決策略：使用 Dictionary<string, List<ContactData>> 建桶（bucket），以 TryGetValue 取得清單，保持 O(1) 近似查詢。

實施步驟：
1. 調整索引值型別
- 實作細節：新增或附加至 List bucket
- 所需資源：Dictionary、List
- 預估時間：1 小時

2. 改寫查詢 API
- 實作細節：回傳 IEnumerable<ContactData>
- 所需資源：C#
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
var nameIndex = new Dictionary<string, List<ContactData>>();
void AddToNameIndex(ContactData cd)
{
    if (!nameIndex.TryGetValue(cd.Name, out var bucket))
    {
        bucket = new List<ContactData>();
        nameIndex[cd.Name] = bucket;
    }
    bucket.Add(cd);
}
IEnumerable<ContactData> FindByName(string name)
    => nameIndex.TryGetValue(name, out var bucket) ? bucket : Array.Empty<ContactData>();
```

實際案例：原文提及 Dictionary 限制；此為延伸正確建模

實作環境：.NET、C#

實測數據：
- 改善前：覆蓋舊值、結果不完整
- 改善後：完整回傳同名清單；查詢近 O(1)
- 改善幅度：正確性 100%；時間維持近 O(1)

Learning Points（學習要點）
核心知識點：
- 一對多索引建模
- TryGetValue 慣用法
- API 簡潔回傳多筆

技能要求：
- 必備技能：Dictionary 進階用法
- 進階技能：索引值結構設計

延伸思考：
- 需否加入排序或去重邏輯？
- 記憶體是否成為新壓力？
- 是否要限制 bucket 大小？

Practice Exercise（練習題）
- 基礎練習：改寫為 List bucket（30 分鐘）
- 進階練習：為 bucket 加入排序（2 小時）
- 專案練習：通用 MultiIndex 建模（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確處理重名
- 程式碼品質（30%）：API 清晰
- 效能優化（20%）：近 O(1) 查詢
- 創新性（10%）：易擴充至多欄位

---

## Case #12: 避免查詢時動態排序，改以預排序索引

### Problem Statement（問題陳述）
業務場景：某些功能需即時依欄位排序輸出，開發者傾向在查詢時計算 List.Sort，導致高延遲與 GC 壓力。

技術挑戰：將 O(n log n) 的排序成本移出熱路徑，改以預排序索引支援 O(1) 迭代輸出。

影響範圍：吞吐、延遲穩定性、使用者體驗。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. List.Sort 每次執行 O(n log n)。
2. 查詢頻率高會造成頻繁重算。
3. 無預排序結構可直接迭代。

深層原因：
- 架構層面：計算搬運未分離（寫入 vs 讀取）
- 技術層面：忽略 Sorted 系列集合
- 流程層面：未經過熱路徑分析

### Solution Design（解決方案設計）
解決策略：改以 SortedList/SortedDictionary 維持有序，查詢時直接迭代已排序的 Keys/Values。

實施步驟：
1. 建立預排序索引
- 實作細節：載入時維護
- 所需資源：SortedList/SortedDictionary
- 預估時間：1 小時

2. 移除查詢時計算
- 實作細節：把 Sort 移出查詢路徑
- 所需資源：N/A
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
// 壞例子：熱路徑動態排序
// contacts.Sort((a,b) => string.Compare(a.Name, b.Name)); // O(n log n)

// 好例子：直接迭代預排序索引
foreach (var kv in nameIndex) { /* 已排序 */ }
```

實際案例：原文建議用 Sorted 系列以 O(1) 取得有序輸出

實作環境：.NET、C#

實測數據：
- 改善前：每次排序 O(n log n)
- 改善後：遍歷 O(n)，單查詢延遲顯著降低
- 改善幅度：視查詢頻率與 n 而定，通常大幅

Learning Points（學習要點）
核心知識點：
- 將計算移出熱路徑
- 預計算/物化的概念
- 有序索引的迭代特性

技能要求：
- 必備技能：Sorted 集合
- 進階技能：熱路徑追蹤

延伸思考：
- 更新頻率高時的折衷？
- 可否批次重建索引？
- 多排序鍵如何處理？

Practice Exercise（練習題）
- 基礎練習：從 Sort 改為 SortedList 輸出（30 分鐘）
- 進階練習：同時支援兩種排序鍵（2 小時）
- 專案練習：索引刷新策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能輸出排序結果
- 程式碼品質（30%）：結構清楚
- 效能優化（20%）：移除熱路徑重算
- 創新性（10%）：刷新策略

---

## Case #13: 即時打字過濾（type-ahead）以前綴範圍查詢實作

### Problem Statement（問題陳述）
業務場景：類手機通訊錄輸入時即時過濾清單，隨輸入長度增加結果逐步縮小，需流暢體驗。

技術挑戰：需要隨字元數成長維持低延遲，並避免每次全表掃描。

影響範圍：使用者體驗、互動延遲、CPU 使用率。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. List.FindAll 每次 O(n) 掃描影響流暢性。
2. Dictionary 缺序，不支援範圍。
3. 缺少上下界快速定位。

深層原因：
- 架構層面：未為互動式體驗設計資料結構。
- 技術層面：前綴範圍策略缺失。
- 流程層面：缺熱路徑壓測。

### Solution Design（解決方案設計）
解決策略：用 SortedList 以鍵排序，對於每次輸入變化以 BinarySearch(prefixLow)、BinarySearch(prefixHigh) 取得子區間，僅遍歷該區間。

實施步驟：
1. 排序索引
- 實作細節：以目標欄位（如 Phone/Name）建 SortedList
- 所需資源：SortedList
- 預估時間：1 小時

2. 範圍查詢
- 實作細節：prefixHigh=下一字典序（數字例：+1）
- 所需資源：BinarySearch（Case #4）
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
IEnumerable<ContactData> FilterByPhonePrefix(string prefix)
{
    int start = BinarySearch(phoneIndex, prefix);
    // 對於數字前綴，求下一個前綴（例：0928-1234 -> 0928-1235）
    string next = "0928-" + (int.Parse(prefix.Substring(5)) + 1).ToString("D4");
    int end = BinarySearch(phoneIndex, next);
    for (int i = start; i < end; i++) yield return phoneIndex.Values[i];
}
```

實際案例：原文展示以 "0928-1234" ~ "0928-1235" 取範圍

實作環境：.NET、C#

實測數據：
- 改善前：List 前綴 ≈ 240 ms/百萬筆
- 改善後：O(log n + k)，在百萬筆下查界限極快
- 改善幅度：視 k 而定，通常顯著

Learning Points（學習要點）
核心知識點：
- 字典序與上界計算
- 以範圍取代過濾掃描
- 使用者輸入節流/去抖（debounce）

技能要求：
- 必備技能：BinarySearch、字串操作
- 進階技能：UI 互動優化（debounce）

延伸思考：
- 一般字串上界如何計算？（可用 prefix + '\uffff'）
- 非 ASCII 情境？
- 多欄位聯合前綴？

Practice Exercise（練習題）
- 基礎練習：完成 Phone 前綴匹配（30 分鐘）
- 進階練習：通用字串前綴（2 小時）
- 專案練習：整合 UI，實作 debounce + 範圍查詢（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：輸入即時過濾
- 程式碼品質（30%）：邏輯清晰、邊界正確
- 效能優化（20%）：流暢無卡頓
- 創新性（10%）：支持模糊度量

---

## Case #14: 兩層迴圈與迴圈內重工的效能陷阱

### Problem Statement（問題陳述）
業務場景：常見邏輯錯誤包含兩層迴圈順序不當、或將不必要的操作放在迴圈內，導致成倍數的時間浪費。

技術挑戰：辨識可外提的計算、調整迴圈次序以降低複雜度。

影響範圍：CPU 使用率、響應時間、能源成本。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 迴圈內做不變計算（如格式化、IO）。
2. 內外層迴圈順序錯導致資料區域性差或重複比較。
3. 單次查詢內做多次掃描。

深層原因：
- 架構層面：未抽離不可變計算。
- 技術層面：對時間複雜度不敏感。
- 流程層面：缺少效能 code review 專項。

### Solution Design（解決方案設計）
解決策略：外提不變計算、以索引替代內層掃描、調整迴圈順序與資料結構配合以降維。

實施步驟：
1. 迴圈審視
- 實作細節：找出不變量，移出迴圈
- 所需資源：程式碼審查
- 預估時間：0.5 小時

2. 引入索引
- 實作細節：內層 Find → Dictionary O(1)
- 所需資源：Dictionary
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 壞例子：內層線性 Find
foreach (var a in listA)
    foreach (var b in listB)
        if (listC.Find(x => x.Key == b.Key) != null) { /* ... */ }

// 好例子：先建索引 → 迴圈內 O(1)
var cIndex = listC.ToDictionary(x => x.Key);
foreach (var a in listA)
    foreach (var b in listB)
        if (cIndex.ContainsKey(b.Key)) { /* ... */ }
```

實際案例：原文指出常見迴圈錯放造成倍數耗時

實作環境：.NET、C#

實測數據：
- 改善前：O(n*m*k)
- 改善後：O(n*m)（使用 O(1) 取代內層掃描）
- 改善幅度：數量級下降

Learning Points（學習要點）
核心知識點：
- 外提不變量
- 以索引取代掃描
- 數據區域性與快取友善

技能要求：
- 必備技能：時間複雜度分析
- 進階技能：效能 code review

延伸思考：
- 何時要進一步改用 Join 結構？
- 是否要改變資料儲存型態？
- 可否平行化？

Practice Exercise（練習題）
- 基礎練習：找出並外提不變計算（30 分鐘）
- 進階練習：以索引取代內層查找（2 小時）
- 專案練習：撰寫效能審查清單（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：重構正確
- 程式碼品質（30%）：可讀可維護
- 效能優化（20%）：複雜度下降
- 創新性（10%）：審查工具/腳本

---

## Case #15: SortedList vs SortedDictionary 的選型抉擇

### Problem Statement（問題陳述）
業務場景：已決定使用排序結構，但需判斷在插入、搜尋、記憶體、索引需求上是選 SortedList 還是 SortedDictionary。

技術挑戰：理解兩者在插入成本、索引訪問（by index）、記憶體占用與迭代性能的差異。

影響範圍：載入時間、更新性能、記憶體占用、API 便利性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. SortedList 插入非末端 O(n)、搜尋 O(log n)；索引 by position 快。
2. SortedDictionary 插入/搜尋 O(log n)、無 by index。
3. 資料到達模式與 API 需求不同。

深層原因：
- 架構層面：資料流型態（批次 vs 實時）未納入。
- 技術層面：忽略 by-index 的需求與優勢。
- 流程層面：未做工作負載分類。

### Solution Design（解決方案設計）
解決策略：以工作負載分類：
- 批次載入且常順序輸出/按位置訪問 → SortedList
- 實時插入/刪除多 → SortedDictionary

實施步驟：
1. 收集工作負載
- 實作細節：插入/查詢/遍歷比例
- 所需資源：需求分析
- 預估時間：1 小時

2. 原型測試
- 實作細節：兩者小型原型比較
- 所需資源：.NET
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
// 只需搜尋 + 迭代 + by index: SortedList
var idx1 = new SortedList<string, ContactData>();

// 實時寫入多、頻繁更新：SortedDictionary
var idx2 = new SortedDictionary<string, ContactData>();
```

實際案例：原文列出 SortedList 與 SortedDictionary 的考量

實作環境：.NET、C#

實測數據：
- 改善前：不當選型導致插入或查詢成本過高
- 改善後：依負載選型，整體延遲/建置時間下降
- 改善幅度：依負載而定，通常顯著

Learning Points（學習要點）
核心知識點：
- 兩種排序集合的差異
- 工作負載驅動選型
- by index 的價值

技能要求：
- 必備技能：集合 API 認知
- 進階技能：負載建模

延伸思考：
- 是否需要自建雙結構混合？
- 記憶體占用如何比較？
- 如何在運行期切換策略？

Practice Exercise（練習題）
- 基礎練習：用兩者各建 10 萬筆並比較插入（30 分鐘）
- 進階練習：加入更新/刪除測試（2 小時）
- 專案練習：撰寫自動化選型基準（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：基準腳本可運行
- 程式碼品質（30%）：結構清晰、報表化
- 效能優化（20%）：數據可支持選型
- 創新性（10%）：自動化推薦

---

## Case #16: 從 List → SortedList 的搜尋性能飛躍（80 倍～近 6000 倍）

### Problem Statement（問題陳述）
業務場景：對姓名/電話的搜尋在 100 萬筆時需可在低毫秒回應，且須對 1 億筆具可擴展性。現況 List 搜尋性能不足。

技術挑戰：在不犧牲過多建置時間與記憶體下，將搜尋延遲大幅壓低。

影響範圍：查詢延遲、吞吐、SLA 可靠度。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. List.Find O(n) → 3,131,861 ticks
2. SortedList 二分 O(log n) → 39,294 ticks
3. 1 億筆時差距擴大至近 6000 倍

深層原因：
- 架構層面：資料結構選型未以查詢為導向
- 技術層面：忽略對數級的優勢
- 流程層面：缺少以數據支持的改造

### Solution Design（解決方案設計）
解決策略：將熱查詢移轉至 SortedList 的排序索引，使用二分搜尋；保留 Dictionary 供精確即時鍵查。

實施步驟：
1. 建立 SortedList 索引
- 實作細節：對熱欄位建索引
- 所需資源：SortedList
- 預估時間：1 小時

2. 搜尋切換
- 實作細節：以 BinarySearch 查目標 key/範圍
- 所需資源：BinarySearch API
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// List 基線（3,131,861 ticks @ 1M）
var hit = contacts.Find(x => x.Name == "A123456");

// SortedList（39,294 ticks @ 1M）
var hit2 = nameIndex["A123456"]; // 或 BinarySearch 尋位
```

實際案例：原文提供 ticks 與外插

實作環境：.NET、C#

實測數據：
- 改善前：3,131,861 ticks（List @1M）
- 改善後：39,294 ticks（SortedList @1M）
- 改善幅度：約 80 倍；@100M 約 5,978 倍

Learning Points（學習要點）
核心知識點：
- O(n) → O(log n) 的質變
- 以資料結構選型解鎖性能
- 以 ticks 作相對比較

技能要求：
- 必備技能：SortedList、Stopwatch
- 進階技能：性能策略與取捨

延伸思考：
- 讀多寫少 vs 寫多讀少怎選？
- 二級快取/熱資料如何配合？
- 分片（sharding）是否需要？

Practice Exercise（練習題）
- 基礎練習：重現 ticks 對比（30 分鐘）
- 進階練習：對 10 萬/100 萬/500 萬做曲線（2 小時）
- 專案練習：將策略封裝為可插拔模組（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：數據可重現
- 程式碼品質（30%）：模組化
- 效能優化（20%）：策略可配置
- 創新性（10%）：自動選路

---

案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case 1（List 基準測試）
  - Case 8（預先容量）
  - Case 9（MSDN 複雜度選型）
  - Case 10（記憶體量測）
- 中級（需要一定基礎）
  - Case 2（Dictionary 精確索引）
  - Case 3（SortedList 前綴範圍）
  - Case 4（二分搜尋實作）
  - Case 5（多索引架構）
  - Case 6（擴展性外插）
  - Case 7（載入順序優化）
  - Case 12（移除查詢時排序）
  - Case 13（type-ahead 前綴）
  - Case 15（SortedList vs SortedDictionary）
  - Case 16（List→SortedList 性能飛躍）
- 高級（需要深厚經驗）
  - Case 11（非唯一鍵建模）
  - Case 14（效能 code review 與陷阱）

2. 按技術領域分類
- 架構設計類：Case 5, 9, 12, 15
- 效能優化類：Case 1, 2, 3, 4, 6, 7, 8, 10, 13, 16
- 整合開發類：Case 5, 13
- 除錯診斷類：Case 1, 6, 10, 14
- 安全防護類：不適用（本篇不涉及安全議題）

3. 按學習目標分類
- 概念理解型：Case 6, 9, 15
- 技能練習型：Case 2, 3, 4, 7, 8, 13
- 問題解決型：Case 1, 5, 10, 12, 14, 16
- 創新應用型：Case 11（多值索引建模）

案例關聯圖（學習路徑建議）
- 起點（基礎與量測）：先學 Case 1（建立基準與感知 O(n)），Case 9（懂得看 MSDN 複雜度），Case 10（學會量化記憶體）
- 精確查詢優化：Case 2（Dictionary）
- 範圍/排序查詢：Case 3（SortedList 前綴）、Case 4（二分搜尋）
- 多需求整合：Case 5（多索引架構）、Case 12（移除查詢時排序）
- 可擴展性認知：Case 6（1M→100M 外插）、Case 7（載入順序）
- 進階資料建模：Case 11（非唯一鍵索引）
- 互動體驗：Case 13（type-ahead）
- 效能習慣與陷阱：Case 14（迴圈與重工）
- 選型深化：Case 15（SortedList vs SortedDictionary）
- 總結強化：Case 16（List→SortedList 大幅提升的量化）

依賴關係簡述：
- Case 3 依賴 Case 4（BinarySearch）
- Case 5 依賴 Case 2/3（索引能力）
- Case 13 依賴 Case 3/4（前綴範圍）
- Case 16 建議在理解 Case 1/3/6 後進行

完整學習路徑建議：
1 → 9 → 10 → 2 → 3 → 4 → 5 → 12 → 6 → 7 → 11 → 13 → 14 → 15 → 16

說明：
- 先建立量測與選型基礎，再解決精確與前綴兩大類查詢，進而整合多索引與移除熱路徑重算；以外插與載入策略掌握可擴展性；之後補齊非唯一鍵建模與互動體驗；最後建立效能開發習慣與選型能力，用 Case 16 總結量化成果。