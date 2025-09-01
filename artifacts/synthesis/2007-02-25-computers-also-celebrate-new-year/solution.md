以下內容基於原文提到的更新情境（SQL Server 2005 SP2、ActiveSync 4.5、Virtual PC 2007、一次爆出多個安全性修補）所抽象與延展出的實戰性案例。每個案例均以教學與評測為目的設計，含問題、根因、解法、步驟、程式碼/設定、學習要點與練習。

注意：原文未提供量測數據，本文在「實測數據」欄位提供可衡量的指標設計與「示例（模擬環境）」數值，供教學與評估使用，請於實作環境自行驗證。


## Case #1: SQL Server 2005 SP2 就地升級的零停機切換策略

### Problem Statement（問題陳述）
- 業務場景：公司核心 ERP 與報表系統使用 SQL Server 2005（未打 SP2），春節前後需要導入 SP2 以獲得安全修補與修正，但產線允許的停機時間極短（< 5 分鐘）。需確保升級過程中交易不丟失、相依系統不中斷。
- 技術挑戰：就地升級存在服務重啟與元件更新，風險包括長時間停機或回滾困難；且需確保應用相容、資料一致性。
- 影響範圍：所有依賴資料庫的內外部服務（ERP、API、報表、ETL），營運受阻、SLA 違約、資料風險。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單節點部署無備援，升級需停機。
  2. 未建立標準化升級程序與回滾計畫，升級窗口無法預估。
  3. 相依應用的相容性未驗證，升級後可能出現執行計劃變動。
- 深層原因：
  - 架構層面：缺少高可用或災難備援設計（無鏡像、無 AlwaysOn）。
  - 技術層面：缺少前置健康檢查、統計資訊陳舊、缺少升級前基準。
  - 流程層面：變更管理與分環測試（Dev/QA/Prod）的門檻不完備。

### Solution Design（解決方案設計）
- 解決策略：採「次級節點切換」策略（Log Shipping/鏡像/複寫）在新節點完成 SP2 升級驗證後，於短時間內切換服務，降低停機；同步準備回滾劇本。透過前置健康檢查、基準測量、影響分析與自動化腳本確保一致性與可回復性。

- 實施步驟：
  1. 規劃與預備
     - 實作細節：盤點資料庫清單、相依系統、停機時段；設定 DB 為 FULL，建立基準（延遲、TPS、主要查詢計劃）。
     - 所需資源：監控（PerfMon/Query Store 替代）、版本庫、變更單。
     - 預估時間：0.5-1 天
  2. 建立次級節點（Log Shipping）
     - 實作細節：在次級伺服器還原完整/交易記錄備份（NORECOVERY）；設定日誌傳送；在次級安裝 SP2。
     - 所需資源：第二台 SQL Server、網路共享。
     - 預估時間：0.5-1 天
  3. 切換與驗證
     - 實作細節：凍結寫入（應用只讀）、傳送最後一個 Log、在次級恢復為可讀寫，更新連線字串或 DNS；觀測指標。
     - 所需資源：切換腳本、監控告警。
     - 預估時間：5-15 分鐘

- 關鍵程式碼/設定：
```sql
-- 升級前：確認相容等級與恢復模式
SELECT name, compatibility_level, recovery_model_desc FROM sys.databases;

-- 設定 Full Recovery 以支援 Log Shipping
ALTER DATABASE [YourDB] SET RECOVERY FULL;

-- 基準與健康檢查
DBCC CHECKDB([YourDB]) WITH NO_INFOMSGS, ALL_ERRORMSGS;
EXEC sp_updatestats; -- 更新統計資訊以穩定計劃

-- 切換（簡化示意，實務請用 Log Shipping/鏡像程序）
-- 最後一次交易記錄備份於主伺服器
BACKUP LOG [YourDB] TO DISK = N'\\share\YourDB_Last.trn' WITH INIT;

-- 次級伺服器上恢復
RESTORE LOG [YourDB] FROM DISK = N'\\share\YourDB_Last.trn' WITH RECOVERY;
```

- 實際案例：基於文中「春節前後更新、導入 SP2」情境，設計以次級節點切換減停機的升級流程。
- 實作環境：Windows Server 2003 R2/2008，SQL Server 2005 RTM→SP2，雙節點（主/次級）。
- 實測數據：
  - 改善前：就地升級停機 30-60 分鐘（示例數據）
  - 改善後：切換停機 3-10 分鐘（示例數據）
  - 改善幅度：停機縮短約 70-90%（示例）

Learning Points（學習要點）
- 核心知識點：
  - Log Shipping/鏡像切換基本原理
  - 升級前健康檢查與基準測量
  - 低風險回滾策略設計
- 技能要求：
  - 必備技能：T-SQL、備份還原、基本網路與共享設定
  - 進階技能：自動化切換腳本、監控/告警整合
- 延伸思考：
  - 能否以複寫或 AlwaysOn（更高版本）替代？
  - 切換時序如何減少寫入凍結時間？
  - 如何將切換納入例行 DR 演練？

Practice Exercise（練習題）
- 基礎練習：在測試環建立 FULL 模式與 DBCC CHECKDB 流程（30 分）
- 進階練習：用兩臺 SQL 2005 建立 Log Shipping 並進行一次計畫切換（2 小時）
- 專案練習：制定完整升級手冊（含回滾）、自動化腳本與驗證清單（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：切換成功、資料一致、應用連線更新
- 程式碼品質（30%）：腳本可重複、日志清晰、錯誤處理完善
- 效能優化（20%）：切換時間、恢復時間目標（RTO）達標
- 創新性（10%）：自動化與監控整合程度


## Case #2: 將 SQL2005 從 2000 相容模式提升以解鎖功能與效能

