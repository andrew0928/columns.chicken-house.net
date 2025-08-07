# NGenerics - DataStructure / Algorithm Library

# 問答集 (FAQ, frequently asked questions and answers)

## Q: System.Collections.Generic.SortedList 的 Key 可以重複嗎？
不可以。SortedList 的 Key 必須是唯一的，不能出現重複值。

## Q: 作者為什麼不自己實作資料結構，而是去找現成的 Library？
作者認為自己重寫不一定比較好，而且若自己寫的類別沒有完整支援 ICollection、IEnumerable 等介面，實際使用時反而不方便，所以決定尋找現成且完善的實作。

## Q: NGenerics 是什麼？它提供哪些功能？
NGenerics 是一套開放原始碼的 .NET 資料結構與演算法函式庫。它實作了多種常用資料結構（如 Heap、BinaryTree、CircularQueue、PriorityQueue、Graph 等）以及各類演算法（包含排序、圖形演算法等），並附上完整 Source Code 方便研究或擴充。

## Q: NGenerics 的 GraphAlgorithms 目前內建哪三種圖形演算法？各自用途為何？
1. Dijkstras Algorithm（代克思托演算法）：用於計算單一來源到其他節點的最短路徑。  
2. Kruskals Algorithm：用於產生圖形的 Minimal Spanning Tree（最小生成樹）。  
3. Prims Algorithm（普林演算法）：同樣用於求取 Minimal Spanning Tree。

## Q: 使用 NGenerics 的 DijkstrasAlgorithm 時有什麼限制？
目前的實作只會回傳結果（各節點的最短距離/權重），並未同時回傳實際走過的節點路徑；若需要取得完整路徑資訊，必須自行修改 Source Code，透過 delegate 或 IVisitor 介面在演算法運行時紀錄走訪過程。

## Q: 若要在高速公路模型中計算過路費，應如何處理？
因為 Graph 的模型中「點」(Vertex) 本身無權重，需將道路設為有方向的兩條 Edge（南下與北上），並把過路費直接加入 Edge 的 weight，才能把油錢與過路費一起計算進最短路徑成本。