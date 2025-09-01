以下內容基於原文「升級失敗… Orz」重構，圍繞「CS 2.0 RTM → 2.1 SP2 升級後整站無法啟動且錯誤被產品機制隱藏」這一核心情境，擴展為可實作、可教學、可評估的 15 個完整案例。每個案例都包含問題、根因、方案、實施步驟、範例程式與評估方式。實測數據部分如未出現在原文，提供可替換的示例口徑與量測方法。

## Case #1: 升級後錯誤被產品錯誤頁遮蔽，無法快速定位問題

### Problem Statement（問題陳述）
**業務場景**：將 Community Server（CS）從 2.0 RTM 升級到 2.1 SP2 後，網站啟動即顯示通用錯誤頁。產品內建的錯誤回報機制攔截了詳細例外與堆疊，導致工程師只能看到「Error」字樣，無法得知是哪個組件、設定或資料庫步驟出錯，排查效率極低，維修時間拉長。
**技術挑戰**：例外被應用層錯誤處理包裹；ASP.NET customErrors 啟用、debug 關閉、缺乏外部日誌。
**影響範圍**：整站不可用、MTTD 增長、RTO 增長、使用者流失、營收/口碑受損。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 啟用 customErrors，導致詳細錯誤不顯示。
2. 產品層錯誤攔截（HTTP Module/Handler）吞掉例外堆疊。
3. 未配置任何持久化日誌（EventLog/檔案/DB）。

**深層原因**：
- 架構層面：單一錯誤處理模組攔截一切例外，缺少旁路與降級策略。
- 技術層面：web.config 未針對維運切換到「診斷模式」；缺少健康監控。
- 流程層面：升級前未列入「開啟詳細錯誤」的預備步驟。

### Solution Design（解決方案設計）
**解決策略**：在維修視窗內暫時開啟 ASP.NET 詳細錯誤、追蹤與健康監控，必要時暫時移除/停用產品錯誤處理模組，增加 Global.asax 的 Application_Error 持久化記錄，快速取得完整堆疊與環境上下文，縮短定位時間。

**實施步驟**：
1. 開啟詳細錯誤與追蹤
- 實作細節：web.config 設 customErrors="Off"、compilation debug="true"、trace enabled="true"
- 所需資源：IIS 管理權限
- 預估時間：10 分鐘

2. 暫停產品錯誤攔截
- 實作細節：暫時註解/移除相應的 httpModule 或產品錯誤頁設定（升級完畢再恢復）
- 所需資源：產品文件、IIS 重啟權限
- 預估時間：10-20 分鐘

3. 加入 Application_Error 記錄
- 實作細節：在 Global.asax 將例外寫入 EventLog/檔案
- 所需資源：檔案系統寫入權限或 EventLog 權限
- 預估時間：15 分鐘

**關鍵程式碼/設定**：
```xml
<!-- web.config：開啟詳細錯誤與追蹤，維修完畢務必關閉 -->
<configuration>
  <system.web>
    <customErrors mode="Off" />
    <compilation debug="true" />
    <trace enabled="true" pageOutput="false" mostRecent="true" />
    <healthMonitoring enabled="true">
      <rules>
        <add name="All Errors To EventLog" eventName="All Errors"
             provider="EventLogProvider" profile="Default" minInterval="00:01:00" />
      </rules>
    </healthMonitoring>
  </system.web>
</configuration>
```

```csharp
// Global.asax：最低可用的錯誤落地策略
void Application_Error(object sender, EventArgs e)
{
    var ex = Server.GetLastError();
    try
    {
        System.IO.File.AppendAllText(
          Server.MapPath("~/App_Data/errors.log"),
          DateTime.Now + " " + ex.ToString() + Environment.NewLine);
    }
    catch { /* 防止次生錯誤中斷 */ }
}
```

實際案例：原文情境：升級至 CS 2.1 SP2 後只見 Error，錯誤細節被產品機制隐藏。
實作環境：Windows Server 2003/IIS 6、.NET 2.0、SQL Server 2005、CS 2.0→2.1 SP2。
實測數據：
- 改善前：MTTD > 30 分鐘；幾乎無堆疊。
- 改善後：MTTD < 3 分鐘；完整堆疊可得。
- 改善幅度：定位時間縮短約 90%

Learning Points（學習要點）
核心知識點：
- ASP.NET customErrors/compilation/trace 的影響
- 健康監控與 Global.asax Application_Error
- 產品級錯誤攔截的旁路方法

技能要求：
- 必備技能：IIS/ASP.NET 基本設定、web.config 編輯
- 進階技能：模組/處理常式診斷、健康監控事件路由

延伸思考：
- 可整合集中式日誌（ELK、Seq）
- 風險：詳細錯誤暴露風險，僅限維修視窗
- 優化：以環境變數或變更旗標自動切換診斷模式

Practice Exercise（練習題）
- 基礎練習：在本機開啟 customErrors Off 並觸發一個錯誤，確認 log 落地（30 分鐘）
- 進階練習：加入健康監控規則並寫入 EventLog（2 小時）
- 專案練習：做一個「維修模式切換器」工具，可一鍵切換診斷模式（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能顯示詳細錯誤並可靠落地
- 程式碼品質（30%）：錯誤處理完整，不影響正常流程
- 效能優化（20%）：診斷模式不顯著拖慢系統
- 創新性（10%）：提供自動化切換與安全控管

---

## Case #2: 以「影子拷貝 + DB 備份」建立可驗證的快速回復機制（Rollback）

### Problem Statement（問題陳述）
**業務場景**：升級後站台無法啟動且無法即時定位，需要快速恢復服務。作者用「shadow copy」回復檔案，但缺少可重複、可驗證、含資料庫的完整回復流程，風險仍在。
**技術挑戰**：需同時保證檔案與資料庫一致性、回復時間短且可自動化。
**影響範圍**：長時間中斷、資料不一致風險、回復不確定性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 僅回復檔案，DB 可能已部份升級。
2. 沒有原子性回復步驟與驗證清單。
3. 手作回復耗時、容易誤操作。

**深層原因**：
- 架構層面：缺少藍綠/金絲雀或版本化資產管理。
- 技術層面：未腳本化的備份/回復流程。
- 流程層面：無回復演練與 RTO/RPO 目標。

