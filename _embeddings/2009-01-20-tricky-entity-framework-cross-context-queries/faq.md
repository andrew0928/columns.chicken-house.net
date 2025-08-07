# 難搞的 Entity Framework - 跨越 Context 的查詢

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 分割成多個 .edmx 檔會帶來哪些問題？
1. 每個 .edmx 都會產生自己的 ObjectContext，若兩邊都有物件變動，就必須對每一個 ObjectContext 各自呼叫 SaveChanges。  
2. 無論是 LINQ to Entities 還是 eSQL，都無法在不同 .edmx 所屬的 ObjectContext 之間做 JOIN，會直接拋出「不支援跨 context 的操作」錯誤。  
3. AssociationSet 無法跨越不同的 .edmx，因此跨 .edmx 的 Entity 不能透過 Navigation Property 來導覽或關聯。

## Q: 要如何在 Entity Framework 中對大型、模組化的資料庫進行跨 .edmx 的 JOIN 查詢？
做法是在執行階段建立「單一」ObjectContext，但在 EntityConnection 的連接字串中同時指定多組 .csdl、.ssdl、.msl 檔案。例如：  
```
metadata=res://*/Model1.csdl|res://*/Model1.ssdl|res://*/Model1.msl|
        res://*/Model2.csdl|res://*/Model2.ssdl|res://*/Model2.msl;
...
```  
如此一來就能讓 eSQL 透過同一個 ObjectContext 存取兩份 .edmx 之中的所有 EntitySet；LINQ 查詢則可用 `CreateQuery<T>()` 產生對應的 EntitySet 來使用。

## Q: 這種「多組 metadata 同一條連接字串」的作法能滿足哪些需求？
1. 可將每個模組的 .edmx 與商業邏輯封裝在各自的 assembly 中，保持模組化。  
2. 不同模組定義的 EntitySet 可以在 eSQL 中互相 JOIN。  
3. 基本的 LINQ 查詢仍可使用（透過 `CreateQuery<T>()`）。  
4. 新增或修改某個模組時，其餘模組不需要重新編譯。