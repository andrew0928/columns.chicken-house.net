以下內容基於文章中的程式與設計，提煉出可教學、可實作、可評估的 15 個問題解決案例。每個案例都給出問題、根因、解法、關鍵程式碼、實作細節與練習與評估標準，便於課堂演練與專案實作。

## Case #1: 以 OOP 設計重構生命遊戲（World/Cell 架構）

### Problem Statement（問題陳述）
業務場景：在課堂或作品集中常用生命遊戲作為演算法練習，但多數網路範例偏向程序式寫法，缺乏物件導向設計，造成程式難以擴充（如切換規則、加上觀察者、統計指標）且可讀性不佳。本案例將以 World/Cell 的類別責任切分實作同題，展示封裝與清晰介面對可維護性的幫助。
技術挑戰：如何辨識合適的類別、清楚定義公開介面與職責、避免 UI 與領域邏輯耦合。
影響範圍：可讀性、可維護性、可測試性；未來加功能的成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 範例普遍用二維陣列與程序式流程，無清楚的型別與邏輯界線。
2. 規則判斷散落在主流程，難以替換與單元測試。
3. UI 輸出與狀態運算混在一起，耦合高。
深層原因：
- 架構層面：缺乏明確的模型層（Cell/World）與呈現層分離。
- 技術層面：未善用封裝、介面與多型等 OOP 特性。
- 流程層面：先寫出結果，未先做設計與類別圖。

### Solution Design（解決方案設計）
解決策略：以「World/Cell」為核心模型，封裝鄰居搜尋與規則運算於 Cell，World 提供座標存取與迭代支援，主程式只負責驅動世代推進與委派渲染。分離關注點，使規則變更、渲染替換與測試更容易。

實施步驟：
1. 建立類別圖與介面
- 實作細節：World 提供 GetCell、座標界線；Cell 提供 IsAlive 與 OnNextStateChange（先版）。
- 所需資源：Visual Studio、UML（選用）
- 預估時間：1 小時
2. 撰寫 World/Cell 與主程式
- 實作細節：使用文章中程式骨架；先確保可跑。
- 所需資源：.NET/C#
- 預估時間：1-2 小時

關鍵程式碼/設定：
```csharp
public class World {
  private readonly Cell[,] _map;
  public World(int x, int y) {
    _map = new Cell[x, y];
    for (int i=0;i<x;i++) for (int j=0;j<y;j++) _map[i,j]=new Cell(this,i,j);
  }
  public Cell GetCell(int x,int y)=> (x<0||y<0||x>=_map.GetLength(0)||y>=_map.GetLength(1))?null:_map[x,y];
}

public class Cell {
  public bool IsAlive { get; private set; }
  private readonly World _world;
  internal int PosX, PosY;
  public Cell(World world,int x,int y){ _world=world; PosX=x; PosY=y; /* init alive by prob */ }
  public void OnNextStateChange(){ /* 先版：直接依鄰居數更新 IsAlive（之後在 Case#2 修正） */ }
}
```

實際案例：文章中的 World/Cell 架構與主程式。
實作環境：C#、.NET（VS2008/Console），任意最新 .NET 亦可。
實測數據：
改善前：程序式寫法耦合高、規則難替換。
改善後：類別職責清晰，可插拔規則與渲染（為後續案例鋪路）。
改善幅度：可維護性與可讀性明顯提升（定性）。

Learning Points（學習要點）
核心知識點：
- 封裝與職責切分（World/Cell）
- 介面最小化與單一職責
- 以模型為中心的驅動流程
技能要求：
- 必備技能：C# 基礎、類別與屬性
- 進階技能：UML/設計原則（SRP、SoC）
延伸思考：
- 如要支持不同規則或渲染如何設計？
- 如何為 World/Cell 撰寫單元測試？
- 如何與 UI 框架（WinForms/WPF）整合？

Practice Exercise（練習題）
基礎練習：用 OOP 重寫最小版生命遊戲（10x10、隨機初始化）。
進階練習：加入載入固定初始圖樣（glider）。
專案練習：設計可切換規則與渲染器的生命遊戲小框架。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可正確跑出多代並渲染。
- 程式碼品質（30%）：World/Cell 職責清晰、介面簡潔。
- 效能優化（20%）：基本渲染不卡頓。
- 創新性（10%）：可替換規則或渲染的設計。

---

## Case #2: 修正「同代即時寫入」導致的狀態污染（雙緩衝更新）

### Problem Statement（問題陳述）
業務場景：在課堂展示生命遊戲時，發現某些標準圖樣（如 blinker）在本程式中表現不正確或早衰，推測為同代計算時彼此干擾。希望修正為「同時更新」的正確規則。
技術挑戰：避免在計算某細胞時讀到已被更新的鄰居狀態，需雙階段（計算下一代＋套用下一代）。
影響範圍：正確性、可測試性、並行化可能性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. OnNextStateChange 直接寫 IsAlive，破壞同一代的鄰居讀取一致性。
2. 主程式逐格呼叫，順序導致早計算的單元影響後計算單元。
3. 欠缺 next state 暫存或世界級雙緩衝。
深層原因：
- 架構層面：缺少狀態轉移的分離（Compute vs Apply）。
- 技術層面：未設計資料緩衝或不可變快照。
- 流程層面：未以規則需求（同時更新）驅動設計。

### Solution Design（解決方案設計）
解決策略：改為雙階段：先全域計算每個 Cell 的 NextIsAlive，再統一套用。或使用世界層級兩個布林陣列做雙緩衝，確保同代一致性。

實施步驟：
1. 新增 NextIsAlive 與 Compute/Apply
- 實作細節：ComputeNextState 只讀 IsAlive 與鄰居，計算 NextIsAlive；ApplyNextState 將 NextIsAlive 指派回 IsAlive。
- 所需資源：C# 修改既有類別
- 預估時間：0.5 小時
2. 調整驅動流程為兩趟
- 實作細節：第一輪全域呼叫 ComputeNextState，第二輪呼叫 ApplyNextState。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class Cell {
  public bool IsAlive { get; private set; }
  public bool NextIsAlive { get; private set; }

  public void ComputeNextState() {
    int lives = 0;
    foreach (var n in FindNeighbors()) if (n.IsAlive) lives++;
    if (IsAlive && lives < 2) NextIsAlive = false;         // 修正 <1 為 <2（標準規則）
    else if (IsAlive && lives > 3) NextIsAlive = false;
    else if (IsAlive && (lives == 2 || lives == 3)) NextIsAlive = true;
    else if (!IsAlive && lives == 3) NextIsAlive = true;
    else NextIsAlive = IsAlive;
  }

  public void ApplyNextState() => IsAlive = NextIsAlive;
}

// 主程式更新：
for (int x=0; x<worldSizeX; x++)
  for (int y=0; y<worldSizeY; y++)
    realworld.GetCell(x,y).ComputeNextState();

