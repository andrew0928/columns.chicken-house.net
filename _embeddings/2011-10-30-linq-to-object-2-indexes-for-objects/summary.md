# LINQ to Object #2, Indexes for Objects

## 摘要提示
- i4o 函式庫: 介紹 indexes for objects（i4o）在 LINQ to Objects 場景中的應用與效益。
- 三種集合對照: 比較無索引 List、客製 IndexedList、i4o 的 IndexableCollection。
- 索引建立: 以 CreateIndexFor 建立屬性索引（如 Text、Number）。
- 查詢效能: 透過 Stopwatch 實測建立索引與查詢時間差異。
- 操作簡單: i4o 提供直覺 API，將現有集合轉為可索引集合並建索引。
- 相容 LINQ 語法: 仍使用標準 LINQ 查詢語法 where x.Text == "888365"。
- 客製索引限制: 自訂 IndexedList 僅支援 == 運算子，功能較受限。
- 擴充性: i4o 可為多個屬性建索引，利於多種查詢條件。
- 實務導向: 相較前一篇自製範例，i4o 是更「上得了檯面」的方案。
- 測試場景: 百萬筆 Foo 資料，觀察索引建立成本與查詢加速效果。

## 全文重點
本文延續前一篇以自製方式在 LINQ to Objects 場景中加入索引的嘗試，進一步引入更成熟可用的 i4o（indexes for objects）函式庫，示範其在實務程式中的用法與效能表現。作者建立三組資料集合進行對照：第一組是一般的 List<Foo>（不含索引），第二組是自行實作的 IndexedList（針對 Foo.Text 與 Foo.Number 建索引，但查詢僅支援 ==），第三組則是套用 i4o 的 IndexableCollection<Foo>。測試資料規模為 100 萬筆，並使用 Stopwatch 分別量測索引建立時間與查詢時間。

在程式實作上，List 版本無需額外動作，直接以 LINQ 進行 where 過濾；客製 IndexedList 需呼叫 ReIndex() 建索引，再執行查詢；i4o 版本則先將原本 List 轉為 IndexableCollection，再以 CreateIndexFor(i => i.Text).CreateIndexFor(i => i.Number) 建立索引，最後用相同的 LINQ 查詢語法執行過濾。三者雖在查詢語法上無異，但有無索引的效能差距，在大數據量下相當顯著；i4o 的優勢在於以最少改動就能為多個屬性建立索引，維持 LINQ 可讀性，同時獲得接近資料結構化查詢的加速效果。

相較於手工打造的索引結構，i4o 封裝了索引維護與查詢加速，且支援為不同屬性建立多個索引，使用上更直觀、泛用及易於整合現有程式碼。客製 IndexedList 的限制（僅支援 ==）凸顯了 i4o 在彈性上的優勢。整體而言，本文的結論是：若要在記憶體內以 LINQ to Objects 查詢大量物件，且需頻繁依特定欄位過濾，採用 i4o 能在接受的索引建立成本下，獲得可觀的查詢效能提升，並保留原有 LINQ 查詢的簡潔語法與可維護性。

## 段落重點
### 引言：從自製範例到實務方案
作者回顧上一回以自製方式結合 LINQ 與索引的示範，指出該作法仍屬初步嘗試，不夠成熟。本文轉向介紹可直接應用於實務的 i4o（indexes for objects）函式庫，目標是在不放棄 LINQ to Objects 可讀性的前提下，為物件集合加入可運作的索引機制，改善在大量資料情境下的查詢效率。此段為本文動機鋪陳：用成熟工具取代自製輪子，提升可用性與可維護性。

### 實驗設計：三種集合與測試方法
延續前一篇的情境，將查詢對象由 string 改為自訂類別 Foo，並建立三個對照組集合：1) 一般 List<Foo>，無索引；2) 自訂 IndexedList，針對 Foo.Text 與 Foo.Number 建索引，但查詢只支援 ==；3) 使用 i4o 的 IndexableCollection<Foo>。每組集合皆含約 100 萬筆資料，透過 Stopwatch 量測兩階段時間：索引建立時間（若需要）與執行 where x.Text == "888365" 的查詢時間。此設計可直接比較未索引與有索引情況的效能，並評估 i4o 的易用性與加速幅度。

### 程式重點：API 使用與索引建立
在無索引的 List 版本中，直接以標準 LINQ 語法查詢，作為基準。自訂 IndexedList 需先呼叫 ReIndex() 建立索引，再以相同 LINQ 語法查詢，顯示其功能可用但受限於運算子支援。i4o 版本則先將 List 轉為 IndexableCollection（ToIndexableCollection<Foo>()），接著對指定屬性呼叫 CreateIndexFor(i => i.Text) 與 CreateIndexFor(i => i.Number)，最後同樣以 LINQ 查詢。i4o 的 API 設計讓引入索引的改動極小，且可對多個欄位建立索引，提升多條件查詢的彈性。

