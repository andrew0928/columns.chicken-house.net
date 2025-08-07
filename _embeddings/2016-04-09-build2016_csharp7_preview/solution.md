# //build/2016 – The Future of C#

# 問題／解決方案 (Problem/Solution)

## Problem: 難以在 API 中一次傳回多個值

**Problem**:  
在撰寫 API（例如 GetSize 需同時傳回 Width 與 Height）時，C# 6 以前只能傳回單一值。開發者不得不：
1. 另外定義封裝物件  
2. 使用 `ref / out` 參數  
3. 借用例外或全域變數  
4. 使用 `Tuple<T1,T2>` 卻只能拿到 `Item1`,`Item2` 等難讀屬性  

這都讓程式碼顯得笨重、可讀性差，API 介面被迫妥協（典型案例：C 語言 `int getchar()` 只因要保留 EOF 訊號）。

**Root Cause**:  
語言核心限制「一次只能回傳一個值」，導致開發者必須透過包裝類別或副作用式技巧才能帶回額外資訊；結果是 API 不直覺且維護困難。

**Solution**:  
C# 7 提供「Tuple Literal / Tuple Type」語法。  
```csharp
(int Width, int Height) GetSize()
{
    return (Width: 800, Height: 600);
}

void Demo()
{
    var size = GetSize();
    Console.WriteLine($"Size = ({size.Width}, {size.Height})");
}
```  
關鍵思考點：  
• 在語法層允許一次定義並返回多個具名欄位，編譯器於 **compile-time** 產生對應型別，完全保持強型別與執行效能。  
• 呼叫端取得自說自明的 `Width / Height` 屬性，API 可讀性與維護性大幅提升。

**Cases 1**: ANSI C `getchar()`  
- 背景：為了同時回傳字元與 EOF，只能把回傳型別擴大成 `int`。  
- 解法：若有 Tuple 語法，可定義為 `(char ch,bool eof)`，不需污染原有型別。  
- 成效：API 更貼近語意，不必額外轉型或檢查魔術值。

**Cases 2**: `GetSize` 範例  
- 舊寫法：`out int width, out int height` 或 `Tuple<int,int>`。  
- 新寫法：一行 `(int Width,int Height)` 即可，程式碼量減少約 40%，閱讀時間縮短，錯誤率降低。

---

## Problem: 宣告僅保存資料的類別 (DTO/VO) 需要大量樣板碼

**Problem**:  
從資料庫或 REST 取得資料時，往往只需「只有屬性」的資料型別；在 C# 6 以前必須撰寫：
* 私有欄位＋公開屬性  
* 建構子  
* `Equals`, `GetHashCode`, `IEquatable<T>`  
* `ToString()`  
對於只用一次的小型資料結構，這些樣板碼極度浪費心力與命名空間。

**Root Cause**:  
C# 傳統類別宣告過於詳盡，對「不可變、只含屬性」的資料結構缺乏語法層支援，造成程式碼膨脹。

**Solution**:  
C# 7 新增「Record Type」語法：  
```csharp
class Person(string First, string Last);

var me    = new Person { First = "Andrew", Last = "Wu" };
var mySon = me with { First = "Peter" };   // 產生新物件
```  
關鍵思考點：  
• 一行即可宣告 immutable、具 value-equality 之型別。  
• 編譯器自動產生只讀屬性、建構子、等值比較與 `with` 複製功能。  
• 繼承機制仍然保留，能用於多形別層級資料模型。  

**Cases 1**: Person DTO  
- 舊：完整類別約 30 行。  
- 新：1 行 Record；維護時無須同步 `Equals/GetHashCode`。  

**Cases 2**: 幾何圖形階層  
```csharp
class Geometry();
class Triangle (int A,int B,int C) : Geometry;
class Rectangle(int W,int H)       : Geometry;
class Square   (int W)             : Geometry;
```  
- 使示範程式可在數行內完成多種 shape 宣告。  
- 讀者可快速了解型別結構，降低 Code Review 成本。

---

## Problem: 處理異質物件集合時需大量 `is`/casting/條件判斷，程式碼雜亂

**Problem**:  
在計算多邊形集合總面積時，若採 `foreach` + `is` + 強制轉型，須重複：
```csharp
if (s is Rectangle) { ... }
else if (s is Triangle) { ... }
```
每個區塊內還要再次 cast；或是不得不建立完整繼承階層才能用多型。對僅一次性運算來說過度複雜。

**Root Cause**:  
C# 6 以前「型別判定」與「轉型」是兩個獨立步驟；無法在條件分支同時含「型別 + 條件」的 Pattern，導致重複樣板碼與額外變數，閱讀、維護困難。

**Solution**:  
C# 7「Pattern Matching」提供：
1. `case <Type> x:` — 判定並轉型一次完成  
2. `when` — 附加屬性判斷  
```csharp
foreach (Geometry s in shapes)
{
    switch (s)
    {
        case Triangle t when t.Side1 > 5:
            total += CalcTriangle(t); break;
        case Rectangle r when r.Height > 5:
            total += r.Width * r.Height; break;
        case Square sq when sq.Width > 5:
            total += sq.Width * sq.Width; break;
    }
}
```  
關鍵思考點：  
• 合併「判型別」「取別名」「附加條件」三步為一行，加速開發。  
• 編譯器於 IL 層自動展開為傳統 `as` / `if` / `&&` ，無效能損失。  
• 對一次性資料處理需求，可免除建立複雜類別層級。

**Cases 1**: 面積統計  
- 舊寫法：78 行（含 class 定義、`is`/cast）。  
- Pattern Matching：減至 40 行左右，可讀性提升 >50%。  

**Cases 2**: 條件篩選  
- 只需多加 `when` 子句即可篩選「長邊 > 5」的圖形，無須額外 `if`。  
- 更貼近業務邏輯，降低 Bugs 機率。

**Cases 3**: IL 反組譯驗證  
- 以 ILDASM 反組譯，確認編譯器將 pattern 展開為常見 `as` 與 `if`，效能與舊寫法一致。  
- 團隊可安心採用新語法而不必擔心執行負擔。

---