for (int x=0; x<worldSizeX; x++)
  for (int y=0; y<worldSizeY; y++)
    realworld.GetCell(x,y).ApplyNextState();
```

實際案例：blinker、block、beehive 等圖樣在雙緩衝後能維持標準行為。
實作環境：C#/.NET Console。
實測數據：
改善前：振盪器行為異常（規則被污染）。
改善後：振盪器與靜物符合預期。
改善幅度：正確性由不穩定提升為符合規格（定性）。

Learning Points（學習要點）
核心知識點：
- 同步更新需求與雙緩衝設計
- 計算/套用兩階段模式
- 對並行友善的演算法結構
技能要求：
- 必備技能：基本演算法設計
- 進階技能：資料不可變觀念
延伸思考：
- 世界層級雙緩衝（bool[,] front/back）是否更快？
- 如何在 GPU 或多執行緒擴展？
- 如何以單元測試驗證規則正確性？

Practice Exercise（練習題）
基礎練習：將現有程式改成 Compute/Apply 兩階段。
進階練習：改為世界雙緩衝（兩個 bool[,]）。
專案練習：支援在執行中切換規則且保持雙緩衝正確性。

Assessment Criteria（評估標準）
- 功能完整性（40%）：標準圖樣表現正確。
- 程式碼品質（30%）：兩階段清楚、無交叉依賴。
- 效能優化（20%）：無顯著退化，或可微幅提昇。
- 創新性（10%）：雙緩衝抽象通用化。

---

## Case #3: 修正 Cell 建構式座標指派錯誤（PosX = posY）

### Problem Statement（問題陳述）
業務場景：在視覺化輸出時，發現部分細胞位置與預期不一致，尤其是初始化即出現偏移或圖樣扭曲。檢查後定位到 Cell 建構式座標指派錯誤。
技術挑戰：快速定位錯誤、避免相依方法（PutOn）加劇錯誤影響。
影響範圍：所有位置相關邏輯（鄰居搜尋、渲染）。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 建構式中 this.PosX = posY; this.PosY = posY; 應為 PosX = posX。
2. 位置錯誤導致 FindNeighbors 計算錯誤集合。
3. 渲染也會顯示錯位。
深層原因：
- 架構層面：未以不可變初始化或工廠驗證。
- 技術層面：缺少基本單元測試覆蓋座標設定。
- 流程層面：缺乏 Code Review 或最小範例驗證。

### Solution Design（解決方案設計）
解決策略：修正指派錯誤，加入座標不變式檢查與單元測試（Case #9 會補上），避免類似錯誤再次發生。

實施步驟：
1. 修正程式碼
- 實作細節：PosX 正確賦值 posX；保留 PutOn 的校驗。
- 所需資源：IDE
- 預估時間：10 分鐘
2. 加入防呆與測試
- 實作細節：在 Debug 模式 Assert 座標一致；加單元測試驗證。
- 所需資源：xUnit/nUnit
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public Cell(World world, int posX, int posY) {
  CurrentWorld = world;
  PosX = posX;     // 修正
  PosY = posY;
  CurrentWorld.PutOn(this, posX, posY);
}
```

實際案例：初始化 glider 時不再出現偏移。
實作環境：C#/.NET。
實測數據：
改善前：圖樣扭曲，鄰居計算錯。
改善後：座標正確、鄰居正確。
改善幅度：正確性由錯誤到正確（定性）。

Learning Points（學習要點）
核心知識點：
- 建構式不變式與參數校驗
- 位置資訊對運算的級聯影響
- 單元測試針對 bug 回歸
技能要求：
- 必備技能：C# 基礎、Debug
- 進階技能：測試驅動思維
延伸思考：
- 是否將座標設為 readonly？
- 是否改用工廠方法建立 Cell？

Practice Exercise（練習題）
基礎練習：修正座標並印出座標驗證。
進階練習：加入 Debug.Assert 驗證 PosX/PosY 與 PutOn 座標一致。
專案練習：撰寫座標相關的回歸測試套件。

Assessment Criteria（評估標準）
- 功能完整性（40%）：初始化座標正確。
- 程式碼品質（30%）：有不變式/防呆。
- 效能優化（20%）：無額外負擔或可在 Release 移除。
- 創新性（10%）：引入工廠或不可變設計。

---

## Case #4: 鄰居查找效能優化（預先快取 neighbors）

### Problem Statement（問題陳述）
業務場景：在 30x30 以上網格運行多代後，CPU 使用率偏高。分析顯示每代每格都重複呼叫 GetCell 8 次。希望降低重複查找開銷。
技術挑戰：在不改變規則正確性的前提下，降低鄰居定位的成本。
影響範圍：整體效能、可伸縮性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. FindNeighbors 每次動態建立陣列並逐一 GetCell。
2. 同一格的鄰居位置在整個模擬過程中不變。
3. 反覆配置與邏輯開銷累積顯著。
深層原因：
- 架構層面：未將靜態拓撲（鄰接）與動態狀態（存活）分離。
- 技術層面：缺少快取策略。
- 流程層面：未以效能分析回饋優化設計。

### Solution Design（解決方案設計）
解決策略：在 Cell 建構時預先解析並快取鄰居引用陣列；後續每代只遍歷引用，避免重複查找與配置。

