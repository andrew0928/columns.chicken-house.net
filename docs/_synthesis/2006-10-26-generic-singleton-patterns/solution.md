---
layout: synthesis
title: "泛型 + Singleton Patterns"
synthesis_type: solution
source_post: /2006/10/26/generic-singleton-patterns/
redirect_from:
  - /2006/10/26/generic-singleton-patterns/solution/
postid: 2006-10-26-generic-singleton-patterns
---

以下內容基於文章「泛型 + Singleton Patterns」中的情境與程式片段，將其拆解為可教學、可練習、可評估的結構化案例。部分案例補充了文章中已明確提到的解決方向（繼承 + 泛型）以形成完整可落地的實作方案；對於文章未提供之量化數據，以下均以質化成效說明。

## Case #1: 單一類別的基本 Singleton 實作

### Problem Statement（問題陳述）
業務場景：在一個 .NET 2.0 團隊專案中，有部分服務類別（如設定存取、資源管理）在應用程式生命週期中應該只有唯一實例，以避免狀態不一致與資源重複初始化。開發者首先採用最常見的單例寫法，直接在類別內用 static 欄位緩存唯一實例，並於存取器中延遲建立。
技術挑戰：如何正確建立唯一實例並隱藏建構子，避免外部 new。
影響範圍：若錯誤建立多個實例，將造成資源競爭與設定異常。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少對建構子的保護容易被誤用 new。
2. 延遲建立的 get 存取器若無同步策略，潛在執行緒安全問題（文章未談，但常見）。
3. 方案僅適用單一類別，跨多類別時會出現重複樣板程式。
深層原因：
- 架構層面：沒有抽象出共用的「單例產生流程」。
- 技術層面：靜態成員與型別耦合，無法重用。
- 流程層面：缺乏統一樣式與審查，易散落多份近似實作。

### Solution Design（解決方案設計）
解決策略：於單一類別內封裝單例，隱藏建構子並透過 static 屬性延遲建立，保證只在首次需要時建立實例，同時作為後續重構到泛型/繼承方案的基準版本。

實施步驟：
1. 封裝建構子
- 實作細節：將建構子設為 private。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 提供延遲建立的存取器
- 實作細節：以 static 欄位保存；在 getter 檢查 null 則 new。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public class SampleSingletonClass
{
    private static SampleSingletonClass _instance = null;
    public static SampleSingletonClass Instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = new SampleSingletonClass();
            }
            return _instance;
        }
    }
    private SampleSingletonClass() { /* ctor code */ }
}
```

實際案例：即文章中的 SampleSingletonClass 程式碼。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：
改善前：無單例保護，易被 new。
改善後：建構子封裝 + static 欄位確保唯一入口。
改善幅度：文章未提供量化數據，質化為「避免誤用」。

Learning Points（學習要點）
核心知識點：
- 單例的三要素：唯一存取點、唯一實例、封閉建構子。
- 延遲建立的基本寫法。
- 單例與狀態一致性的關聯。
技能要求：
- 必備技能：C# 的存取修飾與 static 的語義。
- 進階技能：理解潛在的執行緒安全議題。
延伸思考：
- 如何在多執行緒下保證安全？
- 如何將此模式抽象成可重用的基底？
- 如何避免未來在多個類別中重複此樣板？
Practice Exercise（練習題）
- 基礎練習：為某個設定讀取器加上基本單例（30 分鐘）。
- 進階練習：加入簡單的 thread-safe 寫法（2 小時）。
- 專案練習：替三個服務類別統一改為單例（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：能保證唯一實例且可用。
- 程式碼品質（30%）：封裝明確、命名一致。
- 效能優化（20%）：避免不必要的初始化。
- 創新性（10%）：對可測試性或擴展性的考量。

---

## Case #2: 多類別需要 Singleton 時的重複樣板問題

### Problem Statement（問題陳述）
業務場景：專案中有多個服務類別都需要單例行為（如資源池、字典快取、策略提供者）。若每個類別都各自複製一份單例樣板，導致專案中散落大量相似 static 欄位與屬性，維護困難。
技術挑戰：在不影響呼叫方式與使用體驗的前提下，消除重複樣板。
影響範圍：重複碼增加維護成本與出錯機會（某些類別忘了封閉建構子或忘了 lazy check）。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. static 屬性必須指定具體型別，導致每個類別都要寫一份。
2. static 成員不具多型性，無法靠繼承共用。
3. 缺乏跨類別的單例管理抽象。
深層原因：
- 架構層面：缺乏「單例管理器」的通用設計。
- 技術層面：未運用泛型以解耦型別與樣板。
- 流程層面：沒有建立樣板檢查與程式碼審查清單。

### Solution Design（解決方案設計）
解決策略：先以「繼承 + 集中管理」方式把重複碼搬到基底類，後續再升級為泛型，逐步消弭重複樣板與提升型別安全。

實施步驟：
1. 導入基底類集中管理
- 實作細節：建立 SingletonBase，集中實例建立與快取。
- 所需資源：C# 2.0。
- 預估時間：1 小時。
2. 讓需要單例的類別繼承基底
- 實作細節：統一建構子存取修飾、呼叫基底。
- 所需資源：C# 2.0。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
public class SingletonBase
{
    private static System.Collections.Hashtable _singleton_storage = new System.Collections.Hashtable();

    public static SingletonBase Instance(Type seed)
    {
        if (_singleton_storage[seed] == null)
        {
            _singleton_storage[seed] = Activator.CreateInstance(seed);
        }
        return _singleton_storage[seed] as SingletonBase;
    }
}

public class SingletonBaseImpl1 : SingletonBase
{
    public SingletonBaseImpl1() : base() { Console.WriteLine("Impl1.ctor"); }
}
public class SingletonBaseImpl2 : SingletonBase
{
    public SingletonBaseImpl2() : base() { Console.WriteLine("Impl2.ctor"); }
}
```

