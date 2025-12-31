---
layout: synthesis
title: "Canon Digital Camera 記憶卡歸檔工具 - RAW Support Update"
synthesis_type: solution
source_post: /2006/11/04/canon-digital-camera-organizer-raw-support-update/
redirect_from:
  - /2006/11/04/canon-digital-camera-organizer-raw-support-update/solution/
postid: 2006-11-04-canon-digital-camera-organizer-raw-support-update
---

以下內容基於你提供的文章，將其中隱含與明示的問題情境抽象為可教學、可實作、可評估的解決方案案例。每個案例皆包含問題、根因、解法（含程式碼/流程）、效益與練習評估。文章雖短，但涉及的技術面向可拆解成多個可實作主題。為避免臆測未出現之量化數據，實測與改善幅度欄位在無明確數據時以功能性與風險降低作定性描述。

## Case #1: 在 .NET 記憶卡歸檔工具中加入 Canon RAW（CRW）讀取能力

### Problem Statement（問題陳述）
• 業務場景：現有的記憶卡歸檔工具用於整理相片，但不支援 Canon 的 RAW（CRW）檔，使用者希望能讀取 RAW 以便將其與 JPEG 一致歸檔（依拍攝時間、相機型號）。  
• 技術挑戰：找不到穩定可靠且可在 .NET 中直接使用的 RAW 解析函式庫；Canon 官方 SDK 僅提供 C++。  
• 影響範圍：RAW 使用者無法使用工具完成歸檔，需手動處理，造成體驗不一致且提高維護成本。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：
1) 缺乏 .NET 原生的 RAW 解析函式庫。  
2) Canon 官方 SDK 僅支援 C++，開發者（與現有程式）偏向 C#。  
3) 開源專案不成熟、可靠度不足。

• 深層原因：
- 架構層面：原始工具未預留跨格式的metadata抽象層。  
- 技術層面：技術選型侷限在 .NET，排除 C++ 導致可選方案變少。  
- 流程層面：缺乏對外部元件/解碼器依賴的預研清單與評估流程。

### Solution Design（解決方案設計）
• 解決策略：安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP，引用其安裝資料夾中的 RawManager.Interop.dll，在 C# 透過 COM Interop 讀取 CRW 檔的相機型號與其他 metadata（最小可行功能）。

• 實施步驟：
1) 安裝依賴  
- 實作細節：先安裝 Microsoft RAW Viewer，確保系統有該 Interop。  
- 所需資源：Microsoft RAW Image Thumbnailer and Viewer。  
- 預估時間：0.5 小時。
2) 參考 Interop 並封裝  
- 實作細節：專案加入 RawManager.Interop.dll 參考，撰寫 wrapper。  
- 所需資源：Visual Studio、.NET Framework。  
- 預估時間：1 小時。
3) 實作讀取與展示  
- 實作細節：呼叫 CRawViewerClass.Load，讀 CameraModel 等屬性。  
- 所需資源：C#。  
- 預估時間：0.5 小時。
4) 整合到歸檔流程  
- 實作細節：將讀到的 metadata 餵給歸檔命名/路徑規則。  
- 所需資源：既有工具程式碼。  
- 預估時間：1 小時。

• 關鍵程式碼/設定：
```csharp
// 需先安裝 Microsoft RAW Image Thumbnailer and Viewer for Windows XP
// 並將 RawManager.Interop.dll 加入參考
using RawManager;

public static void PrintCameraModel(string crwPath)
{
    var raw = new CRawViewerClass();
    raw.Load(crwPath); // 載入 CRW
    Console.WriteLine($"Camera Model: {raw.CameraModel}");
}
```

• 實際案例：作者以 CRawViewerClass 成功讀出 CameraModel，更新工具並提供 MSI。  
• 實作環境：Windows XP、.NET Framework（2.0+）、Visual Studio 2005、Microsoft RAW Viewer。  
• 實測數據：  
- 改善前：不支援 RAW metadata 讀取。  
- 改善後：可讀 CRW 相機型號（與其他可用屬性）。  
- 改善幅度：功能覆蓋從 0% → 可支援 CRW 讀取（定性）。

Learning Points（學習要點）
• 核心知識點：COM Interop 基礎、第三方解碼器再利用、最小可行功能落地。  
• 技能要求：  
- 必備技能：C#、.NET 參考管理、基本例外處理。  
- 進階技能：Interop 封裝、依賴治理。  
• 延伸思考：可否改為 WIC（Windows Imaging Component）？如何管理未來不同廠牌的 RAW？相容性如何驗證？  
• Practice Exercise：  
- 基礎：撰寫函式讀取 CameraModel。  
- 進階：封裝為 IMetadataReader 供策略切換。  
- 專案：將讀取結果整合到歸檔流程、命名與路徑生成。  
• Assessment Criteria：  
- 功能完整性：可穩定讀取 CRW 基本 metadata。  
- 程式碼品質：封裝清楚、無硬編依賴路徑。  
- 效能優化：避免不必要的完整解碼。  
- 創新性：可擴展多格式的策略設計。

---

## Case #2: 安裝先決條件偵測與啟動前檢查（Microsoft RAW Viewer）

### Problem Statement（問題陳述）
• 業務場景：工具更新為支援 RAW，但需依賴 Microsoft RAW Viewer；若使用者未安裝，功能會失效。  
• 技術挑戰：如何在啟動或安裝時準確偵測依賴狀態並提供友善指引？  
• 影響範圍：未安裝依賴的使用者會遇到錯誤或無法使用 RAW 功能，增加支援成本。  
• 複雜度評級：低-中

