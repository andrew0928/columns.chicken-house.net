---
layout: synthesis
title: "原來 .NET 早就內建 XmlNodeWriter 了..."
synthesis_type: solution
source_post: /2008/12/07/dotnet-built-in-xmlnodewriter-discovery/
redirect_from:
  - /2008/12/07/dotnet-built-in-xmlnodewriter-discovery/solution/
---

以下內容基於原文中可辨識的問題、根因、解法與效益描述，萃取並重組為可教學、可練習、可評估的 18 個案例。每一個案例都以實務導向呈現，並附示範程式碼與練習題。

## Case #1: 在 XmlDocument 局部使用 XmlWriter 直接更新節點

### Problem Statement（問題陳述）
業務場景：專案需在既有 XmlDocument 中，對特定節點進行插入/覆寫（寫入新子節點、屬性與 CDATA），但不想先將片段序列化成文字再解析回 DOM，避免多餘轉換與潛在效能損耗。
技術挑戰：XmlWriter 官方常見用法多寫入檔案或 TextWriter，缺乏直覺「寫到 XmlNode」的入口。
影響範圍：導致多一次字串序列化與再解析、程式碼冗長、可讀性差、容易出錯。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 認知落差：不知 .NET 2.0 已可從 XmlNode 取得可供 XmlWriter 寫入的通道（CreateNavigator().AppendChild）。
2. API 可見度低：功能藏在 XPathNavigator.AppendChild，不在 XmlWriter 類型清單中。
3. 舊解法慣性：習慣以字串中介（StringBuilder → parse）回寫 XML。
深層原因：
- 架構層面：未將「資料流」（Writer 直接寫 DOM）設為既定模式。
- 技術層面：API 使用經驗停留在 XmlTextWriter 與檔案/文字輸出。
- 流程層面：缺少針對局部 XML 更新的標準封裝。

### Solution Design（解決方案設計）
解決策略：改以 node.CreateNavigator().AppendChild() 取得目標節點的 XmlWriter，直接用 Writer API 在 DOM 上建立元素/屬性/CDATA，避免中間字串往返。

實施步驟：
1. 取得目標節點的 Writer
- 實作細節：XmlNode.CreateNavigator().AppendChild() 回傳 XmlWriter。
- 所需資源：System.Xml、System.Xml.XPath
- 預估時間：0.5 小時
2. 以 Writer 寫入元素/屬性/CDATA
- 實作細節：WriteStartElement/WriteAttributeString/WriteCData/WriteEndElement。
- 所需資源：C#、單元測試框架
- 預估時間：0.5 小時
3. 儲存/檢視結果
- 實作細節：XmlDocument.Save 或比對節點。
- 所需資源：Console 或測試
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
XmlDocument xdoc = new XmlDocument();
xdoc.LoadXml("<root><node1/><node2/></root>");

// 直接針對 node1 建立可寫入的 Writer
XmlNode node1 = xdoc.DocumentElement.SelectSingleNode("node1");
using (XmlWriter xw = node1.CreateNavigator().AppendChild())
{
    xw.WriteStartElement("newNode");
    xw.WriteAttributeString("newatt", "123");
    xw.WriteCData("1234567890");
    xw.WriteEndElement();
}
xdoc.Save(Console.Out); // 驗證結果
```

實際案例：原文示範將 newNode（含屬性與 CDATA）直接寫入目標節點。
實作環境：.NET Framework 2.0+、C#、System.Xml
實測數據：
- 改善前：需 TextWriter/StringBuilder 中介並再解析
- 改善後：直接寫入 XmlNode，無需往返
- 改善幅度：移除 1 次序列化與 1 次解析步驟（定性）

Learning Points（學習要點）
核心知識點：
- XmlNode.CreateNavigator().AppendChild 可取得寫入 DOM 的 Writer
- Writer API 操作元素/屬性/CDATA
- 直接寫 DOM 減少中間轉換
技能要求：
- 必備技能：C#、XmlDocument 與 XmlWriter 基礎
- 進階技能：XPath 選取節點、單元測試驗證
延伸思考：
- 可用於大量節點批次更新
- 注意 Writer 關閉與 Flush，以免內容不完整
- 可封裝為共用工具方法以統一團隊用法
Practice Exercise（練習題）
- 基礎練習：將三個不同子節點與屬性寫入指定節點（30 分）
- 進階練習：寫入含混合內容文字與 CDATA 的節點結構（2 小時）
- 專案練習：實作一個節點更新器，支援多節點路徑與條件更新（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：是否正確寫入元素/屬性/CDATA
- 程式碼品質（30%）：可讀性、錯誤處理、資源釋放
- 效能優化（20%）：避免不必要轉換
- 創新性（10%）：API 封裝與擴充性

---

## Case #2: 以 XSLT 將記憶體內 XmlDocument 直接轉成另一份 XmlDocument

### Problem Statement（問題陳述）
業務場景：需在記憶體中以 XSLT 將輸入 XmlDocument 轉換為另一份 XmlDocument（如報表或介面輸出），不可落地檔案且需高效。
技術挑戰：傳統做法需把輸出導到 StringBuilder/文本，再解析回 XmlDocument。
影響範圍：多餘記憶體拷貝與解析，程式碼冗長。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不知可用 XmlNode.CreateNavigator().AppendChild 當作 XSLT 輸出。
2. 慣用 XmlWriter to StringBuilder 的中介方式。
3. 對 XslCompiledTransform 之輸出多載不熟。
深層原因：
- 架構層面：未建立「全記憶體管線」處理模式。
- 技術層面：Writer 目的地不只檔案/文字的知識落差。
- 流程層面：缺少最佳實務指引。

### Solution Design（解決方案設計）
解決策略：建立輸出 XmlDocument 的導航器與 AppendChild() Writer，將 XSLT 直接寫入該 Writer，省去中介字串。

實施步驟：
1. 建立輸出文件與 Writer
- 實作細節：output.CreateNavigator().AppendChild()
- 所需資源：System.Xml.Xsl
- 預估時間：0.5 小時
2. 載入 XSLT 並執行轉換
- 實作細節：XslCompiledTransform.Load/Transform
- 所需資源：XSLT 檔
- 預估時間：1 小時
3. 驗證輸出為有效 XML
- 實作細節：儲存/比對節點
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
XmlDocument input = new XmlDocument();
input.LoadXml("<root><item>1</item></root>");

XmlDocument output = new XmlDocument();
XslCompiledTransform xslt = new XslCompiledTransform();
xslt.Load("transform.xslt");

using (XmlWriter writer = output.CreateNavigator().AppendChild())
{
    // 也可用 xslt.Transform(input, (XsltArgumentList)null, writer);
    xslt.Transform(input, null, writer);
}
// output 直接為轉換後的 XmlDocument
```