### Solution Design（解決方案設計）
**解決策略**：建立「檔案快照 + DB 備份」雙保險，並以腳本化與核對清單確保一致性；提供原子切換（資料夾別名/符號連結），將 RTO 壓到分鐘級。

**實施步驟**：
1. 升級前快照與備份
- 實作細節：robocopy 做網站根目錄快照；SQL FULL 備份；紀錄版本
- 所需資源：磁碟空間、SQL 權限
- 預估時間：15-30 分鐘（依大小）

2. 原子切換與回復腳本
- 實作細節：用目錄切換或 symlink 指向「current」；失敗時切回
- 所需資源：PowerShell、IIS reset 權限
- 預估時間：15 分鐘

3. 回復驗證清單
- 實作細節：檢查首頁、登入、發文等核心流程
- 所需資源：測試帳號、清單
- 預估時間：10-20 分鐘

**關鍵程式碼/設定**：
```powershell
# 1) 檔案快照
$src="C:\inetpub\wwwroot\CS"
$snapshot="D:\snapshots\CS_$(Get-Date -f yyyyMMdd_HHmm)"
robocopy $src $snapshot /MIR /Z /R:1 /W:1 /XF web.config

# 2) DB 備份（SQLCMD）
sqlcmd -S .\SQLEXPRESS -Q "BACKUP DATABASE [CSDB] TO DISK='D:\snapshots\CSDB_full.bak' WITH INIT, COPY_ONLY"

# 3) 原子切換（以 junction/symlink 管理 current）
# 先準備新版本到 C:\sites\CS_v2.1，再切換 C:\inetpub\wwwroot\CS → current
```

實際案例：原文使用 shadow copy 回復檔案。本方案擴充成系統化回復含 DB。
實作環境：Windows Server 2003/2008、IIS、SQL Server 2005。
實測數據：
- 改善前：回復耗時 30-60 分鐘，易遺漏
- 改善後：RTO 5-10 分鐘可復原（檔案+DB）
- 改善幅度：回復時間縮短 70-90%

Learning Points（學習要點）
- 回復設計要同時涵蓋檔案與資料
- 原子切換與快照策略
- 腳本化與演練的重要性

技能要求：
- 必備技能：robocopy/PowerShell、SQL 備份/還原
- 進階技能：原子部署（symlink/junction）、自動驗證

延伸思考：
- 可導入藍綠部署、金絲雀釋出
- 風險：快照未含權限/隱藏檔，需驗證
- 優化：加入備份完整性校驗（RESTORE VERIFYONLY）

Practice Exercise
- 基礎：寫一個檔案快照腳本（30 分鐘）
- 進階：加入 SQL 備份與還原測試（2 小時）
- 專案：做一鍵回復工具與驗證清單（8 小時）

Assessment Criteria
- 功能完整性（40%）：可完整回復檔案+DB
- 程式碼品質（30%）：腳本穩定、容錯良好
- 效能（20%）：RTO 可量化下降
- 創新（10%）：原子切換/驗證自動化

---

## Case #3: 升級 SQL 腳本的交易安全與斷點恢復

### Problem Statement
**業務場景**：執行「2.x → 2.1」的 SQL 升級腳本後，站台無法啟動，懷疑資料庫模式部份更新。需避免半套用狀態，並能在錯誤時自動回滾。
**技術挑戰**：老腳本缺少交易、錯誤處理、版本守衛；可能多批次依賴順序。
**影響範圍**：資料不一致、應用啟動失敗、回復困難。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 升級腳本無交易包覆，錯誤即殘留半狀態。
2. 未檢查當前版本即執行不相容操作。
3. 缺少錯誤日誌與執行審計。

**深層原因**：
- 架構層面：無中心化版本表與遷移歷史。
- 技術層面：腳本未啟用 XACT_ABORT、TRY...CATCH。
- 流程層面：缺少預演與驗證。

### Solution Design
**解決策略**：為升級腳本加上交易與版本守衛，錯誤自動回滾；先在 staging 完整預演。將每步寫入審計表，便於追蹤與重跑。

**實施步驟**：
1. 版本偵測與守衛
- 實作細節：讀取版本表（若未知，先掃描包含 Version 字樣資料表）
- 所需資源：DBA 權限
- 預估時間：20 分鐘

2. 交易化與錯誤處理
- 實作細節：XACT_ABORT、TRY/CATCH、錯誤時 ROLLBACK + 記錄
- 所需資源：SQLCMD/SSMS
- 預估時間：30-60 分鐘

3. 審計與重跑
- 實作細節：建立 MigrationHistory 表記錄每步
- 所需資源：DB 權限
- 預估時間：30 分鐘

**關鍵程式碼/設定**：
```sql
-- 發現版本表（通用探測）
SELECT name FROM sys.tables WHERE name LIKE '%Version%' OR name LIKE '%Schema%';

-- 交易化升級框架
SET XACT_ABORT ON;
BEGIN TRY
  BEGIN TRAN;

  -- 版本守衛
  DECLARE @currentVersion NVARCHAR(50) = (SELECT TOP 1 Version FROM dbo.MigrationHistory ORDER BY AppliedAt DESC);
  IF @currentVersion IS NULL SET @currentVersion = '2.0.0';
  IF @currentVersion <> '2.0.0' RAISERROR('Unexpected DB version',16,1);

  -- 示例：加欄位
  ALTER TABLE dbo.Posts ADD IsArchived BIT NOT NULL DEFAULT(0);

  -- 記錄
  INSERT dbo.MigrationHistory(ScriptName,Version,AppliedAt) VALUES('2.1-upgrade.sql','2.1.0',GETDATE());

  COMMIT TRAN;
END TRY
BEGIN CATCH
  IF @@TRANCOUNT > 0 ROLLBACK TRAN;
  DECLARE @msg NVARCHAR(4000)=ERROR_MESSAGE();
  INSERT dbo.MigrationErrors(WhenAt,Message) VALUES(GETDATE(),@msg);
  RAISERROR(@msg,16,1);
END CATCH;
```

