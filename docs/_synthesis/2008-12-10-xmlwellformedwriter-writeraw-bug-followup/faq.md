---
layout: synthesis
title: "XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展"
synthesis_type: faq
source_post: /2008/12/10/xmlwellformedwriter-writeraw-bug-followup/
redirect_from:
  - /2008/12/10/xmlwellformedwriter-writeraw-bug-followup/faq/
---

# XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 XmlWriter？
- A簡: XmlWriter 是 .NET 的抽象寫入器，用於輸出良構 XML，提供元素、屬性與文字等安全寫入 API。
- A詳: XmlWriter 是 .NET System.Xml 的抽象類別，負責將 XML 資料以良構格式輸出至串流、檔案或字串。它提供 WriteStartElement、WriteAttributeString、WriteString、WriteRaw、WriteNode 等方法，協助開發者控制節點與內容的輸出。核心價值在於強制良構性、避免手動拼接 XML 與自動處理跳脫，降低錯誤與安全風險，並支援格式化與編碼設定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q8

A-Q2: 什麼是 XmlWellFormedWriter？
- A簡: XmlWellFormedWriter 是 XmlWriter 的內部包裝，負責檢查並維護寫入的良構性與正確生命週期。
- A詳: XmlWellFormedWriter 是 .NET 內部用來包裝實際 writer 的類別，確保寫入遵守 XML 規範，包括元素配對、屬性位置正確、禁止在不合法狀態寫入等。對使用者而言，經由 XmlWriter.Create 或特定來源（如 XPathNavigator.AppendChild）取得的 writer，往往由其監護。它著重流程與狀態檢查，而輸出方式仍取決於底層目標（串流或 DOM）。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q8, A-Q3

A-Q3: 什麼是 WriteRaw？
- A簡: WriteRaw 直接寫出字串而不轉義，適用已預先轉義或已驗證的片段或文字。
- A詳: WriteRaw(string) 會將提供的字串原樣寫出，不做字元轉義或驗證。其設計初衷在於「格式化文本 XML」的輸出情境，當字串已保證良構或已正確跳脫時，可避免重複處理提升效率。然而其行為依賴底層 writer 實作；寫入 DOM 時多被視為「文字節點」，而非解析為元素，導致顯示為 &lt;…&gt; 的文字。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q12, B-Q2

A-Q4: WriteRaw 的設計初衷與適用情境是什麼？
- A簡: 初衷是將已格式化、已跳脫的 XML 片段或特殊文字直接輸出至文字型目標。
- A詳: 官方說明指出，WriteRaw 原本是給「將文本 XML 寫入檔案/串流」的 writer 使用。典型用途：1) 寫出已格式化且良構的 XML 片段；2) 寫出已經處理過跳脫的文字節點，避免再次轉義。此法在串流輸出時直觀有效，但在 DOM 後端則會變成文字節點，不會解析成結點樹。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, B-Q2, A-Q16

A-Q5: 為何在 XmlDocument/XDocument 上使用 WriteRaw 具爭議？
- A簡: 因 DOM 期望建立節點樹，WriteRaw 卻被視為文字，導致片段不會成為元素節點。
- A詳: 在 DOM（XmlDocument/XDocument）的情境，writer 的角色是建構節點樹，而 WriteRaw 僅寫「原樣文字」。若將片段字串經 WriteRaw 寫入，它不會被解析成元素/屬性，而是形成含 < 與 > 的文字節點，序列化時轉為 &lt; 與 &gt;。這違背多數開發者對「把片段插入 DOM」的直覺，故引發爭議。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, A-Q6, C-Q2

A-Q6: 將 WriteRaw 視為文字與解析為節點的差異？
- A簡: 視為文字僅產生文字節點；解析為節點則建立完整元素樹與命名空間關係。
- A詳: 視為文字：把輸入原樣當 TextNode，保存字元，不建立任何元素/屬性，輸出時會跳脫。解析為節點：把字串解析成 Element/Attribute/Namespace 結構，融入當前樹狀，支援命名空間繼承與驗證。前者簡單可行但失去結構語意，後者需複雜的部分片段解析與狀態管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q9, C-Q2

