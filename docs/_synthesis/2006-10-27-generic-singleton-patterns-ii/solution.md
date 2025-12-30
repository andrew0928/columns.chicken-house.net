---
layout: synthesis
title: "泛型 + Singleton Patterns (II)"
synthesis_type: solution
source_post: /2006/10/27/generic-singleton-patterns-ii/
redirect_from:
  - /2006/10/27/generic-singleton-patterns-ii/solution/
---

以下內容基於原文的泛型 Singleton 基底類別設計，系統化拆解並延伸出可直接實作與教學使用的 16 個問題解決案例。每一案皆以原文程式碼為核心，逐步補強在實務上會遇到的效能、測試、序列化、生命週期、DI 整合等議題。原文中的實例與程式片段均在「實際案例」或「關鍵程式碼/設定」中標示。

## Case #1: 以泛型基底封裝 Singleton 樣板碼

### Problem Statement（問題陳述）
業務場景：企業系統中有多個需要單例的服務（設定管理、快取、登錄器等），過往每個類別都重複撰寫 Singleton 樣板碼與同步邏輯，容易出錯且維護成本高。作者希望做出一個基底類別，把單例實作細節封裝起來，讓使用者只需繼承即可安全取得單例。
技術挑戰：設計可重用、型別安全、最少樣板碼的 Singleton 基底類別。
影響範圍：開發效率、程式碼一致性、維護成本與錯誤率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 各類別重複實作 Singleton，樣板碼多且易漏。
2. 開發者對 CLR 靜態初始化行為理解不一致，容易產生非必要鎖或競態。
3. 缺乏統一基底，導致每個類別用不同的寫法與命名。
深層原因：
- 架構層面：缺少模式抽象與統一規範。
- 技術層面：未善用泛型與 CRTP（Curiously Recurring Template Pattern）。
- 流程層面：未沉澱為函式庫，重複勞動。

### Solution Design（解決方案設計）
解決策略：以 CRTP 設計 GenericSingletonBase<T>，由靜態 readonly 欄位承擔建置唯一實例，對使用者暴露強型別的 Instance，只需繼承即可使用。

實施步驟：
1. 建立泛型基底類別
- 實作細節：使用 where T : GenericSingletonBase<T>, new() 與 public readonly static T Instance = new T();
- 所需資源：.NET（C# 2.0+）
- 預估時間：0.5 小時
2. 實作一個衍生單例類別
- 實作細節：class Foo : GenericSingletonBase<Foo> {}
- 所需資源：同上
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class GenericSingletonBase<T>
    where T : GenericSingletonBase<T>, new()
{
    // CLR 保證類型初始化的執行緒安全
    public readonly static T Instance = new T();
}

public class GenericSingletonImpl1 : GenericSingletonBase<GenericSingletonImpl1>
{
    public GenericSingletonImpl1()
    {
        Console.WriteLine("GenericSingletonImpl1.ctor()");
    }
}
```

實際案例：原文提供之 GenericSingletonBase<T> 與 GenericSingletonImpl1。
實作環境：.NET Framework 2.0+ 或 .NET 5/6+，C# 2.0+。
實測數據：
改善前：每個單例需撰寫樣板（私有建構子、靜態欄位、同步等）
改善後：僅需繼承與（可選）建構子
改善幅度：樣板碼定性下降，維護點集中於基底類別

Learning Points（學習要點）
核心知識點：
- CRTP 在 C# 的應用
- CLR 類型初始化的執行緒安全性
- 封裝重複樣板碼的設計思維
技能要求：
- 必備技能：C# 泛型、靜態成員、繼承
- 進階技能：.NET 型別初始化規則
延伸思考：
- 若需延遲載入、測試替換、DI、序列化，基底應如何演進？
- 如何確保真正單例不可被 new？
- 是否需要跨 AppDomain 或 ALC 的一致性？
Practice Exercise（練習題）
- 基礎練習：為兩個服務類別套用 GenericSingletonBase<T>
- 進階練習：將既有專案中的 3 個單例改為繼承基底
- 專案練習：撰寫一個可重用的 Utilities 套件，內含 5+ 個單例服務
Assessment Criteria（評估標準）
- 功能完整性（40%）：可用、可引用、多個類別可正常取 Instance
- 程式碼品質（30%）：命名一致、無重複樣板碼、清晰註解
- 效能優化（20%）：無不必要鎖、啟動開銷合理
- 創新性（10%）：對基底擴展（如診斷、日誌）設計良好

---

## Case #2: 以強型別 Instance 取代轉型需求

### Problem Statement（問題陳述）
業務場景：舊寫法的單例常透過物件型別或基底回傳，呼叫端需轉型後才能使用，導致程式碼「醜」且可讀性差。作者希望呼叫端直接寫 ClassName.Instance 即獲得正確型別變數，避免任何轉型。
技術挑戰：讓泛型基底同時保有衍生型別資訊，對外暴露強型別成員。
影響範圍：呼叫端可讀性、型別安全、編譯期錯誤偵測。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 回傳型別不具備具體衍生型別資訊。
2. 呼叫端需顯式轉型，易產生 InvalidCastException。
3. 缺乏編譯期型別檢查，錯誤延後到執行期。
深層原因：
- 架構層面：API 設計未對外提供精確型別。
- 技術層面：未利用泛型型參保留衍生型別。
- 流程層面：未制定 API 可讀性與安全性規範。

### Solution Design（解決方案設計）
解決策略：以 CRTP 讓基底類別的 static 成員直接是衍生型別 T，呼叫端以 T.Instance 即可得到強型別。

實施步驟：
1. 設計基底回傳 T
- 實作細節：public static readonly T Instance
- 所需資源：.NET
- 預估時間：0.5 小時
2. 呼叫端直接使用
- 實作細節：var s = MySingleton.Instance;
- 所需資源：同上
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class GenericSingletonBase<T> where T : GenericSingletonBase<T>, new()
{
    public readonly static T Instance = new T();
}

// 呼叫端
GenericSingletonImpl1 s = GenericSingletonImpl1.Instance;
```

實際案例：原文示範三次取得 Instance 均為強型別。
實作環境：同 Case #1。
實測數據：
改善前：每次存取需轉型，潛在執行期錯誤
改善後：零轉型，編譯期型別保證
改善幅度：轉型相關錯誤風險定性為 0

