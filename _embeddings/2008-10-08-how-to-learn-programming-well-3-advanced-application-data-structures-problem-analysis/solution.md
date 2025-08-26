以下為基於原文梳理出的 15 個結構化解決方案案例。每個案例對應文章中出現的實際難題、根因、解法與效益描述，並補齊可操作的實作細節與練習評估。

## Case #1: 高速公路網路的圖模型建構（Node/Link）

### Problem Statement（問題陳述）
- 業務場景：需要在台灣高速公路網（中山高、北二高、國道二號）中，依使用者指定起點與終點，輸出建議路線與沿途交流道、收費站，並具備擴充性與可維護性。
- 技術挑戰：如何在程式內正確表示道路網路的連結關係，支援路段屬性（距離、所屬道路）與節點屬性（名稱、過路費）。
- 影響範圍：資料結構若設計不當，將無法正確搜尋路線或進行效能優化，導致功能不可用或效能低落。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺乏合適的資料結構描述道路的連通性與屬性。
  2. 未能區分「節點（交流道/收費站）」與「連線（路段）」。
  3. 未建立由節點出發的鄰接關係，造成搜尋算法無從施展。
- 深層原因：
  - 架構層面：缺乏以圖（Graph）為核心的領域模型。
  - 技術層面：對圖的鄰接表（Adjacency List）/鄰接矩陣（Adjacency Matrix）特性不熟。
  - 流程層面：需求分析未落實到資料模型，導致設計階段卡關。

### Solution Design（解決方案設計）
- 解決策略：以圖（Graph）資料結構建模道路網：節點 Node（Name, TollFee, Links）+ 連線 Link（From, To, Distance, Road），採用鄰接表以兼顧記憶體與遍歷效率，為後續路徑搜尋提供基礎。

- 實施步驟：
  1. 建模節點與連線
     - 實作細節：Node 含 Name/TollFee/Links；Link 含 From/To/Distance/Road。
     - 所需資源：C#/.NET
     - 預估時間：0.5 天
  2. 決定鄰接結構與圖的有向/無向
     - 實作細節：將 Link 加入兩端 Node.Links，視為無向道路。
     - 所需資源：設計文件
     - 預估時間：0.5 天
  3. 擴充路段屬性
     - 實作細節：加入 RoadNameEnum 以利輸出說明或路線限制。
     - 所需資源：C# Enum
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public class Node
{
    public string Name;
    public int TollFee;
    public List<Link> Links = new List<Link>();
    public Node(string name, int tollFee) { Name = name; TollFee = tollFee; }
}

public class Link
{
    public double Distance;
    public Node FromNode;
    public Node ToNode;
    public RoadNameEnum Road;
    public Link(Node from, Node to, double distance, RoadNameEnum road)
    { FromNode = from; ToNode = to; Distance = distance; Road = road; }

    public enum RoadNameEnum { Highway1, Highway2, Highway3 }
}
```

- 實際案例：原文以 Node/Link 建模交流道與路段，為路徑搜尋鋪墊。
- 實作環境：.NET 3.5/C#；集合類型使用 List<T>
- 實測數據：
  - 改善前：無法正確枚舉路徑（缺跨節點關聯）
  - 改善後：可由節點出發遍歷鄰接連線
  - 改善幅度：功能性由不可用到可用（質變）

- Learning Points（學習要點）
  - 核心知識點：
    - Graph 資料結構的節點與連線建模
    - 鄰接表適用於稀疏圖
    - 類別設計與領域模型映射
  - 技能要求：
    - 必備技能：C# 類別/集合、基本圖論
    - 進階技能：面向對象建模、可擴充結構設計
  - 延伸思考：
    - 應用於路網、電網、社群圖譜等
    - 風險：資料不一致（孤立節點/懸空連線）
    - 優化：加入驗證、建立圖建構器與資料匯入

- Practice Exercise（練習題）
  - 基礎練習：新增 5 個交流道與 8 條路段（30 分鐘）
  - 進階練習：為 Link 加入限速、車道資訊（2 小時）
  - 專案練習：匯入一段真實高速路網資料並可視化（8 小時）

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：節點/連線正確；可遍歷
  - 程式碼品質（30%）：命名合理、結構清晰
  - 效能優化（20%）：選對鄰接表；避免重複連線
  - 創新性（10%）：擴充屬性與驗證機制


## Case #2: 以 Dictionary 進行節點快取與 O(1) 查找

### Problem Statement（問題陳述）
- 業務場景：建圖與路徑計算時需頻繁依名稱取得 Node，若以 List 線性搜尋，負載成長時延遲暴增。
- 技術挑戰：確保節點查找具可預測的低延遲，支援動態建圖與查詢。
- 影響範圍：建圖與搜尋皆受累，整體反應時間不穩定。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 使用 List 檢索名稱為 O(n)。
  2. 節點數量增長導致建圖/查找成瓶頸。
  3. 缺少名稱到節點的索引。
- 深層原因：
  - 架構層面：未建立鍵值存取策略
  - 技術層面：忽略 Dictionary 的哈希特性
  - 流程層面：未在早期確立查詢模式

### Solution Design（解決方案設計）
- 解決策略：以 Dictionary<string, Node> 保存節點，AddNode/FindNode 時使用 O(1) 查找，AddLink 內部直接索引端點。

- 實施步驟：
  1. 引入字典索引
     - 實作細節：_nodes[name] 直取
     - 所需資源：C# Dictionary
     - 預估時間：0.5 天
  2. 封裝建圖 API
     - 實作細節：AddNode/AddLink 統一使用字典
     - 所需資源：單元測試
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public class Map
{
    private Dictionary<string, Node> _nodes = new Dictionary<string, Node>();
    private void AddNode(string name, int tollFee) => _nodes.Add(name, new Node(name, tollFee));
    private void AddLink(string n1, string n2, double distance, Link.RoadNameEnum road)
    {
        var node1 = _nodes[n1]; var node2 = _nodes[n2];
        var link = new Link(node1, node2, distance, road);
        node1.Links.Add(link); node2.Links.Add(link);
    }
}
```

