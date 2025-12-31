---
layout: synthesis
title: "Paint.NET 2.0"
synthesis_type: solution
source_post: /2004/12/22/paint-net-2-0/
redirect_from:
  - /2004/12/22/paint-net-2-0/solution/
postid: 2004-12-22-paint-net-2-0
---

以下內容基於文章所提到的關鍵功能與設計取向（外掛架構、指令歷史、圖層、工具視窗半透明、濾鏡、套索/噴槍/滴管工具、完整原始碼可學習）進行教學化的案例萃取與設計。原文未提供量化效益與具體數據，本文以工程實作與質性效益為主，並在「實測數據」處明確標註「文章未提供」。

## Case #1: 浮動工具視窗遮擋畫布的半透明化設計

### Problem Statement（問題陳述）
- 業務場景：影像編修過程中，使用者常需放大照片做細部修飾；然而浮動工具視窗（工具列、層面板、屬性窗）在屏幕空間有限時易遮蔽畫布，導致視覺阻擋、頻繁移動視窗、操作斷點增加，降低效率與體驗。
- 技術挑戰：在多浮動窗體環境下，如何在不影響功能可達性的前提下降低遮擋面積，且不引入卡頓與閃爍。
- 影響範圍：UI/UX、使用效率、視覺流暢性、可訪問性。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 浮動窗體始終不透明，遮蔽畫布區域。
  2. 視窗焦點切換時無對應視覺狀態切換策略。
  3. 小螢幕/高DPI放大倍率時遮擋效應更顯著。
- 深層原因：
  - 架構層面：UI層缺乏視窗狀態管理（Active/Inactive）及視覺層級策略。
  - 技術層面：未使用窗體不透明度、穿透或自動折疊等技術。
  - 流程層面：UI可用性測試不足，未針對高倍率工作流做驗證。

### Solution Design（解決方案設計）
- 解決策略：在浮動工具視窗失焦（Deactivated）時自動切換半透明（降低不透明度），獲得焦點（Activated）恢復全不透明，兼顧可視性與不遮擋畫布；必要時加入自動暫時穿透或邊緣貼齊。
- 實施步驟：
  1. 視窗狀態偵測
     - 實作細節：訂閱 Activated/Deactivate 事件，切換 Opacity。
     - 所需資源：WinForms/WPF 事件系統
     - 預估時間：0.5 天
  2. 視覺參數與使用者偏好
     - 實作細節：加入偏好設定（透明度百分比、動畫時長、是否穿透滑鼠）。
     - 所需資源：設定存取（user.config）、UI 選單
     - 預估時間：0.5 天
  3. 邊界情境測試
     - 實作細節：高DPI、雙螢幕、工具視窗重疊測試。
     - 所需資源：測試環境
     - 預估時間：0.5 天
- 關鍵程式碼/設定：
```csharp
// WinForms: 浮動工具視窗在失焦時半透明
public partial class ToolWindow : Form
{
    private double inactiveOpacity = 0.6; // 可在偏好設定中調整
    private double activeOpacity = 1.0;

    public ToolWindow()
    {
        InitializeComponent();
        this.Activated += (_, __) => this.Opacity = activeOpacity;
        this.Deactivate += (_, __) => this.Opacity = inactiveOpacity;
        // 可選：避免閃爍
        this.DoubleBuffered = true;
    }
}
```
- 實際案例：文章提到「這些浮動的工具視窗在沒取得 focus 時，會切換到半透明模式」；此案例即為該功能的工程化拆解。
- 實作環境：C#、WinForms（.NET 6+ 或 .NET Framework 均可）
- 實測數據：
  - 改善前：畫布被工具視窗遮擋，需頻繁移動視窗（文章未提供量化）
  - 改善後：失焦工具視窗半透明，畫布可視性提升（質性描述）
  - 改善幅度：文章未提供

- Learning Points（學習要點）
  - 核心知識點：
    - 視窗焦點事件與狀態管理
    - WinForms/WPF 透明度與重繪
    - 使用者偏好與可用性
  - 技能要求：
    - 必備技能：WinForms 事件、基礎 UI 程式設計
    - 進階技能：高DPI/雙螢幕相容性處理、動畫化
  - 延伸思考：
    - 可應用於 IDE、影音編輯器的浮動面板
    - 潛在風險：透明度過低導致可讀性下降
    - 進一步優化：加入滑鼠懸停自動「實體化」

- Practice Exercise（練習題）
  - 基礎練習：製作一個浮動窗體，失焦變 60% 透明，獲焦恢復（30 分鐘）
  - 進階練習：加入滑鼠停留全不透明、離開漸變透明（2 小時）
  - 專案練習：多工具窗體管理器（可設定透明度、動畫、停駐位置）（8 小時）

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：失焦透明、獲焦恢復、使用者可設定
  - 程式碼品質（30%）：事件管理乾淨、避免閃爍
  - 效能優化（20%）：重繪平滑、低延遲
  - 創新性（10%）：穿透點擊、智慧停駐

---

## Case #2: 可擴充特效外掛（Plugin）架構設計

### Problem Statement（問題陳述）
- 業務場景：影像處理產品迭代快速、特效需求多變；官方團隊無法涵蓋所有特效與濾鏡，需讓社群或第三方擴充。
- 技術挑戰：如何設計穩定、版本相容、易發佈與易安裝的外掛機制，支援參數化與預覽。
- 影響範圍：產品可擴充性、生態圈、維護成本。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 需求多樣且變動快，官方內建難以全面覆蓋。
  2. 特效演算法各異，需模組化與隔離。
  3. 版本演進需避免破壞相容性。
- 深層原因：
  - 架構層面：缺乏穩定的介面契約與載入/隔離策略。
  - 技術層面：組件探索、反射載入、依賴管理。
  - 流程層面：外掛發佈與驗證流程不明確。

