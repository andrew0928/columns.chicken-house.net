以下內容依據原文逐一抽取並整理為可教學、可演練且可評估的 18 個問題解決案例。每一則案例均包含業務與技術脈絡、根因分析、解決方案與程式碼、量化效益、學習要點、練習題與評估標準。

說明：本文的資料規模與環境（除非個別案例另有補充）如下：
- 資料規模：Total Dir(s) 218,817；Total File(s) 1,143,165；Max Dir Level 18；Max Files In One Dir 83,947
- DB：Microsoft SQL Server（2005+；CTE；2017 測試畫面）；OS：Windows 10
- 範例根據 C:\（特別是 c:\windows 與 c:\windows\system32）資料爬取結果


## Case #1: 方案一（Adjacency List）列出指定目錄的直屬內容

### Problem Statement（問題陳述）
- 業務場景：企業內部檔案管理系統需快速列出 c:\windows 目錄的直屬資料夾與檔案，提供前台 UI 分頁顯示與容量統計。此操作屬於最常見的「目錄瀏覽」行為，頻次高、延遲敏感，若回應慢會影響使用體驗與後續批次作業。
- 技術挑戰：RDBMS 以 Adjacency List（父子關係）儲存，需先定位指定目錄節點，再各自查 DIRINFO 與 FILEINFO（以 PARENT_ID/DIR_ID）合併輸出。
- 影響範圍：查詢延遲影響頁面響應；若設計不當將導致後端資源浪費、鎖競爭、查詢計畫不穩定。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 需先找出 c:\windows 的目錄 ID，才能查直屬子節點。
  2. 目錄與檔案分表，需整合輸出與排序。
  3. 無需遞迴，但仍需良好索引以保證穩定延遲。
- 深層原因：
  - 架構層面：以樹狀的邏輯用關聯表表達，需轉譯步驟（先定位目錄，再查子節點）。
  - 技術層面：依賴 PARENT_ID 與 DIR_ID 的索引設計來避免全表掃描。
  - 流程層面：缺乏標準化存取模式容易在不同頁面出現不一致 SQL。

### Solution Design（解決方案設計）
- 解決策略：使用 Adjacency List 的最小成本作法。先 inner join 自表找出目標目錄 ID，再以 PARENT_ID/DIR_ID 各自查詢 DIRINFO/FILEINFO，最後以 UNION 合併並排序，輸出接近 dir c:\windows 的清單格式。

- 實施步驟：
  1. 取得目標目錄 ID
     - 實作細節：DIRINFO 自表 join（c:\ → windows）
     - 所需資源：SQL Server、對 DIRINFO(NAME)、PARENT_ID 的索引
     - 預估時間：0.5 小時
  2. 查詢直屬資料夾與檔案並合併輸出
     - 實作細節：DIRINFO 以 PARENT_ID=@root；FILEINFO 以 DIR_ID=@root；UNION 與排序
     - 所需資源：對 FILEINFO(DIR_ID) 與（必要時）SIZE 的索引
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
declare @root int;
select @root = D2.ID
from demo1.DIRINFO D1
join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID
where D1.NAME = 'c:\' and D2.NAME = 'windows';

select *
from (
  select '<DIR>' as type, name, NULL as size from demo1.DIRINFO where PARENT_ID = @root
  union
  select '' as type, NAME as name, SIZE as size from demo1.FILEINFO where DIR_ID = @root
) X
order by name asc;
```

- 實際案例：模擬 dir c:\windows
- 實作環境：SQL Server；資料規模如前述
- 實測數據：
  - 改善前：無標準化查法，可能多次往返
  - 改善後：0.279 秒；Estimated Subtree Cost 0.516889
  - 改善幅度：顯著降低非必要往返與掃描

Learning Points（學習要點）
- 核心知識點：
  - Adjacency List 自表關聯（Self-Join）
  - 以 PARENT_ID/DIR_ID 快速取得直屬子節點
  - 結果整形（UNION、ORDER）
- 技能要求：
  - 必備技能：基本 SQL join、索引使用
  - 進階技能：查詢計畫閱讀與索引調優
- 延伸思考：
  - 多語系或權限過濾要如何併入？
  - 大型目錄需分頁與統計緩存以免昂貴排序
  - 如何將此查詢封裝為儲存程序以統一存取？

Practice Exercise（練習題）
- 基礎練習：改寫為可參數化的儲存程序（30 分鐘）
- 進階練習：加入大小總計與檔案數量統計欄（2 小時）
- 專案練習：做一個分頁 API，支援排序與關鍵字過濾（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確列出直屬資料夾與檔案
- 程式碼品質（30%）：SQL 清晰、可維護、參數化
- 效能優化（20%）：合理索引、避免全表掃描
- 創新性（10%）：輸出格式與統計的擴展性


## Case #2: 方案一（Adjacency List）遞迴搜尋（CTE）

### Problem Statement（問題陳述）
- 業務場景：支援類似 dir /s /b c:\windows\system32\*.ini 的功能，需在指定目錄含所有子目錄搜尋副檔名為 .ini 的檔案，提供內容管理、稽核與清點。
- 技術挑戰：未知深度的樹狀結構，Self-Join 無法寫死層數；純程式遞迴查詢往返昂貴且難整合排序。
- 影響範圍：遞迴查詢效能與可攜性；大範圍時延遲明顯。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Adjacency List 天生需遞迴才能展開整棵子樹。
  2. 不同 DB 對遞迴語法支援不一（CTE、CONNECT BY）。
  3. 遞迴深度控制與路徑組裝增加複雜度。
- 深層原因：
  - 架構層面：樹狀結構與關聯模型表述落差大。
  - 技術層面：CTE 遞迴不代表高效，仍易成本高。
  - 流程層面：若未封裝，應用層容易重複造輪子。

### Solution Design（解決方案設計）
- 解決策略：使用 SQL Server CTE（Common Table Expression）遞迴展開子目錄並同時組合相對路徑，再 join FILEINFO 過濾目標副檔名。必要時使用 MAXRECURSION 限制深度避免失控。

- 實施步驟：
  1. 取得起始節點 ID
     - 實作細節：自表連接（c:\ → windows → system32）
     - 所需資源：DIRINFO 上 NAME/PARENT_ID 索引
     - 預估時間：0.5 小時
  2. 撰寫遞迴 CTE 走訪子目錄並組合 FULLNAME
     - 實作細節：CTE union all；cast 與 concat
     - 所需資源：SQL Server 2005+；必要時 MAXRECURSION
     - 預估時間：1 小時
  3. join FILEINFO 過濾 .ini 並輸出
     - 實作細節：join on DIR_ID；where EXT='.ini'
     - 所需資源：FILEINFO(DIR_ID, EXT) 索引
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
declare @root int;
-- 找 c:\windows\system32
select @root = D3.ID
from demo1.DIRINFO D1
join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID
join demo1.DIRINFO D3 on D2.ID = D3.PARENT_ID
where D1.NAME='c:\' and D2.NAME='windows' and D3.NAME='system32';

;with DIR_CTE(ID, NAME, FULLNAME) as (
  select ID, NAME, cast('./' + NAME as ntext)
  from demo1.DIRINFO where PARENT_ID = @root
  union all
  select D1.ID, D1.NAME, cast(concat(D2.FULLNAME,'/',D1.NAME) as ntext)
  from demo1.DIRINFO D1 join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)
select concat(D.FULLNAME, '/', F.NAME) as NAME, F.SIZE
from DIR_CTE D join demo1.FILEINFO F on D.ID = F.DIR_ID
where F.EXT = '.ini';
-- 可選: OPTION (MAXRECURSION 18);
```