Learning Points（學習要點）
核心知識點：
- CRTP 與型別消除轉型
- 強型別 API 的可讀性與安全性
- 編譯期 vs 執行期錯誤差異
技能要求：
- 必備技能：泛型、靜態成員
- 進階技能：API 設計與可讀性
延伸思考：
- 是否需要將 Instance 改為屬性提供更多彈性？
- 若需懶載入與錯誤處理，欄位或屬性的選擇？
- 是否要加入診斷資訊（如建置時機記錄）？
Practice Exercise（練習題）
- 基礎：將舊單例回傳 object 的程式改為強型別
- 進階：設計一個通用 Result<T> 包裝並應用於 Instance 取得
- 專案：抽取既有 2 個框架庫的單例 API，統一為強型別介面
Assessment Criteria（評估標準）
- 功能完整性（40%）：呼叫端無轉型、編譯通過
- 程式碼品質（30%）：命名清楚、註解完整
- 效能優化（20%）：無多餘包裝、快速取得
- 創新性（10%）：改良可讀性與診斷能力

---

## Case #3: 利用 CLR 類型初始化，確保執行緒安全

### Problem Statement（問題陳述）
業務場景：在多執行緒環境中，傳統 Singleton 常需要鎖與雙重檢查，容易寫錯。希望以 CLR 的類型初始化特性，簡化並保證單例建置的執行緒安全。
技術挑戰：正確使用 static readonly 欄位與靜態建構子的行為保障。
影響範圍：正確性、效能（避免不必要鎖）、可維護性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 手寫鎖與雙重檢查易出錯。
2. 不了解 CLR 類型初始化只執行一次。
3. 多緒環境造成競態條件與不一致狀態。
深層原因：
- 架構層面：未將同步責任下放給 CLR 機制。
- 技術層面：缺乏對類型建置時機的掌握。
- 流程層面：無統一寫法標準化。

### Solution Design（解決方案設計）
解決策略：以 public static readonly T Instance = new T(); 或靜態建構子，交由 CLR 保證執行一次且鎖內建。

實施步驟：
1. 使用 static readonly 欄位
- 實作細節：CLR 在 Type 初始化期執行、保證一次性
- 所需資源：.NET
- 預估時間：0.5 小時
2. 驗證多緒行為
- 實作細節：啟動多緒同時存取 Instance，觀察建構子只執行一次
- 所需資源：單元測試或簡單 Console
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public class GenericSingletonBase<T>
    where T : GenericSingletonBase<T>, new()
{
    public readonly static T Instance = new T(); // Thread-safe by CLR type initializer
}
```

實際案例：原文實作採用 static readonly 欄位。
實作環境：同 Case #1。
實測數據：
改善前：手動鎖開銷與錯誤風險
改善後：零鎖、一次建置
改善幅度：同步複雜度定性為 0

Learning Points（學習要點）
核心知識點：
- CLR 類型初始化與執行緒安全
- static readonly 與 static ctor 差異
- 單例初始化時機掌控
技能要求：
- 必備技能：C# 靜態成員、執行緒基本觀念
- 進階技能：多緒測試
延伸思考：
- 若需延遲載入（Lazy），應如何調整？
- 初始化失敗如何處理與重試策略？
- 是否需記錄初始化時序與診斷？
Practice Exercise（練習題）
- 基礎：撰寫多緒測試驗證建構子只被呼叫一次
- 進階：將鎖實作版改為 static readonly 版並做效能比較
- 專案：在高併發服務中替換 3 個鎖版單例
Assessment Criteria（評估標準）
- 功能完整性（40%）：多緒下仍僅建置一次
- 程式碼品質（30%）：無冗餘同步、結構清晰
- 效能優化（20%）：鎖競爭消除
- 創新性（10%）：加入診斷與健康檢查

---

## Case #4: new() 約束破壞真正 Singleton 的風險與修正

### Problem Statement（問題陳述）
業務場景：基底以 where T : new() 造成衍生類別必須有 public 無參數建構子，因此任何人都能 new T()，違背「全域唯一」的經典 Singleton 要求，可能導致多實例錯誤。
技術挑戰：在保持易用性的前提下，阻止外部 new，確保存留唯一實例。
影響範圍：正確性與安全性（可能出現多個實例）、可維護性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. new() 約束要求 public ctor。
2. 外部程式可自行 new，繞過單例。
3. 無防護檢測或禁止。
深層原因：
- 架構層面：以語言約束取代執行時驗證。
- 技術層面：缺乏對非公開建構子的反射建置技巧。
- 流程層面：未明確規範「不得外部 new」。

### Solution Design（解決方案設計）
解決策略：移除 new() 約束，改用反射建立非公開建構子實例，並拒絕存在 public 無參數建構子的類型；衍生類別將建構子標為 private。

實施步驟：
1. 改以反射建置單例
- 實作細節：Activator.CreateInstance(typeof(T), nonPublic: true)
- 所需資源：System.Reflection
- 預估時間：1 小時
2. 強制檢查與文件化
- 實作細節：偵測 public 無參數建構子存在則擲例外
- 所需資源：同上
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public abstract class GenericSingletonBase<T>
    where T : GenericSingletonBase<T>
{
    private static readonly T _instance = CreateInstance();

    public static T Instance => _instance;

    private static T CreateInstance()
    {
        var type = typeof(T);
        // 不允許 public 無參數建構子，避免外部 new
        var publicCtor = type.GetConstructor(
            System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public,
            binder: null, types: Type.EmptyTypes, modifiers: null);
        if (publicCtor != null)
            throw new InvalidOperationException($"{type.Name} must not expose a public parameterless constructor.");

        // 建立非公開建構子
        return (T)Activator.CreateInstance(type, nonPublic: true);
    }
}

public sealed class SecureSingleton : GenericSingletonBase<SecureSingleton>
{
    private SecureSingleton() {} // 不可外部 new
}
```

實際案例：以原文基底為起點，修正為阻止 public ctor 的版本。
實作環境：.NET 4.5+（皆可）
實測數據：
改善前：可能出現多實例
改善後：外部 new 受阻，僅可由基底建立
改善幅度：多實例風險定性降為 0

