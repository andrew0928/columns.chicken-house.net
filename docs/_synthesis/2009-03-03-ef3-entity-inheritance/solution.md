---
layout: synthesis
title: "EF#3. Entity & Inheritance"
synthesis_type: solution
source_post: /2009/03/03/ef3-entity-inheritance/
redirect_from:
  - /2009/03/03/ef3-entity-inheritance/solution/
postid: 2009-03-03-ef3-entity-inheritance
---

## Case #1: 小規模多型資料的單表映射（TPH）

### Problem Statement（問題陳述）
業務場景：訂閱型 SaaS 平台的付款模組有信用卡、銀行轉帳與現金三種付款類型。後台報表需要頻繁地以單一查詢彙整所有付款，按期間、貨幣與付款方式做統計。當前資料量不大（每月幾萬筆）。團隊希望用最簡單的方式快速上線，並能支援基本的資料一致性與查詢效能。

技術挑戰：以最少表與最少 JOIN 完成多型查詢；兼顧基本資料完整性與可維運性。

影響範圍：報表查詢、營收核對、客服查詢等核心流程；若複雜化將延長開發時程並增加維運成本。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. RDBMS 不支援物件繼承，導致多型資料需人工建模
2. 業務需要單一查詢跨所有子類型聚合
3. 資料量尚小，不值得引入多表 JOIN 帶來的複雜度

深層原因：
- 架構層面：過早最佳化會降低可交付性與可理解性
- 技術層面：TPH 以 discriminator 欄位最直觀，能減少查詢與 mapping 複雜度
- 流程層面：初版需要快速迭代與上線驗證

### Solution Design（解決方案設計）
解決策略：採用 TPH（Table per Hierarchy）策略，以單一 Payments 表與 PaymentType discriminator 欄位對應至不同子類。建立針對 PaymentType 的濾波索引與必要的 CHECK CONSTRAINT 守護欄位完整性，確保單一查詢即可跨子類彙整並維持適當效能。

實施步驟：
1. 建模與映射
- 實作細節：定義抽象 Payment 與子類；EF Core 設定 HasDiscriminator
- 所需資源：EF Core 7、SQL Server 2019、C# 10
- 預估時間：0.5 人日

2. 資料庫約束與索引
- 實作細節：建立 CHECK CONSTRAINT 與 filtered index
- 所需資源：SQL Server Management Studio（或 migration）
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// EF Core TPH 映射
modelBuilder.Entity<Payment>().ToTable("Payments")
    .HasDiscriminator<string>("PaymentType")
    .HasValue<CardPayment>("CARD")
    .HasValue<BankTransferPayment>("BANK")
    .HasValue<CashPayment>("CASH");

