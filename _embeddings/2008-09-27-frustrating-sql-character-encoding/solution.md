## Case #1: 中繼資料庫 + Linked Server 的跨系統資料轉換架構

### Problem Statement（問題陳述）
**業務場景**：客戶 A 系統資料需整理修正後匯入我們維運的 B 系統。因 A/B 兩方 IT 多為外包，直接對接常陷入責任釐清與排程僵局。為可控地完成清洗與搬移，決定在我方環境先建中繼資料庫，透過 Linked Server 從 A 拉資料，進行一連串修正，再送往 B。
**技術挑戰**：跨伺服器、跨編碼的資料搬運，需避免亂碼與型別/定序不一致；同時提供可重複、可回溯的 ETL 管線。
**影響範圍**：若設計不當，將造成匯入失敗、資料誤植或長期依賴外包方配合而延誤時程。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. A→B 之間資料需修正，無法直接複製表格
2. 兩端編碼/定序不同，直接 SELECT 會產生亂碼
3. 外包協作溝通成本高，環境調整與補丁無法即時配合

**深層原因**：
- 架構層面：缺少可控的中繼層，跨系統耦合度高
- 技術層面：未事先統一 Unicode/Collation，造成跨伺服器轉碼風險
- 流程層面：缺乏標準 ETL 流程與驗證關卡

### Solution Design（解決方案設計）
**解決策略**：建立中繼資料庫（Staging），在我方完全可控的 SQL Server 中，以 Linked Server 從 A 系統批次讀入原始資料，先轉成 Unicode 並落地，再依需求進行校正與清洗，最後輸出到 B 系統。

**實施步驟**：
1. 規劃中繼資料表結構
- 實作細節：目標欄位使用 NVARCHAR/NVARCHAR(MAX) 儲存中文
- 所需資源：SQL Server、資料字典
- 預估時間：0.5 天

2. 建立 Linked Server 與安全性對應
- 實作細節：使用 SQLNCLI 或對應 OLE DB Provider，設定登入映射
- 所需資源：DBA 權限、A 系統連線資訊
- 預估時間：0.5 天

3. 跨伺服器載入資料與 Unicode 正規化
- 實作細節：SELECT/INSERT 時使用 CONVERT 為 NTEXT/NVARCHAR
- 所需資源：T-SQL 腳本
- 預估時間：0.5 天

4. 制定清洗/驗證/回補流程
- 實作細節：增量重跑、差異比對、錯誤重試
- 所需資源：T-SQL、排程
- 預估時間：1 天

**關鍵程式碼/設定**：
```sql
-- 建立 Linked Server（示意）
EXEC sp_addlinkedserver
  @server = N'A_LINK',
  @srvproduct = N'SQL Server',
  @provider = N'SQLNCLI',
  @datasrc = N'A_HOST';

-- 建立中繼表（使用 Unicode 型別）
CREATE TABLE dbo.Stg_Customer (
  Id        INT PRIMARY KEY,
  NameZh    NVARCHAR(200),
  AddressZh NVARCHAR(500),
  UpdatedAt DATETIME2
);

-- 從 A 系統拉資料到中繼（轉為 Unicode）
INSERT INTO dbo.Stg_Customer (Id, NameZh, AddressZh, UpdatedAt)
SELECT
  Id,
  CONVERT(NVARCHAR(200), Name),        -- 轉 Unicode
  CONVERT(NVARCHAR(500), Address),     -- 轉 Unicode
  UpdatedAt
FROM A_LINK.DB_A.dbo.Customer;
```

實際案例：以中繼表承接 A 的整表資料，再進行更新欄位、合併、清洗，最後由我方掌控時間與責任，避免外包雙方推諉。
實作環境：SQL Server（約 2005/2008 時代），Linked Server 透過 SQL Native Client。
實測數據：
- 改善前：直連跨系統需協調外包排程，資料亂碼比對困難
- 改善後：以中繼層完整掌控載入與清洗，匯入 B 系統前可 100% 校驗
- 改善幅度：可控性/成功率提升到 100%（以我方可驗證為準）

Learning Points（學習要點）
核心知識點：
- 中繼層降低跨系統耦合與責任不清
- Unicode 型別是中文跨伺服器傳輸的基本保障
- Linked Server 基本設定與安全性對應

技能要求：
- 必備技能：T-SQL、Linked Server 設定、Unicode/Collation 基礎
- 進階技能：ETL 流程設計、資料驗證與容錯

延伸思考：
- 還能應用於異質來源（Oracle/MySQL）到 SQL Server 的整合
- 風險：Linked Server 效能/穩定性受網路與 Provider 影響
- 可進一步優化為 SSIS 或作業排程、增量同步

Practice Exercise（練習題）
- 基礎練習：建立一個 Linked Server 並成功查詢遠端表
- 進階練習：把遠端表落地到中繼表，使用 NVARCHAR 型別
- 專案練習：設計一條 ETL 流程，包含落地、清洗、驗證、導出

Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確拉到資料並落地中繼表
- 程式碼品質（30%）：型別設計正確、錯誤處理與日誌完善
- 效能優化（20%）：批次處理、索引與鎖定控制合理
- 創新性（10%）：有增量/重跑/錯誤恢復機制


## Case #2: Linked Server 中文亂碼，轉成 NTEXT/NVARCHAR 修正

### Problem Statement（問題陳述）
**業務場景**：從 A 系統透過 Linked Server 查詢中文欄位，直接 SELECT 看到的是亂碼或問號，導致後續清洗與比對不可行。
**技術挑戰**：跨伺服器的字元集轉換，char/varchar 經 Provider 轉碼時失真。
**影響範圍**：中文欄位不可用，造成全流程中斷或人工比對成本暴增。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 來源端用非 Unicode（varchar）儲存中文
2. Linked Server 的 Provider 在不同定序/碼頁下轉換失真
3. 目的端以非 Unicode 型別接收（或未轉換）

**深層原因**：
- 架構層面：未強制跨系統以 Unicode 溝通
- 技術層面：忽略 CONVERT/CAST 的明確轉型
- 流程層面：缺少跨系統欄位型別對齊規範

### Solution Design（解決方案設計）
**解決策略**：在查詢時明確把來源欄位 CONVERT 成 NTEXT/NVARCHAR，在目的表用 NVARCHAR/NVARCHAR(MAX) 接收，確保全鏈路以 Unicode 傳遞。