- 實際案例：原文 Map 類別即採用 Dictionary 存取節點。
- 實作環境：.NET 3.5/C#
- 實測數據：
  - 改善前：List 線性查找 O(n)
  - 改善後：Dictionary 哈希查找平均 O(1)
  - 改善幅度：理論上顯著（n 越大效益越高）

- Learning Points（學習要點）
  - 核心知識點：鍵值索引、哈希查找、字典使用
  - 技能要求：
    - 必備：C# 集合使用
    - 進階：碰撞處理理解、哈希品質
  - 延伸思考：大規模場景可引入快取過期策略；風險為鍵重複；可優化為 TryGetValue

- Practice Exercise
  - 基礎：將 List 改寫為 Dictionary（30 分鐘）
  - 進階：TryGetValue 與錯誤處理（2 小時）
  - 專案：導入快取命中率統計（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：正確查找
  - 程式碼品質（30%）：介面清晰、例外處理
  - 效能優化（20%）：O(1) 查找落地
  - 創新性（10%）：快取策略設計


## Case #3: 以遞迴 DFS + Stack 走迷宮找出所有路徑

### Problem Statement（問題陳述）
- 業務場景：在圖模型上找出起點至終點的所有可達路線，再依成本挑選最省方案，支援教學與小規模實作。
- 技術挑戰：需遍歷所有路徑且避免環路；同時累積成本與記錄當前路徑。
- 影響範圍：若無系統化遍歷，將漏解或陷入無窮迴圈。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 圖非樹，可能回到已訪節點。
  2. 缺少「麵包屑」機制記錄路徑。
  3. 成本累積與最佳解更新未整合。
- 深層原因：
  - 架構層面：搜尋與狀態管理耦合
  - 技術層面：對遞迴/堆疊的掌握不足
  - 流程層面：未定義搜尋終止條件與剪枝策略

### Solution Design（解決方案設計）
- 解決策略：以遞迴 DFS，使用 Stack 記錄路徑，訪問時累積成本，到達終點比較並更新最佳解；避免 revisiting。

- 實施步驟：
  1. 設計搜尋入口
     - 實作細節：FindBestPath 包裝初始化/返回
     - 所需資源：單元測試
     - 預估時間：0.5 天
  2. 實作遞迴函式
     - 實作細節：Push/Pop、累積成本、到終點時更新
     - 所需資源：C#
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
private double _cost = 0;
private string[] _best_path = null;
private Stack<string> _path = null;

private void Search(string startName, string endName, double current_cost)
{
    _path.Push(startName);
    if (startName == endName)
    {
        if (_cost == 0 || current_cost < _cost)
        { _cost = current_cost; _best_path = _path.ToArray(); } // 注意順序反轉問題見 Case #9
        _path.Pop(); return;
    }
    foreach (var way in _nodes[startName].Links)
    {
        string next = way.FromNode.Name == startName ? way.ToNode.Name : way.FromNode.Name;
        if (_path.Contains(next) == false) // 見 Case #5 改為 HashSet
        {
            Search(next, endName, current_cost + _nodes[next].TollFee + way.Distance * 3);
        }
    }
    _path.Pop();
}

