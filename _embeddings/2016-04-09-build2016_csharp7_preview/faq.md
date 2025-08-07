# //build/2016 - The Future of C#

# 問答集 (FAQ, frequently asked questions and answers)

## Q: C# 7 公布的語法特性屬於哪一層級？需要更新 CLR 或 .NET Runtime 嗎？
這些都是「編譯期的 syntactic sugar」，編譯器會在 Compile Time 把新語法轉成舊有 IL，因此不需要任何新版 CLR / Runtime，就能在既有平台上執行。

## Q: 這場 Build 2016 Session 中，作者最關注的三個 C# 7 新語法是哪些？
1. Tuples Literal  
2. Record Type  
3. Pattern Matching  

## Q: Visual Studio “15” Preview 是否完整支援所有 C# 7 語法？
尚未。預覽版目前不支援 Tuples 與 Records，其他語法（如 Pattern Matching 等）已可體驗。

## Q: 要在 Visual Studio “15” Preview 開啟 C# 7 語法，應在哪裡設定？
在「專案 ➜ 屬性 ➜ Build ➜ Conditional compilation symbols」加入  
__DEMO__, __DEMO_EXPERIMENTAL__ 兩個 Symbol 後即可正常編譯並在 IDE 取得 IntelliSense 支援。

## Q: 為什麼需要 Tuples Literal？它解決了什麼問題？
以往 C# 僅能 `return` 一個值；若要回傳多值只能：
1. 自訂類別包裝  
2. 使用 `out/ref` 參數  
3. 依賴 `Tuple<T1,T2>` 但成員名稱僅有 Item1、Item2  
Tuples Literal 讓開發者用 `(int Width, int Height)` 之類語法，就能同時回傳多個具名且強型別的值，程式碼更精簡也更易讀。

## Q: Tuples Literal 編譯後的效能與既有做法有差異嗎？
沒有。編譯器最終仍會為你產生類似匿名型別的封裝類別；省下的只是打字與閱讀成本，而非執行時效能。

## Q: 什麼是 Record Type？與 Tuples 有何不同？
Record Type 是「只包含唯讀屬性」的特殊類別：
• 宣告可簡化為 `class Person(string First, string Last);`  
• 編譯器自動產生建構式、唯讀屬性、`IEquatable<T>` 實作  
• 物件為 Immutable，修改需以 `with` 產生新物件  
相較於 Tuples，Record 可繼承、具明確型名且可在程式中重複使用。

## Q: Record Type 是否可以繼承？範例語法為何？
可以，例如：
```
class Geometry();
class Rectangle(int Width, int Height) : Geometry;
class Square(int Width) : Geometry;
```

## Q: Pattern Matching 的核心優勢是什麼？
它把「型別判斷 (is)＋轉型 (cast)」與「條件判斷」合併成單一敘述，能在 `switch` 或 `if` 中直接：
```
case Rectangle r when r.Height > 5:
    ...
```
減少樣板程式碼、提升可讀性，讓程式碼更貼近開發者的思考流程。

## Q: Pattern Matching 的 `when` 子句可以用來做什麼？
`when` 可在比對型別後再加上額外條件，例如只處理「高度大於 5」的矩形：
```
case Rectangle r when r.Height > 5:
```

## Q: 採用 Pattern Matching 會帶來效能改善嗎？已寫好的舊程式需要重寫嗎？
不會有明顯效能差異；編譯器最終仍展開為傳統 `as` 轉型加 if 判斷。若現有程式碼運作正常，除非特別追求可讀性，沒有強制需要改寫。

## Q: 作者如何看待 C# 近年的語法演進方向？
文章指出 C# 明顯受到 JavaScript／JSON 生態的影響：  
• Tuples 與 Records 讓建立大量複雜資料結構更容易  
• Pattern Matching 讓資料過濾、樣式比對更簡潔  
目的都是在保持靜態型別優勢的同時，使程式碼更貼近日常資料處理需求。