實際案例：文章提供的 SingletonBase + Hashtable + Activator.CreateInstance。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：
改善前：每類別一份樣板。
改善後：樣板集中於基底。
改善幅度：文章未提供量化，質化為「重複碼減少」。

Learning Points（學習要點）
核心知識點：
- 為樣板設計建立集中管理。
- 以 Type 為 key 的實例快取。
- 反射建立物件的基本使用。
技能要求：
- 必備技能：反射、集合。
- 進階技能：API 設計中的易用性與型別安全思考。
延伸思考：
- 這種 API 需要 typeof 和轉型，DX 不佳，如何優化？
- 記憶體釋放與 AppDomain 生命週期關聯？
- 如何避免重複建立（加鎖）？
Practice Exercise（練習題）
- 基礎練習：為兩個類別導入基底類管理（30 分鐘）。
- 進階練習：加上 lock 確保多執行緒不重複建立（2 小時）。
- 專案練習：將專案中 5 個單例類別收斂至基底管理（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：多類別皆可取得唯一實例。
- 程式碼品質（30%）：重複碼顯著下降，可讀性提升。
- 效能優化（20%）：避免不必要的重複建立。
- 創新性（10%）：對擴展性的思考。

---

## Case #3: Type 參數實作帶來的 API 體驗問題與局部緩解

### Problem Statement（問題陳述）
業務場景：導入 SingletonBase 後，呼叫方必須寫 SingletonBase.Instance(typeof(Foo))，且回傳為基底型別，需要再轉型，導致呼叫處處出現 typeof 與 as/強制轉型，破壞易讀性。
技術挑戰：在維持既有非泛型基底的前提下改善呼叫體驗。
影響範圍：API 難看、易錯（傳錯型別、轉型錯誤）。
複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. API 設計以 Type 參數與 object 儲存導致弱型別。
2. 回傳基底型別需轉型。
3. 呼叫方負擔 typeof 重複撰寫。
深層原因：
- 架構層面：未將型別資訊融入 API 簽章。
- 技術層面：未使用泛型改善型別安全。
- 流程層面：缺少 DX 評估與呼叫方負擔審視。

### Solution Design（解決方案設計）
解決策略：在各具體類別中提供一層型別專用的靜態屬性包裝，將 SingletonBase.Instance(typeof(T)) 封裝起來，讓呼叫方以 Foo.Instance 方式使用，暫時改善 DX。

實施步驟：
1. 為每個具體類別加靜態屬性
- 實作細節：在 Foo 內部提供 public static Foo Instance => (Foo)SingletonBase.Instance(typeof(Foo));
- 所需資源：C# 2.0。
- 預估時間：每類別 0.5 小時。
2. 移除外部直接呼叫非泛型 API
- 實作細節：統一改用類別上的 Instance。
- 所需資源：C# 2.0。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
public class SingletonBaseImpl1 : SingletonBase
{
    public static SingletonBaseImpl1 Instance
        => (SingletonBaseImpl1)SingletonBase.Instance(typeof(SingletonBaseImpl1));