public string[] FindBestPath(string startName, string endName, out double cost)
{
    try { _cost = 0; _path = new Stack<string>(); Search(startName, endName, 0); cost = _cost; return _best_path; }
    finally { _cost = 0; _path = null; }
}
```

- 實際案例：原文以遞迴 DFS 實作，成功得出「機場端→基金」最佳成本路線。
- 實作環境：.NET 3.5/C#
- 實測數據：
  - 改善前：無系統化搜尋，可能漏解
  - 改善後：可列舉所有路徑並選最省
  - 改善幅度：正確性由隨機/不完整 → 完整

- Learning Points
  - DFS 與遞迴/堆疊等價性
  - 圖遍歷的狀態管理
  - 終止條件與最優更新
- 技能要求
  - 必備：遞迴、集合遍歷
  - 進階：狀態封裝與剪枝策略
- 延伸思考
  - 可應用於迷宮解、拓撲搜尋
  - 風險：指數時間複雜度
  - 優化：剪枝與改用 Dijkstra（見 Case #7）

- Practice
  - 基礎：實作 DFS 並列印所有路徑（30 分）
  - 進階：加入剪枝（2 小時）
  - 專案：比較 DFS vs Dijkstra 表現（8 小時）

- Assessment
  - 功能完整性：能找出最省路徑
  - 程式碼品質：遞迴清晰、邏輯正確
  - 效能優化：能加入剪枝
  - 創新性：路徑統計/可視化


## Case #4: 迴圈檢查改用 HashSet，將 Contains 從 O(n) 降到 O(1)

### Problem Statement（問題陳述）
- 業務場景：DFS 搜尋時需頻繁判斷節點是否已訪問，選用 Stack.Contains 帶來線性時間成本。
- 技術挑戰：訪問檢查是熱路徑，O(n) 造成整體效能劣化。
- 影響範圍：路徑越長、分支越多，整體搜尋時間急遽上升。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Stack.Contains 為 O(n) 線性搜尋。
  2. 訪問檢查頻繁，疊加成本大。
  3. 未以集合語意（唯一性）建模。
- 深層原因：
  - 架構層面：未區分「路徑順序」與「已訪集合」
  - 技術層面：未利用 HashSet 的 O(1) Contains
  - 流程層面：缺乏複雜度檢視習慣

### Solution Design
- 解決策略：保留 Stack 作為路徑（順序），另增 HashSet<string> visited 作為已訪集合，Contains 改為 O(1)。

- 實施步驟：
  1. 新增 visited 集合
     - 實作細節：進入/離開節點時同步 Add/Remove
     - 所需資源：HashSet<T>
     - 預估時間：0.5 天
  2. 代碼替換/測試
     - 實作細節：將 _path.Contains 改為 visited.Contains
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
private HashSet<string> _visited;
private void Search(string startName, string endName, double current_cost)
{
    _path.Push(startName);
    _visited.Add(startName);

    if (startName == endName) { /* 更新最佳解 */ _visited.Remove(startName); _path.Pop(); return; }

    foreach (var way in _nodes[startName].Links)
    {
        var next = way.FromNode.Name == startName ? way.ToNode.Name : way.FromNode.Name;
        if (!_visited.Contains(next))
        {
            Search(next, endName, current_cost + _nodes[next].TollFee + way.Distance * 3);
        }
    }
    _visited.Remove(startName);
    _path.Pop();
}
```

- 實際案例：原文指出 Stack.Contains 為 O(n)，建議 HashSet 替代；HashSet.Contains 為 O(1)。
- 實作環境：.NET 3.5 HashSet<T>
- 實測數據：
  - 改善前：Contains O(n)
  - 改善後：Contains O(1)
  - 改善幅度：平均可觀（視路徑長度 n）

- Learning Points
  - 用對集合類型＝正確複雜度
  - 路徑（有序）與已訪（集合）的分離
  - 熱路徑優化策略
- 技能要求
  - 必備：集合與複雜度
  - 進階：記憶體/速度權衡
- 延伸思考
  - 可應用於去重、交集運算
  - 風險：空間增加
  - 優化：初始容量預估，降低 rehash

- Practice
  - 基礎：替換 Contains 實作（30 分）
  - 進階：加入容量預估與測試（2 小時）
  - 專案：壓測比較 O(n) vs O(1)（8 小時）

- Assessment
  - 功能：正確避環
  - 品質：簡潔、低耦合
  - 效能：熱路徑降耗
  - 創新：容量/探測策略


## Case #5: 將暴力列舉改為 Dijkstra 擴散式最短路徑

### Problem Statement（問題陳述）
- 業務場景：需在大圖上高效率找「總成本最低」路徑（油錢+過路費），暴力 DFS 列舉全部路徑的時間不可接受。
- 技術挑戰：必須在不漏解下大幅降低探索數量。
- 影響範圍：資料規模放大即無法完成功能。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. DFS 列舉所有簡單路徑，成長指數級。
  2. 未保存節點當前最小成本，重複探索。
  3. 無優先順序擴展，缺乏「最短優先」策略。
- 深層原因：
  - 架構層面：演算法選型未對齊目標函數
  - 技術層面：未使用 Dijkstra/優先佇列
  - 流程層面：未量化複雜度差異

### Solution Design
- 解決策略：採用 Dijkstra 自起點擴散，維護每節點當前最小成本 dist[] 與前驅 prev[]，以優先佇列按成本最小擴展，終點出佇列即得最短路。