### Problem Statement（問題陳述）
- 業務場景：團隊把 SQL Server 2005 當 SQL2000 用，長期設定為相容等級 80，導致新功能（例如更佳的查詢最佳化器、部分 CLR 功能）無法使用，報表與批次作業效能受限。
- 技術挑戰：更改相容等級可能改變查詢計劃或行為，需在不影響生產的前提下完成評估與切換。
- 影響範圍：關鍵查詢效能、批次作業時程、BI 報表產出時間。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 相容等級設定為 80（SQL2000）。
  2. 缺少升級顧問與用例覆蓋測試。
  3. 部分舊語法/提示與新最佳化器衝突。
- 深層原因：
  - 架構層面：應用對查詢計劃過度依賴（硬編碼提示）。
  - 技術層面：未利用 DMV/Profiler 觀測退步查詢。
  - 流程層面：缺乏預備環境與藍綠切換流程。

### Solution Design（解決方案設計）
- 解決策略：建立測試複本，切換為 90 相容等級（SQL2005），以回歸測試與基準比較確保安全；針對退步查詢採用索引調整或提示微調，最後在產線分段切換。

- 實施步驟：
  1. 盤點與評估
     - 實作細節：列出資料庫與主力查詢；執行 Upgrade Advisor（或相當工具）與 Query 取樣。
     - 所需資源：測試環境、樣本負載。
     - 預估時間：0.5 天
  2. 試切與調整
     - 實作細節：在測試庫將相容等級調至 90，跑回歸；針對退步查詢調整索引/提示。
     - 所需資源：DMV、Profiler
     - 預估時間：1 天
  3. 產線分段切換
     - 實作細節：低風險資料庫先切，持續監控；完成後全面切換。
     - 所需資源：監控儀表板
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```sql
-- 盤點與切換相容等級
SELECT name, compatibility_level FROM sys.databases;
-- 將相容等級調整為 SQL 2005（90）
ALTER DATABASE [YourDB] SET COMPATIBILITY_LEVEL = 90;

-- 退步查詢定位（示意）
SELECT TOP 20 qs.total_worker_time, st.text
FROM sys.dm_exec_query_stats qs
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY qs.total_worker_time DESC;
```

- 實際案例：文中提到「把 SQL2005 當 2000 用」，本方案示範如何安全升級相容等級。
- 實作環境：SQL Server 2005 SP2，測試/產線一式兩份。
- 實測數據：
  - 改善前：部分報表 30 分完成（示例）
  - 改善後：相容等級 90 後報表 18 分完成（示例）
  - 改善幅度：效能提升約 40%（示例）

Learning Points
- 核心知識點：相容等級的行為差異；退步查詢定位；迭代切換策略
- 技能要求：T-SQL、DMV/Profiler 使用；索引與提示調優
- 延伸思考：是否能用 Query Hints 臨時緩解退步？如何制定藍綠/灰度切換？

Practice Exercise
- 基礎：查詢並修改測試庫相容等級（30 分）
- 進階：比對前後前 10 慢查詢並提出索引方案（2 小時）
- 專案：完成一份相容等級升級操作手冊與回歸清單（8 小時）

Assessment Criteria
- 功能完整性：切換成功、回歸通過
- 程式碼品質：腳本可重複、注釋清楚
- 效能優化：關鍵查詢耗時下降
- 創新性：自動化比較與告警設計


## Case #3: SQL SP 升級後健康檢查與統計資訊回補

### Problem Statement
- 業務場景：SP 升級後，部分批次作業與報表偶發變慢，需確認資料庫完整性與統計資訊是否陳舊，避免計劃不穩定。
- 技術挑戰：快速辨識問題層面（資料完整、索引碎片、統計資訊、計劃快取）。
- 影響範圍：夜間批次窗口、白天報表 SLA、客戶體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 統計資訊陳舊導致錯誤估算。
  2. 升級後計劃快取失效重編譯造成抖動。
  3. 潛在資料或索引碎片異常。
- 深層原因：
  - 架構層面：缺乏例行維護窗口與自動化。
  - 技術層面：未建立健康檢查清單。
  - 流程層面：缺少升級後驗收步驟。

### Solution Design
- 解決策略：建立升級後標準健康檢查與維護流程（CHECKDB、更新統計、重建或重組索引、必要時清理特定快取），以腳本自動化並納入驗收清單。

- 實施步驟：
  1. 健康檢查
     - 實作細節：CHECKDB、錯誤日誌掃描、異常警示。
     - 資源：SQL Agent Job、監控
     - 時間：1 小時
  2. 統計與索引維護
     - 實作細節：sp_updatestats；依碎片率 REBUILD/REORGANIZE。
     - 資源：維護腳本
     - 時間：1-2 小時
  3. 驗收與監控
     - 實作細節：比較關鍵查詢耗時、批次窗口。
     - 資源：基準報表
     - 時間：1 小時

- 關鍵程式碼/設定：
```sql
-- 資料完整性檢查
DBCC CHECKDB ([YourDB]) WITH NO_INFOMSGS, ALL_ERRORMSGS;

-- 更新統計資訊
EXEC sp_updatestats;

-- 碎片調整（示例）
SELECT dbschemas.[name] AS 'Schema', dbtables.[name] AS 'Table',
       dbindexes.[name] AS 'Index', indexstats.avg_fragmentation_in_percent
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'SAMPLED') indexstats
JOIN sys.tables dbtables ON dbtables.[object_id] = indexstats.[object_id]
JOIN sys.schemas dbschemas ON dbtables.[schema_id] = dbschemas.[schema_id]
JOIN sys.indexes dbindexes ON dbindexes.[object_id] = indexstats.[object_id]
AND indexstats.index_id = dbindexes.index_id
ORDER BY indexstats.avg_fragmentation_in_percent DESC;
```

- 實際案例：SP2 後建立標準化健康檢查，明顯降低夜間批次延遲。
- 實作環境：SQL Server 2005 SP2。
- 實測數據（示例）：
  - 改善前：批次作業 120 分
  - 改善後：90 分
  - 幅度：-25%