### Solution Design（解決方案設計）
- 解決策略：定義精簡穩定的 IEffect 介面（名稱、套用、參數），以反射動態載入外掛 DLL；提供外掛目錄、簽章與版本策略；支持參數化與預覽回呼。
- 實施步驟：
  1. 介面契約設計
     - 實作細節：定義 IEffect/IEffectWithConfig；分離介面到獨立契約組件。
     - 所需資源：C#、Strong-naming（可選）
     - 預估時間：1 天
  2. 掃描與載入
     - 實作細節：掃描「Effects」資料夾，Assembly.LoadFrom + Type 篩選 + new()。
     - 所需資源：檔案系統、反射
     - 預估時間：1 天
  3. 執行與錯誤防護
     - 實作細節：例外處理、逾時/取消、UI 隔離，必要時 AppDomain（.NET Framework）或獨立進程。
     - 所需資源：Task、CancellationToken
     - 預估時間：1-2 天
- 關鍵程式碼/設定：
```csharp
public interface IEffect
{
    string Name { get; }
    Bitmap Apply(Bitmap input, IDictionary<string, object>? parameters);
}

public interface IConfigurableEffect : IEffect
{
    Control CreateConfigUI(IDictionary<string, object> parameters);
}

// 掃描載入
var effects = new List<IEffect>();
foreach (var file in Directory.GetFiles("Effects", "*.dll"))
{
    var asm = Assembly.LoadFrom(file);
    var types = asm.GetTypes()
                   .Where(t => typeof(IEffect).IsAssignableFrom(t) && !t.IsAbstract);
    foreach (var t in types)
        if (Activator.CreateInstance(t) is IEffect eff) effects.Add(eff);
}
```
- 實際案例：文章指出「設計支援特效外掛」；本案例將其落地為契約與載入流程。
- 實作環境：C#、WinForms/WPF、.NET 6+ 或 .NET Framework
- 實測數據：
  - 改善前：內建特效固定、擴充困難（文章未提供量化）
  - 改善後：以 DLL 擴充特效、免改核心程式（質性描述）
  - 改善幅度：文章未提供

- Learning Points
  - 核心知識點：組件設計、反射、版本相容
  - 技能要求：C# 反射、介面設計、例外處理
  - 延伸思考：插件沙箱、權限限制、跨進程隔離

- Practice Exercise
  - 基礎：撰寫一個「反相」特效外掛（30 分鐘）
  - 進階：加入參數 UI（強度滑桿）、即時預覽（2 小時）
  - 專案：完成外掛管理器（安裝/啟用/停用/排序）（8 小時）

- Assessment Criteria
  - 功能完整性（40%）：掃描、載入、執行、參數化
  - 程式碼品質（30%）：契約穩定、錯誤處理
  - 效能優化（20%）：載入快、執行效率
  - 創新性（10%）：外掛隔離/安全策略

---

## Case #3: 命令歷史（Undo/Redo）與非破壞式回溯

### Problem Statement
- 業務場景：影像編修常需反覆嘗試效果，若無 Undo/Redo，錯誤代價高、學習成本大。
- 技術挑戰：如何在保證效能與記憶體可控的情況下，提供穩定的多步撤銷/重做機制。
- 影響範圍：使用體驗、資料完整性、記憶體/磁碟消耗。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 編輯操作具破壞性，覆蓋原始像素。
  2. 操作不可逆，缺乏狀態保存。
  3. 大圖記憶體壓力高，快照成本大。
- 深層原因：
  - 架構層面：缺乏命令模式（Command）與狀態快照（Memento）。
  - 技術層面：沒有區域差異（Delta）儲存策略。
  - 流程層面：未定義操作粒度與合併策略。

### Solution Design
- 解決策略：實作命令模式，每個操作實作 Execute/Undo；搭配差異快照（區塊級或選區級）儲存；支援步驟合併（例如連續畫筆動作）。
- 實施步驟：
  1. 命令介面與堆疊
     - 實作細節：ICommand、undo/redo stack、描述字串。
     - 資源：C# 基礎
     - 時間：1 天
  2. 差異快照
     - 實作細節：僅保存影響區塊 bitmap 片段與座標。
     - 資源：Bitmap/LockBits
     - 時間：1-2 天
  3. 粒度控制與合併
     - 實作細節：短時間多筆畫合併為一命令。
     - 資源：計時器、輸入緩衝
     - 時間：0.5 天
- 關鍵程式碼/設定：
```csharp
public interface ICommand
{
    string Description { get; }
    void Execute();
    void Undo();
}

public class DrawStrokeCommand : ICommand
{
    private readonly Bitmap canvas;
    private readonly List<Point> points;
    private Rectangle affected;
    private Bitmap? before;

    public string Description => "Draw Stroke";

    public DrawStrokeCommand(Bitmap canvas, List<Point> points)
    {
        this.canvas = canvas; this.points = points;
    }

    public void Execute()
    {
        affected = ComputeBounds(points);
        before = canvas.Clone(affected, canvas.PixelFormat); // delta snapshot
        using var g = Graphics.FromImage(canvas);
        // ... render stroke ...
    }

    public void Undo()
    {
        if (before != null)
        {
            using var g = Graphics.FromImage(canvas);
            g.DrawImageUnscaled(before, affected.Location);
        }
    }
}
```
- 實際案例：文章提及「command history」；此案例將其工程化。
- 實作環境：C#、WinForms、.NET 6+/Framework
- 實測數據：文章未提供（質性：支援撤銷/重做提升容錯）

- Learning Points：Command/Memento、差異快照、操作合併
- 技能要求：GDI+ 繪圖、記憶體管理
- 延伸思考：磁碟換頁、歷史容量限制、跨文件回溯

- Practice：基礎（單步撤銷）、進階（差異快照）、專案（完整歷史管理器）
- Assessment：完整性（多步與合併）、品質（記憶體釋放）、效能（大圖不卡）、創新（可視化歷史）

---

## Case #4: 圖層（Layer）管理與非破壞式合成

### Problem Statement
- 業務場景：影像編修需分離元素（文字、形狀、修飾），避免互相覆蓋。
- 技術挑戰：多層合成、透明度、混合模式、可視性切換與效能。
- 影響範圍：靈活性、可維護性、效能、檔案大小。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 單一畫布破壞式編輯，難以微調。
  2. 合成需求多（透明度/模式）。
  3. 線上預覽與最終輸出的差異控制。
