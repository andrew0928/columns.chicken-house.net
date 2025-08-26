## Case #1: 用虛擬化隔離家庭伺服器角色與 Media Center

### Problem Statement（問題陳述）
業務場景：家用 PC 原本跑 Windows Server 2003 x64，僅承載 RRAS、IIS、SQL Express、DNS、DHCP、SMTP 與檔案服務，日常負載不到 5%。規劃改為桌機並加上 Vista Ultimate 的 Media Center（MCE）播放/錄影與一般桌面用途，同時保留既有網路服務不中斷。
技術挑戰：伺服器角色與 MCE 在相同 OS 上有相容性與體驗衝突（媒體與互動需求 VS 伺服器硬化與背景服務），亦可能發生埠衝突、權限與休眠策略不一致。
影響範圍：服務可用性、家庭網路核心服務（DNS/DHCP/RRAS）、影音體驗、工作站日常使用。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 伺服器角色與 MCE 的互斥需求（互動 UI/休眠 vs 常駐服務）造成體驗與穩定性衝突
2. 伺服器服務與桌面應用可能發生埠與檔案鎖定衝突（如 IIS、SMTP 與其他程式）
3. 安全性與硬化策略不同（伺服器嚴格防火牆/原則 vs MCE 上網與外掛）
深層原因：
- 架構層面：單機多角色耦合，缺少邏輯隔離
- 技術層面：OS 功能定位不同（Server vs Desktop/MCE）
- 流程層面：缺乏逐步遷移與回滾驗證流程

### Solution Design（解決方案設計）
解決策略：以虛擬化解耦，將所有網路服務遷至 Virtual PC 來賓 OS（Windows Server 2003），Host 改裝 Vista Ultimate 承載 MCE、檔案服務、備份與桌面工作。來賓使用橋接網路，確保 DNS/DHCP/RRAS 對整個 LAN 提供服務；Host 專注互動與多媒體，互不干擾。

實施步驟：
1. 規劃與盤點
- 實作細節：盤點所有服務（RRAS、DNS、DHCP、IIS、SMTP、SQL Express）與資料、埠、憑證
- 所需資源：服務清單模板、埠映射表
- 預估時間：0.5 天

2. 建置來賓 OS
- 實作細節：在 Virtual PC 建立 Win2003 VM，RAM 256–512MB，網卡設為橋接
- 所需資源：Virtual PC 2007、Windows Server 2003 安裝媒體
- 預估時間：0.5 天

3. 遷移服務
- 實作細節：依序遷移 DNS/DHCP（Case 8）、IIS/SMTP（Case 7）、SQL Express（Case 9）
- 所需資源：遷移腳本、備份工具
- 預估時間：1–2 天

4. Host 安裝與優化
- 實作細節：安裝 Vista Ultimate、啟用 MCE、配置檔案分享與備份（Case 4/5）
- 所需資源：Vista 安裝媒體、驅動程式
- 預估時間：0.5–1 天

5. 啟動自動化與監控
- 實作細節：設定 VM 開機自動啟動、關機順序（Case 12），佈建效能監控（Case 13）
- 所需資源：工作排程器、PerfMon
- 預估時間：0.5 天

關鍵程式碼/設定：
```cmd
:: 啟動時自動開 VM（以 VMC 檔為例）
schtasks /create /tn "Start-Services-VM" /sc ONSTART ^
/tr "\"C:\VMs\Services.vmc\"" /ru "SYSTEM" /rl HIGHEST

:: Host 設定不要自動睡眠避免中斷 VM（Vista 可用 powercfg）
powercfg -change -standby-timeout-ac 0
```

實際案例：作者將 RRAS、IIS、SQL Express、DNS、DHCP、SMTP 全部搬到 VPC 來賓；Host 裝 Vista Ultimate 承載 MCE、檔案、備份與桌面應用，家用功能與服務並存。
實作環境：E6300 + 3GB RAM；Virtual PC 2007；來賓 Windows Server 2003；Host Vista Ultimate。
實測數據：
改善前：主機僅伺服器用途，CPU loading < 5%，資源閒置
改善後：一機多用，VM 256→512MB，主觀體感無明顯變慢
改善幅度：功能覆蓋 +4 項（MCE/桌面/備份/轉檔），資源利用度顯著提升（定性）

Learning Points（學習要點）
核心知識點：
- 以虛擬化解耦衝突角色的架構思維
- 桥接網路確保基礎網路服務可對外提供
- 主機互動負載與來賓後台服務的職責分離

技能要求：
- 必備技能：Windows 伺服器角色基本操作、虛擬機安裝、基礎網路
- 進階技能：服務遷移腳本化、效能監控與容量規劃

延伸思考：
- 可替換更現代的虛擬化平台（支援 SMP）
- VM 服務單點故障如何高可用？
- Host/Guest 的安全邊界與更新策略

Practice Exercise（練習題）
- 基礎練習：在本機建立一台 Win2003 VM 並設定橋接（30 分鐘）
- 進階練習：將簡單 HTTP 服務遷移至 VM 並對 LAN 提供服務（2 小時）
- 專案練習：完成 RRAS/DNS/DHCP/IIS/SQL Express 全量遷移與驗收（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：服務可用、啟停自動化、MCE 正常
- 程式碼品質（30%）：腳本可讀、可重複執行、錯誤處理
- 效能優化（20%）：Host/Guest 資源分配合理，無明顯卡頓
- 創新性（10%）：補充監控告警、文件化與回滾方案


## Case #2: 應對 Virtual PC 不支援 SMP 的 CPU 受限

### Problem Statement（問題陳述）
業務場景：來賓 VM 承載基礎網路服務，Virtual PC 不支援 SMP，導致 VM 僅能用單核心。需確保 RRAS/DNS/DHCP/IIS/SMTP/SQL Express 穩定，並讓 CPU 密集型的視訊轉檔留在 Host。
技術挑戰：單核心 VM 可能成為瓶頸；需控制 CPU 密集工作不佔用 VM；並維持 Host 的互動流暢性。
影響範圍：服務響應時間、影音播放順暢度、整機體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Virtual PC 平台不支援 SMP，VM 僅單核心
2. 視訊轉檔等工作 CPU 密集，若在 VM 執行會拖慢服務
3. 未控管 Host/Guest 的程序優先序與親和性
深層原因：
- 架構層面：工作負載定位不明（CPU 密集 vs I/O 密集）
- 技術層面：虛擬化平台功能限制
- 流程層面：缺乏執行層級的資源控制策略

