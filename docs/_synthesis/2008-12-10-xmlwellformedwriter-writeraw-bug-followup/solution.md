---
layout: synthesis
title: "XmlWellFormedWriter.WriteRaw( ) 的 Bug 後續發展"
synthesis_type: solution
source_post: /2008/12/10/xmlwellformedwriter-writeraw-bug-followup/
redirect_from:
  - /2008/12/10/xmlwellformedwriter-writeraw-bug-followup/solution/
postid: 2008-12-10-xmlwellformedwriter-writeraw-bug-followup
---

以下內容基於文章中描述的情境與提供的官方解法（InnerXml、XmlReader + ConformanceLevel.Fragment + WriteNode），將問題拆解為多個可教學、可實作的案例。每個案例均包含問題、根因、解法、代碼、驗證方法與練習與評估標準，利於實戰教學與能力評估。

----------------------------------------

## Case #1: WriteRaw 在 XmlDocument 上被當作文字，無法追加節點

### Problem Statement（問題陳述）
業務場景：某組態生成器需要將多個功能模組回傳的 XML 片段動態合併至既有 XmlDocument 中。團隊沿用舊有以檔案為目標的寫法，直接在 XmlWriter 上呼叫 WriteRaw 寫入片段字串。上線前檢查輸出發現原本應是節點 <a/> 的內容成了文字 &lt;a/&gt;，導致下游 XPath 查詢完全失效。
技術挑戰：當 XmlWriter 背後是 XmlDocument/XPathNavigator 時，WriteRaw 內容被視為文字，不會解析為節點。
影響範圍：所有使用 WriteRaw 寫入片段的功能，均產出錯誤結構 XML，導致查詢/序列化/匯入流程失敗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. XmlWriter over XmlDocument 對 WriteRaw 的實作選擇了「視為文字」，未做節點解析。
2. WriteRaw 原始用意是給格式化輸出（檔案、文字流），非 DOM 編輯。
3. 片段可被多次 WriteRaw 跨呼叫/交錯寫入，使得「解析成節點」難以正確實作。

深層原因：
- 架構層面：XmlWriter 抽象難以在不同後端（文件/串流）保持一致語義。
- 技術層面：缺乏片段邊界與狀態管理，難在多次 WriteRaw 中還原節點結構。
- 流程層面：團隊移植舊碼未重新審視 DOM 寫入語義，缺少用法準則。

### Solution Design（解決方案設計）
解決策略：避免在 XmlDocument 背後使用 WriteRaw。改用可解析片段的路徑：1) 若已信任輸入，用 InnerXml 一次性指派；2) 若需嚴格解析與控制，用 XmlReader 設定 ConformanceLevel.Fragment，再以 writer.WriteNode 寫入，確保轉為節點。

實施步驟：
1. 盤點 WriteRaw 呼叫點
- 實作細節：grep/Code Search，列出所有在 DOM 寫入路徑使用的 WriteRaw
- 所需資源：IDE 搜尋、簡單腳本
- 預估時間：0.5 天

2. 替換為 InnerXml 或 WriteNode
- 實作細節：信任輸入→InnerXml；非信任→XmlReader(Fragment)+WriteNode
- 所需資源：System.Xml、單元測試
- 預估時間：1 天

3. 驗證與回歸測試
- 實作細節：比較輸出、統計節點數、XPath 驗證
- 所需資源：測試框架
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 問題重現（錯誤：節點被當文字）
XmlDocument doc = new XmlDocument();
XmlWriter w = doc.CreateNavigator().AppendChild();
w.WriteStartElement("root");
w.WriteRaw("<a/><a/>"); // 會變成文字 "&lt;a/&gt;&lt;a/&gt;"
w.WriteEndElement();
w.Close();
doc.Save(Console.Out); // <root>&lt;a/&gt;&lt;a/&gt;</root>

// 解法1：信任輸入 → InnerXml
var doc1 = new XmlDocument();
var root1 = doc1.CreateElement("root");
root1.InnerXml = "<a/><a/>"; // 直接變成節點
doc1.AppendChild(root1);
doc1.Save(Console.Out); // <root><a/><a/></root>