    private SingletonBaseImpl1() { }
}
```

實際案例：呼應文章批評「用起來很醜」的用法，提供局部緩解方案。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「呼叫端可讀性提升，錯誤率降低」。

Learning Points（學習要點）
核心知識點：
- 以 Facade/包裝改善 DX。
- 降低呼叫端轉型與 typeof 噪音。
- 漸進式重構策略。
技能要求：
- 必備技能：C# 屬性、轉型。
- 進階技能：API 可用性觀點。
延伸思考：
- 此法仍依賴反射與 Hashtable，如何從根本改善？
- 是否能用泛型移除轉型？
- 如何追蹤 API 使用點，批次修正？
Practice Exercise（練習題）
- 基礎練習：為兩個類別新增型別專用 Instance 包裝（30 分鐘）。
- 進階練習：寫 Roslyn/正規表達式腳本，批次替換呼叫點（2 小時）。
- 專案練習：在專案中替換所有 typeof 呼叫為型別專用屬性（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：呼叫端能以 T.Instance 使用。
- 程式碼品質（30%）：可讀性提升、無轉型散落。
- 效能優化（20%）：避免重複反射呼叫。
- 創新性（10%）：重構自動化程度。

---

## Case #4: 泛型化 Singleton 管理，消除 typeof 與轉型

### Problem Statement（問題陳述）
業務場景：為了徹底解決「typeof + 轉型」的醜陋用法與弱型別問題，團隊希望以 .NET 2.0 的泛型機制提供型別安全的單例存取方式。
技術挑戰：如何設計泛型 API 讓呼叫者以 Singleton<T>.Instance 或基底 Instance<T>() 取得強型別實例。
影響範圍：DX、可維護性與錯誤率顯著影響。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 非泛型 API 的 Type 參數與 object 回傳造成弱型別。
2. typeof 與轉型噪音降低可讀性。
3. 基底類設計未承載型別資訊。
深層原因：
- 架構層面：缺少以泛型承載型別資訊的通用抽象。
- 技術層面：未利用 closed generic 靜態欄位的隔離特性。
- 流程層面：DX 與型別安全未成為 API 設計的優先指標。

### Solution Design（解決方案設計）
解決策略：以泛型類/方法承載型別資訊，提供 Singleton<T>.Instance 或 SingletonBase.Instance<T>()，回傳 T 而非基底，徹底移除 typeof 與轉型。

實施步驟：
1. 設計泛型單例提供者
- 實作細節：提供 static T Instance 屬性。
- 所需資源：C# 2.0。
- 預估時間：1 小時。
2. 改造呼叫端
- 實作細節：將所有 typeof 呼叫替換為泛型呼叫。
- 所需資源：C# 2.0。
- 預估時間：2 小時。

關鍵程式碼/設定：
```csharp
public sealed class Singleton<T> where T : class, new()
{
    private Singleton() { }
    public static T Instance
    {
        get { return Nested.instance; }
    }
    private static class Nested
    {
        internal static readonly T instance = new T();
        static Nested() { } // 保證 lazy 初始化語意
    }
}
// 用法
// var s1 = Singleton<SomeService>.Instance;
```

實際案例：文章明確提出「用泛型處理」的方向，這是符合主題的落地方案。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「型別安全、可讀性顯著提升」。

Learning Points（學習要點）
核心知識點：
- 靜態成員對每個閉包型別各自分離。
- 泛型約束 new() 的用途。
- 巢狀類的 lazy 初始化特性。
技能要求：
- 必備技能：C# 泛型、約束。
- 進階技能：CLR 型別初始化時機（beforefieldinit）。
延伸思考：
- 若不能提供無參數建構子，如何擴展？
- 是否需要處理 IDisposable 與釋放生命週期？
- 如何包裝成 NuGet 或內部套件？
Practice Exercise（練習題）
- 基礎練習：將兩個單例改為 Singleton<T>（30 分鐘）。
- 進階練習：對比 Activator vs new() 的效能（2 小時，質化比較）。
- 專案練習：建立內部共用的 Singleton<T> 套件並導入（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：可正確取得唯一 T 實例。
- 程式碼品質（30%）：API 簡潔、型別安全。
- 效能優化（20%）：移除不必要反射。
- 創新性（10%）：泛型抽象設計。

---

## Case #5: 用 new() 約束取代 Activator.CreateInstance 的反射成本

### Problem Statement（問題陳述）
業務場景：非泛型基底用 Activator.CreateInstance(seed) 動態建立實例，雖然彈性高，但在熱路徑中反射帶來額外成本與可能的執行期錯誤（無預設建構子）。
技術挑戰：降低反射開銷，同時在編譯期保障可建立。
影響範圍：效能、穩定性、設計可預期性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 反射建立物件較慢。
2. 無預設建構子時容易在執行期爆例外。
3. 回傳 object 缺乏型別資訊。
深層原因：
- 架構層面：未在 API 上宣示建立條件。
- 技術層面：未運用泛型約束轉換至編譯期檢查。
- 流程層面：缺少對建立路徑的效能審視。

### Solution Design（解決方案設計）
解決策略：在泛型 Singleton<T> 上以 where T : class, new() 限定無參數建構子，改用 new T() 直接建立，移除反射與執行期風險。

實施步驟：
1. 修改泛型約束
- 實作細節：where T : class, new()。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 取代 Activator 呼叫
- 實作細節：使用 new T()。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public sealed class Singleton<T> where T : class, new()
{
    private Singleton() { }
    public static T Instance { get { return Nested.instance; } }
    private static class Nested
    {
        internal static readonly T instance = new T(); // 無反射成本
        static Nested() { }
    }
}
```

實際案例：延伸文章「用泛型處理」的具體化。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「避免反射、將風險轉為編譯期」。

Learning Points（學習要點）
核心知識點：
- 泛型約束 new() 的意義與限制。
- 反射與直接建構的權衡。
- 編譯期 vs 執行期錯誤。
技能要求：
- 必備技能：泛型語法與約束。
- 進階技能：效能敏感路徑識別。
延伸思考：
- 若必須參數化建構，如何以工廠委派支援？
- 是否可引入 DI 容器接管建立？
- 如何在 .NET 2.0 的限制內設計可測？
Practice Exercise（練習題）
- 基礎練習：替換 Activator 為 new()（30 分鐘）。
- 進階練習：加入非參數建構支援失敗的編譯期驗證（2 小時）。
- 專案練習：統計專案中所有 Activator 使用點並評估是否改寫（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：建立成功且型別安全。
- 程式碼品質（30%）：簡潔、可讀。
- 效能優化（20%）：移除反射。
- 創新性（10%）：建立路徑優化思路。

---

## Case #6: 用泛型靜態欄位實現每個 T 各一實例（無共享干擾）

### Problem Statement（問題陳述）
業務場景：需要確保不同類別（T1、T2）各自獨立地只產生一個實例，避免共享快取造成邏輯耦合或 Key 撞號。
技術挑戰：如何透過 CLR 對 closed generic 類別的靜態區隔特性，天然地達成「每個 T 一份」。
影響範圍：正確性、簡潔度、維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 用 Hashtable/Dictionary 需要管理 Key 與同步。
2. 同一張表管理多型別，增加複雜度。
3. 呼叫錯誤 Key 可能取得錯誤實例。
深層原因：
- 架構層面：未利用 CLR 型別系統的天然隔離。
- 技術層面：未運用 closed generic 靜態成員分離。
- 流程層面：容器式設計增加管理負擔。

### Solution Design（解決方案設計）
解決策略：採用 Singleton<T> 靜態欄位 per T 的特性，每個 T 自有一份巢狀靜態欄位 instance，避免共享容器與 Key 管理。