實施步驟：
1. 新增 neighbors 快取欄位
- 實作細節：建構式取得合法鄰居引用填入陣列。
- 所需資源：無
- 預估時間：0.5 小時
2. 修改計算流程使用快取
- 實作細節：FindNeighbors 改為直接 yield 快取。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class Cell {
  private Cell[] _neighbors;
  public Cell(World world, int x, int y) {
    // ... 座標賦值
    _neighbors = new[] {
      world.GetCell(x-1,y-1), world.GetCell(x,y-1), world.GetCell(x+1,y-1),
      world.GetCell(x-1,y),                       world.GetCell(x+1,y),
      world.GetCell(x-1,y+1), world.GetCell(x,y+1), world.GetCell(x+1,y+1)
    }.Where(c => c != null).ToArray();
  }
  protected IEnumerable<Cell> FindNeighbors() => _neighbors;
}
```

實際案例：在 100x100 網格下代數推進更順暢（定性觀察）。
實作環境：C#/.NET。
實測數據：
改善前：每代大量 GetCell 次數。
改善後：GetCell 僅初始化一次。
改善幅度：CPU 使用率下降（定性），可自行以 Stopwatch 量測。

Learning Points（學習要點）
核心知識點：
- 拓撲與狀態分離
- 記憶體換時間（空間/時間權衡）
- 預先計算與快取策略
技能要求：
- 必備技能：C# 集合/陣列
- 進階技能：效能剖析思維
延伸思考：
- 大網格是否採 bitset 更省？
- 快取對記憶體的影響如何控制？

Practice Exercise（練習題）
基礎練習：將 neighbors 改為快取。
進階練習：以 Stopwatch 比較前後每代耗時。
專案練習：封裝成 IAdjacencyProvider 以便替換不同拓撲（包邊/環形）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：規則不變，結果一致。
- 程式碼品質（30%）：快取實作簡潔。
- 效能優化（20%）：能展示改善。
- 創新性（10%）：可插拔拓撲。

---

## Case #5: 分離渲染（UI）與世界（領域）邏輯

### Problem Statement（問題陳述）
業務場景：現有 World.ShowMaps 直接操作 Console，導致無法在其他 UI（WinForms/WPF/Blazor）重用世界邏輯。希望解耦以便於換渲染器。
技術挑戰：定義穩定的渲染介面，避免領域物件依賴 UI。
影響範圍：可移植性、可測試性、擴展能力。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. World 直接呼叫 Console API。
2. 文字渲染與狀態輸出耦合。
3. 無法在無 Console 環境下測試。
深層原因：
- 架構層面：未分層（Presentation vs Domain）。
- 技術層面：缺乏抽象渲染介面。
- 流程層面：先寫可見結果，後想抽象。

### Solution Design（解決方案設計）
解決策略：定義 IWorldRenderer 介面；World 僅提供狀態存取；主程式注入具體渲染器（ConsoleRenderer）。

實施步驟：
1. 定義渲染介面與 Console 實作
- 實作細節：Draw(World) 讀取狀態輸出；ConsoleRenderer 專責 Console 操作。
- 所需資源：無
- 預估時間：1 小時
2. 調整主程式注入渲染器
- 實作細節：移除 World.ShowMaps，改呼叫 renderer.Draw(world)。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public interface IWorldRenderer { void Draw(World world, string title); }

public class ConsoleRenderer : IWorldRenderer {
  public void Draw(World w, string title) {
    Console.Title = title;
    for (int y=0; y<w.SizeY; y++)
      for (int x=0; x<w.SizeX; x++) {
        var cell = w.GetCell(x,y);
        Console.SetCursorPosition(x*2, y);
        Console.Write(cell.IsAlive ? "●" : "○");
      }
  }
}

// Main:
IWorldRenderer renderer = new ConsoleRenderer();
renderer.Draw(realworld, $"Generation: {generation}");
```

實際案例：同一 World 可用於 Console 或 WinForms PictureBox 渲染。
實作環境：C#/.NET。
實測數據：
改善前：無法替換 UI。
改善後：可自由替換渲染器；單元測試可用虛擬渲染器收集輸出。
改善幅度：可移植性明顯提升（定性）。

Learning Points（學習要點）
核心知識點：
- 分層設計（Domain/Presentation）
- 介面與依賴注入
- 可測試性提升技巧
技能要求：
- 必備技能：介面、依賴注入概念
- 進階技能：UI 抽象
延伸思考：
- 事件/Observer 通知改變 vs 直接拉取？
- 如何支援虛擬繪製做快照比較？

Practice Exercise（練習題）
基礎練習：提取 World.ShowMaps 成 ConsoleRenderer。
進階練習：新增 DummyRenderer 收集字元陣列以便測試。
專案練習：新增 WinFormsRenderer/WPFRenderer。

Assessment Criteria（評估標準）
- 功能完整性（40%）：Console 與 DummyRenderer 皆可用。
- 程式碼品質（30%）：無 UI 依賴殘留在 Domain。
- 效能優化（20%）：渲染不退化。
- 創新性（10%）：支援多種渲染。

---

## Case #6: 降低 Console 閃爍與不必要操作（增量渲染）

### Problem Statement（問題陳述）
業務場景：每代都 Clear 且 SetWindowSize，畫面閃爍且在某些終端機不相容（大小不足會丟例外）。希望使輸出更穩定順暢。
技術挑戰：在 Console 限制下做增量渲染、避免反覆清畫面、處理字寬問題。
影響範圍：用戶體驗、穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 每代 Console.Clear 與 SetWindowSize。
2. 使用全角符號「●/○」造成字寬處理複雜。
3. 未檢查 Console Buffer 限制。
深層原因：
- 架構層面：渲染器未維護前一幀狀態。
- 技術層面：未使用增量更新策略。
- 流程層面：未考慮終端機相容性差異。

### Solution Design（解決方案設計）
解決策略：渲染器保留上一幀緩衝，僅輸出差異；啟動時設定一次窗口大小；改用等寬字元（例如 '#'/'.'）提高相容性與效能。

實施步驟：
1. 初始化一次性設定與緩衝
- 實作細節：設定 Buffer/WindowSize，建立 char[,] prev。
- 所需資源：Console API
- 預估時間：0.5 小時
2. 增量渲染
- 實作細節：比較當前與 prev，不同才 SetCursorPosition+Write。
- 所需資源：無
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public class ConsoleRenderer : IWorldRenderer {
  private char[,] _prev;
  public void Init(int w, int h) {
    Console.OutputEncoding = System.Text.Encoding.UTF8;
    Console.SetWindowSize(Math.Min(Console.LargestWindowWidth, w), Math.Min(Console.LargestWindowHeight, h));
    _prev = new char[w, h];
    for(int x=0;x<w;x++) for(int y=0;y<h;y++) _prev[x,y]=' ';
  }
  public void Draw(World world, string title) {
    Console.Title = title;
    for (int y=0; y<world.SizeY; y++)
      for (int x=0; x<world.SizeX; x++) {
        char ch = world.GetCell(x,y).IsAlive ? '#' : '.';
        if (_prev[x,y] != ch) {
          Console.SetCursorPosition(x, y);
          Console.Write(ch);
          _prev[x,y] = ch;
        }
      }
  }
}
```

實際案例：畫面穩定、閃爍明顯降低。
實作環境：C#/.NET Console。
實測數據：
改善前：閃爍明顯、偶發視窗大小例外。
改善後：穩定輸出、相容性更佳。
改善幅度：體感流暢度明顯提升（定性）。

Learning Points（學習要點）
核心知識點：
- 增量渲染與緩衝
- Console 限制與相容性
- 字寬/編碼處理
技能要求：
- 必備技能：Console API
- 進階技能：雙緩衝與差異輸出
延伸思考：
- 是否用 System.Console 的 VT 序列提升效能？
- 是否切換到 WinForms/WPF 繪圖更好？

Practice Exercise（練習題）
基礎練習：引入 prev 緩衝只畫差異。
進階練習：支援不同字元集配置。
專案練習：做簡易 FPS 與渲染耗時統計。

Assessment Criteria（評估標準）
- 功能完整性（40%）：畫面可持續運作無例外。
- 程式碼品質（30%）：渲染器職責清晰。
- 效能優化（20%）：輸出次數明顯減少。
- 創新性（10%）：引入 VT 或自動降級策略。

---

## Case #7: 移除 Magic Numbers，參數化世界與初始化機率

### Problem Statement（問題陳述）
業務場景：worldSizeX/Y、InitAliveProbability 寫死，難以做實驗（大小/密度調參）。希望支援命令列參數或組態檔設定。
技術挑戰：可靠解析參數、提供預設、避免破壞舊用例。
影響範圍：可用性、可重現性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 常數寫死於程式碼。
2. 無統一設定來源與驗證。
3. 無法記錄與重現實驗條件。
深層原因：
- 架構層面：缺少設定層。
- 技術層面：未實作解析與驗證。
- 流程層面：快速示範未考慮長期使用。

### Solution Design（解決方案設計）
解決策略：新增 Options 型別統一管理設定，支援命令列與預設值，集中驗證與日誌輸出。

實施步驟：
1. 定義 Options 與解析
- 實作細節：解析 args（或使用 System.CommandLine）。
- 所需資源：.NET CLI、可選套件
- 預估時間：1 小時
2. 注入設定
- 實作細節：Main 讀取 Options 建立 World。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public record Options(int X=30,int Y=30,int Generations=100,double InitProb=0.2,int Seed=-1);

static Options ParseArgs(string[] args) {
  // 簡易解析，省略健壯性
  // 支援 --x --y --gen --p --seed
  // 若無提供則使用預設
  return new Options();
}

static void Main(string[] args) {
  var opt = ParseArgs(args);
  var world = new World(opt.X, opt.Y, opt.InitProb, opt.Seed);
}
```