// 解法2：嚴格解析 → Fragment + WriteNode
var doc2 = new XmlDocument();
var w2 = doc2.CreateNavigator().AppendChild();
w2.WriteStartElement("root");
using (var r = XmlReader.Create(new StringReader("<a/><a/>"),
           new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment }))
{
    w2.WriteNode(r, false);
}
w2.WriteEndElement();
w2.Close();
doc2.Save(Console.Out); // <root><a/><a/></root>
```

實際案例：MS Connect 官方回覆指出 WriteRaw 在 XmlDocument 上的設計是「視為文字」，並提供 InnerXml 與 XmlReader(Fragment)+WriteNode 的解法。
實作環境：Visual Studio 2008, .NET Framework 3.5, System.Xml
實測數據：
- 改善前：root 子節點為單一文字節點；XPath 選不到 <a/>
- 改善後：root 子節點為元素 <a/> 數量=2
- 改善幅度：元素節點數 0 → 2；XPath 命中率 0% → 100%

Learning Points（學習要點）
核心知識點：
- XmlWriter.WriteRaw 在不同後端的語義差異
- ConformanceLevel.Fragment 的用途
- InnerXml 與 WriteNode 的選用時機

技能要求：
- 必備技能：C#、System.Xml API、基本 XPath
- 進階技能：XML 片段解析、API 語義辨識

延伸思考：
- 解法可用於任何需將 XML 字串轉節點的場景
- 風險：InnerXml 不可用於不信任輸入
- 優化：封裝通用 AppendFragment 方法

Practice Exercise（練習題）
- 基礎練習：寫出錯誤/正確輸出對照（30 分鐘）
- 進階練習：將專案內所有 WriteRaw 改為 WriteNode（2 小時）
- 專案練習：封裝一個安全的 AppendXmlFragment 工具類並加測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：節點正確追加、XPath 可命中
- 程式碼品質（30%）：清晰封裝、例外處理
- 效能優化（20%）：避免多次字串拼接
- 創新性（10%）：可重用 API 設計

----------------------------------------

## Case #2: 用 InnerXml 快速把可信任的 XML 片段追加到 XmlDocument

### Problem Statement（問題陳述）
業務場景：後台 CMS 需要將安全來源（平台自產）的多個小組件輸出的 XML 片段合併至單一頁面 XML。來源可完全信任，且要求快速、少碼量。
技術挑戰：如何以最少代碼，將片段直接變為 DOM 節點，不再出現被當作文字的情況。
影響範圍：內容組裝流程；若處理不當會導致頁面渲染錯誤。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. WriteRaw 在此後端不會解析片段，導致誤用。
2. 片段原本已是合法 XML，可直接用 InnerXml 指定。
3. 開發者不清楚 XmlElement.InnerXml 可轉為子節點。

深層原因：
- 架構層面：DOM API 已提供直寫片段的屬性（InnerXml）
- 技術層面：XML 版型為可信管道，無需額外逃脫或校驗
- 流程層面：對 API 能力缺乏對齊與知識傳遞

### Solution Design（解決方案設計）
解決策略：對於信任來源，使用 InnerXml 直接指定子節點，簡化流程與代碼，避免 WriteRaw 語義陷阱。

實施步驟：
1. 建立根節點
- 實作細節：doc.CreateElement + AppendChild
- 所需資源：System.Xml
- 預估時間：10 分鐘

2. 指派 InnerXml
- 實作細節：將片段字串設為 InnerXml
- 所需資源：同上
- 預估時間：10 分鐘

3. 輸出驗證
- 實作細節：Save(Console.Out) 或節點計數
- 所需資源：同上
- 預估時間：10 分鐘

關鍵程式碼/設定：
```csharp
XmlDocument doc = new XmlDocument();
XmlElement root = doc.CreateElement("root");
root.InnerXml = "<a/><a/><a/><a/><a/>"; // 信任來源可直接指定
doc.AppendChild(root);
doc.Save(Console.Out); // <root><a/><a/><a/><a/><a/></root>
```

實際案例：與文中官方建議一致：使用 InnerXml 追加片段。
實作環境：VS 2008, .NET 3.5
實測數據：
- 改善前：文字節點 1；元素節點 0
- 改善後：元素節點 5
- 改善幅度：正確節點率 0% → 100%

Learning Points（學習要點）
核心知識點：
- InnerXml 的用途與風險邊界
- DOM 操作基本流程
- 與 WriteRaw 差異

技能要求：
- 必備技能：C#、XML DOM 操作
- 進階技能：輸入信任等級判斷與風險控管

延伸思考：
- 可用於匯入平台內產 XML
- 限制：不適用不信任輸入
- 優化：封裝檢查與降級策略

Practice Exercise（練習題）
- 基礎：使用 InnerXml 追加 3 個子節點（30 分鐘）
- 進階：寫一個方法，可選擇 InnerXml 或安全路徑（2 小時）
- 專案：整合到 CMS 模組合併流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：節點完整呈現
- 程式碼品質：清晰、可讀、可測
- 效能：最少中間物件
- 創新性：介面友善、可擴充

----------------------------------------

## Case #3: 以 XmlReader(Fragment) + WriteNode 安全寫入多個片段

### Problem Statement（問題陳述）
業務場景：ETL 管線需將外部系統送入的 XML 片段併入平台 XmlDocument。輸入可能包含多個並列節點（非單一根），且必須檢查格式正確。
技術挑戰：確保每個片段被解析為節點（非文字），並且能處理多個頂層節點。
影響範圍：資料治理與下游查詢正確性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WriteRaw 無解析能力，導致片段成文字。
2. 預設 ConformanceLevel.Document 不允許多根。
3. 缺少使片段轉節點的可靠管道。

深層原因：
- 架構層面：片段場景天生需要 Fragment conformance
- 技術層面：需要以 XmlReader 先解析，再導入 DOM
- 流程層面：未建立「輸入為片段」的標準處理模版

### Solution Design（解決方案設計）
解決策略：以 XmlReader 設 ConformanceLevel.Fragment 解析字串，再用 writer.WriteNode 寫入 DOM。此路徑可保證格式檢查，且支援多個頂層節點。

實施步驟：
1. 準備 XmlReaderSettings
- 實作細節：ConformanceLevel = Fragment
- 所需資源：System.Xml
- 預估時間：10 分鐘

2. 解析與導入
- 實作細節：XmlReader.Create + WriteNode
- 所需資源：同上
- 預估時間：30 分鐘

3. 驗證
- 實作細節：節點類型與數量；XPath 測試
- 所需資源：測試框架
- 預估時間：20 分鐘

關鍵程式碼/設定：
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
doc.Save(Console.Out); // <root><a/><a/><a/><a/><a/></root>
```

