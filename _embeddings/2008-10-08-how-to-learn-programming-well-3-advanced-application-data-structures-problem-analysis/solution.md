# 該如何學好「寫程式」#3 ‑ 進階應用：資料結構 + 問題分析

# 問題／解決方案 (Problem/Solution)

## Problem: 讓使用者輸入高速公路起訖交流道，產生「花費最低」的建議行車路線

**Problem**:  
在「中山高、北二高、國道二號」等多條高速公路組成的複雜路網中，使用者輸入「起點交流道」與「終點交流道」後，程式必須列出經過的所有交流道 / 收費站，並計算「油錢 + 過路費」最便宜的路線。  

**Root Cause**:  
1. 路網屬於「多對多」連線關係，若以傳統資料表或一維陣列儲存，將無法直接描述「點與點之間的多重連線」。  
2. 若以暴力列舉所有可能路徑，再逐一比較成本，當節點數量增加時，計算量呈指數成長，效能無法接受。  

**Solution**:  
1. 使用「Graph（圖）」資料結構：  
   • Node = 交流道 / 收費站（Name, TollFee, Links）  
   • Link = 兩節點間路段（FromNode, ToNode, Distance, RoadName）  
   ```csharp
   public class Node {
       public string Name;  public int TollFee;
       public List<Link> Links = new List<Link>();
       public Node(string name,int toll){ Name=name; TollFee=toll; }
   }
   public class Link {
       public double Distance; public Node FromNode, ToNode;
       public RoadNameEnum Road;
       public Link(Node from,Node to,double dist,RoadNameEnum rd){
           FromNode=from; ToNode=to; Distance=dist; Road=rd; }
   }
   ```
2. 在 Map 類別中載入所有 Node / Link，形成完整路網。  
3. 採用「深度優先搜尋 + Stack / Recursion」：  
   • 以 Stack 保存目前路徑 (= 麵包屑)  
   • 遇到走過的節點即回溯，避免無窮迴圈  
   • 計算目前累積成本 (油錢 = Distance*2 + TollFee)，找到最低者即為最佳解  
   ```csharp
   private void Search(string start,string end,double cost){
       _path.Push(start);
       if(start==end){ … 更新最佳解 …; _path.Pop(); return; }
       foreach(var way in _nodes[start].Links){
           string next = way.GetOtherNodeName(start);
           if(!_path.Contains(next))
               Search(next,end,cost + _nodes[next].TollFee + way.Distance*2);
       }
       _path.Pop();
   }
   ```
4. 為避免 Stack.Contains 的 O(n) 成本，可平行維護一個 HashSet 供 O(1) 查詢；或改用 Dijkstra、A* 等更高效率的最短／最便宜路徑演算法。

**Cases 1**:  
• 測試「機場端 → 基金」路線，程式輸出：  
  機場端 → 機場系統 → … → 基金，共 79.5km，總花費 192 元。  
• 透過圖資料結構與 DFS，能正確列舉所有合法路徑並挑出最低成本者，證實模型正確可行。

---

## Problem: 節點大量增加時，搜尋過程效能急遽下降

**Problem**:  
當高速公路節點、路段資料擴充到上千筆以上，原本的 DFS + Stack.Contains 版本開始出現嚴重延遲。

**Root Cause**:  
1. `Stack<string>.Contains()` 為 O(n) 線性搜尋；每深入一層都需掃描整條 Stack，造成立方級甚至更差的耗時。  
2. 若仍使用暴力 DFS，而未限制搜尋範圍或使用啟發式演算法，搜尋樹會呈爆炸性成長。

**Solution**:  
1. 以 HashSet 取代 Stack.Contains 判重：  
   ```csharp
   HashSet<string> _visited = new HashSet<string>();
   …
   if(_visited.Add(next)) {     // O(1)
       Search(next,end,cost+…);
       _visited.Remove(next);
   }
   ```
   增刪、判斷皆 O(1)，大幅降低檢查已訪節點的成本。  
2. 進一步可將整體演算法改為：  
   • Dijkstra：適用「非負權重」找最短（或最便宜）路徑，時間複雜度 O(E log V)。  
   • A*：加入啟發函式 (heuristic) 後，可視實際情況更快收斂。

**Cases 1**:  
• 於前一篇文章的範例中，僅將 `List` 換成 `SortedList`，搜尋操作由 O(n) → O(log n)，效能提升約 6,000 倍；同樣概念應用於本例，HashSet 亦帶來等級差距的效能改善。  

---

## Problem: 對資料結構／演算法缺乏概念，導致「只微調程式碼卻無法真正加速」

**Problem**:  
部分開發者習慣從「把程式碼寫對」直接跳到「把程式碼寫快」；卻只著眼於語法層面的小優化（少幾行、換語法糖），面對大型資料或高併發需求時仍無法通過效能門檻。

**Root Cause**:  
1. 缺乏「資料結構 + 演算法」的整體思維，無法在設計階段就將效率問題連根拔起。  
2. 錯把硬體升級、語法優化當成主要解法，忽視真正造成複雜度爆炸的底層結構選擇。

**Solution**:  
1. 先辨識問題類型，從「如何描述資料」著手（Graph、Tree、Hash…），再決定對應演算法。  
2. 將改進焦點放在能帶來倍數級成長的層面，例如：  
   • 線性搜尋 → 二分搜尋 / 雜湊搜尋  
   • 暴力枚舉 → 最短路徑演算法  
3. 保持程式碼可維護、可擴充，同時確保最關鍵的資料結構與演算法選型正確。

**Cases 1**:  
• List → SortedList 由 O(n) 改為 O(log n)，範例中搜尋效能提升 6,000 倍。  
• 使用 HashSet 後，判重由 O(n) → O(1)，在 1,000+ 節點的道路測試資料集上，總搜尋時間降至原先的數十分之一。  

---