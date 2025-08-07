# 該如何學好「寫程式」#2 ─ 為什麼 Programmer 該學資料結構？？

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼程式設計師一定要學資料結構？
資料結構決定了程式在「處理大量資料」時能否又快又穩。  
懂資料結構才能：  
1. 看懂 time complexity，預估程式在資料成長 10 倍、100 倍後的速度。  
2. 在 .NET 的 `System.Collections.Generic` 等函式庫裡選到「對的容器」，把同一支邏輯寫得快上數十倍、甚至數千倍。  
3. 避免寫出「語法很炫卻效能可笑」的程式碼，真正把工具用在對的地方。

---

## Q: 如果用 `List<ContactData>` 來搜尋一百萬筆通訊錄資料，效能會怎麼變化？
`List<T>` 的搜尋 (`Find`/`FindAll`) 為 O(n)。  
• 一百萬筆時約 3,131,861 ticks。  
• 當資料量增為一億筆，理論上要再乘 100 倍，約 313,186,100 ticks（約 100 倍變慢）。  
線性成長讓程式很快就慢到無法接受。

---

## Q: 把 `Dictionary<TKey,TValue>` 拿來當索引就萬事 OK 嗎？為什麼它無法滿足所有需求？
`Dictionary` 的索引是 HashTable，做 **完全符合 (exact match)** 查詢時是 O(1)，非常快；  
但它有兩個限制：  
1. Key 不能重複，無法拿來當「電話號碼」「郵件地址」等可能重複欄位的多重索引。  
2. 無法保證元素順序，也不支援區間或前綴查詢（如 `StartsWith("0928-1234")`），所以排序、範圍搜尋都做不到。

---

## Q: 作者最後用什麼做法同時解決「快速搜尋」與「可排序／區間查詢」？效能差多少？
做法：  
1. 針對每個索引欄位各建一個 `SortedList<string, ContactData>`。  
2. `SortedList` 內部保持排序，取值是 O(log n)；再配合自行實作的 Binary Search，可做前綴或區間搜尋。  

效能對比（一百萬筆資料）：  
• `List` 搜尋：3,131,861 ticks  
• `SortedList` + Binary Search：39,294 ticks（快約 80 倍）  

推估一億筆時，差距可達約 6,000 倍。

---

## Q: `List`、`Dictionary`、`SortedList` 在「新增」與「搜尋」的時間複雜度各是多少？
1. `List<T>`  
   • Add：O(1) (無擴充) / O(n) (觸發擴充)  
   • Search：O(n)  

2. `Dictionary<TKey,TValue>` (HashTable)  
   • Add：O(1) (平均) / O(n) (擴充)  
   • Exact Search：O(1)  

3. `SortedList<TKey,TValue>`  
   • Add：O(n)；若插在尾端且不擴充為 O(log n)  
   • Search (Binary Search 或索引子)：O(log n)  
   • 順序列舉：O(1)（因為始終保持排序）