Learning Points
- 核心：CHECKDB、統計資訊、碎片管理
- 技能：DMV 使用、維護腳本排程
- 延伸：是否需要逐表重建索引？如何迴避尖峰時段？

Practice
- 基礎：對測試庫執行 CHECKDB 與 sp_updatestats（30 分）
- 進階：依碎片率自動決策 REBUILD/REORGANIZE（2 小時）
- 專案：建立升級後健康檢查 Job 與報表（8 小時）

Assessment
- 功能：腳本正確、無誤報
- 程式碼：可維護、記錄化
- 效能：批次窗口縮短
- 創新：動態門檻與告警


## Case #4: 以 T-SQL 取代圖形化維護計畫，提升可控性

### Problem Statement
- 業務場景：原以維護計畫精靈建立備份/清理，但升級後部分計畫失效或難以追蹤。需改為 T-SQL/Agent Job 管理，以提升透明度與可移植性。
- 技術挑戰：將圖形化維護轉為可版本控管的腳本；避免人為誤操作。
- 影響範圍：備份可靠性、RPO/RTO 目標、審計可視性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. GUI 維護計畫難以審核與追蹤變更。
  2. 升級後 SSIS 套件或作業相依破裂。
  3. 無一致命名與失敗告警。
- 深層原因：
  - 架構：維護流程未標準化。
  - 技術：缺少腳本化與版本控管。
  - 流程：缺少審計與告警規範。

### Solution Design
- 解決策略：以 T-SQL 與 SQL Agent Job 建立全備/差異/交易記錄備份與清理作業，納入版本控管與告警，確保一致性。

- 實施步驟：
  1. 腳本化備份策略
     - 細節：全/差/Log 排程；含驗證與壓縮（依版本）。
     - 資源：版本庫、Agent
     - 時間：0.5 天
  2. 日誌與告警
     - 細節：失敗寄信、事件記錄。
     - 資源：Database Mail/SMTP
     - 時間：0.5 天
  3. 清理與驗證
     - 細節：保留策略 N 天；定期還原測試。
     - 資源：備援伺服器
     - 時間：0.5 天

- 關鍵程式碼/設定：
```sql
-- 全備（示例）
DECLARE @path nvarchar(260) = N'\\backupshare\YourDB_FULL_' +
    CONVERT(nvarchar(8), GETDATE(), 112) + N'.bak';
BACKUP DATABASE [YourDB] TO DISK = @path WITH INIT, CHECKSUM, STATS=5;

-- 交易記錄備份
DECLARE @tlog nvarchar(260) = N'\\backupshare\YourDB_LOG_' +
    REPLACE(CONVERT(nvarchar(19), GETDATE(), 120),':','') + N'.trn';
BACKUP LOG [YourDB] TO DISK = @tlog WITH INIT, CHECKSUM, STATS=5;
```

- 實際案例：將維護轉為腳本後，備份成功率與審計可視性顯著提升。
- 實作環境：SQL Server 2005 SP2。
- 實測數據（示例）：備份失敗率由 3% 降至 <0.5%；平均備份時間 -15%。

Learning Points
- 核心：腳本化維護、可審核性
- 技能：SQL Agent、Database Mail、備份策略
- 延伸：如何加入完整性驗證與自動還原演練？

Practice
- 基礎：建立全/差/Log 備份 Job（30 分）
- 進階：加入失敗告警與清理策略（2 小時）
- 專案：用版本庫管理維護腳本與變更（8 小時）

Assessment
- 功能：備份成功、可還原
- 程式碼：標準化、可讀性
- 效能：時間可控、資源占用合理
- 創新：自動驗證與報表


## Case #5: SQL Agent 作業在 SP 升級後失敗的快速診斷

### Problem Statement
- 業務場景：SP2 升級後，部分 SQL Agent 作業（備份、ETL、報表）失敗或未執行，需快速恢復。
- 技術挑戰：辨識失敗根因（權限、路徑、帳號、腳本變動），降低影響面。
- 影響範圍：備份中斷、ETL 延遲、SLA 風險。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 服務帳號權限變更或失效。
  2. 路徑/磁碟權限或網路共享不可達。
  3. 作業步驟相依元件（SSIS/ODBC）版本不符。
- 深層原因：
  - 架構：過度集中在單帳號/單共享。
  - 技術：缺少作業健康儀表板。
  - 流程：未進行升級前逐作業回歸。

### Solution Design
- 解決策略：建立故障清單與標準化診斷查詢，快速鎖定近 24 小時失敗作業與訊息；修正權限與相依；加上監控與告警。

- 實施步驟：
  1. 快速盤點
     - 細節：查詢失敗作業與錯誤訊息。
     - 資源：T-SQL、Agent Views
     - 時間：30 分
  2. 權限/相依修復
     - 細節：服務帳號、共享權限、ODBC/Provider。
     - 資源：AD/檔案伺服器
     - 時間：1-2 小時
  3. 監控告警
     - 細節：失敗寄信與儀表板。
     - 資源：Database Mail
     - 時間：1 小時

- 關鍵程式碼/設定：
```sql
-- 最近失敗作業（step_id=0 表示作業層級結果）
SELECT TOP 50 j.name, h.run_date, h.run_time, h.run_duration, h.message
FROM msdb.dbo.sysjobhistory h
JOIN msdb.dbo.sysjobs j ON h.job_id = j.job_id
WHERE h.run_status = 0 AND h.step_id = 0
ORDER BY h.instance_id DESC;
```

- 實際案例：升級當日即發現備份作業失敗，依訊息修正共享權限立即恢復。
- 實作環境：SQL Server 2005 SP2。
- 實測數據（示例）：平均修復時間由 2 小時降至 30 分鐘。