### Solution Design（解決方案設計）
解決策略：將所有 CPU 密集型工作保留在 Host，設定程序優先序/親和性降低對互動的影響；VM 僅承載 I/O 輕量的網路服務；如果 VM 偶有尖峰，則調整服務執行排程與快取參數。

實施步驟：
1. 負載分類
- 實作細節：標記 CPU 密集（轉檔）與 I/O/記憶體輕量（DNS/DHCP）
- 所需資源：PerfMon/Task Manager
- 預估時間：1 小時

2. Host 程序優先序/親和性
- 實作細節：對轉檔等工作設 /low 與指定位元組集
- 所需資源：cmd/PowerShell
- 預估時間：0.5 小時

3. VM 服務優化
- 實作細節：調整 IIS app pool、SQL Express 最大記憶體等
- 所需資源：IIS 管理工具、SQLCMD
- 預估時間：1 小時

關鍵程式碼/設定：
```cmd
:: 在 Host 以低優先序與限定核心執行轉檔
start "" /low /affinity 3 "C:\Tools\ffmpeg\bin\ffmpeg.exe" -i input.ts -c:v libx264 -preset slow -crf 22 -c:a aac out.mp4
```

實際案例：作者在 VM 僅配 256→512MB RAM 且單核運行，網路服務仍無體感變慢；轉檔等重負載留在 Host。
實作環境：E6300 雙核；Virtual PC 2007；Host Vista；Guest Win2003。
實測數據：
改善前：VM 有機會被重負載影響
改善後：重負載留 Host，VM 僅承載輕量服務
改善幅度：干擾事件降至可接受（定性）

Learning Points
核心知識點：
- 工作負載分類與資源隔離
- 程序優先序/親和性對互動體驗的影響
- 虛擬化平台能力對架構選擇的限制

技能要求：
- 必備技能：Windows 程序管理、PerfMon
- 進階技能：IIS/SQL 資源限額調整

延伸思考：
- 何時應更換支援 SMP 的虛擬化平台？
- 是否需為 VM 加入資源限制與告警？

Practice Exercise
- 基礎：以 /low 啟動 CPU 密集程序並觀察互動性（30 分鐘）
- 進階：為 SQL Express 設定 Max Server Memory 並驗證（2 小時）
- 專案：制定 Host/VM 程序優先序與親和性策略文檔（8 小時）

Assessment Criteria
- 功能完整性：負載分類清晰、策略落地
- 程式碼品質：啟動腳本穩定、可重用
- 效能優化：互動體驗穩定，VM 無尖峰
- 創新性：自動化監控告警


## Case #3: 低負載主機的資源重分配與 VM 記憶體調參

### Problem Statement（問題陳述）
業務場景：原主機負載 <5%，遷移後需在 Host 跑 MCE/桌面/備份/轉檔，VM 跑網路服務。需在記憶體 3GB 下合理分配以獲得順暢體驗與穩定服務。
技術挑戰：VM 記憶體過低影響服務，過高又會壓榨 Host；需以數據驅動調參。
影響範圍：VM 服務穩定性、Host 音影片播放與多工體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. VM 初始 256MB 可能不足以承載 IIS/SQL/DNS/DHCP
2. Host MCE 與桌面應用需要足量可用記憶體
3. 無監測依據下難以精準配置
深層原因：
- 架構層面：單機競用有限實體記憶體
- 技術層面：工作集、分頁、快取策略互相影響
- 流程層面：缺少基準測試與滾動調參機制

### Solution Design（解決方案設計）
解決策略：建立基準監控（CPU/記憶體/分頁/磁碟佔用），先給 VM 256MB，觀察工作集與分頁；必要時升至 512MB。對 Host 使用者工作高峰時段與 VM 服務尖峰時段錯開。

實施步驟：
1. 建置監控
- 實作細節：用 logman 建立計數器收集（每 60 秒）
- 所需資源：PerfMon/Logman
- 預估時間：0.5 小時

2. 初始配置與試運行
- 實作細節：VM 256MB 連續跑 24 小時，觀察分頁/Queue 長度
- 所需資源：Virtual PC、事件檢視器
- 預估時間：1 天

3. 調參與驗收
- 實作細節：必要時調至 512MB，再測 24 小時
- 所需資源：同上
- 預估時間：1 天

關鍵程式碼/設定：
```cmd
:: 建立效能收集組
logman create counter VMHostPerf -f bincirc -max 200 -si 00:01:00 ^
-c "\Processor(_Total)\% Processor Time" ^
-c "\Memory\Available MBytes" ^
-c "\Process(vpc)\Working Set" ^
-c "\Paging File(_Total)\% Usage" ^
-o "C:\perf\vmhostperf"

logman start VMHostPerf
```

實際案例：作者由 256MB 起步，後續提升至 512MB，仍無明顯變慢。
實作環境：E6300 + 3GB；Virtual PC 2007；Vista Host。
實測數據：
改善前：無監控，資源配置憑感覺
改善後：以監測結果調整至 512MB，Host/VM 體感穩定
改善幅度：資源配置決策效率顯著提升（定性）

Learning Points
- 以數據驅動記憶體調參
- 工作集/分頁/可用記憶體的關係
- 短期基準測試與滾動驗證

Practice Exercise
- 基礎：建立 logman 收集組並匯出 CSV（30 分鐘）
- 進階：分析 24 小時資料並提出建議（2 小時）
- 專案：制定 Host/VM 調參 Runbook（8 小時）

Assessment Criteria
- 功能完整性：監測項齊全、資料可用
- 程式碼品質：腳本健壯、可重跑
- 效能優化：調參合理、體感改善
- 創新性：可視化報表、告警閾值


## Case #4: 家用檔案伺服器的 RAID-1 與 VSS 快照保護

### Problem Statement（問題陳述）
業務場景：需長期保存照片、DV 影片與個人檔案。採用 Windows 內建軟體 RAID-1 與卷陰影複製（VSS）保護，確保磁碟故障/誤刪能快速恢復。
技術挑戰：正確建立軟體鏡像、配置 VSS 空間與排程，避免影響 MCE 與日常使用的 I/O。
影響範圍：資料可用性、備份窗口、磁碟空間占用。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 單碟故障風險高，需冗餘
2. 誤刪或覆寫需時間點還原
3. 未規劃 VSS 空間易導致快照失敗
深層原因：
- 架構層面：缺少獨立備援盤或外部備份
- 技術層面：軟 RAID 與 VSS 空間管理
- 流程層面：快照與備份排程未協調

