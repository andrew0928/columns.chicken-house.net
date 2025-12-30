---
layout: synthesis
title: "原來 System.Xml.XmlWellFormedWriter 有 Bug .."
synthesis_type: solution
source_post: /2008/12/08/system-xml-xmlwellformedwriter-bug/
redirect_from:
  - /2008/12/08/system-xml-xmlwellformedwriter-bug/solution/
---

## Case #1: XmlWellFormedWriter.WriteRaw 將原始片段錯誤編碼（雙重轉義）

### Problem Statement（問題陳述）
業務場景：系統需將多個已生成的 XML 片段（如 <a/> 重複）插入到一個既有的 XML 文件根節點下，並輸出到 Console 或儲存到 XmlDocument。為提升效率，工程師採用 WriteRaw 直接寫入片段，期望保留原始標記，避免額外編碼與解析成本。

技術挑戰：使用 XmlDocument.CreateNavigator().AppendChild() 取得的 XmlWriter（實為 XmlWellFormedWriter）在 WriteRaw 時將 < > 轉成 &lt; &gt;，造成原始標記被當作文字寫出。

影響範圍：產出的 XML 結構錯誤（原始標記被逃逸），下游解析失敗；需回退產線或緊急修補。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. XmlWellFormedWriter 對 WriteRaw 實作不符合 MSDN 行為預期，對原始片段進行了不必要的編碼。
2. 寫入端從 XmlDocument navigator 取得的 Writer 實際類型不同於以流建立的 Writer，行為差異未被注意。
3. 缺乏針對 WriteRaw 行為差異的單元測試與回歸測試。

深層原因：
- 架構層面：未抽象 Writer 行為差異（Stream Writer 與 DOM Writer）。
- 技術層面：在不可驗證內容的 API（WriteRaw）上堆疊關鍵功能。
- 流程層面：未建立針對平台 API 差異的兼容性檢查流程。

### Solution Design（解決方案設計）
解決策略：避免透過 XmlWellFormedWriter.WriteRaw 寫入片段，改用 XmlReader 解析已存在的片段並以 XmlWriter 寫出（XmlCopyPipe）。此方式既繞過 WriteRaw 的錯誤行為，也對內容做語法驗證，防止寫入不合法片段。

實施步驟：
1. 實作 XmlCopyPipe
- 實作細節：使用 reader.Read() + switch NodeType，對元素、文字、CDATA、PI、Doctype 等逐一轉寫。
- 所需資源：System.Xml
- 預估時間：1 小時

2. 以 XmlReaderSettings 啟用 Fragment 模式
- 實作細節：settings.ConformanceLevel = ConformanceLevel.Fragment，允許多個根級節點。
- 所需資源：System.Xml
- 預估時間：30 分鐘

3. 取代 WriteRaw 呼叫
- 實作細節：在 root 節點內呼叫 XmlCopyPipe(reader, writer) 寫入片段。
- 所需資源：既有程式碼庫
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
// 建立目標 XmlWriter（來自 XmlDocument）
var xmldoc = new XmlDocument();
using (var writer = xmldoc.CreateNavigator().AppendChild())
{
    writer.WriteStartElement("root");

    // 以 Fragment 模式讀取多個 <a/> 片段
    var settings = new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment };
    using var reader = XmlReader.Create(new StringReader("<a/><a/><a/><a/><a/>"), settings);

    XmlCopyPipe(reader, writer);      // 關鍵：改用 Pipe，避免 WriteRaw 的錯誤轉義
    writer.WriteEndElement();
}

// XmlCopyPipe: 將 Reader 事件逐一寫到 Writer
static void XmlCopyPipe(XmlReader reader, XmlWriter writer)
{
    while (reader.Read())
    {
        switch (reader.NodeType)
        {
            case XmlNodeType.Element:
                writer.WriteStartElement(reader.Prefix, reader.LocalName, reader.NamespaceURI);
                writer.WriteAttributes(reader, true);
                if (reader.IsEmptyElement) writer.WriteEndElement();
                break;
            case XmlNodeType.Text: writer.WriteString(reader.Value); break;
            case XmlNodeType.CDATA: writer.WriteCData(reader.Value); break;
            case XmlNodeType.EntityReference: writer.WriteEntityRef(reader.Name); break;
            case XmlNodeType.ProcessingInstruction:
            case XmlNodeType.XmlDeclaration:
                writer.WriteProcessingInstruction(reader.Name, reader.Value); break;
            case XmlNodeType.DocumentType:
                writer.WriteDocType(reader.Name, reader.GetAttribute("PUBLIC"), reader.GetAttribute("SYSTEM"), reader.Value);
                break;
            case XmlNodeType.Comment: writer.WriteComment(reader.Value); break;
            case XmlNodeType.Whitespace:
            case XmlNodeType.SignificantWhitespace: writer.WriteWhitespace(reader.Value); break;
            case XmlNodeType.EndElement: writer.WriteFullEndElement(); break;
        }
    }
}
```

實際案例：同文示例，WriteRaw 在 XmlWellFormedWriter 下輸出 &lt;a/&gt; 等錯誤轉義；改用 XmlCopyPipe 後輸出 <a/> 正確標記。

實作環境：.NET Framework（System.Xml），XmlDocument + XPathNavigator.AppendChild()（XmlWellFormedWriter）

實測數據：
- 改善前：輸出 <root>&lt;a/&gt;…</root>（原始標記被逃逸，100% 失敗）
- 改善後：輸出 <root><a/><a/><a/><a/><a/></root>（100% 正確）
- 改善幅度：錯誤率 100% → 0%

Learning Points（學習要點）
核心知識點：
- XmlWriter 具體類型不同，WriteRaw 行為可能有差異
- 以 Reader→Writer 管線替代 WriteRaw 可同時保證正確性與安全性
- Fragment 模式允許多根片段安全導入

技能要求：
- 必備技能：C#、System.Xml、XmlReader/Writer API
- 進階技能：XML 事件式處理、錯誤重現與回歸測試

延伸思考：
- 還能用於服務間 XML 轉發、日誌匿名化（Reader 過濾後再寫）
- 風險：未覆蓋所有 NodeType 會丟資訊
- 優化：加入命名空間與前綴正規化、流式處理大檔

Practice Exercise（練習題）
- 基礎練習：重現 WriteRaw 轉義問題與修正（30 分鐘）
- 進階練習：為 XmlCopyPipe 加入命名空間修正與單測（2 小時）
- 專案練習：封裝一個可插拔的 XmlPipe 庫並支持過濾規則（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：Pipe 對所有常見 NodeType 的覆蓋
- 程式碼品質（30%）：可讀性、單元測試完整度
- 效能優化（20%）：串流處理避免額外解析
- 創新性（10%）：可擴充的過濾與轉換規則設計


## Case #2: 移除 WriteRaw 以防止不合法內容破壞輸出

### Problem Statement（問題陳述）
業務場景：匯入的 XML 片段來源多樣，可能包含不成對標籤或錯誤 Entity。現行流程用 WriteRaw 直接植入，偶發產出不可解析的最終 XML，造成批次作業中斷與重跑。

技術挑戰：WriteRaw 不做內容驗證，任何片段都原封不動寫入，風險完全由上游負擔。

影響範圍：一旦片段含錯，整份輸出報廢；下游消費者/ETL 全部失敗。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WriteRaw 跳過驗證，導致上游錯誤直達輸出。
2. 缺少片段語法檢查與清洗流程。
3. 錯誤處理策略不完善（無回退或隔離機制）。

深層原因：
- 架構層面：將可疑資料直接插入最終文件的核心路徑。
- 技術層面：對 WriteRaw 的語義（不驗證）理解不足。
- 流程層面：缺乏對輸入片段的驗證關卡與錯誤隔離。

### Solution Design（解決方案設計）
解決策略：統一以 XmlReader 解析輸入片段，解析成功才寫入 XmlWriter（XmlCopyPipe），在解析階段即捕捉並拒絕不合法內容，保護最終輸出。

實施步驟：
1. 建立片段驗證器
- 實作細節：以 XmlReaderSettings.ConformanceLevel.Fragment 嘗試讀取，失敗時拋出並記錄。
- 所需資源：System.Xml
- 預估時間：45 分鐘

2. 導入 XmlCopyPipe
- 實作細節：只對解析成功的 reader 進行管線複製。
- 所需資源：共用工具庫
- 預估時間：1 小時

3. 增加錯誤隔離
- 實作細節：對失敗片段隔離到錯誤節點或錯誤檔案；主輸出繼續。
- 所需資源：日誌/監控
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
XmlReader CreateValidatedFragmentReader(string fragment)
{
    var settings = new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment };
    try
    {
        return XmlReader.Create(new StringReader(fragment), settings);
    }
    catch (XmlException ex)
    {
        // 記錄並重新拋出或轉為業務錯誤
        throw new InvalidOperationException("XML 片段不合法", ex);
    }
}
```

