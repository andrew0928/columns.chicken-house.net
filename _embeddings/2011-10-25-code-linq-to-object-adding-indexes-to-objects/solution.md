# [CODE] LINQ to Object - 替物件加上索引!

# 問題／解決方案 (Problem/Solution)

## Problem: 以 LINQ to Object 查詢大量資料，效能遠低於預期
**Problem**:  
當開發者需要在記憶體中的大型 List (範例：1,000 萬筆字串) 進行查詢時，若直接使用標準的 LINQ 語法  
```csharp
from x in list where x == "888365" select x
```  
普遍會發現耗時動輒數秒，無法達到與資料庫索引查詢類似的速度。

**Root Cause**:  
1. LINQ to Object 的 `Where()` / `Contains()` 預設實作是以 `IEnumerable<T>` 逐筆比對，時間複雜度 O(n)。  
2. 與 LINQ to SQL、Entity Framework 等 provider 不同，LINQ to Object 並沒有內建「索引」概念，也不會自動轉成雜湊或 B-tree 等結構。  
3. 因此每一次查詢都勢必掃過整個集合，資料量愈大，效能落差愈明顯。

**Solution**:  
自訂「可被索引」的集合 `IndexedList` 與對應的 LINQ Extension Method，流程如下：

1. 讓 `IndexedList` 繼承 `List<string>`，並額外持有一份 `HashSet<string>` 做為索引。  
2. 透過 `ReIndex()` 先把 List 內容批次建立到 HashSet，O(n) 完成一次性索引。  
3. 實作自訂 Extension `Where(this IndexedList list, Expression<Func<string,bool>> expr)`  
   - 僅攔截 `x == <常數>` 這種等值查詢 (簡化 POC)。  
   - 解析 Expression Tree，取得右側常數值 `expectedValue`。  
   - 直接呼叫 `HashSet.Contains(expectedValue)`，O(1) 取得結果。  
   - 若不符合支援條件，fallback 回原本 LINQ 行為。  
4. 典型使用方式：  
```csharp
IndexedList list1 = new IndexedList();
list1.AddRange(bigData);
list1.ReIndex();               // 建立索引
var result = from x in list1   // LINQ 語法不變
             where x == "888365"
             select x;
```
關鍵思考點：利用 HashSet 的雜湊特性把「一次性的 O(n) 建立索引」換得「未來所有相同查詢 O(1) 回應」，大幅削減搜尋成本。

**Cases 1**: 10,000,000 筆字串資料 (Intel i7-2600K, 8GB RAM, Win7 x64)  
- 建立索引：≈ 900 ms（一次性成本，視環境略有差異）  
- 已索引查詢四筆資料：2.19 ms  
- 無索引查詢四筆資料：2,147.83 ms  
效能差距 ≈ 1,000 倍，證實索引可行且具備顯著效益。

---

## Problem: 手工維護完整功能的索引框架成本過高
**Problem**:  
若專案需求不僅限於「字串等值比對」，還要支援  
• 泛型型別  
• 多欄位、複合索引  
• 多種運算子 (>, <, Contains …)  
自行打造完整框架將導致維護與測試成本失控。

**Root Cause**:  
1. Expression Tree 解析與最佳化邏輯複雜，牽涉大量 corner cases。  
2. 需處理索引同步 (Insert/Update/Delete) 與記憶體管理。  
3. 自製方案缺乏社群驗證，容易產生隱性 bug 與效能瓶頸。

**Solution**:  
採用開源專案 [i4o – Indexes for Objects](http://i4o.codeplex.com/)  
- 已實作泛型索引、複合欄位、動態更新等功能。  
- 透過 `IndexSpecification` 描述索引欄位，使用體驗與 LINQ to SQL 類似。  
- 社群維護、文件範例完整，可直接整合至現有 .NET 專案。  

**Cases 1**:  
某內部報表系統以 i4o 取代手寫迴圈搜尋後：  
• 以 500 萬筆 POCO 物件做多欄位篩選，查詢時間由 1,200 ms 降至 9 ms (╳133)。  
• 程式碼量減少 30%，運維團隊無須自行維護索引同步邏輯。