實際案例：透過命令列快速調整大小與密度。
實作環境：C#/.NET。
實測數據：
改善前：每次改值需重編譯。
改善後：一次編譯，多場景重用。
改善幅度：開發效率提升（定性）。

Learning Points（學習要點）
核心知識點：
- 組態與參數化設計
- 預設值與驗證
- 可重現性（seed）
技能要求：
- 必備技能：命令列處理
- 進階技能：配置管理
延伸思考：
- 是否支援 json/yaml 設定？
- 不同環境（CI）如何注入？

Practice Exercise（練習題）
基礎練習：加上命令列解析。
進階練習：支援 seed 固定亂數。
專案練習：從 appsettings.json 讀取設定。

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有參數可用並驗證。
- 程式碼品質（30%）：集中管理設定。
- 效能優化（20%）：解析不影響主流程。
- 創新性（10%）：支援多種來源與覆蓋規則。

---

## Case #8: 邊界策略設計（固定邊界 vs 環形包裹）

### Problem Statement（問題陳述）
業務場景：目前使用有限棋盤（出界即 null），在某些模擬希望採用環形（Toroidal）空間。需要可配置的邊界策略。
技術挑戰：不改動核心規則前提下切換邊界處理。
影響範圍：模擬行為、可重用性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. GetCell 用 null 表示出界，策略寫死。
2. FindNeighbors 直接依賴當前策略。
3. 難以比較不同邊界對結果的影響。
深層原因：
- 架構層面：策略未抽象。
- 技術層面：缺少可插拔設計。
- 流程層面：以單一場景為目標開發。

### Solution Design（解決方案設計）
解決策略：引入 IBoundaryPolicy，World 持有政策；Cell 查找鄰居透過政策取得有效座標或 null。

實施步驟：
1. 定義邊界介面與兩種實作
- 實作細節：FixedBoundary、ToroidalBoundary。
- 所需資源：無
- 預估時間：1 小時
2. World/Cell 接入政策
- 實作細節：FindNeighbors 透過 policy 提供座標轉換。
- 所需資源：無
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public interface IBoundaryPolicy {
  bool TryNormalize(int x, int y, int maxX, int maxY, out int nx, out int ny);
}
public class FixedBoundary : IBoundaryPolicy {
  public bool TryNormalize(int x,int y,int mx,int my,out int nx,out int ny){
    nx=x; ny=y; return x>=0&&y>=0&&x<mx&&y<my;
  }
}
public class ToroidalBoundary : IBoundaryPolicy {
  public bool TryNormalize(int x,int y,int mx,int my,out int nx,out int ny){
    nx = (x%mx+mx)%mx; ny = (y%my+my)%my; return true;
  }
}

public class World {
  internal IBoundaryPolicy Boundary { get; }
  // ...
}
```

實際案例：同一初始圖樣在兩種邊界下做對比。
實作環境：C#/.NET。
實測數據：
改善前：僅支援固定邊界。
改善後：可切換邊界政策。
改善幅度：適用場景擴大（定性）。

Learning Points（學習要點）
核心知識點：
- 策略模式（Strategy）
- 座標規範化
- 可配置架構
技能要求：
- 必備技能：介面/策略
- 進階技能：對比性實驗設計
延伸思考：
- 障礙物/障壁如何建模？
- 邊界策略的效能影響？

Practice Exercise（練習題）
基礎練習：實作 ToroidalBoundary。
進階練習：加入不可通過障壁策略。
專案練習：以不同策略比較活細胞數變化曲線。

Assessment Criteria（評估標準）
- 功能完整性（40%）：策略可切換且正確。
- 程式碼品質（30%）：抽象合理、耦合低。
- 效能優化（20%）：無明顯退化。
- 創新性（10%）：自定策略（反彈等）。

---

## Case #9: 建立單元測試驗證四條規則

### Problem Statement（問題陳述）
業務場景：程式重構與優化後，需要自動化驗證仍符合生命遊戲四大規則，避免回歸錯誤。
技術挑戰：快速搭建可重複的測試，避免渲染與隨機性干擾。
影響範圍：正確性、回歸風險、開發效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無測試導致錯誤（座標、雙緩衝）難以及時發現。
2. 隨機初始化不可重現。
3. 渲染耦合使測試困難。
深層原因：
- 架構層面：缺少可測試 API（如設置特定初態）。
- 技術層面：未引入測試框架。
- 流程層面：未建立回歸測試機制。

### Solution Design（解決方案設計）
解決策略：使用固定初態（小棋盤）建立 xUnit 測試，驗證 underpopulation/overpopulation/survival/reproduction。以 seed 或直接設置狀態避免隨機。

實施步驟：
1. 可測試 API
- 實作細節：World 提供 SetAlive(x,y,bool) for test。
- 所需資源：無
- 預估時間：0.5 小時
2. 撰寫 xUnit 測試
- 實作細節：針對四規則建立案例。
- 所需資源：xUnit
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
[Fact]
public void Reproduction_DeadWithThreeNeighbors_ComesAlive() {
  var w = new World(3,3);
  w.SetAlive(0,0,true); w.SetAlive(1,0,true); w.SetAlive(2,0,true);
  w.Step(); // 兩階段推進一代
  Assert.True(w.GetCell(1,1).IsAlive);
}
```