實際案例：原文評論引用 Oleg 的做法，以 AppendChild Writer 承接 XSLT 輸出。
實作環境：.NET 2.0+、C#、System.Xml.Xsl
實測數據：
- 改善前：Transform → StringBuilder → 解析回 XmlDocument
- 改善後：Transform → 直接寫入 XmlDocument
- 改善幅度：移除 1 次序列化與 1 次解析（定性）

Learning Points（學習要點）
核心知識點：
- XslCompiledTransform 的多載使用
- IXPathNavigable（XmlDocument）可直接參與 Transform
- AppendChild Writer 作為輸出接點
技能要求：
- 必備技能：XSLT、C#
- 進階技能：錯誤處理與字元編碼
延伸思考：
- 可串接 XmlReader 當輸入，形成 Reader→Writer 全記憶體流
- 注意 XSLT 安全與外部資源參考
- 可加入 XmlWriterSettings 控制縮排
Practice Exercise（練習題）
- 基礎練習：以 XSLT 將 items 轉為 summary（30 分）
- 進階練習：加入 XsltArgumentList 與參數化轉換（2 小時）
- 專案練習：打造可插拔的 XSLT 管線（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出節點正確、格式合法
- 程式碼品質（30%）：可維護、清晰
- 效能優化（20%）：避免中介字串
- 創新性（10%）：可擴充的管線架構

---

## Case #3: 外部 XmlNodeWriter 元件失效（網站下線）後的替代策略

### Problem Statement（問題陳述）
業務場景：既有專案仰賴第三方 XmlNodeWriter（host 在 gotdotnet），網站關閉後無法取得原始碼與更新，需要立即替代方案。
技術挑戰：必須維持原有程式設計風格與效能，快速替換不應影響既有業務邏輯。
影響範圍：建置流程卡關、相依套件中斷、交付風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 相依資源單點（gotdotnet）關閉。
2. 無內部鏡像或原始碼備份。
3. 團隊不了解等效內建 API。
深層原因：
- 架構層面：缺乏替代與降級策略。
- 技術層面：不熟悉 .NET 內建 DOM Writer 能力。
- 流程層面：相依套件治理與資安盤點不足。

### Solution Design（解決方案設計）
解決策略：改用內建 node.CreateNavigator().AppendChild() 取得 Writer，若需 API 相容性則加輕量 Adapter；短期內嵌程式碼，解除外部依賴。

實施步驟：
1. 盤點使用點
- 實作細節：搜尋專案中 XmlNodeWriter 的使用
- 所需資源：IDE 搜尋、靜態分析
- 預估時間：0.5-1 小時
2. 快速替換
- 實作細節：以 AppendChild Writer 或 Adapter 類替代
- 所需資源：C# 原始碼
- 預估時間：1-2 小時
3. 驗證與佈署
- 實作細節：單元測試、CI
- 所需資源：測試框架、CI
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 直接替換：取得 Writer 的那一行
using (XmlWriter xw = targetNode.CreateNavigator().AppendChild())
{
    // 原有寫入邏輯維持不變
}
```

實際案例：原文指出 gotdotnet 關閉，改以內建 API 成功替代。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：外部依賴中斷、無法建置
- 改善後：完全移除外部依賴，原功能可運作
- 改善幅度：相依風險由高降為低（定性）

Learning Points（學習要點）
核心知識點：
- 以內建 API 替代外部工具
- 風險治理與相依套件管理
- 以程式碼內嵌快速止血
技能要求：
- 必備技能：C#、Xml API
- 進階技能：相依性分析、重構
延伸思考：
- 長期可封裝 NuGet 套件供內部使用
- 建立相依鏡像與版本控管
- 風險演練與退出策略
Practice Exercise（練習題）
- 基礎練習：移除一個外部 DLL，相同功能用內建 API 重寫（30 分）
- 進階練習：用靜態分析找出所有使用點並寫測試（2 小時）
- 專案練習：撰寫替換計畫書、執行與驗收（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：替代後行為相同
- 程式碼品質（30%）：簡潔、可維護
- 效能優化（20%）：無顯著退化
- 創新性（10%）：替代策略與風險控制

---

## Case #4: 以 Adapter 包裝實作自製 XmlNodeWriter（維持舊 API 習慣）

### Problem Statement（問題陳述）
業務場景：既有程式碼與開發者習慣使用 XmlNodeWriter 類型，想維持 new XmlNodeWriter(node, clean) 的使用方式，但內部改用內建 AppendChild Writer。
技術挑戰：XmlWriter 為抽象類，需實作多個抽象方法，避免大幅改造。
影響範圍：介面不一致導致大量修改成本與學習成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 原有 API 為類型，非工廠方法。
2. 內建能力以方法返回 Writer，非具名類型。
3. 繼承 XmlWriter 需補齊多個抽象方法。
深層原因：
- 架構層面：API 設計與使用慣性未一致。
- 技術層面：不了解委派/裝飾器模式可快速落地。
- 流程層面：缺少共用 Adapter 範本。

### Solution Design（解決方案設計）
解決策略：以 Adapter（委派）模式包裝內部 Writer，所有抽象方法直接轉呼叫內部 _inner_writer，確保行為一致且低風險替換。

實施步驟：
1. 建立建構子與清理邏輯
- 實作細節：若 clean 為 true 則 RemoveAll，再用 AppendChild 建 inner
- 所需資源：C#
- 預估時間：0.5 小時
2. 補齊抽象方法委派
- 實作細節：將抽象方法/屬性轉呼叫 _inner_writer
- 所需資源：IDE 產生樣板
- 預估時間：1 小時
3. 套用並驗證
- 實作細節：替換 new XmlNodeWriter 呼叫
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class XmlNodeWriter : XmlWriter
{
    private readonly XmlWriter _inner;
    public XmlNodeWriter(XmlNode node, bool clean)
    {
        if (clean) node.RemoveAll();
        _inner = node.CreateNavigator().AppendChild();
    }
    public override void Close() => _inner.Close();
    public override void Flush() => _inner.Flush();
    public override string LookupPrefix(string ns) => _inner.LookupPrefix(ns);
    public override WriteState WriteState => _inner.WriteState;
    public override void WriteStartElement(string prefix, string localName, string ns)
        => _inner.WriteStartElement(prefix, localName, ns);
    public override void WriteEndElement() => _inner.WriteEndElement();
    public override void WriteString(string text) => _inner.WriteString(text);
    // ...其餘抽象成員同樣委派（略）
}
```

