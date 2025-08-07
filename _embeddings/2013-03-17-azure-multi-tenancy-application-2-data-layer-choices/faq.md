# [Azure] Multi-Tenancy Application #2 ─ 資料層的選擇

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 對於大規模 Multi-Tenancy 應用，作者最推薦哪一種資料切割方式？為什麼？
Shared Schema。Separated DB 與 Separated Schema 都必須為每個租戶建立獨立的 Database 或 Table，不但需要在執行期動態產生結構、增加維運複雜度，還會受限於 SQL Server 本身的物理上限 (Database 與 Database Object 數量)。Shared Schema 則只要空間與效能允許，就沒有這些硬性限制，對數量動輒上萬、上十萬的租戶更為合適。

## Q: SQL Server 2012 單一 Instance 理論上最多可以建立多少個資料庫 (Database)？
32,767 個。

## Q: 若採用「一租戶一資料庫」(Separated DB) 架構，理論上最多能支援多少租戶？
約三萬多個租戶，因為每個租戶需要一個 Database，而 SQL Server 單一 Instance 的上限是 32,767 個 Database。

## Q: 在「Separated Schema」模式下，假設每個租戶平均使用 5,000 個資料庫物件，一個資料庫最多可服務多少租戶？
大約 400,000 個租戶。SQL Server 單一資料庫可容納 2,147,483,647 個 objects，用 2 G 物件數 ÷ 5,000 ≒ 400K。

## Q: 採用 Shared Schema 時最需要面對的技術挑戰是什麼？
隨租戶數增加，單一 Table 可能累積到上億筆資料；索引維護成本高、查詢變慢。如果沒有良好的資料庫最佳化與索引設計，效能會急遽下降。

## Q: Azure Table Storage 的 PartitionKey／RowKey 設計對 Multi-Tenancy 有何優勢？
1. 同一 Partition (通常可對應單一租戶) 會被放在同一 Storage Node，利用快取與資料在地化獲得最佳效能。  
2. Azure 會自動依 PartitionKey 將資料分散到多節點，隨負載動態調整，提供高度的橫向延展性與自動負載平衡。

## Q: 相較於傳統 RDBMS，使用 Azure Table Storage 時必須接受哪些主要限制？
• 只能依 PartitionKey + RowKey 排序，無法對其他欄位索引或排序。  
• 不支援 JOIN、COUNT 等複雜查詢，報表統計需自行在程式端處理。  
• 若查詢條件未含 PartitionKey，效能會大幅下降。  
• 分頁、排序、彙總等功能須自行在應用程式實作。

## Q: 儘管有上述限制，作者仍推薦考慮 Azure Table Storage 的原因是什麼？
Azure Table Storage 具備極佳的水平擴充能力，可輕易儲存與處理巨量資料；其 Partition 機制天生就適合做租戶隔離。對需要上萬甚至數十萬租戶的 SaaS 服務而言，它以犧牲部分關聯式查詢功能換得更好的擴充性與效能，整體仍十分划算。

## Q: 文章中三種資料層設計在 Scale-Out 方面各有何特性？
• Separated DB：最容易直接做 Scale-Out，但執行多個 DB 浪費資源，且共用資料查詢困難。  
• Separated Schema：較易受到 SQL Server 物件數限制，Scale-Out 能力介於兩者之間。  
• Shared Schema：執行負擔最小，但難以透過資料庫本身水平切割，需依賴 Partition 或分片技術。

## Q: 作者對後續內容有什麼計畫？
下一篇將示範實際程式碼，說明如何以 Azure Table Storage 實作 Multi-Tenancy Application 的資料層。