A-Q7: 為何 Microsoft 選擇把 WriteRaw 在 DOM 上「視為文字」？
- A簡: 因 WriteRaw 可分段、多次交錯呼叫，正確解析成節點極難實作且成本高。
- A詳: 官方回應指出，WriteRaw 可跨多次呼叫累積片段，且可與其他 XmlWriter 呼叫交錯與巢狀。這使得要判斷「何時片段完整」、如何與既有節點邏輯整合，變得極度困難。故選擇一致地將其當文字處理，以維持穩定可預期的行為，並提供改用 InnerXml 或 WriteNode 的替代作法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q16, C-Q2

A-Q8: 什麼是 XML 片段（Fragment）與完整文件（Document）？
- A簡: 片段是不含單一根元素的合法 XML 節點序列；文件則具一個根元素與宣告。
- A詳: 完整文件包含可選的 XML 聲明與唯一根元素，符合文件層級規則。片段則可是一連串元素、文字或處理指示的組合，常用於拼接或局部更新。讀寫片段需設定 ConformanceLevel.Fragment 以允許多個頂層節點，否則使用 Document 規則會拋出例外。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q2, D-Q4

A-Q9: 什麼是 ConformanceLevel？
- A簡: ConformanceLevel 控制讀寫器對 XML 良構性的層級：Document、Fragment 或 Auto。
- A詳: ConformanceLevel 是 XmlReaderSettings/XmlWriterSettings 的配置，用來指定所處理內容的型態。Document 要求單一根元素與文件規則；Fragment 允許多個頂層節點；Auto 嘗試推斷。將片段用 XmlReader 讀入時，需設定 Fragment 以避免「不是單一根元素」錯誤。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q2, D-Q4

A-Q10: 什麼是 InnerXml？
- A簡: InnerXml 是節點內部的 XML 字串表示，指派時會解析字串並建立子節點。
- A詳: InnerXml 屬於 XmlNode/XmlElement，取得時回傳節點內部序列化的 XML；設置時會先解析字串，若不合法會擲出 XmlException。它是把片段轉為節點樹的捷徑，適合快速插入小片段，但每次都需完整解析，對大型/頻繁操作可能有效能成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q3, A-Q8

A-Q11: 什麼是 WriteNode？
- A簡: WriteNode 將 XmlReader 當前流的節點寫入至 XmlWriter，保留結構與命名空間。
- A詳: WriteNode(XmlReader, bool) 會讀取來源 reader 的節點並輸出到當前 writer。若 reader 以 Fragment 讀取，便可把片段正確轉為 DOM/串流輸出。它是由「Reader 解析」配合「Writer 輸出」的標準管線，可避開 WriteRaw 在 DOM 上的限制，維持節點語意。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q4, A-Q9

A-Q12: WriteRaw 與 WriteString 有何差異？
- A簡: WriteString 會自動跳脫特殊字元；WriteRaw 完全不處理，原樣輸出字串。
- A詳: WriteString 用於純文字內容，會把 <、& 等轉為 &lt;、&amp;，確保良構。WriteRaw 則直接寫入，若目標是串流，可能插入未轉義標記；若是 DOM，通常變為文字節點。處理使用者輸入或不可信資料時，一律選擇 WriteString 以避免注入與格式錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q7, A-Q3

A-Q13: WriteRaw 與 WriteCData 的差異？
- A簡: WriteCData 產生 CDATA 節點包裹文字；WriteRaw 僅原樣寫出字串，不建節點。
- A詳: WriteCData 會生成 <![CDATA[...]]> 節點，內文不需跳脫（除 ]]&gt;），序列化清楚表達「這是文字」。WriteRaw 不會建立 CDATA 結構，也不保證被視為節點。若需明確保護大量文字或包含特殊符號，WriteCData 較安全直觀。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q2, D-Q7

