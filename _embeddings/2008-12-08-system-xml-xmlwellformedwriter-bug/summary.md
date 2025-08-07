# 原來 System.Xml.XmlWellFormedWriter 有 Bug ..

## 摘要提示
- WriteRaw 雙重編碼: XmlWellFormedWriter 在 WriteRaw 時會把已經是 Raw 的內容再做一次字元轉義，造成輸出錯誤。
- XmlTextWriter 正常: 相同程式碼在 XmlTextWriter 下可得正確 XML，證實 MSDN 所述行為才是正確規格。
- 範例重現: 透過簡易 Console 範例即可重現 &lt; 變成 &amp;lt; 的問題，確認問題範圍。
- 影響侷限: Bug 只出現在 WriteRaw 方法，其餘 WriteStartElement、WriteString 等 API 正常。
- 安全性考量: WriteRaw 不會幫忙驗證內容，本就有風險，Bug 只是讓風險更加明顯。
- XmlCopyPipe 解法: 作者以「Reader→Writer Pipe」方式繞過 WriteRaw，並兼顧內容驗證。
- XmlCopyPipe 原理: 使用 XmlReader 先行剖析，再依節點類型逐一寫入 XmlWriter，避免重複剖析。
- 片段讀取技巧: 透過 XmlReaderSettings.ConformanceLevel = Fragment 可讀取多 Root 片段。
- 效能與可用性: Pipe 作法不額外產生 XmlDocument，省記憶體且維持可讀、可維護特性。
- 來源參考: 實作靈感來自 Mark Fussell 部落格文章，作者僅加上迴圈與重新命名。

## 全文重點
作者為替代已過時的 XmlNodeWriter，而改用 .NET Framework 內部的 System.Xml.XmlWellFormedWriter；在試用過程中，他使用 WriteRaw 將一段「多個 <a/> 節點的片段」寫入目標文件，卻發現輸出結果與 XmlTextWriter 明顯不同──預期應直接輸出 <a/>、實際卻變成 &lt;a/&gt;，顯示 XmlWellFormedWriter 將 Raw 字串再次編碼。根據 MSDN 文件，XmlTextWriter 的做法才符合規範，因此可判定 XmlWellFormedWriter 實作有缺陷。雖然作者對此 Bug 感到「幸運地踩到」，但也承認這個 Writer 仍有其價值，因為它能解決他原本想避開「多重剖析」的性能問題。為了既避開 WriteRaw Bug，又能確保輸入內容合法，作者實作了 XmlCopyPipe 方法：先用 XmlReader（設定為 Fragment 以支援多 Root）把來源片段讀成節點流，隨即依節點類型呼叫對應的 XmlWriter 方法輸出，如此便能在寫入前先經過一次 Parser 驗證，不合法內容會立即被抓出，同時也避免 XmlWellFormedWriter 對 Raw 的再編碼。最後作者展示將 XmlCopyPipe 應用於原範例的修正版，證實可產生正確 XML。文末提到此解法大部分概念來自 Mark Fussell 的 MSDN 部落格，並提醒讀者記得感謝原作者。

## 段落重點
### 1. 發現 Bug 的背景
作者原想以 XmlWellFormedWriter 取代早年內部才有的 XmlNodeWriter，希望減少記憶體負擔與重複剖析；豈料剛寫完測試程式就撞見新 Bug。這段先鋪陳過去曾抓到 SmtpMail Bug 的經驗，語帶調侃地說「冷門 API 果然比較晚被踩」，也為後文示範埋下伏筆。

### 2. 範例程式與輸出差異
作者給出兩段完全等價的程式，差別只在於取得 XmlWriter 的方式：第一段直接用 XmlWriter.Create 產生 XmlTextWriter，第二段透過 XmlDocument.CreateNavigator().AppendChild() 取得 XmlWellFormedWriter。相同地呼叫 WriteStartElement、WriteRaw、WriteEndElement 之後，前者輸出正確的 <a/> 序列，後者卻把 < 轉成 &amp;lt;。截圖可看見一目了然的差異，進一步證實是 WriteRaw 實作上的問題。

### 3. 問題評估與既有風險
按照 MSDN 對 WriteRaw 的說明，該方法應直接寫入字串而不變動，因此 XmlTextWriter 行為正確；XmlWellFormedWriter 的「多此一舉」顯示它誤把 Raw 當一般文字再次編碼。作者指出，WriteRaw 天生就不會驗證輸入是否合法 XML，開發者若不慎把破碎或未轉義的片段寫進去，文件本身就會毀損，因此就算沒有 Bug，WriteRaw 也應慎用。Bug 反而提醒大家重新思考安全寫法。

### 4. XmlCopyPipe 的誕生
為兼顧效能與正確性，作者決定改走「Reader→Writer Pipeline」：先用 XmlReader 解析原始片段，把每一種 NodeType 轉呼叫對應的 XmlWriter 方法。如此一來，Raw 片段經 Parser 驗證後才寫出，既避開 WriteRaw 也避免非法字元。作者詳細列出 XmlCopyPipe 的 switch-case 邏輯，涵蓋 Element、Text、CDATA、Comment、PI 等所有常見節點，確保全面支援。

### 5. 實際替換與測試結果
作者把原本直接 WriteRaw 的程式改為：1. 建立 XmlReaderSettings，將 ConformanceLevel 設 Fragment；2. 以字串來源建立 XmlReader；3. 呼叫 XmlCopyPipe，把 Reader 流導向 XmlWriter；4. 收尾 WriteEndElement 並 Close。執行後能成功得到與 XmlTextWriter 相同的輸出，截圖顯示 <a/> 片段被正確寫入，證實 Bug 已被繞過且內容合法。

### 6. 參考來源與結語
XmlCopyPipe 的核心概念源自 Mark Fussell 於 MSDN Blog 的文章，作者僅在原範例基礎上增加迴圈與改名；因此特別提醒讀者若覺得此技巧有用應向原作者致謝。最後總結：XmlWellFormedWriter 雖有 WriteRaw Bug，但在避開該 API 且配合 XmlCopyPipe 的前提下，仍是兼具效能與便利的好工具。