實際案例：原文執行 2.x→2.1 升級腳本後站台起不來，疑似 DB 差異導致。
實作環境：SQL Server 2005 及以上。
實測數據：
- 改善前：半套用機率高、回復困難
- 改善後：錯誤自動回滾，DB 一致性保證；重跑成本下降 80%
- 改善幅度：DB 回復與可追蹤性大幅提升

Learning Points
- 交易與 XACT_ABORT 的必要性
- 版本守衛與審計表設計
- 先行預演的重要性

技能要求：
- 必備：T-SQL、交易/錯誤處理
- 進階：資料庫遷移框架思維

延伸思考：
- 導入 Flyway/Liquibase 類工具可行性
- 風險：長交易引發鎖定，需分批
- 優化：冪等化腳本設計

Practice Exercise
- 基礎：將一個 ALTER 腳本包裝成交易+錯誤處理（30 分鐘）
- 進階：設計 MigrationHistory 與錯誤表（2 小時）
- 專案：把整個 2.x→2.1 腳本重構為可重跑遷移（8 小時）

Assessment Criteria
- 功能（40%）：錯誤自動回滾
- 品質（30%）：腳本冪等、可讀性
- 效能（20%）：鎖影響最小化
- 創新（10%）：審計與報表

---

## Case #4: 使用 app_offline.htm 安全進入維護模式

### Problem Statement
**業務場景**：升級期間用戶仍可能進站，導致在不一致狀態下操作，引發更多錯誤與資料污染。需迅速切入維護模式並提供友善訊息。
**技術挑戰**：IIS 上如何確保應用停擺但服務不中斷（回應 503/維護頁）。
**影響範圍**：避免用戶誤操作與抱怨，保護資料一致性。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無維護模式，升級期間仍有流量。
2. 用戶體驗差，反覆刷新誤操作。
3. 工程師在壓力下排錯，風險上升。

**深層原因**：
- 架構層面：缺少閘門（gate）策略。
- 技術層面：不熟悉 app_offline.htm 特性。
- 流程層面：維護視窗與公告不足。

### Solution Design
**解決策略**：在站台根目錄放置 app_offline.htm 以讓 ASP.NET 自動卸載 AppDomain，所有請求回傳該頁；升級完成後移除即可。

**實施步驟**：
1. 準備維護頁
- 實作細節：提供服務時間、客服、狀態連結
- 所需資源：靜態 HTML
- 預估時間：15 分鐘

2. 進入/退出維護模式
- 實作細節：放置/移除 app_offline.htm
- 所需資源：檔案系統
- 預估時間：1 分鐘

**關鍵程式碼/設定**：
```html
<!-- app_offline.htm 範例 -->
<!doctype html><html><head><meta charset="utf-8"><title>維護中</title>
<style>body{font-family:sans-serif;padding:40px}</style></head>
<body>
<h2>系統維護中</h2>
<p>預計 02:00-03:00 完成。請稍後再試或關注 <a href="https://status.example.com">狀態頁</a>。</p>
</body></html>
```

實際案例：原文升級時直接嘗試，未提及維護頁；此步能顯著降低用戶影響。
實作環境：IIS 6/7/8，ASP.NET。
實測數據：
- 改善前：升級期間 5-10% 用戶遭遇錯誤
- 改善後：錯誤率降至 <1%，投訴下降
- 改善幅度：故障曝光降低 80%+

Learning Points
- app_offline.htm 的機制
- 用戶溝通與體驗設計
- 維運視窗管理

技能要求：
- 必備：IIS/檔案操作
- 進階：自動化切換與公告

延伸思考：
- 配合狀態頁、流量導流
- 風險：忘記移除；需清單管控
- 優化：腳本自動加/移與驗證

Practice Exercise
- 基礎：建立 app_offline.htm 並手動測試（30 分鐘）
- 進階：製作切換腳本與通知（2 小時）
- 專案：整合 CI/CD 加入維護模式步驟（8 小時）

Assessment Criteria
- 功能（40%）：可靠阻擋請求
- 品質（30%）：頁面資訊清楚
- 效能（20%）：切換快速無殘留
- 創新（10%）：自動化與狀態整合

---

## Case #5: 升級後 web.config/communityserver.config 差異合併策略

### Problem Statement
**業務場景**：更新檔案後常見因設定差異導致啟動失敗（缺少新節點/多餘舊節點/版本不相容）。需安全合併 2.0 與 2.1 的設定。
**技術挑戰**：手動合併易錯；缺乏差異檢測與回滾。
**影響範圍**：啟動錯誤、功能缺失、隱藏錯誤。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 未比對新舊設定 schema。
2. 手動 Copy 覆蓋造成遺漏/重複。
3. 環境特定設定（連線字串）被覆蓋。

**深層原因**：
- 架構層面：設定與程式未分離。
- 技術層面：缺少差異工具與變更管理。
- 流程層面：無設定合併準則與審核。

### Solution Design
**解決策略**：建立「範本設定」與「環境覆蓋」的雙層策略；先用差異工具比對，針對 appSettings/httpModules/connectionStrings 做白名單合併與驗證。

**實施步驟**：
1. 差異分析
- 實作細節：比較 CS 2.1 新版 config 與現有 config
- 所需資源：WinMerge/BeyondCompare 或 PowerShell
- 預估時間：30-60 分鐘

2. 白名單合併
- 實作細節：僅合併必要節點，保留環境變數
- 所需資源：設定清單
- 預估時間：30 分鐘

3. 驗證與備份
- 實作細節：備份、啟動自測
- 所需資源：備份空間
- 預估時間：20 分鐘

**關鍵程式碼/設定**：
```powershell
# 比對兩份 web.config 的 appSettings/connectionStrings 差異
[xml]$old = Get-Content ".\web_old.config"
[xml]$new = Get-Content ".\web_new.config"

"== appSettings new keys =="
$oldKeys=$old.configuration.appSettings.add|%{$_.key}
$new.configuration.appSettings.add|?{$_.key -notin $oldKeys}|%{$_.key}

"== connectionStrings names only =="
$oldCon=$old.configuration.connectionStrings.add|%{$_.name}
$new.configuration.connectionStrings.add|?{$_.name -notin $oldCon}|%{$_.name}
```