實施步驟：
1. 定義 Singleton<T>
- 實作細節：參見 Case #4 程式碼。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 在多個 T 上測試隔離性
- 實作細節：對 T1、T2 分別取得 Instance，驗證不同參考。
- 所需資源：單元測試框架。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
var a1 = Singleton<SingletonBaseImpl1>.Instance;
var a2 = Singleton<SingletonBaseImpl1>.Instance;
var b1 = Singleton<SingletonBaseImpl2>.Instance;
// 斷言：ReferenceEquals(a1, a2) == true; a1 != b1
```

實際案例：對應文章中兩個實作類型（Impl1/Impl2）的需求。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「天然隔離、無 Key 管理」。

Learning Points（學習要點）
核心知識點：
- closed generic 靜態欄位的獨立性。
- 以型別系統建模狀態隔離。
- 減少容器式共享的管理成本。
技能要求：
- 必備技能：泛型閉包型別概念。
- 進階技能：單元測試撰寫與斷言。
延伸思考：
- 若需列舉所有單例，無容器會不會有不便？
- 如何在測試中重置單例狀態？
- 是否需要 AppDomain 隔離？
Practice Exercise（練習題）
- 基礎練習：對兩個 T 驗證實例隔離（30 分鐘）。
- 進階練習：提供 ResetForTest 方案（2 小時）。
- 專案練習：將容器式單例遷移至 per T 靜態欄位（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：各 T 有且僅有一實例。
- 程式碼品質（30%）：簡潔、無 Key 管理邏輯。
- 效能優化（20%）：移除容器查找。
- 創新性（10%）：測試友善設計。

---

## Case #7: 巢狀類確保延遲載入與執行緒安全

### Problem Statement（問題陳述）
業務場景：單例通常希望延遲建立，並天然具備執行緒安全。單純在 getter 中 new 可能造成 race condition。如何無鎖且簡潔地保障這兩點？
技術挑戰：在 .NET 2.0 環境中不使用 Lazy<T> 的條件下，正確利用 CLR 型別初始化機制。
影響範圍：正確性、效能、穩定性。
複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. getter 中檢查 null 再 new 在多執行緒下不安全。
2. 額外加鎖增加成本與複雜度。
3. 需要 lazy 且 thread-safe。
深層原因：
- 架構層面：未善用型別初始化語意。
- 技術層面：不了解 beforefieldinit 與靜態建構子行為。
- 流程層面：缺乏併發情境測試。

### Solution Design（解決方案設計）
解決策略：使用巢狀靜態類 Nested 搭配顯式靜態建構子，確保在首次存取 Instance 時才初始化，且由 CLR 保證執行緒安全。

實施步驟：
1. 引入巢狀類 Nested
- 實作細節：static readonly T instance = new T(); 並加 static ctor。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 壓力測試
- 實作細節：多執行緒並發讀取 Instance。
- 所需資源：簡單執行緒測試。
- 預估時間：1-2 小時。

關鍵程式碼/設定：
```csharp
public sealed class Singleton<T> where T : class, new()
{
    private Singleton() { }
    public static T Instance { get { return Nested.instance; } }
    private static class Nested
    {
        internal static readonly T instance = new T();
        static Nested() { } // 禁止 beforefieldinit，使初始化延後至首次存取
    }
}
```

實際案例：對應文章想達到的「更漂亮」與「正確」單例。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「lazy + thread-safe」。

Learning Points（學習要點）
核心知識點：
- CLR 靜態初始化與 beforefieldinit。
- 無鎖 lazy 單例技巧。
- .NET 2.0 無 Lazy<T> 的替代方案。
技能要求：
- 必備技能：C# 靜態建構子。
- 進階技能：多執行緒測試設計。
延伸思考：
- 若 T 的建構子很重，是否需背景載入？
- 初始化失敗如何重試或回滾？
- 記錄初始化時間與診斷資訊。
Practice Exercise（練習題）
- 基礎練習：套用巢狀類寫法（30 分鐘）。
- 進階練習：寫並發測試驗證唯一性（2 小時）。
- 專案練習：將現有單例統一替換為巢狀類實作（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：lazy 且唯一。
- 程式碼品質（30%）：簡潔無鎖。
- 效能優化（20%）：初始化只發生一次。
- 創新性（10%）：測試與診斷設計。

---

## Case #8: CRTP 風格的 Singleton 基底，簡化派生類使用

### Problem Statement（問題陳述）
業務場景：希望開發者在定義派生類時，能自然地以 類別名.Instance 取得單例，同時重用泛型管理的邏輯。
技術挑戰：靜態成員不具多型性，如何提供一致的呼叫體驗？
影響範圍：DX、一致性、易學性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態成員不會被繼承為成員呼叫。
2. 需要在派生類中提供轉發屬性。
3. 仍需保證建構子的封裝。
深層原因：
- 架構層面：需要 self-referential generic 的樣式。
- 技術層面：了解 static 成員與繼承關係。
- 流程層面：建立一致的樣板指引。

### Solution Design（解決方案設計）
解決策略：定義抽象基底 SingletonBase<TSelf>，派生類以自身為泛型參數，並在派生類提供一個簡單的 static Instance 屬性轉發到 Singleton<TSelf>.Instance。

實施步驟：
1. 定義抽象基底
- 實作細節：僅提供受保護建構子與文件化樣板。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 在派生類提供轉發屬性
- 實作細節：public static TSelf Instance => Singleton<TSelf>.Instance;
- 所需資源：C# 2.0。
- 預估時間：每類別 0.5 小時。

關鍵程式碼/設定：
```csharp
public abstract class SingletonBase<TSelf> where TSelf : class, new()
{
    protected SingletonBase() { }
}