- 深層原因：
  - 架構層面：缺少文件-圖層-視圖分離。
  - 技術層面：Alpha 混合、合成順序、Dirty Region。
  - 流程層面：缺少圖層命名、群組與鎖定規則。

### Solution Design
- 解決策略：設計 Document -> List<Layer>；Layer 持有 Bitmap、Opacity、BlendMode、Visible；合成時使用 SourceOver；Dirty Region 局部重繪。
- 實施步驟：
  1. 模型設計
     - 細節：Layer 類別、文件結構、屬性（Visible、Locked、Opacity）。
     - 資源：C#
     - 時間：1 天
  2. 合成與重繪
     - 細節：自上而下合成至顯示緩衝；Dirty Rectangle。
     - 資源：Graphics、CompositingMode
     - 時間：1-2 天
  3. UI 與互動
     - 細節：圖層面板、拖拽排序、眼睛圖示切換。
     - 資源：WinForms/WPF UI
     - 時間：1 天
- 關鍵程式碼/設定：
```csharp
public class Layer
{
    public Bitmap Bitmap { get; set; }
    public float Opacity { get; set; } = 1f;
    public bool Visible { get; set; } = true;
}

public Bitmap Compose(IEnumerable<Layer> layers, Size size)
{
    var result = new Bitmap(size.Width, size.Height, PixelFormat.Format32bppArgb);
    using var g = Graphics.FromImage(result);
    g.CompositingMode = CompositingMode.SourceOver;
    foreach (var layer in layers.Where(l => l.Visible))
    {
        var cm = new ColorMatrix { Matrix33 = layer.Opacity };
        using var ia = new ImageAttributes();
        ia.SetColorMatrix(cm);
        g.DrawImage(layer.Bitmap, 
            new Rectangle(0,0,size.Width,size.Height),
            0,0,layer.Bitmap.Width, layer.Bitmap.Height,
            GraphicsUnit.Pixel, ia);
    }
    return result;
}
```
- 實際案例：文章提到「layer」功能；此為工程實現。
- 實作環境：C#、GDI+、WinForms/WPF
- 實測數據：文章未提供

- Learning Points：Layer 模型、Alpha 合成、Dirty Region
- 技能要求：GDI+、顏色矩陣、UI 模型
- 延伸思考：混合模式擴展、圖層群組、調整圖層（Adjustment Layer）

- Practice：基礎（兩層合成）、進階（Opacity/可視性）、專案（圖層面板）
- Assessment：完整性（增刪改查/排序）、品質（重繪效率）、效能（大圖不卡）、創新（調整圖層）

---

## Case #5: 套索（Lasso）選取工具與選區遮罩

### Problem Statement
- 業務場景：使用者需精確選取不規則區域以套用局部特效或操作。
- 技術挑戰：高精度邊界、滑順繪製、HitTest、轉遮罩與反選、效能。
- 影響範圍：局部編修能力、特效精準度、使用體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 不規則邊界難以以矩形描述。
  2. 多段點擊與平滑處理需求。
  3. 選區需轉成遮罩以限制特效範圍。
- 深層原因：
  - 架構層面：缺乏統一的選區資料結構。
  - 技術層面：GraphicsPath、Region 與遮罩轉換。
  - 流程層面：多工具共享選區狀態管理。

### Solution Design
- 解決策略：以點集建立 GraphicsPath，轉 Region 與二值遮罩；提供反選、羽化（feather）與擴張/侵蝕；同步顯示虛線螢光（marching ants）。
- 實施步驟：
  1. 幾何與遮罩
     - 細節：點集 -> GraphicsPath -> Region；Region -> Mask（Bitmap）。
     - 資源：GDI+、System.Drawing.Drawing2D
     - 時間：1 天
  2. 視覺化與互動
     - 細節：虛線動畫、滑鼠事件、鍵盤完成/取消。
     - 資源：Timer、Paint 事件
     - 時間：1 天
- 關鍵程式碼/設定：
```csharp
List<Point> points = new();
GraphicsPath path = new();

void OnMouseDown(Point p) { points.Add(p); }
void OnMouseMove(Point p) { if (isDrawing) { points.Add(p); Invalidate(); } }
void OnPaint(object sender, PaintEventArgs e)
{
    if (points.Count > 1)
    {
        using var pen = new Pen(Color.White, 1) { DashStyle = DashStyle.Dash };
        e.Graphics.DrawLines(pen, points.ToArray());
    }
}

Region ToRegion()
{
    path.Reset();
    if (points.Count > 2) path.AddPolygon(points.ToArray());
    return new Region(path);
}
```
- 實際案例：文章列出「套索」工具；此為工程落地。
- 實作環境：C#、WinForms、GDI+
- 實測數據：文章未提供

- Learning Points：選區資料結構、Region/Mask、UI 互動
- 技能要求：事件驅動、幾何圖形、GDI+ API
- 延伸思考：羽化/擴張、智慧選取（邊緣偵測）

- Practice：基礎（多邊形選取）、進階（轉遮罩/反選）、專案（羽化與預覽）
- Assessment：完整性（新增/完成/取消）、品質（邊界平滑）、效能、創新（智慧選取）

---

## Case #6: 噴槍（Airbrush）工具的粒子分佈與流量控制

### Problem Statement
- 業務場景：模擬噴漆效果，用於柔和上色或局部修飾。
- 技術挑戰：粒子隨機分佈、壓力/流量控制、疊加與透明度、效能。
- 影響範圍：繪畫質感、工具表現力、CPU 負載。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 噴灑需持續性、隨機性。
  2. 疊加須符合 Alpha 混合。
  3. 高頻率繪製易造成效能瓶頸。
- 深層原因：
  - 架構層面：工具執行緒/計時器模型。
  - 技術層面：隨機分佈、筆刷材質、Alpha blending。
  - 流程層面：與 Undo/Redo 合併策略。

