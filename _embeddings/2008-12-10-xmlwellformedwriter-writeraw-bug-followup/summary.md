# XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展

## 摘要提示
- Bug回報: 作者透過 Visual Studio 2008 的 [Report Bug] 功能回報 WriteRaw 的行為問題。
- Microsoft回覆: Connect 平台上由 System.Xml 團隊工程師 Helena Kotas 公開說明設計緣由。
- WriteRaw設計初衷: 原本僅用於「把已格式化、已轉義的字串直接寫入文字型 XML 檔」。
- 爭議產生: 內建到 XmlDocument/XDocument 後，WriteRaw 可能面臨「當作純文字」或「解析成節點」兩難。
- 無法解析: 多次 WriteRaw 呼叫可交錯其他寫入操作，使片段解析成本過高且難以完善實作。
- 官方決策: 統一將 WriteRaw 內容視為純文字，不進行額外解析，屬「By Design」而非 Bug。
- 建議解法1: 直接以 XmlElement.InnerXml 設定整段 XML 字串。
- 建議解法2: 建立 XmlReader（ConformanceLevel.Fragment），再用 WriteNode 寫入。
- 作者觀點: 若無意支援解析，應拋出 NotSupportedException，而非給出「看似能用」的實作。
- 感想延伸: Web 2.0 時代連 Microsoft 工程師也需兼任客服，回應用戶回饋。

## 全文重點
作者在前篇文章發現 XmlWellFormedWriter.WriteRaw( ) 與 XmlDocument/XDocument 搭配時，寫入的 XML 片段並未被解析成節點，反而被當成普通文字輸出。他於 Visual Studio 2008 內直接使用 [Report Bug] 功能，在 Microsoft Connect 站點提出問題（FeedbackID: 386899）。數日後，System.Xml 團隊工程師 Helena Kotas 公開回覆，說明 WriteRaw 的歷史定位與目前行為屬「設計結果」而非程式錯誤。

回覆指出，WriteRaw 原本只服務於「格式化後的文字型 XML 輸出」，因此可直接寫入已轉義或已檢查過完整性的字串；當此 API 被套用到 XmlDocument/XDocument（透過 XPathNavigator 產生的 XmlWriter）時，必須在「把內容當文字」與「解析成節點」之間做取捨。若選擇解析，須處理多次 WriteRaw 斷續寫入、與其他寫入函式交錯、乃至於巢狀層級等複雜情況，實作難度極高且影響效能，故最終決定延用「純文字」策略。

為了讓開發者仍能插入真正的節點，官方給出兩種替代方案：一、先建立 XmlElement，透過 InnerXml 直接設定整段片段；二、將字串包成 ConformanceLevel.Fragment 的 XmlReader，再以 WriteNode 寫進目標 XmlWriter。這兩種方法均能確保 XML 片段維持節點結構並避開 WriteRaw 限制。

作者得知此結論後，發現自己上一篇文章中已採用官方建議中的第二種做法，因此問題實際上已解。儘管如此，作者仍質疑：「既然無意支援解析功能，是否應在 WriteRaw 上對此情境拋出 NotSupportedException，而非讓開發者誤以為可直接寫入片段？」最後，作者順帶感嘆在 Web 2.0 時代，Microsoft 工程師不僅要寫程式，還得親自回覆社群與用戶的提問，可見工作多元且辛勞。

## 段落重點
### 1. Bug 回報與 Microsoft Connect 連結
作者於 Visual Studio 2008 按下 Report Bug，將先前發現的 WriteRaw 異常送交 Microsoft Connect；連結與回報編號皆公開，顯示回報流程的透明與效率。

### 2. Microsoft 官方回覆內容
System.Xml 團隊說明 WriteRaw 的歷史用途、設計考量及在 XmlDocument/XDocument 中的取捨；因多重呼叫與交錯問題，解析片段幾近不可行，故決策維持「純文字」行為，並提出 InnerXml 與 WriteNode 兩大替代方案。

### 3. 作者觀點與後續思考
作者肯定官方快速回應，同時指出應以 NotSupportedException 明示限制，以免誤導開發者；最後感嘆 Web 2.0 與社群文化下，工程師須兼顧開發與客服，工作負荷更形多樣。