實際案例：原文作者以「延長線」式樣板委派所有成員，成功 Work。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：需全面改寫呼叫端
- 改善後：維持相同建構子與用法
- 改善幅度：呼叫端改動接近 0（定性）

Learning Points（學習要點）
核心知識點：
- Adapter/Decorator 委派技巧
- XmlWriter 抽象類的覆寫要點
- 以最小改動維持相容
技能要求：
- 必備技能：C# 繼承與委派
- 進階技能：自動產生與維護樣板碼
延伸思考：
- 可以 Source Generator/繼承輔助工具減少樣板碼
- 以組合優於繼承，降低耦合
- 注意 Dispose/Flush 行為一致性
Practice Exercise（練習題）
- 基礎練習：實作 5 個常用抽象方法的委派（30 分）
- 進階練習：完成全部抽象成員並寫單元測試（2 小時）
- 專案練習：將專案中對 XmlNodeWriter 的使用改到新 Adapter（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：行為與原期望一致
- 程式碼品質（30%）：委派清晰、無重複
- 效能優化（20%）：無額外顯著開銷
- 創新性（10%）：封裝與自動化手段

---

## Case #5: 以工廠模式取代大量抽象成員樣板碼

### Problem Statement（問題陳述）
業務場景：不想維護繁雜的繼承與委派樣板碼，希望只用靜態方法建立寫入 XmlNode 的 XmlWriter，並沿用官方 Create 的操作習慣。
技術挑戰：無法為現有類型（XmlWriter）新增 static 擴充方法。
影響範圍：若硬繼承，將產生數十個覆寫，維護成本高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. C# Extension Method 僅支援實例方法。
2. XmlWriter 為抽象類，多抽象成員需實作。
3. 需要兼顧易用性與低成本。
深層原因：
- 架構層面：工廠模式能統一建構邏輯。
- 技術層面：API 易用性要求與語言限制的折衝。
- 流程層面：團隊需要穩定可複用入口。

### Solution Design（解決方案設計）
解決策略：建立 XmlWriterFactory 類別，提供多個 Create 多載，內部用 node.CreateNavigator().AppendChild()，可選擇清空內容，並接受 XmlWriterSettings。