- 實施步驟：
  1. 抽象成本函式
     - 實作細節：Cost(link,nextNode) 對齊 Case #6
     - 預估時間：0.5 天
  2. 實作 Dijkstra
     - 實作細節：優先佇列、小於等於重鬆弛
     - 預估時間：1-2 天
  3. 回溯路徑
     - 實作細節：由 prev[] 重建
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 假設有優先佇列 MinHeap<(node, cost)>
public List<string> Dijkstra(string start, string end, Func<Link,Node,double> edgeCost, out double total)
{
    var dist = new Dictionary<string,double>(); var prev = new Dictionary<string,string>();
    var pq = new SortedSet<(double cost, string node)>();
    foreach(var name in _nodes.Keys){ dist[name]=double.PositiveInfinity; }
    dist[start]=0; pq.Add((0,start));

    while(pq.Count>0)
    {
        var (cost,u)=pq.Min; pq.Remove(pq.Min);
        if (u==end) break;
        foreach(var e in _nodes[u].Links)
        {
            var v = e.FromNode.Name==u? e.ToNode.Name : e.FromNode.Name;
            double nc = cost + edgeCost(e, _nodes[v]);
            if (nc < dist[v])
            {
                if (dist[v]!=double.PositiveInfinity) pq.Remove((dist[v], v));
                dist[v]=nc; prev[v]=u; pq.Add((dist[v],v));
            }
        }
    }
    total = dist[end];
    // 回溯
    var path = new List<string>(); for(var cur=end; cur!=null && prev.ContainsKey(cur); cur=prev.ContainsKey(cur)? prev[cur]: null) path.Add(cur);
    path.Add(start); path.Reverse(); return path;
}
```

- 實際案例：原文描述「由起點往外擴散、同點保留較便宜路徑」即 Dijkstra 思路。
- 實作環境：.NET（SortedSet 或自定最小堆）
- 實測數據：
  - 改善前：指數級（DFS）
  - 改善後：O(E log V)
  - 改善幅度：數量級提升

- Learning Points
  - 最短路演算法與適用性
  - 優先佇列在圖演算法中的角色
  - 成本函式抽象
- 技能要求
  - 必備：Dijkstra 原理
  - 進階：最小堆/SortedSet
- 延伸思考
  - 可應用於導航、網路路由
  - 風險：負權成本不適用
  - 優化：雙向 Dijkstra、A*

- Practice
  - 基礎：實作不帶 PQ 的 Dijkstra（30 分）
  - 進階：加入 PQ 並壓測（2 小時）
  - 專案：比較 DFS/Dijkstra/A*（8 小時）

- Assessment
  - 功能：正確最短路
  - 品質：結構清晰、模組化
  - 效能：E log V 達成
  - 創新：啟發式/雙向搜尋


## Case #6: 成本函式設計與常數錯置修正（2 元/km vs 3）

### Problem Statement（問題陳述）
- 業務場景：最佳路徑以「油錢 + 過路費」為目標。文中假設每公里 2 元，但程式碼以 3 計算，導致成本偏差。
- 技術挑戰：成本模型需可調且一致，避免硬編常數出錯。
- 影響範圍：輸出結果不可信，決策錯誤。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 常數硬編碼，與需求敘述不一致。
  2. 成本模型未抽象，難以校正。
  3. 無集中管理/設定檔。
- 深層原因：
  - 架構層面：缺乏配置與依賴注入
  - 技術層面：未引入成本委派函式
  - 流程層面：缺少驗證與單元測試覆核

### Solution Design
- 解決策略：引入可參數化成本函式，油價/油耗/費率不硬編，統一由設定或注入；修正每公里成本為 2。

- 實施步驟：
  1. 定義成本計算策略
     - 實作細節：Func<Link,Node,double> 可注入
     - 預估時間：0.5 天
  2. 封裝常數與設定
     - 實作細節：AppSettings 或常數集中於 Config
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public class CostConfig { public double FuelPricePerL = 30; public double KmPerL = 15; public double PerKm => FuelPricePerL / KmPerL; }

Func<Link,Node,double> MakeCost(CostConfig cfg) =>
    (link,nextNode) => nextNode.TollFee + link.Distance * cfg.PerKm;

// 使用：Dijkstra(start,end, MakeCost(cfg), out total);
```

- 實際案例：文述「每公里 2 元」與程式碼「*3」不一致；以策略與設定修正。
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：每公里成本 3 → 偏高 50%
  - 改善後：每公里成本 2 → 與敘述一致
  - 改善幅度：誤差從 50% → 0%

- Learning Points
  - 策略模式/函式注入
  - 設定集中化
  - 可測試性提升
- 技能要求
  - 必備：委派/函式型 API
  - 進階：DI 與設定管理
- 延伸思考
  - 可引入時段浮動費率
  - 風險：設定變更影響廣泛
  - 優化：版本化與校驗

- Practice
  - 基礎：將常數改為配置（30 分）
  - 進階：寫 3 個成本策略（2 小時）
  - 專案：加入 A/B 測試不同費率（8 小時）

- Assessment
  - 功能：一致計價
  - 品質：策略清晰
  - 效能：無額外負擔
  - 創新：多策略切換


## Case #7: 圖上循環偵測與已訪語意（避免兜圈）

### Problem Statement（問題陳述）
- 業務場景：路網是圖，存在環路。若未避免重訪，可能無窮迴圈或重複成本。
- 技術挑戰：如何定義「已訪」語意與時機（入/離開），確保正確性。
- 影響範圍：可能卡死、結果錯誤或過度膨脹計算。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 圖非樹，有回邊。
  2. 已訪集合與回溯時機未定義。
  3. 多次路過同站可能重複計費。
- 深層原因：
  - 架構層面：狀態管理散落
  - 技術層面：缺乏入站/離站點對點協議
  - 流程層面：未建立測試涵蓋環路情境

