---
layout: synthesis
title: "[Tips] 用 磁碟鏡像 無痛更換硬碟"
synthesis_type: solution
source_post: /2010/03/06/tips-painless-hard-drive-replacement-with-disk-mirroring/
redirect_from:
  - /2010/03/06/tips-painless-hard-drive-replacement-with-disk-mirroring/solution/
postid: 2010-03-06-tips-painless-hard-drive-replacement-with-disk-mirroring
---

## Case #1: 無中斷擴容：以動態磁碟鏡像 + Extend Volume 更換資料碟

### Problem Statement（問題陳述）
**業務場景**：內部 Windows Server 承載 IIS 網站、SQL 資料庫與檔案分享（皆位於 D:），需將 750GB 磁碟升級為 1.5TB，同時盡量維持服務不中斷，避免重新設定分享與服務路徑，降低人工與風險。  
**技術挑戰**：在不中斷服務狀態下遷移大量資料並擴展磁區容量；處理 Advanced Format 對齊問題與鏡像重建負載。  
**影響範圍**：網站/資料庫/檔案分享可用性、資料一致性、服務設定延續性、維運停機窗口。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 傳統 clone 工具需離線，750GB 複製耗時且服務需停機。  
2. 手動複製需停止服務且易遺漏分享權限與設定。  
3. Advanced Format 複製後易產生對齊不良導致效能下降。

**深層原因**：
- 架構層面：資料與服務綁定至單一資料磁區（D:），缺乏不中斷遷移機制。  
- 技術層面：未善用 OS 內建軟體 RAID 功能處理在線資料鏡射與擴容。  
- 流程層面：缺少標準作業程序覆蓋「在線遷移 + 擴容 + 回滾」。

### Solution Design（解決方案設計）
**解決策略**：利用 Windows Server 動態磁碟鏡像（RAID1）在線同步資料至新碟，鏡像完成後中斷鏡像保留新碟，再以 Extend Volume 吃進尾端未配置空間完成擴容。全程服務不中斷，僅於加掛硬碟時短暫關機。

**實施步驟**：
1. 硬體安裝與環境前檢  
- 實作細節：關機加裝新硬碟；確認韌體/磁碟狀態（SMART），備份關鍵資料。  
- 所需資源：機房維運流程、備份工具。  
- 預估時間：0.5 小時

2. 建立鏡像（動態磁碟）  
- 實作細節：將 D: 轉為動態磁碟，對新硬碟新增鏡像，等待 Resync 完成（在線、服務不中斷）。  
- 所需資源：磁碟管理（diskmgmt.msc）。  
- 預估時間：視容量/I/O（750GB 可能數小時）

3. 中斷鏡像與擴容  
- 實作細節：Break mirror 保留新碟為 D:，使用 Extend Volume 擴展至未配置空間，驗證服務。  
- 所需資源：磁碟管理、事件檢視器。  
- 預估時間：0.2 小時

**關鍵程式碼/設定**：
```cmd
:: 使用 DiskPart 擴展 D:（動態磁碟/Windows Server 2008+）
diskpart
list volume
select volume <D 的編號>
extend

:: 驗證 NTFS 與 4K 對齊（Advanced Format）
fsutil fsinfo ntfsinfo D:
```

實際案例：文章示範將 750GB 升級為 1.5TB，於步驟 (2)~(5) 期間 IIS/SQL/pagefile 對 D: 的使用持續不中斷。  
實作環境：Windows Server（2008+ 推薦），動態磁碟軟體 RAID1。  
實測數據：  
改善前：需完整停機進行 clone 或大量檔案搬遷，設定需重建。  
改善後：僅於加裝硬碟時關機一次；鏡像/同步/擴容全程不中斷；設定零變更。  
改善幅度：停機窗口由「複製耗時」縮至「換碟時間」。

Learning Points（學習要點）  
核心知識點：  
- 動態磁碟鏡像（RAID1）在線同步特性  
- Extend Volume 線上擴容流程  
- Advanced Format 對齊檢核

技能要求：  
- 必備技能：Windows 磁碟管理、基礎備援與備份  
- 進階技能：故障回滾策略、I/O 監測與變更管控

延伸思考：  
- 可用於更換更大容量或不同品牌硬碟的在線遷移  
- 風險：鏡像期間 I/O 負載上升，操作失誤可能導致錯誤移除  
- 優化：排程於離峰、提前備份/標註磁碟識別、操作雙人覆核

Practice Exercise（練習題）  
- 基礎練習：在 VM 中以兩顆虛擬磁碟重現鏡像、Break、Extend 操作。  
- 進階練習：於鏡像期間壓測 IIS/SQL，觀察效能與事件日誌。  
- 專案練習：撰寫 SOP 與回滾計畫，完成一次生產模擬演練。