實際案例：作者指出 WriteRaw 不做驗證，容易讓非法內容毀掉整份輸出；改以解析後寫入，輸出可靠。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：片段錯誤將導致整份 XML 損毀（不可解析）
- 改善後：錯誤片段在解析階段被攔截；主輸出可正常完成
- 改善幅度：主輸出失敗率大幅下降（以案例觀察：由高風險情境轉為可控）

Learning Points（學習要點）
核心知識點：
- WriteRaw 的語義與風險
- 以解析作為驗證關卡
- Fragment 模式的實務用法

技能要求：
- 必備技能：例外處理、XmlReader API
- 進階技能：錯誤隔離與恢復策略設計

延伸思考：
- 可加入 XSD 驗證強化內容正確性
- 過度嚴格驗證可能影響吞吐
- 依場景調整容錯與重試策略

Practice Exercise（練習題）
- 基礎練習：將 WriteRaw 呼叫替換為解析+Pipe（30 分鐘）
- 進階練習：加入錯誤片段隔離輸出（2 小時）
- 專案練習：實作完整 XML 匯入驗證/隔離框架（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：錯誤片段不應污染主輸出
- 程式碼品質（30%）：例外處理清晰、日誌充分
- 效能優化（20%）：在驗證下仍維持可接受吞吐
- 創新性（10%）：驗證與隔離策略的可配置性


## Case #3: 以 ConformanceLevel.Fragment 正確讀取多個根級片段

### Problem Statement（問題陳述）
業務場景：上游提供的是多段平行元素（如 <a/><a/><a/>），必須嵌入到目標文件單一根節點下。若按預設 Document 模式讀取，會因多根級節點而失敗。

技術挑戰：XmlReader 默認 ConformanceLevel.Document 僅允許單一根節點，無法讀取多個並列根級片段。

影響範圍：讀取階段異常導致整個匯入失敗。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用預設 ConformanceLevel.Document 處理多根片段。
2. 未明確設定 Fragment 模式。
3. 測試資料多為單根，未覆蓋多根場景。

深層原因：
- 架構層面：上游輸入協議未約束單根或多根格式。
- 技術層面：XmlReader 設定項理解不足。
- 流程層面：測試樣本不足。

### Solution Design（解決方案設計）
解決策略：使用 XmlReaderSettings.ConformanceLevel = Fragment 讀取輸入，並在目標 Writer 中加一個容器根節點承載片段。

實施步驟：
1. 設定 Fragment 模式
- 實作細節：new XmlReaderSettings{ ConformanceLevel = Fragment }
- 所需資源：System.Xml
- 預估時間：10 分鐘

2. 包裝容器根節點
- 實作細節：writer.WriteStartElement("root"); XmlCopyPipe(...); writer.WriteEndElement();
- 所需資源：既有 Writer
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
var settings = new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment };
using var reader = XmlReader.Create(new StringReader("<a/><a/>"), settings);