### Solution Design
- 解決策略：採用「進站即標記、離站即清除」策略；成本在「到達 next 時計一次」；已訪語意為「本條當前路徑已訪」。

- 實施步驟：
  1. 設計訪問協議
     - 實作細節：visited.Add 前 push；回溯時 Remove 後 pop
     - 預估時間：0.5 天
  2. 設計計費時機
     - 實作細節：到達 next 計 TollFee（每路徑節點一次）
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 見 Case #4 程式片段，進出對稱 Add/Remove。
// 計費在探索 next 時加上 next.TollFee，避免重入情況下重複。
```

- 實際案例：原文在 DFS 中以 Contains 避免重訪（後改 HashSet）；成本在遞迴前加 next 費用。
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：可能重入循環、重複計費
  - 改善後：每路徑節點僅計一次費用，且能終止
  - 改善幅度：正確性顯著提升

- Learning Points
  - 已訪語意與回溯對稱性
  - 成本計算時機的確定性
  - 測試覆蓋循環情境
- 技能要求
  - 必備：DFS 狀態管理
  - 進階：測試設計（含環路）
- 延伸思考
  - 可應用於去重、圖匹配
  - 風險：全域狀態污染
  - 優化：狀態封裝到物件

- Practice
  - 基礎：加入環路單元測試（30 分）
  - 進階：設計多環測例（2 小時）
  - 專案：報表中標註曾接觸環路（8 小時）

- Assessment
  - 功能：無循環卡死
  - 品質：狀態一致
  - 效能：不重複探索
  - 創新：診斷資訊


## Case #8: 路線輸出報表（含道路名稱與路段資訊）

### Problem Statement（問題陳述）
- 業務場景：使用者不只要「路徑」，還要沿途交流道與所屬高速公路，便於人工檢視與導航。
- 技術挑戰：需由節點序列還原路段細節（道路名、距離）。
- 影響範圍：缺少可讀輸出降低工具價值。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 路徑結果僅為節點名稱陣列。
  2. 未將節點對映回 Link。
  3. 無輸出格式化模組。
- 深層原因：
  - 架構層面：缺展示層組件
  - 技術層面：FindLink 為 O(deg(v)) 線性掃描
  - 流程層面：未定義輸出需求

### Solution Design
- 解決策略：利用 Map.FindLink(name1,name2) 找到段落，輸出 Road/Distance/TollFee；提供簡單報表格式。

- 實施步驟：
  1. 路段分解
     - 實作細節：相鄰節點 pair → Link
     - 預估時間：0.5 天
  2. 格式化輸出
     - 實作細節：含道路名、距離、費用
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
public void PrintRoute(string[] path)
{
    for (int i=0; i<path.Length-1; i++)
    {
        var link = FindLink(path[i], path[i+1]);
        Console.WriteLine($"{path[i]} -> {path[i+1]} via {link.Road}, {link.Distance} km, Toll next: {_nodes[path[i+1]].TollFee}");
    }
}
```

- 實際案例：原文提供 FindLink 與道路枚舉。
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：節點序列不可讀
  - 改善後：含道路/距離/費用的可讀報表
  - 改善幅度：可用性提升

- Learning Points
  - 資料回溯與呈現
  - 封裝輸出邏輯
  - 可讀性與驗證
- 技能要求
  - 必備：I/O 與字串格式化
  - 進階：本地化/單位轉換
- 延伸思考
  - 可輸出為 CSV/JSON
  - 風險：FindLink 為 O(deg(v))；可引入快取
  - 優化：鄰接字典加速查找

- Practice
  - 基礎：印出每段路資訊（30 分）
  - 進階：匯出 CSV（2 小時）
  - 專案：產生地圖可視化（8 小時）

- Assessment
  - 功能：完整輸出
  - 品質：格式一致
  - 效能：無多餘查找
  - 創新：視覺化呈現


## Case #9: 修正 Stack.ToArray 導致的路徑順序反轉

### Problem Statement（問題陳述）
- 業務場景：為了保存目前路徑，程式於到達終點時以 Stack.ToArray 輸出，但該方法回傳順序為「頂→底」，導致路徑呈現反轉。
- 技術挑戰：需要以「起點→終點」的自然順序輸出。
- 影響範圍：輸出可讀性差，易誤判。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Stack.ToArray 回傳順序為 LIFO
  2. 未進行反轉處理
  3. 缺少對輸出順序的測試
- 深層原因：
  - 架構層面：資料與呈現耦合
  - 技術層面：不熟悉集合 API 行為
  - 流程層面：驗收案例未包含順序檢查

### Solution Design
- 解決策略：於輸出前反轉陣列或改採 List 動態維護；或使用 prev[] 回溯後再反轉（Dijkstra）。

- 實施步驟：
  1. 補充反轉邏輯
     - 實作細節：Array.Reverse 或 Enumerable.Reverse
     - 預估時間：0.2 天
  2. 加入測試
     - 實作細節：起點=第一項，終點=最後一項
     - 預估時間：0.3 天

- 關鍵程式碼/設定：
```csharp
var arr = _path.ToArray();
Array.Reverse(arr); // 修正為起點 -> 終點
_best_path = arr;
```