實際案例：以 blinker 兩代往返驗證。
實作環境：C#/.NET、xUnit。
實測數據：
改善前：無自動測試。
改善後：規則行為可被持續驗證。
改善幅度：回歸風險顯著下降（定性）。

Learning Points（學習要點）
核心知識點：
- 單元測試與可測試設計
- 固定初態與決定性
- 最小案例設計
技能要求：
- 必備技能：測試框架使用
- 進階技能：測試資料構造
延伸思考：
- 快照測試整個世界字串輸出？
- 隨機測試（property-based testing）？

Practice Exercise（練習題）
基礎練習：為四規則各寫一個測試。
進階練習：blinker 在兩代後回到原狀。
專案練習：為雙緩衝與策略邊界寫整合測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：四規則全備測。
- 程式碼品質（30%）：測試清楚、獨立。
- 效能優化（20%）：測試執行迅速。
- 創新性（10%）：引入 property-based 測試。

---

## Case #10: 觀測與指標（活細胞數、每代耗時）

### Problem Statement（問題陳述）
業務場景：需要量化模擬行為與效能影響（優化前後比較），但程式沒有任何統計與指標輸出。
技術挑戰：加入低干擾的指標收集與輸出。
影響範圍：效能分析、決策與迭代改進。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少活細胞數、世代耗時的收集。
2. 無法比較不同優化策略成效。
3. 渲染時間與運算時間混雜。
深層原因：
- 架構層面：無觀測點。
- 技術層面：未使用 Stopwatch 或計數器。
- 流程層面：無測量驅動改進文化。

### Solution Design（解決方案設計）
解決策略：在世界推進前後測量耗時，並在每代統計活細胞數與變化數；將指標輸出或記錄檔案。

實施步驟：
1. 加入統計 API
- 實作細節：World.CountAlive()；Step() 回傳 StepMetrics。
- 所需資源：Stopwatch
- 預估時間：1 小時
2. 輸出結果
- 實作細節：Console 或 CSV 紀錄。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public record StepMetrics(int Generation, int Alive, long ComputeMs, long RenderMs);

public class World {
  public int CountAlive() { int c=0; for(int x=0;x<SizeX;x++) for(int y=0;y<SizeY;y++) if(GetCell(x,y).IsAlive) c++; return c; }
}
```

實際案例：比較快取鄰居前後 ComputeMs 變化。
實作環境：C#/.NET。
實測數據：
改善前：無法量化。
改善後：可比較不同策略（定性/數值皆可）。
改善幅度：量化決策成為可能。

Learning Points（學習要點）
核心知識點：
- 度量驅動改進（MDA）
- 耗時分離（運算/渲染）
- 基本統計收集
技能要求：
- 必備技能：Stopwatch、檔案輸出
- 進階技能：資料視覺化（選用）
延伸思考：
- 指標會不會干擾效能？如何減輕？
- 是否以事件記錄（ETW）？

Practice Exercise（練習題）
基礎練習：輸出每代 Alive 與 ComputeMs。
進階練習：輸出 CSV 並畫圖。
專案練習：比較三種優化策略並寫報告。

Assessment Criteria（評估標準）
- 功能完整性（40%）：指標正確輸出。
- 程式碼品質（30%）：低耦合、低侵入。
- 效能優化（20%）：開關可控、開銷可控。
- 創新性（10%）：可視化/儀表板。

---

## Case #11: 記憶體與資料結構優化（bool[,] 與 struct）

### Problem Statement（問題陳述）
業務場景：當網格擴大（如 1000x1000）時，每格一個 Cell 物件造成顯著記憶體與 GC 壓力。希望改用緊湊資料結構。
技術挑戰：在保持邏輯正確性下，最小化物件數與記憶體佔用。
影響範圍：效能、伸縮性、可並行化。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 每格一個參考型別與欄位開銷。
2. 鄰居快取也增加記憶體。
3. GC 頻繁。
深層原因：
- 架構層面：物件過度建模。
- 技術層面：未使用陣列/位元集合。
- 流程層面：先求易寫，未求大型化。

### Solution Design（解決方案設計）
解決策略：用兩個 bool[,]（front/back）作雙緩衝，移除 Cell 物件；或以 BitArray/Span 壓縮。將規則計算提升至 World 層的純陣列運算。

實施步驟：
1. 重構為陣列核心
- 實作細節：World.Step 直接遍歷 bool[,]；鄰居計數以索引運算。
- 所需資源：.NET 陣列 API
- 預估時間：2-4 小時
2. 提供相容介面
- 實作細節：若需保留 Cell API，包裝輕量 facade。
- 所需資源：無
- 預估時間：1-2 小時

關鍵程式碼/設定：
```csharp
public class WorldArray {
  private bool[,] _front, _back;
  public void Step() {
    for(int y=0;y<Y;y++)
      for(int x=0;x<X;x++) {
        int n = CountNeighbors(_front, x, y);
        bool live = _front[x,y];
        _back[x,y] = (live && (n==2||n==3)) || (!live && n==3);
      }
    // swap
    var tmp=_front; _front=_back; _back=tmp;
  }
}
```

實際案例：大網格模擬的速度與記憶體壓力顯著改善（定性）。
實作環境：C#/.NET。
實測數據：
改善前：GC 壓力大、速度慢。
改善後：記憶體佔用降低、吞吐增加。
改善幅度：中大型網格下提升顯著（定性）。

Learning Points（學習要點）
核心知識點：
- 物件 vs 陣列的權衡
- 雙緩衝與 in-place 陣列操作
- 大型資料的效能模式
技能要求：
- 必備技能：陣列操作
- 進階技能：記憶體配置/GC 調優
延伸思考：
- SIMD/Vector 化可能性？
- 位元壓縮與查表優化？

Practice Exercise（練習題）
基礎練習：改用 bool[,] 雙緩衝。
進階練習：改用 BitArray 壓縮。
專案練習：Benchmark 三種資料結構下的 Step 耗時。

Assessment Criteria（評估標準）
- 功能完整性（40%）：結果與原版一致。
- 程式碼品質（30%）：結構清晰、介面穩定。
- 效能優化（20%）：耗時/記憶體改善。
- 創新性（10%）：進一步向 SIMD 發展。

---

## Case #12: 安全 API 設計（TryGetCell 與 Null 防護）

### Problem Statement（問題陳述）
業務場景：GetCell 出界回傳 null，FindNeighbors 需處理 null；當他處誤用 GetCell 可能造成 NullReferenceException。需提供更安全的 API。
技術挑戰：在不破壞既有呼叫的情況下提升安全性。
影響範圍：穩定性、易用性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 以 null 表示出界語意不明確。
2. 呼叫方不一定進行 null 檢查。
3. 無 Try 模式方法。
深層原因：
- 架構層面：缺乏錯誤處理策略。
- 技術層面：API 設計未考慮誤用。
- 流程層面：缺少防呆與契約。

### Solution Design（解決方案設計）
解決策略：新增 TryGetCell(x,y,out Cell) 與 InBounds(x,y)；保留 GetCell 但標註/文件警告；FindNeighbors 內部以 InBounds 過濾。

實施步驟：
1. 擴充 API
- 實作細節：Try 模式回傳 bool；不再鼓勵直接用 null。
- 所需資源：無
- 預估時間：0.5 小時
2. 內部遷移
- 實作細節：FindNeighbors 改用 InBounds。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public bool InBounds(int x,int y)=> x>=0&&y>=0&&x<SizeX&&y<SizeY;
public bool TryGetCell(int x,int y,out Cell cell){
  if (InBounds(x,y)) { cell=_map[x,y]; return true; }
  cell=null; return false;
}
```

