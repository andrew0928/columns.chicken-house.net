# [C#: yield return] #1. How It Work ?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼要使用 IEnumerator / Iterator Pattern，而不是直接在迴圈裡把「列舉邏輯」和「處理邏輯」寫在一起？
Iterator Pattern 的目的就是「毋須知曉聚合物件的內部細節，即可依序存取內含的每一個元素」。  
透過 IEnumerator，  
1. 「走訪順序 (iteration)」可以被封裝於一個獨立物件中。  
2. 「每取出一個元素後要做的事 (process)」則寫在呼叫端。  
兩者分離後，任何一方的邏輯要更動或替換都變得容易，也不必暴露集合內部的資料結構。

## Q: 直接寫 IEnumerator 類別太麻煩，有沒有兼顧美觀與功能的方法？
有，用 C# 的 yield return。  
只要在一個傳回 IEnumerable<T> 的方法裡，用 yield return 逐一傳回元素，C# 編譯器就會自動產生一個隱藏的類別，替你實作 IEnumerable<T>/IEnumerator<T>，同時保留簡潔的迴圈寫法。

## Q: yield return 背後到底做了什麼魔法？  
編譯器會：
1. 為含有 yield return 的方法，產生一個隱藏的巢狀類別 (名稱類似 `<MethodName>d__0`)。  
2. 該類別同時實作 IEnumerable<T> 與 IEnumerator<T>，內含  
   • 代表目前狀態的私有欄位 (state)  
   • 目前元素 (current)  
   • MoveNext、Current、Reset 等必要成員。  
3. 原本的方法僅建立並回傳這個隱藏類別的實例。  
如此即可在每次 foreach/MoveNext 時保存與回復執行狀態，達成「暫停並繼續」的效果。

## Q: yield return 看似違反「函式呼叫完成才能 return」的結構化程式設計規則，它怎麼辦到的？  
實際上沒有違反規則；yield return 只是把方法拆成一個「狀態機」。  
• 第一次呼叫 MoveNext 時執行到第一個 yield return 就暫停，並記錄目前 state。  
• 下次 MoveNext 會依 state 回到上次暫停的位置繼續執行。  
整個過程由編譯器產生的 IEnumerator 類別管理，因此在語意上仍屬於合法的函式呼叫/回傳行為。

## Q: IEnumerator / yield return 是 Microsoft 發明的嗎？  
Iterator 這個概念早在 Design Patterns 一書中就已提出，Microsoft 只是將其介面化為 IEnumerator 並在 C# 提供 yield return 這種語法糖，讓開發者更容易使用 Iterator Pattern。

## Q: .NET 與 Java 在語言新特性的態度上有何不同？  
過去為了維持 JVM 向前相容，Java 很少修改 VM 規格，語法演進相對保守；  
.NET / C# 則樂於在編譯器層面做出讓步，新增各種 Syntax Sugar（如 delegate、LINQ、yield return 等），用較簡潔的程式碼換取編譯器在背後產生複雜實作。