A-Q14: 為何有人主張此情境應拋 NotSupportedException？
- A簡: 因 WriteRaw 在 DOM 的結果違反直覺，拋例外較能提醒 API 誤用與早期失敗。
- A詳: 設計觀點認為，當 API 行為顯著偏離多數人預期（插入片段卻得文字），且風險高（靜默失真），不如直接拒絕並指引用法（InnerXml/WriteNode）。NotSupportedException 讓開發者快速發現誤用，改善可維護性。不過官方選擇維持可用但文件化的行為。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, A-Q7, A-Q16

A-Q15: 使用 WriteRaw 的風險與安全考量是什麼？
- A簡: 主要風險是注入與格式錯誤；不可信資料請改用 WriteString 或 CDATA。
- A詳: WriteRaw 不做跳脫，若來源含 <、& 等，可能破壞良構或導致注入。於 DOM 上雖被視為文字，但會使語意丟失，且輸出時轉義產生「看似 XML 的文字」。最佳實務：不處理使用者輸入，寧用 WriteString/WriteCData；插入片段改用 Reader+WriteNode。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q9, C-Q4, A-Q12

A-Q16: Microsoft 對此回報的核心結論為何？
- A簡: 這是設計取捨非 Bug；建議用 InnerXml 或 XmlReader+WriteNode 插入片段。
- A詳: 官方回覆指出，將 WriteRaw 在 DOM 上解析為節點幾乎不可行，因為可分段、可交錯且難以界定片段完成時機。故採「文字化」的行為並非錯誤。若要插入片段，建議兩法：1) 使用 InnerXml；2) 以 XmlReader（ConformanceLevel.Fragment）搭配 WriteNode 寫入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, A-Q7

### Q&A 類別 B: 技術原理類

B-Q1: XmlWriter 建立於 XmlDocument 時如何運作？
- A簡: 透過 XPathNavigator.AppendChild 取得的 XmlWriter 會向 DOM 建構節點。
- A詳: 當以 XmlDocument.CreateNavigator().AppendChild() 取得 XmlWriter，其寫入目標是 DOM 而非串流。WriteStartElement/WriteAttributeString 會在樹上建立對應節點。此 writer 不負責序列化輸出，而是動態修改記憶體中的節點結構，最後由 Save 才轉為文字。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q10, C-Q2

B-Q2: WriteRaw 在 DOM 支援下的處理機制是什麼？
- A簡: 它被視為文字內容，建立 TextNode，而非解析為元素或屬性節點。
- A詳: DOM 寫入器接收 WriteRaw 時，為避免不完整或交錯片段造成狀態混亂，直接新增文字節點保存字串。後續序列化會自動將 <、& 等轉義。此設計確保 Writer 狀態機簡單一致，但失去片段結構語意。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q6, D-Q1

B-Q3: 含「<」的文字節點在序列化時如何處理？
- A簡: 會自動轉為 &lt; 等實體，確保輸出良構，不被誤判為標記。
- A詳: DOM 內部允許文字節點持有原始字元，但在 Save 或 XmlWriter 輸出時，序列化器會掃描並將保留字元轉義（< → &lt;、& → &amp;）。因此，WriteRaw 在 DOM 上寫的「<a/>」會輸出為「&lt;a/&gt;」，呈現為純文字效果。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q7, D-Q1

B-Q4: XmlReader(ConformanceLevel.Fragment)+WriteNode 的流程是什麼？
- A簡: Reader 解析片段，Writer 接收節點事件並建樹，完整保留結構與命名空間。
- A詳: 流程：1) 用 XmlReaderSettings 設 ConformanceLevel.Fragment；2) 建立 XmlReader 讀取片段字串；3) 在 DOM-writer 上呼叫 WriteNode(reader,false)。Reader 會依序產生元素、屬性、文字等事件，Writer 將其轉為節點，正確合併至現有樹中。適用於片段插入的標準解法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, A-Q11, A-Q9