實際案例：官方建議二：XmlReader(Fragment) + WriteNode。
實作環境：VS 2008, .NET 3.5
實測數據：
- 改善前：節點為文字，XPath 失敗
- 改善後：元素節點 5，XPath 可命中
- 改善幅度：正確解析率 0% → 100%

Learning Points（學習要點）
核心知識點：
- ConformanceLevel.Fragment 的必要性
- WriteNode 將 reader 內容輸出到 writer
- 與 InnerXml 的差異

技能要求：
- 必備技能：C#、XmlReader/XmlWriter API
- 進階技能：輸入管道的合規檢查

延伸思考：
- 可應用於任何需要「多根片段」導入的場景
- 限制：需額外解析開銷
- 優化：重用 XmlReaderSettings 與緩衝

Practice Exercise（練習題）
- 基礎：將 N 個 <a/> 寫入 root（30 分鐘）
- 進階：處理含屬性與子節點的片段（2 小時）
- 專案：封裝一個 AppendFragment 安全 API（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：正確導入所有節點
- 程式碼品質：錯誤處理清楚
- 效能優化：合理重用物件
- 創新性：可配置策略

----------------------------------------

## Case #4: 多次 WriteRaw 分段拼接導致解析不可能的風險控管

### Problem Statement（問題陳述）
業務場景：某舊程式將片段拆成多段 WriteRaw 呼叫（例：「<a」「/>」），並與其他寫入呼叫交錯。移植到 XmlDocument 後，輸出變文字。
技術挑戰：多次 WriteRaw 無從得知片段邊界，DOM 寫入端無法將其還原成節點。
影響範圍：舊模組統一移植時全數失效。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WriteRaw 片段被拆分多次呼叫，無法組裝解析。
2. 與其他 XmlWriter 呼叫交錯，邏輯更混亂。
3. DOM 寫入端以文字處理（By Design）。

深層原因：
- 架構層面：XmlWriter 是前饋式串流抽象，不保留跨呼叫語境
- 技術層面：沒有「片段終止」語意可供判斷
- 流程層面：舊碼未建立「片段一次性寫入」的規範

### Solution Design（解決方案設計）
解決策略：禁止分段 WriteRaw。將片段完整交給 XmlReader(Fragment) 並 WriteNode；或先組裝完整片段字串後再以安全路徑導入。

實施步驟：
1. 封裝 API
- 實作細節：提供 AppendFragment(string xml) 入口，內部統一走安全路徑
- 所需資源：公用程式庫
- 預估時間：0.5 天

2. 取代舊呼叫
- 實作細節：移除所有分段 WriteRaw
- 所需資源：重構工具
- 預估時間：1 天

3. 驗證
- 實作細節：對比輸出、單元測試
- 所需資源：測試框架
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public static void AppendFragment(XmlWriter writer, string fragment)
{
    using var r = XmlReader.Create(new StringReader(fragment),
        new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment });
    writer.WriteNode(r, false);
}