實施步驟：
1. 設計工廠多載
- 實作細節：Create(node)、Create(node, clean)、Create(node, clean, settings)
- 所需資源：C#
- 預估時間：1 小時
2. 設定包裹 WriterSettings
- 實作細節：XmlWriter.Create(inner, settings)
- 預估時間：0.5 小時
3. 替換呼叫端取得 Writer 的那一行
- 實作細節：最小改動
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public abstract class XmlWriterFactory : XmlWriter
{
    public static XmlWriter Create(XmlNode node) => Create(node, false, null);
    public static XmlWriter Create(XmlNode node, bool cleanContent) => Create(node, cleanContent, null);
    public static XmlWriter Create(XmlNode node, bool cleanContent, XmlWriterSettings settings)
    {
        if (node == null) throw new ArgumentNullException(nameof(node));
        if (cleanContent) node.RemoveAll();
        XmlWriter xw = node.CreateNavigator().AppendChild();
        if (settings != null) xw = XmlWriter.Create(xw, settings);
        return xw;
    }
}
```

實際案例：原文提供完整工廠實作並示範改造。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：維護 20+ 抽象成員委派
- 改善後：僅數十行工廠方法
- 改善幅度：樣板碼大幅減少（定性）

Learning Points（學習要點）
核心知識點：
- 工廠模式封裝建構複雜度
- XmlWriterSettings 的包裹用法
- 最小改動替換策略
技能要求：
- 必備技能：C# 類別設計
- 進階技能：API 設計與相容性
延伸思考：
- 是否需要介面以利測試替身
- 以 NuGet 封裝工廠工具
- 進一步提供非靜態 DI 版本
Practice Exercise（練習題）
- 基礎練習：為工廠新增 Create(node, settings) 多載（30 分）
- 進階練習：加入驗證與日誌（2 小時）
- 專案練習：以工廠全面替換專案中的 Writer 取得方式（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：多載與清空、設定都可用
- 程式碼品質（30%）：簡潔、清楚
- 效能優化（20%）：無多餘包裹開銷
- 創新性（10%）：API 易用性設計

---

## Case #6: 可選擇清空目標節點內容再寫入（RemoveAll 開關）

### Problem Statement（問題陳述）
業務場景：在既有節點上覆寫內容時，需要先清掉原有子節點與屬性，避免新舊內容混雜或破壞結構一致性。
技術挑戰：AppendChild 預設為附加，需顯式處理「清空後重建」的語意。
影響範圍：漏清空將導致資料殘留、驗證失敗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. AppendChild 不會自動清掉舊內容。
2. DOM 更新語意未標準化。
3. 呼叫端容易忽略前置狀態。
深層原因：
- 架構層面：缺乏「覆寫模式」的 API 約束。
- 技術層面：需顧及屬性與子節點的一致清理。
- 流程層面：缺少範本與約定。

### Solution Design（解決方案設計）
解決策略：在工廠/建構子加入 cleanContent 布林參數，為 true 時先 node.RemoveAll()，再建立 Writer 寫入，確保狀態乾淨。

實施步驟：
1. API 設計
- 實作細節：Create(node, cleanContent)
- 預估時間：0.5 小時
2. 實作清理
- 實作細節：node.RemoveAll()
- 預估時間：0.2 小時
3. 文件與範本
- 實作細節：寫明覆寫模式需設置 cleanContent
- 預估時間：0.3 小時

關鍵程式碼/設定：
```csharp
XmlWriter xw = XmlWriterFactory.Create(targetNode, cleanContent: true);
using (xw)
{
    xw.WriteStartElement("config");
    xw.WriteAttributeString("version", "2");
    xw.WriteEndElement();
}
```

實際案例：原文中 XmlNodeWriter 建構子支援 clean 參數。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：可能殘留舊節點/屬性
- 改善後：覆寫前統一清空
- 改善幅度：資料殘留風險降為低（定性）

Learning Points（學習要點）
核心知識點：
- RemoveAll 的作用範圍（子節點與屬性）
- API 設計加入明確語意
- 覆寫與附加兩種模式
技能要求：
- 必備技能：XmlDocument 操作
- 進階技能：API 契約設計
延伸思考：
- 是否支援選擇性清空（如僅子節點）
- 需不需要保留指定屬性
- 建立預設策略與註解
Practice Exercise（練習題）
- 基礎練習：對指定節點清空後重建單一子節點（30 分）
- 進階練習：實作可傳入白名單屬性保留邏輯（2 小時）
- 專案練習：為專案所有覆寫場景加上 cleanContent 參數（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：清空與重建正確
- 程式碼品質（30%）：介面直覺
- 效能優化（20%）：不重複清理
- 創新性（10%）：選擇性清空策略

---

## Case #7: 使用 XmlWriterSettings 控制縮排、編碼與特性

### Problem Statement（問題陳述）
業務場景：在寫入 DOM 時需維持一致格式（縮排、換行、字元處理），方便 diff 與審閱。
技術挑戰：AppendChild 回傳的 Writer 沒有直接帶入設定。 
影響範圍：輸出格式不一致，影響版本控管與審查。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 直接使用 AppendChild Writer 未套設定。
2. 呼叫端未意識到 WriterSettings 的包裹手法。
3. 忽略格式一致性的價值。
深層原因：
- 架構層面：缺乏跨模組格式約束。
- 技術層面：不熟悉「包裹內層 Writer」的技巧。
- 流程層面：缺少格式化規範。

### Solution Design（解決方案設計）
解決策略：先取得 inner Writer，再以 XmlWriter.Create(inner, settings) 包裹，藉此套用縮排/換行等設定；在工廠方法統一實作。

實施步驟：
1. 準備設定
- 實作細節：new XmlWriterSettings { Indent = true, NewLineOnAttributes = true, ... }
- 預估時間：0.3 小時
2. 包裹 Writer
- 實作細節：XmlWriter.Create(inner, settings)
- 預估時間：0.2 小時
3. 規範化
- 實作細節：在工廠方法提供 settings 參數
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
var settings = new XmlWriterSettings
{
    Indent = true,
    NewLineOnAttributes = true
};
using (var xw = XmlWriterFactory.Create(targetNode, cleanContent: false, settings))
{
    xw.WriteStartElement("pretty");
    xw.WriteAttributeString("a", "1");
    xw.WriteEndElement();
}
```

實際案例：原文工廠支援 settings 並示範包裹。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：格式無一致性
- 改善後：統一設定輸出
- 改善幅度：審閱/比對成本降低（定性）

Learning Points（學習要點）
核心知識點：
- XmlWriterSettings 作用與常用欄位
- 包裹內層 Writer 的技巧
- 在工廠集中設定
技能要求：
- 必備技能：C#、XmlWriterSettings
- 進階技能：團隊格式規範建立
延伸思考：
- 規範化設定集中於單一處管理
- 測試保證格式一致
- 針對不同場景定義預設設定
Practice Exercise（練習題）
- 基礎練習：輸出帶縮排與屬性換行的節點（30 分）
- 進階練習：為不同環境（dev/prod）切換設定（2 小時）
- 專案練習：將專案 Writer 全面導入一致設定（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：設定正確套用
- 程式碼品質（30%）：集中化與解耦
- 效能優化（20%）：設定不造成明顯成本
- 創新性（10%）：設定管理方式

---

## Case #8: 對齊官方體驗的多載 Create API 設計

### Problem Statement（問題陳述）
業務場景：團隊希望像官方 XmlWriter.Create 一樣直覺，提供多種 Create 多載以降低學習曲線。
技術挑戰：無法擴充現有類型的 static 方法，只能自建工廠類。
影響範圍：不一致 API 體驗將增加教學成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. C# 限制 static 擴充。
2. 原類型無法修改。
3. 使用方期待一致命名與行為。
深層原因：
- 架構層面：API 一致性提升採用率。
- 技術層面：需以自建工廠彌補。
- 流程層面：文件與 IntelliSense 引導。

### Solution Design（解決方案設計）
解決策略：在 XmlWriterFactory 提供 3 個常用多載（node / node+clean / node+clean+settings），命名與行為貼近官方。