B-Q5: 為何跨多次 WriteRaw 難以解析成節點？
- A簡: 片段可能分段且與其他呼叫交錯，無法判斷完整邊界與正確巢狀位置。
- A詳: WriteRaw 可於不同時機輸入片段的一部分，並穿插 WriteStartElement/WriteEndElement 等呼叫。若要「延後解析」，需維護複雜緩衝與巢狀對映，且要處理錯誤回溯與命名空間合併。這使正確性、效能與實作成本極高，因而被放棄。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q7, B-Q11, B-Q14

B-Q6: 使用 InnerXml 追加片段的內部流程為何？
- A簡: 將字串以 parser 解析為節點，再替換或插入到目標節點的子樹。
- A詳: 設置 InnerXml 會觸發 XML 解析器，將字串驗證為良構，生成臨時節點樹，再用該樹覆蓋/插入到目標節點的子集合。若字串不合法則擲出 XmlException。優點是簡潔，缺點是每次完整解析，對大量更新有成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, D-Q3, C-Q1

B-Q7: XmlWellFormedWriter 的核心組件與檢查機制？
- A簡: 以狀態機追蹤元素堆疊、屬性上下文與內容模型，阻止非法寫入順序。
- A詳: 它維持元素堆疊以配對 Start/End、追蹤是否在屬性上下文、限制不當內容（例如屬性內不得再開元素），並管理命名空間宣告。其本身不解析 WriteRaw，但會在不合上下文時拒絕相關呼叫，確保整體良構性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q2, B-Q12, B-Q11

B-Q8: 寫入串流與寫入 DOM 的架構差異？
- A簡: 串流 writer 直出文字；DOM writer 建立節點樹，延後到序列化才變文字。
- A詳: 串流 writer（如 XmlWriter.Create(Stream)）將呼叫直接轉為文字輸出，格式與換行由設定控制。DOM writer（透過 Navigator）則把呼叫轉為節點物件，立即更新樹，再由 Save() 統一序列化。這也導致 WriteRaw 在兩者上行為差異顯著。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q2, D-Q6

B-Q9: ConformanceLevel 在 XmlReader 中的機制與影響？
- A簡: 影響讀者允許的結構邊界，決定是否接受多頂層節點與宣告位置。
- A詳: Document 模式強制單一根節點與正確宣告位置；Fragment 模式允許多頂層節點、處理指示、評論混雜；Auto 嘗試猜測來源類型。為讀取片段字串以便插入 DOM，必須使用 Fragment，否則會拋「多個根」或「位置不合法」錯誤。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q2, D-Q4

B-Q10: XPathNavigator.AppendChild() 如何產生 XmlWriter？
- A簡: 它回傳一個 DOM 背書的 XmlWriter，將事件轉成節點插入導航位置。
- A詳: Navigator 指向 DOM 節點時，AppendChild 會建立 writer，將寫入事件轉為對應節點並插入到選定位置（例如新增子節點或屬性）。此 writer 不輸出文字，而是更新 DOM，直至關閉 writer 才完成插入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q2, D-Q6

B-Q11: WriteRaw 與其他呼叫交錯為何會複雜？
- A簡: 交錯造成片段邊界模糊與巢狀錯綜，無法安全還原為節點結構。
- A詳: 例如先 WriteStartElement，再 WriteRaw 部分屬性文本，接著 WriteEndElement 或另一段 WriteRaw。此時很難判定 raw 中含哪些節點、屬性是否應屬於哪個元素，且需處理命名空間宣告與作用域，錯誤處理異常棘手。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q7, A-Q7

B-Q12: .NET 對 WriteRaw 的契約是什麼？
- A簡: 僅保證「原樣寫出不跳脫」，其餘行為依 writer 實作與目標而定。
- A詳: 官方設計允許不同 writer 有不同詮釋。串流 writer 可直接寫入原文，DOM writer 可將其視為文字。文件並未承諾「會解析成節點」，因此在 DOM 上文字化的行為符合契約，並非框架層面的 Bug。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q16, B-Q2

