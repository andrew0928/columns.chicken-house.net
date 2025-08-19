---
layout: post
title: "XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展"
categories:

tags: [".NET","C#","MSDN","Tips","技術隨筆","有的沒的"]
published: true
comments: true
redirect_from:
  - /2008/12/10/xmlwellformedwriter-writeraw-的-bug-後續發展/
  - /columns/post/2008/12/10/XmlWellFormedWriterWriteRaw(-)-e79a84-Bug-e5be8ce7ba8ce799bce5b195.aspx/
  - /post/2008/12/10/XmlWellFormedWriterWriteRaw(-)-e79a84-Bug-e5be8ce7ba8ce799bce5b195.aspx/
  - /post/XmlWellFormedWriterWriteRaw(-)-e79a84-Bug-e5be8ce7ba8ce799bce5b195.aspx/
  - /columns/2008/12/10/XmlWellFormedWriterWriteRaw(-)-e79a84-Bug-e5be8ce7ba8ce799bce5b195.aspx/
  - /columns/XmlWellFormedWriterWriteRaw(-)-e79a84-Bug-e5be8ce7ba8ce799bce5b195.aspx/
wordpress_postid: 47
---
一時順手，就按下 Visual Studio 2008 上面的 [Report Bug] 回報[上一篇](http://columns.chicken-house.net/post/e58e9fe4be86-XmlWellFormedWriter-e4b99fe69c89-Bug-.aspx)發現的 Bug, 沒想到 Microsoft 真的有回應耶... :D

反正 Microsoft 在 connect 裡的回應本來就公開的，我就順手貼一下:

 

[https://connect.microsoft.com/VisualStudio/feedback/ViewFeedback.aspx?FeedbackID=386899&wa=wsignin1.0](https://connect.microsoft.com/VisualStudio/feedback/ViewFeedback.aspx?FeedbackID=386899&wa=wsignin1.0)

 

Hello,  
Originally the WriteRaw method was designed for XmlWriters that are formatting text XML into a file. In those cases the WriteRaw method can be used to write out an XML fragment that is already formatted and checked for well-formedness. It can also be used for writing text nodes with special character that have been already escaped and no further processing of the text is needed.  
However, when we introduced the XmlWriter over XmlDocument/XDocument (accessed via XPathNavigator editing methods), the use of the WriteRaw method on top of XmlDocument became controversial. We had two options:  
1.   Threat it as a text  
2.   Parse it into nodes

The second option is very difficult (if not possible) to do. The XML fragment can we written out in multiple WriteRaw calls, so we could not assume that a single WriteRaw will contain a fully enclosed fragment. It can also be interleaved with other XmlWriter calls and nested many times – overall a very hard thing to implement properly. So that is why we have decided to treat the WriteRaw content as text, which is what you are seeing.  
If you have an XML fragment in a string and you want to append it to XmlDocument, you can do it like this:

               XmlDocument doc = new XmlDocument();  
               XmlElement rootElement = doc.CreateElement("root");  
               rootElement.InnerXml = "<a/><a/><a/><a/><a/>";  
               doc.AppendChild(rootElement);

Or if you really want to use the XmlWriter from XPathNavigator.AppendChild(), you can create an XmlReader over your fragment and use the WriteNode method on the XmlWriter:

               XmlDocument doc = new XmlDocument();  
               XmlWriter writer = doc.CreateNavigator().AppendChild();  
               writer.WriteStartElement("root");  
               using (XmlReader r = XmlReader.Create(new StringReader("<a/><a/><a/><a/><a/>"), new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment } ) ) {  
                   writer.WriteNode(r, false);  
               }  
               writer.WriteEndElement();  
               writer.Close();  
               doc.Save(Console.Out);

I hope this helps.  
Thank you,  
-Helena Kotas, System.Xml Developer

 

看來 Microsoft 認為這是權宜之計，不算 BUG，要 USER 就直接避掉了，只是他建議的解法剛好就是我[上一篇](/post/e58e9fe4be86-XmlWellFormedWriter-e4b99fe69c89-Bug-.aspx)用的，用 XmlReader, 搭上 ConformanceLevel.Fragment 的設定解決掉...

只不過，這種情況，不是應該丟出 NotSupportException 比較好嘛? 幹嘛拿個不適當的實作填進來?

 

提外話，現在 WEB 2.0 的時代，Microsoft 工程師除了寫 CODE 之外，也要負責回客戶的問題了? 真辛苦...
