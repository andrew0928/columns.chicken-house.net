# Generic Type 的繼承...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 ASP.NET 的使用者控制項中，如何把「要輸入的資料型別」抽離，並同時保有共用的基底行為？
透過宣告一個泛型基底類別 Editor<T>，把「實際輸入／取得的值」以型別參數 T 抽象化，再由各種具體控制項 (如 DateEditor) 指定自己的 T 型別即可。如此一來，衍生類別不再是泛型，卻仍可共用 Editor<T> 所實作的行為。

## Q: Editor<T> 這個泛型基底類別最精簡的實作長怎樣？
```csharp
public abstract class Editor<T> : System.Web.UI.UserControl {
    public abstract T Value { get; set; }
    // 其餘共用功能都可以集中寫在這裡
}
```

## Q: 若要做一個日期用的輸入控制項 (DateEditor) ，要怎麼繼承 Editor<T>？
```csharp
// .ascx 只需放一個 <asp:Calendar>
<asp:calendar runat="server" id="calendar1" />

// .ascx.cs
public class DateEditor : Editor<DateTime> {
    public override DateTime Value {
        get { return this.calendar1.SelectedDate; }
        set { this.calendar1.SelectedDate = value; }
    }
}
```
使用時即可在頁面放上  
```aspx
<chicken:DateEditor runat="server" value="2000/01/01" />
```

## Q: 讓所有 Editor 衍生類別共用同一個基底類別，有哪些直接好處？
1. 可以在 Editor<T> 裡一次性實作「記住上次輸入值」等行為，所有衍生類別自動享用。  
2. 可統一加入 OnChange 事件，寫頁面的人不用理會是哪一種具體 Editor。  
3. 因為型別一致，能配合 reflection＋attribute 動態產生任何物件的編輯畫面 (polymorphism)。  
4. 其他想得到的共用功能都能集中寫在 Editor<T>，衍生類別立刻擁有。  
5. 最重要的：寫起來比較爽，程式碼更乾淨。