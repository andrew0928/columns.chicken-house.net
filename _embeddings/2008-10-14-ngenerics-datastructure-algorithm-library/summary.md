# NGenerics - DataStructure / Algorithm Library

## 摘要提示
- SortedList 限制: 作者因忘記 SortedList 的 Key 必須唯一而萌生尋找替代資料結構的念頭。  
- NGenerics 來源: 在 CodePlex 上找到的 NGenerics 提供完整的泛型資料結構與演算法實作。  
- 資料結構齊全: Library 內建 Heap、BinaryTree、CircularQueue、PriorityQueue、Graph…等常見結構。  
- 內含圖論演算法: 提供 Dijkstra、Kruskal、Prim 等最短路徑／最小生成樹演算法實作。  
- 原始碼開放: 雖缺乏 MSDN 式複雜度說明，但附完整 Source Code 可自行研究。  
- 高速公路範例: 以 Graph + Dijkstra 重寫計算北二高通行費的程式，行數大幅縮減。  
- 介面友善: 支援 ICollection、IEnumerable 等 .NET 介面，易於整合現有程式。  
- 收費站建模: 透過有向邊並將過路費加到 Edge Weight 來模擬收費站成本。  
- 擴充空間: 若需回傳路徑細節，可利用 Library 原始碼加入 Visitor 或 Delegate。  
- 學習呼籲: 善用現成函式庫可省時又能深入理解資料結構與演算法。

## 全文重點
作者原想在教學文章中親手實作各種資料結構，但因一時疏忽忘記 SortedList<TKey,TValue> 的 Key 必須唯一，而被同事提醒後體認到自行「造輪子」容易埋入錯誤且缺乏完整介面支援。於是他轉向開源社群，並在 CodePlex 發現 NGenerics—一套涵蓋堆積、樹、佇列、圖形與多種排序、圖論演算法的 .NET 泛型函式庫。NGenerics 以 MIT 授權開放，不僅可商用，也能作為學習範例。雖然官方文件沒有像 MSDN 那樣標示時間複雜度，但附帶的 Source Code 足以讓開發者自行追蹤實作細節。

為展示 Library 的威力，作者把原本需上百行程式碼的「北二高通行費計算」範例，以 NGenerics 的 Graph 與 Dijkstra 演算法重寫：先用 Graph<string> 逐一新增節點、邊及距離，再呼叫 GraphAlgorithms.DijkstrasAlgorithm 取得從「機場端」到「基金」的最短費用，程式只剩寥寥數行。若要考慮收費站，則可把道路改為有向邊，並在邊的 Weight 加入過路費即可。雖然現成 API 只回傳結果而非路徑，但利用開放原始碼可輕鬆加上 Visitor 或 Delegate 來取得中繼資訊。作者最後鼓勵讀者多利用像 NGenerics 這類成熟函式庫，既能省時，又能透過閱讀原始碼深化對資料結構與演算法的理解。

## 段落重點
### 從 SortedList 失誤到尋找替代方案
作者在撰寫資料結構教學時，因忘記 SortedList 的 Key 必須唯一而踩雷，體認到自行實作不僅易出錯，若沒有完整實作 ICollection、IEnumerable 等介面也難以實務使用。為兼顧正確性與維護成本，他決定放棄手刻，轉向尋找成熟的開源函式庫。

### 發現 NGenerics：完整的資料結構／演算法集合
在 CodePlex 搜尋後，作者找到 NGenerics。此庫支援 .NET 的泛型語法，涵蓋 Heap、BinaryTree、CircularQueue、PriorityQueue、Graph 等結構，以及 Dijkstra、Kruskal、Prim 等圖論演算法，宛如一本可執行的資料結構課本。MIT 授權讓商用或修改都無障礙，對學習者亦是寶貴範例來源。

### 文件不足與原始碼補位
NGenerics 官方文件雖不若 MSDN 詳盡，缺乏明確的時間複雜度標示，但幸好提供完整 Source Code。開發者既可直接使用，也能透過閱讀、修改程式碼深入理解演算法細節與效能。對願意「拼程式」的人來說，這不僅不是缺點，反而是更直接的學習管道。

### Graph + Dijkstra：高速公路費用計算實作
作者將「北二高通行費」範例改寫為 Graph<string>。先逐點新增「基金」「七堵收費站」「汐止系統」等節點，再以 AddEdge 指定距離（以油錢計算）。接著僅用 GraphAlgorithms.DijkstrasAlgorithm(highway, 起點) 即可計算「機場端」到「基金」的最低油錢。原本上百行的程式簡化為數行，效益立竿見影。

### 收費站建模與延伸應用
在 Graph 模型中 Vertex 無 Weight，為計入收費站得把道路改為有向邊並將過路費加到 Edge Weight。Dijkstra 的現成實作雖僅回傳費用結果，無法直接列出行車路徑，但因 NGenerics 開源，可自行加入 Visitor 或 Delegate 於走訪過程中記錄前驅節點，即可拿到所需的路徑資訊，顯示 Library 的可塑性與擴充空間。

### 結語：善用函式庫，提高效率與深度
藉由 NGenerics，作者不只解決了程式重寫與維護的負擔，也示範了如何透過現成函式庫快速完成複雜演算法應用。對開發者而言，選擇「用輪子」而非「造輪子」可把時間投資在真正的商業或創意需求上；而開放原始碼則提供另一條深入學習、精進內功的道路。