實施步驟：
1. 設計多載與文件
- 實作細節：參數順序與預設合理
- 預估時間：0.5 小時
2. 補充 IntelliSense 註解
- 實作細節：XML Doc Comments
- 預估時間：0.5 小時
3. 教學指引
- 實作細節：README/範例
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
// 同 Case #5 的工廠多載
// 使用端
using (var xw = XmlWriterFactory.Create(node, cleanContent: true))
{
    // ...
}
```

實際案例：原文展示繼承後可見 13 種 Create 選項（含自建）。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：API 分裂、記憶成本高
- 改善後：一致風格，易於採用
- 改善幅度：新手導入時間縮短（定性）

Learning Points（學習要點）
核心知識點：
- API 設計一致性
- 多載與預設參數策略
- 文件與 IDE 體驗
技能要求：
- 必備技能：C#、API 設計
- 進階技能：開發者體驗優化
延伸思考：
- 提供擴充點（回呼、選項物件）
- 是否提供異常訊息標準化
- 加入分析器提醒誤用
Practice Exercise（練習題）
- 基礎練習：加入 Create(node, settings) 並撰寫 XML Doc（30 分）
- 進階練習：寫使用指南與範例（2 小時）
- 專案練習：做一個小型 XML 工具箱（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：多載合宜
- 程式碼品質（30%）：註解與一致性
- 效能優化（20%）：介面無冗餘
- 創新性（10%）：DX 改善

---

## Case #9: 僅改「取得 Writer 的那一行」即可完成整合

### Problem Statement（問題陳述）
業務場景：既有大量以 XmlWriter 操作的程式碼，不希望大改，盡量只換取得 Writer 的方式即可。
技術挑戰：需確保後續 Write 邏輯完全無需修改。
影響範圍：改動越小，風險越低，越容易快速導入。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 現況僅在 Writer 來源不同。
2. 業務寫入邏輯可重用。
3. 不想引入新型別與語法。
深層原因：
- 架構層面：解耦「來源」與「行為」。
- 技術層面：Writer 是共通介面。
- 流程層面：漸進式導入策略。

### Solution Design（解決方案設計）
解決策略：將 Writer 取得方式替換為 XmlWriterFactory.Create(node, ...)，其餘寫入邏輯不動，快速驗證與佈署。

實施步驟：
1. 找出建構點
- 實作細節：以搜尋/重構工具定位
- 預估時間：0.5 小時
2. 替換為工廠
- 實作細節：改為 Create(node, clean, settings)
- 預估時間：0.5 小時
3. 回歸測試
- 實作細節：比對輸出 XML
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
// 原：XmlWriter xw = XmlWriter.Create(sb);
XmlWriter xw = XmlWriterFactory.Create(targetNode, cleanContent: true);
// 後續 xw.Write... 不變
```

實際案例：原文指出「只要改掉如何拿到 XmlWriter 那行，其它都照舊就可執行」。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：需字串中介
- 改善後：直接寫入節點
- 改善幅度：開發改動極小（定性）

Learning Points（學習要點）
核心知識點：
- 最小侵入式重構
- Writer 行為一致的好處
- 回歸測試的重要性
技能要求：
- 必備技能：重構、測試
- 進階技能：自動化比對 XML
延伸思考：
- 可否以 Adapter 減少替換點
- 引入 DI 管理 Writer 來源
- 建構統一的 Writer Provider
Practice Exercise（練習題）
- 基礎練習：替換一處 Writer 來源（30 分）
- 進階練習：撰寫比對工具驗證前後輸出一致（2 小時）
- 專案練習：完成一輪全專案替換與回歸（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：結果一致
- 程式碼品質（30%）：改動最小
- 效能優化（20%）：移除中介
- 創新性（10%）：測試自動化

---

## Case #10: 大型 XML 操作選擇 XmlReader/Writer 以改善效能

### Problem Statement（問題陳述）
業務場景：處理大型 XML（如報表、整批資料交換），使用 XmlDocument 導致記憶體壓力與速度不佳。
技術挑戰：如何在保留可維護性的前提下提升效能。
影響範圍：執行時間長、記憶體高、易 OOM。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. XmlDocument 為 DOM 需完整載入。
2. 大量物件配置與樹操作。
3. 誤用 DOM 做串流型工作。
深層原因：
- 架構層面：未以串流思維設計。
- 技術層面：對 Reader/Writer 的優勢不熟。
- 流程層面：未做效能基準比較。

### Solution Design（解決方案設計）
解決策略：優先採用 XmlReader/Writer，僅在需要 DOM 時局部使用，結合 AppendChild 可在必要時直接回寫至 DOM。

實施步驟：
1. 識別串流友善區段
- 實作細節：以 Reader 逐項處理
- 預估時間：1 小時
2. 局部 DOM 更新
- 實作細節：用 AppendChild 寫回目標節點
- 預估時間：1 小時
3. 基準測試
- 實作細節：比對 DOM 全載入 vs 串流
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
using (XmlReader xr = XmlReader.Create("big.xml"))
{
    while (xr.Read())
    {
        // 讀取處理...
    }
}
// 僅在必要時回寫到既有 DOM 節點
using (XmlWriter xw = targetNode.CreateNavigator().AppendChild())
{
    xw.WriteStartElement("summary");
    xw.WriteEndElement();
}
```

實際案例：原文指出 XmlReader/Writer 以效能為考量，避免大型 XML 用 XmlDocument。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：DOM 全載入，記憶體/時間高
- 改善後：多用串流，局部 DOM 更新
- 改善幅度：資源占用下降（定性）

Learning Points（學習要點）
核心知識點：
- Reader/Writer 對大型資料的優勢
- 串流+局部 DOM 的折衷
- 減少中間字串往返
技能要求：
- 必備技能：XmlReader/Writer
- 進階技能：效能測試
延伸思考：
- 管線化處理與背壓
- 例外處理與錯誤復原
- 分塊/分頁策略
Practice Exercise（練習題）
- 基礎練習：用 Reader 讀入並計數節點（30 分）
- 進階練習：Reader→Writer 轉換流程（2 小時）
- 專案練習：重寫大型 XML 任務為串流管線（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：結果正確
- 程式碼品質（30%）：無資源外洩
- 效能優化（20%）：明顯改善
- 創新性（10%）：處理策略

---

## Case #11: 使用 using/Close 確保 Writer 正確 Flush 與釋放

### Problem Statement（問題陳述）
業務場景：偶發輸出不完整或格式異常，多因 Writer 未正確關閉或 Flush。
技術挑戰：容易忽略 Close/Dispose 導致緩衝未寫入。
影響範圍：產出 XML 損壞、測試不穩定。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 少呼叫 Close/Dispose。
2. 忽略 Writer 具緩衝區。
3. 缺少 using 模式。
深層原因：
- 架構層面：資源管理未制度化。
- 技術層面：對 IDisposable 認知不足。
- 流程層面：無靜態分析/規範提醒。

### Solution Design（解決方案設計）
解決策略：以 using 包裹 Writer 生命週期，或在 finally 中 Close/Flush，確保緩衝刷新。

實施步驟：
1. 套用 using
- 實作細節：using (XmlWriter xw = ...) { ... }
- 預估時間：0.2 小時
2. 加入靜態分析/規則
- 實作細節：分析器或 code review 清單
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
using (XmlWriter xw = targetNode.CreateNavigator().AppendChild())
{
    xw.WriteStartElement("ok");
    xw.WriteEndElement();
} // 自動 Close/Flush
```