### Solution Design
- 解決策略：用 Timer/CompositionTarget 驅動持續噴灑；高斯分佈或圓形均勻分佈粒子；批次繪製降低重繪次數；壓力->粒子密度與Alpha。
- 實施步驟：
  1. 計時與分佈
     - 細節：每 tick 產生 N 個粒子，半徑與強度可參數化。
     - 資源：Timer、Random
     - 時間：1 天
  2. 批次渲染
     - 細節：離屏緩衝（Bitmap）合併到圖層，減少閃爍。
     - 資源：Graphics、Double Buffer
     - 時間：1 天
- 關鍵程式碼/設定：
```csharp
Timer sprayTimer = new() { Interval = 16 };
Random rng = new();
int radius = 20; int density = 100; Color color = Color.FromArgb(20, 255, 0, 0);

sprayTimer.Tick += (_, __) =>
{
    using var g = Graphics.FromImage(activeLayer.Bitmap);
    for (int i=0; i<density; i++)
    {
        var angle = rng.NextDouble() * Math.PI * 2;
        var r = rng.NextDouble() * radius;
        int x = cursor.X + (int)(Math.Cos(angle) * r);
        int y = cursor.Y + (int)(Math.Sin(angle) * r);
        using var b = new SolidBrush(color);
        g.FillRectangle(b, x, y, 1, 1);
    }
    Invalidate(new Rectangle(cursor.X-radius, cursor.Y-radius, radius*2, radius*2));
};
```
- 實際案例：文章列出「噴槍」工具。
- 實作環境：C#、WinForms/GDI+
- 實測數據：文章未提供

- Learning Points：隨機分佈、Alpha 疊加、批次渲染
- 技能要求：計時器、GDI+、效能思維
- 延伸思考：筆刷形狀紋理、壓力筆支援

- Practice：基礎（圓形分佈噴灑）、進階（高斯分佈/壓力調整）、專案（筆刷系統）
- Assessment：完整性（持續噴灑/停止）、品質（平滑度）、效能（60 FPS）、創新（筆刷引擎）

---

## Case #7: 滴管（Eyedropper）顏色取樣與 UI 同步

### Problem Statement
- 業務場景：從畫布任意位置快速取色以持續繪製或設定前景/背景色。
- 技術挑戰：跨圖層合成取色、單像素/平均取樣、效能與準確性。
- 影響範圍：繪製效率、一致性、工具聯動。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 畫面顯示為合成後結果，需對 composed buffer 取樣。
  2. 單像素取樣對雜訊敏感，需可選平均取樣。
  3. 高 DPI/縮放需正確對映座標。
- 深層原因：
  - 架構層面：渲染與資料模型分離。
  - 技術層面：畫面緩衝存取、縮放座標轉換。
  - 流程層面：與色盤/筆刷狀態同步。

### Solution Design
- 解決策略：以顯示緩衝（合成結果）為取樣來源；支援 NxN 取樣平均；更新全域前景/背景色狀態與 UI；支援鍵盤切換模式。
- 實施步驟：
  1. 取樣來源
     - 細節：維護合成後 Bitmap 緩衝；滑鼠座標轉換至畫布坐標。
     - 資源：Render Buffer
     - 時間：0.5 天
  2. 平均取樣
     - 細節：可選 3x3/5x5 box filter 作為平均。
     - 資源：LockBits
     - 時間：0.5 天
- 關鍵程式碼/設定：
```csharp
Color Sample(Bitmap composed, Point canvasPt, int kernel = 1)
{
    int r=0,g=0,b=0,count=0;
    for (int dy=-kernel; dy<=kernel; dy++)
    for (int dx=-kernel; dx<=kernel; dx++)
    {
        int x = Math.Clamp(canvasPt.X + dx, 0, composed.Width-1);
        int y = Math.Clamp(canvasPt.Y + dy, 0, composed.Height-1);
        var c = composed.GetPixel(x,y);
        r += c.R; g += c.G; b += c.B; count++;
    }
    return Color.FromArgb(r/count, g/count, b/count);
}
```
- 實際案例：文章列出「滴管」工具。
- 實作環境：C#、WinForms
- 實測數據：文章未提供

- Learning Points：緩衝取樣、縮放對映、工具狀態同步
- 技能要求：事件處理、色彩處理
- 延伸思考：HDR/線性空間取樣、ICC 色彩管理

- Practice：基礎（單像素取樣）、進階（3x3/5x5 平均）、專案（與色盤/筆刷聯動）
- Assessment：完整性（前景/背景切換）、品質（正確取樣）、效能、創新（快速取樣快捷鍵）

---

## Case #8: 濾鏡實作範例（灰階/模糊）

### Problem Statement
- 業務場景：需提供常見濾鏡（灰階、模糊）以滿足基本修圖需求，並可擴充。
- 技術挑戰：像素級處理效能、選區限制、參數化。
- 影響範圍：功能覆蓋度、效能、外掛擴充。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 濾鏡需快速處理大圖。
  2. 需支援選區範圍內套用。
  3. 支援參數（強度/半徑）。
- 深層原因：
  - 架構層面：濾鏡管線、選區遮罩。
  - 技術層面：LockBits/Span、卷積。
  - 流程層面：預覽與套用一致性。

### Solution Design
- 解決策略：以 IEffect 實作濾鏡；用 LockBits 處理像素；配合遮罩只處理選區；提供參數與預覽。
- 實施步驟：
  1. 灰階
     - 細節：Lum = 0.2126R+0.7152G+0.0722B。
     - 時間：0.5 天
  2. 盒狀模糊
     - 細節：簡化卷積，半徑可調。
     - 時間：1 天
