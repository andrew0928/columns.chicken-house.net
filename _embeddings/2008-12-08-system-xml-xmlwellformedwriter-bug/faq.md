# 原來 System.Xml.XmlWellFormedWriter 有 Bug ..

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 XmlWriter？
- A簡: .NET 的串流式 XML 輸出 API，提供逐步寫入節點、屬性與內容的能力。
- A詳: XmlWriter 是 .NET 中用於產生 XML 的抽象類別，採用順序寫入（forward-only）的串流模式。它提供 WriteStartElement、WriteString、WriteEndElement 等方法，能控制元素、屬性、處理指令與註解的輸出。相較於 DOM（如 XmlDocument），XmlWriter 記憶體占用小、速度快，適合大量或即時輸出場景，如記錄檔、管線輸出與網路串流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q12, B-Q10

Q2: XmlTextWriter 與 XmlWellFormedWriter 有什麼差異？
- A簡: 兩者皆為 XmlWriter 實作；在 WriteRaw 上行為不同，前者依規範，後者有雙重編碼問題。
- A詳: XmlTextWriter 是公開類別，遵循 MSDN 對 WriteRaw 的規範：不額外轉義，直接輸出字串。XmlWellFormedWriter 是框架內部用於確保良構的實作，會包裝多種來源（如 XmlDocument 的 AppendChild 產生）。本文案例顯示其在 WriteRaw 上會對已轉義內容再次編碼，導致 &lt; 變 &amp;lt;，屬於不符規範的行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q8, B-Q1, B-Q2

Q3: 什麼是 WriteRaw？何時該使用？
- A簡: 直接寫入未驗證、未轉義的原始 XML 字串；需自行確保合法與安全。
- A詳: WriteRaw(string) 會把參數原封不動寫入輸出流，不做字元轉義或結構驗證。因此速度快、彈性高，但風險也高：一旦傳入不合法的 XML（如未轉義的 < 或不匹配的結束標記），整份輸出會被破壞。通常僅在上游字串已被信任且確保為合法 XML 片段時使用，否則應改用 WriteString 或透過 XmlReader 解析後再寫出。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q13, B-Q9, C-Q10

Q4: WriteString 與 WriteRaw 的差異是什麼？
- A簡: WriteString 會自動轉義非法字元；WriteRaw 不轉義、不驗證，直接輸出。
- A詳: WriteString 適用於寫入純文字內容，會自動把 <、&、" 等轉為 &lt;、&amp;、&quot;，確保輸出仍為良構 XML。WriteRaw 則假定呼叫端提供的是合法 XML 片段，不做任何整理與檢查。若要插入元素或屬性結構，應用 WriteRaw 或管線方式；若只插入文字，應選擇 WriteString 以降低風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, B-Q9, C-Q10

Q5: 什麼是 XML 片段（XmlFragment）？
- A簡: 不含單一根元素的多段頂層 XML 內容；需以 Fragment 模式解析。
- A詳: XML 片段指一段包含多個並列頂層節點的內容，例如 "<a/><b/><c/>"，它不是完整文件（缺少單一根元素）。解析片段需使用 XmlReaderSettings.ConformanceLevel=Fragment，讓解析器放寬單根限制。常用於模板插入、多段批量輸出或跨系統拼接時，應搭配管線寫出以維持良構性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q8, C-Q4

Q6: XmlReader 是什麼？主要用途為何？
- A簡: 只進式、向前讀的 XML 解析器，逐節點提供 NodeType、Name、Value 等資訊。
- A詳: XmlReader 是 .NET 的串流式解析器，採 forward-only、read-only 模式，不建立完整樹。透過 Read() 逐步前進，並依 NodeType（元素、文字、註解等）存取細節。它可降低記憶體與延遲，常搭配 XmlWriter 組成「讀-寫」管線，將已解析的語義安全地重建成輸出，避免 WriteRaw 帶來的風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q5, C-Q3

Q7: XmlDocument.CreateNavigator().AppendChild() 取得的 XmlWriter 有何特性？
- A簡: 會回傳 XmlWellFormedWriter，直接把內容寫入 XmlDocument 節點樹。
- A詳: 透過 XPathNavigator.AppendChild() 取得的 Writer，內部是 XmlWellFormedWriter，負責在寫入過程維持節點序與良構性，並直接構建至 XmlDocument。其優點是無須先建完整字串再載入；但在 WriteRaw 的實作上存在雙重編碼問題，需改用安全寫法（如 XmlCopyPipe）避免錯誤輸出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q8, B-Q3, C-Q5