**實施步驟**：
1. 確認來源欄位與目的欄位型別
- 實作細節：sys.columns 檢查資料型別
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 修改查詢加上 CONVERT
- 實作細節：CONVERT(NTEXT|NVARCHAR) 包裹問題欄位
- 所需資源：T-SQL
- 預估時間：0.25 天

3. 驗證亂碼消失
- 實作細節：抽樣比對原字串與結果
- 所需資源：驗證腳本
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
-- 直接跨伺服器查詢（四段式命名），並轉為 Unicode
SELECT
  Id,
  CONVERT(NTEXT, Name)     AS NameZh,
  CONVERT(NTEXT, Address)  AS AddressZh
FROM A_LINK.DB_A.dbo.Customer;

-- 推薦用法（現代 SQL Server）：改用 NVARCHAR(MAX)
SELECT
  Id,
  CONVERT(NVARCHAR(MAX), Name)    AS NameZh,
  CONVERT(NVARCHAR(MAX), Address) AS AddressZh
FROM A_LINK.DB_A.dbo.Customer;
```

實際案例：直接 SELECT 後亂碼，改用 CONVERT 成 NTEXT 後顯示正常。
實作環境：SQL Server + Linked Server（SQL Native Client）。
實測數據：
- 改善前：中文欄位亂碼/問號（不可比對）
- 改善後：中文顯示正確
- 改善幅度：欄位可用率由 0% → 100%

Learning Points（學習要點）
核心知識點：
- Unicode 型別的必要性
- Linked Server 與碼頁/定序的互動
- CONVERT 與 CAST 的差異

技能要求：
- 必備技能：T-SQL、資料型別、Linked Server 查詢
- 進階技能：跨系統型別對齊策略

延伸思考：
- 同招也適用於 CSV/BCP 匯入時的亂碼修正
- 風險：NTEXT 已淘汰，建議用 NVARCHAR(MAX)
- 優化：在遠端端點即轉型（OPENQUERY）

Practice Exercise（練習題）
- 基礎：將遠端 varchar 欄位改以 CONVERT 成 NVARCHAR(MAX) 查詢
- 進階：把結果寫入 NVARCHAR 目的表，抽樣驗證
- 專案：建立一個跨伺服器中文欄位轉換與驗證流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：亂碼消除、資料正確
- 程式碼品質（30%）：型別適當、邏輯清晰
- 效能優化（20%）：最小必要轉換
- 創新性（10%）：加入驗證與報表


## Case #3: SELECT INTO 後資料串行污染（上一筆殘影）之異常鑑別

### Problem Statement（問題陳述）
**業務場景**：單純 SELECT 已能看到正常中文，但改為 SELECT INTO 暫存或中繼表後，出現「上一筆資料殘影」混入當前列等怪異字串拼接。
**技術挑戰**：同一查詢路徑在落地時才出錯，難以直覺定位為編碼或定序問題。
**影響範圍**：資料錯亂且非簡單亂碼，可能發生誤匯入，後果嚴重。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. SELECT 與 SELECT INTO 的執行路徑/Provider 處理不同
2. 文字緩衝未正確清空或終止（疑似 0x00 結尾缺失）
3. 某驅動/版本缺陷導致跨列資料被覆寫

**深層原因**：
- 架構層面：過度依賴單一路徑（SELECT INTO）落地
- 技術層面：Provider/SQL Native Client 版本缺陷
- 流程層面：缺乏自動化差異比對，問題延後發現

### Solution Design（解決方案設計）
**解決策略**：建立鑑別流程：同時執行直接 SELECT 與 SELECT INTO，對比兩者結果差異；一旦 SELECT INTO 出現「上一筆殘影」樣態，判定非 Collation/編碼設定問題，改用替代路徑落地。

**實施步驟**：
1. 產生對比樣本
- 實作細節：TOP + ORDER BY 固定順序，確保可重現
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 落地與比對
- 實作細節：SELECT INTO 後與直接 SELECT 結果 JOIN 比對
- 所需資源：比對腳本
- 預估時間：0.25 天

3. 樣態判讀與結論
- 實作細節：若出現跨列殘影，判定為 Provider/路徑 bug
- 所需資源：分析報告
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
-- 直接查
WITH S AS (
  SELECT TOP (100) Id, Name, Address
  FROM A_LINK.DB_A.dbo.Customer
  ORDER BY Id
)
SELECT * FROM S;  -- 基準

-- SELECT INTO 落地
SELECT * INTO #S_Landed FROM S;

-- 差異比對
SELECT a.Id, a.Name AS SrcName, b.Name AS LandedName
FROM S a
JOIN #S_Landed b ON a.Id = b.Id
WHERE a.Name <> b.Name;
```

實際案例：第 33 筆出現前一筆內容殘影，非單純亂碼，判定為 buffer/overflow 類缺陷。
實作環境：SQL Server + Linked Server（SQL Native Client）。
實測數據：
- 改善前：第 33 筆出現污染
- 改善後：改用其他落地路徑（見 Case #4/6）後 0 筆污染
- 改善幅度：錯誤筆數 1 → 0（100% 修復）

Learning Points（學習要點）
核心知識點：
- SELECT vs SELECT INTO 執行差異
- 異常樣態輔助定位根因
- 自動化差異比對的重要性

技能要求：
- 必備技能：T-SQL、視圖/CTE、JOIN 比對
- 進階技能：可重現性測試與樣態分析

延伸思考：
- 同法可鑑別各種 Provider 不一致問題
- 風險：未固定順序（缺 ORDER BY）可能導致誤判
- 優化：包裝成每日健康檢查

Practice Exercise（練習題）
- 基礎：寫一段 SELECT 與 SELECT INTO 的對比腳本
- 進階：把差異輸出成報表含樣本值
- 專案：將比對納入 ETL pipeline 的自動驗收

Assessment Criteria（評估標準）
- 功能完整性（40%）：能確實找出差異
- 程式碼品質（30%）：順序可控、可重現
- 效能優化（20%）：比對只對疑似欄位
- 創新性（10%）：報表化/告警化


## Case #4: 以 CURSOR 逐筆抓取＋NVARCHAR 變數更新，繞過 Provider Bug

### Problem Statement（問題陳述）
**業務場景**：SELECT INTO 會導致跨列污染；直接 SELECT 正常。需找一條可行路徑安全落地資料。
**技術挑戰**：避免走到會觸發缺陷的資料路徑，又能保證中文正確。
**影響範圍**：若不避開，將把污染資料匯入 B 系統，造成重大錯誤。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. SELECT INTO 落地路徑觸發 Provider 緩衝處理缺陷
2. 文字緩衝未清空/結尾處理有誤
3. 非 Collation 問題，單純 SELECT 是正確的