### Solution Design
解決策略：以軟體 RAID-1 提供即時硬體故障冗餘，VSS 提供細顆粒度版本點；規劃獨立資料分割區承載媒體與個資，為 VSS 配置 10–20% 快照空間，並與備份排程錯開。

實施步驟：
1. 建立軟體鏡像
- 實作細節：磁碟管理將兩顆磁碟轉動態磁碟並鏡像
- 所需資源：磁碟管理 MMC
- 預估時間：0.5 小時

2. VSS 空間與排程
- 實作細節：設定影子儲存上限，排程每日快照
- 所需資源：vssadmin、wmic
- 預估時間：0.5 小時

3. 還原演練
- 實作細節：從 VSS 取回檔案、模擬單碟故障拆除/重建
- 所需資源：檔總管、事件檢視器
- 預估時間：1 小時

關鍵程式碼/設定：
```cmd
:: 設定 VSS 影子儲存（為 D: 配置 15%）
vssadmin resize shadowstorage /for=D: /on=D: /maxsize=15%

:: 建立一次快照（WMIC）
wmic shadowcopy call Create Volume='D:\'

:: 列出快照
vssadmin list shadows
```

實際案例：作者沿用軟 RAID-1 + VSS 保護家用資料。
實作環境：Vista Host；兩顆數據盤。
實測數據：
改善前：單點故障風險、無版本快照
改善後：單碟容錯、可回溯版本
改善幅度：RPO/RTO 顯著改善（定性）

Learning Points
- 軟 RAID-1 原理與適用性
- VSS 快照空間與保留策略
- 還原演練的重要性

Practice Exercise
- 基礎：建立與列出一次 VSS 快照（30 分鐘）
- 進階：設計每日/每週快照策略並測試還原（2 小時）
- 專案：完成 RAID-1 建置與 VSS 策略文檔（8 小時）

Assessment Criteria
- 功能完整性：鏡像/快照可用、還原成功
- 程式碼品質：設定腳本化、可復現
- 效能優化：I/O 影響可接受
- 創新性：加上自動清理/告警


## Case #5: 每週自動備份流程設計（VSS + Robocopy）

### Problem Statement（問題陳述）
業務場景：需每週自動備份重要檔案，避免與 MCE 錄影與桌面使用衝突，確保可回復且可審核。
技術挑戰：一致性快照、權限與時間戳保留、斷點續傳、排程與日誌。
影響範圍：備份成功率、恢復時間、磁碟空間。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 線上檔案開啟導致不一致
2. 權限/ACL 未保留造成還原失敗
3. 缺乏排程與重試機制
深層原因：
- 架構層面：無專用備份盤/路徑
- 技術層面：未運用 VSS 影像與 Robocopy 參數
- 流程層面：缺少日誌與驗證

### Solution Design
解決策略：透過 VSS 建立一致性影像，使用 Robocopy /MIR /COPY:DATSOU 複製到備份目錄；以工作排程器每週夜間執行，產生日誌並郵件通知（可選）。

實施步驟：
1. 準備備份腳本
- 實作細節：建立快照→從快照路徑複製→清理舊版本
- 所需資源：robocopy、wmic、PowerShell（可選）
- 預估時間：1 小時

2. 設定排程與權限
- 實作細節：SYSTEM 帳戶執行、每週夜間
- 所需資源：schtasks
- 預估時間：0.5 小時

3. 還原驗證
- 實作細節：抽樣檔案還原與 ACL 校驗
- 所需資源：icacls
- 預估時間：0.5 小時

關鍵程式碼/設定：
```cmd
:: backup.cmd（簡化示例）
@echo off
set SRC=D:
set DEST=E:\Backups\D
for /f "tokens=2 delims==; " %%i in ('wmic shadowcopy call create Volume^="%SRC%\" ^| find "ID"') do set SHADOWID=%%i
for /f "tokens=2 delims==" %%p in ('wmic shadowcopy where "ID=%SHADOWID%" get DeviceObject /value ^| find "="') do set DEV=%%p
robocopy "%DEV%\" "%DEST%" /MIR /R:2 /W:5 /COPY:DATSOU /DCOPY:T /XJ /TEE /LOG+:E:\Backups\logs\backup.log
wmic shadowcopy where "ID=%SHADOWID%" delete
```
```cmd
:: 每週排程
schtasks /create /tn "Weekly-Backup" /sc WEEKLY /d SUN /st 02:00 ^
/tr "C:\Scripts\backup.cmd" /ru "SYSTEM" /rl HIGHEST
```

實際案例：作者規劃 weekly backup 作為 batch job。
實作環境：Vista Host；備份到本機或外接碟。
實測數據：
改善前：手動備份，易遺漏
改善後：每週自動且留存日誌
改善幅度：人為疏漏降至最低（定性）

Learning Points
- 以 VSS + Robocopy 實現一致性備份
- ACL/時間戳的保留
- 排程與日誌化

Practice Exercise
- 基礎：運行腳本備份一個資料夾（30 分鐘）
- 進階：加入郵件通知與錯誤重試（2 小時）
- 專案：備份與還原演練手冊（8 小時）

Assessment Criteria
- 功能完整性：備份/還原成功、日誌齊全
- 程式碼品質：健壯、可維護
- 效能優化：窗口選擇合理
- 創新性：通知與報表


## Case #6: 視訊轉檔工作離峰排程與低優先順序執行

### Problem Statement（問題陳述）
業務場景：需定期將錄影內容轉檔，避免影響 MCE 播放與日常操作；轉檔 CPU 密集，應在離峰進行並降低對互動影響。
技術挑戰：CPU/磁碟佔用高；需限制優先序與時間窗口。
影響範圍：系統流暢度、影片產出 SLA。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 轉檔工作長時間佔用 CPU
2. 與 MCE/桌面互動衝突
3. 無排程/節流
深層原因：
- 架構層面：與互動工作無隔離
- 技術層面：缺省優先序/親和性配置
- 流程層面：無離峰策略

