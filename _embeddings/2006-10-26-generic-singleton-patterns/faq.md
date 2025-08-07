# 泛型 + Singleton Patterns

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 C# 中，若只有單一類別需要 Singleton，最簡單的實作方式是什麼？
使用「私有建構子 + 靜態欄位 + Lazy 取得屬性」即可：
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

    private SampleSingletonClass() { }
}
```

## Q: 為什麼傳統 Singleton 作法在多個類別都想套用時會造成困擾？
因為每個類別都得複製幾乎相同的程式碼，只是 `public static XXX Instance` 的型別不同，導致重複程式碼多且維護困難。

## Q: 將 Singleton 共同邏輯抽到基底類別（Inheritance）能解決什麼問題？
可以把重複程式碼集中到 `SingletonBase`，用一個 `Hashtable` 儲存各型別的唯一實例，子類別就不必再寫一次相同的 Lazy 建立邏輯。

## Q: 單純依賴 Inheritance 的 Singleton 作法有何缺點？
呼叫端必須這樣使用：
```csharp
SingletonBase.Instance(typeof(SingletonBaseImpl1));
```
1. 需要傳入 `Type` 物件，程式碼醜且不直覺。  
2. 回傳型別被降到 `SingletonBase`，失去編譯期型別安全，必須再做型別轉換。

## Q: .NET 2.0 的泛型機制對 Singleton Pattern 有何幫助？
泛型可以將「共用的 Singleton 邏輯」寫成一個 `Singleton<T>` 類別，  
編譯器在使用時會自動幫你代入 `T` 的實際型別，既避免重複程式碼，又保留型別安全，呼叫端也更優雅。

## Q: 作者提出的直覺解法包含哪兩個步驟？
1. 透過繼承，把重複的程式碼集中到 Super Class。  
2. 再用泛型把相同邏輯套用到不同型別。  

（完整程式實作將於下一篇〈待續〉說明）