**深層原因**：
- 架構層面：缺替代落地手段
- 技術層面：未明確以 NVARCHAR 變數中轉
- 流程層面：未建立回退方案

### Solution Design（解決方案設計）
**解決策略**：用 CURSOR 逐筆 FETCH，將文字欄位讀入 NVARCHAR 變數後再 UPDATE 回中繼表，確保每筆字串走安全路徑，避免共享緩衝的副作用。

**實施步驟**：
1. 預先建立中繼表（NVARCHAR 欄位）
- 實作細節：避免 SELECT INTO，改用顯式 DDL
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 以 INSERT…SELECT 批次載入非問題欄位
- 實作細節：問題欄位先以 NULL/預留欄位
- 所需資源：T-SQL
- 預估時間：0.25 天

3. 用 CURSOR 逐筆更新問題欄位
- 實作細節：FETCH → NVARCHAR 變數 → UPDATE
- 所需資源：T-SQL
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- 預先建立中繼表
CREATE TABLE dbo.Stg_Customer (
  Id        INT PRIMARY KEY,
  NameZh    NVARCHAR(200) NULL,
  AddressZh NVARCHAR(500) NULL
);

-- 先載入非問題欄位（假設 NameZh, AddressZh 是問題欄位）
INSERT INTO dbo.Stg_Customer (Id)
SELECT Id
FROM A_LINK.DB_A.dbo.Customer;

-- Cursor 逐筆抓取後更新
DECLARE @Id INT, @NameZh NVARCHAR(200), @AddressZh NVARCHAR(500);

DECLARE cur FAST_FORWARD FOR
SELECT Id,
       CONVERT(NVARCHAR(200), Name),
       CONVERT(NVARCHAR(500), Address)
FROM A_LINK.DB_A.dbo.Customer
ORDER BY Id;

OPEN cur;
FETCH NEXT FROM cur INTO @Id, @NameZh, @AddressZh;
WHILE @@FETCH_STATUS = 0
BEGIN
  UPDATE dbo.Stg_Customer
     SET NameZh = @NameZh,
         AddressZh = @AddressZh
   WHERE Id = @Id;

  FETCH NEXT FROM cur INTO @Id, @NameZh, @AddressZh;
END
CLOSE cur; DEALLOCATE cur;
```

實際案例：改為 Cursor 路徑後，原本第 33 筆污染消失，中文正確。
實作環境：SQL Server + Linked Server。
實測數據：
- 改善前：第 33 筆欄位出現上一筆殘影
- 改善後：0 筆污染
- 改善幅度：正確率 100%

Learning Points（學習要點）
核心知識點：
- Row-by-row 可作為 Provider 缺陷的繞道
- NVARCHAR 變數可避免緩衝共用副作用
- 顯式 DDL 控制資料型別

技能要求：
- 必備技能：T-SQL Cursor、UPDATE、變數
- 進階技能：混合式 ETL 設計（批次+逐筆）

延伸思考：
- 何時該接受較慢但正確的路徑？
- 風險：Cursor 效能較差
- 優化：FAST_FORWARD、批次提交（見 Case #12）

Practice Exercise（練習題）
- 基礎：將一個文字欄位以 Cursor 逐筆讀入變數並更新
- 進階：將多欄位以 Cursor 更新，中途失敗可重試
- 專案：混合式流程（批次載入 + 逐筆修正）

Assessment Criteria（評估標準）
- 功能完整性（40%）：資料 0 污染
- 程式碼品質（30%）：錯誤處理、資源釋放
- 效能優化（20%）：Cursor 選項、批次化
- 創新性（10%）：混合式思路


## Case #5: 以 NVARCHAR 變數作為跨伺服器讀取的 Unicode 保險箱

### Problem Statement（問題陳述）
**業務場景**：跨 Linked Server 讀取中文欄位時，直接落地有風險。需要安全的中轉容器確保字串不被錯誤轉碼或污染。
**技術挑戰**：Provider/路徑不可控，需在 SQL 中建立可信賴的緩衝。
**影響範圍**：若中轉不安全，將擴散錯誤。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 來源為非 Unicode，跨伺服器有轉碼流程
2. 直接落地會走到缺陷路徑
3. 需要顯式宣告 Unicode 緩衝避免污染

**深層原因**：
- 架構層面：資料傳輸缺少型別保護
- 技術層面：未以 NVARCHAR 變數接收
- 流程層面：未規定跨系統讀取時的型別策略

### Solution Design（解決方案設計）
**解決策略**：所有跨伺服器讀取的中文欄位，先 CONVERT 成 NVARCHAR，放入 NVARCHAR 變數，再寫入目標表。

**實施步驟**：
1. 標註所有中文欄位
- 實作細節：欄位清單與型別
- 所需資源：資料字典
- 預估時間：0.25 天

2. 以變數中轉寫入
- 實作細節：DECLARE NVARCHAR 變數 → SELECT…CONVERT → INSERT/UPDATE
- 所需資源：T-SQL
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
DECLARE @NameZh NVARCHAR(200);

SELECT @NameZh = CONVERT(NVARCHAR(200), Name)
FROM A_LINK.DB_A.dbo.Customer WHERE Id = 33;

UPDATE dbo.Stg_Customer
  SET NameZh = @NameZh
WHERE Id = 33;
```

實際案例：透過變數中轉後，不再復現上一筆殘影污染。
實作環境：SQL Server。
實測數據：
- 改善前：指定筆數出現字串污染
- 改善後：污染消失
- 改善幅度：100% 修正該筆錯誤

Learning Points（學習要點）
核心知識點：
- 變數是安全緩衝的技巧
- CONVERT 時機點影響結果
- 目的欄位選擇 NVARCHAR

技能要求：
- 必備技能：T-SQL 變數、UPDATE
- 進階技能：欄位級別的安全策略

延伸思考：
- 可封裝為 Stored Procedure 統一調用
- 風險：粒度細、工作量增加
- 優化：部分欄位才用變數（見 Case #7）

Practice Exercise（練習題）
- 基礎：單筆用變數轉存
- 進階：批次以 Cursor+變數轉存
- 專案：把變數中轉封裝為可重用程式

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確寫入
- 程式碼品質（30%）：可讀性、重用性
- 效能優化（20%）：僅在必要欄位使用
- 創新性（10%）：Template 化


## Case #6: 放棄 SELECT INTO，預先建立目標表（NVARCHAR）再 INSERT