Assessment Criteria（評估標準）  
- 功能完整性（40%）：不中斷完成鏡像與擴容，服務連續  
- 程式碼品質（30%）：使用腳本化步驟（DiskPart/驗證）  
- 效能優化（20%）：離峰時段與監測  
- 創新性（10%）：自動化與可回滾設計


## Case #2: 避免 Advanced Format（4K）對齊不良引發效能下降

### Problem Statement（問題陳述）
**業務場景**：既有 750GB 磁碟升級為 1.5TB Advanced Format（4K）硬碟，網站/DB/分享皆位於 D:；欲避免升級後隨機 I/O 效能大幅下降。  
**技術挑戰**：傳統 clone 工具對 4K 對齊不敏感，可能導致分割區起始位移不對齊，影響 DB 與網頁讀寫。  
**影響範圍**：DB 查詢延遲、網站響應時間、備份/維護作業耗時。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 從舊碟 byte-to-byte 複製至 AF 硬碟，保留了舊有錯誤對齊。  
2. 工具未調整分割區起始偏移（通常需 1MB 對齊）。  
3. 未於遷移前驗證實體/邏輯扇區大小與對齊狀態。

**深層原因**：  
- 架構層面：升級流程未納入 AF 對齊標準。  
- 技術層面：使用不支援 AF 對齊的 clone 工具。  
- 流程層面：缺乏對齊檢核與驗證關卡。

### Solution Design（解決方案設計）
**解決策略**：優先採用 OS 鏡像（動態磁碟）或重新建立對齊良好的分割區，再執行檔案層複製；遷移後以工具驗證對齊狀態，必要時執行廠商對齊修正。

**實施步驟**：
1. 遷移前對齊檢核  
- 實作細節：查詢分割區起始位移與實體扇區大小。  
- 所需資源：fsutil、wmic。  
- 預估時間：0.1 小時

2. 遷移方式選擇與執行  
- 實作細節：以動態鏡像同步（首選）或重建分割區（align=1024）後 robocopy 檔案層複製。  
- 所需資源：diskpart、robocopy。  
- 預估時間：視容量

**關鍵程式碼/設定**：
```cmd
:: 檢視 NTFS 與物理扇區大小
fsutil fsinfo ntfsinfo D:

:: 檢查分割區起始位移（需為 1MB 對齊，起始位移 % 1048576 = 0）
wmic partition get Name, StartingOffset, Size

:: 建立 1MB 對齊分割區（必要時）
diskpart
select disk <n>
clean
convert gpt
create partition primary align=1024
format fs=ntfs quick label="Data"
assign letter=D
```

實測數據：  
改善前：Clone 後隨機 I/O 延遲升高（對齊不良風險）。  
改善後：分割區 1MB 對齊，I/O 恢復正常；鏡像法可自動維持正確對齊。  
改善幅度：對齊風險由高降至低。

Learning Points  
核心知識點：AF 4K 與 1MB 對齊、分割區位移檢核、對齊重建。  
技能要求：  
- 必備：fsutil/wmic/diskpart 基礎  
- 進階：規劃對齊流程與回滾

延伸思考：適用 SSD 4K 對齊；限制為需重建或鏡像；優化可自動檢測。  
Practice Exercise：  
- 基礎：讀取 StartingOffset 判斷是否對齊  
- 進階：重建對齊分割區並 robocopy 遷移  
- 專案：撰寫對齊檢核/報告腳本

Assessment Criteria：  
- 功能完整性（40%）：對齊檢核與修正完成  
- 程式碼品質（30%）：腳本準確性  
- 效能優化（20%）：I/O 改善可驗證  
- 創新性（10%）：自動化/報表


## Case #3: 保持 IIS/SQL/Share 不中斷的資料遷移

### Problem Statement（問題陳述）
**業務場景**：伺服器 D: 承載 IIS 網站、SQL DB、檔案分享；需擴容與換碟，但營運時間不可中斷服務。  
**技術挑戰**：開啟中的檔案與 DB 檔案上鎖，傳統檔案層搬遷會失敗或需停機。  
**影響範圍**：SLA、使用者連線、交易處理。  
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：  
1. 檔案層複製遇到鎖定檔案。  
2. Clone 需離線。  
3. 分享與權限重新建立耗時。

**深層原因**：  
- 架構：資料與服務緊綁 D:。  
- 技術：未使用區塊層同步（鏡像）。  
- 流程：缺少不中斷遷移程序。

### Solution Design
**解決策略**：使用動態磁碟鏡像在線複製（區塊層），無視文件鎖定；同步完成後中斷鏡像，保留新碟與原路徑，服務持續提供。

**實施步驟**：
1. 建立鏡像與監測  
- 實作細節：將 D: 加入鏡像；監測 Resync 進度與事件（I/O 波動）。  
- 資源：diskmgmt.msc、事件檢視器。  
- 時間：視容量

