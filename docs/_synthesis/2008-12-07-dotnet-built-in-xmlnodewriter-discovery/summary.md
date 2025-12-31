---
layout: synthesis
title: "原來 .NET 早就內建 XmlNodeWriter 了..."
synthesis_type: summary
source_post: /2008/12/07/dotnet-built-in-xmlnodewriter-discovery/
redirect_from:
  - /2008/12/07/dotnet-built-in-xmlnodewriter-discovery/summary/
postid: 2008-12-07-dotnet-built-in-xmlnodewriter-discovery
---

# 原來 .NET 早就內建 XmlNodeWriter 了...

## 摘要提示
- 問題背景: 作者長期用 XmlNodeWriter 處理在記憶體中以 XmlWriter API 寫入 XmlNode 的需求
- 官方限制: 內建 XmlWriter 主要寫到檔案或 TextWriter，直接寫回 XmlNode 不便
- 舊解法缺口: 早期社群版 XmlNodeWriter 已失傳（gotdotnet 關站），尋覓無門
- 內建替代: .NET 2.0 起其實可用 XmlNode.CreateNavigator().AppendChild() 取得可寫入 XmlNode 的 XmlWriter
- 範例應用: 以 AppendChild() 讓 XSLT Transform 直接輸出至 XmlDocument，省去字串再解析
- 自製封裝: 作者用「延長線」做法包成 XmlNodeWriter 類別，將所有抽象方法代理到內部 XmlWriter
- 代碼負擔: 繼承 XmlWriter 需補齊數十個抽象成員，雖可行但顯得冗長
- 工廠設計: 改以 XmlWriterFactory 靜態 Create(XmlNode, …) 封裝，乾淨直接且重用既有 XmlWriterSettings
- 語言限制: C# Extension Method 不支援 static，無法直接擴充 XmlWriter.Create
- 開源分享: 作者提供輕量實作，歡迎直接貼用並回饋使用情形

## 全文重點
作者回顧自己長期以 XmlNodeWriter 解決「用 XmlWriter API 直接寫入 XmlNode」的需求。由於內建 XmlWriter 的預設輸出目標多是檔案或 TextWriter，若要在記憶體中更新 XmlDocument 的部分節點，常得走「寫成字串再解析回 XmlNode」的笨路。早年社群曾有好用的 XmlNodeWriter 類別，但隨 gotdotnet 關閉已難以取得。

在搜尋過程中，作者於 Microsoft XmlTeam 的部落格留言發現：.NET 2.0 起其實已可透過 xmlNode.CreateNavigator().AppendChild() 取得一個可寫回指定 XmlNode 的 XmlWriter。這等於隱藏版的「內建 XmlNodeWriter」，亦能滿足像是將 XSLT 轉換結果直接輸出到 XmlDocument 的情境，省去中間字串化與重解析的成本與醜陋流程。

作者先以繼承 XmlWriter 的方式自製 XmlNodeWriter，內部包一個由 AppendChild() 取得的 XmlWriter，並把所有抽象方法/屬性全數代理出去，證實可行但代碼冗長。為了讓呼叫端更乾淨，接著改採工廠模式，實作 XmlWriterFactory 靜態 Create(XmlNode, bool cleanContent, XmlWriterSettings) 多載：可選擇是否清空節點內容，必要時再用 XmlWriter.Create 包裝 settings，便於沿用原生 XmlWriter 的設定與使用體驗。由於 C# 的擴充方法無法擴充靜態方法，無法直接「加掛」到 XmlWriter.Create，因此以獨立工廠類別折衷。

最終只需把原程式碼中取得 XmlWriter 的那行改用 XmlWriterFactory.Create(node, …) 即可，其餘輸出邏輯維持不變。作者分享此輕量實作，鼓勵讀者直接貼到專案中使用，亦歡迎回饋與支持。

## 段落重點
### 緣起與需求：XmlWriter 與 XmlDocument 的落差
作者長期處理 XML，偏好以高效的 XmlReader/XmlWriter 避免大型 DOM 帶來的效能問題。但在實務上，常需要保留 XmlDocument 的可操作性，同時以 XmlWriter 的簡潔 API 產生複雜節點內容。內建 XmlWriter 主要輸出到檔案或文字流，使得直接「寫回節點」的需求難以優雅達成，過去只好依賴社群提供的 XmlNodeWriter。