### Problem Statement（問題陳述）
**業務場景**：SELECT INTO 落地觸發缺陷。需改為顯式定義目標表型別，避免隱式推斷導致走到問題路徑。
**技術挑戰**：保證目標表的 Unicode 型別，並避開 Provider 潛在問題。
**影響範圍**：避免污染與型別不當造成的二次風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. SELECT INTO 讓型別由來源推斷，難控
2. 推斷過程可能走到缺陷邏輯
3. 目標欄位未明確使用 NVARCHAR

**深層原因**：
- 架構層面：依賴隱式型別推斷
- 技術層面：未顯式定義 Unicode 欄位
- 流程層面：未制定建模規範

### Solution Design（解決方案設計）
**解決策略**：以 CREATE TABLE 明確定義目標表結構（特別是 NVARCHAR），之後用 INSERT INTO…SELECT，查詢端同樣 CONVERT Unicode。

**實施步驟**：
1. 建表（顯式型別）
- 實作細節：NVARCHAR/MAX、索引與主鍵
- 所需資源：T-SQL
- 預估時間：0.25 天

2. INSERT INTO…SELECT
- 實作細節：來源端 CONVERT，目的端直接接收
- 所需資源：T-SQL
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
CREATE TABLE dbo.Stg_Order (
  OrderId  INT PRIMARY KEY,
  NoteZh   NVARCHAR(MAX) NULL
);

INSERT INTO dbo.Stg_Order (OrderId, NoteZh)
SELECT OrderId, CONVERT(NVARCHAR(MAX), Note)
FROM A_LINK.DB_A.dbo.[Order];
```

實際案例：以顯式建表 + INSERT，避免 SELECT INTO 的污染問題。
實作環境：SQL Server。
實測數據：
- 改善前：SELECT INTO 後資料污染
- 改善後：INSERT INTO 顯式表後資料正確
- 改善幅度：污染筆數降為 0

Learning Points（學習要點）
核心知識點：
- SELECT INTO vs INSERT INTO 的差異
- 顯式建模控制型別
- NVARCHAR(MAX) 取代 NTEXT

技能要求：
- 必備技能：DDL、DML
- 進階技能：模式設計與型別規劃

延伸思考：
- 大表需注意記錄大小與行外儲存
- 風險：初期建模成本
- 優化：用表型別/同構模板

Practice Exercise（練習題）
- 基礎：建立目標表並 INSERT INTO…SELECT
- 進階：加入索引與主鍵
- 專案：把多張表改為顯式建表路徑

Assessment Criteria（評估標準）
- 功能完整性（40%）：資料正確落地
- 程式碼品質（30%）：建表設計合理
- 效能優化（20%）：最小必要索引
- 創新性（10%）：Template 化建表


## Case #7: 混合式方案：批次複製 + 僅對問題欄位逐筆修正

### Problem Statement（問題陳述）
**業務場景**：全表用 Cursor 過慢，但某些中文欄位才會在落地時出問題。
**技術挑戰**：在正確性與效能間取捨，以最小成本修正。
**影響範圍**：改善整體搬運時間並保證正確。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 只有特定文字欄位在落地時出錯
2. 全量逐筆處理效能差
3. 需要最小化逐筆處理範圍

**深層原因**：
- 架構層面：未分離無風險與高風險欄位
- 技術層面：缺乏分段策略
- 流程層面：未定義欄位級別處理策略

### Solution Design（解決方案設計）
**解決策略**：先批次複製所有非問題欄位，對問題欄位再以 Cursor 逐筆更新，兩者結合達成正確與效率。

**實施步驟**：
1. 批次複製安全欄位
- 實作細節：INSERT INTO…SELECT（排除問題欄位）
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 逐筆更新高風險欄位
- 實作細節：Cursor+NVARCHAR 變數
- 所需資源：T-SQL
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- 先批次複製安全欄位
INSERT INTO dbo.Stg_Customer (Id)
SELECT Id FROM A_LINK.DB_A.dbo.Customer;

-- 再逐筆補問題欄位
DECLARE @Id INT, @NameZh NVARCHAR(200);

DECLARE cur FAST_FORWARD FOR
SELECT Id, CONVERT(NVARCHAR(200), Name)
FROM A_LINK.DB_A.dbo.Customer ORDER BY Id;

OPEN cur;
FETCH NEXT FROM cur INTO @Id, @NameZh;
WHILE @@FETCH_STATUS = 0
BEGIN
  UPDATE dbo.Stg_Customer SET NameZh = @NameZh WHERE Id = @Id;
  FETCH NEXT FROM cur INTO @Id, @NameZh;
END
CLOSE cur; DEALLOCATE cur;
```

實際案例：混合方案在保持正確前提下，顯著減少逐筆處理量。
實作環境：SQL Server。
實測數據：
- 改善前：全表 Cursor，時間較長
- 改善後：僅問題欄位逐筆，正確且耗時下降
- 改善幅度：逐筆處理筆數大幅下降（依欄位比例）

Learning Points（學習要點）
核心知識點：
- 分治法：風險欄位單獨處理
- Row-by-row 與 Set-based 協作
- 效能/正確性取捨

技能要求：
- 必備技能：T-SQL、欄位選擇
- 進階技能：流程優化

延伸思考：
- 自動識別問題欄位
- 風險：欄位清單需維護
- 優化：多執行緒分段處理

Practice Exercise（練習題）
- 基礎：排除欄位的 INSERT INTO…SELECT
- 進階：對單一欄位逐筆補值
- 專案：多欄位混合式搬運

Assessment Criteria（評估標準）
- 功能完整性（40%）：資料正確
- 程式碼品質（30%）：清晰分段
- 效能優化（20%）：逐筆量最小化
- 創新性（10%）：自動欄位分析


## Case #8: 最小可重現腳本：從上百行抽絲剝繭鎖定第 33 筆

### Problem Statement（問題陳述）
**業務場景**：原腳本上百行，錯誤散落且難以追蹤。需要最小可重現以便判讀根因。
**技術挑戰**：在不失真前提下最大限度簡化案例。
**影響範圍**：提升排錯效率、促成正確判斷。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 冗長腳本使症狀被淹沒
2. 執行順序不固定導致結果不穩
3. 缺少固定資料集與順序

**深層原因**：
- 架構層面：無最小重現範本
- 技術層面：缺乏可控測試資料集
- 流程層面：未建立排錯準則

