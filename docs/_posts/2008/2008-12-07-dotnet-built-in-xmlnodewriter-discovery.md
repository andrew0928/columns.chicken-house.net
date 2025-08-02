---
layout: post
title: "原來 .NET 早就內建 XmlNodeWriter 了..."
categories:

tags: [".NET","C#","Tips","作品集","技術隨筆","物件導向"]
published: true
comments: true
redirect_from:
  - /2008/12/07/原來-net-早就內建-xmlnodewriter-了/
  - /columns/post/2008/12/07/e58e9fe4be86-NET-FX-e697a9e5b0b1e69c89-XmlNodeWriter-e4ba86.aspx/
  - /post/2008/12/07/e58e9fe4be86-NET-FX-e697a9e5b0b1e69c89-XmlNodeWriter-e4ba86.aspx/
  - /post/e58e9fe4be86-NET-FX-e697a9e5b0b1e69c89-XmlNodeWriter-e4ba86.aspx/
  - /columns/2008/12/07/e58e9fe4be86-NET-FX-e697a9e5b0b1e69c89-XmlNodeWriter-e4ba86.aspx/
  - /columns/e58e9fe4be86-NET-FX-e697a9e5b0b1e69c89-XmlNodeWriter-e4ba86.aspx/
wordpress_postid: 49
---
最近事情一堆，上班忙上班的事，下班還在忙著研究 Enterprise Library, Entity Framework, 還有一堆五四三的，文章寫的就少了... 先跟有訂閱我 BLOG 的朋友們說聲道歉...。 不過在寫新專案的過程中，意外的發現這東西，一定要提一下...

 

