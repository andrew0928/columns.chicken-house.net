# EF#3. Entity & Inheritance — 物件繼承如何落地到 Relational DB

# 問題／解決方案 (Problem/Solution)

## Problem: 物件導向「繼承」模型在 RDBMS 落地時，無法直接對應

**Problem**:  
在使用 Entity Framework (EF) 或 NHibernate (NH) 這類 ORM 時，開發者希望把 C#/Java 程式碼中的類別繼承階層，持久化到傳統的關聯式資料庫 (RDBMS)。然而 RDBMS 天生只支援 Table 與 Row 概念，完全沒有「類別」「繼承」等 OOP 結構；如果直接一張表就塞所有欄位，可能導致 Schema 難以維護、效能不佳；若拆成多張表，又面臨複雜 JOIN 與 Constraint 管理。如何在「正規化」「效能」「維護成本」之間取得平衡，是 ORM 專案常見且棘手的難題。

**Root Cause**:  
1. OOP 與 RDBMS 天生模型差異 (Object–Relational Impedance Mismatch)。  
2. RDBMS 不具備 Virtual Table、Inheritance 等概念，只能用 Table / Column 表達。  
3. 若沒有一套映射策略，資料庫 Schema 可能隨需求頻繁調整，帶來維運風險。  

**Solution**:  
實務上 EF 與 NH 總結出三套「Inheritance Mapping Strategy」：  

1. Table per Hierarchy (TPH)  
2. Table per Type (TPT)  
3. Table per Concrete Type (TPC)  

三種策略各自對應不同場景，下面一併說明選用時機、優缺點與關鍵思考點。

---

### Solution 1: Table per Hierarchy (TPH)

• 關鍵作法  
  - 所有父類別與子類別資料放在「同一張」Table。  
  - 以一個 Discriminator Column (如 `Type`) 區分實際子類別。  

• 為何能解決 Root Cause  
  - 透過單一表即可存取完整繼承資料，避開多表 JOIN。  
  - 對 Instance 數量不大時，效能最佳、實作最簡單。  

**Cases 1**:  
  - 小型系統 (例如權限角色只有 Admin / Guest / Member 三種) 放進一張 `Users` 表，加 `RoleType` 欄位即可。單表 CRUD、查詢語法簡單，部署快速。

**Cases 2**:  
  - PoC 或 Startup MVP 階段，需要最快速推上線：採用 TPH 能把 Schema 設計時間壓到最低，程式邏輯直接用 ORM 的 `Discriminator` 屬性分流。

---

### Solution 2: Table per Type (TPT)

• 關鍵作法  
  - 父類別一張 Table；每個子類別各自一張 Table。  
  - 子表以 PK = FK 方式連回父表。  

• 為何能解決 Root Cause  
  - 各子類別可套用嚴謹的 Table Constraint / Index。  
  - Schema 反映清楚繼承關係，維護時易於加欄位或改約束。  

**Cases 1**:  
  - 企業內部 ERP：`Document` 為父表，`Invoice`、`PurchaseOrder` 子表各有獨特欄位與資料制約。TPT 讓每張單獨表可設定外鍵、唯一索引，避免資料不一致。  

**Cases 2**:  
  - 報表系統需要「一次撈所有文件類別」：ORM 仍可用單一 LINQ 查詢，EF 會自動組合 JOIN，開發體驗與物件模型一致。

---

### Solution 3: Table per Concrete Type (TPC)

• 關鍵作法  
  - 每個「具體子類別」自建一張獨立 Table。  
  - 父類別不落地任何 Table；共用欄位重複出現在每張子表。  

• 為何能解決 Root Cause  
  - 綜合了 TPH 單表簡單和 TPT 嚴謹 Constraint 的優點。  
  - 各子表單獨存在，查詢單一子類別時無 JOIN；可依不同需求打 Index。  

**Cases 1**:  
  - SaaS 平台多租戶情境：`CustomerTaiwan`, `CustomerUS`, `CustomerEU` 三種子類別欄位大同小異但法規不同，需要各自設定欄位型別與 Constraint。TPC 讓三張 Table 各自優化，不互相干擾。  

**Cases 2**:  
  - 當前端 UI 僅會一次載入單一子類別資料，例如「員工檔」與「外包商檔」分開管理，不需合併查詢，同步排除了多表 JOIN 的效能疑慮。  

---

# 小結  

• TPH → 最快上手、單表、適合小量資料。  
• TPT → 父子拆表、JOIN 讀取、但 Constraint 最完整。  
• TPC → 每個子類別完全獨立、查詢單查效率高，但跨類查詢要 UNION/JOIN。  

透過選擇合適的 Inheritance Mapping Strategy，ORM 專案可以在「開發速度」「效能」「資料完整性」之間取得最佳平衡，降低日後 Schema 變更與技術債成本。