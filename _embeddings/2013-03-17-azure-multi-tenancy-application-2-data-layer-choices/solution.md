# [Azure] Multi-Tenancy Application #2 ─ 資料層的選擇

# 問題／解決方案 (Problem/Solution)

## Problem: Separated DB 方案無法支撐大量租戶

**Problem**:  
在傳統 RDBMS 上, 如果我們採用「每個租戶一個 Database」(Separated DB) 來隔離資料, 當 SaaS 服務的租戶數成長到數萬甚至數十萬時, 會面臨無法再建立新 DB 的困難, 造成服務無法擴充。

**Root Cause**:  
1. SQL Server 每個 Instance 最多只允許 32,767 個 Database。  
2. 建立與維護大量獨立 DB 會導致 CPU / RAM / Metadata 負荷, 連線資源也會被快速耗盡, 形成瓶頸。  
3. 任何試用帳號、測試環境也都必須佔用一個 DB, 進一步壓縮可用額度。

**Solution**:  
改採「Shared Schema 或 NoSQL-based 儲存」, 以同一個資料庫 (或同一個 Table-like 儲存) 承載所有租戶資料, 再利用軟體層面的 Partition / TenantID 欄位來做隔離。  
關鍵思考：  
• 透過邏輯隔離避免資料庫數量膨脹, 根本性地移除 32,767 的上限。  
• 可搭配 Azure Table Storage 的 PartitionKey/RowKey, 讓系統自動將分割過的租戶資料分散到無數節點, 既隔離又擴充。

**Cases 1**:  
假設目標市場 50,000 個公司租戶:  
• Separated DB → 理論上限 32,767, 無法完整支援。  
• 改用 Shared Schema + TenantID, 在單一 DB 仍能容納 50,000+ 筆租戶資料, 不受 DB 數量限制。  
• 系統維運人員只需管理少量 DB, 大幅降低 DBA 工作量與自動化成本。

---

## Problem: Separated Schema 方案的資料庫物件上限與維護成本

**Problem**:  
若採「每個租戶建立一組 Schema 及其 Table/Index」(Separated Schema), 雖然減少 DB 數量, 但當租戶數破十萬時, 單一 DB 的物件 (table / view / trigger…) 將逼近上限, 且部署過程複雜。

**Root Cause**:  
1. SQL Server 單一 Database 的物件總數上限約 2,147,483,647, 平均每租戶 5,000 個物件, 大約 400,000 個租戶就會打滿。  
2. 每次 On-boarding / Schema 變更都要執行 DDL, 時間長且易失敗。  
3. Schema 版本控制極度複雜, 測試與回滾流程成本高。

**Solution**:  
• 改用 Shared Schema 或 Azure Table Storage: 所有租戶共用相同結構, 只多一個 TenantID / PartitionKey 欄位。  
• 單次 Migration 即可覆蓋所有租戶, 避免多版本併存。  
• 若使用 Azure Table Storage, 無須 DDL, 動態欄位天生支援結構演進。  

**Cases 1**:  
專案早期 1,000 租戶 → Separated Schema 尚可; 成長到 50,000 租戶後, Schema 變更 (新增一欄位) 需跑 50,000 次 ALTER TABLE, 時間 > 10 小時。  
遷移到 Shared Schema 僅需一次 ALTER, 完成時間 < 1 分鐘, 發布風險大幅下降。

---

## Problem: Shared Schema 單一 Table 數億筆資料導致查詢與索引性能惡化

**Problem**:  
在 Shared Schema 中, 若未妥善分割資料, 單一 Table 可能快速累積至數億筆, insert / update / join 時索引維運成本與 I/O 飆升, 造成整體服務變慢。

**Root Cause**:  
1. 所有租戶資料集中於少數大型 Table, 任何 DML 皆需更新龐大索引。  
2. 無法水平拆分 (shard) 時, 實體硬體 (磁碟/IOPS) 成瓶頸。  
3. 跨租戶複雜查詢 (JOIN) 容易掃描整張表, 奪走資源。

**Solution**:  
1. 在 RDBMS 端  
   • 先以 TenantID 建立 Partition / 分割表或 Row-Level Security, 控制索引大小與 I/O 範圍。  
2. 更根本做法 ─ 轉用 Azure Table Storage  
   • 以 PartitionKey = TenantID, RowKey = BusinessKey, 讓平台自動切分到多節點, 單一節點只處理單租戶資料。  
   • Table Storage 天然支援水平擴充, 並且避免大型 JOIN——改以 Key-Value 模式直接定位資料。  

