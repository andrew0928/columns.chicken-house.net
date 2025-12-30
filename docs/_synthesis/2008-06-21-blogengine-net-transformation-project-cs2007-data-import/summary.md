---
layout: synthesis
title: "[BlogEngine.NET] 改造工程 - CS2007 資料匯入"
synthesis_type: summary
source_post: /2008/06/21/blogengine-net-transformation-project-cs2007-data-import/
redirect_from:
  - /2008/06/21/blogengine-net-transformation-project-cs2007-data-import/summary/
---

# [BlogEngine.NET] 改造工程 - CS2007 資料匯入

## 摘要提示
- 搬站動機: 由 CS2007 遷移到 BlogEngine.NET，為補齊遺漏資料而自行重寫匯入流程。
- 既有工具限制: 官方 BlogML 匯入器以 Web Service 單筆呼叫、不開源且欄位不足，無法滿足需求。
- 自行實作: 參考 .asmx 實作，改寫成 .ashx 讀取 App_Data 中的 BlogML，兩層迴圈完成 90% 匯入。
- 補強項目: 文章計數、留言詳細資訊、舊新 ID 對應、網址修正、Modified Date 等缺陷修正。
- CS 隱藏屬性: 解析 cs_posts 的 PropertyNames/PropertyValues 自行解碼匿名留言資訊。
- 資料導出: 利用 SQL2005 Management Studio 將查詢結果直接輸出為 XML，減少自寫工具。
- 圖檔連結轉換: 以正則表達式批次將 CS 絕對路徑改為 BlogEngine 的 image.axd/file.axd。
- 站內連結: 因新 ID 需待匯入後產生，採兩階段處理，先建舊新 ID 對照再回填連結。
- URL 樣式差異: 處理 CS 多種 URL 與 BlogEngine 單純 ID/Slug 形式的對映。
- 舊連結轉址: 自寫 HttpHandler (CSUrlMap) 擷取舊 PostID，查表轉向新網址，確保外部舊連結不中斷。

## 全文重點
作者從 CS2007 遷移到 BlogEngine.NET，使用「CS2007 → BlogML → BlogEngine」雖可轉入約九成內容，但仍遺漏關鍵資訊（例如原始 PostID、PageView 計數與留言細節），為避免日後無法補救，決定自行重寫匯入流程。由於 BlogEngine 的 BlogML 匯入器不開源且以 Web Service 單筆呼叫，擴充成本高，作者改以參考其 .asmx 實作，寫成一個 .ashx 處理器，直接從 App_Data 讀 BlogML，逐篇文章與留言處理，快速完成既有九成資料的導入。

接著作者列出需補強的資訊：文章瀏覽計數、留言詳細資料、舊新 PostID 對照與各類網址修正，以及修補原程式的 Modified Date 錯誤。為補齊 BlogML 未涵蓋的留言匿名者、IP 等資訊，需從 CS2007 資料庫中的 PropertyNames/PropertyValues 解碼。該欄位以序列化大字串儲存屬性名稱、型別與起迄位置，作者撰寫解析程式將這些資訊拆解出來，並運用 SQL Server 2005 Management Studio 的 FOR XML AUTO 將查詢結果匯出成 XML，再以程式抽取所需屬性寫回補強資料，完成第一階段資料蒐整。

在網址修正部分，作者先處理最單純的圖檔與附件連結。CS2007 採絕對路徑，而 BlogEngine 以 image.axd/file.axd HttpHandler 提供檔案服務，且歷經網域變動、相對/絕對路徑混用與需避開內建路由等複雜情形，因此作者透過正則表達式彈性配對各種來源形式，精準抓取 /blogs/chicken/ 之後的路徑並重寫為 axd 參數。雖後來發現少數 RSS 之類路徑未涵蓋，便以手動補正收尾。

站內連結較為棘手，因為新文章的 ID 與最終網址需在匯入後才能確定，無法一次完成替換。作者採兩階段策略：第一次匯入時先建立舊（CS PostID）與新（BlogEngine GUID/Slug）的對照表，待所有文章完成匯入後，再回填替換內容中的站內連結。CS2007 的連結有多種格式（含日期/標題哈希/純 ID），作者以正則抓取 PostID，映射到 BlogEngine 的 post.aspx?id=GUID 或依 API 取回的 Slug 形成新連結。