### Root Cause Analysis（根因分析）
• 直接原因：外部 Interop 由系統安裝提供，非應用程式內建。  
• 深層原因：  
- 架構：沒有集中化的依賴檢查機制。  
- 技術：未建立檢查方法（登錄/檔案/COM ProgID）。  
- 流程：缺乏安裝說明與失敗處理流程。

### Solution Design（解決方案設計）
• 解決策略：在應用程式啟動或安裝流程加入檢查，若缺少即引導下載安裝，避免執行時失敗。

• 實施步驟：
1) 設計檢查函式  
- 實作細節：掃描登錄 Uninstall 項或檢查 DLL 存在。  
- 工具：Microsoft.Win32 Registry API。  
- 時間：1 小時。
2) 啟動時阻擋並引導  
- 實作細節：顯示對話框附下載連結。  
- 工具：WinForms/WPF（或 Console 提示）。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
using Microsoft.Win32;
using System;

public static bool IsRawViewerInstalled()
{
    string[] roots = {
        @"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        @"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    };
    foreach (var root in roots)
    {
        using (var key = Registry.LocalMachine.OpenSubKey(root))
        {
            if (key == null) continue;
            foreach (var subName in key.GetSubKeyNames())
            {
                using (var sub = key.OpenSubKey(subName))
                {
                    var displayName = sub?.GetValue("DisplayName") as string;
                    if (!string.IsNullOrEmpty(displayName) &&
                        displayName.IndexOf("RAW Image Thumbnailer", StringComparison.OrdinalIgnoreCase) >= 0)
                        return true;
                }
            }
        }
    }
    return false;
}
```

• 實際案例：原文要求「使用前請先安裝」——此檢查可將文字說明轉為技術落地。  
• 實作環境：Windows XP、.NET Framework 2.0。  
• 實測數據：  
- 改善前：使用者可能在不知情下執行，導致錯誤。  
- 改善後：啟動前即提示安裝，降低故障率。  
- 改善幅度：支援工單預期下降（定性）。

Learning Points
• 核心知識點：依賴檢查與使用者引導。  
• 技能要求：  
- 必備：Registry 操作。  
- 進階：安裝程式 LaunchCondition。  
• 延伸思考：是否可改為 Bundle/Bootstrapper 自動安裝？  
• Practice：  
- 基礎：列出所有 Uninstall 項。  
- 進階：加入 UI 提示與連結。  
- 專案：在 MSI/Setup 中加入啟動前檢查。  
• 評估：  
- 功能：能正確判斷是否安裝。  
- 品質：錯誤處理完善。  
- 效能：啟動檢查迅速。  
- 創新：提供一鍵下載。

---

## Case #3: 以反組譯找出可用 Interop 類型並驗證存取

### Problem Statement（問題陳述）
• 業務場景：缺乏官方 .NET 文件說明如何使用 RAW Viewer 的 Interop。  
• 技術挑戰：需要找出可用型別（如 CRawViewerClass）與屬性名稱。  
• 影響範圍：無法快速落地呼叫，延誤專案時程。  
• 複雜度評級：高

### Root Cause Analysis（根因分析）
• 直接原因：沒有 .NET API 文件。  
• 深層原因：  
- 架構：依賴內部/未公開的 Interop。  
- 技術：需借助反組譯工具與反射驗證。  
- 流程：缺少法遵檢視（反組譯/EULA 考量）。

### Solution Design（解決方案設計）
• 解決策略：使用反組譯工具（Reflector/ILSpy）了解 Interop 類型名稱，再用反射在程式內驗證類型存在、屬性可讀，建立最小呼叫範例。

• 實施步驟：
1) 反組譯 Interop  
- 細節：定位 RawManager.Interop.dll，查看公開類型與屬性。  
- 資源：ILSpy/Reflector。  
- 時間：0.5-1 小時。
2) 反射驗證  
- 細節：程式內用 Assembly.LoadFrom + Type/Property 檢查。  
- 資源：System.Reflection。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
using System;
using System.IO;
using System.Linq;
using System.Reflection;

public static void ProbeRawInterop(string assemblyPath)
{
    if (!File.Exists(assemblyPath))
        throw new FileNotFoundException("Interop not found.", assemblyPath);

    var asm = Assembly.LoadFrom(assemblyPath);
    var type = asm.GetTypes().FirstOrDefault(t => t.Name.Contains("CRawViewer"));
    Console.WriteLine(type != null
        ? $"Found type: {type.FullName}"
        : "CRawViewer type not found.");
}
```

• 實際案例：作者「隨便找個 DLL 反組譯」找到可用類型並成功呼叫。  
• 實作環境：Windows XP、.NET 2.0。  
• 實測數據：  
- 改善前：無可用 API 文件，無法呼叫。  
- 改善後：定位到可用型別並成功讀取 CameraModel。  
- 改善幅度：需求落地時間大幅縮短（定性）。

Learning Points
• 核心知識點：反組譯探索、反射驗證、風險提示（EULA）。  
• 技能要求：  
- 必備：反射、組件載入。  
- 進階：符合法遵的逆向工程邊界。  
• 延伸思考：以 WIC/官方 SDK 取代未公開 API。  
• Practice：  
- 基礎：列出 Interop 內所有 public 型別。  
- 進階：列舉型別屬性與方法。  
- 專案：生成最小呼叫測試工具。  
• 評估：  
- 功能：能列舉與檢測目標型別。  
- 品質：容錯、錯誤訊息清楚。  
- 效能：快速探測。  
- 創新：自動產生呼叫樣板。

---

## Case #4: 以 C# 包裝 Interop，避免直接依賴 C++ Canon SDK

