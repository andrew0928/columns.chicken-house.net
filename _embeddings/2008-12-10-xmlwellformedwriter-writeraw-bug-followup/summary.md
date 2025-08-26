# XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展

## 摘要提示
- 回報背景: 作者於 VS2008 透過 Report Bug 回報 WriteRaw 行為問題並收到 Microsoft 於 Connect 的公開回應。
- 設計初衷: WriteRaw 原設計用於將已格式化且保證 well-formed 的片段直接寫入文字型 XML 輸出。
- 使用情境轉變: 當 XmlWriter 套在 XmlDocument/XDocument（透過 XPathNavigator 編輯）時，WriteRaw 的語義變得有爭議。
- 實作抉擇: 微軟在此情境選擇將 WriteRaw 內容視為單純文字，而非解析成節點。
- 技術難點: 片段可能由多次 WriteRaw 混雜其他寫入呼叫組成，難以正確解析與嵌套處理。
- 官方替代: 若有片段字串需附加到 XmlDocument，建議用 InnerXml 設定或以 XmlReader + WriteNode 寫入。
- 範例做法: 使用 XmlReaderSettings.ConformanceLevel = Fragment，搭配 writer.WriteNode 將片段安全寫入。
- 非 Bug 定性: 微軟視為權衡下的行為設計，而非框架缺陷或錯誤。
- 作者觀點: 認為此情況應丟 NotSupportedException 比較合適，避免誤導性實作。
- 文化觀察: 感嘆 Web 2.0 時代工程師除寫程式外還需直接回應客戶問題。

## 全文重點
作者在 Visual Studio 2008 以 Report Bug 回報 XmlWellFormedWriter.WriteRaw 在搭配 XmlDocument/XDocument（透過 XPathNavigator）時的「像是 Bug」行為，意外得到 Microsoft 於 Connect 平台的正式回覆。微軟說明 WriteRaw 的設計初衷是針對以文字形式輸出 XML 的 XmlWriter，允許直接寫入已格式化且已確保 well-formed 的 XML 片段，或寫入已跳脫的文字。然而當 XmlWriter 以 XmlDocument/XDocument 為後端時，WriteRaw 的語義產生爭議：要把它當作純文字，還是把它解析成節點？微軟表示後者在工程上極難（甚至不可行），因為 XML 片段可能被拆成多次 WriteRaw 呼叫、與其他 XmlWriter 呼叫交錯、且有多層嵌套，難以穩健判定片段邊界與正確性，因此決定在此情境一律將 WriteRaw 視為純文字處理。

針對「把 XML 片段接到 XmlDocument」的需求，微軟提供兩個官方替代作法：其一是直接設定節點的 InnerXml；其二是若要堅持用 XPathNavigator.AppendChild() 取得的 XmlWriter，則建立一個針對該片段的 XmlReader（ConformanceLevel 設為 Fragment），再以 writer.WriteNode(reader, false) 寫入，最後正常結束並保存。作者指出，這解法正是他先前文章採用的方式。

回應最後，作者認為微軟將其定調為設計權衡而非 Bug，雖可理解但仍覺得「在不支援的情境應拋出 NotSupportedException」比較清楚，避免以不恰當的實作掩飾限制，造成行為直覺與開發者預期不符。文末他也順口感嘆 Web 2.0 時代工程師除寫程式外也要在線上公開回應客戶問題，辛勞不易。

## 段落重點
### 回報與官方回應背景
作者在 VS2008 中以 Report Bug 回報 XmlWellFormedWriter.WriteRaw 相關問題，並分享 Microsoft Connect 上的公開回覆連結。微軟由 System.Xml 的開發者 Helena Kotas 出面說明設計考量與替代作法，態度明確、技術面具體，顯示官方將之視為已知且有既定取捨的行為，而非需要修正的缺陷。這段鋪陳了事件脈絡：從作者觀察與測試，到官方渠道的正式答覆，建立讀者對後續技術細節的信任基礎。

