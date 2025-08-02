---
layout: post
title: "泛型 + Singleton Patterns (II)"
categories:
- "系列文章: 泛型 + Singleton Patterns"
tags: [".NET"]
published: true
comments: true
redirect_from:
  - /2006/10/27/泛型-singleton-patterns-ii/
  - /columns/post/2006/10/27/e6b39be59e8b-2b-Singleton-Patterns-(II).aspx/
  - /post/2006/10/27/e6b39be59e8b-2b-Singleton-Patterns-(II).aspx/
  - /post/e6b39be59e8b-2b-Singleton-Patterns-(II).aspx/
  - /columns/2006/10/27/e6b39be59e8b-2b-Singleton-Patterns-(II).aspx/
  - /columns/e6b39be59e8b-2b-Singleton-Patterns-(II).aspx/
  - /blogs/chicken/archive/2006/10/27/1894.aspx/
wordpress_postid: 218
---

上篇因為貼 code , 放一起實在太長了, 只好分兩篇... 吊完胃口, 不囉唆了, 直接看我想出來的解法. 原則還是跟一般的函式庫一樣, 我希望先做出一個 base class, 把 singleton 的實作細節都處理掉, 函式庫的目的是讓使用你 lib 的人會很快樂才對, 因此 base class 可以辛苦點沒關係, 但是絕不能讓用你 code 的人得做苦工...

好了, 我實做出來的版本, code 如下:

```csharp
public class GenericSingletonBase<T>
    where T: GenericSingletonBase<T>,
    new()
{
    public readonly static T Instance = new T();
}
```

<!--more-->

沒看錯, 就是只有這幾行... 接下來貼的 code 是, 如果我自己要實作 singleton pattern 的 class 時, 該如何來用這個 lib:

```csharp
public class GenericSingletonImpl1
    : GenericSingletonBase<GenericSingletonImpl1>
{
    public GenericSingletonImpl1()
        : base()
    {
        Console.WriteLine("GenericSingletonImpl1.ctor()");
    }
}
```

扣掉非必要的 constructor, 其實 class 繼承的部份寫完, 就沒有其它必要的 code 了, 很好, 又滿足了我一個要求...

再來就剩最後一個, 要用這個 class 的 code 會不會像上一篇的例子一樣醜? 每次都要自己 casting ? 再看一下 code ...

```csharp
GenericSingletonImpl1 o1 = GenericSingletonImpl1.Instance;
GenericSingletonImpl1 o2 = GenericSingletonImpl1.Instance;
GenericSingletonImpl1 o3 = GenericSingletonImpl1.Instance;
```

很好, 收工... 哈哈... 謝謝大家的收看 [:D]