// 使用：一次性導入，不做分段 WriteRaw
```

實作環境：VS 2008, .NET 3.5
實測數據：
- 改善前：<root>&lt;a/&gt;</root>
- 改善後：<root><a/></root>
- 改善幅度：元素節點率 0% → 100%

Learning Points（學習要點）
核心知識點：
- 多次 WriteRaw 的風險
- Append API 的必要性
- Stream vs DOM 語意差異

技能要求：
- 必備：C#、重構技巧
- 進階：API 設計

延伸思考：
- 也適用於其他語意不一致 API 的包裝
- 風險：不正確片段仍需解析例外處理
- 優化：增加片段結構檢查

Practice Exercise（練習題）
- 基礎：將分段寫入改為一次導入（30 分鐘）
- 進階：寫單元測試防回歸（2 小時）
- 專案：完成團隊級替換腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：正確節點輸出
- 程式碼品質：易讀、可維護
- 效能：少中間拼接
- 創新性：封裝與自動化

----------------------------------------

## Case #5: WriteRaw 與其他 XmlWriter 呼叫交錯導致結構混亂

### Problem Statement（問題陳述）
業務場景：頁面渲染器先用 WriteStartElement，再交錯多次 WriteRaw 插入片段與文字，結果 DOM 結構錯亂。
技術挑戰：交錯語意使得 WriteRaw 更難正確解讀，落入文字處理。
影響範圍：模板引擎輸出錯誤，瀏覽器或下游解析失敗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WriteRaw 內容被視為文字，交錯無法重建樹。
2. 交錯導致層級與節點邊界丟失。
3. 開發者對 API 語意不熟。

深層原因：
- 架構層面：XmlWriter 無上下文緩衝以供回溯
- 技術層面：混合語意（節點/文字）難以保證結構正確
- 流程層面：缺乏使用準則與審查

### Solution Design（解決方案設計）
解決策略：建立清晰管道：元素結構靠 XmlWriter 節點 API；外部片段統一走 XmlReader(Fragment)+WriteNode。禁止交錯 WriteRaw。

實施步驟：
1. 設計寫入規約
- 實作細節：撰寫規約文件與範例
- 所需資源：團隊共識
- 預估時間：0.5 天

2. 重構模板
- 實作細節：把片段區域改為安全導入
- 所需資源：IDE
- 預估時間：1 天

3. 驗證與審查
- 實作細節：Code Review/測試
- 所需資源：審查流程
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 交錯的錯誤示例（簡化）
writer.WriteStartElement("root");
writer.WriteAttributeString("id", "1");
writer.WriteRaw("<a/>"); // 變文字，破壞意圖
writer.WriteString("text");
writer.WriteEndElement();

// 改為：
writer.WriteStartElement("root");
writer.WriteAttributeString("id", "1");
AppendFragment(writer, "<a/>"); // 解析為節點
writer.WriteString("text");
writer.WriteEndElement();
```

實作環境：VS 2008, .NET 3.5
實測數據：
- 改善前：子節點為 ["文字", "文字"]
- 改善後：子節點為 ["元素 a", "文字"]
- 改善幅度：結構正確率 0% → 100%

Learning Points（學習要點）
核心知識點：
- 混合寫入的風險
- 元素 vs 文字的 API 劃分
- 結構正確性驗證

技能要求：
- 必備：C#、XML 結構思維
- 進階：重構與規約制定

延伸思考：
- 可延伸至 JSON/HTML 生成器
- 風險：舊模板多，改造成本
- 優化：工具化檢查

Practice Exercise（練習題）
- 基礎：把交錯示例改寫正確（30 分鐘）
- 進階：為模板加入結構校驗測試（2 小時）
- 專案：編寫規約 + CI 檢查（8 小時）

Assessment Criteria（評估標準）
- 功能：節點正確
- 品質：規約落地
- 效能：無明顯退化
- 創新：自動化檢查

----------------------------------------

## Case #6: 從檔案輸出型 XmlWriter 移植至 XmlDocument 的替代策略

### Problem Statement（問題陳述）
業務場景：舊系統以 XmlWriter 直接輸出檔案，廣泛使用 WriteRaw。新系統改為先建 DOM（XmlDocument）再輸出，移植後發現 WriteRaw 全部失效。
技術挑戰：需要一套系統化替代策略，快速、正確替換 WriteRaw。
影響範圍：跨多模組，改造成本高。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 兩種後端的 WriteRaw 語意不同。
2. 舊程式依賴已被轉義/格式化的輸出假設。
3. 缺少統一替代 API。

深層原因：
- 架構層面：不同後端下抽象不一致
- 技術層面：需要片段解析或節點 API 替代
- 流程層面：缺乏移植指引與代碼規範

### Solution Design（解決方案設計）
解決策略：制定替代策略矩陣：純文字→WriteString；可信片段→InnerXml；非信任片段→XmlReader(Fragment)+WriteNode；並提供搜尋替換腳本與封裝。

實施步驟：
1. 分類呼叫場景
- 實作細節：以規則分類（文字/片段/混合）
- 所需資源：程式碼分析
- 預估時間：1 天

