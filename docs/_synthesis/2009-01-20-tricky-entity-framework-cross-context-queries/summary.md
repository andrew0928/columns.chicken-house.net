---
layout: synthesis
title: "難搞的 Entity Framework - 跨越 Context 的查詢"
synthesis_type: summary
source_post: /2009/01/20/tricky-entity-framework-cross-context-queries/
redirect_from:
  - /2009/01/20/tricky-entity-framework-cross-context-queries/summary/
---

# 難搞的 Entity Framework - 跨越 Context 的查詢

## 摘要提示
- 大型模型挑戰: EF 在大型、複雜 schema 的專案中，面臨設計工具限制與跨 Context 查詢困難。
- 設計工具問題: 視覺化設計器易出小錯，常需手改 .edmx，影響開發效率。
- 模型切割動機: 為避免單一龐大 OR Mapping，需將模型切割為多個 .edmx 並模組化。
- 跨 Context 限制: LINQ/eSQL 無法直接跨 ObjectContext 查詢，Navigation Property 也受限。
- 多 Context 操作成本: 多個 ObjectContext 需分別 SaveChanges，協作複雜度提升。
- 官方建議參考: 來自 ADO.NET Team 的 Large Models 系列提供模型分割與重用策略。
- 核心解法線索: 透過單一 EntityConnection 在連線字串中合併多組 metadata 檔。
- 單一 Context 聚合: 以一個 ObjectContext 載入多組 .csdl/.ssdl/.msl，達成跨模型 eSQL 查詢。
- LINQ 使用方式: 需自行用 CreateQuery 生成 EntitySet，再進行 LINQ 查詢。
- 模組化落地: 新增模組不需重編其他模組，支持跨模組資料查詢與維運擴充。

## 全文重點
作者分享在研究 Entity Framework 與 Enterprise Library 的過程中，面對大型資料庫架構下的實務難題。雖然 EF 的設計理念不錯，但第一代工具仍有不少小問題，例如將 TABLE/VIEW 拉入模型、刪除再加入、或無法正確設定 VIEW 主鍵，常導致建置失敗，開發者不得不手動修改 .edmx。真正的痛點在於大型系統的 O/R Mapping：當資料庫 schema 複雜、表數量龐大（動輒上百個），單一 ER 模型與映射設定會變得不可維護，因此必須將模型適度切割成多個 .edmx 並以模組化封裝。

然而模型分割帶來三大問題：一是多個 ObjectContext 必須分別 SaveChanges；二是 LINQ to Entities 與 eSQL 無法跨 Context 進行 join 查詢；三是 AssociationSet 無法跨越 Context，導致不同 .edmx 的實體無法用 Navigation Property 導覽關聯。作者的實際需求包括：每個模組（含 .edmx 與邏輯）需封裝於獨立組件；不同模組的 EntitySet 能用 eSQL join；支援基本 LINQ；新增模組時不需重新編譯其他模組。

閱讀 ADO.NET Team Blog 的 Large Models 系列後，作者從 Part 2 的一段提示獲得關鍵解法：在執行階段透過一個 EntityConnection 的連線字串，於 Metadata 參數同時指定多組 .csdl/.ssdl/.msl，讓單一 ObjectContext 可以同時載入多個模型的中繼資料。如此，eSQL 可在單一 Context 內跨模型查詢；LINQ 則可先以 CreateQuery 產生 EntitySet 再進行查詢。此法使得模組化與跨模組查詢得以並存，也避免了重編譯依賴，最終解決作者長期以來的困擾。

## 段落重點
### 研究背景與工具抱怨
作者兩個月專注於 Entity Framework 與 Enterprise Library。後者入門相對容易，但 EF 因為架構宏大且仍是初版，學習與落地難度較高。EF 設計工具雖提升了映射工作的可視化體驗，但實務上常出現小問題，例如表或檢視重新加入後導致建置錯誤、VIEW 無法正確設定鍵、需手動調整 .edmx。這些瑕疵在大型專案中會被放大，拖慢開發節奏。作者指出，撇開工具瑕疵，EF 的概念與設計仍有其優點，但在現階段仍難與成熟 ORM 方案全面抗衡。

