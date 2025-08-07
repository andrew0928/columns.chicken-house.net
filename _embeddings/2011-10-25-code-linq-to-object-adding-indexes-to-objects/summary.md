# [CODE] LINQ to Object - 替物件加上索引!

## 摘要提示
- 動機: 看到 LINQ to Object 效能問題後，作者想證明「物件」也能像資料庫一樣透過索引加速查詢。  
- Extension Method: 透過自訂 `Where(this IndexedList …)` 取代預設實作，攔截 LINQ 查詢並導向索引。  
- POC 限制: 僅針對 `List<string>`、`==` 運算與常數比對，示範最簡可行案例。  
- HashSet 索引: 利用 `HashSet` O(1) 的查找時間實作索引，並提供 `ReIndex()` 重新建立索引。  
- 效能差異: 1,000 萬筆資料實測，未索引需 2147 ms，有索引僅 2.19 ms，差距達千倍以上。  
- Expression 解析: 以 `Expression<Func<string,bool>>` 取得運算式樹，檢查 `BinaryExpression`、`ExpressionType.Equal` 判斷是否可走索引。  
- 可行性: 實驗證明「LINQ to Object 可支援索引」概念成立。  
- 限制與不足: POC 僅示範核心原理，功能單一且無泛型/多欄位排序支援。  
- 既有方案: 社群已有完整實作 i4o（Indexing for Objects），功能更完整。  
- 建議: 若需實務應用，直接採用 i4o 等成熟套件，而非重造輪子。  

## 全文重點
作者因閱讀 darkthread 探討 LINQ to Object 效能的文章，產生「替物件集合加上索引」的想法，於是撰寫一段 Proof of Concept。核心作法是繼承 `List<string>` 成為 `IndexedList`，並以 `HashSet<string>` 儲存同內容的索引。在 `IndexedList` 上實作專用 LINQ Extension Method `Where`，攔截查詢，解析傳入的 `Expression<Func<string,bool>>`；當條件是「常數字串相等運算」時，就以 `_index.Contains(value)` 直接判斷，否則落回原本 `List.Where()` 逐筆掃描。接著作者產生 1,000 萬筆隨機字串，分別放入含索引、無索引兩份集合，比較四次相等查詢的耗時：含索引 2.19 ms、無索引 2147.83 ms，顯示 O(1) 與 O(n) 的巨大差距。雖然 POC 已證明概念，但功能仍極度簡化，只支援單一型別與比對運算；作者指出對於真正需求，可採用 codeplex 上的 i4o 專案，它已支援泛型、多欄位與更完整的索引能力，本文僅供學習 LINQ 與 Expression Tree 介入技巧之用。

## 段落重點
### 緒論：從效能問題談起
作者距離上篇文章已十個月，因閱讀 darkthread 對 LINQ to Object 效能陷阱的探討，產生「LINQ 為何不能像資料庫那樣有索引」的疑問，決定動手實驗。

### Embedded SQL 與 LINQ 類比
回顧早期 C/C++ 使用 Embedded SQL 的範例，說明「在程式語言內嵌查詢指令」的概念，並點出 LINQ 運作與編譯期翻譯的相似性，鋪陳可替 LINQ to Object 擴充功能的可能。

### 建立 Extension Method 的 POC
先繼承 `List<string>` 為 `IndexedList`，再加入同名 `Where` Extension Method 以攔截 LINQ 查詢，證明編譯器確實會呼叫自訂方法，是索引化的切入點。

### 簡化需求與資料結構選擇
為了將程式縮小到一眼可懂的 POC，限定：只處理字串、只支援 `==`、常數需在右邊；同時因不需排序選擇 `HashSet` 做索引，取得 O(1) 查找複雜度。

### IndexedList 與 ReIndex 實作
在 `IndexedList` 中新增 `_index` 欄位及 `ReIndex()`，遍歷清單將所有值存進 `HashSet`，建立快速索引；並展示完整程式碼。

### 效能測試流程
產生 1,000 萬筆亂數字串，分別建構 `IndexedList` 與 `List<string>`；測量重建索引時間後，對四組指定值進行 LINQ 查詢，比較索引與非索引的耗時差異。

### 測試結果與分析
在 i7-2600K+8 GB Windows 7 環境，索引版查詢僅 2.19 ms，非索引需 2147.83 ms；說明 HashSet 與 List 線性搜尋的理論複雜度差距在實務上的體現。

### Extension Method 解析式處理細節
說明 `Expression<Func<string,bool>>` 如何被轉為運算式樹，透過 `expr.Body.NodeType==Equal` 及 `ConstantExpression` 取值來判定是否可走索引；不符條件則回退原生 `Where`。

### 反思：POC 的侷限與現成方案
雖已證明 LINQ to Object 可透過索引大幅提速，但 POC 功能陽春，且若直接使用 HashSet 亦能達成相同目的；社群已有成熟的 i4o 套件支援泛型、多欄位與排序，實務上應優先採用。

### 結語
本實驗提供一個理解 Expression Tree 與 Extension Method 攔截技巧的範例，並提醒開發者：掌握索引概念與正確工具，才能在 LINQ to Object 場景中兼顧語法優雅與執行效能。