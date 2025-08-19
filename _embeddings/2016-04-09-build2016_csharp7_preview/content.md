---
layout: post
title: "//build/2016 - The Future of C#"
categories:
tags: [".NET","C#","MSDN","專欄","技術隨筆"]
published: true
comments: true
permalink: "/2016/04/09/build2016_csharp7_preview/"
redirect_from:
wordpress_postid: 1041
---

在寫這篇文章之前，一定要先秀一下我用了好幾年的桌布... :D

![](/wp-content/uploads/2016/04/img_5707dbccb3191.png)

從開始學寫 code 的第一天起 (正規開始學 coding 是大一計概，學寫 Fortran & C)，我就很講究 code 到底寫的漂不漂亮? 好不好懂? 好不好維護? 寫到後來，連 code 寫的夠不夠優雅都開始計較起來... 學了 OOP / Design Patterns 之後，就開始計較起 code 的結構到底正不正確? 是否跟真實要描述的事物有沒有正確的對應? 沒有的話就要改到滿意為止才罷休...

所以，當年在 MSDN 逛到這張桌布的時候 (現在找不到原始連結了) 就立刻拿來用了。我平常是不用桌布的，一裝好 windows 就把它改成黑色來用... 直到看到這張桌布為止...

<!--more-->

好吧，這其實不代表啥，只代表我對一行一行的 code 有潔癖而已 XD，常看我部落格的老讀者們，應該都對這幾篇有印象，我為何會一直用 .NET Framework, C# 的語法漂亮其實是主要原因... 在 [Anders Hejlsberg](https://github.com/ahejlsberg) 大神的掌舵之下，C# 有很多著名的 syntactic sugar .. 舉幾篇我寫過的文章，都是探討 C# 語法 & syntactic sugar 精妙的地方:

---