Q8: 為何 XmlWellFormedWriter 的 WriteRaw 會造成雙重編碼？
- A簡: 其實作對已轉義內容再次轉義，將 < → &lt; → &amp;lt;，與規範不符。
- A詳: 實務觀察顯示，XmlWellFormedWriter 在 WriteRaw 上會多做一層字元轉義，將呼叫端原本就合法的片段再度編碼，產生 &amp;lt; 這類結果。相比之下，XmlTextWriter 會依規範原樣寫出。此差異導致用相同程式碼在不同 Writer 上得到迥異輸出，因此建議避免對其呼叫 WriteRaw。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q2, C-Q8, D-Q1

Q9: MSDN 對 WriteRaw 行為的規範是什麼？
- A簡: 應原封輸出呼叫端提供的合法 XML 字串，不應另行轉義或驗證。
- A詳: 依 MSDN，WriteRaw 旨在讓高階使用者輸出既有的 XML 片段，因此不進行轉義、正規化或驗證，呼叫端必須自保合法性。XmlTextWriter 符合此設計，而 XmlWellFormedWriter 的再次編碼行為違反預期。當需安全性時，應改以 WriteString 或 XmlReader→XmlWriter 管線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q4, B-Q1, B-Q9

Q10: 什麼是「雙重編碼」？
- A簡: 已被轉義的字元再次被轉義，如 < 轉 &lt; 又變 &amp;lt;，造成顯示錯誤。
- A詳: 在 XML/HTML 中，<、& 等需用實體（如 &lt;、&amp;）表示。若同一內容被連續轉義兩次，就會把 &lt; 的 & 符號再轉為 &amp;，形成 &amp;lt;。呈現時會露出原文字，而非結構。這會破壞輸出語義，影響解析與顯示，常見於不當串接或錯誤 API 行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q8, D-Q2

Q11: WriteEndElement 與 WriteFullEndElement 有何差異？
- A簡: WriteEndElement 可能輸出自閉合；WriteFullEndElement 強制輸出成對結束標記。
- A詳: 在空元素情境下，WriteEndElement 得到的輸出可能是 <a />（自閉合）而非 <a></a>。若需要與來源完全一致（例如由 XmlReader 讀到的 EndElement 需對應完整結束），可以改用 WriteFullEndElement，確保輸出穩定，有利差異比對與格式一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q14, C-Q3

Q12: DOM（XmlDocument）與串流 API（XmlReader/Writer）差異？
- A簡: DOM 建樹可隨機存取，耗記憶體；串流順序處理，省資源但不可回讀。
- A詳: XmlDocument 會載入整份 XML 成為節點樹，便於查詢、修改與搬移（如 ImportNode）。XmlReader/Writer 則走一次、順序操作，極省記憶體且效能佳，適合巨量資料輸入輸出或即時管線。實務上常用 Reader 解析、Writer 輸出，或混用以兼顧可用性與性能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q13, B-Q15

Q13: 為什麼需要 XmlCopyPipe？
- A簡: 用解析後的節點重建輸出，避開 WriteRaw 風險與 WellFormedWriter 的 Bug。
- A詳: XmlCopyPipe 指以 XmlReader 讀入已解析的 NodeType 與值，再以對應的 WriteXXX 寫出至 XmlWriter。此法兼具安全與性能：避免 WriteRaw 破壞良構或雙重編碼，也省去先組字串再重新解析的開銷。對含片段、多根或混合內容（元素、文字、註解）尤為適合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, C-Q8, D-Q1

Q14: XmlReaderSettings.ConformanceLevel 有哪些選項？何時用？
- A簡: Document 與 Fragment。Fragment 允許多個頂層節點，適合處理片段。
- A詳: 預設 Document 要求單一根元素並完整宣告。設定 ConformanceLevel=Fragment 則放寬限制，允許 <a/><b/> 這類多頂層片段被解析。當要把多段內容插入某個父元素內，或從外部來源接收片段時，務必啟用 Fragment，否則會因多根而拋例外。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q8, C-Q4, D-Q4