### WriteRaw 的設計初衷與語義轉變
微軟指出 WriteRaw 最初針對純文字輸出管線設計：可直接輸出已格式化、已驗證 well-formed 的 XML 片段，或是輸出已進行字元跳脫的文字，且不再二次處理。然而當 XmlWriter 的後端改為 XmlDocument/XDocument（例如透過 XPathNavigator 的編輯接口）時，WriteRaw 的用途變得曖昧：如果仍期望它像串流一樣直寫片段，將牴觸文件模型對節點與結構的一致性要求；若要解析其內容為節點，則脫離原本「原封不動寫原始文字」的語義，產生語意衝突。

### 為何選擇「視為文字」：工程難點與取捨
官方說明若改為「解析成節點」有多重難題：XML 片段可能被切成多次 WriteRaw 呼叫，單一呼叫未必構成完整片段；且 WriteRaw 可與其他 XmlWriter 呼叫交錯、甚至多層嵌套，導致難以在寫入階段精確界定與維持正確的樹狀結構。這類狀況在文件模型上不易保證一致性與錯誤處理的明確性。基於可行性與實作風險，微軟選擇在文件型 Writer 上將 WriteRaw 一律當作純文字，避免引入脆弱且難以維護的片段解析機制。這也解釋了為何實際行為與部分開發者直覺不符。

### 官方建議的替代作法與程式示例
微軟提供兩種可靠途徑處理「將 XML 片段加入 XmlDocument」的需求。第一，直接以 InnerXml 設定節點的內部 XML，讓框架負責解析並建構節點樹，語義清晰。第二，若流程需要透過 XPathNavigator.AppendChild() 取得的 XmlWriter，則先用字串片段建立 XmlReader，並設定 XmlReaderSettings.ConformanceLevel = Fragment，接著以 writer.WriteNode(reader, false) 將片段寫入，最後妥善結束元素與關閉 Writer。這兩種方式分別對應文件模型與串流寫入的常見場景，能安全滿足片段導入需求。

### 作者觀點與批評、題外話
作者認為微軟的定調是權衡而非 Bug，可理解但不盡理想；在不支援的情境，丟出 NotSupportedException 更能避免誤導，讓開發者立即意識到應改走 InnerXml 或 XmlReader+WriteNode 等正確途徑，而不是默默以不恰當的實作吞掉期望。最後他也感嘆 Web 2.0 的開發文化：工程師除了開發產品，還需公開回覆使用者問題與提供範例，增加了工作負擔，但也提升了透明度與回饋效率。整體而言，本文既傳達官方技術立場，也保留實務開發者對 API 設計訊號明確性的期待。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本 XML 概念（節點、片段、轉義與 well-formedness）
- .NET 中 XML 相關類別：XmlWriter、XmlReader、XmlDocument、XPathNavigator/XDocument
- 例外處理與 API 設計概念（NotSupportedException 的語意）
- ConformanceLevel（Document vs Fragment）的差異

2. 核心概念：本文的 3-5 個核心概念及其關係
- WriteRaw 的設計初衷：為串流式/格式化輸出用（文字型 XML writer），假設輸入已經正確轉義且不需再處理
- XmlWriter 在 XmlDocument/XDocument 之上的行為差異：在 DOM 背後的 writer 無法可靠地把 WriteRaw 視為節點解析，因此被當作文字
- XML 片段處理策略：用 InnerXml 直接賦值於 XmlElement，或以 XmlReader + ConformanceLevel.Fragment 搭配 WriteNode
- API 行為界定 vs Bug：微軟將其視為規格性取捨與權宜實作，而非 Bug

3. 技術依賴：相關技術之間的依賴關係
- XmlDocument 依賴 DOM 模型，XmlWriter 在此情境下需對節點樹完整一致
- WriteRaw 若要「解析成節點」需能跨多次呼叫組合、與其他寫入 API 交錯，難以保證正確性
- 使用 XmlReader（ConformanceLevel.Fragment）可把字串片段轉成可被 WriteNode 吸收的節點流
- InnerXml 由 DOM 內部解析字串為節點樹，繞過 WriteRaw 的限制