### 大型資料庫的本質問題
文章將「大型」定義為 schema 複雜、表與檢視繁多，而非資料量龐大。此類系統常因版本演進保留舊表且不斷加入新表，形成極其複雜的 ER 結構。所有 ORM 都需維護 O/R Mapping，若將上百個表集中在單一模型，維護極度困難且風險高。因此合理的策略是將模型切割成多個 .edmx，對應功能模組分而治之。然而，單純切割並非萬靈丹，會引出執行與查詢層面的新挑戰，特別是資料跨模組關聯的需求無可避免。

### 模型切割後的三大限制
將模型分散到多個 .edmx 後，會產生：1) 多個 ObjectContext 並存，狀態管理與交易邏輯變複雜，需分別 SaveChanges；2) 查詢層面，無論 LINQ to Entities 或 eSQL，都不支援跨 Context 的 join，造成跨模組查資料受阻；3) 關聯導覽方面，AssociationSet 無法跨 Context，意味不同 .edmx 的實體之間無法透過 Navigation Property 導覽，削弱了 EF 的關聯導向優勢。這三點在大型系統中都會成為阻礙，必須另尋辦法統一查詢層並維持模組自治。

### 實務需求與模組化目標
作者明確列出需求：一是配合模組化，將每個 .edmx 與其商業邏輯封裝為各自的 assembly；二是不同模組的 EntitySet 能以 eSQL 進行跨模組 join 查詢；三是保有基本 LINQ 能力；四是後續擴充新模組不需重編其他模組，以降低耦合與部署成本。這些條件反映出企業級系統在演進式維護、跨界面資料整合與持續交付上的實際要求，也限定了解法必須在執行期具備彈性聚合能力，而非編譯期綁定。

### 線索來源：官方 Large Models 系列
雖然 Large Models 兩篇文章多數內容超出作者當下需求，但 Part 2 的一段關鍵說明提供了突破口：在執行階段可以建立一個 ObjectContext，使用帶有 EntityConnectionString 的建構子，並在連線字串的 Metadata 參數同時指定多組中繼資料檔路徑，讓單一 Context 同時「認得」多個模型。這個技巧將拆分設計與執行期聚合分離，既保留了模型切割的可維護性，也創造了跨模型操作的可能，正中作者的痛點。

### 解法細節：合併多組 metadata
EF 的 EntityConnection 連線字串除了資料庫連線外，還包含 .csdl、.ssdl、.msl 的中繼資料位置。一般是單組檔案；而依據官方說法，可以在 Metadata 段落串接多組檔案清單。如此，建立單一 ObjectContext 時，即可載入多個 .edmx 對應的中繼資料集合。結果是：eSQL 能在同一 Context 內跨模型進行 join 等查詢；LINQ 雖無法直接跨 Context，但在此情境中可透過 CreateQuery 建立對應的 EntitySet 再進行 LINQ 查詢。這種做法達成了查詢整合，同時不破壞模組邊界。

### 成果與影響
透過合併 metadata 的連線字串技巧，作者解決了跨 Context 查詢的瓶頸，保有模組化封裝並支援跨模組 eSQL 與基本 LINQ。這也緩解了多 Context 帶來的交易與查詢複雜度問題，讓大型 schema 能以多模型管理、單 Context 查詢的方式取得平衡。此外，此法相容於增量式擴充：新增模組只需提供其 .edmx 對應的中繼資料，不必重編其他模組。作者以此作結，表示困擾多時的問題終於落地，後續應用細節將再分享。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - .NET 3.5 SP1 與 Visual Studio 2008 基本開發環境
   - Entity Framework v1 基礎觀念（ObjectContext、EntitySet、Navigation Property）
   - O/R Mapping 與 .edmx 檔結構（CSDL/SSDL/MSL）
   - LINQ to Entities 與 eSQL 基本使用
   - 連接字串與 EntityConnection 的概念