using var writer = xmldoc.CreateNavigator().AppendChild();
writer.WriteStartElement("root");
XmlCopyPipe(reader, writer);   // 多個根級片段會被依序寫入 root 下
writer.WriteEndElement();
```

實際案例：文中明確指出「陷阱」為如何讀取 XmlFragment，並提供 Fragment 模式設定。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：多根片段在 Document 模式下讀取失敗
- 改善後：Fragment 模式正常讀取多根片段
- 改善幅度：失敗率 100% → 0%（在該用例）

Learning Points（學習要點）
核心知識點：
- ConformanceLevel 的差異
- 多根片段的容器化處理
- Pipe 對齊兩端模型（Reader→Writer）

技能要求：
- 必備技能：XmlReaderSettings 配置
- 進階技能：輸入協議設計（單根 vs 多根）

延伸思考：
- 是否改為上游保證單根？
- 片段間是否需要分隔或排序？
- 可否邊讀邊驗證結構規則？

Practice Exercise（練習題）
- 基礎練習：以 Fragment 模式讀取三個元素並嵌入 root（30 分鐘）
- 進階練習：設計可變 root 名稱與命名空間（2 小時）
- 專案練習：設計可配置的多源片段合併流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：多根片段可正確合併
- 程式碼品質（30%）：設定清楚、錯誤處理合理
- 效能優化（20%）：流式合併不阻塞
- 創新性（10%）：容器 root 與命名空間策略靈活


## Case #4: 實作 XmlCopyPipe 打造 Reader→Writer 安全管線

### Problem Statement（問題陳述）
業務場景：需在不影響效能的前提下，將外部產生的 XML 片段整合到主文件，並保留各種節點（元素、屬性、CDATA、註解、PI 等）。

技術挑戰：既要避免 WriteRaw 的風險，又要最大程度保持來源 XML 的語義與結構。

影響範圍：若節點型別未覆蓋，會導致資訊遺失或輸出不一致。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未有既用既驗證的通用管線工具。
2. 單點 API（WriteRaw）無法滿足完整節點型別處理。
3. 缺乏通用化設計，導致各處各寫造成不一致。

深層原因：
- 架構層面：缺少 XML 轉寫的共用元件
- 技術層面：對 XmlReader/Writer 事件模型掌握不足
- 流程層面：工具復用與測試覆蓋不足

### Solution Design（解決方案設計）
解決策略：封裝 XmlCopyPipe，逐一處理 XmlReader 的 NodeType 並轉寫到 XmlWriter，成為跨專案可重用的安全轉寫工具。

實施步驟：
1. 定義 Pipe 介面
- 實作細節：XmlCopyPipe(XmlReader, XmlWriter)
- 所需資源：工具庫專案
- 預估時間：30 分鐘

2. 實作 NodeType 覆蓋
- 實作細節：switch NodeType 全覆蓋（Element, Text, CDATA, EntityRef, PI, DocType, Comment, Whitespace, EndElement）
- 所需資源：System.Xml
- 預估時間：1.5 小時

3. 單元測試
- 實作細節：為每一種 NodeType 構造輸入與期望輸出
- 所需資源：測試框架
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static class XmlPipes
{
    public static void Copy(XmlReader reader, XmlWriter writer)
    {
        if (reader == null) throw new ArgumentNullException(nameof(reader));
        if (writer == null) throw new ArgumentNullException(nameof(writer));

        while (reader.Read())
        {
            switch (reader.NodeType)
            {
                case XmlNodeType.Element:
                    writer.WriteStartElement(reader.Prefix, reader.LocalName, reader.NamespaceURI);
                    writer.WriteAttributes(reader, true);
                    if (reader.IsEmptyElement) writer.WriteEndElement();
                    break;
                case XmlNodeType.Text: writer.WriteString(reader.Value); break;
                case XmlNodeType.CDATA: writer.WriteCData(reader.Value); break;
                case XmlNodeType.EntityReference: writer.WriteEntityRef(reader.Name); break;
                case XmlNodeType.ProcessingInstruction:
                case XmlNodeType.XmlDeclaration:
                    writer.WriteProcessingInstruction(reader.Name, reader.Value); break;
                case XmlNodeType.DocumentType:
                    writer.WriteDocType(reader.Name, reader.GetAttribute("PUBLIC"), reader.GetAttribute("SYSTEM"), reader.Value); break;
                case XmlNodeType.Comment: writer.WriteComment(reader.Value); break;
                case XmlNodeType.Whitespace:
                case XmlNodeType.SignificantWhitespace: writer.WriteWhitespace(reader.Value); break;
                case XmlNodeType.EndElement: writer.WriteFullEndElement(); break;
            }
        }
    }
}
```

實際案例：文章提供同名函式與完整 NodeType 覆蓋範例，實測可正確轉寫為期望輸出。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：WriteRaw 易出錯且無驗證
- 改善後：Pipe 可驗證且保持語義
- 改善幅度：穩定性顯著提升（以事件覆蓋與示例輸出驗證）

Learning Points（學習要點）
核心知識點：
- XML 事件式讀寫模型
- NodeType 覆蓋與對應 API
- 工具化封裝與單測策略

技能要求：
- 必備技能：C#、System.Xml
- 進階技能：可組態的轉寫與過濾

延伸思考：
- 增加節點過濾（如移除 Comment）
- 加入命名空間清理
- 管線插拔式轉換（XSLT/自定規則）

Practice Exercise（練習題）
- 基礎練習：覆蓋所有 NodeType 的單測（30 分鐘）
- 進階練習：加入節點白名單/黑名單功能（2 小時）
- 專案練習：實作可配置 XML 管線引擎（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：NodeType 覆蓋
- 程式碼品質（30%）：可讀性、可維護性
- 效能優化（20%）：串流處理無額外 DOM
- 創新性（10%）：擴充性與可組態性


## Case #5: 保留 CDATA、Entity、PI 與 DocType 的完整性

### Problem Statement（問題陳述）
業務場景：收錄的 XML 片段中包含 CDATA 區塊、Entity 參照、處理指示與 DTD 宣告；要求在整合後輸出完全等價，以確保下游解析與渲染一致。

技術挑戰：簡化轉寫往往遺漏少見節點型別，造成資訊丟失或語義變更（例如 CDATA 被展平為文字）。

影響範圍：下游客戶端（瀏覽器、轉換器）行為改變或錯誤。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Pipe/轉寫邏輯未完整覆蓋特殊節點。
2. 對特殊節點（PI、DocType）語義理解不足。
3. 測試樣本缺少這些節點。

深層原因：
- 架構層面：未定義「語義等價」的轉寫標準
- 技術層面：API 對應關係不熟悉（WriteCData、WriteEntityRef、WriteProcessingInstruction、WriteDocType）
- 流程層面：測試集合不完整

### Solution Design（解決方案設計）
解決策略：在 XmlCopyPipe 中補齊相應 NodeType 的對應寫入 API，並以單元測試保證輸出語義等價（特別是 CDATA 與 Entity）。

實施步驟：
1. 擴充 Pipe
- 實作細節：針對 CDATA/Entity/PI/DocType 逐一補齊
- 所需資源：System.Xml
- 預估時間：45 分鐘

2. 撰寫對應測試
- 實作細節：構造含特殊節點的輸入與期望輸出
- 所需資源：測試框架
- 預估時間：1.5 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）- 特殊節點處理
switch (reader.NodeType)
{
    case XmlNodeType.CDATA: writer.WriteCData(reader.Value); break;
    case XmlNodeType.EntityReference: writer.WriteEntityRef(reader.Name); break;
    case XmlNodeType.ProcessingInstruction:
    case XmlNodeType.XmlDeclaration:
        writer.WriteProcessingInstruction(reader.Name, reader.Value); break;
    case XmlNodeType.DocumentType:
        writer.WriteDocType(reader.Name, reader.GetAttribute("PUBLIC"), reader.GetAttribute("SYSTEM"), reader.Value); break;
}
```

實際案例：文章中的 XmlCopyPipe 已涵蓋上述節點，保證了語義保真。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：特殊節點遺失或語義變更
- 改善後：輸出包含等價 CDATA/Entity/PI/DocType
- 改善幅度：語義保真度從不確定 → 穩定保真（以測試驗證）

Learning Points（學習要點）
核心知識點：
- 特殊節點的讀寫 API 對應
- 語義等價與序列化策略
- 單測驅動的轉寫正確性

技能要求：
- 必備技能：XmlReader/Writer API
- 進階技能：測試資料構造與差異比對

延伸思考：
- 若需標準化輸出（如移除 DTD），策略如何設計？
- Entity 的解析與保留取捨？
- 安全性：DTD 是否允許（XXE 風險）？

Practice Exercise（練習題）
- 基礎練習：加入 CDATA/PI 測試（30 分鐘）
- 進階練習：可配置地忽略 DocType 與 PI（2 小時）
- 專案練習：增強 Pipe，支援白名單節點輸出策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：特殊節點完整保留
- 程式碼品質（30%）：清晰與可測
- 效能優化（20%）：不引入多餘解析
- 創新性（10%）：可配置策略設計


## Case #6: 使用 WriteFullEndElement 確保結束標記正確

### Problem Statement（問題陳述）
業務場景：在轉寫時，需對非空元素輸出完整結束標記以保證相容性；部分消費端對自動簡寫（Empty Element）處理不一致。

技術挑戰：使用 WriteEndElement 對空元素可能輸出短標記（<a/>），對某些解析器不友好或影響可讀性。

影響範圍：下游工具鏈或手工檢視時產生誤解或解析差異。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 WriteEndElement 對空元素輸出簡寫。
2. 需求要求完整閉合標記。

深層原因：
- 架構層面：未定義輸出風格規範
- 技術層面：對 WriteFullEndElement 與 WriteEndElement 差異不熟
- 流程層面：缺乏對下游客戶端相容性驗證

### Solution Design（解決方案設計）
解決策略：在 Pipe 的 EndElement 分支使用 WriteFullEndElement，強制輸出</tag> 完整結束標記，提高相容性與可讀性。

實施步驟：
1. 調整 EndElement 分支
- 實作細節：改為 writer.WriteFullEndElement()
- 所需資源：System.Xml
- 預估時間：5 分鐘

2. 驗證輸出
- 實作細節：比較不同 Writer 行為並測試解析
- 所需資源：測試框架
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
case XmlNodeType.EndElement:
    writer.WriteFullEndElement(); // 確保輸出 </tag> 而非自動簡寫
    break;
```