### Solution Design（解決方案設計）
**解決策略**：固定資料集、固定順序（ORDER BY）、僅保留問題欄位，建立小型測試腳本鎖定第 33 筆。

**實施步驟**：
1. 取樣與固定順序
- 實作細節：TOP + ORDER BY
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 刪減無關欄位/邏輯
- 實作細節：只保留出錯欄位
- 所需資源：T-SQL
- 預估時間：0.25 天

3. 對比與紀錄
- 實作細節：輸出差異與樣本值
- 所需資源：T-SQL
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
;WITH S AS (
  SELECT TOP (50) Id, CONVERT(NVARCHAR(200), Name) AS NameZh
  FROM A_LINK.DB_A.dbo.Customer
  ORDER BY Id
)
SELECT * FROM S;   -- 基準

SELECT * INTO #S_Landed FROM S;  -- 觸發缺陷的路徑（示意）

SELECT a.Id, a.NameZh AS Src, b.NameZh AS Landed
FROM S a JOIN #S_Landed b ON a.Id = b.Id
WHERE a.NameZh <> b.NameZh;      -- 鎖定第 33 筆
```

實際案例：成功縮小到第 33 筆的差異，便於判讀為緩衝/溢位類問題。
實作環境：SQL Server。
實測數據：
- 改善前：長腳本難以定位
- 改善後：最小化重現、快速鎖定
- 改善幅度：排錯時間明顯降低

Learning Points（學習要點）
核心知識點：
- 最小可重現原則
- 資料順序對重現的重要性
- 只保留問題欄位

技能要求：
- 必備技能：T-SQL、CTE
- 進階技能：排錯方法論

延伸思考：
- 封裝為自動化重現工具
- 風險：過度簡化會誤判
- 優化：腳本參數化

Practice Exercise（練習題）
- 基礎：寫出 TOP+ORDER BY 的取樣重現
- 進階：輸出差異報表
- 專案：建立團隊重現腳本範本庫

Assessment Criteria（評估標準）
- 功能完整性（40%）：能重現問題
- 程式碼品質（30%）：簡潔、可讀
- 效能優化（20%）：取樣合理
- 創新性（10%）：可重用性


## Case #9: 自動比對器：遠端 SELECT 與本地落地結果差異檢出

### Problem Statement（問題陳述）
**業務場景**：需要在搬運後自動驗證資料，避免污染/亂碼偷偷流入下一階段。
**技術挑戰**：建立可重複的差異檢測與報表。
**影響範圍**：保障資料品質，避免誤匯。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無自動化比對，錯誤晚期發現
2. 搬運路徑多，難人工檢查
3. 高風險欄位需重點監控

**深層原因**：
- 架構層面：缺乏驗收關
- 技術層面：未建立差異檢出 SQL
- 流程層面：未制度化

### Solution Design（解決方案設計）
**解決策略**：以鍵值 JOIN 遠端即時 SELECT 與本地落地表，產生差異清單與統計，納入流程門檻。

**實施步驟**：
1. 建立比對視圖
- 實作細節：同鍵 JOIN、多欄位比對
- 所需資源：T-SQL
- 預估時間：0.5 天

2. 報表輸出
- 實作細節：錯誤筆數、樣本值
- 所需資源：T-SQL
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
SELECT COUNT(*) AS DiffCount
FROM A_LINK.DB_A.dbo.Customer r
JOIN dbo.Stg_Customer l ON r.Id = l.Id
WHERE CONVERT(NVARCHAR(200), r.Name) <> l.NameZh
   OR CONVERT(NVARCHAR(500), r.Address) <> l.AddressZh;

-- 明細
SELECT TOP (50) r.Id, CONVERT(NVARCHAR(200), r.Name) AS SrcName, l.NameZh AS LandedName
FROM A_LINK.DB_A.dbo.Customer r
JOIN dbo.Stg_Customer l ON r.Id = l.Id
WHERE CONVERT(NVARCHAR(200), r.Name) <> l.NameZh
ORDER BY r.Id;
```

實際案例：在導入變更後，自動回歸驗證 0 差異。
實作環境：SQL Server。
實測數據：
- 改善前：手動抽查，易漏
- 改善後：全量比對，0 差異方可過關
- 改善幅度：驗證覆蓋率 0% → 100%

Learning Points（學習要點）
核心知識點：
- 自動化驗收門檻
- 多欄位比對策略
- 轉型一致性

技能要求：
- 必備技能：T-SQL、JOIN 比對
- 進階技能：報表化、門檻化

延伸思考：
- 可每日健康檢查
- 風險：遠端查詢負載
- 優化：快照/落地再比對

Practice Exercise（練習題）
- 基礎：寫出差異筆數查詢
- 進階：輸出差異明細
- 專案：納入 CI/排程之驗收關

Assessment Criteria（評估標準）
- 功能完整性（40%）：準確檢出差異
- 程式碼品質（30%）：可維護
- 效能優化（20%）：負載可控
- 創新性（10%）：自動告警


## Case #10: 排除 Collation 誤解：系統化檢查「不是定序問題」

### Problem Statement（問題陳述）
**業務場景**：面對資料錯亂，常被誤導為編碼/定序問題。需建立快速檢查以排除。
**技術挑戰**：以事證否定定序，避免把時間耗在錯方向。
**影響範圍**：縮短排錯時間，聚焦真正根因。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 直接 SELECT 正常 → 非 Collation 問題
2. SELECT INTO 才壞 → 路徑/Provider 差異
3. 無快速檢查指引

**深層原因**：
- 架構層面：無診斷手冊
- 技術層面：缺乏系統化排除法
- 流程層面：排錯憑直覺

### Solution Design（解決方案設計）
**解決策略**：建立檢查清單：直接 SELECT vs 落地結果、欄位定序、資料庫定序、N 前綴確認，快速做出非 Collation 的結論。

**實施步驟**：
1. 查定序
- 實作細節：DATABASEPROPERTYEX、sys.columns
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 直接查 vs 落地查
- 實作細節：差異比對（Case #9）
- 所需資源：T-SQL
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
-- 資料庫定序
SELECT DB_NAME() AS DbName, DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS DbCollation;

-- 欄位定序
SELECT name, collation_name
FROM sys.columns
WHERE object_id = OBJECT_ID('dbo.Stg_Customer');

