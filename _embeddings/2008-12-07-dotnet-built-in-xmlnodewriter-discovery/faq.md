# 原來 .NET 早就內建 XmlNodeWriter 了...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 .NET Framework 裡到底有沒有 XmlNodeWriter？
是的，從 .NET 2.0 開始就「內建」了。  
其實它隱身在 `XmlNode.CreateNavigator().AppendChild()` 回傳的 `XmlWriter` 物件中，功能與早期社群版的 XmlNodeWriter 完全相同，可直接把 XmlWriter 的輸出寫進指定的 `XmlNode`。

## Q: 如果我想把 XSLT 轉換結果直接寫回記憶體中的 XmlDocument，要怎麼做？
可以這樣寫：  
```csharp
XmlDocument doc = new XmlDocument();
using (XmlWriter writer = doc.CreateNavigator().AppendChild())
{
    xslt.Transform(inputDoc, (XsltArgumentList)null, writer);
}
```  
透過 `AppendChild()` 取得的 `XmlWriter`，XSLT 產生的結果會直接長在 `doc` 裡，不必先輸出成字串再重新載入。

## Q: 為什麼要用 XmlWriter/XmlNodeWriter，而不是直接用 XmlDocument 操作整棵 XML？
1. XmlWriter 以串流方式輸出，效能遠高於一次整棵載入記憶體的 XmlDocument。  
2. 撰寫複雜 XML 時語法較簡潔。  
3. 直接寫入 `XmlNode` 可避免「先輸出成文字→再 Parse 回節點」的不必要開銷與醜陋流程。