2. 中斷鏡像與驗證服務  
- 實作細節：Break mirror、保留新碟為 D:；檢視 IIS/SQL/Share 正常。  
- 資源：IIS 管理員、SQL 工具。  
- 時間：0.2 小時

**關鍵程式碼/設定**：
```powershell
# 驗證關鍵服務不中斷
Get-Service W3SVC, MSSQLSERVER, LanmanServer | Select Name, Status

# IIS 簡測
Invoke-WebRequest http://localhost -UseBasicParsing | Select-Object StatusCode

# SQL 簡測
sqlcmd -Q "SELECT @@VERSION;"
```

實測數據：  
改善前：需停機才能搬遷或 clone。  
改善後：鏡像期間服務持續，僅硬體加裝時短暫停機。  
改善幅度：服務可用性顯著提升。

Learning Points：區塊層 vs 檔案層遷移、服務健診自動化。  
技能要求：  
- 必備：IIS/SQL 基本管理  
- 進階：監測/告警自動化

延伸思考：同法適用檔案伺服器大型遷移。限制是 resync 負載。  
Practice：  
- 基礎：撰寫服務健診檢查腳本  
- 進階：加入重試與報表  
- 專案：建立遷移運維 Runbook

Assessment Criteria：完整性（40）/程式碼（30）/效能（20）/創新（10）


## Case #4: 避免分享與權限重建：保留磁碟代號與路徑

### Problem Statement
**業務場景**：Windows 檔案分享與應用服務硬性依賴 D:\ 路徑；手動搬遷後需重建分享、ACL 與相依設定，風險高。  
**技術挑戰**：確保遷移後 D: 代號不變且 ACL 完整延續。  
**影響範圍**：使用者掛載、應用程式設定、稽核權限。  
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：手動複製導致新路徑/代號差異。  
**深層原因**：  
- 架構：硬綁代號與路徑。  
- 技術：未使用保留代號的遷移手法（鏡像/Break）。  
- 流程：未先備份分享設定。

### Solution Design
**解決策略**：鏡像與 Break 後保留新碟為 D:；在變更前備份分享與 ACL，必要時快速還原。

**實施步驟**：
1. 備份分享/ACL  
- 實作細節：匯出 Shares 與 ACL。  
- 資源：reg、icacls。  
- 時間：0.1 小時

2. Break 後代號校正  
- 實作細節：確保新碟維持 D:；舊碟離線。  
- 資源：diskmgmt、mountvol。  
- 時間：0.1 小時

**關鍵程式碼/設定**：
```cmd
:: 匯出分享設定
reg export HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Shares C:\Shares.reg

:: 匯出 ACL
icacls D:\ /save C:\d_acl.txt /t /c

:: 查看/設定掛載點與代號
mountvol
mountvol D: /L
```

實測數據：  
改善前：需手動重建分享/權限。  
改善後：代號不變，設定零變更；具備快速回復備援。  
改善幅度：設定錯誤風險大幅降低。

Learning Points：分享/ACL 備份、代號管理。  
技能要求：  
- 必備：ACL/分享基礎  
- 進階：自動化稽核腳本

延伸思考：可用掛載點（目錄掛載）取代代號依賴。  
Practice：備份/還原分享與 ACL；模擬故障復原。  
Assessment：還原成功率、腳本健壯性。


## Case #5: 雙碟 RAID1 成對升級的序列化替換策略

### Problem Statement
**業務場景**：現有 RAID1（兩顆 750GB）需升級為兩顆 1.5TB，要求服務不中斷且全程可回滾。  
**技術挑戰**：分兩次替換避免單點風險，正確選擇 Break/Remove 以保留資料完整。  
**影響範圍**：資料可用性、回滾能力、操作風險。  
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：一次性雙碟替換風險高；誤操作易導致資料遺失。  
**深層原因**：  
- 架構：缺乏多層備援（僅 RAID1）。  
- 技術：對 Break/Remove 行為理解不足。  
- 流程：未分步執行與驗證。

### Solution Design
**解決策略**：一次替換一顆：新增大碟→鏡像→Break 保留新碟→拔舊碟；再對第二顆重複，最終兩顆皆為大碟；最後 Extend 擴容。

**實施步驟**：
1. 第一次替換  
- 細節：新增 1.5TB→加入鏡像→等待同步→Break 保留新碟→移除舊碟。  
- 資源：diskmgmt。  
- 時間：視容量

2. 第二次替換與重建  
- 細節：插入第二顆 1.5TB→將 D: 再次鏡像到新碟→完成後保持 RAID1。  
- 資源：diskmgmt。  
- 時間：視容量

3. 擴容  
- 細節：Extend Volume 吃進尾端空間。  
- 資源：diskpart/diskmgmt。  
- 時間：0.1 小時

**關鍵程式碼/設定**：
```cmd
diskpart
list volume
select volume <D>
extend
```

