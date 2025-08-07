# [CODE] LINQ to Object - 替物件加上索引!

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者想要「替 LINQ to Object 加上索引」？
LINQ to SQL、Entity Framework 等都有索引支援，但 LINQ to Object 沒有。當集合資料量大時，單純用 `List<T>.Contains` 等線性搜尋會產生 O(n) 的時間複雜度，導致效能低落，因此作者嘗試證明 LINQ to Object 也可以透過索引取得類似資料庫的效能提升。

## Q: 真的能用自訂 Extension Method 為 LINQ to Object 加上索引嗎？
可以。作者示範：
1. 先繼承 `List<string>`，做出 `IndexedList` 並額外持有 `HashSet<string>` 當索引。
2. 實作 `Where(this IndexedList …)` Extension Method，在符合「等值比對」的情況下直接查 `HashSet.Contains`，否則退回原生 LINQ 邏輯。
實驗證明 LINQ 執行時確實會呼叫這個自訂 `Where`，達到使用索引的效果。

## Q: 實測結果顯示，加索引與不加索引的速度差多少？
在 1,000 萬筆隨機字串中搜尋 4 筆指定資料：
‧ 未加索引：2147.83 ms  
‧ 加上 `HashSet` 索引：2.19 ms  
兩者落差約千倍，符合 O(n) 對比 O(1) 的理論。

## Q: 作者為什麼選擇 `HashSet` 來當索引結構？
因為實驗僅針對「等值比對 (`==`)」且不需要排序，`HashSet` 的 `Contains` 為 O(1) 時間複雜度，實作簡單又高速，足以證明概念。

## Q: 這份 Proof of Concept 有哪些限制？
1. 只處理 `List<string>`，沒做成泛型或可挑欄位的索引。  
2. 只支援 `==` 運算子，且常數必須寫在右側（如 `x == "123"`）。  
3. 若查詢條件不符合上述限制，就回退成原生 LINQ，不使用索引。

## Q: 若想用完整又實用的 LINQ 物件索引方案，有推薦的現成工具嗎？
有，作者指出 CodePlex 上的 i4o（Indexing for Objects）專案已提供較完整的索引功能，建議直接採用。

## Q: Embedded SQL 與 LINQ 有何相似之處？
兩者都是把查詢語言嵌入在一般程式碼中，經由編譯器或前處理器轉成一般資料存取呼叫，最終產生可執行的程式並達到查詢效果。