- 關鍵程式碼/設定：
```csharp
public class GrayscaleEffect : IEffect
{
    public string Name => "Grayscale";
    public Bitmap Apply(Bitmap input, IDictionary<string, object>? parameters)
    {
        var bmp = new Bitmap(input.Width, input.Height, PixelFormat.Format32bppArgb);
        using var src = new Bitmap(input);
        var rect = new Rectangle(0,0,input.Width,input.Height);
        var dataSrc = src.LockBits(rect, ImageLockMode.ReadOnly, src.PixelFormat);
        var dataDst = bmp.LockBits(rect, ImageLockMode.WriteOnly, bmp.PixelFormat);
        unsafe
        {
            byte* pSrc = (byte*)dataSrc.Scan0;
            byte* pDst = (byte*)dataDst.Scan0;
            for (int y=0; y<input.Height; y++)
            {
                for (int x=0; x<input.Width; x++)
                {
                    byte b = pSrc[0], g = pSrc[1], r = pSrc[2], a = pSrc[3];
                    byte lum = (byte)(0.0722*b + 0.7152*g + 0.2126*r);
                    pDst[0]=lum; pDst[1]=lum; pDst[2]=lum; pDst[3]=a;
                    pSrc += 4; pDst += 4;
                }
                pSrc += dataSrc.Stride - input.Width*4;
                pDst += dataDst.Stride - input.Width*4;
            }
        }
        src.UnlockBits(dataSrc); bmp.UnlockBits(dataDst);
        return bmp;
    }
}
```
- 實際案例：文章提及「支援濾鏡」。
- 實作環境：C#、WinForms、Unsafe Code（可選）
- 實測數據：文章未提供

- Learning Points：像素處理、遮罩、卷積
- 技能要求：LockBits、unsafe、參數化 UI
- 延伸思考：多執行緒、SIMD 加速

- Practice：基礎（灰階特效）、進階（盒狀模糊）、專案（高斯模糊 + 預覽）
- Assessment：完整性（選區支援）、品質（邊緣處理）、效能、創新（多核）

---

## Case #9: 外掛參數 UI 與即時預覽流程

### Problem Statement
- 業務場景：使用者需在套用前調整特效參數（強度/半徑/阈值）並即時預覽。
- 技術挑戰：雙緩衝預覽、取消/套用一致性、UI-算法解耦。
- 影響範圍：易用性、準確性、效能。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 需要高互動參數調整。
  2. 預覽不可改變原圖層，需暫存。
  3. 需要取消/恢復。
- 深層原因：
  - 架構層面：插件 UI 與核心演算法解耦。
  - 技術層面：離屏渲染、節流/去抖。
  - 流程層面：Confirm/Cancel 與 Undo 整合。

### Solution Design
- 解決策略：IConfigurableEffect 提供 CreateConfigUI；核心提供 PreviewRenderer 接口；節流重算，OK/Cancel 更新/丟棄結果。
- 實施步驟：
  1. 參數 UI
     - 細節：TrackBar/TextBox 綁定；事件觸發預覽。
     - 時間：0.5 天
  2. 預覽渲染
     - 細節：Task.Run + Throttle；顯示在預覽面板。
     - 時間：1 天
- 關鍵程式碼/設定：
```csharp
public Control CreateConfigUI(IDictionary<string, object> parameters)
{
    var slider = new TrackBar { Minimum=0, Maximum=100, Value=50 };
    slider.ValueChanged += async (_, __) =>
    {
        parameters["strength"] = slider.Value;
        await previewService.RenderAsync(this, parameters); // 節流實作於 service
    };
    return slider;
}
```
- 實際案例：文章提到外掛與濾鏡；此為參數化與預覽的實作。
- 實作環境：C#、WinForms/WPF
- 實測數據：文章未提供

- Learning Points：插件 UI、即時預覽、節流
- 技能要求：事件、非同步、UI/核心解耦
- 延伸思考：區域預覽（只重算視窗範圍）、GPU 加速

- Practice：基礎（滑桿預覽）、進階（多參數）、專案（可重用預覽服務）
- Assessment：完整性（OK/Cancel）、品質（不卡頓）、效能（節流）、創新（區域預覽）

---

## Case #10: 外掛發現、排序與分類呈現

### Problem Statement
- 業務場景：外掛數量增多，需要可發現性、分類與排序，便於使用者快速找到特效。
- 技術挑戰：外掛中繼資料（分類/權重/版本）、本地化、衝突處理。
- 影響範圍：可用性、學習成本、維護。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 外掛多，清單雜亂。
  2. 缺乏分類與搜尋。
  3. 命名/重複衝突。
- 深層原因：
  - 架構層面：缺少標註（Attribute）與中繼資料索引。
  - 技術層面：反射讀取屬性與多語系資源。
  - 流程層面：外掛命名規範不一致。

### Solution Design
- 解決策略：定義 EffectMetadata Attribute（分類、排序、描述、資源鍵），載入時建索引；提供搜尋欄與分類樹。
- 實施步驟：
  1. 中繼資料
     - 細節：Attribute + ResourceManager（本地化）。
     - 時間：0.5 天
  2. 呈現與搜尋
     - 細節：TreeView/Filter，排序與去重策略。
     - 時間：1 天
- 關鍵程式碼/設定：
```csharp
[AttributeUsage(AttributeTargets.Class)]
public class EffectMetadataAttribute : Attribute
{
    public string Category { get; }
    public int Order { get; }
    public EffectMetadataAttribute(string category, int order = 0)
        => (Category, Order) = (category, order);
}

// 掃描時讀取 Attribute 做清單與分類
```
- 實際案例：衍生自「支援特效外掛」的可用性設計。
- 實作環境：C#
- 實測數據：文章未提供

- Learning Points：Attribute、反射、中繼資料索引
- 技能要求：C# Attribute、UI 清單
- 延伸思考：外掛商店、線上更新

- Practice：基礎（分類 Attribute）、進階（搜尋/排序）、專案（外掛總管）
- Assessment：完整性（分類/搜尋）、品質（本地化）、效能、創新（商店/評分）

---

## Case #11: 預覽與最終套用一致性的雙緩衝設計

### Problem Statement
- 業務場景：預覽效果與最終套用結果需一致，避免「看起來」與「實際」不同。
- 技術挑戰：縮放/取樣差異、色彩空間、選區邊界與羽化一致性。
- 影響範圍：可信度、使用者信心、返工成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 預覽在縮放/降採樣後進行，結果不同。
  2. 預覽與套用走不同路徑或參數。
  3. 選區遮罩解析度不一致。
- 深層原因：
  - 架構層面：單一演算法路徑未共用。
  - 技術層面：取樣、Gamma/色彩空間不一致。
  - 流程層面：缺乏一致性驗證流程。