實際案例：原文描述「更新檔案」但起不來，常見是 config 差異所致。
實作環境：ASP.NET 2.0。
實測數據：
- 改善前：配置錯誤導致啟動失敗率 20-30%
- 改善後：降至 <5%
- 改善幅度：錯誤下降 80%+

Learning Points
- 設定變更即程式變更
- 白名單合併與環境保護
- 差異工具與腳本

技能要求：
- 必備：XML 基礎、差異比對
- 進階：配置管理與審核流程

延伸思考：
- 引入環境變數或外部化設定
- 風險：手動操作出錯
- 優化：自動化合併與驗證

Practice Exercise
- 基礎：用工具標示差異（30 分鐘）
- 進階：寫腳本產生差異報告（2 小時）
- 專案：建立 config 範本+覆蓋流程（8 小時）

Assessment Criteria
- 功能（40%）：合併正確啟動成功
- 品質（30%）：可讀性、可追蹤
- 效能（20%）：自動化程度
- 創新（10%）：校驗與回滾設計

---

## Case #6: 升級後檔案/資料夾權限不足導致啟動失敗

### Problem Statement
**業務場景**：更新檔案後因 ACL 丟失或變更，IIS 執行帳號對 App_Data/Uploads/Logs 等目錄無寫入權限，應用啟動或運行時失敗。
**技術挑戰**：辨識需要授權的目錄並快速修復權限。
**影響範圍**：啟動失敗、上傳/快取/日誌功能失效。
**複雜度評級**：低-中

### Root Cause Analysis
**直接原因**：
1. 覆蓋檔案重置了 ACL。
2. 新版本新增目錄未授權。
3. 檔案屬性唯讀或鎖定。

**深層原因**：
- 架構層面：寫入路徑散落。
- 技術層面：不熟悉 IIS 執行身分與 ACL。
- 流程層面：未列入權限檢查。

### Solution Design
**解決策略**：列出需寫入目錄清單並以腳本套用權限，升級前後自動驗證，避免人為遺漏。

**實施步驟**：
1. 盤點寫入目錄
- 實作細節：App_Data、Uploads、Logs、Temp
- 所需資源：產品文件
- 預估時間：20 分鐘

2. 套用權限
- 實作細節：icacls/xcacls 設定 NETWORK SERVICE 或應用池帳號
- 所需資源：系統管理權限
- 預估時間：10-20 分鐘

3. 驗證
- 實作細節：建立測試寫入檔案
- 所需資源：測試頁或小工具
- 預估時間：10 分鐘

**關鍵程式碼/設定**：
```bat
REM 適用於 Windows 2008+ 使用 icacls（2003 可用 cacls）
icacls "C:\inetpub\wwwroot\CS\App_Data" /grant "NETWORK SERVICE:(OI)(CI)M" /T
icacls "C:\inetpub\wwwroot\CS\Uploads"   /grant "NETWORK SERVICE:(OI)(CI)M" /T
icacls "C:\inetpub\wwwroot\CS\Logs"      /grant "NETWORK SERVICE:(OI)(CI)M" /T
```

實際案例：升級後站台不起可能為權限問題之一。
實作環境：IIS 6/7。
實測數據：
- 改善前：權限造成的啟動/運行錯誤 10-20%
- 改善後：<2%
- 改善幅度：下降 80%+

Learning Points
- IIS 帳號與權限模型
- 寫入路徑盤點
- 腳本化 ACL 設定

技能要求：
- 必備：Windows ACL 基礎
- 進階：安全最小化授權

延伸思考：
- 使用虛擬帳號與隔離
- 風險：過度授權
- 優化：以檔案清單驅動的精準授權

Practice Exercise
- 基礎：對 App_Data 設定寫入並測試（30 分鐘）
- 進階：整理完整授權腳本（2 小時）
- 專案：做一鍵權限健康檢查工具（8 小時）

Assessment Criteria
- 功能（40%）：正確授權、運作無誤
- 品質（30%）：最小權限、可維護
- 效能（20%）：自動化程度
- 創新（10%）：健康檢查與報告

---

## Case #7: 清理 ASP.NET 暫存與重建應用程式快取

### Problem Statement
**業務場景**：升級後仍載入舊版組件或暫存檔，引起版本衝突、類型載入錯誤。
**技術挑戰**：辨識與清理 ASP.NET Temporary Files。
**影響範圍**：啟動失敗或偶發例外。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 暫存舊版組件/預編譯產物未清。
2. 部署未完全覆蓋。
3. 應用域未正確回收。

**深層原因**：
- 架構層面：缺乏乾淨部署流程。
- 技術層面：不熟悉 ASP.NET 暫存目錄。
- 流程層面：缺少清理步驟。

### Solution Design
**解決策略**：升級後清除 Temporary ASP.NET Files、回收應用池，確保載入全新組件與編譯產物。

**實施步驟**：
1. 停站/回收
- 實作細節：app_offline.htm 或 iisreset
- 所需資源：IIS 管理權限
- 預估時間：5 分鐘

2. 清理暫存
- 實作細節：刪除對應 .NET 版本的 Temporary ASP.NET Files
- 所需資源：檔案系統
- 預估時間：5-10 分鐘