### Solution Design
解決策略：透過工作排程於夜間啟動轉檔，使用 /low 與 /affinity 限制資源；可加上 I/O 節流工具或拆分批次以縮短佔用時間。

實施步驟：
1. 轉檔腳本
- 實作細節：批次掃描資料夾、對新檔轉檔
- 所需資源：ffmpeg
- 預估時間：1 小時

2. 排程與優先序
- 實作細節：夜間執行、/low /affinity
- 所需資源：schtasks
- 預估時間：0.5 小時

3. 成果校驗
- 實作細節：轉檔日誌、錯誤重試
- 所需資源：logrotate（可選）
- 預估時間：0.5 小時

關鍵程式碼/設定：
```cmd
:: transcode.cmd
for %%f in ("D:\Recordings\*.ts") do (
  if not exist "D:\Encoded\%%~nf.mp4" (
    start "" /low /affinity 3 "C:\Tools\ffmpeg\bin\ffmpeg.exe" -i "%%f" -c:v libx264 -preset slow -crf 22 -c:a aac "D:\Encoded\%%~nf.mp4"
  )
)

:: 每日 01:00 執行
schtasks /create /tn "Nightly-Transcode" /sc DAILY /st 01:00 ^
/tr "C:\Scripts\transcode.cmd" /ru "SYSTEM"
```

實際案例：作者將 video encoding 歸類為 batch job，於離峰執行。
實作環境：Vista Host；ffmpeg。
實測數據：
改善前：轉檔期間影響互動
改善後：離峰低優先序執行
改善幅度：互動受影響時段壓縮至夜間窗口（定性）

Learning Points
- CPU 密集工作對系統的影響與緩解
- 排程與低優先序的實務
- 產出校驗與重試

Practice Exercise
- 基礎：轉檔單一檔案並觀察 CPU（30 分鐘）
- 進階：批次轉檔並記錄日誌（2 小時）
- 專案：完整排程/回報/重試系統（8 小時）

Assessment Criteria
- 功能完整性：轉檔正確、重試可用
- 程式碼品質：清晰、健壯
- 效能優化：對互動影響最小
- 創新性：節流/並行度控制


## Case #7: 將 IIS/SMTP 從主機遷移至來賓系統

### Problem Statement（問題陳述）
業務場景：需將 IIS 網站與 IIS 6 SMTP 從原主機遷移到 VM，確保站台設定、憑證、虛擬目錄與郵件轉送一致。
技術挑戰：IIS 設定匯出/匯入、SMTP 與防火牆、TLS/憑證搬遷。
影響範圍：網站可用性、郵件轉送可靠性。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 主機改裝為 Vista，需卸載伺服器角色
2. 手動重建易遺漏設定
3. 郵件與網站中斷風險
深層原因：
- 架構層面：設定/內容耦合
- 技術層面：IIS/SMTP 匯入匯出流程不熟
- 流程層面：缺少切換/回退計畫

### Solution Design
解決策略：使用 iiscnfg.vbs 匯出/匯入 IIS 6 設定，先於測試埠驗證；SMTP 參數比對，完成後 DNS 切換；保留回退備份。

實施步驟：
1. 匯出 IIS 設定
- 實作細節：iiscnfg.vbs 匯出 metabase
- 所需資源：IIS 6 AdminScripts
- 預估時間：0.5 小時

2. 匯入與驗證
- 實作細節：在 VM 匯入、測試站台
- 所需資源：Host 檔案、測試用 hosts
- 預估時間：1 小時

3. SMTP 設定與測試
- 實作細節：對接中繼/信箱，測通
- 所需資源：SMTP MMC
- 預估時間：0.5 小時

4. 切換與回退
- 實作細節：DNS/防火牆/埠轉發切換，保留回退
- 所需資源：DNS 管理、路由器
- 預估時間：0.5 小時

關鍵程式碼/設定：
```cmd
:: 匯出 IIS 6 設定
cscript "%systemdrive%\Inetpub\AdminScripts\iiscnfg.vbs" /export /f C:\backup\iis6.xml /inherited /children /sp /LM/W3SVC

:: 在 VM 匯入
cscript "%systemdrive%\Inetpub\AdminScripts\iiscnfg.vbs" /import /f C:\backup\iis6.xml /inherited /sp /LM/W3SVC

:: 檢查 SMTP 服務
sc query smtpsvc
```

實際案例：作者把 IIS/SMTP 遷至 VM，Host 專注 MCE。
實作環境：Win2003 VM（IIS 6）、Vista Host。
實測數據：
改善前：主機承載站台與 SMTP
改善後：VM 承載，Host 乾淨
改善幅度：角色隔離度提升（定性）

Learning Points
- IIS 6 設定移轉方法
- SMTP 測試與切換
- 回退策略

Practice Exercise
- 基礎：匯出/匯入單一站台（30 分鐘）
- 進階：完成 SMTP 測通與 DNS 切換（2 小時）
- 專案：撰寫完整移轉 Runbook（8 小時）

Assessment Criteria
- 功能完整性：站台/SMTP 可用
- 程式碼品質：腳本化、可追蹤
- 效能優化：切換無明顯中斷
- 創新性：自動健康檢查


## Case #8: DNS/DHCP 遷移與 VPC 橋接網路配置

### Problem Statement（問題陳述）
業務場景：家中 LAN 需由 VM 提供 DHCP 租約與 DNS 解析。Virtual PC 必須讓 VM 以橋接連到實體網路，確保廣播封包傳遞。
技術挑戰：DHCP 廣播需可達；DNS 區域/轉送設定移轉；避免雙 DHCP 衝突。
影響範圍：全網裝置上網、名稱解析、家庭網路穩定性。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. VM 若用 NAT/Host-only，DHCP 廣播無法對外
2. DNS 區域資料需正確遷移
3. 舊 DHCP 未停用會產生雙服務衝突
深層原因：
- 架構層面：網路拓樸未對齊服務需求
- 技術層面：廣播/多播在虛擬網路的限制
- 流程層面：切換窗口與驗收缺失

### Solution Design
解決策略：將 VM 網卡設為橋接至實體 NIC；先在隔離網段測試 DHCP；以 netsh 匯出/匯入 DHCP，dnscmd 匯移 DNS；切換時停用舊 DHCP，核對租約與解析。