- 實際案例：搜尋 c:\windows\system32 下 .ini
- 實作環境：SQL Server；資料規模如前述
- 實測數據：
  - system32/.ini：0.547 秒；Estimated Subtree Cost 0.942181
  - c:\windows/*.dll（大範圍）：8.138 秒；Cost 3.09097
  - 改善幅度：相較硬寫多層 self-join，可維護性大幅提升

Learning Points（學習要點）
- 核心知識點：
  - CTE 遞迴模式與 MAXRECURSION
  - 路徑組裝與型別處理
  - 遞迴查詢的效能邊界
- 技能要求：
  - 必備技能：CTE 寫法、join/where 最佳化
  - 進階技能：遞迴深度控制、計畫分析
- 延伸思考：
  - 如何把 CTE 封裝為可重用 stored procedure？
  - 跨 DBMS 的遞迴可攜性問題如何化解？
  - 何時應改採其他樹模型？

Practice Exercise（練習題）
- 基礎練習：改為搜尋 .log 與 .ini 多副檔名（30 分鐘）
- 進階練習：加入大小上限過濾與排序（2 小時）
- 專案練習：將 CTE 與分頁/搜尋 API 整合（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：遞迴正確性、結果一致
- 程式碼品質（30%）：CTE 可讀性與參數化
- 效能優化（20%）：索引與遞迴深度控制
- 創新性（10%）：可攜性與通用性考量


## Case #3: 方案一（Adjacency List）建立目錄（mkdir）

### Problem Statement（問題陳述）
- 業務場景：在 c:\windows 下新增 backup 目錄。此為頻次較低但需穩定、可審計之操作。
- 技術挑戰：需先定位父節點，再插入新節點並取回新 ID。
- 影響範圍：錯誤的 parent 參照會造成孤兒資料與瀏覽異常。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 需先查 parent（c:\windows）ID。
  2. 插入時須正確設定 PARENT_ID。
  3. 無層級計算，操作簡單但需一致性檢查。
- 深層原因：
  - 架構層面：以父子關係表達，新增僅影響單一行。
  - 技術層面：無需更新其他節點，有利效能。
  - 流程層面：建議使用交易與審計紀錄。

### Solution Design（解決方案設計）
- 解決策略：取得父節點 ID 後插入新列，回傳新目錄 ID；可加上唯一性檢查避免重名衝突。

- 實施步驟：
  1. 查父節點 ID（c:\windows）
     - 實作細節：自表 join
     - 所需資源：DIRINFO 索引
     - 預估時間：0.5 小時
  2. 插入新節點
     - 實作細節：insert DIRINFO(PARENT_ID, NAME)
     - 所需資源：唯一性檢查（可選）
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
declare @root int;
select @root = D2.ID
from demo1.DIRINFO D1
join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID
where D1.NAME='c:\' and D2.NAME='windows';

insert demo1.DIRINFO (PARENT_ID, NAME) values (@root, 'backup');
select @@identity as NewId;
```

- 實際案例：mkdir c:\windows\backup
- 實作環境：SQL Server
- 實測數據：
  - 執行時間：0.028 秒；Estimated Subtree Cost 0.0500064

Learning Points（學習要點）
- 核心知識點：父節點定位、insert 參照一致性
- 技能要求：基本 SQL DML、交易控制
- 延伸思考：加入命名規則、權限檢查、審計欄位

Practice Exercise（練習題）
- 基礎練習：新增 c:\windows\logs（30 分鐘）
- 進階練習：若重名則回傳錯誤碼（2 小時）
- 專案練習：封裝成 API 與審計記錄（8 小時）

Assessment Criteria
- 功能完整性（40%）：能建立且可瀏覽
- 程式碼品質（30%）：交易與錯誤處理
- 效能優化（20%）：索引利用
- 創新性（10%）：審計與驗證


## Case #4: 方案一（Adjacency List）搬移目錄（move）

### Problem Statement（問題陳述）
- 業務場景：將 c:\users 搬移到 c:\windows\backup 下。屬結構調整類操作，需即時生效且不破壞子樹。
- 技術挑戰：Adjacency List 搬移只需改變被搬節點 PARENT_ID；子節點引用不變。
- 影響範圍：前台路徑與瀏覽受影響，需確保邏輯一致。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 需同時取得來源與目的地節點 ID。
  2. 僅更新來源節點 PARENT_ID 即可完成搬移。
  3. 若應用層以完整路徑緩存，需同步更新。
- 深層原因：
  - 架構層面：子樹隨父節點移動，資料不需批次更新。
  - 技術層面：單行 update；效率高。
  - 流程層面：應封裝為交易，並記錄審計。

### Solution Design（解決方案設計）
- 解決策略：查出目的地（c:\windows\backup）與來源（c:\users）ID，將來源 ID 的 PARENT_ID 更新為目的地 ID。再以 CTE 列出搬移後子項驗證。

- 實施步驟：
  1. 取得目的地與來源 ID
     - 實作細節：自表 join 多層定位
     - 所需資源：DIRINFO 索引
     - 預估時間：0.5 小時
  2. 更新來源節點 PARENT_ID
     - 實作細節：單行 update
     - 所需資源：交易、安全檢查
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
declare @srcID int, @destID int;

-- dest: c:\windows\backup
select @destID = D3.ID
from demo1.DIRINFO D1
join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID
join demo1.DIRINFO D3 on D2.ID = D3.PARENT_ID
where D1.NAME='c:\' and D2.NAME='windows' and D3.NAME='backup';

-- src: c:\users
select @srcID = D2.ID
from demo1.DIRINFO D1
join demo1.DIRINFO D2 on D1.ID = D2.PARENT_ID
where D1.NAME='c:\' and D2.NAME='users';

update demo1.DIRINFO set PARENT_ID = @destID where ID = @srcID;
```

- 實際案例：move c:\users c:\windows\backup
- 實作環境：SQL Server
- 實測數據：
  - 更新（Step 3）時間：0.026 秒；Cost 0.0232853

Learning Points
- 核心知識點：Adjacency List 搬移的 O(1) 更新
- 技能要求：路徑定位、交易處理
- 延伸思考：跨 Volume/分片時如何處理？如何避免循環（將子節點移入自身）？

Practice Exercise
- 基礎練習：搬移 c:\windows\fonts 至 c:\windows\backup（30 分鐘）
- 進階練習：加入防呆（不可將節點移至其子孫）（2 小時）
- 專案練習：設計一個搬移 API，含審計、權限、回滾（8 小時）

Assessment Criteria
- 功能完整性（40%）：搬移後樹正確
- 程式碼品質（30%）：交易、約束防呆
- 效能優化（20%）：單行更新、索引命中
- 創新性（10%）：循環保護、審計方案


## Case #5: 方案一（Adjacency List）刪除子樹（rm -r）

### Problem Statement（問題陳述）
- 業務場景：刪除 c:\windows\backup 底下所有子目錄與檔案（保留根），常見於清空暫存、撤銷某一類目。
- 技術挑戰：需遞迴選出子樹再分階段刪除（先檔案後資料夾）。
- 影響範圍：I/O 大、鎖競爭風險、長交易。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Adjacency List 必須遞迴才能取子孫節點。
  2. 刪除順序需正確（file → dir）。
  3. 大量刪除導致 I/O 高、可能鎖表。
- 深層原因：
  - 架構層面：資料分表，需多次 join/CTE。
  - 技術層面：CTE 擴展 + 刪除 IN 子查詢成本高。
  - 流程層面：缺少批次/分批 + 審計。

### Solution Design
- 解決策略：以 CTE 展開子樹，分兩段刪除：FILEINFO（DIR_ID in 子樹）→ DIRINFO（ID in 子樹），最後驗證前後差異。必要時分批。

- 實施步驟：
  1. CTE 展開子樹
     - 實作細節：同 Case #2 的遞迴模式
     - 所需資源：索引、MAXRECURSION
     - 預估時間：1 小時
  2. 先刪檔後刪目錄
     - 實作細節：delete FILEINFO where DIR_ID in (...)；再刪 DIRINFO
     - 所需資源：交易、分批刪除
     - 預估時間：1 小時

- 關鍵程式碼/設定（節錄刪除段落）：
```sql
;with DIR_CTE(ID) as (
  select ID from demo1.DIRINFO where PARENT_ID = @destID
  union all
  select D1.ID from demo1.DIRINFO D1 join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)
delete demo1.FILEINFO where DIR_ID in (select ID from DIR_CTE);

;with DIR_CTE(ID) as (
  select ID from demo1.DIRINFO where PARENT_ID = @destID
  union all
  select D1.ID from demo1.DIRINFO D1 join DIR_CTE D2 on D1.PARENT_ID = D2.ID
)
delete demo1.DIRINFO where ID in (select ID from DIR_CTE);
```

- 實際案例：rm /s /q c:\windows\backup（保留根）
- 實作環境：SQL Server
- 實測數據：
  - 刪檔 Cost 2.57332；刪目錄 Cost 1.90982；總 22.536 秒

Learning Points
- 核心知識點：CTE 遞迴 + 分階段刪除
- 技能要求：大批刪除的交易與分批策略
- 延伸思考：可否先快照再刪？如何降低鎖衝突？

Practice Exercise
- 基礎練習：改為只刪 .tmp 檔（30 分鐘）
- 進階練習：加入分批（TOP N 循環刪）（2 小時）
- 專案練習：設計安全刪除 API（模擬回收桶）（8 小時）

Assessment Criteria
- 功能完整性（40%）：刪除正確有序
- 程式碼品質（30%）：交易、錯誤復原
- 效能優化（20%）：分批、索引適配
- 創新性（10%）：安全刪除、審計追蹤


## Case #6: 方案二（Flattened Columns）列出直屬內容

### Problem Statement
- 業務場景：列出 c:\windows 直屬資料夾與檔案，要求比遞迴方案更快的查詢延遲。
- 技術挑戰：使用預攤平欄位 ID01~ID20 表示各層 ID；直屬子節點需以 ID03 is null（或同義條件）快速過濾。
- 影響範圍：查詢速度快，但 schema 限制最大層級與維護成本高。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 已預先將層級展開欄位，查詢只需簡單 where。
  2. 需保證資料一致性（上層變更時連動）。
  3. 需大量索引支援不同 ID 欄位。
- 深層原因：
  - 架構層面：以空間換取時間。
  - 技術層面：欄位數固定，限制最大深度。
  - 流程層面：搬移/重構難以優雅表達。

### Solution Design
- 解決策略：使用 ID02=WindowsId and ID03 is null 過濾直屬資料夾，FILEINFO 以 DIR_ID=WindowsId 取檔案，UNION 輸出。

- 實施步驟：
  1. 直屬資料夾查詢
     - 實作細節：where ID02 = 151535 and ID03 is null
     - 所需資源：對 ID02/ID03 建索引
     - 預估時間：0.5 小時
  2. 直屬檔案查詢
     - 實作細節：where DIR_ID = 151535
     - 所需資源：FILEINFO(DIR_ID) 索引
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
select * from demo2.DIRINFO where ID02 = 151535 and ID03 is null;
select * from demo2.FILEINFO where DIR_ID = 151535;
```

- 實測數據：
  - 目錄：0.184 秒；Cost 0.0077312
  - 檔案：0.157 秒；Cost 0.213376

Learning Points
- 核心知識點：以攤平欄位消除遞迴
- 技能要求：條件化索引、查詢組合
- 延伸思考：如何在不改 schema 的情況支援超深目錄？

Practice Exercise
- 基礎：改查 c:\users 直屬目錄（30 分鐘）
- 進階：加入名稱關鍵字過濾與排序（2 小時）
- 專案：封裝通用 API（8 小時）

Assessment Criteria
- 功能完整性（40%）：結果正確
- 程式碼品質（30%）：清晰、參數化
- 效能優化（20%）：索引命中
- 創新性（10%）：查詢模板化


## Case #7: 方案二（Flattened Columns）遞迴搜尋

### Problem Statement
- 業務場景：搜尋 c:\windows\system32 下所有 .ini，需快速回應。
- 技術挑戰：改以「指定層欄位等於父層 ID」代表「在此父層子樹下」，不需遞迴。
- 影響範圍：效能好，但欄位固定限制彈性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 以 D.ID03=system32Id 代表在該子樹下（含所有更深層）。
  2. 只需 join FILEINFO 過濾副檔名。
  3. 索引設計決定速度。
- 深層原因：
  - 架構層面：用欄位位置表示層級關係。
  - 技術層面：不需遞迴、極快。
  - 流程層面：建立、搬移時需正確維護欄位。

### Solution Design
- 解決策略：DIRINFO 以 ID03=189039 過濾所有 system32 子樹；join FILEINFO 並 where EXT='.ini'。

- 實施步驟：
  1. 查子樹下目錄
     - 實作細節：where ID03 = 189039
     - 所需資源：ID03 索引
     - 預估時間：0.5 小時
  2. 查檔案清單
     - 實作細節：join FILEINFO，EXT 過濾
     - 所需資源：FILEINFO(DIR_ID, EXT) 索引
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
select F.NAME, F.SIZE
from demo2.FILEINFO F
join demo2.DIRINFO D on F.DIR_ID = D.ID
where F.EXT = '.ini' and D.ID03 = 189039;
```

- 實測數據：
  - 目錄：0.407 秒；Cost 0.0264708
  - join 取檔案：0.067 秒；Cost 0.18752

Learning Points
- 核心知識點：以層位欄位取代遞迴
- 技能要求：欄位與索引規劃
- 延伸思考：如何在不同父層用同一 SQL？（參數化列選擇）

Practice Exercise
- 基礎：改為過濾 .dll（30 分鐘）
- 進階：加入檔案大小與修改時間條件（2 小時）
- 專案：做一個「多條件過濾 + 分頁」API（8 小時）

Assessment Criteria 同上


## Case #8: 方案二（Flattened Columns）建立目錄（mkdir）

### Problem Statement
- 業務場景：在 c:\windows 下新增 backup（不涉及遞迴）
- 技術挑戰：需正確填入對應層欄位（ID01=c:\，ID02=windows）
- 影響範圍：層欄位錯誤將使查詢結果錯亂
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 新增節點需設定正確欄位（依層)。
  2. 靜態 SQL 難以涵蓋未知層級（可能需動態 SQL）。
  3. 需防 SQL Injection。
- 深層原因：
  - 架構層面：以欄位固定層級，新增需依層寫值。
  - 技術層面：動態 SQL 風險與維護負擔。
  - 流程層面：建議封裝至安全模組執行。

### Solution Design
- 解決策略：明確指定要填的層欄位（本例 ID01、ID02），儲存程序參數化避免注入。

- 實施步驟：
  1. 設計參數化存程
     - 實作細節：以父層 ID 與層級計算目標欄位
     - 所需資源：存程、權限
     - 預估時間：1 小時
  2. 插入新節點
     - 實作細節：insert 指定欄位
     - 所需資源：唯一性檢查
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
insert demo2.DIRINFO (NAME, ID01, ID02) values ('backup', 1, 151535);
select @@identity as NewId;
```

- 實測數據：0.117 秒；Cost 0.0400054

Learning Points
- 核心知識點：以欄位表達層級的新增模式
- 技能要求：防注入、存程參數化
- 延伸思考：若插入更深層，如何自動計算對應欄位？

Practice/Assessment 同 Case #3 調整


## Case #9: 方案二（Flattened Columns）搬移目錄（大量欄位位移）

### Problem Statement
- 業務場景：將 c:\users 搬到 c:\windows\backup 下
- 技術挑戰：需將整個子樹所有節點之層位欄位「整體右移」，並重設上層欄位對應值；SQL 冗長且易錯。
- 影響範圍：重構風險高、維護困難；但單次執行效率尚可。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 搬移需 shift-right 多個層欄位（ID04←ID03…）。
  2. 並設定新上層（ID01~ID03）。
  3. 難寫成通用存程，易導致注入或錯誤。
- 深層原因：
  - 架構層面：以欄位承載層級天然不利結構調整。
  - 技術層面：SQL 極度冗長，錯一欄全域錯。
  - 流程層面：需嚴格測試與交易保護。

### Solution Design
- 解決策略：以單一 update 將 ID20→ID19…依序右移，再補上 ID01~ID03 的新父層，並以查詢驗證。

- 實施步驟：
  1. 準備右移與新父層值
     - 實作細節：update set ID20=ID19 … ID04=ID03；ID03=dest；ID02/windows；ID01=c:\
     - 所需資源：交易、備份
     - 預估時間：2 小時
  2. 驗證
     - 實作細節：where ID03 = 目的地ID 列出確認
     - 所需資源：查詢腳本
     - 預估時間：0.5 小時

- 關鍵程式碼/設定（節錄）：
```sql
update demo2.DIRINFO
set
  ID20=ID19, ID19=ID18, ..., ID04=ID03,
  ID03 = 218818, -- backup
  ID02 = 151535, -- windows
  ID01 = 1       -- c:\
where ID02 = 134937; -- c:\users
```

- 實測數據：0.758 秒；Estimated Subtree Cost 18.3011

Learning Points
- 核心知識點：以欄位位移實現搬移的代價
- 技能要求：長 SQL 正確性、交易控制
- 延伸思考：是否改用 Nested Set 降低此類操作複雜度？

Practice/Assessment
- 讓學員為 10 層模型寫可重用的存程與測試


## Case #10: 方案二（Flattened Columns）刪除子樹

### Problem Statement
- 業務場景：清空 c:\windows\backup 子樹
- 技術挑戰：根據層欄位（ID03=backupId）一次選出子樹節點，先刪檔、再刪目錄。
- 影響範圍：I/O 高，需確保正確順序與交易。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. where ID03=目的地Id 即表示整個子樹。
  2. 大量 delete 導致 I/O 高。
  3. 必須先 file 後 dir。
- 深層原因：
  - 架構層面：攤平後選集簡單。
  - 技術層面：刪除仍是重 I/O。
  - 流程層面：建議分批與審計。

### Solution Design
- 解決策略：delete FILEINFO where DIR_ID in (select ID from DIRINFO where ID03=dest) → delete DIRINFO where ID03=dest

- 實施步驟：
  1. 刪檔
     - 實作細節：子查詢取目標目錄集
     - 所需資源：索引、交易
     - 預估時間：1 小時
  2. 刪目錄
     - 實作細節：直接刪除目錄集
     - 所需資源：同上
     - 預估時間：0.5 小時

- 關鍵程式碼/設定：
```sql
delete demo2.FILEINFO where DIR_ID in (select ID from demo2.DIRINFO where ID03 = 218818);
delete demo2.DIRINFO where ID03 = 218818;
```

- 實測數據：
  - 刪檔：18.962 秒；Cost 143.985
  - 刪目錄：1.343 秒；Cost 13.7447

Learning Points/Practice/Assessment 同 Case #5 調整


## Case #11: 方案三（Nested Set）列出直屬內容（含優化建議）

### Problem Statement
- 業務場景：列出 c:\windows 的直屬目錄（不包含所有孫節點），Nested Set 天生適合「整棵子樹」查詢，但「直屬」需排除中間祖先。
- 技術挑戰：僅用 left/right 時，直屬計算需額外 NOT EXISTS 過濾，否則會包含所有後代。
- 影響範圍：查詢成本高；建議增設 PARENT_ID 或 DEPTH。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Nested Set 的 between 查詢天生選到所有後代。
  2. 直屬需排除「中間祖先存在」的情況。
  3. 未額外維護 PARENT_ID/DEPTH 時，查詢繁瑣。
- 深層原因：
  - 架構層面：Nested Set 最佳在整棵子樹與計數。
  - 技術層面：直屬需附加條件或額外欄位。
  - 流程層面：索引維護策略需一併考慮。

### Solution Design
- 解決策略：以 self-join P（父）與 C（候選子）找出 P 範圍內的 C，再以 NOT EXISTS 排除任何介於 P 與 C 之間的 M。優化建議：額外維護 PARENT_ID 或 DEPTH 以簡化查詢。

- 實施步驟：
  1. 直屬查詢
     - 實作細節：C.left between P.left and P.right；NOT EXISTS 中間祖先
     - 所需資源：LEFT/RIGHT 索引
     - 預估時間：1 小時
  2. 加值欄位（建議）
     - 實作細節：維護 PARENT_ID 或 DEPTH
     - 所需資源：維護策略/存程
     - 預估時間：2 小時

- 關鍵程式碼/設定：
```sql
select C.*
from demo3.DIRINFO C
join demo3.DIRINFO P on C.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
where P.ID = 151535 and not exists (
  select 1
  from demo3.DIRINFO M
  where M.LEFT_INDEX between P.LEFT_INDEX and P.RIGHT_INDEX
    and C.LEFT_INDEX between M.LEFT_INDEX and M.RIGHT_INDEX
    and M.ID <> P.ID and M.ID <> C.ID
);
```

- 實測數據：
  - 2 分 33.591 秒；Cost 0.941395（慢）
  - 優化後（維護 PARENT_ID）：可回到與 Case #1 類似速度

Learning Points
- 核心知識點：Nested Set 的強弱項
- 技能要求：集合查詢、條件排除
- 延伸思考：什麼場景需要同時維護 PARENT_ID/DEPTH？

Practice/Assessment：同型變化練習（加 PARENT_ID 後重寫語法）


## Case #12: 方案三（Nested Set）遞迴搜尋（system32/.ini）

### Problem Statement
- 業務場景：在 c:\windows\system32 下搜尋 .ini，要求高效、可攜，避免 DB 專屬遞迴語法
- 技術挑戰：依 left/right 間距（between）無腦選出所有後代，再 join FILEINFO 過濾副檔名
- 影響範圍：查詢秒返，可跨 DB 套用
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Nested Set 天生支援整棵子樹查詢
  2. 單純 between，無需遞迴
  3. 僅需維護索引時更新成本
- 深層原因：
  - 架構層面：以範圍代表包含關係
  - 技術層面：join + filter 即完成
  - 流程層面：建議儲存程序化

### Solution Design
- 解決策略：以 C.LEFT between root.left and root.right；join FILEINFO 過濾 .ini

- 實施步驟：
  1. 取得 system32 範圍
  2. between + join 過濾

- 關鍵程式碼/設定：
```sql
select F.*
from demo3.DIRINFO C
join demo3.FILEINFO F on C.ID = F.DIR_ID
where F.EXT = '.ini' and C.LEFT_INDEX between 378075 and 380740;
```

- 實測數據：0.173 秒；Cost 0.167235

Learning Points/Practice/Assessment：同 Case #2，但以 between 改寫


## Case #13: 方案三（Nested Set）大量遞迴搜尋（windows/*.dll）

### Problem Statement
- 業務場景：搜尋 c:\windows 底下所有 .dll（更大範圍），需穩定低延遲
- 技術挑戰：大範圍 between + join 的索引命中與計畫穩定性
- 影響範圍：查詢時間直接影響使用者體感與後續批次
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. between 範圍大，join 行數多
  2. EXT 過濾與連接策略影響成本
  3. 索引設計左右結果
- 深層原因：
  - 架構層面：Nested Set 可保證語法簡單
  - 技術層面：索引與統計資訊需良好
  - 流程層面：建議封裝為存程與計畫指南

### Solution Design
- 解決策略：使用 between + join + EXT 過濾，建立/維護必要索引；封裝為存程。

- 關鍵程式碼/設定：
```sql
select F.*
from demo3.DIRINFO C
join demo3.FILEINFO F on C.ID = F.DIR_ID
where F.EXT = '.dll' and C.LEFT_INDEX between 303068 and 437609;
```

- 實測數據：
  - 0.546–0.836 秒（文中顯示 0.836 秒、整體比較表顯示 0.546 秒）
  - 對比 方案一：8.138 秒（約 10–15x 加速）

Learning Points/Practice/Assessment：同 Case #12，加入大範圍測試與對比


## Case #14: 方案三（Nested Set）建立目錄（插入與索引位移）

### Problem Statement
- 業務場景：在 c:\windows 插入 backup 節點，需更新整棵樹的 left/right 區間，確保連續性
- 技術挑戰：在插入點右側的所有 left/right 需 +2，為新節點騰出空間
- 影響範圍：更新行數可能大，但可在單交易內完成
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 插入騰位（right > 插入點；left > 插入點）各 +2
  2. 新節點 left=插入點+1、right=插入點+2
  3. 需完整交易避免不一致
- 深層原因：
  - 架構層面：Nested Set 更新成本集中在變動點右側
  - 技術層面：兩次大範圍 update + 一次 insert
  - 流程層面：需審計與回滾策略

### Solution Design
- 解決策略：三步驟（更新 right；更新 left；插入新節點）

- 關鍵程式碼/設定：
```sql
declare @windows_left int = 303068;

update demo3.DIRINFO set RIGHT_INDEX = RIGHT_INDEX + 2 where RIGHT_INDEX > @windows_left;
update demo3.DIRINFO set LEFT_INDEX  = LEFT_INDEX  + 2 where LEFT_INDEX  > @windows_left;
insert demo3.DIRINFO (NAME, LEFT_INDEX, RIGHT_INDEX) values ('backup', @windows_left+1, @windows_left+2);
```

- 實測數據：
  - step1：1.343 秒；step2：2.017 秒；step3：0.017 秒；總 3.377 秒

Learning Points/Practice/Assessment：強化交易、驗證與索引維護


## Case #15: 方案三（Nested Set）搬移目錄（暫存區位移法）

### Problem Statement
- 業務場景：將 c:\users 搬到 c:\windows\backup 下，需同時位移整個子樹的區間
- 技術挑戰：避免區間互卡，採用負區段暫存再回填；需精確位移量計算
- 影響範圍：多批次大範圍 update，需嚴格交易
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 將來源子樹整體移到負區間（暫存）
  2. 在目標節點騰空間（擴張區間）
  3. 將負區間移回新空間
- 深層原因：
  - 架構層面：以數線視角規劃可靠位移
  - 技術層面：位移量/範圍邏輯需精準
  - 流程層面：交易、測試、審計

### Solution Design
- 解決策略：三步位移（移至負區→騰位→回填）

- 關鍵程式碼/設定（節錄）：
```sql
-- step 1: move src to temp (negative)
set @offset = 0 - 302911 - 1;
update demo3.DIRINFO
set LEFT_INDEX = LEFT_INDEX + @offset,
    RIGHT_INDEX= RIGHT_INDEX+ @offset
where LEFT_INDEX between 269871 and 302912;

-- step 2: allocate space near destination
set @offset = 302911 - 269872 + 1;
update demo3.DIRINFO set LEFT_INDEX  = LEFT_INDEX  - @offset where LEFT_INDEX  between 269872 and 303069;
update demo3.DIRINFO set RIGHT_INDEX = RIGHT_INDEX - @offset where RIGHT_INDEX between 269872 and 303069;

-- step 3: move from temp to allocated space
set @offset = 303070;
update demo3.DIRINFO
set LEFT_INDEX = LEFT_INDEX + @offset,
    RIGHT_INDEX= RIGHT_INDEX+ @offset
where LEFT_INDEX < 0;
```

- 實測數據：總 0.550 秒（step1：0.527；step2：0.116；step3：0.023）

Learning Points/Practice/Assessment：數線思維、位移量計算、交易化


## Case #16: 方案三（Nested Set）刪除子樹＋回收索引空間

### Problem Statement
- 業務場景：刪除 c:\windows\backup 子樹並回收 left/right 空間，保持連續性
- 技術挑戰：先刪檔後刪目錄，再把空間收縮回來；需多次大範圍 update
- 影響範圍：I/O 大，需交易與驗證
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. between 取子樹，先刪檔後刪 dir
  2. 更新目標根 right=left+1（清空）
  3. 將左、右索引整體往回位移
- 深層原因：
  - 架構層面：Nested Set 維護連續性
  - 技術層面：多次更新與範圍條件
  - 流程層面：建議封裝存程與審計

### Solution Design
- 解決策略：三步（刪檔→刪目錄→回收區間）

- 關鍵程式碼/設定（節錄）：
```sql
-- step 1
delete demo3.FILEINFO where DIR_ID in (
  select ID from demo3.DIRINFO where LEFT_INDEX >= 270029 and LEFT_INDEX <= 303070
);
-- step 2
delete demo3.DIRINFO where LEFT_INDEX > 270029 and LEFT_INDEX < 303070;
-- step 3
update demo3.DIRINFO set RIGHT_INDEX = LEFT_INDEX + 1 where ID = 218825;
update demo3.DIRINFO set LEFT_INDEX  = LEFT_INDEX  - (303070-270029-1) where LEFT_INDEX  > 270030;
update demo3.DIRINFO set RIGHT_INDEX = RIGHT_INDEX - (303070-270029-1) where RIGHT_INDEX > 270030;
```

- 實測數據：
  - step1：5.756 秒；step2：0.887 秒；step3：2.515 秒；總 9.158 秒

Learning Points/Practice/Assessment：同 Case #5，增加回收步驟與驗證


## Case #17: 索引預計算導入管線（C# 遞迴掃描＋寫入 DB）

### Problem Statement
- 業務場景：以自動化工具掃描檔案系統（C:\）並一次寫入能同時支援三方案（Adjacency、Flattened、Nested Set）的索引欄位，降低查詢與維護成本
- 技術挑戰：在應用層遞迴（C#）同時計算 PATH（ID01~ID20）、LEFT/RIGHT（DFS traversal）與父子關係，並批次寫 DB
- 影響範圍：一次導入時間長；但之後查詢開銷大幅降低
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. DB 內寫遞迴與維護索引成本高且難維護
  2. 應用層 DFS 遞迴更自然
  3. 可一次產出三種索引欄位
- 深層原因：
  - 架構層面：把計算前移至資料導入階段
  - 技術層面：使用 stack/context 維持路徑與 traversal index
  - 流程層面：導入過程需容錯（無權限、連結點等）

### Solution Design
- 解決策略：以 C# 進行 DFS 掃描，計算並寫入 DIRINFO/FILEINFO 所需欄位；處理無權限與符號連結等例外。

- 關鍵程式碼/設定（節錄）：
```csharp
// 遞迴 DFS，於進入節點時寫入 DIRINFO(LEVEL, LEFT, PATH1..PATH20)
// 離開節點時補上 RIGHT_INDEX
// 並同時寫 FILEINFO 資料（DIR_ID=rootid）
ProcessFolder(context) {
  context.TravelIndex++;
  int rootid = _conn.ExecuteScalar<int>(/* insert DIRINFO with LEFT/PATHs */);
  foreach (var file in dir.GetFiles()) { /* insert FILEINFO */ }
  foreach (var subdir in dir.GetDirectories()) {
    if (subdir.Attributes.HasFlag(FileAttributes.ReparsePoint)) continue;
    context.LevelIndex++; context.PATHIDs[context.LevelIndex] = rootid;
    ProcessFolder(context);
    context.PATHIDs[context.LevelIndex] = 0; context.LevelIndex--;
  }
  context.TravelIndex++;
  _conn.Execute(@"update DIRINFO set RIGHT_INDEX=@RIGHT where ID=@ID", ...);
}
```

- 實際案例：掃描 C:\ 寫入 SQL
- 實作環境：.NET + SQL Server
- 實測數據：
  - Total Scan Time：1199.42 秒（953.10 files/sec）
  - 輸出資料：Dir 218,817；File 1,143,165；Max Depth 18

Learning Points
- 核心知識點：DFS、前移計算、三模型兼容
- 技能要求：C# 檔案系統 API、交易、批次寫入
- 延伸思考：如何多執行緒掃描與批次寫入加速？

Practice Exercise
- 基礎：只掃描某一子樹並寫入（30 分鐘）
- 進階：加上限速與錯誤重試（2 小時）
- 專案：做一個可配置的 ETL 工具（8 小時）

Assessment Criteria
- 功能完整性（40%）：索引正確可驗證
- 程式碼品質（30%）：結構清晰與容錯
- 效能優化（20%）：批次/連線池/交易
- 創新性（10%）：可配置與擴展性


## Case #18: 三方案選型與效能對比決策（搜尋為主的場景）

### Problem Statement
- 業務場景：大型內容平台對「在整個類目下做遞迴搜尋」的需求非常高（如 c:\windows\*.dll），需在可控成本下獲得最好的 RT
- 技術挑戰：Adjacency（CTE）慢、Flattened 查詢快但維護難、Nested Set 兼顧可攜與效能
- 影響範圍：影響搜尋體驗與運維成本
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Adjacency 遞迴擴展計算重
  2. Flattened 需固定層欄位且搬移/重構昂貴
  3. Nested Set 以包含範圍解出子樹，語法簡單
- 深層原因：
  - 架構層面：以資料模型匹配主要使用情境
  - 技術層面：索引維護 vs 查詢成本的取捨
  - 流程層面：資料變更頻率對模型選擇影響大

### Solution Design
- 解決策略：搜尋為主選 Nested Set；若幾乎只查不搬，Flattened 可考慮；若搬移極常見，Adjacency 可配合應用層遞迴。以實測指標做決策。

- 關鍵程式碼/設定（對比查詢摘要）：
```sql
-- 方案一：CTE 遞迴 + join
-- 方案三：between + join
```

- 實測數據（文中總表）：
  - c:\windows\*.dll：方案一 8.138 s；方案三 0.546 s（約 10–15x）
  - 刪除子樹：皆在同一數量級，方案三最佳（9.158 s）

- 改善幅度：大規模遞迴搜尋，方案三顯著優勢；維護與可攜性也更好

Learning Points
- 核心知識點：用使用情境驅動資料模型選擇
- 技能要求：閱讀計畫與基準測試
- 延伸思考：混搭三方案以取長補短的維護策略

Practice/Assessment：撰寫選型報告，含風險、成本與遷移計畫


--------------------------------
案例分類
--------------------------------

1) 按難度分類
- 入門級（適合初學者）
  - Case #1, #3, #6, #7, #12
- 中級（需要一定基礎）
  - Case #2, #5, #8, #10, #11, #13, #14, #18
- 高級（需要深厚經驗）
  - Case #4, #9, #15, #16, #17

2) 按技術領域分類
- 架構設計類
  - Case #11, #14, #15, #16, #17, #18
- 效能優化類
  - Case #2, #6, #7, #12, #13, #16, #18
- 整合開發類
  - Case #1, #3, #4, #5, #8, #9, #10, #17
- 除錯診斷類
  - Case #5, #10, #11, #16
- 安全防護類（注入/防呆/交易）
  - Case #8, #9, #15（防循環）、#5/#10（長交易/分批）

3) 按學習目標分類
- 概念理解型
  - Case #11, #14, #15, #18
- 技能練習型
  - Case #1, #2, #3, #6, #7, #12, #13
- 問題解決型
  - Case #4, #5, #8, #9, #10, #16
- 創新應用型
  - Case #17（ETL/前移計算）、#18（選型報告）


--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------

學習順序與依賴關係：
1. 先學基礎查詢與資料模型
   - Case #1（Adjacency 直屬查）、#3（Adjacency 建立） → 建立對父子關係與基本操作的直覺
2. 再學遞迴與刪除
   - Case #2（CTE 遞迴搜尋）→ #5（CTE 刪除子樹）
   - 依賴：了解 Adjacency 的遞迴本質（Case #1）
3. 導入效能取捨（Flattened）
   - Case #6（直屬）→ #7（遞迴搜尋）→ #8（建立）→ #9（搬移）→ #10（刪除）
   - 依賴：掌握欄位層級表示與其限制（Case #6/7）
4. 進階模型（Nested Set）
   - Case #11（直屬的困難與優化）→ #12（小範圍搜尋）→ #13（大範圍搜尋）
   - 依賴：理解包含關係與 between 查詢（Case #11）
5. 結構操作（Nested Set 更新）
   - Case #14（插入騰位）→ #15（搬移暫存位移）→ #16（刪除回收空間）
   - 依賴：熟悉 left/right 更新規則（Case #11/14）
6. 整體實戰與落地
   - Case #17（ETL 導入：三模型兼容索引一次算好）
   - Case #18（選型與決策：以指標導向模型）
   - 依賴：已理解三模型優缺與更新成本

完整學習路徑建議：
- 入門段：Case #1 → #3 → #2 → #5（掌握 Adjacency 與 CTE）
- 取捨段：Case #6 → #7 → #8 → #9 → #10（體會 Flattened 的速度與維護代價）
- 進階段：Case #11 → #12 → #13 → #14 → #15 → #16（熟練 Nested Set 查詢與更新）
- 實戰段：Case #17（資料導入/索引前移）→ Case #18（撰寫選型報告，制定團隊標準）

以上 18 個案例均直接源自原文的操作與指標，並補齊教學所需的結構與評估面向，可作為分段課程、專題實作與面試考核的完整素材。