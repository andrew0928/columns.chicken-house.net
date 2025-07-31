---
layout: post
title: "泛型 + Singleton Patterns"
categories:
- "系列文章: 泛型 + Singleton Patterns"
tags: [".NET"]
published: true
comments: true
redirect_from:
  - /2006/10/26/泛型-singleton-patterns/
  - /columns/post/2006/10/26/e6b39be59e8b-2b-Singleton-Patterns.aspx/
  - /post/2006/10/26/e6b39be59e8b-2b-Singleton-Patterns.aspx/
  - /post/e6b39be59e8b-2b-Singleton-Patterns.aspx/
  - /columns/2006/10/26/e6b39be59e8b-2b-Singleton-Patterns.aspx/
  - /columns/e6b39be59e8b-2b-Singleton-Patterns.aspx/
  - /blogs/chicken/archive/2006/10/26/1892.aspx/
wordpress_postid: 219
---

聽起來 singleton 跟 generic 好像搭不上邊, 不過搭配 .net framework 2.0 的 generic 機制, 倒是可以讓 singleton 好做很多... 我先簡單寫一下不使用 generic 時的做法...

只有單一 class 要實作 singleton 很簡單, 只要寫這樣的 code 就可以:

<!--more-->

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

    private SampleSingletonClass()
    {
        //
        // ToDo: constructor code here.
        //
    }
}
```

很標準的 code, 不是嗎? 不過問題來了... 當我有第二個 class 也要套用 singleton patterns 時, 幾乎一樣的 code 就得再抄一次, 只因為 public static XXX Instance; 這個 static property 的型別不一樣, 很討厭...

這堆看起來差不多的 code 想要省掉, 那只好動點手腳, 用繼承的技術解決, 不過問題又來了, 型別的宣告... 就像一堆 Collection 物件一樣, 傳回型別宣告為 object 就好了, 不過這樣的 code 用起來實在麻煩... 寫起來就像這樣:

```csharp
public class SingletonBase
{
    public static SingletonBase Instance(Type seed)
    {
        if (_singleton_storage[seed] == null)
        {
            _singleton_storage[seed] = Activator.CreateInstance(seed);
        }

        return _singleton_storage[seed] as SingletonBase;
    }

    private static Hashtable _singleton_storage = new Hashtable();
}

public class SingletonBaseImpl1 : SingletonBase
{
    public SingletonBaseImpl1()
        : base()
    {
        Console.WriteLine("SingletonBaseImpl1.ctor() called.");
    }
}

public class SingletonBaseImpl2 : SingletonBase
{
    public SingletonBaseImpl2()
        : base()
    {
        Console.WriteLine("SingletonBaseImpl2.ctor() called.");
    }
}
```

看來不怎麼漂亮? 不過看在重複的 code 只寫一次就好的份上, 醜一點關起門來就看不到了. 不過這樣就沒事了? 不... 用起來更醜... [:'(]

```csharp
SingletonBase.Instance(typeof(SingletonBaseImpl1));
SingletonBase.Instance(typeof(SingletonBaseImpl1));
SingletonBase.Instance(typeof(SingletonBaseImpl1));

SingletonBase.Instance(typeof(SingletonBaseImpl2));
SingletonBase.Instance(typeof(SingletonBaseImpl2));
SingletonBase.Instance(typeof(SingletonBaseImpl2));
```

實在無法接受這種 quality 的 "class library" ... 這種 code 看起來一點美感都沒有, 就像文筆不好的人在寫文章一樣...

處女座的個性, 實在不能容忍這種 code 出現在我的 project 裡... 碰到這種問題, 直覺的解決辦法就是:

1. 透過 inherence, 把這些重複的 code 集中到 super class 一次解決
2. 同樣邏輯, 要套用到不同型別的應用, 就用 generic 的方式處理

不過要實作還沒那麼簡單, 試了半天, 總算找出一種看起來最得意的解法... <待續>