-- 若直接 SELECT = 正常、落地 = 異常 → 排除 Collation
```

實際案例：確認非定序問題後，轉向 Provider 路徑缺陷處理（Cursor）。
實作環境：SQL Server。
實測數據：
- 改善前：糾結於 Collation 設定
- 改善後：快速排除，聚焦正確方向
- 改善幅度：排錯時間明顯縮短

Learning Points（學習要點）
核心知識點：
- Collation 與 Unicode 的關係
- 觀察法排除非因
- 檢查清單化

技能要求：
- 必備技能：T-SQL、系統視圖
- 進階技能：診斷方法論

延伸思考：
- 其他常見誤解的清單化
- 風險：過度依賴 checklist
- 優化：自動化檢查

Practice Exercise（練習題）
- 基礎：查一張表的欄位定序
- 進階：寫出「排除 Collation」的判讀腳本
- 專案：建立診斷手冊

Assessment Criteria（評估標準）
- 功能完整性（40%）：能判斷非 Collation
- 程式碼品質（30%）：清晰可用
- 效能優化（20%）：最小查詢
- 創新性（10%）：清單可擴充


## Case #11: 無法升級/打補丁下的風險控管與取捨

### Problem Statement（問題陳述）
**業務場景**：客戶 IT 不願或無法套用 Service Pack/Update。需在現況下交付正確資料。
**技術挑戰**：Vendor bug 存在，需以繞道維持穩定交付。
**影響範圍**：交付時程與品質。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 外包/IT 流程難以快速升版
2. 既知缺陷短期內無法根治
3. 必須以 workaround 落地

**深層原因**：
- 架構層面：對 Vendor 依賴度高
- 技術層面：未設計替代路徑
- 流程層面：缺乏風險記錄與驗收

### Solution Design（解決方案設計）
**解決策略**：採用 Cursor 等 workaround；建立驗收（Case #9）、記錄已知缺陷與繞道方案，納入上線文件並規畫未來升級窗口。

**實施步驟**：
1. Workaround 落地
- 實作細節：Cursor/變數中轉
- 所需資源：T-SQL
- 預估時間：0.5 天

2. 驗收與監控
- 實作細節：差異檢出、告警
- 所需資源：比對腳本
- 預估時間：0.5 天

3. 文件與風險台帳
- 實作細節：缺陷描述、重現步驟、替代方案
- 所需資源：文件
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- 見 Case #4/#9 的 Cursor 與比對腳本
-- 於上線批次最後一關執行差異檢出，非 0 即中止
```

實際案例：不升級的前提下仍達成 0 差異交付。
實作環境：SQL Server。
實測數據：
- 改善前：存在污染風險
- 改善後：以 workaround + 驗收達成 0 污染
- 改善幅度：品質達標

Learning Points（學習要點）
核心知識點：
- 工程取捨與風險控管
- Workaround 的可維護性
- 上線文件與缺陷紀錄

技能要求：
- 必備技能：流程設計、文件撰寫
- 進階技能：風險管理

延伸思考：
- 何時應堅持升級？
- 風險：workaround 技債
- 優化：排程升級窗口

Practice Exercise（練習題）
- 基礎：撰寫一份 workaround 使用說明
- 進階：把差異比對納入上線關卡
- 專案：建立缺陷台帳與升級計畫

Assessment Criteria（評估標準）
- 功能完整性（40%）：流程可執行
- 程式碼品質（30%）：驗收可重現
- 效能優化（20%）：流程耗時可控
- 創新性（10%）：風險可視化


## Case #12: Cursor 效能與穩定性優化（FAST_FORWARD/批次提交/鎖控）

### Problem Statement（問題陳述）
**業務場景**：Cursor 解決正確性，但單執行緒逐筆可能過慢或造成鎖競爭。
**技術挑戰**：優化游標處理效能與穩定性。
**影響範圍**：批次時窗與對線上系統的影響。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 逐筆更新耗時
2. 預設游標鎖定與記錄檔壓力
3. 無批次提交機制

**深層原因**：
- 架構層面：缺少批次化設計
- 技術層面：未使用 FAST_FORWARD/READ_ONLY
- 流程層面：未規劃斷點續傳

### Solution Design（解決方案設計）
**解決策略**：使用 FAST_FORWARD/READ_ONLY、每 N 筆提交、降低鎖範圍，必要時分段處理，避免長交易。

**實施步驟**：
1. 游標選項優化
- 實作細節：FAST_FORWARD/READ_ONLY
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 批次提交
- 實作細節：每 500/1000 筆 COMMIT
- 所需資源：T-SQL
- 預估時間：0.25 天

3. 斷點續傳
- 實作細節：記錄最後處理的鍵值
- 所需資源：控制表
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
DECLARE @Id INT, @NameZh NVARCHAR(200), @count INT = 0;

BEGIN TRAN;
DECLARE cur CURSOR FAST_FORWARD READ_ONLY FOR
SELECT Id, CONVERT(NVARCHAR(200), Name)
FROM A_LINK.DB_A.dbo.Customer ORDER BY Id;

OPEN cur;
FETCH NEXT FROM cur INTO @Id, @NameZh;
WHILE @@FETCH_STATUS = 0
BEGIN
  UPDATE dbo.Stg_Customer SET NameZh = @NameZh WHERE Id = @Id;
  SET @count += 1;

  IF (@count % 1000 = 0)
  BEGIN
    COMMIT TRAN;
    BEGIN TRAN;
  END

  FETCH NEXT FROM cur INTO @Id, @NameZh;
END
CLOSE cur; DEALLOCATE cur;
COMMIT TRAN;
```

實際案例：以批次提交與 FAST_FORWARD，穩定完成大批量逐筆更新。
實作環境：SQL Server。
實測數據：
- 改善前：長交易易造成阻塞
- 改善後：阻塞下降、處理穩定
- 改善幅度：穩定性明顯提升

Learning Points（學習要點）
核心知識點：
- 游標選項的效能影響
- 交易分段與記錄檔壓力
- 斷點續傳設計

技能要求：
- 必備技能：T-SQL、交易控制
- 進階技能：效能調優

延伸思考：
- 可搭配隔離級別調整
- 風險：批次大小不當
- 優化：自適應批次大小

Practice Exercise（練習題）
- 基礎：加上 FAST_FORWARD
- 進階：每 1000 筆提交
- 專案：實作斷點續傳

Assessment Criteria（評估標準）
- 功能完整性（40%）：穩定完成
- 程式碼品質（30%）：交易處理正確
- 效能優化（20%）：阻塞最小化
- 創新性（10%）：自適應控制


## Case #13: 確保字串常值/參數使用 N 前綴以維持 Unicode

### Problem Statement（問題陳述）
**業務場景**：清洗過程常涉及字串常值或參數；若缺 N 前綴，中文仍可能被轉碼成問號。
**技術挑戰**：容易疏忽造成非預期亂碼。
**影響範圍**：校正值/預設值寫入錯誤。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. '中文' 與 N'中文' 意義不同
2. 預設字串常值為非 Unicode
3. 參數型別未宣告為 NVARCHAR

**深層原因**：
- 架構層面：缺少程式碼規範
- 技術層面：忽略 N 前綴
- 流程層面：缺少 Code Review 檢查點

### Solution Design（解決方案設計）
**解決策略**：統一規範：凡中文常值與參數，一律使用 N 前綴與 NVARCHAR 型別。

**實施步驟**：
1. 稽核現有腳本
- 實作細節：檢查 '…' 用法
- 所需資源：搜尋/靜態分析
- 預估時間：0.25 天

2. 修正與防呆
- 實作細節：SQL 樣板、Code Review 清單
- 所需資源：文件+流程
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```sql
-- 錯誤：非 Unicode
UPDATE dbo.Stg_Customer SET NameZh = '測試' WHERE Id = 1;

