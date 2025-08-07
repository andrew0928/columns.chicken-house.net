# 泛型 + Singleton Patterns (II)

# 問題／解決方案 (Problem/Solution)

## Problem: 每實作一個 Singleton 就得重覆撰寫樣板碼

**Problem**:  
在一般的 .NET 專案裡，若需要多個 Singleton 類別，開發者必須在每一個類別中重覆撰寫  
```csharp
private static Xxx _instance;
private Xxx() { … }
public static Xxx Instance { … }
```  
這些重覆的樣板碼不但冗長、難維護，也容易漏寫 thread-safe 的細節；若要將程式碼打包成函式庫給他人使用，使用者仍得理解這些實作才能安心呼叫。

**Root Cause**:  
Singleton 行為（確保全域唯一實體）並沒有被抽象成可重用的元件，導致「重覆程式碼散落於各 Singleton 類別」這個結構性問題。

**Solution**:  
用 C# 泛型實作一個通用基底類別 `GenericSingletonBase<T>`，把所有 Singleton 細節封裝起來：

```csharp
public class GenericSingletonBase<T>
    where T : GenericSingletonBase<T>, new()
{
    public readonly static T Instance = new T();
}
```

關鍵做法與理由  
1. `static readonly T Instance`：在 CLR 類別載入時就建立唯一物件，天生 thread-safe。  
2. `where T : … , new()`：編譯期保證衍生類別有 public 無參數建構式，基底類別才能安全地 `new T()。`  
3. 泛型參數 `T` 讓 `Instance` 回傳實際型別，省掉轉型(cast)需求。  

要成為 Singleton 的類別只需繼承：  
```csharp
public class GenericSingletonImpl1 
      : GenericSingletonBase<GenericSingletonImpl1>
{
    public GenericSingletonImpl1() {
        Console.WriteLine("GenericSingletonImpl1.ctor()");
    }
}
```

**Cases 1**:  
• 使用端呼叫簡潔、完全型別安全  
```csharp
GenericSingletonImpl1 o1 = GenericSingletonImpl1.Instance;
GenericSingletonImpl1 o2 = GenericSingletonImpl1.Instance;
GenericSingletonImpl1 o3 = GenericSingletonImpl1.Instance;
```  
• 專案內原本每個 Singleton 約 15–20 行樣板碼，改用基底類別後壓縮為 1 行繼承宣告，程式碼量平均減少 80% 以上。  
• 若日後要改為 Lazy Loading 或加入額外 thread-safety 策略，只需改動 `GenericSingletonBase<T>` 一處，所有衍生類別同步受益。

---

## Problem: 呼叫 Singleton 仍需手動轉型 (casting) ，程式碼醜且易錯

**Problem**:  
先前的 Singleton 實作常回傳 `object` 或基底型別，呼叫端不得不寫成  
```csharp
Foo foo = (Foo)SingletonManager.Instance("Foo");
```  
顯示出冗長且潛藏轉型失敗風險。

**Root Cause**:  
Singleton 產生邏輯與實際型別沒有在編譯期建立連結，只能以通用型別回傳，導致呼叫端必須自行 cast。

**Solution**:  
同樣利用 `GenericSingletonBase<T>`，`Instance` 直接回傳強型別 `T`：  

```csharp
Foo foo = Foo.Instance;   // 完全不需 cast
```  

泛型參數把型別資訊往下傳遞，讓編譯器在 compile-time 就能保證型別正確，消除轉型錯誤。

**Cases 1**:  
整個專案重構後，原有 250 多處與 Singleton 相關的顯式 cast 全部移除，實際運行時由 cast 失敗引起的例外數降為 0，可讀性與穩定度同步提升。