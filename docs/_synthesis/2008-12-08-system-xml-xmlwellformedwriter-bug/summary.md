---
layout: synthesis
title: "原來 System.Xml.XmlWellFormedWriter 有 Bug .."
synthesis_type: summary
source_post: /2008/12/08/system-xml-xmlwellformedwriter-bug/
redirect_from:
  - /2008/12/08/system-xml-xmlwellformedwriter-bug/summary/
---

# 原來 System.Xml.XmlWellFormedWriter 有 Bug ..

## 摘要提示
- 問題來源: 使用 XmlWellFormedWriter 執行 WriteRaw 時，內容被不當編碼，與規格不符
- 行為差異: XmlTextWriter 正確輸出 Raw 片段；XmlWellFormedWriter 將 < > 變成實體
- MSDN 依據: WriteRaw 應直接寫入未編碼內容，XmlWellFormedWriter 行為過度「雞婆」
- 影響範圍: 僅限 WriteRaw；一般節點與常規寫入不受影響
- 風險提醒: WriteRaw 不做內容驗證，可能導致整份 XML 壞掉
- 替代作法: 以 XmlReader+XmlWriter 管線化複製，避免 WriteRaw
- 實作重點: XmlCopyPipe 逐節點讀寫，涵蓋元素、屬性、文字、CDATA、PI、註解等
- 片段處理: 以 XmlReaderSettings 設定 ConformanceLevel.Fragment 正確讀取多 root 片段
- 效能思維: 避免使用雙重載入的 XmlDocument.ImportNode，改以 reader/writer streaming
- 參考來源: 作法靈感取自 Mark Fussell 的 MSDN 部落格文章

## 全文重點
作者在比較 XmlTextWriter 與 XmlWellFormedWriter 時，發現一個與 MSDN 規格不符的行為：在 XmlWellFormedWriter 上呼叫 WriteRaw 寫入一段已成形的 XML 片段（例如 <a/><a/>…），輸出卻被自動轉義成 &lt;a/&gt; 等 HTML 實體，導致原先意圖直接嵌入的節點成為純文字；相對地，使用 XmlTextWriter 則會如預期將片段原樣寫出。依照 MSDN，WriteRaw 應該是「不做編碼、直接寫入」，因此 XmlWellFormedWriter 的行為可視為 Bug（或至少是與規格不一致的實作）。

雖然作者已找到可替代 XmlNodeWriter 的方式並十分倚賴 XmlWellFormedWriter，但這個 WriteRaw 的問題仍需避開。此外，即便沒有此 Bug，WriteRaw 本身也不會替輸入內容做合法性驗證，若塞入不合規的片段會破壞整份輸出，風險不小。基於這兩點，作者提出一個更穩妥的替代方案：用 XmlReader 解析來源，再逐節點寫入 XmlWriter（XmlCopyPipe）。此方式像管線一樣，把 reader 讀到的節點（元素、屬性、文字、CDATA、註解、處理指令、DTD、實體參考、空白、結尾元素等）一一對映到 writer，確保內容是經過解析且結構正確的 XML，而非單純的字串拼接。

在處理多個 root 的 XML 片段時，需要將 XmlReaderSettings 的 ConformanceLevel 設為 Fragment，才能讓 XmlReader 正確讀取連續片段。最後作者示範將原本的 WriteRaw 改為以 XmlReader 讀入字串片段，再用 XmlCopyPipe 複製到 XmlWellFormedWriter，成功避開 WriteRaw 的錯誤行為且得到正確結果。作者也提到，這種 reader/writer 的 streaming 方式比過往用兩個 XmlDocument 搭配 ImportNode 來得更有效率且更安全。此作法靈感多取自 Mark Fussell 的文章，文末也提醒讀者致謝原作者。

## 段落重點
### 問題發現：XmlTextWriter v.s. XmlWellFormedWriter
作者以兩段幾乎相同的程式碼比較兩個 XmlWriter：XmlTextWriter 與透過 XmlDocument.CreateNavigator().AppendChild() 取得的 XmlWellFormedWriter。相同的 WriteRaw("<a/><a/><a/><a/><a/>") 在 XmlTextWriter 下能輸出為真正的元素節點；但在 XmlWellFormedWriter 下卻被轉義成 &lt;a/&gt; 文字實體，導致結果與預期不符。根據 MSDN，WriteRaw 應直接寫出原始字串，不應再做編碼，因此 XmlWellFormedWriter 的行為被判定為 Bug 或過度處理。作者強調雖然找到問題，但他仍會使用這個 Writer，因為它解決了其他層面的需求；只是 WriteRaw 這一點需要特別留意與避開。

### 安全替代：XmlCopyPipe 實作
為了避免 WriteRaw 的非預期行為與其不做驗證的風險，作者實作 XmlCopyPipe(reader, writer)：以 XmlReader 讀取來源 XML，並依據每個節點類型逐一寫入 XmlWriter。涵蓋的節點包含元素、屬性、文字、空白、CDATA、實體參考、處理指令、XML 宣告/PI、DTD、註解與結尾元素等，確保完整對映。這種作法好處在於：1) 經過解析後再寫入，能避免不合法內容破壞輸出；2) 不必用兩個 XmlDocument 搭配 ImportNode 的笨重流程；3) 適合將一段 XML 內容從來源安全地「管線化」到目的地，同時保留結構與內容的正確性。