Learning Points
- 核心：Agent 作業診斷、權限與相依管理
- 技能：T-SQL、事件歷史分析
- 延伸：如何建立作業健康儀表板與自動告警？

Practice
- 基礎：撈出 24 小時內全部失敗作業（30 分）
- 進階：將查詢包成報表並寄送（2 小時）
- 專案：建立 Agent 健康面板與告警（8 小時）

Assessment
- 功能：快速定位故障
- 程式碼：查詢可維護
- 效能：縮短 MTTR
- 創新：自動化報表


## Case #6: ActiveSync 4.5 升級後合作關係重建的資料保護

### Problem Statement
- 業務場景：升級 ActiveSync 4.5 後，既有「合作關係」需重建，擔心聯絡人、行事曆、郵件等資料重複或遺失。
- 技術挑戰：在重建合作關係過程中保留資料一致性，並能快速回復。
- 影響範圍：業務人員行動資料、郵件同步、工作排程。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 版本升級變更配對與儲存結構。
  2. 桌面端 ActiveSync 設定與裝置端對應關係重置。
  3. 未事先備份裝置與 PC 的資料。
- 深層原因：
  - 架構：單一同步管道缺乏冗餘。
  - 技術：不了解合作關係儲存於 Registry。
  - 流程：無升級前備份與還原流程。

### Solution Design
- 解決策略：制定升級前後的資料保護SOP：備份 Outlook/PST 與裝置資料、匯出 ActiveSync 合作關係註冊表、重建後驗證並去重，確保零資料遺失。

- 實施步驟：
  1. 升級前備份
     - 細節：匯出 Outlook 資料/PST，備份裝置資料（OEM 工具）；匯出合作關係 Registry。
     - 資源：Outlook、reg.exe
     - 時間：30-60 分
  2. 升級與重建
     - 細節：安裝 4.5，首次連線以「取代/合併」策略選擇，避免雙向覆蓋。
     - 資源：ActiveSync 4.5 安裝包
     - 時間：30 分
  3. 驗證與去重
     - 細節：比對筆數，必要時執行去重腳本（Outlook）。
     - 資源：Outlook VBA/內建偵測重複
     - 時間：30-60 分

- 關鍵程式碼/設定：
```bat
:: 匯出 ActiveSync 合作關係（Windows XP）
reg export "HKCU\Software\Microsoft\Windows CE Services\Partners" "%USERPROFILE%\Desktop\AS_Partners.reg" /y

:: 匯出 Outlook（建議使用 Outlook 匯出功能）
:: 另可備份 PST: 載入檔案位置 -> 複製至安全位置
```

- 實際案例：依原文「升級 4.5 後需重建合作關係」，建立備份與重建 SOP 後避免資料丟失。
- 實作環境：Windows XP SP2、Outlook 2003/2007、ActiveSync 4.5、Windows Mobile 5/6。
- 實測數據（示例）：重建平均時間 < 30 分；資料遺失 0；重複項目 < 1%。

Learning Points
- 核心：合作關係/資料備份點
- 技能：Registry 匯出、Outlook 匯入匯出
- 延伸：是否可自動化備份與驗證？如何做大規模用戶升級？

Practice
- 基礎：匯出 Registry 與 PST（30 分）
- 進階：設計重建後驗證清單與筆數核對（2 小時）
- 專案：撰寫端點使用者操作指引（8 小時）

Assessment
- 功能：資料完整、可回復
- 程式碼：備份腳本正確
- 效能：重建時長可控
- 創新：自動驗證流程


## Case #7: ActiveSync 4.5 升級後無法連線的驅動/USB 疑難排解

### Problem Statement
- 業務場景：升級 ActiveSync 4.5 後，裝置連上 USB 但不同步；裝置顯示不受信任或驅動未知。
- 技術挑戰：辨識是驅動、USB 連線模式、或防火牆/權限問題。
- 影響範圍：全體行動裝置使用者，同步中斷。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. Windows CE USB 驅動異常或殘留舊版。
  2. USB 連線設定（僅充電/傳輸模式）不正確。
  3. 防火牆或安全策略阻擋 ActiveSync 程序。
- 深層原因：
  - 架構：端點驅動管理與標準化不足。
  - 技術：不熟悉裝置管理員與驅動清理。
  - 流程：缺少升級後端點健檢。

### Solution Design
- 解決策略：建立端點疑難排解流程：驅動清理重裝、切換 USB 埠與傳輸模式、驗證程序與防火牆例外，確保可重複操作。

- 實施步驟：
  1. 驅動清理與重裝
     - 細節：裝置管理員移除未知裝置與舊驅動；重新插拔安裝。
     - 資源：devmgmt.msc、ActiveSync 安裝包
     - 時間：20-30 分
  2. 連線設定檢查
     - 細節：更換 USB 埠/線；切換裝置「允許 USB 連線」與同步模式。
     - 資源：裝置設定
     - 時間：10-15 分
  3. 防火牆與程序
     - 細節：允許 wcescomm.exe、rapimgr.exe；關閉與檢查安防軟體衝突。
     - 資源：本機防火牆設定
     - 時間：10-15 分

- 關鍵程式碼/設定：
```bat
:: 終止並重啟 ActiveSync 相關程序
taskkill /IM wcescomm.exe /F
taskkill /IM rapimgr.exe /F
start "" "C:\Program Files\Microsoft ActiveSync\wcescomm.exe"
```

- 實際案例：批量升級後少量端點需手動清驅動即恢復同步。
- 實作環境：Windows XP SP2、ActiveSync 4.5。
- 實測數據（示例）：首次處理成功率 > 90%，平均處理時間 25 分鐘。

Learning Points
- 核心：端點驅動與連線模式
- 技能：裝置管理員操作、程序與防火牆例外
- 延伸：如何標準化端點映像與驅動管理？