Q15: 什麼是「良構（well-formed）」XML？為什麼重要？
- A簡: 遵循語法規則（單一根、正確巢狀、正確轉義）；否則解析會失敗。
- A詳: 良構意指 XML 符合基本文法：單一根元素、大小寫敏感、一一對應的開始/結束標記、正確的屬性引用與字元實體。良構是所有解析器的最低要求，未達標將直接拋錯或產生錯誤輸出。使用 WriteString 與管線策略是維持良構的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, B-Q9

---

### Q&A 類別 B: 技術原理類

Q1: XmlTextWriter 如何處理 WriteRaw？
- A簡: 依規範直接輸出字串，不轉義、不驗證，保持原貌。
- A詳: 技術原理說明：XmlTextWriter 將 WriteRaw 的字串直接寫入基礎輸出流，省略任何轉換。關鍵步驟/流程：接收字串→直接 Flush 至 TextWriter/Stream。核心組件：TextWriter、編碼設定（Encoding）、緩衝區。此行為與 MSDN 一致，適合受信任的已合法片段。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q9, C-Q1

Q2: XmlWellFormedWriter 在 WriteRaw 上的機制為何會出錯？
- A簡: 實作中對已轉義內容再次轉義，導致 &lt; 變成 &amp;lt; 的雙重編碼。
- A詳: 技術原理說明：WellFormedWriter 為維持良構與一致性，常在輸出前走字元篩查；其 WriteRaw 實作疑似未完全遵循“原樣輸出”的契約。關鍵流程：接收字串→掃描特定字元→再轉義→輸出。核心組件：WellFormedWriter 包裝、字元寫入器。結果是 WriteRaw 成為「WriteEncoded」，造成偏差。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q8, D-Q1

Q3: CreateNavigator().AppendChild() 產生的 Writer 如何運作？
- A簡: 透過 WellFormedWriter 把串流輸出直接建成 XmlDocument 節點樹。
- A詳: 技術原理說明：XPathNavigator 定位到目標節點後，AppendChild 會回傳一個 Writer，內部使用 WellFormedWriter 驗證標記序列並建樹。關鍵流程：WriteStartElement→寫屬性→文字/子節點→結束→關閉時合併入 DOM。核心組件：XPathNavigator、XmlWellFormedWriter、XmlDocument。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q2, C-Q5

Q4: XmlCopyPipe 的運作原理是什麼？
- A簡: Reader 解析節點，按 NodeType 分派至對應的 WriteXXX，逐一重建輸出。
- A詳: 技術原理說明：以 while(reader.Read()) 驅動，switch(reader.NodeType) 決定寫入 API。關鍵步驟：Element→WriteStartElement+WriteAttributes；Text→WriteString；CDATA/Comment/PI/DocType 分別對應；EndElement→WriteFullEndElement。核心組件：XmlReader、XmlWriter、NodeType、WriteAttributes。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q5, C-Q3

Q5: XmlReader.Read 與 NodeType 對應寫出流程如何設計？
- A簡: 以 Read 前進，依 NodeType 呼叫對應 WriteXXX，保持語義一致。
- A詳: 技術原理說明：Read 逐節點推進，NodeType 類型包含 Element、Text、Whitespace、CDATA、EntityReference、ProcessingInstruction、DocumentType、Comment、EndElement。關鍵步驟：switch 映射→寫入→處理空元素與命名空間。核心組件：NodeType 判斷、WriteStart/End、WriteString/Whitespace。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q7, C-Q7

Q6: 為何 WriteAttributes(reader, true) 能複製屬性與命名空間？
- A簡: 讀取當前元素的所有屬性與 namespace 宣告並逐一寫入。
- A詳: 技術原理說明：當 NodeType 為 Element 時，XmlReader 提供屬性游標；WriteAttributes 會迭代 reader 上的屬性與 xmlns 宣告。關鍵步驟：定位元素→寫入元素→WriteAttributes(reader, true)→處理 IsEmptyElement。核心組件：XmlReader 屬性 API、XmlWriter 屬性寫入器、命名空間處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q3, D-Q8