Learning Points（學習要點）
核心知識點：
- new() 約束的限制與風險
- 反射建立非公開建構子
- API 合約檢查與防呆
技能要求：
- 必備技能：Reflection、例外處理
- 進階技能：API 合約與防護策略
延伸思考：
- 如何避免反射在 AOT 環境的限制？
- 是否要允許具參數建構子（透過 DI）？
- 需不需要 sealed 衍生類別？
Practice Exercise（練習題）
- 基礎：將原本 public ctor 改為 private，並驗證外部 new 失敗
- 進階：寫一個檢查器，掃描組件內所有單例類別是否符合規範
- 專案：將專案中 3 個單例切換到禁止 public ctor 的反射版基底
Assessment Criteria（評估標準）
- 功能完整性（40%）：外部 new 被阻止
- 程式碼品質（30%）：檢查清楚、錯誤訊息明確
- 效能優化（20%）：反射僅在初始化一次
- 創新性（10%）：加入 Roslyn Analyzer 或建置時檢查

---

## Case #5: 延遲載入（Lazy<T>）避免不必要的啟動成本

### Problem Statement（問題陳述）
業務場景：部分單例建置成本高（讀設定、建連線、加載快取），啟動時全建置造成延遲或資源占用。希望延遲到首次用到再建立，且仍維持執行緒安全。
技術挑戰：延遲載入、避免重入、確保唯一性。
影響範圍：啟動時間、記憶體占用、資源壓力。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. eager 初始化在未使用時也建置。
2. 建置成本高造成啟動延遲。
3. 缺乏安全的延遲機制。
深層原因：
- 架構層面：未區分熱路徑與冷路徑資源。
- 技術層面：不熟悉 Lazy<T> 與其執行緒模式。
- 流程層面：未做啟動分析。

### Solution Design（解決方案設計）
解決策略：以 Lazy<T> 包裝實例建置，使用 ExecutionAndPublication 保證一次建置與多緒安全。

實施步驟：
1. 引入 Lazy<T>
- 實作細節：new Lazy<T>(CreateInstance, LazyThreadSafetyMode.ExecutionAndPublication)
- 所需資源：System
- 預估時間：1 小時
2. 改以屬性存取
- 實作細節：public static T Instance => _lazy.Value;
- 所需資源：同上
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public abstract class GenericSingletonBase<T> where T : GenericSingletonBase<T>
{
    private static readonly Lazy<T> _lazy =
        new Lazy<T>(() => (T)Activator.CreateInstance(typeof(T), nonPublic: true),
                    System.Threading.LazyThreadSafetyMode.ExecutionAndPublication);

    public static T Instance => _lazy.Value;

    protected GenericSingletonBase() {}
}
```

實際案例：以原文架構改為延遲載入。
實作環境：.NET 4.0+。
實測數據：
改善前：啟動即建置全部單例
改善後：按需建置，未使用不建置
改善幅度：啟動時間定性下降，記憶體占用定性下降

Learning Points（學習要點）
核心知識點：
- Lazy<T> 與執行緒安全模式
- 啟動效能與資源延遲化
- 例外快取（Lazy 初始化例外的重用行為）
技能要求：
- 必備技能：Lazy<T> 使用
- 進階技能：初始化重試策略與錯誤處理
延伸思考：
- 初始化失敗是否應清空 Lazy 以允許重試？
- 是否提供預熱 API 以控制建置時機？
- 延遲載入對可觀測性與診斷影響？
Practice Exercise（練習題）
- 基礎：將 eager 版改為 Lazy 版
- 進階：加入重試與熔斷邏輯
- 專案：分析專案所有單例，決定哪些改為延遲載入
Assessment Criteria（評估標準）
- 功能完整性（40%）：首次存取建置、之後重用
- 程式碼品質（30%）：錯誤處理與註解
- 效能優化（20%）：啟動時間改善
- 創新性（10%）：預熱與診斷設計

---

## Case #6: 防止建構子內部意外存取 Instance 的重入風險

### Problem Statement（問題陳述）
業務場景：衍生類別建構子若在初始化中呼叫 T.Instance（直接或間接），會導致 re-entrancy，造成部分初始化或例外。需偵測並避免此反模式。
技術挑戰：偵測重入、清楚錯誤訊息、避免半成品狀態。
影響範圍：正確性、穩定性、可診斷性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 建構子中不當呼叫 Instance。
2. static 欄位賦值流程與建構子呼叫時序錯綜。
3. 無防護與診斷。
深層原因：
- 架構層面：初始化邏輯分層不明。
- 技術層面：類型初始化時序不熟。
- 流程層面：缺少反模式檢查。

### Solution Design（解決方案設計）
解決策略：以 ThreadStatic 旗標標記建置中狀態，若偵測到建構子期間再取 Instance，立即擲出清楚例外。

實施步驟：
1. 建置防重入機制
- 實作細節：ThreadStatic 布林旗標
- 所需資源：System
- 預估時間：1 小時
2. 加入明確錯誤訊息
- 實作細節：InvalidOperationException 說明避免的寫法
- 所需資源：同上
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public abstract class GenericSingletonBase<T> where T : GenericSingletonBase<T>
{
    [ThreadStatic] private static bool _constructing;

    private static T CreateInstance()
    {
        if (_constructing)
            throw new InvalidOperationException($"Re-entrant initialization detected on {typeof(T).Name}. Do not access Instance inside constructor.");
        try
        {
            _constructing = true;
            return (T)Activator.CreateInstance(typeof(T), nonPublic: true);
        }
        finally { _constructing = false; }
    }

    private static readonly Lazy<T> _lazy =
        new Lazy<T>(CreateInstance, System.Threading.LazyThreadSafetyMode.ExecutionAndPublication);

    public static T Instance => _lazy.Value;
}
```

實際案例：延伸原文方案加入防重入。
實作環境：.NET 4.0+。
實測數據：
改善前：可能半初始化或隨機例外
改善後：明確阻止錯誤用法
改善幅度：此類錯誤風險定性降為 0