public sealed class ConfigService : SingletonBase<ConfigService>
{
    private ConfigService() { }
    public static ConfigService Instance
    {
        get { return Singleton<ConfigService>.Instance; }
    }
}
```

實際案例：將文章的「繼承 + 泛型」構想具體化為可用樣板。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「呼叫體驗一致」。

Learning Points（學習要點）
核心知識點：
- CRTP（奇異遞迴模板）在 C# 的應用。
- 靜態成員與繼承的限制。
- 以轉發維持 DX 一致。
技能要求：
- 必備技能：泛型、繼承。
- 進階技能：可維護樣板設計。
延伸思考：
- 如何自動產生轉發屬性（T4/程式碼產生器）？
- 是否需要標註屬性供分析工具識別單例？
- 可否加入診斷欄位（建立時間、堆疊）？
Practice Exercise（練習題）
- 基礎練習：建立一個派生類並轉發（30 分鐘）。
- 進階練習：寫單元測試確保 Instance 唯一（2 小時）。
- 專案練習：替換 3 個服務類至 CRTP 樣式（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：派生類可用 .Instance。
- 程式碼品質（30%）：樣板一致、註解清楚。
- 效能優化（20%）：無額外成本。
- 創新性（10%）：工具化程度。

---

## Case #9: 控制建構子可見度，防止誤用 new

### Problem Statement（問題陳述）
業務場景：即使有 Singleton<T>，若類別建構子仍為 public，外部仍可 new 出第二個實例，破壞單例語義。
技術挑戰：在維持測試與開發便利性的前提下，嚴格封閉建構子。
影響範圍：正確性、封裝、API 合約。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 建構子可見度設錯。
2. 無守門機制阻止外部 new。
3. 缺少合約測試。
深層原因：
- 架構層面：未在樣板中強制規範。
- 技術層面：對可見度影響理解不足。
- 流程層面：缺少 API 準則檢查。

### Solution Design（解決方案設計）
解決策略：將單例類建構子設為 private，必要時用 InternalsVisibleTo 給測試專案；或保留 private 並透過測試由 Singleton<T> 啟動建立。

實施步驟：
1. 調整建構子為 private
- 實作細節：所有單例類皆 private ctor。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 加入測試驗證
- 實作細節：嘗試反射 new 並捕捉例外，確認合約。
- 所需資源：單元測試。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
public sealed class ResourcePool
{
    private ResourcePool() { }
    public static ResourcePool Instance { get { return Singleton<ResourcePool>.Instance; } }
}
```

實際案例：補強文章中基本單例實作的封裝要求。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「杜絕誤用」。

Learning Points（學習要點）
核心知識點：
- 封裝是單例的前提。
- 測試如何驗證 API 合約。
- InternalsVisibleTo 的用途（如需）。
技能要求：
- 必備技能：存取修飾子。
- 進階技能：測試與反射驗證。
延伸思考：
- 是否要 seal 類別避免被繼承破壞假設？
- 反射仍可 new，是否需額外保護？
- 如何在文件中標註使用方式？
Practice Exercise（練習題）
- 基礎練習：將三個單例類建構子封閉（30 分鐘）。
- 進階練習：撰寫反射測試驗證（2 小時）。
- 專案練習：建立 API 規範清單並自動檢查（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：無法外部 new。
- 程式碼品質（30%）：可見度一致。
- 效能優化（20%）：無額外負擔。
- 創新性（10%）：規範自動化。

---

## Case #10: 用 Dictionary<Type, object> 取代 Hashtable 提升型別安全

### Problem Statement（問題陳述）
業務場景：沿用 SingletonBase + Hashtable 的方案時，Hashtable 為非泛型集合，需大量轉型且缺乏編譯期檢查。
技術挑戰：在不大改呼叫面的前提下提升型別安全與可讀性。
影響範圍：DX、錯誤率、維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 非泛型集合需要轉型。
2. 缺少鍵值型別限制。
3. 讀寫容易犯錯。
深層原因：
- 架構層面：延用舊集合類型。
- 技術層面：未採用 .NET 2.0 泛型集合。
- 流程層面：缺乏 API 型別安全審視。

### Solution Design（解決方案設計）
解決策略：改以 Dictionary<Type, object> 儲存，並在 API 層提供泛型 Instance<T>()，逐步導向全泛型解法。

實施步驟：
1. 替換集合
- 實作細節：Hashtable -> Dictionary<Type, object>。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 增加泛型包裝方法
- 實作細節：public static T Instance<T>()。
- 所需資源：C# 2.0。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
public class SingletonBase
{
    private static readonly object _sync = new object();
    private static readonly System.Collections.Generic.Dictionary<Type, object> _map =
        new System.Collections.Generic.Dictionary<Type, object>();

    public static T Instance<T>() where T : class, new()
    {
        object value;
        if (_map.TryGetValue(typeof(T), out value))
            return (T)value;

        lock (_sync)
        {
            if (_map.TryGetValue(typeof(T), out value))
                return (T)value;

            T created = new T();
            _map[typeof(T)] = created;
            return created;
        }
    }
}
```

實際案例：文章非泛型基底的改良版。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「轉型減少、可讀性提升」。

Learning Points（學習要點）
核心知識點：
- 泛型集合相對於 Hashtable 的優勢。
- 以鍵入型別作為容器 Key。
- 簡易雙重檢查鎖（示意）。
技能要求：
- 必備技能：泛型集合。
- 進階技能：執行緒同步與容器設計。
延伸思考：
- 字典法 vs per T 靜態欄位的取捨？
- 如何避免記憶體洩漏（靜態根）？
- AppDomain 卸載策略。
Practice Exercise（練習題）
- 基礎練習：替換 Hashtable（30 分鐘）。
- 進階練習：寫 TryGet + Lock 的單元測試（2 小時）。
- 專案練習：以此容器替換舊設計並評估風險（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：正確取回 T。
- 程式碼品質（30%）：型別安全、易讀。
- 效能優化（20%）：減少反射與擷取成本。
- 創新性（10%）：平滑遷移策略。

---

## Case #11: 提供一致簡潔的呼叫介面（DX 導向）

### Problem Statement（問題陳述）
業務場景：API 的可讀性與一致性直接影響團隊生產力，目標是讓開發者用 Foo.Instance 或 Singleton<Foo>.Instance 兩種方式都直觀且無痛。
技術挑戰：在不破壞模式正確性的前提下，裁剪最少樣板碼。
影響範圍：DX、入門門檻、維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多種實作導致呼叫風格不一致。
2. 類別上缺少直覺的靜態入口。
3. 文件不足導致誤用。
深層原因：
- 架構層面：缺少統一呼叫約定。
- 技術層面：未提供轉發屬性。
- 流程層面：API 文檔缺失。

### Solution Design（解決方案設計）
解決策略：統一要求所有單例類提供 public static 類別專屬 Instance 屬性，內部轉發至泛型單例提供者，並於文件中固定此規範。

實施步驟：
1. 樣板化轉發屬性
- 實作細節：定義片段範本供貼用或程式碼產生。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
2. 文檔與範例
- 實作細節：在 README 提供規範與範例。
- 所需資源：文件工具。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
public sealed class Foo
{
    private Foo() { }
    public static Foo Instance { get { return Singleton<Foo>.Instance; } }
}
```