Q7: 空元素與 IsEmptyElement 應如何處理？
- A簡: 檢查 IsEmptyElement，必要時立刻 WriteEndElement 以維持結構完整。
- A詳: 技術原理說明：IsEmptyElement 為 true 表示 <a/>，無子節點；需立即關閉。關鍵步驟：WriteStartElement→WriteAttributes→if (IsEmpty) WriteEndElement。核心組件：IsEmptyElement 屬性、WriteEndElement/WriteFullEndElement。確保輸出與來源一致，避免變形為非預期格式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q14, C-Q3

Q8: ConformanceLevel.Fragment 如何允許多個根？
- A簡: 放寬單根限制，解析器於頂層接受多個並列元素與節點。
- A詳: 技術原理說明：設定 Fragment 後，XmlReader 允許在文件層出現多個頂層 Element、PI、Comment 等。關鍵步驟：XmlReaderSettings.ConformanceLevel=Fragment→Create(reader)→正常 Read。核心組件：XmlReaderSettings、ConformanceLevel 列舉、驗證引擎。用於片段拼接與內嵌多段內容。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q14, C-Q4, D-Q4

Q9: 為何 WriteRaw 不做驗證？如何降低風險？
- A簡: 為性能與彈性設計；可改用 WriteString 或先以 Reader 解析後再寫出。
- A詳: 技術原理說明：WriteRaw 直接寫流，省去解析與轉義成本。關鍵策略：只對受信任的片段使用；否則用 WriteString（自動轉義）或 XmlCopyPipe（先解析後輸出）。核心組件：WriteRaw/WriteString、XmlReader/Writer。此設計把安全責任交給呼叫端，因此需建立防護流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q13, C-Q10, D-Q3

Q10: XmlWriter 的輸出編碼如何決定？
- A簡: 由 XmlWriterSettings.Encoding 或目標基礎流的編碼與宣告決定。
- A詳: 技術原理說明：XmlWriter.Create 可指定 XmlWriterSettings.Encoding；若目標是 TextWriter（如 Console.Out），則沿用其編碼。關鍵步驟：設定 Encoding→Create→首次寫入會輸出宣告與編碼。核心組件：XmlWriterSettings、XmlDeclaration、TextWriter/Stream。務必一致以避免亂碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, D-Q6

Q11: 為何處理指令與 XML 宣告要透過專用 API？
- A簡: Writer 管控格式與位置；使用 WriteProcessingInstruction 與自動宣告生成。
- A詳: 技術原理說明：處理指令（PI）與 XML 宣告有嚴格位置/格式限制。關鍵步驟：PI 用 WriteProcessingInstruction(name, value)；宣告通常由 Writer 依設定自動輸出，避免手寫錯誤。核心組件：WriteProcessingInstruction、XmlDeclaration、自動序列化器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q7

Q12: EntityReference 與 WriteEntityRef 的作用是什麼？
- A簡: 輸出命名實體參考（如 nbsp、amp），保留語義與可讀性。
- A詳: 技術原理說明：EntityReference 節點代表 &name; 形式的實體。關鍵步驟：讀到 EntityReference→writer.WriteEntityRef(reader.Name)。核心組件：EntityResolver（若展開）、實體表。對需保留原樣的內容（如轉義教學、模板）特別有用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q7

Q13: 空白與重要空白該如何處理？
- A簡: 依 NodeType 分別用 WriteWhitespace 寫出，保留排版與語義。
- A詳: 技術原理說明：Whitespace 與 SignificantWhitespace 區分可忽略與不可忽略空白。關鍵步驟：switch 兩種空白→writer.WriteWhitespace(reader.Value)。核心組件：空白節點分類、空白保留（xml:space）。確保格式化與資料語義（如混合內容）不被破壞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q7

Q14: 為何在 Pipe 中使用 WriteFullEndElement？
- A簡: 保證輸出與來源閉合形式一致，避免空元素被折成自閉合。
- A詳: 技術原理說明：某些格式化或比較工具要求完整結束標記；自閉合與成對結束在語義等價但字串不同。關鍵步驟：遇 EndElement→WriteFullEndElement。核心組件：EndElement 處理策略、格式一致性需求。提升 diff 穩定性與可讀性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q7, C-Q3

