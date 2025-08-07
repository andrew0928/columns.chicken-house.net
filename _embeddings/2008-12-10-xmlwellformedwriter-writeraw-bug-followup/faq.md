# XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Microsoft 對於在 XmlDocument / XDocument (透過 XPathNavigator) 上呼叫 XmlWellFormedWriter.WriteRaw() 的行為有什麼結論？
官方表示這並不是 Bug，而是「設計使然」(by design)。由於 WriteRaw 可能被分成多次呼叫、且可與其他 XmlWriter 呼叫交錯並多層巢狀，若要在此情境下把 WriteRaw 的輸入當成 XML 片段再解析成節點，實作上相當困難。因此團隊選擇把 WriteRaw 的內容一律當作純文字處理。

## Q: 如果我手上已經有一段 XML 字串，想要插入到 XmlDocument，該用什麼做法來取代 WriteRaw？
Microsoft 建議的兩種替代方式：
1. 直接利用節點的 InnerXml 屬性  
   ```csharp
   XmlDocument doc = new XmlDocument();
   XmlElement root = doc.CreateElement("root");
   root.InnerXml = "<a/><a/><a/><a/><a/>";
   doc.AppendChild(root);
   ```
2. 透過 XPathNavigator.AppendChild() 取得 XmlWriter，再使用 XmlReader + WriteNode  
   ```csharp
   XmlDocument doc = new XmlDocument();
   XmlWriter writer = doc.CreateNavigator().AppendChild();
   writer.WriteStartElement("root");
   using (XmlReader r = XmlReader.Create(
           new StringReader("<a/><a/><a/><a/><a/>"),
           new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment }))
   {
       writer.WriteNode(r, false);
   }
   writer.WriteEndElement();
   writer.Close();
   doc.Save(Console.Out);
   ```

## Q: 為什麼 Microsoft 沒改成在不支援的情境直接丟出 NotSupportedException，而是維持目前「把內容當文字」的實作？
回覆中並未明確說明，但從說明可推測：相較於拋出例外，他們認為保持現行實作（將輸入視為文字）對既有程式碼影響最小，也避免了實作解析整段片段所需的大量複雜度與效能成本。