實際案例：取代文章中「很醜」的 typeof 寫法。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「呼叫一致，易用」。

Learning Points（學習要點）
核心知識點：
- API 設計中的 DX。
- 一致性的重要性。
- 範本化與文件化。
技能要求：
- 必備技能：C# 屬性轉發。
- 進階技能：內部標準制定。
延伸思考：
- 是否需分析工具檢查未提供 Instance 的類別？
- 如何在大型專案推行規範？
- 是否需要 Obsolete 舊 API？
Practice Exercise（練習題）
- 基礎練習：為 2 個類別提供轉發屬性（30 分鐘）。
- 進階練習：撰寫 Analyzer 偵測缺漏（2 小時，概念設計）。
- 專案練習：完成規範與教學文件（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：可使用 Foo.Instance。
- 程式碼品質（30%）：一致且簡潔。
- 效能優化（20%）：無額外成本。
- 創新性（10%）：規範推行方法。

---

## Case #12: 將現有非單例類別最小變動接入 Singleton 模式

### Problem Statement（問題陳述）
業務場景：既有類別已廣泛使用，全面重構成本高，需要以最小變動接入單例模式。
技術挑戰：保留既有 public API，僅增加單例入口與建構子保護。
影響範圍：回溯相容、風險控制。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 廣泛使用的既有 API 難以大改。
2. 呼叫點分散。
3. 風險期望低。
深層原因：
- 架構層面：缺乏漸進遷移策略。
- 技術層面：未抽象建立流程。
- 流程層面：缺少 deprecation 計畫。

### Solution Design（解決方案設計）
解決策略：保留既有建構邏輯，將建構子變為 private，提供靜態 Instance 轉發至 Singleton<T>。若必須保留 new，則改 internal 並以工廠與文件引導替代。

實施步驟：
1. 新增 Instance 屬性
- 實作細節：轉發至 Singleton<T>。
- 所需資源：C# 2.0。
- 預估時間：1 小時。
2. 調整建構子可見度
- 實作細節：private 或 internal + 文件。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public sealed class LegacyService
{
    private LegacyService() { /* 原邏輯保留 */ }
    public static LegacyService Instance { get { return Singleton<LegacyService>.Instance; } }
}
```

實際案例：延伸文章場景於大型專案的落地手法。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「風險可控、最小侵入」。

Learning Points（學習要點）
核心知識點：
- 漸進式重構。
- 可見度調整與相容性。
- 文件化替代路徑。
技能要求：
- 必備技能：影響分析。
- 進階技能：相容性維護策略。
延伸思考：
- 是否需提供 obsolete 指示器？
- 如何在版本發佈節點執行？
- 回滾機制？
Practice Exercise（練習題）
- 基礎練習：為既有類別加單例入口（30 分鐘）。
- 進階練習：建立遷移指南（2 小時）。
- 專案練習：遷移三個核心元件並監測風險（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：不破壞既有功能。
- 程式碼品質（30%）：改動最小。
- 效能優化（20%）：無負面影響。
- 創新性（10%）：遷移策略。

---

## Case #13: 單例建立的診斷與可觀測性（建立時機記錄）

### Problem Statement（問題陳述）
業務場景：在調試問題時，需了解單例何時被建立。文章示例在建構子中 Console.WriteLine()，顯示建立時機。
技術挑戰：在不污染核心邏輯的前提下，為單例建立加入輕量診斷。
影響範圍：除錯效率、可觀測性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 延遲建立使建立時機不明確。
2. 問題重現需要知道初始化次序。
3. 缺少標準化診斷輸出。
深層原因：
- 架構層面：缺少可觀測性設計。
- 技術層面：未集中紀錄建立事件。
- 流程層面：缺少調試指引。

### Solution Design（解決方案設計）
解決策略：提供 ICreationObserver 或簡單的靜態事件在 Singleton<T> 觸發，或統一在建構子內記錄；若不便修改，至少以 Debug.WriteLine 搭配條件編譯。

實施步驟：
1. 建立簡易日誌
- 實作細節：在建構子內 Debug.WriteLine。
- 所需資源：System.Diagnostics。
- 預估時間：0.5 小時。
2. 條件編譯保護
- 實作細節：#if DEBUG 包裹。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public sealed class Foo
{
    private Foo()
    {
#if DEBUG
        System.Diagnostics.Debug.WriteLine("Foo singleton created at: " + DateTime.Now);
#endif
    }
    public static Foo Instance { get { return Singleton<Foo>.Instance; } }
}
```

實際案例：文章示範 Console.WriteLine 建立訊息的強化版。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「除錯效率提升」。