Q15: Pipe 模式對效能與可用性有何影響？
- A簡: 以解析後節點直寫輸出，避免重複解析，兼顧安全與性能。
- A詳: 技術原理說明：Reader 已完成語法分析，Writer 只需對應序列化，無需再 parse 原始字串。關鍵步驟：Read→switch→Write；可串流大量資料。核心組件：XmlReader/Writer、緩衝策略。相較 ImportNode 需建兩顆 DOM，Pipe 更省資源且可邊讀邊寫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q6, D-Q10

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何用 XmlTextWriter 正確寫出 XML 片段？
- A簡: 在父元素內用 WriteRaw 寫入片段，或以 Reader 解析後寫入。
- A詳: 實作步驟：1) var w=XmlWriter.Create(...); 2) w.WriteStartElement("root"); 3) w.WriteRaw("<a/><b/><c/>"); 4) w.WriteEndElement(); 5) w.Close。程式碼片段:
  w.WriteStartElement("root"); w.WriteRaw("<a/><b/>"); w.WriteEndElement();
  注意：WriteRaw 僅在片段確保合法時使用。最佳實踐：若片段來源不可信，改以 XmlReader(Fragment)+Pipe 寫入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, C-Q4

Q2: 如何用 XmlWellFormedWriter 寫入已解析資料並避開 WriteRaw？
- A簡: 以 XmlReader 解析片段，再以 XmlCopyPipe 將節點寫入 Writer。
- A詳: 實作步驟：1) 以 ConformanceLevel.Fragment 建立 XmlReader；2) 取得 xmldoc.CreateNavigator().AppendChild(); 3) 先 WriteStartElement("root")；4) XmlCopyPipe(reader, writer)；5) Close。程式碼：
  XmlReader r=XmlReader.Create(sr, new XmlReaderSettings{ConformanceLevel=Fragment});
  XmlCopyPipe(r, writer);
  注意：避免直接呼叫 WriteRaw。最佳實踐：以 Pipe 確保良構與正確編碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q13, B-Q4

Q3: 如何實作 XmlCopyPipe 方法？
- A簡: 以 while(reader.Read()) + switch(NodeType) 對應 WriteXXX 寫出。
- A詳: 具體步驟：1) 檢查參數非 null；2) while(reader.Read()); 3) switch NodeType→Element: WriteStartElement+WriteAttributes(+IsEmpty)、Text: WriteString、CDATA: WriteCData、PI: WriteProcessingInstruction、DocType: WriteDocType、Comment: WriteComment、EndElement: WriteFullEndElement。程式碼片段：參考文內 XmlCopyPipe。注意：確保 EndElement 對應完整閉合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, B-Q14

Q4: 如何設定 XmlReader 以讀取多個根節點的片段？
- A簡: 設定 XmlReaderSettings.ConformanceLevel=Fragment，然後建立 Reader。
- A詳: 實作步驟：1) var settings=new XmlReaderSettings{ConformanceLevel=Fragment}; 2) var reader=XmlReader.Create(new StringReader("<a/><b/>"), settings)；3) while(reader.Read()) 處理。程式碼：
  var s=new XmlReaderSettings{ConformanceLevel=ConformanceLevel.Fragment};
  var r=XmlReader.Create(new StringReader(xml), s);
  注意：若用 Document 會拋多根例外。最佳實踐：配合同步的 Pipe。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q14, B-Q8

Q5: 如何把字串片段輸出到 XmlDocument？
- A簡: 使用 AppendChild 取得 Writer，WriteStartElement 包住，再 Pipe 寫入。
- A詳: 步驟：1) var doc=new XmlDocument(); 2) var w=doc.CreateNavigator().AppendChild(); 3) w.WriteStartElement("root"); 4) var r=XmlReader.Create(new StringReader(fragment), new XmlReaderSettings{ConformanceLevel=Fragment}); 5) XmlCopyPipe(r,w); 6) w.WriteEndElement(); 7) w.Close(); 8) doc.Save(...）。注意：避免 WriteRaw。最佳實踐：以 Pipe 確保一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q2, C-Q3

Q6: 如何把一個 XmlDocument 的片段複製到另一個 XmlWriter？
- A簡: 使用 XmlNodeReader 讀來源節點，Pipe 到目標 XmlWriter。
- A詳: 步驟：1) var node=srcDoc.DocumentElement; 2) var reader=new XmlNodeReader(node); 3) 目標 writer.WriteStartElement("root"); 4) XmlCopyPipe(reader, writer); 5) writer.WriteEndElement(); 6) 關閉。程式碼片段：
  using var r=new XmlNodeReader(node); XmlCopyPipe(r, w);
  注意：XmlNodeReader 預設 ConformanceLevel=Fragment。最佳實踐：保留命名空間與屬性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q15