實測數據：  
改善前：一次性雙碟更換需長停機。  
改善後：兩次在線重建，僅硬體插拔短暫停機；全程可回滾。  
改善幅度：風險/停機顯著下降。

Learning Points：分步替換、回滾保證。  
技能要求：  
- 必備：鏡像操作與驗證  
- 進階：變更風險控管

延伸思考：同法適用不同容量/品牌混用。  
Practice：在 VM 中模擬成對替換。  
Assessment：正確保留資料與鏡像狀態。


## Case #6: Windows Server 2003 的限制與替代作法

### Problem Statement
**業務場景**：舊環境為 Windows Server 2003，欲採鏡像+擴容，但 Extend/呈現方式受限。  
**技術挑戰**：2003 僅支援部分動態磁碟功能，擴容後可能以 Spanned 呈現，不同於 2008+。  
**影響範圍**：管理體驗、監控一致性、心理負擔。  
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：作業系統版本功能不足。  
**深層原因**：  
- 架構：遲未升級 OS。  
- 技術：無線上 extend 鏡像一致呈現。  
- 流程：升級計畫缺失。

### Solution Design
**解決策略**：接受 Spanned 呈現或先升級至 2008+；若短期無法升級，採用鏡像後 Break 再以 Spanned 擴容，功能正常但外觀不同。

**實施步驟**：
1. 現況核對  
- 細節：確認 2003 的磁碟管理限制；盤點風險接受度。  
- 資源：系統文件。  
- 時間：0.2 小時

2. 擴容（2003）  
- 細節：使用 diskpart extend；接受 Spanned 呈現。  
- 資源：diskpart。  
- 時間：0.1 小時

**關鍵程式碼/設定**：
```cmd
diskpart
list volume
select volume <D>
extend
```

實測數據：  
改善前：無法在 2003 上獲得 2008+ 的體驗。  
改善後：功能可用但外觀（Spanned）不同。  
改善幅度：可用性提升，體驗部分受限。

Learning Points：版本差異與替代策略。  
技能要求：  
- 必備：diskpart 操作  
- 進階：升級規劃與風險管理

延伸思考：可先虛擬化後再升級。  
Practice：在 2003 VM 測試 extend 呈現。  
Assessment：風險說明與決策合理性。


## Case #7: 桌面版 Windows（XP/7）不支援鏡像的低停機遷移替代

### Problem Statement
**業務場景**：Desktop OS 僅部分支援動態磁碟，不支援鏡像；仍需低停機遷移資料至新碟。  
**技術挑戰**：無法使用 OS 鏡像，檔案層遷移需處理鎖定檔案。  
**影響範圍**：應用可用性、資料一致性。  
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：OS 功能限制。  
**深層原因**：  
- 架構：桌機化部署無伺服器功能。  
- 技術：缺乏區塊層鏡像能力。  
- 流程：未規劃替代機制。

### Solution Design
**解決策略**：使用 VSS 快照 + Robocopy 檔案層準同步；停機切換前做差異補複製，縮短停機窗口。

**實施步驟**：
1. 初次同步  
- 細節：建立快照，從快照路徑 Robocopy 到新碟。  
- 資源：diskshadow、robocopy。  
- 時間：視容量

2. 切換前差異同步與換碟  
- 細節：再執行一次差異 Robocopy；短暫停機切換代號。  
- 資源：robocopy、磁碟管理。  
- 時間：0.3 小時

**關鍵程式碼/設定**：
```cmd
:: 建立快照
diskshadow /s create_vss.txt

:: create_vss.txt 內容示例
# 
# diskshadow 腳本
#
SET CONTEXT PERSISTENT
ADD VOLUME D: ALIAS DataVol
CREATE
EXPOSE %DataVol% X:

:: 從快照複製
robocopy X:\ D:\ /MIR /COPYALL /R:0 /W:0 /MT:16 /XJ /LOG:C:\robolog.txt

:: 切換前差異同步（來源為原 D:）
robocopy D:\ <新碟掛載點或代號> /MIR /COPYALL /R:0 /W:0 /MT:16
```

實測數據：  
改善前：需長停機完整搬遷。  
改善後：停機縮短為最終切換時間。  
改善幅度：停機由小時降至分鐘等級（視資料量）。

Learning Points：VSS 與檔案層準同步。  
技能要求：  
- 必備：robocopy 參數  
- 進階：diskshadow 腳本

延伸思考：也可用於單機開發者工作站遷移。  
Practice：以 VHD 模擬快照複製。  
Assessment：資料一致性與停機縮短程度。


## Case #8: 動態磁碟在異質 OS/工具的相容性風險控管

### Problem Statement
**業務場景**：資料碟用動態磁碟（鏡像），惟部分 Linux/第三方工具無法辨識，需兼顧相容性。  
**技術挑戰**：在保持鏡像優勢下，減輕異質讀取需求的風險。  
**影響範圍**：跨平台維護、救援工具使用。  
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：動態磁碟專有格式，非所有工具支援。  
**深層原因**：  
- 架構：資料以直連磁碟共享給異質系統。  
- 技術：未採用網路層共享或標準封裝。  
- 流程：救援流程未演練。