### Problem Statement（問題陳述）
• 業務場景：開發者與既有程式碼主力在 C#/.NET，希望避免導入 C++ 與 P/Invoke 複雜度。  
• 技術挑戰：需以 .NET 方式調用 RAW 能力，同時維持易測試與可替換。  
• 影響範圍：團隊技能、維護成本、交付時程。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：Canon SDK 僅有 C++。  
• 深層原因：  
- 架構：未定義抽象層。  
- 技術：無 .NET 友善 API。  
- 流程：技能配比不符。

### Solution Design（解決方案設計）
• 解決策略：定義 IRawReader 介面，使用 RawManager.Interop.dll 實作 RawInteropReader，未來可用其他方案替換。

• 實施步驟：
1) 定義抽象介面  
- 細節：IRawReader.ReadInfo 回傳標準化結構。  
- 工具：C#。  
- 時間：0.5 小時。
2) Interop 實作  
- 細節：呼叫 CRawViewerClass。  
- 工具：RawManager.Interop.dll。  
- 時間：0.5 小時。
3) 依賴注入  
- 細節：UI/流程層依賴介面而非實作。  
- 工具：簡單工廠或 DI。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
public class RawInfo
{
    public string CameraModel { get; set; }
    public DateTime? CaptureTime { get; set; }
    public string FilePath { get; set; }
}

public interface IRawReader
{
    bool CanRead(string path);
    RawInfo ReadInfo(string path);
}

public class RawInteropReader : IRawReader
{
    public bool CanRead(string path) => 
        string.Equals(Path.GetExtension(path), ".crw", StringComparison.OrdinalIgnoreCase);

    public RawInfo ReadInfo(string path)
    {
        var raw = new RawManager.CRawViewerClass();
        raw.Load(path);
        return new RawInfo
        {
            FilePath = path,
            CameraModel = raw.CameraModel
            // CaptureTime 視 Interop 可用屬性取得
        };
    }
}
```

• 實際案例：作者成功呼叫 Interop，符合快速交付需求。  
• 實作環境：Windows XP、.NET 2.0。  
• 實測數據：  
- 改善前：需改用 C++ 或混合專案。  
- 改善後：純 C# 完成整合。  
- 改善幅度：開發複雜度與維護成本下降（定性）。

Learning Points
• 核心知識點：介面抽象、可替換實作、依賴倒置。  
• 技能要求：  
- 必備：C# 介面、封裝。  
- 進階：DI/測試替身。  
• 延伸思考：如何平滑切換到 WIC 或其他 RAW SDK？  
• Practice：  
- 基礎：以假物件模擬 IRawReader。  
- 進階：在 UI 層以介面注入實作。  
- 專案：加入第二個讀取器並以檔案副檔名選擇。  
• 評估：  
- 功能：可讀取 CRW。  
- 品質：低耦合、可測試。  
- 效能：無不必要的重複載入。  
- 創新：熱插拔讀取器。

---

## Case #5: 以最小可行功能對齊需求：只讀 metadata（不做 RAW 編輯）

### Problem Statement（問題陳述）
• 業務場景：使用者只需拍攝時間與基本資訊；RAW 編輯非必要。  
• 技術挑戰：避免陷入不存在或複雜的編輯 API。  
• 影響範圍：功能優先級與交付時程。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：Interop 未見明確編輯 API；編輯難度與風險高。  
• 深層原因：  
- 架構：未規劃影像處理管線。  
- 技術：編輯 RAW 涉大量相機/色彩學細節。  
- 流程：需求澄清不足易導致過度設計。

### Solution Design（解決方案設計）
• 解決策略：與利害關係人確認只需 metadata，落地 CameraModel 與拍攝時間等欄位，聚焦「歸檔」核心價值。

• 實施步驟：
1) 需求鎖定  
- 細節：只讀 metadata，列出欄位清單。  
- 工具：需求文件。  
- 時間：0.5 小時。
2) 實作 metadata 讀取  
- 細節：CRawViewer 可讀欄位 + 反射嘗試時間欄位；失敗則 fallback。  
- 工具：C# 反射。  
- 時間：1 小時。

• 關鍵程式碼/設定：
```csharp
public static DateTime? TryGetCaptureTime(object rawCom)
{
    string[] candidates = { "DateTaken", "ShootingTime", "CaptureTime", "DateTime" };
    var t = rawCom.GetType();
    foreach (var name in candidates)
    {
        var pi = t.GetProperty(name);
        if (pi != null)
        {
            var val = pi.GetValue(rawCom, null);
            if (val is DateTime dt) return dt;
            if (DateTime.TryParse(val?.ToString(), out var parsed)) return parsed;
        }
    }
    // Fallback：檔案建立時間（次佳）
    return null;
}
```

• 實際案例：對齊「raw 只要知道啥米時間拍的應該就 OK」。  
• 實作環境：Windows XP、.NET 2.0。  
• 實測數據：  
- 改善前：功能範圍模糊，可能拖延。  
- 改善後：快速交付 metadata 讀取。  
- 改善幅度：時程風險降低（定性）。

Learning Points
• 核心知識點：MVP/MVF、避免過度工程。  
• 技能要求：  
- 必備：反射、例外處理。  
- 進階：驗收條件撰寫。  
• 延伸思考：如何在不改變 UI 的前提逐步擴充？  
• Practice：  
- 基礎：實作 TryGetCaptureTime。  
- 進階：增加多個候補欄位名稱並記錄成功率。  
- 專案：建立 metadata 欄位能力矩陣。  
• 評估：  
- 功能：可取得拍攝時間或合理 fallback。  
- 品質：清楚的錯誤訊息。  
- 效能：呼叫次數最小化。  
- 創新：欄位探索機制。

---

## Case #6: RAW 載入的錯誤處理與回復策略

### Problem Statement（問題陳述）
• 業務場景：在批次歸檔時，RAW 檔可能遺失、損毀或不支援，需避免整批中斷。  
• 技術挑戰：Interop 例外處理、失敗隔離、可追溯。  
• 影響範圍：穩定性、使用者信任、資料安全。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：外部元件行為不確定、檔案品質參差。  
• 深層原因：  
- 架構：缺乏容錯與重試設計。  
- 技術：例外分類與重試條件不明。  
- 流程：缺少錯誤紀錄與支援流程。

### Solution Design（解決方案設計）
• 解決策略：將載入包在 Try/Catch，分類錯誤，對單檔失敗以警示/跳過，批次持續；同時記錄 Log。

• 實施步驟：
1) 錯誤分類  
- 細節：檔案不存在 / 格式不支援 / Interop 例外。  
- 工具：自訂例外類型。  
- 時間：0.5 小時。
2) 日誌與告警  
- 細節：TraceSource/檔案日誌。  
- 工具：System.Diagnostics。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
public RawInfo SafeRead(string path, IRawReader reader, Action<string> warn)
{
    try
    {
        if (!File.Exists(path)) { warn($"Not found: {path}"); return null; }
        if (!reader.CanRead(path)) { warn($"Unsupported: {path}"); return null; }
        return reader.ReadInfo(path);
    }
    catch (COMException ex)
    {
        warn($"Interop error: {ex.Message}");
        return null;
    }
    catch (Exception ex)
    {
        warn($"Unexpected error: {ex}");
        return null;
    }
}
```

