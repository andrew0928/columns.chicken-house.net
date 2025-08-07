# LINQ to Object #2, Indexes for Objects  

# 問題／解決方案 (Problem/Solution)

## Problem: 使用 LINQ to Objects 在大量資料 ( List<T> ) 上查詢，效能無法接受  

**Problem**:  
當我們把一百萬筆以上的物件 (Foo) 放在記憶體裡，接著用  
```csharp
(from x in list1 where x.Text == "888365" select x).ToList();
```  
這種典型的 LINQ to Objects 語法篩選資料時，程式會以 O(n) 方式掃描整個集合。面對需要經常、即時查詢 (尤其是等值查詢) 的系統，這樣的延遲無法接受。  

**Root Cause**:  
List<T> 只是線性資料結構，Framework 並不替它自動維護任何索引。只要呼叫 Where(...) 就會走一次完整迭代；筆數愈大、條件愈複雜，時間就愈長。  

**Solution**:  
利用 i4o (Indexes for Objects) 函式庫，替物件集合在指定屬性上動態建立索引︰  
```csharp
IndexableCollection<Foo> list3 = list1.ToIndexableCollection();
list3.CreateIndexFor(i => i.Text)          // 建立 Text 欄位索引
     .CreateIndexFor(i => i.Number);       // 建立 Number 欄位索引
var result = (from x in list3
              where x.Text == "888365"
              select x.Text).ToList();
```  
i4o 會在背景使用平衡樹結構維護索引，之後的 Where/First/Any … 等 LINQ 運算子就可以走 O(log n) 的查詢路徑，直接命中候選資料列，大幅降低搜尋時間。  

**Cases 1**: 單次查詢效能  
資料量：1,000,000 筆 Foo  
‧ 無索引 List<T>：Query ≒ 200~300 ms  
‧ 自行實作 Dictionary 索引：Query < 5 ms (但功能侷限，只能等值比對)  
‧ i4o：  
  Build Index ≒ 150~200 ms (一次性)  
  Query < 1 ms  
建立完索引後，每一次查詢都能維持於毫秒等級，在需要大量、反覆查詢的情境中，總體效益遠大於第一次建立索引花費的時間。

---

## Problem: 手動實作索引 (例如用 Dictionary) 難以維護且功能受限  

**Problem**:  
為了加速等值查詢，開發者常自行用 Dictionary<TKey,List<T>> 之類結構幫某個欄位做索引；但這樣的客製做法只支援「==」運算子，若日後要加入範圍查詢、複合索引或同步多欄位，就得整組重寫。  

**Root Cause**:  
手動索引意味著程式需要自己維護新增、刪除、更新時的同步邏輯；而資料結構若只對齊單一查詢模式 (等值) 就很難再擴充到 Between / > / < 等需求。  

**Solution**:  
改用 i4o – 它已經實作  

1. 動態維護索引 (新增/刪除/修改自動更新)。  
2. 同時支援多欄位、多種比較運算子。  
3. LINQ Provider 介面 – 直接寫標準 LINQ 語法，i4o 會判斷是否可走索引路徑。  

示例：  
```csharp
// 同時對 Text 與 Number 建立索引
list3.CreateIndexFor(i => i.Text)
     .CreateIndexFor(i => i.Number);

// 可以立即寫範圍查詢
var r2 = list3.Where(f => f.Number > 100 && f.Number < 500).ToList();
```  

**Cases 1**: 維護成本  
‧ 手動 Dictionary：每種索引都得寫一次 Add/Remove/Update 邏輯，程式碼量倍增。  
‧ i4o：單行 CreateIndexFor(...) 即可，後續 CRUD 不需額外維護。  

**Cases 2**: 功能擴充  
‧ 客製 Dictionary ＝ 只能等值比對。  
‧ i4o ＝ 支援複合鍵、範圍查詢、排序、Top N … 等需求。  

透過 i4o，我們把「自己管索引」的負擔交給元件，保持了 LINQ 語法的易讀性，同時獲得接近資料庫層級的查詢性能。