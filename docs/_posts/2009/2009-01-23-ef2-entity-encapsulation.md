---
layout: post
title: "EF#2. Entity & Encapsulation"
categories:
- "系列文章: Entity Framework 與 物件導向設計"
tags: [".NET","C#","SQL","物件導向", "Entity Framework"]
published: true
comments: true
permalink: "/2009/01/23/ef2-entity-encapsulation/"
redirect_from:
  - /columns/post/2009/01/23/EF2-Entity-Encapsulation.aspx/
  - /post/2009/01/23/EF2-Entity-Encapsulation.aspx/
  - /post/EF2-Entity-Encapsulation.aspx/
  - /columns/2009/01/23/EF2-Entity-Encapsulation.aspx/
  - /columns/EF2-Entity-Encapsulation.aspx/
wordpress_postid: 43
---

前一篇講了一堆大道理，這篇就來看一些實作吧。各種 ORM 的技術都有共同的目的，就是能把物件的狀態存到關聯式資料庫，而這樣的對應機制則是各家 ORM 競爭的重點，勝負的關鍵不外乎是那一套比較簡單? 那一套包裝出的 Entity 物件能夠更貼近一般的物件?

會有這樣的 "對應" 機制需求，原因只有一個，物件技術發展的很快，已經能解決大多數軟體開發的需求了，不過資料庫就沒這麼幸運，現在的 DBMS 撇開一些技術規格不談，本質上還是跟廿年前差不多，就是關聯式資料庫而已，本質上就是一堆 table + relationship, 配合 SQL 語法來處理資料。發展至今，物件技術跟資料庫技術能處理的問題，已經是兩個完全不同世界的問題了，三層式的架構在這段出現斷層...。

解決方式大概有兩條路，一種就是想辦法把這兩個世界串起來，就是 ORM framework 想做的事。另一個就是改造 RDBMS，讓 RDBMS 進化成也具有物件導向特性的資料庫。不過以眼前的五年十年來看，ORM 還是大有可為。ORM 只要能把 "對應" 這件事做到完美的地步，其實在某個層面上就已經做到 OODB 的願景了，只差在這些物件是活在 APP 這端，不是活在資料庫那端...。

扯遠了，接下來我會試著從物件技術的三大核心 (封裝、繼承、多型)，及資料庫最需要的查尋機制 (QUERY) 來看看 Entity Framework 各能提供什麼支援，才能客觀的評論 Entity Framework 值不值得你投資在它身上。