實施步驟：
1. 設定橋接
- 實作細節：VPC VM 網卡連到實體 NIC（非 NAT）
- 所需資源：Virtual PC 設定
- 預估時間：0.25 小時

2. DHCP 移轉
- 實作細節：netsh 匯出/匯入，全域選項核對
- 所需資源：netsh
- 預估時間：0.5 小時

3. DNS 移轉
- 實作細節：dnscmd 區域匯出/新增/轉送器設定
- 所需資源：dnscmd
- 預估時間：0.5 小時

4. 切換與驗收
- 實作細節：停舊 DHCP、釋放/更新客戶端租約、解析測試
- 所需資源：ipconfig、nslookup
- 預估時間：0.5 小時

關鍵程式碼/設定：
```cmd
:: DHCP 匯出（舊主機）
netsh dhcp server export C:\backup\dhcp.txt all

:: DHCP 匯入（VM）
netsh dhcp server import C:\backup\dhcp.txt all

:: DNS 區域匯出（舊主機）
dnscmd /ZoneExport home.lan home.lan.dns

:: 在 VM 建立主區並引用檔案
dnscmd /ZoneAdd home.lan /Primary /file home.lan.dns

:: 設定 DNS 轉送器（至 ISP DNS）
dnscmd /ResetForwarders 8.8.8.8 1.1.1.1
```

實際案例：作者將 DNS/DHCP 遷到 VM 並持續服務全家網路。
實作環境：Win2003 VM；Virtual PC 橋接。
實測數據：
改善前：服務在 Host
改善後：VM 提供 DHCP/DNS，租約與解析正常
改善幅度：網路服務隔離度提升（定性）

Learning Points
- DHCP 廣播在虛擬網路的要求
- netsh/dnscmd 的移轉技巧
- 切換窗口與雙服務風險

Practice Exercise
- 基礎：建立測試作用域並成功租約（30 分鐘）
- 進階：完成 DNS 區域移轉與轉送器設定（2 小時）
- 專案：完成 DHCP/DNS 切換與驗收清單（8 小時）

Assessment Criteria
- 功能完整性：租約/解析成功
- 程式碼品質：腳本正確、可重跑
- 效能優化：切換無中斷
- 創新性：自動健康檢測腳本


## Case #9: SQL Express 資料庫遷移到 VM 並維持連線

### Problem Statement（問題陳述）
業務場景：原本在主機上的 SQL Express 需遷至 VM，確保資料完整、登入/權限與應用連線字串更新。
技術挑戰：選擇備份/還原或分離/附加；服務中斷窗口最小化。
影響範圍：依賴資料庫的網站/服務。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. Host 改裝，需搬遷資料庫
2. 權限/登入同步問題
3. 應用未更新連線字串
深層原因：
- 架構層面：應用/DB 耦合，缺少配置集中
- 技術層面：遷移手法選擇
- 流程層面：停機/驗收規劃不足

### Solution Design
解決策略：以 BACKUP/RESTORE 遷移，確保登入轉移；或 detach/attach 停機時間更短。完成後更新連線字串至 VM 名稱或固定 IP。

實施步驟：
1. 備份與搬遷
- 實作細節：使用 BACKUP DATABASE 並複製 .bak
- 所需資源：sqlcmd
- 預估時間：0.5–1 小時

2. 還原與登入同步
- 實作細節：RESTORE 後校驗登入與權限
- 所需資源：SQL Server Management Studio Express
- 預估時間：0.5 小時

3. 應用連線更新
- 實作細節：更新連線字串，測試連線
- 所需資源：配置檔
- 預估時間：0.5 小時

關鍵程式碼/設定：
```sql
-- 舊主機備份
BACKUP DATABASE MyDB TO DISK='C:\backup\MyDB.bak' WITH INIT, COPY_ONLY;
GO
```
```cmd
:: VM 上還原
sqlcmd -S .\SQLEXPRESS -Q "RESTORE DATABASE MyDB FROM DISK='C:\backup\MyDB.bak' WITH REPLACE;"
```
```ini
; 連線字串示例（更新為 VM 名稱或 IP）
Server=VM-SQL\SQLEXPRESS;Database=MyDB;Trusted_Connection=True;
```

實際案例：作者將 SQL Express 與其他服務一併搬到 VM。
實作環境：SQL Express 2005；Win2003 VM。
實測數據：
改善前：DB 在 Host
改善後：DB 在 VM，應用正常連線
改善幅度：服務隔離度提升（定性）

Learning Points
- SQL Express 遷移手法
- 登入/權限同步
- 連線字串管理

Practice Exercise
- 基礎：備份/還原單一資料庫（30 分鐘）
- 進階：模擬 detach/attach 並縮短停機（2 小時）
- 專案：多應用連線切換腳本（8 小時）

Assessment Criteria
- 功能完整性：資料完整、連線正常
- 程式碼品質：腳本可復用、日誌化
- 效能優化：停機窗口最小
- 創新性：配置集中化


## Case #10: 在 VPC 中先行驗證 Vista（32/64 位）相容性

### Problem Statement（問題陳述）
業務場景：Vista 僅將在 Host 上使用，作者先把 Vista 裝進 VM 測試操作與應用兼容，降低正式換裝風險。
技術挑戰：VM 難以測試實體驅動，但可測 UI/應用/策略；需清楚邊界。
影響範圍：換裝成功率、回退成本。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 直接換裝風險高
2. 驅動與應用兼容不明
3. 缺乏回退策略
深層原因：
- 架構層面：測試環境與生產無隔離
- 技術層面：VM 驗證能力有限
- 流程層面：缺少預先驗證

### Solution Design
解決策略：在 VM 先裝 Vista 32/64 位，測試核心應用、策略、MCE 基本流程（除實體驅動）；使用 Undo Disks/快照手段反覆試驗；彙整風險清單。

實施步驟：
1. 建置測試 VM
- 實作細節：建立兩台 VM（x86/x64）
- 所需資源：Vista 安裝媒體
- 預估時間：1 小時

2. 測試用例
- 實作細節：安裝應用、瀏覽器/多媒體、策略
- 所需資源：軟體清單
- 預估時間：2–4 小時

3. 風險評估
- 實作細節：整理不相容清單與替代方案
- 所需資源：測試報告模板
- 預估時間：1 小時