B-Q13: 如何設計穩健的片段插入管線？
- A簡: 用 XmlReader(Fragment) 解析，XmlWriter/DOM 接收 WriteNode，避免 Raw 拼接。
- A詳: 標準做法：1) 驗證/淨化片段來源；2) 建 XmlReaderSettings.ConformanceLevel=Fragment；3) 以 XmlReader 解析；4) 以 WriteNode 寫入 DOM 或串流；5) 如需重用，快取已解析的 XNode/XmlNode。避免使用 WriteRaw 串接片段，以減少注入與良構失敗。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q2, C-Q5, D-Q9

B-Q14: 拋 NotSupportedException 與「靜默文字化」的差異？
- A簡: 前者早期失敗可指引用法；後者相容性高但可能掩蓋語意錯誤。
- A詳: 拋例外可立即警示誤用，促使改用 InnerXml/WriteNode；但可能破壞舊程式相容。靜默文字化維持穩定，但讓程式看似成功、實際丟失結構。API 設計取捨在「相容性 vs 可預期性」，官方選擇前者。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, A-Q16, D-Q1

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 InnerXml 將片段插入 XmlDocument？
- A簡: 建立元素後指派 InnerXml，解析字串生成子節點，最後附加到文件。
- A詳: 步驟：1) var doc=new XmlDocument(); 2) var root=doc.CreateElement("root"); 3) root.InnerXml="<a/><a/><a/>"; 4) doc.AppendChild(root)。程式碼片段：root.InnerXml = "<a/><a/>"; 注意：若片段不良構會擲 XmlException；大型片段或頻繁更新效能較差，建議評估 WriteNode。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, D-Q3, C-Q2

C-Q2: 如何用 XmlReader(Fragment)+WriteNode 安全插入片段？
- A簡: 用 Fragment 模式讀片段，再用 DOM-writer 的 WriteNode 建立節點樹。
- A詳: 步驟與程式碼： 
  - var doc=new XmlDocument(); var w=doc.CreateNavigator().AppendChild(); 
  - w.WriteStartElement("root");
  - using(var r=XmlReader.Create(new StringReader("<a/><a/>"), new XmlReaderSettings{ConformanceLevel=ConformanceLevel.Fragment})) { w.WriteNode(r,false); }
  - w.WriteEndElement(); w.Close(); 
  注意：片段中命名空間將被正確保留；來源不可信時先驗證/淨化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q11, D-Q4

C-Q3: 如何安全寫入使用者輸入到 XML？
- A簡: 使用 WriteString 或 WriteCData，避免 WriteRaw，確保特殊字元被正確跳脫。
- A詳: 做法：writer.WriteStartElement("msg"); writer.WriteString(userInput); writer.WriteEndElement(); 使用 WriteString 會自動將 <、& 跳脫，避免破壞結構或注入。若文字很長或含大量符號，可用 WriteCData。切勿對未信任內容使用 WriteRaw。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q9, C-Q4

C-Q4: 如何在寫入檔案時正確使用 WriteRaw？
- A簡: 僅對已預先跳脫/驗證的內容使用 WriteRaw，並避免混用未處理輸入。
- A詳: 典型：writer.WriteStartElement("root"); writer.WriteRaw("<!-- preformatted -->"); writer.WriteRaw("<item id=\"1\"/>"); writer.WriteEndElement(); 注意：確保 Raw 片段來源可信、良構且不與其他呼叫交錯破壞結構；對不可信資料用 WriteString。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q12, D-Q7

C-Q5: 如何撰寫 AppendXmlFragment 擴充方法？
- A簡: 將字串以 XmlReader(Fragment) 解析，然後以 WriteNode 插入到目標元素。
- A詳: 範例：
  - public static void AppendXmlFragment(this XmlElement elem, string frag){ using var w=elem.OwnerDocument.CreateNavigator().AppendChild(); w.WriteStartElement(elem.Name); using var r=XmlReader.Create(new StringReader(frag), new XmlReaderSettings{ConformanceLevel=Fragment}); w.WriteNode(r,false); w.WriteEndElement(); }
  注意：根據需求調整插入位置與命名空間處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q2, D-Q10