在繼續看下去之前，請先俱備基本的 Entity Framework 運用的能力。在 [MSDN 名家專欄裡 MVP(朱明中)](http://www.microsoft.com/taiwan/msdn/columns/jhu_ming_jhong/) 寫的這幾篇我覺的很不錯，可以參考看看。我就是看這幾篇入門的 :D。幾年前在比賽上碰過他幾次，我還蠻配服他的，可以靠自學而有今天的成就。以下是他寫的幾篇 ADO.NET / Entity Framework 的系列文章:

1. [讀寫 ADO.NET Entity Framework](http://www.microsoft.com/taiwan/msdn/columns/jhu_ming_jhong/ADO.NET_Entity_Framework_Entity_Operation.htm) (2007 年 9 月)
2. [由 LINQ 存取 ADO.NET 物件](http://www.microsoft.com/taiwan/msdn/columns/jhu_ming_jhong/ADO.NET_Entity_Framework_Interaction_to_ADO.NET_data_objects.htm) (2007 年 9 月)
3. [整合 ADO.NET Entity Framework 到應用程式中](http://www.microsoft.com/taiwan/msdn/columns/jhu_ming_jhong/ADO.NET_Entity_Framework_Integration_with_exist_applications.htm) (2007 年 9 月)
4. [首次接觸 ADO.NET Entity Framework](http://www.microsoft.com/taiwan/msdn/columns/jhu_ming_jhong/ADO.NET_Entity_Framework_A_First_look.htm) (2007 年 9 月)
5. [ADO.NET Entity Framework 概觀](http://www.microsoft.com/taiwan/msdn/columns/jhu_ming_jhong/ADO.NET_Entity_Framework_Overview.htm) (2007 年 9 月)

在開始之前，我們先來看看一個最簡單的 Entity Framework 的範例，然後來看看封裝性能夠對你的程式帶來什麼影響? 先來看看只用到了 ORM 卻沒發揮封裝性的例子:

![image](/wp-content/be-files/WindowsLiveWriter/EF2.Entityencapsulation_14856/image_thumb_1.png)

這是存放會員資料的表格，對應的 TABLE 很簡單，SQL 如下:

```sql
CREATE TABLE [dbo].[Users](
	[ID] [nvarchar](50) NOT NULL,
	[PasswordHash] [image] NOT NULL,
	[PasswordHint] [nvarchar](100) NOT NULL,
	[SSN] [nchar](10) NOT NULL,
	[Gender] [int] NOT NULL,
 CONSTRAINT [PK_Users] PRIMARY KEY CLUSTERED
ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
```

大部份的人在 EDMX Designer 裡把資料表拉進來後，就開始用這個 Entity Class 了吧? 密碼的部份為了安全及實作上的考量，DB只存放 HASH，而 HASH 的運算則透過 .NET 程式來計算，不透過 SQL 的函數。作法決定後，你可能會寫出這樣的程式碼:

**建立帳號的程式碼**

```csharp
// 準備 object context
using (Membership ctx = new Membership())
{
    // create user account:
    User newUser = new User();

    newUser.ID = "andrew";
    newUser.PasswordHint = "12345";
    newUser.PasswordHash = HashAlgorithm.Create("MD5").ComputeHash(Encoding.Unicode.GetBytes("12345"));
    newUser.SSN = "A123456789";
    newUser.Gender = 1;

    ctx.AddToUserSet(newUser);
    ctx.SaveChanges();
}
```

**檢查密碼的程式碼**

```csharp
// 準備 object context
using (Membership ctx = new Membership())
{
    string passwordText = "12345";
    User curUser = ctx.GetObjectByKey(new EntityKey("Membership.UserSet", "ID", "andrew")) as User;

    bool isPasswordCorrect = true;

    {
        byte[] passwordTextHash = HashAlgorithm.Create("MD5").ComputeHash(Encoding.Unicode.GetBytes(passwordText));
        if (passwordTextHash.Length != curUser.PasswordHash.Length)
        {
            isPasswordCorrect = false;
        }
        else
        {
            for (int pos = 0; pos < curUser.PasswordHash.Length; pos++)
            {
                if (passwordTextHash[pos] != curUser.PasswordHash[pos])
                {
                    isPasswordCorrect = false;
                    break;
                }
            }
        }
    }

    Console.WriteLine("Password ({0}) check: {1}", passwordText, isPasswordCorrect ? "PASS" : "FAIL");
}
```

這樣的 User 類別設計有什麼問題? 我列幾個我認為設計上不妥的地方:

1. 直接提供 PasswordHash 曝露過多不必要的實作細節
2. 在台灣，身份證字號 (SSN) 跟性別 (Gender) 是相依的欄位 ( functional dependency )

以物件導向的角度來看，User 真正要提供的是接受 "驗證密碼" 的要求，至於你的實作是提供明碼或是用 Hash, 都是實作的細節。提供原始未加密的密碼，或是提供處理過的 HASH，在需求上都是不必要個功能。物件的介面定義要盡量以能滿足需求的最小介面為原則，其它的都不要公開，才滿足 "封裝性" 的要求。因此良好的設計應該把這些細節封裝起來，只在公開的介面表達你要提供的功能。

另外依照[台灣的身份證字號規則](http://zh.wikipedia.org/wiki/%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E5%9C%8B%E6%B0%91%E8%BA%AB%E5%88%86%E8%AD%89#.E7.B7.A8.E8.99.9F.E8.A6.8F.E5.89.87)， SNN 跟 Gender 是連動的。目前 User 的設計是把兩者的關係丟給前端寫網頁的人來維護，一不注意就會發生不一致的情況。DB 對於這種問題的解決方式，不外乎寫 trigger 或是其它 constraint 的方式來阻擋不正確的資料被寫入 DB，不過看了前面提到的規則，要單純用 SQL 的功能完整實作出來，還不大容易。

另一種作法，只儲存 SSN，Gender 欄位則以 VIEW 的方式提供，這樣就不會有不一致的問題。不過這方法的缺點在於，當邏輯太複雜的時後，常常會超出 SQL 能處理的範圍，效能也許會是個問題，或是 constraint 不能完全跟程式端一致。

就我看來，這類看似應該在 data layer 實作的複雜邏輯，又難以在 SQL DB 上面解決的問題，才是 Entity Framework 的強項。現在來看看 Entity Framework 能怎麼解決這些資料封裝的需求:

首先，把不需要公開的細節改成 Private 隱藏起來，包括 PasswordHash 的 Getter / Setter, Gender 更名為 GenderCode, 同時把 Getter / Setter 也改為 Private ...

接下來就要把這些封裝起來的細節，提供另一組較合適的公開資訊的方式。這時 .EDMX designer 替我們產出的 code 就能搭配 partial class 擴充功能了。來看看我們在 partial class 裡寫了什麼?

**User.cs 的內容 (partial class)**

```csharp
public partial class User
{
    public string Password
    {
        set
        {
            this.PasswordHash = this.ComputePasswordHash(value);
        }
    }

    public bool ComparePassword(string passwordText)
    {
        byte[] hash = this.ComputePasswordHash(passwordText);

        // compare hash
        if (this.PasswordHash == null) return false;
        if (hash.Length != this.PasswordHash.Length) return false;
        for (int pos = 0; pos < hash.Length; pos++)
        {
            if (hash[pos] != this.PasswordHash[pos]) return false;
        }
        return true;
    }

    public GenderCodeEnum Gender
    {
        get
        {
            return (GenderCodeEnum)this.GenderCode;
        }
    }

    partial void OnSSNChanging(string value)
    {
        // ToDo: check ssn rules.

        // sync gender code
        this.GenderCode = int.Parse(value.Substring(1, 1));
    }




    private byte[] ComputePasswordHash(string password)
    {
        if (string.IsNullOrEmpty(password) == true) return null;
        return HashAlgorithm.Create("MD5").ComputeHash(Encoding.Unicode.GetBytes(password));
    }
}

public enum GenderCodeEnum : int
{
    FEMALE = 0,
    MALE = 1
}
```

被隱藏起來的 PasswordHash, 公開的介面就用 Password 的 Setter 跟 ComparePassword( ) method 取代，明確的用程式碼告訴所有要用它的 programmer:

"密碼只准你寫，不准你讀 (read only)... 只告訴你密碼對不對, 不會讓你把真正的密碼拿出去"

另一個部份，就是身份證字號跟性別的問題，則改用另一個方式解決。SSN 這個屬性維持不變，在它被更動時就一起更動 GenderCode 這個欄位。GenderCode 完全不對外公開，公開的只有把 int 轉成 GenderCodeEnum 的屬性: Gender。同時為了保護資料的正確性，只開放 Getter, 不開放 Setter。

同樣的程式，在我們調整過 Entity 的封裝之後，再來重寫一次看看:

**建立新的使用者帳號**

```csharp
// 準備 object context
using (Membership ctx = new Membership())
{
    User newUser = new User();

    newUser.ID = "andrew";
    newUser.PasswordHint = "My Password: 12345";
    newUser.Password = "12345";
    newUser.SSN = "A123456789";

    ctx.AddToUserSet(newUser);
    ctx.SaveChanges();
}
```

**檢查密碼是否正確**

```csharp
// 準備 object context
using (Membership ctx = new Membership())
{
    EntityKey key = new EntityKey("Membership.UserSet", "ID", "andrew");
    User user = ctx.GetObjectByKey(key) as User;

    // 要比對的密碼
    string passwordText = "123456";
    bool isPasswordCorrect = user.ComparePassword(passwordText);

    Console.WriteLine("Password ({0}) check: {1}", passwordText, isPasswordCorrect ? "PASS" : "FAIL");
}
```

修改過的程式簡潔多了。不過比少打幾行程式碼更重要的是，它的邏輯更清楚，更不容易出錯。如果沒有妥善的處理封裝性的問題，可以想像寫出來的程式一定亂七八糟。要嘛不正確的資料都會被寫進 DB，不然就是 DB 有作適當的防範，但是程式沒有作好，最後就是到處都出現 SqlException ...

這裡只是簡單示範一下 Entity Framework 如何替資料提供封裝的特性，後續的文章會繼續示範 Entity Framework 如何能把 DBMS 的資料，進一步的應用到物件技術的繼承及多型等特性。敬請期待下集 :D
