---
layout: post
title: "Generic Type 的繼承..."
categories:
tags: [".NET","Tips","技術隨筆","物件導向"]
published: true
comments: true
redirect_from:
  - "/2007/02/12/generic-type-的繼承/"
  - /columns/post/2007/02/12/Generic-Type-e79a84e7b9bce689bf.aspx/
  - /post/2007/02/12/Generic-Type-e79a84e7b9bce689bf.aspx/
  - /post/Generic-Type-e79a84e7b9bce689bf.aspx/
  - /columns/2007/02/12/Generic-Type-e79a84e7b9bce689bf.aspx/
  - /columns/Generic-Type-e79a84e7b9bce689bf.aspx/
  - /blogs/chicken/archive/2007/02/12/2138.aspx/
wordpress_postid: 188
---

之前貼過一篇 Singleton 的文章 ([泛型 + Singleton Patterns](/post/e6b39be59e8b-2b-Singleton-Patterns.aspx), [泛型 + Singleton Patterns (II)](/post/e6b39be59e8b-2b-Singleton-Patterns-(II).aspx)), 就用到 base class 是 generic type 的作法, base class 可以是 generic type, 在繼承時直接給型別, 衍生出來的子類別就不再是 generic type 了.. 不過這種怪異的用法, 大概沒什麼書上的範例有講到, 也沒什麼書上有應用範例... 這完全是我自己亂配出來的藥方, 沒練過的人不要亂吃, 咳咳..

除了 Singleton 那種例子之外, 我另外碰到一個例子... 某個用 asp.net 開發的 project, 需要準備一套輸入各種型別資料的 control, 如基本的型別: string, int, bool, DateTime, TimeSpan... 及較複雜的自定型別, 如 MemberInfo, RoleInfo, ..... 等.

基本型別的部份, 大概大家都是搭配 asp:textbox, asp:checkbox, asp:calendar 這幾個控制項加一些 code 就搞定了, 反正用起來夠簡單, 也不用再呼它夠不夠精簡, 可不可以 reuse 了, 後面的自訂型別應該也不會太多, 可能土法練鋼, 每種各硬寫出個 user control 就解決了...

不過我怎麼能容忍這種 code 擺在我眼前? 哈哈... 看了就很不順眼... 以一般的 OO 觀點來看, 這些控制項應該有些共通的地方 (generalization) 能抽出來, 往上堆到 base class .. 不過卡在每種 user control **要輸入的型別跟本完全不一樣, 不是通通用 object 代替, 就是要寫的很醜**...

看到那段紅字, 大家大概就會聯想到泛型 (generic) 了, 沒錯... 不過套用到 control 的世界該怎麼用?

貼一段不能 run 的 sample ... base class 的部份:

```csharp
public class Editor<T> : System.Web.UI.UserControl {
    public abstract T Value { get; set; }
    // 其它就不干我的事了
}
```

之後假設我要寫個選日期的控制項, 只要這樣寫:

.ascx

```aspx
<asp:calendar runat="server" id="calendar1" />
```

.ascx.cs

```csharp
public class DateEditor : Editor<DateTime> {
    public override DateTime Value {
        get { return this.calendar1.SelectedDate; }
        set { this.calendar1.SelectedDate = value; }
    }
}
```

最後用起來就沒什麼特別的了, 大概像這樣:

```aspx
<chicken:DateEditor runat="server" value="2000/01/01" />
```

看到最後, 讓大家失望了 (H), 沒什麼特別的 code 嘛, 其實不然, 這個作法可以替你的 project 打下一個很好的基礎, 透過 generic 的 base class, 解決掉型別的問題後, 你就可以把各種型別的 editor 都綁在一起, 讓它們有共通的 base class, 這樣的好處很快就出現了, 有許多功能你就有機會只作一次, 每種不同的 editor 都能享用...:

1. 例: Editor 可以實作 "記住上次輸入的值" 這動作, 只要把 value set 的 code 插一段, 記到 file / db 之類的地方..., 所有 editor 自動都有這個能力了
2. 可以統一加上 OnChange Event, 所有的 editor 都可以有這事件讓寫 page 的人能應用
3. 因為所有的 editor 都有共同的 base class, 因此搭配 reflection 及 attribute, 你就能把 polymorphism 的技巧應用出來. 舉例來說, 你可以拿任意物件, 產生它專用的編輯畫面. 你可以透過 reflection api, 把所有的 field / property 名字及型別列出來, 同時在畫面上動態產生一個對應型別的 editor control ... 最後底下放個 [save] 的 button, 按下 ok 後自動的把每個 editor 收集到的值寫回 object ... 這一連串的動作如果沒有共同的 base class, 你是沒有辦法做的出來的
4. 其它 543 的功能, 你有辦法都可以加在 class Editor<T> 裡, 馬上所有的 Editor 都能夠繼承這些能力
5. 想不出來了, 剩下的原因只有這樣寫起來比較爽...

實際的 sample code 還真的不大好寫, 我碰到的 project 裡寫的東西又牽扯太多, 那天有空想要把它精簡一點的話再放 sample code, 不然就再說... 哈哈..