Learning Points（學習要點）
核心知識點：
- 重入偵測
- 建構子與靜態初始化時序
- 診斷友善錯誤
技能要求：
- 必備技能：例外處理
- 進階技能：執行緒區域狀態管理
延伸思考：
- 是否需在建置後提供一個 Initialize 方法取代在 ctor 的重邏輯？
- 加入事件或回呼以隔離重邏輯？
- 靜態分析工具能提前警告嗎？
Practice Exercise（練習題）
- 基礎：撰寫會重入的錯誤範例並驗證防護
- 進階：將重邏輯移到 PostConstruct 回呼
- 專案：為 2 個高風險單例加入防重入保護
Assessment Criteria（評估標準）
- 功能完整性（40%）：可偵測並阻止重入
- 程式碼品質（30%）：錯誤訊息明確
- 效能優化（20%）：無額外顯著開銷
- 創新性（10%）：提供替代初始化流程

---

## Case #7: 單例的資源釋放與應用程式關閉整合

### Problem Statement（問題陳述）
業務場景：單例通常長期存活，若持有非受控資源（檔案、Socket、Db 連線池），需要正確釋放，並在程序結束時確保清理。否則可能導致資源外洩。
技術挑戰：生命週期管理、I/O 清理、應用程式關閉的掛鉤。
影響範圍：穩定性、資源使用、監控。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單例未實作 IDisposable。
2. 缺少關閉事件處理。
3. 忽略釋放順序與相依。
深層原因：
- 架構層面：未定義資源擁有者。
- 技術層面：未處理 AppDomain/Host 關閉鉤子。
- 流程層面：缺少關閉測試。

### Solution Design（解決方案設計）
解決策略：基底實作 IDisposable 與虛擬 Dispose，並在 ProcessExit/DomainUnload 注入清理；在 ASP.NET Core 中可使用 IHostApplicationLifetime。

實施步驟：
1. 基底支援釋放
- 實作細節：virtual Dispose、釋放事件
- 所需資源：System
- 預估時間：1 小時
2. 關閉鉤子
- 實作細節：訂閱 ProcessExit，呼叫 Instance.Dispose()
- 所需資源：同上
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public abstract class DisposableSingletonBase<T> : GenericSingletonBase<T>, IDisposable
    where T : DisposableSingletonBase<T>
{
    static DisposableSingletonBase()
    {
        AppDomain.CurrentDomain.ProcessExit += (_, __) =>
        {
            if (_disposed) return;
            (Instance as IDisposable)?.Dispose();
        };
    }

    private static bool _disposed;
    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        DisposeCore();
        GC.SuppressFinalize(this);
    }
    protected virtual void DisposeCore() {}
}
```

實際案例：在原文基底上擴充為可釋放單例。
實作環境：.NET Framework/.NET Core。
實測數據：
改善前：關閉時資源可能未釋放
改善後：可預期釋放路徑
改善幅度：資源外洩風險定性下降

Learning Points（學習要點）
核心知識點：
- IDisposable 模式
- 應用程式關閉事件
- 釋放順序與安全
技能要求：
- 必備技能：IDisposable
- 進階技能：關閉流程測試
延伸思考：
- 在 ASP.NET Core 應改用 DI 管理生命週期？
- Dispose 的多執行緒競態處理？
- 釋放失敗的重試與日誌？
Practice Exercise（練習題）
- 基礎：建立一個寫檔單例，驗證關閉釋放
- 進階：模擬釋放例外並記錄日誌
- 專案：審視 3 個單例的資源釋放設計
Assessment Criteria（評估標準）
- 功能完整性（40%）：關閉時成功釋放
- 程式碼品質（30%）：Dispose 模式正確
- 效能優化（20%）：釋放成本可控
- 創新性（10%）：整合日誌/監控

---

## Case #8: 測試可替換的單例（SetTestInstance/Reset）

### Problem Statement（問題陳述）
業務場景：單元測試需要替換單例為假物件或測試替身，但 readonly static 欄位不可改，導致測試難以撰寫或需用私有反射黑魔法。
技術挑戰：在生產保持安全，在測試可替換。
影響範圍：可測試性、CI/CD 效率、設計可維護性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. readonly static 封死替換入口。
2. 缺少注入點或替換 API。
3. 測試不得不使用反射繞過。
深層原因：
- 架構層面：全域狀態難測。
- 技術層面：未提供測試後門。
- 流程層面：缺少測試先行設計。

### Solution Design（解決方案設計）
解決策略：於基底提供 internal SetTestInstance/Reset API（受 InternalsVisibleTo 或條件編譯守護），測試可注入替身，生產不暴露。

實施步驟：
1. 提供替換 API
- 實作細節：internal static void SetTestInstance(T fake)
- 所需資源：InternalsVisibleTo
- 預估時間：1 小時
2. 加入 Reset
- 實作細節：清回預設 Lazy 建置
- 所需資源：同上
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public abstract class TestableSingletonBase<T> where T : TestableSingletonBase<T>
{
    private static Lazy<T> _lazy = new Lazy<T>(() => (T)Activator.CreateInstance(typeof(T), true));
    private static T _override;

    public static T Instance => _override ?? _lazy.Value;

    internal static void SetTestInstance(T instance) => _override = instance;
    internal static void Reset() { _override = null; _lazy = new Lazy<T>(() => (T)Activator.CreateInstance(typeof(T), true)); }
}
// AssemblyInfo.cs
// [assembly: InternalsVisibleTo("Your.Tests")]
```

實際案例：在原文模式上加入測試替換能力。
實作環境：.NET。
實測數據：
改善前：需私有反射繞過，易碎
改善後：一行替換，測試清晰
改善幅度：測試開發效率定性提升

Learning Points（學習要點）
核心知識點：
- InternalsVisibleTo
- 測試替身注入
- 全域狀態測試策略
技能要求：
- 必備技能：單元測試
- 進階技能：測試隔離與重設
延伸思考：
- 是否以 DI 完全取代單例？
- 測試後必須 Reset 的紀律如何保證？
- 多緒下 override 的可見性？
Practice Exercise（練習題）
- 基礎：為一個單例加入 SetTestInstance 並撰寫測試
- 進階：多緒測試下替換與重設
- 專案：將 2 個難測單例改為可替換方案
Assessment Criteria（評估標準）
- 功能完整性（40%）：測試可替換、可重設
- 程式碼品質（30%）：權限控制明確
- 效能優化（20%）：無非必要鎖
- 創新性（10%）：測試輔助工具封裝