Q7: 如何在 Pipe 中處理 CDATA、註解與處理指令？
- A簡: 對應使用 WriteCData、WriteComment、WriteProcessingInstruction 寫出。
- A詳: 步驟：在 switch(NodeType) 中加入：CDATA→writer.WriteCData(reader.Value)；Comment→WriteComment(reader.Value)；ProcessingInstruction→WriteProcessingInstruction(reader.Name, reader.Value)。程式碼片段：參照 XmlCopyPipe。注意：PI 與 DocType 的位置需合理。最佳實踐：保持與來源一致以利比對。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q11

Q8: 如何在 .NET 中避免 XmlWellFormedWriter 的 WriteRaw 雙重編碼？
- A簡: 不用 WriteRaw；改以 XmlReader+XmlCopyPipe 或使用 WriteString。
- A詳: 步驟：1) 將字串片段用 XmlReader(Fragment) 解析；2) 以 XmlCopyPipe 寫入 WellFormedWriter；3) 僅在純文字時用 WriteString。程式碼：
  var r=XmlReader.Create(new StringReader(xml), new XmlReaderSettings{ConformanceLevel=Fragment});
  XmlCopyPipe(r, writer);
  注意：此法同時防止非法輸入破壞輸出。最佳實踐：建立共用 Pipe 工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q2, C-Q2, D-Q1

Q9: 如何測試與比較 XmlTextWriter 與 XmlWellFormedWriter 輸出差異？
- A簡: 對同一段程式碼分別建立兩種 Writer，輸出到字串並比對。
- A詳: 步驟：1) 建立 StringWriter+XmlWriter.Create 與 XmlDocument.AppendChild 兩組；2) 執行相同寫入流程（含 WriteRaw）；3) 分別取得字串；4) 比對差異（應看到 &lt; vs &amp;lt;）。程式碼：以 StringWriter、Console.Out 或 MemoryStream 收集。注意：確保相同編碼與格式化設定。最佳實踐：加入單元測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, B-Q2

Q10: 如何安全地插入未轉義的 XML 內容？
- A簡: 先用 XmlReader 解析該內容，確認合法後再 Pipe 到目標 Writer。
- A詳: 步驟：1) 使用 Fragment 設定建立 Reader；2) 若解析失敗即中止（避免破壞良構）；3) 成功則 XmlCopyPipe 寫入；4) 包在預期的父元素內。程式碼片段：
  var r=XmlReader.Create(new StringReader(xmlFrag), s);
  XmlCopyPipe(r, w);
  注意：不要用 WriteRaw 直寫。最佳實踐：對外部來源一律解析驗證後寫出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q9, C-Q2

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 使用 XmlWellFormedWriter.WriteRaw 後輸出出現 &amp;lt; 等轉義，怎麼辦？
- A簡: 停用 WriteRaw，改以 XmlReader+XmlCopyPipe 或用 WriteString。
- A詳: 問題症狀：原本應為 <a/> 的片段被輸出為 &amp;lt;a/&amp;gt;。可能原因：WellFormedWriter 在 WriteRaw 進行了再次編碼。解決步驟：以 Fragment Reader 解析片段→XmlCopyPipe 寫入→或改寫成 WriteString（僅文字）。預防：封裝共用 Pipe；禁止在 WellFormedWriter 上呼叫 WriteRaw。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q8

Q2: 為何輸出 XML 變成雙重編碼？如何診斷？
- A簡: 來源字串已轉義又被 Writer 二次轉義；比對不同 Writer 輸出確認。
- A詳: 症狀：&lt; 變 &amp;lt;、&amp; 變 &amp;amp;。原因：混用 WriteRaw/WriteString 或 Writer 錯誤行為。診斷：以相同程式碼在 XmlTextWriter 與 WellFormedWriter 產生輸出並比對。解法：改用 Pipe；統一輸出策略。預防：建立單元測試檢查關鍵片段。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q2, C-Q9