3. 重啟驗證
- 實作細節：重啟站台、驗證頁面
- 所需資源：瀏覽器/腳本
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bat
REM .NET 2.0 位置
rmdir /s /q "C:\Windows\Microsoft.NET\Framework\v2.0.50727\Temporary ASP.NET Files"
rmdir /s /q "C:\Windows\Microsoft.NET\Framework64\v2.0.50727\Temporary ASP.NET Files"
iisreset
```

實際案例：升級後起不來，清理暫存常能排除舊檔干擾。
實作環境：.NET 2.0。
實測數據：
- 改善前：因暫存導致的啟動錯誤 5-10%
- 改善後：<1%
- 改善幅度：下降 80%+

Learning Points
- ASP.NET 暫存原理
- 部署與回收關聯
- 清理時機

技能要求：
- 必備：IIS 操作、檔案系統
- 進階：自動化清理

延伸思考：
- 以 CI/CD 做 Clean Deploy
- 風險：刪錯目錄
- 優化：以腳本安全刪除並記錄

Practice Exercise
- 基礎：清理暫存並驗證（30 分鐘）
- 進階：整合部署腳本（2 小時）
- 專案：實作 Clean Deploy 流程（8 小時）

Assessment Criteria
- 功能（40%）：清理有效、啟動正常
- 品質（30%）：腳本安全
- 效能（20%）：自動化程度
- 創新（10%）：與 CI/CD 整合

---

## Case #8: 組件版本衝突與 assemblyBinding 重導

### Problem Statement
**業務場景**：升級帶入新 DLL，舊程式參考舊版導致 TypeLoad/FileLoad 例外。需用 assembly binding redirect 導正。
**技術挑戰**：辨識衝突組件、撰寫正確的 bindingRedirect。
**影響範圍**：應用啟動或特定功能失效。
**複雜度評級**：中-高

### Root Cause Analysis
**直接原因**：
1. 不同版本 DLL 混用。
2. Publisher policy 不一致。
3. GAC/本地 bin 版本衝突。

**深層原因**：
- 架構層面：組件相依複雜。
- 技術層面：缺少 Fusion log 診斷。
- 流程層面：未控管相依版本矩陣。

### Solution Design
**解決策略**：開啟 Fusion Log 取得載入資訊，釐清組件版本，於 web.config/runtime 設定 assemblyBinding redirect。

**實施步驟**：
1. 啟用 Fusion Log
- 實作細節：Fusion Log Viewer 或登錄檔設定
- 所需資源：系統權限
- 預估時間：20 分鐘

2. 撰寫 bindingRedirect
- 實作細節：鎖定 problem assembly，設定 newVersion
- 所需資源：web.config 編輯
- 預估時間：20 分鐘

3. 驗證
- 實作細節：重啟並觀察無載入錯誤
- 所需資源：IIS
- 預估時間：10 分鐘

**關鍵程式碼/設定**：
```xml
<configuration>
  <runtime>
    <assemblyBinding xmlns="urn:schemas-microsoft-com:asm.v1">
      <dependentAssembly>
        <assemblyIdentity name="YourProblemAssembly" publicKeyToken="32ab4ba45e0a69a1" culture="neutral"/>
        <bindingRedirect oldVersion="0.0.0.0-2.1.0.0" newVersion="2.1.0.0"/>
      </dependentAssembly>
    </assemblyBinding>
  </runtime>
</configuration>
```

實際案例：升級 CS 可能帶入新版本核心 DLL，需導正相依。
實作環境：.NET 2.0。
實測數據：
- 改善前：TypeLoad/FileLoad 例外頻發
- 改善後：消除相依錯誤、穩定啟動
- 改善幅度：啟動成功率顯著提升

Learning Points
- Fusion Log 使用
- assemblyBinding 原理
- 相依版本矩陣

技能要求：
- 必備：web.config/runtime 知識
- 進階：診斷與 GAC/本地衝突處理

延伸思考：
- 用 NuGet/包管理統一版本（新平台）
- 風險：錯誤重導造成潛在不相容
- 優化：最小範圍重導與測試

Practice Exercise
- 基礎：為指定 DLL 加入 bindingRedirect（30 分鐘）
- 進階：用 Fusion Log 定位衝突（2 小時）
- 專案：做一個相依掃描+建議 redirect 的工具（8 小時）

Assessment Criteria
- 功能（40%）：衝突解決
- 品質（30%）：設定準確
- 效能（20%）：診斷效率
- 創新（10%）：自動建議/報表

---

## Case #9: 驗證 IIS/.NET 映射與應用程式集區設定

### Problem Statement
**業務場景**：升級後發生「無法載入 .NET」或 handler 無對應，疑似 ASP.NET 映射遺失或應用程式集區版本錯誤。
**技術挑戰**：在 IIS 6/7 上正確設定 .NET 版本與映射。
**影響範圍**：整站不可用。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. ASP.NET 映射未正確註冊。
2. 應用程式集區使用錯誤 .NET 版本。
3. 32/64 位混用。

**深層原因**：
- 架構層面：環境管理鬆散。
- 技術層面：IIS 與 .NET 管理不熟。
- 流程層面：變更未記錄。

### Solution Design
**解決策略**：確認 IIS 應用程式集區所用 .NET 版本與管線模式，必要時用 aspnet_regiis 重建映射。

**實施步驟**：
1. 檢查映射
- 實作細節：aspnet_regiis -lv/-lk
- 所需資源：系統權限
- 預估時間：10 分鐘

2. 設定站台映射
- 實作細節：aspnet_regiis -s W3SVC/... 或在 IIS 管理員選擇正確版本
- 所需資源：IIS 管理員
- 預估時間：10-20 分鐘

3. 驗證與回收
- 實作細節：回收應用程式集區
- 所需資源：IIS
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bat
"C:\Windows\Microsoft.NET\Framework\v2.0.50727\aspnet_regiis.exe" -lv
"C:\Windows\Microsoft.NET\Framework\v2.0.50727\aspnet_regiis.exe" -s W3SVC/1/ROOT/CS
```

實際案例：升級後起不來，需排除環境層問題。
實作環境：IIS 6/7、.NET 2.0。
實測數據：
- 改善前：環境錯誤占比 10%
- 改善後：<2%
- 改善幅度：下降 80%

Learning Points
- aspnet_regiis 的用途
- App Pool 與 .NET 映射
- 32/64 位注意事項

技能要求：
- 必備：IIS 管理
- 進階：自動化配置

延伸思考：
- IaC 管理 IIS 設定
- 風險：誤設影響其他站台
- 優化：最小範圍註冊

Practice Exercise
- 基礎：列出版本映射（30 分鐘）
- 進階：設定特定站台映射（2 小時）
- 專案：腳本化站台/IIS 配置（8 小時）

Assessment Criteria
- 功能（40%）：映射正確
- 品質（30%）：無副作用
- 效能（20%）：自動化程度
- 創新（10%）：IaC 化

---

## Case #10: 隔離外掛/自訂模組，建立「安全模式」啟動

### Problem Statement
**業務場景**：升級後第三方外掛或自訂模組與新版本不相容，導致啟動失敗。需快速隔離非核心組件。
**技術挑戰**：識別外掛存放與載入機制，安全下線。
**影響範圍**：整站或部分功能異常。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 外掛與核心 API 變更不相容。
2. 外掛覆蓋相同命名空間/DLL。
3. 升級前未進行相容性檢查。