---

## Case #9: 與 DI 容器整合的單例門面

### Problem Statement（問題陳述）
業務場景：在現代 .NET 應用，建議以 DI 管理生命週期（AddSingleton），而非硬編碼全域單例。既有程式使用 GenericSingletonBase<T>，希望在不大改的前提下與 DI 整合。
技術挑戰：相容舊有 API，同時可交由 DI 託管。
影響範圍：架構一致性、可測試性、擴展性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態單例難以注入與替換。
2. DI 生命週期管理優勢無法使用。
3. 兩者並存導致重複狀態。
深層原因：
- 架構層面：過度倚賴全域狀態。
- 技術層面：缺少橋接層。
- 流程層面：遷移策略缺位。

### Solution Design（解決方案設計）
解決策略：提供可選服務提供者通道，若 ServiceProvider 已設定則由 DI 解析，否則回退至內建 Lazy 單例。

實施步驟：
1. 提供 ServiceProvider 設定
- 實作細節：internal static IServiceProvider Provider
- 所需資源：Microsoft.Extensions.DependencyInjection.Abstractions
- 預估時間：1 小時
2. Instance 走 DI 或回退
- 實作細節：Provider?.GetService(typeof(T)) ?? Lazy.Value
- 所需資源：同上
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public abstract class DiAwareSingletonBase<T> where T : DiAwareSingletonBase<T>
{
    internal static IServiceProvider? ServiceProvider { get; set; }

    private static readonly Lazy<T> _lazy =
        new Lazy<T>(() => (T)Activator.CreateInstance(typeof(T), true));

    public static T Instance =>
        (ServiceProvider?.GetService(typeof(T)) as T) ?? _lazy.Value;
}
```

實際案例：在原文基底外包一層 DI 感知能力。
實作環境：.NET、Microsoft.Extensions.DependencyInjection。
實測數據：
改善前：無法享受 DI 的替換與設定
改善後：可在組態切換至 DI 託管
改善幅度：可測試性與彈性定性提升

Learning Points（學習要點）
核心知識點：
- AddSingleton 與靜態單例差異
- 門面與回退策略
- 組態切換
技能要求：
- 必備技能：DI 基本
- 進階技能：抽象與相容性設計
延伸思考：
- 長期是否應全面改為 DI？
- DI 容器切換成本？
- 組態注入敏感資訊的處理？
Practice Exercise（練習題）
- 基礎：將一個單例改為 DI 可控
- 進階：在測試以 DI 提供替身，生產用內建 Lazy
- 專案：規劃單例向 DI 遷移藍圖
Assessment Criteria（評估標準）
- 功能完整性（40%）：DI/內建路徑皆可用
- 程式碼品質（30%）：依賴清晰、無循環
- 效能優化（20%）：解析成本合理
- 創新性（10%）：動態切換策略

---

## Case #10: 序列化/反序列化保持單例語意

### Problem Statement（問題陳述）
業務場景：單例若可序列化，反序列化時可能產生新實例，破壞唯一性。需確保反序列化回復為 Instance。
技術挑戰：ISerializable/IObjectReference 正確實作。
影響範圍：正確性、資料一致性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 預設序列化會建新物件。
2. 未實作特殊回復邏輯。
3. 無測試覆蓋。
深層原因：
- 架構層面：缺少序列化策略。
- 技術層面：不了解 IObjectReference。
- 流程層面：跨程序傳輸未被納入設計。

### Solution Design（解決方案設計）
解決策略：在基底實作 ISerializable 與 IObjectReference，GetRealObject 回傳 Instance，並確保衍生標註 [Serializable]。

實施步驟：
1. 基底實作序列化介面
- 實作細節：GetObjectData 空實作，GetRealObject 回 Instance
- 所需資源：System.Runtime.Serialization
- 預估時間：1.5 小時
2. 測試
- 實作細節：BinaryFormatter/其他格式測試（注意安全）
- 所需資源：測試框架
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
[Serializable]
public abstract class SerializableSingletonBase<T> :
    GenericSingletonBase<T>, System.Runtime.Serialization.ISerializable, System.Runtime.Serialization.IObjectReference
    where T : SerializableSingletonBase<T>
{
    protected SerializableSingletonBase() {}

    protected SerializableSingletonBase(System.Runtime.Serialization.SerializationInfo info,
                                        System.Runtime.Serialization.StreamingContext context) {}

    public void GetObjectData(System.Runtime.Serialization.SerializationInfo info,
                              System.Runtime.Serialization.StreamingContext context) {}

    public object GetRealObject(System.Runtime.Serialization.StreamingContext context) => Instance;
}
```

實際案例：原文基底延伸為序列化安全。
實作環境：.NET。
實測數據：
改善前：反序列化產生新實例
改善後：反序列化回覆為 Instance
改善幅度：破壞唯一性的風險定性為 0

Learning Points（學習要點）
核心知識點：
- ISerializable/IObjectReference
- 單例與序列化語意
- 二進位序列化風險（安全）
技能要求：
- 必備技能：序列化 API
- 進階技能：安全考量
延伸思考：
- 在 JSON/XML 下通常不應序列化單例本體，而序列化其狀態
- 使用 System.Text.Json Converter 自訂行為
- 避免 BinaryFormatter（已過時不安全）
Practice Exercise（練習題）
- 基礎：對單例進行序列化/反序列化並驗證同一參考
- 進階：實作 System.Text.Json 自訂轉換器處理單例
- 專案：審核專案序列化使用點，避免序列化單例本體
Assessment Criteria（評估標準）
- 功能完整性（40%）：反序列化維持唯一
- 程式碼品質（30%）：實作簡潔、註解清楚
- 效能優化（20%）：序列化成本合理
- 創新性（10%）：提供安全的序列化策略建議

---

## Case #11: AppDomain 與 AssemblyLoadContext 的單例邊界