實際案例：原文評論示範 using 包裹 Writer。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：偶發輸出不完整
- 改善後：資源自動釋放、內容完整
- 改善幅度：穩定性提高（定性）

Learning Points（學習要點）
核心知識點：
- IDisposable/using 模式
- Writer 緩衝機制
- 例外下的資源釋放
技能要求：
- 必備技能：C# using/try-finally
- 進階技能：分析器設定
延伸思考：
- 非同步寫入時的釋放策略
- 混合使用多層 Writer 的關閉順序
Practice Exercise（練習題）
- 基礎練習：將手動 Close 改為 using（30 分）
- 進階練習：實作容錯與 finally Close（2 小時）
- 專案練習：掃描專案加上 using/Dispose（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：無遺漏釋放
- 程式碼品質（30%）：一致使用模式
- 效能優化（20%）：避免重複 Flush
- 創新性（10%）：自動化檢查

---

## Case #12: 以 Writer 在現有節點上快速寫屬性與 CDATA

### Problem Statement（問題陳述）
業務場景：需在節點上新增屬性與 CDATA，若用 DOM API（CreateElement/AppendChild）較繁瑣。
技術挑戰：維持簡潔、可讀的寫入程式碼。
影響範圍：開發效率與可讀性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. DOM 操作步驟多。
2. 開發者不熟 Writer 對 DOM 的寫法。
3. 缺少範例。
深層原因：
- 架構層面：未建立統一寫入風格。
- 技術層面：API 使用偏好差異。
- 流程層面：模板/範例缺少。

### Solution Design（解決方案設計）
解決策略：在目標節點上取得 Writer，以 WriteAttributeString/WriteCData/WriteStartElement 提高可讀性與效率。

實施步驟：
1. 取得 Writer
- 實作細節：CreateNavigator().AppendChild()
2. 寫入屬性/CDATA
- 實作細節：Writer API
3. 驗證
- 實作細節：比對節點

關鍵程式碼/設定：
```csharp
using (var xw = node.CreateNavigator().AppendChild())
{
    xw.WriteStartElement("newNode");
    xw.WriteAttributeString("newatt", "123");
    xw.WriteCData("1234567890");
    xw.WriteEndElement();
}
```

實際案例：原文示範相同操作。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：多行 DOM 建構
- 改善後：幾行 Writer 寫入
- 改善幅度：程式碼量明顯下降（定性）

Learning Points（學習要點）
核心知識點：
- Writer 寫屬性/CDATA 的 API
- DOM 與 Writer 混搭
- 可讀性提升的價值
技能要求：
- 必備技能：XML 基礎
- 進階技能：設計寫入模板
延伸思考：
- 抽成輔助方法（寫常見片段）
- 規範命名與屬性順序
Practice Exercise（練習題）
- 基礎練習：寫入 2 個屬性與一段 CDATA（30 分）
- 進階練習：封裝擴充方法/輔助類（2 小時）
- 專案練習：將重複片段改用輔助庫（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：節點正確
- 程式碼品質（30%）：可讀與可重用
- 效能優化（20%）：避免多餘 API 呼叫
- 創新性（10%）：抽象設計

---

## Case #13: 「延長線」式委派補齊抽象成員（覆寫策略）

### Problem Statement（問題陳述）
業務場景：必須繼承 XmlWriter（如為相容而自建類），需要快速補齊 20+ 抽象方法/屬性。
技術挑戰：樣板碼多，易出錯。
影響範圍：維護成本高、風險上升。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 抽象成員數量多。
2. 人工實作易遺漏。
3. 不知自動產生/委派技巧。
深層原因：
- 架構層面：傾向繼承而非組合。
- 技術層面：IDE 自動化未善用。
- 流程層面：缺少審查清單。

### Solution Design（解決方案設計）
解決策略：以「延長線」委派至 _inner_writer，透過 IDE 產生覆寫骨架，逐一指派委派呼叫，確保行為一致。

實施步驟：
1. 生成覆寫骨架
- 實作細節：IDE 產生 override
2. 全面委派至 _inner
- 實作細節：每個成員僅轉呼叫
3. 測試覆蓋
- 實作細節：端到端寫入驗證

關鍵程式碼/設定：
```csharp
public override void Flush() => _inner_writer.Flush();
public override string LookupPrefix(string ns) => _inner_writer.LookupPrefix(ns);
// ...其餘同理
```

實際案例：原文稱其為「無聊的延長線程式碼」但可行。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：大量手寫錯誤風險
- 改善後：一致委派，行為可靠
- 改善幅度：錯誤風險下降（定性）

Learning Points（學習要點）
核心知識點：
- 委派/裝飾器模式
- 覆寫自動化
- 行為一致性的重要
技能要求：
- 必備技能：C# 覆寫
- 進階技能：工具化產生碼
延伸思考：
- 是否改用工廠減少複雜度（見 Case #5）
- 以測試金字塔保障
Practice Exercise（練習題）
- 基礎練習：委派 10 個常用成員（30 分）
- 進階練習：完成所有成員並測（2 小時）
- 專案練習：建立範本與指北（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：行為等同
- 程式碼品質（30%）：無重複與遺漏
- 效能優化（20%）：委派開銷可忽略
- 創新性（10%）：自動化程度

---

## Case #14: 無法擴充 static 方法的替代作法

### Problem Statement（問題陳述）
業務場景：希望以 Extension Method 擴充 XmlWriter.Create 來支持寫入 XmlNode，但 C# 不支援擴充 static。
技術挑戰：需提供近似體驗且不破壞現有 API。
影響範圍：設計折衷與使用者體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Extension Method 限定擴充實例方法。
2. XmlWriter 為 BCL 類，無法修改。
3. 團隊期待一致體驗。
深層原因：
- 架構層面：需替代路徑不影響使用。
- 技術層面：語言限制。
- 流程層面：文件溝通不足。