**深層原因**：
- 架構層面：可插拔但缺少相容性治理。
- 技術層面：外掛載入約定不清。
- 流程層面：未建立「安全模式」啟動流程。

### Solution Design
**解決策略**：建立安全模式：僅保留核心 DLL，將第三方/自訂 DLL 暫移到隔離資料夾，先確認核心可啟動，再逐一回加。

**實施步驟**：
1. 識別非核心 DLL
- 實作細節：以命名規則/簽章過濾非 Telligent/CommunityServer 前綴
- 所需資源：PowerShell
- 預估時間：15 分鐘

2. 暫移並啟動
- 實作細節：將非核心 DLL 移至 bin\_off，啟動並驗證
- 所需資源：檔案操作權限
- 預估時間：10-20 分鐘

3. 逐一回加
- 實作細節：逐個加回並測試，定位不相容者
- 所需資源：測試清單
- 預估時間：60 分鐘+

**關鍵程式碼/設定**：
```powershell
$bin="C:\inetpub\wwwroot\CS\bin"
$off="$bin\_off"
New-Item -ItemType Directory -Force -Path $off | Out-Null
Get-ChildItem $bin -Filter *.dll | Where-Object {
  $_.Name -notmatch "^CommunityServer|^Telligent"
} | Move-Item -Destination $off
```

實際案例：升級起不來時先確保核心可啟動，再排除外掛干擾。
實作環境：CS 2.x、ASP.NET 2.0。
實測數據：
- 改善前：定位不相容外掛需半天
- 改善後：1-2 小時內完成定位
- 改善幅度：排查時間下降 60-80%

Learning Points
- 可插拔相容性治理
- 安全模式策略
- 漸進回加法

技能要求：
- 必備：檔案與模組管理
- 進階：載入順序與相依分析

延伸思考：
- 啟動參數切安全模式
- 風險：遺漏必要模組
- 優化：自動化掃描相依

Practice Exercise
- 基礎：搬移非核心 DLL 並啟動（30 分鐘）
- 進階：逐一回加定位（2 小時）
- 專案：安全模式切換工具（8 小時）

Assessment Criteria
- 功能（40%）：核心可啟動
- 品質（30%）：操作安全可回復
- 效能（20%）：定位效率
- 創新（10%）：自動識別外掛

---

## Case #11: 升級前置檢查清單（Preflight Checklist）

### Problem Statement
**業務場景**：缺少升級前檢查導致中途失敗與回退。需以清單化確保可控。
**技術挑戰**：全面盤點依賴、空間、備援、視窗、人力。
**影響範圍**：降低升級風險與未知數。
**複雜度評級**：低-中

### Root Cause Analysis
**直接原因**：
1. 未確認磁碟空間/備份可用。
2. 未測試腳本相容性。
3. 未安排維護視窗與溝通。

**深層原因**：
- 架構層面：缺少標準作業程序。
- 技術層面：環境差異未梳理。
- 流程層面：變更管理不足。

### Solution Design
**解決策略**：建立 preflight checklist，涵蓋備份、視窗、資源、腳本預演、回復方案與責任分工。

**實施步驟**：
1. 清單制定
- 實作細節：列出 20+ 項標準檢核
- 所需資源：PM/SA/Dev 協作
- 預估時間：60 分鐘

2. 執行與簽核
- 實作細節：逐項核對、簽章
- 所需資源：變更單
- 預估時間：30 分鐘

**關鍵範例**：
- DB/檔案備份完成並驗證
- 維護頁與診斷模式預備
- staging 預演通過
- 回復腳本可用
- 權限與磁碟空間充足

實際案例：原文升級失敗且回退，若有清單可減少中斷。
實作環境：通用。
實測數據：
- 改善前：升級失敗率 20%+
- 改善後：<5%
- 改善幅度：下降 75%+

Learning Points
- SRE 思維導入
- SOP 與審核
- 風險前置

技能要求：
- 必備：變更管理基本功
- 進階：統籌與度量

延伸思考：
- 與工單系統整合
- 風險：流於形式
- 優化：以數據驅動清單優化

Practice Exercise
- 基礎：撰寫 15 項檢核清單（30 分鐘）
- 進階：導入簽核流程（2 小時）
- 專案：建立可重用 SOP（8 小時）

Assessment Criteria
- 功能（40%）：完整性與落地
- 品質（30%）：可操作性
- 效能（20%）：失敗率下降
- 創新（10%）：工具化程度

---

## Case #12: 建立與生產等同的 Staging 預演環境

### Problem Statement
**業務場景**：直接在生產升級，失敗風險極高。需先在 staging 完整跑一遍。
**技術挑戰**：環境等同性（IIS/OS/.NET/DB/資料）。
**影響範圍**：顯著降低在生產踩雷。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 無預演導致未知差異。
2. 資料不同引發隱藏 bug。
3. 設定不一致。

**深層原因**：
- 架構層面：缺 staging 架構與流程。
- 技術層面：無環境配置自動化。
- 流程層面：缺預演 gate。

### Solution Design
**解決策略**：搭建 staging，從生產還原資料（脫敏），IIS/.NET/SQL 同版，完整演練升級與測試腳本。

**實施步驟**：
1. 環境建置
- 實作細節：相同 OS/IIS/.NET/SQL
- 所需資源：VM/資源池
- 預估時間：0.5-1 天

2. 資料脫敏還原
- 實作細節：還原生產備份並脫敏
- 所需資源：DBA
- 預估時間：2-4 小時

3. 預演與測試
- 實作細節：完整跑升級與驗證
- 所需資源：測試清單/腳本
- 預估時間：0.5-1 天

**關鍵程式碼/設定**：
```sql
-- 還原驗證
RESTORE VERIFYONLY FROM DISK='D:\backups\CSDB_full.bak';
RESTORE DATABASE [CSDB_Staging] FROM DISK='D:\backups\CSDB_full.bak' WITH MOVE ...
-- 脫敏示例
UPDATE Users SET Email = CONCAT('user',UserID,'@example.test');
```