Learning Points（學習要點）
核心知識點：
- 可觀測性基本做法。
- 條件編譯與非侵入式記錄。
- 初始化次序調試。
技能要求：
- 必備技能：Debug/Trace。
- 進階技能：診斷策略。
延伸思考：
- 是否導入事件或 hook？
- 產品環境如何控制噪音？
- 與記錄系統整合？
Practice Exercise（練習題）
- 基礎練習：加入 Debug 訊息（30 分鐘）。
- 進階練習：建立簡單 observer 通知（2 小時）。
- 專案練習：統一單例建立記錄規範（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：能看到建立時間。
- 程式碼品質（30%）：非侵入、可控。
- 效能優化（20%）：編譯條件避免生產開銷。
- 創新性（10%）：觀測設計。

---

## Case #14: 單例行為的單元測試與驗證

### Problem Statement（問題陳述）
業務場景：需要確保多次呼叫取得同一個實例，並在併發下仍然唯一。
技術挑戰：設計自動化測試覆蓋重點行為。
影響範圍：品質保證、回歸風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少自動化檢查。
2. 併發場景難以手動驗證。
3. 多型別隔離需測。
深層原因：
- 架構層面：缺少可測性設計。
- 技術層面：不了解關鍵風險點。
- 流程層面：未建立測試模板。

### Solution Design（解決方案設計）
解決策略：撰寫三類測試：同一執行緒多次取用同一參考、不同型別不相同、併發取得仍唯一。

實施步驟：
1. 同參考測試
- 實作細節：ReferenceEquals 斷言。
- 所需資源：測試框架。
- 預估時間：0.5 小時。
2. 型別隔離測試
- 實作細節：T1 != T2。
- 所需資源：測試框架。
- 預估時間：0.5 小時。
3. 併發測試
- 實作細節：多執行緒取得指標集合去重。
- 所需資源：Thread/Task（.NET 2 可用 Thread）。
- 預估時間：1-2 小時。

關鍵程式碼/設定：
```csharp
// 伪碼示意
var r1 = Singleton<SingletonBaseImpl1>.Instance;
var r2 = Singleton<SingletonBaseImpl1>.Instance;
System.Diagnostics.Debug.Assert(object.ReferenceEquals(r1, r2));

var a = Singleton<SingletonBaseImpl1>.Instance;
var b = Singleton<SingletonBaseImpl2>.Instance;
System.Diagnostics.Debug.Assert(!object.ReferenceEquals(a, b));
```

實際案例：以文章中的 Impl1/Impl2 作為測試對象。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「自動驗證唯一性」。

Learning Points（學習要點）
核心知識點：
- ReferenceEquals 的使用。
- 併發測試設計。
- 測試覆蓋要點。
技能要求：
- 必備技能：單元測試基礎。
- 進階技能：併發測試與去重分析。
延伸思考：
- 是否需在測試中重置單例？
- 測試環境的隔離（AppDomain）？
- 失敗診斷資訊如何輸出？
Practice Exercise（練習題）
- 基礎練習：寫兩個斷言測試（30 分鐘）。
- 進階練習：手寫多執行緒壓力測（2 小時）。
- 專案練習：建立單例測試模板套用（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：測試涵蓋關鍵場景。
- 程式碼品質（30%）：測試清楚、可維護。
- 效能優化（20%）：測試時間合理。
- 創新性（10%）：測試設計巧思。

---

## Case #15: 模式限制與風險識別（無參數建構子、釋放、反射繞過）

### Problem Statement（問題陳述）
業務場景：導入單例後，出現部分限制（需要無參數建構子、無法方便注入依賴、釋放時機等），必須清楚告知並設計對策。
技術挑戰：在 .NET 2.0 條件下，平衡限制與可用性。
影響範圍：功能覆蓋、維護策略。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. new() 約束限制建構子設計。
2. 靜態根導致生命週期不可控。
3. 反射可繞過 private ctor。
深層原因：
- 架構層面：單例本質上是全域狀態。
- 技術層面：缺乏 DI 與資源釋放機制。
- 流程層面：未明確文件化限制。

### Solution Design（解決方案設計）
解決策略：文件化限制與替代方案。若需參數化建立，考慮容器/工廠注入；釋放可提供顯式 Shutdown 方法（僅測試用）；反射繞過以內部規範與測試防範。

實施步驟：
1. 限制文件化
- 實作細節：README/貢獻指南明列。
- 所需資源：文件工具。
- 預估時間：1 小時。
2. 提供測試用釋放 API（可選）
- 實作細節：條件編譯下允許 Reset。
- 所需資源：C# 2.0。
- 預估時間：1-2 小時。

關鍵程式碼/設定：
```csharp
// 僅供測試使用的重置（示意，不建議產品使用）
public static class SingletonTestHooks<T> where T : class, new()
{
#if DEBUG
    public static void ResetForTest()
    {
        typeof(Singleton<T>).TypeInitializer.Invoke(null, null);
    }
#endif
}
```

實際案例：針對文章場景下常見的限制給出治理策略。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「風險可控、預期一致」。

Learning Points（學習要點）
核心知識點：
- 單例作為全域狀態的影響。
- 生命週期管理策略。
- 測試與產品行為隔離。
技能要求：
- 必備技能：文件撰寫、風險分析。
- 進階技能：條件編譯與測試 hook。
延伸思考：
- 長期看是否應以 DI 容器替代單例？
- 如何避免狀態共享帶來的隱性耦合？
- 安全與反射繞過的治理？
Practice Exercise（練習題）
- 基礎練習：撰寫限制清單（30 分鐘）。
- 進階練習：設計測試重置方案（2 小時）。
- 專案練習：制定替代策略與遷移計畫（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：限制與對策清晰。
- 程式碼品質（30%）：測試/產品區隔明確。
- 效能優化（20%）：無不必要負擔。
- 創新性（10%）：替代方案思路。