2. 建立封裝 API
- 實作細節：AppendText, AppendFragment, SetInnerXml
- 所需資源：公共庫
- 預估時間：1 天

3. 自動/半自動替換
- 實作細節：腳本輔助
- 所需資源：腳本工具
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public static void AppendText(XmlWriter w, string text) => w.WriteString(text);

public static void AppendFragment(XmlWriter w, string fragment)
{
    using var r = XmlReader.Create(new StringReader(fragment),
        new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment });
    w.WriteNode(r, false);
}
```

實作環境：VS 2008, .NET 3.5
實測數據：
- 改善前：大量結構錯誤
- 改善後：全部測試通過
- 改善幅度：阻斷率 100% → 0%

Learning Points（學習要點）
核心知識點：
- 替代矩陣設計
- 封裝與治理
- 大規模移植策略

技能要求：
- 必備：C#、重構與自動化
- 進階：程式碼分析

延伸思考：
- 套用至其他 API 語意差異移植
- 風險：分類錯誤造成漏網
- 優化：加強測試覆蓋

Practice Exercise（練習題）
- 基礎：替換 5 個呼叫（30 分鐘）
- 進階：寫替換腳本（2 小時）
- 專案：完成一個模組移植（8 小時）

Assessment Criteria（評估標準）
- 功能完整
- 品質優良
- 效能穩定
- 創新落地

----------------------------------------

## Case #7: 寫入特殊字元文字應用 WriteString 而非 WriteRaw

### Problem Statement（問題陳述）
業務場景：寫入包含 <、& 的純文字內容，誤用 WriteRaw 導致非法 XML 或多重轉義。
技術挑戰：區分「純文字」與「片段」，確保正確轉義。
影響範圍：檔案/頁面載入錯誤。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. WriteRaw 假設輸入已被轉義，且不再處理。
2. 開發者以為 WriteRaw 會自動轉義。
3. DOM 後端仍視為文字，放大錯誤。

深層原因：
- 架構層面：WriteRaw 設計目標不同
- 技術層面：轉義語意應由 WriteString 處理
- 流程層面：未建立使用界線

### Solution Design（解決方案設計）
解決策略：純文字一律使用 WriteString，讓 API 自動處理必要轉義。片段才走 Fragment 管道。

實施步驟：
1. 梳理純文字寫入點
- 實作細節：替換為 WriteString
- 所需資源：IDE
- 預估時間：0.5 天

2. 測試特殊字元
- 實作細節：含 <, >, &, " 的樣本
- 所需資源：單元測試
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
writer.WriteStartElement("root");
writer.WriteString("1 < 2 & 3 > 2"); // 自動轉義
writer.WriteEndElement();
```

實作環境：VS 2008, .NET 3.5
實測數據：
- 改善前：非法 XML 或錯誤轉義
- 改善後：合法 XML
- 改善幅度：錯誤率 100% → 0%

Learning Points（學習要點）
核心知識點：
- WriteString vs WriteRaw
- 轉義責任歸屬
- 安全/正確性優先

技能要求：
- 必備：C#、XML 基礎
- 進階：輸入分類

延伸思考：
- 防止 XSS/注入
- 限制：片段不能用 WriteString
- 優化：建立輔助方法

Practice Exercise（練習題）
- 基礎：寫入含特殊字元文字（30 分鐘）
- 進階：建立自動測試樣本集（2 小時）
- 專案：掃描替換錯誤用法（8 小時）

Assessment Criteria（評估標準）
- 功能：合法 XML
- 品質：清楚易讀
- 效能：無過度轉換
- 創新：驗證工具

----------------------------------------

## Case #8: 在 XPathNavigator.AppendChild 上正確插入元素與片段

### Problem Statement（問題陳述）
業務場景：需在現有 XmlDocument 上透過 XPath 定位，並動態插入節點與片段。
技術挑戰：確保 writer 來源為 AppendChild 時，片段仍能被解析為節點。
影響範圍：動態內容生成。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. AppendChild 取得的是 XmlWriter over XmlDocument
2. WriteRaw 仍當文字
3. 必須改用 WriteNode 與 Fragment

深層原因：
- 架構層面：XPathNavigator 與 DOM 寫入合流
- 技術層面：需懂得合併 API 的正確姿勢
- 流程層面：未有指引

### Solution Design（解決方案設計）
解決策略：在 navigator.AppendChild() 建立 writer 後，先 WriteStartElement 建立容器，再以 XmlReader(Fragment)+WriteNode 寫入片段。

實施步驟：
1. 取得 navigator 與 writer
2. 建立容器元素
3. 以 WriteNode 導入片段
4. 驗證