• 實際案例：文章指出資源不成熟，容錯設計能降低風險。  
• 實作環境：Windows XP、.NET 2.0。  
• 實測數據：  
- 改善前：單檔失敗可能中斷批次。  
- 改善後：失敗隔離、可追溯。  
- 改善幅度：批次成功率提升（定性）。

Learning Points
• 核心知識點：容錯、失敗隔離、可觀測性。  
• 技能要求：  
- 必備：例外處理、日誌。  
- 進階：重試策略、熔斷。  
• 延伸思考：是否需要錯誤收斂報告？  
• Practice：  
- 基礎：分類並記錄錯誤。  
- 進階：加入重試與指數退避。  
- 專案：日誌儀表板。  
• 評估：  
- 功能：批次不中斷。  
- 品質：錯誤訊息明確。  
- 效能：日誌不拖慢流程。  
- 創新：可插拔警示通道。

---

## Case #7: 多格式支援與擴充策略（RAW + JPEG）

### Problem Statement（問題陳述）
• 業務場景：記憶卡通常混有 JPEG 與 RAW，需一致化歸檔流程。  
• 技術挑戰：不同格式的 metadata 來源不同（EXIF vs Interop）。  
• 影響範圍：使用者體驗與維護複雜度。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：多格式管線未抽象化。  
• 深層原因：  
- 架構：缺少策略路由。  
- 技術：各格式 API 差異大。  
- 流程：擴充無標準。

### Solution Design（解決方案設計）
• 解決策略：以副檔名/魔術數決定使用 IMetadataReader 實作（RawInteropReader / JpegExifReader），管線輸出同一 RawInfo 結構。

• 實施步驟：
1) Reader 註冊表  
- 細節：Dictionary<string, IMetadataReader>。  
- 工具：C#。  
- 時間：0.5 小時。
2) 路由實作  
- 細節：先判斷副檔名，再 fallback。  
- 工具：策略模式。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
public class MetadataRouter
{
    private readonly List<IMetadataReader> readers;

    public MetadataRouter(IEnumerable<IMetadataReader> readers) => this.readers = readers.ToList();