### Solution Design
**解決策略**：盡量以 SMB/NFS 網路共享避免直連；Break 後舊碟離線保存作為回滾；異質需求改以備份鏡像檔或 VHD 封裝對接。

**實施步驟**：
1. 救援與回滾設計  
- 細節：Break 後將舊碟離線標記保存。  
- 資源：diskmgmt/diskpart。  
- 時間：0.1 小時

2. 異質讀取方式調整  
- 細節：跨系統以 SMB/NFS/備份鏡像方式存取。  
- 資源：檔案分享服務/備份系統。  
- 時間：0.2 小時

**關鍵程式碼/設定**：
```cmd
:: 將舊碟離線，避免誤用
diskpart
list disk
select disk <舊碟>
offline disk
```

實測數據：  
改善前：直連讀取可能失敗。  
改善後：改以網路層或備份鏡像方式互通；保留回滾碟。  
改善幅度：相容性風險降低。

Learning Points：動態磁碟相容性策略。  
技能要求：  
- 必備：diskpart、SMB/NFS 概念  
- 進階：備份鏡像管理

延伸思考：如常需直連，評估硬體 RAID 或儲存空間。  
Practice：模擬離線舊碟與回附。  
Assessment：回滾可行性、相容性方案明確。


## Case #9: 正確使用 Break vs Remove：保留可回滾的新舊副本

### Problem Statement
**業務場景**：鏡像完成後需中斷；若誤用 Remove 可能刪除一側資料，失去回滾保障。  
**技術挑戰**：理解 Break 與 Remove 行為差異，選擇正確動作並標記新舊磁碟。  
**影響範圍**：回滾能力、資料安全。  
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：介面相似、術語不清易誤點。  
**深層原因**：  
- 架構：回滾策略未固化。  
- 技術：操作經驗不足。  
- 流程：缺少雙人覆核。

### Solution Design
**解決策略**：一律使用 Break（保留雙方卷），標註新碟為生產，舊碟立即 Offline；設定操作覆核清單。

**實施步驟**：
1. Break 與標記  
- 細節：Break 後以標籤/記錄標示新舊碟。  
- 資源：變更單、標籤。  
- 時間：0.1 小時

2. 舊碟離線與保存  
- 細節：將舊碟 Offline 保存一定天數。  
- 資源：diskmgmt/diskpart。  
- 時間：0.1 小時

**關鍵程式碼/設定**：
```powershell
# Windows Server 2012+ 可用
Get-Disk | Where-Object SerialNumber -eq '<舊碟序號>' | Set-Disk -IsOffline $true
```

實測數據：  
改善前：誤操作可能刪除一側。  
改善後：雙副本保留且舊碟離線保護。  
改善幅度：回滾保障提升至可實測。

Learning Points：操作語義與風險管控。  
技能要求：  
- 必備：磁碟管理操作  
- 進階：變更管理流程設計

延伸思考：可加入自動化盤點與截圖存證。  
Practice：在測試環境演練 Break/Remove 差異。  
Assessment：是否能在誤操作下保持回滾。


## Case #10: 鏡像重建期間的效能影響與排程

### Problem Statement
**業務場景**：Resync 重建期間，I/O 負載上升導致網站/DB 反應變慢；需降低對業務的影響。  
**技術挑戰**：缺乏明顯節流控制；需監測並合理排程。  
**影響範圍**：使用者體驗、交易延遲。  
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：鏡像重建為大量順序讀寫，爭用 I/O。  
**深層原因**：  
- 架構：單一磁碟群資源有限。  
- 技術：軟體 RAID 無節流控制。  
- 流程：未規劃離峰時段。

### Solution Design
**解決策略**：於離峰時段執行重建；使用 PerfMon 監測磁碟延遲與佇列，必要時暫緩大量任務；對外公告窗口。

**實施步驟**：
1. 監測基線與告警  
- 細節：建立 Data Collector Set，監看 Avg. Disk sec/Read/Write、Current Disk Queue Length。  
- 資源：logman/typeperf。  
- 時間：0.2 小時

2. 排程與載荷調整  
- 細節：安排於夜間，暫停批次/維護作業。  
- 資源：排程系統。  
- 時間：依窗口

**關鍵程式碼/設定**：
```cmd
:: 建立簡易效能收集（10 秒取樣）
typeperf "\PhysicalDisk(_Total)\Avg. Disk sec/Read" "\PhysicalDisk(_Total)\Avg. Disk sec/Write" -si 10 -o C:\disk_perf.csv
```

實測數據：  
改善前：重建期間延遲明顯。  
改善後：離峰操作，干擾降至可接受。  
改善幅度：高峰體驗提升。