實際案例：若原文先在 staging 預演，生產失敗機率可大幅降低。
實作環境：VM/IIS/SQL。
實測數據：
- 改善前：生產直接升級失敗率 15-20%
- 改善後：<3%
- 改善幅度：下降 80%+

Learning Points
- 環境等同性
- 脫敏與資料治理
- 預演流程化

技能要求：
- 必備：IaaS/VM、DB 還原
- 進階：IaC、資料脫敏

延伸思考：
- 導入基礎設施即程式（IaC）
- 風險：成本與維護
- 優化：自動同步配置

Practice Exercise
- 基礎：建立同版 IIS/.NET（30 分鐘）
- 進階：還原並脫敏資料（2 小時）
- 專案：全量預演與報告（8 小時）

Assessment Criteria
- 功能（40%）：成功預演
- 品質（30%）：等同性程度
- 效能（20%）：流程時間
- 創新（10%）：自動化工具

---

## Case #13: 注入結構化日誌與健康監控，補強觀測性

### Problem Statement
**業務場景**：產品內建錯誤頁遮蔽細節，需持久化與可查詢之日誌與健康監控。
**技術挑戰**：在 .NET 2.0 時代使用健康監控/自訂 provider。
**影響範圍**：縮短偵錯到位時間。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 無持久化日誌。
2. 無健康監控規則。
3. 無集中化查詢。

**深層原因**：
- 架構層面：觀測性不足。
- 技術層面：未啟用 ASP.NET 健康監控。
- 流程層面：無事件告警。

### Solution Design
**解決策略**：啟用 ASP.NET 健康監控，事件落地到 EventLog/DB；補 Global.asax 結構化日誌；配合簡單告警。

**實施步驟**：
1. 健康監控配置
- 實作細節：錯誤事件→EventLog
- 所需資源：web.config 編輯
- 預估時間：20 分鐘

2. 結構化日誌
- 實作細節：JSON 行式落地到檔案
- 所需資源：檔案權限
- 預估時間：30 分鐘

3. 告警
- 實作細節：EventLog 觸發簡報或郵件
- 所需資源：郵件服務
- 預估時間：30 分鐘

**關鍵程式碼/設定**：
```xml
<system.web>
  <healthMonitoring enabled="true">
    <providers>
      <add name="EventLogProvider" type="System.Web.Management.EventLogWebEventProvider, System.Web, ..."/>
    </providers>
    <rules>
      <add name="All Errors" eventName="All Errors" provider="EventLogProvider" profile="Default" />
    </rules>
  </healthMonitoring>
</system.web>
```

```csharp
// Global.asax：簡單 JSON 行式日誌
void Application_Error(object sender, EventArgs e) {
  var ex = Server.GetLastError();
  var payload = new {
    at = DateTime.UtcNow,
    url = Request?.RawUrl,
    msg = ex.Message,
    stack = ex.ToString()
  };
  System.IO.File.AppendAllText(Server.MapPath("~/App_Data/err.jsonl"),
    System.Web.Script.Serialization.JavaScriptSerializer().Serialize(payload) + "\n");
}
```

實際案例：補上觀測性即可快速定位升級問題。
實作環境：ASP.NET 2.0。
實測數據：
- 改善前：定位需人工重現
- 改善後：一跳即得堆疊與上下文
- 改善幅度：MTTD 下降 70%+

Learning Points
- 健康監控與 provider
- 結構化日誌
- 告警路由

技能要求：
- 必備：web.config/Global.asax
- 進階：集中化日誌設計

延伸思考：
- 導入集中平台（ELK/Seq）
- 風險：I/O 開銷
- 優化：非同步寫入/批次

Practice Exercise
- 基礎：EventLog 寫入錯誤（30 分鐘）
- 進階：JSON 行式日誌與查詢（2 小時）
- 專案：小型集中化查詢頁（8 小時）

Assessment Criteria
- 功能（40%）：錯誤可追蹤
- 品質（30%）：結構化程度
- 效能（20%）：開銷可控
- 創新（10%）：告警與儀表

---

## Case #14: 升級路徑與版本驗證（選對腳本，順序正確）

### Problem Statement
**業務場景**：CS 2.0→2.1 有多條腳本與相依順序；若版本偵測錯誤或跳步執行，將導致不可用。
**技術挑戰**：辨識當前 DB/應用版本並選用正確腳本順序。
**影響範圍**：升級失敗、資料不一致。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 使用錯誤的 2.x→2.1 腳本。
2. 略過中間 schema 變更。
3. 多站點/多資料庫版本不一。

**深埋原因**：
- 架構層面：版本資訊散落。
- 技術層面：未建立標準版本查詢法。
- 流程層面：文件/步驟不清。

### Solution Design
**解決策略**：建立版本探測 SQL，確認當前版本；對照官方升級矩陣，生成「適用腳本序列」並記錄執行狀態。

**實施步驟**：
1. 版本探測
- 實作細節：掃描包含 Version/Schema 的表或擴充屬性
- 所需資源：DB 權限
- 預估時間：20 分鐘

2. 腳本序列生成
- 實作細節：以當前版本對映至需執行清單
- 所需資源：變更文件
- 預估時間：30 分鐘

3. 執行與標記
- 實作細節：每步完成寫入歷史
- 所需資源：DB 權限
- 預估時間：依腳本長度

**關鍵程式碼/設定**：
```sql
-- 探測版本資訊（通用策略）
SELECT TOP 10 name FROM sys.tables WHERE name LIKE '%Version%' OR name LIKE '%Schema%';
-- 若找到版本表：
SELECT * FROM dbo.CS_Version /* 假名，依實際表調整 */;
-- 找不到時可用擴充屬性：
SELECT * FROM fn_listextendedproperty(default, default, default, default, default, default, default);
```

實際案例：原文提及執行 2.x→2.1 腳本後失敗；需先確定腳本正確性與順序。
實作環境：SQL Server。
實測數據：
- 改善前：誤用腳本機率顯著
- 改善後：腳本誤用近零
- 改善幅度：升級成功率提升 30%+

Learning Points
- 版本探測技巧
- 腳本序列化
- 執行狀態記錄

技能要求：
- 必備：T-SQL
- 進階：版本矩陣管理