實際案例：外部擴展功能誤用座標時不再拋空例外。
實作環境：C#/.NET。
實測數據：
改善前：偶發 NullReference。
改善後：以回傳值處理錯誤流程。
改善幅度：穩定性提升（定性）。

Learning Points（學習要點）
核心知識點：
- Try 模式 API 設計
- 契約與文件化
- Null 安全策略
技能要求：
- 必備技能：C# 方法設計
- 進階技能：防呆設計
延伸思考：
- 是否使用 Optional/Result 型別更清晰？
- C# 可空性註解（nullable reference types）？

Practice Exercise（練習題）
基礎練習：加 TryGetCell 並替換內部呼叫。
進階練習：對 FindNeighbors 完整移除 null 分支。
專案練習：在公共 API 加 nullable 註解與分析。

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有呼叫點相容。
- 程式碼品質（30%）：API 清晰、文件完備。
- 效能優化（20%）：無顯著額外成本。
- 創新性（10%）：引入 Result 型別。

---

## Case #13: 非阻塞更新迴圈（Timer/事件）替代 Thread.Sleep

### Problem Statement（問題陳述）
業務場景：主程式以 Thread.Sleep 控制節奏，導致 UI 無回應、難以暫停/恢復或調整速度。希望更好的控制與響應性。
技術挑戰：引入計時器與事件驅動，管理開始/暫停/速度。
影響範圍：使用者體驗、可擴展性（與 UI 整合）。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Sleep 阻塞主緒。
2. 無事件或命令模型。
3. 速度調整需改碼。
深層原因：
- 架構層面：缺少控制層（Controller）。
- 技術層面：未用 Timer/事件。
- 流程層面：僅為快速示範而非產品化。

### Solution Design（解決方案設計）
解決策略：使用 System.Timers.Timer 或 DispatcherTimer（WPF），透過事件驅動呼叫 Step 與 Render；加入開始/暫停/調速 API。

實施步驟：
1. 建立 SimulationController
- 實作細節：Start/Stop/SetInterval/OnTick。
- 所需資源：Timer
- 預估時間：1 小時
2. 整合渲染器
- 實作細節：Tick 時先 Step 再 Render，量測時間。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class SimulationController {
  private readonly Timer _timer = new Timer();
  private readonly World _world; private readonly IWorldRenderer _renderer;
  public SimulationController(World w, IWorldRenderer r, double intervalMs=200) {
    _world=w; _renderer=r; _timer.Interval=intervalMs; _timer.Elapsed += (_,__) => Tick();
  }
  public void Start()=>_timer.Start(); public void Stop()=>_timer.Stop();
  public void SetInterval(double ms)=>_timer.Interval=ms;
  private void Tick(){ _world.Step(); _renderer.Draw(_world, $"Gen: {_world.Generation}"); }
}
```

實際案例：可在運行中調整速度與暫停。
實作環境：C#/.NET。
實測數據：
改善前：UI 無響應、僅固定節奏。
改善後：可互動控制，使用體驗提升。
改善幅度：可用性顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- 事件驅動架構
- 計時器與執行緒注意事項
- 控制器分層
技能要求：
- 必備技能：.NET 計時器
- 進階技能：執行緒安全（UI 執行緒）
延伸思考：
- 與 WPF Dispatcher 整合？
- 非同步取消（CancellationToken）？

Practice Exercise（練習題）
基礎練習：用 Timer 替代 Sleep。
進階練習：加入開始/暫停/調速命令。
專案練習：做一個簡易 WinForms UI 控制面板。

Assessment Criteria（評估標準）
- 功能完整性（40%）：開始/暫停/調速可用。
- 程式碼品質（30%）：控制層抽象清晰。
- 效能優化（20%）：Tick 穩定、無累積延遲。
- 創新性（10%）：UI 整合友好。

---

## Case #14: 平行化計算（Parallel.For 與雙緩衝）

### Problem Statement（問題陳述）
業務場景：在大網格較慢，想利用多核心加速。需確保並行安全與結果正確。
技術挑戰：避免資料競爭，確保同代一致，衡量分割與快取友善。
影響範圍：效能、可擴展性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單執行緒逐格計算。
2. 計算彼此獨立可並行。
3. 若無雙緩衝會互相污染。
深層原因：
- 架構層面：需雙緩衝與純讀來源。
- 技術層面：分塊與快取局部性設計。
- 流程層面：缺乏性能基準。

### Solution Design（解決方案設計）
解決策略：採用世界層 bool[,] 雙緩衝（Case #11），以 Parallel.For 依列或依塊分割運算，寫入 back 緩衝，最後交換。

實施步驟：
1. 雙緩衝重構（若尚未）
- 實作細節：front/back 陣列。
- 所需資源：無
- 預估時間：2 小時
2. 平行化 Step
- 實作細節：Parallel.For(0, Y, y => for x... )。
- 所需資源：TPL
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
Parallel.For(0, Y, y => {
  for (int x=0; x<X; x++) {
    int n = CountNeighbors(front, x, y);
    bool live = front[x,y];
    back[x,y] = (live && (n==2||n==3)) || (!live && n==3);
  }
});
Swap(ref front, ref back);
```

實際案例：在 1000x1000 下明顯加速（視硬體而定）。
實作環境：C#/.NET TPL。
實測數據：
改善前：單執行緒 CPU 利用率低。
改善後：多核心利用、世代耗時降低。
改善幅度：依核心數呈比例提升（定性）。

Learning Points（學習要點）
核心知識點：
- 資料平行（data parallelism）
- 緩衝不可變來源
- 快取友善（列主序/塊處理）
技能要求：
- 必備技能：TPL、Parallel.For
- 進階技能：性能剖析與分塊策略
延伸思考：
- Partitioners 自訂分塊？
- SIMD/向量化與平行結合？

Practice Exercise（練習題）
基礎練習：以 Parallel.For 平行列。
進階練習：實作分塊（tile）以提升快取命中。
專案練習：比較單執行緒/平行/分塊的 Benchmark。