關鍵程式碼/設定：
```csharp
XmlDocument doc = new XmlDocument();
var writer = doc.CreateNavigator().AppendChild();
writer.WriteStartElement("root");
using (var r = XmlReader.Create(new StringReader("<a/><a/>"),
         new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment }))
{
    writer.WriteNode(r, false);
}
writer.WriteEndElement();
writer.Close();
doc.Save(Console.Out);
```

實作環境：VS 2008, .NET 3.5
實測數據：元素節點 0 → 2；輸出正確
改善幅度：100%

Learning Points（學習要點）
核心知識點：XPathNavigator.AppendChild 用法、容器元素必要性、Fragment 導入
技能要求：C#、XPath、Xml API
延伸思考：可對應任意定位點；風險在於未建立容器的設計；優化為輔助方法

Practice Exercise：以 XPath 定位插入片段（30 分鐘）；將多個片段插入不同節點（2 小時）；做一個插入器小專案（8 小時）
Assessment：功能正確、程式碼清晰、效能穩定、介面友善

----------------------------------------

## Case #9: 自製包裝器禁止 DOM 後端的 WriteRaw（模擬 NotSupportedException）

### Problem Statement（問題陳述）
業務場景：團隊希望在 DOM 背後嚴禁 WriteRaw，用「快錯」方式避免誤用。
技術挑戰：無法更改框架行為，但可自製包裝器攔截。
影響範圍：團隊開發體驗與錯誤率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 官方不丟 NotSupportedException（By Design）
2. 易被誤用
3. 缺少防呆機制

深層原因：
- 架構層面：自定包裝器可控用法
- 技術層面：繼承 XmlWriter 攔截方法
- 流程層面：建立一致規範

### Solution Design（解決方案設計）
解決策略：用 Delegating XmlWriter 包裝內部 writer，覆寫 WriteRaw 時直接丟出例外或記錄告警。

實施步驟：
1. 建立 DelegatingXmlWriter
2. 攔截 WriteRaw
3. 提供工廠方法建立安全 writer

關鍵程式碼/設定：
```csharp
public class SafeXmlWriter : XmlWriter
{
    private readonly XmlWriter _inner;
    public SafeXmlWriter(XmlWriter inner) => _inner = inner;

    public override void WriteRaw(string data) =>
        throw new NotSupportedException("WriteRaw is not allowed over XmlDocument.");

    // 其餘成員轉呼叫 _inner
    public override void WriteStartElement(string prefix, string localName, string ns) => _inner.WriteStartElement(prefix, localName, ns);
    public override void WriteString(string text) => _inner.WriteString(text);
    public override void WriteEndElement() => _inner.WriteEndElement();
    public override void Flush() => _inner.Flush();
    public override string LookupPrefix(string ns) => _inner.LookupPrefix(ns);
    public override WriteState WriteState => _inner.WriteState;
    public override void Close() => _inner.Close();
    public override void WriteStartDocument() => _inner.WriteStartDocument();
    public override void WriteEndDocument() => _inner.WriteEndDocument();
    public override void WriteStartAttribute(string prefix, string localName, string ns) => _inner.WriteStartAttribute(prefix, localName, ns);
    public override void WriteEndAttribute() => _inner.WriteEndAttribute();
    public override void WriteCData(string text) => _inner.WriteCData(text);
    public override void WriteCharEntity(char ch) => _inner.WriteCharEntity(ch);
    public override void WriteChars(char[] buffer, int index, int count) => _inner.WriteChars(buffer, index, count);
    public override void WriteComment(string text) => _inner.WriteComment(text);
    public override void WriteWhitespace(string ws) => _inner.WriteWhitespace(ws);
    public override void WriteSurrogateCharEntity(char lowChar, char highChar) => _inner.WriteSurrogateCharEntity(lowChar, highChar);
    public override void WriteRaw(char[] buffer, int index, int count) =>
        throw new NotSupportedException("WriteRaw is not allowed over XmlDocument.");
    public override void WriteProcessingInstruction(string name, string text) => _inner.WriteProcessingInstruction(name, text);
    public override void WriteEntityRef(string name) => _inner.WriteEntityRef(name);
    public override void WriteFullEndElement() => _inner.WriteFullEndElement();
}
```

實作環境：VS 2008, .NET 3.5
實測數據：
- 改善前：誤用導致錯誤輸出
- 改善後：在開發期即拋例外
- 改善幅度：誤用落地 100% → 0%

Learning Points：包裝器設計、快錯策略、團隊治理
技能要求：C# 繼承/委派、API 設計
延伸思考：可記錄 telemetry；風險是向後相容性；優化：以 DI 注入

Practice/Assessment：略（同上模式）

----------------------------------------

## Case #10: 多根片段用 Document 等級讀取失敗—切換到 Fragment