**Cases 1**:  
• 原設計: 1,000 租戶、每租戶 10 萬筆 = 1 億筆/表, 任何 INSERT 延遲 400ms。  
• 改用 Azure Table Storage: PartitionKey 分散後, 單節點平均 < 100 萬筆, INSERT 延遲降至 20ms。  
• 後續租戶倍增至 2,000, 延遲維持 25ms, 幾乎線性擴充。

---

## Problem: RDBMS 難以水平擴充 (Scale-Out) 以支援雲端高並發

**Problem**:  
SaaS 流量高峰 (例如行銷活動) 可能瞬間暴增, 傳統 RDBMS 主要依賴 Scale-Up (加 CPU/RAM) 或昂貴複寫+分片, 對成本與技術人力都是挑戰。

**Root Cause**:  
1. SQL Server Cluster / Sharding 架構複雜, 部署及維運成本高。  
2. RDBMS 為了 ACID 與關聯完整性, 天生對分區與分片敏感, 影響交易一致性。  
3. DBA 與 DevOps 需投入大量工時調教索引、統計資訊、分區策略, 無法專注產品功能。

**Solution**:  
• 以雲端原生 NoSQL 服務 (Azure Table Storage) 取代大部分 OLTP 工作負載:  
  - 自動分割 Partition, 隨流量水平擴充到成千上萬節點。  
  - CAP 模型下選擇 AP (高可用 + 分區容忍), 以應付網際網路級讀寫量。  
• 在應用程式層把統計、報表等重運算工作搬到離線批次或大數據平台 (Ex: Hadoop/Synapse)。

**Cases 1**:  
• 某行銷 SaaS, 高峰期 3,000 RPS, 過去 SQL DB 權限鎖競爭, CPU 飆 95%。  
• 改接 Table Storage 後, 高峰期 15,000 RPS 仍 < 60% CPU, 只需調高儲存 Account 吞吐等級, 滾動升級 0 停機。  

**Cases 2**:  
• 研發團隊從「SQL 分片 + 自行維運」移轉到「PaaS Table Storage」, DBA 工時減少 70%, 營運成本 (License + VM) 降 50%, 可將資源挪到新功能開發。

---

## Problem: NoSQL（Azure Table Storage）引入的功能缺失與開發挑戰

**Problem**:  
Azure Table Storage 沒有 JOIN、ORDER BY、COUNT(*) 等 RDBMS 功能, 不正確建模會導致查詢效能低, 甚至無法產出必要的報表。

**Root Cause**:  
1. 只有 PartitionKey / RowKey 唯一索引, 其他欄位無索引, 依非主鍵查詢將全表掃描。  
2. 不支援 Server-Side JOIN / Aggregate 聚合, 開發者若不改寫 Domain Model 及 Query Pattern, 將難以實作商業邏輯。  

**Solution**:  
1. 在設計階段將查詢需求反推回 PartitionKey / RowKey 設計, 讓 90% 以上讀寫都落在單一 Partition 或直接命中 RowKey。  
   Example Code:  
   ```csharp
   // TenantID + OrderID 做唯一索引, 快速定位單筆訂單
   public class OrderEntity : TableEntity
   {
       public OrderEntity(string tenantId, string orderId)
       {
           PartitionKey = tenantId;   // Tenant 隔離
           RowKey       = orderId;    // PK
       }
       public DateTime CreateTime { get; set; }
       public decimal  Amount     { get; set; }
   }
   ```  
2. 跨租戶統計或報表 → 透過  
   • 後端 Worker Role / Function App 批次彙整到 Power BI / SQL DW  
   • 或快取在 Redis / Cosmos DB Analytical Store。  
3. 以 CQRS / Event-Sourcing 替代傳統「即時 JOIN + Aggregate」, 報表用 Read-Model 專庫呈現。

**Cases 1**:  
• 原報表需 GROUP BY TenantID, COUNT(*). 改為  
  - 每筆寫入同時推送 Event 至 Azure Function,  
  - 在 Azure SQL DW 累計, 3 分鐘內即時同步。  
• 系統成功保持 OLTP 高併發, 又兼顧 BI 報表, 用戶體感無延遲。  

---

## 結論

1. 若租戶數 > 幾千, Separated DB/Schema 必定陷入「物件上限 + 維運成本」兩大瓶頸。  
2. Shared Schema 雖能撐更高租戶數, 但單表膨脹及索引成本不可忽視。  
3. Azure Table Storage 透過 PartitionKey/RowKey 天生具備水平擴充與低成本特性, 是大規模 Multi-Tenancy 資料層的最終解。  
4. 對應功能缺失, 需改用 Domain-oriented Modeling、CQRS 及離線統計來補強。  

藉由正確的資料層選型與設計, SaaS 服務才能從「幾百租戶」無痛擴張到「數十萬租戶」, 並在高流量場景下依然保持成本可控、效能穩定。