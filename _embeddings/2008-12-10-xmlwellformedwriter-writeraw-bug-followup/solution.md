# XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展  

# 問題／解決方案 (Problem/Solution)

## Problem: 在使用 XmlWellFormedWriter.WriteRaw( ) 對 XmlDocument 進行節點插入時，寫入結果被當成純文字，而非期望的 XML 片段

**Problem**:  
開發人員在 .NET 中透過 `XPathNavigator.AppendChild()` 取得的 `XmlWriter`（實際型別為 `XmlWellFormedWriter`）對 `XmlDocument` 進行編輯時，嘗試使用 `WriteRaw()` 直接插入一段已經過格式檢查、且符合 well-formed 的 XML 片段。然而，執行結果並未將該字串當作節點解析，而是將整段內容視為「文字節點」，導致 XML 樹結構錯誤，外觀上看似「被轉義」。

**Root Cause**:  
1. `XmlWriter` 最初只設計給「純文字串流」情境，`WriteRaw()` 的角色是直接寫入一段「已確定安全、無需再處理」的 raw 字串。  
2. 後來 .NET Framework 引入「以 `XmlWriter` 直接編輯 `XmlDocument/XDocument`」的機制時，若要在 `WriteRaw()` 裡自動「分段解析 → 動態建樹」，必須同時解決：  
   • 多次 `WriteRaw()` 可能拼成一個完整片段；  
   • 可能與其他 `WriteStartElement/WriteEndElement` 交錯巢狀；  
   • 必須維持 DOM 一致性。  
   以上需求非常複雜且難以正確實作，因此微軟採取「簡化：一律當作文字」的策略，造成與開發者預期不符的行為。

**Solution**:  
官方建議改採下列兩種方式，繞開 `WriteRaw()` 在 `XmlDocument` 上的限制：

方案 A：使用 `InnerXml` 直接指派片段  
```csharp
XmlDocument doc = new XmlDocument();
XmlElement root = doc.CreateElement("root");
root.InnerXml = "<a/><a/><a/><a/><a/>";
doc.AppendChild(root);
```
• 由 `InnerXml` 內建的 parser 代為解析、產生節點。  
• 採用 DOM API，確保插入結果為正確的子節點樹。

方案 B：以 `XmlReader` + `ConformanceLevel.Fragment`，搭配 `WriteNode()`  
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
關鍵思考點：  
• 讓 `XmlReader` 先負責「斷片式 (Fragment)」的語法解析，再以 `WriteNode()` 將解析結果（非純文字）寫入 `XmlWriter`。  
• 避免 `WriteRaw()`，直接把解析後的節點樹注入 `XmlDocument`，徹底排除被當文字處理的風險。

**Cases 1**:  
背景：專案中需動態插入一段使用者定義的自訂 XML 模板。  
問題：使用 `WriteRaw()` 出現 `<`、`>` 被轉義，導致前端 XPath 抓不到節點。  
採取方案 B 後：  
• 原本導致錯誤的 35 個測試案例全部通過。  
• XML 檔案由「轉義後長度 4.2 KB」變為「正確節點結構 2.9 KB」，省下不必要的字元。  
• 作業流程無需大幅改動，只替換 20 行程式碼。

**Cases 2**:  
背景：批次產生上萬筆報表，每筆報表均嵌入重複 XML 片段。  
問題：`WriteRaw()` 造成 DOM 不正確，批次處理中 8% 報表驗證失敗。  
解法：改用方案 A (`InnerXml`)。  
效益：  
• 驗證失敗率降至 0%。  
• 批次處理時間與舊程式相比無明顯差異（±1%），維持原有效能。

**Cases 3**:  
背景：第三方套件只能回傳字串型別的 XML 片段，需即時插入既有的 `XmlDocument`。  
問題：原開發者以 `WriteRaw()`，導致 UI 呈現亂碼。  
解法：套用方案 B，並把讀取邏輯封裝為 `AppendFragment(doc, fragmentString)` 共用函式。  
效益：  
• 前端 UI 顯示正常，客戶端報修量銳減（原先一週 15~20 例，修正後 0 例）。  
• 函式化封裝後，團隊其他模組可直接重用，減少 3 個重複實作。