### Solution Design
- 解決策略：預覽與套用共用演算法函式；預覽使用縮放至視窗尺寸的「相同演算法」；遮罩與色彩管理一致；建立回歸測試影像。
- 實施步驟：
  1. 演算法共用
     - 細節：抽出核心 ApplyCore(area, params)，預覽/套用共用。
     - 時間：0.5 天
  2. 一致性測試
     - 細節：黃金圖（golden image）輸出對比。
     - 時間：0.5 天
- 關鍵程式碼/設定：
```csharp
Bitmap ApplyEffect(Bitmap src, Rect area, Params p) => ApplyCore(src, area, p);
Bitmap PreviewEffect(Bitmap src, Rect area, Params p, Size previewSize)
{
    using var region = ScaleRegion(area, src.Size, previewSize);
    return ApplyCore(Downscale(src, previewSize), region, p);
}
```
- 實際案例：外掛/濾鏡預覽所必需的工程設計。
- 實作環境：C#
- 實測數據：文章未提供

- Learning Points：演算法共用、測試圖像、色彩一致性
- 技能要求：單元測試、影像取樣
- 延伸思考：ICC、顯示器配置差異

- Practice：基礎（共用函式）、進階（黃金圖對比）、專案（自動化快照測試）
- Assessment：完整性（預覽=套用）、品質（一致性報告）、效能、創新（可視化差異）

---

## Case #12: 像素處理效能優化（LockBits 與區塊處理）

### Problem Statement
- 業務場景：大尺寸影像應用濾鏡或畫筆時，若逐像素 API 取用（GetPixel/SetPixel）會非常慢。
- 技術挑戰：提高像素存取吞吐、降低 GC 與鎖定成本、避免 UI 卡頓。
- 影響範圍：效能、體驗、可處理圖片上限。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. GetPixel/SetPixel 開銷高。
  2. 每像素呼叫跨界/安全檢查昂貴。
  3. 單執行緒處理無法利用多核。
- 深層原因：
  - 架構層面：缺乏批次/區塊處理設計。
  - 技術層面：未使用 LockBits/Span/unsafe。
  - 流程層面：未實作進度匯報與取消。

### Solution Design
- 解決策略：使用 LockBits 或 MemoryMarshal.Span<byte> 批次處理；以區塊平行化；UI 以非同步執行並提供取消。
- 實施步驟：
  1. 批次處理
     - 細節：LockBits + 指標迴圈。
     - 時間：0.5 天
  2. 平行化
     - 細節：Parallel.For 區塊分段。
     - 時間：0.5 天
- 關鍵程式碼/設定：
```csharp
Parallel.For(0, height, y =>
{
    byte* row = pBase + y * stride;
    for (int x=0; x<width; x++)
    {
        byte b=row[0], g=row[1], r=row[2]; // BGRA
        // ...處理...
        row += 4;
    }
});
```
- 實際案例：文章提到「濾鏡」，此為效能實作策略。
- 實作環境：C#、unsafe、TPL
- 實測數據：文章未提供

- Learning Points：LockBits、平行化、取消
- 技能要求：unsafe、Parallel、非同步
- 延伸思考：SIMD、GPU

- Practice：基礎（LockBits 灰階）、進階（平行卷積）、專案（進度/取消）
- Assessment：完整性（處理正確）、品質（邊界處理）、效能、創新（SIMD）

---

## Case #13: 選區遮罩與特效套用範圍控制

### Problem Statement
- 業務場景：特效應僅影響選取區域，其他區域保持不變。
- 技術挑戰：遮罩合併圖層、羽化邊緣、避免硬邊產生。
- 影響範圍：效果品質、自然過渡、使用體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無遮罩將導致全圖套用。
  2. 羽化邊緣難以自然。
  3. 多層合成下遮罩傳遞複雜。
- 深層原因：
  - 架構層面：統一遮罩格式缺乏。
  - 技術層面：Alpha mask、羽化算法。
  - 流程層面：選區/遮罩生命週期管理。

### Solution Design
- 解決策略：使用單通道 Alpha 遮罩（byte[]）；特效 Apply 時僅處理 mask>0 區域；羽化使用距離場或高斯模糊。
- 實施步驟：
  1. 遮罩格式
     - 細節：Region -> Raster Mask；size = canvas size。
     - 時間：0.5 天
  2. 羽化
     - 細節：遮罩高斯模糊半徑可調。
     - 時間：0.5 天
- 關鍵程式碼/設定：
```csharp
// 假設 mask[y*width+x] ∈ [0,255]
if (mask[i] > 0)
{
    // 根據 mask 權重混合原像素與處理後像素
    byte w = mask[i];
    dst = Lerp(src, effect(src), w/255f);
}
```
- 實際案例：文章中的套索/濾鏡功能組合。
- 實作環境：C#
- 實測數據：文章未提供

- Learning Points：遮罩、羽化、權重混合
- 技能要求：影像混合、資料結構
- 延伸思考：向量遮罩、貝茲曲線選區

- Practice：基礎（遮罩限定）、進階（羽化）、專案（距離場羽化）
- Assessment：完整性（遮罩生效）、品質（邊緣自然）、效能、創新（距離場）

---

## Case #14: 開放原始碼專案閱讀與學習路徑（以 Paint.NET 為例）

### Problem Statement
- 業務場景：C# 開發者需要可參考的完整影像處理應用程式以提升實戰能力。
- 技術挑戰：大型程式碼基礎導覽、模組關聯、效能與 UI 交互。
- 影響範圍：學習效率、技能成長、團隊培訓。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺乏高品質開源範例作為對照。
  2. 影像處理知識跨領域。
  3. 缺乏系統化閱讀方法。
- 深層原因：
  - 架構層面：大型專案模組多、文件有限。
  - 技術層面：UI/核心/插件的結構理解難。
  - 流程層面：缺乏學習路線圖。

### Solution Design
- 解決策略：建立閱讀路線：UI（工具窗體/視窗狀態）→ 模型（文檔/圖層/選區）→ 核心（濾鏡/管線/效能）→ 外掛（契約/載入/安全）；輔以小實作練習。
- 實施步驟：
  1. 環境建置
     - 細節：下載原始碼、對應 .NET 版本、能編譯與執行。
     - 時間：0.5 天
  2. 導讀計畫
     - 細節：按模組閱讀，邊讀邊做微型練習（新增簡單濾鏡）。
     - 時間：2 天