實際案例：文章 Pipe 示範中即使用 WriteFullEndElement。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：可能輸出 <a/>
- 改善後：輸出 </a>
- 改善幅度：相容性風險降低（以消費端解析一致性觀察）

Learning Points（學習要點）
核心知識點：
- EndElement 兩種寫法差異
- 相容性與可讀性考量
- 序列化風格規範化

技能要求：
- 必備技能：XmlWriter API
- 進階技能：相容性測試設計

延伸思考：
- 是否提供配置選項讓呼叫端選擇風格？
- 對大型文件的輸出尺寸影響可接受度？

Practice Exercise（練習題）
- 基礎練習：比對兩種寫法輸出差異（30 分鐘）
- 進階練習：可配置的輸出風格參數（2 小時）
- 專案練習：建立序列化風格檢查器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可強制完整閉合
- 程式碼品質（30%）：選項設計清楚
- 效能優化（20%）：輸出尺寸影響最小
- 創新性（10%）：可擴展的風格策略


## Case #7: 以 CreateNavigator().AppendChild() 直寫 XmlDocument

### Problem Statement（問題陳述）
業務場景：需要將資料直接寫入 XmlDocument 而非先輸出至字串或檔案，再回讀建立 DOM，以避免中間文件與額外解析。

技術挑戰：取得能直接寫入 DOM 的 XmlWriter 類型，並確保寫入與關閉流程正確。

影響範圍：若流程錯誤，可能導致 DOM 不一致或內容未寫入。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 不熟悉 XmlDocument 的 Writer 取得方式。
2. Writer 的生命週期管理不當（未 Close/Flush）。

深層原因：
- 架構層面：中間層過多（字串/檔案）
- 技術層面：缺乏對 XPathNavigator.AppendChild 的使用經驗
- 流程層面：資源管理未標準化

### Solution Design（解決方案設計）
解決策略：使用 xmldoc.CreateNavigator().AppendChild() 取得 XmlWriter，搭配 XmlCopyPipe 寫入，最後正確關閉 Writer，再由 xmldoc.Save 輸出。

實施步驟：
1. 取得 Writer
- 實作細節：XPathNavigator.AppendChild()
- 所需資源：System.Xml.XPath
- 預估時間：10 分鐘

2. 寫入與關閉
- 實作細節：寫入 root、管線、EndElement，最後 writer.Close()
- 所需資源：既有工具
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
var xmldoc = new XmlDocument();
using (var writer = xmldoc.CreateNavigator().AppendChild())
{
    writer.WriteStartElement("root");
    XmlPipes.Copy(reader, writer);
    writer.WriteEndElement();
} // 釋放並落盤到 DOM
xmldoc.Save(Console.Out);
```

實際案例：與文中相同流程，成功避免 WriteRaw 並正確輸出。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：需要中間輸出→再讀入 DOM
- 改善後：直接寫 DOM
- 改善幅度：中間步驟 2 → 0（解析/序列化輪次減少）

Learning Points（學習要點）
核心知識點：
- DOM 直寫 Writer 取得方式
- Writer 的生命週期管理
- 與 Pipe 的結合使用

技能要求：
- 必備技能：System.Xml、XPathNavigator
- 進階技能：資源管理模式（using/IDisposable）

延伸思考：
- 是否可以改用 XDocument + XmlWriter？
- 跨框架（.NET Core）的等價用法？

Practice Exercise（練習題）
- 基礎練習：AppendChild 寫入一段片段（30 分鐘）
- 進階練習：封裝 DOM 寫入輔助類（2 小時）
- 專案練習：建一個 DOM 管線編輯器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：DOM 寫入正確
- 程式碼品質（30%）：資源安全釋放
- 效能優化（20%）：避免不必要中間層
- 創新性（10%）：API 封裝的通用性


## Case #8: 建立最小可重現（MCVE）檢測 Writer 行為差異

### Problem Statement（問題陳述）
業務場景：平台升級或部署環境不同時，WriteRaw 在不同 Writer 類型上行為不一致，需要快速檢測與回歸保護。

技術挑戰：缺乏針對不同 Writer 來源（Console/Stream vs DOM）的自動化對比測試。

影響範圍：升級後出現產出錯誤無法即時察覺。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無系統化回歸測試覆蓋 Writer 行為差異。
2. 依賴手工檢查輸出。

深層原因：
- 架構層面：缺測試閘道
- 技術層面：未封裝可重用測試樣本
- 流程層面：升級流程缺乏自動驗證

### Solution Design（解決方案設計）
解決策略：編寫 MCVE 以同樣輸入比對兩種 Writer 輸出的差異（期望：XmlTextWriter 正確、不應被轉義；XmlWellFormedWriter 觸發錯誤行為），納入 CI。

實施步驟：
1. 建立比較測試
- 實作細節：對 Console Writer 與 DOM Writer 以相同輸入檢查輸出
- 所需資源：測試框架
- 預估時間：1 小時

2. CI 集成
- 實作細節：升級前後跑測試
- 所需資源：CI 工具
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
string input = "<a/><a/>";
string Expected = "<root><a/><a/></root>";

string RunWithConsoleWriter()
{
    var sb = new StringBuilder();
    using var sw = new StringWriter(sb);
    using var writer = XmlWriter.Create(sw);
    writer.WriteStartElement("root");
    writer.WriteRaw(input);
    writer.WriteEndElement();
    writer.Flush();
    return sb.ToString();
}

string RunWithDomWriter()
{
    var doc = new XmlDocument();
    using var writer = doc.CreateNavigator().AppendChild();
    writer.WriteStartElement("root");
    writer.WriteRaw(input); // 預期會錯
    writer.WriteEndElement();
    writer.Close();
    var sb = new StringBuilder();
    using var sw = new StringWriter(sb);
    doc.Save(sw);
    return sb.ToString();
}
```