關鍵程式碼/設定：
```cmd
:: 匯出已安裝驅動清單（用於日後比對）
driverquery /v /fo csv > C:\temp\drivers.csv
```

實際案例：作者先灌到 VPC 裡玩再決定正式換裝。
實作環境：Virtual PC 2007；Vista Ultimate x86/x64。
實測數據：
改善前：未知相容性風險
改善後：完成應用流程驗證
改善幅度：換裝風險顯著降低（定性）

Learning Points
- 在 VM 做應用/流程驗證
- VM 驗證的邊界（實體驅動除外）
- 測試報告與風險清單

Practice Exercise
- 基礎：安裝 Vista VM 並跑基準流程（30 分鐘）
- 進階：編寫相容性測試清單與結果（2 小時）
- 專案：換裝決策評估報告（8 小時）

Assessment Criteria
- 功能完整性：關鍵應用覆蓋
- 程式碼品質：測試記錄清晰
- 效能優化：測試步驟高效
- 創新性：風險矩陣設計


## Case #11: Vista 32/64 位選型評估與驅動相容測試

### Problem Statement（問題陳述）
業務場景：Vista 盒裝附 32/64 位，需評估驅動與應用相容、MCE 外掛與硬體解碼卡支援，決定安裝版本。
技術挑戰：64 位驅動供應狀況參差；部分軟體外掛僅支援 32 位。
影響範圍：影音體驗、周邊硬體可用性。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 硬體廠商 64 位驅動覆蓋不足（年代因素）
2. MCE 相關外掛/濾鏡相容性不一
3. 使用者場景偏多媒體，容錯率低
深層原因：
- 架構層面：驅動與核心版本密切耦合
- 技術層面：32/64 位混用限制
- 流程層面：缺少系統性驗證

### Solution Design
解決策略：列出所有周邊與外掛清單，分別蒐集 32/64 位驅動與支援聲明；在 VM 驗證應用面，在實機以 WinPE/備援系統進一步測實體驅動；綜合後選擇相容性最佳的版本。

實施步驟：
1. 清單與資料收集
- 實作細節：硬體/外掛清單、官網驅動
- 所需資源：廠商頁面
- 預估時間：1–2 小時

2. 應用面測試
- 實作細節：VM 上安裝並驗證關鍵應用
- 所需資源：Case 10 VM
- 預估時間：2 小時

3. 驅動面測試（實機）
- 實作細節：以映像備援後在實機測試驅動
- 所需資源：映像工具（ImageX/Clonezilla）
- 預估時間：2–4 小時

關鍵程式碼/設定：
```cmd
:: 列出即插即用裝置與硬體ID
wmic path Win32_PnPEntity get Name,HardwareID /format:htable > C:\temp\hw.htm
```

實際案例：作者提到 32/64 位皆可用，計畫先在 VPC 測過再定。
實作環境：Vista Ultimate；E6300 + 3GB。
實測數據：
改善前：選型不確定
改善後：基於清單與測試決策
改善幅度：決策確定性提升（定性）

Learning Points
- 選型決策方法
- 驅動/外掛驗證策略
- 實機與 VM 的測試互補

Practice Exercise
- 基礎：產出硬體/外掛清單（30 分鐘）
- 進階：完成 32/64 位應用對比表（2 小時）
- 專案：選型決策報告（8 小時）

Assessment Criteria
- 功能完整性：清單/對比完整
- 程式碼品質：記錄與引用規範
- 效能優化：測試效率
- 創新性：決策矩陣


## Case #12: VPC 服務自動化啟動與關機順序設計

### Problem Statement（問題陳述）
業務場景：Host 重開機或斷電後，VM 需自動啟動以恢復網路服務；關機時避免暴力中止導致資料不一致。
技術挑戰：Virtual PC 自動啟動、保存狀態、關機順序協調。
影響範圍：服務可用性、資料一致性。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 手動啟動 VM 容易遺漏
2. 關機時 VM 若未保存狀態可能損毀
3. 無統一順序與延遲
深層原因：
- 架構層面：控制面流程缺失
- 技術層面：VPC 指令有限
- 流程層面：未定義 SOP

### Solution Design
解決策略：使用工作排程器 OnStart 啟動 VM，VPC 設定關閉時保存狀態；延遲啟動以等待網卡/磁碟就緒，降低錯誤。

實施步驟：
1. 開機自啟
- 實作細節：schtasks OnStart 執行 VMC
- 所需資源：VMC 檔
- 預估時間：0.25 小時

2. 關機保存
- 實作細節：VPC 設定 Close→Save state
- 所需資源：VPC GUI
- 預估時間：0.25 小時

3. 延遲與重試
- 實作細節：啟動前 sleep、失敗重啟
- 所需資源：啟動批次
- 預估時間：0.25 小時

關鍵程式碼/設定：
```cmd
:: 延遲 60 秒後啟動 VM
schtasks /create /tn "AutoStart-ServicesVM" /sc ONSTART ^
/tr "cmd /c timeout /t 60 && start \"\" \"C:\VMs\Services.vmc\"" /ru SYSTEM /rl HIGHEST
```

實際案例：作者將服務移到 VM，需確保開機即服務。
實作環境：Virtual PC 2007；Vista Host。
實測數據：
改善前：需手動介入
改善後：自動啟動與保存狀態
改善幅度：恢復時間縮短（定性）

Learning Points
- 自動化啟停設計
- 保存狀態避免資料損毀
- 延遲等待依賴資源

Practice Exercise
- 基礎：建立 OnStart 排程並測試（30 分鐘）
- 進階：加入重試與日誌（2 小時）
- 專案：關機/重啟 SOP（8 小時）

Assessment Criteria
- 功能完整性：自啟/保存/重試
- 程式碼品質：簡潔健壯
- 效能優化：等待時間合理
- 創新性：健康檢查後再啟動


## Case #13: 效能監控與容量規劃（PerfMon + Logman）

### Problem Statement（問題陳述）
業務場景：遷移後需持續監控 Host 與 VM 的 CPU/記憶體/磁碟/網路，以保證「無明顯變慢」的目標並提前發現瓶頸。
技術挑戰：選擇合適計數器、資料保存與輪替、可視化。
影響範圍：服務穩定性、容量規劃。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無數據支撐的體感判斷不可靠
2. 監控缺失導致問題晚發現
3. 計數器與採樣不足或過多
深層原因：
- 架構層面：缺少監控系統
- 技術層面：計數器選型
- 流程層面：無週期性審視