### 結果與觀察：索引成本與查詢加速
實測輸出顯示三組在查詢時間上有明顯差距：未索引的 List 在百萬筆資料時查詢較慢；自訂 IndexedList 與 i4o 在完成索引後查詢明顯加速。雖然索引建立需額外時間，但對於多次查詢情境，其攤提成本後能帶來整體效益。相較之下，自訂 IndexedList 的可擴充性與運算子支援受限；i4o 則能以簡潔語法對多屬性建索引，維持 LINQ 查詢的一致性。綜合來看，i4o 提供了可上線的實務解法，適合在記憶體內對大量物件進行高頻率的條件查詢。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C# 語言與泛型（List<T>）
   - LINQ to Objects（查詢運算子、where 過濾）
   - 委派與 Lambda、Expression 樹（以屬性選取器定義索引）
   - 基本資料結構（Dictionary/Hash 索引概念）
   - 基本效能量測（Stopwatch）

2. 核心概念：
   - LINQ to Objects：在記憶體集合上以查詢語法操作物件資料。
   - 物件索引化（Indexes for Objects）：為集合中的某些屬性建立索引以加速查詢。
   - i4o 函式庫：提供 IndexableCollection 與 CreateIndexFor API，自動維護索引並最佳化查詢。
   - 自訂索引容器對照組：以自建 IndexedList/Dictionary 支援 == 查詢的索引。
   - 成本-效益權衡：建立索引需要時間與記憶體，需視查詢次數與資料規模決定是否值得。

3. 技術依賴：
   - .NET/CLR 與 C# 語言特性（泛型、LINQ、Lambda/Expression）
   - i4o Library（IndexableCollection、CreateIndexFor）
   - 基礎索引結構（以字典/雜湊做鍵值對應）與相容的相等比較器
   - Stopwatch 進行建立索引與查詢時間量測

4. 應用場景：
   - 大量資料的記憶體集合（如百萬筆）需頻繁以等值條件過濾
   - Read-heavy、資料相對穩定，重建索引頻率低的工作負載
   - 需在未使用資料庫的情況下，為領域模型提供查詢加速
   - 批次或互動式查詢系統中，對特定屬性（如 Text、Number）進行高速檢索

### 學習路徑建議
1. 入門者路徑：
   - 熟悉 C# 泛型集合（List<T>）、LINQ 基本語法（where/select）
   - 了解 Stopwatch 量測方法，對單純 List<T> 做等值查詢並觀察耗時
   - 練習以 Dictionary 建立簡單鍵索引，體會索引與掃描的差異

2. 進階者路徑：
   - 導入 i4o，將 List<T> 轉為 IndexableCollection<T>
   - 使用 CreateIndexFor(i => i.Property) 為多個屬性建立索引
   - 比較「無索引 vs 自建索引 vs i4o」在建立索引與查詢上的時間差異
   - 分析查詢分佈、資料更新頻率，評估索引建立時機與策略

3. 實戰路徑：
   - 在實際專案中挑選查詢頻繁、選擇性高的欄位建立索引
   - 以情境測試（不同資料量、查詢次數）驗證是否達到加速門檻
   - 封裝索引建立與重建（ReIndex/CreateIndexFor）流程與生命週期管理
   - 監控記憶體占用與延遲，調整索引數量與更新策略

### 關鍵要點清單
- LINQ to Objects 的限制與優勢: 記憶體內查詢易用但大型資料等值過濾會退化為全掃描 (優先級: 高)
- 物件索引化的必要性: 對高頻率等值查詢以索引加速可大幅降低延遲 (優先級: 高)
- i4o 函式庫概念: 提供 IndexableCollection 與 CreateIndexFor，簡化索引建立與維護 (優先級: 高)
- CreateIndexFor 用法: 使用 Lambda 指定屬性，如 CreateIndexFor(i => i.Text).CreateIndexFor(i => i.Number) (優先級: 高)
- 建立索引的成本: 索引建立需時間與記憶體，須以查詢次數與資料規模平衡 (優先級: 高)
- 等值查詢的適配性: 本文示範以 == 為主，最能受惠於雜湊式索引 (優先級: 高)
- 自建 IndexedList 對照: 以 Dictionary 實作索引能加速，但功能與維護性不如 i4o (優先級: 中)
- 資料更新與索引同步: 新增/刪除/修改需觸發索引更新或重建（如 ReIndex） (優先級: 高)
- Stopwatch 效能量測: 實務上以精確量測比較「建立索引」與「查詢」的時間 (優先級: 中)
- 多欄位索引策略: 只為高選擇性與高使用頻率的屬性建立索引以避免過度成本 (優先級: 高)
- 記憶體占用考量: 索引會增加 RAM 使用量，需與系統資源做取捨 (優先級: 中)
- 轉換集合型別: 以 ToIndexableCollection<T>() 將 List<T> 升級為可索引集合 (優先級: 中)
- 查詢模式分析: 若查詢條件多變或非等值，需評估其他資料結構或不同索引策略 (優先級: 中)
- 快速回傳需求情境: 互動式查詢、Autocomplete、即時過濾等能顯著受益 (優先級: 中)
- 測試與基準: 在目標資料量（如百萬筆）與真實查詢負載下做基準測試 (優先級: 高)