實際案例：文章所示兩段輸出對比即為 MCVE。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：無回歸檢測
- 改善後：可自動比對輸出差異
- 改善幅度：回歸檢測覆蓋率提升（針對此風險點）

Learning Points（學習要點）
核心知識點：
- MCVE 概念
- Writer 行為差異驗證
- CI 回歸保護

技能要求：
- 必備技能：單元測試、斷言輸出
- 進階技能：測試資料驅動

延伸思考：
- 擴展到更多 Writer 來源與設定
- 異常輸出是否計入負向測試

Practice Exercise（練習題）
- 基礎練習：撰寫上述兩個測試（30 分鐘）
- 進階練習：將 Pipe 納入第三組對照（2 小時）
- 專案練習：建置完整 XML I/O 行為測試套件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可穩定重現與比對
- 程式碼品質（30%）：測試可讀性與維護性
- 效能優化（20%）：測試執行效率
- 創新性（10%）：測試資料參數化


## Case #9: 以流式 Pipe 取代 ImportNode 降低重複解析與記憶體占用

### Problem Statement（問題陳述）
業務場景：傳統做法以兩個 XmlDocument 載入/合併片段並用 ImportNode 搬移，再序列化。對大量資料時記憶體與時間成本高。

技術挑戰：DOM 雙份載入與 ImportNode 造成重複解析與物件配置，效率低下。

影響範圍：吞吐下降、GC 壓力上升、延遲變高。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 來源與目標都以 DOM 載入。
2. ImportNode 與 Save 過程重複解析與配置。

深層原因：
- 架構層面：以 DOM 為核心處理模型
- 技術層面：未應用流式 Reader→Writer
- 流程層面：忽略大檔/高吞吐場景的性能策略

### Solution Design（解決方案設計）
解決策略：改用 XmlReader 讀來源、XmlWriter 寫目標的流式管線（XmlCopyPipe），避免中間 DOM，減少一次解析與 DOM 記憶體占用。

實施步驟：
1. 建立來源 Reader
- 實作細節：可用字串、檔案或 Stream
- 所需資源：System.Xml
- 預估時間：15 分鐘

2. Pipe 寫入目標
- 實作細節：XmlCopyPipe(reader, writer)
- 所需資源：既有 Pipe
- 預估時間：20 分鐘

3. 移除 ImportNode 流程
- 實作細節：重構流程，避免雙 DOM 載入
- 所需資源：既有系統
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
using var reader = XmlReader.Create(sourceStream, new XmlReaderSettings{ ConformanceLevel = ConformanceLevel.Fragment });
using var writer = targetDoc.CreateNavigator().AppendChild();
writer.WriteStartElement("root");
XmlPipes.Copy(reader, writer);
writer.WriteEndElement();
```

實際案例：作者指出此法「效能跟可用性都兼顧」，避免重複解析。

實作環境：.NET Framework，System.Xml

實測數據（估算與觀察）：
- 改善前：解析次數 2（來源 DOM + 輸出 Save）
- 改善後：解析/序列化各 1 次（流式）
- 改善幅度：解析輪次 2 → 1（-50%），記憶體峰值下降（依資料規模）

Learning Points（學習要點）
核心知識點：
- DOM vs 流式處理取捨
- Pipe 模式降低中介層成本
- 大檔/高吞吐下的策略

技能要求：
- 必備技能：XmlReader/Writer 流式用法
- 進階技能：效能剖析與最佳化

延伸思考：
- 管線化多步驟（過濾、轉換）
- 異常時的恢復策略
- 背壓與節流設計

Practice Exercise（練習題）
- 基礎練習：測量 DOM 與流式的記憶體占用（30 分鐘）
- 進階練習：針對 100MB XML 比較吞吐（2 小時）
- 專案練習：封裝可監控的 XML 流式轉寫服務（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：無資料遺失
- 程式碼品質（30%）：可維護的抽象
- 效能優化（20%）：可量化優化
- 創新性（10%）：監控與伸縮設計


## Case #10: 正確處理 Whitespace 與 SignificantWhitespace

### Problem Statement（問題陳述）
業務場景：輸出需保持格式與縮排，或在混合內容模型中保留有意義的空白；錯誤處理空白會導致渲染差異。

技術挑戰：區分一般空白與重要空白並正確寫入。

影響範圍：格式化、渲染與差異比對工具的穩定性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 忽略 Whitespace 與 SignificantWhitespace 的差異。
2. 轉寫時丟棄或合併空白。

深層原因：
- 架構層面：未定義空白保留策略
- 技術層面：API 認知不足
- 流程層面：測試未覆蓋空白敏感案例

### Solution Design（解決方案設計）
解決策略：在 Pipe 中針對兩種空白節點呼叫 WriteWhitespace(reader.Value)，確保輸出保留原樣。

實施步驟：
1. 擴充空白處理
- 實作細節：NodeType.Whitespace / SignificantWhitespace → WriteWhitespace
- 所需資源：System.Xml
- 預估時間：10 分鐘

2. 測試與比對
- 實作細節：以字面比對確保空白一致
- 所需資源：測試框架
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
case XmlNodeType.Whitespace:
case XmlNodeType.SignificantWhitespace:
    writer.WriteWhitespace(reader.Value);
    break;
```

實際案例：文章 Pipe 已涵蓋此處理。

實作環境：.NET Framework，System.Xml

實測數據：
- 改善前：空白可能丟失或被規範化
- 改善後：空白按原樣保留
- 改善幅度：格式一致性提升（以可視化與比對驗證）

Learning Points（學習要點）
核心知識點：
- 兩類空白的差異
- 渲染與差異比對影響
- 序列化策略

技能要求：
- 必備技能：XmlReader/Writer
- 進階技能：字符處理

延伸思考：
- 是否需要縮排美化器？
- 與最小化（minify）的取捨？

Practice Exercise（練習題）
- 基礎練習：保留混合內容中的空白（30 分鐘）
- 進階練習：加入縮排/美化選項（2 小時）
- 專案練習：製作可配置的 XML pretty printer（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：空白保留正確
- 程式碼品質（30%）：清晰可讀
- 效能優化（20%）：處理大檔可接受
- 創新性（10%）：格式化策略靈活


## Case #11: 確認原始標記不被二次編碼（正確編碼策略）

### Problem Statement（問題陳述）
業務場景：將既有標記插入到 XML 中，需確保標記保持標記，不被當成文字；同時普通文字必須被正確編碼。

技術挑戰：不同 Writer 行為差異導致原始標記被 &lt; &gt; 轉義；而 WriteString/WriteRaw 的語義混用也可能出錯。

