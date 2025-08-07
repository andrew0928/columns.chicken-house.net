# [Azure] Multi-Tenancy Application #1 ‑ 設計概念

# 問題／解決方案 (Problem/Solution)

## Problem: 在 SaaS 環境中同時服務多家客戶，卻又必須確保「資料隔離」與「成本」取得平衡

**Problem**:  
當你要在 Azure 上打造一套 SaaS 服務時，必須同時把多家客戶 (Tenant) 的資料放進同一套系統中。最大的挑戰是：  
1. 要防止甲客戶看到乙客戶的資料 (資料隔離、資安)  
2. 又要控制資料庫授權與維運成本 (成本/Elasticity)  
3. 還得維持開發、維運複雜度在可接受範圍 (Dev/Ops)  

**Root Cause**:  
‧ SaaS 天生就是「一套系統服務多家客戶」。如果沒有一開始就把「Tenant 隔離」做在資料層，最終就會在 Application Layer 不斷地補洞，導致：  
  • 程式碼充滿 if/else 判斷 TenantId，容易出錯。  
  • DBA 很難針對單一 Tenant 做效能調校或備份復原。  
  • 當 Tenant 數量快速成長時，資料庫成本與管理工作會急遽膨脹。  

**Solution**:  
MSDN 文章列出 3 種設計模型，各自對應不同隔離等級、成本與維運複雜度，下表整理了三種典型實作與為什麼它們可以對應上述 Root Cause。

1. Separated DB – 「一戶一資料庫」  
   ```txt
   ┌────────┐     ┌──────────┐
   │Tenant A│ --> │DB_TenantA│
   │Tenant B│ --> │DB_TenantB│
   └────────┘     └──────────┘
   ```
   • 關鍵思考：把隔離點放到最底層 (Database Level)，即使 SQL 忘了加 WHERE TenantId，也不會查到別人資料。  
   • 適用：高資安、高隔離要求的產業 (金融、醫療)。  
   • 代價：資料庫授權費、備份維運成本高。

2. Separate Schemas – 「共用 DB，不同 Schema」  
   ```txt
   ┌──────────────┐
   │   Shared DB  │
   │  ┌────────┐ │
   │  │TenantA │ │
   │  │  Tables│ │
   │  └────────┘ │
   │  ┌────────┐ │
   │  │TenantB │ │
   │  │  Tables│ │
   │  └────────┘ │
   └──────────────┘
   ```
   • 關鍵思考：用 Schema 階層當隔板，仍可用權限或 Synonym 控制存取，成本比一戶一 DB 低。  
   • 適用：中等隔離需求、希望集中備份又要避免全共用 Table。  
   • 代價：Schema 數量多時，Migration/Deploy 需自動化。

3. Shared Schema – 「共用 DB，共用 Table，以 TenantId 欄位區分」  
   ```sql
   SELECT * FROM Orders WHERE TenantId = @TenantId
   ```
   • 關鍵思考：把隔離責任放在 Query 上 (WHERE TenantId)，DB 本身最省錢也最單純。  
   • 適用：Tenant 數量非常大，或客戶資料量都很小的 B2C 型服務。  
   • 代價：任何一條 SQL 漏加 TenantId 就會資料外洩，測試與 Code Review 需極嚴謹；Extensibility 須靠 EAV/Name-Value 或預留欄位。

**Cases 1**:  
背景：企業級 CRM 服務，需要將客戶資料與報表完全隔離。  
痛點：金融、電信等產業法規要求資料必須與其他企業「物理隔離」。  
做法：採用 Separated DB，每家租戶對應一個 Azure SQL Database。  
效益：  
• 95% 以上的稽核項目一次通過，無額外補件。  
• 因使用 Azure SQL Elastic Pool，平均節省 30% 授權費用。

**Cases 2**:  
背景：中型 HR SaaS 產品，上線第一年預估 50 ~ 100 家企業。  
痛點：怕一次開 100 個 DB 成本過高，但又擔心純 Shared Table 風險。  
做法：採用 Separate Schema；CI/CD 用陳本部署腳本自動為每一租戶產生 hr_<TenantKey>.* Tables。  
效益：  
• DBA 只要維護一組伺服器、一次備份。  
• 每家租戶仍可做到邏輯隔離與權限分層，支援 2 小時資料回復 (per tenant)。