### 實務應用：用 XmlCopyPipe 取代 WriteRaw()
作者將原本在 XmlWellFormedWriter 上呼叫 WriteRaw 的程式改為：先建立 XmlReader，並以 XmlReaderSettings 將 ConformanceLevel 設定為 Fragment 來處理多 root 片段，接著用 XmlCopyPipe 將 reader 的內容寫入 writer。此舉成功避開 XmlWellFormedWriter 的 WriteRaw 編碼問題，輸出也符合預期。作者補充指出，處理 XML 片段時一定要記得設定 Fragment 模式，否則 reader 可能無法正確讀取。整體作法與靈感主要源自 Mark Fussell 的文章，作者在此基礎上加上迴圈與命名調整，並提醒讀者若覺得有幫助，應向原作者致謝。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 XML 概念：元素、屬性、字元轉義、Well-formed 與 Fragment 的差異
   - .NET System.Xml 基本類別：XmlReader、XmlWriter、XmlDocument、XmlTextWriter
   - 字元編碼與轉義的差別：Raw 字串輸出 vs 文字節點輸出

2. 核心概念：
   - XmlWriter 的多種實作差異：XmlTextWriter 與 XmlWellFormedWriter 在 WriteRaw 的行為不同
   - WriteRaw 的風險：不做驗證、可能破壞整體 XML、實作差異造成雙重轉義
   - XmlReader-XmlWriter 管線（XmlCopyPipe）：以已解析的節點為單位複製，避免 Raw 直寫風險
   - XML Fragment 處理：使用 XmlReaderSettings.ConformanceLevel = Fragment 以讀取多 root 片段
   - 效能與安全平衡：避免重複解析，同時維持輸出合法性

3. 技術依賴：
   - XmlDocument.CreateNavigator().AppendChild() 取得的 Writer 實際為 XmlWellFormedWriter
   - XmlTextWriter 與 XmlWellFormedWriter 對 WriteRaw 的處理差異（前者如預期原樣寫入，後者會再做轉義，導致 &lt; 變成 &amp;lt;）
   - XmlReader 經由解析後以節點型式輸出至 XmlWriter，降低不合法內容風險
   - ConformanceLevel.Fragment 使 XmlReader 能處理多個連續元素的片段

4. 應用場景：
   - 將一段 XML 片段安全地插入至既有文件（多 root 片段）
   - 以串流方式複製或轉寫 XML（Reader → Writer）避免 DOM 全載入
   - 在需要避免 WriteRaw 破壞輸出或被雙重編碼時的安全替代方案
   - 於資料整併、匯入匯出與中介層（Pipe）中進行 XML 節點級複製

### 學習路徑建議
1. 入門者路徑：
   - 先理解 XML 結構與字元轉義（<, >, &, "）
   - 學會使用 XmlWriter 寫入基本元素、屬性與文字（WriteStartElement、WriteString、WriteEndElement）
   - 了解 WriteRaw 與 WriteString 的差異與風險

2. 進階者路徑：
   - 練習使用 XmlReader 逐節點讀取 XML，理解 NodeType 與屬性讀取
   - 實作 XmlReader → XmlWriter 的節點複製（XmlCopyPipe），涵蓋元素、屬性、CDATA、PI、DTD、註解等
   - 學會處理 XML Fragment：設定 ConformanceLevel.Fragment 並測試多元素片段

3. 實戰路徑：
   - 在實務專案中以 XmlCopyPipe 取代 WriteRaw 插入片段，確保輸出合法
   - 用 XmlDocument.CreateNavigator().AppendChild() 建立 Writer 並搭配 Pipe，避免重複解析與記憶體膨脹
   - 撰寫單元測試驗證各 NodeType 複製正確，並測試錯誤片段的例外行為與韌性

### 關鍵要點清單
- XmlWriter 實作差異：不同來源取得的 XmlWriter（如 XmlTextWriter vs XmlWellFormedWriter）對 WriteRaw 反應不同，需測試確認 (優先級: 高)
- WriteRaw 的風險：不做內容驗證，易導致整體 XML 壞掉，應謹慎使用或避免 (優先級: 高)
- 雙重編碼問題：XmlWellFormedWriter 對 WriteRaw 可能額外轉義，造成 &lt; 被寫成 &amp;lt; (優先級: 高)
- 正確行為參照：MSDN 指出 XmlTextWriter 對 WriteRaw 的原樣輸出為預期行為 (優先級: 中)
- 安全替代：以 XmlReader→XmlWriter 的 XmlCopyPipe 節點級複製取代 WriteRaw (優先級: 高)
- NodeType 覆蓋面：XmlCopyPipe 需處理 Element、Text、Whitespace、CDATA、EntityRef、PI、DocType、Comment、EndElement (優先級: 中)
- Fragment 處理：使用 XmlReaderSettings.ConformanceLevel = Fragment 讀取多 root 片段 (優先級: 高)
- Writer 來源特性：XmlDocument.CreateNavigator().AppendChild() 取得的 Writer 背後實作為 XmlWellFormedWriter (優先級: 中)
- 效能考量：Pipe 可避免重複解析與整份載入，兼顧效能與正確性 (優先級: 中)
- 錯誤防護：經由 Reader 解析後再寫出，可在輸出前發現不合法內容（比 Raw 安全） (優先級: 高)
- API 陷阱意識：同名 API 在不同實作上的行為差異屬常見陷阱，需閱讀官方文件與驗證 (優先級: 中)
- 測試策略：為 WriteRaw/WriteString/XmlCopyPipe 覆蓋多語系字元與邊界案例（如未關閉元素、非法字元） (優先級: 中)
- 維運建議：將 WriteRaw 的使用限制在可控、已驗證的輸入來源，並以程式碼審查把關 (優先級: 中)
- 相容性注意：老程式若從 XmlTextWriter 遷移到 XmlWellFormedWriter，需特別檢視 Raw 相關輸出 (優先級: 中)
- 參考資源：MSDN 行為說明與 Mark Fussell 的 Fragment 讀取教學可作為設計與除錯依據 (優先級: 低)