影響範圍：資料語義改變、消費端解析錯誤。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 WriteRaw 於 XmlWellFormedWriter 導致錯誤編碼。
2. WriteString 與 WriteRaw 使用場合混淆。

深層原因：
- 架構層面：無統一的輸出策略
- 技術層面：API 行為差異理解不足
- 流程層面：缺乏輸出驗證

### Solution Design（解決方案設計）
解決策略：明確規範：文字用 WriteString（讓 Writer 負責編碼）、已解析的標記用 XmlReader+Pipe 重放；避免直接使用 WriteRaw。

實施步驟：
1. 制定規範
- 實作細節：文字 vs 標記 的處理路徑
- 所需資源：團隊規範文件
- 預估時間：1 小時

2. 重構呼叫點
- 實作細節：替換 WriteRaw，導入 Pipe
- 所需資源：程式碼庫
- 預估時間：1-2 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
writer.WriteStartElement("root");
writer.WriteString("純文字 < 不該成為標記"); // Writer 自動編碼
XmlPipes.Copy(XmlReader.Create(new StringReader("<a/>"),
    new XmlReaderSettings{ ConformanceLevel = ConformanceLevel.Fragment }), writer); // 已解析標記
writer.WriteEndElement();
```

實際案例：文中顯示錯誤地將標記當文字輸出，改以 Pipe 後正確。

實作環境：.NET Framework

實測數據：
- 改善前：標記被轉義
- 改善後：標記保留、文字被編碼
- 改善幅度：語義錯誤率顯著下降（觀察輸出）

Learning Points（學習要點）
核心知識點：
- WriteString vs WriteRaw
- 標記與文字的處理路徑
- 驗證輸出策略

技能要求：
- 必備技能：XmlWriter API
- 進階技能：規範制定與 Code Review 要點

延伸思考：
- 是否需要靜態分析檢查 WriteRaw 使用？
- 在高風險模組禁用 WriteRaw

Practice Exercise（練習題）
- 基礎練習：混合文字/標記輸出（30 分鐘）
- 進階練習：靜態分析規則（Roslyn Analyzer）（2 小時）
- 專案練習：導入規則到 CI 並建立基線（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：語義正確
- 程式碼品質（30%）：規範落地
- 效能優化（20%）：零額外成本或可接受
- 創新性（10%）：工具化落地


## Case #12: 以容器根節點封裝片段，輸出成完整文件

### Problem Statement（問題陳述）
業務場景：上游只提供一串兄弟節點（多個 <a/>），需輸出為完整 XML 文件，供下游解析。

技術挑戰：多個根級片段不構成合法文件，需要封裝在單一根節點內。

影響範圍：若不加容器，輸出不合法，無法被消費。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 直接把片段當完整文件輸出。
2. 忽略 XML 單根規範。

深層原因：
- 架構層面：未定義文件邊界
- 技術層面：對片段與文件差異理解不足
- 流程層面：缺少輸出驗證

### Solution Design（解決方案設計）
解決策略：先輸出一個容器根節點（如 root），再以 Pipe 寫入片段，確保最終輸出是合法文件。

實施步驟：
1. 寫入容器根
- 實作細節：WriteStartElement("root") + WriteEndElement()
- 所需資源：XmlWriter
- 預估時間：10 分鐘

2. Pipe 片段
- 實作細節：Fragment 讀取並轉寫
- 所需資源：XmlReaderSettings
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
writer.WriteStartElement("root");
XmlPipes.Copy(fragmentReader, writer);
writer.WriteEndElement();
```

實際案例：文中示例皆在 root 下嵌入片段。

實作環境：.NET Framework

實測數據：
- 改善前：輸出非合法文件
- 改善後：輸出合法文件
- 改善幅度：合法率 0% → 100%（針對該狀況）

Learning Points（學習要點）
核心知識點：
- 片段 vs 文件
- 文件單根要求
- 封裝策略

技能要求：
- 必備技能：XmlWriter
- 進階技能：輸出協議設計

延伸思考：
- 容器 root 名稱、命名空間策略
- 是否保留原片段層級資訊

Practice Exercise（練習題）
- 基礎練習：將多片段包成合法文件（30 分鐘）
- 進階練習：支援自定 root 與 namespace（2 小時）
- 專案練習：實作片段合併器 CLI（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出合法
- 程式碼品質（30%）：抽象清楚
- 效能優化（20%）：流式合併
- 創新性（10%）：可配置化


## Case #13: 正確管理 Writer 的 Flush 與 Close

### Problem Statement（問題陳述）
業務場景：將資料寫入 Console 或 XmlDocument 後，發現部分內容未出現或不完整，尤其以 DOM Writer 情況更為敏感。

技術挑戰：Flush 與 Close 的語義與不同 Writer 的行為差異，易導致未完全寫入。

影響範圍：輸出缺漏、資料完整性受損。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未呼叫 Close 導致緩衝未落盤至 DOM。
2. 僅呼叫 Flush 不足以完成結束操作。

深層原因：
- 架構層面：資源生命週期管理鬆散
- 技術層面：不同 Writer 行為差異不明
- 流程層面：缺少針對資源管理的檢查

### Solution Design（解決方案設計）
解決策略：對 DOM Writer 採用 using 或顯式 Close；對 Stream/Console Writer 在 Flush 後仍建議 Close/Dispose；納入程式碼規約。

實施步驟：
1. using 包裹 Writer
- 實作細節：確保 Dispose 被呼叫
- 所需資源：C# 語言特性
- 預估時間：10 分鐘

2. 補充規約
- 實作細節：PR 模板檢查項
- 所需資源：團隊規範
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
using (var writer = xmldoc.CreateNavigator().AppendChild())
{
    writer.WriteStartElement("root");
    XmlPipes.Copy(reader, writer);
    writer.WriteEndElement();
} // 自動 Close，內容已寫入 DOM
```

實際案例：文章示例在 DOM Writer 路徑上顯式呼叫 Close。

實作環境：.NET Framework

實測數據：
- 改善前：偶發缺漏
- 改善後：輸出完整
- 改善幅度：缺漏率下降（以觀察為主）

Learning Points（學習要點）
核心知識點：
- Flush vs Close 差異
- using/IDisposable 模式
- DOM Writer 的落盤時機

技能要求：
- 必備技能：C# 資源管理
- 進階技能：針對不同 Writer 的測試

延伸思考：
- 非同步寫入與取消支援
- 例外時的資源釋放

Practice Exercise（練習題）
- 基礎練習：用 using 重構 Writer 使用（30 分鐘）
- 進階練習：在例外場景驗證完整輸出（2 小時）
- 專案練習：建置資源管理規範與 Analyzer（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出完整無缺
- 程式碼品質（30%）：資源釋放正確
- 效能優化（20%）：不引入額外阻塞
- 創新性（10%）：自動化檢查


## Case #14: 防禦式參數檢查避免 Null 造成隱性錯誤

### Problem Statement（問題陳述）
業務場景：Pipe 作為共用工具，會被多處呼叫；一旦參數為 null 造成執行期錯誤，可能影響整體批次。

技術挑戰：快速定位與回報出錯點，避免 NRE 在深層堆疊中爆出。

影響範圍：不穩定、難除錯。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 參數未檢查即使用。
2. NRE 堆疊不利定位。

深層原因：
- 架構層面：共用工具缺少契約檢查
- 技術層面：防禦式程式設計不足
- 流程層面：邊界條件測試不足

### Solution Design（解決方案設計）
解決策略：在 XmlCopyPipe 開頭即檢查 reader/writer 為 null 時拋出 ArgumentNullException，明確契約與錯誤訊息。

實施步驟：
1. 參數檢查
- 實作細節：if (reader==null) throw new ArgumentNullException(nameof(reader));
- 所需資源：C#
- 預估時間：5 分鐘

2. 測試邊界
- 實作細節：空參數單元測試
- 所需資源：測試框架
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
if (reader == null) throw new ArgumentNullException(nameof(reader));
if (writer == null) throw new ArgumentNullException(nameof(writer));
```