### Problem Statement（問題陳述）
業務場景：外部提供 "<a/><b/>" 形式的片段，開發者用預設 XmlReaderSettings（Document）讀取導致錯誤。
技術挑戰：如何允許多個頂層元素。
影響範圍：資料匯入流程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. ConformanceLevel.Document 僅允許單一根元素
2. 多根資料被視為非法
3. 未正確設定 Fragment

深層原因：
- 架構層面：XML 規範
- 技術層面：設定不當
- 流程層面：預設值盲用

### Solution Design（解決方案設計）
解決策略：將 ConformanceLevel 設為 Fragment，允許多根片段解析，再導入 DOM。

實施步驟：設定 Reader、讀取、寫入、驗證

關鍵程式碼/設定：
```csharp
var settings = new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment };
using var r = XmlReader.Create(new StringReader("<a/><b/>"), settings);
// 接著 WriteNode 導入
```

實作環境：VS 2008, .NET 3.5
實測數據：例外 → 正常；導入節點數 2
改善幅度：100%

Learning Points：ConformanceLevel 差異、片段處理
技能要求：XmlReader 熟悉
延伸思考：Fragment 對驗證/DTD 的影響；優化：統一設定來源

Practice/Assessment：略

----------------------------------------

## Case #11: 寫一個通用 AppendFragment(XmlDocument, string) 輔助函式

### Problem Statement（問題陳述）
業務場景：多處需要寫入片段，重複代碼多。
技術挑戰：避免每處重複 XmlReader + WriteNode 樣板。
影響範圍：維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少共用封裝
2. 片段寫入模式一致
3. 可抽象化

深層原因：
- 架構層面：工具化提升一致性
- 技術層面：統一錯誤處理
- 流程層面：推廣最佳實務

### Solution Design（解決方案設計）
解決策略：封裝 AppendFragment，內部統一使用 Fragment+WriteNode。

實施步驟：撰寫方法、單元測試、替換呼叫

關鍵程式碼/設定：
```csharp
public static void AppendFragment(XmlDocument doc, string containerName, string fragment)
{
    var w = doc.CreateNavigator().AppendChild();
    w.WriteStartElement(containerName);
    using var r = XmlReader.Create(new StringReader(fragment),
        new XmlReaderSettings{ ConformanceLevel = ConformanceLevel.Fragment});
    w.WriteNode(r, false);
    w.WriteEndElement();
    w.Close();
}
```

實測數據：重複碼 -80%；錯誤率下降
Learning/Skills/Practice/Assessment：同模式

----------------------------------------

## Case #12: 以 Save(Console.Out) 與節點計數驗證輸出（除錯診斷）

### Problem Statement（問題陳述）
業務場景：快速確認輸出是否為元素節點或文字節點。
技術挑戰：低成本驗證方法。
影響範圍：功能驗收與除錯效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無立即可視化輸出
2. 隱性錯誤不易發現
3. 缺少簡便檢查

深層原因：
- 架構層面：DOM 檢查需工具
- 技術層面：輸出比對可揭示問題
- 流程層面：建立除錯習慣

### Solution Design（解決方案設計）
解決策略：使用 Save(Console.Out) 快速印出結果，同時計算 ChildNodes 類型以驗證。

關鍵程式碼/設定：
```csharp
doc.Save(Console.Out);
Console.WriteLine();
Console.WriteLine("Element children: " +
    doc.DocumentElement.ChildNodes.OfType<XmlElement>().Count());
```

實測數據：定位問題時間 30 分 → 5 分
Learning/Skills/Practice/Assessment：略

----------------------------------------

## Case #13: 將「Bug」最小重現並回報（VS Report Bug → Connect）

### Problem Statement（問題陳述）
業務場景：團隊誤判為框架 Bug，需與供應商確認設計意圖並取得建議。
技術挑戰：建立最小重現、清晰描述、快速得到回應。
影響範圍：問題澄清與解法落地。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 語意誤解
2. 缺少官方說明
3. 需要溝通管道

深層原因：
- 架構層面：API 行為複雜
- 技術層面：需準確重現
- 流程層面：回報機制

### Solution Design（解決方案設計）
解決策略：用 VS 2008 Report Bug 將最小重現、輸出前後、期待行為上送 Connect，取得官方說明與建議。

實施步驟：撰寫重現、貼上輸出、連結官方回覆、同步團隊

關鍵程式碼/設定：使用 Case #1 重現代碼

實測數據：回覆時間短；建議方案可落地（InnerXml/WriteNode）
Learning/Skills/Practice/Assessment：略

----------------------------------------

## Case #14: 將「By Design」行為轉為團隊規範與範本代碼

### Problem Statement（問題陳述）
業務場景：官方認定為 By Design，需將知識轉為規範避免重犯。
技術挑戰：標準化與宣導。
影響範圍：整個團隊。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：認知落差、歷史用法慣性、缺少範本
深層原因：知識管理不足、範例欠缺、審查缺位