為了讓外部世界既有的舊連結仍能順利到達新站文章，作者另寫一個 HttpHandler（CSUrlMap）攔截 /blogs/*.aspx 的請求，從各種可能 URL 中抓取 PostID，查表後發出伺服器端轉向或提示訊息，並處理 RSS 等特殊路徑。此舉確保搜尋引擎索引與他站引用的連結不中斷，順利完成搬遷中的「連結續航」。

整體而言，這次改造工程以少量自訂程式碼彌補了官方匯入工具的不足，包含隱藏屬性解析、資料補強、網址重寫與轉址，雖然均為繁瑣的細項，但最終在一週內完成資料與連結面的所有處理。作者預告下一篇將著重版面調整與與 FunP 推推王的整合，屬於較輕鬆的視覺與互動優化階段。

## 段落重點
### 專案背景與動機
作者搬家到 BlogEngine.NET 後，發現以 BlogML 匯入僅能轉入約九成資料，仍遺失原始 PostID、PageView 計數與留言細節等對後續維運與導引至關重要的欄位。由於這些資料一旦遺失就難以補回，因此決定主動重匯與補齊。官方匯入工具採 Web Service 單筆呼叫、未開源且欄位不足，若要擴充需同時改動客端與伺服端，工程繁瑣且效率不佳。作者因此選擇參考其 .asmx 內部實作，改以 .ashx 直接讀 BlogML 檔，逐篇文章與留言處理，快速完成主要匯入工作，並為後續自訂補強鋪路。

### 重新實作匯入流程
作者以 BlogEngine 的程式為藍本，撰寫一個 .ashx，從 App_Data 載入 BlogML，透過兩層迴圈處理所有文章與留言，達成原流程能完成的九成匯入內容。接著規劃需補強的五項：文章瀏覽數、留言詳細資訊、舊新 PostID 對照、所有內外部連結修正與原程式 Modified Date 錯誤。BlogEngine 的 Library 結構清晰，讓重寫成本降低，整體開發進度順利。此階段的目標是把可直接由 BlogML 取得的資料完整導入，為第二階段的資料補齊與連結修復提供基礎。

### CS2007 隱藏屬性解析與匯出
BlogML 未涵蓋匿名留言者名稱、URL、IP 等資訊，而這些被 CS2007 以序列化字串分別存放於 cs_posts 的 PropertyNames 與 PropertyValues。PropertyNames 以 Name:Type:Start:End: 連續描述欄位結構，對應到 PropertyValues 的子字串位置，例如 SubmittedUserName 與 TitleUrl 的值需依位置切割取出。作者撰寫解析程式進行反解，並利用 SQL Server 2005 Management Studio 的 FOR XML AUTO 將查詢結果導出為 XML，再以程式抽取所需欄位寫入補強資料，修正 BlogML 未正確呈現匿名留言資訊的問題，完成補齊留言細節的第一步。

### 圖檔與附件連結替換
CS2007 的圖檔/附件多為絕對路徑，且站點歷經網域更迭與早期相對路徑混用；BlogEngine 則以 image.axd/file.axd 的 HttpHandler 提供檔案服務。單純文字替換易誤傷或順序顛倒導致替換錯誤，作者改用正則表達式匹配各種來源網址（含 community/columns 網域與 /blogs/chicken/ 前綴），精準擷取實際檔案路徑並改寫為 axd 形式。同時避開內建路由如 rss.aspx 等，降低誤判風險。少數未涵蓋的古早路徑以手動修正補齊，確保內容中的媒體資源在新站可正確載入。

### 站內連結修正策略
站內連結需指向新站文章，但 BlogEngine 的最終網址（GUID/Slug）需在匯入後才確定，因此無法一次性替換。作者採兩階段策略：第一階段匯入時僅建立舊 CS PostID 與新 BlogEngine ID/Slug 的對照表；第二階段再回填替換文章內的站內連結。CS2007 存在多種 URL 形式（日期 + PostID、日期 + TitleHash、純 PostID），作者以正則抓取 PostID，映射到 BlogEngine 的 post.aspx?id=GUID 或使用 API 取得 Slug 組合新連結，最終完成全站站內連結的正確轉向。

### 舊站外部連結轉址
外部網站或搜尋引擎的舊連結無法直接修改，需在新站提供轉址機制。作者撰寫 CSUrlMap.cs HttpHandler，攔截 /blogs/*.aspx 請求，從路徑中解析出舊 PostID，查詢對照表取得新文章 ID 或網址，並以伺服器端轉向引導使用者至新頁面；對於 RSS 或不存在的 PostID 則提供相應回應與導回首頁。此機制確保外部連結不中斷，既維護使用者體驗也有助於搜尋引擎索引在搬站後的延續與收斂。

### 結語與後續計畫
整體搬遷歷時約一週，雖多為瑣碎工作，但透過自訂匯入器、欄位補齊、正則批次重寫與轉址處理，已完整解決資料層與連結層的問題。作者在本篇完成資料面與技術面的收攤，下一篇將專注於前端版面與互動設計，特別是與 FunP 推推王的整合，讓新站在內容已穩定落地後，提升使用者體驗與社群分發效果。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - .NET/C# 語言與 ASP.NET 基礎（.asmx Web Services、.ashx HttpHandler）
   - BlogEngine.NET 架構與 API、Web.config 設定（HttpHandlers）
   - Community Server 2007（CS2007）資料庫結構，特別是 cs_posts
   - SQL Server 2005 基本操作、以 FOR XML 匯出查詢結果
   - XML/BlogML 格式與欄位理解
   - Regular Expression（正規表達式）與網址規則
2. 核心概念：
   - 以 BlogML 為骨幹的資料匯入：利用 BlogML 作為中介格式，實作自訂匯入流程
   - 缺漏資料補齊：解析 CS2007 序列化屬性（PropertyNames/PropertyValues）以補齊匿名留言作者、IP、計數器等
   - 連結與資源修正：圖檔/附件路徑替換、站內連結兩階段（2-pass）重寫
   - 舊新 ID 對照表：建立 CS PostID 與 BlogEngine 新 GUID/Slug 的映射
   - 兼容與轉址：撰寫 HttpHandler（CSUrlMap）將各種舊 CS URL 轉向新 BlogEngine URL
3. 技術依賴：
   - BlogEngine 核心 Library 與其 Web.config 中的 image.axd/file.axd 處理鏈
   - SQL Server 2005 查詢與 FOR XML 匯出 → 產生中繼 XML
   - 正規表達式用於批次偵測/取代舊網址與抽取 PostID
   - .ashx 自訂匯入器以取代 .asmx Web Service 匯入（更有效率、可擴充欄位）
   - BlogEngine 提供的 API 生成新文章、取得 Slug、處理留言
4. 應用場景：
   - 從 CS2007 遷移到 BlogEngine.NET 的整站資料搬移
   - 保留歷史資料完整性（計數器、留言細節、原始 PostID）
   - 維持 SEO 與外部連結可用性（301/302 轉址與站內連結修正）
   - 大量內容平台搬遷時的規則化批次處理（Regex、兩階段處理）

### 學習路徑建議
1. 入門者路徑：
   - 了解 BlogML 結構與 BlogEngine.NET 基本匯入流程
   - 熟悉 CS2007 → BlogML → BlogEngine 的基本轉換管線
   - 練習 SQL Server FOR XML 匯出與簡單 Regex 匹配
2. 進階者路徑：
   - 研究 CS2007 cs_posts 的 PropertyNames/PropertyValues 序列化格式並撰寫解析程式
   - 掌握 BlogEngine 的 HttpHandler 設定，理解 image.axd/file.axd 的存取模式
   - 設計兩階段（2-pass）站內連結修正流程與舊新 ID 對照表建置
3. 實戰路徑：
   - 撰寫自訂 .ashx 匯入器：逐篇文章/留言處理、補齊缺漏欄位、修正時間戳與計數器
   - 建立 Regex 規則集：圖檔/附件路徑、CS 多種文章 URL、RSS 與例外路由
   - 開發 CSUrlMap HttpHandler：解析舊網址（含多種格式）、查映射表、執行轉址
   - 進行端對端驗證：樣本抽查、批次日誌、外部連結實測、SEO 檢視

### 關鍵要點清單
- BlogML 為中介格式：以 BlogML 承載大部分文章與留言資料，但需擴充以補齊缺漏欄位 (優先級: 高)
- 自訂 .ashx 匯入器：比 .asmx Web Service 匯入更高效率、可控制欄位與流程 (優先級: 高)
- CS2007 序列化屬性解析：解析 PropertyNames/PropertyValues 以取得匿名留言者、IP、額外欄位 (優先級: 高)
- 舊新 ID 對照表：建立 CS PostID 與 BlogEngine GUID/Slug 映射，支援站內連結修正與轉址 (優先級: 高)
- 兩階段連結修正：先匯入建立映射，再以第二階段批次替換站內連結 (優先級: 高)
- 圖檔/附件路徑替換：將 CS 絕對路徑改為 BlogEngine 的 image.axd/file.axd 模式 (優先級: 中)
- 多來源網址正規化：處理分家前/後域名、相對路徑、內建路由例外（如 rss.aspx） (優先級: 中)
- 正規表達式策略：使用精準 Regex 抽取 PostID 與匹配替換，避免覆寫與誤傷 (優先級: 高)
- SQL FOR XML 匯出：以 SQL Server 2005 FOR XML 產生中繼 XML，減少一次性開發成本 (優先級: 中)
- BlogEngine API 運用：透過核心 API 建立文章、留言、取得 Slug、處理計數與時間 (優先級: 中)
- 計數器與時間戳修正：補齊 PageViewCount、Modified Date 等在 BlogML/匯入器缺漏的資訊 (優先級: 中)
- CS 多種 URL 支援：支援 /archive/日期/ID.aspx、/archive/日期/TitleHash.aspx、/blogs/ID.aspx 等 (優先級: 高)
- 轉址 HttpHandler（CSUrlMap）：攔截舊 CS URL，解析 ID，查映射表並轉向新 URL (優先級: 高)
- 測試與回溯：小量多次測試、使用日誌核對遺漏（如特例的 rss 與內建路由） (優先級: 中)
- 工具輔助：活用 RegexLib 測試與驗證 Regex、管理規則複雜度 (優先級: 低)