Practice
- 基礎：清除重裝驅動與重啟 ActiveSync（30 分）
- 進階：撰寫端點疑難排解 Runbook（2 小時）
- 專案：製作自助檢核工具（8 小時）

Assessment
- 功能：恢復連線
- 程式碼：批次命令正確
- 效能：平均修復時間
- 創新：自動化檢測


## Case #8: ActiveSync 重建合作關係後避免/清理由重複資料

### Problem Statement
- 業務場景：重建合作關係後，Outlook 與裝置中出現重複聯絡人/行事曆。
- 技術挑戰：判斷重複準則並安全去重，避免刪錯。
- 影響範圍：使用者體驗、資料品質、搜尋效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 首次同步選擇合併導致雙向重複。
  2. 重複檢測未開啟或準則不足。
  3. 第三方外掛/規則造成複製。
- 深層原因：
  - 架構：未建立去重策略。
  - 技術：不熟悉 Outlook 去重機制/VBA。
  - 流程：缺少同步後驗收清單。

### Solution Design
- 解決策略：定義去重準則（名稱+主郵件），先備份 PST，再以 VBA 或手工過濾去重；同步前開啟 Outlook 重複偵測。

- 實施步驟：
  1. 備份與設定
     - 細節：備份 PST；在 Outlook 選項開啟「建立新項目時檢查重複」。
     - 資源：Outlook
     - 時間：15 分
  2. 去重執行
     - 細節：用 VBA 以字典比對 FullName+Email 去重。
     - 資源：Outlook VBA
     - 時間：45 分
  3. 驗證
     - 細節：抽樣核對、再同步一次觀察。
     - 資源：ActiveSync
     - 時間：15 分

- 關鍵程式碼/設定：
```vba
' Outlook VBA：以 FullName+Email1Address 去重聯絡人（示例）
Sub DeDupContacts()
  Dim olApp As Outlook.Application, ns As Outlook.NameSpace
  Dim items As Outlook.Items, it As Object
  Dim dict As Object, key As String
  Set olApp = Application: Set ns = olApp.GetNamespace("MAPI")
  Set items = ns.GetDefaultFolder(olFolderContacts).Items
  Set dict = CreateObject("Scripting.Dictionary")
  For i = items.Count To 1 Step -1
    Set it = items(i)
    If TypeName(it) = "ContactItem" Then
      key = LCase(it.FullName & "|" & it.Email1Address)
      If dict.Exists(key) Then it.Delete Else dict.Add key, True
    End If
  Next
End Sub
```

- 實際案例：重建後 3% 重複，經 VBA 腳本一次清理。
- 實作環境：Outlook 2003/2007、ActiveSync 4.5。
- 實測數據（示例）：重複率 3%→0%，處理時間 < 1 小時。

Learning Points
- 核心：資料去重策略與安全刪除
- 技能：Outlook 設定與 VBA
- 延伸：如何擴展至行事曆/工作？如何加入更嚴謹比對鍵？

Practice
- 基礎：開啟重複偵測並備份 PST（30 分）
- 進階：修改 VBA 支援多郵件欄位（2 小時）
- 專案：製作一鍵去重外掛（8 小時）

Assessment
- 功能：重複移除準確
- 程式碼：VBA 稳健、有註解
- 效能：處理效率
- 創新：多欄位比對與報表


## Case #9: 自動化備份/還原 ActiveSync 合作關係設定

### Problem Statement
- 業務場景：大規模升級 ActiveSync 4.5，需要自動化備份與（必要時）還原合作關係設定，降低服務台負擔。
- 技術挑戰：批量端點差異與權限；需安靜（silent）執行與記錄。
- 影響範圍：多部門行動用戶。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 合作關係儲存在 HKCU，需用戶上下文操作。
  2. 無標準化腳本與日誌。
  3. 權限與檔案路徑不一致。
- 深層原因：
  - 架構：端點管理缺乏集中化。
  - 技術：對 Registry 操作與流程不熟。
  - 流程：變更前備份未強制化。

### Solution Design
- 解決策略：提供使用者自助批次檔，完成關閉程序→匯出 Registry→備份 PST→記錄；必要時可還原。

- 實施步驟：
  1. 腳本編寫
     - 細節：taskkill、reg export、log 記錄。
     - 資源：批次檔
     - 時間：1 小時
  2. 發布與指引
     - 細節：內網下載、圖文教學。
     - 資源：入口網站
     - 時間：1 小時
  3. 驗證與回報
     - 細節：收集日誌、抽樣驗證。
     - 資源：共享資料夾
     - 時間：1 小時

- 關鍵程式碼/設定：
```bat
@echo off
set LOG=%USERPROFILE%\Desktop\as_backup.log
echo [%date% %time%] Stopping ActiveSync >> "%LOG%"
taskkill /IM wcescomm.exe /F >nul 2>&1
taskkill /IM rapimgr.exe /F >nul 2>&1

echo [%date% %time%] Exporting partnership >> "%LOG%"
reg export "HKCU\Software\Microsoft\Windows CE Services\Partners" "%USERPROFILE%\Desktop\AS_Partners.reg" /y

echo Done. Please backup your Outlook PST via Outlook Export wizard. >> "%LOG%"
```

- 實際案例：批量推行後，服務台單量下降 60%（示例）。
- 實作環境：Windows XP SP2、ActiveSync 4.5。
- 實測數據（示例）：用戶平均操作 < 5 分鐘；成功率 > 95%。

Learning Points
- 核心：端點自助化與可回復性
- 技能：批次檔、日誌管理
- 延伸：加入 PST 自動備份（需關 Outlook）？

Practice
- 基礎：執行備份腳本並檢視日誌（30 分）
- 進階：加入基本健檢（檢查檔案存在）（2 小時）
- 專案：包裝為 MSI 佈署（8 小時）

Assessment
- 功能：備份檔與日誌產出
- 程式碼：錯誤處理完善
- 效能：操作時間
- 創新：圖形化介面/自動回報