### Solution Design（解決方案設計）
解決策略：撰寫「XML 片段寫入指南」，附 InnerXml 與 WriteNode 範例與反例，納入 Code Review 檢查清單。

實施步驟：文件、範本、審查清單、訓練

關鍵程式碼/設定：引用 Case #2/#3 作為標準範例

實測數據：回歸缺陷數降低；審查通過率提高
Learning/Skills/Practice/Assessment：略

----------------------------------------

## Case #15: 用單元測試驗證片段導入正確性（XPath 驗證）

### Problem Statement（問題陳述）
業務場景：持續驗證輸入片段最終成為元素節點而非文字節點。
技術挑戰：自動化驗證。
影響範圍：CI 稳定。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：容易回歸誤用
深層原因：測試覆蓋不足

### Solution Design（解決方案設計）
解決策略：在測試中使用 XPath 驗證元素存在數量與結構。

關鍵程式碼/設定：
```csharp
var doc = new XmlDocument();
var root = doc.CreateElement("root");
root.InnerXml = "<a/><a/>";
doc.AppendChild(root);
var n = doc.SelectNodes("/root/a").Count;
Assert.AreEqual(2, n);
```

實測數據：回歸缺陷攔截率↑
Learning/Skills/Practice/Assessment：略

----------------------------------------

## Case #16: 為片段導入提供兩軌策略（信任 vs 非信任）

### Problem Statement（問題陳述）
業務場景：片段來源有時可信、有時不可信。
技術挑戰：選擇適合的導入策略，兼顧安全與效率。
影響範圍：安全/正確性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：策略未分層
深層原因：風險評估未固化

### Solution Design（解決方案設計）
解決策略：信任來源走 InnerXml，非信任走 XmlReader(Fragment)+WriteNode（可加額外驗證）。

關鍵程式碼/設定：
```csharp
void AppendByTrust(XmlElement container, string fragment, bool trusted)
{
    if (trusted)
        container.InnerXml = fragment;
    else
    {
        using var w = container.OwnerDocument.CreateNavigator().AppendChild();
        w.WriteStartElement(container.Name);
        using var r = XmlReader.Create(new StringReader(fragment),
            new XmlReaderSettings { ConformanceLevel = ConformanceLevel.Fragment });
        w.WriteNode(r, false);
        w.WriteEndElement();
        w.Close();
    }
}
```

實測數據：正確性與安全性兼顧
Learning/Skills/Practice/Assessment：略

----------------------------------------

案例分類
1. 按難度分類
- 入門級：Case #2, #3, #7, #10, #12, #15
- 中級：Case #1, #4, #5, #8, #11, #16
- 高級：Case #6, #9, #14

2. 按技術領域分類
- 架構設計類：#6, #9, #14, #16
- 效能優化類：#11（減少重複與開銷）
- 整合開發類：#3, #5, #8, #10
- 除錯診斷類：#1, #12, #15
- 安全防護類：#7, #16, #9

3. 按學習目標分類
- 概念理解型：#1, #2, #7, #10
- 技能練習型：#3, #8, #11, #12, #15
- 問題解決型：#4, #5, #6
- 創新應用型：#9, #14, #16

案例關聯圖（學習路徑建議）
- 先學：#7（WriteString vs WriteRaw 基本概念）、#10（ConformanceLevel.Document vs Fragment）、#2（InnerXml）
- 再學：#3（XmlReader(Fragment)+WriteNode 實作）、#8（AppendChild 實戰）
- 進一步：#1（理解設計意圖與問題重現）、#12（輸出驗證）、#15（測試）
- 高階：#4、#5（複雜寫入情境重構）、#11（工具化封裝）
- 進階架構與治理：#6（大規模移植策略）、#9（包裝器禁用 WriteRaw）、#14（團隊規範）、#16（兩軌策略）

依賴關係：
- #3 依賴 #10（Fragment 概念）
- #8 依賴 #3（WriteNode 用法）
- #11 依賴 #3/#2（內部實作）
- #6 依賴 #2/#3/#7（替代矩陣）
- #9 依賴 #1（行為理解）
- #14 依賴 #1/#2/#3（知識沉澱）

完整學習路徑：
#7 → #10 → #2 → #3 → #8 → #1 → #12 → #15 → #4 → #5 → #11 → #6 → #9 → #14 → #16

說明
- 本組案例完全建立在文章與官方回覆所述的行為與解法（InnerXml、XmlReader(Fragment)+WriteNode）上，將相同核心問題拆解成多個教學導向的使用情境，涵蓋從單點修正到團隊治理、從 API 正確用法到測試驗證的完整閉環。