### Problem Statement（問題陳述）
業務場景：在 .NET Framework（AppDomain）或 .NET Core（ALC）中，單例是「每域/每載入上下文一份」。若外掛或多載入上下文，可能出現多個單例，需釐清與設計對策。
技術挑戰：識別邊界、跨界共享策略、避免隱性多實例。
影響範圍：正確性、記憶體使用、外掛模型。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態在每個 AppDomain/ALC 各有一份。
2. 外掛動態載入造成多上下文。
3. 缺乏跨界同步。
深層原因：
- 架構層面：未定義跨域資源治理。
- 技術層面：不熟悉 ALC 行為。
- 流程層面：缺少外掛與版本管理策略。

### Solution Design（解決方案設計）
解決策略：明確標註「單例的範圍」為進程/域/ALC；跨界共享時改以 IPC/服務端點；或限制外掛在共享 ALC。

實施步驟：
1. 宣告準則與檢測
- 實作細節：記錄與暴露目前 ALC/Domain Id
- 所需資源：System.Runtime.Loader
- 預估時間：1 小時
2. 跨界策略
- 實作細節：用 IPC/RPC 或集中服務取代跨域單例
- 所需資源：依選型
- 預估時間：視情況

關鍵程式碼/設定：
```csharp
public static class SingletonDiagnostics
{
#if NETCOREAPP
    public static string CurrentContext => System.Runtime.Loader.AssemblyLoadContext.GetLoadContext(typeof(SingletonDiagnostics).Assembly)?.Name ?? "Default";
#else
    public static string CurrentContext => AppDomain.CurrentDomain.FriendlyName;
#endif
}
```

實際案例：在單例內記錄建立時的上下文資訊，供診斷。
實作環境：.NET Framework/.NET Core。
實測數據：
改善前：誤以為全進程唯一
改善後：清楚範圍並採取對策
改善幅度：跨域錯誤風險定性下降

Learning Points（學習要點）
核心知識點：
- AppDomain/ALC 行為
- 單例範圍定義
- 外掛模型策略
技能要求：
- 必備技能：平台知識
- 進階技能：IPC/RPC 設計
延伸思考：
- 宿主是否能統一在 Default ALC？
- 使用單例門面代理跨界？
- 避免 Assembly 衝突與幽靈多實例
Practice Exercise（練習題）
- 基礎：列印單例的 ALC/Domain Id
- 進階：在兩個 ALC 各載入一份並觀察
- 專案：為外掛系統定義單例範圍與共享策略
Assessment Criteria（評估標準）
- 功能完整性（40%）：能辨識範圍
- 程式碼品質（30%）：診斷清楚
- 效能優化（20%）：無多餘開銷
- 創新性（10%）：提出可行共享模式

---

## Case #12: 事件訂閱導致的記憶體保留與弱事件策略

### Problem Statement（問題陳述）
業務場景：單例長期存活，若訂閱其他短命物件的事件或曝露事件被大量訂閱，易造成記憶體保留（訂閱者未解除）。需提供弱事件或安全解除策略。
技術挑戰：避免記憶體洩漏、提供安全 API。
影響範圍：穩定性、記憶體足跡。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單例持有強參考委派。
2. 訂閱者未解除訂閱。
3. 無弱事件封裝。
深層原因：
- 架構層面：事件生命週期未定義。
- 技術層面：對 WeakReference 應用不足。
- 流程層面：無解除規範。

### Solution Design（解決方案設計）
解決策略：封裝弱事件或提供 SafeSubscribe/Unsubscribe；於 Dispose 中清理事件。

實施步驟：
1. 封裝弱事件
- 實作細節：弱參考列表與清理
- 所需資源：WeakReference
- 預估時間：2 小時
2. 指南與測試
- 實作細節：文件與單元測試
- 所需資源：測試框架
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public class WeakEvent<THandler> where THandler : class
{
    private readonly List<WeakReference> _handlers = new();

    public void Add(THandler handler) => _handlers.Add(new WeakReference(handler));
    public void Raise(Action<THandler> invoker)
    {
        _handlers.RemoveAll(wr => !wr.IsAlive);
        foreach (var wr in _handlers)
            if (wr.Target is THandler h) invoker(h);
    }
}
```

實際案例：在長命單例上以 WeakEvent 暴露事件。
實作環境：.NET。
實測數據：
改善前：記憶體未釋放
改善後：訂閱者釋放不再被單例保留
改善幅度：記憶體洩漏風險定性下降

Learning Points（學習要點）
核心知識點：
- 事件與記憶體保留
- WeakReference 應用
- Dispose 中解除事件
技能要求：
- 必備技能：委派/事件
- 進階技能：弱事件封裝
延伸思考：
- 使用內建 WeakEventManager（WPF）？
- 以 Observable/Reactive 取代事件？
- 事件風險告警與分析工具？
Practice Exercise（練習題）
- 基礎：改為弱事件並驗證 GC 可回收訂閱者
- 進階：壓測大量訂閱/解除
- 專案：審視 2 個單例的事件暴露策略
Assessment Criteria（評估標準）
- 功能完整性（40%）：不保留已釋放訂閱者
- 程式碼品質（30%）：封裝清晰
- 效能優化（20%）：Raise 成本可控
- 創新性（10%）：事件監控工具

---

## Case #13: 型別約束誤用的防呆（CRTP 自我檢查）

### Problem Statement（問題陳述）
業務場景：CRTP 要求衍生類別將自身作為泛型參數，若誤寫成其他型別或多重繼承層級錯置，可能造成難以理解的行為或例外。
技術挑戰：在執行期進一步防呆提示錯誤用法。
影響範圍：正確性、開發體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 編譯器僅檢查繼承約束，無法驗證 T==實際型別。
2. 複雜繼承結構易誤用。
3. 缺少明確錯誤訊息。
深層原因：
- 架構層面：CRTP 應用規範未文件化。
- 技術層面：未做執行期自檢。
- 流程層面：缺少範本與範例。

### Solution Design（解決方案設計）
解決策略：於基底建構子或靜態初始化加入檢查，若 typeof(T) != GetType()，明確擲出例外。

實施步驟：
1. 加入檢查
- 實作細節：if (GetType() != typeof(T)) throw...
- 所需資源：無
- 預估時間：0.5 小時
2. 文件化範例
- 實作細節：說明正確/錯誤範例
- 所需資源：文件
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
protected GenericSingletonBase()
{
    if (GetType() != typeof(T))
        throw new InvalidOperationException($"Generic parameter mismatch. Expected {typeof(T).Name} to be {GetType().Name}.");
}
```