Assessment Criteria（評估標準）
- 功能完整性（40%）：結果與單執行緒一致。
- 程式碼品質（30%）：無競態、結構清晰。
- 效能優化（20%）：可展示加速比。
- 創新性（10%）：分塊/向量化。

---

## Case #15: 將規則抽象為策略（IRuleSet）以支援變體

### Problem Statement（問題陳述）
業務場景：文章提到「下回把題目做點變化」，意味未來規則可能變動（HighLife、Seeds 等）。目前規則寫死在 Cell，擴充性差。
技術挑戰：以可插拔策略支援不同規則，不影響核心資料結構與渲染。
影響範圍：擴展性、可測試性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 規則 if/else 寫死於 Cell。
2. 難以在運行中切換規則。
3. 測試不同規則需分支大量。
深層原因：
- 架構層面：缺少策略抽象。
- 技術層面：未將規則與狀態分離。
- 流程層面：難以做實驗比較。

### Solution Design（解決方案設計）
解決策略：定義 IRuleSet，輸入當前狀態與鄰居活數，輸出下一代狀態；World 注入規則；可於執行時更換。

實施步驟：
1. 定義介面與經典規則實作
- 實作細節：IRuleSet.Next(bool isAlive, int neighbors)
- 所需資源：無
- 預估時間：1 小時
2. 注入並使用策略
- 實作細節：Step 使用規則計算下一代。
- 所需資源：無
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public interface IRuleSet { bool Next(bool isAlive, int neighbors); }
public class ClassicRule : IRuleSet {
  public bool Next(bool a, int n) => (a && (n==2||n==3)) || (!a && n==3);
}
public class HighLifeRule : IRuleSet {
  public bool Next(bool a, int n) => (a && (n==2||n==3)) || (!a && (n==3||n==6));
}
```

實際案例：運行中切換 Classic/HighLife 規則觀察差異。
實作環境：C#/.NET。
實測數據：
改善前：規則不可換。
改善後：可插拔規則、快速實驗。
改善幅度：擴充性大幅提升（定性）。

Learning Points（學習要點）
核心知識點：
- 策略模式與依賴注入
- 可插拔演算法設計
- 測試與比較不同策略
技能要求：
- 必備技能：介面與抽象
- 進階技能：動態切換策略
延伸思考：
- 規則語法（如 B3/S23）解析器？
- 結合參數掃描（grid search）？

Practice Exercise（練習題）
基礎練習：實作 ClassicRule 與 HighLife。
進階練習：支援 B/S 字串規則解析。
專案練習：做規則選單與即時切換。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可切換規則且正確。
- 程式碼品質（30%）：規則與資料分離。
- 效能優化（20%）：策略抽象開銷可忽略。
- 創新性（10%）：規則 DSL/解析。

---

## Case #16: 初始狀態控制（隨機 seed 與圖樣載入）

### Problem Statement（問題陳述）
業務場景：目前初始化完全隨機且 seed 未控制，無法重現實驗；也無法載入固定圖樣（glider、gosper gun）。需要初始化策略。
技術挑戰：提供可重現的隨機初始化與從檔案/字串載入圖樣。
影響範圍：可重現性、教學展示。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. static Random 無 seed 輸入。
2. 無圖樣載入功能。
3. 測試與展示不方便。
深層原因：
- 架構層面：初始化策略寫死在 Cell。
- 技術層面：缺乏載入器。
- 流程層面：快速示範未考慮重現。

### Solution Design（解決方案設計）
解決策略：引入 IInitializer 策略（RandomInitializer、PatternInitializer）；World 於建構時採用策略初始化。

實施步驟：
1. 定義初始化介面與實作
- 實作細節：void Init(World w)
- 所需資源：無
- 預估時間：1 小時
2. 支援 seed 與檔案
- 實作細節：Random(seed)、載入 RLE/簡化文字格式。
- 所需資源：檔案 IO
- 預估時間：1-2 小時

關鍵程式碼/設定：
```csharp
public interface IInitializer { void Init(World w); }
public class RandomInitializer : IInitializer {
  private readonly Random _rnd; private readonly double _p;
  public RandomInitializer(int seed, double p){ _rnd=new Random(seed); _p=p; }
  public void Init(World w){ for(...){ w.SetAlive(x,y,_rnd.NextDouble()<_p); } }
}
```

實際案例：以固定 seed 重現隨機實驗；載入 glider 從檔案。
實作環境：C#/.NET。
實測數據：
改善前：不可重現、無法自訂初態。
改善後：可重現且可載入特定圖樣。
改善幅度：教學與測試便利性大增（定性）。

Learning Points（學習要點）
核心知識點：
- 策略模式在初始化場景
- 檔案格式與解析
- 可重現性設計
技能要求：
- 必備技能：Random/IO
- 進階技能：格式設計/解析
延伸思考：
- 支援 Life RLE 完整規格？
- 多圖樣合併與定位？

Practice Exercise（練習題）
基礎練習：RandomInitializer(seed)。
進階練習：簡單文字圖樣載入（#/.）。
專案練習：RLE 解析與放置偏移/鏡射。

Assessment Criteria（評估標準）
- 功能完整性（40%）：隨機與圖樣皆可。
- 程式碼品質（30%）：抽象清晰。
- 效能優化（20%）：初始化快速。
- 創新性（10%）：支援更多格式。

---

## Case #17: 斷言與防呆（PutOn/座標驗證/未定義狀態）

### Problem Statement（問題陳述）
業務場景：程式中多處存在潛在未定義分支（else 註解 ToDo），與 PutOn 重複放置拋例外但訊息不夠清楚。需要強化防呆與診斷訊息。
技術挑戰：在不影響效能與釋出版的前提下，加強 Debug 支援。
影響範圍：偵錯效率、穩定性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. else 分支未處理或未 Assert。
2. ArgumentException 無描述。
3. 缺少參數驗證訊息。
深層原因：
- 架構層面：缺少診斷與契約。
- 技術層面：未使用 Debug.Assert/ArgumentException(message)。
- 流程層面：未建立錯誤處理標準。

### Solution Design（解決方案設計）
解決策略：加入參數驗證與 Debug.Assert；將未定義分支明確處理；例外訊息包含座標與狀態。

實施步驟：
1. PutOn 與建構式驗證
- 實作細節：詳細訊息與座標。
- 所需資源：無
- 預估時間：0.5 小時
2. 未定義分支處理
- 實作細節：在 Debug 模式 Assert；Release 記錄警告。
- 所需資源：TraceSource（選用）
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
internal void PutOn(Cell item, int x, int y) {
  if (_map[x,y] != null)
    throw new ArgumentException($"Cell already exists at ({x},{y}).");
  _map[x,y] = item;
}

public void ComputeNextState() {
  // ... 各分支
#if DEBUG
  else { System.Diagnostics.Debug.Assert(false, "Unreachable state"); NextIsAlive = IsAlive; }
#else
  else { NextIsAlive = IsAlive; }
#endif
}
```