-- 正確：Unicode
UPDATE dbo.Stg_Customer SET NameZh = N'測試' WHERE Id = 1;

-- 參數亦需 NVARCHAR
DECLARE @v NVARCHAR(200) = N'預設值';
```

實際案例：以 N 前綴統一後，避免了校正過程中的新亂碼。
實作環境：SQL Server。
實測數據：
- 改善前：偶發問號替代
- 改善後：中文正確
- 改善幅度：問題消失

Learning Points（學習要點）
核心知識點：
- N 前綴的必要性
- 參數型別與常值一致性
- 規範的力量

技能要求：
- 必備技能：T-SQL 基礎
- 進階技能：程式碼稽核

延伸思考：
- 可建立 lint 規則
- 風險：大量舊碼修正成本
- 優化：樣板/範本

Practice Exercise（練習題）
- 基礎：修正一段字串常值
- 進階：寫一份檢查清單
- 專案：批次稽核並修正專案

Assessment Criteria（評估標準）
- 功能完整性（40%）：中文不亂碼
- 程式碼品質（30%）：規範一致
- 效能優化（20%）：—
- 創新性（10%）：工具化檢查


## Case #14: #Temp vs Staging Table：暫存表選型對資料正確性的影響

### Problem Statement（問題陳述）
**業務場景**：曾以 SELECT INTO 到暫存表/中繼表後出現污染。需釐清選用差異與正確做法。
**技術挑戰**：選擇合適的落地容器與型別控制。
**影響範圍**：避免重蹈 SELECT INTO 缺陷。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. #temp 自動推斷型別，難保 Unicode
2. SELECT INTO 路徑易觸發缺陷
3. 中繼表若顯式型別可降低風險

**深層原因**：
- 架構層面：臨時 vs 長存未規範
- 技術層面：未顯式 DDL
- 流程層面：求快忽略正確性

### Solution Design（解決方案設計）
**解決策略**：偏向使用顯式建立的 Staging 表（NVARCHAR），若需 #temp 則先 CREATE TABLE #temp 顯式欄位，再 INSERT。

**實施步驟**：
1. 明確建表
- 實作細節：CREATE TABLE（NVARCHAR）
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 插入資料
- 實作細節：CONVERT Unicode 後 INSERT
- 所需資源：T-SQL
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
-- 不建議：直接 SELECT INTO #temp
-- 建議：先顯式定義，再 INSERT
CREATE TABLE #CustomerTmp (
  Id INT,
  NameZh NVARCHAR(200)
);

INSERT INTO #CustomerTmp (Id, NameZh)
SELECT Id, CONVERT(NVARCHAR(200), Name)
FROM A_LINK.DB_A.dbo.Customer;
```

實際案例：改為顯式建表後，未再發生污染。
實作環境：SQL Server。
實測數據：
- 改善前：#temp SELECT INTO 有污染
- 改善後：顯式 #temp + INSERT 沒污染
- 改善幅度：錯誤筆數 0

Learning Points（學習要點）
核心知識點：
- #temp 型別推斷的風險
- 顯式 DDL 的價值
- 選型與正確性的關聯

技能要求：
- 必備技能：DDL/DML
- 進階技能：暫存策略

延伸思考：
- TempDB 負載與效能
- 風險：臨時表生命週期
- 優化：索引暫時化

Practice Exercise（練習題）
- 基礎：顯式 #temp 建表 + INSERT
- 進階：與 SELECT INTO 結果對比
- 專案：把既有 SELECT INTO 改寫

Assessment Criteria（評估標準）
- 功能完整性（40%）：資料正確
- 程式碼品質（30%）：建表清晰
- 效能優化（20%）：最小必要索引
- 創新性（10%）：模板化


## Case #15: 異常樣態學：從亂碼到「上一筆殘影」的快速定位

### Problem Statement（問題陳述）
**業務場景**：遇到中文欄位錯誤，有的呈亂碼/問號，有的呈現上一筆殘影。需依樣態判斷根因類別。
**技術挑戰**：用觀察快速縮小排錯範圍。
**影響範圍**：縮短修復時間。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 亂碼/問號：典型碼頁/編碼問題
2. 上一筆殘影：疑似緩衝未清/溢位
3. 落地才錯：執行路徑差異

**深層原因**：
- 架構層面：未有樣態知識庫
- 技術層面：缺模式識別
- 流程層面：無快速分流流程

### Solution Design（解決方案設計）
**解決策略**：建立「樣態→疑似根因→建議動作」對照表：亂碼→CONVERT Unicode；殘影→改路徑（Cursor/顯式建表）。

**實施步驟**：
1. 樣態蒐集
- 實作細節：截圖/樣本值
- 所需資源：知識庫
- 預估時間：0.25 天