Q3: WriteRaw 導致輸出不合法（壞掉的 XML），如何修復？
- A簡: 改以 WriteString 或先解析後寫出；檢查來源片段合法性。
- A詳: 症狀：解析時拋 XML 異常、缺閉合或非法字元。原因：未轉義 <、& 或結構錯誤。解決：把文字用 WriteString；元素用 XmlReader 解析再 Pipe。預防：禁止外部輸入直通 WriteRaw；設定 Fragment 模式驗證片段；加入輸入白名單過濾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q9, C-Q10

Q4: XmlReader 讀取片段時出現「多個根元素」例外，怎麼辦？
- A簡: 將 ConformanceLevel 設為 Fragment，再建立 Reader。
- A詳: 症狀：讀取 "<a/><b/>" 時拋出單根限制錯誤。原因：使用預設 Document 模式。解決步驟：XmlReaderSettings.ConformanceLevel=Fragment→XmlReader.Create(...)。預防：凡處理片段一律啟用 Fragment，並在 API 邊界清楚註記輸入型態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q14, C-Q4

Q5: Pipe 後輸出少了結尾標記，原因與解法？
- A簡: 可能錯用 WriteEndElement 或漏處理 EndElement，改用 WriteFullEndElement。
- A詳: 症狀：來源為 <a></a>，輸出成 <a/> 或遺漏結尾。原因：未處理 EndElement 或使用自閉合策略。解決：在 EndElement 分支呼叫 WriteFullEndElement；確認 IsEmptyElement 時機。預防：加入回歸測試，覆蓋空元素與非空元素案例。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, B-Q14, C-Q3

Q6: Console.Out 與 XmlWriter 編碼不符導致亂碼，怎麼辦？
- A簡: 明確設定 XmlWriterSettings.Encoding 或改用對應編碼的 TextWriter。
- A詳: 症狀：中文字或特殊字元顯示錯亂。原因：Console.Out 編碼與 XmlWriter 宣告不一致。解決：XmlWriter.Create(Console.Out, new XmlWriterSettings{Encoding=Console.OutputEncoding})；或輸出到 MemoryStream/StringWriter 再以正確編碼寫出。預防：統一編碼策略與宣告。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10

Q7: 使用 AppendChild 後 Save 輸出空文件，為什麼？
- A簡: 可能未寫入任何節點或未關閉 Writer，導致變更未提交。
- A詳: 症狀：doc.Save() 無輸出或僅宣告。原因：未呼叫 WriteStartElement/WriteEndElement、未 Close/Flush Writer。解決：確保正確的開始/結束寫入並 Close；檢查 Pipe 是否有 Read 迴圈。預防：以 using 包裝 Writer；加入寫入計數與斷言。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q5

Q8: 為什麼 WriteAttributes 不會複製預設命名空間？
- A簡: 預設 xmlns 受命名空間範疇影響，需確保來源/目標上下文一致。
- A詳: 症狀：輸出節點缺少預設 xmlns，導致解析到錯誤命名空間。原因：WriteAttributes 依 reader 當前上下文寫入；若目標已有不同預設 xmlns 或範疇不一致，就需手動處理。解決：顯式寫入需要的 xmlns 或使用 WriteStartElement(prefix, local, ns)。預防：在 Pipe 起始元素建立正確命名空間。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q6, C-Q6

Q9: 為何 WriteEndElement 與 WriteFullEndElement 讓格式不同導致比對困難？
- A簡: 自閉合與完整結束雖等價但字串不同；需統一策略。
- A詳: 症狀：Diff 工具顯示大量差異但語義相同。原因：WriteEndElement 可能折疊為 <a/>；WriteFullEndElement 輸出 </a>。解決：在 Pipe 固定使用 WriteFullEndElement；或在比對前正規化格式。預防：建立一致的序列化規則並文件化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q14, C-Q3