- 實際案例：原文以 _path.ToArray() 保存路徑，需注意方向。
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：輸出順序顛倒
  - 改善後：起點→終點
  - 改善幅度：可讀性完全修復

- Learning Points
  - 集合 API 行為理解
  - 輸出與內部結構不必一致
  - 善用測試保護
- 技能要求
  - 必備：陣列操作
  - 進階：迭代器與延遲序列
- 延伸思考
  - 以 List 維護即時順序
  - 風險：重複反轉造成性能損耗（可忽略）
  - 優化：僅於最終輸出反轉一次

- Practice
  - 基礎：新增順序測試（30 分）
  - 進階：封裝 Path 對象（2 小時）
  - 專案：加入格式化與驗證（8 小時）

- Assessment
  - 功能：順序正確
  - 品質：測試完備
  - 效能：最小化處理
  - 創新：API 包裝


## Case #10: 用對集合，效能差 6000 倍：List 改 SortedList/Dictionary

### Problem Statement（問題陳述）
- 業務場景：大量搜尋與查找操作時，若使用 List 線性掃描，效能極差；原文提及曾有 6000 倍差異案例。
- 技術挑戰：選擇正確集合以對齊存取模式。
- 影響範圍：搜尋密集流程的吞吐與延遲。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. List 搜尋為 O(n)
  2. 缺少排序或索引
  3. 未評估資料規模
- 深層原因：
  - 架構層面：資料存取模式未建模
  - 技術層面：忽略 SortedList/Dictionary 特性
  - 流程層面：缺基準測試

### Solution Design
- 解決策略：頻繁 Key 查找使用 Dictionary；需要有序且以 Key 搜索使用 SortedList；建立基準測試驗證。

