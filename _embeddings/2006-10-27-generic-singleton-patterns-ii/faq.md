# 泛型 + Singleton Patterns (II)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 如何利用 .NET 的泛型撰寫一個可重複使用的 Singleton 基底類別？
透過以下程式碼即可完成。  
```csharp
public class GenericSingletonBase<T>
    where T : GenericSingletonBase<T>, new()
{
    public readonly static T Instance = new T();
}
```  
重點在於：
1. 以 `where T : …, new()` 這條件限制 `T` 必須繼承自己並具備無參數建構式。  
2. 於型別內宣告 `public readonly static T Instance`，在第一次存取時就會產生惟一實例。  
如此一來，Singleton 的所有細節都被封裝在 3 行程式碼裡。

## Q: 如果我要讓自己的類別成為 Singleton，只需要做哪些事？
只要讓你的類別繼承 `GenericSingletonBase<你的類別>` 即可，其餘程式碼皆非必要。  
範例：  
```csharp
public class GenericSingletonImpl1 
        : GenericSingletonBase<GenericSingletonImpl1>
{
    public GenericSingletonImpl1()
    {
        Console.WriteLine("GenericSingletonImpl1.ctor()");
    }
}
```  
完成繼承之後，該類別立刻具備 Singleton 行為，無須額外撰寫鎖定或靜態屬性等樣板程式碼。

## Q: 在取得 Singleton 物件時，還需要再做型別轉換 (casting) 嗎？
完全不需要。  
因為 `Instance` 本身就是衍生類別的型別，使用時可以直接這麼寫：  
```csharp
GenericSingletonImpl1 o1 = GenericSingletonImpl1.Instance;
GenericSingletonImpl1 o2 = GenericSingletonImpl1.Instance;
GenericSingletonImpl1 o3 = GenericSingletonImpl1.Instance;
```  
程式碼簡潔、可讀性高，也避免了每次呼叫都必須自行做型別轉換的麻煩。