[[C#: yield return] #1. How It Work ?](http://columns.chicken-house.net/2008/09/18/c-yield-return-1-how-it-work/)

[[C# yield return] #2. 另類的應用 – Thread Sync 替代方案](http://columns.chicken-house.net/2008/09/21/c-yield-return-2-%e5%8f%a6%e9%a1%9e%e7%9a%84%e6%87%89%e7%94%a8-thread-sync-%e6%9b%bf%e4%bb%a3%e6%96%b9%e6%a1%88/)

[處理大型資料的技巧 – Async / Await](http://columns.chicken-house.net/2013/04/14/%e8%99%95%e7%90%86%e5%a4%a7%e5%9e%8b%e8%b3%87%e6%96%99%e7%9a%84%e6%8a%80%e5%b7%a7-async-await/)

[[CODE] LINQ to Object – 替物件加上索引!](http://columns.chicken-house.net/2011/10/25/code-linq-to-object-%e6%9b%bf%e7%89%a9%e4%bb%b6%e5%8a%a0%e4%b8%8a%e7%b4%a2%e5%bc%95/)

[Extension Methods 的應用: Save DataSet as Excel file…](http://columns.chicken-house.net/2010/11/06/extension-methods-%e7%9a%84%e6%87%89%e7%94%a8-save-dataset-as-excel-file/)

---

好，懷舊結束了，前面寫這段只是先讓大家知道，講 C# 我有多專精倒還不敢，但是講到我對 C# 7 提供的這堆 syntactic sugar 到底好不好用，我想我應該還有足夠的經驗來做點評論... //Build/2016 發表的 [The Future of C# (C# 7)](https://channel9.msdn.com/Events/Build/2016/B889), 這段 video 我花了一個多小時，反覆看了幾次.. 決定寫篇文章記錄一下我的看法...

<iframe width="640" height="360" src="https://channel9.msdn.com/Events/Build/2016/B889/player" allowfullscreen="allowfullscreen" frameborder="0"></iframe>

直接切入主題了，底下的 sample code 除了 tuple 的部分還沒辦法測試之外，其他其實我都已經實際編譯及執行過了。想嘗鮮的讀者們可以跳到最後一段，看看如何準備執行環境實際測試。這次公布的 C# 7 幾個新語法，都算是 syntactic sugar, 都屬於編譯器就可以處理掉的層級，不需要新的 Runtime 來支援，因此不用擔心編譯出來的 Code 無法在舊的平台上面執行。

這個 session 提到這幾個 C# 7 新的語法 (Visual Studio 15 Preview 尚不支援 Tuples & Records，其餘都已可體驗使用)

![](/wp-content/uploads/2016/04/img_5707e232050f3.png)

我比較囉嗦，對我有興趣的幾個新功能會多花點口舌來介紹，所以幾個基本的語法我就跳過了... 我只介紹我比較有興趣的三個: Tuples, Records, Pattern matching

# Tuples Literal, 一次傳回多個回傳值

也許是受到古早數學函數 (function, f(x) = x + 1) 這種型態的影響，我學過的 programming language 清一色都只能 return 單一一個傳回值。若有多個值要傳回，那只有把它包裝成複雜的物件，或是集合物件再傳回來，否則就要用其他非 return value 的管道.. 例如 Global Variable, Ref / Out parameters, Exception 等等做法。要傳回兩個以上的傳回值，同時還保有強型別的特性跟簡潔，就這麼難嗎?

先來看看只能傳回單一值的限制，造就多少可笑的 API interface 了... 我舉個知名的古典例子: ANSI C 定義的 standard C library 的 function: [int getchar()](https://msdn.microsoft.com/zh-tw/library/x198c66c(v=vs.80).aspx),

幫大家複習一下，這是 C 標準函式庫的一員，會從 stdin 讀取一個 char 後傳回來... 但是奇怪的地方是，明明是讀取 char, 為何傳回來的是 int ??? 來看看這段 sample code (這是錯誤的程式碼版本):

```c
char ch;

ch = getchar();

if (ch == EOF)
{
  // ...
}
else
{
  // use ch to do something...
}
```

看出端倪了嗎? 當年的 C 還沒有這麼多先進的機制，這個 function 除了要能傳回正常的傳回值 (char) 之外，還需要額外傳回 EOF 這特殊值。問題來了，宣告傳回值是 char 型別的話，那所有可能的傳回值都是合法的，沒有任何機會告訴呼叫者拿到的值是 EOF，不要拿去用... 不得已的情況下，只好擴充 return type, 從 char 擴大為 int ...

於是為了這種限制，只好把 getchar( ) 的 API 定義改成很可笑的 int getchar( ) ... 來看看 "語法正確" 的用法:

```c
int ch;

ch = getchar();

if (ch == EOF)
{
  // ...
}
else
{
  // 啊啊啊啊，你搞得我好亂啊...
  char temp = (char)ch;
}
```

的確是搞得我好亂啊，getchar( ) 你到底是傳回 char 還是 int 啊? 為何 getchar( ) 要用 int 去接，然後再 casting 成 char ....

探究根本的原因，就是我們必須在 "只能傳回單一值" 的限制內，同時擠進正常的傳回值，也要擠進錯誤代碼或是例外狀況的訊息，所付出的代價...。於是，在多年後的今天，C# 7 總算正式的回應這樣的需求了，那就是 Tuples !

我用傳回 Size 的 method 當作範例，Size 包括了 Height / Width 兩個數值。通常我們有這幾種方式可以處理:

1. 宣告物件 Size 來封裝 Width 及 Height，缺點是你必須額外定義類別... 如果你只用一次也是得這樣做...
(實在是很不想只為了用這一次就弄髒了 namespace 啊...)

```csharp
Size GetSize()
{
    return new Size(800, 600);
}

void Demo()
{
  Size s = GetSize();
  Console.WriteLine($"Size = ({s.Width}, {s.Height})");
}

class Size 
{
  int Width,
  int Height
}
```

2. 用 call by reference 的方式，透過參數來傳回多個數值，缺點是這看起來一點都不像 "return" value 啊...
只是當年 C++ 的 reference 技巧的 C# 版而已... 還得先準備 variables 丟過去，再回頭看看你塞了什麼值給我 @@

```csharp
void GetSize(out int width, out int height)
{
  width = 800;
  height = 600;
}


void Demo()
{
  int width;
  int height;

  GetSize(out width, out height);
  Console.WriteLine($"Size = ({width}, {height})");
}
```

3. .NET BCL 預先幫你準備好一組泛型的 Tuple 類別，讓你不用額外宣告，就有現成的類別可以封裝多個傳回值。
雖然解決了 (1) (2) 的困擾，但是... Tuple 只有讓擬定義封裝的型別能力而已，他的名字已被限制為 Item1, Item2...
看到這種命名，就跟我看到 database table 有人宣告 field1 ~ field10 一樣令人抓狂... @@

```csharp
Tuple<int, int> GetSize()
{
  return new Tuple<int, int>(800, 600);
}

void Demo()
{
  Tuple<int, int> s = GetSize();
  Console.WriteLine($"Size = ({s.Item1}, {s.Item2})");
}
```

4. 最後的絕招，總算在 C# 終於出現了，C# 7 syntactic sugar 提供了這樣的語法，來表達同一件事:

```csharp
(int Width, int Height) GetSize()
{
  return (Width: 800, Height: 600);
}

void Demo()
{
  var s = GetSize();
  Console.WriteLine($"Size = ({s.Width}, {s.Height})");
}
```

這樣看起來是不是舒服多了? 哈哈... 沒錯，至少滿足了我對程式碼的潔癖要求.. XD

不過，因為 Tuples 的 Sample Code 我還沒辦法實際執行，沒機會親眼瞧瞧他到底編譯了甚麼樣的 code 出來? 不過我猜八成跟 anonymous class 一樣，編譯器動態幫你 gen 一個給你專用的 class, 實際的結果應該跟 (2) 類似，唯一省掉的就是 coding 時可以少打幾個字，跟看起來清爽一點而已。實際的效能等等應該完全沒有差別吧?

最後，補充一下延伸的應用方式。其實這是 Tuples 的縮寫，也可以當作產生 Tuples 的 syntactic sugar .. 並非只能拿來用在一次傳回多個回傳值這情境。你也可以拿來直接產生 Tuple 物件作其他用途使用。例如:

```csharp
// tuple literals demo
var size = (width: 800, height: 600);
```

# Record Type, 只包含屬性的資料型別

雖然這個部分被歸在 Records ，但是我覺得他跟 Tuples 還蠻雷同的，我就改一下順序接在 Tuples 後面說明好了。前面介紹的 Tuples 的縮寫，可以直接用 (800, 600) 的方式，讓你打最少的字就可以產生一個 Tuple 物件。很多時候，尤其是從資料庫撈資料出來，往往我們為了強型別的各種好處，每個 table 我們都會宣告一個對應的 class... 討厭的是 SQL 我們不見得每次都會 select * from table ...那麼我們到底要宣告多少種 class ?

就定義上來說，Record Type 其實就是個特殊的 class, 它只包含 read only properties 的 data type, 它設計出來是為了要簡化這種 data type 的宣告過程。透過 Record Type 產生出來的 data type 都會自動實作 [IEquatable<T>](https://msdn.microsoft.com/zh-tw/library/ms131187(v=vs.110).aspx) 介面，意思是你可以直接比對兩個 Record Type 的物件是否相同? (value equal)

加上宣告這些 class 其實蠻囉嗦的，有一堆 code 要寫... 這我就直接撿現成的投影片:

![](/wp-content/uploads/2016/04/img_5707f180d508b.png)

我只是想要宣告一個物件 Person, 能包含他的 First Name, 及 Last Name 兩個 property 而已啊... 結果搞的落落長的宣告... 雖然可以靠 code generator 的方式解決，但是 code gen 的缺點就是 gen 出來之後要修改就很麻煩了。syntactic sugar 其實也是 code generator, 只不過他不是在你 coding time 產生 code, 而是在 compile time 才幫你產生，所以基本上你可以無視他，就當作有這種語法可以用就好... 底下那落落長的 code, 可以濃縮成一行就搞定:

```csharp
class Person(string First, string Last);
```

使用起來就跟一般類別無異，直接 new , 配合 [object initializer](https://msdn.microsoft.com/en-us/library/bb397680.aspx) 就可以了。不過 Records 就跟字串一樣，物件一旦被產生了就是不可更改的 (沒看到上方 gen 出來的 code, 屬性都只有支援 get 嗎?)，因此你要改變屬性值的話，就跟字串一樣，會產生一個新的物件來替換。語法比較特別，要用 with 就可以 "替換" 特定的屬性，產生一個新的物件給你:

```csharp
var me = new Person { First = "Andrew", Last = "Wu" };

var myson = me with { First = "Peter" };
```

// 註: 這種一旦被產生之後就不能改變內容的物件，就叫做 [immutable objects](https://en.wikipedia.org/wiki/Immutable_object) (又叫 unchangeable object)

最後，介紹一下延伸的應用。既然 Record Type 其實是個標準的 class, 所以他當然也支援最基本的類別繼承機制。舉例來說，我想定義多種幾何物件的型別的話，我可以這樣宣告:

```csharp
// 多邊形
class Geometry();

// 三角形
class Triangle(int Width, int Height, int Base) : Geometry;

// 矩形
class Rectangle(int Width, int Height) : Geometry;

// 正方形
class Square(int width) : Geometry;
```

# Pattern Matching, 物件的型別判定及比對語法

這是另一個重頭戲，Pattern Matching 想解決的問題，是當你有一堆各種型別的物件要處理時，通常會伴隨著 foreach loop, 以及一堆型別判定 ( [is operator](https://msdn.microsoft.com/en-us/library/scekt9xw.aspx) )，轉型 ([casting](https://msdn.microsoft.com/en-us/library/ms173105.aspx))，還有判斷 (condition) 等等操作。這整串操作的 code 寫下來，除了多寫好幾行之外，也多了很多很煩人的暫存物件。這種 code 寫多了其實真的會很煩躁啊啊啊啊...

延續前面提到的 Records Type, 產生 record objects 變容易了，於是我會有更多機會要過濾及處理這些 records。若我有個存放各種多邊形的陣列，然而我想寫一段 code 去統計它的各數及總面積... 過去我會這樣寫:

1. 設計各種多邊形的 class, 同時宣告計算面積的 abstract method, 衍生類別各自定義自己計算面積的公式。
2. 用多型的作法，foreach 跑過每一個物件，呼叫它的計算面積公式
3. 沿途加總各數及面積

傳統的方式，寫出來的 code 會像這樣:

```csharp
    static void Demo1()
    {
        // 產生各種幾何形狀的物件
        List<Geometry> shapes = new List<Geometry>()
        {
            new Triangle() { Side1 = 3, Side2 = 4, Side3 = 5},
            new Square() {Width=10 },
            new Triangle() { Side1 = 3, Side2 = 4, Side3 = 5},
            new Square() {Width=10 },
            new Rectangle() {Width=4, Height = 6 },
            new Square() {Width=10 },
            new Rectangle() {Width=4, Height = 6 },
            new Triangle() { Side1 = 3, Side2 = 4, Side3 = 5},
            new Triangle() { Side1 = 3, Side2 = 4, Side3 = 5},
            new Square() {Width=10 },
            new Square() {Width=10 },
            new Rectangle() {Width=4, Height = 6 },
            new Rectangle() {Width=4, Height = 6 },
            new Triangle() { Side1 = 3, Side2 = 4, Side3 = 5}
        };

        int total_area = 0;

        foreach(Geometry s in shapes)
        {
            total_area += s.GetArea();
        }

        Console.WriteLine($"Total area: {total_area}.");
    }

        

    public abstract class Geometry
    {
        public abstract int GetArea();
    }

    public class Triangle:Geometry
    {
        public int Side1 { get; set; }
        public int Side2 { get; set; }
        public int Side3 { get; set; }

        public override int GetArea()
        {
            int s = (this.Side1 + this.Side2 + this.Side3) / 2;
            return (int)Math.Sqrt(s * (s - this.Side1) * (s - this.Side2) * (s - this.Side3));
        }
    }

    public class Rectangle : Geometry
    {
        public int Width { get; set; }
        public int Height { get; set; }
        public override int GetArea()
        {
            return this.Width * this.Height;
        }
    }

    public class Square : Geometry
    {
        public int Width { get; set; }

        public override int GetArea()
        {
            return this.Width * this.Width;
        }
    }
```

來看看改用 C# 7 的新語法，來改寫看看。前題是我的目的只是單純的計算，沒有太多 code reuse 的考量，不需要建立太多沒機會被使用的 class 及 object，能夠最精簡最方便的 coding 為主。物件的部分就直接用前面提到的 Record Types 取代，而判定型別及計算的部分就讓 Pattern Matching 來發揮!

調整過的流程:

1. 直接用 records + 繼承，定義各種多邊形的 record types
2. 用 foreach 跑過每一個物件
3. 用 switch + pattern matching 區分各種物件，直接在 switch case 內引到到不同的程式碼去計算面積

```csharp
    static void Demo1()
    {
        // 產生各種幾何形狀的物件
        List<Geometry> shapes = new List<Geometry>()
        {
            new Triangle(3, 4, 5),
            new Square(10),
            new Triangle(3, 4, 5),
            new Square(10),
            new Rectangle(4, 6),
            new Square(10),
            new Rectangle(4, 6),
            new Triangle(3, 4, 5),
            new Triangle(3, 4, 5),
            new Square(10),
            new Square(10),
            new Rectangle(4, 6),
            new Rectangle(4, 6),
            new Triangle(3, 4, 5)
        };

        int total_area = 0;

        foreach(Geometry s in shapes)
        {
            switch (s)
            {
                case Triangle x:
                    int total_side = (x.Side1 + x.Side2 + x.Side3) / 2;
                    total_area += (int)Math.Sqrt(total_side * (total_side - x.Side1) * (total_side - x.Side2) * (total_side - x.Side3));
                    break;

                case Rectangle x:
                    total_area += x.Width * x.Height;
                    break;

                case Square x:
                    total_area += x.Width * x.Width;
                    break;
            }
        }

        Console.WriteLine($"Total area: {total_area}.");
    }

    public class Geometry();
    public class Triangle(int Side1, int Side2, int Side3) : Geometry;
    public class Rectangle(int Width, int Height) : Geometry;
    public class Square(int width) : Geometry;
```

Pattern Matching 的語法，很巧妙的把 is 跟 casting 合併成單一的指令。過去沒有這種 syntactic sugar 時，都得先用 is 判斷型別，之後再 casting。因為順序要是反了，就可能引發 InvalidCastException..

上面例子的 Pattern Matching 是搭配 switch case 使用的，我先改成 if else 的結構，再來對比看看新舊的用法:

使用 pattern matching 的 switch case 用法:

```csharp
switch (s)
{
    case Triangle x:
        int total_side = x.Side1 + x.Side2 + x.Side3;
        total_area += (int)Math.Sqrt(total_side * (total_side - x.Side1) * (total_side - x.Side2) * (total_side - x.Side3));
        break;

    case Rectangle x:
        total_area += x.Width * x.Height;
        break;

    case Square x:
        total_area += x.Width * x.Width;
        break;
}
```

使用 pattern match 的 if else 用法:

```csharp
if (s is Triangle x)
{
    int total_side = (x.Side1 + x.Side2 + x.Side3) / 2;
    total_area += (int)Math.Sqrt(total_side * (total_side - x.Side1) * (total_side - x.Side2) * (total_side - x.Side3));
}
else if (s is Rectangle x)
{
    total_area += x.Width * x.Height;
}
else if (s is Square x)
{
    total_area += x.Width * x.Width;
}
```

不使用 pattern match 的 if else 對等的用法:

```csharp
if (s is Triangle)
{
    Triangle x = (Triangle)s;
    int total_side = (x.Side1 + x.Side2 + x.Side3) / 2;
    total_area += (int)Math.Sqrt(total_side * (total_side - x.Side1) * (total_side - x.Side2) * (total_side - x.Side3));
}
else if (s is Rectangle)
{
    Rectangle x = (Rectangle)s;
    total_area += x.Width * x.Height;
}
else if (s is Square)
{
    Square x = (Square)s;
    total_area += x.Width * x.Width;
}
```

其實最大的差別，就是邏輯上單一的操作，硬要拆成兩段來處理而已。其實類似的狀況，在 .NET Framework 裡的 basic class library 裡也常看到，最常見的就是基本型別的 TryParse( ... ) 也是異曲同工之妙 (例如: [int.TryParse()](https://msdn.microsoft.com/zh-tw/library/f02979c7(v=vs.110).aspx) )。Parse 需要先判斷格式，格式正確後才能解析字串內容傳回結果。TryParse( ... ) 就可以在單一一次呼叫內完成這兩個動作，在 code 的層面上，把它變成不可切割的行為 (atom operation)。

Pattern Matching 當然不只如此，只是省一行也太小看它了。既然這語法的目標在於 "Pattern" matching, 那麼對於處理 Pattern 絕對不止處理型別而已。在這邊的 Pattern, 指的是對應物件的樣式，包含要挑出特定的型別，甚至是特定屬性包含特定的值，都在處理範圍內。

舉個實際的例子好了，延續上述的例子，同樣一堆多邊形的物件，如果我統計只想挑出高度大於 5 的物件出來計算的話 (三角形拿第一個邊長當作高度)，那麼 Pattern Matching 的 when 子句就可以派上用場:

```csharp
switch (s)
{
    case Triangle x when x.Side1 > 5:
        int total_side = (x.Side1 + x.Side2 + x.Side3) / 2;
        total_area += (int)Math.Sqrt(total_side * (total_side - x.Side1) * (total_side - x.Side2) * (total_side - x.Side3));
        break;

    case Rectangle x when x.Height > 5:
        total_area += x.Width * x.Height;
        break;

    case Square x when x.Width > 5:
        total_area += x.Width * x.Width;
        break;
}
```

when 後面就接正常的判斷式即可，就跟 if ( ) 裡面的判斷式一樣。透過這些組合，pattern matching 能夠一次處理完物件的型別及屬性的判斷。我覺得它最大的意義，不只是替你省掉幾行 code 而已，而是在大幅提高程式碼的可讀性，讓你的 code 更直接的反應出你思考的邏輯。寫出來的 code 不必因為語法的限制，把單一的邏輯判斷，硬生生的拆成好幾個分開的語句。這種機械式的動作不需要花費寶貴的人力來做啊，編譯器來做這種事又快又好..

這段 code 正好可以用 Visual Studio 15 Preview 編譯，一時手癢，就把 switch case 的部分用 [ILDASM](https://msdn.microsoft.com/zh-tw/library/f7dy01k1(v=vs.110).aspx) 反組譯來看看，編譯器替我們做了什麼事:

![](/wp-content/uploads/2016/04/img_57088a511fe94.png)

註解的部分，是對應的 C# 原始碼，可以對照著看。CLR 的 IL 如果看不懂指令是什麼意思，可以參考 Wiki 的[這篇文章: List of CIL instructions](https://en.wikipedia.org/wiki/List_of_CIL_instructions)。至於 IL 的語法... Orz, 這我沒辦法簡短的說明，有學過組合語言，加上對於 stack machine 有概念的話就看的懂了! 突然很感謝大三時跑去修資工的課 (系統程式)，這門課的作業是要寫 stack machine 的模擬器... 沒想到當年作業學到的知識現在還派的上用場 XD

```csharp
 int total_area = 0;
    foreach (Geometry s in shapes)
    {
        Geometry geometry = s;
        Triangle x = geometry as Triangle;
        if ((x != null) && (x.Side1 > 5))
        {
            int total_side = ((x.Side1 + x.Side2) + x.Side3) / 2;
            total_area += (int) Math.Sqrt((double) (((total_side * (total_side - x.Side1)) * (total_side - x.Side2)) * (total_side - x.Side3)));
        }
        else
        {
            Rectangle x = geometry as Rectangle;
            if ((x != null) && (x.Height > 5))
            {
                total_area += x.Width * x.Height;
            }
            else
            {
                Square x = geometry as Square;
                if ((x != null) && (x.Width > 5))
                {
                    total_area += x.Width * x.Width;
                }
            }
        }
    }
    Console.WriteLine($"Total area: {total_area}.");
```

看 IL 實在太辛苦了，我看的懂可是很難解釋啊... 於是我把編譯好的 .exe 拿去給 [.NET Refactor](http://www.red-gate.com/products/dotnet-development/reflector/) 還原成 C# 6 的 code, 看得比較輕鬆一點。

還原後就可以很清楚的看到，C# 7 編譯器幫我們產生什麼樣的 code 了... 首先，switch case 就是翻成對等的 if else 而已。接下來 pattern matching 就真的如我預期，另外宣告變數，用 as 轉型後，產生一連串的 if (condition) 來達成 pattern match 的目的。其實這段 IL / 反組譯的結果可以證明，編譯器就真的是把一串動作拆成非 C# 7 的版本而已。所以如果你以為改用新語法會對效能有任何改善，就別肖想了... 他就真的只是讓你語法簡潔一點的改變而已。已經寫好的 code 除非你很在意 code 好不好看，不然不大需要刻意拿出來重改重新編譯..

另外，在使用時機上，也不用因為有了新語法就一頭熱，全部拋棄原有的寫法。以這個例子來說，我的第一個範例 (多型的版本) 跟第二個範例 (Pattern Match 的版本) 其實各有優缺點。

如果你的物件邏輯比較複雜，需要高度的封裝 (大小、狀態資訊，及對應的運算)，同時類似的運算操作 (如此例的計算面積加總) 會出現在好幾個地方的話，那麼多型的寫法是比較適合的。你會看到多型的寫法，花了比較多的精神在封裝物件，封裝帶來的好處是主程式非常精簡，遠比 Pattern Match 的版本還要乾淨漂亮。

```csharp
int total_area = 0;

        foreach(Geometry s in shapes)
        {
            total_area += s.GetArea();
        }
```

但是如果你沒這些需求，或是物件的來源已經是從資料庫或是 JSON 之類轉移過來，已經沒有機會把運算的部分包進去的話，其實不用動用到那麼多物件導向的高級技巧... Pattern Match 比較直覺的語法是有優勢的。

其實，看完這個 session 之後，有個感想: C# 受到近幾年來很熱門的 JavaScript 影響很大。JavaScript 紅到什麼程度? 由於實在太熱門，熱門到程式語言的物件表示方式，都可以變成結構化資料的儲存格式，跟前後端資料傳輸的標準格式 (JSON)。感覺起來 Tuples, Records, 還有 Pattern Matching 也都逐步的朝向這方面在演進。前面兩個語法，讓你用程式碼產生大量複雜結構的物件變的更容易，而 Pattern Matching 則讓你做物件的搜尋與樣式比對變的更容易。雖然 C# 不會也不大可能取代 JSON 的地位，不過至少這樣的改變，讓我們在程式碼內處理大量資料的時候，可以寫出更簡潔的 code, 這也是件好事吧? :D

# Visual Studio 15 Preview 啟用 C# 7 新語法支援

最後，補上怎麼體驗 C# 新語法的方法!

第一件事，當然是先去下載 Visual Studio 15 Preview 回來安裝... 別把他跟 VS 2015 搞混了喔...VS 2015 如果照版本號碼來看應該是 14.0 版，而這次預覽的是 15.0 版本，將來正式推出應該是 VS 2016 或是 VS 2017 了..

受惠於 Roslyn 的架構，編譯器及 IDE 要支援這些語言的新機制更容易了。這次的 VS 15 就已經內建了 C# 7 的支援，只不過預設是停用的，要啟用它的話，需要在你的專案裡面條件式編譯，定義這兩個 symbols:  __DEMO__, __DEMO_EXPERIMENTAL__ 。

找不到在哪裡的，可以看截圖: 專案 > 屬性 > Build

![](/wp-content/uploads/2016/04/img_5708950c6a29a.png)

修改完成後，你就可以直接寫 code 了，可以正常編譯，IDE editor 也不會有語法錯誤的警告:

![](/wp-content/uploads/2016/04/img_570895657bebe.png)

# 後記

[![csharp[1]](http://columns.chicken-house.net/wp-content/uploads/2016/04/csharp1.jpg)](http://columns.chicken-house.net/wp-content/uploads/2016/04/csharp1.jpg)

中文的技術部落格，大多都是講 How To, 很少碰到跟我一樣對語法有高度潔癖的探討文章 @@，所以這次我就野人獻曝的整理這一篇，希望能幫助到有需要的人!

最後，不知看過這段 channel 9 video 的人有沒有發現? 兩位講者身上的 T 恤上有印著超人圖案，不過裡面寫的不是 S，而是 C# ... 哈哈! 這件衣服太讚了，不知有沒有機會買到? 真想去弄一件.. :D

結果在講師的部落格找到這張圖.. 就拿來當本篇文章的 LOGO 吧 XD

# References

[The Future of C#](https://channel9.msdn.com/Events/Build/2016/B889#formats)

[C# 7 features preview](http://asizikov.github.io/2016/04/02/csharp-seven-preview/)

[C# 7: New Features](https://www.kenneth-truyers.net/2016/01/20/new-features-in-c-sharp-7/)

[Enabling C# 7 Features in Visual Studio "15" Preview](http://www.strathweb.com/2016/03/enabling-c-7-features-in-visual-studio-15-preview/)

[C# Futures: Tuples and Anonymous Structs](http://www.infoq.com/news/2015/04/CSharp-7-Tuples)

[Proposal: Language support for Tuples #347](https://github.com/dotnet/roslyn/issues/347)

[C# 7新語法預覽](https://dotblogs.com.tw/wellwind/2016/04/05/the-future-of-csharp-7)

[C# Design Notes for Jan 21, 2015 #98](https://github.com/dotnet/roslyn/issues/98)
