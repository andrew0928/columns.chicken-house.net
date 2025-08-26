果然沒啥人知道的 code, bug 也會比較慢被抓出來 ... 兩個小時前我才貼了找到 XmlNodeWriter 的替代品，用了一下就被我挖到一個 BUG ... @_@

先來看看我的 Sample Code:

**XmlTextWriter v.s. XmlWellFormedWriter**

```csharp
// test xml text writer, correct result
// output: <?xml version="1.0" encoding="big5"?><root><a/><a/><a/><a/><a/></root>
{
    Console.WriteLine("Using XmlTextWriter:");

    XmlWriter writer = XmlWriter.Create(Console.Out);
    writer.WriteStartElement("root");
    writer.WriteRaw("<a/><a/><a/><a/><a/>");
    writer.WriteEndElement();
    writer.Flush();

    Console.WriteLine();
    Console.WriteLine();
}


// test xml node writer, wrong result
// output: <?xml version="1.0" encoding="big5"?><root>&lt;a/&gt;&lt;a/&gt;&lt;a/&gt;&lt;a/&gt;&lt;a/&gt;</root>
{
    Console.WriteLine("Using XmlWellFormedWriter:");

    XmlDocument xmldoc = new XmlDocument();
    XmlWriter writer = xmldoc.CreateNavigator().AppendChild();
    writer.WriteStartElement("root");
    writer.WriteRaw("<a/><a/><a/><a/><a/>");
    writer.WriteEndElement();
    writer.Close();

    xmldoc.Save(Console.Out);
    Console.WriteLine();
    Console.WriteLine();
}
```

 

而這是程式的輸出畫面:

![image](/images/2008-12-08-system-xml-xmlwellformedwriter-bug/image_3.png)

 

兩段 code 除了拿到的 XmlWriter 來源不同之外，用它寫 XML DATA 的方式是一致的，不過寫出來的 XML 則完全不同。看來兩種 XmlWriter 對於 WriteRaw(...) 的實作不大相同。而照 MSDN 上的[說明](http://msdn.microsoft.com/zh-tw/library/0755ytay.aspx)來說，XmlTextWriter的行為是對的，XmlWellFormedWriter 則太雞婆了，沒事多作一次編碼...

 

該說運氣好嘛? 哈哈... 繼[上次撈到一個 SmtpMail 的 Bug](http://columns.chicken-house.net/post/e58e9fe4be86-SystemNetMail-e4b99fe69c83e69c89-Bug-.aspx) 之後，這次又撈到一個... 要用的人注意一下，不過即使有這個 Bug, 也不會影響它的地位啦，這 Writer 解決了我很大的困擾，動搖國本也要用下去... (咳... 不過是避開一個 API ...)

 

最後我改了用法，一方面 API 有 BUG 是一回事，另一方面直接用這 API 也很危險，因為 MSDN 說它不會去做內容的驗證，也就是說透過 WriteRaw( ) 寫進不合法的資料，會讓你整份輸出都毀了... 第二個原因比較重要，因此我換了一個替代作法, 類似 Pipe 一樣，把 XmlReader 讀到的東西都寫到 XmlWriter:

**XmlCopyPipe 實作**

```csharp
/// <summary>
/// 從 XmlReader 複製到 XmlWriter
/// </summary>
/// <param name="reader"></param>
/// <param name="writer"></param>
private static void XmlCopyPipe(XmlReader reader, XmlWriter writer)
{

    if (reader == null)
    {

        throw new ArgumentNullException("reader");

    }

    if (writer == null)
    {

        throw new ArgumentNullException("writer");

    }


    while (reader.Read() == true)
    {
        switch (reader.NodeType)
        {

            case XmlNodeType.Element:

                writer.WriteStartElement(reader.Prefix, reader.LocalName, reader.NamespaceURI);

                writer.WriteAttributes(reader, true);

                if (reader.IsEmptyElement)
                {

                    writer.WriteEndElement();

                }

                break;

            case XmlNodeType.Text:

                writer.WriteString(reader.Value);

                break;

            case XmlNodeType.Whitespace:

            case XmlNodeType.SignificantWhitespace:

                writer.WriteWhitespace(reader.Value);

                break;

            case XmlNodeType.CDATA:

                writer.WriteCData(reader.Value);

                break;

            case XmlNodeType.EntityReference:

                writer.WriteEntityRef(reader.Name);

                break;

            case XmlNodeType.XmlDeclaration:

            case XmlNodeType.ProcessingInstruction:

                writer.WriteProcessingInstruction(reader.Name, reader.Value);

                break;

            case XmlNodeType.DocumentType:

                writer.WriteDocType(reader.Name, reader.GetAttribute("PUBLIC"), reader.GetAttribute("SYSTEM"), reader.Value);

                break;

            case XmlNodeType.Comment:

                writer.WriteComment(reader.Value);

                break;

            case XmlNodeType.EndElement:

                writer.WriteFullEndElement();

                break;

        }
    }
}
```

 

很好用的作法，就像過去需要 COPY XML 資料，最常見的就是把來源跟目的都用 XmlDocument 載入，直接用 ImportNode( ) 把 XML 片段資料搬到另一個 XmlDocument 再儲存。跟上一篇的原因一樣，看起來很蠢... 就想到這個作法，透過 XmlReader, 拿到的是已經 parsing 過的資料，直接寫到 XmlWriter。而我用的 Writer 正好又可避開重複作 parsing 動作的優點，正好這樣效能跟可用性都兼顧了... 經過 parsing, 至少寫出來的東西會安心一點...

 

把最後我的程式搭配這個 XmlPipeCopy 改一改:

**用 XmlCopyPipe 取代 WriteRaw( )**

```csharp
XmlDocument xmldoc = new XmlDocument();
XmlWriter writer = xmldoc.CreateNavigator().AppendChild();
writer.WriteStartElement("root");

XmlReaderSettings settings = new XmlReaderSettings();
settings.ConformanceLevel = ConformanceLevel.Fragment;
XmlReader reader = XmlReader.Create(
    new StringReader("<a/><a/><a/><a/><a/>"),
    settings);
XmlCopyPipe(reader, writer);

writer.WriteEndElement();
writer.Close();

xmldoc.Save(Console.Out);
```

 

試了一下，果然如預期的執行了 :D，結果也沒錯，還好 XmlWellFormedWriter 的 Bug 只存在於 WriteRaw... 閃開就沒事了:

![image](/images/2008-12-08-system-xml-xmlwellformedwriter-bug/image_6.png)

 

 

其中有個陷阱，就是如何用 XmlReader 讀取 XmlFragment (可以有多個 ROOT 的 XML DATA)。其實這個解法跟程式碼，大部份都是[這篇](http://blogs.msdn.com/mfussell/archive/2005/02/12/371546.aspx)看來的，只不過在裡面加了個 LOOP 跟改了名字，各位覺的好用的話記得去謝原作者 [Mark Fussell](http://blogs.msdn.com/mfussell/), 別謝錯人了 :D