C-Q6: 如何建立單元測試驗證 WriteRaw 在 DOM 與串流不同？
- A簡: 比較兩種 writer 的輸出：DOM 保存後為轉義文字；串流為原樣標記。
- A詳: 測試步驟：1) DOM：用 AppendChild 取得 writer，WriteRaw("<a/>")，保存成字串，斷言包含 "&lt;a/&gt;"；2) 串流：XmlWriter.Create(StringWriter)，WriteRaw("<a/>")，斷言包含 "<a/>"。可用 FluentAssertions 比對字串，確保行為差異清晰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q1, A-Q16

C-Q7: 如何將使用 WriteRaw 的程式改為 WriteNode 模式？
- A簡: 將片段來源改走 XmlReader(Fragment)，並以 WriteNode 輸入 DOM。
- A詳: 重構步驟：1) 找出 WriteRaw 片段；2) 用 XmlReader.Create(new StringReader(fragment), new XmlReaderSettings{ConformanceLevel=Fragment}); 3) 用 writer.WriteNode(reader,false) 取代 WriteRaw；4) 清理不再需要的手動跳脫。測試命名空間與順序是否維持。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q4, D-Q10

C-Q8: 如何辨識當前 XmlWriter 是否寫入 DOM？
- A簡: 以取得方式判斷：若來自 XPathNavigator.AppendChild，多半為 DOM writer。
- A詳: 公開 API 無法可靠反射判型。最佳實務：以「產生方式」分流（AppendChild → DOM；XmlWriter.Create(Stream/TextWriter) → 串流）。在組件邊界傳遞時，傳遞目的型別或策略旗標，避免依賴執行期推斷。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q10, D-Q6

C-Q9: 如何在片段插入時正確處理命名空間？
- A簡: 保持片段內宣告，或在父元素先寫入需要的 xmlns，再 WriteNode。
- A詳: 若片段含 xmlns，Reader+WriteNode 會保留宣告。若希望繼承父命名空間，可先 writer.WriteStartElement("p","root","urn:x")，然後 WriteNode 插入僅有前綴的片段。注意避免重複宣告；可在輸出後 normalize。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q10, B-Q4, A-Q6

C-Q10: 如何用 LINQ to XML（XDocument）插入片段？
- A簡: 以 XElement.Parse 解析片段，Add 到目標節點，再與 XmlDocument 互轉。
- A詳: 範例：var root=new XElement("root"); root.Add(XElement.Parse("<a/>")); var xdoc=new XDocument(root); 如需 XmlDocument：var doc=new XmlDocument(); using var xr=xdoc.CreateReader(); doc.Load(xr); 或使用 XNode.ReadFrom/WriteTo。LINQ to XML 在片段操作上更直觀。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q5, B-Q8, D-Q10

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 WriteRaw 寫入後顯示為「&lt;a/&gt;」怎麼辦？
- A簡: 這是 DOM 將 Raw 視為文字的結果；改用 InnerXml 或 Reader+WriteNode。
- A詳: 症狀：保存 XmlDocument 出現 &lt;a/&gt;。原因：DOM writer 將 WriteRaw 當文字節點處理。解法：1) 小片段用 InnerXml；2) 用 XmlReader(Fragment)+WriteNode 正確建樹。預防：在 DOM 上避免用 WriteRaw 插入片段。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q1, C-Q2

D-Q2: 混用 WriteRaw 與 WriteStartElement 後結構錯亂？
- A簡: 交錯導致片段邊界不明。改以 WriteNode 一次性輸入片段，避免交錯。
- A詳: 症狀：最終 XML 結構破裂或節點順序異常。原因：Raw 片段與元素呼叫交錯，狀態難以協調。解法：將片段改以 XmlReader(Fragment)+WriteNode 寫入，避免 Raw 與節點 API 混用。預防：規範只用一種策略管理結構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q5, C-Q7