實際案例：在原文基底上強化自我檢查。
實作環境：.NET。
實測數據：
改善前：誤用可能延後才發現
改善後：立即擲例外提示
改善幅度：誤用風險定性下降

Learning Points（學習要點）
核心知識點：
- CRTP 合約保護
- 與編譯期/執行期檢查的互補
- 易用性提升
技能要求：
- 必備技能：例外處理
- 進階技能：設計防呆訊息
延伸思考：
- 可否用 Analyzer 在編譯期預警？
- 在大型繼承樹如何組織 CRTP？
- 何時應避免 CRTP？
Practice Exercise（練習題）
- 基礎：故意誤用並觀察錯誤訊息
- 進階：撰寫簡易 Source Generator/Analyzer 檢查
- 專案：將檢查加入現有基底並文件化
Assessment Criteria（評估標準）
- 功能完整性（40%）：可識別誤用
- 程式碼品質（30%）：訊息清晰
- 效能優化（20%）：檢查成本低
- 創新性（10%）：工具鏈整合

---

## Case #14: 高成本初始化的控制（預熱/顯式 Initialize）

### Problem Statement（問題陳述）
業務場景：某些單例建置耗時，延遲到第一次用時才初始化可能造成尖峰延遲；相反地，啟動時建置又拉長啟動時間。需要策略化控制建置時機。
技術挑戰：可配置的初始化策略、觀測與預熱。
影響範圍：啟動體驗、延遲尾端、容量規劃。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 初始化成本高、資源多。
2. 啟動/首用兩難。
3. 缺少預熱機制。
深層原因：
- 架構層面：初始化與業務路徑耦合。
- 技術層面：缺乏觀測資料。
- 流程層面：無啟動/預熱流程。

### Solution Design（解決方案設計）
解決策略：保留 Lazy 為預設，提供顯式 Initialize/Prewarm API 與計時診斷，讓部署可選擇啟動即預熱或按需。

實施步驟：
1. 提供 Initialize/Prewarm
- 實作細節：存取 Instance 觸發建置並記錄耗時
- 所需資源：Stopwatch、日誌
- 預估時間：1 小時
2. 配置化策略
- 實作細節：讀組態決定預熱清單
- 所需資源：設定系統
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public static class SingletonPrewarmer
{
    public static TimeSpan Prewarm<T>() where T : GenericSingletonBase<T>
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        _ = ((GenericSingletonBase<T>)null).GetType(); // 只是示意; 實務直接觸發 Instance
        var _ = (T)typeof(T).GetProperty("Instance").GetValue(null);
        sw.Stop();
        return sw.Elapsed;
    }
}
```

實際案例：在部署腳本或啟動程式碼預熱關鍵單例。
實作環境：.NET。
實測數據：
改善前：首用長尾延遲
改善後：首用延遲下降，啟動可控上升
改善幅度：延遲分佈更平滑（定性）

Learning Points（學習要點）
核心知識點：
- 預熱策略
- 觀測與計時
- 啟動/運行時權衡
技能要求：
- 必備技能：Stopwatch、設定
- 進階技能：容量與延遲分析
延伸思考：
- 以背景工作分批預熱？
- 熱點分析自動決定預熱清單？
- 可否在部署健康檢查中內建預熱？
Practice Exercise（練習題）
- 基礎：為一個單例加入 Prewarm 並記錄耗時
- 進階：根據流量模式切換策略
- 專案：建立預熱工具，覆蓋 3 個高成本單例
Assessment Criteria（評估標準）
- 功能完整性（40%）：能顯式預熱
- 程式碼品質（30%）：介面簡潔
- 效能優化（20%）：延遲尾端改善
- 創新性（10%）：智慧預熱策略

---

## Case #15: 版本演進與二進位相容的基底設計

### Problem Statement（問題陳述）
業務場景：基底類別一旦廣泛使用，後續變更（欄位、方法、相依）可能破壞相容性。需設計安全的演進策略。
技術挑戰：公開 API 穩定、避免破壞性變更。
影響範圍：相容性、升級成本、維護效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 對外 API 暴露過多。
2. 破壞性變更無門檻。
3. 缺乏版本策略。
深層原因：
- 架構層面：未定義 public surface 最小化。
- 技術層面：缺少 API 兼容檢查工具。
- 流程層面：版本化與發佈治理不足。

### Solution Design（解決方案設計）
解決策略：最小化公開面、以 protected virtual 擴展點、以新類型/新命名空間演進；導入 API Comparer 工具並建立 SemVer 政策。

實施步驟：
1. 穩定 API
- 實作細節：審視 public 成員、改 internal 或 protected
- 所需資源：API 檢視
- 預估時間：2 小時
2. 導入工具與政策
- 實作細節：APICompat 或 Roslyn Analyzer、SemVer
- 所需資源：工具鏈
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
// 範例：將可變動點以 protected virtual 提供
public abstract class EvolvingSingletonBase<T> where T : EvolvingSingletonBase<T>
{
    protected virtual void OnAfterCreate() { }
}
```

實際案例：以原文基底為核心，將擴展點改為虛擬方法，避免破壞性變更。
實作環境：.NET、API 比對工具。
實測數據：
改善前：升級常破壞
改善後：升級平滑、風險可控
改善幅度：破壞性變更風險定性下降

Learning Points（學習要點）
核心知識點：
- API Surface 最小化
- 擴展點設計
- 版本化策略
技能要求：
- 必備技能：API 設計
- 進階技能：工具自動化驗證
延伸思考：
- 提供 Obsolete 指引遷移
- 發佈節奏與相容承諾
- 文檔與 Changelog
Practice Exercise（練習題）
- 基礎：審視基底 API 並收斂 public 面
- 進階：導入 API 比對工具於 CI
- 專案：規劃基底 v2 升級指引
Assessment Criteria（評估標準）
- 功能完整性（40%）：無功能缺失
- 程式碼品質（30%）：API 清晰、文件完備
- 效能優化（20%）：無引入額外負擔
- 創新性（10%）：自動化檢查流程