### Solution Design
解決策略：建立 Host 與 VM 各一個 Data Collector，選取關鍵計數器，每分鐘採樣，循環二進制檔保存，週期匯出 CSV 分析；設定閾值警報（可選）。

實施步驟：
1. 計數器選型
- 實作細節：CPU/記憶體/分頁/磁碟/網路
- 所需資源：PerfMon
- 預估時間：0.5 小時

2. 建立收集組
- 實作細節：logman 腳本化建立
- 所需資源：logman
- 預估時間：0.5 小時

3. 匯出與分析
- 實作細節：每週匯出 CSV，趨勢分析
- 所需資源：PowerShell/Excel
- 預估時間：1 小時

關鍵程式碼/設定：
```cmd
logman create counter HostPerf -si 00:01:00 -o C:\perf\HostPerf -f bincirc -max 200 ^
-c "\Processor(_Total)\% Processor Time" ^
-c "\Memory\Available MBytes" ^
-c "\LogicalDisk(_Total)\Avg. Disk Queue Length" ^
-c "\Network Interface(*)\Bytes Total/sec" ^
-c "\Process(vpc)\% Processor Time"

logman start HostPerf
```

實際案例：作者以「無明顯變慢」為目標，建議以數據驗證。
實作環境：Vista Host；Win2003 VM。
實測數據：
改善前：缺乏量化依據
改善後：持續監測，容量可預測
改善幅度：問題定位時間縮短（定性）

Learning Points
- 關鍵計數器與解讀
- 循環存檔與匯出
- 趨勢分析支援調參

Practice Exercise
- 基礎：建立與啟動收集組（30 分鐘）
- 進階：用 PowerShell 匯出與繪圖（2 小時）
- 專案：撰寫容量規劃建議（8 小時）

Assessment Criteria
- 功能完整性：監控到位
- 程式碼品質：腳本穩定
- 效能優化：指標選取合理
- 創新性：可視化與告警


## Case #14: 檔案分享與 ACL/Share 權限無痛遷移

### Problem Statement（問題陳述）
業務場景：Host 需承載檔案分享；遷移過程要保留共用設定與檔案 ACL，避免用戶權限錯亂與中斷。
技術挑戰：保留 DACL/SACL/擁有者、Share 定義、路徑調整。
影響範圍：資料存取、內網協作。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 僅複製檔案會丟失 ACL
2. Share 設定存於登錄，易遺漏
3. SID 不一致可能造成權限問題
深層原因：
- 架構層面：身份/授權與資料耦合
- 技術層面：Robocopy 參數與登錄匯出
- 流程層面：缺乏驗收清單

### Solution Design
解決策略：使用 Robocopy /COPY:DATSOU 複製以保留 ACL 等，匯出 LanmanServer\Shares 設定，導入新機後驗證路徑與權限，必要時 ICACLS 修正 SID。

實施步驟：
1. 檔案複製
- 實作細節：/MIR /COPY:DATSOU /R:2 /W:5
- 所需資源：robocopy
- 預估時間：依資料量

2. Share 匯入
- 實作細節：匯出/匯入登錄；調整路徑
- 所需資源：reg.exe
- 預估時間：0.5 小時

3. 權限驗收
- 實作細節：icacls 校驗與修正
- 所需資源：icacls
- 預估時間：0.5 小時

關鍵程式碼/設定：
```cmd
:: 檔案與 ACL 保留
robocopy D:\Data \\HOST\D$\Data /MIR /COPY:DATSOU /R:2 /W:5 /XJ /TEE /LOG+:C:\logs\copy.log

:: 匯出/匯入 Share 設定（需備份！）
reg export "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Shares" C:\backup\shares.reg
reg import C:\backup\shares.reg

:: 權限檢查
icacls "D:\Data" /verify
```

實際案例：作者在 Host 維持檔案伺服器角色。
實作環境：Vista Host。
實測數據：
改善前：手動重建風險高
改善後：ACL/Share 自動化遷移
改善幅度：錯誤率顯著下降（定性）

Learning Points
- 檔案/ACL/Share 遷移技巧
- SID 與權限核對
- 變更後驗收流程

Practice Exercise
- 基礎：Robocopy 保留 ACL 複製（30 分鐘）
- 進階：Share 匯出/匯入並調整路徑（2 小時）
- 專案：完整檔案伺服器遷移（8 小時）

Assessment Criteria
- 功能完整性：存取正常、權限正確
- 程式碼品質：腳本化、可追溯
- 效能優化：複製效率
- 創新性：自動驗收腳本


## Case #15: Media Center 上網與啟動故障排除（防火牆/DNS/時間）

### Problem Statement（問題陳述）
業務場景：作者曾被 MCE 的上網啟動問題卡住很久；改裝 Vista 後需確保 MCE 正常啟動、抓取節目表與線上功能。
技術挑戰：MCE 需要正確 DNS、時間同步與防火牆放行；VM 上跑基礎網路服務，需協調。
影響範圍：MCE 可用性、線上功能。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. DNS 解析/代理錯誤導致 MCE 初始化失敗
2. 系統時間偏差造成 TLS 驗證問題
3. 防火牆未放行導致連線被阻
深層原因：
- 架構層面：Host 依賴 VM 的 DNS/DHCP
- 技術層面：防火牆規則與服務端口未對齊
- 流程層面：未建立故障檢查清單

### Solution Design
解決策略：建立 MCE 啟動前檢查清單：時間同步、DNS 連通、必要端口放行；對 Host 設定優先 DNS 指向 VM；防火牆放行 MCE 所需規則。

實施步驟：
1. 時間/DNS 校驗
- 實作細節：w32tm 校時、nslookup 測解析
- 所需資源：w32tm、nslookup
- 預估時間：0.25 小時

2. 防火牆放行
- 實作細節：啟用 MCE 規則群組（Vista）
- 所需資源：netsh advfirewall
- 預估時間：0.25 小時

3. 啟動與日誌
- 實作細節：啟動 MCE，檢查事件檢視器
- 所需資源：Event Viewer
- 預估時間：0.25 小時

關鍵程式碼/設定：
```cmd
:: 同步時間
w32tm /resync /force

:: 測 DNS
nslookup www.microsoft.com 192.168.1.10

:: 啟用 Windows Media Center 防火牆規則（實際群組名稱依語系可能不同）
netsh advfirewall firewall set rule group="Windows Media Center" new enable=Yes
```