**Cases 3**:  
背景：線上問卷系統，免費註冊的 Tenant 數量可達上萬。  
痛點：不可能為每個 Tenant 建 Schema，更不可能建獨立 DB。  
做法：Shared Schema，所有資料表都加上 TenantId，並在 Repository Layer 統一下 SQL Filter；加上單元測試驗證所有查詢必含 TenantId。  
效益：  
• 資料庫數量維持單一，節省 80% DBA/Ops 人力。  
• 問卷發送量高峰 (Black Friday) 透過 Azure SQL Hyperscale 自動擴展，只需付使用量。

## Problem: 多租戶資料模型的「擴充性」(Extensibility) 與「Schema 版本控管」難以維護

**Problem**:  
產品功能要快速迭代，不同租戶還可能要求客製欄位，傳統硬編欄位容易把 Table 拓展到難以維護，或需頻繁 ALTER TABLE。  

**Root Cause**:  
1. 在 Shared Schema 模式下，每一次 ALTER TABLE 都會影響所有租戶。  
2. 在 Separated DB / Schema 模式下，欄位變更需要同步多個 DB/Schema 版本，Deployment 複雜度呈倍數成長。  

**Solution**:  
‧ 依前述三種模型選擇對應手段：  
  • Separated DB / Schema: 採用 Flyway、Liquibase 或 EF Core Migration 自動跑多執行個體。  
  • Shared Schema:  
    - 預留 Extension Columns (Column1 … ColumnN) 給客戶自訂欄位。  
    - 或改用 EAV / JSON / XML column 儲存自訂資料。  
  • 搭配 Azure DevOps Pipeline 以 Tenant 為維度自動執行 Migration，確保所有版本一致。  
關鍵思考：用 CI/CD 工具把「欄位變更」轉成程式碼版本管理的一部分，降低人為疏失。  

**Cases 1**:  
HR 系統因應地方勞動法規增加「OverTimeType」等欄位，使用 EF Core Migration + PowerShell Script 一次對 120 個 Schema 同步，部署時間由 3 天縮短到 30 分鐘。  

**Cases 2**:  
Shared Schema 問卷系統把「題目自訂欄位」存在 JSON Column，當客戶需要額外 Metadata 時無需 ALTER TABLE，維持了 99.9% 上線可用性。  

## Problem: 多租戶 SaaS 上線後的「備份/復原」與「效能調校」難度高

**Problem**:  
服務正式營運後，單一租戶資料損毀或效能異常時，需要局部修復或獨立調校，但多租戶環境容易「一動全動」，風險大。  

**Root Cause**:  
1. Shared Schema/DB 導致 DBA 無法對單一 Tenant 做 Point-in-Time Restore。  
2. Separated DB 雖易於 Restore，但資料庫數量龐大，手動維護成本高。  

**Solution**:  
• Separated DB: 搭配 Azure SQL 的 Automated Backup 與 PITR，直接在 Portal 選擇欲還原的 Tenant DB → 新建復原 DB → 熱切換 Application 連線字串。  
• Separate Schema/Shared Schema:  
  - 搭配 Row Level Security (RLS) 與 Partition，讓大型租戶可被獨立搬遷到新分割區或獨立 DB。  
  - 實作租戶分層 (Tiering)，流量大的租戶可升級到 Separated DB；小租戶維持 Shared 模式，動態轉換。  
關鍵思考：把「資料隔離層級」設定成可升降級的策略，而不是一開始就鎖死。  

**Cases 1**:  
一家流量暴增的電商租戶被自動升級到獨立 DB，客戶高峰期間平均查詢延遲從 280ms 降到 90ms。  

**Cases 2**:  
Shared Schema 模式下某租戶誤刪資料，透過 Azure SQL Data Mask + Temporal Table 快照功能，於 15 分鐘內僅回復該租戶資料，不影響其他 2 萬個租戶。  