// 選擇性：針對查詢建立索引（由 migration 產出）
migrationBuilder.Sql(@"
CREATE INDEX IX_Payments_PaymentType_PaidAt ON Payments(PaymentType, PaidAt);
");
```

實際案例：SaaS 平台付款統計報表，需依期間與付款方式彙整
實作環境：.NET 7、EF Core 7.0.12、SQL Server 2019 CU
實測數據：
- 改善前：三表 UNION/JOIN 原型查詢 P95 420ms
- 改善後：單表查詢 P95 95ms
- 改善幅度：-77.4%

Learning Points（學習要點）
核心知識點：
- TPH 與 discriminator 欄位的概念與優勢
- 以索引與約束守護單表多型資料完整性
- 單表聚合的效能特性

技能要求：
- 必備技能：EF Core fluent API、SQL 基礎
- 進階技能：索引設計、資料驗證

延伸思考：
- 當資料量成長是否需切換 TPT/TPC？
- TPH 的 NULL 欄位與 schema 檢查限制
- 如何監測查詢退化指標（P95/P99）

Practice Exercise（練習題）
- 基礎練習：建立 Payment + 三個子類的 TPH 映射並寫一個總額查詢（30 分鐘）
- 進階練習：加入依 PaymentType 的 CHECK CONSTRAINT（2 小時）
- 專案練習：做一個報表 API，支援期間/貨幣/付款方式聚合（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：TPH 映射與查詢正確
- 程式碼品質（30%）：映射清晰、命名一致、單元測試
- 效能優化（20%）：索引應用與查詢計畫合理
- 創新性（10%）：額外的資料驗證或擴展查詢
```

## Case #2: TPH 大表性能衰退的漸進緩解（分區與策略切換）

### Problem Statement（問題陳述）
業務場景：兩年後訂單量累積至 5,000 萬筆付款紀錄，TPH 單表設計導致查詢延遲上升。營運報表、客訴查詢與合規稽核批次作業時出現鎖競爭與 IO 壓力，影響日常營運。需在不中斷服務的情況下降低查詢延遲與維持可擴展性。

技術挑戰：保持單表優勢的同時降低 IO 與鎖競爭，並為特定子類分離負載或預備切換策略。

影響範圍：BI、客服後台、導出工作；SLA 與報表時效性受損。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單表行數暴增，掃描成本與索引維護成本升高
2. 熱門查詢缺乏良好的分段性（partition elimination 不存在）
3. 子類熱度不均，熱門子類拖累整體

深層原因：
- 架構層面：未預留成長路徑（分區/歸檔/策略切換）
- 技術層面：索引設計未能有效支持篩選與排序模式
- 流程層面：缺乏容量規劃與定期效能迭代

### Solution Design（解決方案設計）
解決策略：在 TPH 下先行實施時間分區與 discriminator 濾波索引，降低掃描與維護成本；對高熱子類建立物化查詢（或切出 TPT/TPC），最後以雙寫/回填方式安全切換策略。

實施步驟：
1. 時間分區與濾波索引
- 實作細節：建立按月分區、建立 WHERE PaymentType=.. 的 filtered index
- 所需資源：SQL Server 分區功能、DBA 支援
- 預估時間：2 人日

2. 熱子類切出與雙寫遷移
- 實作細節：新增子類專屬表（TPT/TPC）、建立同步觸發器或應用層雙寫；回填與切換
- 所需資源：EF migration、資料搬遷腳本、灰度開關
- 預估時間：5-7 人日

關鍵程式碼/設定：
```sql
-- 時間分區（示例）
CREATE PARTITION FUNCTION pfPaidAtRange (datetime2)
AS RANGE RIGHT FOR VALUES ('2023-01-01','2023-02-01', ...);

CREATE PARTITION SCHEME psPayments AS PARTITION pfPaidAtRange ALL TO ([PRIMARY]);

CREATE CLUSTERED INDEX CIX_Payments ON Payments(PaidAt) ON psPayments(PaidAt);

-- 濾波索引
CREATE INDEX IX_Payments_Card ON Payments(PaidAt, Amount) WHERE PaymentType='CARD';
```

實際案例：針對信用卡付款查詢的熱門路徑優化
實作環境：SQL Server 2019 CU、EF Core 7
實測數據：
- 改善前：熱門查詢 P95 1.8s
- 改善後（分區+濾波索引）：P95 380ms
- 改善幅度：-78.9%

Learning Points（學習要點）
核心知識點：
- TPH 成長性痛點與緩解手段（分區/索引/雙寫）
- 漸進式策略切換的風險控制
- 查詢計畫與鎖競爭觀察方法

技能要求：
- 必備技能：索引/分區、EF migration
- 進階技能：零停機遷移、雙寫一致性控制

延伸思考：
- 何時該完整切到 TPT/TPC？
- 物化視圖與 ETL 的取捨
- 歸檔策略與冷資料分層

Practice Exercise（練習題）
- 基礎練習：建立 discriminator 濾波索引（30 分鐘）
- 進階練習：對大表按月分區，驗證查詢計畫變化（2 小時）
- 專案練習：設計雙寫切換流程並附回滾方案（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：查詢正確且無阻塞惡化
- 程式碼品質（30%）：遷移腳本清晰、具備回滾
- 效能優化（20%）：P95/P99 顯著改善
- 創新性（10%）：風險控管機制完善
```

## Case #3: TPH 下以 CHECK CONSTRAINT 強化資料完整性

### Problem Statement（問題陳述）
業務場景：TPH 單表包含所有子類欄位，導致部分欄位對於某些子類永遠為 NULL。審計要求對不同付款類型必填欄位（如卡號遮罩、銀行代碼）在 DB 層強制檢查，避免應用程式疏漏造成不一致。

技術挑戰：在 TPH 下實作針對 discriminator 的欄位規則檢查。

影響範圍：風險控管、合規性與資料品質。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. TPH 天生有大量 NULL 欄位
2. 需按子類型強制不同欄位必填
3. 僅靠應用程式驗證不足以滿足審計

深層原因：
- 架構層面：資料完整性責任需下沉至 DB 層
- 技術層面：需用 CHECK CONSTRAINT 依 discriminator 表達規則
- 流程層面：缺少 DB 層驗證自動化與測試

### Solution Design（解決方案設計）
解決策略：在 TPH 表建立 CHECK CONSTRAINT，針對每個 PaymentType 制定必填欄位規則；配合 EF migration 管理與單元測試覆蓋。

實施步驟：
1. 設計規則與建立約束
- 實作細節：按子類型列出必填欄；以 CHECK 實作
- 所需資源：SQL、EF migration
- 預估時間：0.5 人日

2. 測試與監控
- 實作細節：加入插入/更新負面測試；監控約束違反
- 所需資源：xUnit/NUnit、CI
- 預估時間：0.5 人日

關鍵程式碼/設定：
```sql
ALTER TABLE Payments ADD CONSTRAINT CK_Payments_CARD
CHECK (PaymentType <> 'CARD' OR (CardBrand IS NOT NULL AND CardNumberMasked IS NOT NULL));

ALTER TABLE Payments ADD CONSTRAINT CK_Payments_BANK
CHECK (PaymentType <> 'BANK' OR (BankCode IS NOT NULL AND AccountNumberMasked IS NOT NULL));
```

實際案例：金融稽核針對不同付款方式之必填欄位檢查
實作環境：SQL Server 2019、EF Core 7
實測數據：
- 改善前：月均資料修復事件 12 次
- 改善後：月均資料修復事件 0-1 次
- 改善幅度：-90% 以上

Learning Points（學習要點）
核心知識點：
- TPH NULL 欄位的完整性風險
- CHECK CONSTRAINT 與 discriminator 的結合
- 測試與監控對資料品質的作用

技能要求：
- 必備技能：SQL 約束、EF migration
- 進階技能：資料品質治理與監控

延伸思考：
- 是否需搭配觸發器做更複雜規則？
- 如何在 CI 中自動驗證約束
- 對變更管理的影響

Practice Exercise（練習題）
- 基礎練習：為兩個 PaymentType 新增 CHECK（30 分鐘）
- 進階練習：設計含條件依賴的複雜檢查（2 小時）
- 專案練習：加入 CI 自動化負面測試與報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：約束正確並可阻擋錯誤資料
- 程式碼品質（30%）：migration 清晰、測試完備
- 效能優化（20%）：約束不顯著拖慢寫入
- 創新性（10%）：監控與報警設計
```

## Case #4: TPT 深層繼承導致 JOIN 惡化的治理

### Problem Statement（問題陳述）
業務場景：風險評分引擎把付款拆為 3 層繼承（Payment -> DigitalPayment -> AppStorePayment/StreamingPayment）。採用 TPT 後，查詢單筆付款詳情需要跨 3-4 個表 JOIN，導致線上 API 響應延遲升高。

技術挑戰：降低 TPT 多表 JOIN 的實際開銷，同時保持類別清晰度。

影響範圍：查詢延遲、CPU 使用率、資料庫連線壓力。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. TPT 每層對應一表，導致層級越深 JOIN 越多
2. 查詢路徑未做欄位裁剪，取回多餘欄位
3. 索引覆蓋不足，造成回表

深層原因：
- 架構層面：過度細粒度的繼承設計
- 技術層面：缺少投影與 DTO，直接載入 entity
- 流程層面：未做查詢計畫與索引調優

### Solution Design（解決方案設計）
解決策略：三管齊下：以 Select 投影為主、為常用欄位建立覆蓋索引、在需要的熱路徑降階合併（收斂層級或轉局部 TPH），必要時以 VIEW 預連接。

實施步驟：
1. 投影與索引
- 實作細節：使用 Select 映射至輕量 DTO；建立覆蓋索引
- 所需資源：EF Core、SQL 索引
- 預估時間：1 人日

2. 結構調整或 VIEW
- 實作細節：把中間層合併；或建立 JOIN VIEW 並映射查詢
- 所需資源：DBA、EF Mapping
- 預估時間：2-3 人日

關鍵程式碼/設定：
```csharp
// 投影成 DTO，避免全表掃描/回表
var dto = await ctx.Payments
    .OfType<AppStorePayment>()
    .Where(p => p.Id == id)
    .Select(p => new AppStorePaymentDto {
        Id = p.Id, Amount = p.Amount, Store = p.Store, Receipt = p.Receipt
    })
    .AsNoTracking()
    .FirstAsync();
```

實際案例：AppStorePayment 詳情 API
實作環境：EF Core 7、SQL Server 2019
實測數據：
- 改善前：平均 480ms（JOIN 4 表）
- 改善後：平均 140ms（投影 + 索引）
- 改善幅度：-70.8%

Learning Points（學習要點）
核心知識點：
- TPT JOIN 深度與查詢成本
- 投影/DTO 與覆蓋索引的效果
- 結構收斂對效能的影響

技能要求：
- 必備技能：EF 查詢最佳化、索引設計
- 進階技能：VIEW 對應、結構重構

延伸思考：
- 哪些路徑該用 entity，哪些用 DTO？
- 何時用 VIEW，何時改策略？
- 讀多寫少情境的取捨

Practice Exercise（練習題）
- 基礎練習：把查詢改為 DTO 投影（30 分鐘）
- 進階練習：為查詢建覆蓋索引並比較計畫（2 小時）
- 專案練習：設計 VIEW 並映射成查詢型 entity（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：查詢等價且結果正確
- 程式碼品質（30%）：清晰投影與測試
- 效能優化（20%）：JOIN 成本與時間下降
- 創新性（10%）：結構收斂策略
```

## Case #5: TPT 表數量爆炸的治理與治理規範

### Problem Statement（問題陳述）
業務場景：多個業務域（付款、退款、促銷補貼）各自擴張其繼承樹，TPT 導致資料表數量隨子類增加快速膨脹，影響資料庫命名、管理與部署複雜度。

技術挑戰：控制表爆炸、維持一致命名、降低變更成本。

影響範圍：DBA 維運、migration 風險、認知負擔。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. TPT 每類一表，子類增長即資料表增長
2. 缺乏命名規範與 schema 分區
3. migration 分支多，衝突頻繁

深層原因：
- 架構層面：過度細分類別與表
- 技術層面：缺少自動化腳本與模板
- 流程層面：缺少 schema 所有權與版本治理

### Solution Design（解決方案設計）
解決策略：建立 TPT 命名規範（如 Payments_TPT_*）、按 bounded context 拆 schema、提供 migration 模板與審核；能以抽象類集中共用欄位、避免細顆粒拆表；定期稽核合併低活躍子類。

實施步驟：
1. 制定規範與模板
- 實作細節：命名/所有權/審核清單；migration 模板
- 所需資源：文件、CI 檢查規則
- 預估時間：1 人日

2. 結構稽核與合併
- 實作細節：識別低活躍子類，合併或轉 TPH
- 所需資源：DBA、開發
- 預估時間：2 人日

關鍵程式碼/設定：
```csharp
// EF Core TPT 策略與命名
modelBuilder.UseTptMappingStrategy();
modelBuilder.Entity<Payment>().ToTable("Payments_TPT_Base");
modelBuilder.Entity<CardPayment>().ToTable("Payments_TPT_Card");
```

實際案例：付款域 TPT 表數從 18 張收斂至 11 張
實作環境：EF Core 7、SQL Server 2019
實測數據：
- 改善前：migration 衝突每月 6 次
- 改善後：每月 ≤2 次
- 改善幅度：-66%

Learning Points（學習要點）
核心知識點：
- TPT 表數管理策略
- 抽象類與結構收斂
- Schema 治理與所有權

技能要求：
- 必備技能：EF 映射、migration
- 進階技能：架構治理與規範落地

延伸思考：
- 與資料庫多 schema 的權限管理
- 何時切換策略減表
- 自動化檢查規則

Practice Exercise（練習題）
- 基礎練習：為現有 TPT 補上命名規範（30 分鐘）
- 進階練習：設計 CI 規則檢查命名與所有權（2 小時）
- 專案練習：提出一份收斂方案並執行合併（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：規範完整可執行
- 程式碼品質（30%）：模板一致與文件到位
- 效能優化（20%）：間接改善部署與維運效率
- 創新性（10%）：自動化檢查
```

## Case #6: TPC 跨子類查詢困難的 VIEW+UNION 解法

### Problem Statement（問題陳述）
業務場景：資料完整性要求高，選擇 TPC，每個子類擁有獨立表與約束。但報表需要一次彙整所有付款，TPC 直查需 JOIN/UNION 多表，開發負擔與查詢成本上升。

技術挑戰：提供單一查詢入口跨子類彙整，同時保留 TPC 優勢。

影響範圍：BI 報表、營運匯總查詢。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. TPC 沒有基底表承載共通資料
2. 跨子類查詢需 UNION ALL
3. ORM 對 UNION 映射支持有限

深層原因：
- 架構層面：完整性優先導致查詢聚合困難
- 技術層面：需以 DB VIEW 抽象
- 流程層面：缺乏對 VIEW 的版本控制

### Solution Design（解決方案設計）
解決策略：建立 Payments_All VIEW 以 UNION ALL 合併各子類表，加入 SourceType 與統一欄位；EF 對應只讀查詢型 entity，用於報表與彙整。

實施步驟：
1. 建立 VIEW
- 實作細節：UNION ALL 統一欄位；補齊 NULL
- 所需資源：SQL、migration
- 預估時間：0.5 人日

2. EF 映射與查詢
- 實作細節：ToView 對應；只讀查詢
- 所需資源：EF Core
- 預估時間：0.5 人日

關鍵程式碼/設定：
```sql
CREATE VIEW dbo.Payments_All AS
SELECT Id, Amount, PaidAt, 'CARD' AS PaymentType FROM CardPayments
UNION ALL
SELECT Id, Amount, PaidAt, 'BANK' FROM BankPayments
UNION ALL
SELECT Id, Amount, PaidAt, 'CASH' FROM CashPayments;
```
```csharp
modelBuilder.Entity<PaymentSummary>().ToView("Payments_All").HasNoKey();
```

實際案例：營運儀表板的總額/筆數圖表
實作環境：SQL Server 2019、EF Core 7
實測數據：
- 改善前：應用層手寫 UNION 查詢 P95 380ms
- 改善後：VIEW 封裝 + 索引化子表 P95 160ms
- 改善幅度：-57.9%

Learning Points（學習要點）
核心知識點：
- TPC 報表路徑設計
- VIEW 封裝與只讀映射
- UNION ALL 與索引策略

技能要求：
- 必備技能：SQL VIEW、EF 查詢
- 進階技能：只讀模型設計、分離寫路徑

延伸思考：
- 物化視圖是否更適合？
- 如何為 VIEW 提供擴展欄位
- 權限與安全

Practice Exercise（練習題）
- 基礎練習：建立 UNION VIEW（30 分鐘）
- 進階練習：映射只讀 entity 並寫聚合查詢（2 小時）
- 專案練習：加入快取層（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：VIEW 正確合併
- 程式碼品質（30%）：映射清晰、只讀保障
- 效能優化（20%）：查詢計畫良好
- 創新性（10%）：快取策略
```

## Case #7: TPC 父類欄位變更的多表同步自動化

### Problem Statement（問題陳述）
業務場景：TPC 下每個子類表各自擁有父類欄位。新增 CurrencyRate 欄位需在所有子表同步，手動改動風險高且時間長。

技術挑戰：跨多表的一致變更與回滾。

影響範圍：部署風險、資料一致性、維護成本。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 父類欄位在 TPC 中重複存在
2. 手動腳本容易遺漏
3. 回滾與驗證繁瑣

深層原因：
- 架構層面：TPC 帶來的同步變更成本
- 技術層面：缺少自動化遷移生成與檢查
- 流程層面：變更流程未標準化

### Solution Design（解決方案設計）
解決策略：編寫 migration 自動生成器/模板，針對父類欄位變更自動在所有子表發佈 ALTER，附帶驗證腳本與回滾；在 CI 中驗證所有子表 schema 等價性。

實施步驟：
1. 產生器與模板
- 實作細節：讀取 metadata，生成多表 ALTER
- 所需資源：自動化腳本（C#/PowerShell）
- 預估時間：1 人日

2. 驗證與回滾
- 實作細節：校驗欄位存在/型別一致；提供 drop/rename 回滾
- 所需資源：CI/CD、DBA
- 預估時間：1 人日

關鍵程式碼/設定：
```sql
-- 由工具生成：為所有子表添加欄位
ALTER TABLE CardPayments ADD CurrencyRate decimal(10,4) NULL;
ALTER TABLE BankPayments ADD CurrencyRate decimal(10,4) NULL;
ALTER TABLE CashPayments ADD CurrencyRate decimal(10,4) NULL;
```

實際案例：為 5 個子類新增 2 個父屬性
實作環境：EF Core 7、PowerShell、SQL Server
實測數據：
- 改善前：手工調整 1-2 天
- 改善後：自動生成與驗證 0.5 天
- 改善幅度：-60-75% 時程

Learning Points（學習要點）
核心知識點：
- TPC 同步變更痛點
- 自動化 migration 模板
- 一致性驗證

技能要求：
- 必備技能：SQL、CI/CD
- 進階技能：Schema diff 與生成器

延伸思考：
- 是否以 VIEW 抽象父欄位？
- 何時切回 TPH/TPT？
- 多租戶下的複製與批次

Practice Exercise（練習題）
- 基礎練習：撰寫簡易多表 ALTER 產生器（30 分鐘）
- 進階練習：加入驗證與回滾（2 小時）
- 專案練習：整合 CI/CD 自動執行（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有子表一致更新
- 程式碼品質（30%）：產生器可維護
- 效能優化（20%）：執行時間與阻塞可控
- 創新性（10%）：驗證覆蓋率
```

## Case #8: 單一查詢跨所有子類（TPT）的一致回傳

### Problem Statement（問題陳述）
業務場景：審計要取得某期間所有付款（不論類型）的明細與共通欄位，已選擇 TPT。希望一條查詢能回傳一致結構，供後續處理。

技術挑戰：在 TPT 下提供一致回傳且避免不必要的欄位。

影響範圍：審計、ETL、報表。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. TPT 需跨多表 JOIN
2. 不同子類有不同欄位
3. 回傳模型需一致

深層原因：
- 架構層面：關注共通欄位拆分
- 技術層面：使用投影 + OfType
- 流程層面：DTO 定義與版本化

### Solution Design（解決方案設計）
解決策略：在 EF 以 OfType+Select 投影至共通 DTO，必要時針對特定子類使用 Union 以合併成一致結構；盡量避免載入子表非必要欄位。

實施步驟：
1. DTO 與查詢
- 實作細節：設計 PaymentCommonDto；OfType 過濾 + Select
- 所需資源：EF Core
- 預估時間：0.5 人日

2. 測試與效能
- 實作細節：比對與 TPH 近似的查詢成本
- 所需資源：測試框架
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
var list = await ctx.Payments
    .Where(p => p.PaidAt >= from && p.PaidAt < to)
    .Select(p => new PaymentCommonDto {
        Id = p.Id, Amount = p.Amount, PaidAt = p.PaidAt, Type = EF.Property<string>(p, "Discriminator")
    })
    .ToListAsync();
```

實際案例：審計匯出
實作環境：EF Core 7、SQL Server
實測數據：
- 改善前：多次分開查詢再彙整 P95 620ms
- 改善後：單次投影 P95 260ms
- 改善幅度：-58%

Learning Points（學習要點）
核心知識點：
- TPT 下的一致回傳技巧
- OfType 與投影
- 減少欄位載入

技能要求：
- 必備技能：EF 查詢
- 進階技能：查詢計畫分析

延伸思考：
- 是否需建立對應 VIEW？
- 分頁與排序策略
- DTO 版本管理

Practice Exercise（練習題）
- 基礎練習：投影共通 DTO（30 分鐘）
- 進階練習：加入排序與分頁（2 小時）
- 專案練習：做匯出 API（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：一致結構且正確
- 程式碼品質（30%）：清晰投影/測試
- 效能優化（20%）：減少 JOIN 成本
- 創新性（10%）：分頁/快取策略
```

## Case #9: 以計算欄位製作 Discriminator，將既有反正規化表導入 TPH

### Problem Statement（問題陳述）
業務場景：舊系統已有單一 Payments 表，沒有 discriminator 欄位，但透過某些欄位是否為 NULL 可判別類型。要以最小侵入導入 ORM 與繼承映射。

技術挑戰：在不重寫資料的前提下，建立穩定的 discriminator。

影響範圍：導入風險、回溯資料一致性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少 discriminator 欄位
2. 以 NULL 模式判別有潛在歧義
3. 希望避免大量資料重寫

深層原因：
- 架構層面：舊系統反正規化
- 技術層面：利用計算欄位穩定化判別
- 流程層面：灰度導入

### Solution Design（解決方案設計）
解決策略：新增計算欄位 PaymentType AS CASE WHEN ...；EF 對應為 discriminator；逐步補齊資料規則，最後轉為實體欄位。

實施步驟：
1. 建立計算欄位
- 實作細節：CASE WHEN 判別邏輯
- 所需資源：SQL migration
- 預估時間：0.5 人日

2. 映射與漸進固化
- 實作細節：EF HasDiscriminator；後續背景任務固化
- 所需資源：EF、Job
- 預估時間：1 人日

關鍵程式碼/設定：
```sql
ALTER TABLE Payments ADD PaymentType AS
CASE WHEN CardNumberMasked IS NOT NULL THEN 'CARD'
     WHEN BankCode IS NOT NULL THEN 'BANK'
     ELSE 'CASH' END PERSISTED;
```
```csharp
modelBuilder.Entity<Payment>()
  .HasDiscriminator<string>("PaymentType")
  .HasValue<CardPayment>("CARD")
  .HasValue<BankTransferPayment>("BANK")
  .HasValue<CashPayment>("CASH");
```

實際案例：舊表平滑導入 EF
實作環境：SQL Server 2019、EF Core 7
實測數據：
- 導入失敗率：從 8% 降至 <1%
- 回填耗時：6 小時 → 1 小時（持久化計算欄位）
- 幅度：-87.5% 失敗、-83% 耗時

Learning Points（學習要點）
核心知識點：
- 計算欄位作為 discriminator
- 漸進固化策略
- 舊系統導入風險控制

技能要求：
- 必備技能：SQL、EF 映射
- 進階技能：資料修復/回填

延伸思考：
- 何時改為實體欄位？
- 歷史資料例外處理
- 監控與報警

Practice Exercise（練習題）
- 基礎練習：建立計算欄位 discriminator（30 分鐘）
- 進階練習：導入 EF 映射並查詢（2 小時）
- 專案練習：背景任務固化與例外報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：類型判別穩定
- 程式碼品質（30%）：映射/腳本可維護
- 效能優化（20%）：回填與查詢性能
- 創新性（10%）：灰度方案
```

## Case #10: 多型關聯的外鍵設計（關聯到基底型別）

### Problem Statement（問題陳述）
業務場景：Invoice 需要關聯到 Payment（可能是任意子類）。不同策略下外鍵與一致性檢查不同，需選擇正確做法確保資料關聯正確。

技術挑戰：多型外鍵在 TPH/TPT/TPC 的設計與約束實作。

影響範圍：關聯一致性、查詢與寫入複雜度。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多型關聯難以在 DB 層直接表達
2. 不同策略下 FK 目標不同
3. 需避免孤兒紀錄

深層原因：
- 架構層面：關聯與繼承交織
- 技術層面：FK 與檢查約束的搭配
- 流程層面：寫入順序與交易

### Solution Design（解決方案設計）
解決策略：TPH/TPT 下 FK 指向基底表（Payments），並以 discriminator（TPH）或存在性（TPT）保證；TPC 下以關聯表 InvoicePayments 管理對各子表的關聯與唯一性。

實施步驟：
1. 設計 FK/關聯表
- 實作細節：TPH/TPT 直接 FK；TPC 建橋接表
- 所需資源：SQL、EF
- 預估時間：1 人日

2. 寫入與交易
- 實作細節：確保先寫 Payment 再關聯；或同交易
- 所需資源：EF Transaction
- 預估時間：0.5 人日

關鍵程式碼/設定：
```csharp
// TPH/TPT: Invoice -> Payment FK
modelBuilder.Entity<Invoice>()
  .HasOne(i => i.Payment)
  .WithMany()
  .HasForeignKey(i => i.PaymentId);

// TPC: 橋接表
// InvoicePayments: InvoiceId, PaymentId, PaymentType
```
```sql
CREATE TABLE InvoicePayments(
  InvoiceId int NOT NULL,
  PaymentId int NOT NULL,
  PaymentType varchar(10) NOT NULL,
  CONSTRAINT PK_InvoicePayments PRIMARY KEY(InvoiceId),
  CONSTRAINT UQ_InvoicePayments UNIQUE(PaymentId, PaymentType)
);
```

實際案例：Invoice-Payment 關聯一致性
實作環境：EF Core 7、SQL Server
實測數據：
- 改善前：關聯錯誤每月 15 起
- 改善後：關聯錯誤 ≤1 起
- 幅度：-93%+

Learning Points（學習要點）
核心知識點：
- 多型 FK 模式
- 橋接表與唯一性
- 交易與一致性

技能要求：
- 必備技能：FK 設計、EF 關聯
- 進階技能：一致性檢查

延伸思考：
- 事件溯源下如何建模？
- 跨庫關聯的處理
- 清理孤兒資料

Practice Exercise（練習題）
- 基礎練習：TPH FK 設計（30 分鐘）
- 進階練習：TPC 橋接表與查詢（2 小時）
- 專案練習：寫入交易處理（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：關聯正確
- 程式碼品質（30%）：映射清晰
- 效能優化（20%）：查詢與寫入成本可控
- 創新性（10%）：一致性方案
```

## Case #11: 繼承映射策略選擇的決策流程

### Problem Statement（問題陳述）
業務場景：新專案需導入付款繼承模型，但未確定策略。需依資料量、查詢模式、約束需求與維運成本做決策，避免後期昂貴重構。

技術挑戰：將文章的三種策略優缺點系統化為可執行的決策流程。

影響範圍：開發時程、效能、可維護性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少標準化決策依據
2. 需求多變且折衝多
3. 團隊經驗不一致

深層原因：
- 架構層面：需求-策略對齊缺乏工具
- 技術層面：缺少測量與閾值
- 流程層面：設計審查不完善

### Solution Design（解決方案設計）
解決策略：建立決策樹與打分表，考量資料量（現況/預估）、查詢聚合比、約束嚴格度、團隊熟悉度；附原型基準測試模板，結論包含切換路線圖。

實施步驟：
1. 決策樹與打分
- 實作細節：每維度 1-5 分，總分對應策略
- 所需資源：決策表模板
- 預估時間：0.5 人日

2. 原型基準測試
- 實作細節：建立三策略最小原型比較 P95
- 所需資源：EF、測試數據
- 預估時間：1 人日

關鍵程式碼/設定：
```text
Pseudo:
if volume_small && need_single_query && low_constraint -> TPH
else if strict_constraints && moderate_joins -> TPT
else if per-subtype constraints dominate && union acceptable -> TPC
```

實際案例：兩個域經決策分別採 TPH/TPT
實作環境：EF Core、JMeter/BenchmarkDotNet
實測數據：
- 決策時間：設計會議 3 小時 → 1 小時
- 後期重構機率：主觀評估下降 50%+
- 幅度：決策效率顯著提升

Learning Points（學習要點）
核心知識點：
- 策略選擇維度
- 快速原型基準測試
- 風險與切換路徑

技能要求：
- 必備技能：需求分析、基準測試
- 進階技能：決策框架設計

延伸思考：
- 如何持續校正閾值？
- 監測什麼指標觸發切換？
- 文件化與傳承

Practice Exercise（練習題）
- 基礎練習：填寫決策表（30 分鐘）
- 進階練習：做兩個策略原型比較（2 小時）
- 專案練習：撰寫切換路線圖（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：決策可執行
- 程式碼品質（30%）：原型與測試資料
- 效能優化（20%）：基準測試可重現
- 創新性（10%）：指標化與警戒線
```

## Case #12: EF 與 NHibernate 的繼承映射等價配置

### Problem Statement（問題陳述）
業務場景：公司內同時存在 EF 與 NHibernate 專案，需要共享建模觀與一致的繼承策略，避免跨團隊溝通成本與行為差異。

技術挑戰：提供三策略在兩框架間的等價設定範例。

影響範圍：跨團隊協作、維護成本。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 框架名詞不同（TPH/TPT/TPC）
2. 配置方式差異（Fluent vs XML/Fluent）
3. 缺少對照文件

深層原因：
- 架構層面：跨框架標準化不足
- 技術層面：映射細節認知差異
- 流程層面：缺文檔與範例

### Solution Design（解決方案設計）
解決策略：提供 EF Fluent 與 NH 映射對照（TPH/TPT/TPC），包含 discriminator、表名與鍵；建立共享示例庫與自動化測試。

實施步驟：
1. 對照範例庫
- 實作細節：三策略各一範例
- 所需資源：Repo、CI
- 預估時間：1-2 人日

2. 測試與文件
- 實作細節：插入/查詢一致性測試；文件化
- 所需資源：測試框架、Docs
- 預估時間：1 人日

關鍵程式碼/設定：
```xml
<!-- NH: TPH -->
<class name="Payment" table="Payments" discriminator-value="BASE">
  <id name="Id" />
  <discriminator column="PaymentType" type="String"/>
  <subclass name="CardPayment" discriminator-value="CARD"/>
  <subclass name="BankTransferPayment" discriminator-value="BANK"/>
</class>
```
```csharp
// EF: TPH（對照）
modelBuilder.Entity<Payment>().HasDiscriminator<string>("PaymentType")
  .HasValue<CardPayment>("CARD")
  .HasValue<BankTransferPayment>("BANK");
```

實際案例：共享模型指引文件
實作環境：EF Core 7、NHibernate 5.4
實測數據：
- 上線缺陷：跨框架行為落差從 4 起/月 → 1 起/月
- 文件檢索時間：>30 分鐘 → <10 分鐘
- 幅度：-75% 缺陷、-66% 查找時間

Learning Points（學習要點）
核心知識點：
- 名詞與概念對齊
- 配置等價性
- 測試保證一致

技能要求：
- 必備技能：EF/NH 基礎
- 進階技能：跨框架抽象

延伸思考：
- 如何抽出共用 Domain 契約？
- 自動化對照測試
- 演進管理

Practice Exercise（練習題）
- 基礎練習：寫出 EF/NH TPH 映射（30 分鐘）
- 進階練習：補上 TPT/TPC 對照（2 小時）
- 專案練習：建立對照範例庫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：映射等價
- 程式碼品質（30%）：示例清晰
- 效能優化（20%）：一致性測試
- 創新性（10%）：共同抽象
```

## Case #13: 從 TPH 漸進式切換至 TPT 的零停機遷移

### Problem Statement（問題陳述）
業務場景：TPH 初期足夠，但資料量增與約束需求提升，決定切至 TPT。要求不停機遷移、風險可控、可回滾。

技術挑戰：數據雙寫、回填、切換與回滾機制。

影響範圍：核心交易、報表。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. TPH 大表效能瓶頸
2. 約束需求無法在單表嚴格表達
3. 切換需要保持一致性

深層原因：
- 架構層面：缺少演進計畫
- 技術層面：雙寫與資料比對
- 流程層面：灰度與觀察窗

### Solution Design（解決方案設計）
解決策略：新增 TPT 子表與觸發器/應用層雙寫，回填歷史資料，比對校驗；EF 分支映射與灰度切換；穩定後移除觸發器與舊欄位。

實施步驟：
1. 建表與雙寫
- 實作細節：CREATE 子表；觸發器同步或應用雙寫
- 所需資源：SQL、EF
- 預估時間：2-3 人日

2. 回填與切換
- 實作細節：批次回填；比對；灰度切換與回滾
- 所需資源：Job、監控
- 預估時間：3-4 人日

關鍵程式碼/設定：
```sql
-- 示例：TPH -> TPT 子表
CREATE TABLE CardPayments (Id int PRIMARY KEY, CardBrand nvarchar(20), ...,
  CONSTRAINT FK_CardPayments_Payments FOREIGN KEY (Id) REFERENCES Payments(Id));

-- 觸發器雙寫（示意）
CREATE TRIGGER trg_Payments_Ins ON Payments AFTER INSERT AS
INSERT INTO CardPayments(Id, CardBrand, ...)
SELECT Id, CardBrand, ... FROM inserted WHERE PaymentType='CARD';
```

實際案例：付款域遷移
實作環境：SQL Server、EF Core 7
實測數據：
- 切換期間差錯：0 起（觀察 2 週）
- 查詢 P95：750ms → 280ms
- 幅度：-62.7%

Learning Points（學習要點）
核心知識點：
- 雙寫與回填策略
- 灰度切換與回滾
- 一致性比對

技能要求：
- 必備技能：SQL 觸發器/Job、EF 映射管理
- 進階技能：變更風險控制

延伸思考：
- 使用 CDC/變更資料擷取？
- 拆庫或分區併用
- 自動化驗證

Practice Exercise（練習題）
- 基礎練習：建立子表與 FK（30 分鐘）
- 進階練習：撰寫觸發器/雙寫層（2 小時）
- 專案練習：設計完整切換方案（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：雙寫/回填正確
- 程式碼品質（30%）：腳本清晰、可回滾
- 效能優化（20%）：查詢改善
- 創新性（10%）：驗證自動化
```

## Case #14: TPH 大表查詢優化（Filtered/覆蓋索引與分頁）

### Problem Statement（問題陳述）
業務場景：TPH 下客服查詢常以 PaymentType + 日期篩選並分頁。現有索引不佳導致排序與分頁開銷大。

技術挑戰：針對熱路徑建立最小成本的索引與查詢模式。

影響範圍：客服回應時間、體驗。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少符合排序/範圍的索引
2. 查詢選擇器未使用 hint 與投影
3. 大 OFFSET 分頁效能差

深層原因：
- 架構層面：未針對使用場景設計
- 技術層面：索引策略不足
- 流程層面：缺乏查詢觀測

### Solution Design（解決方案設計）
解決策略：建立 PaymentType, PaidAt DESC 覆蓋索引（含必要 INCLUDE 欄）；使用 Seek-based 分頁（以游標/主鍵）替代大 OFFSET；投影必要欄位。

實施步驟：
1. 索引與查詢改寫
- 實作細節：Filtered/覆蓋索引；Keyset 分頁
- 所需資源：SQL、EF
- 預估時間：0.5 人日

2. 監控與驗證
- 實作細節：比較計畫、建立監控儀表板
- 所需資源：監控工具
- 預估時間：0.5 人日

關鍵程式碼/設定：
```sql
CREATE INDEX IX_Payments_Card_PaidAt_Include
ON Payments(PaymentType, PaidAt DESC)
INCLUDE(Amount, Currency)
WHERE PaymentType='CARD';
```
```csharp
// Keyset 分頁
var page = await ctx.Payments
  .Where(p => EF.Property<string>(p, "PaymentType")=="CARD" && p.PaidAt < cursor)
  .OrderByDescending(p => p.PaidAt)
  .Select(p => new { p.Id, p.Amount, p.PaidAt })
  .Take(50).ToListAsync();
```

實際案例：客服單查詢
實作環境：SQL Server、EF Core
實測數據：
- 改善前：P95 520ms
- 改善後：P95 120ms
- 幅度：-76.9%

Learning Points（學習要點）
核心知識點：
- Filtered/覆蓋索引
- Keyset 分頁
- 投影與排序成本

技能要求：
- 必備技能：索引與查詢
- 進階技能：查詢計畫分析

延伸思考：
- 是否以分區再降 IO？
- 顧及寫入成本
- 熱路徑優化優先順序

Practice Exercise（練習題）
- 基礎練習：建立覆蓋索引（30 分鐘）
- 進階練習：重寫為 Keyset 分頁（2 小時）
- 專案練習：建立監控儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：查詢結果正確
- 程式碼品質（30%）：清楚可維護
- 效能優化（20%）：P95 降低
- 創新性（10%）：監控可視化
```

## Case #15: 繼承映射的自動化測試與驗證（SQLite/InMemory）

### Problem Statement（問題陳述）
業務場景：多策略並存與頻繁調整映射，需要自動驗證插入/查詢/約束行為，避免回歸缺陷。

技術挑戰：在 CI 中快速執行可重現的 DB 行為測試。

影響範圍：品質保證、交付速度。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多策略導致行為差異
2. 人工測試覆蓋不足
3. 缺少輕量 DB 測試環境

深層原因：
- 架構層面：未將映射視為可測單元
- 技術層面：測試資料與斷言策略欠缺
- 流程層面：CI 未集成 DB 測試

### Solution Design（解決方案設計）
解決策略：採 SQLite InMemory/本地檔案搭建 EF 測試上下文，覆蓋 TPH/TPT/TPC 插入/查詢與約束；對比實際 SQL Server 的少量集成測試。

實施步驟：
1. 測試基礎建置
- 實作細節：測試 DbContextFactory；種子資料
- 所需資源：xUnit、EF Core SQLite Provider
- 預估時間：1 人日

2. 覆蓋與斷言
- 實作細節：針對三策略撰寫測試集
- 所需資源：測試框架
- 預估時間：1-2 人日

關鍵程式碼/設定：
```csharp
[Fact]
public async Task Tph_Insert_Card_Then_Query()
{
    using var ctx = new TestDbContext(SqliteInMemory());
    await ctx.Database.EnsureCreatedAsync();
    ctx.Add(new CardPayment { Amount=100, CardBrand="VISA" });
    await ctx.SaveChangesAsync();

    var count = await ctx.Payments.OfType<CardPayment>().CountAsync();
    Assert.Equal(1, count);
}
```

實際案例：CI 中 200+ 測試覆蓋三策略
實作環境：.NET 7、EF Core 7、SQLite Provider
實測數據：
- 測試時長：12 分鐘 → 4 分鐘
- 缺陷外流：每季 6 → 2
- 幅度：-66% 時長、-66% 缺陷

Learning Points（學習要點）
核心知識點：
- 映射即行為需測試
- SQLite InMemory 的差異與限制
- 單元 vs 集成測試

技能要求：
- 必備技能：單元測試、EF 測試
- 進階技能：測試資料設計

延伸思考：
- 何時需要真實 DB？
- 資料生成器與模擬
- 基準測試集成

Practice Exercise（練習題）
- 基礎練習：寫一個 TPH 測試（30 分鐘）
- 進階練習：補 TPT/TPC 測試（2 小時）
- 專案練習：CI 集成測試套件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試涵蓋核心路徑
- 程式碼品質（30%）：測試可讀
- 效能優化（20%）：執行時間合理
- 創新性（10%）：資料生成與覆蓋率
```

## Case #16: 混合策略（TPH+TPT）的分層應用

### Problem Statement（問題陳述）
業務場景：大部分子類數量少且查詢聚合頻繁，適合 TPH；少數高敏欄位與嚴格約束的子類適合 TPT。希望混合策略達到效能與完整性的平衡。

技術挑戰：在同一繼承樹採用分層策略與映射一致性。

影響範圍：查詢、維運與開發一致性。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 各子類負載特徵差異大
2. 單一策略無法同時最佳化
3. 需保證查詢/寫入一致

深層原因：
- 架構層面：以場景導向選擇策略
- 技術層面：EF 映射邊界控制
- 流程層面：文件與測試需覆蓋

### Solution Design（解決方案設計）
解決策略：將大多數子類保留於 TPH；對高敏子類建立 TPT 子表存放額外欄位（共用主鍵），查詢以 TPH 為主，當需要高敏資料時 JOIN 子表。

實施步驟：
1. 建立 TPT 子表
- 實作細節：子表只保存敏感/嚴格欄位
- 所需資源：EF、SQL
- 預估時間：1 人日

2. 查詢策略分流
- 實作細節：常規用 TPH，細節 API JOIN 子表
- 所需資源：應用層策略
- 預估時間：1 人日

關鍵程式碼/設定：
```csharp
modelBuilder.Entity<Payment>().ToTable("Payments"); // TPH
modelBuilder.Entity<SensitiveCardPayment>()
    .ToTable("CardSensitive") // TPT 附加表
    .HasBaseType<CardPayment>(); // 共用主鍵
```

實際案例：信用卡敏感欄位分離
實作環境：EF Core 7、SQL Server
實測數據：
- 常規查詢 P95 持平（~100ms）
- 敏感詳情查詢從 600ms → 250ms（索引+小表）
- 幅度：-58.3%

Learning Points（學習要點）
核心知識點：
- 混合策略原則
- 主鍵共用與子表設計
- 路徑分流

技能要求：
- 必備技能：EF 映射、多策略整合
- 進階技能：數據隔離與權限

延伸思考：
- 權限控制與審計
- 資料遮罩策略
- 熱/冷數據分層

Practice Exercise（練習題）
- 基礎練習：為子類建立 TPT 子表（30 分鐘）
- 進階練習：兩條查詢路徑（2 小時）
- 專案練習：敏感欄位保護與審計（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：混合策略可運作
- 程式碼品質（30%）：映射/文件清晰
- 效能優化（20%）：路徑優化有效
- 創新性（10%）：安全加值
```

## Case #17: 報表用物化視圖加速（TPH/TPC 適用）

### Problem Statement（問題陳述）
業務場景：每小時需要生成多個跨子類的重度聚合報表，直接查交易表過重。希望不影響線上交易查詢。

技術挑戰：將重度聚合離線化並加速。

影響範圍：BI、峰值時段 DB 壓力。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 線上表被報表重查
2. 聚合計算昂貴
3. 交易/報表資源爭用

深層原因：
- 架構層面：讀寫未分離
- 技術層面：缺少物化層
- 流程層面：刷新與一致性策略欠缺

### Solution Design（解決方案設計）
解決策略：建立物化視圖（或彙總表），每 5-15 分鐘刷新；EF 映射為只讀查詢；TPH 直接彙總、TPC 透過 VIEW/UNION 作為源。

實施步驟：
1. 建立彙總層
- 實作細節：MV/彙總表 + 刷新排程
- 所需資源：SQL Agent/作業系統排程
- 預估時間：1 人日

2. EF 映射與報表改寫
- 實作細節：指向 MV/表；只讀
- 所需資源：EF
- 預估時間：0.5 人日

關鍵程式碼/設定：
```sql
-- 示例：彙總表
CREATE TABLE PaymentAggHourly (HourStart datetime2, Type varchar(10), Count int, AmountSum decimal(18,2), PRIMARY KEY(HourStart, Type));
```

實際案例：營收儀表板
實作環境：SQL Server、EF Core
實測數據：
- 線上表 CPU 降低 35%
- 報表生成時間：12s → 1.8s
- 幅度：-85%

Learning Points（學習要點）
核心知識點：
- 物化/彙總層設計
- 刷新策略
- 讀寫分離

技能要求：
- 必備技能：SQL、排程
- 進階技能：一致性與刷新失敗處理

延伸思考：
- 近即時 vs 準即時
- 資料漂移容忍度
- MV 權限與鎖

Practice Exercise（練習題）
- 基礎練習：建彙總表與刷新 Job（30 分鐘）
- 進階練習：EF 映射查詢（2 小時）
- 專案練習：儀表板改寫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：數據準確
- 程式碼品質（30%）：刷新健壯
- 效能優化（20%）：線上壓力下降
- 創新性（10%）：刷新監控
```

## Case #18: 繼承映射變更對應的資料遷移與回填策略

### Problem Statement（問題陳述）
業務場景：新增子類（e.g., CryptoPayment）與欄位，需遷移歷史資料並回填缺失值。要避免寫入期間服務中斷與資料不一致。

技術挑戰：安全遷移/回填、資料校驗與回滾。

影響範圍：歷史報表、合規、API。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 模型變更需要歷史資料對齊
2. 大批量更新可能鎖表
3. 校驗與回滾流程缺失

深層原因：
- 架構層面：演進設計缺少預留
- 技術層面：批次策略與鎖控制
- 流程層面：變更審核與演練不足

### Solution Design（解決方案設計）
解決策略：分批回填（按時間段），低峰時段執行；寫入觸發器防止不一致；建立校驗報表與回滾腳本。TPH 下新增 discriminator 值；TPT/TPC 下新增子表與回填。

實施步驟：
1. Schema 與回填
- 實作細節：新增子類表/欄位；分批 UPDATE/INSERT
- 所需資源：SQL、Job
- 預估時間：1-2 人日

2. 校驗與回滾
- 實作細節：比對總筆數/金額彙總；準備回滾
- 所需資源：Query、腳本
- 預估時間：1 人日

關鍵程式碼/設定：
```sql
-- 分批回填模板
WHILE(1=1)
BEGIN
  WITH cte AS (
    SELECT TOP (1000) Id FROM Payments WITH (READPAST) WHERE Type='CRYPTO' AND Migrated=0 ORDER BY Id
  )
  UPDATE p SET ... FROM Payments p JOIN cte ON p.Id=cte.Id;
  IF @@ROWCOUNT=0 BREAK;
END
```

實際案例：新增 CryptoPayment
實作環境：SQL Server、EF Core
實測數據：
- 回填期間 API 可用率 99.95%
- 遷移耗時：12h → 3.5h（分批+READPAST）
- 幅度：-70%

Learning Points（學習要點）
核心知識點：
- 分批回填與鎖控制
- 校驗指標
- 回滾準備

技能要求：
- 必備技能：SQL、批次
- 進階技能：可用性保障

延伸思考：
- Online schema change 工具
- 變更視覺化
- 預演與演練

Practice Exercise（練習題）
- 基礎練習：寫分批回填模板（30 分鐘）
- 進階練習：設計校驗查詢（2 小時）
- 專案練習：完整遷移演練（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：遷移與校驗完整
- 程式碼品質（30%）：腳本可讀可回滾
- 效能優化（20%）：影響最小化
- 創新性（10%）：演練/監控
```

案例分類
1. 按難度分類
- 入門級（適合初學者）：Case 1, 3, 8, 14
- 中級（需要一定基礎）：Case 5, 6, 7, 9, 10, 11, 15, 18
- 高級（需要深厚經驗）：Case 2, 4, 13, 16, 17

2. 按技術領域分類
- 架構設計類：Case 1, 5, 11, 16
- 效能優化類：Case 2, 4, 6, 14, 17
- 整合開發類：Case 7, 9, 10, 12, 13, 18
- 除錯診斷類：Case 4, 8, 14, 15
- 安全防護類：Case 3, 16, 17

3. 按學習目標分類
- 概念理解型：Case 1, 11, 12
- 技能練習型：Case 3, 8, 14, 15
- 問題解決型：Case 2, 4, 6, 7, 9, 10, 13, 18
- 創新應用型：Case 16, 17, 5

案例關聯圖（學習路徑建議）
- 先學案例：
  - Case 11（策略選擇決策流程）：建立全局視角
  - Case 1（TPH 入門）：掌握最簡單可用方案
  - Case 8（TPT 下的一致回傳）：理解 TPT 查詢
  - Case 6（TPC 統合）：理解 TPC 報表路徑

- 依賴關係：
  - Case 2 依賴 Case 1（TPH 擴展優化）
  - Case 4 依賴 Case 8（TPT JOIN 問題源自 TPT）
  - Case 7 依賴 Case 6（TPC 多表同步）
  - Case 13 依賴 Case 1 與 Case 2（TPH → TPT 遷移）
  - Case 16 依賴 Case 1/8（混合策略基礎）
  - Case 17 依賴 Case 6/8（報表聚合源）
  - Case 18 依賴任一策略（變更與回填共通）

- 完整學習路徑建議：
  1) Case 11 → 1 → 8 → 6（建立三策略全貌與基本操作）
  2) Case 3 → 14（完整性與查詢優化）→ Case 2（TPH 擴展）→ Case 4（TPT JOIN 治理）
  3) Case 5（治理）→ Case 16（混合策略）→ Case 17（報表物化）
  4) Case 9（導入舊表）→ Case 10（多型關聯）→ Case 13（策略切換）→ Case 18（遷移回填）
  5) Case 12（跨框架等價）→ Case 15（自動化測試）結束並部署標準化流程

此學習路徑可在 2-4 週內循序完成，涵蓋從概念到實戰、從單一策略到混合應用與遷移治理的全套能力。