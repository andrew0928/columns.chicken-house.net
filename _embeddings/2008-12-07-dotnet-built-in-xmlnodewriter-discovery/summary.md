# 原來 .NET 早就內建 XmlNodeWriter 了...

## 摘要提示
- 開場背景: 作者在新專案中意外發現 .NET 內建「隱藏版」XmlNodeWriter。
- XmlWriter 與 XmlDocument: XmlWriter 效能佳但功能受限、XmlDocument 操作方便但慢。
- 舊版 XmlNodeWriter: 社群先前自行實作，可直接將 XmlWriter 輸出寫回 XmlNode。
- 官方隱藏實作: `XmlNode.CreateNavigator().AppendChild()` 其實就是內建 XmlNodeWriter。
- 自行包裝: 作者示範用少量程式碼把這個功能重新包成類似舊版 XmlNodeWriter。
- 延長線程式碼: 為了繼承 XmlWriter 必須補完 20 多個抽象方法。
- Factory 改造: 進一步寫 `XmlWriterFactory`，提供多種 `Create` 多載取代靜態延伸方法限制。
- 實務建議: 讀者可直接複製貼上十幾行程式碼，歡迎回報使用並順手點擊作者廣告。

## 全文重點
作者因忙於 Enterprise Library 與 Entity Framework 的研究而減少發文，卻在新專案裡偶然發現 .NET 其實早已內建可將 XmlWriter 直接指向 XmlNode 的能力。過去為了在記憶體中對 XML 節點做高效寫入，開發者依賴社群版 XmlNodeWriter，因它能像 XmlWriter 一樣操作、卻把結果直接寫進某個 XmlNode，省下「輸出字串再 parse 回 XmlDocument」的低效率步驟。然而舊程式碼原本寄放在 gotdotnet 已下架，令作者一度失落。直到讀到 Microsoft Xml Team 的 blog 回覆才恍然大悟：在 .NET 2.0 之後，只要對 XmlNode 呼叫 `CreateNavigator().AppendChild()` 取得的 XmlWriter 物件，即具備完全相同功能。  

為了讓程式碼看起來與舊有介面一致，作者示範建立 `XmlNodeWriter` 類別：建構子接收目標 XmlNode 與是否清除原內容兩參數，內部僅用 `AppendChild()` 取得真正的 XmlWriter，後續所有抽象方法與屬性都單純代理至這個內部物件即可。雖然得實作二十多個方法頗為繁瑣，但效果完美等同。  

接著作者因「程式碼潔癖」進一步抽象成 `XmlWriterFactory`：利用靜態多載 `Create(XmlNode, bool, XmlWriterSettings)` 包裝上述流程，並保留原先 XmlWriter 的 10 種多載，加總後能在同一型別上選擇 13 種建立方式。受限於 C# 目前僅支援實例延伸方法、無法延伸 static method，作者只好用繼承而非 extension 方式達成。最終，完整功能僅需十多行主要程式碼與一段「延長線」代理碼即可實現。作者開放任何人自由貼用，並幽默地請讀者若採用可回覆告知，或順手多點幾下他部落格上的廣告以示支持。

## 段落重點
### 前言與寫作背景
作者最近專注於研究 Enterprise Library、Entity Framework 等技術而少發文，卻在開發新專案時意外遇到一項值得分享的發現：.NET 其實暗中提供操作 XmlNode 的高效 Writer。

### XmlWriter 與 XmlDocument 的取捨
XmlWriter 以串流方式輸出大型 XML，效能遠勝 XmlDocument，但只能寫檔案或 TextWriter；反之，XmlDocument 方便編輯卻耗資源。開發者常想在保留 XmlDocument 便利性的前提下，用 XmlWriter 高效寫入部分節點。

### 舊版社群 XmlNodeWriter 的好處
早年有 MVP 釋出 XmlNodeWriter，可透過 Writer API 直接更新 XmlNode，非常好用；可惜原碼隨 gotdotnet 關站而失傳，令人扼腕。

### 發現 .NET 內建替代方案
從 Microsoft Xml Team 部落格留言得知：在 .NET 2.0 起，只要對任一 XmlNode 呼叫 `CreateNavigator().AppendChild()` 即可取得能寫回該節點的 XmlWriter，功能與舊 XmlNodeWriter 完全相同，只是文件未明列。

### 自行封裝為新 XmlNodeWriter
作者寫了一個新的 `XmlNodeWriter` 類別：建構時可選擇是否清空節點，再以 `AppendChild()` 取回內部 XmlWriter，外部介面則繼承 XmlWriter 並單純代理所有方法，使程式能用回熟悉的呼叫風格。

### 補完抽象方法的「延長線」程式碼
由於繼承自 XmlWriter，必須實作二十餘個抽象方法與屬性，實際上皆只需呼叫內部 Writer；這段大量但機械式的程式碼被作者戲稱為「延長線」。

### 改造成 XmlWriterFactory
考量到 static extension 不支援，作者改寫 `XmlWriterFactory`：利用靜態多載 Create 包裝前述邏輯，並串接 `XmlWriter.Create` 讓使用者保有設定物件的彈性。透過繼承，原本 XmlWriter 的 10 種 Create 加上新 3 種，總計 13 種建立途徑一次到位。

### 結語與分享
最終成果程式碼精簡、易於移植。作者鼓勵有需要的開發者直接複製使用，無特殊授權限制，只希望使用者回饋或在部落格多按幾下廣告以資支持。