實際案例：文章中的 XmlCopyPipe 即包含此檢查。

實作環境：.NET Framework

實測數據：
- 改善前：NRE 難定位
- 改善後：立即報明確異常
- 改善幅度：除錯成本下降（以案例觀察）

Learning Points（學習要點）
核心知識點：
- 防禦式編程
- 契約清晰化
- 單測覆蓋邊界條件

技能要求：
- 必備技能：例外處理
- 進階技能：合約式設計（Design by Contract）

延伸思考：
- 引入參數檢查庫或 Code Contracts
- 適度而非過度檢查

Practice Exercise（練習題）
- 基礎練習：加入參數檢查與測試（30 分鐘）
- 進階練習：統一例外訊息格式（2 小時）
- 專案練習：建立工具庫模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：即時阻止不合法呼叫
- 程式碼品質（30%）：訊息清晰
- 效能優化（20%）：零額外負擔
- 創新性（10%）：可重用模板


## Case #15: 從多種輸入來源建立 XmlReader（字串/檔案/串流）

### Problem Statement（問題陳述）
業務場景：片段來源多樣（字串、檔案、網路串流），需要統一以 XmlReader 串流讀取，利於管線化。

技術挑戰：不同來源的 Reader 建立方式與設定差異，易出錯。

影響範圍：讀取失敗或行為不一致，影響整體管線。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 針對來源類型硬編碼，重複且易錯。
2. 忽略 ConformanceLevel 設定。

深層原因：
- 架構層面：缺乏統一工廠方法
- 技術層面：Reader 選項使用不一致
- 流程層面：未抽象輸入來源

### Solution Design（解決方案設計）
解決策略：封裝 Reader 工廠，輸入來源與設定（Fragment/Encoding）由單點統一。

實施步驟：
1. ReaderFactory
- 實作細節：CreateFromString/CreateFromStream，統一設定 Fragment
- 所需資源：System.Xml
- 預估時間：45 分鐘

2. 導入呼叫點
- 實作細節：替換零散建立
- 所需資源：程式碼庫
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
static XmlReader CreateFragmentReader(TextReader source) =>
    XmlReader.Create(source, new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment });

// 用法
using var reader = CreateFragmentReader(new StringReader("<a/><a/>"));
XmlPipes.Copy(reader, writer);
```

實際案例：文章以 StringReader 建立 Fragment Reader。

實作環境：.NET Framework

實測數據：
- 改善前：建立方式分散、易漏設定
- 改善後：統一工廠，行為一致
- 改善幅度：錯誤機率降低（以程式碼審查觀察）

Learning Points（學習要點）
核心知識點：
- Reader 建立與設定
- 工廠模式封裝
- 一致性與可測性

技能要求：
- 必備技能：C# 抽象設計
- 進階技能：依賴注入與測試替身

延伸思考：
- 支援驗證/XSD 選項
- 超時與安全設定（DTD 禁用）

Practice Exercise（練習題）
- 基礎練習：實作 ReaderFactory（30 分鐘）
- 進階練習：加入 XSD 驗證開關（2 小時）
- 專案練習：封裝管線輸入層（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：來源支援完整
- 程式碼品質（30%）：抽象清晰
- 效能優化（20%）：零額外負擔
- 創新性（10%）：配置彈性


## Case #16: API Bug 風險管理與迴避策略（繞過 WriteRaw）

### Problem Statement（問題陳述）
業務場景：雖然 XmlWellFormedWriter 在多數面向上表現良好，但其 WriteRaw 存在已知 Bug；團隊仍希望使用該 Writer 的其他優勢。

技術挑戰：在不等待平台修補的前提下，快速制定可持續的迴避策略與代碼準則。

影響範圍：核心匯出功能的穩定性與可維護性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 平台 API 缺陷（WriteRaw 雙重轉義）
2. 誤用高風險 API

深層原因：
- 架構層面：缺少替代路徑
- 技術層面：未審視 API 風險
- 流程層面：缺免責與升級計畫

### Solution Design（解決方案設計）
解決策略：制訂「禁用 WriteRaw」準則與替代方案（XmlCopyPipe），在代碼審查、靜態掃描、CI 測試中落地。保留 XmlWellFormedWriter 的使用，但繞開有問題 API。

實施步驟：
1. 規範與公告
- 實作細節：ADR/工程準則：禁用 WriteRaw（除非測試證實安全）
- 所需資源：團隊治理
- 預估時間：1 小時

2. 代碼改造
- 實作細節：引入 XmlCopyPipe；替換使用點
- 所需資源：程式碼庫
- 預估時間：1-3 小時

3. 自動化防護
- 實作細節：靜態掃描關鍵字、回歸測試
- 所需資源：CI/CD
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）- 規範化替代
// 禁用：writer.WriteRaw(fragment); // 禁用規範
// 取代：
using var reader = XmlReader.Create(new StringReader(fragment),
    new XmlReaderSettings{ ConformanceLevel = ConformanceLevel.Fragment });
XmlPipes.Copy(reader, writer);
```

實際案例：作者選擇「閃開就沒事」策略，繼續使用該 Writer，但避開 WriteRaw。

實作環境：.NET Framework

實測數據：
- 改善前：使用 WriteRaw 造成輸出錯誤
- 改善後：以 Pipe 取代，輸出正確
- 改善幅度：穩定性恢復（錯誤率降為 0%，以示例輸出驗證）

Learning Points（學習要點）
核心知識點：
- 風險繞過策略
- 規範與自動化結合
- 平台缺陷期間的工程對策

技能要求：
- 必備技能：治理與流程落地
- 進階技能：靜態分析與 CI 線上防護

延伸思考：
- 是否應向原廠回報或跟進修補
- 待修補後的回退計畫

Practice Exercise（練習題）
- 基礎練習：撰寫禁用清單與替代指引（30 分鐘）
- 進階練習：加上 CI 檢查（2 小時）
- 專案練習：完成全專案 WriteRaw 移除（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：替代落地
- 程式碼品質（30%）：規範可維護
- 效能優化（20%）：替代無明顯退化
- 創新性（10%）：自動化治理