## Case #10: 啟用 Intel VT/AMD‑V 讓 Virtual PC 2007 發揮效能

### Problem Statement
- 業務場景：已升級 Virtual PC 2007，但 VM 效能無明顯提升。懷疑 CPU 虛擬化未啟用。
- 技術挑戰：確認硬體支援、BIOS 設定、作業系統報告，並正確啟用。
- 影響範圍：測試環 VM 效能/密度。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. CPU 支援 VT-x/AMD‑V 但 BIOS 預設關閉。
  2. 啟用後未斷電重開機（冷啟）設定未生效。
  3. 主機安全機制（如某些防毒/Hypervisor）衝突。
- 深層原因：
  - 架構：硬體異質，缺乏標準與資產資訊。
  - 技術：未知如何檢測 VT 是否啟用。
  - 流程：無標準化啟用手冊。

### Solution Design
- 解決策略：建立檢測→啟用→驗證三步流程；先用系統指令檢測，再進 BIOS 啟用，最後以指令驗證與 VM 測試。

- 實施步驟：
  1. 檢測
     - 細節：以 systeminfo 或 CIM 查詢是否啟用。
     - 資源：PowerShell/CMD
     - 時間：10 分
  2. 啟用
     - 細節：BIOS 開啟 Intel VT‑x/AMD‑V；關機再開機。
     - 資源：主機 BIOS
     - 時間：10-20 分
  3. 驗證
     - 細節：再次檢測、運行 VM 基準測試。
     - 資源：Virtual PC 2007
     - 時間：20 分

- 關鍵程式碼/設定：
```powershell
# Windows 10+ 檢測（部分屬性依機型/OS）
systeminfo | Select-String "Virtualization Enabled In Firmware"
Get-CimInstance Win32_Processor | Select-Object Name, VirtualizationFirmwareEnabled
```

- 實際案例：原文提到「支援 Intel VT」，啟用後 VM CPU 經延遲降低。
- 實作環境：Intel VT-x/AMD-V CPU、Virtual PC 2007。
- 實測數據（示例）：CPU 密集任務耗時 -20%；VM 密度 +1 台。

Learning Points
- 核心：硬體輔助虛擬化原理
- 技能：BIOS 設定、指令檢測
- 延伸：如何避免與其他 Hypervisor 衝突？

Practice
- 基礎：檢測並記錄主機 VT 狀態（30 分）
- 進階：撰寫批量盤點腳本（2 小時）
- 專案：制定部門級啟用手冊（8 小時）

Assessment
- 功能：正確啟用並生效
- 程式碼：檢測腳本穩定
- 效能：基準提升
- 創新：報表化盤點


## Case #11: 將 Virtual PC 2004 VM 平滑遷移至 Virtual PC 2007

### Problem Statement
- 業務場景：既有 VPC 2004 VM 需移轉到 VPC 2007；擔心驅動與整合功能（Additions）不相容。
- 技術挑戰：避免 Additions/整合元件衝突造成藍屏或裝置失效。
- 影響範圍：測試環可用性、驗證時程。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 舊版 VM Additions 與新版驅動衝突。
  2. 不同虛擬硬體裝置 ID 改變。
  3. 未清理快取/殘留驅動。
- 深層原因：
  - 架構：缺少遷移步驟標準。
  - 技術：對 Additions 升級流程不熟。
  - 流程：缺少回滾還原點。

### Solution Design
- 解決策略：採標準流程「先卸、後升、再驗」：卸載舊 Additions→關機→轉到 VPC 2007→安裝新版 Additions→驗證。

- 實施步驟：
  1. 來源清理
     - 細節：在 VPC 2004 VM 內卸載 Additions、關機。
     - 資源：控制台
     - 時間：10-15 分
  2. 移轉與升級
     - 細節：在 VPC 2007 開啟 VHD，安裝新 Additions。
     - 資源：VPC 2007
     - 時間：15-20 分
  3. 驗證
     - 細節：測網路、滑鼠、視訊整合、時間同步。
     - 資源：測試腳本
     - 時間：20 分

- 關鍵程式碼/設定：
```text
操作提示：
- 使用 VHD 直接掛載至 VPC 2007
- 於 VM 內以「新增/移除程式」移除舊 Additions，再安裝新版本
```

- 實際案例：多台 VM 平滑移轉後，整合功能正常。
- 實作環境：VPC 2004→VPC 2007、Windows XP 32-bit 來賓。
- 實測數據（示例）：單台移轉時間 ~45 分；成功率 100%。

Learning Points
- 核心：Additions 升級順序
- 技能：VM 磁碟遷移、客體驅動管理
- 延伸：如何自動化批量遷移？

Practice
- 基礎：移轉一台 VHD 並安裝 Additions（30 分）
- 進階：撰寫驗證清單（2 小時）
- 專案：小規模批量移轉計畫（8 小時）

Assessment
- 功能：整合功能正常
- 程式碼：流程文件完整
- 效能：移轉耗時可控
- 創新：自動驗證腳本


## Case #12: 用 Virtual PC 2007 差異磁碟建立「修補測試沙箱」

### Problem Statement
- 業務場景：一次爆出多個安全性修補，需在隔離環境快速測試對 OS/應用影響，且可快速回復。
- 技術挑戰：頻繁重置環境、避免污染基準。
- 影響範圍：修補上線時程與風險。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 測試 VM 缺乏快照/回復機制。
  2. 重建 VM 成本高。
  3. 多修補組合需反覆測試。
- 深層原因：
  - 架構：未利用差異磁碟。
  - 技術：不熟 VHD 親子磁碟運作。
  - 流程：無修補測試流程。

### Solution Design
- 解決策略：建立「乾淨母盤 VHD」+ 多個差異磁碟做為測試分支；每個修補集在獨立分支測試，完成後丟棄差異磁碟即可回復。