- 實施步驟：
  1. 建立測試數據
     - 實作細節：隨機鍵 100 萬
     - 預估時間：0.5 天
  2. 替換集合
     - 實作細節：List.Find → Dict/SortedList 索引/二分
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// Dictionary: O(1) 平均
var dict = new Dictionary<int,string>();
// SortedList: O(log n) 尋找，保持鍵排序
var sorted = new SortedList<int,string>();
```

- 實際案例：原文強調 List → SortedList 搜尋差 6000 倍。
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：List O(n)
  - 改善後：SortedList O(log n)/Dictionary O(1)
  - 改善幅度：高達數千倍

- Learning Points
  - 適材適所用集合
  - 時間複雜度直覺
  - 基準測試習慣
- 技能要求
  - 必備：集合 API
  - 進階：性能剖析
- 延伸思考
  - 應用：高頻查詢模組
  - 風險：哈希攻擊/碰撞
  - 優化：合適的比較器/哈希器

- Practice
  - 基礎：替換到 Dictionary（30 分）
  - 進階：寫 micro-bench（2 小時）
  - 專案：集合選型守則文檔（8 小時）

- Assessment
  - 功能：查找正確
  - 品質：可維護
  - 效能：量化提升
  - 創新：測試框架搭建


## Case #11: 「演算法優先」的效能策略（而非微調代碼或換 CPU）

### Problem Statement（問題陳述）
- 業務場景：系統效能瓶頸明顯，微調代碼（從 100ms 到 90ms）或升級硬體效果有限，需靠演算法帶動數倍提升。
- 技術挑戰：辨識瓶頸與選擇合適演算法。
- 影響範圍：成本/時程/用戶體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 微優化收益固定且有限
  2. 錯誤的資料結構/演算法導致多餘運算
  3. 缺乏複雜度思維
- 深層原因：
  - 架構層面：未確立性能設計原則
  - 技術層面：對典型演算法了解不足
  - 流程層面：無基準、無對比

### Solution Design
- 解決策略：建立性能優先級：先換演算法/資料結構（如 DFS→Dijkstra、List→HashSet/Dict），再考慮微優化，最後才是硬體。

- 實施步驟：
  1. 性能剖析
     - 實作細節：找熱點/時間佔比
     - 預估時間：0.5 天
  2. 複雜度分析與替換
     - 實作細節：確認可降階（如 O(n)→O(1)）
     - 預估時間：1 天
  3. 回歸測試
     - 實作細節：確保正確性不退化
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```text
Workflow:
- Profile -> Identify Hotspots -> Map to Algorithm/DS -> Replace -> Benchmark -> Iterate
```

- 實際案例：原文多處強調：List→SortedList 差 6000 倍；HashSet.Contains O(1)；DFS→擴散式演算法數量級提升。
- 實作環境：任意
- 實測數據：依案例不同（見各案）
- Learning Points：演算法優先、量化思維、替換策略
- 技能要求：基礎演算法複雜度；進階性能剖析
- 延伸思考：可應用於資料庫索引、快取策略；風險是過早優化；可透過 SLA 導向

- Practice：建立性能診斷清單（30 分）；替換一個瓶頸（2 小時）；完成端到端性能優化（8 小時）
- Assessment：功能正確、代碼清晰、效能可驗、創新方案


## Case #12: 遞迴 vs 顯式堆疊的取捨（可讀性與風險）

### Problem Statement（問題陳述）
- 業務場景：搜尋邏輯以遞迴實作更簡潔，但可能遇到遞迴深度限制；顯式堆疊更可控但代碼較長。
- 技術挑戰：在可讀性與穩定性間平衡。
- 影響範圍：大圖下可能 StackOverflow、除錯難度不同。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 遞迴深度受限於 call stack
  2. 顯式堆疊管理繁瑣
  3. 缺少壓測
- 深層原因：
  - 架構層面：邏輯與實作綁定
  - 技術層面：不熟兩者等價轉換
  - 流程層面：未規劃極端案例測試

### Solution Design
- 解決策略：小圖用遞迴；大圖用顯式堆疊；提供兩種實作並透過設定切換，兼顧教學與實務。

- 實施步驟：
  1. 撰寫迭代版 DFS
  2. 加入策略切換
  3. 壓測最大深度

- 關鍵程式碼/設定：
```csharp
public void DFSIterative(string start, string end)
{
    var stack = new Stack<(string node, IEnumerator<Link> it)>();
    var visited = new HashSet<string>();
    stack.Push((start, _nodes[start].Links.GetEnumerator()));
    visited.Add(start);
    // ... 模擬遞迴呼叫與回溯
}
```

- 實際案例：原文偏好遞迴以簡化代碼。
- 實作環境：.NET/C#
- 實測數據：
  - 遞迴：代碼短、風險在深度
  - 迭代：代碼長、穩定性高
- Learning Points：兩者等價性、風險管理、壓測
- 技能要求：控制流程；進階為狀態機設計
- 延伸思考：尾遞迴優化（C# 不保證）；風險在複雜狀態
- Practice：將遞迴改為迭代（30 分）；壓測比較（2 小時）；策略切換（8 小時）
- Assessment：功能一致、代碼品質、穩健性、創新策略


## Case #13: 使用 HashSet 做集合運算（交集/聯集）輔助圖運算

### Problem Statement（問題陳述）
- 業務場景：需快速求兩集合（如可達節點、道路集合）的交/聯集，用於分析或優化（如雙向搜尋、篩選）。
- 技術挑戰：若用 List 進行操作，效能差。
- 影響範圍：分析工具與搜尋剪枝效率。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. List 無集合語義與對應操作
  2. 交/聯集操作成本高
  3. 缺乏 O(1) Contains
- 深層原因：
  - 架構層面：缺集合抽象
  - 技術層面：未利用 HashSet.IntersectWith/UnionWith
  - 流程層面：缺性能意識

### Solution Design
- 解決策略：採用 HashSet<T> 儲存集合，使用內建 IntersectWith/UnionWith/ExceptWith 操作。

- 實施步驟：
  1. 集合轉型
  2. 應用內建方法
  3. 加入驗證/基準測試

- 關鍵程式碼/設定：
```csharp
var s1 = new HashSet<string>(reachableFromA);
var s2 = new HashSet<string>(reachableFromB);
s1.IntersectWith(s2); // s1 現在是交集
```

- 實際案例：原文指出 HashSet 適合集合運算，並列舉 IntersectWith 的複雜度。
- 實作環境：.NET 3.5+
- 實測數據：
  - 改善前：自實作交集 O(n*m)
  - 改善後：O(n) 或 O(n+m)
  - 改善幅度：數倍至數十倍

- Learning Points：集合運算複雜度、內建 API
- 技能要求：集合 API；進階為多集合操作
- 延伸思考：雙向搜尋剪枝；風險為記憶體增長；可優化為序列化儲存
- Practice：用交集找共同可達點（30 分）；雙向剪枝（2 小時）；集合度量報表（8 小時）
- Assessment：功能正確、代碼簡潔、效能顯著、創新使用場景


## Case #14: 以資料庫表建模圖（Node/Link 表）—設計正確性

### Problem Statement（問題陳述）
- 業務場景：實務上資料多存於資料庫；若不懂圖模型，無法設計正確資料表以支援路徑搜尋。
- 技術挑戰：如何以關聯式表正確表示圖、避免資料異常。
- 影響範圍：後續查詢/效能/資料一致性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 不知以節點/連線拆表
  2. 無端點外鍵，難保一致
  3. 缺索引，查詢慢
- 深層原因：
  - 架構層面：資料模型未對齊領域模型
  - 技術層面：關聯式表與圖的映射知識缺乏
  - 流程層面：需求分析不到位

### Solution Design
- 解決策略：設計 Node/Link 兩表，Link 以 NodeId1/NodeId2 外鍵連至 Node，建立必要索引；以視圖/儲存程序提供查詢。

- 實施步驟：
  1. 定義表
  2. 設索引/外鍵
  3. 匯入資料與驗證

- 關鍵程式碼/設定：
```sql
CREATE TABLE Node (Id INT PRIMARY KEY, Name NVARCHAR(50) UNIQUE, TollFee INT);
CREATE TABLE Link (Id INT PRIMARY KEY, FromNodeId INT, ToNodeId INT, Distance FLOAT, Road TINYINT,
  FOREIGN KEY (FromNodeId) REFERENCES Node(Id),
  FOREIGN KEY (ToNodeId) REFERENCES Node(Id));