    public RawInfo Read(string path)
    {
        var reader = readers.FirstOrDefault(r => r.CanRead(path));
        return reader?.ReadInfo(path);
    }
}
```

• 實際案例：文章提及 RAW 與 JPEG 同場景的歸檔需求。  
• 實作環境：.NET 2.0。  
• 實測數據：  
- 改善前：單一格式處理。  
- 改善後：多格式一致輸出。  
- 改善幅度：覆蓋率提升（定性）。

Learning Points
• 核心知識點：策略模式、抽象化。  
• 技能要求：  
- 必備：介面設計。  
- 進階：可擴充性設計。  
• 延伸思考：加入 Heif/Heic、DNG 支援。  
• Practice：  
- 基礎：新增 PNG Reader（即便只回傳基本資訊）。  
- 進階：以魔術數偵測格式。  
- 專案：動態載入 Reader 外掛。  
• 評估：  
- 功能：多格式可用。  
- 品質：路由清晰。  
- 效能：最小化不必要嘗試。  
- 創新：外掛化支援。

---

## Case #8: 安裝程式與相依性說明（MSI + 先安裝提示）

### Problem Statement（問題陳述）
• 業務場景：提供 MSI 供使用者安裝更新版工具，但必須先安裝 Microsoft RAW Viewer。  
• 技術挑戰：MSI 不能直接內嵌該 Viewer，需在安裝階段強化說明或檢查。  
• 影響範圍：安裝成功率、支援成本。  
• 複雜度評級：低-中

### Root Cause Analysis（根因分析）
• 直接原因：授權/再散佈限制，無法打包 Viewer。  
• 深層原因：  
- 架構：安裝程式未檢查外部相依性。  
- 技術：缺少 LaunchCondition 或 Bootstrapper。  
- 流程：說明文件不足。

### Solution Design（解決方案設計）
• 解決策略：  
- 在 MSI 前置說明與下載頁面連結。  
- 應用程式啟動時二次檢查（Case #2）。  
- 若採 WiX，可加入 LaunchCondition。

• 實施步驟：
1) 文件與連結  
- 細節：在下載頁明確標註先決條件與官方下載連結。  
- 時間：0.5 小時。
2) 啟動檢查  
- 細節：程式啟動時阻擋。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：同 Case #2 檢查函式（略）。

• 實際案例：原文已提供 MSI 與「使用前請先安裝」說明。  
• 實作環境：Windows XP。  
• 實測數據：  
- 改善前：安裝成功但執行失敗。  
- 改善後：安裝即知缺何物。  
- 改善幅度：安裝體驗提升（定性）。

Learning Points
• 核心知識點：相依性管理與安裝體驗。  
• 技能要求：  
- 必備：安裝文檔撰寫。  
- 進階：WiX/Bootstrapper。  
• 延伸思考：是否能提供一鍵安裝腳本？  
• Practice：  
- 基礎：在安裝畫面顯示先決條件。  
- 進階：建立 Bootstrapper。  
- 專案：安裝記錄與回報。  
• 評估：  
- 功能：清晰提示與阻擋。  
- 品質：錯誤引導友善。  
- 效能：安裝流程簡潔。  
- 創新：自動偵測下載鏡像。

---

## Case #9: JPEG EXIF 與 RAW Metadata 的一致化輸出

### Problem Statement（問題陳述）
• 業務場景：需將 JPEG 與 RAW 檔以同一欄位集合輸出以利歸檔。  
• 技術挑戰：JPEG EXIF 與 RAW Interop 的欄位名稱/型態不一致。  
• 影響範圍：資料對齊、查詢、命名規則。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：不同格式有不同 metadata 規範。  
• 深層原因：  
- 架構：缺乏標準化資料模型。  
- 技術：欄位解析/轉換缺少策略。  
- 流程：未定義必備欄位清單。

### Solution Design（解決方案設計）
• 解決策略：制定標準 RawInfo（相機型號、拍攝時間等），JPEG 用 System.Drawing 讀 EXIF（0x0110、0x9003），RAW 用 Interop，同步映射到 RawInfo。

• 實施步驟：
1) 定義 RawInfo  
- 細節：最小欄位集。  
- 時間：0.5 小時。
2) JPEG EXIF 讀取  
- 細節：使用 GetPropertyItem。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
using System.Drawing;
using System.Text;

public static string GetJpegCameraModel(string path)
{
    using (var img = Image.FromFile(path))
    {
        const int ModelId = 0x0110; // Camera Model
        var item = img.GetPropertyItem(ModelId);
        return Encoding.ASCII.GetString(item.Value).Trim('\0');
    }
}

public static DateTime? GetJpegDateTaken(string path)
{
    using (var img = Image.FromFile(path))
    {
        const int DateTakenId = 0x9003; // DateTimeOriginal
        var item = img.GetPropertyItem(DateTakenId);
        var s = Encoding.ASCII.GetString(item.Value).Trim('\0');
        // EXIF 格式 "yyyy:MM:dd HH:mm:ss"
        if (DateTime.TryParse(s.Replace(':', '-').Substring(0, 10) + s.Substring(10), out var dt))
            return dt;
        return null;
    }
}
```

• 實際案例：與 RAW 輸出對齊便於後續歸檔。  
• 實作環境：.NET 2.0、System.Drawing。  
• 實測數據：  
- 改善前：欄位不一致。  
- 改善後：統一資料模型。  
- 改善幅度：資料處理複雜度下降（定性）。

Learning Points
• 核心知識點：EXIF 基礎、欄位對齊。  
• 技能要求：  
- 必備：System.Drawing 使用。  
- 進階：EXIF Tag Map 管理。  
• 延伸思考：非 EXIF 的副檔案（XMP）如何處理？  
• Practice：  
- 基礎：讀取 JPEG 的 0x0110 與 0x9003。  
- 進階：建立 Tag -> 欄位映射表。  
- 專案：將 JPEG/RAW 產生統一 JSON。  
• 評估：  
- 功能：資料統一輸出。  
- 品質：錯誤與缺值處理。  
- 效能：批次處理速度。  
- 創新：自動欄位偵測。

---

## Case #10: 以拍攝時間與相機型號為依據的自動歸檔與命名

### Problem Statement（問題陳述）
• 業務場景：將記憶卡內容自動整理到以日期/相機為層級的資料夾，含 RAW 與 JPEG。  
• 技術挑戰：正確取得拍攝時間與相機型號，並處理缺值。  
• 影響範圍：檔案管理效率與可追溯性。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：RAW 先前無法讀 metadata，導致無法歸檔。  
• 深層原因：  
- 架構：缺少標準命名/路徑策略。  
- 技術：欄位取得不穩定。  
- 流程：無缺值 fallback。

### Solution Design（解決方案設計）
• 解決策略：統一取得 RawInfo，按 yyyy\\yyyyMMdd\\CameraModel 命名，缺值以 Unknown 或檔案時間替代。

• 實施步驟：
1) 產生目錄與檔名  
- 細節：Path.Combine + Directory.CreateDirectory。  
- 時間：0.5 小時。
2) 移動/複製檔案  
- 細節：處理命名衝突。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
public static string BuildArchivePath(RawInfo info, string baseDir)
{
    var dt = info.CaptureTime ?? File.GetCreationTime(info.FilePath);
    var model = string.IsNullOrEmpty(info.CameraModel) ? "UnknownCamera" : Sanitize(info.CameraModel);
    string y = dt.ToString("yyyy");
    string ymd = dt.ToString("yyyyMMdd");
    string dir = Path.Combine(baseDir, y, ymd, model);
    Directory.CreateDirectory(dir);
    return Path.Combine(dir, Path.GetFileName(info.FilePath));
}

