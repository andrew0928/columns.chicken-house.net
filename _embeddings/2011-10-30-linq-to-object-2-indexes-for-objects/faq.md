# LINQ to Object #2, Indexes for Objects

# 問答集 (FAQ, frequently asked questions and answers)

## Q: i4o (indexes for objects) 這套函式庫的用途是什麼？
i4o 讓 .NET 開發者能在記憶體中的物件集合上建立索引，之後透過 LINQ 查詢時，就能像使用資料庫索引一樣大幅提升查詢效率。

## Q: 如何在 `IndexableCollection<T>` 上使用 i4o 建立索引？
先把原本的 `IEnumerable<T>` 轉成 `IndexableCollection<T>`，接著呼叫 `CreateIndexFor`，並傳入要索引的屬性 Lambda，例如：
```csharp
IndexableCollection<Foo> list = originalList.ToIndexableCollection<Foo>();
list.CreateIndexFor(i => i.Text)
    .CreateIndexFor(i => i.Number);
```
這段程式就同時為 `Text` 與 `Number` 兩個屬性建立索引。

## Q: 文章中比較了哪三種查詢方式？
1. 不使用索引的 `List<Foo>`。  
2. 自訂 `IndexedList`，在內部以 Dictionary 方式維護索引，僅支援 `==` 運算子。  
3. 使用 i4o 的 `IndexableCollection<Foo>`，可針對多個屬性建立索引。

## Q: 建立索引與不使用索引的查詢效能差異為何？
從範例輸出來看：
- 不使用索引 (List) 直接查詢需要最多時間。
- 自訂 `IndexedList` 需額外時間重建索引 (`ReIndex()`)，但查詢較快。
- i4o 在建立索引後，查詢時間最短，且可對多欄位同時加索引。

## Q: 如果要在自訂的 `IndexedList` 重新產生索引，該怎麼做？
呼叫 `ReIndex()` 方法即可，之後就能用 LINQ 針對已索引欄位進行快速查詢。