不知道有多少人用過 XmlNodeWriter ? 我用這東西用很久了，當年 Microsoft 推出 .NET Framework 時，強調有很強的 XML 處理能力，其中 XmlReader / XmlWriter 就是以效能為考量，讓你避開處理大型 XML 資料效能很糟糕的 XmlDocument, 也不用去碰很難寫的 [SAX](http://zh.wikipedia.org/w/index.php?title=SAX&variant=zh-tw) 的替代方案...

無奈 Microsoft 內建的 XmlWriter 少的可憐，只能寫到檔案或是 TextWriter ... 看看權威的 MSDN 告訴我們[有那些 XmlWriter 可以用](http://msdn.microsoft.com/zh-tw/library/system.xml.xmlwriter.aspx)?

![image](/wp-content/images/2008-12-07-dotnet-built-in-xmlnodewriter-discovery/image_9.png)

老實說除了 XmlTextWriter 之外，另外兩個很少用的到。XmlWriter 在輸出 XML 時很好用 (如果你只作輸出的話)，複雜的 XML 輸出用 XmlWriter 比用 XmlDocument 簡單多了，不過最常碰到的情況是我還是想用 XmlDocument 來操作 XML，不過其中一部份的 NODE 想用 XmlWriter 來更新內容...

古早有位好心的 MVP 寫了 XmlNodeWriter, 就可以讓我這樣用:

**XmlNodeWriter Sample Code:**

```csharp
XmlDocument xdoc = new XmlDocument();
xdoc.LoadXml("<root><node1><data/><data/><data/></node1><node2/></root>");

XmlNodeWriter xnw = new XmlNodeWriter(xdoc.DocumentElement, true);

xnw.WriteStartElement("newNode");
xnw.WriteAttributeString("newatt", "123");
xnw.WriteCData("1234567890");
xnw.WriteEndElement();
xnw.Close();

xdoc.Save(Console.Out);
```

 

第一個參數是 XmlNode, 第二個參數是要不要清掉原來 Node 下的內容。很棒，我可以直接拿 XmlNode 當作 XmlWriter 輸出的對象，透過 Writer 寫出去的東西就直接反映在 XmlNode 身上了，省掉輸出成 Text 然後再 PARSING 回 XML NODE 這種蠢事...

 

前面只是緬懷 XmlNodeWriter 到底有多好用，現在找不到有多難過而已... 接下來才是正題...

 

不過現在想再去找 XmlNodeWriter 官方網站已經找不到了 @_@，原本這 lib 是 hosting 在 gotdotnet.com 這網站上，不過 Microsoft 已經把它關了，改成 [codeplex.com](http://www.codeplex.com/) / [MSDN Code Gallery](http://code.msdn.microsoft.com/) 取代，只好求助 GOOGLE 大神，無意間又發現這 Microsoft XmlTeam 的 [BLOG](http://blogs.msdn.com/xmlteam/)，[COMMENTS](http://blogs.msdn.com/xmlteam/archive/2007/02/02/xml-features-in-the-february-ctp-of-visual-studio-orcas.aspx#1586207) 有這麼一段:

 

> **# re: XML Features in the February CTP of Visual Studio "Orcas"**  
> Friday, February 02, 2007 8:27 PM by Stuart Ballard 
> 
> Is there going to be an XmlNodeWriter in Orcas? It's a fairly glaring hole, especially if you've ever wanted to apply an XSL transformation to an in-memory XmlDocument and get the result as another in-memory XmlDocument. You can pass the input to the transform via XmlNodeReader, but to get it back out again you just have to feed your XmlWriter to a StringBuilder and then parse it... 
> 
> Fortunately my use case wasn't performance-critical, but it's still ugly...
>  
> **# re: XML Features in the February CTP of Visual Studio "Orcas"**  
> Saturday, February 03, 2007 3:22 AM by Oleg Tkachenko 
> 
> Stuart, XmlNodeWriter in .NET 2.0 is hiding in 
> 
> xmlNode.createNavigator().AppendChild() method. It can be used to populate XmlNode via XmlWriter API and so you can 
> 
> XmlDocument doc = new XmlDocument(); 
> 
> using (XmlWriter writer = doc.CreateNavigator().AppendChild()) { 
> 
>   xslt.Transform(input, (XsltArgumentList)null, writer); 
> 
> } 
> 
> Mike, am I right that  Orcas January CTP includes none of these coolness?

真是太機車了，這麼好用的東西藏在這種地方? @_@，枉我從 .NET 1.0 beta 就開始用 C# 處理 XML，連 XSLT Extension 都寫過一堆， Trace Code 也追到 XSLT 內抓過一堆問題... 竟然連這東西都沒發現? 可惡...

於是手又癢了，拿來試用看看，發現只要動手寫幾行 Code, 我就能把 XmlNodeWriter 變回來了，像這樣:

 

**我的 XmlNodeWriter 實作**

```csharp
public class XmlNodeWriter : XmlWriter
{
    private XmlWriter _inner_writer = null;
    public XmlNodeWriter(XmlNode node, bool clean)
    {
        if (clean == true)
        {
            node.RemoveAll();
        }

        this._inner_writer = node.CreateNavigator().AppendChild();
    }


    #region 無聊的 "延長線" 程式碼...

    // 略! 共一百多行，補上廿幾個 abstract method / property, 把它接到 _inner_writer 上

    #endregion
}
```

 

這樣果真可以 WORK 了 :D  不過要真正變出一個新的 XmlNodeWriter 代價還不低，繼承 XmlWriter 的後果是有廿幾個 abstract method / property 得補上實作... 全都是很無聊的 code, 就是拿 _inner_writer 的直接套上去而已... 像這樣:

**"延長線" 型的程式碼**

```csharp
public override void Close()
{
    this._inner_writer.Close();
}

public override void Flush()
{
    this._inner_writer.Flush();
}

public override string LookupPrefix(string ns)
{
    return this._inner_writer.LookupPrefix(ns);
}
```

 

這堆 Code 我就不貼了，總之可以 WORK :D

 

![image](/wp-content/images/2008-12-07-dotnet-built-in-xmlnodewriter-discovery/image_10.png)

 

不過對 CODE 有點潔癖的我，越看越不是味道，就動起 Factory 的腦筋了。繼續改造一下... 原本 .NET 2.0 內建的 XmlWriter 就已經提供 Factory 的用法了，像這樣:

> XmlWriter my_writer = XmlWriter.Create( ... );

不過沒辦法不改 .NET FX 原始碼的情況下 "加掛" 我自己的 Create(...) 實作，原本腦筋是動到 C# 3.0 開始支援的 Extension Method, 不過它只支援 instance method, 不支援 static method ... 只好改成這樣:

 

**XmlWriterFactory 實作**

```csharp
public abstract class XmlWriterFactory : XmlWriter
{
    public static XmlWriter Create(XmlNode node)
    {
        return Create(node, false, null);
    }

    public static XmlWriter Create(XmlNode node, bool clearnContent)
    {
        return Create(node, clearnContent, null);
    }

    public static XmlWriter Create(XmlNode node, bool cleanContent, XmlWriterSettings settings)
    {
        if (node == null) throw new ArgumentNullException("node");

        if (cleanContent == true)
        {
            node.RemoveAll();
        }

        XmlWriter xw = node.CreateNavigator().AppendChild();

        if (settings != null)
        {
            xw = XmlWriter.Create(xw, settings);
        }

        return xw;
    }
}
```

 

沒事還繼承原本的 XmlWriter 只有一個目的，就是要延用它原來的 10 種 Create method 啊... 貼張圖為証，繼承之後我就有 13 種不同的 Create method 可以用... 不用再兩頭跑 (只是不能加在原本的 XmlWriter 上真是殘念， C# 什麼時後會支援 static method extension ?):

![image](/wp-content/images/2008-12-07-dotnet-built-in-xmlnodewriter-discovery/image_11.png)

 

 

當然，原程式只要改掉如何拿到 XmlWriter 那行而已，其它都照舊就可以執行了 :D

 

有需要的就拿去用吧，CODE 才十幾行，還包成 DLL 實在太麻煩了，需要的直接貼到你自己的 CODE 裡就好! 要散怖都隨便，沒有什麼授權問題，唯一的要求就是讓我知道我的 CODE 你有在用就好 :D，想讚助我的也很簡單，BLOG 上該多點幾下的東西，沒事就點一點... 哈哈