Learning Points：效能監測與操作窗口。  
技能要求：  
- 必備：PerfMon 指標  
- 進階：容量與負載管理

延伸思考：必要時使用硬體 RAID。  
Practice：記錄重建期間指標並出圖。  
Assessment：是否在 SLA 內維持效能。


## Case #11: Pagefile 置於 D: 的遷移與傾印需求

### Problem Statement
**業務場景**：Pagefile 位於 D:；遷移與擴容期間需確保系統穩定與記憶體傾印（BSOD dump）需求。  
**技術挑戰**：維持虛擬記憶體可用，同時滿足 crash dump 最小 pagefile 要求。  
**影響範圍**：系統穩定性、疑難排解能力。  
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：Pagefile 濫移造成不可用或 dump 缺失。  
**深層原因**：  
- 架構：pagefile 與資料混置。  
- 技術：未配置系統碟最小 pagefile。  
- 流程：變更未同步到作業指引。

### Solution Design
**解決策略**：在 C: 維持最小 pagefile（供傾印），D: 配置主要 pagefile；遷移期間不移除 C: pagefile。

**實施步驟**：
1. 配置 pagefile  
- 細節：C: 最小、D: 主要。  
- 資源：wmic/SystemPropertiesAdvanced。  
- 時間：0.1 小時

2. 驗證  
- 細節：重開機驗證設定生效。  
- 資源：事件檢視器。  
- 時間：0.1 小時

**關鍵程式碼/設定**：
```cmd
:: 關閉自動管理
wmic computersystem set AutomaticManagedPagefile=False

:: C: 建立最小 pagefile（例如 800MB）
wmic pagefileset create name="C:\\pagefile.sys"
wmic pagefileset where name="C:\\pagefile.sys" set InitialSize=800,MaximumSize=800

:: D: 主要 pagefile（依實際需求）
wmic pagefileset create name="D:\\pagefile.sys"
wmic pagefileset where name="D:\\pagefile.sys" set InitialSize=16384,MaximumSize=16384
```

實測數據：  
改善前：可能缺少傾印或發生記憶體壓力。  
改善後：傾印可用、效能穩定。  
改善幅度：故障可診斷性提升。

Learning Points：pagefile 策略。  
技能要求：  
- 必備：WMIC 操作  
- 進階：crash dump 分析需求

延伸思考：伺服器傾印檔案儲存規劃。  
Practice：調整/驗證 pagefile。  
Assessment：傾印檔案是否可生成。


## Case #12: Extend Volume 的先決條件與故障排除

### Problem Statement
**業務場景**：Break 後擴容時，需確保 D: 後方有連續未配置空間；若 UI 不允許擴展需排除原因。  
**技術挑戰**：處理非連續空間、分割區順序、檔案系統限制。  
**影響範圍**：擴容成功率、工期。  
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：未配置空間不連續或在不同磁碟。  
**深層原因**：  
- 架構：早期分割區佈局不佳。  
- 技術：對 NTFS/動態磁碟擴展邏輯不熟。  
- 流程：未事先規劃空間位置。

### Solution Design
**解決策略**：確保 D: 右側為未配置空間再 Extend；必要時調整分割區順序或改採動態磁碟 Spanned（2003）/或重建對齊分割區。

**實施步驟**：
1. 檢視分割區佈局  
- 細節：確認未配置空間位置。  
- 資源：diskmgmt。  
- 時間：0.1 小時

2. 擴容或替代  
- 細節：若可延伸則 extend；否則評估重建或 Spanned。  
- 資源：diskpart。  
- 時間：0.2 小時

**關鍵程式碼/設定**：
```cmd
diskpart
list volume
select volume <D>
extend
```

實測數據：  
改善前：擴容失敗或受限。  
改善後：成功完成擴容或採替代方案。  
改善幅度：工期可控。

Learning Points：分割區連續性與擴容條件。  
技能要求：  
- 必備：磁碟管理  
- 進階：重建/搬遷規劃

延伸思考：長期以 GPT + 單分割區簡化。  
Practice：設計連續空間擴容演練。  
Assessment：一次成功率與回滾方案。


## Case #13: >2TB 容量規劃：MBR/GPT 選型避免天花板

### Problem Statement
**業務場景**：雖本次升級到 1.5TB，但後續可能擴至 >2TB；需避免 MBR 2TB 限制。  
**技術挑戰**：老系統與工具可能預設 MBR；超過 2TB 無法完整使用。  
**影響範圍**：容量可用性、未來擴充彈性。  
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：MBR 限制單碟最大 2TB。  
**深層原因**：  
- 架構：早期建立錯誤分割表。  
- 技術：缺乏 GPT 規劃。  
- 流程：容量成長路線未定義。

### Solution Design
**解決策略**：新碟以 GPT 建立；超過 2TB 場景預先規劃 GPT 與 OS 版本支援；避免日後重建成本。