- 關鍵程式碼/設定：不適用（閱讀計畫與實作任務綁定）
- 實際案例：文章強調「完整 source code 可參考」。
- 實作環境：Visual Studio、.NET 相容版本
- 實測數據：文章未提供

- Learning Points：系統化閱讀、模組化理解、以做帶學
- 技能要求：C# 中高階、WinForms/WPF、影像處理基礎
- 延伸思考：將閱讀筆記轉為團隊知識庫

- Practice：基礎（成功建置）、進階（新增灰階特效）、專案（外掛管理器原型）
- Assessment：完整性（可編譯/運行）、品質（筆記/文檔）、效能（Demo 流暢）、創新（改良點）

---

## Case #15: 工具面板浮動/停駐管理（Dock/Floating 切換）

### Problem Statement
- 業務場景：使用者在不同工作流下需要將工具面板浮動或停駐於主視窗，搭配半透明以最佳化空間。
- 技術挑戰：拖放停駐、佈局保存、尺寸限制、Z-Order。
- 影響範圍：可用性、作業效率、跨解析度一致性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 固定佈局限制使用。
  2. 多螢幕/高DPI 情境需要彈性。
  3. 重啟後佈局遺失。
- 深層原因：
  - 架構層面：缺乏停駐系統/佈局儲存。
  - 技術層面：拖放命中測試與佈局演算法。
  - 流程層面：設定同步與遷移。

### Solution Design
- 解決策略：實作簡單 Dock Manager 或採用成熟 Docking 套件；保存佈局到設定檔；結合 Case #1 的半透明策略。
- 實施步驟：
  1. Dock 區域與拖放
     - 細節：定義上/下/左/右 Dock 區；拖入高亮。
     - 時間：1 天
  2. 佈局保存
     - 細節：序列化面板位置/尺寸/狀態。
     - 時間：0.5 天
- 關鍵程式碼/設定：可選用 WeifenLuo DockPanel Suite（示意），或自研 Dock Manager。
- 實際案例：文章描述「浮動的工具視窗」；本案例加上 Dock 能力。
- 實作環境：C#、WinForms
- 實測數據：文章未提供

- Learning Points：拖放、佈局序列化、停駐
- 技能要求：HitTest、序列化、UI 佈局
- 延伸思考：佈局預設、雲端同步

- Practice：基礎（左右停駐）、進階（佈局保存/恢復）、專案（完整 Dock Manager）
- Assessment：完整性（浮動/停駐）、品質（拖放體驗）、效能、創新（佈局快照）

---

## Case #16: 外掛載入安全與失效隔離（故障不拖垮主程式）

### Problem Statement
- 業務場景：第三方外掛品質不一，可能拋例外或造成卡死，需避免影響核心應用穩定性。
- 技術挑戰：外掛載入/執行隔離、逾時/取消、錯誤收斂與使用者提示。
- 影響範圍：穩定性、信任度、生態健康。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 外掛未處理例外或有長時間運算。
  2. 外掛相依性衝突。
  3. 記憶體洩漏/資源未釋放。
- 深層原因：
  - 架構層面：外掛與核心同進程、同 AppDomain。
  - 技術層面：缺少逾時/取消與資源限制。
  - 流程層面：外掛簽章與評級制度缺乏。

### Solution Design
- 解決策略：提供外掛執行容器，執行在可取消的 Task，設逾時；嚴格 try-catch 記錄；可選 AppDomain 隔離（.NET Framework）或外部進程；黑名單。
- 實施步驟：
  1. 可取消執行
     - 細節：CancellationToken + timeout + 例外包裝。
     - 時間：0.5 天
  2. 隔離策略
     - 細節：Framework 用 AppDomain；Core 用外部進程 IPC（可後續擴展）。
     - 時間：1-2 天
- 關鍵程式碼/設定：
```csharp
async Task<Bitmap> RunEffectSafeAsync(IEffect eff, Bitmap input, IDictionary<string,object> p, TimeSpan timeout)
{
    using var cts = new CancellationTokenSource(timeout);
    try
    {
        return await Task.Run(() => eff.Apply(input, p), cts.Token);
    }
    catch (Exception ex)
    {
        LogPluginError(eff, ex);
        throw new InvalidOperationException($"Plugin failed: {eff.Name}", ex);
    }
}
```
- 實際案例：衍生自「支援外掛」的工程保障。
- 實作環境：C#、.NET 6+/Framework
- 實測數據：文章未提供

- Learning Points：隔離、取消/逾時、錯誤治理
- 技能要求：非同步、例外處理、IPC（進階）
- 延伸思考：權限沙箱、資源配額

- Practice：基礎（逾時/取消）、進階（AppDomain 隔離）、專案（外部進程容器）
- Assessment：完整性（逾時/錯誤提示）、品質（記錄/回收）、效能、創新（沙箱）

---

## Case #17: 工具架構抽象（畫筆/選取/滴管的一致性介面）

### Problem Statement
- 業務場景：多種工具（套索、噴槍、滴管）需共享一致的生命週期與輸入事件處理。
- 技術挑戰：避免重複程式碼、提升可測性、易於新增工具。
- 影響範圍：可維護性、可擴充性、Bug 率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 各工具自行處理 MouseDown/Move/Up，代碼分散。
  2. 工具狀態管理不一致。
  3. Undo 事件粒度不一致。
- 深層原因：
  - 架構層面：缺少 Tool 抽象與工具管理器。
  - 技術層面：策略模式/狀態機未建立。
  - 流程層面：開發規範缺乏。

### Solution Design
- 解決策略：定義 ITool（Activate/Deactivate/OnMouse*/OnKey*）；ToolManager 管理當前工具；統一事件派發與 Undo 合併策略。
- 實施步驟：
  1. 介面與骨架
     - 細節：抽象基底類別 ToolBase，提供預設行為。
     - 時間：0.5 天
  2. 管理器
     - 細節：切換工具、快捷鍵、光標樣式。
     - 時間：0.5 天