---

## Case #16: 記錄建置行為與可觀測性（診斷友善 Singleton）

### Problem Statement（問題陳述）
業務場景：在複雜系統中，需知道單例何時被建置、耗時、呼叫堆疊，以便除錯與優化。原文示例以 Console.WriteLine 顯示建構子呼叫，實務需更完整的可觀測性。
技術挑戰：低入侵地收集診斷資訊、不影響效能。
影響範圍：除錯效率、效能優化。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少建置時序資訊。
2. 難以重現初始化問題。
3. Console 日誌不可用於生產。
深層原因：
- 架構層面：無觀測策略。
- 技術層面：對 Activity/ETW/EventSource 應用不足。
- 流程層面：無標準化日誌。

### Solution Design（解決方案設計）
解決策略：在基底加上可選診斷鉤子，透過 ILogger/EventSource 發送「初始化開始/結束/例外」事件與耗時。

實施步驟：
1. 注入診斷介面
- 實作細節：可選 ILogger 或 EventSource
- 所需資源：Logging Abstractions
- 預估時間：1 小時
2. 發送事件
- 實作細節：Stopwatch 計時，記錄型別名與堆疊摘要
- 所需資源：同上
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public interface ISingletonDiagnostics
{
    void InitStarted(Type t);
    void InitSucceeded(Type t, TimeSpan elapsed);
    void InitFailed(Type t, Exception ex);
}

public abstract class ObservableSingletonBase<T> where T : ObservableSingletonBase<T>
{
    public static ISingletonDiagnostics? Diagnostics { get; set; }

    private static T CreateInstance()
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        Diagnostics?.InitStarted(typeof(T));
        try
        {
            var instance = (T)Activator.CreateInstance(typeof(T), true);
            sw.Stop();
            Diagnostics?.InitSucceeded(typeof(T), sw.Elapsed);
            return instance;
        }
        catch (Exception ex)
        {
            Diagnostics?.InitFailed(typeof(T), ex);
            throw;
        }
    }
}
```

實際案例：將原文 Console.WriteLine 升級為標準化診斷。
實作環境：.NET、Logging。
實測數據：
改善前：難追蹤建置問題
改善後：可量測與定位
改善幅度：除錯時間定性下降

Learning Points（學習要點）
核心知識點：
- 可觀測性三支柱之一：日誌
- 低入侵診斷
- Activity/TraceId（可再擴充）
技能要求：
- 必備技能：ILogger/EventSource
- 進階技能：端到端追蹤
延伸思考：
- 結合 Activity 與分佈式追蹤
- 以 ETW/PerfView 分析
- 設計診斷開關避免生產開銷
Practice Exercise（練習題）
- 基礎：實作簡易 Diagnostics 並驗證事件
- 進階：注入 ILogger 串接 Serilog
- 專案：為 3 個關鍵單例加入診斷
Assessment Criteria（評估標準）
- 功能完整性（40%）：事件完整
- 程式碼品質（30%）：低入侵、清晰
- 效能優化（20%）：開銷受控
- 創新性（10%）：追蹤整合

---

案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #1 封裝樣板碼
  - Case #2 強型別存取
  - Case #3 CLR 初始化執行緒安全
  - Case #16 可觀測性
- 中級（需要一定基礎）
  - Case #4 new() 約束修正
  - Case #5 延遲載入
  - Case #6 防重入
  - Case #7 資源釋放
  - Case #8 測試替換
  - Case #9 DI 整合
  - Case #10 序列化語意
  - Case #12 事件與弱參考
  - Case #14 高成本初始化策略
  - Case #15 版本演進
- 高級（需要深厚經驗）
  - Case #11 AppDomain/ALC 邊界

2. 按技術領域分類
- 架構設計類：#1, #4, #9, #11, #14, #15
- 效能優化類：#3, #5, #14, #16
- 整合開發類：#9, #10, #16
- 除錯診斷類：#6, #11, #16
- 安全防護類（語意/正確性保障）：#4, #6, #10, #12, #13

3. 按學習目標分類
- 概念理解型：#1, #2, #3
- 技能練習型：#5, #6, #7, #8, #12, #16
- 問題解決型：#4, #9, #10, #11, #14
- 創新應用型：#15（版本演進）、#16（診斷）

案例關聯圖（學習路徑建議）
- 先學順序（基礎打底）：
  1) Case #1 封裝樣板碼
  2) Case #2 強型別存取
  3) Case #3 CLR 初始化安全
- 接著學（核心能力）：
  4) Case #5 延遲載入
  5) Case #4 new() 約束修正（守住真正單例）
  6) Case #6 防重入
- 擴展與工程化：
  7) Case #7 資源釋放
  8) Case #8 測試替換
  9) Case #9 DI 整合
  10) Case #10 序列化語意
- 進階專題：
  11) Case #12 事件弱參考與洩漏防治
  12) Case #11 AppDomain/ALC 邊界與外掛
  13) Case #14 初始化策略與預熱
- 長期維運：
  14) Case #16 可觀測性
  15) Case #15 版本演進與相容性

依賴關係說明：
- #4 依賴 #1-#3（理解基底與初始化）；
- #5 依賴 #3（多緒安全）；
- #6 依賴 #4/#5（初始化流程）；
- #9 依賴 #1/#2（API）；
- #10 依賴 #1（基底設計）；
- #11 依賴 #1（單例語意）；
- #14 依賴 #5（Lazy）；
- #16 可併入任意案例用於觀測。

完整學習路徑建議：
- 基礎（#1→#2→#3）掌握模式與型別安全；
- 強化（#5→#4→#6）掌握初始化策略與正確性；
- 工程化（#7→#8→#9→#10）涵蓋生命週期、測試與整合；
- 進階（#12→#11→#14）面向洩漏、外掛邊界與效能；
- 維運（#16→#15）落實觀測與版本治理。

備註
- 原文核心方案（GenericSingletonBase<T> 與強型別 Instance）對應 Case #1–#3、#16 的起點；其餘案例為在實務工程場景下常見的延伸與完善。若需精準量化數據，建議依專案場景撰寫對應的基準測試與指標收集。