D-Q3: 設置 InnerXml 時拋 XmlException，如何排查？
- A簡: 表示片段不良構。檢查根元素閉合、命名空間、非法字元與實體。
- A詳: 症狀：InnerXml 指派即例外。原因：未閉合標籤、重複屬性、xmlns 衝突、控制字元或未宣告實體。步驟：用 XmlReader 驗證片段，或用 XDocument.Parse 檢測。修正內容或改用 WriteNode。預防：前置驗證與單元測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q6, C-Q1

D-Q4: 為何 WriteNode 用 ConformanceLevel.Document 會失敗？
- A簡: 片段含多個頂層節點時，Document 模式不允許，應改用 Fragment。
- A詳: 症狀：XmlException 提示多個根元素或宣告位置錯誤。原因：Document 模式要求單一根。解法：將 XmlReaderSettings.ConformanceLevel 設為 Fragment。預防：依資料型態選擇正確模式，片段一律用 Fragment。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q9, C-Q2

D-Q5: 重複使用 InnerXml 效能不佳，怎麼優化？
- A簡: InnerXml 每次完整解析。改以 WriteNode、預先解析 XNode，或批次處理。
- A詳: 症狀：大量更新時 CPU 飆高。原因：每次 InnerXml 都重新解析字串。解法：用 XmlReader(Fragment)+WriteNode；或先 XElement.Parse 再 Add，重用已解析的節點樹；合併多次更新為單次批次。預防：避免在迴圈中頻繁指派 InnerXml。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, C-Q2, C-Q10

D-Q6: 如何診斷目前使用的 XmlWriter 是否為 DOM 寫入器？
- A簡: 檢視取得來源。AppendChild 取得者幾乎是 DOM；Create(Stream) 為串流。
- A詳: 症狀：行為與預期不同。方法：追蹤建構路徑；若來自 doc.CreateNavigator().AppendChild() 即 DOM；若來自 XmlWriter.Create(StringWriter/Stream) 則串流。也可以整合測試驗證 Raw 行為。預防：用明確命名工廠/抽象封裝目標類型。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q8, C-Q8

D-Q7: 如何避免雙重跳脫（double-escaping）問題？
- A簡: 僅對純文字用 WriteString；對片段用 WriteNode；避免先轉義後 WriteString。
- A詳: 症狀：輸出出現 &amp;amp;lt;。原因：對已轉義字串再次 WriteString。解法：明確區分資料性質；純文字直接 WriteString；原生片段走 WriteNode；不得使用 WriteRaw 混寫未跳脫文字。預防：建立輸出層策略與型別標註。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q4, C-Q7

D-Q8: WriteRaw 格式化（縮排、換行）不如預期怎麼辦？
- A簡: Raw 內容不受格式器干預；請自行包含換行或改用自動縮排設定。
- A詳: 症狀：縮排錯位或無換行。原因：WriteRaw 跳過格式器，內容原樣輸出。解法：在 Raw 中自行加入必要空白或換行；或避免 Raw，改用正式 API（WriteElementString 等）並開啟 XmlWriterSettings.Indent。預防：統一由 writer 處理格式化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, B-Q8, A-Q4

D-Q9: 不可信片段導致安全風險，如何處理？
- A簡: 絕不接受原樣片段；先驗證/白名單解析，再用 WriteNode 或 WriteString。
- A詳: 症狀：注入惡意標記或實體炸彈。原因：直接 WriteRaw 或 InnerXml 未過濾。解法：以安全的 parser（禁用 DTD，XmlReaderSettings.DtdProcessing=Prohibit）解析，僅允許預期節點，之後用 WriteNode。純文字輸入一律 WriteString。預防：輸入驗證與安控測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q13, C-Q3