static string Sanitize(string s) => string.Join("_", s.Split(Path.GetInvalidFileNameChars()));
```

• 實際案例：RAW 能讀時間後，與 JPEG 一致歸檔成為可能。  
• 實作環境：.NET 2.0。  
• 實測數據：  
- 改善前：RAW 手動分類。  
- 改善後：RAW/JPEG 一致自動分類。  
- 改善幅度：歸檔效率提升（定性）。

Learning Points
• 核心知識點：命名策略、缺值處理。  
• 技能要求：  
- 必備：IO 操作。  
- 進階：衝突解決（加序號/雜湊）。  
• 延伸思考：如何支持自訂模板？  
• Practice：  
- 基礎：建立日期層級目錄。  
- 進階：處理相同檔名衝突。  
- 專案：支援模板（例如：{yyyy}/{yyyyMMdd}/{Model}）。  
• 評估：  
- 功能：正確建置路徑。  
- 品質：特殊字元處理。  
- 效能：批次處理速度。  
- 創新：模板化。

---

## Case #11: 建立 RAW/EXIF 讀取的單元測試與回歸測試

### Problem Statement（問題陳述）
• 業務場景：確保不同檔案與機型的 metadata 讀取穩健，避免回歸。  
• 技術挑戰：外部相依導致可測性下降、測試樣本管理。  
• 影響範圍：品質保證與交付信心。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：依賴 Interop 與檔案樣本。  
• 深層原因：  
- 架構：缺少 Mock 抽象。  
- 技術：測試環境依賴安裝狀態。  
- 流程：樣本檔案管理未制度化。

### Solution Design（解決方案設計）
• 解決策略：IRawReader 介面允許替身；整合測試需跳過未安裝環境；集中樣本資料夾。

• 實施步驟：
1) 單元測試（Mock）  
- 細節：以假實作回傳固定 RawInfo。  
- 時間：0.5 小時。
2) 整合測試（有樣本）  
- 細節：檢查環境條件，不滿足則 Inconclusive。  
- 時間：1 小時。

• 關鍵程式碼/設定：
```csharp
// 以 NUnit 為例
[Test]
public void Read_CRW_Should_Return_CameraModel_When_Viewer_Installed()
{
    if (!IsRawViewerInstalled())
        Assert.Inconclusive("RAW Viewer not installed.");
    string sample = @"C:\samples\CRW_1234.crw";
    if (!File.Exists(sample))
        Assert.Inconclusive("Sample not found.");
    var reader = new RawInteropReader();
    var info = reader.ReadInfo(sample);
    Assert.IsFalse(string.IsNullOrEmpty(info.CameraModel));
}
```

• 實際案例：原文透過簡短程式驗證 CameraModel，延伸為測試。  
• 實作環境：.NET 2.0、NUnit/MSTest。  
• 實測數據：  
- 改善前：手動驗證、風險高。  
- 改善後：自動測試、可回歸。  
- 改善幅度：測試覆蓋提升（定性）。

Learning Points
• 核心知識點：可測架構、條件式測試。  
• 技能要求：  
- 必備：單元測試工具。  
- 進階：整合測試隔離。  
• 延伸思考：CI 佈署如何處理外部依賴？  
• Practice：  
- 基礎：為 JpegExifReader 寫測試。  
- 進階：測試 Router 對不同格式的行為。  
- 專案：以資料驅動跑多樣本。  
• 評估：  
- 功能：關鍵行為被測到。  
- 品質：測試獨立、可重現。  
- 效能：測試執行時間可控。  
- 創新：條件跳過策略。

---

## Case #12: XP 與後續作業系統的相容性檢查與退場策略

### Problem Statement（問題陳述）
• 業務場景：Microsoft RAW Viewer 主要針對 Windows XP；在非 XP 環境可能不可用或已由 WIC 取代。  
• 技術挑戰：偵測 OS 與可用方案，避免在不支援環境崩潰。  
• 影響範圍：適用範圍、穩定性。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：相依元件的 OS 支援範圍有限。  
• 深層原因：  
- 架構：未抽象影像平台層。  
- 技術：未偵測環境差異。  
- 流程：未定義退場/替代策略。

### Solution Design（解決方案設計）
• 解決策略：啟動時檢測 OS 版本與 Interop 可用性，若不符則提示轉用其他方案（例如：WIC/相容解碼器）或停用 RAW 功能。

• 實施步驟：
1) 檢測 OS 與 Interop  
- 細節：Environment.OSVersion + Interop 探測。  
- 時間：0.5 小時。
2) 提示替代方案  
- 細節：引導文件。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
public static bool IsSupportedEnvironment()
{
    var os = Environment.OSVersion;
    bool isXP = os.Platform == PlatformID.Win32NT && os.Version.Major == 5;
    return isXP && IsRawViewerInstalled();
}
```

• 實際案例：原文鎖定 XP Viewer。  
• 實作環境：Windows XP（主要）。  
• 實測數據：  
- 改善前：跨 OS 風險未知。  
- 改善後：明確檢測與告知。  
- 改善幅度：穩定性提升（定性）。