**實施步驟**：
1. 轉換與建立  
- 細節：新碟 convert gpt，建立對齊分割區。  
- 資源：diskpart。  
- 時間：0.1 小時

2. 驗證支援  
- 細節：確認 OS 支援 GPT 資料碟。  
- 資源：系統文件。  
- 時間：0.1 小時

**關鍵程式碼/設定**：
```cmd
diskpart
select disk <n>
clean
convert gpt
create partition primary align=1024
format fs=ntfs quick
assign letter=D
```

實測數據：  
改善前：>2TB 空間不可用。  
改善後：完整使用大容量。  
改善幅度：容量可用性 100%。

Learning Points：MBR vs GPT。  
技能要求：  
- 必備：diskpart  
- 進階：UEFI/開機磁碟規劃（若為系統碟）

延伸思考：未來可用 ReFS/Storage Spaces。  
Practice：以 VHDX >2TB 測試。  
Assessment：容量完整性與相容性說明。


## Case #14: 保持 D: 代號穩定：掛載點與代號切換策略

### Problem Statement
**業務場景**：更換後系統可能變更新碟代號；應用強依賴 D:\ 路徑，需避免代號漂移。  
**技術挑戰**：Break 後正確保留新碟為 D:，避免服務指向舊碟或錯碟。  
**影響範圍**：服務中斷、資料誤用。  
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：自動指派代號不可預期。  
**深層原因**：  
- 架構：強耦合路徑。  
- 技術：未事先保留代號。  
- 流程：缺少代號切換檢核表。

### Solution Design
**解決策略**：Break 後立即將舊碟 Offline，確保新碟承接 D:；若需平滑切換，可先以掛載點方式掛入既有目錄再改回代號。

**實施步驟**：
1. 代號確認  
- 細節：列出卷與 GUID；必要時解除 D: 再指派給新碟。  
- 資源：diskmgmt、mountvol。  
- 時間：0.1 小時

2. 舊碟處置  
- 細節：Offline 舊碟防誤用。  
- 資源：diskpart。  
- 時間：0.1 小時

**關鍵程式碼/設定**：
```cmd
mountvol
:: 解除代號
mountvol D: /D
:: 將新卷以 D: 指派（以卷 GUID）
mountvol D: \\?\Volume{<GUID>}\
```

實測數據：  
改善前：代號漂移導致服務找不到路徑。  
改善後：代號穩定，服務不受影響。  
改善幅度：中斷風險降至極低。

Learning Points：卷 GUID 與掛載點。  
技能要求：  
- 必備：mountvol 使用  
- 進階：自動化切換腳本

延伸思考：以目錄掛載取代代號依賴。  
Practice：在 VM 模擬代號切換。  
Assessment：切換零中斷與正確性。


## Case #15: 遷移前後的資料與服務健康驗證與回滾策略

### Problem Statement
**業務場景**：換碟/擴容後需確認資料完整與服務運作；保留舊碟作為回滾保險。  
**技術挑戰**：快速驗證多項服務，定義回滾觸發條件與步驟。  
**影響範圍**：可用性、資料安全、工期。  
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：缺乏標準化驗證與回滾計畫。  
**深層原因**：  
- 架構：多服務依賴 D:。  
- 技術：手動檢查易遺漏。  
- 流程：變更管理不完善。

### Solution Design
**解決策略**：建立驗證清單（IIS/SQL/Share/pagefile/事件日誌），通過後才將舊碟下架；設定回滾時限與條件。

**實施步驟**：
1. 健檢腳本化  
- 細節：檢查服務、端點、DB 可用性、檔案比對。  
- 資源：PowerShell、curl/sqlcmd。  
- 時間：0.3 小時

2. 回滾窗口  
- 細節：保留舊碟離線 X 天；明確回滾流程。  
- 資源：SOP。  
- 時間：規劃

**關鍵程式碼/設定**：
```powershell
# 基本健檢
$web = Invoke-WebRequest http://localhost -UseBasicParsing
$sql = sqlcmd -Q "SELECT DB_NAME();" 2>&1
$share = (net share) -match "D\$|DataShare"

# 簡單檔案抽樣比對
Get-ChildItem D:\Critical\ -Recurse | Get-FileHash | Export-Csv C:\post_hash.csv -NoTypeInformation
```

實測數據：  
改善前：驗證零散，回滾不明確。  
改善後：標準化健檢與回滾窗口。  
改善幅度：變更風險可控。

Learning Points：驗證與回滾工程化。  
技能要求：  
- 必備：PowerShell 腳本  
- 進階：CI/CD 變更檢查整合

延伸思考：加入合規記錄與審計。  
Practice：撰寫端對端健檢腳本。  
Assessment：驗證覆蓋率與回滾成功率。


## Case #16: 批量自動化：以腳本推動多伺服器換碟擴容