D-Q10: 片段插入後命名空間錯亂怎麼排查？
- A簡: 檢查 xmlns 宣告位置與前綴對應；必要時在父節點先行宣告。
- A詳: 症狀：前綴未綁定或重複宣告。原因：片段宣告與父層不一致或遺漏。解法：在寫入前建立正確的命名空間環境（WriteStartElement 含 namespace），或保留片段內宣告。使用 WriteNode(false) 讓 writer 管理宣告。預防：規範片段命名空間策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, B-Q4, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 XmlWriter？
    - A-Q3: 什麼是 WriteRaw？
    - A-Q4: WriteRaw 的設計初衷與適用情境是什麼？
    - A-Q12: WriteRaw 與 WriteString 有何差異？
    - A-Q13: WriteRaw 與 WriteCData 的差異？
    - A-Q8: 什麼是 XML 片段與完整文件？
    - A-Q9: 什麼是 ConformanceLevel？
    - B-Q3: 含「<」的文字節點在序列化時如何處理？
    - B-Q8: 寫入串流與寫入 DOM 的架構差異？
    - C-Q1: 如何用 InnerXml 將片段插入 XmlDocument？
    - C-Q3: 如何安全寫入使用者輸入到 XML？
    - D-Q1: 遇到 WriteRaw 寫入後顯示為「&lt;a/&gt;」怎麼辦？
    - D-Q4: 為何 WriteNode 用 ConformanceLevel.Document 會失敗？
    - D-Q8: WriteRaw 格式化不如預期怎麼辦？
    - A-Q16: Microsoft 對此回報的核心結論為何？

- 中級者：建議學習哪 20 題
    - A-Q2: 什麼是 XmlWellFormedWriter？
    - A-Q5: 為何在 XmlDocument/XDocument 上使用 WriteRaw 具爭議？
    - A-Q6: 視為文字與解析為節點的差異？
    - A-Q7: 為何選擇「視為文字」？
    - A-Q10: 什麼是 InnerXml？
    - A-Q11: 什麼是 WriteNode？
    - B-Q1: XmlWriter 建立於 XmlDocument 時如何運作？
    - B-Q2: WriteRaw 在 DOM 支援下的處理機制是什麼？
    - B-Q4: XmlReader(Fragment)+WriteNode 的流程？
    - B-Q6: 使用 InnerXml 追加片段的內部流程為何？
    - B-Q9: ConformanceLevel 在 XmlReader 的機制與影響？
    - C-Q2: 用 XmlReader(Fragment)+WriteNode 安全插入片段
    - C-Q4: 在寫入檔案時正確使用 WriteRaw
    - C-Q7: 將 WriteRaw 程式改為 WriteNode 模式
    - C-Q9: 片段插入的命名空間處理
    - C-Q10: LINQ to XML 插入片段
    - D-Q2: 混用 WriteRaw 與節點 API 結構錯亂
    - D-Q3: InnerXml 擲例外排查
    - D-Q6: 診斷 XmlWriter 是否為 DOM 寫入器
    - D-Q7: 避免雙重跳脫問題

- 高級者：建議關注哪 15 題
    - B-Q5: 為何跨多次 WriteRaw 難以解析成節點？
    - B-Q7: XmlWellFormedWriter 的核心組件與檢查機制？
    - B-Q11: WriteRaw 與其他呼叫交錯的複雜度
    - B-Q12: .NET 對 WriteRaw 的契約是什麼？
    - B-Q13: 設計穩健的片段插入管線
    - B-Q14: NotSupportedException vs 靜默文字化
    - A-Q14: 為何此情境可考慮拋 NotSupportedException？
    - A-Q15: 使用 WriteRaw 的風險與安全考量
    - C-Q5: AppendXmlFragment 擴充方法
    - C-Q6: 測試 WriteRaw 在 DOM 與串流不同行為
    - C-Q8: 辨識 XmlWriter 是否寫入 DOM
    - D-Q5: InnerXml 效能優化
    - D-Q9: 不可信片段的安全防護
    - D-Q10: 命名空間錯亂排查
    - C-Q2: XmlReader(Fragment)+WriteNode 標準實作