Learning Points
• 核心知識點：環境檢測與條件式功能。  
• 技能要求：  
- 必備：OS 檢測。  
- 進階：平台抽象。  
• 延伸思考：如何在新 OS 轉向 WIC/新增解碼器。  
• Practice：  
- 基礎：顯示 OS 與支援狀態。  
- 進階：以 feature flag 停用 RAW 功能。  
- 專案：平台偵測與替代路由。  
• 評估：  
- 功能：正確偵測。  
- 品質：使用者提示清晰。  
- 效能：檢測開銷小。  
- 創新：動態選路。

---

## Case #13: 法遵與授權風險控管（未打包第三方 Interop）

### Problem Statement（問題陳述）
• 業務場景：開發使用 Microsoft RAW Viewer 的 Interop，但無法隨 MSI 打包再散佈。  
• 技術挑戰：維持功能同時遵守授權。  
• 影響範圍：法遵風險、散佈策略。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：第三方軟體 EULA 限制。  
• 深層原因：  
- 架構：外部依賴未獨立管理。  
- 技術：無自動化授權檢查。  
- 流程：合規審查缺失。

### Solution Design（解決方案設計）
• 解決策略：不打包 Interop，僅在執行端檢測並提示安裝；文件中標明第三方授權與下載來源。

• 實施步驟：
1) 文件與告知  
- 細節：README/官網下載連結。  
- 時間：0.5 小時。
2) 執行時檢測  
- 細節：參見 Case #2。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
public static void EnsureLegalUseOrWarn()
{
    if (!IsRawViewerInstalled())
    {
        Console.WriteLine("此功能需 Microsoft RAW Image Thumbnailer and Viewer，請依授權條款安裝官方版本。");
        // 可開啟官方連結
    }
}
```

• 實際案例：原文以「使用前請先安裝」方式呈現。  
• 實作環境：—  
• 實測數據：  
- 改善前：潛在侵權風險。  
- 改善後：合規使用第三方元件。  
- 改善幅度：法遵風險降低（定性）。

Learning Points
• 核心知識點：第三方授權管理。  
• 技能要求：  
- 必備：EULA 閱讀。  
- 進階：合規流程設計。  
• 延伸思考：OSS 替代方案的授權比較。  
• Practice：  
- 基礎：撰寫授權聲明區塊。  
- 進階：建立相依清單與版本。  
- 專案：CI 內建授權掃描。  
• 評估：  
- 功能：清楚告知。  
- 品質：文件完善。  
- 效能：無。  
- 創新：自動化檢查。

---

## Case #14: 以「只取 metadata」優化效能與資源使用

### Problem Statement（問題陳述）
• 業務場景：批次讀取大量 RAW 與 JPEG，需快速取得關鍵 metadata，不做影像完整解碼。  
• 技術挑戰：避免不必要的高成本解碼。  
• 影響範圍：處理速度、記憶體占用。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：完整解碼耗時耗資源。  
• 深層原因：  
- 架構：無 metadata-first 策略。  
- 技術：未知哪些 API 僅取 metadata。  
- 流程：沒有效能基準。

### Solution Design（解決方案設計）
• 解決策略：只呼叫必要屬性（如 CameraModel、DateTaken），避免產生縮圖或完整解碼；建立簡易 Stopwatch 量測。

• 實施步驟：
1) 實作 metadata-only 路徑  
- 細節：僅呼叫屬性，不取影像資料。  
- 時間：0.5 小時。
2) 基準量測  
- 細節：Stopwatch 比較前後策略。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
var sw = Stopwatch.StartNew();
var raw = new RawManager.CRawViewerClass();
raw.Load(path);
string model = raw.CameraModel; // 僅取必要屬性
sw.Stop();
Console.WriteLine($"Metadata read took: {sw.ElapsedMilliseconds} ms");
```

• 實際案例：原文僅取 CameraModel 也能滿足主要需求。  
• 實作環境：.NET 2.0。  
• 實測數據：  
- 改善前：可能執行完整解碼（假設）。  
- 改善後：只取 metadata。  
- 改善幅度：處理時間下降（定性）。

Learning Points
• 核心知識點：效能思維、基準量測。  
• 技能要求：  
- 必備：Stopwatch。  
- 進階：分析與剖析。  
• 延伸思考：多緒讀取與 IO 併發。  
• Practice：  
- 基礎：建立量測程式。  
- 進階：對比縮圖與 metadata-only 的耗時。  
- 專案：批次處理報表。  
• 評估：  
- 功能：正確讀 metadata。  
- 品質：量測準確。  
- 效能：明顯下降耗時。  
- 創新：自動化效能回歸。

---

## Case #15: 啟動與 UI 層級的可用性控制（功能開關與提示）

### Problem Statement（問題陳述）
• 業務場景：當 Interop/Viewer 未安裝或 OS 不支援時，需在 UI 停用 RAW 功能並提示。  
• 技術挑戰：避免使用者在不支援情境下操作導致錯誤。  
• 影響範圍：UX、穩定性。  
• 複雜度評級：低

### Root Cause Analysis（根因分析）
• 直接原因：依賴存在可用性。  
• 深層原因：  
- 架構：無狀態同步至 UI。  
- 技術：缺乏 feature flag。  
- 流程：提示不一致。

### Solution Design（解決方案設計）
• 解決策略：在啟動時判斷支援狀態，將狀態注入 UI，禁用相關按鈕/選單，提供安裝連結。

• 實施步驟：
1) 狀態提供器  
- 細節：ISupportStatusProvider 回傳支援狀態。  
- 時間：0.5 小時。
2) UI 綁定  
- 細節：依狀態設定 Enabled/Visible。  
- 時間：0.5 小時。