2. 核心概念：
   - 大型模型拆分：將龐大 schema 切成多個 .edmx 以便模組化與維護
   - 跨 Context 限制：LINQ/eSQL/Navigation 無法直接跨多個 ObjectContext
   - Metadata 併載：在單一 EntityConnection 的 Metadata 參數同時指向多組 CSDL/SSDL/MSL
   - 單一 ObjectContext 遍歷多模型：透過併載後的單一 Context 進行 eSQL JOIN
   - LINQ 的建置方式差異：跨模型時以 CreateQuery<T>() 明確對 EntitySet 開查詢

3. 技術依賴：
   - ObjectContext 依賴 EntityConnection
   - EntityConnection 依賴 Metadata Workspace（CSDL/SSDL/MSL）
   - eSQL/LINQ 查詢依賴於單一 Context 的可見模型範圍
   - Navigation/AssociationSet 侷限於定義所在的單一模型（.edmx）

4. 應用場景：
   - 大型資料庫（大量 Table/View、複雜 schema）的企業級應用
   - 模組化架構：各模組各自封裝 .edmx 與邏輯於獨立組件
   - 跨模組查詢：需要在不同 .edmx 的 EntitySet 之間做 JOIN
   - 增量擴充：新增模組時，不希望重建或重編譯既有模組

### 學習路徑建議
1. 入門者路徑：
   - 學會 EF v1 基本組件：ObjectContext、EntitySet、EntityConnection
   - 理解 .edmx 與 CSDL/SSDL/MSL 的角色與關係
   - 練習基本 LINQ to Entities 與 eSQL 查詢

2. 進階者路徑：
   - 練習將大型模型切割為多個 .edmx，理解其優缺點
   - 了解跨 Context 的限制（LINQ、eSQL、Navigation）
   - 學會手動調整 .edmx 與設計工具限制下的修正（如 View Key、重匯入問題）

3. 實戰路徑：
   - 建立可併載多組 Metadata 的 EntityConnection 連接字串
   - 以單一 ObjectContext 進行跨 .edmx 的 eSQL JOIN
   - 使用 CreateQuery<T>() 在單一 Context 下對多模型的 EntitySet 建查詢
   - 驗證 SaveChanges 流程簡化（相較多 Context 的多次保存）

### 關鍵要點清單
- 大型模型拆分：將巨量 schema 拆到多個 .edmx 以降低複雜度與編譯負擔 (優先級: 高)
- 跨 Context 限制：EF v1 不支援跨 Context 的 LINQ/eSQL/Navigation 操作 (優先級: 高)
- AssociationSet 範圍：關聯集無法跨 .edmx，因此 Navigation 無法跨模型 (優先級: 高)
- 多組 Metadata 併載：在 EntityConnection 的 Metadata 參數同時指定多組 CSDL/SSDL/MSL (優先級: 高)
- 單一 ObjectContext：用併載後的單一 Context 使 eSQL 可以跨多 .edmx 進行 JOIN (優先級: 高)
- LINQ CreateQuery：跨模型時以 CreateQuery<T>() 明確建立對目標 EntitySet 的 LINQ 查詢 (優先級: 高)
- SaveChanges 策略：多 Context 需多次 SaveChanges；合併後可由單一 Context 管控 (優先級: 中)
- 設計工具限制：VS2008 EF 設計器可能有重匯入失敗、View Key 指定受限等問題 (優先級: 中)
- 手動編修 .edmx：必要時直接修改 .edmx 以解決設計器無法處理的鍵與對應問題 (優先級: 中)
- 模組化封裝：每個模組封裝自己的 .edmx 與邏輯於獨立組件，便於維護與部署 (優先級: 中)
- 擴充不重編：新增模組時，透過併載 Metadata 避免重編舊模組 (優先級: 中)
- eSQL 與 LINQ 差異：eSQL 在併載後能跨模型 JOIN；LINQ 需明確指定查詢來源 (優先級: 中)
- 連接字串管理：EntityConnection 連接字串較長且易錯，需制定組裝與維護策略 (優先級: 低)
- 版本與路線圖：EF v1 能力有限，了解未來版本方向與限制有助風險控管 (優先級: 低)
- 參考資源：ADO.NET Team Blog「Working With Large Models In EF」Part 1/2 提供設計指引 (優先級: 中)