CREATE INDEX IX_Link_From ON Link(FromNodeId);
CREATE INDEX IX_Link_To ON Link(ToNodeId);
```

- 實際案例：原文指出不懂圖就不知如何建表；此為對應方案。
- 實作環境：SQL Server 等
- 實測數據：
  - 改善前：無法支援路徑查詢
  - 改善後：具備正確關聯與查詢基礎
  - 改善幅度：功能性從無到有

- Learning Points：圖→關聯式映射、索引設計
- 技能要求：SQL 基礎；進階是圖查詢（CTE/遞迴）
- 延伸思考：可用圖資料庫；風險為遞迴查詢成本；優化為離線計算/快取
- Practice：設計表與匯入（30 分）；CTE 查找 k 步可達（2 小時）；儲存程序版最短路（8 小時）
- Assessment：結構正確、資料一致、查詢可用、創新映射


## Case #15: 道路網採用鄰接表而非鄰接矩陣（稀疏圖優化）

### Problem Statement（問題陳述）
- 業務場景：高速公路網屬稀疏圖（節點間連線有限），需節省記憶體並提升遍歷效率。
- 技術挑戰：選擇合適的圖存儲結構（Adjacency List vs Matrix）。
- 影響範圍：記憶體占用、遍歷速度、可擴充性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 矩陣記憶體 O(V^2) 過大
  2. 稀疏圖下大量 0 邊
  3. 遍歷鄰接邊需求明確
- 深層原因：
  - 架構層面：資料規模預估不足
  - 技術層面：未評估兩種結構利弊
  - 流程層面：缺總體容量評估

### Solution Design
- 解決策略：採用鄰接表（每個 Node 維護 Links），以 O(V+E) 記憶體、O(deg(v)) 遍歷鄰邊，匹配路網特性。

- 實施步驟：
  1. 建模為 List<Link>（見 Case #1）
  2. 驗證遍歷成本
  3. 壓測記憶體占用

- 關鍵程式碼/設定：
```csharp
public class Node { public List<Link> Links = new List<Link>(); /* ... */ }
```

- 實際案例：原文即採用鄰接表結構。
- 實作環境：.NET/C#
- 實測數據：
  - 改善前：若用矩陣，空間 O(V^2)
  - 改善後：鄰接表 O(V+E)
  - 改善幅度：大規模下顯著

- Learning Points：結構選型與圖密度
- 技能要求：圖結構；進階為圖壓縮技巧
- 延伸思考：非常密集圖再考慮矩陣；風險為隨機邊查找較慢；可優化為鄰接字典
- Practice：模擬 V=1e4、E=3e4 記憶體估算（30 分）；鄰接字典改造（2 小時）；圖壓縮（8 小時）
- Assessment：結構合理、可擴充、效能匹配、創新壓縮


--------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case #1, #2, #4, #8, #9, #13, #15
- 中級（需要一定基礎）
  - Case #3, #6, #10, #11, #12, #14
- 高級（需要深厚經驗）
  - Case #5

2) 按技術領域分類
- 架構設計類：#1, #11, #12, #14, #15
- 效能優化類：#4, #5, #10, #11, #13, #15
- 整合開發類：#2, #6, #8, #14
- 除錯診斷類：#6, #9, #11, #12
- 安全防護類：無直接案例（本篇未涉及安全）

3) 按學習目標分類
- 概念理解型：#1, #11, #12, #15
- 技能練習型：#2, #3, #4, #8, #9, #13
- 問題解決型：#5, #6, #10, #14
- 創新應用型：#11, #13, #14, #15

--------------------------------
案例關聯圖（學習路徑建議）
- 先學順序（基礎概念與建模）
  1) Case #1（圖模型）→ 2) Case #2（Dictionary 索引）→ 3) Case #15（鄰接表選型）
- 路徑搜尋核心
  4) Case #3（DFS 全路徑）→ 5) Case #4（HashSet 已訪）→ 6) Case #9（路徑順序）→ 7) Case #8（路線輸出）
- 成本與正確性
  8) Case #6（成本函式與修正）
- 進階效能與演算法
  9) Case #10（集合選型效能觀）→ 10) Case #11（演算法優先策略）→ 11) Case #5（Dijkstra）
- 工程化與擴展
  12) Case #12（遞迴 vs 迭代）→ 13) Case #13（集合運算輔助）→ 14) Case #14（資料庫建模）

依賴關係：
- #3 依賴 #1、#2、#15
- #4 依賴 #3
- #5 依賴 #1、#2、#6
- #8 依賴 #3 或 #5 與 #2
- #6 為 #3/#5 的通用依賴
- #10/#11 為橫向能力，支持 #3/#5/#13 優化
- #14 建基於 #1 的模型概念

完整學習路徑：
- 建模（#1→#2→#15）→ 搜尋基礎與輸出（#3→#4→#9→#8）→ 成本與正確性（#6）→ 效能觀與演算法升級（#10→#11→#5）→ 工程化與擴展（#12→#13→#14）。此路徑由易到難、由小到大，兼顧概念、實作與工程化落地。