- 實施步驟：
  1. 建立母盤
     - 細節：安裝 OS、工具、打到基準修補，關機封存。
     - 資源：VPC 2007、VHD 向導
     - 時間：2-3 小時
  2. 建立差異磁碟
     - 細節：以母盤為父，為每組修補建立差異 VHD。
     - 資源：Virtual Disk Wizard
     - 時間：10-15 分/個
  3. 測試與回復
     - 細節：安裝修補、測試、記錄；丟棄差異磁碟回復。
     - 資源：測試腳本
     - 時間：視情況

- 關鍵程式碼/設定：
```text
操作提示：
- Virtual PC 2007 -> File -> Virtual Disk Wizard -> Create a differencing disk
- 指定 Parent VHD（唯讀保存），差異 VHD 存於專案資料夾
```

- 實際案例：春節前修補爆量，以差異磁碟並行測試 3 組路徑。
- 實作環境：Virtual PC 2007、Windows XP/2003 來賓。
- 實測數據（示例）：環境重置時間由 45 分降至 5 分；測試吞吐 +300%。

Learning Points
- 核心：差異磁碟原理與回復策略
- 技能：VHD 管理、測試設計
- 延伸：如何做多層差異鏈？如何管理父盤更新？

Practice
- 基礎：建立一組母/差異 VHD（30 分）
- 進階：為兩組修補建立平行分支（2 小時）
- 專案：制定修補測試 SOP（8 小時）

Assessment
- 功能：快速回復環境
- 程式碼：流程文件清晰
- 效能：重置時間顯著下降
- 創新：並行測試設計


## Case #13: 面對 64 位來賓需求時的虛擬化平台選型

### Problem Statement
- 業務場景：團隊誤以為啟用 Intel VT 後 VPC 2007 可跑 64 位來賓，實際不支援，需提出替代方案。
- 技術挑戰：辨識平台能力、遷移成本與風險。
- 影響範圍：新專案測試與部署時程。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 對 VPC 2007 能力誤解（不支援 64 位來賓）。
  2. 無平台選型評估。
  3. 既有 VHD 與工具鏈相依。
- 深層原因：
  - 架構：虛擬化策略未更新。
  - 技術：對 Hyper-V/VMware 等能力不熟。
  - 流程：無技術評估流程。

### Solution Design
- 解決策略：明確列出需求（64 位來賓、裝置、快照、效能），比對平台（如 Hyper‑V、VMware Workstation/ESXi），規劃遷移路徑與過渡期並行運行。

- 實施步驟：
  1. 需求盤點
     - 細節：來賓 OS、快照、多核心、網路需求。
     - 資源：需求單
     - 時間：0.5 天
  2. 平台 PoC
     - 細節：安裝 Hyper-V/VMware，導入 VHD/VMDK，跑基準。
     - 資源：測試主機
     - 時間：1-2 天
  3. 遷移計畫
     - 細節：新專案上新平台、舊案逐步退出。
     - 資源：變更計畫
     - 時間：1 天

- 關鍵程式碼/設定：
```text
要點：
- Virtual PC 2007 僅支援 32 位來賓
- 可評估 Hyper‑V（支援 64 位來賓、快照、整合服務）
```

- 實際案例：新專案 64 位測試改走 Hyper‑V，VPC 僅保留舊 32 位測試。
- 實作環境：Windows Server/Client with Hyper‑V、VMware。
- 實測數據（示例）：基準一致性與支援度達成 100%。

Learning Points
- 核心：平台能力對齊需求
- 技能：PoC 基準、遷移計畫
- 延伸：如何最小化停機與資料轉換？

Practice
- 基礎：列出需求與平台對照表（30 分）
- 進階：完成 Hyper‑V 來賓 PoC（2 小時）
- 專案：制定 VPC→新平台遷移路線（8 小時）

Assessment
- 功能：選型合理、PoC 通過
- 程式碼：文件與指標清晰
- 效能：基準達標
- 創新：混合運行策略


## Case #14: 大量安全性修補的 WSUS 分環佈署流程

### Problem Statement
- 業務場景：一次爆出十幾個安全性修補，需在風險可控下快速覆蓋全網，避免生產事故。
- 技術挑戰：測試充分、佈署節奏、回報機制與合規。
- 影響範圍：全體 Windows 用戶端與伺服器。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 無分環（Ring）推送策略。
  2. 缺少測試沙箱（見 Case #12）。
  3. 合規與回報機制不完善。
- 深層原因：
  - 架構：未部署 WSUS 或集中更新管理。
  - 技術：GPO/Registry 設定不熟。
  - 流程：變更管理薄弱。

### Solution Design
- 解決策略：建立「測試→試點→廣泛」三環策略，透過 WSUS/GPO 控制佈署，結合回報與合規儀表板，確保安全且快速的推送。

- 實施步驟：
  1. WSUS 設置與同歩
     - 細節：選平台與分類、排程同歩。
     - 資源：WSUS、IIS、SQL
     - 時間：0.5-1 天
  2. GPO 分環
     - 細節：依 OU 分三環，設定自動下載/排程安裝。
     - 資源：AD/GPO
     - 時間：0.5 天
  3. 回報與合規
     - 細節：Get-HotFix/WSUS 報表、合規目標 95%+。
     - 資源：報表工具
     - 時間：持續

- 關鍵程式碼/設定：
```bat
:: 客戶端指向 WSUS（範例）
reg add "HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate" /v WUServer /t REG_SZ /d http://wsus.contoso.com /f
reg add "HKLM\Software\Policies\Microsoft\Windows\Windows\WindowsUpdate" /v WUStatusServer /t REG_SZ /d http://wsus.contoso.com /f
reg add "HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate\AU" /v AUOptions /t REG_DWORD /d 3 /f
reg add "HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate\AU" /v ScheduledInstallDay /t REG_DWORD /d 0 /f
reg add "HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate\AU" /v ScheduledInstallTime /t REG_DWORD /d 3 /f
```