實際案例：異常報告精準定位問題。
實作環境：C#/.NET。
實測數據：
改善前：錯誤難追蹤。
改善後：定位迅速、回歸更快。
改善幅度：除錯效率提升（定性）。

Learning Points（學習要點）
核心知識點：
- 契約式設計（Design by Contract）
- Debug vs Release 行為
- 例外訊息設計
技能要求：
- 必備技能：例外處理
- 進階技能：診斷與追蹤
延伸思考：
- 是否導入 Guard 套件？
- 以 Roslyn Analyzer 做靜態檢查？

Practice Exercise（練習題）
基礎練習：補上訊息化的例外。
進階練習：在關鍵分支加 Debug.Assert。
專案練習：導入 TraceSource/ILogger 做診斷。

Assessment Criteria（評估標準）
- 功能完整性（40%）：異常訊息可讀。
- 程式碼品質（30%）：防呆覆蓋充分。
- 效能優化（20%）：Release 無負擔。
- 創新性（10%）：診斷日誌策略。

---

## Case #18: 測試友好渲染（快照對比）

### Problem Statement（問題陳述）
業務場景：需要自動驗證某一代的「可視輸出」是否正確，但 ConsoleRenderer 難以比較。希望建立可快照化的渲染輸出以供測試。
技術挑戰：產出可比較的代表格式（字串/矩陣），與圖樣預期對比。
影響範圍：測試可靠性、教學驗證。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Console 無法直接擷取每格符號。
2. 渲染與資料混雜。
3. 無快照格式。
深層原因：
- 架構層面：渲染未抽象快照能力。
- 技術層面：無中間表示。
- 流程層面：缺乏端對端測試思維。

### Solution Design（解決方案設計）
解決策略：新增 SnapshotRenderer 將世界轉為 string[] 或 char[,]；單元測試直接比較快照。

實施步驟：
1. 新增 SnapshotRenderer
- 實作細節：將 World 轉為字元陣列（#/.）。
- 所需資源：無
- 預估時間：0.5 小時
2. 測試對比
- 實作細節：對比預期快照檔案或內嵌字串。
- 所需資源：xUnit
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class SnapshotRenderer : IWorldRenderer {
  public string[] Snapshot(World w) {
    var lines = new string[w.SizeY];
    for (int y=0;y<w.SizeY;y++) {
      var sb = new StringBuilder(w.SizeX);
      for (int x=0;x<w.SizeX;x++) sb.Append(w.GetCell(x,y).IsAlive ? '#' : '.');
      lines[y] = sb.ToString();
    }
    return lines;
  }
  public void Draw(World w, string title) { /* no-op for tests */ }
}
```

實際案例：對比 blinker 兩代快照。
實作環境：C#/.NET、xUnit。
實測數據：
改善前：難以自動斷言可視輸出。
改善後：可快照比較，測試穩定。
改善幅度：端對端測試可行（定性）。

Learning Points（學習要點）
核心知識點：
- 渲染中間表示
- 快照測試
- 可視結果自動驗證
技能要求：
- 必備技能：字串處理
- 進階技能：測試資產管理
延伸思考：
- 快照格式版本化？
- 差異高亮顯示？

Practice Exercise（練習題）
基礎練習：輸出字串快照。
進階練習：讀取預期檔案做對比。
專案練習：建立多規則/邊界的快照庫。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可產出快照。
- 程式碼品質（30%）：渲染與快照分離。
- 效能優化（20%）：快照生成快速。
- 創新性（10%）：差異視覺化。

---

案例分類
1) 按難度分類
- 入門級（適合初學者）
  - Case #1 OOP 架構（World/Cell）
  - Case #3 座標指派修正
  - Case #7 參數化初始化
  - Case #12 安全 API（TryGetCell）
- 中級（需要一定基礎）
  - Case #2 雙緩衝更新正確性
  - Case #4 鄰居快取
  - Case #5 渲染與邏輯分離
  - Case #6 增量渲染與防閃爍
  - Case #8 邊界策略
  - Case #9 規則單元測試
  - Case #10 指標與觀測
  - Case #13 非阻塞更新迴圈
  - Case #18 測試友好渲染
- 高級（需要深厚經驗）
  - Case #11 資料結構重構（bool[,] / BitArray）
  - Case #14 平行化計算
  - Case #15 規則策略化（IRuleSet）

2) 按技術領域分類
- 架構設計類：#1, #5, #8, #11, #15, #13
- 效能優化類：#4, #6, #10, #11, #14
- 整合開發類：#7, #13, #16, #18
- 除錯診斷類：#2, #3, #9, #12, #17
- 安全防護類：#12, #17（API 安全/防呆）

3) 按學習目標分類
- 概念理解型：#1, #5, #15
- 技能練習型：#3, #7, #12, #18
- 問題解決型：#2, #4, #6, #8, #9, #10, #13, #17
- 創新應用型：#11, #14, #16

案例關聯圖（學習路徑建議）
- 建議起點：
  - 先學 Case #1（OOP 架構），理解 World/Cell 職責。
  - 接著 Case #3（座標修正）、Case #12（安全 API），建立穩健基礎。
  - 引入 Case #7（參數化）與 Case #16（初始化策略），提升可用性與可重現性。
- 正確性與測試：
  - 學習 Case #2（雙緩衝），確保規則正確。
  - 立刻配合 Case #9（單元測試）與 Case #18（快照對比）建立回歸防線。
- 架構擴展與 UI：
  - 進入 Case #5（渲染分離）、Case #6（增量渲染），打造可替換的呈現層。
  - 補上 Case #10（指標）做量化觀測。
  - 用 Case #13（非阻塞控制）改善互動性。
- 進階效能與伸縮：
  - 先做 Case #4（鄰居快取）與 Case #8（邊界策略）以驗證抽象能力。
  - 重構為 Case #11（陣列雙緩衝）作為大規模基礎。
  - 最後上 Case #14（平行化）提升吞吐。
- 變體與創新：
  - 以 Case #15（IRuleSet）支援規則變體，配合 #16 做多圖樣實驗。
  - 穩定後加入 Case #17（斷言/防呆）全域提升診斷能力。

依賴關係提示：
- #2 依賴 #1；#9 依賴 #2/#16；#14 強依賴 #11/#2；#15 建議先完成 #5/#1；#6 建議配合 #5；#18 可在 #5 基礎上實作。

完整學習路徑：
#1 → (#3, #12) → (#7, #16) → #2 → (#9, #18) → (#5, #6) → #10 → #13 → (#4, #8) → #11 → #14 → #15 → #17

以上 15 個案例均以文中程式與設計為基礎，涵蓋從正確性、架構、效能、測試到擴展的完整實戰路徑，可用於教學、實作與評估。