### 舊版 XmlNodeWriter 用法與遺失
社群版 XmlNodeWriter 可接受 XmlNode 與是否清空內容的參數，透過 Writer API 直接把新節點、屬性、CDATA 寫到指定 XmlNode 上，避免先轉成字串再解析回去。可惜其原站 gotdotnet 關閉後失聯，讓依賴者面臨升級與維護困境。

### 發現內建替代：CreateNavigator().AppendChild()
經由 Microsoft XmlTeam 部落格留言提示，.NET 2.0 其實提供了等效能力：對任一 XmlNode 呼叫 CreateNavigator().AppendChild()，即可取得一個能把輸出直接附加到該節點的 XmlWriter。這也讓如 XSLT.Transform 可直接寫入 XmlDocument 成為可能，消除中間字串暫存與解析，不僅更優雅也更有效率。

### 自製 XmlNodeWriter：代理「延長線」的權衡
作者先嘗試打造同名 XmlNodeWriter 類別：內部持有由 AppendChild() 取得的 XmlWriter，並將 Close、Flush、LookupPrefix 等所有抽象方法/屬性逐一代理。雖能完全回復舊 API 體驗且可正常運作，但需要補上二十多個成員，代碼雖單純卻顯冗長，不符作者對整潔代碼的偏好。

### 工廠化封裝：XmlWriterFactory.Create 多載
為減少樣板碼與提升可用性，作者改採工廠類別 XmlWriterFactory：提供 Create(XmlNode)、Create(XmlNode, bool cleanContent)、Create(XmlNode, bool, XmlWriterSettings) 等多載。內部先視需求清空節點，再用 CreateNavigator().AppendChild() 取得 Writer；若提供 settings，則以 XmlWriter.Create 進一步包裝，沿用原生設定行為。此設計保留原生 XmlWriter 的使用習慣與彈性，呼叫端只需替換取得 Writer 的那行即可。

### 語言限制與結語：實用小工具的分享
作者指出 C# 擴充方法無法套用於靜態方法，故無法直接擴充 XmlWriter.Create 只好使用獨立工廠。最終提供精簡可貼用的程式碼，無授權門檻，鼓勵讀者自由使用與散布，只希望告知使用情況並以點擊支持部落格。整篇文章重點在揭示 .NET 早已內建可寫入 XmlNode 的 Writer 入口，以及如何以小改造將其封裝為更易用的工廠方法。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- 基本 XML 結構與命名空間觀念
- .NET 中 XmlDocument、XmlNode、XmlReader/XmlWriter 的基本用法與差異
- C# 物件導向概念（繼承、抽象方法、封裝）
- XSLT 與 .NET 的轉換 API 基礎（XslCompiledTransform）
- IDisposable/using 模式與資源釋放

2. 核心概念：本文的 3-5 個核心概念及其關係
- XmlWriter 面向：以串流方式高效輸出 XML，但預設只寫到檔案/文字流
- XmlDocument/XmlNode 面向：樹狀結構便於修改，但在大量/複雜輸出時較繁瑣
- XmlNodeWriter 需求：希望用 XmlWriter API 直接寫入既有 XmlNode（避免中間文字化再 Parse）
- 內建替代做法：XmlNode.CreateNavigator().AppendChild() 可取得寫入該節點的 XmlWriter
- 封裝與工廠：以包裝類或 Factory 方法統一取得寫入 XmlNode 的 XmlWriter（可選是否清空與套用 XmlWriterSettings）

3. 技術依賴：相關技術之間的依賴關係
- XmlDocument 包含 XmlNode
- XmlNode 可建立 XPathNavigator（CreateNavigator）
- XPathNavigator.AppendChild() 產生指向該節點的 XmlWriter
- XSLT 可將輸出導向任意 XmlWriter（因此可直接產生到 XmlDocument/XmlNode）
- XmlWriterSettings 可包裝既有 XmlWriter 以調整縮排、編碼、大小寫等輸出行為