### Solution Design（解決方案設計）
解決策略：建立獨立工廠類 XmlWriterFactory 提供靜態 Create，多載設計貼近官方，並加文件說明。

實施步驟：
1. 建立工廠與多載（見 Case #5）
2. 文件與註解引導
3. 教育與範例

關鍵程式碼/設定：
```csharp
// 無法：XmlWriter.Create(this XmlNode node) // 不支援
// 改用：
var xw = XmlWriterFactory.Create(node, cleanContent: false);
```

實際案例：原文提到 Extension Method 僅支援 instance，不支援 static。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：無法擴充 static，體驗落差
- 改善後：以工廠彌補
- 改善幅度：體驗接近預期（定性）

Learning Points（學習要點）
核心知識點：
- 語言限制與替代設計
- 工廠類的角色
技能要求：
- 必備技能：C# 語言基礎
- 進階技能：API 設計折衷
延伸思考：
- 若日後支援 static 擴充可回遷
- 以 DI 抽象建立點
Practice Exercise（練習題）
- 基礎練習：撰寫工廠+文件（30 分）
- 進階練習：包裝 NuGet 並撰說明（2 小時）
- 專案練習：內部導入替代 API（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：體驗相近
- 程式碼品質（30%）：簡潔清晰
- 效能優化（20%）：零額外成本
- 創新性（10%）：設計折衷

---

## Case #15: 避免文字往返（Text→Parse）造成的效能與風險

### Problem Statement（問題陳述）
業務場景：過去流程為 Writer→StringBuilder→Parse 回 DOM，常見於局部更新或 XSLT 轉換。
技術挑戰：中介字串增加 CPU/記憶體、錯誤點增多。
影響範圍：效能不佳、錯誤率高。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 不知 DOM 可直接作 Writer 目的地。
2. 習慣性使用字串中介。
3. 缺乏替代方案模板。
深層原因：
- 架構層面：資料流未最佳化。
- 技術層面：API 知識不足。
- 流程層面：欠缺效能意識。

### Solution Design（解決方案設計）
解決策略：直接用 AppendChild Writer 寫入 DOM，將中介字串完全移除，減少兩次轉換。

實施步驟：
1. 改寫輸出流向（見 Case #1/#2）
2. 建立共用輔助方法
3. 實測與回歸

關鍵程式碼/設定：
```csharp
using (var xw = targetNode.CreateNavigator().AppendChild())
{
    // 直接寫入 DOM，無需 StringBuilder
}
```

實際案例：原文多次強調避免「輸出成 Text 再 parse 回去」的蠢事。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：兩次轉換（序列化+解析）
- 改善後：零中介轉換
- 改善幅度：移除兩個昂貴步驟（定性）

Learning Points（學習要點）
核心知識點：
- 直接寫 DOM 的好處
- 減少中介帶來的穩定性
技能要求：
- 必備技能：XmlWriter
- 進階技能：效能剖析
延伸思考：
- 監控 GC/配置下降情況
- 以測試防止回歸為字串中介
Practice Exercise（練習題）
- 基礎練習：移除一段 StringBuilder 中介（30 分）
- 進階練習：量測前後時間/配置（2 小時）
- 專案練習：掃描並消除專案中此反模式（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：行為不變
- 程式碼品質（30%）：清爽
- 效能優化（20%）：顯著減少轉換
- 創新性（10%）：檢測工具

---

## Case #16: 以 XmlNodeReader 做為輸入，AppendChild Writer 做為輸出之純記憶體管線

### Problem Statement（問題陳述）
業務場景：在記憶體中完成 XML 輸入與輸出處理，不需落地檔案；例如 Transform 或過濾。
技術挑戰：如何以 Reader 讀取 XmlDocument 並以 Writer 寫入另一 XmlDocument。
影響範圍：I/O 依賴降低，處理效率提升。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Reader/Writer 皆可針對記憶體運作。
2. 易忽略 XmlNodeReader 與 AppendChild 的搭配。
3. 傳統偏向檔案流。
深層原因：
- 架構層面：全記憶體處理管線未普及。
- 技術層面：對 API 搭配不熟。
- 流程層面：缺少樣板。

### Solution Design（解決方案設計）
解決策略：以 XmlNodeReader 包裹輸入 XmlDocument，輸出側以 AppendChild Writer 承接，形成 Reader→Writer 全記憶體流。

實施步驟：
1. 準備輸入 Reader
- 實作細節：new XmlNodeReader(inputDoc)
2. 準備輸出 Writer
- 實作細節：output.CreateNavigator().AppendChild()
3. 處理/轉換
- 實作細節：XSLT 或自訂過濾

關鍵程式碼/設定：
```csharp
XmlDocument input = ...;
XmlDocument output = new XmlDocument();

using (XmlReader reader = new XmlNodeReader(input))
using (XmlWriter writer = output.CreateNavigator().AppendChild())
{
    // 例如直接複製或套 XSLT:
    // xslt.Transform(reader, writer);
}
```

實際案例：原文評論提及可用 XmlNodeReader 作為輸入。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：依賴檔案/字串中介
- 改善後：純記憶體
- 改善幅度：I/O 成本消除（定性）

Learning Points（學習要點）
核心知識點：
- XmlNodeReader 與 AppendChild 的搭配
- 記憶體內處理最佳實務
技能要求：
- 必備技能：Reader/Writer
- 進階技能：XSLT/轉換管線
延伸思考：
- 與管線/串流 API 結合
- 大型資料需注意記憶體峰值
Practice Exercise（練習題）
- 基礎練習：Reader→Writer 複製子樹（30 分）
- 進階練習：加入節點過濾（2 小時）
- 專案練習：打造可配置的記憶體管線（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出正確
- 程式碼品質（30%）：流向清楚
- 效能優化（20%）：無中介 I/O
- 創新性（10%）：可配置性

---

## Case #17: 發掘「藏在 XPathNavigator」的內建能力並知識擴散