4. 應用場景：適用於哪些實際場景？
- 將一段已存在的 XML 片段插入到 XmlDocument 裡
- 在使用 XPathNavigator.AppendChild() 建立內容時，從字串片段安全地產生節點
- 處理需保留已轉義文字但不希望再次編碼的情境（僅限串流文字輸出場景）
- 釐清 WriteRaw 在不同後端（串流 vs DOM）上的語義差異，避免誤用

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 XML 結構與 well-formed 規則、轉義字元
- 熟悉 .NET 的 XmlDocument、XmlWriter、XmlReader 基本用法
- 寫出最簡單的讀/寫 XML 範例（讀取、建立元素、儲存）

2. 進階者路徑：已有基礎如何深化？
- 比較 ConformanceLevel.Document 與 Fragment 的差異與使用時機
- 練習用 XmlReader.Create(StringReader, settings) + WriteNode 將片段插入 DOM
- 了解 XPathNavigator 與 AppendChild() 的 writer 如何與 DOM 互動
- 分析 API 設計權衡（為何不丟 NotSupportedException、行為一致性 vs 易用性）

3. 實戰路徑：如何應用到實際專案？
- 建立一個工具方法：InsertFragment(XmlElement target, string fragment) 內部用 XmlReader(Fragment) + WriteNode 或 InnerXml
- 為輸入片段建立驗證（try 解析，捕捉例外）並回報可診斷錯誤
- 抽象封裝：針對串流輸出使用 WriteRaw；針對 DOM 插入使用 InnerXml 或 Reader+WriteNode，統一介面避免誤用

### 關鍵要點清單
- WriteRaw 的設計初衷: 針對文字型 XML 輸出（串流 writer）寫入已格式化/已轉義內容，不再做轉義或驗證 (優先級: 高)
- DOM 背後的 XmlWriter 行為: 在 XmlDocument/XDocument 上，WriteRaw 內容被視為純文字，非自動解析成節點 (優先級: 高)
- 不是 Bug 的定位: 微軟將其視為規格性取捨而非錯誤，避免實作解析片段的高複雜度 (優先級: 中)
- 為何難以解析片段: 片段可能分多次 WriteRaw、與其他呼叫交錯、巢狀複雜，實作成本與風險高 (優先級: 高)
- 正確插入片段方案一（InnerXml）: 以 rootElement.InnerXml = "<a/><a/>…" 讓 DOM 解析片段成節點 (優先級: 高)
- 正確插入片段方案二（Reader+WriteNode）: 用 XmlReader(Fragment) 讀片段，writer.WriteNode 將其寫入 (優先級: 高)
- ConformanceLevel.Fragment: 使 XmlReader 能合法讀取多個頂層節點的片段 (優先級: 高)
- XPathNavigator.AppendChild() 搭配 Writer: 搭配 WriteNode 可安全將片段加入 XmlDocument (優先級: 中)
- 何時用 WriteRaw: 僅在確定需要原樣輸出、且輸出目標為串流文字 XML 時使用 (優先級: 中)
- 轉義與雙重編碼風險: 不當使用 WriteRaw 可能導致未轉義或重複轉義問題 (優先級: 中)
- InnerXml 的風險與責任: 輸入必須是 well-formed，否則會拋出例外 (優先級: 中)
- API 設計考量: 拋 NotSupportedException 可防誤用，但微軟選擇提供可用但語義受限的行為 (優先級: 低)
- 測試與驗證: 為片段插入撰寫單元測試，涵蓋多次呼叫、交錯 API、錯誤片段 (優先級: 中)
- 效能考量: Reader+WriteNode 對大量片段更穩健；InnerXml 適合一次性插入 (優先級: 低)
- 問題回報與追蹤: 了解 Microsoft Connect/回應脈絡，有助釐清行為是否為規格或缺陷 (優先級: 低)