---

## Case #16: 從非泛型繼承式設計平滑升級到泛型單例

### Problem Statement（問題陳述）
業務場景：專案已使用 SingletonBase + Instance(Type) 一段時間，決定升級到泛型 Singleton<T> 以改善 DX 與型別安全，但需確保平滑過渡。
技術挑戰：雙實作共存期間如何避免混用與混亂。
影響範圍：風險、技術債清理。
複雜度評級：中-高

### Root Cause Analysis（根因分析）
直接原因：
1. 舊 API 已遍佈呼叫點。
2. 新舊模式差異大。
3. 缺乏自動化替換。
深層原因：
- 架構層面：演進式升級策略缺失。
- 技術層面：工具化能力不足。
- 流程層面：遷移窗口與規範未定義。

### Solution Design（解決方案設計）
解決策略：提供過渡層與 Obsolete 標註，先引入泛型轉發，允許舊呼叫在內部改走新路徑，逐步替換呼叫點，最終移除舊 API。

實施步驟：
1. 在 SingletonBase 增加泛型包裝
- 實作細節：Instance<T>() 內部走 Singleton<T>。
- 所需資源：C# 2.0。
- 預估時間：1 小時。
2. Obsolete 舊 API
- 實作細節：為 Instance(Type) 加上註解或文件標註。
- 所需資源：C# 2.0。
- 預估時間：0.5 小時。
3. 批次替換呼叫點
- 實作細節：腳本/IDE 搜尋替換。
- 所需資源：工具。
- 預估時間：4-8 小時（視規模）。

關鍵程式碼/設定：
```csharp
public class SingletonBase
{
    [Obsolete("Use Instance<T>() instead.")]
    public static SingletonBase Instance(Type seed) { /* 原實作 */  return null; }

    public static T Instance<T>() where T : class, new()
    {
        return Singleton<T>.Instance; // 過渡層統一路徑
    }
}
```

實際案例：對應文章「用繼承 + 用泛型」的整合過渡策略。
實作環境：.NET Framework 2.0, C# 2.0。
實測數據：文章未提供；質化為「風險可控、平滑升級」。

Learning Points（學習要點）
核心知識點：
- 漸進式重構的策略與步驟。
- Obsolete 與替代 API 的使用。
- 風險控管與回滾。
技能要求：
- 必備技能：重構與工具使用。
- 進階技能：版本治理與變更管理。
延伸思考：
- 如何度量技術債減少？
- 何時移除舊 API？
- 是否需版本標記事務？
Practice Exercise（練習題）
- 基礎練習：為舊 API 加上過渡層（30 分鐘）。
- 進階練習：製作替換腳本（2 小時）。
- 專案練習：在模組內完成新舊共存到移除全流程（8 小時）。
Assessment Criteria（評估標準）
- 功能完整性（40%）：不破壞既有功能。
- 程式碼品質（30%）：過渡清晰、無重複邏輯。
- 效能優化（20%）：無額外成本。
- 創新性（10%）：升級治理方法。

---

案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case 1, 3, 9, 11, 13
- 中級（需要一定基礎）
  - Case 2, 4, 5, 6, 8, 10, 12, 14, 16
- 高級（需要深厚經驗）
  - Case 7, 15

2. 按技術領域分類
- 架構設計類
  - Case 2, 4, 6, 7, 8, 11, 15, 16
- 效能優化類
  - Case 5, 6, 7, 10
- 整合開發類
  - Case 12, 16
- 除錯診斷類
  - Case 13, 14
- 安全防護類
  - Case 9, 15

3. 按學習目標分類
- 概念理解型
  - Case 1, 2, 4, 6, 7
- 技能練習型
  - Case 3, 5, 8, 10, 11, 12
- 問題解決型
  - Case 9, 14, 16
- 創新應用型
  - Case 13, 15

案例關聯圖（學習路徑建議）
- 起步建議順序
  1) Case 1（理解基本單例）→ 2) Case 2（多類別重複問題）→ 3) Case 3（非泛型 API 的 DX 問題）
  4) Case 4（泛型化解法）→ 5) Case 5（去反射 new() 約束）→ 6) Case 6（per T 靜態欄位）
  7) Case 7（巢狀類確保 lazy + thread-safe）
- 進一步最佳化與落地
  - Case 8（CRTP 樣式）與 Case 11（DX 統一）依賴 Case 4-7 導入。
  - Case 9（建構子可見度）是全程必備規範，建議在 Case 4 後立即落實。
  - Case 10（Dictionary 替換）適用仍在容器式設計的過渡期，若已用 Case 4/6 可略過。
- 專案級導入與治理
  - 完成上述後，進入 Case 12（最小侵入接入）與 Case 16（平滑升級策略），確保大規模導入。
  - 品質保障與可觀測性：並行導入 Case 13（診斷）與 Case 14（單元測試模板）。
  - 風險與限制治理：最後研讀與落實 Case 15，完善文件與長期策略。
- 依賴關係
  - Case 7 依賴對 Case 4/6 的理解（泛型與 per T 靜態欄位）。
  - Case 8、11 依賴 Case 4（泛型單例）基礎。
  - Case 16 依賴 Case 2（舊設計）與 Case 4（新設計）的共同理解。
  - Case 14 測試覆蓋需先有 Case 4/6 的實作基礎。

說明
- 文章提供了問題背景、非泛型基底方案與「泛型 + 繼承」的方向；本文將其補全為可落地的 16 個教學案例。對於效益與數據，因原文未提供，均以質化描述呈現。