2. 對照表/決策樹
- 實作細節：處置流程化
- 所需資源：文件
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
-- 檢測「上一筆殘影」樣態（簡化示意）
WITH R AS (
  SELECT Id,
         NameZh,
         ROW_NUMBER() OVER (ORDER BY Id) AS rn
  FROM dbo.Stg_Customer
)
SELECT cur.Id, cur.NameZh AS CurVal, prv.NameZh AS PrevVal
FROM R cur
JOIN R prv ON cur.rn = prv.rn + 1
WHERE cur.NameZh LIKE LEFT(prv.NameZh, 2) + N'%';  -- 假設前 2 字殘影
```

實際案例：以樣態識別快速導向「非 Collation，為 Provider 路徑缺陷」。
實作環境：SQL Server。
實測數據：
- 改善前：嘗試錯方向
- 改善後：快速對症下藥
- 改善幅度：排錯時間降低

Learning Points（學習要點）
核心知識點：
- 樣態→根因的映射
- 觀察力與工程經驗
- 快速決策樹

技能要求：
- 必備技能：T-SQL、模式識別
- 進階技能：知識庫維護

延伸思考：
- 引入機器學習做樣態分類？
- 風險：誤判樣態
- 優化：多指標交叉驗證

Practice Exercise（練習題）
- 基礎：做一張對照表
- 進階：寫一段檢測殘影的 SQL
- 專案：把決策樹納入 Runbook

Assessment Criteria（評估標準）
- 功能完整性（40%）：能分流處理
- 程式碼品質（30%）：檢測合理
- 效能優化（20%）：—
- 創新性（10%）：知識庫化


## Case #16: 上線前驗收：抽樣 + 全量校驗，確保 0 筆錯誤

### Problem Statement（問題陳述）
**業務場景**：在 BATCH 全跑完前，需有自動化驗收保證不把污染資料導入 B 系統。
**技術挑戰**：兼顧速度與覆蓋率。
**影響範圍**：資料品質與上線風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無驗收關，錯誤易外溢
2. 手動抽查不可靠
3. 需快速 100% 覆蓋檢測

**深層原因**：
- 架構層面：流程缺少 Gate
- 技術層面：缺比對腳本（Case #9）
- 流程層面：未標準化

### Solution Design（解決方案設計）
**解決策略**：先抽樣早期偵錯，再以全量比對作為放行門檻；任一錯誤即中止併輸出差異清單。

**實施步驟**：
1. 抽樣驗證
- 實作細節：隨機/系統抽樣 500 筆
- 所需資源：T-SQL
- 預估時間：0.25 天

2. 全量比對 Gate
- 實作細節：差異筆數=0 方放行
- 所需資源：比對腳本
- 預估時間：0.25 天

**關鍵程式碼/設定**：
```sql
-- 抽樣（示意）
WITH R AS (
  SELECT TOP (500) *
  FROM A_LINK.DB_A.dbo.Customer
  ORDER BY NEWID()
)
SELECT COUNT(*) AS DiffCount
FROM R r
JOIN dbo.Stg_Customer l ON r.Id = l.Id
WHERE CONVERT(NVARCHAR(200), r.Name) <> l.NameZh;

-- 全量 Gate
IF EXISTS (
  SELECT 1
  FROM A_LINK.DB_A.dbo.Customer r
  JOIN dbo.Stg_Customer l ON r.Id = l.Id
  WHERE CONVERT(NVARCHAR(200), r.Name) <> l.NameZh
)
BEGIN
  RAISERROR(N'驗收失敗：存在差異', 16, 1);
END
```

實際案例：以 Gate 控制，確保 0 差異才匯入 B 系統。
實作環境：SQL Server。
實測數據：
- 改善前：有機會把污染資料送出
- 改善後：0 差異門檻保障品質
- 改善幅度：重大風險歸零

Learning Points（學習要點）
核心知識點：
- 驗收即程式碼（Quality Gate）
- 抽樣與全量的搭配
- 中止策略

技能要求：
- 必備技能：T-SQL、流程控制
- 進階技能：品質工程

延伸思考：
- 加入告警與儀表板
- 風險：全量比對成本
- 優化：快照比對、Hash 校驗

Practice Exercise（練習題）
- 基礎：寫一段抽樣比對
- 進階：實作 Gate
- 專案：把 Gate 納入批次排程

Assessment Criteria（評估標準）
- 功能完整性（40%）：Gate 能擋錯
- 程式碼品質（30%）：清晰可維護
- 效能優化（20%）：執行時間可控
- 創新性（10%）：告警集成


————————————
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #2, #5, #10, #13
- 中級（需要一定基礎）
  - Case #1, #6, #7, #8, #9, #14, #16
- 高級（需要深厚經驗）
  - Case #3, #4, #11, #12, #15

2. 按技術領域分類
- 架構設計類
  - Case #1, #11, #16
- 效能優化類
  - Case #12, #7, #14
- 整合開發類
  - Case #2, #4, #5, #6, #7, #14
- 除錯診斷類
  - Case #3, #8, #9, #10, #15
- 安全防護類（資料品質/風險控管）
  - Case #11, #16, #9

3. 按學習目標分類
- 概念理解型
  - Case #1, #10, #15
- 技能練習型
  - Case #2, #5, #6, #7, #12, #14
- 問題解決型
  - Case #3, #4, #8, #9, #16
- 創新應用型
  - Case #11, #12, #15


案例關聯圖（學習路徑建議）
- 建議先學
  - Case #2（Unicode 轉換基本功）
  - Case #5（NVARCHAR 變數中轉）
  - Case #10（排除 Collation 誤解）
- 之後學
  - Case #1（中繼層架構），鋪陳整體脈絡
  - Case #6（顯式建表 + INSERT）、Case #14（#temp vs Staging）
- 進一步
  - Case #3（SELECT INTO 異常鑑別）、Case #8（最小可重現）
  - Case #9（自動化差異比對）
- 解法落地
  - Case #4（Cursor 繞道）
  - Case #7（混合式方案）
  - Case #12（Cursor 效能優化）
- 流程與風險
  - Case #16（上線 Gate）
  - Case #11（無法升級下的風險控管）
  - Case #15（異常樣態學，強化判斷力）

依賴關係：
- Case #2/#5 是 Case #4/#6/#7 的前置（Unicode 與變數中轉）。
- Case #3 依賴 Case #8/#9（先能重現/比對，才做正確判斷）。
- Case #12 依賴 Case #4（先有 Cursor 再談優化）。
- Case #16 依賴 Case #9（先有比對器才能設 Gate）。
- Case #11 橫跨整體，與 Case #4/#16 密切相關。

完整學習路徑：
2 → 5 → 10 → 1 → 6/14 → 8 → 3 → 9 → 4 → 7 → 12 → 16 → 11 → 15

說明：
- 先掌握 Unicode 與排除法（2/5/10），建立正確心智模型
- 再懂架構與正確落地方式（1/6/14）
- 透過重現與比對（8/3/9）提升診斷能力
- 進入實際繞道與優化（4/7/12）
- 以品質 Gate 與風險控管（16/11）確保交付
- 最後用樣態學（15）強化快速判斷能力