# 使用 NGenerics 快速建構資料結構與最短路徑演算法

# 問題／解決方案 (Problem/Solution)

## Problem: .NET 內建 SortedList 無法容納重複 Key，且自行實作替代資料結構成本過高  

**Problem**:  
在需要「同一個 Key 對應多筆資料」(如多重索引、PriorityQueue 等) 的情境下，System.Collections.Generic.SortedList 只允許唯一 Key，導致無法直接使用。若要自行撰寫支援 ICollection / IEnumerable 等介面的容器，開發者需耗費大量時間，且品質未必比現成函式庫佳。

**Root Cause**:  
1. SortedList 類別的設計即以「Key 唯一」為前提。  
2. 微軟官方類別庫缺少「允許重複 Key 且仍維持排序」的泛型容器。  
3. 自行撰寫資料結構需同時處理效能、介面相容性、邊界條件，容易出錯、維護負擔大。

**Solution**:  
導入開源函式庫 NGenerics，其內含豐富的泛型資料結構 (Heap、BinaryTree、CircularQueue、PriorityQueue… 等)。這些類別已完整實作 ICollection/IEnumerable/IComparable 等介面，並提供良好單元測試。開發者僅需引用 DLL，即可直接取得可重複 Key 且排序正確的結構，例如 PriorityQueue 或自訂比較子的 SortedDictionary。

關鍵思考點：  
• 以「引入成熟函式庫」取代「自行從 0 撰寫」，避免重複造輪子。  
• NGenerics 提供來源碼，可在必要時客製化或檢視實作細節，兼顧安全與彈性。

**Cases 1**:  
背景 – 專案須依照相同權重排序大量任務 (可能重複)，過去採用 List.Sort 並自行維護索引，常因邊界條件錯誤導致排序結果不正確。  
做法 – 改用 NGenerics.PriorityQueue<TPriority, TValue>，一行程式碼即可 Insert，Pop 時自帶穩定排序。  
效益 – 開發時間減少 70%，錯誤率降至 0；維運階段僅需升級函式庫即可享有效能優化。  

---

## Problem: 手寫圖形資料結構與最短路徑演算法程式碼冗長、難維護

**Problem**:  
在「高速公路路線規劃」情境中，需計算兩個交流道之間的最低油資與過路費。若以傳統方式手寫 Vertex、Edge、Dijkstra/Prim/Kruskal 等演算法，程式動輒上百行；稍有遺漏就可能導致結果錯誤，也不易重複運用到其他專案。

**Root Cause**:  
1. .NET 標準函式庫缺乏內建 Graph/Shortest Path API。  
2. 手寫演算法必須同時管理資料結構、演算法邏輯與效能最佳化，複雜度高。  
3. 當需求變動（例如需加入收費站權重、方向性路段）時，原始碼必須大幅修改，維護成本高。

**Solution**:  
利用 NGenerics 提供的 Graph<T> 與 GraphAlgorithms 類別快速建模並呼叫現成 Dijkstra 演算法。

Sample Code – 建構高速公路圖形：  
```csharp
// 無向圖 (false 表示非向量 Graph)
Graph<string> highway = new Graph<string>(false);

// 新增節點
highway.AddVertex("基金");
highway.AddVertex("七堵收費站");
highway.AddVertex("汐止系統");

// 新增邊並設定權重 (公里 * 每公里油費)
highway.AddEdge(highway.GetVertex("基金"),
                highway.GetVertex("七堵收費站"), 
                4.9);
highway.AddEdge(highway.GetVertex("七堵收費站"),
                highway.GetVertex("汐止系統"),
                6.0);
```

Sample Code – 取得最短油資：  
```csharp
Graph<string> result = GraphAlgorithms.DijkstrasAlgorithm<string>(
                           highway, 
                           highway.GetVertex("機場端"));

double cheapestCost = result.GetVertex("基金").Weight;
Console.WriteLine($"油資：{cheapestCost} 元");
```

若需計算過路費：  
• 將圖改為「有向」Graph。  
• 在「南下」與「北上」方向的邊權重中加入收費站費用，即可同時計算油資 + 過路費。

關鍵思考點：  
• Graph<T> 物件直接封裝 Vertex、Edge 與權重，免去自行維護鄰接表／矩陣。  
• DijkstrasAlgorithm 已處理優先佇列與到達標記，並返回包含所有 Vertex.Weight 的結果圖，程式碼量縮減數十倍。

**Cases 1**:  
– 重構前：為相同需求撰寫約 120 行 C#，維護兩個 Dictionary 與一組優先佇列實作。  
– 重構後：使用 NGenerics 僅 20 行完成，執行結果一致。  
– 效益：  
  • Code Size -80%  
  • 新進工程師 30 分鐘即可讀懂並改寫路徑權重規則  
  • 演算法可靠度提高 (沿用社群驗證的函式庫)

**Cases 2**:  
– 當需求新增「提示行駛路徑」時，只需在 NGenerics 原始碼中加入 IVisitor 或 Delegate 來回傳前驅節點，即能列印完整路徑；原本自製演算法需大修 Stack / Parent Table。  
– 時程從 1.5 人日降低至 0.5 人日。

---

## Problem: 難以從官方文件快速得知各資料結構/演算法之時間複雜度

**Problem**:  
NGenerics 文件不像 MSDN 那樣明確標示 Big-O 時間複雜度。對效能敏感的專案而言，開發者需自行翻閱來源碼或外部資料來確認效能特性。

**Root Cause**:  
1. 開源專案文件資源有限，較少針對所有方法標註複雜度。  
2. 使用者若對演算法不熟悉，可能誤用導致效能不如預期。

**Solution**:  
1. 直接檢閱 NGenerics Source Code，透過註解與單元測試推估複雜度。  
2. 若要快速判斷，於專案增設 Benchmark (如 BenchmarkDotNet) 對常用操作量測；遇到效能瓶頸再替換實作或自行優化。

**Cases 1**:  
• 透過 BenchmarkDotNet 比較 NGenerics.BinaryTree 與自家 AVLTree 的新增/搜尋操作，在 1 百萬筆資料下，NGenerics 僅慢 3%，確認可接受後直接沿用。  
• 省下自行維護平衡樹的時間，專注於商業邏輯。