4. 應用場景：適用於哪些實際場景？
- 在既有 XmlDocument 的某一節點下，以 XmlWriter 高效產生複雜子樹
- 以 XSLT 將來源 XmlNode 轉換，直接輸出到另一個 XmlDocument/XmlNode（全程 in-memory）
- 需要可控的輸出格式（透過 XmlWriterSettings）又要落點在 XmlNode 的場景
- 在序列化或中介層生成 XML 片段後，插入到既有 DOM 結構

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 XmlDocument vs XmlReader/XmlWriter 的差異與使用情境
- 實作：用 XmlWriter 產生簡單 XML 到 StringWriter/File
- 練習：使用 XmlDocument 載入/修改節點
- 嘗試：在某節點上呼叫 CreateNavigator().AppendChild()，用 XmlWriter 寫入子節點

2. 進階者路徑：已有基礎如何深化？
- 熟悉 XmlWriterSettings（縮排、字元檢查、命名空間處理）
- 以 XslCompiledTransform.Transform 將輸出導向 XmlWriter，驗證可直接寫入 XmlDocument
- 封裝 Factory：撰寫靜態 Create(XmlNode, bool clean, XmlWriterSettings) 以統一取得 Writer
- 了解資源管理：using/Close/Flush 的差異與實務

3. 實戰路徑：如何應用到實際專案？
- 建立 XML 組裝模組：以 Factory 取得指向目標節點的 XmlWriter 並生成內容
- 以單元測試驗證生成結果與命名空間正確性
- 效能比較：XmlDocument 直接操作 vs XmlWriter 寫入節點的耗時與記憶體
- 在資料轉換流程中導入 XSLT→XmlWriter→XmlNode 的 in-memory pipeline

### 關鍵要點清單
- XmlWriter 與 XmlDocument 的取捨: XmlWriter 適合高效順序輸出，XmlDocument 便於任意修改與讀取 (優先級: 高)
- 直接寫入 XmlNode 的方法: 透過 node.CreateNavigator().AppendChild() 取得可寫回該節點的 XmlWriter (優先級: 高)
- 避免字串中轉與重解析: 以 Writer 直寫 Node 可省去 StringBuilder 與再 Parse 的成本與風險 (優先級: 高)
- 清空目標節點選項: 寫入前依需求 node.RemoveAll()，避免殘留舊內容 (優先級: 中)
- XSLT 輸出到 XmlNode: 使用 XslCompiledTransform.Transform 輸出到上述 Writer，實現全程 in-memory 轉換 (優先級: 高)
- XmlWriterSettings 的應用: 以 XmlWriter.Create(innerWriter, settings) 疊加設定（縮排、驗證、編碼）(優先級: 中)
- Factory 模式封裝: 建立 XmlWriterFactory.Create(XmlNode, bool, XmlWriterSettings) 統一入口 (優先級: 中)
- Wrapper/Delegation 實作成本: 直接繼承 XmlWriter 需實作多個抽象成員，維護成本高，宜以 Factory 簡化 (優先級: 中)
- 資源釋放與 using: 取得的 XmlWriter 需正確 Close/Dispose，確保游標狀態與緩衝寫入完成 (優先級: 高)
- 命名空間處理: 使用 WriteStartElement/WriteAttributeString 時留意命名空間與前綴（可配合 LookupPrefix）(優先級: 中)
- 讀寫混用策略: 先以 DOM 定位節點、再以 Writer 生成複雜內容，結合雙方優勢 (優先級: 高)
- 例外處理與驗證: 在寫入前後驗證 XML 完整性，捕捉無效名稱或未閉合標籤等錯誤 (優先級: 中)
- 版本與 API 位置認知: AppendChild 入口藏於 XPathNavigator（CreateNavigator）而非 XmlWriter 本身 (優先級: 中)
- 可測性設計: 把寫入邏輯封裝為方法，注入 XmlNode/Writer，便於單元測試與替身 (優先級: 中)
- 效能觀測: 在大型 XML 或高頻生成場景，度量 Writer-to-Node 與純 DOM 操作的效能差異 (優先級: 中)