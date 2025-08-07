# [Azure] Multi-Tenancy Application #2 ‑ 資料層的選擇

## 摘要提示
- 資料切割模式: Multi-Tenancy 常見三種資料切割方式為 Separated DB、Separated Schema 與 Shared Schema。
- 容量瓶頸: SQL Server 每實例僅能建立 32,767 個 Database，對 Separated DB 架構形成用戶數硬上限。
- 物件上限: Separated Schema 雖可撐到約 40 萬租戶，但仍受單庫 20 億 objects 限制。
- Shared Schema 優勢: 不受 Database 與 objects 數量限制，只要硬體資源足夠即可橫向擴充。
- 效能對比: Separated DB 容易 Scale-Out 卻浪費資源；Shared Schema 執行效率佳但需面對巨表優化。
- Partition 策略: 良好的 Partition 設計是突破單表龐大資料筆數瓶頸的關鍵。
- NoSQL 崛起: 為解決 RDBMS 天生限制，可考慮 Azure Table Storage 等 NoSQL 服務。
- PartitionKey/RowKey: Azure Table Storage 以雙鍵驅動資料分散與快取，是實作 Multi-Tenancy 的理想機制。
- 查詢限制: Azure Table Storage 缺乏多重索引與 JOIN，須以程式與平行查詢來彌補。
- 取捨原則: 系統須在查詢彈性與高延展性之間抉擇，巨量 SaaS 服務宜優先考慮 Shared Schema＋NoSQL。

## 全文重點
本文延續前篇設計討論，聚焦在 SaaS／Multi-Tenancy 應用的資料層選型。作者先引用 MSDN 提出的三類切割模型，並以「用戶數 5 萬、每戶 500 張表、10 萬筆資料」的情境做容量估算。結果顯示 Separated DB 受限於 SQL Server 單實例 32,767 個 database 的天花板，實務上僅適合租戶數極少的系統；Separated Schema 雖能提升至約 40 萬租戶，仍無法支撐面向大眾市場的服務，而且動態建立資料庫／資料表在維運與效能上都並非長久之計。Shared Schema 將所有租戶資料儲於同一結構，消弭了物件數量上限問題，但單表筆數極大帶來索引、查詢與維護挑戰，必須依賴精細的分割與調校手段。

接著作者從 Scale-Out 角度比較三者：Separated DB 由於資料已天然分散，對水平擴充最友善，但多實例管理與資源浪費明顯；Shared Schema 相反，計算成本最低，卻容易陷入單庫瓶頸，需要資料分區（Partition）或更進一步的資料服務拆分。傳統 RDBMS 強調一致性，對高擴充性設計造成桎梏，於是作者引介 NoSQL 思維，特別是 Azure Table Storage。該服務以 Key-Value 模型組合結構化表格語意，核心的 PartitionKey 與 RowKey 既提供唯一索引，也讓平台能自動依存取熱度跨節點重新分布資料，達到幾近無限的延展，極度契合租戶隔離需求。

文章並列舉 Azure Table Storage 的限制：無排序、缺乏二級索引、無 Join、Count、報表困難等；然而對比其高可用、高平行吞吐與低成本特性，在追求大規模租戶與巨量資料時，這些缺點往往可以藉由應用層計算、預聚合或快取策略補足。最終作者下結論：若租戶規模已超越傳統 RDBMS 所能承載，採 Shared Schema 搭配 Azure Table Storage 等 NoSQL 技術，是打造雲端 SaaS 的最佳方案，下一篇將示範實作細節。

## 段落重點
### 導言：設計理念與方案篩選
作者延續上一回合的設計概念，先回顧 MSDN 三種資料隔離模式，指出 Separated DB／Schema 本質只是過渡方案，僅當租戶規模在「幾十」量級時才具可行性；若 SaaS 服務面向的是上萬租戶市場，光靠動態建立資料庫或資料表就會碰到數量上限與維運複雜度，故本文將鎖定能長期支撐成長的 Shared Schema 與新型儲存技術作為討論重心。

### 能容納的用戶量限制
以 5 萬租戶、每租戶 500 張表等假設，對照 SQL Server 2012 上限可知：Separated DB 受制於 3.2 萬 database 天花板而提早出局；Separated Schema 雖能撐到約 40 萬租戶，但對以部門或家庭為單位的微型租戶仍顯不足；Shared Schema 則只受磁碟與效能限制，不會被物件數量卡住，在容量面最具彈性。

### 效能擴充（Scale-Out）的限制
Separated DB 因每租戶獨立資料庫，執行負擔大且資源浪費，但搬遷或複製資料庫即可水平擴充；Shared Schema 單庫最省資源，卻易產生超大表，引發索引調整、查詢延遲與跨租戶資料衝突風險，若需擴充通常得導入 Partition 或拆分服務，成本與技術門檻較高。故無論採哪種模式，都必須在資源利用率與擴充便利性之間取得平衡。

### RDBMS 之外的選擇：Azure Table Storage
為突破 RDBMS 天生的固定 Schema 與一致性負擔，作者介紹 NoSQL 與 Azure Table Storage。該服務將 Key-Value 儲存與表格 API 結合，透過 PartitionKey/RowKey 實現資料定位、熱區分散與自動負載均衡，非常適合拿來當作租戶隔離的切割維度。文章引述多篇技術文獻，解析其可線性擴充的原因，同時說明缺乏排序、索引與 Join 的限制，強調在設計時必須以查詢模式導向 Partition 策略。總結而言，Azure Table Storage 以成本低、延展性高彌補查詢靈活度的不足，是大型 Multi-Tenancy 應用值得考慮的核心資料層方案。