• 關鍵程式碼/設定：
```csharp
public static bool RawFeatureAvailable => IsSupportedEnvironment();

void UpdateUi()
{
    btnReadRaw.Enabled = RawFeatureAvailable;
    linkInstallViewer.Visible = !RawFeatureAvailable;
}
```

• 實際案例：原文以事前安裝說明，延伸為 UI 控制。  
• 實作環境：WinForms/WPF。  
• 實測數據：  
- 改善前：使用者誤用導致錯誤。  
- 改善後：按鍵自動禁用。  
- 改善幅度：錯誤率下降（定性）。

Learning Points
• 核心知識點：Feature Flag、狀態驅動 UI。  
• 技能要求：  
- 必備：UI 控制屬性。  
- 進階：MVVM/MVP。  
• 延伸思考：國際化提示與指引。  
• Practice：  
- 基礎：加入連結到安裝頁。  
- 進階：動態刷新狀態。  
- 專案：完整設定面板。  
• 評估：  
- 功能：正確禁用。  
- 品質：提示清楚。  
- 效能：UI 流暢。  
- 創新：自動重新檢測。

---

## Case #16: 日誌與故障排除機制（收斂外部依賴問題）

### Problem Statement（問題陳述）
• 業務場景：使用者反映無法讀 RAW，需快速定位是安裝缺失、檔案問題或 Interop 例外。  
• 技術挑戰：建置可讀性高的日誌與故障排除路徑。  
• 影響範圍：支援效率、MTTR。  
• 複雜度評級：中

### Root Cause Analysis（根因分析）
• 直接原因：多種失敗來源未被清楚記錄。  
• 深層原因：  
- 架構：缺少集中式日誌。  
- 技術：未分類錯誤。  
- 流程：未定義回報格式。

### Solution Design（解決方案設計）
• 解決策略：TraceSource + 統一錯誤分類碼 + 使用者導向的診斷報告匯出。

• 實施步驟：
1) TraceSource 設定  
- 細節：資訊/警告/錯誤分級。  
- 時間：0.5 小時。
2) 診斷匯出  
- 細節：一鍵匯出日誌與環境資訊。  
- 時間：1 小時。

• 關鍵程式碼/設定：
```csharp
static readonly TraceSource ts = new TraceSource("DigitalCameraFiler");

void LogRawError(string code, string message, Exception ex = null)
{
    ts.TraceEvent(TraceEventType.Error, 0, $"[{code}] {message} {ex}");
    ts.Flush();
}
```

• 實際案例：文章點出外部資源不成熟，需良好故障排除。  
• 實作環境：.NET 2.0。  
• 實測數據：  
- 改善前：問題定位困難。  
- 改善後：錯誤歸因快速。  
- 改善幅度：MTTR 降低（定性）。

Learning Points
• 核心知識點：可觀測性、診斷設計。  
• 技能要求：  
- 必備：TraceSource。  
- 進階：結合事件檢視器。  
• 延伸思考：雲端遙測（後續）。  
• Practice：  
- 基礎：寫入與讀取日誌。  
- 進階：加入錯誤碼表。  
- 專案：一鍵匯出診斷包。  
• 評估：  
- 功能：完整記錄。  
- 品質：可讀性好。  
- 效能：低開銷。  
- 創新：自動化診斷。

---

## 案例分類

1) 按難度分類
• 入門級（適合初學者）：Case 2, 5, 8, 10, 12, 15  
• 中級（需要一定基礎）：Case 1, 4, 6, 7, 9, 11, 14, 16  
• 高級（需要深厚經驗）：Case 3

2) 按技術領域分類
• 架構設計類：Case 4, 7, 9, 12  
• 效能優化類：Case 14  
• 整合開發類：Case 1, 2, 8  
• 除錯診斷類：Case 3, 6, 11, 16  
• 安全防護/合規類：Case 13

3) 按學習目標分類
• 概念理解型：Case 5, 12, 13  
• 技能練習型：Case 2, 9, 10, 15  
• 問題解決型：Case 1, 4, 6, 7, 11, 16  
• 創新應用型：Case 3, 14

---

## 案例關聯圖（學習路徑建議）

• 建議先學：
- Case 5（確立最小可行功能，避免過度工程）
- Case 2（安裝/依賴檢查基本功）
- Case 1（核心整合：在 .NET 中讀取 RAW）

• 依賴關係：
- Case 1 依賴 Case 2（需先安裝/檢查 Viewer）
- Case 7、9 依賴 Case 1（RAW Reader）與 JPEG EXIF 能力
- Case 10 依賴 Case 7、9（統一輸出後才能歸檔）
- Case 6、16 橫切支援上述任意功能（容錯與診斷）
- Case 8、13 與部署與合規相關，搭配任何功能點進行
- Case 3 可作為探索與風險控管的進階補充
- Case 11 建立在 1/7/9 的功能之上
- Case 14 建立在 1/9 完成後進行優化
- Case 12、15 是環境與 UX 的護欄

• 完整學習路徑建議：
1) 需求對齊與 MVP：Case 5  
2) 安裝與依賴檢查：Case 2 → 合規：Case 13  
3) RAW 整合：Case 1 → 型別探索：Case 3  
4) 多格式策略：Case 7 + JPEG EXIF：Case 9  
5) 整合歸檔：Case 10  
6) 穩定性與測試：Case 6 → Case 11 → 診斷：Case 16  
7) 部署與相容：Case 8 + Case 12 + UI 護欄：Case 15  
8) 效能優化：Case 14

以上 16 個案例皆以原文的實際情境（.NET 工具、RAW 支援、使用 Microsoft RAW Viewer Interop、MSI 與先決條件說明）為基礎，拆解為可教學、可實作與可評估的練習主題。