延伸思考：
- 自動版控（遷移工具）
- 風險：多資料庫不同步
- 優化：集中版本服務

Practice Exercise
- 基礎：寫出版本探測 SQL（30 分鐘）
- 進階：生成腳本序列（2 小時）
- 專案：小型遷移執行器（8 小時）

Assessment Criteria
- 功能（40%）：版本偵測準確
- 品質（30%）：記錄清晰
- 效能（20%）：步驟自動化
- 創新（10%）：序列生成器

---

## Case #15: 以 DebugDiag/WinDbg 擷取啟動期例外與傾印分析

### Problem Statement
**業務場景**：站台啟動即錯，連頁面都出不來；需在 w3wp 啟動期擷取第一時間例外或存取違例，取得根因。
**技術挑戰**：在 IIS 下掛勾進程並擷取 First-chance Exception/Dump。
**影響範圍**：關鍵排障能力，特別是「無頁可看」時。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 啟動期例外未落地。
2. 產品錯誤頁攔截，前端無堆疊。
3. 無進程級分析工具。

**深層原因**：
- 架構層面：缺少低階觀測。
- 技術層面：不熟悉 DebugDiag/WinDbg。
- 流程層面：無 dump 授權流程。

### Solution Design
**解決策略**：安裝 DebugDiag 2.x，建立「Crash/Exception」規則對準 w3wp，捕捉特定例外型態；或用 WinDbg 附加，設置 .loadby sos clr 與 !pe 分析堆疊。

**實施步驟**：
1. 安裝與規則設定
- 實作細節：DebugDiag 建立「Crash Rule」監看 w3wp，條件 First Chance
- 所需資源：伺服器安裝權限
- 預估時間：30 分鐘

2. 觸發並收集
- 實作細節：重現啟動錯誤，收集 dump
- 所需資源：維護視窗
- 預估時間：10-20 分鐘

3. 分析
- 實作細節：DebugDiag 解析報告；或 WinDbg + SOS 指令
- 所需資源：工具
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
- DebugDiag：GUI 設定 First-chance CLR Exception。
- WinDbg 常用：
```
.loadby sos mscorwks
!pe
!clrstack
!dumpexception
```

實際案例：原文站台啟動即錯且無細節，此法可直擊根因。
實作環境：Windows Server/IIS/.NET 2.0。
實測數據：
- 改善前：卡在黑箱，無堆疊
- 改善後：取得完整 CLR 堆疊與模組
- 改善幅度：定位效率+90%

Learning Points
- Dump 擷取時機
- SOS/CLR 診斷指令
- 例外路徑分析

技能要求：
- 必備：IIS/進程概念
- 進階：WinDbg/SOS

延伸思考：
- 自動策略：特定錯誤自動 dump
- 風險：dump 包含敏感資料
- 優化：脫敏處理與存放策略

Practice Exercise
- 基礎：用 DebugDiag 捕捉例外（30 分鐘）
- 進階：WinDbg 讀取並輸出堆疊（2 小時）
- 專案：建立標準 dump 流程與 SOP（8 小時）

Assessment Criteria
- 功能（40%）：成功擷取/分析
- 品質（30%）：報告清晰
- 效能（20%）：定位時間
- 創新（10%）：自動化觸發

---

## 案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 4（維護模式）
  - Case 6（目錄權限）
  - Case 7（清理暫存）
  - Case 11（Preflight 清單）

- 中級（需要一定基礎）
  - Case 1（詳細錯誤/旁路）
  - Case 2（回復機制）
  - Case 5（設定合併）
  - Case 9（IIS/.NET 映射）
  - Case 10（安全模式）
  - Case 13（健康監控）
  - Case 14（版本驗證）

- 高級（需要深厚經驗）
  - Case 3（交易化升級腳本）
  - Case 8（assemblyBinding）
  - Case 12（Staging 等同性）
  - Case 15（Dump 診斷）

2) 按技術領域分類
- 架構設計類
  - Case 2、11、12、14
- 效能優化類
  - Case 7、13（觀測效率提升屬運維效能）
- 整合開發類
  - Case 5、8、9、10
- 除錯診斷類
  - Case 1、3、6、7、13、15
- 安全防護類
  - Case 4、6（權限最小化亦涉安全）

3) 按學習目標分類
- 概念理解型
  - Case 4、11、12
- 技能練習型
  - Case 6、7、9、13
- 問題解決型
  - Case 1、2、3、5、8、10、14、15
- 創新應用型
  - Case 2（原子切換）、12（IaC）、13（結構化日誌）、15（自動 dump 策略）

---

## 案例關聯圖（學習路徑建議）
- 入門起點（環境安全與基本操作）：
  1) Case 4（維護模式）→ 2) Case 6（權限）→ 3) Case 7（清暫存）→ 4) Case 11（Preflight）

- 基礎診斷與設定：
  5) Case 1（關閉遮蔽、開啟詳細錯誤）→ 6) Case 13（健康監控/日誌）→ 7) Case 9（IIS/.NET 映射）

- 升級正確性與相依治理：
  8) Case 14（版本驗證/腳本順序）→ 9) Case 3（交易化升級腳本）→ 10) Case 5（config 合併）→ 11) Case 8（assemblyBinding）

- 風險控制與回復能力：
  12) Case 2（回復/原子切換）與 13) Case 10（安全模式）並行練習 → 14) Case 12（Staging 等同性）

- 深度故障排除：
  15) Case 15（Dump/進程級診斷），依賴前述觀測與環境知識

完整學習路徑建議：
- 先掌握維護/權限/暫存/清單（Case 4,6,7,11）
- 再學會顯示錯誤與日誌（Case 1,13）與 IIS 映射（Case 9）
- 接著攻克版本與 DB 升級（Case 14,3）與設定/相依（Case 5,8）
- 進一步建立回復與安全模式（Case 2,10）並搭建 staging 預演（Case 12）
- 最後進入進程級診斷（Case 15）

以上 15 個案例，均以原文「升級 CS 2.0→2.1 失敗、錯誤被遮蔽、回退至影子拷貝」為核心情境展開，適合用於實戰教學、專案練習與能力評估。實測數據部分為可替換之示例口徑，建議在各自環境中落地量測並更新。