### Problem Statement（問題陳述）
業務場景：團隊多年使用 XML，卻不知 .NET 2.0 已可直接在 DOM 上取得 Writer，錯失效能與簡化機會。
技術挑戰：API 被動可見度低、知識傳遞不足。
影響範圍：重複造輪子、依賴外部庫。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 功能不在 XmlWriter 類別頁面醒目處。
2. 文件與部落格分散。
3. 經驗慣性。
深層原因：
- 架構層面：技術雷達未更新。
- 技術層面：缺少 API 全貌地圖。
- 流程層面：知識分享不足。

### Solution Design（解決方案設計）
解決策略：將「XmlNode.CreateNavigator().AppendChild」納入團隊指北與模板，並以範例教學與代碼檢查推廣。

實施步驟：
1. 建教案與範例碼
2. 納入 code review checklist
3. 內部分享/讀書會

關鍵程式碼/設定：
```csharp
// 教學範例核心
using (XmlWriter xw = node.CreateNavigator().AppendChild())
{
    // ...
}
```

實際案例：原文作者驚訝多年未發現，並分享來源。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：不知能直接寫 DOM
- 改善後：團隊普及此技巧
- 改善幅度：重複造輪子減少（定性）

Learning Points（學習要點）
核心知識點：
- API 發掘與知識管理
- 把隱蔽 API 拉成慣用法
技能要求：
- 必備技能：學習與整理
- 進階技能：內部布道
延伸思考：
- 建立技術雷達/週報
- 用 Linters 提醒反模式
Practice Exercise（練習題）
- 基礎練習：撰寫一篇內部 Wiki（30 分）
- 進階練習：做分享簡報（2 小時）
- 專案練習：導入 checklist 與範本（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：內容正確
- 程式碼品質（30%）：範例可用
- 效能優化（20%）：推廣對產出助益
- 創新性（10%）：分享形式

---

## Case #18: 直接嵌入十幾行共用程式碼（不包成 DLL）的散佈策略

### Problem Statement（問題陳述）
業務場景：僅需十幾行工廠/Adapter 程式碼，為避免建置繁瑣與授權問題，偏好直接貼入專案中使用。
技術挑戰：如何在不製作 DLL 的前提下，保持可重用與易散佈。
影響範圍：交付速度、授權合規、維護便利。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 程式碼短小、封裝簡單。
2. 外部套件治理成本高。
3. 授權不明風險。
深層原因：
- 架構層面：小片段內嵌成本最低。
- 技術層面：避免跨專案依賴。
- 流程層面：散佈與回饋機制。

### Solution Design（解決方案設計）
解決策略：將 XmlWriterFactory（與可選 Adapter）以原始碼形式置於共用資料夾；以 README 註明用法與回饋方式（如回報使用）。

實施步驟：
1. 建立共用檔案
2. 加入註解與示例
3. 在多專案複用

關鍵程式碼/設定：
```csharp
// 放入 Shared/XmlWriterFactory.cs，並附 README 用法
// 使用端只需呼叫 XmlWriterFactory.Create(node, ...)
```

實際案例：原文建議「CODE 才十幾行，直接貼進去用」。
實作環境：.NET 2.0+、C#
實測數據：
- 改善前：建置/發佈 DLL 麻煩
- 改善後：內嵌即用，散佈快速
- 改善幅度：交付速度提升（定性）

Learning Points（學習要點）
核心知識點：
- 小工具以原始碼散佈
- 授權與回饋溝通
技能要求：
- 必備技能：專案結構管理
- 進階技能：多專案共用策略
延伸思考：
- 日後轉 NuGet 的時機
- 版本控管與變更紀錄
Practice Exercise（練習題）
- 基礎練習：將工廠檔案加入兩個專案使用（30 分）
- 進階練習：撰寫 README 與範例（2 小時）
- 專案練習：建立共享程式碼目錄與 pipeline（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可直接使用
- 程式碼品質（30%）：註解清晰
- 效能優化（20%）：零額外開銷
- 創新性（10%）：散佈策略

---

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 6, 7, 8, 9, 11, 12, 14, 18
- 中級（需要一定基礎）
  - Case 1, 2, 3, 5, 10, 16, 17
- 高級（需要深厚經驗）
  - Case 4, 13, 15（涉及相容性、樣板自動化與效能策略）

2) 按技術領域分類
- 架構設計類：Case 5, 8, 14, 17, 18
- 效能優化類：Case 1, 2, 10, 15, 16
- 整合開發類：Case 3, 4, 6, 7, 9, 12
- 除錯診斷類：Case 11, 13
- 安全防護類：無直接案例（可在 Case 2、16 延伸討論外部資源安全）

3) 按學習目標分類
- 概念理解型：Case 10, 14, 17
- 技能練習型：Case 1, 6, 7, 11, 12, 16
- 問題解決型：Case 2, 3, 4, 5, 8, 9, 13, 15, 18
- 創新應用型：Case 5, 16, 18

案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 10（理解 Reader/Writer vs DOM 的本質與效能）
  - Case 1（核心技能：直接寫入 DOM 節點）
  - Case 11（資源釋放基本功）
  - Case 12（常見寫入模式：屬性、CDATA）
- 依賴關係：
  - Case 2 依賴 Case 1（需會 AppendChild Writer）
  - Case 16 依賴 Case 1 與 Case 10（記憶體管線）
  - Case 5、8 依賴 Case 1（封裝與 API 設計）
  - Case 4、13 依賴 Case 1（Adapter 與覆寫技巧）
  - Case 15 依賴 Case 1、2（去中介最佳化）
- 完整學習路徑：
  1) Case 10 → 了解選擇 Reader/Writer 的原因
  2) Case 1 → 學會直接對 DOM 寫入
  3) Case 11、12 → 穩固基本操作與品質
  4) Case 6、7 → 控制覆寫語意與格式設定
  5) Case 8、5 → 打造一致且易用的工廠 API
  6) Case 2、16 → 建立純記憶體轉換管線（含 XSLT）
  7) Case 9 → 將既有專案低風險導入
  8) Case 15 → 系統性移除字串中介提升效能
  9) Case 4、13 → 需要相容時的 Adapter 與覆寫策略
  10) Case 3、18、17 → 完成替代、散佈與知識擴散戰術

以上每個案例皆從原文中提到的問題、根因、解法與效益（或定性指標）萃取並重構，附上可直接實作的核心程式碼與練習規劃，可作為實戰教學與評估素材。