### Problem Statement
**業務場景**：多台 Windows Server 需進行同樣的換碟+擴容操作，要求一致性與可追溯。  
**技術挑戰**：GUI 操作難以規模化，易發生手誤。  
**影響範圍**：效率、可重複性、稽核。  
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：人工操作成本高且不可重放。  
**深層原因**：  
- 架構：缺少自動化工具鏈。  
- 技術：缺乏腳本化經驗。  
- 流程：未建立標準化 Runbook。

### Solution Design
**解決策略**：將可腳本化動作（擴容、驗證、離線舊碟、健康檢查）以 PowerShell/DiskPart 腳本落地，搭配日誌與截圖存證；仍保留鏡像/Break 用 GUI 交由人工雙簽。

**實施步驟**：
1. 腳本化可自動部分  
- 細節：DiskPart extend、fsutil 對齊檢核、服務健檢、離線舊碟。  
- 資源：PowerShell Remoting。  
- 時間：1-2 小時/台（含測試）

2. 交付與稽核  
- 細節：日誌保存、工單流程化、雙人覆核鏡像/Break。  
- 資源：工單系統。  
- 時間：持續

**關鍵程式碼/設定**：
```powershell
$server = "server01"
Invoke-Command -ComputerName $server -ScriptBlock {
  # 擴容
  $vol = Get-Volume -DriveLetter D
  $part = Get-Partition -DriveLetter D
  $size = (Get-PartitionSupportedSize -DriveLetter D)
  Resize-Partition -DriveLetter D -Size $size.SizeMax

  # 對齊檢查
  fsutil fsinfo ntfsinfo D: | Out-File C:\ntfsinfo.txt

  # 舊碟離線（以序號匹配）
  # Get-Disk | ft Number, SerialNumber
}
```

實測數據：  
改善前：人工操作易錯。  
改善後：一致性與可追溯性提升。  
改善幅度：效率與品質同步改善。

Learning Points：半自動化拆分、人機協同流程。  
技能要求：  
- 必備：PowerShell 遠端  
- 進階：Idempotent 腳本設計

延伸思考：配合 DSC/Ansible。  
Practice：對兩台 VM 批量擴容與健檢。  
Assessment：一致性、失敗重跑能力。


---------------------
案例分類
---------------------

1. 按難度分類  
- 入門級（適合初學者）：#4, #9, #11, #12, #13, #14, #15  
- 中級（需要一定基礎）：#1, #2, #3, #5, #6, #7, #8  
- 高級（需要深厚經驗）：#10, #16

2. 按技術領域分類  
- 架構設計類：#5, #8, #13, #15  
- 效能優化類：#2, #10, #12  
- 整合開發類（自動化/腳本）：#3, #4, #7, #11, #14, #16  
- 除錯診斷類：#2, #12, #15  
- 安全防護類（風險/回滾/相容）：#8, #9, #13, #15

3. 按學習目標分類  
- 概念理解型：#2, #6, #8, #13  
- 技能練習型：#4, #7, #11, #12, #14  
- 問題解決型：#1, #3, #5, #9, #10, #15  
- 創新應用型：#16

---------------------
案例關聯圖（學習路徑建議）
---------------------
- 建議先學案例順序：
  1) #4（代號與權限保留基礎）  
  2) #9（Break vs Remove 觀念）  
  3) #11（pagefile 與傾印基本功）  
  4) #12（Extend 先決條件）  
  5) #2（AF 對齊與檢核）  
  6) #1（主流程：鏡像 + 擴容）  
  7) #3（服務不中斷檢核）  
  8) #5（雙碟升級策略）  
  9) #10（重建期間效能管控）  
  10) #8（動態磁碟相容與風險）  
  11) #6（舊版 OS 限制）  
  12) #7（Desktop 替代方案）  
  13) #13（>2TB 規劃）  
  14) #14（代號掛載策略）  
  15) #15（驗證與回滾）  
  16) #16（批量自動化）

- 依賴關係：
  - #1 依賴 #2/#4/#9/#12 的基礎（對齊、代號、Break 正確性、Extend 條件）。  
  - #5 依賴 #1（先完成單顆替換流程）。  
  - #10 依賴 #1（鏡像重建）才能談效能管控。  
  - #16 建立在 #1/#3/#4/#12/#15 的可腳本化步驟之上。  
  - #7 是 #6 的替代分支（當 OS 不支援鏡像時）。

- 完整學習路徑建議：
  先掌握磁碟與分割區基礎（#4/#9/#11/#12），再理解 AF 對齊與限制（#2/#6/#13）。隨後完成主流程（#1）與服務不中斷驗證（#3），擴展至成對替換（#5）與效能管控（#10）。最後補齊相容性與替代方案（#8/#7），建立驗證與回滾（#15），並推進自動化（#16）。此路徑從基礎到實戰到規模化，覆蓋多數生產情境。