- 實際案例：文中「十幾個 security patch」，以三環 1/3/7 天節奏推送。
- 實作環境：WSUS on Windows Server、AD GPO。
- 實測數據（示例）：7 天內合規達 97%；失敗率 < 2%。

Learning Points
- 核心：分環佈署、策略與合規
- 技能：WSUS/GPO、回報自動化
- 延伸：如何處理離線裝置與遠端節點？

Practice
- 基礎：設立測試 OU 與 WSUS 目標群組（30 分）
- 進階：撰寫合規報表腳本（2 小時）
- 專案：制定季度修補佈署計畫（8 小時）

Assessment
- 功能：分環與策略正確
- 程式碼：設定可重用
- 效能：合規率與時效
- 創新：自動化報表/告警


## Case #15: 修補失敗的回滾與變更凍結策略

### Problem Statement
- 業務場景：修補集中釋出期間，個別 KB 造成應用相容性問題，需快速回滾與調整凍結策略。
- 技術挑戰：跨版本回滾工具差異、識別影響面、溝通與凍結窗口管理。
- 影響範圍：受影響應用與部門。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 個別 KB 與應用衝突。
  2. 未預先測試特定情境。
  3. 回滾步驟不熟或無自動化。
- 深層原因：
  - 架構：缺少標準回滾劇本。
  - 技術：舊/新系統回滾工具差異未梳理。
  - 流程：凍結策略與例外流程不足。

### Solution Design
- 解決策略：建立「識別→隔離→回滾→豁免」流程與 SOP，包含各 OS 回滾命令、測試用例、凍結與豁免表單，並在 WSUS 上暫停有問題的 KB。

- 實施步驟：
  1. 快速識別
     - 細節：蒐集事件、比對 KB；在 WSUS 暫停/拒絕該 KB。
     - 資源：WSUS 控制台
     - 時間：15 分
  2. 回滾執行
     - 細節：依 OS 使用合適工具（wusa/spuninst），記錄。
     - 資源：PowerShell/CMD
     - 時間：30-60 分
  3. 凍結與改期
     - 細節：啟動變更凍結與例外審批；更新時程。
     - 資源：變更管理系統
     - 時間：視情況

- 關鍵程式碼/設定：
```bat
:: Windows 7/2008 R2+ 回滾
wusa /uninstall /kb:5000000 /quiet /norestart

:: Windows XP/2003 舊式回滾（安裝目錄示例）
C:\Windows\$NtUninstallKB5000000$\spuninst\spuninst.exe /quiet /norestart
```

- 實際案例：問題 KB 暫停 24 小時內完成回滾與替代方案測試。
- 實作環境：混合 OS、WSUS 管理。
- 實測數據（示例）：MTTR < 2 小時；事故影響面 < 10 台。

Learning Points
- 核心：回滾與凍結策略
- 技能：各版本回滾工具使用
- 延伸：如何自動判斷並回滾指定 KB？

Practice
- 基礎：實驗室回滾一個 KB（30 分）
- 進階：批次回滾腳本（2 小時）
- 專案：建立凍結/豁免流程文件（8 小時）

Assessment
- 功能：快速回滾成功
- 程式碼：腳本安全且可追蹤
- 效能：MTTR 指標
- 創新：自動化與例外流程整合



————————
案例分類
————————

1) 按難度分類
- 入門級（適合初學者）
  - Case 6, 7, 8, 9, 11
- 中級（需要一定基礎）
  - Case 2, 3, 4, 5, 10, 12, 13, 15
- 高級（需要深厚經驗）
  - Case 1, 14

2) 按技術領域分類
- 架構設計類
  - Case 1, 12, 13, 14, 15
- 效能優化類
  - Case 2, 3, 10
- 整合開發類
  - Case 4, 8, 9, 11
- 除錯診斷類
  - Case 5, 6, 7
- 安全防護類
  - Case 14, 15

3) 按學習目標分類
- 概念理解型
  - Case 10, 12, 13, 14
- 技能練習型
  - Case 4, 6, 7, 8, 9, 11
- 問題解決型
  - Case 1, 2, 3, 5, 15
- 創新應用型
  - Case 12, 14（流程與自動化設計）



————————
案例關聯圖（學習路徑建議）
————————

- 建議先學順序（由淺入深）：
  1) Case 6 → 7 → 8 → 9（ActiveSync 升級、連線、去重與自動化，一條完整端點升級線）
  2) Case 11 → 10 → 12 → 13（VPC 遷移→啟用 VT→差異磁碟測試→平台選型）
  3) Case 4 → 3 → 5 → 2 → 1（SQL 維護腳本→健康檢查→作業診斷→相容等級→零停機升級）
  4) Case 12 → 14 → 15（修補測試沙箱→WSUS 分環→回滾與凍結）

- 依賴關係：
  - Case 12 是 Case 14 的測試基礎（修補沙箱先於分環佈署）
  - Case 4/3 是 Case 1/2 的基礎（維護與健康檢查先於升級/相容切換）
  - Case 6/8/9 互為前後關係（備份→重建→去重）
  - Case 11 先於 Case 10（先安定遷移，再談效能）

- 完整學習路徑建議：
  - 初學者路徑：Case 6 → 7 → 8 → 9 → 11 → 10
  - DBA 路徑：Case 4 → 3 → 5 → 2 → 1
  - IT 安全/維運路徑：Case 12 → 14 → 15 → 13（認知平台能力，避免錯誤期待）
  - 綜合實戰（專案級）：Case 12 → 14 → 1 → 2 → 3 → 4 → 5（從修補到資料庫升級的端到端演練）

以上 15 個案例，均從原文提到的技術事件出發，擴展為可落地的實戰教學與評測素材。