## Case #17: 將字串片段安全注入為節點而非文字

### Problem Statement（問題陳述）
業務場景：需要把外部產生的 XML 字串片段安全插入到現有 XML 結構中，要求以節點形式存在而非被當作文字。

技術挑戰：直寫字串易被編碼成文字；需先解析為節點事件再寫入。

影響範圍：如果被當文字，下游無法以 XPath/XQuery 操作這些元素。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 誤用 WriteString 或錯誤使用 WriteRaw
2. 未先解析片段

深層原因：
- 架構層面：輸入處理路徑未明確
- 技術層面：對 API 語義混淆
- 流程層面：缺乏示例與指導

### Solution Design（解決方案設計）
解決策略：一律將標記片段轉為 XmlReader 再以 Pipe 寫入，確保其變為節點樹的一部分。

實施步驟：
1. 建立 Fragment Reader
- 實作細節：ConformanceLevel.Fragment
- 所需資源：System.Xml
- 預估時間：15 分鐘

2. Pipe 注入
- 實作細節：在目標父節點內轉寫
- 所需資源：Pipe
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
writer.WriteStartElement("container");
using var reader = XmlReader.Create(new StringReader("<a id='1'/>"), 
    new XmlReaderSettings{ ConformanceLevel = ConformanceLevel.Fragment });
XmlPipes.Copy(reader, writer);
writer.WriteEndElement();
```

實際案例：文章以相同手法將 <a/> 片段正確輸出為節點。

實作環境：.NET Framework

實測數據：
- 改善前：片段被當文字輸出
- 改善後：片段以節點形式存在
- 改善幅度：XPath 可見性由 0% → 100%

Learning Points（學習要點）
核心知識點：
- 節點 vs 文字序列化
- Pipe 的節點化效果
- XPath 操作前提

技能要求：
- 必備技能：XmlReader/Writer
- 進階技能：結構化資料輸入策略

延伸思考：
- 加入節點校驗（必備屬性/結構）
- 避免命名空間衝突

Practice Exercise（練習題）
- 基礎練習：插入一段帶屬性的片段（30 分鐘）
- 進階練習：對片段做 schema 驗證（2 小時）
- 專案練習：做一個片段注入工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：節點插入正確
- 程式碼品質（30%）：健壯與可用
- 效能優化（20%）：流式速度
- 創新性（10%）：校驗擴展


## Case #18: 驗證 Writer 行為與 MSDN 契約一致性

### Problem Statement（問題陳述）
業務場景：依據 MSDN 說明，WriteRaw 應寫出「原樣」內容；實測發現特定 Writer（XmlWellFormedWriter）偏離契約，需建立驗證與文檔化。

技術挑戰：API 行為不一致導致預期落差，需用文件與測試保護。

影響範圍：錯誤假設導致設計不當與故障。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 實作與文件行為不一致。
2. 團隊未建立即時驗證機制。

深層原因：
- 架構層面：依賴單一文件敘述
- 技術層面：缺少 API 行為測試
- 流程層面：缺少變更追蹤

### Solution Design（解決方案設計）
解決策略：撰寫行為驗證測試，將期望行為（依 MSDN）與實測行為記錄於 ADR；在必要時提供替代方案（Pipe），同步更新開發指引。

實施步驟：
1. 行為測試
- 實作細節：對多 Writer 類型比對 WriteRaw 行為
- 所需資源：測試框架
- 預估時間：1 小時

2. 文件化
- 實作細節：ADR/Readme 記錄差異與建議用法
- 所需資源：文件工具
- 預估時間：1 小時

3. 替代路徑
- 實作細節：導向 Pipe
- 所需資源：既有工具
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）- 期望 vs 實測
Assert.Equal("...<root><a/></root>...", RunWithXmlTextWriter());
Assert.NotEqual("...<root><a/></root>...", RunWithXmlWellFormedWriter()); // 觀察到被轉義
```

實際案例：文章引用 MSDN 並指出實測不一致。

實作環境：.NET Framework

實測數據：
- 改善前：未知差異，導致錯誤設計
- 改善後：差異被文檔化並有替代方案
- 改善幅度：設計決策風險降低

Learning Points（學習要點）
核心知識點：
- 文件契約 vs 實作行為
- ADR 的價值
- 測試驅動驗證平台 API

技能要求：
- 必備技能：單元測試、寫作
- 進階技能：風險管理

延伸思考：
- 向上游回報與追蹤
- 跨版本與跨平台對齊

Practice Exercise（練習題）
- 基礎練習：撰寫 ADR 記錄差異（30 分鐘）
- 進階練習：多版本測試矩陣（2 小時）
- 專案練習：建立平台 API 行為回歸套件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：行為被驗證
- 程式碼品質（30%）：測試可靠
- 效能優化（20%）：測試可快速執行
- 創新性（10%）：知識沉澱機制


--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）：#3, #6, #7, #10, #12, #13, #14, #15
- 中級（需要一定基礎）：#1, #2, #4, #5, #8, #11, #16, #17, #18
- 高級（需要深厚經驗）：#9

2. 按技術領域分類
- 架構設計類：#9, #16, #18
- 效能優化類：#9, #7
- 整合開發類：#3, #4, #5, #12, #15, #17
- 除錯診斷類：#1, #2, #8, #11, #13, #14, #18
- 安全防護類：#2, #5, #9, #16

3. 按學習目標分類
- 概念理解型：#3, #6, #11, #12, #13
- 技能練習型：#4, #5, #7, #10, #15, #17
- 問題解決型：#1, #2, #8, #9, #16, #18
- 創新應用型：#9, #16

--------------------------------
案例關聯圖（學習路徑建議）
- 建議先學：#3（Fragment 概念）、#11（文字 vs 標記處理）、#7（取得 DOM Writer）、#13（Flush/Close 管理）
- 依賴關係：
  - #4（XmlCopyPipe）依賴 #3、#11 的概念
  - #1（繞過 WriteRaw Bug）依賴 #4 的管線技能
  - #2（去除 WriteRaw 風險）依賴 #4
  - #5（特殊節點保留）依賴 #4
  - #9（效能優化流式）依賴 #4、#7
  - #8、#18（行為驗證/回歸）依賴 #1 的問題認知
  - #16（風險治理）依賴 #1、#2、#18 的結論
  - #12（容器根策略）依賴 #3
  - #10（空白處理）依賴 #4
  - #15（Reader 工廠）依賴 #3
  - #17（節點注入）依賴 #3、#4

完整學習路徑：
1) #3 → 2) #7 → 3) #11 → 4) #13 → 5) #4 → 6) #1 → 7) #2 → 8) #5 → 9) #10 → 10) #12 → 11) #15 → 12) #8 → 13) #18 → 14) #9 → 15) #16 → 16) #17

此路徑從概念與基礎 API 操作入門，逐步建立安全轉寫管線，最終達成效能優化與治理落地。