- 關鍵程式碼/設定：
```csharp
public interface ITool
{
    string Name { get; }
    void Activate(); void Deactivate();
    void OnMouseDown(Point p); void OnMouseMove(Point p); void OnMouseUp(Point p);
    void OnKeyDown(Keys k);
}
```
- 實際案例：文章列出多種工具；此為統一架構。
- 實作環境：C#
- 實測數據：文章未提供

- Learning Points：策略模式、事件抽象、解耦
- 技能要求：OOP 設計、事件派發
- 延伸思考：工具外掛化

- Practice：基礎（兩種工具抽象）、進階（快捷切換/游標）、專案（工具外掛框架）
- Assessment：完整性（生命週期）、品質（低耦合）、效能、創新（外掛工具）

---

## Case #18: 內建與外掛濾鏡的管線化與排序

### Problem Statement
- 業務場景：使用者常連續套用多個特效，需要定義順序與重用流程。
- 技術挑戰：可重用管線、狀態保存、參數序列化與重放。
- 影響範圍：效率、可重現性、分享與協作。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 多步手動操作重複性高。
  2. 無法記錄/重放參數組合。
  3. 管線順序影響結果。
- 深層原因：
  - 架構層面：缺少 Effect Pipeline。
  - 技術層面：序列化與快取策略。
  - 流程層面：預設模板與分享流程。

### Solution Design
- 解決策略：設計 EffectStep（EffectId + Params）；EffectPipeline = List<EffectStep>；支援序列化到 Json，重放時依序套用；快取中間結果可選。
- 實施步驟：
  1. 數據結構
     - 細節：EffectId 與參數字典；版本與相容性。
     - 時間：0.5 天
  2. 執行器
     - 細節：逐步套用、可取消、進度條。
     - 時間：1 天
- 關鍵程式碼/設定：
```csharp
public record EffectStep(string Id, Dictionary<string, object> Params);
public class EffectPipeline { public List<EffectStep> Steps { get; } = new(); }
// Serialize to JSON and replay
```
- 實際案例：衍生自外掛與濾鏡。
- 實作環境：C#、System.Text.Json
- 實測數據：文章未提供

- Learning Points：管線化、序列化、可重現性
- 技能要求：序列化、流程控制
- 延伸思考：共享模板、市集

- Practice：基礎（兩步管線）、進階（序列化/重放）、專案（管線編輯器）
- Assessment：完整性（順序/參數）、品質（相容性）、效能、創新（模板分享）

---

## 案例分類

1) 按難度分類
- 入門級（適合初學者）：
  - Case #1 半透明工具視窗
  - Case #7 滴管取樣
  - Case #8 灰階濾鏡（基礎）
- 中級（需要一定基礎）：
  - Case #2 外掛架構
  - Case #3 命令歷史
  - Case #4 圖層管理
  - Case #5 套索選取
  - Case #6 噴槍工具
  - Case #9 外掛參數與預覽
  - Case #10 外掛分類呈現
  - Case #11 預覽一致性
  - Case #12 像素效能優化
  - Case #13 遮罩與範圍控制
  - Case #17 工具架構抽象
  - Case #18 濾鏡管線
- 高級（需要深厚經驗）：
  - Case #16 外掛隔離與安全

2) 按技術領域分類
- 架構設計類：Case #2, #3, #4, #11, #16, #17, #18
- 效能優化類：Case #12
- 整合開發類：Case #9, #10, #15
- 除錯診斷類：Case #11, #16
- 安全防護類：Case #16

3) 按學習目標分類
- 概念理解型：Case #4（圖層）、#3（命令歷史）、#2（插件架構）
- 技能練習型：Case #5（套索）、#6（噴槍）、#7（滴管）、#8（濾鏡）
- 問題解決型：Case #1（遮擋問題）、#11（預覽一致性）、#12（效能瓶頸）、#13（範圍控制）、#16（外掛故障）
- 創新應用型：Case #10（外掛可發現性）、#15（Dock 管理）、#18（濾鏡管線）

## 案例關聯圖（學習路徑建議）

- 先學案例（基礎工具與概念）：
  - Step 1：Case #1（UI 半透明）→ 熟悉 WinForms 事件/視窗狀態
  - Step 2：Case #7（滴管）→ 學習像素取樣、座標對映
  - Step 3：Case #5（套索）→ 選區/Region/Mask 概念
  - Step 4：Case #6（噴槍）→ 計時器與繪製

- 中階建構（核心模型與效能）：
  - Step 5：Case #4（圖層管理）→ 文件/圖層/合成基礎
  - Step 6：Case #3（命令歷史）→ Undo/Redo 與差異快照
  - Step 7：Case #8（濾鏡實作）→ 像素處理與遮罩
  - Step 8：Case #12（效能優化）→ LockBits/平行化

- 擴充與可用性提升：
  - Step 9：Case #2（外掛架構）→ 介面/反射載入
  - Step 10：Case #9（參數 UI 與預覽）→ 使用體驗
  - Step 11：Case #11（預覽一致性）→ 品質保障
  - Step 12：Case #10（外掛分類）→ 可發現性

- 高階保障與進階整合：
  - Step 13：Case #16（外掛隔離與安全）→ 穩定性/可靠性
  - Step 14：Case #15（Dock 管理）→ 佈局體驗
  - Step 15：Case #17（工具架構抽象）→ 解耦與擴充
  - Step 16：Case #18（濾鏡管線）→ 可重現工作流與分享

依賴關係說明：
- Case #8（濾鏡）依賴 Case #4（圖層/合成）與 Case #13（遮罩）。
- Case #9（預覽）與 Case #11（一致性）依賴 Case #8（濾鏡核心）。
- Case #2（外掛）為 Case #8、#9、#10、#16、#18 的基礎。
- Case #12（效能）是 Case #6、#8、#13 的通用優化基礎。
- Case #3（命令歷史）建議在所有編輯操作上統一套用。

說明：原文為功能/設計層級的簡述，未提供量化指標與完整特定案例。以上案例以工程實作為導向，結合文章提到的功能點進行教學化設計，實測數據處均標註「文章未提供」。