Q10: 大量複製 XML 時效能不佳，如何優化？
- A簡: 使用 Reader→Writer 管線，避免 DOM 兩次解析與 ImportNode 開銷。
- A詳: 症狀：記憶體高與 GC 頻繁。原因：同時建立多顆 XmlDocument 或字串拼接後再解析。解決：以 XmlReader 串流讀、XmlWriter 串流寫（XmlCopyPipe）；關閉格式化與驗證；使用適當緩衝。預防：避免中介巨大字串，採用串流與分段處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q15, C-Q6

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 XmlWriter？
    - A-Q2: XmlTextWriter 與 XmlWellFormedWriter 有什麼差異？
    - A-Q3: 什麼是 WriteRaw？何時該使用？
    - A-Q4: WriteString 與 WriteRaw 的差異是什麼？
    - A-Q5: 什麼是 XML 片段（XmlFragment）？
    - A-Q6: XmlReader 是什麼？主要用途為何？
    - A-Q11: WriteEndElement 與 WriteFullEndElement 有何差異？
    - A-Q14: XmlReaderSettings.ConformanceLevel 有哪些選項？何時用？
    - A-Q15: 什麼是「良構（well-formed）」XML？為什麼重要？
    - B-Q5: XmlReader.Read 與 NodeType 對應寫出流程如何設計？
    - B-Q8: ConformanceLevel.Fragment 如何允許多個根？
    - C-Q1: 如何用 XmlTextWriter 正確寫出 XML 片段？
    - C-Q4: 如何設定 XmlReader 以讀取多個根節點的片段？
    - C-Q9: 如何測試與比較兩種 Writer 的輸出差異？
    - D-Q4: XmlReader 讀取片段時出現「多個根元素」例外，怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q7: AppendChild 取得的 Writer 有何特性？
    - A-Q8: 為何 XmlWellFormedWriter 的 WriteRaw 會造成雙重編碼？
    - A-Q9: MSDN 對 WriteRaw 行為的規範是什麼？
    - A-Q13: 為什麼需要 XmlCopyPipe？
    - B-Q1: XmlTextWriter 如何處理 WriteRaw？
    - B-Q2: XmlWellFormedWriter 在 WriteRaw 上的機制為何會出錯？
    - B-Q3: CreateNavigator().AppendChild() 產生的 Writer 如何運作？
    - B-Q4: XmlCopyPipe 的運作原理是什麼？
    - B-Q6: 為何 WriteAttributes(reader, true) 能複製屬性與命名空間？
    - B-Q7: 空元素與 IsEmptyElement 應如何處理？
    - B-Q10: XmlWriter 的輸出編碼如何決定？
    - B-Q11: 為何處理指令與 XML 宣告要透過專用 API？
    - B-Q14: 為何在 Pipe 中使用 WriteFullEndElement？
    - B-Q15: Pipe 模式對效能與可用性有何影響？
    - C-Q2: 如何用 XmlWellFormedWriter 寫入已解析資料並避開 WriteRaw？
    - C-Q3: 如何實作 XmlCopyPipe 方法？
    - C-Q5: 如何把字串片段輸出到 XmlDocument？
    - C-Q6: 如何把一個 XmlDocument 的片段複製到另一個 XmlWriter？
    - C-Q7: 如何在 Pipe 中處理 CDATA、註解與處理指令？
    - C-Q8: 如何在 .NET 中避免 XmlWellFormedWriter 的 WriteRaw 雙重編碼？

- 高級者：建議關注哪 15 題
    - D-Q1: 使用 XmlWellFormedWriter.WriteRaw 後輸出出現 &amp;lt; 等轉義，怎麼辦？
    - D-Q2: 為何輸出 XML 變成雙重編碼？如何診斷？
    - D-Q3: WriteRaw 導致輸出不合法（壞掉的 XML），如何修復？
    - D-Q5: Pipe 後輸出少了結尾標記，原因與解法？
    - D-Q6: Console.Out 與 XmlWriter 編碼不符導致亂碼，怎麼辦？
    - D-Q7: 使用 AppendChild 後 Save 輸出空文件，為什麼？
    - D-Q8: 為什麼 WriteAttributes 不會複製預設命名空間？
    - D-Q9: 為何 WriteEndElement 與 WriteFullEndElement 讓格式不同導致比對困難？
    - D-Q10: 大量複製 XML 時效能不佳，如何優化？
    - A-Q10: 什麼是「雙重編碼」？
    - B-Q9: 為何 WriteRaw 不做驗證？如何降低風險？
    - B-Q12: EntityReference 與 WriteEntityRef 的作用是什麼？
    - B-Q13: 空白與重要空白該如何處理？
    - C-Q10: 如何安全地插入未轉義的 XML 內容？
    - A-Q12: DOM（XmlDocument）與串流 API（XmlReader/Writer）差異？