實際案例：作者提到先前 MCE 上網啟動曾卡關，本次希望避免重蹈覆轍。
實作環境：Vista Host；VM 提供 DNS/DHCP。
實測數據：
改善前：MCE 啟動不穩
改善後：建立檢查清單與規則
改善幅度：啟動成功率提升（定性）

Learning Points
- MCE 前置條件
- 防火牆規則群組操作
- 故障清單化

Practice Exercise
- 基礎：完成一次檢查清單並啟動 MCE（30 分鐘）
- 進階：製作自動檢查批次腳本（2 小時）
- 專案：建立常見故障 KB（8 小時）

Assessment Criteria
- 功能完整性：MCE 啟動與線上功能正常
- 程式碼品質：檢查腳本可靠
- 效能優化：快速定位問題
- 創新性：自動修復步驟


## Case #16: 使用 Undo Disks/影像備援實現回滾策略

### Problem Statement（問題陳述）
業務場景：正式換裝與服務遷移風險高，需可快速回滾。Virtual PC 提供 Undo Disks；亦可用系統映像在 Host 實作備援。
技術挑戰：正確使用 Undo Disks、制定切換窗口與回退邏輯、避免資料遺失。
影響範圍：換裝失敗成本、服務中斷。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 配置錯誤或相容性問題
2. 無回滾將導致長時間停擺
3. 人為誤操作風險
深層原因：
- 架構層面：缺少版本化/快照
- 技術層面：對工具機制不熟
- 流程層面：缺乏回退 SLO

### Solution Design
解決策略：VM 啟用 Undo Disks，遷移前建立基準點；完成驗收後選擇 Commit；若失敗則 Discard 回滾。Host 以全碟映像保護（換裝前/後各一次）。

實施步驟：
1. VM 啟用 Undo Disks
- 實作細節：Virtual PC 設定層級開啟
- 所需資源：VPC GUI
- 預估時間：0.25 小時

2. 切換窗口規劃
- 實作細節：低峰時段、通知用戶
- 所需資源：變更管理單
- 預估時間：0.5 小時

3. 驗收與回退
- 實作細節：驗證清單；若失敗選擇 Discard
- 所需資源：驗收表、日誌
- 預估時間：0.5–1 小時

關鍵程式碼/設定：
```text
Virtual PC 2007 不提供 CLI 控制 Undo，於 VM 設定啟用：
- Settings -> Undo Disks -> Enable
切換後於關閉提示選擇：Commit（保留變更）或 Discard（回滾）
```

實際案例：作者在 VPC 中先行測試 Vista，同步具備回滾思維。
實作環境：Virtual PC 2007；Vista/Win2003 VM。
實測數據：
改善前：變更不可逆
改善後：可快速回退
改善幅度：回復時間明顯縮短（定性）

Learning Points
- Undo Disks 機制
- 變更窗口與驗收
- 回退決策標準

Practice Exercise
- 基礎：啟用 Undo 並模擬回滾（30 分鐘）
- 進階：設計回退判斷表與門檻（2 小時）
- 專案：完整變更與回退手冊（8 小時）

Assessment Criteria
- 功能完整性：回滾可行
- 程式碼品質：手冊/流程清晰
- 效能優化：恢復時間最小
- 創新性：多層備援（影像+Undo）


-------------------------
案例分類

1) 按難度分類
- 入門級：Case 6, 10, 12, 15
- 中級：Case 2, 3, 4, 5, 8, 9, 13, 14, 16
- 高級：Case 1, 7, 11

2) 按技術領域分類
- 架構設計類：Case 1, 2, 3, 11, 16
- 效能優化類：Case 2, 3, 6, 13
- 整合開發類（配置/遷移）：Case 4, 5, 7, 8, 9, 14
- 除錯診斷類：Case 10, 13, 15
- 安全防護類：Case 4, 5, 14, 16（資料保護/回滾）

3) 按學習目標分類
- 概念理解型：Case 1, 11, 16
- 技能練習型：Case 4, 5, 6, 8, 9, 14
- 問題解決型：Case 2, 3, 7, 12, 13, 15
- 創新應用型：Case 1, 13, 16

-------------------------
案例關聯圖（學習路徑建議）

- 入門起步：
  1) 先做 Case 10（VM 測試 Vista），理解測試邊界
  2) 接著 Case 11（32/64 位選型），完成決策
- 架構定稿：
  3) 做 Case 1（虛擬化解耦方案），形成整體藍圖
  4) 配合 Case 12（自動啟停）讓 VM 穩定運轉
- 網路基礎服務：
  5) 先做 Case 8（DNS/DHCP 遷移與橋接），確保 LAN 正常
  6) 再做 Case 7（IIS/SMTP）與 Case 9（SQL Express）
- 檔案與資料保護：
  7) 做 Case 4（RAID-1+VSS）與 Case 14（ACL/Share 遷移）
  8) 做 Case 5（每週備份），完成資料面閉環
- 效能與運營：
  9) 佈建 Case 13（監控與容量規劃）
  10) 佈建 Case 6（轉檔離峰排程），保障體驗
- 體驗與除錯：
  11) 套用 Case 15（MCE 故障排除），穩定多媒體
- 風險控制：
  12) 全程搭配 Case 16（回滾策略）
  13) 針對 CPU/記憶體限制，持續用 Case 2、3 微調

依賴關係要點：
- Case 1 是核心設計，先於所有遷移案例
- Case 8 是 DNS/DHCP 基礎，應先於站台與 DB 遷移（Case 7、9）
- Case 4/5/14 應在大規模遷移前完成，以保資料安全
- Case 12/16 可橫向支持整個遷移過程，隨時可用回滾與自動化

完整學習路徑：
Case 10 → Case 11 → Case 1 → Case 12 → Case 8 → Case 7 → Case 9 → Case 4 → Case 14 → Case 5 → Case 13 → Case 6 → Case 15 → Case 2 → Case 3 → Case 16

說明：以上案例皆以原文情境為核心（家用伺服器角色與 Vista/MCE 共存），擴充為可操作的實戰教學與評估內容；實測數據以觀察與定性指標為主，並提供量化方法以利學員在實務環境中驗證。